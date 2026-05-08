from catalog.models import Instrument


def get_most_viewed_products(limit=5):
    return (
        Instrument.objects.filter(is_active=True)
        .select_related("brand")
        .order_by("-views_count")[:limit]
    )


def get_zero_views_products():
    return (
        Instrument.objects.filter(is_active=True, views_count=0)
        .select_related("brand")
        .order_by("created_at")
    )


def get_analytics_overview():
    active_qs = Instrument.objects.filter(is_active=True)
    total = active_qs.count()
    with_views = active_qs.filter(views_count__gt=0).count()
    zero_views = total - with_views
    total_views = sum(active_qs.values_list("views_count", flat=True))
    return {
        "total": total,
        "with_views": with_views,
        "zero_views": zero_views,
        "total_views": total_views,
    }
