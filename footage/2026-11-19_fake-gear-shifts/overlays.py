# Overlays for "This Electric Car Fakes 8 Gears On Purpose. Here's Why" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)
BLUE = (90, 170, 255)

def wt(s, word, n=0):
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!:'").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def ov_hook(d, lt, t, s):
    pill(d, CX, 420, "ELECTRIC CAR", 56, WHITE, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "one")) / 0.3))
    if k > 0.02: text(d, CX, 580, "1 GEAR", 150 * k, LIME, stroke=14)
    a = lt - sent(s, 1)
    if a > 0:
        k2 = clamp(pop((lt - wt(s, "eight")) / 0.35))
        if k2 > 0.02: text(d, CX, 800, "8 SHIFTS?", 160 * k2, YELLOW, stroke=16)

def ov_hyundai(d, lt, t, s):
    pill(d, CX, 420, "HYUNDAI IONIQ 5 N", 56, WHITE, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "six")) / 0.3))
    if k > 0.02: text(d, CX, 560, "~600 HP", 120 * k, LIME, stroke=12)
    a = lt - sent(s, 1)
    if a > 0:
        card(d, 90, 650, W - 90, 1000)
        text(d, CX, 700, "MOTOR POWER", 40, GREY)
        # power trace with a dip at each fake shift
        x0, x1, yb, yt = 140, W - 140, 960, 760
        prog = clamp((lt - wt(s, "cuts")) / 2.5)
        pts = []
        n = 120
        for i in range(int(n * prog) + 1):
            f = i / n
            y = yt + 40 + 30 * f
            for c in (0.3, 0.6, 0.85):
                if abs(f - c) < 0.025: y = yb - 30
            pts.append((x0 + (x1 - x0) * f, y))
        if len(pts) > 1: d.line(pts, fill=YELLOW, width=10, joint="curve")
        b = lt - wt(s, "eight")
        if b > 0: pill(d, CX, 1040, "FAKE 8-SPEED SHIFTS", 48, YELLOW, fg=INK, k=clamp(pop(b / 0.3)))

def ov_limiter(d, lt, t, s):
    k0 = clamp(pop(lt / 0.3))
    if lt < wt(s, "rev"): pill(d, CX, 430, "FORGET TO SHIFT?", 58, WHITE, k=k0)
    k = clamp(pop((lt - wt(s, "rev")) / 0.3))
    if k > 0.02:
        pill(d, CX, 430, "FAKE REV LIMITER", 58, RED, fg=WHITE, k=k)
        # tachometer bar bouncing at redline
        card(d, 90, 520, W - 90, 680)
        bounce = 0.93 + 0.05 * abs(((lt * 6) % 2) - 1)
        rect(d, 130, 570, 130 + (W - 260) * bounce * smooth(k), 630, ORANGE, r=12)
        rect(d, 130 + (W - 260) * 0.85, 560, W - 130, 640, (255, 60, 60, 90), r=12)
    a = lt - wt(s, "ten")
    if a > 0:
        kk = clamp(pop(a / 0.3))
        text(d, CX, 820, "10 SPEAKERS", 120 * kk, YELLOW, stroke=12)
        text(d, CX, 940, "playing a fake engine", 44, WHITE, stroke=6)

def ov_dodge(d, lt, t, s):
    pill(d, CX, 420, "DODGE CHARGER (ELECTRIC)", 50, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "sound")
    if a > 0: pill(d, CX, 540, "SOUND BOX AT THE BACK", 46, ORANGE, fg=INK, k=clamp(pop(a / 0.3)))
    b = lt - sent(s, 1)
    if b > 0:
        k = clamp(pop((lt - wt(s, "one")) / 0.35))
        if k > 0.02: text(d, CX, 720, "126 dB", 190 * k, YELLOW, stroke=16)
        c = lt - wt(s, "hellcat")
        if c > 0:
            pill(d, CX, 890, "AS LOUD AS A HELLCAT", 54, RED, fg=WHITE, k=clamp(pop(c / 0.3)))
            text(d, CX, 980, "Dodge figure, via Green Car Reports", 30, GREY, name="Inter-SemiBold.otf")

def ov_why(d, lt, t, s):
    pill(d, CX, 420, "WHY FAKE IT?", 60, YELLOW, fg=INK, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "hyundai")
    if a > 0:
        card(d, 90, 520, W - 90, 760)
        k = clamp(pop(a / 0.3))
        text(d, CX, 600, "\"LACK OF DRIVER", 64 * k, WHITE, stroke=8)
        text(d, CX, 690, "FEEDBACK\"", 64 * k, WHITE, stroke=8)
        text(d, CX, 740, "Hyundai", 30, GREY, name="Inter-SemiBold.otf")
    b = lt - sent(s, 2)
    if b > 0:
        pill(d, CX, 860, "COMING TO MORE MODELS", 52, LIME, fg=INK, k=clamp(pop(b / 0.3)))
        if b > 0.3: text(d, CX, 960, "Ioniq 9 · Ioniq 6 N · Genesis (Edmunds)", 32, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "IT CAN BE SWITCHED OFF", 52, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "fun")
    if a > 0:
        k = clamp(pop(a / 0.3))
        text(d, CX, 570, "FUN", 140 * k, LIME, stroke=14)
        text(d, CX, 665, "or", 60 * k, WHITE, stroke=8)
        c = lt - wt(s, "fake")
        if c > 0: text(d, CX, 760, "FAKE?", 140 * clamp(pop(c / 0.3)), RED, stroke=14)
    k2 = clamp(pop((lt - wt(s, "tell")) / 0.3))
    if k2 > 0.02: pill(d, CX, 900, "TELL ME BELOW ↓", 64, YELLOW, fg=INK, k=k2)
    e = lt - wt(s, "follow")
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
