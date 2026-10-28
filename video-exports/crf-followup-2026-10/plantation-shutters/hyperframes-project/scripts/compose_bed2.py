"""Original light, upbeat music bed: marimba ostinato, round bass, soft shaker. G major, 100 bpm.

Usage: python3 compose_bed2.py <out.wav> [seconds]
"""
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
OUT = sys.argv[1]
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 14.0
rng = np.random.default_rng(21)
N = int(DUR * SR)
BPM = 100
E8 = 60 / BPM / 2  # eighth note


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, s, sig, gain=1.0):
    s0 = int(s * SR)
    if s0 >= N:
        return
    e = min(N, s0 + len(sig))
    buf[s0:e] += sig[: e - s0] * gain


def marimba(f, length=1.2):
    t = np.arange(int(length * SR)) / SR
    tone = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 18)
    return tone * (1 - np.exp(-t * 400)) * np.exp(-t * 5.5)


def bass(f, length):
    t = np.arange(int(length * SR)) / SR
    tone = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)
    return tone * (1 - np.exp(-t * 60)) * np.exp(-t * 1.8)


def shaker(length=0.09):
    n = int(length * SR)
    t = np.arange(n) / SR
    return rng.standard_normal(n) * np.exp(-t * 60)


# Em - C - G - D, one bar each
chords = [
    ([64, 67, 71, 76], 40),
    ([60, 64, 67, 72], 36),
    ([62, 67, 71, 74], 43),
    ([62, 66, 69, 74], 38),
]
pattern = [0, 2, 1, 3, 2, 1, 3, 2]  # chord-tone order per eighth
accent = [1.0, 0.55, 0.8, 0.55, 0.9, 0.55, 0.8, 0.6]

mar = np.zeros(N)
bas = np.zeros(N)
shk = np.zeros(N)
bar = 8 * E8
b = 0
while b * bar < DUR:
    tones, root = chords[b % 4]
    t0 = b * bar
    for k in range(8):
        f = hz(tones[pattern[k]])
        place(mar, t0 + k * E8, marimba(f), accent[k] * (0.85 + 0.15 * rng.random()))
        place(shk, t0 + k * E8, shaker(), 0.5 if k % 2 else 0.25)
    place(bas, t0, bass(hz(root), bar))
    place(bas, t0 + 5 * E8, bass(hz(root + 7), bar - 5 * E8), 0.6)
    b += 1

shk = sosfilt(butter(2, 6000, "high", fs=SR, output="sos"), shk)
bas = sosfilt(butter(2, 400, "low", fs=SR, output="sos"), bas)
for x in (mar, bas, shk):
    x /= np.max(np.abs(x)) + 1e-9
dry = 0.6 * mar + 0.35 * bas + 0.12 * shk

ir_len = int(1.4 * SR)
ir_t = np.arange(ir_len) / SR
lp = butter(2, 5000, "low", fs=SR, output="sos")
irL = sosfilt(lp, rng.standard_normal(ir_len) * np.exp(-ir_t * 4.5))
irR = sosfilt(lp, rng.standard_normal(ir_len) * np.exp(-ir_t * 4.5))
wetL = fftconvolve(dry, irL)[:N]
wetR = fftconvolve(dry, irR)[:N]
wetL /= np.max(np.abs(wetL)); wetR /= np.max(np.abs(wetR))
L = 0.8 * dry + 0.3 * wetL
R = 0.8 * dry + 0.3 * wetR

t = np.arange(N) / SR
fade = np.minimum(1, t / 0.5) * np.minimum(1, (DUR - t) / 2.0)
st = np.stack([L * fade, R * fade], axis=1)
st *= 0.5 / np.max(np.abs(st))
sf.write(OUT, st.astype(np.float32), SR, subtype="PCM_16")
print("wrote", OUT, DUR, "s")
