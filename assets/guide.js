/* 59만모바일 가이드 허브
 * - 카테고리 필터 + 한국어 검색 + 해시 라우팅(#esim, #sim/kt-바로유심 …: 뒤로가기/새로고침 지원)
 * - PC(1024px 이상): 왼쪽 목록 + 오른쪽 상세 미리보기 2열. 상세 내용은 각 가이드의 독립 URL에서 가져와 보여 주며,
 *   모든 가이드는 계속 자기 URL(예: /kt-바로유심/)로 직접 열 수 있다.
 */
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
  var split = document.getElementById('gc-split');
  var pane = document.getElementById('gc-pane');
  if (total) total.setAttribute('aria-live', 'polite');

  function norm(s) { return (s || '').toLowerCase().replace(/\s+/g, ''); }
  function linkOf(li) { return li.firstElementChild; }
  function pathOf(li) { return decodeURIComponent(linkOf(li).getAttribute('href')); }
  var index = items.map(function (li) { return norm(li.textContent + ' ' + (linkOf(li).getAttribute('data-kw') || '')); });
  var state = { cat: 'all', q: '', sel: null };
  var mq = window.matchMedia ? window.matchMedia('(min-width: 1024px)') : null;
  function paneOn() { return !!(mq && mq.matches && split && pane); }

  /* ---------- 목록 ---------- */
  function visibleItems() { return items.filter(function (li) { return !li.hidden; }); }

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
    syncSelection();
  }

  /* ---------- 상세 미리보기(PC) ---------- */
  var cache = {};
  function hashFor(li) {
    return '#' + state.cat + '/' + pathOf(li).replace(/^\/|\/$/g, '');
  }

  function syncSelection() {
    if (!paneOn()) { split && split.classList.remove('has-pane'); if (pane) pane.hidden = true; return; }
    split.classList.add('has-pane');
    pane.hidden = false;
    var vis = visibleItems();
    var cur = vis.filter(function (li) { return pathOf(li) === state.sel; })[0];
    if (!cur) cur = vis[0];
    items.forEach(function (li) { li.classList.toggle('is-selected', li === cur); linkOf(li).removeAttribute('aria-current'); });
    if (!cur) { pane.innerHTML = ''; return; }
    linkOf(cur).setAttribute('aria-current', 'true');
    state.sel = pathOf(cur);
    showPane(cur);
  }

  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function extract(htmlText) {
    var doc = new DOMParser().parseFromString(htmlText, 'text/html');
    var art = doc.querySelector('.article');
    var wrap = document.createElement('div');
    wrap.className = 'gc-pane-body article';
    if (!art) return wrap;
    var kept = 0;
    [].slice.call(art.children).forEach(function (el) {
      if (el.tagName !== 'SECTION') return;
      if (el.classList.contains('faq') || el.classList.contains('activation-flow') || el.classList.contains('shot-guide')) return;
      if (!el.classList.contains('answer-card') && kept >= 4) return;
      if (!el.classList.contains('answer-card')) kept++;
      var node = document.importNode(el, true);
      [].slice.call(node.querySelectorAll('script')).forEach(function (s) { s.remove(); });
      wrap.appendChild(node);
    });
    return wrap;
  }

  var token = 0;
  function showPane(li) {
    var my = ++token;
    var a = linkOf(li);
    var href = a.getAttribute('href');
    var cat = li.getAttribute('data-cat');
    var thumb = li.querySelector('.gc-thumb');
    var t = a.querySelector('.gc-body b').textContent;
    var d = a.querySelector('.gc-desc').textContent;
    var head =
      '<div class="gc-pane-top"><nav class="gc-pane-crumb" aria-label="경로"><a href="/">홈</a><span>›</span><a href="/guide/">가이드</a><span>›</span><span>' + esc(data[cat].label) + '</span></nav>' +
      '<a class="gc-open" href="' + esc(href) + '">전체 페이지 열기<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8"/></svg></a></div>' +
      '<div class="gc-pane-hero"><div><h2 class="gc-pane-title">' + esc(t) + '</h2><p class="gc-pane-desc">' + esc(d) + '</p></div>' +
      '<span class="gc-pane-art">' + (thumb ? thumb.innerHTML : '') + '</span></div>';
    var foot =
      '<div class="gc-pane-cta"><a class="button" href="' + esc(href) + '">이 가이드 전체 보기 →</a>' +
      '<a class="button alt" href="https://preplan.site/?from=59man_guide_pane">개통 시작하기</a>' +
      '<a class="button alt" href="https://pf.kakao.com/_akxmKn/chat" rel="noopener">카톡 상담</a></div>';
    pane.scrollTop = 0;
    function paint(body) {
      if (my !== token) return;
      pane.innerHTML = head;
      pane.appendChild(body);
      pane.insertAdjacentHTML('beforeend', foot);
      pane.scrollTop = 0;
    }
    if (cache[href]) { paint(cache[href].cloneNode(true)); return; }
    pane.innerHTML = head + '<p class="gc-pane-loading">내용을 불러오는 중이에요…</p>';
    fetch(href, { credentials: 'same-origin' }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.text();
    }).then(function (txt) {
      var body = extract(txt);
      cache[href] = body;
      paint(body.cloneNode(true));
    }).catch(function () {
      if (my !== token) return;
      pane.innerHTML = head + '<p class="gc-pane-loading">미리보기를 불러오지 못했어요. <a href="' + esc(href) + '">전체 페이지에서 확인하기</a></p>' + foot;
    });
  }

  list.addEventListener('click', function (e) {
    if (!paneOn()) return;
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
    var a = e.target.closest && e.target.closest('a.gc-card');
    if (!a) return;
    e.preventDefault();
    var li = a.parentNode;
    state.sel = pathOf(li);
    syncSelection();
    if (history.replaceState) history.replaceState(null, '', hashFor(li));
  });

  /* ---------- 해시 라우팅 ---------- */
  function fromHash() {
    var h = '';
    try { h = decodeURIComponent(location.hash.slice(1)); } catch (e) { h = ''; }
    var i = h.indexOf('/');
    var cat = i < 0 ? h : h.slice(0, i);
    state.cat = data[cat] ? cat : 'all';
    state.sel = i < 0 ? null : '/' + h.slice(i + 1).replace(/\/$/, '') + '/';
    render();
  }

  tiles.forEach(function (t) {
    t.addEventListener('click', function () {
      var key = t.getAttribute('data-cat');
      if (state.q) { state.q = ''; input.value = ''; }
      state.sel = null;
      if (key === 'all') {
        if (location.hash) history.pushState(null, '', location.pathname + location.search);
        fromHash();
      } else if (location.hash.split('/')[0] !== '#' + key || location.hash.indexOf('/') > -1) {
        location.hash = key;
      } else {
        fromHash();
      }
      if (!paneOn() && section && section.getBoundingClientRect().top > window.innerHeight * 0.75) {
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
  if (mq && mq.addEventListener) mq.addEventListener('change', render);
  fromHash();
})();
