/* Confirm the common detail-article skin across every indexed article.
   Intentional differences (product images, tables, onboarding carousel, FAQs) are preserved. */
const fs=require('fs'),path=require('path');
const {chromium}=require('./browser_runtime.cjs');
const root=path.join(__dirname,'..');
const xml=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');
const routes=[...xml.matchAll(/<loc>https:\/\/www\.59man\.shop(\/[^<]*)<\/loc>/g)]
 .map(x=>x[1]).filter(p=>p!=='/'&&p!=='/guide/');
const outDir=path.join(root,'reports','ui','design-unification');
fs.mkdirSync(outDir,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true});
 const results=[],issues=[];
 const samples=new Set(['/kt선불폰-개통/','/lg-원칩/','/선불폰-개통방법/','/편의점-선불유심/','/미납정지-선불폰/','/앤텔레콤-선불폰-개통-방법/']);
 for(const width of [390,480,1440]){
  let baseline=null;
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
  for(const route of routes){
   const errors=[];const listen=e=>errors.push(String(e.message||e));
   page.on('pageerror',listen);
   await page.goto('http://127.0.0.1:8765'+route,{waitUntil:'load'});
   await page.evaluate(()=>document.fonts.ready);
   const m=await page.evaluate(()=>{
    const a=document.querySelector('#main-content .detail-article');
    if(!a)return {missingArticle:true};
    const h1=a.querySelector('.hero h1');
    const h2=a.querySelector(':scope > section:not(.hero):not(.answer-card):not(.faq):not(.cta):not(.plan-cards):not(.activation-flow) > h2');
    const p=a.querySelector(':scope > section:not(.hero):not(.answer-card) > p:not(.updated)');
    const related=a.querySelector('.related'),rTitle=related?.querySelector('.related-title'),rLink=related?.querySelector('a');
    const css=e=>e?getComputedStyle(e):null;
    const round=(e,n)=>e?Math.round(parseFloat(css(e)[n])*100)/100:null;
    const c=css(a),cr=css(related),cl=css(rLink);
    return {
      font:c.fontFamily,
      articleWidth:Math.round(a.getBoundingClientRect().width*10)/10,
      padding:round(a,'paddingLeft'),borderRadius:round(a,'borderTopLeftRadius'),
      borderColor:c.borderTopColor,
      bg:c.backgroundColor,
      h1Font:round(h1,'fontSize'),h1Color:css(h1)?.color,
      h2Font:round(h2,'fontSize'),h2Quote:h2?getComputedStyle(h2,'::before').content:null,
      paragraphSize:round(p,'fontSize'),paragraphLine:round(p,'lineHeight'),
      relatedTitle:rTitle?.textContent.trim(),relatedBorder:cr?.borderTopColor,
      relatedBorderStyle:cr?.borderTopStyle,relatedRadius:round(related,'borderTopLeftRadius'),
      relatedLinkColor:cl?.color,relatedLinkWeight:cl?.fontWeight,
      overflow:document.documentElement.scrollWidth>innerWidth+1,
      bottomLink:document.querySelector('.bottom-bar-main')?.getAttribute('href'),
      cssLink:!![...document.querySelectorAll('link[rel=stylesheet]')].find(l=>l.getAttribute('href').includes('/assets/hub.css')),
      editorial:a.classList.contains('editorial-v2'),
      countPhoto:document.querySelectorAll('.article-photo-figure img').length
    };
   });
   const common=['padding','borderRadius','borderColor','bg','h1Font','h1Color','h2Font','h2Quote','paragraphSize','paragraphLine','relatedTitle','relatedBorder','relatedBorderStyle','relatedRadius','relatedLinkColor','relatedLinkWeight'];
   const baseRecord=Object.fromEntries(common.map(k=>[k,m[k]]));
   if(!baseline)baseline=baseRecord;
   const drift=common.filter(k=>m[k]!==baseline[k]);
   const ok=!m.missingArticle&&!m.overflow&&m.cssLink&&m.articleWidth<=480.5&&
      m.font?.includes('Pretendard')&&m.relatedTitle==='함께 보면 좋은 글'&&
      m.bottomLink?.startsWith('https://preplan.site/')&&
      m.h2Quote?.includes('“')&&m.relatedLinkColor==='rgb(114, 80, 239)'&&
      drift.length===0&&errors.length===0;
   const row={width,route,ok,drift,...m,errors};
   results.push(row);
   if(!ok)issues.push(row);
   if(width===390&&samples.has(route)){
    await page.screenshot({path:path.join(outDir,encodeURIComponent(route.replace(/\//g,'_'))+'.png'),fullPage:false});
   }
   page.removeListener('pageerror',listen);
  }
  await page.close();
 }
 await browser.close();
 const report={pages:routes.length,viewports:[390,480,1440],checked:results.length,failed:issues.length,issues,results};
 fs.writeFileSync(path.join(outDir,'results.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({pages:routes.length,checked:results.length,failed:issues.length,issues:issues.slice(0,12)},null,2));
 if(issues.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
