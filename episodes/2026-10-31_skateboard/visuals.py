# Episode visuals: How it works — the EV skateboard platform.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
CELL = (52, 62, 76)
BLUE = (90, 170, 255)

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

def label(d, x, y, s, col, a, size=28, bold="Inter-SemiBold.otf"):
    text_c(d, x, y, s, FL(bold, size), rgba(col, a))

def body_shell(d, x, y, sc, a, col=WHITE, kind=0):
    """Car body silhouette (side) with no wheels; kind 0 sedan, 1 SUV, 2 van."""
    if kind == 0:
        pts = [(-230, 30), (-230, -10), (-200, -40), (-110, -50), (-60, -110), (90, -112), (160, -55), (225, -40), (238, 0), (238, 30)]
        gl = [[(-45, -95), (10, -97), (10, -52), (-90, -52)], [(25, -97), (82, -97), (130, -52), (25, -52)]]
    elif kind == 1:
        pts = [(-235, 30), (-235, -60), (-215, -135), (-60, -140), (120, -135), (180, -70), (232, -55), (240, 0), (240, 30)]
        gl = [[(-195, -122), (-70, -124), (-70, -78), (-200, -78)], [(-55, -124), (110, -122), (160, -78), (-55, -78)]]
    else:
        pts = [(-240, 30), (-240, -160), (-225, -175), (140, -175), (200, -95), (240, -70), (245, 30)]
        gl = [[(-215, -155), (-40, -155), (-40, -100), (-215, -100)], [(-20, -155), (130, -155), (180, -100), (-20, -100)]]
    poly(d, [(x + px * sc, y + py * sc) for px, py in pts], rgba(col, a))
    for g in gl:
        poly(d, [(x + px * sc, y + py * sc) for px, py in g], rgba(BG, a))

def wheel(d, cx, cy, r, ang, a):
    tire(d, cx, cy, r, ang, (60, 68, 80), a)

def slab(d, x0, y0, x1, y1, a, cells=1.0, glow=0.0, t=0.0):
    """Side/top battery slab with cells filling in (cells: 0..1)."""
    d.rounded_rectangle(p(x0 + 5, y0 + 8, x1 + 5, y1 + 8), radius=10 * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=10 * S, fill=rgba(STEEL, a))
    n = 12
    cw = (x1 - x0 - 16) / n
    for i in range(n):
        k = clamp(cells * n - i)
        if k <= 0:
            continue
        cx0 = x0 + 8 + i * cw
        d.rounded_rectangle(p(cx0 + 2, y0 + 6, cx0 + cw - 2, y1 - 6), radius=4 * S, fill=rgba(ACC, a * k * (0.75 + 0.25 * math.sin(t * 4 + i * 0.6))))
    if glow > 0:
        d.rounded_rectangle(p(x0 - 6, y0 - 6, x1 + 6, y1 + 6), radius=14 * S, outline=rgba(ACC, glow * a), width=int(4 * S))

def motor(d, cx, cy, r, a, t):
    d.ellipse(p(cx - r, cy - r, cx + r, cy + r), fill=rgba(ACC2, a))
    d.ellipse(p(cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55), fill=rgba(BG, a))
    ang = t * 6
    for k in range(3):
        aa = ang + k * 2.094
        d.line(p(cx, cy, cx + math.cos(aa) * r * 0.5, cy + math.sin(aa) * r * 0.5), fill=rgba(ACC2, a), width=int(5 * S))

# ---------- scene 1: body lifts off, skateboard revealed ----------
def vis_sk_hook(d, lt, t):
    a = ease_out(lt / 0.35)
    gy = 520
    lift = ease_inout((lt - 0.9) / 1.2) * 260
    fade = 1 - 0.55 * ease_inout((lt - 0.9) / 1.2)
    # skateboard underneath
    slab(d, 245, gy - 22, 655, gy + 18, a, cells=ease_out((lt - 1.2) / 1.4), glow=ease_out((lt - 2.4) / 0.5) * (0.6 + 0.4 * math.sin(t * 5)), t=t)
    for wx in (290, 610):
        wheel(d, wx, gy + 20, 58, t * 3, a)
    # body lifting
    body_shell(d, 450, gy - 20 - lift, 1.15, a * fade, WHITE, 0)
    if lift > 20:
        for x in (330, 450, 570):
            yy = gy - 60 - lift * 0.45
            d.line(p(x, yy + 40, x, yy - 10), fill=rgba(ACC, a * 0.8), width=int(6 * S))
            poly(d, [(x - 16, yy - 4), (x + 16, yy - 4), (x, yy - 26)], rgba(ACC, a * 0.8))
    k = back_out((lt - 2.6) / 0.5)
    if k > 0:
        text_c(d, 450, 650, "SKATEBOARD", FL("InterDisplay-Black.otf", max(1, int(78 * k))), rgba(ACC, clamp(k)))
        text_c(d, 450, 750, "PLATFORM", FL("InterDisplay-Black.otf", max(1, int(78 * k))), rgba(WHITE, clamp(k)))

# ---------- scene 2: top view, motors, bodies swapping ----------
def vis_sk_board(d, lt, t):
    a = ease_out(lt / 0.35)
    # top view of the platform
    x0, x1, y0, y1 = 190, 710, 150, 450
    # axles + wheels
    for wy in (y0 + 10, y1 - 10):
        pass
    for wx in (150, 750):
        d.line(p(wx, 170, wx, 430), fill=rgba(STEEL, a), width=int(14 * S))
        for wy in (150, 450):
            d.rounded_rectangle(p(wx - 34, wy - 58, wx + 34, wy + 58), radius=14 * S, fill=rgba((60, 68, 80), a))
            d.rounded_rectangle(p(wx - 34, wy - 58, wx + 34, wy + 58), radius=14 * S, outline=rgba((18, 22, 30), a), width=int(4 * S))
    # battery grid fills in
    d.rounded_rectangle(p(x0 + 6, y0 + 10, x1 + 6, y1 + 10), radius=24 * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=24 * S, fill=rgba(STEEL, a))
    cols, rows = 8, 4
    cw, ch = (x1 - x0 - 30) / cols, (y1 - y0 - 30) / rows
    fill = ease_inout((lt - 0.3) / 1.4)
    for r in range(rows):
        for c in range(cols):
            k = clamp(fill * cols * rows - (c * rows + r))
            if k <= 0:
                continue
            cx0, cy0 = x0 + 15 + c * cw, y0 + 15 + r * ch
            d.rounded_rectangle(p(cx0 + 4, cy0 + 4, cx0 + cw - 4, cy0 + ch - 4), radius=8 * S,
                                fill=rgba(ACC, a * k * (0.7 + 0.3 * math.sin(t * 3 + c * 0.5 + r))))
    label(d, 450, 465, "BATTERY · between the axles", WHITE, a * ease_out((lt - 1.2) / 0.4), 30, "InterDisplay-Bold.otf")
    # motors at axles
    m = back_out((lt - 1.8) / 0.5)
    if m > 0:
        for wx in (150, 750):
            motor(d, wx, 300, 48 * m, clamp(m), t)
        label(d, 150, 368, "MOTOR", ACC2, clamp(m), 26, "InterDisplay-Bold.otf")
        label(d, 750, 368, "MOTOR", ACC2, clamp(m), 26, "InterDisplay-Bold.otf")
    # bodies swapping on side view below
    k2 = ease_out((lt - 2.6) / 0.5)
    if k2 > 0:
        gy = 760
        slab(d, 290, gy - 16, 610, gy + 14, k2, 1.0, t=t)
        for wx in (325, 575):
            wheel(d, wx, gy + 18, 44, t * 3, k2)
        cyc = max(0, lt - 2.9)
        kind = int(cyc / 1.0) % 3
        ph = (cyc % 1.0)
        drop = (1 - ease_out(ph / 0.35)) * 90
        ba = k2 * (1 - ease_inout((ph - 0.8) / 0.2))
        body_shell(d, 450, gy - 16 - drop, 0.82, ba, WHITE, kind)
        label(d, 450, 545 - 0, ["SEDAN", "SUV", "VAN"][kind], MUTED, ba, 30, "InterDisplay-Bold.otf")

# ---------- scene 3: weight counter + center of gravity drop ----------
def vis_sk_weight(d, lt, t):
    a = ease_out(lt / 0.35)
    k = ease_out((lt - 0.2) / 1.4)
    text_c(d, 450, 40, f"≈{int(1000 * k):,} lb", FL("InterDisplay-Black.otf", 104), rgba(ACC, a))
    label(d, 450, 170, f"≈{int(454 * k)} kg · typical battery pack", MUTED, a, 30)
    gy = 600
    car_side(d, 450, gy, 1.3, WHITE, a)
    slab(d, 290, gy + 4, 610, gy + 34, a, cells=ease_out((lt - 0.8) / 1.0), t=t)
    # center of gravity marker drops
    drop = ease_inout((lt - 1.8) / 1.4)
    cy = gy - 95 + drop * 85
    r = 26
    d.ellipse(p(450 - r - 6, cy - r - 6, 450 + r + 6, cy + r + 6), fill=rgba(BG, a))
    for q in range(4):
        col = ACC2 if q % 2 == 0 else WHITE
        d.pieslice(p(450 - r, cy - r, 450 + r, cy + r), q * 90, q * 90 + 90, fill=rgba(col, a))
    # ghost of old position
    if drop > 0.05:
        oy = gy - 95
        d.ellipse(p(450 - r, oy - r, 450 + r, oy + r), outline=rgba(MUTED, a * 0.8), width=int(3 * S))
        d.line(p(520, oy, 520, cy - 4), fill=rgba(ACC2, a * drop), width=int(5 * S))
        poly(d, [(508, cy - 18), (532, cy - 18), (520, cy)], rgba(ACC2, a * drop))
    label(d, 450, 760, "CENTER OF GRAVITY ↓", ACC2, ease_out((lt - 2.6) / 0.4), 44, "InterDisplay-Black.otf")

# ---------- scene 4: tilt test + rollover risk gauge ----------
def vis_sk_rollover(d, lt, t):
    a = ease_out(lt / 0.35)
    # front view of an SUV being pushed: tilts and settles back
    cx, gy = 450, 420
    push = math.sin(clamp(lt / 2.4) * math.pi) * 0.22 * (1 - 0.4 * clamp((lt - 1.2) / 1.2))
    piv = (cx + 150, gy)  # right wheel contact
    def rot(px, py):
        dx, dy = px - piv[0], py - piv[1]
        c, s_ = math.cos(-push), math.sin(-push)
        return (piv[0] + dx * c - dy * s_, piv[1] + dx * s_ + dy * c)
    d.line(p(110, gy + 4, 790, gy + 4), fill=rgba(DARK, a), width=int(6 * S))
    bodyp = [(cx - 175, gy - 40), (cx - 175, gy - 160), (cx - 140, gy - 250), (cx + 140, gy - 250), (cx + 175, gy - 160), (cx + 175, gy - 40)]
    poly(d, [rot(*q) for q in bodyp], rgba(WHITE, a))
    poly(d, [rot(*q) for q in [(cx - 125, gy - 235), (cx + 125, gy - 235), (cx + 150, gy - 170), (cx - 150, gy - 170)]], rgba(BG, a))
    poly(d, [rot(*q) for q in [(cx - 160, gy - 70), (cx + 160, gy - 70), (cx + 160, gy - 35), (cx - 160, gy - 35)]], rgba(ACC, a))
    for wx in (cx - 150, cx + 150):
        q0 = rot(wx - 28, gy - 70); q1 = rot(wx + 28, gy - 70); q2 = rot(wx + 28, gy); q3 = rot(wx - 28, gy)
        poly(d, [q0, q1, q2, q3], rgba((60, 68, 80), a))
    # CG marker low
    cgx, cgy = rot(cx, gy - 70)
    d.ellipse(p(cgx - 16, cgy - 16, cgx + 16, cgy + 16), fill=rgba(ACC2, a))
    # push arrow
    pa = clamp(1 - lt / 2.4) * a
    if pa > 0:
        d.line(p(150, gy - 150, 240, gy - 150), fill=rgba(MUTED, pa), width=int(8 * S))
        poly(d, [(240, gy - 170), (240, gy - 130), (272, gy - 150)], rgba(MUTED, pa))
    # gauge bar
    g = ease_out((lt - 1.6) / 1.6)
    panel(d, 90, 500, 810, 820, ease_out((lt - 1.3) / 0.4))
    pa2 = ease_out((lt - 1.3) / 0.4)
    label(d, 450, 520, "NHTSA ROLLOVER RISK · TESLA MODEL Y", MUTED, pa2, 30, "InterDisplay-Bold.otf")
    text_c(d, 450, 565, f"{7.9 * g:.1f}%", FL("InterDisplay-Black.otf", 110), rgba(ACC, pa2))
    bx0, bx1 = 140, 760
    d.rounded_rectangle(p(bx0, 710, bx1, 740), radius=15 * S, fill=rgba(DARK, pa2))
    d.rounded_rectangle(p(bx0, 710, bx0 + max(30, (bx1 - bx0) * 0.079 * g), 740), radius=15 * S, fill=rgba(ACC, pa2))
    label(d, 450, 760, "lowest SUV score at the time (2020 test)", WHITE, ease_out((lt - 3.0) / 0.4), 26)

# ---------- scene 5: top-down cabin, engine & tunnel vanish, frunk ----------
def vis_sk_space(d, lt, t):
    a = ease_out(lt / 0.35)
    # car outline top view, front at top
    x0, x1, y0, y1 = 250, 650, 90, 800
    d.rounded_rectangle(p(x0 + 6, y0 + 10, x1 + 6, y1 + 10), radius=110 * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(x0, y0, x1, y1), radius=110 * S, fill=rgba(PANEL, a), outline=rgba(WHITE, a), width=int(5 * S))
    gone = ease_inout((lt - 1.2) / 0.9)
    # engine block
    ea = a * (1 - gone)
    if ea > 0.01:
        d.rounded_rectangle(p(330, 130, 570, 280), radius=18 * S, fill=rgba(ACC2, ea))
        label(d, 450, 185, "ENGINE", BG, ea, 34, "InterDisplay-Black.otf")
        d.rounded_rectangle(p(425, 280, 475, 740), radius=12 * S, fill=rgba(ACC2, ea * 0.85))
        label(d, 450 + 0, 750, "TUNNEL", ACC2, ea, 24, "InterDisplay-Bold.otf")
    # flat floor glow
    ff = ease_out((lt - 1.9) / 0.8)
    if ff > 0:
        d.rounded_rectangle(p(290, 320, 610, 740), radius=30 * S, outline=rgba(ACC, ff * a * (0.6 + 0.4 * math.sin(t * 4))), width=int(5 * S))
        label(d, 450, 760, "FLAT FLOOR", ACC, ff * a, 30, "InterDisplay-Black.otf")
    # seats
    for sx, sy in [(340, 360), (560, 360), (340, 560), (450, 560), (560, 560)]:
        sw = 40 if sy == 560 else 50
        d.rounded_rectangle(p(sx - sw, sy, sx + sw, sy + 110), radius=16 * S, fill=rgba(STEEL, a))
    # frunk
    fk = back_out((lt - 2.4) / 0.5)
    if fk > 0:
        d.rounded_rectangle(p(320, 120, 580, 270), radius=22 * S, fill=rgba(ACC, clamp(fk) * 0.18), outline=rgba(ACC, clamp(fk)), width=int(5 * S))
        text_c(d, 450, 165, "FRUNK", FL("InterDisplay-Black.otf", max(1, int(48 * fk))), rgba(ACC, clamp(fk)))

# ---------- scene 6: structural pack cross-section ----------
def vis_sk_struct(d, lt, t):
    a = ease_out(lt / 0.35)
    m = ease_inout((lt - 1.2) / 1.4)
    label(d, 450, 70, "CROSS-SECTION", MUTED, a, 28, "InterDisplay-Bold.otf")
    # left: separate floor + pack box ; merge
    fy = 260 + m * 120     # floor sheet moves down to become pack lid
    py0 = 420
    # pack box
    d.rounded_rectangle(p(125, py0 + 10, 785, py0 + 210), radius=14 * S, fill=rgba((0, 0, 0), 0.35 * a))
    d.rounded_rectangle(p(120, py0, 780, py0 + 200), radius=14 * S, fill=rgba(STEEL, a))
    for i in range(10):
        cx0 = 145 + i * 62
        d.rounded_rectangle(p(cx0, py0 + 30 + (1 - m) * 0, cx0 + 50, py0 + 175), radius=8 * S, fill=rgba(ACC, a * (0.65 + 0.3 * math.sin(t * 3 + i))))
    # separate pack lid (fades out as floor takes over)
    lid = a * (1 - m)
    d.rectangle(p(120, py0 - 4, 780, py0 + 14), fill=rgba(MUTED, lid))
    # floor sheet
    d.rectangle(p(80, fy, 820, fy + 30 + m * 8), fill=rgba(WHITE, a))
    # seats on floor
    for sx in (260, 640):
        d.rounded_rectangle(p(sx - 60, fy - 120, sx + 60, fy - 6), radius=18 * S, fill=rgba(STEEL, a))
    label(d, 450, fy - 60, "FLOOR", WHITE, a * (1 - m), 30, "InterDisplay-Bold.otf")
    label(d, 450, 652, "BATTERY PACK", ACC, a * (1 - m), 30, "InterDisplay-Bold.otf")
    k = back_out((lt - 2.7) / 0.5)
    if k > 0:
        text_c(d, 450, 655, "PACK = FLOOR", FL("InterDisplay-Black.otf", max(1, int(64 * k))), rgba(ACC, clamp(k)))
        c = ease_out((lt - 3.2) / 0.4)
        d.rounded_rectangle(p(150, 760, 430, 830), radius=35 * S, fill=rgba(WHITE, c))
        label(d, 290, 772, "STIFFER", BG, c, 34, "InterDisplay-Black.otf")
        d.rounded_rectangle(p(470, 760, 750, 830), radius=35 * S, fill=rgba(ACC2, c))
        label(d, 610, 772, "FEWER PARTS", BG, c, 30, "InterDisplay-Black.otf")

# ---------- outro ----------
def end_card(d, lt, cut):
    k = back_out((lt - cut) / 0.5)
    bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
    text_c(d, 450, 420, "EV DRIVE", FL("InterDisplay-Black.otf", max(1, int(130 * max(k, 0.01)))), rgba(WHITE, clamp(k)))
    a = ease_out((lt - cut - 0.5) / 0.4)
    d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
    text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL("InterDisplay-Black.otf", 36), rgba(BG, a))

def vis_sk_outro(d, lt, t):
    dur = sdur("sk_outro")
    cut = dur * 0.55
    if lt < cut:
        a = 1 - ease_inout((lt - cut + 0.3) / 0.3)
        slab(d, 250, 110, 650, 190, a, 1.0, glow=0.5 + 0.5 * math.sin(t * 4), t=t)
        jobs = [("STABILITY", "low center of gravity"), ("SPACE", "flat floor · frunk"), ("STRENGTH", "part of the body")]
        for i, (j, sub) in enumerate(jobs):
            k = ease_out((lt - 0.3 - i * 0.45) / 0.4)
            y = 250 + i * 125
            panel(d, 130, y, 770, y + 105, a * k)
            d.ellipse(p(160, y + 25, 215, y + 80), fill=rgba(ACC, a * k))
            d.line(p(173, y + 54, 185, y + 66, 204, y + 40), fill=rgba(BG, a * k), width=int(7 * S))
            text_c(d, 480, y + 12, j, FL("InterDisplay-Black.otf", 40), rgba(WHITE, a * k))
            text_c(d, 480, y + 62, sub, FL("Inter-SemiBold.otf", 24), rgba(MUTED, a * k))
        q = back_out((lt - 1.8) / 0.5)
        if q > 0:
            text_c(d, 450, 660, "WHAT ELSE COULD", FL("InterDisplay-Black.otf", 46), rgba(ACC, a * clamp(q)))
            text_c(d, 450, 720, "PULL DOUBLE DUTY?", FL("InterDisplay-Black.otf", 46), rgba(ACC, a * clamp(q)))
    else:
        end_card(d, lt, cut)

VIS.update({"sk_hook": vis_sk_hook, "sk_board": vis_sk_board, "sk_weight": vis_sk_weight,
            "sk_rollover": vis_sk_rollover, "sk_space": vis_sk_space, "sk_struct": vis_sk_struct,
            "sk_outro": vis_sk_outro})
