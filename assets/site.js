/* Shared content enhancement. Tables scroll inside their own accessible region. */
window.enhanceHubContent = function (root) {
  root.querySelectorAll('table').forEach(function (table) {
    if (table.closest('.table-scroll')) return;
    var region = document.createElement('div');
    region.className = 'table-scroll';
    region.tabIndex = 0;
    region.setAttribute('role', 'region');
    var heading = table.parentElement.querySelector('h2');
    region.setAttribute('aria-label', (heading ? heading.textContent : '안내') + ' 표');
    table.before(region);
    region.appendChild(table);
  });
};
window.enhanceHubContent(document);
/* 59만모바일 공통 스크립트: 모바일 메뉴 열기/닫기 (JS가 꺼져도 <details>로 열고 닫힘) */
(function () {
  var menu = document.querySelector('.top-menu');
  if (!menu) return;
  function close() { menu.removeAttribute('open'); }
  menu.addEventListener('toggle', function () {
    document.documentElement.classList.toggle('menu-open', menu.open);
  });
  menu.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('a')) close();
  });
  document.addEventListener('click', function (e) {
    if (menu.open && !menu.contains(e.target)) close();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menu.open) { close(); var s = menu.querySelector('summary'); if (s) s.focus(); }
  });
})();

/* User-uploaded article images. Missing photos are invisible to public visitors. */
(function(){
  var article=document.querySelector('main .detail-article');
  if(!article)return;
  var raw=decodeURIComponent(window.location.pathname).replace(/^\/+|\/+$/g,'');
  if(!raw||raw==='guide'||raw==='tools/photo-manager')return;
  var key=raw.replace(/\//g,'--');
  var preview=new URLSearchParams(window.location.search).get('image-slots')==='1';
  var sections=Array.prototype.filter.call(article.children,function(el){
    if(el.tagName!=='SECTION'||!el.querySelector('h2'))return false;
    if(/\b(hero|faq|related|cta)\b/.test(el.className||''))return false;
    return true;
  });
  if(!sections.length)return;
  var anchors=[sections.length>1?sections[1]:sections[0]];
  if(sections.length>=3)anchors.push(sections.length>=4?sections[3]:sections[2]);
  anchors.forEach(function(anchor,i){
    var slot=('0'+(i+1)).slice(-2),name=key+'--'+slot+'.webp';
    var path='/img/article-photos/'+encodeURIComponent(name);
    var holder=document.createElement('div');holder.className='article-photo-anchor';
    holder.setAttribute('data-photo-slot',slot);
    anchor.insertAdjacentElement('afterend',holder);
    var loader=new Image();
    loader.onload=function(){
      var fig=document.createElement('figure');fig.className='article-photo-figure';
      var img=document.createElement('img');img.src=path;img.loading='lazy';img.decoding='async';
      var heading=anchor.querySelector('h2');img.alt=(heading?heading.textContent.trim():'본문')+' 관련 사진';
      fig.appendChild(img);holder.replaceWith(fig);
    };
    loader.onerror=function(){
      if(!preview){holder.remove();return;}
      var box=document.createElement('div');box.className='article-photo-preview';
      var label=document.createElement('strong');label.textContent='사진 넣을 위치 '+slot;
      var code=document.createElement('code');code.textContent=name;
      var link=document.createElement('a');link.href='/tools/photo-manager/?page='+encodeURIComponent(key)+'&slot='+slot;
      link.textContent='사진 준비·업로드 안내';
      box.appendChild(label);box.appendChild(code);box.appendChild(link);holder.replaceWith(box);
    };
    loader.src=path;
  });
})();


/* Owner-provided common icon sprite: 5 verification logos, 3 ID illustrations and eSIM.
   Never replace a fallback unless the sprite has loaded successfully. */
(function () {
  var cards=document.querySelectorAll('.auth-grid li, .img-cards--id li, .img-cards--sim li');
  if(!cards.length)return;
  var spriteUrl='/img/article-photos/common-icons-sprite.png';
  var ownerPosterPaths={'주민등록증':true,'운전면허증':true,'모바일 신분증':true,'eSIM':true};
  var coords={
    '카카오':[0,0],'토스':[1,0],'PASS':[2,0],'국민':[3,0],'신한':[4,0],
    '주민등록증':[0,1],'운전면허증':[1,1],'모바일 신분증':[2,1],'eSIM':[3,1]
  };
  function icon(name,kind){
    var el=document.createElement('span');
    el.className='common-icon-sprite common-icon-sprite--'+kind;
    el.style.backgroundPosition=(coords[name][0]*25)+'% '+(coords[name][1]*100)+'%';
    el.setAttribute('aria-hidden','true');
    return el;
  }
  var test=new Image();
  test.onload=function(){
    if(test.naturalWidth!==320||test.naturalHeight!==128)return;
    document.querySelectorAll('.auth-grid li').forEach(function(card){
      var label=card.querySelector('b'),badge=card.querySelector('.auth-badge');
      var name=label&&label.textContent.trim();
      if(!badge||!coords[name])return;
      badge.replaceChildren(icon(name,'auth'));
      badge.classList.add('auth-badge--photo');
    });
    [['.img-cards--id li','id'],['.img-cards--sim li','sim']].forEach(function(spec){
      document.querySelectorAll(spec[0]).forEach(function(card){
        var label=card.querySelector('figcaption b'),holder=card.querySelector('.ic-art');
        var name=label&&label.textContent.trim();
        if(!holder||!coords[name])return;
        if(ownerPosterPaths[name])return; /* Owner-provided full-card artwork wins over the sprite. */
        holder.replaceChildren(icon(name,spec[1]));
      });
    });
  };
  test.onerror=function(){};
  test.src=spriteUrl;
})();

/* Optional user-provided portrait posters for the three ID cards and the eSIM card.
   Keep the existing icon when a poster is unavailable. */
(function(){
  var posters={
    '주민등록증':{path:'/img/article-photos/identity-resident-card.png',w:265,h:361},
    '운전면허증':{path:'/img/article-photos/identity-driver-license.png',w:261,h:361},
    '모바일 신분증':{path:'/img/article-photos/identity-mobile-id.png',w:253,h:361},
    'eSIM':{path:'/img/article-photos/esim-guide.png',w:262,h:361}
  };
  document.querySelectorAll('.img-cards--id li, .img-cards--sim li').forEach(function(card){
    var title=card.querySelector('figcaption b');
    var holder=card.querySelector('.ic-art');
    var name=title&&title.textContent.trim(),poster=posters[name];
    if(!holder||!poster)return;
    var pic=new Image();
    pic.alt=name+' 예시 안내 이미지';
    pic.loading='eager'; /* Preload before inserting the detached image into the card. */
    pic.decoding='async';
    pic.width=poster.w;pic.height=poster.h;
    pic.className='owner-poster';
    pic.onload=function(){
      holder.classList.add('owner-poster-holder');
      holder.replaceChildren(pic);
    };
    pic.onerror=function(){};
    pic.src=poster.path;
  });
})();


/* Official illustrated walkthrough carousel with native swipe + accessible controls.
   If official images are not in the repository, existing live screenshots stay visible.
   The user's original screenshot walkthrough is never deleted. */
(function(){
  var section=document.querySelector('.detail-article .shot-guide');
  var original=section&&section.querySelector('.shot-grid');
  if(!section||!original||original.dataset.carouselMounted==='1')return;
  original.dataset.carouselMounted='1';

  var official=[
    {file:'00',title:'셀프개통 시작 안내',caption:'플랫폼에서 제공한 셀프개통 가이드 표지입니다.'},
    {file:'01',title:'개통할 통신망 선택',caption:'K망 또는 L망을 선택하고 신청을 시작합니다.'},
    {file:'02',title:'가입유형·고객유형 및 본인정보',caption:'신규가입·번호이동과 내국인·외국인을 선택하고 안내에 따라 본인정보를 입력합니다.'},
    {file:'03',title:'안면인증 방법 선택',caption:'화면에 표시되는 방법으로 안면인증을 진행합니다. 건너뛰기 사용 가능 여부는 신청 화면의 안내에 따릅니다.'},
    {file:'04',title:'간편인증 진행',caption:'카카오·토스·PASS·국민·신한 등 신청 화면에서 지원하는 수단으로 인증합니다.'},
    {file:'05',title:'유심번호 입력',caption:'K망은 F를 제외한 유심번호 19자리, L망은 모델코드와 일련번호를 확인해 입력합니다.'},
    {file:'06',title:'요금제·납부 정보 입력',caption:'이용할 요금제와 납부 관련 정보를 확인하고 신청합니다. 실제 충전 순서는 개통 방법에 따라 다릅니다.'},
    {file:'07',title:'선불 충전 방식 참고',caption:'이 이미지는 선불·후불을 비교합니다. 선불폰 이용자는 선불 충전 설명을 확인하세요.'}
  ];
  function makeSlide(item){
    var figure=document.createElement('figure');figure.className='guide-slide';
    var link=document.createElement('a');link.href='/img/guide/platform-rule-'+item.file+'.webp';
    link.target='_blank';link.rel='noopener';
    link.setAttribute('aria-label',item.title+' 이미지 크게 보기');
    var img=document.createElement('img');img.src=link.href;img.alt='앤텔레콤 공식 안내: '+item.title;
    img.width=1024;img.height=1024;img.loading='lazy';img.decoding='async';
    link.appendChild(img);figure.appendChild(link);
    var cap=document.createElement('figcaption');
    var strong=document.createElement('strong');strong.textContent=item.title;
    cap.appendChild(strong);cap.appendChild(document.createTextNode(item.caption));
    figure.appendChild(cap);return figure;
  }
  function mount(track,officialActive){
    // Preserve the insert location before moving the original track.
    var anchor=document.createElement('span');
    original.before(anchor);
    var slides=[].slice.call(track.children);
    if(!slides.length)return;
    track.classList.add('guide-carousel-track');
    track.setAttribute('role','group');
    track.setAttribute('aria-label','셀프개통 안내 이미지');
    var gallery=document.createElement('div');gallery.className='guide-carousel';
    var viewport=document.createElement('div');viewport.className='guide-carousel-viewport';
    viewport.appendChild(track);gallery.appendChild(viewport);
    var toolbar=document.createElement('div');toolbar.className='guide-carousel-toolbar';
    var counter=document.createElement('output');counter.className='guide-carousel-index';
    counter.setAttribute('aria-live','polite');
    var actions=document.createElement('div');actions.className='guide-carousel-actions';
    var previous=document.createElement('button'),next=document.createElement('button');
    previous.type='button';previous.textContent='‹';previous.setAttribute('aria-label','이전 안내 보기');
    next.type='button';next.textContent='›';next.setAttribute('aria-label','다음 안내 보기');
    actions.appendChild(previous);actions.appendChild(next);
    toolbar.appendChild(counter);toolbar.appendChild(actions);gallery.appendChild(toolbar);
    var dots=document.createElement('div');dots.className='guide-carousel-dots';
    if(slides.length<=8){
      slides.forEach(function(slide,i){
        var dot=document.createElement('button');dot.type='button';
        dot.setAttribute('aria-label',(i+1)+'번째 안내 보기');
        dot.addEventListener('click',function(){show(i)});
        dots.appendChild(dot);
      });gallery.appendChild(dots);
    }
    var helper=document.createElement('p');helper.className='guide-carousel-helper';
    helper.textContent='좌우로 밀거나 화살표로 다음 이미지를 볼 수 있습니다.';
    gallery.appendChild(helper);
    var idx=0;
    function update(i){
      idx=Math.max(0,Math.min(slides.length-1,i));
      counter.textContent=(idx+1)+' / '+slides.length;
      previous.disabled=idx===0;next.disabled=idx===slides.length-1;
      [].forEach.call(dots.children,function(d,n){
        if(n===idx)d.setAttribute('aria-current','true');
        else d.removeAttribute('aria-current');
      });
    }
    function show(i){
      update(i);
      track.scrollTo({left:slides[idx].offsetLeft-slides[0].offsetLeft,behavior:'smooth'});
    }
    previous.addEventListener('click',function(){show(idx-1)});
    next.addEventListener('click',function(){show(idx+1)});
    var raf=0;
    track.addEventListener('scroll',function(){
      if(raf)cancelAnimationFrame(raf);
      raf=requestAnimationFrame(function(){
        raf=0;
        var left=track.scrollLeft,nearest=0,distance=Infinity;
        slides.forEach(function(slide,i){
          var gap=Math.abs((slide.offsetLeft-slides[0].offsetLeft)-left);
          if(gap<distance){nearest=i;distance=gap;}
        });
        if(nearest!==idx)update(nearest);
      });
    },{passive:true});
    track.addEventListener('keydown',function(e){
      if(e.key==='ArrowRight'){e.preventDefault();show(idx+1);}
      if(e.key==='ArrowLeft'){e.preventDefault();show(idx-1);}
    });
    anchor.replaceWith(gallery);
    if(officialActive){
      var details=document.createElement('details');
      details.className='guide-original-steps';
      var summary=document.createElement('summary');
      summary.textContent='실제 신청 화면 16장 자세히 보기';
      details.appendChild(summary);details.appendChild(original);
      gallery.after(details);
      var note=section.querySelector('p.updated');
      if(note)note.textContent='앤텔레콤 플랫폼에서 제공한 공식 안내 이미지입니다. 실제 신청 화면은 아래에서 펼쳐 볼 수 있으며, 화면 구성은 달라질 수 있습니다.';
    }
    update(0);
    if(officialActive)gallery.dataset.source='official';
    else gallery.dataset.source='existing';
  }
  function hasImage(src){
    return new Promise(function(resolve){
      var test=new Image();test.onload=function(){resolve(test.naturalWidth>0)};
      test.onerror=function(){resolve(false)};test.src=src;
    });
  }
  Promise.all(official.map(function(item){
    return hasImage('/img/guide/platform-rule-'+item.file+'.webp');
  })).then(function(check){
    if(check.every(Boolean)){
      var track=document.createElement('div');track.className='shot-grid';
      official.forEach(function(item){track.appendChild(makeSlide(item));});
      mount(track,true);
    }else{
      mount(original,false);
    }
  }).catch(function(){mount(original,false)});
})();


/* Keep the common related-reading heading consistent on legacy and new articles.
   Does not touch link URLs, page titles, canonical, robots or structured data. */
(function(){
  document.querySelectorAll('#main-content .detail-article .related > .related-title')
    .forEach(function(h){if(h.textContent.trim()==='관련 안내')h.textContent='함께 보면 좋은 글';});
})();


/* Keep guide directory totals and same-topic links in sync with newly indexed L-network guides. */
(function(){
  var items=[
    {href:'/lg-모두의원칩-셀프개통/',cat:'self',title:'LG 모두의 원칩 셀프개통 방법',desc:'L망 원칩 입력부터 첫 충전까지'},
    {href:'/l망-464-요금제/',cat:'plan',title:'L망 5G 464 요금제',desc:'20GB·3Mbps·핫스팟 조건'},
    {href:'/l망-2-5gb-요금제/',cat:'plan',title:'L망 2.5GB 17,000원',desc:'통화 100분·문자 50건'}
  ],counts={all:26,self:6,plan:5};
  document.querySelectorAll('.detail-categories .gc-tile').forEach(function(a){
    var m=(a.getAttribute('href')||'').match(/#(\w+)/);
    var k=m?m[1]:'all';
    if(counts[k]!=null){var small=a.querySelector('small');if(small)small.textContent=counts[k]+'개 가이드';}
  });
  var ctx=document.querySelector('.guide-context');
  if(ctx){
    var heading=ctx.querySelector('.context-heading h2'),title=heading&&heading.textContent.trim();
    var cat=title==='셀프개통'?'self':title==='요금제·충전'?'plan':null;
    if(cat){
      var total=ctx.querySelector('.context-heading span');
      if(total)total.textContent=counts[cat]+'개 가이드';
      var place=ctx.querySelector('.context-all');
      items.filter(function(x){return x.cat===cat}).forEach(function(x,i){
        if(!ctx.querySelector('a[href="'+x.href+'"]')&&place){
          var a=document.createElement('a');a.className='context-card';a.href=x.href;
          var s=document.createElement('span');s.className='context-number';s.textContent=cat==='self'?'06':('0'+(4+i));
          var info=document.createElement('span');
          var small=document.createElement('small');small.textContent=title;
          var b=document.createElement('b');b.textContent=x.title;
          var d=document.createElement('span');d.className='context-desc';d.textContent=x.desc;
          info.append(small,b,d);a.append(s,info);place.before(a);
        }
      });
    }
  }
})();


/* 59만모바일 BLUE editorial magazine
   Progressively enhances existing indexable articles without changing their
   SEO text, canonical URLs, product facts, site navigation or activation links.
   Reference layout: summary tiles -> topic-specific cards -> numbered sections
   -> related reading -> factual next action.
*/
(function(){
  var root=document.querySelector('#main-content .detail-article');
  if(!root||root.classList.contains('magazine-blue'))return;
  root.classList.add('magazine-blue');
  var route;
  try{route=decodeURI(location.pathname)}catch(e){route=location.pathname}
  var specs={
    '/lg-모두의원칩-셀프개통/':{
      facts:[['L망 원칩 가격','8,800원'],['모델코드','5자리'],['일련번호','8자리']],
      choices:[
        ['원칩을 이미 구매했다면','https://preplan.site/lg-self/?from=59man_lgonechip_choice','L망 셀프개통 화면에서 모델코드·일련번호 입력'],
        ['원칩 구매 전이라면','/lg-원칩/','판매처와 제품 정보를 먼저 확인']
      ],
      tip:['신청 후 충전 순서','플랫폼 비대면 신청은 개통 완료 → 요금 충전 → 사용 시작 → 이후 1899-7700 해피콜 순서입니다.'],
      final:['원칩이 준비됐다면','L망을 선택하고 안면인증·간편인증을 거쳐 모델코드 5자리와 일련번호 8자리를 입력하세요.','원칩으로 개통 시작하기','https://preplan.site/lg-self/?from=59man_lgonechip_magazine']
    },
    '/l망-464-요금제/':{
      facts:[['월 요금','46,400원'],['기본 데이터','20GB'],['소진 후','최대 3Mbps']],
      choices:[
        ['실물 원칩으로 신청','/lg-모두의원칩-셀프개통/','유심을 갖고 있다면 L망 개통 순서 확인'],
        ['eSIM으로 신규가입','/v4-1/topic/esim-new/','지원 기종·EID·발급비 확인']
      ],
      tip:['핫스팟 조건을 확인하세요','L망은 기본 데이터 소진 후 핫스팟 이용이 제한됩니다. 노트북 데이터 공유가 중요하면 이 조건을 먼저 비교하세요.'],
      final:['L망 464가 맞는지 확인했다면','월 46,400원, 기본 20GB, 소진 후 최대 3Mbps 조건과 핫스팟 제한을 확인하고 진행하세요.','464 요금제로 신청하기','https://preplan.site/?from=59man_l464_magazine']
    },
    '/l망-2-5gb-요금제/':{
      facts:[['월 요금','17,000원'],['데이터','2.5GB'],['통화','100분'],['문자','50건']],
      choices:[
        ['가벼운 세컨폰 용도','/lg-모두의원칩-셀프개통/','원칩 셀프개통 순서 확인'],
        ['데이터가 더 필요하다면','/l망-464-요금제/','20GB급 요금제 이용 조건 비교']
      ],
      tip:['무제한 요금제가 아닙니다','월 통화 100분·문자 50건 제공량이 있는 요금제입니다. 업무 전화나 문자 발신이 잦다면 사용량을 먼저 살펴보세요.'],
      final:['소량 사용에 맞는다면','2.5GB·100분·50건의 제공량과 월 17,000원 요금을 확인하고 본인 명의 L망 신규가입을 진행하세요.','2.5GB 요금제로 신청하기','https://preplan.site/?from=59man_l25_magazine']
    },
    '/편의점-선불유심/':{
      facts:[['KT 바로유심','K망 · NFC'],['LG 모두의 원칩','L망 · NFC'],['다이소 고고비','L망 · NFC 미지원']],
      products:[
        ['K망 · 편의점','KT 바로유심','8,800원','CU·GS25·세븐일레븐·이마트24','/kt-바로유심/','구매처 확인'],
        ['L망 · 편의점','LG 모두의 원칩','8,800원','이마트24·스토리웨이','/lg-원칩/','원칩 정보 확인'],
        ['L망 · 다이소','고고비 유심','5,000원','다이소 · NFC 미지원','/다이소-유심/','구매 안내']
      ]
    },
    '/kt선불폰-개통/':{
      facts:[['KT 바로유심','K망'],['유심정보','19자리'],['편의점 판매가','8,800원']],
      choices:[
        ['바로유심 준비 완료','https://preplan.site/?from=59man_ktbaro_magazine','K망 개통 신청 화면으로'],
        ['아직 구매 전이라면','/kt-바로유심/','편의점 판매처 확인']
      ]
    }
  };
  var spec=specs[route]||null;
  function el(tag,cl,text){
    var node=document.createElement(tag);
    if(cl)node.className=cl;
    if(text!==undefined)node.textContent=text;
    return node;
  }
  var hero=root.querySelector(':scope > .hero');
  if(spec&&hero){
    var insertAt=hero;
    if(spec.facts){
      var facts=el('div','sm-quick'+(spec.facts.length===4?' is-four':''));
      facts.setAttribute('aria-label','핵심 정보 요약');
      spec.facts.forEach(function(f){
        var item=el('div','sm-quick-item');
        item.append(el('span','sm-quick-label',f[0]),el('strong','sm-quick-value',f[1]));
        facts.appendChild(item);
      });
      insertAt.after(facts);insertAt=facts;
    }
    if(spec.products){
      var products=el('div','sm-product-grid is-three');
      products.setAttribute('aria-label','유심 제품별 상세 안내');
      spec.products.forEach(function(p){
        var card=el('div','sm-product-card');
        card.appendChild(el('span','sm-product-card-tag',p[0]));
        card.appendChild(el('h3','',p[1]));
        card.appendChild(el('strong','sm-product-price',p[2]));
        card.appendChild(el('p','',p[3]));
        var link=el('a','',p[5]);link.href=p[4];card.appendChild(link);
        products.appendChild(card);
      });
      insertAt.after(products);insertAt=products;
    }
    if(spec.choices){
      var choices=el('div','sm-choice-grid');
      choices.setAttribute('aria-label','상황에 맞는 다음 단계');
      spec.choices.forEach(function(a){
        var link=el('a','');link.href=a[1];
        link.append(el('strong','',a[0]),el('span','',a[2]));
        choices.appendChild(link);
      });
      insertAt.after(choices);
    }
  }
  var excluded=['hero','answer-card','faq','cta','plan-cards','activation-flow'];
  var sections=Array.from(root.children).filter(function(x){
    return x.tagName==='SECTION'&&!excluded.some(function(c){return x.classList.contains(c)})&&
      Array.from(x.children).some(function(y){return y.tagName==='H2'});
  });
  sections.forEach(function(section,i){
    section.classList.add('magazine-section');
    if(!section.id)section.id='magazine-section-'+(i+1);
    var h=Array.from(section.children).find(function(y){return y.tagName==='H2'});
    if(h)h.setAttribute('data-sm-number',('0'+(i+1)).slice(-2));
  });
  if(sections.length>=3){
    var nav=el('nav','sm-page-nav');
    nav.setAttribute('aria-label','이 페이지 목차');
    sections.slice(0,7).forEach(function(section){
      var h=Array.from(section.children).find(function(y){return y.tagName==='H2'});
      if(!h)return;
      var a=el('a','',h.textContent.trim());
      a.setAttribute('href','#'+section.id);
      nav.appendChild(a);
    });
    var answer=root.querySelector(':scope > .answer-card');
    if(answer)answer.after(nav);
    else {
      var lead=root.querySelector(':scope > .detail-lead-visual');
      (lead||hero||root.firstElementChild).after(nav);
    }
  }
  if(spec&&spec.tip&&sections.length){
    var tip=el('div','sm-tip');
    tip.append(el('strong','',spec.tip[0]),el('span','',spec.tip[1]));
    // Put the warning near the first explanation, rather than the top conversion CTA.
    sections[0].appendChild(tip);
  }
  if(spec&&spec.final){
    var [heading,summary,action,url]=spec.final;
    var final=el('aside','sm-final');
    final.setAttribute('aria-label','핵심 내용 정리');
    final.append(el('h2','',heading),el('p','',summary));
    var link=el('a','',action+' →');link.href=url;final.appendChild(link);
    var related=root.querySelector(':scope > .related');
    if(related)related.before(final);else root.appendChild(final);
  }
})();
