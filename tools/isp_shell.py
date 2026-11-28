"""Общая оболочка страниц пособия в стиле ISP: левое меню (бренд, страницы, содержание страницы),
верхняя панель на телефоне, шапка и подвал. Стили — isp-shell.css в корне сайта."""
import html

esc = html.escape
NOTION = 'https://fortune-swing-02e.notion.site/41112bb3b5cd81839661da69963a035b?source=copy_link'
PAGES = [('guide', 'redev-guide.html', 'Пособие'), ('schedule', 'redev-schedule.html', 'Расписание'),
         ('glossary', 'redev-glossary.html', 'Словарь терминов')]

JS = r'''<script>
(function(){
  var side=document.getElementById('iSide');
  var links=Array.prototype.slice.call(side.querySelectorAll('.sd-nav a[data-s]'));
  var map={}; links.forEach(function(a){ map[a.getAttribute('data-s')]=a; });
  function offs(){ var t=document.querySelector('.i-topbar'); return (t && t.offsetParent!==null ? t.offsetHeight : 0)+12; }
  function jumpTo(id){ var el=document.getElementById(id); if(!el) return; window.scrollTo({top:el.getBoundingClientRect().top+window.pageYOffset-offs()+6,behavior:'smooth'}); }
  var selS=document.getElementById('iSelL'), selP=document.getElementById('iSelM');
  if(selP) selP.addEventListener('change',function(){ if(selP.value) location.href=selP.value; });
  if(selS) selS.addEventListener('change',function(){ jumpTo(selS.value); });
  var ticking=false;
  function spy(){ ticking=false; var y=window.innerHeight*0.28, c=null;
    links.forEach(function(a){ var t=document.getElementById(a.getAttribute('data-s')); if(t && t.getBoundingClientRect().top<=y) c=a; });
    links.forEach(function(a){ a.classList.toggle('is-on', a===c); });
    if(c){ if(selS) selS.value=c.getAttribute('data-s');
      var sr=side.getBoundingClientRect(), ar=c.getBoundingClientRect(); if(ar.top<sr.top+40||ar.bottom>sr.bottom-30) side.scrollTop+=ar.top-sr.top-sr.height/3; } }
  window.addEventListener('scroll',function(){ if(!ticking){ ticking=true; requestAnimationFrame(spy);} },{passive:true});
  window.addEventListener('resize',spy);
  links.forEach(function(a){ a.addEventListener('click',function(e){ var id=a.getAttribute('data-s'); e.preventDefault(); history.replaceState(null,'','#'+id); jumpTo(id); }); });
  document.addEventListener('DOMContentLoaded',function(){ spy(); if(location.hash.length>1){ setTimeout(function(){ jumpTo(decodeURIComponent(location.hash.slice(1))); },80); } });
})();
</script>'''


def page(key, title, desc, sub, sections, main_html, head_extra='', script=''):
    """key — guide|schedule|glossary; sections — [(id, номер, название, справа)] для меню этой страницы."""
    nav = []
    for k, href, name in PAGES:
        cls = ' class="is-cur"' if k == key else ''
        nav.append(f'<a{cls} href="{href}"><span>·</span><b>{esc(name)}</b></a>')
    nav.append(f'<a href="{NOTION}" target="_blank" rel="noopener"><span>↗</span><b>Рабочая тетрадь</b></a>')
    nav.append('<div class="sd-gap"></div>')
    for sid, num, name, right in sections:
        em = f'<em>{esc(right)}</em>' if right else ''
        nav.append(f'<a href="#{sid}" data-s="{sid}"><span>{esc(num)}</span><b>{esc(name)}</b>{em}</a>')
    opts_p = ''.join(f'<option value="{h}"{" selected" if k == key else ""}>{esc(n)}</option>' for k, h, n in PAGES)
    opts_s = ''.join(f'<option value="{sid}">{esc(name)}</option>' for sid, num, name, right in sections)
    tb_end = main_html.index('</section>') + len('</section>')
    cover = main_html[:tb_end].replace('</section>', f'<a class="i-down" href="#{sections[0][0]}">Вниз ↓</a></section>')
    rest = main_html[tb_end:]
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700;800;900&display=swap">
<link rel="stylesheet" href="isp-shell.css">
<style>*{{margin:0;padding:0;box-sizing:border-box}}html{{background:#F6F4F0}}body{{background:#F6F4F0;font-family:'Inter Tight','Helvetica Neue',Arial,sans-serif;color:#0A0F1A}}a{{color:inherit}}{head_extra}</style>
</head>
<body>
<div class="i-app" id="iApp">
<div class="i-topbar"><select class="i-sel" id="iSelM" aria-label="Страница">{opts_p}</select><select class="i-sel" id="iSelL" aria-label="Раздел">{opts_s}</select></div>
<aside class="i-side" id="iSide"><div class="sd-top"><a class="sd-brand" href="index.html"><span class="sd-logo"><img src="images/ai2arch-sign.png" alt="" width="26" height="26"></span><span class="sd-bt"><b>AI2ARCH</b><small>{esc(sub)}</small></span></a></div>
<div class="sd-course"><a class="on" href="redev-guide.html">Редевелопмент</a><a href="archi-guide.html">Архитектура</a></div>
<nav class="sd-nav" id="sdNav">{''.join(nav)}</nav><a class="sd-tg" href="https://t.me/alkuleshov" target="_blank" rel="noopener">Вопросы: @alkuleshov</a></aside>
<div class="i-main" id="iMain">
<div class="i-cover"><header class="i-band i-head"><div class="i-grid"><div class="i-display i-brand">AI2<span class="g">ARCH</span></div>
<div class="i-head-text"><p class="i-small"><b>Курс дополнительного образования</b><br>ААИ ЮФУ · Ростов-на-Дону</p><div class="i-course"><a class="on" href="redev-guide.html">Редевелопмент</a><a href="archi-guide.html">Архитектура</a></div></div></div></header>
{cover}</div>
{rest}
<footer class="i-band i-foot i-grid"><div class="i-foot-a"><p>AI2ARCH · 2026</p><p class="i-small" style="margin-top:4px">Лаборатория проектного интеллекта</p></div>
<div class="i-foot-b"><p>Курс дополнительного образования</p><p>ААИ ЮФУ · Ростов-на-Дону</p></div>
<div class="i-foot-c"><p>Остались вопросы?</p><a class="i-btn" href="https://t.me/alkuleshov" target="_blank" rel="noopener">Написать в Telegram →</a></div></footer>
</div></div>
{JS}
{script}
</body>
</html>
'''
