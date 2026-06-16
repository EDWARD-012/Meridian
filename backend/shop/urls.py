from django.urls import path
from django.http import JsonResponse
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/suggest/", views.search_suggest_api, name="search_suggest"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:item_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    path("profile/", views.profile, name="profile"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_list, name="orders"),
    path("orders/<int:order_id>/track/", views.order_track, name="order_track"),
    path("register/", views.register_view, name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("payment/razorpay/<int:order_id>/", views.razorpay_pay, name="razorpay_pay"),
    path("payment/razorpay/<int:order_id>/confirm/", views.razorpay_confirm, name="razorpay_confirm"),
    path("db-insights/", views.db_insights, name="db_insights"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
]


def health_check(_request):
    import logging
    from django.db import connection

    logger = logging.getLogger(__name__)
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception:
        logger.exception("Health check database failure")
        return JsonResponse({"status": "error"}, status=503)
