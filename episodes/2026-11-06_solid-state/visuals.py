# Episode visuals: solid-state batteries — what changes and why they're hard.

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
RED = (255, 80, 80)
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
    d.ellipse(p(x - r, y - r, x + r, y + r), outline=col, width=int(w * S))

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
    d.line(p(*[v for xy in pts for v in xy]), fill=col, width=int(w * S), joint="curve")

def arrow(d, x0, y0, x1, y1, col, w=10, head=26):
    line(d, [(x0, y0), (x1, y1)], col, w)
    ang = math.atan2(y1 - y0, x1 - x0)
    a1, a2 = ang + 2.6, ang - 2.6
    poly(d, [(x1 + math.cos(ang) * 6, y1 + math.sin(ang) * 6), (x1 + math.cos(a1) * head, y1 + math.sin(a1) * head),
             (x1 + math.cos(a2) * head, y1 + math.sin(a2) * head)], col)

def bolt(d, x, y, sc, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in pts], col)

def progress(d, x0, y, x1, frac, col, a, h=34):
    d.rounded_rectangle(p(x0, y, x1, y + h), radius=h / 2 * S, fill=rgba(DARK, a))
    if frac > 0.01:
        d.rounded_rectangle(p(x0 + 4, y + 4, x0 + 4 + (x1 - x0 - 8) * clamp(frac), y + h - 4), radius=(h - 8) / 2 * S, fill=rgba(col, a))


CATH = ACC2          # cathode
GRAPH = (62, 70, 84) # graphite
LIM = (205, 214, 226) # lithium metal (silver)
LIQ = (40, 120, 150)  # liquid electrolyte (teal-ish)
CER = (150, 160, 176) # ceramic solid

def flame(d, cx, cy, sc, a, t):
    fl = 1 + 0.08 * math.sin(t * 14)
    for r, col in [(1.0, ACC2), (0.6, (255, 200, 80))]:
        h = 90 * sc * r * fl; w = 46 * sc * r
        pts = []
        for k in range(25):
            u = k / 24 * 2 * math.pi
            x = math.sin(u) * w * (0.5 + 0.5 * math.cos(u / 2) ** 2)
            y = -math.cos(u) * h * 0.55 + (h * 0.25 if math.cos(u) < 0 else 0)
            pts.append((cx + x * (0.9 if math.cos(u) > 0 else 1), cy + y * (1.4 if math.cos(u) > 0 else 0.7)))
        poly(d, pts, rgba(col, a))

def cell_frame(d, x0, y0, x1, y1, a):
    d.rounded_rectangle(p(x0 - 10, y0 - 10, x1 + 10, y1 + 10), radius=26 * S, fill=rgba(PANEL, a), outline=rgba(STEEL, a), width=4 * S)

def graphite(d, x0, y0, x1, y1, a):
    d.rectangle(p(x0, y0, x1, y1), fill=rgba(GRAPH, a))
    for k in range(int((y1 - y0) / 26)):
        yy = y0 + 13 + k * 26
        line(d, [(x0 + 8, yy), (x1 - 8, yy)], rgba((95, 104, 120), a), 5)

def cathode(d, x0, y0, x1, y1, a):
    d.rectangle(p(x0, y0, x1, y1), fill=rgba(CATH, a))
    for k in range(int((y1 - y0) / 40)):
        for j in range(2):
            circ(d, x0 + 30 + j * ((x1 - x0) - 60), y0 + 24 + k * 40, 9, rgba((200, 85, 40), a))

def ceramic(d, x0, y0, x1, y1, a):
    d.rectangle(p(x0, y0, x1, y1), fill=rgba(CER, a))
    # grain pattern
    for k in range(int((y1 - y0) / 34) + 1):
        for j in range(int((x1 - x0) / 34) + 1):
            gx = x0 + j * 34 + (17 if k % 2 else 0); gy = y0 + k * 34
            if x0 < gx < x1 and y0 < gy < y1:
                d.line(p(gx, gy, min(gx + 20, x1), min(gy + 14, y1)), fill=rgba((120, 130, 146), a), width=3 * S)

# ---------- scenes ----------
def vis_ss_hook(d, lt, t):
    a = ease_out(lt / 0.4)
    label(d, 450, 60, "SAME SIZE PACK", MUTED, a, size=34)
    # two battery packs, today's vs solid-state: energy bars build up
    rows = [("TODAY", 0.62, WHITE), ("SOLID-STATE", 0.92, ACC)]
    for i, (nm, frac, col) in enumerate(rows):
        y = 170 + i * 230
        ka = ease_out((lt - 0.2 - 0.5 * i) / 0.4)
        label(d, 450, y - 10, nm, col, ka, size=40)
        x0, x1 = 130, 730
        d.rounded_rectangle(p(x0, y + 50, x1, y + 170), radius=22 * S, outline=rgba(STEEL, ka), width=6 * S)
        d.rounded_rectangle(p(x1 + 4, y + 85, x1 + 30, y + 135), radius=8 * S, fill=rgba(STEEL, ka))
        f = frac * ease_inout((lt - 0.5 - 0.6 * i) / 1.2)
        if f > 0.01:
            d.rounded_rectangle(p(x0 + 12, y + 62, x0 + 12 + (x1 - x0 - 24) * f, y + 158), radius=14 * S, fill=rgba(col, ka))
    q = back_out((lt - 2.4) / 0.5)
    if q > 0:
        pul = 1 + 0.05 * math.sin(t * 6)
        circ(d, 450, 730, 85 * q * pul, rgba(ACC2, clamp(q)))
        label(d, 450, 730 - 62 * q, "?", BG, clamp(q), size=110 * q)

def vis_ss_liquid(d, lt, t):
    a = ease_out(lt / 0.4)
    x0, x1, y0, y1 = 110, 790, 120, 560
    cell_frame(d, x0, y0, x1, y1, a)
    cathode(d, x0, y0, x0 + 150, y1, a)
    graphite(d, x1 - 150, y0, x1, y1, a)
    # liquid with moving waves
    lx0, lx1 = x0 + 150, x1 - 150
    d.rectangle(p(lx0, y0, lx1, y1), fill=rgba(LIQ, a * 0.75))
    for k in range(6):
        yy = y0 + 40 + k * 75
        pts = [(lx0 + u * 8, yy + 8 * math.sin(u * 0.5 + t * 3 + k)) for u in range(int((lx1 - lx0) / 8) + 1)]
        line(d, pts, rgba((90, 180, 205), a * 0.8), 4)
    # ions flowing cathode -> anode
    for i in range(9):
        ph = (t * 0.45 + i / 9) % 1.0
        ix = lx0 + 10 + (lx1 - lx0 - 20) * ph
        iy = y0 + 40 + (i * 53) % (y1 - y0 - 80) + 12 * math.sin(t * 2 + i)
        circ(d, ix, iy, 14, rgba(ACC, a))
        label(d, ix, iy - 13, "+", BG, a, size=20)
    la = ease_out((lt - 0.8) / 0.4)
    label(d, x0 + 75, y1 + 30, "CATHODE", CATH, la, size=26)
    label(d, 450, y1 + 30, "LIQUID ELECTROLYTE", (110, 200, 225), la, size=26)
    label(d, x1 - 75, y1 + 30, "GRAPHITE", MUTED, la, size=26)
    label(d, 450, 70, "LITHIUM IONS", ACC, la, size=30)
    fa = back_out((lt - 2.4) / 0.45)
    if fa > 0:
        flame(d, 450, 300, 1.4 * fa, clamp(fa), t)
        chip(d, 450, 690, "FLAMMABLE", ACC2, clamp(fa), size=44)

def vis_ss_solid(d, lt, t):
    a = ease_out(lt / 0.4)
    x0, x1, y0, y1 = 110, 790, 100, 470
    cell_frame(d, x0, y0, x1, y1, a)
    cathode(d, x0, y0, x0 + 150, y1, a)
    lx0, lx1 = x0 + 150, x1 - 150
    # liquid drains down, ceramic slab slides in from the top (thin layer)
    drain = ease_inout((lt - 0.3) / 0.8)
    d.rectangle(p(lx0, y0 + (y1 - y0) * drain, lx1, y1), fill=rgba(LIQ, a * 0.75 * (1 - drain)))
    sx0, sx1 = 260, 340
    k = ease_out((lt - 0.9) / 0.6)
    if k > 0:
        ceramic(d, sx0, y0, sx1, y0 + (y1 - y0) * k, a)
    label(d, (sx0 + sx1) / 2, y0 - 50, "SOLID LAYER", WHITE, ease_out((lt - 1.3) / 0.3), size=28)
    # anode: graphite morphs to lithium metal and the freed space shrinks the cell
    m = ease_inout((lt - 2.0) / 0.7)
    gx0 = x1 - 150
    if m < 1:
        graphite(d, gx0, y0, x1, y1, a * (1 - m))
    if m > 0:
        lmx0 = sx1 + 6
        d.rectangle(p(lmx0, y0, lmx0 + 60 + (1 - m) * 200, y1), fill=rgba(LIM, a * m))
        sh = (t * 120) % (y1 - y0)
        line(d, [(lmx0 + 12, y0 + sh), (lmx0 + 40, y0 + sh - 30)], rgba(WHITE, a * m * 0.9), 6)
        label(d, lmx0 + 110, y1 + 25, "LITHIUM METAL", LIM, m, size=28)
        label(d, 600, (y0 + y1) / 2 - 18, "SPACE SAVED", MUTED, m, size=30)
    # charge-per-anode bars
    ba = ease_out((lt - 2.8) / 0.4)
    label(d, 450, 560, "CHARGE THE ANODE CAN HOLD", MUTED, ba, size=28)
    for i, (nm, frac, col) in enumerate([("GRAPHITE", 0.12, GRAPH if False else MUTED), ("LITHIUM METAL", 1.0, ACC)]):
        yy = 620 + i * 100
        label(d, 230, yy + 4, nm, col, ba, size=28)
        progress(d, 370, yy, 790, frac * ease_out((lt - 3.0 - 0.3 * i) / 0.9), col, ba, h=46)

def vis_ss_gaps(d, lt, t):
    dur = sdur("ss_gaps")
    a = ease_out(lt / 0.4)
    # vertical stack: cathode / solid / lithium, viewed from the side
    cx0, cx1 = 170, 730
    squeeze = ease_inout((lt - dur * 0.58) / 0.6)
    breathe = math.sin(t * 3.2)
    sw = 1 - squeeze
    gap = max(0, breathe) * 26 * sw * ease_out((lt - 0.8) / 0.5)
    ytop = 180
    # cathode
    cathode(d, cx0, ytop, cx1, ytop + 120 + breathe * 8 * sw, a)
    y = ytop + 120 + breathe * 8 * sw + gap
    ceramic(d, cx0, y, cx1, y + 70, a)
    y2 = y + 70 + gap
    lh = 110 - breathe * 14 * sw
    d.rectangle(p(cx0, y2, cx1, y2 + lh), fill=rgba(LIM, a))
    label(d, 450, ytop + 44, "CATHODE", BG, a, size=30)
    label(d, 450, y + 18, "SOLID", BG, a, size=28)
    label(d, 450, y2 + lh / 2 - 18, "LITHIUM METAL", BG, a, size=30)
    if gap > 3:
        for gy in (y - gap / 2, y2 - gap / 2):
            for k in range(5):
                xx = cx0 + 60 + k * 110
                line(d, [(xx, gy), (xx + 40, gy)], rgba(ACC2, a), 4)
    ga = ease_out((lt - 1.0) / 0.4) * sw
    chip(d, 450, 590, "GAPS  →  RESISTANCE ↑", ACC2, ga, size=34)
    # pressure plates + arrows
    if squeeze > 0:
        pa = clamp(squeeze * 1.5)
        d.rounded_rectangle(p(cx0 - 20, ytop - 40 - 30 * (1 - squeeze), cx1 + 20, ytop - 14 - 30 * (1 - squeeze)), radius=8 * S, fill=rgba(STEEL, pa))
        bot = y2 + lh + 14 + 30 * (1 - squeeze)
        d.rounded_rectangle(p(cx0 - 20, bot, cx1 + 20, bot + 26), radius=8 * S, fill=rgba(STEEL, pa))
        for xx in (250, 450, 650):
            off = 8 * math.sin(t * 6)
            arrow(d, xx, 40 + off, xx, ytop - 52, rgba(ACC, pa), 10, 24)
            arrow(d, xx, bot + 110 - off, xx, bot + 36, rgba(ACC, pa), 10, 24)
        chip(d, 450, 700, "KEEP IT SQUEEZED", ACC, ease_out((lt - dur * 0.58 - 0.4) / 0.4), size=40)

def vis_ss_dendrite(d, lt, t):
    a = ease_out(lt / 0.4)
    x0, x1 = 130, 770
    cathode(d, x0, 110, x1, 210, a)
    ceramic(d, x0, 210, x1, 450, a)
    d.rectangle(p(x0, 450, x1, 560), fill=rgba(LIM, a))
    label(d, 450, 70, "CATHODE", CATH, a, size=26)
    label(d, 450, 575, "LITHIUM METAL", LIM, a, size=26)
    g = ease_inout((lt - 0.4) / 2.4)
    # branching needle from anode upward
    rnd = [0.3, -0.5, 0.6, -0.2, 0.4, -0.6, 0.2, -0.3]
    def branch(x, y, ang, length, depth, prog):
        if prog <= 0 or depth > 3: return
        seg = length * min(1, prog)
        ex, ey = x + math.cos(ang) * seg, y + math.sin(ang) * seg
        line(d, [(x, y), (ex, ey)], rgba(WHITE, a), max(3, 11 - depth * 3))
        if prog > 1:
            branch(ex, ey, ang + 0.45 * rnd[depth * 2 % 8], length * 0.8, depth + 1, prog - 1)
            if depth < 2:
                branch(ex, ey, ang - 0.7 + rnd[(depth * 2 + 1) % 8] * 0.3, length * 0.5, depth + 2, prog - 1)
    branch(450, 452, -math.pi / 2 - 0.1, 70, 0, g * 4.0)
    # cracks spreading in ceramic
    ca = ease_out((lt - 1.4) / 0.8)
    if ca > 0:
        for sgn in (-1, 1):
            pts = [(450, 360), (450 + sgn * 60 * ca, 330), (450 + sgn * 110 * ca, 350), (450 + sgn * 170 * ca, 300)]
            line(d, pts, rgba(BG, a), 5)
    label(d, 640, 250, "DENDRITE", WHITE, ease_out((lt - 0.8) / 0.4), size=30)
    sp = ease_out((lt - 2.9) / 0.2)
    if sp > 0:
        fl = 0.6 + 0.4 * abs(math.sin(t * 18))
        for k in range(8):
            ang = k * math.pi / 4 + t
            line(d, [(450, 212), (450 + math.cos(ang) * 70 * fl, 212 + math.sin(ang) * 70 * fl)], rgba(ACC, sp), 7)
        circ(d, 450, 212, 26, rgba(WHITE, sp))
        chip(d, 450, 660, "SHORT CIRCUIT", ACC2, sp, size=46)

def vis_ss_progress(d, lt, t):
    dur = sdur("ss_progress")
    a = ease_out(lt / 0.4)
    label(d, 450, 40, "2025 TEST DRIVE · ONE CHARGE", MUTED, a, size=30)
    # stylised route Stuttgart (bottom) -> Malmo (top)
    route = [(300, 560), (330, 470), (310, 390), (370, 300), (430, 240), (470, 170), (560, 120)]
    line(d, route, rgba(DARK, a), 14)
    prog = ease_inout((lt - 0.4) / (dur * 0.7))
    # partial route
    segs = len(route) - 1; pos = prog * segs; idx = min(int(pos), segs - 1); fr = pos - idx
    pts = route[:idx + 1] + [(route[idx][0] + (route[idx + 1][0] - route[idx][0]) * fr, route[idx][1] + (route[idx + 1][1] - route[idx][1]) * fr)]
    if len(pts) > 1: line(d, pts, rgba(ACC, a), 14)
    circ(d, route[0][0], route[0][1], 18, rgba(WHITE, a))
    circ(d, route[-1][0], route[-1][1], 18, rgba(WHITE, a))
    label(d, route[0][0] - 10, route[0][1] + 28, "STUTTGART", WHITE, a, size=28)
    label(d, route[-1][0] + 110, route[-1][1] - 18, "MALMÖ", WHITE, a, size=28)
    cx, cy = pts[-1]
    circ(d, cx, cy, 28 + 4 * math.sin(t * 6), rgba(ACC, a * 0.35)); circ(d, cx, cy, 16, rgba(ACC, a))
    # counter
    miles = int(round(749 * prog))
    label(d, 680, 330, f"{miles}", ACC, a, size=96)
    label(d, 680, 440, "MILES", WHITE, a, size=34)
    # battery gauge drains but doesn't empty
    bx0, bx1, by = 560, 800, 520
    d.rounded_rectangle(p(bx0, by, bx1, by + 70), radius=14 * S, outline=rgba(STEEL, a), width=5 * S)
    d.rounded_rectangle(p(bx1 + 4, by + 20, bx1 + 18, by + 50), radius=4 * S, fill=rgba(STEEL, a))
    lvl = 1 - 0.9 * prog
    d.rounded_rectangle(p(bx0 + 10, by + 10, bx0 + 10 + (bx1 - bx0 - 20) * lvl, by + 60), radius=8 * S, fill=rgba(ACC if lvl > 0.25 else ACC2, a))
    fa = ease_out((lt - dur * 0.75) / 0.4)
    chip(d, 450, 680, "1,205 km · NO CHARGING STOP", ACC, fa, size=36)
    label(d, 450, 790, "137 km STILL LEFT", MUTED, fa, size=28)

def vis_ss_outro(d, lt, t):
    dur = sdur("ss_outro")
    if lt < dur * 0.6:
        a = ease_out(lt / 0.4)
        x0, x1, y = 120, 780, 330
        line(d, [(x0, y), (x1, y)], rgba(DARK, a), 12)
        line(d, [(x0, y), (x0 + (x1 - x0) * ease_inout((lt - 0.2) / 1.6), y)], rgba(ACC, a), 12)
        marks = [(0.0, "2025", "TEST CARS"), (0.55, "2027–28", "TOYOTA TARGET"), (1.0, "~2030", "MERCEDES GOAL")]
        for i, (f, yr, nm) in enumerate(marks):
            ka = back_out((lt - 0.3 - 0.55 * i) / 0.4)
            if ka <= 0: continue
            xx = x0 + (x1 - x0) * f
            circ(d, xx, y, 26 * ka, rgba(ACC if i < 2 else ACC2, clamp(ka)))
            label(d, xx, y - 110, yr, WHITE, clamp(ka), size=46)
            label(d, xx, y + 50, nm, MUTED if i != 1 else ACC, clamp(ka), size=28)
        q = ease_out((lt - 1.8) / 0.4)
        label(d, 450, 560, "WOULD YOU WAIT?", WHITE, q, size=72)
    else:
        k = back_out((lt - dur * 0.6) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.6 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"ss_hook": vis_ss_hook, "ss_liquid": vis_ss_liquid, "ss_solid": vis_ss_solid, "ss_gaps": vis_ss_gaps,
            "ss_dendrite": vis_ss_dendrite, "ss_progress": vis_ss_progress, "ss_outro": vis_ss_outro})
