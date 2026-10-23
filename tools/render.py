"""Render a 1080x1920 graphics-only Short from script.json + timing.json + voice.wav."""
import json, math, subprocess, sys, re
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else f"{BASE}/short.mp4"
PREVIEW = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None

W, H, FPS = 1080, 1920, 30
BG = (10, 13, 18)
ACC = (198, 255, 61)      # electric lime
ACC2 = (255, 122, 61)     # orange
WHITE = (244, 246, 248)
MUTED = (120, 132, 150)
GRIDC = (22, 28, 37)
F = "/usr/share/fonts/opentype/inter/"
def font(name, size): return ImageFont.truetype(F + name, size)
ACC_RGB = ACC

cfg = json.load(open(f"{BASE}/script.json"))
tim = json.load(open(f"{BASE}/timing.json"))
TOTAL = tim["total"]
scenes = []
for s, t in zip(cfg["scenes"], tim["scenes"]):
    scenes.append({**s, **t})
# each scene's visual stays until the next scene starts
for i, s in enumerate(scenes):
    s["vis_end"] = scenes[i + 1]["start"] if i + 1 < len(scenes) else TOTAL

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_inout(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def back_out(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------- captions: chunk words, time proportional to characters ----------
captions = []
for s in scenes:
    words = s["text"].split()
    weights = [len(re.sub(r"[^\w]", "", w)) + 1.5 for w in words]
    tot = sum(weights); dur = s["end"] - s["start"]; t = s["start"]
    wt = []
    for w, wg in zip(words, weights):
        d = dur * wg / tot; wt.append((w, t, t + d)); t += d
    chunk = []
    for i, item in enumerate(wt):
        chunk.append(item)
        end_punct = item[0][-1] in ".,:?!"
        if len(chunk) == 3 or end_punct or i == len(wt) - 1:
            captions.append(chunk); chunk = []

CAP_FONT = font("InterDisplay-Black.otf", 92)
def draw_captions(img, t):
    cur = None
    for c in captions:
        if c[0][1] <= t < c[-1][2] + 0.12: cur = c
    if not cur: return
    d = ImageDraw.Draw(img)
    words = [w for w, _, _ in cur]
    text_w = [d.textlength(w.upper(), font=CAP_FONT) for w in words]
    space = 26
    lines, line, lw = [], [], 0
    for i, w in enumerate(words):
        if line and lw + space + text_w[i] > 940:
            lines.append(line); line, lw = [], 0
        lw += (space if line else 0) + text_w[i]; line.append(i)
    lines.append(line)
    pop = back_out((t - cur[0][1]) / 0.18)
    y0 = 1330 - (len(lines) - 1) * 55
    for li, ln in enumerate(lines):
        total = sum(text_w[i] for i in ln) + space * (len(ln) - 1)
        x = (W - total) / 2; y = y0 + li * 112
        for i in ln:
            w, ws, we = cur[i]
            active = ws <= t < we
            col = ACC if active else WHITE
            sc = 0.85 + 0.15 * pop
            # shadow
            tw = text_w[i]
            layer_txt = w.upper()
            fsz = int(92 * sc)
            f2 = font("InterDisplay-Black.otf", fsz)
            ox = x + (tw - d.textlength(layer_txt, font=f2)) / 2
            d.text((ox + 4, y + 6), layer_txt, font=f2, fill=(0, 0, 0))
            d.text((ox, y), layer_txt, font=f2, fill=col, stroke_width=3, stroke_fill=(0, 0, 0))
            x += tw + space

# ---------- static background ----------
def make_bg():
    img = Image.new("RGB", (W, H), BG)
    return img
BG_IMG = make_bg()
glow = Image.new("L", (W, H), 0)
ImageDraw.Draw(glow).ellipse((140, 420, 940, 1220), fill=255)
glow = glow.filter(ImageFilter.GaussianBlur(160))

def background(t, accent):
    img = BG_IMG.copy()
    d = ImageDraw.Draw(img)
    off = (t * 18) % 90
    for x in range(-90, W + 90, 90):
        d.line([(x + off, 0), (x + off, H)], fill=GRIDC, width=2)
    for y in range(-90, H + 90, 90):
        d.line([(0, y + off), (W, y + off)], fill=GRIDC, width=2)
    pulse = 0.16 + 0.04 * math.sin(t * 2.2)
    col = Image.new("RGB", (W, H), accent)
    img = Image.composite(col, img, glow.point(lambda v: int(v * pulse)))
    return img

# ---------- vector helpers on 2x layer (900x900 logical -> 1800 px) ----------
S = 2
VW = 900
def L(): return Image.new("RGBA", (VW * S, VW * S), (0, 0, 0, 0))
def p(*xy): return [v * S for v in xy]
def arc(d, cx, cy, r, a0, a1, col, w):
    d.arc(p(cx - r, cy - r, cx + r, cy + r), a0, a1, fill=col, width=int(w * S))
def rgba(c, a): return (c[0], c[1], c[2], int(clamp(a) * 255))

def speaker(d, cx, cy, sc, col, alpha=1.0):
    c = rgba(col, alpha)
    d.rounded_rectangle(p(cx - 70 * sc, cy - 45 * sc, cx - 10 * sc, cy + 45 * sc), radius=12 * S * sc, fill=c)
    d.polygon(p(cx - 18 * sc, cy - 45 * sc, cx + 50 * sc, cy - 105 * sc, cx + 50 * sc, cy + 105 * sc, cx - 18 * sc, cy + 45 * sc), fill=c)

def waves(d, cx, cy, t, col, n=3, base=80, gap=55, alpha=1.0, w=16):
    for i in range(n):
        ph = (t * 1.6 + i / n) % 1.0
        r = base + gap * i + ph * 20
        a = alpha * (1 - ph * 0.6)
        arc(d, cx, cy, r, -45, 45, rgba(col, a), w)

def car_side(d, x, y, sc, body, alpha=1.0, glass=(10, 13, 18)):
    c = rgba(body, alpha)
    pts = [(-230, 40), (-230, -10), (-200, -40), (-110, -50), (-60, -110), (90, -112), (160, -55), (225, -40), (238, 0), (238, 40)]
    d.polygon(p(*[v for xx, yy in pts for v in (x + xx * sc, y + yy * sc)]), fill=c)
    g = rgba(glass, alpha)
    d.polygon(p(x - 45 * sc, y - 95 * sc, x + 10 * sc, y - 97 * sc, x + 10 * sc, y - 52 * sc, x - 90 * sc, y - 52 * sc), fill=g)
    d.polygon(p(x + 25 * sc, y - 97 * sc, x + 82 * sc, y - 97 * sc, x + 130 * sc, y - 52 * sc, x + 25 * sc, y - 52 * sc), fill=g)
    for wx in (-140, 140):
        d.ellipse(p(x + (wx - 52) * sc, y + (40 - 52) * sc, x + (wx + 52) * sc, y + (40 + 52) * sc), fill=rgba((10, 13, 18), alpha))
        d.ellipse(p(x + (wx - 40) * sc, y + (40 - 40) * sc, x + (wx + 40) * sc, y + (40 + 40) * sc), fill=rgba((60, 68, 80), alpha))
        d.ellipse(p(x + (wx - 16) * sc, y + (40 - 16) * sc, x + (wx + 16) * sc, y + (40 + 16) * sc), fill=c)
    # headlight
    d.line(p(x + 205 * sc, y - 22 * sc, x + 232 * sc, y - 16 * sc), fill=rgba(ACC, alpha), width=int(8 * S * sc))

def person(d, x, y, sc, col, alpha=1.0, t=0):
    c = rgba(col, alpha); w = int(16 * S * sc)
    d.ellipse(p(x - 28 * sc, y - 190 * sc, x + 28 * sc, y - 134 * sc), fill=c)
    d.line(p(x, y - 125 * sc, x, y - 30 * sc), fill=c, width=w)
    sw = math.sin(t * 6) * 28
    d.line(p(x, y - 30 * sc, x - 30 * sc + sw * sc, y + 50 * sc), fill=c, width=w)
    d.line(p(x, y - 30 * sc, x + 30 * sc - sw * sc, y + 50 * sc), fill=c, width=w)
    d.line(p(x, y - 105 * sc, x - 40 * sc - sw * sc, y - 40 * sc), fill=c, width=w)
    d.line(p(x, y - 105 * sc, x + 40 * sc + sw * sc, y - 40 * sc), fill=c, width=w)

def text_c(d, x, y, s, f, col):
    tw = d.textlength(s, font=f)
    d.text(((x * S) - tw / 2, y * S), s, font=f, fill=col)

def tire(d, cx, cy, r, ang, col, alpha=1.0):
    d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=rgba((30, 36, 46), alpha))
    d.ellipse(p(cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62), fill=rgba((70, 78, 92), alpha))
    for k in range(14):
        a = ang + k * 2 * math.pi / 14
        x0, y0 = cx + math.cos(a) * r * 0.86, cy + math.sin(a) * r * 0.86
        x1, y1 = cx + math.cos(a) * r * 0.98, cy + math.sin(a) * r * 0.98
        d.line(p(x0, y0, x1, y1), fill=rgba(MUTED, alpha), width=int(10 * S))
    for k in range(5):
        a = ang + k * 2 * math.pi / 5
        d.line(p(cx, cy, cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55), fill=rgba(col, alpha), width=int(12 * S))
    d.ellipse(p(cx - 18, cy - 18, cx + 18, cy + 18), fill=rgba(col, alpha))

# ---------- scene visuals (logical 900x900) ----------
FL = lambda n, s: font(n, s * S)
def vis_speaker(d, lt, t):
    k = back_out(lt / 0.45)
    speaker(d, 360, 430, 1.6 * k, WHITE)
    waves(d, 400, 430, t, ACC, n=3, base=110, gap=70, alpha=k, w=20)
    text_c(d, 450, 700, "SHHH… IT'S ON PURPOSE", FL("InterDisplay-Bold.otf", 40), rgba(MUTED, ease_out(lt / 0.8)))

def vis_pedestrian(d, lt, t):
    x = -250 + 560 * ease_out(lt / 2.2)
    d.line(p(40, 560, 860, 560), fill=rgba(GRIDC if False else (40, 48, 60), 1), width=6 * S)
    car_side(d, x, 470, 0.95, WHITE)
    person(d, 740, 500, 1.15, ACC, t=t)
    # muted icon above car
    a = ease_out((lt - 0.4) / 0.4)
    speaker(d, x + 10, 220, 0.6, MUTED, a)
    d.line(p(x - 60, 160, x + 70, 290), fill=rgba(ACC2, a), width=14 * S)
    text_c(d, 450, 700, "NEAR-SILENT", FL("InterDisplay-Black.otf", 64), rgba(ACC2, a))

def vis_avas(d, lt, t):
    f = FL("InterDisplay-Black.otf", 230)
    letters = "AVAS"; widths = [d.textlength(c, font=f) for c in letters]
    tot = sum(widths) + 20 * S * 3; x = (VW * S - tot) / 2
    for i, c in enumerate(letters):
        k = back_out((lt - 0.12 * i) / 0.4)
        if k <= 0: x += widths[i] + 20 * S; continue
        d.text((x, (300 - 60 * (1 - k)) * S), c, font=f, fill=rgba(ACC, clamp(k)))
        x += widths[i] + 20 * S
    sub = ["ACOUSTIC", "VEHICLE", "ALERTING", "SYSTEM"]
    for i, w in enumerate(sub):
        a = ease_out((lt - 2.0 - 0.25 * i) / 0.35)
        text_c(d, 450, 560 + i * 58, w, FL("InterDisplay-Bold.otf", 46), rgba(WHITE if i % 2 == 0 else MUTED, a))
    a = ease_out((lt - 0.8) / 0.4)
    speaker(d, 450, 190, 0.55, WHITE, a)
    waves(d, 470, 190, t, ACC, n=2, base=50, gap=35, alpha=a, w=10)

def gauge(d, cx, cy, r, speed, maxs, lt, show_us, alpha=1.0):
    a0, a1 = 150, 390
    def ang(v): return a0 + (a1 - a0) * v / maxs
    arc(d, cx, cy, r, a0, a1, rgba((40, 48, 60), alpha), 36)
    arc(d, cx, cy, r, a0, ang(20), rgba(ACC, alpha), 36)
    if show_us > 0:
        arc(d, cx, cy, r, ang(20), ang(20 + 10 * ease_out(show_us)), rgba(ACC2, alpha), 36)
    fs = FL("Inter-SemiBold.otf", 30)
    for v in range(0, maxs + 1, 10):
        a = math.radians(ang(v))
        tx, ty = cx + math.cos(a) * (r - 75), cy + math.sin(a) * (r - 75)
        tw = d.textlength(str(v), font=fs)
        d.text((tx * S - tw / 2, ty * S - 18 * S), str(v), font=fs, fill=rgba(MUTED, alpha))
    na = math.radians(ang(speed))
    d.line(p(cx, cy, cx + math.cos(na) * (r - 30), cy + math.sin(na) * (r - 30)), fill=rgba(WHITE, alpha), width=12 * S)
    d.ellipse(p(cx - 26, cy - 26, cx + 26, cy + 26), fill=rgba(WHITE, alpha))

def vis_gauge(d, lt, t):
    dur = scenes[3]["vis_end"] - scenes[3]["start"]
    half = dur * 0.5
    if lt < half:
        spd = 20 * ease_inout(lt / (half * 0.7)); us = 0
    else:
        spd = 20 + 10 * ease_inout((lt - half) / (half * 0.6)); us = (lt - half) / 0.5
    gauge(d, 450, 430, 300, spd, 60, lt, us)
    text_c(d, 450, 470, f"{int(round(spd))}", FL("InterDisplay-Black.otf", 110), rgba(WHITE, 1))
    text_c(d, 450, 600, "km/h", FL("Inter-SemiBold.otf", 36), rgba(MUTED, 1))
    a1 = ease_out(lt / 0.4)
    d.rounded_rectangle(p(130, 720, 420, 820), radius=24 * S, fill=rgba(ACC, a1))
    text_c(d, 275, 742, "EU  < 20", FL("InterDisplay-Black.otf", 46), rgba(BG, a1))
    a2 = ease_out((lt - half) / 0.4)
    d.rounded_rectangle(p(480, 720, 770, 820), radius=24 * S, fill=rgba(ACC2, a2))
    text_c(d, 625, 742, "US  ≈ 30", FL("InterDisplay-Black.otf", 46), rgba(BG, a2))

def vis_tires(d, lt, t):
    spd = 30 + 25 * ease_inout(lt / 2.5)
    gauge(d, 450, 300, 200, spd, 60, lt, 1, alpha=1)
    text_c(d, 450, 425, f"{int(round(spd))} km/h", FL("InterDisplay-Black.otf", 56), rgba(WHITE, 1))
    ang = t * (4 + spd * 0.25)
    tire(d, 300, 700, 120, ang, ACC)
    k = ease_out((lt - 0.8) / 0.6)
    # tire noise waves grow
    for i in range(3):
        ph = (t * 2.4 + i / 3) % 1.0
        arc(d, 300, 700, 150 + i * 40 + ph * 20, -50, 50, rgba(ACC, k * (1 - ph * 0.6)), 12)
    # speaker fades + slash
    sa = 1 - 0.6 * k
    speaker(d, 690, 700, 0.75, WHITE, sa)
    d.line(p(620, 610, 770, 790), fill=rgba(ACC2, k), width=14 * S)

def vis_outro(d, lt, t):
    dur = scenes[5]["vis_end"] - scenes[5]["start"]
    if lt < dur * 0.45:
        x = 100 + 350 * ease_out(lt / 1.2)
        d.line(p(40, 520, 860, 520), fill=rgba((40, 48, 60), 1), width=6 * S)
        car_side(d, x, 430, 1.0, WHITE)
        waves(d, x + 250, 400, t, ACC, n=3, base=40, gap=40, alpha=1, w=12)
        text_c(d, 450, 650, "THAT HUM = A SPEAKER", FL("InterDisplay-Black.otf", 56), rgba(ACC, ease_out((lt - 0.6) / 0.4)))
    else:
        k = back_out((lt - dur * 0.45) / 0.5)
        # bolt
        bx, by, bs = 450, 260, 1.7 * k
        pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
        d.polygon(p(*[v for xx, yy in pts for v in (bx + xx * bs, by + yy * bs)]), fill=rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.45 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

VIS = {"speaker": vis_speaker, "pedestrian": vis_pedestrian, "avas": vis_avas,
       "gauge": vis_gauge, "tires": vis_tires, "outro": vis_outro}

# Episode-specific visuals: BASE/visuals.py may define new vis_* functions and
# add them to VIS (or replace helpers). It runs with this module's globals.
import os
if os.path.exists(f"{BASE}/visuals.py"):
    exec(compile(open(f"{BASE}/visuals.py").read(), f"{BASE}/visuals.py", "exec"), globals())

BADGE_F = font("InterDisplay-Black.otf", 40)
def header(img, t):
    d = ImageDraw.Draw(img)
    # progress bar
    d.rectangle((0, 0, int(W * t / TOTAL), 10), fill=ACC)
    # badge
    d.rounded_rectangle((W / 2 - 150, 120, W / 2 + 150, 196), radius=38, fill=(22, 28, 37), outline=(48, 58, 72), width=3)
    pts = [(-4, -24), (-18, 3), (-6, 3), (-10, 22), (8, -4), (-2, -4)]
    bx, by = W / 2 - 92, 158
    d.polygon([(bx + x * 1.1, by + y * 1.1) for x, y in pts], fill=ACC)
    d.text((W / 2 - 62, 134), "EV DRIVE", font=BADGE_F, fill=WHITE)

def frame(t):
    img = background(t, ACC)
    for i, s in enumerate(scenes):
        st = s["start"] if i else 0.0
        if st <= t < s["vis_end"] or (i == len(scenes) - 1 and t >= st):
            lt = t - st
            fin = ease_out(lt / 0.3)
            fout = 1 - ease_inout((t - (s["vis_end"] - 0.25)) / 0.25) if i < len(scenes) - 1 else 1
            layer = L(); d = ImageDraw.Draw(layer)
            VIS[s["visual"]](d, lt, t)
            layer = layer.resize((VW, VW), Image.LANCZOS)
            a = clamp(min(fin, fout))
            if a < 1:
                al = layer.getchannel("A").point(lambda v: int(v * a)); layer.putalpha(al)
            sc = 0.94 + 0.06 * fin
            if sc < 0.999:
                nw = int(VW * sc); layer = layer.resize((nw, nw), Image.BILINEAR)
            else: nw = VW
            img.paste(layer, ((W - nw) // 2, 300 + (VW - nw) // 2), layer)
    header(img, t)
    draw_captions(img, t)
    return img

if PREVIEW:
    for tt in PREVIEW:
        frame(tt).save(f"{BASE}/preview_{tt:05.1f}.png")
    sys.exit()

# ---------- audio: music bed + whooshes + voice ----------
voice, sr = sf.read(f"{BASE}/voice.wav")
n = len(voice); tt = np.arange(n) / sr
bpm = 112; beat = 60 / bpm
music = np.zeros(n)
chords = [[110, 164.81, 220, 261.63], [87.31, 130.81, 174.61, 220], [98, 146.83, 196, 246.94], [82.41, 123.47, 164.81, 207.65]]
bar = beat * 4
for ci in range(int(TOTAL / bar) + 1):
    s0 = int(ci * bar * sr); s1 = min(int((ci + 1) * bar * sr), n)
    if s0 >= n: break
    seg_t = np.arange(s1 - s0) / sr
    env = np.minimum(1, seg_t / 0.4) * np.minimum(1, (bar - seg_t) / 0.4)
    for f in chords[ci % 4]:
        music[s0:s1] += 0.05 * np.sin(2 * np.pi * f * seg_t) * env
        music[s0:s1] += 0.015 * np.sin(2 * np.pi * f * 2.005 * seg_t) * env
# kick + hat
for b in range(int(TOTAL / beat)):
    s0 = int(b * beat * sr); L_ = int(0.25 * sr)
    if s0 + L_ > n: break
    kt = np.arange(L_) / sr
    music[s0:s0 + L_] += 0.35 * np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14)
    h0 = s0 + int(beat * sr / 2); hl = int(0.05 * sr)
    if h0 + hl < n:
        music[h0:h0 + hl] += 0.04 * np.random.randn(hl) * np.exp(-np.arange(hl) / sr * 80)
# whooshes at scene changes
rng = np.random.default_rng(1)
for s in scenes[1:]:
    c = int((s["start"] - 0.15) * sr); L_ = int(0.45 * sr)
    if c < 0 or c + L_ > n: continue
    noise = rng.standard_normal(L_)
    noise = np.convolve(noise, np.ones(30) / 30, mode="same")
    env = np.sin(np.linspace(0, np.pi, L_)) ** 2
    music[c:c + L_] += 0.5 * noise * env
fade = np.minimum(1, tt / 1.0) * np.minimum(1, (TOTAL - tt) / 1.2)
music *= fade
music = music / np.max(np.abs(music)) * 0.16
mix = voice + music
mix = mix / np.max(np.abs(mix)) * 0.95
sf.write(f"{BASE}/mix.wav", mix, sr)

nframes = int(TOTAL * FPS)
proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                         "-i", f"{BASE}/mix.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(nframes):
    proc.stdin.write(frame(i / FPS).tobytes())
    if i % 150 == 0: print(f"frame {i}/{nframes}", flush=True)
proc.stdin.close(); proc.wait()
print("done", OUT)
