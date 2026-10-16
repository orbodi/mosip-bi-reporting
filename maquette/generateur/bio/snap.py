import sys, pathlib
from playwright.sync_api import sync_playwright
src, out, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': w, 'height': h})
    pg.goto(pathlib.Path(src).resolve().as_uri()); pg.wait_for_timeout(300)
    pg.screenshot(path=out); b.close()
