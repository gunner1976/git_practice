const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const html = '<!doctype html><html><head><meta charset="utf-8"><style>[hidden]{display:none!important}body{margin:0}</style></head><body>' + fs.readFileSync('../tecapp/index.html', 'utf8') + '</body></html>';
  fs.writeFileSync('../tecapp/_test.html', html);
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] });
  for (const mode of ['getVoicesThrows', 'allThrow']) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true }); const errs = [];
    await page.addInitScript(mode => {
      const boom = () => { throw new TypeError("undefined is not an object (evaluating 'Object.getPrototypeOf(voice)')"); };
      const s = window.speechSynthesis; s.getVoices = boom;
      if (mode === 'allThrow') { s.addEventListener = boom; s.speak = boom; s.cancel = boom; }
    }, mode);
    const map = { 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js': 'cdn/three.module.js', 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js': 'cdn/OrbitControls.js', 'https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js': 'cdn/d3.min.js' };
    await page.route(/^https:\/\//, r => { const f = map[r.request().url()]; if (f) r.fulfill({ status: 200, contentType: 'text/javascript', body: fs.readFileSync(f) }); else r.abort(); });
    page.on('pageerror', e => errs.push(e.message));
    await page.goto('http://127.0.0.1:8765/_test.html');
    const ok = await page.waitForFunction(() => window.TEC && window.TEC.player, null, { timeout: 60000 }).then(() => true).catch(() => false);
    const loading = await page.evaluate(() => document.getElementById('loading')?.textContent);
    await page.waitForTimeout(1500);
    const voices = await page.evaluate(() => [...document.querySelectorAll('#voice option')].map(o => o.textContent));
    await page.evaluate(() => TEC.player.go(2, 0, { play: false })); await page.waitForTimeout(800); await page.click('#play'); await page.waitForTimeout(2500);
    const st = await page.evaluate(() => ({ ct: +TEC.narrator.audio.currentTime.toFixed(2), paused: TEC.narrator.audio.paused, cap: document.querySelector('#caption').textContent.slice(0, 40) }));
    await page.screenshot({ path: `shots2/broken_${mode}.png` });
    console.log(mode, 'booted', ok, '| loading:', (loading || '').slice(0, 60), '| voices', voices, '|', JSON.stringify(st), '| errs', errs.join(' | '));
    await page.close();
  }
  await browser.close();
})();
