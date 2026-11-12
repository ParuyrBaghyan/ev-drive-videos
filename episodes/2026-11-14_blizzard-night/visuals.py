# Episode visuals: stuck in a blizzard all night, EV vs gas car (experiment).

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

def vis_bz_hook(d, lt, t):
    dur = sdur("bz_hook")
    label(d, 450, -40, "STUCK ALL NIGHT", WHITE, 1, size=88)
    label(d, 450, 70, "EV OR GAS?", ACC, 1, size=124)
    # car with snow piling up
    put_car(d, "side_white", 130, 330 + 2 * math.sin(t * 2), 640)
    pile = ease_inout(lt / max(1.0, dur))
    snow_cap(d, 300, 640, 352, 18 + 30 * pile, 1)
    snow_cap(d, 60, 860, 590, 30 + 40 * pile, 1)
    rrect(d, 60, 588, 860, 640, 0, rgba(SNOW, 1))
    # clock
    hrs = 22 + 8 * ease_inout(lt / max(1.0, dur))
    hh = int(hrs) % 24
    ap = "PM" if 12 <= hh < 24 else "AM"
    hd = hh % 12 or 12
    rrect(d, 630, 210, 860, 290, 20, rgba(PANEL, 1), outline=rgba(STEEL, 1), w=3)
    label(d, 745, 226, f"{hd}:00 {ap}", WHITE, 1, size=40)
    thermo(d, 120, 300, 0.12, "9°F", 1)
    snowfall(d, t, 1, n=80)
    label(d, 450, 690, "A REAL TEST, NOT A GUESS", MUTED, ease_out((lt - 1.2) / 0.4), size=30, f=SEMI)

def vis_bz_test(d, lt, t):
    dur = sdur("bz_test")
    a = ease_out(lt / 0.3)
    chip(d, 450, -30, "CAR AND DRIVER TEST · JAN 2022", WHITE, a, size=28)
    for i, (name, sub, img, col) in enumerate([("GAS", "HYUNDAI SONATA", "side_red", ACC2), ("EV", "TESLA MODEL 3", "side_silver" if False else "side_white", ACC)]):
        k = back_out((lt - 0.2 - i * 0.35) / 0.45)
        if k <= 0: continue
        kk = clamp(k); y = 70 + i * 260
        rrect(d, 40, y, 600, y + 230, 26, rgba(PANEL, kk), outline=rgba(col, kk), w=4)
        put_car(d, img, 230, y + 70, 350, kk)
        label(d, 130, y + 50, name, col, kk, size=60)
        label(d, 130, y + 130, sub.split()[0], WHITE, kk, size=24, f=SEMI)
        label(d, 130, y + 160, " ".join(sub.split()[1:]), WHITE, kk, size=24, f=SEMI)
        snow_cap(d, 300, 520, y + 92, 14, kk)
    # outside thermometer dropping
    f = ease_inout((lt - 0.5) / max(1.0, dur - 1.5))
    temp = 26 - 17 * f
    thermo(d, 745, 140, 0.4 - 0.28 * f, f"{int(round(temp))}°F", a)
    label(d, 745, 480, "OUTSIDE", MUTED, a, size=26, f=SEMI)
    kc = ease_out((lt - dur * 0.55) / 0.4)
    if kc > 0:
        rrect(d, 180, 600, 720, 700, 50, rgba(ACC2, kc))
        label(d, 450, 622, "CABIN HEAT: 65°F", BG, kc, size=46)
    snowfall(d, t, a * 0.7, n=40, seed=5)

def vis_bz_gas(d, lt, t):
    dur = sdur("bz_gas")
    a = ease_out(lt / 0.3)
    label(d, 450, -40, "GAS CAR, IDLING", ACC2, a, size=72)
    f = ease_inout((lt - 0.3) / max(1.0, dur * 0.55))
    fuel_gauge(d, 250, 300, 170, 1 - 0.47 * f, a)
    label(d, 250, 500, "JUST UNDER HALF A TANK", MUTED, a, size=22, f=SEMI)
    label(d, 250, 530, "AFTER 24 HOURS", MUTED, a, size=22, f=SEMI)
    rrect(d, 480, 130, 860, 330, 26, rgba(PANEL, a), outline=rgba(ACC2, a), w=4)
    label(d, 670, 150, "≈0.3", ACC2, a, size=96)
    label(d, 670, 270, "GALLON PER HOUR", WHITE, a, size=28)
    label(d, 670, 360, "ENGINE RUNS", WHITE, a, size=34)
    label(d, 670, 410, "JUST FOR HEAT", MUTED, a, size=28, f=SEMI)
    kb = ease_out((lt - dur * 0.55) / 0.4)
    if kb > 0:
        fb = ease_out((lt - dur * 0.55) / 1.2)
        label(d, 450, 590, "FULL TANK =", WHITE, kb, size=34, f=SEMI)
        hours_bar(d, 650, 52 * fb, 55, ACC2, "GAS", kb, shown=f"~{int(round(52 * fb))} HOURS")

def vis_bz_ev(d, lt, t):
    dur = sdur("bz_ev")
    a = ease_out(lt / 0.3)
    label(d, 450, -40, "EV, PARKED", ACC, a, size=72)
    f = ease_inout((lt - 0.3) / max(1.0, dur * 0.5))
    lvl = 1.0 - 0.022 * 10 * f
    pack_bar(d, 80, 120, 520, 240, lvl, ACC, a)
    label(d, 300, 260, f"{int(round(lvl * 100))}%", ACC, a, size=60)
    label(d, 300, 340, f"AFTER {int(round(10 * f))} HOURS", MUTED, a, size=24, f=SEMI)
    rrect(d, 580, 100, 860, 380, 26, rgba(PANEL, a), outline=rgba(ACC, a), w=4)
    label(d, 720, 125, "≈2.2%", ACC, a, size=72)
    label(d, 720, 225, "OF BATTERY", WHITE, a, size=26)
    label(d, 720, 265, "PER HOUR", WHITE, a, size=26)
    label(d, 720, 315, "(HEAT ONLY)", MUTED, a, size=20, f=SEMI)
    label(d, 450, 430, "HEATER RUNS OFF THE BIG BATTERY", MUTED, a, size=28, f=SEMI)
    kb = ease_out((lt - dur * 0.55) / 0.4)
    if kb > 0:
        fb = ease_out((lt - dur * 0.55) / 1.2)
        label(d, 450, 520, "FULL CHARGE =", WHITE, kb, size=34, f=SEMI)
        hours_bar(d, 580, 52, 55, ACC2, "GAS", kb * 0.55, shown="~52 HOURS")
        hours_bar(d, 670, 45 * fb, 55, ACC, "EV", kb, shown=f"~{int(round(45 * fb))} HOURS")

def vis_bz_twist(d, lt, t):
    dur = sdur("bz_twist")
    a = ease_out(lt / 0.3)
    if lt < dur * 0.28:
        k = back_out(lt / 0.45)
        label(d, 450, 60, "ALMOST", WHITE, clamp(k), size=max(1, 80 * k))
        label(d, 450, 160, "A TIE", ACC, clamp(k), size=max(1, 150 * k))
        hours_bar(d, 420, 52, 55, ACC2, "GAS", a, shown="~52 H")
        hours_bar(d, 510, 45, 55, ACC, "EV", a, shown="~45 H")
        return
    u = lt - dur * 0.28
    k1 = ease_out(u / 0.4)
    label(d, 450, -40, "BUT…", ACC2, k1, size=80)
    # gas car, rear (left) end buried in a drift
    rrect(d, 60, 70, 840, 470, 28, rgba(PANEL, k1), outline=rgba(RED, k1), w=4)
    sc = put_car(d, "side_red", 190, 175, 620, k1)
    rrect(d, 64, 352, 836, 466, 24, rgba(SNOW, k1))
    rrect(d, 150, 322, 262, 338, 8, rgba(CHROME, k1))
    grow = ease_out(u / 1.0)
    poly(d, [(70, 356), (90, 356 - 80 * grow), (150, 356 - 105 * grow), (215, 356 - 60 * grow), (240, 356)], rgba(SNOW, k1))
    ka = ease_out((u - 0.5) / 0.4)
    if ka > 0:
        label(d, 160, 380, "TAILPIPE", (60, 70, 85), ka, size=28)
    # CO seeping into the cabin
    kc = ease_out((u - 0.8) / 1.0)
    if kc > 0:
        for i in range(8):
            ph = (t * 0.5 + i / 8) % 1
            cx = 360 + 260 * (i / 8) + 18 * math.sin(t * 2 + i)
            cy = 240 - 30 * ph
            circ(d, cx, cy, 26 + 12 * math.sin(t + i), rgba(SMOKE, kc * 0.6))
        label(d, 500, 212, "CO", WHITE, kc, size=50)
        warn_tri(d, 140, 140, 50, kc)
        label(d, 450, 490, "SNOW-BLOCKED TAILPIPE → CARBON MONOXIDE", RED, kc, size=26)
    ke = back_out((u - dur * 0.42) / 0.45)
    if ke > 0:
        kk = clamp(ke)
        rrect(d, 60, 560, 840, 740, 28, rgba(PANEL, kk), outline=rgba(ACC, kk), w=4)
        put_car(d, "side_white", 90, 600, 300, kk)
        label(d, 615, 585, "EV", ACC, kk, size=56)
        label(d, 615, 660, "NO TAILPIPE", WHITE, kk, size=40)
        check(d, 790, 610, 26, ACC, kk)
        label(d, 450, 760, "GAS CAR? KEEP THE TAILPIPE CLEAR OF SNOW", MUTED, kk, size=22, f=SEMI)

def vis_bz_catch(d, lt, t):
    dur = sdur("bz_catch")
    a = ease_out(lt / 0.3)
    label(d, 450, -40, "THE EV'S CATCH", ACC2, a, size=80)
    rows = [(1.0, ACC, "START FULL", "~45 HOURS OF HEAT"), (0.2, RED, "START AT 20%", "~9 HOURS OF HEAT")]
    for i, (lv, col, l1, l2) in enumerate(rows):
        k = back_out((lt - 0.2 - i * dur * 0.3) / 0.45)
        if k <= 0: continue
        kk = clamp(k); y = 110 + i * 270
        blink = 1.0 if i == 0 else (0.55 + 0.45 * (math.sin(t * 8) > 0))
        rrect(d, 50, y, 850, y + 230, 26, rgba(PANEL, kk), outline=rgba(col, kk), w=4)
        pack_bar(d, 90, y + 60, 380, y + 160, lv, col, kk * blink)
        label(d, 615, y + 50, l1, col, kk, size=48)
        label(d, 615, y + 125, l2, WHITE, kk, size=30, f=SEMI)
    kn = ease_out((lt - dur * 0.7) / 0.4)
    label(d, 450, 690, "AT THE TEST'S ≈2.2% PER HOUR", MUTED, kn, size=26, f=SEMI)
    snowfall(d, t, a * 0.5, n=30, seed=9)

def vis_bz_outro(d, lt, t):
    dur = sdur("bz_outro")
    if lt < dur * 0.6:
        a = ease_out(lt / 0.3)
        k1 = back_out(lt / 0.4); k2 = back_out((lt - 0.4) / 0.4)
        if k1 > 0:
            rrect(d, 50, 160, 410, 380, 30, rgba(ACC, clamp(k1)))
            label(d, 230, 205, "EV", BG, clamp(k1), size=max(1, 90 * k1))
            label(d, 230, 310, "NO TAILPIPE", BG, clamp(k1), size=max(1, 28 * k1))
        label(d, 450, 245, "OR", WHITE, a, size=40)
        if k2 > 0:
            rrect(d, 490, 160, 850, 380, 30, rgba(ACC2, clamp(k2)))
            label(d, 670, 205, "GAS", BG, clamp(k2), size=max(1, 90 * k2))
            label(d, 670, 310, "MORE HOURS", BG, clamp(k2), size=max(1, 28 * k2))
        label(d, 450, 480, "TELL ME BELOW", WHITE, ease_out((lt - 0.8) / 0.4), size=50)
        snowfall(d, t, a * 0.5, n=30, seed=11)
    else:
        k = back_out((lt - dur * 0.6) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.6 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"bz_hook": vis_bz_hook, "bz_test": vis_bz_test, "bz_gas": vis_bz_gas, "bz_ev": vis_bz_ev,
            "bz_twist": vis_bz_twist, "bz_catch": vis_bz_catch, "bz_outro": vis_bz_outro})
