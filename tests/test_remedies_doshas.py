"""Unit tests for remedies and Manglik dosha rules.

Run with:
    python -m tests.test_remedies_doshas
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chart_service import BirthData, build
from app.astro.remedies import recommend_remedies
from app.astro.doshas import analyze_manglik


def test_remedies_and_doshas():
    # Let's cast a real chart: DOB: 1987-11-26 01:37 AM, Varanasi
    session = build(BirthData(
        name="Test Native", date="1987-11-26", time="01:37",
        latitude=25.3176, longitude=82.9739, timezone="Asia/Kolkata",
        place="Varanasi, Uttar Pradesh, India", zodiac="sidereal",
        ayanamsa="lahiri", house_system="Whole Sign"
    ))
    
    # 1. Test Remedies
    rem = recommend_remedies(session)
    assert "gemstones" in rem
    assert rem["gemstones"]["life_stone"]["planet"] == "Mercury"  # Virgo Lagna -> Mercury
    assert rem["gemstones"]["life_stone"]["name"] == "Emerald (Panna)"
    assert rem["gemstones"]["lucky_stone"]["planet"] == "Saturn"  # 5th house is Capricorn -> Saturn
    assert rem["gemstones"]["fortune_stone"]["planet"] == "Venus"  # 9th house is Taurus -> Venus
    
    assert rem["dasha_remedies"]["mahadasha_lord"] == "Jupiter" # Born in Moon, currently in Jupiter
    
    # 2. Test Manglik
    mang = analyze_manglik(session)
    # In this chart, Mars is in Virgo (1st house)
    # Let's check:
    assert mang["houses"]["from_lagna"] == 1
    assert mang["flags"]["from_lagna"] is True  # Mars in 1st house is Manglik
    # But Mars in Virgo is in Mercury's sign in the 2nd? No, in 1st house
    # Let's see if there are cancellations:
    # Mars is in Virgo. It's conjunct Ketu/Sun/Mercury etc. Let's see if any cancellation applies:
    # "Mars is conjunct or aspected by Moon/Jupiter"
    # Let's check is_manglik:
    print("Manglik status:", mang)


if __name__ == "__main__":
    test_remedies_and_doshas()
    print("ALL REMEDIES AND DOSHA TESTS PASSED!")
