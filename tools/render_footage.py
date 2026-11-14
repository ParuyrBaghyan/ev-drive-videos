"""Real-footage Shorts: stock clips (footage/pexels/*.mp4) + voiceover + word captions + number overlays.
Usage: render_footage.py EP OUT.mp4 | render_footage.py EP preview t1,t2
script.json scenes: {visual, clip, speed, ss (start offset in the clip, s), text}; EP/overlays.py defines ov_<visual>(d, lt, t, s).
Voice + timing.json come from tools/tts_edge_long.py.
"""
import json, math, os, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

EP = sys.argv[1]; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, "footage", "pexels")
W, H, FPS = 1080, 1920, 30
FD = "/usr/share/fonts/opentype/inter/"
_fc = {}
def font(px, name="InterDisplay-Black.otf"):
    k = (name, max(2, int(px)))
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + name, k[1])
    return _fc[k]
INK = (14, 16, 24); WHITE = (255, 255, 255); LIME = (198, 255, 61); YELLOW = (255, 214, 64); ORANGE = (255, 138, 60); RED = (240, 84, 84); GREEN = (84, 214, 120)

cfg = json.load(open(f"{EP}/script.json")); tim = json.load(open(f"{EP}/timing.json")); TOTAL = tim["total"]
scenes = tim["scenes"]
for i, s in enumerate(scenes):
    s.update({k: v for k, v in cfg["scenes"][i].items() if k in ("clip", "speed", "ss")})
    s["vs"] = 0.0 if i == 0 else s["start"] - 0.12
    s["ve"] = scenes[i + 1]["start"] - 0.12 if i + 1 < len(scenes) else TOTAL
WORDS = [w for s in scenes for se in s["sentences"] for w in se["words"]]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def pop(x):
    x = clamp(x); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def mix(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * clamp(k)) for i in range(3))
def sent(s, k): return s["sentences"][min(k, len(s["sentences"]) - 1)]["start"] - s["vs"]

# ---- overlay helpers (draw on an RGBA layer, final pixels) ----
def rect(d, x0, y0, x1, y1, fill, r=0, ol=None, w=5):
    if x1 <= x0 or y1 <= y0: return
    d.rounded_rectangle((x0, y0, x1, y1), radius=min(r, (x1 - x0) / 2, (y1 - y0) / 2), fill=fill, outline=ol, width=w if ol else 0)
def text(d, x, y, s, size, col, anchor="mm", stroke=0, scol=INK, name="InterDisplay-Black.otf"):
    d.text((x, y), s, font=font(size, name), fill=col, anchor=anchor, stroke_width=int(stroke), stroke_fill=scol)
def pill(d, x, y, s, size, bg, fg=INK, k=1.0):
    if k <= 0.02: return
    sz = size * k; tw = d.textlength(s, font=font(sz))
    rect(d, x - tw / 2 - sz * 0.6, y - sz * 0.8, x + tw / 2 + sz * 0.6, y + sz * 0.8, bg, r=sz * 0.8, ol=INK, w=5)
    text(d, x, y, s, sz, fg)
def card(d, x0, y0, x1, y1, a=0.82): rect(d, x0, y0, x1, y1, (14, 16, 24, int(255 * a)), r=40, ol=(255, 255, 255, 60), w=3)
def battery(d, x, y, w, pct, col, label=None):
    h = w * 0.5
    rect(d, x - w / 2, y - h / 2, x + w / 2, y + h / 2, (250, 250, 252), r=h * 0.2, ol=INK, w=7)
    rect(d, x + w / 2 - 2, y - h * 0.2, x + w / 2 + w * 0.06, y + h * 0.2, INK, r=4)
    fw = (w - 22) * clamp(pct / 100)
    if fw > 6: rect(d, x - w / 2 + 11, y - h / 2 + 11, x - w / 2 + 11 + fw, y + h / 2 - 11, col, r=h * 0.12)
    if label: text(d, x, y, label, h * 0.56, INK)

OV = {}
exec(compile(open(f"{EP}/overlays.py").read(), f"{EP}/overlays.py", "exec"), globals())

# ---- captions ----
GROUPS = []; g = []
for i, w in enumerate(WORDS):
    g.append(w)
    if len(g) == 3 or w["w"][-1] in ".?!,:" or sum(len(x["w"]) for x in g) > 13 or i == len(WORDS) - 1:
        GROUPS.append(g); g = []
for i, g in enumerate(GROUPS):
    g[0]["gs"] = g[0]["s"]; g[0]["ge"] = GROUPS[i + 1][0]["s"] if i + 1 < len(GROUPS) and GROUPS[i + 1][0]["s"] - g[-1]["e"] < 0.6 else g[-1]["e"] + 0.25
CAPY = 1360
def captions(d, t):
    cur = next((g for g in GROUPS if g[0]["gs"] <= t < g[0]["ge"]), None)
    if not cur: return
    k = 0.86 + 0.14 * pop((t - cur[0]["gs"]) / 0.14); size = 104
    f = font(size * k); ws = [w["w"].upper() for w in cur]; sp = 26 * k
    tw = [d.textlength(x, font=f) for x in ws]; tot = sum(tw) + sp * (len(ws) - 1)
    if tot > 980:
        k *= 980 / tot; f = font(size * k); sp = 26 * k; tw = [d.textlength(x, font=f) for x in ws]; tot = sum(tw) + sp * (len(ws) - 1)
    x = (W - tot) / 2
    for i, w in enumerate(cur):
        act = w["s"] <= t < (cur[i + 1]["s"] if i + 1 < len(cur) else cur[0]["ge"])
        d.text((x + 5, CAPY + 8), ws[i], font=f, fill=(0, 0, 0), anchor="lm", stroke_width=int(11 * k), stroke_fill=(0, 0, 0))
        d.text((x, CAPY), ws[i], font=f, fill=YELLOW if act else WHITE, anchor="lm", stroke_width=int(11 * k), stroke_fill=INK)
        x += tw[i] + sp

def badge(d, t):
    d.rectangle((0, 0, int(W * t / TOTAL), 10), fill=LIME)
    d.rounded_rectangle((W / 2 - 132, 150, W / 2 + 132, 214), radius=32, fill=INK)
    pts = [(-4, -24), (-18, 3), (-6, 3), (-10, 22), (8, -4), (-2, -4)]
    d.polygon([(W / 2 - 92 + px * 0.95, 182 + py * 0.95) for px, py in pts], fill=LIME)
    d.text((W / 2 + 18, 182), "EV DRIVE", font=font(34), fill=WHITE, anchor="mm")

# soft dark gradient so captions and numbers stay readable on any footage
_g = np.zeros((H, W), np.float32); yy = np.arange(H)[:, None] / H
_g[:] = 0.22 + 0.38 * np.clip((yy - 0.45) / 0.4, 0, 1) + 0.25 * np.clip((0.18 - yy) / 0.18, 0, 1)
SHADE = (1 - _g)[:, :, None]

def clip_reader(s, n):
    """ffmpeg pipe: n frames of the scene's clip, scaled+cropped to 1080x1920, looped, slowed."""
    sp = s.get("speed", 1.0)
    vf = f"setpts=PTS/{sp},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},eq=saturation=1.12:contrast=1.04"
    cmd = ["ffmpeg", "-v", "error", "-stream_loop", "-1", "-ss", str(s.get("ss", 0)), "-i", os.path.join(CLIPS, s["clip"]), "-an", "-vf", vf,
           "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)

def compose(raw, s, t, first):
    lt = t - s["vs"]
    a = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) * SHADE
    z = 1 + 0.05 * (lt / max(0.1, s["ve"] - s["vs"]))                       # slow push-in
    img = Image.fromarray(a.astype(np.uint8))
    if not first:
        k = 1 - smooth(lt / 0.16); z += 0.06 * k
    nw, nh = int(W * z), int(H * z)
    img = img.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    OV[s["visual"]](d, lt, t, s); badge(d, t); captions(d, t)
    img.paste(layer, (0, 0), layer)
    return img

def audio():
    v, sr = sf.read(f"{EP}/voice.wav"); n = len(v); rng = np.random.default_rng(3)
    mus = np.zeros(n); beat = 60 / 100; bar = beat * 4
    chords = [[110.0, 164.81, 220.0], [87.31, 130.81, 174.61], [98.0, 146.83, 196.0], [82.41, 123.47, 164.81]]
    for ci in range(int(TOTAL / bar) + 1):
        s0 = int(ci * bar * sr); s1 = min(int((ci + 1) * bar * sr), n)
        if s0 >= n: break
        tt = np.arange(s1 - s0) / sr; env = np.minimum(1, tt / 0.4) * np.minimum(1, (bar - tt) / 0.4)
        for f in chords[ci % 4]: mus[s0:s1] += 0.05 * np.sin(2 * np.pi * f * tt) * env + 0.012 * np.sin(2 * np.pi * f * 2.004 * tt) * env
        for b in range(4):
            k0 = int((ci * bar + b * beat) * sr); L = int(0.22 * sr)
            if k0 + L > n: break
            kt = np.arange(L) / sr
            mus[k0:k0 + L] += 0.3 * np.sin(2 * np.pi * (48 + 80 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14)
    fx = np.zeros(n)
    for s in scenes[1:]:
        c = int((s["vs"] - 0.1) * sr); L = int(0.4 * sr)
        if c < 0 or c + L > n: continue
        nz = np.convolve(rng.standard_normal(L), np.ones(40) / 40, mode="same")
        fx[c:c + L] += 0.9 * nz * np.sin(np.linspace(0, np.pi, L)) ** 2
    m = v + mus * 0.5 + fx * 0.5; m = m / np.max(np.abs(m)) * 0.92
    sf.write(f"{EP}/mix.wav", m, sr)

if __name__ == "__main__":
    NF = int(TOTAL * FPS)
    bounds = [(s, int(round(s["vs"] * FPS)), int(round(s["ve"] * FPS)) if s is not scenes[-1] else NF) for s in scenes]
    if sys.argv[2] == "preview":
        for tt in [float(x) for x in sys.argv[3].split(",")]:
            s, f0, f1 = next(b for b in bounds if b[1] <= int(tt * FPS) < b[2])
            k = int(tt * FPS) - f0; p = clip_reader(s, k + 1); raw = None
            for _ in range(k + 1): raw = p.stdout.read(W * H * 3)
            p.kill(); compose(raw, s, tt, s is scenes[0]).save(f"{EP}/prev_{tt:05.1f}.png")
        sys.exit()
    OUT = sys.argv[2]; audio()
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
                           "-i", f"{EP}/mix.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for s, f0, f1 in bounds:
        p = clip_reader(s, f1 - f0)
        for i in range(f0, f1):
            raw = p.stdout.read(W * H * 3)
            if len(raw) < W * H * 3: break
            ff.stdin.write(compose(raw, s, i / FPS, s is scenes[0]).tobytes())
        p.kill(); print("scene", s["visual"], "done", flush=True)
    ff.stdin.close(); ff.wait(); os.remove(f"{EP}/mix.wav"); print("done", OUT)
