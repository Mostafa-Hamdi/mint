// Shared finishing touches: floating sticky header + back-to-top button.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var here = location.pathname.split('/').pop() || 'index.html';

  /* ---------- floating header (built from #sticky-cfg) ---------- */
  var cfgEl = document.getElementById('sticky-cfg');
  var bar = null, panel = null, progress = null, menuBtn = null;
  if (cfgEl) {
    var cfg = JSON.parse(cfgEl.textContent);
    bar = document.createElement('header');
    bar.className = 'fh';
    bar.setAttribute('aria-label', 'Quick navigation');
    var links = cfg.links.map(function (l) {
      var cur = l.href.split('#')[0] === here && !l.href.includes('#') ? ' aria-current="page"' : '';
      return '<a href="' + l.href + '"' + cur + '>' + l.label + '</a>';
    }).join('');
    bar.innerHTML =
      '<div class="fh-pill">' +
        '<a class="fh-logo" href="' + cfg.home + '" aria-label="' + cfg.name + ' home"><img src="' + cfg.logo + '" alt=""></a>' +
        '<nav class="fh-nav" aria-label="Quick">' + links + '</nav>' +
        '<a class="fh-login" href="#"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/></svg><span>Log in</span></a>' +
        '<button class="fh-menu" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="fh-panel"><i></i><i></i><i></i></button>' +
        '<span class="fh-progress" aria-hidden="true"></span>' +
      '</div>' +
      '<nav class="fh-panel" id="fh-panel" aria-label="Menu">' + links + '</nav>';
    document.body.appendChild(bar);
    panel = bar.querySelector('.fh-panel');
    progress = bar.querySelector('.fh-progress');
    menuBtn = bar.querySelector('.fh-menu');
    function setMenu(open) {
      bar.classList.toggle('menu-open', open);
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    }
    menuBtn.addEventListener('click', function () { setMenu(!bar.classList.contains('menu-open')); });
    panel.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
    document.addEventListener('click', function (e) { if (bar.classList.contains('menu-open') && !bar.contains(e.target)) setMenu(false); });
    bar._setMenu = setMenu;
  }

  /* ---------- phone tab bar (sticky, bottom) ---------- */
  var ICONS = {
    home: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    grid: '<rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2"/>',
    book: '<path d="M4 4.5A1.5 1.5 0 0 1 5.5 3H20v15H5.5A1.5 1.5 0 0 0 4 19.5z"/><path d="M4 19.5A1.5 1.5 0 0 0 5.5 21H20v-3"/>',
    tag: '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/>'
  };
  function svg(name) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONS[name] + '</svg>';
  }
  var tabbar = null;
  if (cfgEl && cfg.tabs) {
    tabbar = document.createElement('nav');
    tabbar.className = 'tb';
    tabbar.setAttribute('aria-label', 'Mobile navigation');
    var sheetHtml = '';
    var items = cfg.tabs.map(function (t, i) {
      if (t.sheet) {
        sheetHtml = '<div class="tb-sheet" id="tb-sheet" role="menu">' + t.sheet.map(function (s) {
          return '<a role="menuitem" href="' + s.href + '"><span class="tb-sl"><img src="' + s.logo + '" alt=""></span><span class="tb-st"><b>' + s.label + '</b><small>' + s.note + '</small></span>' +
            '<svg class="tb-go" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>';
        }).join('') + '</div>';
        return '<button type="button" class="tb-i" data-i="' + i + '" aria-expanded="false" aria-controls="tb-sheet">' + svg(t.icon) + '<span>' + t.label + '</span></button>';
      }
      var cur = t.href === here ? ' aria-current="page"' : '';
      return '<a class="tb-i" data-i="' + i + '" href="' + t.href + '"' + cur + '>' + svg(t.icon) + '<span>' + t.label + '</span></a>';
    }).join('');
    tabbar.innerHTML = sheetHtml + '<div class="tb-bar" style="--n:' + cfg.tabs.length + '"><span class="tb-ind" aria-hidden="true"></span>' + items + '</div>';
    document.body.appendChild(tabbar);
    document.body.classList.add('has-tb');
    var ind = tabbar.querySelector('.tb-ind');
    function moveInd(el) {
      if (!el) { ind.style.opacity = 0; return; }
      ind.style.opacity = 1;
      ind.style.transform = 'translateX(' + (+el.getAttribute('data-i') * 100) + '%)';
    }
    var active = tabbar.querySelector('.tb-i[aria-current="page"]');
    moveInd(active);
    var sheetBtn = tabbar.querySelector('button.tb-i');
    function setSheet(open) {
      if (!sheetBtn) return;
      tabbar.classList.toggle('sheet-open', open);
      sheetBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      moveInd(open ? sheetBtn : active);
    }
    if (sheetBtn) sheetBtn.addEventListener('click', function () { setSheet(!tabbar.classList.contains('sheet-open')); });
    tabbar.querySelectorAll('a.tb-i').forEach(function (a) { a.addEventListener('click', function () { setSheet(false); moveInd(a); }); });
    document.addEventListener('click', function (e) { if (tabbar.classList.contains('sheet-open') && !tabbar.contains(e.target)) setSheet(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setSheet(false); });
    window.addEventListener('pageshow', function () { setSheet(false); moveInd(active); });
  }

  /* ---------- back to top ---------- */
  var top = document.createElement('button');
  top.type = 'button'; top.className = 'to-top'; top.setAttribute('aria-label', 'Back to top');
  top.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>';
  top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });
  document.body.appendChild(top);

  /* ---------- scroll logic ---------- */
  var lastY = window.scrollY, ticking = false;
  function update() {
    ticking = false;
    var y = window.scrollY, dy = y - lastY;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    top.classList.toggle('show', y > Math.max(700, window.innerHeight * 1.2));
    if (bar) {
      if (progress) progress.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0) + ')';
      var past = y > 160;
      // stays visible the whole time the original header is out of view
      if (!past) { bar.classList.remove('show'); bar._setMenu(false); }
      else bar.classList.add('show');
    }
    lastY = y;
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  update();
})();
