import pytest
from decimal import Decimal
from faker import Faker

from orders.models import Order, OrderItem, Payment

fake = Faker("pt_BR")


@pytest.fixture
def order(db, user, instrument):
    return Order.objects.create(
        customer=user,
        status=Order.STATUS_PENDING,
        total_price=Decimal("5000.00"),
    )


@pytest.fixture
def order_item(db, order, instrument):
    return OrderItem.objects.create(
        order=order,
        instrument=instrument,
        quantity=2,
        unit_price=Decimal("2500.00"),
    )


@pytest.fixture
def payment(db, order):
    return Payment.objects.create(
        order=order,
        status="pending",
        amount=Decimal("5000.00"),
        method="pix",
    )


class TestOrder:
    def test_create_order(self, db, user):
        total = Decimal(str(fake.pydecimal(left_digits=4, right_digits=2, positive=True)))
        order = Order.objects.create(
            customer=user,
            status=Order.STATUS_PENDING,
            total_price=total,
        )
        assert order.pk is not None
        assert order.status == Order.STATUS_PENDING
        assert order.total_price == total
        assert order.customer == user

    def test_str(self, order):
        assert f"Pedido #{order.pk}" in str(order)

    def test_status_choices_exist(self):
        statuses = [c[0] for c in Order.STATUS_CHOICES]
        assert Order.STATUS_PENDING in statuses
        assert Order.STATUS_PAID in statuses
        assert Order.STATUS_SHIPPED in statuses
        assert Order.STATUS_DELIVERED in statuses
        assert Order.STATUS_CANCELLED in statuses

    def test_status_css_pending(self, order):
        order.status = Order.STATUS_PENDING
        assert "yellow" in order.status_css

    def test_status_css_paid(self, order):
        order.status = Order.STATUS_PAID
        assert "blue" in order.status_css

    def test_status_css_cancelled(self, order):
        order.status = Order.STATUS_CANCELLED
        assert "red" in order.status_css

    def test_status_css_delivered(self, order):
        order.status = Order.STATUS_DELIVERED
        assert "green" in order.status_css

    def test_history_created(self, order):
        assert order.history.count() >= 1

    def test_default_ordering_newest_first(self, db, user):
        o1 = Order.objects.create(customer=user, total_price=Decimal("100.00"))
        o2 = Order.objects.create(customer=user, total_price=Decimal("200.00"))
        orders = list(Order.objects.all())
        assert orders[0].pk == o2.pk


class TestOrderItem:
    def test_subtotal(self, order_item):
        assert order_item.subtotal == order_item.unit_price * order_item.quantity

    def test_subtotal_precision(self, db, order, instrument):
        item = OrderItem.objects.create(
            order=order,
            instrument=instrument,
            quantity=3,
            unit_price=Decimal("1999.99"),
        )
        assert item.subtotal == Decimal("5999.97")

    def test_str(self, order_item):
        assert str(order_item.quantity) in str(order_item)
        assert order_item.instrument.name in str(order_item)


class TestPayment:
    def test_create_payment(self, db, order):
        amount = Decimal(str(fake.pydecimal(left_digits=4, right_digits=2, positive=True)))
        payment = Payment.objects.create(
            order=order,
            status="approved",
            amount=amount,
            method="credit_card",
        )
        assert payment.pk is not None
        assert payment.order == order
        assert payment.amount == amount

    def test_str(self, payment):
        assert str(payment.order_id) in str(payment)

    def test_one_to_one_constraint(self, db, order):
        Payment.objects.create(
            order=order,
            amount=Decimal("100.00"),
            method="pix",
        )
        with pytest.raises(Exception):
            Payment.objects.create(
                order=order,
                amount=Decimal("200.00"),
                method="boleto",
            )

    def test_method_choices(self):
        methods = [c[0] for c in Payment.METHOD_CHOICES]
        assert "credit_card" in methods
        assert "pix" in methods
        assert "boleto" in methods

    def test_history_created(self, payment):
        assert payment.history.count() >= 1
