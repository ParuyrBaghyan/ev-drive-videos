# Overlays for "Tesla Sells Fewer Cars Every Year. So Why Is It Worth So Much?" (runs inside tools/render_footage.py globals).
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
    if k > 0.3: text(d, min(x0 + w + 16, x1 - 10) if val / vmax < 0.5 else x0 + 18, y + 24, shown, 36, WHITE if val / vmax < 0.5 else INK, anchor="lm", stroke=6 if val / vmax < 0.5 else 0)

def ov_hook(d, lt, t, s):
    pill(d, CX, 400, "TOYOTA vs TESLA", 58, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "six")
    if a > 0:
        card(d, 90, 455, W - 90, 1010)
        text(d, CX, 500, "CARS SOLD IN 2025", 38, GREY)
        hbar(d, 575, "Toyota", 10.5, 10.5, LIME, clamp(a / 0.6), "10.5 MILLION")
        hbar(d, 675, "Tesla", 1.64, 10.5, RED, clamp(a / 0.6), "1.64 MILLION")
    b = lt - sent(s, 1)
    if b > 0:
        text(d, CX, 770, "COMPANY VALUE · NOV 2026", 38, GREY)
        hbar(d, 845, "Toyota", 0.25, 1.5, ORANGE, clamp(b / 0.6), "$0.25 TRILLION")
        hbar(d, 945, "Tesla", 1.5, 1.5, LIME, clamp(b / 0.6), "$1.5 TRILLION")

def ov_sales(d, lt, t, s):
    pill(d, CX, 420, "TESLA DELIVERIES", 56, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "peaked")
    if a > 0:
        text(d, CX, 580, "1.81M", 150 * clamp(pop(a / 0.3)), LIME, stroke=14)
        text(d, CX, 680, "2023 · THE PEAK", 40, WHITE, stroke=8)
    b = lt - wt(s, "fell")
    if b > 0:
        text(d, CX, 840, "1.64M", 150 * clamp(pop(b / 0.3)), RED, stroke=14)
        text(d, CX, 940, "2025 · DOWN 2 YEARS IN A ROW", 40, WHITE, stroke=8)

def ov_profit(d, lt, t, s):
    pill(d, CX, 420, "NET PROFIT · Q3 2026", 54, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "forty")
    if a > 0:
        text(d, CX, 640, "-43%", 230 * clamp(pop(a / 0.3)), RED, stroke=18)
        text(d, CX, 800, "$1.37B  →  $787M", 60, WHITE, stroke=10)
        text(d, CX, 880, "Source: Tesla Q3 2026 results, via Electrek", 30, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_reveal(d, lt, t, s):
    k = clamp(pop((lt - wt(s, "trillion")) / 0.3))
    if lt > 0: pill(d, CX, 420, "TESLA'S VALUE", 56, WHITE, k=clamp(pop(lt / 0.3)))
    if k > 0.02: text(d, CX, 580, "$1.5 TRILLION", 130 * k, LIME, stroke=14)
    a = lt - sent(s, 1)
    if a > 0: pill(d, CX, 740, "NOT A BET ON CARS", 56, YELLOW, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "robot")
    if b > 0: pill(d, CX - 210, 900, "ROBOTAXIS", 54, LIME, k=clamp(pop(b / 0.3)))
    c = lt - wt(s, "robots")
    if c > 0: pill(d, CX + 230, 900, "ROBOTS", 54, ORANGE, k=clamp(pop(c / 0.3)))

def ov_bets(d, lt, t, s):
    pill(d, CX, 420, "TESLA'S BET", 56, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "nearly")
    if a > 0:
        text(d, CX, 570, "~2 MILLION", 140 * clamp(pop(a / 0.3)), LIME, stroke=14)
        text(d, CX, 670, "ROBOTAXI MILES, NO ONE SUPERVISING", 38, WHITE, stroke=8)
    b = lt - wt(s, "research")
    if b > 0:
        card(d, 160, 760, W - 160, 990)
        text(d, CX, 810, "R&D SPENDING · Q3 2026", 38, GREY)
        text(d, CX, 910, "+69%", 130 * clamp(pop(b / 0.3)), YELLOW, stroke=10)

def ov_sides(d, lt, t, s):
    pill(d, CX, 420, "TWO SIDES", 56, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "skeptics")
    if a > 0: pill(d, CX, 600, "SKEPTICS: YEARS TO PAY OFF", 50, RED, fg=WHITE, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "fans")
    if b > 0: pill(d, CX, 780, "FANS: CARS WERE NEVER THE POINT", 46, LIME, k=clamp(pop(b / 0.3)))

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "CAR COMPANY?", 64, WHITE, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "robot")) / 0.3))
    if k > 0.02: pill(d, CX, 580, "OR ROBOT COMPANY?", 64, ORANGE, k=k)
    k2 = clamp(pop((lt - wt(s, "tell")) / 0.3))
    if k2 > 0.02: pill(d, CX, 780, "YOUR ANSWER ↓", 70, LIME, fg=INK, k=k2)
    e = lt - wt(s, "follow")
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
