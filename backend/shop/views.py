from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q, Count, Sum, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from catalog.models import Category, Product
from catalog.search import search_products, search_suggestions
from cart.models import CartItem
from cart.services import (
    get_cart_with_items,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    cart_subtotal,
    replace_cart_with_product,
    clamp_cart_to_stock,
)
from orders.models import Address, Order, Payment, OrderTracking
from orders.services import place_order, fail_razorpay_payment, confirm_razorpay_payment
from .forms import RegisterForm, AddressForm, CheckoutForm, ReviewForm, ProfileForm, ProfileAddressForm
from .utils import safe_redirect, parse_quantity, parse_cart_quantity
from cart.services import cart_item_count


def _wants_json(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _cart_payload(request, product=None, quantity=0, item_id=None, ok=True, message=""):
    data = {
        "ok": ok,
        "message": message,
        "cart_count": cart_item_count(request.user),
    }
    if product:
        data["product_id"] = product.id
        data["quantity"] = quantity
        data["item_id"] = item_id
        cart = get_cart_with_items(request.user)
        item = cart.items.filter(product_id=product.id).first()
        if item:
            data["item_id"] = item.id
            data["quantity"] = item.quantity
            data["available"] = max(0, product.stock_quantity - item.quantity)
        else:
            data["quantity"] = 0
            data["available"] = product.stock_quantity
    return data


def _annotate_products(qs):
    return qs.annotate(
        avg_rating=Avg("reviews__rating"),
        review_total=Count("reviews", distinct=True),
    )


def home(request):
    category_slug = request.GET.get("category", "")
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "featured")

    products = Product.objects.filter(is_active=True).select_related("category", "seller")
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = search_products(products, query)

    products = _annotate_products(products)
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "rating":
        products = products.order_by("-avg_rating", "-review_total")
    else:
        products = products.order_by("-created_at")

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.annotate(
        product_count=Count("products", filter=Q(products__is_active=True))
    )
    active_category_name = ""
    if category_slug:
        active_category_name = categories.filter(slug=category_slug).values_list("name", flat=True).first() or ""

    return render(request, "shop/home.html", {
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "categories": categories,
        "active_category": category_slug,
        "active_category_name": active_category_name,
        "query": query,
        "sort": sort,
    })


def search_suggest_api(request):
    """Live search suggestions from product & category DB tables."""
    q = request.GET.get("q", "").strip()
    return JsonResponse(search_suggestions(q))


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category", "seller").prefetch_related("images"),
        slug=slug,
        is_active=True,
    )
    gallery = list(product.images.all())
    reviews = product.reviews.select_related("user").all()
    rating_breakdown = {
        star: reviews.filter(rating=star).count() for star in range(5, 0, -1)
    }
    user_review = None
    review_form = ReviewForm()
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        if request.method == "POST" and "submit_review" in request.POST:
            if user_review:
                messages.warning(request, "You already reviewed this product.")
            else:
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    try:
                        review = review_form.save(commit=False)
                        review.product = product
                        review.user = request.user
                        review.verified_purchase = Order.objects.filter(
                            user=request.user, items__product=product
                        ).exists()
                        review.save()
                        messages.success(request, "Review submitted.")
                        return redirect("product_detail", slug=slug)
                    except IntegrityError:
                        messages.warning(request, "You already reviewed this product.")
        elif user_review:
            review_form = None

    related = _annotate_products(
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)
        .select_related("category")[:5]
    )

    return render(request, "shop/product_detail.html", {
        "product": product,
        "gallery": gallery,
        "reviews": reviews,
        "rating_breakdown": rating_breakdown,
        "star_list": [5, 4, 3, 2, 1],
        "review_form": review_form,
        "user_review": user_review,
        "related_products": related,
    })


@login_required
@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    quantity = parse_quantity(request.POST.get("quantity", 1))
    try:
        cart = add_to_cart(request.user, product.id, quantity)
        item = cart.items.filter(product_id=product.id).first()
        if _wants_json(request):
            return JsonResponse(_cart_payload(
                request, product, item.quantity if item else quantity,
                item.id if item else None, True, "Added to cart",
            ))
    except ValueError as e:
        if _wants_json(request):
            return JsonResponse({**_cart_payload(request, product, ok=False), "message": str(e)}, status=400)
        messages.error(request, str(e))
        return safe_redirect(request, request.POST.get("next"), "/")
    return safe_redirect(request, request.POST.get("next"), "/")


@login_required
@require_POST
def cart_update(request, item_id):
    quantity = parse_cart_quantity(request.POST.get("quantity", 1))
    cart = get_cart_with_items(request.user)
    item = cart.items.filter(pk=item_id).select_related("product").first()
    product = item.product if item else None
    if not item:
        if _wants_json(request):
            return JsonResponse({**_cart_payload(request, ok=False), "message": "Item not in cart"}, status=404)
        messages.error(request, "Item not found in your cart.")
        return redirect("cart")
    try:
        if quantity < 1:
            product = item.product
            product_id = product.id
            remove_from_cart(request.user, item_id)
            if _wants_json(request):
                return JsonResponse({
                    "ok": True,
                    "message": "Removed from cart",
                    "cart_count": cart_item_count(request.user),
                    "product_id": product_id,
                    "quantity": 0,
                    "item_id": None,
                    "available": product.stock_quantity,
                })
        else:
            cart = update_cart_item(request.user, item_id, quantity)
            item = cart.items.filter(pk=item_id).first()
            product = item.product if item else product
            if _wants_json(request) and product:
                return JsonResponse(_cart_payload(
                    request, product, item.quantity, item.id, True, "Updated",
                ))
    except ValueError as e:
        if _wants_json(request):
            return JsonResponse({**_cart_payload(request, product, ok=False), "message": str(e)}, status=400)
        messages.error(request, str(e))
        return safe_redirect(request, request.POST.get("next"), "/cart/")
    return safe_redirect(request, request.POST.get("next"), "/cart/")


@login_required
@require_POST
def cart_remove(request, item_id):
    cart = get_cart_with_items(request.user)
    item = cart.items.filter(pk=item_id).select_related("product").first()
    if not item:
        if _wants_json(request):
            return JsonResponse({**_cart_payload(request, ok=False), "message": "Item not in cart"}, status=404)
        return redirect("cart")
    product_id = item.product_id
    stock = item.product.stock_quantity
    remove_from_cart(request.user, item_id)
    if _wants_json(request):
        return JsonResponse({
            "ok": True,
            "message": "Removed from cart",
            "cart_count": cart_item_count(request.user),
            "product_id": product_id,
            "quantity": 0,
            "item_id": None,
            "available": stock,
        })
    return safe_redirect(request, request.POST.get("next"), "/cart/")


@login_required
def cart_view(request):
    clamp_cart_to_stock(request.user)
    cart = get_cart_with_items(request.user)
    return render(request, "shop/cart.html", {
        "cart": cart,
        "subtotal": cart_subtotal(cart),
    })


@login_required
def profile(request):
    from accounts.models import UserProfile

    UserProfile.objects.get_or_create(user=request.user)
    user = request.user
    profile_form = ProfileForm(instance=user)
    address_form = ProfileAddressForm()

    if request.method == "POST":
        if "save_profile" in request.POST:
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated.")
                return redirect("profile")
        elif "add_address" in request.POST:
            address_form = ProfileAddressForm(request.POST)
            if address_form.is_valid():
                with transaction.atomic():
                    addr = address_form.save(commit=False)
                    addr.user = user
                    if addr.is_default:
                        Address.objects.select_for_update().filter(user=user).update(is_default=False)
                    addr.save()
                messages.success(request, "Address saved.")
                return redirect("profile")

    addresses = Address.objects.filter(user=user)
    order_count = Order.objects.filter(user=user).count()
    return render(request, "shop/profile.html", {
        "profile_form": profile_form,
        "address_form": address_form,
        "addresses": addresses,
        "order_count": order_count,
        "cart_count_user": cart_item_count(user),
    })


@login_required
@require_POST
def buy_now(request, product_id):
    quantity = parse_quantity(request.POST.get("quantity", 1))
    try:
        replace_cart_with_product(request.user, product_id, quantity)
    except ValueError as e:
        messages.error(request, str(e))
        product = Product.objects.filter(pk=product_id).first()
        if product:
            return redirect("product_detail", slug=product.slug)
        return redirect("home")
    return redirect("checkout")


@login_required
def checkout(request):
    import secrets

    cart = get_cart_with_items(request.user)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("home")

    if request.method == "GET":
        request.session["checkout_token"] = secrets.token_hex(16)

    form = CheckoutForm(user=request.user)
    address_form = AddressForm()
    checkout_token = request.session.get("checkout_token", "")

    if request.method == "POST":
        posted_token = request.POST.get("checkout_token", "")
        if not posted_token or posted_token != request.session.get("checkout_token"):
            messages.error(request, "Checkout session expired or duplicate submit. Please try again.")
            return redirect("checkout")

        form = CheckoutForm(request.user, request.POST)
        address_form = AddressForm(request.POST)
        use_saved = request.POST.get("use_saved") == "on"

        if form.is_valid():
            try:
                if use_saved and form.cleaned_data.get("saved_address"):
                    address = form.cleaned_data["saved_address"]
                else:
                    if not address_form.is_valid():
                        messages.error(request, "Please enter a valid shipping address.")
                        return render(request, "shop/checkout.html", {
                            "cart": cart,
                            "subtotal": cart_subtotal(cart),
                            "form": form,
                            "address_form": address_form,
                            "checkout_token": request.session.get("checkout_token", ""),
                        })
                    address = address_form.save(commit=False)
                    address.user = request.user
                    address.is_default = True
                    with transaction.atomic():
                        Address.objects.select_for_update().filter(user=request.user).update(is_default=False)
                        address.save()

                order = place_order(
                    request.user,
                    address,
                    form.cleaned_data["payment_method"],
                )
                request.session.pop("checkout_token", None)
                if form.cleaned_data["payment_method"] == Payment.Method.RAZORPAY:
                    messages.info(request, "Complete payment via Razorpay demo.")
                    return redirect("razorpay_pay", order_id=order.id)
                messages.success(request, f"Order #{order.id} placed successfully.")
                return redirect("order_track", order_id=order.id)
            except ValueError as e:
                messages.error(request, str(e))

    return render(request, "shop/checkout.html", {
        "cart": cart,
        "subtotal": cart_subtotal(cart),
        "form": form,
        "address_form": address_form,
        "checkout_token": checkout_token,
    })


@login_required
def order_list(request):
    orders = (
        Order.objects.filter(user=request.user)
        .select_related("payment", "address")
        .prefetch_related("items__product")
        .order_by("-order_date")
    )
    return render(request, "shop/orders.html", {"orders": orders})


@login_required
def order_track(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product", "tracking_events", "payment", "address"),
        pk=order_id,
        user=request.user,
    )
    status_steps = [
        ("pending", "Ordered"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for delivery"),
        ("delivered", "Delivered"),
    ]
    current_idx = next(
        (i for i, (code, _) in enumerate(status_steps) if code == order.status),
        0,
    )
    if order.status == Order.Status.CANCELLED:
        current_idx = -1

    show_pay_now = (
        order.payment.payment_method == Payment.Method.RAZORPAY
        and order.payment.status == Payment.Status.PENDING
        and order.status == Order.Status.PENDING
    )
    return render(request, "shop/order_track.html", {
        "order": order,
        "status_steps": status_steps,
        "current_step": current_idx,
        "show_pay_now": show_pay_now,
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. Welcome!")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = "home"


@login_required
def razorpay_pay(request, order_id):
    from datetime import timedelta
    from django.utils import timezone
    from orders.services import cancel_stale_razorpay_order

    order = get_object_or_404(
        Order.objects.select_related("payment").prefetch_related("items"),
        pk=order_id,
        user=request.user,
    )
    payment = order.payment
    if payment.payment_method != Payment.Method.RAZORPAY:
        return redirect("order_track", order_id=order.id)
    if payment.status == Payment.Status.SUCCESS:
        return redirect("order_track", order_id=order.id)
    if order.status == Order.Status.CANCELLED or payment.status == Payment.Status.FAILED:
        messages.error(request, "This order was cancelled. Please place a new order.")
        return redirect("order_track", order_id=order.id)

    stale_cutoff = timezone.now() - timedelta(minutes=60)
    if order.order_date < stale_cutoff and payment.status == Payment.Status.PENDING:
        cancel_stale_razorpay_order(order)
        messages.warning(request, "Payment window expired. Order cancelled and stock restored.")
        return redirect("order_track", order_id=order.id)

    return render(request, "shop/razorpay_pay.html", {
        "order": order,
        "item_count": order.items.count(),
    })


@login_required
@require_POST
def razorpay_confirm(request, order_id):
    from django.urls import reverse

    order = get_object_or_404(
        Order.objects.select_related("payment"),
        pk=order_id,
        user=request.user,
    )
    payment = order.payment
    wants_json = request.headers.get("Accept") == "application/json"

    if payment.payment_method != Payment.Method.RAZORPAY:
        if wants_json:
            return JsonResponse({"success": False, "message": "Invalid payment method"})
        return redirect("order_track", order_id=order.id)

    action = request.POST.get("action", "pay")
    if action == "fail":
        fail_razorpay_payment(order)
        if wants_json:
            return JsonResponse({
                "success": False,
                "message": "Payment declined by bank (demo)",
                "redirect_url": reverse("order_track", args=[order.id]),
            })
        messages.error(request, "Payment failed. Order cancelled and stock restored.")
        return redirect("order_track", order_id=order.id)

    if payment.status == Payment.Status.SUCCESS:
        if wants_json:
            return JsonResponse({
                "success": True,
                "transaction_id": payment.transaction_id,
                "redirect_url": reverse("order_track", args=[order.id]),
            })
        return redirect("order_track", order_id=order.id)

    try:
        payment = confirm_razorpay_payment(order)
    except ValueError as e:
        if wants_json:
            return JsonResponse({"success": False, "message": str(e)})
        messages.error(request, str(e))
        return redirect("order_track", order_id=order.id)

    if wants_json:
        return JsonResponse({
            "success": True,
            "transaction_id": payment.transaction_id,
            "redirect_url": reverse("order_track", args=[order.id]),
        })
    messages.success(request, f"Payment successful! Txn: {payment.transaction_id}")
    return redirect("order_track", order_id=order.id)


@user_passes_test(lambda u: u.is_staff)
def db_insights(request):
    from shop.db_insights import build_insights_context
    return render(request, "shop/db_insights.html", build_insights_context())

