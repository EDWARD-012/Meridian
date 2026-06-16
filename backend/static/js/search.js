(function () {
  const input = document.getElementById('search-input');
  const box = document.getElementById('search-suggestions');
  if (!input || !box) return;

  const url = input.dataset.suggestUrl;
  let timer = null;
  let controller = null;

  function hide() {
    box.hidden = true;
    box.innerHTML = '';
  }

  function show(html) {
    box.innerHTML = html;
    box.hidden = !html;
  }

  function render(data) {
    if (!data.categories.length && !data.products.length) {
      show('<div class="suggest-empty">No matches in database</div>');
      return;
    }

    let html = '';

    if (data.categories.length) {
      html += '<div class="suggest-group"><div class="suggest-label">Categories (DB)</div>';
      data.categories.forEach(function (c) {
        html += '<a class="suggest-item suggest-cat" href="' + c.url + '">'
          + '<span>' + escapeHtml(c.name) + '</span>'
          + '<span class="suggest-meta">' + c.product_count + ' products</span></a>';
      });
      html += '</div>';
    }

    if (data.products.length) {
      html += '<div class="suggest-group"><div class="suggest-label">Products (DB)</div>';
      data.products.forEach(function (p) {
        html += '<a class="suggest-item" href="' + p.url + '">'
          + '<img src="' + escapeHtml(p.image_url) + '" alt="">'
          + '<div><strong>' + escapeHtml(p.name) + '</strong>'
          + '<span class="suggest-meta">' + escapeHtml(p.category) + ' · ₹' + Math.round(p.price) + '</span></div></a>';
      });
      html += '</div>';
    }

    show(html);
  }

  function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function fetchSuggestions(q) {
    if (controller) controller.abort();
    if (q.length < 2) { hide(); return; }

    controller = new AbortController();
    fetch(url + '?q=' + encodeURIComponent(q), { signal: controller.signal })
      .then(function (r) { return r.json(); })
      .then(render)
      .catch(function () {});
  }

  input.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () { fetchSuggestions(input.value.trim()); }, 220);
  });

  input.addEventListener('focus', function () {
    if (input.value.trim().length >= 2) fetchSuggestions(input.value.trim());
  });

  document.addEventListener('click', function (e) {
    if (!box.contains(e.target) && e.target !== input) hide();
  });

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') hide();
  });
})();
