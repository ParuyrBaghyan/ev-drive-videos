# Episode visuals: Xiaomi YU7 GT Nürburgring SUV record vs Porsche/Audi (comparison).

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

def label_l(d, x, y, s, col, a, size=28, f=BLK):
    if a <= 0: return
    d.text((x * S, y * S), s, font=FL(f, max(1, int(size))), fill=rgba(col, a))

def label_r(d, x, y, s, col, a, size=28, f=BLK):
    if a <= 0: return
    fo = FL(f, max(1, int(size)))
    d.text((x * S - d.textlength(s, font=fo), y * S), s, font=fo, fill=rgba(col, a))

def chip(d, x, y, s, col, a, size=30, tcol=None):
    if a <= 0: return
    f = FL(BLK, max(1, int(size)))
    tw = d.textlength(s, font=f) / S
    w = tw + 50
    d.rounded_rectangle(p(x - w / 2, y, x + w / 2, y + size * 1.7), radius=size * 0.85 * S, fill=rgba(col, a))
    text_c(d, x, y + size * 0.3, s, f, rgba(tcol or BG, a))

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
    return w / (bb[2] - bb[0]), bb

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

def hbar(d, x, y, w, h, frac, col, a):
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=h / 2 * S, fill=rgba(PANEL, a))
    fw = max(h, w * clamp(frac))
    d.rounded_rectangle(p(x, y, x + fw, y + h), radius=h / 2 * S, fill=rgba(col, a))

def laptime(sec):
    m = int(sec // 60); s = sec - m * 60
    return f"{m}:{s:06.3f}"

def phone(d, x, y, w, h, a, glow=0.0):
    d.rounded_rectangle(p(x - 6, y - 6, x + w + 6, y + h + 6), radius=40 * S, fill=rgba(STEEL, a))
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=34 * S, fill=rgba((12, 16, 22), a))
    if glow > 0:
        d.rounded_rectangle(p(x + 10, y + 10, x + w - 10, y + h - 10), radius=26 * S, fill=rgba(ACC, a * glow * 0.18))
    d.rounded_rectangle(p(x + w / 2 - 34, y + 16, x + w / 2 + 34, y + 30), radius=7 * S, fill=rgba(BG, a))

def flag(d, x, y, sc, a):
    line(d, [(x, y), (x, y - 70 * sc)], rgba(WHITE, a), 5)
    n = 4
    for r in range(3):
        for c in range(n):
            col = WHITE if (r + c) % 2 == 0 else (20, 20, 20)
            xx = x + c * 14 * sc; yy = y - 70 * sc + r * 12 * sc
            d.rectangle(p(xx, yy, xx + 14 * sc, yy + 12 * sc), fill=rgba(col, a))

# ---------------- scenes ----------------
def vis_xm_hook(d, lt, t):
    streaks(d, t, 1.0, y0=330, y1=720, speed=1.4)
    label(d, 450, 20, "7:22.755", ACC, 1, size=170)
    label(d, 450, 230, "NÜRBURGRING · FASTEST SUV EVER", WHITE, 1, size=34)
    g = 0.6 + 0.4 * math.sin(t * 5)
    phone(d, 70, 330, 210, 400, 1, glow=g)
    label(d, 175, 500, "PHONE", MUTED, 1, size=30)
    label(d, 175, 540, "MAKER", MUTED, 1, size=30)
    x = 250 + 60 * ease_out(lt / 1.5)
    put_car(d, "cn_side_teal", x, 430, 580)
    for k in range(2):
        cx, cy, r = wheel_pos(x, 430, 580, k)
        for j in range(3):
            arc(d, cx, cy, r * 1.05, (t * 900 + j * 120) % 360, (t * 900 + j * 120 + 40) % 360, rgba(ACC, 0.5), 5)
    chip(d, 450, 780, "BEAT PORSCHE", ACC2, 1, size=40)

X0, X1, Y0, Y1 = 110, 790, 2014, 2026
def yx(yr): return X0 + (X1 - X0) * (yr - Y0) / (Y1 - Y0)

def vis_xm_race(d, lt, t):
    a = ease_out(lt / 0.4)
    # axis
    line(d, [(X0, 700), (X1, 700)], rgba(STEEL, a), 4)
    for yr in (2014, 2018, 2021, 2024, 2026):
        line(d, [(yx(yr), 690), (yx(yr), 710)], rgba(STEEL, a), 4)
        label(d, yx(yr), 722, str(yr), MUTED, a, size=26, f=SEMI)
    # Apple row
    label_l(d, X0, 120, "APPLE", WHITE, a, size=44)
    label_l(d, X0 + 175, 136, "CAR PROJECT", MUTED, a, size=24, f=SEMI)
    fa = ease_inout((lt - 0.3) / 2.2)
    w = (yx(2024) - yx(2014)) * fa
    d.rounded_rectangle(p(yx(2014), 200, yx(2014) + max(40, w), 250), radius=25 * S, fill=rgba(STEEL, a))
    label(d, yx(2014) + max(40, w) / 2, 205, f"~{int(round(10 * fa))} YEARS", WHITE, a if fa > 0.15 else 0, size=30)
    kx = back_out((lt - 2.6) / 0.4)
    if kx > 0:
        cx, cy, r = yx(2024) + 10, 225, 46 * kx
        line(d, [(cx - r, cy - r), (cx + r, cy + r)], rgba(RED, clamp(kx)), 12)
        line(d, [(cx - r, cy + r), (cx + r, cy - r)], rgba(RED, clamp(kx)), 12)
        chip(d, yx(2024), 285, "QUIT 2024", RED, clamp(kx), size=30, tcol=WHITE)
    # Xiaomi row
    kb = ease_out((lt - 0.9) / 0.4)
    label_l(d, X0, 400, "XIAOMI", ACC, kb, size=44)
    label_l(d, X0 + 200, 416, "PHONES → CARS", MUTED, kb, size=24, f=SEMI)
    fx = ease_inout((lt - 3.0) / 2.6)
    w2 = (yx(2026) - yx(2021)) * fx
    d.rounded_rectangle(p(yx(2021), 480, yx(2021) + max(40, w2), 530), radius=25 * S, fill=rgba(ACC, kb))
    for yr, txt, k0 in ((2021, "CAR PLAN", 0.0), (2024, "FIRST CAR", 0.6), (2026, "RING RECORD", 0.98)):
        k = ease_out((fx - k0) / 0.05) if fx >= k0 else 0
        if yr == 2021: k = kb
        if k > 0:
            circ(d, yx(yr), 505, 16, rgba(WHITE, k))
            ly = 440 if yr == 2024 else 560
            lx = min(max(yx(yr), 170), 730) if yr != 2024 else yx(yr) - 20
            label(d, lx, ly, txt, WHITE, k, size=26)
    kf = back_out((lt - 5.6) / 0.4)
    if kf > 0:
        flag(d, yx(2026) - 10, 470, 1.0 * kf, clamp(kf))

# Stylised Nordschleife-like loop (not to scale), logical coords
TRACK = [(150, 300), (190, 210), (270, 160), (360, 190), (430, 140), (520, 120), (600, 160), (660, 120),
         (740, 140), (780, 210), (740, 270), (770, 340), (720, 400), (640, 390), (580, 440), (500, 420),
         (450, 470), (370, 450), (300, 480), (230, 440), (180, 380), (150, 300)]

def track_pts(n=400):
    segs = []
    tot = 0
    for i in range(len(TRACK) - 1):
        (x0, y0), (x1, y1) = TRACK[i], TRACK[i + 1]
        l = math.hypot(x1 - x0, y1 - y0); segs.append((x0, y0, x1, y1, l)); tot += l
    return segs, tot

def track_at(u):
    segs, tot = track_pts()
    dist = (u % 1.0) * tot
    for x0, y0, x1, y1, l in segs:
        if dist <= l:
            f = dist / l
            return x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        dist -= l
    return TRACK[-1]

def draw_track(d, a, prog=1.0, col=None):
    line(d, TRACK, rgba(DARK, a), 26)
    line(d, TRACK, rgba(STEEL, a), 14)
    n = int(120 * prog)
    if n > 1:
        pts = [track_at(i / 120) for i in range(n + 1)]
        line(d, pts, rgba(col or ACC, a), 8)

def row(d, y, name, tm, col, a, hl=False, rank=None):
    if a <= 0: return
    d.rounded_rectangle(p(70, y, 830, y + 78), radius=20 * S, fill=rgba(PANEL, a), outline=rgba(col, a) if hl else None, width=int(3 * S))
    if rank:
        label(d, 115, y + 18, str(rank), col, a, size=38)
    label_l(d, 160, y + 22, name, WHITE if not hl else col, a, size=30)
    label_r(d, 805, y + 18, tm, col, a, size=38)

def vis_xm_ring(d, lt, t):
    a = ease_out(lt / 0.4)
    chip(d, 450, 20, "NORDSCHLEIFE · GERMANY", WHITE, a, size=30)
    prog = ease_inout((lt - 0.3) / 2.6)
    draw_track(d, a, prog)
    if prog > 0:
        x, y = track_at(prog * 0.999)
        circ(d, x, y, 20, rgba(ACC, 0.35)); circ(d, x, y, 11, rgba(WHITE, 1))
    label(d, 450, 270, "20.8 KM", WHITE, ease_out((lt - 1.0) / 0.4), size=56)
    label(d, 450, 340, "PER LAP", MUTED, ease_out((lt - 1.0) / 0.4), size=24, f=SEMI)
    label(d, 450, 525, "SUV RECORD BEFORE XIAOMI", MUTED, ease_out((lt - 2.6) / 0.3), size=26, f=SEMI)
    row(d, 575, "PORSCHE CAYENNE TURBO GT", "7:38.925", ACC2, ease_out((lt - 3.0) / 0.35))
    row(d, 670, "AUDI RS Q8 PERFORMANCE", "7:36.698", ACC2, ease_out((lt - 3.5) / 0.35))

def vis_xm_record(d, lt, t):
    a = ease_out(lt / 0.3)
    f = ease_out(lt / 2.4)
    tm = 442.755 * f
    label(d, 450, 30, laptime(tm), ACC, a, size=150)
    label(d, 450, 220, "XIAOMI YU7 GT · LAP TIME", WHITE, a, size=30)
    k = ease_out((lt - 2.4) / 0.5)
    # rows: before -> after sort
    yA0, yP0 = 360, 455
    sh = 95 * k
    row(d, 360 - (1 - k) * 60, "XIAOMI YU7 GT", "7:22.755", ACC, k, hl=True, rank=1)
    row(d, yA0 + sh, "AUDI RS Q8 PERFORMANCE", "7:36.698", ACC2, a, rank=2 if k > 0.5 else None)
    row(d, yP0 + sh, "PORSCHE CAYENNE TURBO GT", "7:38.925", ACC2, a, rank=3 if k > 0.5 else None)
    kb = back_out((lt - 3.2) / 0.45)
    if kb > 0:
        chip(d, 450, 690, "−13.9 SECONDS", ACC, clamp(kb), size=max(1, 52 * kb))

def vis_xm_specs(d, lt, t):
    a = ease_out(lt / 0.4)
    x, y, w = 70, 40, 760
    put_car(d, "side_xray", x, y, w, a)
    for kk in range(2):
        cx, cy, r = wheel_pos(x, y, w, kk)
        g = ease_out((lt - 0.3 - kk * 0.25) / 0.4)
        for j in range(3):
            ph = (t * 1.5 + j / 3) % 1
            ring(d, cx, cy, r * (0.6 + 0.6 * ph), rgba(ACC, g * (1 - ph)), 6)
        circ(d, cx, cy, r * 0.42, rgba(ACC, g * 0.9))
        for s_ in range(3):
            aa = t * 18 + s_ * 2.094
            line(d, [(cx, cy), (cx + math.cos(aa) * r * 0.38, cy + math.sin(aa) * r * 0.38)], rgba(BG, g), 5)
        label(d, cx, cy - r * 1.55, "MOTOR", ACC, g, size=24)
    # stat tiles
    tiles = [("HP", 990, "{:,.0f}", "738 KW"), ("0–100 KM/H", 2.92, "{:.2f} S", "UNDER 3 S"), ("FROM", 57000, "${:,.0f}", "389,900 YUAN")]
    for i, (hd, v, fmt, sub) in enumerate(tiles):
        k = ease_out((lt - 1.0 - i * 1.3) / 0.35)
        if k <= 0: continue
        cx = 165 + i * 285
        fv = ease_out((lt - 1.0 - i * 1.3) / 1.2)
        d.rounded_rectangle(p(cx - 130, 470 + 30 * (1 - k), cx + 130, 700 + 30 * (1 - k)), radius=24 * S, fill=rgba(PANEL, k), outline=rgba(ACC if i < 2 else ACC2, k), width=int(3 * S))
        label(d, cx, 490 + 30 * (1 - k), hd, MUTED, k, size=24, f=SEMI)
        label(d, cx, 535 + 30 * (1 - k), fmt.format(v * fv), ACC if i < 2 else ACC2, k, size=54 if i < 2 else 46)
        label(d, cx, 630 + 30 * (1 - k), sub, WHITE, k, size=22, f=SEMI)
    label(d, 450, 740, "2 MOTORS · 1 FRONT, 1 REAR", WHITE, ease_out((lt - 0.6) / 0.3), size=30)

def tire_top(d, cx, y, w, h, slick, col, a, t):
    d.rounded_rectangle(p(cx - w / 2, y, cx + w / 2, y + h), radius=22 * S, fill=rgba((26, 30, 38), a), outline=rgba(col, a), width=int(4 * S))
    if not slick:
        off = (t * 120) % 40
        for i in range(-1, int(h / 40) + 1):
            yy = y + i * 40 + off
            if y + 8 < yy < y + h - 8:
                line(d, [(cx - w / 2 + 14, yy), (cx - 4, yy + 16)], rgba(STEEL, a), 6)
                line(d, [(cx + 4, yy + 16), (cx + w / 2 - 14, yy)], rgba(STEEL, a), 6)
        for gx in (-w / 4, w / 4):
            line(d, [(cx + gx, y + 10), (cx + gx, y + h - 10)], rgba(BG, a), 6)
    else:
        line(d, [(cx, y + 14), (cx, y + h - 14)], rgba(BG, a * 0.8), 4)

def wheel_icon(d, cx, cy, r, a, t):
    ring(d, cx, cy, r, rgba(WHITE, a), 22)
    circ(d, cx, cy, r * 0.26, rgba(WHITE, a))
    for ang in (90, 210, 330):
        rr = math.radians(ang)
        line(d, [(cx, cy), (cx + math.cos(rr) * r, cy + math.sin(rr) * r)], rgba(WHITE, a), 16)

def vis_xm_catch(d, lt, t):
    dur = sdur("xm_catch")
    split = dur * 0.52
    if lt < split:
        a = ease_out(lt / 0.35)
        chip(d, 450, 30, "THE CATCH", RED, a, size=40, tcol=WHITE)
        k1 = ease_out((lt - 0.4) / 0.4); k2 = ease_out((lt - 0.9) / 0.4)
        tire_top(d, 270, 170 + 40 * (1 - k1), 150, 400, False, MUTED, k1, t)
        label(d, 270, 600, "STANDARD", MUTED, k1, size=28)
        label(d, 270, 640, "295 MM REAR", MUTED, k1, size=22, f=SEMI)
        tire_top(d, 630, 170 + 40 * (1 - k2), 165, 400, True, ACC2, k2, t)
        label(d, 630, 600, "SEMI-SLICK", ACC2, k2, size=28)
        label(d, 630, 640, "325 MM REAR", ACC2, k2, size=22, f=SEMI)
        chip(d, 450, 720, "TRACK PACKAGE · NOT ON SALE YET", ACC2, ease_out((lt - 1.6) / 0.35), size=30)
    else:
        lk = lt - split
        a = ease_out(lk / 0.3)
        draw_track(d, a * 0.6, 0)
        u = (lk / 4.0) % 1.0
        x, y = track_at(u)
        circ(d, x, y, 18, rgba(ACC, 0.4)); circ(d, x, y, 10, rgba(WHITE, a))
        kw = back_out(lk / 0.45)
        if kw > 0:
            wheel_icon(d, 450, 300, 85 * kw, clamp(kw) * 0.9, t)
            ka = clamp(kw)
            line(d, [(345, 195), (555, 405)], rgba(RED, ka), 14)
        label(d, 450, 530, "NOBODY AT THE WHEEL", WHITE, ease_out((lk - 0.4) / 0.3), size=40)
        f = ease_out((lk - 0.8) / 1.6)
        label(d, 450, 600, laptime(629.483 * f), ACC, ease_out((lk - 0.8) / 0.3), size=96)
        label(d, 450, 730, "SELF-DRIVING LAP · JUNE 2026", MUTED, ease_out((lk - 1.2) / 0.3), size=26, f=SEMI)

def vis_xm_outro(d, lt, t):
    dur = sdur("xm_outro")
    if lt < dur * 0.6:
        a = ease_out(lt / 0.3)
        k1 = back_out(lt / 0.4); k2 = back_out((lt - 0.6) / 0.4)
        if k1 > 0:
            d.rounded_rectangle(p(70, 140, 430, 460), radius=30 * S, fill=rgba(ACC, clamp(k1)))
            label(d, 250, 170, "XIAOMI", BG, clamp(k1), size=max(1, 46 * k1))
            label(d, 250, 245, "5 YRS", BG, clamp(k1), size=max(1, 88 * k1))
            label(d, 250, 375, "→ RECORD", BG, clamp(k1), size=max(1, 34 * k1))
        label(d, 450, 280, "VS", WHITE, a, size=36)
        if k2 > 0:
            d.rounded_rectangle(p(470, 140, 830, 460), radius=30 * S, fill=rgba(STEEL, clamp(k2)))
            label(d, 650, 170, "APPLE", WHITE, clamp(k2), size=max(1, 46 * k2))
            label(d, 650, 245, "10 YRS", WHITE, clamp(k2), size=max(1, 88 * k2))
            label(d, 650, 375, "→ QUIT", RED, clamp(k2), size=max(1, 34 * k2))
        label(d, 450, 540, "HOW DID THEY DO IT?", WHITE, ease_out((lt - 1.2) / 0.4), size=52)
        label(d, 450, 630, "TELL ME BELOW", MUTED, ease_out((lt - 1.5) / 0.4), size=32, f=SEMI)
    else:
        k = back_out((lt - dur * 0.6) / 0.5)
        bx, by, bs = 450, 220, 1.7 * k
        pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
        poly(d, [(bx + xx * bs, by + yy * bs) for xx, yy in pts], rgba(ACC, clamp(k)))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.6 - 0.4) / 0.4)
        d.rounded_rectangle(p(170, 600, 730, 710), radius=55 * S, fill=rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"xm_hook": vis_xm_hook, "xm_race": vis_xm_race, "xm_ring": vis_xm_ring, "xm_record": vis_xm_record,
            "xm_specs": vis_xm_specs, "xm_catch": vis_xm_catch, "xm_outro": vis_xm_outro})
