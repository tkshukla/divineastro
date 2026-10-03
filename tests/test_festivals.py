"""The vrat / festival engine (DIVASTRO-111) against Drik Panchang, New Delhi 2026.

Every reference row below was read from drikpanchang.com's own pages for New
Delhi (geoname-id 1261481) on 2026-10-03:

  /vrats/ekadashidates.html + each /ekadashis/<slug>/... page  (Smarta)
  /vrats/pradoshdates.html, /vrats/sankashti-chaturthi-dates.html,
  /vrats/vinayaka-chaturthi-dates.html, /vrats/purnimasidates.html,
  /vrats/amavasyadates.html, /vrats/masik-shivaratri-dates.html,
  /vrats/masik-durgashtami-dates.html, and the /festivals/... pages for each
  major festival (see FESTIVAL_REF), corroborated where noted.

Dates must match exactly; times within TOL_MIN minutes (Drik rounds to the
minute and uses a 212 m elevation for Delhi, we use sea level).

    ~/.venvs/divineastro/bin/python -u -m tests.test_festivals
"""

from __future__ import annotations

import datetime as dt
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.astro import festivals as F  # noqa: E402

TOL_MIN = 3
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# --------------------------------------------------------------------------
# Reference data (Drik Panchang, New Delhi, 2026; 24-hour clock)
# --------------------------------------------------------------------------

# fast date, name, parana date, parana start, parana end
EKADASHI = [
    ("2026-01-14", "Shattila Ekadashi", "2026-01-15", "07:15", "09:21"),
    ("2026-01-29", "Jaya Ekadashi", "2026-01-30", "07:10", "09:20"),
    ("2026-02-13", "Vijaya Ekadashi", "2026-02-14", "07:00", "09:14"),
    ("2026-02-27", "Amalaki Ekadashi", "2026-02-28", "06:47", "09:06"),
    ("2026-03-15", "Papmochani Ekadashi", "2026-03-16", "06:30", "08:54"),
    ("2026-03-29", "Kamada Ekadashi", "2026-03-30", "06:14", "07:09"),
    ("2026-04-13", "Varuthini Ekadashi", "2026-04-14", "06:54", "08:31"),
    ("2026-04-27", "Mohini Ekadashi", "2026-04-28", "05:43", "08:21"),
    ("2026-05-13", "Apara Ekadashi", "2026-05-14", "05:31", "08:14"),
    ("2026-05-27", "Padmini Ekadashi", "2026-05-28", "05:25", "07:56"),
    ("2026-06-11", "Parama Ekadashi", "2026-06-12", "05:23", "08:10"),
    ("2026-06-25", "Nirjala Ekadashi", "2026-06-26", "05:25", "08:13"),
    ("2026-07-10", "Yogini Ekadashi", "2026-07-11", "13:50", "16:36"),
    ("2026-07-25", "Devshayani Ekadashi", "2026-07-26", "05:39", "08:22"),
    ("2026-08-09", "Kamika Ekadashi", "2026-08-10", "05:47", "08:00"),
    ("2026-08-23", "Shravana Putrada Ekadashi", "2026-08-24", "13:41", "16:16"),
    ("2026-09-07", "Aja Ekadashi", "2026-09-08", "06:02", "08:33"),
    ("2026-09-22", "Parsva Ekadashi", "2026-09-23", "06:10", "08:35"),
    ("2026-10-06", "Indira Ekadashi", "2026-10-07", "06:17", "08:38"),
    ("2026-10-22", "Papankusha Ekadashi", "2026-10-23", "06:27", "08:42"),
    ("2026-11-05", "Rama Ekadashi", "2026-11-06", "06:37", "08:48"),
    ("2026-11-20", "Devutthana Ekadashi", "2026-11-21", "13:11", "15:18"),
    ("2026-12-04", "Utpanna Ekadashi", "2026-12-05", "06:59", "09:04"),
    ("2026-12-20", "Mokshada Ekadashi", "2026-12-21", "07:10", "09:13"),
]

# Pradosh vrat: date, puja window as Drik prints it (cut to the Trayodashi).
PRADOSH = [
    ("2026-01-01", "17:35", "20:19"), ("2026-01-16", "17:47", "20:29"),
    ("2026-01-30", "17:59", "20:37"), ("2026-02-14", "18:10", "20:44"),
    ("2026-03-01", "18:21", "19:09"), ("2026-03-16", "18:30", "20:54"),
    ("2026-03-30", "18:38", "20:57"), ("2026-04-15", "18:47", "21:00"),
    ("2026-04-28", "18:54", "21:04"), ("2026-05-14", "19:04", "21:09"),
    ("2026-05-28", "19:12", "21:15"), ("2026-06-12", "19:36", "21:20"),
    ("2026-06-27", "19:23", "21:23"), ("2026-07-12", "19:22", "21:24"),
    ("2026-07-26", "19:16", "21:21"), ("2026-08-10", "19:05", "21:14"),
    ("2026-08-25", "18:51", "21:04"), ("2026-09-08", "18:35", "20:52"),
    ("2026-09-24", "18:16", "20:39"), ("2026-10-08", "17:59", "20:27"),
    ("2026-10-23", "17:44", "20:16"), ("2026-11-06", "17:33", "20:09"),
    ("2026-11-22", "17:25", "20:06"), ("2026-12-06", "17:24", "20:07"),
    ("2026-12-21", "17:36", "20:13"),
]

# Sankashti Chaturthi: date, moonrise.
SANKASHTI = [
    ("2026-01-06", "20:59"), ("2026-02-05", "21:39"), ("2026-03-06", "21:18"),
    ("2026-04-05", "21:58"), ("2026-05-05", "22:35"), ("2026-06-03", "22:04"),
    ("2026-07-03", "21:53"), ("2026-08-02", "21:24"), ("2026-08-31", "20:29"),
    ("2026-09-29", "19:44"), ("2026-10-29", "20:17"), ("2026-11-27", "20:18"),
    ("2026-12-26", "20:19"),
]

# Vinayaka Chaturthi: date, madhyahna puja window (cut to the Chaturthi).
VINAYAKA = [
    ("2026-01-22", "11:29", "13:37"), ("2026-02-21", "11:27", "13:00"),
    ("2026-03-22", "11:15", "13:41"), ("2026-04-20", "11:02", "13:38"),
    ("2026-05-20", "10:56", "11:06"), ("2026-06-18", "10:58", "13:46"),
    ("2026-07-17", "11:05", "13:50"), ("2026-08-16", "11:06", "13:44"),
    ("2026-09-14", "11:02", "13:31"), ("2026-10-14", "10:58", "13:16"),
    ("2026-11-13", "11:01", "13:10"), ("2026-12-13", "11:13", "13:17"),
]

PURNIMA_VRAT = ["2026-01-03", "2026-02-01", "2026-03-03", "2026-04-01", "2026-05-01",
                "2026-05-30", "2026-06-29", "2026-07-29", "2026-08-27", "2026-09-26",
                "2026-10-25", "2026-11-24", "2026-12-23"]

# Drik's "<month> Amavasya" (sunrise) dates - the snan/daan day.
AMAVASYA = ["2026-01-18", "2026-02-17", "2026-03-19", "2026-04-17", "2026-05-16",
            "2026-06-15", "2026-07-14", "2026-08-12", "2026-09-11", "2026-10-10",
            "2026-11-09", "2026-12-08"]

# Masik Shivratri: date, nishita window.
SHIVRATRI = [
    ("2026-01-16", "00:04", "00:58"), ("2026-02-15", "00:09", "01:01"),
    ("2026-03-17", "00:05", "00:53"), ("2026-04-15", "23:59", "00:43"),
    ("2026-05-15", "23:57", "00:38"), ("2026-06-13", "00:01", "00:41"),
    ("2026-07-12", "00:07", "00:47"), ("2026-08-11", "00:05", "00:48"),
    ("2026-09-09", "23:55", "00:41"), ("2026-10-08", "23:44", "00:33"),
    ("2026-11-07", "23:39", "00:31"), ("2026-12-07", "23:46", "00:40"),
]

DURGASHTAMI = ["2026-01-26", "2026-02-24", "2026-03-26", "2026-04-24", "2026-05-23",
               "2026-06-22", "2026-07-21", "2026-08-20", "2026-09-19", "2026-10-19",
               "2026-11-17", "2026-12-17"]

# Drik /vrats/masik-kalashtami-dates.html?year=2026 (New Delhi), incl. the
# adhika one (8 Jun) and Kalabhairav Jayanti (1 Dec). Nishita would give 9 Apr
# and 30 Nov; Pradosh gives all 13.
KALASHTAMI = ["2026-01-10", "2026-02-09", "2026-03-11", "2026-04-10", "2026-05-09",
              "2026-06-08", "2026-07-07", "2026-08-05", "2026-09-04", "2026-10-03",
              "2026-11-01", "2026-12-01", "2026-12-30"]

# Drik /vrats/skanda-sashti-dates.html?year=2026 (New Delhi), incl. adhika
# (21 May), Soora Samharam (15 Nov) and Subrahmanya Sashti (15 Dec).
SKANDA = ["2026-01-24", "2026-02-22", "2026-03-24", "2026-04-22", "2026-05-21",
          "2026-06-19", "2026-07-19", "2026-08-17", "2026-09-16", "2026-10-16",
          "2026-11-15", "2026-12-15"]


# Major festivals: key, date, {timing key: (start, end) | at}, source note.
# All Drik Panchang (New Delhi). "PK" = Prokerala (New Delhi) agrees on the date.
FESTIVAL_REF = [
    ("maha_shivratri", "2026-02-15", {"nishita": ("00:09", "01:01")}, "Drik; PK agrees"),
    ("ram_navami", "2026-03-26", {"madhyahna": ("11:13", "13:41")}, "Drik Smarta; PK agrees"),
    ("chaitra_navratri", "2026-03-19", {"ghatasthapana_abhijit": ("12:05", "12:53")},
     "Drik; PK agrees"),
    ("hanuman_jayanti", "2026-04-02", {}, "Drik; PK agrees"),
    ("akshaya_tritiya", "2026-04-19", {"puja": ("10:49", "12:20")}, "Drik; PK date agrees"),
    ("raksha_bandhan", "2026-08-28", {"rakhi": ("05:57", "09:48")}, "Drik; PK agrees"),
    ("janmashtami", "2026-09-04", {"nishita": ("23:57", "00:43")}, "Drik (Smarta); PK agrees"),
    ("ganesh_chaturthi", "2026-09-14", {"madhyahna": ("11:02", "13:31")}, "Drik; PK agrees"),
    ("navratri", "2026-10-11", {"ghatasthapana": ("06:19", "10:12"),
                                "ghatasthapana_abhijit": ("11:44", "12:31")}, "Drik; PK agrees"),
    ("dussehra", "2026-10-20", {"vijay": ("13:59", "14:45"), "aparahna": ("13:14", "15:30")},
     "Drik (PK says 21 Oct; Drik followed, see page note)"),
    ("karwa_chauth", "2026-10-29", {"karwa_puja": ("17:38", "18:56"), "moonrise": "20:17"},
     "Drik; news agree (PK says 30 Oct despite its own Chaturthi ending 29 Oct)"),
    ("holika_dahan", "2026-03-03", {"holika_dahan": ("18:22", "20:50")},
     "Drik 3 Mar 6:22-8:50 PM ('during Pradosh without Udaya Vyapini Purnima'); PK agrees"),
    ("ahoi_ashtami", "2026-11-01", {"karwa_puja": ("17:36", "18:54"), "moonrise": "23:40"},
     "Drik; PK date agrees"),
    ("dhanteras", "2026-11-06", {"dhanteras_puja": ("18:02", "19:57"),
                                 "pradosh_kaal": ("17:33", "20:09"), "vrishabha": ("18:02", "19:57")},
     "Drik; PK date agrees"),
    ("diwali", "2026-11-08", {"lakshmi_puja": ("17:54", "19:50"), "pradosh_kaal": ("17:31", "20:09"),
                              "vrishabha": ("17:54", "19:50")}, "Drik; PK agrees"),
    ("govardhan", "2026-11-10", {"pratah": ("06:40", "08:50")}, "Drik; PK agrees"),
    ("bhai_dooj", "2026-11-11", {"aparahna": ("13:10", "15:20")}, "Drik; PK agrees"),
    ("chhath", "2026-11-15", {"sandhya_arghya": "17:28", "usha_arghya": "06:44"},
     "Drik; PK date agrees"),
    ("ekadashi", "2026-11-20", {"parana": ("13:11", "15:18")}, "Devutthana; Drik; PK agrees"),
    ("makar_sankranti", "2026-01-14", {}, "Drik; PK date agrees (moment differs - omitted)"),
    ("vasant_panchami", "2026-01-23", {"puja": ("07:13", "12:33")}, "Drik"),
    ("guru_purnima", "2026-07-29", {}, "Drik; PK agrees"),
    ("sharad_purnima", "2026-10-25", {"moonrise": "17:00"}, "Drik; PK agrees"),
    # 2027
    ("diwali", "2027-10-29", {"lakshmi_puja": ("18:34", "19:05"), "pradosh_kaal": ("17:39", "20:13"),
                              "vrishabha": ("18:34", "20:30")}, "Drik 2027"),
    ("makar_sankranti", "2027-01-15", {}, "Drik 2027; PK agrees"),
    ("maha_shivratri", "2027-03-06", {}, "PK 2027"),
    ("ram_navami", "2027-04-15", {}, "PK 2027"),
    ("raksha_bandhan", "2027-08-17", {}, "PK 2027"),
    ("janmashtami", "2027-08-25", {}, "PK 2027"),
    ("ganesh_chaturthi", "2027-09-04", {}, "PK 2027"),
    # Festivals Drik's rate limit kept out of DRIK_YEARS: the widely published
    # 2025 dates and the 2027 web consensus (timeanddate, calendarlabs, samvat,
    # shubhpanchang, dekhopanchang - searched 2026-10-03).
    ("vasant_panchami", "2025-02-02", {}, "published 2025"),
    ("guru_purnima", "2025-07-10", {}, "published 2025"),
    ("sharad_purnima", "2025-10-06", {}, "published 2025"),
    ("karwa_chauth", "2025-10-10", {}, "published 2025"),
    ("govardhan", "2025-10-22", {}, "published 2025"),
    ("bhai_dooj", "2025-10-23", {}, "published 2025"),
    ("chhath", "2025-10-27", {}, "published 2025"),
    ("vasant_panchami", "2027-02-11", {}, "web consensus 2027"),
    ("guru_purnima", "2027-07-18", {}, "web consensus 2027"),
    ("sharad_purnima", "2027-10-15", {}, "web consensus 2027"),
    ("karwa_chauth", "2027-10-18", {}, "web consensus 2027"),
    ("govardhan", "2027-10-30", {}, "web consensus 2027"),
    ("bhai_dooj", "2027-10-31", {}, "web consensus 2027"),
    ("chhath", "2027-11-04", {}, "web consensus 2027"),

    # ---- Added after the Jivitputrika report (searched/fetched 2026-10-03).
    # "Drik" = drikpanchang.com New Delhi page (fetched, or its own search
    # snippet); "PK" = prokerala.com /astrology/panchang/2026.html agrees.
    ("jivitputrika", "2026-10-03", {},
     "Drik /vrats/jivitputrika/...?year=2026 (Ashtami 07:59 3 Oct - 05:51 4 Oct; no parana "
     "time); Prabhat Khabar, India TV, Punjab Kesari: nahay-khay 2 Oct, vrat 3 Oct, parana 4 Oct"),
    ("sakat_chauth", "2026-01-06", {"moonrise": "20:59"}, "Drik; PK agrees"),
    ("lohri", "2026-01-13", {}, "Drik ('one day before Makara Sankranti'); PK agrees"),
    ("mauni_amavasya", "2026-01-18", {}, "Drik; PK agrees"),
    ("sheetala_ashtami", "2026-03-11", {"puja": ("06:36", "18:27")}, "Drik; PK agrees"),
    ("gudi_padwa", "2026-03-19", {}, "Drik (Gudi Padwa and Ugadi); PK agrees"),
    ("gangaur", "2026-03-21", {}, "Drik; PK agrees"),
    ("vat_savitri", "2026-05-16", {}, "Drik; PK agrees"),
    ("ganga_dussehra", "2026-05-25", {},
     "Drik (adhika Jyeshtha Dashami); PK and Aaj Tak agree"),
    ("vat_purnima", "2026-06-29", {}, "Drik; PK agrees"),
    ("hariyali_teej", "2026-08-15", {}, "Drik; PK agrees"),
    ("nag_panchami", "2026-08-17", {}, "Drik (North India); PK agrees"),
    ("kajari_teej", "2026-08-31", {}, "Drik; PK agrees"),
    ("hal_shashthi", "2026-09-02", {}, "Drik; Amar Ujala agrees"),
    ("hartalika_teej", "2026-09-14", {"pratah": ("06:05", "07:06")}, "Drik; PK agrees"),
    ("rishi_panchami", "2026-09-15", {"madhyahna": ("11:02", "13:30")}, "Drik; PK agrees"),
    ("anant_chaturdashi", "2026-09-25", {"puja": ("06:11", "23:06")}, "Drik; PK agrees"),
    ("pitru_paksha", "2026-09-27", {"kutup": ("11:48", "12:36"), "rohina": ("12:36", "13:24"),
                                    "aparahna_kaal": ("13:24", "15:48")},
     "Drik Pratipada Shraddha page; PK agrees"),
    ("sarva_pitru_amavasya", "2026-10-10", {"kutup": ("11:45", "12:31")},
     "Drik Amavasya Shraddha; Pitru Paksha listings (astrovachmi, sanatanajourney) agree"),
    ("narak_chaturdashi", "2026-11-08", {"abhyang": ("05:41", "06:38")}, "Drik; PK agrees"),
    ("tulsi_vivah", "2026-11-21", {}, "Drik; PK agrees"),
    ("kartik_purnima", "2026-11-24", {}, "Drik; PK agrees"),
    ("dev_deepawali", "2026-11-24", {}, "Drik (Varanasi); PK agrees"),
    # 2027 and the years where the candidate rules disagree.
    ("rishi_panchami", "2027-09-04", {"madhyahna": ("12:25", "13:36")},
     "Drik New Delhi 2027 (Madhyahna, earlier day - not the 5 Sep sunrise day)"),
    ("tulsi_vivah", "2027-11-11", {}, "Drik New Delhi 2027 (Dwadashi at sunrise)"),
    ("kartik_purnima", "2027-11-14", {}, "Drik New Delhi 2027 (upavasa 13 Nov)"),
    ("dev_deepawali", "2027-11-13", {}, "Drik 2027 (Varanasi; Purnima in Pradosh)"),
    ("sarva_pitru_amavasya", "2027-09-29", {"kutup": ("11:47", "12:35"),
                                            "rohina": ("12:35", "13:23"),
                                            "aparahna_kaal": ("13:23", "15:46")},
     "Drik New Delhi 2027 (Aparahna - not the 30 Sep sunrise day)"),
    ("sheetala_ashtami", "2027-03-30", {"puja": ("06:14", "18:38")}, "Drik 2027"),
    ("kajari_teej", "2027-08-20", {}, "samvat.in 2027"),
    ("narak_chaturdashi", "2027-10-28", {}, "samvat.in, drrpsharma 2027"),
    ("vat_savitri", "2025-05-26", {}, "Drik 2025 (Madhyahna - not the 27 May sunrise day)"),
    ("vat_purnima", "2025-06-10", {}, "Drik 2025 (Madhyahna, earlier day)"),
    ("ganga_dussehra", "2022-06-09", {}, "Drik 2022 page; India TV agrees"),
    ("hal_shashthi", "2023-09-05", {}, "Times Now Hindi 2023 (not the 4 Sep sayahna day)"),
]

# Jivitputrika: Drik's own New Delhi pages, ?year=YYYY (fetched 2026-10-03).
# 2023 is the year that rules out "Ashtami at sunrise" (6 Oct, not 7 Oct) and
# 2022/2029 the ones that rule out "Ashtami at Pradosh/sunset" (18 Sep, 1 Oct).
# Hartalika 2029: Tritiya at sunrise for 4 minutes, still the day (Drik).
NEW_DRIK_YEARS = {
    "jivitputrika": ["2022-09-18", "2023-10-06", "2024-09-25", "2026-10-03", "2029-10-01"],
    "hartalika_teej": ["2026-09-14", "2029-09-11"],
}


# Drik Panchang's own date for each festival, New Delhi: 2022-2030 read from
# each festival page with ?year=YYYY, plus the 'in Recent Years' lists (to 2033)
# on the Diwali, Dhanteras, Akshaya Tritiya, Janmashtami and Ganesh pages
# (2026-10-03; Drik then rate-limited the rest). These pin the dating RULES
# across many tithi configurations (vriddhi, kshaya, Bhadra, Rohini, Shravana).
DRIK_YEARS = {
    "makar_sankranti": [
        "2022-01-14", "2023-01-15", "2024-01-15", "2025-01-14",
        "2026-01-14", "2027-01-15", "2028-01-15", "2029-01-14",
        "2030-01-14",
    ],
    "maha_shivratri": [
        "2022-03-01", "2023-02-18", "2024-03-08", "2025-02-26",
        "2026-02-15", "2027-03-06", "2028-02-23", "2029-02-11",
        "2030-03-02",
    ],
    "holika_dahan": [
        "2022-03-17", "2023-03-07", "2024-03-24", "2025-03-13",
        "2026-03-03", "2027-03-21", "2028-03-10", "2029-02-28",
        "2030-03-19",
    ],
    "ram_navami": [
        "2022-04-10", "2023-03-30", "2024-04-17", "2025-04-06",
        "2026-03-26", "2027-04-15", "2028-04-03", "2029-04-23",
        "2030-04-12",
    ],
    "hanuman_jayanti": [
        "2022-04-16", "2023-04-06", "2024-04-23", "2025-04-12",
        "2026-04-02", "2027-04-20", "2028-04-09", "2029-04-28",
        "2030-04-18",
    ],
    "akshaya_tritiya": [
        "2022-05-03", "2023-04-22", "2024-05-10", "2025-04-30",
        "2026-04-19", "2027-05-09", "2028-04-27", "2029-05-16",
        "2030-05-05", "2031-04-24", "2032-05-12", "2033-05-01",
    ],
    "raksha_bandhan": [
        "2022-08-11", "2023-08-30", "2024-08-19", "2025-08-09",
        "2026-08-28", "2027-08-17", "2028-08-05", "2029-08-23",
        "2030-08-13",
    ],
    "janmashtami": [
        "2022-08-18", "2023-09-06", "2024-08-26", "2025-08-15",
        "2026-09-04", "2027-08-25", "2028-08-13", "2029-09-01",
        "2030-08-21", "2031-08-09", "2032-08-28", "2033-08-17",
    ],
    "ganesh_chaturthi": [
        "2022-08-31", "2023-09-19", "2024-09-07", "2025-08-27",
        "2026-09-14", "2027-09-04", "2028-08-23", "2029-09-11",
        "2030-09-01", "2031-09-20", "2032-09-08", "2033-08-28",
    ],
    "navratri": [
        "2022-09-26", "2023-10-15", "2024-10-03", "2025-09-22",
        "2026-10-11", "2027-09-30", "2028-09-19", "2029-10-08",
        "2030-09-28",
    ],
    "chaitra_navratri": [
        "2022-04-02", "2023-03-22", "2024-04-09", "2025-03-30",
        "2026-03-19", "2027-04-07", "2028-03-27", "2029-04-14",
        "2030-04-03",
    ],
    "dussehra": [
        "2022-10-05", "2023-10-24", "2024-10-12", "2025-10-02",
        "2026-10-20", "2027-10-09", "2028-09-27",
    ],
    "ahoi_ashtami": [
        "2022-10-17", "2023-11-05", "2024-10-24", "2025-10-13",
        "2026-11-01", "2027-10-22", "2028-10-11", "2029-10-30",
        "2030-10-19",
    ],
    "dhanteras": [
        "2023-11-10", "2024-10-29", "2025-10-18", "2026-11-06",
        "2027-10-27", "2028-10-15", "2029-11-04", "2030-10-24",
        "2031-11-12", "2032-10-31", "2033-10-20",
    ],
    "diwali": [
        "2023-11-12", "2024-11-01", "2025-10-20", "2026-11-08",
        "2027-10-29", "2028-10-17", "2029-11-05", "2030-10-26",
        "2031-11-14", "2032-11-02", "2033-10-22",
    ],
}
DRIK_YEARS.update(NEW_DRIK_YEARS)

# --------------------------------------------------------------------------

def _hm(iso: str) -> int:
    t = dt.datetime.fromisoformat(iso)
    return t.hour * 60 + t.minute + (1 if t.second >= 30 else 0)


def _near(iso: str | None, ref: str) -> bool:
    if not iso:
        return False
    h, m = map(int, ref.split(":"))
    diff = abs(_hm(iso) - (h * 60 + m)) % 1440
    return min(diff, 1440 - diff) <= TOL_MIN


def _timing(o: dict, key: str) -> dict | None:
    return next((t for t in o["timings"] if t["key"] == key), None)


def _dates(obs: list[dict], key: str) -> list[str]:
    return [o["date"] for o in obs if o["key"] == key]


def recurring(obs: list[dict]) -> None:
    by_key = lambda k: {o["date"]: o for o in obs if o["key"] == k}  # noqa: E731

    print("1. Ekadashi (Smarta) dates, names and parana")
    eks = by_key("ekadashi")
    check("24 Ekadashis in 2026", len(eks) == 24, str(len(eks)))
    for date, name, pdate, ps, pe in EKADASHI:
        o = eks.get(date)
        check(f"{name} on {date}", o is not None and o["name_en"] == name,
              o["name_en"] if o else f"not on that date; ours: {sorted(eks)}")
        if not o:
            continue
        p = _timing(o, "parana")
        ok = (p is not None and p["date"] == pdate and _near(p["start"], ps)
              and _near(p["end"], pe))
        check(f"  parana {pdate} {ps}-{pe}", ok,
              f"{p['date']} {p['start'][11:16]}-{p['end'][11:16]}" if p else "missing")

    print("2. Pradosh vrat: dates and pradosh kaal")
    pr = by_key("pradosh")
    check("pradosh dates", sorted(pr) == [d for d, *_ in PRADOSH], str(sorted(pr)))
    for d, s, e in PRADOSH:
        t = _timing(pr[d], "pradosh") if d in pr else None
        check(f"  {d} {s}-{e}", bool(t and _near(t["start"], s) and _near(t["end"], e)),
              f"{t['start'][11:16]}-{t['end'][11:16]}" if t else "missing")

    print("3. Sankashti Chaturthi: dates and moonrise")
    sk = by_key("sankashti")
    check("sankashti dates", sorted(sk) == [d for d, _ in SANKASHTI], str(sorted(sk)))
    for d, m in SANKASHTI:
        t = _timing(sk[d], "moonrise") if d in sk else None
        check(f"  {d} moonrise {m}", bool(t and _near(t["at"], m)),
              t["at"][11:16] if t else "missing")

    print("4. Vinayaka Chaturthi: dates and madhyahna")
    vk = by_key("vinayaka")
    check("vinayaka dates", sorted(vk) == [d for d, *_ in VINAYAKA], str(sorted(vk)))
    for d, s, e in VINAYAKA:
        t = _timing(vk[d], "madhyahna") if d in vk else None
        check(f"  {d} {s}-{e}", bool(t and _near(t["start"], s) and _near(t["end"], e)),
              f"{t['start'][11:16]}-{t['end'][11:16]}" if t else "missing")

    print("5. Purnima vrat, Amavasya, Masik Durgashtami")
    check("purnima vrat dates", _dates(obs, "purnima") == PURNIMA_VRAT, str(_dates(obs, "purnima")))
    check("amavasya dates", _dates(obs, "amavasya") == AMAVASYA, str(_dates(obs, "amavasya")))
    check("durgashtami dates", _dates(obs, "durgashtami") == DURGASHTAMI,
          str(_dates(obs, "durgashtami")))

    print("6. Masik Shivratri: dates and nishita kaal")
    ms = by_key("masik_shivratri")
    check("masik shivratri dates", sorted(ms) == [d for d, *_ in SHIVRATRI], str(sorted(ms)))
    for d, s, e in SHIVRATRI:
        t = _timing(ms[d], "nishita") if d in ms else None
        check(f"  {d} {s}-{e}", bool(t and _near(t["start"], s) and _near(t["end"], e)),
              f"{t['start'][11:16]}-{t['end'][11:16]}" if t else "missing")

    print("6b. Kalashtami and Skanda Shashthi dates")
    check("kalashtami dates", _dates(obs, "kalashtami") == KALASHTAMI, str(_dates(obs, "kalashtami")))
    check("skanda shashthi dates", _dates(obs, "skanda_shashthi") == SKANDA,
          str(_dates(obs, "skanda_shashthi")))


def festivals(obs: list[dict]) -> None:
    print("7. Major festivals: dates and puja timings")
    pools = {2026: obs}
    for key, date, timings, src in FESTIVAL_REF:
        y = int(date[:4])
        if y not in pools:
            pools[y] = F.observances(dt.date(y, 1, 1), dt.date(y, 12, 31))
        pool = pools[y]
        mine = [o for o in pool if o["key"] == key and o["date"] == date]
        others = [o["date"] for o in pool if o["key"] == key]
        check(f"{key} {date} ({src})", bool(mine), f"ours: {others}")
        if not mine:
            continue
        for tkey, ref in timings.items():
            t = _timing(mine[0], tkey)
            if isinstance(ref, str):
                ok = bool(t and _near(t.get("at"), ref))
                got = t.get("at", "")[11:16] if t else "missing"
            else:
                ok = bool(t and _near(t.get("start"), ref[0]) and _near(t.get("end"), ref[1]))
                got = f"{t['start'][11:16]}-{t['end'][11:16]}" if t else "missing"
            check(f"  {tkey} {ref}", ok, got)


def rules_and_flags(obs: list[dict]) -> None:
    print("8. Omitted observances never appear; every entry is complete")
    keys = {o["key"] for o in obs}
    for k in F.OMITTED:
        check(f"omitted '{k}' not in output", k not in keys)
    for (k, tk) in F.OMITTED_TIMINGS:
        hit = [o for o in obs if o["key"] == k and any(t["key"] == tk for t in o["timings"])]
        check(f"omitted timing {k}/{tk} not in output", not hit)
    for o in obs:
        if not (o["name_en"] and o["name_hi"] and o["rule_en"] and o["rule_hi"]):
            check(f"{o['key']} {o['date']} has names and rule text", False)
            break
    else:
        check("every observance has EN/HI names and a rule", True)
    hi = [o for o in obs if not any("\u0900" <= c <= "\u097f" for c in o["name_hi"])]
    check("Hindi names are Devanagari", not hi, str([o["key"] for o in hi][:3]))
    check("sorted by date", [o["date"] for o in obs] == sorted(o["date"] for o in obs))
    majors = {o["slug"] for o in obs if o["major"]}
    check("major festivals carry a page slug", None not in majors)

    print("9. API helpers: range, single day, another city")
    day = F.on(dt.date(2026, 10, 22))
    check("on(22 Oct 2026) -> Papankusha Ekadashi",
          [o["name_en"] for o in day] == ["Papankusha Ekadashi"], str([o["name_en"] for o in day]))
    rng = F.observances(dt.date(2026, 12, 25), dt.date(2027, 1, 20))
    check("range across a year boundary", any(o["date"].startswith("2027") for o in rng)
          and any(o["date"].startswith("2026") for o in rng))
    mum = F.observances(dt.date(2026, 11, 1), dt.date(2026, 11, 30), 19.076, 72.8777,
                        "Asia/Kolkata")
    d = next(o for o in mum if o["key"] == "diwali")
    check("Mumbai Diwali 8 Nov with its own (later) pradosh",
          d["date"] == "2026-11-08" and _timing(d, "pradosh_kaal")["start"][11:16] > "17:45",
          _timing(d, "pradosh_kaal")["start"])

    print("9b. The bug report: Jivitputrika on 3 Oct 2026")
    day = F.on(dt.date(2026, 10, 3))
    names = [o["name_en"] for o in day]
    check("on(3 Oct 2026) -> Jivitputrika Vrat (Jitiya) first, then Kalashtami",
          names == ["Jivitputrika Vrat (Jitiya)", "Kalashtami"], str(names))
    j = day[0] if day else {}
    check("  Hindi name जीवित्पुत्रिका व्रत (जितिया), slug jivitputrika, no parana time",
          j.get("name_hi") == "जीवित्पुत्रिका व्रत (जितिया)" and j.get("slug") == "jivitputrika"
          and not j.get("timings"), str(j.get("timings")))
    patna = [o["key"] for o in F.on(dt.date(2026, 10, 3), 25.5941, 85.1376, "Asia/Kolkata")]
    check("  Patna (another city) also has it on 3 Oct", "jivitputrika" in patna, str(patna))
    h29 = [o for o in F.observances(dt.date(2029, 9, 1), dt.date(2029, 9, 30))
           if o["key"] == "hartalika_teej"]
    t = _timing(h29[0], "pratah") if h29 else None
    check("Hartalika 2029: 11 Sep, Pratahkala 06:04-06:08 (Tritiya 4 minutes past sunrise)",
          bool(t and h29[0]["date"] == "2029-09-11" and _near(t["start"], "06:04")
               and _near(t["end"], "06:08")), str(t))
    for y, ref in ((2026, ("17:08", "19:47")), (2027, ("17:11", "19:48"))):
        vns = [o for o in F.observances(dt.date(y, 11, 1), dt.date(y, 11, 30), 25.3176, 82.9739,
                                        "Asia/Kolkata") if o["key"] == "dev_deepawali"]
        t = _timing(vns[0], "pradosh_kaal") if vns else None
        check(f"Dev Deepawali {y}, Varanasi pradoshkal {ref[0]}-{ref[1]} (Drik prints Varanasi)",
              bool(t and _near(t["start"], ref[0]) and _near(t["end"], ref[1])), str(t))


def multi_year() -> None:
    print("10. Festival dates 2022-2033 against Drik Panchang (the dating rules)")
    by_year: dict[int, list[dict]] = {}
    for key, dates in DRIK_YEARS.items():
        bad = []
        for date in dates:
            y = int(date[:4])
            if y not in by_year:
                # The full engine, OMITTED included - a switched-off festival's
                # date is still checked here, it is only kept off the pages.
                saved = dict(F.OMITTED)
                F.OMITTED.clear()
                F._year.cache_clear()
                try:
                    by_year[y] = list(F.observances(dt.date(y, 1, 1), dt.date(y, 12, 31)))
                finally:
                    F.OMITTED.update(saved)
                    F._year.cache_clear()
            ours = [o["date"] for o in by_year[y] if o["key"] == key]
            if date not in ours:
                bad.append(f"{date} (ours {ours})")
        check(f"{key}: {len(dates)} years", not bad, "; ".join(bad))


def main() -> int:
    t0 = time.time()
    obs = F.observances(dt.date(2026, 1, 1), dt.date(2026, 12, 31))
    print(f"(2026 computed in {time.time() - t0:.2f}s, {len(obs)} observances)")
    check("first computation of a year < 1 s", time.time() - t0 < 1.0)
    recurring(obs)
    festivals(obs)
    rules_and_flags(obs)
    multi_year()
    print()
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1
    print("all green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
