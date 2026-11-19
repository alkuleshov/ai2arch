# Сборка PDF «53 способа» (tools/guide53)

Источник контента: `build/data.py` (53 способа, разделы, курсы). Вёрстка: `build/build.py` (reportlab, A4).
Шрифты Manrope и DejaVu Sans Mono лежат в `fonts/`, изображения в `img/`.

Сборка:

    cd tools/guide53/build
    python3 build.py ../out.pdf        # нужен пакет reportlab

Страницы для листалки на сайте (WebP 1200 px и @2x 2200 px, `guide/53/pNN.webp`, `pNN@2x.webp`):

    pdftoppm -r 267 -png out.pdf pages/h
    # затем PIL: resize до 2200 и до 1200 px по ширине, WebP quality 82, method 6

Масштаб текста карточек задаёт константа `K` в `build.py`.
