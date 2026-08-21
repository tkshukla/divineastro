"""Doshas and cancellations engine.

Computes Manglik Dosha from Lagna, Moon, and Venus, applying classical cancellations,
and checks Kaal Sarp status.
"""

from __future__ import annotations

from ..chart_service import DOMICILE

MANGLIK_HOUSES = {1, 2, 4, 7, 8, 12}


def analyze_manglik(session) -> dict:
    """Evaluate Manglik Dosha from Lagna, Moon, and Venus reference frames."""
    bundle = session.bundle
    objects = bundle.get("objects", {})
    if "Mars" not in objects or "ASC" not in objects:
        return {"is_manglik": False, "score": 0.0, "details": "Mars or Ascendant data missing."}

    mars_sign = objects["Mars"]["sign"]
    
    # Resolve whole-sign houses relative to Lagna, Moon, Venus
    house_signs = bundle.get("houses", {}).get("signs", [])
    if not house_signs:
        # Fallback if houses signs not populated
        house_signs = [objects["ASC"]["sign"]]
        for i in range(1, 12):
            house_signs.append("")

    def get_house(planet_name: str) -> int:
        if planet_name == "Lagna":
            ref_sign = objects["ASC"]["sign"]
        else:
            ref_sign = objects[planet_name]["sign"]
        
        # Calculate inclusive sign distance
        try:
            ref_idx = house_signs.index(ref_sign)
            mars_idx = house_signs.index(mars_sign)
            return (mars_idx - ref_idx) % 12 + 1
        except ValueError:
            return 1

    h_lagna = get_house("Lagna")
    h_moon = get_house("Moon") if "Moon" in objects else 0
    h_venus = get_house("Venus") if "Venus" in objects else 0

    is_manglik_lagna = h_lagna in MANGLIK_HOUSES
    is_manglik_moon = h_moon in MANGLIK_HOUSES
    is_manglik_venus = h_venus in MANGLIK_HOUSES

    # Check cancellations
    cancellations = []
    
    # 1. Mars in own sign or exaltation
    if mars_sign in ("Aries", "Scorpio", "Capricorn"):
        cancellations.append("Mars is dignified (in Aries, Scorpio, or Capricorn), which cancels the dosha.")

    # 2. Specific house-sign rules
    if h_lagna == 2 and mars_sign in ("Gemini", "Virgo"):
        cancellations.append("Mars in the 2nd house in Mercury's sign (Gemini/Virgo) cancels the dosha.")
    elif h_lagna == 4 and mars_sign in ("Taurus", "Libra"):
        cancellations.append("Mars in the 4th house in Venus's sign (Taurus/Libra) cancels the dosha.")
    elif h_lagna == 7 and mars_sign in ("Cancer", "Capricorn"):
        cancellations.append("Mars in the 7th house in Cancer (debilitated but softened) or Capricorn (exalted) cancels the dosha.")
    elif h_lagna == 8 and mars_sign in ("Sagittarius", "Pisces"):
        cancellations.append("Mars in the 8th house in Jupiter's sign (Sagittarius/Pisces) cancels the dosha.")
    elif h_lagna == 12 and mars_sign in ("Taurus", "Libra"):
        cancellations.append("Mars in the 12th house in Venus's sign (Taurus/Libra) cancels the dosha.")

    # 3. Association with Benefics (Jupiter or Moon)
    from ..astro.vargas import _conjunct, _aspects, _view
    view = _view(bundle)
    if _conjunct(view, "Mars", "Jupiter") or _aspects(view, "Jupiter", "Mars"):
        cancellations.append("Mars is conjunct or aspected by auspicious Jupiter (Guru-Mangala Yoga).")
    if _conjunct(view, "Mars", "Moon") or _aspects(view, "Moon", "Mars"):
        cancellations.append("Mars is conjunct or aspected by the Moon (Chandra-Mangala Yoga).")

    is_cancelled = len(cancellations) > 0
    raw_score = (int(is_manglik_lagna) * 1.0 + int(is_manglik_moon) * 0.5 + int(is_manglik_venus) * 0.3)
    final_score = 0.0 if is_cancelled else raw_score
    is_manglik = final_score > 0

    return {
        "is_manglik": is_manglik,
        "is_cancelled": is_cancelled,
        "cancellations": cancellations,
        "score": round(final_score, 2),
        "houses": {
            "from_lagna": h_lagna,
            "from_moon": h_moon,
            "from_venus": h_venus,
        },
        "flags": {
            "from_lagna": is_manglik_lagna,
            "from_moon": is_manglik_moon,
            "from_venus": is_manglik_venus,
        },
        "description": (
            "Manglik Dosha forms when Mars is placed in the 1st, 2nd, 4th, 7th, 8th, or 12th house. "
            "It can create challenges in relationship harmony, but cancellations significantly soften or nullify these effects."
        )
    }
