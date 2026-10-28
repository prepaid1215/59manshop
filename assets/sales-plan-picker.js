(function(){'use strict';var root=document.querySelector('.sales-pilot');if(!root)return;
var plans={basic1:{network:'L',name:'L망 기본1',prepare:'L망 호환 유심과 안면인증·간편인증 수단을 준비하세요. 데이터 300MB, 통화 50분, 문자 30건을 확인하세요.'},l25:{network:'L',name:'L망 2.5GB',prepare:'L망 호환 유심을 준비하세요. 월 17,000원, 데이터 2.5GB, 통화 100분, 문자 50건이며 유심 구입비는 별도입니다.'},k396:{network:'K',name:'K망 396',prepare:'KT 바로유심 등 K망 호환 유심을 준비하세요. 월 39,600원, 10.3GB 이후 최대 3Mbps입니다. 최초 충전은 충전 화면에서 가능한 단위로 진행합니다.'},k459:{network:'K',name:'K망 459',prepare:'K망 호환 유심을 준비하세요. 월 45,900원, 20.3GB 이후 최대 3Mbps입니다.'},l464:{network:'L',name:'L망 5G 464',prepare:'L망 호환 유심 또는 지원 단말 eSIM을 확인하세요. 월 46,400원, 20GB 이후 최대 3Mbps입니다.'}};
var current='basic1';var opts=[].slice.call(root.querySelectorAll('[data-sales-plan]'));var chosen=root.querySelector('#sales-chosen'),prep=root.querySelector('#sales-preparation'),link=root.querySelector('#sales-purchase-link'),disclosure=root.querySelector('.sales-disclosure');
function update(){var p=plans[current],join=root.querySelector('input[name="sales-join-type"]:checked').value,label=join==='port'?'번호이동':'신규가입';chosen.textContent=p.name+' · '+label;prep.textContent=p.prepare+(join==='port'?' 기존 번호를 유지하는 번호이동은 미납요금을 정산해야 하며, 접수 가능 시간을 먼저 확인하세요.':'');
link.href='https://preplan.site/?from=59man_plancompare_'+current+'_'+join;
link.dataset.salesPlan=current;link.dataset.salesNetwork=p.network;link.dataset.salesJoin=join;
disclosure.textContent='이 버튼은 59만모바일 개통 홈으로 이동합니다. 플랫폼에서 '+p.network+'망·'+label+'·'+p.name.replace(/^.+?망 /,'')+'을 직접 선택해야 하며 상품이 자동 적용되지는 않습니다.';
opts.forEach(function(b){var selected=b.dataset.salesPlan===current;b.classList.toggle('is-selected',selected);b.setAttribute('aria-pressed',String(selected));});
}
opts.forEach(function(b){b.addEventListener('click',function(){current=b.dataset.salesPlan;update()})});
[].slice.call(root.querySelectorAll('input[name="sales-join-type"]')).forEach(function(b){b.addEventListener('change',update)});
update();
})();