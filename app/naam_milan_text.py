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
}
