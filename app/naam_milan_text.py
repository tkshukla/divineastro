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

    # Tamil (DIVASTRO-123). The 108 namakshar syllables come from the engine in
    # Devanagari, and names are read from English letters or Devanagari only.
    "ta": {
        "title": "பெயர் பொருத்தம் — பெயர் மூலம் 36 குணப் பொருத்தம், இலவசம் | {brand}",
        "desc": ("பெயர் மூலம் திருமணப் பொருத்தம்: மணமகன், மணமகள் பெயர்களின் முதல் எழுத்திலிருந்து "
                 "நட்சத்திரமும் ராசியும் கண்டு, முழு 36 குண அஷ்டகூடப் பொருத்தம். பெயர்களை ஆங்கில "
                 "எழுத்துகளில் தட்டச்சு செய்யுங்கள் — இலவசம், பதிவு தேவையில்லை."),
        "crumb": "பெயர் பொருத்தம்",
        "h1": "<h1>பெயர் பொருத்தம் — பெயர் மூலம் ஜாதகப் பொருத்தம்</h1>",
        "sub": '<p class="hi">நாம நட்சத்திரப் பொருத்தம் (நாமாக்ஷரம்)</p>',
        "intro": ("<p>பிறந்த நேரம் தெரியாதபோது, பாரம்பரியமாக இருவரின் <strong>பெயரின் முதல் "
                  "எழுத்தை</strong> வைத்துப் பொருத்தம் பார்க்கப்படுகிறது. இருவரின் பெயர்களையும் ஆங்கில "
                  "எழுத்துகளில் (அல்லது தேவநாகரியில்) தட்டச்சு செய்யுங்கள்: பயன்படுத்திய எழுத்து, அதன் "
                  "நட்சத்திரப் பாதம், ராசி, முழு 36 குணப் பொருத்தம் ஆகியவற்றைக் காட்டுவோம்.</p>"),
        "open_milan": "பிறப்பு விவரங்களுடன் ஜாதகப் பொருத்தம் திறக்கவும்",
        "auto": "பெயரிலிருந்து தானாக",
        "alt_head": "இந்தப் பெயருக்குப் பொருந்தக்கூடிய மற்ற எழுத்துகள்",
        "all_head": "108 நாம எழுத்துகளும்",
        "boy_label": "மணமகன் பெயர்",
        "girl_label": "மணமகள் பெயர்",
        "boy_ph": "ஆங்கில எழுத்துகளில், எ.கா. Ram",
        "girl_ph": "ஆங்கில எழுத்துகளில், எ.கா. Sita",
        "pick": "முதல் எழுத்தை மாற்றவும்",
        "button": "பொருத்தம் பார்க்கவும்",
        "via.abhijit": ("இந்த எழுத்து 28வது நட்சத்திரமான அபிஜித்துக்கு உரியது; 27 நட்சத்திர "
                        "முறையில் இது உத்திராடம் 4ஆம் பாதத்தில் கணக்கிடப்படுகிறது."),
        "via.alias": ("பாரம்பரிய விதிப்படி ‘ப’ (b) ஒலி ‘வ’ ஆகவும், ‘ஶ’ ஒலி ‘ஷ’ (அ உயிருடன்) "
                      "அல்லது ‘ஸ’ ஆகவும் படிக்கப்படுகிறது."),
        "via.nearest": ("இந்த எழுத்து 108 எழுத்துப் பட்டியலில் இல்லை, எனவே அதே மெய்யெழுத்துடைய "
                        "மிக நெருக்கமான எழுத்து எடுக்கப்பட்டது — விரும்பினால் கீழே மாற்றலாம்."),
        "via.latin": ("ஆங்கில எழுத்துக்கூட்டலால் இந்த எழுத்தை உறுதியாகச் சொல்ல முடியாது (எ.கா. T = ‘த’ "
                      "அல்லது ‘ட’), எனவே பொதுவான உச்சரிப்பு எடுக்கப்பட்டது — தேவைப்பட்டால் கீழே வேறு "
                      "எழுத்தைத் தேர்ந்தெடுக்கவும்."),
        "via.chosen": "இந்த எழுத்தை நீங்களே தேர்ந்தெடுத்தீர்கள்.",
        "unreadable": ("இந்தப் பெயரிலிருந்து முதல் எழுத்தைக் கண்டறிய முடியவில்லை — பெயரை ஆங்கில "
                       "எழுத்துகளில் தட்டச்சு செய்யுங்கள், அல்லது கீழே உள்ள பட்டியலில் இருந்து ஒன்றைத் "
                       "தேர்ந்தெடுக்கவும்."),
        "pada": "பாதம்",
        "result": "முடிவு",
        "res.head": "<tr><th></th><th>முதல் எழுத்து</th><th>நட்சத்திரம்</th><th>ராசி</th></tr>",
        "boy": "மணமகன்",
        "girl": "மணமகள்",
        "res.th": "<tr><th>பொருத்தம்</th><th>புள்ளிகள்</th><th>காரணம்</th></tr>",
        "total": "மொத்தம்",
        "mangal": ("<strong>செவ்வாய் தோஷம்: பொருந்தாது.</strong> செவ்வாய் தோஷம் பிறந்தபோது "
                   "லக்னம், சந்திரன், சுக்கிரனிலிருந்து செவ்வாய் எங்கே இருந்தது என்பதைப் பொறுத்தது — "
                   "பெயரால் அதைச் சொல்ல முடியாது. அதற்குப் பிறப்பு ஜாதகப் பொருத்தத்தைப் பயன்படுத்துங்கள்."),
        "res.cta": "பிறப்பு விவரங்களுடன் பொருத்தம் பாருங்கள் — மேலும் துல்லியம், இலவசம்",
        "caveat": ('<div class="box"><p><strong>கவனிக்கவும்:</strong> பெயர் மூலம் பொருத்தம் '
                   "என்பது பிறப்பு விவரங்கள் தெரியாதபோது பயன்படும் ஒரு பாரம்பரியக் குறுக்குவழி. "
                   "ஒவ்வொருவரின் பெயரும் அவரது ஜன்ம நட்சத்திர எழுத்தில் வைக்கப்பட்டது என்று இது "
                   "எடுத்துக்கொள்கிறது — இன்று பெரும்பாலும் அப்படி இருப்பதில்லை. பிறந்த தேதி, நேரம், "
                   "இடம் கொண்டு பார்க்கும் பொருத்தம் மிகவும் துல்லியமானது; செவ்வாய் தோஷத்தையும் "
                   "அதன் மூலமே பார்க்க முடியும்.</p></div>"),
        "syl.head": "<tr><th>ராசி</th><th>நாம எழுத்துகள்</th></tr>",
        "explainer": """
<h2>பெயர் மூலம் பொருத்தம் எப்படிப் பார்க்கப்படுகிறது</h2>
<p>27 நட்சத்திரங்களில் ஒவ்வொன்றுக்கும் நான்கு பாதங்கள், ஒவ்வொரு பாதத்துக்கும் ஒரு எழுத்து
(நாமாக்ஷரம்) — மொத்தம் 108. பெயர் <strong>எந்த எழுத்தில் தொடங்குகிறதோ</strong> அந்தப் பாதத்தின்
நட்சத்திரமே அவரது நட்சத்திரமாகவும், அதன் ராசியே அவரது சந்திர ராசியாகவும் கொள்ளப்படுகிறது. பிறகு
ஜாதகப் பொருத்தத்தில் பயன்படும் அதே <strong>அஷ்டகூட (36 குண)</strong> பொருத்தம் — வர்ணம், வசியம்,
தினம் (தாரா), யோனி, ராசி அதிபதி (கிரக மைத்ரி), கணம், ராசி (பகூட்), நாடி — இந்த இரு
நட்சத்திரங்களிலிருந்து, எங்கள் ஜாதகப் பொருத்தக் கருவியின் அதே கணிப்பு முறையால் கணக்கிடப்படுகிறது.</p>
<h3>முதல் எழுத்து எப்படிப் படிக்கப்படுகிறது</h3>
<ul>
<li>முதல் எழுத்தின் முதல் மெய்யும் அதன் உயிரும்: <strong>பிரியா → பீ</strong>,
<strong>க்ஷிதிஜ் → கீ</strong>. குறில், நெடில் இரண்டும் ஒன்றாகவே கொள்ளப்படும் (இ/ஈ, உ/ஊ);
ஐ என்பது ஏ ஆகவும், ஔ என்பது ஓ ஆகவும் கொள்ளப்படும்.</li>
<li>‘ப’ (b) ஒலி ‘வ’ ஆகவும், ‘ஶ’ ஒலி ‘ஷ’ (அ உயிருடன்) அல்லது ‘ஸ’ ஆகவும், ‘ரு’ (ṛ) ஒலி ‘ரீ’
ஆகவும் படிக்கப்படும்.</li>
<li>அபிஜித் நட்சத்திர எழுத்துகள் ({abhijit}) உத்திராடம் 4ஆம் பாதத்தில் கணக்கிடப்படும்.</li>
<li>பெயர்களை ஆங்கில எழுத்துகளில் தட்டச்சு செய்யுங்கள்; அவை ஒலிபெயர்க்கப்படும். T, D, N, Th, Dh
போன்ற எழுத்துகள் இரண்டு ஒலிகளைக் குறிக்கலாம் (எ.கா. ‘த’/‘ட’), எனவே எந்த எழுத்து
எடுக்கப்பட்டது என்பதை முடிவு காட்டும்; நீங்கள் வேறு ஒன்றைத் தேர்ந்தெடுக்கலாம். பாரம்பரிய
108 நாம எழுத்துப் பட்டியல் தேவநாகரி எழுத்தில் உள்ளது; தேவநாகரியில் தட்டச்சு செய்தால் அப்படியே
படிக்கப்படும்.</li>
</ul>
<h3>ராசி வாரியாக நாம எழுத்துகள்</h3>
{syllables}
<p>ஒவ்வொரு நட்சத்திரத்தின் எழுத்துகள், தெய்வம், கணம், நாடி ஆகியவற்றுக்கு
<a href="{href}">27 நட்சத்திரங்களையும்</a> பாருங்கள்.</p>""",
    },

    # Malayalam (DIVASTRO-123). Same engine limits as Tamil above.
    "ml": {
        "title": "പേരുപൊരുത്തം — പേരിലൂടെ 36 ഗുണ പൊരുത്തം, സൗജന്യം | {brand}",
        "desc": ("പേരിലൂടെ വിവാഹപ്പൊരുത്തം: വരന്റെയും വധുവിന്റെയും പേരിന്റെ ആദ്യാക്ഷരത്തിൽ നിന്ന് "
                 "നക്ഷത്രവും രാശിയും കണ്ടെത്തി, പൂർണ്ണ 36 ഗുണ അഷ്ടകൂട പൊരുത്തം. പേരുകൾ "
                 "ഇംഗ്ലീഷ് അക്ഷരങ്ങളിൽ ടൈപ്പ് ചെയ്യുക — സൗജന്യം, സൈൻ-അപ്പ് വേണ്ട."),
        "crumb": "പേരുപൊരുത്തം",
        "h1": "<h1>പേരുപൊരുത്തം — പേരിലൂടെ ജാതകപ്പൊരുത്തം</h1>",
        "sub": '<p class="hi">നാമാക്ഷര നക്ഷത്രപ്പൊരുത്തം</p>',
        "intro": ("<p>ജനനസമയം അറിയില്ലെങ്കിൽ, പാരമ്പര്യമനുസരിച്ച് ഇരുവരുടെയും <strong>പേരിന്റെ "
                  "ആദ്യാക്ഷരം</strong> നോക്കി പൊരുത്തം കണക്കാക്കുന്നു. രണ്ടു പേരുകളും ഇംഗ്ലീഷ് "
                  "അക്ഷരങ്ങളിൽ (അല്ലെങ്കിൽ ദേവനാഗരിയിൽ) ടൈപ്പ് ചെയ്യുക: ഉപയോഗിച്ച അക്ഷരം, അതിന്റെ "
                  "നക്ഷത്രപാദം, രാശി, പൂർണ്ണ 36 ഗുണ പൊരുത്തം എന്നിവ ഞങ്ങൾ കാണിക്കും.</p>"),
        "open_milan": "ജനനവിവരങ്ങൾ വെച്ചുള്ള ജാതകപ്പൊരുത്തം തുറക്കുക",
        "auto": "പേരിൽ നിന്ന് സ്വയമേവ",
        "alt_head": "ഈ പേരിന് സാധ്യതയുള്ള മറ്റ് അക്ഷരങ്ങൾ",
        "all_head": "108 നാമാക്ഷരങ്ങളും",
        "boy_label": "വരന്റെ പേര്",
        "girl_label": "വധുവിന്റെ പേര്",
        "boy_ph": "ഇംഗ്ലീഷ് അക്ഷരങ്ങളിൽ, ഉദാ. Ram",
        "girl_ph": "ഇംഗ്ലീഷ് അക്ഷരങ്ങളിൽ, ഉദാ. Sita",
        "pick": "ആദ്യാക്ഷരം മാറ്റുക",
        "button": "പൊരുത്തം നോക്കുക",
        "via.abhijit": ("ഈ അക്ഷരം 28-ാമത്തെ നക്ഷത്രമായ അഭിജിത്തിന്റേതാണ്; 27 നക്ഷത്ര "
                        "സമ്പ്രദായത്തിൽ ഇത് ഉത്രാടം 4-ാം പാദത്തിൽ കണക്കാക്കുന്നു."),
        "via.alias": "പരമ്പരാഗത നിയമപ്രകാരം ബ-യെ വ ആയും, ശ-യെ ഷ (അ-സ്വരത്തോടെ) അല്ലെങ്കിൽ സ ആയും വായിക്കുന്നു.",
        "via.nearest": ("ഈ അക്ഷരം 108 അക്ഷരങ്ങളുടെ പട്ടികയിൽ ഇല്ല, അതിനാൽ അതേ വ്യഞ്ജനമുള്ള ഏറ്റവും "
                        "അടുത്ത അക്ഷരം എടുത്തു — വേണമെങ്കിൽ താഴെ മാറ്റാം."),
        "via.latin": ("ഇംഗ്ലീഷ് സ്പെല്ലിങ്ങിൽ നിന്ന് ഈ അക്ഷരം ഉറപ്പിക്കാനാവില്ല (ഉദാ. T = ത അല്ലെങ്കിൽ ട), "
                      "അതിനാൽ ഏറ്റവും സാധാരണമായ ഉച്ചാരണം എടുത്തു — ആവശ്യമെങ്കിൽ താഴെ മറ്റൊന്ന് "
                      "തിരഞ്ഞെടുക്കുക."),
        "via.chosen": "ഈ അക്ഷരം നിങ്ങൾ തിരഞ്ഞെടുത്തതാണ്.",
        "unreadable": ("ഈ പേരിൽ നിന്ന് ആദ്യാക്ഷരം തിരിച്ചറിയാനായില്ല — പേര് ഇംഗ്ലീഷ് അക്ഷരങ്ങളിൽ "
                       "ടൈപ്പ് ചെയ്യുക, അല്ലെങ്കിൽ താഴെയുള്ള പട്ടികയിൽ നിന്ന് ഒന്ന് തിരഞ്ഞെടുക്കുക."),
        "pada": "പാദം",
        "result": "ഫലം",
        "res.head": "<tr><th></th><th>ആദ്യാക്ഷരം</th><th>നക്ഷത്രം</th><th>രാശി</th></tr>",
        "boy": "വരൻ",
        "girl": "വധു",
        "res.th": "<tr><th>പൊരുത്തം</th><th>പോയിന്റ്</th><th>കാരണം</th></tr>",
        "total": "ആകെ",
        "mangal": ("<strong>ചൊവ്വാദോഷം: ബാധകമല്ല.</strong> ജനനസമയത്ത് ലഗ്നം, ചന്ദ്രൻ, ശുക്രൻ "
                   "എന്നിവയിൽ നിന്ന് ചൊവ്വ എവിടെ നിന്നു എന്നതിനെ ആശ്രയിച്ചാണ് ചൊവ്വാദോഷം — പേരിൽ "
                   "നിന്ന് അത് അറിയാനാവില്ല. അതിന് ജനന ജാതകം വെച്ചുള്ള പൊരുത്തം ഉപയോഗിക്കുക."),
        "res.cta": "ജനനവിവരങ്ങൾ വെച്ച് പൊരുത്തം നോക്കൂ — കൂടുതൽ കൃത്യം, സൗജന്യം",
        "caveat": ('<div class="box"><p><strong>ശ്രദ്ധിക്കുക:</strong> പേരിലൂടെയുള്ള പൊരുത്തം, '
                   "ജനനവിവരങ്ങൾ അറിയാത്തപ്പോൾ ഉപയോഗിക്കുന്ന ഒരു പരമ്പരാഗത എളുപ്പവഴിയാണ്. ഓരോരുത്തരുടെയും "
                   "പേര് ജന്മനക്ഷത്രത്തിന്റെ അക്ഷരത്തിൽ ഇട്ടതാണെന്ന് ഇത് അനുമാനിക്കുന്നു — ഇന്ന് "
                   "പലപ്പോഴും അങ്ങനെയല്ല. ജനനത്തീയതി, സമയം, സ്ഥലം എന്നിവ വെച്ചുള്ള പൊരുത്തം വളരെ "
                   "കൂടുതൽ കൃത്യമാണ്; ചൊവ്വാദോഷം നോക്കാനുള്ള ഏക മാർഗവും അതാണ്.</p></div>"),
        "syl.head": "<tr><th>രാശി</th><th>നാമാക്ഷരങ്ങൾ</th></tr>",
        "explainer": """
<h2>പേരിലൂടെയുള്ള പൊരുത്തം എങ്ങനെ</h2>
<p>27 നക്ഷത്രങ്ങൾക്കും നാലു പാദങ്ങൾ വീതം, ഓരോ പാദത്തിനും ഒരു അക്ഷരം (നാമാക്ഷരം) — ആകെ 108.
പേര് <strong>ഏത് അക്ഷരത്തിൽ തുടങ്ങുന്നുവോ</strong> ആ പാദത്തിന്റെ നക്ഷത്രം ആ വ്യക്തിയുടെ നക്ഷത്രമായും,
അതിന്റെ രാശി ചന്ദ്രരാശിയായും എടുക്കുന്നു. തുടർന്ന് ജാതകപ്പൊരുത്തത്തിലെ അതേ <strong>അഷ്ടകൂട (36 ഗുണ)</strong>
പൊരുത്തം — വർണം, വശ്യം, ദിനം (താരാ), യോനി, രാശ്യാധിപ (ഗ്രഹമൈത്രി), ഗണം, രാശി (ഭകൂടം), നാഡി —
ഈ രണ്ടു നക്ഷത്രങ്ങളിൽ നിന്ന്, ഞങ്ങളുടെ ജാതകപ്പൊരുത്തം ടൂളിന്റെ അതേ ഗണനരീതിയിൽ കണക്കാക്കുന്നു.</p>
<h3>ആദ്യാക്ഷരം എങ്ങനെ വായിക്കുന്നു</h3>
<ul>
<li>ആദ്യ അക്ഷരത്തിന്റെ ആദ്യ വ്യഞ്ജനവും അതിന്റെ സ്വരവും: <strong>പ്രിയ → പീ</strong>,
<strong>ക്ഷിതിജ് → കീ</strong>. ഹ്രസ്വ-ദീർഘ സ്വരങ്ങൾ ഒന്നായി കണക്കാക്കും (ഇ/ഈ, ഉ/ഊ);
ഐ-യെ ഏ ആയും ഔ-യെ ഓ ആയും കണക്കാക്കും.</li>
<li>ബ-യെ വ ആയും, ശ-യെ ഷ (അ-സ്വരത്തോടെ) അല്ലെങ്കിൽ സ ആയും, ഋ-യെ രീ ആയും വായിക്കുന്നു.</li>
<li>അഭിജിത് നക്ഷത്രത്തിന്റെ അക്ഷരങ്ങൾ ({abhijit}) ഉത്രാടം 4-ാം പാദത്തിൽ കണക്കാക്കുന്നു.</li>
<li>പേരുകൾ ഇംഗ്ലീഷ് അക്ഷരങ്ങളിൽ ടൈപ്പ് ചെയ്യുക; അവ ലിപ്യന്തരണം ചെയ്യപ്പെടും. T, D, N, Th, Dh
പോലുള്ള അക്ഷരങ്ങൾക്ക് രണ്ട് ഉച്ചാരണം വരാം (ത/ട, ദ/ഡ), അതിനാൽ ഏത് അക്ഷരം എടുത്തുവെന്ന് ഫലം
കാണിക്കും; നിങ്ങൾക്ക് മറ്റൊന്ന് തിരഞ്ഞെടുക്കാം. പരമ്പരാഗത 108 നാമാക്ഷരങ്ങളുടെ പട്ടിക
ദേവനാഗരി ലിപിയിലാണ്; ദേവനാഗരിയിൽ ടൈപ്പ് ചെയ്താൽ അതേപടി വായിക്കും.</li>
</ul>
<h3>രാശി തിരിച്ചുള്ള നാമാക്ഷരങ്ങൾ</h3>
{syllables}
<p>ഓരോ നക്ഷത്രത്തിന്റെയും അക്ഷരങ്ങൾ, ദേവത, ഗണം, നാഡി എന്നിവയ്ക്ക് <a href="{href}">27
നക്ഷത്രങ്ങളും</a> കാണുക.</p>""",
    },
}
