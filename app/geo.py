"""Offline geocoding.

Everything here runs against bundled GeoNames dumps in ``C:/Astro/data`` — no
network call is ever made, which is what keeps the app usable fully local.

Data files (downloaded once at install time):
  cities5000.txt        ~55k cities with population >= 5000, incl. IANA timezone
  admin1CodesASCII.txt  state/province names
  countryInfo.txt       ISO country code -> country name
"""

from __future__ import annotations

import csv
import math
import pickle
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE = DATA_DIR / "cities.index.pkl"

# GeoNames cities5000.txt column offsets
_NAME, _ASCII, _ALT, _LAT, _LON = 1, 2, 3, 4, 5
_CC, _ADMIN1, _POP, _TZ = 8, 10, 14, 17


@dataclass(frozen=True)
class Place:
    name: str
    admin1: str
    country: str
    country_code: str
    latitude: float
    longitude: float
    timezone: str
    population: int
    aliases: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        bits = [self.name]
        if self.admin1 and self.admin1 != self.name:
            bits.append(self.admin1)
        bits.append(self.country)
        return ", ".join(bits)

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("aliases", None)
        d["label"] = self.label
        return d


def _fold(text: str) -> str:
    """Lowercase and strip accents so 'Zurich' matches 'Zürich'."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def _load_lookup(path: Path, key_col: int, val_col: int, sep: str = "\t") -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split(sep)
            if len(parts) > max(key_col, val_col):
                out[parts[key_col]] = parts[val_col]
    return out


class PlaceIndex:
    """In-memory city index with prefix search, ranked by population."""

    def __init__(self, places: list[Place]):
        self._places = places
        # search key -> list of indices, so aliases ("Bombay") resolve too
        self._keys: list[tuple[str, int]] = []
        for i, p in enumerate(places):
            seen = set()
            for alias in (p.name, *p.aliases):
                k = _fold(alias)
                if k and k not in seen:
                    seen.add(k)
                    self._keys.append((k, i))
        self._keys.sort()

    def __len__(self) -> int:
        return len(self._places)

    def search(self, query: str, limit: int = 8) -> list[Place]:
        q = _fold(query.strip())
        if len(q) < 2:
            return []
        # Split "delhi, india" -> match on the first token, filter on the rest.
        head, _, tail = q.partition(",")
        head, tail = head.strip(), tail.strip()

        hits: dict[int, int] = {}  # index -> match rank (lower is better)
        for key, idx in self._keys:
            if key == head:
                rank = 0
            elif key.startswith(head):
                rank = 1
            elif head in key:
                rank = 2
            else:
                continue
            if rank < hits.get(idx, 9):
                hits[idx] = rank

        results = [(rank, self._places[i]) for i, rank in hits.items()]
        if tail:
            results = [
                (r, p) for r, p in results
                if tail in _fold(p.country) or tail in _fold(p.admin1)
                or tail == _fold(p.country_code)
            ]
        # A closer name match wins, but a far larger city can outrank a looser
        # one — otherwise "new york" surfaces a 10k-person village in Ukraine
        # ahead of New York City.
        results.sort(key=lambda rp: rp[0] * 1.5 - math.log10(rp[1].population + 1))
        return [p for _, p in results[:limit]]


def _build_index() -> list[Place]:
    countries = _load_lookup(DATA_DIR / "countryInfo.txt", 0, 4)
    admin1 = _load_lookup(DATA_DIR / "admin1CodesASCII.txt", 0, 1)

    cities_file = DATA_DIR / "cities5000.txt"
    if not cities_file.exists():
        raise FileNotFoundError(
            f"Missing {cities_file}. Run tools/fetch_data.py to download the "
            "offline GeoNames city database."
        )

    places: list[Place] = []
    with cities_file.open(encoding="utf-8", newline="") as fh:
        for row in csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
            if len(row) < 18:
                continue
            try:
                lat, lon = float(row[_LAT]), float(row[_LON])
                pop = int(row[_POP] or 0)
            except ValueError:
                continue
            cc = row[_CC]
            # Keep a few ASCII aliases so historical names still resolve
            # (Bombay -> Mumbai, Calcutta -> Kolkata, Madras -> Chennai).
            seen_alias = {_fold(row[_NAME])}
            aliases = []
            for a in row[_ALT].split(","):
                folded = _fold(a)
                if (
                    a.isascii()
                    and folded not in seen_alias
                    and a.replace(" ", "").replace("-", "").isalpha()
                ):
                    seen_alias.add(folded)
                    aliases.append(a)
                    if len(aliases) == 6:
                        break
            places.append(
                Place(
                    name=row[_NAME] or row[_ASCII],
                    admin1=admin1.get(f"{cc}.{row[_ADMIN1]}", ""),
                    country=countries.get(cc, cc),
                    country_code=cc,
                    latitude=lat,
                    longitude=lon,
                    timezone=row[_TZ],
                    population=pop,
                    aliases=tuple(aliases),
                )
            )
    return places


_index: PlaceIndex | None = None


def get_index() -> PlaceIndex:
    """Load the city index, using a pickle cache to keep startup near-instant."""
    global _index
    if _index is not None:
        return _index

    places: list[Place] | None = None
    if CACHE.exists():
        try:
            with CACHE.open("rb") as fh:
                places = pickle.load(fh)
        except Exception:
            places = None
    if places is None:
        places = _build_index()
        try:
            with CACHE.open("wb") as fh:
                pickle.dump(places, fh, protocol=pickle.HIGHEST_PROTOCOL)
        except OSError:
            pass  # cache is an optimisation, not a requirement

    _index = PlaceIndex(places)
    return _index


def search(query: str, limit: int = 8) -> list[Place]:
    return get_index().search(query, limit)


_tf = None


def timezone_for(latitude: float, longitude: float) -> str:
    """Resolve an IANA zone from coordinates — offline, via timezonefinder."""
    global _tf
    if _tf is None:
        from timezonefinder import TimezoneFinder

        _tf = TimezoneFinder()
    return _tf.timezone_at(lat=latitude, lng=longitude) or "UTC"
