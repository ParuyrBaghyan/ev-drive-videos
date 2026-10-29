# Episode visuals: Myth vs fact — do EVs catch fire more often?
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
FIRE = (255, 92, 51)
WATER = (90, 170, 255)
RED = (255, 70, 70)

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
    d.rounded_rectangle(p(x0 + 6, y0 + 10, x1 + 6, y1 + 10), radius=28 * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=28 * S, fill=rgba(PANEL, 0.94 * a),
                        outline=rgba(outline or DARK, a), width=int(4 * S))

def flame(d, cx, by, sz, t, a=1.0, seed=0):
    """Layered flickering flame, base at (cx, by)."""
    for layer, (col, sc) in enumerate([(FIRE, 1.0), (ACC2, 0.72), ((255, 210, 90), 0.45)]):
        f = 1 + 0.08 * math.sin(t * 11 + seed + layer)
        h = sz * sc * f
        w = sz * 0.42 * sc
        sway = math.sin(t * 7 + seed) * w * 0.25
        left, right = [], []
        for k in range(25):
            u = k / 24
            hw = w * math.sin(math.pi / 2 * min(u * 2.2, 1)) * (1 - u) ** 0.85
            sx = sway * u * u + math.sin(t * 13 + seed + u * 6) * w * 0.06 * u
            y = by - h * u
            left.append((cx - hw + sx, y)); right.append((cx + hw + sx, y))
        bot = [(cx + w * 0.7 * math.cos(math.pi * j / 8), by + w * 0.35 * math.sin(math.pi * j / 8)) for j in range(9)]
        pts = left + right[::-1]
        poly(d, left + right[::-1], rgba(col, a))

def sedan(d, x, y, sc, col, a=1.0):
    pts = [(-230, 40), (-230, -10), (-200, -40), (-110, -50), (-60, -108), (90, -110), (160, -55), (225, -40), (238, 0), (238, 40)]
    poly(d, [(x + px * sc, y + py * sc) for px, py in pts], rgba(col, a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in [(-45, -95), (10, -97), (10, -52), (-90, -52)]], rgba(BG, a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in [(25, -97), (82, -97), (130, -52), (25, -52)]], rgba(BG, a))
    for wx in (-140, 140):
        r1, r2 = 52 * sc, 38 * sc
        d.ellipse(p(x + wx * sc - r1, y + 40 * sc - r1, x + wx * sc + r1, y + 40 * sc + r1), fill=rgba(BG, a))
        d.ellipse(p(x + wx * sc - r2, y + 40 * sc - r2, x + wx * sc + r2, y + 40 * sc + r2), fill=rgba((70, 78, 92), a))

def stamp(d, cx, cy, word, col, k):
    if k <= 0:
        return
    s = 1.6 - 0.6 * clamp(k)
    f = FL("InterDisplay-Black.otf", max(1, int(70 * s)))
    tw = d.textlength(word, font=f) / S
    d.rounded_rectangle(p(cx - tw / 2 - 26 * s, cy - 50 * s, cx + tw / 2 + 26 * s, cy + 50 * s), radius=18 * S,
                        outline=rgba(col, clamp(k)), width=int(8 * S))
    text_c(d, cx, cy - 42 * s, word, f, rgba(col, clamp(k)))

# ---------- scene 1: the myth ----------
def vis_fm_hook(d, lt, t):
    a = ease_out(lt / 0.35)
    sedan(d, 450, 330, 1.15, WHITE, a)
    bolt(d, 450, 300, 0.45, rgba(ACC, a))
    fl = ease_out((lt - 0.3) / 0.6) * (1 - ease_inout((lt - 2.4) / 0.6))
    if fl > 0:
        for i, x in enumerate([330, 450, 570]):
            flame(d, x, 250, 170 * fl, t, fl * 0.95, seed=i * 2.1)
    text_c(d, 450, 520, "“EVs CATCH FIRE", FL("InterDisplay-Black.otf", 54), rgba(WHITE, a))
    text_c(d, 450, 585, "ALL THE TIME”", FL("InterDisplay-Black.otf", 54), rgba(WHITE, a))
    stamp(d, 450, 740, "MYTH?", ACC2, back_out((lt - 2.6) / 0.4))

# ---------- dot grid helper ----------
def dot_grid(d, x0, y0, cols, rows, gap, r, lit, a, col_on, col_off=DARK):
    for k in range(cols * rows):
        cx = x0 + (k % cols) * gap
        cy = y0 + (k // cols) * gap
        on = k in lit
        d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=rgba(col_on if on else col_off, a * (1 if on else 0.7)))

# ---------- scene 2: Sweden EV rate ----------
def vis_fm_sweden(d, lt, t):
    a = ease_out(lt / 0.35)
    panel(d, 70, 60, 830, 820, a)
    text_c(d, 450, 85, "SWEDEN · 2022", FL("InterDisplay-Black.otf", 40), rgba(WHITE, a))
    text_c(d, 450, 140, "electric cars that caught fire", FL("Inter-SemiBold.otf", 28), rgba(MUTED, a))
    k = ease_out((lt - 0.6) / 1.6)
    text_c(d, 450, 200, f"{0.004 * k:.3f}%", FL("InterDisplay-Black.otf", 110), rgba(ACC, a))
    # 1 in 25,000 visual: 25x14 grid = 350 dots, each ~71 cars; one dot lit
    g = ease_out((lt - 1.4) / 1.0)
    dot_grid(d, 150, 380, 25, 14, 25, 7.5, set(), a * g, ACC)
    pk = back_out((lt - 2.6) / 0.5)
    if pk > 0:
        cx, cy = 150 + 12 * 25, 380 + 7 * 25
        rr = 7.5 + 10 * (0.5 + 0.5 * math.sin(t * 6))
        d.ellipse(p(cx - rr - 6, cy - rr - 6, cx + rr + 6, cy + rr + 6), outline=rgba(FIRE, clamp(pk)), width=int(4 * S))
        d.ellipse(p(cx - 9, cy - 9, cx + 9, cy + 9), fill=rgba(FIRE, clamp(pk)))
    text_c(d, 450, 342, "each dot ≈ 70 cars", FL("Inter-SemiBold.otf", 24), rgba(MUTED, a * g))
    text_c(d, 450, 745, "≈ 1 IN 25,000", FL("InterDisplay-Black.otf", 44), rgba(WHITE, ease_out((lt - 3.0) / 0.4)))

# ---------- scene 3: comparison bars ----------
def vis_fm_compare(d, lt, t):
    a = ease_out(lt / 0.35)
    panel(d, 70, 60, 830, 820, a)
    text_c(d, 450, 85, "FIRE RATE · SWEDEN 2022", FL("InterDisplay-Black.otf", 36), rgba(WHITE, a))
    base, top = 640, 270
    full = base - top
    k1 = ease_out((lt - 0.2) / 0.5)
    k2 = ease_inout((lt - 0.6) / 1.8)
    # EV bar (1 unit) vs gas/diesel (20 units)
    hev = full / 20 * k1
    hgas = full * k2
    for x, h, col in [(280, hev, ACC), (620, hgas, ACC2)]:
        d.rounded_rectangle(p(x - 85 + 6, base - max(h, 8) + 8, x + 85 + 6, base + 8), radius=16 * S, fill=rgba((0, 0, 0), 0.3 * a))
        d.rounded_rectangle(p(x - 85, base - max(h, 8), x + 85, base), radius=16 * S, fill=rgba(col, a))
    text_c(d, 280, base - hev - 70, "0.004%", FL("InterDisplay-Black.otf", 40), rgba(ACC, a * k1))
    text_c(d, 620, base - hgas - 70, f"{0.004 + 0.076 * k2:.3f}%", FL("InterDisplay-Black.otf", 40), rgba(ACC2, a))
    d.line(p(150, base, 750, base), fill=rgba(DARK, a), width=int(4 * S))
    fs = FL("InterDisplay-Bold.otf", 30)
    text_c(d, 280, 660, "ELECTRIC", fs, rgba(WHITE, a))
    text_c(d, 620, 660, "GAS + DIESEL", fs, rgba(WHITE, a))
    m = back_out((lt - 2.5) / 0.5)
    if m > 0:
        text_c(d, 390, 330, "≈20×", FL("InterDisplay-Black.otf", max(1, int(80 * m))), rgba(WHITE, clamp(m)))
    c = ease_out((lt - 3.6) / 0.4)
    text_c(d, 450, 735, "* gas/diesel total includes arson", FL("Inter-SemiBold.otf", 28), rgba(MUTED, c))

# ---------- scene 4: thermal runaway cell chain ----------
def vis_fm_runaway(d, lt, t):
    a = ease_out(lt / 0.35)
    text_c(d, 450, 70, "INSIDE THE PACK", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, a))
    cols, rows = 6, 3
    cw, ch, gx, gy = 105, 150, 18, 22
    x0 = 450 - (cols * cw + (cols - 1) * gx) / 2
    y0 = 150
    start = 2.6
    for r in range(rows):
        for c in range(cols):
            dist = math.hypot(c - 1, r - 1)
            ign = start + dist * 0.55
            h = clamp((lt - ign) / 0.6) if lt > ign else 0
            if (c, r) == (1, 1):
                h = clamp((lt - 1.2) / 1.0)
            base = (60, 68, 80)
            col = tuple(int(base[i] + (FIRE[i] - base[i]) * h) for i in range(3))
            x = x0 + c * (cw + gx); y = y0 + r * (ch + gy)
            d.rounded_rectangle(p(x + 5, y + 8, x + cw + 5, y + ch + 8), radius=14 * S, fill=rgba((0, 0, 0), 0.3 * a))
            d.rounded_rectangle(p(x, y, x + cw, y + ch), radius=14 * S, fill=rgba(col, a))
            d.rounded_rectangle(p(x + cw * 0.3, y - 10, x + cw * 0.7, y + 4), radius=4 * S, fill=rgba(MUTED, a))
            if h > 0.6:
                gl = 0.5 + 0.5 * math.sin(t * 9 + c + r)
                d.rounded_rectangle(p(x - 6, y - 6, x + cw + 6, y + ch + 6), radius=18 * S, outline=rgba((255, 200, 80), (h - 0.6) * 2 * gl * a), width=int(4 * S))
    # damage marker on first cell
    dm = back_out((lt - 0.4) / 0.4)
    if dm > 0:
        cx = x0 + 1 * (cw + gx) + cw / 2; cy = y0 + 1 * (ch + gy) + ch / 2
        d.line(p(cx - 30, cy - 40, cx + 5, cy - 5, cx - 10, cy + 5, cx + 30, cy + 40), fill=rgba(WHITE, clamp(dm)), width=int(7 * S))
    # temperature readout
    tk = ease_inout((lt - 1.0) / 4.0)
    text_c(d, 450, 690, "THERMAL RUNAWAY", FL("InterDisplay-Black.otf", 62), rgba(FIRE, ease_out((lt - 3.0) / 0.4)))
    text_c(d, 450, 775, "heat → neighbor → heat → neighbor", FL("Inter-SemiBold.otf", 28), rgba(MUTED, ease_out((lt - 3.4) / 0.4)))

# ---------- scene 5: water counter ----------
def vis_fm_water(d, lt, t):
    a = ease_out(lt / 0.35)
    # left: "RARE" tile, right: "STUBBORN" tile
    k1 = ease_out((lt - 0.1) / 0.4)
    d.rounded_rectangle(p(110, 60, 430, 150), radius=24 * S, fill=rgba(ACC, k1))
    text_c(d, 270, 82, "RARE", FL("InterDisplay-Black.otf", 44), rgba(BG, k1))
    k2 = ease_out((lt - 0.6) / 0.4)
    d.rounded_rectangle(p(470, 60, 790, 150), radius=24 * S, fill=rgba(FIRE, k2))
    text_c(d, 630, 82, "STUBBORN", FL("InterDisplay-Black.otf", 44), rgba(BG, k2))
    # tank filling
    tx0, ty0, tx1, ty1 = 300, 210, 600, 640
    panel(d, tx0, ty0, tx1, ty1, a, outline=WATER)
    lvl = ease_inout((lt - 1.4) / 3.0)
    top = ty1 - 14 - (ty1 - ty0 - 28) * lvl
    if lvl > 0.01:
        pts = [(tx0 + 14, ty1 - 14)]
        for k in range(31):
            x = tx0 + 14 + (tx1 - tx0 - 28) * k / 30
            pts.append((x, top + 8 * math.sin(k / 30 * 2 * math.pi * 2 + t * 4)))
        pts.append((tx1 - 14, ty1 - 14))
        poly(d, pts, rgba(WATER, 0.85 * a))
    # falling drops above tank
    for i in range(5):
        ph = (t * 1.3 + i / 5) % 1.0
        x = 360 + i * 45; y = 170 + ph * 60
        d.ellipse(p(x - 7, y - 7, x + 7, y + 9), fill=rgba(WATER, a * (1 - ph) * clamp(lvl * 5)))
    n = int(30000 * lvl)
    text_c(d, 450, 665, f"{n:,}+ GALLONS", FL("InterDisplay-Black.otf", 64), rgba(WHITE, a))
    text_c(d, 450, 750, "one EV crash fire · Texas (NFPA)", FL("Inter-SemiBold.otf", 28), rgba(MUTED, ease_out((lt - 2.0) / 0.4)))

# ---------- outro ----------
def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

def vis_fm_outro(d, lt, t):
    dur = sdur("fm_outro")
    cut = dur * 0.6
    if lt < cut:
        a = 1 - ease_inout((lt - cut + 0.3) / 0.3)
        # headline size vs actual frequency
        k = ease_out((lt - 0.2) / 0.6)
        panel(d, 90, 90, 810, 330, a)
        text_c(d, 450, 110, "HOW IT FEELS", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
        d.rounded_rectangle(p(140, 170, 140 + 620 * k, 270), radius=20 * S, fill=rgba(FIRE, a))
        text_c(d, 450, 190, "HEADLINES", FL("InterDisplay-Black.otf", 50), rgba(BG, a * k))
        k2 = ease_out((lt - 1.2) / 0.6)
        panel(d, 90, 380, 810, 620, a)
        text_c(d, 450, 400, "HOW OFTEN IT HAPPENS", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
        d.rounded_rectangle(p(140, 460, 140 + 40 * k2, 560), radius=20 * S, fill=rgba(ACC, a * k2))
        text_c(d, 480, 480, "RARE", FL("InterDisplay-Black.otf", 50), rgba(ACC, a * k2))
        q = back_out((lt - 2.2) / 0.5)
        if q > 0:
            text_c(d, 450, 680, "WHAT ELSE DO WE MISJUDGE?", FL("InterDisplay-Black.otf", 44), rgba(WHITE, a * clamp(q)))
    else:
        end_card(d, lt, cut)

VIS.update({"fm_hook": vis_fm_hook, "fm_sweden": vis_fm_sweden, "fm_compare": vis_fm_compare,
            "fm_runaway": vis_fm_runaway, "fm_water": vis_fm_water, "fm_outro": vis_fm_outro})
