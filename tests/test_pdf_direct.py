import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chart_service import BirthData, build
import app.pdf_report as pdf_report
import datetime as dt

def test_direct():
    bd = BirthData(
        name="Sanskruti", date="1999-08-14", time="14:07",
        latitude=18.5204, longitude=73.8567, timezone="Asia/Kolkata",
        place="Pune", zodiac="sidereal", ayanamsa="lahiri", house_system="Whole Sign"
    )
    s = build(bd)
    print("Session created.")

    # Compile English Kundali PDF
    print("Compiling English Kundali PDF...")
    pdf_en = pdf_report.chart_pdf(s, brand="Divine Astro", site="divineastro.org", language="en")
    print(f"English PDF success! Size: {len(pdf_en) / 1024:.2f} KB")

    # Compile Hindi Kundali PDF
    print("Compiling Hindi Kundali PDF...")
    pdf_hi = pdf_report.chart_pdf(s, brand="Divine Astro", site="divineastro.org", language="hi")
    print(f"Hindi PDF success! Size: {len(pdf_hi) / 1024:.2f} KB")

if __name__ == "__main__":
    test_direct()
