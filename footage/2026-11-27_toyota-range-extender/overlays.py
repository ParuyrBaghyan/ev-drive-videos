# Overlays for "Toyota's Next Electric Car Has a Gas Engine. Here's Why" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)

def wt(s, word, n=0):
    """Start time (scene-local) of the n-th spoken word that starts with `word`."""
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!:'").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def hbar(d, y, label, val, vmax, col, k, shown, x0=150, x1=930):
    text(d, x0, y - 28, label, 32, WHITE, anchor="lm", stroke=6)
    w = (x1 - x0) * max(0.04, val / vmax) * smooth(k)
    rect(d, x0, y, x0 + w, y + 48, col, r=12)
    if k > 0.3: text(d, x0 + 18, y + 24, shown, 34, INK, anchor="lm")

def ov_hook(d, lt, t, s):
    pill(d, CX, 420, "TOYOTA'S NEXT ELECTRIC CAR", 52, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "gas")
    if a > 0:
        text(d, CX, 600, "+ A GAS", 130 * clamp(pop(a / 0.3)), ORANGE, stroke=16)
        text(d, CX, 730, "ENGINE", 130 * clamp(pop(a / 0.3)), ORANGE, stroke=16)
    b = lt - wt(s, "guangzhou")
    if b > 0: pill(d, CX, 880, "GUANGZHOU AUTO SHOW · NOV 27", 46, LIME, k=clamp(pop(b / 0.3)))

def ov_how(d, lt, t, s):
    a = lt - wt(s, "range")
    if a > 0: pill(d, CX, 420, "RANGE EXTENDER", 60, LIME, k=clamp(pop(a / 0.3)))
    if lt - sent(s, 1) > 0 or lt - sent(s, 2) > 0:
        card(d, 110, 520, W - 110, 990)
    b = lt - wt(s, "electric")
    if b > 0:
        text(d, CX, 590, "WHEELS ← ELECTRIC MOTORS", 48, WHITE, stroke=0)
    c = lt - sent(s, 2)
    if c > 0:
        text(d, CX, 700, "GAS ENGINE", 64, ORANGE)
        text(d, CX, 790, "↓ generator only ↓", 40, GREY, name="Inter-SemiBold.otf")
    if c > 0.8:
        battery(d, CX, 895, 300, 100 * (0.25 + 0.6 * smooth((c - 0.8) / 2.5)), GREEN)

def ov_xiaomi(d, lt, t, s):
    pill(d, CX, 420, "XIAOMI · OCTOBER 2026", 54, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - sent(s, 2)
    if a > 0:
        card(d, 110, 500, W - 110, 990)
        text(d, CX, 560, "CARS DELIVERED", 38, GREY)
        hbar(d, 670, "Range extenders", 27147, 27147, ORANGE, clamp(a / 0.6), "27,147")
        hbar(d, 790, "Pure electric", 23021, 27147, LIME, clamp(a / 0.6), "23,021")
        if a > 0.8: text(d, CX, 900, "54% OF SALES", 70 * clamp(pop((a - 0.8) / 0.3)), YELLOW, stroke=8)
        text(d, CX, 960, "Source: CPCA data via CnEVPost", 28, GREY, name="Inter-SemiBold.otf")
    elif lt - wt(s, "september") > 0:
        pill(d, CX, 600, "FIRST ONES: SEPTEMBER", 52, ORANGE, k=clamp(pop((lt - wt(s, "september")) / 0.3)))

def ov_toyota(d, lt, t, s):
    pill(d, CX, 420, "TOYOTA SALES IN CHINA", 54, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "nineteen")
    if a > 0:
        text(d, CX, 620, "-19%", 230 * clamp(pop(a / 0.3)), RED, stroke=18)
        text(d, CX, 770, "JAN–SEP 2026 · via Electrek", 38, WHITE, stroke=8)
    b = lt - wt(s, "joining")
    if b > 0: pill(d, CX, 900, "TARGET: 200,000 IN 2027 (NIKKEI)", 44, LIME, k=clamp(pop(b / 0.3)))

def ov_catch(d, lt, t, s):
    pill(d, CX, 420, "THE CATCH", 60, YELLOW, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "burns")
    if a > 0: pill(d, CX, 600, "STILL BURNS GAS", 60, RED, fg=WHITE, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "less")
    if b > 0: pill(d, CX, 760, "LESS EFFICIENT THAN PURE EV", 50, ORANGE, k=clamp(pop(b / 0.3)))

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "SMART BRIDGE?", 64, LIME, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "step")) / 0.3))
    if k > 0.02: pill(d, CX, 580, "OR STEP BACK?", 64, ORANGE, k=k)
    k2 = clamp(pop((lt - wt(s, "tell")) / 0.3))
    if k2 > 0.02: pill(d, CX, 780, "YOUR ANSWER ↓", 70, WHITE, fg=INK, k=k2)
    e = lt - wt(s, "follow")
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
