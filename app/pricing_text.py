"""The words of /pricing (DIVASTRO-149), English and Hindi.

Nothing here states a price, a count or a name: those come from the billing
catalogue and its settings (pricing_pages.py fills the {placeholders}), and what
each product delivers is the catalogue's own blurb. The sentences below are only
the frame around them, and each one is limited to what the code does:

* purchases are one-off (there is no subscription or renewal anywhere in the code);
* the free allowance is billing.FREE_QUESTIONS;
* a hand-written kundali is made by the astrologer named in the settings, with the
  turnaround from the settings;
* the payment sentence depends on the gateway that is really configured.

Another registry language gets this English text under its own prefix, noindex,
with the "translation coming soon" notice (pricing_pages.TRANSLATED).
"""

TEXT: dict[str, dict[str, str]] = {
    "en": {
        "title": "Prices: question packs, reports and Life Book | {brand}",
        "desc": ("What Divine Astro costs, in rupees: {free} free questions, question packs from "
                 "₹{pack_from}, single-topic reports at ₹{report_from}, the Life Book at ₹{book} "
                 "and hand-written kundali."),
        "h1": "Divine Astro prices",
        "crumb": "Prices",
        "lead": ("Start free: {free} questions about your chart cost nothing. After that you pay only "
                 "for what you choose. Every purchase is one-off, there is no subscription, and all "
                 "prices are in Indian rupees (INR)."),
        "free.h2": "What is free",
        "free.p": ("Every new account gets {free} free questions about your chart. Casting your "
                   "kundali, the daily Panchang, Rahu Kaal, Choghadiya, Muhurat and Kundali Milan "
                   "are free tools."),
        "reports.h2": "Single-topic reports",
        "reports.p": "One PDF report on one area of life, read from your own chart. Pick the one you care about.",
        "packs.h2": "Question packs",
        "packs.p": ("Ask in your own words and get an answer read from your chart. A bigger pack "
                    "costs less per question."),
        "book.h2": "Life Book",
        "kundali.h2": "Hand-written kundali",
        "kundali.p": ("Written by hand by {astrologer} and delivered as a scanned PDF, expected in "
                      "about {days} days."),
        "kundali.p0": "Written by hand by our astrologer and delivered as a scanned PDF.",
        "kundali.texts": ("Hand-written kundali readings are prepared from the knowledge of Ravan "
                          "Samhita, Lal Kitab and Jataka Parijata."),
        "th.product": "Product",
        "th.price": "Price",
        "per_q": "₹{value} per question",
        "popular": "Most popular",
        "sample.link": "See a sample",
        "sample.note": "Sample for a fictional chart; yours is cast from your own birth details",
        "pay.h2": "How you pay",
        "pay.gateway": ("You pay on {gateway}'s secure checkout page, in rupees. The payment "
                        "methods you can choose are the ones {gateway} shows there."),
        "pay.upi": ("You pay by UPI: scan the QR code or pay to our UPI ID, then enter the last 5 "
                    "characters of the payment reference (UTR). We match the payment by hand, so "
                    "credits are added once it is confirmed."),
        "pay.test": "A secure checkout page opens when you choose a product.",
        "pay.orders": "Every order, with its status, is listed under My orders in the app.",
        "refund.h2": "Refunds and cancellation",
        "refund.p": ("Please read the {refund} policy before you buy. The {terms} apply to every "
                     "purchase."),
        "refund.link": "Refund &amp; Cancellation",
        "terms.link": "Terms &amp; Conditions",
        "cta": "Start free",
        "cta.sub": "Cast your kundali in about 30 seconds. No card needed.",
        "faq.h2": "Questions about pricing",
        "faq.free_q": "Is Divine Astro free?",
        "faq.free_a": ("Yes, to start: {free} questions about your chart are free, and the kundali, "
                       "Panchang, Rahu Kaal, Choghadiya, Muhurat and Kundali Milan tools cost "
                       "nothing. Question packs, reports, the Life Book and hand-written kundali "
                       "are paid."),
        "faq.cost_q": "How much does a question cost?",
        "faq.cost_a": ("{packs}. The bigger the pack, the lower the price per question."),
        "faq.pay_q": "How do I pay?",
        "faq.refund_q": "Can I get a refund?",
        "faq.refund_a": ("Refunds and cancellation are covered on our Refund & Cancellation "
                         "page, divineastro.org/refund. Please read it before you buy."),
        "pack_item": "{count} questions for ₹{price} (₹{each} each)",
        "related.h2": "More from Divine Astro",
        "related.kundali": "Free kundali",
        "related.milan": "Kundali Milan",
        "related.panchang": "Today's Panchang",
        "related.sitemap": "Site map",
        "offer.pill": "Diwali offer · ends {date}",
        "offer.banner": "Diwali offer prices are valid until {date}, 11:59 PM IST. Regular prices apply after that.",
        "offer.h2": "About the Diwali offer",
        "offer.p1": ("Every product on this page is on our Diwali offer: the question packs, the "
                     "single-topic reports, the Life Book and the hand-written kundali. The offer "
                     "ends on {date}, 11:59 PM IST."),
        "offer.p2": ("After that the regular prices apply automatically. While the offer lasts, each "
                     "regular price is shown struck through beside the offer price. An order you "
                     "start during the offer keeps the price it was quoted at."),
        "offer.was": "Regular price",
        "offer.now": "now",
        "offer.save": "Save {n}%",
    },
    "hi": {
        "title": "कीमतें: प्रश्न पैक, रिपोर्ट और लाइफ बुक | {brand}",
        "desc": ("डिवाइन एस्ट्रो की कीमतें रुपयों में: {free} मुफ़्त प्रश्न, प्रश्न पैक ₹{pack_from} से, "
                 "एक विषय की रिपोर्ट ₹{report_from} में, लाइफ बुक ₹{book} में और हस्तलिखित कुंडली।"),
        "h1": "डिवाइन एस्ट्रो की कीमतें",
        "crumb": "कीमतें",
        "lead": ("मुफ़्त से शुरू करें: आपकी कुंडली पर {free} प्रश्न बिल्कुल मुफ़्त हैं। उसके बाद आप वही "
                 "चुनते हैं जो आपको चाहिए। हर खरीद एकमुश्त है, कोई सब्सक्रिप्शन नहीं, और सभी कीमतें "
                 "भारतीय रुपयों (INR) में हैं।"),
        "free.h2": "क्या मुफ़्त है",
        "free.p": ("हर नए खाते को आपकी कुंडली पर {free} मुफ़्त प्रश्न मिलते हैं। कुंडली बनाना, दैनिक "
                   "पंचांग, राहु काल, चौघड़िया, मुहूर्त और कुंडली मिलान मुफ़्त टूल हैं।"),
        "reports.h2": "एक विषय की रिपोर्ट",
        "reports.p": "जीवन के एक क्षेत्र पर एक PDF रिपोर्ट, आपकी अपनी कुंडली से। वही चुनें जो आपके लिए ज़रूरी हो।",
        "packs.h2": "प्रश्न पैक",
        "packs.p": ("अपने शब्दों में पूछिए और अपनी कुंडली से पढ़ा हुआ उत्तर पाइए। बड़ा पैक लेने पर "
                    "प्रति प्रश्न कीमत कम पड़ती है।"),
        "book.h2": "लाइफ बुक",
        "kundali.h2": "हस्तलिखित कुंडली",
        "kundali.p": ("{astrologer} द्वारा हाथ से लिखी और स्कैन की गई PDF के रूप में भेजी जाती है, "
                      "लगभग {days} दिन में अपेक्षित।"),
        "kundali.p0": "हमारे ज्योतिषी द्वारा हाथ से लिखी और स्कैन की गई PDF के रूप में भेजी जाती है।",
        "kundali.texts": ("हस्तलिखित कुंडली रावण संहिता, लाल किताब और जातक पारिजात के ज्ञान के आधार पर "
                          "तैयार की जाती है।"),
        "th.product": "उत्पाद",
        "th.price": "कीमत",
        "per_q": "₹{value} प्रति प्रश्न",
        "popular": "सबसे लोकप्रिय",
        "sample.link": "नमूना देखें",
        "sample.note": "काल्पनिक कुंडली का नमूना; आपकी रिपोर्ट आपके अपने जन्म विवरण से बनती है",
        "pay.h2": "भुगतान कैसे करें",
        "pay.gateway": ("भुगतान रुपयों में {gateway} के सुरक्षित चेकआउट पेज पर होता है। भुगतान के जो "
                        "तरीके चुन सकते हैं, वे वही हैं जो {gateway} वहाँ दिखाता है।"),
        "pay.upi": ("भुगतान UPI से होता है: QR कोड स्कैन करें या हमारी UPI ID पर भेजें, फिर भुगतान "
                    "संदर्भ (UTR) के आख़िरी 5 अक्षर लिखें। हम भुगतान हाथ से मिलाते हैं, इसलिए पुष्टि "
                    "होने पर ही प्रश्न जुड़ते हैं।"),
        "pay.test": "उत्पाद चुनते ही सुरक्षित चेकआउट पेज खुलता है।",
        "pay.orders": "हर ऑर्डर अपनी स्थिति के साथ ऐप में मेरे ऑर्डर में दिखता है।",
        "refund.h2": "रिफंड और रद्दीकरण",
        "refund.p": "खरीदने से पहले कृपया {refund} नीति पढ़ लें। हर खरीद पर {terms} लागू होती हैं।",
        "refund.link": "रिफंड और रद्दीकरण",
        "terms.link": "नियम व शर्तें",
        "cta": "मुफ़्त शुरू करें",
        "cta.sub": "लगभग 30 सेकंड में अपनी कुंडली बनाइए। कार्ड की ज़रूरत नहीं।",
        "faq.h2": "कीमतों के बारे में प्रश्न",
        "faq.free_q": "क्या डिवाइन एस्ट्रो मुफ़्त है?",
        "faq.free_a": ("शुरुआत के लिए हाँ: आपकी कुंडली पर {free} प्रश्न मुफ़्त हैं, और कुंडली, पंचांग, राहु "
                       "काल, चौघड़िया, मुहूर्त और कुंडली मिलान टूल मुफ़्त हैं। प्रश्न पैक, रिपोर्ट, लाइफ "
                       "बुक और हस्तलिखित कुंडली सशुल्क हैं।"),
        "faq.cost_q": "एक प्रश्न की कीमत क्या है?",
        "faq.cost_a": "{packs}। पैक जितना बड़ा, प्रति प्रश्न कीमत उतनी कम।",
        "faq.pay_q": "भुगतान कैसे करूँ?",
        "faq.refund_q": "क्या रिफंड मिल सकता है?",
        "faq.refund_a": ("रिफंड और रद्दीकरण की जानकारी हमारे रिफंड और रद्दीकरण पेज "
                         "divineastro.org/refund पर है। खरीदने से पहले कृपया उसे पढ़ लें।"),
        "pack_item": "{count} प्रश्न ₹{price} में (₹{each} प्रति प्रश्न)",
        "related.h2": "डिवाइन एस्ट्रो में और",
        "related.kundali": "मुफ़्त कुंडली",
        "related.milan": "कुंडली मिलान",
        "related.panchang": "आज का पंचांग",
        "related.sitemap": "साइट मैप",
        "offer.pill": "दिवाली ऑफ़र · अंतिम तिथि {date}",
        "offer.banner": "दिवाली ऑफ़र की कीमतें {date}, रात 11:59 बजे (IST) तक मान्य हैं। उसके बाद सामान्य कीमतें लागू होंगी।",
        "offer.h2": "दिवाली ऑफ़र के बारे में",
        "offer.p1": ("इस पेज पर दिया हर उत्पाद हमारे दिवाली ऑफ़र में है: प्रश्न पैक, एक विषय की रिपोर्ट, "
                     "लाइफ बुक और हस्तलिखित कुंडली। ऑफ़र {date}, रात 11:59 बजे (IST) समाप्त होता है।"),
        "offer.p2": ("उसके बाद सामान्य कीमतें अपने आप लागू हो जाती हैं। ऑफ़र के दौरान हर ऑफ़र कीमत के "
                     "पास उसकी सामान्य कीमत कटी हुई दिखाई जाती है। ऑफ़र के दौरान शुरू किया गया ऑर्डर उसी "
                     "कीमत पर रहता है जो उसे बताई गई थी।"),
        "offer.was": "सामान्य कीमत",
        "offer.now": "अब",
        "offer.save": "{n}% बचत",
    },
}
