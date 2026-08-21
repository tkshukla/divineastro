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
    
    print("\n=== Natal Placements ===")
    for k, v in session.bundle["objects"].items():
        print(f"{k}: Sign={v['sign']}, House={v.get('house', 'N/A')}")
        
    rem = recommend_remedies(session)
    print("\n=== Remedies ===")
    print(rem)
    
    mang = analyze_manglik(session)
    print("\n=== Manglik ===")
    print(mang)

if __name__ == "__main__":
    test_remedies_and_doshas()
