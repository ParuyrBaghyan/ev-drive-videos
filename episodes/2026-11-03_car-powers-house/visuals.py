# Episode visuals: vehicle-to-load / vehicle-to-home — your EV as a power plant.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
HOLE = (8, 10, 14)
CYAN = (90, 200, 255)
WARM = (255, 210, 120)
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

def circ(d, x, y, r, col, outline=None, w=0):
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=col, outline=outline, width=int(w * S) if w else 0)

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

def bolt(d, x, y, sc, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in pts], col)

def house(d, x, y, sc, a, lit=0.0):
    """House centred at x, ground at y."""
    w, h = 150 * sc, 140 * sc
    d.rectangle(p(x - w + 10, y - h + 14, x + w + 10, y + 14), fill=rgba((0, 0, 0), 0.35 * a))
    d.rectangle(p(x - w, y - h, x + w, y), fill=rgba(PANEL, a), outline=rgba(STEEL, a), width=int(5 * S))
    poly(d, [(x - w - 30 * sc, y - h), (x, y - h - 120 * sc), (x + w + 30 * sc, y - h)], rgba(STEEL, a))
    # windows light up
    wc = tuple(int(DARK[i] + (WARM[i] - DARK[i]) * lit) for i in range(3))
    for dx in (-0.55, 0.55):
        d.rectangle(p(x + dx * w - 34 * sc, y - h * 0.78, x + dx * w + 34 * sc, y - h * 0.38), fill=rgba(wc, a))
        if lit > 0.3:
            for i in range(3):
                d.rectangle(p(x + dx * w - (34 + i * 8) * sc, y - h * 0.78 - i * 8 * sc, x + dx * w + (34 + i * 8) * sc, y - h * 0.38 + i * 8 * sc),
                            outline=rgba(WARM, a * lit * (0.25 - i * 0.07)), width=int(5 * S))
    d.rectangle(p(x - 26 * sc, y - h * 0.55, x + 26 * sc, y), fill=rgba(DARK, a))

def flow_dots(d, pts, t, col, a, n=8, speed=0.7, r=9):
    """Dots travelling along a polyline."""
    segs = []; tot = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L_ = math.hypot(x1 - x0, y1 - y0); segs.append((x0, y0, x1, y1, L_)); tot += L_
    for i in range(n):
        u = ((t * speed + i / n) % 1.0) * tot
        for x0, y0, x1, y1, L_ in segs:
            if u <= L_:
                f = u / L_ if L_ else 0
                cx, cy = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
                circ(d, cx, cy, r + 6, rgba(col, a * 0.25))
                circ(d, cx, cy, r, rgba(col, a))
                break
            u -= L_

def pickup(d, x, y, sc, a, fill=0.0):
    """Pickup truck side view, ground line y, with battery pack in the floor."""
    c = rgba(WHITE, a)
    pts = [(-250, 30), (-250, -40), (-80, -40), (-60, -110), (60, -112), (105, -50), (240, -40), (252, 0), (252, 30)]
    poly(d, [(x + xx * sc, y - 50 * sc + yy * sc) for xx, yy in pts], c)
    poly(d, [(x - 45 * sc, y - 150 * sc), (x + 50 * sc, y - 152 * sc), (x + 88 * sc, y - 100 * sc), (x - 60 * sc, y - 100 * sc)], rgba(BG, a))
    # battery pack in the floor (cutaway)
    bx0, bx1, by0, by1 = x - 170 * sc, x + 170 * sc, y - 34 * sc, y - 4 * sc
    d.rounded_rectangle(p(bx0, by0, bx1, by1), radius=6 * S, fill=rgba(DARK, a))
    fw = (bx1 - bx0) * clamp(fill)
    if fw > 2:
        d.rounded_rectangle(p(bx0, by0, bx0 + fw, by1), radius=6 * S, fill=rgba(ACC, a))
    for i in range(1, 10):
        xx = bx0 + (bx1 - bx0) * i / 10
        d.line(p(xx, by0, xx, by1), fill=rgba(BG, a), width=int(3 * S))
    for wx in (-160, 160):
        circ(d, x + wx * sc, y, 50 * sc, rgba(HOLE, a))
        circ(d, x + wx * sc, y, 36 * sc, rgba(STEEL, a))
        circ(d, x + wx * sc, y, 14 * sc, c)

# ---------- scenes ----------
def vis_pp_hook(d, lt, t):
    a = ease_out(lt / 0.4)
    d.line(p(40, 620, 860, 620), fill=rgba(DARK, a), width=6 * S)
    cx = -150 + 380 * ease_out(lt / 1.0)
    car_side(d, cx, 540, 0.9, WHITE, a)
    hk = back_out((lt - 0.4) / 0.6)
    house(d, 680, 620, 0.95 * max(hk, 0.01), clamp(hk), lit=ease_out((lt - 1.6) / 0.6))
    ca = ease_out((lt - 1.1) / 0.4)
    cable = [(cx + 200, 520), (cx + 230, 600), (540, 600), (560, 560)]
    if ca > 0:
        line(d, cable, rgba(ACC, ca * 0.5), 8)
        flow_dots(d, cable, t, ACC, ca, n=6, speed=0.9, r=8)
    bolt(d, 680, 400, 0.6 * clamp(back_out((lt - 1.8) / 0.5)), rgba(ACC, ease_out((lt - 1.8) / 0.4)))
    chip(d, 450, 720, "CAR  →  HOUSE", ACC, ease_out((lt - 2.0) / 0.4), size=44)

def vis_pp_outlet(d, lt, t):
    a = back_out(lt / 0.5)
    # US outlet face
    x, y = 300, 400
    s = clamp(a)
    d.rounded_rectangle(p(x - 140 + 10, y - 200 + 14, x + 140 + 10, y + 200 + 14), radius=36 * S, fill=rgba((0, 0, 0), 0.4 * s))
    d.rounded_rectangle(p(x - 140, y - 200, x + 140, y + 200), radius=36 * S, fill=rgba(STEEL, s))
    for oy in (-95, 95):
        d.rounded_rectangle(p(x - 95, oy + y - 70, x + 95, oy + y + 70), radius=60 * S, fill=rgba(PANEL, s), outline=rgba(ACC, s), width=int(4 * S))
        d.rounded_rectangle(p(x - 45, y + oy - 38, x - 30, y + oy + 10), radius=4 * S, fill=rgba(HOLE, s))
        d.rounded_rectangle(p(x + 30, y + oy - 44, x + 45, y + oy + 10), radius=4 * S, fill=rgba(HOLE, s))
        d.ellipse(p(x - 14, y + oy + 22, x + 14, y + oy + 50), fill=rgba(HOLE, s))
    label(d, x, y + 230, "UNDER THE BACK SEAT", MUTED, ease_out((lt - 0.5) / 0.4), size=28, f=BLD)
    # power meter on the right
    mx, my0, my1 = 640, 180, 600
    ma = ease_out((lt - 0.8) / 0.4)
    d.rounded_rectangle(p(mx - 60, my0, mx + 60, my1), radius=24 * S, fill=rgba(PANEL, ma), outline=rgba(DARK, ma), width=int(4 * S))
    k = ease_inout((lt - 1.2) / 2.4)
    top = my1 - (my1 - my0 - 20) * k
    if top < my1 - 30:
        d.rounded_rectangle(p(mx - 46, top, mx + 46, my1 - 12), radius=16 * S, fill=rgba(ACC, ma))
        for i in range(3):
            d.rounded_rectangle(p(mx - 46 - i * 6, top - i * 6, mx + 46 + i * 6, my1 - 12 + i * 6), radius=(16 + i * 6) * S,
                                outline=rgba(ACC, ma * (0.2 - i * 0.05)), width=int(5 * S))
    val = 3.6 * k
    label(d, mx, my1 + 30, f"{val:.1f} kW", ACC, ma, size=64, f=BLK)
    # appliance icons appearing
    icons = ["LAPTOP", "KETTLE", "LIGHTS", "FRIDGE"]
    for i, nm in enumerate(icons):
        ia = ease_out((lt - 1.6 - i * 0.55) / 0.35)
        chip(d, 450 + (i - 1.5) * 200, 760, nm, WHITE if i % 2 else ACC2, ia, size=26)

def vis_pp_inverter(d, lt, t):
    a = ease_out(lt / 0.4)
    # battery
    bx, by = 150, 400
    d.rounded_rectangle(p(bx - 95, by - 140, bx + 95, by + 140), radius=22 * S, fill=rgba(PANEL, a), outline=rgba(ACC, a), width=int(5 * S))
    d.rectangle(p(bx - 35, by - 162, bx + 35, by - 140), fill=rgba(ACC, a))
    for i in range(4):
        d.rounded_rectangle(p(bx - 70, by + 100 - i * 62 - 48, bx + 70, by + 100 - i * 62), radius=8 * S, fill=rgba(ACC, a * (0.9 - i * 0.12)))
    label(d, bx, by + 170, "BATTERY", MUTED, a, size=28, f=BLD)
    # DC line in: flat
    da = ease_out((lt - 0.4) / 0.4)
    line(d, [(250, 300), (360, 300)], rgba(ACC, da), 8)
    flow_dots(d, [(250, 300), (360, 300)], t, ACC, da, n=3, speed=1.2, r=7)
    label(d, 305, 220, "DC", ACC, da, size=48, f=BLK)
    # inverter box with switching flicker
    ia = back_out((lt - 0.7) / 0.5)
    ix, iy = 450, 300
    s = clamp(ia)
    d.rounded_rectangle(p(ix - 90 + 8, iy - 90 + 12, ix + 90 + 8, iy + 90 + 12), radius=20 * S, fill=rgba((0, 0, 0), 0.4 * s))
    d.rounded_rectangle(p(ix - 90, iy - 90, ix + 90, iy + 90), radius=20 * S, fill=rgba(STEEL, s))
    for r_ in range(2):
        for c_ in range(3):
            on = (int(t * 14) + r_ + c_ * 2) % 3 == 0
            d.rounded_rectangle(p(ix - 66 + c_ * 48, iy - 52 + r_ * 56, ix - 30 + c_ * 48, iy - 8 + r_ * 56), radius=6 * S,
                                fill=rgba(ACC2 if on else PANEL, s))
    label(d, ix, iy + 110, "INVERTER", WHITE, s, size=30, f=BLK)
    # AC sine out, scrolling
    aa = ease_out((lt - 1.2) / 0.5)
    if aa > 0:
        x0, x1 = 545, 870
        pts = []
        for i in range(60):
            xx = x0 + (x1 - x0) * i / 59
            if xx > x0 + (x1 - x0) * aa: break
            pts.append((xx, 300 - 60 * math.sin((xx - x0) / 40 - t * 8)))
        if len(pts) > 1:
            line(d, pts, rgba(CYAN, 0.25), 20)
            line(d, pts, rgba(CYAN, 1), 8)
        label(d, 710, 180, "AC", CYAN, aa, size=48, f=BLK)
    # plug -> socket at bottom
    pa = ease_out((lt - 2.0) / 0.4)
    label(d, 450, 640, "FLAT  →  WAVE", WHITE, pa, size=52, f=BLK)
    label(d, 450, 715, "what every home appliance expects", MUTED, pa, size=28, f=SEMI)

def vis_pp_truck(d, lt, t):
    dur = sdur("pp_truck")
    a = ease_out(lt / 0.4)
    d.line(p(30, 470, 870, 470), fill=rgba(DARK, a), width=6 * S)
    tx = -200 + 450 * ease_out(lt / 1.1)
    k = ease_inout((lt - 1.0) / 2.6)
    pickup(d, tx, 420, 0.9, a, fill=k)
    # big battery counter
    label(d, 450, 520, f"{int(round(131 * k))} kWh", ACC, ease_out((lt - 1.0) / 0.4), size=96, f=BLK)
    label(d, 450, 640, "BATTERY PACK  ·  ABOUT 131 kWh", MUTED, ease_out((lt - 1.0) / 0.4), size=26, f=BLD)
    # second half: power into house
    h0 = dur * 0.42
    hk = ease_out((lt - h0) / 0.6)
    if hk > 0:
        house(d, 740, 270, 0.5, hk, lit=ease_out((lt - h0 - 0.6) / 0.6))
        cable = [(tx + 230, 360), (620, 300), (660, 240)]
        line(d, cable, rgba(ACC, hk * 0.45), 8)
        flow_dots(d, cable, t, ACC, hk, n=6, speed=1.2, r=8)
        chip(d, 450, 730, f"UP TO {9.6 * ease_out((lt - h0) / 1.6):.1f} kW TO THE HOUSE", ACC2, hk, size=34)

def vis_pp_days(d, lt, t):
    dur = sdur("pp_days")
    a = ease_out(lt / 0.4)
    label(d, 450, 130, "HOME  ≈  30 kWh / DAY", WHITE, a, size=46, f=BLK)
    # 10 day tiles (2 rows of 5); first 3 bright at normal use, all 10 with rationing
    k1 = (lt - 0.9) / 0.5
    phase2 = dur * 0.55
    for i in range(10):
        r_, c_ = divmod(i, 5)
        x = 130 + c_ * 160; y = 260 + r_ * 200
        if i < 3:
            ta = back_out(clamp(k1 - i * 0.9))
            col = ACC
        else:
            ta = back_out(clamp((lt - phase2 - (i - 3) * 0.12) / 0.35))
            col = ACC2
        if ta <= 0.01:
            d.rounded_rectangle(p(x - 62, y - 70, x + 62, y + 70), radius=18 * S, outline=rgba(DARK, a), width=int(4 * S))
            continue
        s = clamp(ta); h = 70 * ta
        d.rounded_rectangle(p(x - 62 + 6, y - h + 10, x + 62 + 6, y + h + 10), radius=18 * S, fill=rgba((0, 0, 0), 0.4 * s))
        d.rounded_rectangle(p(x - 62, y - h, x + 62, y + h), radius=18 * S, fill=rgba(col, s))
        d.rectangle(p(x - 62, y - h, x + 62, y - h + 26), fill=rgba(BG, s * 0.35))
        label(d, x, y - 18, str(i + 1), BG, s, size=56, f=BLK)
    label(d, 450, 690, "≈ 3 DAYS  normal use", ACC, ease_out((lt - 1.6) / 0.4), size=46, f=BLK)
    label(d, 450, 760, "UP TO 10  rationed (Ford)", ACC2, ease_out((lt - phase2 - 0.8) / 0.4), size=46, f=BLK)

def vis_pp_island(d, lt, t):
    dur = sdur("pp_island")
    a = ease_out(lt / 0.4)
    gy = 560
    d.line(p(30, gy, 870, gy), fill=rgba(DARK, a), width=6 * S)
    # utility pole on the left
    px = 100
    d.rectangle(p(px - 10, 230, px + 10, gy), fill=rgba(STEEL, a))
    d.rectangle(p(px - 50, 250, px + 50, 266), fill=rgba(STEEL, a))
    label(d, px, 180, "GRID", MUTED, a, size=30, f=BLK)
    # house on the right
    house(d, 730, gy, 0.7, a, lit=1.0)
    # truck parked on the ground
    pickup(d, 380, gy - 23, 0.45, ease_out((lt - 0.3) / 0.4), fill=0.7)
    # charger box on the house wall side
    ca = back_out((lt - 0.6) / 0.5)
    cx = 560
    s = clamp(ca)
    d.rounded_rectangle(p(cx - 32, 430, cx + 32, 530), radius=12 * S, fill=rgba(STEEL, s), outline=rgba(ACC, s), width=int(4 * S))
    bolt(d, cx, 480, 0.33, rgba(ACC, s))
    flow_dots(d, [(480, 520), (cx - 32, 500)], t, ACC, s, n=3, speed=1.2, r=6)
    flow_dots(d, [(cx + 32, 480), (625, 480)], t, ACC, s, n=3, speed=1.2, r=6)
    chip(d, 480, 600, "BIDIRECTIONAL CHARGER", ACC, ease_out((lt - 0.9) / 0.4), size=28)
    # switch between grid and house: lever opens
    sx = 300
    open_k = ease_inout((lt - dur * 0.45) / 0.6)
    line(d, [(px + 50, 258), (sx - 40, 300)], rgba(WHITE, a), 6)
    line(d, [(sx + 40, 300), (715, 392)], rgba(WHITE, a), 6)
    circ(d, sx - 40, 300, 10, rgba(WHITE, a)); circ(d, sx + 40, 300, 10, rgba(WHITE, a))
    ang = math.radians(-50 * open_k)
    ex, ey = sx - 40 + 80 * math.cos(ang), 300 + 80 * math.sin(ang)
    line(d, [(sx - 40, 300), (ex, ey)], rgba(ACC2 if open_k > 0.5 else WHITE, a), 10)
    sa = ease_out((lt - dur * 0.45 - 0.4) / 0.4)
    chip(d, sx, 140, "GRID DISCONNECT", ACC2, sa, size=30)
    # line worker at the pole, safe
    person(d, px + 75, gy, 0.6, WHITE, ease_out((lt - dur * 0.5) / 0.4), t)
    label(d, px + 75, gy + 30, "CREW SAFE", ACC2, sa, size=28, f=BLK)

def vis_pp_outro(d, lt, t):
    dur = sdur("pp_outro")
    if lt < dur * 0.55:
        a = ease_out(lt / 0.4)
        # rows of driveways: houses + cars all feeding a glowing grid bus
        line(d, [(60, 470), (840, 470)], rgba(ACC, a * 0.35), 12)
        for i in range(5):
            x = 130 + i * 160
            ia = back_out(clamp((lt - i * 0.12) / 0.35))
            house(d, x, 380, 0.42 * max(ia, 0.01), clamp(ia), lit=0.6 + 0.4 * math.sin(t * 3 + i))
            circ(d, x, 600, 34 * max(ia, 0.01), rgba(WHITE, clamp(ia)))
            bolt(d, x, 600, 0.25 * max(ia, 0.01), rgba(BG, clamp(ia)))
            flow_dots(d, [(x, 560), (x, 470)], t + i * 0.2, ACC, clamp(ia), n=2, speed=1.4, r=6)
        flow_dots(d, [(60, 470), (840, 470)], t, ACC, a, n=10, speed=0.4, r=7)
        label(d, 450, 690, "A POWER PLANT ON EVERY DRIVEWAY?", ACC, ease_out((lt - 0.6) / 0.4), size=44, f=BLK)
    else:
        k = back_out((lt - dur * 0.55) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.55 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"pp_hook": vis_pp_hook, "pp_outlet": vis_pp_outlet, "pp_inverter": vis_pp_inverter,
            "pp_truck": vis_pp_truck, "pp_days": vis_pp_days, "pp_island": vis_pp_island, "pp_outro": vis_pp_outro})
