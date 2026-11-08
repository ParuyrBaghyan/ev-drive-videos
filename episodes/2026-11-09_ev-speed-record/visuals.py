# Episode visuals: Yangwang U9 Xtreme 503.17 km/h record (news / impossible tech).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
CHROME = (176, 186, 200)
RED = (255, 84, 84)
GOLD = (255, 205, 60)
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

# ---- 3D car sprites (photoreal renders in assets/cars) ----
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
    """Paste car so its bbox top-left is at logical (x, y), width w. Returns (scale, bbox)."""
    im, bb = car_img(name, w)
    if a < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * clamp(a))))
    d._image.alpha_composite(im, (int(x * S), int(y * S)))
    return w / (bb[2] - bb[0]), bb

# wheel centres of the side renders (source px, 1600x1000 canvas)
WHEELS = [(410, 562), (1112, 562)]
def wheel_pos(x, y, w, k):
    sc = w / (1355 - 245)
    wx, wy = WHEELS[k]
    return x + (wx - 245) * sc, y + (wy - 367) * sc, 95 * sc

def streaks(d, t, a, y0=120, y1=760, n=14, speed=1.0, col=WHITE):
    for i in range(n):
        yy = y0 + (y1 - y0) * ((i * 0.618) % 1.0)
        ln = 120 + 140 * ((i * 0.37) % 1.0)
        x = 900 - ((t * 1400 * speed + i * 211) % 1300)
        line(d, [(x, yy), (x + ln, yy)], rgba(col, a * 0.35), 4)

def counter_txt(v, dec=0):
    return f"{v:,.{dec}f}"

# ---------------- scenes ----------------
def vis_sr_hook(d, lt, t):
    dur = sdur("sr_hook")
    streaks(d, t, 1.0, speed=1.6)
    # big number visible from frame one (cover)
    v = 503
    label(d, 450, 40, counter_txt(v), ACC, 1, size=230)
    label(d, 450, 300, "KM/H", WHITE, 1, size=64)
    chip(d, 450, 410, "FASTER THAN ANY BUGATTI?", ACC2, 1, size=34)
    x = -820 + 860 * ease_out((lt - 0.0) / 1.2)
    put_car(d, "cn_side_teal", x, 560, 820)
    # wheel motion blur rings
    for k in range(2):
        cx, cy, r = wheel_pos(x, 560, 820, k)
        for j in range(3):
            arc(d, cx, cy, r * 1.05, (t * 900 + j * 120) % 360, (t * 900 + j * 120 + 40) % 360, rgba(ACC, 0.5), 5)

def hbar(d, x, y, w, h, frac, col, a):
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=h / 2 * S, fill=rgba(PANEL, a))
    fw = max(h, w * clamp(frac))
    d.rounded_rectangle(p(x, y, x + fw, y + h), radius=h / 2 * S, fill=rgba(col, a))

def crown(d, x, y, sc, col, a):
    pts = [(-60, 30), (-70, -40), (-30, -5), (0, -55), (30, -5), (70, -40), (60, 30)]
    poly(d, [(x + px * sc, y + py * sc) for px, py in pts], rgba(col, a))
    for px, py in [(-70, -40), (0, -55), (70, -40)]:
        circ(d, x + px * sc, y + py * sc, 10 * sc, rgba(col, a))

def vis_sr_king(d, lt, t):
    dur = sdur("sr_king")
    a = ease_out(lt / 0.4)
    crown(d, 450, 120 - 6 * math.sin(t * 3), 1.3 * back_out(lt / 0.5), GOLD, a)
    label(d, 450, 200, "SPEED KING SINCE 2019", WHITE, a, size=44)
    # piston engine icon: 16 cylinders as a grid
    for i in range(16):
        r, c = divmod(i, 8)
        k = ease_out((lt - 0.4 - i * 0.05) / 0.25)
        cx = 210 + c * 68; cy = 330 + r * 70
        bob = 10 * math.sin(t * 14 + i * 1.3) * k
        d.rounded_rectangle(p(cx - 24, cy - 26 + bob, cx + 24, cy + 26 + bob), radius=8 * S, fill=rgba(ACC2, k))
    label(d, 450, 480, "16-CYLINDER GAS ENGINE", ACC2, ease_out((lt - 1.0) / 0.4), size=34)
    # speed bar
    f = ease_out((lt - 1.6) / 1.6)
    hbar(d, 90, 600, 720, 70, f * 490 / 520, ACC2, ease_out((lt - 1.4) / 0.3))
    label(d, 450, 700, "BUGATTI CHIRON  ·  " + counter_txt(490.48 * f, 2) + " KM/H", WHITE, ease_out((lt - 1.4) / 0.3), size=36)
    label(d, 450, 760, "2019 · GERMANY", MUTED, ease_out((lt - 2.2) / 0.3), size=30, f=SEMI)

def vis_sr_close(d, lt, t):
    dur = sdur("sr_close")
    cx, cy, r = 450, 400, 290
    a0, a1 = 150, 390; vmax = 520
    up = ease_inout(lt / 3.0)
    lift = ease_inout((lt - 3.6) / 1.2)
    v = 496.22 * up * (1 - 0.55 * lift)
    peak = 496.22 * up
    ang = lambda x: a0 + (a1 - a0) * x / vmax
    arc(d, cx, cy, r, a0, a1, rgba(DARK, 1), 30)
    arc(d, cx, cy, r, a0, ang(peak), rgba(ACC2 if lift > 0 else ACC, 0.45), 30)
    arc(d, cx, cy, r, a0, ang(v), rgba(ACC, 1), 30)
    # 500 target tick
    ta = math.radians(ang(500))
    line(d, [(cx + math.cos(ta) * (r - 40), cy + math.sin(ta) * (r - 40)), (cx + math.cos(ta) * (r + 40), cy + math.sin(ta) * (r + 40))], rgba(WHITE, 1), 8)
    label(d, cx + math.cos(ta) * (r + 20) + 40, cy + math.sin(ta) * (r + 20) - 60, "500", WHITE, 1, size=34)
    na = math.radians(ang(v))
    line(d, [(cx, cy), (cx + math.cos(na) * (r - 40), cy + math.sin(na) * (r - 40))], rgba(WHITE, 1), 10)
    circ(d, cx, cy, 20, rgba(WHITE, 1))
    label(d, cx, cy + 50, counter_txt(peak, 2), ACC, 1, size=96)
    label(d, cx, cy + 165, "KM/H PEAK · 2025", MUTED, 1, size=30, f=SEMI)
    chip(d, 450, 760, "LIFTED OFF", RED, ease_out((lt - 3.6) / 0.3), size=40, tcol=WHITE)
    chip(d, 450, 40, "YANGWANG U9 XTREME", ACC, ease_out(lt / 0.4), size=32)

def vis_sr_record(d, lt, t):
    dur = sdur("sr_record")
    a = ease_out(lt / 0.4)
    # perspective highway
    vx, vy = 450, 190
    poly(d, [(vx - 12, vy), (vx + 12, vy), (860, 560), (40, 560)], rgba(PANEL, a))
    for side in (-1, 1):
        line(d, [(vx + side * 12, vy), (450 + side * 410, 560)], rgba(CHROME, a), 4)
    for k in range(7):
        u = ((k / 7) + t * 0.9) % 1.0
        uu = u * u
        y0 = vy + (560 - vy) * uu; y1 = vy + (560 - vy) * min(1, (u + 0.06) ** 2)
        line(d, [(vx, y0), (vx, y1)], rgba(ACC, a), 3 + 10 * uu)
    chip(d, 450, 60, "ABU DHABI · E11 · CLOSED", WHITE, a, size=30)
    label(d, 450, 115, "7 KM STRAIGHT", MUTED, a, size=28, f=SEMI)
    # counter
    f = ease_out((lt - 0.8) / 2.6)
    k = ease_out((lt - 0.8) / 0.3)
    label(d, 450, 600, counter_txt(503.17 * f, 2), ACC, k, size=150)
    label(d, 450, 775, "KM/H  ·  " + counter_txt(312.66 * f, 2) + " MPH", WHITE, k, size=40)
    # FIA badge
    bk = back_out((lt - 4.0) / 0.4)
    if bk > 0:
        circ(d, 775, 250, 75 * bk, rgba(ACC, 1))
        label(d, 775, 207, "FIA", BG, clamp(bk), size=max(1, 50 * bk))
        line(d, [(752, 278), (770, 296), (802, 260)], rgba(BG, clamp(bk)), 9)
        label(d, 775, 340, "RECOGNIZED", ACC, clamp(bk), size=26)
    chip(d, 135, 230, "NOV 1, 2026", ACC2, ease_out((lt - 0.4) / 0.3), size=28)

def vis_sr_motors(d, lt, t):
    dur = sdur("sr_motors")
    a = ease_out(lt / 0.4)
    x, y, w = 60, 70, 780
    put_car(d, "side_xray", x, y, w, a)
    for kk in range(2):
        cx, cy, r = wheel_pos(x, y, w, kk)
        g = ease_out((lt - 0.3 - kk * 0.2) / 0.4)
        for j in range(3):
            ph = (t * 1.5 + j / 3) % 1
            ring(d, cx, cy, r * (0.6 + 0.6 * ph), rgba(ACC, g * (1 - ph)), 6)
        circ(d, cx, cy, r * 0.45, rgba(ACC, g * 0.85))
        rot_a = t * 20
        for s_ in range(3):
            aa = rot_a + s_ * 2.094
            line(d, [(cx, cy), (cx + math.cos(aa) * r * 0.4, cy + math.sin(aa) * r * 0.4)], rgba(BG, g), 5)
    chip(d, 450, 20, "4 MOTORS · 1 PER WHEEL", ACC, ease_out((lt - 0.6) / 0.3), size=32)
    # rpm counter
    f = ease_out((lt - 1.2) / 1.8)
    ka = ease_out((lt - 1.2) / 0.3)
    label(d, 250, 400, counter_txt(30000 * f), WHITE, ka, size=72)
    label(d, 250, 485, "RPM PER MOTOR", MUTED, ka, size=26, f=SEMI)
    # hp compare bars
    kb = ease_out((lt - 3.4) / 0.3)
    fb = ease_out((lt - 3.4) / 1.4)
    label(d, 640, 400, "HORSEPOWER", MUTED, kb, size=26, f=SEMI)
    hbar(d, 500, 445, 300, 40, fb * 1600 / 3100, ACC2, kb)
    label(d, 650, 492, "BUGATTI ~1,600", ACC2, kb, size=24)
    hbar(d, 500, 545, 300, 40, fb * 3000 / 3100, ACC, kb)
    label(d, 650, 592, "U9 XTREME 3,000+", ACC, kb, size=24)
    chip(d, 450, 690, "ALMOST 2×", ACC, back_out((lt - 4.8) / 0.4) if lt > 4.8 else 0, size=44)

def plug_icon(d, x, y, sc, col, a):
    d.rounded_rectangle(p(x - 60 * sc, y - 70 * sc, x + 60 * sc, y + 70 * sc), radius=24 * S * sc, fill=rgba(PANEL, a), outline=rgba(col, a), width=int(5 * S))
    for dx in (-20, 20):
        d.rounded_rectangle(p(x + dx * sc - 6 * sc, y - 30 * sc, x + dx * sc + 6 * sc, y + 5 * sc), radius=3 * S, fill=rgba(col, a))
    circ(d, x, y + 35 * sc, 10 * sc, rgba(col, a))

def flow_line(d, x0, x1, y, wdt, t, col, a, n, speed):
    line(d, [(x0, y), (x1, y)], rgba(STEEL, a), wdt)
    for i in range(n):
        u = (t * speed + i / n) % 1.0
        circ(d, x0 + (x1 - x0) * u, y, wdt * 0.32, rgba(col, a))

def vis_sr_volts(d, lt, t):
    dur = sdur("sr_volts")
    split = dur * 0.62
    if lt < split:
        a = ease_out(lt / 0.4)
        plug_icon(d, 170, 170, 1.0, MUTED, a)
        label(d, 450, 120, "120 V", MUTED, a, size=70)
        label(d, 450, 205, "YOUR WALL OUTLET", MUTED, a, size=26, f=SEMI)
        kb = back_out((lt - 0.8) / 0.5)
        if kb > 0:
            label(d, 450, 290, "1,200 V", ACC, clamp(kb), size=max(1, 120 * kb))
            label(d, 770, 300, "×10", ACC2, clamp(kb), size=56)
        k2 = ease_out((lt - 2.0) / 0.4)
        label(d, 450, 470, "SAME POWER:", WHITE, k2, size=32)
        flow_line(d, 120, 780, 560, 46, t, ACC2, k2, 12, 1.4)
        label(d, 450, 600, "LOW VOLTAGE = HIGH CURRENT, MORE HEAT", ACC2, k2, size=24)
        flow_line(d, 120, 780, 700, 16, t, ACC, k2, 5, 1.4)
        label(d, 450, 730, "HIGH VOLTAGE = LESS CURRENT, LESS HEAT", ACC, k2, size=24)
    else:
        lk = lt - split
        a = ease_out(lk / 0.3)
        label(d, 450, 40, "ONLY", WHITE, a, size=60)
        n = int(30 * ease_out(lk / 1.4))
        for i in range(30):
            r, c = divmod(i, 5)
            cx = 170 + c * 140; cy = 160 + r * 78
            if i < n:
                put_car(d, "cn_side_teal", cx - 62, cy - 20, 124)
            else:
                d.rounded_rectangle(p(cx - 58, cy - 12, cx + 58, cy + 18), radius=8 * S, fill=rgba(PANEL, a))
        label(d, 450, 650, f"{n} BUILT", ACC, a, size=100)

def vis_sr_outro(d, lt, t):
    dur = sdur("sr_outro")
    if lt < dur * 0.55:
        a = ease_out(lt / 0.3)
        k1 = back_out(lt / 0.4); k2 = back_out((lt - 0.5) / 0.4)
        if k1 > 0:
            d.rounded_rectangle(p(80, 180, 420, 380), radius=30 * S, fill=rgba(ACC, clamp(k1)))
            label(d, 250, 245, "GENIUS", BG, clamp(k1), size=max(1, 60 * k1))
        label(d, 450, 255, "OR", WHITE, a, size=40)
        if k2 > 0:
            d.rounded_rectangle(p(480, 180, 820, 380), radius=30 * S, fill=rgba(ACC2, clamp(k2)))
            label(d, 650, 245, "POINTLESS?", BG, clamp(k2), size=max(1, 50 * k2))
        label(d, 450, 500, "WHO BEATS 503 NEXT?", WHITE, ease_out((lt - 1.0) / 0.4), size=48)
        label(d, 450, 590, "TELL ME BELOW", MUTED, ease_out((lt - 1.3) / 0.4), size=32, f=SEMI)
    else:
        k = back_out((lt - dur * 0.55) / 0.5)
        bx, by, bs = 450, 220, 1.7 * k
        pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
        poly(d, [(bx + xx * bs, by + yy * bs) for xx, yy in pts], rgba(ACC, clamp(k)))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.55 - 0.4) / 0.4)
        d.rounded_rectangle(p(170, 600, 730, 710), radius=55 * S, fill=rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"sr_hook": vis_sr_hook, "sr_king": vis_sr_king, "sr_close": vis_sr_close, "sr_record": vis_sr_record,
            "sr_motors": vis_sr_motors, "sr_volts": vis_sr_volts, "sr_outro": vis_sr_outro})
