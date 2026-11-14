# Episode visuals: steer-by-wire (unusual engineering): the steering wheel with no shaft.

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
GREEN = (80, 220, 140)

def flow(d, pts, t, a, col=ACC, n=10, r=7, speed=0.7, w=10, base=STEEL, dash=False):
    """cable with signal dots flowing along it"""
    if dash:
        segs0 = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        for (a0, b0) in segs0:
            L_ = math.hypot(b0[0] - a0[0], b0[1] - a0[1]); nd = max(1, int(L_ / 26))
            for k in range(nd):
                if k % 2: continue
                f0, f1 = k / nd, min(1, (k + 1) / nd)
                line(d, [(a0[0] + (b0[0] - a0[0]) * f0, a0[1] + (b0[1] - a0[1]) * f0),
                         (a0[0] + (b0[0] - a0[0]) * f1, a0[1] + (b0[1] - a0[1]) * f1)], rgba(base, a), w)
    else:
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

def rot_pts(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]

def wheel(d, x, y, r, ang, a, col=CHROME, hub=ACC):
    """steering wheel seen from the driver; ang in radians (positive = clockwise)"""
    if a <= 0: return
    circ(d, x + 6, y + 10, r + 4, rgba((0, 0, 0), a * 0.35))
    ring(d, x, y, r, rgba(DARK, a), r * 0.2)
    ring(d, x, y, r, rgba(col, a), r * 0.13)
    ring(d, x, y - 2, r * 1.02, rgba(WHITE, a * 0.25), 3)
    for k in (90, 210, 330):
        aa = math.radians(k) + ang
        line(d, [(x, y), (x + r * 0.9 * math.cos(aa), y + r * 0.9 * math.sin(aa))], rgba(col, a), r * 0.14)
    circ(d, x, y, r * 0.3, rgba(PANEL, a)); ring(d, x, y, r * 0.3, rgba(col, a), 5)
    # top-centre marker shows rotation
    ma = -math.pi / 2 + ang
    circ(d, x + r * math.cos(ma), y + r * math.sin(ma), r * 0.09, rgba(hub, a))

def tire_top(d, x, y, ang, a, w=46, h=110, col=(24, 28, 34)):
    """tire seen from above, rotated by ang (radians, 0 = pointing up)"""
    pts = rot_pts([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], x, y, ang)
    poly(d, [(px + 5, py + 8) for px, py in pts], rgba((0, 0, 0), a * 0.4))
    poly(d, pts, rgba(col, a))
    line(d, pts + [pts[0]], rgba(STEEL, a), 4)
    for k in range(-3, 4):
        tp = rot_pts([(-w / 2 + 6, k * h / 8), (w / 2 - 6, k * h / 8)], x, y, ang)
        line(d, tp, rgba(STEEL, a * 0.6), 3)

def axle(d, cx, y, half, steer, a, rack_col=STEEL, rack_shift=0.0):
    """front axle top view: rack bar + tie rods + two tires"""
    rrect(d, cx - half + 70 + rack_shift, y - 14, cx + half - 70 + rack_shift, y + 14, 14, rgba(rack_col, a))
    for sx in (-1, 1):
        tx = cx + sx * half
        line(d, [(cx + sx * (half - 70) + rack_shift, y), (tx - sx * 30, y + 10)], rgba(CHROME, a), 10)
        tire_top(d, tx, y, steer, a)

def sdelay(lt, t0, dur=0.45):
    return ease_out((lt - t0) / dur)

# ---------------- scenes ----------------
def vis_sw_hook(d, lt, t):
    ang = 0.75 * math.sin(lt * 2.2)
    label(d, 450, -50, "CONNECTED TO", WHITE, 1, size=74)
    label(d, 450, 35, "NOTHING?", ACC, 1, size=104)
    wheel(d, 450, 330, 140, ang, 1)
    # broken shaft gap with X
    line(d, [(450, 480), (450, 530)], rgba(STEEL, 1), 22)
    line(d, [(450, 640), (450, 690)], rgba(STEEL, 1), 22)
    xmark(d, 450, 585, 34, RED, 1, w=14)
    label(d, 590, 560, "NO SHAFT", RED, 1, size=34)
    # wire with signal
    flow(d, [(330, 330), (200, 330), (200, 760), (330, 760)], t, 1, col=ACC, n=12, r=8, speed=0.6, w=6, base=(60, 90, 40), dash=True)
    label(d, 120, 520, "WIRES", ACC, 1, size=30)
    axle(d, 450, 760, 280, ang * 0.45, 1)

def vis_sw_old(d, lt, t):
    dur = sdur("sw_old")
    sw = 0.6 * math.sin(lt * 2.0)
    split = dur * 0.5
    k2 = ease_out((lt - split) / 0.5)
    label(d, 450, -50, "1900s - TODAY" if k2 < 0.5 else "INFINITI Q50 - 2013", WHITE if k2 < 0.5 else ACC2, 1, size=56)
    wheel(d, 230, 230, 120, sw, 1)
    # column: wheel hub -> pinion box
    col_a = 1 - 0.75 * k2
    line(d, [(230, 230), (560, 590)], rgba(CHROME, col_a), 34)
    line(d, [(230, 222), (560, 582)], rgba(WHITE, col_a * 0.3), 6)
    if k2 < 0.5:
        k1 = sdelay(lt, 0.4)
        chip(d, 590, 260, "STEEL SHAFT", CHROME, k1, size=34)
        line(d, [(520, 330), (420, 420)], rgba(CHROME, k1), 5)
    # pinion box
    rrect(d, 520, 560, 610, 640, 16, rgba(DARK, 1), outline=rgba(STEEL, 1), w=4)
    axle(d, 450, 700, 320, sw * 0.4, 1, rack_shift=sw * 20)
    if k2 > 0:
        # electronic path + clutch
        flow(d, [(330, 230), (720, 230), (720, 560), (610, 600)], t, k2, col=ACC, n=10, r=8, speed=0.7, w=6, base=(60, 90, 40), dash=True)
        chip(d, 730, 140, "ELECTRONIC", ACC, k2, size=30)
        # clutch on the column (open: two plates apart)
        gap = 18 + 6 * math.sin(lt * 3)
        cx, cy = 395, 410
        for s_ in (-1, 1):
            plate = rot_pts([(-50, s_ * gap - 8), (50, s_ * gap - 8), (50, s_ * gap + 8), (-50, s_ * gap + 8)], cx, cy, math.radians(-47))
            poly(d, plate, rgba(ACC2, k2))
        chip(d, 250, 470, "BACKUP CLUTCH", ACC2, sdelay(lt, split + 0.6), size=30)

def vis_sw_cyber(d, lt, t):
    dur = sdur("sw_cyber")
    label(d, 450, -50, "CYBERTRUCK", WHITE, 1, size=70)
    label(d, 450, 40, "NO BACKUP SHAFT", RED, sdelay(lt, 0.3), size=44)
    shift = 40 * math.sin(lt * 2.0)
    y = 360
    # rack housing
    rrect(d, 120, y - 30, 780, y + 30, 30, rgba(DARK, 1), outline=rgba(STEEL, 1), w=4)
    rrect(d, 70 + shift, y - 12, 830 + shift, y + 12, 12, rgba(CHROME, 1))
    # two motors
    fault = lt > dur * 0.55
    for i, mx in enumerate((300, 600)):
        k = back_out((lt - 0.5 - i * 0.35) / 0.45)
        if k <= 0: continue
        kk = clamp(k)
        bad = fault and i == 0
        colm = RED if bad else ACC
        rrect(d, mx - 85, y + 50, mx + 85, y + 210, 24, rgba(PANEL, kk), outline=rgba(colm, kk), w=6)
        label(d, mx, y + 80, f"MOTOR {i + 1}", colm, kk, size=34)
        if not bad:
            # spinning rotor
            for q in range(4):
                aa = lt * 6 + q * math.pi / 2
                line(d, [(mx, y + 160), (mx + 34 * math.cos(aa), y + 160 + 34 * math.sin(aa))], rgba(ACC, kk), 8)
            circ(d, mx, y + 160, 12, rgba(ACC, kk))
        else:
            xmark(d, mx, y + 160, 28, RED, kk, w=12)
        # sensor dot
        circ(d, mx, y - 60, 20, rgba(BLUE, kk)); label(d, mx, y - 120, f"SENSOR {i + 1}", BLUE, kk, size=24)
    k3 = back_out((lt - 1.6) / 0.45)
    if k3 > 0:
        circ(d, 450, y - 60, 20, rgba(YEL, clamp(k3)))
        label(d, 450, y - 150, "SENSOR 3", YEL, clamp(k3), size=24)
        chip(d, 450, y + 260, "TIE BREAKER", YEL, clamp(k3), size=32)
    kf = sdelay(lt, dur * 0.55 + 0.3)
    label(d, 450, y + 380, "ONE FAILS, THE OTHER STEERS", WHITE, kf, size=36)
    for sx in (-1, 1):
        tire_top(d, 450 + sx * 400, y, shift / 200, 1, w=40, h=100)

def vis_sw_ratio(d, lt, t):
    label(d, 450, -50, "SOFTWARE SETS THE RATIO", WHITE, 1, size=50)
    sw = 0.9 * (0.5 - 0.5 * math.cos(lt * 2.4))  # 0..0.9 rad wheel turn
    for i, (nm, gain, col, note) in enumerate([("PARKING", 0.7, ACC, "BIG TIRE TURN"), ("HIGHWAY", 0.08, BLUE, "TINY TIRE TURN")]):
        k = back_out((lt - 0.2 - i * 0.5) / 0.5)
        if k <= 0: continue
        kk = clamp(k)
        cx = 230 + i * 440
        rrect(d, cx - 200, 60, cx + 200, 780, 30, rgba(PANEL, kk), outline=rgba(col, kk), w=5)
        label(d, cx, 90, nm, col, kk, size=44)
        wheel(d, cx, 290, 100, sw, kk)
        label(d, cx, 410, f"WHEEL {int(round(math.degrees(sw)))}°", WHITE, kk, size=30)
        tire_top(d, cx - 80, 590, sw * gain, kk, w=44, h=104)
        tire_top(d, cx + 80, 590, sw * gain, kk, w=44, h=104)
        label(d, cx, 680, note, col, kk, size=26)

def vis_sw_nowheel(d, lt, t):
    dur = sdur("sw_nowheel")
    label(d, 450, -50, "NO SHAFT =", WHITE, 1, size=62)
    label(d, 450, 30, "NO WHEEL NEEDED", ACC, sdelay(lt, 0.2), size=60)
    # dashboard
    rrect(d, 90, 280, 810, 360, 30, rgba(DARK, 1), outline=rgba(STEEL, 1), w=4)
    rrect(d, 330, 220, 570, 290, 14, rgba(PANEL, 1), outline=rgba(STEEL, 1), w=3)
    rrect(d, 345, 233, 555, 277, 8, rgba(BLUE, 0.25 + 0.1 * math.sin(t * 3)))
    k = ease_inout((lt - 0.8) / 1.4)
    # seats (from behind)
    for sx in (260, 640):
        rrect(d, sx - 110, 560, sx + 110, 820, 40, rgba(PANEL, 1), outline=rgba(STEEL, 1), w=4)
        rrect(d, sx - 60, 510, sx + 60, 570, 24, rgba(PANEL, 1), outline=rgba(STEEL, 1), w=4)
    if k < 1:
        wheel(d, 260, 440, 95 * (1 - 0.5 * k), 0.3 * math.sin(lt * 2), 1 - k)
        xmark(d, 260, 440, 70, RED, min(k * 3, 1 - k) if k > 0 else 0, w=12)
    kc = sdelay(lt, 1.8)
    chip(d, 450, 135, "CYBERCAB: NO WHEEL, NO PEDALS", ACC, kc, size=30)

def vis_sw_china(d, lt, t):
    dur = sdur("sw_china")
    k0 = back_out(lt / 0.45)
    rrect(d, 300, -60, 600, 200, 28, rgba(PANEL, clamp(k0)), outline=rgba(RED, clamp(k0)), w=5)
    rrect(d, 300, -60, 600, 10, 28, rgba(RED, clamp(k0)))
    label(d, 450, -50, "JULY 1", WHITE, clamp(k0), size=46)
    label(d, 450, 40, "2026", WHITE, clamp(k0), size=90)
    label(d, 450, 225, "CHINA STANDARD GB 17675-2025", MUTED, sdelay(lt, 0.4), size=26, f=SEMI)
    k1 = sdelay(lt, 0.9)
    if k1 > 0:
        rrect(d, 120, 290, 780, 370, 20, rgba(DARK, k1))
        label(d, 450, 305, "MECHANICAL LINK REQUIRED", WHITE, k1, size=36)
        ks = ease_out((lt - 1.4) / 0.4)
        if ks > 0:
            line(d, [(110, 330), (110 + 680 * ks, 330)], rgba(RED, 1), 10)
    items = ["BACKUP POWER", "BACKUP SIGNALS", "SAFE STOP IF IT FAILS"]
    for i, s_ in enumerate(items):
        k = back_out((lt - dur * 0.45 - i * 0.35) / 0.4)
        if k <= 0: continue
        kk = clamp(k); yy = 420 + i * 95
        rrect(d, 170, yy, 730, yy + 78, 20, rgba(PANEL, kk), outline=rgba(GREEN, kk), w=4)
        check(d, 220, yy + 39, 20, GREEN, kk)
        label(d, 480, yy + 18, s_, WHITE, kk, size=34)
    chip(d, 450, 730, "FIRST IN CHINA: NIO ET9", ACC, sdelay(lt, dur * 0.8), size=28)

def vis_sw_outro(d, lt, t):
    dur = sdur("sw_outro")
    if lt < dur * 0.6:
        a = ease_out(lt / 0.3)
        label(d, 450, -40, "WHICH WOULD YOU TRUST?", WHITE, a, size=56)
        k1 = back_out((lt - 0.2) / 0.4); k2 = back_out((lt - 0.5) / 0.4)
        if k1 > 0:
            rrect(d, 50, 140, 395, 420, 30, rgba(ACC, clamp(k1)))
            label(d, 222, 175, "SOFTWARE", BG, clamp(k1), size=max(1, 54 * k1))
            bolt(d, 222, 330, 0.8 * clamp(k1), BG, clamp(k1))
        label(d, 450, 255, "OR", WHITE, a, size=40)
        if k2 > 0:
            rrect(d, 505, 140, 850, 420, 30, rgba(CHROME, clamp(k2)))
            label(d, 678, 175, "STEEL", BG, clamp(k2), size=max(1, 60 * k2))
            line(d, [(620, 380), (740, 260)], rgba(STEEL, clamp(k2)), 26)
        label(d, 450, 500, "TELL ME BELOW", WHITE, ease_out((lt - 0.8) / 0.4), size=50)
    else:
        k = back_out((lt - dur * 0.6) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.6 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"sw_hook": vis_sw_hook, "sw_old": vis_sw_old, "sw_cyber": vis_sw_cyber, "sw_ratio": vis_sw_ratio,
            "sw_nowheel": vis_sw_nowheel, "sw_china": vis_sw_china, "sw_outro": vis_sw_outro})
