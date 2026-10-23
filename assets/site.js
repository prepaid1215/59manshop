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
