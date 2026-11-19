# -*- coding: utf-8 -*-
import sys, os, math, argparse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit, ImageReader

sys.path.insert(0, os.path.dirname(__file__))
from strings import STRINGS

_parser = argparse.ArgumentParser(description="Build the AI2ARCH 53-ways PDF.")
_parser.add_argument("out", nargs="?", default=None, help="output PDF path")
_parser.add_argument("--lang", choices=("ru", "en"), default="ru", help="edition language")
_args = _parser.parse_args()

LANG = _args.lang
S = STRINGS[LANG]
if LANG == "en":
    import data_en as _data
else:
    import data as _data
W, SECTIONS, COURSES, A, R = _data.W, _data.SECTIONS, _data.COURSES, _data.A, _data.R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
IMG = os.path.join(ROOT, "img")
OUT = _args.out or os.path.join(ROOT, "ai2arch-53ways.pdf")

pdfmetrics.registerFont(TTFont("MR", os.path.join(FONTS, "Manrope-Regular.ttf")))
pdfmetrics.registerFont(TTFont("MS", os.path.join(FONTS, "Manrope-SemiBold.ttf")))
pdfmetrics.registerFont(TTFont("MB", os.path.join(FONTS, "Manrope-ExtraBold.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(FONTS, "DejaVuSansMono.ttf")))
pdfmetrics.registerFont(TTFont("MonoB", os.path.join(FONTS, "DejaVuSansMono-Bold.ttf")))

PW, PH = A4
M = 50
BG = HexColor("#000C1F"); BG_COVER = HexColor("#010516")
CARD = HexColor("#0D1E35"); PROMPT_BG = HexColor("#132540"); BAND = HexColor("#061428")
GRID = HexColor("#08182E"); LINE = HexColor("#1B2C47")
AZ = HexColor("#1A6BFF"); AZ_L = HexColor("#4DA3FF")
WHITE = HexColor("#F6F4F0"); TXT = HexColor("#C9D3E3"); MUTED = HexColor("#8A97AD"); FAINT = HexColor("#56647C")
GREEN = HexColor("#3DDC97"); BIGNUM = HexColor("#0C1D36")

ARTIFACT = ImageReader(os.path.join(IMG, "artifact_soft.png"))
SIGN = ImageReader(os.path.join(IMG, "sign.png"))

SEC_BY_NO = {s[0]: s for s in SECTIONS}
COVERED = {w[0] for w in W if w[7]}


def tw(text, font, size):
    return pdfmetrics.stringWidth(text, font, size)


def spaced(c, x, y, text, font, size, color, tracking=0.8, anchor="left"):
    width = sum(tw(ch, font, size) for ch in text) + tracking * (len(text) - 1)
    if anchor == "center":
        x -= width / 2
    elif anchor == "right":
        x -= width
    c.setFont(font, size); c.setFillColor(color)
    for ch in text:
        c.drawString(x, y, ch)
        x += tw(ch, font, size) + tracking
    return width


def bg(c, color=BG, grid=True, step=28):
    c.setFillColor(color); c.rect(0, 0, PW, PH, stroke=0, fill=1)
    if grid:
        c.setStrokeColor(GRID); c.setLineWidth(0.4)
        x = 0
        while x <= PW:
            c.line(x, 0, x, PH); x += step
        y = 0
        while y <= PH:
            c.line(0, y, PW, y); y += step


def brand_mark(c, x, y, size=22, small=True):
    c.drawImage(SIGN, x, y - size / 2, size, size, mask="auto")
    c.setFillColor(WHITE); c.setFont("MB", 8.5 if small else 11)
    c.drawString(x + size + 7, y + 1.5, "AI2ARCH")
    spaced(c, x + size + 7, y - 7.5, S["brand_descriptor"], "MR", 4.6, MUTED, 0.35)


def header(c, sec):
    c.setFillColor(BAND); c.rect(0, PH - 46, PW, 46, stroke=0, fill=1)
    c.setFillColor(AZ); c.rect(0, PH - 46, 8, 46, stroke=0, fill=1)
    c.setFillColor(WHITE); c.setFont("MB", 9)
    c.drawString(M, PH - 28, f"{sec[0]}  {sec[1]}")
    spaced(c, PW - M, PH - 28, S["header_site"], "Mono", 7, FAINT, 0.6, "right")
    c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(0, PH - 46, PW, PH - 46)


def footer(c, page_no):
    c.setFillColor(BAND); c.rect(0, 0, PW, 32, stroke=0, fill=1)
    c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(0, 32, PW, 32)
    spaced(c, M, 13, S["footer_page"].format(n=page_no), "Mono", 7, FAINT, 0.4)
    spaced(c, PW - M, 13, S["footer_brand"], "Mono", 6.6, FAINT, 0.5, "right")


def dot(c, x, y, r, color):
    c.setFillColor(color); c.circle(x, y, r, stroke=0, fill=1)


def chip(c, x, y, text, url=None, h=15, size=7.2):
    """Значок курса: рамка, точка, текст. y — нижняя граница. Возвращает ширину."""
    w = tw(text, "MS", size) + 22
    c.setFillColor(HexColor("#0F2A55")); c.setStrokeColor(AZ); c.setLineWidth(0.7)
    c.roundRect(x, y, w, h, h / 2, stroke=1, fill=1)
    dot(c, x + 8, y + h / 2, 2.2, AZ_L)
    c.setFillColor(WHITE); c.setFont("MS", size)
    c.drawString(x + 14, y + h / 2 - size * 0.36, text)
    if url:
        c.linkURL(url, (x, y, x + w, y + h), relative=0, thickness=0)
    return w


def chip_text(course, label):
    return f"{COURSES[course][0]} · {label}"


# ---------- карточка способа ----------
K = 1.36  # масштаб текста карточек (экранное чтение)
CARD_X = M; CARD_W = PW - 2 * M
NUM_COL = 50
IN_X = CARD_X + NUM_COL + 14
IN_W = CARD_W - NUM_COL - 14 - 14
TITLE_SIZE = 12.2 * K
SUB_SIZE = 8.5 * K
DESC_SIZE, DESC_LEAD = 8.7 * K, 12.4 * K
TOOL_SIZE, TOOL_LEAD = 8 * K, 11.2 * K
P_SIZE, P_LEAD = 7.3 * K, 10.4 * K
LBL_SIZE = 6.2 * K
CHIP_SIZE, CHIP_H = 7.2 * K, 15 * K
LBL_W = 11 * K + tw(S["extended_label"], "MS", LBL_SIZE) + 0.5 * 10 + 16


def card_layout(w):
    """Все вертикальные позиции — отступы вниз от верха карточки (d). Возвращает высоту и план отрисовки."""
    n, sec, title, sub, desc, osn, ext, courses, prompt = w
    plan = []
    d = 26 * K
    tl = simpleSplit(title, "MB", TITLE_SIZE, IN_W)
    for i, ln in enumerate(tl):
        plan.append(("title", d, ln))
        if i < len(tl) - 1:
            d += 15.5 * K
    d += 14 * K
    sl = simpleSplit(sub, "MS", SUB_SIZE, IN_W)
    for i, ln in enumerate(sl):
        plan.append(("sub", d, ln))
        if i < len(sl) - 1:
            d += 11 * K
    d += 16 * K
    for ln in simpleSplit(desc, "MR", DESC_SIZE, IN_W):
        plan.append(("desc", d, ln)); d += DESC_LEAD
    d += 5 * K
    tools = []
    if osn:
        tools.append((S["core_label"], GREEN, " · ".join(osn)))
    tools.append((S["extended_label"], MUTED, " · ".join(ext)))
    for label, color, text in tools:
        plan.append(("label", d, (label, color)))
        for ln in simpleSplit(text, "MR", TOOL_SIZE, IN_W - LBL_W):
            plan.append(("tool", d, ln)); d += TOOL_LEAD
    d -= TOOL_LEAD  # d = baseline последней строки инструментов
    if courses:
        d += 10 * K
        plan.append(("chips", d + CHIP_H, courses))  # нижняя граница значков
        d += CHIP_H + 11 * K
    else:
        d += 13 * K
    p_lines = simpleSplit(prompt, "Mono", P_SIZE, IN_W - 24)
    p_top = d
    d += 14 * K
    plan.append(("plabel", d, None))
    d += 12 * K
    for ln in p_lines:
        plan.append(("pline", d, ln)); d += P_LEAD
    d = d - P_LEAD + 9 * K
    plan.append(("pbox", p_top, d))
    h = d + 14 * K
    return h, plan


def draw_card(c, w, top):
    n, sec, title, sub, desc, osn, ext, courses, prompt = w
    h, plan = card_layout(w)
    y0 = top - h
    c.bookmarkPage(f"w{n}", fit="XYZ", left=0, top=top + 10)
    c.setFillColor(CARD); c.rect(CARD_X, y0, CARD_W, h, stroke=0, fill=1)
    c.setFillColor(HexColor("#091A31")); c.rect(CARD_X, y0, NUM_COL, h, stroke=0, fill=1)
    c.setFillColor(AZ); c.rect(CARD_X, y0, 6, h, stroke=0, fill=1)
    c.setFillColor(WHITE); c.setFont("MB", 16 * K)
    cx = CARD_X + 6 + (NUM_COL - 6) / 2
    c.drawCentredString(cx, y0 + h / 2 - 5 * K, f"{n:02d}")
    if courses:
        dot(c, cx, y0 + h / 2 - 17 * K, 2.4 * K, AZ_L)
    for kind, d, p in plan:
        if kind == "pbox":
            c.setFillColor(PROMPT_BG); c.rect(IN_X, top - p, IN_W, p - d, stroke=0, fill=1)
            c.setFillColor(AZ); c.rect(IN_X, top - p, 3, p - d, stroke=0, fill=1)
    for kind, d, p in plan:
        y = top - d
        if kind == "title":
            c.setFillColor(WHITE); c.setFont("MB", TITLE_SIZE); c.drawString(IN_X, y, p)
        elif kind == "sub":
            c.setFillColor(AZ_L); c.setFont("MS", SUB_SIZE); c.drawString(IN_X, y, p)
        elif kind == "desc":
            c.setFillColor(TXT); c.setFont("MR", DESC_SIZE); c.drawString(IN_X, y, p)
        elif kind == "label":
            label, color = p
            dot(c, IN_X + 3, y + 2.7 * K, 2.4 * K, color)
            spaced(c, IN_X + 11 * K, y + 0.4 * K, label, "MS", LBL_SIZE, color, 0.5)
        elif kind == "tool":
            c.setFillColor(TXT); c.setFont("MR", TOOL_SIZE); c.drawString(IN_X + LBL_W, y, p)
        elif kind == "chips":
            x = IN_X
            for course, label in p:
                x += chip(c, x, y, chip_text(course, label), COURSES[course][1], h=CHIP_H, size=CHIP_SIZE) + 8
            if x - 8 > IN_X + IN_W:
                print("WARN chips overflow", n)
        elif kind == "plabel":
            spaced(c, IN_X + 12, y, S["prompt_label"], "MonoB", 6.8 * K, AZ_L, 0.5)
        elif kind == "pline":
            c.setFillColor(HexColor("#E3EAF5")); c.setFont("Mono", P_SIZE); c.drawString(IN_X + 12, y, p)
    return h


# ---------- страницы ----------
class Doc:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.c.setTitle(S["meta_title"])
        self.c.setAuthor(S["meta_author"])
        self.c.setSubject(S["meta_subject"])
        self.c.setKeywords(S["meta_keywords"])
        self.page = 1

    def next(self):
        self.c.showPage(); self.page += 1


def cover(d):
    c = d.c
    bg(c, BG_COVER)
    c.setFillColor(AZ); c.rect(0, PH - 6, PW, 6, stroke=0, fill=1)
    s = 330
    c.drawImage(ARTIFACT, (PW - s) / 2, PH - 70 - s, s, s, mask="auto")
    y = PH - 70 - s - 34
    spaced(c, PW / 2, y, S["cover_eyebrow"], "Mono", 6.6, MUTED, 0.6, "center")
    y -= 52
    c.setFillColor(WHITE); c.setFont("MB", 44); c.drawCentredString(PW / 2, y, S["cover_title"])
    y -= 30
    c.setFont("MR", 22); c.drawCentredString(PW / 2, y, S["cover_sub1"])
    y -= 27
    c.drawCentredString(PW / 2, y, S["cover_sub2"])
    y -= 26
    c.setStrokeColor(AZ); c.setLineWidth(0.8); c.line(PW / 2 - 110, y, PW / 2 + 110, y)
    y -= 20
    spaced(c, PW / 2, y, S["cover_tagline"], "Mono", 6.8, MUTED, 0.6, "center")
    brand_mark(c, M, 52, 26)
    spaced(c, PW - M, 50, S["cover_date"], "Mono", 7, MUTED, 0.6, "right")
    c.linkURL(S["brand_url"], (PW - M - 140, 44, PW - M, 58), relative=0, thickness=0)
    c.bookmarkPage("cover"); c.addOutlineEntry(S["bm_cover"], "cover", level=0)
    d.next()


def toc_and_legend(d):
    c = d.c
    first = True
    top_limit = PH - 150
    bottom = 60

    def start_page(with_title):
        bg(c)
        c.setFillColor(AZ); c.rect(0, PH - 6, PW, 6, stroke=0, fill=1)
        brand_mark(c, M, PH - 52, 22)
        y = PH - 70
        if with_title:
            c.setFillColor(WHITE); c.setFont("MB", 24); c.drawString(M, PH - 108, S["toc_heading"])
            dot(c, PW - M - 168, PH - 104, 2.6, AZ_L)
            c.setFillColor(MUTED); c.setFont("MR", 7.6)
            c.drawString(PW - M - 161, PH - 106.5, S["toc_note"])
            c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(M, PH - 122, PW - M, PH - 122)
            y = PH - 140
        else:
            y = PH - 95
        footer(c, d.page)
        return y

    y = start_page(True)
    c.bookmarkPage("toc"); c.addOutlineEntry(S["bm_toc"], "toc", level=0)
    col_w = (PW - 2 * M) / 2
    for no, name, _, off in SECTIONS:
        items = [w for w in W if w[1] == no]
        rows = math.ceil(len(items) / 2)
        need = 26 + 14 + rows * 15.5 + 12
        if y - need < bottom:
            d.next(); y = start_page(False)
        c.setFillColor(HexColor("#0D1E35")); c.rect(M, y - 24, PW - 2 * M, 24, stroke=0, fill=1)
        c.setFillColor(AZ); c.rect(M, y - 24, 5, 24, stroke=0, fill=1)
        c.setFillColor(WHITE); c.setFont("MB", 8.6); c.drawString(M + 16, y - 15.5, f"{no}  {name}")
        if off:
            spaced(c, PW - M - 12, y - 15, S["toc_outside"], "MS", 6.2, MUTED, 0.6, "right")
        c.linkRect("", f"sec{no}", (M, y - 24, PW - 2 * M + M, y), relative=0, thickness=0)
        y -= 24 + 16
        for i, w in enumerate(items):
            col = i % 2; row = i // 2
            x = M + col * col_w
            yy = y - row * 15.5
            cov = w[0] in COVERED
            c.setFillColor(AZ_L if cov else FAINT); c.setFont("MonoB", 7.4)
            c.drawString(x, yy, f"{w[0]:02d}")
            c.setFillColor(TXT if cov else MUTED); c.setFont("MR", 8.2)
            c.drawString(x + 22, yy, w[2])
            if cov:
                dot(c, x + 22 + tw(w[2], "MR", 8.2) + 6, yy + 2.8, 2.1, AZ_L)
            c.linkRect("", f"w{w[0]}", (x, yy - 3, x + col_w - 10, yy + 9), relative=0, thickness=0)
        y -= rows * 15.5 + 12

    # --- Как читать гайд ---
    legend_h = 330
    if y - legend_h < bottom:
        d.next(); y = start_page(False)
    y -= 14
    c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(M, y + 8, PW - M, y + 8)
    y -= 22
    c.setFillColor(WHITE); c.setFont("MB", 18); c.drawString(M, y, S["legend_heading"])
    c.bookmarkPage("legend", fit="XYZ", left=0, top=y + 30); c.addOutlineEntry(S["bm_legend"], "legend", level=0)
    y -= 26

    def block(y, title, lines_spec):
        spaced(c, M, y, title, "MS", 6.8, AZ_L, 0.7)
        y -= 15
        for kind, color, label, text in lines_spec:
            x = M
            if kind == "dot":
                dot(c, x + 3, y + 3, 2.6, color)
                spaced(c, x + 11, y + 0.5, label, "MS", 6.4, color, 0.55)
                x = M + 78
            lines = simpleSplit(text, "MR", 8.6, PW - M - x)
            c.setFillColor(TXT); c.setFont("MR", 8.6)
            for ln in lines:
                c.drawString(x, y, ln); y -= 12.4
            y -= 4
        return y - 8

    y = block(y, S["legend_toolsets"], [
        ("dot", GREEN, S["core_label"], S["legend_core_text"]),
        ("dot", MUTED, S["extended_label"], S["legend_extended_text"]),
    ])
    spaced(c, M, y, S["legend_badges"], "MS", 6.8, AZ_L, 0.7)
    y -= 22
    x = M
    for course, label in S["legend_badge_chips"]:
        x += chip(c, x, y, chip_text(course, label), COURSES[course][1]) + 8
    y -= 16
    txt = S["legend_badge_note"].format(n=len(COVERED))
    c.setFillColor(TXT); c.setFont("MR", 8.6)
    for ln in simpleSplit(txt, "MR", 8.6, PW - 2 * M):
        c.drawString(M, y, ln); y -= 12.4
    y -= 12
    y = block(y, S["legend_prompts"], [
        ("txt", None, None, S["legend_prompt_text"]),
    ])
    y = block(y, S["legend_sections"], [
        ("txt", None, None, S["legend_sections_text"]),
    ])
    d.next()


def divider(d, sec):
    c = d.c
    no, name, title, off = sec
    items = [w for w in W if w[1] == no]
    cov = [w for w in items if w[0] in COVERED]
    bg(c)
    c.setFillColor(AZ); c.rect(0, 0, 6, PH, stroke=0, fill=1)
    c.drawImage(SIGN, PW - M - 70, PH - 140, 70, 70, mask="auto")
    c.setFillColor(BIGNUM); c.setFont("MB", 190); c.drawString(M - 6, PH / 2 - 210, no)
    c.setFillColor(WHITE); c.setFont("MB", 30)
    y = PH / 2 + 110
    for ln in title.split("\n"):
        c.drawString(M, y, ln.upper()); y -= 38
    y += 14
    c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(M, y, M + 150, y)
    y -= 20
    count_key = "divider_count_many" if len(items) >= 5 else "divider_count_one"
    spaced(c, M, y, S[count_key].format(n=len(items)), "MonoB", 7.2, AZ_L, 0.7)
    y -= 22
    if off:
        c.setFillColor(HexColor("#0D1E35")); c.setStrokeColor(MUTED); c.setLineWidth(0.6)
        bw = tw(S["divider_outside"], "MS", 7) + 0.6 * 19 + 24
        c.roundRect(M, y - 6, bw, 18, 9, stroke=1, fill=1)
        spaced(c, M + 12, y - 0.5, S["divider_outside"], "MS", 7, TXT, 0.6)
        y -= 26
        note = S["divider_note_off"].format(off=off)
    else:
        note = S["divider_note_cover"].format(cov=len(cov), total=len(items))
    c.setFillColor(MUTED); c.setFont("MR", 8.6)
    for ln in simpleSplit(note, "MR", 8.6, 300):
        c.drawString(M, y, ln); y -= 12.4
    c.bookmarkPage(f"sec{no}"); c.addOutlineEntry(f"{no}  " + title.replace("\n", " "), f"sec{no}", level=0)
    footer(c, d.page)
    d.next()


def section_pages(d, sec):
    c = d.c
    items = [w for w in W if w[1] == sec[0]]
    top_y = PH - 46 - 26
    bottom_y = 32 + 16
    gap = 12

    def new_page():
        bg(c); header(c, sec); footer(c, d.page)
        return top_y

    y = new_page()
    for w in items:
        h = card_layout(w)[0]
        if y - h < bottom_y:
            d.next(); y = new_page()
        draw_card(c, w, y)
        c.addOutlineEntry(f"{w[0]:02d}  {w[2]}", f"w{w[0]}", level=1)
        y -= h + gap
    d.next()


def final_page(d):
    c = d.c
    bg(c, BG_COVER)
    c.setFillColor(AZ); c.rect(0, PH - 6, PW, 6, stroke=0, fill=1)
    s = 210
    c.drawImage(ARTIFACT, (PW - s) / 2, PH - 40 - s, s, s, mask="auto")
    y = PH - 40 - s - 30
    c.setFillColor(WHITE); c.setFont("MB", 26); c.drawCentredString(PW / 2, y, S["final_heading"])
    y -= 22
    c.setFillColor(TXT); c.setFont("MR", 10)
    c.drawCentredString(PW / 2, y, S["final_lead1"])
    y -= 14
    c.drawCentredString(PW / 2, y, S["final_lead2"])
    y -= 30

    cards = S["final_courses"]

    # "which ways" line is computed from the data
    def ways_of(course):
        ns = [w[0] for w in W if any(cc == course for cc, _ in w[7])]
        return S["final_ways_prefix"] + ", ".join(f"{n:02d}" for n in ns)

    gapx = 16
    cw = (PW - 2 * M - gapx) / 2
    inner = cw - 36
    layouts = []
    for card in cards:
        on = simpleSplit(card["official"], "MR", 7.4, inner)
        ds = simpleSplit(card["desc"], "MR", 9, inner)
        layouts.append((on, ds))
    course_keys = [card["key"] for card in cards]
    ways_lines = [simpleSplit(ways_of(k), "MR", 7.2, inner) for k in course_keys]
    ch = max(16 + 12 + 26 + len(on) * 10 + 10 + len(ds) * 12.8 + 10 + 22 + 10 + len(wl) * 10 + 14 + 26 + 18
             for (on, ds), wl in zip(layouts, ways_lines))
    for i, (card, (on, ds), wl) in enumerate(zip(cards, layouts, ways_lines)):
        st, name, desc, facts, link, url = (card["eyebrow"], card["name"], card["desc"],
                                            card["facts"], card["link"], card["url"])
        x = M + i * (cw + gapx)
        y0 = y - ch
        c.setFillColor(CARD); c.setStrokeColor(LINE); c.setLineWidth(0.6)
        c.roundRect(x, y0, cw, ch, 10, stroke=1, fill=1)
        c.setFillColor(AZ); c.rect(x + 10, y - 2, cw - 20, 2, stroke=0, fill=1)
        yy = y - 26
        spaced(c, x + 18, yy, st, "MS", 6.6, MUTED, 0.7)
        yy -= 24
        c.setFillColor(WHITE); c.setFont("MB", 16.5); c.drawString(x + 18, yy, name)
        yy -= 16
        c.setFillColor(FAINT); c.setFont("MR", 7.4)
        for ln in on:
            c.drawString(x + 18, yy, ln); yy -= 10
        yy -= 8
        c.setFillColor(TXT); c.setFont("MR", 9)
        for ln in ds:
            c.drawString(x + 18, yy, ln); yy -= 12.8
        yy -= 8
        fx = x + 18
        for f in facts:
            fw = tw(f, "MS", 7.4) + S["fact_pad"]
            c.setFillColor(HexColor("#0F2A55")); c.setStrokeColor(HexColor("#24406E")); c.setLineWidth(0.6)
            c.roundRect(fx, yy - 5, fw, 16, 8, stroke=1, fill=1)
            c.setFillColor(WHITE); c.setFont("MS", 7.4); c.drawString(fx + S["fact_pad"] // 2, yy, f)
            fx += fw + S["fact_gap"]
        yy -= 24
        c.setFillColor(MUTED); c.setFont("MR", 7.2)
        for ln in wl:
            c.drawString(x + 18, yy, ln); yy -= 10
        # кнопка
        by = y0 + 16
        bw = cw - 36
        c.setFillColor(AZ); c.roundRect(x + 18, by, bw, 24, 12, stroke=0, fill=1)
        c.setFillColor(WHITE); c.setFont("MB", 9)
        c.drawCentredString(x + 18 + bw / 2, by + 8.2, f"{link}  →")
        c.linkURL(url, (x + 18, by, x + 18 + bw, by + 24), relative=0, thickness=0)
    # низ страницы
    brand_mark(c, M, 62, 26)
    c.setFillColor(MUTED); c.setFont("MR", 7.4)
    c.drawString(M, 36, S["final_footer"])
    c.setFillColor(AZ_L); c.setFont("MB", 9); c.drawRightString(PW - M, 58, S["header_site"])
    c.linkURL(S["brand_url"], (PW - M - 70, 52, PW - M, 68), relative=0, thickness=0)
    c.bookmarkPage("courses"); c.addOutlineEntry(S["bm_courses"], "courses", level=0)
    c.showPage()


def build():
    d = Doc(OUT)
    cover(d)
    toc_and_legend(d)
    for sec in SECTIONS:
        divider(d, sec)
        section_pages(d, sec)
    final_page(d)
    d.c.save()
    print("pages:", d.page, "->", OUT)


if __name__ == "__main__":
    build()
