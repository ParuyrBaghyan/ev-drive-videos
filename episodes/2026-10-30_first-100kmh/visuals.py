# Episode visuals: History — La Jamais Contente, the first car past 100 km/h (electric, 1899).
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
BRASS = (214, 170, 92)

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

def BF(n): return FL("InterDisplay-Black.otf", n)
def BD(n): return FL("InterDisplay-Bold.otf", n)

# ---------- the 1899 torpedo car (nose to the right) ----------
WHEEL_X = (-150, 150)
def spoked_wheel(d, cx, cy, r, ang, a):
    d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=rgba((24, 29, 38), a))
    arc(d, cx, cy, r - 5, 0, 360, rgba(MUTED, a), 9)
    for k in range(12):
        an = ang + k * math.pi / 6
        d.line(p(cx, cy, cx + math.cos(an) * (r - 8), cy + math.sin(an) * (r - 8)), fill=rgba(MUTED, a * 0.8), width=int(3 * S))
    d.ellipse(p(cx - 9, cy - 9, cx + 9, cy + 9), fill=rgba(BRASS, a))

def torpedo_pts(x, y, sc):
    pts = []
    n = 40
    for i in range(n + 1):           # top edge, tail (left) -> nose (right)
        u = -1 + 2 * i / n
        h = 52 * (max(0.0, 1 - u * u) ** 0.5) * (0.62 + 0.38 * (u + 1) / 2) + (8 if u > 0.9 else 0) * 0
        pts.append((x + 235 * u * sc, y - h * sc))
    for i in range(n, -1, -1):       # bottom edge back
        u = -1 + 2 * i / n
        h = 40 * (max(0.0, 1 - u * u) ** 0.5) * (0.7 + 0.3 * (u + 1) / 2)
        pts.append((x + 235 * u * sc, y + h * sc))
    return pts

def old_car(d, x, y, sc, a=1.0, ang=0.0, parts=(1, 1, 1), body_col=None, body_alpha=1.0):
    """parts = alpha multipliers for (wheels, body, driver)."""
    aw, ab, ad = [a * clamp(v) for v in parts]
    wy = y + 48 * sc
    # shadow
    d.ellipse(p(x - 250 * sc, wy + 50 * sc, x + 250 * sc, wy + 72 * sc), fill=rgba((0, 0, 0), 0.35 * aw))
    for wx in WHEEL_X:
        spoked_wheel(d, x + wx * sc, wy, 62 * sc, ang, aw)
    # chassis rail
    d.line(p(x - 205 * sc, y + 26 * sc, x + 205 * sc, y + 26 * sc), fill=rgba(DARK, ab), width=int(10 * S * sc))
    # driver (sits high, behind the middle)
    if ad > 0:
        hx, hy = x - 30 * sc, y - 108 * sc
        d.rounded_rectangle(p(hx - 26 * sc, hy + 18 * sc, hx + 26 * sc, hy + 70 * sc), radius=14 * S * sc, fill=rgba((70, 78, 92), ad))
        d.ellipse(p(hx - 22 * sc, hy - 24 * sc, hx + 22 * sc, hy + 20 * sc), fill=rgba((150, 158, 170), ad))
        d.chord(p(hx - 25 * sc, hy - 30 * sc, hx + 25 * sc, hy + 8 * sc), 180, 360, fill=rgba((70, 78, 92), ad))
        d.line(p(hx + 15 * sc, hy + 34 * sc, hx + 70 * sc, hy + 40 * sc), fill=rgba(MUTED, ad), width=int(6 * S * sc))
    col = body_col or (205, 212, 222)
    if ab > 0:
        poly(d, torpedo_pts(x, y, sc), rgba(col, ab * body_alpha))
        # highlight stripe for depth
        poly(d, [(px, py + 14 * sc) for px, py in torpedo_pts(x, y - 8 * sc, sc * 0.93)][:41] +
                [(px, py + 4 * sc) for px, py in torpedo_pts(x, y - 8 * sc, sc * 0.93)][:41][::-1],
             rgba(WHITE, 0.55 * ab * body_alpha))
        # seat opening
        d.rounded_rectangle(p(x - 70 * sc, y - 58 * sc, x + 10 * sc, y - 44 * sc), radius=7 * S * sc, fill=rgba(BG, ab))

def speed_lines(d, t, x0, x1, ys, a, col=MUTED, speed=900):
    for i, yy in enumerate(ys):
        L_ = 90 + 40 * (i % 3)
        off = (t * speed + i * 137) % (x1 - x0 + L_)
        xs = x1 - off
        d.line(p(max(x0, xs), yy, min(x1, xs + L_), yy), fill=rgba(col, a), width=int(6 * S))

# ---------- scene 1: hook — speedometer to 100 ----------
def vis_jc_hook(d, lt, t):
    a = ease_out(lt / 0.35)
    cx, cy, r = 450, 340, 230
    k = ease_inout((lt - 0.3) / 2.6)
    v = 106 * k
    a0, a1 = 160, 380
    arc(d, cx, cy, r, a0, a1, rgba(DARK, a), 34)
    if v > 0.5:
        arc(d, cx, cy, r, a0, a0 + (a1 - a0) * v / 120, rgba(ACC if v >= 100 else WHITE, a), 34)
    # 100 marker
    am = math.radians(a0 + (a1 - a0) * 100 / 120)
    d.line(p(cx + math.cos(am) * (r - 40), cy + math.sin(am) * (r - 40), cx + math.cos(am) * (r + 40), cy + math.sin(am) * (r + 40)),
           fill=rgba(ACC2, a), width=int(8 * S))
    text_c(d, cx + math.cos(am) * (r + 80) - 10, cy + math.sin(am) * (r + 80) - 22, "100", BF(40), rgba(ACC2, a))
    # needle
    an = math.radians(a0 + (a1 - a0) * v / 120)
    d.line(p(cx, cy, cx + math.cos(an) * (r - 50), cy + math.sin(an) * (r - 50)), fill=rgba(WHITE, a), width=int(10 * S))
    d.ellipse(p(cx - 22, cy - 22, cx + 22, cy + 22), fill=rgba(WHITE, a))
    text_c(d, cx, cy + 40, f"{int(v)}", BF(110), rgba(ACC if v >= 100 else WHITE, a))
    text_c(d, cx, cy + 165, "KM/H", BD(34), rgba(MUTED, a))
    # car racing below
    speed_lines(d, t, 60, 840, [715, 750, 795, 830], a * 0.6 * clamp(k * 3))
    old_car(d, 450 + math.sin(t * 9) * 3, 750, 0.62, a, ang=t * 14)
    # badge
    kb = back_out((lt - 2.9) / 0.5)
    if kb > 0:
        bx, by = 450, 618
        d.rounded_rectangle(p(bx - 190, by - 34, bx + 190, by + 34), radius=34 * S, fill=rgba(ACC, clamp(kb)))
        bolt(d, bx - 160, by + 2, 0.32, rgba(BG, clamp(kb)))
        text_c(d, bx + 22, by - 24, "ELECTRIC · 1899", BF(38), rgba(BG, clamp(kb)))

# ---------- scene 2: record duel bar chart ----------
RECS = [(63.2, "DEC", ACC2), (66.7, "JAN", ACC), (70.3, "JAN", ACC2), (80.4, "JAN", ACC), (92.8, "MAR", ACC2), (105.9, "APR", ACC)]
def vis_jc_duel(d, lt, t):
    a = ease_out(lt / 0.35)
    panel(d, 50, 70, 850, 830, a)
    text_c(d, 450, 95, "WORLD SPEED RECORD", BF(46), rgba(WHITE, a))
    text_c(d, 450, 152, "Dec 1898 → Apr 1899  (km/h)", BD(30), rgba(MUTED, a))
    base, top = 640, 250
    for i, (v, m, col) in enumerate(RECS):
        k = ease_out((lt - 0.3 - 0.45 * i) / 0.6)
        x = 140 + i * 124
        h = (base - top) * v / 110 * k
        d.rounded_rectangle(p(x - 44, base - (base - top), x + 44, base), radius=14 * S, fill=rgba(DARK, 0.45 * a))
        if h > 4:
            d.rounded_rectangle(p(x - 38, base - h + 8, x + 50, base + 8), radius=14 * S, fill=rgba((0, 0, 0), 0.3 * a))
            d.rounded_rectangle(p(x - 44, base - h, x + 44, base), radius=14 * S, fill=rgba(col, a))
            bolt(d, x, base - 34, 0.3, rgba(BG, a * clamp(k * 2)))
            text_c(d, x, base - h - 48, f"{v * clamp(k * 1.1):.0f}", BF(36), rgba(col, a * clamp(k * 2)))
        text_c(d, x, base + 14, m, BD(28), rgba(MUTED, a))
    # legend
    kl = ease_out((lt - 2.0) / 0.5)
    d.ellipse(p(110, 712, 140, 742), fill=rgba(ACC2, kl))
    d.text(p(152, 707), "CHASSELOUP-LAUBAT", font=BD(30), fill=rgba(WHITE, kl))
    d.ellipse(p(560, 712, 590, 742), fill=rgba(ACC, kl))
    d.text(p(602, 707), "JENATZY", font=BD(30), fill=rgba(WHITE, kl))
    kt = back_out((lt - 3.0) / 0.5)
    if kt > 0:
        d.rounded_rectangle(p(270, 768, 630, 818), radius=25 * S, fill=rgba(ACC, clamp(kt)))
        text_c(d, 450, 774, "ALL 6 CARS ELECTRIC", BF(32), rgba(BG, clamp(kt)))

# ---------- scene 3: the car is assembled ----------
def callout(d, x0, y0, x1, y1, label, k, col=ACC, left=False):
    if k <= 0:
        return
    kk = clamp(k)
    d.ellipse(p(x0 - 9, y0 - 9, x0 + 9, y0 + 9), fill=rgba(col, kk))
    xm = x0 + (x1 - x0) * kk; ym = y0 + (y1 - y0) * kk
    d.line(p(x0, y0, xm, ym), fill=rgba(col, kk), width=int(4 * S))
    text_c(d, x1, y1 - 46 if y1 < y0 else y1 + 8, label, BD(30), rgba(WHITE, kk))

def vis_jc_car(d, lt, t):
    a = ease_out(lt / 0.3)
    parts = (ease_out((lt - 0.1) / 0.4), ease_out((lt - 0.5) / 0.5), ease_out((lt - 1.0) / 0.4))
    old_car(d, 450, 360, 1.12, a, ang=lt * 1.2, parts=parts)
    callout(d, 690, 345, 720, 210, "TORPEDO", ease_out((lt - 1.4) / 0.5))
    callout(d, 300, 330, 200, 210, "LIGHT ALLOY", ease_out((lt - 1.9) / 0.5), col=ACC2, left=False)
    kn = back_out((lt - 2.5) / 0.5)
    if kn > 0:
        a2 = clamp(kn)
        panel(d, 110, 590, 790, 790, a2)
        text_c(d, 450, 612, "LA JAMAIS CONTENTE", BF(54), rgba(ACC, a2))
        text_c(d, 450, 692, "“the never satisfied”", BD(38), rgba(MUTED, a2))

# ---------- scene 4: cutaway — motors + batteries ----------
def vis_jc_inside(d, lt, t):
    a = ease_out(lt / 0.3)
    cx, cy, sc = 450, 300, 1.12
    old_car(d, cx, cy, sc, a, ang=t * 2, parts=(1, 1, 0.5), body_col=(120, 132, 150), body_alpha=0.28)
    # battery cells filling the torpedo
    cells = []
    for row in range(3):
        for col in range(9):
            x = cx - 175 * sc + col * 40 * sc
            y = cy - 38 * sc + row * 30 * sc
            u = (x - cx) / (235 * sc)
            if abs(u) < 0.86 and not (row == 0 and -0.35 < u < 0.08):
                cells.append((x, y))
    nshow = int(len(cells) * ease_inout((lt - 0.4) / 1.6))
    for i, (x, y) in enumerate(cells[:nshow]):
        d.rounded_rectangle(p(x, y, x + 34 * sc, y + 24 * sc), radius=5 * S, fill=rgba(ACC, a * 0.9))
        d.rectangle(p(x + 12 * sc, y - 4 * sc, x + 22 * sc, y), fill=rgba(ACC, a * 0.9))
    # motors at the rear wheel (left = rear)
    km = back_out((lt - 0.9) / 0.5)
    mx, my = cx + WHEEL_X[0] * sc + 70 * sc, cy + 48 * sc
    if km > 0:
        kk = clamp(km)
        rr = 30 * sc * kk
        d.ellipse(p(mx - rr, my - rr, mx + rr, my + rr), fill=rgba(ACC2, kk), outline=rgba(WHITE, kk), width=int(3 * S))
        # chain to wheel hub
        wx = cx + WHEEL_X[0] * sc
        for side in (-1, 1):
            d.line(p(mx, my + side * 16 * sc, wx, my + side * 9), fill=rgba(BRASS, kk), width=int(4 * S))
        # moving chain dots
        for j in range(5):
            f = ((t * 1.5 + j / 5) % 1.0)
            px = mx + (wx - mx) * f
            d.ellipse(p(px - 4, my - 16 * sc - 4, px + 4, my - 16 * sc + 4), fill=rgba(WHITE, kk))
    callout(d, mx, my, 300, 470, "2 MOTORS · 1 PER WHEEL", ease_out((lt - 1.3) / 0.5), col=ACC2)
    # weight bar
    kw = ease_out((lt - 2.0) / 0.4)
    if kw > 0:
        y0 = 640
        text_c(d, 450, y0 - 40 + 0 * kw, "≈ 1,450 KG TOTAL", BF(40), rgba(WHITE, kw))
        d.rounded_rectangle(p(110, y0 + 20, 790, y0 + 90), radius=35 * S, fill=rgba(DARK, kw))
        kf = ease_inout((lt - 2.3) / 1.0)
        if kf > 0.05:
            d.rounded_rectangle(p(110, y0 + 20, 110 + 340 * kf, y0 + 90), radius=35 * S, fill=rgba(ACC, kw))
        text_c(d, 280, y0 + 34, "BATTERIES", BF(32), rgba(BG, kw * clamp(kf * 2 - 0.6)))
        text_c(d, 620, y0 + 34, "EVERYTHING ELSE", BD(30), rgba(MUTED, kw))
        text_c(d, 450, y0 + 110, "≈ HALF", BF(44), rgba(ACC, kw * clamp(kf * 2 - 1)))

# ---------- scene 5: the record run ----------
def vis_jc_record(d, lt, t):
    a = ease_out(lt / 0.3)
    k = ease_inout((lt - 0.2) / 2.6)
    v = 105.88 * k
    text_c(d, 450, 70, f"{v:.1f}" if k < 1 else "105.88", BF(170), rgba(ACC if v >= 100 else WHITE, a))
    text_c(d, 450, 270, "KM/H", BD(40), rgba(MUTED, a))
    km = ease_out((lt - 3.2) / 0.5)
    d.rounded_rectangle(p(250, 330, 650, 400), radius=35 * S, fill=rgba(ACC2, km))
    text_c(d, 450, 340, "= 65.8 MPH", BF(42), rgba(BG, km))
    # track + car crossing a 100 km/h ribbon
    ty = 640
    d.line(p(40, ty + 82, 860, ty + 82), fill=rgba(DARK, a), width=int(6 * S))
    speed_lines(d, t, 40, 860, [480, 520, 575, 610, 660], a * 0.7 * clamp(k * 3), speed=1400)
    xcar = 160 + 420 * ease_inout((lt - 0.2) / 3.0)
    rib_x = 650
    broken = xcar + 0.62 * 235 > rib_x
    if not broken:
        d.line(p(rib_x, 470, rib_x, ty + 82), fill=rgba(ACC, a), width=int(6 * S))
    else:
        f = clamp((lt - 1.0))
        d.line(p(rib_x, 470, rib_x + 40 * f, 520 + 60 * f), fill=rgba(ACC, a * (1 - f * 0.6)), width=int(6 * S))
        d.line(p(rib_x, ty + 82, rib_x + 50 * f, ty + 30 - 30 * f), fill=rgba(ACC, a * (1 - f * 0.6)), width=int(6 * S))
    old_car(d, xcar, ty, 0.62, a, ang=t * 18)
    text_c(d, 450, 760, "ACHÈRES, NEAR PARIS · 29 APRIL 1899", BD(30), rgba(MUTED, a))

# ---------- scene 6: timeline electric -> steam -> gas ----------
def steam_icon(d, x, y, s, col):
    for dx, dy, r in ((-18, 6, 20), (6, -8, 26), (28, 8, 18)):
        d.ellipse(p(x + (dx - r) * s, y + (dy - r) * s, x + (dx + r) * s, y + (dy + r) * s), fill=col)

def drop_icon(d, x, y, s, col):
    poly(d, [(x, y - 34 * s), (x + 22 * s, y + 2 * s), (x - 22 * s, y + 2 * s)], col)
    d.ellipse(p(x - 23 * s, y - 14 * s, x + 23 * s, y + 30 * s), fill=col)

TL = [("1899", "ELECTRIC", "105.9 km/h", ACC, "bolt"), ("APR 1902", "STEAM", "120.8 km/h", WHITE, "steam"),
      ("NOV 1902", "GAS", "122.4 km/h", ACC2, "drop")]
def vis_jc_after(d, lt, t):
    a = ease_out(lt / 0.3)
    xL = 150
    y0, gap = 150, 230
    kline = ease_inout((lt - 0.2) / 2.6)
    d.line(p(xL, y0, xL, y0 + 2 * gap), fill=rgba(DARK, a), width=int(10 * S))
    d.line(p(xL, y0, xL, y0 + 2 * gap * kline), fill=rgba(WHITE, a), width=int(10 * S))
    for i, (yr, kind, spd, col, ic) in enumerate(TL):
        k = back_out((lt - 0.2 - 1.1 * i) / 0.5)
        if k <= 0:
            continue
        kk = clamp(k)
        y = y0 + i * gap
        rr = 56 * kk
        d.ellipse(p(xL - rr, y - rr, xL + rr, y + rr), fill=rgba(col, kk))
        if ic == "bolt": bolt(d, xL, y, 0.48 * kk, rgba(BG, kk))
        elif ic == "steam": steam_icon(d, xL, y, 0.9 * kk, rgba(BG, kk))
        else: drop_icon(d, xL, y, 0.9 * kk, rgba(BG, kk))
        panel(d, 240, y - 80, 830, y + 80, kk)
        d.text(p(275, y - 62), kind, font=BF(52), fill=rgba(col, kk))
        d.text(p(275, y + 6), yr, font=BD(32), fill=rgba(MUTED, kk))
        f = BF(40); tw = d.textlength(spd, font=f) / S
        d.text(p(800 - tw, y - 24), spd, font=f, fill=rgba(WHITE, kk))
    kb = back_out((lt - 1.0) / 0.5)
    if kb > 0:
        kk = clamp(kb)
        d.rounded_rectangle(p(18, y0 + gap / 2 - 30, 112, y0 + gap / 2 + 30), radius=18 * S, fill=rgba(ACC, kk))
        text_c(d, 65, y0 + gap / 2 - 21, "3 YRS", BF(26), rgba(BG, kk))
    kg = ease_out((lt - 3.4) / 0.5)
    if kg > 0:
        text_c(d, 450, 760, "THEN GAS RULED FOR A CENTURY", BF(38), rgba(ACC2, kg))

# ---------- outro ----------
def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

def vis_jc_outro(d, lt, t):
    dur = sdur("jc_outro")
    cut = dur * 0.5
    if lt < cut:
        a = 1 - ease_inout((lt - cut + 0.3) / 0.3)
        k1 = back_out(lt / 0.5); k2 = back_out((lt - 0.8) / 0.5)
        for (x, lab, k) in ((220, "1899", k1), (680, "TODAY", k2)):
            if k <= 0:
                continue
            kk = clamp(k) * a
            d.ellipse(p(x - 110, 200, x + 110, 420), fill=rgba(PANEL, kk), outline=rgba(ACC, kk), width=int(5 * S))
            bolt(d, x, 312, 0.9 * clamp(k), rgba(ACC, kk))
            text_c(d, x, 450, lab, BF(52), rgba(WHITE, kk))
        # the century gap arc
        kg = ease_inout((lt - 1.2) / 1.0)
        if kg > 0:
            arc(d, 450, 400, 300, 215, 215 + 110 * kg, rgba(ACC2, a), 8)
        kq = back_out((lt - 2.0) / 0.5)
        if kq > 0:
            text_c(d, 450, 230, "?", FL("InterDisplay-Black.otf", max(1, int(110 * max(kq, 0.01)))), rgba(ACC2, a * clamp(kq)))
        text_c(d, 450, 590, "FASTEST FIRST", BF(76), rgba(ACC, a * ease_out((lt - 0.4) / 0.4)))
    else:
        end_card(d, lt, cut)

VIS.update({"jc_hook": vis_jc_hook, "jc_duel": vis_jc_duel, "jc_car": vis_jc_car, "jc_inside": vis_jc_inside,
            "jc_record": vis_jc_record, "jc_after": vis_jc_after, "jc_outro": vis_jc_outro})
