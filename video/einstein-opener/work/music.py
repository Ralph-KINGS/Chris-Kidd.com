"""Generates a lo-fi bed with MusicGen and loops it to cover the film."""
import numpy as np, soundfile as sf, torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

PROMPT = "inspiring cinematic background music, soft piano, warm strings, gentle uplifting pulse, hopeful and curious, 100 bpm, no vocals"
TARGET = 46.5
torch.manual_seed(5)
proc = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
inputs = proc(text=[PROMPT], padding=True, return_tensors="pt")
sr = model.config.audio_encoder.sampling_rate
audio = model.generate(**inputs, max_new_tokens=int(24 * 50), do_sample=True, guidance_scale=3.0)[0, 0].numpy()
# skip the first second (weak start), then crossfade-loop to the target length
audio = audio[sr:]
xf = int(1.5 * sr)
out = audio.copy()
while len(out) < TARGET * sr:
    ramp = np.linspace(0, 1, xf)
    out = np.concatenate([out[:-xf], out[-xf:] * (1 - ramp) + audio[:xf] * ramp, audio[xf:]])
out = out[: int(TARGET * sr)]
out = out / (np.abs(out).max() + 1e-9) * 0.89
sf.write("work/bed.wav", out, sr)
print("ok", len(out) / sr, sr)
