# Episode visuals: China zero-mileage "used" cars (controversy).

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
def odometer(d, x, y, digits, a, col=ACC, w=420):
    rrect(d, x - w / 2 + 8, y + 10, x + w / 2 + 8, y + 120, 20, rgba((0, 0, 0), a * 0.5))
    rrect(d, x - w / 2, y, x + w / 2, y + 110, 20, rgba(PANEL, a), outline=rgba(STEEL, a), w=5)
    n = len(digits); cw = (w - 60) / n
    for i, ch in enumerate(digits):
        cx = x - w / 2 + 30 + cw * i
        rrect(d, cx + 4, y + 14, cx + cw - 4, y + 96, 8, rgba(BG, a))
        label(d, cx + cw / 2, y + 18, ch, col, a, size=64)

def stamp(d, x, y, s, col, a, k, size=80, rot=0):
    if k <= 0: return
    sc = 1 + 1.2 * (1 - clamp(k))
    f = FL(BLK, max(1, int(size * sc)))
    tw = d.textlength(s, font=f) / S
    rrect(d, x - tw / 2 - 30, y - 10 * sc, x + tw / 2 + 30, y + size * sc * 1.25, 14, None, outline=rgba(col, a * clamp(k)), w=10)
    text_c(d, x, y, s, f, rgba(col, a * clamp(k)))

def plate(d, x, y, a, cut=0.0):
    rrect(d, x - 120, y, x + 120, y + 64, 10, rgba((40, 110, 220), a), outline=rgba(WHITE, a), w=4)
    label(d, x, y + 10, "A·0000", WHITE, a, size=34)
    if cut > 0:
        xmark(d, x, y + 32, 46 * clamp(cut), RED, a, w=14)

def doc(d, x0, y0, w, h, a, title):
    rrect(d, x0 + 8, y0 + 10, x0 + w + 8, y0 + h + 10, 16, rgba((0, 0, 0), a * 0.5))
    rrect(d, x0, y0, x0 + w, y0 + h, 16, rgba(WHITE, a))
    label(d, x0 + w / 2, y0 + 18, title, DARK, a, size=26)
    for i in range(3):
        rrect(d, x0 + 30, y0 + 70 + i * 34, x0 + w - 30 - i * 40, y0 + 84 + i * 34, 6, rgba(CHROME, a))

def vis_zu_hook(d, lt, t):
    # cover frame: full-strength hook from frame 0
    label(d, 450, -20, "0 MILES.", ACC, 1, size=150)
    label(d, 450, 160, "SOLD AS \"USED\"", WHITE, 1, size=72)
    bob = 4 * math.sin(t * 3)
    put_car(d, "cn_side_teal", 110, 290 + bob, 680)
    odometer(d, 450, 610, "000000", 1, w=470)
    label(d, 450, 735, "ODOMETER · KM", MUTED, 1, size=24, f=SEMI)
    k = (lt - 1.6) / 0.35
    stamp(d, 450, 340, "USED", RED, 1, ease_out(k), size=110)
    label(d, 450, 800, "NO OWNER · NEVER DRIVEN", MUTED, ease_out((lt - 2.6) / 0.4), size=30, f=SEMI)

def vis_zu_trick(d, lt, t):
    dur = sdur("zu_trick")
    a = ease_out(lt / 0.3)
    chip(d, 450, -10, "THE PAPER TRICK", WHITE, a, size=30)
    steps = [(0.0, "NEW CAR", ACC), (dur * 0.25, "REGISTERED", ACC2), (dur * 0.5, "PLATES CANCELLED", RED), (dur * 0.72, "\"USED\" CAR", WHITE)]
    for i, (st, name, col) in enumerate(steps):
        k = back_out((lt - st) / 0.45)
        if k <= 0: continue
        y = 90 + i * 175
        kk = clamp(k)
        rrect(d, 70, y, 830, y + 150, 26, rgba(PANEL, kk), outline=rgba(col, kk), w=4)
        circ(d, 135, y + 75, 42, rgba(col, kk))
        label(d, 135, y + 50, str(i + 1), BG, kk, size=44)
        sz = 30 if len(name) > 12 else 42
        label(d, 385, y + 75 - sz * 0.62, name, col, kk, size=sz)
        if i == 0:
            put_car(d, "cn_side_teal", 620, y + 30, 190, kk)
        elif i == 1:
            plate(d, 690, y + 42, kk)
        elif i == 2:
            plate(d, 690, y + 42, kk, cut=ease_out((lt - st - 0.3) / 0.4))
        else:
            label(d, 690, y + 45, "0 km", ACC, kk, size=46)
        if i < 3:
            ka = ease_out((lt - steps[i + 1][0] + 0.2) / 0.3)
            if ka > 0:
                poly(d, [(430, y + 152), (470, y + 152), (450, y + 172)], rgba(MUTED, ka))
    # "SOLD" counter tick on step 2
    ks = back_out((lt - dur * 0.3) / 0.4)
    if ks > 0:
        chip(d, 450, 790, "COUNTS AS A SALE ✓", GREEN, clamp(ks), size=max(1, 34 * ks), tcol=BG)

def vis_zu_why(d, lt, t):
    dur = sdur("zu_why")
    a = ease_out(lt / 0.3)
    label(d, 450, -10, "PRICE WAR", ACC2, a, size=90)
    # car lot filling up: rows of cars appear faster and faster
    n = int(clamp(lt / (dur * 0.5)) ** 0.7 * 15)
    for i in range(15):
        r, c = divmod(i, 5)
        x = 60 + c * 160; y = 140 + r * 95
        rrect(d, x - 6, y + 58, x + 152, y + 66, 3, rgba(STEEL, a * 0.6))
        if i < n:
            put_car(d, "cn_side_teal" if (i % 3) else "side_white", x, y, 146)
    kf = ease_out((lt - 1.2) / 0.4)
    label(d, 450, 445, "TOO MANY CARS", WHITE, kf, size=40)
    # price tag with discount
    kt = ease_out((lt - dur * 0.45) / 0.4)
    if kt > 0:
        x, y = 450, 530 + 20 * (1 - kt)
        poly(d, [(x - 330, y), (x + 290, y), (x + 340, y + 85), (x + 290, y + 170), (x - 330, y + 170)], rgba(ACC2, kt))
        circ(d, x + 280, y + 85, 14, rgba(BG, kt))
        f = ease_out((lt - dur * 0.5) / 1.2)
        lo = int(round(20 * f)); hi = int(round(30 * f))
        label(d, x - 45, y + 22, f"UP TO {lo}–{hi}% OFF", BG, kt, size=62)
        label(d, x - 45, y + 110, "VS. NEW-CAR STICKER", BG, kt, size=28)

def vis_zu_where(d, lt, t):
    dur = sdur("zu_where")
    a = ease_out(lt / 0.3)
    label(d, 330, 0, "USED-CAR EXPORTS · 2024", MUTED, a, size=28, f=SEMI)
    f = ease_out((lt - 0.2) / 1.8)
    label(d, 330, 40, f"{int(436000 * f):,}", ACC, a, size=110)
    # stylised flow map: China node -> 3 destinations
    cx, cy = 690, 570
    dests = [("RUSSIA", 330, 340), ("CENTRAL ASIA", 250, 540), ("MIDDLE EAST", 220, 730)]
    km = ease_out((lt - 1.2) / 0.5)
    for i, (nm, x, y) in enumerate(dests):
        kd = ease_out((lt - 1.4 - i * 0.35) / 0.5)
        if kd <= 0: continue
        mx, my = (cx + x) / 2, min(cy, y) - 60
        pts = [(cx, cy)]
        for j in range(1, 13):
            u = j / 12 * kd
            pts.append(((1 - u) ** 2 * cx + 2 * (1 - u) * u * mx + u * u * x, (1 - u) ** 2 * cy + 2 * (1 - u) * u * my + u * u * y))
        flow(d, pts, t, 1, col=ACC2, n=6, r=8, speed=0.6, w=10, base=DARK)
        if kd > 0.95:
            circ(d, x, y, 22, rgba(ACC2, 1))
            ring(d, x, y, 22 + 14 * ((t * 1.5 + i * 0.3) % 1), rgba(ACC2, 1 - ((t * 1.5 + i * 0.3) % 1)), 4)
            label(d, x, y + 32, nm, WHITE, 1, size=32)
    if km > 0:
        circ(d, cx, cy, 60 * km, rgba(RED, km))
        label(d, cx, cy - 20, "CHINA", WHITE, km, size=30)
    # "most = 0 miles" pie
    kp = ease_out((lt - dur * 0.5) / 0.5)
    if kp > 0:
        px, py, r = 730, 95, 70
        circ(d, px, py, r, rgba(DARK, kp))
        d.pieslice(p(px - r, py - r, px + r, py + r), -90, -90 + 360 * 0.8 * kp, fill=rgba(ACC, kp))
        circ(d, px, py, r * 0.55, rgba(BG, kp))
        label(d, px, py - 15, "MOST", WHITE, kp, size=22)
        label(d, px, py + 82, "0-MILE CARS", ACC, kp, size=28)
        label(d, px, py + 118, "ANALYST ESTIMATE", MUTED, kp, size=20, f=SEMI)

def vis_zu_cost(d, lt, t):
    dur = sdur("zu_cost")
    a = ease_out(lt / 0.3)
    label(d, 450, -10, "WHO PAYS?", RED, a, size=90)
    rows = [(0.2, "BUYER", "WARRANTY CLOCK ALREADY RUNNING"), (dur * 0.33, "DEALERS ABROAD", "UNDERCUT ON PRICE"), (dur * 0.62, "EVERYONE", "SALES LOOK BIGGER")]
    for i, (st, who, what) in enumerate(rows):
        k = back_out((lt - st) / 0.45)
        if k <= 0: continue
        kk = clamp(k)
        y = 140 + i * 215
        rrect(d, 60, y, 840, y + 190, 26, rgba(PANEL, kk), outline=rgba(RED if i != 2 else ACC2, kk), w=4)
        label(d, 520, y + 40, who, WHITE, kk, size=44)
        label(d, 520, y + 110, what, MUTED, kk, size=26, f=SEMI)
        ix, iy = 165, y + 95
        lk = lt - st
        if i == 0:   # clock with hand sweeping
            ring(d, ix, iy, 62, rgba(WHITE, kk), 7)
            ang = -math.pi / 2 + lk * 3
            line(d, [(ix, iy), (ix + 46 * math.cos(ang), iy + 46 * math.sin(ang))], rgba(ACC2, kk), 8)
            circ(d, ix, iy, 8, rgba(WHITE, kk))
        elif i == 1:  # price arrow falling
            dy = 20 * ease_out(lk / 0.8)
            line(d, [(ix - 50, iy - 45), (ix - 10, iy - 5 + dy * 0.3), (ix + 20, iy - 20 + dy * 0.5), (ix + 50, iy + 35 + dy * 0.2)], rgba(RED, kk), 10)
            poly(d, [(ix + 30, iy + 40), (ix + 68, iy + 58), (ix + 64, iy + 18)], rgba(RED, kk))
        else:  # bar with dashed fake part
            h1 = 70; h2 = 60 * ease_out(lk / 0.8)
            rrect(d, ix - 30, iy + 60 - h1, ix + 30, iy + 60, 6, rgba(CHROME, kk))
            for j in range(int(h2 // 14)):
                rrect(d, ix - 30, iy + 60 - h1 - 14 * (j + 1) + 3, ix + 30, iy + 60 - h1 - 14 * j - 3, 3, rgba(ACC2, kk * 0.8))
            label(d, ix + 62, iy - 60, "?", ACC2, kk, size=54)

def vis_zu_fix(d, lt, t):
    dur = sdur("zu_fix")
    a = ease_out(lt / 0.3)
    chip(d, 450, -10, "NEW RULE · SINCE JAN 1, 2026", ACC, a, size=30)
    # 180-day calendar counter
    f = ease_out((lt - 0.2) / 1.6)
    ring(d, 250, 300, 150, rgba(DARK, a), 26)
    d.arc(p(100, 150, 400, 450), -90, -90 + 360 * f, fill=rgba(ACC, a), width=int(26 * S))
    label(d, 250, 240, f"{int(180 * f)}", WHITE, a, size=96)
    label(d, 250, 355, "DAYS", MUTED, a, size=30, f=SEMI)
    # export doc needing maker's stamp
    kd = ease_out((lt - 0.8) / 0.4)
    if kd > 0:
        doc(d, 520, 160 + 20 * (1 - kd), 310, 320, kd, "EXPORT LICENCE")
        ks = (lt - dur * 0.45) / 0.3
        if ks > 0:
            stamp(d, 675, 360, "MAKER OK", GREEN, 1, ease_out(ks), size=44)
    kt = ease_out((lt - dur * 0.35) / 0.4)
    label(d, 450, 520, "UNDER 180 DAYS? NEED THE", WHITE, kt, size=40)
    label(d, 450, 575, "CARMAKER'S SIGN-OFF", ACC, kt, size=52)
    label(d, 450, 690, "CHINA COMMERCE MINISTRY + 3 AGENCIES", MUTED, ease_out((lt - dur * 0.6) / 0.4), size=24, f=SEMI)

def vis_zu_outro(d, lt, t):
    dur = sdur("zu_outro")
    if lt < dur * 0.6:
        a = ease_out(lt / 0.3)
        k1 = back_out(lt / 0.4); k2 = back_out((lt - 0.4) / 0.4)
        if k1 > 0:
            rrect(d, 50, 160, 410, 380, 30, rgba(ACC, clamp(k1)))
            label(d, 230, 205, "SMART", BG, clamp(k1), size=max(1, 62 * k1))
            label(d, 230, 285, "BARGAIN", BG, clamp(k1), size=max(1, 46 * k1))
        label(d, 450, 245, "OR", WHITE, a, size=40)
        if k2 > 0:
            rrect(d, 490, 160, 850, 380, 30, rgba(RED, clamp(k2)))
            label(d, 670, 205, "FAKE", BG, clamp(k2), size=max(1, 62 * k2))
            label(d, 670, 285, "SALES", BG, clamp(k2), size=max(1, 46 * k2))
        label(d, 450, 480, "TELL ME BELOW", WHITE, ease_out((lt - 0.8) / 0.4), size=50)
    else:
        k = back_out((lt - dur * 0.6) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.6 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"zu_hook": vis_zu_hook, "zu_trick": vis_zu_trick, "zu_why": vis_zu_why, "zu_where": vis_zu_where,
            "zu_cost": vis_zu_cost, "zu_fix": vis_zu_fix, "zu_outro": vis_zu_outro})
