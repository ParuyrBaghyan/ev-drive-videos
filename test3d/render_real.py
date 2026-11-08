"""render_real.py OUTDIR poses.json [W H]  -> transparent PNG per pose (photoreal Car Concept)."""
import sys, os, json, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
DIR = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
POSES = json.load(open(sys.argv[2])); W = int(sys.argv[3]) if len(sys.argv) > 3 else 1600; H = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Q, directory=DIR)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
with sync_playwright() as pw:
    br = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = br.new_page(viewport={"width": W, "height": H})
    pg.on("console", lambda m: print("console:", m.text) if m.type in ("error", "warning") else None)
    pg.goto(f"http://127.0.0.1:{port}/realcar.html?w={W}&h={H}")
    pg.wait_for_function("window.READY === true || window.LOAD_ERR", timeout=300000)
    if pg.evaluate("window.LOAD_ERR"): sys.exit(pg.evaluate("window.LOAD_ERR"))
    json.dump(pg.evaluate("window.CAR_INFO"), open(os.path.join(OUT, "_info.json"), "w"), indent=1)
    for name, o in POSES.items():
        pg.evaluate(f"pose({json.dumps(o)})"); pg.evaluate("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
        pg.screenshot(path=f"{OUT}/{name}.png", omit_background=not o.get("bg"))
        print("ok", name, flush=True)
    br.close()
