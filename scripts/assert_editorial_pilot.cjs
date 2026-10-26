const fs=require('fs'),path=require('path');
const {chromium}=require('./browser_runtime.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const dir=path.join(__dirname,'../reports/ui/editorial-pilot');
 fs.mkdirSync(dir,{recursive:true});
 const results=[],errors=[];
 for(const width of [390,430,480,1024,1440]){
  for(const [name,route] of [['activation','/선불폰-개통방법/'],['arrears','/미납정지-선불폰/'],['sim','/편의점-선불유심/']]){
   const page=await browser.newPage({viewport:{width,height:900}});
   const pageErr=[];page.on('pageerror',e=>pageErr.push(e.message));
   await page.goto('http://127.0.0.1:8765'+route,{waitUntil:'networkidle'});
   await page.evaluate(()=>document.fonts.ready);
   const detail=await page.evaluate(()=>{
    const $=x=>document.querySelector(x);
    const rect=x=>{const e=$(x);return e?{top:Math.round(e.getBoundingClientRect().top),bottom:Math.round(e.getBoundingClientRect().bottom),width:Math.round(e.getBoundingClientRect().width)}:null};
    const txt=x=>$(x)?.textContent?.trim()||'';
    const a=$('.detail-article');
    const summary=$('.detail-article>.answer-card');
    return {
     pageWidth:innerWidth,
     fontFamily:getComputedStyle(document.body).fontFamily,
     shellWidth:rect('.top .site')?.width,contentWidth:rect('main.site')?.width,articleWidth:rect('.editorial-v2')?.width,
     headline:txt('.editorial-v2 h1'),summary:txt('.editorial-v2>.answer-card h2'),
     conclusionChars:txt('.editorial-v2>.answer-card .answer-lead').length,summaryTop:rect('.editorial-v2>.answer-card')?.top,
     summaryEnd:rect('.editorial-v2>.answer-card')?.bottom,heroEnd:rect('.editorial-v2>.hero')?.bottom,
     coverInSummary:!!$('.editorial-v2>.answer-card>.detail-lead-visual'),
     duplicateCover:document.querySelectorAll('.editorial-v2 .detail-lead-visual').length,
     sectionCount:document.querySelectorAll('.editorial-v2>section').length,
     paraFont:parseFloat(getComputedStyle($('.editorial-v2>section:not(.hero):not(.answer-card) p')).fontSize),
     overflow:document.documentElement.scrollWidth>innerWidth+1,
     broken:[...document.images].filter(x=>x.complete&&x.naturalWidth===0).map(x=>x.getAttribute('src')),
     canonical:$('link[rel=canonical]')?.getAttribute('href'),
     robots:$('meta[name=robots]')?.getAttribute('content'),
     backMenu:getComputedStyle($('.top-menu')).display,
     pcMenu:getComputedStyle($('.desktop-nav')).display,
     cta:$('.bottom-bar-main')?.getAttribute('href'),
    };
   });
   const ok=detail.fontFamily.includes('Pretendard Variable')&&detail.shellWidth<=480&&detail.contentWidth<=480&&detail.articleWidth<=480&&!detail.overflow&&!detail.broken.length&&detail.coverInSummary&&detail.duplicateCover===1&&detail.summaryTop<Math.min(900,detail.heroEnd+90)&&detail.paraFont>=14.7&&detail.conclusionChars>35&&detail.robots==='index,follow'&&detail.backMenu!=='none'&&detail.pcMenu==='none'&&pageErr.length===0;
   const record={name,width,ok,...detail,errors:pageErr};results.push(record);if(!ok)errors.push(record);
   if(width===390||width===1440){await page.screenshot({path:path.join(dir,name+'-'+width+'.png'),fullPage:false});
    if(width===390) await page.screenshot({path:path.join(dir,name+'-390-full.png'),fullPage:true});}
   await page.close();
  }
 }
 await browser.close();
 fs.writeFileSync(path.join(dir,'results.json'),JSON.stringify({checked:results.length,failed:errors,results},null,2));
 console.log(JSON.stringify({checked:results.length,failed:errors},null,2));
 if(errors.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
