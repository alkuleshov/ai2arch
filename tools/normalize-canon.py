#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приводит текст лекции из Gemini к канону docs/lectures/N.N.md.

Что правит:
  * «Вывод по слайду: …» → весь абзац курсивом;
  * пустые строки между пунктами списков убирает;
  * таблицы, разорванные пустыми строками внутри ячеек, склеивает;
  * сноску под таблицей таймкодов приводит к виду «\\* В варианте на 60 минут…»;
  * лишние пустые строки схлопывает.

Использование: normalize-canon.py вход.txt [выход.md]  (без выхода — печатает в stdout)
"""
import re
import sys


def normalize(text: str) -> str:
    t = text.replace('\r\n', '\n').replace(' ', ' ')
    t = '\n'.join(line.rstrip() for line in t.split('\n'))
    # таблицы: пустая строка внутри строки таблицы
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r'(?m)^(\|[^\n]*[^|\n])\n[ \t]*\n[ \t]*\|', r'\1 |', t)
    # пустые строки между пунктами списков
    item = r'(?:\* |\d+\. |- )'
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r'(\n' + item + r'[^\n]*)\n{2,}(?=' + item + r')', r'\1\n', t)
    # вывод по слайду курсивом
    t = re.sub(r'^Вывод по слайду:[ \t]*(.+?)[ \t]*$', r'*Вывод по слайду: \1*', t, flags=re.M)
    t = re.sub(r'^\*\*Вывод по слайду:[ \t]*(.+?)\*\*$', r'*Вывод по слайду: \1*', t, flags=re.M)
    # сноска таймкодов
    t = re.sub(r'^\*{1,2}[ \t]*(В варианте на 60 минут[^\n]*?)\*{0,2}$', r'\\* \1', t, flags=re.M)
    # схлопнуть лишние пустые строки
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip() + '\n'


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = open(sys.argv[1], encoding='utf-8').read()
    out = normalize(src)
    if len(sys.argv) > 2:
        open(sys.argv[2], 'w', encoding='utf-8').write(out)
    else:
        sys.stdout.write(out)
