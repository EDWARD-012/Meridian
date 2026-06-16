from django.urls import path
from .views import CartView, CartItemAddView, CartItemUpdateView, CartItemRemoveView, CartClearView

urlpatterns = [
    path("", CartView.as_view(), name="cart-detail"),
    path("items/", CartItemAddView.as_view(), name="cart-add"),
    path("items/<int:item_id>/", CartItemUpdateView.as_view(), name="cart-update"),
    path("items/<int:item_id>/remove/", CartItemRemoveView.as_view(), name="cart-remove"),
    path("clear/", CartClearView.as_view(), name="cart-clear"),
]
