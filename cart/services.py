from catalog.models import Instrument

CART_SESSION_KEY = "cart"


def _get_raw(session):
    return session.setdefault(CART_SESSION_KEY, {})


def get_cart(session):
    """Return list of dicts with product info + qty + subtotal."""
    raw = _get_raw(session)
    if not raw:
        return []

    instruments = Instrument.objects.filter(pk__in=raw.keys()).select_related("brand").prefetch_related("images")
    instrument_map = {str(obj.pk): obj for obj in instruments}

    items = []
    for pk_str, entry in raw.items():
        obj = instrument_map.get(pk_str)
        if obj is None:
            continue
        qty = max(1, min(entry.get("qty", 1), obj.stock))
        items.append({
            "pk": obj.pk,
            "name": str(obj),
            "slug": obj.slug,
            "price": obj.price,
            "qty": qty,
            "subtotal": obj.price * qty,
            "main_image": obj.main_image,
            "in_stock": obj.in_stock,
            "max_stock": obj.stock,
        })
    return items


def cart_total(session):
    return sum(item["subtotal"] for item in get_cart(session))


def cart_count(session):
    raw = _get_raw(session)
    return sum(entry.get("qty", 0) for entry in raw.values())


def add_item(session, product_pk, qty=1):
    if qty <= 0:
        return
    raw = _get_raw(session)
    try:
        obj = Instrument.objects.get(pk=product_pk, is_active=True)
    except Instrument.DoesNotExist:
        return
    pk_str = str(product_pk)
    current_qty = raw.get(pk_str, {}).get("qty", 0)
    new_qty = min(current_qty + qty, obj.stock)
    raw[pk_str] = {"qty": new_qty}
    session[CART_SESSION_KEY] = raw
    session.modified = True


def update_item(session, product_pk, qty):
    raw = _get_raw(session)
    pk_str = str(product_pk)
    if qty <= 0:
        raw.pop(pk_str, None)
    else:
        try:
            obj = Instrument.objects.get(pk=product_pk, is_active=True)
        except Instrument.DoesNotExist:
            return
        raw[pk_str] = {"qty": min(qty, obj.stock)}
    session[CART_SESSION_KEY] = raw
    session.modified = True


def remove_item(session, product_pk):
    raw = _get_raw(session)
    raw.pop(str(product_pk), None)
    session[CART_SESSION_KEY] = raw
    session.modified = True


def clear_cart(session):
    session[CART_SESSION_KEY] = {}
    session.modified = True
