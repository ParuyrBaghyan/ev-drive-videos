# Episode visuals: Lohner-Porsche hub motors & the first series hybrid (History).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
CHROME = (176, 186, 200)
BLK = "InterDisplay-Black.otf"
SEMI = "Inter-SemiBold.otf"

def sdur(name):
    for s in scenes:
        if s["visual"] == name:
            return s["vis_end"] - s["start"]
    return 4.0

def poly(d, pts, col):
    d.polygon(p(*[v for xy in pts for v in xy]), fill=col)

def circ(d, x, y, r, col):
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=col)

def ring(d, x, y, r, col, w):
    d.ellipse(p(x - r, y - r, x + r, y + r), outline=col, width=max(1, int(w * S)))

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

def line(d, pts, col, w):
    d.line(p(*[v for xy in pts for v in xy]), fill=col, width=max(1, int(w * S)), joint="curve")

def arrow(d, x0, y0, x1, y1, col, w=10, head=26):
    line(d, [(x0, y0), (x1, y1)], col, w)
    ang = math.atan2(y1 - y0, x1 - x0)
    a1, a2 = ang + 2.6, ang - 2.6
    poly(d, [(x1 + math.cos(ang) * 6, y1 + math.sin(ang) * 6), (x1 + math.cos(a1) * head, y1 + math.sin(a1) * head),
             (x1 + math.cos(a2) * head, y1 + math.sin(a2) * head)], col)

def bolt(d, x, y, sc, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in pts], col)

def road(d, y, t, a, speed=1.0, x0=40, x1=860):
    line(d, [(x0, y), (x1, y)], rgba(DARK, a), 8)
    off = (t * 260 * speed) % 120
    for k in range(-1, 9):
        xx = x1 - k * 120 - off
        if x0 < xx < x1 - 50:
            line(d, [(xx, y + 40), (min(xx + 60, x1), y + 40)], rgba(STEEL, a), 6)


RED = (255, 84, 84)

def batt(d, x, y, w, h, frac, a, col=None, label_pct=True):
    # horizontal battery icon, fill frac in [0,1]
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=18 * S, fill=rgba(PANEL, a), outline=rgba(CHROME, a), width=6 * S)
    d.rounded_rectangle(p(x + w, y + h * 0.3, x + w + 22, y + h * 0.7), radius=6 * S, fill=rgba(CHROME, a))
    c = col or (ACC if frac > 0.25 else (ACC2 if frac > 0.1 else RED))
    fw = (w - 28) * clamp(frac)
    if fw > 2:
        d.rounded_rectangle(p(x + 14, y + 14, x + 14 + fw, y + h - 14), radius=10 * S, fill=rgba(c, a))


def wheel_spin(d, cx, cy, r, ang, col, a):
    circ(d, cx, cy, r, rgba((10, 13, 18), a))
    ring(d, cx, cy, r * 0.8, rgba(col, a), 6)
    for k in range(5):
        aa = ang + k * 2 * math.pi / 5
        line(d, [(cx, cy), (cx + math.cos(aa) * r * 0.78, cy + math.sin(aa) * r * 0.78)], rgba(col, a), 6)
    circ(d, cx, cy, r * 0.18, rgba(col, a))

def gear(d, cx, cy, r, ang, teeth, col, a):
    pts = []
    for k in range(teeth * 2):
        aa = ang + k * math.pi / teeth
        rr = r if k % 2 == 0 else r * 0.82
        pts.append((cx + math.cos(aa) * rr, cy + math.sin(aa) * rr))
    poly(d, pts, rgba(col, a))
    circ(d, cx, cy, r * 0.3, rgba(BG, a))

def counter(d, x, y, v, unit, col, a, size=120):
    label(d, x, y, f"{int(round(v))}", col, a, size=size)
    label(d, x, y + size * 1.05, unit, MUTED, a, size=28, f=SEMI)


def snowflake(d, x, y, r, col, a):
    for k in range(6):
        aa = k * math.pi / 3
        ex, ey = x + math.cos(aa) * r, y + math.sin(aa) * r
        line(d, [(x, y), (ex, ey)], rgba(col, a), 8)
        for sgn in (-1, 1):
            mx, my = x + math.cos(aa) * r * 0.6, y + math.sin(aa) * r * 0.6
            ba = aa + sgn * 0.7
            line(d, [(mx, my), (mx + math.cos(ba) * r * 0.3, my + math.sin(ba) * r * 0.3)], rgba(col, a), 6)

def flow_dots(d, pts, t, col, a, n=5, speed=0.8, r=9):
    # dots moving along a polyline
    segs = []; tot = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        Lg = math.hypot(x1 - x0, y1 - y0); segs.append((x0, y0, x1, y1, Lg)); tot += Lg
    for i in range(n):
        u = ((t * speed + i / n) % 1.0) * tot
        for x0, y0, x1, y1, Lg in segs:
            if u <= Lg:
                f = u / Lg; circ(d, x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, r, rgba(col, a)); break
            u -= Lg

WOOD = (150, 110, 70)
BRASS = (214, 176, 90)
SEPIA = (196, 170, 130)

def spoked_wheel(d, cx, cy, r, ang, a, hub_glow=0.0, rim=CHROME):
    circ(d, cx, cy, r, rgba((26, 30, 38), a))
    ring(d, cx, cy, r, rgba(rim, a), 10)
    ring(d, cx, cy, r * 0.88, rgba(WOOD, a), 6)
    for k in range(12):
        aa = ang + k * math.pi / 6
        line(d, [(cx + math.cos(aa) * r * 0.36, cy + math.sin(aa) * r * 0.36),
                 (cx + math.cos(aa) * r * 0.86, cy + math.sin(aa) * r * 0.86)], rgba(WOOD, a), 6)
    hc = tuple(int(STEEL[i] + (ACC[i] - STEEL[i]) * hub_glow) for i in range(3))
    circ(d, cx, cy, r * 0.36, rgba(hc, a))
    circ(d, cx, cy, r * 0.12, rgba(BG, a))

def old_car(d, x, y, sc, a, ang, glow=0.0):
    # 1900-style electric carriage: tall box body, coachman seat, big spoked wheels
    c = rgba((60, 70, 86), a); c2 = rgba((84, 96, 114), a)
    d.rounded_rectangle(p(x - 200 * sc, y - 150 * sc, x + 120 * sc, y - 10 * sc), radius=14 * S, fill=c)
    d.rounded_rectangle(p(x - 190 * sc, y - 270 * sc, x - 10 * sc, y - 150 * sc), radius=16 * S, fill=c2)
    d.rounded_rectangle(p(x - 175 * sc, y - 255 * sc, x - 30 * sc, y - 170 * sc), radius=10 * S, fill=rgba(BG, a))
    d.rounded_rectangle(p(x + 20 * sc, y - 200 * sc, x + 120 * sc, y - 150 * sc), radius=10 * S, fill=c2)  # front seat
    line(d, [(x + 120 * sc, y - 120 * sc), (x + 170 * sc, y - 210 * sc)], rgba(CHROME, a), 7 * sc)  # tiller
    spoked_wheel(d, x - 150 * sc, y + 20 * sc, 95 * sc, -ang, a)
    spoked_wheel(d, x + 140 * sc, y + 30 * sc, 85 * sc, -ang * 1.12, a, hub_glow=glow)

def hub_motor(d, cx, cy, r, ang, a):
    # cutaway: stator ring of coils + spinning rotor
    circ(d, cx, cy, r, rgba(PANEL, a))
    ring(d, cx, cy, r, rgba(CHROME, a), 8)
    for k in range(12):
        aa = k * math.pi / 6
        x0, y0 = cx + math.cos(aa) * r * 0.9, cy + math.sin(aa) * r * 0.9
        x1, y1 = cx + math.cos(aa) * r * 0.66, cy + math.sin(aa) * r * 0.66
        line(d, [(x0, y0), (x1, y1)], rgba(ACC2, a), 22)
    circ(d, cx, cy, r * 0.56, rgba(STEEL, a))
    for k in range(4):
        aa = ang + k * math.pi / 2
        poly(d, [(cx, cy), (cx + math.cos(aa - 0.35) * r * 0.54, cy + math.sin(aa - 0.35) * r * 0.54),
                 (cx + math.cos(aa + 0.35) * r * 0.54, cy + math.sin(aa + 0.35) * r * 0.54)], rgba(ACC if k % 2 else WHITE, a))
    circ(d, cx, cy, r * 0.12, rgba(BG, a))

def strike(d, x, y, w, a):
    line(d, [(x - w, y - w * 0.6), (x + w, y + w * 0.6)], rgba(RED, a), 12)

def engine_block(d, x, y, sc, a, t):
    d.rounded_rectangle(p(x - 80 * sc, y - 60 * sc, x + 80 * sc, y + 60 * sc), radius=12 * S, fill=rgba(STEEL, a))
    for k in range(3):
        yy = y - 40 * sc + k * 34 * sc
        line(d, [(x - 65 * sc, yy), (x + 65 * sc, yy)], rgba(CHROME, a), 5)
    pp = math.sin(t * 14) * 8 * sc
    d.rectangle(p(x - 30 * sc, y - 95 * sc + pp, x + 30 * sc, y - 60 * sc), fill=rgba(CHROME, a))

def gen_icon(d, x, y, r, a, t):
    circ(d, x, y, r, rgba(PANEL, a)); ring(d, x, y, r, rgba(ACC, a), 7)
    label(d, x, y - 24, "G", ACC, a, size=42)
    arc(d, x, y, r * 0.75, (t * 400) % 360, (t * 400) % 360 + 90, rgba(ACC, a), 6)

def batt_v(d, x, y, w, h, a, frac=1.0):
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=12 * S, fill=rgba(PANEL, a), outline=rgba(CHROME, a), width=5 * S)
    d.rectangle(p(x + w * 0.3, y - 14, x + w * 0.7, y), fill=rgba(CHROME, a))
    fh = (h - 20) * clamp(frac)
    d.rounded_rectangle(p(x + 10, y + h - 10 - fh, x + w - 10, y + h - 10), radius=8 * S, fill=rgba(ACC, a))

# ---------- scenes ----------
def vis_hm_hook(d, lt, t):
    a = ease_out(lt / 0.3)
    yr = 2026 - 126 * ease_inout((lt - 0.2) / 1.6)
    label(d, 450, 40, f"{int(round(yr))}", SEPIA if yr < 1950 else WHITE, a, size=170)
    k = back_out((lt - 1.6) / 0.5)
    if k > 0:
        spoked_wheel(d, 450, 520, 200 * clamp(k), t * 1.5, clamp(k), hub_glow=0.5 + 0.5 * math.sin(t * 5) ** 2)
        hub_motor(d, 450, 520, 70 * clamp(k), t * 6, clamp(k))
    chip(d, 450, 760, "MOTOR INSIDE THE WHEEL", ACC, ease_out((lt - 2.4) / 0.4), size=38)

def vis_hm_paris(d, lt, t):
    a = ease_out(lt / 0.4)
    x = -150 + 560 * ease_out(lt / 2.2)
    mv = 1 - ease_out(lt / 2.2)
    road(d, 530, t, a, speed=0.3 * mv)
    old_car(d, x, 470, 1.0, a, t * 3 * mv + 2.2 * ease_out(lt / 2.2) * 3, glow=ease_inout((lt - 2.4) / 0.6))
    chip(d, 450, 20, "PARIS · APRIL 1900", SEPIA, ease_out((lt - 0.3) / 0.4), size=36)
    lk = ease_out((lt - 2.8) / 0.4)
    if lk > 0:
        hx, hy = x + 140, 510
        arrow(d, 700, 690, hx + 30, hy + 50, rgba(ACC, lk), w=8)
        label(d, 700, 700, "FRONT HUB MOTORS", ACC, lk, size=34)

def vis_hm_direct(d, lt, t):
    dur = sdur("hm_direct")
    a = ease_out(lt / 0.4)
    spoked_wheel(d, 300, 300, 230, t * 1.2, a, hub_glow=1.0)
    hub_motor(d, 300, 300, 95, t * 7, a)
    label(d, 300, 545, "WHEEL = MOTOR", WHITE, a, size=34)
    items = ["GEARBOX", "CHAINS", "DRIVESHAFT"]
    for i, s in enumerate(items):
        k = ease_out((lt - 0.4 - 0.55 * i) / 0.35)
        yy = 140 + i * 120
        label(d, 700, yy, s, MUTED, k, size=40)
        sk = ease_out((lt - 0.65 - 0.55 * i) / 0.25)
        if sk > 0:
            line(d, [(580, yy + 26), (580 + 240 * sk, yy + 26)], rgba(RED, sk), 10)
    hk = back_out((lt - dur * 0.55) / 0.45)
    if hk > 0:
        chip(d, 450, 650, "≈ 2.5 HP PER MOTOR", ACC, clamp(hk), size=44)

def vis_hm_battery(d, lt, t):
    dur = sdur("hm_battery")
    a = ease_out(lt / 0.4)
    # battery blocks stacking up
    n = int(12 * ease_inout((lt - 0.2) / max(1.0, dur * 0.6)))
    for i in range(n):
        cx = 150 + (i % 4) * 95
        cy = 560 - (i // 4) * 105
        d.rounded_rectangle(p(cx - 42, cy - 45, cx + 42, cy + 45), radius=10 * S, fill=rgba((70, 78, 92), a), outline=rgba(CHROME, a), width=3 * S)
        d.rectangle(p(cx - 15, cy - 55, cx + 15, cy - 45), fill=rgba(CHROME, a))
        label(d, cx, cy - 18, "Pb", SEPIA, a, size=28)
    line(d, [(90, 615), (500, 615)], rgba(CHROME, a), 10)
    kg = 1800 * ease_inout((lt - 0.2) / max(1.0, dur * 0.6))
    label(d, 690, 130, f"{int(round(kg / 10) * 10):,}", WHITE, a, size=110)
    label(d, 690, 255, "KG OF LEAD-ACID", MUTED, a, size=30, f=SEMI)
    label(d, 690, 295, "(UP TO, SOME VERSIONS)", MUTED, a, size=24, f=SEMI)
    rk = ease_out((lt - dur * 0.62) / 0.4)
    if rk > 0:
        label(d, 450, 665, "RANGE", MUTED, rk, size=30, f=SEMI)
        d.rounded_rectangle(p(150, 710, 750, 760), radius=25 * S, fill=rgba(DARK, rk))
        d.rounded_rectangle(p(150, 710, 150 + 150 * ease_out((lt - dur * 0.62) / 0.6), 760), radius=25 * S, fill=rgba(ACC2, rk))
        label(d, 380, 712, "≈ 25 MI", ACC2, rk, size=36)

def vis_hm_hybrid(d, lt, t):
    dur = sdur("hm_hybrid")
    a = ease_out(lt / 0.4)
    ex, ey = 170, 200
    engine_block(d, ex, ey, 0.9, a, t)
    label(d, ex, ey + 70, "GASOLINE ENGINE", MUTED, a, size=24, f=SEMI)
    gk = ease_out((lt - 0.6) / 0.4)
    gen_icon(d, 450, ey, 62, gk, t)
    label(d, 450, ey + 70, "GENERATOR", MUTED, gk, size=24, f=SEMI)
    bk = ease_out((lt - 1.2) / 0.4)
    batt_v(d, 690, ey - 70, 100, 150, bk, frac=0.5 + 0.4 * ease_inout((lt - 1.4) / 3))
    label(d, 740, ey + 95, "BATTERY", MUTED, bk, size=24, f=SEMI)
    # flows
    if gk > 0:
        line(d, [(250, ey), (380, ey)], rgba(DARK, gk), 10); flow_dots(d, [(250, ey), (380, ey)], t, ACC2, gk, n=3, speed=1.2)
    if bk > 0:
        line(d, [(515, ey), (680, ey)], rgba(DARK, bk), 10); flow_dots(d, [(515, ey), (680, ey)], t, ACC, bk, n=3, speed=1.2)
    # down to wheel hub motors
    wk = ease_out((lt - 1.8) / 0.4)
    if wk > 0:
        spoked_wheel(d, 450, 520, 110, t * 2, wk, hub_glow=1.0)
        hub_motor(d, 450, 520, 42, t * 8, wk)
        pts = [(740, ey + 130), (740, 520), (570, 520)]
        line(d, pts, rgba(DARK, wk), 10); flow_dots(d, pts, t, ACC, wk, n=4, speed=0.9)
        label(d, 450, 645, "HUB MOTORS", MUTED, wk, size=24, f=SEMI)
    # broken link engine -> wheel
    xk = ease_out((lt - 2.6) / 0.4)
    if xk > 0:
        for j in range(6):
            y0 = ey + 100 + j * 50
            line(d, [(ex, y0), (ex, y0 + 26)], rgba(MUTED, xk), 6)
        line(d, [(ex, 520), (330, 520)], rgba(MUTED, xk), 6)
        strike(d, ex, 400, 40, xk)
        label(d, ex - 10, 585, "NO LINK", RED, xk, size=28)
    ck = back_out((lt - dur * 0.6) / 0.45)
    if ck > 0:
        chip(d, 450, 720, "SERIES HYBRID · SEMPER VIVUS", ACC, clamp(ck), size=36)

def vis_hm_range(d, lt, t):
    dur = sdur("hm_range")
    a = ease_out(lt / 0.4)
    rows = (("BATTERY ONLY", 25, ACC2), ("+ ENGINES", 100, ACC))
    for i, (lab, mi, col) in enumerate(rows):
        yy = 140 + i * 260
        k = ease_out((lt - 0.2 - 0.5 * i) / 0.4)
        label(d, 450, yy - 60, lab, MUTED, k, size=34, f=SEMI)
        d.rounded_rectangle(p(110, yy, 790, yy + 90), radius=30 * S, fill=rgba(DARK, k))
        g = ease_inout((lt - 0.4 - 0.5 * i) / 1.4)
        w = 680 * mi / 100 * g
        if w > 20:
            d.rounded_rectangle(p(110, yy, 110 + w, yy + 90), radius=30 * S, fill=rgba(col, k))
        label(d, 450, yy + 110, f"≈ {int(round(mi * g))} MI", col, k, size=46)
    chip(d, 450, 660, "IN PRODUCTION UNTIL 1915", SEPIA, ease_out((lt - 1.8) / 0.4), size=34)

def rover(d, x, y, sc, a, t):
    d.rounded_rectangle(p(x - 190 * sc, y - 60 * sc, x + 190 * sc, y - 20 * sc), radius=8 * S, fill=rgba(CHROME, a))
    line(d, [(x - 120 * sc, y - 60 * sc), (x - 150 * sc, y - 150 * sc)], rgba(CHROME, a), 6)
    poly(d, [(x + 60 * sc, y - 60 * sc), (x + 130 * sc, y - 60 * sc), (x + 95 * sc, y - 140 * sc)], rgba(STEEL, a))
    circ(d, x + 95 * sc, y - 170 * sc, 30 * sc, rgba(STEEL, a))
    for wx in (-140, 140):
        wheel_spin(d, x + wx * sc, y + 20 * sc, 55 * sc, t * 3, ACC, a)
        circ(d, x + wx * sc, y + 20 * sc, 16 * sc, rgba(ACC, a))

def vis_hm_outro(d, lt, t):
    dur = sdur("hm_outro")
    if lt < dur * 0.55:
        a = ease_out(lt / 0.3)
        circ(d, 760, 110, 60, rgba((200, 204, 212), a)); circ(d, 740, 95, 12, rgba((150, 156, 166), a))
        line(d, [(60, 500), (840, 500)], rgba(DARK, a), 6)
        rover(d, 450, 430, 1.0, a, t)
        chip(d, 450, 570, "EACH WHEEL ITS OWN MOTOR", ACC, ease_out((lt - 0.4) / 0.4), size=34)
        k = back_out((lt - dur * 0.3) / 0.4)
        if k > 0:
            chip(d, 450, 680, "SO WHY NOT TODAY?", ACC2, clamp(k), size=44)
    else:
        k = back_out((lt - dur * 0.55) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.55 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"hm_hook": vis_hm_hook, "hm_paris": vis_hm_paris, "hm_direct": vis_hm_direct, "hm_battery": vis_hm_battery,
            "hm_hybrid": vis_hm_hybrid, "hm_range": vis_hm_range, "hm_outro": vis_hm_outro})
