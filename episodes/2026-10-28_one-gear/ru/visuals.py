# Episode visuals: How it works — why most EVs have only one gear.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
BLUE = (110, 190, 255)

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

def gear(d, cx, cy, r, teeth, ang, col, a=1.0, hub=None, depth=None):
    """Spur gear: r = pitch radius."""
    depth = depth or max(8, r * 0.16)
    ro, ri = r + depth * 0.5, r - depth * 0.5
    pts = []
    for k in range(teeth):
        base = ang + k * 2 * math.pi / teeth
        step = 2 * math.pi / teeth
        for f, rr in ((0.0, ri), (0.18, ro), (0.5, ro), (0.68, ri)):
            aa = base + f * step
            pts.append((cx + math.cos(aa) * rr, cy + math.sin(aa) * rr))
    # shadow
    poly(d, [(x + 6, y + 8) for x, y in pts], rgba((0, 0, 0), 0.35 * a))
    poly(d, pts, rgba(col, a))
    hr = ri * 0.62
    d.ellipse(p(cx - hr, cy - hr, cx + hr, cy + hr), fill=rgba(PANEL, a))
    hub = hub or col
    h2 = ri * 0.28
    d.ellipse(p(cx - h2, cy - h2, cx + h2, cy + h2), fill=rgba(hub, a))
    for k in range(4):
        aa = ang + k * math.pi / 2 + math.pi / 4
        x0, y0 = cx + math.cos(aa) * h2, cy + math.sin(aa) * h2
        x1, y1 = cx + math.cos(aa) * hr, cy + math.sin(aa) * hr
        d.line(p(x0, y0, x1, y1), fill=rgba(hub, a), width=int(max(4, r * 0.08) * S))

def glow_line(d, pts, col, a=1.0, w=10):
    flat = [v * S for xy in pts for v in xy]
    if len(pts) < 2:
        return
    d.line(flat, fill=rgba(col, 0.18 * a), width=int(w * 3 * S), joint="curve")
    d.line(flat, fill=rgba(col, a), width=int(w * S), joint="curve")

def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "ПОДПИШИСЬ НА КАНАЛ", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

# ---------- torque chart helpers ----------
CX0, CX1, CY0, CY1 = 130, 820, 170, 640   # plot area (x: rpm, y: torque)
def axes(d, a, maxr, ticks):
    d.rounded_rectangle(p(60, 110, 860, 760), radius=30 * S, fill=rgba(PANEL, 0.85 * a), outline=rgba(DARK, a), width=int(4 * S))
    d.line(p(CX0, CY1, CX1, CY1), fill=rgba(MUTED, a), width=int(4 * S))
    d.line(p(CX0, CY0 - 20, CX0, CY1), fill=rgba(MUTED, a), width=int(4 * S))
    fs = FL("Inter-Bold.otf", 26) if os.path.exists(F + "Inter-Bold.otf") else FL("InterDisplay-Bold.otf", 26)
    for v, lab in ticks:
        x = CX0 + (CX1 - CX0) * v / maxr
        d.line(p(x, CY1, x, CY1 + 12), fill=rgba(MUTED, a), width=int(3 * S))
        text_c(d, x, CY1 + 20, lab, fs, rgba(MUTED, a))
    text_c(d, (CX0 + CX1) / 2, 700, "ОБОРОТЫ ДВИГАТЕЛЯ (об/мин)", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
    # vertical label as stacked short word
    text_c(d, 190, 128, "МОМЕНТ", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, a))

def ice_torque(r):
    # idealised gas-engine torque curve: nothing below idle, hump mid-range
    if r < 800:
        return None
    x = (r - 4200) / 3200
    return max(0.0, 0.78 - 0.55 * x * x) if r <= 6500 else None

def ev_torque(r, base=5000, maxr=18000):
    return 0.95 if r <= base else 0.95 * base / r

def curve_pts(fn, maxr, r0, r1, n=80):
    pts = []
    for i in range(n + 1):
        r = r0 + (r1 - r0) * i / n
        v = fn(r)
        if v is None:
            continue
        pts.append((CX0 + (CX1 - CX0) * r / maxr, CY1 - (CY1 - CY0) * v))
    return pts

# ---------------- scene 1: hook — 10 gears vs 1 gear ----------------
def vis_og_hook(d, lt, t):
    # left: stack of ten small gears popping in with a counter
    n = int(clamp((lt - 0.2) / 1.6) * 10 + 0.001)
    a = ease_out(lt / 0.4)
    text_c(d, 230, 90, "НА БЕНЗИНЕ", FL("InterDisplay-Black.otf", 46), rgba(ACC2, a))
    for i in range(10):
        if i >= n:
            break
        k = back_out((lt - 0.2 - i * 0.16) / 0.35)
        col_ = i % 2
        cx = 160 + col_ * 140
        cy = 200 + (i // 2) * 105
        gear(d, cx, cy, 38 * k + 0.01, 12, t * (2.5 if col_ else -2.5) + i, ACC2, a=clamp(k))
        text_c(d, cx, cy - 16, str(i + 1), FL("InterDisplay-Black.otf", 28), rgba(WHITE, clamp(k)))
    text_c(d, 230, 730, f"{n} " + ("ПЕРЕДАЧА" if n == 1 else "ПЕРЕДАЧИ" if 2 <= n <= 4 else "ПЕРЕДАЧ"), FL("InterDisplay-Black.otf", 52), rgba(WHITE, a))
    # divider
    d.line(p(450, 120, 450, 760), fill=rgba(DARK, a), width=int(4 * S))
    text_c(d, 450, 410, "VS", FL("InterDisplay-Black.otf", 44), rgba(MUTED, a))
    # right: one big lime gear
    k = back_out((lt - 2.0) / 0.6)
    text_c(d, 670, 90, "ЭЛЕКТРОКАР", FL("InterDisplay-Black.otf", 46), rgba(ACC, clamp(k)))
    if k > 0.01:
        gear(d, 670, 400, 150 * k, 24, t * 0.9, ACC, a=clamp(k), hub=BG)
        text_c(d, 670, 730, "1 ПЕРЕДАЧА", FL("InterDisplay-Black.otf", 52), rgba(WHITE, clamp(k)))
    qa = ease_out((lt - 3.2) / 0.4)
    if qa > 0:
        text_c(d, 670, 335, "?", FL("InterDisplay-Black.otf", 110), rgba(WHITE, qa))

# ---------------- scene 2: gas engine torque curve + narrow band ----------------
def vis_og_engine(d, lt, t):
    a = ease_out(lt / 0.4)
    maxr = 7000
    axes(d, a, maxr, [(0, "0"), (2000, "2k"), (4000, "4k"), (6000, "6k")])
    k = ease_inout((lt - 0.4) / 1.6)
    pts = curve_pts(ice_torque, maxr, 0, 800 + (6500 - 800) * k)
    # zero-rpm dead zone
    za = ease_out((lt - 0.6) / 0.4)
    x800 = CX0 + (CX1 - CX0) * 800 / maxr
    d.rectangle(p(CX0 + 3, CY0, x800, CY1 - 3), fill=rgba((255, 84, 84), 0.18 * za))
    text_c(d, CX0 + 95, CY0 + 30, "0 об/мин:", FL("InterDisplay-Black.otf", 30), rgba((255, 110, 110), za))
    text_c(d, CX0 + 95, CY0 + 66, "НЕТ МОЩНОСТИ", FL("InterDisplay-Black.otf", 30), rgba((255, 110, 110), za))
    # sweet-spot band
    ba = ease_out((lt - 2.6) / 0.6)
    xb0 = CX0 + (CX1 - CX0) * 2600 / maxr
    xb1 = CX0 + (CX1 - CX0) * 5800 / maxr
    pulse = 0.22 + 0.06 * math.sin(t * 4)
    d.rectangle(p(xb0, CY0, xb1, CY1 - 3), fill=rgba(ACC2, pulse * ba))
    d.line(p(xb0, CY0, xb0, CY1), fill=rgba(ACC2, ba), width=int(3 * S))
    d.line(p(xb1, CY0, xb1, CY1), fill=rgba(ACC2, ba), width=int(3 * S))
    text_c(d, (xb0 + xb1) / 2, CY0 - 10, "РАБОЧИЙ ДИАПАЗОН", FL("InterDisplay-Black.otf", 28), rgba(ACC2, ba))
    if len(pts) > 1:
        glow_line(d, pts, ACC2, a, w=9)
        hx, hy = pts[-1]
        d.ellipse(p(hx - 12, hy - 12, hx + 12, hy + 12), fill=rgba(WHITE, a))
    # gears keep it inside: needle bouncing within band with gear number
    ga = ease_out((lt - 4.8) / 0.5)
    if ga > 0:
        cyc = ((lt - 4.8) * 0.9) % 1.0
        gear_n = 1 + int((lt - 4.8) * 0.9) % 6
        rr = 2800 + 2900 * cyc
        x = CX0 + (CX1 - CX0) * rr / maxr
        d.line(p(x, CY0 + 10, x, CY1), fill=rgba(WHITE, ga), width=int(5 * S))
        d.rounded_rectangle(p(x - 46, CY1 - 160, x + 46, CY1 - 80), radius=16 * S, fill=rgba(BG, ga), outline=rgba(WHITE, ga), width=int(3 * S))
        text_c(d, x, CY1 - 150, f"{gear_n}-я", FL("InterDisplay-Black.otf", 44), rgba(WHITE, ga))
        text_c(d, 450, 780, "ПЕРЕКЛЮЧИЛ → СНОВА В ДИАПАЗОНЕ", FL("InterDisplay-Black.otf", 40), rgba(WHITE, ga))

# ---------------- scene 3: electric motor — full torque from 0 rpm ----------------
def vis_og_motor(d, lt, t):
    a = ease_out(lt / 0.4)
    maxr = 7000
    axes(d, a, maxr, [(0, "0"), (2000, "2k"), (4000, "4k"), (6000, "6k")])
    ghost = curve_pts(ice_torque, maxr, 0, 6500)
    glow_line(d, ghost, MUTED, 0.45 * a, w=6)
    k = ease_inout((lt - 0.3) / 1.4)
    pts = curve_pts(lambda r: ev_torque(r, base=3500, maxr=maxr), maxr, 0, 7000 * k + 1)
    if len(pts) > 1:
        glow_line(d, pts, ACC, a, w=10)
        hx, hy = pts[-1]
        d.ellipse(p(hx - 13, hy - 13, hx + 13, hy + 13), fill=rgba(WHITE, a))
    # callout at 0 rpm
    ca = back_out((lt - 1.4) / 0.5)
    y0 = CY1 - (CY1 - CY0) * 0.95
    if ca > 0.01:
        d.ellipse(p(CX0 - 18 * ca, y0 - 18 * ca, CX0 + 18 * ca, y0 + 18 * ca), fill=rgba(ACC, clamp(ca)))
        rr = 30 + ((lt * 1.4) % 1.0) * 40
        d.ellipse(p(CX0 - rr, y0 - rr, CX0 + rr, y0 + rr), outline=rgba(ACC, clamp(ca) * (1 - ((lt * 1.4) % 1.0))), width=int(4 * S))
        d.rounded_rectangle(p(320, 470, 660, 590), radius=24 * S, fill=rgba(BG, clamp(ca)), outline=rgba(ACC, clamp(ca)), width=int(4 * S))
        text_c(d, 490, 482, "ПОЛНЫЙ МОМЕНТ", FL("InterDisplay-Black.otf", 32), rgba(ACC, clamp(ca)))
        text_c(d, 490, 535, "С 0 об/мин", FL("InterDisplay-Black.otf", 36), rgba(WHITE, clamp(ca)))
    la = ease_out((lt - 2.4) / 0.4)
    text_c(d, 760, 440, "бензиновый", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, la))
    text_c(d, 450, 780, "ЭЛЕКТРОМОТОР", FL("InterDisplay-Black.otf", 44), rgba(ACC, la))

# ---------------- scene 4: rpm — two tachometers ----------------
def tach(d, cx, cy, r, frac, maxlab, col, a, label, value):
    arc(d, cx, cy, r, 150, 390, rgba(DARK, a), 26)
    if frac > 0.002:
        arc(d, cx, cy, r, 150, 150 + 240 * frac, rgba(col, a), 26)
    ang = math.radians(150 + 240 * frac)
    d.line(p(cx, cy, cx + math.cos(ang) * (r - 34), cy + math.sin(ang) * (r - 34)), fill=rgba(WHITE, a), width=int(8 * S))
    d.ellipse(p(cx - 16, cy - 16, cx + 16, cy + 16), fill=rgba(WHITE, a))
    text_c(d, cx, cy + 40, value, FL("InterDisplay-Black.otf", 52), rgba(col, a))
    text_c(d, cx, cy + 104, "об/мин", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, a))
    text_c(d, cx, cy - r - 70, label, FL("InterDisplay-Black.otf", 40), rgba(WHITE, a))

def vis_og_rpm(d, lt, t):
    a = ease_out(lt / 0.4)
    k = ease_inout((lt - 0.4) / 2.6)
    # same 0..20k scale for both so the difference is visible
    gas = min(6000, 20000 * k) if k > 0 else 0
    ev = 18447 * k
    jitter = math.sin(t * 40) * 0.004 if gas >= 6000 else 0
    tach(d, 225, 380, 170, gas / 20000 + jitter, "20k", ACC2, a, "БЕНЗИН", f"{int(gas):,}".replace(",", " "))
    tach(d, 675, 380, 170, ev / 20000, "20k", ACC, a, "ЭЛЕКТРО", f"{int(ev):,}".replace(",", " "))
    ra = ease_out((lt - 2.0) / 0.4)
    text_c(d, 225, 560, "обычная отсечка", FL("InterDisplay-Bold.otf", 28), rgba(ACC2, ra))
    text_c(d, 675, 560, "Model 3 на макс. скорости", FL("InterDisplay-Bold.otf", 28), rgba(ACC, ra))
    # bar comparison
    ba = ease_out((lt - 3.2) / 0.5)
    if ba > 0:
        x0 = 120; w = 660
        d.rounded_rectangle(p(x0, 650, x0 + w * 6000 / 20000 * ba, 690), radius=14 * S, fill=rgba(ACC2, 1))
        d.rounded_rectangle(p(x0, 710, x0 + w * 18447 / 20000 * ba, 750), radius=14 * S, fill=rgba(ACC, 1))
        text_c(d, 450, 780, "≈ В 3 РАЗА БОЛЬШЕ ОБОРОТОВ", FL("InterDisplay-Black.otf", 40), rgba(WHITE, ba))

# ---------------- scene 5: one reduction gear ≈ 9:1 ----------------
def motor_icon(d, cx, cy, r, ang, a):
    d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=rgba(PANEL, a), outline=rgba(ACC, a), width=int(6 * S))
    for k in range(3):
        aa = ang + k * 2 * math.pi / 3
        x1, y1 = cx + math.cos(aa) * r * 0.78, cy + math.sin(aa) * r * 0.78
        d.line(p(cx, cy, x1, y1), fill=rgba(ACC, a), width=int(16 * S))
    d.ellipse(p(cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2), fill=rgba(WHITE, a))

def vis_og_gear(d, lt, t):
    a = ease_out(lt / 0.4)
    run = max(0.0, lt - 0.5)
    motor_turns = run * 2.2               # turns per second
    wheel_turns = motor_turns / 9.0
    ma = motor_turns * 2 * math.pi
    wa = wheel_turns * 2 * math.pi
    # motor -> pinion -> big gear -> wheel
    text_c(d, 150, 80, "МОТОР", FL("InterDisplay-Black.otf", 40), rgba(ACC, a))
    motor_icon(d, 150, 300, 95, ma, a)
    d.line(p(245, 300, 330, 300), fill=rgba(MUTED, a), width=int(14 * S))
    # one mesh, drawn 1:2.8 for clarity (real unit: two stages ≈ 9:1)
    gear(d, 375, 300, 50, 10, ma, ACC, a=a, hub=BG)
    gear(d, 375 + 50 + 140, 300, 140, 28, -ma / 2.8 + math.pi / 28, WHITE, a=a * 0.92, hub=BG)
    text_c(d, 565, 80, "РЕДУКТОР", FL("InterDisplay-Black.otf", 40), rgba(WHITE, a))
    d.line(p(715, 300, 750, 300), fill=rgba(MUTED, a), width=int(14 * S))
    tire(d, 815, 300, 70, wa, ACC2, alpha=a)
    text_c(d, 815, 385, "КОЛЕСО", FL("InterDisplay-Black.otf", 34), rgba(ACC2, a))
    # counters
    ca = ease_out((lt - 0.8) / 0.4)
    fb = FL("InterDisplay-Black.otf", 60)
    text_c(d, 225, 500, f"{motor_turns:4.1f}", fb, rgba(ACC, ca))
    text_c(d, 225, 570, "обороты мотора", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, ca))
    text_c(d, 675, 500, f"{wheel_turns:4.2f}", fb, rgba(ACC2, ca))
    text_c(d, 675, 570, "обороты колеса", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, ca))
    ra = back_out((lt - 1.6) / 0.5)
    if ra > 0.01:
        d.rounded_rectangle(p(300, 630, 600, 730), radius=30 * S, fill=rgba(ACC, clamp(ra)))
        text_c(d, 450, 640, "≈ 9 : 1", FL("InterDisplay-Black.otf", max(1, int(70 * clamp(ra)))), rgba(BG, clamp(ra)))
    sa = ease_out((lt - 3.0) / 0.5)
    text_c(d, 450, 760, "ОДНА ПЕРЕДАЧА: 0 → МАКСИМУМ", FL("InterDisplay-Black.otf", 40), rgba(WHITE, sa))

# ---------------- scene 6: Porsche Taycan two-speed rear unit ----------------
def vis_og_taycan(d, lt, t):
    a = ease_out(lt / 0.4)
    text_c(d, 450, 90, "ИСКЛЮЧЕНИЕ: 2 ПЕРЕДАЧИ СЗАДИ", FL("InterDisplay-Black.otf", 40), rgba(WHITE, a))
    # car accelerating across a road
    dur = sdur("og_taycan")
    k = ease_inout((lt - 0.3) / (dur - 0.8))
    d.line(p(40, 380, 860, 380), fill=rgba(DARK, a), width=int(6 * S))
    for i in range(8):
        x = (i * 120 - t * 300 * (0.3 + k)) % 960 - 40
        d.line(p(x, 380, x + 50, 380), fill=rgba(MUTED, a * 0.6), width=int(6 * S))
    cx = 220 + 420 * k
    car_side(d, cx, 290, 0.85, WHITE, alpha=a)
    for i in range(4):
        y = 230 + i * 26
        L_ = 60 + 80 * k
        d.line(p(cx - 210 - L_, y, cx - 210, y), fill=rgba(ACC, a * 0.5 * (0.4 + k)), width=int(5 * S))
    # gear selector: 1st during first 45%, then 2nd
    in2 = k > 0.5
    rows = [("1-я", "≈ 15 : 1", "СТАРТ", 15, ACC2, not in2), ("2-я", "≈ 8 : 1", "ЭКОНОМИЯ · СКОРОСТЬ", 8, ACC, in2)]
    for j, (g, rat, use, val, col, on) in enumerate(rows):
        ra = ease_out((lt - 0.6 - j * 0.6) / 0.5)
        y = 470 + j * 150
        hl = 1.0 if on else 0.35
        d.rounded_rectangle(p(70, y, 830, y + 120), radius=26 * S, fill=rgba(PANEL, ra), outline=rgba(col, ra * hl), width=int((6 if on else 3) * S))
        text_c(d, 140, y + 28, g, FL("InterDisplay-Black.otf", 52), rgba(col, ra * hl))
        text_c(d, 330, y + 30, rat, FL("InterDisplay-Black.otf", 48), rgba(WHITE, ra * hl))
        text_c(d, 640, y + 40, use, FL("InterDisplay-Bold.otf", 28), rgba(MUTED if not on else WHITE, ra))
        # ratio bar
        bw = 260 * val / 15 * ra
        d.rounded_rectangle(p(510, y + 84, 510 + bw, y + 100), radius=8 * S, fill=rgba(col, ra * hl))

# ---------------- scene 7: outro ----------------
def vis_og_outro(d, lt, t):
    dur = sdur("og_outro")
    cut = dur * 0.5
    if lt < cut:
        items = ["МЕНЬШЕ ДЕТАЛЕЙ", "БЕЗ ПЕРЕКЛЮЧЕНИЙ", "ПЛАВНЫЙ РАЗГОН"]
        for i, it in enumerate(items):
            k = back_out((lt - 0.15 - i * 0.45) / 0.45)
            if k <= 0.01:
                continue
            y = 200 + i * 170
            x0 = 450 - 330 * clamp(k)
            d.rounded_rectangle(p(120, y, 780, y + 130), radius=36 * S, fill=rgba(PANEL, clamp(k)), outline=rgba(ACC, clamp(k)), width=int(4 * S))
            # check mark
            d.line(p(180, y + 68, 210, y + 98, 265, y + 36), fill=rgba(ACC, clamp(k)), width=int(14 * S), joint="curve")
            text_c(d, 525, y + 44, it, FL("InterDisplay-Black.otf", 42), rgba(WHITE, clamp(k)))
        gear(d, 450, 790, 60, 14, t * 1.5, ACC, a=ease_out((lt - 1.6) / 0.4), hub=BG)
    else:
        end_card(d, lt, cut)

VIS.update({"og_hook": vis_og_hook, "og_engine": vis_og_engine, "og_motor": vis_og_motor, "og_rpm": vis_og_rpm,
            "og_gear": vis_og_gear, "og_taycan": vis_og_taycan, "og_outro": vis_og_outro})
