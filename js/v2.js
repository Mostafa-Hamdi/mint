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
  var LABEL = {
    terms: 'Terms Of Use',
    privacy: 'Privacy Policy',
    faq: 'FAQ',
    refunds: 'Refunds Policy',
    copyright: 'Copyrights',
  };
  var chips = document.createElement('nav');
  chips.className = 'lgc';
  chips.setAttribute('aria-label', 'Legal sections');
  chips.innerHTML = ORDER.map(function (k) {
    return (
      '<a href="pils-legal.html" data-section="' + k + '">' + LABEL[k] + '</a>'
    );
  }).join('');
  document.body.appendChild(chips);
  function vis(sel) {
    return Array.prototype.find.call(
      document.querySelectorAll(sel),
      function (el) {
        return el.offsetParent !== null;
      },
    );
  }
  function docTop(el) {
    return el.getBoundingClientRect().top + window.scrollY;
  }
  function size() {
    // the desktop list stays pinned until the footer
    var nav = vis('.fv-d .lgn'),
      end = vis('[data-anchor="legal-end"]');
    if (nav && end)
      nav.style.height = Math.max(0, docTop(end) - docTop(nav)) + 'px';
  }
  var current = null;
  function spy() {
    var line = (window.innerWidth < 768 ? 80 : 100) + 60;
    var list = ORDER.map(function (k) {
      var a = vis('[data-anchor="' + k + '"]');
      return a ? { k: k, top: a.getBoundingClientRect().top } : null;
    })
      .filter(Boolean)
      .sort(function (a, b) {
        return a.top - b.top;
      });
    var act = list.length ? list[0].k : null;
    list.forEach(function (s) {
      if (s.top <= line) act = s.k;
    });
    if (act !== current) {
      current = act;
      document.querySelectorAll('.lgn-a, .lgc a').forEach(function (a) {
        if (a.getAttribute('data-section') === act)
          a.setAttribute('aria-current', 'true');
        else a.removeAttribute('aria-current');
      });
      var on = chips.querySelector('[aria-current="true"]');
      if (on)
        chips.scrollTo({
          left: on.offsetLeft - (chips.clientWidth - on.offsetWidth) / 2,
          behavior: 'smooth',
        });
    }
    // chips appear once the phone list has scrolled under the header, and leave at the footer
    var mnav = vis('.fv-m .lgn'),
      end = vis('[data-anchor="legal-end"]');
    var show = !!(
      mnav &&
      mnav.getBoundingClientRect().bottom < 70 &&
      (!end || end.getBoundingClientRect().top > 160)
    );
    // sit 8px under whatever height the header has at this width (phone capsule vs taller tablet capsule)
    var pill = document.querySelector('.fh-pill');
    var hb = pill ? pill.getBoundingClientRect().bottom : 64;
    chips.style.top = Math.round(hb + 8) + 'px';
    var under = hb + 8;
    show = !!(
      mnav &&
      mnav.getBoundingClientRect().bottom < under &&
      (!end || end.getBoundingClientRect().top > under + 90)
    );
    chips.classList.toggle('show', show);
  }
  var tick = false;
  window.addEventListener(
    'scroll',
    function () {
      if (!tick) {
        tick = true;
        requestAnimationFrame(function () {
          tick = false;
          spy();
        });
      }
    },
    { passive: true },
  );
  window.addEventListener('resize', function () {
    size();
    spy();
  });
  window.addEventListener('load', function () {
    size();
    spy();
  });
  document.addEventListener('transitionend', function (e) {
    if (
      e.target.classList &&
      (e.target.classList.contains('bd') || e.target.classList.contains('az-a'))
    ) {
      size();
      spy();
    }
  });
  size();
  spy();
})();

// Typography: re-flow body text.
// Each paragraph (lines up to a real line break) is re-flowed on its own: Figma's manual line breaks are dropped,
// the text fills the width it has (its widest design line, or its card), line height is evened out, and body copy
// on phones is capped at 17. Every paragraph keeps its first baseline where the design puts it, so it can only get
// shorter and never runs into what follows. Paragraphs that sit next to a separate link or other text stay as designed.
(function () {
  function u(fv) {
    return (
      fv.getBoundingClientRect().width /
      parseFloat(fv.style.getPropertyValue('--W'))
    );
  }
  function v(el, name) {
    return parseFloat(el.style.getPropertyValue(name));
  }
  function hits(a, b) {
    return (
      a.left < b.right &&
      b.left < a.right &&
      a.top < b.bottom &&
      b.top < a.bottom
    );
  }
  function box(rs) {
    return {
      left: Math.min.apply(
        null,
        rs.map(function (r) {
          return r.left;
        }),
      ),
      right: Math.max.apply(
        null,
        rs.map(function (r) {
          return r.right;
        }),
      ),
      top:
        Math.min.apply(
          null,
          rs.map(function (r) {
            return r.top;
          }),
        ) + 2,
      bottom:
        Math.max.apply(
          null,
          rs.map(function (r) {
            return r.bottom;
          }),
        ) - 2,
    };
  }
  function flow(p) {
    var fv = p.closest('.fv');
    if (!fv || !p.offsetParent) return;
    var U = u(fv);
    if (!U) return;
    var spans = Array.prototype.slice.call(p.querySelectorAll(':scope > .ln'));
    if (!spans.length) return;
    var fs = parseFloat(p.dataset.fs),
      gap = parseFloat(p.dataset.gap),
      asc = parseFloat(p.dataset.asc),
      x = parseFloat(p.dataset.x);
    // one body size per screen: never above 20 (desktop) / 19 (tablet) / 17 (phone)
    var cap = fv.classList.contains('fv-m')
      ? 17
      : fv.classList.contains('fv-t')
        ? 20
        : 20;
    var nfs = Math.min(fs, cap);
    if (!(gap > 0)) gap = fs * 1.6;
    var lh = Math.min(gap, nfs * 1.6);
    // lines
    var byY = {};
    spans.forEach(function (s) {
      var y = v(s, '--y');
      (byY[y] = byY[y] || []).push({ s: s, r: s.getBoundingClientRect() });
    });
    var lines = Object.keys(byY)
      .map(parseFloat)
      .sort(function (a, b) {
        return a - b;
      })
      .map(function (y) {
        var row = byY[y].sort(function (a, b) {
          return a.r.left - b.r.left;
        });
        return {
          y: y,
          row: row,
          w: row[row.length - 1].r.right - row[0].r.left,
          br: row[row.length - 1].s.hasAttribute('data-br'),
        };
      });
    var maxW = Math.max.apply(
      null,
      lines.map(function (l) {
        return l.w;
      }),
    );
    var wU = maxW / U + 2;
    var FW = parseFloat(fv.style.getPropertyValue('--W'));
    var mobile = fv.classList.contains('fv-m'),
      ta = 'left';
    if (mobile) {
      // phone type scale: body 16.5-18, headings capped (34 for big titles, 28 for section titles), steady line height
      var head = /^H[1-3]$/.test(p.tagName) || fs >= 26;
      if (head) {
        nfs = Math.min(fs, fs >= 44 ? 34 : 28);
        lh = nfs * 1.22;
      } else {
        nfs = Math.min(Math.max(fs, 16.5), 18);
        lh = nfs * 1.6;
      }
      var fl = fv.getBoundingClientRect().left;
      var lefts = lines.map(function (l) {
        return (l.row[0].r.left - fl) / U;
      });
      var cents = lines.map(function (l) {
        return (
          ((l.row[0].r.left + l.row[l.row.length - 1].r.right) / 2 - fl) / U
        );
      });
      var isLeft =
        Math.max.apply(null, lefts) - Math.min.apply(null, lefts) < 2;
      var isCent =
        Math.max.apply(null, cents) - Math.min.apply(null, cents) < 12;
      if (lines.length === 1) {
        isCent = Math.abs(cents[0] - FW / 2) < 8;
        isLeft = !isCent;
      } else if (!isLeft && !isCent) return; // irregular layout: leave as designed
      if (isLeft && !(lines.length === 1 && isCent)) {
        ta = 'left';
        wU = Math.max(
          wU,
          (p.dataset.cw ? parseFloat(p.dataset.cw) : FW - 20) - x,
        );
      } else {
        ta = 'center';
        var c =
          cents.reduce(function (a, b) {
            return a + b;
          }, 0) / cents.length;
        wU = 2 * Math.min(c - 18, FW - 18 - c);
        x = c - wU / 2;
      }
    } else if (p.dataset.cw) wU = Math.max(wU, parseFloat(p.dataset.cw) - x);
    else if (x < FW * 0.3) wU = Math.max(wU, FW - 2 * x); // free-standing text in the left column: use the page width, same margin both sides
    // paragraphs: a line ending in a real break closes one; a jump of more than 1.6 line gaps also does
    var paras = [],
      cur = [];
    lines.forEach(function (l, i) {
      if (cur.length && l.y - cur[cur.length - 1].y > gap * 1.6) {
        paras.push(cur);
        cur = [];
      }
      cur.push(l);
      if (l.br || i === lines.length - 1) {
        paras.push(cur);
        cur = [];
      }
    });
    var blockers = Array.prototype.filter
      .call(
        fv.querySelectorAll('a.tx, .crumb, .tx .ln, .tx .fl'),
        function (el) {
          return !p.contains(el) && el.offsetParent;
        },
      )
      .map(function (el) {
        return el.getBoundingClientRect();
      });
    var out = '',
      run = [];
    function paraHtml(para) {
      return para
        .map(function (l, n) {
          var t = l.row
            .map(function (o) {
              var st = o.s
                .getAttribute('style')
                .split(';')
                .filter(function (d) {
                  return d && d.trim().indexOf('--') !== 0;
                })
                .join(';');
              return st
                ? '<span style="' + st + '">' + o.s.innerHTML + '</span>'
                : o.s.innerHTML;
            })
            .join('');
          return t.replace(/\s+$/, '') + (n === para.length - 1 ? '' : ' ');
        })
        .join('')
        .trim();
    }
    // consecutive free paragraphs flow as one block from the first one's baseline; blank design lines stay blank lines
    function flush() {
      if (!run.length) return;
      var html = '';
      run.forEach(function (para, i) {
        if (i) {
          var prev = run[i - 1];
          html += '<br>';
          if (para[0].y - prev[prev.length - 1].y > gap * 1.6) html += '<br>'; // a skipped design line = blank line
        }
        html += paraHtml(para);
      });
      // a link Figma broke over two lines (e.g. an e-mail) becomes one link again, with no space inside it
      html = html.replace(
        /<\/a>(<\/span>)?\s+(<span style="[^"]*">)?<a href="[^"]*">/g,
        '',
      );
      var base = run[0][0].y + asc * fs;
      var top = base - ((lh - nfs * 1.4) / 2 + asc * nfs);
      out +=
        '<span class="fl" style="--x:' +
        x.toFixed(2) +
        ';--y:' +
        top.toFixed(2) +
        ';--w:' +
        wU.toFixed(1) +
        ';--fs:' +
        nfs +
        ';--lh:' +
        lh.toFixed(2) +
        (ta === 'center' ? ';text-align:center' : '') +
        '">' +
        html +
        '</span>';
      run = [];
    }
    paras.forEach(function (para) {
      if (!paraHtml(para)) return; // empty design lines are handled as spacing by flush()
      var rs = [];
      para.forEach(function (l) {
        l.row.forEach(function (o) {
          rs.push(o.r);
        });
      });
      var area = box(rs);
      area.left -= 40;
      area.right += 40;
      if (
        blockers.some(function (b) {
          return hits(area, b);
        })
      ) {
        flush();
        para.forEach(function (l) {
          l.row.forEach(function (o) {
            out += o.s.outerHTML;
          });
        });
        return;
      }
      // other text drawn between the previous paragraph and this one: start this one at its own design position
      if (run.length) {
        var last = run[run.length - 1],
          lr = [];
        last.forEach(function (l) {
          l.row.forEach(function (o) {
            lr.push(o.r);
          });
        });
        var between = {
          left: area.left,
          right: area.right,
          top: box(lr).bottom,
          bottom: area.top + 2,
        };
        if (
          between.bottom > between.top &&
          blockers.some(function (b) {
            return hits(between, b);
          })
        )
          flush();
      }
      run.push(para);
    });
    flush();
    p.innerHTML = out;
    p.removeAttribute('data-flow');
  }
  function run() {
    document.querySelectorAll('[data-flow]').forEach(function (p) {
      if (!p.offsetParent) return;
      flow(p);
      p.removeAttribute('data-flow');
    });
  }
  (document.fonts && document.fonts.ready
    ? document.fonts.ready
    : Promise.resolve()
  ).then(run);
  window.addEventListener('load', run);
  var t;
  window.addEventListener('resize', function () {
    clearTimeout(t);
    t = setTimeout(run, 150);
  });
})();

// Pricing: country picker (United Kingdom / Saudi Arabia / Egypt) and Continue -> that country's office on Contact.
document.querySelectorAll('[data-cty]').forEach(function (box) {
  var btn = box.querySelector('.cty-b'),
    list = box.querySelector('.cty-l'),
    items = Array.prototype.slice.call(list.querySelectorAll('li'));
  var label = box.querySelector('.cty-v'),
    act = -1;
  function mark() {
    items.forEach(function (li, i) {
      li.classList.toggle('act', i === act);
    });
    if (items[act]) list.setAttribute('aria-activedescendant', items[act].id);
  }
  function open(on) {
    box.classList.toggle('open', on);
    btn.setAttribute('aria-expanded', on ? 'true' : 'false');
    if (on) {
      act = Math.max(
        0,
        items.findIndex(function (li) {
          return li.getAttribute('aria-selected') === 'true';
        }),
      );
      mark();
      list.focus({ preventScroll: true });
    }
  }
  function pick(li) {
    items.forEach(function (x) {
      x.setAttribute('aria-selected', x === li ? 'true' : 'false');
    });
    label.innerHTML = li.innerHTML;
    box.dataset.value = li.dataset.v;
    box.classList.add('has');
    box.classList.remove('need');
    open(false);
    btn.focus();
  }
  btn.addEventListener('click', function () {
    open(!box.classList.contains('open'));
  });
  btn.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown') {
      open(true);
      e.preventDefault();
    }
  });
  items.forEach(function (li) {
    li.addEventListener('click', function () {
      pick(li);
    });
  });
  list.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown') {
      act = (act + 1) % items.length;
      mark();
      e.preventDefault();
    } else if (e.key === 'ArrowUp') {
      act = (act - 1 + items.length) % items.length;
      mark();
      e.preventDefault();
    } else if (e.key === 'Enter' || e.key === ' ') {
      if (items[act]) pick(items[act]);
      e.preventDefault();
    } else if (e.key === 'Escape') {
      open(false);
      btn.focus();
    }
  });
  document.addEventListener('click', function (e) {
    if (!box.contains(e.target)) open(false);
  });
  var go = box.closest('.fv').querySelector('.cty-go');
  if (go)
    go.addEventListener('click', function () {
      if (!box.dataset.value) {
        box.classList.remove('need');
        void box.offsetWidth;
        box.classList.add('need');
        open(true);
        return;
      }
      try {
        sessionStorage.setItem('mint-section', box.dataset.value);
      } catch (err) {}
      location.href = 'contact.html';
    });
});

// HTML accordions (guide + legal FAQ): the question button opens / closes its answer.
document.querySelectorAll('.az-q[aria-controls]').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var item = btn.closest('.az-i'),
      open = !item.classList.contains('open');
    item.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
});

// Guide videos: the play badge opens a video in a glass lightbox. Until the real guide videos exist,
// every thumbnail plays a short CC0 test clip (set data-video on a .az-media to use another file).
(function () {
  var TEST =
    'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4';
  var media = document.querySelectorAll('.az-media');
  if (!media.length) return;
  var box = document.createElement('div');
  box.className = 'vlb';
  box.setAttribute('role', 'dialog');
  box.setAttribute('aria-modal', 'true');
  box.setAttribute('aria-label', 'Video');
  box.innerHTML =
    '<div class="vlb-bg"></div><div class="vlb-card"><button type="button" class="vlb-x" aria-label="Close video"></button>' +
    '<video class="vlb-v" controls playsinline preload="none"></video><p class="vlb-t"></p></div>';
  document.body.appendChild(box);
  var v = box.querySelector('video'),
    title = box.querySelector('.vlb-t'),
    last = null;
  function close() {
    box.classList.remove('show');
    v.pause();
    setTimeout(function () {
      if (!box.classList.contains('show')) {
        v.removeAttribute('src');
        v.load();
      }
    }, 400);
    document.documentElement.classList.remove('vlb-lock');
    if (last) last.focus();
  }
  function open(fig) {
    last = fig.querySelector('.az-play');
    var img = fig.querySelector('img');
    v.poster = img ? img.currentSrc || img.src : '';
    v.src = fig.dataset.video || TEST;
    var q = fig.closest('.az-i');
    q = q && q.querySelector('.az-q span');
    title.textContent = q ? q.textContent : '';
    box.classList.add('show');
    document.documentElement.classList.add('vlb-lock');
    box.querySelector('.vlb-x').focus();
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  }
  media.forEach(function (fig) {
    var play = fig.querySelector('.az-play');
    if (!play) return;
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'az-play';
    b.setAttribute('aria-label', 'Play video');
    play.replaceWith(b);
    fig.addEventListener('click', function () {
      open(fig);
    });
  });
  box.querySelector('.vlb-x').addEventListener('click', close);
  box.querySelector('.vlb-bg').addEventListener('click', close);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && box.classList.contains('show')) close();
  });
})();

// Phones: after the text re-flow, even out the vertical rhythm. Every text block that got shorter gives back the
// space under it, every block that got longer gets room - using only rows of the drawing that are plain
// (a row identical to the one below it can be repeated or removed without anyone noticing).
(function () {
  function num(el, n) {
    return parseFloat(el.style.getPropertyValue(n));
  }
  function topOf(el) {
    var t = num(el, '--y'),
      d = el.querySelectorAll('[style*="--y"]');
    for (var i = 0; i < d.length; i++) {
      var y = num(d[i], '--y');
      if (!(t <= y)) t = isNaN(t) ? y : Math.min(t, y);
    }
    return t;
  }
  function fit(fv) {
    if (!fv.classList.contains('fv-m') || !fv.dataset.runs || !fv.offsetParent)
      return;
    var W = num(fv, '--W'),
      H = num(fv, '--H'),
      U = fv.getBoundingClientRect().width / W;
    var runs = fv.dataset.runs
      .split(',')
      .filter(Boolean)
      .map(function (r) {
        var c = r.split(':'),
          ab = c[0].split('-').map(Number);
        ab.color = c[1] || '';
        return ab;
      });
    function runColor(y) {
      var r = runs.filter(function (q) {
        return q[0] <= y && y < q[1];
      })[0];
      return r ? r.color : '';
    }
    fv.removeAttribute('data-runs');
    // 1. everything into bands (a page without accordions is one band)
    if (!fv.classList.contains('banded')) {
      var b = document.createElement('div');
      b.className = 'bd';
      b.style.cssText = '--y0:0;--h:' + H;
      var inn = document.createElement('div');
      inn.className = 'bd-in';
      b.appendChild(inn);
      while (fv.firstChild) inn.appendChild(fv.firstChild);
      fv.appendChild(b);
      fv.classList.add('banded');
    }
    var plain = function () {
      return Array.prototype.filter.call(fv.children, function (e) {
        return e.className === 'bd';
      });
    };
    // loose items placed straight on the section (legal nav) move into the band that holds them
    Array.prototype.slice.call(fv.children).forEach(function (e) {
      if (e.classList.contains('bd')) return;
      var y = topOf(e);
      if (isNaN(y)) return;
      var host = plain().filter(function (b) {
        var y0 = num(b, '--y0');
        return y0 <= y && y < y0 + num(b, '--h');
      })[0];
      if (host) host.firstElementChild.appendChild(e);
    });
    // 1b. a one-line centred heading sitting right on top of a left-aligned paragraph lines up with that paragraph
    var fls = Array.prototype.slice
      .call(fv.querySelectorAll('.bd > .bd-in > .tx > .fl'))
      .map(function (f) {
        return {
          f: f,
          y: num(f, '--y'),
          x: num(f, '--x'),
          w: num(f, '--w'),
          c: f.style.textAlign === 'center',
          h: f.getBoundingClientRect().height / U,
          lh: num(f, '--lh'),
        };
      })
      .sort(function (a, b) {
        return a.y - b.y;
      });
    fls.forEach(function (a, i) {
      if (!a.c || a.h > a.lh * 1.5) return;
      var b = fls.slice(i + 1).filter(function (o) {
        return o.y > a.y;
      })[0];
      if (!b || b.c || b.y - (a.y + a.h) > 90) return;
      a.f.style.textAlign = 'left';
      a.f.style.setProperty('--x', b.x);
      a.f.style.setProperty('--w', b.w);
    });
    // 2. measure text blocks (design units)
    function ext(el) {
      var band = el.closest('.bd'),
        br = band.getBoundingClientRect(),
        y0 = num(band, '--y0');
      var rs = Array.prototype.map
        .call(el.querySelectorAll('.ln, .fl'), function (n) {
          return n.getBoundingClientRect();
        })
        .filter(function (r) {
          return r.height;
        });
      if (!rs.length) {
        var r0 = el.getBoundingClientRect();
        if (!r0.height) return null;
        rs = [r0];
      }
      return {
        top:
          y0 +
          (Math.min.apply(
            null,
            rs.map(function (r) {
              return r.top;
            }),
          ) -
            br.top) /
            U,
        bot:
          y0 +
          (Math.max.apply(
            null,
            rs.map(function (r) {
              return r.bottom;
            }),
          ) -
            br.top) /
            U,
      };
    }
    var items = [];
    plain().forEach(function (b) {
      Array.prototype.forEach.call(b.firstElementChild.children, function (e) {
        if (e.classList.contains('decor')) return;
        var x = ext(e);
        if (!x) {
          var t = topOf(e);
          if (isNaN(t)) return;
          x = { top: t, bot: t + 1 };
        }
        x.el = e;
        x.yb = parseFloat(e.dataset.yb);
        items.push(x);
      });
    });
    function inRun(a, b) {
      // longest plain stretch inside [a, b)
      var best = null;
      runs.forEach(function (r) {
        var s = Math.max(a, r[0]),
          e = Math.min(b, r[1]);
        if (e - s > 0 && (!best || e - s > best[1] - best[0])) best = [s, e];
      });
      return best;
    }
    var ops = [];
    items
      .filter(function (x) {
        return !isNaN(x.yb);
      })
      .sort(function (a, b) {
        return a.top - b.top;
      })
      .forEach(function (x) {
        var delta = x.bot - x.yb;
        if (Math.abs(delta) < 4) return;
        var next = items
          .filter(function (o) {
            return o !== x && o.top > Math.min(x.bot, x.yb) - 1;
          })
          .reduce(function (m, o) {
            return Math.min(m, o.top);
          }, H);
        if (delta < 0) return; // shorter: the empty-stretch rule below takes the space back
        {
          // got longer: add room at the first plain row under the old bottom
          var seg2 = inRun(x.yb - 2, Math.max(next, x.yb + 2) - 2);
          if (!seg2) seg2 = inRun(x.top + 4, next - 2);
          if (seg2) ops.push({ y: seg2[0] + 1, add: delta + 8 });
        }
      });
    // every empty stretch (plain rows with no text, logo or picture on them) taller than 88 shrinks to 52
    var HH = num(fv, '--HH') || 0; // the drawn header is hidden
    var busy = items.map(function (x) {
      return [x.top - 4, x.bot + 4];
    });
    // inner heroes: the wide photo under the navy block is cropped to 220 (top and bottom), and the space above the
    // logo equals the space under the breadcrumb (36 each)
    var photos = (fv.dataset.imgs || '')
      .split(',')
      .filter(Boolean)
      .map(function (r) {
        return {
          f: /f$/.test(r),
          a: parseFloat(r),
          b: parseFloat(r.split('-')[1]),
        };
      });
    var ph = photos.filter(function (q) {
      return q.f && q.a > HH + 40 && q.a < HH + 800;
    })[0];
    var T = 36;
    if (ph && ph.b - ph.a > 230) {
      var pc = ph.b - ph.a - 220,
        h1 = Math.round(pc / 2);
      ops.push({ y: ph.a, cut: h1 });
      ops.push({ y: ph.b - (pc - h1), cut: pc - h1 });
    }
    runs.forEach(function (r) {
      var segs = [[Math.max(r[0], HH), r[1]]];
      busy.forEach(function (b) {
        segs = segs.reduce(function (acc, s_) {
          if (b[1] <= s_[0] || b[0] >= s_[1]) acc.push(s_);
          else {
            if (b[0] > s_[0]) acc.push([s_[0], b[0]]);
            if (b[1] < s_[1]) acc.push([b[1], s_[1]]);
          }
          return acc;
        }, []);
      });
      segs.forEach(function (s_) {
        var L = s_[1] - s_[0],
          keep = 52,
          lim = 88;
        if (ph && (s_[0] <= HH + 2 || Math.abs(s_[1] - ph.a) < 4)) {
          keep = T;
          lim = T + 2;
        } // inner hero padding, equal top and bottom
        if (L <= lim) return;
        var c = L - keep,
          y = s_[0] + keep / 2;
        if (
          !ops.some(function (o) {
            return o.y < y + c && y < o.y + (o.cut || 1);
          })
        )
          ops.push({ y: y, cut: c });
      });
    });
    var imgR = (fv.dataset.imgs || '')
      .split(',')
      .filter(Boolean)
      .map(function (r) {
        return r.replace('f', '').split('-').map(Number);
      });
    var svgUrl = fv.dataset.svg;
    function lightDecor(band) {
      // a strip with no photo in it can use a plain <img> of the drawing (much lighter than <object>)
      var y0 = num(band, '--y0'),
        y1 = y0 + num(band, '--h'),
        d = band.firstElementChild.querySelector(':scope > .decor');
      if (!svgUrl || !d || d.tagName !== 'OBJECT') return;
      if (
        imgR.some(function (r) {
          return r[0] < y1 && r[1] > y0;
        })
      )
        return;
      var im = document.createElement('img');
      im.className = 'decor';
      im.alt = '';
      im.setAttribute('aria-hidden', 'true');
      im.src = svgUrl;
      d.replaceWith(im);
    }
    // 3. apply from the bottom up (design coordinates stay valid)
    ops.sort(function (a, b) {
      return b.y - a.y;
    });
    var used = [];
    ops.forEach(function (op) {
      var a = op.y,
        e = op.y + (op.cut || 0);
      if (
        used.some(function (u) {
          return a < u[1] && u[0] < e + 1;
        })
      )
        return;
      var band = plain().filter(function (b) {
        var y0 = num(b, '--y0');
        return y0 <= a && e <= y0 + num(b, '--h');
      })[0];
      if (!band) return;
      used.push([a, e]);
      var y0 = num(band, '--y0'),
        y1 = y0 + num(band, '--h'),
        inn = band.firstElementChild;
      var decor = inn.querySelector(':scope > .decor');
      var nb = document.createElement('div');
      nb.className = 'bd';
      nb.style.cssText = '--y0:' + e + ';--h:' + (y1 - e);
      var ni = document.createElement('div');
      ni.className = 'bd-in';
      nb.appendChild(ni);
      if (decor) ni.appendChild(decor.cloneNode(true));
      Array.prototype.slice.call(inn.children).forEach(function (c) {
        if (c.classList.contains('decor')) return;
        var t = topOf(c);
        if (!isNaN(t) && t >= a) ni.appendChild(c);
      });
      band.style.setProperty('--h', a - y0);
      var after = band.nextSibling;
      if (op.add) {
        var st = document.createElement('div');
        st.className = 'bd st';
        st.style.cssText =
          '--y0:' + (a - 1) + ';--h:1;--k:' + op.add.toFixed(1);
        var si = document.createElement('div');
        si.className = 'bd-in';
        st.appendChild(si);
        var flat = runColor(a - 1) || runColor(a);
        if (flat) {
          st.style.background = flat;
          st.classList.add('flat');
        } // a flat colour: plain block, no image stretching
        else if (decor) {
          var sd = document.createElement('img');
          sd.className = 'decor';
          sd.alt = '';
          sd.setAttribute('aria-hidden', 'true');
          sd.src =
            svgUrl || decor.getAttribute('src') || decor.getAttribute('data');
          si.appendChild(sd);
        }
        fv.insertBefore(st, after);
      }
      fv.insertBefore(nb, after);
    });
    plain().forEach(lightDecor);
    function plainRow(y) {
      return runs.some(function (q) {
        return q[0] <= y && y < q[1];
      });
    }
    hero(fv, U);
    // joins inside one flat colour get a 6px block of that colour on top (under the text), so no hairline can show
    function edgeColor(b, top) {
      if (b.classList.contains('st')) return b.classList.contains('flat') ? b.style.backgroundColor : '';
      var y0 = num(b, '--y0'),
        y1 = y0 + num(b, '--h');
      return top
        ? plainRow(y0 + 3) && runColor(y0)
        : plainRow(y1 - 4) && runColor(y1 - 1);
    }
    function norm(c) {
      var d = document.createElement('i');
      d.style.color = c;
      return d.style.color;
    }
    var bands = Array.prototype.filter.call(fv.children, function (e) {
      return e.classList.contains('bd') && !e.classList.contains('hero');
    });
    // the block lives in the lower strip (top edge) or, when that one clips, the upper strip (bottom edge), so it moves with them
    function clips(b) {
      return b.classList.contains('st') || getComputedStyle(b).overflow !== 'visible';
    }
    for (var i = 1; i < bands.length; i++) {
      var up = bands[i - 1],
        dn = bands[i],
        ca = edgeColor(up, false),
        cb = edgeColor(dn, true);
      if (!ca || !cb || norm(ca) !== norm(cb)) continue;
      var host = !clips(dn) ? dn : !clips(up) ? up : null;
      if (!host) continue;
      var p = document.createElement('i');
      p.className = 'seam ' + (host === dn ? 'seam-t' : 'seam-b');
      p.setAttribute('aria-hidden', 'true');
      p.style.background = cb;
      host.appendChild(p);
    }
  }
  // phone heroes: restack the title / subtitle / text with steady spacing and keep the block centred
  function hero(fv, U) {
    var hb = fv.querySelector('.bd.hero'),
      hc = hb && hb.querySelector('.hero-c');
    if (!hc) return;
    var hy0 = num(hb, '--y0'),
      hh = num(hb, '--h');
    var blocks = Array.prototype.filter
      .call(hc.children, function (e) {
        return e.classList.contains('tx');
      })
      .map(function (e) {
        var rs = Array.prototype.map
          .call(e.querySelectorAll('.ln, .fl'), function (n) {
            return n.getBoundingClientRect();
          })
          .filter(function (r) {
            return r.height;
          });
        if (!rs.length) return null;
        var hr = hc.getBoundingClientRect();
        var t =
            (Math.min.apply(
              null,
              rs.map(function (r) {
                return r.top;
              }),
            ) -
              hr.top) /
            U,
          b =
            (Math.max.apply(
              null,
              rs.map(function (r) {
                return r.bottom;
              }),
            ) -
              hr.top) /
            U;
        return { el: e, top: t, bot: b, yb: parseFloat(e.dataset.yb) };
      })
      .filter(Boolean)
      .sort(function (a, b) {
        return a.top - b.top;
      });
    if (!blocks.length) return;
    var y = blocks[0].top,
      prevDesignBot = null;
    blocks.forEach(function (b, i) {
      if (i) {
        var g = isNaN(prevDesignBot) ? 20 : b.top - prevDesignBot; // design gap (tops keep their design place)
        y += Math.min(Math.max(g, 14), 36);
      }
      var shift = y - b.top;
      if (Math.abs(shift) > 0.5)
        b.el.style.transform =
          'translateY(calc(' + shift.toFixed(1) + ' * var(--u)))';
      prevDesignBot = b.yb;
      y += b.bot - b.top;
    });
    var top = blocks[0].top,
      bot = y; // relative to the frame (hero-c sits at the frame origin)
    var dy = hy0 + hh / 2 - (top + bot) / 2;
    // the hero is as tall as its content plus the same 44 above and below
    var vis = Math.min(hh, bot - top + 88);
    hb.style.setProperty('--vis', 'calc(' + vis.toFixed(1) + ' * var(--u))');
    hc.style.setProperty('--dy', dy.toFixed(1));
  }
  function run() {
    document.querySelectorAll('section.fv-m[data-runs]').forEach(fit);
  }
  window.__mintFit = run;
  (document.fonts && document.fonts.ready
    ? document.fonts.ready
    : Promise.resolve()
  ).then(function () {
    setTimeout(run, 50);
  });
})();
