(function () {
  "use strict";

  var toastBox = document.getElementById("toast");
  var toastTimer = null;
  var inFlight = false;

  function getCsrf() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) return meta.content;
    var el = document.querySelector("[name=csrfmiddlewaretoken]");
    return el ? el.value : "";
  }

  function showToast(msg, type) {
    if (!toastBox) return;
    toastBox.textContent = msg;
    toastBox.className = "toast toast-" + (type || "ok");
    toastBox.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastBox.hidden = true; }, 2200);
  }

  function updateCartBadge(count) {
    var badge = document.querySelector(".amz-cart-count");
    if (count > 0) {
      if (!badge) {
        var cart = document.querySelector(".amz-cart");
        if (cart) {
          badge = document.createElement("span");
          badge.className = "amz-cart-count";
          cart.appendChild(badge);
        }
      }
      if (badge) badge.textContent = count;
    } else if (badge) {
      badge.remove();
    }
  }

  function qtyControlsHtml(data) {
    var pid = data.product_id;
    var qty = data.quantity;
    var iid = data.item_id;
    var avail = data.available;
    var minus = qty - 1;
    var plus = qty + 1;
    var plusDisabled = avail <= 0 ? " disabled" : "";
    return (
      '<div class="card-qty js-cart-slot">' +
      '<form class="qty-inline js-cart-form" data-action="update" data-item-id="' + iid + '" data-product-id="' + pid + '">' +
      '<button type="submit" name="quantity" value="' + minus + '" class="btn btn-outline btn-sm">−</button>' +
      '<span class="qty-num">' + qty + ' in cart</span>' +
      '<button type="submit" name="quantity" value="' + plus + '" class="btn btn-outline btn-sm"' + plusDisabled + '>+</button>' +
      '</form></div>'
    );
  }

  function addButtonHtml(productId) {
    return (
      '<form class="card-action js-cart-form" data-action="add" data-product-id="' + productId + '">' +
      '<button type="submit" class="btn btn-amz-yellow btn-sm" style="width:100%">Add to cart</button></form>'
    );
  }

  function swapCardControls(productId, data) {
    var card = document.querySelector('[data-product-id="' + productId + '"]');
    if (!card) return;
    var slot = card.querySelector(".js-cart-slot") || card.querySelector(".card-action") || card.querySelector(".card-qty");
    if (!slot) {
      slot = document.createElement("div");
      var body = card.querySelector(".card-body");
      if (body) body.appendChild(slot);
    }
    if (data.quantity > 0 && data.item_id) {
      slot.outerHTML = qtyControlsHtml(data);
    } else {
      slot.outerHTML = addButtonHtml(productId);
    }
  }

  function updateBuybox(data) {
    var box = document.getElementById("buybox-cart");
    if (!box) return;
    if (data.quantity > 0 && data.item_id) {
      box.innerHTML =
        '<div class="buybox-in-cart">✓ ' + data.quantity + ' in cart</div>' +
        '<form class="qty-inline js-cart-form buybox-qty" data-action="update" data-item-id="' + data.item_id + '" data-product-id="' + data.product_id + '">' +
        '<button type="submit" name="quantity" value="' + (data.quantity - 1) + '" class="btn btn-outline btn-sm">−</button>' +
        '<span class="qty-num">' + data.quantity + '</span>' +
        '<button type="submit" name="quantity" value="' + (data.quantity + 1) + '" class="btn btn-outline btn-sm"' + (data.available <= 0 ? " disabled" : "") + '>+</button>' +
        '</form>';
    } else {
      box.innerHTML =
        '<form class="js-cart-form" data-action="add" data-product-id="' + data.product_id + '">' +
        '<button type="submit" class="btn btn-amz-yellow" style="width:100%;margin-bottom:0.5rem">Add to Cart</button></form>';
    }
  }

  function postCart(url, body) {
    return fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCsrf(),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: body,
    }).then(function (r) {
      return r.json().then(function (d) {
        return { ok: r.ok, data: d };
      }).catch(function () {
        return { ok: false, data: { message: "Unexpected server response" } };
      });
    });
  }

  function handleSubmit(e) {
    var form = e.target.closest(".js-cart-form");
    if (!form) return;
    e.preventDefault();
    if (inFlight) return;

    var btn = e.submitter || form.querySelector('button[type="submit"]');
    inFlight = true;
    if (btn) btn.disabled = true;
    form.querySelectorAll("button[type=submit]").forEach(function (b) { b.disabled = true; });

    var action = form.dataset.action;
    var productId = form.dataset.productId;
    var itemId = form.dataset.itemId;
    var qty = btn && btn.name === "quantity" ? btn.value : "1";

    var url, body;
    var csrf = getCsrf();
    if (action === "add") {
      url = "/cart/add/" + productId + "/";
      body = "quantity=1&csrfmiddlewaretoken=" + encodeURIComponent(csrf);
    } else {
      url = "/cart/update/" + itemId + "/";
      body = "quantity=" + encodeURIComponent(qty) + "&csrfmiddlewaretoken=" + encodeURIComponent(csrf);
    }

    postCart(url, body).then(function (res) {
      inFlight = false;
      form.querySelectorAll("button[type=submit]").forEach(function (b) { b.disabled = false; });
      if (!res.ok || !res.data.ok) {
        showToast(res.data.message || "Could not update cart", "err");
        return;
      }
      var d = res.data;
      updateCartBadge(d.cart_count);
      if (action === "add") showToast("Added to cart", "ok");
      swapCardControls(d.product_id, d);
      updateBuybox(d);
    }).catch(function () {
      inFlight = false;
      form.querySelectorAll("button[type=submit]").forEach(function (b) { b.disabled = false; });
      showToast("Network error", "err");
    });
  }

  document.addEventListener("submit", function (e) {
    if (e.target.closest(".js-cart-form")) handleSubmit(e);
  });
})();
