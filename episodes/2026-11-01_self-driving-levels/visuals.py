# Episode visuals: The numbers — SAE levels of driving automation, 0 to 5.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
ROAD = (30, 36, 46)
RED = (255, 84, 84)

def sdur(name):
    for s in scenes:
        if s["visual"] == name:
            return s["vis_end"] - s["start"]
    return 4.0

def poly(d, pts, col):
    d.polygon(p(*[v for xy in pts for v in xy]), fill=col)

def bolt(d, bx, by, bs, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(bx + xx * bs, by + yy * bs) for xx, yy in pts], col)

def panel(d, x0, y0, x1, y1, a=1.0, outline=None, r=28):
    d.rounded_rectangle(p(x0 + 6, y0 + 10, x1 + 6, y1 + 10), radius=r * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=r * S, fill=rgba(PANEL, 0.94 * a),
                        outline=rgba(outline or DARK, a), width=int(4 * S))

def label(d, x, y, s, col, a, size=28, bold="Inter-SemiBold.otf"):
    text_c(d, x, y, s, FL(bold, size), rgba(col, a))

def ladder(d, lt, active, a=1.0, y=20):
    """Row of six level chips 0..5; `active` may be a float (lights chips <= active) or a set."""
    for i in range(6):
        k = ease_out((lt - i * 0.06) / 0.35)
        x0 = 105 + i * 120
        on = (i in active) if isinstance(active, (set, tuple, list)) else False
        col = ACC if on else DARK
        d.rounded_rectangle(p(x0, y, x0 + 90, y + 90), radius=20 * S, fill=rgba(PANEL, a * k),
                            outline=rgba(col, a * k), width=int((5 if on else 3) * S))
        if on:
            d.rounded_rectangle(p(x0 - 8, y - 8, x0 + 98, y + 98), radius=26 * S,
                                outline=rgba(ACC, a * k * (0.25 + 0.2 * math.sin(lt * 5))), width=int(4 * S))
        text_c(d, x0 + 45, y + 8, str(i), FL("InterDisplay-Black.otf", 60), rgba(ACC if on else MUTED, a * k))

def wheel_icon(d, cx, cy, r, a, rot=0.0, col=WHITE):
    arc(d, cx, cy, r, 0, 360, rgba(col, a), 16)
    d.ellipse(p(cx - r * 0.22, cy - r * 0.22, cx + r * 0.22, cy + r * 0.22), fill=rgba(col, a))
    for k in (math.pi / 2, math.pi * 7 / 6, math.pi * 11 / 6):
        ang = k + rot
        d.line(p(cx, cy, cx + math.cos(ang) * r * 0.9, cy + math.sin(ang) * r * 0.9), fill=rgba(col, a), width=int(12 * S))

def hands(d, cx, cy, r, a, off=0.0):
    """Two hands gripping the wheel at 9 and 3; off>0 lifts them away."""
    for sgn in (-1, 1):
        hx = cx + sgn * (r + off * 70)
        hy = cy - off * 90
        d.ellipse(p(hx - 30, hy - 36, hx + 30, hy + 36), fill=rgba(ACC2, a))
        d.ellipse(p(hx - 30, hy - 36, hx + 30, hy + 36), outline=rgba((0, 0, 0), a * 0.5), width=int(3 * S))

def eye(d, cx, cy, sc, a, col=WHITE, open_=1.0):
    h = 34 * sc * open_
    poly(d, [(cx - 70 * sc, cy), (cx - 35 * sc, cy - h), (cx + 35 * sc, cy - h), (cx + 70 * sc, cy),
             (cx + 35 * sc, cy + h), (cx - 35 * sc, cy + h)], rgba(col, a))
    if open_ > 0.3:
        d.ellipse(p(cx - 22 * sc, cy - 22 * sc, cx + 22 * sc, cy + 22 * sc), fill=rgba(BG, a))
        d.ellipse(p(cx - 9 * sc, cy - 9 * sc, cx + 9 * sc, cy + 9 * sc), fill=rgba(ACC, a))

def car_top(d, cx, cy, sc, a, col=WHITE, driver=True, drv_col=ACC2):
    w, h = 58 * sc, 110 * sc
    d.rounded_rectangle(p(cx - w + 4, cy - h + 8, cx + w + 4, cy + h + 8), radius=30 * S * sc, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(cx - w, cy - h, cx + w, cy + h), radius=30 * S * sc, fill=rgba(col, a))
    d.rounded_rectangle(p(cx - w * 0.75, cy - h * 0.55, cx + w * 0.75, cy - h * 0.15), radius=10 * S * sc, fill=rgba(BG, a))
    d.rounded_rectangle(p(cx - w * 0.75, cy + h * 0.35, cx + w * 0.75, cy + h * 0.6), radius=10 * S * sc, fill=rgba(BG, a))
    sx = cx - w * 0.38
    if driver:
        d.ellipse(p(sx - 16 * sc, cy - 14 * sc, sx + 16 * sc, cy + 18 * sc), fill=rgba(drv_col, a))
    else:
        d.ellipse(p(sx - 16 * sc, cy - 14 * sc, sx + 16 * sc, cy + 18 * sc), outline=rgba(MUTED, a), width=int(3 * S))
    for hx in (-1, 1):
        d.ellipse(p(cx + hx * w * 0.6 - 9 * sc, cy - h + 2, cx + hx * w * 0.6 + 9 * sc, cy - h + 16 * sc), fill=rgba(ACC, a))

def warn_tri(d, cx, cy, s, a, col=ACC2):
    poly(d, [(cx, cy - s), (cx + s * 1.1, cy + s * 0.8), (cx - s * 1.1, cy + s * 0.8)], rgba(col, a))
    d.line(p(cx, cy - s * 0.4, cx, cy + s * 0.25), fill=rgba(BG, a), width=int(8 * S))
    d.ellipse(p(cx - 5, cy + s * 0.45, cx + 5, cy + s * 0.65), fill=rgba(BG, a))

def pill(d, cx, cy, w, txt, fill, a, size=32, tcol=BG):
    d.rounded_rectangle(p(cx - w / 2, cy - 34, cx + w / 2, cy + 34), radius=34 * S, fill=rgba(fill, a))
    text_c(d, cx, cy - size * 0.62, txt, FL("InterDisplay-Black.otf", size), rgba(tcol, a))

# ---------- scene 1: hook — counter 0→5 and a car steering itself ----------
def vis_lv_hook(d, lt, t):
    a = ease_out(lt / 0.35)
    # wheel turning by itself
    rot = math.sin(lt * 2.2) * 0.6
    wheel_icon(d, 450, 300, 120, a, rot)
    # "?" orbiting badge
    q = back_out((lt - 1.4) / 0.5)
    if q > 0:
        d.ellipse(p(590, 150, 690, 250), fill=rgba(ACC2, clamp(q)))
        text_c(d, 640, 158, "?", FL("InterDisplay-Black.otf", max(1, int(70 * q))), rgba(BG, clamp(q)))
        label(d, 450, 460, "SELF-DRIVING?", WHITE, clamp(q), 60, "InterDisplay-Black.otf")
    # scale builds: 0..5 counter
    k = ease_out((lt - 3.2) / 1.6)
    if lt > 3.0:
        n = int(min(5, k * 5.999))
        ladder(d, lt - 3.0, set(range(n + 1)), 1.0, y=560)
        label(d, 450, 690, "THE SAE SCALE", MUTED, ease_out((lt - 4.2) / 0.4), 34, "InterDisplay-Bold.otf")

# ---------- scene 2: level 0 — you drive, warnings don't count ----------
def vis_lv_zero(d, lt, t):
    a = ease_out(lt / 0.35)
    ladder(d, lt, {0}, a)
    wheel_icon(d, 450, 330, 120, a, math.sin(t * 1.5) * 0.25)
    hands(d, 450, 330, 120, a)
    pill(d, 450, 520, 330, "YOU DRIVE", ACC2, ease_out((lt - 0.6) / 0.4), 38)
    # warnings appear and are crossed: still level 0
    items = [("BEEP", 2.0), ("AUTO BRAKE", 3.0)]
    for i, (txt, st) in enumerate(items):
        k = ease_out((lt - st) / 0.4)
        if k <= 0:
            continue
        x = 250 + i * 400
        panel(d, x - 170, 620, x + 170, 760, k, r=24)
        if i == 0:
            warn_tri(d, x - 105, 690, 34 * (1 + 0.12 * math.sin(t * 10)), k)
        else:
            d.ellipse(p(x - 140, 655, x - 70, 725), outline=rgba(RED, k), width=int(8 * S))
            label(d, x - 105, 668, "!", RED, k, 40, "InterDisplay-Black.otf")
        label(d, x + 35, 670, txt, WHITE, k, 30 if i else 38, "InterDisplay-Black.otf")
    c = back_out((lt - 4.0) / 0.5)
    if c > 0:
        label(d, 450, 790, "STILL LEVEL 0", ACC, clamp(c), 44, "InterDisplay-Black.otf")

# ---------- scene 3: levels 1 & 2 — steering OR speed, then both, eyes on road ----------
def vis_lv_onetwo(d, lt, t):
    a = ease_out(lt / 0.35)
    dur = sdur("lv_onetwo")
    lvl2 = lt > dur * 0.42
    ladder(d, lt, {2} if lvl2 else {1}, a)
    # two function tiles
    tiles = [("STEERING", 220), ("SPEED", 680)]
    for i, (name, x) in enumerate(tiles):
        on = (i == 0 and lt > 0.8) or (i == 1 and lvl2)
        if not lvl2 and i == 1 and lt > 0.8:
            alt = (math.sin(lt * 3.5) > 0)          # level 1: one OR the other
            on = alt
            tiles_on0 = not alt
        k = ease_out((lt - 0.2 - i * 0.15) / 0.4)
        panel(d, x - 150, 160, x + 150, 420, k, outline=ACC if on else DARK)
        if i == 0:
            wheel_icon(d, x, 260, 62, k, math.sin(t * 2) * 0.5 if on else 0, ACC if on else MUTED)
        else:
            arc(d, x, 285, 70, 180, 360, rgba(ACC if on else MUTED, k), 12)
            ang = math.pi + (0.5 + 0.4 * math.sin(t * 2)) * math.pi if on else math.pi * 1.2
            d.line(p(x, 285, x + math.cos(ang) * 58, 285 + math.sin(ang) * 58), fill=rgba(ACC2, k), width=int(8 * S))
        label(d, x, 345, name, ACC if on else MUTED, k, 34, "InterDisplay-Black.otf")
    # level 1: steering tile follows the alternation too
    if not lvl2 and lt > 0.8 and math.sin(lt * 3.5) > 0:
        d.rounded_rectangle(p(70, 160, 370, 420), radius=28 * S, fill=rgba(PANEL, 0.75))
        wheel_icon(d, 220, 260, 62, 0.9, 0, MUTED)
        label(d, 220, 345, "STEERING", MUTED, 1, 34, "InterDisplay-Black.otf")
    mid = "AND" if lvl2 else "OR"
    label(d, 450, 255, mid, ACC2, ease_out((lt - 0.8) / 0.3), 52, "InterDisplay-Black.otf")
    # eye: you must watch the road
    e = ease_out((lt - dur * 0.6) / 0.5)
    if e > 0:
        eye(d, 450, 560, 1.4, e, WHITE, 0.6 + 0.4 * abs(math.sin(t * 1.3)))
        label(d, 450, 650, "EYES ON THE ROAD", ACC2, e, 46, "InterDisplay-Black.otf")
        label(d, 450, 715, "you are still the driver", MUTED, e, 30)

# ---------- scene 4: level 3 — car drives in limited conditions, takeover request ----------
def vis_lv_three(d, lt, t):
    a = ease_out(lt / 0.35)
    dur = sdur("lv_three")
    ladder(d, lt, {3}, a)
    # highway, top view scrolling
    x0, x1 = 250, 650
    d.rounded_rectangle(p(x0, 150, x1, 640), radius=20 * S, fill=rgba(ROAD, a))
    off = (t * 260) % 80
    for lx in (383, 517):
        y = 150 - 80 + off
        while y < 640:
            if y + 40 > 150:
                d.line(p(lx, max(150, y), lx, min(640, y + 40)), fill=rgba(WHITE, a * 0.7), width=int(6 * S))
            y += 80
    req = dur * 0.62
    alarm = lt > req
    car_top(d, 450, 420, 1.0, a, WHITE, driver=True, drv_col=ACC2 if alarm else MUTED)
    # car-drives bubble
    k = ease_out((lt - 0.6) / 0.4)
    pill(d, 450, 205, 300, "CAR DRIVES", ACC, k * (1 - ease_out((lt - req) / 0.3)), 34)
    # conditions tags
    for i, txt in enumerate(["LIMITED", "CONDITIONS"]):
        c = ease_out((lt - 1.2 - i * 0.2) / 0.4)
        label(d, 145 if i == 0 else 755, 360, txt, MUTED, c, 26, "InterDisplay-Bold.otf")
    if alarm:
        fl = 0.6 + 0.4 * math.sin((lt - req) * 14)
        d.rounded_rectangle(p(x0 - 10, 140, x1 + 10, 650), radius=26 * S, outline=rgba(ACC2, fl), width=int(8 * S))
        pill(d, 450, 205, 420, "TAKE OVER NOW", ACC2, ease_out((lt - req) / 0.25), 36)
        h = ease_out((lt - req - 0.6) / 0.5)
        label(d, 450, 700, "YOU TAKE OVER", WHITE, h, 46, "InterDisplay-Black.otf")
        label(d, 450, 765, "only when it asks", MUTED, h, 30)

# ---------- scene 5: level 4 — no driver, geofenced zone, safe stop ----------
def vis_lv_four(d, lt, t):
    a = ease_out(lt / 0.35)
    dur = sdur("lv_four")
    ladder(d, lt, {4}, a)
    # zone polygon draws in
    zone = [(170, 230), (520, 160), (740, 300), (700, 600), (330, 660), (150, 470)]
    k = ease_out((lt - 0.2) / 0.8)
    pts = zone + [zone[0]]
    for i in range(len(zone)):
        seg = clamp(k * len(zone) - i)
        if seg <= 0:
            continue
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        d.line(p(xa, ya, xa + (xb - xa) * seg, ya + (yb - ya) * seg), fill=rgba(ACC, a), width=int(6 * S))
    if k >= 1:
        poly(d, zone, rgba(ACC, 0.08 + 0.04 * math.sin(t * 3)))
        label(d, 450, 680, "SET CONDITIONS", ACC, ease_out((lt - 1.0) / 0.4), 30, "InterDisplay-Black.otf")
    # car path loop inside zone
    stop_t = dur * 0.6
    tt = min(lt, stop_t)
    ang = tt * 1.1
    cx, cy = 440 + math.cos(ang) * 170, 430 + math.sin(ang) * 120
    d.ellipse(p(270, 310, 610, 550), outline=rgba(MUTED, a * 0.35), width=int(3 * S))
    # draw car as a small top view (rotated look via scaling not needed — keep upright)
    car_top(d, cx, cy, 0.55, a, WHITE, driver=False)
    e = ease_out((lt - 0.8) / 0.4)
    pill(d, 450, 775, 360, "NO DRIVER", WHITE, e * (1 - ease_out((lt - stop_t) / 0.3)), 38)
    if lt > stop_t:
        blink = 1.0 if int((lt - stop_t) * 4) % 2 == 0 else 0.35
        for hx in (-1, 1):
            d.ellipse(p(cx + hx * 22 - 10, cy - 62, cx + hx * 22 + 10, cy - 42), fill=rgba(ACC2, blink))
        warn_tri(d, cx + 85, cy - 40, 26, ease_out((lt - stop_t) / 0.3))
        pill(d, 450, 775, 380, "STOPS SAFELY", ACC2, ease_out((lt - stop_t - 0.2) / 0.3), 38)

# ---------- scene 6: level 5 — anywhere, any weather, not built ----------
def vis_lv_five(d, lt, t):
    a = ease_out(lt / 0.35)
    ladder(d, lt, {5}, a)
    icons = ["SNOW", "RAIN", "NIGHT", "DIRT"]
    for i, name in enumerate(icons):
        k = back_out((lt - 0.3 - i * 0.25) / 0.45)
        if k <= 0:
            continue
        x = 180 + i * 180
        y = 260
        panel(d, x - 75, y - 75, x + 75, y + 95, clamp(k), r=24)
        c = rgba(WHITE, clamp(k))
        if name == "SNOW":
            for j in range(3):
                ang = j * math.pi / 3 + t * 0.6
                d.line(p(x - math.cos(ang) * 38, y - math.sin(ang) * 38, x + math.cos(ang) * 38, y + math.sin(ang) * 38), fill=c, width=int(7 * S))
        elif name == "RAIN":
            for j in range(4):
                yy = y - 40 + ((t * 120 + j * 23) % 80)
                xx = x - 36 + j * 24
                d.line(p(xx, yy, xx - 8, yy + 22), fill=rgba(ACC, clamp(k)), width=int(6 * S))
        elif name == "NIGHT":
            d.ellipse(p(x - 36, y - 36, x + 36, y + 36), fill=c)
            d.ellipse(p(x - 14, y - 46, x + 50, y + 18), fill=rgba(PANEL, clamp(k)))
        else:
            for j in range(3):
                d.line(p(x - 40, y + 20 - j * 22 + 8 * math.sin(t * 3 + j), x + 40, y + 20 - j * 22 - 8 * math.sin(t * 3 + j)), fill=rgba(ACC2, clamp(k)), width=int(7 * S))
        label(d, x, y + 50, name, MUTED, clamp(k), 24, "InterDisplay-Bold.otf")
    label(d, 450, 420, "ANY ROAD · ANY WEATHER", WHITE, ease_out((lt - 1.4) / 0.4), 40, "InterDisplay-Black.otf")
    s = back_out((lt - 2.2) / 0.45)
    if s > 0:
        w = 520 * clamp(s, 0, 1.2)
        d.rounded_rectangle(p(450 - w / 2, 520, 450 + w / 2, 640), radius=20 * S, outline=rgba(RED, clamp(s)), width=int(8 * S))
        text_c(d, 450, 538, "NOT BUILT YET", FL("InterDisplay-Black.otf", max(1, int(66 * min(1, s)))), rgba(RED, clamp(s)))

# ---------- scene 7: responsibility split + end card ----------
def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

def vis_lv_outro(d, lt, t):
    dur = sdur("lv_outro")
    cut = dur * 0.66
    if lt < cut:
        a = 1 - ease_inout((lt - cut + 0.3) / 0.3)
        label(d, 450, 40, "WHO IS RESPONSIBLE?", WHITE, a * ease_out(lt / 0.4), 46, "InterDisplay-Black.otf")
        # six bars: orange = you, lime = car
        you = [1.0, 0.85, 0.7, 0.35, 0.0, 0.0]
        for i in range(6):
            k = ease_out((lt - 0.3 - i * 0.18) / 0.5)
            x = 120 + i * 120
            top, bot = 140, 560
            hgt = (bot - top) * k
            yv = you[i]
            ys = bot - hgt * yv
            d.rounded_rectangle(p(x, bot - hgt, x + 90, bot), radius=14 * S, fill=rgba(ACC, a * 0.9))
            if yv > 0:
                d.rounded_rectangle(p(x, ys, x + 90, bot), radius=14 * S, fill=rgba(ACC2, a))
            text_c(d, x + 45, 575, str(i), FL("InterDisplay-Black.otf", 48), rgba(WHITE, a * k))
        c = ease_out((lt - 1.6) / 0.4)
        d.rounded_rectangle(p(170, 660, 210, 700), radius=8 * S, fill=rgba(ACC2, a * c))
        label(d, 290, 660, "YOU", WHITE, a * c, 34, "InterDisplay-Black.otf")
        d.rounded_rectangle(p(500, 660, 540, 700), radius=8 * S, fill=rgba(ACC, a * c))
        label(d, 620, 660, "THE CAR", WHITE, a * c, 34, "InterDisplay-Black.otf")
        q = back_out((lt - 3.2) / 0.5)
        if q > 0:
            label(d, 450, 760, "WOULD YOU LET GO?", ACC, a * clamp(q), 48, "InterDisplay-Black.otf")
    else:
        end_card(d, lt, cut)

VIS.update({"lv_hook": vis_lv_hook, "lv_zero": vis_lv_zero, "lv_onetwo": vis_lv_onetwo,
            "lv_three": vis_lv_three, "lv_four": vis_lv_four, "lv_five": vis_lv_five,
            "lv_outro": vis_lv_outro})
