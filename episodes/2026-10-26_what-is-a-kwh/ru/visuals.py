# Episode visuals: The numbers — what a kilowatt-hour actually is.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
RED = (255, 84, 84)
YEL = (255, 214, 90)

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

def glow_rect(d, x0, y0, x1, y1, r, col, a=1.0):
    for g, al in ((14, 0.07), (8, 0.12), (4, 0.2)):
        d.rounded_rectangle(p(x0 - g, y0 - g, x1 + g, y1 + g), radius=int((r + g) * S), fill=rgba(col, al * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=int(r * S), fill=rgba(col, a))

def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "ПОДПИШИСЬ НА EV DRIVE", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

def jerrycan(d, x, y, w, h, level, a=1.0, liquid=ACC2):
    """Fuel can outline (x,y = top-left of body) with liquid filled to level 0..1."""
    # handle + spout
    d.rounded_rectangle(p(x + w * 0.12, y - 46, x + w * 0.55, y + 10), radius=int(16 * S), outline=rgba(WHITE, a), width=int(8 * S))
    poly(d, [(x + w * 0.70, y + 4), (x + w * 0.80, y - 50), (x + w * 0.95, y - 44), (x + w * 0.90, y + 10)], rgba(WHITE, a))
    # body
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=int(26 * S), fill=rgba(PANEL, a), outline=rgba(WHITE, a), width=int(8 * S))
    if level > 0.01:
        top = y + h - 10 - (h - 20) * level
        d.rounded_rectangle(p(x + 10, top, x + w - 10, y + h - 10), radius=int(18 * S), fill=rgba(liquid, 0.85 * a))
    # emboss X
    d.line(p(x + 30, y + 30, x + w - 30, y + h - 30), fill=rgba(DARK, 0.6 * a), width=int(6 * S))
    d.line(p(x + w - 30, y + 30, x + 30, y + h - 30), fill=rgba(DARK, 0.6 * a), width=int(6 * S))

def bulb(d, cx, cy, sc, glow, a=1.0):
    if glow > 0.02:
        for g, al in ((2.6, 0.06), (2.0, 0.10), (1.5, 0.16)):
            r = 70 * sc * g
            d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=rgba(YEL, al * glow * a))
    col = tuple(int(DARK[i] + (YEL[i] - DARK[i]) * glow) for i in range(3))
    d.ellipse(p(cx - 70 * sc, cy - 70 * sc, cx + 70 * sc, cy + 70 * sc), fill=rgba(col, a))
    poly(d, [(cx - 38 * sc, cy + 50 * sc), (cx + 38 * sc, cy + 50 * sc), (cx + 30 * sc, cy + 100 * sc), (cx - 30 * sc, cy + 100 * sc)], rgba(col, a))
    for i in range(3):
        yy = cy + (106 + i * 18) * sc
        d.rounded_rectangle(p(cx - 32 * sc, yy, cx + 32 * sc, yy + 12 * sc), radius=int(5 * S), fill=rgba(MUTED, a))

def house(d, x, y, w, h, a=1.0, fillk=0.0, col=ACC):
    roof = [(x - 30, y), (x + w / 2, y - h * 0.55), (x + w + 30, y)]
    poly(d, roof, rgba(WHITE, a))
    d.rectangle(p(x, y, x + w, y + h), fill=rgba(PANEL, a), outline=rgba(WHITE, a), width=int(7 * S))

def ev_icon(d, x, y, sc, col, a=1.0):
    car_side(d, x, y, sc, col, a)

# ---------- 1. a gallon of gas = 33.7 kWh ----------
def vis_kwh_hook(d, lt, t):
    k = back_out(lt / 0.5)
    lvl = ease_inout((lt - 0.3) / 2.6)
    jerrycan(d, 110, 230, 260 * max(k, 0.01), 330, lvl, clamp(k))
    text_c(d, 240, 600, "1 ГАЛЛОН", FL("InterDisplay-Black.otf", 44), rgba(WHITE, clamp(k)))
    text_c(d, 240, 652, "БЕНЗИНА", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, clamp(k)))
    # equals + counter
    a2 = ease_out((lt - 0.6) / 0.4)
    text_c(d, 450, 330, "=", FL("InterDisplay-Black.otf", 100), rgba(MUTED, a2))
    val = 33.7 * lvl
    text_c(d, 670, 300, f"{val:.1f}".replace('.', ','), FL("InterDisplay-Black.otf", 120), rgba(ACC, a2))
    text_c(d, 670, 440, "кВт·ч", FL("InterDisplay-Black.otf", 64), rgba(WHITE, a2))
    # bolts stacking up as energy units
    nb = int(10 * lvl)
    for i in range(10):
        r_, c_ = divmod(i, 5)
        bx, by = 560 + c_ * 55, 560 + r_ * 80
        bolt(d, bx, by, 0.36, rgba(ACC if i < nb else DARK, 1.0 if i < nb else 0.6))
    a3 = ease_out((lt - 3.6) / 0.4)
    d.rounded_rectangle(p(200, 770, 700, 850), radius=40 * S, fill=rgba(PANEL, a3), outline=rgba(ACC, a3), width=4 * S)
    text_c(d, 450, 786, "ЧТО ТАКОЕ кВт·ч?", FL("InterDisplay-Black.otf", 42), rgba(ACC, a3))

# ---------- 2. definition: 1000 W x 1 h; 10 W bulb x 100 h ----------
def vis_kwh_def(d, lt, t):
    dur = sdur("kwh_def")
    cut = dur * 0.48
    fE = FL("InterDisplay-Black.otf", 70)
    if lt < cut:
        parts = [("1000 Вт", WHITE, 0.0), ("×", MUTED, 0.5), ("1 ЧАС", WHITE, 0.9)]
        xs = [210, 450, 680]
        for (s_, c, st), x in zip(parts, xs):
            kk = back_out((lt - st) / 0.4)
            if kk > 0.01:
                text_c(d, x, 170 - 30 * (1 - kk), s_, fE, rgba(c, clamp(kk)))
        # watt meter: bar of 1000 W, clock sweep of one hour
        a = ease_out((lt - 0.3) / 0.4)
        sweep = ease_inout((lt - 1.0) / 1.8)
        cx, cy, r = 450, 470, 140
        d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=rgba(PANEL, a), outline=rgba(WHITE, a), width=6 * S)
        if sweep > 0.01:
            d.pieslice(p(cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14), -90, -90 + 360 * sweep, fill=rgba(ACC, 0.8 * a))
        ang = math.radians(-90 + 360 * sweep)
        d.line(p(cx, cy, cx + math.cos(ang) * (r - 30), cy + math.sin(ang) * (r - 30)), fill=rgba(WHITE, a), width=8 * S)
        d.ellipse(p(cx - 12, cy - 12, cx + 12, cy + 12), fill=rgba(WHITE, a))
        text_c(d, cx, cy + r + 20, f"{int(60 * sweep)} МИН", FL("InterDisplay-Bold.otf", 34), rgba(MUTED, a))
        a3 = ease_out((lt - 2.6) / 0.35)
        glow_rect(d, 270, 740, 630, 830, 26, ACC, a3)
        text_c(d, 450, 752, "= 1 кВт·ч", FL("InterDisplay-Black.otf", 54), rgba(BG, a3))
    else:
        l2 = lt - cut
        k = ease_out(l2 / 0.4)
        hours = 100 * ease_inout((l2 - 0.3) / (dur - cut - 0.9))
        bulb(d, 450, 300, 1.25, 0.4 + 0.6 * k * (0.92 + 0.08 * math.sin(t * 9)), k)
        text_c(d, 450, 40, "LED 10 Вт", FL("InterDisplay-Black.otf", 52), rgba(YEL, k))
        # hour counter bar
        d.rounded_rectangle(p(140, 640, 760, 690), radius=25 * S, fill=rgba(DARK, k))
        if hours > 0.5:
            glow_rect(d, 140, 640, 140 + 620 * hours / 100, 690, 25, YEL, k)
        text_c(d, 450, 715, f"{int(hours)} Ч", FL("InterDisplay-Black.otf", 60), rgba(WHITE, k))
        text_c(d, 450, 800, "10 Вт × 100 ч = 1 кВт·ч", FL("InterDisplay-Bold.otf", 34), rgba(MUTED, ease_out((l2 - 1.6) / 0.4)))

# ---------- 3. average US home ~28 kWh/day ----------
def vis_kwh_home(d, lt, t):
    dur = sdur("kwh_home")
    k = back_out(lt / 0.45)
    hx, hy, hw, hh = 210, 250, 480, 360
    house(d, hx, hy, hw, hh, clamp(k))
    n = int(28 * ease_out((lt - 0.3) / max(1.0, dur - 1.0)))
    # 28 energy cells inside the house: 7 x 4
    for i in range(28):
        r_, c_ = divmod(i, 7)
        x = hx + 34 + c_ * 61; y = hy + 40 + r_ * 80
        on = i < n
        if on:
            glow_rect(d, x, y, x + 46, y + 60, 8, ACC, clamp(k))
            bolt(d, x + 23, y + 30, 0.26, rgba(BG, clamp(k)))
        else:
            d.rounded_rectangle(p(x, y, x + 46, y + 60), radius=8 * S, fill=rgba(DARK, 0.7 * clamp(k)))
    text_c(d, 450, 650, f"≈ {n} кВт·ч", FL("InterDisplay-Black.otf", 72), rgba(ACC, clamp(k)))
    text_c(d, 450, 760, "СРЕДНИЙ ДОМ В США ЗА ДЕНЬ", FL("InterDisplay-Bold.otf", 34), rgba(MUTED, clamp(k)))

# ---------- 4. efficient EV: ~4 mi per kWh, 33.7 kWh -> 130+ mi ----------
def vis_kwh_car(d, lt, t):
    dur = sdur("kwh_car")
    cut = dur * 0.36
    road_y = 430
    d.line(p(30, road_y + 92, 870, road_y + 92), fill=rgba(DARK, 1), width=6 * S)
    off = (t * 220) % 120
    for x in range(-120, 900, 120):
        d.line(p(x - off + 40, road_y + 130, x - off + 90, road_y + 130), fill=rgba(DARK, 1), width=6 * S)
    if lt < cut:
        units = 1.0; full = 1.0
        prog = ease_inout((lt - 0.3) / (cut - 0.5))
        miles = 4 * prog
        label = "1 кВт·ч"
        rem = 1 - prog
    else:
        l2 = lt - cut
        prog = ease_inout((l2 - 0.2) / (dur - cut - 1.0))
        miles = 4 * 33.7 * prog * (134.8 / 134.8)
        label = "33,7 кВт·ч"
        rem = 1 - prog
    car_side(d, 450, road_y, 0.9, WHITE)
    # battery gauge above car
    a = ease_out(lt / 0.4)
    bx0, bx1, by0, by1 = 260, 640, 180, 250
    d.rounded_rectangle(p(bx0, by0, bx1, by1), radius=16 * S, outline=rgba(WHITE, a), width=6 * S)
    d.rounded_rectangle(p(bx1 + 4, by0 + 20, bx1 + 18, by1 - 20), radius=4 * S, fill=rgba(WHITE, a))
    if rem > 0.01:
        d.rounded_rectangle(p(bx0 + 12, by0 + 12, bx0 + 12 + (bx1 - bx0 - 24) * rem, by1 - 12), radius=8 * S, fill=rgba(ACC, a))
    text_c(d, 450, 110, label, FL("InterDisplay-Black.otf", 54), rgba(ACC, a))
    # odometer
    text_c(d, 450, 600, f"{miles:.0f} МИЛЬ" if miles >= 10 else f"{miles:.1f} МИЛИ".replace('.', ','), FL("InterDisplay-Black.otf", 120), rgba(WHITE, a))
    if lt >= cut:
        a3 = ease_out((lt - cut - 1.0) / 0.4)
        text_c(d, 450, 760, "ЭНЕРГИЯ 1 ГАЛЛОНА", FL("InterDisplay-Bold.otf", 36), rgba(MUTED, a3))

# ---------- 5. bar comparison EV vs gas car on same energy ----------
def vis_kwh_gas(d, lt, t):
    a = ease_out(lt / 0.4)
    text_c(d, 450, 40, "МИЛЬ НА 33,7 кВт·ч", FL("InterDisplay-Black.otf", 48), rgba(WHITE, a))
    text_c(d, 450, 105, "(ЭНЕРГИЯ 1 ГАЛЛОНА БЕНЗИНА)", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
    base_x = 120; maxw = 660
    rows = [("ЭКОНОМИЧНЫЙ ЭЛЕКТРОМОБИЛЬ", 135, ACC, 0.0, "130+"), ("НОВАЯ БЕНЗИНОВАЯ МАШИНА", 27, ACC2, 1.0, "≈ 27")]
    for i, (lab, v, col, st, txt) in enumerate(rows):
        y = 260 + i * 260
        k = ease_out((lt - st) / 1.1)
        d.text((base_x * S, (y - 60) * S), lab, font=FL("InterDisplay-Bold.otf", 36), fill=rgba(WHITE, a))
        d.rounded_rectangle(p(base_x, y, base_x + maxw, y + 90), radius=20 * S, fill=rgba(DARK, 0.5 * a))
        w = max(20, maxw * v / 140 * k)
        if k > 0:
            glow_rect(d, base_x, y, base_x + w, y + 90, 20, col, clamp(k * 1.4))
            tx = base_x + w + 20
            f = FL("InterDisplay-Black.otf", 56)
            if tx + d.textlength(txt, font=f) / S > 860:
                text_c(d, base_x + w - 110, y + 10, txt, f, rgba(BG, clamp(k * 1.4)))
            else:
                d.text((tx * S, (y + 10) * S), txt, font=f, fill=rgba(col, clamp(k * 1.4)))
    a2 = ease_out((lt - 2.4) / 0.4)
    text_c(d, 450, 790, "ТА ЖЕ ЭНЕРГИЯ. В 5 РАЗ ДАЛЬШЕ.", FL("InterDisplay-Black.otf", 42), rgba(ACC, a2))

# ---------- 6. where the energy goes: engine vs EV ----------
def vis_kwh_why(d, lt, t):
    a = ease_out(lt / 0.4)
    x0, x1 = 110, 790
    def stack(y, wheel_frac, lab, st, wheel_col):
        k = ease_out((lt - st) / 1.2)
        d.text((x0 * S, (y - 62) * S), lab, font=FL("InterDisplay-Bold.otf", 36), fill=rgba(WHITE, a))
        d.rounded_rectangle(p(x0, y, x1, y + 100), radius=20 * S, fill=rgba(DARK, 0.5 * a))
        wx = x0 + (x1 - x0) * wheel_frac * k
        if k > 0.02:
            glow_rect(d, x0, y, wx, y + 100, 20, wheel_col, clamp(k * 1.3))
            # heat part
            hx1 = x0 + (x1 - x0) * k
            if hx1 - wx > 50:
                d.rounded_rectangle(p(wx + 4, y, hx1, y + 100), radius=20 * S, fill=rgba(RED, 0.75 * clamp(k * 1.3)))
            # rising heat squiggles over loss part
            for i in range(int((hx1 - wx) / 60)):
                ph = (t * 0.9 + i * 0.37) % 1.0
                sx = wx + 30 + i * 60
                sy = y - 10 - ph * 70
                d.arc(p(sx - 12, sy - 12, sx + 12, sy + 12), 180, 360, fill=rgba(ACC2, (1 - ph) * k), width=4 * S)
            f = FL("InterDisplay-Black.otf", 44)
            if wheel_frac * k > 0.15:
                text_c(d, (x0 + wx) / 2, y + 24, f"{int(round(wheel_frac * 100 * k))}%", f, rgba(BG, clamp(k * 1.3)))
        return k
    stack(200, 0.30, "БЕНЗИНОВЫЙ ДВИГАТЕЛЬ", 0.2, ACC2)
    stack(500, 0.89, "ЭЛЕКТРОМОТОР", 1.6, ACC)
    a2 = ease_out((lt - 0.8) / 0.4)
    # legend
    d.rounded_rectangle(p(150, 700, 190, 740), radius=8 * S, fill=rgba(ACC, a2))
    d.text((205 * S, 700 * S), "НА КОЛЁСА", font=FL("InterDisplay-Bold.otf", 30), fill=rgba(WHITE, a2))
    d.rounded_rectangle(p(520, 700, 560, 740), radius=8 * S, fill=rgba(RED, a2))
    d.text((575 * S, 700 * S), "ПОТЕРИ В ТЕПЛО", font=FL("InterDisplay-Bold.otf", 30), fill=rgba(WHITE, a2))
    text_c(d, 450, 790, "ТИПИЧНЫЕ АВТО (МИНЭНЕРГО США)", FL("Inter-SemiBold.otf", 26), rgba(MUTED, a2))

# ---------- 7. outro ----------
def vis_kwh_outro(d, lt, t):
    dur = sdur("kwh_outro")
    cut = dur * 0.5
    if lt < cut:
        k = back_out(lt / 0.5)
        jerrycan(d, 120, 260, 200, 260, 1.0, ease_out(lt / 0.4))
        text_c(d, 450, 330, "→", FL("InterDisplay-Black.otf", 110), rgba(MUTED, ease_out((lt - 0.3) / 0.4)))
        bolt(d, 680, 380, 1.6 * max(k, 0.01), rgba(ACC, clamp(k)))
        text_c(d, 450, 620, "ГАЛЛОНЫ ИЛИ кВт·ч?", FL("InterDisplay-Black.otf", 70), rgba(WHITE, ease_out((lt - 1.4) / 0.4)))
    else:
        end_card(d, lt, cut)

VIS.update({"kwh_hook": vis_kwh_hook, "kwh_def": vis_kwh_def, "kwh_home": vis_kwh_home, "kwh_car": vis_kwh_car,
            "kwh_gas": vis_kwh_gas, "kwh_why": vis_kwh_why, "kwh_outro": vis_kwh_outro})
