# Episode visuals: the EV plug format war — CHAdeMO, CCS, NACS.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
HOLE = (8, 10, 14)
CYAN = (90, 200, 255)
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

def chip(d, x, y, s, col, a, size=30, w=None, tcol=None):
    if a <= 0: return
    f = FL(BLK, max(1, int(size)))
    tw = d.textlength(s, font=f) / S
    w = w or tw + 50
    d.rounded_rectangle(p(x - w / 2, y, x + w / 2, y + size * 1.7), radius=size * 0.85 * S, fill=rgba(col, a))
    text_c(d, x, y + size * 0.3, s, f, rgba(tcol or BG, a))

def shadow_round(d, x0, y0, x1, y1, r, a):
    d.rounded_rectangle(p(x0 + 8, y0 + 12, x1 + 8, y1 + 12), radius=r * S, fill=rgba((0, 0, 0), 0.4 * a))

def glow_ring(d, x, y, r, col, a):
    for i in range(5):
        arc(d, x, y, r + i * 6, 0, 360, rgba(col, a * (0.28 - i * 0.05)), 6)

# ---------- plug faces (front view), centre (x, y), scale sc ----------
def face_chademo(d, x, y, sc, a, col=ACC2):
    R = 120 * sc
    circ(d, x + 8, y + 12, R, rgba((0, 0, 0), 0.4 * a))
    circ(d, x, y, R, rgba(STEEL, a))
    circ(d, x, y, R * 0.86, rgba(PANEL, a), outline=rgba(col, a), w=5 * sc)
    # two big DC pins
    for dx in (-0.42, 0.42):
        circ(d, x + dx * R, y - 0.12 * R, 0.24 * R, rgba(HOLE, a), outline=rgba(col, a), w=4 * sc)
        circ(d, x + dx * R, y - 0.12 * R, 0.09 * R, rgba(col, a))
    # small signal pins
    for i in range(7):
        ang = math.radians(200 + i * 20)
        px, py = x + math.cos(ang) * 0.55 * R, y - math.sin(ang) * 0.55 * R * -1 + 0.05 * R
        circ(d, x + (i - 3) * 0.17 * R, y + 0.45 * R, 0.055 * R, rgba(HOLE, a), outline=rgba(MUTED, a), w=2 * sc)

def face_j1772(d, x, y, sc, a, col=CYAN):
    # J1772: round face with a flat-ish top notch, 5 pins
    R = 95 * sc
    circ(d, x + 8, y + 12, R, rgba((0, 0, 0), 0.4 * a))
    circ(d, x, y, R, rgba(STEEL, a))
    circ(d, x, y, R * 0.84, rgba(PANEL, a), outline=rgba(col, a), w=5 * sc)
    for dx, dy, r in ((-0.36, -0.22, 0.17), (0.36, -0.22, 0.17), (0, 0.42, 0.15), (-0.32, 0.25, 0.09), (0.32, 0.25, 0.09)):
        circ(d, x + dx * R, y + dy * R, r * R, rgba(HOLE, a), outline=rgba(col, a), w=3 * sc)

def dc_block(d, x, y, sc, a, col=ACC2):
    w, h = 150 * sc, 70 * sc
    shadow_round(d, x - w, y - h, x + w, y + h, 50 * sc, a)
    d.rounded_rectangle(p(x - w, y - h, x + w, y + h), radius=50 * sc * S, fill=rgba(STEEL, a))
    d.rounded_rectangle(p(x - w * 0.88, y - h * 0.75, x + w * 0.88, y + h * 0.75), radius=40 * sc * S, fill=rgba(PANEL, a), outline=rgba(col, a), width=int(5 * S * sc))
    for dx in (-0.48, 0.48):
        circ(d, x + dx * w, y, 0.55 * h, rgba(HOLE, a), outline=rgba(col, a), w=4 * sc)
        circ(d, x + dx * w, y, 0.2 * h, rgba(col, a))

def face_nacs(d, x, y, sc, a, col=ACC, glow=0.0):
    # NACS: compact teardrop/rounded shape, 2 big pins + 3 small
    w, h = 80 * sc, 95 * sc
    pts = []
    for i in range(48):
        ang = 2 * math.pi * i / 48
        rx = w * (1 - 0.18 * max(0, -math.sin(ang)))
        pts.append((x + math.cos(ang) * rx, y + math.sin(ang) * h))
    poly(d, [(px + 8, py + 12) for px, py in pts], rgba((0, 0, 0), 0.4 * a))
    poly(d, pts, rgba(STEEL, a))
    inner = [(x + (px - x) * 0.84, y + (py - y) * 0.84) for px, py in pts]
    poly(d, inner, rgba(PANEL, a))
    d.line(p(*[v for xy in inner + inner[:1] for v in xy]), fill=rgba(col, a), width=int(5 * S * sc))
    for dx in (-0.4, 0.4):
        circ(d, x + dx * w, y + 0.12 * h, 0.24 * w, rgba(HOLE, a), outline=rgba(col, a), w=4 * sc)
        circ(d, x + dx * w, y + 0.12 * h, 0.1 * w + glow * 0.08 * w, rgba(col, a))
    for dx in (-0.22, 0, 0.22):
        circ(d, x + dx * w, y - 0.45 * h, 0.07 * w, rgba(HOLE, a), outline=rgba(MUTED, a), w=2 * sc)

def ccs1(d, x, y, sc, a, join=1.0):
    face_j1772(d, x, y - 70 * sc, sc, a)
    dc_block(d, x, y + 95 * sc + (1 - join) * 220, sc * 0.82, a)

# ---------- scene 1: three plugs, format war ----------
def vis_pw_hook(d, lt, t):
    items = [(180, "CHADEMO", ACC2), (450, "CCS", CYAN), (720, "NACS", ACC)]
    for i, (x, nm, col) in enumerate(items):
        k = back_out((lt - 0.25 - 0.35 * i) / 0.45)
        if k <= 0: continue
        a = clamp(k)
        bob = math.sin(t * 2 + i) * 6
        y = 420 + (1 - k) * 120 + bob
        if i == 0: face_chademo(d, x, y, 0.68, a)
        elif i == 1: ccs1(d, x, y - 10, 0.62, a)
        else: face_nacs(d, x, y, 0.95, a)
        chip(d, x, 640, nm, col, a, size=30)
    k = ease_out((lt - 1.8) / 0.4)
    if k > 0:
        f = FL(BLK, 54)
        for x in (318, 588):
            text_c(d, x, 395, "VS", f, rgba(WHITE, k * (0.7 + 0.3 * math.sin(t * 6))))
    k2 = ease_out((lt - 2.6) / 0.5)
    label(d, 450, 760, "THE PLUG FORMAT WAR", MUTED, k2, size=42, f=BLD)

# ---------- scene 2: CHAdeMO, 2010 ----------
def vis_pw_chademo(d, lt, t):
    yr = int(round(2000 + 10 * ease_out(lt / 1.0)))
    label(d, 450, 40, str(yr), ACC2, 1, size=110, f=BLK)
    k = back_out((lt - 0.3) / 0.6)
    if k > 0:
        glow_ring(d, 290, 410, 130 * k, ACC2, clamp(k) * (0.6 + 0.4 * math.sin(t * 3)))
        face_chademo(d, 290, 410, 1.05 * k, clamp(k))
    label(d, 290, 570, "CHADEMO", WHITE, ease_out((lt - 0.8) / 0.4), size=40, f=BLK)
    label(d, 290, 620, "MADE IN JAPAN", MUTED, ease_out((lt - 1.0) / 0.4), size=28)
    backers = ["TEPCO", "NISSAN", "TOYOTA", "MITSUBISHI"]
    for i, b in enumerate(backers):
        a = ease_out((lt - 1.4 - 0.35 * i) / 0.35)
        if a <= 0: continue
        y = 270 + i * 80
        x = 680 + (1 - a) * 60
        chip(d, x, y, b, ACC2 if i < 2 else STEEL, a, size=28, w=260, tcol=BG if i < 2 else WHITE)
    label(d, 680, 230, "BACKED BY", MUTED, ease_out((lt - 1.2) / 0.3), size=26)
    # Leaf: little car plugging in
    a = ease_out((lt - 4.2) / 0.5)
    if a > 0:
        cx = 680 + (1 - a) * 80
        car_side(d, cx, 650, 0.62, WHITE, a)
        chip(d, cx, 730, "NISSAN LEAF", ACC2, a, size=26)

# ---------- scene 3: CCS = AC plug + DC pins ----------
def vis_pw_ccs(d, lt, t):
    a1 = ease_out(lt / 0.4)
    face_j1772(d, 450, 290, 1.25, a1)
    label(d, 450, 60, "AC PLUG (J1772)", CYAN, a1, size=34, f=BLK)
    j = ease_inout((lt - 1.4) / 1.0)
    a2 = ease_out((lt - 1.1) / 0.4)
    if a2 > 0:
        y = 900 - (900 - 525) * j
        dc_block(d, 450, y, 1.05, a2)
        label(d, 450, y + 90, "+ 2 DC PINS", ACC2, a2 * (1 - j), size=34, f=BLK)
    # merge flash and arrow pulse
    if j >= 1:
        k = ease_out((lt - 2.5) / 0.5)
        for i in range(3):
            ph = (t * 1.3 + i / 3) % 1.0
            arc(d, 450, 400, 230 + ph * 60, 0, 360, rgba(ACC, k * (1 - ph) * 0.5), 5)
        chip(d, 450, 710, "COMBINED CHARGING SYSTEM", ACC, k, size=34)

# ---------- scene 4: Tesla plug, smaller, shared pins ----------
def vis_pw_tesla(d, lt, t):
    label(d, 450, 40, "TESLA · 2012", ACC, ease_out(lt / 0.4), size=56, f=BLK)
    # size comparison: CCS1 outline vs NACS
    a = ease_out((lt - 0.3) / 0.4)
    ccs1(d, 250, 400, 0.85, a * 0.85)
    label(d, 250, 150, "CCS", CYAN, a, size=32, f=BLK)
    k = back_out((lt - 0.8) / 0.5)
    if k > 0:
        face_nacs(d, 640, 430, 1.25 * k, clamp(k), glow=0.5 + 0.5 * math.sin(t * 6))
        label(d, 640, 150, "TESLA PLUG", ACC, clamp(k), size=32, f=BLK)
    # height bars for size
    hb = ease_out((lt - 1.6) / 0.6)
    if hb > 0:
        d.line(p(90, 210, 90, 210 + 370 * hb), fill=rgba(CYAN, 0.8), width=5 * S)
        d.line(p(800, 315, 800, 315 + 235 * hb), fill=rgba(ACC, 0.8), width=5 * S)
        label(d, 800, 565, "SMALLER", ACC, hb, size=26, f=BLD)
    # AC and DC flows into the two pins
    fl = ease_out((lt - 3.4) / 0.5)
    if fl > 0:
        for i, (nm, col) in enumerate((("AC", CYAN), ("DC", ACC2))):
            y0 = 760
            x0 = 560 + i * 160
            chip(d, x0, y0, nm, col, fl, size=30, w=110)
            pin_x = 640
            d.line(p(x0, y0 - 6, pin_x, 562), fill=rgba(col, fl * 0.35), width=4 * S)
            for j in range(3):
                ph = (t * 1.2 + j / 3 + i * 0.17) % 1.0
                yy = (y0 - 6) + ph * (562 - (y0 - 6))
                xx = x0 + (pin_x - x0) * ph
                circ(d, xx, yy, 11, rgba(col, fl * (1 - ph * 0.4)))
        label(d, 640, 840, "SAME TWO PINS", WHITE, fl, size=30, f=BLK)

# ---------- scene 5: opened as NACS, automakers sign on ----------
def vis_pw_flip(d, lt, t):
    # timeline
    x0, x1, y = 90, 810, 260
    k = ease_out(lt / 0.8)
    d.line(p(x0, y, x0 + (x1 - x0) * k, y), fill=rgba(DARK, 1), width=8 * S)
    nodes = [(0.0, "NOV 2022", "NACS OPENED", ACC, 0.4), (0.45, "2023", "FORD", WHITE, 2.4), (0.75, "2023", "GM", WHITE, 3.2)]
    for fx, top, bot, col, t0 in nodes:
        a = back_out((lt - t0) / 0.4)
        if a <= 0: continue
        x = x0 + 40 + (x1 - x0 - 80) * fx
        circ(d, x, y, 18 * clamp(a), rgba(col, 1))
        label(d, x, y - 80, top, MUTED, clamp(a), size=26)
        label(d, x, y + 34, bot, col, clamp(a), size=32, f=BLK)
    # open padlock -> NACS
    a = ease_out((lt - 0.4) / 0.5)
    face_nacs(d, 450, 520, 1.0, a, glow=0.5 + 0.5 * math.sin(t * 5))
    # adoption: little car icons joining from both sides
    n = 14
    for i in range(n):
        t0 = 3.6 + i * 0.16
        k2 = ease_out((lt - t0) / 0.45)
        if k2 <= 0: continue
        side = -1 if i % 2 == 0 else 1
        row = (i // 2) % 2
        col_i = i // 4
        tx = 450 + side * (150 + (i // 2 % 4) * 70)
        ty = 470 + row * 110 + (col_i % 2) * 0
        sx = 450 + side * 520
        x = sx + (tx - sx) * k2
        circ(d, x, ty, 20, rgba(ACC if i < 2 else WHITE, k2 * 0.9))
        d.line(p(x, ty, 450 + side * 90, 520), fill=rgba(ACC, k2 * 0.25), width=3 * S)
    label(d, 450, 760, "NEARLY EVERY AUTOMAKER", ACC, ease_out((lt - 5.2) / 0.4), size=40, f=BLK)

# ---------- scene 6: SAE J3400 standard ----------
def vis_pw_sae(d, lt, t):
    a = ease_out(lt / 0.4)
    # document
    x0, y0, x1, y1 = 230, 120, 670, 700
    shadow_round(d, x0, y0, x1, y1, 26, a)
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=26 * S, fill=rgba(PANEL, a), outline=rgba(DARK, a), width=4 * S)
    for i in range(6):
        w = ease_out((lt - 0.2 - i * 0.12) / 0.4)
        d.rounded_rectangle(p(x0 + 50, y0 + 330 + i * 52, x0 + 50 + (x1 - x0 - 100) * w * (0.6 if i % 3 == 2 else 1), y0 + 348 + i * 52), radius=8 * S, fill=rgba(DARK, a))
    face_nacs(d, 450, 240, 0.85, a)
    # stamp
    k = back_out((lt - 1.3) / 0.35)
    if k > 0:
        sc = 1 + (1 - clamp(k)) * 1.2
        w, h = 210 * sc, 60 * sc
        cx, cy = 450, 470
        d.rounded_rectangle(p(cx - w, cy - h, cx + w, cy + h), radius=20 * S, outline=rgba(ACC, clamp(k)), width=int(8 * S), fill=rgba(BG, clamp(k) * 0.9))
        text_c(d, cx, cy - 38 * sc, "SAE J3400", FL(BLK, max(1, int(64 * sc))), rgba(ACC, clamp(k)))
    label(d, 450, 760, "OFFICIAL STANDARD · 2024", WHITE, ease_out((lt - 2.0) / 0.4), size=38, f=BLK)

# ---------- scene 7: question + outro ----------
def vis_pw_outro(d, lt, t):
    dur = sdur("pw_outro")
    if lt < dur * 0.55:
        a = ease_out(lt / 0.4)
        # one big plug with many small cars around
        face_nacs(d, 450, 380, 1.4, a, glow=0.5 + 0.5 * math.sin(t * 5))
        for i in range(10):
            ang = t * 0.6 + i * 2 * math.pi / 10
            circ(d, 450 + math.cos(ang) * 260, 380 + math.sin(ang) * 200, 16, rgba(WHITE, a * 0.8))
        label(d, 450, 660, "ONE PLUG FOR ALL?", ACC, ease_out((lt - 0.5) / 0.4), size=60, f=BLK)
    else:
        k = back_out((lt - dur * 0.55) / 0.5)
        bx, by, bs = 450, 260, 1.7 * k
        pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
        poly(d, [(bx + xx * bs, by + yy * bs) for xx, yy in pts], rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.55 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"pw_hook": vis_pw_hook, "pw_chademo": vis_pw_chademo, "pw_ccs": vis_pw_ccs,
            "pw_tesla": vis_pw_tesla, "pw_flip": vis_pw_flip, "pw_sae": vis_pw_sae, "pw_outro": vis_pw_outro})
