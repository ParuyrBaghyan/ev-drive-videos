# Visuals for "BYD vs Tesla" — runs inside tools/render_long2.py globals. Logical canvas 1500 x 720.
import random, os
ROOT_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(EP))), "assets", "cars")
CX = 750
BYDC = (70, 205, 255)      # BYD colour (cool blue)
TSLC = (255, 84, 84)       # Tesla colour (red)
GOOD = ACC; BAD = (255, 84, 84); GOLD = (255, 205, 70)

def sent_t(name, k):
    for sc in scenes:
        if sc["visual"] == name:
            k = min(k, len(sc["sentences"]) - 1)
            return sc["sentences"][k]["start"] - sc["vis_start"]
    return 0.0
def appear(lt, at, dur=0.45): return ease_out((lt - at) / dur)
def pop(lt, at, dur=0.5): return clamp(back_out((lt - at) / dur), 0, 1.15)
def label_pill(d, x, y, s, col, a=1.0, size=28, fg=None, name=BLACK):
    if a <= 0: return
    f = FL(name, size); tw = d.textlength(s, font=f) / S / CAM[0]
    rrect(d, x - tw / 2 - 20, y, x + tw / 2 + 20, y + size + 22, (size + 22) / 2, rgba(col, a))
    text_c(d, x, y + 9, s, size, rgba(fg or BG, a), name)
def big_text(d, x, y, s, size, col, a=1.0):
    if a <= 0: return
    text_c(d, x + 4, y + 6, s, size, rgba((0, 0, 0), 0.5 * a), BLACK)
    text_c(d, x, y, s, size, rgba(col, a), BLACK)
def count(lt, at, dur, v): return v * ease_inout((lt - at) / dur)
def source(d, s, a=1.0): text_r(d, 1460, 690, s, 17, rgba(MUTED, a))

# ---------- 3D car stills (transparent PNGs from test3d/render_real.py) ----------
_cars = {}
def car_img(d, name, x, y, w, a=1.0, flip=False):
    """paste a transparent car render, top-left at logical (x, y), logical width w (camera-aware)"""
    if a <= 0.01: return
    X, Y = p(x, y); Wpx = int(SZ(w))
    key = (name, Wpx, flip)
    if key not in _cars:
        if len(_cars) > 24: _cars.clear()
        im = Image.open(os.path.join(ROOT_ASSETS, name + ".png")).convert("RGBA")
        im = im.crop(im.getbbox())
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        _cars[key] = im.resize((Wpx, max(1, int(im.height * Wpx / im.width))), Image.LANCZOS)
    im = _cars[key]
    if a < 0.99:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    d._image.paste(im, (int(X), int(Y)), im)
def car_h(name, w):
    im = Image.open(os.path.join(ROOT_ASSETS, name + ".png")); bb = im.getbbox()
    return (bb[3] - bb[1]) * w / (bb[2] - bb[0])

# ---------- 3D frame sequences ----------
_seq = {}
def seq_frame(folder, i, n):
    i = max(0, min(n - 1, i))
    key = (folder, i)
    if key not in _seq:
        if len(_seq) > 6: _seq.clear()
        pth = f"{EP}/{folder}/f{i:04d}.png"
        _seq[key] = Image.open(pth).convert("RGB").resize((LW * S, LH * S), Image.BILINEAR) if os.path.exists(pth) else None
    return _seq[key]
_fm = []
def _feather():
    if not _fm:
        m = Image.new("L", (LW * S, LH * S), 0); f = 90 * S
        ImageDraw.Draw(m).rectangle((f, f, LW * S - f, LH * S - f), fill=255)
        _fm.append(m.filter(ImageFilter.GaussianBlur(f * 0.6)))
    return _fm[0]
def paste_seq(d, folder, lt, n, fps=15, rev=False):
    i = int(lt * fps); i = (n - 1 - i) if rev else i
    im = seq_frame(folder, i, n)
    if im is not None: d._image.paste(im, (0, 0), _feather())

def stat_card(d, x0, y0, x1, y1, title, val, col, a, sub=None, vsize=58):
    if a <= 0: return
    rrect(d, x0 + 6, y0 + 10, x1 + 6, y1 + 10, 24, rgba((0, 0, 0), 0.35 * a))
    rrect(d, x0, y0, x1, y1, 24, rgba(PANEL, 0.92 * a), rgba(col, a), 3)
    text_c(d, (x0 + x1) / 2, y0 + 16, title, 22, rgba(MUTED, a), BLACK)
    text_c(d, (x0 + x1) / 2, y0 + 48, val, vsize, rgba(col, a), BLACK)
    if sub: text_c(d, (x0 + x1) / 2, y1 - 40, sub, 20, rgba(WHITE, a))

def hbar(d, x, y, w, h, frac, col, a, label, val, lab_col=WHITE):
    rrect(d, x, y, x + w, y + h, h / 2, rgba(DARK, a))
    ww = w * clamp(frac)
    if ww > h: rrect(d, x, y, x + ww, y + h, h / 2, rgba(col, a))
    text_l(d, x, y - 40, label, 28, rgba(lab_col, a), BLACK)
    if ww > 1: text_l(d, x + ww + 18, y + h / 2 - 22, val, 40, rgba(WHITE, a), BLACK)

def phone(d, x, y, s, col, a=1.0):
    rrect(d, x - 45 * s, y - 85 * s, x + 45 * s, y + 85 * s, 14 * s, rgba(col, a))
    rrect(d, x - 38 * s, y - 70 * s, x + 38 * s, y + 62 * s, 6 * s, rgba(BG, a))
    circle(d, x, y + 73 * s, 6 * s, rgba(BG, a))

def cell(d, x, y, w, h, col, a=1.0, lvl=1.0):
    rrect(d, x, y, x + w, y + h, 6, rgba(PANEL, a), rgba(col, a), 3)
    rrect(d, x + w * 0.3, y - 8, x + w * 0.7, y, 3, rgba(col, a))
    if lvl > 0: rrect(d, x + 6, y + h - 6 - (h - 12) * lvl, x + w - 6, y + h - 6, 4, rgba(col, 0.75 * a))

def tag(d, x, y, price, sub, col, a, k=1.0):
    if a <= 0: return
    pts = [(x, y), (x + 300, y), (x + 360, y + 70), (x + 300, y + 140), (x, y + 140)]
    poly(d, [(px + 6, py + 10) for px, py in pts], rgba((0, 0, 0), 0.35 * a))
    poly(d, pts, rgba(col, a))
    circle(d, x + 320, y + 70, 12, rgba(BG, a))
    text_l(d, x + 26, y + 18, price, 54, rgba(BG, a), BLACK)
    text_l(d, x + 26, y + 88, sub, 22, rgba(BG, a), BLACK)

# ======================= INTRO =======================
def vis_hero(d, lt, t, dur):
    paste_seq(d, "hero_frames", lt, 165)
    a = appear(lt, 0.5)
    k1 = count(lt, 0.6, 2.2, 762478); k2 = count(lt, sent_t("hero", 1), 1.6, 486532)
    rrect(d, 40, 40, 520, 200, 24, rgba(PANEL, 0.88 * a), rgba(BYDC, a), 3)
    text_l(d, 66, 54, "COMPANY ???  ·  JUL–SEP 2026", 22, rgba(MUTED, a), BLACK)
    text_l(d, 66, 90, f"{int(k1):,}", 70, rgba(BYDC, a), BLACK)
    text_l(d, 68, 168, "fully electric cars", 20, rgba(WHITE, a))
    b = appear(lt, sent_t("hero", 1))
    if b > 0:
        rrect(d, 980, 40, 1460, 200, 24, rgba(PANEL, 0.88 * b), rgba(TSLC, b), 3)
        text_l(d, 1006, 54, "TESLA  ·  JUL–SEP 2026", 22, rgba(MUTED, b), BLACK)
        text_l(d, 1006, 90, f"{int(k2):,}", 70, rgba(TSLC, b), BLACK)
        text_l(d, 1008, 168, "deliveries", 20, rgba(WHITE, b))
    c = pop(lt, sent_t("hero", 2))
    if c > 0: label_pill(d, CX, 620, "THE WINNER WASN'T TESLA", GOLD, clamp(c), 34)

def vis_who(d, lt, t, dur):
    cam_path(lt, [(0, 1.08, 750, 360), (dur, 1.0, 750, 360)])
    a = pop(lt, 0.1)
    if a > 0:
        aa = clamp(a)
        big_text(d, CX, 120, "BYD", 230, BYDC, aa)
        text_c(d, CX, 370, "“BUILD YOUR DREAMS”  ·  SHENZHEN, CHINA", 28, rgba(WHITE, aa), BLACK)
    b = appear(lt, 1.6)
    if b > 0:
        phone(d, 470, 560, 0.75, WHITE, b)
        arrow(d, 560, 560, 760, 560, ACC, 8, b)
        car_img(d, "cn_side_teal", 800, 500, 300, b)
        text_c(d, 470, 650, "phone batteries", 20, rgba(MUTED, b))
        text_c(d, 950, 650, "electric cars", 20, rgba(MUTED, b))
    c = pop(lt, sent_t("who", 1))
    if c > 0: label_pill(d, 1240, 440, "NOT SOLD IN THE USA", BAD, clamp(c), 26, WHITE)

def vis_questions(d, lt, t, dur):
    qs = [("How did a battery maker win?", 0), ("Is Tesla really losing?", 1), ("Or playing a different game?", 2)]
    for i, (q, k) in enumerate(qs):
        at = sent_t("questions", 0) + 0.2 if i == 0 else sent_t("questions", k)
        c = pop(lt, at)
        if c <= 0: continue
        aa = clamp(c); y = 70 + i * 150
        rrect(d, 230, y, 1270, y + 120, 30, rgba(PANEL, aa), rgba(GOLD if i == 2 else WHITE, aa), 3)
        big_text(d, 300, y + 18, "?", 70, GOLD, aa)
        text_l(d, 360, y + 34, q, 44, rgba(WHITE, aa), BLACK)
    e = appear(lt, sent_t("questions", 4))
    if e > 0: label_pill(d, CX, 600, "WATCH FOR THE NUMBER IN THE MIDDLE", ACC, e, 28)

# ======================= 01 SCOREBOARD =======================
def vis_q3_bars(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, CX, 30, "BATTERY-ELECTRIC CARS SOLD · JULY–SEPTEMBER 2026", 32, rgba(WHITE, a), BLACK)
    k = ease_inout((lt - 0.4) / 1.6)
    hbar(d, 110, 190, 1080, 90, 762478 / 800000 * k, BYDC, a, "BYD", f"{int(762478 * k):,}", BYDC)
    hbar(d, 110, 380, 1080, 90, 486532 / 800000 * k, TSLC, a, "TESLA", f"{int(486532 * k):,}", TSLC)
    b = appear(lt, sent_t("q3_bars", 1) - 0.3)
    if b > 0:
        x0 = 110 + 1080 * 486532 / 800000; x1 = 110 + 1080 * 762478 / 800000
        line(d, [(x0, 500), (x0, 530), (x1, 530), (x1, 500)], rgba(GOLD, b), 5)
        label_pill(d, (x0 + x1) / 2, 550, "+275,946 FOR BYD", GOLD, b, 28)
    c = appear(lt, sent_t("q3_bars", 2))
    if c > 0: text_c(d, CX, 640, "plug-in hybrids NOT included", 24, rgba(MUTED, c), BLACK)
    source(d, "Sources: company sales and delivery reports, Q3 2026", a)

def vis_growth(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, CX, 30, "CHANGE FROM A YEAR EARLIER", 34, rgba(WHITE, a), BLACK)
    for i, (n, v, col, at) in enumerate([("BYD · electric sales", 30.9, GOOD, sent_t("growth", 1)), ("TESLA · deliveries", -2.1, BAD, sent_t("growth", 2))]):
        k = appear(lt, at)
        if k <= 0: continue
        x = 400 + i * 700
        text_c(d, x, 110, n, 30, rgba(WHITE, k), BLACK)
        kk = ease_inout((lt - at) / 1.2)
        if v > 0:
            arrow(d, x, 470, x, 470 - 260 * kk - 10, col, 34, k, 80)
            big_text(d, x, 500, f"+{v * kk:.0f}%", 90, col, k)
        else:
            arrow(d, x, 170, x, 170 + 150 * kk + 10, col, 34, k, 80)
            big_text(d, x, 380, f"{v * kk:.0f}%", 90, col, k)
    b = appear(lt, sent_t("growth", 2) + 2.6)
    if b > 0: label_pill(d, 1100, 520, "STILL BEAT WALL STREET'S GUESS (461,974)", WHITE, b, 20)
    source(d, "Sources: BYD and Tesla Q3 2026 reports; Tesla-compiled consensus", a)

def vis_annual(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, 380, 40, "FULL YEAR 2025 · BATTERY-ELECTRIC", 28, rgba(WHITE, a), BLACK)
    k = ease_inout((lt - sent_t("annual", 1)) / 1.5)
    base = 600; sc = 340 / 2.4
    for i, (n, v, col) in enumerate([("BYD", 2.254714, BYDC), ("TESLA", 1.636129, TSLC)]):
        x = 220 + i * 320; h = v * sc * 100 * k / 100
        rrect(d, x - 90, base - h, x + 90, base, 16, rgba(col, a))
        text_c(d, x, base + 14, n, 30, rgba(col, a), BLACK)
        if k > 0.2: text_c(d, x, base - h - 56, f"{v * k:.2f}M", 40, rgba(WHITE, a), BLACK)
    b = appear(lt, sent_t("annual", 2))
    if b > 0:
        rrect(d, 800, 90, 1440, 600, 28, rgba(PANEL, b), rgba(TSLC, b), 3)
        text_c(d, 1120, 110, "TESLA DELIVERIES PER YEAR", 24, rgba(MUTED, b), BLACK)
        vals = [("2023", 1.808581), ("2024", 1.789226), ("2025", 1.636129)]
        kk = ease_inout((lt - sent_t("annual", 2)) / 1.6)
        pts = [(900 + j * 220, 540 - (v - 1.55) * 900) for j, (_, v) in enumerate(vals)]
        glow_line(d, partial(pts, kk), TSLC, b, 7)
        for j, ((yr, v), (px, py)) in enumerate(zip(vals, pts)):
            if kk >= j / 2 - 0.01:
                circle(d, px, py, 12, rgba(WHITE, b))
                text_c(d, px, py - 52, f"{v:.2f}M", 26, rgba(WHITE, b), BLACK)
                text_c(d, px, 540, yr, 24, rgba(MUTED, b), BLACK)
    c = appear(lt, sent_t("annual", 2) + 2.6)
    if c > 0: label_pill(d, 1120, 620, "2 YEARS OF DECLINE", TSLC, c, 24, WHITE)
    source(d, "Sources: BYD and Tesla annual sales reports", a)

# ======================= 02 ORIGIN =======================
def vis_phone(d, lt, t, dur):
    cam_path(lt, [(0, 1.1, 650, 360), (dur, 1.0, 750, 360)])
    a = appear(lt, 0)
    big_text(d, 330, 110, "1995", 120, ACC, a)
    text_c(d, 330, 250, "SHENZHEN, CHINA", 28, rgba(WHITE, a), BLACK)
    b = appear(lt, sent_t("phone", 1))
    if b > 0:
        text_c(d, 330, 320, "Wang Chuanfu starts a battery company", 24, rgba(MUTED, b))
        for i in range(5):
            k = appear(lt, sent_t("phone", 1) + 0.15 * i)
            cell(d, 120 + i * 88, 400, 60, 140, BYDC, k, 0.4 + 0.15 * i)
    c = appear(lt, sent_t("phone", 2))
    if c > 0:
        for i in range(6):
            k = appear(lt, sent_t("phone", 2) + 0.12 * i)
            phone(d, 800 + (i % 3) * 200, 220 + (i // 3) * 230, 0.95, WHITE, k)
        label_pill(d, 1000, 590, "2003: WORLD'S #1 NICKEL-CADMIUM BATTERY MAKER", GOLD, c, 22)

def vis_buy_carmaker(d, lt, t, dur):
    a = appear(lt, 0)
    big_text(d, 330, 70, "2003", 110, ACC, a)
    b = appear(lt, sent_t("buy_carmaker", 1))
    if b > 0:
        rrect(d, 120, 240, 540, 560, 28, rgba(PANEL, b), rgba(BYDC, b), 3)
        poly(d, [(170, 470), (170, 380), (250, 340), (250, 380), (330, 340), (330, 380), (410, 340), (410, 470)], rgba(BYDC, b))
        rrect(d, 430, 300, 470, 470, 4, rgba(BYDC, b))
        text_c(d, 330, 490, "STATE-OWNED CAR MAKER · XI'AN", 22, rgba(WHITE, b), BLACK)
    c = appear(lt, sent_t("buy_carmaker", 2))
    if c > 0:
        rrect(d, 660, 120, 1420, 600, 28, rgba(PANEL, c), rgba(BAD, c), 3)
        text_c(d, 1040, 140, "BYD SHARE PRICE AFTER THE DEAL", 24, rgba(MUTED, c), BLACK)
        kk = ease_inout((lt - sent_t("buy_carmaker", 2)) / 1.4)
        pts = [(720, 260), (860, 250), (960, 270), (1010, 260), (1080, 420), (1180, 450), (1360, 470)]
        glow_line(d, partial(pts, kk), BAD, c, 7)
        if kk > 0.6: big_text(d, 1250, 280, "−21%", 80, BAD, appear(lt, sent_t("buy_carmaker", 2) + 0.9))
    e = appear(lt, sent_t("buy_carmaker", 3))
    if e > 0: label_pill(d, 1040, 640, "“A BATTERY COMPANY BUILDING CARS?”", WHITE, e, 24)

def vis_buffett(d, lt, t, dur):
    a = appear(lt, 0)
    big_text(d, 330, 70, "2008", 110, ACC, a)
    b = appear(lt, sent_t("buffett", 1))
    if b > 0:
        stat_card(d, 100, 240, 560, 420, "BERKSHIRE HATHAWAY BUYS", "$230M", GOLD, b, "≈10% of BYD")
    c = appear(lt, sent_t("buffett", 2))
    if c > 0:
        rrect(d, 660, 90, 1420, 600, 28, rgba(PANEL, c), rgba(GOOD, c), 3)
        text_c(d, 1040, 110, "BYD STOCK · SEP 2008 → MAR 2025", 24, rgba(MUTED, c), BLACK)
        kk = ease_inout((lt - sent_t("buffett", 2)) / 2.0)
        rnd = random.Random(5); pts = []
        for i in range(31):
            u = i / 30; v = (math.exp(u * 3.83) - 1) / (math.exp(3.83) - 1)
            pts.append((720 + u * 640, 540 - 360 * v + (rnd.uniform(-14, 14) if 0 < i < 30 else 0)))
        glow_line(d, partial(pts, kk), GOOD, c, 7)
        if kk > 0.7: big_text(d, 900, 180, "+4,500%", 76, GOOD, appear(lt, sent_t("buffett", 2) + 1.4))
        text_r(d, 1400, 560, "shape illustrative; start and end values from Berkshire filings", 15, rgba(MUTED, c))
    source(d, "Sources: Berkshire Hathaway filings via Reuters and Business Standard", a)

# ======================= 03 SECRET WEAPON =======================
PARTS = [("BATTERIES", 0), ("CHIPS", 1), ("MOTORS", 2), ("SOFTWARE", 3), ("SHIPS", 4)]
def vis_inhouse(d, lt, t, dur):
    a = appear(lt, 0)
    car_img(d, "side_xray", 420, 60, 660, a)
    b = appear(lt, sent_t("inhouse", 2))
    if b > 0:
        rrect(d, 110, 330, 720, 690, 26, rgba(PANEL, b), rgba(DARK, b), 3)
        text_c(d, 415, 345, "TYPICAL CAR MAKER", 26, rgba(MUTED, b), BLACK)
        for i, (n, _) in enumerate(PARTS[:4]):
            k = appear(lt, sent_t("inhouse", 2) + 0.2 * i)
            text_l(d, 160, 400 + i * 66, n, 30, rgba(WHITE, k), BLACK)
            text_r(d, 680, 400 + i * 66, "BUYS IT", 28, rgba(MUTED, k), BLACK)
    c = appear(lt, sent_t("inhouse", 3))
    if c > 0:
        rrect(d, 780, 330, 1390, 690, 26, rgba(PANEL, c), rgba(BYDC, c), 3)
        text_c(d, 1085, 345, "BYD", 26, rgba(BYDC, c), BLACK)
        for i, (n, _) in enumerate(PARTS[:4]):
            k = pop(lt, sent_t("inhouse", 3) + 0.2 * i)
            if k <= 0: continue
            text_l(d, 830, 400 + i * 66, n, 30, rgba(WHITE, clamp(k)), BLACK)
            text_r(d, 1350, 400 + i * 66, "MAKES IT ✓", 28, rgba(GOOD, clamp(k)), BLACK)

def vis_blade(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, 420, 40, "BLADE BATTERY", 40, rgba(BYDC, a), BLACK)
    n = 14
    for i in range(n):
        k = ease_out((lt - 0.3 - i * 0.08) / 0.5)
        if k <= 0: continue
        y = 130 + i * 30 - (1 - k) * 60
        rrect(d, 120, y, 720, y + 22, 6, rgba(mix(BYDC, WHITE, 0.15 * (i % 2)), k * a), rgba(BG, k * a), 2)
    b = appear(lt, 1.6)
    if b > 0: label_pill(d, 420, 580, "LFP · NO COBALT · NO NICKEL", GOOD, b, 26)
    c = appear(lt, sent_t("blade", 1))
    if c > 0:
        stat_card(d, 880, 90, 1400, 300, "CHIPS", "SINCE 2004", BYDC, c, "BYD Semiconductor", 52)
    e = appear(lt, sent_t("blade", 1) + 2.0)
    if e > 0:
        stat_card(d, 880, 360, 1400, 570, "MOTORS & DRIVE SYSTEMS", "IN-HOUSE", BYDC, e, "FinDreams Powertrain", 52)

def vis_ship(d, lt, t, dur):
    a = appear(lt, 0)
    bob = 6 * math.sin(t * 1.6)
    x = 1500 - 1350 * ease_out(lt / 3.2)
    sy = 450 + bob
    for k in range(4):
        wy = 520 + k * 40
        pts = [(xx, wy + 8 * math.sin(xx / 60 + t * 2 + k)) for xx in range(0, 1501, 30)]
        line(d, pts, rgba(mix((40, 90, 160), BG, k * 0.2), a), 6)
    hull = [(x, sy - 220), (x + 1020, sy - 220), (x + 1100, sy - 140), (x + 1060, sy + 40), (x + 40, sy + 40)]
    poly(d, [(px + 6, py + 10) for px, py in hull], rgba((0, 0, 0), 0.35 * a))
    poly(d, hull, rgba((235, 238, 242), a))
    rrect(d, x + 40, sy - 20, x + 1060, sy + 40, 8, rgba((30, 60, 120), a))
    for r in range(3):
        for c in range(16):
            rrect(d, x + 70 + c * 58, sy - 190 + r * 50, x + 100 + c * 58, sy - 175 + r * 50, 3, rgba(DARK, a))
    rrect(d, x + 40, sy - 290, x + 200, sy - 220, 10, rgba((235, 238, 242), a))
    text_l(d, x + 380, sy - 20, "BYD SHENZHEN", 40, rgba(WHITE, a), BLACK)
    b = appear(lt, sent_t("ship", 2))
    if b > 0:
        rrect(d, 1040, 40, 1450, 200, 24, rgba(PANEL, 0.92 * b), rgba(BYDC, b), 3)
        text_c(d, 1245, 56, "CARS PER TRIP", 22, rgba(MUTED, b), BLACK)
        big_text(d, 1245, 90, f"{int(count(lt, sent_t('ship', 2), 1.6, 9200)):,}", 76, BYDC, b)

def vis_price(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, CX, 30, "STARTING PRICE IN CHINA · END OF 2023", 32, rgba(WHITE, a), BLACK)
    b = appear(lt, sent_t("price", 1))
    car_img(d, "cn_side_teal", 110, 150, 520, b)
    tag(d, 160, 400, "≈ $10,000", "BYD SEAGULL", BYDC, b)
    c = appear(lt, sent_t("price", 2))
    car_img(d, "side_red", 860, 150, 520, c, flip=True)
    tag(d, 900, 400, "≈ $32,000", "TESLA MODEL 3", TSLC, c)
    e = appear(lt, sent_t("price", 2) + 1.5)
    if e > 0: label_pill(d, CX, 600, "OVER 3× CHEAPER", GOLD, e, 30)
    text_c(d, CX, 660, "cars shown are generic 3D models, not the real vehicles", 17, rgba(MUTED, a))
    source(d, "Source: CNN/KTVZ, prices 73,800 vs 229,900 yuan", a)

# ======================= 04 TESLA'S BET =======================
def vis_two_models(d, lt, t, dur):
    a = appear(lt, 0)
    b = appear(lt, sent_t("two_models", 1) - 0.2)
    if b > 0:
        text_c(d, 360, 40, "BYD", 40, rgba(BYDC, b), BLACK)
        rnd = random.Random(2)
        for i in range(30):
            k = appear(lt, sent_t("two_models", 1) + i * 0.04)
            x = 110 + (i % 6) * 100; y = 140 + (i // 6) * 92
            col = mix(BYDC, WHITE, rnd.uniform(0, 0.5))
            sc_ = rnd.uniform(0.32, 0.42)
            poly(d, [(x + px * sc_, y + py * sc_) for px, py in [(-120, 30), (-122, 0), (-100, -18), (-60, -26), (-30, -58), (40, -60), (80, -30), (118, -16), (124, 30)]], rgba(col, k))
        text_c(d, 360, 640, "a huge range of models", 24, rgba(MUTED, b))
    c = appear(lt, sent_t("two_models", 2))
    if c > 0:
        text_c(d, 1100, 40, "TESLA", 40, rgba(TSLC, c), BLACK)
        kk = ease_inout((lt - sent_t("two_models", 2)) / 1.6)
        cx, cy, r = 1100, 360, 190
        arc(d, cx, cy, r, 0, 360, rgba(DARK, c), 46)
        arc(d, cx, cy, r, -90, -90 + 360 * 0.983 * kk, rgba(TSLC, c), 46)
        big_text(d, cx, cy - 60, f"{98.3 * kk:.0f}%", 90, WHITE, c)
        text_c(d, cx, cy + 50, "MODEL 3 + MODEL Y", 24, rgba(WHITE, c), BLACK)
        text_c(d, cx, 600, "of Q3 2026 deliveries", 24, rgba(MUTED, c))

def vis_robotaxi(d, lt, t, dur):
    paste_seq(d, "rt_frames", lt, 180)
    a = appear(lt, sent_t("robotaxi", 2))
    if a > 0:
        rrect(d, 40, 40, 560, 210, 24, rgba(PANEL, 0.88 * a), rgba(ACC, a), 3)
        text_l(d, 66, 54, "TESLA ROBOTAXI · TO END OF SEP 2026", 20, rgba(MUTED, a), BLACK)
        text_l(d, 66, 88, f"≈{int(count(lt, sent_t('robotaxi', 2), 2.0, 2000000)):,}", 64, rgba(ACC, a), BLACK)
        text_l(d, 68, 166, "miles of what Tesla calls unsupervised driving", 18, rgba(WHITE, a))
    b = pop(lt, sent_t("robotaxi", 3))
    if b > 0: label_pill(d, 1180, 620, "CYBERCAB: NO WHEEL · NO PEDALS", WHITE, clamp(b), 26)

def vis_valuation(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, CX, 30, "WHAT INVESTORS PAY · JUNE 2026", 32, rgba(WHITE, a), BLACK)
    k = ease_out((lt - sent_t("valuation", 1)) / 1.4)
    R = 250; r = R * math.sqrt(120 / 1500)
    circle(d, 520, 380, R * k, rgba(TSLC, 0.9 * a))
    if k > 0.3:
        big_text(d, 520, 330, "$1.5T", 90, WHITE, a)
        text_c(d, 520, 440, "TESLA", 30, rgba(WHITE, a), BLACK)
    b = appear(lt, sent_t("valuation", 2))
    if b > 0:
        circle(d, 1100, 560, r * ease_out((lt - sent_t("valuation", 2)) / 0.8), rgba(BYDC, b))
        text_c(d, 1100, 420, "BYD  $120B", 36, rgba(BYDC, b), BLACK)
    c = pop(lt, sent_t("valuation", 3))
    if c > 0: label_pill(d, 1100, 160, "FEWER CARS · OVER 10× THE VALUE", GOLD, clamp(c), 28)
    source(d, "Source: market values reported by 24/7 Wall St., June 11, 2026", a)

# ======================= 05 PLOT TWIST =======================
def vis_profit(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, CX, 30, "NET PROFIT · JULY–SEPTEMBER 2026", 34, rgba(WHITE, a), BLACK)
    base = 600; sc_ = 380 / 1.5
    for i, (n, v, col, at, lab) in enumerate([("TESLA", 0.787, TSLC, sent_t("profit", 1), "$787M"), ("BYD", 1.41, BYDC, sent_t("profit", 2), "≈ $1.4B")]):
        k = appear(lt, at)
        if k <= 0: continue
        kk = ease_inout((lt - at) / 1.3)
        x = 500 + i * 500; h = v * sc_ * kk
        rrect(d, x - 120, base - h, x + 120, base, 18, rgba(col, k))
        text_c(d, x, base + 16, n, 34, rgba(col, k), BLACK)
        if kk > 0.3: text_c(d, x, base - h - 70, lab, 52, rgba(WHITE, k), BLACK)
    b = appear(lt, sent_t("profit", 2))
    if b > 0: text_c(d, 1000, 140, "10.02 billion yuan", 24, rgba(MUTED, b))
    source(d, "Sources: Tesla and BYD Q3 2026 results (via Electrek); USD conversion approximate", a)

def gauge(d, x, y, r, frac, col, a, lab, val):
    arc(d, x, y, r, 180, 360, rgba(DARK, a), 40)
    arc(d, x, y, r, 180, 180 + 180 * frac, rgba(col, a), 40)
    big_text(d, x, y - 90, val, 80, WHITE, a)
    text_c(d, x, y + 30, lab, 28, rgba(col, a), BLACK)

def vis_margins(d, lt, t, dur):
    a = appear(lt, 0)
    b = pop(lt, 0.1)
    if b > 0: label_pill(d, CX, 40, "THE CHEAPER CAR MAKER EARNED MORE", GOLD, clamp(b), 30)
    for i, (n, v, col, at, sub) in enumerate([("TESLA · car business", 18.1, TSLC, sent_t("margins", 2), "automotive, excl. credits"), ("BYD · whole company", 18.0, BYDC, sent_t("margins", 3), "Electrek calculation")]):
        k = appear(lt, at)
        if k <= 0: continue
        kk = ease_inout((lt - at) / 1.2)
        x = 430 + i * 640
        gauge(d, x, 470, 210, v / 40 * kk, col, k, n, f"{v * kk:.1f}%")
        text_c(d, x, 560, sub, 20, rgba(MUTED, k))
    text_c(d, CX, 640, "gross margin = share of revenue left after the cost of making the cars", 20, rgba(MUTED, appear(lt, sent_t("margins", 2))))

def vis_exports(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, CX, 30, "JULY–SEPTEMBER 2026", 32, rgba(WHITE, a), BLACK)
    k = ease_inout((lt - sent_t("exports", 1)) / 1.6)
    hbar(d, 110, 200, 1080, 100, 550704 / 600000 * k, BYDC, a, "BYD · CARS SHIPPED ABROAD", f"{int(550704 * k):,}", BYDC)
    b = appear(lt, sent_t("exports", 2) - 0.2)
    if b > 0:
        kk = ease_inout((lt - sent_t("exports", 2) + 0.2) / 1.4)
        hbar(d, 110, 430, 1080, 100, 486532 / 600000 * kk, TSLC, b, "TESLA · DELIVERIES WORLDWIDE", f"{int(486532 * kk):,}", TSLC)
    source(d, "Sources: BYD and Tesla Q3 2026 reports", a)

# ======================= 06 BYD'S PROBLEM =======================
def vis_china_down(d, lt, t, dur):
    a = appear(lt, 0)
    text_c(d, CX, 30, "BYD SALES IN CHINA · CHANGE FROM A YEAR EARLIER", 30, rgba(WHITE, a), BLACK)
    months = ["MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR", "APR", "MAY"]
    t0 = sent_t("china_down", 3)
    for i, m in enumerate(months):
        k = pop(lt, t0 + i * 0.12)
        if k <= 0: continue
        x = 115 + i * 100
        rrect(d, x - 42, 160, x + 42, 300, 14, rgba(PANEL, clamp(k)), rgba(BAD, clamp(k)), 3)
        text_c(d, x, 172, m, 20, rgba(MUTED, clamp(k)), BLACK)
        arrow(d, x, 215, x, 285, BAD, 12, clamp(k), 30)
    if appear(lt, t0) > 0:
        text_c(d, 415, 320, "2025", 22, rgba(MUTED, appear(lt, t0)), BLACK)
        text_c(d, 1115, 320, "2026", 22, rgba(MUTED, appear(lt, t0 + 1.0)), BLACK)
    b = appear(lt, t0 + 1.8)
    if b > 0: label_pill(d, CX, 380, "13 MONTHS IN A ROW OF DECLINES IN CHINA", BAD, b, 28, WHITE)
    c = pop(lt, sent_t("china_down", 4))
    if c > 0:
        rrect(d, 360, 470, 1140, 640, 28, rgba(PANEL, clamp(c)), rgba(GOLD, clamp(c)), 3)
        text_c(d, CX, 490, "EARLY 2026 · CHINA'S BEST-SELLING CAR MAKER", 22, rgba(MUTED, clamp(c)), BLACK)
        big_text(d, CX, 530, "GEELY  >  BYD", 70, GOLD, clamp(c))
    source(d, "Sources: Automotive World (May 2026), CarsGuide/Reuters (Mar 2026)", a)

def vis_price_war(d, lt, t, dur):
    a = appear(lt, 0)
    for i in range(5):
        k = appear(lt, 0.2 + i * 0.2)
        x = 140 + i * 150; y = 140 + (i % 2) * 40
        drop = 160 * ease_inout((lt - 0.8 - i * 0.2) / 1.0)
        rrect(d, x, y + drop, x + 120, y + 70 + drop, 10, rgba(GOLD, k))
        text_c(d, x + 60, y + 16 + drop, "SALE ↓", 28, rgba(BG, k), BLACK)
    text_c(d, 440, 470, "PRICE CUTS", 30, rgba(WHITE, a), BLACK)
    b = pop(lt, sent_t("price_war", 1) + 3.5)
    if b > 0: stat_card(d, 860, 70, 1420, 280, "CHINA · FEBRUARY 2026", "BANNED", BAD, clamp(b), "selling cars below their cost", 64)
    c = pop(lt, sent_t("price_war", 2))
    if c > 0: stat_card(d, 860, 340, 1420, 550, "BYD PROFIT · Q1 2026", "−55%", BAD, clamp(c), "from a year earlier", 72)
    source(d, "Sources: SAMR rules via Automotive World; BYD Q1 2026 results", a)

def vis_abroad(d, lt, t, dur):
    a = appear(lt, 0)
    ox, oy = 1120, 300
    circle(d, ox, oy, 26, rgba(BYDC, a)); text_c(d, ox, oy + 40, "CHINA", 22, rgba(WHITE, a), BLACK)
    dests = [("EUROPE", 760, 170), ("LATIN AMERICA", 420, 520), ("MIDDLE EAST", 860, 330), ("SOUTHEAST ASIA", 1180, 520), ("AUSTRALIA", 1330, 640)]
    for i, (n, x, y) in enumerate(dests):
        k = appear(lt, 0.3 + i * 0.25)
        if k <= 0: continue
        mx, my = (ox + x) / 2, min(oy, y) - 120
        pts = [((1 - u) ** 2 * ox + 2 * (1 - u) * u * mx + u * u * x, (1 - u) ** 2 * oy + 2 * (1 - u) * u * my + u * u * y) for u in [j / 20 for j in range(21)]]
        line(d, partial(pts, ease_inout((lt - 0.3 - i * 0.25) / 0.9)), rgba(BYDC, 0.5 * k), 4)
        flow(d, pts, t + i, BYDC, k, 3, 6, 0.4, False)
        circle(d, x, y, 12, rgba(WHITE, k)); text_c(d, x, y + 18, n, 18, rgba(WHITE, k), BLACK)
    b = pop(lt, sent_t("abroad", 1))
    if b > 0: stat_card(d, 60, 60, 460, 240, "EXPORTS · Q3 2026", "+137%", GOOD, clamp(b), "from a year earlier", 66)
    c = pop(lt, sent_t("abroad", 1) + 3.0)
    if c > 0: stat_card(d, 60, 280, 460, 460, "SHARE OF BYD SALES", "≈42%", GOOD, clamp(c), "now sold abroad", 66)
    source(d, "Map schematic. Source: BYD Q3 2026 (via Electrek)", a)

# ======================= 07 USA =======================
def vis_tariff(d, lt, t, dur):
    a = appear(lt, 0)
    b = appear(lt, 0.4)
    base = 600
    if b > 0:
        rrect(d, 300, base - 200, 520, base, 16, rgba(BYDC, b)); text_c(d, 410, base + 16, "COST OF THE CAR", 22, rgba(WHITE, b), BLACK)
    c = appear(lt, sent_t("tariff", 1))
    if c > 0:
        kk = ease_inout((lt - sent_t("tariff", 1)) / 1.2)
        rrect(d, 700, base - 200, 920, base, 16, rgba(BYDC, c))
        rrect(d, 700, base - 200 - 200 * kk, 920, base - 200, 16, rgba(BAD, c))
        text_c(d, 810, base + 16, "+ 100% TARIFF", 22, rgba(BAD, c), BLACK)
        if kk > 0.5: big_text(d, 1180, 260, "×2", 140, BAD, appear(lt, sent_t("tariff", 1) + 0.8))
    text_c(d, CX, 30, "BRINGING A CHINESE EV INTO THE US", 32, rgba(WHITE, a), BLACK)
    source(d, "Source: US Section 301 tariffs, raised to 100% in 2024", a)

def vis_software(d, lt, t, dur):
    a = appear(lt, 0)
    rrect(d, 560, 70, 940, 330, 24, rgba(PANEL, a), rgba(WHITE, a), 3)
    for i in range(6):
        line(d, [(600 + i * 60, 50), (600 + i * 60, 70)], rgba(WHITE, a), 6)
        line(d, [(600 + i * 60, 330), (600 + i * 60, 350)], rgba(WHITE, a), 6)
    text_c(d, CX, 160, "CONNECTED-CAR", 30, rgba(WHITE, a), BLACK)
    text_c(d, CX, 200, "SOFTWARE & HARDWARE", 24, rgba(MUTED, a), BLACK)
    b = pop(lt, sent_t("software", 1) + 0.5)
    if b > 0: label_pill(d, CX, 380, "MY2027: CHINESE SOFTWARE BANNED · HARDWARE LATER", BAD, clamp(b), 24, WHITE)
    c = appear(lt, sent_t("software", 1))
    if c > 0: stat_card(d, 90, 480, 700, 660, "SUPPORTERS SAY", "DATA & SECURITY", GOOD, c, None, 42)
    e = appear(lt, sent_t("software", 2))
    if e > 0: stat_card(d, 800, 480, 1410, 660, "CRITICS SAY", "FEWER CHEAP CARS", GOLD, e, None, 42)
    source(d, "Source: US Commerce Dept. connected-vehicle rule (Jan 2025)", a)

def vis_no_entry(d, lt, t, dur):
    cam_path(lt, [(0, 1.0, 750, 360), (dur, 1.06, 750, 370)])
    a = appear(lt, 0)
    car_img(d, "cn_front34_white", 120, 170, 800, a)
    b = pop(lt, 0.5)
    if b > 0:
        aa = clamp(b)
        circle(d, 1200, 260, 120, rgba(BAD, aa)); rrect(d, 1120, 240, 1280, 280, 8, rgba(WHITE, aa))
        text_c(d, 1200, 400, "NOT FOR SALE IN THE US", 26, rgba(WHITE, aa), BLACK)
    c = appear(lt, sent_t("no_entry", 1))
    if c > 0: label_pill(d, CX, 630, "THE WORLD'S BIGGEST EV MAKER", BYDC, c, 30)

# ======================= 08 VERDICT =======================
ROWS = [("CARS SOLD", "BYD", 2), ("PROFIT LAST QUARTER", "BYD", 3), ("COMPANY VALUE", "TESLA", 4), ("DRIVERLESS TAXIS", "TESLA", 5), ("PRICE", "BYD", 6)]
def vis_scorecard(d, lt, t, dur):
    a = appear(lt, 0)
    text_l(d, 160, 40, "CATEGORY", 26, rgba(MUTED, a), BLACK)
    text_c(d, 960, 40, "BYD", 30, rgba(BYDC, a), BLACK); text_c(d, 1250, 40, "TESLA", 30, rgba(TSLC, a), BLACK)
    for i, (n, w, k) in enumerate(ROWS):
        at = sent_t("scorecard", k)
        r = appear(lt, at - 0.1)
        if r <= 0: continue
        y = 110 + i * 112
        rrect(d, 120, y, 1400, y + 92, 20, rgba(PANEL, r), rgba(DARK, r), 2)
        text_l(d, 160, y + 26, n, 34, rgba(WHITE, r), BLACK)
        c = pop(lt, at + 0.3)
        if c > 0:
            x = 960 if w == "BYD" else 1250
            circle(d, x, y + 46, 34 * clamp(c), rgba(BYDC if w == "BYD" else TSLC, clamp(c)))
            text_c(d, x, y + 26, "✓", 32, rgba(BG, clamp(c)), BLACK)

def vis_two_games(d, lt, t, dur):
    a = appear(lt, 0)
    line(d, [(CX, 60), (CX, 660)], rgba(DARK, a), 4)
    b = appear(lt, sent_t("two_games", 1))
    if b > 0:
        car_img(d, "cn_side_teal", 70, 120, 610, b)
        text_c(d, 375, 400, "BYD", 44, rgba(BYDC, b), BLACK)
        text_c(d, 375, 470, "MAKE ALMOST EVERYTHING", 26, rgba(WHITE, b), BLACK)
        text_c(d, 375, 510, "SELL EVERYWHERE · CHEAPLY", 26, rgba(WHITE, b), BLACK)
    c = appear(lt, sent_t("two_games", 2))
    if c > 0:
        car_img(d, "side34_red", 830, 100, 600, c)
        text_c(d, 1125, 400, "TESLA", 44, rgba(TSLC, c), BLACK)
        text_c(d, 1125, 470, "AI · ROBOTAXIS · ROBOTS", 26, rgba(WHITE, c), BLACK)
        text_c(d, 1125, 510, "“that happens to sell cars”", 24, rgba(MUTED, c))

def vis_question(d, lt, t, dur):
    paste_seq(d, "hero_frames", lt, 165, fps=15, rev=True)
    a = pop(lt, 0.2)
    if a > 0:
        rrect(d, 260, 60, 1240, 250, 30, rgba(PANEL, 0.9 * clamp(a)), rgba(GOLD, clamp(a)), 3)
        big_text(d, CX, 80, "IS TESLA LOSING?", 68, TSLC, clamp(a))
        text_c(d, CX, 180, "or playing a different game?", 36, rgba(WHITE, clamp(a)), BLACK)
    b = appear(lt, sent_t("question", 1))
    if b > 0: label_pill(d, CX, 600, "PICK A SIDE IN THE COMMENTS", ACC, b, 30)
    c = appear(lt, sent_t("question", 2))
    if c > 0: label_pill(d, CX, 660, "SUBSCRIBE · EV DRIVE", WHITE, c, 22)

VIS.update({k[4:]: v for k, v in list(globals().items()) if k.startswith("vis_") and callable(v)})
