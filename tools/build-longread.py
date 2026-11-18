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

C52_PLANS = [
    ('plan2016-1etazh-uroven1-fragment.jpg', '1 этаж, уровень 1 — фрагмент. По обмерам 2016 г.'),
    ('plan2016-1etazh-uroven1-s-okruzheniem.jpg', '1 этаж, уровень 1 — с окружением. По обмерам 2016 г.'),
    ('plan2016-1etazh-uroven2.jpg', '1 этаж, уровень 2. Серая заливка — зона на отметке 0,000; без заливки — антресоль. По обмерам 2016 г.'),
    ('plan2016-2etazh.jpg', '2 этаж. По обмерам 2016 г.'),
    ('plan2016-3etazh.jpg', '3 этаж. По обмерам 2016 г.'),
    ('plan2016-4etazh.jpg', '4 этаж. По обмерам 2016 г.'),
]

TRAINER = [
    ('аренда большого зала (почасовая)', 'income'),
    ('аренда малого зала', 'income'),
    ('субаренда под фитобар', 'income'),
    ('продажа абонементов', 'income'),
    ('коммунальные платежи (вода, тепло, свет)', 'opex'),
    ('клининг', 'opex'),
    ('охрана', 'opex'),
    ('техобслуживание вентиляции', 'opex'),
    ('налог на имущество', 'opex'),
    ('вывоз ТБО', 'opex'),
    ('архитектурный проект', 'capex', '1 · Обследование и проектирование'),
    ('инженерные изыскания', 'capex', '1 · Обследование и проектирование'),
    ('демонтаж старого оборудования', 'capex', '2 · Конструктив'),
    ('усиление проёмов', 'capex', '2 · Конструктив'),
    ('приточно-вытяжная вентиляция', 'capex', '3 · Инженерия'),
    ('новые стояки', 'capex', '3 · Инженерия'),
    ('акустические панели', 'capex', '4 · Отделка'),
    ('специализированный пол для залов', 'capex', '4 · Отделка'),
    ('душевые кабины', 'capex', '4 · Отделка'),
    ('освещение входа', 'capex', '5 · Благоустройство'),
    ('получение разрешительной документации', 'capex', '6 · Согласования'),
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

def extract_verdict(text):
    """Вынимает фразу «Вывод …: …» из основного текста."""
    m = re.search(r'(?:(?<=[.!?])\s+|^)(Вывод[^\n:]{0,80}:\s*)(.+?\.)(?=\s|$)', text, re.S)
    if not m:
        return text, ''
    verdict = m.group(2).strip()
    before = text[:m.start()].rstrip()
    after = text[m.end():].lstrip()
    if before and after:
        text = before + ' ' + after
    else:
        text = before or after
    text = re.sub(r' {2,}', ' ', text).strip()
    return text, verdict

def parse_slide(n,title,body):
    data={'n':n,'title':title,'base':'','verdict':'','why':'','context':'','c52':{},'transition':'','task':'','prompt':''}
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
        data['base'], data['verdict'] = extract_verdict(data['base'])
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
    data['base'], data['verdict'] = extract_verdict(data['base'])
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
    return (f'<figure class="{cls}" data-n="{n}"><div class="inline-frame"><img src="{SLIDE_DIR}/{name}-1600.webp" '
            f'srcset="{SLIDE_DIR}/{name}-1600.webp 1600w, {SLIDE_DIR}/{name}.webp 3200w" '
            f'sizes="(min-width:1100px) 1000px, calc(100vw - 32px)" loading="lazy" '
            f'alt="Слайд {n} из 20"><button class="expand-btn" type="button" data-open="{n}">⤢ Развернуть</button></div>'
            f'<figcaption>Слайд {n} из 20</figcaption></figure>')

def c52_gallery(n):
    if n not in (5, 13):
        return ''
    items=''.join(
        f'<button class="c52-thumb" type="button" data-img="images/c52/{file}" data-caption="{html.escape(cap, True)}">'
        f'<img src="images/c52/{file}" alt="{html.escape(cap, True)}" loading="lazy" decoding="async"></button>'
        for file,cap in C52_PLANS
    )
    return f'<div class="c52-gallery"><div class="c52-gallery-mark">Планы C52 · по обмерам 2016 г.</div><div class="c52-thumbs">{items}</div></div>'

def c52_card(fields, n=0):
    if not fields: return ''
    labels=[('Что есть','Что есть'),('Чего нет','Чего нет'),('С чем работаем','С чем работаем'),('Как закрываем','Как закрываем')]
    rows=''.join(f'<div class="c52-row"><span>{lab}</span><p>{inline(fields[key])}</p></div>' for key,lab in labels if key in fields)
    return f'<aside class="c52-card"><div class="c52-mark">C52: что есть и с чем работаем</div>{rows}{c52_gallery(n)}</aside>'

def chapter_brief(cnum, slides, minutes):
    items=[]
    for sl in slides:
        verdict = f'<p>{inline(sl["verdict"])}</p>' if sl.get('verdict') else ''
        items.append(f'<li><a href="#slide-{sl["n"]}"><b>{sl["n"]}</b><span>{esc(sl["title"])}</span></a>{verdict}</li>')
    return (f'<aside class="chapter-brief"><div class="brief-head"><span>Главное в главе</span>'
            f'<span class="brief-time">{minutes} мин чтения</span></div><ol>{"".join(items)}</ol></aside>')

def trainer_block():
    return '''<section class="trainer" id="trainer" aria-labelledby="trainerTitle">
  <div class="trainer-head"><div class="trainer-kicker">Тренажёр</div><h3 id="trainerTitle">Доходы, OPEX или CAPEX?</h3><p class="trainer-sub">Учебный пример, не данные C52.</p></div>
  <div class="trainer-top"><span id="trainerProgress">1 из 21</span><span id="trainerLast" class="trainer-last"></span></div>
  <div class="trainer-body" id="trainerBody"></div>
  <div class="trainer-feedback" id="trainerFeedback" aria-live="polite"></div>
  <div class="trainer-actions" id="trainerActions"></div>
</section>'''

def gaps_registry():
    rows = [
        ('Выписка ПЗЗ','Орган местного самоуправления','Допустимую функцию и градостроительные ограничения','Доходы и CAPEX','income capex'),
        ('Актуальный техпаспорт','БТИ','GBA, GLA, состав помещений','Доходы и CAPEX','income capex'),
        ('ТУ по мощности','Ресурсоснабжающая организация','Доступная мощность','CAPEX (инженерия) и OPEX','opex capex phase3'),
        ('Обследование конструкций','Проектная организация','Несущую способность, потребность в усилении','CAPEX','capex'),
    ]
    items=''.join(
        f'<button class="gap-row" type="button" data-blocks="{blocks}" aria-pressed="false">'
        f'<span class="gap-doc">{esc(doc)}</span>'
        f'<span class="gap-meta"><b>Кто выдаёт:</b> {esc(issuer)}</span>'
        f'<span class="gap-meta"><b>Что определяет:</b> {esc(defines)}</span>'
        f'<span class="gap-affects"><b>Влияет:</b> {esc(affects)}</span></button>'
        for doc,issuer,defines,affects,blocks in rows
    )
    phases=''.join(f'<span class="ms-phase" data-block="phase{i}">{name}</span>' for i,name in enumerate(
        ['Обследование и проектирование','Конструктив','Инженерия','Отделка','Благоустройство','Согласования'],1))
    return f'''<section class="gaps-block" id="gaps" aria-labelledby="gapsTitle">
  <div class="gaps-head"><div class="gaps-kicker">Реестр</div><h3 id="gapsTitle">Документ → зависимость</h3><p>Нажмите на строку — подсветятся блоки модели, которые ждут этот документ.</p></div>
  <div class="gaps-layout">
    <div class="gaps-list">{items}</div>
    <div class="mini-scheme" aria-label="Мини-схема скелета модели">
      <div class="ms-op"><span class="ms-label">Операционная часть · в год</span>
        <span class="ms-block" data-block="income">Доходы</span><span class="ms-sign">−</span>
        <span class="ms-block" data-block="opex">OPEX</span><span class="ms-sign">=</span>
        <span class="ms-block ms-noi" data-block="noi">NOI</span>
      </div>
      <div class="ms-capex"><span class="ms-label">CAPEX · по фазам</span><span class="ms-capex-box" data-block="capex">{phases}</span></div>
    </div>
  </div>
  <p class="gaps-note">Без цифр: только документы и зависимости.</p>
</section>'''

def finish_card(tasks):
    items=''.join(
        f'<li data-finish-task="{t["n"]}"><a href="#slide-{t["n"]}">Слайд {t["n"]} · {esc(t["title"])}</a>'
        f'<span>{inline(t["task"])}</span></li>'
        for t in tasks
    )
    return f'''<section class="finish-card" id="finish">
  <div class="finish-kicker">Финал</div>
  <h2>Урок прочитан</h2>
  <p class="finish-count" id="finishCount">Задания: 0 из {len(tasks)} отмечены</p>
  <div class="finish-missing" id="finishMissing"><h3>Осталось самостоятельно</h3><ul>{items}</ul></div>
  <div class="finish-actions">
    <a class="finish-btn finish-btn-dark" href="https://fortune-swing-02e.notion.site/41112bb3b5cd81839661da69963a035b?source=copy_link" target="_blank" rel="noopener">Рабочая тетрадь ↗</a>
    <a class="finish-btn" href="redev-guide.html#t22">Промпты темы 2.2</a>
    <a class="finish-btn" href="redev-guide.html#t23">Следующая тема →</a>
  </div>
</section>'''

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
    skip_tags={'h1','h2','h3','h4','summary','button','pre','code','figcaption','script','style'}
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
    chapter_bodies=[]; toc=[]; all_tasks=[]
    for ci,(cnum,a,b,name) in enumerate(CHAPTERS):
        part=next(p for p in parts if any(s['n']==a for s in p['slides']))
        slides=[s for s in part['slides'] if a<=s['n']<=b]
        toc.append(f'<a href="#chapter-{cnum}" class="toc-ch">Глава {cnum}. {esc(name)}</a>')
        header=f'<header class="chapter-head"><div class="chapter-kicker">Глава {cnum}</div><h1>{esc(name)}</h1></header>'
        intro_html=''
        if part['intro']:
            intro_html='<div class="lesson-intro" id="intro">'+md_html(part['intro'])+'</div>'
        example_html=''
        if cnum==1 and example:
            example_html='<aside class="example-card" id="example"><div class="example-mark">Учебный пример, не данные C52</div>'+md_html(example)+'</aside>'
        content=[]
        for s in slides:
            toc.append(f'<a href="#slide-{s["n"]}" class="toc-slide"><span>{s["n"]}</span>{esc(s["title"])}</a>')
            sec=[f'<section class="slide-sec" id="slide-{s["n"]}" data-n="{s["n"]}"><div class="sec-kicker">Слайд {s["n"]} из 20</div><h2>{esc(s["title"])}</h2>']
            sec.append(slide_img(s['n']))
            sec.append('<div class="prose">'+md_html(s['base'])+'</div>')
            if s['verdict']:
                sec.append(f'<aside class="verdict"><div class="verdict-mark">Вывод</div><p>{inline(s["verdict"])}</p></aside>')
            if s['prompt']:
                pid=f'prompt-{s["n"]}'
                sec.append(f'<div class="prompt-block"><div class="prompt-bar"><span>Промпт</span><button class="copy" type="button" data-copy="{pid}">Копировать</button></div><pre id="{pid}">{esc(s["prompt"])}</pre></div>')
            if s['c52']:
                sec.append(c52_card(s['c52'], s['n']))
            for key,label in [('why','Зачем и экономика'),('context','Контекст и история')]:
                if s[key]:
                    sec.append(f'<details class="fold"><summary>{label}</summary><div class="prose">{md_html(s[key])}</div></details>')
            if s['task']:
                sec.append(f'<div class="task-card"><label><input type="checkbox" data-task="{s["n"]}"> <span>Сделано</span></label><p>{inline(s["task"])}</p></div>')
                all_tasks.append({'n':s['n'],'title':s['title'],'task':s['task']})
            if s['transition']:
                sec.append(f'<p class="transition">{inline(s["transition"])}</p>')
            sec.append('</section>')
            content.append(''.join(sec))
            if cnum==1 and s['n']==3:
                content.append(trainer_block())
            if cnum==3 and s['n']==13:
                content.append(gaps_registry())
        chapter_visible=header+intro_html+example_html+''.join(content)
        chapter_words=len(re.sub(r'<[^>]+>',' ',chapter_visible).split())
        chapter_minutes=max(1,round(chapter_words/180))
        body=[f'<section class="chapter" id="chapter-{cnum}" data-chapter="{cnum}">',header,
              chapter_brief(cnum,slides,chapter_minutes)]
        if intro_html: body.append(intro_html)
        if example_html: body.append(example_html)
        body += content
        body.append(chapter_end(part))
        if cnum==3 and part['final']:
            body.append('<section class="lesson-end" id="lesson-end"><h2>Итог темы 2.2</h2>'+md_html(part['final'])+'</section>')
            body.append(finish_card(all_tasks))
        body.append('</section>')
        chapter_bodies.append(''.join(body))
    body_html=''.join(chapter_bodies)
    body_html=mark_terms(body_html, terms)
    glossary=''.join(f'<div><dt>{esc(n)}</dt><dd>{inline(d)}</dd></div>' for n,d in terms)
    # rail
    rail=''.join(f'<img data-rail="{n}" src="{SLIDE_DIR}/{n:02d}-1600.webp" srcset="{SLIDE_DIR}/{n:02d}-1600.webp 1600w, {SLIDE_DIR}/{n:02d}.webp 3200w" sizes="(min-width:1280px) 1150px, 1px" loading="lazy" alt="Слайд {n} из 20">' for n in range(1,21))
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
