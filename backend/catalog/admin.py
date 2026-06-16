from django.contrib import admin
from .models import Category, Product, Seller, Review, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("name", "rating", "total_sales", "verified", "city")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "seller", "price", "stock_quantity", "is_active")
    list_filter = ("category", "seller", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "title", "verified_purchase", "created_at")
    list_filter = ("rating", "verified_purchase")
