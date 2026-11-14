# Scenes for "Two brothers, same EV" — runs inside tools/render_story.py globals.
GY = 1080                      # ground line
SAM, LEO = (120, 200, 90), ORANGE      # shirt colours: Sam = green cap, Leo = orange, spiky hair
CARC = (86, 156, 255)
POPS = []
def _s(name): return next(x for x in scenes if x["visual"] == name)
def _pop_at(name, k, dt=0.0): POPS.append(_s(name)["sentences"][min(k, len(_s(name)["sentences"]) - 1)]["start"] + dt)

def sky(d, top, bot, horizon=GY):
    for i in range(24):
        rect(d, 0, horizon * i / 24, W, horizon * (i + 1) / 24 + 1, mix(top, bot, i / 23))
def stars(d, t):
    import random; rnd = random.Random(4)
    for i in range(40):
        x, y = rnd.uniform(0, W), rnd.uniform(240, 800)
        circ(d, x, y, 2.5 + 1.5 * math.sin(t * 2 + i), (255, 255, 230))
def wallbox(d, x, y):
    rect(d, x - 60, y - 190, x + 60, y - 30, (245, 246, 250), r=22, ol=INK, w=7)
    bolt(d, x, y - 120, 38, LIME)
    circ(d, x, y - 55, 10, GREEN, INK, 3)
def fast_charger(d, x, y, t):
    rect(d, x - 90, y - 520, x + 90, y, (245, 246, 250), r=28, ol=INK, w=8)
    rect(d, x - 64, y - 480, x + 64, y - 300, (30, 36, 60), r=14, ol=INK, w=6)
    bolt(d, x, y - 390, 62, YELLOW)
    rect(d, x - 64, y - 270, x + 64, y - 232, ORANGE, r=10, ol=INK, w=5)
    text(d, x, y - 251, "350 kW", 26, INK)
    rect(d, x - 120, y - 16, x + 120, y + 14, (120, 126, 150), r=8, ol=INK, w=6)
def window_moon(d, x, y, t):
    rect(d, x - 130, y - 130, x + 130, y + 130, (36, 44, 92), r=18, ol=INK, w=8)
    circ(d, x + 40, y - 30, 46, (255, 240, 180), INK, 4); circ(d, x + 62, y - 44, 40, (36, 44, 92))
    for i, (sx, sy) in enumerate([(-70, -60), (-30, 50), (80, 70), (-90, 30)]):
        circ(d, x + sx, y + sy, 4 + 2 * math.sin(t * 3 + i), (255, 255, 230))
    line(d, [(x, y - 130), (x, y + 130)], INK, 6); line(d, [(x - 130, y), (x + 130, y)], INK, 6)

# ---------- 1. hook ----------
_pop_at("hook", 1); _pop_at("hook", 1, 1.3); _pop_at("hook", 2)
def sc_hook(d, lt, t, s):
    room(d, (255, 206, 120), (232, 150, 96), GY, (214, 120, 80))
    rect(d, W / 2 - 5, 0, W / 2 + 5, H, INK)
    k0 = ease(lt / 0.5)
    for i, (cx, shirt, hair) in enumerate([(270, SAM, "cap"), (810, LEO, "spiky")]):
        car(d, cx + (60 if i == 0 else -60), GY + 70 + (1 - k0) * 40, 400, CARC, t, 0, 1 if i == 0 else -1)
        late = lt >= sent(s, 1) + 1.2
        mood = "smile" if (not late or i == 0) else "wow"
        person(d, cx + (-130 if i == 0 else 130), GY + 190, 400, shirt, hair, t, mood, -0.3, 2.6 if not late or i == 0 else 0.3, face=1 if i == 0 else -1)
        text(d, cx, 420, "SAM" if i == 0 else "LEO", 54, WHITE, stroke=8)
    pill(d, W / 2, 300, "SAME CAR", 46, LIME, k=clamp(pop(lt / 0.3)))
    a = lt - sent(s, 1)
    if a > 0:
        pill(d, W / 2, 560, "8 YEARS LATER", 54, YELLOW, k=clamp(pop(a / 0.3)))
        battery(d, 270, 720, 300, 88, GREEN, k=clamp(pop((a - 0.6) / 0.3)))
        battery(d, 810, 720, 300, 88 - 38 * smooth((a - 1.3) / 0.8), mix(GREEN, RED, smooth((a - 1.3) / 0.8)), k=clamp(pop((a - 0.6) / 0.3)))
    b = lt - sent(s, 2)
    if b > 0.02: text(d, 810, 880, "?", 150 * clamp(pop(b / 0.3)), RED, stroke=12)

# ---------- 2. home charging ----------
_pop_at("home", 0, 0.9)
def sc_home(d, lt, t, s):
    room(d, (92, 104, 168), (70, 78, 120), GY, (60, 66, 104))
    window_moon(d, 800, 520, t)
    wallbox(d, 150, 860)
    cx = 620
    px, py = car(d, cx, GY + 130, 640, CARC, t, 0, 1)
    plug = ease((lt - 0.5) / 0.5)
    if plug > 0: cable(d, 150, 800, 150 + (px - 150) * plug, 800 + (py - 800) * plug, 150, (60, 64, 80), t, 0.22, 4, 9)
    person(d, 250, GY + 60, 330, SAM, "cap", t, "smile", -0.2, 1.2 - 0.9 * plug)
    pill(d, W / 2, 300, "SAM · HOME CHARGER", 44, LIME, k=clamp(pop(lt / 0.3)))
    for i in range(3):                                      # zzz
        z = (t * 0.5 + i / 3) % 1
        text(d, 880 + z * 60, 330 + 100 - z * 120, "Z", 30 + 26 * z, (255, 255, 255, int(255 * (1 - z))), stroke=0)
    a = lt - sent(s, 1)
    for i, wd in enumerate(["SLOW", "BORING", "CHEAP"]):
        k = clamp(pop((a - 0.25 - i * 0.55) / 0.25))
        if k > 0: pill(d, 250 + i * 290, 1500, wd, 40, WHITE, k=k)

# ---------- 3. fast charging ----------
_pop_at("fast", 1, 0.5); _pop_at("fast", 2)
def sc_fast(d, lt, t, s):
    sky(d, (255, 170, 110), (255, 226, 160)); circ(d, 860, 420, 90, (255, 244, 200), INK, 5)
    rect(d, 0, GY, W, H, (96, 100, 120)); line(d, [(0, GY), (W, GY)], INK, 7)
    for i in range(6): rect(d, 60 + i * 190 - (t * 0 % 190), GY + 300, 150 + i * 190, GY + 320, (240, 240, 245), r=6)
    fast_charger(d, 170, GY + 90, t)
    go = lt - sent(s, 2) - 0.9
    dx = 1400 * smooth(go / 0.9) ** 2 if go > 0 else 0
    cx = 650 + dx
    px, py = car(d, cx, GY + 150, 640, CARC, t, dx * 0.02, 1)
    if go <= 0:
        cable(d, 250, GY - 250, px, py, 120, (40, 44, 60), t, 1.6, 9, 13, 14)
        person(d, 420, GY + 40, 320, LEO, "spiky", t, "smile", -0.3, 0.9)
    else:
        for i in range(5): line(d, [(cx - 380 - i * 60, GY + 30 - i * 26), (cx - 520 - i * 60, GY + 30 - i * 26)], WHITE, 10)
    pill(d, W / 2, 300, "LEO · FAST CHARGER", 44, ORANGE, k=clamp(pop(lt / 0.3)))
    a = lt - sent(s, 2)
    if a > 0:
        k = clamp(pop(a / 0.3))
        circ(d, 820, 640, 120 * k, WHITE, INK, 9); line(d, [(820, 640), (820 + 80 * k * math.cos(-1.57 + a * 5), 640 + 80 * k * math.sin(-1.57 + a * 5))], RED, 10)
        text(d, 820, 810, "10 MIN", 56 * k, WHITE, stroke=9)

# ---------- 4. years pass ----------
def sc_years(d, lt, t, s):
    dur = s["ve"] - s["vs"]
    yr = min(7, 1 + int(lt / dur * 7.2))
    day = (lt / dur * 7) % 1
    sky(d, mix((120, 190, 255), (40, 48, 110), abs(day - 0.5) * 2), mix((210, 236, 255), (110, 96, 150), abs(day - 0.5) * 2))
    rect(d, 0, GY, W, H, (110, 190, 120)); line(d, [(0, GY), (W, GY)], INK, 7)
    rect(d, 0, GY + 120, W, GY + 330, (96, 100, 120)); line(d, [(0, GY + 120), (W, GY + 120)], INK, 6); line(d, [(0, GY + 330), (W, GY + 330)], INK, 6)
    for i, (cx, shirt, hair) in enumerate([(280, SAM, "cap"), (800, LEO, "spiky")]):
        person(d, cx - 150, GY + 110, 300, shirt, hair, t, "smile", -0.3, 0.3)
        car(d, cx + 40, GY + 300, 420, CARC, t, t * 9, 1)
        battery(d, cx, 620, 280, 97 - yr * (1.2 if i == 0 else 1.6), GREEN)
        text(d, cx, 480, "SAM" if i == 0 else "LEO", 50, WHITE, stroke=8)
    kk = clamp(pop(((lt / dur * 7.2) % 1) / 0.25))
    pill(d, W / 2, 320, f"YEAR {yr}", 64, YELLOW, k=0.85 + 0.15 * kk)

# ---------- 5. year eight ----------
_pop_at("year8", 0); _pop_at("year8", 1, 1.6); _pop_at("year8", 2, 1.4)
def sc_year8(d, lt, t, s):
    room(d, (255, 206, 120), (232, 150, 96), GY, (214, 120, 80))
    rect(d, W / 2 - 5, 0, W / 2 + 5, H, INK)
    pill(d, W / 2, 320, "YEAR 8", 70, YELLOW, k=clamp(pop(lt / 0.3)))
    a, b = lt - sent(s, 1), lt - sent(s, 2)
    va = 100 - 12 * smooth(a / 1.8) if a > 0 else 100
    vb = 100 - 24 * smooth(b / 1.8) if b > 0 else 100
    for i, (cx, shirt, hair, v, on) in enumerate([(270, SAM, "cap", va, a), (810, LEO, "spiky", vb, b)]):
        col = GREEN if i == 0 else mix(GREEN, ORANGE, (100 - v) / 24)
        battery(d, cx, 640, 380, v, col, f"{v:.0f}%" if on > 0 else None)
        text(d, cx, 480, "SAM" if i == 0 else "LEO", 54, WHITE, stroke=8)
        done = on > 1.8
        mood = ("smile" if i == 0 else "sad") if done else "flat"
        person(d, cx, GY + 60, 340, shirt, hair, t, mood, -0.3 if not (done and i == 0) else -2.6, 0.3 if not (done and i == 0) else 2.6, face=1 if i == 0 else -1)
        if done: pill(d, cx, 800, "ABOUT 88%" if i == 0 else "ABOUT 76%", 40, WHITE, k=clamp(pop((on - 1.8) / 0.3)))

# ---------- 6. the data ----------
_pop_at("data", 1, 0.6); _pop_at("data", 2, 0.4); _pop_at("data", 2, 2.2)
def sc_data(d, lt, t, s):
    rect(d, 0, 0, W, H, (40, 46, 84))
    a = lt - sent(s, 1)
    for i in range(60):                                     # a crowd of little cars
        k = clamp(pop((a - i * 0.02) / 0.2)) if a > 0 else 0
        if k > 0:
            k *= 1.35; x = 130 + (i % 10) * 91; y = 480 + (i // 10) * 62
            rect(d, x - 30 * k, y - 12 * k, x + 30 * k, y + 8 * k, [CARC, LIME, ORANGE, WHITE][i % 4], r=8, ol=INK, w=3)
            rect(d, x - 14 * k, y - 26 * k, x + 14 * k, y - 10 * k, (190, 228, 250), r=6, ol=INK, w=3)
    pill(d, W / 2, 330, "22,700+ EVs TRACKED", 50, LIME, k=clamp(pop(a / 0.3)) if a > 0 else 0)
    b = lt - sent(s, 2)
    if b > 0:
        rect(d, 60, 860, W - 60, 1210, (250, 250, 252), r=40, ol=INK, w=8)
        text(d, W / 2, 905, "BATTERY WEAR PER YEAR", 34, INK)
        g = smooth((b - 0.3) / 1.0); g2 = smooth((b - 2.0) / 1.0)
        text(d, 100, 975, "MOSTLY SLOW CHARGING", 28, INK, anchor="lm")
        rect(d, 100, 1000, 100 + 360 * g, 1050, GREEN, r=18, ol=INK, w=5)
        if g > 0.9: text(d, 480, 1025, "1.5%", 44, INK, anchor="lm")
        text(d, 100, 1095, "HEAVY HIGH-POWER FAST CHARGING", 28, INK, anchor="lm")
        rect(d, 100, 1120, 100 + 720 * g2, 1170, ORANGE, r=18, ol=INK, w=5)
        if g2 > 0.9: text(d, 840, 1145, "3.0%", 44, INK, anchor="lm")
    text(d, W / 2, 1560, "Source: Geotab EV battery health study (2025 data)", 26, (200, 206, 230), name="Inter-SemiBold.otf")

# ---------- 7. twist ----------
_pop_at("twist", 2); _pop_at("twist", 3)
def sc_twist(d, lt, t, s):
    sky(d, (120, 190, 255), (210, 236, 255))
    rect(d, 0, GY, W, H, (96, 100, 120)); line(d, [(0, GY), (W, GY)], INK, 7)
    a, b, c = lt - sent(s, 1), lt - sent(s, 2), lt - sent(s, 3)
    stop = smooth((b + 0.2) / 0.8) if b > -0.2 else 0
    sx = (t * 520 * (1 - stop)) % 220
    for i in range(8): rect(d, i * 220 - sx - 100, GY + 290, i * 220 - sx + 20, GY + 312, (240, 240, 245), r=6)
    for i in range(4):                                      # passing clouds
        x = (i * 380 - t * 60 * (1 - stop)) % (W + 300) - 150
        oval(d, x, 540 + (i % 2) * 120, 110, 44, WHITE, INK, 5)
    if stop > 0: fast_charger(d, 170 + (1 - stop) * -500, GY + 90, t)
    px, py = car(d, 640, GY + 150, 620, CARC, t, t * 12 * (1 - stop), 1)
    if stop > 0.95: cable(d, 250, GY - 250, px, py, 110, (40, 44, 60), t, 1.6, 9, 13, 14)
    if b > 0.9: person(d, 420, GY + 40, 300, LEO, "spiky", t, "flat", -0.3, 0.9)
    if b <= -0.2: pill(d, W / 2, 320, "STILL DRIVES FINE", 48, LIME, k=clamp(pop((a if a > 0 else lt) / 0.3)))
    elif c <= 0: pill(d, W / 2, 320, "MORE CHARGING STOPS", 48, ORANGE, k=clamp(pop(b / 0.3)))
    else:
        k = clamp(pop(c / 0.3))
        pill(d, W / 2, 320, "IS 10 MINUTES WORTH IT?", 50, YELLOW, k=k)
        pill(d, W / 2, 1520, "FOLLOW EV DRIVE", 44, LIME, k=clamp(pop((c - 1.2) / 0.3)))

SCENES.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("sc_") and callable(v)})
