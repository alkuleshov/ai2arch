# -*- coding: utf-8 -*-
# All UI strings of the 53-ways PDF, per language.
# Content of the ways lives in data.py (ru) and data_en.py (en).

RU = {
    # PDF metadata
    "meta_title": "53 способа использовать ИИ для архитектора — AI2ARCH",
    "meta_author": "AI2ARCH · Лаборатория проектного интеллекта",
    "meta_subject": "Практический гайд с промпт-шаблонами. Редакция: ноябрь 2026",
    "meta_keywords": "ИИ, архитектура, промпты, AI2ARCH, ai2arch.ru",

    # brand, header, footer
    "brand_descriptor": "ЛАБОРАТОРИЯ ПРОЕКТНОГО ИНТЕЛЛЕКТА",
    "header_site": "AI2ARCH.RU",
    "brand_url": "https://ai2arch.ru",
    "footer_page": "стр. {n}",
    "footer_brand": "AI2ARCH  ·  ЛАБОРАТОРИЯ ПРОЕКТНОГО ИНТЕЛЛЕКТА",

    # way card
    "core_label": "ОСНОВНОЙ",
    "extended_label": "РАСШИРЕННЫЙ",
    "prompt_label": "ПРОМПТ:",

    # cover
    "cover_eyebrow": "СИСТЕМА   ·   АНАЛИЗ   ·   СТРАТЕГИЯ   ·   ИССЛЕДОВАНИЕ",
    "cover_title": "53 СПОСОБА",
    "cover_sub1": "использовать ИИ",
    "cover_sub2": "для архитектора",
    "cover_tagline": "ПРАКТИЧЕСКИЙ ГАЙД С ПРОМПТ-ШАБЛОНАМИ",
    "cover_date": "AI2ARCH.RU   ·   НОЯБРЬ 2026",
    "bm_cover": "Обложка",

    # TOC
    "toc_heading": "Содержание",
    "toc_note": "способ разбирается в курсах AI2ARCH",
    "bm_toc": "Содержание",
    "toc_outside": "ВНЕ ПРОГРАММЫ КУРСОВ",

    # legend
    "legend_heading": "Как читать гайд",
    "bm_legend": "Как читать гайд",
    "legend_toolsets": "КОНТУРЫ ИНСТРУМЕНТОВ",
    "legend_core_text": "Работает из России напрямую, оплата из РФ: Алиса AI, GigaChat (Kandinsky), Шедеврум, DeepSeek, QGIS, Яндекс Геоаналитика, Яндекс Переводчик, НСПД, Gamma.",
    "legend_extended_text": "Зарубежные сервисы с ограниченным доступом из России: ChatGPT, Claude, Gemini, Midjourney, Flux, QuickOSM, Photoshop и другие. Выбор сервиса и доступ к нему — за пользователем.",
    "legend_badges": "ЗНАЧКИ КУРСОВ",
    "legend_badge_chips": [("archi", "модуль 3"), ("redev", "тема 1.3")],
    "legend_badge_note": "Способ разбирается на курсе AI2ARCH, рядом — модуль или тема. Значок — ссылка на страницу курса. Таких способов {n} из 53; в содержании они отмечены точкой.",
    "legend_prompts": "ПРОМПТЫ",
    "legend_prompt_text": "В квадратных скобках — то, что подставляете вы. Факты, нормы и цифры проверяйте по первоисточникам: ИИ ошибается и выдумывает.",
    "legend_sections": "РАЗДЕЛЫ 05 И 08",
    "legend_sections_text": "BIM-автоматизацию, бизнес и маркетинг курсы AI2ARCH не разбирают — это карта на вырост. Исключения внутри разделов отмечены значками курсов.",

    # dividers
    "divider_outside": "ВНЕ ПРОГРАММЫ КУРСОВ",
    "divider_count_one": "{n} СПОСОБ ПРИМЕНЕНИЯ",
    "divider_count_many": "{n} СПОСОБОВ ПРИМЕНЕНИЯ",
    "divider_note_off": "Карта на вырост: эти задачи курсы AI2ARCH не разбирают. Исключения — способы {off}, они есть в курсах.",
    "divider_note_cover": "В курсах AI2ARCH разбираются {cov} из {total} способов раздела — они отмечены значками курсов.",

    # final page
    "bm_courses": "Курсы AI2ARCH",
    "final_heading": "Курсы AI2ARCH",
    "final_lead1": "Исследуем, как ИИ работает в архитектуре и девелопменте,",
    "final_lead2": "и учим этому на двух курсах.",
    "final_ways_prefix": "Способы из гайда: ",
    "final_footer": "Объединяем архитектуру, данные и искусственный интеллект для проектирования будущего городов и территорий.",
    # fact chip padding and gap on the final page
    "fact_pad": 16, "fact_gap": 6,
    "final_courses": [
        {
            "key": "archi",
            "eyebrow": "ПЕРВАЯ СТУПЕНЬ",
            "name": "ИИ в архитектуре",
            "official": "«Современные инструменты проектного анализа: ИИ и мобильные сервисы в работе с архитектурной средой»",
            "desc": "Базовый вводный курс: цифровой двойник участка, ИИ-анализ и презентация для заказчика. С нуля, два трека на выбор.",
            "facts": ["22 ак. часа", "2,5 недели", "Удостоверение ЮФУ"],
            "link": "ai2arch.ru/archi",
            "url": "https://ai2arch.ru/archi.html",
        },
        {
            "key": "redev",
            "eyebrow": "ВТОРАЯ СТУПЕНЬ",
            "name": "ИИ в редевелопменте",
            "official": "«Современные инструменты развития территорий и объектов недвижимости: аналитика данных и генеративный ИИ в разработке концепций»",
            "desc": "Реальное здание или территория — до защищённой концепции. Два трека: проектировщик и девелопер.",
            "facts": ["72 ак. часа", "4,5 недели", "Удостоверение ЮФУ"],
            "link": "ai2arch.ru/redev",
            "url": "https://ai2arch.ru/redev.html",
        },
    ],
}

EN = {
    # PDF metadata
    "meta_title": "53 Ways to Use AI for Architects — AI2ARCH",
    "meta_author": "AI2ARCH · Project Intelligence Lab",
    "meta_subject": "A practical guide with prompt templates. November 2026 edition",
    "meta_keywords": "AI, architecture, prompts, AI2ARCH, ai2arch.ru",

    # brand, header, footer
    "brand_descriptor": "PROJECT INTELLIGENCE LAB",
    "header_site": "AI2ARCH.RU",
    "brand_url": "https://ai2arch.ru/en/",
    "footer_page": "page {n}",
    "footer_brand": "AI2ARCH  ·  PROJECT INTELLIGENCE LAB",

    # way card
    "core_label": "CORE",
    "extended_label": "EXTENDED",
    "prompt_label": "PROMPT:",

    # cover
    "cover_eyebrow": "SYSTEM   ·   ANALYSIS   ·   STRATEGY   ·   RESEARCH",
    "cover_title": "53 WAYS",
    "cover_sub1": "to use AI",
    "cover_sub2": "for architects",
    "cover_tagline": "A PRACTICAL GUIDE WITH PROMPT TEMPLATES",
    "cover_date": "AI2ARCH.RU   ·   NOVEMBER 2026",
    "bm_cover": "Cover",

    # TOC
    "toc_heading": "Contents",
    "toc_note": "ways covered in AI2ARCH courses",
    "bm_toc": "Contents",
    "toc_outside": "OUTSIDE THE COURSE PROGRAM",

    # legend
    "legend_heading": "How to Read This Guide",
    "bm_legend": "How to Read This Guide",
    "legend_toolsets": "TOOLSETS",
    "legend_core_text": "Works from Russia without a VPN and can be paid for from Russia: Alice AI, GigaChat (Kandinsky), Shedevrum, DeepSeek, QGIS, Yandex Geoanalytics, Yandex Translate, NSPD, Gamma.",
    "legend_extended_text": "International services with restricted access from Russia: ChatGPT, Claude, Gemini, Midjourney, Flux, QuickOSM, Photoshop, and others. Choosing a service and arranging access is up to the user.",
    "legend_badges": "COURSE BADGES",
    "legend_badge_chips": [("archi", "Module 3"), ("redev", "Topic 1.3")],
    "legend_badge_note": "A way is covered in an AI2ARCH course; the module or topic is shown next to it. The badge links to the course page. {n} of the 53 ways are covered; they are marked with a dot in the contents.",
    "legend_prompts": "PROMPTS",
    "legend_prompt_text": "Square brackets mark the parts you fill in. Verify facts, codes, and figures against primary sources: AI makes mistakes and invents things.",
    "legend_sections": "SECTIONS 05 AND 08",
    "legend_sections_text": "AI2ARCH courses do not cover BIM automation, business, or marketing; this is a map for future growth. Exceptions within the sections are marked with course badges.",

    # dividers
    "divider_outside": "OUTSIDE THE COURSE PROGRAM",
    "divider_count_one": "{n} WAY TO USE",
    "divider_count_many": "{n} WAYS TO USE",
    "divider_note_off": "A map for future growth: AI2ARCH courses do not cover these tasks. Exceptions are ways {off}, which are covered.",
    "divider_note_cover": "AI2ARCH courses cover {cov} of the {total} ways in this section; they are marked with course badges.",

    # final page
    "bm_courses": "AI2ARCH Courses",
    "final_heading": "AI2ARCH Courses",
    "final_lead1": "We study how AI works in architecture and redevelopment,",
    "final_lead2": "and teach it in two courses.",
    "final_ways_prefix": "Ways from the guide: ",
    "final_footer": "We bring together architecture, data, and artificial intelligence to design the future of cities and territories.",
    # English fact labels are longer; tighter chips keep them inside the card
    "fact_pad": 12, "fact_gap": 4,
    "final_courses": [
        {
            "key": "archi",
            "eyebrow": "LEVEL 1",
            "name": "AI in Architecture",
            "official": "Modern Tools of Project Analysis: AI and Mobile Services for the Architectural Environment",
            "desc": "An introductory course: a digital site model, AI analysis, and a client presentation. From scratch, with two tracks to choose from.",
            "facts": ["22 academic hours", "2.5 weeks", "SFedU certificate"],
            "link": "ai2arch.ru/en/archi",
            "url": "https://ai2arch.ru/en/archi.html#enroll",
        },
        {
            "key": "redev",
            "eyebrow": "LEVEL 2",
            "name": "AI in Redevelopment",
            "official": "Modern Tools for the Development of Territories and Real Estate: Data Analytics and Generative AI in Concept Development",
            "desc": "A real building or territory, carried through to a fully developed concept. Two tracks: designer and developer.",
            "facts": ["72 academic hours", "4.5 weeks", "SFedU certificate"],
            "link": "ai2arch.ru/en/redev",
            "url": "https://ai2arch.ru/en/redev.html#apply",
        },
    ],
}

STRINGS = {"ru": RU, "en": EN}
