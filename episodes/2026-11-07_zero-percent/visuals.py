# Episode visuals: what happens when an EV hits 0% (What would happen if...?).

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


RED = (255, 84, 84)

def batt(d, x, y, w, h, frac, a, col=None, label_pct=True):
    # horizontal battery icon, fill frac in [0,1]
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=18 * S, fill=rgba(PANEL, a), outline=rgba(CHROME, a), width=6 * S)
    d.rounded_rectangle(p(x + w, y + h * 0.3, x + w + 22, y + h * 0.7), radius=6 * S, fill=rgba(CHROME, a))
    c = col or (ACC if frac > 0.25 else (ACC2 if frac > 0.1 else RED))
    fw = (w - 28) * clamp(frac)
    if fw > 2:
        d.rounded_rectangle(p(x + 14, y + 14, x + 14 + fw, y + h - 14), radius=10 * S, fill=rgba(c, a))

def turtle(d, x, y, sc, col, a):
    c = rgba(col, a)
    # legs
    for lx in (-50, 40):
        d.rounded_rectangle(p(x + (lx - 12) * sc, y + 10 * sc, x + (lx + 12) * sc, y + 45 * sc), radius=8 * S, fill=c)
    # head
    circ(d, x + 95 * sc, y - 5 * sc, 26 * sc, c)
    # shell
    d.pieslice(p(x - 85 * sc, y - 80 * sc, x + 75 * sc, y + 80 * sc), 180, 360, fill=c)
    d.rectangle(p(x - 90 * sc, y - 2 * sc, x + 80 * sc, y + 16 * sc), fill=c)
    # shell pattern
    for sx in (-40, 0, 40):
        d.line(p(x + sx * sc - 18 * sc, y - 50 * sc, x + sx * sc, y - 20 * sc, x + sx * sc + 18 * sc, y - 50 * sc), fill=rgba(BG, a), width=int(5 * S * sc) or 1)

def truck(d, x, y, sc, a, bed_tilt=0.0):
    c = rgba(STEEL, a)
    # cab
    poly(d, [(x + 200 * sc, y + 30 * sc), (x + 200 * sc, y - 90 * sc), (x + 290 * sc, y - 90 * sc), (x + 330 * sc, y - 30 * sc), (x + 330 * sc, y + 30 * sc)], c)
    poly(d, [(x + 215 * sc, y - 78 * sc), (x + 280 * sc, y - 78 * sc), (x + 308 * sc, y - 36 * sc), (x + 215 * sc, y - 36 * sc)], rgba((10, 13, 18), a))
    # bed
    d.rounded_rectangle(p(x - 300 * sc, y - 2 * sc, x + 195 * sc, y + 22 * sc), radius=6 * S, fill=rgba(CHROME, a))
    d.rectangle(p(x - 300 * sc, y + 22 * sc, x + 330 * sc, y + 44 * sc), fill=c)
    for wx in (-220, -120, 260):
        circ(d, x + wx * sc, y + 60 * sc, 38 * sc, rgba((10, 13, 18), a))
        circ(d, x + wx * sc, y + 60 * sc, 18 * sc, rgba(CHROME, a))

def wheel_spin(d, cx, cy, r, ang, col, a):
    circ(d, cx, cy, r, rgba((10, 13, 18), a))
    ring(d, cx, cy, r * 0.8, rgba(col, a), 6)
    for k in range(5):
        aa = ang + k * 2 * math.pi / 5
        line(d, [(cx, cy), (cx + math.cos(aa) * r * 0.78, cy + math.sin(aa) * r * 0.78)], rgba(col, a), 6)
    circ(d, cx, cy, r * 0.18, rgba(col, a))

def gear(d, cx, cy, r, ang, teeth, col, a):
    pts = []
    for k in range(teeth * 2):
        aa = ang + k * math.pi / teeth
        rr = r if k % 2 == 0 else r * 0.82
        pts.append((cx + math.cos(aa) * rr, cy + math.sin(aa) * rr))
    poly(d, pts, rgba(col, a))
    circ(d, cx, cy, r * 0.3, rgba(BG, a))

def counter(d, x, y, v, unit, col, a, size=120):
    label(d, x, y, f"{int(round(v))}", col, a, size=size)
    label(d, x, y + size * 1.05, unit, MUTED, a, size=28, f=SEMI)

# ---------- scenes ----------
def vis_z_hook(d, lt, t):
    dur = sdur("z_hook")
    a = ease_out(lt / 0.4)
    pr = ease_inout((lt - 0.2) / max(0.5, dur - 1.2))
    pct = 100 * (1 - pr)
    batt(d, 170, 170, 540, 220, pct / 100, a)
    col = ACC if pct > 25 else (ACC2 if pct > 10 else RED)
    label(d, 440, 440, f"{int(round(pct))}%", col, a, size=150)
    road(d, 800, t, a, speed=0.3 + 0.7 * (1 - pr))
    car_side(d, 450, 720, 0.6, WHITE, a)
    if pct < 1:
        k = back_out((lt - (dur - 1.0)) / 0.4)
        chip(d, 450, 40, "NOW WHAT?", ACC2, clamp(k), size=44)

def vis_z_turtle(d, lt, t):
    dur = sdur("z_turtle")
    a = ease_out(lt / 0.4)
    # warnings stacking
    warns = [("LOW BATTERY", ACC2), ("CHARGE NOW", RED)]
    for i, (s, c) in enumerate(warns):
        k = back_out((lt - 0.2 - 0.6 * i) / 0.35)
        if k <= 0: continue
        blink = 0.65 + 0.35 * (math.sin(t * 9) > 0)
        chip(d, 450, 20 + i * 95, "⚠ " + s if False else s, c, clamp(k) * blink, size=40)
    # power bar shrinking
    ta = ease_out((lt - 1.4) / 0.4)
    shrink = ease_inout((lt - 1.6) / 1.2)
    label(d, 220, 230, "POWER", MUTED, ta, size=28, f=SEMI)
    d.rounded_rectangle(p(100, 280, 800, 330), radius=25 * S, fill=rgba(DARK, ta))
    pw = 100 + 700 * (1 - 0.8 * shrink)
    if ta > 0:
        d.rounded_rectangle(p(100, 280, pw, 330), radius=25 * S, fill=rgba(ACC if shrink < 0.5 else ACC2, ta))
    # top speed gauge
    v = 85 - 50 * shrink
    speedo(d, 640, 560, 130, v, 100, ta, set_v=v)
    label(d, 640, 568, f"{int(round(v))}", WHITE, ta, size=54)
    label(d, 640, 630, "MAX MPH", MUTED, ta, size=22)
    # turtle pops in
    k = back_out((lt - 2.0) / 0.45)
    if k > 0:
        bob = 6 * math.sin(t * 3)
        turtle(d, 250, 560 + bob, 1.2 * k, ACC2, clamp(k))
        label(d, 250, 680, "TURTLE MODE", ACC2, clamp(k), size=36)

def vis_z_buffer(d, lt, t):
    dur = sdur("z_buffer")
    a = ease_out(lt / 0.4)
    # vertical pack cross-section
    x0, x1, y0, y1 = 120, 380, 60, 800
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=24 * S, fill=rgba(PANEL, a), outline=rgba(CHROME, a), width=6 * S)
    zero_y = 640
    # usable area (empty now)
    d.rectangle(p(x0 + 14, y0 + 14, x1 - 14, zero_y), fill=rgba(DARK, a))
    label(d, (x0 + x1) / 2, 300, "USABLE", MUTED, a, size=30, f=SEMI)
    # zero line
    line(d, [(x0 - 30, zero_y), (x1 + 30, zero_y)], rgba(WHITE, a), 6)
    label(d, x1 + 90, zero_y - 22, "0%", WHITE, a, size=40)
    # hidden buffer reveal
    k = ease_out((lt - 0.4) / 0.6)
    if k > 0:
        glow = 0.75 + 0.25 * math.sin(t * 4)
        drain = 0.6 * ease_inout((lt - 1.6) / (dur - 2.0))
        top = zero_y + 6 + (y1 - 14 - zero_y - 6) * drain
        d.rectangle(p(x0 + 14, top, x1 - 14, y1 - 14), fill=rgba(ACC2, k * glow))
        label(d, (x0 + x1) / 2, y1 + 20, "HIDDEN BUFFER", ACC2, k, size=30)
    # miles past zero counter
    ca = ease_out((lt - 1.2) / 0.4)
    miles = 13 * ease_out((lt - 1.5) / max(0.5, dur - 2.6))
    d.rounded_rectangle(p(470, 200, 840, 560), radius=26 * S, fill=rgba(PANEL, ca), outline=rgba(STEEL, ca), width=3 * S)
    label(d, 655, 225, "MILES PAST ZERO", MUTED, ca, size=26, f=SEMI)
    label(d, 655, 285, f"+{int(round(miles))}", ACC, ca, size=150)
    label(d, 655, 480, "AAA TEST · MODEL 3", MUTED, ca, size=24, f=SEMI)
    # small car creeping along
    cx = 500 + 280 * ease_inout((lt - 1.5) / (dur - 2.0))
    road(d, 780, t, ca, speed=0.15, x0=440, x1=880)
    car_side(d, cx, 720, 0.32, WHITE, ca)

def vis_z_12v(d, lt, t):
    dur = sdur("z_12v")
    a = ease_out(lt / 0.4)
    line(d, [(40, 420), (860, 420)], rgba(DARK, a), 8)
    blink = (math.sin(t * 7) > 0)
    car_side(d, 450, 330, 0.95, MUTED, a)
    # hazard lights
    if blink and lt > 1.6:
        for hx in (450 + 215 * 0.95, 450 - 225 * 0.95):
            circ(d, hx, 330 - 14, 22, rgba(ACC2, a))
            ring(d, hx, 330 - 14, 40, rgba(ACC2, a * 0.5), 5)
    # big pack (dead)
    d.rounded_rectangle(p(110, 520, 480, 640), radius=18 * S, fill=rgba(PANEL, a), outline=rgba(STEEL, a), width=4 * S)
    label(d, 295, 548, "MAIN PACK", MUTED, a, size=28, f=SEMI)
    label(d, 295, 588, "EMPTY", RED, a, size=30)
    # small 12V battery alive
    k = back_out((lt - 0.5) / 0.4)
    if k > 0:
        kk = clamp(k)
        d.rounded_rectangle(p(560, 520, 790, 640), radius=18 * S, fill=rgba(PANEL, kk), outline=rgba(ACC, kk), width=5 * S)
        bolt(d, 610, 580, 0.45, rgba(ACC, kk))
        label(d, 705, 553, "12 V", ACC, kk, size=50)
    # feeds
    targets = [(240, "LOCKS"), (450, "SCREENS"), (660, "HAZARDS")]
    for i, (tx, s) in enumerate(targets):
        f = ease_out((lt - 1.0 - 0.35 * i) / 0.4)
        if f <= 0: continue
        sx, sy = 675, 650
        ex, ey = tx, 760
        line(d, [(sx, sy), (sx + (ex - sx) * f, sy + (ey - sy) * f)], rgba(ACC, f * 0.8), 5)
        # moving dot
        u = (t * 1.3 + i * 0.3) % 1.0
        circ(d, sx + (ex - sx) * u * f, sy + (ey - sy) * u * f, 8, rgba(ACC, f))
        chip(d, tx, 770, s, ACC if s != "HAZARDS" else ACC2, f, size=28)

def vis_z_tow(d, lt, t):
    dur = sdur("z_tow")
    a = ease_out(lt / 0.4)
    # top: flatbed with car
    tx = 380 + 40 * (1 - ease_out(lt / 1.0))
    truck(d, tx, 210, 0.95, a)
    car_side(d, tx - 60, 145, 0.55, WHITE, a)
    ok = back_out((lt - 0.6) / 0.4)
    chip(d, 450, 0, "FLATBED", ACC, clamp(ok), size=40)
    line(d, [(40, 310), (860, 310)], rgba(DARK, a), 6)
    # bottom: why — wheel -> gear -> motor -> electricity
    ba = ease_out((lt - 1.4) / 0.4)
    spin = t * 6
    wheel_spin(d, 160, 560, 95, spin, CHROME, ba)
    label(d, 160, 680, "WHEEL", MUTED, ba, size=26, f=SEMI)
    gear(d, 345, 560, 60, -spin * 1.6, 12, STEEL, ba)
    gear(d, 440, 560, 38, spin * 2.6, 8, CHROME, ba)
    label(d, 390, 680, "GEARS", MUTED, ba, size=26, f=SEMI)
    # motor
    d.rounded_rectangle(p(520, 470, 720, 650), radius=24 * S, fill=rgba(PANEL, ba), outline=rgba(CHROME, ba), width=5 * S)
    for k in range(5):
        yy = 495 + k * 32
        line(d, [(545, yy), (695, yy)], rgba(ACC2 if lt > 2.6 else STEEL, ba), 8)
    label(d, 620, 680, "MOTOR", MUTED, ba, size=26, f=SEMI)
    ga = ease_out((lt - 2.6) / 0.4)
    if ga > 0:
        fl = 0.6 + 0.4 * (math.sin(t * 14) > 0)
        bolt(d, 800, 560, 0.85, rgba(ACC2, ga * fl))
        chip(d, 450, 750, "BECOMES A GENERATOR", ACC2, ga, size=36)
        # heat squiggles
        for k in range(3):
            ph = (t * 1.5 + k / 3) % 1
            yy = 460 - ph * 90
            xx = 560 + k * 60
            line(d, [(xx, yy), (xx + 10, yy - 15), (xx, yy - 30)], rgba(RED, ga * (1 - ph)), 5)

def vis_z_rescue(d, lt, t):
    dur = sdur("z_rescue")
    a = ease_out(lt / 0.4)
    # van + cable + car
    d.rounded_rectangle(p(60, 120, 300, 300), radius=22 * S, fill=rgba(STEEL, a))
    bolt(d, 180, 210, 0.7, rgba(ACC, a))
    for wx in (110, 250):
        circ(d, wx, 305, 30, rgba((10, 13, 18), a)); circ(d, wx, 305, 13, rgba(CHROME, a))
    car_side(d, 650, 260, 0.7, WHITE, a)
    cab = ease_out((lt - 0.3) / 0.6)
    cx1 = 300 + (530 - 300) * cab
    pts = [(300 + (cx1 - 300) * u / 20, 260 + 50 * math.sin(math.pi * u / 20)) for u in range(21)]
    line(d, pts, rgba(ACC, a), 8)
    if cab >= 1:
        u = (t * 1.2) % 1.0
        circ(d, 300 + 230 * u, 260 + 50 * math.sin(math.pi * u), 11, rgba(WHITE, 1))
    # counters
    pr = ease_out((lt - 0.8) / (dur - 1.4))
    ca = ease_out((lt - 0.6) / 0.4)
    d.rounded_rectangle(p(70, 400, 430, 700), radius=26 * S, fill=rgba(PANEL, ca), outline=rgba(STEEL, ca), width=3 * S)
    d.rounded_rectangle(p(470, 400, 830, 700), radius=26 * S, fill=rgba(PANEL, ca), outline=rgba(STEEL, ca), width=3 * S)
    # clock ring
    arc(d, 250, 520, 80, -90, 270, rgba(DARK, ca), 14)
    if pr > 0.01:
        arc(d, 250, 520, 80, -90, -90 + 180 * pr, rgba(ACC2, ca), 14)
    label(d, 250, 490, f"{int(round(30 * pr))}", WHITE, ca, size=54)
    label(d, 250, 630, "MINUTES", MUTED, ca, size=26, f=SEMI)
    label(d, 650, 440, f"+{int(round(14 * pr))}", ACC, ca, size=130)
    label(d, 650, 630, "MILES", MUTED, ca, size=26, f=SEMI)
    sa = ease_out((lt - dur + 1.2) / 0.4)
    label(d, 450, 750, "AAA MOBILE CHARGER TEST", MUTED, max(sa, ca * 0.0), size=24, f=SEMI)

def vis_z_outro(d, lt, t):
    dur = sdur("z_outro")
    if lt < dur * 0.55:
        a = ease_out(lt / 0.4)
        # shield over battery
        batt(d, 230, 330, 400, 160, 0.12, a, col=ACC2)
        k = back_out((lt - 0.3) / 0.45)
        if k > 0:
            for i in range(3):
                ph = (t * 1.1 + i / 3) % 1.0
                ring(d, 440, 410, 220 + ph * 50, rgba(ACC, clamp(k) * (1 - ph) * 0.8), 6)
        q = ease_out((lt - 0.4) / 0.4)
        label(d, 450, 60, "PROTECTS THE BATTERY", ACC, q, size=50)
        q2 = ease_out((lt - 1.4) / 0.4)
        label(d, 450, 700, "NOT A SPARE TANK", ACC2, q2, size=62)
        if q2 > 0:
            line(d, [(160, 800), (160 + 580 * q2, 800)], rgba(ACC2, q2), 8)
    else:
        k = back_out((lt - dur * 0.55) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.55 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"z_hook": vis_z_hook, "z_turtle": vis_z_turtle, "z_buffer": vis_z_buffer, "z_12v": vis_z_12v,
            "z_tow": vis_z_tow, "z_rescue": vis_z_rescue, "z_outro": vis_z_outro})
