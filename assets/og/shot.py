from playwright.sync_api import sync_playwright
import pathlib
p=pathlib.Path(__file__).parent
with sync_playwright() as pw:
    b=pw.chromium.launch(); pg=b.new_page(viewport={"width":1200,"height":630})
    pg.goto((p/"card.html").as_uri()); pg.wait_for_timeout(300)
    pg.screenshot(path=str(p/"og-card.jpg"),type="jpeg",quality=88); b.close()
