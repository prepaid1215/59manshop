const fs=require('fs'),path=require('path'),{chromium}=require('./browser_runtime.cjs');
const root=path.join(__dirname,'..'),out=path.join(root,'reports/ui/ai-media-previews');
const refs=['kt-baro-concept-a.png','lg-onechip-concept-a.png','daiso-concept-a.png','three-sim-concept-a.png','kt-number-mockup.png','lg-number-mockup.png','kt-baro-reference-style.png','lg-onechip-reference-style.png','daiso-back-reference-style.png','three-sim-reference-style.png','tablet-member-2893496-ai.png'];
for(const file of refs){const p=path.join(root,'img/ai-examples',file);if(!fs.existsSync(p)||fs.statSync(p).size<1000)throw Error('Missing media '+file);}
const pages=[
 ['/kt-바로유심/','kt-baro-reference-style.png'],
 ['/lg-원칩/','lg-onechip-reference-style.png'],
 ['/다이소-유심/','daiso-concept-a.png'],
 ['/v4-1/topic/sim-buy-where/','three-sim-reference-style.png'],
 ['/태블릿-소유자-회원번호/','tablet-member-2893496-ai.png']
];
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true});const results=[],failures=[];
for(const width of [390,480,1440]){const page=await browser.newPage({viewport:{width,height:880}});
for(const [route,file]of pages){const errs=[],listener=e=>errs.push(e.message);page.on('pageerror',listener);
await page.goto('http://127.0.0.1:8765'+route,{waitUntil:'load'});
const o=await page.evaluate(async f=>{const ai=document.querySelector('.sm-ai-photo-preview');const img=ai?.querySelector('img');if(img){img.loading='eager';await img.decode().catch(()=>{});}const article=document.querySelector('#main-content .detail-article');
return{image:img?.getAttribute('src'),alt:img?.alt,loaded:!!(img?.complete&&img.naturalWidth===200&&img.naturalHeight===200),caption:ai?.textContent?.trim(),imgWidth:img?.getBoundingClientRect().width,articleWidth:article?.getBoundingClientRect().width,css:getComputedStyle(ai||article).display,overflow:document.documentElement.scrollWidth>innerWidth+1,cta:article?.querySelector('.hero-cta')?.getAttribute('href'),member:routeIsMember(location.pathname)?document.querySelector('#member-number')?.textContent?.trim():null};
function routeIsMember(p){return decodeURI(p).includes('태블릿-소유자-회원번호');}},file);
const pass=o.loaded&&o.image==='/img/ai-examples/'+file&&o.alt&&o.caption?.includes('AI')&&o.imgWidth<=135&&o.articleWidth<=480.5&&!o.overflow&&o.cta?.startsWith('https://preplan.site/')&&(!route.includes('태블릿-소유자-회원번호')||o.member==='2893496')&&!errs.length;
const row={route,width,pass,...o,errors:errs};results.push(row);if(!pass)failures.push(row);
if(width===390)await page.screenshot({path:path.join(out,encodeURIComponent(route)+'-390.png'),fullPage:false});
page.removeListener('pageerror',listener);
}await page.close();}
await browser.close();fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({checked:results.length,failures},null,2));console.log(JSON.stringify({checked:results.length,failures},null,2));if(failures.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
