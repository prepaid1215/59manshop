const fs=require('fs'),path=require('path');
const {chromium}=require('./browser_runtime.cjs');
const dir=path.join(__dirname,'../reports/ui/visual-v2');fs.mkdirSync(dir,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true});
 const rows=[];
 for(const width of [1440,390,430]){
  const page=await browser.newPage({viewport:{width,height:960},reducedMotion:'reduce',isMobile:width<=768,hasTouch:width<=768});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  async function images(){await page.locator('img').evaluateAll(imgs=>Promise.all(imgs.map(i=>{i.loading='eager';return i.decode().catch(()=>{});})));}
  async function capture(name,fullPage=false){
   await images();await page.screenshot({path:path.join(dir,name+'-'+width+'.png'),fullPage,style:fullPage?'.bottom-bar{visibility:hidden!important}':undefined});
   const metrics=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.getAttribute('src'))}));
   rows.push({name,width,...metrics,errors:[...errors]});
  }
  await page.goto('http://127.0.0.1:8765/guide/',{waitUntil:'networkidle'});
  await capture('guide-chooser');await capture('guide-full',true);
  const choose=key=>width<=768?page.locator('.gh-category[data-cat="'+key+'"]').tap():page.locator('.gh-category[data-cat="'+key+'"]').click();
  await choose('check');await capture('guide-list');
  await page.locator('#gc-section').screenshot({path:path.join(dir,'guide-list-section-'+width+'.png'),style:'.bottom-bar{visibility:hidden!important}'});
  await page.goto('http://127.0.0.1:8765/guide/#esim',{waitUntil:'networkidle'});
  await choose('esim');await capture('guide-esim');
  await page.locator('#gc-list>li:visible a').first().click();await page.waitForLoadState('networkidle');await capture('detail');
  await page.goto('http://127.0.0.1:8765/',{waitUntil:'networkidle'});await capture('home-full',true);
  await images();await page.locator('.home-featured').screenshot({path:path.join(dir,'home-quick-'+width+'.png'),style:'.bottom-bar{visibility:hidden!important}'});
  await page.close();
 }
 await browser.close();fs.writeFileSync(path.join(dir,'results.json'),JSON.stringify(rows,null,2)+'\n');console.log(JSON.stringify(rows,null,2));
 if(rows.some(r=>r.overflow||r.broken.length||r.errors.length))process.exitCode=1;
})();
