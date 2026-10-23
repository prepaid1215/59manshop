/* 59만모바일 가이드 허브(모바일 UI): 카테고리 필터 + 한국어 검색 + 해시 라우팅(#esim 등, 뒤로가기/새로고침 지원) */
(function () {
  var list = document.getElementById('gc-list');
  var dataEl = document.getElementById('gc-data');
  if (!list || !dataEl) return;
  var data = JSON.parse(dataEl.textContent);
  var items = [].slice.call(list.children);
  var tiles = [].slice.call(document.querySelectorAll('.gc-tile'));
  var input = document.getElementById('gc-q');
  var clear = document.getElementById('gc-clear');
  var form = document.getElementById('gc-form');
  var empty = document.getElementById('gc-empty');
  var title = document.getElementById('gc-title');
  var desc = document.getElementById('gc-desc');
  var total = document.getElementById('gc-total');
  var headIc = document.getElementById('gc-head-ic');
  var section = document.getElementById('gc-section');
  if (total) total.setAttribute('aria-live', 'polite');

  function norm(s) { return (s || '').toLowerCase().replace(/\s+/g, ''); }
  var index = items.map(function (li) {
    var a = li.firstElementChild;
    return norm(li.textContent + ' ' + ((a && a.getAttribute('data-kw')) || ''));
  });
  var state = { cat: 'all', q: '' };

  function render() {
    var term = norm(state.q);
    var shown = 0;
    items.forEach(function (li, i) {
      var ok = term ? index[i].indexOf(term) > -1 : (state.cat === 'all' || li.getAttribute('data-cat') === state.cat);
      li.hidden = !ok;
      if (ok) shown++;
    });
    var c = data[state.cat] || data.all;
    tiles.forEach(function (t) {
      var on = !term && t.getAttribute('data-cat') === state.cat;
      t.classList.toggle('is-active', on);
      t.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    list.classList.toggle('is-mixed', !!term || state.cat === 'all');
    if (term) {
      title.textContent = '“' + state.q.trim() + '” 검색 결과';
      desc.textContent = '모든 가이드에서 제목·설명·키워드로 찾았어요.';
      headIc.innerHTML = data.all.icon;
    } else {
      title.textContent = c.label;
      desc.textContent = c.desc;
      headIc.innerHTML = c.icon;
    }
    total.innerHTML = '<b>' + shown + '</b>개';
    empty.hidden = shown > 0;
    list.hidden = shown === 0;
    clear.hidden = !state.q;
  }

  function fromHash() {
    var h = '';
    try { h = decodeURIComponent(location.hash.slice(1)); } catch (e) { h = ''; }
    state.cat = data[h] ? h : 'all';
    render();
  }

  tiles.forEach(function (t) {
    t.addEventListener('click', function () {
      var key = t.getAttribute('data-cat');
      if (state.q) { state.q = ''; input.value = ''; }
      if (key === 'all') {
        if (location.hash) history.pushState(null, '', location.pathname + location.search);
        fromHash();
      } else if (location.hash !== '#' + key) {
        location.hash = key;
      } else {
        fromHash();
      }
      if (section && section.getBoundingClientRect().top > window.innerHeight * 0.75) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  input.addEventListener('input', function () { state.q = input.value; render(); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && input.value) { input.value = ''; state.q = ''; render(); }
  });
  clear.addEventListener('click', function () { input.value = ''; state.q = ''; render(); input.focus(); });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();
