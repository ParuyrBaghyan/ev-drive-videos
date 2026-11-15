# Overlays for "This Chinese SUV Can Spin Like a Tank. And Float" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)
BLUE = (90, 170, 255)

def wt(s, word, n=0):
    """Start time (scene-local) of the n-th spoken word that starts with `word`."""
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def topcar(d, cx, cy, ang, sc, wheel_cols=None, motors=0.0, arrows=0.0):
    """Generic top-down car: body + 4 wheels, rotated by ang (radians). Not a real model."""
    ca, sa = math.cos(ang), math.sin(ang)
    def P(x, y): return (cx + (x * ca - y * sa) * sc, cy + (x * sa + y * ca) * sc)
    def poly(pts, fill, ol=INK, w=6): d.polygon([P(*p) for p in pts], fill=fill, outline=ol, width=w)
    bw, bl = 1.0, 2.1
    wl = [(-1.12, -1.35), (1.12, -1.35), (-1.12, 1.35), (1.12, 1.35)]
    for i, (x, y) in enumerate(wl):
        col = wheel_cols[i] if wheel_cols else (40, 42, 52)
        poly([(x - .22, y - .42), (x + .22, y - .42), (x + .22, y + .42), (x - .22, y + .42)], col, ol=INK)
    poly([(-bw, -bl + .35), (-bw + .35, -bl), (bw - .35, -bl), (bw, -bl + .35), (bw, bl - .25), (bw - .25, bl), (-bw + .25, bl), (-bw, bl - .25)], (236, 238, 244))
    poly([(-.78, -1.2), (.78, -1.2), (.68, -.55), (-.68, -.55)], (60, 70, 90), w=3)
    poly([(-.72, .9), (.72, .9), (.64, 1.4), (-.64, 1.4)], (60, 70, 90), w=3)
    if motors > 0.02:
        for (x, y) in wl:
            mx = x * 0.62
            px, py = P(mx, y)
            r = 34 * sc / 110 * clamp(pop(motors))
            d.ellipse((px - r, py - r, px + r, py + r), fill=LIME, outline=INK, width=4)
            text(d, px, py, "M", r * 1.1, INK)
    if arrows > 0.02:
        for (x, y) in wl:
            f = 1 if x < 0 else -1    # left wheels forward (towards the nose, -y), right wheels backward
            ox = x * 1.0 + (-.55 if x < 0 else .55)
            a0, a1 = P(ox, y + 0.45 * f), P(ox, y - 0.45 * f)
            col = GREEN if x < 0 else ORANGE
            a1 = (a0[0] + (a1[0] - a0[0]) * clamp(arrows), a0[1] + (a1[1] - a0[1]) * clamp(arrows))
            d.line([a0, a1], fill=col, width=14)
            vx, vy = a1[0] - a0[0], a1[1] - a0[1]; L = math.hypot(vx, vy) or 1
            ux, uy = vx / L, vy / L
            hd = [(a1[0] + ux * 26, a1[1] + uy * 26), (a1[0] - uy * 22, a1[1] + ux * 22), (a1[0] + uy * 22, a1[1] - ux * 22)]
            d.polygon(hd, fill=col, outline=INK)

def ov_hook(d, lt, t, s):
    pill(d, CX, 420, "THIS CHINESE SUV", 60, YELLOW, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - 0.8) / 0.3))
    if k > 0.02:
        text(d, CX, 575, "SPINS LIKE", 120 * k, WHITE, stroke=14)
        text(d, CX, 715, "A TANK", 150 * k, WHITE, stroke=14)
    k2 = clamp(pop((lt - sent(s, 1) - 0.9) / 0.3))
    if k2 > 0.02: pill(d, CX, 890, "...AND FLOATS", 70, BLUE, fg=INK, k=k2)

def ov_motors(d, lt, t, s):
    k = clamp(pop((lt - 0.2) / 0.3))
    pill(d, CX, 420, "YANGWANG U8", 66, WHITE, k=k)
    if k > 0.5 and lt < sent(s, 1):
        text(d, CX, 530, "a luxury brand owned by BYD", 40, YELLOW, stroke=8)
        text(d, CX, 600, "on sale in China since 2023", 34, GREY, stroke=6, name="Inter-SemiBold.otf")
    b = lt - sent(s, 1)
    if b > 0:
        card(d, 230, 480, W - 230, 1010)
        topcar(d, CX, 720, 0, 105, motors=b / 0.5)
        text(d, CX, 960, "4 MOTORS · 1 PER WHEEL", 40, LIME)

def ov_tank(d, lt, t, s):
    pill(d, CX, 420, "THE TANK TURN", 66, YELLOW, k=clamp(pop(lt / 0.3)))
    card(d, 190, 500, W - 190, 1040)
    a = lt - wt(s, "left")
    arrows = a / 0.4 if a > 0 else 0
    c = lt - wt(s, "whole")
    ang = 0.0 if c < 0 else (c * 1.6)
    topcar(d, CX, 715, ang, 80, arrows=arrows)
    if a > 0:
        text(d, CX, 960, "LEFT WHEELS: FORWARD", 32, GREEN)
        text(d, CX, 1005, "RIGHT WHEELS: BACKWARD", 32, ORANGE)

def ov_float(d, lt, t, s):
    pill(d, CX, 420, "EMERGENCY FLOAT MODE", 58, BLUE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "thirty") + 0.1
    if a > 0:
        card(d, 90, 510, W - 90, 960)
        n = int(30 * smooth(a / 0.8))
        text(d, 300, 590, "AFLOAT", 38, GREY)
        text(d, 300, 700, f"~{n} min", 92, WHITE)
        b = lt - wt(s, "three") + 0.1
        if b > 0:
            k = clamp(pop(b / 0.3))
            text(d, 780, 590, "SPEED", 38, GREY)
            text(d, 780, 700, "~3 km/h", 92 * k, LIME)
            text(d, 780, 780, "(about 1.8 mph)", 30, GREY, name="Inter-SemiBold.otf")
        text(d, CX, 900, "BYD at launch, Sept 2023 · emergency use only", 28, GREY, name="Inter-SemiBold.otf")

def ov_catch(d, lt, t, s):
    pill(d, CX, 420, "THE CATCH", 72, RED, fg=WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "hundred")
    if a > 0:
        text(d, CX, 600, "$150,000+", 150 * clamp(pop(a / 0.3)), WHITE, stroke=14)
    b = lt - wt(s, "plug")
    if b > 0:
        pill(d, CX, 790, "PLUG-IN HYBRID", 62, ORANGE, k=clamp(pop(b / 0.3)))
        c = lt - wt(s, "gas")
        if c > 0: text(d, CX, 920, "+ GAS ENGINE ON BOARD", 46 * clamp(pop(c / 0.3)), YELLOW, stroke=8)

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "LIFE-SAVER", 62, LIME, k=clamp(pop(lt / 0.3)))
    k2 = clamp(pop((lt - wt(s, "party")) / 0.3))
    if k2 > 0.02: pill(d, CX, 560, "PARTY TRICK", 62, ORANGE, k=k2)
    c = lt - sent(s, 1)
    if c > 0: text(d, CX, 740, "WHICH ONE?", 110 * clamp(pop(c / 0.3)), WHITE, stroke=12)
    e = lt - sent(s, 2)
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
