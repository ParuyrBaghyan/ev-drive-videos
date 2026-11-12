# Episode visuals: NIO battery swapping vs the West (unusual engineering).

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

def robot_arm(d, x, y, ext, a):
    """lift platform with two bolt guns rising from floor"""
    rrect(d, x - 170, y, x + 170, y + 26, 8, rgba(STEEL, a))
    for dx in (-110, 110):
        rrect(d, x + dx - 14, y - ext, x + dx + 14, y, 6, rgba(CHROME, a))
        rrect(d, x + dx - 26, y - ext - 22, x + dx + 26, y - ext, 6, rgba(ACC2, a))

def batt_slab(d, x0, y0, w, h, level, col, a):
    rrect(d, x0 + 5, y0 + 8, x0 + w + 5, y0 + h + 8, 10, rgba((0, 0, 0), a * 0.5))
    rrect(d, x0, y0, x0 + w, y0 + h, 10, rgba(PANEL, a), outline=rgba(col, a), w=4)
    if level > 0.01:
        rrect(d, x0 + 6, y0 + 6, x0 + 6 + (w - 12) * clamp(level), y0 + h - 6, 6, rgba(col, a * 0.85))
    for k in range(1, 8):
        xx = x0 + w * k / 8
        line(d, [(xx, y0 + 4), (xx, y0 + h - 4)], rgba(BG, a * 0.6), 3)

def vis_sw_hook(d, lt, t):
    dur = sdur("sw_hook")
    label(d, 450, -30, "EMPTY → FULL", WHITE, 1, size=84)
    label(d, 450, 80, "IN ~3 MIN", ACC, 1, size=130)
    bob = 3 * math.sin(t * 3)
    put_car(d, "cn_side_teal", 140, 300 + bob, 620)
    f = ease_inout((lt - 0.6) / max(0.5, dur - 1.2))
    lvl = 0.08 + 0.92 * f
    col = RED if lvl < 0.25 else (ACC2 if lvl < 0.6 else ACC)
    pack_bar(d, 160, 620, 700, 720, lvl, col, 1)
    label(d, 450, 740, f"{int(round(lvl * 100))}%", col, 1, size=56)
    kp = ease_out((lt - 1.0) / 0.4)
    if kp > 0:
        rrect(d, 600, 790, 860, 860, 35, rgba(PANEL, kp), outline=rgba(RED, kp), w=4)
        label(d, 730, 802, "NO PLUG", RED, kp, size=36)

def vis_sw_robot(d, lt, t):
    dur = sdur("sw_robot")
    a = ease_out(lt / 0.3)
    chip(d, 450, -20, "INSIDE A SWAP STATION", WHITE, a, size=30)
    # station frame
    rrect(d, 40, 70, 860, 560, 30, rgba(PANEL, a * 0.6), outline=rgba(STEEL, a), w=4)
    put_car(d, "side_black", 120, 150, 660, a)
    # floor line & pit
    line(d, [(40, 470), (860, 470)], rgba(STEEL, a), 6)
    u = lt / dur
    # phases: 0-.25 bolts out, .25-.45 old drops+slides right, .45-.7 new slides in & up, .7-1 locked
    ext = 60 * ease_out(u / 0.12)
    bx, bw, bh = 250, 400, 46
    by_car = 400
    # old battery
    if u < 0.25:
        ob = (bx, by_car)
    elif u < 0.45:
        k = (u - 0.25) / 0.2
        kk2 = ease_inout(max(0, k - 0.4) / 0.6)
        ob = (bx + 300 * kk2, by_car + 90 * ease_out(k / 0.4), 1 - kk2)
    else:
        ob = None
    if ob:
        batt_slab(d, ob[0], ob[1], bw, bh, 0.1, RED, a * (ob[2] if len(ob) > 2 else 1))
    if u > 0.45:
        k = (u - 0.45) / 0.25
        ki = ease_inout(clamp(k / 0.6))
        nx = bx - 200 * (1 - ki)
        ny = by_car + 90 * (1 - ease_out(clamp((k - 0.6) / 0.4)))
        batt_slab(d, nx, ny, bw, bh, 1.0, ACC, a * ki)
    robot_arm(d, 450, 560, ext if u < 0.25 or u > 0.7 else 20, a)
    # bolt spin icons
    for i, bxx in enumerate((290, 370, 450, 530, 610)):
        if u < 0.25 or u > 0.7:
            ang = t * 12 + i
            circ(d, bxx, by_car - 8, 9, rgba(ACC2, a))
            line(d, [(bxx, by_car - 8), (bxx + 9 * math.cos(ang), by_car - 8 + 9 * math.sin(ang))], rgba(BG, a), 3)
    # step labels
    steps = [(0.0, "UNBOLT"), (0.25, "DROP OUT"), (0.45, "NEW PACK IN"), (0.72, "LOCKED ✓")]
    for i, (st, s) in enumerate(steps):
        k = ease_out((u - st) / 0.06)
        if k <= 0: continue
        col = ACC if (i == 3 or (u >= st and (i == 3 or u < steps[i + 1][0]))) else MUTED
        chip(d, 125 + i * 217, 620, s, col if col == ACC else DARK, k, size=24, tcol=BG if col == ACC else WHITE)
    label(d, 450, 730, "DRIVER STAYS IN THE CAR", MUTED, ease_out((lt - 1.0) / 0.4), size=30, f=SEMI)

def vis_sw_scale(d, lt, t):
    dur = sdur("sw_scale")
    a = ease_out(lt / 0.3)
    label(d, 450, 0, "NIO BATTERY SWAPS", MUTED, a, size=34, f=SEMI)
    f = ease_out((lt - 0.2) / 2.0)
    label(d, 450, 45, f"{int(130_000_000 * f):,}", ACC, a, size=104)
    label(d, 450, 180, "TOTAL · AS OF NOV 3, 2026", MUTED, a, size=24, f=SEMI)
    # per-day: batteries flying out of a station
    kd = ease_out((lt - dur * 0.42) / 0.4)
    if kd > 0:
        rrect(d, 80, 260, 820, 620, 30, rgba(PANEL, kd), outline=rgba(ACC2, kd), w=4)
        label(d, 450, 285, "110,000+", WHITE, kd, size=110)
        label(d, 450, 420, "SWAPS EVERY DAY", ACC2, kd, size=44)
        # conveyor of mini packs
        for i in range(9):
            x = 120 + ((t * 160 + i * 80) % 680)
            batt_slab(d, x, 515, 60, 34, 1.0, ACC, kd)
    kc = ease_out((lt - dur * 0.7) / 0.4)
    label(d, 450, 690, "≈ ONE CAR EVERY 0.8 SECONDS", WHITE, kc, size=36)

def vis_sw_west(d, lt, t):
    dur = sdur("sw_west")
    a = ease_out(lt / 0.3)
    chip(d, 450, -20, "STARTUP: BETTER PLACE", WHITE, a, size=30)
    # money pile grows
    f = ease_out((lt - 0.3) / (dur * 0.45))
    label(d, 450, 70, f"${int(850 * f)}M", ACC2, a, size=130)
    label(d, 450, 225, "RAISED FOR SWAP STATIONS", MUTED, a, size=28, f=SEMI)
    n = int(f * 18)
    for i in range(n):
        r, c = divmod(i, 6)
        coin(d, 210 + c * 96, 520 - r * 70, 40, a)
    # station icon
    rrect(d, 110, 560, 790, 600, 10, rgba(STEEL, a))
    kb = (lt - dur * 0.62) / 0.35
    if kb > 0:
        rrect(d, 120, 350, 780, 520, 24, rgba(BG, 0.85 * ease_out(kb)))
        stamp(d, 450, 380, "BANKRUPT", RED, 1, ease_out(kb), size=96)
        label(d, 450, 650, "MAY 2013", RED, ease_out(kb), size=54)
        label(d, 450, 730, "ONLY ~750 DRIVERS SIGNED UP IN ISRAEL", MUTED, ease_out((lt - dur * 0.75) / 0.4), size=26, f=SEMI)

def vis_sw_tesla(d, lt, t):
    dur = sdur("sw_tesla")
    a = ease_out(lt / 0.3)
    chip(d, 450, -20, "TESLA · 2013 DEMO", WHITE, a, size=30)
    f = ease_out((lt - 0.2) / 1.6)
    timer(d, 230, 230, 140, f, f"{int(90 * f)}s", a)
    label(d, 230, 395, "ONE SWAP", MUTED, a, size=28, f=SEMI)
    put_car(d, "side_red", 430, 150, 420, a)
    # 200 invited owners grid
    kg = ease_out((lt - dur * 0.42) / 0.4)
    if kg > 0:
        label(d, 450, 460, "2015 PILOT: ~200 OWNERS INVITED", WHITE, kg, size=34)
        lit = ease_out((lt - dur * 0.62) / 0.4)
        for i in range(200):
            r, c = divmod(i, 25)
            x = 105 + c * 29; y = 530 + r * 30
            on = i in (37, 88, 121, 164) and lit > 0
            circ(d, x, y, 9, rgba(ACC if on else STEEL, kg if not on else lit))
            if on:
                ring(d, x, y, 9 + 10 * ((t * 1.4) % 1), rgba(ACC, lit * (1 - (t * 1.4) % 1)), 3)
        label(d, 450, 790, "ONLY 4–5 TRIED IT", ACC, lit, size=52)

def vis_sw_catch(d, lt, t):
    dur = sdur("sw_catch")
    a = ease_out(lt / 0.3)
    label(d, 450, -20, "THE CATCH", ACC2, a, size=96)
    rows = [(0.2, "ONE SHARED", "BATTERY DESIGN"), (dur * 0.33, "THOUSANDS", "OF STATIONS")]
    for i, (st, l1, l2) in enumerate(rows):
        k = back_out((lt - st) / 0.45)
        if k <= 0: continue
        kk = clamp(k); y = 140 + i * 230
        rrect(d, 60, y, 840, y + 200, 26, rgba(PANEL, kk), outline=rgba(ACC2, kk), w=4)
        label(d, 540, y + 40, l1, WHITE, kk, size=48)
        label(d, 540, y + 110, l2, MUTED, kk, size=34, f=SEMI)
        if i == 0:
            for j in range(3):
                batt_slab(d, 95, y + 40 + j * 44, 160, 30, 1.0, ACC, kk)
        else:
            for j in range(12):
                r, c = divmod(j, 4)
                house(d, 110 + c * 50, y + 60 + r * 48, 18, ACC2 if (j * 7 + int(t * 4)) % 5 else ACC, kk)
    kn = ease_out((lt - dur * 0.62) / 0.4)
    if kn > 0:
        f = ease_out((lt - dur * 0.62) / 1.2)
        label(d, 450, 630, f"NIO: {int(4236 * f):,} STATIONS", ACC, kn, size=60)
        label(d, 450, 715, "IN CHINA · NOV 2026", MUTED, kn, size=26, f=SEMI)

def vis_sw_outro(d, lt, t):
    dur = sdur("sw_outro")
    if lt < dur * 0.6:
        a = ease_out(lt / 0.3)
        k1 = back_out(lt / 0.4); k2 = back_out((lt - 0.4) / 0.4)
        if k1 > 0:
            rrect(d, 50, 160, 410, 380, 30, rgba(ACC, clamp(k1)))
            label(d, 230, 205, "ROBOT", BG, clamp(k1), size=max(1, 62 * k1))
            label(d, 230, 285, "SWAP", BG, clamp(k1), size=max(1, 46 * k1))
        label(d, 450, 245, "OR", WHITE, a, size=40)
        if k2 > 0:
            rrect(d, 490, 160, 850, 380, 30, rgba(ACC2, clamp(k2)))
            label(d, 670, 205, "WAIT AT", BG, clamp(k2), size=max(1, 52 * k2))
            label(d, 670, 285, "CHARGER", BG, clamp(k2), size=max(1, 46 * k2))
        label(d, 450, 480, "TELL ME BELOW", WHITE, ease_out((lt - 0.8) / 0.4), size=50)
    else:
        k = back_out((lt - dur * 0.6) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.6 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"sw_hook": vis_sw_hook, "sw_robot": vis_sw_robot, "sw_scale": vis_sw_scale, "sw_west": vis_sw_west,
            "sw_tesla": vis_sw_tesla, "sw_catch": vis_sw_catch, "sw_outro": vis_sw_outro})
