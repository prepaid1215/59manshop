/* QA: explicit consent, no PII, both static and JS-created activation links. */
const fs=require('fs'),path=require('path');
const {chromium}=require('./browser_runtime.cjs');
const root=path.join(__dirname,'..');
const out=path.join(root,'reports','ui','conversion-tracking');
fs.mkdirSync(out,{recursive:true});
const base='http://127.0.0.1:8765';
(async()=>{
 const browser=await chromium.launch({headless:true});
 const failures=[],results=[];
 async function scenario(label,route,fn){
   const page=await browser.newPage({viewport:{width:390,height:844}});
   await page.route(/googletagmanager\.com/,r=>r.abort());
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   try{
     await page.goto(base+route,{waitUntil:'load'});
     await page.waitForFunction(()=>typeof window.mm59TrackingStatus==='function');
     const data=await fn(page);
     const pass=!!data.pass&&!errors.length;
     results.push({label,pass,detail:data,errors});
     if(!pass)failures.push({label,data,errors});
   }catch(e){failures.push({label,error:String(e)})}
   await page.close();
 }
 await scenario('default: opt-in required, outgoing click is marked', '/',async page=>{
   const before=await page.evaluate(()=>({
     state:mm59TrackingStatus().analyticsConsent,
     banner:!!document.getElementById('mm59-analytics-consent'),
     gaScript:!!document.querySelector('script[src*="gtag/js?id="]')
   }));
   const after=await page.evaluate(()=>{
     document.addEventListener('click',e=>e.preventDefault());
     const a=document.querySelector('.landing-primary-cta');
     a.click();
     const sent=(window.dataLayer||[]).filter(x=>x&&x.event==='mm59_outbound_click').pop();
     return {event:sent,href:a.href,gaScript:!!document.querySelector('script[src*="gtag/js?id="]')};
   });
   return {pass:before.state==='unset'&&before.banner&&!before.gaScript&&after.event?.mm_destination_type==='activation_home'&&after.event?.mm_source==='59man_home_hero'&&!after.gaScript, before,after};
 });
 await scenario('existing info link stays info; sticky CTA gets source code', '/lg-모두의원칩-셀프개통/',async page=>{
   return page.evaluate(()=>{
     document.addEventListener('click',e=>e.preventDefault());
     const info=document.querySelector('a[href*="preplan.site/lg-self/"]');
     const initial=info?.href;
     info?.click();
     const out1=(window.dataLayer||[]).filter(x=>x&&x.event==='mm59_outbound_click').pop();
     const sticky=document.querySelector('.bottom-bar-main');
     sticky?.click();
     const out2=(window.dataLayer||[]).filter(x=>x&&x.event==='mm59_outbound_click').pop();
     const modified=sticky?.href;
     return {
       pass:!!info&&initial===info.href&&out1?.mm_destination_type==='information'&&
         out2?.mm_destination_type==='activation_home'&&
         new URL(modified).searchParams.get('from')==='59man_lg-모두의원칩-셀프개통_sticky',
       initial,modified,infoEvent:out1,activationEvent:out2
     };
   });
 });
 await scenario('consent opt-in loads GA4 only after click', '/guide/',async page=>{
   await page.locator('#mm59-analytics-consent button').filter({hasText:'동의'}).click();
   return page.evaluate(()=>{
     const st=mm59TrackingStatus();
     const gtagScript=document.querySelector('script[src*="gtag/js?id="]')?.src;
     const queued=(window.dataLayer||[]).filter(x=>Object.prototype.toString.call(x)==='[object Arguments]');
     return {pass:st.analyticsConsent==='yes'&&st.gaLoaded&&gtagScript?.includes('G-N22WSXXPHH')&&queued.some(x=>x[0]==='config'&&x[1]==='G-N22WSXXPHH'),state:st,gtagScript,gtagEvents:queued.map(x=>x[0])};
   });
 });
 await browser.close();
 const output={checked:results.length,failures,results};
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(output,null,2));
 console.log(JSON.stringify({checked:results.length,failures},null,2));
 if(failures.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});