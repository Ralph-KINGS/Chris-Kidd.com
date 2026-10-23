"""Generates index.html and compositions/*.html from the edit data in work/."""
import json, re, html, os, subprocess

W = json.load(open("work/words_out.json"))
SHOTS = json.load(open("work/shots.json"))
TALK_DUR = 35.62
END_START = 36.10
END_DUR = 2.0
TOTAL = round(END_START + END_DUR, 2)
GOLD = "#C9A646"

# B-roll: (id, file, start, duration, media offset)
_m = os.path.exists("assets/broll/montage-bbq.mp4")
BROLL = [
    ("broll-awkward", "assets/broll/coffee-awkward.mp4", 3.95, 1.35, 0.5),
    ("broll-chat", "assets/broll/coffee-chat.mp4", 32.40, 1.38, 0.5),
    ("broll-beach", "assets/broll/montage-beach.mp4", 34.55, 0.55 if _m else 1.55, 1.0),
    ("broll-bbq", "assets/broll/montage-bbq.mp4", 35.10, 0.50, 0.6),
    ("broll-footy", "assets/broll/montage-footy.mp4", 35.60, 0.50, 0.6),
]


# ---------- captions ----------
KEY = set()
W.sort(key=lambda w: w["start"])
PHRASES = [
 "\u201cDid you have", "a good weekend?\u201d", "The typical response", "is yes or no", "and the conversation", "is over.",
 "Typical ^closed questions", "start with can,", "did, will, have.",
 "And any of those", "can, did, will, have", "questions can be", "recrafted into", "an ^open question.",
 "Remember you're trying", "to get people", "to elaborate", "on what you've asked.",
 "What is an", "^open question?",
 "Typically these", "will start with", "^what, when,", "where, who,", "why or ^how.",
 "For example,", "instead of", "\u201cDid you have", "a good weekend,\u201d", "ask", "\u201c^How was your weekend?\u201d",
 "Now you may just get", "a simple", "\u201cGood, thanks,\u201d", "but within that", "you have an opening", "to ask another", "^open question.",
 "\u201cGreat!", "^What did you", "get up to?\u201d",
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
        hot = "^" in t
        t = t.replace("^", "")
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
      position: absolute; left: 0; width: 1080px; top: 222px; text-align: center;
      color: #fff; font-weight: 800; font-size: 74px; line-height: 1.1; letter-spacing: -0.01em;
    }}
    #g-title .gold {{ color: {GOLD}; }}
    .split {{ position: absolute; left: 54px; width: 972px; top: 200px; }}
    .row {{ display: flex; align-items: center; gap: 9px; height: 92px; white-space: nowrap; }}
    .row + .row {{ margin-top: 14px; }}
    .ic {{ width: 46px; height: 46px; border-radius: 23px; display: flex; align-items: center; justify-content: center; flex: none; }}
    .ic.grey {{ background: #636366; }}
    .ic.gold {{ background: {GOLD}; }}
    .pill {{ padding: 14px 18px; border-radius: 20px; font-weight: 700; font-size: 28px; }}
    .qg {{ background: #3A3A3C; color: #D1D1D6; }}
    .ag {{ background: #2C2C2E; color: #8E8E93; }}
    .qy {{ background: #fff; color: #0d0d0d; }}
    .ay {{ background: {GOLD}; color: #0d0d0d; }}
    .ar {{ color: #8E8E93; font-weight: 800; font-size: 36px; }}
    .r2 .ar {{ color: {GOLD}; }}
    .dim {{ opacity: 0.55; }}
    #g-deep .small {{ position: absolute; left: 0; width: 1080px; top: 198px; text-align: center; color: #fff; font-weight: 700; font-size: 52px; }}
    #g-deep .big {{ position: absolute; left: 0; width: 1080px; top: 262px; text-align: center; color: {GOLD}; font-weight: 900; font-size: 112px; letter-spacing: -0.01em; }}
    .col {{ position: absolute; top: 188px; width: 470px; }}
    #g-oc-open {{ left: 50px; }}
    #g-oc-closed {{ left: 560px; }}
    .lab {{ display: inline-block; padding: 6px 18px; border-radius: 10px; font-weight: 800; font-size: 32px; letter-spacing: 0.08em; }}
    .lab.gold {{ background: {GOLD}; color: #0d0d0d; }}
    .lab.grey {{ background: #636366; color: #fff; }}
    .words {{ margin-top: 16px; display: flex; flex-wrap: wrap; gap: 10px 12px; }}
    .wd {{ padding: 8px 16px; border-radius: 12px; font-weight: 800; font-size: 36px; opacity: 0; }}
    #g-oc-open .wd {{ background: #fff; color: #0d0d0d; }}
    #g-oc-closed .wd {{ background: #3A3A3C; color: #D1D1D6; }}
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
      <div id="g-title-in" class="t">One word <span class="gold">kills</span><br />your conversations</div>
    </div>
    <div id="g-s1" class="clip band" data-start="2.72" data-duration="2.58" data-track-index="1">
      <div class="split"><div class="row r1"><span class="ic grey"><svg viewBox="0 0 24 24" width="30" height="30"><path d="M6 6l12 12M18 6L6 18" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/></svg></span><span class="pill qg">\u201cDid you have a good weekend?\u201d</span><span class="ar">\u2192</span><span class="pill ag RYES">\u201cYes.\u201d</span></div></div>
    </div>
    <div id="g-deep" class="clip band" data-start="14.45" data-duration="3.75" data-track-index="2">
      <div id="g-deep-a" class="small">You want people to</div>
      <div id="g-deep-b" class="big">GO DEEPER</div>
    </div>
    <div id="g-oc" class="clip band" data-start="19.70" data-duration="5.45" data-track-index="2">
      <div id="g-oc-open" class="col"><span class="lab gold">OPEN</span><div class="words">
        <span id="o1" class="wd">what</span><span id="o2" class="wd">when</span><span id="o3" class="wd">where</span><span id="o4" class="wd">who</span><span id="o5" class="wd">how</span></div></div>
      <div id="g-oc-closed" class="col"><span class="lab grey">CLOSED</span><div class="words">
        <span id="c1" class="wd">did</span><span id="c2" class="wd">can</span><span id="c3" class="wd">have</span><span id="c4" class="wd">will</span><span id="c5" class="wd">do</span><span id="c6" class="wd">could</span></div></div>
    </div>
    <div id="g-s2" class="clip band" data-start="26.95" data-duration="2.35" data-track-index="1">
      <div class="split"><div class="row r1"><span class="ic grey"><svg viewBox="0 0 24 24" width="30" height="30"><path d="M6 6l12 12M18 6L6 18" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/></svg></span><span class="pill qg">\u201cDid you have a good weekend?\u201d</span><span class="ar">\u2192</span><span class="pill ag RYES">\u201cYes.\u201d</span></div> <div class="row r2"><span class="ic gold"><svg viewBox="0 0 24 24" width="30" height="30"><path d="M5 12.5l4.5 4.5L19 7.5" stroke="#0d0d0d" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></span><span class="pill qy RQ">\u201cHow was your weekend?\u201d</span><span class="ar">\u2192</span><span class="pill ay RA" style="opacity:0">\u201cWhat did you get up to?\u201d</span></div></div>
    </div>
    <div id="g-s3" class="clip band" data-start="34.05" data-duration="{round(END_START - 34.05, 2)}" data-track-index="1">
      <div class="split"><div class="row r1"><span class="ic grey"><svg viewBox="0 0 24 24" width="30" height="30"><path d="M6 6l12 12M18 6L6 18" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/></svg></span><span class="pill qg">\u201cDid you have a good weekend?\u201d</span><span class="ar">\u2192</span><span class="pill ag RYES">\u201cYes.\u201d</span></div> <div class="row r2"><span class="ic gold"><svg viewBox="0 0 24 24" width="30" height="30"><path d="M5 12.5l4.5 4.5L19 7.5" stroke="#0d0d0d" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></span><span class="pill qy RQ">\u201cHow was your weekend?\u201d</span><span class="ar">\u2192</span><span class="pill ay RA" style="opacity:0">\u201cWhat did you get up to?\u201d</span></div></div>
    </div>
    <div id="g-credit" class="clip" data-start="0" data-duration="3.0" data-track-index="3">
      <div id="g-credit-lt" class="lt">Andrew Jepson, <span>FBP</span></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const out_ = (t) => tl.to("#g-title-in", {{ opacity: 0, filter: "blur(6px)", duration: 0.16, ease: "power2.in" }}, t);
    const in_ = (t) => tl.to("#g-title-in", {{ opacity: 1, filter: "blur(0px)", duration: 0.28, ease: "power3.out" }}, t);
    tl.set("#g-title-in", {{ opacity: 1, filter: "blur(0px)" }}, 0);
    out_(2.55); in_(5.36); out_(14.28); in_(18.26); out_(19.53); in_(25.2); out_(26.78); in_(29.34); out_(33.88);
    const pop = (sel, t) => tl.fromTo(sel, {{ opacity: 0, scale: 0.6, y: 10 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.3, ease: "back.out(1.9)" }}, t);
    const fade = (sel, t, o) => tl.fromTo(sel, {{ opacity: 0 }}, {{ opacity: o, duration: 0.18, ease: "power2.out" }}, t);
    // split card, step 1: the dead end
    pop("#g-s1 .r1 .ic", 2.72); fade("#g-s1 .r1 .qg", 2.74, 1); fade("#g-s1 .r1 .ar", 2.78, 1); pop("#g-s1 .RYES", 2.83);
    tl.to("#g-s1 .split", {{ opacity: 0, duration: 0.15, ease: "power2.in" }}, 5.12);
    // go deeper
    tl.fromTo("#g-deep-a", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.15, ease: "power4.out" }}, 14.47);
    tl.fromTo("#g-deep-b", {{ opacity: 0, scale: 1.2, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, 16.40);
    tl.to(["#g-deep-a", "#g-deep-b"], {{ opacity: 0, duration: 0.15, ease: "power2.in" }}, 18.02);
    // open / closed columns, words pop one at a time
    tl.fromTo("#g-oc .lab", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "expo.out", stagger: 0.08 }}, 19.72);
    [["#o1",21.46],["#o2",21.79],["#o3",22.17],["#o4",22.62],["#o5",23.57],["#c1",23.95],["#c2",24.07],["#c3",24.19],["#c4",24.31],["#c5",24.43],["#c6",24.55]].forEach(([s_, t]) => pop(s_, t));
    tl.to("#g-oc .col", {{ opacity: 0, duration: 0.15, ease: "power2.in" }}, 24.98);
    // split card, step 2: the open version
    fade("#g-s2 .r1", 26.95, 0.5); pop("#g-s2 .r2 .ic", 27.02); pop("#g-s2 .RQ", 27.04); fade("#g-s2 .r2 .ar", 27.3, 1);
    tl.to("#g-s2 .split", {{ opacity: 0, duration: 0.15, ease: "power2.in" }}, 29.12);
    fade("#g-s3 .r1", 34.05, 0.5); fade("#g-s3 .r2 .ic", 34.05, 1); fade("#g-s3 .RQ", 34.05, 1); fade("#g-s3 .r2 .ar", 34.05, 1); pop("#g-s3 .RA", 34.19);
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
    #e-wrap {{ position: absolute; left: 0; width: 1080px; top: 840px; text-align: center; color: #fff; }}
    #e-kicker {{ font-weight: 700; font-size: 64px; letter-spacing: 0.02em; }}
    #e-line {{ margin-top: 0; font-weight: 900; font-size: 88px; line-height: 1.08; padding: 0 90px; }}
    #e-line .gold {{ color: {GOLD}; }}
    #e-line .grey {{ color: #8E8E93; }}
    #e-line .w {{ white-space: nowrap; }}
    #e-line .grey {{ color: #8E8E93; }}
    #e-line .w {{ white-space: nowrap; }}
    #e-rule {{ width: 120px; height: 8px; background: {GOLD}; margin: 46px auto 0; border-radius: 4px; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="e-wrap">
      <div id="e-line"><span class="w">Swap</span> <span class="w grey">\u201cDid you\u2026\u201d</span><br /><span class="w">for</span> <span class="w gold">\u201cHow was\u2026\u201d</span></div>
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

WHOOSH = [3.59, 7.55, 27.03, 34.16]
POP = []
def dur(f):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())
sfx = []
for k, t in enumerate(WHOOSH):
    f = "assets/sfx/whoosh-short.mp3" if k % 2 == 0 else "assets/sfx/whoosh.mp3"
    sfx.append(f'    <audio id="sfx-whoosh-{k}" class="clip" data-start="{t - 0.12:.2f}" data-duration="{dur(f):.2f}" data-track-index="{10 + k % 2}" data-volume="0.22" src="{f}"></audio>')
for k, t in enumerate(POP):
    sfx.append(f'    <audio id="sfx-pop-{k}" class="clip" data-start="{t:.2f}" data-duration="{dur('assets/sfx/pop.mp3'):.2f}" data-track-index="12" data-volume="0.3" src="assets/sfx/pop.mp3"></audio>')

sfx.append(f'    <audio id="sfx-wrong" class="clip" data-start="2.82" data-duration="{dur('assets/sfx/error.mp3'):.2f}" data-track-index="13" data-volume="0.22" src="assets/sfx/error.mp3"></audio>')
sfx.append(f'    <audio id="sfx-chime" class="clip" data-start="27.03" data-duration="{dur('assets/sfx/chime.mp3'):.2f}" data-track-index="14" data-volume="0.22" src="assets/sfx/chime.mp3"></audio>')
sfx.append(f'    <audio id="sfx-pop-a" class="clip" data-start="34.18" data-duration="{dur('assets/sfx/pop.mp3'):.2f}" data-track-index="12" data-volume="0.3" src="assets/sfx/pop.mp3"></audio>')

music_auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0.0}, {"t": 0.3, "v": 0.26}, {"t": END_START - 0.6, "v": 0.26}, {"t": END_START + 0.25, "v": 0.6},
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
