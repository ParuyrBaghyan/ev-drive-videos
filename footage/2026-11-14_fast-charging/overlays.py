# Number overlays for the fast-charging Short (runs inside tools/render_footage.py globals).
CX = W / 2
def ov_hook(d, lt, t, s):
    k = clamp(pop(lt / 0.3))
    pill(d, CX, 420, "FAST CHARGING", 76, YELLOW, k=k)
    k2 = clamp(pop((lt - 0.5) / 0.3))
    if k2 > 0.02: text(d, CX, 600, "BATTERY KILLER?", 96 * k2, WHITE, stroke=12)

def ov_study(d, lt, t, s):
    k = clamp(pop((lt - 0.3) / 0.3))
    if k <= 0.02: return
    card(d, 120, 420, W - 120, 800)
    n = int(22700 * smooth((lt - 0.4) / 1.4))
    text(d, CX, 540, f"{n:,}+", 150, LIME)
    text(d, CX, 690, "ELECTRIC CARS TRACKED", 46, WHITE)
    text(d, CX, 760, "Geotab battery health study, 2025 data", 28, (210, 214, 230), name="Inter-SemiBold.otf")

def _bars(d, lt, slow_at, fast_at):
    card(d, 70, 400, W - 70, 880)
    text(d, CX, 455, "BATTERY LOST PER YEAR", 40, WHITE)
    g = smooth((lt - slow_at) / 0.9)
    text(d, 120, 540, "MOSTLY SLOW CHARGING", 32, (210, 214, 230), anchor="lm")
    rect(d, 120, 570, 120 + 330 * g + 10, 640, GREEN, r=20)
    if g > 0.9: text(d, 480, 605, "1.5%", 64, WHITE, anchor="lm")
    if fast_at is None: return
    g2 = smooth((lt - fast_at) / 0.9)
    text(d, 120, 715, "HEAVY HIGH-POWER FAST CHARGING", 32, (210, 214, 230), anchor="lm")
    rect(d, 120, 745, 120 + 660 * g2 + 10, 815, ORANGE, r=20)
    if g2 > 0.9: text(d, 810, 780, "3.0%", 64, WHITE, anchor="lm")

def ov_slow(d, lt, t, s): _bars(d, lt, 1.6, None)
def ov_fast(d, lt, t, s):
    _bars(d, lt, -5, 2.4)
    b = lt - sent(s, 1)
    if b > 0: pill(d, CX, 990, "THAT'S DOUBLE", 64, YELLOW, k=clamp(pop(b / 0.3)))

def ov_eight(d, lt, t, s):
    pill(d, CX, 400, "AFTER 8 YEARS", 64, YELLOW, k=clamp(pop(lt / 0.3)))
    a = lt - 1.6; b = lt - 3.9
    if a > 0:
        v = 100 - 12 * smooth(a / 1.2)
        text(d, 290, 560, "SLOW", 44, WHITE, stroke=8); battery(d, 290, 700, 400, v, GREEN, f"{v:.0f}%")
    if b > 0:
        v = 100 - 24 * smooth(b / 1.0)
        text(d, 790, 560, "FAST", 44, WHITE, stroke=8); battery(d, 790, 700, 400, v, mix(GREEN, ORANGE, (100 - v) / 24), f"{v:.0f}%")
    if a > 0: text(d, CX, 880, "rough estimate from the yearly rates above", 28, WHITE, stroke=5, name="Inter-SemiBold.otf")

def ov_advice(d, lt, t, s):
    k = clamp(pop((lt - 0.3) / 0.3)); k2 = clamp(pop((lt - sent(s, 1)) / 0.3))
    pill(d, CX, 440, "ROAD TRIPS: FINE", 66, LIME, k=k)
    pill(d, CX, 600, "EVERY DAY: AVOID", 66, ORANGE, k=k2)
    pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop((lt - sent(s, 1) - 1.6) / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
