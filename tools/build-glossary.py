#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает общий словарь курса из docs/glossary.md и «Словарей» канонов лекций.

Результат:
  docs/glossary.json       — консолидированный список терминов (источник для лонгридов);
  redev-glossary.html      — страница словаря с поиском и якорями.
Лонгриды ссылаются на термины через redev-glossary.html#<id>.
Термины из канонов, которых нет в docs/glossary.md, добавляются в раздел «Из лекций».
"""
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / 'docs' / 'glossary.md'
LECTURES = ROOT / 'docs' / 'lectures'
OUT_JSON = ROOT / 'docs' / 'glossary.json'
OUT_HTML = ROOT / 'redev-glossary.html'
EXTRA = 'Из лекций'
BULLET = re.compile(r'^\s*[*-]\s+\*\*(.+?)\*\*\s+[—-]\s+(.+)$')


def term_id(name):
    return 't-' + hashlib.md5(name.lower().encode('utf-8')).hexdigest()[:8]


def read_master():
    items, section = [], None
    for line in MASTER.read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            section = line[3:].strip()
            continue
        m = BULLET.match(line)
        if m and section:
            items.append({'term': m.group(1).strip(), 'def': m.group(2).strip(), 'section': section})
    return items


def read_canon_terms():
    out = []
    for path in sorted(LECTURES.glob('*.md')):
        text = path.read_text(encoding='utf-8')
        m = re.search(r'^#### Словарь\s*$(.*?)(?=^#### |^## )', text, re.M | re.S)
        if not m:
            continue
        for line in m.group(1).splitlines():
            b = re.match(r'^\*\s+\*\*(.+?)\*\*\s+—\s+(.+)$', line.strip())
            if b:
                out.append({'term': b.group(1).strip(), 'def': b.group(2).strip(), 'section': EXTRA, 'from': path.stem})
    return out


def consolidate():
    seen, items = set(), []
    for it in read_master() + read_canon_terms():
        # ключ — первое слово термина: «CAPEX (capital…)» и «CAPEX» считаются одним термином
        key = re.split(r'[\s(]', it['term'].lower())[0]
        if key in seen:
            continue
        seen.add(key)
        items.append(it)
    items.sort(key=lambda x: x['term'].lower())
    for it in items:
        it['id'] = term_id(it['term'])
    return items


def render_html(items):
    sections = {}
    for it in items:
        sections.setdefault(it['section'], []).append(it)
    rows = []
    for name, group in sections.items():
        dl = ''.join(
            f'<div class="g-item" id="{it["id"]}" data-q="{html.escape((it["term"] + " " + it["def"]).lower(), True)}">'
            f'<dt>{html.escape(it["term"])}</dt><dd>{html.escape(it["def"])}</dd></div>'
            for it in group)
        rows.append(f'<section class="g-sec"><h2>{html.escape(name)}</h2><div class="g-list">{dl}</div></section>')
    body = ''.join(rows)
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Словарь курса «ИИ в редевелопменте» · AI2ARCH</title>
<meta name="description" content="Общий словарь терминов курса: расшифровки и простые объяснения.">
<style>
:root{{--bg:#F6F4F0;--surface:#fff;--ink:#0F1B2D;--muted:#5B6678;--line:#E2DED6;--accent:#C46A16;--accent-l:#FBF1E6;}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#101827;--surface:#172236;--ink:#F3F6FC;--muted:#A9B4C7;--line:#2A3550;--accent:#F0A35C;--accent-l:#2A2418;}}}}
:root[data-theme="dark"]{{--bg:#101827;--surface:#172236;--ink:#F3F6FC;--muted:#A9B4C7;--line:#2A3550;--accent:#F0A35C;--accent-l:#2A2418;}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:860px;margin:0 auto;padding:28px 16px 64px}}
h1{{font-size:clamp(26px,4vw,36px);line-height:1.15;margin:6px 0 8px}}
.lead{{color:var(--muted);margin:0 0 18px}}
.back{{font-size:14px;color:var(--accent);text-decoration:none;font-weight:700}}
.search{{width:100%;box-sizing:border-box;font:inherit;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--surface);color:var(--ink);margin:12px 0 22px}}
.g-sec{{margin:0 0 26px}}
.g-sec h2{{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:0 0 8px}}
.g-list{{display:grid;gap:8px}}
.g-item{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;scroll-margin-top:16px}}
.g-item:target{{border-color:var(--accent);background:var(--accent-l)}}
.g-item dt{{font-weight:800}}
.g-item dd{{margin:3px 0 0;color:var(--muted);font-size:15px}}
.hide{{display:none!important}}
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="redev-guide.html">← Пособие курса</a>
  <h1>Словарь курса</h1>
  <p class="lead">Все термины курса «ИИ в редевелопменте» в одном месте. В лонгридах термины ведут сюда.</p>
  <input class="search" id="q" type="search" placeholder="Поиск по термину или слову в определении" aria-label="Поиск по словарю">
  {body}
</div>
<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{{const s=q.value.trim().toLowerCase();
  document.querySelectorAll('.g-item').forEach(el=>el.classList.toggle('hide',!!s&&!el.dataset.q.includes(s)));
  document.querySelectorAll('.g-sec').forEach(sec=>sec.classList.toggle('hide',!sec.querySelector('.g-item:not(.hide)')));}});
if(location.hash){{const t=document.querySelector(location.hash);if(t)t.scrollIntoView();}}
</script>
</body>
</html>
'''


def main():
    items = consolidate()
    OUT_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding='utf-8')
    OUT_HTML.write_text(render_html(items), encoding='utf-8')
    print(f'терминов: {len(items)}')


if __name__ == '__main__':
    main()
