/* v2.6.2 directory adapter. Real anchors and static cards work without JS. */
(() => {
  'use strict';
  const root=document.querySelector('.visual-guide');if(!root)return;
  const data=JSON.parse(document.getElementById('gc-data').textContent);
  const list=document.getElementById('gc-list'),items=[...list.children];
  const tiles=[...root.querySelectorAll('.gh-category')],bar=root.querySelector('.gh-categories');
  const input=document.getElementById('gc-q'),clear=document.getElementById('gc-clear');
  const filters=document.getElementById('gh-subfilters'),section=document.getElementById('gc-section');
  const mobile=matchMedia('(max-width:768px)'),reduce=matchMedia('(prefers-reduced-motion:reduce)');
  const norm=s=>String(s||'').toLocaleLowerCase('ko-KR').replace(/\s+/g,'');
  const index=items.map(li=>norm(li.textContent+' '+li.firstElementChild.dataset.kw));
  const aliases={preparation:'check','self-activation':'self',identity:'fix',usim:'sim','number-transfer':'move',billing:'plan'};
  let category='all',tag='',dragged=null,justDragged=false;
  const scrollTo=el=>el.scrollIntoView({behavior:reduce.matches?'auto':'smooth',block:'start'});
  function updateUrl(push){
    const url=new URL(location.href);url.searchParams.delete('guide_category');
    input.value.trim()?url.searchParams.set('q',input.value.trim()):url.searchParams.delete('q');
    url.hash=category==='all'?'':category;
    history[push?'pushState':'replaceState']({guideCategory:category},'',url);
  }
  function render(){
    const terms=input.value.trim().split(/\s+/).map(norm).filter(Boolean),searching=terms.length>0;
    const effective=searching?'all':category,info=data[effective]||data.all;
    const categoryItems=items.filter(li=>effective==='all'||li.dataset.cat===effective);
    if(searching)tag='';filters.replaceChildren();
    if(!searching&&effective!=='all'){
      const options=[['전체','',categoryItems.length],...(info.filters||[]).map(([label,value])=>[label,value,categoryItems.filter(li=>index[items.indexOf(li)].includes(norm(value))).length])];
      options.forEach(([label,value,count])=>{
        const b=document.createElement('button');b.type='button';b.dataset.tag=value;b.textContent=label+' '+count;
        b.classList.toggle('is-active',tag===value);b.setAttribute('aria-pressed',String(tag===value));
        b.addEventListener('click',()=>{tag=value;render();});filters.append(b);
      });
    }
    let shown=0;
    items.forEach((li,i)=>{
      const matched=(effective==='all'||li.dataset.cat===effective)&&terms.every(t=>index[i].includes(t))&&(!tag||index[i].includes(norm(tag)));
      li.hidden=!matched;if(matched)li.querySelector('.gc-num').textContent=String(++shown).padStart(2,'0');
    });
    tiles.forEach(t=>{const on=!searching&&t.dataset.cat===category;t.classList.toggle('is-active',on);t.setAttribute('aria-pressed',String(on));t.draggable=category==='all'&&!searching;});
    document.getElementById('gc-title').textContent=searching?'“'+input.value.trim()+'” 검색 결과':info.label;
    document.getElementById('gc-desc').textContent=searching?'모든 가이드에서 제목·설명·키워드로 찾았어요.':info.desc;
    document.getElementById('gh-current').textContent=searching?'검색 결과':info.label;
    document.getElementById('gh-selected').textContent=searching?'검색 결과':'선택한 카테고리: '+info.label;
    root.querySelectorAll('.gh-category-hero img').forEach(img=>img.src=info.art);
    document.getElementById('gc-total').textContent=shown+'개';
    document.getElementById('gh-status').textContent=shown+'개의 가이드를 확인할 수 있어요.';
    document.getElementById('gc-empty').hidden=shown>0;list.hidden=shown===0;
    document.getElementById('gh-esim-note').hidden=effective!=='esim'||searching;
    root.classList.toggle('is-category-all',effective==='all');root.classList.toggle('is-searching',searching);clear.hidden=!input.value;
  }
  function readLocation(){
    const params=new URLSearchParams(location.search);let key='';try{key=decodeURIComponent(location.hash.slice(1));}catch(_e){}
    const query=params.get('guide_category')||'';key=key||aliases[query]||query;
    category=data[key]?key:(mobile.matches?'check':'all');tag='';input.value=(params.get('q')||'').slice(0,100);render();
  }
  function select(key){category=key;tag='';input.value='';updateUrl(true);render();scrollTo(section);}
  tiles.forEach(button=>{
    button.addEventListener('click',()=>{if(!justDragged)select(button.dataset.cat);});
    button.addEventListener('dragstart',e=>{dragged=button;e.dataTransfer?.setData('text/plain',button.dataset.cat);});
    button.addEventListener('dragover',e=>{if(!dragged||dragged===button)return;e.preventDefault();const r=button.getBoundingClientRect();bar.insertBefore(dragged,e.clientX<r.left+r.width/2?button:button.nextSibling);});
    button.addEventListener('drop',e=>e.preventDefault());
    button.addEventListener('dragend',()=>{dragged=null;justDragged=true;try{localStorage.setItem('59manCategoryOrderV2',JSON.stringify([...bar.children].map(b=>b.dataset.cat)));}catch(_e){}setTimeout(()=>justDragged=false,0);});
    button.addEventListener('keydown',e=>{
      if(!e.altKey||category!=='all')return;const steps={ArrowLeft:-1,ArrowRight:1,ArrowUp:mobile.matches?-3:-8,ArrowDown:mobile.matches?3:8};
      if(!(e.key in steps))return;const order=[...bar.children],i=order.indexOf(button),next=Math.max(0,Math.min(order.length-1,i+steps[e.key]));if(i===next)return;
      e.preventDefault();bar.insertBefore(button,next>i?order[next].nextSibling:order[next]);button.focus();
      try{localStorage.setItem('59manCategoryOrderV2',JSON.stringify([...bar.children].map(b=>b.dataset.cat)));}catch(_e){}
    });
  });
  try{const saved=JSON.parse(localStorage.getItem('59manCategoryOrderV2')||'[]');if(Array.isArray(saved))saved.forEach(k=>{const b=tiles.find(t=>t.dataset.cat===k);if(b)bar.append(b);});}catch(_e){}
  input.addEventListener('input',()=>{tag='';render();});
  input.addEventListener('keydown',e=>{if(e.key==='Escape'&&input.value){input.value='';tag='';updateUrl(false);render();}});
  document.getElementById('gc-form').addEventListener('submit',e=>{e.preventDefault();updateUrl(false);render();scrollTo(section);});
  clear.addEventListener('click',()=>{input.value='';tag='';updateUrl(false);render();input.focus();});
  document.getElementById('gh-back').addEventListener('click',()=>{scrollTo(document.getElementById('gh-directory'));tiles.find(t=>t.dataset.cat===category)?.focus({preventScroll:true});});
  addEventListener('popstate',readLocation);addEventListener('hashchange',readLocation);mobile.addEventListener('change',()=>render());readLocation();
})();
