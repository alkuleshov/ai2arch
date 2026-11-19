# Stage 3 brief — English versions of the redevelopment lesson pages

Normative sources: `/srv/projects/ai2arch/CLAUDE.md`, `tools/i18n/glossary.md`, this file.
Source pages: `redev-*.html` in the repository root (except `redev.html`, `redev-guide.html`, `redev-schedule.html`).
Output: the same file names under `/en/`.

## Non-negotiables

- Do not modify Russian root files, shared assets, or other agents' files.
- Do not run git commands.
- Copy the Russian HTML and apply exact replacements with a Python script; verify every replacement occurred. Preserve CSS, HTML structure, and JavaScript logic. Never rewrite a page from scratch.
- Translate every human-visible string, SVG `<text>`, `alt`, `aria-label`, `placeholder`, `title`, `data-foot`, success/error/hint text, JS user-facing strings and comments, and CSS/HTML comments.
- Professional English, C1, no calques, no marketing noise. Follow the glossary.
- Zero Cyrillic in the output. Check with:
  `grep -nP '[\x{0400}-\x{04FF}]' en/<file>`
- Keep all ids, classes, `data-*` logic values, slide indices, prompt-copy targets, quiz answer indices and localStorage keys unchanged.
- Do not mention Essentuki or Bazarny Lane. The teaching object is C52 (Suvorova St., 52 and 52a). Prices, dates and volumes stay unchanged: 72 academic hours, 4.5 weeks, 18,900 ₽ / 14,900 ₽, November 5, 2026, Demo Day December 6, November 16.
- Never use “defense before a jury” or “jury” for the redevelopment final format. Use **Demo Day**, **remote expert review**, **pitch**, **final project review**.
- The group chat / meeting service is **Yandex Telemost** everywhere.
- Keep emoji, arrows and visual markers.

## Paths from `/en/`

- `images/...` → `../images/...`
- `assets/...` → `../assets/...`
- favicons / apple-touch → `../favicon...`, `../apple-touch-icon.png`
- `guide/...` → `../guide/...`
- Sibling pages (`index.html`, `redev.html`, `redev-guide.html`, `redev-schedule.html`, `redev-*.html`) stay sibling names — they resolve inside `/en/`.
- Absolute links to Russian pages such as `https://ai2arch.ru/redev-schedule.html` become `redev-schedule.html` (or `https://ai2arch.ru/en/redev-schedule.html` if an absolute URL is required by the markup).
- External links (Notion, Google Sheets, Telemost, VK Video, c52.space, NSPD, etc.) stay byte-for-byte identical.

## Head block for slide-deck pages

Slide-deck pages (`redev-artifact2`, `crashtest`, `dossier`, `gen`, `hbu`, `hypothesis`, `income`, `intro`, `market`, `meeting2`, `moodboard`, `roles`, `stress`, `m4-*`) currently have only `<title>` and no meta description/OG.

Add:

```html
<html lang="en">
...
<title>Translated title · AI in Architecture / AI in Redevelopment · AI2ARCH</title>
<meta name="description" content="One or two English sentences describing this lesson. Derive it from the page's own hero/intro, do not invent facts.">
<link rel="canonical" href="https://ai2arch.ru/en/FILE.html">
<link rel="alternate" hreflang="ru" href="https://ai2arch.ru/FILE.html">
<link rel="alternate" hreflang="en" href="https://ai2arch.ru/en/FILE.html">
<link rel="alternate" hreflang="x-default" href="https://ai2arch.ru/FILE.html">
<meta property="og:type" content="article">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="https://ai2arch.ru/en/FILE.html">
<meta property="og:title" content="Translated title">
<meta property="og:description" content="Same as meta description">
<meta property="og:image" content="https://ai2arch.ru/images/og-ai2arch.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Translated title">
<meta name="twitter:description" content="Same as meta description">
<meta name="twitter:image" content="https://ai2arch.ru/images/og-ai2arch.jpg">
<link rel="stylesheet" href="../assets/lang-switch.css">
```

Place the stylesheet link before the page `<style>` block. Do not add Metrika to pages that do not have it.

## Language switcher

### Slide-deck pages (fixed pill, no header)

Immediately after `<body>` (before the SVG sprite), add:

```html
<span class="lang-switch deck-lang" aria-label="Language switcher"><a href="../FILE.html" hreflang="ru" lang="ru">RU</a><span class="sep" aria-hidden="true">|</span><span class="on" aria-current="true">EN</span></span>
```

It points to the same page in Russian, not to `redev.html`.

### Longread (`redev-read-income.html`, fixed `.lr-head`)

Add in the `.lr-head`, before `<button id="tocBtn" ...>`:

```html
<span class="lang-switch" aria-label="Language switcher"><a href="../redev-read-income.html" hreflang="ru" lang="ru">RU</a><span class="sep" aria-hidden="true">|</span><span class="on" aria-current="true">EN</span></span>
```

The header is light, so the switcher inherits the dark ink colour; do not force white.

## Slide-deck specifics

- Keep the deck JS (`prev/next`, TOC, fullscreen, keyboard, copy buttons, prompts section) unchanged except translated strings/comments.
- Translate the TOC labels that JS builds from slide headings automatically (they use the translated `h2`).
- Translate the bottom control `aria-label`/`title` (`Back`, `Next`, `Contents`, `Expand to full screen`), the hint (`← → to navigate · F — fullscreen`), the counter format, and the prompts-section headings/lead.
- Translate `data-foot` values and all `.terms` glossary entries.
- Translate SVG `<text>` labels. If the English string is longer, reduce that `<text>` element's `font-size` by 1–2 px or wrap it; do not let text leave its box.
- Prompts must work as English prompts: imperative, explicit output format, placeholders in square brackets.
- Images with baked-in Russian text cannot be retranslated; keep them and report which pages contain such images.

## Longread specifics (`redev-read-income.html`)

- Preserve chapter/section ids, the reading-progress JS, font-size and slide-position controls, quiz logic and localStorage keys.
- Translate the header controls (`Contents`, `Font size`, slide position options `Side / Above text / Hide`), TOC entries, chapter briefs, verdicts, terms, prompts, tables, quiz questions/answers, and the trainer.
- Keep table structure and numeric data unchanged.
- If a quiz answer index points to an option, keep the same index after translation; verify the correct answer is still correct.

## Verification before returning

1. `python3` HTML parser: the file parses; counts of `<section>`, `<script>`, `<style>`, `<svg>` (and `<table>` where present) equal the Russian source.
2. No relative URL starts with `images/`, `assets/`, `guide/`, `favicon` or `apple-touch` without `../`.
3. `grep -nP '[\x{0400}-\x{04FF}]' en/<file>` returns nothing.
4. The switcher points to the Russian counterpart; canonical/hreflang point to the right URLs.
5. `git diff --stat <source>` is empty; you did not touch the Russian file.
6. External URLs are identical to the source (compare programmatically).
7. No Essentuki/Bazarny; C52 format is correct.

Report back: files written, replacement counts, check results, non-obvious translation choices, and any raster images that still contain Russian text.
