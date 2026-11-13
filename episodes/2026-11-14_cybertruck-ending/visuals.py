# Episode visuals: Tesla ends Cybertruck production (news / controversy).

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

def ticket(d, x, y, sc, a, rot=0.0):
    """small reservation ticket"""
    rrect(d, x - 46 * sc, y - 26 * sc, x + 46 * sc, y + 26 * sc, 8 * sc, rgba(ACC, a))
    circ(d, x - 46 * sc, y, 9 * sc, rgba(BG, a)); circ(d, x + 46 * sc, y, 9 * sc, rgba(BG, a))
    label(d, x, y - 15 * sc, "$100", BG, a, size=max(1, 22 * sc))

def factory(d, x, y, w, h, a, col=STEEL):
    """sawtooth-roof factory hall, x,y = bottom-left"""
    n = 4; tw = w / n
    pts = [(x, y), (x, y - h)]
    for i in range(n):
        pts += [(x + tw * i, y - h - 70), (x + tw * (i + 1), y - h)]
    pts += [(x + w, y)]
    poly(d, [(px + 8, py + 10) for px, py in pts], rgba((0, 0, 0), a * 0.45))
    poly(d, pts, rgba(DARK, a))
    line(d, pts + [pts[0]], rgba(col, a), 5)
    rrect(d, x + w - 70, y - h - 150, x + w - 30, y - h - 20, 4, rgba(DARK, a), outline=rgba(col, a), w=4)

def price_tag(d, x, y, s, col, a, size=64, tcol=None):
    f = FL(BLK, max(1, int(size)))
    tw = d.textlength(s, font=f) / S
    x0, x1 = x - tw / 2 - 40, x + tw / 2 + 50
    h = size * 1.6
    rrect(d, x0 + 8, y + 10, x1 + 8, y + h + 10, 16, rgba((0, 0, 0), a * 0.45))
    poly(d, [(x0 - 50, y + h / 2), (x0 + 6, y), (x1, y), (x1, y + h), (x0 + 6, y + h)], rgba(col, a))
    circ(d, x0 - 14, y + h / 2, 12, rgba(BG, a))
    text_c(d, x + 10, y + size * 0.25, s, f, rgba(tcol or BG, a))

def vis_ct_hook(d, lt, t):
    dur = sdur("ct_hook")
    # hook cover text, visible from frame 0
    label(d, 450, -40, "1,000,000+", ACC, 1, size=140)
    label(d, 450, 120, "RESERVATIONS", WHITE, 1, size=64)
    # tickets raining into a pile
    for i in range(16):
        r1 = ((i * 7919) % 1000) / 1000.0; r2 = ((i * 3571) % 1000) / 1000.0
        u = (t * (0.35 + 0.25 * r2) + r1) % 1.0
        ticket(d, 110 + 680 * ((i * 0.618) % 1.0), 230 + 330 * u, 0.8 + 0.4 * r2, (1 - u) * 0.85)
    factory(d, 220, 600, 460, 170, 1)
    for i in range(3):
        rrect(d, 260 + i * 140, 480, 340 + i * 140, 600, 6, rgba(BG, 1), outline=rgba(STEEL, 1), w=3)
    label(d, 450, 615, "GIGA TEXAS", MUTED, 1, size=26, f=SEMI)
    k = ease_out((lt - dur * 0.55) / 0.35)
    if k > 0:
        stamp(d, 450, 440, "PRODUCTION ENDING", RED, 1, k, size=62)
    label(d, 450, 700, "TESLA CYBERTRUCK · NOV 2026", MUTED, ease_out((lt - 0.6) / 0.4), size=28, f=SEMI)

def vis_ct_plan(d, lt, t):
    dur = sdur("ct_plan")
    a = ease_out(lt / 0.3)
    chip(d, 450, -40, "THE PLAN", WHITE, a, size=34)
    # left card: price promise
    k1 = back_out((lt - 0.2) / 0.45)
    if k1 > 0:
        kk = clamp(k1)
        rrect(d, 40, 60, 440, 480, 28, rgba(PANEL, kk), outline=rgba(ACC, kk), w=4)
        label(d, 240, 90, "2019 UNVEIL", MUTED, kk, size=28, f=SEMI)
        label(d, 240, 150, "STARTING", WHITE, kk, size=36)
        label(d, 240, 196, "PRICE", WHITE, kk, size=36)
        price_tag(d, 250, 290, "<$40K", ACC, kk, size=66)
        label(d, 240, 420, "$100 TO RESERVE", MUTED, kk, size=26, f=SEMI)
    # right card: production target counter
    k2 = back_out((lt - dur * 0.42) / 0.45)
    if k2 > 0:
        kk = clamp(k2)
        rrect(d, 460, 60, 860, 480, 28, rgba(PANEL, kk), outline=rgba(ACC2, kk), w=4)
        label(d, 660, 90, "TARGET", MUTED, kk, size=28, f=SEMI)
        factory(d, 520, 330, 280, 110, kk)
        f = ease_out((lt - dur * 0.42) / 1.4)
        label(d, 660, 350, f"{int(250000 * f):,}", ACC2, kk, size=60)
        label(d, 660, 425, "TRUCKS A YEAR", WHITE, kk, size=28)
    kn = ease_out((lt - dur * 0.75) / 0.4)
    label(d, 450, 560, "BIG PROMISE. BIG FACTORY.", WHITE, kn, size=40)

def vis_ct_reality(d, lt, t):
    dur = sdur("ct_reality")
    a = ease_out(lt / 0.3)
    label(d, 450, -40, "REALITY", ACC2, a, size=90)
    label(d, 450, 70, "US CYBERTRUCK SALES", MUTED, a, size=30, f=SEMI)
    base = 640; top = 150; maxv = 250000
    def bh(v): return (base - top) * v / maxv
    # target ghost bar
    rrect(d, 600, top, 800, base, 18, rgba(PANEL, a), outline=rgba(STEEL, a), w=4)
    for yy in range(int(top) + 20, base, 36):
        line(d, [(612, yy), (788, yy)], rgba(STEEL, a * 0.35), 3)
    label(d, 700, top + 30, "250,000", MUTED, a, size=40)
    label(d, 700, top + 80, "TARGET / YR", MUTED, a, size=24, f=SEMI)
    rows = [(120, "2024", 38965, ACC, 0.25), (360, "2025", 20237, RED, dur * 0.45)]
    for x, yr, v, col, t0 in rows:
        f = ease_out((lt - t0) / 0.9)
        if f <= 0: continue
        h = bh(v) * f
        rrect(d, x + 8, base - h + 10, x + 168, base + 10, 14, rgba((0, 0, 0), 0.45))
        rrect(d, x, base - h, x + 160, base, 14, rgba(col, 1))
        label(d, x + 80, base - h - 70, f"{int(v * f):,}", col, 1, size=46)
        label(d, x + 80, base + 20, yr, WHITE, 1, size=40)
    line(d, [(60, base), (840, base)], rgba(STEEL, a), 4)
    kd = back_out((lt - dur * 0.62) / 0.45)
    if kd > 0:
        burst(d, 430, 300, 110 * clamp(kd), RED, clamp(kd), n=12, rot=t * 0.3)
        label(d, 430, 270, "−48%", WHITE, clamp(kd), size=max(1, 58 * kd))
    label(d, 450, 730, "SOURCE: KELLEY BLUE BOOK (VIA FOX BUSINESS)", MUTED, a * 0.9, size=20, f=SEMI)

def vis_ct_reveal(d, lt, t):
    dur = sdur("ct_reveal")
    a = ease_out(lt / 0.3)
    chip(d, 450, -40, "NOV 6, 2026 · ELON MUSK", WHITE, a, size=32)
    label(d, 450, 50, "GIGA TEXAS", ACC, a, size=64)
    # factory floor plan: lanes switching from truck to robotaxi
    x0, x1, y0, y1 = 70, 830, 150, 470
    rrect(d, x0, y0, x1, y1, 24, rgba(PANEL, a), outline=rgba(STEEL, a), w=5)
    sw = ease_inout((lt - dur * 0.28) / (dur * 0.35))
    n = 5
    for i in range(n):
        yy = y0 + 30 + i * 58
        line(d, [(x0 + 30, yy + 22), (x1 - 30, yy + 22)], rgba(DARK, a), 30)
        # moving units on the line
        for j in range(4):
            u = (t * 0.18 + j / 4 + i * 0.13) % 1.0
            xx = x0 + 50 + (x1 - x0 - 100) * u
            flip = sw > (i + 0.5) / n
            col = ACC if flip else STEEL
            if flip:
                circ(d, xx, yy + 22, 15, rgba(col, a))
            else:
                rrect(d, xx - 30, yy + 10, xx + 30, yy + 34, 5, rgba(col, a))
    lab_k = clamp(sw)
    label(d, 270, 490, "CYBERTRUCK", STEEL, a * (1 - 0.6 * lab_k), size=40)
    label(d, 450, 490, "→", WHITE, a, size=40)
    label(d, 640, 490, "CYBERCAB", ACC, a * (0.3 + 0.7 * lab_k), size=40)
    # timeline
    kt = ease_out((lt - dur * 0.62) / 0.4)
    if kt > 0:
        line(d, [(110, 640), (790, 640)], rgba(STEEL, kt), 8)
        for x, s1, s2, col in [(150, "NOV 2026", "ANNOUNCED", WHITE), (470, "MID-2027", "FIRST PLAN", MUTED), (750, "LATE SUMMER", "2027 · LAST TRUCKS", RED)]:
            circ(d, x, 640, 16, rgba(col, kt))
            label(d, x, 570, s1, col, kt, size=28)
            label(d, x, 668, s2, col, kt, size=22, f=SEMI)
        k3 = ease_out((lt - dur * 0.8) / 0.3)
        if k3 > 0:
            ring(d, 750, 640, 30 + 6 * math.sin(t * 6), rgba(RED, k3), 5)

def vis_ct_price(d, lt, t):
    dur = sdur("ct_price")
    a = ease_out(lt / 0.3)
    label(d, 450, -40, "CHEAPEST YOU CAN ORDER", WHITE, a, size=52)
    label(d, 450, 30, "US CONFIGURATOR (ELECTREK CHECKS)", MUTED, a, size=24, f=SEMI)
    steps = [("2019 PLAN", "<$40K", MUTED, 0.2), ("AUG 2026", "$69,990", ACC2, dur * 0.22), ("NOV 13, 2026", "$109,990", RED, dur * 0.45)]
    for i, (when, val, col, t0) in enumerate(steps):
        k = back_out((lt - t0) / 0.45)
        if k <= 0: continue
        kk = clamp(k); y = 120 + i * 170
        label(d, 200, y + 30, when, col, kk, size=30, f=SEMI)
        price_tag(d, 590, y, val, col, kk, size=56, tcol=BG if col != MUTED else WHITE)
    kb = ease_out((lt - dur * 0.6) / 0.4)
    if kb > 0:
        rrect(d, 140, 640, 760, 730, 45, rgba(PANEL, kb), outline=rgba(RED, kb), w=4)
        label(d, 450, 660, "ONLY TRIM LEFT: CYBERBEAST", WHITE, kb, size=34)

def vis_ct_outro(d, lt, t):
    dur = sdur("ct_outro")
    if lt < dur * 0.68:
        a = ease_out(lt / 0.3)
        rrect(d, 70, -20, 830, 160, 28, rgba(PANEL, a), outline=rgba(STEEL, a), w=4)
        label(d, 450, 10, "MUSK: “BEST VEHICLE", WHITE, a, size=42)
        label(d, 450, 80, "TESLA HAS EVER MADE”", WHITE, a, size=42)
        k1 = back_out((lt - dur * 0.25) / 0.4); k2 = back_out((lt - dur * 0.25 - 0.35) / 0.4)
        if k1 > 0:
            rrect(d, 50, 250, 410, 470, 30, rgba(RED, clamp(k1)))
            label(d, 230, 300, "FAILURE", BG, clamp(k1), size=max(1, 64 * k1))
            label(d, 230, 390, "20K SOLD IN 2025", BG, clamp(k1), size=max(1, 24 * k1))
        label(d, 450, 335, "OR", WHITE, ease_out((lt - dur * 0.3) / 0.3), size=40)
        if k2 > 0:
            rrect(d, 490, 250, 850, 470, 30, rgba(ACC, clamp(k2)))
            label(d, 670, 290, "AHEAD OF", BG, clamp(k2), size=max(1, 48 * k2))
            label(d, 670, 350, "ITS TIME", BG, clamp(k2), size=max(1, 48 * k2))
        label(d, 450, 560, "TELL ME BELOW", WHITE, ease_out((lt - dur * 0.45) / 0.4), size=50)
    else:
        k = back_out((lt - dur * 0.68) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.68 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"ct_hook": vis_ct_hook, "ct_plan": vis_ct_plan, "ct_reality": vis_ct_reality,
            "ct_reveal": vis_ct_reveal, "ct_price": vis_ct_price, "ct_outro": vis_ct_outro})
