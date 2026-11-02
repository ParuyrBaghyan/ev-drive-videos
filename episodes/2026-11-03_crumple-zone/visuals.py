# Episode visuals: crumple zones — why cars are designed to crush.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
HOLE = (8, 10, 14)
CYAN = (90, 200, 255)
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

def wheel(d, x, y, r, a):
    circ(d, x, y, r, rgba(HOLE, a)); circ(d, x, y, r * 0.72, rgba(STEEL, a)); circ(d, x, y, r * 0.28, rgba(WHITE, a))

def crash_car(d, x, y, sc, crush, a, show_zones=0.0, rear_crush=0.0):
    """Side-view car facing right, ground at y, rear end at x.
    crush (0..1) folds the front section like an accordion; the cabin never changes."""
    R = 150 * sc * (1 - 0.55 * rear_crush)       # rear section length
    C = 300 * sc                                # cabin (rigid cell)
    Fn = 170 * sc * (1 - 0.6 * crush)           # front section length
    x0 = x; x1 = x0 + R; x2 = x1 + C; x3 = x2 + Fn
    top = y - 70 * sc; roof = y - 175 * sc; sill = y - 20 * sc
    # shadow
    d.rounded_rectangle(p(x0 + 10, top + 14, x3 + 10, sill + 14), radius=14 * S, fill=rgba((0, 0, 0), 0.35 * a))
    # rear section
    rc = ACC2 if show_zones > 0 else WHITE
    mix = lambda c1, c2, k: tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))
    zc = mix(WHITE, ACC2, show_zones)
    if rear_crush > 0:
        n = 5; pts = [(x0, top)]
        for i in range(1, n + 1):
            pts.append((x0 + R * i / n, top + (14 * sc if i % 2 else 0) * rear_crush))
        pts += [(x1, sill)]
        for i in range(n, -1, -1):
            pts.append((x0 + R * i / n, sill - (14 * sc if i % 2 else 0) * rear_crush))
        poly(d, pts, rgba(zc, a))
    else:
        d.rounded_rectangle(p(x0, top, x1 + 4, sill), radius=10 * S, fill=rgba(zc, a))
    # cabin: rigid cell
    cc = mix(WHITE, (225, 230, 236), show_zones)
    poly(d, [(x1, sill), (x1, top), (x1 + 40 * sc, roof), (x2 - 70 * sc, roof), (x2, top), (x2, sill)], rgba(cc, a))
    poly(d, [(x1 + 50 * sc, top - 8 * sc), (x1 + 75 * sc, roof + 14 * sc), (x1 + 140 * sc, roof + 14 * sc), (x1 + 140 * sc, top - 8 * sc)], rgba(BG, a))
    poly(d, [(x1 + 158 * sc, top - 8 * sc), (x1 + 158 * sc, roof + 14 * sc), (x2 - 78 * sc, roof + 14 * sc), (x2 - 30 * sc, top - 8 * sc)], rgba(BG, a))
    if show_zones > 0:
        w = 7
        line(d, [(x1, sill), (x1, top), (x1 + 40 * sc, roof), (x2 - 70 * sc, roof), (x2, top), (x2, sill), (x1, sill)], rgba(ACC, a * show_zones), w)
        line(d, [(x1 + 147 * sc, roof), (x1 + 147 * sc, sill)], rgba(ACC, a * show_zones), w)
    # front section: accordion folds
    n = 6
    amp = 22 * sc * crush
    up = [(x2, top)]
    for i in range(1, n + 1):
        up.append((x2 + Fn * i / n, top + 10 * sc + (amp if i % 2 else -amp * 0.4)))
    lo = []
    for i in range(n, 0, -1):
        lo.append((x2 + Fn * i / n, sill - (amp if i % 2 else -amp * 0.3)))
    lo.append((x2, sill))
    poly(d, up + lo, rgba(zc, a))
    if crush > 0.05:
        for i in range(1, n):
            xx = x2 + Fn * i / n
            line(d, [(xx, top + 14 * sc), (xx, sill - 6 * sc)], rgba(BG, a * crush * 0.8), 4)
    # headlight
    if crush < 0.5:
        line(d, [(x3 - 22 * sc, top + 22 * sc), (x3 - 4 * sc, top + 26 * sc)], rgba(ACC, a * (1 - crush * 2)), 7)
    # wheels
    wheel(d, x1 - 20 * sc, y - 12 * sc, 46 * sc, a)
    wheel(d, x2 + min(60 * sc, Fn * 0.45), y - 12 * sc, 46 * sc, a)
    return x3

# ---------- scenes ----------
def vis_cz_hook(d, lt, t):
    a = ease_out(lt / 0.3)
    gy = 560; wall = 760
    d.line(p(20, gy, 880, gy), fill=rgba(DARK, a), width=6 * S)
    # wall
    d.rectangle(p(wall, 200, wall + 70, gy), fill=rgba(STEEL, a))
    for r in range(8):
        yy = 200 + r * 45
        d.line(p(wall, yy, wall + 70, yy), fill=rgba(DARK, a), width=4 * S)
        off = 35 if r % 2 else 0
        d.line(p(wall + off, yy, wall + off, yy + 45), fill=rgba(DARK, a), width=4 * S)
    # car drives in, hits at t_hit, front folds
    t_hit = 0.9
    sc = 0.95
    full_len = (150 + 300 + 170) * sc
    if lt < t_hit:
        xr = -650 + (wall - full_len + 650) * (lt / t_hit) ** 1.6
        crush = 0.0
    else:
        crush = ease_out((lt - t_hit) / 0.35)
        xr = wall - full_len + 170 * sc * 0.6 * crush
    if lt < t_hit:
        for i in range(3):
            line(d, [(xr - 40 - i * 50, gy - 100 + i * 30), (xr - 140 - i * 50, gy - 100 + i * 30)], rgba(MUTED, a * 0.6), 6)
    crash_car(d, xr, gy, sc, crush, a)
    if lt >= t_hit:
        fl = 1 - ease_out((lt - t_hit) / 0.6)
        ix, iy = wall - 20, gy - 110
        for k in range(7):
            ang = -math.pi / 2 + (k - 3) * 0.33 - 0.25
            r0, r1 = 25, 25 + 110 * ease_out((lt - t_hit) / 0.4)
            line(d, [(ix + math.cos(ang) * r0, iy + math.sin(ang) * r0), (ix + math.cos(ang) * r1, iy + math.sin(ang) * r1)], rgba(ACC2, fl), 7)
        za = ease_out((lt - t_hit - 0.5) / 0.4)
        chip(d, 450, 120, "BUILT TO CRUSH", ACC2, za, size=48)
        label(d, xr + 225 * sc, 600, "CABIN STAYS INTACT", ACC, ease_out((lt - t_hit - 0.9) / 0.4), size=34, f=BLK)

def vis_cz_physics(d, lt, t):
    dur = sdur("cz_physics")
    a = ease_out(lt / 0.4)
    # axes: force vs time
    ox, oy, xw, yh = 120, 600, 700, 430
    line(d, [(ox, oy - yh), (ox, oy), (ox + xw, oy)], rgba(MUTED, a), 5)
    label(d, ox + xw - 40, oy + 18, "TIME", MUTED, a, size=26, f=BLD)
    label(d, ox - 10, oy - yh - 44, "FORCE ON YOU", MUTED, a, size=26, f=BLD)
    # pulse 1: short and tall (no crumple)
    k1 = ease_out((lt - 0.4) / 0.9)
    w1, h1 = 120, 380
    def pulse(w, h, k, col, alpha):
        pts = []
        for i in range(41):
            u = i / 40
            xx = ox + 20 + w * u
            yy = oy - h * math.sin(math.pi * u) ** 1.5 * k
            pts.append((xx, yy))
        poly(d, pts + [(ox + 20 + w, oy), (ox + 20, oy)], rgba(col, alpha * 0.28))
        line(d, pts, rgba(col, alpha), 7)
    pulse(w1, h1, k1, RED, a)
    label(d, ox + 20 + w1 / 2, oy - h1 * k1 - 50, "RIGID", RED, ease_out((lt - 1.0) / 0.4), size=30, f=BLK)
    # pulse 2: twice as long, about half the height
    p2 = dur * 0.45
    k2 = ease_out((lt - p2) / 1.0)
    if k2 > 0:
        pulse(w1 * 2 * (0.5 + 0.5 * k2), h1 / 2, k2, ACC, a)
        label(d, ox + 20 + w1, oy - h1 / 2 * k2 - 50, "CRUMPLES", ACC, ease_out((lt - p2 - 0.5) / 0.4), size=30, f=BLK)
    # time bracket labels
    ta = ease_out((lt - p2 - 0.8) / 0.4)
    if ta > 0:
        line(d, [(ox + 20, oy + 70), (ox + 20 + w1 * 2, oy + 70)], rgba(ACC, ta), 5)
        line(d, [(ox + 20, oy + 58), (ox + 20, oy + 82)], rgba(ACC, ta), 5)
        line(d, [(ox + 20 + w1 * 2, oy + 58), (ox + 20 + w1 * 2, oy + 82)], rgba(ACC, ta), 5)
        label(d, ox + 20 + w1, oy + 92, "×2 TIME", ACC, ta, size=30, f=BLK)
    # right-hand formula card
    fa = ease_out((lt - p2 - 1.2) / 0.4)
    if fa > 0:
        cx = 640
        d.rounded_rectangle(p(cx - 140, 170, cx + 140, 400), radius=24 * S, fill=rgba(PANEL, fa), outline=rgba(DARK, fa), width=int(4 * S))
        label(d, cx, 195, "×2 TIME", WHITE, fa, size=46, f=BLK)
        label(d, cx, 262, "↓", MUTED, fa, size=40, f=BLK)
        label(d, cx, 318, "≈ ½ FORCE", ACC, fa, size=46, f=BLK)
    label(d, 450, 740, "same speed lost · spread over more time", MUTED, ease_out((lt - 1.4) / 0.4), size=28, f=SEMI)

def vis_cz_patent(d, lt, t):
    a = ease_out(lt / 0.4)
    zk = ease_out((lt - 0.8) / 0.6)
    sc = 1.15
    total = (150 + 300 + 170) * sc
    x0 = 450 - total / 2
    gy = 470
    d.line(p(30, gy + 10, 870, gy + 10), fill=rgba(DARK, a), width=5 * S)
    crash_car(d, x0, gy, sc, 0.0, a, show_zones=zk)
    # zone brackets & labels
    za = ease_out((lt - 1.2) / 0.4)
    def bracket(xa, xb, col, txt, al, yb=530):
        if al <= 0: return
        line(d, [(xa + 6, yb), (xb - 6, yb)], rgba(col, al), 6)
        line(d, [(xa + 6, yb - 14), (xa + 6, yb + 14)], rgba(col, al), 6)
        line(d, [(xb - 6, yb - 14), (xb - 6, yb + 14)], rgba(col, al), 6)
        label(d, (xa + xb) / 2, yb + 22, txt, col, al, size=26, f=BLK)
    bracket(x0, x0 + 150 * sc, ACC2, "CRUSH", za)
    bracket(x0 + 150 * sc, x0 + 450 * sc, ACC, "RIGID CAGE", ease_out((lt - 1.6) / 0.4))
    bracket(x0 + 450 * sc, x0 + total, ACC2, "CRUSH", ease_out((lt - 2.0) / 0.4))
    # patent document
    pa = back_out((lt - 0.2) / 0.5)
    s = clamp(pa)
    px, py = 450, 70
    d.rounded_rectangle(p(px - 190, py, px + 190, py + 120), radius=16 * S, fill=rgba(PANEL, s), outline=rgba(STEEL, s), width=int(4 * S))
    yr = int(round(1900 + 52 * ease_out((lt - 0.3) / 1.2)))
    label(d, px, py + 12, "PATENT", MUTED, s, size=26, f=BLD)
    label(d, px, py + 46, f"{yr}", ACC, s, size=56, f=BLK)
    label(d, 450, 680, "BÉLA BARÉNYI · MERCEDES-BENZ", MUTED, ease_out((lt - 2.4) / 0.4), size=28, f=BLD)
    label(d, 450, 728, "patent no. 854157", MUTED, ease_out((lt - 2.6) / 0.4), size=24, f=SEMI)

def fintail(d, x, y, sc, a):
    """Generic late-50s saloon silhouette with small rear fins; rear at x, facing right."""
    body = [(0, -20), (0, -78), (30, -84), (40, -96), (60, -84), (150, -84), (195, -140), (330, -142), (380, -86), (520, -80), (540, -60), (540, -20)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in body], rgba(WHITE, a))
    poly(d, [(x + 210 * sc, y - 92 * sc), (x + 222 * sc, y - 130 * sc), (x + 265 * sc, y - 130 * sc), (x + 265 * sc, y - 92 * sc)], rgba(BG, a))
    poly(d, [(x + 278 * sc, y - 92 * sc), (x + 278 * sc, y - 130 * sc), (x + 322 * sc, y - 130 * sc), (x + 355 * sc, y - 92 * sc)], rgba(BG, a))
    line(d, [(x + 10 * sc, y - 60 * sc), (x + 520 * sc, y - 58 * sc)], rgba(STEEL, a), 3)
    for wx in (110, 430):
        wheel(d, x + wx * sc, y - 12 * sc, 40 * sc, a)

def vis_cz_fintail(d, lt, t):
    a = ease_out(lt / 0.35)
    # timeline
    ty = 170
    xs = [(150, "1937", "first idea"), (450, "1952", "patent"), (750, "1959", "FINTAIL")]
    prog = ease_inout((lt - 0.2) / 1.2)
    line(d, [(150, ty), (750, ty)], rgba(DARK, a), 8)
    line(d, [(150, ty), (150 + 600 * prog, ty)], rgba(ACC, a), 8)
    for i, (x, yr, nm) in enumerate(xs):
        on = prog >= i / 2 - 0.01
        k = back_out((lt - 0.2 - i * 0.6) / 0.4) if on else 0
        circ(d, x, ty, 22 * max(k, 0.4), rgba(ACC if on else DARK, a))
        label(d, x, ty - 82, yr, WHITE if i < 2 else ACC, clamp(k) * a, size=44, f=BLK)
        label(d, x, ty + 36, nm, MUTED if i < 2 else ACC, clamp(k) * a, size=26, f=BLD)
    # the car rolls in
    ck = ease_out((lt - 1.0) / 0.9)
    gy = 560
    d.line(p(30, gy, 870, gy), fill=rgba(DARK, a), width=5 * S)
    fintail(d, -600 + 780 * ck, gy, 1.1, a * clamp(ck * 2))
    chip(d, 450, 650, "FIRST MERCEDES WITH CRUMPLE ZONES", ACC, ease_out((lt - 1.8) / 0.4), size=30)

def vis_cz_ev(d, lt, t):
    dur = sdur("cz_ev")
    a = ease_out(lt / 0.4)
    def cut(y, ev, al):
        # simple cutaway outline of a front end: firewall at x=520, bumper at x=840
        d.rounded_rectangle(p(160, y - 120, 860, y), radius=26 * S, outline=rgba(STEEL, al), width=int(5 * S))
        line(d, [(520, y - 120), (520, y)], rgba(WHITE, al), 8)
        label(d, 340, y - 76, "CABIN", MUTED, al, size=32, f=BLD)
        if not ev:
            d.rounded_rectangle(p(560, y - 100, 700, y - 18), radius=10 * S, fill=rgba(STEEL, al))
            for i in range(4):
                circ(d, 590 + i * 30, y - 72, 9, rgba(DARK, al))
            label(d, 630, y - 50, "ENGINE", WHITE, al, size=26, f=BLK)
        else:
            d.rounded_rectangle(p(560, y - 100, 700, y - 40), radius=10 * S, outline=rgba(MUTED, al), width=int(3 * S))
            label(d, 630, y - 90, "FRUNK", MUTED, al, size=26, f=BLD)
            circ(d, 610, y - 22, 14, rgba(ACC, al)); circ(d, 650, y - 22, 14, rgba(ACC, al))
            label(d, 760, y - 42, "motor", ACC, al, size=26, f=BLD)
    ya, yb = 250, 520
    label(d, 70, ya - 82, "GAS", WHITE, a, size=34, f=BLK)
    cut(ya, False, a)
    ea = ease_out((lt - 0.5) / 0.4)
    label(d, 64, yb - 82, "EV", ACC, ea, size=34, f=BLK)
    cut(yb, True, ea)
    # crush-space bars growing from the bumper toward the cabin
    k = ease_inout((lt - 1.0) / 1.2)
    if k > 0:
        d.rounded_rectangle(p(840 - 120 * k, ya + 16, 840, ya + 40), radius=8 * S, fill=rgba(ACC2, a))
        d.rounded_rectangle(p(840 - 300 * k, yb + 16, 840, yb + 40), radius=8 * S, fill=rgba(ACC, ea))
        label(d, 840 - 60 * k, ya + 48, "crush space", ACC2, k, size=28, f=BLD)
        label(d, 840 - 150 * k, yb + 48, "can be more…", ACC, k, size=28, f=BLD)
    # caveat
    ca = ease_out((lt - dur * 0.55) / 0.4)
    chip(d, 450, 650, "FORD MACH-E: ~10% LESS", ACC2, ca, size=36)
    label(d, 450, 730, "every design is a trade-off", MUTED, ease_out((lt - dur * 0.55 - 0.4) / 0.4), size=26, f=SEMI)

def vis_cz_battery(d, lt, t):
    dur = sdur("cz_battery")
    a = ease_out(lt / 0.4)
    # top-down car
    x0, x1, y0, y1 = 210, 690, 90, 720
    d.rounded_rectangle(p(x0 + 10, y0 + 14, x1 + 10, y1 + 14), radius=110 * S, fill=rgba((0, 0, 0), 0.4 * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=110 * S, fill=rgba(PANEL, a), outline=rgba(STEEL, a), width=int(5 * S))
    # wheels
    for wx in (x0 - 18, x1 - 22):
        for wy in (175, 590):
            d.rounded_rectangle(p(wx, wy - 50, wx + 40, wy + 50), radius=12 * S, fill=rgba(HOLE, a))
    # battery pack: grid of modules
    bx0, bx1, by0, by1 = 300, 600, 230, 560
    pk = ease_out((lt - 0.3) / 0.6)
    for r in range(5):
        for c in range(3):
            i = r * 3 + c
            ma = ease_out((lt - 0.3 - i * 0.04) / 0.3)
            xx = bx0 + 10 + c * 98; yy = by0 + 8 + r * 64
            d.rounded_rectangle(p(xx, yy, xx + 86, yy + 54), radius=8 * S, fill=rgba(ACC, ma * 0.85))
    label(d, 450, 625, "BATTERY", ACC, pk, size=30, f=BLK)
    # side sills (thick rails) + cross-members
    sk = ease_out((lt - 1.0) / 0.5)
    for sx in (255, 645):
        d.rounded_rectangle(p(sx - 18, 210, sx + 18, 210 + 370 * sk), radius=10 * S, fill=rgba(WHITE, a * sk))
    for cy in (215, 395, 575):
        d.rectangle(p(300, cy - 5, 300 + 300 * sk, cy + 5), fill=rgba(STEEL, a * sk))
    label(d, 120, 380, "SIDE", WHITE, sk, size=26, f=BLK)
    label(d, 120, 412, "SILL", WHITE, sk, size=26, f=BLK)
    # side impact: pole comes in from the right, sill flexes, force arrows route around the pack
    hit = dur * 0.4
    hk = ease_out((lt - hit) / 0.5)
    if lt > hit - 0.6:
        pa = ease_out((lt - hit + 0.6) / 0.4)
        px = 860 - 160 * hk
        circ(d, px, 395, 40, rgba(STEEL, pa))
        circ(d, px, 395, 28, rgba(DARK, pa))
        label(d, 830, 300, "POLE", MUTED, pa, size=26, f=BLK)
    if hk > 0.5:
        fa = ease_out((lt - hit - 0.4) / 0.5)
        ph = (t * 1.2) % 1.0
        # arrows travel up and down the sill, then across cross-members
        arrow(d, 668, 380, 668, 380 - 150 * fa, rgba(ACC2, fa), w=10)
        arrow(d, 668, 410, 668, 410 + 150 * fa, rgba(ACC2, fa), w=10)
        arrow(d, 630, 215, 630 - 300 * fa, 215, rgba(ACC2, fa), w=8)
        arrow(d, 630, 575, 630 - 300 * fa, 575, rgba(ACC2, fa), w=8)
        chip(d, 450, 760, "FORCE GOES AROUND THE PACK", ACC2, ease_out((lt - hit - 0.8) / 0.4), size=30)

def vis_cz_outro(d, lt, t):
    dur = sdur("cz_outro")
    if lt < dur * 0.55:
        a = ease_out(lt / 0.35)
        gy = 520
        d.line(p(30, gy, 870, gy), fill=rgba(DARK, a), width=5 * S)
        crash_car(d, 140, gy, 0.95, 1.0, a, show_zones=1.0)
        # shield over cabin
        k = back_out((lt - 0.5) / 0.5)
        cx = 140 + (150 + 150) * 0.95
        s = clamp(k); r = 70 * max(k, 0.01)
        poly(d, [(cx - r, 170), (cx + r, 170), (cx + r, 170 + r * 0.9), (cx, 170 + r * 1.6), (cx - r, 170 + r * 0.9)], rgba(ACC, s))
        line(d, [(cx - r * 0.45, 170 + r * 0.7), (cx - r * 0.1, 170 + r * 1.05), (cx + r * 0.5, 170 + r * 0.35)], rgba(BG, s), 12)
        label(d, 450, 600, "IT TOOK THE HIT", ACC, ease_out((lt - 0.9) / 0.4), size=60, f=BLK)
    else:
        k = back_out((lt - dur * 0.55) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.55 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"cz_hook": vis_cz_hook, "cz_physics": vis_cz_physics, "cz_patent": vis_cz_patent, "cz_fintail": vis_cz_fintail,
            "cz_ev": vis_cz_ev, "cz_battery": vis_cz_battery, "cz_outro": vis_cz_outro})
