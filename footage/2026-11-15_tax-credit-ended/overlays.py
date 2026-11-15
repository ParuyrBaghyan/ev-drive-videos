# Overlays for "The EV Tax Credit Ended" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)

def ov_hook(d, lt, t, s):
    pill(d, CX, 420, "$7,500 TAX CREDIT", 72, YELLOW, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - 1.2) / 0.3))
    if k > 0.02: text(d, CX, 590, "GONE", 150 * k, WHITE, stroke=14)
    k2 = clamp(pop((lt - sent(s, 1)) / 0.3))
    if k2 > 0.02: pill(d, CX, 790, "SALES CUT ~IN HALF", 60, RED, fg=WHITE, k=k2)

def ov_cliff(d, lt, t, s):
    k = clamp(pop((lt - 0.2) / 0.3))
    if k <= 0.02: return
    card(d, 70, 400, W - 70, 970)
    text(d, CX, 455, "SHARE OF NEW CARS SOLD: ELECTRIC", 36, WHITE)
    base = 830; hmax = 270
    g = smooth((lt - 1.0) / 0.9)
    h1 = hmax * g
    rect(d, 230, base - h1, 450, base, GREEN, r=18)
    text(d, 340, base + 40, "SEP 2025", 34, GREY)
    if g > 0.9: text(d, 340, base - h1 - 45, "11.4%", 64, WHITE)
    b = lt - sent(s, 1)
    if b > 0:
        g2 = smooth(b / 0.9); h2 = hmax * 11.4 / 11.4 * (1 - (1 - 5.8 / 11.4) * g2)
        rect(d, 630, base - h2, 850, base, mix(GREEN, RED, g2), r=18)
        text(d, 740, base + 40, "OCT 2025", 34, GREY)
        if g2 > 0.9: text(d, 740, base - h2 - 45, "5.8%", 64, WHITE)
    text(d, CX, 932, "Edmunds data, via NPR", 28, GREY, name="Inter-SemiBold.otf")

def ov_hybrid(d, lt, t, s):
    a = lt - sent(s, 1)
    if a > 0: pill(d, CX, 430, "BOUGHT INSTEAD: HYBRIDS", 62, LIME, k=clamp(pop(a / 0.3)))
    b = lt - sent(s, 2)
    if b > 0:
        k = clamp(pop(b / 0.3))
        n = 27 * smooth(b / 1.0)
        text(d, CX, 650, f"+{n:.0f}%", 200 * k, WHITE, stroke=14)
        text(d, CX, 800, "HYBRID SALES IN ONE YEAR", 46, YELLOW, stroke=8)

def ov_used(d, lt, t, s):
    pill(d, CX, 420, "USED ELECTRIC CARS", 66, YELLOW, k=clamp(pop(lt / 0.3)))
    b = lt - sent(s, 1)
    if b > 0:
        k = clamp(pop(b / 0.3))
        card(d, 120, 520, W - 120, 940)
        n = int(47000 * smooth(b / 1.2))
        text(d, CX, 640, f"{n:,}+", 150, LIME)
        text(d, CX, 760, "SOLD IN ONE MONTH", 46, WHITE)
        if lt - sent(s, 1) > 2.0: pill(d, CX, 850, "+21% VS A YEAR AGO", 44, GREEN)
        text(d, CX, 912, "Cox Automotive, Sept 2026", 28, GREY, name="Inter-SemiBold.otf")

def ov_price(d, lt, t, s):
    b = lt - sent(s, 1)
    if b <= 0:
        text(d, CX, 560, "WHY?", 170 * clamp(pop(lt / 0.3)), WHITE, stroke=14); return
    k = clamp(pop(b / 0.3))
    card(d, 120, 420, W - 120, 900)
    text(d, CX, 490, "AVERAGE NEW ELECTRIC CAR", 42, WHITE)
    n = int(56220 * smooth(b / 1.2))
    text(d, CX, 640, f"${n:,}", 150, ORANGE)
    text(d, CX, 790, "Kelley Blue Book, October 2026", 30, GREY, name="Inter-SemiBold.otf")

def ov_ending(d, lt, t, s):
    a = lt - 0.2
    if lt < sent(s, 1):
        k = clamp(pop(a / 0.3))
        card(d, 120, 420, W - 120, 820)
        text(d, CX, 490, "ELECTRIC SHARE, Q3 2026", 42, WHITE)
        text(d, CX, 640, "6.4%", 170 * k, LIME)
        text(d, CX, 775, "up from 5.8% in Q2 (Cox Automotive)", 30, GREY, name="Inter-SemiBold.otf")
        return
    b = lt - sent(s, 1)
    pill(d, CX, 450, "REJECTED THE CAR?", 64, ORANGE, k=clamp(pop(b / 0.3)))
    k2 = clamp(pop((b - 1.6) / 0.3))
    if k2 > 0.02: text(d, CX, 600, "OR THE PRICE?", 96 * k2, WHITE, stroke=12)
    c = lt - sent(s, 2)
    if c > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(c / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
