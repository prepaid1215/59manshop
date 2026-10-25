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
  var params = new URLSearchParams(window.location.search);
  var initialQuery = (params.get('q') || '').slice(0, 100);
  if (input) input.value = initialQuery;
  var state = { cat: 'all', q: initialQuery };

  function render() {
    var terms = (state.q || '').trim().split(/\s+/).map(norm).filter(Boolean);
    var term = terms.join('');
    var shown = 0;
    items.forEach(function (li, i) {
      var ok = terms.length ? terms.every(function (word) { return index[i].indexOf(word) > -1; }) : (state.cat === 'all' || li.getAttribute('data-cat') === state.cat);
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
      if (headIc) headIc.innerHTML = data.all.icon || '';
    } else {
      title.textContent = c.label;
      desc.textContent = c.desc;
      if (headIc) headIc.innerHTML = c.icon || '';
    }
    total.innerHTML = '<b>' + shown + '</b>개';
    empty.hidden = shown > 0;
    list.hidden = shown === 0;
    clear.hidden = !state.q;
    list.dispatchEvent(new CustomEvent('guides:filtered'));
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
      if (state.q) { state.q = ''; input.value = ''; history.replaceState(null, '', location.pathname + location.hash); }
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
  clear.addEventListener('click', function () { input.value = ''; state.q = ''; history.replaceState(null, '', location.pathname + location.hash); render(); input.focus(); });
  form.addEventListener('submit', function (e) { e.preventDefault(); state.q = input.value.slice(0, 100).trim(); history.replaceState(null, '', location.pathname + (state.q ? '?q=' + encodeURIComponent(state.q) : '') + location.hash); render(); });
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();

/* On wide screens the real, existing detail route can also be read beside the
 * list. Links remain ordinary navigable anchors on mobile and without JS. */
(function () {
  var list = document.getElementById('gc-list');
  var panel = document.getElementById('preview-content');
  var open = document.getElementById('preview-open');
  var status = document.getElementById('preview-status');
  if (!list || !panel || !open) return;
  var wide = window.matchMedia('(min-width: 1024px)');
  var current = '';
  var generation = 0;
  var cache = new Map();

  async function select(link) {
    if (!wide.matches || !link) return;
    var href = link.getAttribute('href');
    if (href === current && panel.querySelector('.detail-article')) return;
    current = href;
    var request = ++generation;
    open.href = href;
    panel.setAttribute('aria-busy', 'true');
    list.querySelectorAll('.gc-card').forEach(function (a) {
      a.classList.toggle('is-selected', a === link);
      if (a === link) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
    try {
      var source = cache.get(href);
      if (!source) {
        var response = await fetch(href, {credentials: 'same-origin'});
        if (!response.ok) throw new Error('HTTP ' + response.status);
        source = await response.text();
        cache.set(href, source);
      }
      if (request !== generation) return;
      var doc = new DOMParser().parseFromString(source, 'text/html');
      var article = doc.querySelector('.detail-article');
      if (!article) throw new Error('Missing article');
      var heading = article.querySelector('h1');
      var pageTitle = heading ? heading.textContent : link.textContent;
      article.querySelectorAll('script').forEach(function (s) { s.remove(); });
      // Imported headings/figures may share IDs with the guide hub itself.
      article.querySelectorAll('[id]').forEach(function (el) { el.id = 'preview-' + el.id; });
      article.querySelectorAll('[aria-labelledby]').forEach(function (el) {
        el.setAttribute('aria-labelledby', el.getAttribute('aria-labelledby').split(/\s+/).map(function (id) { return 'preview-' + id; }).join(' '));
      });
      article.querySelectorAll('a[href^="#"]').forEach(function (a) { a.setAttribute('href', '#preview-' + a.getAttribute('href').slice(1)); });
      // The hub already owns its h1; the embedded guide is a nested section.
      if (heading) {
        var nestedTitle = document.createElement('h2');
        nestedTitle.className = 'preview-title';
        nestedTitle.textContent = heading.textContent;
        if (heading.id) nestedTitle.id = heading.id;
        heading.replaceWith(nestedTitle);
      }
      panel.replaceChildren(document.importNode(article, true));
      if (window.enhanceHubContent) window.enhanceHubContent(panel);
      panel.scrollTop = 0;
      var anchor = href.split('#')[1];
      if (anchor) {
        var target = panel.querySelector('[id="preview-' + anchor + '"]');
        if (target) panel.scrollTop = target.offsetTop - panel.offsetTop;
      }
      if (status) status.textContent = pageTitle + ' 안내를 불러왔습니다.';
    } catch (e) {
      if (request !== generation) return;
      var p = document.createElement('p');
      p.textContent = '안내를 불러오지 못했습니다. 상세페이지에서 확인해 주세요.';
      var a = document.createElement('a');
      a.href = href;
      a.textContent = '상세페이지에서 보기 →';
      panel.replaceChildren(p, a);
      if (status) status.textContent = p.textContent;
      current = '';
    } finally {
      if (request === generation) panel.setAttribute('aria-busy', 'false');
    }
  }

  function sync() {
    if (!wide.matches) return;
    var visible = [].slice.call(list.querySelectorAll('li:not([hidden]) > .gc-card'));
    var retained = visible.find(function (a) { return a.getAttribute('href') === current; });
    if (visible.length) select(retained || visible[0]);
    else {
      generation++;
      current = '';
      panel.setAttribute('aria-busy', 'false');
      panel.textContent = '검색 결과가 없습니다. 다른 검색어를 입력해 주세요.';
      open.href = '/guide/';
    }
  }
  list.addEventListener('click', function (event) {
    var a = event.target.closest('.gc-card');
    if (!a || !wide.matches || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    select(a);
  });
  list.addEventListener('guides:filtered', sync);
  wide.addEventListener('change', sync);
  sync();
})();
