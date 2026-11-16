# Overlays for "Tesla vs Waymo: The Robotaxi Number Nobody Talks About" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)
BLUE = (90, 170, 255)
TCOL = (240, 84, 84)    # Tesla bars (red)
WCOL = (90, 170, 255)   # Waymo bars (blue)

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
    pill(d, CX, 420, "SAN ANTONIO ROBOTAXIS", 54, YELLOW, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - 0.25) / 0.3))
    if k > 0.02:
        text(d, CX, 590, "4x BIGGER", 140 * k, WHITE, stroke=14)
        text(d, CX, 700, "Tesla's zone vs Waymo's", 44 * k, GREY, stroke=8)
    k2 = clamp(pop((lt - sent(s, 1)) / 0.3))
    if k2 > 0.02: text(d, CX, 880, "TESLA WINS?", 96 * k2, YELLOW, stroke=12)

def ov_maps(d, lt, t, s):
    pill(d, CX, 420, "SERVICE AREA", 62, WHITE, k=clamp(pop(lt / 0.3)))
    card(d, 90, 500, W - 90, 1000)
    a = lt - wt(s, "two")
    if a > 0: hbar(d, 640, "TESLA · from Nov 9", 274, 274, TCOL, a / 0.8, lambda v: f"~{int(v)} sq mi")
    b = lt - wt(s, "sixty")
    if b > 0: hbar(d, 820, "WAYMO · since Feb", 59, 274, WCOL, b / 0.6, lambda v: f"~{int(v)} sq mi")
    text(d, CX, 950, "Source: Robotaxi Tracker via Electrek, Nov 9, 2026", 26, GREY, name="Inter-SemiBold.otf")

def ov_cars(d, lt, t, s):
    pill(d, CX, 420, "COUNT THE CARS", 66, YELLOW, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "four")
    if a > 0:
        card(d, 90, 500, W - 90, 1000)
        text(d, CX, 560, "DRIVERLESS ROBOTAXIS, US", 36, GREY)
        hbar(d, 680, "WAYMO", 4000, 4000, WCOL, a / 0.8, lambda v: f"{int(v):,}+")
        b = lt - wt(s, "six")
        if b > 0: hbar(d, 850, "TESLA", 666, 4000, TCOL, b / 0.6, lambda v: f"{int(v)}")
        text(d, CX, 950, "Robotaxi Tracker count, Nov 9, 2026", 26, GREY, name="Inter-SemiBold.otf")

def ov_zero(d, lt, t, s):
    pill(d, CX, 420, "LAUNCH MORNING", 62, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "zero")
    if a > 0:
        text(d, CX, 650, "0", 330 * clamp(pop(a / 0.35)), RED, stroke=16)
        text(d, CX, 860, "Teslas spotted in San Antonio", 46, WHITE, stroke=8)
        text(d, CX, 930, "(Robotaxi Tracker, morning of Nov 9)", 30, GREY, name="Inter-SemiBold.otf")

def ov_bets(d, lt, t, s):
    pill(d, CX, 420, "TWO DIFFERENT BETS", 60, YELLOW, k=clamp(pop(lt / 0.3)))
    card(d, 90, 500, W - 90, 1000)
    text(d, 300, 570, "WAYMO", 52, WCOL)
    text(d, 780, 570, "TESLA", 52, TCOL)
    for i, (w, at) in enumerate([("LIDAR", "lidar"), ("RADAR", "radar"), ("CAMERAS", "cameras")]):
        k = clamp(pop((lt - wt(s, at)) / 0.3))
        if k > 0.02: pill(d, 300, 680 + i * 105, w, 44, WCOL, fg=INK, k=k)
    b = lt - sent(s, 1)
    if b > 0:
        pill(d, 780, 680, "CAMERAS", 44, TCOL, fg=WHITE, k=clamp(pop(b / 0.3)))
        c = lt - wt(s, "AI")
        if c > 0: pill(d, 780, 785, "+ AI", 44, TCOL, fg=WHITE, k=clamp(pop(c / 0.3)))
        e = lt - wt(s, "cheaper")
        if e > 0: text(d, 780, 905, "cheaper per car", 38 * clamp(pop(e / 0.3)), YELLOW, stroke=6)

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "BIGGER MAP", 62, TCOL, fg=WHITE, k=clamp(pop(lt / 0.3)))
    k2 = clamp(pop((lt - wt(s, "more")) / 0.3))
    if k2 > 0.02: pill(d, CX, 560, "MORE CARS", 62, WCOL, fg=INK, k=k2)
    c = lt - wt(s, "who")
    if c > 0: text(d, CX, 740, "WHO WINS?", 120 * clamp(pop(c / 0.3)), WHITE, stroke=12)
    e = lt - sent(s, 2)
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
