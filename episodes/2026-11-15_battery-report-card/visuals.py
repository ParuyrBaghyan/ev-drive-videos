# Episode visuals: Ford checked 36,000 EV batteries after 5 years (myth vs data, news peg).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
CHROME = (176, 186, 200)
RED = (255, 84, 84)
TEAL = (30, 110, 112)
TEAL2 = (18, 72, 76)

OFFY = 70  # shift everything down: canvas clips y<0
def p(*xy): return [v * S + (OFFY * S if i % 2 else 0) for i, v in enumerate(xy)]
def text_c(d, x, y, s, f, col):
    tw = d.textlength(s, font=f)
    d.text(((x * S) - tw / 2, (y + OFFY) * S), s, font=f, fill=col)
BLK = "InterDisplay-Black.otf"
SEMI = "Inter-SemiBold.otf"

def sdur(name):
    for s in scenes:
        if s["visual"] == name:
            return s["vis_end"] - (s["start"] if s is not scenes[0] else 0.0)
    return 4.0

def poly(d, pts, col):
    d.polygon(p(*[v for xy in pts for v in xy]), fill=col)

def circ(d, x, y, r, col):
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=col)

def ring(d, x, y, r, col, w):
    d.ellipse(p(x - r, y - r, x + r, y + r), outline=col, width=max(1, int(w * S)))

def line(d, pts, col, w):
    d.line(p(*[v for xy in pts for v in xy]), fill=col, width=max(1, int(w * S)), joint="curve")

def label(d, x, y, s, col, a, size=28, f=BLK):
    if a <= 0: return
    text_c(d, x, y, s, FL(f, max(1, int(size))), rgba(col, a))

def chip(d, x, y, s, col, a, size=30, tcol=None):
    if a <= 0: return
    f = FL(BLK, max(1, int(size)))
    tw = d.textlength(s, font=f) / S
    w = tw + 50
    d.rounded_rectangle(p(x - w / 2, y, x + w / 2, y + size * 1.7), radius=size * 0.85 * S, fill=rgba(col, a))
    text_c(d, x, y + size * 0.3, s, f, rgba(tcol or BG, a))

def rrect(d, x0, y0, x1, y1, r, col, outline=None, w=0):
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=r * S, fill=col, outline=outline, width=int(w * S) if w else 0)

_CARS = {}
def car_img(name, w):
    key = (name, int(w))
    if key not in _CARS:
        im = Image.open(os.path.join(os.path.dirname(BASE.rstrip("/")), "..", "assets", "cars", name + ".png")).convert("RGBA")
        bb = im.getbbox(); im = im.crop(bb)
        ww = int(w * S); hh = int(im.height * ww / im.width)
        _CARS[key] = (im.resize((ww, hh), Image.LANCZOS), bb)
    return _CARS[key]

def put_car(d, name, x, y, w, a=1.0):
    im, bb = car_img(name, w)
    if a < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * clamp(a))))
    d._image.alpha_composite(im, (int(x * S), int((y + OFFY) * S)))
    return w / (bb[2] - bb[0])

def car_pt(x, y, w, sx, sy):
    sc = w / 1110
    return x + (sx - 245) * sc, y + (sy - 367) * sc

def hand(d, x, y, sc, col, a):
    """Simple hand/fingers reaching up-left to grab (4 fingers + palm)."""
    rrect(d, x - 40 * sc, y, x + 40 * sc, y + 70 * sc, 22 * sc, rgba(col, a))
    for i in range(4):
        fx = x - 33 * sc + i * 22 * sc
        rrect(d, fx - 9 * sc, y - 42 * sc + abs(i - 1.5) * 6 * sc, fx + 9 * sc, y + 10 * sc, 9 * sc, rgba(col, a))
    rrect(d, x + 30 * sc, y + 10 * sc, x + 62 * sc, y + 30 * sc, 10 * sc, rgba(col, a))

def xmark(d, x, y, r, col, a, w=16):
    line(d, [(x - r, y - r), (x + r, y + r)], rgba(col, a), w)
    line(d, [(x - r, y + r), (x + r, y - r)], rgba(col, a), w)

def check(d, x, y, r, col, a, w=10):
    line(d, [(x - r, y), (x - r * 0.3, y + r * 0.7), (x + r, y - r * 0.7)], rgba(col, a), w)

def bolt(d, x, y, sc, col, a):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in pts], rgba(col, a))

def flame(d, x, y, sc, t, a, ph=0.0):
    for k, (col, s) in enumerate([(RED, 1.0), (ACC2, 0.72), ((255, 205, 60), 0.42)]):
        h = (90 + 18 * math.sin(t * 9 + ph + k)) * sc * s
        wd = 42 * sc * s
        pts = [(x - wd, y), (x - wd * 0.8, y - h * 0.45), (x + 6 * sc * math.sin(t * 7 + ph), y - h), (x + wd * 0.8, y - h * 0.45), (x + wd, y)]
        poly(d, pts, rgba(col, a))

BLUE = (90, 200, 255)
YEL = (255, 205, 60)

def flow(d, pts, t, a, col=ACC, n=10, r=7, speed=0.7, w=12, base=STEEL):
    """polyline cable with dots flowing along it"""
    line(d, pts, rgba(base, a), w)
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [math.hypot(b[0] - a_[0], b[1] - a_[1]) for a_, b in segs]
    tot = sum(lens)
    for i in range(n):
        u = ((t * speed + i / n) % 1.0) * tot
        for (a_, b), L_ in zip(segs, lens):
            if u <= L_:
                f = u / L_
                circ(d, a_[0] + (b[0] - a_[0]) * f, a_[1] + (b[1] - a_[1]) * f, r, rgba(col, a))
                break
            u -= L_

def pack_bar(d, x0, y0, x1, y1, level, col, a, seg=10):
    """horizontal battery with segment ticks, level 0..1"""
    rrect(d, x0 + 6, y0 + 10, x1 + 6, y1 + 10, 18, rgba((0, 0, 0), a * 0.5))
    rrect(d, x0, y0, x1, y1, 18, rgba(PANEL, a), outline=rgba(STEEL, a), w=5)
    rrect(d, x1, (y0 + y1) / 2 - 18, x1 + 16, (y0 + y1) / 2 + 18, 6, rgba(STEEL, a))
    if level > 0.005:
        rrect(d, x0 + 10, y0 + 10, x0 + 10 + (x1 - x0 - 20) * clamp(level), y1 - 10, 12, rgba(col, a))
        rrect(d, x0 + 10, y0 + 10, x0 + 10 + (x1 - x0 - 20) * clamp(level), y0 + 22, 6, rgba(WHITE, a * 0.25))
    for k in range(1, seg):
        xx = x0 + (x1 - x0) * k / seg
        line(d, [(xx, y0 + 6), (xx, y1 - 6)], rgba(BG, a * 0.5), 3)

def charger(d, x, y, sc, a, glow=0.0):
    """T-shaped flash charger post"""
    rrect(d, x - 60 * sc, y - 230 * sc, x + 60 * sc, y, 18 * sc, rgba(DARK, a), outline=rgba(STEEL, a), w=4)
    rrect(d, x - 140 * sc, y - 280 * sc, x + 140 * sc, y - 220 * sc, 20 * sc, rgba(DARK, a), outline=rgba(STEEL, a), w=4)
    rrect(d, x - 40 * sc, y - 200 * sc, x + 40 * sc, y - 140 * sc, 10 * sc, rgba(BG, a))
    rrect(d, x - 120 * sc, y - 262 * sc, x + 120 * sc, y - 240 * sc, 8 * sc, rgba(ACC, a * (0.35 + 0.65 * glow)))
    bolt(d, x, y - 170 * sc, 0.32 * sc, ACC, a)

def house(d, x, y, s, col, a):
    poly(d, [(x - s, y), (x, y - s * 0.9), (x + s, y)], rgba(col, a))
    rrect(d, x - s * 0.75, y - 2, x + s * 0.75, y + s * 0.9, 3, rgba(col, a))
    rrect(d, x - s * 0.2, y + s * 0.35, x + s * 0.2, y + s * 0.9, 2, rgba(BG, a * 0.8))

def pylon(d, x, y, sc, col, a):
    pts = [(x - 60 * sc, y), (x - 14 * sc, y - 260 * sc), (x + 14 * sc, y - 260 * sc), (x + 60 * sc, y)]
    line(d, [pts[0], pts[1]], rgba(col, a), 8); line(d, [pts[3], pts[2]], rgba(col, a), 8)
    for k, yy in enumerate((-200, -150, -90)):
        line(d, [(x - (70 - k * 12) * sc, y + yy * sc), (x + (70 - k * 12) * sc, y + yy * sc)], rgba(col, a), 7)
    line(d, [(x - 40 * sc, y - 40 * sc), (x + 30 * sc, y - 130 * sc)], rgba(col, a * 0.6), 5)
    line(d, [(x + 40 * sc, y - 40 * sc), (x - 30 * sc, y - 130 * sc)], rgba(col, a * 0.6), 5)

GREEN = (80, 220, 140)

def shield(d, x, y, s, col, a, outline=None):
    pts = [(x, y - s), (x + s * 0.85, y - s * 0.65), (x + s * 0.75, y + s * 0.25), (x, y + s), (x - s * 0.75, y + s * 0.25), (x - s * 0.85, y - s * 0.65)]
    poly(d, pts, rgba(col, a))
    if outline:
        line(d, pts + [pts[0]], rgba(outline, a), 6)

def coin(d, x, y, r, a):
    circ(d, x + 3, y + 5, r, rgba((0, 0, 0), a * 0.4))
    circ(d, x, y, r, rgba(YEL, a))
    ring(d, x, y, r * 0.78, rgba((200, 150, 20), a), 4)
    label(d, x, y - r * 0.62, "$", (150, 105, 10), a, size=r * 1.1)

def burst(d, x, y, r, col, a, n=10, rot=0.0):
    pts = []
    for i in range(n * 2):
        ang = rot + i * math.pi / n
        rr = r if i % 2 == 0 else r * 0.5
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    poly(d, pts, rgba(col, a))

def money(v):
    return f"${int(round(v)):,}"

def stamp(d, x, y, s, col, a, k, size=80, rot=0):
    if k <= 0: return
    sc = 1 + 1.2 * (1 - clamp(k))
    f = FL(BLK, max(1, int(size * sc)))
    tw = d.textlength(s, font=f) / S
    rrect(d, x - tw / 2 - 30, y - 10 * sc, x + tw / 2 + 30, y + size * sc * 1.25, 14, None, outline=rgba(col, a * clamp(k)), w=10)
    text_c(d, x, y, s, f, rgba(col, a * clamp(k)))

def timer(d, x, y, r, frac, txt, a, col=ACC):
    ring(d, x, y, r, rgba(DARK, a), 22)
    if frac > 0:
        d.arc(p(x - r, y - r, x + r, y + r), -90, -90 + 360 * clamp(frac), fill=rgba(col, a), width=int(22 * S))
    label(d, x, y - r * 0.38, txt, WHITE, a, size=r * 0.62)

ICE = (190, 225, 255)
SNOW = (235, 242, 250)
SMOKE = (150, 156, 166)

def snowfall(d, t, a, n=70, x0=0, x1=900, y0=-60, y1=820, seed=3, speed=1.0):
    for i in range(n):
        r1 = ((i * 7919 + seed * 104729) % 1000) / 1000.0
        r2 = ((i * 3571 + seed * 7727) % 1000) / 1000.0
        r3 = ((i * 2311 + seed * 911) % 1000) / 1000.0
        sp = (60 + 90 * r2) * speed
        yy = y0 + ((r1 * (y1 - y0) + t * sp) % (y1 - y0))
        xx = x0 + r3 * (x1 - x0) + 14 * math.sin(t * 1.3 + i)
        rr = 3 + 4 * r2
        circ(d, xx, yy, rr, rgba(SNOW, a * (0.35 + 0.5 * r2)))

def snow_cap(d, x0, x1, y, h, a):
    """mound of snow lying on a surface (top edge bumpy)"""
    if h <= 1: return
    pts = [(x0, y)]
    n = 14
    for k in range(n + 1):
        xx = x0 + (x1 - x0) * k / n
        bump = math.sin(k / n * math.pi) ** 0.6
        pts.append((xx, y - h * bump - 4 * math.sin(k * 2.1)))
    pts.append((x1, y))
    poly(d, pts, rgba(SNOW, a))

def thermo(d, x, y, frac, txt, a, col=ICE):
    """vertical thermometer: x,y top, 300 tall"""
    rrect(d, x - 22, y, x + 22, y + 260, 22, rgba(PANEL, a), outline=rgba(STEEL, a), w=4)
    circ(d, x, y + 285, 40, rgba(PANEL, a)); ring(d, x, y + 285, 40, rgba(STEEL, a), 4)
    circ(d, x, y + 285, 28, rgba(col, a))
    hh = 230 * clamp(frac)
    rrect(d, x - 10, y + 255 - hh, x + 10, y + 270, 10, rgba(col, a))
    label(d, x, y - 70, txt, col, a, size=48)

def flake(d, x, y, r, col, a, rot=0.0):
    for k in range(3):
        ang = rot + k * math.pi / 3
        dx, dy = r * math.cos(ang), r * math.sin(ang)
        line(d, [(x - dx, y - dy), (x + dx, y + dy)], rgba(col, a), max(3, r * 0.14))
        for s in (-1, 1):
            bx, by = x + s * dx * 0.6, y + s * dy * 0.6
            for q in (-0.6, 0.6):
                ang2 = ang + q + (0 if s > 0 else math.pi)
                line(d, [(bx, by), (bx + r * 0.3 * math.cos(ang2), by + r * 0.3 * math.sin(ang2))], rgba(col, a), max(2, r * 0.1))

def hours_bar(d, y, val, maxv, col, name, a, shown=None):
    x0, x1 = 210, 800
    rrect(d, x0, y, x1, y + 70, 16, rgba(PANEL, a), outline=rgba(STEEL, a), w=3)
    w = (x1 - x0 - 12) * clamp(val / maxv)
    if w > 4:
        rrect(d, x0 + 6, y + 6, x0 + 6 + w, y + 64, 12, rgba(col, a))
    label(d, 120, y + 14, name, col, a, size=34)
    s = shown if shown is not None else f"{int(round(val))} H"
    tw = d.textlength(s, font=FL(BLK, 36)) / S
    tx = x0 + 6 + w - tw / 2 - 18 if w > tw + 40 else x0 + 6 + w + tw / 2 + 16
    label(d, tx, y + 14, s, BG if w > tw + 40 else WHITE, a, size=36)

def fuel_gauge(d, cx, cy, r, level, a):
    ring(d, cx, cy, r, rgba(DARK, a), 18)
    d.arc(p(cx - r, cy - r, cx + r, cy + r), 150, 390, fill=rgba(STEEL, a), width=int(18 * S))
    d.arc(p(cx - r, cy - r, cx + r, cy + r), 150, 150 + 240 * clamp(level), fill=rgba(ACC2, a), width=int(18 * S))
    ang = math.radians(150 + 240 * clamp(level))
    line(d, [(cx, cy), (cx + (r - 30) * math.cos(ang), cy + (r - 30) * math.sin(ang))], rgba(WHITE, a), 8)
    circ(d, cx, cy, 14, rgba(WHITE, a))
    label(d, cx - r * 0.72, cy + r * 0.45, "E", MUTED, a, size=34)
    label(d, cx + r * 0.72, cy + r * 0.45, "F", MUTED, a, size=34)
    # pump icon
    rrect(d, cx - 22, cy + 36, cx + 14, cy + 86, 5, rgba(ACC2, a))
    rrect(d, cx - 14, cy + 44, cx + 6, cy + 58, 3, rgba(BG, a))
    line(d, [(cx + 14, cy + 50), (cx + 28, cy + 58), (cx + 28, cy + 80)], rgba(ACC2, a), 5)

def puff(d, x, y, t, a, n=4, col=SMOKE, drift=1.0):
    for i in range(n):
        u = (t * 0.8 + i / n) % 1.0
        circ(d, x - 30 - 140 * u * drift, y - 50 * u, 16 + 34 * u, rgba(col, a * (1 - u) * 0.6))

def warn_tri(d, x, y, s, a):
    poly(d, [(x, y - s), (x + s * 1.1, y + s * 0.8), (x - s * 1.1, y + s * 0.8)], rgba(YEL, a))
    rrect(d, x - s * 0.1, y - s * 0.45, x + s * 0.1, y + s * 0.35, s * 0.08, rgba(BG, a))
    circ(d, x, y + s * 0.57, s * 0.11, rgba(BG, a))

# ---------------- scenes ----------------

def cell(d, x, y, w, h, lvl, col, a):
    """small upright battery cell with fill level"""
    rrect(d, x + w * 0.3, y - h * 0.08, x + w * 0.7, y + 2, 3, rgba(STEEL, a))
    rrect(d, x, y, x + w, y + h, 6, rgba(PANEL, a), outline=rgba(STEEL, a), w=2)
    hh = (h - 8) * clamp(lvl)
    if hh > 2:
        rrect(d, x + 4, y + h - 4 - hh, x + w - 4, y + h - 4, 4, rgba(col, a))

def health_col(v):
    return ACC if v >= 0.9 else (YEL if v >= 0.85 else RED)

def odo(d, x, y, val, a, digits=13, size=46):
    s = f"{int(val):,}".rjust(digits)
    f = FL(BLK, size)
    cw = size * 0.78
    w = cw * len(s)
    rrect(d, x - w / 2 - 20, y - 12, x + w / 2 + 20, y + size * 1.35, 14, rgba(BG, a), outline=rgba(STEEL, a), w=3)
    for i, ch in enumerate(s):
        cx = x - w / 2 + cw * (i + 0.5)
        if ch != " ":
            label(d, cx, y, ch, WHITE if ch != "," else MUTED, a, size=size)

def vis_bh_hook(d, lt, t):
    dur = sdur("bh_hook")
    label(d, 450, -40, "36,000 EV BATTERIES", WHITE, 1, size=74)
    label(d, 450, 60, "5 YEARS LATER", ACC, 1, size=108)
    # grid of cells; scan line reveals health
    cols, rows = 14, 6
    x0, y0, cw, ch, gx, gy = 72, 230, 40, 64, 14, 22
    scan = ease_inout((lt - 1.2) / max(1.0, dur * 0.6))
    for r in range(rows):
        for c in range(cols):
            k = 1.0 if lt < 0.12 else ease_out((lt * 6 - (r * cols + c) * 0.02) + 0.6)
            if k <= 0: continue
            rnd = ((r * 31 + c * 17) % 11) / 10.0
            lv = 0.87 + 0.10 * rnd
            x = x0 + c * (cw + gx); y = y0 + r * (ch + gy)
            revealed = (c + 0.5) / cols < scan
            cell(d, x, y, cw, ch, lv if revealed else 0.25 + 0.1 * math.sin(t * 3 + c + r), health_col(lv) if revealed else RED, k)
    if 0 < scan < 1:
        sx = x0 + scan * cols * (cw + gx)
        line(d, [(sx, y0 - 20), (sx, y0 + rows * (ch + gy))], rgba(ACC, 0.9), 6)
    kq = 1 - ease_out((scan - 0.45) / 0.15)
    if kq > 0:
        chip(d, 450, 760, "DEAD AFTER A FEW YEARS?", RED, kq, size=34, tcol=WHITE)
    kf = ease_out((scan - 0.6) / 0.3)
    if kf > 0:
        chip(d, 450, 760, "FORD'S FLEET DATA · NOV 2026", ACC, kf, size=32)

def vis_bh_fleet(d, lt, t):
    dur = sdur("bh_fleet")
    a = ease_out(lt / 0.3)
    k1 = back_out((lt - 0.0) / 0.45); k2 = back_out((lt - 0.35) / 0.45)
    if k1 > 0: chip(d, 250, -40, "2021 MUSTANG MACH-E", WHITE, clamp(k1), size=30)
    if k2 > 0: chip(d, 680, -40, "≈5 YEARS", ACC2, clamp(k2), size=30, tcol=BG)
    put_car(d, "side_xray", 120, 40, 660, a)
    fo = ease_inout((lt - 0.5) / max(1.0, dur * 0.35))
    label(d, 450, 300, "ALL-ELECTRIC MILES DRIVEN", MUTED, a, size=26, f=SEMI)
    odo(d, 450, 345, 2_000_000_000 * fo, a)
    kb = ease_out((lt - dur * 0.5) / 0.4)
    if kb > 0:
        fb = ease_inout((lt - dur * 0.5) / 1.2)
        lvl = 1.0 - 0.08 * fb
        label(d, 450, 470, "AVERAGE BATTERY HEALTH", WHITE, kb, size=32)
        pack_bar(d, 120, 530, 700, 650, lvl, ACC, kb, seg=10)
        label(d, 410, 548, f"{int(round(lvl * 100))}%", BG, kb, size=70)
        # ghost of the lost 8%
        if fb > 0.05:
            x_a = 130 + (700 - 140) * lvl; x_b = 690
            rrect(d, x_a, 540, x_b, 640, 8, rgba(RED, kb * 0.35))
        label(d, 450, 690, "USABLE CAPACITY · FORD CONNECTED-CAR DATA", MUTED, kb, size=22, f=SEMI)

def vis_bh_miles(d, lt, t):
    dur = sdur("bh_miles")
    a = ease_out(lt / 0.3)
    label(d, 450, -40, "HEALTH VS MILES", WHITE, a, size=66)
    X0, X1, Y0, Y1 = 150, 820, 120, 600   # plot box
    def px(m): return X0 + (X1 - X0) * m / 220000
    def py(h): return Y1 - (Y1 - Y0) * (h - 60) / 40
    line(d, [(X0, Y0), (X0, Y1), (X1, Y1)], rgba(STEEL, a), 4)
    for h in (100, 90, 80, 70):
        line(d, [(X0, py(h)), (X1, py(h))], rgba(DARK, a), 2)
        label(d, X0 - 50, py(h) - 16, f"{h}%", MUTED, a, size=24, f=SEMI)
    for m, s in ((0, "0"), (100000, "100K"), (200000, "200K")):
        label(d, px(m), Y1 + 14, s, MUTED, a, size=24, f=SEMI)
    label(d, (X0 + X1) / 2, Y1 + 50, "MILES", MUTED, a, size=22, f=SEMI)
    # the myth curve (illustrative)
    km = ease_out((lt - 0.2) / 0.6) * (1 - 0.6 * ease_out((lt - dur * 0.6) / 0.5))
    if km > 0:
        pts = [(px(m), py(max(60, 100 - 40 * (m / 120000) ** 1.3))) for m in range(0, 130001, 10000)]
        for i in range(0, len(pts) - 1, 2):
            line(d, [pts[i], pts[i + 1]], rgba(RED, km * 0.8), 6)
        label(d, px(120000) + 40, py(62) - 50, "THE FEAR", RED, km, size=30)
    # real data line
    data = [(0, 100), (55000, 92), (100000, 91), (200000, 88)]
    f = ease_inout((lt - 0.2) / max(1.0, dur * 0.4))
    reach = 200000 * f
    pts = [(px(m), py(h)) for m, h in data if m <= reach]
    nxt = next(((m, h) for m, h in data if m > reach), None)
    if nxt and pts:
        (m0, h0) = [(m, h) for m, h in data if m <= reach][-1]
        u = (reach - m0) / (nxt[0] - m0)
        pts.append((px(reach), py(h0 + (nxt[1] - h0) * u)))
    if len(pts) > 1:
        line(d, pts, rgba(ACC, a), 10)
    for (m, h), lab in zip(data[1:], ("AVG 55K MI · 92%", "2,000+ CARS · 91%+", "30+ CARS · 88%")):
        k = back_out((reach - m + 20000) / 25000)
        if k <= 0: continue
        kk = clamp(k)
        circ(d, px(m), py(h), 16 * kk, rgba(ACC, kk))
        circ(d, px(m), py(h), 7 * kk, rgba(BG, kk))
        lx = min(px(m), 690)
        chip(d, lx, py(h) - 80 if m != 55000 else py(h) + 26, lab, PANEL, kk, size=24, tcol=WHITE)

def vis_bh_range(d, lt, t):
    dur = sdur("bh_range")
    a = ease_out(lt / 0.3)
    label(d, 450, -40, "WHAT 92% MEANS", WHITE, a, size=72)
    # road
    rrect(d, 40, 330, 860, 450, 18, rgba(DARK, a))
    for i in range(10):
        xx = 60 + ((i * 90 - t * 160) % 860)
        if xx < 820: rrect(d, xx, 385, xx + 46, 395, 4, rgba(MUTED, a))
    put_car(d, "side_white", 210 + 4 * math.sin(t * 3), 205, 480, a)
    f = ease_inout((lt - 0.6) / max(1.0, dur * 0.45))
    rows = [("NEW", 305, MUTED), ("NOW", 305 - 25 * f, ACC)]
    for i, (nm, v, col) in enumerate(rows):
        y = 510 + i * 110
        x0, x1 = 210, 800
        rrect(d, x0, y, x1, y + 70, 16, rgba(PANEL, a), outline=rgba(STEEL, a), w=3)
        w = (x1 - x0 - 12) * v / 320
        rrect(d, x0 + 6, y + 6, x0 + 6 + w, y + 64, 12, rgba(col, a))
        label(d, 130, y + 14, nm, col if i else WHITE, a, size=34)
        label(d, x0 + w - 60, y + 14, f"{int(round(v))} MI", BG, a, size=34)
    kd = back_out((lt - dur * 0.6) / 0.45)
    if kd > 0:
        chip(d, 450, 110, "≈ −25 MILES", ACC2, clamp(kd), size=max(1, 52 * clamp(kd)), tcol=BG)
    label(d, 450, 750, "EPA RANGE × HEALTH, ROUGH ESTIMATE (INSIDEEVS)", MUTED, a, size=20, f=SEMI)

def vis_bh_others(d, lt, t):
    dur = sdur("bh_others")
    a = ease_out(lt / 0.3)
    label(d, 450, -40, "INDEPENDENT TESTS", WHITE, a, size=66)
    chip(d, 450, 50, "AVILOO · 500,000 TESTS · ~93,000 MI", PANEL, a, size=26, tcol=WHITE)
    X0, X1 = 330, 820
    def px(h): return X0 + (X1 - X0) * (h - 80) / 20
    # 90-94 band
    kb = ease_out((lt - 0.4) / 0.5)
    rrect(d, px(90), 150, px(94), 640, 10, rgba(ACC, kb * 0.28), outline=rgba(ACC, kb * 0.7), w=3)
    label(d, 520, 660, "MOST EVs: 90–94%", ACC, kb, size=34)
    bars = [("MACH-E", 92.5, ACC), ("MODEL Y", 90.3, WHITE), ("MODEL 3", 88.9, ACC2)]
    for i, (nm, v, col) in enumerate(bars):
        k = ease_out((lt - 0.8 - i * 0.35) / 0.8)
        if k <= 0: continue
        y = 260 + i * 130
        label(d, 160, y + 16, nm, col, clamp(k * 3), size=34)
        w = (px(v) - X0) * k
        rrect(d, X0 - 60, y, X0 + w, y + 76, 14, rgba(col, clamp(k * 3)))
        label(d, X0 + w - 70, y + 16, f"{v * clamp(k) + (1 - clamp(k)) * 80:.1f}", BG, clamp(k * 3), size=34)
    label(d, 450, 730, "BATTERY HEALTH AFTER 150,000 KM (SEPT 2026)", MUTED, a, size=22, f=SEMI)

def vis_bh_catch(d, lt, t):
    dur = sdur("bh_catch")
    a = ease_out(lt / 0.3)
    label(d, 450, -40, "THE CATCH", ACC2, a, size=84)
    ks = ease_out((lt - 0.2) / 0.5)
    stamp(d, 450, 80, "FORD'S OWN DATA", ACC2, 1, ks, size=56)
    items = [("HEAT", "sun"), ("FAST CHARGING", "plug"), ("TO 100% OFTEN", "full")]
    for i, (nm, ic) in enumerate(items):
        k = back_out((lt - 0.5 - i * 0.4) / 0.45)
        if k <= 0: continue
        kk = clamp(k)
        cx = 160 + i * 290; cy = 380
        rrect(d, cx - 125, cy - 130, cx + 125, cy + 170, 26, rgba(PANEL, kk), outline=rgba(RED, kk), w=4)
        if ic == "sun":
            burst(d, cx, cy - 10, 80, YEL, kk, n=12, rot=t * 0.6)
            circ(d, cx, cy - 10, 48, rgba(ACC2, kk))
        elif ic == "plug":
            rrect(d, cx - 45, cy - 60, cx + 45, cy + 30, 16, rgba(STEEL, kk))
            for dx in (-18, 18):
                rrect(d, cx + dx - 7, cy - 95, cx + dx + 7, cy - 60, 4, rgba(CHROME, kk))
            line(d, [(cx, cy + 30), (cx, cy + 70), (cx + 40, cy + 85)], rgba(STEEL, kk), 12)
            bolt(d, cx, cy - 15, 0.45, YEL, kk)
        else:
            rrect(d, cx - 40, cy - 85, cx + 40, cy + 70, 12, rgba(PANEL, kk), outline=rgba(STEEL, kk), w=4)
            rrect(d, cx - 18, cy - 100, cx + 18, cy - 85, 4, rgba(STEEL, kk))
            fl = 0.85 + 0.15 * (math.sin(t * 6) > 0)
            rrect(d, cx - 30, cy + 60 - 135 * fl, cx + 30, cy + 60, 8, rgba(RED, kk))
        label(d, cx, cy + 110, nm, WHITE, kk, size=24 if len(nm) > 8 else 30)
    kn = ease_out((lt - dur * 0.6) / 0.4)
    label(d, 450, 600, "= FASTER WEAR", RED, kn, size=60)
    label(d, 450, 690, "FORD: DAILY CHARGE AT HOME, FAST-CHARGE WHEN NEEDED", MUTED, kn, size=21, f=SEMI)

def vis_bh_outro(d, lt, t):
    dur = sdur("bh_outro")
    if lt < dur * 0.6:
        a = ease_out(lt / 0.3)
        label(d, 450, -30, "5-YEAR-OLD USED EV?", WHITE, a, size=66)
        k1 = back_out((lt - 0.2) / 0.4); k2 = back_out((lt - 0.5) / 0.4)
        if k1 > 0:
            rrect(d, 50, 140, 395, 380, 30, rgba(ACC, clamp(k1)))
            label(d, 222, 180, "YES", BG, clamp(k1), size=max(1, 100 * k1))
            label(d, 222, 310, "92% IS PLENTY", BG, clamp(k1), size=max(1, 28 * k1))
        label(d, 450, 240, "OR", WHITE, a, size=40)
        if k2 > 0:
            rrect(d, 505, 140, 850, 380, 30, rgba(ACC2, clamp(k2)))
            label(d, 678, 180, "NO", BG, clamp(k2), size=max(1, 100 * k2))
            label(d, 678, 310, "TOO RISKY", BG, clamp(k2), size=max(1, 28 * k2))
        label(d, 450, 470, "TELL ME BELOW", WHITE, ease_out((lt - 0.8) / 0.4), size=50)
    else:
        k = back_out((lt - dur * 0.6) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.6 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"bh_hook": vis_bh_hook, "bh_fleet": vis_bh_fleet, "bh_miles": vis_bh_miles, "bh_range": vis_bh_range,
            "bh_others": vis_bh_others, "bh_catch": vis_bh_catch, "bh_outro": vis_bh_outro})
