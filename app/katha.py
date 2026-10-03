"""Katha: retold mythological stories, the evening WhatsApp Channel post.

Each story lives twice: a teaser on the channel that stops at the turning
point, and the whole story at /katha/<slug> on the site, so the "read more"
click lands on our own page (and the page itself can rank for "<story> ki
katha" searches).

The stories are retellings of episodes from the Itihasa, the Puranas and the
vrat kathas, in plain Hindi. Each names the text it comes from; nothing is
invented that is not in the source episode. Adding a story is adding an entry
to STORIES; the page, the index, the sitemap and the channel post follow.

    python -m app.katha --slug savitri-satyavan --dry-run   # print the teaser
    python -m app.katha --slug savitri-satyavan             # post it to the channel
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass
from urllib.parse import urlencode

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import daily_state, seo_pages
from .seo_pages import HI, SITE_URL, _e, _render

router = APIRouter()
JOB = "katha"


@dataclass(frozen=True)
class Story:
    slug: str
    title: str                 # Hindi title
    title_en: str              # for the URL-less English mention (meta, logs)
    source: str                # the text the episode comes from
    summary: str               # one line, for the index and meta description
    teaser: tuple[str, ...]    # channel paragraphs, ending on the turning point
    hook: str                  # the question that sends readers to the page
    rest: tuple[str, ...]      # the remainder, on the page after the teaser
    message: str               # what the story teaches
    note: str = ""             # e.g. the vrat it is read on
    links: tuple[tuple[str, str], ...] = ()   # (label, path) for the closing CTA


STORIES: dict[str, Story] = {s.slug: s for s in [
    Story(
        slug="savitri-satyavan",
        title="सावित्री और सत्यवान",
        title_en="Savitri and Satyavan",
        source="महाभारत, वन पर्व (पतिव्रता माहात्म्य पर्व)",
        summary="जिस पत्नी ने धैर्य, बुद्धि और धर्म से यमराज से भी अपने पति के प्राण लौटा लिए।",
        teaser=(
            "मद्र देश के राजा अश्वपति की कोई संतान नहीं थी। अठारह वर्षों तक उन्होंने देवी सावित्री "
            "की उपासना की। देवी प्रसन्न हुईं और उन्हें एक तेजस्वी पुत्री का वरदान मिला। राजा ने उसका "
            "नाम रखा: सावित्री।",
            "सावित्री बड़ी हुई तो उसके तेज के कारण कोई राजकुमार उससे विवाह का प्रस्ताव लेकर आने का "
            "साहस नहीं कर सका। तब पिता ने कहा, “बेटी, तुम स्वयं अपना वर चुनो।”",
            "सावित्री ने वन में रहने वाले सत्यवान को चुना, जो अंधे और राज्य से निकाले गए राजा "
            "द्युमत्सेन के पुत्र थे। जब यह बात देवर्षि नारद ने सुनी, तो वे चिंतित हो उठे: “राजन, "
            "सत्यवान गुणों में अद्वितीय है… पर उसकी आयु में केवल *एक वर्ष* शेष है।”",
            "सबने सावित्री को समझाया। पर सावित्री ने शांत स्वर में कहा, “मैंने एक बार मन से जिसे "
            "चुन लिया, वही मेरा पति है।”",
            "विवाह हुआ। सावित्री ने राजसी वस्त्र उतारकर वल्कल पहने और वन में सास-ससुर की सेवा करने "
            "लगी। दिन गिनती रही… और जब तीन दिन शेष रहे, उसने कठोर व्रत आरंभ किया।",
            "चौथे दिन सत्यवान लकड़ी काटने वन में गए, और सावित्री भी साथ चली। अचानक सत्यवान के सिर "
            "में तीव्र पीड़ा उठी। वे सावित्री की गोद में सिर रखकर लेट गए…",
            "तभी सावित्री ने देखा: लाल वस्त्र पहने, हाथ में पाश लिए, एक तेजस्वी पुरुष सामने खड़ा था। "
            "*“मैं यमराज हूँ।”*",
        ),
        hook="क्या सावित्री अपने पति को मृत्यु के देवता से वापस ला सकी? उसने यमराज से ऐसा क्या "
             "माँगा कि स्वयं यमराज भी हार गए?",
        rest=(
            "यमराज ने सत्यवान के शरीर से अंगूठे के आकार का प्राण-पुरुष निकाला, पाश में बाँधा और "
            "दक्षिण दिशा की ओर चल पड़े। सावित्री भी उनके पीछे-पीछे चलने लगी।",
            "यमराज रुके। “पुत्री, लौट जाओ। तुम्हारे पति का समय पूरा हुआ। जहाँ तक कोई मनुष्य आ सकता "
            "है, तुम आ चुकी हो।”",
            "सावित्री ने विनम्रता से कहा, “जहाँ मेरे पति जाते हैं, वहीं मेरा धर्म मुझे ले जाता है। "
            "सज्जनों के साथ सात कदम चलने से मित्रता हो जाती है। उसी मित्रता के नाते मेरी बात "
            "सुनिए।” और उसने धर्म पर ऐसी सारगर्भित बातें कहीं कि यमराज प्रसन्न हो गए।",
            "*“सत्यवान के प्राणों को छोड़कर कोई भी वर माँग लो।”*",
            "सावित्री ने माँगा: *मेरे ससुर की आँखों की ज्योति लौट आए।* “तथास्तु।”",
            "वह फिर भी पीछे चलती रही। यमराज ने दूसरा वर दिया, और उसने माँगा: *मेरे ससुर को उनका "
            "खोया राज्य वापस मिले।* “तथास्तु।”",
            "तीसरा वर: *मेरे पिता, जिनका कोई पुत्र नहीं, उन्हें सौ पुत्र हों।* “तथास्तु।”",
            "फिर भी सावित्री पीछे-पीछे चलती रही। उसकी धर्मनिष्ठ वाणी से यमराज का हृदय पिघल गया। "
            "“सत्यवान के प्राण छोड़कर एक और वर माँगो।”",
            "सावित्री ने हाथ जोड़कर कहा: *“मुझे सत्यवान से सौ तेजस्वी पुत्र हों।”*",
            "यमराज ने कहा, “तथास्तु”… और फिर ठिठक गए। सत्यवान के बिना सावित्री को सत्यवान से "
            "पुत्र कैसे होते? अपने ही वचन से बंधे यमराज मुस्कुराए, पाश खोला और सत्यवान के प्राण "
            "लौटा दिए। “कल्याणी, तुमने धर्म से मृत्यु को भी जीत लिया।”",
            "सावित्री लौटकर आई। सत्यवान ऐसे जागे मानो गहरी नींद से उठे हों। आश्रम पहुँचे तो "
            "द्युमत्सेन की आँखों में ज्योति लौट आई थी, और कुछ ही समय में उनका राज्य भी उन्हें वापस "
            "मिल गया।",
        ),
        message="सावित्री ने न रोकर माँगा, न लड़कर। उसने *धैर्य, बुद्धि और धर्म* से वह पा लिया जो "
                "असंभव था।",
        note="इसी कथा की स्मृति में सुहागिन स्त्रियाँ ज्येष्ठ अमावस्या (और कुछ परंपराओं में ज्येष्ठ "
             "पूर्णिमा) को *वट सावित्री व्रत* रखती हैं और वट वृक्ष की पूजा कर पति की दीर्घायु की "
             "कामना करती हैं।",
        links=(("कुंडली मिलान (36 गुण)", "/hi/kundali-milan"),
               ("अपनी मुफ़्त कुंडली बनाएं", "/hi/free-kundali")),
    ),
]}


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

_BOLD = re.compile(r"\*(.+?)\*")


def _html(text: str) -> str:
    """Our paragraph markup: *bold*, everything else escaped."""
    return _BOLD.sub(r"<strong>\1</strong>", _e(text))


def page_path(slug: str | None = None) -> str:
    return f"/katha/{slug}" if slug else "/katha"


def sitemap_paths() -> list[str]:
    return [page_path()] + [page_path(s) for s in STORIES]


def is_public_path(path: str) -> bool:
    return path in sitemap_paths()


@router.get("/katha", response_class=HTMLResponse)
def katha_index() -> HTMLResponse:
    items = "".join(
        f'<li><a href="{_e(page_path(s.slug))}"><strong>{_e(s.title)}</strong></a> — '
        f'{_e(s.summary)} <small>({_e(s.source)})</small></li>' for s in STORIES.values())
    body = ("<h1>पौराणिक कथाएँ</h1>"
            "<p>रामायण, महाभारत, पुराणों और व्रत कथाओं की प्रसिद्ध कथाएँ, सरल हिंदी में। हर कथा के "
            "साथ उसका मूल स्रोत दिया गया है।</p>"
            f'<ul class="links katha-list">{items}</ul>')
    return _render(title="पौराणिक कथाएँ | Divine Astro",
                   description="रामायण, महाभारत, पुराण और व्रत कथाएँ सरल हिंदी में, मूल स्रोत सहित।",
                   path=page_path(), crumbs=[("कथाएँ", page_path())], body=body, lang=HI)


@router.get("/katha/{slug}", response_class=HTMLResponse)
def katha_page(slug: str) -> HTMLResponse:
    s = STORIES.get(slug)
    if s is None:
        return _render(title="कथा नहीं मिली | Divine Astro", description="यह कथा उपलब्ध नहीं है।",
                       path=page_path(slug), crumbs=[("कथाएँ", page_path())],
                       body='<h1>कथा नहीं मिली</h1><p><a href="/katha">सभी कथाएँ देखें</a></p>',
                       lang=HI, status=404, cache=False)
    paras = "".join(f"<p>{_html(p)}</p>" for p in (*s.teaser, *s.rest))
    links = "".join(f'<li><a href="{_e(p)}">{_e(label)}</a></li>' for label, p in s.links)
    body = (f"<h1>{_e(s.title)}</h1>"
            f'<p class="date">स्रोत: {_e(s.source)}</p>'
            f"{paras}"
            f"<h2>इस कथा का संदेश</h2><p>{_html(s.message)}</p>"
            + (f"<p>{_html(s.note)}</p>" if s.note else "")
            + (f'<h2>आगे</h2><ul class="links">{links}'
               '<li><a href="/katha">और कथाएँ पढ़ें</a></li></ul>'))
    article = {"@type": "Article", "headline": s.title, "inLanguage": "hi-IN",
               "description": s.summary, "isBasedOn": s.source,
               "url": SITE_URL + page_path(slug),
               "publisher": {"@type": "Organization", "name": seo_pages.BRAND,
                             "url": SITE_URL + "/"}}
    return _render(title=f"{s.title} की कथा | Divine Astro",
                   description=f"{s.title}: {s.summary} स्रोत: {s.source}.",
                   path=page_path(slug),
                   crumbs=[("कथाएँ", page_path()), (s.title, page_path(slug))],
                   body=body, lang=HI, extra_ld=(article,))


# --------------------------------------------------------------------------
# The channel post
# --------------------------------------------------------------------------

def link(slug: str, campaign: str = "katha") -> str:
    q = urlencode({"utm_source": "whatsapp", "utm_medium": "channel", "utm_campaign": campaign})
    return f"{SITE_URL}{page_path(slug)}?{q}"


def teaser(slug: str) -> str:
    """The WhatsApp post: title, the story up to its turning point, the hook,
    the link to the rest, the source. WhatsApp *bold* markup."""
    s = STORIES[slug]
    return "\n\n".join([
        f"*📖 आज की कथा: {s.title}*",
        *s.teaser,
        f"🙏 {s.hook}",
        f"👉 *पूरी कथा पढ़ें:*\n{link(slug)}",
        f"_स्रोत: {s.source}_",
    ])


def main(argv: list[str] | None = None) -> int:
    from . import whatsapp_channel as W           # lazy: only the CLI needs the connector
    import os

    ap = argparse.ArgumentParser(prog="python -m app.katha", description=__doc__.split("\n\n")[0])
    ap.add_argument("--slug", required=True, choices=sorted(STORIES))
    ap.add_argument("--dry-run", action="store_true", help="print the post, send nothing")
    ap.add_argument("--force", action="store_true", help="post even if this story went out already")
    args = ap.parse_args(argv)

    text = teaser(args.slug)
    if args.dry_run:
        print(f"----- katha {args.slug} ({len(text)} chars, WhatsApp *bold*) -----")
        print(text)
        return 0
    if not args.force and daily_state.recall(JOB, args.slug):
        print(f"katha: {args.slug} already posted ({daily_state.recall(JOB, args.slug)}); "
              f"--force to post again")
        return 0
    token, chan = os.environ.get("ASTRO_WA_TOKEN", ""), os.environ.get("ASTRO_WA_CHANNEL_LINK", "")
    if not token or not chan:
        print("katha: ASTRO_WA_TOKEN / ASTRO_WA_CHANNEL_LINK not set", file=sys.stderr)
        return 2
    client = W.Client(os.environ.get("ASTRO_WA_URL", W.DEFAULT_URL), token)
    try:
        W.wait_connected(client, float(os.environ.get("ASTRO_WA_WAIT", "60")))
        jid = W.channel_jid(client, chan)
        msg_id = client.post(jid, text, None, None)
    except (W.Unlinked, W.ConnectorError) as exc:
        print(f"katha: {exc}", file=sys.stderr)
        return 1
    daily_state.remember(JOB, args.slug, {"posted": dt.datetime.now().isoformat(timespec="seconds"),
                                          "id": msg_id})
    print(f"katha: posted {args.slug} (message {msg_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
