/* AI proficiency scale and legend.
   Data: data/ai-levels-en.json. Markup is generated here, styles live in assets/ai-levels.css. */
(function () {
  'use strict';

  var mounts = Array.prototype.slice.call(document.querySelectorAll('[data-ai-course]'));
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
    var result = data.results[String(level)] || '';
    if (!result) {
      var levelInfo = data.levels.filter(function (item) { return Number(item.n) === level; })[0];
      if (levelInfo) result = levelInfo.description.charAt(0).toUpperCase() + levelInfo.description.slice(1);
    }
    var squares = '';
    for (var i = 1; i <= 5; i++) {
      squares += '<span class="ai-level-square' + (i <= level ? ' is-on' : '') + '" aria-hidden="true"></span>';
    }

    mount.innerHTML =
      '<div class="ai-level-box">' +
        '<p class="ai-level-title">AI proficiency level after the course: <b>' + level + ' of 5</b></p>' +
        '<div class="ai-level-scale" aria-hidden="true">' + squares + '</div>' +
        '<p class="ai-level-result">' + esc(result) + '</p>' +
        '<p class="ai-level-entry"><b>Entry requirements:</b> ' + esc(data.entry) + '</p>' +
        '<button type="button" class="ai-level-open" data-ai-open>What the levels mean</button>' +
      '</div>';

    mount.setAttribute('role', 'group');
    mount.setAttribute('aria-label', 'Level ' + level + ' of 5');

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
        '<div><p class="ai-legend-kicker">AI proficiency levels</p><h2 id="aiLegendTitle">What the levels mean</h2></div>' +
        '<button type="button" class="ai-legend-close" data-ai-close aria-label="Close">×</button>' +
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
      course.name + '. AI proficiency level after the course: ' + level + ' of 5';

    var items = '';
    data.levels.forEach(function (item) {
      var current = Number(item.n) === level;
      items +=
        '<li class="ai-legend-item' + (current ? ' is-current' : '') + '"' + (current ? ' aria-current="true"' : '') + '>' +
          '<span class="ai-legend-num" aria-hidden="true">' + item.n + '</span>' +
          '<div class="ai-legend-text">' +
            '<h3>' + esc(item.title) + '</h3>' +
            '<p>' + esc(item.description) + '</p>' +
            (current ? '<span class="ai-legend-badge">This course\'s level</span>' : '') +
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

  fetch(new URL('../data/ai-levels-en.json', document.currentScript.src))
    .then(function (response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.json();
    })
    .then(function (json) {
      data = json;
      mounts.forEach(renderMount);
    })
    .catch(function (error) {
      if (window.console && console.error) console.error('Could not load data/ai-levels-en.json', error);
    });
})();
