from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from catalog.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart = get_or_create_cart(request.user)
        cart = Cart.objects.prefetch_related(
            "items__product__category"
        ).get(pk=cart.pk)
        return Response(CartSerializer(cart).data)


class CartItemAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        if quantity < 1:
            return Response({"detail": "Quantity must be at least 1."}, status=400)

        product = get_object_or_404(Product, pk=product_id, is_active=True)
        if product.stock_quantity < quantity:
            return Response(
                {"detail": f"Only {product.stock_quantity} units available."},
                status=400,
            )

        cart = get_or_create_cart(request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )
        if not created:
            new_qty = item.quantity + quantity
            if new_qty > product.stock_quantity:
                return Response(
                    {"detail": f"Cannot add more than {product.stock_quantity} units."},
                    status=400,
                )
            item.quantity = new_qty
            item.save()

        cart = Cart.objects.prefetch_related("items__product__category").get(pk=cart.pk)
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, item_id):
        cart = get_or_create_cart(request.user)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        quantity = int(request.data.get("quantity", item.quantity))
        if quantity < 1:
            return Response({"detail": "Quantity must be at least 1."}, status=400)
        if quantity > item.product.stock_quantity:
            return Response(
                {"detail": f"Only {item.product.stock_quantity} units available."},
                status=400,
            )
        item.quantity = quantity
        item.save()
        cart = Cart.objects.prefetch_related("items__product__category").get(pk=cart.pk)
        return Response(CartSerializer(cart).data)


class CartItemRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        cart = get_or_create_cart(request.user)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        cart = Cart.objects.prefetch_related("items__product__category").get(pk=cart.pk)
        return Response(CartSerializer(cart).data)


class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart = get_or_create_cart(request.user)
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)
