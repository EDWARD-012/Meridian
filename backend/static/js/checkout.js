(function () {
  const useSaved = document.querySelector('input[name="use_saved"]');
  const newSection = document.getElementById('new-address-section');
  const savedList = document.getElementById('saved-address-list');
  const checkoutForm = document.getElementById('checkout-form');
  const submitBtn = document.getElementById('checkout-submit');

  function toggleAddressSections() {
    if (!useSaved || !newSection) return;
    const useSavedChecked = useSaved.checked;
    newSection.style.display = useSavedChecked ? 'none' : 'block';
    if (savedList) savedList.style.display = useSavedChecked ? 'block' : 'none';
    newSection.querySelectorAll('input, select, textarea').forEach(function (el) {
      el.disabled = useSavedChecked;
      el.required = !useSavedChecked;
    });
  }

  if (useSaved) {
    useSaved.addEventListener('change', toggleAddressSections);
    toggleAddressSections();
  }

  if (checkoutForm && submitBtn) {
    checkoutForm.addEventListener('submit', function () {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Placing order…';
    });
  }
})();
