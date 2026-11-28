#!/usr/bin/env python3
"""Генератор методического пособия ИСП → /home/claude/ai2arch/corp/isp.html"""
import re, html, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from data_isp import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "corp", "isp.html")

def t(s):
    """экранирование + неразрывные пробелы после коротких слов и перед тире"""
    s = html.escape(s, quote=False)
    s = re.sub(r'(?<![\w-])([А-Яа-яЁёA-Za-z]{1,2}) ', '\\1&nbsp;', s)
    s = re.sub(r'(?<![\w-])([А-Яа-яЁёA-Za-z]{1,2}) ', '\\1&nbsp;', s)
    s = s.replace(' — ', '&nbsp;— ').replace(' → ', '&nbsp;→ ')
    s = re.sub(r'(\d) (ч|человек|минут|часа|часов|декабря|февраля|ноября)', '\\1&nbsp;\\2', s)
    s = s.replace('№ ', '№&nbsp;')
    return s

GO = '<svg class="ix-go" viewBox="0 0 26 26" aria-hidden="true"><circle cx="13" cy="13" r="12" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M9 17 L17 9 M11 9 H17 V15" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'

def lead_short(l):
    return l

# ---------- расписание ----------
def sched_rows():
    out = []
    cur = None
    for i, s in enumerate(SESSIONS, 1):
        if s["block"] != cur:
            if cur == 1:
                out.append(f'<tr class="r-pause"><td colspan="6"><b>{t(PAUSE["range"])}</b> · пауза: применение на живых проектах, <a href="#pause">задание между блоками</a></td></tr>')
            cur = s["block"]; b = BLOCKS[cur]
            out.append(f'<tr class="r-blk {b["cls"]}"><td colspan="6"><span>Блок {cur} · {t(b["when"])}</span><b>{t(b["name"])}</b><em>{t(b["range"])} · {b["hours"]}&nbsp;ч очно</em></td></tr>')
            if cur == 1:
                pass
        out.append(
            f'<tr><td class="c-d"><b>{t(s["date"])}</b></td>'
            f'<td class="c-t"><span class="tm">{s["time"]}</span><small>предварительно</small></td>'
            f'<td class="c-f"><span class="fm{" fm-on" if s["fmt"]=="Онлайн" else ""}">{s["fmt"]}</span></td>'
            f'<td class="c-n"><a href="#s{i:02d}">{t(s["title"])}<span class="g"> — {t(s["sub"])}</span></a></td>'
            f'<td class="c-l"><span class="lv {s["lvc"]}">{s["lvl"]}</span></td>'
            f'<td class="c-w">{t(s["lead"])}<small>{t(s["who"])}</small></td></tr>')
        if s["block"] == 1 and i == max(j for j, x in enumerate(SESSIONS, 1) if x["block"] == 1):
            out.append('<tr class="r-res"><td colspan="6"><b>17–18 декабря</b> · резерв на переносы</td></tr>')
    return "\n".join(out)

# ---------- карточки занятий ----------
def session_card(i, s):
    b = BLOCKS[s["block"]]
    flow = []
    for tm, what, who in s["flow"]:
        tag = '<span class="who who-s">сами</span>' if who == "сами" else ('<span class="who">ведущий</span>' if who == "вед" else '')
        cls = ' class="brk"' if not who else ''
        flow.append(f'<li{cls}><span class="ft">{tm}</span><span class="fw">{t(what)}</span>{tag}</li>')
    prep = "".join(f'<li>{t(x)}</li>' for x in s["prep"])
    res = "".join(f'<li>{t(x)}</li>' for x in s["result"])
    note = f'<p class="note">{t(s["note"])}</p>' if s.get("note") else ''
    after = f'<div class="box"><h4>После занятия</h4><p>{t(s["after"])}</p></div>' if s.get("after") else ''
    return f'''
  <article class="band ses" id="s{i:02d}">
    <div class="grid ses-g">
      <div class="ses-n"><span class="nn">{i:02d}</span><span class="bt {b["cls"]}">Блок {s["block"]}</span></div>
      <div class="ses-main">
        <p class="skick"><b>{t(s["date"])}</b> · {s["time"]} · <span class="pre">время предварительное</span></p>
        <h3 class="display ses-title">{t(s["title"])} <span class="g">{t(s["sub"])}</span></h3>
        <dl class="facts">
          <div><dt>Формат</dt><dd>{s["fmt"]}{" в бюро" if s["fmt"]=="Очно" else ", Яндекс Телемост"} · {t(s["dur"])}</dd></div>
          <div><dt>Глубина</dt><dd><span class="lv {s["lvc"]}">{s["lvl"]}</span></dd></div>
          <div><dt>Ведёт</dt><dd>{t(s["lead"])}</dd></div>
          <div><dt>Участники</dt><dd>{t(s["who"])}</dd></div>
        </dl>
        <div class="why"><h4>Зачем бюро</h4><p>{t(s["why"])}</p></div>
        <div class="flow"><h4>Ход занятия</h4><ol>{"".join(flow)}</ol></div>
        {note}
      </div>
      <aside class="ses-side">
        <div class="box"><h4>Подготовить до занятия</h4><ul class="sq">{prep}</ul></div>
        <div class="box"><h4>Результат</h4><ol class="results">{res}</ol></div>
        {after}
      </aside>
    </div>
  </article>'''

def pause_band():
    items = "".join(f'<li><span><b>{t(a)}</b>&nbsp;— {t(b)}</span></li>' for a, b in PAUSE["items"])
    return f'''
<section class="band pause" id="pause" aria-labelledby="pause-h">
  <div class="grid pz">
    <div class="pz-k"><p class="small"><b>Между блоками</b></p><p class="pz-mark">{t(PAUSE["range"])}</p></div>
    <h2 class="display pz-title" id="pause-h">Задание <span class="g">на паузу</span></h2>
    <p class="pz-text">{t(PAUSE["intro"])}</p>
    <ol class="results pz-list">{items}</ol>
  </div>
</section>'''

MON = {"декабря": "дек", "февраля": "фев", "января": "янв", "ноября": "ноя"}
def dshort(d):
    """'Пт 4 декабря' -> ('Пт', '4 дек')"""
    wd, day, mon = d.split(" ")
    return wd, f"{day} {MON.get(mon, mon)}"

def lshort(l):
    return (l.replace("Эксперт по QGIS, Александр Кулешов", "эксперт QGIS + Кулешов")
             .replace("Александр ", "").replace("Екатерина ", ""))

SHORT = {"Нормы и проверка документации":"Нормы и проверка","Презентации и подача":"Презентации","Тексты и документы":"Тексты",
         "ИИ для инженерных разделов":"ИИ для инженеров","Анализ участка (QGIS)":"Анализ участка","Концепции и ИИ-ТЗ":"Концепции и ИИ-ТЗ"}
def part(s):
    m = re.match(r"часть (\d)", s["sub"])
    return f" · ч. {m.group(1)}" if m else ""

GENERAL = [
    ("tasks", "01", "Задачи бюро", "Что бюро хочет получить и где это решается"),
    ("schedule", "02", "Расписание", "Все занятия: даты, время, ведущие"),
    ("how", "03", "Как устроено", "Формат, глубина, кто ведёт"),
    ("prep", "04", "Рабочие места", "Что установить и к какой дате"),
    ("rules", "05", "Правила данных", "Что можно загружать в ИИ"),
]

def side_nav():
    o = ['<a href="#toc" data-l="Содержание"><span>—</span>Содержание</a>']
    for k, n, a, _ in GENERAL:
        o.append(f'<a href="#{k}" data-l="{a}"><span>{n}</span>{t(a)}</a>')
    cur = None
    for i, s in enumerate(SESSIONS, 1):
        if s["block"] != cur:
            if cur == 1:
                o.append(f'<a class="sd-pz" href="#pause" data-l="Пауза: задание между блоками"><span>пауза</span>Задание на паузу</a>')
            cur = s["block"]; b = BLOCKS[cur]
            o.append(f'<a class="sd-blk" href="#block{cur}" data-l="Блок {cur}: {b["name"]}"><span>Блок {cur}</span>{t(b["name"])}</a>')
        wd, d = dshort(s["date"])
        o.append(f'<a class="sd-s" href="#s{i:02d}" data-l="{i:02d} · {s["title"]}{part(s)}"><span>{d}</span>{t(SHORT.get(s["title"], s["title"]))}{part(s)}</a>')
    return "\n      ".join(o)

def toc_block(bn):
    b = BLOCKS[bn]
    rows = []
    for i, s in enumerate(SESSIONS, 1):
        if s["block"] != bn: continue
        wd, d = dshort(s["date"])
        fmt = "онлайн" if s["fmt"] == "Онлайн" else "очно"
        rows.append(f'<a class="ts" href="#s{i:02d}"><span class="ts-n">{i:02d}</span><span class="ts-d">{wd}<b>{d}</b></span>'
                    f'<span class="ts-t">{t(s["title"])}{part(s)}<small>{s["time"]} · {fmt} · {t(lshort(s["lead"]))}</small></span></a>')
    return (f'<div class="toc-b toc-b{bn}"><a class="tb-h" href="#block{bn}"><span>Блок {bn} · {t(b["when"])}</span>'
            f'<b>{t(b["name"])}</b><em>{t(b["range"])} · {b["hours"]}&nbsp;ч очно</em></a>{"".join(rows)}</div>')

def toc_general():
    return "".join(f'<a class="tc" href="#{k}"><span class="tc-n">{n}</span><span class="tc-t">{t(a)}<small>{t(d)}</small></span></a>' for k, n, a, d in GENERAL)

def build():
    n_ses = len(SESSIONS)
    tasks = "".join(f'<li><span class="tk">{t(a)}</span><span class="tz">{t(b)}</span><span class="td">{t(c)}</span></li>' for a, b, c in TASKS)
    levels = "".join(f'<div class="lvd"><span class="lv {c}">{n}</span><p>{t(d)}</p></div>' for n, c, d in LEVELS)
    princ = "".join(f'<div class="pr"><small>{k:02d}</small><b>{t(a)}</b><p>{t(d)}</p></div>' for k, (a, d) in enumerate(PRINCIPLES, 1))
    people = "".join(f'<div class="pp"><b>{t(a)}</b><p>{t(d)}</p></div>' for a, d in PEOPLE)
    prep = "".join(f'<tr><td>{t(a)}</td><td>{t(b)}</td><td class="nw">{t(c)}</td></tr>' for a, b, c in PREP)
    rules = "".join(f'<li>{t(r)}</li>' for r in RULES)

    cards1 = "".join(session_card(i, s) for i, s in enumerate(SESSIONS, 1) if s["block"] == 1)
    cards2 = "".join(session_card(i, s) for i, s in enumerate(SESSIONS, 1) if s["block"] == 2)

    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="referrer" content="no-referrer">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#F6F4F0">
<title>ИСП × AI2ARCH — методическое пособие</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600;700;800;900&display=swap">
<style>
/* Пособие ИСП: стиль главной ai2arch.ru — швейцарская сетка, видимые линии, двухцветные заголовки, цветные строки-индексы.
   Страница открывается только по прямой ссылке: noindex, ссылок с сайта нет. Генерируется скриптом gen_isp.py. */
:root{{
  color-scheme: light;
  --paper:#F6F4F0; --grid:#E1DDD5; --cell:#F1E1E7;
  --ink:#0A0F1A; --gray:#848A9A; --muted:#5A6070;
  --azure:#1A82FF; --blush:#EDC3D2; --cobalt:#2B4FD8; --midnight:#13234B; --powder:#BED0EE; --sand:#E6D9BE;
  --on-dark:#F6F4F0; --on-dark-2:#EDC3D2; --panel:#E7E3DB; --ink-hover:#1E2636;
  --sans:'Inter Tight', 'Helvetica Neue', Arial, system-ui, sans-serif;
  --cols:4; --row:88px;
  --pad:max(16px, env(safe-area-inset-left, 0px)); --pad-r:max(16px, env(safe-area-inset-right, 0px));
}}
@media (min-width: 900px){{ :root{{ --cols:8; --row:120px; --pad:max(32px, env(safe-area-inset-left, 0px)); --pad-r:max(32px, env(safe-area-inset-right, 0px)); }} }}
*{{ box-sizing:border-box; }}
html{{ background:var(--paper); scroll-behavior:smooth; }}
body{{ margin:0; background:var(--paper); color:var(--ink); font-family:var(--sans); font-size:15px; line-height:1.35; -webkit-font-smoothing:antialiased; overflow-x:clip; }}
a{{ color:inherit; }}
:focus-visible{{ outline:2px solid var(--azure); outline-offset:3px; }}
.band{{ position:relative; padding-left:var(--pad); padding-right:var(--pad-r);
  border-bottom:1px solid var(--grid); }}
.grid{{ display:grid; grid-template-columns:repeat(var(--cols), minmax(0,1fr)); column-gap:0; }}
.grid > *{{ min-width:0; }}
.display{{ margin:0; font-weight:800; letter-spacing:-0.045em; line-height:.92; text-wrap:balance; }}
.display .g{{ color:var(--gray); }}
.small{{ margin:0; font-size:12.5px; line-height:1.22; font-weight:500; color:var(--muted); letter-spacing:-0.005em; }}
.small b{{ color:var(--ink); font-weight:700; }}
.bullet{{ display:flex; gap:7px; align-items:baseline; margin:0; font-size:13px; line-height:1.15; font-weight:700; letter-spacing:-0.01em; text-decoration:none; }}
.bullet::before{{ content:''; flex:none; width:8px; height:8px; border-radius:50%; background:var(--ink); transform:translateY(-1px); }}
.bullet:hover{{ text-decoration:underline; text-underline-offset:3px; }}
h4{{ margin:0 0 8px; font-size:12.5px; font-weight:800; letter-spacing:-0.01em; }}

/* шапка */
.head{{ padding-block:18px 0; }}
.brand{{ grid-column:span 4; font-size:clamp(34px, 9.5vw, 46px); padding-bottom:18px; }}
.head-text{{ grid-column:span 2; padding:2px 14px 16px 0; }}
.head-menu{{ grid-column:span 2; display:flex; flex-direction:column; gap:9px; padding:4px 0 16px; }}
@media (min-width:900px){{ .brand{{ grid-column:span 5; font-size:52px; padding-right:20px; }} .head-text{{ grid-column:span 3; padding-top:6px; }} .head-text--2{{ grid-column:6 / span 3; padding-top:0; }} }}
.marks{{ display:flex; align-items:center; justify-content:space-between; padding-block:14px 26px; }}
.signs{{ display:flex; align-items:center; gap:8px; }}
.signs svg{{ display:block; height:52px; width:auto; }}
.goto{{ display:flex; align-items:center; gap:10px; text-decoration:none; }}
.goto svg{{ width:56px; height:56px; }}
.num-badge{{ display:grid; place-items:center; width:52px; height:52px; border-radius:50%; background:var(--ink); color:var(--paper); font-weight:800; font-size:26px; letter-spacing:-0.04em; }}
.goto-cap{{ font-size:12.5px; font-weight:600; color:var(--muted); max-width:13ch; line-height:1.15; text-align:right; }}
@media (min-width:900px){{ .num-badge{{ width:72px; height:72px; font-size:34px; }} .signs svg{{ height:72px; }} .goto svg{{ width:76px; height:76px; }} }}

/* рабочая среда: закреплённое меню */
.app{{ position:relative; }}
.topbar{{ position:sticky; top:0; z-index:40; display:flex; align-items:center; gap:12px; height:54px; padding:0 var(--pad-r) 0 var(--pad); background:rgba(246,244,240,.95); -webkit-backdrop-filter:blur(8px); backdrop-filter:blur(8px); border-bottom:1.5px solid var(--ink); }}
.tb-brand{{ font-size:15px; font-weight:800; letter-spacing:-0.035em; text-decoration:none; white-space:nowrap; }}
.tb-cur{{ flex:1; min-width:0; font-size:12.5px; font-weight:600; color:var(--muted); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.tb-btn{{ flex:none; display:inline-flex; align-items:center; gap:8px; height:38px; padding:0 15px; border:0; border-radius:999px; background:var(--ink); color:var(--paper); font:700 13px/1 var(--sans); cursor:pointer; }}
.tb-btn svg{{ width:14px; height:14px; }}
.side{{ position:fixed; top:0; right:0; bottom:0; z-index:60; width:min(88vw, 360px); overflow-y:auto; overscroll-behavior:contain; padding:14px 16px 14px 20px; background:var(--paper); border-left:1.5px solid var(--ink); transform:translateX(104%); transition:transform .25s ease; }}
.nav-open .side{{ transform:none; }}
.scrim{{ position:fixed; inset:0; z-index:55; background:rgba(10,15,26,.35); opacity:0; pointer-events:none; transition:opacity .2s; }}
.nav-open .scrim{{ opacity:1; pointer-events:auto; }}
.side{{ display:flex; flex-direction:column; }}
.sd-top{{ display:flex; align-items:center; justify-content:space-between; gap:10px; padding-bottom:10px; border-bottom:1.5px solid var(--ink); }}
.sd-brand{{ display:flex; align-items:center; gap:10px; text-decoration:none; color:var(--ink); }}
.sd-logo{{ flex:none; display:grid; place-items:center; width:36px; height:36px; border-radius:8px; background:#0A0F1A; }}
.sd-logo img{{ display:block; width:26px; height:26px; }}
.sd-bt b{{ display:block; font-size:17px; font-weight:800; letter-spacing:-0.04em; line-height:1; }}
.sd-bt small{{ display:block; margin-top:3px; font-size:11px; font-weight:600; letter-spacing:0; line-height:1.1; color:var(--muted); }}
.sd-close{{ flex:none; width:32px; height:32px; border:1.5px solid var(--ink); border-radius:50%; background:none; font:700 17px/1 var(--sans); color:var(--ink); cursor:pointer; }}
.sd-nav{{ --rh:clamp(21px, calc((100vh - 190px) / 25), 31px); margin-top:8px; display:flex; flex-direction:column; }}
.sd-nav a{{ display:grid; grid-template-columns:46px minmax(0,1fr) auto; gap:4px; align-items:center; height:var(--rh); margin:0 -8px; padding:0 8px; border-radius:5px; text-decoration:none; font-size:clamp(12px, calc(var(--rh) * .47), 14px); font-weight:600; letter-spacing:-0.01em; color:var(--ink); white-space:nowrap; overflow:hidden; }}
.sd-nav a > span{{ font-size:clamp(10.5px, calc(var(--rh) * .4), 12px); font-weight:600; color:var(--gray); font-variant-numeric:tabular-nums; }}
.sd-nav a:hover{{ background:rgba(10,15,26,.06); }}
.sd-nav a.is-on{{ background:var(--ink); color:var(--paper); }}
.sd-nav a.is-on > span, .sd-nav a.is-on em{{ color:rgba(246,244,240,.7); }}
.sd-nav .sd-blk{{ margin-top:8px; border-top:1.5px solid var(--ink); border-radius:0; font-size:clamp(13px, calc(var(--rh) * .5), 15px); font-weight:800; letter-spacing:-0.03em; grid-template-columns:46px minmax(0,1fr) auto; }}
.sd-nav .sd-blk em{{ font-style:normal; font-size:10.5px; font-weight:600; color:var(--gray); }}
.sd-nav .sd-blk.is-on{{ border-radius:5px; }}
.sd-nav .sd-pz{{ border-top:1px dashed var(--gray); border-radius:0; }}
.sd-nav .sd-pz.is-on{{ border-radius:5px; }}
.sd-tg{{ margin-top:auto; padding-top:10px; font-size:11.5px; font-weight:700; color:var(--muted); text-decoration:none; }}
.sd-tg:hover{{ color:var(--ink); text-decoration:underline; }}
[id]{{ scroll-margin-top:66px; }}
@media (min-width:1100px){{
  .topbar, .scrim, .sd-close{{ display:none; }}
  .app{{ display:grid; grid-template-columns:276px minmax(0,1fr); }}
  .side{{ position:sticky; top:0; height:100vh; width:auto; z-index:1; transform:none; transition:none; border-left:0; border-right:1.5px solid var(--ink); padding:16px 16px 14px 24px; }}
  [id]{{ scroll-margin-top:12px; }}
}}
.main{{ min-width:0; }}

/* первый экран: содержание прямо на полотне */
.toc-g{{ padding-block:18px 28px; row-gap:26px; }}
.toc-cap{{ grid-column:1/-1; display:flex; justify-content:space-between; align-items:baseline; gap:12px; margin:0; padding-bottom:10px; border-bottom:1.5px solid var(--ink); }}
.toc-cap b{{ font-size:clamp(30px, 8vw, 48px); font-weight:800; letter-spacing:-0.05em; line-height:.9; }}
.toc-cap span{{ font-size:12.5px; font-weight:600; color:var(--muted); text-align:right; }}
.toc-gen, .toc-b{{ grid-column:1/-1; display:flex; flex-direction:column; }}
.toc-k{{ margin:0 0 6px; font-size:10.5px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--gray); }}
.tc{{ display:grid; grid-template-columns:34px minmax(0,1fr); gap:8px; align-items:baseline; padding:10px 0; border-bottom:1px solid var(--grid); text-decoration:none; }}
.tc-n{{ font-size:13px; font-weight:800; color:var(--gray); font-variant-numeric:tabular-nums; }}
.tc-t{{ font-size:21px; font-weight:800; letter-spacing:-0.035em; line-height:1.02; }}
.tc-t small, .ts-t small{{ display:block; margin-top:4px; font-size:12px; font-weight:500; letter-spacing:0; line-height:1.25; color:var(--muted); }}
.tc:hover .tc-t, .ts:hover .ts-t, .tb-h:hover b{{ text-decoration:underline; text-underline-offset:3px; text-decoration-thickness:1.5px; }}
.tb-h{{ display:block; padding:0 0 10px; border-bottom:1.5px solid var(--ink); text-decoration:none; }}
.tb-h span{{ display:block; font-size:10.5px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--gray); }}
.tb-h b{{ display:block; margin:5px 0 4px; font-size:24px; font-weight:800; letter-spacing:-0.04em; line-height:1; }}
.tb-h em{{ font-style:normal; font-size:12.5px; font-weight:600; color:var(--muted); }}
.ts{{ display:grid; grid-template-columns:24px 58px minmax(0,1fr); gap:8px; align-items:baseline; padding:9px 0; border-bottom:1px solid var(--grid); text-decoration:none; }}
.ts-n{{ font-size:11.5px; font-weight:800; color:var(--gray); font-variant-numeric:tabular-nums; }}
.ts-d{{ font-size:11px; font-weight:600; color:var(--muted); line-height:1.1; }}
.ts-d b{{ display:block; font-size:14px; font-weight:800; color:var(--ink); letter-spacing:-0.02em; white-space:nowrap; }}
.ts-t{{ font-size:15.5px; font-weight:700; letter-spacing:-0.02em; line-height:1.15; }}
.toc-pz{{ grid-column:1/-1; display:grid; grid-template-columns:minmax(0,1fr) auto; gap:4px 14px; align-items:baseline; padding:12px 0; border-top:1px dashed var(--gray); border-bottom:1px dashed var(--gray); text-decoration:none; }}
.toc-pz b{{ font-size:17px; font-weight:800; letter-spacing:-0.025em; }}
.toc-pz span{{ font-size:12.5px; font-weight:600; color:var(--muted); }}
.toc-pz:hover b{{ text-decoration:underline; text-underline-offset:3px; }}
@media (min-width:900px){{
  .toc-gen{{ grid-column:1 / span 3; padding-right:24px; }}
  .toc-b1{{ grid-column:4 / span 5; }}
  .toc-pz{{ grid-column:4 / span 5; }}
  .toc-b2{{ grid-column:4 / span 5; }}
}}
@media (min-width:1360px){{
  .toc-gen{{ grid-column:1 / span 2; padding-right:20px; }}
  .toc-b1{{ grid-column:3 / span 3; padding-right:20px; }}
  .toc-b2{{ grid-column:6 / span 3; grid-row:2; }}
  .toc-pz{{ grid-column:3 / span 6; }}
}}
/* приветственный экран: на десктопе вся шапка и содержание помещаются в одну высоту окна */
@media (min-width:1100px) and (min-height:720px){{
  .head{{ padding-block:clamp(10px, 2.2vh, 20px) 0; }}
  .brand{{ font-size:clamp(40px, 7vh, 56px); padding-bottom:clamp(8px, 1.6vh, 16px); }}
  .head-text, .head-text--2{{ padding-top:0; padding-bottom:clamp(6px, 1.2vh, 12px); }}
  .toc-g{{ padding-block:clamp(8px, 1.6vh, 16px) 0; row-gap:clamp(8px, 1.6vh, 16px); }}
  .toc-cap b{{ font-size:clamp(26px, 4.4vh, 40px); }}
  .toc-cap{{ padding-bottom:6px; }}
  .toc-k{{ margin-bottom:2px; }}
  .tc{{ padding:clamp(3px, .6vh, 7px) 0; }}
  .tc-t{{ font-size:clamp(15px, 2.3vh, 19px); }}
  .tc-t small, .ts-t small{{ display:inline; margin:0 0 0 8px; font-size:12px; }}
  .tb-h{{ padding-bottom:clamp(4px, .8vh, 8px); }}
  .tb-h b{{ font-size:clamp(18px, 3.2vh, 26px); margin:2px 0; }}
  .ts{{ padding:clamp(3px, .6vh, 7px) 0; }}
  .ts-t{{ font-size:clamp(13.5px, 2.1vh, 16px); }}
  .ts-d b{{ font-size:13px; }}
  .toc-pz{{ padding:clamp(5px, .9vh, 9px) 0; }}
  .toc-pz b{{ font-size:15px; }}
}}
.word{{ position:relative; z-index:0; margin:-.1em 0 0; padding:0; font-weight:800; letter-spacing:-0.075em; line-height:.76; font-size:22vw; white-space:nowrap; width:max-content; }}
.word-wrap{{ overflow:hidden; padding-bottom:1.2vw; }}

/* разделы */
.sec-head{{ padding-block:20px 18px; }}
.sec-title{{ grid-column:span 4; font-size:clamp(32px, 8.4vw, 64px); padding-bottom:14px; }}
.sec-note{{ grid-column:span 4; }}
@media (min-width:900px){{ .sec-title{{ grid-column:span 5; padding-bottom:0; }} .sec-note{{ grid-column:6 / span 3; padding-top:6px; }} }}
.wrap{{ padding-block:18px 24px; }}
.wrap > *{{ grid-column:1/-1; }}

/* задачи бюро */
.tasks{{ list-style:none; margin:0; padding:0; }}
.tasks li{{ display:grid; grid-template-columns:1fr; gap:2px; padding:12px 0; border-top:1px solid var(--grid); }}
.tasks li:last-child{{ border-bottom:1px solid var(--grid); }}
.tk{{ font-size:20px; font-weight:800; letter-spacing:-0.035em; line-height:1.05; }}
.tz{{ font-size:14px; font-weight:600; }}
.td{{ font-size:13px; color:var(--muted); font-weight:500; }}
@media (min-width:900px){{ .tasks li{{ grid-template-columns:3fr 3fr 2fr; align-items:baseline; gap:12px; }} .tk{{ font-size:24px; }} }}

/* уровни и форматы */
.lv{{ display:inline-block; padding:3px 8px 4px; border-radius:999px; font-size:11.5px; font-weight:700; line-height:1; white-space:nowrap; }}
.lv-o{{ background:var(--powder); }} .lv-p{{ background:var(--blush); }} .lv-v{{ background:var(--cobalt); color:var(--on-dark); }} .lv-s{{ background:var(--midnight); color:var(--on-dark); }}
.fm{{ display:inline-block; padding:2px 7px 3px; border:1.5px solid var(--ink); border-radius:999px; font-size:11.5px; font-weight:700; line-height:1; }}
.fm-on{{ border-style:dashed; }}
.levels{{ display:grid; gap:10px; margin-top:16px; }}
.lvd{{ display:grid; grid-template-columns:96px minmax(0,1fr); gap:10px; align-items:baseline; }}
.lvd .lv{{ justify-self:start; }}
.lvd p{{ margin:0; font-size:13.5px; color:var(--muted); font-weight:500; line-height:1.3; }}
@media (min-width:900px){{ .levels{{ grid-template-columns:repeat(3, minmax(0,1fr)); gap:20px; }} .lvd{{ grid-template-columns:1fr; gap:8px; }} }}

/* расписание */
.sch{{ width:100%; border-collapse:collapse; font-size:14px; }}
.sch th{{ text-align:left; font-size:11px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); padding:0 10px 8px 0; border-bottom:1.5px solid var(--ink); }}
.sch td{{ padding:12px 10px 12px 0; border-bottom:1px solid var(--grid); vertical-align:top; }}
.sch small{{ display:block; margin-top:3px; font-size:11.5px; color:var(--muted); font-weight:500; }}
.sch .tm{{ font-weight:700; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.sch .c-d b{{ white-space:nowrap; }}
.sch .c-n a{{ font-weight:700; text-decoration:none; }}
.sch .c-n a:hover{{ text-decoration:underline; text-underline-offset:3px; }}
.sch .c-n .g{{ color:var(--muted); font-weight:500; }}
.r-blk td{{ padding:22px 0 10px; border-bottom:1.5px solid var(--ink); }}
.r-blk span{{ display:block; font-size:11px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; opacity:.8; }}
.r-blk b{{ font-size:22px; font-weight:800; letter-spacing:-0.035em; margin-right:10px; }}
.r-blk em{{ font-style:normal; font-size:13px; font-weight:600; white-space:nowrap; display:inline-block; }}
.r-pause td{{ padding:12px 0; font-size:13.5px; border-top:1px dashed var(--gray); border-bottom:1px dashed var(--gray); }}
.r-res td{{ padding:10px 0; font-size:13.5px; color:var(--muted); }}
@media (max-width:899px){{
  .sch, .sch tbody, .sch tr, .sch td{{ display:block; width:100%; }}
  .sch thead{{ display:none; }}
  .sch tr{{ padding:12px 0; border-bottom:1px solid var(--grid); }}
  .sch tr.r-blk, .sch tr.r-pause, .sch tr.r-res{{ padding:0; border:0; margin-top:8px; }}
  .sch td{{ border:0; padding:2px 0; }}
  .sch tr:not(.r-blk):not(.r-pause):not(.r-res){{ display:grid; grid-template-columns:auto auto 1fr; gap:4px 10px; align-items:baseline; }}
  .sch .c-d{{ grid-column:1; }} .sch .c-t{{ grid-column:2; }} .sch .c-f{{ grid-column:3; justify-self:end; }}
  .sch .c-t small{{ display:none; }}
  .sch .c-n, .sch .c-l, .sch .c-w{{ grid-column:1/-1; }}
  .sch .c-n a{{ font-size:17px; }}
  .sch tr.r-blk td{{ padding:18px 0 8px; }} .sch tr.r-pause td, .sch tr.r-res td{{ padding:10px 0; }}
}}
.sch-note{{ margin:12px 0 0; }}

/* принципы и ведущие */
.prs{{ display:grid; grid-template-columns:repeat(var(--cols), minmax(0,1fr)); }}
.pr, .pp{{ grid-column:span 4; padding:16px 14px 18px 0; border-top:1px solid var(--grid); }}
.pr small{{ font-size:10.5px; font-weight:600; color:var(--gray); }}
.pr b, .pp b{{ display:block; margin:6px 0 6px; font-size:20px; font-weight:800; letter-spacing:-0.035em; line-height:1; }}
.pr p, .pp p{{ margin:0; font-size:13.5px; line-height:1.32; color:var(--muted); font-weight:500; }}
@media (min-width:900px){{ .pr{{ grid-column:span 2; min-height:calc(var(--row) * 1.5); }} .pp{{ grid-column:span 2; }} .pp:first-child{{ grid-column:span 4; }} }}

/* подготовка рабочих мест */
.prep{{ width:100%; border-collapse:collapse; font-size:14px; }}
.prep th{{ text-align:left; font-size:11px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); padding:0 10px 8px 0; border-bottom:1.5px solid var(--ink); }}
.prep td{{ padding:11px 12px 11px 0; border-bottom:1px solid var(--grid); vertical-align:top; }}
.prep td:first-child{{ font-weight:600; }}
.prep .nw{{ white-space:nowrap; font-weight:700; }}
@media (max-width:899px){{
  .prep thead{{ display:none; }}
  .prep, .prep tbody, .prep tr, .prep td{{ display:block; }}
  .prep tr{{ padding:10px 0; border-bottom:1px solid var(--grid); }}
  .prep td{{ border:0; padding:1px 0; }}
  .prep td:nth-child(2){{ color:var(--muted); font-size:13px; }}
  .prep td:nth-child(3)::before{{ content:'Готово к: '; font-weight:500; color:var(--muted); }}
}}
.note{{ margin:14px 0 0; padding:10px 12px; border-left:3px solid var(--azure); background:rgba(26,130,255,.06); font-size:13.5px; line-height:1.35; font-weight:500; }}

/* правила данных — полночная полоса */
.dark{{ background-color:var(--midnight); color:var(--on-dark); border-bottom:0; }}
.dk{{ padding-block:22px 26px; row-gap:16px; }}
.dk-k{{ grid-column:span 4; }}
.dk-k .small{{ color:rgba(246,244,240,.75); }}
.dk-mark{{ display:block; font-size:clamp(64px, 18vw, 120px); font-weight:800; letter-spacing:-0.07em; line-height:.8; margin-top:10px; }}
.dk-title{{ grid-column:span 4; font-size:clamp(34px, 9vw, 60px); }}
.dk-title .g{{ color:var(--on-dark-2); }}
.dk-list{{ grid-column:span 4; }}
.dark .results li{{ color:var(--on-dark); font-weight:600; }}
.dark .results li::before{{ background:var(--blush); color:var(--midnight); }}
@media (min-width:900px){{ .dk-k{{ grid-column:span 2; }} .dk-mark{{ font-size:84px; }} .dk-title{{ grid-column:3 / span 5; }} .dk-list{{ grid-column:3 / span 5; }} }}

/* списки */
.results{{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px; counter-reset:r; }}
.results li{{ display:grid; grid-template-columns:22px minmax(0,1fr); gap:8px; align-items:start; font-size:14px; font-weight:600; line-height:1.25; letter-spacing:-0.01em; }}
.results li::before{{ counter-increment:r; content:counter(r); display:grid; place-items:center; width:20px; height:20px; border-radius:50%; background:var(--ink); color:var(--paper); font-size:11px; font-weight:800; }}
.sq{{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:7px; }}
.sq li{{ display:grid; grid-template-columns:14px minmax(0,1fr); gap:8px; font-size:14px; line-height:1.28; font-weight:500; }}
.sq li::before{{ content:''; width:10px; height:10px; border:1.5px solid var(--ink); margin-top:3px; }}

/* занятия */
.ses{{ padding-block:0; }}
.ses-g{{ padding-block:26px 30px; row-gap:20px; }}
.ses-n{{ grid-column:span 4; display:flex; align-items:center; gap:10px; }}
.nn{{ font-size:56px; font-weight:800; letter-spacing:-0.07em; line-height:.8; }}
.bt{{ display:inline-block; padding:4px 9px 5px; border-radius:999px; font-size:11.5px; font-weight:700; line-height:1; }}
.bt.b1{{ background:var(--blush); }} .bt.b2{{ background:var(--powder); }}
.ses-main{{ grid-column:span 4; display:flex; flex-direction:column; gap:16px; }}
.ses-side{{ grid-column:span 4; display:flex; flex-direction:column; gap:14px; }}
@media (min-width:900px){{
  .ses-g{{ row-gap:0; }}
  .ses-n{{ grid-column:span 1; flex-direction:column; align-items:flex-start; }}
  .nn{{ font-size:64px; }}
  .ses-main{{ grid-column:2 / span 4; padding-right:28px; }}
  .ses-side{{ grid-column:6 / span 3; }}
}}
.skick{{ margin:0; font-size:13px; font-weight:600; color:var(--muted); }}
.skick b{{ color:var(--ink); }}
.pre{{ white-space:nowrap; }}
.ses-title{{ font-size:clamp(32px, 8.4vw, 52px); }}
.ses-title .g{{ display:block; margin-top:6px; font-size:.56em; letter-spacing:-0.035em; line-height:1; }}
.facts{{ display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:12px 12px; margin:0; }}
.facts dt{{ margin:0 0 3px; font-size:12.5px; font-weight:800; letter-spacing:-0.01em; }}
.facts dd{{ margin:0; font-size:13.5px; line-height:1.28; font-weight:500; color:var(--muted); }}
@media (min-width:900px){{ .facts{{ grid-template-columns:repeat(4, minmax(0,1fr)); }} }}
.why p{{ margin:0; font-size:15px; line-height:1.42; font-weight:500; max-width:62ch; }}
.flow ol{{ list-style:none; margin:0; padding:0; border-top:1px solid var(--grid); }}
.flow li{{ display:grid; grid-template-columns:92px minmax(0,1fr) auto; gap:4px 12px; align-items:baseline; padding:9px 0; border-bottom:1px solid var(--grid); font-size:14px; line-height:1.3; }}
.flow .ft{{ font-weight:700; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.flow .fw{{ font-weight:500; }}
.flow li.brk .fw{{ color:var(--muted); }}
.who{{ font-size:11px; font-weight:700; color:var(--muted); white-space:nowrap; }}
.who-s{{ color:var(--ink); background:var(--blush); padding:2px 7px 3px; border-radius:999px; }}
@media (max-width:520px){{ .flow li{{ grid-template-columns:1fr auto; }} .flow .ft{{ grid-column:1; }} .flow .who{{ grid-column:2; grid-row:1; }} .flow .fw{{ grid-column:1/-1; }} }}
.box{{ padding:14px; background:rgba(246,244,240,.85); border:1.5px solid var(--ink); }}
.box p{{ margin:0; font-size:14px; line-height:1.32; font-weight:500; }}
.blk-head{{ padding-block:22px 20px; }}
.blk-head .bh-k{{ grid-column:span 4; }}
.blk-head .bh-t{{ grid-column:span 4; font-size:clamp(36px, 10vw, 72px); }}
.blk-head{{ border-top:3px solid var(--ink); }}
@media (min-width:900px){{ .blk-head .bh-k{{ grid-column:span 2; padding-top:8px; }} .blk-head .bh-t{{ grid-column:3 / span 6; }} }}

/* пауза */
.pause{{ border-top:1px dashed var(--gray); }}
.pz{{ padding-block:24px 28px; row-gap:16px; }}
.pz-k{{ grid-column:span 4; }}
.pz-mark{{ margin:8px 0 0; font-size:26px; font-weight:800; letter-spacing:-0.04em; line-height:1; }}
.pz-title{{ grid-column:span 4; font-size:clamp(34px, 9vw, 60px); }}
.pz-text{{ grid-column:span 4; margin:0; font-size:15px; line-height:1.4; font-weight:500; max-width:60ch; }}
.pz-list{{ grid-column:span 4; }}
@media (min-width:900px){{ .pz-k{{ grid-column:span 2; }} .pz-title, .pz-text, .pz-list{{ grid-column:3 / span 5; }} }}

/* подвал */
.foot{{ padding-block:18px 26px; row-gap:14px; }}
.foot-a{{ grid-column:span 2; }} .foot-b{{ grid-column:span 2; }} .foot-c{{ grid-column:span 4; }}
.foot-a p, .foot-b p{{ margin:0; font-size:13px; font-weight:700; letter-spacing:-0.01em; }}
.foot-b p{{ color:var(--gray); }}
.btn{{ display:inline-flex; align-items:center; gap:10px; min-height:44px; padding:0 18px; border-radius:999px; font-size:14px; font-weight:700; text-decoration:none; border:1.5px solid var(--ink); background:var(--ink); color:var(--paper); margin-top:10px; }}
.btn:hover{{ background:var(--ink-hover); }}
@media (min-width:900px){{ .foot-a{{ grid-column:span 1; }} .foot-b{{ grid-column:span 1; }} .foot-c{{ grid-column:4 / span 4; }} }}

@media (prefers-reduced-motion: reduce){{ *{{ transition:none !important; }} html{{ scroll-behavior:auto; }} }}
@media print{{
  .band{{ background-image:none !important; }}
  .topbar, .side, .scrim, .word-wrap, .btn{{ display:none !important; }} .app{{ display:block !important; }}
  .ses, .box, .pr, .tasks li{{ break-inside:avoid; }}
  .dark{{ background:#fff !important; color:var(--ink) !important; }}
  .dark .results li{{ color:var(--ink); }} .dk-title .g{{ color:var(--gray); }}
  body{{ font-size:12px; }}
}}
</style>
</head>
<body>
<div class="topbar">
  <a class="tb-brand" href="#top">ИСП × AI2ARCH</a>
  <span class="tb-cur" id="tbCur">Содержание</span>
  <button class="tb-btn" type="button" aria-controls="side" aria-expanded="false"><svg viewBox="0 0 14 14" aria-hidden="true"><path d="M1 3h12M1 7h12M1 11h12" stroke="currentColor" stroke-width="2"/></svg>Содержание</button>
</div>
<div class="app">
<aside class="side" id="side" aria-label="Содержание пособия">
  <div class="sd-top"><a class="sd-brand" href="/"><span class="sd-logo"><img src="/images/ai2arch-sign.png" alt="" width="26" height="26"></span><span class="sd-bt"><b>AI2ARCH</b><small>ИСП · методическое пособие</small></span></a><button class="sd-close" type="button" aria-label="Закрыть меню">×</button></div>
  <nav class="sd-nav">
      {side_nav()}
  </nav>
  <a class="sd-tg" href="https://t.me/alkuleshov" rel="noopener" target="_blank">Вопросы: @alkuleshov</a>
</aside>
<main class="main" id="top">

<header class="band head">
  <div class="grid">
    <h1 class="display brand">ИСП × AI2ARCH <span class="g">Методическое пособие для&nbsp;сотрудников</span></h1>
    <p class="small head-text">Корпоративное обучение ИИ для&nbsp;проектного бюро ИСП: расписание и&nbsp;описание каждого занятия под&nbsp;задачи бюро.</p>
    <p class="small head-text head-text--2"><b>Даты и&nbsp;время предварительные на&nbsp;{t(AS_OF)}&nbsp;г.</b> Время московское. Час занятия&nbsp;— астрономический, 60&nbsp;минут.</p>
  </div>
</header>

<section class="band toc" id="toc" aria-labelledby="toc-h">
  <div class="grid toc-g">
    <h2 class="toc-cap" id="toc-h"><b>Содержание</b><span>{n_ses} занятий · 7&nbsp;декабря&nbsp;— 24&nbsp;февраля</span></h2>
    <nav class="toc-gen" aria-label="Общие разделы"><p class="toc-k">Общее</p>{toc_general()}</nav>
    {toc_block(1)}
    <a class="toc-pz" href="#pause"><b>Пауза между блоками: задание на&nbsp;живых проектах</b><span>{t(PAUSE["range"])}</span></a>
    {toc_block(2)}
  </div>
</section>

<section aria-labelledby="tasks-h" id="tasks">
  <div class="band sec-head"><div class="grid">
    <h2 class="display sec-title" id="tasks-h">Задачи бюро <span class="g">и&nbsp;где они решаются</span></h2>
    <p class="small sec-note">Программа собрана под задачи, которые назвало бюро. Команда прошла базовый курс по&nbsp;нейросетям и&nbsp;работает в&nbsp;ChatGPT Plus и&nbsp;Qwen, поэтому начинаем сразу с&nbsp;работы на&nbsp;объекте.</p>
  </div></div>
  <div class="band"><div class="grid wrap"><ul class="tasks">{tasks}</ul></div></div>
</section>

<section aria-labelledby="schedule-h" id="schedule">
  <div class="band sec-head"><div class="grid">
    <h2 class="display sec-title" id="schedule-h">Расписание <span class="g">двух блоков</span></h2>
    <p class="small sec-note"><b>Даты и&nbsp;время предварительные на&nbsp;{t(AS_OF)}&nbsp;г.</b> Время московское, час&nbsp;— 60&nbsp;минут. Название занятия ведёт к&nbsp;его описанию.</p>
  </div></div>
  <div class="band"><div class="grid wrap">
    <table class="sch">
      <thead><tr><th>Дата</th><th>Время</th><th>Формат</th><th>Занятие</th><th>Глубина</th><th>Ведёт · участники</th></tr></thead>
      <tbody>
{sched_rows()}
      </tbody>
    </table>
    <div class="levels">{levels}</div>
  </div></div>
</section>

<section aria-labelledby="how-h" id="how">
  <div class="band sec-head"><div class="grid">
    <h2 class="display sec-title" id="how-h">Как устроено <span class="g">обучение</span></h2>
    <p class="small sec-note">Показываем приём&nbsp;— вы делаете на&nbsp;своём объекте&nbsp;— проверяем результат и&nbsp;замеряем время.</p>
  </div></div>
  <div class="band"><div class="grid wrap"><div class="prs">{princ}</div></div></div>
  <div class="band"><div class="grid wrap"><h4>Кто ведёт</h4><div class="prs">{people}</div></div></div>
</section>

<section aria-labelledby="prep-h" id="prep">
  <div class="band sec-head"><div class="grid">
    <h2 class="display sec-title" id="prep-h">Подготовка <span class="g">рабочих мест</span></h2>
    <p class="small sec-note">Все занятия проходят на&nbsp;компьютерах бюро. Ответственный в&nbsp;бюро ставит программы к&nbsp;указанной дате, на&nbsp;Старте проверяем всё вместе.</p>
  </div></div>
  <div class="band"><div class="grid wrap">
    <table class="prep"><thead><tr><th>Что подготовить</th><th>Для каких занятий</th><th>Готово к</th></tr></thead><tbody>{prep}</tbody></table>
    <p class="note">{t(PREP_NOTE)}</p>
  </div></div>
</section>

<section class="band dark" id="rules" aria-labelledby="rules-h">
  <div class="grid dk">
    <div class="dk-k"><p class="small">Обязательно для&nbsp;всех участников</p><span class="dk-mark">{len(RULES)}</span></div>
    <h2 class="display dk-title" id="rules-h">Правила работы <span class="g">с&nbsp;данными в&nbsp;ИИ</span></h2>
    <ol class="results dk-list">{rules}</ol>
  </div>
</section>

<section aria-labelledby="b1-h" id="block1">
  <div class="band blk-head b1"><div class="grid">
    <p class="small bh-k"><b>Блок 1 · {t(BLOCKS[1]["when"])}</b><br>{t(BLOCKS[1]["range"])} · {BLOCKS[1]["hours"]}&nbsp;ч очно и&nbsp;0,5&nbsp;ч онлайн</p>
    <h2 class="display bh-t" id="b1-h">{t(BLOCKS[1]["name"])}</h2>
  </div></div>
  {cards1}
</section>

{pause_band()}

<section aria-labelledby="b2-h" id="block2">
  <div class="band blk-head b2"><div class="grid">
    <p class="small bh-k"><b>Блок 2 · {t(BLOCKS[2]["when"])}</b><br>{t(BLOCKS[2]["range"])} · {BLOCKS[2]["hours"]}&nbsp;ч очно</p>
    <h2 class="display bh-t" id="b2-h">{t(BLOCKS[2]["name"])}</h2>
  </div></div>
  {cards2}
</section>

<footer class="band">
  <div class="grid foot">
    <div class="foot-a"><p>ИСП × AI2ARCH</p></div>
    <div class="foot-b"><p>Лаборатория проектного интеллекта</p></div>
    <div class="foot-c">
      <p class="small"><b>Вопросы по&nbsp;программе, переносы и&nbsp;материалы&nbsp;— Александр Кулешов.</b></p>
      <p class="small" style="margin-top:6px">Пособие для&nbsp;сотрудников ИСП. Материалы занятий бюро использует внутри компании.</p>
      <a class="btn" href="https://t.me/alkuleshov" rel="noopener" target="_blank">Telegram @alkuleshov</a>
    </div>
  </div>
  <div class="word-wrap"><p class="word" aria-hidden="true">ИСП×AI2ARCH</p></div>
</footer>
</main>
</div>
<div class="scrim" aria-hidden="true"></div>

<script>
/* Марка растягивается ровно на ширину полосы */
(function(){{
  var w=document.querySelector('.word'); if(!w) return;
  function fit(){{ w.style.fontSize='100px'; var box=w.parentNode.clientWidth; var k=box/w.scrollWidth; w.style.fontSize=(100*k)+'px'; }}
  fit(); window.addEventListener('resize', fit);
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(fit);
}})();
/* Меню: открытие на телефоне и подсветка текущего раздела */
(function(){{
  var body=document.body, btn=document.querySelector('.tb-btn'), side=document.getElementById('side'), cur=document.getElementById('tbCur');
  function open(v){{ body.classList.toggle('nav-open', v); btn.setAttribute('aria-expanded', v?'true':'false'); }}
  btn.addEventListener('click', function(){{ open(!body.classList.contains('nav-open')); }});
  document.querySelector('.sd-close').addEventListener('click', function(){{ open(false); }});
  document.querySelector('.scrim').addEventListener('click', function(){{ open(false); }});
  document.addEventListener('keydown', function(e){{ if(e.key==='Escape') open(false); }});
  var links=[].slice.call(side.querySelectorAll('.sd-nav a'));
  links.forEach(function(a){{ a.addEventListener('click', function(){{ open(false); }}); }});
  var map=links.map(function(a){{ return {{a:a, el:document.getElementById(a.getAttribute('href').slice(1))}}; }}).filter(function(m){{ return m.el; }});
  var last=null, tick=false;
  function spy(){{
    tick=false; var line=Math.min(window.innerHeight*0.3, 260), on=null;
    for(var i=0;i<map.length;i++){{ if(map[i].el.getBoundingClientRect().top-line<=0) on=map[i]; }}
    if(!on) on=map[0];
    if(on===last) return; last=on;
    links.forEach(function(a){{ a.classList.remove('is-on'); a.removeAttribute('aria-current'); }});
    on.a.classList.add('is-on'); on.a.setAttribute('aria-current','location');
    cur.textContent=on.a.getAttribute('data-l')||'';
    var r=on.a.offsetTop, h=side.clientHeight;
    if(r<side.scrollTop+60 || r>side.scrollTop+h-80) side.scrollTop=Math.max(0, r-h/3);
  }}
  window.addEventListener('scroll', function(){{ if(!tick){{ tick=true; requestAnimationFrame(spy); }} }}, {{passive:true}});
  window.addEventListener('resize', spy); spy();
}})();
</script>
</body>
</html>
'''

SHELL = """<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive"><meta name="referrer" content="no-referrer"><meta name="theme-color" content="#F9DADA">
<title>ИСП × AI2ARCH — методическое пособие</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;700;800&display=swap">
<style>
*{box-sizing:border-box}html,body{margin:0;background:#F6F4F0;color:#0A0F1A;font-family:'Inter Tight','Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased}
.gate{position:sticky;top:0;z-index:10;display:flex;align-items:center;flex-wrap:wrap;gap:10px 14px;padding:12px 16px;background:#F9DADA;border-bottom:1px solid #E8A3A3;border-left:4px solid #C0392B}
.badge{display:inline-flex;align-items:center;gap:6px;background:#C0392B;color:#fff;font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;padding:6px 11px;border-radius:6px;white-space:nowrap}
.txt{flex:1 1 180px;font-size:13px;line-height:1.25;color:#8A3232;font-weight:600}
form{display:flex;gap:8px;flex-wrap:wrap;flex:0 1 auto}
input{width:150px;height:38px;padding:0 12px;border:1px solid #E8A3A3;border-radius:7px;background:#fff;font:600 14px 'Inter Tight',Arial,sans-serif;color:#0A0F1A}
input::placeholder{color:#B87A7A;font-weight:500}
input:focus-visible{outline:2px solid #C0392B;outline-offset:1px}
button{height:38px;padding:0 18px;border:0;border-radius:7px;background:#C0392B;color:#fff;font:700 13.5px 'Inter Tight',Arial,sans-serif;cursor:pointer;white-space:nowrap}
button:hover{opacity:.9}button:disabled{opacity:.6}
.err{flex-basis:100%;min-height:0;margin:0;font-size:12.5px;font-weight:700;color:#8A3232}
.err:empty{display:none}
.prev{position:relative;height:calc(100vh - 62px);overflow:hidden;pointer-events:none;user-select:none}
.prev img{display:block;width:100%;height:auto;min-height:100%;object-fit:cover;object-position:top}
.prev::after{content:'';position:absolute;inset:0;background:linear-gradient(to bottom,rgba(246,244,240,0) 55%,#F6F4F0 100%)}
.prev .m{display:none}
@media (max-width:700px){.prev .d{display:none}.prev .m{display:block}input{flex:1 1 40%;width:auto;min-width:0}form{flex:1 1 100%}button{flex:1 1 100%}.txt{flex-basis:100%;font-size:12.5px}.gate{padding:10px 14px}}
</style></head><body>
<div class="gate" role="region" aria-label="Вход">
  <span class="badge">🔒 ИСП × AI2ARCH</span>
  <form id="f" autocomplete="on">
    <input id="p" name="password" type="password" placeholder="Пароль" aria-label="Пароль" autocomplete="current-password" required>
    <button id="b" type="submit">Войти</button>
  </form>
  <p class="err" id="e" role="alert"></p>
</div>
<div class="prev" aria-hidden="true"><img class="d" alt="" src="__PREV_D__"><img class="m" alt="" src="__PREV_M__"></div>
<script>
(function(){
  var D = __PAYLOAD__;
  var f=document.getElementById('f'), er=document.getElementById('e'), bt=document.getElementById('b');
  function b64(s){ var r=atob(s), a=new Uint8Array(r.length); for(var i=0;i<r.length;i++) a[i]=r.charCodeAt(i); return a; }
  async function keyFrom(pass){
    var enc=new TextEncoder();
    var base=await crypto.subtle.importKey('raw', enc.encode(pass.trim()), 'PBKDF2', false, ['deriveKey']);
    return crypto.subtle.deriveKey({name:'PBKDF2', salt:b64(D.s), iterations:D.i, hash:'SHA-256'}, base, {name:'AES-GCM', length:256}, true, ['decrypt']);
  }
  async function open(key){
    var buf=await crypto.subtle.decrypt({name:'AES-GCM', iv:b64(D.n)}, key, b64(D.c));
    var html=new TextDecoder().decode(buf), hash=location.hash;
    document.open(); document.write(html); document.close();
    if(hash){ setTimeout(function(){ var el=document.getElementById(hash.slice(1)); if(el) el.scrollIntoView(); }, 60); }
  }
  async function tryKey(key, silent){
    try{ await open(key); return true; }catch(x){ if(!silent) er.textContent='Неверный пароль'; return false; }
  }
  f.addEventListener('submit', async function(ev){
    ev.preventDefault(); er.textContent=''; bt.disabled=true; bt.textContent='Проверяем…';
    try{
      if(!(window.crypto&&crypto.subtle)){ er.textContent='Откройте страницу по защищённой ссылке https://'; return; }
      var key=await keyFrom(document.getElementById('p').value);
      var raw=await crypto.subtle.exportKey('raw', key);
      var ok=await tryKey(key, false);
      if(ok){ try{ sessionStorage.setItem('isp_k', btoa(String.fromCharCode.apply(null,new Uint8Array(raw)))); }catch(x){} }
    } finally { bt.disabled=false; bt.textContent='Войти'; }
  });
  /* повторное открытие в той же вкладке: ключ хранится до закрытия вкладки */
  window.addEventListener('load', function(){
    try{
      var saved=sessionStorage.getItem('isp_k');
      if(saved && window.crypto && crypto.subtle){
        crypto.subtle.importKey('raw', b64(saved), {name:'AES-GCM'}, false, ['decrypt']).then(function(k){ return tryKey(k, true); }).then(function(ok){ if(!ok) sessionStorage.removeItem('isp_k'); });
      }
    }catch(x){}
  });
})();
</script></body></html>
"""

def previews(plain):
    """Размытые снимки начала страницы (размытие запечено в картинку, текст не восстановить)."""
    import base64, io
    from PIL import Image, ImageFilter
    from playwright.sync_api import sync_playwright
    tmp = "/tmp/isp_plain.html"; open(tmp, "w", encoding="utf-8").write(plain)
    out = []
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for w, h, tw, rad in ((1440, 1100, 1100, 6), (390, 1300, 390, 4)):
            pg = br.new_page(viewport={"width": w, "height": 900}); pg.goto("file://" + tmp); pg.wait_for_timeout(900)
            png = pg.screenshot(clip={"x": 0, "y": 0, "width": w, "height": h}, full_page=True)
            im = Image.open(io.BytesIO(png)).convert("RGB")
            im = im.resize((tw, int(im.height * tw / im.width)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(rad))
            buf = io.BytesIO(); im.save(buf, "JPEG", quality=60)
            out.append("data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode())
        br.close()
    return out

def encrypt(plain, password, iters=300000):
    import base64, secrets
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    import json
    salt, nonce = secrets.token_bytes(16), secrets.token_bytes(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iters).derive(password.strip().encode("utf-8"))
    ct = AESGCM(key).encrypt(nonce, plain.encode("utf-8"), None)
    b = lambda x: base64.b64encode(x).decode()
    pd, pm = previews(plain)
    return (SHELL.replace("__PREV_D__", pd).replace("__PREV_M__", pm)
                 .replace("__PAYLOAD__", json.dumps({"s": b(salt), "n": b(nonce), "i": iters, "c": b(ct)})))

if __name__ == "__main__":
    # Пароль в репозиторий не кладём: передаётся переменной ISP_PASS при сборке.
    # Без них (или с --plain) открытая версия пишется только во временный файл для просмотра и в сайт не попадает.
    plain = build()
    pw = os.environ.get("ISP_PASS")
    if "--plain" in sys.argv or not pw:
        path = "/tmp/isp_plain.html"; open(path, "w", encoding="utf-8").write(plain)
        print("plain ->", path, "(в сайт не попадает; для публикации задайте ISP_PASS)")
    else:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        open(OUT, "w", encoding="utf-8").write(encrypt(plain, pw))
        print("ok (encrypted)", OUT, os.path.getsize(OUT))
