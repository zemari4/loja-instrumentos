from django.views.generic import TemplateView

from manager.mixins import BackstagePermissionMixin
from dashboard.services import analytics as analytics_svc


class AnalyticsView(BackstagePermissionMixin, TemplateView):
    template_name = "manager/analytics/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["overview"] = analytics_svc.get_analytics_overview()
        ctx["most_viewed"] = analytics_svc.get_most_viewed_products(limit=20)
        ctx["zero_views"] = analytics_svc.get_zero_views_products()
        return ctx
