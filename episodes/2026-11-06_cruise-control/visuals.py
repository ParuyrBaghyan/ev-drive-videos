# Episode visuals: Ralph Teetor, the blind engineer behind cruise control (History).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
CHROME = (176, 186, 200)
BLK = "InterDisplay-Black.otf"
SEMI = "Inter-SemiBold.otf"

def sdur(name):
    for s in scenes:
        if s["visual"] == name:
            return s["vis_end"] - s["start"]
    return 4.0

def poly(d, pts, col):
    d.polygon(p(*[v for xy in pts for v in xy]), fill=col)

def circ(d, x, y, r, col):
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=col)

def ring(d, x, y, r, col, w):
    d.ellipse(p(x - r, y - r, x + r, y + r), outline=col, width=max(1, int(w * S)))

def label(d, x, y, s, col, a, size=28, f=BLK):
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
    d.line(p(*[v for xy in pts for v in xy]), fill=col, width=max(1, int(w * S)), joint="curve")

def arrow(d, x0, y0, x1, y1, col, w=10, head=26):
    line(d, [(x0, y0), (x1, y1)], col, w)
    ang = math.atan2(y1 - y0, x1 - x0)
    a1, a2 = ang + 2.6, ang - 2.6
    poly(d, [(x1 + math.cos(ang) * 6, y1 + math.sin(ang) * 6), (x1 + math.cos(a1) * head, y1 + math.sin(a1) * head),
             (x1 + math.cos(a2) * head, y1 + math.sin(a2) * head)], col)

def bolt(d, x, y, sc, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in pts], col)

def road(d, y, t, a, speed=1.0, x0=40, x1=860):
    line(d, [(x0, y), (x1, y)], rgba(DARK, a), 8)
    off = (t * 260 * speed) % 120
    for k in range(-1, 9):
        xx = x1 - k * 120 - off
        if x0 < xx < x1 - 50:
            line(d, [(xx, y + 40), (min(xx + 60, x1), y + 40)], rgba(STEEL, a), 6)

def speedo(d, cx, cy, r, v, vmax, a, set_v=None):
    a0, a1 = 150, 390
    def ang(x): return a0 + (a1 - a0) * x / vmax
    arc(d, cx, cy, r, a0, a1, rgba(DARK, a), 22)
    arc(d, cx, cy, r, a0, ang(v), rgba(ACC, a), 22)
    if set_v is not None:
        sa = math.radians(ang(set_v))
        circ(d, cx + math.cos(sa) * r, cy + math.sin(sa) * r, 16, rgba(ACC2, a))
    na = math.radians(ang(v))
    line(d, [(cx, cy), (cx + math.cos(na) * (r - 24), cy + math.sin(na) * (r - 24))], rgba(WHITE, a), 9)
    circ(d, cx, cy, 16, rgba(WHITE, a))

def eye(d, cx, cy, sc, col, a, closed=0.0):
    # almond eye outline + iris; closed in [0,1] squashes it shut
    h = 60 * sc * (1 - closed) + 4
    pts_top = [(cx - 120 * sc + 240 * sc * u / 20, cy - h * math.sin(math.pi * u / 20)) for u in range(21)]
    pts_bot = [(cx + 120 * sc - 240 * sc * u / 20, cy + h * math.sin(math.pi * u / 20)) for u in range(21)]
    poly(d, pts_top + pts_bot, rgba(PANEL, a))
    line(d, pts_top + pts_bot + [pts_top[0]], rgba(col, a), 7)
    if closed < 0.7:
        r = 38 * sc * (1 - closed)
        circ(d, cx, cy, r, rgba(col, a)); circ(d, cx, cy, r * 0.45, rgba(BG, a))

# ---------- scenes ----------
def vis_cc_hook(d, lt, t):
    dur = sdur("cc_hook")
    a = ease_out(lt / 0.4)
    road(d, 560, t, a)
    car_side(d, 380, 470, 1.0, WHITE, a)
    # speedometer locked at 65
    v = 65 * ease_out(lt / 1.0)
    speedo(d, 450, 210, 120, v, 100, a, set_v=65)
    label(d, 450, 218, f"{int(round(v))}", WHITE, a, size=54)
    label(d, 450, 280, "MPH", MUTED, a, size=22)
    ca = back_out((lt - 0.5) / 0.4)
    chip(d, 450, 650, "CRUISE CONTROL", ACC, clamp(ca), size=42)
    # eye closes: inventor couldn't see
    ea = ease_out((lt - 1.4) / 0.4)
    if ea > 0:
        eye(d, 450, 810, 0.75, ACC2, ea, closed=0.45 * ease_inout((lt - 1.8) / 0.6))
        sl = ease_out((lt - 2.0) / 0.35)
        if sl > 0:
            line(d, [(350, 760), (350 + 200 * sl, 760 + 100 * sl)], rgba(WHITE, ea), 10)

def vis_cc_blind(d, lt, t):
    dur = sdur("cc_blind")
    a = ease_out(lt / 0.4)
    label(d, 450, 40, "RALPH TEETOR", WHITE, a, size=56)
    x = 170; y0, y1 = 170, 760
    line(d, [(x, y0), (x, y0 + (y1 - y0) * ease_inout((lt - 0.2) / 2.6))], rgba(ACC, a), 10)
    items = [("1890", "BORN IN INDIANA", WHITE), ("AGE 5", "BLINDED IN AN ACCIDENT", ACC2),
             ("1912", "ENGINEERING DEGREE", WHITE), ("1936", "PRESIDENT OF THE SAE", ACC)]
    for i, (yr, txt, col) in enumerate(items):
        k = back_out((lt - 0.4 - 0.7 * i) / 0.4)
        if k <= 0: continue
        yy = y0 + 30 + i * 175
        circ(d, x, yy, 24 * k, rgba(col, clamp(k)))
        circ(d, x, yy, 10 * k, rgba(BG, clamp(k)))
        xo = 230 + 60 * (1 - clamp(k))
        d.rounded_rectangle(p(xo, yy - 62, 800, yy + 62), radius=22 * S, fill=rgba(PANEL, clamp(k)), outline=rgba(STEEL, clamp(k)), width=3 * S)
        d.text(p(xo + 30, yy - 52), yr, font=FL(BLK, 48), fill=rgba(col, clamp(k)))
        d.text(p(xo + 30, yy + 6), txt, font=FL(SEMI, 28), fill=rgba(MUTED, clamp(k)))
    sa = ease_out((lt - 3.6) / 0.4)
    label(d, 450, 800, "SOCIETY OF AUTOMOTIVE ENGINEERS", MUTED, sa, size=24, f=SEMI)

def vis_cc_lawyer(d, lt, t):
    dur = sdur("cc_lawyer")
    a = ease_out(lt / 0.4)
    gx0, gx1, gy0, gy1 = 110, 800, 110, 520
    d.rounded_rectangle(p(gx0 - 30, gy0 - 40, gx1 + 30, gy1 + 30), radius=26 * S, fill=rgba(PANEL, a), outline=rgba(STEEL, a), width=3 * S)
    label(d, 160, gy0 - 30, "SPEED", MUTED, a, size=24)
    label(d, gx1 - 40, gy1 - 6, "TIME", MUTED, a, size=24)
    base = (gy0 + gy1) / 2
    prog = clamp((lt - 0.3) / (dur * 0.55))
    n = int(80 * prog) + 1
    pts = []
    for k in range(n):
        u = k / 80
        y = base - 120 * math.sin(u * 2 * math.pi * 2.0)
        pts.append((gx0 + (gx1 - gx0) * u, y))
    if len(pts) > 1: line(d, pts, rgba(ACC2, a), 9)
    if pts: circ(d, pts[-1][0], pts[-1][1], 14, rgba(ACC2, a))
    # annotations at first peak/trough
    if prog > 0.15:
        ka = ease_out((prog - 0.15) / 0.1)
        label(d, gx0 + (gx1 - gx0) * 0.125, base - 190, "LISTENING", ACC2, ka, size=26)
    if prog > 0.4:
        ka = ease_out((prog - 0.4) / 0.1)
        label(d, gx0 + (gx1 - gx0) * 0.375, base + 140, "TALKING", ACC2, ka, size=26)
    # goal: flat line
    fa = ease_out((lt - dur * 0.62) / 0.5)
    if fa > 0:
        fl = gx0 + (gx1 - gx0) * fa
        line(d, [(gx0, base), (fl, base)], rgba(ACC, 1), 11)
        circ(d, fl, base, 14, rgba(ACC, 1))
        chip(d, 450, 600, "GOAL: HOLD ONE SPEED", ACC, fa, size=40)
    # small car bobbing along the bottom
    cx = 140 + 620 * ease_inout(lt / dur)
    jitter = 4 * math.sin(t * 9) if fa <= 0 else 0
    car_side(d, cx, 790 + jitter, 0.45, WHITE, a)

def vis_cc_device(d, lt, t):
    dur = sdur("cc_device")
    a = ease_out(lt / 0.4)
    # left: dial with set speed
    label(d, 200, 50, "SET SPEED DIAL", MUTED, a, size=24)
    circ(d, 200, 210, 110, rgba(PANEL, a)); ring(d, 200, 210, 110, rgba(CHROME, a), 6)
    for k in range(9):
        ang = math.radians(150 + 30 * k)
        line(d, [(200 + math.cos(ang) * 82, 210 + math.sin(ang) * 82), (200 + math.cos(ang) * 98, 210 + math.sin(ang) * 98)], rgba(MUTED, a), 4)
    sa = math.radians(150 + 160 * ease_inout((lt - 0.3) / 0.8))
    line(d, [(200, 210), (200 + math.cos(sa) * 80, 210 + math.sin(sa) * 80)], rgba(ACC2, a), 9)
    circ(d, 200, 210, 18, rgba(ACC2, a))
    # right: speed governor (spinning flyweights)
    spd = clamp((lt - 0.4) / 2.0)
    gx, gy = 620, 230
    label(d, gx, 50, "SPEED SENSOR", MUTED, a, size=24)
    line(d, [(gx, gy - 120), (gx, gy + 140)], rgba(CHROME, a), 10)
    spread = 40 + 70 * ease_out(spd)
    ph = t * (2 + 10 * spd)
    for sgn in (-1, 1):
        wx = gx + sgn * spread * math.cos(ph) ; wy = gy + 10 - 30 * spd
        line(d, [(gx, gy - 90), (wx, wy)], rgba(CHROME, a), 6)
        line(d, [(gx, gy + 70 - 30 * spd), (wx, wy)], rgba(CHROME, a), 6)
        depth = 0.75 + 0.25 * math.sin(ph) * sgn
        circ(d, wx, wy, 28 * depth, rgba(ACC, a))
    d.rounded_rectangle(p(gx - 30, gy + 60 - 30 * spd, gx + 30, gy + 82 - 30 * spd), radius=6 * S, fill=rgba(STEEL, a))
    # bottom: gas pedal with pushback
    px, py = 330, 600
    reach = ease_inout(clamp((lt - 2.2) / 0.6))
    tilt = 0.35 - 0.2 * reach
    pl = 170
    tip = (px + math.cos(-math.pi / 2 + tilt) * pl, py + math.sin(-math.pi / 2 + tilt) * pl)
    d.rounded_rectangle(p(px - 120, py, px + 160, py + 28), radius=10 * S, fill=rgba(DARK, a))
    line(d, [(px, py), tip], rgba(WHITE, a), 30)
    label(d, px + 10, py + 50, "GAS PEDAL", MUTED, a, size=24)
    # linkage from governor down to pedal
    line(d, [(gx, gy + 140), (gx, 470), (tip[0] + 60, 470)], rgba(STEEL, a), 6)
    pb = ease_out((lt - 2.4) / 0.4)
    if pb > 0:
        wob = 8 * math.sin(t * 10)
        arrow(d, tip[0] + 200 + wob, tip[1] + 20, tip[0] + 50 + wob, tip[1] + 20, rgba(ACC2, pb), w=12, head=30)
        label(d, tip[0] + 135, tip[1] - 40, "PUSH BACK", ACC2, pb, size=30)
    # lock mode
    la = back_out((lt - dur * 0.6) / 0.4)
    if la > 0:
        chip(d, 680, 600, "LOCK", ACC, clamp(la), size=40)
    ba = ease_out((lt - dur * 0.8) / 0.3)
    if ba > 0:
        tap = abs(math.sin((lt - dur * 0.8) * 6)) if lt - dur * 0.8 < 0.6 else 0
        d.rounded_rectangle(p(600, 730 + 10 * tap, 760, 780 + 10 * tap), radius=12 * S, fill=rgba(WHITE, ba))
        label(d, 680, 800, "BRAKE TAP = OFF", MUTED, ba, size=24)

def vis_cc_launch(d, lt, t):
    dur = sdur("cc_launch")
    a = ease_out(lt / 0.4)
    # patent document card
    k = back_out((lt - 0.1) / 0.45)
    if k > 0:
        x0 = 120 + 40 * (1 - clamp(k))
        d.rounded_rectangle(p(x0, 60, x0 + 300, 440), radius=16 * S, fill=rgba((226, 230, 236), clamp(k)))
        d.text(p(x0 + 24, 84), "U.S. PATENT", font=FL(BLK, 30), fill=rgba(BG, clamp(k)))
        d.text(p(x0 + 24, 126), "2,519,859", font=FL(BLK, 34), fill=rgba(BG, clamp(k)))
        for j in range(6):
            w = 250 - (j * 37) % 90
            d.rounded_rectangle(p(x0 + 24, 190 + j * 34, x0 + 24 + w, 202 + j * 34), radius=5 * S, fill=rgba(CHROME, clamp(k)))
        st = back_out((lt - 0.8) / 0.35)
        if st > 0:
            ring(d, x0 + 220, 380, 52 * st, rgba(ACC2, clamp(st)), 7)
            label(d, x0 + 220, 360, "1950", ACC2, clamp(st), size=30 * max(st, 0.1))
    # right: year counter to 1958
    yr = 1950 + int(round(8 * ease_inout((lt - 1.2) / 1.4)))
    ya = ease_out((lt - 1.0) / 0.4)
    label(d, 640, 120, f"{yr}", WHITE if yr < 1958 else ACC, ya, size=96)
    label(d, 640, 240, "FIRST CAR", MUTED, ya, size=28)
    # car rolls in with badge
    ca = ease_out((lt - 2.4) / 0.8)
    if ca > 0:
        cx = -200 + 650 * ca
        road(d, 730, t, 1, speed=0.5)
        car_side(d, cx, 640, 1.0, CHROME)
        label(d, 450, 462, "CHRYSLER IMPERIAL", WHITE, ca, size=34)
    ba = back_out((lt - 3.4) / 0.4)
    if ba > 0:
        chip(d, 450, 800, "\"AUTO-PILOT\"", ACC, clamp(ba), size=44)

def vis_cc_radar(d, lt, t):
    dur = sdur("cc_radar")
    a = ease_out(lt / 0.4)
    road(d, 560, t, a)
    # lead car slows a bit, follower keeps the gap
    lead = 680 - 30 * math.sin(lt * 1.6)
    gap = 430
    fol = lead - gap
    car_side(d, lead, 480, 0.5, MUTED, a)
    car_side(d, fol, 480, 0.5, WHITE, a)
    # radar waves from follower's nose
    for i in range(4):
        ph = (t * 1.8 + i / 4) % 1.0
        r = 20 + ph * (gap - 250)
        arc(d, fol + 125, 465, r, -28, 28, rgba(ACC, a * (1 - ph)), 8)
    # gap bracket
    ga = ease_out((lt - 0.8) / 0.4)
    y = 620
    line(d, [(fol + 125, y), (lead - 115, y)], rgba(ACC, ga), 6)
    line(d, [(fol + 125, y - 18), (fol + 125, y + 18)], rgba(ACC, ga), 6)
    line(d, [(lead - 115, y - 18), (lead - 115, y + 18)], rgba(ACC, ga), 6)
    label(d, (fol + lead) / 2, y + 30, "SAFE GAP", ACC, ga, size=30)
    label(d, 450, 110, "ADAPTIVE CRUISE", WHITE, a, size=56)
    label(d, 450, 190, "RADAR MEASURES THE CAR AHEAD", MUTED, a, size=26, f=SEMI)
    fa = back_out((lt - 1.4) / 0.4)
    chip(d, 450, 750, "FIRST RADAR ACC · 1999", ACC2, clamp(fa), size=34)

def vis_cc_outro(d, lt, t):
    dur = sdur("cc_outro")
    if lt < dur * 0.55:
        a = ease_out(lt / 0.4)
        # a hand-like pressure wave: concentric pulses from a pedal
        for i in range(4):
            ph = (t * 1.2 + i / 4) % 1.0
            ring(d, 450, 330, 60 + ph * 220, rgba(ACC, a * (1 - ph) * 0.9), 8)
        circ(d, 450, 330, 60, rgba(ACC, a))
        label(d, 450, 300, "FEEL", BG, a, size=40)
        q = ease_out((lt - 0.8) / 0.4)
        label(d, 450, 640, "WHAT WOULD", WHITE, q, size=66)
        label(d, 450, 720, "YOU NOTICE?", ACC, q, size=66)
    else:
        k = back_out((lt - dur * 0.55) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.55 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"cc_hook": vis_cc_hook, "cc_blind": vis_cc_blind, "cc_lawyer": vis_cc_lawyer, "cc_device": vis_cc_device,
            "cc_launch": vis_cc_launch, "cc_radar": vis_cc_radar, "cc_outro": vis_cc_outro})
