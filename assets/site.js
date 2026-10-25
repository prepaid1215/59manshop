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
