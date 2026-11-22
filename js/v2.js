// MINT CONSENT / MINT PILs pages.
// Phone menu: burger toggles it; a tap outside, a link tap or Esc closes it.
document.querySelectorAll('.burger').forEach(function (btn) {
  var nav = document.getElementById(btn.getAttribute('aria-controls'));
  function set(open) {
    nav.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }
  btn.addEventListener('click', function () { set(!nav.classList.contains('open')); });
  nav.addEventListener('click', function (e) { if (e.target.closest('a')) set(false); });
  document.addEventListener('click', function (e) {
    if (nav.classList.contains('open') && !nav.contains(e.target) && !btn.contains(e.target)) set(false);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('open')) { set(false); btn.focus(); } });
});
// Mark the current page in the phone menu.
var here = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.mnav a').forEach(function (a) { if (a.getAttribute('href') === here) a.setAttribute('aria-current', 'page'); });
// Each page holds three layouts, so "#contact" scrolls to the anchor of the visible one.
function goToHash(smooth) {
  if (!location.hash) return;
  var name = location.hash.slice(1);
  var t = Array.prototype.find.call(document.querySelectorAll('[data-anchor="' + name + '"]'), function (el) { return el.offsetParent; });
  if (t) t.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto' });
  else if (name === 'contact') location.href = 'contact.html';
}
window.addEventListener('load', function () { goToHash(false); });
window.addEventListener('hashchange', function () { goToHash(true); });
document.addEventListener('click', function (e) {
  var a = e.target.closest('a[href^="#"]');
  if (a && a.getAttribute('href').length > 1) { e.preventDefault(); history.pushState(null, '', a.getAttribute('href')); goToHash(true); }
});
