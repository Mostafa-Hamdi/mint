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
    // sit 8px under whatever height the header has at this width (phone capsule vs taller tablet capsule)
    var pill = document.querySelector('.fh-pill');
    var hb = pill ? pill.getBoundingClientRect().bottom : 64;
    chips.style.top = Math.round(hb + 8) + 'px';
    var under = hb + 8;
    show = !!(mnav && mnav.getBoundingClientRect().bottom < under && (!end || end.getBoundingClientRect().top > under + 90));
    chips.classList.toggle('show', show);
  }
  var tick = false;
  window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(function () { tick = false; spy(); }); } }, { passive: true });
  window.addEventListener('resize', function () { size(); spy(); });
  window.addEventListener('load', function () { size(); spy(); });
  document.addEventListener('transitionend', function (e) { if (e.target.classList && (e.target.classList.contains('bd') || e.target.classList.contains('az-a'))) { size(); spy(); } });
  size(); spy();
})();

// Typography: re-flow body text.
// Each paragraph (lines up to a real line break) is re-flowed on its own: Figma's manual line breaks are dropped,
// the text fills the width it has (its widest design line, or its card), line height is evened out, and body copy
// on phones is capped at 17. Every paragraph keeps its first baseline where the design puts it, so it can only get
// shorter and never runs into what follows. Paragraphs that sit next to a separate link or other text stay as designed.
(function () {
  function u(fv) { return fv.getBoundingClientRect().width / parseFloat(fv.style.getPropertyValue('--W')); }
  function v(el, name) { return parseFloat(el.style.getPropertyValue(name)); }
  function hits(a, b) { return a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom; }
  function box(rs) {
    return { left: Math.min.apply(null, rs.map(function (r) { return r.left; })), right: Math.max.apply(null, rs.map(function (r) { return r.right; })),
             top: Math.min.apply(null, rs.map(function (r) { return r.top; })) + 2, bottom: Math.max.apply(null, rs.map(function (r) { return r.bottom; })) - 2 };
  }
  function flow(p) {
    var fv = p.closest('.fv'); if (!fv || !p.offsetParent) return;
    var U = u(fv); if (!U) return;
    var spans = Array.prototype.slice.call(p.querySelectorAll(':scope > .ln')); if (!spans.length) return;
    var fs = parseFloat(p.dataset.fs), gap = parseFloat(p.dataset.gap), asc = parseFloat(p.dataset.asc), x = parseFloat(p.dataset.x);
    // one body size per screen: never above 20 (desktop) / 19 (tablet) / 17 (phone)
    var cap = fv.classList.contains('fv-m') ? 17 : fv.classList.contains('fv-t') ? 20 : 20;
    var nfs = Math.min(fs, cap);
    if (!(gap > 0)) gap = fs * 1.6;
    var lh = Math.min(gap, nfs * 1.6);
    // lines
    var byY = {};
    spans.forEach(function (s) { var y = v(s, '--y'); (byY[y] = byY[y] || []).push({ s: s, r: s.getBoundingClientRect() }); });
    var lines = Object.keys(byY).map(parseFloat).sort(function (a, b) { return a - b; }).map(function (y) {
      var row = byY[y].sort(function (a, b) { return a.r.left - b.r.left; });
      return { y: y, row: row, w: row[row.length - 1].r.right - row[0].r.left, br: row[row.length - 1].s.hasAttribute('data-br') };
    });
    var maxW = Math.max.apply(null, lines.map(function (l) { return l.w; }));
    var wU = maxW / U + 2;
    var FW = parseFloat(fv.style.getPropertyValue('--W'));
    if (p.dataset.cw) wU = Math.max(wU, parseFloat(p.dataset.cw) - x);
    else if (x < FW * .3) wU = Math.max(wU, FW - 2 * x);   // free-standing text in the left column: use the page width, same margin both sides
    // paragraphs: a line ending in a real break closes one; a jump of more than 1.6 line gaps also does
    var paras = [], cur = [];
    lines.forEach(function (l, i) {
      if (cur.length && l.y - cur[cur.length - 1].y > gap * 1.6) { paras.push(cur); cur = []; }
      cur.push(l);
      if (l.br || i === lines.length - 1) { paras.push(cur); cur = []; }
    });
    var blockers = Array.prototype.filter.call(fv.querySelectorAll('a.tx, .crumb, .tx .ln, .tx .fl'), function (el) { return !p.contains(el) && el.offsetParent; })
      .map(function (el) { return el.getBoundingClientRect(); });
    var out = '', run = [];
    function paraHtml(para) {
      return para.map(function (l, n) {
        var t = l.row.map(function (o) {
          var st = o.s.getAttribute('style').split(';').filter(function (d) { return d && d.trim().indexOf('--') !== 0; }).join(';');
          return st ? '<span style="' + st + '">' + o.s.innerHTML + '</span>' : o.s.innerHTML;
        }).join('');
        return t.replace(/\s+$/, '') + (n === para.length - 1 ? '' : ' ');
      }).join('').trim();
    }
    // consecutive free paragraphs flow as one block from the first one's baseline; blank design lines stay blank lines
    function flush() {
      if (!run.length) return;
      var html = '';
      run.forEach(function (para, i) {
        if (i) {
          var prev = run[i - 1];
          html += '<br>';
          if (para[0].y - prev[prev.length - 1].y > gap * 1.6) html += '<br>';   // a skipped design line = blank line
        }
        html += paraHtml(para);
      });
      var base = run[0][0].y + asc * fs;
      var top = base - ((lh - nfs * 1.4) / 2 + asc * nfs);
      out += '<span class="fl" style="--x:' + x + ';--y:' + top.toFixed(2) + ';--w:' + wU.toFixed(1) + ';--fs:' + nfs + ';--lh:' + lh.toFixed(2) + '">' + html + '</span>';
      run = [];
    }
    paras.forEach(function (para) {
      if (!paraHtml(para)) return;           // empty design lines are handled as spacing by flush()
      var rs = []; para.forEach(function (l) { l.row.forEach(function (o) { rs.push(o.r); }); });
      var area = box(rs); area.left -= 40; area.right += 40;
      if (blockers.some(function (b) { return hits(area, b); })) {
        flush();
        para.forEach(function (l) { l.row.forEach(function (o) { out += o.s.outerHTML; }); });
        return;
      }
      // other text drawn between the previous paragraph and this one: start this one at its own design position
      if (run.length) {
        var last = run[run.length - 1], lr = [];
        last.forEach(function (l) { l.row.forEach(function (o) { lr.push(o.r); }); });
        var between = { left: area.left, right: area.right, top: box(lr).bottom, bottom: area.top + 2 };
        if (between.bottom > between.top && blockers.some(function (b) { return hits(between, b); })) flush();
      }
      run.push(para);
    });
    flush();
    p.innerHTML = out;
    p.removeAttribute('data-flow');
  }
  function run() { document.querySelectorAll('[data-flow]').forEach(flow); }
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(run);
  window.addEventListener('load', run);
  var t; window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(run, 150); });
})();

// Pricing: country picker (United Kingdom / Saudi Arabia / Egypt) and Continue -> that country's office on Contact.
document.querySelectorAll('[data-cty]').forEach(function (box) {
  var btn = box.querySelector('.cty-b'), list = box.querySelector('.cty-l'), items = Array.prototype.slice.call(list.querySelectorAll('li'));
  var label = box.querySelector('.cty-v'), act = -1;
  function mark() {
    items.forEach(function (li, i) { li.classList.toggle('act', i === act); });
    if (items[act]) list.setAttribute('aria-activedescendant', items[act].id);
  }
  function open(on) {
    box.classList.toggle('open', on); btn.setAttribute('aria-expanded', on ? 'true' : 'false');
    if (on) {
      act = Math.max(0, items.findIndex(function (li) { return li.getAttribute('aria-selected') === 'true'; }));
      mark(); list.focus({ preventScroll: true });
    }
  }
  function pick(li) {
    items.forEach(function (x) { x.setAttribute('aria-selected', x === li ? 'true' : 'false'); });
    label.innerHTML = li.innerHTML; box.dataset.value = li.dataset.v; box.classList.add('has'); box.classList.remove('need');
    open(false); btn.focus();
  }
  btn.addEventListener('click', function () { open(!box.classList.contains('open')); });
  btn.addEventListener('keydown', function (e) { if (e.key === 'ArrowDown') { open(true); e.preventDefault(); } });
  items.forEach(function (li) { li.addEventListener('click', function () { pick(li); }); });
  list.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown') { act = (act + 1) % items.length; mark(); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { act = (act - 1 + items.length) % items.length; mark(); e.preventDefault(); }
    else if (e.key === 'Enter' || e.key === ' ') { if (items[act]) pick(items[act]); e.preventDefault(); }
    else if (e.key === 'Escape') { open(false); btn.focus(); }
  });
  document.addEventListener('click', function (e) { if (!box.contains(e.target)) open(false); });
  var go = box.closest('.fv').querySelector('.cty-go');
  if (go) go.addEventListener('click', function () {
    if (!box.dataset.value) { box.classList.remove('need'); void box.offsetWidth; box.classList.add('need'); open(true); return; }
    try { sessionStorage.setItem('mint-section', box.dataset.value); } catch (err) {}
    location.href = 'contact.html';
  });
});

// HTML accordions (guide + legal FAQ): the question button opens / closes its answer.
document.querySelectorAll('.az-q[aria-controls]').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var item = btn.closest('.az-i'), open = !item.classList.contains('open');
    item.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
});

// Guide videos: the play badge opens a video in a glass lightbox. Until the real guide videos exist,
// every thumbnail plays a short CC0 test clip (set data-video on a .az-media to use another file).
(function () {
  var TEST = 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4';
  var media = document.querySelectorAll('.az-media');
  if (!media.length) return;
  var box = document.createElement('div');
  box.className = 'vlb'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-label', 'Video');
  box.innerHTML = '<div class="vlb-bg"></div><div class="vlb-card"><button type="button" class="vlb-x" aria-label="Close video"></button>' +
    '<video class="vlb-v" controls playsinline preload="none"></video><p class="vlb-t"></p></div>';
  document.body.appendChild(box);
  var v = box.querySelector('video'), title = box.querySelector('.vlb-t'), last = null;
  function close() {
    box.classList.remove('show'); v.pause();
    setTimeout(function () { if (!box.classList.contains('show')) { v.removeAttribute('src'); v.load(); } }, 400);
    document.documentElement.classList.remove('vlb-lock');
    if (last) last.focus();
  }
  function open(fig) {
    last = fig.querySelector('.az-play');
    var img = fig.querySelector('img');
    v.poster = img ? img.currentSrc || img.src : '';
    v.src = fig.dataset.video || TEST;
    var q = fig.closest('.az-i'); q = q && q.querySelector('.az-q span');
    title.textContent = q ? q.textContent : '';
    box.classList.add('show'); document.documentElement.classList.add('vlb-lock');
    box.querySelector('.vlb-x').focus();
    var p = v.play(); if (p && p.catch) p.catch(function () {});
  }
  media.forEach(function (fig) {
    var play = fig.querySelector('.az-play');
    if (!play) return;
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'az-play'; b.setAttribute('aria-label', 'Play video');
    play.replaceWith(b);
    fig.addEventListener('click', function () { open(fig); });
  });
  box.querySelector('.vlb-x').addEventListener('click', close);
  box.querySelector('.vlb-bg').addEventListener('click', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && box.classList.contains('show')) close(); });
})();
