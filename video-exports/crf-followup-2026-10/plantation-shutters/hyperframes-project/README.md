# Plantation shutters follow-up video (HyperFrames)

A 9:16 frame around the 3:4 selfie clip: a logo bar on top and an animated text band underneath (`compositions/frame.html`), then the shared end card (`compositions/endcard.html`). Copy and colours are composition variables.

The music (`assets/bgm/bed.mp3`) is an original track made with `scripts/compose_bed2.py`. It sits about 23 dB below the voice and rises over the end card.

The footage isn't committed. Rebuild it from the original WhatsApp clip:

```bash
ffmpeg -i original.mp4 -vf "scale=1080:1456:flags=lanczos,setsar=1" -c:v libx264 -crf 18 -g 30 -pix_fmt yuv420p -c:a aac -b:a 160k assets/clip-src.mp4
npx hyperframes@0.8.207 render -o master.mp4
```
