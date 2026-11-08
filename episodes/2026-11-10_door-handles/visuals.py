# Episode visuals: China bans hidden (flush, electric) door handles (hidden problem).

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

# ---- door panel close-up (shared by flush / power scenes) ----
PX0, PY0, PX1, PY1 = 70, 150, 830, 620
HX0, HY0, HX1, HY1 = 260, 330, 640, 400  # handle slot

def door_panel(d, a):
    rrect(d, PX0 + 10, PY0 + 16, PX1 + 10, PY1 + 16, 46, rgba((0, 0, 0), a * 0.5))
    rrect(d, PX0, PY0, PX1, PY1, 46, rgba(TEAL2, a))
    rrect(d, PX0, PY0, PX1, PY0 + 200, 46, rgba(TEAL, a))
    rrect(d, PX0, PY0 + 120, PX1, PY1, 46, rgba(TEAL2, a))
    line(d, [(PX0 + 40, PY0 + 70), (PX1 - 40, PY0 + 60)], rgba(WHITE, a * 0.25), 6)  # paint highlight
    line(d, [(PX1 - 120, PY0), (PX1 - 150, PY1)], rgba(BG, a * 0.7), 5)  # door seam

def handle(d, out, a, col=CHROME):
    """out: 0 = flush, 1 = popped out."""
    rrect(d, HX0 - 8, HY0 - 8, HX1 + 8, HY1 + 8, 36, rgba(BG, a * 0.85))
    dy = -28 * out
    # shadow underneath when out
    rrect(d, HX0 + 6, HY0 + 18, HX1 + 6, HY1 + 18, 34, rgba((0, 0, 0), a * 0.45 * out))
    rrect(d, HX0, HY0 + dy, HX1, HY1 + dy, 34, rgba(col, a))
    line(d, [(HX0 + 30, HY0 + 14 + dy), (HX1 - 30, HY0 + 14 + dy)], rgba(WHITE, a * 0.6), 5)

def motor(d, x, y, t, spin, col, a):
    ring(d, x, y, 44, rgba(col, a), 10)
    for k in range(8):
        ang = spin + k * math.pi / 4
        line(d, [(x + math.cos(ang) * 44, y + math.sin(ang) * 44), (x + math.cos(ang) * 60, y + math.sin(ang) * 60)], rgba(col, a), 14)
    circ(d, x, y, 14, rgba(col, a))

def wire(d, pts, t, a, live=True, col=ACC, cut=None):
    line(d, pts, rgba(STEEL, a), 12)
    if not live: return
    # flowing dots along a polyline
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [math.hypot(b[0] - a_[0], b[1] - a_[1]) for a_, b in segs]
    tot = sum(lens)
    for i in range(10):
        u = ((t * 0.7 + i / 10) % 1.0) * tot
        for (a_, b), L_ in zip(segs, lens):
            if u <= L_:
                f = u / L_
                circ(d, a_[0] + (b[0] - a_[0]) * f, a_[1] + (b[1] - a_[1]) * f, 7, rgba(col, a))
                break
            u -= L_

def battery(d, x, y, col, a, level=1.0):
    rrect(d, x - 60, y - 34, x + 60, y + 34, 10, rgba(PANEL, a), outline=rgba(col, a), w=5)
    rrect(d, x + 60, y - 12, x + 72, y + 12, 4, rgba(col, a))
    if level > 0:
        rrect(d, x - 50, y - 24, x - 50 + 100 * level, y + 24, 6, rgba(col, a))

# ---------------- scenes ----------------
def vis_dh_hook(d, lt, t):
    # cover frame: strong text from frame 0
    label(d, 450, 20, "TRAPPED", RED, 1, size=150)
    label(d, 450, 190, "BY YOUR OWN DOOR?", WHITE, 1, size=58)
    x, y, w = 40, 330, 820
    x += 8 * math.sin(t * 1.3)
    put_car(d, "cn_side_teal", x, y, w)
    hx, hy = car_pt(x, y, w, 760, 470)
    pul = 0.5 + 0.5 * math.sin(t * 6)
    ring(d, hx, hy, 70 + 10 * pul, rgba(RED, 1), 10)
    ring(d, hx, hy, 95 + 25 * pul, rgba(RED, 0.35 * (1 - pul)), 6)
    # arrow to the handle
    k = ease_out((lt - 0.3) / 0.5)
    if k > 0:
        line(d, [(hx + 260, hy - 150), (hx + 95, hy - 50)], rgba(RED, k), 16)
        poly(d, [(hx + 80, hy - 40), (hx + 128, hy - 50), (hx + 104, hy - 82)], rgba(RED, k))
    chip(d, 450, 690, "HIDDEN DOOR HANDLES", ACC, 1, size=36)

def vis_dh_flush(d, lt, t):
    dur = sdur("dh_flush")
    a = ease_out(lt / 0.4)
    door_panel(d, a)
    cyc = (lt - 0.6) % 2.6
    out = ease_inout(cyc / 0.5) if cyc < 1.4 else 1 - ease_inout((cyc - 1.4) / 0.5)
    if lt < 0.6: out = 0
    handle(d, out, a)
    # power path: battery -> motor -> handle
    ka = ease_out((lt - 0.4) / 0.4)
    battery(d, 190, 530, ACC, ka)
    wire(d, [(250, 530), (560, 530), (680, 500)], t, ka)
    motor(d, 720, 470, t, t * 6 * (1 if 0 < out < 1 else 0.15), ACC, ka)
    label(d, 190, 575, "POWER", ACC, ka, size=24)
    label(d, 720, 535, "MOTOR", ACC, ka, size=24)
    label(d, 450, 75, "FLUSH = HIDDEN", WHITE, a, size=54)
    tag = "POPS OUT ON POWER" if out > 0.5 else "SITS FLUSH WITH THE DOOR"
    chip(d, 450, 680, tag, ACC, ka, size=34)
    k2 = ease_out((lt - 3.2) / 0.4)
    label(d, 450, 780, "MADE FAMOUS BY TESLA", ACC2, k2, size=40)

def vis_dh_power(d, lt, t):
    dur = sdur("dh_power")
    a = ease_out(lt / 0.3)
    split = 3.6
    door_panel(d, a)
    cut = ease_out((lt - 0.8) / 0.3)
    # crash flash
    if 0.6 < lt < 1.2:
        fl = 1 - abs(lt - 0.8) / 0.4
        rrect(d, PX0, PY0, PX1, PY1, 46, rgba(WHITE, clamp(fl) * 0.5))
    handle(d, 0, a)
    battery(d, 190, 530, RED if cut > 0 else ACC, a, level=1 - cut)
    if cut <= 0:
        wire(d, [(250, 530), (560, 530), (680, 500)], t, a)
    else:
        line(d, [(250, 530), (420, 530)], rgba(STEEL, a), 12)
        line(d, [(470, 540), (560, 530), (680, 500)], rgba(STEEL, a), 12)
        bolt(d, 445, 520, 0.7, RED, cut)
    motor(d, 720, 470, t, 0, RED if cut > 0 else ACC, a)
    label(d, 450, 75, "CRASH CUTS THE POWER", RED, ease_out((lt - 0.8) / 0.3), size=50)
    # hand pulls, handle won't move
    kh = ease_out((lt - 1.4) / 0.4)
    if kh > 0:
        jig = 6 * math.sin(t * 30) if lt > 1.8 else 0
        hand(d, 450 + jig, 410, 1.3, (230, 190, 160), kh)
        xmark(d, 700, 300, 34, RED, ease_out((lt - 2.0) / 0.3), 14)
        label(d, 700, 210, "STUCK", RED, ease_out((lt - 2.0) / 0.3), size=40)
    # fire + the real case
    kf = ease_out((lt - split) / 0.5)
    if kf > 0:
        for i, fx in enumerate((150, 300, 600, 760)):
            flame(d, fx, PY1 + 5, 1.0, t, kf, ph=i * 1.7)
        chip(d, 450, 690, "OCT 2025 · XIAOMI SU7 · CHENGDU", ACC2, kf, size=30)
        label(d, 450, 780, "BYSTANDERS COULDN'T OPEN THE DOORS", WHITE, ease_out((lt - split - 0.6) / 0.4), size=30)

def child_icon(d, x, y, sc, col, a):
    circ(d, x, y, 26 * sc, rgba(col, a))
    rrect(d, x - 30 * sc, y + 30 * sc, x + 30 * sc, y + 100 * sc, 24 * sc, rgba(col, a))

def vis_dh_probe(d, lt, t):
    dur = sdur("dh_probe")
    a = ease_out(lt / 0.3)
    chip(d, 450, 0, "U.S. SAFETY REGULATOR (NHTSA) PROBE", WHITE, a, size=28)
    f = ease_out((lt - 0.3) / 1.8)
    label(d, 450, 80, f"{int(174300 * f):,}", ACC, a, size=150)
    label(d, 450, 255, "2021 TESLA MODEL Y", WHITE, a, size=40)
    # rear window with child inside
    kw = ease_out((lt - 1.6) / 0.4)
    if kw > 0:
        wx0, wy0, wx1, wy1 = 230, 360, 670, 640
        poly(d, [(wx0 + 60, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], rgba((30, 44, 60), kw))
        poly(d, [(wx0 + 80, wy0 + 15), (wx0 + 200, wy0 + 15), (wx0 + 80, wy0 + 200)], rgba(WHITE, kw * 0.08))
        child_icon(d, 470, 470, 1.2, (255, 205, 60), kw)
        line(d, [(wx0 + 60, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1), (wx0 + 60, wy0)], rgba(CHROME, kw), 8)
        label(d, 450, 655, "LOW BATTERY VOLTAGE → OUTSIDE HANDLE DEAD", MUTED, kw, size=24, f=SEMI)
    # cracks: windows broken
    kc = ease_out((lt - 3.8) / 0.5)
    if kc > 0:
        cx, cy = 560, 430
        for k in range(9):
            ang = k * 0.7 + 0.3
            r1 = (60 + 90 * ((k * 0.37) % 1)) * kc
            mx = cx + math.cos(ang) * r1 * 0.5 + 10 * math.sin(k)
            my = cy + math.sin(ang) * r1 * 0.5
            line(d, [(cx, cy), (mx, my), (cx + math.cos(ang) * r1, cy + math.sin(ang) * r1)], rgba(WHITE, kc), 4)
        chip(d, 450, 715, "9 REPORTS · 4 PARENTS BROKE A WINDOW", ACC2, kc, size=30)

def vis_dh_ban(d, lt, t):
    dur = sdur("dh_ban")
    a = ease_out(lt / 0.3)
    chip(d, 450, 0, "CHINA · FIRST COUNTRY TO BAN THEM", RED, a, size=32, tcol=WHITE)
    # calendar slam
    k = back_out((lt - 0.3) / 0.5)
    if k > 0:
        cx, cy, sc = 210, 260, k
        rrect(d, cx - 120 * sc, cy - 120 * sc, cx + 120 * sc, cy + 130 * sc, 24 * sc, rgba(WHITE, clamp(k)))
        rrect(d, cx - 120 * sc, cy - 120 * sc, cx + 120 * sc, cy - 50 * sc, 24 * sc, rgba(RED, clamp(k)))
        rrect(d, cx - 120 * sc, cy - 75 * sc, cx + 120 * sc, cy - 50 * sc, 0, rgba(RED, clamp(k)))
        label(d, cx, cy - 112 * sc, "JAN", WHITE, clamp(k), size=max(1, 44 * sc))
        label(d, cx, cy - 40 * sc, "1", BG, clamp(k), size=max(1, 110 * sc))
        label(d, cx, cy + 82 * sc, "2027", RED, clamp(k), size=max(1, 34 * sc))
    label(d, 600, 170, "NEW MODELS", WHITE, ease_out((lt - 0.7) / 0.3), size=42)
    label(d, 600, 230, "ALREADY APPROVED:", MUTED, ease_out((lt - 1.0) / 0.3), size=28, f=SEMI)
    label(d, 600, 270, "BY JAN 2029", ACC2, ease_out((lt - 1.0) / 0.3), size=40)
    items = ["MECHANICAL RELEASE OUTSIDE", "MECHANICAL RELEASE INSIDE", "WORKS WITH NO POWER", "ROOM FOR A HAND: 6×2×2.5 CM"]
    for i, s in enumerate(items):
        ki = ease_out((lt - 2.2 - i * 0.7) / 0.35)
        if ki <= 0: continue
        y = 440 + i * 95
        xo = 40 * (1 - ki)
        rrect(d, 70 + xo, y, 830 + xo, y + 78, 22, rgba(PANEL, ki))
        circ(d, 120 + xo, y + 39, 26, rgba(ACC, ki))
        check(d, 120 + xo, y + 39, 13, BG, ki, 7)
        label(d, 480 + xo, y + 20, s, WHITE, ki, size=32)

def vis_dh_tip(d, lt, t):
    dur = sdur("dh_tip")
    a = ease_out(lt / 0.3)
    # interior door card
    rrect(d, 80, 120, 820, 640, 50, rgba(PANEL, a), outline=rgba(STEEL, a), w=4)
    rrect(d, 120, 160, 780, 300, 30, rgba(DARK, a))           # upper trim
    rrect(d, 140, 450, 760, 610, 30, rgba((26, 33, 44), a))   # door pocket
    line(d, [(160, 330), (740, 330)], rgba(ACC2, a * 0.6), 4)  # ambient light strip
    # electric button
    rrect(d, 560, 200, 700, 260, 20, rgba(STEEL, a))
    label(d, 630, 212, "OPEN", WHITE, a, size=26)
    label(d, 630, 270, "ELECTRIC BUTTON", MUTED, a, size=20, f=SEMI)
    # hidden manual lever (glows)
    kg = ease_out((lt - 0.8) / 0.4)
    pul = 0.5 + 0.5 * math.sin(t * 7)
    pull = ease_inout(((lt - 1.6) % 1.6) / 0.6) if lt > 1.6 else 0
    pull = pull if ((lt - 1.6) % 1.6) < 0.8 else 1 - ease_inout((((lt - 1.6) % 1.6) - 0.8) / 0.6)
    lx0, ly0 = 220, 370
    rrect(d, lx0 - 20, ly0 - 20, lx0 + 200, ly0 + 70, 26, rgba(ACC, kg * (0.18 + 0.2 * pul)))
    rrect(d, lx0, ly0 + 12 * pull, lx0 + 180, ly0 + 50 + 12 * pull, 20, rgba(ACC, max(a * 0.5, kg)))
    if kg > 0:
        line(d, [(lx0 + 300, ly0 + 130), (lx0 + 205, ly0 + 70)], rgba(ACC, kg), 12)
        poly(d, [(lx0 + 190, ly0 + 60), (lx0 + 238, ly0 + 66), (lx0 + 214, ly0 + 104)], rgba(ACC, kg))
        label(d, 590, 485, "MANUAL RELEASE", ACC, kg, size=40)
        label(d, 590, 540, "PULL · WORKS WITHOUT POWER", WHITE, kg, size=24, f=SEMI)
    chip(d, 450, 700, "CHECK YOUR OWNER'S MANUAL", ACC2, ease_out((lt - 2.0) / 0.4), size=34)

def vis_dh_outro(d, lt, t):
    dur = sdur("dh_outro")
    if lt < dur * 0.58:
        a = ease_out(lt / 0.3)
        k1 = back_out(lt / 0.4); k2 = back_out((lt - 0.5) / 0.4)
        if k1 > 0:
            rrect(d, 70, 160, 395, 360, 30, rgba(ACC, clamp(k1)))
            label(d, 232, 225, "SLEEK", BG, clamp(k1), size=max(1, 64 * k1))
        label(d, 450, 235, "OR", WHITE, a, size=40)
        if k2 > 0:
            rrect(d, 505, 160, 830, 360, 30, rgba(RED, clamp(k2)))
            label(d, 668, 225, "RISKY?", WHITE, clamp(k2), size=max(1, 64 * k2))
        label(d, 450, 480, "SHOULD THE U.S. BAN THEM?", WHITE, ease_out((lt - 1.0) / 0.4), size=44)
        label(d, 450, 570, "TELL ME BELOW", MUTED, ease_out((lt - 1.3) / 0.4), size=32, f=SEMI)
    else:
        k = back_out((lt - dur * 0.58) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.58 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"dh_hook": vis_dh_hook, "dh_flush": vis_dh_flush, "dh_power": vis_dh_power, "dh_probe": vis_dh_probe,
            "dh_ban": vis_dh_ban, "dh_tip": vis_dh_tip, "dh_outro": vis_dh_outro})
