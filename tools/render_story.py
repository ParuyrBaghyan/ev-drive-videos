"""Cartoon story Shorts engine (original EV DRIVE characters, flat cartoon rooms, big word captions).
Usage: render_story.py EP OUT.mp4            -> full render (voice.wav + timing.json from tools/tts_edge_long.py)
       render_story.py EP preview t1,t2,...  -> EP/prev_<t>.png
EP/scenes.py defines scene functions  sc_<visual>(d, lt, t, s)  and registers them in SCENES.
All coordinates are final pixels (1080x1920); drawing is 2x supersampled.
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

EP = sys.argv[1]
W, H, FPS, S = 1080, 1920, 30, 2
FD = "/usr/share/fonts/opentype/inter/"
_fc = {}
def font(px, name="InterDisplay-Black.otf"):
    px = max(2, px); k = (name, int(px))
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + name, int(px))
    return _fc[k]

INK = (24, 26, 38)            # outline colour
WHITE = (255, 255, 255); LIME = (198, 255, 61); YELLOW = (255, 214, 64); ORANGE = (255, 138, 60)
RED = (240, 84, 84); GREEN = (84, 214, 120); BLUE = (86, 156, 255); SKIN = (255, 214, 170); SKIN2 = (214, 158, 112)

tim = json.load(open(f"{EP}/timing.json")); TOTAL = tim["total"]
scenes = tim["scenes"]
for i, s in enumerate(scenes):
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

# ---------------- drawing primitives (final px in, 2x canvas out) ----------------
def P(pts): return [(x * S, y * S) for x, y in pts]
def rect(d, x0, y0, x1, y1, fill, r=0, ol=None, w=6):
    if x1 <= x0 or y1 <= y0: return
    box = (x0 * S, y0 * S, x1 * S, y1 * S)
    if r: d.rounded_rectangle(box, radius=min(r, (x1 - x0) / 2, (y1 - y0) / 2) * S, fill=fill, outline=ol, width=int(w * S) if ol else 0)
    else: d.rectangle(box, fill=fill, outline=ol, width=int(w * S) if ol else 0)
def circ(d, x, y, r, fill, ol=None, w=6):
    if r <= 0: return
    d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=fill, outline=ol, width=int(w * S) if ol else 0)
def oval(d, x, y, rx, ry, fill, ol=None, w=6):
    d.ellipse(((x - rx) * S, (y - ry) * S, (x + rx) * S, (y + ry) * S), fill=fill, outline=ol, width=int(w * S) if ol else 0)
def poly(d, pts, fill, ol=None, w=6):
    d.polygon(P(pts), fill=fill)
    if ol: d.line(P(pts + [pts[0]]), fill=ol, width=int(w * S), joint="curve")
def line(d, pts, col, w=8):
    d.line(P(pts), fill=col, width=int(w * S), joint="curve")
    r = w / 2
    for x, y in (pts[0], pts[-1]): circ(d, x, y, r, col)
def limb(d, x0, y0, x1, y1, col, w, ol=INK, ow=5):
    line(d, [(x0, y0), (x1, y1)], ol, w + ow * 2); line(d, [(x0, y0), (x1, y1)], col, w)
def text(d, x, y, s, size, col, anchor="mm", stroke=0, scol=INK, name="InterDisplay-Black.otf"):
    d.text((x * S, y * S), s, font=font(size * S, name), fill=col, anchor=anchor, stroke_width=int(stroke * S), stroke_fill=scol)
def pill(d, x, y, s, size, bg, fg=INK, k=1.0):
    if k <= 0: return
    sz = size * k; f = font(sz * S); tw = d.textlength(s, font=f) / S
    rect(d, x - tw / 2 - sz * 0.6, y - sz * 0.8, x + tw / 2 + sz * 0.6, y + sz * 0.8, bg, r=sz * 0.8, ol=INK, w=6)
    text(d, x, y, s, sz, fg)
def bolt(d, x, y, s, col, ol=INK):
    pts = [(x + 0.15 * s, y - s), (x - 0.55 * s, y + 0.12 * s), (x - 0.05 * s, y + 0.12 * s), (x - 0.2 * s, y + s), (x + 0.55 * s, y - 0.2 * s), (x + 0.05 * s, y - 0.2 * s)]
    poly(d, pts, col, ol, max(3, s * 0.08))

# ---------------- original characters ----------------
def person(d, x, y, h, shirt, hair, t, mood="smile", arm_l=-0.25, arm_r=0.25, skin=SKIN, pants=(52, 60, 92), face=1, bob=True):
    """x = centre, y = feet, h = height. hair: 'cap' | 'spiky'. mood: smile | sad | wow | flat. arms: angle from straight down (rad)."""
    u = h / 10.0
    y = y + (math.sin(t * 2.6 + x * 0.01) * 0.12 * u if bob else 0)
    hip = y - 3.2 * u
    for sx in (-1, 1):                                   # legs + shoes
        limb(d, x + sx * 0.8 * u, hip, x + sx * 0.95 * u, y - 0.35 * u, pants, 1.0 * u)
        oval(d, x + sx * 1.15 * u + face * 0.2 * u, y - 0.2 * u, 0.95 * u, 0.48 * u, (245, 245, 250), INK, 5)
    sh_y = y - 6.3 * u
    def arm(sx, ang):
        ax, ay = x + sx * 1.75 * u, sh_y
        hx, hy = ax + math.sin(ang) * 3.0 * u, ay + math.cos(ang) * 3.0 * u
        limb(d, ax, ay, hx, hy, shirt, 0.95 * u)
        circ(d, hx, hy, 0.62 * u, skin, INK, 5)
    arm(-1, arm_l)
    rect(d, x - 1.9 * u, y - 6.9 * u, x + 1.9 * u, y - 2.7 * u, shirt, r=1.5 * u, ol=INK, w=6)     # torso
    rect(d, x - 0.5 * u, y - 5.3 * u, x + 0.5 * u, y - 4.3 * u, mix(shirt, WHITE, 0.55), r=0.3 * u)  # pocket patch
    arm(1, arm_r)
    hy = y - 8.35 * u; r = 1.95 * u                       # head
    circ(d, x, hy, r, skin, INK, 6)
    if hair == "cap":
        d.pieslice(((x - r * 1.04) * S, (hy - r * 1.1) * S, (x + r * 1.04) * S, (hy + r * 0.98) * S), 180, 360, fill=shirt, outline=INK, width=6 * S)
        rect(d, x + face * r * 0.25 - r * 0.9, hy - 0.2 * u, x + face * r * 0.25 + r * 0.9 + (r * 0.5 if face > 0 else 0) - (0 if face > 0 else 0), hy + 0.22 * u, mix(shirt, INK, 0.35), r=0.2 * u, ol=INK, w=5)
    else:
        pts = [(x - r * 1.0, hy - r * 0.25)]
        for i in range(6):
            a = math.pi - i * math.pi / 5
            pts.append((x + math.cos(a) * r * 1.25, hy - 0.15 * r - math.sin(a) * r * 1.3))
            if i < 5:
                a2 = a - math.pi / 10
                pts.append((x + math.cos(a2) * r * 0.9, hy - 0.2 * r - math.sin(a2) * r * 0.82))
        pts.append((x + r * 1.0, hy - r * 0.25))
        poly(d, pts, (70, 48, 40), INK, 5)
    blink = (t * 1.0 + x * 0.013) % 3.4 < 0.13
    ex = face * 0.25 * u
    for sx in (-1, 1):
        if blink: line(d, [(x + ex + sx * 0.75 * u - 0.3 * u, hy + 0.25 * u), (x + ex + sx * 0.75 * u + 0.3 * u, hy + 0.25 * u)], INK, 0.16 * u)
        else:
            circ(d, x + ex + sx * 0.75 * u, hy + 0.25 * u, (0.34 if mood != "wow" else 0.42) * u, INK)
            circ(d, x + ex + sx * 0.75 * u + 0.1 * u, hy + 0.15 * u, 0.11 * u, WHITE)
        if mood == "sad": line(d, [(x + ex + sx * 1.15 * u, hy - 0.45 * u), (x + ex + sx * 0.4 * u, hy - 0.72 * u)], INK, 0.16 * u)
    my = hy + 1.05 * u
    if mood == "smile": d.arc(((x + ex - 0.7 * u) * S, (my - 0.75 * u) * S, (x + ex + 0.7 * u) * S, (my + 0.3 * u) * S), 20, 160, fill=INK, width=int(0.2 * u * S))
    elif mood == "sad": d.arc(((x + ex - 0.6 * u) * S, (my - 0.05 * u) * S, (x + ex + 0.6 * u) * S, (my + 0.9 * u) * S), 200, 340, fill=INK, width=int(0.2 * u * S))
    elif mood == "wow": oval(d, x + ex, my + 0.05 * u, 0.36 * u, 0.5 * u, (120, 40, 50), INK, 4)
    else: line(d, [(x + ex - 0.45 * u, my), (x + ex + 0.45 * u, my)], INK, 0.18 * u)

def car(d, x, y, w, col, t=0.0, spin=0.0, face=1, lights=True):
    """x = centre, y = ground line, w = length. Chunky original cartoon EV, side view."""
    u = w / 10.0; f = face
    def X(a): return x + f * a * u
    wr = 1.05 * u
    oval(d, x, y + 0.1 * u, 5.2 * u, 0.35 * u, (0, 0, 0, 60))                       # ground shadow
    body = [(X(-4.9), y - 1.0 * u), (X(-4.9), y - 2.5 * u), (X(-4.3), y - 3.0 * u), (X(-2.6), y - 3.2 * u), (X(-1.4), y - 4.7 * u),
            (X(1.5), y - 4.7 * u), (X(3.0), y - 3.2 * u), (X(4.5), y - 2.9 * u), (X(5.0), y - 2.2 * u), (X(5.0), y - 1.0 * u)]
    poly(d, body, col, INK, 7)
    glass = [(X(-2.0), y - 3.25 * u), (X(-1.1), y - 4.3 * u), (X(1.3), y - 4.3 * u), (X(2.4), y - 3.25 * u)]
    poly(d, glass, (190, 228, 250), INK, 5)
    line(d, [(X(0.1), y - 4.3 * u), (X(0.1), y - 3.25 * u)], INK, 5)
    rect(d, min(X(-4.9), X(5.0)), y - 1.35 * u, max(X(-4.9), X(5.0)), y - 0.95 * u, mix(col, INK, 0.45), r=0.2 * u, ol=INK, w=5)   # sill
    line(d, [(X(0.3), y - 2.6 * u), (X(1.0), y - 2.6 * u)], INK, 6)                   # door handle
    if lights:
        rect(d, min(X(4.2), X(4.95)), y - 2.55 * u, max(X(4.2), X(4.95)), y - 2.2 * u, (255, 244, 190), r=0.15 * u, ol=INK, w=4)
        rect(d, min(X(-4.85), X(-4.3)), y - 2.6 * u, max(X(-4.85), X(-4.3)), y - 2.25 * u, RED, r=0.15 * u, ol=INK, w=4)
    for a in (-3.0, 3.1):
        cx = X(a)
        circ(d, cx, y - wr, wr, (40, 42, 54), INK, 6); circ(d, cx, y - wr, wr * 0.55, (214, 220, 230), INK, 4)
        for k in range(5):
            an = spin + k * 2 * math.pi / 5
            line(d, [(cx, y - wr), (cx + math.cos(an) * wr * 0.5, y - wr + math.sin(an) * wr * 0.5)], INK, 4)
    return X(-3.9), y - 2.3 * u   # charge-port position (rear quarter)

def battery(d, x, y, w, pct, col, label=None, k=1.0):
    if k <= 0: return
    w *= k; h = w * 0.5
    rect(d, x - w / 2, y - h / 2, x + w / 2, y + h / 2, (250, 250, 252), r=h * 0.2, ol=INK, w=7)
    rect(d, x + w / 2 - 2, y - h * 0.2, x + w / 2 + w * 0.06, y + h * 0.2, INK, r=4)
    fw = (w - 22) * clamp(pct / 100)
    if fw > 6: rect(d, x - w / 2 + 11, y - h / 2 + 11, x - w / 2 + 11 + fw, y + h / 2 - 11, col, r=h * 0.12)
    if label: text(d, x, y, label, h * 0.56, INK)

def cable(d, x0, y0, x1, y1, sag, col, t, speed, n, dot, w=10):
    pts = []
    for i in range(25):
        u = i / 24; pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + math.sin(u * math.pi) * sag))
    line(d, pts, INK, w + 8); line(d, pts, col, w)
    for i in range(n):
        u = (t * speed + i / n) % 1.0; j = min(23, int(u * 24)); fr = u * 24 - j
        px = pts[j][0] + (pts[j + 1][0] - pts[j][0]) * fr; py = pts[j][1] + (pts[j + 1][1] - pts[j][1]) * fr
        circ(d, px, py, dot, LIME, INK, 3)

def room(d, wall, floor, horizon=1080, stripe=None):
    rect(d, 0, 0, W, horizon, wall); rect(d, 0, horizon, W, H, floor)
    if stripe: rect(d, 0, horizon - 26, W, horizon, stripe)
    line(d, [(0, horizon), (W, horizon)], INK, 7)
    for i in range(1, 6):                                   # floor perspective lines
        x = W / 2 + (i - 3) * 260
        d.line(P([(W / 2 + (i - 3) * 150, horizon), (x + (i - 3) * 380, H)]), fill=mix(floor, INK, 0.12), width=4 * S)

SCENES = {}
exec(compile(open(f"{EP}/scenes.py").read(), f"{EP}/scenes.py", "exec"), globals())

# ---------------- captions: 1-3 words at a time, centred, active word highlighted ----------------
GROUPS = []
g = []
for i, w in enumerate(WORDS):
    g.append(w)
    end_s = w["w"][-1] in ".?!,:"
    if len(g) == 3 or end_s or sum(len(x["w"]) for x in g) > 13 or i == len(WORDS) - 1:
        GROUPS.append(g); g = []
for i, g in enumerate(GROUPS):
    g[0]["gs"] = g[0]["s"]; g[0]["ge"] = GROUPS[i + 1][0]["s"] if i + 1 < len(GROUPS) and GROUPS[i + 1][0]["s"] - g[-1]["e"] < 0.6 else g[-1]["e"] + 0.25
CAPY = 1330
def captions(img, t):
    cur = next((g for g in GROUPS if g[0]["gs"] <= t < g[0]["ge"]), None)
    if not cur: return
    d = ImageDraw.Draw(img)
    k = 0.86 + 0.14 * pop((t - cur[0]["gs"]) / 0.14)
    size = 104
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

def badge(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, int(W * t / TOTAL), 10), fill=LIME)
    d.rounded_rectangle((W / 2 - 132, 150, W / 2 + 132, 214), radius=32, fill=INK)
    pts = [(-4, -24), (-18, 3), (-6, 3), (-10, 22), (8, -4), (-2, -4)]
    d.polygon([(W / 2 - 92 + px * 0.95, 182 + py * 0.95) for px, py in pts], fill=LIME)
    d.text((W / 2 + 18, 182), "EV DRIVE", font=font(34), fill=WHITE, anchor="mm")

def frame(t):
    s = next((x for x in scenes if x["vs"] <= t < x["ve"]), scenes[-1])
    big = Image.new("RGB", (W * S, H * S), (30, 34, 52)); d = ImageDraw.Draw(big, "RGBA")
    lt = t - s["vs"]
    SCENES[s["visual"]](d, lt, t, s)
    img = big.resize((W, H), Image.LANCZOS)
    k = 1 - smooth(lt / 0.16)                              # quick punch-in at each cut
    if k > 0.01 and s is not scenes[0]:
        z = 1 + 0.06 * k; nw, nh = int(W * z), int(H * z)
        img = img.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    badge(img, t); captions(img, t)
    return img

def _frame_bytes(i): return frame(i / FPS).tobytes()

def audio():
    v, sr = sf.read(f"{EP}/voice.wav"); n = len(v); rng = np.random.default_rng(3)
    mus = np.zeros(n); beat = 60 / 96; bar = beat * 4
    chords = [[130.81, 164.81, 196.0], [110.0, 130.81, 164.81], [87.31, 110.0, 130.81], [98.0, 123.47, 146.83]]
    for ci in range(int(TOTAL / bar) + 1):
        for bi in range(8):                                 # plucky marimba-like arpeggio
            s0 = int((ci * bar + bi * beat / 2) * sr); L = int(0.45 * sr)
            if s0 + L > n: break
            tt = np.arange(L) / sr; f = chords[ci % 4][bi % 3] * (2 if bi % 4 == 3 else 1)
            mus[s0:s0 + L] += 0.10 * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) + 0.03 * np.sin(2 * np.pi * f * 3 * tt) * np.exp(-tt * 16)
        for b in range(4):
            s0 = int((ci * bar + b * beat) * sr); L = int(0.2 * sr)
            if s0 + L > n: break
            tt = np.arange(L) / sr
            mus[s0:s0 + L] += 0.16 * np.sin(2 * np.pi * (48 + 70 * np.exp(-tt * 35)) * tt) * np.exp(-tt * 16)
    fx = np.zeros(n)
    for s in scenes[1:]:                                    # whoosh on each cut
        c = int((s["vs"] - 0.1) * sr); L = int(0.4 * sr)
        if c < 0 or c + L > n: continue
        nz = np.convolve(rng.standard_normal(L), np.ones(40) / 40, mode="same")
        fx[c:c + L] += 0.9 * nz * np.sin(np.linspace(0, np.pi, L)) ** 2
    for tp in globals().get("POPS", []):                    # scene-defined pop sounds
        c = int(tp * sr); L = int(0.12 * sr)
        if c + L > n: continue
        tt = np.arange(L) / sr
        fx[c:c + L] += 0.25 * np.sin(2 * np.pi * (520 + 500 * tt / 0.12) * tt) * np.exp(-tt * 28)
    mixed = v * 1.0 + mus * 0.42 + fx * 0.5
    mixed = mixed / np.max(np.abs(mixed)) * 0.92
    sf.write(f"{EP}/mix.wav", mixed, sr)

if __name__ == "__main__":
    if sys.argv[2] == "preview":
        for tt in [float(x) for x in sys.argv[3].split(",")]:
            frame(tt).save(f"{EP}/prev_{tt:05.1f}.png")
        sys.exit()
    OUT = sys.argv[2]; audio()
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
                           "-i", f"{EP}/mix.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    with Pool(int(os.environ.get("PROCS", "2"))) as pool:
        for i, b in enumerate(pool.imap(_frame_bytes, range(n), chunksize=8)):
            ff.stdin.write(b)
            if i % 150 == 0: print("frame", i, "/", n, flush=True)
    ff.stdin.close(); ff.wait(); os.remove(f"{EP}/mix.wav")
    print("done", OUT)
