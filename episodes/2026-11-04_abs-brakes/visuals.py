# Episode visuals: how anti-lock brakes (ABS) keep you steering.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
HOLE = (8, 10, 14)
ICE = (150, 215, 255)
RED = (255, 80, 80)
BLK = "InterDisplay-Black.otf"
BLD = "InterDisplay-Bold.otf"
SEMI = "Inter-SemiBold.otf"

def sdur(name):
    for s in scenes:
        if s["visual"] == name:
            return s["vis_end"] - s["start"]
    return 4.0

def poly(d, pts, col, outline=None, w=0):
    d.polygon(p(*[v for xy in pts for v in xy]), fill=col, outline=outline, width=int(w * S) if w else 0)

def circ(d, x, y, r, col):
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=col)

def ring(d, x, y, r, col, w):
    d.ellipse(p(x - r, y - r, x + r, y + r), outline=col, width=int(w * S))

def label(d, x, y, s, col, a, size=28, f=SEMI):
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
    d.line(p(*[v for xy in pts for v in xy]), fill=col, width=int(w * S), joint="curve")

def arrow(d, x0, y0, x1, y1, col, w=10, head=26):
    line(d, [(x0, y0), (x1, y1)], col, w)
    ang = math.atan2(y1 - y0, x1 - x0)
    a1, a2 = ang + 2.6, ang - 2.6
    poly(d, [(x1 + math.cos(ang) * 6, y1 + math.sin(ang) * 6), (x1 + math.cos(a1) * head, y1 + math.sin(a1) * head),
             (x1 + math.cos(a2) * head, y1 + math.sin(a2) * head)], col)

def bolt(d, x, y, sc, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in pts], col)

def rot(pts, cx, cy, ang):
    c, s_ = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s_, cy + (x - cx) * s_ + (y - cy) * c) for x, y in pts]

def top_car(d, cx, cy, sc, a, steer=0.0, body=WHITE, wheel_col=None):
    """Top-down car pointing up. steer = front wheel angle (rad)."""
    wc = wheel_col or (30, 36, 46)
    # wheels
    for wx, wy, front in [(-62, -80, True), (62, -80, True), (-62, 80, False), (62, 80, False)]:
        x, y = cx + wx * sc, cy + wy * sc
        pts = [(x - 13 * sc, y - 28 * sc), (x + 13 * sc, y - 28 * sc), (x + 13 * sc, y + 28 * sc), (x - 13 * sc, y + 28 * sc)]
        if front: pts = rot(pts, x, y, steer)
        poly(d, pts, rgba(wc, a))
    d.rounded_rectangle(p(cx + 8 - 58 * sc, cy + 10 - 135 * sc, cx + 8 + 58 * sc, cy + 10 + 135 * sc), radius=40 * sc * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(cx - 58 * sc, cy - 135 * sc, cx + 58 * sc, cy + 135 * sc), radius=40 * sc * S, fill=rgba(body, a))
    # glass
    d.rounded_rectangle(p(cx - 44 * sc, cy - 62 * sc, cx + 44 * sc, cy - 18 * sc), radius=12 * sc * S, fill=rgba(BG, a))
    d.rounded_rectangle(p(cx - 42 * sc, cy + 50 * sc, cx + 42 * sc, cy + 80 * sc), radius=10 * sc * S, fill=rgba(BG, a))
    # headlights
    line(d, [(cx - 44 * sc, cy - 128 * sc), (cx - 20 * sc, cy - 132 * sc)], rgba(ACC, a), 6)
    line(d, [(cx + 20 * sc, cy - 132 * sc), (cx + 44 * sc, cy - 128 * sc)], rgba(ACC, a), 6)

def steering_wheel(d, cx, cy, r, ang, col, a):
    ring(d, cx, cy, r, rgba(col, a), 14)
    for k in (0, 2.1, 4.2):
        aa = ang + k + math.pi / 2
        line(d, [(cx, cy), (cx + math.cos(aa) * r, cy + math.sin(aa) * r)], rgba(col, a), 10)
    circ(d, cx, cy, r * 0.25, rgba(col, a))

def side_tire(d, cx, cy, r, ang, a, col=WHITE):
    circ(d, cx, cy, r, rgba((30, 36, 46), a))
    circ(d, cx, cy, r * 0.62, rgba(STEEL, a))
    for k in range(16):
        aa = ang + k * 2 * math.pi / 16
        line(d, [(cx + math.cos(aa) * r * 0.84, cy + math.sin(aa) * r * 0.84), (cx + math.cos(aa) * r * 0.98, cy + math.sin(aa) * r * 0.98)], rgba(MUTED, a), 7)
    for k in range(5):
        aa = ang + k * 2 * math.pi / 5
        line(d, [(cx, cy), (cx + math.cos(aa) * r * 0.55, cy + math.sin(aa) * r * 0.55)], rgba(col, a), 10)
    circ(d, cx, cy, r * 0.12, rgba(col, a))

# ---------- scenes ----------
def vis_abs_hook(d, lt, t):
    dur = sdur("abs_hook")
    a = ease_out(lt / 0.3)
    # icy road
    d.rounded_rectangle(p(230, 20, 670, 880), radius=30 * S, fill=rgba((24, 40, 56), a))
    for i in range(14):
        yy = (i * 70 + lt * 260) % 900
        line(d, [(450, yy), (450, yy + 34)], rgba(MUTED, a * 0.6), 6)
    rng = [(260 + (k * 97) % 390, (k * 151) % 860) for k in range(26)]
    for x, y in rng:
        yy = (y + lt * 260) % 860 + 20
        circ(d, x, yy, 4, rgba(ICE, a * 0.5))
    # intended curved path (dashed, lime) vs actual straight slide
    pa = ease_out((lt - 0.4) / 0.6)
    for k in range(10):
        u0, u1 = k / 10, (k + 0.5) / 10
        if u1 > pa: break
        f = lambda u: (450 + 180 * u * u, 520 - 420 * u)
        line(d, [f(u0), f(u1)], rgba(ACC, a), 8)
    if pa > 0.9:
        label(d, 735, 230, "WHERE YOU STEER", ACC, ease_out((lt - 1.0) / 0.3), size=28, f=BLK)
    # car slides straight; front wheels turned
    steer = 0.45 * ease_out((lt - 0.3) / 0.5)
    cy = 560 - 120 * ease_out(lt / max(dur, 1))
    jitter = math.sin(lt * 40) * 2
    # skid marks behind locked wheels
    for wx in (-62, 62):
        line(d, [(450 + wx * 0.9, cy + 100), (450 + wx * 0.9, 880)], rgba(HOLE, a * 0.8), 18)
    top_car(d, 450 + jitter, cy, 0.9, a, steer=steer)
    arrow(d, 450, cy - 150, 450, cy - 260, rgba(ACC2, ease_out((lt - 0.8) / 0.3)), w=10)
    label(d, 450, cy - 320, "WHERE YOU GO", ACC2, ease_out((lt - 1.0) / 0.3), size=28, f=BLK)
    # steering wheel turning, useless
    sw = 0.9 * math.sin(min(lt, 3) * 2.2)
    d.rounded_rectangle(p(30, 680, 210, 860), radius=30 * S, fill=rgba(PANEL, a))
    steering_wheel(d, 120, 770, 62, sw, WHITE, a)
    chip(d, 760, 720, "LOCKED", RED, ease_out((lt - 1.3) / 0.3), size=34, tcol=WHITE)

def vis_abs_lock(d, lt, t):
    a = ease_out(lt / 0.35)
    gy = 500
    for side, x in ((0, 230), (1, 670)):
        sa = ease_out((lt - side * 0.6) / 0.4)
        d.rounded_rectangle(p(x - 200, 70, x + 200, 860), radius=28 * S, fill=rgba(PANEL, a * 0.9))
        # ground with moving texture
        line(d, [(x - 180, gy + 120), (x + 180, gy + 120)], rgba(DARK, sa), 8)
        for k in range(8):
            xx = x - 180 + ((k * 52 - lt * 220) % 360)
            line(d, [(xx, gy + 132), (xx - 16, gy + 146)], rgba(MUTED, sa * 0.5), 4)
        if side == 0:
            side_tire(d, x, gy, 120, lt * 5, sa, ACC)
            label(d, x, 110, "ROLLING", ACC, sa, size=46, f=BLK)
        else:
            side_tire(d, x + math.sin(lt * 50) * 2, gy, 120, 0.3, sa, RED)
            for k in range(3):
                line(d, [(x - 140 - k * 30, gy + 112 - k * 12), (x - 60 - k * 30, gy + 112 - k * 12)], rgba(ACC2, sa * 0.7), 6)
            label(d, x, 110, "SLIDING", RED, sa, size=46, f=BLK)
            circ(d, x + 6, gy + 120, 10 + 4 * math.sin(lt * 20), rgba(ACC2, sa * 0.8))
        # steering grip bar
        ba = ease_out((lt - 1.2 - side * 0.4) / 0.6)
        label(d, x, 680, "SIDEWAYS GRIP", WHITE, ba, size=26, f=BLK)
        d.rounded_rectangle(p(x - 150, 730, x + 150, 776), radius=23 * S, fill=rgba(DARK, ba))
        frac = (0.92 if side == 0 else 0.1) * ba
        d.rounded_rectangle(p(x - 150, 730, x - 150 + 300 * max(frac, 0.06), 776), radius=23 * S, fill=rgba(ACC if side == 0 else RED, ba))
        # sideways force arrows on rolling tire
        if side == 0:
            fa = ease_out((lt - 1.6) / 0.4)
            arrow(d, x, gy + 175, x + 130 * fa + 1, gy + 175, rgba(ACC, fa), w=8, head=20)
            arrow(d, x, gy + 175, x - 130 * fa - 1, gy + 175, rgba(ACC, fa), w=8, head=20)

def vis_abs_sensors(d, lt, t):
    dur = sdur("abs_sensors")
    a = ease_out(lt / 0.35)
    # tone ring + sensor (left top)
    cx, cy, r = 220, 250, 135
    ang = lt * 3.2 * (1 - 0.6 * ease_out((lt - 3.0) / 1.5))
    circ(d, cx, cy, r + 12, rgba(PANEL, a))
    for k in range(24):
        aa = ang + k * 2 * math.pi / 24
        pts = [(cx + math.cos(aa - 0.06) * r * 0.82, cy + math.sin(aa - 0.06) * r * 0.82), (cx + math.cos(aa - 0.06) * r, cy + math.sin(aa - 0.06) * r),
               (cx + math.cos(aa + 0.06) * r, cy + math.sin(aa + 0.06) * r), (cx + math.cos(aa + 0.06) * r * 0.82, cy + math.sin(aa + 0.06) * r * 0.82)]
        poly(d, pts, rgba(STEEL, a))
    circ(d, cx, cy, r * 0.8, rgba((30, 36, 46), a))
    circ(d, cx, cy, r * 0.25, rgba(MUTED, a))
    # sensor head
    d.rounded_rectangle(p(cx + r + 6, cy - 22, cx + r + 110, cy + 22), radius=10 * S, fill=rgba(ACC, a))
    label(d, cx, cy + r + 28, "WHEEL-SPEED SENSOR", ACC, ease_out((lt - 0.4) / 0.4), size=26, f=BLK)
    # pulse signal wire to ECU
    ex, ey = 700, 250
    d.rounded_rectangle(p(ex - 110, ey - 80, ex + 110, ey + 80), radius=18 * S, fill=rgba(PANEL, a), outline=rgba(ACC, a), width=3 * S)
    for k in range(5):
        line(d, [(ex - 80 + k * 40, ey - 80), (ex - 80 + k * 40, ey - 100)], rgba(STEEL, a), 8)
        line(d, [(ex - 80 + k * 40, ey + 80), (ex - 80 + k * 40, ey + 100)], rgba(STEEL, a), 8)
    label(d, ex, ey - 22, "ABS", WHITE, a, size=40, f=BLK)
    label(d, ex, ey + 22, "COMPUTER", MUTED, a, size=22, f=BLK)
    wx0, wx1 = cx + r + 110, ex - 110
    pts = []
    for i in range(41):
        u = i / 40
        x = wx0 + (wx1 - wx0) * u
        sq = 1 if math.sin((u * 6 - lt * 6) * math.pi) > 0 else -1
        pts.append((x, ey + sq * 16))
    line(d, pts, rgba(ACC, a * 0.9), 4)
    # speed graph
    gx0, gx1, gy0, gy1 = 110, 820, 470, 800
    ga = ease_out((lt - 0.8) / 0.4)
    line(d, [(gx0, gy0), (gx0, gy1), (gx1, gy1)], rgba(MUTED, ga), 4)
    prog = clamp((lt - 1.0) / max(dur - 2.0, 1))
    car_pts, whl_pts = [], []
    n = int(60 * prog) + 1
    for i in range(n):
        u = i / 60
        x = gx0 + (gx1 - gx0) * u
        car_pts.append((x, gy0 + 30 + 120 * u))
        dive = max(0, u - 0.45)
        whl_pts.append((x, gy0 + 30 + 120 * u + 900 * dive * dive))
    if n > 1:
        line(d, car_pts, rgba(WHITE, ga), 7)
        line(d, [(x, min(y, gy1 - 4)) for x, y in whl_pts], rgba(ACC2, ga), 7)
    label(d, 280, gy0 + 110, "CAR SPEED", WHITE, ga, size=26, f=BLK)
    label(d, 280, gy0 + 220, "WHEEL SPEED", ACC2, ga, size=26, f=BLK)
    if prog > 0.62:
        k = ease_out((prog - 0.62) / 0.1)
        bx = gx0 + (gx1 - gx0) * 0.62
        ring(d, bx, gy0 + 30 + 120 * 0.62 + 900 * 0.0289, 34 * k + 1, rgba(RED, k), 6)
        chip(d, 620, 820, "ABOUT TO LOCK!", RED, k, size=32, tcol=WHITE)

def vis_abs_pulse(d, lt, t):
    dur = sdur("abs_pulse")
    a = ease_out(lt / 0.35)
    # brake disc + caliper (left)
    cx, cy = 260, 300
    spin = lt * 4
    circ(d, cx, cy, 190, rgba(STEEL, a))
    circ(d, cx, cy, 150, rgba((90, 100, 116), a))
    for k in range(10):
        aa = spin + k * 2 * math.pi / 10
        circ(d, cx + math.cos(aa) * 170, cy + math.sin(aa) * 170, 7, rgba(DARK, a))
    circ(d, cx, cy, 70, rgba(DARK, a))
    for k in range(5):
        aa = spin + k * 2 * math.pi / 5
        circ(d, cx + math.cos(aa) * 42, cy + math.sin(aa) * 42, 9, rgba(MUTED, a))
    # pressure cycle: 0..1 sawtooth-ish (slow visual cycle ~4 Hz, labelled up to 40/s)
    ph = (lt * 3.0) % 1.0
    press = 1 - ease_out(ph / 0.3) if ph < 0.3 else ease_inout((ph - 0.3) / 0.7)
    gap = 26 * (1 - press)
    # caliper (top of disc)
    d.rounded_rectangle(p(cx - 80, cy - 245, cx + 80, cy - 120), radius=24 * S, fill=rgba(ACC2, a))
    d.rectangle(p(cx - 60, cy - 160 + 0 - gap, cx + 60, cy - 140 - gap), fill=rgba(WHITE, a))
    label(d, cx, cy - 225, "CALIPER", BG, a, size=24, f=BLK)
    # valve + hydraulic line
    vx, vy = 640, 200
    d.rounded_rectangle(p(vx - 120, vy - 80, vx + 120, vy + 80), radius=18 * S, fill=rgba(PANEL, a), outline=rgba(ACC, a), width=3 * S)
    label(d, vx, vy - 60, "VALVE", ACC, a, size=26, f=BLK)
    open_ = press > 0.5
    chip(d, vx, vy - 10, "SQUEEZE" if open_ else "RELEASE", ACC if open_ else ACC2, a, size=28)
    line(d, [(vx - 120, vy + 30), (cx + 80, vy + 30), (cx + 80, cy - 190)], rgba(ACC2, a * (0.4 + 0.6 * press)), 12)
    # pressure graph builds
    gx0, gx1, gy0, gy1 = 90, 830, 560, 760
    ga = ease_out((lt - 0.5) / 0.4)
    line(d, [(gx0, gy0), (gx0, gy1), (gx1, gy1)], rgba(MUTED, ga), 4)
    label(d, gx0 + 120, gy0 - 40, "BRAKE PRESSURE", MUTED, ga, size=22, f=BLK)
    span = 2.2
    pts = []
    for i in range(121):
        u = i / 120
        tt = lt - span + u * span
        if tt < 0.5: continue
        q = (tt * 3.0) % 1.0
        pr = 1 - ease_out(q / 0.3) if q < 0.3 else ease_inout((q - 0.3) / 0.7)
        pts.append((gx0 + (gx1 - gx0) * u, gy1 - 20 - 150 * (0.35 + 0.65 * pr)))
    if len(pts) > 1: line(d, pts, rgba(ACC, ga), 7)
    # counter
    ca = ease_out((lt - 1.5) / 0.4)
    n = int(40 * ease_out((lt - 1.5) / max(dur - 2.5, 1)))
    d.rounded_rectangle(p(520, 330, 860, 490), radius=24 * S, fill=rgba(PANEL, ca))
    label(d, 690, 330, f"{n}", ACC, ca, size=110, f=BLK)
    label(d, 690, 450, "TIMES / SECOND (UP TO)", WHITE, ca, size=20, f=BLK)

def vis_abs_history(d, lt, t):
    dur = sdur("abs_history")
    a = ease_out(lt / 0.35)
    yr = int(1950 + 28 * ease_out((lt - 0.2) / 1.4))
    label(d, 450, 60, f"{yr}", ACC, a, size=170, f=BLK)
    # timeline
    tl_y = 320
    line(d, [(80, tl_y), (820, tl_y)], rgba(DARK, a), 8)
    for i, y in enumerate(range(1950, 1990, 10)):
        x = 80 + (y - 1950) / 40 * 740
        circ(d, x, tl_y, 10, rgba(MUTED, a))
        label(d, x, tl_y + 24, str(y), MUTED, a, size=22, f=BLK)
    mx = 80 + 28 / 40 * 740 * ease_out((lt - 0.2) / 1.4)
    circ(d, mx, tl_y, 20, rgba(ACC, a))
    # sedan rolls in
    ca = ease_out((lt - 1.2) / 0.6)
    car_side(d, 450 - 300 * (1 - ca), 560, 1.25, WHITE, ca)
    line(d, [(80, 615), (820, 615)], rgba(DARK, ca), 6)
    ka = ease_out((lt - 1.8) / 0.4)
    chip(d, 290, 690, "MERCEDES + BOSCH", ACC, ka, size=30)
    chip(d, 650, 690, "S-CLASS", WHITE, ka, size=30)
    label(d, 450, 790, "FIRST SERIES-PRODUCTION ABS · OPTIONAL EXTRA", MUTED, ease_out((lt - 2.2) / 0.4), size=24, f=BLK)

def vis_abs_driver(d, lt, t):
    dur = sdur("abs_driver")
    a = ease_out(lt / 0.35)
    split = dur * 0.58
    if lt < split:
        # brake pedal with pulsing
        px, py = 330, 420
        buzz = math.sin(lt * 60) * 6 * ease_out((lt - 0.3) / 0.3)
        line(d, [(px + 40, 120), (px + 40 + buzz * 0.3, py - 40)], rgba(STEEL, a), 22)
        d.rounded_rectangle(p(px - 60 + buzz, py - 50, px + 140 + buzz, py + 40), radius=20 * S, fill=rgba(WHITE, a))
        for k in range(4):
            line(d, [(px - 40 + k * 50 + buzz, py - 30), (px - 40 + k * 50 + buzz, py + 20)], rgba(MUTED, a), 6)
        waves(d, px + 160, py, t, ACC2, n=3, base=50, gap=40, alpha=a * 0.9, w=10)
        label(d, px + 40, py + 70, "BUZZ = ABS WORKING", ACC2, ease_out((lt - 0.4) / 0.4), size=28, f=BLK)
        # don't pump / press hard + steer
        ka = ease_out((lt - 1.0) / 0.4)
        d.rounded_rectangle(p(60, 620, 430, 820), radius=24 * S, fill=rgba(PANEL, ka))
        label(d, 245, 645, "PUMP", WHITE, ka, size=48, f=BLK)
        line(d, [(120, 650), (370, 790)], rgba(RED, ka), 12)
        line(d, [(370, 650), (120, 790)], rgba(RED, ka), 12)
        kb = ease_out((lt - 1.6) / 0.4)
        d.rounded_rectangle(p(470, 620, 840, 820), radius=24 * S, fill=rgba(PANEL, kb), outline=rgba(ACC, kb), width=4 * S)
        label(d, 655, 645, "PRESS HARD", ACC, kb, size=40, f=BLK)
        label(d, 655, 705, "+ STEER", ACC, kb, size=40, f=BLK)
        line(d, [(620, 790), (645, 805), (700, 770)], rgba(ACC, kb), 8)
    else:
        lt2 = lt - split
        k = ease_out(lt2 / 0.4)
        # motor block
        mx, my = 260, 330
        d.rounded_rectangle(p(mx - 150, my - 110, mx + 150, my + 110), radius=40 * S, fill=rgba(STEEL, k))
        for i in range(6):
            line(d, [(mx - 120 + i * 48, my - 110), (mx - 120 + i * 48, my + 110)], rgba(DARK, k), 6)
        circ(d, mx + 150, my, 36, rgba(MUTED, k))
        bolt(d, mx, my, 0.9, rgba(ACC, k))
        label(d, mx, my + 130, "MOTOR REGEN", WHITE, k, size=30, f=BLK)
        # regen gauge drops to ~0 when ABS kicks in
        drop = ease_inout((lt2 - 0.6) / 0.8)
        bx0, by0, bx1, by1 = 560, 160, 680, 520
        d.rounded_rectangle(p(bx0, by0, bx1, by1), radius=20 * S, fill=rgba(DARK, k))
        h = (by1 - by0 - 16) * (0.8 * (1 - drop) + 0.03)
        d.rounded_rectangle(p(bx0 + 8, by1 - 8 - h, bx1 - 8, by1 - 8), radius=14 * S, fill=rgba(ACC if drop < 0.5 else ACC2, k))
        label(d, 620, by1 + 20, "REGEN", MUTED, k, size=26, f=BLK)
        chip(d, 780, 300, "→ 0", ACC2, ease_out((lt2 - 1.2) / 0.3), size=40)
        chip(d, 450, 700, "ABS ACTIVE: FRICTION BRAKES TAKE OVER", ACC, ease_out((lt2 - 1.0) / 0.4), size=26)

def vis_abs_outro(d, lt, t):
    dur = sdur("abs_outro")
    if lt < dur * 0.62:
        a = ease_out(lt / 0.35)
        label(d, 450, 40, "LOOSE GRAVEL", ACC2, a, size=44, f=BLK)
        for k in range(60):
            x = 60 + (k * 131) % 780; y = 120 + (k * 53) % 40
            circ(d, x, y, 5 + (k % 3) * 2, rgba(MUTED, a * 0.6))
        # stopping distance bars
        rows = [("NO ABS", 0.78, WHITE, 0.6), ("ABS", 0.9, ACC, 1.0)]
        for i, (nm, v, col, dl) in enumerate(rows):
            y = 230 + i * 110
            ba = ease_out((lt - dl) / 0.7)
            label(d, 150, y + 6, nm, col, a, size=28, f=BLK)
            d.rounded_rectangle(p(250, y, 250 + 560 * max(v * ba, 0.02), y + 56), radius=28 * S, fill=rgba(col, a * 0.9))
        label(d, 530, 450, "STOPPING DISTANCE (ILLUSTRATIVE)", MUTED, a, size=22, f=BLK)
        # but steering
        sa = ease_out((lt - 1.8) / 0.4)
        d.rounded_rectangle(p(100, 540, 800, 800), radius=28 * S, fill=rgba(PANEL, sa))
        label(d, 450, 560, "CAN YOU STILL STEER?", WHITE, sa, size=34, f=BLK)
        label(d, 270, 640, "NO ABS", MUTED, sa, size=26, f=BLK)
        label(d, 270, 690, "NO", RED, sa, size=56, f=BLK)
        label(d, 630, 640, "ABS", MUTED, sa, size=26, f=BLK)
        label(d, 630, 690, "YES", ACC, sa, size=56, f=BLK)
        steering_wheel(d, 450, 715, 40, math.sin(lt * 3) * 0.7, ACC, sa)
    else:
        k = back_out((lt - dur * 0.62) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.62 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"abs_hook": vis_abs_hook, "abs_lock": vis_abs_lock, "abs_sensors": vis_abs_sensors, "abs_pulse": vis_abs_pulse,
            "abs_history": vis_abs_history, "abs_driver": vis_abs_driver, "abs_outro": vis_abs_outro})
