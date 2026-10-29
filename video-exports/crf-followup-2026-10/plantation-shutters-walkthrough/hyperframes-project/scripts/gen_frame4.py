"""Build followup4/compositions/frame.html from followup2's styles and a list of text lines."""
import json
import re
import sys

src_path, out_path = sys.argv[1], sys.argv[2]
src = open(src_path).read()
style = src[: src.index('  <div\n    id="root"')]
style = re.sub(r"\s*#fr-arrow \{.*?\n    \}\n    #fr-arrow svg \{.*?\n    \}", "", style, flags=re.S)

lines = [  # start, duration, kicker, title
    (0.4, 4.0, "Just finished", "Plantation shutters"),
    (4.5, 7.4, "Close them up or", "Let the light in"),
    (12.2, 6.8, "Look at that", "Absolutely beautiful"),
    (19.2, 3.6, "Stunning", "Great views today"),
    (22.9, 6.8, "Stunning and", "Immaculate"),
    (29.9, 2.2, "Kings Roller Shutters", "Awesome job"),
]


def esc(x):
    return x.replace("&", "&amp;").replace("'", "&#39;")


variables = [
    {"id": "gold", "type": "color", "label": "Brand gold", "default": "#D4B23D"},
    {"id": "cream", "type": "color", "label": "Brand cream", "default": "#FFFAEA"},
]
blocks = []
for i, (s, d, k, t) in enumerate(lines, 1):
    variables += [
        {"id": f"l{i}-kicker", "type": "string", "label": f"Line {i} kicker", "default": k},
        {"id": f"l{i}-title", "type": "string", "label": f"Line {i} title", "default": t},
    ]
    blocks.append(
        f'''    <div id="fr-l{i}" class="fr-line clip" data-start="{s}" data-duration="{d}" data-track-index="{i}">
      <div id="fr-l{i}-k" class="fr-kicker" data-var-text="l{i}-kicker">{esc(k)}</div>
      <div id="fr-l{i}-t" class="fr-title" data-var-text="l{i}-title">{esc(t)}</div>
    </div>'''
    )

var_json = ",\n      ".join(esc(json.dumps(v)) for v in variables)
arr = ",\n      ".join(f'["fr-l{i}", {s}, {d}]' for i, (s, d, k, t) in enumerate(lines, 1))

out = (
    style
    + f'''  <div
    id="root"
    data-composition-id="frame"
    data-width="1080"
    data-height="1920"
    data-composition-variables='[
      {var_json}
    ]'
    style="--gold: #d4b23d; --cream: #fffaea"
  >
    <div id="fr-top"><img id="fr-logo" src="assets/logo.png" alt="Kings Roller Shutters WA" /></div>
    <div id="fr-rule-top" class="fr-rule"></div>
    <div id="fr-rule-bot" class="fr-rule"></div>

'''
    + "\n".join(blocks)
    + f'''
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#fr-logo", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 0);
    tl.fromTo("#fr-rule-top", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power3.out" }}, 0.1);
    tl.fromTo("#fr-rule-bot", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power3.out" }}, 0.2);

    // [id, start, duration]; the last line stays until the end card covers it
    const lines = [
      {arr},
    ];
    lines.forEach(([id, start, dur], i) => {{
      tl.fromTo(`#${{id}}-k`, {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }}, start);
      tl.fromTo(
        `#${{id}}-t`,
        {{ opacity: 0, y: 40, scale: 0.96 }},
        {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.6)" }},
        start + 0.08,
      );
      if (i < lines.length - 1) {{
        tl.to([`#${{id}}-k`, `#${{id}}-t`], {{ opacity: 0, y: -20, duration: 0.2, ease: "power2.in" }}, start + dur - 0.22);
      }}
    }});

    window.__timelines["frame"] = tl;
  </script>
</template>
'''
)
open(out_path, "w").write(out)
print("wrote", out_path, len(lines), "lines")
