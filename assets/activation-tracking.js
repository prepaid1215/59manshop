/* 59만모바일: first-party activation CTA attribution, no personal data.
   GA4 G-N22WSXXPHH is from public preplan.site GTM. Load after opt-in only. */
(function () {
  'use strict';
  var GA_ID='G-N22WSXXPHH';
  var KEY='mm59_analytics_consent_v1';
  var allowedHost='preplan.site';
  var currentPath=window.location.pathname||'/';
  var consent='unset';
  try{consent=localStorage.getItem(KEY)||'unset'}catch(e){}
  function slot(a){
    if(a.matches('.bottom-bar-main'))return 'sticky';
    if(a.matches('.landing-primary-cta,.hero-cta'))return 'hero';
    if(a.matches('.nav-apply,.menu-cta'))return 'menu';
    if(a.matches('.landing-plan-cta'))return 'plan';
    if(a.closest('.sm-final'))return 'summary';
    if(a.closest('.sm-choice-grid'))return 'choice';
    if(a.matches('.primary-cta,.button'))return 'content';
    if(a.closest('footer'))return 'footer';
    return 'body';
  }
  function sourceCode(place){
    var path=currentPath.replace(/^\/+|\/+$/g,'')||'home';
    try{path=decodeURIComponent(path)}catch(e){}
    path=path.replace(/\//g,'_').replace(/[^a-zA-Z0-9가-힣_-]/g,'-').slice(0,76);
    return '59man_'+path+'_'+place;
  }
  function getPreplanUrl(a){
    try{
      var u=new URL(a.getAttribute('href'),location.href);
      if(u.protocol==='https:'&&u.hostname===allowedHost)return u;
    }catch(e){}
    return null;
  }
  function analyticsEvent(name,props){
    if(consent!=='yes')return;
    if(typeof window.gtag==='function'){
      window.gtag('event',name,Object.assign({send_to:GA_ID,transport_type:'beacon'},props));
    }
  }
  function onLink(e){
    var a=e.target&&e.target.closest&&e.target.closest('a[href]');
    if(!a)return;
    var u=getPreplanUrl(a);
    if(!u)return;
    var place=slot(a);
    if(!u.searchParams.get('from')){
      u.searchParams.set('from',sourceCode(place));
      a.href=u.href;
    }
    var source=u.searchParams.get('from')||sourceCode(place);
    var dest=u.pathname==='/'?'activation_home':'information';
    var payload={
      event:'mm59_outbound_click',
      mm_source:source,
      mm_origin_path:currentPath,
      mm_placement:place,
      mm_destination_type:dest
    };
    window.dataLayer=window.dataLayer||[];
    window.dataLayer.push(payload);
    analyticsEvent('mm59_outbound_click',{
      source_code:source,
      source_path:currentPath,
      placement:place,
      destination_type:dest
    });
  }
  // Capturing updates the actual href before navigation; delegated for JS-created links.
  document.addEventListener('click',onLink,true);
  document.addEventListener('auxclick',function(e){if(e.button===1)onLink(e)},true);
  function loadGA(){
    if(window.__mm59GaLoaded)return;
    window.__mm59GaLoaded=true;
    window.dataLayer=window.dataLayer||[];
    window.gtag=window.gtag||function(){window.dataLayer.push(arguments)};
    window.gtag('js',new Date());
    window.gtag('consent','default',{
      analytics_storage:'granted',
      ad_storage:'denied',
      ad_user_data:'denied',
      ad_personalization:'denied'
    });
    window.gtag('set','linker',{domains:['www.59man.shop','59man.shop','preplan.site'],accept_incoming:true});
    window.gtag('config',GA_ID,{
      allow_google_signals:false,
      allow_ad_personalization_signals:false,
      // Exclude URL query strings from GA4 automatic page_view (may contain user data).
      page_location:location.origin+location.pathname,
      page_referrer:document.referrer.split('?')[0].split('#')[0],
      cookie_flags:'SameSite=Lax;Secure'
    });
    var sc=document.createElement('script');
    sc.async=true;sc.src='https://www.googletagmanager.com/gtag/js?id='+GA_ID;
    document.head.appendChild(sc);
  }
  function setConsent(value){
    consent=value;
    try{localStorage.setItem(KEY,value)}catch(e){}
    var dlg=document.getElementById('mm59-analytics-consent');
    if(dlg)dlg.remove();
    if(value==='yes'&&window.__mm59GaLoaded&&typeof window.gtag==='function'){
      window.gtag('consent','update',{
        analytics_storage:'granted',ad_storage:'denied',
        ad_user_data:'denied',ad_personalization:'denied'
      });
    }
    if(value==='yes')loadGA();
  }
  function consentNotice(){
    if(document.getElementById('mm59-analytics-consent'))return;
    var node=document.createElement('aside');
    node.id='mm59-analytics-consent';
    node.setAttribute('role','region');
    node.setAttribute('aria-label','방문 통계 동의');
    node.style.cssText='position:fixed;z-index:2147483000;bottom:80px;left:50%;transform:translateX(-50%);box-sizing:border-box;width:calc(100% - 24px);max-width:456px;padding:13px 15px;background:#fff;color:#17305c;border:1px solid #d8e3f4;border-radius:12px;box-shadow:0 10px 34px rgba(0,0,0,.14);font:13px/1.5 sans-serif';
    var p=document.createElement('p');
    p.textContent='방문·개통 버튼 클릭 통계 수집에 동의하시나요? 이름·전화번호·인증정보는 이벤트에 보내지 않습니다.';
    p.style.cssText='margin:0 0 9px';
    node.appendChild(p);
    var controls=document.createElement('div');
    controls.style.cssText='display:flex;gap:8px;justify-content:flex-end';
    var no=document.createElement('button');
    no.type='button';no.textContent='거절';
    no.style.cssText='padding:7px 12px;border:1px solid #c2cfe0;border-radius:8px;color:#17305c;background:#fff;cursor:pointer';
    var yes=document.createElement('button');
    yes.type='button';yes.textContent='동의';
    yes.style.cssText='padding:7px 12px;border:1px solid #235ccc;border-radius:8px;color:#fff;background:#235ccc;cursor:pointer';
    no.addEventListener('click',function(){setConsent('no')});
    yes.addEventListener('click',function(){setConsent('yes')});
    controls.append(no,yes);node.appendChild(controls);
    document.body.appendChild(node);
  }
  function settingsButton(){
    if(document.getElementById('mm59-analytics-settings'))return;
    var footer=document.querySelector('footer .footer-info')||document.querySelector('footer');
    if(!footer)return;
    var button=document.createElement('button');
    button.id='mm59-analytics-settings';
    button.type='button';
    button.textContent='방문 통계 설정';
    button.style.cssText='background:transparent;border:0;padding:4px 0;color:inherit;text-decoration:underline;cursor:pointer;font:inherit';
    button.addEventListener('click',function(){
      // Withdrawing consent stops future events and avoids loading GA on reload.
      if(consent==='yes'&&typeof window.gtag==='function'){
        window.gtag('consent','update',{
          analytics_storage:'denied',ad_storage:'denied',
          ad_user_data:'denied',ad_personalization:'denied'
        });
      }
      consent='unset';
      try{localStorage.removeItem(KEY)}catch(e){}
      consentNotice();
    });
    footer.appendChild(button);
  }
  function startup(){
    settingsButton();
    if(consent==='yes')loadGA();
    else if(consent==='unset')consentNotice();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',startup);
  else startup();
  // Explicit, local-only hook for diagnostics. It never marks a verified activation.
  window.mm59TrackingStatus=function(){return {analyticsConsent:consent,gaLoaded:!!window.__mm59GaLoaded}};
})();