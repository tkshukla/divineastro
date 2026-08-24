from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import datetime as dt
from zoneinfo import ZoneInfo
from app.chart_service import BirthData, build
from app.astro import panchang as panchang_engine
from app.pdf_report import _dasha_ladder
from app.chart_service import sign_of
import swisseph as swe

class FakeSession:
    def __init__(self, chart, birth):
        self.chart = chart
        self.birth = birth
        self.bundle = chart.bundle

def test():
    birth_data = BirthData(
        name="Sanskruti", date="1999-08-14", time="14:07",
        latitude=18.5204, longitude=73.8567, timezone="Asia/Kolkata",
        place="Pune, Maharashtra, India", zodiac="sidereal",
        ayanamsa="lahiri", house_system="Whole Sign"
    )
    chart = build(birth_data)
    session = FakeSession(chart, birth_data)
    
    birth = session.birth
    now = dt.datetime.now(ZoneInfo(birth.timezone))
    
    print("1. Panchang...")
    p_data = panchang_engine.daily_panchang(
        date=now.date(),
        latitude=birth.latitude,
        longitude=birth.longitude,
        timezone=birth.timezone,
        ayanamsa=birth.ayanamsa
    )
    print("Panchang ok:", p_data.keys())

    print("2. Moon long...")
    swe.set_ephe_path(None)
    julian_day = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0 + now.second/3600.0)
    from stellium.core.ayanamsa import get_ayanamsa_value
    ayan_val = get_ayanamsa_value(birth.ayanamsa, julian_day)
    res, err = swe.calc_ut(julian_day, swe.MOON)
    moon_lon = (res[0] - ayan_val) % 360.0
    moon_sign_now = sign_of(moon_lon)
    print("Moon sign now:", moon_sign_now)

    print("3. Dasha ladder...")
    ladder = _dasha_ladder(session, now)
    print("Ladder ok, length:", len(ladder))

if __name__ == "__main__":
    test()
