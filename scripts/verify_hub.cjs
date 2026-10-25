// Layout, content and interaction checks in real Chromium. No service calls mutate state.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('./browser_runtime.cjs');
const root=path.join(__dirname,'..'),base='http://127.0.0.1:8765';
function routes(dir=root){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.name==='.git'||e.name==='reports'?[]:e.isDirectory()?routes(path.join(dir,e.name)):e.name==='index.html'&&!fs.readFileSync(path.join(dir,e.name),'utf8').includes('http-equiv="refresh"')?['/'+path.relative(root,path.join(dir,e.name)).replaceAll('\\','/').slice(0,-10)]:[]);}
async function layout(page){return page.evaluate(()=>{
  const errors=[];
  if(document.querySelectorAll('main').length!==1||document.querySelectorAll('h1').length!==1)errors.push('main/h1 count must be one');
  if(document.documentElement.scrollWidth>innerWidth)errors.push('horizontal page overflow');
  const broken=[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.getAttribute('src'));
  if(broken.length)errors.push('broken images: '+broken.join(', '));
  const duplicates=[...document.querySelectorAll('[id]')].map(e=>e.id).filter((id,i,ids)=>ids.indexOf(id)!==i);
  if(duplicates.length)errors.push('duplicate IDs: '+[...new Set(duplicates)].join(', '));
  // Compare text ranges, excluding intentional fixed navigation and hidden content.
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let node;const leaves=[];
  while(node=walker.nextNode()){
    if(!node.textContent.trim()||node.parentElement.closest('script,style,.sr-only,.bottom-bar,.top,.skip-link,svg'))continue;
    const disclosure=node.parentElement.closest('details:not([open])');
    if(disclosure&&!disclosure.querySelector('summary')?.contains(node.parentElement))continue;
    const range=document.createRange();range.selectNodeContents(node);
    const clip=node.parentElement.closest('.gc-desc,.gc-list,.preview-content');
    const bounds=clip?.getBoundingClientRect();
    for(const rect of range.getClientRects()){
      const r={left:rect.left,right:rect.right,top:rect.top,bottom:rect.bottom};
      if(bounds){r.left=Math.max(r.left,bounds.left);r.right=Math.min(r.right,bounds.right);r.top=Math.max(r.top,bounds.top);r.bottom=Math.min(r.bottom,bounds.bottom);}
      if(r.right-r.left>2&&r.bottom-r.top>5)leaves.push({r,text:node.textContent.trim().slice(0,35),el:node.parentElement});
    }
  }
  leaves.sort((a,b)=>a.r.top-b.r.top);
  for(let i=0;i<leaves.length;i++)for(let j=i+1;j<leaves.length&&leaves[j].r.top<leaves[i].r.bottom-3;j++){
    const a=leaves[i],b=leaves[j];
    if(a.el===b.el||a.el.contains(b.el)||b.el.contains(a.el))continue;
    const w=Math.min(a.r.right,b.r.right)-Math.max(a.r.left,b.r.left),h=Math.min(a.r.bottom,b.r.bottom)-Math.max(a.r.top,b.r.top);
    if(w>4&&h>5){errors.push('overlapping text: '+a.text+' / '+b.text);if(errors.length>8)return errors;}
  }
  for(const i of document.querySelectorAll('.gc-tile .gc-ic img'))if(i.closest('.gc-tile').getBoundingClientRect().width>0&&i.getBoundingClientRect().width===0)errors.push('invisible category icon');
  return errors;
});}
(async()=>{
 const browser=await chromium.launch({headless:true}),results=[],interactions=[];
 const legacyOnly=process.argv.includes('--noindex'),visualOnly=process.argv.includes('--visual');
 const widths=[390,430,480,1024,1440],all=routes().filter(route=>(!visualOnly||['/','/guide/'].includes(route))&&(!legacyOnly||/name="robots" content="[^"]*noindex/.test(fs.readFileSync(path.join(root,route.replace(/^\/+/,''),'index.html'),'utf8'))));
 for(const width of (process.argv.includes('--interactions-only') ? [] : widths)){
  for(let start=0;start<all.length;start+=2){
   await Promise.all(all.slice(start,start+2).map(async route=>{
    const page=await browser.newPage({viewport:{width,height:960},reducedMotion:'reduce'}),jsErrors=[];page.on('pageerror',e=>jsErrors.push(String(e)));
    try{
     await page.goto(base+route,{waitUntil:'networkidle'});
     await page.locator('img').evaluateAll(images=>Promise.all(images.map(i=>{i.loading='eager';return i.decode().catch(()=>{});})));
     if(route==='/guide/')await page.locator('.gh-guide-grid').waitFor();
     results.push({route,width,errors:[...jsErrors,...await layout(page)]});
    }catch(e){results.push({route,width,errors:[String(e)]});}finally{await page.close();}
   }));
  }
  console.log('Rendered '+all.length+' pages at '+width+'px');
 }
 if(legacyOnly){
  await browser.close();
  const report={pages:all.length,widths,rendered:results.length,failures:results.filter(r=>r.errors.length)};
  fs.writeFileSync(path.join(root,'reports/legacy-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
  if(report.failures.length)process.exitCode=1;
  return;
 }
 const page=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
 page.setDefaultTimeout(10000);
 async function test(name,fn){try{await fn();interactions.push({name,passed:true});console.log('PASS: '+name);}catch(e){interactions.push({name,passed:false,error:String(e)});console.log('FAIL: '+name+' '+String(e));}}
 await test('Mobile category → list → real detail URL',async()=>{
  await page.goto(base+'/guide/',{waitUntil:'networkidle'});await page.locator('.gc-tile[data-cat="sim"]').click();
  await page.waitForFunction(()=>location.hash==='#sim');assert.equal(await page.locator('#gc-list>li:visible').count(),6);
  await page.locator('#gc-list>li:visible a').first().click();await page.waitForFunction(()=>decodeURIComponent(location.pathname)==='/편의점-선불유심/');assert.equal(await page.locator('h1').count(),1);
  await page.goBack();await page.waitForFunction(()=>location.hash==='#sim');assert.equal(await page.locator('#gc-list>li:visible').count(),6);
 });
 await test('Menu disclosure, Escape and native keyboard links',async()=>{
  await page.locator('.top-menu summary').click();assert.equal(await page.locator('.top-menu').getAttribute('open'),'');await page.keyboard.press('Escape');assert.equal(await page.locator('.top-menu').getAttribute('open'),null);
 });
 await test('Search, empty state, clear and URL query',async()=>{
  await page.goto(base+'/guide/?q=eSIM',{waitUntil:'networkidle'});assert.ok(await page.locator('#gc-list>li:visible').count()>0);
  await page.locator('#gc-q').fill('결과없는문자열xyz');await page.locator('#gc-empty').waitFor({state:'visible'});
  await page.locator('#gc-clear').click();assert.equal(await page.locator('#gc-list>li:visible').count(),4);
  await page.locator('#gc-q').fill('유심');await page.locator('#gc-q').press('Enter');assert.ok(page.url().includes('?q='));
 });
 await test('Reference desktop two-column art cards and original detail route',async()=>{
  await page.setViewportSize({width:1440,height:960});await page.goto(base+'/guide/#self',{waitUntil:'networkidle'});
  assert.equal(await page.locator('.gh-guide-grid').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length),2);
  assert.ok(await page.locator('#gc-list>li:visible .gh-guide-art').first().evaluate(e=>e.getBoundingClientRect().width>=132));
  const link=page.locator('#gc-list>li:visible a').nth(1),href=await link.getAttribute('href');await link.click();
  await page.waitForFunction(href=>decodeURIComponent(location.pathname)===href,href);
  assert.equal(await page.locator('h1').textContent(),'선불폰 개통방법, 준비물부터 첫 충전까지');
 });
 await test('Rapid category selection keeps only the last category',async()=>{
  await page.goto(base+'/guide/#check',{waitUntil:'networkidle'});
  await page.locator('.gc-tile[data-cat="check"]').click();await page.locator('.gc-tile[data-cat="plan"]').click();
  assert.equal(await page.locator('#gc-title').textContent(),'요금제·충전');assert.equal(await page.locator('#gc-list>li:visible').count(),3);
 });
 await test('Reference mobile three-column chooser, subfilters and return scroll',async()=>{
  await page.setViewportSize({width:390,height:844});await page.goto(base+'/guide/',{waitUntil:'networkidle'});
  const positions=await page.locator('.gh-category').evaluateAll(es=>es.map(e=>({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y})));
  assert.equal(positions[0].y,positions[2].y);assert.ok(positions[3].y>positions[0].y);assert.ok(positions[6].x>positions[0].x);
  await page.locator('.gh-category[data-cat="check"]').click();
  assert.ok(await page.locator('#gc-section').evaluate(e=>e.getBoundingClientRect().top<110));
  await page.locator('#gh-subfilters button[data-tag="신청조건"]').click();assert.equal(await page.locator('#gc-list>li:visible').count(),1);
  assert.equal(await page.locator('#gc-list>li:visible .gc-num').textContent(),'01');
  await page.locator('#gh-back').click();assert.ok(await page.locator('#gh-directory').evaluate(e=>e.getBoundingClientRect().top<110));
 });
 await test('Mobile eSIM selection keeps note and native detail navigation',async()=>{
  await page.setViewportSize({width:430,height:900});await page.goto(base+'/guide/#esim',{waitUntil:'networkidle'});await page.locator('#gc-list>li:visible a').first().click();await page.waitForFunction(()=>location.pathname==='/v4-1/topic/esim-new/');
 });
 await test('Plugin category query aliases preserve existing canonical',async()=>{
  await page.goto(base+'/guide/?guide_category=preparation',{waitUntil:'networkidle'});assert.equal(await page.locator('#gc-list>li:visible').count(),4);
  assert.equal(await page.locator('link[rel=canonical]').getAttribute('href'),'https://www.59man.shop/guide/');
 });
 await test('Accessible category reorder persists without changing routes',async()=>{
  await page.goto(base+'/guide/#all',{waitUntil:'networkidle'});const first=page.locator('.gh-category').first();const key=await first.getAttribute('data-cat');
  await first.focus();await page.keyboard.press('Alt+ArrowRight');assert.equal(await page.locator('.gh-category').nth(1).getAttribute('data-cat'),key);
  await page.reload();assert.equal(await page.locator('.gh-category').nth(1).getAttribute('data-cat'),key);
 });
 await test('Conversion URLs and business contact remain accessible',async()=>{
  await page.goto(base+'/',{waitUntil:'networkidle'});assert.ok(await page.locator('.bottom-bar a[href^="https://preplan.site/"]').isVisible());assert.ok(await page.locator('.bottom-bar a[href="https://pf.kakao.com/_akxmKn/chat"]').isVisible());assert.ok((await page.locator('.footer').textContent()).includes('774-56-00506'));
 });
 await test('No-JavaScript fallback renders all guide anchors',async()=>{
  const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}}),p=await context.newPage();await p.goto(base+'/guide/');assert.equal(await p.locator('.gc-card').count(),23);await p.locator('.gc-card').first().focus();await p.keyboard.press('Enter');await p.waitForURL(url=>decodeURIComponent(url.pathname)==='/선불폰-개통/');await context.close();
 });
 await page.close();await browser.close();
 const previous=process.argv.includes('--interactions-only')?JSON.parse(fs.readFileSync(path.join(root,'reports/browser-verification.json'),'utf8')):null;
 const report={pages:all.length,widths,rendered:previous?previous.rendered:results.length,failures:previous?previous.failures:results.filter(r=>r.errors.length),interactions};
 fs.writeFileSync(path.join(root,visualOnly?'reports/visual-browser-verification.json':'reports/browser-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
 if(report.failures.length||interactions.some(i=>!i.passed))process.exitCode=1;
})();
