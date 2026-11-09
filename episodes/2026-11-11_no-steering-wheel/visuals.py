# Episode visuals: Tesla Cybercab (no steering wheel/pedals) and the NHTSA self-certification audit (news, controversy).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
CHROME = (176, 186, 200)
RED = (255, 84, 84)
TEAL = (30, 110, 112)
TEAL2 = (18, 72, 76)
BLK = "InterDisplay-Black.otf"
SEMI = "Inter-SemiBold.otf"

def sdur(name):
    for s in scenes:
        if s["visual"] == name:
            return s["vis_end"] - (s["start"] if s is not scenes[0] else 0.0)
    return 4.0

def poly(d, pts, col):
    d.polygon(p(*[v for xy in pts for v in xy]), fill=col)

def circ(d, x, y, r, col):
    d.ellipse(p(x - r, y - r, x + r, y + r), fill=col)

def ring(d, x, y, r, col, w):
    d.ellipse(p(x - r, y - r, x + r, y + r), outline=col, width=max(1, int(w * S)))

def line(d, pts, col, w):
    d.line(p(*[v for xy in pts for v in xy]), fill=col, width=max(1, int(w * S)), joint="curve")

def label(d, x, y, s, col, a, size=28, f=BLK):
    if a <= 0: return
    text_c(d, x, y, s, FL(f, max(1, int(size))), rgba(col, a))

def chip(d, x, y, s, col, a, size=30, tcol=None):
    if a <= 0: return
    f = FL(BLK, max(1, int(size)))
    tw = d.textlength(s, font=f) / S
    w = tw + 50
    d.rounded_rectangle(p(x - w / 2, y, x + w / 2, y + size * 1.7), radius=size * 0.85 * S, fill=rgba(col, a))
    text_c(d, x, y + size * 0.3, s, f, rgba(tcol or BG, a))

def rrect(d, x0, y0, x1, y1, r, col, outline=None, w=0):
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=r * S, fill=col, outline=outline, width=int(w * S) if w else 0)

_CARS = {}
def car_img(name, w):
    key = (name, int(w))
    if key not in _CARS:
        im = Image.open(os.path.join(os.path.dirname(BASE.rstrip("/")), "..", "assets", "cars", name + ".png")).convert("RGBA")
        bb = im.getbbox(); im = im.crop(bb)
        ww = int(w * S); hh = int(im.height * ww / im.width)
        _CARS[key] = (im.resize((ww, hh), Image.LANCZOS), bb)
    return _CARS[key]

def put_car(d, name, x, y, w, a=1.0):
    im, bb = car_img(name, w)
    if a < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * clamp(a))))
    d._image.alpha_composite(im, (int(x * S), int(y * S)))
    return w / (bb[2] - bb[0])

def car_pt(x, y, w, sx, sy):
    sc = w / 1110
    return x + (sx - 245) * sc, y + (sy - 367) * sc
def xmark(d, x, y, r, col, a, w=16):
    line(d, [(x - r, y - r), (x + r, y + r)], rgba(col, a), w)
    line(d, [(x - r, y + r), (x + r, y - r)], rgba(col, a), w)

def check(d, x, y, r, col, a, w=10):
    line(d, [(x - r, y), (x - r * 0.3, y + r * 0.7), (x + r, y - r * 0.7)], rgba(col, a), w)

def bolt(d, x, y, sc, col, a):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in pts], rgba(col, a))

BLUE = (90, 200, 255)
YEL = (255, 205, 60)

def dashed_ring(d, x, y, r, col, a, w=8, n=16, rot=0.0):
    for k in range(n):
        a0 = rot + k * 360 / n
        d.arc(p(x - r, y - r, x + r, y + r), a0, a0 + 360 / n * 0.55, fill=rgba(col, a), width=max(1, int(w * S)))

def ghost_wheel(d, x, y, r, a, t):
    dashed_ring(d, x, y, r, MUTED, a * 0.8, w=9, rot=t * 20)
    dashed_ring(d, x, y, r * 0.25, MUTED, a * 0.6, w=6, n=8)
    for ang in (200, 340, 90):
        rr = math.radians(ang)
        line(d, [(x + math.cos(rr) * r * 0.3, y + math.sin(rr) * r * 0.3), (x + math.cos(rr) * r * 0.85, y + math.sin(rr) * r * 0.85)], rgba(MUTED, a * 0.35), 6)

def pedal(d, x, y, sc, col, a):
    rrect(d, x - 22 * sc, y - 60 * sc, x + 22 * sc, y + 10 * sc, 8 * sc, rgba(col, a))
    line(d, [(x, y - 60 * sc), (x - 10 * sc, y - 110 * sc)], rgba(col, a), 6 * sc)

def seat(d, x, y, sc, col, a):
    rrect(d, x - 70 * sc + 6, y - 150 * sc + 10, x + 70 * sc + 6, y + 40 * sc + 10, 34 * sc, rgba((0, 0, 0), a * 0.5))
    rrect(d, x - 70 * sc, y - 150 * sc, x + 70 * sc, y + 40 * sc, 34 * sc, rgba(col, a), outline=rgba(STEEL, a), w=4)
    rrect(d, x - 42 * sc, y - 205 * sc, x + 42 * sc, y - 150 * sc, 20 * sc, rgba(col, a), outline=rgba(STEEL, a), w=4)

def cabin(d, a, t, lt):
    """interior seen from the back seat: windshield, dash, two seats"""
    poly(d, [(120, 120), (780, 120), (850, 400), (50, 400)], rgba((26, 40, 56), a))
    # road through windshield
    poly(d, [(420, 170), (480, 170), (700, 400), (200, 400)], rgba((34, 40, 50), a))
    for k in range(4):
        u = ((lt * 0.8 + k / 4) % 1.0)
        yy = 175 + 225 * u * u
        hw = 3 + 10 * u * u
        rrect(d, 450 - hw, yy, 450 + hw, yy + 6 + 30 * u * u, 3, rgba(YEL, a * 0.8))
    poly(d, [(30, 400), (870, 400), (870, 470), (30, 470)], rgba(DARK, a))
    rrect(d, 30, 395, 870, 412, 6, rgba(STEEL, a))
    rrect(d, 330, 418, 570, 450, 10, rgba(BG, a))
    rrect(d, 340, 424, 340 + 220 * (0.5 + 0.5 * math.sin(t * 1.5)), 444, 8, rgba(ACC, a * 0.6))

def vis_sw_hook(d, lt, t):
    label(d, 450, -10, "NO STEERING WHEEL", WHITE, 1, size=86)
    label(d, 450, 95, "IS IT LEGAL?", ACC, 1, size=72)
    a = 1
    # cabin shifted down
    d2y = 120
    poly(d, [(120, 120 + d2y), (780, 120 + d2y), (850, 400 + d2y), (50, 400 + d2y)], rgba((26, 40, 56), a))
    poly(d, [(420, 170 + d2y), (480, 170 + d2y), (700, 400 + d2y), (200, 400 + d2y)], rgba((34, 40, 50), a))
    for k in range(4):
        u = ((lt * 0.8 + k / 4) % 1.0)
        yy = 175 + d2y + 225 * u * u; hw = 3 + 10 * u * u
        rrect(d, 450 - hw, yy, 450 + hw, yy + 6 + 30 * u * u, 3, rgba(YEL, a * 0.8))
    poly(d, [(30, 400 + d2y), (870, 400 + d2y), (870, 470 + d2y), (30, 470 + d2y)], rgba(DARK, a))
    rrect(d, 30, 395 + d2y, 870, 412 + d2y, 6, rgba(STEEL, a))
    # ghost wheel where a driver would hold it
    ghost_wheel(d, 260, 470 + d2y, 105, a, t)
    k = back_out((lt - 0.6) / 0.35)
    if k > 0: xmark(d, 260, 470 + d2y, 70 * k, RED, clamp(k), w=18)
    # ghost pedals
    for i, px in enumerate((215, 300)):
        pedal(d, px, 790, 1.0, (60, 70, 84), a)
    k2 = back_out((lt - 1.3) / 0.35)
    if k2 > 0: xmark(d, 258, 750, 55 * k2, RED, clamp(k2), w=14)
    # ghost mirror
    rrect(d, 560, 255, 700, 300, 18, None, outline=rgba(MUTED, 0.8), w=5)
    k3 = back_out((lt - 2.0) / 0.35)
    if k3 > 0: xmark(d, 630, 278, 34 * k3, RED, clamp(k3), w=12)
    chips = [(0.6, 600, 540, "NO WHEEL"), (1.3, 600, 640, "NO PEDALS"), (2.0, 600, 740, "NO MIRRORS")]
    for st, x, y, s in chips:
        kc = ease_out((lt - st) / 0.3)
        chip(d, x + 40 * (1 - kc), y, s, RED, kc, size=36, tcol=WHITE)

def vis_sw_cab(d, lt, t):
    a = ease_out(lt / 0.3)
    w = 700; x = 100 - 30 * (1 - ease_out(lt / 1.2)); y = 120
    # camera cones sweeping in front of the car
    kc = ease_out((lt - 1.0) / 0.5)
    if kc > 0:
        for i, (ox, ang) in enumerate(((250, 200), (210, 160), (330, 240))):
            sw = 10 * math.sin(t * 1.6 + i)
            a0 = math.radians(ang - 22 + sw); a1 = math.radians(ang + 22 + sw)
            R = 330
            poly(d, [(ox + 40, 330), (ox + 40 + math.cos(a0) * R, 330 + math.sin(a0) * R * 0.6), (ox + 40 + math.cos(a1) * R, 330 + math.sin(a1) * R * 0.6)], rgba(BLUE, kc * 0.18))
    put_car(d, "cn_front34_white", x, y, w, a)
    specs = [(1.2, "2 SEATS", ACC), (2.0, "CAMERAS ONLY", BLUE), (3.0, "PAID RIDES · AUSTIN, TX", WHITE)]
    for i, (st, s, col) in enumerate(specs):
        k = back_out((lt - st) / 0.4)
        if k <= 0: continue
        chip(d, 450, 520 + i * 90, s, col, clamp(k), size=max(1, 38 * min(1.0, k)))
    k = ease_out((lt - 3.6) / 0.4)
    label(d, 450, 0, "TESLA CYBERCAB", WHITE, a, size=70)
    label(d, 450, 800, "SINCE SEPTEMBER 2026 · ILLUSTRATION", MUTED, k, size=24, f=SEMI)

def vis_sw_rules(d, lt, t):
    a = ease_out(lt / 0.3)
    label(d, 450, -10, "U.S. SAFETY RULES (FMVSS)", WHITE, a, size=50)
    # rule book page
    k = ease_out(lt / 0.5)
    x0, y0 = 80, 90
    rrect(d, x0 + 10, y0 + 14, x0 + 470 + 10, y0 + 640 + 14, 20, rgba((0, 0, 0), k * 0.5))
    rrect(d, x0, y0, x0 + 470, y0 + 640, 20, rgba((232, 236, 240), k))
    for i in range(12):
        kk = ease_out((lt - 0.3 - i * 0.07) / 0.3)
        ww = 380 - (i * 53) % 140
        rrect(d, x0 + 40, y0 + 60 + i * 46, x0 + 40 + ww * kk, y0 + 74 + i * 46, 6, rgba((150, 160, 172), k))
    # highlight rule 135
    kh = ease_out((lt - 1.6) / 0.5)
    if kh > 0:
        rrect(d, x0 + 24, y0 + 240, x0 + 24 + 422 * kh, y0 + 340, 12, rgba(YEL, 0.85 * k))
        label(d, x0 + 235, y0 + 252, "FMVSS 135", BG, kh, size=34)
        label(d, x0 + 235, y0 + 296, "BRAKES: A FOOT CONTROL", BG, kh, size=24)
    # driver assumption at right: person + pedal, then person vanishes
    kp = ease_out((lt - 0.5) / 0.4)
    gone = ease_inout((lt - 3.4) / 0.8)
    person(d, 700, 420, 1.2, WHITE, kp * (1 - gone), t=0)
    pedal(d, 790, 610, 1.2, ACC2, kp)
    label(d, 790, 640, "FOOT PEDAL", ACC2, kp, size=28)
    if gone > 0:
        label(d, 700, 220, "?", RED, gone, size=180)
        label(d, 700, 700, "NO DRIVER", RED, gone, size=40)

def vis_sw_audit(d, lt, t):
    a = ease_out(lt / 0.3)
    # calendar flip SEP 3 -> SEP 4
    flip = ease_inout((lt - 0.5) / 0.5)
    rrect(d, 300, 0, 600, 250, 24, rgba(WHITE, a))
    rrect(d, 300, 0, 600, 70, 24, rgba(RED, a)); rrect(d, 300, 40, 600, 70, 0, rgba(RED, a))
    label(d, 450, 10, "SEPT 2026", WHITE, a, size=40)
    label(d, 450, 85, "3" if flip < 0.5 else "4", BG, a, size=130)
    kl = ease_out((lt - 0.5) / 0.4)
    label(d, 160, 60, "LAUNCH", MUTED, kl, size=28, f=SEMI); label(d, 160, 100, "SEPT 3", WHITE, kl, size=38)
    label(d, 745, 60, "AUDIT", ACC, ease_out((lt - 1.0) / 0.4), size=28, f=SEMI); label(d, 745, 100, "SEPT 4", ACC, ease_out((lt - 1.0) / 0.4), size=38)
    # grid of cab icons counting up to ~1,000
    cols, rows_ = 20, 8
    shown = int(cols * rows_ * ease_inout((lt - 1.5) / 2.5))
    for r in range(rows_):
        for c in range(cols):
            idx = r * cols + c
            if idx >= shown: continue
            x = 75 + c * 39; y = 320 + r * 36
            rrect(d, x, y, x + 30, y + 18, 7, rgba(STEEL, a))
            rrect(d, x + 7, y - 6, x + 23, y + 4, 4, rgba(STEEL, a))
    n = int(1000 * ease_inout((lt - 1.5) / 2.5))
    if lt > 1.5:
        label(d, 450, 620, f"~{n:,} CYBERCABS", WHITE, a, size=60)
    # magnifier sweeping over grid
    km = ease_out((lt - 2.0) / 0.4)
    if km > 0:
        mx = 450 + 280 * math.sin(lt * 1.1); my = 440 + 60 * math.cos(lt * 1.7)
        ring(d, mx, my, 70, rgba(ACC, km), 12)
        line(d, [(mx + 50, my + 50), (mx + 110, my + 110)], rgba(ACC, km), 22)
    kq = ease_out((lt - 4.5) / 0.4)
    chip(d, 450, 730, "HOW DID TESLA CERTIFY THEM?", ACC, kq, size=34)

def vis_sw_secret(d, lt, t):
    a = ease_out(lt / 0.3)
    # timeline
    pts = [(0.0, 130, "SEPT", "21 QUESTIONS", WHITE), (0.9, 450, "OCT 30", "ANSWERED", ACC), (2.2, 770, "NOV 5", "KEEP IT SECRET", RED)]
    prog = ease_inout(lt / 2.4)
    line(d, [(130, 70), (130 + 640 * prog, 70)], rgba(STEEL, a), 8)
    for st, x, top, bot, col in pts:
        k = back_out((lt - st) / 0.4)
        if k <= 0: continue
        circ(d, x, 70, 20 * clamp(k), rgba(col, 1))
        label(d, x, 0, top, col, clamp(k), size=32)
        label(d, x, 105, bot, WHITE if col != RED else RED, clamp(k), size=26, f=SEMI if col != RED else BLK)
    # answer document with redaction bars sliding across
    kd = ease_out((lt - 0.8) / 0.5)
    x0, y0 = 220, 200
    rrect(d, x0 + 10, y0 + 14, x0 + 460 + 10, y0 + 520 + 14, 18, rgba((0, 0, 0), kd * 0.5))
    rrect(d, x0, y0, x0 + 460, y0 + 520, 18, rgba((232, 236, 240), kd))
    label(d, x0 + 230, y0 + 24, "TESLA RESPONSE", BG, kd, size=30)
    for i in range(9):
        ww = 380 - (i * 61) % 150
        yy = y0 + 90 + i * 44
        rrect(d, x0 + 40, yy, x0 + 40 + ww, yy + 14, 6, rgba((150, 160, 172), kd))
        kr = ease_inout((lt - 2.6 - i * 0.12) / 0.3)
        if kr > 0:
            rrect(d, x0 + 34, yy - 8, x0 + 34 + (ww + 12) * kr, yy + 22, 4, rgba((12, 14, 18), kd))
    # stamp
    ks = back_out((lt - 3.9) / 0.35)
    if ks > 0:
        sz = max(1, int(50 * ks))
        rrect(d, 450 - 270 * ks, 440 - 50 * ks, 450 + 270 * ks, 440 + 50 * ks, 14, rgba(BG, clamp(ks) * 0.85), outline=rgba(RED, clamp(ks)), w=8)
        label(d, 450, 440 - 32 * ks, "CONFIDENTIAL", RED, clamp(ks), size=sz)
    kf = ease_out((lt - 4.4) / 0.4)
    label(d, 450, 760, "\"THE ENTIRETY OF THIS FILE IS CONFIDENTIAL\"", MUTED, kf, size=24, f=SEMI)

def vis_sw_fair(d, lt, t):
    a = ease_out(lt / 0.3)
    kv = back_out(lt / 0.4)
    chip(d, 450, 0, "NO VIOLATION FOUND SO FAR", ACC, clamp(kv), size=38)
    # two roads splitting
    ks = ease_out((lt - 1.5) / 0.6)
    tilt = 0.0
    # balance scale
    bx, by = 450, 260
    line(d, [(bx, by), (bx, 560)], rgba(STEEL, a), 14)
    poly(d, [(bx - 90, 580), (bx + 90, 580), (bx + 50, 550), (bx - 50, 550)], rgba(STEEL, a))
    tilt = 0.08 * math.sin(t * 1.4)
    lx, ly = bx - 280, by + 280 * tilt * -1
    rx, ry = bx + 280, by - 280 * tilt * -1
    line(d, [(lx, ly), (rx, ry)], rgba(CHROME, a), 12)
    circ(d, bx, by, 18, rgba(CHROME, a))
    for (px, py, head, s1, s2, col, st) in ((lx, ly, "TESLA", "SELF-", "CERTIFIED", WHITE, 0.4), (rx, ry, "ZOOX", "OFFICIAL", "EXEMPTION", ACC2, 1.6)):
        k = ease_out((lt - st) / 0.4)
        line(d, [(px, py), (px - 90, py + 170)], rgba(STEEL, a), 4)
        line(d, [(px, py), (px + 90, py + 170)], rgba(STEEL, a), 4)
        poly(d, [(px - 120, py + 170), (px + 120, py + 170), (px + 90, py + 200), (px - 90, py + 200)], rgba(DARK, a))
        if k > 0:
            rrect(d, px - 110, py + 30 - 30 * (1 - k), px + 110, py + 165, 18, rgba(col, k))
            label(d, px, py + 42, head, BG, k, size=38)
            label(d, px, py + 92, s1, BG, k, size=24, f=SEMI)
            label(d, px, py + 124, s2, BG, k, size=24, f=SEMI)
    kz = ease_out((lt - 3.0) / 0.4)
    label(d, rx, ry + 225, "UP TO 2,500 / YEAR", ACC2, kz, size=28)
    label(d, lx, ly + 225, "UNDER AUDIT", MUTED, kz, size=28)
    label(d, 450, 700, "NO EXEMPTION  vs  EXEMPTION", WHITE, ease_out((lt - 3.6) / 0.4), size=34)

def vis_sw_outro(d, lt, t):
    dur = sdur("sw_outro")
    if lt < dur * 0.58:
        a = ease_out(lt / 0.3)
        k1 = back_out(lt / 0.4); k2 = back_out((lt - 0.5) / 0.4)
        if k1 > 0:
            rrect(d, 60, 160, 400, 380, 30, rgba(STEEL, clamp(k1)))
            label(d, 230, 210, "BUSINESS", WHITE, clamp(k1), size=max(1, 52 * k1))
            label(d, 230, 285, "SECRET", WHITE, clamp(k1), size=max(1, 52 * k1))
        label(d, 450, 245, "OR", WHITE, a, size=40)
        if k2 > 0:
            rrect(d, 500, 160, 840, 380, 30, rgba(ACC, clamp(k2)))
            label(d, 670, 210, "PUBLIC", BG, clamp(k2), size=max(1, 52 * k2))
            label(d, 670, 285, "RECORD", BG, clamp(k2), size=max(1, 52 * k2))
        label(d, 450, 470, "WHAT DO YOU THINK?", WHITE, ease_out((lt - 1.0) / 0.4), size=50)
        label(d, 450, 560, "TELL ME BELOW", MUTED, ease_out((lt - 1.3) / 0.4), size=32, f=SEMI)
    else:
        k = back_out((lt - dur * 0.58) / 0.5)
        bolt(d, 450, 220, 1.7 * k, ACC, clamp(k))
        label(d, 450, 380, "EV DRIVE", WHITE, clamp(k), size=max(1, 130 * k))
        a = ease_out((lt - dur * 0.58 - 0.4) / 0.4)
        rrect(d, 170, 600, 730, 710, 55, rgba(ACC, a))
        label(d, 450, 625, "FOLLOW FOR DAILY CAR TECH", BG, a, size=36)

VIS.update({"sw_hook": vis_sw_hook, "sw_cab": vis_sw_cab, "sw_rules": vis_sw_rules, "sw_audit": vis_sw_audit,
            "sw_secret": vis_sw_secret, "sw_fair": vis_sw_fair, "sw_outro": vis_sw_outro})
