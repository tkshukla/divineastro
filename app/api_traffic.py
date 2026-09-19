"""Admin endpoint behind the Traffic tab. The aggregation itself lives in
analytics.py so it can be tested without HTTP."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from . import analytics
from .api_account import admin, get_db
from .db import User

router = APIRouter(prefix="/api")


@router.get("/admin/traffic")
def admin_traffic(days: int = 30, _: User = Depends(admin),
                  db: Session = Depends(get_db)) -> dict:
    """Visitors, page views, new users and where they came from, for the last
    `days` days (1-180, IST calendar days)."""
    return analytics.summary(db, days)
