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
        if s["block"] == 1 and s["date"].startswith("Пт 11"):
            pass
        out.append(
            f'<tr><td class="c-d"><b>{t(s["date"])}</b></td>'
            f'<td class="c-t"><span class="tm">{s["time"]}</span><small>предварительно</small></td>'
            f'<td class="c-f"><span class="fm{" fm-on" if s["fmt"]=="Онлайн" else ""}">{s["fmt"]}</span></td>'
            f'<td class="c-n"><a href="#s{i:02d}">{t(s["title"])}<span class="g"> — {t(s["sub"])}</span></a></td>'
            f'<td class="c-l"><span class="lv {s["lvc"]}">{s["lvl"]}</span></td>'
            f'<td class="c-w">{t(s["lead"])}<small>{t(s["who"])}</small></td></tr>')
        if s["block"] == 1 and s["date"].startswith("Пт 11"):
            out.append('<tr class="r-res"><td colspan="6"><b>14–18 декабря</b> · резерв на переносы</td></tr>')
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
[id]{{ scroll-margin-top:16px; }}
.band{{ position:relative; padding-left:var(--pad); padding-right:var(--pad-r);
  background-image:linear-gradient(to right, var(--grid) 0 1px, transparent 1px), linear-gradient(to bottom, var(--grid) 0 1px, transparent 1px);
  background-size:calc((100% - var(--pad) - var(--pad-r)) / var(--cols)) 100%, 100% var(--row);
  background-position:var(--pad) 0, 0 0; border-bottom:1px solid var(--grid); }}
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
.head-text--2{{ display:none; }}
@media (min-width:900px){{ .brand{{ grid-column:span 2; font-size:40px; }} .head-text--2{{ display:block; grid-column:span 2; }} }}
.marks{{ display:flex; align-items:center; justify-content:space-between; padding-block:14px 26px; }}
.signs{{ display:flex; align-items:center; gap:8px; }}
.signs svg{{ display:block; height:52px; width:auto; }}
.goto{{ display:flex; align-items:center; gap:10px; text-decoration:none; }}
.goto svg{{ width:56px; height:56px; }}
.num-badge{{ display:grid; place-items:center; width:52px; height:52px; border-radius:50%; background:var(--ink); color:var(--paper); font-weight:800; font-size:26px; letter-spacing:-0.04em; }}
.goto-cap{{ font-size:12.5px; font-weight:600; color:var(--muted); max-width:13ch; line-height:1.15; text-align:right; }}
@media (min-width:900px){{ .num-badge{{ width:72px; height:72px; font-size:34px; }} .signs svg{{ height:72px; }} .goto svg{{ width:76px; height:76px; }} }}

/* панель */
.stage{{ position:relative; padding-block:8px 0; overflow:hidden; }}
.panel{{ position:relative; z-index:1; margin-inline:auto; width:min(100%, 760px); background:var(--ink); border-radius:26px; padding:8px; }}
.panel-in{{ background:var(--panel); border-radius:19px; padding:8px; display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:6px; }}
.panel-bar{{ grid-column:1/-1; display:flex; justify-content:space-between; padding:2px 8px; font-size:11px; font-weight:600; }}
.tile{{ position:relative; border-radius:12px; padding:12px; min-height:200px; display:flex; flex-direction:column; justify-content:space-between; text-decoration:none; overflow:hidden; color:var(--ink); }}
.tile h3{{ margin:0; font-size:17px; line-height:1; font-weight:800; letter-spacing:-0.03em; }}
.tile .kick{{ display:block; margin:0 0 4px; font-size:10.5px; font-weight:600; opacity:.75; }}
.tile .big{{ font-size:56px; line-height:.82; font-weight:800; letter-spacing:-0.06em; }}
.tile .unit{{ font-size:11px; font-weight:600; line-height:1.15; text-align:right; }}
.tile .big--s{{ font-size:44px; }}
.tile-foot{{ display:flex; flex-direction:column; align-items:flex-start; gap:8px; }}
.tile .unit{{ text-align:left !important; white-space:nowrap; }}
.tile--blush{{ background:var(--blush); }}
.tile--cobalt{{ background:var(--cobalt); color:var(--on-dark); }}
.index{{ grid-column:1/-1; display:flex; flex-direction:column; gap:3px; }}
.ix{{ display:grid; grid-template-columns:auto minmax(0,1fr) auto; align-items:center; gap:10px; padding:9px 10px; border-radius:9px; text-decoration:none; color:var(--ink); transition:filter .15s; }}
.ix:hover{{ filter:brightness(.95); }}
.ix-n{{ display:grid; place-items:center; width:20px; height:20px; border-radius:50%; background:var(--ink); color:var(--paper); font-size:11px; font-weight:800; }}
.ix-t{{ font-size:19px; line-height:1; font-weight:800; letter-spacing:-0.035em; }}
.ix-s{{ display:block; margin-top:3px; font-size:11px; font-weight:600; letter-spacing:0; opacity:.78; line-height:1.2; }}
.ix-go{{ width:26px; height:26px; }}
.ix--blush{{ background:var(--blush); }} .ix--powder{{ background:var(--powder); }} .ix--sand{{ background:var(--sand); }}
.ix--cobalt{{ background:var(--cobalt); color:var(--on-dark); }}
.ix--midnight{{ background:var(--midnight); color:var(--on-dark); }}
.ix--cobalt .ix-n{{ background:var(--on-dark); color:var(--cobalt); }}
.ix--midnight .ix-n{{ background:var(--blush); color:var(--midnight); }}
@media (min-width:900px){{
  .panel-in{{ grid-template-columns:repeat(4, minmax(0,1fr)); }}
  .tile{{ min-height:250px; padding:14px; }} .tile h3{{ font-size:22px; }} .tile .big{{ font-size:84px; }} .tile .big--s{{ font-size:62px; }}
  .index{{ grid-column:3 / span 2; grid-row:2; }} .ix-t{{ font-size:20px; }}
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
.r-blk td{{ padding:12px 12px; border-bottom:0; }}
.r-blk span{{ display:block; font-size:11px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; opacity:.8; }}
.r-blk b{{ font-size:22px; font-weight:800; letter-spacing:-0.035em; margin-right:10px; }}
.r-blk em{{ font-style:normal; font-size:13px; font-weight:600; white-space:nowrap; display:inline-block; }}
.r-blk.b1 td{{ background:var(--blush); }}
.r-blk.b2 td{{ background:var(--powder); }}
.r-pause td{{ background:var(--sand); padding:12px; font-size:13.5px; }}
.r-res td{{ background:var(--cell); padding:10px 12px; font-size:13.5px; }}
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
  .sch tr.r-blk td, .sch tr.r-pause td, .sch tr.r-res td{{ padding:10px 12px; }}
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
.dark{{ background-color:var(--midnight); color:var(--on-dark); border-bottom:0;
  background-image:linear-gradient(to right, rgba(246,244,240,.10) 0 1px, transparent 1px), linear-gradient(to bottom, rgba(246,244,240,.10) 0 1px, transparent 1px); }}
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
.blk-head.b1{{ background-color:var(--blush); }}
.blk-head.b2{{ background-color:var(--powder); }}
@media (min-width:900px){{ .blk-head .bh-k{{ grid-column:span 2; padding-top:8px; }} .blk-head .bh-t{{ grid-column:3 / span 6; }} }}

/* пауза */
.pause{{ background-color:var(--sand); }}
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
  .marks, .stage, .word-wrap, .btn{{ display:none !important; }}
  .ses, .box, .pr, .tasks li{{ break-inside:avoid; }}
  .dark{{ background:#fff !important; color:var(--ink) !important; }}
  .dark .results li{{ color:var(--ink); }} .dk-title .g{{ color:var(--gray); }}
  body{{ font-size:12px; }}
}}
</style>
</head>
<body>

<header class="band head">
  <div class="grid">
    <h1 class="display brand">ИСП × AI2ARCH <span class="g">Методическое пособие для&nbsp;сотрудников</span></h1>
    <p class="small head-text">Корпоративное обучение ИИ для&nbsp;проектного бюро ИСП: расписание и&nbsp;описание каждого занятия под&nbsp;задачи бюро.</p>
    <nav class="head-menu" aria-label="Разделы">
      <a class="bullet" href="#schedule">Расписание</a>
      <a class="bullet" href="#block1">Занятия</a>
      <a class="bullet" href="#prep">Подготовка рабочих мест</a>
      <a class="bullet" href="#rules">Правила работы с&nbsp;данными</a>
    </nav>
    <p class="small head-text head-text--2"><b>Даты и&nbsp;время предварительные на&nbsp;{t(AS_OF)}&nbsp;г.</b> Время московское. Час занятия&nbsp;— астрономический, 60&nbsp;минут.</p>
  </div>
  <div class="marks">
    <div class="signs" aria-hidden="true">
      <svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="31" fill="#0A0F1A"/><path d="M32 9 L45 45 L32 37 L19 45 Z" fill="#F6F4F0"/><path d="M32 9 L32 37 L19 45 Z" fill="#0A0F1A" stroke="#F6F4F0" stroke-width="2.5" stroke-linejoin="round"/><text x="32" y="58" text-anchor="middle" font-family="Inter Tight, Arial, sans-serif" font-weight="800" font-size="10" fill="#F6F4F0">С</text></svg>
      <svg viewBox="0 0 92 64"><path d="M60 14 L90 32 L60 50 Z" fill="#0A0F1A"/><circle cx="32" cy="32" r="28.5" fill="#F6F4F0" stroke="#0A0F1A" stroke-width="5"/><path d="M4 32 H60" stroke="#0A0F1A" stroke-width="4"/><text x="32" y="26" text-anchor="middle" font-family="Inter Tight, Arial, sans-serif" font-weight="800" font-size="17" fill="#0A0F1A">2</text><text x="32" y="50" text-anchor="middle" font-family="Inter Tight, Arial, sans-serif" font-weight="700" font-size="12" fill="#0A0F1A">ИСП</text></svg>
    </div>
    <a class="goto" href="#schedule" aria-label="К расписанию: {n_ses} занятий">
      <span class="goto-cap">Занятий в&nbsp;программе, старт 4&nbsp;декабря</span>
      <svg viewBox="0 0 64 64" aria-hidden="true"><path d="M14 50 L46 18 M22 16 H48 V42" fill="none" stroke="#0A0F1A" stroke-width="9" stroke-linecap="square"/></svg>
      <span class="num-badge" aria-hidden="true">{n_ses}</span>
    </a>
  </div>
</header>

<section class="band stage" aria-label="Два блока обучения">
  <div class="panel">
    <div class="panel-in">
      <div class="panel-bar"><span>ИСП × AI2ARCH</span><span>Ростов-на-Дону · очно в&nbsp;бюро</span></div>
      <a class="tile tile--blush" href="#block1">
        <div><span class="kick">Блок 1 · {t(BLOCKS[1]["when"])}</span><h3>{t(BLOCKS[1]["name"])}</h3></div>
        <div class="tile-foot"><span class="big">{BLOCKS[1]["hours"]}</span><span class="unit">ч очно · {t(BLOCKS[1]["range"])}</span></div>
      </a>
      <a class="tile tile--cobalt" href="#block2">
        <div><span class="kick">Блок 2 · {t(BLOCKS[2]["when"])}</span><h3>{t(BLOCKS[2]["name"])}</h3></div>
        <div class="tile-foot"><span class="big big--s">{BLOCKS[2]["hours"]}</span><span class="unit">ч очно · {t(BLOCKS[2]["range"])}</span></div>
      </a>
      <nav class="index" aria-label="Содержание">
        <a class="ix ix--blush" href="#schedule"><span class="ix-n">1</span><span class="ix-t">Расписание<span class="ix-s">{n_ses} занятий, даты и&nbsp;время</span></span>{GO}</a>
        <a class="ix ix--cobalt" href="#how"><span class="ix-n">2</span><span class="ix-t">Как устроено<span class="ix-s">Формат, глубина, ведущие</span></span>{GO}</a>
        <a class="ix ix--midnight" href="#prep"><span class="ix-n">3</span><span class="ix-t">Рабочие места<span class="ix-s">Что установить и&nbsp;к&nbsp;какой дате</span></span>{GO}</a>
        <a class="ix ix--powder" href="#rules"><span class="ix-n">4</span><span class="ix-t">Правила данных<span class="ix-s">Что можно загружать в&nbsp;ИИ</span></span>{GO}</a>
        <a class="ix ix--sand" href="#pause"><span class="ix-n">5</span><span class="ix-t">Между блоками<span class="ix-s">Задание на&nbsp;паузу</span></span>{GO}</a>
      </nav>
    </div>
  </div>
  <div class="word-wrap"><p class="word" aria-hidden="true">ИСП×AI2ARCH</p></div>
</section>

<section aria-labelledby="tasks-h">
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
</footer>

<script>
/* Марка растягивается ровно на ширину полосы */
(function(){{
  var w=document.querySelector('.word'); if(!w) return;
  function fit(){{ w.style.fontSize='100px'; var box=w.parentNode.clientWidth; var k=box/w.scrollWidth; w.style.fontSize=(100*k)+'px'; }}
  fit(); window.addEventListener('resize', fit);
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(fit);
}})();
</script>
</body>
</html>
'''

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(build())
    print("ok", OUT, os.path.getsize(OUT))
