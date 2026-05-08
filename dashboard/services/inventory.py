from catalog.models import Instrument

LOW_STOCK_THRESHOLD = 5


def get_inventory_kpis():
    active_qs = Instrument.objects.filter(is_active=True)
    return {
        "total": active_qs.count(),
        "low_stock": active_qs.filter(stock__lt=LOW_STOCK_THRESHOLD).count(),
        "out_of_stock": active_qs.filter(stock=0).count(),
    }


def get_low_stock_instruments():
    return (
        Instrument.objects.filter(is_active=True, stock__lt=LOW_STOCK_THRESHOLD)
        .select_related("category", "brand")
        .order_by("stock")
    )


def get_inventory_list():
    return (
        Instrument.objects.filter(is_active=True)
        .select_related("category", "brand")
        .order_by("name")
    )
