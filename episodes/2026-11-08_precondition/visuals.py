# Episode visuals: battery preconditioning before DC fast charging (Hidden feature).

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


RED = (255, 84, 84)

def batt(d, x, y, w, h, frac, a, col=None, label_pct=True):
    # horizontal battery icon, fill frac in [0,1]
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=18 * S, fill=rgba(PANEL, a), outline=rgba(CHROME, a), width=6 * S)
    d.rounded_rectangle(p(x + w, y + h * 0.3, x + w + 22, y + h * 0.7), radius=6 * S, fill=rgba(CHROME, a))
    c = col or (ACC if frac > 0.25 else (ACC2 if frac > 0.1 else RED))
    fw = (w - 28) * clamp(frac)
    if fw > 2:
        d.rounded_rectangle(p(x + 14, y + 14, x + 14 + fw, y + h - 14), radius=10 * S, fill=rgba(c, a))


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


def snowflake(d, x, y, r, col, a):
    for k in range(6):
        aa = k * math.pi / 3
        ex, ey = x + math.cos(aa) * r, y + math.sin(aa) * r
        line(d, [(x, y), (ex, ey)], rgba(col, a), 8)
        for sgn in (-1, 1):
            mx, my = x + math.cos(aa) * r * 0.6, y + math.sin(aa) * r * 0.6
            ba = aa + sgn * 0.7
            line(d, [(mx, my), (mx + math.cos(ba) * r * 0.3, my + math.sin(ba) * r * 0.3)], rgba(col, a), 6)

def flow_dots(d, pts, t, col, a, n=5, speed=0.8, r=9):
    # dots moving along a polyline
    segs = []; tot = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        Lg = math.hypot(x1 - x0, y1 - y0); segs.append((x0, y0, x1, y1, Lg)); tot += Lg
    for i in range(n):
        u = ((t * speed + i / n) % 1.0) * tot
        for x0, y0, x1, y1, Lg in segs:
            if u <= Lg:
                f = u / Lg; circ(d, x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, r, rgba(col, a)); break
            u -= Lg

ICE = (110, 190, 255)
HEAT = (255, 122, 61)

def lerpc(c0, c1, u):
    u = clamp(u)
    return tuple(int(c0[i] + (c1[i] - c0[i]) * u) for i in range(3))

def thermo(d, x, y, h, frac, a, col):
    # vertical thermometer, bulb at bottom (x,y)
    d.rounded_rectangle(p(x - 22, y - h, x + 22, y), radius=22 * S, fill=rgba(PANEL, a), outline=rgba(CHROME, a), width=4 * S)
    circ(d, x, y + 20, 40, rgba(CHROME, a)); circ(d, x, y + 20, 32, rgba(col, a))
    fh = (h - 30) * clamp(frac)
    d.rounded_rectangle(p(x - 11, y - 10 - fh, x + 11, y + 10), radius=11 * S, fill=rgba(col, a))

def charger(d, x, y, sc, a, lit=1.0):
    d.rounded_rectangle(p(x - 60 * sc, y - 200 * sc, x + 60 * sc, y), radius=18 * S, fill=rgba(STEEL, a))
    d.rounded_rectangle(p(x - 42 * sc, y - 175 * sc, x + 42 * sc, y - 105 * sc), radius=10 * S, fill=rgba(BG, a))
    bolt(d, x, y - 140 * sc, 0.38 * sc, rgba(ACC, a * lit))
    line(d, [(x + 60 * sc, y - 80 * sc), (x + 100 * sc, y - 60 * sc), (x + 100 * sc, y - 10 * sc)], rgba(DARK, a), 10 * sc)

def heat_waves(d, x0, x1, y, t, a, col=HEAT):
    for k in range(4):
        ph = (t * 0.9 + k / 4) % 1.0
        xx = x0 + (x1 - x0) * (k + 0.5) / 4
        yy = y - ph * 70
        pts = [(xx + 10 * math.sin(j * 0.9 + t * 4), yy - j * 6) for j in range(8)]
        line(d, pts, rgba(col, a * (1 - ph)), 6)

# ---------- scenes ----------
def vis_pc_hook(d, lt, t):
    dur = sdur("pc_hook")
    a = ease_out(lt / 0.4)
    road(d, 560, t, a, speed=1.4)
    charger(d, 760, 540, 1.05, a)
    x = 90 + 240 * ease_out(lt / 2.5)
    car_side(d, x + 150, 445, 0.85, WHITE, a)
    # battery slab in floor heating up
    hk = ease_inout((lt - 0.8) / 2.5)
    col = lerpc(ICE, HEAT, hk)
    d.rounded_rectangle(p(x + 15, 455, x + 290, 485), radius=10 * S, fill=rgba(col, a))
    heat_waves(d, x + 40, x + 270, 330, t, a * hk)
    thermo(d, 110, 330, 230, 0.2 + 0.7 * hk, a, col)
    chip(d, 450, 640, "PRE-HEATING THE BATTERY", ACC, ease_out((lt - 1.5) / 0.4), size=38)
    label(d, 760, 598, "FAST CHARGER", MUTED, a, size=26, f=SEMI)

def vis_pc_cold(d, lt, t):
    a = ease_out(lt / 0.4)
    # cell cutaway: cathode | electrolyte | anode
    d.rounded_rectangle(p(110, 120, 790, 560), radius=26 * S, fill=rgba(PANEL, a), outline=rgba(STEEL, a), width=4 * S)
    d.rectangle(p(130, 140, 250, 540), fill=rgba((90, 100, 140), a))
    d.rectangle(p(650, 140, 770, 540), fill=rgba((60, 64, 72), a))
    for yy in range(160, 540, 28):
        line(d, [(660, yy), (760, yy)], rgba((95, 100, 110), a), 4)
    label(d, 190, 575, "CATHODE", MUTED, a, size=26, f=SEMI)
    label(d, 710, 575, "ANODE", MUTED, a, size=26, f=SEMI)
    label(d, 450, 575, "ELECTROLYTE", MUTED, a, size=26, f=SEMI)
    # ions crawling slowly
    slow = 1 - 0.85 * ease_inout((lt - 0.8) / 1.5)
    rng_ = [0.13, 0.41, 0.77, 0.29, 0.58, 0.91, 0.05, 0.66]
    for i, r0 in enumerate(rng_):
        u = (r0 + t * 0.35 * slow) % 1.0
        xx = 270 + 360 * u
        yy = 170 + i * 46 + 6 * math.sin(t * 3 + i)
        circ(d, xx, yy, 14, rgba(ACC, a))
        label(d, xx, yy - 14, "+", BG, a, size=22)
    ck = ease_out((lt - 0.6) / 0.5)
    snowflake(d, 450, 70, 46 * ck, ICE, ck)
    # resistance meter
    rk = ease_out((lt - 2.0) / 0.4)
    if rk > 0:
        d.rounded_rectangle(p(150, 650, 750, 700), radius=25 * S, fill=rgba(DARK, rk))
        w = 600 * (0.25 + 0.7 * ease_inout((lt - 2.2) / 1.2))
        d.rounded_rectangle(p(150, 650, 150 + w, 700), radius=25 * S, fill=rgba(ACC2, rk))
        label(d, 450, 720, "INTERNAL RESISTANCE ↑", ACC2, rk, size=36)

def vis_pc_plating(d, lt, t):
    dur = sdur("pc_plating")
    a = ease_out(lt / 0.4)
    # zoomed anode surface: graphite layers
    d.rounded_rectangle(p(470, 100, 800, 600), radius=20 * S, fill=rgba((60, 64, 72), a))
    for yy in range(125, 600, 34):
        line(d, [(490, yy), (780, yy)], rgba((100, 106, 118), a), 6)
    label(d, 635, 625, "GRAPHITE ANODE", MUTED, a, size=28, f=SEMI)
    # incoming current arrows (fast)
    fk = ease_out((lt - 0.4) / 0.4)
    for i in range(4):
        yy = 170 + i * 110
        ph = (t * 1.6 + i * 0.25) % 1.0
        arrow(d, 110 + 250 * ph, yy, 180 + 250 * ph, yy, rgba(ACC, fk * (1 - ph * 0.5)), w=10)
    chip(d, 230, 40, "FAST CURRENT", ACC, fk, size=30)
    # lithium metal growing on surface (spikes)
    g = ease_inout((lt - 1.4) / max(1.0, dur - 2.5))
    if g > 0:
        for i in range(7):
            yy = 130 + i * 70
            L_ = (40 + 30 * ((i * 37) % 3)) * g
            poly(d, [(470, yy - 16), (470, yy + 16), (470 - L_, yy + 4 * math.sin(i)), ], rgba(CHROME, a))
            poly(d, [(470 - L_ * 0.6, yy), (470 - L_ * 0.8, yy - 14 * g), (470 - L_ * 0.5, yy - 4)], rgba(CHROME, a))
        label(d, 300, 660, "LITHIUM METAL", CHROME, ease_out((lt - 1.8) / 0.4), size=36)
    wk = ease_out((lt - dur * 0.7) / 0.4)
    chip(d, 450, 730, "BATTERY WEAR ↑", RED, wk, size=36, tcol=WHITE)

def vis_pc_limit(d, lt, t):
    dur = sdur("pc_limit")
    a = ease_out(lt / 0.4)
    chip(d, 450, 20, "INL STUDY · SAME 30 MIN OF DC FAST CHARGING", PANEL, a, size=26, tcol=MUTED)
    # gauge: charging power being cut
    pk = ease_inout((lt - 0.3) / 1.6)
    pw = 1 - 0.55 * pk
    arc(d, 450, 300, 150, 150, 390, rgba(DARK, a), 26)
    arc(d, 450, 300, 150, 150, 150 + 240 * pw, rgba(lerpc(ACC, ACC2, pk), a), 26)
    label(d, 450, 255, "kW", MUTED, a, size=34, f=SEMI)
    label(d, 450, 300, "LIMITED" if pk > 0.5 else "CHARGING", lerpc(WHITE, ACC2, pk), a, size=34)
    # two bars
    bk = ease_inout((lt - 2.0) / 2.6)
    ba = ease_out((lt - 1.8) / 0.4)
    for i, (lab, frac, col) in enumerate((("77°F", 1.0, ACC), ("32°F", 0.64, ICE))):
        yy = 500 + i * 120
        label(d, 150, yy + 8, lab, WHITE, ba, size=40)
        d.rounded_rectangle(p(250, yy, 820, yy + 70), radius=20 * S, fill=rgba(DARK, ba))
        w = 570 * frac * bk
        if w > 10:
            d.rounded_rectangle(p(250, yy, 250 + w, yy + 70), radius=20 * S, fill=rgba(col, ba))
    ck = back_out((lt - 4.6) / 0.4)
    if ck > 0:
        chip(d, 690, 760, "−36% CHARGE", ACC2, clamp(ck), size=40)
    label(d, 330, 768, "AT FREEZING:", MUTED, ease_out((lt - 4.6) / 0.4), size=32, f=SEMI)

def vis_pc_nav(d, lt, t):
    dur = sdur("pc_nav")
    a = ease_out(lt / 0.4)
    # nav screen
    d.rounded_rectangle(p(60, 40, 840, 470), radius=30 * S, fill=rgba(PANEL, a), outline=rgba(STEEL, a), width=4 * S)
    for gx in range(100, 840, 80):
        line(d, [(gx, 60), (gx, 450)], rgba((28, 35, 46), a), 3)
    route = [(140, 400), (260, 400), (330, 290), (520, 300), (600, 160), (740, 130)]
    rk = ease_inout((lt - 0.3) / 1.2)
    n = max(2, int(len(route) * rk) + 1)
    line(d, route[:min(n, len(route))], rgba(ACC, a), 12)
    # pin
    pk = back_out((lt - 0.2) / 0.4)
    if pk > 0:
        circ(d, 740, 105, 32 * pk, rgba(ACC, clamp(pk)))
        bolt(d, 740, 105, 0.3 * pk, rgba(BG, clamp(pk)))
    # car dot along route
    u = ease_inout((lt - 1.2) / max(1.0, dur - 2.0))
    segs = list(zip(route, route[1:])); tot = sum(math.hypot(b[0] - a_[0], b[1] - a_[1]) for a_, b in segs)
    s_ = u * tot; cx, cy = route[0]
    for a_, b in segs:
        Lg = math.hypot(b[0] - a_[0], b[1] - a_[1])
        if s_ <= Lg:
            cx = a_[0] + (b[0] - a_[0]) * s_ / Lg; cy = a_[1] + (b[1] - a_[1]) * s_ / Lg; break
        s_ -= Lg; cx, cy = b
    circ(d, cx, cy, 22, rgba(WHITE, a)); circ(d, cx, cy, 10, rgba(BG, a))
    # battery temp bar heating up
    ta = ease_out((lt - 0.8) / 0.4)
    label(d, 450, 510, "BATTERY TEMPERATURE", MUTED, ta, size=30, f=SEMI)
    d.rounded_rectangle(p(80, 570, 820, 630), radius=30 * S, fill=rgba(DARK, ta))
    # target band 70-85 F on 0..100 scale
    bx0, bx1 = 80 + 740 * 0.70, 80 + 740 * 0.85
    d.rounded_rectangle(p(bx0, 556, bx1, 644), radius=16 * S, outline=rgba(ACC, ta), width=5 * S)
    tf = 0.25 + 0.53 * u
    if ta > 0:
        d.rounded_rectangle(p(80, 570, 80 + 740 * tf, 630), radius=30 * S, fill=rgba(lerpc(ICE, HEAT, u), ta))
    label(d, (bx0 + bx1) / 2, 660, "70–85°F", ACC, ta, size=40)
    label(d, 120, 660, "COLD", ICE, ta, size=30, f=SEMI)

def vis_pc_tip(d, lt, t):
    dur = sdur("pc_tip")
    a = ease_out(lt / 0.35)
    u = ease_inout(lt / max(0.8, dur - 0.3))
    arc(d, 450, 330, 220, 0, 360, rgba(DARK, a), 34)
    arc(d, 450, 330, 220, -90, -90 + 360 * u, rgba(ACC, a), 34)
    label(d, 450, 260, f"{int(round(30 * u))}", WHITE, a, size=130)
    label(d, 450, 410, "MIN", MUTED, a, size=40, f=SEMI)
    chip(d, 450, 640, "PLAN 20–30 MIN AHEAD", ACC, ease_out((lt - 0.4) / 0.3), size=40)

def vis_pc_outro(d, lt, t):
    dur = sdur("pc_outro")
    if lt < dur * 0.45:
        a = ease_out(lt / 0.3)
        batt(d, 250, 260, 380, 170, 0.85, a, col=ACC)
        heat_waves(d, 280, 600, 240, t, a, col=ACC)
        k = back_out((lt - 0.3) / 0.4)
        chip(d, 450, 520, "WARM = FASTER + HEALTHIER", ACC2, clamp(k), size=40)
    else:
        k = back_out((lt - dur * 0.45) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.45 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"pc_hook": vis_pc_hook, "pc_cold": vis_pc_cold, "pc_plating": vis_pc_plating, "pc_limit": vis_pc_limit,
            "pc_nav": vis_pc_nav, "pc_tip": vis_pc_tip, "pc_outro": vis_pc_outro})
