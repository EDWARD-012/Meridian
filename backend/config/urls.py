from django.contrib import admin
from django.urls import path, include
from shop.urls import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check),
    path("", include("shop.urls")),
]
