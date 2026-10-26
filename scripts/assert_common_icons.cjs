const fs=require('fs'),path=require('path');
const {chromium}=require('./browser_runtime.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const url='http://127.0.0.1:8765/앤텔레콤-선불폰-개통-방법/';
 const sprite=path.join(__dirname,'../img/article-photos/common-icons-sprite.png');
 const posterNames=['identity-resident-card.png','identity-driver-license.png','identity-mobile-id.png','esim-guide.png'];
 const errors=[],results=[];
 if(!fs.existsSync(sprite))throw Error('Missing supplied common icon sprite');
 for(const name of posterNames){
   if(!fs.existsSync(path.join(__dirname,'../img/article-photos',name)))throw Error('Missing supplied poster '+name);
 }
 for(const width of [390,480,1440]){
  const page=await browser.newPage({viewport:{width,height:900}});
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.querySelectorAll('.owner-poster').length===4);
  const result=await page.evaluate(()=>({
    auth:document.querySelectorAll('.auth-grid .common-icon-sprite--auth').length,
    idPosters:document.querySelectorAll('.img-cards--id .owner-poster').length,
    esimPosters:document.querySelectorAll('.img-cards--sim .owner-poster').length,
    icons:document.querySelectorAll('.common-icon-sprite').length,
    posterAssets:[...document.querySelectorAll('.owner-poster')].every(i=>i.complete&&i.naturalWidth>0&&i.alt),
    backgrounds:[...document.querySelectorAll('.common-icon-sprite')].every(e=>getComputedStyle(e).backgroundImage.includes('common-icons-sprite.png')),
    broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0).length,
    overflow:document.documentElement.scrollWidth>innerWidth+1,
    alignment:(function(){
      const cards=[...document.querySelectorAll('.auth-grid ul > li')];
      return {
        badgeTops:cards.map(c=>Number(c.querySelector('.auth-badge').getBoundingClientRect().top.toFixed(2))),
        labelTops:cards.map(c=>Number(c.querySelector('b').getBoundingClientRect().top.toFixed(2))),
        margins:cards.map(c=>getComputedStyle(c).marginTop),
        badgeWidths:cards.map(c=>Number(c.querySelector('.auth-badge').getBoundingClientRect().width.toFixed(2)))
      };
    })()
  }));
  const spread=xs=>Math.max(...xs)-Math.min(...xs);
  if(result.auth!==5||result.idPosters!==3||result.esimPosters!==1||result.icons!==5
     ||!result.posterAssets||!result.backgrounds||result.broken||result.overflow
     ||result.alignment.badgeTops.length!==5||spread(result.alignment.badgeTops)>1
     ||spread(result.alignment.labelTops)>1
     ||result.alignment.margins.some(m=>m!=='0px')
     ||spread(result.alignment.badgeWidths)>1
  )errors.push(width+': '+JSON.stringify(result));
  results.push({width,...result});await page.close();
 }
 const disabled=sprite+'.temporarily-disabled';
 if(fs.existsSync(disabled))throw Error('Sprite temporary path already exists');
 fs.renameSync(sprite,disabled);
 try{
  const page=await browser.newPage({viewport:{width:390,height:900}});
  await page.goto(url,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.querySelectorAll('.owner-poster').length===4);
  const result=await page.evaluate(()=>({
    icons:document.querySelectorAll('.common-icon-sprite').length,
    badges:[...document.querySelectorAll('.auth-grid .auth-badge')].map(e=>e.textContent.trim()).join(','),
    idPosters:document.querySelectorAll('.img-cards--id .owner-poster').length,
    esimPosters:document.querySelectorAll('.img-cards--sim .owner-poster').length
  }));
  if(result.icons!==0||result.badges!=='카,토,P,국,신'||result.idPosters!==3||result.esimPosters!==1)
     errors.push('Missing sprite fallback: '+JSON.stringify(result));
  await page.close();
 }finally{fs.renameSync(disabled,sprite);}
 await browser.close();
 console.log(JSON.stringify({checked:results,errors},null,2));
 if(errors.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
