# Plantation shutters job walkthrough (HyperFrames)

Same series look as the other follow-ups: a logo bar, the 3:4 clip, an animated text band (`compositions/frame.html`, made by `scripts/gen_frame3.py`) and the shared end card.

`compositions/broll.html` cuts away to slow push-ins on stills from this job (`assets/broll/`) over the talking-head and stair-walking sections. The voice keeps playing underneath.

The music (`assets/bgm/bed.mp3`) is an original track made with `scripts/compose_bed3.py`.

Rebuild the footage from the original WhatsApp clip, then render:

```bash
ffmpeg -i original.mp4 -vf "scale=1080:1456:flags=lanczos,setsar=1" -c:v libx264 -crf 18 -g 30 -pix_fmt yuv420p -c:a aac -b:a 160k assets/clip-src.mp4
npx hyperframes@0.8.207 render -o master.mp4
```
