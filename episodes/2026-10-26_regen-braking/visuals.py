# Episode visuals: How regenerative braking works — and why it can't recover 100%.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
RED = (255, 84, 84)
BLUE = (80, 170, 255)
COPPER = (214, 140, 80)

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

def glow_rect(d, x0, y0, x1, y1, r, col, a=1.0):
    for g, al in ((14, 0.07), (8, 0.12), (4, 0.2)):
        d.rounded_rectangle(p(x0 - g, y0 - g, x1 + g, y1 + g), radius=int((r + g) * S), fill=rgba(col, al * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=int(r * S), fill=rgba(col, a))

def battery_h(d, x, y, w, h, level, col, a=1.0, outline=WHITE):
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=int(h * 0.18 * S), outline=rgba(outline, a), width=int(6 * S))
    d.rounded_rectangle(p(x + w + 3, y + h * 0.3, x + w + 15, y + h * 0.7), radius=int(4 * S), fill=rgba(outline, a))
    pad = 11
    if level > 0.01:
        d.rounded_rectangle(p(x + pad, y + pad, x + pad + (w - 2 * pad) * clamp(level), y + h - pad), radius=int(5 * S), fill=rgba(col, a))

def brake_disc(d, cx, cy, r, heat, a=1.0, ang=0.0):
    """Brake disc with caliper; heat 0..1 makes it glow orange."""
    hc = tuple(int(MUTED[i] + (ACC2[i] - MUTED[i]) * heat) for i in range(3))
    if heat > 0.05:
        for g, al in ((1.35, 0.10), (1.2, 0.18)):
            d.ellipse(p(cx - r * g, cy - r * g, cx + r * g, cy + r * g), fill=rgba(ACC2, al * heat * a))
    d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=rgba(hc, a))
    d.ellipse(p(cx - r * 0.42, cy - r * 0.42, cx + r * 0.42, cy + r * 0.42), fill=rgba(PANEL, a))
    for k in range(10):
        aa = ang + k * math.pi / 5
        hx, hy = cx + math.cos(aa) * r * 0.7, cy + math.sin(aa) * r * 0.7
        d.ellipse(p(hx - 6, hy - 6, hx + 6, hy + 6), fill=rgba(PANEL, a))
    d.rounded_rectangle(p(cx + r * 0.55, cy - r * 0.45, cx + r * 1.12, cy + r * 0.45), radius=int(14 * S), fill=rgba(WHITE, a))

def particles(d, path, t, col, n=10, speed=0.6, a=1.0, size=9):
    """Dots flowing along a polyline path."""
    segs = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    lens = [math.hypot(b[0] - a_[0], b[1] - a_[1]) for a_, b in segs]
    tot = sum(lens)
    for i in range(n):
        u = ((t * speed + i / n) % 1.0) * tot
        for (p0, p1), ln in zip(segs, lens):
            if u <= ln:
                f = u / ln
                x = p0[0] + (p1[0] - p0[0]) * f; y = p0[1] + (p1[1] - p0[1]) * f
                d.ellipse(p(x - size * 1.8, y - size * 1.8, x + size * 1.8, y + size * 1.8), fill=rgba(col, 0.18 * a))
                d.ellipse(p(x - size, y - size, x + size, y + size), fill=rgba(col, a))
                break
            u -= ln

def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

# ---------- 1. car slows; wheels send charge into the floor battery ----------
def vis_hook_r(d, lt, t):
    dur = sdur("hook_r")
    k = ease_out(lt / 2.6)
    x = 180 + 270 * k                      # decelerating glide
    spd = int(round(60 - 45 * ease_inout(lt / 2.8)))
    d.line(p(30, 520, 870, 520), fill=rgba(DARK, 1), width=6 * S)
    # speed streaks fade as car slows
    for i in range(4):
        sx = x - 300 - i * 30
        d.line(p(sx, 400 + i * 22, sx + 120 * (1 - k), 400 + i * 22), fill=rgba(MUTED, 0.5 * (1 - k)), width=5 * S)
    car_side(d, x, 440, 1.05, WHITE)
    # floor battery
    lvl = 0.35 + 0.35 * ease_out((lt - 0.8) / 2.4)
    d.rounded_rectangle(p(x - 85, 432, x + 85, 462), radius=8 * S, fill=rgba(PANEL, 1))
    d.rounded_rectangle(p(x - 80, 437, x - 80 + 160 * lvl, 457), radius=6 * S, fill=rgba(ACC, 1))
    # charge flowing from both wheels into the floor battery
    pa = ease_out((lt - 0.6) / 0.4)
    for wx in (-133, 133):
        particles(d, [(x + wx, 480), (x + wx * 0.62, 447)], t, ACC, n=3, speed=1.2, a=pa, size=6)
    la = ease_out((lt - 1.0) / 0.4)
    text_c(d, x, 250, "FLOOR BATTERY", FL("InterDisplay-Bold.otf", 26), rgba(ACC, la))
    d.line(p(x, 290, x, 430), fill=rgba(ACC, la), width=3 * S)
    text_c(d, 450, 590, f"{spd} mph", FL("InterDisplay-Black.otf", 80), rgba(WHITE, 1))
    text_c(d, 450, 700, "SLOWING DOWN = CHARGING", FL("InterDisplay-Bold.otf", 40), rgba(ACC, ease_out((lt - 1.2) / 0.4)))

# ---------- 2. motor <-> generator ----------
def motor_xs(d, cx, cy, r, ang, gen, a=1.0):
    # stator ring with copper coils
    d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=rgba(DARK, a))
    d.ellipse(p(cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78), fill=rgba(PANEL, a))
    for k in range(12):
        aa = k * math.pi / 6
        x0, y0 = cx + math.cos(aa) * r * 0.80, cy + math.sin(aa) * r * 0.80
        x1, y1 = cx + math.cos(aa) * r * 0.95, cy + math.sin(aa) * r * 0.95
        glow = 0.5 + 0.5 * math.sin(t_glob[0] * 8 + k)
        col = ACC if gen else COPPER
        d.line(p(x0, y0, x1, y1), fill=rgba(col, a * (0.55 + 0.45 * glow)), width=int(22 * S))
    # rotor with magnets
    rr = r * 0.62
    d.ellipse(p(cx - rr, cy - rr, cx + rr, cy + rr), fill=rgba((60, 68, 80), a))
    for k in range(4):
        aa = ang + k * math.pi / 2
        mc = RED if k % 2 == 0 else BLUE
        mx, my = cx + math.cos(aa) * rr * 0.68, cy + math.sin(aa) * rr * 0.68
        d.ellipse(p(mx - rr * 0.24, my - rr * 0.24, mx + rr * 0.24, my + rr * 0.24), fill=rgba(mc, a))
    d.ellipse(p(cx - 20, cy - 20, cx + 20, cy + 20), fill=rgba(WHITE, a))

t_glob = [0.0]

def arrow(d, x0, y, x1, col, a=1.0, w=12):
    d.line(p(x0, y, x1, y), fill=rgba(col, a), width=int(w * S))
    s = 1 if x1 > x0 else -1
    poly(d, [(x1 + s * 26, y), (x1 - s * 4, y - 22), (x1 - s * 4, y + 22)], rgba(col, a))

def vis_motor(d, lt, t):
    t_glob[0] = t
    dur = sdur("motor")
    sw = dur * 0.48
    gen = lt >= sw
    m = ease_out((lt - sw) / 0.5) if gen else 0
    k = ease_out(lt / 0.4)
    # battery left, motor centre, wheel right
    battery_h(d, 40, 330, 150, 70, 0.6 + (0.25 * ease_out((lt - sw) / dur * 2) if gen else 0), ACC, k)
    motor_xs(d, 450, 365, 150, t * 3.0, gen, k)
    tire(d, 760, 365, 95, t * 3.0, ACC if gen else WHITE, k)
    # arrows: battery -> motor -> wheel (motor); reversed (generator)
    if not gen:
        aa = ease_out((lt - 0.4) / 0.4)
        arrow(d, 210, 365, 270, ACC2, aa); arrow(d, 630, 365, 640, WHITE, aa)
        particles(d, [(205, 365), (295, 365)], t, ACC2, n=3, speed=1.4, a=aa, size=8)
    else:
        arrow(d, 640, 365, 630, ACC, m); arrow(d, 270, 365, 205, ACC, m)
        particles(d, [(300, 365), (205, 365)], t, ACC, n=3, speed=1.4, a=m, size=8)
    # mode label flips
    if not gen:
        text_c(d, 450, 570, "MOTOR", FL("InterDisplay-Black.otf", 96), rgba(WHITE, k))
        text_c(d, 450, 690, "ELECTRICITY → MOTION", FL("InterDisplay-Bold.otf", 38), rgba(MUTED, k))
    else:
        sc = back_out((lt - sw) / 0.45)
        text_c(d, 450, 570, "GENERATOR", FL("InterDisplay-Black.otf", max(1, int(96 * max(sc, 0.05)))), rgba(ACC, clamp(sc)))
        text_c(d, 450, 690, "MOTION → ELECTRICITY", FL("InterDisplay-Bold.otf", 38), rgba(ACC, m))
    fs = FL("InterDisplay-Bold.otf", 26)
    text_c(d, 120, 430, "BATTERY", fs, rgba(MUTED, k))
    text_c(d, 760, 480, "WHEEL", fs, rgba(MUTED, k))

# ---------- 3. energy goes to battery, not brake heat ----------
def vis_flow(d, lt, t):
    dur = sdur("flow")
    k = ease_out(lt / 0.4)
    # top: old way, friction brake turning motion into heat
    brake_disc(d, 250, 200, 110, 0.9 * (1 - ease_out((lt - 2.5) / 1.0)) + 0.1, k, ang=t * 2)
    fs = FL("InterDisplay-Bold.otf", 34)
    d.text((420 * S, 150 * S), "FRICTION BRAKE", font=fs, fill=rgba(WHITE, k))
    d.text((420 * S, 200 * S), "MOTION → HEAT", font=fs, fill=rgba(ACC2, k))
    # heat waves rising
    ha = k * (1 - ease_out((lt - 2.5) / 1.0))
    for i in range(3):
        ph = (t * 0.8 + i / 3) % 1.0
        yy = 70 - ph * 50
        d.line(p(200 + i * 50, yy + 20, 210 + i * 50, yy), fill=rgba(ACC2, ha * (1 - ph)), width=5 * S)
    # strike the heat when regen takes over
    xa = ease_out((lt - 2.5) / 0.4)
    d.line(p(410, 220, 410 + 290 * xa, 220), fill=rgba(RED, xa), width=6 * S)
    # bottom: regen path wheel -> motor -> inverter -> battery
    ba = ease_out((lt - 0.8) / 0.5)
    nodes = [(120, 560, "WHEEL"), (330, 560, "MOTOR"), (540, 560, "INVERTER"), (760, 560, "BATTERY")]
    path = [(n[0], n[1]) for n in nodes]
    d.line([v * S for xy in path for v in xy], fill=rgba(DARK, ba), width=14 * S)
    particles(d, path, t, ACC, n=12, speed=0.45, a=ba, size=9)
    fsl = FL("InterDisplay-Bold.otf", 26)
    for i, (x, y, lab) in enumerate(nodes):
        na = ease_out((lt - 0.8 - 0.25 * i) / 0.4)
        glow_rect(d, x - 62, y - 62, x + 62, y + 62, 22, PANEL, na)
        d.rounded_rectangle(p(x - 62, y - 62, x + 62, y + 62), radius=22 * S, outline=rgba(ACC, na), width=4 * S)
        if i == 0: tire(d, x, y, 44, t * 3, ACC, na)
        elif i == 1:
            d.ellipse(p(x - 40, y - 40, x + 40, y + 40), outline=rgba(COPPER, na), width=10 * S)
            d.ellipse(p(x - 16, y - 16, x + 16, y + 16), fill=rgba(WHITE, na))
        elif i == 2:
            for j in range(3):
                d.line(p(x - 34, y - 20 + j * 20, x + 34, y - 20 + j * 20), fill=rgba(WHITE, na), width=5 * S)
        else:
            lv = 0.4 + 0.5 * ease_out((lt - 1.5) / (dur - 1.5))
            battery_h(d, x - 44, y - 24, 80, 48, lv, ACC, na)
        text_c(d, x, y + 80, lab, fsl, rgba(MUTED, na))
    text_c(d, 450, 760, "REGEN: MOTION → CHARGE", FL("InterDisplay-Black.otf", 48), rgba(ACC, ease_out((lt - 2.8) / 0.4)))

# ---------- 4. why not 100%: energy budget waterfall ----------
def vis_loss(d, lt, t):
    dur = sdur("loss")
    k = ease_out(lt / 0.4)
    text_c(d, 450, 20, "WHERE THE ENERGY GOES", FL("InterDisplay-Black.otf", 52), rgba(WHITE, k))
    text_c(d, 450, 90, "ILLUSTRATIVE · NOT TO SCALE", FL("Inter-SemiBold.otf", 24), rgba(MUTED, k))
    # stacked rows: start bar, then pieces peel off
    x0, full = 110, 680
    rows = [
        ("ENERGY USED TO DRIVE", 1.0, 0.0, WHITE, 0.2),
        ("AIR & TIRE DRAG (GONE)", 0.55, 0.0, ACC2, 1.0),
        ("HEAT IN MOTOR, INVERTER, BATTERY", 0.12, 0.55, ACC2, 2.6),
        ("BACK INTO THE BATTERY", 0.33, 0.67, ACC, 4.0),
    ]
    for i, (lab, w, off, col, st) in enumerate(rows):
        y = 170 + i * 150
        a = ease_out((lt - st) / 0.6)
        if a <= 0: continue
        xs = x0 + off * full
        ww = w * full * ease_out((lt - st) / 0.9)
        if col == ACC:
            glow_rect(d, xs, y + 46, xs + max(ww, 4), y + 110, 14, ACC, a)
        else:
            d.rounded_rectangle(p(xs, y + 46, xs + max(ww, 4), y + 110), radius=14 * S, fill=rgba(col, 0.9 * a))
        d.text((x0 * S, y * S), lab, font=FL("InterDisplay-Bold.otf", 32), fill=rgba(col, a))
        # dashed guide back to the full bar
        if i > 0:
            for yy in range(176 + 110, y + 46, 18):
                d.line(p(xs, yy, xs, yy + 9), fill=rgba(MUTED, 0.5 * a), width=2 * S)

# ---------- 5. limits: full / cold / hot -> regen cut, friction brakes on ----------
def snowflake(d, cx, cy, r, col, a):
    for k in range(3):
        aa = k * math.pi / 3
        d.line(p(cx - math.cos(aa) * r, cy - math.sin(aa) * r, cx + math.cos(aa) * r, cy + math.sin(aa) * r), fill=rgba(col, a), width=7 * S)
    d.ellipse(p(cx - 10, cy - 10, cx + 10, cy + 10), fill=rgba(col, a))

def thermo(d, cx, cy, col, a):
    d.rounded_rectangle(p(cx - 16, cy - 60, cx + 16, cy + 30), radius=16 * S, outline=rgba(WHITE, a), width=5 * S)
    d.ellipse(p(cx - 30, cy + 14, cx + 30, cy + 74), fill=rgba(col, a))
    d.rectangle(p(cx - 7, cy - 40, cx + 7, cy + 30), fill=rgba(col, a))

def vis_limits(d, lt, t):
    dur = sdur("limits")
    icons = [("FULL", 0.3), ("TOO COLD", 1.1), ("TOO HOT", 1.9)]
    fs = FL("InterDisplay-Bold.otf", 30)
    for i, (lab, st) in enumerate(icons):
        cx = 180 + i * 270; cy = 120
        a = back_out((lt - st) / 0.45); aa = clamp(a)
        if aa <= 0: continue
        d.rounded_rectangle(p(cx - 100, cy - 90, cx + 100, cy + 110), radius=28 * S, fill=rgba(PANEL, aa), outline=rgba(ACC2, aa), width=4 * S)
        if i == 0: battery_h(d, cx - 60, cy - 30, 110, 56, 1.0, ACC, aa)
        elif i == 1: snowflake(d, cx, cy, 48, BLUE, aa)
        else: thermo(d, cx, cy - 10, RED, aa)
        text_c(d, cx, cy + 62, lab, fs, rgba(WHITE, aa))
    # regen power bar shrinking
    cut = ease_inout((lt - 0.6) / 2.4)
    ra = ease_out((lt - 0.2) / 0.4)
    d.text((110 * S, 300 * S), "REGEN", font=FL("InterDisplay-Black.otf", 40), fill=rgba(ACC, ra))
    d.rounded_rectangle(p(110, 360, 790, 420), radius=18 * S, fill=rgba(DARK, ra))
    glow_rect(d, 110, 360, 110 + 680 * (1 - 0.75 * cut), 420, 18, ACC, ra)
    # friction brake share growing
    fa = ease_out((lt - 2.6) / 0.5)
    d.text((110 * S, 450 * S), "FRICTION BRAKES", font=FL("InterDisplay-Black.otf", 40), fill=rgba(ACC2, fa))
    d.rounded_rectangle(p(110, 510, 790, 570), radius=18 * S, fill=rgba(DARK, fa))
    d.rounded_rectangle(p(110, 510, 110 + 680 * 0.75 * ease_out((lt - 2.8) / 1.2), 570), radius=18 * S, fill=rgba(ACC2, fa))
    brake_disc(d, 450, 720, 90, ease_out((lt - 3.0) / 1.2), fa, ang=t * 2)

# ---------- 6. city vs highway speed traces ----------
def vis_city(d, lt, t):
    dur = sdur("city")
    k = ease_out(lt / 0.3)
    prog = ease_inout(lt / (dur * 0.85))
    def panel(y0, lab, col, trace):
        d.text((110 * S, (y0 - 60) * S), lab, font=FL("InterDisplay-Black.otf", 44), fill=rgba(col, k))
        d.line(p(110, y0 + 180, 790, y0 + 180), fill=rgba(DARK, k), width=4 * S)
        pts = []; sparks = []
        for i in range(0, 121):
            u = i / 120
            if u > prog: break
            v, braking = trace(u)
            x = 110 + 680 * u; y = y0 + 180 - 160 * v
            pts.append((x, y))
            if braking and i % 3 == 0: sparks.append((x, y))
        if len(pts) > 1:
            d.line([vv * S for xy in pts for vv in xy], fill=rgba(WHITE, k), width=6 * S, joint="curve")
        for (x, y) in sparks:
            d.ellipse(p(x - 9, y - 9, x + 9, y + 9), fill=rgba(ACC, k))
            d.ellipse(p(x - 18, y - 18, x + 18, y + 18), fill=rgba(ACC, 0.18 * k))
        return len(sparks)
    def city(u):
        ph = (u * 5) % 1.0
        if ph < 0.35: return ph / 0.35, False
        if ph < 0.6: return 1.0, False
        return max(0.0, 1 - (ph - 0.6) / 0.35), True
    def hwy(u):
        if u < 0.1: return u / 0.1 * 0.95, False
        if u > 0.9: return 0.95 * (1 - (u - 0.9) / 0.1), True
        return 0.95, False
    panel(90, "CITY: STOP & GO", ACC, city)
    panel(470, "HIGHWAY: STEADY", MUTED, hwy)
    la = ease_out((lt - 1.0) / 0.4)
    d.ellipse(p(560, 4, 578, 22), fill=rgba(ACC, la))
    d.text((590 * S, -6 * S), "= REGEN", font=FL("InterDisplay-Bold.otf", 30), fill=rgba(ACC, la))

# ---------- 7. outro: lift off the pedal ----------
def vis_outro_r(d, lt, t):
    dur = sdur("outro_r")
    cut = dur * 0.45
    if lt < cut:
        k = ease_out(lt / 0.4)
        lift = ease_inout((lt - 0.4) / 0.8)
        # pedal on a floor pivot, rotating back as the foot lifts off
        px, py = 250, 600
        ang = math.radians(-60 - 25 * lift)
        L_ = 230
        cx, cy = px + math.cos(ang) * L_, py + math.sin(ang) * L_
        d.ellipse(p(px - 18, py - 18, px + 18, py + 18), fill=rgba(MUTED, k))
        d.line(p(px, py, cx, cy), fill=rgba(MUTED, k), width=16 * S)
        pad = [(-30, -80), (30, -80), (30, 80), (-30, 80)]
        ca, sa = math.cos(ang), math.sin(ang)
        poly(d, [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pad], rgba(WHITE, k))
        d.line(p(120, py + 20, 420, py + 20), fill=rgba(DARK, k), width=8 * S)
        # charge sparks coming off as you lift
        battery_h(d, 540, 300, 210, 90, 0.4 + 0.5 * lift, ACC, k)
        particles(d, [(cx + 40, cy), (540, 345)], t, ACC, n=6, speed=1.0, a=lift, size=8)
        text_c(d, 450, 660, "LIFT OFF = CHARGE", FL("InterDisplay-Black.otf", 64), rgba(ACC, ease_out((lt - 0.9) / 0.4)))
    else:
        end_card(d, lt, cut)

VIS.update({"hook_r": vis_hook_r, "motor": vis_motor, "flow": vis_flow, "loss": vis_loss,
            "limits": vis_limits, "city": vis_city, "outro_r": vis_outro_r})
