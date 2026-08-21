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
    assert mang["houses"]["from_lagna"] == 2
    assert mang["flags"]["from_lagna"] is True  # Mars in 2nd house is Manglik
    assert mang["is_manglik"] is True
    assert mang["score"] == 1.0


if __name__ == "__main__":
    test_remedies_and_doshas()
    print("ALL REMEDIES AND DOSHA TESTS PASSED!")
