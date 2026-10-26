# Episode visuals: What would happen if… you drive an EV at 20°F? (winter range + heat pumps)
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
ICE = (120, 200, 255)
RED = (255, 84, 84)

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

def lerpc(c0, c1, f):
    f = clamp(f)
    return tuple(int(c0[i] + (c1[i] - c0[i]) * f) for i in range(3))

def snowflake(d, cx, cy, r, col, a=1.0, rot=0.0):
    w = max(2, int(r * 0.16))
    for k in range(6):
        ang = rot + k * math.pi / 3
        x1, y1 = cx + math.cos(ang) * r, cy + math.sin(ang) * r
        d.line(p(cx, cy, x1, y1), fill=rgba(col, a), width=int(w * S))
        for side in (-1, 1):
            bx, by = cx + math.cos(ang) * r * 0.6, cy + math.sin(ang) * r * 0.6
            b2 = ang + side * 0.7
            d.line(p(bx, by, bx + math.cos(b2) * r * 0.32, by + math.sin(b2) * r * 0.32), fill=rgba(col, a), width=int(w * S))

def snowfall(d, t, a=1.0, n=22, seed=3):
    for i in range(n):
        x = (i * 137 + seed * 53) % 880 + 10
        sp = 40 + (i * 29) % 50
        y = ((t * sp + i * 97) % 960) - 40
        r = 6 + (i * 7) % 9
        snowflake(d, x + math.sin(t + i) * 12, y, r, ICE, 0.35 * a, rot=t * 0.5 + i)

def thermometer(d, cx, top, bot, frac, col, a=1.0):
    # tube
    d.rounded_rectangle(p(cx - 30, top, cx + 30, bot), radius=30 * S, fill=rgba(PANEL, a), outline=rgba(MUTED, a), width=int(4 * S))
    d.ellipse(p(cx - 55, bot - 30, cx + 55, bot + 80), fill=rgba(PANEL, a), outline=rgba(MUTED, a), width=int(4 * S))
    d.ellipse(p(cx - 42, bot - 17, cx + 42, bot + 67), fill=rgba(col, a))
    h = (bot - top - 30) * frac
    d.rounded_rectangle(p(cx - 16, bot - h, cx + 16, bot + 20), radius=16 * S, fill=rgba(col, a))
    for i in range(6):
        y = top + 30 + i * (bot - top - 40) / 5
        d.line(p(cx + 36, y, cx + 56, y), fill=rgba(MUTED, a), width=int(4 * S))

def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

def flow_arrow(d, x0, y0, x1, y1, t, col, a=1.0, w=10, n=5, speed=0.9):
    """Line with moving chevron dots showing direction of flow."""
    d.line(p(x0, y0, x1, y1), fill=rgba(col, 0.25 * a), width=int(w * S))
    L_ = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L_, (y1 - y0) / L_
    for i in range(n):
        f = (t * speed + i / n) % 1.0
        x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        s_ = w * 1.6
        poly(d, [(x + ux * s_, y + uy * s_), (x - ux * s_ - uy * s_, y - uy * s_ + ux * s_), (x - ux * s_ + uy * s_, y - uy * s_ - ux * s_)], rgba(col, a * (0.4 + 0.6 * math.sin(f * math.pi))))

def heat_waves(d, cx, cy, t, col, a=1.0, n=3, h=90, spread=40):
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * spread
        pts = []
        for k in range(13):
            yy = cy - k * h / 12
            pts.append((x + math.sin(k * 0.9 - t * 6 + i) * 10, yy))
        ph = (t * 1.2 + i * 0.3) % 1.0
        d.line([v * S for xy in pts for v in xy], fill=rgba(col, a * (0.5 + 0.5 * math.sin(ph * math.pi))), width=int(8 * S), joint="curve")

# ---------------- scene 1: hook — thermometer drops, range bar shrinks to 59% ----------------
def vis_wr_hook(d, lt, t):
    k = ease_inout((lt - 0.3) / 2.2)
    snowfall(d, t, a=k)
    temp = 75 - 55 * k
    col = lerpc(ACC2, ICE, k)
    thermometer(d, 170, 120, 560, 0.85 - 0.55 * k, col)
    text_c(d, 170, 690, f"{int(round(temp))}°F", FL("InterDisplay-Black.otf", 72), rgba(col, 1))
    # range bar
    a = ease_out((lt - 0.2) / 0.5)
    text_c(d, 590, 120, "RANGE", FL("InterDisplay-Bold.otf", 40), rgba(MUTED, a))
    x0, x1, y0, y1 = 360, 820, 200, 640
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=28 * S, fill=rgba(PANEL, a), outline=rgba(DARK, a), width=int(5 * S))
    r = ease_inout((lt - 2.6) / 1.6)
    frac = 1.0 - 0.41 * r
    top = y1 - 20 - (y1 - y0 - 40) * frac
    d.rounded_rectangle(p(x0 + 20, top, x1 - 20, y1 - 20), radius=18 * S, fill=rgba(lerpc(ACC, ICE, r), a))
    # lost portion outline
    if r > 0.01:
        lost_top = y1 - 20 - (y1 - y0 - 40)
        if top - 8 > lost_top + 40:
            d.rounded_rectangle(p(x0 + 20, lost_top, x1 - 20, top - 8), radius=18 * S, outline=rgba(RED, r), width=int(4 * S))
        text_c(d, 590, (lost_top + top) / 2 - 30, f"−{int(round(41 * r))}%", FL("InterDisplay-Black.otf", 64), rgba(RED, r))
    text_c(d, 590, top + 40, f"{int(round(100 * frac))}", FL("InterDisplay-Black.otf", 96), rgba(BG, a))
    text_c(d, 590, 680, "MILES LEFT OF EVERY 100", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, a))
    text_c(d, 590, 730, "AAA LAB TEST · HEATER ON", FL("Inter-SemiBold.otf", 26), rgba(MUTED, ease_out((lt - 3) / 0.5)))

# ---------------- scene 2: battery cell cutaway, ions slow as electrolyte thickens ----------------
def vis_wr_battery(d, lt, t):
    cold = ease_inout((lt - 0.8) / 2.0)
    x0, x1, y0, y1 = 110, 790, 170, 600
    d.rounded_rectangle(p(x0 - 10, y0 - 10, x1 + 10, y1 + 10), radius=30 * S, fill=rgba(DARK, 1))
    # electrolyte gets bluer / denser
    ec = lerpc((30, 50, 40), (28, 52, 80), cold)
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=24 * S, fill=rgba(ec, 1))
    # electrodes
    d.rounded_rectangle(p(x0 + 20, y0 + 20, x0 + 140, y1 - 20), radius=14 * S, fill=rgba((70, 78, 92), 1))
    d.rounded_rectangle(p(x1 - 140, y0 + 20, x1 - 20, y1 - 20), radius=14 * S, fill=rgba(ACC2, 0.85))
    text_c(d, x0 + 80, y1 + 26, "ANODE", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, 1))
    text_c(d, x1 - 80, y1 + 26, "CATHODE", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, 1))
    text_c(d, 450, y1 + 26, "ELECTROLYTE", FL("InterDisplay-Bold.otf", 28), rgba(lerpc(ACC, ICE, cold), 1))
    # viscosity texture: drifting blobs
    for i in range(14):
        bx = x0 + 170 + (i * 61) % 400
        by = y0 + 40 + (i * 83) % 350 + math.sin(t * 0.8 + i) * 8
        d.ellipse(p(bx - 26, by - 18, bx + 26, by + 18), fill=rgba(ICE, 0.10 * cold))
    # ions travelling anode -> cathode; speed falls with cold
    tt = 0.0; steps = 40
    for j in range(steps):
        u = lt * (j + 0.5) / steps
        tt += (0.55 - 0.47 * ease_inout((u - 0.8) / 2.0)) * lt / steps
    for i in range(9):
        f = (tt + i / 9) % 1.0
        x = x0 + 160 + (x1 - x0 - 320) * f
        y = y0 + 50 + ((i * 4) % 9) * 40 + math.sin(f * 6 + i) * 10
        col = lerpc(ACC, ICE, cold)
        d.ellipse(p(x - 22, y - 22, x + 22, y + 22), fill=rgba(col, 0.2))
        d.ellipse(p(x - 13, y - 13, x + 13, y + 13), fill=rgba(col, 1))
        text_c(d, x, y - 11, "+", FL("InterDisplay-Black.otf", 18), rgba(BG, 1))
    # labels
    a = ease_out((lt - 0.2) / 0.4)
    text_c(d, 450, 70, "Li⁺ IONS", FL("InterDisplay-Black.otf", 56), rgba(WHITE, a))
    sp = int(round(100 - 70 * cold))
    d.rounded_rectangle(p(250, 700, 650, 800), radius=26 * S, fill=rgba(lerpc(ACC, ICE, cold), ease_out((lt - 1.0) / 0.4)))
    text_c(d, 450, 720, "SLOWER" if cold > 0.5 else "FLOWING", FL("InterDisplay-Black.otf", 50), rgba(BG, ease_out((lt - 1.0) / 0.4)))
    snowflake(d, 820, 90, 40, ICE, cold, rot=t * 0.6)

# ---------------- scene 3: gas engine waste heat vs EV paying from battery ----------------
def vis_wr_heat(d, lt, t):
    dur = sdur("wr_heat")
    a1 = ease_out(lt / 0.4)
    # left: engine block
    text_c(d, 225, 60, "GAS CAR", FL("InterDisplay-Black.otf", 44), rgba(WHITE, a1))
    d.rounded_rectangle(p(110, 260, 340, 470), radius=24 * S, fill=rgba(DARK, a1))
    for i in range(4):
        d.rounded_rectangle(p(130 + i * 52, 200, 170 + i * 52, 262), radius=8 * S, fill=rgba((70, 78, 92), a1))
    d.ellipse(p(185, 320, 265, 400), fill=rgba(ACC2, a1 * (0.7 + 0.3 * math.sin(t * 8))))
    heat_waves(d, 225, 190, t, ACC2, a1, n=4, h=80, spread=45)
    flow_arrow(d, 225, 490, 225, 620, t, ACC2, a1, w=10)
    text_c(d, 225, 650, "WASTE HEAT", FL("InterDisplay-Bold.otf", 34), rgba(ACC2, a1))
    text_c(d, 225, 700, "≈ FREE", FL("InterDisplay-Black.otf", 60), rgba(ACC2, a1))
    # divider
    d.line(p(450, 90, 450, 790), fill=rgba(DARK, a1), width=int(4 * S))
    # right: battery draining into heater
    a2 = ease_out((lt - dur * 0.45) / 0.4)
    text_c(d, 675, 60, "ELECTRIC", FL("InterDisplay-Black.otf", 44), rgba(WHITE, a2))
    drain = ease_inout((lt - dur * 0.5) / (dur * 0.45))
    bx0, bx1, by0, by1 = 575, 775, 170, 470
    d.rounded_rectangle(p(bx0 + 60, by0 - 22, bx1 - 60, by0 + 4), radius=8 * S, fill=rgba(MUTED, a2))
    d.rounded_rectangle(p(bx0, by0, bx1, by1), radius=22 * S, fill=rgba(PANEL, a2), outline=rgba(ACC, a2), width=int(5 * S))
    lvl = 0.9 - 0.35 * drain
    d.rounded_rectangle(p(bx0 + 16, by1 - 16 - (by1 - by0 - 32) * lvl, bx1 - 16, by1 - 16), radius=14 * S, fill=rgba(ACC, a2))
    flow_arrow(d, 675, 490, 675, 620, t, ACC, a2, w=10)
    text_c(d, 675, 650, "PAID FROM", FL("InterDisplay-Bold.otf", 34), rgba(ACC, a2))
    text_c(d, 675, 700, "BATTERY", FL("InterDisplay-Black.otf", 60), rgba(ACC, a2))

# ---------------- scene 4: resistive heater = toaster, 1 in -> 1 out ----------------
def vis_wr_heater(d, lt, t):
    a = ease_out(lt / 0.4)
    # heater coil body
    x0, x1, y0, y1 = 250, 650, 180, 480
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=30 * S, fill=rgba(PANEL, a), outline=rgba(DARK, a), width=int(6 * S))
    glow_k = ease_out((lt - 0.6) / 1.0)
    for i in range(6):
        y = y0 + 45 + i * 42
        pts = [(x0 + 40 + k * 16, y + (8 if k % 2 else -8)) for k in range(21)]
        c = lerpc((90, 60, 50), (255, 110, 50), glow_k * (0.85 + 0.15 * math.sin(t * 7 + i)))
        d.line([v * S for xy in pts for v in xy], fill=rgba(c, a), width=int(8 * S), joint="curve")
    text_c(d, 450, y0 - 70, "RESISTIVE HEATER", FL("InterDisplay-Black.otf", 46), rgba(WHITE, a))
    # in / out boxes
    ka = ease_out((lt - 1.0) / 0.4)
    d.rounded_rectangle(p(40, 560, 330, 690), radius=24 * S, fill=rgba(ACC, ka))
    text_c(d, 185, 566, "1", FL("InterDisplay-Black.otf", 70), rgba(BG, ka))
    text_c(d, 185, 650, "ELECTRICITY", FL("InterDisplay-Bold.otf", 30), rgba(BG, ka))
    flow_arrow(d, 350, 625, 550, 625, t, WHITE, ka, w=10)
    kb = ease_out((lt - 1.8) / 0.4)
    d.rounded_rectangle(p(570, 560, 860, 690), radius=24 * S, fill=rgba(ACC2, kb))
    text_c(d, 715, 566, "1", FL("InterDisplay-Black.otf", 70), rgba(BG, kb))
    text_c(d, 715, 650, "HEAT", FL("InterDisplay-Bold.otf", 30), rgba(BG, kb))
    kc = ease_out((lt - 2.6) / 0.4)
    text_c(d, 450, 740, "NO BONUS · COP = 1", FL("InterDisplay-Black.otf", 44), rgba(MUTED, kc))

# ---------------- scene 5: heat pump loop pulls heat from cold outside air ----------------
def vis_wr_pump(d, lt, t):
    a = ease_out(lt / 0.4)
    # outside (cold) panel left, cabin (warm) panel right
    d.rounded_rectangle(p(30, 150, 290, 560), radius=26 * S, fill=rgba((18, 34, 52), a))
    text_c(d, 160, 100, "OUTSIDE", FL("InterDisplay-Bold.otf", 34), rgba(ICE, a))
    for i in range(3):
        snowflake(d, 90 + i * 70, 210 + (i % 2) * 40, 18, ICE, 0.7 * a, rot=t * 0.7 + i)
    d.rounded_rectangle(p(610, 150, 870, 560), radius=26 * S, fill=rgba((52, 30, 20), a))
    text_c(d, 740, 100, "CABIN", FL("InterDisplay-Bold.otf", 34), rgba(ACC2, a))
    heat_waves(d, 740, 470, t, ACC2, a, n=3, h=150, spread=50)
    # refrigerant loop between them
    loop = [(220, 300), (450, 230), (680, 300), (680, 430), (450, 500), (220, 430), (220, 300)]
    d.line([v * S for xy in loop for v in xy], fill=rgba(DARK, a), width=int(14 * S), joint="curve")
    # moving heat packets along loop (cold->warm along top)
    segs = list(zip(loop[:-1], loop[1:]))
    lens = [math.hypot(b[0] - a_[0], b[1] - a_[1]) for a_, b in segs]
    tot = sum(lens)
    for i in range(10):
        u = ((t * 0.35 + i / 10) % 1.0) * tot
        for (p0, p1), ln in zip(segs, lens):
            if u <= ln:
                f = u / ln
                x = p0[0] + (p1[0] - p0[0]) * f; y = p0[1] + (p1[1] - p0[1]) * f
                warm = clamp((x - 220) / 460) if y < 360 else clamp((680 - x) / 460) * 0 + (1 if x > 600 else 0.2)
                c = lerpc(ICE, ACC2, clamp((x - 220) / 460) if y < 360 else 1 - clamp((680 - x) / 460))
                d.ellipse(p(x - 14, y - 14, x + 14, y + 14), fill=rgba(c, a))
                break
            u -= ln
    # compressor in the middle top
    d.ellipse(p(400, 180, 500, 280), fill=rgba(PANEL, a), outline=rgba(ACC, a), width=int(5 * S))
    ang = t * 5
    for k in range(3):
        aa = ang + k * 2 * math.pi / 3
        d.line(p(450, 230, 450 + math.cos(aa) * 36, 230 + math.sin(aa) * 36), fill=rgba(ACC, a), width=int(8 * S))
    text_c(d, 450, 130, "COMPRESSOR", FL("InterDisplay-Bold.otf", 26), rgba(ACC, a))
    # energy bars: electricity in vs heat delivered
    kb = ease_out((lt - 1.4) / 0.5)
    text_c(d, 225, 610, "ELECTRICITY IN", FL("InterDisplay-Bold.otf", 26), rgba(MUTED, kb))
    if kb > 0.3: d.rounded_rectangle(p(110, 655, 110 + 230 * kb * 0.45, 715), radius=14 * S, fill=rgba(ACC, kb))
    hb = ease_out((lt - 2.0) / 1.2)
    text_c(d, 640, 610, "HEAT OUT", FL("InterDisplay-Bold.otf", 26), rgba(MUTED, hb))
    if hb > 0.1: d.rounded_rectangle(p(470, 655, 470 + 380 * hb, 715), radius=14 * S, fill=rgba(ACC2, hb))
    kc = ease_out((lt - 3.0) / 0.4)
    text_c(d, 450, 760, "MOVES HEAT, DOESN'T MAKE IT", FL("InterDisplay-Black.otf", 38), rgba(WHITE, kc))

# ---------------- scene 6: Recurrent data bars 83% vs 75% ----------------
def vis_wr_data(d, lt, t):
    a = ease_out(lt / 0.4)
    text_c(d, 450, 40, "RANGE KEPT BELOW 32°F", FL("InterDisplay-Black.otf", 46), rgba(WHITE, a))
    text_c(d, 450, 105, "18,000+ EVs · RECURRENT", FL("Inter-SemiBold.otf", 28), rgba(MUTED, a))
    base_y, top_y = 660, 200
    bars = [(270, 83, ACC, "HEAT PUMP", 0.6), (630, 75, ACC2, "NO HEAT PUMP", 1.6)]
    for cx, val, col, lab, delay in bars:
        k = ease_out((lt - delay) / 1.6)
        v = val * k
        h = (base_y - top_y) * v / 100
        d.rounded_rectangle(p(cx - 120, top_y, cx + 120, base_y), radius=22 * S, fill=rgba(PANEL, a), outline=rgba(DARK, a), width=int(4 * S))
        if h > 30:
            d.rounded_rectangle(p(cx - 104, base_y - h, cx + 104, base_y - 16), radius=16 * S, fill=rgba(col, a))
        text_c(d, cx, max(base_y - h + 10, top_y + 24) if h > 120 else base_y - 130, f"{int(round(v))}%", FL("InterDisplay-Black.otf", 76), rgba(BG if h > 120 else WHITE, a * clamp(k * 3)))
        text_c(d, cx, base_y + 24, lab, FL("InterDisplay-Bold.otf", 34), rgba(col, a))
    # 100% reference line
    d.line(p(110, top_y + 16, 790, top_y + 16), fill=rgba(MUTED, 0.4 * a), width=int(3 * S))
    kc = ease_out((lt - 3.6) / 0.4)
    d.rounded_rectangle(p(250, 750, 650, 830), radius=40 * S, fill=rgba(ACC, kc))
    text_c(d, 450, 765, "≈ 8 POINTS MORE", FL("InterDisplay-Black.otf", 40), rgba(BG, kc))

# ---------------- scene 7: precondition while plugged in, then end card ----------------
def vis_wr_outro(d, lt, t):
    dur = sdur("wr_outro")
    cut = dur * 0.5
    if lt < cut:
        a = ease_out(lt / 0.4)
        snowfall(d, t, a=a, n=14)
        car_side(d, 380, 470, 1.1, WHITE, a)
        # warm glow in cabin
        gk = ease_out((lt - 0.5) / 1.0)
        heat_waves(d, 390, 330, t, ACC2, gk, n=3, h=90, spread=40)
        # charger post + cable
        d.rounded_rectangle(p(740, 330, 820, 560), radius=16 * S, fill=rgba(DARK, a))
        d.rounded_rectangle(p(755, 350, 805, 400), radius=8 * S, fill=rgba(ACC, a))
        d.line(p(780, 470, 700, 520, 640, 440, 620, 440), fill=rgba(ACC, a), width=int(10 * S), joint="curve")
        flow_arrow(d, 760, 500, 640, 450, t, ACC, a, w=8, n=3)
        d.line(p(40, 575, 860, 575), fill=rgba(DARK, a), width=int(6 * S))
        kt = ease_out((lt - 0.8) / 0.4)
        text_c(d, 450, 640, "PRE-HEAT WHILE PLUGGED IN", FL("InterDisplay-Black.otf", 48), rgba(ACC, kt))
        text_c(d, 450, 710, "HEAT COMES FROM THE GRID, NOT THE BATTERY", FL("Inter-SemiBold.otf", 26), rgba(MUTED, kt))
    else:
        end_card(d, lt, cut)

VIS.update({"wr_hook": vis_wr_hook, "wr_battery": vis_wr_battery, "wr_heat": vis_wr_heat, "wr_heater": vis_wr_heater,
            "wr_pump": vis_wr_pump, "wr_data": vis_wr_data, "wr_outro": vis_wr_outro})
