"""Generates index.html and compositions/*.html from the edit data in work/."""
import json, re, html, os, subprocess

W = json.load(open("work/words_out.json"))
SHOTS = json.load(open("work/shots.json"))
TALK_DUR = 43.60
END_START = 43.55
QUOTE_END = 7.66
END_DUR = 2.0
TOTAL = round(END_START + END_DUR, 2)
GOLD = "#C9A646"

# B-roll: (id, file, start, duration, media offset)
BROLL = []

# ---------- captions ----------
KEY = {"curious", "curiosity."}
W.sort(key=lambda w: w["start"])
QW = [w for w in W if w["start"] < 6.1]
W = [w for w in W if w["start"] >= 7.5]
PHRASES = [
 "greatest minds,", "he would have made", "the perfect finance", "^business ^partner.",
 "An appetite", "to understand", "for an FBP", "is all about", "curiosity.",
 "That insatiable appetite", "to want to", "understand", "what's really going on", "around here.",
 "The credibility gains", "for anyone", "with this appetite", "has no ceiling.",
 "It's what puts you", "at the front", "of the queue", "when problems", "need to be solved.",
 "You can quickly", "identify when something", "doesn't make sense", "and you are relentless", "in wanting",
 "to understand", "why things are", "the way they are.",
 "If I gave you", "a car ^engine,", "you'd ^pull ^it ^apart", "and put it back", "together", "just to see",
 "^how ^it ^worked.", "And you would", "do it", "very, very quickly.",
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
groups = [g for g in groups if not (13.8 <= g[0]["start"] < 18.0)]
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
        hot = t.startswith("^")
        t = t.lstrip("^")
        cls = "cw key" if hot or t.lower().strip(".,?!'\u201c\u201d\u2026") in KEY else "cw"
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
      position: absolute; left: 0; width: 1080px; top: 236px; text-align: center;
      color: #fff; font-weight: 800; font-size: 76px; line-height: 1.1; letter-spacing: -0.01em;
    }}
    #g-title .gold {{ color: {GOLD}; }}
    #g-credit {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
    #g-credit .lt {{
      position: absolute; left: 110px; top: 1030px; padding: 16px 28px 16px 24px;
      background: rgba(13,13,13,.82); border-left: 8px solid {GOLD}; border-radius: 6px;
      color: #fff; font-weight: 700; font-size: 44px;
    }}
    #g-credit .lt span {{ color: {GOLD}; }}
    #g-kin {{ position: absolute; left: 0; top: 420px; width: 1080px; height: 1500px; background: #121212; }}
    #g-kin .small {{ position: absolute; left: 0; width: 1080px; text-align: center; color: #fff; font-weight: 700; font-size: 54px; }}
    #g-kin .big {{ position: absolute; left: 0; width: 1080px; text-align: center; color: {GOLD}; font-weight: 900; font-size: 150px; letter-spacing: -0.02em; }}
    #g-kin .mid {{ position: absolute; left: 0; width: 1080px; text-align: center; color: #fff; font-weight: 800; font-size: 72px; line-height: 1.12; }}
    #g-kin .w {{ display: inline-block; }}
  </style>
  <div id="root" data-composition-id="graphics" data-width="1080" data-height="1920">
    <div id="g-title" class="clip band" data-start="{QUOTE_END}" data-duration="{round(END_START - QUOTE_END, 2)}" data-track-index="0">
      <div id="g-title-in" class="t">Why <span class="gold">curiosity</span><br />beats clever</div>
    </div>
    <div id="g-kin" class="clip" data-start="13.85" data-duration="4.2" data-track-index="1">
      <div id="g-k1" class="small" style="top: 420px;">is all about</div>
      <div id="g-k2" class="big" style="top: 500px;">curiosity.</div>
      <div id="g-k3" class="mid" style="top: 740px;"><span class="w">That</span> <span class="w">insatiable</span><br /><span class="w">appetite</span></div>
    </div>
    <div id="g-credit" class="clip" data-start="{QUOTE_END}" data-duration="3.2" data-track-index="3">
      <div id="g-credit-lt" class="lt">Andrew Jepson, <span>FBP</span></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#g-title-in", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, {QUOTE_END + 0.02});
    // kinetic card, timed to the words
    tl.fromTo("#g-k1", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.15, ease: "power4.out" }}, 13.86);
    tl.fromTo("#g-k2", {{ opacity: 0, scale: 1.25, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, 14.47);
    tl.fromTo("#g-k3 .w:nth-of-type(1)", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power4.out" }}, 15.41);
    tl.fromTo("#g-k3 .w:nth-of-type(2)", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power4.out" }}, 15.63);
    tl.fromTo("#g-k3 .w:nth-of-type(3)", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power4.out" }}, 16.63);
    // credit lower third, first 3 s after the quote
    tl.fromTo("#g-credit-lt", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }}, {QUOTE_END + 0.2});
    tl.to("#g-credit-lt", {{ opacity: 0, x: -20, duration: 0.22, ease: "power2.in" }}, {QUOTE_END + 2.95});
    window.__timelines["graphics"] = tl;
  </script>
</template>
"""

# ---------- quote card (hook) ----------
QUOTE_TOKENS = ["\u201cI'm", "neither", "especially", "clever", "nor", "especially", "gifted.", "I'm", "just", "very,", "very", "curious.\u201d"]
assert len(QUOTE_TOKENS) == len(QW), (len(QW),)
q_spans, q_js = [], []
for i, (t, w) in enumerate(zip(QUOTE_TOKENS, QW)):
    cls = "qw gold" if "curious" in t else "qw"
    q_spans.append(f'<span id="qw{i}" class="{cls}">{html.escape(t)}</span>')
    q_js.append(f'    tl.to("#qw{i}", {{ opacity: 1, duration: 0.12, ease: "power2.out" }}, {max(0.0, w["start"] - 0.03):.3f});')
quote = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; background: #000; overflow: hidden; }}
    #q-bgwrap {{ position: absolute; left: -64px; top: 0; width: 1209px; height: 1920px; transform-origin: 62% 40%; }}
    #q-bg {{ position: absolute; left: 0; top: 0; width: 1209px; height: 1920px; }}
    #q-dim {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,.62) 40%, rgba(0,0,0,.82) 100%); }}
    #q-text {{
      position: absolute; left: 0; width: 1080px; top: 610px; padding: 0 96px; text-align: center;
      font-family: "Playfair Display", serif; font-weight: 700; font-size: 80px; line-height: 1.16; color: #fff;
    }}
    .qw {{ opacity: 0.42; }}
    .qw.gold {{ color: {GOLD}; }}
    #q-mark {{ position: absolute; left: 0; width: 1080px; top: 400px; text-align: center; font-family: "Playfair Display", serif; font-size: 220px; line-height: 1; color: {GOLD}; }}
    #q-by {{ position: absolute; left: 0; width: 1080px; top: 1330px; text-align: center; font-family: Montserrat, sans-serif; font-weight: 700; font-size: 46px; letter-spacing: 0.12em; color: #fff; }}
    #q-by span {{ color: {GOLD}; }}
  </style>
  <div id="root" data-composition-id="quote" data-width="1080" data-height="1920">
    <div id="q-bgwrap"><img id="q-bg" class="clip" data-start="0" data-duration="{QUOTE_END}" data-track-index="0" src="assets/einstein.jpg" alt="Albert Einstein" /></div>
    <div id="q-dim"></div>
    <div id="q-mark">\u201c</div>
    <div id="q-text">{" ".join(q_spans)}</div>
    <div id="q-by"><span>\u2014</span> ALBERT EINSTEIN</div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#q-bgwrap", {{ scale: 1.0 }}, {{ scale: 1.09, duration: {QUOTE_END}, ease: "none" }}, 0);
    tl.set("#q-mark", {{ opacity: 1 }}, 0);
    tl.fromTo("#q-by", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, 6.0);
{chr(10).join(q_js)}
    tl.to(["#q-text", "#q-mark", "#q-by"], {{ opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }}, {QUOTE_END - 0.2});
    window.__timelines["quote"] = tl;
  </script>
</template>
"""

endcard = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; background: #0d0d0d; font-family: Montserrat, sans-serif; }}
    #e-wrap {{ position: absolute; left: 0; width: 1080px; top: 840px; text-align: center; color: #fff; }}
    #e-kicker {{ font-weight: 700; font-size: 64px; letter-spacing: 0.02em; }}
    #e-line {{ margin-top: 0; font-weight: 900; font-size: 140px; line-height: 1.08; padding: 0 90px; }}
    #e-line .gold {{ color: {GOLD}; }}
    #e-line .grey {{ color: #8E8E93; }}
    #e-rule {{ width: 120px; height: 8px; background: {GOLD}; margin: 46px auto 0; border-radius: 4px; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="e-wrap">
      <div id="e-line"><span class="w">Stay</span> <span class="w gold">curious.</span></div>
      <div id="e-rule"></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
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

WHOOSH = [7.58, 9.55, 13.85, 37.25]
POP = []
def dur(f):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())
sfx = []
for k, t in enumerate(WHOOSH):
    f = "assets/sfx/whoosh-short.mp3" if k % 2 == 0 else "assets/sfx/whoosh.mp3"
    sfx.append(f'    <audio id="sfx-whoosh-{k}" class="clip" data-start="{t - 0.12:.2f}" data-duration="{dur(f):.2f}" data-track-index="{10 + k % 2}" data-volume="0.22" src="{f}"></audio>')
for k, t in enumerate(POP):
    sfx.append(f'    <audio id="sfx-pop-{k}" class="clip" data-start="{t:.2f}" data-duration="{dur('assets/sfx/pop.mp3'):.2f}" data-track-index="12" data-volume="0.3" src="assets/sfx/pop.mp3"></audio>')

sfx.append(f'    <audio id="sfx-riser" class="clip" data-start="0" data-duration="{dur('assets/sfx/riser-soft.mp3'):.2f}" data-track-index="13" data-volume="0.5" src="assets/sfx/riser-soft.mp3"></audio>')

music_auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0.0}, {"t": 0.6, "v": 0.32}, {"t": END_START - 0.25, "v": 0.32}, {"t": END_START + 0.25, "v": 0.6},
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
      #endcard, #quote {{ z-index: 10; }}
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
      <div id="quote" data-composition-id="quote" data-composition-src="compositions/quote.html"
        data-start="0" data-duration="{QUOTE_END}" data-track-index="5" data-track-kind="graphics"
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
open("compositions/quote.html", "w").write(quote)
print("groups", len(groups), "total", TOTAL, "nocaptions" if nocap else "")
for g in groups:
    print(f'{g[0]["start"]:6.2f} ' + " ".join(w["text"] for w in g))
