# Gujarati (gu) — native review sheet (DIVASTRO-148)

Files: `app/lang_data/gu.py` (page text), `app/astro/names_gu.py` (astrology names),
`app/static/i18n/gu.json` (app strings). Written by Claude (Sonnet 5.5) from the English;
nothing here has been read by a Gujarati speaker yet. Register throughout: polite તમે,
`છે / નથી / કરો / જુઓ`, ASCII digits, "." as full stop (Gujarati does not use the danda).
Case endings are attached to city names and tokens the Gujarati way (`{city}માં`,
`{city}નું`, `{sign}માં`), never with a hyphen.

## 1. The 40 most visible strings

| # | where | English | Gujarati |
|---|---|---|---|
| 1 | tool name | Panchang | પંચાંગ |
| 2 | tool name | Rahu Kaal | રાહુકાળ |
| 3 | tool name | Choghadiya | ચોઘડિયાં |
| 4 | /panchang title | Today's Panchang in {city}, {date} — Tithi, Nakshatra, Rahu Kaal | {city}માં આજનું પંચાંગ, {date} — તિથિ, નક્ષત્ર, રાહુકાળ |
| 5 | /panchang H1 | Today's Panchang in {city} | {city}નું આજનું પંચાંગ |
| 6 | /panchang box | Today in {city} is {paksha} {tithi} with the Moon in {nakshatra} nakshatra. Rahu Kaal runs {rahu} — avoid starting anything new in that window. | આજે {city}માં {paksha} {tithi} છે અને ચંદ્ર {nakshatra} નક્ષત્રમાં છે. રાહુકાળ {rahu} દરમિયાન છે — આ સમયમાં કોઈ નવું કામ શરૂ ન કરો. |
| 7 | row labels | Vaar / Tithi / Paksha / Nakshatra / Yoga / Karana | વાર / તિથિ / પક્ષ / નક્ષત્ર / યોગ / કરણ |
| 8 | row labels | Sunrise / Sunset / Moonrise / Moonset | સૂર્યોદય / સૂર્યાસ્ત / ચંદ્રોદય / ચંદ્રાસ્ત |
| 9 | row labels | Yamaganda / Gulika Kaal / Abhijit Muhurat | યમગંડ / ગુલિક કાળ / અભિજિત મુહૂર્ત |
| 10 | Wednesday note | Not observed on Wednesday (Budhavara) | બુધવારે અભિજિત મુહૂર્ત ગણાતું નથી |
| 11 | /rahu-kaal H1 | Rahu Kaal Today in {city} | {city}માં આજનો રાહુકાળ |
| 12 | /choghadiya H1 | Choghadiya Today in {city} | {city}માં આજનાં ચોઘડિયાં |
| 13 | choghadiya names | Amrit, Shubh, Labh, Char, Rog, Kaal, Udveg | અમૃત, શુભ, લાભ, ચલ, રોગ, કાળ, ઉદ્વેગ |
| 14 | choghadiya nature | Auspicious / Neutral / Inauspicious | શુભ / મધ્યમ / અશુભ |
| 15 | tithi label | Shukla Panchami | સુદ પાંચમ |
| 16 | tithi label | Krishna Amavasya | વદ અમાસ |
| 17 | links | Kundali Milan (36 guna) | કુંડળી મિલન (36 ગુણ) |
| 18 | links | Free Janam Kundali | મફત જન્મકુંડળી |
| 19 | links | Today's Rashifal | આજનું રાશિફળ |
| 20 | links | Today's Vrat & Festivals in {city} | {city}માં આજનાં વ્રત અને તહેવાર |
| 21 | footer disclaimer | Astrological readings are provided for guidance and entertainment. They are not medical, legal or financial advice. | જ્યોતિષીય વાચન માર્ગદર્શન અને મનોરંજન માટે આપવામાં આવે છે. તે તબીબી, કાનૂની કે નાણાકીય સલાહ નથી. |
| 22 | stay strip | Get today's panchang on your phone every morning | દરરોજ સવારે આજનું પંચાંગ તમારા ફોન પર મેળવો |
| 23 | stay strip | Join our WhatsApp channel | અમારી WhatsApp ચેનલ સાથે જોડાઓ |
| 24 | /rashifal title | Aaj Ka Rashifal, {date_short} — Today's Horoscope for All 12 Signs | આજનું રાશિફળ, {date_short} — બધી 12 રાશિનું દૈનિક ભવિષ્ય |
| 25 | /rashifal/<sign> H1 | {name} Rashifal Today | આજનું {local} રાશિફળ |
| 26 | tone labels | Favourable day / Mixed day / Take it easy | અનુકૂળ દિવસ / મિશ્ર દિવસ / આજે શાંતિથી કામ લો |
| 27 | Moon transit | The Moon is in {sign} all day — your {house} house. | ચંદ્ર આખો દિવસ {sign}માં છે — તમારા {house} ભાવમાં. |
| 28 | ordinals (houses) | 1st … 12th | 1લા 2જા 3જા 4થા 5મા 6ઠ્ઠા 7મા … 12મા (oblique form, used before ભાવમાં) |
| 29 | Sade Sati | Sade Sati is running — the {phase} phase. | સાડાસાતી ચાલી રહી છે — {phase} તબક્કો. |
| 30 | /vrat-tyohar | Today's vrat & festivals | આજનાં વ્રત અને તહેવાર |
| 31 | vrat | No major vrat or festival today. | આજે કોઈ મોટું વ્રત કે તહેવાર નથી. |
| 32 | festival page | {name} {year} is on {when}. | {name} {year} {when}ના રોજ છે. |
| 33 | Ekadashi page | Ekadashi {year}: dates and parana time | એકાદશી {year}: તારીખો અને પારણાંનો સમય |
| 34 | muhurat | Vivah Muhurat / Griha Pravesh Muhurat / Mundan Muhurat | વિવાહ મુહૂર્ત / ગૃહપ્રવેશ મુહૂર્ત / મુંડન મુહૂર્ત |
| 35 | /nakshatra | The 27 Nakshatras | 27 નક્ષત્ર |
| 36 | /rashi | The 12 Rashis (Moon Signs) | 12 રાશિ (ચંદ્ર રાશિ) |
| 37 | naam milan | Naam se Kundali Milan | નામ પરથી કુંડળી મિલન |
| 38 | app home | Know your kundali. Ask anything. | તમારી કુંડળી જાણો. કંઈ પણ પૂછો. |
| 39 | app CTA | Get your free kundali in 30 seconds | 30 સેકન્ડમાં તમારી મફત કુંડળી મેળવો |
| 40 | app | Show my reading / Ask about career, love, money… | મારું વાચન બતાવો / કારકિર્દી, પ્રેમ, પૈસા વિશે પૂછો… |

## 2. Astrology-term decisions (chosen / rejected / why)

| English | Chosen | Rejected | Why |
|---|---|---|---|
| Paksha Shukla / Krishna | સુદ / વદ | શુક્લ / કૃષ્ણ | Gujarati panchangs and papers print "સુદ પાંચમ", "વદ અમાસ". The label is always "{paksha} {tithi}". The bare word "પક્ષ" (row label, `paksha.full` = "{paksha} પક્ષ") therefore reads "સુદ પક્ષ", which is understood but is not how it is usually said (see 3). |
| Tithi names | એકમ બીજ ત્રીજ ચોથ પાંચમ છઠ સાતમ આઠમ નોમ દશમ અગિયારસ બારસ તેરસ ચૌદશ પૂનમ અમાસ | પ્રતિપદા દ્વિતીયા … પૂર્ણિમા અમાવસ્યા | Everyday Gujarati almanac forms. The Ekadashi vrat names keep the Sanskrit form (કામદા એકાદશી) as Gujarati calendars print them. |
| Purnima / Amavasya in festival names | પૂનમ / અમાસ (ગુરુ પૂનમ, શરદ પૂનમ, કારતક પૂનમ) | પૂર્ણિમા | One word for one thing. |
| Lunar months | ચૈત્ર વૈશાખ જેઠ અષાઢ શ્રાવણ ભાદરવો આસો કારતક માગશર પોષ મહા ફાગણ | જ્યેષ્ઠ, ભાદ્રપદ, આશ્વિન, માર્ગશીર્ષ, પૌષ, માઘ, ફાલ્ગુન | Gujarati panchang forms. Inside running text "ભાદરવા વદ", "આસો વદ" etc. |
| Month system | Amanta (month ends on Amavasya), Vikram Samvat year starting Kartak sud ekam (the day after Diwali) | Purnimanta | The engine's months are Amanta; that is also the Gujarati convention, so "આસો વદ અમાસ" is Diwali. Where the English says "(purnimanta)" I translated it and added the Gujarati equivalent in brackets (e.g. Janmashtami: ભાદરવા વદ આઠમ (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં શ્રાવણ વદ આઠમ)). Those bracketed equivalents are my additions: please check them (Janmashtami, Jivitputrika, Sakat Chauth, Mauni Amavasya, Sheetala Ashtami, Kajari Teej, Hal Shashthi, Pitru Paksha, Narak Chaturdashi, Vat Savitri). |
| Rahu Kaal | રાહુકાળ | રાહુ કાલ, રાહુ કાળ | One compound word, as in Gujarati papers. |
| Yamaganda / Gulika | યમગંડ / ગુલિક કાળ | યમઘંટ | The panchang forms. |
| Abhijit Muhurat | અભિજિત મુહૂર્ત | અભિજીત | Sanskrit-correct. |
| Varjyam | વર્જ્ય | વર્જ્યમ | In Gujarati it is also an ordinary word ("to be avoided"); that is the meaning, so I used it. |
| Nakshatra spellings | મૃગશીર્ષ, કૃત્તિકા, મઘા, આશ્લેષા, પૂર્વા ફાલ્ગુની, પૂર્વાષાઢા, જ્યેષ્ઠા, મૂળ, પૂર્વા ભાદ્રપદ | મૃગશિરા, કૃતિકા, માઘ | Gujarati panchang spellings. |
| Pada | ચરણ | પાદ | Gujarati panchangs say "પ્રથમ ચરણ". |
| Sade Sati | સાડાસાતી | પનોતી | The English term is Sade Sati; "પનોતી" (and "નાની પનોતી" for Dhaiya) is the everyday Gujarati word. Kept સાડાસાતી / ઢૈયા to match the engine. |
| Kharmas | ખરમાસ (કમૂરતાં) | – | Gujarati calls the period કમૂરતાં (કમુહૂર્તા); both given once. |
| Adhik Maas | અધિક માસ | પુરુષોત્તમ માસ | Plain translation. |
| Muhurat | મુહૂર્ત | મુરત | Standard written form. |
| Kundali Milan | કુંડળી મિલન | જન્માક્ષર મેળાપક | Matches the site's nav label; "મેળાપક" appears in descriptions. |
| Rashifal | રાશિફળ | રાશિભવિષ્ય | Gujarat Samachar / Divya Bhaskar use રાશિફળ. |
| Janam kundali | જન્મકુંડળી | જન્માક્ષર | |
| Lagna (ascendant) | લગ્ન | ઉદય લગ્ન | |
| Bhava (house) | ભાવ | સ્થાન | "તમારા 5મા ભાવમાં". |
| Dasha / Mahadasha / Antardasha | દશા / મહાદશા / અંતર્દશા | – | |
| Gochar (transit) | ગોચર | – | |
| Exalted / debilitated / own sign | ઉચ્ચ / નીચ / સ્વરાશિ | | |
| Graha names | સૂર્ય ચંદ્ર મંગળ બુધ ગુરુ શુક્ર શનિ રાહુ કેતુ | | |
| Rashi names | મેષ વૃષભ મિથુન કર્ક સિંહ કન્યા તુલા વૃશ્ચિક ધનુ મકર કુંભ મીન | ધન | ધનુ is the usual Gujarati form. |
| Koota names | વર્ણ વશ્ય તારા યોનિ ગ્રહમૈત્રી ગણ ભકૂટ નાડી | ભકૂટ vs ભકુટ | |
| Yoni animals | અશ્વ ગજ મેષ સર્પ શ્વાન માર્જાર મૂષક ગાય મહિષ વ્યાઘ્ર મૃગ વાનર નકુલ સિંહ | ઘોડો, હાથી … | The traditional Sanskrit animal words used in matching tables. |
| Gana / Nadi | દેવ મનુષ્ય રાક્ષસ / આદ્ય મધ્ય અંત્ય | | |
| Dhaiya / Kantaka Shani / Ashtama Shani | ઢૈયા / કંટક શનિ / અષ્ટમ શનિ | | |
| Chandrashtama | ચંદ્રાષ્ટમ | | |
| Holi / Holika Dahan | ધુળેટી / હોલિકા દહન | હોળી | In Gujarat ધુળેટી is the colour day; the bonfire night is હોળી / હોલિકા દહન. |
| Makar Sankranti | મકરસંક્રાંતિ (ઉત્તરાયણ) | | Gujarat's name given in brackets. |
| Govardhan Puja | ગોવર્ધન પૂજા | બેસતું વર્ષ | The engine has only Govardhan Puja. It is shown with a short note "બેસતું વર્ષ" (REGIONAL_NOTE) and in the long text; no separate New Year observance was invented. |
| Raksha Bandhan | રક્ષાબંધન (બળેવ in text) | | |
| Dussehra | દશેરા (વિજયાદશમી) | | |
| Navratri | શારદીય નવરાત્રિ પ્રારંભ | | The Gujarati-specific garba framing is not added: the engine has no such observance. |
| Smarta | સ્માર્ત | | |
| Drik Panchang | દ્રિક પંચાંગ | | Transliterated, as a name. |

## 3. Places I am unsure of

1. `paksha.full` = "{paksha} પક્ષ" gives "સુદ પક્ષ" / "વદ પક્ષ". Natural Gujarati says "શુક્લ પક્ષ / કૃષ્ણ પક્ષ" or just "સુદ / વદ". The engine hands the same `{paksha}` word to every string, so one of the two had to give way.
2. Ordinal house numbers (1લા, 2જા … 12મા) are oblique forms I wrote so that `{house} ભાવમાં` works. As a stand-alone label (`house_short` = "5મા ભાવમાં") it is fine as a table cell but please confirm.
3. `ચોઘડિયાં` (plural, used as the tool name) versus `ચોઘડિયું` (singular).
4. Long nakshatra and rashi trait paragraphs (39 paragraphs): natural phrasing, gender and "ચંદ્ર અહીં હોય તેવા લોકો" repetition. Please read at least four.
5. `કમૂરતાં` is my recollection of the Gujarati name of Kharmas; confirm.
6. The bracketed Amanta equivalents of purnimanta festival months (section 2).
7. The `tone` label "આજે શાંતિથી કામ લો" for "Take it easy": this word is inserted into a sentence in `s.desc` ("… ગોચર કરે છે — {tone}.").
8. `નામ પરથી કુંડળી મિલન` examples: the tool still reads names typed in Devanagari or Latin only, so the page says "હિન્દી (દેવનાગરી) કે અંગ્રેજીમાં". The two example names are Latin ("Ram", "Sita").
9. `વર્જ્ય` for Varjyam (also an everyday word).
10. `ધુળેટી` for the engine's "Holi" key (the engine date is the colour day).
11. "સ્માર્ત (મુખ્ય) ગણતરી" for "Smarta (default) reckoning".
12. App strings that are English-origin jargon: Zodiacal Releasing, Firdaria, Profection (transliterated), "Succedent/Cadent" (પણફર / આપોક્લિમ: standard but rarely seen in Gujarati).
13. `પેજ` (web page) is used for "page" to match the registry's notice string; "પાનું" is not used.
14. Titles are about as long as the English; a few Gujarati titles (km.title, fk.title) may exceed 60 characters in search results.
15. "AI જ્યોતિષી" / "AI ગુરુ": the Latin "AI" is kept (the English source has "AI").

## 4. Conventions

* Digits ASCII (0-9) everywhere, including guna scores, years, times.
* Weekdays રવિવાર … શનિવાર; short forms રવિ સોમ મંગળ બુધ ગુરુ શુક્ર શનિ.
* Gregorian months જાન્યુઆરી ફેબ્રુઆરી માર્ચ એપ્રિલ મે જૂન જુલાઈ ઑગસ્ટ સપ્ટેમ્બર ઑક્ટોબર નવેમ્બર ડિસેમ્બર.
* Clock words સવાર, બપોર, સાંજ, રાત (the engine has no "late afternoon" key for gu).
* Hindi helper lines (`lang="hi"` sub-headings and Devanagari examples) are not carried over; the `class="hi"` sub-headings hold Gujarati text, like Bengali/Kannada.
* Latin kept only where the English source has it: Divine Astro, WhatsApp, UPI, UTR, PDF, IST, AI, KP, Google Pay, PhonePe, Paytm, FamApp, BHIM, SMS, OAuth, and the transliteration letters in the Naam Milan explainer.
* Registry strings in `app/i18n.py` (written earlier by hand, not by me): `choose` "ભાષા પસંદ કરો", `hint` "શું તમે આ સાઇટ ગુજરાતીમાં જોવા માગો છો?", `yes` "ગુજરાતીમાં જુઓ", `not_now` "હમણાં નહીં", `notice`, `english_answer`: all read naturally; I propose no change.
