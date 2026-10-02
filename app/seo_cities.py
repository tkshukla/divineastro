"""The curated city list behind the public Panchang / Rahu Kaal / Choghadiya pages.

Why a hand-kept list instead of the GeoNames index in geo.py: every entry here
becomes a public URL in the sitemap, so the set has to be small, stable and
deliberately chosen — a city that disappears from a dump refresh would turn an
indexed page into a 404. It also keeps these pages independent of the ~55k-row
city index, which is not even present in a fresh checkout (data/ is fetched by
tools/fetch_data.py).

Coordinates are city-centre values to four decimals; at Indian latitudes a
kilometre of error moves sunrise by well under ten seconds, so this precision is
far more than the minute-resolution times on the pages need. All of India keeps
one zone, so every entry is Asia/Kolkata.

The slug is part of the public URL. Never rename one — add a redirect instead.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class City:
    slug: str
    name: str
    name_hi: str
    state: str
    latitude: float
    longitude: float
    timezone: str = "Asia/Kolkata"

    @property
    def label(self) -> str:
        return f"{self.name}, {self.state}"


CITIES: tuple[City, ...] = (
    City("new-delhi", "New Delhi", "नई दिल्ली", "Delhi", 28.6139, 77.2090),
    City("mumbai", "Mumbai", "मुंबई", "Maharashtra", 19.0760, 72.8777),
    City("kolkata", "Kolkata", "कोलकाता", "West Bengal", 22.5726, 88.3639),
    City("chennai", "Chennai", "चेन्नई", "Tamil Nadu", 13.0827, 80.2707),
    City("bengaluru", "Bengaluru", "बेंगलुरु", "Karnataka", 12.9716, 77.5946),
    City("hyderabad", "Hyderabad", "हैदराबाद", "Telangana", 17.3850, 78.4867),
    City("ahmedabad", "Ahmedabad", "अहमदाबाद", "Gujarat", 23.0225, 72.5714),
    City("pune", "Pune", "पुणे", "Maharashtra", 18.5204, 73.8567),
    City("jaipur", "Jaipur", "जयपुर", "Rajasthan", 26.9124, 75.7873),
    City("lucknow", "Lucknow", "लखनऊ", "Uttar Pradesh", 26.8467, 80.9462),
    City("kanpur", "Kanpur", "कानपुर", "Uttar Pradesh", 26.4499, 80.3319),
    City("nagpur", "Nagpur", "नागपुर", "Maharashtra", 21.1458, 79.0882),
    City("indore", "Indore", "इंदौर", "Madhya Pradesh", 22.7196, 75.8577),
    City("bhopal", "Bhopal", "भोपाल", "Madhya Pradesh", 23.2599, 77.4126),
    City("patna", "Patna", "पटना", "Bihar", 25.5941, 85.1376),
    City("varanasi", "Varanasi", "वाराणसी", "Uttar Pradesh", 25.3176, 82.9739),
    City("prayagraj", "Prayagraj", "प्रयागराज", "Uttar Pradesh", 25.4358, 81.8463),
    City("surat", "Surat", "सूरत", "Gujarat", 21.1702, 72.8311),
    City("vadodara", "Vadodara", "वडोदरा", "Gujarat", 22.3072, 73.1812),
    City("chandigarh", "Chandigarh", "चंडीगढ़", "Chandigarh", 30.7333, 76.7794),
    City("amritsar", "Amritsar", "अमृतसर", "Punjab", 31.6340, 74.8723),
    City("dehradun", "Dehradun", "देहरादून", "Uttarakhand", 30.3165, 78.0322),
    City("haridwar", "Haridwar", "हरिद्वार", "Uttarakhand", 29.9457, 78.1642),
    City("noida", "Noida", "नोएडा", "Uttar Pradesh", 28.5355, 77.3910),
    City("gurugram", "Gurugram", "गुरुग्राम", "Haryana", 28.4595, 77.0266),
    City("bhubaneswar", "Bhubaneswar", "भुवनेश्वर", "Odisha", 20.2961, 85.8245),
    City("guwahati", "Guwahati", "गुवाहाटी", "Assam", 26.1445, 91.7362),
    City("ranchi", "Ranchi", "रांची", "Jharkhand", 23.3441, 85.3096),
    City("kochi", "Kochi", "कोच्चि", "Kerala", 9.9312, 76.2673),
    City("visakhapatnam", "Visakhapatnam", "विशाखापत्तनम", "Andhra Pradesh", 17.6868, 83.2185),
)

BY_SLUG: dict[str, City] = {c.slug: c for c in CITIES}

# What the bare /panchang, /rahu-kaal and /choghadiya URLs show. The capital is
# the least surprising default and the one most other almanacs use.
DEFAULT: City = BY_SLUG["new-delhi"]


def get(slug: str) -> City | None:
    return BY_SLUG.get(slug.lower())
