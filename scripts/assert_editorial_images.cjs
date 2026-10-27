/* Verify commissioned editorial images render at small mobile sizes, without adding
   fake screenshots or changing signup links. */
const fs=require('fs'),path=require('path'),{chromium}=require('./browser_runtime.cjs');
const root=path.join(__dirname,'..');
const pages=[
 {slug:'lg-모두의원칩-셀프개통',expected:['/img/guide/usim-lg-photo.webp','/img/editorial/lg-onechip-activation-steps.svg','/img/guide/platform-rule-03.webp','/img/editorial/lg-onechip-model-serial.svg']},
 {slug:'l망-464-요금제',expected:['/img/editorial/l464-data-condition.svg','/img/guide/usim-lg-photo.webp']},
 {slug:'l망-2-5gb-요금제',expected:['/img/editorial/l25-usage-summary.svg','/img/guide/usim-lg-photo.webp']},
 {slug:'kt선불폰-개통',expected:['/img/guide/usim-kt-photo.webp','/img/editorial/kt-baro-19digits.svg']}
];
(async()=>{
 const browser=await chromium.launch({headless:true});
 const output=path.join(root,'reports','ui','editorial-images');
 fs.mkdirSync(output,{recursive:true});
 const results=[],failed=[];
 for(const width of [390,480,1440]){
   const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
   for(const item of pages){
     const errors=[],listener=e=>errors.push(e.message);page.on('pageerror',listener);
     await page.goto('http://127.0.0.1:8765/'+item.slug+'/',{waitUntil:'load'});
     const imgs=await page.evaluate(async expected=>{
       const nodes=expected.map(src=>document.querySelector('article img[src="'+src+'"]'));
       await Promise.all(nodes.filter(Boolean).map(img=>{img.loading='eager';return img.decode().catch(()=>{})}));
       return nodes.map((img,i)=>img?{
         src:expected[i],loaded:img.complete&&img.naturalWidth>0,
         alt:img.getAttribute('alt'),w:Math.round(img.getBoundingClientRect().width),
         scrollWidth:img.scrollWidth,containerWidth:Math.round(img.parentElement.getBoundingClientRect().width)
       }:{src:expected[i],missing:true});
     },item.expected);
     const m=await page.evaluate(()=>({
       overflow:document.documentElement.scrollWidth>innerWidth+1,
       contentWidth:Math.round(document.querySelector('main.site')?.getBoundingClientRect().width||0),
       primary:document.querySelector('.hero-cta')?.getAttribute('href'),
       hasMag:!!document.querySelector('article.magazine-blue')
     }));
     const ok=imgs.length===item.expected.length&&imgs.every(x=>x.loaded&&!x.missing&&x.alt?.trim()&&x.w<=x.containerWidth+1)&&
       !m.overflow&&m.contentWidth<=480&&m.hasMag&&m.primary?.startsWith('https://preplan.site/')&&!errors.length;
     const row={width,slug:item.slug,ok,...m,imgs,errors};results.push(row);if(!ok)failed.push(row);
     if(width===390){await page.screenshot({path:path.join(output,item.slug+'-390.png'),fullPage:false});}
     page.removeListener('pageerror',listener);
   }
   await page.close();
 }
 await browser.close();
 fs.writeFileSync(path.join(output,'results.json'),JSON.stringify({checked:results.length,failed,results},null,2));
 console.log(JSON.stringify({checked:results.length,failed},null,2));
 if(failed.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
