# Episode visuals: Hidden feature — the 12-volt battery inside every EV.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
RED = (255, 84, 84)
BLUE = (80, 170, 255)
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

def particles(d, path, t, col, n=10, speed=0.6, a=1.0, size=9):
    segs = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    lens = [math.hypot(b[0] - a_[0], b[1] - a_[1]) for a_, b in segs]
    tot = sum(lens)
    for i in range(n):
        u = ((t * speed + i / n) % 1.0) * tot
        for (p0, p1), ln in zip(segs, lens):
            if u <= ln:
                f = u / ln
                x = p0[0] + (p1[0] - p0[0]) * f; y = p0[1] + (p1[1] - p0[1]) * f
                d.ellipse(p(x - size * 1.8, y - size * 1.8, x + size * 1.8, y + size * 1.8), fill=rgba(col, 0.18 * a))
                d.ellipse(p(x - size, y - size, x + size, y + size), fill=rgba(col, a))
                break
            u -= ln

def wire(d, pts, col, w=8):
    d.line([v * S for xy in pts for v in xy], fill=col, width=int(w * S), joint="curve")

def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

def small_batt(d, cx, cy, sc, a=1.0, level=1.0, col=ACC2, label="12V"):
    """Classic 12 V box battery with two terminals."""
    w, h = 150 * sc, 100 * sc
    x0, y0 = cx - w / 2, cy - h / 2
    for tx in (x0 + w * 0.22, x0 + w * 0.78):
        d.rounded_rectangle(p(tx - 12 * sc, y0 - 18 * sc, tx + 12 * sc, y0 + 4), radius=int(4 * S), fill=rgba(MUTED, a))
    d.rounded_rectangle(p(x0, y0, x0 + w, y0 + h), radius=int(14 * S * sc), fill=rgba(col, a))
    if level < 0.999:
        # empty part darkened
        d.rounded_rectangle(p(x0 + 6, y0 + 6, x0 + w - 6, y0 + 6 + (h - 12) * (1 - level)), radius=int(10 * S * sc), fill=rgba(PANEL, 0.85 * a))
    text_c(d, cx, cy - 24 * sc, label, FL("InterDisplay-Black.otf", max(8, int(40 * sc))), rgba(BG if level > 0.5 else WHITE, a))

def hv_pack(d, x0, y0, x1, y1, a=1.0, level=1.0, label="HIGH-VOLTAGE PACK", col=ACC):
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=int(18 * S), fill=rgba(PANEL, a), outline=rgba(col, a), width=int(5 * S))
    n = 8; gw = (x1 - x0 - 30) / n
    for i in range(n):
        cx0 = x0 + 15 + i * gw
        on = (i + 0.5) / n <= level
        d.rounded_rectangle(p(cx0 + 4, y0 + 14, cx0 + gw - 4, y1 - 14), radius=int(6 * S), fill=rgba(col if on else DARK, (0.9 if on else 0.6) * a))
    if label:
        text_c(d, (x0 + x1) / 2, y1 + 26, label, FL("InterDisplay-Bold.otf", 26), rgba(MUTED, a))

def switch(d, x, y, closed, col, a=1.0, length=90):
    """Contactor: two contacts and a blade that pivots closed (closed 0..1)."""
    d.ellipse(p(x - 12, y - 12, x + 12, y + 12), fill=rgba(WHITE, a))
    d.ellipse(p(x + length - 12, y - 12, x + length + 12, y + 12), fill=rgba(WHITE, a))
    ang = math.radians(-38 * (1 - closed))
    d.line(p(x, y, x + math.cos(ang) * length, y + math.sin(ang) * length), fill=rgba(col, a), width=int(10 * S))

def icon_chip(d, cx, cy, c):
    d.rounded_rectangle(p(cx - 34, cy - 34, cx + 34, cy + 34), radius=8 * S, fill=c)
    for i in range(3):
        o = -20 + i * 20
        for dx, dy in ((o, -46), (o, 34), (-46, o), (34, o)):
            d.rectangle(p(cx + dx, cy + dy, cx + dx + 12 if dy in (-46, 34) else cx + dx + 12, cy + dy + 12), fill=c)

def icon_lock(d, cx, cy, c, bg=PANEL, open_=0.0):
    d.arc(p(cx - 26, cy - 58 - 14 * open_, cx + 26, cy - 6 - 14 * open_), 180, 360, fill=c, width=10 * S)
    d.line(p(cx - 26, cy - 32 - 14 * open_, cx - 26, cy - 10), fill=c, width=10 * S)
    if open_ < 0.5:
        d.line(p(cx + 26, cy - 32, cx + 26, cy - 10), fill=c, width=10 * S)
    d.rounded_rectangle(p(cx - 40, cy - 14, cx + 40, cy + 44), radius=10 * S, fill=c)
    d.ellipse(p(cx - 7, cy + 4, cx + 7, cy + 18), fill=bg)

def icon_light(d, cx, cy, c):
    d.pieslice(p(cx - 40, cy - 34, cx + 20, cy + 34), 90, 270, fill=c)
    d.rectangle(p(cx - 10, cy - 34, cx + 4, cy + 34), fill=c)
    for i in range(3):
        yy = cy - 22 + i * 22
        d.line(p(cx + 18, yy, cx + 50, yy), fill=c, width=7 * S)

def icon_screen(d, cx, cy, c):
    d.rounded_rectangle(p(cx - 48, cy - 34, cx + 48, cy + 30), radius=8 * S, outline=c, width=7 * S)
    d.line(p(cx - 20, cy + 44, cx + 20, cy + 44), fill=c, width=7 * S)
    d.line(p(cx - 30, cy + 8, cx - 10, cy - 10, cx + 8, cy + 2, cx + 30, cy - 18), fill=c, width=6 * S)

# ---------- 1. car cutaway: huge pack in the floor + a small 12 V box ----------
def vis_v12_hook(d, lt, t):
    a = ease_out(lt / 0.4)
    d.line(p(30, 560, 870, 560), fill=rgba(DARK, 1), width=6 * S)
    car_side(d, 450, 470, 1.55, (60, 70, 86), a)
    # big pack slides into the floor
    k = ease_out((lt - 0.4) / 0.8)
    hv_pack(d, 290 - 200 * (1 - k), 470, 610 - 200 * (1 - k), 520, a * clamp(k), 1.0, label=None)
    text_c(d, 450, 610, "MAIN BATTERY", FL("InterDisplay-Black.otf", 40), rgba(ACC, clamp(k)))
    # small 12V pops under the hood
    k2 = back_out((lt - 1.9) / 0.5)
    if k2 > 0.01:
        small_batt(d, 715, 400, 0.55 * k2, clamp(k2))
        pulse = 0.5 + 0.5 * math.sin(t * 6)
        d.ellipse(p(640, 330, 790, 470), outline=rgba(ACC2, 0.6 * pulse * clamp(k2)), width=5 * S)
        d.line(p(760, 340, 800, 230), fill=rgba(ACC2, clamp(k2)), width=4 * S)
        text_c(d, 790, 170, "AND THIS?", FL("InterDisplay-Black.otf", 40), rgba(ACC2, clamp(k2)))
    a3 = ease_out((lt - 3.2) / 0.4)
    text_c(d, 450, 700, "?", FL("InterDisplay-Black.otf", 120), rgba(WHITE, a3))

# ---------- 2. 12 V wakes the car: wires to chip, lock, light, screen ----------
def vis_v12_wake(d, lt, t):
    k = back_out(lt / 0.5)
    cx, cy = 450, 430
    small_batt(d, cx, cy, 1.25 * max(k, 0.01), clamp(k))
    text_c(d, cx, cy + 90, "12 VOLTS", FL("InterDisplay-Black.otf", 40), rgba(WHITE, clamp(k)))
    items = [(170, 200, icon_chip, "COMPUTERS"), (730, 200, icon_lock, "LOCKS"),
             (170, 690, icon_light, "LIGHTS"), (730, 690, icon_screen, "SCREENS")]
    for i, (ix, iy, fn, lab) in enumerate(items):
        st = 0.9 + i * 0.75
        on = ease_out((lt - st) / 0.4)
        ka = ease_out((lt - 0.5) / 0.4)
        path = [(cx + (60 if ix > cx else -60), cy + (-30 if iy < cy else 30)), (ix, cy + (-30 if iy < cy else 30)), (ix, iy + (70 if iy < cy else -70))]
        wire(d, path, rgba(ACC if on > 0.5 else DARK, ka), 6)
        if on > 0.5:
            particles(d, path, t, ACC, n=4, speed=0.8, a=on, size=6)
        col = ACC if on > 0.5 else MUTED
        if on > 0.05:
            d.ellipse(p(ix - 78, iy - 78, ix + 78, iy + 78), fill=rgba(ACC, 0.12 * on))
        fn(d, ix, iy, rgba(col, ka))
        text_c(d, ix, iy + (-120 if iy < cy else 70), lab, FL("InterDisplay-Bold.otf", 28), rgba(col, ka))

# ---------- 3. contactors close: 12 V coil pulls switches, HV flows ----------
def contactor_diagram(d, lt, t, closed, cut_label=None, a=1.0, flow=True):
    # HV pack left (vertical), motor/inverter right, two contactor switches on +/- lines
    hv_pack(d, 70, 300, 290, 520, a, 1.0, label="HIGH-VOLTAGE PACK")
    # inverter + motor block
    d.rounded_rectangle(p(640, 280, 840, 540), radius=24 * S, fill=rgba(PANEL, a), outline=rgba(WHITE, a), width=5 * S)
    d.ellipse(p(690, 360, 790, 460), outline=rgba(WHITE, a), width=6 * S)
    ang = t * 8 * closed
    for k_ in range(3):
        aa = ang + k_ * 2.094
        d.line(p(740, 410, 740 + math.cos(aa) * 40, 410 + math.sin(aa) * 40), fill=rgba(ACC if closed > 0.9 else MUTED, a), width=6 * S)
    text_c(d, 740, 556, "MOTOR", FL("InterDisplay-Bold.otf", 26), rgba(MUTED, a))
    # lines
    for yy in (330, 490):
        wire(d, [(290, yy), (405, yy)], rgba(WHITE, a), 6)
        wire(d, [(515, yy), (640, yy)], rgba(WHITE, a), 6)
        switch(d, 415, yy, closed, ACC if closed > 0.95 else ACC2, a)
    text_c(d, 460, 380, "CONTACTORS", FL("InterDisplay-Black.otf", 32), rgba(ACC2 if closed < 0.95 else ACC, a))
    if closed > 0.95 and flow:
        particles(d, [(290, 330), (640, 330)], t, ACC, n=6, speed=0.9, a=a, size=8)
        particles(d, [(640, 490), (290, 490)], t, ACC, n=6, speed=0.9, a=a, size=8)

def vis_v12_contactor(d, lt, t):
    a = ease_out(lt / 0.4)
    closed = ease_inout((lt - 2.0) / 0.6)
    contactor_diagram(d, lt, t, closed, a=a)
    # 12V battery below drives the coil
    small_batt(d, 460, 720, 0.8, a)
    ka = ease_out((lt - 1.2) / 0.4)
    wire(d, [(460, 670), (460, 530)], rgba(ACC2, ka), 5)
    if ka > 0.5:
        particles(d, [(460, 670), (460, 530)], t, ACC2, n=3, speed=1.2, a=ka, size=6)
    d.text((500 * S, 580 * S), "SIGNAL", font=FL("InterDisplay-Bold.otf", 24), fill=rgba(ACC2, ka))
    a2 = ease_out((lt - 2.8) / 0.4)
    text_c(d, 450, 120, "CLICK — CONNECTED", FL("InterDisplay-Black.otf", 52), rgba(ACC, a2))

# ---------- 4. car off / crash: contactors open, pack isolated ----------
def vis_v12_open(d, lt, t):
    dur = sdur("v12_open")
    a = ease_out(lt / 0.3)
    closed = 1 - ease_inout((lt - 0.5) / 0.4)
    contactor_diagram(d, lt, t, closed, a=a)
    # status chips: OFF then CRASH
    k1 = ease_out((lt - 0.3) / 0.3)
    d.rounded_rectangle(p(140, 100, 420, 180), radius=40 * S, fill=rgba(PANEL, k1), outline=rgba(WHITE, k1), width=4 * S)
    text_c(d, 280, 116, "CAR OFF", FL("InterDisplay-Black.otf", 40), rgba(WHITE, k1))
    k2 = ease_out((lt - 1.6) / 0.3)
    shake = math.sin(t * 50) * 6 * (1 - ease_out((lt - 1.6) / 0.6)) if lt > 1.6 else 0
    d.rounded_rectangle(p(480 + shake, 100, 760 + shake, 180), radius=40 * S, fill=rgba(RED, k2))
    text_c(d, 620 + shake, 116, "CRASH", FL("InterDisplay-Black.otf", 40), rgba(BG, k2))
    # shield around pack
    k3 = ease_out((lt - 1.0) / 0.5)
    d.rounded_rectangle(p(52, 284, 308, 536), radius=30 * S, outline=rgba(ACC2, k3 * (0.6 + 0.4 * math.sin(t * 5))), width=6 * S)
    text_c(d, 450, 690, "PACK CUT OFF", FL("InterDisplay-Black.otf", 60), rgba(ACC2, ease_out((lt - 1.2) / 0.4)))

# ---------- 5. DC-DC converter instead of an alternator ----------
def vis_v12_dcdc(d, lt, t):
    a = ease_out(lt / 0.4)
    # crossed-out alternator
    ka = ease_out(lt / 0.4)
    d.ellipse(p(370, 40, 530, 200), outline=rgba(MUTED, ka), width=8 * S)
    for k_ in range(6):
        aa = k_ * 1.047 + t * 0.5
        d.line(p(450 + math.cos(aa) * 30, 120 + math.sin(aa) * 30, 450 + math.cos(aa) * 70, 120 + math.sin(aa) * 70), fill=rgba(MUTED, ka), width=6 * S)
    xk = ease_out((lt - 0.6) / 0.3)
    if xk > 0:
        d.line(p(360, 30, 360 + 180 * xk, 30 + 180 * xk), fill=rgba(RED, 1), width=12 * S)
    text_c(d, 450, 215, "NO ALTERNATOR", FL("InterDisplay-Bold.otf", 30), rgba(RED, xk))
    # pack -> converter -> 12V
    k = ease_out((lt - 1.4) / 0.5)
    hv_pack(d, 40, 380, 260, 520, k, 1.0, label="HIGH VOLTAGE")
    d.rounded_rectangle(p(340, 360, 560, 540), radius=24 * S, fill=rgba(PANEL, k), outline=rgba(BLUE, k), width=6 * S)
    text_c(d, 450, 400, "DC→DC", FL("InterDisplay-Black.otf", 46), rgba(BLUE, k))
    text_c(d, 450, 470, "CONVERTER", FL("InterDisplay-Bold.otf", 26), rgba(MUTED, k))
    lvl = 0.25 + 0.75 * ease_inout((lt - 2.6) / 3.0)
    small_batt(d, 730, 460, 1.0, k, level=lvl)
    flow = ease_out((lt - 2.2) / 0.4)
    wire(d, [(260, 450), (340, 450)], rgba(ACC, k), 10)
    wire(d, [(560, 450), (655, 450)], rgba(ACC2, k), 5)
    if flow > 0.3:
        particles(d, [(260, 450), (340, 450)], t, ACC, n=3, speed=1.4, a=flow, size=11)
        particles(d, [(560, 450), (655, 450)], t, ACC2, n=3, speed=1.0, a=flow, size=6)
    # step-down bar chart
    k2 = ease_out((lt - 3.0) / 0.6)
    d.rounded_rectangle(p(110, 780 - 160 * k2, 190, 780), radius=8 * S, fill=rgba(ACC, k2))
    d.rounded_rectangle(p(700, 780 - 26 * k2, 780, 780), radius=6 * S, fill=rgba(ACC2, k2))
    wire(d, [(200, 700), (690, 765)], rgba(MUTED, 0.6 * k2), 3)
    text_c(d, 150, 800, "HUNDREDS OF V", FL("InterDisplay-Bold.otf", 22), rgba(ACC, k2))
    text_c(d, 740, 800, "12 V", FL("InterDisplay-Bold.otf", 24), rgba(ACC2, k2))
    text_c(d, 450, 690, "STEP DOWN", FL("InterDisplay-Black.otf", 40), rgba(WHITE, k2))

# ---------- 6. dead 12 V: full main battery but locked out ----------
def vis_v12_dead(d, lt, t):
    a = ease_out(lt / 0.4)
    hv_pack(d, 80, 120, 520, 220, a, 1.0, label=None)
    text_c(d, 300, 240, "MAIN: 100%", FL("InterDisplay-Black.otf", 40), rgba(ACC, a))
    lvl = 1 - ease_inout((lt - 0.4) / 1.4)
    small_batt(d, 710, 170, 0.9, a, level=max(lvl, 0.0), col=ACC2 if lvl > 0.2 else RED)
    text_c(d, 710, 250, f"12V: {int(lvl * 100)}%", FL("InterDisplay-Black.otf", 34), rgba(RED if lvl < 0.2 else ACC2, a))
    k = ease_out((lt - 1.8) / 0.4)
    # locked door + dead power button
    icon_lock(d, 290, 470, rgba(RED, k), bg=BG)
    text_c(d, 290, 550, "WON'T UNLOCK", FL("InterDisplay-Bold.otf", 30), rgba(RED, k))
    press = 0.5 + 0.5 * math.sin(t * 7)
    r = 62 - 4 * press * k
    d.ellipse(p(610 - r, 480 - r, 610 + r, 480 + r), outline=rgba(RED, k), width=8 * S)
    d.arc(p(580, 450, 640, 510), -60, 240, fill=rgba(RED, k), width=7 * S)
    d.line(p(610, 438, 610, 478), fill=rgba(RED, k), width=7 * S)
    text_c(d, 610, 560, "WON'T START", FL("InterDisplay-Bold.otf", 30), rgba(RED, k))
    k3 = ease_out((lt - 3.0) / 0.4)
    glow_rect(d, 160, 690, 740, 790, 26, ACC2, k3)
    text_c(d, 450, 708, "CHECK THE 12 V FIRST", FL("InterDisplay-Black.otf", 44), rgba(BG, k3))

# ---------- 7. outro: 12 V -> 48 V ----------
def vis_v12_outro(d, lt, t):
    dur = sdur("v12_outro")
    cut = dur * 0.5
    if lt < cut:
        k = back_out(lt / 0.5)
        m = ease_inout((lt - 1.0) / 0.8)
        v = int(round(12 + 36 * m))
        small_batt(d, 450, 330, 1.6 * max(k, 0.01), clamp(k), col=ACC2 if m < 0.5 else ACC, label=f"{v}V")
        text_c(d, 450, 520, "12V  →  48V", FL("InterDisplay-Black.otf", 64), rgba(WHITE, ease_out((lt - 0.4) / 0.4)))
        text_c(d, 450, 640, "THE FUTURE?", FL("InterDisplay-Black.otf", 54), rgba(ACC, ease_out((lt - 1.8) / 0.4)))
    else:
        end_card(d, lt, cut)

VIS.update({"v12_hook": vis_v12_hook, "v12_wake": vis_v12_wake, "v12_contactor": vis_v12_contactor, "v12_open": vis_v12_open,
            "v12_dcdc": vis_v12_dcdc, "v12_dead": vis_v12_dead, "v12_outro": vis_v12_outro})
