"""Branded 1080x1080 social card generator for Divine Astro, using the app's own
temple-saffron dark palette (deep maroon -> burnt-orange, from app/static/styles.css).
One reusable template: a diya glow behind a headline + one-line sub, brand mark below.

Usage: python make_card.py "<eyebrow>" "<headline>" "<subline>" out.png
"""
import sys
import platform
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1080
INK = (251, 238, 213)          # --ink dark theme
GOLD = (242, 198, 109)         # --gold
PRIMARY_A = (194, 84, 10)      # --primary-a
PRIMARY_B = (166, 58, 8)       # --primary-b
MAROON_DEEP = (43, 18, 25)     # --surface-bar base
MAROON_DARKER = (26, 10, 14)

# The image is English-only by design (see _assert_ascii_only below), so this
# just needs one clean Latin face per OS - no Devanagari shaping involved.
FONT_FILE = (
    Path("C:/Windows/Fonts/Nirmala.ttc") if platform.system() == "Windows"
    else Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf")
)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_FILE), size)


def vertical_gradient(size, top, bottom):
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)
    h = size[1]
    for y in range(h):
        t = y / h
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (size[0], y)], fill=c)
    return img


def radial_glow(size, center, radius, color, max_alpha=140):
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    d.ellipse([center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
              fill=color + (max_alpha,))
    return glow.filter(ImageFilter.GaussianBlur(radius // 2))


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _assert_ascii_only(*texts: str) -> None:
    """Guard against the Devanagari-shaping bug reappearing in a future edit:
    fail loudly instead of silently rendering garbled Hindi onto a public image."""
    for t in texts:
        if any(0x0900 <= ord(ch) <= 0x097F for ch in t):
            raise ValueError(
                f"Devanagari text passed to the image template: {t!r}. "
                "Pillow has no shaping engine here (raqm unavailable) - it WILL render "
                "matras out of order. Put Hindi in the post caption, not the image.")


def make_card(eyebrow: str, headline: str, subline: str, out: str,
              footer: str = "divineastro.org") -> None:
    # English-only on the image by design: Pillow on this machine has no text
    # shaping engine (raqm unavailable), so Devanagari matras render out of
    # visual order (confirmed on a real render). All Hindi content belongs in
    # the POST CAPTION, which Instagram/Facebook shape correctly themselves -
    # never baked into the image.
    base = vertical_gradient((W, H), MAROON_DARKER, MAROON_DEEP)
    glow = radial_glow((W, H), (W // 2, int(H * 0.38)), 420, PRIMARY_A, 130)
    base = Image.alpha_composite(base.convert("RGBA"), glow)
    draw = ImageDraw.Draw(base)

    # thin gold border, temple-frame feel
    margin = 28
    draw.rounded_rectangle([margin, margin, W - margin, H - margin], radius=18,
                            outline=GOLD + (140,), width=2)

    # a simple diya glyph: bowl + flame, drawn not imported (no external asset needed)
    cx, cy = W // 2, 210
    draw.arc([cx - 70, cy - 20, cx + 70, cy + 60], start=20, end=160, fill=GOLD, width=10)
    flame_pts = [(cx, cy - 95), (cx - 22, cy - 20), (cx + 22, cy - 20)]
    draw.polygon(flame_pts, fill=PRIMARY_A)
    draw.ellipse([cx - 10, cy - 80, cx + 10, cy - 40], fill=(255, 214, 130))

    f_eyebrow = font(34)
    f_head = font(64)
    f_sub = font(36)
    f_foot = font(28)

    # Lay out headline + sub first (their combined height varies with wrapping),
    # THEN vertically center the whole block in the space below the diya - so a
    # short one-line post and a long three-line one both look intentional instead
    # of the short one leaving a hole at the bottom.
    lines = wrap(draw, headline, f_head, W - 180)
    sub_lines = wrap(draw, subline, f_sub, W - 220)
    line_h, sub_h = 78, 48
    block_h = len(lines) * line_h + 20 + len(sub_lines) * sub_h
    content_top, content_bottom = 300, H - 150
    y = content_top + max(0, (content_bottom - content_top - block_h - 60) // 2)

    ew = draw.textlength(eyebrow.upper(), font=f_eyebrow)
    draw.text(((W - ew) / 2, y), eyebrow.upper(), font=f_eyebrow, fill=GOLD + (255,))
    y += 80

    for ln in lines:
        lw = draw.textlength(ln, font=f_head)
        draw.text(((W - lw) / 2, y), ln, font=f_head, fill=INK + (255,))
        y += line_h

    y += 20
    for ln in sub_lines:
        lw = draw.textlength(ln, font=f_sub)
        draw.text(((W - lw) / 2, y), ln, font=f_sub, fill=(224, 199, 168, 255))
        y += sub_h

    # small gold divider above the footer, temple-frame finish
    draw.line([(W / 2 - 40, H - 128), (W / 2 + 40, H - 128)], fill=GOLD + (160,), width=2)
    fw = draw.textlength(footer, font=f_foot)
    draw.text(((W - fw) / 2, H - 100), footer, font=f_foot, fill=GOLD + (220,))

    base.convert("RGB").save(out, "PNG", quality=95)
    print("wrote", out)


if __name__ == "__main__":
    make_card(*sys.argv[1:5])
