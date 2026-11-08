import sys, os, json, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
DIR = os.path.abspath("."); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Q, directory=DIR)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
POSES = {
  "side_red":       {"ang": 1.5708, "dist": 9.2, "h": 1.3, "paint": "red"},
  "side_white":     {"ang": 1.5708, "dist": 9.2, "h": 1.3, "paint": "white"},
  "side_black":     {"ang": 1.5708, "dist": 9.2, "h": 1.3, "paint": "black"},
  "side34_red":     {"ang": 1.2, "dist": 8.8, "h": 1.4, "paint": "red"},
  "side34_silver":  {"ang": 1.2, "dist": 8.8, "h": 1.4, "paint": "silver"},
  "rearside_brake": {"ang": 1.95, "dist": 8.8, "h": 1.3, "paint": "black", "brake": True, "caliper": True},
}
_OLD = {
  "front34_silver": {"ang": 0.55, "dist": 7.6, "h": 1.3, "paint": "silver"},
  "front34_red":    {"ang": 0.55, "dist": 7.6, "h": 1.3, "paint": "red"},
  "front34_white":  {"ang": 0.55, "dist": 7.6, "h": 1.3, "paint": "white"},
  "side_xray":      {"ang": 1.5708, "dist": 9.2, "h": 1.4, "xray": 1.0, "paint": "silver"},
  "side_xray_hot":  {"ang": 1.5708, "dist": 9.2, "h": 1.4, "xray": 1.0, "paint": "silver", "packColor": "hot"},
  "rear34_brake":   {"ang": 2.55, "dist": 7.6, "h": 1.3, "brake": True, "paint": "white"},
  "low_front_blue": {"ang": 0.25, "dist": 7.0, "h": 0.7, "paint": "blue", "ly": 0.8},
  "top34_black":    {"ang": 0.8, "dist": 8.0, "h": 4.5, "paint": "black"},
}
with sync_playwright() as pw:
    br = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = br.new_page(viewport={"width": 1600, "height": 1000})
    pg.goto(f"http://127.0.0.1:{port}/asset.html"); pg.wait_for_function("window.READY === true", timeout=180000)
    for name, o in POSES.items():
        pg.evaluate(f"pose({json.dumps(o)})"); pg.evaluate("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
        pg.screenshot(path=f"{OUT}/{name}.png", omit_background=True)
        print("ok", name, flush=True)
