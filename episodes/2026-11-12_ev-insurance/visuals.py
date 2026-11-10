# Episode visuals: why EVs cost more to insure (hidden problem / money).

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

def money(v):
    return f"${int(round(v)):,}"

# ---------------- scenes ----------------
def vis_in_hook(d, lt, t):
    # cover frame: hook text at full strength from frame 0
    label(d, 450, -10, "+$941", ACC2, 1, size=170)
    label(d, 450, 185, "A YEAR... FOR WHAT?", WHITE, 1, size=56)
    put_car(d, "cn_side_teal", 110, 300, 680)
    # insurance shield pulsing over the car
    pul = 1 + 0.05 * math.sin(t * 5)
    shield(d, 450, 420, 95 * pul, (20, 26, 35), 0.92, outline=ACC2)
    label(d, 450, 365, "$", ACC2, 1, size=100)
    # coins dropping out of a wallet line under the car
    for i in range(6):
        ph = (lt * 0.55 + i / 6) % 1.0
        cx = 170 + i * 112
        cy = 640 + 150 * ease_inout(ph)
        coin(d, cx, cy, 30, clamp(1.4 - ph * 1.4))
    label(d, 450, 815, "NOT THE ELECTRICITY", MUTED, ease_out((lt - 2.5) / 0.4), size=30, f=SEMI)

def vis_in_gap(d, lt, t):
    dur = sdur("in_gap")
    a = ease_out(lt / 0.3)
    chip(d, 450, -10, "FULL COVERAGE · AVERAGE PER YEAR", WHITE, a, size=28)
    base_y = 640
    H = 420
    bars = [(0.4, 270, 3159, "EV", ACC2), (2.6, 630, 2218, "GAS", STEEL)]
    for st, x, val, name, col in bars:
        k = ease_out((lt - st) / 1.4)
        if lt < st: continue
        h = H * (val / 3159) * k
        rrect(d, x - 115 + 10, base_y - h + 12, x + 115 + 10, base_y + 12, 22, rgba((0, 0, 0), 0.45))
        rrect(d, x - 115, base_y - h, x + 115, base_y, 22, rgba(col, 1))
        rrect(d, x - 115, base_y - h, x + 115, base_y - h + 18, 9, rgba(WHITE, 0.22))
        label(d, x, base_y - h - 80, money(val * k), col if col != STEEL else CHROME, 1, size=62)
        label(d, x, base_y + 20, name, WHITE, 1, size=50)
        if name == "EV":
            bolt(d, x, base_y - h / 2, 0.55, BG, k)
        else:
            # simple fuel drop
            circ(d, x, base_y - h / 2 + 12, 30, rgba(BG, k))
            poly(d, [(x - 26, base_y - h / 2), (x, base_y - h / 2 - 52), (x + 26, base_y - h / 2)], rgba(BG, k))
    # bracket + 42%
    kb = back_out((lt - 5.2) / 0.5)
    if kb > 0:
        y_ev = base_y - H
        y_gas = base_y - H * 2218 / 3159
        line(d, [(760, y_ev), (800, y_ev), (800, y_gas), (760, y_gas)], rgba(ACC2, clamp(kb)), 8)
        rrect(d, 560, 120, 890, 230, 30, rgba(ACC2, clamp(kb)))
        label(d, 725, 128, "+42%", BG, clamp(kb), size=max(1, 80 * kb))
    label(d, 450, 730, "SOURCE: INSURIFY QUOTE DATA · JUNE 2026", MUTED, ease_out((lt - dur * 0.6) / 0.4), size=24, f=SEMI)

def vis_in_repair(d, lt, t):
    dur = sdur("in_repair")
    a = ease_out(lt / 0.3)
    # crashed car with impact burst at the front
    put_car(d, "cn_side_teal", 40, 0, 470, a)
    kb = back_out((lt - 0.3) / 0.35)
    if kb > 0:
        burst(d, 470, 120, 70 * kb, RED, clamp(kb), rot=t * 0.8)
        burst(d, 470, 120, 38 * kb, YEL, clamp(kb), rot=-t)
    # repair estimate card
    kc = ease_out((lt - 0.8) / 0.4)
    if kc > 0:
        x0, y0 = 540, 10 + 30 * (1 - kc)
        rrect(d, x0 + 8, y0 + 10, x0 + 340, y0 + 300, 18, rgba((0, 0, 0), kc * 0.5))
        rrect(d, x0, y0, x0 + 332, y0 + 290, 18, rgba(WHITE, kc))
        label(d, x0 + 166, y0 + 18, "REPAIR ESTIMATE", DARK, kc, size=26)
        for i in range(4):
            ki = ease_out((lt - 1.1 - i * 0.25) / 0.3)
            rrect(d, x0 + 30, y0 + 75 + i * 38, x0 + 30 + (200 - i * 30) * ki, y0 + 90 + i * 38, 6, rgba(CHROME, kc))
            rrect(d, x0 + 262, y0 + 75 + i * 38, x0 + 302, y0 + 90 + i * 38, 6, rgba(CHROME, kc * ki))
        kt = ease_out((lt - 2.2) / 0.3)
        label(d, x0 + 166, y0 + 232, "TOTAL: $$$", RED, kt * kc, size=34)
    # comparison rows
    rows = [(2.2, "EV CLAIM", 5684, ACC2), (2.7, "GAS CLAIM", 4955, CHROME)]
    for i, (st, name, val, col) in enumerate(rows):
        k = ease_out((lt - st) / 0.9)
        if lt < st: continue
        y = 380 + i * 92
        label(d, 150, y + 6, name, WHITE, 1, size=30)
        rrect(d, 270, y, 270 + 400 * (val / 5684) * k, y + 60, 16, rgba(col, 1))
        label(d, 770, y + 4, money(val * k), col, 1, size=44)
    kd = back_out((lt - 3.7) / 0.4)
    if kd > 0:
        chip(d, 450, 572, "+$729 PER REPAIR", ACC2, clamp(kd), size=max(1, 36 * kd), tcol=BG)
    # factory-parts share
    ke = ease_out((lt - dur * 0.55) / 0.4)
    if ke > 0:
        label(d, 450, 662, "SHARE OF PARTS $ SPENT ON FACTORY PARTS", MUTED, ke, size=24, f=SEMI)
        for i, (name, v, col) in enumerate([("EV", 0.85, ACC2), ("GAS", 0.61, CHROME)]):
            x0 = 80 + i * 400
            kk = ease_out((lt - dur * 0.55 - 0.2 - i * 0.2) / 0.8)
            rrect(d, x0, 705, x0 + 340, 745, 20, rgba(DARK, ke))
            rrect(d, x0, 705, x0 + 340 * v * kk, 745, 20, rgba(col, ke))
            label(d, x0 + 170, 755, f"{name} {int(v * 100 * kk)}%", col, ke, size=30)
    label(d, 450, 805, "MITCHELL · U.S. REPAIRABLE CLAIMS · Q2 2026", MUTED, ease_out((lt - 2.4) / 0.4), size=22, f=SEMI)

def vis_in_battery(d, lt, t):
    a = ease_out(lt / 0.3)
    put_car(d, "side_xray_hot", 50, 40, 800, a)
    # crack across the pack area
    kc = ease_out((lt - 0.5) / 0.5)
    if kc > 0:
        pts = [(300, 160), (340, 135), (370, 175), (410, 140), (450, 180), (490, 145)]
        n = max(2, int(len(pts) * kc))
        line(d, pts[:n], rgba(RED, 1), 9)
        burst(d, 300, 160, 40 * kc, RED, kc * (0.6 + 0.4 * math.sin(t * 10)), n=8, rot=t)
    kt = ease_out((lt - 0.9) / 0.4)
    if kt > 0:
        # price tag
        x, y = 450, 470 + 20 * (1 - kt)
        poly(d, [(x - 330, y), (x + 290, y), (x + 340, y + 85), (x + 290, y + 170), (x - 330, y + 170)], rgba(ACC2, kt))
        circ(d, x + 280, y + 85, 14, rgba(BG, kt))
        f = ease_out((lt - 1.0) / 1.6)
        lo = int(9 * f); hi = int(21 * f)
        label(d, x - 45, y + 26, f"${lo},000 – ${hi},000", BG, kt, size=60)
        label(d, x - 45, y + 112, "NEW PACK, BEFORE LABOR", BG, kt, size=28)
    label(d, 450, 690, "e.g. CHEVY BOLT ~$9K · SILVERADO EV ~$21K", MUTED, ease_out((lt - 2.4) / 0.4), size=26, f=SEMI)

def vis_in_twist(d, lt, t):
    dur = sdur("in_twist")
    a = ease_out(lt / 0.3)
    label(d, 450, -10, "THE TWIST", ACC, a, size=90)
    # gauge-like bar shrinking from 42% to 18%
    k = ease_inout((lt - 0.9) / 1.6)
    v = 42 - 24 * k
    label(d, 450, 105, "EV INSURANCE GAP", WHITE, a, size=34)
    col = ACC2 if k < 0.5 else ACC
    label(d, 450, 150, f"+{int(round(v))}%", col, a, size=80)
    rrect(d, 90, 265, 810, 315, 25, rgba(DARK, a))
    rrect(d, 90, 265, 90 + 720 * v / 42, 315, 25, rgba(col, a))
    label(d, 450, 325, "ALL CARS" if k < 0.5 else "2024 & NEWER MODELS", MUTED if k < 0.5 else ACC, a, size=30, f=SEMI)
    # states where new EVs were cheaper
    ks = ease_out((lt - dur * 0.45) / 0.4)
    if ks > 0:
        label(d, 450, 400, "NEW EVs CHEAPER TO INSURE IN:", WHITE, ks, size=34)
        states = [("MONTANA", "−4%"), ("WEST VIRGINIA", "−4%"), ("NEBRASKA", "−1%")]
        for i, (nm, pc) in enumerate(states):
            ki = back_out((lt - dur * 0.5 - i * 0.3) / 0.4)
            if ki <= 0: continue
            y = 465 + i * 95
            rrect(d, 130, y, 770, y + 80, 24, rgba(PANEL, clamp(ki)), outline=rgba(GREEN, clamp(ki)), w=4)
            check(d, 185, y + 40, 20, GREEN, clamp(ki), w=9)
            label(d, 420, y + 18, nm, WHITE, clamp(ki), size=38)
            label(d, 690, y + 18, pc, GREEN, clamp(ki), size=40)
    label(d, 450, 765, "INSURIFY · 2024+ MODELS · EV vs GAS", MUTED, ease_out((lt - dur * 0.7) / 0.4), size=22, f=SEMI)

def vis_in_outro(d, lt, t):
    dur = sdur("in_outro")
    if lt < dur * 0.6:
        a = ease_out(lt / 0.3)
        k1 = back_out(lt / 0.4); k2 = back_out((lt - 0.4) / 0.4)
        if k1 > 0:
            rrect(d, 50, 160, 410, 380, 30, rgba(ACC2, clamp(k1)))
            label(d, 230, 205, "DEAL", BG, clamp(k1), size=max(1, 66 * k1))
            label(d, 230, 285, "BREAKER", BG, clamp(k1), size=max(1, 46 * k1))
        label(d, 450, 245, "OR", WHITE, a, size=40)
        if k2 > 0:
            rrect(d, 490, 160, 850, 380, 30, rgba(ACC, clamp(k2)))
            label(d, 670, 205, "FADING", BG, clamp(k2), size=max(1, 62 * k2))
            label(d, 670, 285, "FAST", BG, clamp(k2), size=max(1, 46 * k2))
        label(d, 450, 480, "TELL ME BELOW", WHITE, ease_out((lt - 0.8) / 0.4), size=50)
    else:
        k = back_out((lt - dur * 0.6) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.6 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"in_hook": vis_in_hook, "in_gap": vis_in_gap, "in_repair": vis_in_repair, "in_battery": vis_in_battery,
            "in_twist": vis_in_twist, "in_outro": vis_in_outro})
