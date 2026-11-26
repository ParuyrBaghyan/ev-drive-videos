# Overlays for "7 in 10 New Cars in China Now Plug In. But There's a Twist" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)

def wt(s, word, n=0):
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!:'").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def hbar(d, y, label, val, vmax, col, k, shown, x0=150, x1=930):
    text(d, x0, y - 28, label, 32, WHITE, anchor="lm", stroke=6)
    w = (x1 - x0) * max(0.04, val / vmax) * smooth(k)
    rect(d, x0, y, x0 + w, y + 48, col, r=12)
    if k > 0.3: text(d, min(x0 + w + 16, x1 - 10) if val / vmax < 0.5 else x0 + 18, y + 24, shown, 36, WHITE if val / vmax < 0.5 else INK, anchor="lm", stroke=6 if val / vmax < 0.5 else 0)

def ov_hook(d, lt, t, s):
    pill(d, CX, 400, "CHINA · NOVEMBER 2026", 52, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "seven")
    if a > 0:
        text(d, CX, 600, "7 IN 10", 210 * clamp(pop(a / 0.3)), LIME, stroke=18)
        text(d, CX, 740, "NEW CARS PLUG IN", 60, WHITE, stroke=10)
    b = lt - wt(s, "record")
    if b > 0: pill(d, CX, 880, "NEW RECORD", 60, YELLOW, k=clamp(pop(b / 0.3)))

def ov_share(d, lt, t, s):
    pill(d, CX, 420, "SHARE OF NEW CAR SALES", 50, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "seventy")
    if a > 0:
        card(d, 90, 490, W - 90, 1000)
        text(d, CX, 540, "PLUG-IN = ELECTRIC + PLUG-IN HYBRID", 32, GREY)
        hbar(d, 640, "China · plug-in · Nov 1-15", 73.2, 100, LIME, clamp(a / 0.6), "73.2%")
    b = lt - sent(s, 1)
    if b > 0:
        hbar(d, 790, "USA · fully electric · Q3 2026", 6.4, 100, ORANGE, clamp(b / 0.6), "~6%")
        text(d, CX, 930, "Sources: CPCA via CnEVPost · Cox Automotive", 30, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_twist(d, lt, t, s):
    a = lt - wt(s, "twist")
    if a > 0: pill(d, CX, 420, "THE TWIST", 64, YELLOW, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "thirteen")
    if b > 0:
        text(d, CX, 640, "-13%", 230 * clamp(pop(b / 0.3)), RED, stroke=18)
        text(d, CX, 800, "PLUG-IN SALES VS A YEAR AGO", 48, WHITE, stroke=10)
        text(d, CX, 870, "Nov 1-15 retail, CPCA", 32, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_collapse(d, lt, t, s):
    pill(d, CX, 420, "WHY THE SHARE JUMPED", 52, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "gas")
    if a > 0: pill(d, CX, 580, "GAS CARS FELL FASTER", 56, RED, fg=WHITE, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "total")
    if b > 0:
        text(d, CX, 760, "-25%", 200 * clamp(pop(b / 0.3)), ORANGE, stroke=16)
        text(d, CX, 900, "ALL CAR SALES · NOV 1-15", 46, WHITE, stroke=10)

def ov_why(d, lt, t, s):
    pill(d, CX, 420, "THE BLAME", 58, WHITE, k=clamp(pop(lt / 0.3)))
    for i, (w, lab, col) in enumerate([("fuel", "HIGH FUEL PRICES", ORANGE), ("nervous", "NERVOUS BUYERS", YELLOW), ("smaller", "SMALLER SUBSIDIES", LIME)]):
        a = lt - wt(s, w)
        if a > 0: pill(d, CX, 590 + i * 160, lab, 56, col, k=clamp(pop(a / 0.3)))

def ov_survival(d, lt, t, s):
    a = lt - wt(s, "survival")
    if lt > 0: pill(d, CX, 420, "CHINA'S CAR INDUSTRY", 52, WHITE, k=clamp(pop(lt / 0.3)))
    if a > 0:
        text(d, CX, 600, "SURVIVAL", 170 * clamp(pop(a / 0.3)), RED, stroke=16)
        text(d, CX, 730, "PHASE", 110 * clamp(pop(a / 0.3)), WHITE, stroke=12)
    b = lt - wt(s, "weak")
    if b > 0: pill(d, CX, 890, "WEAK BRANDS PUSHED OUT", 52, YELLOW, k=clamp(pop(b / 0.3)))

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "END OF THE GAS CAR?", 62, LIME, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "or")) / 0.3))
    if k > 0.02: pill(d, CX, 580, "OR JUST A BAD YEAR?", 62, ORANGE, k=k)
    k2 = clamp(pop((lt - wt(s, "tell")) / 0.3))
    if k2 > 0.02: pill(d, CX, 780, "YOUR ANSWER ↓", 70, WHITE, fg=INK, k=k2)
    e = lt - wt(s, "follow")
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
