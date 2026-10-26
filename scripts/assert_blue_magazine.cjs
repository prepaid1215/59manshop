/* Magazine layout regression for key keyword landing articles.
   Tests semantic navigation, preserved CTAs, blue brand and mobile-only viewport.
 */
const fs=require('fs'),path=require('path');
const {chromium}=require('./browser_runtime.cjs');
const root=path.join(__dirname,'..');
const dir=path.join(root,'reports/ui/blue-magazine-qa');
fs.mkdirSync(dir,{recursive:true});
const pages=[
 {route:'/lg-모두의원칩-셀프개통/',facts:3,products:0,choices:2,final:true},
 {route:'/l망-464-요금제/',facts:3,products:0,choices:2,final:true},
 {route:'/l망-2-5gb-요금제/',facts:4,products:0,choices:2,final:true},
 {route:'/편의점-선불유심/',facts:3,products:3,choices:0,final:false},
 {route:'/kt선불폰-개통/',facts:3,products:0,choices:2,final:false}
];
(async()=>{
 const browser=await chromium.launch({headless:true});
 const failures=[],results=[];
 for(const width of [390,480,1440]){
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
  for(const spec of pages){
   const errs=[];const onerror=e=>errs.push(e.message);page.on('pageerror',onerror);
   await page.goto('http://127.0.0.1:8765'+spec.route,{waitUntil:'networkidle'});
   await page.evaluate(()=>document.fonts.ready);
   const m=await page.evaluate(()=>{
     const a=document.querySelector('#main-content .detail-article');
     const sections=[...a.querySelectorAll(':scope > section.magazine-section')];
     const nav=a.querySelector('.sm-page-nav'),toc=[...nav?.querySelectorAll('a')||[]];
     const h2=sections[0]?.querySelector(':scope > h2');
     const checks=toc.every(x=>x.hash&&document.querySelector(x.hash)===x.closest('article').querySelector(x.hash));
     return {
      articleWidth:Math.round(a.getBoundingClientRect().width),
      mag:a.classList.contains('magazine-blue'),
      facts:a.querySelectorAll('.sm-quick-item').length,
      products:a.querySelectorAll('.sm-product-card').length,
      choices:a.querySelectorAll('.sm-choice-grid a').length,
      final:!!a.querySelector('.sm-final'),
      numbered:sections.length>=3&&h2?.getAttribute('data-sm-number')==='01'
        &&getComputedStyle(h2,'::before').content.includes('01'),
      blueRule:getComputedStyle(h2,'::after').backgroundColor,
      linkColor:getComputedStyle(a.querySelector('.related>a')).color,
      tocCount:toc.length,
      validToc:checks,
      primary:a.querySelector('.hero-cta')?.getAttribute('href'),
      noOverflow:document.documentElement.scrollWidth<=innerWidth+1,
      imgBroken:[...a.querySelectorAll('img')].filter(x=>x.complete&&x.naturalWidth===0).map(x=>x.src).slice(0,6)
     };
   });
   const ok=m.mag&&m.articleWidth<=480&&m.facts===spec.facts&&m.products===spec.products&&
     m.choices===spec.choices&&m.final===spec.final&&m.numbered&&m.tocCount>=3&&m.validToc&&
     m.blueRule==='rgb(23, 92, 211)'&&m.linkColor==='rgb(23, 92, 211)'&&
     m.primary?.startsWith('https://preplan.site/')&&m.noOverflow&&!m.imgBroken.length&&!errs.length;
   const row={width,route:spec.route,pass:ok,...m,errors:errs};results.push(row);
   if(!ok)failures.push(row);
   if(width===390||width===1440){
     await page.screenshot({path:path.join(dir,encodeURIComponent(spec.route).replace(/%/g,'')+'-'+width+'.png'),fullPage:false});
   }
   page.removeListener('pageerror',onerror);
  }
  await page.close();
 }
 await browser.close();
 fs.writeFileSync(path.join(dir,'results.json'),JSON.stringify({checked:results.length,failures,results},null,2));
 console.log(JSON.stringify({checked:results.length,failures},null,2));
 if(failures.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
