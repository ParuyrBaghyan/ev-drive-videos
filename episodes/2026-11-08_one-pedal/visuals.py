# Episode visuals: one-pedal driving (How it works).

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

def speedo(d, cx, cy, r, v, vmax, a, set_v=None):
    a0, a1 = 150, 390
    def ang(x): return a0 + (a1 - a0) * x / vmax
    arc(d, cx, cy, r, a0, a1, rgba(DARK, a), 22)
    arc(d, cx, cy, r, a0, ang(v), rgba(ACC, a), 22)
    if set_v is not None:
        sa = math.radians(ang(set_v))
        circ(d, cx + math.cos(sa) * r, cy + math.sin(sa) * r, 16, rgba(ACC2, a))
    na = math.radians(ang(v))
    line(d, [(cx, cy), (cx + math.cos(na) * (r - 24), cy + math.sin(na) * (r - 24))], rgba(WHITE, a), 9)
    circ(d, cx, cy, 16, rgba(WHITE, a))

def eye(d, cx, cy, sc, col, a, closed=0.0):
    # almond eye outline + iris; closed in [0,1] squashes it shut
    h = 60 * sc * (1 - closed) + 4
    pts_top = [(cx - 120 * sc + 240 * sc * u / 20, cy - h * math.sin(math.pi * u / 20)) for u in range(21)]
    pts_bot = [(cx + 120 * sc - 240 * sc * u / 20, cy + h * math.sin(math.pi * u / 20)) for u in range(21)]
    poly(d, pts_top + pts_bot, rgba(PANEL, a))
    line(d, pts_top + pts_bot + [pts_top[0]], rgba(col, a), 7)
    if closed < 0.7:
        r = 38 * sc * (1 - closed)
        circ(d, cx, cy, r, rgba(col, a)); circ(d, cx, cy, r * 0.45, rgba(BG, a))


RED = (255, 84, 84)

def batt(d, x, y, w, h, frac, a, col=None, label_pct=True):
    # horizontal battery icon, fill frac in [0,1]
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=18 * S, fill=rgba(PANEL, a), outline=rgba(CHROME, a), width=6 * S)
    d.rounded_rectangle(p(x + w, y + h * 0.3, x + w + 22, y + h * 0.7), radius=6 * S, fill=rgba(CHROME, a))
    c = col or (ACC if frac > 0.25 else (ACC2 if frac > 0.1 else RED))
    fw = (w - 28) * clamp(frac)
    if fw > 2:
        d.rounded_rectangle(p(x + 14, y + 14, x + 14 + fw, y + h - 14), radius=10 * S, fill=rgba(c, a))

def turtle(d, x, y, sc, col, a):
    c = rgba(col, a)
    # legs
    for lx in (-50, 40):
        d.rounded_rectangle(p(x + (lx - 12) * sc, y + 10 * sc, x + (lx + 12) * sc, y + 45 * sc), radius=8 * S, fill=c)
    # head
    circ(d, x + 95 * sc, y - 5 * sc, 26 * sc, c)
    # shell
    d.pieslice(p(x - 85 * sc, y - 80 * sc, x + 75 * sc, y + 80 * sc), 180, 360, fill=c)
    d.rectangle(p(x - 90 * sc, y - 2 * sc, x + 80 * sc, y + 16 * sc), fill=c)
    # shell pattern
    for sx in (-40, 0, 40):
        d.line(p(x + sx * sc - 18 * sc, y - 50 * sc, x + sx * sc, y - 20 * sc, x + sx * sc + 18 * sc, y - 50 * sc), fill=rgba(BG, a), width=int(5 * S * sc) or 1)

def truck(d, x, y, sc, a, bed_tilt=0.0):
    c = rgba(STEEL, a)
    # cab
    poly(d, [(x + 200 * sc, y + 30 * sc), (x + 200 * sc, y - 90 * sc), (x + 290 * sc, y - 90 * sc), (x + 330 * sc, y - 30 * sc), (x + 330 * sc, y + 30 * sc)], c)
    poly(d, [(x + 215 * sc, y - 78 * sc), (x + 280 * sc, y - 78 * sc), (x + 308 * sc, y - 36 * sc), (x + 215 * sc, y - 36 * sc)], rgba((10, 13, 18), a))
    # bed
    d.rounded_rectangle(p(x - 300 * sc, y - 2 * sc, x + 195 * sc, y + 22 * sc), radius=6 * S, fill=rgba(CHROME, a))
    d.rectangle(p(x - 300 * sc, y + 22 * sc, x + 330 * sc, y + 44 * sc), fill=c)
    for wx in (-220, -120, 260):
        circ(d, x + wx * sc, y + 60 * sc, 38 * sc, rgba((10, 13, 18), a))
        circ(d, x + wx * sc, y + 60 * sc, 18 * sc, rgba(CHROME, a))

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

# ---------- scenes ----------
RED = (255, 84, 84)
ICE = (120, 200, 255)

def rot(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]

def pedal(d, x, y, press, sc, col, a, wide=1.0):
    # pivot at (x,y) top; press in [0,1] rotates the pad forward (toward +x)
    ang = math.radians(-8 + 26 * press)
    arm = rot([(-8 * sc, 0), (8 * sc, 0), (8 * sc, 300 * sc), (-8 * sc, 300 * sc)], x, y, -ang)
    poly(d, arm, rgba(STEEL, a))
    pad = rot([(-70 * sc * wide, 250 * sc), (40 * sc * wide, 250 * sc), (40 * sc * wide, 330 * sc), (-70 * sc * wide, 330 * sc)], x, y, -ang)
    poly(d, pad, rgba(col, a))
    circ(d, x, y, 16 * sc, rgba(CHROME, a))
    return pad

def car_tilt(d, x, y, sc, ang, body, a, brake_glow=0.0):
    pts = [(-230, 40), (-230, -10), (-200, -40), (-110, -50), (-60, -110), (90, -112), (160, -55), (225, -40), (238, 0), (238, 40)]
    P = lambda q: rot([(qx * sc, qy * sc) for qx, qy in q], x, y, ang)
    poly(d, P(pts), rgba(body, a))
    poly(d, P([(-45, -95), (10, -97), (10, -52), (-90, -52)]), rgba((10, 13, 18), a))
    poly(d, P([(25, -97), (82, -97), (130, -52), (25, -52)]), rgba((10, 13, 18), a))
    for wx in (-140, 140):
        (cx, cy), = P([(wx, 40)])
        circ(d, cx, cy, 52 * sc, rgba((10, 13, 18), a)); circ(d, cx, cy, 40 * sc, rgba((60, 68, 80), a)); circ(d, cx, cy, 16 * sc, rgba(body, a))
    if brake_glow > 0:
        (bx, by), = P([(-226, -18)])
        circ(d, bx, by, 14 * sc + 4, rgba(RED, brake_glow))
        for k in range(3):
            ring(d, bx, by, (30 + k * 18) * sc + 6, rgba(RED, brake_glow * (0.6 - k * 0.18)), 5)

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

# ---------- scenes ----------
def vis_op_hook(d, lt, t):
    dur = sdur("op_hook")
    a = ease_out(lt / 0.4)
    line(d, [(80, 700), (820, 700)], rgba(DARK, a), 10)
    # brake pedal (wide)
    bk = ease_out((lt - 1.0) / 0.5)
    pedal(d, 300, 250, 0.0, 1.25, (110, 120, 136) if bk < 0.5 else (60, 68, 80), a, wide=1.5)
    label(d, 285, 720, "BRAKE", MUTED, a, size=34, f=SEMI)
    # accelerator, pumping
    press = 0.5 + 0.5 * math.sin(t * 3.2)
    glow = 0.75 + 0.25 * math.sin(t * 6)
    pedal(d, 620, 250, press, 1.25, ACC, a * glow)
    label(d, 625, 720, "ACCELERATOR", ACC, a, size=34, f=SEMI)
    if bk > 0:
        line(d, [(185, 520), (185 + 200 * bk, 520 + 160 * bk)], rgba(ACC2, bk), 16)
        line(d, [(385, 520), (385 - 200 * bk, 520 + 160 * bk)], rgba(ACC2, bk), 16)
    k = back_out((lt - 0.4) / 0.45)
    chip(d, 450, 60, "JUST ONE PEDAL?", ACC, clamp(k), size=46)

def vis_op_map(d, lt, t):
    dur = sdur("op_map")
    a = ease_out(lt / 0.4)
    # pedal position: starts pressed, eases off, repeats
    if lt < 2.6:
        pos = 0.55 + 0.3 * math.sin(lt * 2.4)
    elif lt < 4.0:
        p0 = 0.55 + 0.3 * math.sin(2.6 * 2.4)
        pos = p0 + (0.9 - p0) * ease_inout((lt - 2.6) / 0.6)
    else:
        pos = 0.9 - 0.8 * ease_inout((lt - 4.0) / 1.0)
    pedal(d, 150, 40, pos, 0.95, ACC if pos > 0.3 else ACC2, a)
    label(d, 135, 380, "PEDAL", MUTED, a, size=28, f=SEMI)
    # car with torque arrow
    car_tilt(d, 600, 200, 0.62, 0, WHITE, a, brake_glow=0)
    tq = (pos - 0.3) / 0.6  # >0 drive, <0 regen
    if tq > 0.03:
        arrow(d, 600, 330, 600 + 230 * min(1, tq), 330, rgba(ACC, a), 12, 30)
        label(d, 600, 360, "MOTOR PUSHES", ACC, a, size=32)
    elif tq < -0.03:
        arrow(d, 600, 330, 600 - 230 * min(1, -tq * 1.6), 330, rgba(ACC2, a), 12, 30)
        label(d, 600, 360, "MOTOR BRAKES", ACC2, a, size=32)
    else:
        label(d, 600, 360, "COAST", MUTED, a, size=32)
    # pedal travel map
    ba = ease_out((lt - 0.6) / 0.5)
    x0, x1, y = 110, 790, 560
    xc = x0 + (x1 - x0) * 0.3
    d.rounded_rectangle(p(x0, y, xc, y + 70), radius=20 * S, fill=rgba(ACC2, ba * 0.85))
    d.rounded_rectangle(p(xc, y, x1, y + 70), radius=20 * S, fill=rgba(ACC, ba * 0.85))
    line(d, [(xc, y - 20), (xc, y + 90)], rgba(WHITE, ba), 6)
    label(d, (x0 + xc) / 2, y + 16, "REGEN", BG, ba, size=32)
    label(d, (xc + x1) / 2, y + 16, "DRIVE", BG, ba, size=32)
    label(d, xc, y + 100, "COAST", WHITE, ba, size=24, f=SEMI)
    label(d, x0 + 10, y + 100, "OFF", MUTED, ba, size=24, f=SEMI)
    label(d, x1 - 30, y + 100, "FLOOR", MUTED, ba, size=24, f=SEMI)
    label(d, 450, y - 70, "PEDAL TRAVEL", MUTED, ba, size=26, f=SEMI)
    mx = x0 + (x1 - x0) * pos
    poly(d, [(mx, y - 6), (mx - 22, y - 40), (mx + 22, y - 40)], rgba(WHITE, ba))
    line(d, [(mx, y - 6), (mx, y + 76)], rgba(WHITE, ba), 5)

def vis_op_regen(d, lt, t):
    dur = sdur("op_regen")
    a = ease_out(lt / 0.4)
    pr = ease_out((lt - 0.3) / max(0.5, dur - 0.8))
    spin = t * (7 - 4 * pr)
    wheel_spin(d, 160, 360, 115, spin, CHROME, a)
    label(d, 160, 500, "WHEEL", MUTED, a, size=26, f=SEMI)
    mph = 40 - 25 * pr
    label(d, 160, 120, f"{int(round(mph))}", WHITE, a, size=90)
    label(d, 160, 220, "MPH", MUTED, a, size=24, f=SEMI)
    # motor as generator
    ma = ease_out((lt - 0.4) / 0.4)
    d.rounded_rectangle(p(330, 270, 560, 450), radius=24 * S, fill=rgba(PANEL, ma), outline=rgba(ACC2, ma), width=5 * S)
    gear(d, 445, 360, 62, -spin * 1.4, 10, STEEL, ma)
    circ(d, 445, 360, 20, rgba(ACC2, ma))
    label(d, 445, 470, "GENERATOR", ACC2, ma, size=28)
    # battery
    fill = 0.35 + 0.4 * pr
    bx0, by0, bx1, by1 = 650, 200, 810, 520
    d.rounded_rectangle(p(bx0, by0, bx1, by1), radius=20 * S, fill=rgba(PANEL, ma), outline=rgba(CHROME, ma), width=6 * S)
    d.rounded_rectangle(p(bx0 + 45, by0 - 22, bx1 - 45, by0 + 4), radius=6 * S, fill=rgba(CHROME, ma))
    top = by1 - 14 - (by1 - by0 - 28) * fill
    d.rounded_rectangle(p(bx0 + 14, top, bx1 - 14, by1 - 14), radius=10 * S, fill=rgba(ACC, ma))
    label(d, 730, 540, f"{int(round(fill * 100))}%", ACC, ma, size=40)
    # energy flow
    fa = ease_out((lt - 0.8) / 0.4)
    line(d, [(275, 360), (330, 360)], rgba(STEEL, fa), 8)
    line(d, [(560, 360), (650, 360)], rgba(STEEL, fa), 8)
    flow_dots(d, [(275, 360), (330, 360)], t, ACC2, fa, n=2, speed=1.4)
    flow_dots(d, [(560, 360), (650, 360)], t, ACC, fa, n=3, speed=1.4)
    k = back_out((lt - 1.4) / 0.4)
    chip(d, 450, 680, "SPEED  →  CHARGE", ACC, clamp(k), size=44)

def vis_op_force(d, lt, t):
    dur = sdur("op_force")
    a = ease_out(lt / 0.4)
    # g-ball
    gx, gy, gr = 230, 230, 150
    ring(d, gx, gy, gr, rgba(STEEL, a), 6); ring(d, gx, gy, gr * 0.5, rgba(DARK, a), 4)
    line(d, [(gx - gr, gy), (gx + gr, gy)], rgba(DARK, a), 3); line(d, [(gx, gy - gr), (gx, gy + gr)], rgba(DARK, a), 3)
    g = 0.2 * ease_out((lt - 0.4) / 1.4)
    dy = -gr * g / 0.4
    circ(d, gx, gy + dy, 26, rgba(ACC2, a))
    ring(d, gx, gy + dy, 42, rgba(ACC2, a * 0.4), 5)
    label(d, gx, gy + gr + 20, "G-FORCE", MUTED, a, size=24, f=SEMI)
    # counter
    ca = ease_out((lt - 0.3) / 0.4)
    d.rounded_rectangle(p(450, 90, 840, 400), radius=26 * S, fill=rgba(PANEL, ca), outline=rgba(STEEL, ca), width=3 * S)
    label(d, 645, 115, "UP TO", MUTED, ca, size=26, f=SEMI)
    label(d, 645, 160, f"{g:.2f} g", ACC2, ca, size=100)
    label(d, 645, 310, "NISSAN e-PEDAL", MUTED, ca, size=24, f=SEMI)
    label(d, 645, 345, "≈ A NORMAL BRAKE STOP", WHITE, ca, size=24, f=SEMI)
    # car slowing with brake lights
    pa = ease_out((lt - 0.8) / 0.4)
    road(d, 700, t, pa, speed=max(0.05, 0.8 - 0.6 * ease_out((lt - 0.8) / 2)))
    bl = ease_out((lt - 1.8) / 0.3) * (0.85 + 0.15 * math.sin(t * 8))
    car_tilt(d, 450, 610, 0.62, 0, WHITE, pa, brake_glow=bl)
    k = back_out((lt - 2.0) / 0.4)
    chip(d, 450, 760, "BRAKE LIGHTS ON", RED, clamp(k), size=36, tcol=WHITE)

def vis_op_stop(d, lt, t):
    dur = sdur("op_stop")
    a = ease_out(lt / 0.4)
    grade = 0.30
    ang = -math.atan(grade)
    hx0, hy0 = 40, 800
    hx1 = 860; hy1 = hy0 - grade * (hx1 - hx0)
    poly(d, [(hx0, hy0), (hx1, hy1), (hx1, 860), (hx0, 860)], rgba(PANEL, a))
    line(d, [(hx0, hy0), (hx1, hy1)], rgba(STEEL, a), 8)
    # car moves up the slope and stops
    stop_t = min(2.2, dur * 0.5)
    u = ease_out(lt / stop_t)
    s = 170 + 330 * u
    cxp = hx0 + s * math.cos(-ang)
    cyp = hy0 - s * math.sin(-ang)
    sc = 0.62
    # offset car above the slope surface (wheels at y=+40+52 below center)
    nx, ny = math.sin(-ang), -math.cos(-ang)
    off = 92 * sc
    car_tilt(d, cxp + nx * off * 0 - 0, cyp - off * math.cos(ang), sc, ang, WHITE, a, brake_glow=0.9 if lt > stop_t * 0.7 else 0)
    # speed counter
    mph = 12 * (1 - u)
    label(d, 160, 60, f"{int(math.ceil(mph - 0.01)) if mph > 0.05 else 0}", WHITE, a, size=110)
    label(d, 160, 190, "MPH", MUTED, a, size=26, f=SEMI)
    # stages
    k1 = back_out((lt - 0.5) / 0.35)
    chip(d, 590, 50, "REGEN + FRICTION", ACC2, clamp(k1), size=34)
    k2 = back_out((lt - stop_t) / 0.4)
    if k2 > 0:
        pulse = 0.8 + 0.2 * math.sin(t * 5)
        chip(d, 590, 140, "HOLD", ACC, clamp(k2) * pulse, size=50)
    k3 = ease_out((lt - stop_t - 0.5) / 0.4)
    label(d, 640, 800 - 0.3 * 600 + 120, "≈ 30% GRADE", MUTED, k3, size=30, f=SEMI)
    # grade triangle

def vis_op_limits(d, lt, t):
    dur = sdur("op_limits")
    a = ease_out(lt / 0.4)
    # two causes
    k1 = back_out((lt - 0.2) / 0.4)
    if k1 > 0:
        kk = clamp(k1)
        d.rounded_rectangle(p(70, 30, 430, 300), radius=26 * S, fill=rgba(PANEL, kk), outline=rgba(STEEL, kk), width=3 * S)
        batt(d, 120, 95, 240, 110, 1.0, kk, col=ACC)
        label(d, 250, 225, "FULL BATTERY", WHITE, kk, size=30)
    k2 = back_out((lt - 0.7) / 0.4)
    if k2 > 0:
        kk = clamp(k2)
        d.rounded_rectangle(p(470, 30, 830, 300), radius=26 * S, fill=rgba(PANEL, kk), outline=rgba(STEEL, kk), width=3 * S)
        snowflake(d, 650, 145, 70 * kk, ICE, kk)
        label(d, 650, 225, "COLD BATTERY", WHITE, kk, size=30)
    # regen bar shrinking
    ra = ease_out((lt - 1.0) / 0.4)
    sh = ease_inout((lt - 1.3) / 1.2)
    label(d, 450, 345, "REGEN BRAKING", MUTED, ra, size=28, f=SEMI)
    d.rounded_rectangle(p(110, 395, 790, 455), radius=30 * S, fill=rgba(DARK, ra))
    w = 680 * (1 - 0.7 * sh)
    if ra > 0:
        d.rounded_rectangle(p(110, 395, 110 + w, 455), radius=30 * S, fill=rgba(ACC2, ra))
    label(d, 450, 470, "WEAKER", ACC2, ease_out((lt - 2.0) / 0.3), size=34)
    # brake pedal lights up
    pk = ease_out((lt - dur * 0.55) / 0.4)
    if pk > 0:
        press = 0.6 * ease_out((lt - dur * 0.55 - 0.3) / 0.4)
        pedal(d, 230, 530, press, 0.75, RED, pk, wide=1.5)
        chip(d, 590, 700, "HARD STOP = BRAKE", RED, pk, size=34, tcol=WHITE)

def vis_op_outro(d, lt, t):
    dur = sdur("op_outro")
    if lt < dur * 0.5:
        a = ease_out(lt / 0.4)
        pedal(d, 450, 120, 0.0, 1.1, (90, 100, 116), a, wide=1.5)
        k = back_out((lt - 0.4) / 0.45)
        chip(d, 450, 30, "BACKUP?", ACC2, clamp(k), size=60)
    else:
        k = back_out((lt - dur * 0.5) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.5 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"op_hook": vis_op_hook, "op_map": vis_op_map, "op_regen": vis_op_regen, "op_force": vis_op_force,
            "op_stop": vis_op_stop, "op_limits": vis_op_limits, "op_outro": vis_op_outro})
