# Overlays for "A Tesla Semi Caught Fire Without Crashing. Here's the Problem" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)

def wt(s, word, n=0):
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!:'$").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def ov_hook(d, lt, t, s):
    pill(d, CX, 400, "ELECTRIC SEMI TRUCK", 56, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "fire")
    if a > 0: text(d, CX, 580, "ON FIRE", 170 * clamp(pop(a / 0.3)), ORANGE, stroke=16)
    b = lt - wt(s, "no")
    if b > 0: pill(d, CX, 770, "NO CRASH", 90, RED, fg=WHITE, k=clamp(pop(b / 0.3)))

def ov_event(d, lt, t, s):
    pill(d, CX, 420, "I-880 · HAYWARD, CA · OCT 27", 48, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "driver")
    if a > 0: pill(d, CX, 570, "DRIVER UNHURT", 56, GREEN, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "ten")
    if b > 0:
        text(d, CX, 760, "~10 HOURS", 150 * clamp(pop(b / 0.3)), YELLOW, stroke=14)
        text(d, CX, 870, "SOUTHBOUND LANES CLOSED", 46, WHITE, stroke=10)
        text(d, CX, 930, "CHP via Electrek · cause under investigation", 30, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_why(d, lt, t, s):
    pill(d, CX, 420, "WHY IT'S HARD TO STOP", 52, WHITE, k=clamp(pop(lt / 0.3)))
    labels = [("one", "HOT CELL", RED), ("heats", "HEATS ITS NEIGHBORS", ORANGE), ("feeding", "FEEDS ITS OWN FIRE", YELLOW)]
    for i, (w, lab, col) in enumerate(labels):
        a = lt - wt(s, w)
        if a > 0:
            pill(d, CX, 580 + i * 160, lab, 56, col, fg=WHITE if col == RED else INK, k=clamp(pop(a / 0.3)))
            if i: text(d, CX, 580 + i * 160 - 80, "↓", 50, WHITE, stroke=8)

def ov_past(d, lt, t, s):
    pill(d, CX, 420, "AUG 2024 · I-80 · SIERRA", 52, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "crashed")
    if a > 0: pill(d, CX, 570, "CRASH, THEN FIRE", 56, ORANGE, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "fifty")
    if b > 0:
        text(d, CX, 760, "50,000", 190 * clamp(pop(b / 0.3)), LIME, stroke=16)
        text(d, CX, 880, "GALLONS OF WATER", 56, WHITE, stroke=10)
        text(d, CX, 945, "Source: NTSB preliminary report", 30, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_fair(d, lt, t, s):
    pill(d, CX, 420, "TO BE FAIR", 58, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "fifteen")
    if a > 0:
        text(d, CX, 600, "~15,000", 180 * clamp(pop(a / 0.3)), YELLOW, stroke=16)
        text(d, CX, 720, "LARGE-TRUCK FIRES A YEAR (US)", 46, WHITE, stroke=10)
        text(d, CX, 780, "NFPA, 2018-2022 average · mostly diesel", 30, GREY, stroke=6, name="Inter-SemiBold.otf")
    b = lt - wt(s, "cause")
    if b > 0: pill(d, CX, 920, "CAUSE: UNDER INVESTIGATION", 48, LIME, k=clamp(pop(b / 0.3)))

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "RARE...", 64, LIME, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "harder")) / 0.3))
    if k > 0.02: pill(d, CX, 580, "BUT HARDER TO FIGHT", 60, ORANGE, k=k)
    k2 = clamp(pop((lt - wt(s, "tell")) / 0.3))
    if k2 > 0.02: pill(d, CX, 780, "TRUST THEM? ↓", 70, WHITE, fg=INK, k=k2)
    e = lt - wt(s, "follow")
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
