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
    pic.loading='lazy';
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
