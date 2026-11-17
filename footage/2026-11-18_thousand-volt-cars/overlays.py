# Overlays for "Your Outlet Is 120 Volts. This Electric Car Uses 1,200" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)
BLUE = (90, 170, 255)

def wt(s, word, n=0):
    """Start time (scene-local) of the n-th spoken word that starts with `word`."""
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!:").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def vbar(d, x, label, val, vmax, col, k, base=960, top=560, bw=150):
    h = (base - top) * max(0.03, val / vmax) * smooth(k)
    rect(d, x - bw / 2, base - h, x + bw / 2, base, col, r=18)
    if k > 0.05:
        text(d, x, base - h - 40, f"{int(val * smooth(k)):,} V", 46, col, stroke=8)

def ov_hook(d, lt, t, s):
    pill(d, CX, 420, "YOUR WALL OUTLET", 56, WHITE, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "one")) / 0.3))
    if k > 0.02: text(d, CX, 570, "120 V", 150 * k, BLUE, stroke=14)
    a = lt - sent(s, 1)
    if a > 0:
        pill(d, CX, 740, "NEWEST ELECTRIC HYPERCAR", 48, YELLOW, k=clamp(pop(a / 0.3)))
        k2 = clamp(pop((lt - wt(s, "twelve")) / 0.35))
        if k2 > 0.02:
            text(d, CX, 870, "1,200 V", 170 * k2, YELLOW, stroke=16)
            text(d, CX, 990, "Yangwang U9 Xtreme (BYD) · Top Gear", 30, GREY, name="Inter-SemiBold.otf")

def ov_history(d, lt, t, s):
    card(d, 90, 400, W - 90, 1020)
    text(d, CX, 450, "BATTERY VOLTAGE", 44, GREY)
    items = [("MOST ELECTRIC CARS", 400, BLUE, "about", 330), ("PORSCHE TAYCAN, 2019", 800, ORANGE, "porsche", 750)]
    for lab, v, col, at, x in items:
        k = clamp((lt - wt(s, at)) / 0.6)
        if k > 0:
            vbar(d, x, lab, v, 800, col, k, top=560, bw=200)
            text(d, x, 995, lab, 32, WHITE)

def ov_physics(d, lt, t, s):
    pill(d, CX, 420, "POWER = VOLTS × AMPS", 56, YELLOW, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "double")
    if a > 0:
        card(d, 90, 520, W - 90, 1000)
        k = clamp(pop(a / 0.3))
        text(d, 300, 620, "VOLTS", 44, GREY)
        text(d, 300, 740, "×2", 150 * k, LIME, stroke=12)
        b = lt - wt(s, "half")
        if b > 0:
            k2 = clamp(pop(b / 0.3))
            text(d, 780, 620, "AMPS", 44, GREY)
            text(d, 780, 740, "÷2", 150 * k2, ORANGE, stroke=12)
        c = lt - wt(s, "same")
        if c > 0: text(d, CX, 910, "SAME POWER", 80 * clamp(pop(c / 0.3)), WHITE, stroke=10)

def ov_heat(d, lt, t, s):
    pill(d, CX, 420, "HEAT LOST IN WIRES", 56, RED, fg=WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "quarter")
    if a > 0:
        text(d, CX, 610, "¼", 200 * clamp(pop(a / 0.35)), YELLOW, stroke=16)
        text(d, CX, 745, "heat loss = current² × resistance", 36, GREY, stroke=6, name="Inter-SemiBold.otf")
    b = lt - sent(s, 1)
    if b > 0:
        pill(d, CX, 840, "SLIMMER CABLES", 58, GREEN, fg=INK, k=clamp(pop(b / 0.3)))
        c = lt - wt(s, "faster")
        if c > 0: pill(d, CX, 960, "FASTER CHARGING", 58, LIME, fg=INK, k=clamp(pop(c / 0.3)))

def ov_byd(d, lt, t, s):
    pill(d, CX, 420, "BYD SUPER e-PLATFORM", 54, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "thousand")
    if a > 0:
        k = clamp(pop(a / 0.3))
        text(d, 310, 560, "1,000 V", 100 * k, LIME, stroke=10)
        text(d, 770, 560, "1,000 kW", 100 * k, YELLOW, stroke=10)
    b = lt - wt(s, "four")
    if b > 0:
        card(d, 90, 650, W - 90, 1000)
        text(d, CX, 760, "+400 KM", 140 * clamp(pop(b / 0.35)), LIME, stroke=12)
        c = lt - wt(s, "five")
        if c > 0:
            text(d, CX, 880, "IN 5 MINUTES", 70 * clamp(pop(c / 0.3)), WHITE, stroke=8)
            text(d, CX, 955, "BYD's claim (China, March 2025)", 30, GREY, name="Inter-SemiBold.otf")

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "HOW HIGH CAN IT GO?", 58, WHITE, k=clamp(pop(lt / 0.3)))
    c = lt - wt(s, "two")
    if c > 0: text(d, CX, 640, "2,000 V?", 170 * clamp(pop(c / 0.3)), YELLOW, stroke=14)
    k2 = clamp(pop((lt - wt(s, "guess")) / 0.3))
    if k2 > 0.02: pill(d, CX, 850, "YOUR GUESS ↓", 64, LIME, fg=INK, k=k2)
    e = lt - wt(s, "follow")
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
