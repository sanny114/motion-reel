import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
const [mode, ...rest] = process.argv.slice(2);
const url = 'file://' + process.cwd() + '/live.html?render';
const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
async function page() {
  const p = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('console', m => console.log('console:', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(url); await p.evaluate(() => window.ready); return p;
}
const grab = (p, t, type = 'image/png', q) => p.evaluate(([t, type, q]) => { renderAt(t); return document.getElementById('c').toDataURL(type, q).split(',')[1]; }, [t, type, q]);
if (mode === 'stills') {
  fs.mkdirSync('stills', { recursive: true });
  const p = await page();
  for (const t of rest.map(Number)) fs.writeFileSync(`stills/t${t.toFixed(2)}.png`, Buffer.from(await grab(p, t), 'base64'));
} else {
  const fps = 120, N = 15 * fps, W = Number(rest[0] || 4);
  fs.mkdirSync('frames', { recursive: true });
  const t0 = Date.now();
  await Promise.all(Array.from({ length: W }, async (_, w) => {
    const p = await page();
    for (let i = w; i < N; i += W) {
      fs.writeFileSync(`frames/f${String(i).padStart(5, '0')}.png`, Buffer.from(await grab(p, i / fps), 'base64'));
      if (i % 120 === 0) console.log('frame', i, ((Date.now() - t0) / 1000).toFixed(1) + 's');
    }
  }));
}
await browser.close();
