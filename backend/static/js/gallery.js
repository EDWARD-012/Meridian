(function () {
  var main = document.getElementById('gallery-main-img');
  var thumbs = document.querySelectorAll('.gallery-thumb');
  if (!main || !thumbs.length) return;

  thumbs.forEach(function (btn) {
    btn.addEventListener('click', function () {
      main.src = btn.dataset.src;
      main.alt = btn.dataset.alt || '';
      thumbs.forEach(function (t) { t.classList.remove('active'); });
      btn.classList.add('active');
    });
  });
})();
