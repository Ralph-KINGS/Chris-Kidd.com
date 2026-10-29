"""Original mellow music bed: electric-piano chords with tremolo, soft sub bass, brushed beat. D major, 84 bpm.

Usage: python3 compose_bed3.py <out.wav> [seconds]
"""
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
OUT = sys.argv[1]
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 40.0
rng = np.random.default_rng(84)
N = int(DUR * SR)
BEAT = 60 / 84


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, s, sig, gain=1.0):
    s0 = int(s * SR)
    if s0 >= N:
        return
    e = min(N, s0 + len(sig))
    buf[s0:e] += sig[: e - s0] * gain


def epiano(f, length):
    t = np.arange(int(length * SR)) / SR
    bell = 0.35 * np.sin(2 * np.pi * f * 7 * t) * np.exp(-t * 9)
    body = np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t * 2.5))
    return (body + bell) * (1 - np.exp(-t * 300)) * np.exp(-t * 0.9)


def brush(length=0.25):
    n = int(length * SR)
    t = np.arange(n) / SR
    return rng.standard_normal(n) * (1 - np.exp(-t * 80)) * np.exp(-t * 14)


def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 55 + 60 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


# Dmaj7 - Bm7 - Gmaj7 - A6, one bar (4 beats) each
chords = [
    ([62, 66, 69, 73], 38),
    ([59, 62, 66, 69], 35),
    ([55, 59, 62, 66], 31),
    ([57, 61, 64, 66], 33),
]

keys = np.zeros(N)
bass = np.zeros(N)
drums = np.zeros(N)
bar = 4 * BEAT
b = 0
while b * bar < DUR:
    tones, root = chords[b % 4]
    t0 = b * bar
    for j, m in enumerate(tones):  # slight strum
        place(keys, t0 + j * 0.018, epiano(hz(m), bar + 1.0), 0.8)
    place(keys, t0 + 2.5 * BEAT, epiano(hz(tones[-1] + 12), 1.5), 0.25)
    t = np.arange(int(bar * SR)) / SR
    place(bass, t0, np.sin(2 * np.pi * hz(root) * t) * (1 - np.exp(-t * 40)) * np.exp(-t * 0.7))
    place(drums, t0, kick(), 0.9)
    place(drums, t0 + 2 * BEAT, kick(), 0.6)
    for k in range(8):
        place(drums, t0 + k * BEAT / 2, brush(), 0.35 if k % 2 else 0.2)
    b += 1

# gentle tremolo on the keys
tt = np.arange(N) / SR
keys *= 1 - 0.18 * (0.5 + 0.5 * np.sin(2 * np.pi * 4.2 * tt))
keys = sosfilt(butter(2, 2600, "low", fs=SR, output="sos"), keys)
bass = sosfilt(butter(2, 220, "low", fs=SR, output="sos"), bass)
drums = sosfilt(butter(1, 7000, "low", fs=SR, output="sos"), drums)
for x in (keys, bass, drums):
    x /= np.max(np.abs(x)) + 1e-9
dry = 0.6 * keys + 0.35 * bass + 0.18 * drums

ir_len = int(1.8 * SR)
ir_t = np.arange(ir_len) / SR
lp = butter(2, 4500, "low", fs=SR, output="sos")
irL = sosfilt(lp, rng.standard_normal(ir_len) * np.exp(-ir_t * 3.5))
irR = sosfilt(lp, rng.standard_normal(ir_len) * np.exp(-ir_t * 3.5))
wetL = fftconvolve(dry, irL)[:N]
wetR = fftconvolve(dry, irR)[:N]
wetL /= np.max(np.abs(wetL)); wetR /= np.max(np.abs(wetR))
L = 0.8 * dry + 0.35 * wetL
R = 0.8 * dry + 0.35 * wetR

fade = np.minimum(1, tt / 1.0) * np.minimum(1, (DUR - tt) / 2.5)
st = np.stack([L * fade, R * fade], axis=1)
st *= 0.5 / np.max(np.abs(st))
sf.write(OUT, st.astype(np.float32), SR, subtype="PCM_16")
print("wrote", OUT, DUR, "s")
