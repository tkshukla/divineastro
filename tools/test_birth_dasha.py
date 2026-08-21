import sys
from pathlib import Path
import datetime as dt

# Add root folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chart_service import BirthData, build, vimshottari

dates = ["1987-11-24", "1987-11-25", "1987-11-26"]

for d in dates:
    print(f"\n=================== DOB: {d} 01:37 AM ===================")
    session = build(BirthData(
        name="Test Native", date=d, time="01:37",
        latitude=25.3176, longitude=82.9739, timezone="Asia/Kolkata",
        place="Varanasi, Uttar Pradesh, India", zodiac="sidereal",
        ayanamsa="lahiri", house_system="Whole Sign"
    ))
    
    print("Lagna:", session.bundle["objects"]["ASC"]["sign"])
    moon = session.chart.get_object("Moon")
    print(f"Moon Position: {moon.sign} {moon.longitude:.4f}°")
    
    now_dt = dt.datetime(2026, 8, 21, 12, 0, tzinfo=dt.timezone.utc)
    now_dasha = vimshottari(session, now_dt)
    print("Nakshatra:", now_dasha["nakshatra"])
    print("Mahadasha Now (Aug 2026):", now_dasha["mahadasha"])
    print("Antardasha Now (Aug 2026):", now_dasha["antardasha"])
    
    marriage_dt = dt.datetime(2012, 6, 1, 12, 0, tzinfo=dt.timezone.utc)
    marriage_dasha = vimshottari(session, marriage_dt)
    print("Mahadasha 2012 (Marriage):", marriage_dasha["mahadasha"])
    print("Antardasha 2012 (Marriage):", marriage_dasha["antardasha"])
