# Visuals for "Are Electric Cars Really Better for the Planet?" — runs inside tools/render_long2.py globals.
# Logical canvas 1500 x 720. Every vis_*(d, lt, t, dur).
import random, os

CX = 750
RED = (255, 84, 84); CO2C = (255, 122, 61); GAS = (255, 150, 90); EVC = ACC; WATER = (90, 170, 255)
COAL = (120, 110, 105); HYDRO = (90, 170, 255); SOLAR = (255, 205, 70)

def sent_t(name, k):
    for sc in scenes:
        if sc["visual"] == name:
            k = min(k, len(sc["sentences"]) - 1)
            return sc["sentences"][k]["start"] - sc["vis_start"]
    return 0.0
def appear(lt, at, dur=0.45): return ease_out((lt - at) / dur)
def pop(lt, at, dur=0.5): return clamp(back_out((lt - at) / dur), 0, 1.15)
def label_pill(d, x, y, s, col, a=1.0, size=28, fg=None, name=BLACK):
    if a <= 0: return
    f = FL(name, size); tw = d.textlength(s, font=f) / S / CAM[0]
    rrect(d, x - tw / 2 - 20, y, x + tw / 2 + 20, y + size + 22, (size + 22) / 2, rgba(col, a))
    text_c(d, x, y + 9, s, size, rgba(fg or BG, a), name)
def big_text(d, x, y, s, size, col, a=1.0):
    if a <= 0: return
    text_c(d, x + 4, y + 6, s, size, rgba((0, 0, 0), 0.5 * a), BLACK)
    text_c(d, x, y, s, size, rgba(col, a), BLACK)
def count(lt, at, dur, v): return v * ease_inout((lt - at) / dur)

def chart_axes(d, x0, y0, x1, y1, xl, yl, a=1.0):
    line(d, [(x0, y1), (x1, y1)], rgba(MUTED, a), 4); line(d, [(x0, y0), (x0, y1)], rgba(MUTED, a), 4)
    text_c(d, (x0 + x1) / 2, y1 + 18, xl, 22, rgba(MUTED, a), BLACK)
    text_l(d, x0 + 14, y0 - 12, yl, 22, rgba(MUTED, a), BLACK)

# ---------- icons ----------
def car_icon(d, x, y, s, col, a=1.0, ev=True):
    pts = [(-120, 30), (-122, 0), (-100, -18), (-60, -26), (-30, -58), (40, -60), (80, -30), (118, -16), (124, 30)]
    poly(d, [(x + px * s + 5, y + py * s + 8) for px, py in pts], rgba((0, 0, 0), 0.3 * a))
    poly(d, [(x + px * s, y + py * s) for px, py in pts], rgba(col, a))
    poly(d, [(x + px * s, y + py * s) for px, py in [(-24, -50), (10, -52), (10, -26), (-48, -26)]], rgba(BG, a))
    poly(d, [(x + px * s, y + py * s) for px, py in [(18, -52), (38, -52), (66, -26), (18, -26)]], rgba(BG, a))
    for wx in (-70, 72):
        circle(d, x + wx * s, y + 30 * s, 24 * s, rgba(BG, a)); circle(d, x + wx * s, y + 30 * s, 15 * s, rgba((70, 78, 92), a))
    if ev: bolt(d, x - 2 * s, y + 2 * s, 0.22 * s, rgba(BG, a))
    else:
        rrect(d, x - 132 * s, y + 18 * s, x - 118 * s, y + 26 * s, 3, rgba((60, 60, 60), a))

def battery_icon(d, x, y, w, h, level, col, a=1.0, outline=WHITE):
    rrect(d, x, y, x + w, y + h, 14, rgba(PANEL, a), rgba(outline, a), 5)
    rrect(d, x + w, y + h * 0.32, x + w + 16, y + h * 0.68, 5, rgba(outline, a))
    iw = (w - 20) * clamp(level)
    if iw > 4: rrect(d, x + 10, y + 10, x + 10 + iw, y + h - 10, 8, rgba(col, a))

def cloud(d, x, y, s, col, a=1.0, t=0.0):
    for (dx, dy, r) in ((-40, 10, 38), (0, -14, 48), (44, 8, 36), (-10, 26, 34), (26, 26, 30)):
        circle(d, x + dx * s + 3 * math.sin(t + dx), y + dy * s, r * s, rgba(col, a))

def co2_puffs(d, x, y, t, a=1.0, n=7, spread=60, rise=160, col=CO2C, size=12):
    rnd = random.Random(int(x * 7 + y))
    for i in range(n):
        ph = (t * 0.35 + i / n) % 1
        px = x + rnd.uniform(-spread, spread) + 14 * math.sin(t * 1.3 + i)
        py = y - ph * rise
        circle(d, px, py, size * (0.6 + ph), rgba(col, a * 0.55 * (1 - ph)))

def factory(d, x, y, s, col, a=1.0, t=0.0, smoke=True, smoke_col=(140, 140, 150)):
    poly(d, [(x - 120 * s, y), (x - 120 * s, y - 70 * s), (x - 60 * s, y - 110 * s), (x - 60 * s, y - 70 * s), (x, y - 110 * s), (x, y - 70 * s), (x + 60 * s, y - 110 * s), (x + 60 * s, y), ], rgba(col, a))
    rrect(d, x + 70 * s, y - 170 * s, x + 105 * s, y, 4, rgba(col, a))
    for k in range(3): rrect(d, x - 100 * s + k * 55 * s, y - 50 * s, x - 70 * s + k * 55 * s, y - 25 * s, 3, rgba(BG, a))
    if smoke: co2_puffs(d, x + 88 * s, y - 175 * s, t, a, 6, 18 * s, 120 * s, smoke_col, 14 * s)

def drop(d, x, y, s, col, a=1.0):
    poly(d, [(x, y - 30 * s), (x - 18 * s, y), (x + 18 * s, y)], rgba(col, a))
    circle(d, x, y + 4 * s, 19 * s, rgba(col, a))

def element_tile(d, x, y, sym, name, num, col, a=1.0, w=190):
    rrect(d, x + 6, y + 10, x + w + 6, y + w + 10, 20, rgba((0, 0, 0), 0.35 * a))
    rrect(d, x, y, x + w, y + w, 20, rgba(PANEL, a), rgba(col, a), 4)
    text_l(d, x + 16, y + 12, str(num), 24, rgba(MUTED, a), BLACK)
    text_c(d, x + w / 2, y + 40, sym, 82, rgba(col, a), BLACK)
    text_c(d, x + w / 2, y + w - 46, name, 24, rgba(WHITE, a), BLACK)

def house(d, x, y, s, col, a=1.0):
    poly(d, [(x - 90 * s, y - 60 * s), (x, y - 140 * s), (x + 90 * s, y - 60 * s)], rgba(col, a))
    rrect(d, x - 75 * s, y - 62 * s, x + 75 * s, y + 40 * s, 6, rgba(mix(col, BG, 0.25), a))
    rrect(d, x - 20 * s, y - 5 * s, x + 20 * s, y + 40 * s, 4, rgba(BG, a))

def solar_panel(d, x, y, s, a=1.0):
    poly(d, [(x - 60 * s, y), (x - 40 * s, y - 50 * s), (x + 60 * s, y - 50 * s), (x + 40 * s, y)], rgba((40, 70, 140), a))
    for k in range(1, 4):
        line(d, [(x - 60 * s + k * 25 * s, y), (x - 40 * s + k * 25 * s, y - 50 * s)], rgba((140, 180, 255), a * 0.6), 2)
    line(d, [(x - 50 * s, y - 25 * s), (x + 50 * s, y - 25 * s)], rgba((140, 180, 255), a * 0.6), 2)

def stamp(d, x, y, s, col, a=1.0, ang=-0.15):
    text_c(d, x, y, s, 70, rgba(col, a), BLACK)

# ======================= INTRO =======================
_hero_cache = {}
def hero_frame(i):
    i = max(0, min(299, i))
    if i not in _hero_cache:
        if len(_hero_cache) > 4: _hero_cache.clear()
        pth = f"{EP}/hero_frames/f{i:04d}.jpg"
        _hero_cache[i] = Image.open(pth).convert("RGB").resize((LW * S, LH * S), Image.BILINEAR) if os.path.exists(pth) else None
    return _hero_cache[i]

def vis_hero(d, lt, t, dur):
    im = hero_frame(int(lt * 30))
    if im is not None: d._image.paste(im, (0, 0))
    a = appear(lt, 0.4)
    rrect(d, 40, 40, 380, 150, 24, rgba(PANEL, 0.85 * a), rgba(DARK, a), 3)
    text_l(d, 66, 52, "ODOMETER", 22, rgba(MUTED, a), BLACK)
    text_l(d, 66, 84, "0 MILES", 48, rgba(WHITE, a), BLACK)
    b = appear(lt, sent_t("hero", 1))
    if b > 0:
        kk = ease_inout((lt - sent_t("hero", 1)) / 2.5)
        rrect(d, 1080, 40, 1460, 150, 24, rgba(PANEL, 0.85 * b), rgba(CO2C, b), 3)
        text_l(d, 1106, 52, "CO₂ ALREADY EMITTED", 22, rgba(CO2C, b), BLACK)
        text_l(d, 1106, 84, f"{kk * 9:.1f} t", 48, rgba(WHITE, b), BLACK)
        text_r(d, 1460, 160, "illustrative", 16, rgba(MUTED, b))

def scales(d, cx, cy, tilt, a, lab_l, lab_r, col_l, col_r, sub_l="", sub_r=""):
    poly(d, [(cx, cy), (cx - 50, cy + 330), (cx + 50, cy + 330)], rgba(DARK, a))
    L = 430
    x0, y0 = cx - math.cos(tilt) * L, cy + math.sin(tilt) * L
    x1, y1 = cx + math.cos(tilt) * L, cy - math.sin(tilt) * L
    line(d, [(x0, y0), (x1, y1)], rgba(WHITE, a), 9)
    circle(d, cx, cy, 16, rgba(ACC, a))
    for (x, y, lab, sub, col, ev) in ((x0, y0, lab_l, sub_l, col_l, True), (x1, y1, lab_r, sub_r, col_r, False)):
        line(d, [(x, y), (x, y + 90)], rgba(WHITE, a), 3)
        rrect(d, x - 170, y + 90, x + 170, y + 250, 24, rgba(PANEL, a), rgba(col, a), 3)
        car_icon(d, x, y + 150, 0.9, col, a, ev)
        text_c(d, x, y + 196, lab, 26, rgba(col, a), BLACK)

def vis_scale_tilt(d, lt, t, dur):
    cam_path(lt, [(0, 1.1, 750, 380), (dur, 1.0, 750, 360)])
    a = appear(lt, 0)
    wob = 0.16 * math.sin(lt * 2.4) * (1 - ease_out(lt / dur))
    scales(d, CX, 170, wob, a, "ELECTRIC", "GASOLINE", EVC, GAS)
    q = pop(lt, sent_t("scale_tilt", 1))
    if q > 0: big_text(d, CX, 20, "WHO'S WRONG?", 64, WHITE, clamp(q))

STOPS = [("MINE", (214, 170, 100)), ("FACTORY", (150, 160, 175)), ("ROAD", ACC), ("SCRAPYARD", CO2C)]
def vis_journey(d, lt, t, dur):
    cam_path(lt, [(0, 1.35, 320, 360), (dur * 0.6, 1.0, 750, 360), (dur, 1.0, 750, 360)])
    pts = [(170, 360), (540, 360), (910, 360), (1290, 360)]
    k = ease_inout((lt - 0.6) / (dur * 0.6))
    pl = partial(pts, k)
    glow_line(d, pl, MUTED, 0.6, 8)
    for i, (n, col) in enumerate(STOPS):
        kk = pop(lt, 0.3 + i * dur * 0.18)
        if kk <= 0: continue
        x, y = pts[i]; aa = clamp(kk)
        circle(d, x, y, 90 * aa, rgba(PANEL, aa), rgba(col, aa), 5)
        if i == 0:
            poly(d, [(x - 50, y + 30), (x - 10, y - 30), (x + 10, y), (x + 30, y - 20), (x + 55, y + 30)], rgba(col, aa))
        elif i == 1: factory(d, x - 10, y + 40, 0.5, col, aa, t, smoke=True)
        elif i == 2: car_icon(d, x, y + 4, 0.6, col, aa)
        else:
            for j in range(3): rrect(d, x - 45 + j * 18, y + 10 - j * 22, x + 25 + j * 18, y + 30 - j * 22, 6, rgba(col, aa * (0.6 + 0.2 * j)))
        text_c(d, x, y + 110, n, 30, rgba(col, aa), BLACK)
    if k > 0.05:
        x, y = path_point(pts, k * 0.999)
        circle(d, x, y - 120, 16, rgba(WHITE, 1)); text_c(d, x, y - 108, "", 10, rgba(WHITE))
        co2_puffs(d, x, y - 130, t, 0.9, 5, 20, 90, CO2C, 9)
    q = appear(lt, sent_t("journey", 1))
    if q > 0:
        cam()
        label_pill(d, CX, 600, "WHEN — AND WHERE — DOES IT BECOME GREEN?", ACC, q, 28)

# ======================= 01 DEBT =======================
def vis_factory(d, lt, t, dur):
    cam_path(lt, [(0, 1.15, 750, 400), (dur, 1.0, 750, 360)])
    a = appear(lt, 0)
    factory(d, 280, 420, 1.3, (150, 160, 175), a, t)
    text_c(d, 280, 450, "MANUFACTURING", 26, rgba(MUTED, a), BLACK)
    base = 560
    for i, (lab, v, col, ev, at) in enumerate((("GAS CAR", 1.0, GAS, False, 0.5), ("ELECTRIC CAR", 1.8, EVC, True, 1.3))):
        k = ease_inout((lt - at) / 1.6)
        x = 720 + i * 330
        hh = 230 * v * k
        rrect(d, x - 80, base - 430, x + 80, base, 18, rgba(DARK, a))
        if hh > 10: rrect(d, x - 80, base - hh, x + 80, base, 18, rgba(col, a))
        car_icon(d, x, base + 60, 0.55, col, appear(lt, at), ev)
        text_c(d, x, base + 100, lab, 24, rgba(col, a), BLACK)
        if i == 1 and k > 0.3:
            big_text(d, x, base - hh - 90, f"+{int(80 * clamp((k - 0.3) / 0.7))}%", 64, WHITE, clamp((k - 0.3) * 3))
    text_r(d, 1460, 690, "Source: MIT Climate Portal", 18, rgba(MUTED, a))

def vis_battery_co2(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.06, 750, 340)])
    a = appear(lt, 0)
    battery_icon(d, 170, 140, 520, 230, 1.0, (60, 80, 40), a, WHITE)
    for r in range(3):
        for c in range(8):
            rrect(d, 190 + c * 60, 160 + r * 66, 238 + c * 60, 212 + r * 66, 6, rgba(ACC, a * 0.85))
    text_c(d, 430, 390, "80 kWh BATTERY PACK", 30, rgba(WHITE, a), BLACK)
    co2_puffs(d, 430, 140, t, appear(lt, 1.0), 10, 220, 140, CO2C, 16)
    b = appear(lt, sent_t("battery_co2", 1))
    if b > 0:
        kk = ease_inout((lt - sent_t("battery_co2", 1) - 0.3) / 2.2)
        panel(d, 800, 120, 1440, 460, b)
        text_c(d, 1120, 140, "CO₂ TO MAKE IT", 28, rgba(MUTED, b), BLACK)
        big_text(d, 1120, 190, f"{2.5 * kk:.1f} – {16 * kk:.0f} t", 80, CO2C, b)
        x0, x1 = 850, 1390
        rrect(d, x0, 340, x1, 380, 20, rgba(DARK, b))
        lo = x0 + (x1 - x0) * 2.5 / 16
        rrect(d, lo, 340, lo + (x1 - lo) * kk, 380, 20, rgba(CO2C, b))
        text_l(d, x0, 392, "0 t", 20, rgba(MUTED, b)); text_r(d, x1, 392, "16 t", 20, rgba(MUTED, b))
    text_r(d, 1460, 690, "Source: MIT Climate Portal", 18, rgba(MUTED, a))

def vis_range_why(d, lt, t, dur):
    a = appear(lt, 0)
    for i, (lab, col, sc, smoke_col, v) in enumerate((("COAL-POWERED FACTORY", COAL, 1.0, (90, 85, 80), 1.0), ("CLEAN-POWERED FACTORY", HYDRO, 1.0, (200, 220, 240), 0.2))):
        k = appear(lt, 0.3 + i * 0.9)
        x = 300 + i * 520
        factory(d, x, 330, 1.1, col, k, t, True, smoke_col)
        text_c(d, x, 360, lab, 24, rgba(col, k), BLACK)
        kk = ease_inout((lt - 0.8 - i * 0.9) / 1.4)
        rrect(d, x - 160, 430, x + 160, 470, 20, rgba(DARK, k))
        if kk > 0.02: rrect(d, x - 160, 430, x - 160 + 320 * v * kk, 470, 20, rgba(CO2C if i == 0 else HYDRO, k))
        text_c(d, x, 482, "much more CO₂" if i == 0 else "far less CO₂", 22, rgba(WHITE, k))
    b = pop(lt, sent_t("range_why", 2))
    if b > 0:
        bb = clamp(b)
        car_icon(d, 1250, 420, 1.0, EVC, bb)
        label_pill(d, 1250, 500, "CARBON DEBT", RED, bb, 28, WHITE)
        text_c(d, 1250, 300, "−", 80, rgba(RED, bb), BLACK)

# ======================= 02 MINING =======================
def vis_mine_map(d, lt, t, dur):
    cam_path(lt, [(0, 1.15, 750, 360), (dur, 1.0, 750, 360)])
    els = [("Li", "LITHIUM", 3, (214, 170, 100)), ("Ni", "NICKEL", 28, (150, 200, 160)), ("Co", "COBALT", 27, (110, 150, 255))]
    for i, (sym, n, num, col) in enumerate(els):
        k = pop(lt, 0.3 + i * 0.45)
        if k > 0: element_tile(d, 330 + i * 320 - 95, 170, sym, n, num, col, clamp(k), 200)
    b = appear(lt, sent_t("mine_map", 1))
    if b > 0:
        poly(d, [(250, 600), (520, 470), (640, 540), (780, 440), (1000, 560), (1250, 480), (1250, 640), (250, 640)], rgba((60, 54, 46), b))
        for k in range(4): line(d, [(320 + k * 230, 640), (380 + k * 230, 520)], rgba((110, 98, 80), b), 6)
        text_c(d, CX, 650, "NOT PRETTY", 28, rgba(CO2C, b), BLACK)

def vis_lithium_water(d, lt, t, dur):
    cam_path(lt, [(0, 1.25, 600, 340), (dur * 0.6, 1.0, 750, 360)])
    a = appear(lt, 0)
    rrect(d, 60, 60, 900, 600, 20, rgba((70, 60, 50), a))
    cols = [(80, 200, 220), (110, 220, 200), (160, 230, 190), (210, 240, 170), (240, 235, 160), (230, 220, 200)]
    for r in range(3):
        for c in range(4):
            k = appear(lt, 0.3 + (r * 4 + c) * 0.12)
            x0 = 90 + c * 200; y0 = 90 + r * 165
            col = cols[(r + c) % 6]
            rrect(d, x0, y0, x0 + 180, y0 + 145, 10, rgba(col, k * 0.9), rgba((230, 230, 220), k * 0.6), 3)
            sh = 0.5 + 0.5 * math.sin(t * 1.5 + r + c)
            line(d, [(x0 + 20, y0 + 40 + 10 * sh), (x0 + 150, y0 + 30 + 10 * sh)], rgba(WHITE, 0.3 * k), 3)
    text_c(d, 480, 610, "LITHIUM EVAPORATION PONDS · ATACAMA, CHILE", 22, rgba(WHITE, a), BLACK)
    b = appear(lt, sent_t("lithium_water", 1))
    if b > 0:
        kk = ease_inout((lt - sent_t("lithium_water", 1)) / 2.2)
        panel(d, 960, 80, 1450, 600, b)
        for i in range(12):
            r, c = divmod(i, 4)
            drop(d, 1035 + c * 110, 160 + r * 90, 1.0, WATER, b * clamp(kk * 12 - i))
        big_text(d, 1205, 440, f"~{int(150000 * kk):,} L", 62, WATER, b)
        text_c(d, 1205, 520, "fresh water per tonne of lithium", 22, rgba(WHITE, b))
        text_c(d, 1205, 560, "estimate cited by environmental group AIDA", 16, rgba(MUTED, b))

def vis_cobalt(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.04, 750, 360)])
    a = appear(lt, 0)
    k = ease_inout((lt - 0.4) / 1.8)
    cx, cy, R = 400, 340, 230
    circle(d, cx, cy, R, rgba(DARK, a))
    d.pieslice(p(cx - R, cy - R, cx + R, cy + R), -90, -90 + 270 * k, fill=rgba((110, 150, 255), a))
    circle(d, cx, cy, R * 0.55, rgba(BG, a))
    big_text(d, cx, cy - 50, f"~{int(75 * k)}%", 70, WHITE, a)
    text_c(d, cx, cy + 600 - 600 + 36, "of world cobalt", 22, rgba(MUTED, a))
    text_c(d, cx, cy + R + 24, "DEMOCRATIC REPUBLIC OF CONGO", 24, rgba((110, 150, 255), a), BLACK)
    b = appear(lt, sent_t("cobalt", 1) - 0.8)
    if b > 0:
        rrect(d, 780, 160, 1440, 520, 28, rgba(PANEL, b), rgba(RED, b), 4)
        poly(d, [(860, 250), (820, 320), (900, 320)], rgba(RED, b)); text_c(d, 860, 268, "!", 40, rgba(WHITE, b), BLACK)
        text_l(d, 930, 220, "HUMAN RIGHTS GROUPS", 30, rgba(RED, b), BLACK)
        text_l(d, 930, 262, "have documented child labor", 26, rgba(WHITE, b))
        text_l(d, 930, 300, "at some small, informal mining sites", 26, rgba(WHITE, b))
        text_l(d, 820, 420, "e.g. Amnesty International reporting", 20, rgba(MUTED, b))

def battery_cells(d, x, y, w, h, tiles, a):
    battery_icon(d, x, y, w, h, 0, ACC, a, WHITE)
    for i, (sym, col, on) in enumerate(tiles):
        tx = x + 24 + i * ((w - 40) / len(tiles))
        rrect(d, tx, y + 24, tx + (w - 60) / len(tiles), y + h - 24, 12, rgba(col if on else DARK, a), rgba(col, a), 3)
        text_c(d, tx + (w - 60) / len(tiles) / 2, y + h / 2 - 30, sym, 46, rgba(BG if on else MUTED, a), BLACK)
        if not on:
            line(d, [(tx + 6, y + h - 30), (tx + (w - 60) / len(tiles) - 6, y + 30)], rgba(RED, a), 6)

def vis_lfp(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, 370, 40, "NMC BATTERY", 30, rgba(WHITE, a), BLACK)
    battery_cells(d, 120, 100, 500, 190, [("Ni", (150, 200, 160), 1), ("Mn", (190, 170, 220), 1), ("Co", (110, 150, 255), 1)], a)
    b = appear(lt, 0.8)
    text_c(d, 1130, 40, "LFP BATTERY", 30, rgba(ACC, b), BLACK)
    battery_cells(d, 880, 100, 500, 190, [("Li", (214, 170, 100), 1), ("Fe", (200, 120, 90), 1), ("P", (230, 200, 120), 1)], b)
    c = appear(lt, 1.6)
    if c > 0:
        label_pill(d, 1130, 320, "NO COBALT · NO NICKEL", ACC, c, 26)
    e = appear(lt, sent_t("lfp", 1))
    if e > 0:
        kk = ease_inout((lt - sent_t("lfp", 1)) / 1.6)
        panel(d, 260, 420, 1240, 680, e)
        text_c(d, CX, 438, "AVERAGE COBALT PER BATTERY-ELECTRIC CAR · 2025", 24, rgba(MUTED, e), BLACK)
        v = 4.34 - (4.34 - 3.3) * kk
        rrect(d, 320, 500, 1180, 560, 30, rgba(DARK, e))
        rrect(d, 320, 500, 320 + 860 * v / 4.34, 560, 30, rgba((110, 150, 255), e))
        text_l(d, 340, 508, f"{v:.1f} kg", 34, rgba(BG, e), BLACK)
        big_text(d, 1050, 590, f"−{int(24 * kk)}%", 52, ACC, e)
        text_l(d, 320, 610, "Source: Adamas Intelligence", 18, rgba(MUTED, e))

# ======================= 03 TAILPIPE =======================
def gas_can(d, x, y, s, a=1.0):
    rrect(d, x - 60 * s, y - 70 * s, x + 60 * s, y + 80 * s, 16 * s, rgba(RED, a))
    rrect(d, x - 30 * s, y - 100 * s, x + 10 * s, y - 70 * s, 6 * s, rgba(RED, a))
    line(d, [(x + 20 * s, y - 85 * s), (x + 60 * s, y - 115 * s)], rgba((200, 60, 60), a), 10 * s)
    rrect(d, x - 40 * s, y - 40 * s, x + 40 * s, y + 50 * s, 8 * s, None, rgba((255, 160, 160), a), 4)
    text_c(d, x, y - 12 * s, "1 GAL", 24 * s, rgba(WHITE, a), BLACK)

def vis_gallon(d, lt, t, dur):
    cam_path(lt, [(0, 1.2, 500, 380), (dur, 1.0, 750, 360)])
    a = appear(lt, 0)
    gas_can(d, 380, 380, 1.6, a)
    k = ease_out((lt - 0.8) / 1.4)
    if k > 0:
        cloud(d, 900 + 60 * k, 320 - 20 * k, 1.6 + 0.9 * k, (90, 96, 108), 0.9 * k, t)
        big_text(d, 960, 280, f"{8.9 * k:.1f} kg", 70, WHITE, k)
        text_c(d, 960, 370, "CO₂", 40, rgba(CO2C, k), BLACK)
        arrow(d, 520, 380, 700, 360, MUTED, 6, k, 24)
    b = appear(lt, sent_t("gallon", 1))
    if b > 0: text_r(d, 1460, 680, "Source: US EPA (8,887 g CO₂ per gallon)", 18, rgba(MUTED, b))

def vis_mountain(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.08, 820, 380)])
    a = appear(lt, 0)
    k = ease_inout((lt - 0.4) / (dur * 0.5))
    n = int(5247 * k)
    panel(d, 50, 60, 520, 300, a)
    text_c(d, 285, 80, "FUEL BURNED · 170,000 MI @ 33 MPG", 18, rgba(MUTED, a), BLACK)
    big_text(d, 285, 130, f"{n:,} gal", 70, WHITE, a)
    # gallon stack
    for i in range(int(60 * k)):
        r, c = divmod(i, 12)
        rrect(d, 70 + c * 37, 600 - r * 52, 100 + c * 37, 640 - r * 52, 5, rgba(RED, 0.85 * a))
    m = appear(lt, sent_t("mountain", 2))
    if m > 0:
        kk = ease_inout((lt - sent_t("mountain", 2)) / 1.8)
        hgt = 520 * kk
        poly(d, [(620, 650), (1000, 650 - hgt), (1380, 650)], rgba((96, 100, 112), m))
        poly(d, [(860, 650 - hgt * 0.63), (1000, 650 - hgt), (1140, 650 - hgt * 0.63)], rgba((140, 146, 158), m))
        big_text(d, 1000, 650 - hgt - 110, f"~{int(47 * kk)} t CO₂", 56, CO2C, m)
        text_c(d, 1000, 660, "from the tailpipe alone", 22, rgba(WHITE, m))
        if kk > 0.95:
            rrect(d, 1290, 520, 1340, 650, 6, rgba(ACC, m))
            text_c(d, 1315, 470, "EV battery", 18, rgba(ACC, m), BLACK)
            text_c(d, 1315, 494, "2.5–16 t", 18, rgba(ACC, m), BLACK)

def vis_oil_chain(d, lt, t, dur):
    cam_path(lt, [(0, 1.3, 260, 360), (dur * 0.75, 1.0, 750, 360), (dur, 1.0, 750, 360)])
    steps = ["DRILL", "SHIP", "REFINE", "TRUCK", "PUMP"]
    for i, n in enumerate(steps):
        k = pop(lt, 0.2 + i * dur * 0.14)
        if k <= 0: continue
        aa = clamp(k); x = 170 + i * 290; y = 330
        circle(d, x, y, 100 * aa, rgba(PANEL, aa), rgba(GAS, aa), 4)
        if i == 0:
            poly(d, [(x - 40, y + 50), (x, y - 60), (x + 40, y + 50)], None); line(d, [(x - 40, y + 50), (x, y - 60), (x + 40, y + 50)], rgba(GAS, aa), 8)
            line(d, [(x - 25, y + 10), (x + 25, y + 10)], rgba(GAS, aa), 6)
        elif i == 1:
            poly(d, [(x - 70, y + 10), (x + 70, y + 10), (x + 50, y + 50), (x - 50, y + 50)], rgba(GAS, aa))
            rrect(d, x - 40, y - 30, x + 10, y + 10, 4, rgba(GAS, aa))
        elif i == 2: factory(d, x - 10, y + 50, 0.55, GAS, aa, t, smoke=False)
        elif i == 3:
            rrect(d, x - 70, y - 30, x + 30, y + 30, 20, rgba(GAS, aa)); rrect(d, x + 34, y - 20, x + 70, y + 30, 6, rgba(GAS, aa))
            circle(d, x - 40, y + 38, 14, rgba(BG, aa)); circle(d, x + 40, y + 38, 14, rgba(BG, aa))
        else:
            rrect(d, x - 35, y - 55, x + 35, y + 55, 10, rgba(GAS, aa)); rrect(d, x - 20, y - 40, x + 20, y - 10, 4, rgba(BG, aa))
        text_c(d, x, y + 120, n, 26, rgba(GAS, aa), BLACK)
        co2_puffs(d, x + 40, y - 90, t + i, aa, 4, 20, 90, CO2C, 10)
        if i: arrow(d, x - 290 + 105, y, x - 105, y, MUTED, 5, aa, 20)
    c = appear(lt, dur * 0.8)
    cam()
    if c > 0: label_pill(d, CX, 620, "EVEN MORE EMISSIONS BEFORE IT'S BURNED", CO2C, c, 26)

# ======================= 04 BREAK-EVEN =======================
MAXMI = 173000
def cum_chart(d, lt, a, k_draw, show_cross=0.0, gap=0.0, x_max=MAXMI, t=0.0, labels=True):
    X0, Y0, X1, Y1 = 170, 80, 1400, 590
    chart_axes(d, X0, Y0, X1, Y1, "MILES DRIVEN", "TOTAL CO₂ (tonnes)", a)
    def X(mi): return X0 + (X1 - X0) * mi / x_max
    def Yt(tn): return Y1 - (Y1 - Y0 - 30) * tn / 70
    for mi in (0, 50000, 100000, 150000):
        if mi <= x_max: text_c(d, X(mi), Y1 + 52, f"{mi // 1000}k", 20, rgba(MUTED, a))
    for tn in (0, 20, 40, 60):
        text_r(d, X0 - 12, Yt(tn) - 12, f"{tn}", 20, rgba(MUTED, a))
    # gas: 7 t to build + ~0.27 t / 1000 mi (tailpipe + upstream); EV: 11 t to build + ~0.11 t/1000 mi on US grid
    # (illustrative slopes chosen so the lines cross at 13,500 mi, matching the Argonne/Reuters result)
    # illustrative model: gas 7 t to build + 0.336 t/1000 mi (tailpipe + fuel supply);
    # EV 10.5 t to build; slope set so the lines cross at 13,500 mi (Argonne/Reuters) ->
    # lifetime EV ~24 t vs gas ~65 t, i.e. ~63% lower (inside ICCT's US range of 60-68%)
    g0, gs = 7.0, 0.336; e0 = 10.5
    es = gs - (e0 - g0) / 13.5
    gas = [(X(mi), Yt(g0 + gs * mi / 1000)) for mi in range(0, x_max + 1, 2000)]
    ev = [(X(mi), Yt(e0 + es * mi / 1000)) for mi in range(0, x_max + 1, 2000)]
    if gap > 0:
        upto = int(len(gas) * gap)
        if upto > 8:
            pts = ev[7:upto] + gas[7:upto][::-1]
            poly(d, pts, rgba(ACC, 0.16 * a))
    glow_line(d, partial(gas, k_draw), GAS, a, 6)
    glow_line(d, partial(ev, k_draw), EVC, a, 6)
    if k_draw > 0.02 and labels:
        gx, gy = partial(gas, k_draw)[-1]; ex, ey = partial(ev, k_draw)[-1]
        label_pill(d, gx - 40, gy - 60, "GAS CAR", GAS, a, 20); label_pill(d, ex - 40, ey + 16, "ELECTRIC", EVC, a, 20)
    if show_cross > 0:
        cx_, cy_ = X(13500), Yt(g0 + gs * 13.5)
        circle(d, cx_, cy_, 16 + 6 * math.sin(t * 5), None, rgba(WHITE, show_cross), 5)
        line(d, [(cx_, cy_ + 20), (cx_, Y1)], rgba(WHITE, 0.6 * show_cross), 3)
    return X, Yt

def vis_race(d, lt, t, dur):
    a = appear(lt, 0)
    k = ease_inout((lt - 0.4) / 1.4) * 0.03
    cum_chart(d, lt, a, max(k, 0.0001), x_max=MAXMI)
    b = appear(lt, 1.0)
    if b > 0:
        label_pill(d, 420, 130, "EV STARTS HIGHER: CARBON DEBT", RED, b, 22, WHITE)
    c = appear(lt, sent_t("race", 1))
    if c > 0:
        rrect(d, 900, 110, 1400, 230, 22, rgba(PANEL, c), rgba(DARK, c), 3)
        text_c(d, 1150, 124, "ARGONNE GREET MODEL", 22, rgba(MUTED, c), BLACK)
        text_c(d, 1150, 160, "TESLA MODEL 3  vs  TOYOTA COROLLA", 26, rgba(WHITE, c), BLACK)

def vis_cross(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur * 0.45, 1.0, 750, 360), (dur * 0.75, 2.2, 290, 470), (dur, 2.2, 290, 470)])
    a = appear(lt, 0)
    k = 0.03 + 0.12 * ease_inout((lt - 0.2) / (dur * 0.45))
    cum_chart(d, lt, a, k, show_cross=appear(lt, dur * 0.4), x_max=MAXMI, t=t, labels=lt < dur * 0.45)
    c = appear(lt, dur * 0.42)
    if c > 0:
        cam()
        rrect(d, 40, 560, 330, 690, 20, rgba(PANEL, c), rgba(DARK, c), 2)
        line(d, [(64, 600), (114, 600)], rgba(GAS, c), 8); text_l(d, 130, 586, "GAS CAR", 22, rgba(GAS, c), BLACK)
        line(d, [(64, 650), (114, 650)], rgba(EVC, c), 8); text_l(d, 130, 636, "ELECTRIC", 22, rgba(EVC, c), BLACK)
        rrect(d, 1000, 90, 1460, 260, 26, rgba(PANEL, c), rgba(ACC, c), 4)
        text_c(d, 1230, 104, "BREAK-EVEN · US GRID", 22, rgba(MUTED, c), BLACK)
        big_text(d, 1230, 136, f"{int(13500 * ease_inout((lt - dur * 0.42) / 1.0)):,} mi", 58, ACC, c)
        e = appear(lt, sent_t("cross", 1))
        if e > 0: label_pill(d, 1230, 280, "≈ 1 YEAR OF TYPICAL DRIVING", WHITE, e, 22)

def vis_after(d, lt, t, dur):
    a = appear(lt, 0)
    k = 0.15 + 0.85 * ease_inout((lt - 0.2) / (dur * 0.8))
    cum_chart(d, lt, a, k, show_cross=1.0, gap=k, x_max=MAXMI, t=t)
    c = appear(lt, dur * 0.6)
    if c > 0: label_pill(d, 980, 250, "THE GAP KEEPS GROWING", ACC, c, 26)
    text_r(d, 1400, 690, "illustrative model matching the 13,500-mile break-even", 16, rgba(MUTED, a))

# ======================= 05 GRID =======================
def plug(d, x, y, s, col, a=1.0):
    rrect(d, x - 30 * s, y - 34 * s, x + 30 * s, y + 20 * s, 12 * s, rgba(col, a))
    line(d, [(x - 13 * s, y - 34 * s), (x - 13 * s, y - 60 * s)], rgba(col, a), 9 * s)
    line(d, [(x + 13 * s, y - 34 * s), (x + 13 * s, y - 60 * s)], rgba(col, a), 9 * s)
    line(d, [(x, y + 20 * s), (x, y + 60 * s)], rgba(col, a), 10 * s)

def source_icon(d, x, y, kind, a, t):
    if kind == "coal":
        factory(d, x - 10, y + 50, 0.55, COAL, a, t, True, (80, 76, 72))
    elif kind == "hydro":
        poly(d, [(x - 70, y + 50), (x - 40, y - 50), (x + 40, y - 50), (x + 70, y + 50)], rgba((120, 130, 145), a))
        for k in range(3): line(d, [(x - 30 + k * 30, y + 50), (x - 30 + k * 30 + 8 * math.sin(t * 4 + k), y + 80)], rgba(HYDRO, a), 6)
    elif kind == "solar":
        circle(d, x + 40, y - 40, 22, rgba(SOLAR, a)); solar_panel(d, x - 10, y + 40, 1.0, a)
    else:
        line(d, [(x, y + 60), (x, y - 50)], rgba(WHITE, a), 6)
        for k in range(3):
            ang = t * 3 + k * 2.094
            line(d, [(x, y - 50), (x + math.cos(ang) * 55, y - 50 + math.sin(ang) * 55)], rgba(WHITE, a), 6)

def vis_grid_map(d, lt, t, dur):
    cam_path(lt, [(0, 1.15, 750, 380), (dur, 1.0, 750, 360)])
    a = appear(lt, 0)
    car_icon(d, CX, 520, 1.3, EVC, a)
    plug(d, CX, 380, 1.0, WHITE, a)
    srcs = [("COAL", "coal", 200), ("HYDRO", "hydro", 560), ("SOLAR", "solar", 940), ("WIND", "wind", 1300)]
    for i, (n, kind, x) in enumerate(srcs):
        k = appear(lt, 0.4 + i * 0.3)
        source_icon(d, x, 150, kind, k, t)
        text_c(d, x, 240, n, 24, rgba(WHITE, k), BLACK)
        pts = [(x, 270), (x, 300), (CX, 320)]
        line(d, pts, rgba(DARK, k), 4)
        flow(d, pts, t + i, COAL if kind == "coal" else ACC, k, 3, 6, 0.6, False)
    b = appear(lt, dur * 0.55)
    if b > 0: label_pill(d, CX, 640, "ONLY AS CLEAN AS ITS ELECTRICITY", ACC, b, 26)

def vis_grid_bars(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, CX, 30, "MILES UNTIL THE EV BREAKS EVEN", 36, rgba(WHITE, a), BLACK)
    rows = [("NORWAY · HYDRO", 8400, HYDRO, 0.3), ("UNITED STATES · AVERAGE", 13500, ACC, 0.9), ("100% COAL GRID", 78700, COAL, sent_t("grid_bars", 1))]
    for i, (n, v, col, at) in enumerate(rows):
        k = appear(lt, at)
        if k <= 0: continue
        kk = ease_inout((lt - at) / 1.5)
        y = 140 + i * 170
        text_l(d, 120, y, n, 28, rgba(col, k), BLACK)
        rrect(d, 120, y + 50, 1380, y + 110, 30, rgba(DARK, k))
        w = 1260 * v / 80000 * kk
        if w > 40: rrect(d, 120, y + 50, 120 + w, y + 110, 30, rgba(col, k))
        text_l(d, 140 + w, y + 58, f" {int(v * kk):,} mi", 34, rgba(WHITE, k), BLACK)
    text_r(d, 1460, 690, "Source: Reuters analysis with Argonne GREET model", 18, rgba(MUTED, a))

def vis_states(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.05, 750, 350)])
    cards = [("WASHINGTON", "hydro-powered", "−61%", "vs a hybrid", HYDRO, "hydro", 0.3), ("WEST VIRGINIA", "coal-heavy", "WORSE", "than a hybrid · still beats gas", COAL, "coal", sent_t("states", 2) - 0.3)]
    for i, (n, sub, big, s2, col, kind, at) in enumerate(cards):
        k = pop(lt, at)
        if k <= 0: continue
        aa = clamp(k); x0 = 90 + i * 680
        rrect(d, x0, 70, x0 + 640, 640, 30, rgba(PANEL, aa), rgba(col, aa), 4)
        source_icon(d, x0 + 320, 200, kind, aa, t)
        text_c(d, x0 + 320, 300, n, 40, rgba(WHITE, aa), BLACK)
        text_c(d, x0 + 320, 350, sub, 24, rgba(MUTED, aa))
        big_text(d, x0 + 320, 410, big, 90, ACC if i == 0 else CO2C, aa)
        text_c(d, x0 + 320, 540, s2, 24, rgba(WHITE, aa))
    text_r(d, 1460, 690, "Source: MIT Insights Into Future Mobility", 18, rgba(MUTED, appear(lt, 0.5)))

def vis_cleaner(d, lt, t, dur):
    a = appear(lt, 0)
    X0, Y0, X1, Y1 = 170, 90, 1380, 560
    chart_axes(d, X0, Y0, X1, Y1, "YEARS OF OWNERSHIP", "GRID CARBON", a)
    k = ease_inout((lt - 0.3) / (dur * 0.6))
    pts = [(X0 + (X1 - X0) * u / 40, Y0 + 40 + (Y1 - Y0 - 60) * (1 - math.exp(-u / 22)) ) for u in range(41)]
    glow_line(d, partial(pts, k), ACC, a, 7)
    ex, ey = partial(pts, max(k, 0.01))[-1]
    col = mix(CO2C, ACC, k)
    car_icon(d, ex, ey - 40, 0.55, col, a)
    b = appear(lt, sent_t("cleaner", 1))
    if b > 0:
        label_pill(d, 760, 600, "EV: GETS CLEANER WITH AGE", ACC, b, 24)
        label_pill(d, 760, 652 - 0, "GAS CAR: NEVER DOES", GAS, appear(lt, sent_t("cleaner", 2)), 22)
    text_r(d, 1460, 30, "illustrative", 16, rgba(MUTED, a))

# ======================= 06 MYTHS =======================
def myth_header(d, n, txt, lt, a):
    rrect(d, 60, 30, 240, 100, 20, rgba(RED, a)); text_c(d, 150, 44, f"MYTH {n}", 30, rgba(WHITE, a), BLACK)
    text_l(d, 270, 42, txt, 34, rgba(WHITE, a), BLACK)

def verdict_stamp(d, x, y, txt, col, k):
    if k <= 0: return
    s = 1.6 - 0.6 * clamp(k)
    rrect(d, x - 190 * s, y - 50 * s, x + 190 * s, y + 50 * s, 16 * s, None, rgba(col, clamp(k)), 8 * s)
    text_c(d, x, y - 32 * s, txt, 52 * s, rgba(col, clamp(k)), BLACK)

def vis_myth_battery(d, lt, t, dur):
    a = appear(lt, 0)
    myth_header(d, 1, "“The battery dies after a few years”", lt, a)
    b = appear(lt, sent_t("myth_battery", 2) - 0.4)
    if b > 0:
        rnd = random.Random(4); kk = ease_inout((lt - sent_t("myth_battery", 2) + 0.4) / 1.8)
        n = int(400 * kk)
        for i in range(n):
            r, c = divmod(i, 25)
            hit = i in (37, 141, 222, 309, 377, 96)
            circle(d, 140 + c * 34, 170 + r * 30, 11, rgba(RED if hit else ACC, b * (1 if hit else 0.75)))
        text_l(d, 140, 660 - 0, "each dot = 37 EVs · Recurrent data, 15,000 EVs", 18, rgba(MUTED, b))
        panel(d, 1020, 170, 1450, 520, b)
        big_text(d, 1235, 200, f"{1.5 * kk:.1f}%", 96, RED, b)
        text_c(d, 1235, 340, "needed a battery", 26, rgba(WHITE, b)); text_c(d, 1235, 376, "replacement", 26, rgba(WHITE, b))
        text_c(d, 1235, 420, "(outside of recalls)", 20, rgba(MUTED, b))
    verdict_stamp(d, 1235, 600, "BUSTED", ACC, pop(lt, dur * 0.85))

def vis_myth_dust(d, lt, t, dur):
    a = appear(lt, 0)
    myth_header(d, 2, "“Heavier EVs make more dust”", lt, a)
    k = appear(lt, sent_t("myth_dust", 1))
    if k > 0:
        rrect(d, 80, 140, 700, 600, 26, rgba(PANEL, k), rgba(GAS, k), 3)
        circle(d, 270, 360, 130, rgba((20, 20, 22), k)); circle(d, 270, 360, 80, rgba((70, 76, 88), k))
        co2_puffs(d, 270, 500, t, k, 8, 100, 120, (170, 160, 150), 12)
        text_c(d, 520, 270, "TIRES", 34, rgba(WHITE, k), BLACK)
        arrow(d, 520, 420, 520, 330, GAS, 10, k, 30)
        text_c(d, 520, 440, "can wear", 22, rgba(WHITE, k)); text_c(d, 520, 472, "faster", 22, rgba(WHITE, k))
    b = appear(lt, sent_t("myth_dust", 2))
    if b > 0:
        rrect(d, 760, 140, 1440, 600, 26, rgba(PANEL, b), rgba(ACC, b), 3)
        text_c(d, 1100, 160, "BRAKE DUST (PM2.5, mg/km)", 26, rgba(WHITE, b), BLACK)
        kk = ease_inout((lt - sent_t("myth_dust", 3)) / 1.4)
        for i, (lab, lo, hi, col) in enumerate((("GAS CAR", 2.0, 3.0, GAS), ("ELECTRIC", 0.3, 1.2, ACC))):
            x = 950 + i * 300
            hh = 300 * hi / 3.0 * kk
            rrect(d, x - 70, 540 - 300, x + 70, 540, 16, rgba(DARK, b))
            if hh > 6: rrect(d, x - 70, 540 - hh, x + 70, 540, 16, rgba(col, b))
            text_c(d, x, 550, lab, 22, rgba(col, b), BLACK)
            text_c(d, x, 540 - hh - 40, f"{lo}–{hi}", 26, rgba(WHITE, b * clamp(kk * 3)), BLACK)
        text_c(d, 1100, 610, "Ricardo test: VW Caddy vs VW e-Golf", 16, rgba(MUTED, b))
    verdict_stamp(d, 380, 640, "PARTLY TRUE", ACC2, pop(lt, dur * 0.88))

def vis_myth_tailpipe(d, lt, t, dur):
    a = appear(lt, 0)
    myth_header(d, 3, "“EVs just move pollution to power plants”", lt, a)
    b = appear(lt, sent_t("myth_tailpipe", 1))
    if b > 0:
        kk = ease_inout((lt - sent_t("myth_tailpipe", 1)) / 1.8)
        for i, (lab, eff, col) in enumerate((("ELECTRIC CAR", 0.9, ACC), ("GAS ENGINE", 0.3, GAS))):
            y = 190 + i * 220
            text_l(d, 100, y, lab, 30, rgba(col, b), BLACK)
            x0, x1 = 100, 1300
            rrect(d, x0, y + 50, x1, y + 130, 40, rgba((70, 50, 45), b))
            text_r(d, x1 - 24, y + 72, "LOST AS HEAT" if i else "LOST", 22, rgba((220, 150, 130), b), BLACK)
            w = (x1 - x0) * eff * kk
            if w > 40: rrect(d, x0, y + 50, x0 + min(w, (x1 - x0) * 0.86 if i == 0 else w), y + 130, 40, rgba(col, b))
            text_l(d, x0 + 30, y + 70, f"{int(eff * 100 * kk)}% → MOTION", 32, rgba(BG, b), BLACK)
        text_r(d, 1460, 690, "US Dept. of Energy efficiency estimates", 18, rgba(MUTED, b))
    verdict_stamp(d, 1250, 40 + 0, "PARTLY TRUE", ACC2, 0)
    verdict_stamp(d, 1270, 650, "PARTLY TRUE", ACC2, pop(lt, dur * 0.85)) if False else None
    v = pop(lt, dur * 0.85)
    if v > 0: label_pill(d, CX, 640, "SAME FUEL → FAR LESS WASTED", ACC, clamp(v), 26)

# ======================= 07 END =======================
def vis_second_life(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.06, 820, 360)])
    a = appear(lt, 0)
    car_icon(d, 260, 420, 1.3, (120, 130, 145), a)
    k = ease_inout((lt - 0.8) / 1.6)
    bx = lerp(200, 720, k); by = lerp(440, 470, k)
    battery_icon(d, bx - 80, by - 40, 160, 80, 0.72, ACC, a)
    text_c(d, bx, by + 50, "72% health", 20, rgba(WHITE, a), BLACK)
    b = appear(lt, sent_t("second_life", 2))
    if b > 0:
        house(d, 1150, 470, 1.6, (150, 160, 175), b)
        solar_panel(d, 1100, 300 + 20, 1.0, b); circle(d, 1340, 150, 40, rgba(SOLAR, b))
        for k2 in range(6):
            ang = k2 * 1.047 + t * 0.4
            line(d, [(1340 + math.cos(ang) * 52, 150 + math.sin(ang) * 52), (1340 + math.cos(ang) * 72, 150 + math.sin(ang) * 72)], rgba(SOLAR, b), 5)
        flow(d, [(1100, 330), (980, 420), (800, 470)], t, SOLAR, b, 4, 7, 0.6, False)
        label_pill(d, 1000, 600, "SECOND LIFE: HOME SOLAR STORAGE", ACC, b, 24)

def vis_recycle(d, lt, t, dur):
    a = appear(lt, 0)
    cx, cy, R = 560, 360, 220
    ang0 = t * 0.6
    arc(d, cx, cy, R, math.degrees(ang0), math.degrees(ang0) + 300, rgba(ACC, a), 14)
    nodes = [("OLD BATTERY", -90, (150, 160, 175)), ("SHRED & REFINE", 30, ACC2), ("NEW BATTERY", 150, ACC)]
    for i, (n, deg, col) in enumerate(nodes):
        k = pop(lt, 0.3 + i * 0.6)
        if k <= 0: continue
        x = cx + math.cos(math.radians(deg)) * R; y = cy + math.sin(math.radians(deg)) * R
        circle(d, x, y, 70 * clamp(k), rgba(PANEL, clamp(k)), rgba(col, clamp(k)), 4)
        battery_icon(d, x - 34, y - 18, 60, 36, 0.3 if i == 0 else 0.9, col, clamp(k)) if i != 1 else None
        if i == 1:
            for j in range(5): line(d, [(x - 30 + j * 15, y - 25), (x - 22 + j * 15, y + 25)], rgba(col, clamp(k)), 5)
        text_c(d, x, y + 80, n, 22, rgba(col, clamp(k)), BLACK)
    b = appear(lt, sent_t("recycle", 1))
    if b > 0:
        kk = ease_inout((lt - sent_t("recycle", 1)) / 1.5)
        panel(d, 960, 140, 1450, 540, b)
        text_c(d, 1205, 160, "REDWOOD MATERIALS PILOT", 22, rgba(MUTED, b), BLACK)
        big_text(d, 1205, 210, f"{int(95 * kk)}%+", 110, ACC, b)
        text_c(d, 1205, 360, "of key metals recovered", 26, rgba(WHITE, b))
        tiles = [("Li", (214, 170, 100)), ("Ni", (150, 200, 160)), ("Co", (110, 150, 255)), ("Cu", (214, 140, 82))]
        for j, (sym, col) in enumerate(tiles):
            k2 = pop(lt, sent_t("recycle", 1) + 0.6 + j * 0.15)
            if k2 > 0:
                rrect(d, 1010 + j * 110, 420, 1090 + j * 110, 500, 14, rgba(col, clamp(k2)))
                text_c(d, 1050 + j * 110, 436, sym, 36, rgba(BG, clamp(k2)), BLACK)
    c = appear(lt, sent_t("recycle", 2))
    if c > 0:
        cam(); label_pill(d, CX, 650, "THE MINE OF THE FUTURE?", ACC, c, 26)

# ======================= 08 VERDICT =======================
def vis_verdict_bars(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, CX, 26, "LIFETIME GREENHOUSE GAS: EV vs GAS CAR", 34, rgba(WHITE, a), BLACK)
    rows = [("EUROPE", 66, 69, 1), ("UNITED STATES", 60, 68, 2), ("CHINA", 37, 45, 3), ("INDIA", 19, 34, 4)]
    for i, (n, lo, hi, si) in enumerate(rows):
        at = sent_t("verdict_bars", 1) + i * 1.9 if i else sent_t("verdict_bars", 1) - 0.5
        k = appear(lt, at)
        if k <= 0: continue
        kk = ease_inout((lt - at) / 1.2)
        y = 110 + i * 135
        text_l(d, 90, y + 30, n, 30, rgba(WHITE, k), BLACK)
        x0, x1 = 440, 1340
        rrect(d, x0, y + 20, x1, y + 80, 30, rgba(DARK, k))
        wl = (x1 - x0) * lo / 100 * kk; wh = (x1 - x0) * hi / 100 * kk
        if wh > 30: rrect(d, x0, y + 20, x0 + wh, y + 80, 30, rgba(ACC, 0.45 * k))
        if wl > 30: rrect(d, x0, y + 20, x0 + wl, y + 80, 30, rgba(ACC, k))
        text_l(d, x0 + wh + 18, y + 30, f"−{int(lo * kk)}–{int(hi * kk)}%", 32, rgba(ACC, k), BLACK)
    text_r(d, 1460, 690, "Source: ICCT global lifecycle study (2021)", 18, rgba(MUTED, a))

def vis_half(d, lt, t, dur):
    cam_path(lt, [(0, 1.1, 750, 380), (dur, 1.0, 750, 360)])
    a = appear(lt, 0)
    k = ease_inout((lt - 0.5) / 1.6)
    for i, (lab, v, col, ev) in enumerate((("GAS CAR", 1.0, GAS, False), ("ELECTRIC CAR", 0.5, ACC, True))):
        x = 520 + i * 460
        hh = 420 * v * k
        rrect(d, x - 120, 600 - 420, x + 120, 600, 22, rgba(DARK, a))
        if hh > 10: rrect(d, x - 120, 600 - hh, x + 120, 600, 22, rgba(col, a))
        car_icon(d, x, 650, 0.6, col, a, ev)
        text_c(d, x, 600 - hh - 60, "100%" if i == 0 else "≈ 50%", 40, rgba(WHITE, a * clamp(k * 2)), BLACK)
    big_text(d, CX, 40, "ABOUT HALF", 64, ACC, appear(lt, 1.6))
    text_r(d, 1460, 690, "Source: IEA Global EV Outlook 2024", 18, rgba(MUTED, a))

def vis_caveats(d, lt, t, dur):
    cards = [("COAL-HEAVY GRIDS", "smaller benefit", "coal", 0), ("GIANT BATTERIES", "longer payback", "big", 1), ("MINING", "must get cleaner & fairer", "mine", 2)]
    big_text(d, CX, 30, "NOT A FREE PASS", 56, CO2C, appear(lt, 0))
    for i, (n, s2, kind, si) in enumerate(cards):
        at = sent_t("caveats", si + 1) - 0.2
        k = pop(lt, at)
        if k <= 0: continue
        aa = clamp(k); x0 = 70 + i * 470
        rrect(d, x0, 140, x0 + 430, 640, 28, rgba(PANEL, aa), rgba(CO2C, aa), 3)
        cx = x0 + 215
        if kind == "coal": factory(d, cx, 380, 1.0, COAL, aa, t, True, (80, 76, 72))
        elif kind == "big":
            rrect(d, cx - 150, 260, cx + 150, 380, 20, rgba((120, 130, 145), aa))
            battery_icon(d, cx - 120, 280, 230, 80, 1.0, CO2C, aa)
        else:
            poly(d, [(cx - 120, 380), (cx - 40, 260), (cx + 10, 320), (cx + 60, 270), (cx + 130, 380)], rgba((150, 120, 80), aa))
        text_c(d, cx, 440, n, 30, rgba(WHITE, aa), BLACK)
        text_c(d, cx, 490, s2, 24, rgba(MUTED, aa))

def vis_final(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.05, 750, 350)])
    a = appear(lt, 0)
    tilt = 0.22 * ease_out((lt - 0.6) / 1.6)
    scales(d, CX, 210, -tilt, a, "ELECTRIC", "GASOLINE", EVC, GAS)
    b = pop(lt, sent_t("final", 1))
    if b > 0: big_text(d, CX, 30, "YES — ON ALMOST EVERY GRID", 52, ACC, clamp(b))
    c = pop(lt, sent_t("final", 2))
    if c > 0: label_pill(d, CX, 120, "BUT NOT PERFECTLY GREEN", CO2C, clamp(c), 28)

def vis_question(d, lt, t, dur):
    cam(1.0 + 0.04 * clamp(lt / dur), 750, 360)
    k = pop(lt, 0.1)
    big_text(d, CX, 50, "DID THIS CHANGE", 60, WHITE, clamp(k))
    big_text(d, CX, 125, "YOUR MIND?", 60, ACC, clamp(k))
    opts = [("CHANGED MY MIND", ACC), ("CONFIRMED IT", AIR)]
    for i, (s_, col) in enumerate(opts):
        kk = pop(lt, 0.9 + i * 0.5)
        if kk <= 0: continue
        x = 480 + i * 540; aa = clamp(kk)
        g = 0.5 + 0.5 * math.sin(t * 3 + i * 2)
        rrect(d, x - 240, 270, x + 240, 450, 30, rgba(PANEL, aa), rgba(col, (0.5 + 0.5 * g) * aa), 4)
        text_c(d, x, 335, s_, 38, rgba(col, aa), BLACK)
    c = appear(lt, sent_t("question", 1))
    if c > 0: label_pill(d, CX, 520, "TELL ME IN THE COMMENTS", ACC, c, 30)
    e = appear(lt, sent_t("question", 2))
    if e > 0:
        bolt(d, CX - 190, 650, 0.45, rgba(ACC, e))
        text_l(d, CX - 160, 620, "SUBSCRIBE TO EV DRIVE", 34, rgba(WHITE, e), BLACK)

VIS.update({k[4:]: v for k, v in list(globals().items()) if k.startswith("vis_") and callable(v)})
