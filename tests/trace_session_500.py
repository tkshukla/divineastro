import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import SESSIONS
from app.chart_service import build
import app.db as d
import datetime as dt
from zoneinfo import ZoneInfo
from app.astro import panchang as panchang_engine
import swisseph as swe
from stellium.core.ayanamsa import get_ayanamsa_value
from app.chart_service import sign_of
from app.astro.vargas import _sign_distance
from app.chart_service import vimshottari
from app.pdf_report import _dasha_ladder

# Load session from db instead of memory if memory was cleared, or fake it
def trace():
    with d.session() as db:
        # Load the latest birth profile
        profile = db.query(d.BirthProfile).order_by(d.BirthProfile.created_at.desc()).first()
        if not profile:
            print("No birth profile found!")
            return
        print(f"Tracing profile: {profile.name}, DOB: {profile.date} {profile.time}, place: {profile.place}, ayanamsa: {profile.ayanamsa}")
        
        # Build the chart and session
        from app.chart_service import BirthData
        birth_data = BirthData(
            name=profile.name,
            date=profile.date,
            time=profile.time,
            latitude=float(profile.latitude),
            longitude=float(profile.longitude),
            timezone=profile.timezone,
            place=profile.place,
            zodiac=profile.zodiac,
            ayanamsa=profile.ayanamsa,
            house_system=profile.house_system
        )
        chart = build(birth_data)
        
        class FakeSession:
            def __init__(self, chart, birth):
                self.chart = chart
                self.birth = birth
                self.bundle = chart.bundle

        session = FakeSession(chart, profile)
        
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
        print("Panchang ok.")

        print("2. Moon long...")
        swe.set_ephe_path(None)
        julian_day = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0 + now.second/3600.0)
        import inspect
        print("get_ayanamsa_value signature:", inspect.signature(get_ayanamsa_value))
        print("birth.ayanamsa is:", birth.ayanamsa, "type:", type(birth.ayanamsa))
        ayan_val = get_ayanamsa_value(julian_day, birth.ayanamsa)
        res, err = swe.calc_ut(julian_day, swe.MOON)
        moon_lon = (res[0] - ayan_val) % 360.0
        moon_sign_now = sign_of(moon_lon)
        print("Moon sign now:", moon_sign_now)

        print("3. Dasha...")
        dasha_info = vimshottari(session, now)
        print("Dasha info ok:", dasha_info)

        print("4. Dasha ladder...")
        ladder = _dasha_ladder(session, now)
        print("Ladder ok, length:", len(ladder))

if __name__ == "__main__":
    try:
        trace()
        print("ALL TRACING STEPS COMPLETED SUCCESSFULLY!")
    except Exception as e:
        import traceback
        traceback.print_exc()
