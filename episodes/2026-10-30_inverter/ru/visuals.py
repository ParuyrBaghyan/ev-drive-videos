# Episode visuals: How it works — the traction inverter (DC -> three-phase AC).
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
PH = [ACC, ACC2, (110, 190, 255)]   # phase colours U, V, W

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

def panel(d, x0, y0, x1, y1, a=1.0, outline=None):
    d.rounded_rectangle(p(x0 + 6, y0 + 10, x1 + 6, y1 + 10), radius=28 * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=28 * S, fill=rgba(PANEL, 0.94 * a),
                        outline=rgba(outline or DARK, a), width=int(4 * S))

def battery(d, cx, cy, w, h, a=1.0, fill=0.8):
    panel(d, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, a, outline=ACC)
    d.rounded_rectangle(p(cx + w / 2, cy - h * 0.18, cx + w / 2 + 16, cy + h * 0.18), radius=6 * S, fill=rgba(ACC, a))
    n = 5
    gw = (w - 40) / n
    for i in range(n):
        on = i < round(n * fill)
        x0 = cx - w / 2 + 20 + i * gw
        d.rounded_rectangle(p(x0 + 4, cy - h / 2 + 18, x0 + gw - 4, cy + h / 2 - 18), radius=8 * S,
                            fill=rgba(ACC if on else DARK, a * (0.9 if on else 0.6)))

def motor(d, cx, cy, r, ang, a=1.0, col=WHITE):
    # stator ring with three coloured coil groups, spinning rotor
    d.ellipse(p(cx - r - 8, cy - r - 2, cx + r + 8, cy + r + 14), fill=rgba((0, 0, 0), 0.35 * a))
    d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=rgba(PANEL, a), outline=rgba(DARK, a), width=int(6 * S))
    for k in range(6):
        aa = math.radians(k * 60 - 90)
        x, y = cx + math.cos(aa) * r * 0.78, cy + math.sin(aa) * r * 0.78
        rr = r * 0.17
        d.ellipse(p(x - rr, y - rr, x + rr, y + rr), fill=rgba(PH[k % 3], a * 0.95))
    rr = r * 0.48
    d.ellipse(p(cx - rr, cy - rr, cx + rr, cy + rr), fill=rgba((70, 78, 92), a))
    for k in range(2):
        aa = ang + k * math.pi
        d.line(p(cx, cy, cx + math.cos(aa) * rr * 0.9, cy + math.sin(aa) * rr * 0.9), fill=rgba(col, a), width=int(18 * S))
    d.ellipse(p(cx - 14, cy - 14, cx + 14, cy + 14), fill=rgba(col, a))

def wave_line(d, x0, x1, ymid, amp, freq, phase, col, a=1.0, w=7, reveal=1.0):
    pts = []
    n = 90
    for k in range(int(n * clamp(reveal)) + 1):
        x = x0 + (x1 - x0) * k / n
        y = ymid - amp * math.sin(2 * math.pi * freq * k / n + phase)
        pts.append((x, y))
    if len(pts) > 1:
        d.line([v * S for xy in pts for v in xy], fill=rgba(col, a), width=int(w * S), joint="curve")

def flow_dots(d, pts, t, col, a=1.0, speed=1.0, n=8, r=8):
    """Dots moving along a polyline (energy flow)."""
    segs = []; tot = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        l = math.hypot(x1 - x0, y1 - y0); segs.append((x0, y0, x1, y1, l)); tot += l
    for i in range(n):
        s = ((t * speed * 0.35 + i / n) % 1.0) * tot
        for x0, y0, x1, y1, l in segs:
            if s <= l:
                f = s / l; x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
                d.ellipse(p(x - r, y - r, x + r, y + r), fill=rgba(col, a)); break
            s -= l

def chip(d, cx, cy, w, h, a=1.0, label="ИНВЕРТОР", glow=0.0):
    if glow > 0:
        for g in range(4, 0, -1):
            e = g * 9
            d.rounded_rectangle(p(cx - w / 2 - e, cy - h / 2 - e, cx + w / 2 + e, cy + h / 2 + e), radius=(24 + e) * S,
                                fill=rgba(ACC, 0.05 * glow * a))
    panel(d, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, a, outline=ACC)
    for k in range(5):
        x = cx - w / 2 + 30 + k * (w - 60) / 4
        d.line(p(x, cy - h / 2 - 16, x, cy - h / 2), fill=rgba(MUTED, a), width=int(6 * S))
        d.line(p(x, cy + h / 2, x, cy + h / 2 + 16), fill=rgba(MUTED, a), width=int(6 * S))
    text_c(d, cx, cy - 22, label, FL("InterDisplay-Black.otf", 38), rgba(ACC, a))

# ---------- scene 1: two languages ----------
def vis_iv_hook(d, lt, t):
    a = ease_out(lt / 0.4)
    k = back_out((lt - 0.1) / 0.5)
    battery(d, 200, 250, 250 * (0.6 + 0.4 * clamp(k, 0, 1.1)), 130, a)
    text_c(d, 200, 345, "БАТАРЕЯ", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, a))
    k2 = back_out((lt - 0.4) / 0.5)
    motor(d, 690, 250, 110 * max(k2, 0.01), t * 5, a)
    text_c(d, 690, 375, "МОТОР", FL("InterDisplay-Bold.otf", 30), rgba(MUTED, a))
    # "speech bubbles": DC flat line vs AC wave
    b = ease_out((lt - 0.9) / 0.5)
    panel(d, 70, 450, 410, 640, b, outline=ACC)
    sh = (t * 120) % 60
    for x in range(100, 380, 60):
        xx = x + sh
        if xx < 380:
            d.line(p(xx, 545, min(xx + 30, 380), 545), fill=rgba(ACC, b), width=int(9 * S))
    text_c(d, 240, 580, "ПОСТОЯННЫЙ", FL("InterDisplay-Black.otf", 36), rgba(WHITE, b))
    b2 = ease_out((lt - 1.4) / 0.5)
    panel(d, 490, 450, 830, 640, b2, outline=ACC2)
    wave_line(d, 515, 805, 520, 40, 2, -t * 6, ACC2, b2, 8)
    text_c(d, 660, 580, "ПЕРЕМЕННЫЙ", FL("InterDisplay-Black.otf", 36), rgba(WHITE, b2))
    # question mark between them
    q = back_out((lt - 2.0) / 0.5)
    if q > 0:
        text_c(d, 450, 490 - 8 * math.sin(t * 4), "?", FL("InterDisplay-Black.otf", max(1, int(80 * q))), rgba(ACC, clamp(q)))
    text_c(d, 450, 730, "НУЖЕН ПЕРЕВОДЧИК", FL("InterDisplay-Black.otf", 48), rgba(WHITE, ease_out((lt - 2.6) / 0.4)))

# ---------- scene 2: DC vs three-phase AC ----------
def vis_iv_dcac(d, lt, t):
    a = ease_out(lt / 0.35)
    panel(d, 60, 60, 840, 300, a)
    text_c(d, 450, 80, "ПОСТОЯННЫЙ ТОК", FL("InterDisplay-Black.otf", 38), rgba(ACC, a))
    k = ease_out((lt - 0.2) / 1.0)
    d.line(p(110, 210, 110 + 680 * k, 210), fill=rgba(ACC, a), width=int(10 * S))
    for i in range(6):
        x = 110 + ((t * 140 + i * 115) % 680)
        if x < 110 + 680 * k:
            poly(d, [(x, 192), (x + 26, 210), (x, 228)], rgba(WHITE, a))
    text_c(d, 450, 240, "в одну сторону, ровно", FL("Inter-SemiBold.otf", 28), rgba(MUTED, a))
    b = ease_out((lt - 2.2) / 0.5)
    panel(d, 60, 340, 840, 800, b)
    text_c(d, 450, 360, "ТРЁХФАЗНЫЙ ПЕРЕМЕННЫЙ", FL("InterDisplay-Black.otf", 38), rgba(ACC2, b))
    labels = ["U", "V", "W"]
    for i in range(3):
        rv = ease_inout((lt - 2.6 - 0.5 * i) / 1.2)
        if rv > 0:
            wave_line(d, 140, 800, 580, 140, 2, -t * 4 - i * 2 * math.pi / 3, PH[i], b, 8, reveal=rv)
            text_c(d, 105, 430 + i * 60, labels[i], FL("InterDisplay-Black.otf", 34), rgba(PH[i], b * clamp(rv * 3)))
    d.line(p(140, 580, 800, 580), fill=rgba(DARK, b), width=int(3 * S))
    c = ease_out((lt - 5.0) / 0.5)
    text_c(d, 450, 735, "сдвиг 120° между фазами", FL("InterDisplay-Bold.otf", 32), rgba(WHITE, c))

# ---------- scene 3: six switches in three pairs ----------
def switch(d, x, y, on, a, col):
    d.ellipse(p(x - 9, y - 40 - 9, x + 9, y - 40 + 9), fill=rgba(MUTED, a))
    d.ellipse(p(x - 9, y + 40 - 9, x + 9, y + 40 + 9), fill=rgba(MUTED, a))
    if on:
        d.line(p(x, y - 40, x, y + 40), fill=rgba(col, a), width=int(10 * S))
    else:
        d.line(p(x, y + 40, x + 34, y - 30), fill=rgba(MUTED, a), width=int(10 * S))

def vis_iv_switches(d, lt, t):
    a = ease_out(lt / 0.35)
    chip(d, 450, 105, 330, 110, a, glow=0.6 + 0.4 * math.sin(t * 3))
    text_c(d, 450, 128, "6 КЛЮЧЕЙ · 3 ПАРЫ", FL("Inter-SemiBold.otf", 24), rgba(WHITE, a))
    # bus bars
    b = ease_out((lt - 0.5) / 0.5)
    d.line(p(170, 250, 730, 250), fill=rgba(ACC, b), width=int(8 * S))
    d.line(p(170, 650, 730, 650), fill=rgba(MUTED, b), width=int(8 * S))
    text_c(d, 110, 230, "+", FL("InterDisplay-Black.otf", 50), rgba(ACC, b))
    text_c(d, 110, 625, "–", FL("InterDisplay-Black.otf", 50), rgba(MUTED, b))
    xs = [270, 450, 630]
    for i, x in enumerate(xs):
        k = back_out((lt - 0.9 - 0.3 * i) / 0.45)
        if k <= 0:
            continue
        aa = clamp(k) * a
        d.line(p(x, 250, x, 650), fill=rgba(DARK, aa), width=int(6 * S))
        ph = (t * 1.5 + i / 3) % 1.0
        top_on = ph < 0.5
        d.rounded_rectangle(p(x - 70, 300, x + 70, 420), radius=18 * S, fill=rgba(PANEL, aa), outline=rgba(PH[i], aa), width=int(3 * S))
        d.rounded_rectangle(p(x - 70, 480, x + 70, 600), radius=18 * S, fill=rgba(PANEL, aa), outline=rgba(PH[i], aa), width=int(3 * S))
        switch(d, x - 10, 360, top_on, aa, PH[i])
        switch(d, x - 10, 540, not top_on, aa, PH[i])
        # output to motor phase
        d.line(p(x, 450, x + 90, 450), fill=rgba(PH[i], aa), width=int(6 * S))
        d.ellipse(p(x - 11, 439, x + 11, 461), fill=rgba(PH[i], aa))
    m = ease_out((lt - 2.2) / 0.5)
    text_c(d, 450, 700, "IGBT  или  SiC MOSFET", FL("InterDisplay-Black.otf", 40), rgba(WHITE, m))
    text_c(d, 450, 760, "одна пара на фазу мотора", FL("Inter-SemiBold.otf", 28), rgba(MUTED, m))

# ---------- scene 4: PWM pulses -> smooth sine ----------
def vis_iv_pwm(d, lt, t):
    a = ease_out(lt / 0.35)
    panel(d, 60, 60, 840, 820, a)
    # pulse counter
    k = ease_out((lt - 0.2) / 1.6)
    n = int(20000 * k)
    text_c(d, 450, 90, f"{n:,}".replace(",", " "), FL("InterDisplay-Black.otf", 96), rgba(ACC, a))
    text_c(d, 450, 205, "ПЕРЕКЛЮЧЕНИЙ В СЕКУНДУ (ДО)", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
    # PWM train whose duty follows a sine
    x0, x1, ytop, ybot = 110, 790, 290, 430
    cells = 34
    cw = (x1 - x0) / cells
    rv = ease_inout((lt - 0.6) / 1.4)
    for c in range(int(cells * rv)):
        duty = 0.5 + 0.45 * math.sin(2 * math.pi * 1.5 * (c + 0.5) / cells - t * 3)
        xa = x0 + c * cw
        d.rectangle(p(xa, ytop, xa + cw * duty, ybot), fill=rgba(ACC2, a * 0.9))
    d.line(p(x0, ybot, x1, ybot), fill=rgba(DARK, a), width=int(3 * S))
    text_c(d, 450, 445, "ИМПУЛЬСЫ (ШИМ)", FL("InterDisplay-Bold.otf", 28), rgba(ACC2, a * clamp(rv * 2)))
    # arrow down through a coil
    b = ease_out((lt - 2.2) / 0.5)
    for i in range(5):
        cx = 370 + i * 40
        arc(d, cx, 525, 22, 180, 360, rgba(WHITE, b), 6)
    text_c(d, 450, 545, "обмотка мотора сглаживает", FL("Inter-SemiBold.otf", 26), rgba(MUTED, b))
    c = ease_inout((lt - 2.8) / 1.4)
    if c > 0:
        wave_line(d, 110, 790, 700, 75, 1.5, -t * 3, ACC, 1, 10, reveal=c)
        d.line(p(110, 700, 790, 700), fill=rgba(DARK, c), width=int(3 * S))
    text_c(d, 450, 775, "ПЛАВНЫЙ ТОК", FL("InterDisplay-Bold.otf", 28), rgba(ACC, clamp(c * 2)))

# ---------- scene 5: frequency = speed, current = torque ----------
def vis_iv_control(d, lt, t):
    a = ease_out(lt / 0.35)
    dur = sdur("iv_control")
    half = dur * 0.48
    f = 1 + 2.0 * ease_inout(lt / half)
    amp = 55 + 50 * ease_inout((lt - half) / 1.2)
    panel(d, 60, 60, 840, 330, a)
    wave_line(d, 100, 800, 195, amp, f, -t * 4 * f, ACC, a, 9)
    # spinning motor speed tied to frequency
    ang = t * 3.5 * f
    motor(d, 260, 560, 150, ang, a)
    # left readout: frequency -> rpm
    fs = FL("InterDisplay-Black.otf", 46)
    text_c(d, 640, 400, "ЧАСТОТА", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
    text_c(d, 640, 440, f"→ ОБОРОТЫ ×{f:.1f}".replace(".", ","), fs, rgba(ACC, a))
    b = ease_out((lt - half) / 0.4)
    text_c(d, 640, 560, "ТОК", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, b))
    text_c(d, 640, 600, "→ МОМЕНТ", fs, rgba(ACC2, b))
    # torque bar
    tq = clamp((amp - 55) / 50)
    d.rounded_rectangle(p(480, 690, 800, 730), radius=20 * S, fill=rgba(DARK, b))
    if tq > 0.02:
        d.rounded_rectangle(p(480, 690, 480 + 320 * (0.25 + 0.75 * tq), 730), radius=20 * S, fill=rgba(ACC2, b))
    else:
        d.rounded_rectangle(p(480, 690, 560, 730), radius=20 * S, fill=rgba(ACC2, b))

# ---------- scene 6: regen, energy flows back ----------
def vis_iv_regen(d, lt, t):
    a = ease_out(lt / 0.35)
    battery(d, 190, 300, 230, 120, a, fill=0.4 + 0.4 * ease_inout(lt / 4.0))
    text_c(d, 190, 390, "БАТАРЕЯ", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
    chip(d, 450, 300, 170, 110, a, label="ИНВ", glow=0.7)
    motor(d, 720, 300, 100, -t * 3, a)
    text_c(d, 720, 420, "ГЕНЕРАТОР", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
    # energy flows motor -> inverter -> battery (right to left)
    k = ease_out((lt - 0.5) / 0.5)
    d.line(p(615, 300, 540, 300), fill=rgba(DARK, a), width=int(14 * S))
    d.line(p(365, 300, 320, 300), fill=rgba(DARK, a), width=int(14 * S))
    flow_dots(d, [(615, 300), (540, 300)], -t, ACC2, k, speed=2.4, n=3, r=9)
    flow_dots(d, [(365, 300), (320, 300)], -t, ACC, k, speed=2.4, n=2, r=9)
    # big reverse arrow
    b = ease_out((lt - 0.9) / 0.5)
    poly(d, [(700, 520), (260, 520), (260, 490), (180, 550), (260, 610), (260, 580), (700, 580)], rgba(ACC, b * 0.9))
    text_c(d, 470, 532, "ПЕРЕМ. → ПОСТ.", FL("InterDisplay-Black.otf", 34), rgba(BG, b))
    text_c(d, 450, 680, "РЕКУПЕРАЦИЯ", FL("InterDisplay-Black.otf", 60), rgba(WHITE, ease_out((lt - 1.5) / 0.4)))
    text_c(d, 450, 760, "те же ключи, обратное направление", FL("Inter-SemiBold.otf", 28), rgba(MUTED, ease_out((lt - 1.9) / 0.4)))

# ---------- outro ----------
def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "ПОДПИШИСЬ НА КАНАЛ", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

def vis_iv_outro(d, lt, t):
    dur = sdur("iv_outro")
    cut = dur * 0.5
    if lt < cut:
        a = 1 - ease_inout((lt - cut + 0.3) / 0.3)
        # pedal -> chip -> motor
        poly(d, [(110, 520), (230, 520), (260, 300), (170, 300)], rgba(WHITE, a))
        text_c(d, 190, 560, "ПЕДАЛЬ", FL("InterDisplay-Bold.otf", 28), rgba(MUTED, a))
        chip(d, 450, 410, 200, 120, a, label="ЧИП", glow=0.5 + 0.5 * math.sin(t * 5))
        motor(d, 720, 410, 100, t * 6, a)
        flow_dots(d, [(260, 410), (345, 410)], t, ACC, a, speed=2.5, n=3, r=8)
        flow_dots(d, [(555, 410), (615, 410)], t, ACC, a, speed=2.5, n=2, r=8)
        text_c(d, 450, 640, "ЗАПРОС К ЧИПУ", FL("InterDisplay-Black.otf", 60), rgba(ACC, a * ease_out((lt - 0.4) / 0.4)))
    else:
        end_card(d, lt, cut)

VIS.update({"iv_hook": vis_iv_hook, "iv_dcac": vis_iv_dcac, "iv_switches": vis_iv_switches,
            "iv_pwm": vis_iv_pwm, "iv_control": vis_iv_control, "iv_regen": vis_iv_regen, "iv_outro": vis_iv_outro})
