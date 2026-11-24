#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ставит в пособие карточку урока в каноническом виде (как у 2.2) для лонгридов 2.1, 2.4, 2.5.

Заменяет однострочную карточку, в которой есть href на страницу лонгрида.
Минуты и число слайдов берутся из сборки лонгрида (tools/build-longread.py).
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / 'redev-guide.html'

CARDS = [
    dict(key='2.1', page='redev-read-hbu.html', src='2.1.md', slide_dir='images/slides/hbu', total=40, minutes=54, page_key='hbu',
         title='HBU, сценарии и баланс площадей',
         desc='Тема 2.1 в формате лонгрида: как пройти четыре теста HBU, посчитать NOI по шагам и собрать баланс площадей сценария-победителя. Со слайдами и промптами.'),
    dict(key='2.4', page='redev-read-stress.html', src='2.4.md', slide_dir='images/slides/stress', total=37, minutes=50, page_key='stress',
         title='Стресс-тест финмодели',
         desc='Тема 2.4 в формате лонгрида: красная команда, чувствительность, условия отказа и вопросы юристу. Со слайдами и промптами.'),
    dict(key='2.5', page='redev-read-task3.html', src='2.5.md', slide_dir='images/slides/task3', total=25, minutes=32, page_key='task3',
         title='Сборка задания №3',
         desc='Тема 2.5 в формате лонгрида: как упаковать задание №3 из HBU и расчёта, проверить структуру финмодели и сдать его. Со слайдами и промптами.'),
]


def titles(src):
    raw = (ROOT / 'docs' / 'lectures' / src).read_text(encoding='utf-8')
    return {int(n): t.strip() for n, t in re.findall(r'^### Слайд (\d+) · (.+)$', raw, re.M)}


def card_html(c):
    k = c['key'].replace('.', '')
    t, total, mins, pk = titles(c['src']), c['total'], c['minutes'], c['page_key']
    thumbs = sorted({max(1, round(total * x)) for x in (0, 0.2, 0.45, 0.65, 1)})
    imgs = ''.join(
        f'<img src="{c["slide_dir"]}/{n:02d}-1600.webp" alt="Слайд {n}" loading="lazy">' for n in thumbs)
    titles_js = ','.join('"' + t.get(n, '').replace('"', '\\"') + '"' for n in range(1, total + 1))
    return f'''<div class="lr-preview" id="lrPreview{k}">
  <div class="lr-copy">
    <div class="lr-kicker">Урок · {mins} мин чтения · {total} слайдов</div>
    <h3>{html.escape(c['title'])}</h3>
    <p>{html.escape(c['desc'])}</p>
    <div class="lr-progress-wrap" id="lrProgressWrap{k}" hidden><div class="lr-progress-track"><i id="lrBar{k}"></i></div><span id="lrPercent{k}">Прочитано 0 %</span></div>
    <a class="lr-btn" id="lrLessonBtn{k}" href="{c['page']}">Читать урок →</a>
  </div>
  <div class="lr-ribbon">
    {imgs}
    <div class="lr-ribbon-note"><b>{total}</b><span>слайдов<br>{mins} мин</span></div>
  </div>
</div>
<script>
(function(){{
  const TITLES=[{titles_js}];
  const TOTAL={total};
  const PAGE='{c['page']}';
  const btn=document.getElementById('lrLessonBtn{k}'),wrap=document.getElementById('lrProgressWrap{k}'),bar=document.getElementById('lrBar{k}'),pct=document.getElementById('lrPercent{k}');
  function get(k){{try{{return localStorage.getItem(k)}}catch(e){{return null}}}}
  function update(){{
    let seen=[];try{{seen=JSON.parse(get('lr-{pk}-seen')||'[]')}}catch(e){{}}
    const nums=new Set(seen.map(x=>{{const m=/^slide-(\\d+)$/.exec(x);return m?+m[1]:0}}).filter(Boolean));
    const last=(get('lr-{pk}-last')||'').match(/^slide-(\\d+)$/); const n=last?+last[1]:0;
    if(!n && !nums.size){{wrap.hidden=true;btn.textContent='Читать урок →';btn.href=PAGE;return;}}
    const read=nums.size||n;
    const percent=Math.max(5,Math.min(100,Math.round(read/TOTAL*100)));
    wrap.hidden=false;bar.style.width=percent+'%';pct.textContent='Прочитано '+percent+' %';
    if(n){{btn.textContent='Продолжить: Слайд '+n+' · '+(TITLES[n-1]||'');btn.href=PAGE+'#slide-'+n;}}
    else {{btn.textContent='Продолжить чтение';btn.href=PAGE;}}
  }}
  update();addEventListener('pageshow',update);
}})();
</script>'''


def main():
    g = GUIDE.read_text(encoding='utf-8')
    for c in CARDS:
        lines = g.split('\n')
        idx = [i for i, l in enumerate(lines) if f'href="{c["page"]}"' in l and l.lstrip().startswith('<div style="border:1px solid #0A0F1A')]
        if len(idx) != 1:
            sys.exit(f'{c["key"]}: карточек найдено {len(idx)}')
        lines[idx[0]] = card_html(c)
        g = '\n'.join(lines)
        print(f'{c["key"]}: карточка заменена')
    GUIDE.write_text(g, encoding='utf-8')


if __name__ == '__main__':
    main()
