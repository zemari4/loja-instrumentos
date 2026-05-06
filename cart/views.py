from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from catalog.models import Instrument

from . import services


class CartView(View):
    def get(self, request):
        items = services.get_cart(request.session)
        total = services.cart_total(request.session)
        return render(request, "cart/cart.html", {"items": items, "total": total})


class AddToCartView(View):
    def post(self, request, pk):
        get_object_or_404(Instrument, pk=pk, is_active=True)
        try:
            qty = max(1, int(request.POST.get("qty", 1)))
        except (ValueError, TypeError):
            qty = 1
        services.add_item(request.session, pk, qty)
        messages.success(request, "Produto adicionado ao carrinho.")
        next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
        return redirect(next_url)


class RemoveFromCartView(View):
    def post(self, request, pk):
        services.remove_item(request.session, pk)
        messages.info(request, "Produto removido do carrinho.")
        return redirect("cart:cart")


class UpdateCartView(View):
    def post(self, request, pk):
        try:
            qty = int(request.POST.get("qty", 1))
        except (ValueError, TypeError):
            qty = 1
        services.update_item(request.session, pk, qty)
        return redirect("cart:cart")
