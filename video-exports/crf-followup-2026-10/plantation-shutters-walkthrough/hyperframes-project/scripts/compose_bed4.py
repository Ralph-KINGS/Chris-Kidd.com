"""Original soft music bed: fingerpicked plucked-string (Karplus-Strong) guitar with a low cello-like drone. A major, 92 bpm.

Usage: python3 compose_bed4.py <out.wav> [seconds]
"""
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
OUT = sys.argv[1]
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 40.0
rng = np.random.default_rng(92)
N = int(DUR * SR)
E8 = 60 / 92 / 2


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, s, sig, gain=1.0):
    s0 = int(s * SR)
    if s0 >= N:
        return
    e = min(N, s0 + len(sig))
    buf[s0:e] += sig[: e - s0] * gain


def pluck(f, length=2.5, damp=0.996):
    n = int(length * SR)
    period = int(SR / f)
    buf = rng.uniform(-1, 1, period)
    buf = np.convolve(buf, np.ones(4) / 4, mode="same")  # softer attack (thumb, not pick)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = damp * 0.5 * (buf[i % period] + buf[(i + 1) % period])
    return out


# A - E/G# - F#m - D ; bass note then picked upper strings (travis-style)
chords = [
    (45, [57, 61, 64, 69]),
    (44, [56, 59, 64, 68]),
    (42, [57, 61, 66, 69]),
    (38, [57, 62, 66, 69]),
]
order = [None, 2, 1, 3, None, 2, 1, 0]  # None = bass on beats 1 and 3

cache = {}


def note(m, length):
    key = (m, length)
    if key not in cache:
        cache[key] = pluck(hz(m), length)
    return cache[key]


gtr = np.zeros(N)
drone = np.zeros(N)
bar = 8 * E8
b = 0
while b * bar < DUR:
    root, tones = chords[b % 4]
    t0 = b * bar
    for k, o in enumerate(order):
        if o is None:
            place(gtr, t0 + k * E8, note(root + (0 if k == 0 else 7), 2.5), 0.9)
        else:
            place(gtr, t0 + k * E8 + rng.uniform(0, 0.012), note(tones[o], 2.0), 0.55 + 0.1 * rng.random())
    tt = np.arange(int((bar + 0.6) * SR)) / SR
    f = hz(root + 12)
    env = np.minimum(1, tt / 0.8) * np.minimum(1, (bar + 0.6 - tt) / 0.6)
    place(drone, t0, (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * env)
    b += 1

gtr = sosfilt(butter(2, 3500, "low", fs=SR, output="sos"), gtr)
gtr = sosfilt(butter(1, 90, "high", fs=SR, output="sos"), gtr)
drone = sosfilt(butter(2, 900, "low", fs=SR, output="sos"), drone)
for x in (gtr, drone):
    x /= np.max(np.abs(x)) + 1e-9
dry = 0.75 * gtr + 0.22 * drone

ir_len = int(1.6 * SR)
ir_t = np.arange(ir_len) / SR
lp = butter(2, 5000, "low", fs=SR, output="sos")
irL = sosfilt(lp, rng.standard_normal(ir_len) * np.exp(-ir_t * 4))
irR = sosfilt(lp, rng.standard_normal(ir_len) * np.exp(-ir_t * 4))
wetL = fftconvolve(dry, irL)[:N]
wetR = fftconvolve(dry, irR)[:N]
wetL /= np.max(np.abs(wetL)); wetR /= np.max(np.abs(wetR))
L = 0.8 * dry + 0.3 * wetL
R = 0.8 * dry + 0.3 * wetR

t = np.arange(N) / SR
fade = np.minimum(1, t / 1.0) * np.minimum(1, (DUR - t) / 2.5)
st = np.stack([L * fade, R * fade], axis=1)
st *= 0.5 / np.max(np.abs(st))
sf.write(OUT, st.astype(np.float32), SR, subtype="PCM_16")
print("wrote", OUT, DUR, "s")
