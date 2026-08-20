"""Download the offline city database.

Run once at install time. After this, the app never touches the network:

    C:\\Astro\\.venv\\Scripts\\python.exe tools\\fetch_data.py

Data is from GeoNames (https://geonames.org), CC BY 4.0.
"""

from __future__ import annotations

import io
import sys
import urllib.request
import zipfile
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://download.geonames.org/export/dump/"

FILES = [
    ("cities5000.zip", "cities5000.txt", True),    # ~55k cities with coords + IANA zone
    ("admin1CodesASCII.txt", "admin1CodesASCII.txt", False),   # state / province names
    ("countryInfo.txt", "countryInfo.txt", False),             # ISO code -> country name
]


def fetch(remote: str, target: str, is_zip: bool) -> None:
    dest = DATA / target
    if dest.exists():
        print(f"  {target} already present ({dest.stat().st_size / 1e6:.1f} MB) — skipping")
        return

    print(f"  downloading {remote} …", end="", flush=True)
    with urllib.request.urlopen(BASE + remote, timeout=180) as response:
        payload = response.read()

    if is_zip:
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            zf.extract(target, DATA)
    else:
        dest.write_bytes(payload)
    print(f" done ({dest.stat().st_size / 1e6:.1f} MB)")


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    print(f"Fetching offline geodata into {DATA}")
    try:
        for remote, target, is_zip in FILES:
            fetch(remote, target, is_zip)
    except Exception as exc:
        print(f"\nFailed: {exc}", file=sys.stderr)
        return 1

    # Drop any stale index so the next start rebuilds it from the new dumps.
    cache = DATA / "cities.index.pkl"
    if cache.exists():
        cache.unlink()

    sys.path.insert(0, str(DATA.parent))
    from app import geo

    print(f"\nIndexed {len(geo.get_index()):,} places. Ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
