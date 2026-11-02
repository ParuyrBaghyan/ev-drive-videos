# Episode visuals: do EVs wear tires faster? (myth vs fact)
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
RUBBER = (34, 40, 50)
HOLE = (8, 10, 14)
RED = (255, 80, 80)
BLK = "InterDisplay-Black.otf"
BLD = "InterDisplay-Bold.otf"
SEMI = "Inter-SemiBold.otf"

def sdur(name):
    for s in scenes:
        if s["visual"] == name:
            return s["vis_end"] - s["start"]
    return 4.0

def poly(d, pts, col):
    d.polygon(p(*[v for xy in pts for v in xy]), fill=col)

def circ(d, x, y, r, col):
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=col)

def label(d, x, y, s, col, a, size=28, f=SEMI):
    if a <= 0: return
    text_c(d, x, y, s, FL(f, max(1, int(size))), rgba(col, a))

def chip(d, x, y, s, col, a, size=30, tcol=None):
    if a <= 0: return
    f = FL(BLK, max(1, int(size)))
    tw = d.textlength(s, font=f) / S
    w = tw + 50
    d.rounded_rectangle(p(x - w / 2, y, x + w / 2, y + size * 1.7), radius=size * 0.85 * S, fill=rgba(col, a))
    text_c(d, x, y + size * 0.3, s, f, rgba(tcol or BG, a))

def line(d, pts, col, w):
    d.line(p(*[v for xy in pts for v in xy]), fill=col, width=max(1, int(w * S)), joint="curve")

def arrow(d, x0, y0, x1, y1, col, w=10, head=24):
    line(d, [(x0, y0), (x1, y1)], col, w)
    ang = math.atan2(y1 - y0, x1 - x0)
    a1, a2 = ang + 2.6, ang - 2.6
    poly(d, [(x1 + math.cos(ang) * 6, y1 + math.sin(ang) * 6), (x1 + math.cos(a1) * head, y1 + math.sin(a1) * head),
             (x1 + math.cos(a2) * head, y1 + math.sin(a2) * head)], col)

def bolt(d, x, y, sc, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in pts], col)

def big_tire(d, cx, cy, r, ang, wear, a, glow=False):
    """Side view tire with tread blocks; wear 0..1 shrinks the tread blocks."""
    if glow:
        for k in range(4):
            circ(d, cx, cy, r + 26 - k * 6, rgba(ACC, 0.05 * a))
    circ(d, cx, cy, r + 4, rgba((0, 0, 0), 0.4 * a))
    circ(d, cx, cy, r, rgba(RUBBER, a))
    depth = 0.11 * (1 - wear)
    n = 22
    for k in range(n):
        a0 = ang + k * 2 * math.pi / n
        a1 = a0 + 2 * math.pi / n * 0.55
        ro, ri = r * (1.0 + depth * 0.0), r * (1 - depth)
        pts = [(cx + math.cos(a0) * ri, cy + math.sin(a0) * ri), (cx + math.cos(a0) * (r + depth * r * 0.9), cy + math.sin(a0) * (r + depth * r * 0.9)),
               (cx + math.cos(a1) * (r + depth * r * 0.9), cy + math.sin(a1) * (r + depth * r * 0.9)), (cx + math.cos(a1) * ri, cy + math.sin(a1) * ri)]
        poly(d, pts, rgba((58, 66, 80), a))
    circ(d, cx, cy, r * 0.78, rgba((24, 29, 37), a))
    circ(d, cx, cy, r * 0.62, rgba(STEEL, a))
    for k in range(5):
        aa = ang + k * 2 * math.pi / 5
        line(d, [(cx, cy), (cx + math.cos(aa) * r * 0.58, cy + math.sin(aa) * r * 0.58)], rgba((200, 206, 214), a), r * 0.09)
    circ(d, cx, cy, r * 0.14, rgba(ACC, a))

# 1 ---- hook: worn tire, MYTH? -> FACT
def vis_tw_hook(d, lt, t):
    dur = sdur("tw_hook")
    a = ease_out(lt / 0.4)
    k = ease_out(lt / 0.9)
    cx = -200 + 520 * k
    wear = ease_inout((lt - 0.5) / (dur * 0.6))
    big_tire(d, cx, 380, 230, lt * 4.0, wear, a)
    # rubber crumbs flung behind
    for i in range(14):
        ph = (lt * 1.3 + i / 14) % 1.0
        x = cx - 200 - ph * 260 + (i % 3) * 20
        y = 600 - ph * 140 + math.sin(i * 2.3) * 40
        circ(d, x, y, 7 - ph * 4, rgba(MUTED, a * (1 - ph) * min(1, lt)))
    # tread depth gauge on the right
    gx = 780
    d.rounded_rectangle(p(gx - 34, 190, gx + 34, 590), radius=16 * S, fill=rgba(PANEL, a))
    h = 360 * (1 - 0.7 * wear)
    col = tuple(int(ACC[i] + (ACC2[i] - ACC[i]) * wear) for i in range(3))
    d.rounded_rectangle(p(gx - 22, 580 - h, gx + 22, 580), radius=10 * S, fill=rgba(col, a))
    label(d, gx, 610, "ПРОТЕКТОР", MUTED, a, size=24, f=BLK)
    # verdict
    sw = dur * 0.55
    if lt < sw:
        chip(d, 450, 700, "МИФ?", WHITE, ease_out((lt - 0.4) / 0.3), size=56)
    else:
        kk = back_out((lt - sw) / 0.4)
        chip(d, 450, 700, "В ОСНОВНОМ ФАКТ", ACC, clamp(kk), size=int(56 * max(0.3, kk)))

# 2 ---- J.D. Power survey: counter + expectation vs reality
def vis_tw_study(d, lt, t):
    dur = sdur("tw_study")
    a = ease_out(lt / 0.4)
    n = int(31414 * ease_out(lt / 1.8))
    text_c(d, 450, 70, f"{n:,}".replace(",", " "), FL(BLK, 140), rgba(ACC, a))
    label(d, 450, 245, "ВЛАДЕЛЬЦЕВ НОВЫХ АВТО ОПРОШЕНО", WHITE, a, size=34, f=BLK)
    label(d, 450, 295, "J.D. POWER · ИССЛЕДОВАНИЕ ЗАВОДСКИХ ШИН, 2024", MUTED, a, size=22, f=SEMI)
    # people grid
    for i in range(30):
        r, c = divmod(i, 10)
        pa = ease_out((lt - 0.3 - i * 0.03) / 0.3)
        x = 135 + c * 70; y = 365 + r * 62
        col = ACC if r == 2 else STEEL
        circ(d, x, y, 10, rgba(col, pa))
        d.rounded_rectangle(p(x - 15, y + 13, x + 15, y + 40), radius=10 * S, fill=rgba(col, pa))
    # expected vs felt tread life
    b0 = dur * 0.45
    ka = ease_out((lt - b0) / 0.7)
    kb = ease_out((lt - b0 - 0.5) / 0.7)
    d.text(p(90, 580), "ЧЕГО ЖДАЛИ ВЛАДЕЛЬЦЫ ЭЛЕКТРОМОБИЛЕЙ", font=FL(BLK, 26), fill=rgba(MUTED, ka))
    d.rounded_rectangle(p(90, 620, 90 + 720 * ka, 666), radius=23 * S, fill=rgba(WHITE, ka * 0.85))
    d.text(p(90, 700), "ЧТО ПОЛУЧИЛИ", font=FL(BLK, 26), fill=rgba(ACC2, kb))
    d.rounded_rectangle(p(90, 740, 90 + 480 * kb, 786), radius=23 * S, fill=rgba(ACC2, kb))
    if kb > 0.6:
        fa = ease_out((lt - b0 - 1.2) / 0.4)
        label(d, 700, 745, "ИЗНОС БЫСТРЕЕ", ACC2, fa, size=28, f=BLK)
        label(d, 450, 830, "иллюстрация, не в масштабе", MUTED, fa * 0.8, size=20, f=SEMI)

# 3 ---- weight: battery slab presses on tires; fuel tank empties, battery doesn't
def vis_tw_weight(d, lt, t):
    dur = sdur("tw_weight")
    a = ease_out(lt / 0.4)
    gy = 470
    d.line(p(40, gy + 2, 860, gy + 2), fill=rgba(DARK, a), width=5 * S)
    # simple EV side silhouette
    cx = 450
    body = [(cx - 330, gy - 60), (cx - 320, gy - 120), (cx - 180, gy - 140), (cx - 90, gy - 230), (cx + 120, gy - 232), (cx + 230, gy - 140), (cx + 330, gy - 120), (cx + 340, gy - 60)]
    poly(d, [(x, y) for x, y in body] + [(cx + 340, gy - 60), (cx - 330, gy - 60)], rgba(STEEL, a))
    poly(d, [(cx - 70, gy - 210), (cx + 10, gy - 212), (cx + 10, gy - 150), (cx - 140, gy - 150)], rgba(HOLE, a))
    poly(d, [(cx + 30, gy - 212), (cx + 110, gy - 212), (cx + 190, gy - 150), (cx + 30, gy - 150)], rgba(HOLE, a))
    # battery slab in floor
    pk = ease_out((lt - 0.4) / 0.6)
    bx0, bx1 = cx - 170, cx + 170
    d.rounded_rectangle(p(bx0, gy - 98, bx0 + (bx1 - bx0) * pk, gy - 62), radius=8 * S, fill=rgba(ACC, a * pk))
    for i in range(8):
        xx = bx0 + 8 + i * 42
        if xx + 30 < bx0 + (bx1 - bx0) * pk:
            d.rectangle(p(xx, gy - 92, xx + 30, gy - 68), fill=rgba((150, 200, 40), a))
    # tires squash slightly under the load
    sq = ease_out((lt - 1.0) / 0.6)
    for wx in (cx - 220, cx + 220):
        r = 62
        d.ellipse(p(wx - r - 6 * sq, gy - 2 * r + 6 * sq, wx + r + 6 * sq, gy), fill=rgba(RUBBER, a))
        circ(d, wx, gy - r + 3 * sq, r * 0.58, rgba((200, 206, 214), a))
        circ(d, wx, gy - r + 3 * sq, r * 0.2, rgba(STEEL, a))
        # contact patch
        d.rounded_rectangle(p(wx - 30 - 22 * sq, gy - 4, wx + 30 + 22 * sq, gy + 6), radius=4 * S, fill=rgba(ACC2, a * sq))
    # weight counter + down arrows
    w = int(450 * ease_out((lt - 0.4) / 1.2))
    text_c(d, 450, 40, f"≈ {w} КГ", FL(BLK, 96), rgba(ACC, pk))
    label(d, 450, 165, "ТИПИЧНАЯ БАТАРЕЯ", WHITE, pk, size=30, f=BLK)
    if lt > 1.0:
        bob = math.sin(t * 5) * 6
        for wx in (cx - 220, cx + 220):
            arrow(d, wx, 225 + bob, wx, 290 + bob, rgba(ACC2, sq), w=10)
    # gas tank vs battery over time
    k2 = ease_out((lt - dur * 0.5) / 0.5)
    if k2 > 0:
        drain = clamp((lt - dur * 0.5 - 0.4) / (dur * 0.4))
        # fuel tank
        tx, ty = 230, 600
        d.rounded_rectangle(p(tx - 120, ty, tx + 120, ty + 120), radius=18 * S, outline=rgba(MUTED, k2), width=5 * S)
        lvl = 108 * (1 - 0.85 * drain)
        d.rounded_rectangle(p(tx - 112, ty + 112 - lvl, tx + 112, ty + 112), radius=12 * S, fill=rgba(ACC2, k2 * 0.85))
        label(d, tx, ty + 135, "БЕНЗОБАК", MUTED, k2, size=24, f=BLK)
        label(d, tx, ty + 168, "ЛЕГЧАЕТ", ACC2, k2, size=26, f=BLK)
        # battery
        bx = 670
        d.rounded_rectangle(p(bx - 120, ty, bx + 120, ty + 120), radius=18 * S, outline=rgba(MUTED, k2), width=5 * S)
        d.rounded_rectangle(p(bx - 112, ty + 8, bx + 112, ty + 112), radius=12 * S, fill=rgba(ACC, k2 * 0.85))
        bolt(d, bx, ty + 60, 0.5, rgba(BG, k2))
        label(d, bx, ty + 135, "БАТАРЕЯ", MUTED, k2, size=24, f=BLK)
        label(d, bx, ty + 168, "ВЕС ТОТ ЖЕ", ACC, k2, size=26, f=BLK)

# 4 ---- torque: flat electric torque from 0 rpm, rubber scrubbed off
def vis_tw_torque(d, lt, t):
    dur = sdur("tw_torque")
    a = ease_out(lt / 0.4)
    x0, y0, x1, y1 = 120, 470, 800, 110
    line(d, [(x0, y0), (x1, y0)], rgba(MUTED, a), 5)
    line(d, [(x0, y0), (x0, y1)], rgba(MUTED, a), 5)
    label(d, 460, y0 + 18, "ОБОРОТЫ МОТОРА →", MUTED, a, size=24, f=BLK)
    d.text(p(x0 + 12, y1 - 10), "КРУТЯЩИЙ МОМЕНТ", font=FL(BLK, 24), fill=rgba(MUTED, a))
    k = ease_out((lt - 0.3) / 1.4)
    # electric: flat from zero, then tapers
    pts = []
    for i in range(41):
        u = i / 40
        if u > k: break
        yv = 0.82 if u < 0.45 else 0.82 * (0.45 / u) ** 0.6
        pts.append((x0 + u * (x1 - x0), y0 - yv * (y0 - y1)))
    if len(pts) > 1:
        line(d, pts, rgba(ACC, a), 12)
        circ(d, pts[-1][0], pts[-1][1], 12, rgba(ACC, a))
    # gas: builds up with rpm
    pts2 = []
    for i in range(41):
        u = i / 40
        if u > k: break
        uu = 0.12 + u * 0.88
        yv = 0.45 * math.sin(math.pi * min(1, (uu - 0.12) / 0.95) * 0.85) + 0.05
        pts2.append((x0 + uu * (x1 - x0), y0 - yv * (y0 - y1)))
    if len(pts2) > 1:
        line(d, pts2, rgba(ACC2, a * 0.9), 8)
    la = ease_out((lt - 1.2) / 0.4)
    chip(d, 300, 215, "ЭЛЕКТРО: МАКСИМУМ С НУЛЯ", ACC, la, size=24)
    label(d, 600, 360, "БЕНЗИН", ACC2, la, size=28, f=BLK)
    # spinning tire scrubbing rubber
    k3 = ease_out((lt - dur * 0.45) / 0.4)
    if k3 > 0:
        tx, ty = 450, 690
        d.line(p(150, ty + 112, 750, ty + 112), fill=rgba(DARK, k3), width=5 * S)
        big_tire(d, tx, ty, 108, lt * 9, 0.3, k3, glow=True)
        for i in range(16):
            ph = (lt * 2.2 + i / 16) % 1.0
            x = tx - 110 - ph * 260
            y = ty + 105 - ph * (60 + (i % 4) * 25)
            circ(d, x, y, 8 - ph * 5, rgba(ACC2 if i % 3 == 0 else MUTED, k3 * (1 - ph)))
        arrow(d, tx + 150, ty + 20, tx + 290, ty + 20, rgba(ACC, k3), w=10)
        label(d, tx + 220, ty + 45, "СТАРТ", ACC, k3, size=24, f=BLK)

# 5 ---- HL rating: same size & pressure, more load
def vis_tw_hl(d, lt, t):
    dur = sdur("tw_hl")
    a = ease_out(lt / 0.4)
    # sidewall arc with the code
    cx, cy, r = 450, 760, 640
    arc(d, cx, cy, r, 200, 340, rgba(RUBBER, a), 110)
    arc(d, cx, cy, r - 60, 200, 340, rgba((50, 58, 72), a), 6)
    k = back_out((lt - 0.2) / 0.5)
    hk = clamp(k)
    d.rounded_rectangle(p(250, 105, 360, 175), radius=14 * S, fill=rgba(ACC, hk))
    text_c(d, 305, 112, "HL", FL(BLK, int(52 * max(0.3, k))), rgba(BG, hk))
    d.text(p(380, 112), "255/45 R20", font=FL(BLK, 52), fill=rgba(WHITE, a))
    label(d, 450, 205, "ПРЕФИКС «HL» = ВЫСОКАЯ НАГРУЗКА", MUTED, ease_out((lt - 0.6) / 0.4), size=24, f=BLK)
    # bars: SL 100, XL ~114, HL 125 (HL = +25% vs SL, +10% vs XL)
    rows = [("СТАНДАРТНАЯ (SL)", 1.00, STEEL, "БАЗА"), ("УСИЛЕННАЯ (XL)", 1.136, WHITE, ""), ("ВЫСОКАЯ НАГРУЗКА (HL)", 1.25, ACC, "+25%")]
    for i, (nm, v, col, tag) in enumerate(rows):
        kb = ease_out((lt - 1.0 - i * 0.45) / 0.7)
        y = 290 + i * 125
        d.text(p(90, y), nm, font=FL(BLK, 26), fill=rgba(MUTED if i < 2 else ACC, kb))
        wv = 560 * v * kb
        d.rounded_rectangle(p(90, y + 40, 90 + wv, y + 92), radius=26 * S, fill=rgba(col, kb * (0.9 if i < 2 else 1)))
        if kb > 0.5:
            d.text(p(90 + wv + 14, y + 48), tag, font=FL(BLK, 28), fill=rgba(col if i else MUTED, kb))
    sk = ease_out((lt - dur * 0.6) / 0.4)
    chip(d, 450, 700, "ТОТ ЖЕ РАЗМЕР · ТО ЖЕ ДАВЛЕНИЕ", ACC2, sk, size=30)
    label(d, 450, 775, "грузоподъёмность: Continental HL против SL/XL", MUTED, sk * 0.85, size=20, f=SEMI)

# 6 ---- outro: rotation pattern, range vs tread balance, follow
def vis_tw_outro(d, lt, t):
    dur = sdur("tw_outro")
    p1, p2 = dur * 0.32, dur * 0.68
    if lt < p1:
        a = ease_out(lt / 0.35)
        # top view car with 4 tires, rotation arrows
        d.rounded_rectangle(p(330, 120, 570, 720), radius=90 * S, fill=rgba(STEEL, a))
        d.rounded_rectangle(p(365, 260, 535, 560), radius=40 * S, fill=rgba(HOLE, a))
        for (x, y) in [(300, 220), (600, 220), (300, 620), (600, 620)]:
            d.rounded_rectangle(p(x - 32, y - 70, x + 32, y + 70), radius=16 * S, fill=rgba(RUBBER, a))
            d.rounded_rectangle(p(x - 24, y - 60, x + 24, y + 60), radius=12 * S, outline=rgba((70, 78, 92), a), width=3 * S)
        k = ease_out((lt - 0.4) / 0.8)
        arrow(d, 220, 270, 220, 270 + 300 * k, rgba(ACC, k), w=10)
        arrow(d, 680, 270, 680, 270 + 300 * k, rgba(ACC, k), w=10)
        label(d, 450, 760, "МЕНЯЙТЕ ШИНЫ МЕСТАМИ", ACC, ease_out((lt - 0.7) / 0.4), size=40, f=BLK)
    elif lt < p2:
        lt2 = lt - p1
        a = ease_out(lt2 / 0.35)
        tilt = math.sin(t * 2.2) * 0.12
        cx, cy = 450, 380
        poly(d, [(cx - 40, 640), (cx + 40, 640), (cx, 400)], rgba(STEEL, a))
        dx, dy = math.cos(tilt) * 300, math.sin(tilt) * 300
        line(d, [(cx - dx, cy - dy), (cx + dx, cy + dy)], rgba(WHITE, a), 12)
        circ(d, cx, cy, 16, rgba(ACC, a))
        for sgn, nm, col in ((-1, "ЗАПАС ХОДА", ACC), (1, "РЕСУРС ШИН", ACC2)):
            px, py = cx + sgn * dx, cy + sgn * dy
            line(d, [(px, py), (px, py + 90)], rgba(MUTED, a), 4)
            d.rounded_rectangle(p(px - 110, py + 90, px + 110, py + 170), radius=20 * S, fill=rgba(col, a))
            text_c(d, px, py + 114, nm, FL(BLK, 26), rgba(BG, a))
        label(d, 450, 700, "ЧТО ВЫ ВЫБЕРЕТЕ?", WHITE, ease_out((lt2 - 0.5) / 0.4), size=32, f=BLK)
    else:
        k = back_out((lt - p2) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - p2 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "ПОДПИСЫВАЙСЯ", FL(BLK, 44), rgba(BG, a))

VIS.update({"tw_hook": vis_tw_hook, "tw_study": vis_tw_study, "tw_weight": vis_tw_weight, "tw_torque": vis_tw_torque,
            "tw_hl": vis_tw_hl, "tw_outro": vis_tw_outro})
