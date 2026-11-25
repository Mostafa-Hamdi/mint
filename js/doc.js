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
