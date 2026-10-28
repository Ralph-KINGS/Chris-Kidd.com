"""Original ambient music bed: warm pads + soft felt-piano arpeggio, C major, ~72 bpm.

Usage: python3 compose_bed.py <out.wav> [seconds]
"""
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
OUT = sys.argv[1]
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 46.0
rng = np.random.default_rng(7)
N = int(DUR * SR)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


# I - V/B - vi - IV  (C, G/B, Am, F), 4 bars of 4 beats per chord change
BPM = 72
BEAT = 60 / BPM
BAR = 4 * BEAT
chords = [
    [48, 55, 60, 64, 67],  # C
    [47, 55, 59, 62, 67],  # G/B
    [45, 52, 57, 60, 64],  # Am
    [41, 53, 57, 60, 65],  # F
]
arps = [
    [72, 67, 76, 67, 79, 76, 72, 67],
    [71, 67, 74, 67, 79, 74, 71, 67],
    [69, 64, 72, 64, 76, 72, 69, 64],
    [69, 65, 72, 65, 77, 72, 69, 65],
]

t_all = np.arange(N) / SR
pad = np.zeros(N)
piano = np.zeros(N)

# Pads: each chord held for 2 bars with slow swells, overlapping crossfades
seg = 2 * BAR
i = 0
start = 0.0
while start < DUR:
    ch = chords[i % 4]
    s0 = int(start * SR)
    length = int((seg + 1.5) * SR)
    s1 = min(N, s0 + length)
    tt = np.arange(s1 - s0) / SR
    env = np.minimum(1, tt / 1.6) * np.minimum(1, np.maximum(0, (seg + 1.5 - tt)) / 1.6)
    voice = np.zeros_like(tt)
    for m in ch:
        f = hz(m)
        for det in (-0.06, 0.0, 0.07):  # gentle chorus
            fd = f * 2 ** (det / 12)
            ph = rng.uniform(0, 2 * np.pi)
            voice += np.sin(2 * np.pi * fd * tt + ph) + 0.25 * np.sin(4 * np.pi * fd * tt + ph) + 0.08 * np.sin(6 * np.pi * fd * tt + ph)
    pad[s0:s1] += voice * env
    start += seg
    i += 1

# Felt piano: one note per beat (eighths every other bar for gentle motion)
i = 0
beat_t = 0.0
step = 0
while beat_t < DUR - 0.5:
    chord_idx = int(beat_t // seg) % 4
    note = arps[chord_idx][step % 8]
    s0 = int(beat_t * SR)
    length = int(3.0 * SR)
    s1 = min(N, s0 + length)
    tt = np.arange(s1 - s0) / SR
    f = hz(note)
    vel = 0.75 + 0.25 * rng.random()
    tone = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 3)
            + 0.12 * np.sin(6 * np.pi * f * tt) * np.exp(-tt * 5))
    env = (1 - np.exp(-tt * 180)) * np.exp(-tt * 1.6)
    piano[s0:s1] += tone * env * vel
    beat_t += BEAT
    step += 1

lp = butter(4, 1800, "low", fs=SR, output="sos")
hp = butter(2, 70, "high", fs=SR, output="sos")
pad = sosfilt(hp, sosfilt(lp, pad))
lp2 = butter(2, 3200, "low", fs=SR, output="sos")
piano = sosfilt(lp2, piano)

pad /= np.max(np.abs(pad)) + 1e-9
piano /= np.max(np.abs(piano)) + 1e-9
dry = 0.55 * pad + 0.45 * piano

# Simple stereo reverb: exponentially decaying noise impulse
ir_len = int(2.4 * SR)
ir_t = np.arange(ir_len) / SR
irL = rng.standard_normal(ir_len) * np.exp(-ir_t * 2.6)
irR = rng.standard_normal(ir_len) * np.exp(-ir_t * 2.6)
irL = sosfilt(butter(2, 4000, "low", fs=SR, output="sos"), irL)
irR = sosfilt(butter(2, 4000, "low", fs=SR, output="sos"), irR)
wetL = fftconvolve(dry, irL)[:N]
wetR = fftconvolve(dry, irR)[:N]
wetL /= np.max(np.abs(wetL)); wetR /= np.max(np.abs(wetR))
L = 0.7 * dry + 0.45 * wetL
R = 0.7 * dry + 0.45 * wetR

# Gentle overall fade in/out
fade = np.minimum(1, t_all / 2.0) * np.minimum(1, (DUR - t_all) / 3.0)
st = np.stack([L * fade, R * fade], axis=1)
st *= 0.5 / np.max(np.abs(st))
sf.write(OUT, st.astype(np.float32), SR, subtype="PCM_16")
print("wrote", OUT, DUR, "s")
