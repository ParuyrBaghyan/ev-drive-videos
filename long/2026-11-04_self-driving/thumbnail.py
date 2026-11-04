import sys
sys.argv = ['x', sys.argv[1], 'preview', '1']
src = open('tools/render_long2.py').read().split('if __name__')[0]
exec(src)
img = background(3.0)
base = img.crop((VX - 210, 0, VX - 210 + 1920, 1080))
layer = Image.new("RGB", (LW * S, LH * S), BG)
d = ImageDraw.Draw(layer, "RGBA")
cam(1.0, 750, 360)
point_cloud(d, 4.0, 40.0, 1.0, yaw0=0.6, spin=0.0, sweep=False)
layer = layer.reduce(S).resize((1920, int(1920 * LH / LW)), Image.LANCZOS)
img = Image.new("RGB", (1920, 1080), BG)
img.paste(layer, (0, 1080 - layer.height + 40))
dd = ImageDraw.Draw(img, "RGBA")
dd.rectangle((0, 0, 1920, 420), fill=(10, 13, 18, 200))
f1 = font(BLACK, 150); f2 = font(BLACK, 84)
def ctext(y, s, f, col):
    tw = dd.textlength(s, font=f); x = (1920 - tw) / 2
    dd.text((x + 6, y + 8), s, font=f, fill=(0, 0, 0))
    dd.text((x, y), s, font=f, fill=col, stroke_width=4, stroke_fill=(0, 0, 0))
ctext(40, "HOW ROBOT CARS", f1, WHITE)
ctext(210, "SEE THE WORLD", f1, ACC)
dd.rounded_rectangle((1920 / 2 - 430, 930, 1920 / 2 + 430, 1050), radius=60, fill=ACC2)
s = "WHY IT'S SO HARD"; tw = dd.textlength(s, font=f2)
dd.text((1920 / 2 - tw / 2, 945), s, font=f2, fill=BG)
img.resize((1280, 720), Image.LANCZOS).save(f"{sys.argv[1]}/thumbnail.jpg", quality=92)
