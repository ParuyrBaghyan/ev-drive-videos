# Episode visuals: over-the-air (OTA) software updates.
# Runs inside render.py globals (900x900 logical canvas, 2x supersampled).

DARK = (40, 48, 60)
PANEL = (20, 26, 35)
STEEL = (70, 80, 96)
RED = (255, 80, 80)
BLK = "InterDisplay-Black.otf"
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

def ring(d, x, y, r, col, w):
    d.ellipse(p(x - r, y - r, x + r, y + r), outline=col, width=int(w * S))

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

def line(d, pts, col, w):
    d.line(p(*[v for xy in pts for v in xy]), fill=col, width=int(w * S), joint="curve")

def arrow(d, x0, y0, x1, y1, col, w=10, head=26):
    line(d, [(x0, y0), (x1, y1)], col, w)
    ang = math.atan2(y1 - y0, x1 - x0)
    a1, a2 = ang + 2.6, ang - 2.6
    poly(d, [(x1 + math.cos(ang) * 6, y1 + math.sin(ang) * 6), (x1 + math.cos(a1) * head, y1 + math.sin(a1) * head),
             (x1 + math.cos(a2) * head, y1 + math.sin(a2) * head)], col)

def bolt(d, x, y, sc, col):
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    poly(d, [(x + xx * sc, y + yy * sc) for xx, yy in pts], col)

def cloud(d, cx, cy, sc, col):
    for dx, dy, r in [(-60, 10, 48), (0, -20, 64), (62, 6, 50), (-20, 26, 46), (30, 28, 46)]:
        circ(d, cx + dx * sc, cy + dy * sc, r * sc, col)

def padlock(d, cx, cy, sc, col, a, open_=0.0):
    # shackle lifts and rotates when opening
    lift = 26 * open_ * sc
    sx = cx + 22 * open_ * sc
    arc(d, sx, cy - 30 * sc - lift, 28 * sc, 180, 360, rgba(col, a), 10 * sc)
    line(d, [(sx - 28 * sc, cy - 30 * sc - lift), (sx - 28 * sc, cy - 6 * sc - lift * (1 - open_))], rgba(col, a), 10 * sc)
    line(d, [(sx + 28 * sc, cy - 30 * sc - lift), (sx + 28 * sc, cy - 6 * sc)], rgba(col, a), 10 * sc)
    d.rounded_rectangle(p(cx - 42 * sc, cy - 8 * sc, cx + 42 * sc, cy + 52 * sc), radius=10 * sc * S, fill=rgba(col, a))
    circ(d, cx, cy + 20 * sc, 8 * sc, rgba(BG, a))

def tower(d, cx, cy, sc, col, a, t):
    line(d, [(cx, cy - 120 * sc), (cx - 50 * sc, cy + 60 * sc)], rgba(col, a), 8)
    line(d, [(cx, cy - 120 * sc), (cx + 50 * sc, cy + 60 * sc)], rgba(col, a), 8)
    for k in range(3):
        yy = cy - 70 * sc + k * 45 * sc
        hw = 50 * sc * (yy - (cy - 120 * sc)) / (180 * sc)
        line(d, [(cx - hw, yy), (cx + hw, yy)], rgba(col, a), 5)
    circ(d, cx, cy - 124 * sc, 12 * sc, rgba(ACC, a))
    for i in range(3):
        ph = (t * 1.4 + i / 3) % 1.0
        r = (40 + 34 * i + ph * 18) * sc
        arc(d, cx, cy - 124 * sc, r, -60, 60, rgba(ACC, a * (1 - ph * 0.7)), 7)
        arc(d, cx, cy - 124 * sc, r, 120, 240, rgba(ACC, a * (1 - ph * 0.7)), 7)

def progress(d, x0, y, x1, frac, col, a, h=34):
    d.rounded_rectangle(p(x0, y, x1, y + h), radius=h / 2 * S, fill=rgba(DARK, a))
    if frac > 0.01:
        d.rounded_rectangle(p(x0 + 4, y + 4, x0 + 4 + (x1 - x0 - 8) * clamp(frac), y + h - 4), radius=(h - 8) / 2 * S, fill=rgba(col, a))

# ---------- scenes ----------
def vis_ota_hook(d, lt, t):
    dur = sdur("ota_hook")
    a = ease_out(lt / 0.3)
    # night sky with moon and stars
    circ(d, 760, 90, 46, rgba(WHITE, a * 0.9))
    circ(d, 785, 75, 42, rgba(BG, a))
    for k in range(18):
        x = 60 + (k * 173) % 780; y = 40 + (k * 61) % 200
        tw_ = 0.4 + 0.6 * abs(math.sin(lt * 2 + k))
        circ(d, x, y, 3, rgba(MUTED, a * tw_))
    # garage
    d.rounded_rectangle(p(90, 390, 810, 800), radius=24 * S, fill=rgba(PANEL, a))
    poly(d, [(70, 400), (450, 280), (830, 400)], rgba(DARK, a))
    line(d, [(90, 800), (810, 800)], rgba(STEEL, a), 8)
    # car parked
    car_side(d, 450, 700, 1.25, WHITE, alpha=a)
    # cloud sending packets down
    cloud(d, 300, 150, 0.9, rgba(STEEL, a))
    pa = ease_out((lt - 0.3) / 0.4)
    for k in range(6):
        u = (lt * 0.9 + k / 6) % 1.0
        x = 300 + (450 - 300) * u; y = 210 + (560 - 210) * u
        d.rounded_rectangle(p(x - 14, y - 14, x + 14, y + 14), radius=6 * S, fill=rgba(ACC, pa * (1 - u * 0.4)))
    # progress ring above car
    fr = clamp((lt - 0.4) / max(dur - 1.4, 1))
    ring(d, 620, 500, 46, rgba(DARK, a), 12)
    if fr > 0.01:
        arc(d, 620, 500, 46, -90, -90 + 360 * fr, rgba(ACC, a), 12)
    label(d, 620, 484, f"{int(fr * 100)}%", WHITE, a, size=26)
    chip(d, 450, 830, "BETTER BRAKES · NO SHOP VISIT", ACC, ease_out((lt - dur + 1.4) / 0.4), size=30)

def vis_ota_brakes(d, lt, t):
    dur = sdur("ota_brakes")
    a = ease_out(lt / 0.3)
    label(d, 450, 30, "60 → 0 MPH STOPPING DISTANCE", MUTED, a, size=30)
    rows = [("BEFORE UPDATE", 1.0, ACC2, 0.2), ("AFTER UPDATE", 0.875, ACC, 1.4)]
    x0, x1 = 150, 730
    for i, (nm, v, col, dl) in enumerate(rows):
        y = 170 + i * 260
        k = ease_out((lt - dl) / 0.3)
        d.rounded_rectangle(p(60, y - 30, 840, y + 190), radius=26 * S, fill=rgba(PANEL, a))
        label(d, 450, y - 12, nm, col, k, size=30)
        # road
        line(d, [(x0, y + 150), (x1 + 20, y + 150)], rgba(STEEL, k), 6)
        # car decelerates: position follows v - v*(1-u)^2
        u = clamp((lt - dl) / 1.6)
        pos = x0 + (x1 - x0) * v * (1 - (1 - u) ** 2)
        line(d, [(x0, y + 140), (pos - 80, y + 140)], rgba(col, k * 0.5), 6)
        car_side(d, pos - 60, y + 100, 0.42, WHITE, alpha=k)
        # stop marker
        if u >= 1:
            line(d, [(pos + 40, y + 60), (pos + 40, y + 165)], rgba(col, k), 6)
    # bracket of the gap
    ga = ease_out((lt - 3.2) / 0.4)
    xa = x0 + (x1 - x0) * 0.875 + 40; xb = x0 + (x1 - x0) * 1.0 + 40
    line(d, [(xa, 640), (xa, 700), (xb, 700), (xb, 640)], rgba(ACC, ga), 6)
    chip(d, 560, 730, "≈ 20 FT SHORTER", ACC, ga, size=40)
    label(d, 450, 840, "SOURCE: CONSUMER REPORTS, 2018", MUTED, ease_out((lt - 3.6) / 0.4), size=22, f=SEMI)

def vis_ota_irma(d, lt, t):
    dur = sdur("ota_irma")
    a = ease_out(lt / 0.3)
    chip(d, 450, 10, "HURRICANE IRMA · FLORIDA · 2017", ACC2, a, size=28)
    # pack: 75 cells (15 x 5), 60 usable, 15 locked
    cols, rows_ = 15, 5
    px0, py0, cw, chh = 95, 150, 47, 74
    d.rounded_rectangle(p(px0 - 25, py0 - 25, px0 + cols * cw + 15, py0 + rows_ * chh + 15), radius=24 * S, fill=rgba(PANEL, a), outline=rgba(STEEL, a), width=4 * S)
    unlock = ease_inout((lt - 2.6) / 1.6)
    for c in range(cols):
        for r in range(rows_):
            x = px0 + c * cw; y = py0 + r * chh
            appear = ease_out((lt - 0.2 - (c * rows_ + r) * 0.012) / 0.3)
            if c < 12:
                col = ACC
            else:
                cu = clamp(unlock * 3 - (c - 12))
                col = tuple(int(STEEL[j] + (ACC2[j] - STEEL[j]) * cu) for j in range(3))
            d.rounded_rectangle(p(x, y, x + cw - 8, y + chh - 10), radius=8 * S, fill=rgba(col, a * appear))
    # lock over the hidden section
    lx = px0 + 12 * cw + 1.5 * cw - 4
    la = a * (1 - ease_out((lt - 4.4) / 0.4))
    if la > 0.02:
        d.rounded_rectangle(p(lx - 70, py0 + 110, lx + 70, py0 + 260), radius=20 * S, fill=rgba(BG, la * 0.85))
        padlock(d, lx, py0 + 175, 0.9, WHITE, la, open_=ease_out((lt - 2.0) / 0.5))
    label(d, px0 + 6 * cw, py0 + rows_ * chh + 30, "USABLE", ACC, a, size=26)
    if unlock < 0.5:
        label(d, lx - 20, py0 + rows_ * chh + 30, "LOCKED", MUTED, a * (1 - 2 * unlock), size=26)
    else:
        label(d, lx - 20, py0 + rows_ * chh + 30, "UNLOCKED", ACC2, 2 * unlock - 1, size=26)
    # counter 60 -> 75 kWh
    kwh = 60 + 15 * unlock
    label(d, 300, 640, f"{kwh:.0f} kWh", WHITE, a, size=90)
    mi = ease_out((lt - 4.6) / 0.6)
    chip(d, 690, 660, f"+{int(30 * mi)} MI", ACC, mi, size=46)
    label(d, 450, 810, "TEMPORARY · SENT REMOTELY", MUTED, ease_out((lt - 5.2) / 0.4), size=26)

def vis_ota_download(d, lt, t):
    dur = sdur("ota_download")
    a = ease_out(lt / 0.3)
    # road moving
    d.rounded_rectangle(p(40, 610, 860, 720), radius=20 * S, fill=rgba(PANEL, a))
    for k in range(9):
        x = (k * 120 - lt * 420) % 1080 - 90
        line(d, [(x, 665), (x + 60, 665)], rgba(MUTED, a * 0.7), 6)
    # tower on the left
    tower(d, 170, 360, 1.3, STEEL, a, t)
    # car driving (bobbing)
    cx = 560; cy = 590 + math.sin(lt * 9) * 2
    car_side(d, cx, cy, 0.95, WHITE, alpha=a)
    # antenna on roof
    circ(d, cx + 10, cy - 115, 9, rgba(ACC, a))
    # packets from tower to car
    pa = ease_out((lt - 0.4) / 0.4)
    for k in range(5):
        u = (lt * 0.8 + k / 5) % 1.0
        x = 170 + (cx + 10 - 170) * u; y = 200 + (cy - 120 - 200) * u - math.sin(u * math.pi) * 80
        d.rounded_rectangle(p(x - 12, y - 12, x + 12, y + 12), radius=5 * S, fill=rgba(ACC, pa * (1 - u * 0.3)))
    label(d, 600, 150, "CELLULAR / WI-FI", ACC, pa, size=30)
    # progress bar while driving
    fr = clamp((lt - 0.6) / max(dur - 1.2, 1))
    pb = ease_out((lt - 0.6) / 0.4)
    label(d, 450, 760, "DOWNLOADING IN BACKGROUND", WHITE, pb, size=28)
    progress(d, 140, 810, 760, fr, ACC, pb)

def slot_box(d, x, y, name, ver, active, col, a, fill=1.0, status=""):
    d.rounded_rectangle(p(x - 160, y, x + 160, y + 300), radius=28 * S, fill=rgba(PANEL, a),
                        outline=rgba(col if active else STEEL, a), width=int((8 if active else 4) * S))
    label(d, x, y + 24, f"COPY {name}", MUTED, a, size=28)
    label(d, x, y + 80, ver, col if active else WHITE, a * (0.35 + 0.65 * fill), size=72)
    progress(d, x - 120, y + 200, x + 120, fill, col, a, h=28)
    if status:
        label(d, x, y + 248, status, col, a, size=22)

def vis_ota_ab(d, lt, t):
    dur = sdur("ota_ab")
    a = ease_out(lt / 0.3)
    xa, xb, y = 230, 670, 140
    p1 = 2.2   # install done
    p2 = 3.8   # switch
    p3 = 6.3   # failure + rollback
    inst = clamp((lt - 0.6) / (p1 - 0.6))
    sw = ease_inout((lt - p2) / 0.5)
    fail = ease_out((lt - p3) / 0.3)
    back = ease_inout((lt - p3 - 0.6) / 0.6)
    active_b = sw > 0.5 and back < 0.5
    colb = RED if fail > 0.5 else ACC2
    slot_box(d, xa, y, "A", "v1", not active_b, ACC, a, 1.0, "RUNNING" if not active_b else "STANDBY")
    stb = "INSTALLING" if inst < 1 else ("READY" if sw < 0.5 else ("FAILED" if fail > 0.5 else "RUNNING"))
    slot_box(d, xb, y, "B", "v2", active_b or fail > 0.5, colb, a, inst, stb)
    # car "brain" pointer below that chooses the active copy
    bx, by = 450, 640
    d.rounded_rectangle(p(bx - 120, by - 50, bx + 120, by + 50), radius=24 * S, fill=rgba(DARK, a))
    label(d, bx, by - 20, "CAR BOOTS", WHITE, a, size=30)
    pos = sw * (1 - back)
    tx = xa + (xb - xa) * pos
    arrow(d, bx, by - 56, tx, y + 316, rgba(ACC if fail < 0.5 or back > 0.5 else RED, a), w=10)
    # restart chip
    chip(d, 450, 760, "SWITCH ON RESTART", ACC, ease_out((lt - p2) / 0.3) * (1 - fail), size=30)
    chip(d, 450, 760, "ROLLBACK TO v1", ACC, back, size=34)
    if fail > 0:
        cx_, cy_ = xb + 120, y + 40
        circ(d, cx_, cy_, 30 * fail, rgba(RED, fail))
        line(d, [(cx_ - 12, cy_ - 12), (cx_ + 12, cy_ + 12)], rgba(WHITE, fail), 6)
        line(d, [(cx_ + 12, cy_ - 12), (cx_ - 12, cy_ + 12)], rgba(WHITE, fail), 6)
    label(d, 450, 860, "OLD VERSION KEPT UNTIL THE NEW ONE WORKS", MUTED, ease_out((lt - 1.0) / 0.4), size=26, f=SEMI)

def toggle(d, cx, cy, on, a, colon=ACC):
    col = tuple(int(DARK[j] + (colon[j] - DARK[j]) * on) for j in range(3))
    d.rounded_rectangle(p(cx - 80, cy - 42, cx + 80, cy + 42), radius=42 * S, fill=rgba(col, a))
    circ(d, cx - 40 + 80 * on, cy, 32, rgba(WHITE, a))

def vis_ota_outro(d, lt, t):
    dur = sdur("ota_outro")
    if lt < dur * 0.68:
        a = ease_out(lt / 0.35)
        d.rounded_rectangle(p(110, 70, 790, 520), radius=30 * S, fill=rgba(PANEL, a))
        label(d, 450, 100, "SOFTWARE SETTINGS", MUTED, a, size=28)
        on = ease_inout((lt - 0.4) / 0.4) * (1 - ease_inout((lt - 1.8) / 0.4))
        items = [("EXTRA RANGE", on), ("BRAKE TUNING", 1.0), ("NEW FEATURE", ease_inout((lt - 0.8) / 0.4))]
        for i, (nm, v) in enumerate(items):
            yy = 200 + i * 105
            label(d, 330, yy - 18, nm, WHITE, a, size=34)
            toggle(d, 640, yy, v, a)
        # lock snaps onto the first toggle
        la = ease_out((lt - 2.0) / 0.3)
        padlock(d, 760, 200, 0.55, ACC2, la, open_=0.0)
        q = ease_out((lt - 2.4) / 0.5)
        label(d, 450, 590, "WHO REALLY OWNS", WHITE, q, size=58)
        label(d, 450, 670, "YOUR CAR'S FEATURES?", ACC, q, size=58)
    else:
        k = back_out((lt - dur * 0.68) / 0.5)
        bolt(d, 450, 260, 1.7 * k, rgba(ACC, clamp(k)))
        text_c(d, 450, 420, "EV DRIVE", FL(BLK, int(130 * max(k, 0.01))), rgba(WHITE, clamp(k)))
        a = ease_out((lt - dur * 0.68 - 0.5) / 0.4)
        d.rounded_rectangle(p(170, 640, 730, 750), radius=55 * S, fill=rgba(ACC, a))
        text_c(d, 450, 665, "FOLLOW FOR DAILY CAR TECH", FL(BLK, 36), rgba(BG, a))

VIS.update({"ota_hook": vis_ota_hook, "ota_brakes": vis_ota_brakes, "ota_irma": vis_ota_irma,
            "ota_download": vis_ota_download, "ota_ab": vis_ota_ab, "ota_outro": vis_ota_outro})
