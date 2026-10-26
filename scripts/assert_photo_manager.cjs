const path=require('path');
const fs=require('fs');
const {chromium}=require('./browser_runtime.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const root='http://127.0.0.1:8765';
 const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/photo-pages.json'),'utf8'));
 let errors=[];
 const page=await browser.newPage({viewport:{width:390,height:840},acceptDownloads:true});
 page.on('pageerror',e=>errors.push('JS: '+e.message));
 await page.goto(root+'/tools/photo-manager/',{waitUntil:'networkidle'});
 await page.waitForFunction(()=>document.querySelector('#article').options.length>1);
 const count=await page.locator('#article option').count();
 if(count!==catalog.length+1) errors.push('catalog not loaded: '+count);
 await page.selectOption('#article','선불폰-개통방법');
 await page.selectOption('#slot','01');
 const link=await page.locator('#open-article').getAttribute('href');
 if(!link||!link.includes('image-slots=1'))errors.push('preview link missing');
 const encoded=await page.evaluate(()=>{
  let c=document.createElement('canvas');c.width=20;c.height=20;
  c.getContext('2d').fillRect(0,0,20,20);return c.toDataURL('image/png').split(',')[1];
 });
 await page.locator('#photo').setInputFiles({name:'sample.png',mimeType:'image/png',buffer:Buffer.from(encoded,'base64')});
 const downloadPromise=page.waitForEvent('download');
 await page.locator('#save').click();
 const download=await downloadPromise;
 if(download.suggestedFilename()!=='선불폰-개통방법--01.webp')errors.push('incorrect download filename');
 await page.goto(root+'/선불폰-개통방법/?image-slots=1',{waitUntil:'networkidle'});
 await page.waitForFunction(()=>document.querySelectorAll('.article-photo-preview').length>=1);
 const n=await page.locator('.article-photo-preview').count();
 if(n<1||n>2)errors.push('preview slots unexpected: '+n);
 const emptyImgs=await page.evaluate(()=>[...document.images].filter(x=>x.complete&&x.naturalWidth===0).map(x=>x.src));
 if(emptyImgs.length)errors.push('broken image nodes: '+emptyImgs.join(','));
 for(const width of [390,480,1440]){
  await page.setViewportSize({width,height:840});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
  if(overflow) errors.push('overflow at '+width);
 }
 await page.goto(root+'/선불폰-개통방법/',{waitUntil:'networkidle'});
 if(await page.locator('.article-photo-preview').count())errors.push('public empty slot visible');
 await page.close();await browser.close();
 console.log(JSON.stringify({catalog:catalog.length,errors},null,2));if(errors.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1);});
