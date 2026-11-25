// Shared finishing touches: site header, phone tab bar, back-to-top button.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var here = location.pathname.split('/').pop() || 'index.html';

  /*  site header (built from #sticky-cfg) 
     One header for every page: full width at the top of the page,
     it glides into a floating glass capsule once the page scrolls. */
  // "by MINTFORMED" switcher shown on the product sites: back to the main site, or across to the other product
  function familySwitcher(cfg) {
    var check =
      '<svg class="fh-eco-ok" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>';
    var go =
      '<svg class="fh-eco-go" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
    var items = cfg.family
      .map(function (f) {
        var logo = f.logo
          ? '<img src="' + f.logo + '" alt="">'
          : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="8" r="3.2"/><circle cx="17" cy="9.5" r="2.4"/><path d="M3.5 19c.6-3.2 2.9-5 5.5-5s4.9 1.8 5.5 5M14.8 14.6c.7-.4 1.4-.6 2.2-.6 2 0 3.6 1.4 4 3.6"/></svg>';
        var inner =
          '<span class="fh-eco-l">' +
          logo +
          '</span><span class="fh-eco-t"><b>' +
          f.label +
          '</b><small>' +
          f.note +
          '</small></span>';
        if (f.soon)
          return (
            '<span class="fh-eco-i is-soon" aria-disabled="true">' +
            inner +
            '<em>Coming soon</em></span>'
          );
        if (f.current)
          return (
            '<span class="fh-eco-i is-cur" aria-current="page">' +
            inner +
            check +
            '</span>'
          );
        return (
          '<a class="fh-eco-i' +
          (f.main ? ' is-main' : '') +
          '" href="' +
          f.href +
          '">' +
          inner +
          go +
          '</a>'
        );
      })
      .join('');
    return (
      '<span class="fh-eco-sep" aria-hidden="true"></span>' +
      '<div class="fh-eco"><button class="fh-ecot" type="button" aria-expanded="false" aria-controls="fh-eco-p" aria-label="MINTFORMED family of products">' +
      '<span class="fh-eco-by">by</span><img src="assets/img/logo.svg" alt="MINTFORMED">' +
      '<svg class="fh-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></button>' +
      '<div class="fh-ecop" id="fh-eco-p"><p class="fh-eco-k">The MINTFORMED family</p>' +
      items +
      '</div></div>'
    );
  }
  var cfgEl = document.getElementById('sticky-cfg');
  var bar = null,
    progress = null;
  if (cfgEl) {
    var cfg = JSON.parse(cfgEl.textContent);
    bar = document.createElement('header');
    bar.className = 'fh';
    var chev =
      '<svg class="fh-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
    var arrow =
      '<svg class="fh-go" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
    var links = cfg.links
      .map(function (l, i) {
        if (l.menu) {
          var onMenu = l.menu.some(function (m) {
            return m.href === here;
          });
          return (
            '<div class="fh-dd"><button type="button" class="fh-ddt' +
            (onMenu ? ' is-cur' : '') +
            '" aria-expanded="false" aria-controls="fh-dd' +
            i +
            '">' +
            l.label +
            chev +
            '</button>' +
            '<div class="fh-ddp" id="fh-dd' +
            i +
            '">' +
            l.menu
              .map(function (m) {
                return (
                  '<a href="' +
                  m.href +
                  '"' +
                  (m.href === here ? ' aria-current="page"' : '') +
                  '><span class="fh-ml"><img src="' +
                  m.logo +
                  '" alt=""></span><span class="fh-mt"><b>' +
                  m.label +
                  '</b><small>' +
                  m.note +
                  '</small></span>' +
                  arrow +
                  '</a>'
                );
              })
              .join('') +
            '</div></div>'
          );
        }
        var cur = l.href === here && !l.section ? ' aria-current="page"' : '';
        var sec = l.section ? ' data-section="' + l.section + '"' : '';
        return '<a href="' + l.href + '"' + sec + cur + '>' + l.label + '</a>';
      })
      .join('');
    bar.innerHTML =
      '<div class="fh-pill">' +
      '<span class="fh-bg" aria-hidden="true"></span>' +
      '<a class="fh-logo" href="' +
      cfg.home +
      '" aria-label="' +
      cfg.name +
      ' home"><img src="' +
      cfg.logo +
      '" alt="' +
      cfg.name +
      '"></a>' +
      (cfg.family ? familySwitcher(cfg) : '') +
      '<nav class="fh-nav" aria-label="Main">' +
      links +
      '</nav>' +
      '<a class="fh-login" href="#"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/></svg><span>Log in</span></a>' +
      '<span class="fh-progress" aria-hidden="true"></span>' +
      '</div>';
    var skipEl = document.querySelector(".skip");
    document.body.insertBefore(bar, skipEl ? skipEl.nextSibling : document.body.firstChild);
    document.body.classList.add('has-fh');
    progress = bar.querySelector('.fh-progress');
    // Products dropdown: hover on pointer devices, click/keyboard everywhere, closes on an outside click
    // family switcher: click / keyboard; closes on an outside click or Esc
    var eco = bar.querySelector('.fh-eco');
    if (eco) {
      var et = eco.querySelector('.fh-ecot');
      var setEco = function (open) {
        eco.classList.toggle('open', open);
        et.setAttribute('aria-expanded', open ? 'true' : 'false');
      };
      et.addEventListener('click', function () {
        setEco(!eco.classList.contains('open'));
      });
      document.addEventListener('click', function (e) {
        if (!eco.contains(e.target)) setEco(false);
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && eco.classList.contains('open')) {
          setEco(false);
          et.focus();
        }
      });
    }
    bar.querySelectorAll('.fh-dd').forEach(function (dd) {
      var t = dd.querySelector('.fh-ddt'),
        timer;
      var hoverable = window.matchMedia('(hover: hover)');
      function set(open) {
        dd.classList.toggle('open', open);
        t.setAttribute('aria-expanded', open ? 'true' : 'false');
      }
      t.addEventListener('click', function () {
        set(!dd.classList.contains('open'));
      });
      dd.addEventListener('mouseenter', function () {
        if (hoverable.matches) {
          clearTimeout(timer);
          set(true);
        }
      });
      dd.addEventListener('mouseleave', function () {
        if (hoverable.matches)
          timer = setTimeout(function () {
            set(false);
          }, 180);
      });
      dd.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
          set(false);
          t.focus();
        }
      });
      document.addEventListener('click', function (e) {
        if (!dd.contains(e.target)) set(false);
      });
    });
  }

  /*  phone tab bar (sticky, bottom)  */
  var ICONS = {
    home: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    grid: '<rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2"/>',
    book: '<path d="M4 4.5A1.5 1.5 0 0 1 5.5 3H20v15H5.5A1.5 1.5 0 0 0 4 19.5z"/><path d="M4 19.5A1.5 1.5 0 0 0 5.5 21H20v-3"/>',
    tag: '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/>',
  };
  function svg(name) {
    return (
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      ICONS[name] +
      '</svg>'
    );
  }
  var tabbar = null;
  if (cfgEl && cfg.tabs) {
    tabbar = document.createElement('nav');
    tabbar.className = 'tb';
    tabbar.setAttribute('aria-label', 'Mobile navigation');
    var sheetHtml = '';
    var items = cfg.tabs
      .map(function (t, i) {
        if (t.sheet) {
          sheetHtml =
            '<div class="tb-sheet" id="tb-sheet" role="menu">' +
            t.sheet
              .map(function (s) {
                return (
                  '<a role="menuitem" href="' +
                  s.href +
                  '"><span class="tb-sl"><img src="' +
                  s.logo +
                  '" alt=""></span><span class="tb-st"><b>' +
                  s.label +
                  '</b><small>' +
                  s.note +
                  '</small></span>' +
                  '<svg class="tb-go" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>'
                );
              })
              .join('') +
            '</div>';
          return (
            '<button type="button" class="tb-i" data-i="' +
            i +
            '" aria-expanded="false" aria-controls="tb-sheet">' +
            svg(t.icon) +
            '<span>' +
            t.label +
            '</span></button>'
          );
        }
        var cur = t.href === here && !t.section ? ' aria-current="page"' : '';
        var sec = t.section ? ' data-section="' + t.section + '"' : '';
        return (
          '<a class="tb-i" data-i="' +
          i +
          '" href="' +
          t.href +
          '"' +
          sec +
          cur +
          '>' +
          svg(t.icon) +
          '<span>' +
          t.label +
          '</span></a>'
        );
      })
      .join('');
    tabbar.innerHTML =
      sheetHtml +
      '<div class="tb-bar" style="--n:' +
      cfg.tabs.length +
      '"><span class="tb-ind" aria-hidden="true"></span>' +
      items +
      '</div>';
    document.body.appendChild(tabbar);
    document.body.classList.add('has-tb');
    var ind = tabbar.querySelector('.tb-ind');
    function moveInd(el) {
      if (!el) {
        ind.style.opacity = 0;
        return;
      }
      ind.style.opacity = 1;
      ind.style.transform =
        'translateX(' + +el.getAttribute('data-i') * 100 + '%)';
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
    if (sheetBtn)
      sheetBtn.addEventListener('click', function () {
        setSheet(!tabbar.classList.contains('sheet-open'));
      });
    tabbar.querySelectorAll('a.tb-i').forEach(function (a) {
      a.addEventListener('click', function () {
        setSheet(false);
        moveInd(a);
      });
    });
    document.addEventListener('click', function (e) {
      if (tabbar.classList.contains('sheet-open') && !tabbar.contains(e.target))
        setSheet(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setSheet(false);
    });
    window.addEventListener('pageshow', function () {
      setSheet(false);
      moveInd(active);
    });
  }

  /*  section scrolling (JS only, no #ids in links or the URL) 
     <a data-section="x"> scrolls to the visible [data-anchor="x"]. On another page the
     section name is handed over in sessionStorage and the scroll happens after load. */
  var KEY = 'mint-section';
  function anchorFor(name) {
    return Array.prototype.find.call(
      document.querySelectorAll('[data-anchor="' + name + '"]'),
      function (el) {
        return el.offsetParent !== null;
      },
    );
  }
  function headerSpace() {
    return window.innerWidth < 768 ? 80 : 100;
  }
  function goTo(name, smooth) {
    var el = anchorFor(name);
    if (!el) return false;
    var y = el.getBoundingClientRect().top + window.scrollY - headerSpace();
    window.scrollTo({
      top: Math.max(0, y),
      behavior: smooth && !reduce ? 'smooth' : 'auto',
    });
    return true;
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[data-section]');
    if (a) {
      e.preventDefault();
      var name = a.getAttribute('data-section');
      var page = (a.getAttribute('href') || '').split('?')[0];
      if (!page || page === here) {
        if (!goTo(name, true) && name === 'contact')
          location.href = 'contact.html';
      } else {
        try {
          sessionStorage.setItem(KEY, name);
        } catch (err) {}
        location.href = page;
      }
      return;
    }
    var dead = e.target.closest('a[href="#"]');
    if (dead) e.preventDefault(); // placeholder links (Log in) never jump to the top
  });
  var pending = null;
  try {
    pending = sessionStorage.getItem(KEY);
    sessionStorage.removeItem(KEY);
  } catch (err) {}
  if (pending) {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    var run = function () {
      setTimeout(function () {
        if (!goTo(pending, true) && pending === 'contact')
          location.href = 'contact.html';
      }, 120);
    };
    if (document.readyState === 'complete') run();
    else window.addEventListener('load', run);
  }

  /*  back to top  */
  var top = document.createElement('button');
  top.type = 'button';
  top.className = 'to-top';
  top.setAttribute('aria-label', 'Back to top');
  top.innerHTML =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>';
  top.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
  });
  document.body.appendChild(top);

  /*  scroll logic  */
  var lastY = window.scrollY,
    ticking = false;
  function update() {
    ticking = false;
    var y = window.scrollY,
      dy = y - lastY;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    top.classList.toggle('show', y > Math.max(700, window.innerHeight * 1.2));
    if (bar) {
      if (progress)
        progress.style.transform =
          'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0) + ')';
      bar.classList.toggle('scrolled', y > 24);
    }
    lastY = y;
  }
  window.addEventListener(
    'scroll',
    function () {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(update);
      }
    },
    { passive: true },
  );
  update();
})();

// Cookie consent: a glass card that asks once, remembers the choice, and can be reopened from the cookie button.
(function () {
  var KEY = 'mint-cookie-consent';
  var saved = null;
  try {
    saved = JSON.parse(localStorage.getItem(KEY) || 'null');
  } catch (err) {}
  var cfgEl = document.getElementById('sticky-cfg'),
    home = 'index.html';
  try {
    home = JSON.parse(cfgEl.textContent).home || home;
  } catch (err) {}
  var policy =
    home === 'index.html'
      ? 'cookies.html'
      : home.replace('.html', '-cookies.html');
  var CATS = [
    {
      k: 'essential',
      t: 'Essential',
      d: 'Keep the site secure and working. Always on.',
      fixed: true,
    },
    {
      k: 'functional',
      t: 'Functional',
      d: 'Remember your choices, like recently viewed items.',
    },
    {
      k: 'analytics',
      t: 'Analytics',
      d: 'Help us understand how the site is used.',
    },
    {
      k: 'marketing',
      t: 'Advertising and marketing',
      d: 'Show you relevant messages on other sites.',
    },
  ];
  var icon =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="M12 3a9 9 0 1 0 9 9 3 3 0 0 1-3.6-3.3A3 3 0 0 1 13.6 5 3 3 0 0 1 12 3Z"/><circle cx="8.5" cy="11" r="1"/><circle cx="12" cy="15.5" r="1"/><circle cx="15.5" cy="12.5" r=".6"/><circle cx="9" cy="16" r=".6"/></svg>';
  var box = document.createElement('section');
  box.className = 'ck-pop';
  box.setAttribute('role', 'dialog');
  box.setAttribute('aria-labelledby', 'ck-pop-t');
  box.setAttribute('aria-describedby', 'ck-pop-d');
  box.innerHTML =
    '<div class="ck-head"><span class="ck-ico">' +
    icon +
    '</span><h2 id="ck-pop-t">We value your privacy</h2></div>' +
    '<p id="ck-pop-d">We use cookies to keep the site working, understand how it is used and improve your experience. ' +
    'Read our <a href="' +
    policy +
    '">Cookie Policy</a>.</p>' +
    '<div class="ck-prefs" id="ck-prefs" hidden>' +
    CATS.map(function (c) {
      return (
        '<label class="ck-row"><span><b>' +
        c.t +
        '</b><small>' +
        c.d +
        '</small></span>' +
        '<input type="checkbox" data-k="' +
        c.k +
        '"' +
        (c.fixed ? ' checked disabled' : '') +
        '><i class="ck-sw" aria-hidden="true"></i></label>'
      );
    }).join('') +
    '</div>' +
    '<div class="ck-actions">' +
    '<button type="button" class="ck-btn ck-all">Accept all</button>' +
    '<button type="button" class="ck-btn ck-ghost ck-none">Reject non-essential</button>' +
    '<button type="button" class="ck-link ck-more" aria-expanded="false" aria-controls="ck-prefs">Customize</button>' +
    '</div>';
  var fab = document.createElement('button');
  fab.type = 'button';
  fab.className = 'ck-fab';
  fab.setAttribute('aria-label', 'Cookie settings');
  fab.innerHTML = icon;
  document.body.appendChild(box);
  document.body.appendChild(fab);
  var prefs = box.querySelector('.ck-prefs'),
    more = box.querySelector('.ck-more');
  function fill(choice) {
    box.querySelectorAll('input[data-k]').forEach(function (i) {
      if (!i.disabled) i.checked = !!(choice && choice[i.dataset.k]);
    });
  }
  function show(on) {
    box.classList.toggle('show', on);
    fab.classList.toggle('show', !on && !!saved);
    if (on) fill(saved);
  }
  function save(choice) {
    choice.essential = true;
    choice.date = new Date().toISOString();
    saved = choice;
    try {
      localStorage.setItem(KEY, JSON.stringify(choice));
    } catch (err) {}
    document.dispatchEvent(new CustomEvent('mint:cookies', { detail: choice }));
    show(false);
  }
  function custom(on) {
    prefs.hidden = !on;
    more.setAttribute('aria-expanded', on ? 'true' : 'false');
    more.textContent = on ? 'Save choices' : 'Customize';
    box.classList.toggle('expanded', on);
  }
  box.querySelector('.ck-all').addEventListener('click', function () {
    save({ functional: true, analytics: true, marketing: true });
    custom(false);
  });
  box.querySelector('.ck-none').addEventListener('click', function () {
    save({ functional: false, analytics: false, marketing: false });
    custom(false);
  });
  more.addEventListener('click', function () {
    if (prefs.hidden) {
      custom(true);
      return;
    }
    var c = {};
    box.querySelectorAll('input[data-k]').forEach(function (i) {
      c[i.dataset.k] = i.checked;
    });
    save(c);
    custom(false);
  });
  fab.addEventListener('click', function () {
    show(true);
  });
  if (saved) fab.classList.add('show');
  else
    setTimeout(function () {
      show(true);
    }, 900);
})();

// Forms are demo-only (no backend yet): stop the page reload. Skip link: move focus to the content without a #hash jump.
(function () {
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || f.getAttribute('action') !== '#') return;
    e.preventDefault();
    var ok = f.querySelector('.cf-ok');
    if (ok) {
      f.reset();
      ok.hidden = false;
    }
  });
  var skip = document.querySelector('.skip');
  var main = document.getElementById('main');
  if (skip && main) {
    skip.addEventListener('click', function (e) {
      e.preventDefault();
      main.focus({ preventScroll: true });
      window.scrollTo({ top: 0 });
    });
  }
})();
