#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает статический лонгрид из docs/lectures/2.2.md и шаблона."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'docs' / 'lectures' / '2.2.md'
TPL = ROOT / 'templates' / 'longread.html'
OUT = ROOT / 'redev-read-income.html'
SLIDE_DIR = 'images/slides/income'

CHAPTERS = [
    (1, 1, 6, 'Как устроен скелет модели'),
    (2, 7, 12, 'Собираем скелет с нейросетью'),
    (3, 13, 20, 'Проверяем и забираем в работу'),
]

def esc(t):
    return html.escape(t, quote=False)

def inline(t):
    t = esc(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t

def table_html(block):
    rows = [r.strip() for r in block.strip().splitlines() if r.strip().startswith('|')]
    if len(rows) < 2:
        return None
    def cells(r):
        return [c.strip() for c in r.strip().strip('|').split('|')]
    head = cells(rows[0])
    body = [cells(r) for r in rows[2:]]
    out = ['<div class="table-wrap"><table><thead><tr>']
    out += [f'<th>{inline(c)}</th>' for c in head]
    out.append('</tr></thead><tbody>')
    for row in body:
        out.append('<tr>' + ''.join(f'<td data-label="{html.escape(head[i] if i < len(head) else "", True)}">{inline(c)}</td>' for i,c in enumerate(row)) + '</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)

def md_html(text):
    text = text.strip()
    if not text:
        return ''
    blocks = re.split(r'\n\s*\n', text)
    out = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if b.startswith('|'):
            t = table_html(b)
            if t:
                out.append(t); continue
        lines = [l.rstrip() for l in b.splitlines()]
        if all(re.match(r'^\d+\.\s', l) for l in lines if l.strip()):
            items = [re.sub(r'^\d+\.\s*', '', l) for l in lines if l.strip()]
            out.append('<ol>' + ''.join('<li>' + inline(x) + '</li>' for x in items) + '</ol>')
            continue
        if all(re.match(r'^[*-]\s', l) for l in lines if l.strip()):
            items = [re.sub(r'^[*-]\s*', '', l) for l in lines if l.strip()]
            out.append('<ul>' + ''.join('<li>' + inline(x) + '</li>' for x in items) + '</ul>')
            continue
        # numbered list with continuation lines
        if lines and re.match(r'^\d+\.\s', lines[0]):
            items=[]; cur=''
            for l in lines:
                if re.match(r'^\d+\.\s', l):
                    if cur: items.append(cur)
                    cur=re.sub(r'^\d+\.\s*','',l)
                else:
                    cur += ' ' + l.strip()
            if cur: items.append(cur)
            out.append('<ol>' + ''.join(f'<li>{inline(x.strip())}</li>' for x in items) + '</ol>')
            continue
        out.append('<p>' + inline(' '.join(l.strip() for l in lines)) + '</p>')
    return '\n'.join(out)

def section_text(lines, name):
    """Возвращает текст h4-секции по имени."""
    start = None
    for i,l in enumerate(lines):
        if l.strip() == '#### ' + name:
            start = i + 1; break
    if start is None: return ''
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith('#### ') or lines[j].startswith('## '):
            end = j; break
    return '\n'.join(lines[start:end]).strip()

def strip_memo(text):
    return re.sub(r'#### ПРАКТИЧЕСКАЯ ПАМЯТКА ЛЕКТОРУ\n[\s\S]*?(?=\n#### |\n### |\n## |\Z)', '', text).strip()

def parse_slides(part_text):
    ms = list(re.finditer(r'^### Слайд (\d+) · (.+)$', part_text, re.M))
    slides=[]
    for i,m in enumerate(ms):
        end = ms[i+1].start() if i+1 < len(ms) else len(part_text)
        body = part_text[m.end():end]
        body = re.sub(r'^#### .*$[\s\S]*', '', body, flags=re.M).strip()
        slides.append((int(m.group(1)), m.group(2).strip(), body))
    return slides

def parse_slide(n,title,body):
    data={'n':n,'title':title,'base':'','why':'','context':'','c52':{},'transition':'','task':'','prompt':''}
    # prompt line
    pm = re.search(r'^ПРОМПТ \(на экран, вслух не читается\):\s*\*«(.+?)»\*\s*$', body, re.M)
    if pm:
        data['prompt'] = pm.group(1).strip()
        body = body[:pm.start()] + body[pm.end():]
    # self-study line
    sm = re.search(r'^\*Самостоятельно после лекции:\s*(.+?)\*\s*$', body, re.M)
    if sm:
        data['task'] = sm.group(1).strip()
        body = body[:sm.start()] + body[sm.end():]
    markers = [
        ('base', r'\*\*▶ ОСНОВА\*\*'),
        ('why', r'\*\*◆ ЗАЧЕМ И ЭКОНОМИКА\*\*'),
        ('context', r'\*\*◇ КОНТЕКСТ И ИСТОРИЯ(?: \[МОЖНО СОКРАТИТЬ\])?\*\*'),
        ('c52', r'\*\*⚠ C52: ЧТО ЕСТЬ И С ЧЕМ РАБОТАЕМ\*\*'),
        ('transition', r'\*\*➜ ПЕРЕХОД\*\*'),
    ]
    found=[]
    for key,pat in markers:
        m=re.search(pat,body)
        if m: found.append((m.start(),m.end(),key))
    found.sort()
    # preamble before first marker is base continuation
    if not found:
        data['base']=body.strip()
        return data
    if found[0][0] > 0:
        pre=body[:found[0][0]].strip()
        if pre: data['base']=pre
    for i,(s,e,key) in enumerate(found):
        end=found[i+1][0] if i+1<len(found) else len(body)
        text=body[e:end].strip()
        if key=='c52':
            fields={}
            for line in text.splitlines():
                m=re.match(r'^\*\*(Что есть|Чего нет|С чем работаем|Как закрываем):\*\*\s*(.*)$', line.strip())
                if m: fields[m.group(1)]=m.group(2).strip()
            data['c52']=fields
        elif key in ('base','why','context','transition'):
            data[key]=(data[key]+'\n\n'+text).strip() if data[key] else text
    return data

def load():
    raw = SRC.read_text(encoding='utf-8')
    # глоссарий
    gtxt = section_text(raw.splitlines(), 'Словарь')
    gtxt = re.sub(r'^\*Для лектора:.*\*\s*$', '', gtxt, flags=re.M)
    terms=[]
    for line in gtxt.splitlines():
        m=re.match(r'^\*\s+\*\*(.+?)\*\*\s+—\s+(.+)$', line.strip())
        if m:
            name=m.group(1).strip(); definition=m.group(2).strip()
            terms.append((name,definition))
    # сквозной пример
    ext = section_text(raw.splitlines(), 'Сквозной учебный пример')
    ext = re.sub(r'^\*Для демонстрации.*?C52\.\*\s*', '', ext, flags=re.S).strip()
    # части
    parts=[]
    for m in re.finditer(r'^## Часть (\d+) · Слайды [^\n]+$', raw, re.M):
        end = raw.find('\n## Часть ', m.end())
        if end == -1: end = len(raw)
        text = strip_memo(raw[m.end():end])
        parts.append((int(m.group(1)), text))
    parsed=[]
    for num,text in parts:
        slides=parse_slides(text)
        # intro = text before first slide, remove tail h4
        first = re.search(r'^### Слайд ', text, re.M)
        intro=text[:first.start()].strip() if first else ''
        intro=re.sub(r'^#### .*$[\s\S]*', '', intro, flags=re.M).strip()
        if num in (2,3):
            intro=''
        parsed.append({'num':num,'intro':intro,'slides':[parse_slide(*s) for s in slides],
                       'result':section_text(text.splitlines(),'Минимальный результат слушателя'),
                       'not':section_text(text.splitlines(),'Что не разбираем'),
                       'memo':section_text(text.splitlines(),'Практическая памятка'),
                       'caveats':section_text(text.splitlines(),'Оговорки'),
                       'final':section_text(text.splitlines(),'Итог темы 2.2')})
    return terms, ext, parsed

def slide_img(n, cls='slide-inline'):
    name=f'{n:02d}'
    return (f'<figure class="{cls}"><img src="{SLIDE_DIR}/{name}-800.webp" '
            f'srcset="{SLIDE_DIR}/{name}-800.webp 800w, {SLIDE_DIR}/{name}.webp 1600w" '
            f'sizes="(max-width:1099px) calc(100vw - 40px), 640px" loading="lazy" '
            f'alt="Слайд {n} из 20"><figcaption>Слайд {n} из 20</figcaption></figure>')

def c52_card(fields):
    if not fields: return ''
    labels=[('Что есть','Что есть'),('Чего нет','Чего нет'),('С чем работаем','С чем работаем'),('Как закрываем','Как закрываем')]
    rows=''.join(f'<div class="c52-row"><span>{lab}</span><p>{inline(fields[key])}</p></div>' for key,lab in labels if key in fields)
    return f'<aside class="c52-card"><div class="c52-mark">C52: что есть и с чем работаем</div>{rows}</aside>'

def chapter_end(ch):
    if not ch['result'] and not ch['not'] and not ch['memo'] and not ch['caveats']:
        return ''
    parts=['<section class="chapter-end"><h2>Итог главы</h2>']
    if ch['result']:
        parts.append('<div class="end-card"><h3>Минимальный результат слушателя</h3>'+md_html(ch['result'])+'</div>')
    if ch['not']:
        parts.append('<div class="end-card"><h3>Что не разбираем</h3>'+md_html(ch['not'])+'</div>')
    if ch['memo']:
        parts.append('<div class="end-card"><h3>Практическая памятка</h3>'+md_html(ch['memo'])+'</div>')
    if ch['caveats']:
        parts.append('<details class="caveats"><summary>Оговорки</summary>'+md_html(ch['caveats'])+'</details>')
    parts.append('</section>')
    return ''.join(parts)

def mark_terms(html_text, terms):
    used=set(); out=[]; skip=0
    skip_tags={'h1','h2','h3','h4','summary','button','pre','code','figcaption'}
    tokens=re.split(r'(<[^>]+>)', html_text)
    for tok in tokens:
        if tok.startswith('<'):
            tm=re.match(r'</?([a-zA-Z0-9]+)',tok)
            if tm and tm.group(1).lower() in skip_tags:
                if tok.startswith('</'): skip=max(0,skip-1)
                elif not tok.endswith('/>'): skip+=1
            out.append(tok); continue
        if skip:
            out.append(tok); continue
        for name,defn in terms:
            if name in used: continue
            pat=r'(?<![\wА-Яа-яЁё])'+re.escape(name)+r'(?![\wА-Яа-яЁё])'
            if re.search(pat,tok):
                tok=re.sub(pat, lambda m: f'<span class="term" tabindex="0" data-def="{html.escape(defn, True)}">{m.group(0)}</span>', tok, count=1)
                used.add(name); break
        out.append(tok)
    return ''.join(out)

def build():
    terms, example, parts = load()
    chapter_bodies=[]; toc=[]
    for ci,(cnum,a,b,name) in enumerate(CHAPTERS):
        part=next(p for p in parts if any(s['n']==a for s in p['slides']))
        slides=[s for s in part['slides'] if a<=s['n']<=b]
        toc.append(f'<a href="#chapter-{cnum}" class="toc-ch">Глава {cnum}. {esc(name)}</a>')
        body=[f'<section class="chapter" id="chapter-{cnum}" data-chapter="{cnum}"><header class="chapter-head"><div class="chapter-kicker">Глава {cnum}</div><h1>{esc(name)}</h1></header>']
        if part['intro']:
            body.append('<div class="lesson-intro" id="intro">'+md_html(part['intro'])+'</div>')
        if cnum==1 and example:
            body.append('<aside class="example-card" id="example"><div class="example-mark">Учебный пример, не данные C52</div>'+md_html(example)+'</aside>')
        for s in slides:
            toc.append(f'<a href="#slide-{s["n"]}" class="toc-slide"><span>{s["n"]}</span>{esc(s["title"])}</a>')
            sec=[f'<section class="slide-sec" id="slide-{s["n"]}" data-n="{s["n"]}"><div class="sec-kicker">Слайд {s["n"]} из 20</div><h2>{esc(s["title"])}</h2>']
            sec.append(slide_img(s['n']))
            sec.append('<div class="prose">'+md_html(s['base'])+'</div>')
            if s['prompt']:
                pid=f'prompt-{s["n"]}'
                sec.append(f'<div class="prompt-block"><div class="prompt-bar"><span>Промпт</span><button class="copy" data-copy="{pid}">Копировать</button></div><pre id="{pid}">{esc(s["prompt"])}</pre></div>')
            if s['c52']:
                sec.append(c52_card(s['c52']))
            for key,label in [('why','Зачем и экономика'),('context','Контекст и история')]:
                if s[key]:
                    sec.append(f'<details class="fold"><summary>{label}</summary><div class="prose">{md_html(s[key])}</div></details>')
            if s['task']:
                sec.append(f'<div class="task-card"><label><input type="checkbox" data-task="{s["n"]}"> <span>Сделано</span></label><p>{inline(s["task"])}</p></div>')
            if s['transition']:
                sec.append(f'<p class="transition">{inline(s["transition"])}</p>')
            sec.append('</section>')
            body.append(''.join(sec))
        body.append(chapter_end(part))
        if cnum==3 and part['final']:
            body.append('<section class="lesson-end" id="lesson-end"><h2>Итог темы 2.2</h2>'+md_html(part['final'])+'</section>')
        body.append('</section>')
        chapter_bodies.append(''.join(body))
    body_html=''.join(chapter_bodies)
    body_html=mark_terms(body_html, terms)
    glossary=''.join(f'<div><dt>{esc(n)}</dt><dd>{inline(d)}</dd></div>' for n,d in terms)
    # rail
    rail=''.join(f'<img data-rail="{n}" src="{SLIDE_DIR}/{n:02d}-800.webp" srcset="{SLIDE_DIR}/{n:02d}-800.webp 800w, {SLIDE_DIR}/{n:02d}.webp 1600w" sizes="480px" loading="lazy" alt="Слайд {n} из 20">' for n in range(1,21))
    rail=rail.replace('data-rail="1"','data-rail="1" class="active"',1)
    slides_json=json.dumps([{'n':n,'title':next(s['title'] for p in parts for s in p['slides'] if s['n']==n)} for n in range(1,21)], ensure_ascii=False)
    # время чтения по видимому тексту
    words=len(re.sub(r'<[^>]+>',' ',body_html).split())
    minutes=max(1,round(words/180))
    tpl=TPL.read_text(encoding='utf-8')
    out=(tpl.replace('{{READ_TIME}}',str(minutes)).replace('{{BODY}}',body_html)
         .replace('{{TOC}}',''.join(toc)).replace('{{GLOSSARY}}',glossary)
         .replace('{{RAIL}}',rail).replace('{{SLIDES_JSON}}',slides_json)
         .replace('{{WORDS}}',str(words)))
    OUT.write_text(out,encoding='utf-8')
    print(f'{OUT.name}: {words} слов, {minutes} мин, {len(body_html)} байт')

if __name__=='__main__':
    build()
