import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app, SESSIONS
from app.chart_service import BirthData, build
import datetime as dt

def test_api():
    client = TestClient(app)
    
    # Cast a new chart
    payload = {
        "name": "Sanskruti",
        "date": "1999-08-14",
        "time": "14:07",
        "place": "Pune, Maharashtra, India",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "timezone": "Asia/Kolkata",
        "zodiac": "sidereal",
        "ayanamsa": "lahiri",
        "house_system": "Whole Sign",
        "time_known": True
    }
    
    print("1. Casting chart via POST /api/chart...")
    resp = client.post("/api/chart", json=payload)
    print("Status:", resp.status_code)
    if resp.status_code != 200:
        print("Error details:", resp.text)
        return
        
    sid = resp.json()["session_id"]
    print("Cast succeeded. Session ID:", sid)
    
    # Fetch dashboard
    print("2. Fetching dashboard via GET /api/dashboard/{sid}...")
    resp2 = client.get(f"/api/dashboard/{sid}")
    print("Status:", resp2.status_code)
    print("Response text:", resp2.text)

if __name__ == "__main__":
    test_api()
