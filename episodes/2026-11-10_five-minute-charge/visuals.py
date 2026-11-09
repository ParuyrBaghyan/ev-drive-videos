# Episode visuals: BYD 5-minute flash charging and its catch (impossible tech).

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

# ---------------- scenes ----------------
def vis_fc_hook(d, lt, t):
    # cover frame: big hook text from frame 0
    label(d, 450, 0, "5 MINUTES", ACC, 1, size=150)
    label(d, 450, 175, "TO CHARGE AN EV?", WHITE, 1, size=60)
    x, y, w = 20, 300, 640
    put_car(d, "cn_side_teal", x, y, w)
    # charger at right, cable into car's rear-ish port
    charger(d, 790, 610, 1.0, 1, glow=0.5 + 0.5 * math.sin(t * 6))
    px, py = car_pt(x, y, w, 1250, 420)
    flow(d, [(760, 430), (720, 470), (px + 30, py)], t, 1, col=ACC, n=8, r=8, speed=1.6, w=14)
    circ(d, px + 30, py, 14, rgba(ACC, 1))
    # battery filling fast + timer
    lv = 0.10 + 0.87 * ((lt * 0.35) % 1.0)
    pack_bar(d, 130, 650, 640, 740, lv, ACC, 1)
    label(d, 385, 668, f"{int(lv * 100)}%", BG if lv > 0.55 else WHITE, 1, size=44)
    chip(d, 760, 662, "1,500 kW", ACC2, 1, size=34, tcol=BG)

def vis_fc_claim(d, lt, t):
    a = ease_out(lt / 0.3)
    chip(d, 450, 0, "BYD FLASH CHARGING · 2026", WHITE, a, size=30)
    f = ease_out((lt - 0.2) / 1.6)
    label(d, 450, 80, f"{int(1500 * f):,}", ACC, a, size=170)
    label(d, 450, 280, "KILOWATTS PER CHARGER", WHITE, a, size=40)
    # two timed charge bars
    rows = [(1.9, 0.10, 0.70, "10 → 70%", "~5 MIN", ACC), (3.3, 0.10, 0.97, "10 → 97%", "~9 MIN", ACC2)]
    for i, (st, l0, l1, txt, tm, col) in enumerate(rows):
        k = ease_out((lt - st) / 0.35)
        if k <= 0: continue
        y = 420 + i * 170
        lv = l0 + (l1 - l0) * ease_inout((lt - st - 0.2) / 1.2)
        label(d, 160, y - 50 + 20 * (1 - k), txt, WHITE, k, size=34)
        pack_bar(d, 70, y, 640, y + 80, lv, col, k)
        label(d, 760, y + 10, tm, col, k, size=50)
    label(d, 450, 780, "BYD'S CLAIMS · COMPATIBLE CARS", MUTED, ease_out((lt - 4.5) / 0.4), size=26, f=SEMI)

def vis_fc_how(d, lt, t):
    a = ease_out(lt / 0.3)
    # equation builds: 1,000 V x 1,500 A = 1,500 kW
    parts = [(0.0, 130, "1,000 V", "VOLTS", BLUE), (0.9, 450, "× 1,500 A", "AMPS", ACC2), (1.8, 770, "= 1.5 MW", "POWER", ACC)]
    for st, x, big, small, col in parts:
        k = back_out((lt - st) / 0.4)
        if k <= 0: continue
        label(d, x, 30, big, col, clamp(k), size=max(1, 58 * k))
        label(d, x, 115, small, MUTED, clamp(k), size=28, f=SEMI)
    # thick cable into a cell stack
    kc = ease_out((lt - 2.4) / 0.4)
    if kc > 0:
        flow(d, [(60, 400), (300, 400)], t, kc, col=ACC, n=7, r=13, speed=2.2, w=40, base=DARK)
        label(d, 180, 330, "THICK, COOLED CABLE", WHITE, kc, size=24, f=SEMI)
        # stack of blade cells
        for i in range(9):
            ki = ease_out((lt - 2.6 - i * 0.08) / 0.3)
            x0 = 340 + i * 54
            heat = 0.5 + 0.5 * math.sin(t * 5 + i)
            rrect(d, x0, 250, x0 + 40, 560, 10, rgba(PANEL, ki), outline=rgba(ACC, ki * (0.5 + 0.5 * heat)), w=4)
            fill = clamp(((lt - 2.8) * 0.5 + i * 0.03) % 1.0)
            rrect(d, x0 + 7, 553 - 290 * fill, x0 + 33, 553, 6, rgba(ACC, ki * 0.85))
        label(d, 580, 590, "CELLS BUILT FOR SPEED", ACC, kc, size=34)
    kb = ease_out((lt - 3.8) / 0.4)
    chip(d, 450, 690, "10C: IN THEORY A FULL CHARGE IN 6 MIN", ACC2, kb, size=30)

def vis_fc_catch(d, lt, t):
    a = ease_out(lt / 0.3)
    label(d, 450, 0, "THE CATCH", RED, a, size=90)
    # one plug on the left
    charger(d, 130, 640, 0.9, a, glow=1)
    label(d, 130, 670, "1 PLUG", WHITE, a, size=32)
    label(d, 130, 712, "1,500 kW", ACC, a, size=32)
    label(d, 300, 360, "=", WHITE, ease_out((lt - 0.6) / 0.3), size=80)
    # grid of houses lighting up
    cols, rows_ = 9, 8
    lit_n = int(cols * rows_ * ease_inout((lt - 0.8) / 2.2))
    for r in range(rows_):
        for c in range(cols):
            idx = r * cols + c
            x = 375 + c * 58; y = 180 + r * 62
            on = idx < lit_n
            house(d, x, y, 22, YEL if on else DARK, a)
    k = ease_out((lt - 3.0) / 0.4)
    label(d, 600, 690, "≈ 1,000+ U.S. HOMES", YEL, k, size=44)
    label(d, 600, 750, "AVERAGE HOME ≈ 1.2 kW (EIA)", MUTED, ease_out((lt - 3.4) / 0.4), size=24, f=SEMI)

def vis_fc_buffer(d, lt, t):
    dur = sdur("fc_buffer")
    a = ease_out(lt / 0.3)
    # grid -> trickle -> storage -> blast -> car
    pylon(d, 100, 380, 1.0, MUTED, a)
    label(d, 100, 400, "GRID", MUTED, a, size=28)
    flow(d, [(150, 220), (300, 220)], t, a, col=BLUE, n=4, r=6, speed=0.5, w=8)
    label(d, 225, 160, "SIP", BLUE, a, size=30)
    # storage cabinets
    drain = clamp((lt - dur * 0.55) / (dur * 0.4))
    lvl = 1.0 - 0.85 * drain
    for i in range(2):
        x0 = 320 + i * 130
        ki = ease_out((lt - 0.3 - i * 0.15) / 0.35)
        rrect(d, x0 + 6, 120 + 10, x0 + 110 + 6, 400 + 10, 14, rgba((0, 0, 0), ki * 0.5))
        rrect(d, x0, 120, x0 + 110, 400, 14, rgba(DARK, ki), outline=rgba(STEEL, ki), w=4)
        hh = 250 * lvl
        rrect(d, x0 + 12, 388 - hh, x0 + 98, 388, 8, rgba(ACC if lvl > 0.4 else RED, ki))
    label(d, 445, 420, "STATION BATTERIES", WHITE, a, size=30)
    label(d, 445, 462, "~370 kWh PER CHARGER", MUTED, a, size=24, f=SEMI)
    kb = ease_out((lt - 1.0) / 0.4)
    spd = 2.4 * (1 - drain) + 0.4
    flow(d, [(580, 260), (720, 260), (720, 500)], t, kb, col=ACC if drain < 0.6 else RED, n=8, r=13, speed=spd, w=30, base=DARK)
    label(d, 810, 170, "DUMP", ACC, kb, size=34)
    # car queue sliding in
    for i in range(3):
        ks = ease_out((lt - dur * 0.5 - i * 0.5) / 0.5)
        if ks <= 0 and i > 0: continue
        cx = (560 - i * 240 - 40 * (1 - ks)) if i > 0 else 560
        put_car(d, "cn_side_teal", cx, 520 + (0 if i == 0 else 30), 300 if i == 0 else 220, a if i == 0 else ks)
    kd = ease_out((lt - dur * 0.75) / 0.4)
    chip(d, 450, 760, "A FEW CARS IN A ROW → SLOWER", RED, kd, size=32, tcol=WHITE)

def vis_fc_scale(d, lt, t):
    a = ease_out(lt / 0.3)
    put_car(d, "cn_side_teal", 120, 30, 660, a)
    k1 = back_out((lt - 0.3) / 0.4)
    if k1 > 0:
        rrect(d, 330, 330, 570, 410, 40, rgba(BLUE, clamp(k1)))
        label(d, 450, 344, "1,000 V", BG, clamp(k1), size=max(1, 44 * k1))
    label(d, 450, 425, "CAR MUST SUPPORT IT", MUTED, a, size=26, f=SEMI)
    ks = ease_out((lt - 1.6) / 0.4)
    if ks > 0:
        n = int(10000 * ease_out((lt - 1.6) / 1.4))
        label(d, 450, 480, f"{n:,}", ACC, ks, size=110)
        label(d, 450, 610, "BYD STATIONS IN CHINA · AUG 2026", WHITE, ks, size=30)
        rrect(d, 120, 670, 780, 710, 20, rgba(DARK, ks))
        rrect(d, 120, 670, 120 + 660 * 0.5 * ease_out((lt - 1.8) / 1.2), 710, 20, rgba(ACC, ks))
        label(d, 450, 725, "2026 GOAL: 20,000", MUTED, ks, size=26, f=SEMI)

def vis_fc_outro(d, lt, t):
    dur = sdur("fc_outro")
    if lt < dur * 0.6:
        a = ease_out(lt / 0.3)
        k1 = back_out(lt / 0.4); k2 = back_out((lt - 0.5) / 0.4)
        if k1 > 0:
            rrect(d, 70, 160, 395, 360, 30, rgba(ACC, clamp(k1)))
            label(d, 232, 215, "5 MIN", BG, clamp(k1), size=max(1, 70 * k1))
            label(d, 232, 300, "CHARGE", BG, clamp(k1), size=max(1, 30 * k1))
        label(d, 450, 235, "VS", WHITE, a, size=40)
        if k2 > 0:
            rrect(d, 505, 160, 830, 360, 30, rgba(ACC2, clamp(k2)))
            label(d, 668, 215, "GAS", BG, clamp(k2), size=max(1, 70 * k2))
            label(d, 668, 300, "PUMP", BG, clamp(k2), size=max(1, 30 * k2))
        label(d, 450, 480, "WOULD YOU SWITCH?", WHITE, ease_out((lt - 1.0) / 0.4), size=50)
        label(d, 450, 570, "TELL ME BELOW", MUTED, ease_out((lt - 1.3) / 0.4), size=32, f=SEMI)
    else:
        k = back_out((lt - dur * 0.6) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.6 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"fc_hook": vis_fc_hook, "fc_claim": vis_fc_claim, "fc_how": vis_fc_how, "fc_catch": vis_fc_catch,
            "fc_buffer": vis_fc_buffer, "fc_scale": vis_fc_scale, "fc_outro": vis_fc_outro})
