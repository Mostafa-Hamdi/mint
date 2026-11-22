// Phone menu: burger toggles it; a tap outside, a link tap or Esc closes it.
document.querySelectorAll('.hdr-burger').forEach(function (btn) {
  var nav = document.getElementById(btn.getAttribute('aria-controls'));
  function set(open) {
    nav.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    if (!open) document.querySelectorAll('.nav-products.is-open').forEach(function (li) { li.classList.remove('is-open'); li.querySelector('.nav-trigger').setAttribute('aria-expanded', 'false'); });
  }
  btn.addEventListener('click', function () { set(!nav.classList.contains('open')); });
  nav.addEventListener('click', function (e) { if (e.target.closest('a[href]')) set(false); });
  document.addEventListener('click', function (e) {
    if (nav.classList.contains('open') && !nav.contains(e.target) && !btn.contains(e.target)) set(false);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('open')) { set(false); btn.focus(); } });
});

// Products menu: opens on hover (pointer devices) and on click / keyboard everywhere; closes on an outside tap.
document.querySelectorAll('.nav-products').forEach(function (li) {
  var btn = li.querySelector('.nav-trigger');
  var hoverable = window.matchMedia('(hover: hover) and (min-width: 768px)');
  var timer;
  function set(open) {
    li.classList.toggle('is-open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  btn.addEventListener('click', function () { set(!li.classList.contains('is-open')); });
  li.addEventListener('mouseenter', function () { if (hoverable.matches) { clearTimeout(timer); set(true); } });
  li.addEventListener('mouseleave', function () { if (hoverable.matches) { timer = setTimeout(function () { set(false); }, 180); } });
  li.addEventListener('keydown', function (e) { if (e.key === 'Escape') { set(false); btn.focus(); } });
  li.addEventListener('focusout', function (e) { if (e.relatedTarget && !li.contains(e.relatedTarget)) set(false); });
  document.addEventListener('click', function (e) { if (!li.contains(e.target)) set(false); });
});
