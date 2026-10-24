# Episode visuals: why DC fast charging slows down after ~80 %.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
SHEET = (52, 62, 78)
METAL = (176, 186, 200)

def sdur(name):
    for s in scenes:
        if s["visual"] == name:
            return s["vis_end"] - s["start"]
    return 4.0

def poly_line(d, pts, col, w):
    d.line([v * S for xy in pts for v in xy], fill=col, width=int(w * S), joint="curve")

def dashed_v(d, x, y0, y1, col, w=4, dash=16):
    y = y0
    while y < y1:
        d.line(p(x, y, x, min(y + dash, y1)), fill=col, width=int(w * S)); y += dash * 2

def dashed_h(d, x0, x1, y, col, w=4, dash=16):
    x = x0
    while x < x1:
        d.line(p(x, y, min(x + dash, x1), y), fill=col, width=int(w * S)); x += dash * 2

def ion(d, x, y, a=1.0, r=17, col=None):
    col = col or ACC
    d.ellipse(p(x - r - 6, y - r - 6, x + r + 6, y + r + 6), fill=rgba(col, 0.18 * a))  # glow
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=rgba(col, a))
    d.line(p(x - 8, y, x + 8, y), fill=rgba(BG, a), width=5 * S)
    d.line(p(x, y - 8, x, y + 8), fill=rgba(BG, a), width=5 * S)

def bolt(d, bx, by, bs, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    d.polygon(p(*[v for xx, yy in pts for v in (bx + xx * bs, by + yy * bs)]), fill=col)

def battery(d, x, y, w, h, frac, col, a=1.0):
    d.rounded_rectangle(p(x + 6, y + 8, x + w + 6, y + h + 8), radius=22 * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=22 * S, outline=rgba(WHITE, a), width=8 * S, fill=rgba((16, 20, 27), a))
    d.rounded_rectangle(p(x + w, y + h * 0.3, x + w + 22, y + h * 0.7), radius=8 * S, fill=rgba(WHITE, a))
    fw = (w - 32) * clamp(frac)
    if fw > 4:
        d.rounded_rectangle(p(x + 16, y + 16, x + 16 + fw, y + h - 16), radius=12 * S, fill=rgba(col, a))

# ---------- 1. charging curve ----------
def power_at(s):
    if s < 0.06: return 0.35 + 0.65 * s / 0.06
    if s < 0.55: return 1.0 - 0.14 * (s - 0.06) / 0.49
    return 0.86 * ((1 - s) / 0.45) ** 1.35 + 0.06 * (s - 0.55) / 0.45

def vis_curve(d, lt, t):
    dur = sdur("curve")
    ox, oy, x1, ytop = 120, 640, 820, 220
    k = ease_out(lt / 0.5)
    d.line(p(ox, ytop - 20, ox, oy), fill=rgba(MUTED, k), width=5 * S)
    d.line(p(ox, oy, x1 + 20, oy), fill=rgba(MUTED, k), width=5 * S)
    fs = FL("Inter-SemiBold.otf", 28)
    d.text(p(ox + 16, ytop - 40), "CHARGING POWER", font=fs, fill=rgba(MUTED, k))
    text_c(d, (ox + x1) / 2, oy + 60, "BATTERY CHARGE  →", fs, rgba(MUTED, k))
    for v in (0, 50, 100):
        text_c(d, ox + (x1 - ox) * v / 100, oy + 16, f"{v}%", FL("Inter-SemiBold.otf", 24), rgba(MUTED, k))
    x80 = ox + (x1 - ox) * 0.8
    a80 = ease_out((lt - 0.4) / 0.4)
    dashed_v(d, x80, ytop - 10, oy, rgba(WHITE, 0.5 * a80))
    send = 0.02 + 0.98 * ease_inout((lt - 0.3) / (dur * 0.8))
    def pt(s): return (ox + (x1 - ox) * s, oy - (oy - ytop) * power_at(s))
    n = max(2, int(120 * send))
    pts = [pt(send * i / (n - 1)) for i in range(n)]
    # area fill
    d.polygon(p(*[v for xy in pts + [(pts[-1][0], oy), (ox, oy)] for v in xy]), fill=rgba(ACC, 0.10))
    split = [q for q in pts if q[0] <= x80]
    late = [q for q in pts if q[0] >= x80 - 6]
    if len(split) > 1:
        poly_line(d, split, rgba(ACC, 0.25), 22); poly_line(d, split, rgba(ACC, 1), 9)
    if len(late) > 1:
        poly_line(d, late, rgba(ACC2, 0.25), 22); poly_line(d, late, rgba(ACC2, 1), 9)
    hx, hy = pts[-1]
    col = ACC if send < 0.8 else ACC2
    d.ellipse(p(hx - 18, hy - 18, hx + 18, hy + 18), fill=rgba(col, 1))
    d.ellipse(p(hx - 30, hy - 30, hx + 30, hy + 30), outline=rgba(col, 0.5), width=4 * S)
    text_c(d, x80, ytop - 58, "80%", FL("InterDisplay-Black.otf", 44), rgba(WHITE, a80))
    # labels
    af = ease_out((send - 0.2) / 0.1)
    text_c(d, 330, 330, "FAST", FL("InterDisplay-Black.otf", 54), rgba(ACC, af))
    asl = ease_out((send - 0.85) / 0.08)
    text_c(d, 765, 380, "SLOW", FL("InterDisplay-Black.otf", 46), rgba(ACC2, asl))
    # live counter
    text_c(d, 450, 740, f"{int(round(send * 100))}%", FL("InterDisplay-Black.otf", 96), rgba(col, k))

# ---------- graphite anode with ion "parking spots" ----------
SHEETS = [270, 350, 430, 510, 590, 670]
GAPS = [(a + b) / 2 for a, b in zip(SHEETS, SHEETS[1:])]
SLOT_X = [480 + 62 * i for i in range(6)]
SLOTS = [(x, y) for i in range(6) for y in GAPS for x in [SLOT_X[5 - i]]]  # fill deep end first, all rows
AN_X0, AN_X1 = 430, 840

def anode(d, a=1.0, label=True):
    d.rounded_rectangle(p(AN_X0 - 14, SHEETS[0] - 30, AN_X1 + 14, SHEETS[-1] + 30), radius=20 * S,
                        fill=rgba((18, 23, 31), a), outline=rgba(DARK, a), width=3 * S)
    for y in SHEETS:
        d.rounded_rectangle(p(AN_X0, y - 9, AN_X1, y + 9), radius=9 * S, fill=rgba(SHEET, a))
        for x in range(AN_X0 + 14, AN_X1 - 6, 28):
            d.ellipse(p(x - 5, y - 5, x + 5, y + 5), fill=rgba((96, 108, 126), a))
    if label:
        text_c(d, (AN_X0 + AN_X1) / 2, SHEETS[0] - 82, "GRAPHITE ANODE", FL("InterDisplay-Bold.otf", 34), rgba(WHITE, a))

def flying_ion(d, prog, start_y, tx, ty, a=1.0):
    """prog 0..1: electrolyte -> anode mouth -> slot."""
    if prog <= 0: return
    if prog < 0.65:
        q = ease_inout(prog / 0.65)
        x = 70 + (AN_X0 - 30 - 70) * q
        y = start_y + (ty - start_y) * q + math.sin(q * 7 + start_y) * 18 * (1 - q)
    else:
        q = ease_out((prog - 0.65) / 0.35)
        x = AN_X0 - 30 + (tx - AN_X0 + 30) * q; y = ty
    ion(d, x, y, a)

def electrolyte(d, a=1.0):
    d.rounded_rectangle(p(40, SHEETS[0] - 30, 380, SHEETS[-1] + 30), radius=20 * S, fill=rgba((14, 30, 30), 0.55 * a))
    text_c(d, 210, SHEETS[-1] + 46, "ELECTROLYTE", FL("Inter-SemiBold.otf", 26), rgba(MUTED, a))

def vis_garage(d, lt, t):
    dur = sdur("garage")
    k = ease_out(lt / 0.5)
    electrolyte(d, k); anode(d, k)
    n_fly = 14
    for i in range(n_fly):
        st = 0.5 + i * (dur - 2.0) / n_fly
        prog = (lt - st) / 1.1
        sx, sy = SLOTS[i]
        if prog >= 1: ion(d, sx, sy, 1)
        else: flying_ion(d, prog, 300 + (i * 97) % 360, sx, sy)
    # "P" parking sign
    pa = back_out((lt - 1.6) / 0.4)
    if pa > 0:
        cx, cy, r = 820, 100, 46 * pa
        d.rounded_rectangle(p(cx - r, cy - r, cx + r, cy + r), radius=14 * S, fill=rgba(ACC, clamp(pa)))
        text_c(d, cx, cy - 38 * pa, "P", FL("InterDisplay-Black.otf", max(1, int(64 * pa))), rgba(BG, clamp(pa)))
    la = ease_out((lt - 1.0) / 0.4)
    ion(d, 120, 175, la, r=14)
    d.text(p(150, 155), "LITHIUM ION", font=FL("InterDisplay-Bold.otf", 32), fill=rgba(ACC, la))

def current_meter(d, level, col, a=1.0, label="CURRENT"):
    x0, x1, y = 120, 780, 835
    d.text(p(x0, y - 56), label, font=FL("InterDisplay-Bold.otf", 30), fill=rgba(MUTED, a))
    d.rounded_rectangle(p(x0, y, x1, y + 34), radius=17 * S, fill=rgba(DARK, a))
    w = (x1 - x0) * clamp(level)
    if w > 30:
        d.rounded_rectangle(p(x0 - 4, y - 4, x0 + w + 4, y + 38), radius=19 * S, fill=rgba(col, 0.25 * a))
        d.rounded_rectangle(p(x0, y, x0 + w, y + 34), radius=17 * S, fill=rgba(col, a))

def vis_empty(d, lt, t):
    dur = sdur("empty")
    electrolyte(d); anode(d)
    base = 3
    for i in range(base): ion(d, *SLOTS[i])
    # big fast stream
    n = 12
    for i in range(n):
        st = 0.2 + i * (dur - 1.2) / n
        prog = (lt - st) / 0.75
        sx, sy = SLOTS[base + i]
        if prog >= 1: ion(d, sx, sy)
        else: flying_ion(d, prog, 290 + (i * 131) % 380, sx, sy)
    # flow arrows
    for j in range(3):
        ph = (t * 1.8 + j / 3) % 1.0
        ax = 90 + 260 * ph; ay = 200
        al = math.sin(ph * math.pi)
        d.polygon(p(ax, ay - 16, ax + 30, ay, ax, ay + 16), fill=rgba(ACC, al))
    filled = base + sum(1 for i in range(n) if lt - (0.2 + i * (dur - 1.2) / n) >= 0.75)
    free = len(SLOTS) - filled
    text_c(d, 630, 95, f"OPEN SPOTS: {free}", FL("InterDisplay-Black.otf", 40), rgba(ACC, 1))
    current_meter(d, 0.15 + 0.8 * ease_out(lt / 0.8), ACC, label="CHARGING CURRENT: HIGH")

def dendrite(d, x, y, g, seed):
    """Metallic lithium growth at the anode surface (g = 0..1)."""
    if g <= 0: return
    rnd = (seed * 9301 + 49297) % 233280 / 233280
    L_ = 105 * g
    tipx = x - L_; tipy = y + (rnd - 0.5) * 30 * g
    col = rgba(METAL, 1)
    d.line(p(x, y, tipx, tipy), fill=col, width=int(9 * S))
    for b in (0.45, 0.75):
        if g > b * 0.8:
            bx = x + (tipx - x) * b; by = y + (tipy - y) * b
            sgn = 1 if (seed + int(b * 10)) % 2 else -1
            d.line(p(bx, by, bx - 22 * g, by + sgn * 22 * g), fill=col, width=int(6 * S))
    d.ellipse(p(tipx - 9, tipy - 9, tipx + 9, tipy + 9), fill=rgba(WHITE, 1))

def vis_plating(d, lt, t):
    dur = sdur("plating")
    electrolyte(d); anode(d)
    full = len(SLOTS) - 2
    for i in range(full): ion(d, *SLOTS[i])
    # ions arrive but can't get in: stall at the surface
    for i in range(8):
        st = 0.3 + i * 0.45
        prog = (lt - st) / 0.9
        gy = GAPS[i % len(GAPS)]
        if 0 < prog < 1:
            q = ease_inout(prog)
            x = 70 + (AN_X0 - 40 - 70) * q
            y = 300 + ((i * 113) % 340) + (gy - 300 - ((i * 113) % 340)) * q
            ion(d, x, y)
    # metal growth on the surface, starting ~1.2 s in
    g = ease_out((lt - 1.2) / (dur * 0.55))
    for j, gy in enumerate(GAPS):
        dendrite(d, AN_X0 - 18, gy, clamp(g * (1.2 - 0.12 * j)), j + 3)
    a = ease_out((lt - 2.4) / 0.4)
    # warning tag
    tx, ty = 450, 60
    d.rounded_rectangle(p(tx - 280, ty, tx + 280, ty + 86), radius=43 * S, fill=rgba(ACC2, a))
    text_c(d, tx, ty + 14, "LITHIUM PLATING", FL("InterDisplay-Black.otf", 50), rgba(BG, a))
    text_c(d, 630, 740, "FEW OPEN SPOTS", FL("InterDisplay-Bold.otf", 34), rgba(MUTED, ease_out(lt / 0.4)))
    m = ease_out((lt - 1.4) / 0.4)
    text_c(d, 210, 790, "METALLIC Li", FL("InterDisplay-Bold.otf", 30), rgba(METAL, m))

# ---------- CC-CV ----------
def vis_cccv(d, lt, t):
    dur = sdur("cccv")
    ox, oy, x1, ytop = 110, 660, 820, 230
    k = ease_out(lt / 0.4)
    d.line(p(ox, ytop - 30, ox, oy), fill=rgba(MUTED, k), width=5 * S)
    d.line(p(ox, oy, x1 + 20, oy), fill=rgba(MUTED, k), width=5 * S)
    text_c(d, (ox + x1) / 2, oy + 20, "TIME  →", FL("Inter-SemiBold.otf", 28), rgba(MUTED, k))
    knee = 0.45
    def v_at(u): return 0.42 + 0.58 * (1 - (1 - min(u / knee, 1)) ** 1.8)
    def i_at(u): return 0.78 if u < knee else 0.08 + 0.70 * math.exp(-(u - knee) * 6.5)
    yv = lambda v: oy - (oy - ytop) * v
    # ceiling
    ca = ease_out((lt - 0.3) / 0.4)
    dashed_h(d, ox, x1, yv(1.0), rgba(WHITE, 0.55 * ca))
    d.text(p(x1 - 230, yv(1.0) - 58), "≈ 4.2 V CEILING", font=FL("InterDisplay-Bold.otf", 30), fill=rgba(WHITE, ca))
    u_end = 0.01 + 0.99 * ease_inout((lt - 0.4) / (dur * 0.78))
    n = max(2, int(100 * u_end))
    us = [u_end * j / (n - 1) for j in range(n)]
    vp = [(ox + (x1 - ox) * u, yv(v_at(u))) for u in us]
    ip = [(ox + (x1 - ox) * u, yv(i_at(u))) for u in us]
    for pts, col in ((vp, ACC), (ip, ACC2)):
        poly_line(d, pts, rgba(col, 0.22), 22); poly_line(d, pts, rgba(col, 1), 9)
        hx, hy = pts[-1]; d.ellipse(p(hx - 15, hy - 15, hx + 15, hy + 15), fill=rgba(col, 1))
    # legend
    lg = FL("InterDisplay-Bold.otf", 30)
    d.rounded_rectangle(p(130, 110, 170, 128), radius=9 * S, fill=rgba(ACC, k))
    d.text(p(182, 98), "VOLTAGE", font=lg, fill=rgba(ACC, k))
    d.rounded_rectangle(p(420, 110, 460, 128), radius=9 * S, fill=rgba(ACC2, k))
    d.text(p(472, 98), "CURRENT", font=lg, fill=rgba(ACC2, k))
    # phase bands
    xk = ox + (x1 - ox) * knee
    pa = ease_out((u_end - 0.1) / 0.1); pb = ease_out((u_end - knee - 0.08) / 0.1)
    ph = FL("InterDisplay-Black.otf", 30)
    d.rounded_rectangle(p(ox + 8, 720, xk - 8, 800), radius=16 * S, fill=rgba(ACC, 0.16 * pa), outline=rgba(ACC, pa), width=3 * S)
    text_c(d, (ox + xk) / 2, 742, "CONSTANT CURRENT", FL("InterDisplay-Black.otf", 26), rgba(ACC, pa))
    d.rounded_rectangle(p(xk + 8, 720, x1, 800), radius=16 * S, fill=rgba(ACC2, 0.16 * pb), outline=rgba(ACC2, pb), width=3 * S)
    text_c(d, (xk + x1) / 2, 742, "CONSTANT VOLTAGE", FL("InterDisplay-Black.otf", 26), rgba(ACC2, pb))
    if pb > 0: dashed_v(d, xk, ytop, oy, rgba(MUTED, 0.6 * pb))

# ---------- the numbers: 0-90 vs 90-100 ----------
def vis_bars(d, lt, t):
    dur = sdur("bars")
    T1 = 0.25; P1 = 1.1; T2 = T1 + P1 + 0.15; P2 = dur - T2 - 0.5
    u1 = ease_inout((lt - T1) / P1); u2 = ease_inout((lt - T2) / P2)
    soc = 90 * u1 + 10 * u2
    col = ACC if soc < 90 else ACC2
    battery(d, 200, 150, 470, 170, soc / 100, col)
    text_c(d, 450, 182, f"{int(round(soc))}%", FL("InterDisplay-Black.otf", 80), rgba(WHITE if soc < 55 else BG, 1))
    bw = 520; x0 = 300
    rows = [("0 → 90%", u1, ACC, 440), ("90 → 100%", u2, ACC2, 600)]
    for lab, u, c, y in rows:
        a = ease_out((lt - (T1 if c == ACC else T2) + 0.3) / 0.3)
        d.text(p(70, y + 6), lab, font=FL("InterDisplay-Black.otf", 40), fill=rgba(c, a))
        d.rounded_rectangle(p(x0, y, x0 + bw, y + 64), radius=32 * S, fill=rgba(DARK, a))
        w = bw * u
        if w > 40:
            d.rounded_rectangle(p(x0 - 4, y - 4, x0 + w + 4, y + 68), radius=34 * S, fill=rgba(c, 0.25))
            d.rounded_rectangle(p(x0, y, x0 + w, y + 64), radius=32 * S, fill=rgba(c, 1))
        # clock icon on bar head
        if 0 < u:
            cx, cy = x0 + max(w, 40) - 32 if w > 64 else x0 + 32, y + 32
            d.ellipse(p(cx - 20, cy - 20, cx + 20, cy + 20), outline=rgba(BG, 1), width=4 * S)
            ang = t * 6
            d.line(p(cx, cy, cx + math.cos(ang) * 14, cy + math.sin(ang) * 14), fill=rgba(BG, 1), width=4 * S)
    text_c(d, 450, 370, "CHARGING TIME", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, ease_out(lt / 0.4)))
    ea = back_out((lt - T2 - P2 + 0.1) / 0.4)
    if ea > 0:
        text_c(d, 450, 700 + 10 * (1 - clamp(ea)), "≈ SAME TIME", FL("InterDisplay-Black.otf", 64), rgba(WHITE, clamp(ea)))

# ---------- outro ----------
def vis_outro2(d, lt, t):
    dur = sdur("outro2")
    cut = dur * 0.45
    if lt < cut:
        k = back_out(lt / 0.4)
        frac = 0.8 + 0.2 * (0.5 + 0.5 * math.sin(t * 3))
        battery(d, 210, 230, 450, 170, frac * clamp(k), ACC)
        bolt(d, 435, 315, 0.9, rgba(BG, clamp(k)))
        a = ease_out((lt - 0.5) / 0.4)
        text_c(d, 450, 470, "80%  OR  100%?", FL("InterDisplay-Black.otf", 74), rgba(WHITE, a))
        # ticking clock
        cx, cy = 450, 690
        d.ellipse(p(cx - 70, cy - 70, cx + 70, cy + 70), outline=rgba(ACC2, a), width=8 * S)
        arc(d, cx, cy, 70, -90, -90 + (lt / cut) * 360, rgba(ACC2, a), 14)
        ang = -math.pi / 2 + lt * 4
        d.line(p(cx, cy, cx + math.cos(ang) * 50, cy + math.sin(ang) * 50), fill=rgba(WHITE, a), width=7 * S)
    else:
        k = back_out((lt - cut) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - cut - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

VIS.update({"curve": vis_curve, "garage": vis_garage, "empty": vis_empty, "plating": vis_plating,
            "cccv": vis_cccv, "bars": vis_bars, "outro2": vis_outro2})
