// Phone menu toggle (tablet and desktop show the nav inline)
document.querySelectorAll('.hdr-burger').forEach(function (btn) {
  var nav = document.getElementById(btn.getAttribute('aria-controls'));
  btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
});

// Products menu: opens on hover (pointer devices) and on click / keyboard everywhere.
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
