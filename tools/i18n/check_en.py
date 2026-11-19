#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks for the English version: Cyrillic, internal links, anchors, language switcher.

Usage:
    python3 tools/i18n/check_en.py [--stage 1|2|3]
Exit code 1 on any problem.
"""
import argparse
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[2]
EN = ROOT / "en"

STAGE = {
    1: ["index.html", "archi.html", "redev.html", "53.html"],
    2: ["archi-guide.html", "redev-guide.html", "redev-schedule.html"],
    3: [p.name for p in sorted(ROOT.glob("redev-*.html"))],
}

CYR = re.compile(r"[Ѐ-ӿ]")
# Machine values that are allowed to stay in Cyrillic (see glossary, section 8).
ALLOWED_CYR = ("course: 'ИИ в архитектуре'", "course: 'ИИ в редевелопменте'",
               "cert: 'Удостоверение'", "cert: 'Справка'", "course: payload.course",
               'value="Трек А', 'value="Трек Б', 'value="Пока не определился',
               "sel.value = 'Трек А", "sel.value = 'Трек Б")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []      # (tag, attr, value)
        self.switcher = None
        self.hreflangs = {}
        self.canonical = None
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "name" in a:
            self.ids.add(a["name"])
        if tag in ("a", "link", "script", "img", "source", "video", "audio", "iframe"):
            for attr in ("href", "src"):
                if attr in a and a[attr]:
                    self.links.append((tag, attr, a[attr]))
        cls = a.get("class", "")
        if "lang-switch" in cls.split():
            self.switcher = a
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "link":
            rel = (a.get("rel") or "").lower()
            if "alternate" in rel.split() and a.get("hreflang"):
                self.hreflangs[a["hreflang"]] = a.get("href")
            if rel == "canonical":
                self.canonical = a.get("href")


def parse(path):
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    p.close()
    return p


def is_external(v):
    v = v.strip()
    return (not v or v.startswith("#") or v.startswith("//") or
            re.match(r"^(?:https?:|mailto:|tel:|javascript:|data:|webcal:)", v, re.I))


def check_link(src_page, value, problems):
    if is_external(value):
        return
    parts = urlsplit(value)
    path = unquote(parts.path)
    frag = parts.fragment
    if not path:
        target = src_page
    else:
        target = (src_page.parent / path).resolve()
    if not target.exists():
        problems.append(f"{src_page.relative_to(ROOT)}: broken link {value!r} -> {target.relative_to(ROOT)}")
        return
    if target.is_dir():
        idx = target / "index.html"
        if idx.exists():
            target = idx
        else:
            return
    if frag and target.suffix.lower() == ".html":
        try:
            tp = parse(target)
        except Exception as e:
            problems.append(f"{src_page.relative_to(ROOT)}: cannot parse target {target}: {e}")
            return
        # archi.html#enroll is handled by JS (it opens the application modal and has no element id).
        js_anchor = target.name == "archi.html" and frag == "enroll"
        if frag not in tp.ids and not js_anchor:
            problems.append(f"{src_page.relative_to(ROOT)}: missing anchor #{frag} in {target.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, choices=[1, 2, 3])
    args = ap.parse_args()
    problems = []

    pages = [EN / n for n in STAGE[args.stage]] if args.stage else sorted(EN.glob("*.html"))
    pages = [p for p in pages if p.exists()]
    if not pages:
        print("No English pages found for the selected stage.")
        return 1

    for page in pages:
        rel = page.relative_to(ROOT)
        raw = page.read_text(encoding="utf-8")
        for i, line in enumerate(raw.splitlines(), 1):
            if CYR.search(line):
                if any(a in line for a in ALLOWED_CYR):
                    continue
                problems.append(f"{rel}:{i}: Cyrillic: {line.strip()[:160]}")
        try:
            p = parse(page)
        except Exception as e:
            problems.append(f"{rel}: HTML parse error: {e}")
            continue
        if p.lang != "en":
            problems.append(f"{rel}: <html lang> is {p.lang!r}, expected 'en'")
        if not p.canonical:
            problems.append(f"{rel}: no canonical")
        for code in ("ru", "en", "x-default"):
            if code not in p.hreflangs:
                problems.append(f"{rel}: no hreflang={code}")
        for tag, attr, value in p.links:
            check_link(page, value, problems)
        if p.switcher is None:
            problems.append(f"{rel}: no .lang-switch")
        else:
            links = [v for (t, a, v) in p.links if t == "a" and
                     (v.endswith(page.name) or v == f"../{page.name}")]
            if not links:
                problems.append(f"{rel}: switcher has no link to the Russian counterpart")

    # Russian counterparts must point back to the English page.
    for page in pages:
        ru = ROOT / page.name
        if not ru.exists():
            continue
        rp = parse(ru)
        if rp.switcher is None:
            problems.append(f"{page.name}: Russian page has no .lang-switch")
        else:
            values = [v for (t, a, v) in rp.links if t == "a" and "en/" in v]
            if not any(v.endswith("en/" + page.name) or v.endswith("en/" + page.stem) for v in values):
                problems.append(f"{page.name}: Russian switcher does not point to en/{page.name}")

    if problems:
        print(f"FAIL: {len(problems)} problem(s)")
        for p in problems:
            print(" -", p)
        return 1
    print(f"OK: {len(pages)} English page(s), links/anchors/hreflang/switcher/Cyrillic clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
