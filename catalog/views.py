from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Category, Instrument
from .services import get_most_viewed, increment_views


class InstrumentListView(ListView):
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        qs = (
            Instrument.objects.filter(is_active=True)
            .select_related("brand", "category")
            .prefetch_related("images")
        )
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(brand__name__icontains=q)
        sort = self.request.GET.get("sort", "")
        if sort == "price_asc":
            qs = qs.order_by("price")
        elif sort == "price_desc":
            qs = qs.order_by("-price")
        elif sort == "newest":
            qs = qs.order_by("-created_at")
        else:
            qs = qs.order_by("-views_count", "-created_at")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["sort"] = self.request.GET.get("sort", "")
        ctx["categories"] = Category.objects.filter(parent=None).prefetch_related("children")
        return ctx


class CategoryView(InstrumentListView):
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        descendant_ids = self._get_descendants(self.category)
        qs = (
            Instrument.objects.filter(is_active=True, category_id__in=descendant_ids)
            .select_related("brand", "category")
            .prefetch_related("images")
            .order_by("-views_count", "-created_at")
        )
        return qs

    def _get_descendants(self, category):
        ids = [category.pk]
        for child in category.children.all():
            ids.extend(self._get_descendants(child))
        return ids

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["current_category"] = self.category
        return ctx


class InstrumentDetailView(DetailView):
    model = Instrument
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    queryset = (
        Instrument.objects.filter(is_active=True)
        .select_related("brand", "category")
        .prefetch_related("images")
    )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        increment_views(obj)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["related"] = get_most_viewed(limit=4, exclude_pk=self.object.pk)
        ctx["images"] = list(self.object.images.all())
        return ctx
