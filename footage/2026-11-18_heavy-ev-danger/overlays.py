# Overlays for "Heavy Electric Cars Have a Problem Nobody Talks About" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)
BLUE = (90, 170, 255)

def wt(s, word, n=0):
    """Start time (scene-local) of the n-th spoken word that starts with `word`."""
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!:").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def hbar(d, y, label, val, vmax, col, k, fmt):
    x0, x1 = 150, W - 150
    text(d, x0, y - 48, label, 40, WHITE, anchor="lm")
    rect(d, x0, y - 18, x1, y + 30, (255, 255, 255, 40), r=24)
    w = (x1 - x0) * max(0.04, val / vmax) * smooth(k)
    rect(d, x0, y - 18, x0 + w, y + 30, col, r=24)
    if k > 0.05: text(d, x1, y - 48, fmt(val * smooth(k)), 44, col, anchor="rm", stroke=6)

def ov_hook(d, lt, t, s):
    pill(d, CX, 420, "GMC HUMMER EV PICKUP", 54, YELLOW, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - 0.25) / 0.3))
    if k > 0.02:
        text(d, CX, 590, "9,063 LB", 150 * k, WHITE, stroke=14)
        text(d, CX, 700, "curb weight (GM filing to EPA)", 40 * k, GREY, stroke=8)
    a = lt - sent(s, 1)
    if a > 0:
        card(d, 90, 770, W - 90, 1000)
        hbar(d, 860, "ITS BATTERY", 2923, 2923, ORANGE, a / 0.6, lambda v: f"{int(v):,} lb")
        b = lt - wt(s, "Honda")
        if b > 0: hbar(d, 960, "HONDA CIVIC LX (whole car)", 2877, 2923, BLUE, b / 0.6, lambda v: f"{int(v):,} lb")

def ov_inside(d, lt, t, s):
    pill(d, CX, 430, "INSIDE: SAFER", 66, GREEN, fg=INK, k=clamp(pop(lt / 0.3)))
    a = lt - sent(s, 1)
    if a > 0:
        pill(d, CX, 570, "THE OTHER CAR?", 66, RED, fg=WHITE, k=clamp(pop(a / 0.3)))
        text(d, CX, 780, "?", 260 * clamp(pop((a - 0.3) / 0.35)), YELLOW, stroke=14)

def ov_study(d, lt, t, s):
    pill(d, CX, 420, "HIT BY +1,000 LB", 64, YELLOW, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "forty")
    if a > 0:
        text(d, CX, 640, "+47%", 230 * clamp(pop(a / 0.35)), RED, stroke=16)
        text(d, CX, 820, "risk of dying in the crash", 50, WHITE, stroke=8)
        text(d, CX, 900, "Anderson & Auffhammer, NBER, 2011", 30, GREY, name="Inter-SemiBold.otf")

def ov_iihs(d, lt, t, s):
    pill(d, CX, 420, "IIHS STUDY, 2025", 62, WHITE, k=clamp(pop(lt / 0.3)))
    card(d, 90, 500, W - 90, 1000)
    text(d, CX, 560, "EACH EXTRA 500 LB ON A PICKUP:", 38, GREY)
    a = lt - wt(s, "found")
    if a > 0:
        k = clamp(pop(a / 0.3))
        text(d, 300, 690, "-1", 130 * k, GREEN, stroke=10)
        text(d, 300, 800, "death in", 36, WHITE)
        text(d, 300, 845, "the pickup", 36, WHITE)
    b = lt - wt(s, "endangers")
    if b > 0:
        k = clamp(pop(b / 0.3))
        text(d, 780, 690, "+7", 130 * k, RED, stroke=10)
        text(d, 780, 800, "deaths in", 36, WHITE)
        text(d, 780, 845, "the cars it hits", 36, WHITE)
    if a > 0: text(d, CX, 950, "per million registered vehicle years · IIHS, Feb 2025", 26, GREY, name="Inter-SemiBold.otf")

def ov_fair(d, lt, t, s):
    pill(d, CX, 420, "NOT JUST ELECTRIC", 62, YELLOW, k=clamp(pop(lt / 0.3)))
    for i, (w, at) in enumerate([("GAS PICKUPS", "pickups"), ("BIG SUVs", "SUV")]):
        k = clamp(pop((lt - wt(s, at)) / 0.3))
        if k > 0.02: pill(d, CX, 600 + i * 130, w, 58, ORANGE, fg=INK, k=k)
    c = lt - wt(s, "heavy")
    if c > 0: text(d, CX, 900, "SAME PROBLEM", 90 * clamp(pop(c / 0.3)), WHITE, stroke=10)

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "HEAVIER CAR =", 62, WHITE, k=clamp(pop(lt / 0.3)))
    c = lt - wt(s, "pay")
    if c > 0: text(d, CX, 620, "PAY MORE?", 140 * clamp(pop(c / 0.3)), YELLOW, stroke=14)
    k2 = clamp(pop((lt - sent(s, 1)) / 0.3))
    if k2 > 0.02:
        pill(d, 330, 820, "YES", 70, GREEN, fg=INK, k=k2)
        pill(d, 750, 820, "NO", 70, RED, fg=WHITE, k=k2)
    e = lt - sent(s, 2)
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
