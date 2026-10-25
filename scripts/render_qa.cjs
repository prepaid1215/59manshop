// Local, repeatable real Chromium rendering; run with the bundled Playwright.
const fs = require('fs');
const path = require('path');
const {chromium} = require('./browser_runtime.cjs');
(async () => {
  const baseline = process.argv.includes('--before');
  const dir = path.join(__dirname, '../reports/ui', baseline ? 'before' : 'after');
  fs.mkdirSync(dir, {recursive:true});
  const browser = await chromium.launch({headless:true});
  const widths = baseline ? [390,1440] : [390,430,480,1024,1440];
  const routes = {'home':'/', 'guide':'/guide/#check', 'detail':'/선불폰-개통방법/', 'plans':'/v4-1/topic/plan-compare/'};
  const results = [];
  for (const width of widths) {
    const page = await browser.newPage({viewport:{width,height:960},deviceScaleFactor:1});
    const errors=[];
    page.on('pageerror', e=>errors.push(String(e)));
    for (const [name,route] of Object.entries(routes)) {
      await page.goto('http://127.0.0.1:8765'+route, {waitUntil:'networkidle'});
      await page.evaluate(()=>document.fonts.ready);
      await page.locator('img').evaluateAll(images=>images.forEach(i=>i.loading='eager'));
      await page.locator('img').evaluateAll(images=>Promise.all(images.map(i=>i.decode().catch(()=>{}))));
      if(!baseline&&name==='guide')await page.locator('.gh-guide-grid').waitFor();
      const metrics = await page.evaluate(()=>({
        overflow:document.documentElement.scrollWidth>innerWidth,
        broken:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.getAttribute('src')),
        h1:document.querySelector('h1')?.textContent,
        outside:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width && s.position!=='absolute' && (r.right>innerWidth+1||r.left< -1) && !e.closest('.table-scroll,.preview-content,.gc-list')}).slice(0,8).map(e=>e.tagName+'.'+e.className)
      }));
      await page.screenshot({path:path.join(dir,`${name}-${width}.png`), fullPage:true,style:baseline?undefined:'.bottom-bar{visibility:hidden!important}'});
      if(!baseline)await page.screenshot({path:path.join(dir,`${name}-${width}-viewport.png`)});
      results.push({name,width,...metrics,errors:[...errors]});
    }
    await page.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(dir,'render-results.json'),JSON.stringify(results,null,2));
  console.log(JSON.stringify(results,null,2));
  if(results.some(r=>r.overflow||r.broken.length||r.errors.length))process.exitCode=1;
})();
