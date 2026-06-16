(function () {
  "use strict";

  var cfg = window.RZP;
  if (!cfg) return;

  var SCREENS = {
    checkout: document.getElementById("screen-checkout"),
    processing: document.getElementById("screen-processing"),
    success: document.getElementById("screen-success"),
    failed: document.getElementById("screen-failed"),
  };

  var amountBar = document.getElementById("amount-bar");
  var btnPay = document.getElementById("btn-pay");
  var btnRetry = document.getElementById("btn-retry");
  var btnClose = document.getElementById("btn-close");
  var tabLine = document.getElementById("tab-line");
  var procHeading = document.getElementById("proc-heading");
  var procText = document.getElementById("proc-text");
  var procFill = document.getElementById("proc-fill");

  var activeTab = "upi";
  var paying = false;

  /* ── Screen switcher (only ONE visible) ── */
  function showScreen(name) {
    Object.keys(SCREENS).forEach(function (key) {
      var el = SCREENS[key];
      if (el) el.classList.toggle("screen-active", key === name);
    });
    /* hide amount bar + tabs during processing/success/fail */
    if (amountBar) {
      amountBar.style.display = (name === "checkout") ? "" : "none";
    }
  }

  /* ── Tabs ── */
  function moveTabLine(tab) {
    if (!tabLine || !tab) return;
    tabLine.style.left = tab.offsetLeft + "px";
    tabLine.style.width = tab.offsetWidth + "px";
  }

  document.querySelectorAll(".tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      activeTab = tab.dataset.tab;
      document.querySelectorAll(".tab").forEach(function (t) { t.classList.remove("tab-active"); });
      document.querySelectorAll(".panel").forEach(function (p) { p.classList.remove("panel-active"); });
      tab.classList.add("tab-active");
      var panel = document.getElementById("panel-" + activeTab);
      if (panel) panel.classList.add("panel-active");
      moveTabLine(tab);
    });
  });

  var firstTab = document.querySelector(".tab.tab-active");
  requestAnimationFrame(function () { moveTabLine(firstTab); });
  window.addEventListener("resize", function () {
    moveTabLine(document.querySelector(".tab.tab-active"));
  });

  /* ── UPI verify ── */
  var upiInput = document.getElementById("upi-id");
  var upiVerify = document.getElementById("upi-verify");
  var upiStatus = document.getElementById("upi-status");

  if (upiVerify) {
    upiVerify.addEventListener("click", function () {
      var val = upiInput ? upiInput.value.trim() : "";
      if (!val || val.indexOf("@") === -1) {
        if (upiStatus) { upiStatus.textContent = "Enter a valid UPI ID"; upiStatus.style.color = "#e74c3c"; }
        return;
      }
      upiVerify.textContent = "Verified";
      upiVerify.classList.add("verified");
      if (upiStatus) { upiStatus.textContent = val + " is verified"; upiStatus.style.color = "#27ae60"; }
    });
  }

  /* ── App / bank / wallet selection ── */
  function selectOne(selector, btn) {
    document.querySelectorAll(selector).forEach(function (b) { b.classList.remove("selected"); });
    btn.classList.add("selected");
  }
  document.querySelectorAll(".app-btn").forEach(function (b) {
    b.addEventListener("click", function () { selectOne(".app-btn", b); });
  });
  document.querySelectorAll(".bank-btn").forEach(function (b) {
    b.addEventListener("click", function () { selectOne(".bank-btn", b); });
  });
  document.querySelectorAll(".wallet-btn").forEach(function (b) {
    b.addEventListener("click", function () { selectOne(".wallet-btn", b); });
  });

  /* ── Card formatting ── */
  var cardNum = document.getElementById("card-num");
  if (cardNum) {
    cardNum.addEventListener("input", function () {
      var v = cardNum.value.replace(/\D/g, "").slice(0, 16);
      cardNum.value = v.replace(/(.{4})/g, "$1 ").trim();
    });
  }
  var cardExp = document.getElementById("card-exp");
  if (cardExp) {
    cardExp.addEventListener("input", function () {
      var v = cardExp.value.replace(/\D/g, "").slice(0, 4);
      cardExp.value = v.length >= 2 ? v.slice(0, 2) + " / " + v.slice(2) : v;
    });
  }

  /* ── Fail conditions ── */
  function shouldFail() {
    if (activeTab === "upi" && upiInput && upiInput.value.trim().toLowerCase() === "fail@upi") return true;
    var cvv = document.getElementById("card-cvv");
    if (activeTab === "card" && cvv && cvv.value === "000") return true;
    return false;
  }

  /* ── Progress animation ── */
  function runProgress(ms, cb) {
    var start = Date.now();
    var steps = [
      { pct: 0,  h: "Processing payment", t: "Please do not press back or refresh this page" },
      { pct: 30, h: "Authenticating", t: "Connecting securely to your bank…" },
      { pct: 60, h: "Confirming", t: "Verifying transaction details…" },
      { pct: 85, h: "Almost done", t: "Finalizing your payment…" },
    ];
    function tick() {
      var elapsed = Date.now() - start;
      var pct = Math.min(100, (elapsed / ms) * 100);
      if (procFill) procFill.style.width = pct + "%";
      steps.forEach(function (s) { if (pct >= s.pct) { if (procHeading) procHeading.textContent = s.h; if (procText) procText.textContent = s.t; } });
      if (elapsed < ms) requestAnimationFrame(tick);
      else if (cb) cb();
    }
    requestAnimationFrame(tick);
  }

  function submitPayment(action) {
    return fetch(cfg.confirmUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "X-CSRFToken": cfg.csrfToken,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: "action=" + encodeURIComponent(action) +
            "&method_used=" + encodeURIComponent(activeTab) +
            "&csrfmiddlewaretoken=" + encodeURIComponent(cfg.csrfToken),
    }).then(function (r) { return r.json(); });
  }

  function startPayment() {
    if (paying) return;
    paying = true;
    if (btnPay) btnPay.disabled = true;

    var fail = shouldFail();
    showScreen("processing");
    if (procFill) procFill.style.width = "0%";

    runProgress(fail ? 2400 : 3000, function () {
      submitPayment(fail ? "fail" : "pay")
        .then(function (data) {
          if (data.success) {
            showScreen("success");
            var el = document.getElementById("success-txn");
            if (el) el.textContent = "Payment ID: " + (data.transaction_id || "—");
            setTimeout(function () {
              window.location.href = data.redirect_url || cfg.redirectUrl;
            }, 2000);
          } else {
            showScreen("failed");
            var msg = document.getElementById("fail-msg");
            if (msg) msg.textContent = data.message || "Your payment could not be completed";
            paying = false;
            if (btnPay) btnPay.disabled = false;
          }
        })
        .catch(function () {
          showScreen("failed");
          var msg = document.getElementById("fail-msg");
          if (msg) msg.textContent = "Network error. Please try again.";
          paying = false;
          if (btnPay) btnPay.disabled = false;
        });
    });
  }

  if (btnPay) btnPay.addEventListener("click", startPayment);

  if (btnRetry) {
    btnRetry.addEventListener("click", function () {
      paying = false;
      if (btnPay) btnPay.disabled = false;
      if (procFill) procFill.style.width = "0%";
      showScreen("checkout");
    });
  }

  if (btnClose) {
    btnClose.addEventListener("click", function () {
      if (confirm("Cancel this payment?")) {
        window.location.href = cfg.redirectUrl;
      }
    });
  }

  /* Ensure only checkout visible on load */
  showScreen("checkout");
})();
