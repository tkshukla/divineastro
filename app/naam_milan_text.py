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

    # The engine reads names in Devanagari or Latin script only (astro/namakshar.lookup),
    # so the kn/te text keeps "type in Hindi or English" and gives Latin examples.
    "kn": {
        "title": "ಹೆಸರಿನಿಂದ ಜಾತಕ ಹೊಂದಾಣಿಕೆ (ನಾಮ ಮಿಲನ) — 36 ಗುಣ, ಉಚಿತ | {brand}",
        "desc": ("ಹೆಸರಿನಿಂದ ಜಾತಕ ಹೊಂದಾಣಿಕೆ: ವಧು-ವರರ ಹೆಸರಿನ ಮೊದಲ ಅಕ್ಷರದಿಂದ ನಕ್ಷತ್ರ, ರಾಶಿ "
                 "ಮತ್ತು 36 ಗುಣಗಳ ಅಷ್ಟಕೂಟ ಹೊಂದಾಣಿಕೆ. ಹಿಂದಿ ಅಥವಾ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಹೆಸರು "
                 "ಬರೆಯಿರಿ — ಉಚಿತ, ನೋಂದಣಿ ಬೇಡ."),
        "crumb": "ಹೆಸರಿನಿಂದ ಜಾತಕ ಹೊಂದಾಣಿಕೆ",
        "h1": "<h1>ಹೆಸರಿನಿಂದ ಜಾತಕ ಹೊಂದಾಣಿಕೆ (ನಾಮ ಮಿಲನ)</h1>",
        "sub": '<p class="hi">ಹೆಸರಿನ ಮೊದಲ ಅಕ್ಷರದಿಂದ ಗುಣ ಮಿಲನ</p>',
        "intro": ("<p>ಜನ್ಮ ಸಮಯ ತಿಳಿದಿಲ್ಲದಾಗ, ಸಂಪ್ರದಾಯದಲ್ಲಿ ಜೋಡಿಯನ್ನು <strong>ಹೆಸರಿನ ಮೊದಲ "
                  "ಅಕ್ಷರದಿಂದ</strong> ಹೊಂದಿಸಲಾಗುತ್ತದೆ. ಇಬ್ಬರ ಹೆಸರನ್ನೂ ಹಿಂದಿ ಅಥವಾ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ "
                  "ಬರೆಯಿರಿ: ಬಳಸಿದ ಅಕ್ಷರ, ಅದರ ನಕ್ಷತ್ರ ಪಾದ ಮತ್ತು ರಾಶಿ, ಹಾಗೂ ಸಂಪೂರ್ಣ 36 ಗುಣಗಳ "
                  "ಹೊಂದಾಣಿಕೆಯನ್ನು ನಾವು ತೋರಿಸುತ್ತೇವೆ.</p>"),
        "open_milan": "ಜನ್ಮ ಜಾತಕದಿಂದ ಹೊಂದಾಣಿಕೆ ತೆರೆಯಿರಿ",
        "auto": "ಹೆಸರಿನಿಂದ ಸ್ವಯಂಚಾಲಿತವಾಗಿ",
        "alt_head": "ಈ ಹೆಸರಿಗೆ ಸಾಧ್ಯವಿರುವ ಇತರ ಅಕ್ಷರಗಳು",
        "all_head": "ಎಲ್ಲ 108 ನಾಮಾಕ್ಷರಗಳು",
        "boy_label": "ವರನ ಹೆಸರು (ಹುಡುಗ)",
        "girl_label": "ವಧುವಿನ ಹೆಸರು (ಹುಡುಗಿ)",
        "boy_ph": "ಉದಾ. Ram",
        "girl_ph": "ಉದಾ. Sita",
        "pick": "ಮೊದಲ ಅಕ್ಷರ ಬದಲಿಸಿ",
        "button": "ಗುಣ ಹೊಂದಿಸಿ",
        "via.abhijit": ("ಈ ಅಕ್ಷರ 28ನೇ ನಕ್ಷತ್ರವಾದ ಅಭಿಜಿತ್‌ಗೆ ಸೇರಿದೆ; 27 ನಕ್ಷತ್ರಗಳ ಚಕ್ರದಲ್ಲಿ ಇದನ್ನು "
                        "ಉತ್ತರಾಷಾಢ 4ನೇ ಪಾದದಲ್ಲಿ ಎಣಿಸಲಾಗುತ್ತದೆ."),
        "via.alias": ("ಸಂಪ್ರದಾಯದ ನಿಯಮದಂತೆ ಬ ಅನ್ನು ವ ಎಂದು, ಶ ಅನ್ನು ಷ (ಅ-ಸ್ವರದೊಂದಿಗೆ) ಅಥವಾ ಸ "
                      "ಎಂದು ಓದಲಾಗುತ್ತದೆ."),
        "via.nearest": ("ಈ ನಿಖರ ಅಕ್ಷರ 108 ಅಕ್ಷರಗಳ ಪಟ್ಟಿಯಲ್ಲಿ ಇಲ್ಲ, ಆದ್ದರಿಂದ ಅದೇ ವ್ಯಂಜನದ ಹತ್ತಿರದ "
                        "ಅಕ್ಷರವನ್ನು ಬಳಸಲಾಗಿದೆ — ಬೇಕಿದ್ದರೆ ಕೆಳಗೆ ಬದಲಿಸಿ."),
        "via.latin": ("ಇಂಗ್ಲಿಷ್ ಕಾಗುಣಿತದಿಂದ ಈ ಅಕ್ಷರ ಖಚಿತವಾಗುವುದಿಲ್ಲ (ಉದಾ. T = ತ ಅಥವಾ ಟ), "
                      "ಆದ್ದರಿಂದ ಸಾಮಾನ್ಯ ಓದನ್ನು ಬಳಸಲಾಗಿದೆ — ಬೇಕಿದ್ದರೆ ಕೆಳಗೆ ಬೇರೆಯದನ್ನು ಆರಿಸಿ."),
        "via.chosen": "ಈ ಅಕ್ಷರವನ್ನು ನೀವೇ ಆರಿಸಿದ್ದೀರಿ.",
        "unreadable": "ಈ ಹೆಸರಿನಿಂದ ಮೊದಲ ಅಕ್ಷರವನ್ನು ಗುರುತಿಸಲಾಗಲಿಲ್ಲ — ಕೆಳಗಿನ ಪಟ್ಟಿಯಿಂದ ಒಂದನ್ನು ಆರಿಸಿ.",
        "pada": "ಪಾದ",
        "result": "ಫಲಿತಾಂಶ",
        "res.head": "<tr><th></th><th>ಮೊದಲ ಅಕ್ಷರ</th><th>ನಕ್ಷತ್ರ</th><th>ರಾಶಿ</th></tr>",
        "boy": "ವರ",
        "girl": "ವಧು",
        "res.th": "<tr><th>ಕೂಟ</th><th>ಗುಣ</th><th>ವಿವರ</th></tr>",
        "total": "ಒಟ್ಟು ಗುಣ",
        "mangal": ("<strong>ಕುಜ ದೋಷ: ಅನ್ವಯಿಸುವುದಿಲ್ಲ.</strong> ಕುಜ ದೋಷವು ಜನನ ಸಮಯದಲ್ಲಿ ಲಗ್ನ, "
                   "ಚಂದ್ರ ಮತ್ತು ಶುಕ್ರನಿಂದ ಕುಜ ಎಲ್ಲಿದ್ದನು ಎಂಬುದನ್ನು ಅವಲಂಬಿಸಿದೆ — ಹೆಸರಿನಿಂದ ಅದು "
                   "ತಿಳಿಯುವುದಿಲ್ಲ. ಅದಕ್ಕಾಗಿ ಜನ್ಮ ಜಾತಕದ ಹೊಂದಾಣಿಕೆ ಬಳಸಿ."),
        "res.cta": "ಬದಲಿಗೆ ಜನ್ಮ ವಿವರಗಳಿಂದ ಹೊಂದಿಸಿ — ಹೆಚ್ಚು ನಿಖರ, ಉಚಿತ",
        "caveat": ('<div class="box"><p><strong>ಗಮನಿಸಿ:</strong> ಹೆಸರಿನಿಂದ ಹೊಂದಾಣಿಕೆಯು ಜನ್ಮ '
                   "ವಿವರಗಳು ತಿಳಿಯದಿದ್ದಾಗ ಬಳಸುವ ಸಾಂಪ್ರದಾಯಿಕ ಸುಲಭ ವಿಧಾನ. ಪ್ರತಿ ಹೆಸರನ್ನೂ ಆ "
                   "ವ್ಯಕ್ತಿಯ ಜನ್ಮ ನಕ್ಷತ್ರದ ಅಕ್ಷರದಿಂದ ಇಡಲಾಗಿದೆ ಎಂದು ಇದು ಊಹಿಸುತ್ತದೆ — ಇಂದು "
                   "ಅನೇಕ ಬಾರಿ ಹಾಗಿರುವುದಿಲ್ಲ. ಜನ್ಮ ದಿನಾಂಕ, ಸಮಯ ಮತ್ತು ಸ್ಥಳದಿಂದ ಮಾಡುವ ಹೊಂದಾಣಿಕೆ "
                   "ಬಹಳ ಹೆಚ್ಚು ನಿಖರ, ಮತ್ತು ಕುಜ ದೋಷವನ್ನು ಪರಿಶೀಲಿಸಲು ಅದೊಂದೇ ದಾರಿ.</p></div>"),
        "syl.head": "<tr><th>ರಾಶಿ</th><th>ನಾಮಾಕ್ಷರಗಳು</th></tr>",
        "explainer": """
<h2>ಹೆಸರಿನಿಂದ ಜಾತಕ ಹೊಂದಾಣಿಕೆ ಹೇಗೆ ನಡೆಯುತ್ತದೆ</h2>
<p>27 ನಕ್ಷತ್ರಗಳಲ್ಲಿ ಪ್ರತಿಯೊಂದಕ್ಕೂ ನಾಲ್ಕು ಪಾದಗಳಿವೆ, ಪ್ರತಿ ಪಾದಕ್ಕೂ ಒಂದು ಅಕ್ಷರ (ನಾಮಾಕ್ಷರ) —
ಒಟ್ಟು 108. ಹೆಸರು ಯಾವ ಪಾದದ ಅಕ್ಷರದಿಂದ <strong>ಆರಂಭವಾಗುತ್ತದೋ</strong> ಅದನ್ನು ಆ ವ್ಯಕ್ತಿಯ
ನಕ್ಷತ್ರವಾಗಿ, ಅದರ ರಾಶಿಯನ್ನು ಚಂದ್ರ ರಾಶಿಯಾಗಿ ತೆಗೆದುಕೊಳ್ಳಲಾಗುತ್ತದೆ. ನಂತರ ಜನ್ಮ ಜಾತಕಗಳಿಗೆ ಬಳಸುವ
ಅದೇ <strong>ಅಷ್ಟಕೂಟ (36 ಗುಣ)</strong> ಹೊಂದಾಣಿಕೆಯನ್ನು — ವರ್ಣ, ವಶ್ಯ, ತಾರಾ, ಯೋನಿ, ಗ್ರಹ ಮೈತ್ರಿ,
ಗಣ, ಭಕೂಟ ಮತ್ತು ನಾಡಿ — ಈ ಎರಡು ನಕ್ಷತ್ರಗಳಿಂದ ಲೆಕ್ಕಹಾಕಲಾಗುತ್ತದೆ, ನಮ್ಮ ಜಾತಕ ಹೊಂದಾಣಿಕೆ
ಸಾಧನದ ಅದೇ ಎಂಜಿನ್‌ನಿಂದ.</p>
<h3>ಮೊದಲ ಅಕ್ಷರವನ್ನು ಹೇಗೆ ಓದಲಾಗುತ್ತದೆ</h3>
<ul>
<li>ಮೊದಲ ಅಕ್ಷರದ ಮೊದಲ ವ್ಯಂಜನ ಮತ್ತು ಅದರ ಸ್ವರ: <strong>ಪ್ರಿಯಾ → ಪೀ</strong>,
<strong>ಕ್ಷಿತಿಜ್ → ಕೀ</strong>. ಹ್ರಸ್ವ ಮತ್ತು ದೀರ್ಘ ಸ್ವರಗಳನ್ನು ಒಂದೇ ಎಂದು ಎಣಿಸಲಾಗುತ್ತದೆ (ಇ/ಈ, ಉ/ಊ);
ಐ ಅನ್ನು ಏ ಎಂದು, ಔ ಅನ್ನು ಓ ಎಂದು ಎಣಿಸಲಾಗುತ್ತದೆ.</li>
<li>ಬ ಅನ್ನು ವ ಎಂದು, ಶ ಅನ್ನು ಷ (ಅ-ಸ್ವರದೊಂದಿಗೆ) ಅಥವಾ ಸ ಎಂದು ಓದಲಾಗುತ್ತದೆ; ಋ ಅನ್ನು ರೀ ಎಂದು.</li>
<li>ಅಭಿಜಿತ್ ನಕ್ಷತ್ರದ ಅಕ್ಷರಗಳನ್ನು ({abhijit}) ಉತ್ತರಾಷಾಢ 4ನೇ ಪಾದದಲ್ಲಿ ಎಣಿಸಲಾಗುತ್ತದೆ.</li>
<li>ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಬರೆದ ಹೆಸರುಗಳನ್ನು ಲಿಪ್ಯಂತರಿಸಲಾಗುತ್ತದೆ; T, D, N, Th ಮತ್ತು Dh ನಂತಹ ಅಕ್ಷರಗಳು
ಎರಡು ಹಿಂದಿ ಅಕ್ಷರಗಳನ್ನು ಸೂಚಿಸಬಹುದು (ತ/ಟ, ದ/ಡ), ಆದ್ದರಿಂದ ಯಾವ ಅಕ್ಷರವನ್ನು ಬಳಸಲಾಗಿದೆ ಎಂದು ಫಲಿತಾಂಶ
ತೋರಿಸುತ್ತದೆ ಮತ್ತು ಬೇರೆಯದನ್ನು ಆರಿಸಲು ಅವಕಾಶ ನೀಡುತ್ತದೆ. ಹಿಂದಿ (ದೇವನಾಗರಿ) ಹೆಸರನ್ನು ನಿಖರವಾಗಿ
ಓದಲಾಗುತ್ತದೆ.</li>
</ul>
<h3>ರಾಶಿವಾರು ನಾಮಾಕ್ಷರಗಳು</h3>
{syllables}
<p>ಪ್ರತಿ ನಕ್ಷತ್ರದ ಅಕ್ಷರಗಳು, ದೇವತೆ, ಗಣ ಮತ್ತು ನಾಡಿಗಾಗಿ <a href="{href}">ಎಲ್ಲ 27
ನಕ್ಷತ್ರಗಳು</a> ಪುಟ ನೋಡಿ.</p>""",
    },

    "te": {
        "title": "పేరుతో జాతక పొంతన — 36 గుణాల మేళనం, ఉచితం | {brand}",
        "desc": ("పేరుతో జాతక పొంతన: వధూవరుల పేర్ల మొదటి అక్షరం నుండి నక్షత్రం, రాశి, ఆపై "
                 "పూర్తి 36 గుణాల అష్టకూట పొంతన. పేర్లను హిందీ లేదా ఇంగ్లీష్‌లో రాయండి — ఉచితం, "
                 "నమోదు అవసరం లేదు."),
        "crumb": "పేరుతో జాతక పొంతన",
        "h1": "<h1>పేరుతో జాతక పొంతన</h1>",
        "sub": '<p class="hi">పేరు ద్వారా పెళ్లి పొంతన — నామ నక్షత్రం</p>',
        "intro": ("<p>పుట్టిన సమయం తెలియనప్పుడు, సంప్రదాయంలో జంటను <strong>పేర్ల మొదటి "
                  "అక్షరం</strong> ఆధారంగా సరిపోలుస్తారు. ఇద్దరి పేర్లను హిందీ లేదా ఇంగ్లీష్‌లో "
                  "రాయండి: ఉపయోగించిన అక్షరం, దాని నక్షత్ర పాదం, రాశి, పూర్తి 36 గుణాల పొంతనను "
                  "మేము చూపిస్తాము.</p>"),
        "open_milan": "జనన జాతకంతో పొంతన తెరవండి",
        "auto": "పేరు నుండి స్వయంచాలకంగా",
        "alt_head": "ఈ పేరుకు సాధ్యమైన ఇతర అక్షరాలు",
        "all_head": "మొత్తం 108 నామాక్షరాలు",
        "boy_label": "వరుడి పేరు (అబ్బాయి)",
        "girl_label": "వధువు పేరు (అమ్మాయి)",
        "boy_ph": "ఉదా. Ram",
        "girl_ph": "ఉదా. Sita",
        "pick": "మొదటి అక్షరం మార్చండి",
        "button": "గుణాలు సరిచూడండి",
        "via.abhijit": ("ఈ అక్షరం 28వ నక్షత్రమైన అభిజిత్‌కు చెందినది; 27 నక్షత్రాల చక్రంలో దీనిని "
                        "ఉత్తరాషాఢ 4వ పాదంలో లెక్కిస్తారు."),
        "via.alias": "సంప్రదాయ నియమం ప్రకారం బ ను వ గా, శ ను ష (అ-స్వరంతో) లేదా స గా చదువుతారు.",
        "via.nearest": ("ఈ ఖచ్చితమైన అక్షరం 108 అక్షరాల జాబితాలో లేదు, కాబట్టి అదే హల్లుతో ఉన్న "
                        "దగ్గరి అక్షరాన్ని తీసుకున్నాము — కావాలంటే క్రింద మార్చండి."),
        "via.latin": ("ఇంగ్లీష్ స్పెల్లింగ్‌తో ఈ అక్షరం ఖచ్చితంగా తేలదు (ఉదా. T = త లేదా ట), "
                      "కాబట్టి సాధారణ ఉచ్చారణను తీసుకున్నాము — అవసరమైతే క్రింద వేరొకటి ఎంచుకోండి."),
        "via.chosen": "ఈ అక్షరాన్ని మీరే ఎంచుకున్నారు.",
        "unreadable": "ఈ పేరు నుండి మొదటి అక్షరాన్ని గుర్తించలేకపోయాము — క్రింది జాబితా నుండి ఒకటి ఎంచుకోండి.",
        "pada": "పాదం",
        "result": "ఫలితం",
        "res.head": "<tr><th></th><th>మొదటి అక్షరం</th><th>నక్షత్రం</th><th>రాశి</th></tr>",
        "boy": "వరుడు",
        "girl": "వధువు",
        "res.th": "<tr><th>కూటం</th><th>గుణాలు</th><th>వివరణ</th></tr>",
        "total": "మొత్తం గుణాలు",
        "mangal": ("<strong>కుజ దోషం: వర్తించదు.</strong> కుజ దోషం పుట్టిన సమయంలో లగ్నం, "
                   "చంద్రుడు, శుక్రుడి నుండి కుజుడు ఎక్కడ ఉన్నాడనే దానిపై ఆధారపడుతుంది — పేరు "
                   "దానిని చెప్పలేదు. దానికోసం జనన జాతక పొంతన ఉపయోగించండి."),
        "res.cta": "బదులుగా జనన వివరాలతో పొంతన చూడండి — మరింత ఖచ్చితం, ఉచితం",
        "caveat": ('<div class="box"><p><strong>గమనిక:</strong> పేరుతో పొంతన అనేది జనన వివరాలు '
                   "తెలియనప్పుడు ఉపయోగించే సంప్రదాయ సులభ పద్ధతి. ప్రతి పేరూ ఆ వ్యక్తి జన్మ "
                   "నక్షత్రపు అక్షరంతో పెట్టారని ఇది భావిస్తుంది — ఈ రోజుల్లో చాలాసార్లు అలా "
                   "ఉండదు. పుట్టిన తేదీ, సమయం, ఊరు ఆధారంగా చేసే పొంతన చాలా ఎక్కువ ఖచ్చితమైనది, "
                   "కుజ దోషాన్ని చూడడానికి అదొక్కటే మార్గం.</p></div>"),
        "syl.head": "<tr><th>రాశి</th><th>నామాక్షరాలు</th></tr>",
        "explainer": """
<h2>పేరుతో జాతక పొంతన ఎలా చేస్తారు</h2>
<p>27 నక్షత్రాలలో ప్రతిదానికీ నాలుగు పాదాలు ఉన్నాయి, ప్రతి పాదానికీ ఒక అక్షరం (నామాక్షరం) —
మొత్తం 108. పేరు ఏ పాదపు అక్షరంతో <strong>మొదలవుతుందో</strong> దానిని ఆ వ్యక్తి నక్షత్రంగా,
దాని రాశిని చంద్ర రాశిగా తీసుకుంటారు. ఆపై జనన జాతకాలకు వాడే అదే <strong>అష్టకూట (36 గుణాల)</strong>
పొంతన — వర్ణం, వశ్యం, తార, యోని, గ్రహ మైత్రి, గణం, భకూటం, నాడి — ఈ రెండు నక్షత్రాల నుండి
లెక్కించబడుతుంది, మా జాతక పొంతన సాధనం వెనుక ఉన్న అదే ఇంజిన్‌తో.</p>
<h3>మొదటి అక్షరాన్ని ఎలా చదువుతారు</h3>
<ul>
<li>మొదటి అక్షరంలోని మొదటి హల్లు, దాని అచ్చు: <strong>ప్రియా → పీ</strong>,
<strong>క్షితిజ్ → కీ</strong>. హ్రస్వ, దీర్ఘ అచ్చులను ఒకటిగానే లెక్కిస్తారు (ఇ/ఈ, ఉ/ఊ);
ఐ ని ఏ గా, ఔ ని ఓ గా లెక్కిస్తారు.</li>
<li>బ ను వ గా, శ ను ష (అ-స్వరంతో) లేదా స గా చదువుతారు; ఋ ను రీ గా.</li>
<li>అభిజిత్ నక్షత్రపు అక్షరాలను ({abhijit}) ఉత్తరాషాఢ 4వ పాదంలో లెక్కిస్తారు.</li>
<li>ఇంగ్లీష్‌లో రాసిన పేర్లను లిప్యంతరీకరిస్తారు; T, D, N, Th, Dh వంటి అక్షరాలు రెండు హిందీ
అక్షరాలను సూచించవచ్చు (త/ట, ద/డ), కాబట్టి ఏ అక్షరం తీసుకున్నామో ఫలితం చూపిస్తుంది, వేరొకటి
ఎంచుకునే వీలు కూడా ఇస్తుంది. హిందీ (దేవనాగరి) పేరును ఖచ్చితంగా చదువుతారు.</li>
</ul>
<h3>రాశి వారీగా నామాక్షరాలు</h3>
{syllables}
<p>ప్రతి నక్షత్రపు అక్షరాలు, దేవత, గణం, నాడి కోసం <a href="{href}">మొత్తం 27
నక్షత్రాలు</a> పేజీ చూడండి.</p>""",
    },
}


# DIVASTRO-123: the matching engine writes its verdict text in English or Hindi
# only. For other languages the result's score-band note and the convention note
# come from here (the verdict word is seo_text's km.band<i>); the per-koota notes
# stay the engine's English.
ENGINE: dict[str, dict[str, str]] = {
    "kn": {
        "band_note0": "ಸಾಂಪ್ರದಾಯಿಕ ಕನಿಷ್ಠ 18 ಗುಣಗಳಿಗಿಂತ ಕಡಿಮೆ.",
        "band_note1": "ಸಾಂಪ್ರದಾಯಿಕ 18–24 ಗುಣಗಳ ವರ್ಗದಲ್ಲಿ.",
        "band_note2": "ಸಾಂಪ್ರದಾಯಿಕ 25–32 ಗುಣಗಳ ವರ್ಗದಲ್ಲಿ.",
        "band_note3": "ಸಾಂಪ್ರದಾಯಿಕ 33–36 ಗುಣಗಳ ವರ್ಗದಲ್ಲಿ.",
        "convention_note": ("18/25/33 ಗುಣಗಳ ಮಿತಿಗಳು ವ್ಯಾಪಕವಾಗಿ ಬಳಸುವ ಸಂಪ್ರದಾಯ, ಅಳತೆಯಲ್ಲ. ಹೆಚ್ಚು "
                            "ತೂಕದ ಕೂಟಗಳು ದೋಷರಹಿತವಾಗಿದ್ದರೆ ಜ್ಯೋತಿಷಿಗಳು ಕಡಿಮೆ ಒಟ್ಟು ಗುಣಗಳನ್ನೂ "
                            "ಸಾಮಾನ್ಯವಾಗಿ ಒಪ್ಪುತ್ತಾರೆ."),
    },
    "te": {
        "band_note0": "సంప్రదాయ కనీసం 18 గుణాల కంటే తక్కువ.",
        "band_note1": "సంప్రదాయ 18–24 గుణాల శ్రేణిలో.",
        "band_note2": "సంప్రదాయ 25–32 గుణాల శ్రేణిలో.",
        "band_note3": "సంప్రదాయ 33–36 గుణాల శ్రేణిలో.",
        "convention_note": ("18/25/33 గుణాల పరిమితులు విస్తృతంగా పాటించే సంప్రదాయం, కొలత కాదు. "
                            "బరువైన కూటాలు దోషరహితంగా ఉంటే జ్యోతిష్కులు తక్కువ మొత్తాన్ని కూడా "
                            "సాధారణంగా అంగీకరిస్తారు."),
    },
}
