import pytest
from decimal import Decimal

from cart.services import (
    add_item,
    cart_count,
    cart_total,
    clear_cart,
    get_cart,
    remove_item,
    update_item,
)


@pytest.mark.django_db
class TestAddItem:
    def test_adds_new_item(self, session, instrument):
        add_item(session, instrument.pk, qty=2)
        assert cart_count(session) == 2

    def test_accumulates_qty(self, session, instrument):
        add_item(session, instrument.pk, qty=2)
        add_item(session, instrument.pk, qty=3)
        assert cart_count(session) == 5

    def test_does_not_exceed_stock(self, session, instrument):
        instrument.stock = 3
        instrument.save()
        add_item(session, instrument.pk, qty=10)
        assert cart_count(session) == 3

    def test_ignores_inactive_product(self, session, inactive_instrument):
        add_item(session, inactive_instrument.pk)
        assert cart_count(session) == 0

    def test_ignores_nonexistent_product(self, session):
        add_item(session, 99999)
        assert cart_count(session) == 0

    def test_zero_qty_is_ignored(self, session, instrument):
        add_item(session, instrument.pk, qty=0)
        assert cart_count(session) == 0

    def test_negative_qty_is_ignored(self, session, instrument):
        add_item(session, instrument.pk, qty=-5)
        assert cart_count(session) == 0


@pytest.mark.django_db
class TestUpdateItem:
    def test_updates_quantity(self, session, instrument):
        add_item(session, instrument.pk, qty=2)
        update_item(session, instrument.pk, qty=5)
        assert cart_count(session) == 5

    def test_zero_removes_item(self, session, instrument):
        add_item(session, instrument.pk, qty=2)
        update_item(session, instrument.pk, qty=0)
        assert cart_count(session) == 0

    def test_negative_removes_item(self, session, instrument):
        add_item(session, instrument.pk, qty=2)
        update_item(session, instrument.pk, qty=-1)
        assert cart_count(session) == 0

    def test_capped_at_stock(self, session, instrument):
        instrument.stock = 3
        instrument.save()
        add_item(session, instrument.pk, qty=1)
        update_item(session, instrument.pk, qty=100)
        assert cart_count(session) == 3


@pytest.mark.django_db
class TestRemoveItem:
    def test_removes_item(self, session, instrument):
        add_item(session, instrument.pk, qty=2)
        remove_item(session, instrument.pk)
        assert cart_count(session) == 0

    def test_removing_nonexistent_is_safe(self, session):
        remove_item(session, 99999)


@pytest.mark.django_db
class TestClearCart:
    def test_empties_cart(self, session, instrument):
        add_item(session, instrument.pk, qty=3)
        clear_cart(session)
        assert cart_count(session) == 0


@pytest.mark.django_db
class TestCartTotal:
    def test_correct_total(self, session, instrument):
        instrument.price = Decimal("1000.00")
        instrument.save()
        add_item(session, instrument.pk, qty=3)
        assert cart_total(session) == Decimal("3000.00")

    def test_empty_cart_total(self, session):
        assert cart_total(session) == Decimal("0")


@pytest.mark.django_db
class TestGetCart:
    def test_returns_item_with_correct_fields(self, session, instrument):
        add_item(session, instrument.pk, qty=2)
        items = get_cart(session)
        assert len(items) == 1
        item = items[0]
        assert item["pk"] == instrument.pk
        assert item["qty"] == 2
        instrument.refresh_from_db()
        assert item["subtotal"] == instrument.price * 2

    def test_empty_session_returns_empty(self, session):
        assert get_cart(session) == []

    def test_skips_deleted_products(self, session, instrument):
        add_item(session, instrument.pk, qty=1)
        pk = instrument.pk
        instrument.delete()
        items = get_cart(session)
        assert all(i["pk"] != pk for i in items)
