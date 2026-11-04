# Visuals for "How Self-Driving Cars Actually Work" — runs inside tools/render_long2.py globals.
# Logical canvas 1500 x 720. Every vis_*(d, lt, t, dur).
import random

CX = 750
ROADC = (28, 33, 42); WALK = (38, 45, 56); CURB = (70, 80, 96); YEL = (235, 196, 70)
RED = (255, 84, 84); BLUE = (110, 190, 255); CAMC = (120, 200, 255); LIDC = ACC; RADC = ACC2
CHILD = (255, 214, 102); BALLC = (255, 96, 96)

def appear(lt, at, dur=0.45): return ease_out((lt - at) / dur)
def pop(lt, at, dur=0.5): return clamp(back_out((lt - at) / dur), 0, 1.15)
def label_pill(d, x, y, s, col, a=1.0, size=28, fg=None, name=BLACK):
    f = FL(name, size); tw = d.textlength(s, font=f) / S / CAM[0]
    rrect(d, x - tw / 2 - 20, y, x + tw / 2 + 20, y + size + 22, (size + 22) / 2, rgba(col, a))
    text_c(d, x, y + 9, s, size, rgba(fg or BG, a), name)
def big_text(d, x, y, s, size, col, a=1.0):
    text_c(d, x + 4, y + 6, s, size, rgba((0, 0, 0), 0.5 * a), BLACK)
    text_c(d, x, y, s, size, rgba(col, a), BLACK)

# ======================= top-down street =======================
ROAD_Y0, ROAD_Y1 = 230, 520            # driving lanes
CENTER_Y = 375
EGO_Y = 447
PARK_Y0, PARK_Y1 = 520, 595
def draw_street(d, scroll, a=1.0, crosswalk_wx=None, wet=0.0):
    rrect(d, -400, 120, 1900, 230, 0, rgba(WALK, a))
    rrect(d, -400, 595, 1900, 720, 0, rgba(WALK, a))
    rrect(d, -400, 230, 1900, 595, 0, rgba(mix(ROADC, (20, 30, 44), wet), a))
    line(d, [(-400, 230), (1900, 230)], rgba(CURB, a), 6)
    line(d, [(-400, 595), (1900, 595)], rgba(CURB, a), 6)
    line(d, [(-400, CENTER_Y - 5), (1900, CENTER_Y - 5)], rgba(YEL, a), 4)
    line(d, [(-400, CENTER_Y + 5), (1900, CENTER_Y + 5)], rgba(YEL, a), 4)
    # parking lane edge dashes (move with scroll)
    off = scroll % 120
    for k in range(-4, 18):
        x = k * 120 - off
        line(d, [(x, PARK_Y0), (x + 60, PARK_Y0)], rgba((150, 158, 170), 0.6 * a), 4)
    # sidewalk tiles
    for k in range(-4, 30):
        x = k * 90 - (scroll % 90)
        line(d, [(x, 120), (x, 230)], rgba((48, 56, 68), a), 2); line(d, [(x, 595), (x, 720)], rgba((48, 56, 68), a), 2)
    if crosswalk_wx is not None:
        x = crosswalk_wx - scroll
        for k in range(9):
            y = 240 + k * 31
            rrect(d, x, y, x + 70, y + 18, 3, rgba((210, 214, 222), 0.85 * a))

def topcar(d, x, y, col, facing=1, L=150, Wd=68, a=1.0, glass=None):
    rrect(d, x - L / 2 + 6, y - Wd / 2 + 10, x + L / 2 + 6, y + Wd / 2 + 10, 20, rgba((0, 0, 0), 0.35 * a))
    rrect(d, x - L / 2, y - Wd / 2, x + L / 2, y + Wd / 2, 20, rgba(col, a))
    g = rgba(glass or (16, 20, 28), a)
    fx = x + facing * L * 0.18
    poly(d, [(fx, y - Wd * 0.38), (fx + facing * L * 0.16, y - Wd * 0.3), (fx + facing * L * 0.16, y + Wd * 0.3), (fx, y + Wd * 0.38)], g)
    rx = x - facing * L * 0.3
    poly(d, [(rx, y - Wd * 0.34), (rx - facing * L * 0.08, y - Wd * 0.3), (rx - facing * L * 0.08, y + Wd * 0.3), (rx, y + Wd * 0.34)], g)
    hx = x + facing * (L / 2 - 6)
    circle(d, hx, y - Wd * 0.33, 6, rgba((255, 244, 200), a)); circle(d, hx, y + Wd * 0.33, 6, rgba((255, 244, 200), a))

def ego_top(d, x, y, a=1.0, scale=1.0, brake=0.0):
    L, Wd = 160 * scale, 72 * scale
    topcar(d, x, y, WHITE, 1, L, Wd, a)
    circle(d, x - 8 * scale, y, 14 * scale, rgba(PANEL, a)); circle(d, x - 8 * scale, y, 9 * scale, rgba(ACC, a))
    if brake > 0:
        rx = x - L / 2 + 4
        rrect(d, rx - 4, y - Wd * 0.45, rx + 6, y - Wd * 0.18, 3, rgba(RED, brake * a))
        rrect(d, rx - 4, y + Wd * 0.18, rx + 6, y + Wd * 0.45, 3, rgba(RED, brake * a))
        circle(d, rx, y - Wd * 0.32, 22, rgba(RED, 0.25 * brake * a)); circle(d, rx, y + Wd * 0.32, 22, rgba(RED, 0.25 * brake * a))

def person_top(d, x, y, col, a=1.0, s=1.0, t=0.0, walking=True):
    sw = math.sin(t * 9) * 6 * s if walking else 0
    rrect(d, x - 16 * s, y - 10 * s + sw, x - 2 * s, y + 10 * s + sw, 6 * s, rgba(mix(col, BG, 0.3), a))
    rrect(d, x + 2 * s, y - 10 * s - sw, x + 16 * s, y + 10 * s - sw, 6 * s, rgba(mix(col, BG, 0.3), a))
    rrect(d, x - 20 * s, y - 13 * s, x + 20 * s, y + 13 * s, 12 * s, rgba(col, a))
    circle(d, x, y, 10 * s, rgba(mix(col, (60, 40, 30), 0.5), a))

def bike_top(d, x, y, col, a=1.0, t=0.0):
    line(d, [(x - 44, y), (x + 44, y)], rgba((60, 66, 76), a), 8)
    rrect(d, x - 52, y - 5, x - 34, y + 5, 4, rgba((20, 22, 26), a)); rrect(d, x + 34, y - 5, x + 52, y + 5, 4, rgba((20, 22, 26), a))
    line(d, [(x + 24, y - 16), (x + 24, y + 16)], rgba((150, 158, 170), a), 5)
    person_top(d, x - 4, y, col, a, 0.9, t, walking=False)

def ball_top(d, x, y, a=1.0, r=16, spin=0.0):
    circle(d, x + 4, y + 6, r, rgba((0, 0, 0), 0.35 * a))
    circle(d, x, y, r, rgba(BALLC, a))
    line(d, [(x + math.cos(spin) * r, y + math.sin(spin) * r), (x - math.cos(spin) * r, y - math.sin(spin) * r)], rgba(WHITE, a), 4)

def bbox(d, x0, y0, x1, y1, lab, col, a=1.0, size=22, conf=None):
    k = 18
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        line(d, [(cx, cy + sy * k), (cx, cy), (cx + sx * k, cy)], rgba(col, a), 4)
    rrect(d, x0, y0, x1, y1, 4, rgba(col, 0.07 * a))
    s = lab if conf is None else f"{lab} {conf}%"
    f = FL(BLACK, size); tw = d.textlength(s, font=f) / S / CAM[0]
    rrect(d, x0, y0 - size - 16, x0 + tw + 20, y0 - 4, 6, rgba(col, a))
    text_l(d, x0 + 10, y0 - size - 12, s, size, rgba(BG, a), BLACK)

def lidar_sweep(d, x, y, t, a=1.0, R=900, speed=3.2):
    ang = t * speed
    for k in range(14):
        aa = ang - k * 0.035
        poly(d, [(x, y), (x + math.cos(aa) * R, y + math.sin(aa) * R), (x + math.cos(aa - 0.04) * R, y + math.sin(aa - 0.04) * R)], rgba(ACC, 0.10 * a * (1 - k / 14)))
    line(d, [(x, y), (x + math.cos(ang) * R, y + math.sin(ang) * R)], rgba(ACC, 0.7 * a), 3)
    return ang

def lidar_points_box(d, x0, y0, x1, y1, x, y, ang, a=1.0, n=26, col=LIDC):
    """dots on the box edges facing the sensor, fading by time since sweep passed"""
    pts = []
    for i in range(n):
        u = i / (n - 1)
        pts += [(lerp(x0, x1, u), y0), (lerp(x0, x1, u), y1)]
    for i in range(n // 2):
        u = i / (n // 2 - 1)
        pts += [(x0, lerp(y0, y1, u)), (x1, lerp(y0, y1, u))]
    for (px, py) in pts:
        pa = math.atan2(py - y, px - x)
        since = (ang - pa) % (2 * math.pi)
        vis = max(0.0, 1 - since / (2 * math.pi)) ** 0.6
        if vis > 0.05:
            circle(d, px, py, 3.4, rgba(col, a * vis))

def ground_rings(d, x, y, ang, a=1.0, col=LIDC):
    for r in range(110, 900, 85):
        n = int(r * 0.12)
        for i in range(n):
            pa = i / n * 2 * math.pi
            px, py = x + math.cos(pa) * r, y + math.sin(pa) * r * 0.98
            since = (ang - pa) % (2 * math.pi)
            vis = max(0.0, 1 - since / (2 * math.pi))
            if vis > 0.1 and -50 < px < 1550 and 100 < py < 740:
                circle(d, px, py, 2.2, rgba(col, 0.45 * a * vis))

def cam_cone(d, x, y, a=1.0, ang=0.0, spread=0.42, R=900, col=CAMC):
    poly(d, [(x + 70, y), (x + 70 + math.cos(ang - spread) * R, y + math.sin(ang - spread) * R), (x + 70 + math.cos(ang + spread) * R, y + math.sin(ang + spread) * R)], rgba(col, 0.10 * a))
    line(d, [(x + 70, y), (x + 70 + math.cos(ang - spread) * R, y + math.sin(ang - spread) * R)], rgba(col, 0.5 * a), 2)
    line(d, [(x + 70, y), (x + 70 + math.cos(ang + spread) * R, y + math.sin(ang + spread) * R)], rgba(col, 0.5 * a), 2)

def radar_waves(d, x, y, t, a=1.0, n=4, col=RADC, spread=50, R=820):
    for i in range(n):
        ph = (t * 0.9 + i / n) % 1.0
        r = 60 + ph * R
        arc(d, x + 70, y, r, -spread, spread, rgba(col, a * (1 - ph) * 0.8), 6)

def dashed_path(d, pts, col, a=1.0, w=6, dash=0.06, gap=0.04, t=0.0):
    u = -(t * 0.3) % (dash + gap)
    while u < 1:
        seg = partial(pts, min(1, u + dash))
        st = partial(pts, max(0, u))
        if len(seg) >= 2 and u + dash > 0:
            p0 = st[-1] if st else pts[0]
            sub = [p0] + [q for q in seg if True][len(st):]
            if len(sub) >= 2: line(d, sub, rgba(col, a), w)
        u += dash + gap

def warn_pulse(d, x, y, t, a=1.0, col=RED):
    ph = (t * 1.6) % 1
    circle(d, x, y, 30 + 70 * ph, None, rgba(col, a * (1 - ph)), 5)

# ---- cold-open world (shared by cold_* and replay) ----
PARKED = [(-300, (90, 98, 112)), (-120, (120, 60, 60)), (60, (70, 90, 120)), (240, (110, 110, 120)), (430, (60, 90, 80)),
          (620, (130, 120, 90)), (800, (90, 70, 110)), (980, (80, 100, 130)), (1460, (120, 80, 60)), (1650, (90, 98, 112)),
          (1840, (100, 110, 90)), (2030, (120, 60, 60)), (2220, (70, 90, 120))]
GAP_WX = 1250  # gap between parked cars where the ball comes out
def world(d, scroll, t, a=1.0, crosswalk=True, wet=0.0, oncoming=True):
    draw_street(d, scroll, a, crosswalk_wx=1700 if crosswalk else None, wet=wet)
    for wx, col in PARKED:
        x = wx - scroll
        while x < -300: x += 2520
        topcar(d, x, (PARK_Y0 + PARK_Y1) / 2, col, 1, 150, 62, a)
    if oncoming:
        ox = 1700 - ((t * 420) % 2600)
        topcar(d, ox, 302, (80, 110, 150), -1, 150, 68, a)
    # pedestrians on top sidewalk
    for k, base in enumerate((200, 900, 1450)):
        px = (base - scroll * 0.0 - t * 35 * (1 if k % 2 else -1)) % 1800 - 150
        person_top(d, px, 175 + 18 * (k % 2), (150, 170, 210) if k != 1 else (210, 160, 140), a, 1.0, t + k)

def cold_state(lt, total=6.0):
    """ego scroll and the ball/child positions for the cold-open timeline"""
    v = 150  # px/s ego speed
    scroll = lt * v
    ball_t = lt - 1.2
    bx = GAP_WX - scroll + 0
    by = PARK_Y1 + 40 - max(0, ball_t) * 120
    child_t = lt - 2.4
    cy = PARK_Y1 + 70 - max(0, child_t) * 60
    return scroll, (bx, by, ball_t), (bx - 40, cy, child_t)

def vis_cold_ball(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (1.6, 1.0, 750, 380), (dur, 1.35, 820, 450)])
    scroll, (bx, by, btt), (cx_, cy_, ctt) = cold_state(lt)
    world(d, scroll, t)
    ego_top(d, 330, EGO_Y)
    if btt > 0:
        ball_top(d, bx, max(by, 330), 1, 18, t * 8)
        if btt > 0.3: warn_pulse(d, bx, max(by, 330), t, 1, RED)
    if ctt > 0:
        person_top(d, cx_, max(cy_, 470), CHILD, 1, 1.0, t)
        label_pill(d, cx_ + 90, max(cy_, 470) - 20, "CHILD", CHILD, appear(lt, 2.6), 22)

def vis_cold_react(d, lt, t, dur):
    lt0 = lt + 4.2
    scroll, (bx, by, _), (cx_, cy_, _) = cold_state(min(lt0, 4.4))
    cam(1.25, 760, 430)
    world(d, scroll, t, 0.55)
    ego_top(d, 330, EGO_Y)
    ball_top(d, bx, max(by, 330), 1, 18, 0)
    person_top(d, cx_, max(cy_, 470), CHILD, 1, 1.0, 0, walking=False)
    # reaction timer & distance tape
    k = ease_inout((lt - 0.4) / (dur * 0.55))
    sec = 1.5 * k
    tape_len = 560 * k
    y = EGO_Y
    rrect(d, 412, y - 10, 412 + tape_len, y + 10, 10, rgba(RED, 0.85))
    for i in range(int(tape_len // 56)):
        line(d, [(412 + i * 56, y - 18), (412 + i * 56, y + 18)], rgba(WHITE, 0.8), 3)
    panel(d, 380, 140, 760, 300, 1)
    text_c(d, 570, 152, "HUMAN REACTION", 26, rgba(MUTED), BLACK)
    big_text(d, 570, 190, f"{sec:.1f} s", 80, WHITE)
    panel(d, 800, 140, 1180, 300, appear(lt, 1.0))
    text_c(d, 990, 152, "AT 30 MPH", 26, rgba(MUTED, appear(lt, 1.0)), BLACK)
    big_text(d, 990, 190, f"{int(66 * k)} ft", 80, RED, appear(lt, 1.0))
    if k >= 1:
        label_pill(d, 412 + tape_len / 2, y + 30, "BEFORE YOUR FOOT HITS THE BRAKE", RED, appear(lt, dur * 0.7), 22, WHITE)

def vis_cold_questions(d, lt, t, dur):
    scroll, (bx, by, _), (cx_, cy_, _) = cold_state(4.4)
    cam(1.0 + 0.04 * lt / dur, 750, 360)
    world(d, scroll, t, 0.25)
    ego_top(d, 330, EGO_Y, 0.5)
    qs = [("WHAT IS AROUND ME?", CAMC), ("WHAT WILL IT DO NEXT?", ACC2), ("WHAT SHOULD I DO?", ACC)]
    for i, (q, col) in enumerate(qs):
        k = pop(lt, dur * 0.35 + i * dur * 0.15)
        if k <= 0: continue
        y = 170 + i * 150
        rrect(d, 300, y, 1200, y + 110, 55, rgba(PANEL, clamp(k)), rgba(col, clamp(k)), 4)
        circle(d, 360, y + 55, 34, rgba(col, clamp(k)))
        text_c(d, 360, y + 32, str(i + 1), 40, rgba(BG, clamp(k)), BLACK)
        text_l(d, 420, y + 28, q, 46, rgba(WHITE, clamp(k)), BLACK)
    a = appear(lt, dur * 0.12)
    # loop indicator
    ang = t * 6
    arc(d, 1330, 110, 46, math.degrees(ang), math.degrees(ang) + 280, rgba(ACC, a), 8)
    text_c(d, 1330, 170, "MANY TIMES", 20, rgba(MUTED, a), BLACK); text_c(d, 1330, 196, "PER SECOND", 20, rgba(MUTED, a), BLACK)

def vis_cold_promise(d, lt, t, dur):
    cam(1.0 + 0.05 * clamp(lt / dur), 750, 360)
    k = pop(lt, 0.2)
    big_text(d, CX, 80, "HOW A ROBOT CAR DECIDES", 70, WHITE, clamp(k))
    words = [("SEE", CAMC), ("PREDICT", ACC2), ("PLAN", ACC)]
    for i, (w_, col) in enumerate(words):
        kk = pop(lt, 1.0 + i * 0.45)
        if kk <= 0: continue
        x = 350 + i * 400
        circle(d, x, 330, 110 * clamp(kk), rgba(col, 0.15 * clamp(kk)))
        circle(d, x, 330, 86 * clamp(kk), None, rgba(col, clamp(kk)), 6)
        text_c(d, x, 306, w_, 44, rgba(col, clamp(kk)), BLACK)
        if i < 2: arrow(d, x + 120, 330, x + 280, 330, MUTED, 6, clamp(kk), 22)
    b = appear(lt, dur * 0.55)
    if b > 0:
        rrect(d, 360, 520, 1140, 620, 50, rgba(PANEL, b), rgba(RED, b), 3)
        text_c(d, CX, 545, "WHY 99.9% ISN'T GOOD ENOUGH", 40, rgba(RED, b), BLACK)

# ======================= 01 LEVELS =======================
LV = [("0", "NO AUTOMATION", "you do everything"), ("1", "DRIVER ASSIST", "steering OR speed"), ("2", "PARTIAL", "steer + speed, you watch"),
      ("3", "CONDITIONAL", "eyes off, take over on request"), ("4", "HIGH", "no driver in a set area"), ("5", "FULL", "anywhere, anytime")]
LVCOL = [MUTED, MUTED, CAMC, ACC2, ACC, (200, 140, 255)]
def ladder(d, lt, hi=(), dim=0.25, t=0.0, build=True, sub=True):
    for i, (n, name, desc) in enumerate(LV):
        k = pop(lt, 0.15 + i * 0.22) if build else 1
        if k <= 0: continue
        a = clamp(k) * (1.0 if (not hi or i in hi) else dim)
        x0 = 90 + i * 225; h = 150 + i * 72
        y1 = 640; y0 = y1 - h
        col = LVCOL[i]
        rrect(d, x0 + 6, y0 + 10, x0 + 205, y1 + 10, 18, rgba((0, 0, 0), 0.3 * a))
        rrect(d, x0, y0, x0 + 205, y1, 18, rgba(mix(PANEL, col, 0.25 if i in hi else 0.1), a), rgba(col, a), 3)
        text_c(d, x0 + 102, y0 + 10, n, 70, rgba(col, a), BLACK)
        text_c(d, x0 + 102, y0 + 100, name, 20, rgba(WHITE, a), BLACK)
        if sub and h > 190:
            text_c(d, x0 + 102, y0 + 132, desc if len(desc) < 22 else desc[:22], 15, rgba(MUTED, a), BOLD)
        if i in hi:
            g = 0.5 + 0.5 * math.sin(t * 4)
            rrect(d, x0 - 6, y0 - 6, x0 + 211, y1 + 6, 22, None, rgba(col, 0.4 + 0.4 * g), 4)

def vis_levels_ladder(d, lt, t, dur):
    cam_path(lt, [(0, 1.15, 750, 460), (dur, 1.0, 750, 360)])
    ladder(d, lt, (), t=t)
    a = appear(lt, dur * 0.4)
    big_text(d, CX, 30, "SAE LEVELS OF DRIVING AUTOMATION", 44, WHITE, a)

def vis_levels_low(d, lt, t, dur):
    seg = dur / 3
    hi = (0,) if lt < seg else (1,) if lt < 2 * seg else (2,)
    cam_path(lt, [(0, 1.0, 750, 360), (seg * 2, 1.0, 750, 360), (dur, 1.25, 560, 420)])
    ladder(d, 9, hi, 0.25, t, build=False)
    a = appear(lt, 2 * seg)
    if a > 0:
        rrect(d, 450, 40, 1010, 150, 24, rgba(PANEL, a), rgba(CAMC, a), 3)
        text_c(d, 730, 58, "LEVEL 2: EYES ON THE ROAD", 32, rgba(CAMC, a), BLACK)
        text_c(d, 730, 104, "e.g. Tesla Autopilot", 24, rgba(MUTED, a))

def vis_levels_l3(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur * 0.3, 1.25, 820, 420)])
    ladder(d, 9, (3,), 0.25, t, build=False)
    cam()
    a = appear(lt, dur * 0.25)
    if a > 0:
        rrect(d, 300, 40, 1160, 190, 24, rgba(PANEL, a), rgba(ACC2, a), 3)
        text_c(d, 730, 56, "LEVEL 3: EYES OFF… UNTIL IT ASKS", 30, rgba(ACC2, a), BLACK)
        cnt = max(3, 10 - int((lt - dur * 0.35) * 1.2)) if lt > dur * 0.35 else 10
        text_c(d, 730, 104, f"TAKE OVER IN {cnt} s" if lt > dur * 0.35 else "car drives in set conditions", 30, rgba(WHITE, a), BLACK)
    b = appear(lt, dur * 0.65)
    if b > 0:
        label_pill(d, 730, 640, "MERCEDES DRIVE PILOT · UP TO 95 KM/H ON GERMAN HIGHWAYS", ACC2, b, 22)

def vis_levels_l45(d, lt, t, dur):
    half = dur * 0.6
    if lt < half:
        cam_path(lt, [(0, 1.0, 750, 360), (1.0, 1.0, 750, 360)])
        a = appear(lt, 0)
        # geofence map with robotaxi
        pts = [(380, 120), (980, 90), (1160, 300), (1000, 610), (420, 620), (300, 360)]
        poly(d, pts, rgba(ACC, 0.08 * a)); line(d, pts + [pts[0]], rgba(ACC, a), 5)
        for k in range(6):
            line(d, [(300, 140 + k * 95), (1200, 140 + k * 95)], rgba(DARK, a), 3)
            line(d, [(360 + k * 160, 80), (360 + k * 160, 640)], rgba(DARK, a), 3)
        route = [(460, 520), (460, 235), (840, 235), (840, 520), (1000, 520), (1000, 330)]
        u = (lt * 0.12) % 1
        px, py = path_point(route, u)
        circle(d, px, py, 26, rgba(ACC, a)); circle(d, px, py, 12, rgba(BG, a))
        label_pill(d, 730, 30, "LEVEL 4 · ROBOTAXI INSIDE ITS ZONE", ACC, a, 26)
        text_c(d, 1250, 620, "outside = not allowed", 22, rgba(MUTED, a))
    else:
        lt2 = lt - half
        k = pop(lt2, 0.1)
        circle(d, CX, 330, 190 * clamp(k), None, rgba((200, 140, 255), clamp(k)), 6)
        arc(d, CX, 330, 190 * clamp(k), 0, 360, rgba((200, 140, 255), 0.3), 2)
        for j in range(-2, 3):
            arc(d, CX, 330 + 0, 190 * clamp(k), 0, 360, rgba((200, 140, 255), 0.0), 1)
        line(d, [(CX - 190, 330), (CX + 190, 330)], rgba((200, 140, 255), 0.5 * clamp(k)), 3)
        line(d, [(CX, 140), (CX, 520)], rgba((200, 140, 255), 0.5 * clamp(k)), 3)
        big_text(d, CX, 250, "?", 140, WHITE, clamp(k))
        b = appear(lt2, 0.6)
        label_pill(d, CX, 560, "LEVEL 5 · DOESN'T EXIST YET", (200, 140, 255), b, 30)

# ======================= 02 SENSORS =======================
def vis_suite(d, lt, t, dur):
    cam_path(lt, [(0, 1.7, 750, 360), (dur * 0.45, 1.5, 750, 360), (dur, 1.05, 750, 340)])
    a = appear(lt, 0)
    k = ease_out((lt - 0.5) / 3.0)
    # coverage rings
    for i, (col, R, sp) in enumerate([(CAMC, 520, 0.9), (LIDC, 600, 1.0), (RADC, 680, 1.1)]):
        rr = R * k
        if rr > 10:
            circle(d, CX, 360, rr, rgba(col, 0.05 * a), rgba(col, 0.35 * a), 2)
    ego_top(d, CX, 360, a, 1.6)
    # sensor dots: 13 cams, 4 lidars, 6 radars around the body
    L, Wd = 256, 115
    def around(n, inset, phase=0.0):
        out = []
        for i in range(n):
            ang = phase + i / n * 2 * math.pi
            out.append((CX + math.cos(ang) * (L / 2 + inset), 360 + math.sin(ang) * (Wd / 2 + inset)))
        return out
    groups = [(around(13, -6, 0.1), CAMC, "13 CAMERAS", 1.0), (around(4, -14, 0.78), LIDC, "4 LIDARS", 2.2), (around(6, 2, 0.3), RADC, "6 RADARS", 3.2)]
    for gi, (pts, col, lab, at) in enumerate(groups):
        for j, (x, y) in enumerate(pts):
            kk = pop(lt, at + j * 0.06)
            if kk > 0:
                circle(d, x, y, 9 * clamp(kk), rgba(col, 1)); circle(d, x, y, 16 * clamp(kk), rgba(col, 0.25))
    cam()
    for gi, (pts, col, lab, at) in enumerate(groups):
        label_pill(d, 330 + gi * 420, 640, lab, col, appear(lt, at), 26)
    c = appear(lt, dur * 0.55)
    if c > 0:
        label_pill(d, CX, 20, "SEES UP TO 500 M · OVERLAPPING 360° VIEW", WHITE, c, 24)

def persp_road(d, a=1.0, t=0.0, dark=0.0):
    vx, vy = 750, 250
    # sky & ground
    rrect(d, 0, 0, 1500, vy, 0, rgba(mix((26, 34, 50), (6, 8, 12), dark), a))
    poly(d, [(0, vy), (1500, vy), (1500, 720), (0, 720)], rgba(mix((30, 34, 40), (8, 9, 12), dark), a))
    poly(d, [(vx - 10, vy), (vx + 10, vy), (1350, 720), (150, 720)], rgba(mix((44, 48, 58), (12, 13, 16), dark), a))
    # lane lines (moving dashes)
    for side in (-1, 1):
        line(d, [(vx + side * 8, vy), (750 + side * 600, 720)], rgba(WHITE, a * 0.9), 5)
    for k in range(10):
        u0 = ((k / 10) + t * 0.35) % 1.0
        u1 = min(1, u0 + 0.04)
        def at(u): return (vx + (750 - 750) * u, vy + (720 - vy) * (u ** 2.2))
        y0, y1 = at(u0)[1], at(u1)[1]
        line(d, [(vx, y0), (vx, y1)], rgba(YEL, a), max(2, 2 + 14 * u0))
    return vx, vy

def persp_box(u, side, w_m=1.8, h_m=1.5):
    """object at depth u (0 far .. 1 near), lateral side (-1..1) -> screen rect"""
    vx, vy = 750, 250
    y_ground = vy + (720 - vy) * (u ** 2.2)
    scale = (y_ground - vy) / (720 - vy)
    cxs = vx + side * 600 * scale
    w = 260 * scale * w_m / 1.8; h = 200 * scale * h_m / 1.5
    return cxs - w / 2, y_ground - h, cxs + w / 2, y_ground

def car_rear(d, x0, y0, x1, y1, col, a=1.0, brake=0.0):
    w = x1 - x0; h = y1 - y0
    rrect(d, x0, y0 + h * 0.25, x1, y1, h * 0.12, rgba(col, a))
    poly(d, [(x0 + w * 0.15, y0 + h * 0.27), (x0 + w * 0.25, y0), (x1 - w * 0.25, y0), (x1 - w * 0.15, y0 + h * 0.27)], rgba(mix(col, BG, 0.3), a))
    poly(d, [(x0 + w * 0.22, y0 + h * 0.24), (x0 + w * 0.29, y0 + h * 0.05), (x1 - w * 0.29, y0 + h * 0.05), (x1 - w * 0.22, y0 + h * 0.24)], rgba((18, 22, 30), a))
    for sx in (x0 + w * 0.08, x1 - w * 0.22):
        rrect(d, sx, y0 + h * 0.45, sx + w * 0.14, y0 + h * 0.58, 4, rgba(mix((120, 30, 30), RED, brake), a))
    rrect(d, x0 + w * 0.05, y1 - h * 0.08, x0 + w * 0.2, y1 + h * 0.04, 4, rgba((12, 12, 14), a))
    rrect(d, x1 - w * 0.2, y1 - h * 0.08, x1 - w * 0.05, y1 + h * 0.04, 4, rgba((12, 12, 14), a))

def traffic_light(d, x, y, s, state, a=1.0):
    line(d, [(x, y + 120 * s), (x, y + 360 * s)], rgba((70, 76, 86), a), 8 * s)
    rrect(d, x - 26 * s, y, x + 26 * s, y + 130 * s, 10 * s, rgba((20, 22, 26), a), rgba((60, 64, 72), a), 2)
    for i, c in enumerate([(255, 70, 70), (255, 190, 60), (90, 230, 120)]):
        on = (state == i)
        circle(d, x, y + 22 * s + i * 42 * s, 15 * s, rgba(c if on else mix(c, BG, 0.8), a))
        if on: circle(d, x, y + 22 * s + i * 42 * s, 26 * s, rgba(c, 0.25 * a))

def stop_sign(d, x, y, s, a=1.0):
    line(d, [(x, y), (x, y + 200 * s)], rgba((70, 76, 86), a), 6 * s)
    pts = [(x + math.cos(math.pi / 8 + k * math.pi / 4) * 38 * s, y + math.sin(math.pi / 8 + k * math.pi / 4) * 38 * s) for k in range(8)]
    poly(d, pts, rgba((200, 40, 40), a))
    text_c(d, x, y - 12 * s, "STOP", 20 * s, rgba(WHITE, a), BLACK)

def vis_cam_view(d, lt, t, dur):
    cam_path(lt, [(0, 1.08, 750, 380), (dur, 1.0, 750, 360)])
    dark = ease_inout((lt - dur * 0.68) / 0.8)
    persp_road(d, 1, t, dark)
    bx = persp_box(0.80, 0.0); car_rear(d, *bx, (90, 110, 150), 1)
    bx2 = persp_box(0.62, -0.36); car_rear(d, *bx2, (140, 90, 80), 1)
    traffic_light(d, 1170, 90, 0.9, 0)
    stop_sign(d, 260, 230, 1.0)
    # detections
    dets = [(bx, "CAR", 98, CAMC, 0.6), (bx2, "CAR", 94, CAMC, 1.0), ((1140, 80, 1200, 220), "LIGHT: RED", None, RED, 1.4), ((210, 180, 310, 280), "STOP SIGN", 97, ACC2, 1.8)]
    for (x0, y0, x1, y1), lab, cf, col, at in dets:
        k = appear(lt, at, 0.3) * (1 - 0.6 * dark)
        if k > 0: bbox(d, x0, y0, x1, y1, lab, col, k, 20, cf)
    k = appear(lt, 2.2) * (1 - dark)
    if k > 0:
        line(d, [(742, 250), (150, 720)], rgba(ACC, 0.6 * k), 8); line(d, [(758, 250), (1350, 720)], rgba(ACC, 0.6 * k), 8)
        label_pill(d, 750, 640, "LANE", ACC, k, 20)
    # REC / camera HUD
    rrect(d, 30, 30, 230, 80, 12, rgba(BG, 0.6)); circle(d, 60, 55, 9, rgba(RED, 0.5 + 0.5 * math.sin(t * 5)))
    text_l(d, 80, 40, "CAMERA", 24, rgba(WHITE), BLACK)
    if dark > 0:
        # glare
        circle(d, 1000, 300, 260 * dark, rgba((255, 250, 220), 0.25 * dark)); circle(d, 1000, 300, 120 * dark, rgba((255, 250, 220), 0.5 * dark))
        label_pill(d, 420, 380, "DEPTH?", RED, dark, 30, WHITE)
        label_pill(d, 1000, 470, "GLARE", RED, dark, 30, WHITE)

# ---------- 3D point cloud ----------
_cloud = None
def build_cloud():
    rnd = random.Random(4)
    pts = []
    for r in [3 + i * 2.0 for i in range(18)]:
        n = int(r * 9)
        for i in range(n):
            a = i / n * 2 * math.pi + rnd.uniform(-0.01, 0.01)
            pts.append((math.cos(a) * r, math.sin(a) * r, 0.0, 0))
    def box(cx, cy, L, Wd, H, kind):
        for _ in range(int(L * Wd * 6 + 120)):
            face = rnd.random()
            if face < 0.35: x, y, z = cx + rnd.uniform(-L / 2, L / 2), cy - Wd / 2, rnd.uniform(0.2, H)
            elif face < 0.7: x, y, z = cx + rnd.uniform(-L / 2, L / 2), cy + Wd / 2, rnd.uniform(0.2, H)
            elif face < 0.85: x, y, z = cx - L / 2, cy + rnd.uniform(-Wd / 2, Wd / 2), rnd.uniform(0.2, H)
            else: x, y, z = cx + rnd.uniform(-L / 2, L / 2), cy + rnd.uniform(-Wd / 2, Wd / 2), H
            pts.append((x, y, z, kind))
    box(12, 0, 4.5, 1.9, 1.5, 1)     # car ahead
    box(-10, 3.6, 4.5, 1.9, 1.5, 1)
    box(6, -3.6, 4.6, 1.9, 1.6, 1)
    box(22, -3.6, 4.6, 1.9, 1.5, 1)
    box(9, 6.5, 0.6, 0.6, 1.75, 2)   # pedestrians
    box(17, 7.0, 0.6, 0.6, 1.7, 2)
    box(26, 2.0, 1.8, 0.6, 1.7, 3)   # cyclist
    for x in range(-30, 34, 2):      # building facades
        for z in (0.5, 2, 3.5, 5, 6.5):
            pts.append((x + rnd.uniform(-0.3, 0.3), 11 + rnd.uniform(-0.2, 0.2), z, 4))
            pts.append((x + rnd.uniform(-0.3, 0.3), -11 + rnd.uniform(-0.2, 0.2), z, 4))
    return pts

def project(x, y, z, yaw, camd=26, camh=13, pitch=0.42, F=900):
    cy_, sy = math.cos(yaw), math.sin(yaw)
    xr = x * sy - y * cy_          # right
    yr = x * cy_ + y * sy          # forward
    py = yr + camd; pz = z - camh
    depth = py * math.cos(pitch) - pz * math.sin(pitch)
    up = py * math.sin(pitch) + pz * math.cos(pitch)
    if depth < 1: return None
    return (750 + F * xr / depth, 330 - F * up / depth, depth)

KCOL = {0: (90, 140, 120), 1: ACC, 2: CHILD, 3: ACC2, 4: (90, 120, 170)}
def point_cloud(d, lt, t, a=1.0, yaw0=0.3, spin=0.12, noise=0.0, drop=0.0, sweep=True):
    global _cloud
    if _cloud is None: _cloud = build_cloud()
    yaw = yaw0 + lt * spin
    sw = (t * 3.0) % (2 * math.pi)
    rnd = random.Random(int(t * 10))
    for (x, y, z, kind) in _cloud:
        if drop and rnd.random() < drop: continue
        if noise:
            x += rnd.gauss(0, noise); y += rnd.gauss(0, noise); z += abs(rnd.gauss(0, noise * 0.5))
        pr = project(x, y, z, yaw)
        if not pr: continue
        X, Y, dep = pr
        if not (-20 < X < 1520 and -20 < Y < 740): continue
        vis = 1.0
        if sweep:
            pa = math.atan2(y, x)
            since = (sw - pa) % (2 * math.pi)
            vis = 0.35 + 0.65 * max(0.0, 1 - since / (2 * math.pi))
        col = KCOL[kind] if kind else mix((60, 200, 140), BLUE, min(1, math.hypot(x, y) / 36))
        r = max(1.4, 5.5 - dep * 0.08)
        circle(d, X, Y, r, rgba(col, a * vis))
    # ego car in the middle
    e = project(0, 0, 0.8, yaw)
    if e:
        circle(d, e[0], e[1], 26, rgba(WHITE, a)); circle(d, e[0], e[1], 11, rgba(ACC, a))
    if rnd and noise:
        for _ in range(int(220 * noise)):
            X, Y = rnd.uniform(0, 1500), rnd.uniform(0, 720)
            circle(d, X, Y, 2, rgba((180, 200, 220), 0.5 * a))
    return yaw

def vis_lidar_cloud(d, lt, t, dur):
    cam_path(lt, [(0, 1.25, 750, 360), (dur, 1.0, 750, 360)])
    point_cloud(d, lt, t, appear(lt, 0, 0.8))
    # inset: time of flight
    a = appear(lt, 0.8)
    if a > 0:
        cam()
        panel(d, 40, 40, 560, 230, a)
        text_l(d, 64, 56, "TIME OF FLIGHT", 24, rgba(WHITE, a), BLACK)
        circle(d, 100, 160, 18, rgba(ACC, a))
        rrect(d, 470, 110, 520, 210, 8, rgba(MUTED, a))
        ph = (t * 0.9) % 1
        xx = 120 + (330 * (ph * 2) if ph < 0.5 else 330 * (2 - ph * 2))
        circle(d, 120 + 330 * min(1, ph * 2) if ph < 0.5 else 450 - 330 * (ph * 2 - 1), 160, 9, rgba(RED if ph < 0.5 else ACC, a))
        text_l(d, 64, 196, "distance = time × light speed ÷ 2", 18, rgba(MUTED, a))
    b = appear(lt, dur * 0.55)
    if b > 0:
        cam()
        rrect(d, 920, 600, 1460, 680, 40, rgba(PANEL, b), rgba(ACC, b), 3)
        text_c(d, 1190, 616, "UP TO MILLIONS OF POINTS / SEC", 26, rgba(ACC, b), BLACK)

def rain(d, t, a=1.0, n=160, col=(170, 200, 230), seed=1, ang=0.25):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(-100, 1600); sp = rnd.uniform(900, 1400); ph = rnd.random()
        y = ((t * sp / 720 + ph) % 1.0) * 820 - 60
        x = x0 + y * ang
        line(d, [(x, y), (x + 14 * ang * 2, y + 34)], rgba(col, 0.6 * a), 2)

def vis_lidar_weak(d, lt, t, dur):
    k = ease_inout(lt / (dur * 0.6))
    cam(1.0 + 0.1 * k, 750, 360)
    point_cloud(d, lt + 6, t, 1, noise=0.6 * k, drop=0.45 * k)
    cam()
    rain(d, t, k, 220)
    poly(d, [(0, 0), (1500, 0), (1500, 720), (0, 720)], rgba((150, 165, 185), 0.12 * k))
    label_pill(d, CX, 40, "RAIN · FOG · SNOW SCATTER THE LASER", RED, appear(lt, 0.4), 30, WHITE)

def vis_radar(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.06, 820, 375)])
    scroll = lt * 200
    draw_street(d, scroll, 1, wet=0.6)
    ego_top(d, 300, EGO_Y)
    radar_waves(d, 300, EGO_Y, t, 1, 5, RADC, 38, 1000)
    objs = [(900 - (lt * 40) % 300, EGO_Y, "+3 mph", (90, 110, 150), 1), (1250 - lt * 260 % 1500, 302, "−58 mph", (140, 90, 80), -1)]
    for i, (x, y, sp, col, f) in enumerate(objs):
        topcar(d, x, y, col, f, 150, 66, 0.35)
        # blurry blob
        b = appear(lt, 0.8 + i * 0.6)
        for r, al in ((90, 0.10), (65, 0.16), (40, 0.28)):
            circle(d, x, y, r, rgba(RADC, al * b))
        label_pill(d, x, y - 100, sp, RADC, b, 24)
    rain(d, t, 0.8, 150)
    c = appear(lt, dur * 0.6)
    if c > 0:
        label_pill(d, 380, 640, "SPEED: YES  ·  BAD WEATHER: YES", ACC, c, 24)
        label_pill(d, 1080, 640, "SHAPE: BLURRY", RED, c, 24, WHITE)

def vis_compare(d, lt, t, dur):
    cols = [("CAMERA", CAMC, "WHAT"), ("LIDAR", LIDC, "WHERE"), ("RADAR", RADC, "HOW FAST")]
    rows = ["Color & signs", "Exact depth", "Direct speed", "Bad weather", "Darkness"]
    marks = [[1, 0, 0, 0, 0], [0, 1, 0, 0, 1], [0, 0, 1, 1, 1]]
    a = appear(lt, 0)
    for i, (n, col, big) in enumerate(cols):
        x = 470 + i * 330
        k = pop(lt, 0.2 + i * 0.5)
        if k <= 0: continue
        rrect(d, x - 140, 30, x + 140, 690, 26, rgba(PANEL, clamp(k)), rgba(col, clamp(k)), 3)
        text_c(d, x, 50, n, 30, rgba(col, clamp(k)), BLACK)
        big_text(d, x, 100, big, 44 if len(big) < 6 else 38, WHITE, clamp(k))
        for j, r in enumerate(rows):
            kk = appear(lt, 1.8 + j * 0.25)
            y = 220 + j * 92
            ok = marks[i][j]
            circle(d, x, y + 24, 26, rgba(ACC if ok else (60, 30, 30), kk))
            if ok:
                line(d, [(x - 12, y + 25), (x - 3, y + 35), (x + 14, y + 13)], rgba(BG, kk), 6)
            else:
                line(d, [(x - 10, y + 14), (x + 10, y + 34)], rgba(RED, kk), 6); line(d, [(x + 10, y + 14), (x - 10, y + 34)], rgba(RED, kk), 6)
    for j, r in enumerate(rows):
        kk = appear(lt, 1.8 + j * 0.25)
        text_r(d, 300, 228 + j * 92, r, 24, rgba(WHITE, kk), BOLD)

# ======================= 03 FUSION =======================
def vis_fusion(d, lt, t, dur):
    a = appear(lt, 0)
    srcs = [("CAMERA", CAMC, 0.25, 70), ("LIDAR", LIDC, dur * 0.35, 91), ("RADAR", RADC, dur * 0.55, 98)]
    conf = 0
    for i, (n, col, at, cf) in enumerate(srcs):
        k = appear(lt, at)
        if k <= 0: continue
        y = 110 + i * 200
        panel(d, 60, y, 430, y + 160, k)
        text_l(d, 84, y + 14, n, 26, rgba(col, k), BLACK)
        if i == 0:
            person_top(d, 245, y + 95, CAMC, k, 1.6, t)
            bbox(d, 205, y + 60, 290, y + 132, "PERSON?", CAMC, k, 16)
        elif i == 1:
            rnd = random.Random(3)
            for _ in range(90):
                circle(d, 245 + rnd.gauss(0, 18), y + 95 + rnd.gauss(0, 22), 3, rgba(LIDC, k))
            text_r(d, 410, y + 126, "12.4 m", 22, rgba(WHITE, k), BLACK)
        else:
            for r, al in ((50, 0.12), (34, 0.2), (20, 0.35)):
                circle(d, 245, y + 95, r, rgba(RADC, al * k))
            text_r(d, 410, y + 126, "1.4 m/s →", 22, rgba(WHITE, k), BLACK)
        glow_line(d, [(430, y + 80), (640, y + 80), (760, 360)], col, k * 0.8, 4)
        flow(d, [(430, y + 80), (640, y + 80), (760, 360)], t + i, col, k, 3, 6, 0.7, False)
        if lt > at + 0.4: conf = cf
    # fused result
    b = appear(lt, 0.6)
    rrect(d, 780, 160, 1440, 560, 30, rgba(PANEL, b), rgba(ACC, b), 4)
    text_c(d, 1110, 180, "FUSED OBJECT", 30, rgba(WHITE, b), BLACK)
    person_top(d, 1110, 320, CHILD, b, 2.2, t)
    bbox(d, 1040, 250, 1180, 390, "PEDESTRIAN", ACC, b, 20)
    rrect(d, 840, 450, 1380, 490, 20, rgba(DARK, b))
    cw = 540 * conf / 100
    if cw > 30: rrect(d, 840, 450, 840 + cw, 490, 20, rgba(ACC, b))
    text_c(d, 1110, 500, f"CONFIDENCE {conf}%", 26, rgba(ACC, b), BLACK)
    text_r(d, 1440, 690, "illustrative values", 16, rgba(MUTED, b))

def street_scene_all(d, lt, t, scroll, a=1.0, boxes=0.0, tracks=0.0, cyc=None):
    world(d, scroll, t, a, crosswalk=True)
    ego_top(d, 300, EGO_Y)
    # cyclist ahead in our lane, slower
    cxw = cyc if cyc is not None else 900 - lt * 60
    bike_top(d, cxw, EGO_Y - 10, ACC2, a, t)
    if boxes > 0:
        bbox(d, cxw - 60, EGO_Y - 45, cxw + 60, EGO_Y + 25, "CYCLIST", ACC2, boxes, 18, 96)
        ox = 1700 - ((t * 420) % 2600)
        if -100 < ox < 1600: bbox(d, ox - 82, 262, ox + 82, 342, "CAR", CAMC, boxes, 18, 99)
        for k, base in enumerate((200, 900, 1450)):
            px = (base - t * 35 * (1 if k % 2 else -1)) % 1800 - 150
            if 0 < px < 1500: bbox(d, px - 28, 175 + 18 * (k % 2) - 22, px + 28, 175 + 18 * (k % 2) + 22, "PED", CHILD, boxes, 14)
        for wx, col in PARKED:
            x = wx - scroll
            while x < -300: x += 2520
            if 0 < x < 1500: bbox(d, x - 80, PARK_Y0 + 4, x + 80, PARK_Y1 - 4, "PARKED", MUTED, boxes * 0.7, 14)
    if tracks > 0:
        for j in range(8):
            circle(d, cxw + 24 + j * 22, EGO_Y - 10, 4, rgba(ACC2, tracks * (1 - j / 8)))
    return cxw

def vis_fusion_boxes(d, lt, t, dur):
    cam_path(lt, [(0, 1.3, 760, 420), (dur, 1.0, 750, 380)])
    street_scene_all(d, lt, t, lt * 160, 1, appear(lt, 0.5), appear(lt, dur * 0.5))
    cam()
    label_pill(d, CX, 30, "LIVE 3D MODEL · LABELED · TRACKED", ACC, appear(lt, 1.0), 24)

# ======================= 04 BRAIN =======================
def vis_pipeline(d, lt, t, dur):
    blocks = [("PERCEPTION", "what is around me?", CAMC), ("PREDICTION", "what will it do?", ACC2), ("PLANNING", "what should I do?", ACC)]
    for i, (n, q, col) in enumerate(blocks):
        k = pop(lt, 0.3 + i * dur * 0.18)
        if k <= 0: continue
        x = 280 + i * 470; a = clamp(k)
        rrect(d, x - 190, 170, x + 190, 430, 30, rgba(PANEL, a), rgba(col, a), 4)
        circle(d, x, 250, 50, rgba(col, 0.2 * a)); text_c(d, x, 222, str(i + 1), 50, rgba(col, a), BLACK)
        text_c(d, x, 320, n, 34, rgba(WHITE, a), BLACK)
        text_c(d, x, 370, q, 22, rgba(MUTED, a))
        if i < 2:
            glow_line(d, [(x + 195, 300), (x + 275, 300)], col, a, 6)
            flow(d, [(x + 195, 300), (x + 275, 300)], t, col, a, 2, 7, 1.2, False)
    b = appear(lt, dur * 0.7)
    if b > 0:
        loop = [(1220, 440), (1220, 560), (280, 560), (280, 440)]
        glow_line(d, loop, MUTED, b * 0.7, 4)
        flow(d, loop, t, ACC, b, 5, 6, 0.4, False)
        text_c(d, CX, 590, "REPEAT, MANY TIMES PER SECOND", 26, rgba(ACC, b), BLACK)

def vis_predict(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 380), (dur * 0.3, 1.18, 800, 390)])
    world(d, 0, t, 0.8, crosswalk=False, oncoming=False)
    ego_top(d, 300, EGO_Y)
    bx = 760
    bike_top(d, bx, EGO_Y - 10, ACC2, 1, 0)
    futures = [("STRAIGHT", 70, [(bx + 60, EGO_Y - 10), (1150, EGO_Y - 10), (1400, EGO_Y - 10)], ACC2),
               ("LEFT TURN", 20, [(bx + 60, EGO_Y - 10), (1000, EGO_Y - 30), (1150, 330), (1200, 250)], CAMC),
               ("STOP", 10, [(bx + 60, EGO_Y - 10), (bx + 140, EGO_Y - 10)], RED)]
    for i, (n, pc, pts, col) in enumerate(futures):
        k = appear(lt, dur * (0.3 + 0.13 * i))
        if k <= 0: continue
        pl = partial(pts, ease_out((lt - dur * (0.3 + 0.13 * i)) / 0.8))
        line(d, pl, rgba(col, 0.25 * k), 26)
        dashed_path(d, pl, col, k, 7, t=t)
        ex, ey = pts[-1]
        label_pill(d, ex - (40 if i == 0 else 0), ey - (70 if i != 2 else -40), f"{n} {pc}%", col, k, 20, BG if col != RED else WHITE)
    cam()
    text_r(d, 1480, 690, "illustrative probabilities", 16, rgba(MUTED, appear(lt, 1)))

def vis_plan(d, lt, t, dur):
    cam_path(lt, [(0, 1.3, 760, 420), (dur, 1.0, 750, 380)])
    scroll = lt * 140
    cxw = street_scene_all(d, lt, t, scroll, 1, 0.5, cyc=820)
    # candidate paths
    cands = [[(380, EGO_Y), (cxw - 150, EGO_Y), (cxw - 80, EGO_Y)],
             [(380, EGO_Y), (cxw - 200, EGO_Y), (cxw - 40, 410), (cxw + 200, 410), (cxw + 320, EGO_Y)],
             [(380, EGO_Y), (cxw - 200, EGO_Y), (cxw - 40, 330), (cxw + 200, 330)]]
    okc = [ACC, MUTED, RED]
    labs = ["CHOSEN: FOLLOW SAFELY", "PASS: TOO CLOSE", "CROSS CENTER LINE: ILLEGAL"]
    for i, pts in enumerate(cands):
        k = appear(lt, 0.6 + i * 0.5)
        if k <= 0: continue
        chosen = (i == 0 and lt > dur * 0.5)
        line(d, pts, rgba(okc[i], (0.6 if chosen else 0.25) * k), 30 if chosen else 14)
        if chosen: dashed_path(d, pts, WHITE, k, 5, t=t)
    cam()
    for i in range(3):
        k = appear(lt, 0.6 + i * 0.5)
        if k <= 0: continue
        y = 470 + i * 62
        rrect(d, 1040, y, 1470, y + 50, 25, rgba(PANEL, k), rgba(okc[i], k), 3)
        line(d, [(1062, y + 25), (1110, y + 25)], rgba(okc[i], k), 10)
        text_l(d, 1126, y + 12, labs[i], 22, rgba(WHITE if i == 0 else MUTED, k), BLACK)
    ang = t * 7
    arc(d, 1400, 90, 40, math.degrees(ang), math.degrees(ang) + 290, rgba(ACC, appear(lt, dur * 0.6)), 8)
    text_c(d, 1400, 142, "REPLANNING", 18, rgba(MUTED, appear(lt, dur * 0.6)), BLACK)

def vis_neural(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.08, 760, 370)])
    a = appear(lt, 0)
    # input frame
    panel(d, 40, 200, 300, 470, a)
    text_l(d, 60, 212, "CAMERA FRAME", 18, rgba(MUTED, a), BLACK)
    person_top(d, 170, 350, CHILD, a, 2.4, t, False)
    layers = [6, 9, 9, 7, 4]
    xs = [420 + i * 210 for i in range(len(layers))]
    pos = [[(x, 360 + (j - (n - 1) / 2) * 62) for j in range(n)] for x, n in zip(xs, layers)]
    for li in range(len(layers) - 1):
        for (x0, y0) in pos[li]:
            for (x1, y1) in pos[li + 1]:
                line(d, [(x0, y0), (x1, y1)], rgba(DARK, 0.6 * a), 1.5)
    wave = (t * 1.2) % 1.6
    for li, layer in enumerate(pos):
        act = max(0, 1 - abs(wave * len(layers) / 1.4 - li) * 0.9)
        for j, (x, y) in enumerate(layer):
            g = act * (0.5 + 0.5 * math.sin(j * 1.7 + li))
            circle(d, x, y, 15, rgba(mix(PANEL, ACC, g), a), rgba(ACC, a), 2)
    outs = ["PEDESTRIAN 97%", "CYCLIST 2%", "CAR 1%", "OTHER 0%"]
    for j, (x, y) in enumerate(pos[-1]):
        k = appear(lt, 1.2 + j * 0.2)
        text_l(d, x + 30, y - 14, outs[j], 22 if j else 26, rgba(ACC if j == 0 else MUTED, k), BLACK)
    b = appear(lt, dur * 0.55)
    if b > 0:
        label_pill(d, 760, 620, "LEARNED FROM EXAMPLES, NOT HAND-WRITTEN RULES", ACC, b, 22)
    glow_line(d, [(300, 335), (420, 335)], ACC, a, 4)

def mini_street(d, x0, y0, w, h, t, kind, a=1.0):
    rrect(d, x0, y0, x0 + w, y0 + h, 16, rgba(ROADC, a), rgba(DARK, a), 3)
    line(d, [(x0 + 10, y0 + h / 2), (x0 + w - 10, y0 + h / 2)], rgba(YEL, 0.7 * a), 3)
    u = (t * 0.35 + kind * 0.17) % 1
    ex = x0 + 30 + (w - 60) * u
    rrect(d, ex - 26, y0 + h * 0.62, ex + 26, y0 + h * 0.86, 8, rgba(WHITE, a))
    if kind == 0:
        bx = x0 + w * 0.65; by = y0 + h - (h * 0.7) * ((t * 0.5) % 1)
        circle(d, bx, by, 9, rgba(BALLC, a))
    elif kind == 1:
        rrect(d, x0 + w * 0.6 - (w * 0.3) * u, y0 + h * 0.14, x0 + w * 0.6 - (w * 0.3) * u + 52, y0 + h * 0.38, 8, rgba((140, 90, 80), a))
    elif kind == 2:
        circle(d, x0 + w * 0.5, y0 + h * 0.3 + h * 0.3 * math.sin(t * 2), 9, rgba(CHILD, a))
    elif kind == 3:
        for k in range(6): line(d, [(x0 + 20 + k * w / 6, y0 + 10), (x0 + 30 + k * w / 6, y0 + 40)], rgba(BLUE, 0.6 * a), 2)
    elif kind == 4:
        for k in range(3): poly(d, [(x0 + w * 0.5 + k * 30, y0 + h * 0.3), (x0 + w * 0.5 + k * 30 - 10, y0 + h * 0.48), (x0 + w * 0.5 + k * 30 + 10, y0 + h * 0.48)], rgba(ACC2, a))
    else:
        rrect(d, x0 + w * 0.7, y0 + h * 0.1, x0 + w * 0.82, y0 + h * 0.45, 4, rgba((200, 200, 210), a))

def vis_sim(d, lt, t, dur):
    cam_path(lt, [(0, 1.5, 750, 300), (dur * 0.45, 1.0, 750, 360)])
    labels = ["BALL IN ROAD", "CAR CUTS IN", "JAYWALKER", "HEAVY RAIN", "ROADWORKS", "FALLEN OBJECT"]
    for i in range(6):
        r, c = divmod(i, 3)
        k = pop(lt, 0.2 + i * 0.25)
        if k <= 0: continue
        x0 = 120 + c * 430; y0 = 110 + r * 250
        mini_street(d, x0, y0, 400, 190, t + i, i, clamp(k))
        text_l(d, x0 + 10, y0 + 196, labels[i], 18, rgba(WHITE, clamp(k)), BLACK)
    b = appear(lt, dur * 0.4)
    if b > 0:
        kk = ease_inout((lt - dur * 0.4) / 1.6)
        rrect(d, 360, 30, 1140, 96, 33, rgba(PANEL, b), rgba(ACC, b), 3)
        text_c(d, CX, 44, f"≈ {int(10_000_000 * kk):,} VIRTUAL MILES / DAY", 32, rgba(ACC, b), BLACK)
        text_c(d, CX, 680, "Waymo, 2018", 18, rgba(MUTED, b))

# ======================= 05 MAPS =======================
def city_map(d, k, a=1.0, t=0.0):
    roads = [[(80, 360), (1420, 360)], [(750, 60), (750, 680)], [(80, 160), (1420, 160)], [(80, 580), (1420, 580)], [(330, 60), (330, 680)], [(1170, 60), (1170, 680)]]
    for i, r in enumerate(roads):
        kk = clamp(k * 6 - i)
        if kk <= 0: continue
        pr = partial(r, kk)
        line(d, pr, rgba((44, 52, 66), a), 90)
        line(d, pr, rgba(YEL, 0.7 * a), 3)
    kk = clamp(k * 3 - 1.2)
    if kk > 0:
        for (x, y) in [(750, 360), (330, 360), (1170, 360), (750, 160), (750, 580)]:
            for j in range(5):
                rrect(d, x - 90 + j * 38, y - 70, x - 90 + j * 38 + 20, y - 52, 3, rgba(WHITE, 0.7 * kk * a))
            traffic_light(d, x + 56, y - 110, 0.35, int(t) % 3, kk * a)
        for (x0, y0, x1, y1) in [(80, 205, 1420, 205), (80, 315, 1420, 315), (80, 405, 1420, 405), (80, 535, 1420, 535)]:
            line(d, partial([(x0, y0), (x1, y1)], kk), rgba(CURB, a), 3)

def vis_hdmap(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.25, 750, 360)])
    k = ease_inout(lt / (dur * 0.8))
    city_map(d, k, 1, t)
    tags = [("LANES", 420, 330, 0.25), ("CROSSWALKS", 760, 270, 0.45), ("TRAFFIC LIGHTS", 860, 230, 0.6), ("CURBS", 1000, 420, 0.75)]
    for n, x, y, at in tags:
        kk = appear(lt, dur * at)
        if kk > 0: label_pill(d, x, y, n, ACC, kk, 20)

def vis_localize(d, lt, t, dur):
    cam_path(lt, [(0, 1.5, 750, 360), (dur, 1.5, 750, 360)])
    city_map(d, 1, 0.7, t)
    x, y = 750 + 60 * math.sin(lt * 0.4), 405
    # GPS blob
    gk = 1 - ease_inout((lt - dur * 0.45) / 0.8)
    if gk > 0:
        r = 120 + 12 * math.sin(t * 3)
        circle(d, x + 30 * math.sin(t * 1.3), y - 20, r, rgba(RED, 0.15 * gk), rgba(RED, 0.7 * gk), 3)
        label_pill(d, x, y - r - 60, "GPS: OFF BY METERS", RED, gk, 18, WHITE)
    lk = ease_inout((lt - dur * 0.35) / 1.0)
    if lk > 0:
        rnd = random.Random(2)
        for _ in range(160):
            side = rnd.choice((315, 405, 535))
            px = x + rnd.uniform(-260, 260)
            off = (1 - lk) * rnd.uniform(-40, 40)
            circle(d, px + off, side + off * 0.6, 3, rgba(ACC, lk))
        ego_top(d, x, y + 40, lk, 0.6)
        label_pill(d, x, y + 90, "LIDAR MATCHED TO MAP", ACC, lk, 18)

# ======================= 06 HARD =======================
def truck_top(d, x, y, a=1.0):
    rrect(d, x - 140, y - 40, x + 70, y + 40, 8, rgba((150, 156, 168), a))
    rrect(d, x + 74, y - 36, x + 140, y + 36, 14, rgba((110, 120, 140), a))

def vis_rare(d, lt, t, dur):
    a = appear(lt, 0)
    k = ease_inout((lt - 0.3) / 1.2)
    rrect(d, 150, 60, 1350, 130, 35, rgba(DARK, a))
    rrect(d, 150, 60, 150 + 1188 * k, 130, 35, rgba(MUTED, a))
    rrect(d, 1338, 60, 1350, 130, 6, rgba(RED, a * clamp(k * 3 - 2)))
    text_l(d, 180, 76, f"{int(99 * k)}% BORING", 34, rgba(BG, a), BLACK)
    text_r(d, 1460, 150, "1% CHAOS", 30, rgba(RED, a * clamp(k * 3 - 2)), BLACK)
    cards = [("MATTRESS ON THE ROAD", 0), ("OFFICER WAVES YOU THROUGH", 1), ("CHILD CHASES A BALL", 2)]
    for i, (n, kind) in enumerate(cards):
        kk = pop(lt, dur * (0.35 + 0.17 * i))
        if kk <= 0: continue
        aa = clamp(kk); x0 = 90 + i * 450; y0 = 230
        rrect(d, x0, y0, x0 + 420, y0 + 400, 26, rgba(PANEL, aa), rgba(RED, aa), 3)
        cx, cy = x0 + 210, y0 + 170
        lt2 = lt - dur * (0.35 + 0.17 * i)
        if kind == 0:
            truck_top(d, cx - 20, cy - 60, aa)
            mx = cx - 120 - 20 * lt2; my = cy + min(80, lt2 * 120)
            rrect(d, mx - 60, my - 22, mx + 60, my + 22, 10, rgba((230, 230, 240), aa))
        elif kind == 1:
            traffic_light(d, cx + 110, cy - 130, 0.6, 0, aa)
            person_top(d, cx - 30, cy + 10, (70, 110, 200), aa, 2.0, t, False)
            ang = math.sin(t * 6) * 0.6
            line(d, [(cx - 10, cy - 10), (cx - 10 + math.cos(-1.2 + ang) * 70, cy - 10 + math.sin(-1.2 + ang) * 70)], rgba((70, 110, 200), aa), 12)
        else:
            ball_top(d, cx + 40 - 40 * math.sin(t * 2), cy + 20, aa, 22, t * 5)
            person_top(d, cx - 70 - 40 * math.sin(t * 2), cy + 30, CHILD, aa, 1.8, t)
        text_c(d, x0 + 210, y0 + 330, n, 22, rgba(WHITE, aa), BLACK)

def vis_weather(d, lt, t, dur):
    seg = dur / 3
    panels = [("RAIN BLURS CAMERAS", 0), ("SNOW HIDES LANE LINES", 1), ("FOG SCATTERS LIDAR", 2)]
    for i, (n, kind) in enumerate(panels):
        k = pop(lt, 0.15 + i * seg * 0.8)
        if k <= 0: continue
        a = clamp(k); x0 = 60 + i * 470; y0 = 90; w, h = 440, 470
        rrect(d, x0, y0, x0 + w, y0 + h, 24, rgba(PANEL, a), rgba(DARK, a), 3)
        cxp = x0 + w / 2
        if kind == 0:
            poly(d, [(cxp - 10, y0 + 140), (cxp + 10, y0 + 140), (x0 + w - 30, y0 + h - 20), (x0 + 30, y0 + h - 20)], rgba((44, 48, 58), a))
            car_rear(d, cxp - 70, y0 + 230, cxp + 70, y0 + 330, (90, 110, 150), a)
            rnd = random.Random(5)
            for _ in range(22):
                dx, dy = rnd.uniform(x0 + 20, x0 + w - 20), rnd.uniform(y0 + 20, y0 + h - 20)
                r = rnd.uniform(10, 28)
                circle(d, dx, dy + (t * 20 + r) % 30, r, rgba((180, 210, 240), 0.22 * a), rgba((220, 235, 255), 0.4 * a), 2)
        elif kind == 1:
            rrect(d, x0 + 20, y0 + 60, x0 + w - 20, y0 + h - 30, 14, rgba((44, 48, 58), a))
            cover = clamp((lt - (0.15 + i * seg * 0.8)) / 2.5)
            for k2 in range(6):
                line(d, [(cxp, y0 + 80 + k2 * 60), (cxp, y0 + 110 + k2 * 60)], rgba(WHITE, a * (1 - cover)), 8)
            rrect(d, x0 + 20, y0 + 60, x0 + w - 20, y0 + h - 30, 14, rgba((235, 240, 248), 0.75 * cover * a))
            rnd = random.Random(9)
            for _ in range(70):
                sx = rnd.uniform(x0 + 10, x0 + w - 10); sp = rnd.uniform(40, 90)
                sy = y0 + ((t * sp + rnd.uniform(0, h)) % h)
                circle(d, sx + 8 * math.sin(t + sx), sy, rnd.uniform(2, 5), rgba(WHITE, 0.9 * a))
        else:
            rnd = random.Random(11)
            for _ in range(120):
                ang = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(40, 200)
                px, py = cxp + math.cos(ang) * r, y0 + 250 + math.sin(ang) * r * 0.6
                jit = rnd.gauss(0, 14)
                circle(d, px + jit, py + jit, 3, rgba(LIDC, a * rnd.uniform(0.2, 0.9)))
            rrect(d, x0 + 10, y0 + 10, x0 + w - 10, y0 + h - 10, 18, rgba((190, 200, 215), (0.18 + 0.06 * math.sin(t)) * a))
        text_c(d, cxp, y0 + h + 24, n, 24, rgba(WHITE, a), BLACK)

def cone(d, x, y, s=1.0, a=1.0):
    poly(d, [(x, y - 40 * s), (x - 20 * s, y + 10 * s), (x + 20 * s, y + 10 * s)], rgba(ACC2, a))
    line(d, [(x - 12 * s, y - 12 * s), (x + 12 * s, y - 12 * s)], rgba(WHITE, a), 5 * s)
    rrect(d, x - 26 * s, y + 8 * s, x + 26 * s, y + 16 * s, 3, rgba(ACC2, a))

def vis_recall(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.12, 760, 380)])
    a = appear(lt, 0)
    # closed ramp scene
    rrect(d, 0, 260, 1500, 520, 0, rgba(ROADC, a))
    poly(d, [(700, 260), (900, 260), (1500, 80), (1500, 0), (1300, 0)], rgba((40, 46, 56), a))
    for k in range(6): cone(d, 760 + k * 55, 300 - k * 4, 1, a)
    rrect(d, 820, 120, 1080, 210, 10, rgba(ACC2, a)); text_c(d, 950, 140, "RAMP CLOSED", 30, rgba(BG, a), BLACK)
    u = ease_inout((lt - 0.6) / (dur * 0.45))
    path = [(100, 400), (600, 380), (900, 270), (1200, 120)]
    px, py = path_point(path, u * 0.999)
    line(d, partial(path, u), rgba(RED, 0.6 * a), 6)
    topcar(d, px, py, WHITE, 1, 140, 64, a)
    circle(d, px - 8, py, 10, rgba(ACC, a))
    b = pop(lt, dur * 0.5)
    if b > 0:
        cam()
        bb = clamp(b)
        rrect(d, 380, 420, 1120, 680, 30, rgba(PANEL, bb), rgba(RED, bb), 5)
        text_c(d, CX, 440, "RECALL · 2026", 34, rgba(RED, bb), BLACK)
        kk = ease_inout((lt - dur * 0.5) / 1.0)
        big_text(d, CX, 495, f"~{int(4000 * kk):,} ROBOTAXIS", 66, WHITE, bb)
        text_c(d, CX, 600, "pulled off highways while a fix was built", 24, rgba(MUTED, bb))

def vis_bar(d, lt, t, dur):
    a = appear(lt, 0)
    # balance scale
    tilt = 0.18 * ease_inout((lt - 0.8) / 1.5)
    px, py = CX, 200
    poly(d, [(px, py), (px - 60, 600), (px + 60, 600)], rgba(DARK, a))
    L = 480
    x0, y0 = px - math.cos(tilt) * L, py + math.sin(tilt) * L
    x1, y1 = px + math.cos(tilt) * L, py - math.sin(tilt) * L
    line(d, [(x0, y0), (x1, y1)], rgba(WHITE, a), 10)
    for (x, y, lab, sub, col) in ((x0, y0, "HUMAN DRIVER", "mistakes accepted", MUTED), (x1, y1, "ROBOT CAR", "must be far better", ACC)):
        line(d, [(x, y), (x, y + 120)], rgba(WHITE, a), 4)
        rrect(d, x - 170, y + 120, x + 170, y + 250, 24, rgba(PANEL, a), rgba(col, a), 3)
        text_c(d, x, y + 140, lab, 30, rgba(col, a), BLACK)
        text_c(d, x, y + 192, sub, 22, rgba(WHITE, a))
    circle(d, px, py, 18, rgba(ACC, a))
    b = appear(lt, dur * 0.6)
    if b > 0: label_pill(d, CX, 40, "EVERYWHERE · ALL THE TIME", ACC, b, 30)

# ======================= 07 TODAY =======================
def counter_card(d, x, y, w, h, top, val, bottom, col, a):
    rrect(d, x, y, x + w, y + h, 28, rgba(PANEL, a), rgba(col, a), 3)
    text_c(d, x + w / 2, y + 22, top, 22, rgba(MUTED, a), BLACK)
    big_text(d, x + w / 2, y + 70, val, 84 if len(val) < 7 else 66, col, a)
    text_c(d, x + w / 2, y + h - 60, bottom, 24, rgba(WHITE, a), BLACK)

def vis_waymo_stats(d, lt, t, dur):
    cam_path(lt, [(0, 1.1, 750, 380), (dur, 1.0, 750, 360)])
    items = [("PAID RIDES IN", 15, "{:d}", "US METRO AREAS", CAMC, 0.4), ("EVERY WEEK", 500000, "{:,}+", "PAID RIDES", ACC, 1.4), ("FLEET OF", 4000, "~{:,}", "ROBOTAXIS", ACC2, 2.6)]
    for i, (top, v, fmt, bot, col, at) in enumerate(items):
        k = pop(lt, at)
        if k <= 0: continue
        kk = ease_inout((lt - at) / 1.4)
        counter_card(d, 60 + i * 470, 170, 440, 340, top, fmt.format(int(v * kk)), bot, col, clamp(k))
    text_c(d, CX, 640, "Waymo · figures as of autumn 2026", 20, rgba(MUTED, appear(lt, 1)))

def vis_safety(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, CX, 30, "CRASHES VS HUMAN DRIVERS · 271M DRIVERLESS MILES", 30, rgba(WHITE, a), BLACK)
    groups = [("SERIOUS-INJURY CRASHES", 95, 0.5), ("PEDESTRIAN INJURY CRASHES", 93, dur * 0.55)]
    for gi, (n, red, at) in enumerate(groups):
        k = appear(lt, at)
        if k <= 0: continue
        x0 = 120 + gi * 680
        kk = ease_inout((lt - at - 0.3) / 1.4)
        text_c(d, x0 + 280, 100, n, 24, rgba(MUTED, k), BLACK)
        base = 600
        for j, (lab, v, col) in enumerate((("HUMAN", 100, MUTED), ("WAYMO", 100 - red, ACC))):
            x = x0 + 90 + j * 240
            hh = 380 * (v / 100) * (kk if j else min(1, kk * 2))
            rrect(d, x, base - 380, x + 150, base, 16, rgba(DARK, k))
            if hh > 8: rrect(d, x, base - hh, x + 150, base, 16, rgba(col, k))
            text_c(d, x + 75, base + 12, lab, 24, rgba(col, k), BLACK)
        big_text(d, x0 + 520, 300, f"−{int(red * kk)}%", 64, ACC, k)
    text_c(d, CX, 680, "Source: Waymo's own safety data, through June 2026", 18, rgba(MUTED, a))

def waymo_car_side(d, x, y, a=1.0, s=1.0):
    poly(d, [(x - 200 * s, y + 40 * s), (x - 200 * s, y - 20 * s), (x - 130 * s, y - 50 * s), (x - 60 * s, y - 110 * s), (x + 120 * s, y - 110 * s), (x + 190 * s, y - 40 * s), (x + 205 * s, y + 40 * s)], rgba(WHITE, a))
    rrect(d, x - 40 * s, y - 150 * s, x + 40 * s, y - 110 * s, 14 * s, rgba(ACC, a))
    for wx in (-120, 120):
        circle(d, x + wx * s, y + 40 * s, 44 * s, rgba(BG, a)); circle(d, x + wx * s, y + 40 * s, 30 * s, rgba((70, 78, 92), a))
    for sx, sy in ((-190, 0), (195, 0), (-60, -100), (100, -100)):
        circle(d, x + sx * s, y + sy * s, 9 * s, rgba(CAMC, a))
    for sx in (-200, 205):
        rrect(d, x + sx * s - 8 * s, y + 10 * s, x + sx * s + 8 * s, y + 30 * s, 4, rgba(RADC, a))

def tesla_car_side(d, x, y, a=1.0, s=1.0):
    poly(d, [(x - 200 * s, y + 40 * s), (x - 205 * s, y - 10 * s), (x - 150 * s, y - 40 * s), (x - 40 * s, y - 100 * s), (x + 80 * s, y - 100 * s), (x + 200 * s, y - 20 * s), (x + 205 * s, y + 40 * s)], rgba((200, 60, 60), a))
    for wx in (-120, 120):
        circle(d, x + wx * s, y + 40 * s, 44 * s, rgba(BG, a)); circle(d, x + wx * s, y + 40 * s, 30 * s, rgba((70, 78, 92), a))
    for sx, sy in ((-30, -96), (60, -96), (-200, 0), (200, 0), (20, -40)):
        circle(d, x + sx * s, y + sy * s, 9 * s, rgba(CAMC, a))

def vis_tesla(d, lt, t, dur):
    a = appear(lt, 0)
    k1 = pop(lt, 0.2); k2 = pop(lt, 0.9)
    if k1 > 0:
        tesla_car_side(d, 1080, 330, clamp(k1), 1.0)
        label_pill(d, 1080, 430, "CAMERAS ONLY", CAMC, clamp(k1), 26)
        text_c(d, 1080, 500, "Tesla · robotaxi in 7 metros", 24, rgba(WHITE, clamp(k1)), BLACK)
    if k2 > 0:
        waymo_car_side(d, 420, 330, clamp(k2), 1.0)
        label_pill(d, 420, 430, "CAMERAS + LIDAR + RADAR", ACC, clamp(k2), 26)
        text_c(d, 420, 500, "Waymo", 24, rgba(WHITE, clamp(k2)), BLACK)
    b = pop(lt, dur * 0.6)
    if b > 0:
        circle(d, CX, 330, 60 * clamp(b), rgba(ACC2, clamp(b)))
        text_c(d, CX, 300, "VS", 44, rgba(BG, clamp(b)), BLACK)
        label_pill(d, CX, 600, "THE BIG DEBATE", ACC2, clamp(b), 30)

def wheel(d, x, y, r, a=1.0, ang=0.0):
    circle(d, x, y, r, None, rgba(WHITE, a), 22)
    circle(d, x, y, r * 0.22, rgba(WHITE, a))
    for k in (0, 1, 2):
        aa = ang + math.pi / 2 + k * 2 * math.pi / 3
        line(d, [(x, y), (x + math.cos(aa) * r, y + math.sin(aa) * r)], rgba(WHITE, a), 18)

def eye(d, x, y, s, col, a=1.0, t=0.0):
    poly(d, [(x - 70 * s, y), (x - 30 * s, y - 34 * s), (x + 30 * s, y - 34 * s), (x + 70 * s, y), (x + 30 * s, y + 34 * s), (x - 30 * s, y + 34 * s)], rgba(col, a))
    circle(d, x + 6 * math.sin(t), y, 22 * s, rgba(BG, a)); circle(d, x + 6 * math.sin(t), y, 10 * s, rgba(col, a))

def vis_own_car(d, lt, t, dur):
    cam_path(lt, [(0, 1.2, 600, 380), (dur, 1.0, 750, 360)])
    a = appear(lt, 0)
    wheel(d, 450, 400, 200, a, 0.05 * math.sin(t))
    hk = ease_inout((lt - 0.8) / 1.0)
    for sx in (-1, 1):
        hx = 450 + sx * (200 + 120 * hk); hy = 400 - 40 * hk
        rrect(d, hx - 40, hy - 60, hx + 40, hy + 60, 30, rgba((230, 190, 160), a))
    b = appear(lt, dur * 0.35)
    if b > 0:
        eye(d, 1080, 260, 1.4, ACC, b, t)
        text_c(d, 1080, 340, "EYES ON THE ROAD", 32, rgba(ACC, b), BLACK)
    c = appear(lt, dur * 0.6)
    if c > 0:
        label_pill(d, 1080, 430, "LEVEL 2 = YOU ARE RESPONSIBLE", ACC2, c, 28)

# ======================= OUTRO =======================
def vis_replay(d, lt, t, dur):
    steps = dur
    s1, s2, s3, s4, s5 = 0.12 * steps, 0.3 * steps, 0.45 * steps, 0.6 * steps, 0.75 * steps
    cam_path(lt, [(0, 1.0, 750, 380), (s1, 1.25, 820, 420), (s4, 1.25, 820, 420), (dur, 1.05, 760, 400)])
    # car slows to a stop after s5
    stop_k = ease_out((lt - s5) / 2.2)
    v = 38
    scroll = v * min(lt, s5) + (v * 1.1 * stop_k if lt > s5 else 0)
    world(d, scroll, t, 1)
    bx = GAP_WX - scroll
    by = max(330, PARK_Y1 + 40 - lt * 120)
    cxp, cyp = bx - 40, max(470, PARK_Y1 + 70 - max(0, lt - 1.0) * 60)
    if lt > s2: lidar_sweep(d, 322, EGO_Y, t, 0.8)
    ego_top(d, 330, EGO_Y, 1, 1, brake=stop_k if lt > s5 else 0)
    ball_top(d, bx, by, 1, 18, t * 8)
    person_top(d, cxp, cyp, CHILD, 1, 1.0, t)
    if lt > s1:
        k = appear(lt, s1)
        bbox(d, bx - 30, by - 30, bx + 30, by + 30, "BALL", BALLC, k, 18)
        bbox(d, cxp - 32, cyp - 28, cxp + 32, cyp + 28, "CHILD", CHILD, k, 18)
    if lt > s2:
        lidar_points_box(d, cxp - 30, cyp - 26, cxp + 30, cyp + 26, 322, EGO_Y, t * 3.2, appear(lt, s2), 10)
        label_pill(d, cxp, cyp + 44, "8.6 m", ACC, appear(lt, s2), 18)
    if lt > s3:
        k = appear(lt, s3)
        radar_waves(d, 330, EGO_Y, t, k * 0.6, 3, RADC, 30, 700)
        label_pill(d, cxp + 120, cyp - 20, "1.2 m/s ↑", RADC, k, 18)
    if lt > s4:
        k = appear(lt, s4)
        pts = [(cxp, cyp), (cxp + 10, EGO_Y), (cxp + 20, 380)]
        line(d, pts, rgba(RED, 0.3 * k), 22); dashed_path(d, pts, RED, k, 6, t=t)
    if lt > s5:
        k = appear(lt, s5)
        sx = cxp - 140
        line(d, [(sx, 390), (sx, 505)], rgba(RED, k), 10)
        label_pill(d, sx - 10, 330, "PLAN: STOP", RED, k, 20, WHITE)
    cam()
    steps_lab = [("SEE", CAMC, s1), ("MEASURE", LIDC, s2), ("TRACK", RADC, s3), ("PREDICT", ACC2, s4), ("STOP", RED, s5)]
    for i, (n, col, at) in enumerate(steps_lab):
        k = appear(lt, at)
        if k > 0:
            x = 220 + i * 265
            rrect(d, x - 110, 20, x + 110, 74, 27, rgba(PANEL, k), rgba(col, k), 3)
            text_c(d, x, 32, n, 24, rgba(col, k), BLACK)

def vis_question(d, lt, t, dur):
    cam(1.0 + 0.04 * clamp(lt / dur), 750, 360)
    k = pop(lt, 0.1)
    big_text(d, CX, 40, "WOULD YOU RIDE IN A CAR", 54, WHITE, clamp(k))
    big_text(d, CX, 110, "WITH NO DRIVER TODAY?", 54, ACC, clamp(k))
    opts = [("YES", ACC), ("NO", RED), ("ONLY IN SOME PLACES", ACC2)]
    for i, (s, col) in enumerate(opts):
        kk = pop(lt, 0.9 + i * 0.5)
        if kk <= 0: continue
        x = 300 + i * 450; aa = clamp(kk)
        g = 0.5 + 0.5 * math.sin(t * 3 + i * 2)
        rrect(d, x - 200, 260, x + 200, 480, 30, rgba(PANEL, aa), rgba(col, (0.5 + 0.5 * g) * aa), 4)
        text_c(d, x, 345 if len(s) < 5 else 352, s, 60 if len(s) < 5 else 32, rgba(col, aa), BLACK)
    c = appear(lt, dur * 0.6)
    if c > 0: label_pill(d, CX, 560, "TELL ME IN THE COMMENTS", ACC, c, 32)

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
