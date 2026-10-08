# Marathi (mr) review sheet - DIVASTRO-147

For a native Marathi reader. Files: `app/lang_data/mr.py`, `app/astro/names_mr.py`, `app/static/i18n/mr.json`.

## 1. The 40 most visible strings

| # | English | Marathi |
|---|---|---|
| 1 | Today's Panchang in {city} | {city} मधील आजचे पंचांग |
| 2 | Rahu Kaal today in {city} | {city} मधील आजचा राहुकाळ |
| 3 | Choghadiya today | आजचा चौघडिया |
| 4 | Tithi / Nakshatra / Yoga / Karana | तिथी / नक्षत्र / योग / करण |
| 5 | Vaar (weekday) | वार |
| 6 | Sunrise / Sunset | सूर्योदय / सूर्यास्त |
| 7 | Moonrise / Moonset | चंद्रोदय / चंद्रास्त |
| 8 | Moon sign | चंद्र रास |
| 9 | Yamaganda / Gulika Kaal | यमगंड / गुलिक काळ |
| 10 | Abhijit Muhurat | अभिजित मुहूर्त |
| 11 | Not observed on Wednesday | बुधवारी पाळला जात नाही |
| 12 | Open the full Panchang - any city, any date | संपूर्ण पंचांग उघडा - कोणतेही शहर, कोणतीही तारीख |
| 13 | Today's Rashifal | आजचे राशिभविष्य |
| 14 | {name} Rashifal Today | {local} राशिभविष्य आज - दैनिक भविष्य |
| 15 | Favourable day / Mixed day / Take it easy | अनुकूल दिवस / संमिश्र दिवस / सावकाश घेण्याचा दिवस |
| 16 | Today's Moon transit (Chandra gochar) | आजचे चंद्र गोचर |
| 17 | Sade Sati is running | साडेसाती सुरू आहे |
| 18 | The longer backdrop: slow transits | मोठी पार्श्वभूमी: संथ गोचर |
| 19 | Vrat & festivals | व्रते आणि सण |
| 20 | Today's vrat & festivals | आजची व्रते आणि सण |
| 21 | Next 30 days | पुढील 30 दिवस |
| 22 | Ekadashi {year}: dates and parana time | एकादशी {year}: तारखा आणि पारणे वेळ |
| 23 | {name} {year}: date and muhurat | {name} {year}: तारीख आणि मुहूर्त |
| 24 | Timings vary by city | वेळा शहरानुसार बदलतात |
| 25 | How the date is fixed | तारीख कशी ठरते |
| 26 | Kundali Milan (36 guna) | कुंडली मिलन (36 गुण) |
| 27 | Free Janam Kundali | मोफत जन्मकुंडली |
| 28 | Muhurat Finder | मुहूर्त शोधक |
| 29 | Vivah / Griha Pravesh / Mundan Muhurat | विवाह / गृहप्रवेश / मुंडन मुहूर्त |
| 30 | Naam se Kundali Milan | नावावरून कुंडली मिलन |
| 31 | The 27 Nakshatras | 27 नक्षत्रे |
| 32 | The 12 Rashis (Moon Signs) | 12 राशी (चंद्र राशी) |
| 33 | Nature and traits | स्वभाव आणि वैशिष्ट्ये |
| 34 | Mangal Dosha (Manglik) | मंगळ दोष (मांगलिक) |
| 35 | Show my reading (app) | माझे भविष्य पाहा |
| 36 | Get your free kundali in 30 seconds | 30 सेकंदांत मोफत कुंडली मिळवा |
| 37 | Ask AI Guru | एआय गुरूंना विचारा |
| 38 | Share on WhatsApp | WhatsApp वर शेअर करा |
| 39 | Stay in touch | संपर्कात राहा |
| 40 | Astrological readings are provided for guidance and entertainment... | ज्योतिषीय भविष्य मार्गदर्शन आणि मनोरंजनासाठी दिले आहे. तो वैद्यकीय, कायदेशीर किंवा आर्थिक सल्ला नाही. |

## 2. Astrology-term decisions

| Term | Chosen | Rejected | Why |
|---|---|---|---|
| Rahu Kaal | राहुकाळ | राहु काल | ळ, one word, as in Marathi panchangs |
| Gulika | गुलिक काळ | गुलिक काल | same |
| Full-moon tithi | पौर्णिमा | पूर्णिमा | Marathi spelling (गुरुपौर्णिमा, वटपौर्णिमा) |
| Zodiac sign | रास (चंद्र रास) | राशि | Marathi usage |
| Tula | तूळ | तुला | Marathi form |
| Nakshatra Mula | मूळ | मूल | Marathi ळ |
| Mrigashira / Shatabhisha | मृगशीर्ष / शततारका | मृगशिरा / शतभिषा | Marathi panchang forms |
| Purva/Uttara Bhadrapada | पूर्वा/उत्तरा भाद्रपदा | भाद्रपद | feminine nakshatra form |
| Months | Amanta (चैत्र ... फाल्गुन) | Purnimanta | Maharashtra uses Amanta; matches the engine |
| Holi (colour day) | धुळवड (रंगांची होळी) | होली | Holika Dahan is होळी in Marathi; the colour day is धुळवड |
| Govardhan Puja | गोवर्धन पूजा (दिवाळी पाडवा) | - | the engine has Govardhan; दिवाळी पाडवा is its Marathi name |
| Dhanteras | धनत्रयोदशी | धनतेरस | Marathi usage |
| Bhai Dooj | भाऊबीज | भैया दूज | Marathi usage |
| Vinayaka Chaturthi | विनायकी चतुर्थी | विनायक चतुर्थी | Marathi usage |
| Vat Purnima | वटपौर्णिमा | वट पूर्णिमा | Marathi usage |
| Akshaya Tritiya | अक्षय्य तृतीया | अक्षय तृतीया | Marathi spelling |
| Dhaiya of Saturn | पनवती (ढैया) | अडीचकी | common Marathi word; please confirm |
| Angarki Chaturthi | अंगारकी चतुर्थी | - | well known in Maharashtra |
| Devshayani / Devutthana Ekadashi | देवशयनी (आषाढी) / देवउठनी (कार्तिकी) | - | Marathi nicknames added in brackets |
| Gana | देव / मनुष्य / राक्षस | नर | traditional matching terms |
| Nadi | आद्य / मध्य / अंत्य | - | |
| Pada | चरण | पाद | Marathi usage |
| Varjyam | वर्ज्य | - | |
| Planet names | गुरू, शनी, राहू, केतू | गुरु, शनि | Marathi long ू/ी |
| Wedding (kundali milan) | कुंडली मिलन | गुणमेलन | MILAN terms are used in the engine; गुणमेलन is more Marathi, consider |
| Mundan | मुंडन (जावळ) | - | जावळ is the Marathi word |
| House (bhava) | भाव | घर | |
| Chaturmas, Kharmas, Adhik Maas | चातुर्मास, खरमास, अधिक मास | - | खरमास is North-Indian; Marathi says धनुर्मास/मीनार्क, kept as the engine name |

## 3. Places I was unsure

- House ordinals are written in the locative-ready form (पहिल्या, दुसऱ्या ... बाराव्या) because every sentence continues with "भावात".
- `RASHIFAL_TEXT.s.desc`: "{local} राशीचे ... राशिभविष्य" and the tone label.
- `phase.1-3` "पहिला (आरंभीचा) / दुसरा (शिखराचा) / तिसरा (उतरता)" for the Sade Sati phases.
- Sade Sati dhaiya line (पनवती).
- `VRAT_ABOUT` texts (47) follow the English; check the ritual vocabulary (शमीपूजन, नहाय-खाय, पसाही तांदूळ).
- Karwa Chauth, Hartalika: Marathi names used for the pages the engine has.
- `SEO_FAQ` question 5 now says "in Marathi" instead of "in Hindi".
- Nakshatra trait paragraphs (27) and rashi paragraphs (12) are long free translations.
- `NAAM_MILAN_TEXT.explainer`: examples (प्रिया → पी, क्षितिज → की) kept in Devanagari.
- `CLOCK`: सकाळी/दुपारी/संध्याकाळी/रात्री; times print as "सकाळी 6:26".
- "IST" still appears in some engine-generated place lines (allowed Latin).
- Page lines use "भारतीय वेळ" in my `when` text; `class="hi"` sub lines kept as the engine expects.

## 4. Conventions

- Polite तुम्ही / तुमचे register, `आहे`, `पाहा`, `करा`, `कृपया`; no exclamation marks.
- ASCII digits; months जानेवारी ... डिसेंबर; weekdays रविवार ... शनिवार.
- Anusvara before a consonant (पंचमी, संक्रांत, कुंभ, यमगंड).
- Full stop (.) not danda.
- Amanta month system, Gudi Padwa as new year.
- City and state names as Marathi newspapers spell them (मुंबई, पुणे, नागपूर, नाशिक, छत्रपती संभाजीनगर, बेंगळुरू).
- Hindi twin lines in the English templates are dropped; the `class="hi"` sub-lines carry Marathi text.
- No REGIONAL_NOTE and no SOLAR_MASA (not needed for Maharashtra).

## 5. Registry strings in app/i18n.py (not edited by me)

Not reviewed in this pass; the lead should have them checked together with section 1.
