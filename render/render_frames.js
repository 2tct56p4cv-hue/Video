const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const FPS = 25; const tl = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../timeline.json'), 'utf8'));
  const total = tl.total + 1.0; const nFrames = Math.ceil(total * FPS);
  const outDir = path.resolve(__dirname, '../frames'); fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + path.resolve(__dirname, 'index3.html'));
  await p.waitForTimeout(800);
  // freeze all future animations: everything is driven by __seek
  const t0 = Date.now();
  for (let f = 0; f < nFrames; f++) {
    await p.evaluate((t) => window.__seek(t), f / FPS);
    await p.screenshot({ path: path.join(outDir, String(f).padStart(6, '0') + '.png'), type: 'png' });
    if (f % 250 === 0) console.log('frame', f, '/', nFrames, 'elapsed', ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  await b.close(); console.log('FRAMES_DONE', nFrames);
})();
