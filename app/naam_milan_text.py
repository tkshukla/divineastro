"""The text of /naam-se-kundali-milan (naam_milan.py), per language.

TRANSLATORS: this file is data. To translate the page into, say, Kannada, add a
"kn" dict to TEXT with any subset of the "en" keys; the page shares
nakshatra_pages' TRANSLATED set (add "kn" there once nakshatra_page_text is
done too). A key you leave out falls back to English.

* Templates keep their `{placeholders}`; word order around them is yours.
* Values are HTML unless marked "plain text"; placeholder values arrive
  already escaped. Nakshatra/rashi names come from app/astro/names_<code>.py;
  the koota labels, verdict and notes of a result come from the matching
  engine (English or Hindi) — names_<code>.KOOTA labels the kootas elsewhere.
"""

from __future__ import annotations

TEXT: dict[str, dict[str, str]] = {
    "en": {
        # plain text: {brand}
        "title": "Naam se Kundali Milan — Match 36 Gunas by Name, Free | {brand}",
        "desc": ("Kundali milan by name: the first syllable of the boy's and girl's names "
                 "gives each nakshatra and rashi, then the full 36-guna Ashtakoot match. "
                 "Type names in Hindi or English — free, no sign-up."),
        "crumb": "Naam se Kundali Milan",
        "h1": "<h1>Naam se Kundali Milan — Match by Name</h1>",
        "sub": '<p class="hi" lang="hi">नाम से कुंडली मिलान</p>',
        "intro": ("<p>When birth times are not known, tradition matches a couple by the "
                  "<strong>first syllable of their names</strong>. Type both names in Hindi or "
                  "English: we show the syllable used, its nakshatra pada and rashi, and the full "
                  "36-guna match.</p>"),
        "open_milan": "Open birth-chart Kundali Milan",
        # the form (plain text)
        "auto": "Automatic, from the name",
        "alt_head": "Other likely syllables for this name",
        "all_head": "All 108 syllables",
        "boy_label": "Boy's name (groom)",
        "girl_label": "Girl's name (bride)",
        "boy_ph": "e.g. Ram or राम",
        "girl_ph": "e.g. Sita or सीता",
        "pick": "Change the first syllable",
        "button": "Match the gunas",
        # how the syllable was read (plain text)
        "via.abhijit": ("This syllable belongs to Abhijit, the 28th nakshatra; in the 27-nakshatra "
                        "wheel it is counted in Uttara Ashadha pada 4."),
        "via.alias": "By the traditional rule, ब is read as व, and श as ष (with the a-vowel) or स.",
        "via.nearest": ("This exact syllable is not in the 108-syllable list, so the nearest syllable "
                        "with the same consonant was used — change it below if you prefer."),
        "via.latin": ("An English spelling cannot settle this syllable (e.g. T = त or ट), so the most "
                      "common reading was used — pick another below if needed."),
        "via.chosen": "You chose this syllable.",
        # the result
        "unreadable": "Could not read a first syllable from this name — pick one from the list below.",
        "pada": "pada",
        "result": "Result",
        "res.head": "<tr><th></th><th>First syllable</th><th>Nakshatra</th><th>Rashi</th></tr>",
        "boy": "Boy",
        "girl": "Girl",
        "res.th": "<tr><th>Koota</th><th>Points</th><th>Why</th></tr>",
        "total": "Total",
        "mangal": ("<strong>Mangal dosha: not applicable.</strong> Mangal dosha depends on where "
                   "Mars stood from the Lagna, Moon and Venus at birth — a name cannot tell you "
                   "that. Use birth-chart matching for it."),
        "res.cta": "Match by birth details instead — more accurate, free",
        "caveat": ('<div class="box"><p><strong>Please note:</strong> name-based matching is a '
                   "traditional shortcut, used when birth details are not known. It assumes each name "
                   "was chosen from the syllable of the person's birth nakshatra — which today is often "
                   "not the case. Matching from the date, time and place of birth is far more accurate, "
                   "and is the only way to check Mangal dosha.</p></div>"),
        "syl.head": "<tr><th>Rashi</th><th>Name syllables</th></tr>",
        # HTML: {abhijit} {syllables} {href}
        "explainer": """
<h2>How name-based matching works</h2>
<p>Each of the 27 nakshatras has four padas, and each pada has a syllable (namakshar) — 108 in
all. The pada whose syllable a name <strong>begins with</strong> is taken as that person's
nakshatra, and its sign as their Moon sign. The same <strong>Ashtakoot (36 guna)</strong> match
used with birth charts — Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot and Nadi — is
then computed from those two nakshatras, by the very engine behind our Kundali Milan tool.</p>
<h3>How the first syllable is read</h3>
<ul>
<li>The first consonant of the first akshar and its vowel: <strong>Priya / प्रिया → पी</strong>,
<strong>Kshitij / क्षितिज → की</strong>. Long and short vowels count the same (इ/ई, उ/ऊ);
ऐ counts as ए and औ as ओ.</li>
<li>ब is read as व, and श as ष (with the a-vowel) or स; ऋ as री.</li>
<li>Abhijit's syllables ({abhijit}) are counted in Uttara Ashadha pada 4.</li>
<li>Names typed in English are transliterated; letters such as T, D, N, Th and Dh can stand for
two Hindi letters (त/ट, द/ड), so the result shows which syllable was used and lets you pick
another. Hindi (Devanagari) input is read exactly.</li>
</ul>
<h3>Name syllables by rashi</h3>
{syllables}
<p>For each nakshatra's syllables, deity, gana and nadi see <a href="{href}">all 27
nakshatras</a>.</p>""",
    },

    "hi": {
        "title": "नाम से कुंडली मिलान — नाम के पहले अक्षर से 36 गुण मिलान, मुफ़्त | {brand}",
        "desc": ("नाम से कुंडली मिलान: वर और कन्या के नाम के पहले अक्षर से नक्षत्र और राशि "
                 "निकालकर अष्टकूट 36 गुण मिलान। हिंदी या अंग्रेज़ी में नाम लिखें — मुफ़्त, "
                 "बिना साइन-अप।"),
        "crumb": "नाम से कुंडली मिलान",
        "h1": "<h1>नाम से कुंडली मिलान</h1>",
        "sub": '<p class="hi" lang="en">Naam se Kundali Milan — match by name</p>',
        "intro": ("<p>जन्म समय पता न हो तो परंपरा में <strong>नाम के पहले अक्षर</strong> से गुण "
                  "मिलाए जाते हैं। दोनों के नाम हिंदी या अंग्रेज़ी में लिखें — हम पहला अक्षर, उसका "
                  "नक्षत्र-चरण और राशि दिखाएँगे और पूरे 36 गुणों का मिलान करेंगे।</p>"),
        "open_milan": "जन्म विवरण से कुंडली मिलान खोलें",
        "auto": "नाम से अपने-आप",
        "alt_head": "इस नाम के अन्य संभावित अक्षर",
        "all_head": "सभी 108 नामाक्षर",
        "boy_label": "वर (लड़के) का नाम",
        "girl_label": "कन्या (लड़की) का नाम",
        "boy_ph": "जैसे राम या Ram",
        "girl_ph": "जैसे सीता या Sita",
        "pick": "पहला अक्षर बदलें",
        "button": "गुण मिलाएँ",
        "via.abhijit": ("यह अक्षर अभिजित (28वें) नक्षत्र का है; 27-नक्षत्र पद्धति में इसे उत्तराषाढ़ा "
                        "के चौथे चरण में गिना गया है।"),
        "via.alias": "परंपरा के अनुसार ब को व, और श को ष (अ-स्वर के साथ) या स माना गया है।",
        "via.nearest": ("यह सटीक अक्षर 108 की सूची में नहीं है, इसलिए उसी व्यंजन का निकटतम अक्षर लिया "
                        "गया है — चाहें तो नीचे से बदलें।"),
        "via.latin": ("अंग्रेज़ी वर्तनी से यह अक्षर निश्चित नहीं होता (जैसे T = त या ट), इसलिए सबसे "
                      "सामान्य पढ़त ली गई है — नीचे से दूसरा अक्षर चुन सकते हैं।"),
        "via.chosen": "यह अक्षर आपने स्वयं चुना है।",
        "unreadable": "इस नाम का पहला अक्षर पहचाना नहीं जा सका — नीचे की सूची से अक्षर चुनें।",
        "pada": "चरण",
        "result": "परिणाम",
        "res.head": "<tr><th></th><th>पहला अक्षर</th><th>नक्षत्र</th><th>राशि</th></tr>",
        "boy": "वर",
        "girl": "कन्या",
        "res.th": "<tr><th>कूट</th><th>गुण</th><th>विवरण</th></tr>",
        "total": "कुल गुण",
        "mangal": ("<strong>मांगलिक दोष: लागू नहीं।</strong> मांगलिक दोष जन्म के समय मंगल की लग्न, "
                   "चंद्र और शुक्र से स्थिति पर निर्भर है — नाम से इसका पता नहीं चल सकता। इसके लिए "
                   "जन्म कुंडली से मिलान करें।"),
        "res.cta": "जन्म विवरण से सटीक कुंडली मिलान करें — मुफ़्त",
        "caveat": ('<div class="box"><p><strong>ध्यान दें:</strong> नाम से मिलान एक पारंपरिक '
                   "शॉर्टकट है, जो तब प्रयोग होता है जब जन्म समय ज्ञात न हो। यह मानकर चलता है कि नाम "
                   "जन्म नक्षत्र के अक्षर से रखा गया था — जो आज अक्सर सच नहीं होता। जन्म तिथि, समय और "
                   "स्थान से किया गया कुंडली मिलान कहीं अधिक सटीक है, और मांगलिक दोष भी उसी से देखा "
                   "जा सकता है।</p></div>"),
        "syl.head": "<tr><th>राशि</th><th>नामाक्षर</th></tr>",
        "explainer": """
<h2>नाम से कुंडली मिलान कैसे होता है</h2>
<p>हर नक्षत्र के चार चरण हैं और हर चरण का एक अक्षर (नामाक्षर) है — कुल 108 अक्षर। नाम का
<strong>पहला अक्षर</strong> जिस चरण का है, वही उस व्यक्ति का नक्षत्र और उसकी राशि मानी जाती है।
फिर इन दोनों नक्षत्रों और राशियों से वही <strong>अष्टकूट (36 गुण)</strong> मिलान किया जाता है जो
जन्म कुंडली से होता है — वर्ण, वश्य, तारा, योनि, ग्रह मैत्री, गण, भकूट और नाड़ी। यहाँ गणना हमारे
कुंडली मिलान टूल के ही इंजन से होती है।</p>
<h3>अक्षर कैसे पढ़ा जाता है</h3>
<ul>
<li>पहले अक्षर का पहला व्यंजन और उसकी मात्रा ली जाती है: <strong>प्रिया → पी</strong>,
<strong>क्षितिज → की</strong>; छोटी-बड़ी मात्रा (इ/ई, उ/ऊ) में अंतर नहीं किया जाता, ऐ को ए और औ को ओ
माना जाता है।</li>
<li>ब को व, और श को ष (अ के साथ) या स माना जाता है; ऋ को री।</li>
<li>अभिजित नक्षत्र के अक्षर ({abhijit}) उत्तराषाढ़ा के चौथे चरण में गिने जाते हैं।</li>
<li>अंग्रेज़ी में लिखे नाम में T/D/N/Th/Dh जैसे अक्षर दो तरह पढ़े जा सकते हैं (त/ट, द/ड) — परिणाम में
दिखाया जाता है कि कौन-सा अक्षर लिया गया, और आप सूची से दूसरा चुन सकते हैं।</li>
</ul>
<h3>राशि अनुसार नामाक्षर</h3>
{syllables}
<p>हर नक्षत्र के अक्षर, देवता, गण और नाड़ी के लिए <a href="{href}">27 नक्षत्रों की सूची</a>
देखें।</p>""",
    },
    "bn": {
        "title": "নাম দিয়ে যোটক বিচার — নামের আদ্যক্ষরে 36 গুণ মিলন, বিনামূল্যে | {brand}",
        "desc": ("নাম দিয়ে যোটক বিচার: পাত্র ও পাত্রীর নামের প্রথম অক্ষর থেকে নক্ষত্র ও রাশি "
                 "বের করে পূর্ণ অষ্টকূট 36 গুণ মিলন। নাম ইংরেজি বা হিন্দিতে লিখুন — বিনামূল্যে, "
                 "সাইন-আপ ছাড়াই।"),
        "crumb": "নাম দিয়ে যোটক বিচার",
        "h1": "<h1>নাম দিয়ে যোটক বিচার — নামের অক্ষরে গুণ মিলন</h1>",
        "sub": '<p class="hi">নামের প্রথম অক্ষর থেকে নক্ষত্র, রাশি ও 36 গুণ</p>',
        "intro": ("<p>জন্মের সময় জানা না থাকলে প্রথা অনুযায়ী দুজনের <strong>নামের প্রথম "
                  "অক্ষর</strong> দিয়ে মিলন করা হয়। দুজনের নাম ইংরেজি বা হিন্দি (দেবনাগরী) হরফে "
                  "লিখুন: আমরা দেখাব কোন অক্ষর ধরা হয়েছে, তার নক্ষত্র-পদ ও রাশি, এবং পূর্ণ 36 "
                  "গুণের মিলন।</p>"),
        "open_milan": "জন্মকুণ্ডলী দিয়ে যোটক বিচার খুলুন",
        "auto": "নাম থেকে আপনা-আপনি",
        "alt_head": "এই নামের সম্ভাব্য অন্য অক্ষর",
        "all_head": "সব 108টি নামাক্ষর",
        "boy_label": "পাত্রের (ছেলের) নাম",
        "girl_label": "পাত্রীর (মেয়ের) নাম",
        "boy_ph": "যেমন Ram",
        "girl_ph": "যেমন Sita",
        "pick": "প্রথম অক্ষর বদলান",
        "button": "গুণ মিলিয়ে দেখুন",
        "via.abhijit": ("এই অক্ষরটি অভিজিৎ, অর্থাৎ 28তম নক্ষত্রের; 27-নক্ষত্রের চক্রে একে "
                        "উত্তরাষাঢ়ার চতুর্থ পদে গণনা করা হয়।"),
        "via.alias": ("প্রথাগত নিয়মে বর্গীয় ‘ব’-কে অন্তঃস্থ ‘ব’ (ওয়া-ধ্বনি) হিসেবে, আর ‘শ’-কে "
                      "‘ষ’ (অ-কারসহ) বা ‘স’ হিসেবে পড়া হয়েছে।"),
        "via.nearest": ("এই অক্ষরটি হুবহু 108টির তালিকায় নেই, তাই একই ব্যঞ্জনের সবচেয়ে কাছের "
                        "অক্ষরটি নেওয়া হয়েছে — চাইলে নিচে বদলে নিন।"),
        "via.latin": ("ইংরেজি বানান থেকে এই অক্ষরটি নিশ্চিত করা যায় না (যেমন T = ত না ট), তাই "
                      "সবচেয়ে প্রচলিত উচ্চারণ ধরা হয়েছে — দরকার হলে নিচে অন্যটি বেছে নিন।"),
        "via.chosen": "এই অক্ষরটি আপনি নিজে বেছে নিয়েছেন।",
        "unreadable": "এই নাম থেকে প্রথম অক্ষর পড়া গেল না — নিচের তালিকা থেকে একটি বেছে নিন।",
        "pada": "পদ",
        "result": "ফলাফল",
        "res.head": "<tr><th></th><th>প্রথম অক্ষর</th><th>নক্ষত্র</th><th>রাশি</th></tr>",
        "boy": "পাত্র",
        "girl": "পাত্রী",
        "res.th": "<tr><th>কূট</th><th>গুণ</th><th>কারণ</th></tr>",
        "total": "মোট গুণ",
        "mangal": ("<strong>মাঙ্গলিক দোষ: প্রযোজ্য নয়।</strong> মাঙ্গলিক দোষ নির্ভর করে জন্মের "
                   "সময় লগ্ন, চন্দ্র ও শুক্র থেকে মঙ্গল কোথায় ছিল তার ওপর — নাম থেকে তা জানা যায় "
                   "না। এর জন্য জন্মকুণ্ডলী দিয়ে মিলন করুন।"),
        "res.cta": "বরং জন্মের বিবরণ দিয়ে মেলান — আরও নির্ভুল, বিনামূল্যে",
        "caveat": ('<div class="box"><p><strong>দয়া করে মনে রাখবেন:</strong> নাম দিয়ে মিলন একটি '
                   "প্রথাগত সংক্ষিপ্ত পদ্ধতি, যা জন্মের বিবরণ জানা না থাকলে ব্যবহার হয়। এটি ধরে নেয় "
                   "যে নামটি জন্মনক্ষত্রের অক্ষর থেকে রাখা হয়েছিল — আজকাল প্রায়ই যা হয় না। জন্মের "
                   "তারিখ, সময় ও স্থান দিয়ে করা যোটক বিচার অনেক বেশি নির্ভুল, এবং মাঙ্গলিক দোষ "
                   "কেবল সেভাবেই দেখা যায়।</p></div>"),
        "syl.head": "<tr><th>রাশি</th><th>নামাক্ষর</th></tr>",
        "explainer": """
<h2>নাম দিয়ে মিলন কীভাবে হয়</h2>
<p>27টি নক্ষত্রের প্রত্যেকটির চারটি পদ, আর প্রতিটি পদের একটি অক্ষর (নামাক্ষর) — সব মিলিয়ে
108টি। নামটি যে পদের অক্ষর দিয়ে <strong>শুরু হয়</strong>, সেটিই ওই ব্যক্তির নক্ষত্র, আর তার রাশিই
চন্দ্ররাশি ধরা হয়। তারপর এই দুটি নক্ষত্র থেকে সেই একই <strong>অষ্টকূট (36 গুণ)</strong> মিলন
করা হয়, যা জন্মকুণ্ডলী দিয়ে করা হয় — বর্ণ, বশ্য, তারা, যোনি, গ্রহমৈত্রী, গণ, রাশিকূট ও নাড়ী —
আমাদের যোটক বিচার টুলের সেই একই গণনা-পদ্ধতিতে।</p>
<h3>প্রথম অক্ষর কীভাবে পড়া হয়</h3>
<ul>
<li>প্রথম অক্ষরের প্রথম ব্যঞ্জন ও তার স্বরচিহ্ন নেওয়া হয়: <strong>Priya → পী</strong>,
<strong>Kshitij → কী</strong>। হ্রস্ব ও দীর্ঘ স্বর একই ধরা হয় (ই/ঈ, উ/ঊ); ঐ-কে এ আর ঔ-কে ও
ধরা হয়।</li>
<li>বর্গীয় ‘ব’-কে অন্তঃস্থ ‘ব’ (ওয়া-ধ্বনি), আর ‘শ’-কে ‘ষ’ (অ-কারসহ) বা ‘স’ হিসেবে পড়া হয়; ঋ-কে রী।</li>
<li>অভিজিৎ নক্ষত্রের অক্ষর ({abhijit}) উত্তরাষাঢ়ার চতুর্থ পদে গণনা করা হয়।</li>
<li>ইংরেজিতে লেখা নাম লিপ্যন্তর করে পড়া হয়; T, D, N, Th, Dh-এর মতো অক্ষর দুটি আলাদা অক্ষর
বোঝাতে পারে (ত/ট, দ/ড), তাই ফলাফলে দেখানো হয় কোন অক্ষর ধরা হয়েছে, আর আপনি অন্যটি বেছে নিতে
পারেন। হিন্দি (দেবনাগরী) হরফে লেখা নাম হুবহু পড়া হয়।</li>
</ul>
<h3>রাশি অনুযায়ী নামাক্ষর</h3>
{syllables}
<p>প্রতিটি নক্ষত্রের অক্ষর, দেবতা, গণ ও নাড়ী জানতে দেখুন <a href="{href}">27টি নক্ষত্রের
তালিকা</a>।</p>""",
    },

    "or": {
        "title": "ନାମରୁ କୁଣ୍ଡଳୀ ମିଳନ — ନାମର ପ୍ରଥମ ଅକ୍ଷରରୁ 36 ଗୁଣ ମିଳନ, ମାଗଣା | {brand}",
        "desc": ("ନାମରୁ କୁଣ୍ଡଳୀ ମିଳନ: ବର ଓ କନ୍ୟାଙ୍କ ନାମର ପ୍ରଥମ ଅକ୍ଷରରୁ ନକ୍ଷତ୍ର ଓ ରାଶି ବାହାର "
                 "କରି ସମ୍ପୂର୍ଣ୍ଣ ଅଷ୍ଟକୂଟ 36 ଗୁଣ ମିଳନ। ନାମ ଇଂରାଜୀ ବା ହିନ୍ଦୀରେ ଲେଖନ୍ତୁ — ମାଗଣା, "
                 "ସାଇନ୍-ଅପ୍ ବିନା।"),
        "crumb": "ନାମରୁ କୁଣ୍ଡଳୀ ମିଳନ",
        "h1": "<h1>ନାମରୁ କୁଣ୍ଡଳୀ ମିଳନ — ନାମ ଅକ୍ଷରରେ ଗୁଣ ମିଳନ</h1>",
        "sub": '<p class="hi">ନାମର ପ୍ରଥମ ଅକ୍ଷରରୁ ନକ୍ଷତ୍ର, ରାଶି ଓ 36 ଗୁଣ</p>',
        "intro": ("<p>ଜନ୍ମ ସମୟ ଜଣା ନଥିଲେ ପରମ୍ପରା ଅନୁସାରେ ଦୁହିଁଙ୍କ <strong>ନାମର ପ୍ରଥମ "
                  "ଅକ୍ଷର</strong>ରୁ ମିଳନ କରାଯାଏ। ଦୁହିଁଙ୍କ ନାମ ଇଂରାଜୀ ବା ହିନ୍ଦୀ (ଦେବନାଗରୀ) ଅକ୍ଷରରେ "
                  "ଲେଖନ୍ତୁ: ଆମେ ଦେଖାଇବୁ କେଉଁ ଅକ୍ଷର ନିଆଗଲା, ତାର ନକ୍ଷତ୍ର-ପାଦ ଓ ରାଶି, ଏବଂ ସମ୍ପୂର୍ଣ୍ଣ "
                  "36 ଗୁଣର ମିଳନ।</p>"),
        "open_milan": "ଜନ୍ମ କୁଣ୍ଡଳୀରୁ କୁଣ୍ଡଳୀ ମିଳନ ଖୋଲନ୍ତୁ",
        "auto": "ନାମରୁ ସ୍ୱୟଂଚାଳିତ",
        "alt_head": "ଏହି ନାମର ଅନ୍ୟ ସମ୍ଭାବ୍ୟ ଅକ୍ଷର",
        "all_head": "ସମସ୍ତ 108 ନାମାକ୍ଷର",
        "boy_label": "ବରଙ୍କ (ପୁଅର) ନାମ",
        "girl_label": "କନ୍ୟାଙ୍କ (ଝିଅର) ନାମ",
        "boy_ph": "ଯେପରି Ram",
        "girl_ph": "ଯେପରି Sita",
        "pick": "ପ୍ରଥମ ଅକ୍ଷର ବଦଳାନ୍ତୁ",
        "button": "ଗୁଣ ମିଳାନ୍ତୁ",
        "via.abhijit": ("ଏହି ଅକ୍ଷର ଅଭିଜିତ୍, ଅର୍ଥାତ୍ 28ତମ ନକ୍ଷତ୍ରର; 27-ନକ୍ଷତ୍ର ଚକ୍ରରେ ଏହାକୁ "
                        "ଉତ୍ତରାଷାଢ଼ାର ଚତୁର୍ଥ ପାଦରେ ଗଣାଯାଏ।"),
        "via.alias": ("ପାରମ୍ପରିକ ନିୟମରେ ‘ବ’କୁ ‘ଵ’ ଭାବେ, ଏବଂ ‘ଶ’କୁ ‘ଷ’ (ଅ-କାର ସହିତ) ବା ‘ସ’ "
                      "ଭାବେ ପଢ଼ାଯାଇଛି।"),
        "via.nearest": ("ଏହି ଅକ୍ଷର ଠିକ୍ ସେହିପରି 108ର ତାଲିକାରେ ନାହିଁ, ତେଣୁ ସେହି ବ୍ୟଞ୍ଜନର ସବୁଠାରୁ "
                        "ନିକଟତମ ଅକ୍ଷର ନିଆଯାଇଛି — ଚାହିଁଲେ ତଳେ ବଦଳାନ୍ତୁ।"),
        "via.latin": ("ଇଂରାଜୀ ବନାନରୁ ଏହି ଅକ୍ଷର ନିଶ୍ଚିତ ହୁଏ ନାହିଁ (ଯେପରି T = ତ ବା ଟ), ତେଣୁ "
                      "ସବୁଠାରୁ ପ୍ରଚଳିତ ଉଚ୍ଚାରଣ ନିଆଯାଇଛି — ଆବଶ୍ୟକ ହେଲେ ତଳୁ ଅନ୍ୟଟି ବାଛନ୍ତୁ।"),
        "via.chosen": "ଏହି ଅକ୍ଷର ଆପଣ ନିଜେ ବାଛିଛନ୍ତି।",
        "unreadable": "ଏହି ନାମରୁ ପ୍ରଥମ ଅକ୍ଷର ପଢ଼ାଗଲା ନାହିଁ — ତଳ ତାଲିକାରୁ ଗୋଟିଏ ବାଛନ୍ତୁ।",
        "pada": "ପାଦ",
        "result": "ଫଳାଫଳ",
        "res.head": "<tr><th></th><th>ପ୍ରଥମ ଅକ୍ଷର</th><th>ନକ୍ଷତ୍ର</th><th>ରାଶି</th></tr>",
        "boy": "ବର",
        "girl": "କନ୍ୟା",
        "res.th": "<tr><th>କୂଟ</th><th>ଗୁଣ</th><th>କାରଣ</th></tr>",
        "total": "ମୋଟ ଗୁଣ",
        "mangal": ("<strong>ମାଙ୍ଗଳିକ ଦୋଷ: ପ୍ରଯୁଜ୍ୟ ନୁହେଁ।</strong> ମାଙ୍ଗଳିକ ଦୋଷ ଜନ୍ମ ସମୟରେ "
                   "ଲଗ୍ନ, ଚନ୍ଦ୍ର ଓ ଶୁକ୍ରଙ୍କଠାରୁ ମଙ୍ଗଳ କେଉଁଠି ଥିଲେ ତାହା ଉପରେ ନିର୍ଭର କରେ — ନାମରୁ "
                   "ଏହା ଜାଣିହେବ ନାହିଁ। ଏଥିପାଇଁ ଜନ୍ମ କୁଣ୍ଡଳୀରୁ ମିଳନ କରନ୍ତୁ।"),
        "res.cta": "ବରଂ ଜନ୍ମ ବିବରଣୀରୁ ମିଳାନ୍ତୁ — ଅଧିକ ସଠିକ୍, ମାଗଣା",
        "caveat": ('<div class="box"><p><strong>ଦୟାକରି ଧ୍ୟାନ ଦିଅନ୍ତୁ:</strong> ନାମରୁ ମିଳନ ଏକ '
                   "ପାରମ୍ପରିକ ସଂକ୍ଷିପ୍ତ ପଦ୍ଧତି, ଯାହା ଜନ୍ମ ବିବରଣୀ ଜଣା ନଥିଲେ ବ୍ୟବହାର ହୁଏ। ଏହା ଧରିନିଏ "
                   "ଯେ ନାମଟି ଜନ୍ମ ନକ୍ଷତ୍ରର ଅକ୍ଷରରୁ ରଖାଯାଇଥିଲା — ଯାହା ଆଜିକାଲି ପ୍ରାୟତଃ ହୁଏ ନାହିଁ। "
                   "ଜନ୍ମ ତାରିଖ, ସମୟ ଓ ସ୍ଥାନରୁ କରାଯାଇଥିବା କୁଣ୍ଡଳୀ ମିଳନ ବହୁତ ଅଧିକ ସଠିକ୍, ଏବଂ "
                   "ମାଙ୍ଗଳିକ ଦୋଷ କେବଳ ସେଥିରୁ ହିଁ ଦେଖାଯାଇପାରେ।</p></div>"),
        "syl.head": "<tr><th>ରାଶି</th><th>ନାମାକ୍ଷର</th></tr>",
        "explainer": """
<h2>ନାମରୁ ମିଳନ କିପରି ହୁଏ</h2>
<p>27ଟି ନକ୍ଷତ୍ରର ପ୍ରତ୍ୟେକର ଚାରିଟି ପାଦ, ଏବଂ ପ୍ରତ୍ୟେକ ପାଦର ଗୋଟିଏ ଅକ୍ଷର (ନାମାକ୍ଷର) — ମୋଟ
108ଟି। ନାମଟି ଯେଉଁ ପାଦର ଅକ୍ଷରରେ <strong>ଆରମ୍ଭ ହୁଏ</strong>, ତାହା ସେହି ବ୍ୟକ୍ତିଙ୍କ ନକ୍ଷତ୍ର, ଏବଂ
ତାହାର ରାଶି ତାଙ୍କ ଚନ୍ଦ୍ର ରାଶି ବୋଲି ଧରାଯାଏ। ତାପରେ ଏହି ଦୁଇ ନକ୍ଷତ୍ରରୁ ସେହି ସମାନ <strong>ଅଷ୍ଟକୂଟ
(36 ଗୁଣ)</strong> ମିଳନ କରାଯାଏ ଯାହା ଜନ୍ମ କୁଣ୍ଡଳୀରୁ କରାଯାଏ — ବର୍ଣ୍ଣ, ବଶ୍ୟ, ତାରା, ଯୋନି,
ଗ୍ରହମୈତ୍ରୀ, ଗଣ, ଭକୂଟ ଓ ନାଡ଼ୀ — ଆମର କୁଣ୍ଡଳୀ ମିଳନ ଟୁଲ୍‌ର ସେହି ସମାନ ଗଣନା ପଦ୍ଧତିରେ।</p>
<h3>ପ୍ରଥମ ଅକ୍ଷର କିପରି ପଢ଼ାଯାଏ</h3>
<ul>
<li>ପ୍ରଥମ ଅକ୍ଷରର ପ୍ରଥମ ବ୍ୟଞ୍ଜନ ଓ ତାର ସ୍ୱରଚିହ୍ନ ନିଆଯାଏ: <strong>Priya → ପୀ</strong>,
<strong>Kshitij → କୀ</strong>। ହ୍ରସ୍ୱ ଓ ଦୀର୍ଘ ସ୍ୱର ସମାନ ଧରାଯାଏ (ଇ/ଈ, ଉ/ଊ); ଐକୁ ଏ ଏବଂ ଔକୁ ଓ
ଧରାଯାଏ।</li>
<li>‘ବ’କୁ ‘ଵ’ ଭାବେ, ଏବଂ ‘ଶ’କୁ ‘ଷ’ (ଅ-କାର ସହିତ) ବା ‘ସ’ ଭାବେ ପଢ଼ାଯାଏ; ଋକୁ ରୀ।</li>
<li>ଅଭିଜିତ୍ ନକ୍ଷତ୍ରର ଅକ୍ଷର ({abhijit}) ଉତ୍ତରାଷାଢ଼ାର ଚତୁର୍ଥ ପାଦରେ ଗଣାଯାଏ।</li>
<li>ଇଂରାଜୀରେ ଲେଖାଯାଇଥିବା ନାମ ଲିପ୍ୟନ୍ତର କରି ପଢ଼ାଯାଏ; T, D, N, Th, Dh ଭଳି ଅକ୍ଷର ଦୁଇଟି ଭିନ୍ନ
ଅକ୍ଷର ବୁଝାଇପାରେ (ତ/ଟ, ଦ/ଡ), ତେଣୁ ଫଳାଫଳରେ ଦେଖାଯାଏ କେଉଁ ଅକ୍ଷର ନିଆଗଲା, ଏବଂ ଆପଣ ଅନ୍ୟଟି
ବାଛିପାରିବେ। ହିନ୍ଦୀ (ଦେବନାଗରୀ) ଅକ୍ଷରରେ ଲେଖାଯାଇଥିବା ନାମ ଠିକ୍ ସେହିପରି ପଢ଼ାଯାଏ।</li>
</ul>
<h3>ରାଶି ଅନୁସାରେ ନାମାକ୍ଷର</h3>
{syllables}
<p>ପ୍ରତ୍ୟେକ ନକ୍ଷତ୍ରର ଅକ୍ଷର, ଦେବତା, ଗଣ ଓ ନାଡ଼ୀ ପାଇଁ <a href="{href}">27ଟି ନକ୍ଷତ୍ରର
ତାଲିକା</a> ଦେଖନ୍ତୁ।</p>""",
    },
}
