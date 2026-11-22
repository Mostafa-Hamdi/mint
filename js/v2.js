// MINT CONSENT / MINT PILs pages.
// Accordions (guide + FAQ): the question row toggles its answer strip.
document.querySelectorAll('.acc-t').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var band = document.getElementById(btn.getAttribute('aria-controls'));
    var open = btn.getAttribute('aria-expanded') !== 'true';
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    band.classList.toggle('closed', !open);
  });
});

// Legal page: sticky section nav + scroll-spy (desktop list, phone chips bar).
(function () {
  var navs = Array.prototype.slice.call(document.querySelectorAll('.lgn'));
  if (!navs.length) return;
  var ORDER = ['terms', 'privacy', 'faq', 'refunds', 'copyright'];
  var LABEL = { terms: 'Terms Of Use', privacy: 'Privacy Policy', faq: 'FAQ', refunds: 'Refunds Policy', copyright: 'Copyrights' };
  var chips = document.createElement('nav');
  chips.className = 'lgc'; chips.setAttribute('aria-label', 'Legal sections');
  chips.innerHTML = ORDER.map(function (k) { return '<a href="pils-legal.html" data-section="' + k + '">' + LABEL[k] + '</a>'; }).join('');
  document.body.appendChild(chips);
  function vis(sel) { return Array.prototype.find.call(document.querySelectorAll(sel), function (el) { return el.offsetParent !== null; }); }
  function docTop(el) { return el.getBoundingClientRect().top + window.scrollY; }
  function size() {   // the desktop list stays pinned until the footer
    var nav = vis('.fv-d .lgn'), end = vis('[data-anchor="legal-end"]');
    if (nav && end) nav.style.height = Math.max(0, docTop(end) - docTop(nav)) + 'px';
  }
  var current = null;
  function spy() {
    var line = (window.innerWidth < 768 ? 80 : 100) + 60;
    var list = ORDER.map(function (k) { var a = vis('[data-anchor="' + k + '"]'); return a ? { k: k, top: a.getBoundingClientRect().top } : null; })
      .filter(Boolean).sort(function (a, b) { return a.top - b.top; });
    var act = list.length ? list[0].k : null;
    list.forEach(function (s) { if (s.top <= line) act = s.k; });
    if (act !== current) {
      current = act;
      document.querySelectorAll('.lgn-a, .lgc a').forEach(function (a) {
        if (a.getAttribute('data-section') === act) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
      });
      var on = chips.querySelector('[aria-current="true"]');
      if (on) chips.scrollTo({ left: on.offsetLeft - (chips.clientWidth - on.offsetWidth) / 2, behavior: 'smooth' });
    }
    // chips appear once the phone list has scrolled under the header, and leave at the footer
    var mnav = vis('.fv-m .lgn'), end = vis('[data-anchor="legal-end"]');
    var show = !!(mnav && mnav.getBoundingClientRect().bottom < 70 && (!end || end.getBoundingClientRect().top > 160));
    chips.classList.toggle('show', show);
  }
  var tick = false;
  window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(function () { tick = false; spy(); }); } }, { passive: true });
  window.addEventListener('resize', function () { size(); spy(); });
  window.addEventListener('load', function () { size(); spy(); });
  document.addEventListener('transitionend', function (e) { if (e.target.classList && e.target.classList.contains('bd')) { size(); spy(); } });
  size(); spy();
})();
