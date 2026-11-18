/* 59만모바일 — 쿠키 없는 일별 집계 (개인 식별자/원시 이벤트 미저장).
 * Only day, page path, coarse traffic source, event kind, button location, network.
 * Explicit "수집 중지" in footer applies to this counter as well.
 */
(function () {
  'use strict';
  var ENDPOINT='https://jvatfvqudcyrocykvpot.supabase.co/functions/v1/mm59-daily-aggregate';
  var ALLOWED_SOURCES=['chatgpt','gemini','google','naver','bing','threads','instagram','kakao','direct','other'];
  var ALLOWED_NETWORKS=['kt','lg','unknown'];
  var path=window.location.pathname||'/';

  // Avoid collecting URL query strings, full referrers, identifiers, device/IP fingerprints.
  try { path=decodeURIComponent(path); } catch (_) { return; }
  if (!/^\/[가-힣A-Za-z0-9_/-]*$/.test(path) || path.length>180) return;

  function sourceFromName(value) {
    var n=(value||'').toLowerCase().trim();
    if (/^(chatgpt|chatgpt\.com|chat\.openai\.com|openai)$/.test(n)) return 'chatgpt';
    if (/^(gemini|gemini\.google\.com|google-gemini)$/.test(n)) return 'gemini';
    if (/^(google|google\.com|google\.co\.kr)$/.test(n)) return 'google';
    if (/^(naver|naver\.com|blog\.naver\.com)$/.test(n)) return 'naver';
    if (/^(bing|bing\.com)$/.test(n)) return 'bing';
    if (/^(threads|threads\.net|threads\.com)$/.test(n)) return 'threads';
    if (/^(instagram|instagram\.com)$/.test(n)) return 'instagram';
    if (/^(kakao|kakaotalk|pf\.kakao\.com)$/.test(n)) return 'kakao';
    return '';
  }

  function sourceFromHostname(host) {
    var h=(host||'').toLowerCase();
    if (/(^|\.)chatgpt\.com$|(^|\.)chat\.openai\.com$/.test(h)) return 'chatgpt';
    if (/(^|\.)gemini\.google\.com$/.test(h)) return 'gemini';
    if (/(^|\.)google\.([a-z.]+)$/.test(h)) return 'google';
    if (/(^|\.)naver\.com$/.test(h)) return 'naver';
    if (/(^|\.)bing\.com$/.test(h)) return 'bing';
    if (/(^|\.)threads\.(net|com)$/.test(h)) return 'threads';
    if (/(^|\.)instagram\.com$/.test(h)) return 'instagram';
    if (/(^|\.)kakao\.(com|talk)$/.test(h)) return 'kakao';
    return '';
  }

  function identifySource() {
    try {
      var qs=new URLSearchParams(window.location.search);
      var campaign=sourceFromName(qs.get('utm_source')||'');
      if (campaign) return campaign;
    } catch (_) {}
    try {
      if (!document.referrer) return 'direct';
      var host=new URL(document.referrer).hostname;
      if (host===window.location.hostname || host==='59man.shop' || host==='www.59man.shop') return 'direct';
      return sourceFromHostname(host)||'other';
    } catch (_) { return 'other'; }
  }

  var source=identifySource();
  if (ALLOWED_SOURCES.indexOf(source)===-1) source='other';

  function optedOut() {
    // Read the existing site-wide voluntary privacy choice. No tracking key is created.
    try {
      if (window.mm59TrackingStatus && window.mm59TrackingStatus().optedOut) return true;
      return window.localStorage.getItem('mm59_analytics_consent_v1')==='no';
    } catch (_) { return false; }
  }

  function send(kind,placement,network) {
    if (optedOut() || !window.fetch) return;
    if (ALLOWED_NETWORKS.indexOf(network)===-1) network='unknown';
    var data=JSON.stringify({
      kind:kind, page:path, source:source,
      placement:placement, network:network
    });
    // This fetch is fire-and-forget, does not block navigation, never includes cookies.
    try {
      window.fetch(ENDPOINT,{
        method:'POST',
        mode:'cors',
        credentials:'omit',
        cache:'no-store',
        keepalive:true,
        referrerPolicy:'no-referrer',
        headers:{'Content-Type':'text/plain;charset=UTF-8'},
        body:data
      }).catch(function(){});
    } catch (_) {}
  }

  function placementOf(a) {
    if (a.matches('.bottom-bar-main,.bottom-bar-sub')) return 'sticky';
    if (a.matches('.nav-apply,.menu-cta')) return 'menu';
    if (a.closest('.sm-quick-apply,.hero,.home-hero')) return 'hero';
    if (a.matches('.landing-plan-cta')) return 'plan';
    if (a.closest('.sm-final,.sm-answer-next')) return 'summary';
    if (a.closest('.sm-choice-grid')) return 'choice';
    if (a.closest('footer')) return 'footer';
    if (a.matches('.primary-cta,.button')) return 'content';
    return 'body';
  }
  function destinationOf(a) {
    var u;
    try { u=new URL(a.href,window.location.href); } catch (_) { return null; }
    if (u.protocol!=='https:') return null;
    if (u.hostname==='pf.kakao.com' && u.pathname.replace(/\/$/,'')==='/_akxmKn/chat')
      return {kind:'kakao_click',network:'unknown'};
    if (u.hostname==='preplan.site' || u.hostname==='59만모바일.com' ||
        u.hostname==='xn--59-9f0jm2a95cuu4a.com')
      return {kind:'signup_click',network:'unknown'};
    if (u.hostname==='www.n-telecom.co.kr' &&
        /^\/59man\/view\/open\/(kt|lg)\/face_auth\.aspx$/i.test(u.pathname))
      return {kind:'signup_click',network:u.pathname.match(/\/(kt|lg)\//i)[1].toLowerCase()};
    return null;
  }
  function onClick(evt) {
    var a=evt.target && evt.target.closest && evt.target.closest('a[href]');
    if (!a) return;
    var dest=destinationOf(a);
    if (!dest) return;
    send(dest.kind,placementOf(a),dest.network);
  }
  // Delegated capture supports links generated by article scripts.
  document.addEventListener('click',onClick,true);
  document.addEventListener('auxclick',function(evt){
    if (evt.button===1) onClick(evt);
  },true);

  send('page_view','page','unknown');
})();
