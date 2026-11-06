"""Capture the 3D page frame by frame with Chromium, pipe JPEGs to ffmpeg.
Usage: capture.py DIR OUT.mp4 [t0 t1]   or   capture.py DIR --stills t1,t2,...
"""
import sys, os, json, time, threading, subprocess, functools, http.server, socketserver
from playwright.sync_api import sync_playwright

DIR = os.path.abspath(sys.argv[1]); FPS = 30
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIR)
class Quiet(Handler.func):
    def log_message(self, *a): pass
srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=DIR))
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    br = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--enable-webgl"])
    pg = br.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{port}/index.html")
    pg.wait_for_function("window.READY === true", timeout=180000)
    pg.evaluate("document.fonts.ready")
    if errs: print("console:", errs[:5], flush=True)
    total = json.load(open(f"{DIR}/timing.json"))["total"]
    if sys.argv[2] == "--stills":
        for tt in [float(x) for x in sys.argv[3].split(",")]:
            pg.evaluate(f"renderAt({tt})"); pg.evaluate("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
            pg.screenshot(path=f"{DIR}/still_{tt:05.1f}.jpg", type="jpeg", quality=92)
        print("stills done"); sys.exit()
    out = sys.argv[2]
    t0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    t1 = float(sys.argv[4]) if len(sys.argv) > 4 else total
    tmp = out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    st = time.time()
    for i in range(n0, n1):
        pg.evaluate(f"renderAt({i / FPS})"); pg.evaluate("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
        ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
        if (i - n0) % 60 == 0: print(f"frame {i - n0}/{n1 - n0}  {(time.time() - st) / max(1, i - n0 + 1):.2f}s/frame", flush=True)
    ff.stdin.close()
    if ff.wait() == 0: os.replace(tmp, out)
    print("done", out)
