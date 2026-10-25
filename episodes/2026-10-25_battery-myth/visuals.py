# Episode visuals: Myth vs fact — do EV batteries die after a few years?
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
RED = (255, 84, 84)
BLUE = (80, 170, 255)

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

def battery_h(d, x, y, w, h, level, col, a=1.0, outline=WHITE):
    """Horizontal battery icon; level 0..1."""
    d.rounded_rectangle(p(x, y, x + w, y + h), radius=int(h * 0.18 * S), outline=rgba(outline, a), width=int(7 * S))
    d.rounded_rectangle(p(x + w + 4, y + h * 0.3, x + w + 18, y + h * 0.7), radius=int(4 * S), fill=rgba(outline, a))
    pad = 14
    if level > 0.01:
        d.rounded_rectangle(p(x + pad, y + pad, x + pad + (w - 2 * pad) * level, y + h - pad), radius=int(6 * S), fill=rgba(col, a))

def phone(d, cx, cy, sc, a=1.0):
    d.rounded_rectangle(p(cx - 80 * sc, cy - 150 * sc, cx + 80 * sc, cy + 150 * sc), radius=int(26 * S * sc), fill=rgba(PANEL, a), outline=rgba(MUTED, a), width=int(6 * S))
    d.rounded_rectangle(p(cx - 25 * sc, cy - 136 * sc, cx + 25 * sc, cy - 128 * sc), radius=int(4 * S), fill=rgba(MUTED, a))

def stamp(d, cx, cy, word, col, k, ang_deg=-12):
    """Rubber-stamp label that pops in (drawn on a rotated temp layer)."""
    if k <= 0.01: return
    f = FL("InterDisplay-Black.otf", 84)
    tw = d.textlength(word, font=f) / S
    w, h = tw + 70, 130
    tmp = Image.new("RGBA", (int(w * S) + 40, int(h * S) + 40), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.rounded_rectangle((20, 20, 20 + w * S, 20 + h * S), radius=int(18 * S), outline=rgba(col, clamp(k)), width=int(10 * S))
    td.text((20 + 35 * S, 20 + 14 * S), word, font=f, fill=rgba(col, clamp(k)))
    sc = 1.6 - 0.6 * clamp(k)
    tmp = tmp.resize((max(1, int(tmp.width * sc)), max(1, int(tmp.height * sc))), Image.BILINEAR).rotate(ang_deg, expand=True, resample=Image.BICUBIC)
    d._image.alpha_composite(tmp, (int(cx * S - tmp.width / 2), int(cy * S - tmp.height / 2)))

def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

# ---------- 1. the myth: phone battery fades, "MYTH" stamp ----------
def vis_myth(d, lt, t):
    dur = sdur("myth")
    k = back_out(lt / 0.5)
    phone(d, 260, 330, 1.0 * max(k, 0.01), clamp(k))
    lvl = 1 - 0.85 * ease_inout((lt - 0.4) / 2.2)
    col = ACC if lvl > 0.5 else (ACC2 if lvl > 0.25 else RED)
    # vertical battery inside phone
    bx0, by0, bx1, by1 = 215, 220, 305, 440
    d.rounded_rectangle(p(bx0, by0, bx1, by1), radius=12 * S, outline=rgba(WHITE, clamp(k)), width=6 * S)
    d.rectangle(p(240, 206, 280, 220), fill=rgba(WHITE, clamp(k)))
    d.rounded_rectangle(p(bx0 + 12, by1 - 12 - (by1 - by0 - 24) * lvl, bx1 - 12, by1 - 12), radius=6 * S, fill=rgba(col, clamp(k)))
    text_c(d, 260, 470, f"{int(round(lvl * 100))}%", FL("InterDisplay-Black.otf", 34), rgba(col, clamp(k)))
    # "=" then car battery
    a2 = ease_out((lt - 0.9) / 0.4)
    text_c(d, 450, 290, "=", FL("InterDisplay-Black.otf", 90), rgba(MUTED, a2))
    car_side(d, 650, 380, 0.62, WHITE, a2)
    battery_h(d, 560, 430, 170, 64, lvl, col, a2)
    text_c(d, 650, 520, "AFTER A FEW YEARS?", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a2))
    # MYTH stamp
    stamp(d, 450, 690, "MYTH?", ACC2, ease_out((lt - 2.4) / 0.35))

# ---------- 2. 1.8% per year counter + fleet of dots ----------
def vis_rate(d, lt, t):
    dur = sdur("rate")
    # fleet of ~5,000 EVs represented by a dot field
    n_on = int(200 * ease_out(lt / 2.0))
    for i in range(200):
        r_, c_ = divmod(i, 20)
        x = 92 + c_ * 37.5; y = 40 + r_ * 26
        on = i < n_on
        d.rounded_rectangle(p(x - 12, y - 7, x + 12, y + 7), radius=4 * S, fill=rgba(ACC if on else DARK, 0.9 if on else 0.6))
    a = ease_out((lt - 0.3) / 0.4)
    cnt = int(round(4900 * ease_out(lt / 2.0) / 100.0)) * 100
    text_c(d, 450, 300, f"≈ {cnt:,} EVs TRACKED", FL("InterDisplay-Bold.otf", 34), rgba(WHITE, a))
    # big counter
    k = ease_out((lt - 2.3) / 1.6)
    val = 1.8 * k
    a3 = ease_out((lt - 2.2) / 0.3)
    text_c(d, 450, 380, f"−{val:.1f}%", FL("InterDisplay-Black.otf", 170), rgba(ACC, a3))
    text_c(d, 450, 590, "CAPACITY PER YEAR (AVERAGE)", FL("InterDisplay-Bold.otf", 32), rgba(MUTED, a3))
    # one year's loss shown as a sliver of a full battery
    a4 = ease_out((lt - 3.6) / 0.5)
    battery_h(d, 190, 680, 500, 110, 1.0, ACC, a4)
    sliver = 0.018 * 472 * 4 * ease_out((lt - 4.2) / 0.6)  # exaggerated x4 so it is visible
    if sliver > 1:
        d.rectangle(p(190 + 14 + 472 - sliver, 694, 190 + 14 + 472, 776), fill=rgba(ACC2, a4))
    text_c(d, 450, 810, "ONE YEAR'S LOSS (SHOWN ×4)", FL("Inter-SemiBold.otf", 24), rgba(ACC2, ease_out((lt - 4.6) / 0.4)))

# ---------- 3. 12-year projection line ----------
def vis_curve(d, lt, t):
    dur = sdur("curve")
    x0, x1, y0, y1 = 150, 800, 120, 640   # plot box: y0 = 100%, y1 = 50%
    def Y(v): return y1 - (v - 50) / 50 * (y1 - y0)
    def X(yr): return x0 + (x1 - x0) * yr / 12
    a = ease_out(lt / 0.4)
    d.line(p(x0, y0 - 20, x0, y1, x1 + 20, y1), fill=rgba(MUTED, a), width=4 * S)
    fs = FL("Inter-SemiBold.otf", 26)
    for v in (100, 75, 50):
        d.line(p(x0, Y(v), x1, Y(v)), fill=rgba(DARK, a), width=2 * S)
        tw = d.textlength(f"{v}%", font=fs)
        d.text((x0 * S - tw - 16 * S, Y(v) * S - 16 * S), f"{v}%", font=fs, fill=rgba(MUTED, a))
    for yr in (0, 4, 8, 12):
        text_c(d, X(yr), y1 + 16, str(yr), fs, rgba(MUTED, a))
    text_c(d, (x0 + x1) / 2, y1 + 56, "YEARS", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
    k = ease_inout((lt - 0.3) / 2.2)
    yr_now = 12 * k
    pts = []
    for i in range(0, 61):
        yr = 12 * i / 60
        if yr > yr_now: break
        pts.append((X(yr), Y(100 - 1.8 * yr)))
    if len(pts) > 1:
        # area under line
        poly(d, pts + [(pts[-1][0], y1), (pts[0][0], y1)], rgba(ACC, 0.12))
        d.line([v * S for xy in pts for v in xy], fill=rgba(ACC, 1), width=8 * S, joint="curve")
        ex, ey = pts[-1]
        for g, al in ((22, 0.15), (14, 0.3)):
            d.ellipse(p(ex - g, ey - g, ex + g, ey + g), fill=rgba(ACC, al))
        d.ellipse(p(ex - 9, ey - 9, ex + 9, ey + 9), fill=rgba(WHITE, 1))
        cap = 100 - 1.8 * yr_now
        text_c(d, min(ex, 720), ey - 80, f"{cap:.0f}%", FL("InterDisplay-Black.otf", 52), rgba(WHITE, 1))
    a2 = ease_out((lt - 2.5) / 0.4)
    glow_rect(d, 200, 740, 700, 830, 24, ACC, a2)
    text_c(d, 450, 760, "NEARLY 80% LEFT", FL("InterDisplay-Black.otf", 44), rgba(BG, a2))

# ---------- 4. replacement rates by model year ----------
def vis_replace(d, lt, t):
    dur = sdur("replace")
    a = ease_out(lt / 0.4)
    text_c(d, 450, 20, "20,000+ EVs STUDIED", FL("InterDisplay-Black.otf", 50), rgba(WHITE, a))
    text_c(d, 450, 90, "SHARE THAT GOT A NEW BATTERY PACK", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
    base = 640
    scale = 30   # px per percent
    bars = [("PRE-2015", 13, ACC2, "UP TO 13%", 0.6), ("2016 +", 1, ACC, "≤ 1%", 2.6)]
    for i, (lab, v, col, txt, st) in enumerate(bars):
        cx = 280 + i * 340
        k = ease_out((lt - st) / 1.0)
        h = max(6, v * scale * k)
        if k > 0:
            glow_rect(d, cx - 90, base - h, cx + 90, base, 14, col, clamp(k * 1.3))
            text_c(d, cx, base - h - 72, txt, FL("InterDisplay-Black.otf", 52), rgba(col, clamp(k * 1.5)))
        text_c(d, cx, base + 20, lab, FL("InterDisplay-Bold.otf", 36), rgba(WHITE, a))
    d.line(p(120, base, 780, base), fill=rgba(MUTED, a), width=4 * S)
    # 100-car strip: 1 in 100 replaced
    a3 = ease_out((lt - 3.6) / 0.5)
    for i in range(50):
        r_, c_ = divmod(i, 25)
        x = 126 + c_ * 27; y = 740 + r_ * 30
        col = ACC2 if i == 0 else ACC
        d.rounded_rectangle(p(x - 10, y - 8, x + 10, y + 8), radius=4 * S, fill=rgba(col, a3 * (1 if i == 0 else 0.55)))
    text_c(d, 450, 815, "NEWER EVs: FEWER THAN 1 IN 100", FL("Inter-SemiBold.otf", 26), rgba(MUTED, a3))

# ---------- 5. why: liquid cooling + hidden buffer ----------
def vis_buffer(d, lt, t):
    dur = sdur("buffer")
    # tall battery pack cross-section
    x0, x1, y0, y1 = 300, 600, 90, 690
    k = ease_out(lt / 0.5)
    d.rounded_rectangle(p(x0 - 14, y0 - 14, x1 + 14, y1 + 14), radius=28 * S, fill=rgba(PANEL, k), outline=rgba(WHITE, k), width=6 * S)
    d.rounded_rectangle(p(400, y0 - 36, 500, y0 - 14), radius=8 * S, fill=rgba(WHITE, k))
    H_ = y1 - y0
    top = y0 + H_ * 0.05; bot = y1 - H_ * 0.15
    fill = ease_inout((lt - 0.3) / 1.2)
    # usable band
    d.rectangle(p(x0, bot - (bot - top) * fill, x1, bot), fill=rgba(ACC, 0.85 * k))
    # hidden buffers (hatched)
    hb = ease_out((lt - 1.6) / 0.5)
    for (ya, yb) in ((y0, top), (bot, y1)):
        d.rectangle(p(x0, ya, x1, yb), fill=rgba(ACC2, 0.25 * hb))
        for hx in range(int(x0) - 60, int(x1), 22):
            d.line(p(max(hx, x0), ya + (max(hx, x0) - hx), min(hx + (yb - ya), x1), ya + (min(hx + (yb - ya), x1) - hx)), fill=rgba(ACC2, 0.8 * hb), width=3 * S)
    fs = FL("InterDisplay-Bold.otf", 28)
    d.line(p(x1 + 20, (y0 + top) / 2, x1 + 70, (y0 + top) / 2), fill=rgba(ACC2, hb), width=3 * S)
    d.text(((x1 + 80) * S, ((y0 + top) / 2 - 18) * S), "HIDDEN ~5%", font=fs, fill=rgba(ACC2, hb))
    d.line(p(x1 + 20, (bot + y1) / 2, x1 + 70, (bot + y1) / 2), fill=rgba(ACC2, hb), width=3 * S)
    d.text(((x1 + 80) * S, ((bot + y1) / 2 - 18) * S), "HIDDEN ~15%", font=fs, fill=rgba(ACC2, hb))
    ua = ease_out((lt - 1.0) / 0.4)
    text_c(d, 450, (top + bot) / 2 - 24, "USABLE", FL("InterDisplay-Black.otf", 44), rgba(BG, ua))
    # liquid cooling plate on the left with flowing coolant
    ca = ease_out((lt - 2.8) / 0.5)
    px = 210
    d.rounded_rectangle(p(px - 26, y0, px + 26, y1), radius=20 * S, fill=rgba((18, 40, 70), ca), outline=rgba(BLUE, ca), width=4 * S)
    for i in range(9):
        ph = (t * 0.6 + i / 9) % 1.0
        yy = y1 - 20 - ph * (H_ - 40)
        d.ellipse(p(px - 11, yy - 11, px + 11, yy + 11), fill=rgba(BLUE, ca * (0.5 + 0.5 * math.sin(ph * math.pi))))
    for yy in range(int(y0) + 60, int(y1), 120):
        d.line(p(px + 26, yy, x0 - 14, yy), fill=rgba(BLUE, 0.6 * ca), width=5 * S)
    text_c(d, px - 20, y1 + 40, "LIQUID", FL("InterDisplay-Bold.otf", 28), rgba(BLUE, ca))
    text_c(d, px - 20, y1 + 74, "COOLING", FL("InterDisplay-Bold.otf", 28), rgba(BLUE, ca))
    text_c(d, 450, y1 + 40, "BATTERY PACK", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, k))

# ---------- 6. outro ----------
def vis_outro_b(d, lt, t):
    dur = sdur("outro_b")
    cut = dur * 0.45
    if lt < cut:
        k = ease_out(lt / 0.5)
        # two lifespan bars: car body vs battery
        fs = FL("InterDisplay-Bold.otf", 34)
        g1 = ease_out((lt - 0.2) / 1.0); g2 = ease_out((lt - 0.4) / 1.4)
        d.text((120 * S, 170 * S), "THE CAR", font=fs, fill=rgba(WHITE, k))
        d.rounded_rectangle(p(120, 220, 120 + 560 * g1, 280), radius=16 * S, fill=rgba(WHITE, 0.85 * k))
        d.text((120 * S, 330 * S), "ITS BATTERY", font=fs, fill=rgba(ACC, k))
        glow_rect(d, 120, 380, 120 + 680 * g2, 440, 16, ACC, k)
        text_c(d, 450, 560, "WHAT'S NEXT FOR IT?", FL("InterDisplay-Black.otf", 60), rgba(WHITE, ease_out((lt - 1.2) / 0.4)))
    else:
        end_card(d, lt, cut)

VIS.update({"myth": vis_myth, "rate": vis_rate, "curve": vis_curve, "replace": vis_replace,
            "buffer": vis_buffer, "outro_b": vis_outro_b})
