const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const outDir = path.resolve(__dirname, '../video_raw');
  fs.mkdirSync(outDir, { recursive: true });

  const timeline = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../timeline.json'), 'utf8'));
  const totalMs = Math.ceil((timeline.total + 1.0) * 1000);

  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox'],
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: { dir: outDir, size: { width: 1920, height: 1080 } },
  });

  const page = await context.newPage();
  const file = 'file://' + path.resolve(__dirname, 'scene.html');
  const t0 = Date.now();
  await page.goto(file);
  console.log('navigated, recording for', totalMs, 'ms');

  await page.waitForTimeout(totalMs);

  console.log('elapsed', (Date.now() - t0) / 1000);
  await context.close();
  await browser.close();

  const files = fs.readdirSync(outDir).filter(f => f.endsWith('.webm'));
  console.log('produced:', files);
})();
