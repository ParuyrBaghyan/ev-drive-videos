# Episode visuals: electric cars ruled ~1900, then vanished. Why?
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
GREY = (92, 102, 118)
SMOKE = (150, 158, 170)

def sdur(name):
    for s in scenes:
        if s["visual"] == name:
            return s["vis_end"] - s["start"]
    return 4.0

def poly(d, pts, col):
    d.polygon(p(*[v for xy in pts for v in xy]), fill=col)

def poly_line(d, pts, col, w):
    d.line([v * S for xy in pts for v in xy], fill=col, width=int(w * S), joint="curve")

def bolt(d, bx, by, bs, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(bx + xx * bs, by + yy * bs) for xx, yy in pts], col)

def glow_circle(d, x, y, r, col, a=1.0):
    for k, al in ((1.9, 0.08), (1.5, 0.14), (1.2, 0.22)):
        d.ellipse(p(x - r * k, y - r * k, x + r * k, y + r * k), fill=rgba(col, al * a))
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=rgba(col, a))

def spoke_wheel(d, cx, cy, r, ang, col, a=1.0):
    d.ellipse(p(cx - r, cy - r, cx + r, cy + r), outline=rgba(col, a), width=int(7 * S))
    for k in range(10):
        aa = ang + k * math.pi / 5
        d.line(p(cx, cy, cx + math.cos(aa) * r * 0.92, cy + math.sin(aa) * r * 0.92), fill=rgba(col, 0.8 * a), width=int(3 * S))
    d.ellipse(p(cx - 8, cy - 8, cx + 8, cy + 8), fill=rgba(col, a))

def vintage_car(d, x, y, sc, body, a=1.0, ang=0.0, ev=True):
    """Tall early-1900s car ('horseless carriage'), side view. (x, y) = ground centre."""
    c = rgba(body, a)
    wr = 52 * sc
    # shadow
    d.ellipse(p(x - 190 * sc, y - 8 * sc, x + 190 * sc, y + 10 * sc), fill=rgba((0, 0, 0), 0.35 * a))
    # chassis + body
    d.rounded_rectangle(p(x - 175 * sc, y - wr - 30 * sc, x + 175 * sc, y - wr - 6 * sc), radius=int(8 * S * sc), fill=c)
    d.rounded_rectangle(p(x - 150 * sc, y - wr - 130 * sc, x + 60 * sc, y - wr - 24 * sc), radius=int(18 * S * sc), fill=c)
    # bench seat back + roof posts + canopy
    d.rounded_rectangle(p(x - 140 * sc, y - wr - 205 * sc, x + 70 * sc, y - wr - 186 * sc), radius=int(9 * S * sc), fill=c)
    for px in (-130, 55):
        d.line(p(x + px * sc, y - wr - 190 * sc, x + px * sc, y - wr - 120 * sc), fill=c, width=int(7 * S * sc))
    # front: EV has a short flat front (batteries under seat), gas car a long hood
    if ev:
        d.rounded_rectangle(p(x + 50 * sc, y - wr - 75 * sc, x + 160 * sc, y - wr - 24 * sc), radius=int(14 * S * sc), fill=c)
        bolt(d, x - 45 * sc, y - wr - 78 * sc, 0.42 * sc, rgba(BG, a))
    else:
        d.rounded_rectangle(p(x + 50 * sc, y - wr - 100 * sc, x + 185 * sc, y - wr - 24 * sc), radius=int(10 * S * sc), fill=c)
        for gx in range(70, 175, 22):
            d.line(p(x + gx * sc, y - wr - 88 * sc, x + gx * sc, y - wr - 36 * sc), fill=rgba(BG, 0.5 * a), width=int(3 * S * sc))
    # lamp
    d.ellipse(p(x + 158 * sc, y - wr - 70 * sc, x + 182 * sc, y - wr - 46 * sc), fill=rgba(ACC if ev else ACC2, a))
    for wx in (-115, 115):
        spoke_wheel(d, x + wx * sc, y - wr, wr, ang, WHITE if ev else SMOKE, a)

def smoke(d, x, y, t, a=1.0, seed=0):
    for i in range(4):
        ph = (t * 0.9 + i / 4 + seed * 0.37) % 1.0
        r = 10 + 26 * ph
        d.ellipse(p(x - 60 * ph - r, y - 40 * ph - r, x - 60 * ph + r, y - 40 * ph + r), fill=rgba(SMOKE, 0.45 * (1 - ph) * a))

# ---------- 1. one in three cars was electric ----------
def vis_third(d, lt, t):
    dur = sdur("third")
    yr = 1890 + int(round(10 * ease_out(lt / 1.4)))
    k = ease_out(lt / 0.4)
    text_c(d, 450, 10, str(yr), FL("InterDisplay-Black.otf", 110), rgba(WHITE, k))
    text_c(d, 450, 140, "CARS ON U.S. ROADS", FL("InterDisplay-Bold.otf", 32), rgba(MUTED, k))
    rows = [320, 480, 640]
    cols = [155, 450, 745]
    ev_idx = {(0, 1), (1, 0), (2, 2)}
    reveal = ease_out((lt - 2.2) / 0.6)
    for r, y in enumerate(rows):
        for c, x0 in enumerate(cols):
            st = 0.3 + 0.12 * (r * 3 + c)
            q = ease_out((lt - st) / 0.7)
            if q <= 0: continue
            x = x0 - 120 * (1 - q)
            is_ev = (r, c) in ev_idx
            col = ACC if (is_ev and reveal > 0) else GREY
            if is_ev and reveal > 0:
                d.ellipse(p(x - 120, y - 120, x + 120, y + 20), fill=rgba(ACC, 0.10 * reveal))
            vintage_car(d, x, y + 40, 0.5, col, q, ang=t * 3, ev=is_ev)
            if not is_ev and reveal > 0:
                smoke(d, x - 95, y + 2, t, reveal * 0.8, seed=r * 3 + c)
    a = back_out((lt - 2.8) / 0.45)
    if a > 0:
        d.rounded_rectangle(p(190, 735, 710, 835), radius=50 * S, fill=rgba(ACC, clamp(a)))
        text_c(d, 450, 752, "≈ 1 IN 3 ELECTRIC", FL("InterDisplay-Black.otf", int(52 * max(a, 0.05))), rgba(BG, clamp(a)))

# ---------- 2. why drivers loved them ----------
def icon_slash(d, x, y, a):
    d.line(p(x - 44, y - 44, x + 44, y + 44), fill=rgba(ACC2, a), width=int(9 * S))

def vis_loved(d, lt, t):
    k = ease_out(lt / 0.4)
    x = 450 + 30 * math.sin(t * 0.8)
    vintage_car(d, x, 270, 0.75, WHITE, k, ang=t * 2.2, ev=True)
    # silent: no waves, just a calm "zzz"-free line
    text_c(d, 450, 20, "ELECTRIC, c.1900", FL("InterDisplay-Bold.otf", 34), rgba(ACC, k))
    cards = [("QUIET", "speaker"), ("NO EXHAUST", "cloud"), ("NO GEARS", "gear")]
    for i, (lab, ic) in enumerate(cards):
        st = 0.5 + i * 0.9
        q = ease_out((lt - st) / 0.5)
        if q <= 0: continue
        y = 340 + i * 160
        xo = 160 * (1 - q)
        d.rounded_rectangle(p(110 + xo + 6, y + 8, 790 + xo + 6, y + 128), radius=28 * S, fill=rgba((0, 0, 0), 0.35 * q))
        d.rounded_rectangle(p(110 + xo, y, 790 + xo, y + 120), radius=28 * S, fill=rgba((22, 28, 37), q), outline=rgba(DARK, q), width=3 * S)
        cx, cy = 200 + xo, y + 60
        if ic == "speaker":
            speaker(d, cx + 10, cy, 0.42, MUTED, q)
        elif ic == "cloud":
            for ox, oy, r in ((-22, 6, 24), (8, -10, 30), (34, 8, 22)):
                d.ellipse(p(cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r), fill=rgba(MUTED, q))
        else:
            for kk in range(8):
                aa = kk * math.pi / 4 + t
                d.line(p(cx, cy, cx + math.cos(aa) * 40, cy + math.sin(aa) * 40), fill=rgba(MUTED, q), width=int(12 * S))
            d.ellipse(p(cx - 30, cy - 30, cx + 30, cy + 30), fill=rgba(MUTED, q))
            d.ellipse(p(cx - 11, cy - 11, cx + 11, cy + 11), fill=rgba((22, 28, 37), q))
        sl = ease_out((lt - st - 0.3) / 0.3)
        icon_slash(d, cx, cy, sl * q)
        d.text(p(290 + xo, y + 32), lab, font=FL("InterDisplay-Black.otf", 50), fill=rgba(WHITE, q))
        # check mark
        ck = ease_out((lt - st - 0.35) / 0.3)
        if ck > 0:
            mx = 730 + xo
            glow_circle(d, mx, cy, 30, ACC, ck)
            poly_line(d, [(mx - 14, cy), (mx - 4, cy + 11), (mx + 15, cy - 12)], rgba(BG, ck), 7)

# ---------- 3. the hand crank and kickback ----------
def vis_crank(d, lt, t):
    dur = sdur("crank")
    k = ease_out(lt / 0.4)
    # engine block (cutaway) on the left
    d.rounded_rectangle(p(70 + 6, 250 + 8, 420 + 6, 610 + 8), radius=24 * S, fill=rgba((0, 0, 0), 0.35 * k))
    d.rounded_rectangle(p(70, 250, 420, 610), radius=24 * S, fill=rgba((26, 32, 42), k), outline=rgba(GREY, k), width=4 * S)
    text_c(d, 245, 200, "GAS ENGINE", FL("InterDisplay-Bold.otf", 34), rgba(MUTED, k))
    kick_t = dur * 0.55
    if lt < kick_t:
        ang = lt * 3.2
    else:
        u = lt - kick_t
        ang = kick_t * 3.2 - 9.0 * (1 - math.exp(-u * 5))  # violent reverse spin
    # pistons moving with the crank angle
    for i, x in enumerate((140, 245, 350)):
        off = math.sin(ang + i * 2.1) * 40
        d.rectangle(p(x - 38, 290, x + 38, 520), fill=rgba((16, 20, 27), k))
        d.rounded_rectangle(p(x - 34, 330 + off, x + 34, 400 + off), radius=8 * S, fill=rgba(SMOKE, k))
        d.line(p(x, 400 + off, 245 + math.cos(ang + i * 2.1) * 30, 560), fill=rgba(GREY, k), width=8 * S)
    # crankshaft out the front to the handle
    cx, cy = 640, 560
    d.line(p(420, 560, cx, cy), fill=rgba(SMOKE, k), width=16 * S)
    r = 150
    hx, hy = cx + math.cos(ang) * r, cy + math.sin(ang) * r
    arc_col = ACC if lt < kick_t else ACC2
    # rotation trail
    deg = math.degrees(ang)
    if lt < kick_t:
        arc(d, cx, cy, r, deg - 70, deg, rgba(arc_col, 0.35 * k), 14)
    else:
        arc(d, cx, cy, r, deg, deg + 120, rgba(arc_col, 0.5), 18)
    d.ellipse(p(cx - 34, cy - 34, cx + 34, cy + 34), fill=rgba(WHITE, k))
    d.line(p(cx, cy, hx, hy), fill=rgba(WHITE, k), width=20 * S)
    d.rounded_rectangle(p(hx - 22, hy - 48, hx + 22, hy + 48), radius=18 * S, fill=rgba(ACC2 if lt >= kick_t else WHITE, k))
    text_c(d, cx, 300, "HAND CRANK", FL("InterDisplay-Black.otf", 44), rgba(WHITE, k))
    a = back_out((lt - kick_t) / 0.35)
    if a > 0:
        shake = 6 * math.sin(lt * 60) * max(0, 1 - (lt - kick_t) / 0.6)
        tx, ty = 450 + shake, 750
        d.rounded_rectangle(p(tx - 230, ty, tx + 230, ty + 96), radius=48 * S, fill=rgba(ACC2, clamp(a)))
        text_c(d, tx, ty + 16, "KICKBACK!", FL("InterDisplay-Black.otf", int(58 * max(a, 0.05))), rgba(BG, clamp(a)))
        # warning triangle
        wx, wy = 790, 150
        poly(d, [(wx, wy - 60 * a), (wx - 62 * a, wy + 48 * a), (wx + 62 * a, wy + 48 * a)], rgba(ACC2, clamp(a)))
        text_c(d, wx, wy - 30 * a, "!", FL("InterDisplay-Black.otf", int(66 * max(a, 0.05))), rgba(BG, clamp(a)))

# ---------- 4. price: $650 vs $1,750 ----------
def vis_price(d, lt, t):
    dur = sdur("price")
    k = ease_out(lt / 0.4)
    # assembly line conveyor at the top
    text_c(d, 450, 20, "MASS PRODUCTION", FL("InterDisplay-Bold.otf", 32), rgba(MUTED, k))
    d.rounded_rectangle(p(60, 170, 840, 196), radius=13 * S, fill=rgba(DARK, k))
    for j in range(12):
        rx = 60 + ((j * 70 + t * 70) % 780)
        d.ellipse(p(rx - 9, 174, rx + 9, 192), fill=rgba(GREY, k))
    for j in range(4):
        cx = 60 + ((j * 200 + t * 90) % 780)
        q = clamp(min((cx - 60) / 60, (840 - cx) / 60))
        vintage_car(d, cx, 170, 0.28, SMOKE, q * k, ang=t * 4, ev=False)
    # bars
    base = 760
    gx, ex = 270, 630
    hmax = 430
    u1 = ease_inout((lt - 1.2) / 1.2)
    u2 = ease_inout((lt - 2.8) / 1.6)
    for x, val, col, lab, u, st in ((gx, 650, ACC2, "GAS CAR", u1, 1.0), (ex, 1750, ACC, "ELECTRIC", u2, 2.6)):
        a = ease_out((lt - st) / 0.3)
        if a <= 0: continue
        h = hmax * val / 1750 * u
        d.rounded_rectangle(p(x - 110 - 6, base - h - 6, x + 110 + 6, base + 6), radius=24 * S, fill=rgba(col, 0.2 * a))
        if h > 8:
            d.rounded_rectangle(p(x - 110, base - h, x + 110, base), radius=20 * S, fill=rgba(col, a))
        text_c(d, x, base + 20, lab, FL("InterDisplay-Black.otf", 38), rgba(col, a))
        text_c(d, x, base - h - 80, f"${int(round(val * u)):,}", FL("InterDisplay-Black.otf", 66), rgba(WHITE, a))
    d.line(p(90, base, 810, base), fill=rgba(MUTED, k), width=4 * S)
    yr = ease_out((lt - 0.6) / 0.4)
    d.rounded_rectangle(p(80, 240, 240, 300), radius=30 * S, fill=rgba((22, 28, 37), yr), outline=rgba(WHITE, yr), width=3 * S)
    text_c(d, 160, 250, "1912", FL("InterDisplay-Black.otf", 38), rgba(WHITE, yr))
    m = back_out((lt - 4.6) / 0.4)
    if m > 0:
        text_c(d, 270, 390, "≈ 2.7×", FL("InterDisplay-Black.otf", int(64 * max(m, 0.05))), rgba(ACC, clamp(m)))

# ---------- 5. the electric starter ----------
def gear(d, cx, cy, r, teeth, ang, col, a=1.0, tooth=14):
    pts = []
    for i in range(teeth * 2):
        aa = ang + i * math.pi / teeth
        rr = r + (tooth if i % 2 == 0 else 0)
        for dd in (-0.35, 0.35):
            a2 = aa + dd * math.pi / teeth
            pts.append((cx + math.cos(a2) * rr, cy + math.sin(a2) * rr))
    poly(d, pts, rgba(col, a))
    d.ellipse(p(cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55), fill=rgba((22, 28, 37), a))
    d.ellipse(p(cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18), fill=rgba(col, a))

def vis_starter(d, lt, t):
    dur = sdur("starter")
    k = ease_out(lt / 0.4)
    press = 0.9
    pressed = lt > press
    spin = max(0.0, lt - press - 0.25)
    # START button
    bx, by = 200, 200
    depth = 10 if pressed and lt < press + 0.5 else 0
    d.ellipse(p(bx - 100, by - 100 + 14, bx + 100, by + 100 + 14), fill=rgba((0, 0, 0), 0.4 * k))
    if pressed:
        d.ellipse(p(bx - 125, by - 125, bx + 125, by + 125), fill=rgba(ACC, 0.15 * k))
    d.ellipse(p(bx - 100, by - 100 + depth, bx + 100, by + 100 + depth), fill=rgba(ACC if pressed else GREY, k))
    text_c(d, bx, by - 26 + depth, "START", FL("InterDisplay-Black.otf", 44), rgba(BG, k))
    # battery -> wire -> motor
    d.rounded_rectangle(p(560, 120, 800, 260), radius=18 * S, fill=rgba((22, 28, 37), k), outline=rgba(WHITE, k), width=5 * S)
    text_c(d, 680, 166, "BATTERY", FL("InterDisplay-Black.otf", 40), rgba(WHITE, k))
    wire = [(680, 260), (680, 400), (320, 400), (320, 560)]
    poly_line(d, wire, rgba(DARK, k), 10)
    if pressed:
        f = ease_out((lt - press) / 0.4)
        poly_line(d, wire, rgba(ACC, 0.25 * f), 22)
        poly_line(d, wire, rgba(ACC, f), 8)
        # current pulses travelling down the wire
        segs = [(wire[i], wire[i + 1]) for i in range(3)]
        lens = [abs(b[0] - a_[0]) + abs(b[1] - a_[1]) for a_, b in segs]; tot = sum(lens)
        for j in range(4):
            s_ = ((lt * 500 + j * tot / 4) % tot)
            for (a_, b), ln in zip(segs, lens):
                if s_ <= ln:
                    q = s_ / ln; x = a_[0] + (b[0] - a_[0]) * q; y = a_[1] + (b[1] - a_[1]) * q
                    glow_circle(d, x, y, 9, ACC, f); break
                s_ -= ln
    # starter motor pinion meshing with the flywheel ring gear
    fx, fy, fr = 590, 640, 165
    pr = 52
    px, py = 320, 640
    ga = spin * 2.2
    gear(d, fx, fy, fr, 36, -ga * pr / fr, SMOKE, k, tooth=14)
    gear(d, px + 55, py, pr, 11, ga + 0.15, ACC if pressed else GREY, k, tooth=14)
    d.rounded_rectangle(p(px - 150, py - 62, px - 20, py + 62), radius=20 * S, fill=rgba(ACC if pressed else GREY, k))
    text_c(d, px - 85, py + 80, "MOTOR", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, k))
    text_c(d, fx, fy + fr + 24, "FLYWHEEL", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, k))
    a = ease_out((lt - 1.8) / 0.4)
    d.rounded_rectangle(p(470, 30, 860, 100), radius=35 * S, fill=rgba(WHITE, a))
    text_c(d, 665, 44, "1912 · ELECTRIC STARTER", FL("InterDisplay-Black.otf", 28), rgba(BG, a))
    # the crank, crossed out
    c2 = ease_out((lt - 2.6) / 0.4)
    if c2 > 0:
        cx, cy = 110, 470
        d.line(p(cx - 40, cy + 30, cx + 30, cy - 30), fill=rgba(WHITE, c2), width=10 * S)
        d.rounded_rectangle(p(cx + 18, cy - 60, cx + 44, cy - 16), radius=10 * S, fill=rgba(WHITE, c2))
        d.line(p(cx - 60, cy - 60, cx + 60, cy + 60), fill=rgba(ACC2, c2), width=10 * S)

# ---------- 6. oil + roads -> long range wins ----------
CITIES = [(140, 200), (330, 110), (560, 170), (760, 90), (250, 330), (500, 330), (720, 300)]
ROADS = [(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6), (2, 5), (3, 6)]

def derrick(d, x, y, sc, a):
    c = rgba(WHITE, a)
    d.line(p(x - 40 * sc, y, x, y - 130 * sc), fill=c, width=int(6 * S))
    d.line(p(x + 40 * sc, y, x, y - 130 * sc), fill=c, width=int(6 * S))
    for f in (0.3, 0.6):
        yy = y - 130 * sc * f; w = 40 * sc * (1 - f)
        d.line(p(x - w, yy, x + w, yy), fill=c, width=int(5 * S))
    d.line(p(x - 60 * sc, y, x + 60 * sc, y), fill=c, width=int(6 * S))

def vis_roads(d, lt, t):
    dur = sdur("roads")
    k = ease_out(lt / 0.4)
    # map panel
    d.rounded_rectangle(p(60, 50, 840, 400), radius=28 * S, fill=rgba((18, 23, 31), k), outline=rgba(DARK, k), width=3 * S)
    for i, (a_, b_) in enumerate(ROADS):
        q = ease_inout((lt - 0.3 - i * 0.18) / 0.5)
        if q <= 0: continue
        (x0, y0), (x1, y1) = CITIES[a_], CITIES[b_]
        d.line(p(x0, y0, x0 + (x1 - x0) * q, y0 + (y1 - y0) * q), fill=rgba(ACC2, 0.85 * k), width=8 * S)
    for x, y in CITIES:
        glow_circle(d, x, y, 10, WHITE, k)
    # a car travelling the network
    u = (lt * 0.35) % 1.0
    path = [CITIES[i] for i in (0, 4, 5, 2, 3, 6)]
    seg = u * (len(path) - 1); i = int(seg); q = seg - i
    cx = path[i][0] + (path[i + 1][0] - path[i][0]) * q; cy = path[i][1] + (path[i + 1][1] - path[i][1]) * q
    if lt > 1.2: glow_circle(d, cx, cy, 13, ACC2, ease_out((lt - 1.2) / 0.3))
    # oil derrick in the corner ("Texas")
    da = ease_out((lt - 0.8) / 0.4)
    derrick(d, 760, 385, 1.0, da)
    text_c(d, 590, 352, "CHEAP OIL", FL("InterDisplay-Bold.otf", 26), rgba(WHITE, da))
    # timeline: EV share 1900 -> 1935
    ca = ease_out((lt - 1.6) / 0.4)
    ox, oy, x1 = 120, 760, 800
    d.line(p(ox, oy, x1, oy), fill=rgba(MUTED, ca), width=4 * S)
    for yr, lab in ((1900, "1900"), (1935, "1935")):
        x = ox + (x1 - ox) * (yr - 1900) / 35
        text_c(d, x, oy + 14, lab, FL("InterDisplay-Bold.otf", 30), rgba(MUTED, ca))
    text_c(d, 460, 450, "ELECTRIC SHARE", FL("InterDisplay-Bold.otf", 30), rgba(ACC, ca))
    prog = ease_inout((lt - 2.0) / (dur * 0.6))
    n = max(2, int(80 * prog))
    def share(u_):  # qualitative fall from ~1/3 to ~0
        return 0.33 * (1 - ease_inout(u_)) ** 1.3
    pts = [(ox + (x1 - ox) * (prog * j / (n - 1)), oy - 700 * share(prog * j / (n - 1))) for j in range(n)]
    if prog > 0 and ca > 0:
        poly_line(d, pts, rgba(ACC, 0.25 * ca), 22); poly_line(d, pts, rgba(ACC, ca), 9)
        hx, hy = pts[-1]
        d.ellipse(p(hx - 14, hy - 14, hx + 14, hy + 14), fill=rgba(ACC, ca))
        text_c(d, ox + 40, oy - 700 * 0.33 - 60, "≈ 1/3", FL("InterDisplay-Black.otf", 40), rgba(WHITE, ca))
    za = ease_out((prog - 0.92) / 0.08)
    if za > 0:
        d.text(p(x1 - 150, oy - 100), "≈ 0", font=FL("InterDisplay-Black.otf", 52), fill=rgba(ACC2, za))

# ---------- 7. outro ----------
def vis_outro3(d, lt, t):
    dur = sdur("outro3")
    cut = dur * 0.5
    if lt < cut:
        k = ease_out(lt / 0.5)
        m = ease_inout((lt - 0.6) / 1.0)
        va = k * clamp(1 - 2 * m); ma = clamp(2 * m - 1)
        if ma <= 0.01:
            vintage_car(d, 450, 330, 0.85, WHITE, va, ang=t * 2, ev=True)
            text_c(d, 450, 460, "1900", FL("InterDisplay-Black.otf", 54), rgba(MUTED, va))
        else:
            car_side(d, 450, 290, 1.25, ACC, ma)
            text_c(d, 450, 460, "TODAY", FL("InterDisplay-Black.otf", 54), rgba(ACC, ma))
        a = ease_out((lt - 1.3) / 0.4)
        text_c(d, 450, 570, "NOT WRONG.", FL("InterDisplay-Black.otf", 70), rgba(WHITE, a))
        b = ease_out((lt - 1.6) / 0.4)
        text_c(d, 450, 660, "JUST EARLY.", FL("InterDisplay-Black.otf", 70), rgba(ACC, b))
    else:
        k = back_out((lt - cut) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - cut - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

VIS.update({"third": vis_third, "loved": vis_loved, "crank": vis_crank, "price": vis_price,
            "starter": vis_starter, "roads": vis_roads, "outro3": vis_outro3})
