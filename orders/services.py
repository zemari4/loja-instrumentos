from django.db import models, transaction
from django.db.models import Count

from cart.services import cart_instrument_pks, cart_total, clear_cart, get_cart
from orders.models import Order, OrderItem


class OutOfStockError(Exception):
    pass


class ItemUnavailableError(Exception):
    """Algum instrumento do carrinho foi desativado depois de adicionado."""

    def __init__(self, names):
        self.names = list(names)
        super().__init__("Itens indisponíveis: " + ", ".join(self.names))


def create_order_from_cart(user, cart_session, address_data):
    if not cart_instrument_pks(cart_session):
        raise ValueError("Carrinho vazio.")

    with transaction.atomic():
        from catalog.models import Instrument

        # Bloqueia as linhas de todas as entradas do carrinho, inclusive as de
        # instrumentos inativos, e revalida is_active sobre o estado bloqueado.
        instruments = {
            inst.pk: inst
            for inst in Instrument.objects.select_for_update().filter(
                pk__in=cart_instrument_pks(cart_session)
            )
        }

        inativos = [inst.name for inst in instruments.values() if not inst.is_active]
        if inativos:
            raise ItemUnavailableError(inativos)

        cart_items = get_cart(cart_session)
        if not cart_items:
            raise ValueError("Carrinho vazio.")
        qty_map = {item["pk"]: item["qty"] for item in cart_items}

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
