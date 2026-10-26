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


/* Optional, owner-uploaded common card images. Missing assets retain the original UI. */
(function () {
  var base = '/img/article-photos/';
  var auth = {'카카오':'common-auth-kakao.webp','토스':'common-auth-toss.webp',
              'PASS':'common-auth-pass.webp','국민':'common-auth-kb.webp',
              '신한':'common-auth-shinhan.webp'};
  var identity = {'주민등록증':'common-id-resident.webp',
                  '운전면허증':'common-id-driver.webp',
                  '모바일 신분증':'common-id-mobile.webp'};
  function preload(file, show) {
    var url = base + file, probe = new Image();
    probe.onload = function () { show(url); };
    probe.onerror = function () {}; // Keep the text or illustration fallback.
    probe.src = url;
  }
  document.querySelectorAll('.auth-grid li').forEach(function (card) {
    var label = card.querySelector('b'), badge = card.querySelector('.auth-badge');
    var name = label && label.textContent.trim();
    if (!badge || !auth[name]) return;
    preload(auth[name], function (url) {
      var img = document.createElement('img');
      img.src = url;
      img.alt = '';
      img.setAttribute('aria-hidden','true');
      img.width = 28; img.height = 28;
      badge.replaceChildren(img);
      badge.classList.add('auth-badge--photo');
    });
  });
  function swap(selector, names) {
    document.querySelectorAll(selector).forEach(function (card) {
      var label=card.querySelector('figcaption b'), img=card.querySelector('.ic-art img');
      var name=label&&label.textContent.trim();
      if(!img||!names[name])return;
      preload(names[name],function(url) {
        img.src=url;
        img.alt=name+' 안내 이미지';
        img.removeAttribute('aria-hidden');
        img.width=96;img.height=96;
        img.classList.add('common-card-photo');
      });
    });
  }
  swap('.img-cards--id li', identity);
  swap('.img-cards--sim li', {'eSIM':'common-esim.webp'});
})();
