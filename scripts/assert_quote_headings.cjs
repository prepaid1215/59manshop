const fs = require('fs'), path = require('path');
const { chromium } = require('./browser_runtime.cjs');
const selector = '.detail-article > section:not(.hero):not(.answer-card):not(.faq):not(.cta):not(.plan-cards):not(.activation-flow) > h2';
(async () => {
 const browser = await chromium.launch({headless:true});
 const errors=[], results=[];
 const urls=['/선불폰-개통방법/','/미납정지-선불폰/','/편의점-선불유심/','/v4-1/topic/plan-396/','/kt-바로유심/'];
 const out=path.join(__dirname,'../reports/ui/quote-heading-qa');
 fs.mkdirSync(out,{recursive:true});
 for (const width of [390,480,1440]){
  const page=await browser.newPage({viewport:{width,height:900}});
  page.on('pageerror',e=>errors.push(e.message));
  for(const url of urls){
   await page.goto('http://127.0.0.1:8765'+url,{waitUntil:'networkidle'});
   const info=await page.evaluate(sel=>{
     const headings=Array.from(document.querySelectorAll(sel));
     const first=headings[0];if(!first)return {count:0,overflow:document.documentElement.scrollWidth>innerWidth+1};
     const style=getComputedStyle(first),p=getComputedStyle(first,'::before');
     const excluded=document.querySelector('.detail-article > section.faq > h2');
     return{
      count:headings.length,
      quote:p.content,
      quoteColor:p.color,
      quoteDisplay:p.display,
      border:style.borderBottomWidth,
      borderColor:style.borderBottomColor,
      fontSize:style.fontSize,
      marginBottom:style.marginBottom,
      overflow:document.documentElement.scrollWidth>innerWidth+1,
      nonDecorativeFaq:excluded?getComputedStyle(excluded,'::before').content:null,
      text:first.textContent.trim()
     };
   },selector);
   const ok=info.count>0&&info.quote.includes('“')&&info.quoteDisplay==='block'&&info.border==='1px'&&!info.overflow&&(!info.nonDecorativeFaq||info.nonDecorativeFaq==='none');
   results.push({url,width,ok,...info});
   if(!ok)errors.push(JSON.stringify({url,width,info}));
   if(width===390&&url==='/선불폰-개통방법/'){
    const h=page.locator(selector).first();
    await h.scrollIntoViewIfNeeded();
    await h.screenshot({path:path.join(out,'heading-390.png')});
   }
  }
  await page.close();
 }
 await browser.close();
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));
 console.log(JSON.stringify({checked:results.length,errors},null,2));
 if(errors.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
