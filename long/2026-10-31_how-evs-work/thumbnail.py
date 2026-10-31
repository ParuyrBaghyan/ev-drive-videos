import sys
sys.argv = ['x', sys.argv[1], 'preview', '1']
src = open('tools/render_long.py').read().split('if __name__')[0]
exec(src)
img = background(3.0).convert("RGBA")
layer = Image.new("RGBA", (LW * S, LH * S), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
car_xray(d, 1, solid=0.0, t=0.4, highlight=("battery", "inverter", "motor", "bms", "charger", "port"), dim=0.6)
path = [comp_center("port"), comp_center("charger"), (1100, 470), (1030, 481), (520, 481), comp_center("bms"), (700, 420), comp_center("inverter"), comp_center("motor"), WHEELS[1]]
glow_line(d, path, ACC, 0.8, 6)
layer = layer.reduce(S).resize((int(LW * 1.25), int(LH * 1.25)), Image.LANCZOS)
img.paste(layer, ((W - layer.width) // 2 + 40, 180), layer)
dd = ImageDraw.Draw(img)
f1 = font(BLACK, 150); f2 = font(BLACK, 96)
def ctext(y, s, f, col):
    tw = dd.textlength(s, font=f); x = (W - tw) / 2
    dd.text((x + 6, y + 8), s, font=f, fill=(0, 0, 0))
    dd.text((x, y), s, font=f, fill=col, stroke_width=4, stroke_fill=(0, 0, 0))
ctext(40, "HOW AN EV", f1, WHITE)
ctext(200, "REALLY WORKS", f1, ACC)
dd.rounded_rectangle((W / 2 - 520, 900, W / 2 + 520, 1030), radius=65, fill=ACC)
s = "BATTERY → WHEELS"; tw = dd.textlength(s, font=f2)
dd.text((W / 2 - tw / 2, 912), s, font=f2, fill=BG)
img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(f"{EP}/thumbnail.jpg", quality=92)
