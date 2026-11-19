/* Шкала и легенда уровня работы с ИИ.
   Данные: data/ai-levels.json. Разметка создаётся здесь, стили — assets/ai-levels.css. */
(function () {
  'use strict';

  var mounts = Array.prototype.slice.call(document.querySelectorAll('[data-ai-course]'));

  // Число мест берём из data-group-size, чтобы формулировку не править вручную.
  Array.prototype.forEach.call(document.querySelectorAll('[data-group-size]'), function (box) {
    var size = box.getAttribute('data-group-size');
    if (!size) return;
    var out = box.querySelector('[data-group-count]');
    if (out) out.textContent = size;
    else box.textContent = size;
  });

  if (!mounts.length) return;

  var data = null;
  var dialog = null;
  var lastTrigger = null;

  function esc(value) {
    return String(value).replace(/[&<>"']/g, function (ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
    });
  }

  function renderMount(mount) {
    var key = mount.getAttribute('data-ai-course');
    var course = data.courses[key];
    if (!course) return;

    var level = Number(course.level);
    var theme = mount.getAttribute('data-ai-theme') || 'light';
    var squares = '';
    for (var i = 1; i <= 5; i++) {
      squares += '<span class="ai-level-square' + (i <= level ? ' is-on' : '') + '" aria-hidden="true"></span>';
    }

    mount.innerHTML =
      '<div class="ai-level-box">' +
        '<div class="ai-level-head">' +
          '<p class="ai-level-title">Уровень овладения ИИ</p>' +
          '<button type="button" class="ai-level-help" data-ai-open aria-label="Что значат уровни">?</button>' +
        '</div>' +
        '<div class="ai-level-scale" role="img" aria-label="Уровень овладения ИИ: ' + level + ' из 5">' + squares + '</div>' +
      '</div>';

    mount.querySelector('[data-ai-open]').addEventListener('click', function () {
      openLegend(course, theme, this);
    });
  }

  function ensureDialog() {
    if (dialog) return dialog;

    dialog = document.createElement('dialog');
    dialog.className = 'ai-legend';
    dialog.setAttribute('aria-labelledby', 'aiLegendTitle');
    dialog.innerHTML =
      '<div class="ai-legend-top">' +
        '<div><p class="ai-legend-kicker">Уровни работы с ИИ</p><h2 id="aiLegendTitle">Что значат уровни</h2></div>' +
        '<button type="button" class="ai-legend-close" data-ai-close aria-label="Закрыть">×</button>' +
      '</div>' +
      '<div class="ai-legend-body">' +
        '<p class="ai-legend-sub" data-ai-sub></p>' +
        '<ol class="ai-legend-list" data-ai-list></ol>' +
      '</div>';

    document.body.appendChild(dialog);
    dialog.querySelector('[data-ai-close]').addEventListener('click', closeLegend);
    dialog.addEventListener('click', function (event) {
      if (event.target === dialog) closeLegend();
    });
    dialog.addEventListener('close', function () {
      document.documentElement.classList.remove('ai-legend-open');
      if (lastTrigger) lastTrigger.focus();
      lastTrigger = null;
    });
    return dialog;
  }

  function closeLegend() {
    if (dialog && dialog.open) dialog.close();
  }

  function openLegend(course, theme, trigger) {
    var view = ensureDialog();
    var level = Number(course.level);

    view.setAttribute('data-ai-theme', theme);
    view.querySelector('[data-ai-sub]').textContent =
      course.name + '. Уровень овладения ИИ.';

    var items = '';
    data.levels.forEach(function (item) {
      var current = Number(item.n) === level;
      items +=
        '<li class="ai-legend-item' + (current ? ' is-current' : '') + '"' + (current ? ' aria-current="true"' : '') + '>' +
          '<span class="ai-legend-num" aria-hidden="true">' + item.n + '</span>' +
          '<div class="ai-legend-text">' +
            '<h3>' + esc(item.title) + '</h3>' +
            '<p>' + esc(item.description) + '</p>' +
            (current ? '<span class="ai-legend-badge">Уровень этого курса</span>' : '') +
          '</div>' +
        '</li>';
    });
    view.querySelector('[data-ai-list]').innerHTML = items;

    lastTrigger = trigger;
    if (!view.open) {
      view.showModal();
      document.documentElement.classList.add('ai-legend-open');
    }
  }

  fetch(new URL('data/ai-levels.json', document.baseURI))
    .then(function (response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.json();
    })
    .then(function (json) {
      data = json;
      mounts.forEach(renderMount);
    })
    .catch(function (error) {
      if (window.console && console.error) console.error('Не удалось загрузить data/ai-levels.json', error);
    });
})();
