# Episode visuals: what's inside a dead EV battery (the numbers)
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
BLK = "InterDisplay-Black.otf"
BLD = "InterDisplay-Bold.otf"
SEMI = "Inter-SemiBold.otf"
NI = (120, 200, 255)     # nickel blue
CU = (232, 140, 90)      # copper
CO = (150, 120, 255)     # cobalt violet
LI = ACC                 # lithium lime

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

def label_l(d, x, y, s, col, a, size=28, f=SEMI):
    if a <= 0: return
    d.text((x * S, y * S), s, font=FL(f, max(1, int(size))), fill=rgba(col, a))

def label_r(d, x, y, s, col, a, size=28, f=SEMI):
    if a <= 0: return
    fo = FL(f, max(1, int(size)))
    d.text((x * S - d.textlength(s, font=fo), y * S), s, font=fo, fill=rgba(col, a))

def chip(d, x, y, s, col, a, size=30, tcol=None):
    if a <= 0: return
    f = FL(BLK, max(1, int(size)))
    tw = d.textlength(s, font=f) / S
    w = tw + 50
    d.rounded_rectangle(p(x - w / 2, y, x + w / 2, y + size * 1.7), radius=size * 0.85 * S, fill=rgba(col, a))
    text_c(d, x, y + size * 0.3, s, f, rgba(tcol or BG, a))

def line(d, pts, col, w):
    d.line(p(*[v for xy in pts for v in xy]), fill=col, width=max(1, int(w * S)), joint="curve")

def arrow_head(d, x, y, ang, col, head=26):
    a1, a2 = ang + 2.6, ang - 2.6
    poly(d, [(x + math.cos(ang) * 8, y + math.sin(ang) * 8), (x + math.cos(a1) * head, y + math.sin(a1) * head),
             (x + math.cos(a2) * head, y + math.sin(a2) * head)], col)

def bolt(d, x, y, sc, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in pts], col)

def pack(d, x, y, w, h, a, cell_col=STEEL, lit=1.0, rot_dead=False):
    """Battery pack seen from above: casing + grid of cells."""
    d.rounded_rectangle(p(x - w / 2 + 8, y - h / 2 + 12, x + w / 2 + 8, y + h / 2 + 12), radius=22 * S, fill=rgba((0, 0, 0), 0.45 * a))
    d.rounded_rectangle(p(x - w / 2, y - h / 2, x + w / 2, y + h / 2), radius=22 * S, fill=rgba(PANEL, a),
                        outline=rgba(DARK, a), width=4 * S)
    cols, rows = 8, 4
    if w < 120 or h < 95: return
    cw, ch = (w - 60) / cols, (h - 50) / rows
    for r in range(rows):
        for c in range(cols):
            cx0 = x - w / 2 + 30 + c * cw; cy0 = y - h / 2 + 25 + r * ch
            k = (r * cols + c) / (rows * cols)
            col = cell_col if k < lit else DARK
            d.rounded_rectangle(p(cx0 + 4, cy0 + 4, cx0 + cw - 4, cy0 + ch - 4), radius=8 * S, fill=rgba(col, a))

def recycle_ring(d, cx, cy, r, ang, col, a, w=22):
    for k in range(3):
        a0 = math.degrees(ang) + k * 120 + 12
        a1 = a0 + 92
        arc(d, cx, cy, r, a0, a1, rgba(col, a), w)
        ea = math.radians(a1)
        arrow_head(d, cx + math.cos(ea) * r, cy + math.sin(ea) * r, ea + math.pi / 2, rgba(col, a), head=w * 1.5)

# 1 ---- hook: dead pack drops toward a bin -> TRASH? -> recycle ring
def vis_rc_hook(d, lt, t):
    dur = sdur("rc_hook")
    a = ease_out(lt / 0.35)
    sw = dur * 0.74
    # bin
    bx, by = 450, 560
    ba = a * (1 - ease_out((lt - sw) / 0.4))
    if ba > 0:
        poly(d, [(bx - 150, by), (bx + 150, by), (bx + 120, by + 250), (bx - 120, by + 250)], rgba(DARK, ba))
        d.rounded_rectangle(p(bx - 175, by - 30, bx + 175, by), radius=10 * S, fill=rgba(STEEL, ba))
        for k in (-70, 0, 70):
            line(d, [(bx + k, by + 40), (bx + k * 0.85, by + 220)], rgba(PANEL, ba), 14)
    # pack falling & tilting
    fall = ease_inout(lt / (sw * 0.9))
    py = 170 + 220 * fall
    lit = 1 - fall
    if lt < sw:
        pack(d, 450, py, 380, 190, a, cell_col=ACC2 if lit < 0.4 else STEEL, lit=max(lit, 0.15))
        label(d, 450, py - 20, f"{int(100 * max(lit, 0.0))}%", WHITE, a, size=52, f=BLK)
        chip(d, 450, 820, "МУСОР?", WHITE, ease_out((lt - 0.5) / 0.3), size=40)
    else:
        k = back_out((lt - sw) / 0.5)
        recycle_ring(d, 450, 420, 230 * max(k, 0.05), lt * 1.4, ACC, clamp(k), w=26)
        pack(d, 450, 420, 230 * max(k, 0.6), 115 * max(k, 0.6), clamp(k), cell_col=ACC2, lit=1)
        chip(d, 450, 760, "ИЛИ РУДНИК?", ACC, clamp(k), size=40)

# 2 ---- what's inside a 500 kg pack: bars + counters
def vis_rc_inside(d, lt, t):
    dur = sdur("rc_inside")
    a = ease_out(lt / 0.35)
    w = int(500 * ease_out(lt / 1.0))
    text_c(d, 450, 20, f"{w} КГ", FL(BLK, 120), rgba(WHITE, a))
    label(d, 450, 170, "ОДНА БОЛЬШАЯ БАТАРЕЯ ЭЛЕКТРОМОБИЛЯ", MUTED, a, size=30, f=BLK)
    items = [("НИКЕЛЬ", "Ni", 50, NI), ("МЕДЬ", "Cu", 30, CU), ("КОБАЛЬТ", "Co", 10, CO), ("ЛИТИЙ", "Li", 10, LI)]
    for i, (name, sym, kg, col) in enumerate(items):
        st = 1.0 + i * (dur - 2.6) / 4
        k = ease_out((lt - st) / 0.9)
        ia = ease_out((lt - st) / 0.3)
        y = 260 + i * 140
        # element tile
        d.rounded_rectangle(p(60, y, 170, y + 110), radius=16 * S, fill=rgba(col, ia))
        text_c(d, 115, y + 18, sym, FL(BLK, 60), rgba(BG, ia))
        label_l(d, 200, y + 2, name, WHITE, ia, size=32, f=BLK)
        # bar
        bw = 470 * kg / 50
        d.rounded_rectangle(p(200, y + 52, 670, y + 96), radius=22 * S, fill=rgba(PANEL, ia))
        if k > 0.01:
            d.rounded_rectangle(p(200, y + 52, 200 + max(44, bw * k), y + 96), radius=22 * S, fill=rgba(col, ia))
        label_r(d, 860, y + 44, f"~{int(round(kg * k))} кг", col, ia, size=42, f=BLK)
    label(d, 450, 830, "ДОЛИ ПО ПРИМЕРУ БАТАРЕИ VW GROUP", MUTED, ease_out((lt - 2) / 0.5), size=22)

# 3 ---- process: cells -> shredder -> powder -> chemistry -> pure metals
def vis_rc_process(d, lt, t):
    dur = sdur("rc_process")
    a = ease_out(lt / 0.35)
    # conveyor at top
    line(d, [(40, 190), (360, 190)], rgba(DARK, a), 10)
    for i in range(5):
        x = 40 + ((lt * 110 + i * 80) % 330)
        if x < 340:
            d.rounded_rectangle(p(x - 22, 120, x + 22, 186), radius=8 * S, fill=rgba(STEEL, a))
            d.rectangle(p(x - 8, 112, x + 8, 122), fill=rgba(MUTED, a))
    # shredder rollers
    for cx, sgn in ((380, 1), (480, -1)):
        circ(d, cx, 260, 58, rgba(DARK, a))
        for k in range(10):
            an = sgn * lt * 5 + k * math.pi / 5
            poly(d, [(cx + math.cos(an - 0.15) * 50, 260 + math.sin(an - 0.15) * 50),
                     (cx + math.cos(an) * 74, 260 + math.sin(an) * 74),
                     (cx + math.cos(an + 0.15) * 50, 260 + math.sin(an + 0.15) * 50)], rgba(MUTED, a))
        circ(d, cx, 260, 16, rgba(ACC2, a))
    label(d, 430, 50, "ИЗМЕЛЬЧЕНИЕ", ACC2, a, size=34, f=BLK)
    # falling powder
    for i in range(26):
        ph = (lt * 1.2 + i / 26) % 1.0
        x = 430 + math.sin(i * 1.7) * 30
        y = 330 + ph * 190
        circ(d, x, y, 5, rgba((90, 96, 108), a * (1 - ph * 0.3)))
    # beaker with bubbling liquid
    ka = ease_out((lt - 1.0) / 0.5)
    bx, by = 430, 540
    poly(d, [(bx - 120, by), (bx + 120, by), (bx + 100, by + 220), (bx - 100, by + 220)], rgba(PANEL, ka))
    lvl = 80 + 40 * ease_out((lt - 1.0) / 2.0)
    poly(d, [(bx - 120 + 20 * (1 - lvl / 220) + 0, by + 220 - lvl), (bx + 120 - 20 * (1 - lvl / 220), by + 220 - lvl),
             (bx + 100, by + 220), (bx - 100, by + 220)], rgba(NI, 0.55 * ka))
    line(d, [(bx - 120, by), (bx - 100, by + 220), (bx + 100, by + 220), (bx + 120, by)], rgba(WHITE, ka), 6)
    for i in range(8):
        ph = (lt * 0.9 + i / 8) % 1.0
        circ(d, bx - 70 + i * 20, by + 210 - ph * lvl, 6 + 4 * ph, rgba(WHITE, ka * 0.6 * (1 - ph)))
    label(d, 430, by + 240, "РАСТВОРЕНИЕ + ОЧИСТКА", NI, ka, size=30, f=BLK)
    # output ingots on the right
    line(d, [(bx + 125, by + 120), (640, by + 120)], rgba(DARK, ka), 8)
    arrow_head(d, 650, by + 120, 0, rgba(DARK, ka), head=22)
    cols = [NI, CU, CO, LI]; syms = ["Ni", "Cu", "Co", "Li"]
    for i in range(4):
        ia = back_out((lt - 2.2 - i * 0.45) / 0.4)
        if ia <= 0: continue
        ia = clamp(ia)
        x = 720 + (i % 2) * 110 - 55; y = 360 + (i // 2) * 130 + 140
        poly(d, [(x - 48, y + 40), (x + 48, y + 40), (x + 34, y - 20), (x - 34, y - 20)], rgba(cols[i], ia))
        text_c(d, x, y - 14, syms[i], FL(BLK, 34), rgba(BG, ia))
    label(d, 775, 360, "ЧИСТЫЕ", ACC, ease_out((lt - 2.2) / 0.4), size=34, f=BLK)
    label(d, 775, 400, "МЕТАЛЛЫ", ACC, ease_out((lt - 2.2) / 0.4), size=34, f=BLK)

# 4 ---- recovery: donut to 95%+
def vis_rc_recovery(d, lt, t):
    dur = sdur("rc_recovery")
    a = ease_out(lt / 0.35)
    k = ease_inout(lt / 2.2)
    cx, cy, r = 450, 360, 250
    arc(d, cx, cy, r, 0, 360, rgba(PANEL, a), 52)
    arc(d, cx, cy, r, -90, -90 + 342 * k, rgba(ACC, a), 52)
    # glow tip
    ea = math.radians(-90 + 342 * k)
    circ(d, cx + math.cos(ea) * r, cy + math.sin(ea) * r, 34, rgba(ACC, 0.25 * a))
    pct = int(round(95 * k))
    text_c(d, cx, cy - 100, f"{pct}%" + ("+" if k > 0.99 else ""), FL(BLK, 130), rgba(WHITE, a))
    label(d, cx, cy + 60, "ВОЗВРАЩЕНО", MUTED, a, size=34, f=BLK)
    cols = [NI, CU, CO, LI]; syms = ["Li", "Ni", "Co", "Cu"]; cmap = {"Li": LI, "Ni": NI, "Co": CO, "Cu": CU}
    for i, sname in enumerate(syms):
        ia = back_out((lt - 1.4 - i * 0.3) / 0.4)
        if ia <= 0: continue
        x = 180 + i * 180; y = 690
        sz = 64 * clamp(ia, 0.2, 1.2)
        d.rounded_rectangle(p(x - sz, y - sz * 0.9, x + sz, y + sz * 0.9), radius=14 * S, fill=rgba(cmap[sname], clamp(ia)))
        text_c(d, x, y - 36, sname, FL(BLK, max(1, int(56 * clamp(ia, 0.2, 1)))), rgba(BG, clamp(ia)))
    label(d, 450, 820, "ПО ДАННЫМ REDWOOD MATERIALS", MUTED, ease_out((lt - 2.5) / 0.4), size=24)

# 5 ---- recycled vs mined: three paired bars
def vis_rc_mining(d, lt, t):
    dur = sdur("rc_mining")
    a = ease_out(lt / 0.35)
    label_l(d, 70, 20, "ДОБЫЧА", ACC2, a, size=34, f=BLK)
    label_l(d, 260, 20, "vs", MUTED, a, size=34, f=BLK)
    label_l(d, 320, 20, "ПЕРЕРАБОТКА", ACC, a, size=34, f=BLK)
    label(d, 450, 70, "СТЭНФОРД · NATURE COMMUNICATIONS 2025", MUTED, a, size=20)
    rows = [("ПАРНИКОВЫЕ ГАЗЫ", "-58–81%", 0.42, 0.19), ("ВОДА", "-72–88%", 0.28, 0.12), ("ЭНЕРГИЯ", "-77–89%", 0.23, 0.11)]
    for i, (name, txt, hi, lo) in enumerate(rows):
        st = 0.6 + i * (dur - 2.5) / 3
        k = ease_out((lt - st) / 0.9)
        ia = ease_out((lt - st) / 0.3)
        y = 150 + i * 230
        label_l(d, 70, y, name, WHITE, ia, size=32, f=BLK)
        label_r(d, 830, y - 4, txt, ACC, ease_out((lt - st - 0.8) / 0.4), size=40, f=BLK)
        full = 760
        d.rounded_rectangle(p(70, y + 55, 70 + max(40, full * k), y + 100), radius=22 * S, fill=rgba(ACC2, ia))
        # recycled: range band hi..lo, settle
        rk = ease_out((lt - st - 0.5) / 1.0)
        wv = full * (1 - (1 - hi) * rk)
        d.rounded_rectangle(p(70, y + 115, 70 + max(40, wv * min(1, k * 2)), y + 160), radius=22 * S, fill=rgba(ACC, ia * 0.35))
        wl = full * (1 - (1 - lo) * rk)
        d.rounded_rectangle(p(70, y + 115, 70 + max(40, wl * min(1, k * 2)), y + 160), radius=22 * S, fill=rgba(ACC, ia))

# 6 ---- closed loop with travelling metal dot + cycle counter
def vis_rc_loop(d, lt, t):
    a = ease_out(lt / 0.35)
    cx, cy, r = 450, 400, 250
    arc(d, cx, cy, r, 0, 360, rgba(DARK, a), 14)
    speed = 3.2
    ph = lt * speed
    an = -math.pi / 2 + ph
    for k in range(8):
        aa = an - k * 0.06
        circ(d, cx + math.cos(aa) * r, cy + math.sin(aa) * r, 18 - k * 2, rgba(ACC, a * (1 - k / 8)))
    nodes = [("ЯЧЕЙКИ", -90, STEEL), ("EV", 0, WHITE), ("ПЕРЕРАБ.", 90, ACC2), ("МЕТАЛЛЫ", 180, NI)]
    for name, deg, col in nodes:
        an = math.radians(deg)
        x, y = cx + math.cos(an) * r, cy + math.sin(an) * r
        circ(d, x, y, 66, rgba(PANEL, a))
        arc(d, x, y, 66, 0, 360, rgba(col, a), 6)
        label(d, x, y - 16, name, col, a, size=(30 if len(name) <= 4 else 22 if len(name) <= 6 else 19), f=BLK)
    for deg in (-45, 45, 135, 225):
        an = math.radians(deg)
        arrow_head(d, cx + math.cos(an) * r, cy + math.sin(an) * r, an + math.pi / 2, rgba(MUTED, a), head=26)
    cyc = 1 + int(ph / (2 * math.pi))
    text_c(d, cx, cy - 80, f"×{cyc}", FL(BLK, 120), rgba(ACC, a))
    label(d, cx, cy + 60, "ТОТ ЖЕ МЕТАЛЛ", MUTED, a, size=30, f=BLK)

# 7 ---- outro: pile of old packs grows into a mountain -> logo
def vis_rc_outro(d, lt, t):
    dur = sdur("rc_outro")
    sw = dur * 0.5
    if lt < sw:
        a = ease_out(lt / 0.35)
        line(d, [(60, 680), (840, 680)], rgba(DARK, a), 6)
        rows = [7, 6, 5, 4, 3, 2, 1]
        n = 0
        for ri, cnt in enumerate(rows):
            for c in range(cnt):
                k = ease_out((lt - 0.12 * n * 0.5) / 0.35); n += 1
                if k <= 0: continue
                w, h = 100, 52
                x = 450 - (cnt - 1) * w / 2 + c * w
                y = 680 - h / 2 - ri * h - 2 - 260 * (1 - k)
                col = [STEEL, ACC2, DARK, MUTED][(ri + c) % 4]
                d.rounded_rectangle(p(x - w / 2 + 4, y - h / 2 + 3, x + w / 2 - 4, y + h / 2 - 3), radius=8 * S, fill=rgba(col, k))
                d.rectangle(p(x + w / 2 - 4, y - 8, x + w / 2 + 4, y + 8), fill=rgba(MUTED, k))
        chip(d, 450, 120, "НОВЫЙ ЛИТИЕВЫЙ РУДНИК?", ACC, ease_out((lt - 1.2) / 0.4), size=40)
    else:
        k = back_out((lt - sw) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - sw - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "ПОДПИСЫВАЙТЕСЬ!", FL(BLK, 36), rgba(BG, a))

VIS.update({"rc_hook": vis_rc_hook, "rc_inside": vis_rc_inside, "rc_process": vis_rc_process,
            "rc_recovery": vis_rc_recovery, "rc_mining": vis_rc_mining, "rc_loop": vis_rc_loop, "rc_outro": vis_rc_outro})
