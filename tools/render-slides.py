#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Снимает слайды колоды в WebP 3200 и 1600 px для лонгрида.

Требует Node.js и Playwright, установленный в общих node_modules проекта.
По умолчанию снимает redev-income.html в images/slides/income.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / 'redev-income.html'
OUT = ROOT / 'images' / 'slides' / 'income'
NODE_MODULES = Path(os.environ.get('NODE_PATH', '/srv/projects/node_modules'))
CHROMIUM = Path('/root/.cache/ms-playwright/chromium-1148/chrome-linux/chrome')

JS = r'''
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const deck = process.argv[1], out = process.argv[2], chromiumPath = process.argv[3];
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ executablePath: chromiumPath });
  const page = await browser.newPage({ viewport: { width: 3208, height: 1808 } });
  await page.goto('file://' + deck);
  await page.waitForTimeout(500);
  await page.evaluate(() => document.fonts.ready);
  const total = await page.evaluate(() => document.querySelectorAll('.slide').length);
  async function webp(png, w, h) {
    return await page.evaluate(async ({png,w,h}) => {
      const img = new Image();
      img.src = 'data:image/png;base64,' + png;
      await new Promise((res, rej) => { img.onload = res; img.onerror = rej; });
      const c = document.createElement('canvas'); c.width = w; c.height = h;
      const ctx = c.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0,0,w,h);
      ctx.drawImage(img, 0, 0, w, h);
      return c.toDataURL('image/webp', 0.9).split(',')[1];
    }, {png,w,h});
  }
  for (let i = 0; i < total; i++) {
    await page.evaluate((i) => {
      const all = document.querySelectorAll('.slide');
      all.forEach(s => s.classList.remove('active'));
      const s = all[i];
      s.classList.add('active');
      s.style.animation = 'none';
      s.querySelectorAll('*').forEach(e => { e.style.animation='none'; e.style.transition='none'; });
    }, i);
    await page.waitForTimeout(80);
    const r = await page.evaluate(() => document.getElementById('stage').getBoundingClientRect().toJSON());
    const png = await page.screenshot({ clip: { x:r.x, y:r.y, width:r.width, height:r.height } }).then(b => Buffer.from(b).toString('base64'));
    const name = String(i+1).padStart(2,'0');
    fs.writeFileSync(out + '/' + name + '.webp', Buffer.from(await webp(png,3200,1800),'base64'));
    fs.writeFileSync(out + '/' + name + '-1600.webp', Buffer.from(await webp(png,1600,900),'base64'));
    process.stdout.write(name + ' ');
  }
  await browser.close();
  console.log('\nslides: ' + total);
})();
'''

def main():
    if not DECK.exists():
        sys.exit(f'Не найдена колода: {DECK}')
    if not CHROMIUM.exists():
        sys.exit(f'Не найден Chromium: {CHROMIUM}')
    env = dict(os.environ)
    env['NODE_PATH'] = str(NODE_MODULES)
    cmd = ['node', '-e', JS, str(DECK), str(OUT), str(CHROMIUM)]
    subprocess.run(cmd, check=True, env=env)

if __name__ == '__main__':
    main()
