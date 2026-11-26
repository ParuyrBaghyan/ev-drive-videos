# Overlays for "Tesla Added a Button That Can Cause $25,000 in Damage" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)

def wt(s, word, n=0):
    """Start time (scene-local) of the n-th spoken word that starts with `word`."""
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!:'").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def ov_hook(d, lt, t, s):
    pill(d, CX, 420, "NEW TESLA FEATURE", 58, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "twenty")
    if a > 0:
        text(d, CX, 610, "UP TO", 60, WHITE, stroke=10)
        text(d, CX, 760, "$25,000", 210 * clamp(pop(a / 0.3)), RED, stroke=18)
        text(d, CX, 880, "IN DAMAGE", 60, WHITE, stroke=10)
    b = lt - sent(s, 1)
    if b > 0: pill(d, CX, 990, "ON PURPOSE", 56, YELLOW, k=clamp(pop(b / 0.3)))

def ov_why(d, lt, t, s):
    a = lt - wt(s, "emergency")
    if a > 0: pill(d, CX, 430, "EMERGENCY DRIVE AWAY", 56, RED, fg=WHITE, k=clamp(pop(a / 0.3)))
    b = lt - sent(s, 1)
    if b > 0:
        card(d, 120, 560, W - 120, 860)
        text(d, CX, 630, "WHY IT EXISTS", 38, GREY)
        text(d, CX, 720, "SHOOTING AT A", 62, WHITE, stroke=8)
        text(d, CX, 800, "SUPERCHARGER · IDAHO", 54, YELLOW, stroke=8)

def ov_how(d, lt, t, s):
    pill(d, CX, 420, "HOW IT WORKS", 56, WHITE, k=clamp(pop(lt / 0.3)))
    steps = [("shift", "1  SHIFT INTO DRIVE"), ("hold", "2  HOLD THE BRAKE"), ("tap", "3  TAP ACTIVATE"), ("go", "4  ACCELERATE")]
    for i, (wd, lab) in enumerate(steps):
        a = lt - wt(s, wd)
        if a > 0: pill(d, CX, 560 + i * 120, lab, 52, LIME if i < 3 else YELLOW, k=clamp(pop(a / 0.3)))

def ov_snap(d, lt, t, s):
    pill(d, CX, 420, "WHAT HAPPENS", 56, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "breaks")
    if a > 0: text(d, CX, 590, "PLUG BREAKS AWAY", 80 * clamp(pop(a / 0.3)), RED, stroke=12)
    b = lt - wt(s, "coolant")
    if b > 0: pill(d, CX, 740, "COOLANT SPILLS", 52, ORANGE, k=clamp(pop(b / 0.3)))
    c = lt - wt(s, "repair")
    if c > 0: pill(d, CX, 880, "CHARGE PORT: SERVICE VISIT", 48, YELLOW, k=clamp(pop(c / 0.3)))

def ov_cost(d, lt, t, s):
    pill(d, CX, 420, "SUPERCHARGER STALL REPAIR", 52, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "twenty")
    if a > 0:
        text(d, CX, 600, "UP TO $25K", 160 * clamp(pop(a / 0.3)), RED, stroke=16)
        text(d, CX, 710, "Source: Tesla, via Engadget / InsideEVs", 30, GREY, stroke=6, name="Inter-SemiBold.otf")
    b = lt - wt(s, "abusing")
    if b > 0: pill(d, CX, 860, "MISUSE = EXTRA PENALTIES", 52, ORANGE, k=clamp(pop(b / 0.3)))
    if b > 1.2: text(d, CX, 960, "US Superchargers only · not pre-2021 Model S/X", 32, WHITE, stroke=6, name="Inter-SemiBold.otf")

def ov_oops(d, lt, t, s):
    a = lt - wt(s, "austin")
    if a > 0: pill(d, CX, 430, "AUSTIN, TEXAS", 58, WHITE, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "accident")
    if b > 0:
        text(d, CX, 640, "BY ACCIDENT", 120 * clamp(pop(b / 0.3)), YELLOW, stroke=14)
        text(d, CX, 760, "first documented use (Not a Tesla App)", 34, WHITE, stroke=6, name="Inter-SemiBold.otf")

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "LIFE-SAVING ESCAPE?", 62, LIME, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "expensive")) / 0.3))
    if k > 0.02: pill(d, CX, 580, "OR EXPENSIVE MISTAKE?", 62, ORANGE, k=k)
    k2 = clamp(pop((lt - wt(s, "tell")) / 0.3))
    if k2 > 0.02: pill(d, CX, 780, "YOUR ANSWER ↓", 70, WHITE, fg=INK, k=k2)
    e = lt - wt(s, "follow")
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
