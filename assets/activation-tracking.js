/* 59만모바일: activation CTA attribution with privacy-respecting defaults.
   Unset = no GA cookies (Consent Mode denied; cookieless pings). Yes = cookie opt-in.
   No = explicit measurement opt-out. Never send identifying form data. */
(function () {
  'use strict';
  var GA_ID='G-N7ZW223ESP';
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
    if(consent==='no')return;
    if(typeof window.gtag==='function'){
      window.gtag('event',name,Object.assign({send_to:GA_ID,transport_type:'beacon'},props));
    }
  }
  function isKakaoChat(a){
    try {
      var u=new URL(a.getAttribute('href'),location.href);
      return u.protocol==='https:'&&u.hostname==='pf.kakao.com'&&u.pathname.replace(/\/$/,'')==='/_akxmKn/chat';
    }catch(e){return false}
  }
  function onLink(e){
    var a=e.target&&e.target.closest&&e.target.closest('a[href]');
    if(!a)return;
    var u=getPreplanUrl(a);
    var place=slot(a);
    if(!u){
      if(isKakaoChat(a)){
        if(consent!=='no'){
          window.dataLayer=window.dataLayer||[];
          window.dataLayer.push({event:'mm59_contact_click',mm_channel:'kakao',mm_origin_path:currentPath,mm_placement:place});
          analyticsEvent('mm59_contact_click',{channel:'kakao',source_path:currentPath,placement:place});
        }
      }
      return;
    }
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
    if(consent!=='no'){
      window.dataLayer=window.dataLayer||[];
      window.dataLayer.push(payload);
      analyticsEvent('mm59_outbound_click',{
        source_code:source,
        source_path:currentPath,
        placement:place,
        destination_type:dest
      });
    }
  }
  // Capturing updates the actual href before navigation; delegated for JS-created links.
  document.addEventListener('click',onLink,true);
  document.addEventListener('auxclick',function(e){if(e.button===1)onLink(e)},true);
  function loadGA(){
    if(window.__mm59GaLoaded||consent==='no')return;
    window['ga-disable-'+GA_ID]=false;
    window.__mm59GaLoaded=true;
    window.dataLayer=window.dataLayer||[];
    window.gtag=window.gtag||function(){window.dataLayer.push(arguments)};
    // Default deny is registered before Google tag initialization.
    window.gtag('consent','default',{
      analytics_storage:consent==='yes'?'granted':'denied',
      ad_storage:'denied',
      ad_user_data:'denied',
      ad_personalization:'denied'
    });
    window.gtag('js',new Date());
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
    try {
      if(value==='unset')localStorage.removeItem(KEY);
      else localStorage.setItem(KEY,value);
    } catch(e) {}
    var dlg=document.getElementById('mm59-analytics-consent');
    if(dlg)dlg.remove();

    if(value==='no'){
      // Do not transmit analytics events after an explicit opt-out.
      window['ga-disable-'+GA_ID]=true;
      if(window.__mm59GaLoaded&&typeof window.gtag==='function'){
        window.gtag('consent','update',{
          analytics_storage:'denied',ad_storage:'denied',
          ad_user_data:'denied',ad_personalization:'denied'
        });
      }
      return;
    }
    window['ga-disable-'+GA_ID]=false;
    if(window.__mm59GaLoaded&&typeof window.gtag==='function'){
      window.gtag('consent','update',{
        analytics_storage:value==='yes'?'granted':'denied',
        ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'
      });
    } else loadGA();
  }
  // Footer-only preference panel: do not obstruct the first screen.
  function consentNotice(){
    if(document.getElementById('mm59-analytics-consent'))return;
    var node=document.createElement('aside');
    node.id='mm59-analytics-consent';
    node.setAttribute('role','region');
    node.setAttribute('aria-label','방문 통계 설정');
    node.style.cssText='box-sizing:border-box;width:100%;max-width:456px;margin:12px 0 0;padding:12px 14px;background:#f7f9fc;color:#17305c;border:1px solid #d8e3f4;border-radius:10px;font:13px/1.5 sans-serif';
    var p=document.createElement('p');
    p.textContent='기본 설정은 분석 쿠키 없이 방문·개통 버튼 클릭의 제한적 측정 신호를 Google에 전송합니다. 통계를 끄거나 분석 쿠키 사용에 동의할 수 있습니다. 이름·전화번호·인증정보는 전송하지 않습니다.';
    p.style.cssText='margin:0 0 9px';
    node.appendChild(p);
    var controls=document.createElement('div');
    controls.style.cssText='display:flex;gap:8px;justify-content:flex-start;flex-wrap:wrap';
    function option(label,value,primary){
      var button=document.createElement('button');
      button.type='button';button.textContent=label;
      button.style.cssText='padding:7px 11px;border:1px solid '+(primary?'#235ccc':'#c2cfe0')+';border-radius:8px;color:'+(primary?'#fff':'#17305c')+';background:'+(primary?'#235ccc':'#fff')+';cursor:pointer';
      button.addEventListener('click',function(){setConsent(value)});
      controls.appendChild(button);
    }
    option('수집 중지','no',false);
    option('쿠키 없이','unset',false);
    option('쿠키 동의','yes',true);
    var close=document.createElement('button');
    close.type='button';close.textContent='닫기';
    close.style.cssText='padding:7px 11px;border:1px solid #c2cfe0;border-radius:8px;color:#17305c;background:#fff;cursor:pointer';
    close.addEventListener('click',function(){node.remove()});
    controls.appendChild(close);node.appendChild(controls);
    var footer=document.querySelector('footer .footer-info')||document.querySelector('footer');
    if(footer)footer.appendChild(node);
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
      var existing=document.getElementById('mm59-analytics-consent');
      if(existing){existing.remove();return;}
      consentNotice();
    });
    footer.appendChild(button);
  }
  function startup(){
    settingsButton();
    // No forced popup; cookieless measurement unless the visitor opts out.
    if(consent!=='no')loadGA();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',startup);
  else startup();
  // Explicit, local-only hook for diagnostics. It never marks a verified activation.
  window.mm59TrackingStatus=function(){return {analyticsConsent:consent,gaLoaded:!!window.__mm59GaLoaded,cookieless:consent==='unset',optedOut:consent==='no'}};
})();