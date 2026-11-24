#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Добавляет очередную часть лекции из Gemini в канон docs/lectures/N.N.md.

Использование: merge-canon-part.py N.N часть.txt

Что делает:
  * нормализует текст (tools/normalize-canon.py);
  * блок «## Часть K …» (вместе с мостом, оговорками, результатом, таймкодами) вставляет
    перед «#### Итог темы» / «#### Квиз»; если часть K уже была, заменяет её;
  * новые термины словаря дописывает, повторы пропускает;
  * главы квиза добавляет в общий JSON (главы с тем же номером заменяются);
  * «#### Итог темы …» (если пришёл) держит последним перед квизом.
Если файла N.N.md ещё нет, часть сохраняется как есть (первая часть: заголовок, памятка, словарь).
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('norm', ROOT / 'tools' / 'normalize-canon.py')
norm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(norm)

QUIZ_H = '#### Квиз (не читать, добавляется в лонгрид)'


def split_quiz(text):
    i = text.find('#### Квиз')
    if i < 0:
        return text.rstrip() + '\n', []
    head, tail = text[:i], text[i:]
    m = re.search(r'```json\s*(.*?)```', tail, re.S)
    quiz = json.loads(m.group(1)) if m else []
    return head.rstrip() + '\n', quiz


def split_final(text):
    m = re.search(r'^#### Итог темы[^\n]*\n.*?(?=^#### |\Z)', text, re.M | re.S)
    if not m:
        return text, ''
    return text[:m.start()].rstrip() + '\n', m.group(0).strip() + '\n'


def terms_of(block):
    return {m.group(1).strip(): m.group(0) for m in re.finditer(r'^\* \*\*(.+?)\*\* — .+$', block, re.M)}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    key, part_file = sys.argv[1], sys.argv[2]
    target = ROOT / 'docs' / 'lectures' / f'{key}.md'
    new = norm.normalize(Path(part_file).read_text(encoding='utf-8'))
    if not target.exists():
        target.write_text(new, encoding='utf-8')
        print(f'создан {target.name}')
        return
    old = target.read_text(encoding='utf-8')
    old_body, old_quiz = split_quiz(old)
    new_body, new_quiz = split_quiz(new)
    old_body, old_final = split_final(old_body)
    new_body, new_final = split_final(new_body)

    # новая часть: от первого «## Часть» до конца тела
    pm = re.search(r'^## Часть (\d+) · [^\n]*$', new_body, re.M)
    if not pm:
        sys.exit('В тексте нет заголовка «## Часть N · Слайды a–b»')
    part_no = pm.group(1)
    part_text = new_body[pm.start():].strip() + '\n'

    # новые термины
    sm = re.search(r'^#### Словарь\n(.*?)(?=^## |\Z)', new_body, re.M | re.S)
    if sm:
        have = terms_of(old_body)
        add = [t for k, t in terms_of(sm.group(1)).items() if k not in have]
        if add:
            om = re.search(r'^#### Словарь\n.*?(?=^## )', old_body, re.M | re.S)
            old_body = old_body[:om.end()].rstrip() + '\n\n' + '\n'.join(add) + '\n\n' + old_body[om.end():]
            print(f'новых терминов: {len(add)}')

    # заменить часть с тем же номером или добавить в конец
    rm = re.search(rf'^## Часть {part_no} · [^\n]*$.*?(?=^## Часть |\Z)', old_body, re.M | re.S)
    if rm:
        old_body = old_body[:rm.start()] + part_text + '\n' + old_body[rm.end():]
        print(f'часть {part_no} заменена')
    else:
        old_body = old_body.rstrip() + '\n\n' + part_text
        print(f'часть {part_no} добавлена')

    final = new_final or old_final
    out = old_body.rstrip() + '\n\n'
    if final:
        out += final.rstrip() + '\n\n'
    # квиз
    chapters = {c['chapter']: c for c in old_quiz}
    for c in new_quiz:
        chapters[c['chapter']] = c
    quiz = [chapters[k] for k in sorted(chapters)]
    for c in quiz:
        assert len(c['questions']) == 4, f"глава {c['chapter']}: {len(c['questions'])} вопросов"
        for q in c['questions']:
            assert len(q['opts']) == 4 and 0 <= q['a'] < 4, f"глава {c['chapter']}: {q['q'][:40]}"
    out += QUIZ_H + '\n\n```json\n' + json.dumps(quiz, ensure_ascii=False, indent=2) + '\n```\n'
    target.write_text(out, encoding='utf-8')
    slides = len(re.findall(r'^### Слайд', out, re.M))
    print(f'{target.name}: слайдов {slides}, глав квиза {len(quiz)}')


if __name__ == '__main__':
    main()
