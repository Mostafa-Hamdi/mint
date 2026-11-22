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
    bar._setMenu = setMenu;
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
      if (!past) { bar.classList.remove('show'); bar._setMenu(false); }
      else if (dy < -4) bar.classList.add('show');
      else if (dy > 6 && !bar.classList.contains('menu-open')) bar.classList.remove('show');
    }
    lastY = y;
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  update();
})();
