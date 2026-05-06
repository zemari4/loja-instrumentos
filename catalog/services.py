from django.db.models import QuerySet

from .models import Instrument


def get_featured_products(limit: int = 6) -> QuerySet:
    return (
        Instrument.objects.filter(is_active=True, is_featured=True)
        .select_related("brand", "category")
        .prefetch_related("images")
        .order_by("-views_count", "-created_at")[:limit]
    )


def get_most_viewed(limit: int = 6) -> QuerySet:
    return (
        Instrument.objects.filter(is_active=True)
        .select_related("brand", "category")
        .prefetch_related("images")
        .order_by("-views_count")[:limit]
    )


def increment_views(instrument: Instrument) -> None:
    Instrument.objects.filter(pk=instrument.pk).update(views_count=instrument.views_count + 1)
