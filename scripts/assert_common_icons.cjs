const fs=require('fs'),path=require('path');
const {chromium}=require('./browser_runtime.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const url='http://127.0.0.1:8765/앤텔레콤-선불폰-개통-방법/';
 const dir=path.join(__dirname,'../img/article-photos');
 const names=['common-auth-kakao.webp','common-auth-toss.webp','common-auth-pass.webp',
  'common-auth-kb.webp','common-auth-shinhan.webp','common-id-resident.webp',
  'common-id-driver.webp','common-id-mobile.webp','common-esim.webp'];
 const errors=[];
 let page=await browser.newPage({viewport:{width:390,height:900}});
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url,{waitUntil:'networkidle'});
 await page.waitForTimeout(400);
 const missing=await page.evaluate(()=>{
  return {
   badges:[...document.querySelectorAll('.auth-grid .auth-badge')].map(e=>e.textContent.trim()),
   photos:document.querySelectorAll('.auth-grid .auth-badge img').length,
   identities:[...document.querySelectorAll('.img-cards--id .ic-art img')].map(e=>e.getAttribute('src'))
  };
 });
 if(missing.badges.join(',')!=='카,토,P,국,신')errors.push('Fallback badge labels altered: '+missing.badges.join(','));
 if(missing.photos!==0)errors.push('Unexpected icon before upload');
 if(missing.identities.some(x=>!x.includes('guides-check.svg')))errors.push('Identity fallback missing');
 const bytes=await page.evaluate(()=>{
  const c=document.createElement('canvas');c.width=96;c.height=96;
  const ctx=c.getContext('2d');ctx.fillStyle='#175CD3';ctx.fillRect(0,0,96,96);
  return c.toDataURL('image/webp').split(',')[1];
 });
 fs.mkdirSync(dir,{recursive:true});
 const inserted=[];
 try{
  for(const name of names){const dest=path.join(dir,name);if(fs.existsSync(dest))throw Error('Test refuses to overwrite '+name);fs.writeFileSync(dest,Buffer.from(bytes,'base64'));inserted.push(dest);}
  for(const width of [390,480,1440]){
   await page.setViewportSize({width,height:900});
   await page.goto(url,{waitUntil:'networkidle'});
   await page.waitForFunction(()=>document.querySelectorAll('.auth-grid .auth-badge--photo img').length===5
    && document.querySelectorAll('.img-cards--id .common-card-photo').length===3
    && document.querySelectorAll('.img-cards--sim .common-card-photo').length===1);
   const result=await page.evaluate(()=>({
    auth:document.querySelectorAll('.auth-grid .auth-badge--photo img').length,
    id:document.querySelectorAll('.img-cards--id .common-card-photo').length,
    esim:document.querySelectorAll('.img-cards--sim .common-card-photo').length,
    broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0).length,
    overflow:document.documentElement.scrollWidth>innerWidth+1
   }));
   if(result.auth!==5||result.id!==3||result.esim!==1||result.broken||result.overflow)errors.push(width+': '+JSON.stringify(result));
  }
 }finally{for(const dest of inserted){if(fs.existsSync(dest))fs.unlinkSync(dest);}}
 await page.close();await browser.close();
 console.log(JSON.stringify({checked:names.length,errors},null,2));
 if(errors.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
