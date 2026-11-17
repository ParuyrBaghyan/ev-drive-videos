# Overlays for "Land Rover Raided BYD's Offices. Then a Judge Stepped In" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)
BLUE = (90, 170, 255)

def wt(s, word, n=0):
    """Start time (scene-local) of the n-th spoken word that starts with `word`."""
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!:'").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def hbar(d, y, label, val, vmax, col, k, x0=150, x1=930):
    text(d, x0, y - 44, label, 36, WHITE, anchor="lm", stroke=6)
    w = (x1 - x0) * max(0.03, val / vmax) * smooth(k)
    rect(d, x0, y, x0 + w, y + 70, col, r=16)
    if k > 0.05: text(d, x0 + 20, y + 35, f"£{int(val * smooth(k)):,}", 44, INK, anchor="lm")

def ov_hook(d, lt, t, s):
    pill(d, CX, 420, "LAND ROVER vs BYD", 60, WHITE, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "copied")) / 0.3))
    if k > 0.02: text(d, CX, 600, "A COPY?", 170 * k, RED, stroke=16)
    a = lt - sent(s, 1)
    if a > 0:
        pill(d, CX, 800, "OFFICES RAIDED", 66, YELLOW, k=clamp(pop(a / 0.3)))

def ov_car(d, lt, t, s):
    pill(d, CX, 420, "BYD Ti7 · PLUG-IN HYBRID", 52, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "twenty")
    if a > 0:
        card(d, 90, 500, W - 90, 1000)
        text(d, CX, 550, "UK PRICE", 40, GREY)
        hbar(d, 660, "BYD Ti7", 47995, 68465, LIME, clamp(a / 0.6))
        b = lt - wt(s, "seven")
        if b > 0:
            hbar(d, 840, "Defender 110, 7 seats", 68465, 68465, ORANGE, clamp(b / 0.6))
        text(d, CX, 960, "Prices via CarNewsChina / AutoNext, Nov 2026", 28, GREY, name="Inter-SemiBold.otf")

def ov_raid(d, lt, t, s):
    pill(d, CX, 420, "AUGUST 2026", 56, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "two")
    if a > 0:
        text(d, CX, 590, "2 OFFICES", 150 * clamp(pop(a / 0.3)), YELLOW, stroke=14)
        text(d, CX, 700, "THE NETHERLANDS · FILES SEIZED", 40, WHITE, stroke=8)
    b = lt - sent(s, 1)
    if b > 0:
        pill(d, CX, 840, "SUSPECTED: A DEFENDER TAKEN APART", 44, ORANGE, k=clamp(pop(b / 0.3)))
        text(d, CX, 930, "Source: The Guardian, via CarNewsChina", 30, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_twist(d, lt, t, s):
    pill(d, CX, 420, "THE TWIST", 64, YELLOW, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "judge")
    if a > 0:
        card(d, 90, 500, W - 90, 1000)
        text(d, CX, 570, "DUTCH JUDGE · NOV 11, 2026", 44, GREY)
        b = lt - wt(s, "destroy")
        if b > 0:
            text(d, CX, 680, "DESTROY OR RETURN", 70 * clamp(pop(b / 0.3)), WHITE, stroke=8)
            text(d, CX, 760, "THE SEIZED FILES", 50, WHITE, stroke=6)
        c = lt - wt(s, "fifty")
        if c > 0:
            text(d, CX, 890, "€50,000 / HOUR", 110 * clamp(pop(c / 0.3)), RED, stroke=12)

def ov_still(d, lt, t, s):
    pill(d, CX, 430, "FILES NOT NEEDED FOR THE CASE", 46, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - sent(s, 1)
    if a > 0:
        pill(d, CX, 620, "COPY CLAIM: STILL OPEN", 60, LIME, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "nothing")
    if b > 0:
        text(d, CX, 820, "NOTHING PROVEN YET", 90 * clamp(pop(b / 0.3)), YELLOW, stroke=12)

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "COPY OR JUST BOXY?", 62, WHITE, k=clamp(pop(lt / 0.3)))
    k2 = clamp(pop((lt - wt(s, "tell")) / 0.3))
    if k2 > 0.02: pill(d, CX, 640, "YOUR VERDICT ↓", 70, LIME, fg=INK, k=k2)
    e = lt - wt(s, "follow")
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
