from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.views.generic import ListView

from backstage.mixins import BackstagePermissionMixin


class CustomerListView(BackstagePermissionMixin, ListView):
    template_name = "backstage/customers/list.html"
    context_object_name = "customers"
    paginate_by = 25

    def get_queryset(self):
        search = self.request.GET.get("q", "").strip()
        qs = (
            User.objects.annotate(
                order_count=Count("orders"),
                total_spent=Sum("orders__total_price"),
            )
            .filter(order_count__gt=0)
            .order_by("-order_count")
        )
        if search:
            qs = qs.filter(
                Q(username__icontains=search) | Q(email__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search"] = self.request.GET.get("q", "")
        return ctx
