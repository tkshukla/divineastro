"""Page-by-page text out of a PDF written by Typst, with no PDF library.

The app carries no PDF reader (and must not gain a runtime dependency), but the
sample-report tests (DIVASTRO-151) have to prove that every page shows the
watermark and the footer line. Typst writes plain objects, Flate streams and
Identity-H fonts with a ToUnicode map, which is all this reads. It is not a general
extractor: it is exact for the PDFs pdf_report.py produces.
"""

from __future__ import annotations

import re
import zlib

_OBJ = re.compile(rb"(\d+) 0 obj\r?\n(.*?)\r?\nendobj", re.S)
_ESC = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f",
        b"(": b"(", b")": b")", b"\\": b"\\"}


def _objects(pdf: bytes) -> dict[int, bytes]:
    return {int(m.group(1)): m.group(2) for m in _OBJ.finditer(pdf)}


def _stream(body: bytes) -> bytes:
    m = re.search(rb"stream\r?\n(.*)\r?\nendstream", body, re.S)
    if not m:
        return b""
    raw = m.group(1)
    return zlib.decompress(raw) if b"FlateDecode" in body[:m.start()] else raw


def _cmap(data: bytes) -> dict[int, str]:
    out: dict[int, str] = {}
    for block in re.findall(rb"beginbfchar(.*?)endbfchar", data, re.S):
        for a, b in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
            out[int(a, 16)] = bytes.fromhex(b.decode()).decode("utf-16-be", "replace")
    for block in re.findall(rb"beginbfrange(.*?)endbfrange", data, re.S):
        for a, b, c in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
            lo, hi, start = int(a, 16), int(b, 16), int(c, 16)
            for i in range(lo, hi + 1):
                out[i] = chr(start + i - lo)
    return out


def _literal(buf: bytes, i: int) -> tuple[bytes, int]:
    """The literal string starting at buf[i] == '(' and the index after it."""
    depth, out, i = 1, bytearray(), i + 1
    while depth:
        c = buf[i:i + 1]
        if c == b"\\":
            n = buf[i + 1:i + 2]
            if n.isdigit():
                m = re.match(rb"[0-7]{1,3}", buf[i + 1:i + 4])
                out.append(int(m.group(0), 8) & 0xFF)
                i += 1 + len(m.group(0))
                continue
            out += _ESC.get(n, n)
            i += 2
            continue
        if c == b"(":
            depth += 1
        elif c == b")":
            depth -= 1
            if not depth:
                break
        out += c
        i += 1
    return bytes(out), i + 1


def _page_text(content: bytes, fonts: dict[bytes, dict[int, str]]) -> str:
    parts: list[str] = []
    cur: dict[int, str] = {}
    i, n = 0, len(content)
    token = re.compile(rb"/(\w+)\s+[\d.]+\s+Tf|\(|\]\s*TJ|T\*|\bET\b")
    while i < n:
        m = token.search(content, i)
        if not m:
            break
        if m.group(1) is not None:
            cur = fonts.get(m.group(1), {})
            i = m.end()
        elif m.group(0) == b"(":
            s, i = _literal(content, m.start())
            parts.append("".join(cur.get((s[k] << 8) | s[k + 1], "") for k in range(0, len(s) - 1, 2)))
        else:
            parts.append("\n" if m.group(0) in (b"ET", b"T*") else "")
            i = m.end()
    return "".join(parts)


def pages_text(pdf: bytes) -> list[str]:
    """The text of each page, in page order."""
    objs = _objects(pdf)
    pages_obj = next(b for b in objs.values() if b"/Type/Pages" in b[:40])
    kids = re.search(rb"/Kids\s*\[([^\]]*)\]", pages_obj)
    page_ids = [int(x) for x in re.findall(rb"(\d+) 0 R", kids.group(1))]
    out = []
    for pid in page_ids:
        page = objs[pid]
        res = re.search(rb"/Resources\s+(\d+) 0 R", page)
        res_body = objs[int(res.group(1))] if res else page
        fonts: dict[bytes, dict[int, str]] = {}
        for name, num in re.findall(rb"/(\w+)\s+(\d+) 0 R", re.search(rb"/Font<<(.*?)>>", res_body, re.S).group(1)):
            tu = re.search(rb"/ToUnicode\s+(\d+) 0 R", objs[int(num)])
            fonts[name] = _cmap(_stream(objs[int(tu.group(1))])) if tu else {}
        contents = re.search(rb"/Contents\s+(\d+) 0 R", page)
        out.append(_page_text(_stream(objs[int(contents.group(1))]), fonts))
    return out
