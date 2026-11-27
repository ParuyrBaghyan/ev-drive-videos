# Overlays for "BYD Just Built a Rolls-Royce Rival. Here's the Catch" (runs inside tools/render_footage.py globals).
CX = W / 2
GREY = (210, 214, 230)

def wt(s, word, n=0):
    hits = [w["s"] for se in s["sentences"] for w in se["words"] if w["w"].lower().strip(",.?!:'$").startswith(word.lower())]
    return (hits[min(n, len(hits) - 1)] if hits else s["start"]) - s["vs"]

def ov_hook(d, lt, t, s):
    pill(d, CX, 400, "BYD: KNOWN FOR <$10,000 EVs", 52, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "beat")
    if a > 0:
        text(d, CX, 590, "VS", 150 * clamp(pop(a / 0.3)), YELLOW, stroke=16)
        pill(d, CX, 780, "ROLLS-ROYCE", 90, ORANGE, k=clamp(pop(a / 0.3)))

def ov_reveal(d, lt, t, s):
    pill(d, CX, 420, "YANGWANG ALTIOR", 64, LIME, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "fully")
    if a > 0: pill(d, CX, 570, "100% ELECTRIC", 56, GREEN, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "eighteen")
    if b > 0:
        text(d, CX, 740, "5.6 m", 160 * clamp(pop(b / 0.3)), YELLOW, stroke=14)
        text(d, CX, 850, "LONG (~18 FT)", 52, WHITE, stroke=10)
    c = lt - wt(s, "coach")
    if c > 0: pill(d, CX, 960, "COACH DOORS · 4 SEATS", 46, WHITE, k=clamp(pop(c / 0.3)))

def bar2(d, lt, y, lab, val, frac, col, k):
    if k <= 0.01: return
    w = 760 * frac * smooth(k)
    card(d, CX - 400, y - 80, CX + 400, y + 90, a=0.6)
    rect(d, CX - 380, y, CX - 380 + w, y + 70, col, r=16)
    text(d, CX - 380, y - 38, lab, 40, WHITE, anchor="lm", stroke=6)
    if k > 0.6: text(d, CX - 380 + w - 20, y + 35, val, 50, INK, anchor="rm")

def ov_price(d, lt, t, s):
    pill(d, CX, 400, "STARTING PRICE", 56, WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "three")
    if a > 0: bar2(d, lt, 560, "BYD YANGWANG ALTIOR", "~$311,000", 311 / 373, LIME, clamp(a / 0.6))
    b = lt - wt(s, "rolls")
    if b > 0: bar2(d, lt, 760, "ROLLS-ROYCE GHOST", "$373,350", 1.0, ORANGE, clamp(b / 0.6))
    if b > 0.8: text(d, CX, 900, "China pre-sale (InsideEVs) · Ghost MSRP (KBB)", 30, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_power(d, lt, t, s):
    pill(d, CX, 400, "GHOST: GAS V12 · 14 MPG", 52, ORANGE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "four")
    if a > 0: pill(d, CX, 560, "ALTIOR: 4 MOTORS, 1 PER WHEEL", 50, LIME, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "claims")
    if b > 0:
        pc = 10 + 60 * smooth(clamp(b / 1.6))
        battery(d, CX, 740, 360, pc, GREEN, label=f"{int(pc)}%")
    c = lt - wt(s, "minutes")
    if c > 0:
        text(d, CX, 920, "10 → 70% IN ~5 MIN", 64 * clamp(pop(c / 0.3)) + 1, YELLOW, stroke=12)
        text(d, CX, 985, "BYD claim, on its megawatt flash chargers", 30, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_catch(d, lt, t, s):
    pill(d, CX, 420, "THE CATCH", 64, RED, fg=WHITE, k=clamp(pop(lt / 0.3)))
    a = lt - wt(s, "power")
    if a > 0: pill(d, CX, 580, "POWER: ?   BATTERY: ?", 56, WHITE, k=clamp(pop(a / 0.3)))
    b = lt - wt(s, "six")
    if b > 0:
        text(d, CX, 760, "621 MI", 160 * clamp(pop(b / 0.3)), YELLOW, stroke=14)
        text(d, CX, 870, "ON CHINA'S CLTC TEST", 50, WHITE, stroke=10)
        text(d, CX, 930, "lenient vs US EPA ratings · deliveries from Q2 2027", 30, GREY, stroke=6, name="Inter-SemiBold.otf")

def ov_ending(d, lt, t, s):
    pill(d, CX, 430, "$311K BYD", 64, LIME, k=clamp(pop(lt / 0.3)))
    k = clamp(pop((lt - wt(s, "money")) / 0.3))
    if k > 0.02: pill(d, CX, 580, "OR $373K ROLLS?", 64, ORANGE, k=k)
    k2 = clamp(pop((lt - wt(s, "tell")) / 0.3))
    if k2 > 0.02: pill(d, CX, 780, "PICK ONE ↓", 70, WHITE, fg=INK, k=k2)
    e = lt - wt(s, "follow")
    if e > 0: pill(d, CX, 1560, "FOLLOW EV DRIVE", 44, WHITE, k=clamp(pop(e / 0.3)))

OV.update({k[3:]: v for k, v in list(globals().items()) if k.startswith("ov_") and callable(v)})
