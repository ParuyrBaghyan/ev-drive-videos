"""Stereo music bed + sound design + voice, ducked, -> mix.wav (48 kHz stereo)."""
import json, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly, fftconvolve, butter, sosfilt

D = sys.argv[1]
tim = json.load(open(f"{D}/timing.json")); SC = {s["id"]: s for s in tim["scenes"]}
v, vsr = sf.read(f"{D}/voice.wav", dtype="float32")
SR = 48000
voice = resample_poly(v, 2, 1).astype(np.float64)          # 24k -> 48k
N = len(voice); t = np.arange(N) / SR
rng = np.random.default_rng(11)

def lp(x, fc, order=2): return sosfilt(butter(order, fc / (SR / 2), "low", output="sos"), x)
def hp(x, fc, order=2): return sosfilt(butter(order, fc / (SR / 2), "high", output="sos"), x)
def saw(f, ph=0.0): return 2 * ((t * f + ph) % 1.0) - 1

# --- music: Am - F - C - G pad, 84 bpm
bpm = 84; beat = 60 / bpm; bar = beat * 4
prog = [[57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]]
mid = lambda n: 440 * 2 ** ((n - 69) / 12)
padL = np.zeros(N); padR = np.zeros(N); bass = np.zeros(N); pl = np.zeros(N)
for ci in range(int(N / SR / bar) + 2):
    s0 = int(ci * bar * SR); s1 = min(int((ci + 1) * bar * SR + 0.6 * SR), N)
    if s0 >= N: break
    seg = slice(s0, s1); st = np.arange(s1 - s0) / SR
    env = np.minimum(1, st / 0.9) * np.clip((bar + 0.6 - st) / 0.9, 0, 1)
    tt = t[seg]
    for n in prog[ci % 4]:
        f = mid(n)
        padL[seg] += (2 * ((tt * f * 1.003) % 1) - 1) * env * 0.05 + (2 * ((tt * f * 0.501) % 1) - 1) * env * 0.02
        padR[seg] += (2 * ((tt * f * 0.997 + 0.3) % 1) - 1) * env * 0.05 + (2 * ((tt * f * 0.499 + .2) % 1) - 1) * env * 0.02
    fb = mid(prog[ci % 4][0] - 24)
    bass[seg] += np.sin(2 * np.pi * fb * tt) * env * 0.16
    # plucks: arpeggio 8th notes
    for k in range(8):
        n = prog[ci % 4][k % 3] + (12 if k % 4 == 3 else 0) + 12
        p0 = s0 + int(k * beat / 2 * SR); L = int(0.5 * SR)
        if p0 + L >= N: break
        pt = np.arange(L) / SR
        pl[p0:p0 + L] += np.sin(2 * np.pi * mid(n) * pt) * np.exp(-pt * 7) * (0.05 if k % 2 == 0 else 0.035) * (1 + 0.3 * np.sin(2 * np.pi * mid(n) * 2 * pt))
lfo = 0.5 + 0.5 * np.sin(2 * np.pi * t / (bar * 2))
padL = lp(padL, 900 + 700 * lfo.mean()); padR = lp(padR, 900 + 700 * lfo.mean())
# soft kick on beats 1 and 3 after the hook, hats on off-beats
kick = np.zeros(N); hat = np.zeros(N)
for b in range(int(N / SR / beat)):
    p0 = int(b * beat * SR)
    if p0 / SR < SC["lift"]["start"] - 0.2 or p0 / SR > SC["end"]["start"] + 1.2: continue
    if b % 2 == 0:
        L = int(0.3 * SR); kt = np.arange(L) / SR
        if p0 + L < N: kick[p0:p0 + L] += np.sin(2 * np.pi * (46 + 70 * np.exp(-kt * 28)) * kt) * np.exp(-kt * 9) * 0.32
    h0 = p0 + int(beat / 2 * SR); L = int(0.06 * SR)
    if h0 + L < N: hat[h0:h0 + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / SR * 70) * 0.035
hat = hp(hat, 6000)
# reverb
ir_len = int(2.2 * SR); irt = np.arange(ir_len) / SR
irL = rng.standard_normal(ir_len) * np.exp(-irt * 2.6); irR = rng.standard_normal(ir_len) * np.exp(-irt * 2.6)
irL /= np.sqrt(np.sum(irL ** 2)); irR /= np.sqrt(np.sum(irR ** 2))
wetL = fftconvolve(padL + pl, irL)[:N] * 0.35; wetR = fftconvolve(padR + pl, irR)[:N] * 0.35
musL = padL + pl * 0.9 + bass + kick + hat * 0.8 + wetL
musR = padR + pl * 1.1 + bass + kick + hat * 1.2 + wetR
fade = np.minimum(1, t / 1.5) * np.clip((N / SR - t) / 2.0, 0, 1)
musL *= fade; musR *= fade

# --- ducking under speech (exact word timings)
env = np.zeros(N)
for s in tim["scenes"]:
    for w in s["words"]: env[int(w["s"] * SR):int((w["e"] + 0.08) * SR)] = 1
k = int(0.25 * SR); env = np.convolve(env, np.ones(k) / k, mode="same")
duck = 1 - 0.55 * env
mpk = max(np.max(np.abs(musL)), np.max(np.abs(musR)))
musL = musL / mpk * 0.22 * duck; musR = musR / mpk * 0.22 * duck

# --- sound design
sfxL = np.zeros(N); sfxR = np.zeros(N)
def add(sig, at, pan=0.0, g=1.0):
    p0 = int(at * SR); L = min(len(sig), N - p0)
    if p0 < 0 or L <= 0: return
    sfxL[p0:p0 + L] += sig[:L] * g * (1 - pan) ; sfxR[p0:p0 + L] += sig[:L] * g * (1 + pan)
def whoosh(dur=0.9, up=True):
    L = int(dur * SR); x = rng.standard_normal(L); u = np.linspace(0, 1, L)
    x = lp(x, 2500); env = np.sin(np.pi * u) ** 2 * (u if up else 1 - u + 0.2)
    return hp(x * env, 200) * 0.5
for sid in ("lift", "regen", "stop", "light", "end"):
    add(whoosh(1.0), SC[sid]["start"] - 0.7, pan=(-0.4 if sid in ("regen", "light") else 0.4), g=0.55)
# electric hum rising (motor -> generator), then held during regen
tL = SC["lift"]["start"]; tR = SC["regen"]["start"]; tS = SC["stop"]["start"]
L = int((tS + 1.5 - tL - 1.0) * SR); ht = np.arange(L) / SR
f = 110 + 90 * np.clip(ht / 1.2, 0, 1) - 50 * np.clip((ht - (tS - tL - 1.0)) / 2.5, 0, 1)
ph = 2 * np.pi * np.cumsum(f) / SR
hum = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3.01 * ph)) * np.minimum(1, ht / 0.6) * np.clip((L / SR - ht) / 1.0, 0, 1)
add(lp(hum, 1200) * 0.10, tL + 1.0)
# chime: brake lights on
tB = SC["light"]["start"]
L = int(1.6 * SR); ct = np.arange(L) / SR
chime = sum(np.sin(2 * np.pi * fr * ct) * np.exp(-ct * d) * a for fr, d, a in ((1318.5, 3.5, 0.5), (1975.5, 4.5, 0.3), (2637, 6, 0.15)))
add(chime * 0.10, tB + 0.9, pan=-0.2)
# soft impact on end card
tE = SC["end"]["start"]
L = int(1.4 * SR); it = np.arange(L) / SR
imp = np.sin(2 * np.pi * (40 + 60 * np.exp(-it * 12)) * it) * np.exp(-it * 3.5) * 0.5 + lp(rng.standard_normal(L), 800) * np.exp(-it * 9) * 0.25
add(imp * 0.5, tE + 1.6)
# ticks while the battery counter climbs
for i in range(14):
    at = tR + 0.7 + i * (tS - tR - 0.8) / 14
    L = int(0.03 * SR); bt = np.arange(L) / SR
    add(np.sin(2 * np.pi * 2400 * bt) * np.exp(-bt * 160) * 0.05, at, pan=0.5)

L = voice + musL + sfxL; R = voice + musR + sfxR
pk = max(np.max(np.abs(L)), np.max(np.abs(R)))
sf.write(f"{D}/mix.wav", np.stack([L, R], 1) / pk * 0.95, SR)
print("mix ok", round(N / SR, 2))
