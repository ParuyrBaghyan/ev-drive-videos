# Overlays for "What If Every Car in America Went Electric Tomorrow?" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)

def wt(s, word, n=0):
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!:'$").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def ov_hook(d, lt, t, s):
    pill(d, CX, 400, "WHAT IF...", 60, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "every")
    if a > 0:
        text(d, CX, 560, "EVERY CAR", 150 * clamp(pop(a / 0.3)), YELLOW, stroke=16)
        text(d, CX, 690, "WENT ELECTRIC", 96 * clamp(pop(a / 0.3)), WHITE, stroke=12)
    b = lt - wt(s, "grid")
    if b > 0: pill(d, CX, 860, "CAN THE GRID SURVIVE?", 60, RED, fg=WHITE, k=clamp(pop(b / 0.3)))

def ov_miles(d, lt, t, s):
    pill(d, CX, 420, "US DRIVING, 2024", 52, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "three")
    if a > 0:
        text(d, CX, 580, "3.28 TRILLION", 120 * clamp(pop(a / 0.3)), LIME, stroke=14)
        text(d, CX, 680, "MILES A YEAR", 54, WHITE, stroke=10)
        text(d, CX, 735, "Source: FHWA", 30, GREY, stroke=6, name="Inter-SemiBold.otf")
    b = lt - wt(s, "thousand")
    if b > 0:
        pill(d, CX, 850, "x ~0.3 kWh PER MILE", 50, WHITE, k=clamp(pop(b / 0.3)))
        text(d, CX, 960, "≈ 1,000 TWh", 96 * clamp(pop(b / 0.3)), YELLOW, stroke=12)

def ov_grid(d, lt, t, s):
    pill(d, CX, 400, "ALL US POWER, 2025", 52, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "record")
    if a > 0:
        k = clamp(smooth(a / 0.8))
        card(d, 140, 470, 940, 960)
        rect(d, 230, 560, 230 + 620 * k, 650, (90, 160, 255), r=18)
        text(d, 250, 605, "TODAY  4,430 TWh", 40, WHITE, anchor="lm", stroke=6)
        text(d, CX, 700, "EIA record", 28, GREY, stroke=6, name="Inter-SemiBold.otf")
    b = lt - wt(s, "fifth")
    if b > 0:
        k = clamp(smooth(b / 0.6))
        rect(d, 230, 760, 230 + 620 * k, 850, (90, 160, 255), r=18)
        rect(d, 230 + 620 * k * 0.82, 760, 230 + 620 * k, 850, YELLOW, r=18)
        text(d, 250, 805, "ALL-ELECTRIC CARS", 40, WHITE, anchor="lm", stroke=6)
        text(d, CX, 910, "+ ~22%", 70 * clamp(pop(b / 0.3)), YELLOW, stroke=10)

def ov_night(d, lt, t, s):
    pill(d, CX, 400, "THE TWIST", 60, YELLOW, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "night")
    if a > 0: pill(d, CX, 550, "CHARGE AT NIGHT", 60, WHITE, k=clamp(pop(a / 0.3)))
    a2 = lt - wt(s, "idle")
    if a2 > 0: pill(d, CX, 680, "POWER PLANTS IDLE", 52, LIME, k=clamp(pop(a2 / 0.3)))
    b = lt - wt(s, "most", 1)
    if b > 0:
        text(d, CX, 830, "84%", 160 * clamp(pop(b / 0.3)), LIME, stroke=16)
        text(d, CX, 945, "PNNL study, 2006 · plug-in hybrids charging overnight", 28, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_street(d, lt, t, s):
    pill(d, CX, 420, "THE WEAK SPOT", 58, RED, fg=WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "street")
    if a > 0: pill(d, CX, 560, "YOUR STREET", 64, WHITE, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "fifty")
    if b > 0:
        text(d, CX, 700, "1 FAST CHARGER", 70, WHITE, stroke=10)
        text(d, CX, 820, "= 50 HOMES", 130 * clamp(pop(b / 0.3)), ORANGE, stroke=14)
        text(d, CX, 925, "Source: PNNL, 2020 (up to)", 30, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "ENERGY: YES", 64, LIME, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "six")) / 0.3))
    if k > 0.02: pill(d, CX, 580, "ALL AT 6 PM: NO", 60, RED, fg=WHITE, k=k)
    k2 = clamp(pop((lt - wt(s, "would")) / 0.3))
    if k2 > 0.02: pill(d, CX, 780, "CHARGE AT NIGHT? ↓", 64, WHITE, fg=INK, k=k2)
    e = lt - wt(s, "follow")
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
