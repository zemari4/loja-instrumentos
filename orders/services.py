from django.db import models, transaction
from django.db.models import Count

from cart.services import cart_total, clear_cart, get_cart
from orders.models import Order, OrderItem


class OutOfStockError(Exception):
    pass


def create_order_from_cart(user, cart_session, address_data):
    cart_items = get_cart(cart_session)
    if not cart_items:
        raise ValueError("Carrinho vazio.")

    with transaction.atomic():
        from catalog.models import Instrument

        pks = [item["pk"] for item in cart_items]
        qty_map = {item["pk"]: item["qty"] for item in cart_items}

        instruments = {
            inst.pk: inst
            for inst in Instrument.objects.select_for_update().filter(pk__in=pks)
        }

        for pk, inst in instruments.items():
            if inst.stock < qty_map[pk]:
                raise OutOfStockError(
                    f'"{inst.name}" tem apenas {inst.stock} unidade(s) em estoque.'
                )

        order = Order.objects.create(
            customer=user,
            status=Order.STATUS_PENDING,
            total_price=cart_total(cart_session),
            **address_data,
        )

        order_items = [
            OrderItem(
                order=order,
                instrument_id=item["pk"],
                quantity=item["qty"],
                unit_price=item["price"],
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        for item in cart_items:
            Instrument.objects.filter(pk=item["pk"]).update(
                stock=models.F("stock") - item["qty"]
            )

        clear_cart(cart_session)
        return order


def get_user_orders(user):
    return (
        Order.objects.filter(customer=user)
        .annotate(items_count=Count("items"))
        .order_by("-created_at")
    )


def get_order_detail(user, pk):
    return Order.objects.prefetch_related("items__instrument__brand").get(
        pk=pk, customer=user
    )
