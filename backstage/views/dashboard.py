from django.views.generic import TemplateView

from backstage.mixins import BackstagePermissionMixin
from dashboard.services import analytics as analytics_svc
from dashboard.services import inventory as inventory_svc
from dashboard.services import orders as orders_svc


class DashboardView(BackstagePermissionMixin, TemplateView):
    template_name = "backstage/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order_kpis = orders_svc.get_order_kpis()
        inventory_kpis = inventory_svc.get_inventory_kpis()
        ctx.update(order_kpis)
        ctx["low_stock_count"] = inventory_kpis["low_stock"]
        return ctx


class RecentOrdersTableView(BackstagePermissionMixin, TemplateView):
    template_name = "backstage/partials/recent_orders_table.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orders"] = orders_svc.get_recent_orders(limit=10)
        return ctx


class TopProductsTableView(BackstagePermissionMixin, TemplateView):
    template_name = "backstage/partials/top_products_table.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["top_products"] = orders_svc.get_top_sold_products(limit=5)
        return ctx


class MostViewedTableView(BackstagePermissionMixin, TemplateView):
    template_name = "backstage/partials/most_viewed_table.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["most_viewed"] = analytics_svc.get_most_viewed_products(limit=5)
        return ctx
