"""Builds the two visual-direction mockups for DIVASTRO-70 / DIVASTRO-71.

Not part of the app. It runs the REAL app locally (tests/e2e harness), applies a
prototype skin (mockup_a.css / mockup_b.css) on top of the real screens, adds the
decorative pieces (toran garland, mandala, zodiac ring, free-questions badge,
feature grid) and photographs the result at Pixel 7 size, so the picture shows
real content rather than a drawing.

    C:\\Astro\\.venv\\Scripts\\python.exe docs\\design\\build_mockups.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import Page, server  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "shots"
OUT.mkdir(exist_ok=True)
CSS = {"A": (HERE / "mockup_a.css").read_text(encoding="utf-8"),
       "B": (HERE / "mockup_b.css").read_text(encoding="utf-8")}

# ---------------------------------------------------------------- draft copy
# Every claim maps to a shipped feature. The "10" is the server's free-question
# setting (ASTRO_FREE_QUESTIONS); the real page would read it, not hard-code it.
COPY = {
    "en": dict(
        headline="Know your kundali. Ask anything.",
        sub="Your birth chart, cast to the exact minute — with answers in Hindi or English, drawn from your own planets and dashas.",
        badge_b="\U0001FA94 First 10 questions FREE", badge_s="No card needed · sign up in one tap",
        cta="Get my free kundali reading",
        feats=[("\U0001F319", "Kundali cast to the exact minute"), ("\U0001F5E3\uFE0F", "Ask in Hindi or English"),
               ("\u23F3", "Dasha timelines & transits"), ("\U0001F48D", "Kundali Milan — 36 gun match"),
               ("\U0001F48E", "Remedies & gemstones"), ("\U0001F4C4", "Downloadable PDF reports")]),
    "hi": dict(
        headline="अपनी कुंडली जानें। कुछ भी पूछें।",
        sub="सटीक समय पर बनी आपकी जन्म कुंडली — आपके अपने ग्रहों और दशाओं पर आधारित उत्तर, हिंदी या अंग्रेज़ी में।",
        badge_b="\U0001FA94 पहले 10 प्रश्न बिल्कुल मुफ़्त", badge_s="कार्ड की ज़रूरत नहीं · एक टैप में साइन-अप",
        cta="मेरी निःशुल्क कुंडली देखें",
        feats=[("\U0001F319", "सटीक समय की कुंडली"), ("\U0001F5E3\uFE0F", "हिंदी या अंग्रेज़ी में पूछें"),
               ("\u23F3", "दशा और गोचर"), ("\U0001F48D", "कुंडली मिलान — 36 गुण"),
               ("\U0001F48E", "उपाय और रत्न"), ("\U0001F4C4", "PDF रिपोर्ट डाउनलोड")]),
}


# ---------------------------------------------------------------- ornaments
def mandala(color: str, size: int = 460) -> str:
    c = size / 2
    parts = [f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{color}" stroke-width="1.2"/>' for r in (215, 170, 120, 70, 26)]
    for n, r_in, r_out, w in [(24, 150, 215, 20), (16, 100, 165, 26), (12, 54, 112, 22), (8, 12, 62, 18)]:
        for i in range(n):
            a = 360 / n * i
            parts.append(f'<ellipse cx="{c}" cy="{c - (r_in + r_out) / 2}" rx="{w / 2}" ry="{(r_out - r_in) / 2}" '
                         f'fill="none" stroke="{color}" stroke-width="1.1" transform="rotate({a:.2f} {c} {c})"/>')
    return f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'


def toran(width: int = 412) -> str:
    """A hanging marigold garland — the auspicious threshold of a doorway."""
    parts = ['<path d="M0 4 Q%d 22 %d 4" fill="none" stroke="#b8860b" stroke-width="2"/>' % (width / 2, width)]
    colors = ["#f59e0b", "#ea580c", "#facc15", "#ea580c"]
    x, i = 10, 0
    while x < width:
        y = 4 + 18 * math.sin(math.pi * x / width)
        parts.append(f'<line x1="{x}" y1="{y:.1f}" x2="{x}" y2="{y + 11:.1f}" stroke="#7a3b10" stroke-width="1"/>')
        parts.append(f'<circle cx="{x}" cy="{y + 17:.1f}" r="6.5" fill="{colors[i % 4]}" stroke="#7a3b10" stroke-width=".6"/>')
        parts.append(f'<circle cx="{x}" cy="{y + 17:.1f}" r="2.2" fill="#fff3d6" opacity=".8"/>')
        x, i = x + 21, i + 1
    return f'<svg class="toran" viewBox="0 0 {width} 44" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'


def zodiac_ring() -> str:
    glyphs = "♈♉♊♋♌♍♎♏♐♑♒♓"
    parts = ['<circle cx="150" cy="150" r="146" fill="none" stroke="#f2c66d" stroke-width="1" opacity=".55"/>',
             '<circle cx="150" cy="150" r="112" fill="none" stroke="#f2c66d" stroke-width="1" opacity=".55"/>',
             '<circle cx="150" cy="150" r="129" fill="none" stroke="#f2c66d" stroke-width=".6" stroke-dasharray="2 5" opacity=".7"/>']
    for i, g in enumerate(glyphs):
        a = math.radians(-90 + 30 * i)
        x, y = 150 + 129 * math.cos(a), 150 + 129 * math.sin(a)
        parts.append(f'<text x="{x:.1f}" y="{y + 6:.1f}" text-anchor="middle" font-size="17" fill="#ffe3a6" '
                     f'font-family="Segoe UI Symbol, sans-serif">{g}</text>')
    for i in range(12):
        a = math.radians(-75 + 30 * i)
        parts.append(f'<circle cx="{150 + 146 * math.cos(a):.1f}" cy="{150 + 146 * math.sin(a):.1f}" r="1.8" fill="#ff9f43"/>')
    return f'<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'


# ---------------------------------------------------------------- page building
DECORATE_JS = """
(a) => {
  const $ = (s) => document.querySelector(s);
  const inner = $('.home-inner');
  $('#home-tagline').textContent = a.copy.headline;
  $('#home-blurb').textContent = a.copy.sub;
  $('#home-cta').textContent = a.copy.cta;
  $('.home-points')?.remove();
  $('#home-title').insertAdjacentHTML('afterend', '<div class="deva-sub">दिव्य ज्योतिष</div>');
  $('#home-cta').insertAdjacentHTML('beforebegin',
    `<div class="free-badge"><b>${a.copy.badge_b}</b><small>${a.copy.badge_s}</small></div><br>`);
  const feats = a.copy.feats.map(([i, t]) => `<div class="feat"><i>${i}</i><span>${t}</span></div>`).join('');
  $('.tool-row').insertAdjacentHTML('afterend', `<div class="lotus-div">${a.dir === 'A' ? '\\u{1FAB7}' : '\\u2726'}</div><div class="feat-grid">${feats}</div>`);
  if (a.dir === 'A') {
    $('.site-header').insertAdjacentHTML('afterend', a.toran);
    inner.insertAdjacentHTML('afterbegin', `<div class="mandala-bg">${a.mandala}</div><div class="om">ॐ</div>`);
  } else {
    const logo = $('#home-logo'); const wrap = document.createElement('div');
    wrap.className = 'ring-wrap'; wrap.innerHTML = a.ring; logo.before(wrap); wrap.append(logo);
  }
}
"""


def skin(pg, direction: str, dark_variant: bool = False) -> None:
    pg.add_style_tag(content=CSS[direction])
    if dark_variant:
        pg.evaluate("document.documentElement.classList.add('a-dark')")


def context_args(p, w=412, h=915):
    return {"viewport": {"width": w, "height": h}, "is_mobile": True, "has_touch": True, "device_scale_factor": 2,
            "user_agent": p.devices["Pixel 7"]["user_agent"]}


def shoot_home(p, browser, base, direction, lang, theme, dark_variant=False) -> Path:
    ctx = browser.new_context(**context_args(p, 412, 1230), color_scheme=theme)
    pg = Page(ctx.new_page(), base)
    pg.page.add_init_script(f"localStorage.setItem('astro.theme','{theme}'); localStorage.setItem('astro.lang','{lang}');")
    pg.open_home()
    pg.page.wait_for_timeout(500)
    skin(pg.page, direction, dark_variant)
    pg.page.evaluate(DECORATE_JS, {"dir": direction, "copy": COPY[lang], "mandala": mandala("#b8860b" if not dark_variant else "#f2c66d"),
                                   "toran": toran(), "ring": zodiac_ring()})
    pg.page.wait_for_timeout(400)
    path = OUT / f"{direction}{'d' if dark_variant else ''}_home_{lang}.png"
    pg.page.screenshot(path=str(path))
    ctx.close()
    return path


def shoot_reading(p, browser, base, direction, theme, dark_variant=False) -> Path:
    ctx = browser.new_context(**context_args(p, 412, 915), color_scheme=theme)
    pg = Page(ctx.new_page(), base)
    pg.page.add_init_script(f"localStorage.setItem('astro.theme','{theme}');")
    pg.open_chat()
    pg.page.fill("#q", "What does my chart say about my career?")
    pg.page.tap("#send")
    pg.page.wait_for_function("document.querySelectorAll('.msg.bot').length >= 2", timeout=30000)
    pg.page.wait_for_timeout(2500)
    skin(pg.page, direction, dark_variant)
    # Show the reading as a person sees it before tapping the box: header visible (the
    # header steps aside only while the keyboard is up), starting at their question.
    pg.page.evaluate("""() => { document.activeElement.blur(); document.body.classList.remove('kbd');
                                 const t = document.querySelector('#thread'); const u = t.querySelectorAll('.msg.user');
                                 t.scrollTop = u[u.length-1].offsetTop - 10; }""")
    pg.page.wait_for_timeout(400)
    path = OUT / f"{direction}{'d' if dark_variant else ''}_reading.png"
    pg.page.screenshot(path=str(path))
    ctx.close()
    return path


# ---------------------------------------------------------------- composite
def font(size, bold=False):
    for f in (("georgiab.ttf" if bold else "georgia.ttf"), "arial.ttf"):
        try:
            return ImageFont.truetype(f"C:/Windows/Fonts/{f}", size)
        except OSError:
            continue
    return ImageFont.load_default()


def compose(title: str, subtitle: str, shots: list[tuple[str, Path]], out: Path, bg=(240, 236, 228)) -> None:
    pw = 400
    frames = []
    for label, path in shots:
        im = Image.open(path).convert("RGB")
        im = im.resize((pw, int(im.height * pw / im.width)), Image.LANCZOS)
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width, im.height), 26, fill=255)
        frames.append((label, im, mask))
    gap, pad, head = 36, 48, 150
    width = pad * 2 + len(frames) * pw + (len(frames) - 1) * gap
    height = head + max(f[1].height for f in frames) + 96
    canvas = Image.new("RGB", (width, height), bg)
    d = ImageDraw.Draw(canvas)
    d.text((pad, 38), title, font=font(40, True), fill=(58, 20, 16))
    d.text((pad, 92), subtitle, font=font(21), fill=(110, 84, 70))
    x = pad
    for label, im, mask in frames:
        d.rounded_rectangle((x - 6, head - 6, x + pw + 6, head + im.height + 6), 30, fill=(34, 30, 30))
        canvas.paste(im, (x, head), mask)
        d.text((x + pw // 2, head + im.height + 40), label, font=font(22), fill=(70, 50, 40), anchor="mm")
        x += pw + gap
    canvas.save(out, optimize=True)


def main() -> None:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        a_home = shoot_home(p, browser, base, "A", "en", "light")
        a_read = shoot_reading(p, browser, base, "A", "light")
        a_hi = shoot_home(p, browser, base, "A", "hi", "light")
        a_dark = shoot_home(p, browser, base, "A", "en", "dark", dark_variant=True)
        b_home = shoot_home(p, browser, base, "B", "en", "dark")
        b_read = shoot_reading(p, browser, base, "B", "dark")
        b_hi = shoot_home(p, browser, base, "B", "hi", "dark")
        browser.close()
    compose("Direction A — Temple saffron",
            "Ivory and sandal ground, kumkum-maroon header, saffron actions, turmeric-gold frames, marigold toran, mandala.",
            [("Home (English)", a_home), ("Reading", a_read), ("Home (Hindi)", a_hi), ("Home, dark version", a_dark)],
            HERE / "mockup_A_temple_saffron.png")
    compose("Direction B — Midnight Jyotish",
            "Keeps today's midnight-indigo identity; adds saffron accents, gold filigree frames and a zodiac ring.",
            [("Home (English)", b_home), ("Reading", b_read), ("Home (Hindi)", b_hi)],
            HERE / "mockup_B_midnight_jyotish.png", bg=(226, 226, 236))
    print("built")


if __name__ == "__main__":
    main()
