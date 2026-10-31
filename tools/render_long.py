"""Render a 16:9 long-form EV DRIVE video.
EP must contain script.json, timing.json (from tts_long.py), voice.wav and visuals.py.
Usage:
  render_long.py EP preview t1,t2,...      -> EP/prev_<t>.png at full size
  render_long.py EP render OUT.mp4 [jobs]   -> one file per scene, concat, mix audio
"""
import json, math, os, re, subprocess, sys, shutil
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EP = sys.argv[1]
W, H, FPS = 1920, 1080, 30
BG = (10, 13, 18)
ACC = (198, 255, 61)
ACC2 = (255, 122, 61)
WHITE = (244, 246, 248)
MUTED = (120, 132, 150)
DARK = (40, 48, 60)
PANEL = (20, 26, 35)
AIR = (110, 190, 255)
HOT = (255, 92, 72)
GRIDC = (20, 26, 34)
FDIR = "/usr/share/fonts/opentype/inter/"

# visual layer: logical LW x LH drawn at S x, then reduced; pasted at (VX, VY)
LW, LH, S = 1500, 720, 2
VX, VY = (W - LW) // 2, 118

cfg = json.load(open(f"{EP}/script.json"))
tim = json.load(open(f"{EP}/timing.json"))
TOTAL = tim["total"]
scenes = tim["scenes"]
CHAPTERS = cfg["chapters"]
CH_GAP = 2.2

# segment = what is on screen: chapter starts begin CH_GAP early (chapter card)
for i, s in enumerate(scenes):
    s["seg_start"] = 0.0 if i == 0 else (s["start"] - CH_GAP if s["chapter_start"] else s["start"] - 0.19)
for i, s in enumerate(scenes):
    s["seg_end"] = scenes[i + 1]["seg_start"] if i + 1 < len(scenes) else TOTAL
    s["vis_start"] = s["start"] - (0.6 if s["chapter_start"] and i else 0.19 if i else 0)

# ---------- helpers ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_inout(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def back_out(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k
def rgba(c, a=1.0): return (int(c[0]), int(c[1]), int(c[2]), int(clamp(a) * 255))
def mix(c1, c2, k): return tuple(int(lerp(c1[i], c2[i], clamp(k))) for i in range(3))
def p(*xy): return [v * S for v in xy]

_fc = {}
def font(name, px):
    key = (name, int(px))
    if key not in _fc:
        _fc[key] = ImageFont.truetype(FDIR + name, max(1, int(px)))
    return _fc[key]
def FL(name, size): return font(name, size * S)  # logical-size font for the visual layer
BLACK, BOLD, SEMI = "InterDisplay-Black.otf", "InterDisplay-Bold.otf", "Inter-SemiBold.otf"

def text_c(d, x, y, s, size, col, name=BOLD):
    f = FL(name, size); tw = d.textlength(s, font=f)
    d.text((x * S - tw / 2, y * S), s, font=f, fill=col)
def text_l(d, x, y, s, size, col, name=BOLD):
    d.text((x * S, y * S), s, font=FL(name, size), fill=col)
def text_r(d, x, y, s, size, col, name=BOLD):
    f = FL(name, size); tw = d.textlength(s, font=f)
    d.text((x * S - tw, y * S), s, font=f, fill=col)
def poly(d, pts, col): d.polygon(p(*[v for xy in pts for v in xy]), fill=col)
def line(d, pts, col, w):
    if len(pts) > 1: d.line(p(*[v for xy in pts for v in xy]), fill=col, width=int(w * S), joint="curve")
def circle(d, x, y, r, col, outline=None, w=0):
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=col, outline=outline, width=int(w * S))
def arc(d, cx, cy, r, a0, a1, col, w):
    d.arc(p(cx - r, cy - r, cx + r, cy + r), a0, a1, fill=col, width=int(w * S))
def rrect(d, x0, y0, x1, y1, r, col, outline=None, w=0):
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=r * S, fill=col, outline=outline, width=int(w * S))
def panel(d, x0, y0, x1, y1, a=1.0, r=28):
    rrect(d, x0 + 6, y0 + 10, x1 + 6, y1 + 10, r, rgba((0, 0, 0), 0.35 * a))
    rrect(d, x0, y0, x1, y1, r, rgba(PANEL, 0.94 * a), rgba(DARK, a), 3)
def glow_line(d, pts, col, a=1.0, w=8):
    line(d, pts, rgba(col, 0.16 * a), w * 3.2)
    line(d, pts, rgba(col, a), w)
def arrow(d, x0, y0, x1, y1, col, w=8, a=1.0, head=26):
    ang = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - math.cos(ang) * head * 0.8, y1 - math.sin(ang) * head * 0.8
    line(d, [(x0, y0), (bx, by)], rgba(col, a), w)
    poly(d, [(x1, y1), (x1 - math.cos(ang - 0.45) * head, y1 - math.sin(ang - 0.45) * head),
             (x1 - math.cos(ang + 0.45) * head, y1 - math.sin(ang + 0.45) * head)], rgba(col, a))

def path_point(pts, u):
    """point at fraction u (0..1) along polyline"""
    segs = [(pts[i], pts[i + 1], math.dist(pts[i], pts[i + 1])) for i in range(len(pts) - 1)]
    L = sum(s[2] for s in segs) or 1
    tgt = (u % 1.0) * L
    for a, b, l in segs:
        if tgt <= l:
            k = tgt / l if l else 0
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k))
        tgt -= l
    return pts[-1]
def flow(d, pts, t, col, a=1.0, n=6, r=8, speed=0.35, trail=True):
    """animated energy dots travelling along a polyline"""
    for i in range(n):
        u = (t * speed + i / n) % 1.0
        x, y = path_point(pts, u)
        if trail:
            circle(d, x, y, r * 2.2, rgba(col, 0.18 * a))
        circle(d, x, y, r, rgba(col, a))
def partial(pts, k):
    """polyline drawn up to fraction k"""
    if k <= 0: return []
    if k >= 1: return pts
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = sum(segs); tgt = L * k; out = [pts[0]]
    for i, l in enumerate(segs):
        if tgt <= l:
            kk = tgt / l if l else 0
            out.append((lerp(pts[i][0], pts[i + 1][0], kk), lerp(pts[i][1], pts[i + 1][1], kk)))
            return out
        out.append(pts[i + 1]); tgt -= l
    return out
def bolt(d, x, y, s, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + a * s, y + b * s) for a, b in pts], col)

# ---------- background ----------
_grid = Image.new("RGB", (W + 120, H + 120), BG)
_gd = ImageDraw.Draw(_grid)
for x in range(0, W + 120, 60): _gd.line([(x, 0), (x, H + 120)], fill=GRIDC, width=1)
for y in range(0, H + 120, 60): _gd.line([(0, y), (W + 120, y)], fill=GRIDC, width=1)
_glow = Image.new("L", (W, H), 0)
ImageDraw.Draw(_glow).ellipse((W / 2 - 700, 0, W / 2 + 700, 900), fill=255)
_glow = _glow.filter(ImageFilter.GaussianBlur(220))
_accimg = Image.new("RGB", (W, H), ACC)
_glow_masks = {}
def background(t):
    off = int(t * 12) % 60
    img = _grid.crop((off, off, off + W, off + H))
    lvl = round((0.10 + 0.025 * math.sin(t * 1.3)) * 40)
    if lvl not in _glow_masks:
        _glow_masks[lvl] = _glow.point(lambda v: int(v * lvl / 40))
    return Image.composite(_accimg, img, _glow_masks[lvl])

# ---------- captions ----------
CAP_F = font(BOLD, 44)
def build_captions():
    caps = []
    dtmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for sc in scenes:
        for se in sc["sentences"]:
            words = se["text"].split()
            wts = [len(re.sub(r"[^\w]", "", w)) + 2 for w in words]
            tot = sum(wts); dur = se["end"] - se["start"]; t0 = se["start"]
            timed = []
            for w, wt in zip(words, wts):
                dd = dur * wt / tot; timed.append((w, t0, t0 + dd)); t0 += dd
            # chunk into lines of <= 1500px, max 2 lines per caption
            chunk, lines, cur = [], [], []
            def width(ws): return dtmp.textlength(" ".join(x[0] for x in ws), font=CAP_F)
            for item in timed:
                if cur and width(cur + [item]) > 1480:
                    lines.append(cur); cur = []
                    if len(lines) == 2:
                        caps.append(lines); lines = []
                cur.append(item)
            if cur: lines.append(cur)
            if lines: caps.append(lines)
    return caps
CAPS = build_captions()
def draw_captions(img, t):
    cur = None
    for c in CAPS:
        if c[0][0][1] - 0.05 <= t < c[-1][-1][2] + 0.25: cur = c
    if not cur: return
    d = ImageDraw.Draw(img, "RGBA")
    y0 = 908 if len(cur) == 2 else 940
    for li, ln in enumerate(cur):
        s = " ".join(w for w, _, _ in ln)
        tw = d.textlength(s, font=CAP_F)
        x = (W - tw) / 2; y = y0 + li * 60
        d.rounded_rectangle((x - 22, y - 8, x + tw + 22, y + 58), radius=14, fill=(8, 10, 14, 170))
        for w, ws, we in ln:
            col = ACC if ws <= t < we + 0.05 else WHITE
            d.text((x, y), w, font=CAP_F, fill=col)
            x += d.textlength(w + " ", font=CAP_F)

# ---------- header / chapter UI ----------
HEAD_F = font(BLACK, 30); TAG_F = font(BOLD, 26)
CH_ORDER = list(CHAPTERS.keys())
def header(img, t, sc):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, int(W * t / TOTAL), 6), fill=ACC)
    # chapter tick marks on progress bar
    for c in scenes:
        if c["chapter_start"] and c["i"]:
            x = int(W * c["seg_start"] / TOTAL)
            d.rectangle((x - 2, 0, x + 1, 12), fill=WHITE)
    # brand
    bx = W - 250
    d.rounded_rectangle((bx, 34, bx + 200, 84), radius=25, fill=(22, 28, 37, 230), outline=(48, 58, 72), width=2)
    pts = [(-4, -24), (-18, 3), (-6, 3), (-10, 22), (8, -4), (-2, -4)]
    d.polygon([(bx + 32 + x * 0.85, 59 + y * 0.85) for x, y in pts], fill=ACC)
    d.text((bx + 52, 42), "EV DRIVE", font=HEAD_F, fill=WHITE)
    # chapter tag
    if sc["ch"] != "intro":
        lab = CHAPTERS[sc["ch"]].upper()
        num, _, name = lab.partition("  ")
        tw = d.textlength(name or num, font=TAG_F)
        x0 = 50
        if name:
            d.rounded_rectangle((x0, 34, x0 + 70 + tw + 30, 84), radius=25, fill=(22, 28, 37, 230), outline=(48, 58, 72), width=2)
            d.rounded_rectangle((x0 + 6, 40, x0 + 64, 78), radius=19, fill=ACC)
            nw = d.textlength(num, font=TAG_F)
            d.text((x0 + 35 - nw / 2, 43), num, font=TAG_F, fill=BG)
            d.text((x0 + 80, 44), name, font=TAG_F, fill=WHITE)
        else:
            d.rounded_rectangle((x0, 34, x0 + tw + 50, 84), radius=25, fill=(22, 28, 37, 230), outline=(48, 58, 72), width=2)
            d.text((x0 + 25, 44), num, font=TAG_F, fill=WHITE)

CARD_NUM = font(BLACK, 220); CARD_T = font(BLACK, 92)
def chapter_card(img, t, sc):
    """big chapter title during the pause before a chapter"""
    lt = t - sc["seg_start"]; dur = sc["vis_start"] - sc["seg_start"] + 0.35
    if lt > dur: return
    a = min(ease_out(lt / 0.35), 1 - ease_inout((lt - dur + 0.45) / 0.45))
    if a <= 0: return
    lab = CHAPTERS[sc["ch"]]
    num, _, name = lab.partition("  ")
    if not name: num, name = "", lab
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    k = ease_out(lt / 0.6)
    if num:
        nw = d.textlength(num, font=CARD_NUM)
        d.text((W / 2 - nw / 2, 250 - 40 * (1 - k)), num, font=CARD_NUM, fill=rgba(ACC, 1))
    tw = d.textlength(name, font=CARD_T)
    d.text((W / 2 - tw / 2, 520 + 30 * (1 - k)), name, font=CARD_T, fill=rgba(WHITE, 1))
    lw = 220 * ease_out((lt - 0.2) / 0.6)
    d.rounded_rectangle((W / 2 - lw, 660, W / 2 + lw, 668), radius=4, fill=rgba(ACC, 1))
    if a < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    img.paste(layer, (0, 0), layer)

# ---------- episode visuals ----------
VIS = {}
exec(compile(open(f"{EP}/visuals.py").read(), f"{EP}/visuals.py", "exec"), globals())

def frame(t, si):
    sc = scenes[si]
    img = background(t)
    vis_dur = sc["seg_end"] - sc["vis_start"]
    lt = t - sc["vis_start"]
    if lt >= 0:
        fin = ease_out(lt / 0.35)
        fout = 1 - ease_inout((t - (sc["seg_end"] - 0.3)) / 0.3) if si + 1 < len(scenes) else 1.0
        a = clamp(min(fin, fout))
        if a > 0:
            layer = Image.new("RGBA", (LW * S, LH * S), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            VIS[sc["visual"]](d, lt, t, vis_dur)
            layer = layer.reduce(S)
            if a < 1:
                layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
            img.paste(layer, (VX, VY + int(14 * (1 - fin))), layer)
    header(img, t, sc)
    if sc["chapter_start"] and si:
        chapter_card(img, t, sc)
    draw_captions(img, t)
    return img

def scene_at(t):
    for i, s in enumerate(scenes):
        if s["seg_start"] <= t < s["seg_end"]: return i
    return len(scenes) - 1

def render_scene(si):
    sc = scenes[si]
    out = f"{EP}/segs/seg_{si:03d}.mp4"
    if os.path.exists(out): return out
    tmp = f"{EP}/segs/tmp_{si:03d}.mp4"
    f0 = int(round(sc["seg_start"] * FPS)); f1 = int(round(sc["seg_end"] * FPS))
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                             "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        proc.stdin.write(frame(fi / FPS, si).convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait() == 0:
        os.replace(tmp, out)
    print(f"scene {si} done ({f1 - f0} frames)", flush=True)
    return out

def music_bed(n, sr):
    tt = np.arange(n) / sr
    bpm = 96; beat = 60 / bpm; bar = beat * 4
    m = np.zeros(n)
    chords = [[110, 164.81, 220, 261.63], [87.31, 130.81, 174.61, 220], [98, 146.83, 196, 246.94], [82.41, 123.47, 164.81, 207.65]]
    for ci in range(int(n / sr / bar) + 1):
        s0 = int(ci * bar * sr); s1 = min(int((ci + 1) * bar * sr), n)
        if s0 >= n: break
        st = np.arange(s1 - s0) / sr
        env = np.minimum(1, st / 0.6) * np.minimum(1, (bar - st) / 0.6)
        for f in chords[ci % 4]:
            m[s0:s1] += 0.05 * np.sin(2 * np.pi * f * st) * env + 0.012 * np.sin(2 * np.pi * f * 2.003 * st) * env
    for b in range(int(n / sr / beat)):
        s0 = int(b * beat * sr); L = int(0.22 * sr)
        if s0 + L > n: break
        kt = np.arange(L) / sr
        m[s0:s0 + L] += 0.22 * np.sin(2 * np.pi * (48 + 80 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 16)
    rng = np.random.default_rng(3)
    for sc in scenes:
        if sc["chapter_start"] and sc["i"]:
            c = int((sc["seg_start"]) * sr); L = int(0.6 * sr)
            if c + L < n:
                nz = np.convolve(rng.standard_normal(L), np.ones(40) / 40, mode="same")
                m[c:c + L] += 0.6 * nz * np.sin(np.linspace(0, np.pi, L)) ** 2
    m *= np.minimum(1, tt / 2.0) * np.minimum(1, (n / sr - tt) / 3.0)
    return m / np.max(np.abs(m))

if __name__ == "__main__":
    mode = sys.argv[2]
    if mode == "preview":
        for tt in [float(x) for x in sys.argv[3].split(",")]:
            frame(tt, scene_at(tt)).convert("RGB").save(f"{EP}/prev_{tt:06.1f}.png")
        sys.exit()
    OUT = sys.argv[3]; jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    os.makedirs(f"{EP}/segs", exist_ok=True)
    order = sorted(range(len(scenes)), key=lambda i: -(scenes[i]["seg_end"] - scenes[i]["seg_start"]))
    with Pool(jobs) as pool:
        pool.map(render_scene, order, chunksize=1)
    with open(f"{EP}/segs/list.txt", "w") as f:
        for i in range(len(scenes)):
            f.write(f"file 'seg_{i:03d}.mp4'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{EP}/segs/list.txt", "-c", "copy", f"{EP}/video_only.mp4"], check=True)
    import soundfile as sf
    voice, sr = sf.read(f"{EP}/voice.wav")
    mus = music_bed(len(voice), sr)
    # duck music under speech
    env = np.zeros(len(voice))
    for sc in scenes:
        for se in sc["sentences"]:
            env[int(se["start"] * sr):int(se["end"] * sr)] = 1
    k = np.ones(int(0.3 * sr)) / int(0.3 * sr)
    env = np.convolve(env, k, mode="same")
    mus = mus * (0.11 - 0.055 * env)
    mixd = voice + mus
    mixd = mixd / np.max(np.abs(mixd)) * 0.95
    sf.write(f"{EP}/mix.wav", mixd, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{EP}/video_only.mp4", "-i", f"{EP}/mix.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("done", OUT)
