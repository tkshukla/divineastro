import sys
from pathlib import Path
import datetime as dt

# Add root folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chart_service import BirthData, build, vimshottari

session = build(BirthData(
    name="Test Native", date="1987-11-25", time="01:37",
    latitude=25.3176, longitude=82.9739, timezone="Asia/Kolkata",
    place="Varanasi, Uttar Pradesh, India", zodiac="sidereal",
    ayanamsa="lahiri", house_system="Whole Sign"
))

print("=== Chart Details ===")
print("Lagna:", session.bundle["objects"]["ASC"]["sign"])
moon = session.chart.get_object("Moon")
print(f"Moon Position: {moon.sign} {moon.longitude:.4f}°")

print("\n=== Vimshottari Dasha now (Aug 2026) ===")
now_dt = dt.datetime(2026, 8, 21, 12, 0, tzinfo=dt.timezone.utc)
now_dasha = vimshottari(session, now_dt)
print("Nakshatra:", now_dasha["nakshatra"])
print("Mahadasha:", now_dasha["mahadasha"])
print("Antardasha:", now_dasha["antardasha"])

print("\n=== Vimshottari Dasha in 2012 (Marriage) ===")
marriage_dt = dt.datetime(2012, 6, 1, 12, 0, tzinfo=dt.timezone.utc)
marriage_dasha = vimshottari(session, marriage_dt)
print("Mahadasha 2012:", marriage_dasha["mahadasha"])
print("Antardasha 2012:", marriage_dasha["antardasha"])

print("\n=== All Mahadashas ===")
# Let's inspect the calculated majors list
birth = session.birth.local_datetime
lon = moon.longitude
span = 360.0 / 27.0
idx = int(lon // span) % 27
frac = (lon % span) / span
start_lord = idx % 9
SIDEREAL_YEAR = 365.256363004
VIMSHOTTARI = [
    ("Sun", 6), ("Moon", 10), ("Mars", 7), ("Rahu", 18),
    ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17), ("Ketu", 7), ("Venus", 20)
]
cursor = birth - dt.timedelta(days=frac * VIMSHOTTARI[start_lord][1] * SIDEREAL_YEAR)
for i in range(10):
    lord, years = VIMSHOTTARI[(start_lord + i) % 9]
    end = cursor + dt.timedelta(days=years * SIDEREAL_YEAR)
    print(f"{lord}: {cursor.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')} ({years} years)")
    cursor = end
