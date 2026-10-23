"""Generates index.html and compositions/*.html from the edit data in work/."""
import json, re, html, os, subprocess

W = json.load(open("work/words_out.json"))
SHOTS = json.load(open("work/shots.json"))
TALK_DUR = 43.70
END_START = 43.65
END_DUR = 2.0
TOTAL = round(END_START + END_DUR, 2)
GOLD = "#C9A646"

# B-roll: (id, file, start, duration, media offset)
BROLL = [
    ("broll-beach", "assets/broll/beach.mp4", 17.25, 1.55, 0.6),
    ("broll-kitchen", "assets/broll/kitchen.mp4", 38.40, 1.90, 0.5),
    ("broll-boardroom", "assets/broll/boardroom.mp4", 40.83, 1.53, 0.5),
]

# ---------- captions ----------
KEY = {"listen", "repeat", "last", "words", "question", "beach", "partner"}
W.sort(key=lambda w: w["start"])
PHRASES = [
 "It doesn't even", "require you to", "listen that well,", "which is great", "when your mind", "can be wandering.",
 "It's one of", "my favourite ways", "of opening up", "a conversation", "and drilling", "down further.",
 "This technique", "is called", "mirroring.",
 "For this one,", "let's go back to", "the weekend question.", "How was your weekend?", "And the person says,",
 "\u201cGreat, I took", "the kids", "to the beach.\u201d",
 "Right there", "you can use", "the last three words", "with an upward", "inflection", "and say,", "\u201cTo the beach?\u201d",
 "From there", "they'll step down", "into more detail,", "perhaps talking about", "what beach", "they went to,", "how good it was,", "what they did.",
 "You don't have to", "really listen", "to what they said", "to do this.", "You just have to", "listen for", "the last couple", "of words.",
 "\u201cThe last couple", "of words?\u201d", "Yes.",
 "My recommendation", "is to try this out", "with your partner", "or your children", "before you go", "using it", "on your", "business partner.",
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
        cls = "cw key" if t.lower().strip(".,?!'\u201c\u201d") in KEY else "cw"
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
    #g-title {{ position: absolute; left: 0; top: 0; width: 1080px; height: 420px; }}
    #g-title .t {{
      position: absolute; left: 0; width: 1080px; top: 196px; text-align: center;
      color: #fff; font-weight: 800; font-size: 70px; line-height: 1.08; letter-spacing: -0.01em;
    }}
    #g-title .gold {{ color: {GOLD}; }}
    #g-rule {{ position: absolute; left: 0; top: 0; width: 1080px; height: 420px; }}
    #g-rule .card {{
      position: absolute; left: 80px; width: 920px; top: 196px; padding: 26px 30px;
      background: #fff; border-radius: 30px; text-align: center;
      color: #0d0d0d; font-weight: 800; font-size: 46px; line-height: 1.3; white-space: nowrap;
      box-shadow: 0 14px 40px rgba(0,0,0,.35);
    }}
    #g-rule .acc {{ background: {GOLD}; color: #0d0d0d; border-radius: 12px; padding: 0 14px; }}
    .chat {{ position: absolute; left: 0; top: 0; width: 1080px; height: 420px; }}
    .bub {{
      position: absolute; padding: 20px 34px; border-radius: 40px;
      font-weight: 700; font-size: 50px; line-height: 1.1; color: #0d0d0d; white-space: nowrap;
    }}
    .bub.grey {{ left: 110px; top: 186px; background: #E6E6EA; border-bottom-left-radius: 10px; }}
    .bub.gold {{ right: 110px; top: 300px; background: {GOLD}; border-bottom-right-radius: 10px; }}
    #g-credit {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
    #g-credit .lt {{
      position: absolute; left: 110px; top: 1030px; padding: 16px 28px 16px 24px;
      background: rgba(13,13,13,.82); border-left: 8px solid {GOLD}; border-radius: 6px;
      color: #fff; font-weight: 700; font-size: 44px;
    }}
    #g-credit .lt span {{ color: {GOLD}; }}
  </style>
  <div id="root" data-composition-id="graphics" data-width="1080" data-height="1920">
    <div id="g-title" class="clip" data-start="0" data-duration="{END_START}" data-track-index="0">
      <div id="g-title-in" class="t">The <span class="gold">LAZY</span> listening trick<br />that actually works</div>
    </div>
    <div id="g-chat1" class="clip chat" data-start="17.25" data-duration="1.33" data-track-index="1">
      <div id="g-b1" class="bub grey">…took the kids to the beach.</div>
    </div>
    <div id="g-rule" class="clip" data-start="18.58" data-duration="3.38" data-track-index="2">
      <div id="g-rule-card" class="card">REPEAT THE LAST <span class="acc">1–3 WORDS</span><br />→ AS A QUESTION</div>
    </div>
    <div id="g-chat2" class="clip chat" data-start="21.96" data-duration="3.0" data-track-index="1">
      <div id="g-b2" class="bub grey">…took the kids to the beach.</div>
      <div id="g-b3" class="bub gold">To the beach?</div>
    </div>
    <div id="g-credit" class="clip" data-start="0" data-duration="3.0" data-track-index="3">
      <div id="g-credit-lt" class="lt">Andrew Jepson, <span>FCA</span></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    // title: on screen at frame 0 (thumbnail); steps aside for the chat and rule card
    tl.set("#g-title-in", {{ opacity: 1, filter: "blur(0px)" }}, 0);
    tl.to("#g-title-in", {{ opacity: 0, filter: "blur(6px)", duration: 0.18, ease: "power2.in" }}, 17.07);
    tl.to("#g-title-in", {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }}, 24.96);
    // chat 1: grey bubble pops as it is spoken
    tl.fromTo("#g-b1", {{ opacity: 0, scale: 0.6, y: 20 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.32, ease: "back.out(1.8)", transformOrigin: "0% 100%" }}, 17.30);
    tl.to("#g-b1", {{ opacity: 0, duration: 0.12, ease: "power2.in" }}, 18.44);
    // rule card
    tl.fromTo("#g-rule-card", {{ opacity: 0, scale: 0.9, y: 18 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.4, ease: "expo.out" }}, 18.62);
    tl.to("#g-rule-card", {{ opacity: 0, scale: 0.96, duration: 0.18, ease: "power2.in" }}, 21.76);
    // chat 2: grey returns, gold answer pops on "to the beach"
    tl.fromTo("#g-b2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.18, ease: "power2.out" }}, 21.98);
    tl.fromTo("#g-b3", {{ opacity: 0, scale: 0.6, y: 20 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.32, ease: "back.out(1.8)", transformOrigin: "100% 100%" }}, 22.44);
    tl.to(["#g-b2", "#g-b3"], {{ opacity: 0, duration: 0.16, ease: "power2.in" }}, 24.78);
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
    #e-line .nb {{ white-space: nowrap; }}
    #e-rule {{ width: 120px; height: 8px; background: {GOLD}; margin: 46px auto 0; border-radius: 4px; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="e-wrap">
      <div id="e-kicker">Try it today:</div>
      <div id="e-line"><span class="w">repeat</span> <span class="w">their</span><br /><span class="nb"><span class="w gold">last</span> <span class="w gold">1–3</span> <span class="w gold">words.</span></span></div>
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
# slow push-in on the one stretch longer than 5 s without a framing change
long_shot = next(s for s in SHOTS if abs(s["t"] - 37.30) < 0.01)
S = long_shot["s"] * 1.04
fx, fy = long_shot["fx"], long_shot["fy"]
px = 540 - fx * S
py = (long_shot["y"] + fy * long_shot["s"]) - fy * S
cam_js.append(
    f'      tl.fromTo("#cam", {{ x: {long_shot["x"]}, y: {long_shot["y"]}, scale: {long_shot["s"]} }}, '
    f'{{ x: {px:.1f}, y: {py:.1f}, scale: {S:.4f}, duration: {long_shot["end"] - long_shot["t"]:.2f}, ease: "none" }}, {long_shot["t"]});'
)

broll_html = "\n".join(
    f'      <video id="{bid}" class="clip broll" data-start="{st}" data-duration="{du}" data-media-start="{ms}" '
    f'data-track-index="{2 + k}" src="{src}" muted playsinline></video>'
    for k, (bid, src, st, du, ms) in enumerate(BROLL) if os.path.exists(src)
)

WHOOSH = [11.15, 19.66, 22.44, 42.36]
POP = [17.30, 18.62, 22.44, END_START + 0.27]
def dur(f):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())
sfx = []
for k, t in enumerate(WHOOSH):
    f = "assets/sfx/whoosh-short.mp3" if k % 2 == 0 else "assets/sfx/whoosh.mp3"
    sfx.append(f'    <audio id="sfx-whoosh-{k}" class="clip" data-start="{t - 0.12:.2f}" data-duration="{dur(f):.2f}" data-track-index="{10 + k % 2}" data-volume="0.22" src="{f}"></audio>')
for k, t in enumerate(POP):
    sfx.append(f'    <audio id="sfx-pop-{k}" class="clip" data-start="{t:.2f}" data-duration="{dur('assets/sfx/pop.mp3'):.2f}" data-track-index="12" data-volume="0.3" src="assets/sfx/pop.mp3"></audio>')

music_auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0.04}, {"t": END_START - 0.2, "v": 0.04}, {"t": END_START + 0.3, "v": 0.14},
    {"t": TOTAL - 0.4, "v": 0.14}, {"t": TOTAL, "v": 0.0}]}]})

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
