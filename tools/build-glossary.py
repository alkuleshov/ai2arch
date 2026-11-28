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
    """Словарь в оболочке ISP (tools/isp_shell.py): левое меню по разделам, поиск, термины в две-три колонки."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from isp_shell import page
    sections = {}
    for it in items:
        sections.setdefault(it['section'], []).append(it)
    nav, bands = [], []
    for n, (name, group) in enumerate(sections.items(), 1):
        sid = f'g-{n}'
        nav.append((sid, str(n), name, str(len(group))))
        dl = ''.join(
            f'<div class="i-gi g-item" id="{it["id"]}" data-q="{html.escape((it["term"] + " " + it["def"]).lower(), True)}">'
            f'<dt>{html.escape(it["term"])}</dt><dd>{html.escape(it["def"])}</dd></div>'
            for it in group)
        bands.append(
            f'<section class="i-gsec g-sec" id="{sid}"><div class="i-band i-blk i-grid"><div class="i-bh-k"><b>Раздел {n}</b><span>{len(group)} терминов</span></div>'
            f'<h2 class="i-display i-bh-t">{html.escape(name)}</h2></div>'
            f'<div class="i-band i-wrap"><dl class="i-gl">{dl}</dl></div></section>')
    main = (f'<section class="i-band i-title-band"><h1 class="i-display i-h1">Словарь<span class="g">курса</span></h1>'
            f'<p class="i-lead">Все термины курса «ИИ в редевелопменте» в одном месте: расшифровка и простое объяснение. Всего {len(items)} терминов.</p></section>'
            f'<section class="i-band i-wrap"><input class="i-search" id="q" type="search" placeholder="Поиск по термину или слову в определении" aria-label="Поиск по словарю"></section>'
            + ''.join(bands))
    script = """<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{const s=q.value.trim().toLowerCase();
  document.querySelectorAll('.g-item').forEach(el=>el.classList.toggle('hide',!!s&&!el.dataset.q.includes(s)));
  document.querySelectorAll('.g-sec').forEach(sec=>sec.classList.toggle('hide',!sec.querySelector('.g-item:not(.hide)')));});
if(location.hash&&location.hash.indexOf('#t-')===0){const t=document.querySelector(location.hash);if(t)setTimeout(()=>t.scrollIntoView({block:'center'}),100);}
</script>"""
    return page('glossary', 'Словарь курса «ИИ в редевелопменте» · AI2ARCH',
                'Общий словарь терминов курса: расшифровки и простые объяснения.', 'ИИ в редевелопменте',
                nav, main, script=script)


def main():
    items = consolidate()
    OUT_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding='utf-8')
    OUT_HTML.write_text(render_html(items), encoding='utf-8')
    print(f'терминов: {len(items)}')


if __name__ == '__main__':
    main()
