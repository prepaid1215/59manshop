const fs=require('fs');
const path=require('path');
const {chromium}=require('./browser_runtime.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const records=[],failures=[];
 const save=path.join(__dirname,'../reports/ui/article-readability');
 fs.mkdirSync(save,{recursive:true});
 const targets=[
  ['process','/선불폰-개통방법/'],
  ['arrears','/미납정지-선불폰/'],
  ['comparison','/v4-1/topic/plan-compare/'],
  ['guide','/guide/#check']
 ];
 for(const width of [390,430,480,1024,1440]){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  for(const [name,url] of targets){
   const errs=[];page.on('pageerror',e=>errs.push(e.message));
   await page.goto('http://127.0.0.1:8765'+url,{waitUntil:'networkidle'});
   await page.evaluate(()=>document.fonts.ready);
   const x=await page.evaluate(name=>{
    const $=x=>document.querySelector(x);
    const num=(sel,prop)=>parseFloat(getComputedStyle($(sel))[prop]||0);
    const article=name!=='guide',sel=article?'.detail-article > section:not(.hero) p':'.visual-guide .gc-desc';
    const p=$(sel),st=p?getComputedStyle(p):null;
    const s=$(article?'.detail-article > section:not(.hero) > h2':'.visual-guide .gh-guide-title');
    const hs=s?getComputedStyle(s):null;
    const tbl=$('.detail-article table'),tbls=tbl?getComputedStyle(tbl):null;
    const widthOf=e=>e?Math.round(e.getBoundingClientRect().width):null;
    return {
     shell:widthOf($('.top .site')),main:widthOf($('main.site')),
     paragraphFont:st?parseFloat(st.fontSize):null,
     lineRatio:st?parseFloat(st.lineHeight)/parseFloat(st.fontSize):null,
     paragraphColor:st?.color,
     headingFont:hs?parseFloat(hs.fontSize):null,
     tableFont:tbls?parseFloat(tbls.fontSize):null,
     tableOverflow:tbls?.overflowX,
     links:[...document.querySelectorAll('.detail-article > section p a')].slice(0,2).map(x=>getComputedStyle(x).textDecorationLine),
     horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,
     broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0).slice(0,3).map(i=>i.getAttribute('src'))
    };
   },name);
   const ok=x.shell<=480&&x.main<=480&&!x.horizontalOverflow&&
      x.broken.length===0&&x.paragraphFont>=(name==='guide'?12.8:15.3)&&x.lineRatio>=(name==='guide'?1.6:1.7)&&
      x.headingFont>=(name==='guide'?16:21)&&
      (x.tableFont===null||x.tableFont>=13.5)&&errs.length===0;
   const record={width,name,ok,...x,errors:errs};records.push(record);
   if(!ok)failures.push(record);
   if((width===390||width===1440)&&(name==='process'||name==='guide'||name==='comparison')){
    await page.screenshot({path:path.join(save,name+'-'+width+'.png'),fullPage:false});
   }
  }
  await page.close();
 }
 await browser.close();
 fs.writeFileSync(path.join(save,'results.json'),JSON.stringify({checked:records.length,failures,records},null,2));
 console.log(JSON.stringify({checked:records.length,failures},null,2));
 if(failures.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
