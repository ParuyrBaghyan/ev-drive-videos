"""EV DRIVE thumbnail designer.
Usage: thumbnail.py spec.json out.jpg
spec = {
  "size": "long" | "short",                 # 1280x720 (long) or 1080x1920 (Shorts cover)
  "theme": "red" | "lime" | "blue" | "orange" | "purple",
  "lines": [["YOUR NEW EV", "white"], ["DIRTIER", "accent"], ["THAN GAS?", "white"]],   # 2-4 words per line, max 3 lines
  "car": "side_xray_hot",                   # file in assets/cars (without .png) or null
  "car_box": [x, y, w],                     # optional placement (px, in output size); default per layout
  "flip": false,                            # mirror the car
  "stickers": [{"type": "arrow"|"circle"|"warning"|"question"|"number", "x":..,"y":..,"r":..,"ang":..,"text":".."}],
  "tag": "THE HONEST DATA"                   # optional pill (bottom corner)
}
Design rules baked in: huge heavy type with thick stroke, one accent word, dramatic radial glow,
subject fills ~55% of frame, a single attention device (arrow/circle/!), small brand mark.
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
THEMES = {
    "red":    {"bg1": (40, 4, 8),   "bg2": (150, 14, 24),  "accent": (255, 214, 0)},
    "lime":   {"bg1": (8, 20, 6),   "bg2": (70, 120, 10),  "accent": (198, 255, 61)},
    "blue":   {"bg1": (4, 10, 30),  "bg2": (20, 70, 190),  "accent": (90, 220, 255)},
    "orange": {"bg1": (30, 10, 2),  "bg2": (190, 70, 10),  "accent": (255, 214, 0)},
    "purple": {"bg1": (16, 4, 30),  "bg2": (100, 30, 170), "accent": (255, 120, 220)},
}
WHITE = (255, 255, 255); YELLOW = (255, 214, 0); RED = (255, 40, 40); BLACK = (0, 0, 0)

def font(px): return ImageFont.truetype(FONT, int(px))

def background(W, H, th):
    img = Image.new("RGB", (W, H), th["bg1"])
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((W * 0.15, H * 0.1, W * 1.15, H * 1.4), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(min(W, H) * 0.22))
    img = Image.composite(Image.new("RGB", (W, H), th["bg2"]), img, glow)
    d = ImageDraw.Draw(img, "RGBA")
    # speed streaks
    for i in range(14):
        y = H * (0.25 + 0.05 * i); x0 = W * (0.1 + 0.07 * (i % 5))
        d.line([(x0, y), (x0 + W * 0.5, y - H * 0.02)], fill=(255, 255, 255, 14), width=max(2, H // 240))
    # vignette
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).rectangle((0, 0, W, H), fill=150)
    ImageDraw.Draw(vig).ellipse((-W * 0.1, -H * 0.1, W * 1.1, H * 1.1), fill=0)
    vig = vig.filter(ImageFilter.GaussianBlur(min(W, H) * 0.12))
    img = Image.composite(Image.new("RGB", (W, H), BLACK), img, vig)
    return img

def place_car(img, name, box, flip):
    p = os.path.join(ROOT, "assets", "cars", name + ".png")
    car = Image.open(p).convert("RGBA")
    bb = car.getbbox(); car = car.crop(bb)
    if flip: car = car.transpose(Image.FLIP_LEFT_RIGHT)
    x, y, w = box
    h = int(car.height * w / car.width)
    car = car.resize((int(w), h), Image.LANCZOS)
    # rim light / glow behind subject
    pad = int(w * 0.1)
    m = Image.new("L", (car.width + 2 * pad, car.height + 2 * pad), 0)
    m.paste(car.getchannel("A").point(lambda v: 255 if v > 200 else 0), (pad, pad))
    a = m.filter(ImageFilter.GaussianBlur(w * 0.03))
    glow = Image.new("RGBA", m.size, (255, 255, 255, 0)); glow.putalpha(a.point(lambda v: int(v * 0.55)))
    img.paste(glow, (int(x) - pad, int(y) - pad), glow)
    img.paste(car, (int(x), int(y)), car)
    return (int(x), int(y), int(x + w), int(y + h))

def text_block(img, lines, th, x, y, max_w, size, align="left"):
    d = ImageDraw.Draw(img)
    for txt, col in lines:
        c = th["accent"] if col == "accent" else YELLOW if col == "yellow" else RED if col == "red" else WHITE
        f = font(size)
        while d.textlength(txt, font=f) > max_w and size > 30:
            size -= 4; f = font(size)
        tw = d.textlength(txt, font=f)
        xx = x if align == "left" else x - tw / 2
        sw = max(4, size // 11)
        # hard drop shadow
        d.text((xx + sw * 1.4, y + sw * 1.8), txt, font=f, fill=BLACK, stroke_width=sw, stroke_fill=BLACK)
        d.text((xx, y), txt, font=f, fill=c, stroke_width=sw, stroke_fill=BLACK)
        y += size * 1.02
    return y

def arrow(d, x, y, ang, L, col=RED, w=34):
    ex, ey = x + math.cos(ang) * L, y + math.sin(ang) * L
    for (c, ww) in ((BLACK, w + 16), (col, w)):
        d.line([(x, y), (ex - math.cos(ang) * w * 1.2, ey - math.sin(ang) * w * 1.2)], fill=c, width=ww)
        hl = w * 2.4 + (8 if c == BLACK else 0)
        d.polygon([(ex + math.cos(ang) * (8 if c == BLACK else 0), ey + math.sin(ang) * (8 if c == BLACK else 0)),
                   (ex - math.cos(ang - 0.5) * hl, ey - math.sin(ang - 0.5) * hl),
                   (ex - math.cos(ang + 0.5) * hl, ey - math.sin(ang + 0.5) * hl)], fill=c)

def sticker(img, s, W):
    d = ImageDraw.Draw(img)
    t = s["type"]; x, y = s["x"], s["y"]; r = s.get("r", W * 0.06)
    if t == "arrow":
        arrow(d, x, y, s.get("ang", 0.6), s.get("len", W * 0.16), RED, int(W * 0.022))
    elif t == "circle":
        for (c, ww) in ((BLACK, int(r * 0.2)), (RED, int(r * 0.12))):
            d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), outline=c, width=ww)
    elif t == "warning":
        pts = [(x, y - r), (x - r * 1.1, y + r * 0.85), (x + r * 1.1, y + r * 0.85)]
        d.polygon([(px + (px - x) * 0.12, py + (py - y) * 0.12) for px, py in pts], fill=BLACK)
        d.polygon(pts, fill=YELLOW)
        f = font(r * 1.3); tw = d.textlength("!", font=f)
        d.text((x - tw / 2, y - r * 0.62), "!", font=f, fill=BLACK)
    elif t == "question":
        f = font(r * 2.4); tw = d.textlength("?", font=f)
        d.text((x - tw / 2, y - r * 1.3), "?", font=f, fill=YELLOW, stroke_width=int(r * 0.14), stroke_fill=BLACK)
    elif t == "number":
        f = font(r); txt = s["text"]; tw = d.textlength(txt, font=f)
        pad = r * 0.35
        d.rounded_rectangle((x - tw / 2 - pad + 8, y - pad * 0.6 + 10, x + tw / 2 + pad + 8, y + r * 1.1 + pad * 0.4 + 10), radius=r * 0.3, fill=BLACK)
        d.rounded_rectangle((x - tw / 2 - pad, y - pad * 0.6, x + tw / 2 + pad, y + r * 1.1 + pad * 0.4), radius=r * 0.3, fill=YELLOW)
        d.text((x - tw / 2, y - r * 0.05), txt, font=f, fill=BLACK)

def brand(img, W, H, short):
    d = ImageDraw.Draw(img, "RGBA")
    s = W / 1280 if not short else W / 1080
    x, y = (24 * s, H - 70 * s) if not short else (W / 2 - 120 * s, 150 * s)
    d.rounded_rectangle((x, y, x + 210 * s, y + 52 * s), radius=26 * s, fill=(10, 13, 18, 210))
    pts = [(12, -86), (-38, 8), (-4, 8), (-14, 66), (40, -12), (4, -12)]
    d.polygon([(x + 30 * s + px * 0.2 * s, y + 26 * s + py * 0.2 * s) for px, py in pts], fill=(198, 255, 61))
    d.text((x + 50 * s, y + 9 * s), "EV DRIVE", font=font(30 * s), fill=WHITE)

def tag(img, txt, th, W, H, short):
    d = ImageDraw.Draw(img)
    f = font(W * (0.04 if not short else 0.055)); tw = d.textlength(txt, font=f)
    pad = W * 0.02
    x1 = W - W * 0.025; x0 = x1 - tw - pad * 2
    y0 = H - H * (0.15 if not short else 0.2); y1 = y0 + f.size * 1.45
    d.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=(y1 - y0) / 2, fill=BLACK)
    d.rounded_rectangle((x0, y0, x1, y1), radius=(y1 - y0) / 2, fill=th["accent"])
    d.text((x0 + pad, y0 + f.size * 0.2), txt, font=f, fill=BLACK)

def make(spec, out):
    short = spec.get("size") == "short"
    W, H = (1080, 1920) if short else (1280, 720)
    th = THEMES[spec.get("theme", "red")]
    img = background(W, H, th)
    if spec.get("car"):
        box = spec.get("car_box") or ([W * 0.36, H * 0.38, W * 0.68] if not short else [W * -0.24, H * 0.40, W * 1.48])
        place_car(img, spec["car"], box, spec.get("flip", False))
    for s in spec.get("stickers", []): sticker(img, s, W)
    if short:
        text_block(img, spec["lines"], th, W / 2, H * 0.13, W * 0.94, W * 0.19, align="center")
    else:
        text_block(img, spec["lines"], th, W * 0.035, H * 0.05, W * 0.62, H * 0.17)
    if spec.get("tag"): tag(img, spec["tag"], th, W, H, short)
    brand(img, W, H, short)
    img.convert("RGB").save(out, quality=92)

if __name__ == "__main__":
    make(json.load(open(sys.argv[1])), sys.argv[2])
    print("ok", sys.argv[2])
