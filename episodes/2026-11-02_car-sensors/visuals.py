# Episode visuals: how self-driving cars see — cameras, radar, lidar.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
ROAD = (18, 23, 31)
CAMC = ACC          # camera = lime
RADC = ACC2         # radar = orange
LIDC = (90, 200, 255)  # lidar = cyan
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

def chip(d, x, y, s, col, a, size=30, w=None):
    if a <= 0: return
    f = FL(BLK, max(1, int(size)))
    tw = d.textlength(s, font=f) / S
    w = w or tw + 50
    d.rounded_rectangle(p(x - w / 2, y, x + w / 2, y + size * 1.7), radius=size * 0.85 * S, fill=rgba(col, a))
    text_c(d, x, y + size * 0.3, s, f, rgba(BG, a))

def car_top(d, x, y, sc, col, a):
    """Top-down car pointing up; (x, y) = centre."""
    w, h = 70 * sc, 140 * sc
    d.rounded_rectangle(p(x - w + 4, y - h + 8, x + w + 4, y + h + 8), radius=40 * sc * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(x - w, y - h, x + w, y + h), radius=40 * sc * S, fill=rgba(col, a))
    d.rounded_rectangle(p(x - w * 0.72, y - h * 0.52, x + w * 0.72, y - h * 0.18), radius=14 * sc * S, fill=rgba(BG, a))
    d.rounded_rectangle(p(x - w * 0.72, y + h * 0.42, x + w * 0.72, y + h * 0.66), radius=12 * sc * S, fill=rgba(BG, a))
    d.rounded_rectangle(p(x - w * 0.6, y - h * 0.12, x + w * 0.6, y + h * 0.36), radius=12 * sc * S, fill=rgba(tuple(int(c * 0.8) for c in col), a))

def wedge(d, cx, cy, r, a0, a1, col, a):
    d.pieslice(p(cx - r, cy - r, cx + r, cy + r), a0, a1, fill=rgba(col, a))

def eye_icon(d, x, y, sc, col, a):
    d.ellipse(p(x - 34 * sc, y - 20 * sc, x + 34 * sc, y + 20 * sc), outline=rgba(col, a), width=int(6 * S * sc))
    d.ellipse(p(x - 11 * sc, y - 11 * sc, x + 11 * sc, y + 11 * sc), fill=rgba(col, a))

def blob_car(d, x, y, sc, col, a):
    body = [(-60, -14), (-60, -34), (-30, -40), (-14, -62), (26, -62), (44, -40), (62, -34), (62, -14)]
    poly(d, [(x + px * sc, y + py * sc) for px, py in body], rgba(col, a))
    for wx in (-34, 36):
        r = 13 * sc
        d.ellipse(p(x + wx * sc - r, y - 14 * sc - r, x + wx * sc + r, y - 14 * sc + r), fill=rgba((30, 36, 46), a))

# ---------- scene 1: three eyes around a car ----------
def vis_sn_hook(d, lt, t):
    a = ease_out(lt / 0.35)
    cx, cy = 450, 470
    sens = [("CAMERA", CAMC, -90, 40, 0.5, 300), ("RADAR", RADC, -90, 14, 1.3, 330), ("LIDAR", LIDC, 0, 360, 2.1, 250)]
    for nm, col, mid, half, t0, r in sens:
        k = ease_out((lt - t0) / 0.6)
        if k <= 0: continue
        if half >= 180:
            # lidar: rotating sweep + faint ring
            ang = (t * 220) % 360
            for j in range(10):
                wedge(d, cx, cy, r * k, ang - j * 6 - 6, ang - j * 6, col, a * 0.22 * (1 - j / 10))
            arc(d, cx, cy, r * k, 0, 360, rgba(col, a * 0.5), 3)
        else:
            pul = 0.10 + 0.05 * math.sin(t * 5 + t0)
            wedge(d, cx, cy - 120, r * k, mid - half, mid + half, col, a * pul)
            arc(d, cx, cy - 120, r * k, mid - half, mid + half, rgba(col, a * 0.9), 5)
    car_top(d, cx, cy, 1.0, STEEL, a)
    # sensor dots on car
    d.ellipse(p(cx - 12, cy - 152, cx + 12, cy - 128), fill=rgba(CAMC, a))
    d.rectangle(p(cx - 30, cy - 146, cx - 16, cy - 132), fill=rgba(RADC, a))
    d.ellipse(p(cx - 16, cy - 16, cx + 16, cy + 16), fill=rgba(LIDC, a))
    # labels
    for i, (nm, col, *_rest) in enumerate(sens):
        q = back_out((lt - 0.7 - i * 0.8) / 0.5)
        chip(d, 170 + i * 280, 745, nm, col, clamp(q), 34 * clamp(q) + 1, w=240)
    q = ease_out((lt - 3.6) / 0.4)
    if q > 0:
        label(d, 450, 860 - 20 * q, "EACH ONE HAS A BLIND SPOT", WHITE, q, 34, BLK)

# ---------- scene 2: camera ----------
def vis_sn_camera(d, lt, t):
    a = ease_out(lt / 0.35)
    dur = sdur("sn_camera")
    # viewfinder
    x0, y0, x1, y1 = 90, 60, 810, 560
    panel(d, x0, y0, x1, y1, a, outline=CAMC)
    # road in perspective
    vx, vy = 450, 250
    poly(d, [(vx - 20, vy), (vx + 20, vy), (x1 - 40, y1 - 20), (x0 + 40, y1 - 20)], rgba(ROAD, a))
    for side in (-1, 1):
        d.line(p(vx + side * 18, vy, 450 + side * 330, y1 - 20), fill=rgba(WHITE, a * 0.8), width=int(6 * S))
    for k in range(6):
        u = ((k / 6) + t * 0.5) % 1
        yy = vy + (y1 - 20 - vy) * u ** 2
        hh = 6 + 30 * u ** 2
        d.rectangle(p(448 - 2 * u * 4, yy, 452 + 2 * u * 4, min(yy + hh, y1 - 20)), fill=rgba(WHITE, a * 0.7))
    # traffic light (cycles red -> green)
    tl = ease_out((lt - 0.8) / 0.4)
    if tl > 0:
        tx, ty = 700, 110
        d.rounded_rectangle(p(tx - 30, ty, tx + 30, ty + 150), radius=14 * S, fill=rgba((12, 14, 18), tl * a))
        green = (lt % 2.0) > 1.0
        d.ellipse(p(tx - 20, ty + 12, tx + 20, ty + 52), fill=rgba((255, 60, 60) if not green else (60, 30, 30), tl * a))
        d.ellipse(p(tx - 20, ty + 98, tx + 20, ty + 138), fill=rgba((60, 255, 120) if green else (30, 60, 40), tl * a))
        d.line(p(tx, ty + 150, tx, 280), fill=rgba(STEEL, tl * a), width=int(8 * S))
    # speed sign
    sg = ease_out((lt - 1.3) / 0.4)
    if sg > 0:
        sx, sy = 190, 130
        d.rounded_rectangle(p(sx - 52, sy, sx + 52, sy + 130), radius=10 * S, fill=rgba(WHITE, sg * a))
        label(d, sx, sy + 10, "SPEED", BG, sg * a, 20, BLK)
        label(d, sx, sy + 40, "55", BG, sg * a, 64, BLK)
        d.line(p(sx, sy + 130, sx, 290), fill=rgba(STEEL, sg * a), width=int(8 * S))
    # detection boxes
    bx = ease_out((lt - 1.8) / 0.4)
    if bx > 0:
        for (bx0, by0, bx1, by1, nm) in [(125, 118, 255, 268, "SIGN"), (655, 98, 745, 270, "LIGHT"), (300, 380, 600, 540, "LANE")]:
            d.rectangle(p(bx0, by0, bx1, by1), outline=rgba(CAMC, bx * a), width=int(4 * S))
            d.rectangle(p(bx0, by0 - 32, bx0 + 16 * len(nm) + 20, by0), fill=rgba(CAMC, bx * a))
            d.text(((bx0 + 8) * S, (by0 - 30) * S), nm, font=FL(BLK, 22), fill=rgba(BG, bx * a))
    # weaknesses: glare, dark, fog wash over the viewfinder
    wk = [("GLARE", 4.4), ("DARK", 5.4), ("FOG", 6.4)]
    for i, (nm, t0) in enumerate(wk):
        k = ease_out((lt - t0) / 0.35)
        if k <= 0: continue
        nxt = wk[i + 1][1] if i + 1 < len(wk) else 99
        live = k * (1 - ease_out((lt - nxt + 0.1) / 0.3))
        if live > 0:
            if nm == "GLARE":
                for r in range(9, 0, -1):
                    d.ellipse(p(640 - r * 34, 130 - r * 34, 640 + r * 34, 130 + r * 34), fill=rgba((255, 250, 225), live * a * 0.12))
            elif nm == "DARK":
                d.rounded_rectangle(p(x0 + 4, y0 + 4, x1 - 4, y1 - 4), radius=22 * S, fill=rgba((0, 0, 0), live * a * 0.82))
            else:
                d.rounded_rectangle(p(x0 + 4, y0 + 4, x1 - 4, y1 - 4), radius=22 * S, fill=rgba((180, 190, 200), live * a * 0.38))
        chip(d, 190 + i * 260, 600, nm, ACC2, k * a, 32, w=210)
    q = back_out((lt - 7.6) / 0.5)
    if q > 0:
        panel(d, 170, 720, 730, 850, clamp(q))
        label(d, 450, 735, "DISTANCE = ?", WHITE, clamp(q), 46, BLK)
        label(d, 450, 800, "INFERRED BY SOFTWARE", MUTED, clamp(q), 24, BLD)

# ---------- scene 3: radar ----------
def vis_sn_radar(d, lt, t):
    a = ease_out(lt / 0.35)
    # road side view
    gy = 430
    d.rectangle(p(40, gy, 860, gy + 14), fill=rgba(DARK, a))
    # rain
    rn = ease_out((lt - 2.6) / 0.6)
    if rn > 0:
        for i in range(46):
            rx = (i * 97) % 820 + 40
            ry = (i * 53 + t * 700) % 400 + 20
            d.line(p(rx, ry, rx - 8, ry + 26), fill=rgba((140, 170, 210), rn * a * 0.55), width=int(3 * S))
    # ego car (left), target car (right)
    car_side(d, 180, gy - 52, 0.42, STEEL, a)
    tx = 700 - 30 * ease_inout(lt / 8)
    blob_car(d, tx, gy, 1.7, (150, 160, 175), a)
    # emitter
    ex, ey = 278, gy - 72
    d.ellipse(p(ex - 12, ey - 12, ex + 12, ey + 12), fill=rgba(RADC, a))
    # outgoing waves and echoes
    span = tx - 100 - ex
    for i in range(4):
        ph = (lt * 0.9 + i / 4) % 1
        r = 30 + span * ph
        arc(d, ex, ey, r, -28, 28, rgba(RADC, a * (1 - ph) * 0.9), 7)
        rb = 30 + span * ph
        arc(d, tx - 100, ey, rb, 152, 208, rgba(RADC, a * (1 - ph) * 0.45), 4)
    # readouts
    k = ease_out((lt - 1.0) / 0.5)
    if k > 0:
        dist = int(180 - 40 * ease_inout(lt / 8))
        panel(d, 90, 520, 430, 680, k * a, outline=RADC)
        label(d, 260, 535, f"{dist} FT", WHITE, k * a, 62, BLK)
        label(d, 260, 620, "DISTANCE", MUTED, k * a, 24, BLD)
        panel(d, 470, 520, 810, 680, k * a, outline=RADC)
        label(d, 640, 535, "-5 MPH", WHITE, k * a, 62, BLK)
        label(d, 640, 620, "CLOSING SPEED", MUTED, k * a, 24, BLD)
    chip(d, 450, 40, "WORKS IN RAIN & FOG", RADC, ease_out((lt - 3.0) / 0.4) * a, 32)
    # blurry blob: deer or rock?
    b = ease_out((lt - 5.2) / 0.5)
    if b > 0:
        d.rectangle(p(40, 160, 860, gy - 2), fill=rgba(BG, b * 0.85 * a))
        for r in range(7, 0, -1):
            d.ellipse(p(450 - r * 26, 300 - r * 16, 450 + r * 26, 300 + r * 16), fill=rgba(RADC, b * a * 0.13))
        chip(d, 300, 720, "DEER?", WHITE, back_out((lt - 6.0) / 0.4) and clamp(back_out((lt - 6.0) / 0.4)) * a, 36, w=220)
        chip(d, 600, 720, "ROCK?", WHITE, clamp(back_out((lt - 6.5) / 0.4)) * a, 36, w=220)
        label(d, 450, 810, "LOW RESOLUTION", MUTED, b * a, 30, BLK)

# ---------- scene 4: lidar point cloud ----------
_pts_cache = []
def _cloud():
    if _pts_cache: return _pts_cache
    import random
    rnd = random.Random(7)
    # car outline (side view) around x 470..760
    body = [(-60, -14), (-60, -34), (-30, -40), (-14, -62), (26, -62), (44, -40), (62, -34), (62, -14)]
    sc = 2.4; ox, oy = 620, 470
    for i in range(len(body)):
        (xa, ya), (xb, yb) = body[i], body[(i + 1) % len(body)]
        for k in range(18):
            u = k / 18
            _pts_cache.append((ox + (xa + (xb - xa) * u) * sc + rnd.uniform(-3, 3), oy + (ya + (yb - ya) * u) * sc + rnd.uniform(-3, 3), 0))
    for wx in (-34, 36):
        for k in range(20):
            an = k / 20 * 2 * math.pi
            _pts_cache.append((ox + wx * sc + math.cos(an) * 30, oy - 14 * sc + math.sin(an) * 30, 0))
    # pedestrian left
    px_, py_ = 250, 470
    for k in range(16):
        an = k / 16 * 2 * math.pi
        _pts_cache.append((px_ + math.cos(an) * 20, py_ - 190 + math.sin(an) * 20, 1))
    for k in range(40):
        u = k / 40
        _pts_cache.append((px_ + rnd.uniform(-14, 14), py_ - 165 + u * 165, 1))
    # ground dots
    for k in range(70):
        _pts_cache.append((60 + k * 11.6, 480 + (k % 3) * 8, 2))
    rnd.shuffle(_pts_cache)
    return _pts_cache

def vis_sn_lidar(d, lt, t):
    a = ease_out(lt / 0.35)
    pts = _cloud()
    # lidar puck at left-top
    lx, ly = 450, 90
    d.rounded_rectangle(p(lx - 40, ly - 22, lx + 40, ly + 22), radius=12 * S, fill=rgba(STEEL, a))
    d.rectangle(p(lx - 40, ly - 6, lx + 40, ly + 6), fill=rgba(LIDC, a * (0.6 + 0.4 * math.sin(t * 12))))
    label(d, lx, ly - 70, "LIDAR", LIDC, a, 30, BLK)
    grow = ease_inout((lt - 0.4) / 4.0)
    n = int(len(pts) * grow)
    fog = ease_out((lt - 6.0) / 0.6)
    # laser rays to the newest few points
    for j in range(max(0, n - 6), n):
        x, y, _ = pts[j]
        d.line(p(lx, ly + 20, x, y), fill=rgba(LIDC, a * 0.35 * (1 - fog)), width=int(2 * S))
    for j in range(n):
        x, y, kind = pts[j]
        if fog > 0:
            # scatter: jitter and fade
            sx = math.sin(j * 12.9898) * 40 * fog
            sy = math.cos(j * 78.233) * 40 * fog
            x, y = x + sx, y + sy
        col = WHITE if kind == 2 else LIDC
        al = a * (0.9 - 0.6 * fog) * (0.5 if kind == 2 else 1)
        d.ellipse(p(x - 4, y - 4, x + 4, y + 4), fill=rgba(col, al))
    if fog > 0:
        for i in range(5):
            yy = 260 + (i % 3) * 70
            off = (t * 30 + i * 210) % 1100 - 100
            for r in range(4, 0, -1):
                d.ellipse(p(off - 60 * r, yy - 18 * r, off + 60 * r, yy + 18 * r), fill=rgba((170, 180, 192), fog * a * 0.05))
    # counter + labels
    k = ease_out((lt - 0.6) / 0.4)
    if k > 0:
        panel(d, 90, 560, 430, 700, k * a, outline=LIDC)
        label(d, 260, 575, f"{n}", WHITE, k * a, 60, BLK)
        label(d, 260, 655, "LASER ECHOES", MUTED, k * a, 24, BLD)
        panel(d, 470, 560, 810, 700, k * a, outline=LIDC)
        label(d, 640, 580, "3D MAP", LIDC, k * a, 54, BLK)
        label(d, 640, 655, "TIME OF FLIGHT", MUTED, k * a, 24, BLD)
    for i, (nm, t0) in enumerate([("FOG & SNOW", 6.2), ("COST $$$", 8.4)]):
        chip(d, 260 + i * 380, 760, nm, ACC2, clamp(back_out((lt - t0) / 0.45)) * a, 32, w=320)

# ---------- scene 5: fusion ----------
def vis_sn_fusion(d, lt, t):
    a = ease_out(lt / 0.35)
    cx, cy, R = 450, 330, 150
    items = [("CAMERA", CAMC, -90, "SIGNS · COLOR"), ("RADAR", RADC, 30, "SPEED · WEATHER"), ("LIDAR", LIDC, 150, "3D SHAPE")]
    m = ease_inout((lt - 0.2) / 1.4)
    for i, (nm, col, ang, sub) in enumerate(items):
        k = ease_out((lt - i * 0.3) / 0.5)
        if k <= 0: continue
        dist = 230 - 140 * m
        x = cx + math.cos(math.radians(ang)) * dist
        y = cy + math.sin(math.radians(ang)) * dist
        d.ellipse(p(x - R, y - R, x + R, y + R), fill=rgba(col, k * a * 0.22), outline=rgba(col, k * a), width=int(5 * S))

    for i, (nm, col, ang, sub) in enumerate(items):
        k = ease_out((lt - i * 0.3) / 0.5)
        if k <= 0: continue
        dist = 230 - 140 * m
        if ang == -90:
            lx, ly = cx, cy - dist - 195
        else:
            lx = cx + (355 if ang == 30 else -330)
            ly = cy + 90
        lx = max(150, min(750, lx))
        label(d, lx, ly - 30, nm, col, k * a, 32, BLK)
        label(d, lx, ly + 10, sub, WHITE, k * a * ease_out((lt - 1.4) / 0.4), 22, BLD)
    q = back_out((lt - 1.7) / 0.5)
    if q > 0:
        d.ellipse(p(cx - 62 * clamp(q), cy - 62 * clamp(q), cx + 62 * clamp(q), cy + 62 * clamp(q)), fill=rgba(WHITE, clamp(q) * a))
        label(d, cx, cy - 16, "FUSION", BG, clamp(q) * a, 26 * clamp(q) + 1, BLK)
    k = ease_out((lt - 3.6) / 0.5)
    if k > 0:
        panel(d, 110, 620, 790, 840, k * a, outline=ACC2)
        label(d, 450, 640, "THE EXCEPTION", ACC2, k * a, 28, BLK)
        label(d, 450, 690, "TESLA: CAMERAS ONLY", WHITE, k * a, 48, BLK)
        # radar crossed out
        kk = ease_out((lt - 4.6) / 0.4)
        chip(d, 330, 768, "RADAR", RADC, k * a * 0.9, 26, w=170)
        if kk > 0:
            d.line(p(250, 795, 250 + 160 * kk, 780), fill=rgba(WHITE, k * a), width=int(6 * S))
        chip(d, 580, 768, "SINCE 2021", WHITE, k * a, 26, w=230)

# ---------- outro ----------
def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL(BLK, max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

def vis_sn_outro(d, lt, t):
    dur = sdur("sn_outro")
    cut = dur * 0.5
    if lt < cut:
        a = 1 - ease_inout((lt - cut + 0.3) / 0.3)
        for i, col in enumerate([CAMC, RADC, LIDC]):
            k = back_out((lt - i * 0.15) / 0.4)
            eye_icon(d, 250 + i * 200, 250, 2.0 * clamp(k), col, a * clamp(k))
        q = back_out((lt - 0.5) / 0.5)
        if q > 0:
            label(d, 450, 400, "IS ONE KIND OF EYE", WHITE, a * clamp(q), 56 * clamp(q) + 1, BLK)
            label(d, 450, 480, "EVER ENOUGH?", ACC, a * clamp(q), 72 * clamp(q) + 1, BLK)
    else:
        end_card(d, lt, cut)

VIS.update({"sn_hook": vis_sn_hook, "sn_camera": vis_sn_camera, "sn_radar": vis_sn_radar,
            "sn_lidar": vis_sn_lidar, "sn_fusion": vis_sn_fusion, "sn_outro": vis_sn_outro})
