"""Vrat and tyohar (fasts and festivals) pages, English and Hindi (DIVASTRO-111).

    /vrat-tyohar                 today's vrat/festival + the next 30 days
    /vrat-tyohar/2026, /2027     the whole year, month by month
    /tyohar/<festival>-<year>    one major festival: date, puja muhurat, what/how
    /ekadashi-2026, -2027        every Ekadashi with its parana time
    /hi/...                      a Hindi copy of each
    GET /api/vrat/today          the home Today strip's one-liner (any city)
    GET /api/vrat/day            one date's observances with their timings (Panchang tool)

"aaj kaun sa vrat hai", "ekadashi kab hai", "diwali puja muhurat 2026" are
daily searches; the answer is a date and a time, so both are in the raw HTML.
Every date and time comes from `astro.festivals` for New Delhi, whose rules
were checked against Drik Panchang (tests/test_festivals.py); anything that
could not be validated is switched off there and never reaches a page.

A year is ~0.4 s of ephemeris work, computed once per process per city
(`festivals._year` is an lru_cache) - the first request warms it.

The shell is seo_pages._render: same style, AdSense, visit.js beacon, share
button, hreflang pair and footer(lang) as the other SEO pages.
"""

from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, JSONResponse

from . import geo, push, seo_cities, seo_pages
from .astro import festivals
from .astro.muhurat import VARA_HI
from .seo_pages import EN, HI, MONTHS_HI, _e, _long_date, _render, _short_date

router = APIRouter()

CITY = seo_cities.DEFAULT                 # New Delhi
YEARS = (2026, 2027)
UPCOMING_DAYS = 30


# --------------------------------------------------------------------------
# What each major festival is (short, factual, respectful)
# --------------------------------------------------------------------------

ABOUT = {
    "makar-sankranti": (
        "Makar Sankranti marks the Sun's entry into Makara (Capricorn) and the start of its "
        "northward journey (Uttarayana). It is a harvest festival: people bathe in holy rivers, "
        "give til (sesame), jaggery, khichdi and blankets in charity, and fly kites.",
        "मकर संक्रांति पर सूर्य मकर राशि में प्रवेश करते हैं और उत्तरायण आरंभ होता है। यह फसल का "
        "पर्व है - पवित्र नदियों में स्नान, तिल-गुड़, खिचड़ी व कंबल का दान और पतंगबाज़ी इसकी पहचान हैं।"),
    "maha-shivratri": (
        "Maha Shivratri, the great night of Shiva, falls on the Krishna Chaturdashi of Magha. "
        "Devotees fast, offer water, milk and bel leaves on the Shivling, chant Om Namah Shivaya "
        "and keep vigil through the four prahars of the night; the Nishita kaal puja around "
        "midnight is the most important.",
        "महाशिवरात्रि फाल्गुन (अमांत माघ) कृष्ण चतुर्दशी को भगवान शिव की महान रात्रि है। भक्त व्रत "
        "रखते हैं, शिवलिंग पर जल, दूध व बेलपत्र चढ़ाते हैं, ॐ नमः शिवाय का जाप करते हैं और रात्रि "
        "के चारों प्रहर जागरण करते हैं; मध्यरात्रि का निशीथ काल पूजन सबसे महत्वपूर्ण है।"),
    "holika-dahan": (
        "Holika Dahan, on the eve of Holi, celebrates Prahlad's devotion and the victory of good "
        "over evil. A bonfire is lit after sunset, avoiding Bhadra, and families circle it "
        "offering grain, coconut and prayers.",
        "होलिका दहन, होली की पूर्व संध्या पर, प्रह्लाद की भक्ति और बुराई पर अच्छाई की विजय का पर्व "
        "है। सूर्यास्त के बाद, भद्रा से बचकर, होलिका जलाई जाती है और परिवार परिक्रमा कर अन्न, "
        "नारियल व प्रार्थना अर्पित करते हैं।"),
    "holi": (
        "Holi, the festival of colours, is celebrated the morning after Holika Dahan with "
        "colours, music, sweets like gujiya and visits to family and friends.",
        "रंगों का पर्व होली होलिका दहन की अगली सुबह रंग-गुलाल, संगीत, गुझिया जैसी मिठाइयों और "
        "अपनों से मिलने के साथ मनाया जाता है।"),
    "ram-navami": (
        "Ram Navami celebrates the birth of Lord Rama on Chaitra Shukla Navami, at midday. "
        "Devotees fast, read the Ramcharitmanas, and offer puja in the Madhyahna muhurat, the "
        "time of his birth.",
        "राम नवमी चैत्र शुक्ल नवमी को मध्याह्न में भगवान श्रीराम के जन्म का उत्सव है। भक्त व्रत "
        "रखते हैं, रामचरितमानस का पाठ करते हैं और मध्याह्न मुहूर्त में पूजन करते हैं।"),
    "hanuman-jayanti": (
        "Hanuman Jayanti (Chaitra Purnima in North India) celebrates the birth of Lord Hanuman. "
        "Devotees visit Hanuman temples, recite the Hanuman Chalisa and Sundarkand, and offer "
        "sindoor and laddoos.",
        "हनुमान जयंती (उत्तर भारत में चैत्र पूर्णिमा) भगवान हनुमान का जन्मोत्सव है। भक्त हनुमान "
        "मंदिर जाते हैं, हनुमान चालीसा व सुंदरकांड का पाठ करते हैं और सिंदूर व लड्डू चढ़ाते हैं।"),
    "akshaya-tritiya": (
        "Akshaya Tritiya, Vaishakha Shukla Tritiya, is held to make every good deed 'akshaya' - "
        "undiminishing. People worship Vishnu and Lakshmi, give in charity, and begin new "
        "ventures or buy gold.",
        "वैशाख शुक्ल तृतीया, अक्षय तृतीया पर किया गया शुभ कर्म 'अक्षय' माना जाता है। इस दिन विष्णु-"
        "लक्ष्मी पूजन, दान, नए कार्य का आरंभ और सोना खरीदने की परंपरा है।"),
    "raksha-bandhan": (
        "Raksha Bandhan, on Shravana Purnima, celebrates the bond between brothers and sisters. "
        "Sisters tie a rakhi on their brother's wrist and pray for his well-being; the rakhi is "
        "tied in a time free of Bhadra.",
        "श्रावण पूर्णिमा को रक्षा बंधन भाई-बहन के स्नेह का पर्व है। बहनें भाई की कलाई पर राखी "
        "बांधकर उसकी कुशलता की प्रार्थना करती हैं; राखी भद्रा रहित समय में बांधी जाती है।"),
    "janmashtami": (
        "Krishna Janmashtami celebrates the birth of Lord Krishna at midnight on Krishna Ashtami "
        "of Bhadrapada (purnimanta). Devotees fast through the day and break it after the "
        "Nishita (midnight) puja, when the infant Krishna is bathed and placed in a cradle.",
        "कृष्ण जन्माष्टमी भाद्रपद कृष्ण अष्टमी की मध्यरात्रि भगवान श्रीकृष्ण के जन्म का उत्सव है। "
        "भक्त दिनभर व्रत रखते हैं और निशीथ (मध्यरात्रि) पूजा में बाल गोपाल का अभिषेक कर उन्हें "
        "पालने में झुलाते हैं।"),
    "ganesh-chaturthi": (
        "Ganesh Chaturthi, Bhadrapada Shukla Chaturthi, welcomes Lord Ganesha home. The idol is "
        "installed and worshipped in the Madhyahna (midday) muhurat, the time of his birth, with "
        "modak, durva grass and red flowers; looking at the Moon on this day is avoided.",
        "भाद्रपद शुक्ल चतुर्थी, गणेश चतुर्थी पर गणपति का घर में स्वागत होता है। मध्याह्न मुहूर्त में "
        "मूर्ति स्थापना कर मोदक, दूर्वा व लाल फूलों से पूजन किया जाता है; इस दिन चंद्र दर्शन वर्जित "
        "माना जाता है।"),
    "chaitra-navratri": (
        "Chaitra Navratri, the nine nights of Goddess Durga in spring, begins on Chaitra Shukla "
        "Pratipada - also the Hindu New Year (Vikram Samvat). Ghatasthapana (installing the "
        "kalash) opens the nine days of worship.",
        "चैत्र नवरात्रि, वसंत में माँ दुर्गा की नौ रात्रियां, चैत्र शुक्ल प्रतिपदा से आरंभ होती हैं - यही "
        "हिंदू नववर्ष (विक्रम संवत) भी है। घटस्थापना (कलश स्थापना) से नौ दिन की पूजा शुरू होती है।"),
    "navratri": (
        "Sharad Navratri, the nine nights of Goddess Durga in autumn, begins on Ashwin Shukla "
        "Pratipada with Ghatasthapana - installing the kalash and sowing barley - in the "
        "morning. Each day honours one of the nine forms of the Goddess.",
        "शारदीय नवरात्रि, शरद ऋतु में माँ दुर्गा की नौ रात्रियां, आश्विन शुक्ल प्रतिपदा को प्रातः "
        "घटस्थापना - कलश स्थापना और जौ बोने - से आरंभ होती है। हर दिन देवी के एक स्वरूप की पूजा होती है।"),
    "dussehra": (
        "Dussehra (Vijayadashami) marks Lord Rama's victory over Ravana and Goddess Durga's over "
        "Mahishasura. Shami puja, Aparajita puja and the burning of Ravana effigies are held in "
        "the afternoon; the Vijay muhurat is considered good for starting anything new.",
        "दशहरा (विजयादशमी) श्रीराम की रावण पर और माँ दुर्गा की महिषासुर पर विजय का पर्व है। अपराह्न "
        "में शमी पूजा, अपराजिता पूजा और रावण दहन होता है; विजय मुहूर्त नए कार्य के आरंभ के लिए शुभ "
        "माना जाता है।"),
    "karwa-chauth": (
        "On Karwa Chauth married women keep a fast from sunrise to moonrise for their husbands' "
        "long life. The evening puja of Karwa Mata is followed by offering water (arghya) to the "
        "Moon, after which the fast is broken.",
        "करवा चौथ पर सुहागिन स्त्रियां पति की दीर्घायु के लिए सूर्योदय से चंद्रोदय तक व्रत रखती हैं। "
        "संध्या को करवा माता की पूजा के बाद चंद्रमा को अर्घ्य देकर व्रत खोला जाता है।"),
    "ahoi-ashtami": (
        "On Ahoi Ashtami, eight days before Diwali, mothers keep a fast for the well-being of "
        "their children and worship Ahoi Mata in the evening; the fast is traditionally broken "
        "after sighting the stars (or, in some families, the Moon).",
        "दीपावली से आठ दिन पहले अहोई अष्टमी पर माताएं संतान की कुशलता के लिए व्रत रखती हैं और संध्या "
        "को अहोई माता की पूजा करती हैं; परंपरागत रूप से तारों (कुछ परिवारों में चंद्रमा) के दर्शन के "
        "बाद व्रत खोला जाता है।"),
    "dhanteras": (
        "Dhanteras, the first day of Diwali, honours Dhanvantari and Goddess Lakshmi. People buy "
        "new utensils, gold or silver and light the Yama deepak at dusk; the puja is done in "
        "Pradosh kaal, ideally in the fixed (sthir) Vrishabha lagna.",
        "धनतेरस, दीपावली का पहला दिन, धन्वंतरि और माँ लक्ष्मी को समर्पित है। लोग नए बर्तन, सोना-चांदी "
        "खरीदते हैं और संध्या को यम दीपक जलाते हैं; पूजन प्रदोष काल में, संभव हो तो स्थिर वृषभ लग्न "
        "में, किया जाता है।"),
    "diwali": (
        "Diwali, on Kartika Amavasya, is the festival of lights. Lakshmi and Ganesha are "
        "worshipped in the evening - in Pradosh kaal, preferably in the fixed (sthir) Vrishabha "
        "lagna so that prosperity stays - and homes are lit with diyas.",
        "कार्तिक अमावस्या को दीपावली प्रकाश का पर्व है। संध्या को प्रदोष काल में, संभव हो तो स्थिर "
        "वृषभ लग्न में (ताकि लक्ष्मी स्थिर रहें), लक्ष्मी-गणेश पूजन होता है और घर दीयों से जगमगाते हैं।"),
    "govardhan-puja": (
        "Govardhan Puja (Annakut), the day after Diwali, remembers Krishna lifting Govardhan hill. "
        "A Govardhan of cow-dung or food is worshipped and an annakut of many dishes is offered, "
        "usually in the morning (Pratahkala).",
        "गोवर्धन पूजा (अन्नकूट), दीपावली के अगले दिन, श्रीकृष्ण द्वारा गोवर्धन पर्वत उठाने की स्मृति है। "
        "गोबर या अन्न का गोवर्धन बनाकर पूजा जाता है और अनेक व्यंजनों का अन्नकूट भोग लगता है, प्रायः "
        "प्रातःकाल।"),
    "bhai-dooj": (
        "Bhai Dooj, Kartika Shukla Dwitiya, celebrates brothers and sisters: sisters apply a "
        "tilak, perform aarti and pray for their brother's long life, ideally in the Aparahna "
        "(afternoon) time.",
        "कार्तिक शुक्ल द्वितीया, भाई दूज पर बहनें भाई को तिलक लगाकर आरती करती हैं और उसकी लंबी आयु "
        "की कामना करती हैं, उत्तम समय अपराह्न है।"),
    "chhath-puja": (
        "Chhath Puja worships the Sun God and Chhathi Maiya over four days. On the main day "
        "(Kartika Shukla Shashthi) devotees stand in water and offer arghya to the setting Sun, "
        "and to the rising Sun the next morning, ending a fast kept without water.",
        "छठ पूजा चार दिन तक सूर्य देव और छठी मैया की उपासना है। मुख्य दिन (कार्तिक शुक्ल षष्ठी) "
        "व्रती जल में खड़े होकर डूबते सूर्य को और अगली सुबह उगते सूर्य को अर्घ्य देकर निर्जला व्रत "
        "पूरा करते हैं।"),
    "vasant-panchami": (
        "Vasant Panchami, Magha Shukla Panchami, welcomes spring and honours Goddess Saraswati. "
        "Students and artists worship books and instruments, people wear yellow, and children "
        "often begin learning to write (vidyarambh).",
        "माघ शुक्ल पंचमी, वसंत पंचमी वसंत ऋतु का स्वागत और माँ सरस्वती की पूजा का पर्व है। विद्यार्थी "
        "व कलाकार पुस्तकों और वाद्यों की पूजा करते हैं, पीले वस्त्र पहने जाते हैं और विद्यारंभ होता है।"),
    "guru-purnima": (
        "Guru Purnima, Ashadha Purnima, honours one's teachers and Maharishi Ved Vyasa, born on "
        "this day. Disciples offer gratitude, flowers and gifts to their guru.",
        "आषाढ़ पूर्णिमा, गुरु पूर्णिमा गुरुजनों और इसी दिन जन्मे महर्षि वेदव्यास को समर्पित है। शिष्य "
        "अपने गुरु के प्रति कृतज्ञता, पुष्प व भेंट अर्पित करते हैं।"),
    "sharad-purnima": (
        "Sharad Purnima, Ashwin Purnima, is the night the Moon is held to be brightest and full "
        "of nectar. Kheer is kept in the moonlight overnight and eaten as prasad; Lakshmi is "
        "worshipped (Kojagari).",
        "आश्विन पूर्णिमा, शरद पूर्णिमा की रात चंद्रमा सबसे उज्ज्वल और अमृतमय माना जाता है। खीर रात भर "
        "चांदनी में रखकर प्रसाद रूप में ली जाती है; कोजागरी लक्ष्मी पूजा भी होती है।"),
    "devuthani-ekadashi": (
        "Devuthani (Prabodhini) Ekadashi, Kartika Shukla Ekadashi, is when Lord Vishnu is held to "
        "wake from his four-month sleep, ending Chaturmas. Tulsi vivah begins and the wedding "
        "season opens. Devotees fast and break the fast (parana) the next day.",
        "देवउठनी (प्रबोधिनी) एकादशी, कार्तिक शुक्ल एकादशी पर भगवान विष्णु चार माह की योगनिद्रा से "
        "जागते हैं और चातुर्मास समाप्त होता है। तुलसी विवाह होता है और विवाह के मुहूर्त फिर शुरू होते "
        "हैं। भक्त व्रत रखकर अगले दिन पारण करते हैं।"),
    # ---- Added with the Jivitputrika fix.
    "jivitputrika": (
        "Jivitputrika (Jitiya, Jiutiya) is kept by mothers in Bihar, Jharkhand, eastern Uttar "
        "Pradesh and Nepal for the long life and well-being of their children, on Ashwin "
        "Krishna Ashtami (purnimanta). It begins with nahay-khay the day before; the fast "
        "itself is nirjala, without water, through the day and night, with worship of Jimutavahana "
        "and the Jitiya katha. Parana, breaking the fast, is the next morning.",
        "जीवित्पुत्रिका (जितिया, जिउतिया) व्रत बिहार, झारखंड, पूर्वी उत्तर प्रदेश और नेपाल में माताएं "
        "संतान की लंबी आयु और कुशलता के लिए आश्विन कृष्ण अष्टमी (पूर्णिमांत) को रखती हैं। एक दिन पहले "
        "नहाय-खाय होता है; व्रत निर्जला होता है, दिन-रात जल भी ग्रहण नहीं किया जाता, जीमूतवाहन की "
        "पूजा व जितिया कथा होती है। पारण अगली सुबह किया जाता है।"),
    "lohri": (
        "Lohri, the evening before Makar Sankranti, is the winter harvest festival of Punjab and "
        "North India. A bonfire is lit at dusk and people offer til, gur, rewari, peanuts and "
        "popcorn to it, sing and dance; it is especially celebrated for a new bride or a newborn.",
        "लोहड़ी, मकर संक्रांति से पहले की शाम, पंजाब और उत्तर भारत का शीतकालीन फसल पर्व है। संध्या को "
        "अलाव जलाकर तिल, गुड़, रेवड़ी, मूंगफली व मक्का अर्पित किए जाते हैं, गीत और नृत्य होते हैं; नई "
        "बहू या नवजात के घर यह विशेष उत्साह से मनाई जाती है।"),
    "sakat-chauth": (
        "Sakat Chauth (Tilkut Chauth), the Sankashti Chaturthi of Magha (purnimanta), is kept by "
        "mothers for their children. Ganesha and Sakat Mata are worshipped with til and jaggery, "
        "and the fast is broken after offering arghya to the rising Moon.",
        "सकट चौथ (तिलकुट चौथ), माघ (पूर्णिमांत) की संकष्टी चतुर्थी, माताएं संतान के लिए रखती हैं। तिल-गुड़ "
        "से गणेश जी और सकट माता की पूजा होती है और चंद्रोदय पर अर्घ्य देकर व्रत खोला जाता है।"),
    "mauni-amavasya": (
        "Mauni Amavasya, the Amavasya of Magha (purnimanta), is the great bathing day of the Magh "
        "Mela at Prayagraj. Devotees bathe in the Ganga or a holy river, keep silence (mauna) and "
        "give in charity.",
        "माघ (पूर्णिमांत) की अमावस्या, मौनी अमावस्या प्रयागराज के माघ मेले का प्रमुख स्नान पर्व है। "
        "श्रद्धालु गंगा या पवित्र नदी में स्नान, मौन व्रत और दान करते हैं।"),
    "sheetala-ashtami": (
        "Sheetala Ashtami (Basoda), Chaitra Krishna Ashtami (purnimanta), honours Sheetala Mata, "
        "the goddess who protects from fevers and pox. Food is cooked the day before and the "
        "stale (basi) food is offered and eaten; no fire is lit for cooking that day.",
        "चैत्र कृष्ण अष्टमी (पूर्णिमांत), शीतला अष्टमी (बसौड़ा) पर शीतला माता की पूजा होती है, जो रोगों से "
        "रक्षा करती हैं। भोजन एक दिन पहले बनाया जाता है और बासी भोजन का भोग लगाकर ग्रहण किया जाता "
        "है; उस दिन चूल्हा नहीं जलाया जाता।"),
    "gudi-padwa": (
        "Gudi Padwa (Maharashtra) and Ugadi (Karnataka, Andhra Pradesh, Telangana) mark the lunar "
        "New Year on Chaitra Shukla Pratipada. A gudi - a decorated pole with a cloth and kalash - "
        "is raised at the door, and neem with jaggery is eaten for a year of both sweet and bitter.",
        "चैत्र शुक्ल प्रतिपदा को गुड़ी पड़वा (महाराष्ट्र) और उगादी (कर्नाटक, आंध्र, तेलंगाना) चांद्र नववर्ष "
        "के रूप में मनाए जाते हैं। द्वार पर गुड़ी - वस्त्र व कलश से सजा डंडा - लगाई जाती है और "
        "नीम-गुड़ खाकर वर्ष के मीठे-कड़वे अनुभवों को स्वीकार किया जाता है।"),
    "gangaur": (
        "Gangaur, Chaitra Shukla Tritiya, is Rajasthan's festival of Gauri (Parvati) and Shiva. "
        "Women worship Gauri for marital happiness - married women for their husbands, girls for "
        "a good match - ending eighteen days of puja that begin the day after Holi.",
        "चैत्र शुक्ल तृतीया, गणगौर राजस्थान का गौरी (पार्वती) और शिव का पर्व है। सुहागिनें पति के लिए और "
        "कन्याएं अच्छे वर के लिए गौरी पूजन करती हैं; होली के अगले दिन से चलने वाली अठारह दिन की पूजा "
        "इसी दिन पूर्ण होती है।"),
    "vat-savitri": (
        "Vat Savitri Vrat, on Jyeshtha Amavasya in North India (purnimanta), remembers Savitri, "
        "who won back her husband Satyavan's life from Yama. Married women fast, worship the "
        "banyan (vat) tree, tie raw thread around it while circling it, and hear the Savitri katha.",
        "उत्तर भारत में ज्येष्ठ अमावस्या (पूर्णिमांत) को वट सावित्री व्रत सावित्री की स्मृति है, जिन्होंने "
        "यमराज से पति सत्यवान के प्राण वापस पाए। सुहागिनें व्रत रखकर वट वृक्ष की पूजा करती हैं, कच्चा "
        "सूत लपेटते हुए परिक्रमा करती हैं और सावित्री कथा सुनती हैं।"),
    "vat-purnima": (
        "Vat Purnima is the same Vat Savitri vrat as kept on Jyeshtha Purnima in Maharashtra, "
        "Gujarat and the south (amanta calendar), fifteen days after the North Indian date. "
        "Married women fast and worship the banyan tree for their husbands' long life.",
        "वट पूर्णिमा वही वट सावित्री व्रत है जो महाराष्ट्र, गुजरात और दक्षिण भारत (अमांत) में ज्येष्ठ "
        "पूर्णिमा को, उत्तर भारत की तिथि से पंद्रह दिन बाद, रखा जाता है। सुहागिनें पति की दीर्घायु के लिए "
        "व्रत रखकर वट वृक्ष की पूजा करती हैं।"),
    "ganga-dussehra": (
        "Ganga Dussehra, Jyeshtha Shukla Dashami, celebrates the descent of the Ganga to earth "
        "through Bhagiratha's penance. Devotees bathe in the Ganga, offer lamps and give in "
        "charity; the bath is held to wash away ten kinds of sin.",
        "ज्येष्ठ शुक्ल दशमी, गंगा दशहरा भगीरथ के तप से गंगा के पृथ्वी पर अवतरण का पर्व है। श्रद्धालु गंगा "
        "स्नान, दीपदान और दान करते हैं; यह स्नान दस प्रकार के पापों को हरने वाला माना जाता है।"),
    "hariyali-teej": (
        "Hariyali Teej, Shravana Shukla Tritiya, celebrates the reunion of Shiva and Parvati in "
        "the monsoon. Women wear green, apply mehndi, swing on decorated jhoolas, sing Sawan songs "
        "and many keep a fast for their husbands.",
        "श्रावण शुक्ल तृतीया, हरियाली तीज सावन में शिव-पार्वती के मिलन का उत्सव है। स्त्रियां हरे वस्त्र "
        "पहनती हैं, मेहंदी लगाती हैं, झूला झूलती हैं, सावन के गीत गाती हैं और अनेक पति के लिए व्रत रखती हैं।"),
    "nag-panchami": (
        "Nag Panchami, Shravana Shukla Panchami, is the day serpent deities (nagas) are "
        "worshipped. Images of snakes are drawn or installed and offered milk, flowers and "
        "sweets, with prayers for the family's protection. (In Gujarat, Nag Pancham falls later, "
        "in Bhadrapada.)",
        "श्रावण शुक्ल पंचमी, नाग पंचमी पर नाग देवताओं की पूजा होती है। नाग की आकृति बनाकर या स्थापित कर "
        "दूध, पुष्प और मिष्ठान्न अर्पित किए जाते हैं और परिवार की रक्षा की प्रार्थना होती है। (गुजरात में नाग "
        "पंचम बाद में, भाद्रपद में होती है।)"),
    "kajari-teej": (
        "Kajari (Kajli, Badi) Teej, Bhadrapada Krishna Tritiya (purnimanta), is kept by married "
        "women of Uttar Pradesh, Bihar, Rajasthan and Madhya Pradesh. They fast, worship the "
        "neem tree (Neemadi Mata) and break the fast after offering arghya to the Moon; kajari "
        "folk songs are sung.",
        "भाद्रपद कृष्ण तृतीया (पूर्णिमांत), कजरी (कजली, बड़ी) तीज उत्तर प्रदेश, बिहार, राजस्थान और मध्य "
        "प्रदेश में सुहागिनें रखती हैं। वे व्रत रखकर नीमड़ी माता की पूजा करती हैं और चंद्रमा को अर्घ्य देकर "
        "व्रत खोलती हैं; कजरी लोकगीत गाए जाते हैं।"),
    "hal-shashthi": (
        "Hal Shashthi (Lalahi Chhath, Har Chhath), Bhadrapada Krishna Shashthi (purnimanta), is "
        "Lord Balarama's birthday, whose weapon is the plough (hal). Mothers fast for their "
        "children and eat nothing grown with a plough - often pasahi rice and buffalo milk.",
        "भाद्रपद कृष्ण षष्ठी (पूर्णिमांत), हल षष्ठी (ललही छठ, हरछठ) हलधर बलराम जी की जयंती है। माताएं "
        "संतान के लिए व्रत रखती हैं और हल से जोती भूमि का अन्न नहीं खातीं - प्रायः पसही चावल और भैंस "
        "का दूध लिया जाता है।"),
    "hartalika-teej": (
        "Hartalika Teej, Bhadrapada Shukla Tritiya, honours Parvati's penance to win Shiva. "
        "Women keep a nirjala fast, make clay images of Shiva and Parvati, worship them (morning "
        "puja in Pratahkala is preferred), keep vigil at night and break the fast next morning.",
        "भाद्रपद शुक्ल तृतीया, हरतालिका तीज शिव को पाने के लिए पार्वती के तप की स्मृति है। स्त्रियां "
        "निर्जला व्रत रखकर मिट्टी के शिव-पार्वती बनाकर पूजन करती हैं (प्रातःकाल पूजा उत्तम), रात्रि "
        "जागरण करती हैं और अगली सुबह व्रत खोलती हैं।"),
    "rishi-panchami": (
        "Rishi Panchami, Bhadrapada Shukla Panchami, honours the Saptarishis, the seven sages. "
        "Women in particular bathe, fast and worship the sages at midday (Madhyahna), seeking "
        "purification from faults committed unknowingly.",
        "भाद्रपद शुक्ल पंचमी, ऋषि पंचमी सप्तर्षियों को समर्पित है। विशेष रूप से स्त्रियां स्नान, व्रत और "
        "मध्याह्न में सप्तर्षि पूजन करती हैं, ताकि अनजाने में हुए दोषों से शुद्धि हो।"),
    "anant-chaturdashi": (
        "Anant Chaturdashi, Bhadrapada Shukla Chaturdashi, is the worship of Lord Vishnu as "
        "Anant. A sacred thread with fourteen knots (the anant sutra) is tied on the arm after "
        "puja; it is also the day Ganesh idols are immersed (Ganesh Visarjan).",
        "भाद्रपद शुक्ल चतुर्दशी, अनंत चतुर्दशी पर भगवान विष्णु के अनंत रूप की पूजा होती है। पूजा के बाद "
        "चौदह गांठों वाला अनंत सूत्र बांह पर बांधा जाता है; इसी दिन गणेश विसर्जन भी होता है।"),
    "pitru-paksha": (
        "Pitru Paksha, the fortnight of the ancestors, runs from Pratipada to Amavasya of the "
        "dark half of Ashwin (purnimanta). On the tithi of an ancestor's passing, families offer "
        "tarpan and shraddha - pinda, food for Brahmins, cows, crows and dogs - in the Kutup, "
        "Rohina or Aparahna time.",
        "पितृ पक्ष, पितरों का पखवाड़ा, आश्विन (पूर्णिमांत) कृष्ण प्रतिपदा से अमावस्या तक चलता है। पूर्वज की "
        "मृत्यु तिथि पर परिवार कुतुप, रौहिण या अपराह्न काल में तर्पण और श्राद्ध - पिंडदान, ब्राह्मण भोजन "
        "तथा गाय, कौए व कुत्ते के लिए भोजन - करते हैं।"),
    "sarva-pitru-amavasya": (
        "Sarva Pitru Amavasya (Mahalaya Amavasya) closes Pitru Paksha. Shraddha on this day "
        "reaches all ancestors, including those whose tithi is not known; it is done in the "
        "Kutup, Rohina or Aparahna time.",
        "सर्व पितृ अमावस्या (महालया अमावस्या) पितृ पक्ष का अंतिम दिन है। इस दिन किया गया श्राद्ध सभी "
        "पितरों तक पहुंचता है, उन तक भी जिनकी तिथि ज्ञात न हो; यह कुतुप, रौहिण या अपराह्न काल में किया "
        "जाता है।"),
    "narak-chaturdashi": (
        "Narak Chaturdashi (Roop Chaudas), Kartika Krishna Chaturdashi (purnimanta), remembers "
        "Krishna's victory over Narakasura. Before sunrise, while the Moon is up, people take an "
        "oil bath with ubtan (Abhyang snan), and a lamp for Yama is lit in the evening.",
        "कार्तिक कृष्ण चतुर्दशी (पूर्णिमांत), नरक चतुर्दशी (रूप चौदस) श्रीकृष्ण की नरकासुर पर विजय की "
        "स्मृति है। सूर्योदय से पहले, चंद्रोदय के बाद, उबटन व तेल से अभ्यंग स्नान किया जाता है और संध्या "
        "को यम का दीपक जलाया जाता है।"),
    "tulsi-vivah": (
        "Tulsi Vivah, on Kartika Shukla Dwadashi, is the ceremonial wedding of the tulsi plant "
        "(as Vrinda) to Lord Vishnu as Shaligram. Families decorate the tulsi like a bride and "
        "perform the rites of a wedding; the Hindu wedding season begins after it.",
        "कार्तिक शुक्ल द्वादशी को तुलसी विवाह में तुलसी (वृंदा) का शालिग्राम रूप भगवान विष्णु से विधिवत "
        "विवाह कराया जाता है। तुलसी को दुल्हन की तरह सजाकर विवाह की रस्में की जाती हैं; इसके बाद विवाह के "
        "मुहूर्त शुरू होते हैं।"),
    "kartik-purnima": (
        "Kartik Purnima ends the holy month of Kartika. It is a great day for bathing in the "
        "Ganga or a holy river and giving in charity, and also Guru Nanak Jayanti and Tripuri "
        "Purnima, when Shiva destroyed Tripurasura.",
        "कार्तिक पूर्णिमा पवित्र कार्तिक मास का समापन है। यह गंगा या पवित्र नदी में स्नान और दान का "
        "महापर्व है; इसी दिन गुरु नानक जयंती और त्रिपुरी पूर्णिमा (शिव द्वारा त्रिपुरासुर वध) भी है।"),
    "dev-deepawali": (
        "Dev Deepawali, the 'Diwali of the gods', is celebrated on Kartik Purnima evening, above "
        "all on the ghats of Varanasi, which are lit with lakhs of diyas. It marks Shiva's "
        "victory over Tripurasura; lamps are offered to the Ganga in Pradosh kaal.",
        "देव दीपावली, 'देवताओं की दिवाली', कार्तिक पूर्णिमा की संध्या को, विशेषकर वाराणसी के घाटों पर लाखों "
        "दीयों के साथ मनाई जाती है। यह शिव की त्रिपुरासुर पर विजय का पर्व है; प्रदोष काल में गंगा को "
        "दीपदान किया जाता है।"),
}

# Short notes where traditions differ, shown on the festival page.
TRADITION_NOTE = {
    "holika-dahan": (
        "Dates follow Drik Panchang. When Bhadra covers the whole Purnima night and Purnima "
        "lasts most of the next day, Drik moves Holika Dahan to the next evening's Pradosh "
        "(as in 2026, 3 March); some almanacs instead give a time late on the first night, "
        "after Bhadra ends.",
        "तिथि द्रिक पंचांग के अनुसार है। जब पूर्णिमा की पूरी रात भद्रा हो और पूर्णिमा अगले दिन अधिकांश "
        "समय रहे, तो द्रिक पंचांग होलिका दहन अगली संध्या के प्रदोष में बताता है (जैसे 2026 में 3 मार्च); "
        "कुछ पंचांग पहली रात भद्रा समाप्ति के बाद का समय देते हैं।"),
    "janmashtami": (
        "Dates follow Drik Panchang's Smarta (default) reckoning, with Rohini nakshatra at "
        "midnight preferred. Vaishnava/ISKCON communities sometimes keep Janmashtami a day later.",
        "तिथि द्रिक पंचांग की स्मार्त (सामान्य) गणना से है, जिसमें मध्यरात्रि में रोहिणी नक्षत्र को "
        "प्राथमिकता दी गई है। वैष्णव/इस्कॉन परंपरा कभी-कभी अगले दिन जन्माष्टमी मनाती है।"),
    "devuthani-ekadashi": (
        "This is the Smarta (householder) date. Where Ekadashi spans two days, Vaishnavas may fast "
        "on the second day.",
        "यह स्मार्त (गृहस्थ) तिथि है। जब एकादशी दो दिन हो, वैष्णव दूसरे दिन व्रत रख सकते हैं।"),
    "dussehra": (
        "Dates follow Drik Panchang (Dashami in Aparahna, Shravana nakshatra preferred). In "
        "Bengal and some almanacs Vijayadashami can fall a day later.",
        "तिथि द्रिक पंचांग के अनुसार है (अपराह्न में दशमी, श्रवण नक्षत्र को प्राथमिकता)। बंगाल और "
        "कुछ पंचांगों में विजयादशमी एक दिन बाद हो सकती है।"),
    "jivitputrika": (
        "Dates follow Drik Panchang (Ashtami at midday; when it is at sunrise only briefly, as in "
        "2023, the previous day). Nahay-khay is the day before and parana the next morning; "
        "regional panchangs (e.g. Mithila) can differ by a day.",
        "तिथि द्रिक पंचांग के अनुसार है (मध्याह्न में अष्टमी; सूर्योदय पर थोड़ी देर ही हो, जैसे 2023 में, तो "
        "पिछला दिन)। नहाय-खाय एक दिन पहले और पारण अगली सुबह होता है; क्षेत्रीय पंचांगों (जैसे मिथिला) में "
        "कभी-कभी एक दिन का अंतर होता है।"),
    "vat-savitri": (
        "Two traditions: North India keeps Vat Savitri on Jyeshtha Amavasya (this date); "
        "Maharashtra, Gujarat and the south keep it as Vat Purnima fifteen days later.",
        "दो परंपराएं: उत्तर भारत में वट सावित्री ज्येष्ठ अमावस्या (यह तिथि) को; महाराष्ट्र, गुजरात और दक्षिण "
        "भारत में पंद्रह दिन बाद वट पूर्णिमा के रूप में।"),
    "vat-purnima": (
        "Two traditions: this is the Purnima (amanta) date of Maharashtra, Gujarat and the south; "
        "North India keeps Vat Savitri on the Amavasya fifteen days earlier.",
        "दो परंपराएं: यह महाराष्ट्र, गुजरात और दक्षिण भारत की पूर्णिमा (अमांत) तिथि है; उत्तर भारत में वट "
        "सावित्री पंद्रह दिन पहले अमावस्या को होता है।"),
    "ganga-dussehra": (
        "When Jyeshtha is doubled (an adhika month, as in 2026), Drik Panchang keeps Ganga "
        "Dussehra in the adhika Jyeshtha; some almanacs give the nija Jyeshtha date a month later.",
        "जब ज्येष्ठ दो हों (अधिक मास, जैसे 2026 में), द्रिक पंचांग गंगा दशहरा अधिक ज्येष्ठ में बताता है; "
        "कुछ पंचांग एक माह बाद निज ज्येष्ठ की तिथि देते हैं।"),
    "pitru-paksha": (
        "Drik Panchang counts Pitru Paksha from the Pratipada shraddha; Purnima shraddha is on "
        "the day before, and many calendars start the fortnight there.",
        "द्रिक पंचांग पितृ पक्ष प्रतिपदा श्राद्ध से गिनता है; पूर्णिमा श्राद्ध एक दिन पहले होता है और कई "
        "कैलेंडर पखवाड़ा वहीं से शुरू करते हैं।"),
    "dev-deepawali": (
        "Drik Panchang publishes Dev Deepawali for Varanasi; the date here uses the same rule "
        "(Purnima in Pradosh), and the Pradosh kaal shown is New Delhi's.",
        "द्रिक पंचांग देव दीपावली वाराणसी के लिए देता है; यहां तिथि उसी नियम (प्रदोष में पूर्णिमा) से है "
        "और दिया गया प्रदोष काल नई दिल्ली का है।"),
    "kartik-purnima": (
        "This is the snan-daan day (Purnima at sunrise). When Purnima begins the previous "
        "afternoon, the Purnima fast and Dev Deepawali can fall a day earlier.",
        "यह स्नान-दान का दिन है (सूर्योदय पर पूर्णिमा)। जब पूर्णिमा पिछले दिन दोपहर बाद शुरू हो, तो पूर्णिमा "
        "व्रत और देव दीपावली एक दिन पहले हो सकते हैं।"),
}


# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

def _pre(lang: str) -> str:
    return "/hi" if lang == HI else ""


def hub_path(lang: str = EN) -> str:
    return _pre(lang) + "/vrat-tyohar"


def year_path(year: int, lang: str = EN) -> str:
    return _pre(lang) + f"/vrat-tyohar/{year}"


def ekadashi_path(year: int, lang: str = EN) -> str:
    return _pre(lang) + f"/ekadashi-{year}"


def festival_path(slug: str, year: int, lang: str = EN) -> str:
    return _pre(lang) + f"/tyohar/{slug}-{year}"


def _year_obs(year: int) -> tuple[dict, ...]:
    return festivals._year(year, round(CITY.latitude, 4), round(CITY.longitude, 4),
                           CITY.timezone)


def festival_index(year: int) -> dict[str, dict]:
    """slug -> the observance, for every major festival dated in `year`."""
    out: dict[str, dict] = {}
    for o in _year_obs(year):
        if o["major"] and o["slug"] and o["slug"] not in out:
            out[o["slug"]] = o
    return out


def _festival_slugs(year: int) -> list[str]:
    """Pages that exist for a year, WITHOUT computing the year (used by the
    sitemap and the beacon, which must stay cheap): every major spec not
    switched off, plus Devuthani Ekadashi and Makar Sankranti."""
    keys_off = set(festivals.OMITTED)
    slugs = [s.slug for s in festivals.FESTIVALS if s.key not in keys_off and s.slug]
    slugs += ["devuthani-ekadashi", "makar-sankranti", "lohri"]
    if "holi" not in keys_off:
        slugs.append("holi")
    return slugs


def festival_names() -> dict[str, tuple[str, str]]:
    """slug -> (English, Hindi) name, for the share text. No ephemeris work."""
    out = {s.slug: (s.name_en, s.name_hi) for s in festivals.FESTIVALS if s.slug}
    out["devuthani-ekadashi"] = ("Devuthani Ekadashi", "देवउठनी एकादशी")
    out["makar-sankranti"] = ("Makar Sankranti", "मकर संक्रांति")
    out["lohri"] = ("Lohri", "लोहड़ी")
    out["holi"] = ("Holi", "होली")
    return out


def page_paths() -> list[str]:
    """Every page, both languages - for the sitemap and the beacon."""
    out = []
    for lang in (EN, HI):
        out.append(hub_path(lang))
        for y in YEARS:
            out.append(year_path(y, lang))
            out.append(ekadashi_path(y, lang))
            out += [festival_path(s, y, lang) for s in _festival_slugs(y)]
    return out


_PUBLIC = frozenset(page_paths())


def is_public_path(path: str) -> bool:
    return path in _PUBLIC


# --------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------

def _date(o: dict) -> dt.date:
    return dt.date.fromisoformat(o["date"])


def _name(o: dict, lang: str) -> str:
    return o["name_hi"] if lang == HI else o["name_en"]


def _weekday(day: dt.date, lang: str) -> str:
    w = day.strftime("%A")
    return VARA_HI.get(w, w) if lang == HI else w


def _day_label(day: dt.date, lang: str, year: bool = False) -> str:
    text = _long_date(day, lang) if year else _short_date(day, lang)
    return f"{text}, {_weekday(day, lang)}"


def _clock(iso: str, ref: dt.date, lang: str) -> str:
    return seo_pages._time(iso, ref, lang)


def _timing_text(t: dict, day: dt.date, lang: str) -> str:
    label = t["label_hi"] if lang == HI else t["label_en"]
    ref = dt.date.fromisoformat(t["date"]) if t.get("date") else day
    prefix = f"{_short_date(ref, lang)}, " if ref != day else ""
    if t.get("at"):
        value = _clock(t["at"], ref, lang)
    else:
        value = f"{_clock(t['start'], ref, lang)} – {_clock(t['end'], ref, lang)}"
    return f"{label}: {prefix}{value}"


def _timings(o: dict, lang: str, first_only: bool = False) -> str:
    day = _date(o)
    items = o["timings"][:1] if first_only else o["timings"]
    return " · ".join(_timing_text(t, day, lang) for t in items)


def _tithi_text(o: dict, lang: str) -> str:
    t = o.get("tithi")
    if not t:
        return ""
    day = _date(o)
    paksha = seo_pages.PAKSHA_HI.get(t["paksha"], t["paksha"]) if lang == HI else t["paksha"]
    from .astro.muhurat import TITHI_HI
    name = TITHI_HI.get(t["name"], t["name"]) if lang == HI else t["name"]
    if lang == HI:
        return (f"{paksha} {name}: {_clock(t['start'], day, lang)} से "
                f"{_clock(t['end'], day, lang)} तक")
    return f"{paksha} {name}: {_clock(t['start'], day, lang)} to {_clock(t['end'], day, lang)}"


def _link_for(o: dict, lang: str) -> str | None:
    if o["major"] and o["slug"]:
        y = _date(o).year
        if y in YEARS and o["slug"] in _festival_slugs(y):
            return festival_path(o["slug"], y, lang)
    if o["key"] == "ekadashi" and _date(o).year in YEARS:
        return ekadashi_path(_date(o).year, lang)
    return None


def _name_html(o: dict, lang: str) -> str:
    href = _link_for(o, lang)
    name = _e(_name(o, lang))
    return f'<a href="{_e(href)}">{name}</a>' if href else name


def _table(rows: list[dict], lang: str, with_date: bool = True) -> str:
    if lang == HI:
        th = "<tr><th>दिनांक</th><th>व्रत / त्योहार</th><th>समय (नई दिल्ली)</th></tr>"
    else:
        th = "<tr><th>Date</th><th>Vrat / festival</th><th>Timing (New Delhi)</th></tr>"
    body = []
    for o in rows:
        day = _date(o)
        body.append(
            f'<tr data-date="{o["date"]}" data-key="{_e(o["key"])}">'
            f"<td>{_e(_day_label(day, lang))}</td>"
            f"<td>{_name_html(o, lang)}</td>"
            f"<td>{_e(_timings(o, lang, first_only=True)) or '—'}</td></tr>")
    return f'<div class="scroll"><table>{th}{"".join(body)}</table></div>'


def _city_note(lang: str) -> str:
    if lang == HI:
        return ('<div class="box"><p><strong>समय शहर के अनुसार बदलते हैं।</strong> यहां दिए सभी '
                "समय नई दिल्ली के सूर्योदय-सूर्यास्त और चंद्रोदय पर आधारित हैं; दूसरे शहर में कुछ "
                "मिनट और कभी-कभी तिथि भी बदल सकती है। तिथियां द्रिक पंचांग की स्मार्त (सामान्य) "
                "गणना से मेल खाती हैं। अपने शहर के लिए पंचांग देखें।</p></div>")
    return ('<div class="box"><p><strong>Timings vary by city.</strong> Every time here is '
            "for New Delhi's sunrise, sunset and moonrise; in another city they shift by a few "
            "minutes and occasionally the date does too. Dates follow Drik Panchang's Smarta "
            "(default) reckoning. Check the Panchang for your own city.</p></div>")


def _cta(lang: str) -> str:
    text = "अपने शहर का पंचांग देखें — मुफ़्त" if lang == HI else "See the Panchang for your city — free"
    # DIVASTRO-112: the opt-in daily push button ("" while push is switched off).
    return (f'<a class="cta" href="{_e(seo_pages._app_link("panchang", lang))}">{_e(text)}</a>'
            + push.optin_html(lang))


def _more_links(lang: str, skip: str = "") -> str:
    links = [(hub_path(lang), "आज के व्रत और त्योहार" if lang == HI else "Today's vrat & festivals")]
    for y in YEARS:
        links.append((year_path(y, lang), f"व्रत-त्योहार {y}" if lang == HI else f"Festival calendar {y}"))
        links.append((ekadashi_path(y, lang), f"एकादशी {y}" if lang == HI else f"Ekadashi {y}"))
    links.append((_pre(lang) + "/panchang", "आज का पंचांग" if lang == HI else "Today's Panchang"))
    links.append((_pre(lang) + "/rashifal", "आज का राशिफल" if lang == HI else "Today's Rashifal"))
    items = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in links if h != skip)
    heading = "और देखें" if lang == HI else "More"
    return f'<h2>{heading}</h2><ul class="links">{items}</ul>'


def _festival_links(year: int, lang: str, skip: str = "") -> str:
    idx = festival_index(year)
    items = "".join(
        f'<li><a href="{_e(festival_path(s, year, lang))}">{_e(_name(o, lang))}</a></li>'
        for s, o in sorted(idx.items(), key=lambda kv: kv[1]["date"])
        if s != skip and s in _festival_slugs(year))
    heading = f"{year} के प्रमुख त्योहार" if lang == HI else f"Major festivals {year}"
    return f'<h2>{_e(heading)}</h2><ul class="links">{items}</ul>'


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

def _today() -> dt.date:
    return seo_pages._today()


def _obs_range(start: dt.date, end: dt.date) -> list[dict]:
    return festivals.observances(start, end, CITY.latitude, CITY.longitude, CITY.timezone)


def _today_block(today: dt.date, todays: list[dict], nxt: dict | None, lang: str) -> str:
    if todays:
        parts = []
        for o in todays:
            timing = _timings(o, lang)
            rule = o["rule_hi"] if lang == HI else o["rule_en"]
            parts.append(
                f'<h3>{_name_html(o, lang)}</h3>'
                + (f"<p>{_e(timing)}</p>" if timing else "")
                + (f"<p><small>{_e(_tithi_text(o, lang))}</small></p>" if o.get("tithi") else "")
                + f'<p><small>{"नियम" if lang == HI else "Rule"}: {_e(rule)}</small></p>')
        return '<div class="box today">' + "".join(parts) + "</div>"
    if lang == HI:
        text = "आज कोई प्रमुख व्रत या त्योहार नहीं है।"
        if nxt:
            text += (f" अगला: <strong>{_name_html(nxt, lang)}</strong>, "
                     f"{_e(_day_label(_date(nxt), lang))}।")
    else:
        text = "No major vrat or festival today."
        if nxt:
            text += (f" Next: <strong>{_name_html(nxt, lang)}</strong> on "
                     f"{_e(_day_label(_date(nxt), lang))}.")
    return f'<div class="box today"><p>{text}</p></div>'


def render_hub(lang: str, today: dt.date | None = None) -> HTMLResponse:
    today = today or _today()
    upcoming = _obs_range(today, today + dt.timedelta(days=UPCOMING_DAYS))
    todays = [o for o in upcoming if o["date"] == today.isoformat()]
    later = [o for o in upcoming if o["date"] > today.isoformat()]
    nxt = later[0] if later else None
    hi = lang == HI
    path, alt = hub_path(lang), hub_path(HI if not hi else EN)
    names = ", ".join(_name(o, lang) for o in todays)
    if hi:
        title = f"आज के व्रत और त्योहार ({_short_date(today, HI)}) - मुहूर्त सहित"
        h1 = "आज के व्रत और त्योहार"
        description = ((f"आज {_long_date(today, HI)}: {names}। " if names else
                        f"{_long_date(today, HI)}: आज कोई प्रमुख व्रत नहीं। ")
                       + "अगले 30 दिनों के व्रत-त्योहार, एकादशी पारण, प्रदोष, संकष्टी चंद्रोदय समय - नई दिल्ली।")
        up_h = "अगले 30 दिन"
    else:
        title = f"Aaj Ke Vrat aur Tyohar: Today's Vrat & Festivals ({_short_date(today)})"
        h1 = "Today's vrat & festivals"
        description = ((f"Today, {_long_date(today)}: {names}. " if names else
                        f"{_long_date(today)}: no major vrat today. ")
                       + "Upcoming fasts and festivals for 30 days with Ekadashi parana, Pradosh "
                         "and Sankashti moonrise times - New Delhi.")
        up_h = "Next 30 days"
    sub = (f'<p class="hi" lang="en">Today\'s vrat &amp; festivals</p>' if hi
           else '<p class="hi" lang="hi">आज के व्रत और त्योहार</p>')
    body = (f"<h1>{_e(h1)}</h1>{sub}"
            f'<p class="date">{_e(_day_label(today, lang, year=True))} · '
            f'{_e(CITY.name_hi if hi else CITY.label)}</p>'
            + _today_block(today, todays, nxt, lang)
            + f"<h2>{_e(up_h)}</h2>"
            + (_table(later, lang) if later else "<p>—</p>")
            + _city_note(lang) + _cta(lang)
            + _festival_links(today.year if today.year in YEARS else YEARS[0], lang)
            + _more_links(lang, skip=path))
    crumbs = [("व्रत और त्योहार" if hi else "Vrat & festivals", path)]
    return _render(title=title, description=description, path=path, alt=alt, crumbs=crumbs,
                   body=body, lang=lang)


def render_year(year: int, lang: str) -> HTMLResponse:
    hi = lang == HI
    obs = _year_obs(year)
    path, alt = year_path(year, lang), year_path(year, EN if hi else HI)
    if hi:
        title = f"व्रत-त्योहार {year}: पूरी सूची, तिथि और मुहूर्त (नई दिल्ली)"
        h1 = f"व्रत और त्योहार {year}"
        description = (f"{year} के सभी व्रत और त्योहार माहवार - एकादशी, प्रदोष, संकष्टी, पूर्णिमा, "
                       "अमावस्या, शिवरात्रि और दीपावली, होली, नवरात्रि जैसे पर्व, पूजा मुहूर्त सहित।")
        intro = (f"<p>{year} में नई दिल्ली के लिए <strong>{len(obs)}</strong> व्रत और त्योहार, "
                 "पंचांग से गणना किए गए। प्रमुख त्योहार पर क्लिक कर पूजा मुहूर्त और विधि देखें।</p>")
    else:
        title = f"Hindu Festival & Vrat Calendar {year} (New Delhi): Dates and Muhurat"
        h1 = f"Vrat & festival calendar {year}"
        description = (f"Every Hindu vrat and festival of {year}, month by month - Ekadashi, "
                       "Pradosh, Sankashti, Purnima, Amavasya, Shivratri and festivals like Diwali, "
                       "Navratri and Raksha Bandhan, with puja muhurat for New Delhi.")
        intro = (f"<p><strong>{len(obs)}</strong> fasts and festivals in {year} for New Delhi, "
                 "computed from the panchang. Tap a major festival for its puja muhurat and "
                 "what it is about.</p>")
    sections = []
    for m in range(1, 13):
        rows = [o for o in obs if _date(o).month == m]
        month = f"{MONTHS_HI[m - 1]} {year}" if hi else f"{dt.date(year, m, 1):%B} {year}"
        sections.append(f"<h2>{_e(month)}</h2>" + (_table(rows, lang) if rows else "<p>—</p>"))
    body = (f"<h1>{_e(h1)}</h1>"
            f'<p class="date">{_e(CITY.name_hi if hi else CITY.label)} · IST</p>'
            + intro + _city_note(lang) + "".join(sections) + _cta(lang)
            + _festival_links(year, lang) + _more_links(lang, skip=path))
    crumbs = [("व्रत और त्योहार" if hi else "Vrat & festivals", hub_path(lang)),
              (str(year), path)]
    return _render(title=title, description=description, path=path, alt=alt, crumbs=crumbs,
                   body=body, lang=lang)


def render_ekadashi(year: int, lang: str) -> HTMLResponse:
    hi = lang == HI
    eks = [o for o in _year_obs(year) if o["key"] == "ekadashi"]
    path, alt = ekadashi_path(year, lang), ekadashi_path(year, EN if hi else HI)
    if hi:
        title = f"एकादशी {year}: सभी एकादशी व्रत तिथि और पारण समय (नई दिल्ली)"
        h1 = f"एकादशी {year}"
        description = (f"{year} की सभी {len(eks)} एकादशी - व्रत की तिथि, एकादशी तिथि का आरंभ-समाप्ति "
                       "और अगले दिन पारण का समय, नई दिल्ली के लिए।")
        th = "<tr><th>एकादशी</th><th>व्रत</th><th>पारण</th></tr>"
        rule = ("<p><strong>नियम (स्मार्त):</strong> जिस दिन सूर्योदय के समय एकादशी हो उस दिन व्रत; "
                "दो सूर्योदय पर हो तो दूसरा दिन, और किसी सूर्योदय पर न हो तो जिस दिन एकादशी पड़े। पारण "
                "अगले दिन सूर्योदय के बाद, हरि वासर (द्वादशी का पहला चौथाई भाग) समाप्त होने पर, "
                "प्रातःकाल में और द्वादशी समाप्त होने से पहले किया जाता है; हरि वासर प्रातःकाल के बाद तक "
                "रहे तो मध्याह्न छोड़कर अपराह्न में।</p>")
    else:
        title = f"Ekadashi {year}: All Ekadashi Vrat Dates and Parana Time (New Delhi)"
        h1 = f"Ekadashi {year}: dates and parana time"
        description = (f"All {len(eks)} Ekadashis of {year} - fasting date, Ekadashi tithi times "
                       "and the parana (fast-breaking) window next day, for New Delhi.")
        th = "<tr><th>Ekadashi</th><th>Fast</th><th>Parana</th></tr>"
        rule = ("<p><strong>Rule (Smarta):</strong> fast on the day Ekadashi prevails at sunrise; "
                "if it prevails at two sunrises, the second day, and if at none, the day it falls "
                "in. Parana is the next day after sunrise, once Hari Vasara (the first quarter of "
                "Dwadashi) is over, within Pratahkala and before Dwadashi ends; if Hari Vasara runs "
                "past Pratahkala, parana moves to Aparahna (Madhyahna is avoided).</p>")
    rows = []
    for o in eks:
        day = _date(o)
        p = next((t for t in o["timings"] if t["key"] == "parana"), None)
        pday = dt.date.fromisoformat(p["date"]) if p else None
        parana = (f"{_day_label(pday, lang)}, {_clock(p['start'], pday, lang)} – "
                  f"{_clock(p['end'], pday, lang)}") if p else "—"
        rows.append(f'<tr data-date="{o["date"]}"><td><strong>{_e(_name(o, lang))}</strong>'
                    f"<small>{_e(_tithi_text(o, lang))}</small></td>"
                    f"<td>{_e(_day_label(day, lang))}</td><td>{_e(parana)}</td></tr>")
    sub = (f'<p class="hi" lang="en">Ekadashi {year}</p>' if hi
           else f'<p class="hi" lang="hi">एकादशी {year}</p>')
    body = (f"<h1>{_e(h1)}</h1>{sub}"
            f'<p class="date">{_e(CITY.name_hi if hi else CITY.label)} · IST</p>'
            + rule + f'<div class="scroll"><table>{th}{"".join(rows)}</table></div>'
            + _city_note(lang) + _cta(lang) + _more_links(lang, skip=path))
    crumbs = [("व्रत और त्योहार" if hi else "Vrat & festivals", hub_path(lang)),
              (f"एकादशी {year}" if hi else f"Ekadashi {year}", path)]
    return _render(title=title, description=description, path=path, alt=alt, crumbs=crumbs,
                   body=body, lang=lang)


def render_festival(slug: str, year: int, lang: str) -> HTMLResponse:
    hi = lang == HI
    o = festival_index(year).get(slug)
    if o is None or slug not in _festival_slugs(year):
        return _not_found(lang)
    day = _date(o)
    name = _name(o, lang)
    path, alt = festival_path(slug, year, lang), festival_path(slug, year, EN if hi else HI)
    main = o["timings"][0] if o["timings"] else None
    main_txt = _timing_text(main, day, lang) if main else ""
    if hi:
        title = f"{name} {year}: तिथि और शुभ मुहूर्त - {_short_date(day, HI)}"
        h1 = f"{name} {year}"
        description = (f"{name} {year} {_long_date(day, HI)}, {_weekday(day, HI)} को है। "
                       + (f"{main_txt}। " if main_txt else "") + "नई दिल्ली के लिए पूजा मुहूर्त व तिथि।")
        when = f"{name} {year} में <strong>{_e(_day_label(day, lang, year=True))}</strong> को है।"
        t_head, about_head, rule_head = "मुहूर्त और समय", "क्या है और कैसे मनाएं", "तिथि का नियम"
    else:
        title = f"{name} {year}: Date and Puja Muhurat - {_short_date(day)}"
        h1 = f"{name} {year}: date and muhurat"
        description = (f"{name} {year} is on {_weekday(day, EN)}, {_long_date(day)}. "
                       + (f"{main_txt}. " if main_txt else "") + "Puja timings for New Delhi.")
        when = f"{_e(name)} {year} is on <strong>{_e(_day_label(day, lang, year=True))}</strong>."
        t_head, about_head, rule_head = "Muhurat and timings", "What it is and how it is observed", "How the date is fixed"
    items = "".join(f"<li>{_e(_timing_text(t, day, lang))}</li>" for t in o["timings"])
    if o.get("tithi"):
        items += f"<li>{_e(_tithi_text(o, lang))}</li>"
    about = ABOUT.get(slug, ("", ""))[1 if hi else 0]
    note = TRADITION_NOTE.get(slug, TRADITION_NOTE.get(o["key"], ("", "")))[1 if hi else 0]
    rule = o["rule_hi"] if hi else o["rule_en"]
    sub = (f'<p class="hi" lang="en">{_e(o["name_en"])} {year}</p>' if hi
           else f'<p class="hi" lang="hi">{_e(o["name_hi"])} {year}</p>')
    body = (f"<h1>{_e(h1)}</h1>{sub}"
            f'<p class="date">{_e(CITY.name_hi if hi else CITY.label)} · IST</p>'
            f'<div class="box"><p>{when}</p>'
            + (f'<ul class="timings">{items}</ul>' if items else "") + "</div>"
            + (f"<h2>{_e(about_head)}</h2><p>{_e(about)}</p>" if about else "")
            + f"<h2>{_e(rule_head)}</h2><p>{_e(rule)}.</p>"
            + (f"<p><small>{_e(note)}</small></p>" if note else "")
            + _city_note(lang) + _cta(lang)
            + _festival_links(year, lang, skip=slug) + _more_links(lang))
    crumbs = [("व्रत और त्योहार" if hi else "Vrat & festivals", hub_path(lang)),
              (f"{name} {year}", path)]
    event = {"@type": "Event", "name": f"{o['name_en']} {year}", "startDate": o["date"],
             "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
             "location": {"@type": "Place", "name": "India",
                          "address": {"@type": "PostalAddress", "addressCountry": "IN"}},
             "description": ABOUT.get(slug, ("", ""))[0] or o["name_en"]}
    return _render(title=title, description=description, path=path, alt=alt, crumbs=crumbs,
                   body=body, lang=lang, extra_ld=(event,), cache=True)


def _not_found(lang: str) -> HTMLResponse:
    hi = lang == HI
    links = "".join(f'<li><a href="{_e(p)}">{_e(p)}</a></li>'
                    for p in page_paths() if p.startswith("/hi/") == hi)
    body = (f"<h1>{'पृष्ठ नहीं मिला' if hi else 'Page not found'}</h1>"
            f'<ul class="links">{links}</ul>')
    return _render(title="Not found", description="", path=hub_path(lang), crumbs=[],
                   body=body, lang=lang, status=404, cache=False)


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@router.get("/vrat-tyohar", response_class=HTMLResponse)
def hub() -> HTMLResponse:
    return render_hub(EN)


@router.get("/hi/vrat-tyohar", response_class=HTMLResponse)
def hub_hi() -> HTMLResponse:
    return render_hub(HI)


def _year_or_404(year: str, lang: str, fn) -> HTMLResponse:
    if not year.isdigit() or int(year) not in YEARS:
        return _not_found(lang)
    return fn(int(year), lang)


@router.get("/vrat-tyohar/{year}", response_class=HTMLResponse)
def year_page(year: str) -> HTMLResponse:
    return _year_or_404(year, EN, render_year)


@router.get("/hi/vrat-tyohar/{year}", response_class=HTMLResponse)
def year_page_hi(year: str) -> HTMLResponse:
    return _year_or_404(year, HI, render_year)


@router.get("/ekadashi-{year}", response_class=HTMLResponse)
def ekadashi_page(year: str) -> HTMLResponse:
    return _year_or_404(year, EN, render_ekadashi)


@router.get("/hi/ekadashi-{year}", response_class=HTMLResponse)
def ekadashi_page_hi(year: str) -> HTMLResponse:
    return _year_or_404(year, HI, render_ekadashi)


def _festival(slug_year: str, lang: str) -> HTMLResponse:
    slug, _, year = slug_year.rpartition("-")
    if not year.isdigit() or int(year) not in YEARS:
        return _not_found(lang)
    return render_festival(slug, int(year), lang)


@router.get("/tyohar/{slug}", response_class=HTMLResponse)
def festival_page(slug: str) -> HTMLResponse:
    return _festival(slug, EN)


@router.get("/hi/tyohar/{slug}", response_class=HTMLResponse)
def festival_page_hi(slug: str) -> HTMLResponse:
    return _festival(slug, HI)


@router.get("/api/vrat/today")
def vrat_today(
    lat: float = Query(CITY.latitude, ge=-90, le=90),
    lon: float = Query(CITY.longitude, ge=-180, le=180),
    tz: str = "",
) -> JSONResponse:
    """Today's vrat/festival names for the home Today strip. Never errors: a
    failure is an empty list, and the strip simply shows nothing."""
    items: list[dict] = []
    upcoming = None
    day = None
    try:
        zone = tz or geo.timezone_for(lat, lon)
        day = dt.datetime.now(ZoneInfo(zone)).date()
        items = [{"key": o["key"], "name_en": o["name_en"], "name_hi": o["name_hi"],
                  "major": o["major"]}
                 for o in festivals.on(day, lat, lon, zone)]
        # On an ordinary day the strip says what is coming next instead of
        # nothing, so the vrat-tyohar page is always one tap from home.
        if not items:
            nxt = next(iter(festivals.observances(day + dt.timedelta(days=1),
                                                   day + dt.timedelta(days=30), lat, lon, zone)), None)
            if nxt:
                when = dt.date.fromisoformat(nxt["date"])
                upcoming = {"date": nxt["date"], "name_en": nxt["name_en"],
                            "name_hi": nxt["name_hi"], "day_en": _short_date(when, EN),
                            "day_hi": _short_date(when, HI)}
    except Exception:                                  # pragma: no cover - defensive
        items = []
    body = {"date": day.isoformat() if day else None, "items": items, "next": upcoming,
            "url": hub_path(EN), "url_hi": hub_path(HI)}
    return JSONResponse(body, headers={"Cache-Control": "private, max-age=1800"})


# --------------------------------------------------------------------------
# One day's observances with their timings: the Panchang tool and pages
# --------------------------------------------------------------------------

DAY_RANGE_DAYS = 2 * 366              # /api/vrat/day answers within ~2 years of today


def _timing_json(t: dict, day: dt.date) -> dict:
    """A timing exactly as the engine validated it (nothing added, nothing
    invented), plus the other day's short label in EN/HI when it falls on
    another date (Ekadashi parana is the next morning)."""
    out = {k: t[k] for k in ("key", "label_en", "label_hi", "start", "end", "at", "date")
           if t.get(k)}
    if t.get("date") and t["date"] != day.isoformat():
        ref = dt.date.fromisoformat(t["date"])
        out["day_en"], out["day_hi"] = _short_date(ref, EN), _short_date(ref, HI)
    return out


def day_items(day: dt.date, lat: float, lon: float, tz: str) -> list[dict]:
    """The observances of `day` at a place, each with its timings and the page it
    links to (its festival or Ekadashi page, else the vrat-tyohar hub)."""
    return [{
        "key": o["key"], "name_en": o["name_en"], "name_hi": o["name_hi"], "major": o["major"],
        "url": _link_for(o, EN) or hub_path(EN), "url_hi": _link_for(o, HI) or hub_path(HI),
        "timings": [_timing_json(t, day) for t in o["timings"]],
    } for o in festivals.on(day, lat, lon, tz)]


def panchang_block(day: dt.date, lat: float, lon: float, tz: str, lang: str) -> str:
    """'Vrat & festivals today' for the server-rendered /panchang pages: each
    observance linked to its page, with its timings for this city. Empty on an
    ordinary day, and on any failure (the panchang itself must still render)."""
    try:
        rows = festivals.on(day, lat, lon, tz)
    except Exception:                                  # pragma: no cover - defensive
        return ""
    if not rows:
        return ""
    parts = []
    for o in rows:
        href = _link_for(o, lang) or hub_path(lang)
        times = "".join(f"<li>{_e(_timing_text(t, _date(o), lang))}</li>" for t in o["timings"])
        parts.append(f'<h3><a href="{_e(href)}">{_e(_name(o, lang))}</a></h3>'
                     + (f"<ul>{times}</ul>" if times else ""))
    heading = "आज के व्रत-त्योहार" if lang == HI else "Vrat &amp; Festivals today"
    return f'<h2>{heading}</h2><div class="box today vrat-day">{"".join(parts)}</div>'


@router.get("/api/vrat/day")
def vrat_day(
    date: str = "",
    lat: float = Query(CITY.latitude, ge=-90, le=90),
    lon: float = Query(CITY.longitude, ge=-180, le=180),
    tz: str = "",
) -> JSONResponse:
    """One date's vrat/festivals at a place with every validated timing (puja
    muhurat, parana, moonrise, pradosh, nishita...) labelled in English and
    Hindi, for the Panchang tool's "Vrat & festivals" section. Never errors: a
    bad or far-off date, or any failure, is an empty list."""
    body: dict = {"date": None, "items": []}
    try:
        zone = tz or geo.timezone_for(lat, lon)
        today = dt.datetime.now(ZoneInfo(zone)).date()
        day = dt.date.fromisoformat(date) if date else today
        items = (day_items(day, lat, lon, zone)
                 if abs((day - today).days) <= DAY_RANGE_DAYS else [])
        body = {"date": day.isoformat(), "day_en": _long_date(day, EN),
                "day_hi": _long_date(day, HI), "items": items}
    except Exception:
        body = {"date": None, "items": []}
    return JSONResponse(body, headers={"Cache-Control": "private, max-age=1800"})
