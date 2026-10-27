const fs=require('fs'),path=require('path');
const {chromium}=require('./browser_runtime.cjs');
const root=path.resolve(__dirname,'..'),out=path.join(root,'reports/ui/sitewide-paragraph-reading');
fs.mkdirSync(out,{recursive:true});
function collect(folder,base=''){
 let result=[];
 for(const entry of fs.readdirSync(folder,{withFileTypes:true})){
   if(entry.name==='.git'||entry.name==='node_modules'||entry.name==='reports')continue;
   const next=path.join(folder,entry.name),rel=path.posix.join(base,entry.name);
   if(entry.isDirectory())result.push(...collect(next,rel));
   else if(entry.name==='index.html')result.push(rel);
 }
 return result;
}
const files=collect(root).sort();
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
 const summary=[],issues=[],longParagraphs=[];
 for(const width of [390,480]){
  const page=await browser.newPage({viewport:{width,height:850},deviceScaleFactor:1,reducedMotion:'reduce'});
  for(const filename of files){
   const route=filename==='index.html'?'/':'/'+filename.replace(/index\.html$/,'');
   const errors=[];const handler=e=>errors.push(e.message);page.on('pageerror',handler);
   await page.goto('http://127.0.0.1:8765'+route,{waitUntil:'domcontentloaded',timeout:25000});
   // Redirect pages can replace the navigation context after DOMContentLoaded.
   // Retry inspection on the settled document instead of leaving Chromium open.
   let m;
   for(let attempt=0;attempt<3;attempt++){
     try{
       await Promise.race([
         page.evaluate(()=>document.fonts.ready),
         new Promise(resolve=>setTimeout(resolve,2000))
       ]);
       m=await page.evaluate(()=>{
    const article=document.querySelector('article.detail-article');
    const paragraphs=article?[...article.querySelectorAll('p')]:[];
    let seen=0,veryLong=[];
    for(const p of paragraphs){
      // Only prose directly under a section, not a step, note, TOC, FAQ, caption or small card.
      if(p.parentElement?.tagName!=='SECTION'||p.closest('.hero, .answer-card, .faq-item, .steps, .related, .sm-product-card'))continue;
      const text=p.textContent.trim();
      if(!text||text.length<40)continue;
      const range=document.createRange();range.selectNodeContents(p);
      const rects=[...range.getClientRects()].filter(x=>x.width>1);
      const y=[...new Set(rects.map(x=>Math.round(x.top)))];
      const lineHeight=parseFloat(getComputedStyle(p).lineHeight);
      const width=p.getBoundingClientRect().width;
      const estHeight=p.getBoundingClientRect().height;
      const count=Math.max(y.length,Math.round(estHeight/Math.max(1,lineHeight)));
      seen++;
      if(count>=6)veryLong.push({lines:count,chars:text.length,heading:p.closest('section')?.querySelector('h2')?.textContent?.slice(0,46)||'',snippet:text.slice(0,120)});
    }
    return {
      isArticle:!!article,
      paragraphsReviewed:seen,
      long:veryLong,
      articleWidth:article?Math.round(article.getBoundingClientRect().width):0,
      overflow:document.documentElement.scrollWidth>innerWidth+1,
      shellWidth:document.querySelector('.site')?.getBoundingClientRect().width,
      heroText:article?.querySelector('.hero h1')?.textContent?.trim(),
      loaded:true
    };
   });
       break;
     }catch(error){
       if(attempt===2||!/Execution context was destroyed|navigation|Frame was detached/i.test(String(error)))
         throw new Error(route+' at '+width+'px: '+String(error));
       await page.waitForLoadState('domcontentloaded',{timeout:5000}).catch(()=>{});
       await page.waitForTimeout(400);
     }
   }
   const row={route,width,...m,errors:errors.slice(0,2)};
   summary.push(row);
   for(const bad of m.long)longParagraphs.push({route,width,...bad});
   // Treat overflow on indexed article routes as hard error, report other legacy pages separately.
   if(m.isArticle&&m.articleWidth>481)issues.push({route,width,problem:'article > 480px'});
   if(m.overflow&&m.isArticle)issues.push({route,width,problem:'horizontal overflow'});
   if(width===390&&(['/v4-1/topic/sim-buy-where/','/lg-원칩/','/l망-464-요금제/'].includes(route))){
     const head=page.locator('section h2').filter({hasText:route.includes('sim-buy')?'판매처는 제품별로 달라요':route.includes('lg-원칩')?'매장마다 재고':'첫 충전'});
     if(await head.count())await head.first().scrollIntoViewIfNeeded();
     await page.screenshot({path:path.join(out,encodeURIComponent(route).replace(/%/g,'')+'-390.png'),fullPage:false});
   }
   page.removeListener('pageerror',handler);
  }
  await page.close();
 }
 const result={htmlPages:files.length,rendered:summary.length,articlesRendered:summary.filter(r=>r.isArticle).length,issues,longParagraphs,perPage:summary};
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({htmlPages:result.htmlPages,rendered:result.rendered,articlesRendered:result.articlesRendered,issues,paragraphsAtLeast6Lines:longParagraphs.length,longParagraphs:longParagraphs.slice(0,70)},null,2));
 if(issues.length)process.exitCode=1;
 } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1});
