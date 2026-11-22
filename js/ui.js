// Shared finishing touches: site header, phone tab bar, back-to-top button.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var here = location.pathname.split('/').pop() || 'index.html';

  /* ---------- site header (built from #sticky-cfg) ----------
     One header for every page: full width at the top of the page,
     it glides into a floating glass capsule once the page scrolls. */
  var cfgEl = document.getElementById('sticky-cfg');
  var bar = null, progress = null;
  if (cfgEl) {
    var cfg = JSON.parse(cfgEl.textContent);
    bar = document.createElement('header');
    bar.className = 'fh';
    var chev = '<svg class="fh-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
    var arrow = '<svg class="fh-go" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
    var links = cfg.links.map(function (l, i) {
      if (l.menu) {
        var onMenu = l.menu.some(function (m) { return m.href === here; });
        return '<div class="fh-dd"><button type="button" class="fh-ddt' + (onMenu ? ' is-cur' : '') + '" aria-expanded="false" aria-controls="fh-dd' + i + '">' + l.label + chev + '</button>' +
          '<div class="fh-ddp" id="fh-dd' + i + '">' + l.menu.map(function (m) {
            return '<a href="' + m.href + '"' + (m.href === here ? ' aria-current="page"' : '') + '><span class="fh-ml"><img src="' + m.logo + '" alt=""></span><span class="fh-mt"><b>' + m.label + '</b><small>' + m.note + '</small></span>' + arrow + '</a>';
          }).join('') + '</div></div>';
      }
      var cur = l.href === here && !l.section ? ' aria-current="page"' : '';
      var sec = l.section ? ' data-section="' + l.section + '"' : '';
      return '<a href="' + l.href + '"' + sec + cur + '>' + l.label + '</a>';
    }).join('');
    bar.innerHTML =
      '<div class="fh-pill">' +
        '<span class="fh-bg" aria-hidden="true"></span>' +
        '<a class="fh-logo" href="' + cfg.home + '" aria-label="' + cfg.name + ' home"><img src="' + cfg.logo + '" alt="' + cfg.name + '"></a>' +
        '<nav class="fh-nav" aria-label="Main">' + links + '</nav>' +
        '<a class="fh-login" href="#"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/></svg><span>Log in</span></a>' +
        '<span class="fh-progress" aria-hidden="true"></span>' +
      '</div>';
    document.body.insertBefore(bar, document.body.firstChild);
    document.body.classList.add('has-fh');
    progress = bar.querySelector('.fh-progress');
    // Products dropdown: hover on pointer devices, click/keyboard everywhere, closes on an outside click
    bar.querySelectorAll('.fh-dd').forEach(function (dd) {
      var t = dd.querySelector('.fh-ddt'), timer;
      var hoverable = window.matchMedia('(hover: hover)');
      function set(open) { dd.classList.toggle('open', open); t.setAttribute('aria-expanded', open ? 'true' : 'false'); }
      t.addEventListener('click', function () { set(!dd.classList.contains('open')); });
      dd.addEventListener('mouseenter', function () { if (hoverable.matches) { clearTimeout(timer); set(true); } });
      dd.addEventListener('mouseleave', function () { if (hoverable.matches) timer = setTimeout(function () { set(false); }, 180); });
      dd.addEventListener('keydown', function (e) { if (e.key === 'Escape') { set(false); t.focus(); } });
      document.addEventListener('click', function (e) { if (!dd.contains(e.target)) set(false); });
    });
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
      var cur = t.href === here && !t.section ? ' aria-current="page"' : '';
      var sec = t.section ? ' data-section="' + t.section + '"' : '';
      return '<a class="tb-i" data-i="' + i + '" href="' + t.href + '"' + sec + cur + '>' + svg(t.icon) + '<span>' + t.label + '</span></a>';
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

  /* ---------- section scrolling (JS only, no #ids in links or the URL) ----------
     <a data-section="x"> scrolls to the visible [data-anchor="x"]. On another page the
     section name is handed over in sessionStorage and the scroll happens after load. */
  var KEY = 'mint-section';
  function anchorFor(name) {
    return Array.prototype.find.call(document.querySelectorAll('[data-anchor="' + name + '"]'), function (el) { return el.offsetParent !== null; });
  }
  function headerSpace() { return window.innerWidth < 768 ? 80 : 100; }
  function goTo(name, smooth) {
    var el = anchorFor(name);
    if (!el) return false;
    var y = el.getBoundingClientRect().top + window.scrollY - headerSpace();
    window.scrollTo({ top: Math.max(0, y), behavior: smooth && !reduce ? 'smooth' : 'auto' });
    return true;
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[data-section]');
    if (a) {
      e.preventDefault();
      var name = a.getAttribute('data-section');
      var page = (a.getAttribute('href') || '').split('?')[0];
      if (!page || page === here) {
        if (!goTo(name, true) && name === 'contact') location.href = 'contact.html';
      } else {
        try { sessionStorage.setItem(KEY, name); } catch (err) {}
        location.href = page;
      }
      return;
    }
    var dead = e.target.closest('a[href="#"]');
    if (dead) e.preventDefault();          // placeholder links (Log in) never jump to the top
  });
  var pending = null;
  try { pending = sessionStorage.getItem(KEY); sessionStorage.removeItem(KEY); } catch (err) {}
  if (pending) {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    var run = function () {
      setTimeout(function () {
        if (!goTo(pending, true) && pending === 'contact') location.href = 'contact.html';
      }, 120);
    };
    if (document.readyState === 'complete') run(); else window.addEventListener('load', run);
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
      bar.classList.toggle('scrolled', y > 24);
    }
    lastY = y;
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  update();
})();
