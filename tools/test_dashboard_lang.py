import sys
from pathlib import Path
import datetime as dt

# Add root folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chart_service import BirthData, build
from app.main import get_dashboard, chart_remedies, SESSIONS

class DummyRequest:
    headers = {}
    cookies = {}

birth = BirthData(
    name="Test Native", date="1990-01-01", time="12:00",
    latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata",
    place="New Delhi, India", zodiac="sidereal",
    ayanamsa="lahiri", house_system="Whole Sign"
)
session = build(birth)
sid = "test_session_123"
SESSIONS[sid] = {"session": session, "user_id": None}

req = DummyRequest()

print("--- TESTING ENGLISH DASHBOARD ---")
dash_en = get_dashboard(sid, req, language="en")
print("Transit Score:", dash_en["daily_transit"]["score"])
print("Transit Advice:", dash_en["daily_transit"]["advice"])
print("Tithi:", dash_en["panchang"]["tithi"])
print("Nakshatra:", dash_en["panchang"]["nakshatra"])
print("Mahadasha Lord:", dash_en["dasha"]["mahadasha"]["lord"])

print("\n--- TESTING HINDI DASHBOARD ---")
dash_hi = get_dashboard(sid, req, language="hi")
print("Transit Score (HI):", dash_hi["daily_transit"]["score"])
print("Transit Advice (HI):", dash_hi["daily_transit"]["advice"])
print("Tithi (HI):", dash_hi["panchang"]["tithi"])
print("Nakshatra (HI):", dash_hi["panchang"]["nakshatra"])
print("Mahadasha Lord (HI):", dash_hi["dasha"]["mahadasha"]["lord"])

print("\n--- TESTING HINDI REMEDIES ---")
rem_hi = chart_remedies(sid, req, language="hi")
print("Gemstones (HI):", rem_hi["gemstones"])
print("Maha Lord (HI):", rem_hi["dasha_remedies"]["mahadasha_lord"])

assert dash_hi["daily_transit"]["score"] in ("उत्तम", "सामान्य", "सावधानी")
assert any("\u0900" <= c <= "\u097F" for c in dash_hi["daily_transit"]["advice"])
print("\nALL ASSERTIONS PASSED SUCCESSFULLY!")
