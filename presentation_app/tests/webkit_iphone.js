const { webkit, devices } = require('playwright'); const fs = require('fs');
(async () => {
  const browser = await webkit.launch();
  for (const dev of ['iPhone 14', 'iPhone 14 landscape']) {
    const ctx = await browser.newContext({ ...devices[dev] }); const page = await ctx.newPage(); const errs = [];
    const map = { 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js': 'cdn/three.module.js', 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js': 'cdn/OrbitControls.js', 'https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js': 'cdn/d3.min.js' };
    await page.route(/^https:\/\//, r => { const f = map[r.request().url()]; if (f) r.fulfill({ status: 200, contentType: 'text/javascript', body: fs.readFileSync(f), headers: { 'access-control-allow-origin': '*' } }); else r.abort(); });
    page.on('pageerror', e => errs.push('pageerror: ' + e.message));
    await page.goto('http://127.0.0.1:8765/_test.html'); await page.waitForFunction(() => window.TEC && window.TEC.player, null, { timeout: 60000 }); await page.waitForTimeout(2000);
    const tag = dev.replace(/ /g, '_');
    await page.evaluate(() => TEC.player.go(7, 0, { play: false })); await page.waitForTimeout(1500);
    await page.tap('#play'); await page.waitForTimeout(3000);
    const a1 = await page.evaluate(() => ({ ct: +TEC.narrator.audio.currentTime.toFixed(2), paused: TEC.narrator.audio.paused, err: TEC.narrator.audio.error && TEC.narrator.audio.error.code, cap: document.querySelector('#caption').textContent.slice(0, 50), voice: TEC.narrator.voice && TEC.narrator.voice.name }));
    await page.screenshot({ path: `shots2/wk_${tag}_play.png` });
    await page.tap('#langEs'); await page.waitForTimeout(3000);
    const a2 = await page.evaluate(() => ({ ct: +TEC.narrator.audio.currentTime.toFixed(2), paused: TEC.narrator.audio.paused, src: TEC.narrator.audio.src.split('/').slice(-2).join('/'), cap: document.querySelector('#caption').textContent.slice(0, 50) }));
    await page.tap('[data-tab="slides"]'); await page.waitForTimeout(2500); await page.screenshot({ path: `shots2/wk_${tag}_slides.png` });
    await page.tap('[data-tab="field"]'); await page.waitForTimeout(5000); await page.screenshot({ path: `shots2/wk_${tag}_field.png` });
    await page.tap('[data-tab="data"]'); await page.waitForTimeout(1000);
    console.log(dev, '\n EN', JSON.stringify(a1), '\n ES', JSON.stringify(a2), '\n errs', errs.join(' | ') || 'none');
    await ctx.close();
  }
  await browser.close();
})();
