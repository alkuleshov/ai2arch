/* Общая логика корпоративного конструктора AI2ARCH: расчёт, код программы, PDF.
   Данные модулей — в assets/corp-data.js (совпадают с Google Таблицей конструктора). */
(function (W) {
  const D = W.CORP_DATA;
  const REQ = W.CORP_REQ || null;            // реквизиты ИП для счёта и QR; null — счёт и QR не показываются
  const LV = ['Обзор', 'Практика', 'Внедрение'], FMT = ['Онлайн', 'Очно'];
  const byId = Object.fromEntries(D.modules.map(m => [m.id, m]));
  const CAT = D.modules.filter(m => !m.locked);
  const PRESET_KEYS = ['own', ...Object.keys(D.presets)];
  const isNum = v => typeof v === 'number';
  const rub = v => Math.round(v).toLocaleString('ru-RU') + ' ₽';
  const num = v => (Math.round(v * 10) / 10).toLocaleString('ru-RU');
  const clampN = n => Math.min(20, Math.max(1, n || 6));
  // до 6 человек — база; 7–10: +5% базы за человека; 11–20: +4% за человека (10 → ×1,2; 15 → ×1,4; 20 → ×1,6)
  const tierOf = n => { n = Math.max(1, Math.min(20, n)); const k = n <= 6 ? 1 : n <= 10 ? 1 + 0.05 * (n - 6) : 1.2 + 0.04 * (n - 10); return { from: n, to: n, k: Math.round(k * 10000) / 10000 }; };

  /* ---------- состояние и расчёт ---------- */
  function blank() {
    const m = {}; CAT.forEach(x => m[x.id] = { lvl: -1, own: false, fmt: 1, n: 6 });
    return { order: CAT.map(x => x.id), m, fmt: 1, n: 6, sup: 0, preset: 'own' };
  }
  function presetState(key) {
    const s = blank(); s.preset = key;
    Object.entries(D.presets[key].sel).forEach(([id, [l, f, n]]) => {
      const fi = FMT.indexOf(f);
      s.m[id] = { lvl: LV.indexOf(l), own: fi !== s.fmt || n !== s.n, fmt: fi, n };
    });
    return s;
  }
  const eff = (st, id) => { const c = st.m[id]; return c.own ? { fmt: c.fmt, n: c.n } : { fmt: st.fmt, n: st.n }; };
  function cost(st, id) {
    const x = byId[id], c = st.m[id];
    if (c.lvl < 0) return { on: false };
    const base = x.price[c.lvl], e = eff(st, id);
    if (!isNum(base)) return { on: true, req: true, ...e };
    return { on: true, req: false, price: base * D.fmt[e.fmt] * tierOf(e.n).k, hours: x.hours[c.lvl], ...e };
  }
  function totals(st) {
    let t = D.start.price, off = 0, on = D.start.hours, mods = 0, req = 0, maxN = 0, minN = 99;
    st.order.forEach(id => {
      const r = cost(st, id); if (!r.on) return; mods++; maxN = Math.max(maxN, r.n); minN = Math.min(minN, r.n);
      if (r.req) { req++; return; } t += r.price; if (r.fmt === 1) off += r.hours; else on += r.hours;
    });
    t += st.sup * D.support;
    return { t, off, on, mods, req, maxN, minN };
  }
  /* строки программы для документов */
  function rows(st) {
    const R = [{ name: D.start.name, depth: 'Обязательно', fmt: 'Онлайн', n: '', hours: D.start.hours, price: D.start.price, result: byId.M0 ? byId.M0.result : '' }];
    st.order.forEach(id => {
      const r = cost(st, id); if (!r.on) return; const x = byId[id];
      R.push({ name: x.name, depth: LV[st.m[id].lvl], fmt: FMT[r.fmt], n: r.n, hours: r.req ? null : r.hours, price: r.req ? null : r.price, result: x.result });
    });
    if (st.sup) R.push({ name: 'Сопровождение после обучения', depth: `${st.sup} мес.`, fmt: 'Онлайн', n: '', hours: null, price: st.sup * D.support, result: 'Чат и онлайн-сессия раз в месяц' });
    return R;
  }

  /* ---------- короткий код программы (для ссылки, PDF и Telegram) ----------
     Только символы A–Z a–z 0–9 - _, не длиннее 30 знаков. */
  const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
  function encode(st) {
    let bits = '';
    const put = (v, w) => { bits += v.toString(2).padStart(w, '0'); };
    put(1, 3); put(st.fmt, 1); put(st.n - 1, 5); put(st.sup, 4); put(Math.max(0, PRESET_KEYS.indexOf(st.preset)), 2);
    const on = st.order.filter(id => st.m[id].lvl >= 0);
    put(on.length, 4);
    on.forEach(id => { const c = st.m[id]; put(CAT.findIndex(x => x.id === id), 4); put(c.lvl, 2); put(c.own ? 1 : 0, 1); put(c.fmt, 1); put(c.n - 1, 5); });
    while (bits.length % 6) bits += '0';
    let s = ''; for (let i = 0; i < bits.length; i += 6) s += B64[parseInt(bits.slice(i, i + 6), 2)];
    return s;
  }
  function decode(code) {
    try {
      if (!/^[A-Za-z0-9_-]{3,64}$/.test(code)) return null;
      let bits = ''; for (const ch of code) bits += B64.indexOf(ch).toString(2).padStart(6, '0');
      let p = 0; const get = w => { if (p + w > bits.length) throw 0; const v = parseInt(bits.slice(p, p + w), 2); p += w; return v; };
      if (get(3) !== 1) return null;
      const s = blank(); s.fmt = get(1); s.n = clampN(get(5) + 1); s.sup = Math.min(12, get(4)); s.preset = PRESET_KEYS[get(2)] || 'own';
      const k = get(4), order = [];
      for (let i = 0; i < k; i++) {
        const idx = get(4), lvl = get(2), own = get(1), f = get(1), n = get(5) + 1, x = CAT[idx];
        if (!x || lvl > 2 || order.includes(x.id) || x.price[lvl] === 'нет') continue;
        order.push(x.id); s.m[x.id] = { lvl, own: !!own, fmt: f, n: clampN(n) };
      }
      CAT.forEach(x => { if (!order.includes(x.id)) order.push(x.id); }); s.order = order;
      return s;
    } catch (e) { return null; }
  }
  /* ссылки старого формата #p=2~… */
  function decodeLegacy(h) {
    try {
      const [v, f, n, sup, preset, mods] = h.split('~'); if (v !== '2') return null;
      const s = blank(); s.fmt = +f ? 1 : 0; s.n = clampN(+n); s.sup = Math.min(12, Math.max(0, +sup || 0));
      s.preset = PRESET_KEYS.includes(preset) ? preset : 'own';
      const order = [];
      mods.split('_').forEach(t => { const [i, l, o, ff, nn] = t.split('.'); const id = 'M' + i; if (!s.m[id]) return; order.push(id);
        const lvl = Math.min(2, Math.max(-1, (+l) - 1)); s.m[id] = { lvl: lvl >= 0 && byId[id].price[lvl] === 'нет' ? -1 : lvl, own: o === '1', fmt: +ff ? 1 : 0, n: clampN(+nn) }; });
      CAT.forEach(x => { if (!order.includes(x.id)) order.push(x.id); }); s.order = order; return s;
    } catch (e) { return null; }
  }
  function fromHash() {
    const h = decodeURIComponent(location.hash.slice(1));
    if (h.startsWith('c=')) return decode(h.slice(2));
    if (h.startsWith('p=')) return decodeLegacy(h.slice(2));
    return null;
  }
  /* номер программы: одинаковый для одинакового состава, по нему видно, что ссылка не изменена */
  function programId(code) {
    let h = 0x811c9dc5;
    for (const ch of code) { h ^= ch.charCodeAt(0); h = Math.imul(h, 0x01000193) >>> 0; }
    const A = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'; let s = '';
    for (let i = 0; i < 6; i++) { s += A[h & 31]; h >>>= 5; }
    return s.slice(0, 3) + '-' + s.slice(3);
  }
  const base = () => location.origin + location.pathname.replace(/[^/]*$/, '');
  const ext = () => /\.html$/.test(location.pathname) ? '.html' : '';
  const builderUrl = code => base() + 'corp' + ext() + '#c=' + code;
  const orderUrl = code => base() + 'corp-order' + ext() + '#c=' + code;

  /* ---------- QR по ГОСТ Р 56042-2014 (платёжное поручение в банковском приложении) ---------- */
  function payString(sum, purpose) {
    if (!REQ) return '';
    const clean = v => String(v).replace(/\|/g, ' ');
    return ['ST00012', `Name=${clean(REQ.name)}`, `PersonalAcc=${REQ.account}`, `BankName=${clean(REQ.bank)}`, `BIC=${REQ.bik}`,
      `CorrespAcc=${REQ.corr}`, `PayeeINN=${REQ.inn}`, `Sum=${Math.round(sum * 100)}`, `Purpose=${clean(purpose)}`].join('|');
  }
  function qrMatrix(text) {
    const q = W.qrcode(0, 'M'); W.qrcode.stringToBytes = W.qrcode.stringToBytesFuncs['UTF-8'];
    q.addData(text, 'Byte'); q.make(); return q;
  }
  function qrSvg(text) { return qrMatrix(text).createSvgTag({ cellSize: 4, margin: 2, scalable: true }); }
  function qrPng(text) {
    const q = qrMatrix(text), n = q.getModuleCount(), cell = 8, pad = 2 * cell, c = document.createElement('canvas');
    c.width = c.height = n * cell + pad * 2; const g = c.getContext('2d');
    g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height); g.fillStyle = '#000';
    for (let r = 0; r < n; r++) for (let k = 0; k < n; k++) if (q.isDark(r, k)) g.fillRect(pad + k * cell, pad + r * cell, cell, cell);
    return c.toDataURL('image/png');
  }

  /* ---------- PDF ---------- */
  function load(src) { return new Promise((ok, no) => { const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = no; document.head.appendChild(s); }); }
  let pdfReady = null;
  function pdfLib() {
    if (!pdfReady) pdfReady = load(base() + 'assets/vendor/pdfmake.min.js').then(() => load(base() + 'assets/vendor/vfs_fonts.js')).then(() => {
      if (W.pdfMake.addFonts) W.pdfMake.addFonts({ Roboto: { normal: 'Roboto-Regular.ttf', bold: 'Roboto-Medium.ttf', italics: 'Roboto-Italic.ttf', bolditalics: 'Roboto-MediumItalic.ttf' } });
      return W.pdfMake;
    });
    return pdfReady;
  }
  const today = () => new Date().toLocaleDateString('ru-RU');
  const NAVY = '#0A0F1A', MUTED = '#5B6475', LINE = '#E4E1D8', ACC = '#1A6BFF';

  function serviceTable(st) {
    const R = rows(st), T = totals(st);
    const head = ['№', 'Услуга', 'Глубина', 'Формат', 'Чел.', 'Часы', 'Сумма'].map(t => ({ text: t, bold: true, color: MUTED, fontSize: 8 }));
    const body = [head, ...R.map((r, i) => [String(i + 1), { text: r.name, bold: true }, r.depth, r.fmt, r.n ? String(r.n) : '—', r.hours == null ? '—' : num(r.hours), { text: r.price == null ? 'по запросу' : rub(r.price), alignment: 'right', noWrap: true }])];
    body.push([{ text: 'Итого', bold: true, colSpan: 5 }, {}, {}, {}, {}, { text: num(T.off + T.on), bold: true }, { text: rub(T.t), bold: true, alignment: 'right', noWrap: true }]);
    return {
      table: { headerRows: 1, widths: [14, '*', 64, 42, 26, 30, 62], body },
      layout: { hLineWidth: (i, n) => (i === 0 || i === 1 || i === n.table.body.length - 1 || i === n.table.body.length) ? 0.8 : 0.3,
        vLineWidth: () => 0, hLineColor: () => LINE, paddingTop: () => 5, paddingBottom: () => 5 },
      fontSize: 9, margin: [0, 6, 0, 6]
    };
  }
  function docBase(title, sub, content) {
    return {
      pageSize: 'A4', pageMargins: [42, 48, 42, 54], defaultStyle: { font: 'Roboto', fontSize: 9.5, color: NAVY, lineHeight: 1.25 },
      info: { title, author: 'AI2ARCH' },
      footer: (p, n) => ({ columns: [{ text: 'AI2ARCH · лаборатория проектного интеллекта · ai2arch.ru/corp', color: MUTED, fontSize: 7.5 }, { text: `${p} / ${n}`, alignment: 'right', color: MUTED, fontSize: 7.5 }], margin: [42, 16, 42, 0] }),
      content: [
        { text: 'AI2ARCH · ЛАБОРАТОРИЯ ПРОЕКТНОГО ИНТЕЛЛЕКТА', color: ACC, fontSize: 7.5, bold: true, characterSpacing: 1 },
        { text: title, fontSize: 18, bold: true, margin: [0, 6, 0, 2] },
        { text: sub, color: MUTED, margin: [0, 0, 0, 10] },
        ...content
      ]
    };
  }
  function programDoc(st, code) {
    const id = programId(code), T = totals(st), R = rows(st);
    const content = [
      serviceTable(st),
      { text: 'НДС не облагается (УСН). Стоимость, дни и время занятий фиксируются в счёте-договоре после встречи.', color: MUTED, fontSize: 8.5, margin: [0, 0, 0, 12] },
      { text: 'Что получит бюро', bold: true, fontSize: 11, margin: [0, 4, 0, 6] },
      { ul: R.filter(r => r.result).map(r => ({ text: [{ text: r.name + ' — ', bold: true }, r.result] })), margin: [0, 0, 0, 12] },
      { text: 'Как проходит работа', bold: true, fontSize: 11, margin: [0, 4, 0, 6] },
      { ol: [
        'Заявка: программа собрана в конструкторе, номер программы — ' + id + '.',
        'Встреча онлайн 40–60 минут: задачи бюро, софт, программа и смета; согласуем дни, время занятий и состав команды.',
        'Оплата по счёту-договору или QR-коду. Закрывающие документы — после обучения.',
        'Обучение строго в дни и время, указанные в счёте-договоре.'
      ], margin: [0, 0, 0, 12] },
      { text: [{ text: 'Открыть программу в конструкторе', link: builderUrl(code), color: ACC, decoration: 'underline' }, { text: '   ·   Telegram: @alkuleshov', color: MUTED }] }
    ];
    return docBase('Программа корпоративного обучения ИИ', `№ ${id} от ${today()} · ${T.mods} модулей · ${num(T.off)} ч очно, ${num(T.on)} ч онлайн`, content);
  }
  function invoiceDoc(st, code, f) {
    const id = programId(code), T = totals(st), pre = Math.round(T.t * D.prepay), no = `${id}`;
    const purpose = `Оплата по счёту-договору № ${no} от ${today()} за информационно-консультационные услуги. НДС не облагается (УСН)`;
    const party = (label, lines) => ({ stack: [{ text: label, color: MUTED, fontSize: 8, bold: true, margin: [0, 0, 0, 2] }, ...lines.filter(Boolean).map(t => ({ text: t }))] });
    const terms = [
      `Исполнитель оказывает Заказчику информационно-консультационные услуги в форме практических семинаров по применению искусственного интеллекта в проектной работе по программе, указанной в таблице.`,
      `Занятия проводятся в дни и время: ${f.dates}. Формат и состав участников — по таблице. Изменение дат возможно по согласованию сторон.`,
      `Настоящий счёт является офертой. Оплата Заказчиком счёта означает акцепт оферты и заключение договора на изложенных условиях (п. 3 ст. 434, п. 3 ст. 438 ГК РФ).`,
      `Порядок оплаты: 100% (${rub(pre)}) — в течение 5 рабочих дней с даты счёта и до первого занятия. НДС не облагается.`,
      `Занятие переносится без доплаты, если Заказчик предупредил Исполнителя не позднее чем за 2 рабочих дня. Оплаченные и не проведённые по вине Исполнителя занятия проводятся в другие согласованные даты или их стоимость возвращается. Если Заказчик отказывается от занятий до их начала, Исполнитель возвращает стоимость непроведённых занятий за вычетом фактически понесённых расходов (ст. 782 ГК РФ).`,
      `Конфиденциальность обоюдная. Исполнитель не разглашает информацию о проектах, данных, клиентах и внутренней работе Заказчика, использует материалы Заказчика только на занятиях и не называет Заказчика своим клиентом без его согласия. Заказчик и его сотрудники не разглашают содержание и методику занятий и материалы Исполнителя, не записывают занятия и не публикуют их, в том числе в социальных сетях и видео. Публикация кейса возможна только с согласия обеих сторон, достаточно сообщения в мессенджере или по почте. Правила работы с данными в облачных ИИ стороны согласуют до первого занятия; выбор ИИ-сервисов и загружаемые в них данные остаются на стороне Заказчика. Исполнитель не хранит материалы проектов Заказчика после завершения программы. Конфиденциальной не считается общедоступная информация и информация, раскрытие которой требует закон. Обязательство действует 3 года после последнего занятия. Заказчик отвечает за соблюдение условий своими сотрудниками.`,
      `Инструкции, промпты, скрипты и чек-листы, созданные на занятиях, Заказчик использует внутри компании без ограничений, передача и публикация за пределами компании — в рамках условий о конфиденциальности.`,
      `После последнего занятия Исполнитель направляет акт оказанных услуг. Если в течение 5 рабочих дней Заказчик не направил мотивированных возражений, услуги считаются принятыми. Документ об обучении не выдаётся.`,
      `Споры решаются переговорами, при недостижении согласия — в суде по месту нахождения Исполнителя.`
    ];
    const content = [
      { columns: [
        party('ИСПОЛНИТЕЛЬ', [REQ.name, `ИНН ${REQ.inn}`, REQ.ogrnip ? `ОГРНИП ${REQ.ogrnip}` : '', `Р/с ${REQ.account}`, `${REQ.bank}`, `БИК ${REQ.bik}, к/с ${REQ.corr}`]),
        party('ЗАКАЗЧИК', [f.customer, f.inn ? `ИНН ${f.inn}` : ''])
      ], columnGap: 20, margin: [0, 0, 0, 8] },
      serviceTable(st),
      { columns: [
        { width: '*', stack: [
          { text: `Всего к оплате: ${rub(T.t)}, НДС не облагается.`, bold: true },
          { text: `К оплате: ${rub(pre)}. Отсканируйте QR-код в банковском приложении — реквизиты и сумма заполнятся сами.`, color: MUTED, margin: [0, 4, 0, 0] },
          T.req ? { text: `Модули с ценой по запросу (${T.req}) в сумму не входят.`, color: MUTED, margin: [0, 4, 0, 0] } : ''
        ] },
        { width: 110, image: qrPng(payString(pre, purpose)), fit: [110, 110] }
      ], columnGap: 16, margin: [0, 4, 0, 12] },
      { text: 'Условия', bold: true, fontSize: 11, margin: [0, 2, 0, 6] },
      { ol: terms, fontSize: 8.8, margin: [0, 0, 0, 16] },
      { columns: [{ text: `Исполнитель ____________________ ${REQ.short || REQ.name}`, margin: [0, 10, 0, 0] }] }
    ];
    return docBase(`Счёт-договор № ${no}`, `от ${today()} · оферта на оказание информационно-консультационных услуг`, content);
  }
  async function downloadPdf(st, kind, fields) {
    const pm = await pdfLib(), code = encode(st), id = programId(code);
    const dd = kind === 'invoice' ? invoiceDoc(st, code, fields) : programDoc(st, code);
    const name = (kind === 'invoice' ? 'Счёт-договор_AI2ARCH_' : 'Программа_AI2ARCH_') + id + '.pdf';
    const doc = pm.createPdf(dd);
    await doc.download(name);
  }

  W.Corp = { D, REQ, LV, FMT, byId, CAT, isNum, rub, num, clampN, tierOf, blank, presetState, eff, cost, totals, rows,
    encode, decode, decodeLegacy, fromHash, programId, builderUrl, orderUrl, payString, qrSvg, downloadPdf, pdfLib };
})(window);
