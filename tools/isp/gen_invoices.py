#!/usr/bin/env python3
"""Счета-договоры для бюро ИСП: два блока по отдельному документу (оферта: оплата = акцепт).
Реквизиты исполнителя — из assets/corp-req.js. Запуск: python3 tools/isp/gen_invoices.py [папка_вывода]
Требуется: pip install qrcode[pil]; Playwright + Chrome.
Реквизиты заказчика (CUSTOMER, CUSTOMER_INN) заполнить, когда бюро пришлёт их; пока в документе — строки для заполнения."""
import re, io, base64, os, sys, html
import qrcode
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs"

# ---------- что подставляется вручную ----------
CUSTOMER = ""          # например: ООО «ИСП», г. Ростов-на-Дону
CUSTOMER_INN = ""      # ИНН заказчика
NBSP = " "

# Блоки: строки — (название, глубина, формат, чел., часы, цена по прайсу)
BLOCKS = [
    dict(
        no="ИСП-1", date="30.11.2026", title="Блок 1 · «Концепция и подача» · декабрь 2026", total=120500,
        dates=["пт 4 декабря, 10:00–10:30 (онлайн, Яндекс Телемост)", "пн 7 декабря, 10:00–11:30", "вт 8 декабря, 10:00–11:30 и 12:00–15:00",
               "чт 10 декабря, 10:00–11:30 и 12:00–13:30", "пт 11 декабря, 10:00–13:00", "резерв на переносы — 14–18 декабря"],
        rows=[("Старт: рабочее место и правила работы с данными", "Обязательно", "Онлайн", "", "0,5", 6000),
              ("Концепции и ИИ-ТЗ", "Практика", "Очно", "6", "3", 28600),
              ("Визуализации", "Практика", "Очно", "6", "3", 28600),
              ("Презентации и подача", "Обзор", "Очно", "6", "1,5", 10400),
              ("Тексты и документы", "Обзор", "Очно", "10", "1,5", 12480),
              ("Нормы и проверка документации", "Практика", "Очно", "10", "3", 37440)],
        note="Блок 1 из 2. Блок 2 («Участок, модель, команда», февраль 2027) оплачивается отдельным счётом-договором.",
    ),
    dict(
        no="ИСП-2", date="25.01.2027", title="Блок 2 · «Участок, модель, команда» · февраль 2027", total=119500,
        dates=["пн 8 февраля, 10:00–12:00", "вт 9 февраля, 10:00–13:00", "ср 10 февраля, 10:00–11:30 и 12:00–13:30",
               "чт 11 февраля, 10:00–11:30", "пн 15 февраля, 10:00–12:00", "ср 24 февраля, 10:00–12:00"],
        rows=[("Анализ участка (QGIS)", "Внедрение", "Очно", "6", "4", 52000),
              ("Revit + ИИ", "Практика", "Очно", "6", "3", 33800),
              ("ИИ для ГИПа", "Обзор", "Очно", "4", "1,5", 10400),
              ("ИИ для инженерных разделов", "Обзор", "Очно", "6", "1,5", 10400),
              ("AutoCAD + ИИ", "Обзор", "Очно", "6", "1,5", 10400),
              ("Итоговая сессия", "Практика", "Очно", "15", "2", 27300)],
        note="Блок 2 из 2. Блок 1 («Концепция и подача», декабрь 2026) оплачивается отдельным счётом-договором № ИСП-1.",
    ),
]
PROGRAM_TOTAL = sum(b["total"] for b in BLOCKS)   # 240 000 ₽

# ---------- реквизиты исполнителя ----------
req_js = open(os.path.join(ROOT, "assets", "corp-req.js"), encoding="utf-8").read()
REQ = dict(re.findall(r"(\w+):\s*'([^']*)'", req_js))

def rub(v): return f"{int(round(v)):,}".replace(",", NBSP) + NBSP + "₽"
def e(s): return html.escape(s, quote=False)

def qr_data_uri(text):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    q.add_data(text.encode("utf-8")); q.make(fit=True)
    buf = io.BytesIO(); q.make_image(fill_color="#0A0F1A", back_color="white").save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def pay_string(sum_rub, purpose):
    clean = lambda v: str(v).replace("|", " ")
    return "|".join(["ST00012", f"Name={clean(REQ['name'])}", f"PersonalAcc={REQ['account']}", f"BankName={clean(REQ['bank'])}",
                     f"BIC={REQ['bik']}", f"CorrespAcc={REQ['corr']}", f"PayeeINN={REQ['inn']}", f"Sum={sum_rub * 100}", f"Purpose={clean(purpose)}"])

def terms(b, list_total, disc):
    return [
        "Исполнитель оказывает Заказчику информационно-консультационные услуги в форме практических семинаров по применению искусственного интеллекта в проектной работе по программе, указанной в таблице. Программа проводится в два блока, настоящий счёт-договор относится к блоку, указанному в заголовке.",
        f"Занятия проводятся в дни и время: {'; '.join(b['dates'])}. Время начала и окончания предварительное, окончательное подтверждается Исполнителем не позднее чем за 3 рабочих дня до блока. Час занятия — астрономический (60 минут). Формат и состав участников — по таблице. Изменение дат возможно по согласованию сторон.",
        "Настоящий счёт является офертой. Оплата Заказчиком счёта означает акцепт оферты и заключение договора на изложенных условиях (п. 3 ст. 434, п. 3 ст. 438 ГК РФ).",
        f"Порядок оплаты: 100% ({rub(b['total'])}) — в течение 5 рабочих дней с даты счёта и до первого занятия блока. НДС не облагается.",
        f"Стоимость блока указана с учётом скидки {rub(disc)} от прайса ({rub(list_total)}). Скидка предоставлена по условиям пилотной программы: Заказчик даёт письменное согласие на публикацию кейса по итогам программы и отзыв, предоплата каждого блока — 100%. Общая стоимость программы из двух блоков — {rub(PROGRAM_TOTAL)}. Содержание кейса и отзыва согласуется с Заказчиком до публикации.",
        "Занятие переносится без доплаты, если Заказчик предупредил Исполнителя не позднее чем за 2 рабочих дня. Оплаченные и не проведённые по вине Исполнителя занятия проводятся в другие согласованные даты или их стоимость возвращается. Если Заказчик отказывается от занятий до их начала, Исполнитель возвращает стоимость непроведённых занятий за вычетом фактически понесённых расходов (ст. 782 ГК РФ).",
        "Конфиденциальность обоюдная. Исполнитель не разглашает информацию о проектах, данных, клиентах и внутренней работе Заказчика, использует материалы Заказчика только на занятиях и не называет Заказчика своим клиентом без его согласия. Заказчик и его сотрудники не разглашают содержание и методику занятий и материалы Исполнителя, не записывают занятия и не публикуют их, в том числе в социальных сетях и видео. Публикация кейса возможна только с согласия обеих сторон, достаточно сообщения в мессенджере или по почте. Правила работы с данными в облачных ИИ стороны согласуют до первого занятия; выбор ИИ-сервисов и загружаемые в них данные остаются на стороне Заказчика. Исполнитель не хранит материалы проектов Заказчика после завершения программы. Конфиденциальной не считается общедоступная информация и информация, раскрытие которой требует закон. Обязательство действует 3 года после последнего занятия. Заказчик отвечает за соблюдение условий своими сотрудниками.",
        "Инструкции, промпты, скрипты и чек-листы, созданные на занятиях, Заказчик использует внутри компании без ограничений, передача и публикация за пределами компании — в рамках условий о конфиденциальности.",
        "После последнего занятия блока Исполнитель направляет акт оказанных услуг. Если в течение 5 рабочих дней Заказчик не направил мотивированных возражений, услуги считаются принятыми. Документ об обучении не выдаётся.",
        "Споры решаются переговорами, при недостижении согласия — в суде по месту нахождения Исполнителя.",
    ]

CSS = """
@page{size:A4;margin:14mm 14mm 16mm}
*{box-sizing:border-box}
body{margin:0;font-family:'Inter','Roboto','DejaVu Sans',sans-serif;font-size:9.2pt;line-height:1.32;color:#0A0F1A}
.k{font-size:7pt;font-weight:700;letter-spacing:.1em;color:#1A6BFF}
h1{font-size:18pt;margin:5px 0 2px;letter-spacing:-.02em}
.sub{color:#5B6475;margin-bottom:10px}
.cols{display:flex;gap:22px;margin-bottom:10px}.cols>div{flex:1}
.lb{font-size:7.5pt;font-weight:700;color:#5B6475;margin-bottom:2px}
.fill{display:inline-block;min-width:60mm;border-bottom:1px solid #0A0F1A;height:1.1em}
table{width:100%;border-collapse:collapse;margin:6px 0}
th{font-size:7.5pt;color:#5B6475;text-align:left;padding:4px 4px 5px 0;border-bottom:1.2px solid #0A0F1A}
td{padding:5px 4px 5px 0;border-bottom:.5px solid #E4E1D8;vertical-align:top}
td.r,th.r{text-align:right;white-space:nowrap}
tr.tot td{border-top:1.2px solid #0A0F1A;border-bottom:0;font-weight:700;font-size:10pt}
tr.dc td{color:#1A6BFF}
.pay{display:flex;gap:16px;align-items:center;margin:8px 0 12px;break-inside:avoid}.pay img{width:104px;height:104px}
.pay .m{color:#5B6475;margin-top:4px}
h2{font-size:11pt;margin:10px 0 5px}
ol{margin:0;padding-left:16px;font-size:8.4pt}ol li{margin-bottom:4px}
.note{background:#F6F4F0;border-left:3px solid #1A6BFF;padding:6px 9px;margin:6px 0;font-size:8.4pt}
.sign{margin-top:22px;display:flex;justify-content:space-between;gap:30px;break-inside:avoid}.sign>div{flex:1;border-top:1px solid #0A0F1A;padding-top:3px;font-size:8pt;color:#5B6475}
"""

def doc(b):
    list_total = sum(r[5] for r in b["rows"]); disc = list_total - b["total"]
    purpose = f"Оплата по счёту-договору № {b['no']} от {b['date']} за информационно-консультационные услуги. НДС не облагается (УСН)"
    hours = sum(float(r[4].replace(",", ".")) for r in b["rows"])
    hours_s = (f"{hours:g}").replace(".", ",")
    rows = "".join(f"<tr><td>{i}</td><td><b>{e(r[0])}</b></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3] or '—'}</td><td>{r[4]}</td><td class='r'>{rub(r[5])}</td></tr>" for i, r in enumerate(b["rows"], 1))
    cust = (f"<b>{e(CUSTOMER)}</b>" if CUSTOMER else "<span class='fill'></span><br><span style='color:#5B6475;font-size:7.5pt'>наименование, адрес</span>")
    inn = (f"ИНН {e(CUSTOMER_INN)}" if CUSTOMER_INN else "ИНН <span class='fill' style='min-width:36mm'></span>")
    tl = "".join(f"<li>{e(t)}</li>" for t in terms(b, list_total, disc))
    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="k">AI2ARCH · ЛАБОРАТОРИЯ ПРОЕКТНОГО ИНТЕЛЛЕКТА</div>
<h1>Счёт-договор № {b['no']}</h1>
<div class="sub">от {b['date']} · оферта на оказание информационно-консультационных услуг<br>{e(b['title'])}</div>
<div class="cols">
 <div><div class="lb">ИСПОЛНИТЕЛЬ</div>{e(REQ['name'])}<br>ИНН {REQ['inn']}<br>ОГРНИП {REQ['ogrnip']}<br>Р/с {REQ['account']}<br>{e(REQ['bank'])}<br>БИК {REQ['bik']}, к/с {REQ['corr']}</div>
 <div><div class="lb">ЗАКАЗЧИК</div>{cust}<br>{inn}</div>
</div>
<table><thead><tr><th>№</th><th>Услуга</th><th>Глубина</th><th>Формат</th><th>Чел.</th><th>Часы</th><th class="r">Сумма</th></tr></thead><tbody>
{rows}
<tr><td colspan="6">Итого по прайсу, {hours_s}{NBSP}ч</td><td class="r">{rub(list_total)}</td></tr>
<tr class="dc"><td colspan="6">Скидка по условиям пилотной программы</td><td class="r">−{rub(disc)}</td></tr>
<tr class="tot"><td colspan="6">Всего к оплате, НДС не облагается</td><td class="r">{rub(b['total'])}</td></tr>
</tbody></table>
<div class="pay"><img src="{qr_data_uri(pay_string(b['total'], purpose))}"><div><b>К оплате: {rub(b['total'])}.</b><div class="m">Отсканируйте QR-код в банковском приложении — реквизиты и сумма заполнятся сами.</div></div></div>
<div class="note">{e(b['note'])}</div>
<h2>Условия</h2><ol>{tl}</ol>
<div class="sign"><div>Исполнитель: {e(REQ['name'])} / {e(REQ.get('short',''))}</div></div>
</body></html>"""

def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for b in BLOCKS:
            pg = br.new_page(); pg.set_content(doc(b)); pg.wait_for_timeout(300)
            path = os.path.join(OUT, f"Счёт-договор_{b['no']}_AI2ARCH.pdf")
            pg.pdf(path=path, format="A4", print_background=True, display_header_footer=True,
                   header_template="<span></span>",
                   footer_template='<div style="width:100%;font-size:7px;color:#5B6475;padding:0 14mm;display:flex;justify-content:space-between"><span>AI2ARCH · лаборатория проектного интеллекта · ai2arch.ru</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
                   margin=dict(top="14mm", bottom="16mm", left="14mm", right="14mm"))
            print(path, rub(b["total"]))
        br.close()
    assert PROGRAM_TOTAL == 240000, PROGRAM_TOTAL

if __name__ == "__main__":
    main()
