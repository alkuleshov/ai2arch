#!/usr/bin/env python3
"""Расписание потока в стиле ISP: tools/schedule-rows.json → redev-schedule.html.
Строки расписания правятся в JSON (поле cells: дата, время, тема, лектор), затем: python3 tools/build-schedule.py"""
import json, re, sys, pathlib
from bs4 import BeautifulSoup
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from isp_shell import page, esc

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / 'tools' / 'schedule-rows.json', encoding='utf-8'))

def text(h):
    return re.sub(r'\s+', ' ', BeautifulSoup(h, 'html.parser').get_text(' ')).strip()

def row(r):
    date, time, topic, who = r['cells']
    cls = ['i-sr'] + [c for c in r['cls'] if c in ('day-start', 'self-row')]
    cls = [('self' if c == 'self-row' else c) for c in cls]
    t = BeautifulSoup(topic, 'html.parser')
    badge = t.select_one('.meet-badge'); b = badge.get_text(strip=True) if badge else ''
    kind = ' '.join(badge.get('class', [])) if badge else ''
    bt = 'b1' if 'meeting' in kind else ('b3' if 'self' in kind else 'b2')
    main = t.select_one('.slot-main'); mh = main.decode_contents() if main else topic
    dtxt = text(date)
    empty = 'date-empty' in r.get('dcls', [])
    d = f'<span class="d{" e" if empty or not dtxt else ""}">{esc(dtxt) if dtxt else "—"}</span>'
    w = esc(re.sub(r'\s+', ' ', text(who)))
    return (f'<li class="{" ".join(cls)}">{d}<span class="t">{esc(text(time))}</span>'
            f'<span class="n"><span class="i-bt {bt}">{esc(b)}</span>{mh}</span><span class="w">{w}</span></li>')

groups = []; cur = None
for r in D['rows']:
    if r['k'] == 'module':
        m = BeautifulSoup(r['html'], 'html.parser')
        title = m.select_one('.mod-title'); note = m.select_one('.mod-sub')
        note_t = note.get_text(strip=True) if note else ''
        name = title.get_text(strip=True); dates = m.select_one('.mod-dates').get_text(strip=True)
        cur = {'name': name, 'note': note_t, 'dates': dates, 'items': []}; groups.append(cur)
    elif r['k'] == 'pause':
        cur['items'].append(('pause', r['t']))
    else:
        cur['items'].append(('slot', r))

sections = [('s-cal', '—', 'Календарь потока', '')]
bands = []
for n, g in enumerate(groups):
    sid = f's-m{n}'
    kick, _, rest = g['name'].partition(' · ')
    title = rest or g['name']
    if g['note']: title_full = f'{title} ({g["note"]})'
    else: title_full = title
    num = 'М0' if kick.startswith('Вводный') else ('М' + kick.split()[-1] if kick.startswith('Модуль') else '·')
    sections.append((sid, num, title_full, g['dates']))
    kicker = f'{kick}' + (f' · {g["note"]}' if g['note'] else '')
    bands.append(f'<section class="i-band i-blk i-grid" id="{sid}"><div class="i-bh-k"><b>{esc(kicker)}</b><span>{esc(g["dates"])}</span></div>'
                 f'<h2 class="i-display i-bh-t">{esc(title)}</h2></section>')
    body = []
    for kind, v in g['items']:
        if kind == 'pause':
            if body: bands.append('<div class="i-band i-wrap"><ul class="i-sch">' + ''.join(body) + '</ul></div>'); body = []
            bands.append(f'<div class="i-band i-wrap"><p class="i-pause">{esc(v)}</p></div>')
        else:
            body.append(row(v))
    if body: bands.append('<div class="i-band i-wrap"><ul class="i-sch">' + ''.join(body) + '</ul></div>')

cal = D['cal'].replace('section-end-btn primary', 'i-btn')
main = f'''<section class="i-band i-title-band"><h1 class="i-display i-h1">Расписание<span class="g">потока</span></h1><p class="i-lead">{D["lead"]}</p></section>
<section class="i-band i-wrap i-cal" id="s-cal">{cal}</section>
{''.join(bands)}
<div class="i-band i-wrap"><p class="i-small">{esc(D["end"][0])}</p></div>'''

script = '''<script>
(function () {
  var copy = document.getElementById('calCopy');
  if (!copy) return;
  copy.addEventListener('click', function (event) {
    if (!navigator.clipboard) return;
    event.preventDefault();
    navigator.clipboard.writeText(copy.href).then(function () {
      copy.textContent = 'Адрес скопирован';
      setTimeout(function () { copy.textContent = 'Скопировать адрес'; }, 2500);
    }).catch(function () { window.location.href = copy.href; });
  });
})();
</script>'''
html_out = page('schedule', 'Расписание потока · ИИ в редевелопменте · AI2ARCH',
                'Расписание встреч, лекций и самостоятельной работы потока курса «ИИ в редевелопменте».',
                'ИИ в редевелопменте', sections, main, script=script)
(ROOT / 'redev-schedule.html').write_text(html_out, encoding='utf-8')
print('ok', len(groups), 'групп', sum(len(g['items']) for g in groups), 'строк')
