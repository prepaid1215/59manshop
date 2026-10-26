const fs=require('fs');
const path=require('path');
const {chromium}=require('./browser_runtime.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const results=[], failures=[];
 for(const width of [390,430,480,1024,1440]){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  for(const [type,url] of [['home','/'],['guide','/guide/#check'],['detail','/선불폰-개통방법/']]){
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto('http://127.0.0.1:8765'+url,{waitUntil:'networkidle'});
   await page.evaluate(()=>document.fonts.ready);
   const result=await page.evaluate(type=>{
    const $=s=>document.querySelector(s);
    const style=s=>{const e=$(s);return e?getComputedStyle(e):null};
    const countColumns=s=>{const c=style(s)?.gridTemplateColumns;return c&&!['none',''].includes(c)?c.split(/\s+/).filter(Boolean).length:0};
    return {
     shell:Math.round($('.top .site')?.getBoundingClientRect().width||0),
     content:Math.round($('main.site')?.getBoundingClientRect().width||0),
     desktopNav:style('.desktop-nav')?.display,
     mobileMenu:style('.top-menu')?.display,
     bottomBar:style('.bottom-bar')?.display,
     guideColumns:type==='guide'?countColumns('.gh-guide-grid'):null,
     categoryColumns:type==='guide'?countColumns('.gh-categories'):null,
     detailColumns:type==='detail'?countColumns('.detail-workspace'):null,
     sidebar:type==='detail'?style('.context-list')?.display:null,
     featuredColumns:type==='home'?countColumns('.home-featured-list'):null,
     overflow:document.documentElement.scrollWidth>innerWidth+1,
     backButton:type==='guide'?(()=>{
       const x=style('#gh-back');return {background:x?.backgroundColor,border:x?.borderTopWidth,radius:x?.borderTopLeftRadius,padding:x?.paddingTop,appearance:x?.appearance}
     })():null,
     broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.getAttribute('src')).slice(0,6)
    };
   },type);
   const ok=result.shell<=480&&result.content<=480&&result.desktopNav==='none'&&result.mobileMenu!=='none'&&result.bottomBar!=='none'&&!result.overflow&&result.broken.length===0&&(!result.guideColumns||result.guideColumns===1)&&(!result.categoryColumns||result.categoryColumns===3)&&(!result.featuredColumns||result.featuredColumns===1)&&(!result.sidebar||result.sidebar==='none')&&(!result.detailColumns||result.detailColumns===1)&&(!result.backButton||result.backButton.background==='rgb(240, 246, 255)'&&result.backButton.border!=='0px'&&result.backButton.radius==='10px');
   const record={type,width,ok,...result,errors};results.push(record);
   if(!ok||errors.length)failures.push(record);
   if(width===390||width===1440){
    const dir=path.join(__dirname,'../reports/ui/mobile-shell-qa');fs.mkdirSync(dir,{recursive:true});
    await page.screenshot({path:path.join(dir,type+'-'+width+'.png'),fullPage:false});
   }
  }
  await page.close();
 }
 await browser.close();
 fs.mkdirSync(path.join(__dirname,'../reports/ui/mobile-shell-qa'),{recursive:true});
 fs.writeFileSync(path.join(__dirname,'../reports/ui/mobile-shell-qa/results.json'),JSON.stringify(results,null,2));
 process.stdout.write(JSON.stringify({checked:results.length,failures},null,2)+'\n');
 if(failures.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
