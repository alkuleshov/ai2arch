#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Одноразово: templates/longread.html -> templates/longread-isp.html (каркас ISP, скрипты и контент прежние)."""
import re
from pathlib import Path
R = Path(__file__).resolve().parent.parent
t = (R / 'templates' / 'longread.html').read_text(encoding='utf-8')

# 1. шрифты и подключение общей оболочки
t = t.replace("@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');",
              "@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');")
t = t.replace('<style>', '<link rel="stylesheet" href="isp-shell.css">\n<style>', 1)

# 2. старые стили шапки/оглавления/героя больше не нужны — вырезаем
def cut(pattern):
    global t
    t, n = re.subn(pattern, '', t, flags=re.M)
    return n
for pat in [r'^\.lr-head[^\n]*\n', r'^\.lr-back[^\n]*\n', r'^\.lr-name[^\n]*\n',
            r'^\.hero[^\n]*\n', r'^\.start[^\n]*\n', r'^\.glossary[^\n]*\n',
            r'^\.lr-toc[^\n]*\n', r'^\.toc-[^\n]*\n', r'^\.lr-terms[^\n]*\n',
            r'^\.lr-main[^\n]*\n']:
    cut(pat)
t = re.sub(r'@media\(max-width:440px\)\{\.lr-head[^\n]*\n', '', t)

# 3. разметка: шапка, оглавление и «главное» заменяются каркасом ISP
head_start = t.index('<body class="fs-2">')
main_end = t.index('</main>') + len('</main>')
shell = '''<body class="fs-2">
<div class="lr-progress" id="lrProgress"></div>
<div class="i-app lr-app" id="iApp">
<aside class="i-side" id="iSide">
  <div class="sd-top"><a class="sd-brand" href="index.html"><span class="sd-logo"><img src="images/ai2arch-sign.png" alt="" width="26" height="26"></span><span class="sd-bt"><b>AI2ARCH</b><small>{{COURSE_SUB}}</small></span></a></div>
  <div class="sd-course">{{COURSE_SWITCH}}</div>
  <header class="lr-head" id="lrHead">
    <a class="lr-back" href="{{BACK_HREF}}">{{BACK_LABEL}}</a>
    <button id="termsBtn" type="button">Термины</button>
    <button id="tocBtn" type="button">Содержание</button>
    <button id="fontBtn" type="button" aria-label="Размер шрифта">Aa</button>
    <select id="slideMode" aria-label="Положение слайдов">
      <option value="side">Слайды сбоку</option>
      <option value="top">Над текстом</option>
      <option value="hide">Скрыть слайды</option>
    </select>
  </header>
  <nav class="sd-nav lr-toc" id="lrToc" aria-label="Содержание урока">
    <div class="toc-top"><b>Содержание</b><button id="tocClose" type="button" aria-label="Закрыть">×</button></div>
    <a class="toc-home" href="{{BACK_HREF}}"><span>←</span><b>{{BACK_LABEL_PLAIN}}</b></a>
    <a href="redev-schedule.html"><span>·</span><b>Расписание</b></a>
    <a href="redev-glossary.html"><span>·</span><b>Словарь терминов</b></a>
    <div class="sd-gap"></div>
    {{TOC}}
  </nav>
  <a class="sd-tg" href="https://t.me/alkuleshov" target="_blank" rel="noopener">Вопросы: @alkuleshov</a>
</aside>
<aside class="lr-terms" id="lrTerms" aria-label="Термины урока">
  <div class="toc-top"><b>Термины урока</b><button id="termsClose" type="button" aria-label="Закрыть">×</button></div>
  <dl>{{TERMS}}</dl>
</aside>
<div class="i-main" id="iMain">
  <div class="i-cover"><header class="i-band i-head"><div class="i-grid"><div class="i-display i-brand">AI2<span class="g">ARCH</span></div>
  <div class="i-head-text"><p class="i-small"><b>{{KICKER}}</b><br>ААИ ЮФУ · Ростов-на-Дону</p><div class="i-course">{{COURSE_SWITCH}}</div></div></div></header>
  <section class="i-band i-title-band" id="top"><h1 class="i-display i-h1">{{HERO_H1}}</h1>
    <p class="i-lead">{{INTRO}}</p>
    <div class="lr-meta"><span>{{TOTAL}} слайдов</span><span>{{READ_TIME}} мин чтения</span><span>{{WORDS}} слов</span></div>
    <a class="i-down" href="#chapter-1">Вниз ↓</a></section></div>
  <div class="lr-main"><div class="lr-body" id="lrBody">
    <div class="lr-text">{{BODY}}</div>
    <aside class="rail" id="rail" aria-label="Слайды урока">
      <div class="rail-frame">{{RAIL}}<button class="expand-btn" id="railExpand" type="button">⤢ Развернуть</button></div>
      <div class="rail-caption" id="railCaption">Слайд 1 из {{TOTAL}}</div>
    </aside>
  </div></div>
  <footer class="i-band i-foot i-grid"><div class="i-foot-a"><p>AI2ARCH · 2026</p><p class="i-small" style="margin-top:4px">Лаборатория проектного интеллекта</p></div>
  <div class="i-foot-b"><p>Курс дополнительного образования</p><p>ААИ ЮФУ · Ростов-на-Дону</p></div>
  <div class="i-foot-c"><p>Остались вопросы?</p><a class="i-btn" href="https://t.me/alkuleshov" target="_blank" rel="noopener">Написать в Telegram →</a></div></footer>
</div></div>'''
t = t[:head_start] + shell + t[main_end:]

# 4. скрипты: порог «слайды сбоку» с учётом левого меню, акк��рдеон глав в меню
t = t.replace("innerWidth<1280", "innerWidth<1600")
t = t.replace("const body=document.body, head=document.getElementById('lrHead');",
              "const body=document.body, head=document.getElementById('lrHead');\nconst isDesk=()=>innerWidth>=1100;")
t = t.replace("if(innerWidth<=720){", "if(innerWidth<=1099){")
t = t.replace("function setCurrent(id,n){\n  currentN=+n;",
 "function setCurrent(id,n){\n  currentN=+n; markChapter(id);")
t = t.replace("// текущий раздел и липкий слайд",
"""// меню: раскрыта только текущая глава
function markChapter(id){
  const sec=document.getElementById(id); const ch=sec&&sec.closest('.chapter'); if(!ch)return;
  let on=false;
  document.querySelectorAll('#lrToc a.toc-ch,#lrToc a.toc-slide').forEach(a=>{
    if(a.classList.contains('toc-ch')){on=a.getAttribute('href')==='#'+ch.id;a.classList.toggle('is-cur-ch',on);}
    else a.classList.toggle('on-ch',on);
  });
}
// текущий раздел и липкий слайд""")

# 5. оформление: стиль ISP поверх общих стилей контента
ISP = r'''
/* ═══ ISP: переопределения под швейцарскую сетку ═══ */
:root{--navy:#0A0F1A;--ink:#0A0F1A;--muted:#5A6070;--faint:#848A9A;--bg:#F6F4F0;--line:#E1DDD5;--accent:#1A82FF;--accent-l:#EAF2FF;--accent-b:#BED0EE;--orange:#B4601A;--orange-l:#F6EEDC;--orange-b:#E6D9BE;--sans:'Inter Tight','Helvetica Neue',Arial,sans-serif;--head:0px}
body{font-family:var(--sans)}
body.fs-1{--fs:16px} body.fs-2{--fs:17.5px} body.fs-3{--fs:19.5px}
.lr-progress{position:fixed;top:0;left:0;height:3px;background:var(--i-ink);width:0;z-index:70}
.lr-app .i-cover .i-h1{font-size:clamp(38px,8vw,88px)}
.lr-meta{display:flex;gap:16px;flex-wrap:wrap;margin-top:16px;font-size:13px;font-weight:600;color:var(--i-muted)}
.lr-main{padding:0 var(--i-pad) 70px;max-width:none}
.lr-body{max-width:1000px;margin:0 auto;padding-top:40px}
.chapter{margin:0 0 60px;scroll-margin-top:12px}
.chapter-head{padding-top:30px;border-top:1.5px solid var(--i-ink);margin-bottom:22px}
.chapter-kicker{font-size:12px;font-weight:700;letter-spacing:.02em;text-transform:none;color:var(--i-gray)}
.chapter h1{font-size:clamp(34px,5.4vw,60px);font-weight:800;letter-spacing:-.045em;line-height:.95;color:var(--i-ink)}
.slide-sec{border-top:1px solid var(--i-grid);padding:30px 0 34px}
.slide-sec h2{font-weight:800;letter-spacing:-.035em;line-height:1.02;font-size:clamp(26px,3.6vw,38px)}
.sec-kicker{font-size:11.5px;font-weight:700;letter-spacing:0;text-transform:none;color:var(--i-gray)}
.example-card,.chapter-brief,.fold,.prompt-block,.task-card,.chapter-end,.quiz,.trainer,.gaps-block,.finish-card,.lesson-end,.roles-card,.c52-card,.verdict{border-radius:0}
.slide-inline img{border-radius:0}
.verdict{border-left:3px solid var(--i-ink);background:#fff}
.verdict-mark,.chapter-brief .brief-head>span:first-child{color:var(--i-ink)}
.chapter-brief a b{background:var(--i-ink);color:#F6F4F0;border-radius:0}
.start,.finish-btn-dark,.trainer-actions button,#trainerRestart{border-radius:999px}
.copy{border-radius:999px}
.lr-app .lr-head{position:static;display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 0;padding:0;background:none;border:0;backdrop-filter:none;height:auto;transform:none}
.lr-app .lr-head .lr-back{flex:1 0 100%;font-size:12.5px;display:none}
.lr-app .lr-head button,.lr-app .lr-head select{font:700 12px var(--sans);border:1.5px solid var(--i-ink);background:transparent;color:var(--i-ink);border-radius:999px;padding:6px 11px;cursor:pointer}
.lr-app .lr-head button:hover,.lr-app .lr-head select:hover{background:rgba(10,15,26,.06);color:var(--i-ink);border-color:var(--i-ink)}
.lr-app .lr-head #tocBtn{display:none}
.lr-app .lr-head select{flex:1 1 100%;margin-top:0}
/* панель терминов */
.lr-terms{position:fixed;top:0;right:0;bottom:0;width:min(420px,92vw);z-index:120;background:#F6F4F0;border-left:1.5px solid var(--i-ink);box-shadow:none;transform:translateX(102%);transition:transform .22s ease;overflow-y:auto;padding:18px 18px 40px}
.lr-terms.open{transform:none;box-shadow:-20px 0 50px rgba(10,15,26,.12)}
.lr-terms .toc-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.lr-terms .toc-top b{font-size:16px;font-weight:800;letter-spacing:-.02em}
.lr-terms .toc-top button{border:0;background:transparent;font-size:26px;cursor:pointer;color:var(--i-muted)}
.lr-terms dl{display:grid;gap:14px;margin:0}
.lr-terms dt{font-weight:800;font-size:14px;color:var(--i-ink)}
.lr-terms dd{font-size:13px;line-height:1.45;color:var(--i-muted);margin:2px 0 0}
/* меню: главы и слайды */
.lr-app .lr-toc{position:static;transform:none;width:auto;overflow:visible;padding:0;border:0;box-shadow:none;background:none;margin-top:10px;display:flex;flex-direction:column}
.lr-toc .toc-top{display:none}
.lr-toc a.toc-slide{display:none;padding-left:8px!important;color:var(--i-ink)!important;font-weight:600;font-size:13px}
.lr-toc a.toc-slide.on-ch{display:grid}
.lr-toc a.toc-slide.current{background:var(--i-ink);color:#F6F4F0!important}
.lr-toc a.toc-slide.current span{color:rgba(246,244,240,.7)}
.lr-toc a.toc-slide.read:after{content:'';}
.lr-toc a.toc-ch{display:grid;grid-template-columns:34px minmax(0,1fr) auto;margin-top:12px;padding:9px 8px 6px;border-top:1.5px solid var(--i-ink);border-radius:0;font-size:14px;font-weight:800;letter-spacing:-.025em;text-transform:none;color:var(--i-ink)!important}
.lr-toc a.toc-ch:first-of-type{margin-top:4px}
.lr-toc a.toc-ch.is-cur-ch{background:rgba(10,15,26,.05)}
.lr-toc a.toc-ch>span{font-size:11px;font-weight:600;color:var(--i-gray)}
.lr-toc a.toc-home{font-weight:700}
.toc-quiz{display:none}
.toc-ch.passed .toc-quiz{display:inline;font-size:10px;font-weight:600;color:#16724F;white-space:nowrap}
@media(min-width:1100px){
  .lr-app{display:grid;grid-template-columns:288px minmax(0,1fr)}
  .lr-app .lr-terms{z-index:120}
  .lr-app .lr-toc{flex:0 1 auto}
}
/* телефон и планшет: тулбар сверху, содержание — выезжающая панель */
@media(max-width:1099px){
  :root{--head:54px}
  .lr-app .i-side{display:contents}
  .lr-app .sd-top,.lr-app .sd-course,.lr-app .sd-tg{display:none}
  .lr-app .lr-head{position:sticky;top:0;z-index:60;height:54px;flex-wrap:nowrap;margin:0;padding:0 var(--i-pad);align-items:center;background:#F6F4F0;border-bottom:1.5px solid var(--i-ink);gap:6px;order:-1}
  .lr-app .lr-head .lr-back{display:block;flex:1 1 auto;min-width:0;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--i-ink)}
  .lr-app .lr-head #tocBtn{display:inline-block}
  .lr-app .lr-head select{flex:0 0 auto;margin:0;width:72px;text-overflow:ellipsis}
  .lr-app .lr-head.hide{transform:translateY(-105%)}
  .lr-app .lr-toc{position:fixed;top:0;right:0;bottom:0;width:min(420px,92vw);z-index:100;background:#F6F4F0;border-left:1.5px solid var(--i-ink);box-shadow:none;transform:translateX(102%);transition:transform .22s ease;overflow-y:auto;padding:16px 18px 40px;margin:0}
  .lr-app .lr-toc.open{transform:none;box-shadow:-20px 0 50px rgba(10,15,26,.12)}
  .lr-toc .toc-top{display:flex}
  .lr-toc a.toc-slide{display:grid}
  .lr-terms{background:#F6F4F0}
  .lr-app .i-cover{min-height:calc(100svh - 54px)}
}
/* всё по левому краю, как в ISP */
.lr-body{margin:0;max-width:1000px}
.lr-text{margin:0}
.chapter-head,.lesson-intro,.example-card,.chapter-brief,.sec-kicker,.slide-sec h2,.prose,.verdict,.prompt-block,.c52-card,.fold,.task-card,.transition,.chapter-end,.lesson-end,.finish-card,.trainer,.gaps-block,.quiz,.slide-inline{margin-left:0!important;margin-right:auto!important}
.lr-app .lr-toc:not(.open){box-shadow:none}
@media(max-width:560px){
  .lr-app .lr-head .lr-back{font-size:0;flex:0 0 auto}
  .lr-app .lr-head .lr-back:before{content:'←';font-size:20px;line-height:1}
  .lr-app .lr-head button,.lr-app .lr-head select{padding:6px 9px;font-size:11.5px}
  .lr-app .lr-head select{width:56px}
}
@media(min-width:1600px){
  .mode-side .lr-body{max-width:none;display:grid;grid-template-columns:minmax(600px,680px) minmax(0,1fr);gap:40px;align-items:start}
  .mode-side .lr-text{max-width:none}
  .mode-side .slide-inline{display:none}
  .mode-side .rail{display:block;position:sticky;top:16px;width:min(100%,1000px,calc((100vh - 32px)*16/9));max-height:calc(100vh - 32px);align-self:start}
  .mode-side .rail-frame{position:relative;width:100%;aspect-ratio:16/9;overflow:hidden;border:1px solid var(--line);border-radius:0;background:#fff}
  .mode-side .rail img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;opacity:0;transition:opacity .25s;background:#fff;pointer-events:none}
  .mode-side .rail img.active{opacity:1;pointer-events:auto;cursor:zoom-in}
  .mode-side .rail .expand-btn{top:8px;right:8px}
  .rail-caption{font-size:11px;color:var(--faint);margin-top:6px;text-align:center}
}
@media(min-width:1280px) and (max-width:1599px){
  .mode-side .rail{display:none}
  .mode-side .slide-inline{display:block}
}
'''
# 6. убираем прежние правила «сбоку» с порогом 1280 (теперь 1600), добавляем ISP
t = re.sub(r'@media\(min-width:1280px\)\{.*?\n\}\n', '', t, flags=re.S, count=1)
t = t.replace('</style>', ISP + '</style>', 1)
(R / 'templates' / 'longread-isp.html').write_text(t, encoding='utf-8')
print('ok', len(t))
