# Overlays for "Why You Can't Buy a Chinese EV in America" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)

def ov_hook(d, lt, t, s):
    pill(d, CX, 420, "NEW ELECTRIC CAR", 66, YELLOW, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - 1.0) / 0.3))
    if k > 0.02: text(d, CX, 590, "~$10,000", 150 * k, WHITE, stroke=14)
    k2 = clamp(pop((lt - sent(s, 1) - 0.6) / 0.3))
    if k2 > 0.02: pill(d, CX, 790, "NOT FOR SALE IN THE USA", 56, RED, fg=WHITE, k=k2)

def ov_seagull(d, lt, t, s):
    k = clamp(pop((lt - 0.2) / 0.3))
    if k <= 0.02: return
    card(d, 70, 400, W - 70, 980)
    text(d, CX, 455, "STARTING PRICE vs AVERAGE PRICE", 36, WHITE)
    g = smooth((lt - 1.2) / 0.9)
    text(d, 120, 545, "BYD SEAGULL, CHINA (Oct 2026)", 32, GREY, anchor="lm")
    rect(d, 120, 575, 120 + 130 * g + 10, 645, GREEN, r=20)
    if g > 0.9: text(d, 290, 610, "65,900 yuan  (<$10k)", 46, WHITE, anchor="lm")
    b = lt - sent(s, 1)
    if b > 0:
        g2 = smooth(b / 0.9)
        text(d, 120, 730, "AVERAGE NEW ELECTRIC CAR, USA", 32, GREY, anchor="lm")
        rect(d, 120, 760, 120 + 720 * g2 + 10, 830, ORANGE, r=20)
        if g2 > 0.9: text(d, 600, 795, "$56,220", 52, INK, anchor="mm")
        text(d, CX, 925, "Kelley Blue Book, October 2026", 28, GREY, name="Inter-SemiBold.otf")

def ov_tariff(d, lt, t, s):
    pill(d, CX, 420, "WALL #1: TARIFFS", 70, YELLOW, k=clamp(pop(lt / 0.3)))
    b = lt - sent(s, 1)
    if b > 0:
        k = clamp(pop(b / 0.3))
        n = 100 * smooth(b / 1.2)
        text(d, CX, 620, f"{n:.0f}%+", 210 * k, WHITE, stroke=14)
        text(d, CX, 780, "IMPORT TAXES ON CHINESE-MADE EVs", 40, YELLOW, stroke=8)

def ov_software(d, lt, t, s):
    pill(d, CX, 420, "WALL #2: SOFTWARE", 70, LIME, k=clamp(pop(lt / 0.3)))
    b = lt - sent(s, 1)
    if b > 0 and lt < sent(s, 2):
        k = clamp(pop(b / 0.3))
        card(d, 120, 520, W - 120, 860)
        text(d, CX, 600, "MODEL YEAR", 44, GREY)
        text(d, CX, 710, "2027", 150 * k, WHITE)
        text(d, CX, 820, "US Commerce Dept. rule, Jan 2025", 28, GREY, name="Inter-SemiBold.otf")
    c = lt - sent(s, 2)
    if c > 0:
        pill(d, CX, 600, "DATA LEAKS?", 66, ORANGE, k=clamp(pop(c / 0.3)))
        pill(d, CX, 760, "REMOTE CONTROL?", 66, RED, fg=WHITE, k=clamp(pop((c - 1.6) / 0.3)))

def ov_world(d, lt, t, s):
    pill(d, CX, 420, "MEANWHILE IN CANADA", 66, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - 1.0
    if a > 0:
        card(d, 120, 520, W - 120, 940)
        g = smooth(a / 1.0)
        v = 100 - (100 - 6.1) * g
        text(d, 300, 600, "TARIFF", 40, GREY)
        text(d, 300, 720, f"{v:.1f}%" if g > 0.95 else f"{v:.0f}%", 110, LIME if g > 0.95 else WHITE)
        text(d, 300, 610 + 0, "", 10, WHITE)
        b = lt - 2.4
        if b > 0:
            n = int(49000 * smooth(b / 1.0))
            text(d, 780, 600, "CARS / YEAR", 40, GREY)
            text(d, 780, 720, f"{n:,}", 100, WHITE)
        text(d, CX, 880, "Canada-China deal, Jan 2026 (was 100%)", 28, GREY, name="Inter-SemiBold.otf")

def ov_ending(d, lt, t, s):
    k = clamp(pop(lt / 0.3))
    pill(d, CX, 430, "JOBS + DATA", 62, LIME, k=k)
    k2 = clamp(pop((lt - sent(s, 1)) / 0.3))
    if k2 > 0.02: pill(d, CX, 560, "HIGHER PRICES", 62, ORANGE, k=k2)
    c = lt - sent(s, 2)
    if c > 0: text(d, CX, 740, "LET THEM IN?", 110 * clamp(pop(c / 0.3)), WHITE, stroke=12)
    e = lt - sent(s, 3)
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
