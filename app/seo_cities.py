"""The curated city list behind the public Panchang / Rahu Kaal / Choghadiya pages.

Why a hand-kept list instead of the GeoNames index in geo.py: every entry here
becomes a public URL in the sitemap, so the set has to be small, stable and
deliberately chosen — a city that disappears from a dump refresh would turn an
indexed page into a 404. It also keeps these pages independent of the ~55k-row
city index, which is not even present in a fresh checkout (data/ is fetched by
tools/fetch_data.py).

Coordinates are city-centre values to four decimals; at Indian latitudes a
kilometre of error moves sunrise by well under ten seconds, so this precision is
far more than the minute-resolution times on the pages need. `name_hi` is the
city's usual Devanagari spelling, shown on the /hi/ pages; the regional
languages' spellings are in seo_city_names.py (city_name / state_name / place
read both). All of India keeps one zone, so every entry is Asia/Kolkata.

The slug is part of the public URL. Never rename one — add a redirect instead.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import seo_city_names as _names


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
    # DIVASTRO-106: the remaining state capitals, every 2011-census million-plus
    # agglomeration (Vasai-Virar excepted: it is inside the Mumbai region and its
    # times match Mumbai's to the second), major tier-2 cities and the big
    # pilgrimage towns. Coordinates are the GeoNames cities5000 record for the
    # place — the same data the app's own city search (geo.py) returns, so a
    # visitor who follows the CTA and types the city gets the same times. Each
    # was also checked against an independently recalled city-centre value
    # (all within 8 km, i.e. under 20 seconds of sunrise).
    # Exception: Somnath is the temple; GeoNames has only neighbouring Veraval.
    # Kurukshetra is the GeoNames "Thanesar" record, the town proper.
    # New entries go at the end; order here is not display order (by_state is).
    City("thane", "Thane", "ठाणे", "Maharashtra", 19.1970, 72.9635),
    City("navi-mumbai", "Navi Mumbai", "नवी मुंबई", "Maharashtra", 19.0368, 73.0158),
    City("nashik", "Nashik", "नासिक", "Maharashtra", 19.9973, 73.7910),
    City("chhatrapati-sambhajinagar", "Chhatrapati Sambhajinagar", "छत्रपति संभाजीनगर",
         "Maharashtra", 19.8776, 75.3423),
    City("solapur", "Solapur", "सोलापुर", "Maharashtra", 17.6715, 75.9104),
    City("kolhapur", "Kolhapur", "कोल्हापुर", "Maharashtra", 16.6956, 74.2317),
    City("amravati", "Amravati", "अमरावती", "Maharashtra", 20.9333, 77.7500),
    City("shirdi", "Shirdi", "शिरडी", "Maharashtra", 19.7662, 74.4774),
    City("rajkot", "Rajkot", "राजकोट", "Gujarat", 22.2916, 70.7932),
    City("bhavnagar", "Bhavnagar", "भावनगर", "Gujarat", 21.7629, 72.1533),
    City("jamnagar", "Jamnagar", "जामनगर", "Gujarat", 22.4729, 70.0667),
    City("gandhinagar", "Gandhinagar", "गांधीनगर", "Gujarat", 23.2167, 72.6833),
    City("dwarka", "Dwarka", "द्वारका", "Gujarat", 22.2394, 68.9678),
    City("somnath", "Somnath", "सोमनाथ", "Gujarat", 20.8880, 70.4012),
    City("jodhpur", "Jodhpur", "जोधपुर", "Rajasthan", 26.2684, 73.0059),
    City("udaipur", "Udaipur", "उदयपुर", "Rajasthan", 24.5858, 73.7135),
    City("kota", "Kota", "कोटा", "Rajasthan", 25.1825, 75.8391),
    City("ajmer", "Ajmer", "अजमेर", "Rajasthan", 26.4521, 74.6387),
    City("bikaner", "Bikaner", "बीकानेर", "Rajasthan", 28.0176, 73.3149),
    City("agra", "Agra", "आगरा", "Uttar Pradesh", 27.1833, 78.0167),
    City("ghaziabad", "Ghaziabad", "गाज़ियाबाद", "Uttar Pradesh", 28.6654, 77.4391),
    City("meerut", "Meerut", "मेरठ", "Uttar Pradesh", 28.9800, 77.7064),
    City("bareilly", "Bareilly", "बरेली", "Uttar Pradesh", 28.3668, 79.4317),
    City("aligarh", "Aligarh", "अलीगढ़", "Uttar Pradesh", 27.8815, 78.0746),
    City("moradabad", "Moradabad", "मुरादाबाद", "Uttar Pradesh", 28.8389, 78.7768),
    City("gorakhpur", "Gorakhpur", "गोरखपुर", "Uttar Pradesh", 26.7663, 83.3689),
    City("saharanpur", "Saharanpur", "सहारनपुर", "Uttar Pradesh", 29.9679, 77.5452),
    City("ayodhya", "Ayodhya", "अयोध्या", "Uttar Pradesh", 26.7991, 82.2047),
    City("mathura", "Mathura", "मथुरा", "Uttar Pradesh", 27.5035, 77.6722),
    City("vrindavan", "Vrindavan", "वृंदावन", "Uttar Pradesh", 27.5811, 77.6966),
    City("jhansi", "Jhansi", "झांसी", "Uttar Pradesh", 25.4589, 78.5799),
    City("faridabad", "Faridabad", "फ़रीदाबाद", "Haryana", 28.4112, 77.3132),
    City("kurukshetra", "Kurukshetra", "कुरुक्षेत्र", "Haryana", 29.9732, 76.8321),
    City("ludhiana", "Ludhiana", "लुधियाना", "Punjab", 30.9120, 75.8538),
    City("jalandhar", "Jalandhar", "जालंधर", "Punjab", 31.3256, 75.5792),
    City("patiala", "Patiala", "पटियाला", "Punjab", 30.3362, 76.3922),
    City("rishikesh", "Rishikesh", "ऋषिकेश", "Uttarakhand", 30.1078, 78.2926),
    City("shimla", "Shimla", "शिमला", "Himachal Pradesh", 31.1044, 77.1666),
    City("jammu", "Jammu", "जम्मू", "Jammu and Kashmir", 32.7353, 74.8617),
    City("srinagar", "Srinagar", "श्रीनगर", "Jammu and Kashmir", 34.0857, 74.8055),
    City("katra", "Katra", "कटरा", "Jammu and Kashmir", 32.9917, 74.9320),
    City("gwalior", "Gwalior", "ग्वालियर", "Madhya Pradesh", 26.2298, 78.1734),
    City("jabalpur", "Jabalpur", "जबलपुर", "Madhya Pradesh", 23.1670, 79.9501),
    City("ujjain", "Ujjain", "उज्जैन", "Madhya Pradesh", 23.1824, 75.7764),
    City("raipur", "Raipur", "रायपुर", "Chhattisgarh", 21.2333, 81.6333),
    City("bhilai", "Bhilai", "भिलाई", "Chhattisgarh", 21.2092, 81.4285),
    City("gaya", "Gaya", "गया", "Bihar", 24.7969, 85.0038),
    City("bhagalpur", "Bhagalpur", "भागलपुर", "Bihar", 25.2445, 86.9718),
    City("muzaffarpur", "Muzaffarpur", "मुज़फ़्फ़रपुर", "Bihar", 26.1226, 85.3906),
    City("jamshedpur", "Jamshedpur", "जमशेदपुर", "Jharkhand", 22.8028, 86.1855),
    City("dhanbad", "Dhanbad", "धनबाद", "Jharkhand", 23.7976, 86.4299),
    City("deoghar", "Deoghar", "देवघर", "Jharkhand", 24.4898, 86.6990),
    City("howrah", "Howrah", "हावड़ा", "West Bengal", 22.5769, 88.3186),
    City("asansol", "Asansol", "आसनसोल", "West Bengal", 23.6833, 86.9833),
    City("siliguri", "Siliguri", "सिलीगुड़ी", "West Bengal", 26.7100, 88.4285),
    City("cuttack", "Cuttack", "कटक", "Odisha", 20.4650, 85.8793),
    City("puri", "Puri", "पुरी", "Odisha", 19.7982, 85.8249),
    City("coimbatore", "Coimbatore", "कोयंबटूर", "Tamil Nadu", 11.0055, 76.9661),
    City("madurai", "Madurai", "मदुरै", "Tamil Nadu", 9.9190, 78.1195),
    City("tiruchirappalli", "Tiruchirappalli", "तिरुचिरापल्ली", "Tamil Nadu", 10.8155, 78.6965),
    City("salem", "Salem", "सेलम", "Tamil Nadu", 11.6538, 78.1554),
    City("rameswaram", "Rameswaram", "रामेश्वरम", "Tamil Nadu", 9.2885, 79.3127),
    City("thiruvananthapuram", "Thiruvananthapuram", "तिरुवनंतपुरम", "Kerala", 8.4855, 76.9492),
    City("kozhikode", "Kozhikode", "कोझिकोड", "Kerala", 11.2480, 75.7804),
    City("thrissur", "Thrissur", "त्रिशूर", "Kerala", 10.5167, 76.2167),
    City("kollam", "Kollam", "कोल्लम", "Kerala", 8.8811, 76.5847),
    City("kannur", "Kannur", "कन्नूर", "Kerala", 11.8675, 75.3576),
    City("malappuram", "Malappuram", "मलप्पुरम", "Kerala", 11.0420, 76.0815),
    City("mysuru", "Mysuru", "मैसूरु", "Karnataka", 12.2979, 76.6393),
    City("mangaluru", "Mangaluru", "मंगलुरु", "Karnataka", 12.9172, 74.8560),
    City("hubballi", "Hubballi", "हुब्बल्ली", "Karnataka", 15.3478, 75.1338),
    City("warangal", "Warangal", "वारंगल", "Telangana", 18.0000, 79.5833),
    City("vijayawada", "Vijayawada", "विजयवाड़ा", "Andhra Pradesh", 16.5074, 80.6466),
    City("tirupati", "Tirupati", "तिरुपति", "Andhra Pradesh", 13.6355, 79.4199),
    City("guntur", "Guntur", "गुंटूर", "Andhra Pradesh", 16.2997, 80.4573),
    City("panaji", "Panaji", "पणजी", "Goa", 15.4957, 73.8262),
    City("shillong", "Shillong", "शिलांग", "Meghalaya", 25.5689, 91.8831),
    City("imphal", "Imphal", "इंफाल", "Manipur", 24.8081, 93.9442),
    City("agartala", "Agartala", "अगरतला", "Tripura", 23.8361, 91.2794),
    City("gangtok", "Gangtok", "गंगटोक", "Sikkim", 27.3257, 88.6122),
    City("aizawl", "Aizawl", "आइज़ोल", "Mizoram", 23.7289, 92.7179),
    City("kohima", "Kohima", "कोहिमा", "Nagaland", 25.6747, 94.1110),
    City("itanagar", "Itanagar", "ईटानगर", "Arunachal Pradesh", 27.0869, 93.6099),
    City("puducherry", "Puducherry", "पुडुचेरी", "Puducherry", 11.9338, 79.8298),
)

# State and union-territory names for the Hindi pages' grouped city index.
STATE_HI: dict[str, str] = {
    "Andhra Pradesh": "आंध्र प्रदेश", "Arunachal Pradesh": "अरुणाचल प्रदेश",
    "Assam": "असम", "Bihar": "बिहार", "Chandigarh": "चंडीगढ़",
    "Chhattisgarh": "छत्तीसगढ़", "Delhi": "दिल्ली", "Goa": "गोवा",
    "Gujarat": "गुजरात", "Haryana": "हरियाणा", "Himachal Pradesh": "हिमाचल प्रदेश",
    "Jammu and Kashmir": "जम्मू और कश्मीर", "Jharkhand": "झारखंड",
    "Karnataka": "कर्नाटक", "Kerala": "केरल", "Madhya Pradesh": "मध्य प्रदेश",
    "Maharashtra": "महाराष्ट्र", "Manipur": "मणिपुर", "Meghalaya": "मेघालय",
    "Mizoram": "मिज़ोरम", "Nagaland": "नागालैंड", "Odisha": "ओडिशा",
    "Puducherry": "पुडुचेरी", "Punjab": "पंजाब", "Rajasthan": "राजस्थान",
    "Sikkim": "सिक्किम", "Tamil Nadu": "तमिलनाडु", "Telangana": "तेलंगाना",
    "Tripura": "त्रिपुरा", "Uttar Pradesh": "उत्तर प्रदेश", "Uttarakhand": "उत्तराखंड",
    "West Bengal": "पश्चिम बंगाल",
}

BY_SLUG: dict[str, City] = {c.slug: c for c in CITIES}


# DIVASTRO-123: the regional languages' city and state names live in
# seo_city_names (CITIES[lang][slug], STATES[lang][state]); Hindi stays here.
STATE_KN, STATE_TE, STATE_TA, STATE_ML, STATE_BN, STATE_OR = (
    _names.STATES[c] for c in ("kn", "te", "ta", "ml", "bn", "or"))


def has_name(city: City, lang: str) -> bool:
    """Whether `city` has its own spelling in `lang` (hi, or seo_city_names)."""
    return lang == "hi" or city.slug in _names.CITIES.get(lang, {})


def city_name(city: City, lang: str) -> str:
    """The city's name in `lang` (name_hi / seo_city_names), else the English one."""
    if lang == "hi":
        return city.name_hi
    return _names.CITIES.get(lang, {}).get(city.slug) or city.name


def state_name(state: str, lang: str) -> str:
    """A state in `lang` (a `STATE_<CODE>` table here), else the English name."""
    return (globals().get(f"STATE_{lang.upper()}") or {}).get(state, state)


def place(city: City, lang: str) -> str:
    """'New Delhi, Delhi' / 'नई दिल्ली, दिल्ली'; English where `lang` has no city names."""
    if has_name(city, lang):
        return f"{city_name(city, lang)}, {state_name(city.state, lang)}"
    return city.label


def by_state() -> list[tuple[str, list[City]]]:
    """(state, cities) in alphabetical order of state, cities alphabetical within
    each — the order the city index on every tool page is shown in. ~100 pills
    in one undifferentiated cloud is unusable on a phone; grouped, a visitor
    finds their state and then their city."""
    groups: dict[str, list[City]] = {}
    for c in CITIES:
        groups.setdefault(c.state, []).append(c)
    return [(s, sorted(groups[s], key=lambda c: c.name)) for s in sorted(groups)]

# What the bare /panchang, /rahu-kaal and /choghadiya URLs show. The capital is
# the least surprising default and the one most other almanacs use.
DEFAULT: City = BY_SLUG["new-delhi"]


def get(slug: str) -> City | None:
    return BY_SLUG.get(slug.lower())
