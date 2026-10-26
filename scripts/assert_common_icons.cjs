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
  await page.waitForFunction(()=>!!document.querySelector('.shot-guide .guide-carousel'));
  // The four SIM posters are below the first viewport and use browser lazy loading.
  // Scroll them into view and wait for their actual decoding before checking naturalWidth.
  await page.locator('.img-cards--sim').scrollIntoViewIfNeeded();
  await page.waitForFunction(()=>[...document.querySelectorAll('.img-cards--sim .ic-art img')].length===4 &&
    [...document.querySelectorAll('.img-cards--sim .ic-art img')].every(img=>img.complete&&img.naturalWidth>0));
  const result=await page.evaluate(()=>({
    carousel:(function(){
      const box=document.querySelector('.shot-guide .guide-carousel');
      const track=box.querySelector('.guide-carousel-track');
      const cards=[...track.children];
      const outputs=box.querySelector('.guide-carousel-index');
      const dotCount=box.querySelectorAll('.guide-carousel-dots button').length;
      const officialPaths=cards.map(c=>c.querySelector('img')?.getAttribute('src'));
      const originalSteps=!!document.querySelector('.shot-guide .guide-original-steps .shot-grid');
      const next=box.querySelector('[aria-label="다음 안내 보기"]');
      const prev=box.querySelector('[aria-label="이전 안내 보기"]');
      return {present:!!box,source:box.dataset.source,count:cards.length,
        trackDisplay:getComputedStyle(track).display,
        counter:outputs.textContent,buttonNames:!!next&&!!prev,dotCount,officialPaths,originalSteps,
        widths:cards.map(x=>x.getBoundingClientRect().width),
        overflow:track.scrollWidth>track.clientWidth
      };
    })(),

    auth:document.querySelectorAll('.auth-grid .common-icon-sprite--auth').length,
    idPosters:document.querySelectorAll('.img-cards--id .owner-poster').length,
    esimPosters:document.querySelectorAll('.img-cards--sim .owner-poster').length,
    icons:document.querySelectorAll('.common-icon-sprite').length,
    posterAssets:[...document.querySelectorAll('.owner-poster')].every(i=>i.complete&&i.naturalWidth>0&&i.alt),
    backgrounds:[...document.querySelectorAll('.common-icon-sprite')].every(e=>getComputedStyle(e).backgroundImage.includes('common-icons-sprite.png')),
    broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0).length,
    overflow:document.documentElement.scrollWidth>innerWidth+1,
    simLayout:(function(){
      const grid=document.querySelector('.img-cards--sim .img-cards-grid');
      const nodes=[...grid.children];
      const boxes=nodes.map(n=>n.getBoundingClientRect());
      const figures=nodes.map(n=>n.querySelector('figure').getBoundingClientRect());
      const imageBoxes=nodes.map(n=>n.querySelector('.ic-art').getBoundingClientRect());
      const images=nodes.map(n=>n.querySelector('.ic-art img').getBoundingClientRect());
      return {
        count:nodes.length,
        margins:nodes.map(n=>getComputedStyle(n).marginTop),
        equalWidths:Math.max(...figures.map(x=>x.width))-Math.min(...figures.map(x=>x.width))<=1,
        equalHeights:Math.max(...figures.map(x=>x.height))-Math.min(...figures.map(x=>x.height))<=1,
        imageBoxHeights:imageBoxes.map(x=>Math.round(x.height)),
        imageAlignment:imageBoxes.every((r,i)=>Math.abs((r.left+r.right)/2-(images[i].left+images[i].right)/2)<=1),
        rowTops:boxes.map(x=>Math.round(x.top)),
        noOverlap:boxes[2].top>=boxes[0].bottom+8,
        imageLoaded:nodes.every(n=>{const img=n.querySelector('.ic-art img');return img&&img.complete&&img.naturalWidth>0;})
      };
    })(),
    relatedStyle:(function(){
      const nav=document.querySelector('.detail-article .related');
      const link=nav.querySelector('a');
      return {
        title:nav.querySelector('h2').textContent.trim(),
        border:getComputedStyle(nav).borderTopStyle,
        weight:parseInt(getComputedStyle(link).fontWeight,10),
        color:getComputedStyle(link).color,
        hrefs:[...nav.querySelectorAll('a')].every(a=>a.getAttribute('href').startsWith('/'))
      };
    })(),
    inlineLinkColor:getComputedStyle(document.querySelector('.detail-article a[href="/태블릿-소유자-회원번호/"]')).color,
    idLayout:(function(){
      const grid=document.querySelector('.img-cards--id .img-cards-grid');
      const cards=[...grid.children];
      const bounds=cards.map(e=>e.getBoundingClientRect());
      const area=grid.getBoundingClientRect();
      return {
        count:cards.length,
        margins:cards.map(e=>getComputedStyle(e).marginTop),
        widths:bounds.map(e=>e.width),
        firstRowAligned:Math.abs(bounds[0].top-bounds[1].top)<=1,
        centeredLast:Math.abs((bounds[2].left+bounds[2].right)/2-(area.left+area.right)/2)<=1,
        secondRowBelow:bounds[2].top>=bounds[0].bottom+8
      };
    })(),
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
     ||!result.carousel.present||!['existing','official'].includes(result.carousel.source)
     ||![8,16].includes(result.carousel.count)||result.carousel.trackDisplay!=='flex'
     ||(result.carousel.source==='official'&&(result.carousel.count!==8||result.carousel.dotCount!==8||!result.carousel.originalSteps
       ||!['00','01','02','03','04','05','06','07'].every((n,i)=>result.carousel.officialPaths[i]?.endsWith('platform-rule-'+n+'.webp'))))
     ||(result.carousel.source==='existing'&&(result.carousel.count!==16||result.carousel.dotCount!==0))
     ||result.carousel.counter!=='1 / '+result.carousel.count
     ||!result.carousel.buttonNames||!result.carousel.overflow
     ||Math.max(...result.carousel.widths)-Math.min(...result.carousel.widths)>1
     ||result.simLayout.count!==4||!result.simLayout.equalWidths||!result.simLayout.equalHeights
     ||!result.simLayout.imageAlignment||!result.simLayout.noOverlap||!result.simLayout.imageLoaded
     ||result.simLayout.margins.some(m=>m!=='0px')
     ||result.simLayout.imageBoxHeights.some(h=>h!==150)
     ||result.simLayout.rowTops[0]!==result.simLayout.rowTops[1]
     ||result.simLayout.rowTops[2]!==result.simLayout.rowTops[3]
     ||result.relatedStyle.title!=='함께 보면 좋은 글'
     ||result.relatedStyle.border!=='solid'||result.relatedStyle.weight<700
     ||result.relatedStyle.color!=='rgb(23, 92, 211)'||!result.relatedStyle.hrefs
     ||result.inlineLinkColor!=='rgb(23, 92, 211)'
     ||result.idLayout.count!==3||!result.idLayout.firstRowAligned
     ||!result.idLayout.centeredLast||!result.idLayout.secondRowBelow
     ||result.idLayout.margins.some(m=>m!=='0px')
     ||spread(result.idLayout.widths)>1
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
