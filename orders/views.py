from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import ListView, View

from cart.services import get_cart
from orders.forms import CheckoutForm
from orders.models import Order
from orders.services import OutOfStockError, create_order_from_cart, get_order_detail, get_user_orders


class _OrderOwnerMixin(LoginRequiredMixin, View):
    template_name = ""

    def get(self, request, pk):
        try:
            order = get_order_detail(request.user, pk)
        except Order.DoesNotExist:
            raise Http404
        return render(request, self.template_name, {"order": order})


class CheckoutView(LoginRequiredMixin, View):
    template_name = "orders/checkout.html"

    def _render(self, request, form, cart):
        return render(request, self.template_name, {
            "form": form,
            "cart_items": cart,
            "total": sum(item["subtotal"] for item in cart),
        })

    def _get_cart(self, request):
        cart = get_cart(request.session)
        if not cart:
            messages.error(request, "Seu carrinho está vazio.")
            return None
        return cart

    def get(self, request):
        cart = self._get_cart(request)
        if cart is None:
            return redirect("cart:cart")
        return self._render(request, CheckoutForm(), cart)

    def post(self, request):
        cart = self._get_cart(request)
        if cart is None:
            return redirect("cart:cart")
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return self._render(request, form, cart)
        try:
            order = create_order_from_cart(request.user, request.session, form.address_data())
        except OutOfStockError as e:
            messages.error(request, str(e))
            return self._render(request, form, cart)
        return redirect("orders:order_confirm", pk=order.pk)


class OrderConfirmView(_OrderOwnerMixin):
    template_name = "orders/order_confirm.html"


class OrderListView(LoginRequiredMixin, ListView):
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return get_user_orders(self.request.user)


class OrderDetailView(_OrderOwnerMixin):
    template_name = "orders/order_detail.html"
