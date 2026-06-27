from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from manager.mixins import BackstagePermissionMixin
from orders.models import Order


class OrderListView(BackstagePermissionMixin, ListView):
    template_name = "manager/orders/list.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        qs = Order.objects.select_related("customer").order_by("-created_at")
        status = self.request.GET.get("status")
        if status and status in dict(Order.STATUS_CHOICES):
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Order.STATUS_CHOICES
        ctx["selected_status"] = self.request.GET.get("status", "")
        return ctx


class OrderDetailView(BackstagePermissionMixin, DetailView):
    template_name = "manager/orders/detail.html"
    context_object_name = "order"
    queryset = Order.objects.select_related("customer").prefetch_related(
        "items__instrument__brand", "items__instrument__images"
    )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Order.STATUS_CHOICES
        try:
            ctx["payment"] = self.object.payment
        except Exception:
            ctx["payment"] = None
        ctx["history"] = self.object.history.all().order_by("-history_date")[:10]
        return ctx


class UpdateOrderStatusView(BackstagePermissionMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get("status")
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=["status", "updated_at"])
            messages.success(request, "Status do pedido atualizado.")
        else:
            messages.error(request, "Status inválido.")
        return redirect("manager:order_detail", pk=pk)
