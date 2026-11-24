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
<meta name="robots" content="noindex, nofollow">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700;800;900&display=swap">
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box;border-radius:0}}
:root{{--ink:#0A0F1A;--muted:#2A2F3E;--faint:#5A6070;--line:#E1DDD5;--blue:#2B4FD8;--blue-l:#E4EBFB;--sans:'Inter Tight','Helvetica Neue',Arial,sans-serif}}
html{{scroll-behavior:smooth}}
body{{font-family:var(--sans);letter-spacing:-0.005em;color:var(--ink);background-color:#F6F4F0;
  background-image:linear-gradient(to right,#E1DDD5 1px,transparent 1px),linear-gradient(to bottom,#E1DDD5 1px,transparent 1px);
  background-size:calc(min(100%,1200px)/4) 100%,100% 120px;background-position:center top,center top;background-repeat:repeat-y,repeat-y}}
@media(min-width:900px){{body{{background-size:calc(min(100%,1200px)/8) 100%,100% 120px}}}}
a{{color:var(--blue);text-decoration:none}}
.back-bar{{position:sticky;top:0;z-index:50;display:flex;align-items:stretch;min-height:54px;background:#F6F4F0;border-bottom:1.5px solid var(--ink)}}
.back-bar>*{{display:flex;align-items:center}}
.back-btn,.head-actions a{{background:transparent;color:var(--ink);border:1.5px solid var(--ink);font-size:15px;font-weight:800;letter-spacing:-0.02em;padding:16px 22px;white-space:nowrap;text-decoration:none}}
.back-btn{{gap:10px}}
.guide-breadcrumb{{flex:1;min-width:0;overflow:hidden;gap:8px;padding:0 20px 0 16px;white-space:nowrap}}
.bc-root,.bc-sep{{color:#848A9A;font-size:14px;font-weight:600}}
.bc-cur{{color:var(--blue);font-size:15px;font-weight:800;letter-spacing:-0.02em}}
.head-actions a+a{{border-left:none}}
.bar-brand{{padding:0 16px;border-left:1.5px solid var(--ink)}}
.bar-brand img{{width:30px;height:30px}}
.hs-short{{display:none}}
.wrap{{max-width:1200px;margin:0 auto;padding:44px 32px 80px}}
@media(min-width:900px){{.g-list{{grid-template-columns:repeat(2,1fr);gap:0}}.g-item{{border-left:1px solid var(--line)}}.g-item:nth-child(2n+1){{border-left:none}}.g-item:nth-child(-n+2){{border-top:none}}}}
h1{{font-size:clamp(26px,4vw,34px);line-height:1.15;font-weight:900;letter-spacing:-0.035em;margin:0 0 10px}}
.lead{{color:var(--muted);font-size:15px;line-height:1.5;margin:0 0 22px}}
.search{{display:block;width:100%;font:inherit;font-size:15px;padding:13px 14px;border:1.5px solid var(--ink);background:#fff;color:var(--ink);margin:0 0 26px;outline:none}}
.search:focus{{border-color:var(--blue)}}
.g-sec{{margin:0 0 28px}}
.g-sec h2{{font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--blue);margin:0 0 10px}}
.g-list{{display:grid;gap:0;border:1.5px solid var(--ink);background:#fff}}
.g-item{{padding:13px 16px;border-top:1px solid var(--line);scroll-margin-top:72px}}
.g-item:first-child{{border-top:none}}
.g-item:target{{background:var(--blue-l);box-shadow:inset 3px 0 0 var(--blue)}}
.g-item dt{{font-weight:800;letter-spacing:-0.02em}}
.g-item dd{{margin:3px 0 0;color:var(--muted);font-size:14.5px;line-height:1.5}}
.hide{{display:none!important}}
.back-bar{{background:#F6F4F0!important;backdrop-filter:none!important;z-index:100}}
.back-bar .head-actions a{{background:#F6F4F0!important;opacity:1!important}}
  /* ── компактные пилюли в шапке (кнопки расписания/тетради/пособия/словаря) ── */
  .back-bar .head-actions{{align-self:center !important;display:flex !important;align-items:center !important;gap:6px !important;border:0 !important;padding:0 14px 0 0 !important;}}
  .back-bar .head-actions a:not(.head-schedule){{display:inline-flex !important;}}
  .back-bar .head-actions a,.back-bar .workbook-btn{{align-items:center !important;justify-content:center !important;height:30px !important;padding:0 13px !important;margin:0 !important;border:1px solid #0A0F1A !important;border-radius:999px !important;background:transparent !important;color:#0A0F1A !important;font-family:'Inter Tight','Helvetica Neue',Arial,sans-serif !important;font-size:12px !important;font-weight:700 !important;letter-spacing:-0.01em !important;line-height:1 !important;white-space:nowrap !important;text-decoration:none !important;box-shadow:none !important;}}
  .back-bar .head-actions a:hover,.back-bar .workbook-btn:hover{{background:#0A0F1A !important;color:#F6F4F0 !important;text-decoration:none !important;}}
  @media (max-width:640px){{
    .back-bar .head-actions{{gap:4px !important;padding:0 8px 0 0 !important;}}
    .back-bar .head-actions a,.back-bar .workbook-btn{{height:26px !important;padding:0 9px !important;font-size:11px !important;}}
  }}
@media(max-width:760px){{.hs-full{{display:none}}.hs-short{{display:inline}}}}
@media(max-width:640px){{
  .back-bar{{padding:6px 8px;gap:4px;min-height:0}}
  .back-btn,.head-actions a{{font-size:11px;padding:6px 8px}}
  .bar-brand,.guide-breadcrumb{{display:none}}
  .head-actions{{margin-left:auto}}
  .wrap{{padding:24px 16px 56px}}
}}
</style>
</head>
<body>
<div class="back-bar">
  <a class="back-btn" href="redev-guide.html"><span>←</span> <span>К пособию</span></a>
  <div class="guide-breadcrumb">
    <span class="bc-root">ИИ в редевелопменте</span>
    <span class="bc-sep">/</span>
    <span class="bc-cur">Словарь</span>
  </div>
  <div class="head-actions">
    <a href="redev-schedule.html"><span class="hs-full">Расписание ↗</span><span class="hs-short">Расписание</span></a>
  </div>
  <a class="bar-brand" href="index.html" title="AI2ARCH — на главную" aria-label="AI2ARCH — на главную"><img src="images/ai2arch-sign.png" width="30" height="30" alt=""></a>
</div>
<div class="wrap">
  <h1>Словарь курса</h1>
  <p class="lead">Все термины курса «ИИ в редевелопменте» в одном месте.</p>
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
