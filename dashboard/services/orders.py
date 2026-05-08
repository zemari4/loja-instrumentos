from decimal import Decimal

from django.db.models import Avg, Count, Sum

from orders.models import Order, OrderItem


def get_order_kpis():
    total = Order.objects.count()
    paid = Order.objects.filter(status=Order.STATUS_PAID).count()
    cancelled = Order.objects.filter(status=Order.STATUS_CANCELLED).count()

    completed_qs = Order.objects.filter(status__in=[Order.STATUS_PAID, Order.STATUS_DELIVERED])
    revenue = completed_qs.aggregate(total=Sum("total_price"))["total"] or Decimal("0")
    avg_ticket = completed_qs.aggregate(avg=Avg("total_price"))["avg"] or Decimal("0")

    return {
        "total": total,
        "paid": paid,
        "cancelled": cancelled,
        "revenue": revenue,
        "avg_ticket": avg_ticket,
    }


def get_recent_orders(limit=10):
    return (
        Order.objects.select_related("customer")
        .prefetch_related("items__instrument")
        .order_by("-created_at")[:limit]
    )


def get_top_sold_products(limit=5):
    return (
        OrderItem.objects.values(
            "instrument__id",
            "instrument__name",
            "instrument__brand__name",
        )
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")[:limit]
    )
