# Episode visuals: The numbers — aerodynamic drag and EV range.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
AIR = (110, 190, 255)

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

def panel(d, x0, y0, x1, y1, a=1.0):
    d.rounded_rectangle(p(x0 + 6, y0 + 10, x1 + 6, y1 + 10), radius=30 * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=30 * S, fill=rgba(PANEL, 0.92 * a), outline=rgba(DARK, a), width=int(4 * S))

def sleek_car(d, x, y, sc, col, a=1.0):
    """Low teardrop EV profile, nose to the left (air comes from the left)."""
    pts = [(-250, 30), (-252, 0), (-235, -22), (-150, -48), (-70, -92), (30, -100),
           (120, -80), (215, -45), (250, -10), (252, 30)]
    poly(d, [(x + px * sc, y + py * sc) for px, py in pts], rgba(col, a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in [(-120, -50), (-58, -84), (20, -90), (20, -52)]], rgba(BG, a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in [(34, -88), (110, -74), (165, -52), (34, -52)]], rgba(BG, a))
    for wx in (-150, 150):
        r1, r2 = 50 * sc, 38 * sc
        d.ellipse(p(x + wx * sc - r1, y + 30 * sc - r1, x + wx * sc + r1, y + 30 * sc + r1), fill=rgba(BG, a))
        d.ellipse(p(x + wx * sc - r2, y + 30 * sc - r2, x + wx * sc + r2, y + 30 * sc + r2), fill=rgba((70, 78, 92), a))
    d.line(p(x - 248 * sc, y - 6 * sc, x - 210 * sc, y - 18 * sc), fill=rgba(ACC, a), width=int(7 * S * sc))

def boxy_car(d, x, y, sc, col, a=1.0):
    """Tall boxy SUV profile, nose to the left."""
    pts = [(-240, 35), (-240, -40), (-215, -60), (-150, -66), (-100, -140), (200, -140),
           (235, -120), (240, 35)]
    poly(d, [(x + px * sc, y + py * sc) for px, py in pts], rgba(col, a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in [(-90, -125), (40, -125), (40, -70), (-130, -70)]], rgba(BG, a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in [(55, -125), (190, -125), (190, -70), (55, -70)]], rgba(BG, a))
    for wx in (-145, 150):
        r1, r2 = 52 * sc, 40 * sc
        d.ellipse(p(x + wx * sc - r1, y + 35 * sc - r1, x + wx * sc + r1, y + 35 * sc + r1), fill=rgba(BG, a))
        d.ellipse(p(x + wx * sc - r2, y + 35 * sc - r2, x + wx * sc + r2, y + 35 * sc + r2), fill=rgba((70, 78, 92), a))

def streamlines(d, t, x0, x1, ys, a=1.0, bend=None, speed=260, col=AIR, w=5):
    """Moving dashed air lines; bend(x, y) returns the y offset to flow around a body."""
    for i, y in enumerate(ys):
        pts = []
        for k in range(0, 61):
            x = x0 + (x1 - x0) * k / 60
            yy = y + (bend(x, y) if bend else 0)
            pts.append((x, yy))
        seg = 9
        off = int((t * speed / ((x1 - x0) / 60)) + i * 3) % seg
        for k in range(off, 60, seg):
            q = pts[k:k + 5]
            if len(q) > 1:
                d.line([v * S for xy in q for v in xy], fill=rgba(col, a * 0.85), width=int(w * S))

def counter_text(d, x, y, s, size, col):
    text_c(d, x, y, s, FL("InterDisplay-Black.otf", size), col)

# ---------- scene 1: half the energy is air ----------
def vis_ad_hook(d, lt, t):
    a = ease_out(lt / 0.4)
    cx, cy = 450, 300
    def bend(x, y):
        dx = (x - cx) / 230
        if abs(dx) > 1.4:
            return 0
        push = math.exp(-dx * dx * 1.6) * 70
        return -push if y < cy - 10 else push * 0.25
    streamlines(d, t, 40, 860, [150, 195, 240, 380, 420], a=a, bend=bend)
    sleek_car(d, cx, cy + 40, 1.0, WHITE, a)
    # donut: share of highway energy
    k = ease_inout((lt - 0.8) / 1.6)
    dx, dy, r = 450, 640, 120
    arc(d, dx, dy, r, 0, 360, rgba(DARK, a), 46)
    if k > 0:
        arc(d, dx, dy, r, -90, -90 + 180 * k, rgba(AIR, 1), 46)
    counter_text(d, dx, dy - 32, f"~{int(round(50 * k))}%", 50, rgba(WHITE, a))
    text_c(d, 690, 615, "AIR", FL("InterDisplay-Black.otf", 44), rgba(AIR, ease_out((lt - 1.6) / 0.4)))
    text_c(d, 690, 665, "DRAG", FL("InterDisplay-Black.otf", 44), rgba(AIR, ease_out((lt - 1.6) / 0.4)))
    text_c(d, 210, 615, "EVERYTHING", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, ease_out((lt - 1.8) / 0.4)))
    text_c(d, 210, 655, "ELSE", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, ease_out((lt - 1.8) / 0.4)))
    text_c(d, 450, 790, "SHARE OF HIGHWAY ENERGY", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, a))

# ---------- bar helpers ----------
def vbar(d, x, base, w, h, col, a=1.0):
    if h <= 1:
        return
    d.rounded_rectangle(p(x - w / 2 + 6, base - h + 8, x + w / 2 + 6, base + 8), radius=14 * S, fill=rgba((0, 0, 0), 0.3 * a))
    d.rounded_rectangle(p(x - w / 2, base - h, x + w / 2, base), radius=14 * S, fill=rgba(col, a))

# ---------- scene 2: drag ∝ v² ----------
def vis_ad_square(d, lt, t):
    a = ease_out(lt / 0.35)
    panel(d, 70, 90, 830, 800, a)
    text_c(d, 450, 120, "DRAG FORCE", FL("InterDisplay-Black.otf", 46), rgba(WHITE, a))
    text_c(d, 450, 178, "grows with speed²", FL("InterDisplay-Bold.otf", 34), rgba(MUTED, a))
    base, unit = 660, 95
    # speed bars (left pair) and drag bars (right pair)
    k1 = ease_out((lt - 0.3) / 0.6)
    k2 = ease_inout((lt - 1.4) / 1.4)
    vbar(d, 200, base, 90, unit * 1 * k1, MUTED, a)
    vbar(d, 320, base, 90, unit * 2 * k2, WHITE, a)
    vbar(d, 520, base, 90, unit * 1 * k1, AIR, a)
    vbar(d, 640, base, 90, unit * 4 * k2, AIR, a)
    fs = FL("InterDisplay-Bold.otf", 28)
    text_c(d, 260, 680, "SPEED", fs, rgba(MUTED, a))
    text_c(d, 580, 680, "DRAG", fs, rgba(AIR, a))
    text_c(d, 200, 720, "1×", FL("InterDisplay-Black.otf", 34), rgba(MUTED, a))
    text_c(d, 320, 720, f"{1 + k2:.1f}×".replace(".0×", "×"), FL("InterDisplay-Black.otf", 34), rgba(WHITE, a))
    text_c(d, 520, 720, "1×", FL("InterDisplay-Black.otf", 34), rgba(AIR, a))
    val = (1 + k2) ** 2
    counter_text(d, 760, base - unit * 4 * k2 - 30 if k2 > 0.05 else 600, f"×{val:.1f}".replace(".0", "") if k2 < 1 else "×4", 64, rgba(ACC, clamp(k2 * 3)))

# ---------- scene 3: power ∝ v³ ----------
def vis_ad_cube(d, lt, t):
    a = ease_out(lt / 0.35)
    panel(d, 70, 90, 830, 800, a)
    text_c(d, 450, 120, "POWER TO BEAT DRAG", FL("InterDisplay-Black.otf", 46), rgba(WHITE, a))
    text_c(d, 450, 178, "grows with speed³", FL("InterDisplay-Bold.otf", 34), rgba(MUTED, a))
    base, unit = 690, 52
    labels = [("SPEED", 2, MUTED), ("DRAG", 4, AIR), ("POWER", 8, ACC)]
    for i, (lab, mult, col) in enumerate(labels):
        k = ease_inout((lt - 0.3 - 0.7 * i) / 0.9)
        x = 230 + i * 220
        vbar(d, x, base, 120, unit * mult * k, col, a)
        text_c(d, x, base + 18, lab, FL("InterDisplay-Bold.otf", 30), rgba(col, a))
        if k > 0.02:
            v = 1 + (mult - 1) * k
            counter_text(d, x, base - unit * mult * k - 70, f"×{int(round(v))}", 50, rgba(col if col != MUTED else WHITE, clamp(k * 2)))

# ---------- scene 4/5: drag coefficient comparison ----------
CD_ROWS = [("BOXY SUV", 0.40, ACC2, "0.35–0.45"), ("AVERAGE CAR", 0.28, WHITE, "< 0.30"), ("MERCEDES EQS", 0.20, ACC, "0.20")]
def cd_chart(d, lt, rows_shown, a, glow_last=False, t=0):
    panel(d, 50, 90, 850, 810, a)
    text_c(d, 450, 115, "DRAG COEFFICIENT (Cd)", FL("InterDisplay-Black.otf", 44), rgba(WHITE, a))
    text_c(d, 450, 170, "lower = slips through air", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, a))
    x0, xmax = 90, 810
    for i, (lab, v, col, txt) in enumerate(CD_ROWS[:rows_shown]):
        k = ease_out((lt - 0.25 - 0.9 * i) / 0.8) if not (glow_last and i < 2) else 1
        y = 250 + i * 185
        # silhouette
        if i == 0:
            boxy_car(d, 180, y + 35, 0.32, col, a * clamp(k * 2))
        else:
            sleek_car(d, 180, y + 35, 0.32, col, a * clamp(k * 2))
        text_c(d, 470, y - 8, lab, FL("InterDisplay-Bold.otf", 30), rgba(col, a * clamp(k * 2)))
        w = (xmax - 290) * (v / 0.45) * k
        by = y + 40
        d.rounded_rectangle(p(290, by, xmax, by + 46), radius=23 * S, fill=rgba(DARK, a * 0.8))
        if w > 30:
            if glow_last and i == 2:
                g = 0.5 + 0.5 * math.sin(t * 5)
                d.rounded_rectangle(p(284, by - 6, 290 + w + 6, by + 52), radius=29 * S, fill=rgba(ACC, 0.25 * g))
            d.rounded_rectangle(p(290, by, 290 + w, by + 46), radius=23 * S, fill=rgba(col, a))
        text_c(d, 470, by + 58, txt, FL("InterDisplay-Black.otf", 40), rgba(col, a * clamp(k * 2)))

def vis_ad_cd(d, lt, t):
    a = ease_out(lt / 0.35)
    cd_chart(d, lt, 2, a)

def vis_ad_eqs(d, lt, t):
    cd_chart(d, lt + 0.9 * 2, 3, 1.0, glow_last=True, t=t)

# ---------- scene 6: design details ----------
def vis_ad_design(d, lt, t):
    a = ease_out(lt / 0.35)
    def bend(x, y):
        dx = (x - 450) / 230
        if abs(dx) > 1.4:
            return 0
        return -math.exp(-dx * dx * 1.6) * 60 if y < 300 else math.exp(-dx * dx * 1.6) * 15
    streamlines(d, t, 40, 860, [170, 215, 258, 395], a=a * 0.8, bend=bend)
    sleek_car(d, 450, 330, 1.0, WHITE, a)
    items = [("FLUSH HANDLES", (440, 255), "handle"), ("SMOOTH WHEELS", (300, 360), "wheel"), ("CLOSED FRONT", (205, 320), "front")]
    for i, (lab, (hx, hy), kind) in enumerate(items):
        k = back_out((lt - 0.4 - 0.9 * i) / 0.5)
        if k <= 0:
            continue
        kk = clamp(k)
        # highlight on the car
        if kind == "handle":
            d.rounded_rectangle(p(hx - 30, hy - 7, hx + 30, hy + 7), radius=7 * S, fill=rgba(ACC, kk))
        elif kind == "wheel":
            r = 38
            d.ellipse(p(hx - r, hy - r, hx + r, hy + r), fill=rgba(ACC, kk))
            d.ellipse(p(hx - 12, hy - 12, hx + 12, hy + 12), fill=rgba(BG, kk))
        else:
            d.line(p(hx, hy - 20, hx + 18, hy - 32), fill=rgba(ACC, kk), width=int(12 * S))
        # label card underneath
        cy = 520 + i * 95
        d.rounded_rectangle(p(170, cy, 730, cy + 72), radius=36 * S, fill=rgba(PANEL, kk), outline=rgba(ACC, kk), width=int(3 * S))
        d.ellipse(p(195, cy + 18, 231, cy + 54), fill=rgba(ACC, kk))
        d.line(p(203, cy + 37, 211, cy + 45, 224, cy + 28), fill=rgba(BG, kk), width=int(6 * S))
        text_c(d, 470, cy + 14, lab, FL("InterDisplay-Black.otf", 40), rgba(WHITE, kk))
        # connector

# ---------- outro ----------
def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

def vis_ad_outro(d, lt, t):
    dur = sdur("ad_outro")
    cut = dur * 0.45
    if lt < cut:
        a = 1 - ease_inout((lt - cut + 0.3) / 0.3)
        def bend(x, y):
            dx = (x - 450) / 230
            if abs(dx) > 1.4:
                return 0
            return -math.exp(-dx * dx * 1.6) * 70 if y < 360 else math.exp(-dx * dx * 1.6) * 15
        streamlines(d, t, 40, 860, [210, 255, 300, 470], a=a, bend=bend)
        sleek_car(d, 450, 420, 1.05, WHITE, a)
        text_c(d, 450, 600, "SHAPE = RANGE", FL("InterDisplay-Black.otf", 80), rgba(ACC, a * ease_out((lt - 0.4) / 0.4)))
    else:
        end_card(d, lt, cut)

VIS.update({"ad_hook": vis_ad_hook, "ad_square": vis_ad_square, "ad_cube": vis_ad_cube,
            "ad_cd": vis_ad_cd, "ad_eqs": vis_ad_eqs, "ad_design": vis_ad_design, "ad_outro": vis_ad_outro})
