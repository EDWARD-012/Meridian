from django.urls import path
from .views import (
    AddressListCreateView,
    PlaceOrderView,
    OrderListView,
    OrderDetailView,
    OrderTrackView,
)

urlpatterns = [
    path("addresses/", AddressListCreateView.as_view(), name="address-list"),
    path("place/", PlaceOrderView.as_view(), name="place-order"),
    path("", OrderListView.as_view(), name="order-list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<int:order_id>/track/", OrderTrackView.as_view(), name="order-track"),
]
