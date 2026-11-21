/* Просмотр картинок проектов слушателей: тап → во весь экран,
   щипок / колесо / двойной тап — масштаб, перетаскивание, листание внутри проекта. */
(function () {
  'use strict';
  var SELECTOR = '.work-media img';
  var MAX = 6;
  var thumbs = Array.prototype.slice.call(document.querySelectorAll(SELECTOR));
  if (!thumbs.length) return;

  var root, img, countEl, capEl, group = [], index = 0, lastFocus = null;
  var s = 1, tx = 0, ty = 0;
  var ptrs = {}, startDist = 0, startScale = 1, startMid = null, startT = null, moved = false, downAt = 0;
  var lastTap = { t: 0, x: 0, y: 0 };

  function build() {
    root = document.createElement('div');
    root.className = 'lb';
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.setAttribute('aria-label', 'Просмотр изображения');
    root.innerHTML =
      '<img class="lb-img" alt="" draggable="false">' +
      '<button type="button" class="lb-btn lb-close" aria-label="Закрыть">×</button>' +
      '<button type="button" class="lb-btn lb-prev" aria-label="Предыдущее">‹</button>' +
      '<button type="button" class="lb-btn lb-next" aria-label="Следующее">›</button>' +
      '<div class="lb-info"><span class="lb-count"></span><span class="lb-cap"></span></div>';
    document.body.appendChild(root);
    img = root.querySelector('.lb-img');
    countEl = root.querySelector('.lb-count');
    capEl = root.querySelector('.lb-cap');
    root.querySelector('.lb-close').addEventListener('click', close);
    root.querySelector('.lb-prev').addEventListener('click', function () { go(-1); });
    root.querySelector('.lb-next').addEventListener('click', function () { go(1); });
    root.addEventListener('pointerdown', onDown);
    root.addEventListener('pointermove', onMove);
    root.addEventListener('pointerup', onUp);
    root.addEventListener('pointercancel', onUp);
    root.addEventListener('wheel', onWheel, { passive: false });
    document.addEventListener('keydown', onKey);
    window.addEventListener('resize', function () { if (isOpen()) { clamp(); apply(); } });
  }

  function isOpen() { return root && root.classList.contains('is-open'); }

  function apply(anim) {
    img.classList.toggle('is-anim', !!anim);
    img.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + s + ')';
    root.classList.toggle('is-zoomed', s > 1.02);
  }

  function clamp() {
    if (s <= 1) { s = 1; tx = 0; ty = 0; return; }
    var w = img.offsetWidth * s, h = img.offsetHeight * s;
    var mx = Math.max(0, (w - window.innerWidth) / 2);
    var my = Math.max(0, (h - window.innerHeight) / 2);
    tx = Math.max(-mx, Math.min(mx, tx));
    ty = Math.max(-my, Math.min(my, ty));
  }

  // Масштаб вокруг точки экрана (cx, cy); координаты считаем от центра окна.
  function zoomAt(ns, cx, cy) {
    ns = Math.max(1, Math.min(MAX, ns));
    var px = cx - window.innerWidth / 2, py = cy - window.innerHeight / 2;
    tx = px - (px - tx) * (ns / s);
    ty = py - (py - ty) * (ns / s);
    s = ns;
    clamp();
  }

  function show(i) {
    index = (i + group.length) % group.length;
    var el = group[index];
    s = 1; tx = 0; ty = 0; apply();
    img.src = el.currentSrc || el.src;
    img.alt = el.alt || '';
    countEl.textContent = (index + 1) + ' / ' + group.length;
    var cap = /^Превью\s/.test(el.alt || '') ? '' : (el.alt || '');
    capEl.textContent = cap;
    capEl.style.display = cap ? '' : 'none';
    root.classList.toggle('is-single', group.length < 2);
    // соседние кадры подгружаем заранее
    [index - 1, index + 1].forEach(function (k) {
      if (group.length > 1) { var p = new Image(); p.src = group[(k + group.length) % group.length].src; }
    });
  }

  function open(el) {
    if (!root) build();
    var box = el.closest('.work-media');
    group = box ? Array.prototype.slice.call(box.querySelectorAll('img')) : [el];
    lastFocus = el;
    root.classList.add('is-open');
    document.documentElement.classList.add('lb-lock');
    show(group.indexOf(el));
    root.querySelector('.lb-close').focus({ preventScroll: true });
  }

  function close() {
    if (!isOpen()) return;
    root.classList.remove('is-open', 'is-zoomed');
    document.documentElement.classList.remove('lb-lock');
    img.removeAttribute('src');
    if (lastFocus) lastFocus.focus({ preventScroll: true });
  }

  function go(d) { if (group.length > 1) show(index + d); }

  function onKey(e) {
    if (!isOpen()) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') go(-1);
    else if (e.key === 'ArrowRight') go(1);
    else if (e.key === '+' || e.key === '=') { zoomAt(s * 1.5, innerWidth / 2, innerHeight / 2); apply(true); }
    else if (e.key === '-') { zoomAt(s / 1.5, innerWidth / 2, innerHeight / 2); apply(true); }
  }

  function onWheel(e) {
    e.preventDefault();
    zoomAt(s * Math.exp(-e.deltaY * 0.0015), e.clientX, e.clientY);
    apply();
  }

  function dist() {
    var k = Object.keys(ptrs), a = ptrs[k[0]], b = ptrs[k[1]];
    return Math.hypot(a.x - b.x, a.y - b.y);
  }
  function mid() {
    var k = Object.keys(ptrs), a = ptrs[k[0]], b = ptrs[k[1]];
    return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
  }

  function onDown(e) {
    if (e.target.closest('.lb-btn')) return;
    root.setPointerCapture(e.pointerId);
    ptrs[e.pointerId] = { x: e.clientX, y: e.clientY, sx: e.clientX, sy: e.clientY, onImg: e.target === img };
    var n = Object.keys(ptrs).length;
    if (n === 1) { moved = false; downAt = Date.now(); startT = { x: tx, y: ty }; }
    if (n === 2) { startDist = dist(); startScale = s; startMid = mid(); startT = { x: tx, y: ty }; moved = true; }
  }

  function onMove(e) {
    var p = ptrs[e.pointerId];
    if (!p) return;
    p.x = e.clientX; p.y = e.clientY;
    var n = Object.keys(ptrs).length;
    if (n >= 2) {
      var ns = startScale * (dist() / startDist);
      var m = mid();
      tx = startT.x + (m.x - startMid.x);
      ty = startT.y + (m.y - startMid.y);
      zoomAt(ns, m.x, m.y);
      apply();
    } else if (n === 1) {
      var dx = p.x - p.sx, dy = p.y - p.sy;
      if (Math.abs(dx) + Math.abs(dy) > 6) moved = true;
      if (s > 1) { tx = startT.x + dx; ty = startT.y + dy; clamp(); apply(); }
    }
  }

  function onUp(e) {
    var p = ptrs[e.pointerId];
    if (!p) return;
    var n = Object.keys(ptrs).length;
    delete ptrs[e.pointerId];
    if (n === 2) { // после щипка оставшийся палец продолжает перетаскивание
      var k = Object.keys(ptrs)[0];
      if (k) { ptrs[k].sx = ptrs[k].x; ptrs[k].sy = ptrs[k].y; startT = { x: tx, y: ty }; }
      if (s < 1.05) { s = 1; clamp(); apply(true); }
      return;
    }
    if (e.type === 'pointercancel') return;
    var dx = e.clientX - p.sx, dy = e.clientY - p.sy, quick = Date.now() - downAt < 350;
    // свайп по горизонтали в обычном масштабе — листаем
    if (s === 1 && quick && Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) { go(dx < 0 ? 1 : -1); return; }
    if (moved && Math.abs(dx) + Math.abs(dy) > 10) return;
    // тап
    var now = Date.now();
    if (now - lastTap.t < 320 && Math.hypot(e.clientX - lastTap.x, e.clientY - lastTap.y) < 40) {
      lastTap.t = 0;
      if (s > 1.02) { s = 1; tx = 0; ty = 0; }
      else zoomAt(2.5, e.clientX, e.clientY);
      apply(true);
      return;
    }
    lastTap = { t: now, x: e.clientX, y: e.clientY };
    if (!p.onImg && s === 1) close(); // тап по тёмному фону закрывает
  }

  thumbs.forEach(function (el) {
    el.setAttribute('tabindex', '0');
    el.setAttribute('role', 'button');
    el.addEventListener('click', function () { open(el); });
    el.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(el); }
    });
  });
})();
