# Episode visuals: What would happen if every car in a city were electric?
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
SMOKE = (150, 156, 166)
BLK = "InterDisplay-Black.otf"
BLD = "InterDisplay-Bold.otf"
SEMI = "Inter-SemiBold.otf"

def sdur(name):
    for s in scenes:
        if s["visual"] == name:
            return s["vis_end"] - s["start"]
    return 4.0

def poly(d, pts, col):
    d.polygon(p(*[v for xy in pts for v in xy]), fill=col)

def bolt(d, bx, by, bs, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(bx + xx * bs, by + yy * bs) for xx, yy in pts], col)

def panel(d, x0, y0, x1, y1, a=1.0, outline=None):
    d.rounded_rectangle(p(x0 + 6, y0 + 10, x1 + 6, y1 + 10), radius=24 * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=24 * S, fill=rgba(PANEL, 0.94 * a),
                        outline=rgba(outline or DARK, a), width=int(4 * S))

def label(d, x, y, s, col, a, size=28, f=SEMI):
    text_c(d, x, y, s, FL(f, max(1, int(size))), rgba(col, a))

def label_l(d, x, y, s, col, a, size=28, f=SEMI):
    d.text((x * S, y * S), s, font=FL(f, max(1, int(size))), fill=rgba(col, a))

def mini_car(d, x, y, sc, col, a):
    """Small side-view car; (x, y) = road contact centre."""
    body = [(-60, -14), (-60, -34), (-30, -40), (-14, -62), (26, -62), (44, -40), (62, -34), (62, -14)]
    poly(d, [(x + px * sc, y + py * sc) for px, py in body], rgba(col, a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in [(-10, -57), (6, -57), (6, -42), (-24, -42)]], rgba(BG, a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in [(12, -57), (24, -57), (36, -42), (12, -42)]], rgba(BG, a))
    for wx in (-34, 36):
        r = 13 * sc
        d.ellipse(p(x + wx * sc - r, y - 14 * sc - r, x + wx * sc + r, y - 14 * sc + r), fill=rgba((30, 36, 46), a))
        r2 = 6 * sc
        d.ellipse(p(x + wx * sc - r2, y - 14 * sc - r2, x + wx * sc + r2, y - 14 * sc + r2), fill=rgba(STEEL, a))

def puff(d, x, y, r, a):
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=rgba(SMOKE, a))

def skyline(d, a, base=470):
    bl = [(60, 210), (130, 300), (210, 170), (280, 360), (370, 240), (450, 410), (540, 260), (620, 330), (700, 190), (780, 280), (840, 150)]
    for i, (x, h) in enumerate(bl):
        w = 66
        d.rectangle(p(x - w / 2, base - h, x + w / 2, base), fill=rgba((24, 31, 42), a))
        d.rectangle(p(x - w / 2, base - h, x + w / 2, base - h + 6), fill=rgba(DARK, a))
        for wy in range(int(base - h + 26), base - 20, 34):
            for wx in (-16, 0, 16):
                on = (i * 7 + wy // 34 + wx) % 3 == 0
                d.rectangle(p(x + wx - 4, wy, x + wx + 4, wy + 12), fill=rgba(ACC if on else (44, 54, 68), a * (0.55 if on else 1)))

# ---------- scene 1: city flips to electric ----------
def vis_ec_hook(d, lt, t):
    a = ease_out(lt / 0.35)
    skyline(d, a)
    # road
    d.rectangle(p(0, 480, 900, 640), fill=rgba((18, 23, 31), a))
    for k in range(10):
        x = (k * 110 - (t * 160) % 110)
        d.rectangle(p(x, 556, x + 55, 564), fill=rgba(MUTED, a * 0.6))
    n = 6
    flip_t = [0.9 + i * 0.42 for i in range(n)]
    for i in range(n):
        lane = 530 if i % 2 == 0 else 615
        x = (i * 170 + t * (70 if i % 2 == 0 else -60)) % 1020 - 60
        k = ease_out((lt - flip_t[i]) / 0.3)
        col = tuple(int(ACC2[c] * (1 - k) + ACC[c] * k) for c in range(3))
        mini_car(d, x, lane, 0.95, col, a)
        # exhaust puffs before the flip
        if k < 1:
            dirn = -1 if i % 2 == 0 else 1
            for j in range(3):
                ph = (t * 1.5 + j / 3 + i * 0.13) % 1
                puff(d, x + dirn * (64 + ph * 60), lane - 22 - ph * 30, 7 + ph * 12, a * (1 - k) * 0.55 * (1 - ph))
        else:
            bolt(d, x + 6, lane - 92, 0.22, rgba(ACC, a * (0.7 + 0.3 * math.sin(t * 6 + i))))
    # counter
    elec = sum(ease_out((lt - ft) / 0.3) for ft in flip_t)
    pct = int(round(100 * elec / n))
    panel(d, 230, 680, 670, 850, a, outline=ACC if pct == 100 else DARK)
    label(d, 450, 690, f"{pct}%", ACC if pct == 100 else WHITE, a, 96, BLK)
    label(d, 450, 805, "OF CARS ELECTRIC", MUTED, a, 28, BLD)
    q = back_out((lt - 3.8) / 0.5)
    if q > 0:
        for i, (s, c) in enumerate([("3 CHANGES", ACC), ("1 SURPRISE", ACC2)]):
            x = 245 + i * 410
            d.rounded_rectangle(p(x - 175 * clamp(q), 40, x + 175 * clamp(q), 108), radius=34 * S, fill=rgba(c, clamp(q)))
            label(d, x, 52, s, BG, clamp(q), 38 * clamp(q) + 1, BLK)

# ---------- scene 2: noise vs speed ----------
def vis_ec_noise(d, lt, t):
    a = ease_out(lt / 0.35)
    x0, x1, y0, y1 = 140, 820, 110, 600
    panel(d, 60, 40, 860, 720, a)
    # axes
    d.line(p(x0, y1, x1, y1), fill=rgba(MUTED, a), width=int(4 * S))
    d.line(p(x0, y1, x0, y0), fill=rgba(MUTED, a), width=int(4 * S))
    label_l(d, 92, 70, "LOUDER", MUTED, a, 24, BLD)
    label(d, 760, 618, "SPEED →", MUTED, a, 26, BLD)
    # 35 mph marker at 45% of axis
    mx = x0 + (x1 - x0) * 0.42
    def gas(u):   # engine + tire
        return 0.42 + 0.50 * u ** 0.8
    def evc(u):
        g = gas(u)
        k = ease_inout((u - 0.15) / 0.7)
        return (0.06 + 0.45 * u) * (1 - k) + (g - 0.025) * k
    grow = ease_inout((lt - 0.4) / 2.6)
    # shaded quiet zone
    z = ease_out((lt - 2.8) / 0.5)
    if z > 0:
        pts = []
        N = 40
        for i in range(N + 1):
            u = 0.42 * i / N
            pts.append((x0 + (x1 - x0) * u, y1 - (y1 - y0) * gas(u)))
        for i in range(N, -1, -1):
            u = 0.42 * i / N
            pts.append((x0 + (x1 - x0) * u, y1 - (y1 - y0) * evc(u)))
        poly(d, pts, rgba(ACC, 0.18 * z * a))
        label(d, x0 + (mx - x0) / 2, y1 - 165, "QUIETER", ACC, z * a, 34, BLK)
    for fn, col, w in ((gas, ACC2, 9), (evc, ACC, 9)):
        N = 60
        pts = []
        for i in range(int(N * grow) + 1):
            u = i / N
            pts.append((x0 + (x1 - x0) * u, y1 - (y1 - y0) * fn(u)))
        if len(pts) > 1:
            d.line(p(*[v for xy in pts for v in xy]), fill=rgba(col, a), width=int(w * S), joint="curve")
            ex, ey = pts[-1]
            d.ellipse(p(ex - 12, ey - 12, ex + 12, ey + 12), fill=rgba(col, a))
    # marker
    m = ease_out((lt - 2.5) / 0.4)
    if m > 0:
        for yy in range(y0 + 30, y1, 28):
            d.line(p(mx, yy, mx, yy + 14), fill=rgba(WHITE, m * a * 0.7), width=int(3 * S))
        label(d, mx, y1 + 52, "35 MPH", WHITE, m * a, 28, BLK)
    h = ease_out((lt - 5.0) / 0.5)
    if h > 0:
        label(d, x0 + (x1 - x0) * 0.78, y1 - 150, "TIRE ROAR", WHITE, h * a, 34, BLK)
        label(d, x0 + (x1 - x0) * 0.78, y1 - 106, "≈ same for both", MUTED, h * a, 26)
    # legend
    for i, (s, c) in enumerate([("GAS CAR", ACC2), ("EV", ACC)]):
        lx = 250 + i * 330
        d.rounded_rectangle(p(lx - 22, 757, lx + 22, 771), radius=6 * S, fill=rgba(c, a))
        label_l(d, lx + 36, 745, s, WHITE, a, 30, BLD)

# ---------- scene 3: tailpipe fumes vanish ----------
def vis_ec_air(d, lt, t):
    a = ease_out(lt / 0.35)
    gone = ease_inout((lt - 0.9) / 1.4)
    # rear of a car, big
    cx, gy = 560, 470
    body = [(-260, -40), (-260, -150), (-200, -230), (40, -240), (120, -160), (200, -140), (230, -40)]
    poly(d, [(cx + x, gy + y) for x, y in body], rgba(WHITE, a))
    poly(d, [(cx + x, gy + y) for x, y in [(-180, -215), (20, -222), (85, -160), (-225, -160)]], rgba(BG, a))
    for wx in (-160, 120):
        tire(d, cx + wx, gy - 30, 62, t * 4, STEEL, a)
    # tailpipe
    d.rounded_rectangle(p(cx - 300, gy - 70, cx - 250, gy - 48), radius=6 * S, fill=rgba(STEEL, a))
    for j in range(7):
        ph = (t * 0.9 + j / 7) % 1
        px = cx - 310 - ph * 230
        py = gy - 60 - ph * 160 + math.sin(t * 2 + j) * 10
        puff(d, px, py, 14 + ph * 42, a * 0.55 * (1 - ph) * (1 - gone))
    # person on sidewalk
    person(d, 150, 720, 0.85, MUTED, a, t * 0.3)
    # breath arcs (clean air)
    if gone > 0.6:
        k = ease_out((lt - 2.0) / 0.4)
        for i in range(3):
            arc(d, 150, 560, 60 + i * 30, -60, 30, rgba(ACC, k * (1 - i * 0.25)), 6)
    k = back_out((lt - 1.7) / 0.5)
    if k > 0:
        panel(d, 330, 600, 830, 800, clamp(k), outline=ACC)
        label(d, 580, 612, "TAILPIPE", MUTED, clamp(k), 30, BLD)
        label(d, 580, 655, "ZERO", ACC, clamp(k), 100 * clamp(k) + 1, BLK)

# ---------- scene 4: tire + brake dust, OECD bars ----------
def vis_ec_dust(d, lt, t):
    a = ease_out(lt / 0.35)
    dur = sdur("ec_dust")
    cut = 4.2
    if lt < cut:
        fa = a * (1 - ease_inout((lt - cut + 0.4) / 0.4))
        # big wheel with brake disc
        cx, cy, r = 450, 330, 210
        d.rectangle(p(40, cy + r, 860, cy + r + 30), fill=rgba(DARK, fa))
        tire(d, cx, cy, r, t * 2.2, STEEL, fa)
        # brake caliper
        d.rounded_rectangle(p(cx + 70, cy - 100, cx + 130, cy + 10), radius=14 * S, fill=rgba(ACC2, fa))
        # particles shed from contact patch and caliper
        rng_seed = 7
        for j in range(26):
            ph = (t * 0.7 + j * 0.137) % 1
            ang = (j * 1.7) % 1.0
            sx = cx - 40 + (j % 5) * 20
            px = sx - ph * (180 + ang * 260)
            py = cy + r - 6 - ph * (60 + ang * 160) + ph * ph * 120
            rr = 3 + (j % 3) * 2
            d.ellipse(p(px - rr, py - rr, px + rr, py + rr), fill=rgba(SMOKE, fa * (1 - ph) * 0.9))
        for j in range(12):
            ph = (t * 0.9 + j * 0.21) % 1
            px = cx + 100 + ph * 220
            py = cy - 40 + ph * 140 + math.sin(j) * 30 * ph
            rr = 3 + (j % 2) * 2
            d.ellipse(p(px - rr, py - rr, px + rr, py + rr), fill=rgba(ACC2, fa * (1 - ph) * 0.8))
        k = ease_out((lt - 0.8) / 0.4)
        label(d, 200, 600, "TIRE DUST", WHITE, fa * k, 36, BLK)
        k2 = ease_out((lt - 1.3) / 0.4)
        label(d, 690, 600, "BRAKE DUST", ACC2, fa * k2, 36, BLK)
        k3 = ease_out((lt - 2.0) / 0.4)
        label(d, 450, 700, "+ ROAD WEAR", MUTED, fa * k3, 30, BLD)
    else:
        lt2 = lt - cut
        b = ease_out(lt2 / 0.4)
        label(d, 450, 40, "NON-EXHAUST PM2.5", WHITE, b, 40, BLK)
        label(d, 450, 95, "vs. a gas car in the same class · OECD 2020", MUTED, b, 24)
        bars = [("LIGHT EV", 0.88, ACC, "−11 to 13%", 1.2), ("GAS CAR", 1.0, ACC2, "baseline", 0.3), ("HEAVY EV", 1.055, WHITE, "+3 to 8%", 2.4)]
        base_y, top_scale = 720, 470
        for i, (nm, v, c, txt, delay) in enumerate(bars):
            x = 190 + i * 260
            g = ease_inout((lt2 - delay * 0.8) / 0.9)
            h = top_scale * v * g
            if h < 12:
                label(d, x, base_y + 20, nm, WHITE, b, 30, BLK)
                continue
            d.rounded_rectangle(p(x - 75 + 6, base_y - h + 8, x + 75 + 6, base_y), radius=14 * S, fill=rgba((0, 0, 0), 0.3 * g))
            d.rounded_rectangle(p(x - 75, base_y - h, x + 75, base_y), radius=14 * S, fill=rgba(c, b * (0.85 if c != WHITE else 0.9)))
            label(d, x, base_y + 20, nm, WHITE, b, 30, BLK)
            if g > 0.6:
                tk = ease_out((g - 0.6) / 0.4)
                label(d, x, base_y - h - 52, txt, c, tk, 30, BLK)
        # baseline guide
        gl = ease_out((lt2 - 1.0) / 0.5)
        yb = base_y - top_scale
        for xx in range(80, 830, 34):
            d.line(p(xx, yb, xx + 16, yb), fill=rgba(ACC2, gl * 0.6), width=int(3 * S))
        d.line(p(60, base_y, 840, base_y), fill=rgba(MUTED, b), width=int(4 * S))

# ---------- scene 5: grid demand ----------
def vis_ec_grid(d, lt, t):
    a = ease_out(lt / 0.35)
    # pylon icon
    px, py = 450, 140
    for s_ in (-1, 1):
        d.line(p(px, py - 110, px + s_ * 70, py + 90), fill=rgba(MUTED, a), width=int(7 * S))
    for yy, w in ((-60, 70), (-20, 95)):
        d.line(p(px - w, py + yy, px + w, py + yy), fill=rgba(MUTED, a), width=int(7 * S))
    for xx in range(-50, 60, 50):
        d.line(p(px + xx - 18, py - 30, px + xx + 18, py + 10), fill=rgba(DARK, a), width=int(4 * S))
    # wires with flowing dots
    for side in (-1, 1):
        for w_y in (-60, -20):
            x_a = px + side * (70 if w_y == -60 else 95)
            x_b = 450 + side * 450
            d.line(p(x_a, py + w_y, x_b, py + w_y + 40), fill=rgba(DARK, a), width=int(3 * S))
            for j in range(4):
                ph = (t * 0.6 + j / 4) % 1
                if side < 0: ph = 1 - ph
                xx = x_a + (x_b - x_a) * ph
                yy = py + w_y + 40 * ph
                d.ellipse(p(xx - 6, yy - 6, xx + 6, yy + 6), fill=rgba(ACC, a))
    # stacked bar: today's generation + EV share
    bx0, bx1, by, bh = 90, 810, 340, 110
    w_today = (bx1 - bx0) / 1.22
    g1 = ease_inout((lt - 0.4) / 1.0)
    d.rounded_rectangle(p(bx0, by, bx0 + max(30, w_today * g1), by + bh), radius=16 * S, fill=rgba(STEEL, a))
    label(d, bx0 + w_today / 2, by + 34, "US POWER TODAY", WHITE, a * g1, 32, BLK)
    g2 = ease_out((lt - 1.6) / 0.9)
    if g2 > 0:
        xe = bx0 + w_today
        d.rounded_rectangle(p(xe + 6, by, xe + 6 + (bx1 - xe - 6) * g2, by + bh), radius=16 * S, fill=rgba(ACC, a * (0.85 + 0.15 * math.sin(t * 5))))
        n = int(round(22 * g2))
        label(d, (xe + bx1) / 2 + 3, by + bh + 22, f"+{n}%", ACC, a, 64, BLK)
        label(d, (xe + bx1) / 2 + 3, by + bh + 100, "ALL CARS EV", MUTED, a * g2, 24, BLD)
    # timeline 2025 -> 2050 staircase
    k = ease_out((lt - 4.6) / 0.5)
    if k > 0:
        tx0, tx1, ty = 110, 790, 820
        d.line(p(tx0, ty, tx1, ty), fill=rgba(MUTED, k), width=int(4 * S))
        label(d, tx0, ty + 14, "2025", MUTED, k, 26, BLD)
        label(d, tx1, ty + 14, "2050", MUTED, k, 26, BLD)
        steps = 25
        prog = ease_inout((lt - 5.0) / 3.0) * steps
        sw = (tx1 - tx0) / steps
        for i in range(int(prog) + 1):
            if i >= steps: break
            hh = 12 + i * 7.2
            fk = clamp(prog - i)
            d.rectangle(p(tx0 + i * sw + 2, ty - hh * fk, tx0 + (i + 1) * sw - 2, ty), fill=rgba(ACC, k * (0.5 + 0.5 * i / steps)))
        q = back_out((lt - 7.0) / 0.5)
        if q > 0:
            d.rounded_rectangle(p(160, 560, 520, 640), radius=40 * S, fill=rgba(WHITE, clamp(q)))
            label(d, 340, 576, "≈ 1% PER YEAR", BG, clamp(q), 40 * clamp(q) + 1, BLK)

# ---------- outro ----------
def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL(BLK, max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

def vis_ec_outro(d, lt, t):
    dur = sdur("ec_outro")
    cut = dur * 0.55
    if lt < cut:
        a = 1 - ease_inout((lt - cut + 0.3) / 0.3)
        rows = [("TAILPIPE", "FIXED", ACC), ("TIRES & BRAKES", "NOT YET", ACC2)]
        for i, (nm, st, c) in enumerate(rows):
            k = ease_out((lt - 0.2 - i * 0.6) / 0.4)
            y = 120 + i * 170
            panel(d, 110, y, 790, y + 135, a * k, outline=c)
            label_l(d, 150, y + 42, nm, WHITE, a * k, 42, BLK)
            d.rounded_rectangle(p(560, y + 34, 760, y + 100), radius=33 * S, fill=rgba(c, a * k))
            label(d, 660, y + 44, st, BG, a * k, 30, BLK)
        q = back_out((lt - 1.5) / 0.5)
        if q > 0:
            label(d, 450, 520, "NEXT GOAL:", MUTED, a * clamp(q), 36, BLD)
            label(d, 450, 580, "LIGHTER CARS?", ACC, a * clamp(q), 72 * clamp(q) + 1, BLK)
    else:
        end_card(d, lt, cut)

VIS.update({"ec_hook": vis_ec_hook, "ec_noise": vis_ec_noise, "ec_air": vis_ec_air,
            "ec_dust": vis_ec_dust, "ec_grid": vis_ec_grid, "ec_outro": vis_ec_outro})
