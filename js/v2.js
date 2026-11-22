// Phone menu toggle for the MINT CONSENT / MINT PILs pages.
document.querySelectorAll('.burger').forEach(function (btn) {
  var nav = document.getElementById(btn.getAttribute('aria-controls'));
  btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
});
