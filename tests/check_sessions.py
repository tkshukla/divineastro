import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app.db as d
with d.session() as db:
    sessions = db.query(d.ChartSession).order_by(d.ChartSession.created_at.desc()).limit(5).all()
    for s in sessions:
        print(f"Session: {s.id}, Birth: {s.birth.name if s.birth else 'None'}, Created: {s.created_at}")
