const fs=require('fs'),path=require('path');
const {chromium}=require('./browser_runtime.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const results=[],failures=[];
 const outdir=path.join(__dirname,'../reports/ui/home-conversion');
 fs.mkdirSync(outdir,{recursive:true});
 for(const width of [390,430,480,1024,1440]){
  const page=await browser.newPage({viewport:{width,height:844},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8765/',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const result=await page.evaluate(()=>{
   const $=x=>document.querySelector(x),$$=x=>[...document.querySelectorAll(x)];
   const c=e=>e?getComputedStyle(e):null;
   const a=$('.landing-primary-cta'),b=$('.landing-secondary-cta');
   return {
    headerWidth:Math.round($('.top .site').getBoundingClientRect().width),
    heroWidth:Math.round($('.landing-hero .site').getBoundingClientRect().width),
    contentWidth:Math.round($('main.site').getBoundingClientRect().width),
    hamburger:c($('.top-menu'))?.display,
    desktopNav:c($('.desktop-nav'))?.display,
    primary:a?.getAttribute('href'),secondary:b?.getAttribute('href'),
    primaryInViewport:!!a&&a.getBoundingClientRect().bottom<=innerHeight,
    sectionOrder:['landing-intents','home-plans','home-usims','activation-flow','landing-search'].map(name=>$('.'+name)?.getBoundingClientRect().top+scrollY),
    scenarioCount:$$('.landing-intent').length,
    planCTAs:$$('.landing-plan-cta').map(x=>x.getAttribute('href')),
    planNames:$$('.home-plan>b').map(x=>x.textContent.trim()),
    searchAction:$('.landing-search form')?.getAttribute('action'),
    bottomCTA:c($('.bottom-bar'))?.display,
    broken:$$('img').filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.getAttribute('src')),
    overflow:document.documentElement.scrollWidth>innerWidth+1,
    canonical:$('link[rel="canonical"]')?.getAttribute('href'),
    robots:$('meta[name="robots"]')?.getAttribute('content')
   };
  });
  const order=result.sectionOrder;
  const valid=results!==null&&result.headerWidth<=480&&result.heroWidth<=480&&result.contentWidth<=480&&
    result.desktopNav==='none'&&result.hamburger!=='none'&&result.primaryInViewport&&
    result.primary==='https://preplan.site/?from=59man_home_hero'&&result.secondary==='https://pf.kakao.com/_akxmKn/chat'&&
    result.scenarioCount===3&&result.planCTAs.length===3&&result.planCTAs.every(x=>x.startsWith('https://preplan.site/?from=59man_home_plan_'))&&
    order.every((n,i)=>Number.isFinite(n)&&(i===0||n>order[i-1]))&&result.searchAction==='/guide/'&&
    result.bottomCTA!=='none'&&!result.overflow&&result.broken.length===0&&
    result.canonical==='https://www.59man.shop/'&&result.robots==='index,follow'&&errors.length===0;
  const row={width,pass:valid,...result,errors};results.push(row);if(!valid)failures.push(row);
  await page.screenshot({path:path.join(outdir,'home-'+width+'.png'),fullPage:false});
  if(width===390)await page.screenshot({path:path.join(outdir,'home-390-full.png'),fullPage:true});
  await page.close();
 }
 await browser.close();
 fs.writeFileSync(path.join(outdir,'results.json'),JSON.stringify({count:results.length,failures,results},null,2));
 console.log(JSON.stringify({checked:results.length,failures},null,2));
 if(failures.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
