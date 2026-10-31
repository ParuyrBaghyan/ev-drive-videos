# Visuals for "How an Electric Car Actually Works" (16:9 long-form).
# Runs inside tools/render_long.py globals. Logical canvas 1500 x 720.
# Every vis_*(d, lt, t, dur): lt = seconds since this scene's visual started.

COPPER = (214, 140, 82)
COLD = (90, 170, 255)
PH = [ACC, AIR, ACC2]          # three AC phases
CX = 750                        # canvas centre x

def appear(lt, at, dur=0.45): return ease_out((lt - at) / dur)
def pop(lt, at, dur=0.5): return clamp(back_out((lt - at) / dur), 0, 1.15)
def label_pill(d, x, y, s, col, a=1.0, size=30, fg=None):
    f = FL(BLACK, size); tw = d.textlength(s, font=f) / S
    rrect(d, x - tw / 2 - 22, y, x + tw / 2 + 22, y + size + 26, (size + 26) / 2, rgba(col, a))
    text_c(d, x, y + 11, s, size, rgba(fg or BG, a), BLACK)
def counter(v, fmt="{:,.0f}"): return fmt.format(v)

# ---------- car cutaway ----------
BODY = [(250, 505), (252, 445), (292, 412), (420, 388), (522, 302), (642, 280), (884, 282), (1012, 322),
        (1182, 378), (1242, 414), (1250, 505)]
WIN1 = [(545, 312), (650, 296), (742, 296), (742, 382), (470, 382)]
WIN2 = [(760, 296), (878, 298), (990, 352), (1004, 382), (760, 382)]
WHEELS = [(430, 512), (1070, 512)]
PACK = (470, 462, 1030, 500)
COMP = {  # name: (x0, y0, x1, y1)
    "battery": PACK,
    "bms": (490, 428, 570, 458),
    "inverter": (930, 400, 1010, 444),
    "motor": (1030, 430, 1110, 486),
    "charger": (1110, 380, 1176, 414),
    "port": (1196, 392, 1222, 414),
}
def comp_center(n):
    x0, y0, x1, y1 = COMP[n]; return ((x0 + x1) / 2, (y0 + y1) / 2)

def car_xray(d, a=1.0, solid=0.0, t=0.0, highlight=(), dim=0.35, labels=True, lab_a=1.0):
    fill = mix(PANEL, WHITE, solid)
    poly(d, [(x + 6, y + 12) for x, y in BODY], rgba((0, 0, 0), 0.3 * a))
    poly(d, BODY, rgba(fill, (0.75 + 0.25 * solid) * a))
    line(d, BODY + [BODY[0]], rgba(mix(MUTED, WHITE, solid), a), 3)
    poly(d, WIN1, rgba(BG, a)); poly(d, WIN2, rgba(BG, a))
    for wx, wy in WHEELS:
        circle(d, wx, wy, 74, rgba(BG, a)); circle(d, wx, wy, 60, rgba((52, 60, 74), a))
        circle(d, wx, wy, 22, rgba(MUTED, a))
    for n, (x0, y0, x1, y1) in COMP.items():
        hi = n in highlight
        col = ACC if hi else MUTED
        al = a * (1.0 if hi else dim)
        if hi:
            g = 0.5 + 0.5 * math.sin(t * 4)
            rrect(d, x0 - 8, y0 - 8, x1 + 8, y1 + 8, 10, rgba(ACC, (0.18 + 0.12 * g) * a))
        rrect(d, x0, y0, x1, y1, 6, rgba(mix(PANEL, col, 0.85 if hi else 0.4), al), rgba(col, al), 2)
        if n == "battery":
            for k in range(13):
                xx = x0 + 18 + k * 42
                rrect(d, xx, y0 + 7, xx + 32, y1 - 7, 4, rgba(BG if hi else DARK, al * 0.8))

def car_solid(d, x, y, sc, col, a=1.0):
    pts = [(-250, 30), (-252, 0), (-235, -22), (-150, -48), (-70, -92), (30, -100), (120, -80), (215, -45), (250, -10), (252, 30)]
    poly(d, [(x + px * sc + 6, y + py * sc + 10) for px, py in pts], rgba((0, 0, 0), 0.3 * a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in pts], rgba(col, a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in [(-120, -50), (-58, -84), (20, -90), (20, -52)]], rgba(BG, a))
    poly(d, [(x + px * sc, y + py * sc) for px, py in [(34, -88), (110, -74), (165, -52), (34, -52)]], rgba(BG, a))
    for wx in (-150, 150):
        circle(d, x + wx * sc, y + 30 * sc, 50 * sc, rgba(BG, a)); circle(d, x + wx * sc, y + 30 * sc, 38 * sc, rgba((70, 78, 92), a))
    line(d, [(x - 248 * sc, y - 6 * sc), (x - 210 * sc, y - 18 * sc)], rgba(ACC, a), 7 * sc)

def battery_icon(d, x, y, w, h, level, col, a=1.0, outline=WHITE):
    rrect(d, x, y, x + w, y + h, 14, rgba(PANEL, a), rgba(outline, a), 5)
    rrect(d, x + w, y + h * 0.32, x + w + 16, y + h * 0.68, 5, rgba(outline, a))
    iw = (w - 20) * clamp(level)
    if iw > 4:
        rrect(d, x + 10, y + 10, x + 10 + iw, y + h - 10, 8, rgba(col, a))

def cylinder_cell(d, x, y, w, h, col, a=1.0, label=None):
    rrect(d, x + 5, y + 8, x + w + 5, y + h + 8, w * 0.18, rgba((0, 0, 0), 0.3 * a))
    rrect(d, x, y, x + w, y + h, w * 0.18, rgba(col, a))
    rrect(d, x + w * 0.3, y - h * 0.035, x + w * 0.7, y + 4, 4, rgba(MUTED, a))
    rrect(d, x + w * 0.12, y + h * 0.1, x + w * 0.28, y + h * 0.9, w * 0.08, rgba((255, 255, 255), 0.25 * a))

def gear(d, cx, cy, r, teeth, ang, col, a=1.0, depth=None):
    depth = depth or max(9, r * 0.14)
    ro, ri = r + depth * 0.5, r - depth * 0.5
    pts = []
    for k in range(teeth):
        base = ang + k * 2 * math.pi / teeth; step = 2 * math.pi / teeth
        for f, rr in ((0.0, ri), (0.18, ro), (0.5, ro), (0.68, ri)):
            pts.append((cx + math.cos(base + f * step) * rr, cy + math.sin(base + f * step) * rr))
    poly(d, [(x + 6, y + 9) for x, y in pts], rgba((0, 0, 0), 0.35 * a))
    poly(d, pts, rgba(col, a))
    circle(d, cx, cy, ri * 0.62, rgba(PANEL, a))
    circle(d, cx, cy, ri * 0.22, rgba(col, a))
    for k in range(4):
        aa = ang + k * math.pi / 2 + math.pi / 4
        line(d, [(cx + math.cos(aa) * ri * 0.22, cy + math.sin(aa) * ri * 0.22), (cx + math.cos(aa) * ri * 0.62, cy + math.sin(aa) * ri * 0.62)], rgba(col, a), max(4, r * 0.07))

def chip(d, x, y, w, h, lab, col=ACC, a=1.0, size=30):
    for k in range(5):
        yy = y + h * (k + 1) / 6
        line(d, [(x - 14, yy), (x, yy)], rgba(MUTED, a), 4); line(d, [(x + w, yy), (x + w + 14, yy)], rgba(MUTED, a), 4)
    rrect(d, x, y, x + w, y + h, 12, rgba(PANEL, a), rgba(col, a), 4)
    text_c(d, x + w / 2, y + h / 2 - size * 0.62, lab, size, rgba(col, a), BLACK)

def chart_axes(d, x0, y0, x1, y1, xl, yl, a=1.0):
    line(d, [(x0, y1), (x1, y1)], rgba(MUTED, a), 4); line(d, [(x0, y0), (x0, y1)], rgba(MUTED, a), 4)
    text_c(d, (x0 + x1) / 2, y1 + 18, xl, 24, rgba(MUTED, a))
    text_l(d, x0 + 12, y0 - 8, yl, 24, rgba(MUTED, a))

def wave_pts(x0, x1, yc, amp, freq, phase, n=120):
    return [(x0 + (x1 - x0) * k / n, yc - amp * math.sin(2 * math.pi * freq * k / n + phase)) for k in range(n + 1)]

def thermometer(d, x, y, h, level, col, a=1.0):
    rrect(d, x - 22, y, x + 22, y + h, 22, rgba(PANEL, a), rgba(WHITE, a), 4)
    circle(d, x, y + h + 18, 36, rgba(PANEL, a), rgba(WHITE, a), 4)
    circle(d, x, y + h + 18, 26, rgba(col, a))
    fh = (h - 16) * clamp(level)
    rrect(d, x - 11, y + h - fh, x + 11, y + h + 8, 11, rgba(col, a))

def snowflake(d, x, y, r, col, a=1.0):
    for k in range(3):
        ang = k * math.pi / 3
        dx, dy = math.cos(ang) * r, math.sin(ang) * r
        line(d, [(x - dx, y - dy), (x + dx, y + dy)], rgba(col, a), 6)
        for sgn in (-1, 1):
            bx, by = x + sgn * dx * 0.6, y + sgn * dy * 0.6
            for s2 in (-0.6, 0.6):
                line(d, [(bx, by), (bx + sgn * math.cos(ang + s2) * r * 0.3, by + sgn * math.sin(ang + s2) * r * 0.3)], rgba(col, a), 5)

def plug_icon(d, x, y, s, col, a=1.0):
    rrect(d, x - 30 * s, y - 34 * s, x + 30 * s, y + 20 * s, 12 * s, rgba(col, a))
    line(d, [(x - 13 * s, y - 34 * s), (x - 13 * s, y - 60 * s)], rgba(col, a), 9 * s)
    line(d, [(x + 13 * s, y - 34 * s), (x + 13 * s, y - 60 * s)], rgba(col, a), 9 * s)
    line(d, [(x, y + 20 * s), (x, y + 50 * s)], rgba(col, a), 10 * s)

def pylon(d, x, y, s, col, a=1.0):
    line(d, [(x - 40 * s, y + 60 * s), (x, y - 70 * s), (x + 40 * s, y + 60 * s)], rgba(col, a), 7 * s)
    line(d, [(x - 55 * s, y - 35 * s), (x + 55 * s, y - 35 * s)], rgba(col, a), 7 * s)
    line(d, [(x - 40 * s, y), (x + 40 * s, y)], rgba(col, a), 6 * s)
    line(d, [(x - 28 * s, y + 25 * s), (x + 28 * s, y - 15 * s)], rgba(col, a), 5 * s)

# ======================= INTRO =======================
def vis_intro_missing(d, lt, t, dur):
    car_solid(d, CX, 330, 1.3, WHITE, appear(lt, 0))
    items = [("ENGINE", 260, 520), ("GEARBOX", 620, 590), ("EXHAUST", 900, 590), ("OIL CHANGES", 1250, 520)]
    for i, (s, x, y) in enumerate(items):
        k = pop(lt, 0.7 + i * 1.2)
        if k <= 0: continue
        a = clamp(k)
        f = FL(BLACK, 40); tw = d.textlength(s, font=f) / S
        rrect(d, x - tw / 2 - 26, y, x + tw / 2 + 26, y + 70, 35, rgba(PANEL, a), rgba(DARK, a), 3)
        text_c(d, x, y + 13, s, 40, rgba(WHITE, a), BLACK)
        st = ease_out((lt - 1.05 - i * 1.2) / 0.3)
        if st > 0:
            line(d, [(x - tw / 2 - 18, y + 35), (x - tw / 2 - 18 + (tw + 36) * st, y + 35)], rgba(ACC2, a), 9)

def vis_intro_xray(d, lt, t, dur):
    k = ease_inout((lt - 0.3) / 1.4)
    car_xray(d, 1, solid=1 - k, t=t, highlight=("battery", "inverter", "motor", "bms", "charger", "port") if k > 0.6 else (), dim=0.6 * k)
    sx = 200 + 1150 * ((lt * 0.45) % 1.0)
    if k > 0.2:
        line(d, [(sx, 240), (sx, 600)], rgba(ACC, 0.5 * k), 4)
    q = pop(lt, dur * 0.55)
    if q > 0:
        text_c(d, CX, 625, "WHAT'S UNDER THE FLOOR?", 52, rgba(ACC, clamp(q)), BLACK)

CH_NODES = ["Battery", "BMS", "Inverter", "Motor", "Gear", "Regen", "Thermal", "Charging"]
def vis_intro_map(d, lt, t, dur):
    pts = [(160 + i * 168, 330 + (50 if i % 2 else -50)) for i in range(8)]
    k = ease_inout((lt - 0.2) / (dur * 0.6))
    pl = partial(pts, k)
    glow_line(d, pl, DARK, 1, 10)
    plug_icon(d, 70, 340, 0.8, ACC, appear(lt, 0))
    if k >= 1:
        flow(d, pts, t, ACC, 1, n=5, r=9, speed=0.25)
    for i, (x, y) in enumerate(pts):
        kk = pop(lt, 0.2 + dur * 0.6 * i / 7)
        if kk <= 0: continue
        a = clamp(kk)
        circle(d, x, y, 44 * kk, rgba(ACC, a)); text_c(d, x, y - 22, f"{i + 1:02d}", 34, rgba(BG, a), BLACK)
        text_c(d, x, y + (64 if i % 2 else -100), CH_NODES[i].upper(), 26, rgba(WHITE, a), BLACK)
    w = appear(lt, dur * 0.7)
    if w > 0:
        text_c(d, CX, 560, "PLUG  →  WHEELS", 54, rgba(ACC, w), BLACK)

# ======================= 01 BATTERY =======================
def vis_xray_battery(d, lt, t, dur):
    car_xray(d, 1, t=t, highlight=("battery",), dim=0.25)
    a = appear(lt, 0.5)
    x0, y0, x1, y1 = PACK
    line(d, [((x0 + x1) / 2, y1 + 10), ((x0 + x1) / 2, 600)], rgba(ACC, a), 3)
    label_pill(d, (x0 + x1) / 2, 600, "BATTERY PACK", ACC, a, 34)
    b = appear(lt, dur * 0.45)
    if b > 0:
        text_c(d, CX, 120, "NOT ONE BATTERY…", 40, rgba(MUTED, b), BLACK)
        # many cells raining into rows
        for r in range(3):
            for c in range(22):
                kk = ease_out((lt - dur * 0.5 - (r * 22 + c) * 0.025) / 0.4)
                if kk <= 0: continue
                xx = 300 + c * 42; yy = 175 + r * 26 - 20 * (1 - kk)
                circle(d, xx, yy, 11, rgba(ACC, kk))

def vis_cell_compare(d, lt, t, dur):
    # real proportions: 2170 = 21 x 70 mm, AA = 14.5 x 50.5 mm (scale 5 px/mm)
    a = appear(lt, 0)
    sc = 5.0
    cylinder_cell(d, 230, 560 - 70 * sc, 21 * sc, 70 * sc, ACC, a)
    text_c(d, 230 + 10.5 * sc, 580, "2170 CELL", 30, rgba(ACC, a), BLACK)
    text_c(d, 230 + 10.5 * sc, 620, "21 × 70 mm", 24, rgba(MUTED, a))
    b = appear(lt, 0.6)
    cylinder_cell(d, 420, 560 - 50.5 * sc, 14.5 * sc, 50.5 * sc, MUTED, b)
    text_c(d, 420 + 7.25 * sc, 580, "AA", 30, rgba(MUTED, b), BLACK)
    text_c(d, 420 + 7.25 * sc, 620, "14.5 × 50 mm", 24, rgba(MUTED, b))
    # counter + dot grid
    k = ease_inout((lt - 1.0) / (dur * 0.6))
    n = int(4416 * k)
    panel(d, 640, 90, 1430, 660, appear(lt, 0.3))
    text_c(d, 1035, 120, "TESLA MODEL 3 PACK", 30, rgba(MUTED, appear(lt, 0.3)), BLACK)
    text_c(d, 1035, 170, f"{n:,}", 110, rgba(WHITE, appear(lt, 0.3)), BLACK)
    text_c(d, 1035, 300, "CELLS", 34, rgba(ACC, appear(lt, 0.3)), BLACK)
    shown = int(276 * k)  # 1 dot = 16 cells
    for i in range(shown):
        r, c = divmod(i, 23)
        circle(d, 700 + c * 29.5, 370 + r * 19, 7, rgba(ACC, 0.9))
    text_c(d, 1035, 616, "1 dot = 16 cells", 20, rgba(MUTED, appear(lt, 1.2)))

def vis_series_parallel(d, lt, t, dur):
    a = appear(lt, 0)
    # one parallel group (left)
    gx, gy = 150, 210
    for k in range(4):
        cylinder_cell(d, gx + k * 46, gy, 36, 120, ACC, a)
    line(d, [(gx - 10, gy - 22), (gx + 180, gy - 22)], rgba(WHITE, a), 5)
    line(d, [(gx - 10, gy + 142), (gx + 180, gy + 142)], rgba(WHITE, a), 5)
    text_c(d, gx + 85, gy + 170, "PARALLEL", 32, rgba(WHITE, a), BLACK)
    text_c(d, gx + 85, gy + 212, "+ capacity", 28, rgba(ACC, a), BOLD)
    # series chain (right)
    b = appear(lt, dur * 0.3)
    k = ease_inout((lt - dur * 0.35) / (dur * 0.5))
    ngr = 10
    x0, y0 = 520, 230
    for i in range(ngr):
        kk = ease_out((k * ngr - i))
        if kk <= 0: continue
        xx = x0 + i * 88
        rrect(d, xx, y0, xx + 64, y0 + 110, 10, rgba(mix(PANEL, ACC, 0.85), kk), rgba(ACC, kk), 3)
        text_c(d, xx + 32, y0 + 38, "+", 34, rgba(BG, kk), BLACK)
        if i:
            line(d, [(xx - 24, y0 + 55), (xx, y0 + 55)], rgba(WHITE, kk), 5)
    if b > 0:
        text_c(d, 960, y0 + 140, "SERIES  ×  96 GROUPS", 32, rgba(WHITE, b), BLACK)
        text_c(d, 960, y0 + 182, "+ voltage", 28, rgba(ACC, b), BOLD)
    v = 3.65 * 96 * k * 0 + 0
    c = appear(lt, dur * 0.55)
    if c > 0:
        kv = ease_inout((lt - dur * 0.55) / (dur * 0.35))
        panel(d, 470, 470, 1450, 650, c)
        lo, hi = int(350 * kv), int(400 * kv)
        text_c(d, 960, 500, f"≈ {lo}–{hi} V", 84, rgba(ACC, c), BLACK)
        text_c(d, 960, 605, "96 × ~3.6–4.2 V per group", 24, rgba(MUTED, c))

def vis_cell_formats(d, lt, t, dur):
    cols = [(300, "CYLINDRICAL"), (750, "POUCH"), (1200, "PRISMATIC")]
    for i, (x, lab) in enumerate(cols):
        k = pop(lt, 0.2 + i * 0.7)
        if k <= 0: continue
        a = clamp(k); y = 380
        if i == 0:
            for j in range(3): cylinder_cell(d, x - 95 + j * 70, y - 170, 50, 170, MUTED, a)
        elif i == 1:
            poly(d, [(x - 120, y - 150), (x + 120, y - 150), (x + 128, y), (x - 128, y)], rgba(ACC, a))
            rrect(d, x - 60, y - 178, x - 30, y - 150, 4, rgba(MUTED, a)); rrect(d, x + 30, y - 178, x + 60, y - 150, 4, rgba(MUTED, a))
            line(d, [(x - 112, y - 120), (x + 112, y - 120)], rgba((255, 255, 255), 0.3 * a), 4)
        else:
            rrect(d, x - 110, y - 170, x + 110, y, 12, rgba(MUTED, a))
            circle(d, x - 55, y - 186, 14, rgba(WHITE, a)); circle(d, x + 55, y - 186, 14, rgba(WHITE, a))
        text_c(d, x, y + 30, lab, 34, rgba(ACC if i == 1 else WHITE, a), BLACK)
    b = appear(lt, dur * 0.5)
    if b > 0:
        kk = ease_inout((lt - dur * 0.5) / 1.2)
        panel(d, 420, 500, 1080, 660, b)
        text_c(d, 750, 516, "CHEVY BOLT PACK", 26, rgba(MUTED, b), BLACK)
        text_c(d, 750, 556, f"{int(288 * kk)} POUCH CELLS", 60, rgba(ACC, b), BLACK)

def vis_cog(d, lt, t, dur):
    car_xray(d, 1, solid=0.0, t=t, highlight=("battery",), dim=0.2)
    # centre of gravity marker drops
    k = ease_inout((lt - 0.8) / 1.6)
    y = lerp(330, 470, k)
    x = 760
    circle(d, x, y, 30, rgba(WHITE, 1));
    d.pieslice(p(x - 30, y - 30, x + 30, y + 30), 0, 90, fill=rgba(BG)); d.pieslice(p(x - 30, y - 30, x + 30, y + 30), 180, 270, fill=rgba(BG))
    circle(d, x, y, 30, None, rgba(WHITE), 4)
    a = appear(lt, 0.6)
    label_pill(d, x + 230, y - 100, "CENTER OF GRAVITY", WHITE, a, 26)
    if k > 0.05:
        arrow(d, x - 60, 330, x - 60, y, ACC, 6, k, 22)
    # frunk
    f = appear(lt, dur * 0.7)
    if f > 0:
        g = 0.5 + 0.5 * math.sin(t * 4)
        rrect(d, 270, 412, 400, 470, 10, rgba(ACC, (0.4 + 0.3 * g) * f), rgba(ACC, f), 3)
        line(d, [(335, 412), (335, 300)], rgba(ACC, f), 3)
        label_pill(d, 335, 248, "FRONT TRUNK", ACC, f, 28)
    text_c(d, CX, 640, "HEAVY PACK  =  LOW & CENTRAL", 34, rgba(MUTED, appear(lt, 1.8)), BLACK)

# ======================= 02 BMS =======================
def vis_bms_monitor(d, lt, t, dur):
    chip(d, 650, 280, 200, 140, "BMS", ACC, appear(lt, 0), 52)
    text_c(d, CX, 440, "the pack's brain", 26, rgba(MUTED, appear(lt, 0.4)))
    pos = [(150 + i * 170, 90) for i in range(8)]
    for i, (x, y) in enumerate(pos):
        a = appear(lt, 0.3 + i * 0.12)
        cylinder_cell(d, x, 50, 70, 100, MUTED, a)
        v = 3.70 + 0.012 * math.sin(t * 1.7 + i * 1.3) + 0.006 * i % 0.02
        tc = 25 + 1.2 * math.sin(t * 0.9 + i)
        text_c(d, x + 35, 160, f"{v:.2f} V", 24, rgba(ACC, a), BLACK)
        text_c(d, x + 35, 190, f"{tc:.0f} °C", 22, rgba(ACC2, a), BOLD)
        if a > 0.5:
            pts = [(x + 35, 226), (x + 35, 248), (CX + (x + 35 - CX) * 0.3, 276)]
            line(d, pts, rgba(DARK, a), 3)
            flow(d, pts, t + i * 0.13, ACC, a * 0.9, n=2, r=5, speed=0.6, trail=False)
    c = appear(lt, dur * 0.65)
    if c > 0:
        panel(d, 560, 500, 940, 640, c)
        amps = 120 + 40 * math.sin(t * 1.1)
        text_c(d, CX, 516, "PACK CURRENT", 24, rgba(MUTED, c), BLACK)
        text_c(d, CX, 552, f"{amps:.0f} A", 56, rgba(WHITE, c), BLACK)
    text_c(d, 1340, 660, "example readings", 18, rgba(MUTED, appear(lt, 1)))

def vis_soc(d, lt, t, dur):
    k = ease_inout((lt - 0.4) / 2.0)
    a = appear(lt, 0)
    battery_icon(d, 360, 170, 620, 260, 0.78 * k, ACC, a)
    text_c(d, 670, 245, f"{int(78 * k)}%", 110, rgba(WHITE if k < 0.4 else BG, a), BLACK)
    text_c(d, 670, 470, "STATE OF CHARGE", 40, rgba(ACC, a), BLACK)
    ins = [("VOLTAGE", ACC), ("CURRENT", WHITE), ("TEMPERATURE", ACC2)]
    for i, (s, col) in enumerate(ins):
        b = appear(lt, 0.2 + i * 0.25)
        label_pill(d, 1250, 160 + i * 100, s, col, b, 26)
        arrow(d, 1110, 185 + i * 100, 1020, 300, MUTED, 4, b * 0.8, 18)

def vis_balance(d, lt, t, dur):
    lv = [0.84, 0.77, 0.81, 0.70, 0.79, 0.83, 0.76]
    target = 0.70 + (0.80 - 0.70) * 0
    k = ease_inout((lt - dur * 0.55) / (dur * 0.35))
    a = appear(lt, 0)
    panel(d, 200, 70, 1300, 660, a)
    base, top = 560, 150
    weakest = 3
    for i, v in enumerate(lv):
        vv = lerp(v, 0.785, k)
        x = 300 + i * 140
        rrect(d, x, top, x + 90, base, 14, rgba(DARK, a))
        h = (base - top) * vv
        col = ACC2 if (i == weakest and k < 0.5) else ACC
        rrect(d, x, base - h, x + 90, base, 14, rgba(col, a))
        text_c(d, x + 45, base + 16, f"{int(vv * 100)}%", 26, rgba(WHITE, a), BLACK)
    w = appear(lt, 1.0) * (1 - k)
    if w > 0:
        x = 300 + weakest * 140 + 45
        text_c(d, x, 92, "WEAKEST CELL", 26, rgba(ACC2, w), BLACK)
        line(d, [(150 + 140, base - (base - top) * lv[weakest]), (1250, base - (base - top) * lv[weakest])], rgba(ACC2, 0.7 * w), 3)
    if k > 0.1:
        text_c(d, CX, 92, "BALANCED", 32, rgba(ACC, k), BLACK)

def vis_contactor(d, lt, t, dur):
    a = appear(lt, 0)
    battery_icon(d, 120, 230, 300, 150, 0.7, ACC, a)
    text_c(d, 270, 410, "HIGH-VOLTAGE PACK", 26, rgba(WHITE, a), BLACK)
    rrect(d, 1080, 210, 1400, 400, 20, rgba(PANEL, a), rgba(WHITE, a), 4)
    text_c(d, 1240, 280, "REST OF", 30, rgba(WHITE, a), BLACK); text_c(d, 1240, 320, "THE CAR", 30, rgba(WHITE, a), BLACK)
    open_k = ease_inout((lt - dur * 0.62) / 0.5)
    # wires and switch
    line(d, [(436, 305), (690, 305)], rgba(ACC, a), 8)
    line(d, [(830, 305), (1080, 305)], rgba(ACC if open_k < 0.5 else DARK, a), 8)
    circle(d, 690, 305, 14, rgba(WHITE, a)); circle(d, 830, 305, 14, rgba(WHITE, a))
    ang = -0.45 * open_k
    line(d, [(690, 305), (690 + 140 * math.cos(ang), 305 + 140 * math.sin(ang))], rgba(WHITE, a), 10)
    label_pill(d, 760, 380, "CONTACTOR", WHITE if open_k < 0.5 else ACC2, a, 26)
    if open_k < 0.5:
        flow(d, [(436, 305), (1080, 305)], t, ACC, a, n=6, r=8, speed=0.5)
    warns = [("TOO HOT", ACC2), ("TOO FULL", ACC2), ("TOO EMPTY", ACC2)]
    for i, (s, col) in enumerate(warns):
        b = pop(lt, dur * 0.3 + i * 0.35)
        if b > 0: label_pill(d, 420 + i * 330, 520, s, col, clamp(b), 28)
    if open_k > 0.5:
        text_c(d, CX, 150, "DISCONNECTED", 44, rgba(ACC2, open_k), BLACK)

# ======================= 03 INVERTER =======================
def vis_dc_ac(d, lt, t, dur):
    a = appear(lt, 0)
    panel(d, 120, 40, 1380, 320, a)
    text_l(d, 160, 62, "DIRECT CURRENT (DC)", 30, rgba(WHITE, a), BLACK)
    text_r(d, 1340, 62, "from the battery", 24, rgba(MUTED, a))
    line(d, [(180, 210), (1320, 210)], rgba(ACC, a), 8)
    for k in range(6):
        xx = 200 + ((t * 160 + k * 200) % 1120)
        arrow(d, xx, 170, xx + 60, 170, ACC, 5, a * 0.7, 18)
    b = appear(lt, dur * 0.45)
    if b > 0:
        panel(d, 120, 370, 1380, 680, b)
        text_l(d, 160, 392, "3-PHASE ALTERNATING CURRENT (AC)", 30, rgba(WHITE, b), BLACK)
        text_r(d, 1340, 392, "what the motor needs", 24, rgba(MUTED, b))
        for i in range(3):
            pts = wave_pts(180, 1320, 560, 85, 3, -t * 3 + i * 2 * math.pi / 3)
            line(d, pts, rgba(PH[i], b), 6)

def vis_switches(d, lt, t, dur):
    a = appear(lt, 0)
    rrect(d, 300, 90, 1200, 520, 26, rgba(PANEL, a), rgba(ACC, a), 4)
    text_c(d, CX, 110, "INVERTER", 40, rgba(ACC, a), BLACK)
    rate = 1.2 + 6 * ease_inout((lt - 1.0) / 2.5)
    for leg in range(3):
        x = 440 + leg * 310
        line(d, [(x + 50, 180), (x + 50, 480)], rgba(DARK, a), 6)
        for j in range(2):
            on = (math.sin(t * rate * 2 * math.pi + leg * 2.1 + j * math.pi) > 0) == (j == 0)
            y = 200 + j * 150
            rrect(d, x, y, x + 100, y + 100, 14, rgba(PH[leg] if on else DARK, a), rgba(PH[leg], a), 3)
            text_c(d, x + 50, y + 32, "ON" if on else "OFF", 28, rgba(BG if on else MUTED, a), BLACK)
    b = appear(lt, dur * 0.25)
    if b > 0:
        label_pill(d, 470, 560, "SILICON", MUTED, b, 26); label_pill(d, 1030, 560, "SILICON CARBIDE", ACC, b, 26)
    c = appear(lt, dur * 0.6)
    if c > 0:
        kk = ease_inout((lt - dur * 0.6) / 1.2)
        text_c(d, CX, 620, f"{int(6000 * kk):,} – {int(24000 * kk):,}  SWITCHES PER SECOND", 36, rgba(WHITE, c), BLACK)

def vis_pwm(d, lt, t, dur):
    a = appear(lt, 0)
    panel(d, 120, 40, 1380, 680, a)
    k = ease_inout((lt - 0.4) / (dur * 0.7))
    x0, x1 = 180, 1320
    # PWM pulses (duty follows sine)
    text_l(d, 160, 62, "PULSES", 28, rgba(MUTED, a), BLACK)
    n = 40
    for i in range(int(n * k)):
        xs = x0 + (x1 - x0) * i / n; wd = (x1 - x0) / n
        duty = 0.5 + 0.45 * math.sin(2 * math.pi * 2 * (i + 0.5) / n)
        rrect(d, xs + 2, 120, xs + 2 + wd * duty, 270, 3, rgba(ACC, a))
    text_l(d, 160, 330, "RESULT: SMOOTH WAVE", 28, rgba(MUTED, a), BLACK)
    pts = wave_pts(x0, x1, 510, 120, 2, 0)
    pl = partial(pts, k)
    glow_line(d, pl, ACC, a, 7)
    line(d, [(x0, 510), (x1, 510)], rgba(DARK, a), 2)

def vis_pedal(d, lt, t, dur):
    a = appear(lt, 0)
    press = ease_inout((lt - dur * 0.25) / 1.5) * (0.8 + 0.2 * math.sin(t * 0.8))
    # pedal
    px, py = 200, 470
    ang = -1.25 + 0.45 * press
    line(d, [(px, py - 260), (px + 20, py - 120)], rgba(MUTED, a), 10)
    poly(d, [(px - 50, py - 120), (px + 90, py - 120 + 140 * math.sin(0.3 * press)), (px + 90, py - 80 + 140 * math.sin(0.3 * press)), (px - 50, py - 80)], rgba(WHITE, a))
    text_c(d, px + 20, py - 40, "ACCELERATOR", 24, rgba(WHITE, a), BLACK)
    arrow(d, 330, 330, 470, 330, MUTED, 6, a, 22)
    chip(d, 490, 250, 230, 160, "INVERTER", ACC, a, 34)
    text_c(d, 605, 430, "computer", 22, rgba(MUTED, a))
    b = appear(lt, 0.8)
    arrow(d, 740, 290, 860, 200, AIR, 5, b, 20); arrow(d, 740, 370, 860, 470, ACC2, 5, b, 20)
    label_pill(d, 1000, 160, "FREQUENCY → SPEED", AIR, b, 26)
    label_pill(d, 1000, 450, "STRENGTH → TORQUE", ACC2, b, 26)
    freq = 1.5 + 2.5 * press; amp = 30 + 70 * press
    pts = wave_pts(880, 1400, 340, amp, freq, -t * 4)
    line(d, pts, rgba(ACC, b), 6)
    c = appear(lt, dur * 0.65)
    if c > 0:
        text_c(d, CX, 600, "NO THROTTLE — A REQUEST TO A COMPUTER", 34, rgba(WHITE, c), BLACK)

# ======================= 04 MOTOR =======================
def motor_xsec(d, cx, cy, R, t, a=1.0, rot=0.0, lit=None, rotor="pm", coil_lab=False):
    # stator ring with 12 slots
    circle(d, cx, cy, R, rgba((60, 68, 82), a))
    circle(d, cx, cy, R * 0.72, rgba(BG, a))
    for k in range(12):
        ang = k * math.pi / 6
        ph = k % 3
        on = lit is not None and lit[ph] > 0.05
        col = mix(COPPER, PH[ph], lit[ph]) if lit is not None else COPPER
        x, y = cx + math.cos(ang) * R * 0.78, cy + math.sin(ang) * R * 0.78
        circle(d, x, y, R * 0.11, rgba(col, a))
        if on and lit[ph] > 0.5:
            circle(d, x, y, R * 0.16, rgba(PH[ph], 0.25 * a * lit[ph]))
    # rotor
    rr = R * 0.6
    circle(d, cx, cy, rr, rgba((88, 98, 114), a))
    if rotor == "pm":
        for k in range(4):
            a0 = math.degrees(rot) + k * 90
            col = ACC2 if k % 2 == 0 else AIR
            d.pieslice(p(cx - rr * 0.92, cy - rr * 0.92, cx + rr * 0.92, cy + rr * 0.92), a0 + 8, a0 + 82, fill=rgba(col, a))
            mid = math.radians(a0 + 45)
            text_c(d, cx + math.cos(mid) * rr * 0.62, cy + math.sin(mid) * rr * 0.62 - 14, "N" if k % 2 == 0 else "S", 26, rgba(BG, a), BLACK)
    else:
        for k in range(16):
            ang = rot + k * math.pi / 8
            x, y = cx + math.cos(ang) * rr * 0.8, cy + math.sin(ang) * rr * 0.8
            glow = 0.5 + 0.5 * math.sin(t * 6 + k)
            circle(d, x, y, rr * 0.09, rgba(mix((150, 160, 175), ACC, glow * 0.8), a))
    circle(d, cx, cy, rr * 0.2, rgba(PANEL, a)); circle(d, cx, cy, rr * 0.1, rgba(MUTED, a))

def vis_motor_parts(d, lt, t, dur):
    a = appear(lt, 0)
    motor_xsec(d, 600, 340, 270, t, a, rot=t * 0.8)
    b = appear(lt, 0.8)
    line(d, [(820, 180), (1000, 140)], rgba(WHITE, b), 3)
    label_pill(d, 1180, 112, "STATOR", COPPER, b, 32)
    text_c(d, 1180, 180, "fixed · copper coils", 26, rgba(MUTED, b))
    c = appear(lt, dur * 0.55)
    line(d, [(680, 400), (1000, 470)], rgba(WHITE, c), 3)
    label_pill(d, 1180, 440, "ROTOR", AIR, c, 32)
    text_c(d, 1180, 508, "spins inside", 26, rgba(MUTED, c))

def vis_rot_field(d, lt, t, dur):
    a = appear(lt, 0)
    w = 1.6
    phase = t * w
    lit = [max(0, math.sin(phase - i * 2 * math.pi / 3)) for i in range(3)]
    field = -phase + math.pi / 2
    motor_xsec(d, 600, 340, 270, t, a, rot=field - 0.35 - math.pi / 4, lit=lit)
    # field arrow
    L = 260
    x1, y1 = 600 + math.cos(field) * L, 340 + math.sin(field) * L
    glow_line(d, [(600 - math.cos(field) * L, 340 - math.sin(field) * L), (x1, y1)], ACC, 0.9 * a, 8)
    arrow(d, 600, 340, x1, y1, ACC, 8, a, 34)
    b = appear(lt, 0.6)
    for i in range(3):
        label_pill(d, 1150, 120 + i * 90, f"PHASE {'ABC'[i]}", PH[i], b * (0.35 + 0.65 * lit[i]), 26)
    c = appear(lt, dur * 0.45)
    if c > 0:
        text_c(d, 1150, 420, "ROTATING", 40, rgba(ACC, c), BLACK)
        text_c(d, 1150, 470, "MAGNETIC FIELD", 40, rgba(ACC, c), BLACK)
        text_c(d, 1150, 540, "rotor is pulled along", 26, rgba(MUTED, c))

def vis_motor_types(d, lt, t, dur):
    a = appear(lt, 0)
    motor_xsec(d, 400, 300, 220, t, a, rot=t * 1.2, rotor="pm")
    label_pill(d, 400, 560, "PERMANENT MAGNET", ACC, a, 28)
    text_c(d, 400, 620, "magnets lock onto the field", 24, rgba(MUTED, a))
    b = appear(lt, dur * 0.45)
    motor_xsec(d, 1100, 300, 220, t, b, rot=t * 1.0, rotor="ind")
    label_pill(d, 1100, 560, "INDUCTION", AIR, b, 28)
    text_c(d, 1100, 620, "field induces rotor currents", 24, rgba(MUTED, b))

def vis_torque_eff(d, lt, t, dur):
    a = appear(lt, 0)
    panel(d, 60, 50, 860, 660, a)
    chart_axes(d, 130, 120, 820, 560, "MOTOR SPEED (rpm)", "TORQUE", a)
    k = ease_inout((lt - 0.4) / 2.0)
    pts = []
    for i in range(101):
        x = i / 100
        y = 1.0 if x < 0.35 else 0.35 / x
        pts.append((130 + 690 * x, 560 - 380 * y))
    glow_line(d, partial(pts, k), ACC, a, 7)
    if k > 0.1:
        circle(d, 130, 180, 14, rgba(ACC, a)); text_l(d, 160, 140, "full torque at 0 rpm", 26, rgba(ACC, a), BLACK)
    b = appear(lt, dur * 0.55)
    if b > 0:
        kk = ease_inout((lt - dur * 0.55) / 1.4)
        arc(d, 1160, 330, 190, 0, 360, rgba(DARK, b), 46)
        arc(d, 1160, 330, 190, -90, -90 + 360 * 0.92 * kk, rgba(ACC, b), 46)
        text_c(d, 1160, 270, f"{int(90 * kk)}%+", 90, rgba(WHITE, b), BLACK)
        text_c(d, 1160, 570, "ELECTRICAL → MOTION", 26, rgba(MUTED, b), BLACK)
        text_c(d, 1160, 610, "permanent magnet motors", 22, rgba(MUTED, b))

# ======================= 05 GEAR =======================
def vis_reduction(d, lt, t, dur):
    a = appear(lt, 0)
    w1 = 2.4
    # 8-tooth pinion drives a 72-tooth gear: 9 : 1 (same tooth size)
    big_c = (560, 360); R1, R2 = 33, 297
    gear(d, big_c[0], big_c[1], R2, 72, -t * w1 / 9 + 0.02, MUTED, a, depth=16)
    px = big_c[0] - R1 - R2 - 2
    gear(d, px, big_c[1], R1, 8, t * w1, ACC, a, depth=16)
    text_c(d, px, big_c[1] + 50, "MOTOR", 26, rgba(ACC, a), BLACK)
    text_c(d, big_c[0], 672, "TO WHEELS", 24, rgba(WHITE, a), BLACK)
    b = appear(lt, 1.0)
    panel(d, 900, 70, 1440, 640, b)
    text_c(d, 1170, 100, "REDUCTION GEAR", 32, rgba(WHITE, b), BLACK)
    text_c(d, 1170, 160, "≈ 9 : 1", 110, rgba(ACC, b), BLACK)
    text_c(d, 1170, 300, "Tesla Model 3 · real unit uses two stages", 24, rgba(MUTED, b))
    c = appear(lt, dur * 0.5)
    if c > 0:
        kk = ease_inout((lt - dur * 0.5) / 1.2)
        text_c(d, 1170, 370, "SPEED", 26, rgba(MUTED, c), BLACK)
        text_c(d, 1170, 400, f"÷ {1 + 8 * kk:.0f}", 64, rgba(AIR, c), BLACK)
        text_c(d, 1170, 500, "TORQUE", 26, rgba(MUTED, c), BLACK)
        text_c(d, 1170, 530, f"× {1 + 8 * kk:.0f}", 64, rgba(ACC2, c), BLACK)

def vis_one_gear(d, lt, t, dur):
    a = appear(lt, 0)
    panel(d, 60, 40, 1440, 680, a)
    chart_axes(d, 140, 110, 1380, 600, "ROAD SPEED  →", "ENGINE / MOTOR rpm", a)
    k = ease_inout((lt - 0.3) / (dur * 0.55))
    # gas car sawtooth (8 gears)
    gas = []
    for g in range(8):
        x0 = 140 + 1240 * g / 8; x1 = 140 + 1240 * (g + 1) / 8
        gas += [(x0, 520 - 60), (x1, 260 + g * 8)]
        if g < 7: gas.append((x1, 520 - 60 + g * 6))
    line(d, partial(gas, k), rgba(MUTED, a), 5)
    rrect(d, 170, 130, 560, 240, 16, rgba(PANEL, a), rgba(DARK, a), 2)
    line(d, [(195, 170), (255, 170)], rgba(ACC, a), 8); text_l(d, 275, 152, "EV: ONE GEAR", 28, rgba(ACC, a), BLACK)
    line(d, [(195, 212), (255, 212)], rgba(MUTED, a), 5); text_l(d, 275, 194, "GAS: 8 GEARS", 28, rgba(MUTED, a), BLACK)
    ev = [(140, 590), (1380, 150)]
    glow_line(d, partial(ev, k), ACC, a, 7)
    b = appear(lt, dur * 0.65)
    if b > 0:
        label_pill(d, 1060, 130, "PORSCHE TAYCAN: 2 GEARS (EXCEPTION)", ACC2, b, 24)

# ======================= 06 REGEN =======================
def vis_regen_flow(d, lt, t, dur):
    car_xray(d, 1, t=t, highlight=("battery", "inverter", "motor"), dim=0.25)
    a = appear(lt, dur * 0.25)
    wx, wy = WHEELS[1]
    path = [(wx, wy), comp_center("motor"), comp_center("inverter"), (970, 450), (900, 481), (560, 481)]
    if a > 0:
        glow_line(d, path, ACC, 0.5 * a, 5)
        flow(d, path, t, ACC, a, n=7, r=9, speed=0.45)
    b = appear(lt, dur * 0.2)
    label_pill(d, 1070, 110, "MOTOR → GENERATOR", ACC, b, 30)
    line(d, [(1070, 170), (1070, 430)], rgba(ACC, 0.6 * b), 3)
    # speed readout decreasing
    k = ease_inout((lt - 0.5) / (dur * 0.8))
    panel(d, 120, 80, 470, 230, appear(lt, 0))
    text_c(d, 295, 94, "SPEED", 24, rgba(MUTED, appear(lt, 0)), BLACK)
    text_c(d, 295, 124, f"{int(60 - 45 * k)} mph", 64, rgba(WHITE, appear(lt, 0)), BLACK)
    c = appear(lt, dur * 0.8)
    if c > 0: label_pill(d, CX, 600, "REGENERATIVE BRAKING", ACC, c, 34)

def vis_regen_compare(d, lt, t, dur):
    a = appear(lt, 0)
    # gas brake disc glowing
    cx, cy = 360, 300
    heat = 0.5 + 0.5 * math.sin(t * 3)
    circle(d, cx, cy, 190, rgba(mix((90, 98, 112), HOT, 0.6 + 0.3 * heat), a))
    circle(d, cx, cy, 70, rgba(PANEL, a))
    for k in range(10):
        ang = k * math.pi / 5
        circle(d, cx + math.cos(ang) * 130, cy + math.sin(ang) * 130, 10, rgba(PANEL, a))
    rrect(d, cx + 120, cy - 120, cx + 200, cy + 30, 16, rgba(MUTED, a))
    for k in range(4):
        x = 200 + k * 100; ph = (t * 0.8 + k * 0.25) % 1
        pts = [(x + 12 * math.sin(j * 0.9 + t * 4), 110 - ph * 50 - j * 7) for j in range(12)]
        line(d, pts, rgba(HOT, a * (1 - ph)), 5)
    text_c(d, cx, 530, "GAS CAR BRAKES", 30, rgba(WHITE, a), BLACK)
    text_c(d, cx, 575, "speed → wasted heat", 26, rgba(HOT, a))
    b = appear(lt, dur * 0.35)
    if b > 0:
        kk = ease_inout((lt - dur * 0.35) / 1.6)
        panel(d, 760, 70, 1440, 640, b)
        text_c(d, 1100, 100, "REGEN RECOVERS ABOUT", 28, rgba(MUTED, b), BLACK)
        text_c(d, 1100, 150, f"{int(22 * kk)}%", 170, rgba(ACC, b), BLACK)
        text_c(d, 1100, 360, "of the energy", 30, rgba(WHITE, b), BLACK)
        battery_icon(d, 950, 430, 280, 110, 0.22 * kk + 0.4, ACC, b)
        text_c(d, 1100, 580, "EPA city + highway test · U.S. DOE", 22, rgba(MUTED, b))

def vis_regen_limits(d, lt, t, dur):
    a = appear(lt, 0)
    battery_icon(d, 140, 150, 300, 140, 1.0, ACC, a)
    text_c(d, 290, 310, "FULL", 32, rgba(WHITE, a), BLACK)
    b = appear(lt, 0.5)
    snowflake(d, 290, 470, 80, COLD, b)
    text_c(d, 290, 570, "VERY COLD", 32, rgba(COLD, b), BLACK)
    c = appear(lt, 0.9)
    panel(d, 560, 90, 1000, 620, c)
    text_c(d, 780, 110, "REGEN", 30, rgba(MUTED, c), BLACK)
    k = ease_inout((lt - 1.2) / 1.5)
    hgt = 420 * (1 - 0.75 * k)
    rrect(d, 700, 600 - 420, 860, 600 - 20, 16, rgba(DARK, c))
    rrect(d, 700, 600 - 20 - hgt, 860, 600 - 20, 16, rgba(ACC, c))
    e = appear(lt, dur * 0.55)
    if e > 0:
        cx, cy = 1230, 330
        g = 0.5 + 0.5 * math.sin(t * 4)
        circle(d, cx, cy, 150, rgba(mix((90, 98, 112), ACC2, 0.4 + 0.3 * g), e))
        circle(d, cx, cy, 55, rgba(PANEL, e))
        rrect(d, cx + 90, cy - 90, cx + 160, cy + 30, 14, rgba(MUTED, e))
        text_c(d, cx, 510, "FRICTION BRAKES", 30, rgba(ACC2, e), BLACK)
        text_c(d, cx, 552, "take over", 26, rgba(MUTED, e))

# ======================= 07 THERMAL =======================
def vis_temp_scale(d, lt, t, dur):
    a = appear(lt, 0)
    x0, x1, y = 180, 1320, 300
    n = 60
    for i in range(n):
        u = i / (n - 1)
        col = mix(COLD, ACC, u * 2) if u < 0.5 else mix(ACC, HOT, (u - 0.5) * 2)
        xs = x0 + (x1 - x0) * i / n
        d.rectangle(p(xs, y, xs + (x1 - x0) / n + 1, y + 70), fill=rgba(col, a))
    rrect(d, x0, y, x1, y + 70, 35, None, rgba(WHITE, a), 4)
    zones = [(x0 + 150, "TOO COLD", "sluggish · less power", COLD), (CX, "JUST RIGHT", "happy battery", ACC), (x1 - 150, "TOO HOT", "ages faster", HOT)]
    for i, (x, s1, s2, col) in enumerate(zones):
        b = appear(lt, 0.4 + i * 0.5)
        text_c(d, x, 180, s1, 40, rgba(col, b), BLACK)
        text_c(d, x, 410, s2, 28, rgba(WHITE, b))
    m = CX + 470 * math.sin(t * 0.7)
    poly(d, [(m, y - 6), (m - 18, y - 40), (m + 18, y - 40)], rgba(WHITE, a))

def vis_coolant(d, lt, t, dur):
    a = appear(lt, 0)
    x0, y0, x1, y1 = 260, 120, 1240, 560
    rrect(d, x0, y0, x1, y1, 24, rgba(PANEL, a), rgba(WHITE, a), 4)
    for r in range(4):
        for c in range(14):
            circle(d, x0 + 70 + c * 66, y0 + 70 + r * 100, 24, rgba(DARK, a))
    # serpentine channel between rows
    pts = [(x0 - 80, y0 + 120)]
    for r in range(4):
        yy = y0 + 120 + r * 100 - 0
        if r % 2 == 0: pts += [(x0 + 30, yy), (x1 - 30, yy)]
        else: pts += [(x1 - 30, yy), (x0 + 30, yy)]
        if r < 3: pts.append(pts[-1][0:1] + (yy + 100,) if False else (pts[-1][0], yy + 100))
    pts.append((x0 - 80, pts[-1][1]))
    warm = ease_inout((lt - dur * 0.6) / 0.8)
    col = mix(AIR, ACC2, warm)
    line(d, pts, rgba(col, 0.35 * a), 22)
    flow(d, pts, t, col, a, n=14, r=8, speed=0.12)
    b = appear(lt, 0.6)
    label_pill(d, CX, 600, "LIQUID COOLANT LOOP", col, b, 28)
    if warm < 0.5:
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1
            arrow(d, x1 + 30, 200 + k * 140, x1 + 90 + 60 * ph, 200 + k * 140, HOT, 6, b * (1 - ph), 20)
        text_c(d, x1 + 120, 120, "HEAT OUT", 24, rgba(HOT, b * (1 - warm * 2)), BLACK)
    else:
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1
            arrow(d, x0 - 150 + 60 * ph, 220 + k * 120, x0 - 40, 220 + k * 120, ACC2, 6, warm * (1 - ph), 20)
        text_c(d, x0 - 110, 100, "HEAT IN", 24, rgba(ACC2, warm), BLACK)

def vis_heat_pump(d, lt, t, dur):
    a = appear(lt, 0)
    panel(d, 40, 60, 700, 660, a)
    text_c(d, 370, 80, "HEAT PUMP", 34, rgba(WHITE, a), BLACK)
    text_c(d, 370, 125, "moves heat instead of making it", 22, rgba(MUTED, a))
    snowflake(d, 150, 350, 55, COLD, a)
    text_c(d, 150, 430, "cold outside air", 20, rgba(COLD, a))
    rrect(d, 290, 290, 450, 410, 18, rgba(DARK, a), rgba(MUTED, a), 3)
    text_c(d, 370, 330, "PUMP", 26, rgba(WHITE, a), BLACK)
    rrect(d, 520, 270, 660, 430, 18, rgba(mix(PANEL, ACC2, 0.4), a), rgba(ACC2, a), 3)
    text_c(d, 590, 320, "CABIN", 24, rgba(WHITE, a), BLACK); text_c(d, 590, 356, "& PACK", 24, rgba(WHITE, a), BLACK)
    flow(d, [(210, 350), (290, 350)], t, COLD, a, n=2, r=7, speed=0.8)
    flow(d, [(450, 350), (520, 350)], t, ACC2, a, n=2, r=7, speed=0.8)
    text_c(d, 370, 520, "like a fridge in reverse", 26, rgba(MUTED, a))
    b = appear(lt, dur * 0.4)
    if b > 0:
        kk = ease_inout((lt - dur * 0.4) / 1.8)
        panel(d, 760, 60, 1460, 660, b)
        text_c(d, 1110, 80, "RANGE KEPT BELOW FREEZING", 28, rgba(WHITE, b), BLACK)
        for i, (lab, v, col) in enumerate([("WITH HEAT PUMP", 83, ACC), ("WITHOUT", 75, MUTED)]):
            x = 920 + i * 330
            rrect(d, x - 70, 170, x + 70, 560, 16, rgba(DARK, b))
            hh = 390 * v / 100 * kk
            rrect(d, x - 70, 560 - hh, x + 70, 560, 16, rgba(col, b))
            text_c(d, x, 560 - hh - 66, f"{int(v * kk)}%", 50, rgba(WHITE, b), BLACK)
            text_c(d, x, 576, lab, 22, rgba(col, b), BLACK)
        text_c(d, 1110, 620, "18,000+ EVs · Recurrent data", 20, rgba(MUTED, b))

def vis_precondition(d, lt, t, dur):
    a = appear(lt, 0)
    route = [(140, 520), (380, 520), (520, 360), (800, 360), (980, 230), (1200, 230)]
    line(d, route, rgba(DARK, a), 16)
    k = ease_inout((lt - 0.3) / (dur * 0.75))
    glow_line(d, partial(route, k), ACC, a, 8)
    cxp, cyp = path_point(route, k * 0.9999)
    circle(d, cxp, cyp, 20, rgba(WHITE, a))
    # charger icon
    rrect(d, 1220, 140, 1320, 300, 14, rgba(PANEL, a), rgba(ACC, a), 4)
    bolt(d, 1270, 210, 0.6, rgba(ACC, a))
    text_c(d, 1270, 320, "FAST CHARGER", 22, rgba(ACC, a), BLACK)
    # battery temperature
    thermometer(d, 1380, 360, 200, 0.2 + 0.6 * k, mix(COLD, ACC, k), a)
    text_c(d, 1380, 620, "PACK TEMP", 20, rgba(MUTED, a), BLACK)
    b = appear(lt, dur * 0.3)
    label_pill(d, 600, 120, "PRECONDITIONING", ACC, b, 32)
    text_c(d, 600, 190, "warming the pack on the way", 24, rgba(MUTED, b))

# ======================= 08 CHARGING =======================
def vis_levels(d, lt, t, dur):
    rows = [("LEVEL 1", "120 V wall outlet", 1.9, "1–2 kW", "a few miles of range per hour", 0.2),
            ("LEVEL 2", "240 V", 19.2, "up to ~19 kW", "refills most EVs overnight", dur * 0.45)]
    for i, (n, v, kw, kwl, note, at) in enumerate(rows):
        a = appear(lt, at)
        if a <= 0: continue
        y = 90 + i * 290
        panel(d, 80, y, 1420, y + 240, a)
        text_l(d, 120, y + 30, n, 44, rgba(ACC, a), BLACK)
        text_l(d, 120, y + 92, v, 26, rgba(MUTED, a))
        kk = ease_inout((lt - at - 0.2) / 1.0)
        bw = 900 * kw / 19.2 * kk
        rrect(d, 440, y + 50, 1340, y + 110, 30, rgba(DARK, a))
        if bw > 20: rrect(d, 440, y + 50, 440 + max(bw, 60), y + 110, 30, rgba(ACC, a))
        text_l(d, 440, y + 132, kwl, 40, rgba(WHITE, a), BLACK)
        text_r(d, 1380, y + 142, note, 26, rgba(MUTED, a))

def vis_ac_dc_path(d, lt, t, dur):
    def row(y, a, station, car_conv, rate, col):
        pylon(d, 140, y, 0.8, MUTED, a)
        x_station = 420
        if station:
            rrect(d, x_station - 90, y - 90, x_station + 90, y + 90, 16, rgba(PANEL, a), rgba(col, a), 4)
            text_c(d, x_station, y - 78, "STATION", 22, rgba(WHITE, a), BLACK)
            text_c(d, x_station, y + 22, "AC → DC", 30, rgba(col, a), BLACK)
        # car outline box
        rrect(d, 640, y - 110, 1420, y + 110, 24, rgba(PANEL, 0.6 * a), rgba(MUTED, a), 3)
        text_l(d, 660, y - 100, "CAR", 22, rgba(MUTED, a), BLACK)
        rrect(d, 760, y - 74, 980, y + 74, 14, rgba(DARK if not car_conv else mix(PANEL, AIR, 0.5), a), rgba(AIR if car_conv else DARK, a), 3)
        text_c(d, 870, y - 66, "ONBOARD", 22, rgba(WHITE if car_conv else MUTED, a), BLACK)
        text_c(d, 870, y - 40, "CHARGER", 22, rgba(WHITE if car_conv else MUTED, a), BLACK)
        text_c(d, 870, y + 16, "AC → DC" if car_conv else "bypassed", 22, rgba(AIR if car_conv else MUTED, a), BLACK)
        battery_icon(d, 1110, y - 50, 220, 100, 0.6, ACC, a)
        if car_conv:
            path = [(200, y), (760, y), (980, y), (1110, y)]
        else:
            path = [(200, y), (x_station - 90, y), (x_station + 90, y), (700, y), (720, y + 85), (1020, y + 85), (1040, y), (1110, y)]
        line(d, path, rgba(col, 0.35 * a), 10)
        flow(d, path, t, col, a, n=8, r=8, speed=0.35 if car_conv else 0.7)
        label_pill(d, 420 if car_conv else 1230, y + 112 if not car_conv else y + 70, rate, col, a, 24)
    a = appear(lt, 0)
    text_l(d, 60, 20, "AC (LEVEL 1 & 2)", 30, rgba(AIR, a), BLACK)
    row(190, a, False, True, "≤ ~19 kW", AIR)
    b = appear(lt, dur * 0.45)
    if b > 0:
        text_l(d, 60, 360, "DC FAST CHARGING", 30, rgba(ACC, b), BLACK)
        row(530, b, True, False, "50–350+ kW", ACC)

def vis_charge_curve(d, lt, t, dur):
    a = appear(lt, 0)
    panel(d, 60, 40, 1440, 680, a)
    X0, Y0, X1, Y1 = 170, 110, 1370, 590
    chart_axes(d, X0, Y0, X1, Y1, "BATTERY CHARGE (%)", "CHARGING POWER", a)
    for v in (0, 20, 50, 80, 100):
        x = X0 + (X1 - X0) * v / 100
        text_c(d, x, Y1 + 50, f"{v}", 22, rgba(MUTED, a))
    sweet = appear(lt, dur * 0.6)
    if sweet > 0:
        xa, xb = X0 + (X1 - X0) * 0.2, X0 + (X1 - X0) * 0.8
        rrect(d, xa, Y0, xb, Y1, 10, rgba(ACC, 0.10 * sweet))
        text_c(d, (xa + xb) / 2, Y0 + 10, "ROAD-TRIP SWEET SPOT  20 → 80%", 26, rgba(ACC, sweet), BLACK)
    def pw(s):
        if s < 0.08: return 0.55 + 0.45 * s / 0.08
        if s < 0.5: return 1.0 - 0.15 * (s - 0.08) / 0.42
        if s < 0.8: return 0.85 - 0.4 * (s - 0.5) / 0.3
        return 0.45 - 0.35 * (s - 0.8) / 0.2
    k = ease_inout((lt - 0.3) / (dur * 0.5))
    pts = [(X0 + (X1 - X0) * i / 100, Y1 - (Y1 - Y0 - 60) * pw(i / 100)) for i in range(101)]
    glow_line(d, partial(pts, k), ACC, a, 7)
    b = appear(lt, dur * 0.35)
    if b > 0:
        x80 = X0 + (X1 - X0) * 0.8
        line(d, [(x80, Y0 + 60), (x80, Y1)], rgba(ACC2, b), 3)
        label_pill(d, x80 + 140, 230, "SLOWS DOWN", ACC2, b, 24)
    text_r(d, 1420, 52, "typical shape · varies by car", 18, rgba(MUTED, a))

# ======================= OUTRO =======================
def vis_flow_recap(d, lt, t, dur):
    order = ["port", "charger", "battery", "bms", "inverter", "motor"]
    labs = {"port": "PLUG", "charger": "CHARGER", "battery": "CELLS", "bms": "BMS", "inverter": "INVERTER", "motor": "MOTOR + GEAR"}
    step = dur * 0.8 / (len(order) + 1)
    n_on = int(clamp(lt / step, 0, len(order)))
    hl = tuple(order[:n_on])
    car_xray(d, 1, t=t, highlight=hl, dim=0.25)
    pos = {"port": (1210, 150), "charger": (1150, 240), "battery": (750, 600), "bms": (480, 600) , "inverter": (930, 150), "motor": (1300, 600)}
    for i, n in enumerate(order[:n_on]):
        a = appear(lt, i * step)
        cx, cy = comp_center(n); lx, ly = pos[n]
        line(d, [(cx, cy), (lx, ly + (0 if ly > cy else 40))], rgba(ACC, 0.6 * a), 3)
        label_pill(d, lx, ly - (0 if ly > cy else 10), labs[n], ACC, a, 22)
    if n_on >= len(order):
        path = [comp_center("port"), comp_center("charger"), (1100, 470), (1030, 481), (520, 481), comp_center("bms"), (700, 420), comp_center("inverter"), comp_center("motor"), WHEELS[1]]
        flow(d, path, t, ACC, 1, n=9, r=8, speed=0.25)
    r = appear(lt, dur * 0.88)
    if r > 0:
        arrow(d, 1090, 600, 760, 600, ACC, 6, r, 24)
        text_c(d, 925, 640, "regen sends some back", 22, rgba(ACC, r), BLACK)

def vis_efficiency(d, lt, t, dur):
    a = appear(lt, 0)
    panel(d, 200, 40, 1300, 680, a)
    text_c(d, CX, 64, "ENERGY THAT ENDS UP MOVING THE CAR", 30, rgba(WHITE, a), BLACK)
    k = ease_inout((lt - 0.5) / 2.2)
    rows = [("ELECTRIC CAR", 0.89, "87–91%", ACC), ("GASOLINE CAR", 0.30, "~30%", ACC2)]
    for i, (lab, v, s, col) in enumerate(rows):
        y = 180 + i * 220
        text_l(d, 260, y, lab, 32, rgba(col, a), BLACK)
        rrect(d, 260, y + 60, 1240, y + 140, 40, rgba(DARK, a))
        bw = 980 * v * k
        if bw > 40: rrect(d, 260, y + 60, 260 + bw, y + 140, 40, rgba(col, a))
        text_r(d, 1240, y, s if k > 0.95 else f"{int(v * 100 * k)}%", 40, rgba(WHITE, a), BLACK)
    text_c(d, CX, 620, "U.S. Department of Energy · EV figure includes regenerative braking", 22, rgba(MUTED, a))

def vis_question(d, lt, t, dur):
    q = pop(lt, 0.1)
    text_c(d, CX, 40, "WHAT WILL CHANGE THE MOST", 50, rgba(WHITE, clamp(q)), BLACK)
    text_c(d, CX, 110, "IN THE NEXT 10 YEARS?", 50, rgba(ACC, clamp(q)), BLACK)
    opts = [("THE BATTERY", "battery"), ("THE MOTOR", "motor"), ("THE SOFTWARE", "soft")]
    for i, (s, kind) in enumerate(opts):
        k = pop(lt, 0.8 + i * 0.6)
        if k <= 0: continue
        a = clamp(k); x = 300 + i * 450; y = 260
        g = 0.5 + 0.5 * math.sin(t * 3 + i * 2)
        panel(d, x - 180, y, x + 180, y + 330, a)
        if kind == "battery": battery_icon(d, x - 90, y + 70, 170, 90, 0.7, ACC, a)
        elif kind == "motor": gear(d, x, y + 115, 60, 12, t * 0.8, ACC, a)
        else:
            rrect(d, x - 90, y + 50, x + 90, y + 180, 14, rgba(PANEL, a), rgba(ACC, a), 4)
            text_c(d, x, y + 88, "</>", 46, rgba(ACC, a), BLACK)
        text_c(d, x, y + 230, s, 32, rgba(WHITE, a), BLACK)
        rrect(d, x - 180, y, x + 180, y + 330, 28, None, rgba(ACC, 0.3 * g * a), 3)
    c = appear(lt, dur * 0.7)
    if c > 0: text_c(d, CX, 640, "TELL ME IN THE COMMENTS", 34, rgba(ACC, c), BLACK)

def vis_endcard(d, lt, t, dur):
    k = pop(lt, 0.1)
    bolt(d, CX, 190, 1.6 * clamp(k), rgba(ACC, clamp(k)))
    text_c(d, CX, 330, "EV DRIVE", 130, rgba(WHITE, clamp(k)), BLACK)
    b = appear(lt, 0.8)
    g = 0.5 + 0.5 * math.sin(t * 3)
    rrect(d, CX - 230, 580, CX + 230, 680, 50, rgba(ACC, b))
    rrect(d, CX - 238, 572, CX + 238, 688, 58, None, rgba(ACC, 0.4 * g * b), 4)
    text_c(d, CX, 606, "SUBSCRIBE", 46, rgba(BG, b), BLACK)
    text_c(d, CX, 510, "a new car tech explainer every day", 28, rgba(MUTED, b))

VIS.update({k[4:]: v for k, v in list(globals().items()) if k.startswith("vis_") and callable(v)})
