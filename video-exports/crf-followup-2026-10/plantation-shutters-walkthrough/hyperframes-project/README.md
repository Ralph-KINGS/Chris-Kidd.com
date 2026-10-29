# Plantation shutters walkthrough (HyperFrames)

Same series look: a logo bar, the 3:4 clip, an animated text band (`compositions/frame.html`, made by `scripts/gen_frame4.py`) and the shared end card.

Colour correction is on `#a-roll` in `index.html` (`data-color-grading`): +0.2 exposure, shadows +0.45, highlights -0.25, vibrance +0.2 and a slight warm shift. Keyframes in the root timeline briefly raise exposure where the camera passes over closed shutters (about 8.4 s and 23 s).

The music (`assets/bgm/bed.mp3`) is an original fingerpicked track made with `scripts/compose_bed4.py`. It dips under each spoken line and rises slightly in the gaps.

Rebuild the footage from the original WhatsApp clip, then render:

```bash
ffmpeg -i original.mp4 -vf "scale=1080:1456:flags=lanczos,setsar=1" -c:v libx264 -crf 18 -g 30 -pix_fmt yuv420p -c:a aac -b:a 160k assets/clip-src.mp4
npx hyperframes@0.8.207 render -o master.mp4
```
