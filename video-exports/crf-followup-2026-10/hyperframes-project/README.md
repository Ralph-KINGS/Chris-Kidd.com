# CRM follow-up video (HyperFrames)

Overlays for Chris's roof-to-fence blinds follow-up video: b-roll callouts (`compositions/callouts.html`, 0:08–0:17) and a branded end card (`compositions/endcard.html`, from 0:38). Copy, phone, website and colours are composition variables.

The footage isn't committed. Rebuild it from the original WhatsApp clip:

```bash
ffmpeg -i original.mp4 -vf "scale=1080:1920:flags=lanczos,setsar=1" -c:v libx264 -crf 18 -g 30 -pix_fmt yuv420p -c:a aac -b:a 160k assets/chris-src.mp4
npx hyperframes@0.8.207 render -o master.mp4
```

`thumbnail/thumb.html` is the email thumbnail layout (it expects `frame.png`, `logo.png` and the Montserrat woff2 files next to it).

Background music (`assets/bgm/bed.mp3`) is an original track made with `scripts/compose_bed.py`. There is no third-party licence. It plays at about 22 dB below the voice and rises slightly over the end card.
