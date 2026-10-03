"""Naam se Kundali Milan — /naam-se-kundali-milan and /hi/… (DIVASTRO-115).

The traditional shortcut when birth details are unknown: the first syllable
of each name (namakshar) is looked up in the 108-pada table, which gives a
nakshatra pada and so a Moon sign, and the 36-point Ashtakoot is computed from
those two "Moons" by the same engine the birth-chart Kundali Milan uses
(`astro.matching.ashtakoot`), so the two tools can never score the same pair
of nakshatras differently. The syllable rules and their limits are in
astro/namakshar.py and are explained on the page.

Privacy — names are personal data, so:
  * they are never stored, logged or put in a share link. The WhatsApp button
    shares the bare page URL; the form is a plain GET (the page is
    server-rendered and works without JavaScript), so the result response
    is `no-store`, `noindex`, sets `Referrer-Policy: no-referrer` (also as the
    first <meta>, so even the stylesheet request does not carry the URL), and
    loads no third-party script (no AdSense on a result). A one-line inline
    script then drops the query from the address bar, so a copied or shared
    address bar URL carries no names either. The Caddy access log filters
    the `boy`/`girl` parameters out (see Caddyfile).
  * the engine is handed a synthetic chart bundle with an empty name.
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

from .astro import matching
from .astro.namakshar import (ABHIJIT, Match, all_padas, from_pada_id, lookup,
                              match_for_pada, moon_bundle, pada_id, sign_padas)
from .nakshatra_pages import (RASHIS, kundali_cta, milan_path, nak_path, rashi_path, shell)
from .seo_pages import BRAND, _e

router = APIRouter()

MAX_NAME = 60
PARAMS = ("boy", "girl", "boy_pada", "girl_pada")   # the Caddyfile log filter lists these

_STRIP_QUERY = ("<script>try{history.replaceState(null,'',location.pathname)}catch(e){}"
                "</script>")


def _sign_label(index: int, lang: str) -> str:
    r = RASHIS[index]
    return r.name_hi if lang == "hi" else f"{r.name} ({r.english})"


def _nak_label(n, lang: str) -> str:
    return n.name_hi if lang == "hi" else n.name


def resolve(name: str, pada_value: str) -> Match | None:
    """A chosen pada wins (the reader corrected the syllable); otherwise the name."""
    chosen = from_pada_id(pada_value)
    if chosen:
        return match_for_pada(*chosen)
    return lookup(name)


def compute(groom: Match, bride: Match, lang: str = "en") -> dict:
    """Ashtakoot for the two name-derived Moons — the matching engine, unchanged."""
    return matching.ashtakoot(moon_bundle(groom.nakshatra, groom.pada),
                              moon_bundle(bride.nakshatra, bride.pada), lang=lang)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def _options(selected: Match | None, lang: str) -> str:
    """Every one of the 108 syllables, the likely alternatives first."""
    def opt(n, p, sel=False):
        dev, lat = n.syllables[p - 1]
        sign = _sign_label(n.pada_sign(p), lang)
        text = f"{dev} ({lat}) — {_nak_label(n, lang)} {p} · {sign}"
        return (f'<option value="{pada_id(n, p)}"' + (" selected" if sel else "")
                + f">{_e(text)}</option>")

    auto = "नाम से अपने-आप" if lang == "hi" else "Automatic, from the name"
    out = [f'<option value="">{_e(auto)}</option>']
    if selected is not None and selected.alternatives:
        head = "इस नाम के अन्य संभावित अक्षर" if lang == "hi" else "Other likely syllables for this name"
        out.append(f'<optgroup label="{_e(head)}">'
                   + "".join(opt(n, p) for n, p in selected.alternatives) + "</optgroup>")
    head = "सभी 108 नामाक्षर" if lang == "hi" else "All 108 syllables"
    chosen = selected.via == "chosen" if selected else False
    out.append(f'<optgroup label="{_e(head)}">' + "".join(
        opt(n, p, chosen and n == selected.nakshatra and p == selected.pada)
        for n, p in all_padas()) + "</optgroup>")
    return "".join(out)


def _form(lang: str, boy: str = "", girl: str = "", gm: Match | None = None,
          bm: Match | None = None, show_pick: bool = False) -> str:
    hi = lang == "hi"
    lb = "वर (लड़के) का नाम" if hi else "Boy's name (groom)"
    lg = "कन्या (लड़की) का नाम" if hi else "Girl's name (bride)"
    ph_b = "जैसे राम या Ram" if hi else "e.g. Ram or राम"
    ph_g = "जैसे सीता या Sita" if hi else "e.g. Sita or सीता"
    pick = "पहला अक्षर बदलें" if hi else "Change the first syllable"
    btn = "गुण मिलाएँ" if hi else "Match the gunas"
    picks = ""
    if show_pick:
        picks = (f'<label>{_e(pick)} — {_e(lb)}<select name="boy_pada">{_options(gm, lang)}'
                 f'</select></label><label>{_e(pick)} — {_e(lg)}<select name="girl_pada">'
                 f"{_options(bm, lang)}</select></label>")
    return (f'<form class="milan" method="get" action="{milan_path(lang)}" autocomplete="off">'
            f'<label>{_e(lb)}<input name="boy" maxlength="{MAX_NAME}" value="{_e(boy)}" '
            f'placeholder="{_e(ph_b)}"/></label>'
            f'<label>{_e(lg)}<input name="girl" maxlength="{MAX_NAME}" value="{_e(girl)}" '
            f'placeholder="{_e(ph_g)}"/></label>{picks}'
            f'<button type="submit">{_e(btn)}</button></form>')


def _via_note(m: Match, lang: str) -> str:
    hi = lang == "hi"
    notes = {
        "abhijit": ("यह अक्षर अभिजित (28वें) नक्षत्र का है; 27-नक्षत्र पद्धति में इसे उत्तराषाढ़ा "
                    "के चौथे चरण में गिना गया है।",
                    "This syllable belongs to Abhijit, the 28th nakshatra; in the 27-nakshatra "
                    "wheel it is counted in Uttara Ashadha pada 4."),
        "alias": ("परंपरा के अनुसार ब को व, और श को ष (अ-स्वर के साथ) या स माना गया है।",
                  "By the traditional rule, ब is read as व, and श as ष (with the a-vowel) or स."),
        "nearest": ("यह सटीक अक्षर 108 की सूची में नहीं है, इसलिए उसी व्यंजन का निकटतम अक्षर लिया "
                    "गया है — चाहें तो नीचे से बदलें।",
                    "This exact syllable is not in the 108-syllable list, so the nearest syllable "
                    "with the same consonant was used — change it below if you prefer."),
        "latin": ("अंग्रेज़ी वर्तनी से यह अक्षर निश्चित नहीं होता (जैसे T = त या ट), इसलिए सबसे "
                  "सामान्य पढ़त ली गई है — नीचे से दूसरा अक्षर चुन सकते हैं।",
                  "An English spelling cannot settle this syllable (e.g. T = त or ट), so the most "
                  "common reading was used — pick another below if needed."),
        "chosen": ("यह अक्षर आपने स्वयं चुना है।", "You chose this syllable."),
    }
    if m.via in notes:
        return f"<small>{_e(notes[m.via][0 if hi else 1])}</small>"
    return ""


def _person_row(label: str, raw: str, m: Match | None, lang: str) -> str:
    hi = lang == "hi"
    if m is None:
        msg = ("इस नाम का पहला अक्षर पहचाना नहीं जा सका — नीचे की सूची से अक्षर चुनें।" if hi else
               "Could not read a first syllable from this name — pick one from the list below.")
        return f'<tr><th scope="row">{_e(label)}</th><td colspan="3" class="bad">{_e(msg)}</td></tr>'
    n, p = m.nakshatra, m.pada
    used = f'<span class="syl" lang="hi">{_e(m.akshar)}</span>'
    if m.syllable != m.akshar:
        used += f' → <span class="syl" lang="hi">{_e(m.syllable)}</span>'
    return (f'<tr><th scope="row">{_e(label)}</th><td>{used}{_via_note(m, lang)}</td>'
            f'<td><a href="{nak_path(n, lang)}">{_e(_nak_label(n, lang))}</a> '
            f'<small>{"चरण" if hi else "pada"} {p}</small></td>'
            f'<td><a href="{rashi_path(RASHIS[m.sign], lang)}">{_e(_sign_label(m.sign, lang))}'
            "</a></td></tr>")


def _result(boy: str, girl: str, gm: Match | None, bm: Match | None, lang: str) -> str:
    hi = lang == "hi"
    head = ("<tr><th></th><th>पहला अक्षर</th><th>नक्षत्र</th><th>राशि</th></tr>" if hi else
            "<tr><th></th><th>First syllable</th><th>Nakshatra</th><th>Rashi</th></tr>")
    people = (_person_row("वर" if hi else "Boy", boy, gm, lang)
              + _person_row("कन्या" if hi else "Girl", girl, bm, lang))
    out = [f"<h2>{'परिणाम' if hi else 'Result'}</h2>",
           f'<div class="scroll"><table>{head}{people}</table></div>']
    if gm and bm:
        res = compute(gm, bm, lang)
        rows = "".join(
            f'<tr><td><strong>{_e(k["label"])}</strong></td><td>{k["score"]:g} / {k["max"]:g}</td>'
            f'<td>{_e(k["note"])}</td></tr>' for k in res["kootas"])
        th = ("<tr><th>कूट</th><th>गुण</th><th>विवरण</th></tr>" if hi else
              "<tr><th>Koota</th><th>Points</th><th>Why</th></tr>")
        total = f"{res['total']:g} / {res['maximum']:g}"
        out.append(f'<div class="box"><p class="total"><strong>{"कुल गुण" if hi else "Total"}: '
                   f'{_e(total)}</strong> — {_e(res["verdict"])}</p><p>{_e(res["band_note"])}</p>'
                   f"</div>")
        out.append(f'<div class="scroll"><table>{th}{rows}</table></div>')
        out.append(f'<p class="note">{_e(res["convention_note"])}</p>')
        mangal = ("<strong>मांगलिक दोष: लागू नहीं।</strong> मांगलिक दोष जन्म के समय मंगल की लग्न, "
                  "चंद्र और शुक्र से स्थिति पर निर्भर है — नाम से इसका पता नहीं चल सकता। इसके लिए "
                  "जन्म कुंडली से मिलान करें।" if hi else
                  "<strong>Mangal dosha: not applicable.</strong> Mangal dosha depends on where "
                  "Mars stood from the Lagna, Moon and Venus at birth — a name cannot tell you "
                  "that. Use birth-chart matching for it.")
        out.append(f'<div class="box"><p>{mangal}</p></div>')
    out.append(_caveat(lang))
    out.append(f'<a class="cta" href="{"/?open=milan&amp;lang=hi" if hi else "/?open=milan"}">'
               + _e("जन्म विवरण से सटीक कुंडली मिलान करें — मुफ़्त" if hi
                    else "Match by birth details instead — more accurate, free") + "</a>")
    return "".join(out)


def _caveat(lang: str) -> str:
    if lang == "hi":
        return ('<div class="box"><p><strong>ध्यान दें:</strong> नाम से मिलान एक पारंपरिक '
                "शॉर्टकट है, जो तब प्रयोग होता है जब जन्म समय ज्ञात न हो। यह मानकर चलता है कि नाम "
                "जन्म नक्षत्र के अक्षर से रखा गया था — जो आज अक्सर सच नहीं होता। जन्म तिथि, समय और "
                "स्थान से किया गया कुंडली मिलान कहीं अधिक सटीक है, और मांगलिक दोष भी उसी से देखा "
                "जा सकता है।</p></div>")
    return ('<div class="box"><p><strong>Please note:</strong> name-based matching is a '
            "traditional shortcut, used when birth details are not known. It assumes each name "
            "was chosen from the syllable of the person's birth nakshatra — which today is often "
            "not the case. Matching from the date, time and place of birth is far more accurate, "
            "and is the only way to check Mangal dosha.</p></div>")


def _rashi_syllables(lang: str) -> str:
    hi = lang == "hi"
    head = ("<tr><th>राशि</th><th>नामाक्षर</th></tr>" if hi else
            "<tr><th>Rashi</th><th>Name syllables</th></tr>")
    rows = "".join(
        f'<tr><td><a href="{rashi_path(r, lang)}">{_e(r.name_hi if hi else f"{r.name} · {r.english}")}'
        f'</a></td><td lang="hi">{_e(" ".join(n.syllables[p - 1][0] for n, p in sign_padas(r.index)))}'
        "</td></tr>" for r in RASHIS)
    return f'<div class="scroll"><table>{head}{rows}</table></div>'


def _explainer(lang: str) -> str:
    abhijit = " ".join(d for d, _ in ABHIJIT)
    if lang == "hi":
        return f"""
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
{_rashi_syllables(lang)}
<p>हर नक्षत्र के अक्षर, देवता, गण और नाड़ी के लिए <a href="/hi/nakshatra">27 नक्षत्रों की सूची</a>
देखें।</p>"""
    return f"""
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
{_rashi_syllables(lang)}
<p>For each nakshatra's syllables, deity, gana and nadi see <a href="/nakshatra">all 27
nakshatras</a>.</p>"""


def render(lang: str, boy: str | None, girl: str | None, boy_pada: str | None,
           girl_pada: str | None) -> HTMLResponse:
    hi = lang == "hi"
    boy = (boy or "").strip()[:MAX_NAME]
    girl = (girl or "").strip()[:MAX_NAME]
    asked = any(x for x in (boy, girl, boy_pada, girl_pada))
    if hi:
        title = f"नाम से कुंडली मिलान — नाम के पहले अक्षर से 36 गुण मिलान, मुफ़्त | {BRAND}"
        description = ("नाम से कुंडली मिलान: वर और कन्या के नाम के पहले अक्षर से नक्षत्र और राशि "
                       "निकालकर अष्टकूट 36 गुण मिलान। हिंदी या अंग्रेज़ी में नाम लिखें — मुफ़्त, "
                       "बिना साइन-अप।")
        h1, sub = "नाम से कुंडली मिलान", "Naam se Kundali Milan — match by name"
        intro = ("<p>जन्म समय पता न हो तो परंपरा में <strong>नाम के पहले अक्षर</strong> से गुण "
                 "मिलाए जाते हैं। दोनों के नाम हिंदी या अंग्रेज़ी में लिखें — हम पहला अक्षर, उसका "
                 "नक्षत्र-चरण और राशि दिखाएँगे और पूरे 36 गुणों का मिलान करेंगे।</p>")
    else:
        title = f"Naam se Kundali Milan — Match 36 Gunas by Name, Free | {BRAND}"
        description = ("Kundali milan by name: the first syllable of the boy's and girl's names "
                       "gives each nakshatra and rashi, then the full 36-guna Ashtakoot match. "
                       "Type names in Hindi or English — free, no sign-up.")
        h1, sub = "Naam se Kundali Milan — Match by Name", "नाम से कुंडली मिलान"
        intro = ("<p>When birth times are not known, tradition matches a couple by the "
                 "<strong>first syllable of their names</strong>. Type both names in Hindi or "
                 "English: we show the syllable used, its nakshatra pada and rashi, and the full "
                 "36-guna match.</p>")
    gm = bm = None
    result = ""
    if asked:
        gm, bm = resolve(boy, boy_pada or ""), resolve(girl, girl_pada or "")
        result = _result(boy, girl, gm, bm, lang)
    body = f"""
<h1>{_e(h1)}</h1>
<p class="hi" lang="{'en' if hi else 'hi'}">{_e(sub)}</p>
{intro}
{_form(lang, boy, girl, gm, bm, show_pick=asked)}
{result}
{'' if asked else _caveat(lang)}
{_explainer(lang)}
<a class="cta" href="{'/?open=milan&amp;lang=hi' if hi else '/?open=milan'}">{_e(
        'जन्म विवरण से कुंडली मिलान खोलें' if hi else 'Open birth-chart Kundali Milan')}</a>
{kundali_cta(lang)}"""
    crumbs = [("नाम से कुंडली मिलान" if hi else "Naam se Kundali Milan", milan_path(lang))]
    kw = {}
    if asked:
        kw = dict(cache=False, ads=False,
                  head_first='<meta name="referrer" content="no-referrer"/>\n'
                             '<meta name="robots" content="noindex"/>\n' + _STRIP_QUERY + "\n",
                  headers={"Referrer-Policy": "no-referrer", "X-Robots-Tag": "noindex"})
    return shell(lang=lang, en_path=milan_path("en"), hi_path=milan_path("hi"), title=title,
                 description=description, crumbs=crumbs, body=body, **kw)


# No max_length on the parameters: a 422 would echo the name back in its JSON
# body. render() truncates instead.
@router.get("/naam-se-kundali-milan", response_class=HTMLResponse)
def naam_milan(boy: str | None = Query(None),
               girl: str | None = Query(None),
               boy_pada: str | None = Query(None),
               girl_pada: str | None = Query(None)) -> HTMLResponse:
    return render("en", boy, girl, boy_pada, girl_pada)


@router.get("/hi/naam-se-kundali-milan", response_class=HTMLResponse)
def naam_milan_hi(boy: str | None = Query(None),
                  girl: str | None = Query(None),
                  boy_pada: str | None = Query(None),
                  girl_pada: str | None = Query(None)) -> HTMLResponse:
    return render("hi", boy, girl, boy_pada, girl_pada)
