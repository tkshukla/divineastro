"""FastAPI application — serves the UI and the analysis API.

Runs entirely on localhost with no outbound network calls: ephemeris data ships
with `stellium`, the city database is a bundled GeoNames dump, and the
interpretation engine is local Python.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import os
import re
import uuid
from dataclasses import asdict
from pathlib import Path

from starlette.middleware.sessions import SessionMiddleware

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select

from . import auth, geo, llm, pdf_report
from .api_account import router as account_router
from .api_tools import router as tools_router
from .legal import router as legal_router
from .chart_service import BirthData, build, solar_return, timing_snapshot, transits, wheel_svg
from .db import (
    EntryKind, QuestionLog, User, balance, grant, init_db, session as db_session,
)
from .interpret import analyse
from .interpret.topics import TOPICS

STATIC = Path(__file__).parent / "static"

BRAND = os.environ.get("ASTRO_BRAND", "Divine Astro")
SITE_URL = os.environ.get("ASTRO_SITE_URL", "https://divineastro.org")

app = FastAPI(title=BRAND, description="Vedic chart analysis", version="2.0.0")
# Authlib keeps the OAuth state/nonce in this session between the redirect out
# and the callback back. It is separate from the login cookie in auth.py.
app.add_middleware(
    SessionMiddleware,
    secret_key=auth.SECRET,
    session_cookie="gd_oauth",
    same_site="lax",
    https_only=os.environ.get("ASTRO_COOKIE_SECURE", "0") == "1",
    max_age=600,
)
init_db()
app.include_router(account_router)
app.include_router(tools_router)
app.include_router(legal_router)


class InsufficientCredits(HTTPException):
    def __init__(self, credits: int):
        super().__init__(status_code=402, detail={
            "error": "no_credits",
            "credits": credits,
            "message": "You have used all your questions. Choose a pack to continue.",
        })


def _charge_and_log(db, user, question: str, result: dict, birth_id: int | None) -> int:
    """Debit one credit and record the Q&A. Called only after a successful answer.

    Charging after the analysis — never before — means a crash or a model
    failure cannot take a customer's credit.
    """
    grant(db, user.id, -1, EntryKind.question, note=question[:200])
    db.add(QuestionLog(
        user_id=user.id, birth_id=birth_id, question=question,
        answer=result.get("answer", ""), answer_engine=result.get("answer_engine", ""),
        topic=result.get("topic", ""), verdict=result.get("verdict", ""),
        score=float(result.get("score") or 0.0), language=result.get("language", "en"),
    ))
    db.commit()
    return balance(db, user.id)

# Chart sessions live in memory for the life of the process — nothing is written
# to disk, which is the right default for birth data.
#
# Each entry is keyed to the account that created it. Session ids travel through
# URLs and browser history, so treating possession of an id as proof of
# entitlement would let anyone holding one read another person's birth details —
# personal data under the DPDP Act. Ownership is checked on every access.
SESSIONS: dict[str, dict] = {}
SESSION_TTL = dt.timedelta(hours=12)


def _remember(sid: str, session, user_id: int | None) -> None:
    _expire_sessions()
    SESSIONS[sid] = {"session": session, "user_id": user_id, "created": dt.datetime.now()}


def _expire_sessions() -> None:
    """Drop charts nobody has touched for a while, so birth data does not
    accumulate in memory for the life of the process."""
    cutoff = dt.datetime.now() - SESSION_TTL
    for sid in [s for s, v in SESSIONS.items() if v["created"] < cutoff]:
        SESSIONS.pop(sid, None)


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------

class ChartRequest(BaseModel):
    name: str = ""
    date: str = Field(..., description="YYYY-MM-DD")
    time: str = Field("12:00", description="HH:MM, 24-hour")
    place: str = ""
    latitude: float
    longitude: float
    timezone: str = ""
    # Vedic defaults — see the note on BirthData. A client that omits these
    # must get a kundali, not a Western chart.
    zodiac: str = "sidereal"
    ayanamsa: str = "lahiri"
    house_system: str = "Whole Sign"
    time_known: bool = True


class AskRequest(BaseModel):
    session_id: str
    question: str
    date: str | None = None       # analyse "as of" a date; defaults to today
    language: str = "en"          # 'en' | 'hi'
    # 'off' | 'ollama:<model>' | 'anthropic'. None means "not chosen" and
    # resolves to llm.default_provider() — distinct from an explicit 'off', so a
    # stale cached script that omits the field still gets the good narration.
    provider: str | None = None
    birth_id: int | None = None   # links the answer to a saved birth profile


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "cities": len(geo.get_index())}


@app.get("/api/places")
def places(q: str, limit: int = 8) -> dict:
    return {"results": [p.to_dict() for p in geo.search(q, limit)]}


@app.get("/api/topics")
def topics() -> dict:
    return {
        "topics": [
            {"key": t.key, "label": t.label, "houses": list(t.primary_houses)}
            for t in TOPICS
        ]
    }


@app.post("/api/chart")
def create_chart(req: ChartRequest, request: Request) -> dict:
    tz = req.timezone or geo.timezone_for(req.latitude, req.longitude)
    try:
        birth = BirthData(
            name=req.name.strip(),
            date=req.date,
            time=req.time or "12:00",
            latitude=req.latitude,
            longitude=req.longitude,
            timezone=tz,
            place=req.place or f"{req.latitude:.4f}, {req.longitude:.4f}",
            # Forced, not taken from the request. This is a Jyotish product and
            # every Vedic feature is derived from the sidereal Moon: a tropical
            # chart yields no Vimshottari dasha, no nakshatra and no vargas, so
            # "when will X happen" has nothing to answer from — the reading then
            # refuses rather than inventing dates. Honouring a tropical request
            # meant honouring a request for a broken chart. Stale clients and
            # birth profiles saved before this change are corrected here too.
            zodiac="sidereal",
            ayanamsa="lahiri",
            house_system="Whole Sign",
            time_known=req.time_known,
        )
        session = build(birth)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not build chart: {exc}") from exc

    # A full-entropy id: 16 hex chars is only 64 bits, and these travel in URLs.
    sid = uuid.uuid4().hex
    with db_session() as db:
        owner = auth.current_user(request, db)
    _remember(sid, session, owner.id if owner else None)

    return {
        "session_id": sid,
        "chart": session.bundle,
        "svg": wheel_svg(session),
        "now": timing_snapshot(session, dt.datetime.now()),
    }


def _session(sid: str, request: Request):
    """Fetch a chart session, refusing anyone it does not belong to.

    An anonymous session (cast before signing in) is claimed by the first
    signed-in user to touch it, so casting a chart and then signing in to ask
    a question still works.
    """
    entry = SESSIONS.get(sid)
    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Chart session not found — please recast the chart.")

    with db_session() as db:
        viewer = auth.current_user(request, db)
    viewer_id = viewer.id if viewer else None

    if entry["user_id"] is None and viewer_id is not None:
        entry["user_id"] = viewer_id            # claim on first authenticated use
    elif entry["user_id"] != viewer_id:
        # Deliberately 404 rather than 403: confirming that an id exists would
        # itself leak that somebody else has a chart under it.
        raise HTTPException(
            status_code=404,
            detail="Chart session not found — please recast the chart.")

    return entry["session"]


@app.post("/api/ask")
def ask(req: AskRequest, request: Request) -> dict:
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Ask something.")

    when = dt.datetime.now()
    if req.date:
        try:
            when = dt.datetime.fromisoformat(req.date)
        except ValueError:
            pass

    # Auth first, then ownership: a signed-out visitor should be told to sign in
    # (401, actionable) rather than that the chart does not exist. Only once we
    # know who is asking does a wrong owner become a 404.
    with db_session() as db:
        user = auth.require_user(request, db)
        credits = balance(db, user.id)
        if credits <= 0:
            raise InsufficientCredits(credits)

        # Retrieve last 5 questions for context
        hist_stmt = select(QuestionLog).where(QuestionLog.user_id == user.id)
        if req.birth_id:
            hist_stmt = hist_stmt.where(QuestionLog.birth_id == req.birth_id)
        history_rows = db.execute(
            hist_stmt.order_by(QuestionLog.created_at.desc()).limit(5)
        ).scalars().all()
        history = [{"question": r.question, "answer": r.answer} for r in reversed(history_rows)]

        session = _session(req.session_id, request)
        result = analyse(session, question, when).to_dict()
        result["vedic"] = _vedic_context(session)

        # The engine's own wording is always kept, so the UI can show both and
        # the user can see exactly what the model changed.
        result["answer_engine"] = result["answer"]
        provider = req.provider if req.provider is not None else llm.default_provider()
        polished, error = llm.polish(result, req.language, provider, question, history=history)
        result["answer"] = polished
        result["polished_by"] = provider if not error and provider != "off" else None
        result["llm_error"] = error
        result["language"] = req.language

        result["credits"] = _charge_and_log(db, user, question, result, req.birth_id)
    return result


@app.get("/api/llm")
def llm_status() -> dict:
    # `default` is what the browser should pick when the visitor has never
    # chosen. Deciding it here rather than in JS means turning Claude on is a
    # server-side change alone — no cached script has to expire first.
    return {
        "providers": [asdict(p) for p in llm.providers()],
        "default": llm.default_provider(),
    }


@app.post("/api/ask/stream")
def ask_stream(req: AskRequest, request: Request) -> StreamingResponse:
    """Server-sent events: the engine's verdict immediately, then the rewrite.

    The deterministic analysis is sent first so the reading is on screen at once;
    the LLM's version streams in behind it. On a local model running at a few
    tokens a second that is the difference between watching text arrive and
    staring at a spinner for minutes.
    """
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Ask something.")

    when = dt.datetime.now()
    if req.date:
        try:
            when = dt.datetime.fromisoformat(req.date)
        except ValueError:
            pass

    # Auth, then ownership, then the credit check — all before any work. The
    # debit happens after the analysis succeeds, so a failure never costs the
    # customer a question.
    with db_session() as db:
        user = auth.require_user(request, db)
        credits = balance(db, user.id)
        if credits <= 0:
            raise InsufficientCredits(credits)
        user_id = user.id

        # Retrieve last 5 questions for context
        hist_stmt = select(QuestionLog).where(QuestionLog.user_id == user.id)
        if req.birth_id:
            hist_stmt = hist_stmt.where(QuestionLog.birth_id == req.birth_id)
        history_rows = db.execute(
            hist_stmt.order_by(QuestionLog.created_at.desc()).limit(5)
        ).scalars().all()
        history = [{"question": r.question, "answer": r.answer} for r in reversed(history_rows)]

    session = _session(req.session_id, request)
    result = analyse(session, question, when).to_dict()
    result["answer_engine"] = result["answer"]
    result["language"] = req.language

    with db_session() as db:
        result["credits"] = _charge_and_log(
            db, db.get(User, user_id), question, result, req.birth_id)

    provider = req.provider if req.provider is not None else llm.default_provider()

    def events():
        yield f"event: analysis\ndata: {json.dumps(result)}\n\n"
        if provider in ("off", ""):
            yield "event: done\ndata: {}\n\n"
            return
        try:
            produced = 0
            for chunk in llm.stream_polish(result, req.language, provider, question, history=history):
                produced += len(chunk)
                yield f"event: delta\ndata: {json.dumps({'text': chunk})}\n\n"
            if produced < 120:
                yield ("event: error\ndata: "
                       + json.dumps({"error": "The model returned too little text to trust."})
                       + "\n\n")
        except Exception as exc:
            yield ("event: error\ndata: "
                   + json.dumps({"error": f"{type(exc).__name__}: {exc}"}) + "\n\n")
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _vedic_context(session) -> dict:
    """The classical apparatus an Indian reader expects, for the writing layer.

    The scoring engine is untouched by this — these are facts handed to the
    narration so it can cite the Navamsa and the yogas that actually formed,
    rather than describing a chart in purely Western terms. Failure here must
    never cost someone a reading they paid for, so everything is best-effort.
    """
    out: dict = {}
    try:
        from .astro import vargas

        analysis = vargas.analyse(session)
        out["yogas"] = [
            {"name": y.get("name"), "note": y.get("note")}
            for y in analysis["yogas"]["yogas"]
        ]
        d9 = analysis["vargas"]["D9"]
        moon = (d9.get("positions") or {}).get("Moon", {})
        out["navamsa"] = {
            "lagna": (d9.get("lagna") or {}).get("sign"),
            "moon": moon.get("sign"),
            "moon_vargottama": moon.get("same_as_rashi"),
        }
        out["vargottama"] = analysis["vargottama"]["planets"]

        divs = {}
        for dk in ["D3", "D7", "D9", "D10", "D12"]:
            d_meta = analysis["vargas"].get(dk)
            if d_meta:
                positions = d_meta.get("positions") or {}
                pls = {}
                for pl, info in positions.items():
                    if pl != "Lagna":
                        pls[pl] = f"{info['sign']} (H{info['house']})"
                divs[dk] = {
                    "name": d_meta["name"],
                    "lagna": (d_meta.get("lagna") or {}).get("sign"),
                    "placements": pls
                }
        out["divisional_charts"] = divs
    except Exception as exc:                     # noqa: BLE001 — never fatal
        logging.getLogger(__name__).warning("vedic context unavailable: %s", exc)

    try:
        from .astro import panchang as panchang_engine

        out["sade_sati"] = panchang_engine.sade_sati(session).get("current_period")
    except Exception as exc:                     # noqa: BLE001
        logging.getLogger(__name__).warning("sade sati unavailable: %s", exc)

    try:
        from .astro import delineation

        classical = delineation.delineate(session)
        out["dignities"] = {
            name: {"state": p["dignity"]["state"], "note": p["dignity"]["note"],
                   "house": p["house"], "house_note": p["house_text"],
                   "avastha": p["avastha"]["state"], "avastha_note": p["avastha"]["note"]}
            for name, p in classical["planets"].items()
        }
        out["career_significators"] = classical["career"]
        out["conjunctions"] = classical["conjunctions"]

        from .chart_service import vimshottari
        import datetime as _dt
        now = _dt.datetime.now(_dt.timezone.utc)
        antar_lord = vimshottari(session, now).get("antardasha", {}).get("lord")
        antar_reading = delineation.antardasha_reading(antar_lord) if antar_lord else None
        if antar_reading:
            out["antardasha_reading"] = {"lord": antar_lord, "note": antar_reading}

        from .chart_service import yogini_dasha
        yd = yogini_dasha(session, now)
        maha, antar = yd.get("mahadasha"), yd.get("antardasha")
        if maha:
            out["yogini_dasha"] = {
                "mahadasha": {**maha, "reading": delineation.yogini_dasha_reading(maha["name"])},
                "antardasha": ({**antar, "reading": delineation.yogini_dasha_reading(antar["name"])}
                                if antar else None),
            }
    except Exception as exc:                     # noqa: BLE001 — never fatal
        logging.getLogger(__name__).warning("classical delineation unavailable: %s", exc)

    return out


TITHI_HI = {
    "Pratipada": "प्रतिपदा", "Dwitiya": "द्वितीया", "Tritiya": "तृतीया",
    "Chaturthi": "चतुर्थी", "Panchami": "पंचमी", "Shashthi": "षष्ठी",
    "Saptami": "सप्तमी", "Ashtami": "अष्टमी", "Navami": "नवमी",
    "Dashami": "दशमी", "Ekadashi": "एकादशी", "Dwadashi": "द्वादशी",
    "Trayodashi": "त्रयोदशी", "Chaturdashi": "चतुर्दशी", "Purnima": "पूर्णिमा",
    "Amavasya": "अमावस्या"
}

YOGA_HI = {
    "Vishkambha": "विष्कम्भ", "Priti": "प्रीति", "Ayushman": "आयुष्मान",
    "Saubhagya": "सौभाग्य", "Shobhana": "शोभन", "Atiganda": "अतिगण्ड",
    "Sukarma": "सुकर्मा", "Dhriti": "धृति", "Shula": "शूल", "Ganda": "गण्ड",
    "Vriddhi": "वृद्धि", "Dhruva": "ध्रुव", "Vyaghata": "व्याघात",
    "Harshana": "हर्षण", "Vajra": "वज्र", "Siddhi": "सिद्धि",
    "Vyatipata": "व्यतीपात", "Variyana": "वरीयान", "Parigha": "परिघ",
    "Shiva": "शिव", "Siddha": "सिद्ध", "Sadhya": "साध्य", "Shubha": "शुभ",
    "Shukla": "शुक्ल", "Brahma": "ब्रह्म", "Indra": "इन्द्र", "Vaidhriti": "वैधृति"
}

KARANA_HI = {
    "Bava": "बव", "Balava": "बालव", "Kaulava": "कौलव", "Taitila": "तैतिल",
    "Gara": "गर", "Vanija": "वणिज", "Vishti": "विष्टि (भद्रा)", "Shakuni": "शकुनि",
    "Chatushpada": "चतुष्पाद", "Naga": "नाग", "Kimstughna": "किंस्तुघ्न"
}

NAKSHATRAS_HI = {
    "Ashwini": "अश्विनी", "Bharani": "भरणी", "Krittika": "कृत्तिका",
    "Rohini": "रोहिणी", "Mrigashira": "मृगशिरा", "Ardra": "आर्द्रा",
    "Punarvasu": "पुनर्वसु", "Pushya": "पुष्य", "Ashlesha": "आश्लेषा",
    "Magha": "मघा", "Purva Phalguni": "पूर्वा फाल्गुनी",
    "Uttara Phalguni": "उत्तरा फाल्गुनी", "Hasta": "हस्त", "Chitra": "चित्रा",
    "Swati": "स्वाति", "Vishakha": "विशाखा", "Anuradha": "अनुराधा",
    "Jyeshtha": "ज्येष्ठा", "Mula": "मूल", "Purva Ashadha": "पूर्वाषाढ़ा",
    "Uttara Ashadha": "उत्तराषाढ़ा", "Shravana": "श्रवण",
    "Dhanishta": "धनिष्ठा", "Shatabhisha": "शतभिषा",
    "Purva Bhadrapada": "पूर्व भाद्रपद", "Uttara Bhadrapada": "उत्तर भाद्रपद",
    "Revati": "रेवती"
}

PLANET_HI = {
    "Sun": "सूर्य", "Moon": "चंद्रमा", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "बृहस्पति", "Venus": "शुक्र", "Saturn": "शनि",
    "Rahu": "राहु", "Ketu": "केतु"
}


@app.get("/api/doshas/{sid}")
def chart_doshas(sid: str, request: Request) -> dict:
    """Sade Sati, Kaal Sarp and Manglik Dosha analysis for a chart already on screen."""
    from .astro import panchang as panchang_engine
    from .astro.doshas import analyze_manglik

    session = _session(sid, request)
    return {
        "sade_sati": panchang_engine.sade_sati(session),
        "kaal_sarp": panchang_engine.kaal_sarp(session),
        "manglik": analyze_manglik(session)
    }


@app.get("/api/remedies/{sid}")
def chart_remedies(sid: str, request: Request, language: str = "en") -> dict:
    """Get gemstone recommendations and dasha-specific remedies."""
    from .astro.remedies import recommend_remedies
    session = _session(sid, request)
    data = recommend_remedies(session)
    if language == "hi":
        role_map = {
            "Life Stone": "लग्न रत्न (जीवन रत्न)",
            "Lucky Stone": "भाग्य रत्न (पंचमेश)",
            "Fortune Stone": "भाग्येश रत्न (नवमेश)"
        }
        gem_hi = {
            "Ruby (Manik)": "माणिक्य (Ruby)",
            "Pearl (Moti)": "मोती (Pearl)",
            "Red Coral (Moonga)": "मूंगा (Red Coral)",
            "Emerald (Panna)": "पन्ना (Emerald)",
            "Yellow Sapphire (Pukhraj)": "पुखराज (Yellow Sapphire)",
            "Diamond or White Sapphire": "हीरा अथवा सफेद पुखराज",
            "Blue Sapphire (Neelam)": "नीलम (Blue Sapphire)",
            "Hessonite (Gomed)": "गोमेद (Hessonite)",
            "Cat's Eye (Lehsuniya)": "लहसुनिया (Cat's Eye)"
        }
        translated_gems = {}
        for k, v in data.get("gemstones", {}).items():
            translated_gems[k] = {
                **v,
                "role": role_map.get(v.get("role"), v.get("role")),
                "name": gem_hi.get(v.get("name"), v.get("name")),
                "metal": "सोना या तांबा" if "Gold" in v.get("metal", "") else ("चांदी" if "Silver" in v.get("metal", "") else v.get("metal")),
                "finger": "अनामिका (Ring Finger)" if "Ring" in v.get("finger", "") else ("कनिष्ठिका (Little Finger)" if "Little" in v.get("finger", "") else ("तर्जनी (Index Finger)" if "Index" in v.get("finger", "") else "मध्यमा (Middle Finger)"))
            }
        dr = data.get("dasha_remedies", {})
        translated_dr = {
            **dr,
            "mahadasha_lord": PLANET_HI.get(dr.get("mahadasha_lord"), dr.get("mahadasha_lord"))
        }
        return {
            **data,
            "gemstones": translated_gems,
            "dasha_remedies": translated_dr
        }
    return data


@app.get("/api/dashboard/{sid}")
def get_dashboard(sid: str, request: Request, language: str = "en") -> dict:
    """Get daily personalized cosmic dashboard for the native."""
    from .astro import panchang as panchang_engine
    from .chart_service import vimshottari
    import swisseph as swe
    from zoneinfo import ZoneInfo

    session = _session(sid, request)
    birth = session.birth
    now = dt.datetime.now(ZoneInfo(birth.timezone))
    
    # Calculate daily panchang at the birth place/timezone
    p_data = panchang_engine.daily_panchang(
        date=now.date(),
        latitude=birth.latitude,
        longitude=birth.longitude,
        timezone=birth.timezone,
        ayanamsa=birth.ayanamsa
    )

    # Calculate current transit Moon sign
    swe.set_ephe_path(None)
    julian_day = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0 + now.second/3600.0)
    from stellium.core.ayanamsa import get_ayanamsa_value
    ayan_val = get_ayanamsa_value(julian_day, birth.ayanamsa)
    
    res, err = swe.calc_ut(julian_day, swe.MOON)
    moon_lon = (res[0] - ayan_val) % 360.0
    from .chart_service import sign_of
    moon_sign_now = sign_of(moon_lon)

    natal_moon_sign = session.bundle["objects"]["Moon"]["sign"]
    natal_lagna_sign = session.bundle["objects"]["ASC"]["sign"]

    from .astro.vargas import _sign_distance
    dist_moon = _sign_distance(natal_moon_sign, moon_sign_now)
    dist_lagna = _sign_distance(natal_lagna_sign, moon_sign_now)

    if language == "hi":
        transit_score = "सामान्य"
        transit_advice = "चंद्रमा का गोचर सामान्य फलदायी है। नित्य कार्यों को योजनाबद्ध रूप से करने और आत्म-चिंतन के लिए उत्तम दिन है।"
        if dist_moon in (3, 6, 10, 11):
            transit_score = "उत्तम"
            transit_advice = "आज का दिन अत्यंत शुभ और फलदायी है। नए कार्यों की शुरुआत, सामाजिक लाभ और महत्वपूर्ण निर्णयों के लिए समय अनुकूल है।"
        elif dist_moon in (4, 8, 12):
            transit_score = "सावधानी"
            transit_advice = "चंद्रमा आपकी जन्म राशि से अशुभ (४, ८, १२वें) भाव में गोचर कर रहा है। व्यर्थ के विवादों से बचें, वाहन सावधानी से चलाएं और धैर्य रखें।"
    else:
        transit_score = "Neutral"
        transit_advice = "The Moon brings an ordinary day. Good for routine tasks and reflection."
        if dist_moon in (3, 6, 10, 11):
            transit_score = "Excellent"
            transit_advice = "A highly productive and auspicious day. Great for initiating new tasks, social gains, and actions."
        elif dist_moon in (4, 8, 12):
            transit_score = "Caution"
            transit_advice = "Moon is transiting a dusthana house from your natal Moon. Avoid starting major conflicts, drive carefully, and rest."

    dasha_info = vimshottari(session, now)
    
    from .pdf_report import _dasha_ladder
    ladder = []
    try:
        ladder = _dasha_ladder(session, now)
    except Exception:
        pass

    tithis = p_data.get("tithi", [])
    tithi_name = tithis[0].get("name") if (isinstance(tithis, list) and len(tithis) > 0) else "—"
    
    nakshatras = p_data.get("nakshatra", [])
    nakshatra_name = nakshatras[0].get("name") if (isinstance(nakshatras, list) and len(nakshatras) > 0) else "—"
    
    yogas = p_data.get("yoga", [])
    yoga_name = yogas[0].get("name") if (isinstance(yogas, list) and len(yogas) > 0) else "—"
    
    karanas = p_data.get("karana", [])
    karana_name = karanas[0].get("name") if (isinstance(karanas, list) and len(karanas) > 0) else "—"

    if language == "hi":
        tithi_name = TITHI_HI.get(tithi_name, tithi_name)
        nakshatra_name = NAKSHATRAS_HI.get(nakshatra_name, nakshatra_name)
        yoga_name = YOGA_HI.get(yoga_name, yoga_name)
        karana_name = KARANA_HI.get(karana_name, karana_name)

        maha = dasha_info.get("mahadasha")
        if maha:
            maha = {**maha, "lord": PLANET_HI.get(maha.get("lord"), maha.get("lord"))}
        antar = dasha_info.get("antardasha")
        if antar:
            antar = {**antar, "lord": PLANET_HI.get(antar.get("lord"), antar.get("lord"))}
        
        status_map = {"past": "गत काल", "current": "सक्रिय", "ahead": "आगामी"}
        translated_ladder = []
        for row in ladder:
            r = list(row)
            if len(r) > 0:
                r[0] = PLANET_HI.get(r[0], r[0])
            if len(r) > 4:
                r[4] = status_map.get(r[4], r[4])
            translated_ladder.append(r)
        ladder = translated_ladder
    else:
        maha = dasha_info.get("mahadasha")
        antar = dasha_info.get("antardasha")

    return {
        "panchang": {
            "tithi": tithi_name,
            "nakshatra": nakshatra_name,
            "yoga": yoga_name,
            "karana": karana_name,
            "sunrise": p_data.get("sun", {}).get("rise"),
            "sunset": p_data.get("sun", {}).get("set"),
            "muhurtha": {
                "abhijit": {
                    "start": p_data.get("muhurta", {}).get("abhijit", {}).get("start") if p_data.get("muhurta", {}).get("abhijit") else None,
                    "end": p_data.get("muhurta", {}).get("abhijit", {}).get("end") if p_data.get("muhurta", {}).get("abhijit") else None,
                },
                "rahu_kaal": {
                    "start": p_data.get("muhurta", {}).get("rahu_kaal", {}).get("start") if p_data.get("muhurta", {}).get("rahu_kaal") else None,
                    "end": p_data.get("muhurta", {}).get("rahu_kaal", {}).get("end") if p_data.get("muhurta", {}).get("rahu_kaal") else None,
                }
            }
        },
        "daily_transit": {
            "moon_sign_now": moon_sign_now,
            "house_from_moon": dist_moon,
            "house_from_lagna": dist_lagna,
            "score": transit_score,
            "advice": transit_advice
        },
        "dasha": {
            "mahadasha": maha,
            "antardasha": antar,
            "ladder": ladder
        }
    }



@app.get("/api/transits/{sid}")
def current_transits(sid: str, request: Request, date: str | None = None) -> dict:
    session = _session(sid, request)
    when = dt.datetime.fromisoformat(date) if date else dt.datetime.now()
    return {
        "date": when.strftime("%d %B %Y"),
        "transits": transits(session, when)[:20],
        "timing": timing_snapshot(session, when),
    }


@app.get("/api/solar-return/{sid}")
def solar(sid: str, request: Request, year: int | None = None) -> dict:
    session = _session(sid, request)
    return solar_return(session, year or dt.datetime.now().year)


@app.get("/api/report/{sid}")
def report(sid: str, request: Request) -> dict:
    """The chart as the library's own LLM-ready prompt text — handy for export."""
    session = _session(sid, request)
    return {"text": session.chart.to_prompt_text()}


@app.get("/api/ashtakavarga/{sid}")
def ashtakavarga_endpoint(sid: str, request: Request, lang: str = "en") -> dict:
    """Sarvashtakavarga (337 bindus) and Bhinnashtakavarga matrix and house strengths."""
    from .astro.ashtakavarga import calculate_ashtakavarga
    session = _session(sid, request)
    return calculate_ashtakavarga(session, lang=lang)


@app.get("/api/vargas/{sid}")
def shodashvarga_endpoint(sid: str, request: Request, lang: str = "en") -> dict:
    """Classical Parashari Shodashvarga divisional charts (D1 to D60)."""
    from .astro.vargas import get_shodashvarga_data
    session = _session(sid, request)
    return get_shodashvarga_data(session, lang=lang)


@app.get("/api/jaimini/{sid}")
def jaimini_endpoint(sid: str, request: Request, lang: str = "en") -> dict:
    """Jaimini 7 Chara Karakas, Karakamsha Lagna, and 12 Arudha Padas."""
    from .astro.jaimini import get_jaimini_data
    session = _session(sid, request)
    return get_jaimini_data(session, lang=lang)


@app.get("/api/sudarshana/{sid}")
def sudarshana_endpoint(sid: str, request: Request, lang: str = "en") -> dict:
    """Sudarshana Chakra 3-tier synthesis across Janma, Moon, and Sun Lagnas."""
    from .astro.sudarshana import get_sudarshana_data
    session = _session(sid, request)
    return get_sudarshana_data(session, lang=lang)


@app.delete("/api/session/{sid}")
def forget(sid: str, request: Request) -> dict:
    _session(sid, request)          # only the owner may discard it
    SESSIONS.pop(sid, None)
    return {"ok": True}


# --------------------------------------------------------------------------
# PDF export
#
# Both routes require a signed-in user. The question export is scoped to that
# user's own rows in SQL — `?ids=` is intersected with `user_id`, never trusted
# on its own — so no id a caller can invent reaches another account's answers.
# --------------------------------------------------------------------------

MAX_PDF_QUESTIONS = 500


def _pdf_response(data: bytes, filename: str) -> Response:
    return Response(
        content=data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


def _requested_ids(ids: str) -> list[int]:
    out: list[int] = []
    for token in ids.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            out.append(int(token))
        except ValueError:
            raise HTTPException(400, f"'{token}' is not a question id.") from None
    return out


@app.get("/api/pdf/questions")
def pdf_questions(request: Request, limit: int = 200, ids: str = "") -> Response:
    """The signed-in user's questions and answers as a PDF.

    ?limit=N   keep the N most recent (default 200, capped at 500)
    ?ids=1,2,3 export just those questions — still only ones the caller owns
    """
    wanted = _requested_ids(ids)
    with db_session() as db:
        user = auth.require_user(request, db)
        stmt = select(QuestionLog).where(QuestionLog.user_id == user.id)
        if wanted:
            stmt = stmt.where(QuestionLog.id.in_(wanted))
        rows = db.execute(
            stmt.order_by(QuestionLog.created_at.desc(), QuestionLog.id.desc())
            .limit(max(1, min(limit, MAX_PDF_QUESTIONS)))
        ).scalars().all()
        name, email = user.name, user.email

    if not rows:
        raise HTTPException(404, "There are no questions to export yet.")
    rows = list(reversed(rows))          # a record reads oldest-first

    try:
        data = pdf_report.questions_pdf(
            rows, brand=BRAND, site=SITE_URL, user_name=name, user_email=email)
    except Exception as exc:
        raise HTTPException(500, f"Could not build the PDF: {exc}") from exc
    return _pdf_response(data, pdf_report.safe_filename(BRAND, "questions", name or email))


@app.get("/api/pdf/chart/{sid}")
def pdf_chart(sid: str, request: Request, date: str | None = None, lang: str = "en") -> Response:
    """A full chart report PDF for an active chart session."""
    with db_session() as db:
        auth.require_user(request, db)
    session = _session(sid, request)      # and it must be this user's chart

    when = dt.datetime.now()
    if date:
        try:
            when = dt.datetime.fromisoformat(date)
        except ValueError:
            pass

    try:
        data = pdf_report.chart_pdf(session, brand=BRAND, site=SITE_URL, when=when, language=lang)
    except Exception as exc:
        raise HTTPException(500, f"Could not build the PDF: {exc}") from exc
    return _pdf_response(
        data, pdf_report.safe_filename(BRAND, "chart", session.birth.name or "chart"))


@app.get("/api/pdf/remedies/{sid}")
def pdf_remedies(sid: str, request: Request, lang: str = "en") -> Response:
    """A full remedies and gemstones PDF report for an active chart session."""
    with db_session() as db:
        auth.require_user(request, db)
    session = _session(sid, request)      # and it must be this user's chart

    try:
        data = pdf_report.remedies_pdf(session, brand=BRAND, site=SITE_URL, language=lang)
    except Exception as exc:
        raise HTTPException(500, f"Could not build the PDF: {exc}") from exc
    return _pdf_response(
        data, pdf_report.safe_filename(BRAND, "remedies", session.birth.name or "remedies"))


@app.get("/api/pdf/single-question/{sid}")
def pdf_single_question(sid: str, request: Request, sku: str = "sq_career", lang: str = "en") -> Response:
    """Download a purchased single-question consultation report (Career, Marriage, Wealth)."""
    with db_session() as db:
        user = auth.require_user(request, db)
        order = billing.has_paid_report(db, user, sku=sku, topic=sku)
        if not order:
            raise HTTPException(402, "This single-question report requires purchase before downloading.")

    session = _session(sid, request)
    try:
        data = pdf_report.single_question_pdf(session, topic=sku, brand=BRAND, site=SITE_URL, language=lang)
    except Exception as exc:
        raise HTTPException(500, f"Could not build the PDF: {exc}") from exc
    return _pdf_response(
        data, pdf_report.safe_filename(BRAND, sku, session.birth.name or "report"))


@app.get("/api/pdf/life-book/{sid}")
def pdf_life_book(sid: str, request: Request, lang: str = "en") -> Response:
    """Download the comprehensive 35+ page Vedic Life Book PDF report."""
    with db_session() as db:
        user = auth.require_user(request, db)
        order = billing.has_paid_report(db, user, sku="life_book", topic="life_book")
        if not order:
            raise HTTPException(402, "The Comprehensive Life Book requires purchase before downloading.")

    session = _session(sid, request)
    try:
        data = pdf_report.life_book_pdf(session, brand=BRAND, site=SITE_URL, language=lang)
    except Exception as exc:
        raise HTTPException(500, f"Could not build the Life Book PDF: {exc}") from exc
    return _pdf_response(
        data, pdf_report.safe_filename(BRAND, "life-book", session.birth.name or "horoscope"))



@app.get("/api/pdf/fonts")
def pdf_fonts(request: Request) -> dict:
    """Whether this machine can render Devanagari in a PDF. Ops diagnostic."""
    with db_session() as db:
        auth.require_user(request, db)
    return pdf_report.pdf_font_report()


# --------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------

_ASSET_REF = re.compile(r'(/static/[\w./-]+\.(?:css|js))')


def _page(name: str) -> HTMLResponse:
    """Serve an HTML shell with its CSS and JS references version-stamped.

    Without this a deploy is invisible to anyone holding a cached stylesheet:
    the filenames never change, so the browser has no reason to re-fetch, and
    the site looks unchanged however many times it is redeployed. The stamp is
    the newest mtime in the static directory, so it moves on every release and
    only then. The HTML itself must not be cached, or it would keep handing out
    the old stamp.
    """
    version = str(max(int(p.stat().st_mtime) for p in STATIC.glob("*")))
    html = (STATIC / name).read_text(encoding="utf-8")
    html = _ASSET_REF.sub(rf"\1?v={version}", html)
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


@app.get("/")
def index() -> HTMLResponse:
    return _page("index.html")


@app.get("/admin")
def admin_page() -> HTMLResponse:
    """Operator console. The page itself is public — every endpoint behind it
    is gated by the `admin` dependency, so serving the shell reveals nothing."""
    return _page("admin.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
