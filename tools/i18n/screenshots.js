#!/usr/bin/env node
/* Playwright check for the English pages: desktop/mobile screenshots,
   horizontal overflow at 320 px, console errors and failed local requests.

   Usage:
     python3 -m http.server 8765 --bind 127.0.0.1   # from the repo root
     node tools/i18n/screenshots.js [url ...]
*/
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = process.env.BASE_URL || 'http://127.0.0.1:8765';
const OUT = process.env.SHOT_DIR || '/tmp/ai2arch-en-shots';
const pages = process.argv.slice(2).length
  ? process.argv.slice(2)
  : ['/en/', '/en/archi.html', '/en/redev.html', '/en/53.html'];

const slug = u => u.replace(/^\//, '').replace(/\/$/, '') || 'root';

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const exe = process.env.CHROME_PATH || '/root/.cache/ms-playwright/chromium-1148/chrome-linux/chrome';
  const browser = await chromium.launch(fs.existsSync(exe) ? { executablePath: exe } : {});
  const report = [];

  for (const url of pages) {
    const entry = { url, desktop: {}, mobile: {}, narrow: {}, console: [], failed: [] };
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();

    page.on('console', msg => {
      if (msg.type() === 'error') entry.console.push(msg.text());
    });
    page.on('pageerror', err => entry.console.push('pageerror: ' + err.message));
    page.on('requestfailed', req => {
      if (req.url().startsWith(BASE)) entry.failed.push(req.url() + ' :: ' + (req.failure() || {}).errorText);
    });
    page.on('response', res => {
      if (res.url().startsWith(BASE) && res.status() >= 400)
        entry.failed.push(res.url() + ' :: HTTP ' + res.status());
    });

    await page.goto(BASE + url, { waitUntil: 'load', timeout: 45000 });
    await page.waitForTimeout(1200);
    entry.desktop = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      title: document.title,
      lang: document.documentElement.lang,
      switcher: (document.querySelector('.lang-switch') || {}).textContent || null
    }));
    await page.screenshot({ path: path.join(OUT, slug(url) + '-1440.png'), fullPage: false });
    await page.screenshot({ path: path.join(OUT, slug(url) + '-1440-full.png'), fullPage: true });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(500);
    entry.mobile = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth
    }));
    await page.screenshot({ path: path.join(OUT, slug(url) + '-390.png'), fullPage: false });
    await page.screenshot({ path: path.join(OUT, slug(url) + '-390-full.png'), fullPage: true });

    await page.setViewportSize({ width: 320, height: 800 });
    await page.waitForTimeout(500);
    entry.narrow = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
    }));

    await context.close();
    report.push(entry);
  }

  await browser.close();
  fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
  let bad = 0;
  for (const r of report) {
    const over = r.desktop.scrollWidth > r.desktop.clientWidth + 1 ||
                 r.mobile.scrollWidth > r.mobile.clientWidth + 1 || r.narrow.overflow;
    if (over || r.console.length || r.failed.length) bad++;
    console.log(`${r.url}: lang=${r.desktop.lang} desktop=${r.desktop.clientWidth}/${r.desktop.scrollWidth} ` +
      `mobile=${r.mobile.clientWidth}/${r.mobile.scrollWidth} narrow320=${r.narrow.overflow ? 'OVERFLOW' : 'ok'} ` +
      `console=${r.console.length} failed=${r.failed.length}`);
    r.console.slice(0, 5).forEach(e => console.log('  console:', e.slice(0, 200)));
    r.failed.slice(0, 5).forEach(e => console.log('  failed:', e.slice(0, 200)));
  }
  console.log(`Screenshots: ${OUT}`);
  process.exit(bad ? 1 : 0);
})();
