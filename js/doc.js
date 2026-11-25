// Coded pages: accordions and the video player (no framework).
(function () {
  // accordions: one open at a time per list
  document.querySelectorAll('.acc').forEach(function (list) {
    list.addEventListener('click', function (e) {
      var q = e.target.closest('.acc-q');
      if (!q || !list.contains(q)) return;
      var item = q.closest('.acc-i');
      var open = !item.classList.contains('open');
      list.querySelectorAll('.acc-i.open').forEach(function (o) {
        if (o === item) return;
        o.classList.remove('open');
        o.querySelector('.acc-q').setAttribute('aria-expanded', 'false');
      });
      item.classList.toggle('open', open);
      q.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // video player: one <dialog> shared by every thumbnail
  var thumbs = document.querySelectorAll('.vid[data-video]');
  if (!thumbs.length || typeof HTMLDialogElement === 'undefined') return;
  var dlg = document.createElement('dialog');
  dlg.className = 'vdlg';
  dlg.setAttribute('aria-label', 'Video');
  dlg.innerHTML =
    '<p class="vdlg-t"></p><button type="button" class="vdlg-x" aria-label="Close video">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button>' +
    '<video controls playsinline preload="none"></video>';
  document.body.appendChild(dlg);
  var video = dlg.querySelector('video');
  var opener = null;
  function close() {
    video.pause();
    dlg.close();
  }
  dlg.addEventListener('close', function () {
    video.pause();
    video.removeAttribute('src');
    video.load();
    if (opener) opener.focus();
  });
  dlg.querySelector('.vdlg-x').addEventListener('click', close);
  dlg.addEventListener('click', function (e) {
    if (e.target === dlg) close(); // click on the backdrop
  });
  thumbs.forEach(function (t) {
    t.addEventListener('click', function () {
      opener = t;
      dlg.querySelector('.vdlg-t').textContent = t.getAttribute('data-title') || '';
      video.src = t.getAttribute('data-video');
      dlg.showModal();
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
    });
  });
})();

// Pricing: pick a country, then continue to that office on the Contact page
(function () {
  var f = document.querySelector('.cty-form');
  if (!f) return;
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var c = f.querySelector('input[name="country"]:checked');
    var msg = f.querySelector('.cty-msg');
    if (!c) {
      msg.textContent = 'Please choose your country first.';
      f.classList.remove('need');
      void f.offsetWidth;
      f.classList.add('need');
      f.querySelector('input[name="country"]').focus();
      return;
    }
    msg.textContent = '';
    try {
      sessionStorage.setItem('mint-section', c.value);
    } catch (err) {}
    location.href = 'contact.html';
  });
  f.addEventListener('change', function () {
    f.querySelector('.cty-msg').textContent = '';
  });
})();

// Legal: the section link of the part being read is highlighted (and kept in view in the chip row)
(function () {
  var nav = document.querySelector('.legal-nav');
  if (!nav) return;
  var links = {};
  nav.querySelectorAll('a[data-section]').forEach(function (a) {
    links[a.getAttribute('data-section')] = a;
  });
  var secs = Array.prototype.slice.call(document.querySelectorAll('.legal-s'));
  var ul = nav.querySelector('ul');
  var current = null;
  function set(id) {
    if (id === current || !links[id]) return;
    if (current && links[current]) links[current].removeAttribute('aria-current');
    links[id].setAttribute('aria-current', 'true');
    current = id;
    if (ul.scrollWidth > ul.clientWidth) {
      var a = links[id];
      ul.scrollTo({ left: a.offsetLeft - (ul.clientWidth - a.offsetWidth) / 2, behavior: 'smooth' });
    }
  }
  function update() {
    // the last section whose top has passed the upper third of the screen
    var line = window.innerHeight * 0.3;
    var pick = secs[0];
    secs.forEach(function (s) {
      if (s.getBoundingClientRect().top <= line) pick = s;
    });
    set(pick.id);
  }
  var ticking = false;
  window.addEventListener(
    'scroll',
    function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        ticking = false;
        update();
      });
    },
    { passive: true },
  );
  update();
})();
