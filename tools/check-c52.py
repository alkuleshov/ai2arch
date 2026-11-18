#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сверка чисел C52 на слайдах с docs/c52-facts.md.

Ищет в redev-*.html (кроме расписания и пособия), docs/lectures/*.md
и docs/conspekty/*.md кадастровые номера, площадь и ставки C52
и сообщает о расхождениях.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP = {'redev-schedule.html', 'redev-guide.html'}
CANON_KN = '61:44:0040713:43'
CANON_AREA = 1959.2
ALLOWED_RATES = {650, 723, 911}
TEXTBOOK_RATES = {1000}  # только рядом с пометкой «учебный пример»

problems = []
checked = 0


def norm_area(raw):
    return float(raw.replace(' ', '').replace(' ', '').replace(',', '.'))


for path in sorted(glob.glob(os.path.join(ROOT, 'redev-*.html'))):
    name = os.path.basename(path)
    if name in SKIP:
        continue
    text = open(path, encoding='utf-8').read()
    checked += 1

    for m in re.finditer(r'61:\d{2}:\d{7}:\d+', text):
        if m.group(0) != CANON_KN:
            problems.append(f'{name}: кадастровый номер {m.group(0)} вместо {CANON_KN}')

    for m in re.finditer(r'(?<!\d)(1\s?959(?:[.,]\d+)?)(?!\d)', text):
        val = norm_area(m.group(1))
        if abs(val - CANON_AREA) > 0.001:
            problems.append(f'{name}: площадь {m.group(1)} вместо 1 959,2')

    for m in re.finditer(r'(?i)(упёрл|уперл|тупик)', text):
        line = text[:m.start()].count('\n') + 1
        problems.append(f'{name}:{line}: запрещённая формулировка «{m.group(0)}»')

    for m in re.finditer(r'(?<![\d\s])(\d{3,4})\s*₽/м²', text):
        val = int(m.group(1))
        if val in ALLOWED_RATES:
            continue
        start = max(0, m.start() - 400)
        ctx = text[start:m.end() + 400].lower()
        if val in TEXTBOOK_RATES and 'учебный пример' in ctx:
            continue
        problems.append(f'{name}: ставка {val} ₽/м² не из проверенных данных C52')

for pattern in ('conspekty', 'lectures'):
    for path in sorted(glob.glob(os.path.join(ROOT, 'docs', pattern, '*.md'))):
        name = os.path.relpath(path, ROOT)
        text = open(path, encoding='utf-8').read()
        checked += 1

        for m in re.finditer(r'61:\d{2}:\d{7}:\d+', text):
            if m.group(0) != CANON_KN:
                problems.append(f'{name}: кадастровый номер {m.group(0)} вместо {CANON_KN}')

        for m in re.finditer(r'(?<!\d)(1\s?959(?:[.,]\d+)?)(?!\d)', text):
            val = norm_area(m.group(1))
            if abs(val - CANON_AREA) > 0.001:
                problems.append(f'{name}: площадь {m.group(1)} вместо 1 959,2')

        for m in re.finditer(r'(?i)(упёрл|уперл|тупик)', text):
            line = text[:m.start()].count('\n') + 1
            problems.append(f'{name}:{line}: запрещённая формулировка «{m.group(0)}»')

if problems:
    print('Расхождения с docs/c52-facts.md:')
    for p in problems:
        print(' -', p)
    sys.exit(1)

print(f'Проверено файлов: {checked}. Расхождений с docs/c52-facts.md нет.')
