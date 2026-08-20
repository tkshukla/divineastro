"""Prepare web assets from the master logo.

The supplied artwork is 2816x1536 and ~9 MB — fine as a master, ruinous as a
page asset. This produces the sizes the site actually serves and a favicon, and
leaves the master untouched under `assets/`.

    C:\\Astro\\.venv\\Scripts\\python.exe tools\\optimise_logo.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

STATIC = Path(__file__).resolve().parent.parent / "app" / "static"
ASSETS = Path(__file__).resolve().parent.parent / "assets"
MASTER = ASSETS / "logo-master.png"


def kb(path: Path) -> str:
    return f"{path.stat().st_size / 1024:,.0f} KB"


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    source = STATIC / "logo.png"
    if not source.exists() and not MASTER.exists():
        raise SystemExit("No logo found at app/static/logo.png")

    # Work from a stored master so re-running never re-compresses an already
    # compressed file. But if someone drops a NEW logo.png in — different
    # artwork, not our own derivative — that file is the new master. Without
    # this check a rerun would silently overwrite their new logo with the old
    # one, which is exactly the sort of quiet data loss a build step must not do.
    if source.exists():
        adopt = not MASTER.exists()
        if not MASTER.exists():
            reason = "no master yet"
        else:
            derived = source.stat().st_mtime <= MASTER.stat().st_mtime
            adopt = not derived
            reason = "logo.png is newer than the master — treating it as new artwork"
        if adopt:
            if MASTER.exists():
                backup = ASSETS / f"logo-master-previous{MASTER.suffix}"
                shutil.copy2(MASTER, backup)
                print(f"previous master kept as {backup.name}")
            shutil.copy2(source, MASTER)
            print(f"adopted new master ({reason})  {kb(MASTER)}")

    master = Image.open(MASTER).convert("RGBA")
    print(f"master        {master.size[0]}x{master.size[1]}  {kb(MASTER)}")

    def scaled(width: int) -> Image.Image:
        """Resize to `width`, but never upscale — enlarging past the master's
        native size adds bytes and no detail."""
        width = min(width, master.width)
        return master.resize(
            (width, round(master.height * width / master.width)), Image.LANCZOS)

    # The logo is a wide banner; 1200px covers a ~600px slot on a 2x display.
    for name, width in (("logo.png", 1200), ("logo-small.png", 600)):
        out = STATIC / name
        img = scaled(width)
        # Flat gold-on-navy artwork palettes well; quantising cuts the file by
        # ~85% with no visible loss. FASTOCTREE is the only RGBA-safe method.
        img.quantize(colors=256, method=Image.FASTOCTREE,
                     dither=Image.FLOYDSTEINBERG).save(out, "PNG", optimize=True)
        print(f"wrote         {name:24s} {img.width}x{img.height}  {kb(out)}")

    # WebP is smaller again; the page offers it first and falls back to PNG.
    webp = STATIC / "logo.webp"
    scaled(1200).save(webp, "WEBP", quality=88, method=6)
    print(f"wrote         {webp.name:24s} {kb(webp)}")

    # Favicon: crop the central emblem rather than squashing the whole banner,
    # which would be illegible at 32px.
    side = int(master.height * 0.82)
    left = (master.width - side) // 2
    top = (master.height - side) // 2
    emblem = master.crop((left, top, left + side, top + side))
    emblem.resize((512, 512), Image.LANCZOS).save(STATIC / "icon-512.png", "PNG", optimize=True)
    emblem.resize((180, 180), Image.LANCZOS).save(STATIC / "apple-touch-icon.png", "PNG", optimize=True)
    emblem.save(STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    for n in ("icon-512.png", "apple-touch-icon.png", "favicon.ico"):
        print(f"wrote         {n:24s} {kb(STATIC / n)}")


if __name__ == "__main__":
    main()
