# Episode visuals: sodium-ion (salt) battery with no lithium (impossible tech).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
CHROME = (176, 186, 200)
RED = (255, 84, 84)
TEAL = (30, 110, 112)
TEAL2 = (18, 72, 76)
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
    d._image.alpha_composite(im, (int(x * S), int(y * S)))
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


ICE = (150, 215, 255)
SEA = (40, 120, 200)

def snow(d, t, a, n=26, seed=3, y0=-20, y1=840):
    for i in range(n):
        rx = ((i * 137 + seed * 71) % 900)
        sp = 40 + (i * 53 % 50)
        y = y0 + ((t * sp + i * 97) % (y1 - y0))
        x = rx + 14 * math.sin(t * 1.3 + i)
        r = 5 + (i % 3) * 3
        al = a * (0.35 + 0.25 * (i % 3))
        for k in range(3):
            ang = k * math.pi / 3 + t * 0.6
            line(d, [(x - r * math.cos(ang), y - r * math.sin(ang)), (x + r * math.cos(ang), y + r * math.sin(ang))], rgba(WHITE, al), 2.5)

def tile(d, x, y, num, sym, name, col, a, glow=0.0, w=210, h=240):
    if a <= 0: return
    if glow > 0:
        for g in range(4, 0, -1):
            rrect(d, x - w / 2 - g * 8, y - g * 8, x + w / 2 + g * 8, y + h + g * 8, 30 + g * 8, rgba(col, a * glow * 0.07))
    rrect(d, x - w / 2 + 8, y + 12, x + w / 2 + 8, y + h + 12, 26, rgba((0, 0, 0), a * 0.5))
    rrect(d, x - w / 2, y, x + w / 2, y + h, 26, rgba(PANEL, a), outline=rgba(col, a), w=6)
    label(d, x - w / 2 + 34, y + 14, str(num), col, a, size=32, f=SEMI)
    label(d, x, y + 48, sym, WHITE, a, size=110)
    label(d, x, y + 182, name, col, a, size=30)

def crystal(d, x, y, s, a, col=WHITE):
    poly(d, [(x, y - s), (x + s, y), (x, y + s), (x - s, y)], rgba(col, a))
    poly(d, [(x, y - s), (x + s, y), (x, y)], rgba((255, 255, 255), a * 0.5))

def cell(d, x0, y0, x1, y1, level, col, a):
    """vertical cylindrical-style cell, fills from bottom"""
    rrect(d, x0 + 8, y0 + 12, x1 + 8, y1 + 12, 26, rgba((0, 0, 0), a * 0.5))
    rrect(d, x0, y0, x1, y1, 26, rgba(PANEL, a), outline=rgba(STEEL, a), w=6)
    cx = (x0 + x1) / 2
    rrect(d, cx - 30, y0 - 22, cx + 30, y0 + 4, 8, rgba(STEEL, a))
    hh = (y1 - y0 - 24) * clamp(level)
    if hh > 2:
        rrect(d, x0 + 12, y1 - 12 - hh, x1 - 12, y1 - 12, 18, rgba(col, a))
        rrect(d, x0 + 12, y1 - 12 - hh, x0 + 30, y1 - 12, 8, rgba(WHITE, a * 0.25))

# ---------------- scenes ----------------
def vis_na_hook(d, lt, t):
    # cover frame: full strength from frame 0
    label(d, 450, -20, "NO LITHIUM.", WHITE, 1, size=128)
    label(d, 450, 140, "JUST SALT?", ACC, 1, size=84)
    # element tiles
    tile(d, 240, 280, 3, "Li", "LITHIUM", ACC2, 1)
    kx = ease_out((lt - 0.9) / 0.4)
    if kx > 0:
        r = 95 * kx
        line(d, [(240 - r, 400 - r), (240 + r, 400 + r)], rgba(RED, 1), 18)
        line(d, [(240 - r, 400 + r), (240 + r, 400 - r)], rgba(RED, 1), 18)
    pul = 0.6 + 0.4 * math.sin(t * 4)
    tile(d, 660, 280, 11, "Na", "SODIUM", ACC, 1, glow=pul)
    # arrow Li -> Na
    ka = ease_out((lt - 1.4) / 0.5)
    if ka > 0:
        x1 = 380 + 120 * ka
        line(d, [(372, 400), (x1, 400)], rgba(WHITE, 1), 10)
        poly(d, [(x1 + 22, 400), (x1 - 4, 382), (x1 - 4, 418)], rgba(WHITE, 1))
    # salt crystals falling into a cell
    cell(d, 360, 600, 540, 800, 0.15 + 0.6 * ease_inout(lt / 6), ACC, 1)
    for i in range(9):
        ph = (lt * 0.7 + i / 9) % 1.0
        x = 380 + (i * 47) % 140
        y = 545 + 170 * ph
        crystal(d, x, y, 9 + (i % 3) * 3, clamp(1.2 - ph * 1.1))
    label(d, 200, 690, "NaCl", MUTED, 1, size=40, f=SEMI)
    label(d, 700, 690, "Na-ION", ACC, 1, size=40)

def vis_na_salt(d, lt, t):
    dur = sdur("na_salt")
    a = ease_out(lt / 0.3)
    chip(d, 450, 8, "HOW COMMON IN EARTH'S CRUST", WHITE, a, size=28)
    # lithium: one square
    label(d, 140, 90, "LITHIUM", ACC2, a, size=34)
    rrect(d, 128, 160, 152, 184, 4, rgba(ACC2, a))
    label(d, 140, 200, "1", ACC2, a, size=40)
    # sodium: 1000 squares (40 x 25)
    label(d, 600, 90, "SODIUM", ACC, a, size=34)
    gx, gy, cs = 330, 150, 13.5
    k = ease_inout((lt - 0.5) / 2.6)
    nfill = int(1000 * k)
    for i in range(1000):
        c, r = i % 40, i // 40
        x = gx + c * cs; y = gy + r * cs
        col = ACC if i < nfill else DARK
        d.rectangle(p(x, y, x + cs - 3, y + cs - 3), fill=rgba(col, a))
    kb = back_out((lt - 3.0) / 0.45)
    if kb > 0:
        rrect(d, 470, 365, 730, 450, 26, rgba(ACC, clamp(kb)))
        label(d, 600, 374, "≈1,000×", BG, clamp(kb), size=max(1, 58 * kb))
    # sea with crystals rising
    ks = ease_out((lt - dur * 0.45) / 0.5)
    if ks > 0:
        for j in range(3):
            pts = [(x, 640 + j * 34 + 12 * math.sin(x / 60 + t * 2.2 + j)) for x in range(40, 861, 20)]
            line(d, pts, rgba(SEA if j else ICE, ks * (1 - j * 0.25)), 10)
        for i in range(7):
            ph = (lt * 0.5 + i / 7) % 1.0
            crystal(d, 120 + i * 110, 640 - 130 * ph, 11, ks * clamp(1.3 - ph * 1.3))
        label(d, 450, 735, "IT CAN COME FROM SEAWATER", WHITE, ks, size=34)
    kc = ease_out((lt - dur * 0.72) / 0.4)
    if kc > 0:
        rrect(d, 250, 790, 650, 860, 30, rgba(PANEL, kc), outline=rgba(ACC, kc), w=4)
        label(d, 430, 802, "CHEAPER CELLS", ACC, kc, size=36)
        dy = 8 * math.sin(t * 5)
        line(d, [(608, 805 + dy), (608, 838 + dy)], rgba(ACC, kc), 8)
        poly(d, [(594, 832 + dy), (622, 832 + dy), (608, 850 + dy)], rgba(ACC, kc))

def vis_na_cold(d, lt, t):
    dur = sdur("na_cold")
    a = ease_out(lt / 0.3)
    snow(d, t, a)
    # thermometer
    tx, top, bot = 210, 110, 690
    rrect(d, tx - 34, top - 6, tx + 34, bot + 10, 34, rgba(PANEL, a), outline=rgba(STEEL, a), w=6)
    circ(d, tx, bot + 50, 66, rgba(PANEL, a)); ring(d, tx, bot + 50, 66, rgba(STEEL, a), 6)
    def ypos(c):  # +20C at top+40, -40C at bot-20
        return top + 40 + (20 - c) / 60 * (bot - 60 - top)
    k = ease_inout((lt - 0.3) / 3.2)
    cnow = 20 - 60 * k
    col = ACC2 if cnow > 0 else ICE
    circ(d, tx, bot + 50, 50, rgba(col, a))
    rrect(d, tx - 18, ypos(cnow), tx + 18, bot + 30, 18, rgba(col, a))
    for c in (20, 0, -20, -40):
        y = ypos(c); f = c * 9 / 5 + 32
        line(d, [(tx - 50, y), (tx - 34, y)], rgba(MUTED, a), 4)
        line(d, [(tx + 34, y), (tx + 50, y)], rgba(MUTED, a), 4)
        label(d, tx - 105, y - 18, f"{c}°C", MUTED, a, size=28, f=SEMI)
        label(d, tx + 112, y - 18, f"{int(f)}°F", MUTED, a, size=28, f=SEMI)
    label(d, tx, 15, f"{int(round(cnow))}°", col, a, size=60)
    # battery on the right
    label(d, 640, 60, "SODIUM-ION", ACC, a, size=40)
    label(d, 640, 112, "CAPACITY KEPT", WHITE, a, size=30, f=SEMI)
    lvl = 1.0 - 0.09 * k
    cell(d, 545, 190, 735, 520, lvl, ACC, a)
    label(d, 640, 540, f"{int(round(lvl * 100))}%" if k < 0.99 else "90%+", ACC, a, size=64)
    # frost on cell
    for i in range(5):
        crystal(d, 560 + i * 42, 200 + 8 * math.sin(t * 2 + i), 7, a * 0.7 * k, ICE)
    kc = back_out((lt - 3.8) / 0.45)
    if kc > 0:
        rrect(d, 390, 650, 880, 740, 30, rgba(ICE, clamp(kc)))
        label(d, 635, 662, "−40°C = −40°F", BG, clamp(kc), size=max(1, 52 * kc))
    label(d, 635, 760, "CATL CLAIM · NAXTRA CELLS", MUTED, ease_out((lt - dur * 0.6) / 0.4), size=24, f=SEMI)

def vis_na_power(d, lt, t):
    dur = sdur("na_power")
    a = ease_out(lt / 0.3)
    snow(d, t, a * 0.7, seed=7)
    label(d, 450, -20, "AT −30°C", ICE, a, size=100)
    label(d, 450, 110, "DISCHARGE POWER", WHITE, a, size=40)
    rows = [(0.4, "LFP", 1.0, CHROME), (0.9, "SODIUM", 2.9, ACC)]
    for i, (st, nm, v, col) in enumerate(rows):
        k = ease_out((lt - st) / 1.2)
        if lt < st: continue
        y = 230 + i * 150
        label(d, 130, y + 20, nm, col, 1, size=36)
        w = 180 * v * k
        rrect(d, 240 + 6, y + 10, 240 + w + 6, y + 100, 22, rgba((0, 0, 0), 0.45))
        rrect(d, 240, y, 240 + w, y + 90, 22, rgba(col, 1))
        rrect(d, 240, y, 240 + w, y + 16, 8, rgba(WHITE, 0.2))
        if w > 80:
            for j in range(int(w // 70)):
                xx = 240 + ((t * (60 if nm == "LFP" else 220) + j * 70) % max(1, w - 40)) + 20
                bolt(d, xx, y + 46, 0.28, BG, 0.75)
    kb = back_out((lt - 2.2) / 0.45)
    if kb > 0:
        circ(d, 796, 198, 82 * kb, rgba((0, 0, 0), clamp(kb) * 0.45))
        circ(d, 790, 190, 82 * kb, rgba(ACC2, clamp(kb)))
        ring(d, 790, 190, max(12, 98 * kb + 6 * math.sin(t * 6)), rgba(ACC2, clamp(kb) * 0.5), 5)
        label(d, 790, 152, "≈3×", BG, clamp(kb), size=max(1, 62 * kb))
    kc = ease_out((lt - 1.2) / 0.5)
    if kc > 0:
        put_car(d, "cn_side_teal", 150, 560 + 20 * (1 - kc), 600, kc)
    label(d, 450, 815, "CATL / CHANGAN CLAIM", MUTED, ease_out((lt - dur * 0.5) / 0.4), size=24, f=SEMI)

def vis_na_catch(d, lt, t):
    dur = sdur("na_catch")
    a = ease_out(lt / 0.3)
    label(d, 450, -20, "THE CATCH", ACC2, a, size=96)
    label(d, 450, 105, "ENERGY PER KILO (CELL, Wh/kg)", WHITE, a, size=30, f=SEMI)
    sc = 430 / 300
    rows = [(0.5, "SODIUM", 175, 175, ACC), (1.0, "LFP", 180, 200, CHROME), (1.5, "BEST LITHIUM", 250, 300, ACC2)]
    for i, (st, nm, lo, hi, col) in enumerate(rows):
        k = ease_out((lt - st) / 1.0)
        if lt < st: continue
        y = 165 + i * 92
        label(d, 150, y + 12, nm, col, 1, size=28 if len(nm) > 8 else 32)
        x0 = 270
        rrect(d, x0, y, x0 + lo * sc * k, y + 62, 18, rgba(col, 1))
        if hi > lo:
            rrect(d, x0 + lo * sc * k - 18, y, x0 + hi * sc * k, y + 62, 18, rgba(col, 0.45))
        txt = f"{int(lo * k)}" if hi == lo else f"{int(lo * k)}–{int(hi * k)}"
        label(d, 808, y + 8, txt, col, 1, size=36)
    # range
    kr = ease_out((lt - dur * 0.45) / 0.5)
    if kr > 0:
        put_car(d, "cn_side_teal", 30, 470, 380, kr)
        kk = ease_out((lt - dur * 0.45 - 0.3) / 1.4)
        x1 = 440 + 380 * kk
        line(d, [(440, 560), (x1, 560)], rgba(ACC, kr), 10)
        poly(d, [(x1 + 26, 560), (x1, 540), (x1, 580)], rgba(ACC, kr))
        label(d, 640, 470, f"~{int(400 * kk)} km", ACC, kr, size=60)
        label(d, 640, 600, "≈ 250 MILES", WHITE, kr * kk, size=34)
    kn = ease_out((lt - dur * 0.7) / 0.4)
    if kn > 0:
        rrect(d, 110, 700, 790, 790, 28, rgba(PANEL, kn), outline=rgba(ACC2, kn), w=4)
        label(d, 450, 712, "CHINA'S CLTC TEST · REAL WORLD LESS", ACC2, kn, size=30)
    label(d, 450, 815, "CHANGAN NEVO A06 · 45 kWh SODIUM PACK", MUTED, ease_out((lt - dur * 0.5) / 0.4), size=22, f=SEMI)

def vis_na_outro(d, lt, t):
    dur = sdur("na_outro")
    if lt < dur * 0.62:
        a = ease_out(lt / 0.3)
        k1 = back_out(lt / 0.4); k2 = back_out((lt - 0.4) / 0.4)
        if k1 > 0:
            rrect(d, 50, 160, 410, 380, 30, rgba(ACC2, clamp(k1)))
            label(d, 230, 205, "MORE", BG, clamp(k1), size=max(1, 60 * k1))
            label(d, 230, 285, "RANGE", BG, clamp(k1), size=max(1, 60 * k1))
        label(d, 450, 245, "OR", WHITE, a, size=40)
        if k2 > 0:
            rrect(d, 490, 160, 850, 380, 30, rgba(ICE, clamp(k2)))
            label(d, 670, 205, "WINTER", BG, clamp(k2), size=max(1, 60 * k2))
            label(d, 670, 285, "PROOF", BG, clamp(k2), size=max(1, 60 * k2))
        label(d, 450, 480, "TELL ME BELOW", WHITE, ease_out((lt - 0.8) / 0.4), size=50)
        snow(d, t, a * 0.5, n=12, seed=9)
    else:
        k = back_out((lt - dur * 0.62) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.62 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"na_hook": vis_na_hook, "na_salt": vis_na_salt, "na_cold": vis_na_cold, "na_power": vis_na_power,
            "na_catch": vis_na_catch, "na_outro": vis_na_outro})
