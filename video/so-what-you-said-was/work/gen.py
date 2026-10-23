"""Generates index.html and compositions/*.html from the edit data in work/."""
import json, re, html, os, subprocess

W = json.load(open("work/words_out.json"))
SHOTS = json.load(open("work/shots.json"))
TALK_DUR = 50.80
END_START = 50.75
END_DUR = 2.0
TOTAL = round(END_START + END_DUR, 2)
GOLD = "#C9A646"

# B-roll: (id, file, start, duration, media offset)
BROLL = [
    ("broll-nod", "assets/broll/nod.mp4", 9.26, 1.54, 0.5),
    ("broll-think", "assets/broll/think.mp4", 22.60, 2.00, 0.5),
    ("broll-finger", "assets/broll/finger.mp4", 46.50, 1.10, 0.5),
]

# ---------- captions ----------
KEY = {"hearing", "said", "onus", "accurate", "correct"}
W.sort(key=lambda w: w["start"])
PHRASES = [
 "The beauty of", "the \u201cwhat you", "said was\u201d", "versus the", "\u201cwhat I'm hearing is.\u201d",
 "What most people do", "in this situation", "is they will", "repeat back", "to their subject.",
 "\u201cSo what I'm", "hearing is,\u201d", "or a variation", "of that.", "\u201cSo what I", "heard is.\u201d",
 "Now that's good,", "but it's the", "beginner's version", "of confirming that", "you've been listening.",
 "What I want", "you to try", "is the advanced version", "and say,", "\u201cSo what you", "have told me is.\u201d",
 "It's a slight tweak", "that turns the onus", "from you onto them.",
 "When you say", "\u201cSo what I", "am hearing is,\u201d", "they'll say yes,", "you're paraphrasing,", "but you're near enough", "and they'll rarely", "say no unless", "you are way off.",
 "When you say", "\u201cSo what you", "said was,\u201d", "the other person", "takes that question", "very seriously.",
 "Don't be too concerned", "if you weren't", "listening intently", "and you get", "this wrong.",
 "The beauty of", "the \u201cwhat you", "said was\u201d", "versus the", "\u201cwhat I'm hearing is,\u201d",
 "is that they", "will correct you", "if you're wrong.",
 "With the", "\u201cwhat I'm hearing,\u201d", "near enough", "is good enough.",
]
groups, k = [], 0
for ph in PHRASES:
    toks = ph.split(" ")
    g = []
    for t in toks:
        w = dict(W[k]); w["text"] = t; g.append(w); k += 1
    groups.append(g)
assert k == len(W), (k, len(W))
cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    start = max(0.1, g[0]["start"] - 0.04)
    nxt_start = groups[gi + 1][0]["start"] - 0.04 if gi + 1 < len(groups) else None
    end = g[-1]["end"] + 0.35
    if nxt_start is not None:
        end = min(end, nxt_start)
    end = min(end, END_START)
    words = []
    for wi, w in enumerate(g):
        t = w["text"]
        cls = "cw key" if t.lower().strip(".,?!'\u201c\u201d\u2026") in KEY else "cw"
        words.append(f'<span id="cw{gi}-{wi}" class="{cls}">{html.escape(t)}</span>')
        cap_js.append(f'  pop("#cw{gi}-{wi}", {max(start, w["start"] - 0.02):.3f});')
    cap_html.append(
        f'    <div id="cg{gi}" class="clip cg" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
        f'data-track-index="0">{" ".join(words)}</div>'
    )
    cap_js.append(f'  out("#cg{gi}", {end - start + start:.3f});')

captions = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .cg {{
      position: absolute; left: 0; width: 1080px; top: 1215px;
      text-align: center; padding: 0 90px;
      font-family: Montserrat, sans-serif; font-weight: 800; font-size: 76px; line-height: 1.12;
      color: #fff; overflow: visible;
    }}
    .cw {{
      display: inline-block; opacity: 0;
      -webkit-text-stroke: 14px #000; paint-order: stroke fill;
      text-shadow: 0 6px 18px rgba(0,0,0,.45);
    }}
    .cw.key {{ color: {GOLD}; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(cap_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const pop = (sel, t) => tl.fromTo(sel, {{ opacity: 0, y: 14, scale: 0.86 }},
      {{ opacity: 1, y: 0, scale: 1, duration: 0.16, ease: "back.out(2.2)" }}, t);
    const out = (sel, t) => tl.set(sel, {{ opacity: 0, visibility: "hidden" }}, t);
{chr(10).join(cap_js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""

# ---------- graphics (band title, rule card, chat, credit) ----------
graphics = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; font-family: Montserrat, sans-serif; }}
    .band {{ position: absolute; left: 0; top: 0; width: 1080px; height: 420px; }}
    #g-title .t {{
      position: absolute; left: 0; width: 1080px; top: 196px; text-align: center;
      color: #fff; font-weight: 800; font-size: 68px; line-height: 1.12; letter-spacing: -0.01em;
    }}
    #g-title .gold {{ color: {GOLD}; }}
    .cmp {{
      position: absolute; top: 184px; width: 450px; height: 214px; padding: 22px 24px;
      background: #fff; border-radius: 26px; box-shadow: 0 14px 40px rgba(0,0,0,.35);
    }}
    #g-cmp-a {{ left: 60px; }}
    #g-cmp-b {{ left: 570px; }}
    .lab {{
      display: inline-block; padding: 6px 16px; border-radius: 10px;
      font-weight: 800; font-size: 30px; letter-spacing: 0.06em;
    }}
    .lab.grey {{ background: #636366; color: #fff; }}
    .lab.gold {{ background: {GOLD}; color: #0d0d0d; }}
    .q {{ margin-top: 16px; color: #0d0d0d; font-weight: 800; font-size: 42px; line-height: 1.15; }}
    #g-punch .t {{
      position: absolute; left: 0; width: 1080px; top: 188px; text-align: center;
      color: #fff; font-weight: 900; font-size: 76px; line-height: 1.04; letter-spacing: -0.015em;
    }}
    #g-punch .gold {{ color: {GOLD}; }}
    #g-credit {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
    #g-credit .lt {{
      position: absolute; left: 110px; top: 1030px; padding: 16px 28px 16px 24px;
      background: rgba(13,13,13,.82); border-left: 8px solid {GOLD}; border-radius: 6px;
      color: #fff; font-weight: 700; font-size: 44px;
    }}
    #g-credit .lt span {{ color: {GOLD}; }}
  </style>
  <div id="root" data-composition-id="graphics" data-width="1080" data-height="1920">
    <div id="g-title" class="clip band" data-start="0" data-duration="{END_START}" data-track-index="0">
      <div id="g-title-in" class="t">Stop saying<br /><span class="gold">\u201cSo what I'm hearing is\u2026\u201d</span></div>
    </div>
    <div id="g-cmp" class="clip band" data-start="13.0" data-duration="9.5" data-track-index="1">
      <div id="g-cmp-a" class="cmp"><span class="lab grey">BEGINNER</span>
        <div class="q">\u201cSo what I'm<br />hearing is\u2026\u201d</div></div>
      <div id="g-cmp-b" class="cmp"><span class="lab gold">ADVANCED \u2191</span>
        <div class="q">\u201cSo what you<br />said was\u2026\u201d</div></div>
    </div>
    <div id="g-punch" class="clip band" data-start="45.6" data-duration="4.1" data-track-index="2">
      <div id="g-punch-in" class="t">They <span class="gold">WILL</span> correct you<br />if you're wrong.</div>
    </div>
    <div id="g-credit" class="clip" data-start="0" data-duration="3.0" data-track-index="3">
      <div id="g-credit-lt" class="lt">Andrew Jepson, <span>FCA</span></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    // title: on screen at frame 0 (thumbnail); steps aside for the comparison card and punchline
    tl.set("#g-title-in", {{ opacity: 1, filter: "blur(0px)" }}, 0);
    tl.to("#g-title-in", {{ opacity: 0, filter: "blur(6px)", duration: 0.18, ease: "power2.in" }}, 12.92);
    tl.to("#g-title-in", {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }}, 22.55);
    tl.to("#g-title-in", {{ opacity: 0, filter: "blur(6px)", duration: 0.18, ease: "power2.in" }}, 45.45);
    tl.to("#g-title-in", {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }}, 49.8);
    // comparison card: step 1 beginner, step 2 advanced
    tl.fromTo("#g-cmp-a", {{ opacity: 0, scale: 0.88, y: 18 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.42, ease: "expo.out" }}, 13.12);
    tl.fromTo("#g-cmp-b", {{ opacity: 0, scale: 0.88, y: 18 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.42, ease: "expo.out" }}, 17.43);
    tl.to("#g-cmp-a", {{ opacity: 0.55, duration: 0.3, ease: "power2.out" }}, 17.55);
    tl.to(["#g-cmp-a", "#g-cmp-b"], {{ opacity: 0, scale: 0.96, duration: 0.2, ease: "power2.in" }}, 22.28);
    // punchline overlay
    tl.fromTo("#g-punch-in", {{ opacity: 0, scale: 1.18, filter: "blur(8px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "expo.out" }}, 45.72);
    tl.to("#g-punch-in", {{ opacity: 0, filter: "blur(6px)", duration: 0.2, ease: "power2.in" }}, 49.45);
    // credit lower third
    tl.fromTo("#g-credit-lt", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }}, 0.25);
    tl.to("#g-credit-lt", {{ opacity: 0, x: -20, duration: 0.22, ease: "power2.in" }}, 2.72);
    window.__timelines["graphics"] = tl;
  </script>
</template>
"""

endcard = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; background: #0d0d0d; font-family: Montserrat, sans-serif; }}
    #e-wrap {{ position: absolute; left: 0; width: 1080px; top: 760px; text-align: center; color: #fff; }}
    #e-kicker {{ font-weight: 700; font-size: 64px; letter-spacing: 0.02em; }}
    #e-line {{ margin-top: 30px; font-weight: 800; font-size: 92px; line-height: 1.08; padding: 0 90px; }}
    #e-line .gold {{ color: {GOLD}; }}
    #e-line .grey {{ color: #8E8E93; }}
    #e-rule {{ width: 120px; height: 8px; background: {GOLD}; margin: 46px auto 0; border-radius: 4px; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="e-wrap">
      <div id="e-kicker">Try it today:</div>
      <div id="e-line"><span class="w">Swap</span> <span class="w grey">\u201chearing\u201d</span><br /><span class="w">for</span> <span class="w gold">\u201csaid\u201d.</span></div>
      <div id="e-rule"></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#e-kicker", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power4.out" }}, 0);
    tl.fromTo("#e-line .w", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.13, stagger: 0.05, ease: "power4.out" }}, 0.1);
    tl.fromTo("#e-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.4, ease: "expo.out" }}, 0.7);
    window.__timelines["endcard"] = tl;
  </script>
</template>
"""

# ---------- root ----------
cam_js = []
for i, s in enumerate(SHOTS):
    cam_js.append(f'      tl.set("#cam", {{ x: {s["x"]}, y: {s["y"]}, scale: {s["s"]} }}, {s["t"]});')
for s_ in SHOTS:
    if s_["end"] - s_["t"] > 5:
        S = s_["s"] * 1.04
        px = 540 - s_["fx"] * S
        py = (s_["y"] + s_["fy"] * s_["s"]) - s_["fy"] * S
        cam_js.append(f'      tl.fromTo("#cam", {{ x: {s_["x"]}, y: {s_["y"]}, scale: {s_["s"]} }}, '
                      f'{{ x: {px:.1f}, y: {py:.1f}, scale: {S:.4f}, duration: {s_["end"] - s_["t"]:.2f}, ease: "none" }}, {s_["t"]});')

broll_html = "\n".join(
    f'      <video id="{bid}" class="clip broll" data-start="{st}" data-duration="{du}" data-media-start="{ms}" '
    f'data-track-index="{2 + k}" src="{src}" muted playsinline></video>'
    for k, (bid, src, st, du, ms) in enumerate(BROLL) if os.path.exists(src)
)

WHOOSH = [0.80, 19.06, 32.85, 45.38]
POP = [13.12, 17.43, END_START + 0.12]
def dur(f):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())
sfx = []
for k, t in enumerate(WHOOSH):
    f = "assets/sfx/whoosh-short.mp3" if k % 2 == 0 else "assets/sfx/whoosh.mp3"
    sfx.append(f'    <audio id="sfx-whoosh-{k}" class="clip" data-start="{t - 0.12:.2f}" data-duration="{dur(f):.2f}" data-track-index="{10 + k % 2}" data-volume="0.22" src="{f}"></audio>')
for k, t in enumerate(POP):
    sfx.append(f'    <audio id="sfx-pop-{k}" class="clip" data-start="{t:.2f}" data-duration="{dur('assets/sfx/pop.mp3'):.2f}" data-track-index="12" data-volume="0.3" src="assets/sfx/pop.mp3"></audio>')

sfx.append(f'    <audio id="sfx-ding" class="clip" data-start="45.70" data-duration="{dur('assets/sfx/ping.mp3'):.2f}" data-track-index="13" data-volume="0.28" src="assets/sfx/ping.mp3"></audio>')

music_auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0.0}, {"t": 0.4, "v": 0.26}, {"t": END_START - 0.25, "v": 0.26}, {"t": END_START + 0.25, "v": 0.6},
    {"t": TOTAL - 0.5, "v": 0.6}, {"t": TOTAL, "v": 0.0}]}]})

MUSIC_OPEN, MUSIC_CLOSE = ("", "") if os.path.exists("assets/music/bed.mp3") else ("<!-- music pending ", " -->")
index = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0d0d0d; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #0d0d0d; }}
      #band {{ position: absolute; left: 0; top: 0; width: 1080px; height: 420px; background: #0d0d0d; }}
      #band-rule {{ position: absolute; left: 0; top: 416px; width: 1080px; height: 4px; background: #C9A646; z-index: 3; }}
      #stage {{ position: absolute; left: 0; top: 420px; width: 1080px; height: 1500px; overflow: hidden; z-index: 1; }}
      #cam {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; }}
      #talk {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }}
      .broll {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1500px; object-fit: cover; z-index: 2; }}
      #graphics, #captions {{ z-index: 5; }}
      #endcard {{ z-index: 10; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <div id="band"></div>
      <div id="stage" data-layout-allow-overflow>
        <div id="cam">
          <video id="talk" class="clip" data-start="0" data-duration="{TALK_DUR}" data-track-index="1"
            src="assets/talk.mp4" playsinline data-has-audio="true" data-volume="1"></video>
        </div>
{broll_html}
      </div>
      <div id="band-rule"></div>
      <div id="graphics" data-composition-id="graphics" data-composition-src="compositions/graphics.html"
        data-start="0" data-duration="{END_START}" data-track-index="6" data-track-kind="graphics"
        data-width="1080" data-height="1920"></div>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{END_START}" data-track-index="7" data-track-kind="captions"
        data-width="1080" data-height="1920"></div>
      <div id="endcard" data-composition-id="endcard" data-composition-src="compositions/endcard.html"
        data-start="{END_START}" data-duration="{END_DUR}" data-track-index="8" data-track-kind="graphics"
        data-width="1080" data-height="1920"></div>
      {MUSIC_OPEN}<audio id="music" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="9" data-volume="1"
        data-automation='{music_auto}' src="assets/music/bed.mp3"></audio>{MUSIC_CLOSE}
{chr(10).join(sfx)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(cam_js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

import os, sys
os.makedirs("compositions", exist_ok=True)
nocap = "--no-captions" in sys.argv
if nocap:
    index = re.sub(r'\s*<div id="captions".*?></div>', "", index, flags=re.S)
open("index.html", "w").write(index)
open("compositions/graphics.html", "w").write(graphics)
open("compositions/captions.html", "w").write(captions)
open("compositions/endcard.html", "w").write(endcard)
print("groups", len(groups), "total", TOTAL, "nocaptions" if nocap else "")
for g in groups:
    print(f'{g[0]["start"]:6.2f} ' + " ".join(w["text"] for w in g))
