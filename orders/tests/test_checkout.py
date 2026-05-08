import pytest
from decimal import Decimal
from faker import Faker

from django.contrib.auth.models import User
from django.urls import reverse

from cart.services import add_item, cart_count, cart_total
from conftest import MockSession
from orders.forms import STATES as FORM_STATES
from orders.models import Order
from orders.services import OutOfStockError, create_order_from_cart

fake = Faker("pt_BR")

VALID_STATES = [code for code, _ in FORM_STATES if code]


def _fake_address():
    return {
        "shipping_name": fake.name(),
        "shipping_cep": f"{fake.random_int(min=10000, max=99999):05d}-{fake.random_int(min=100, max=999):03d}",
        "shipping_street": f"{fake.street_name()}, {fake.random_int(min=1, max=999)}",
        "shipping_complement": "",
        "shipping_neighborhood": fake.bairro(),
        "shipping_city": fake.city(),
        "shipping_state": fake.random_element(VALID_STATES),
    }


def _checkout_post_data(address=None):
    return {**(address or _fake_address()), "payment_method": "pix"}


def _fake_total():
    return Decimal(str(fake.pydecimal(left_digits=4, right_digits=2, positive=True, min_value=100)))


def _put_in_cart(client, instrument_pk, qty=1):
    """Adiciona item ao carrinho preservando a mesma referência de sessão."""
    from cart.services import add_item
    sess = client.session
    add_item(sess, instrument_pk, qty=qty)
    sess.save()


@pytest.fixture
def logged_user(client, db):
    user = User.objects.create_user(
        username=fake.user_name(),
        password=fake.password(length=12),
    )
    client.force_login(user)
    return user


class TestCheckoutView:
    def test_requires_login(self, client):
        response = client.get(reverse("orders:checkout"))
        assert response.status_code == 302
        assert reverse("authentification:login") in response["Location"]

    def test_empty_cart_redirects_to_cart(self, client, logged_user):
        response = client.get(reverse("orders:checkout"))
        assert response.status_code == 302
        assert response["Location"] == reverse("cart:cart")

    def test_get_shows_form_and_cart(self, client, logged_user, instrument):
        _put_in_cart(client, instrument.pk)
        response = client.get(reverse("orders:checkout"))
        assert response.status_code == 200
        assert "form" in response.context
        assert len(response.context["cart_items"]) == 1

    def test_post_creates_order(self, client, logged_user, instrument):
        _put_in_cart(client, instrument.pk)
        response = client.post(reverse("orders:checkout"), _checkout_post_data())
        assert response.status_code == 302
        assert Order.objects.filter(customer=logged_user).count() == 1

    def test_post_creates_order_items(self, client, logged_user, instrument):
        qty = fake.random_int(min=1, max=3)
        _put_in_cart(client, instrument.pk, qty=qty)
        client.post(reverse("orders:checkout"), _checkout_post_data())
        order = Order.objects.get(customer=logged_user)
        item = order.items.get()
        assert item.instrument == instrument
        assert item.quantity == qty

    def test_post_decrements_stock(self, client, logged_user, instrument):
        initial_stock = instrument.stock
        qty = fake.random_int(min=1, max=3)
        _put_in_cart(client, instrument.pk, qty=qty)
        client.post(reverse("orders:checkout"), _checkout_post_data())
        instrument.refresh_from_db()
        assert instrument.stock == initial_stock - qty

    def test_post_clears_cart(self, client, logged_user, instrument):
        _put_in_cart(client, instrument.pk)
        client.post(reverse("orders:checkout"), _checkout_post_data())
        assert cart_count(client.session) == 0

    def test_post_redirects_to_confirm(self, client, logged_user, instrument):
        _put_in_cart(client, instrument.pk)
        response = client.post(reverse("orders:checkout"), _checkout_post_data())
        order = Order.objects.get(customer=logged_user)
        assert response["Location"] == reverse("orders:order_confirm", kwargs={"pk": order.pk})

    def test_invalid_form_rerenders(self, client, logged_user, instrument):
        _put_in_cart(client, instrument.pk)
        response = client.post(reverse("orders:checkout"), {"shipping_name": ""})
        assert response.status_code == 200
        assert "form" in response.context

    def test_out_of_stock_shows_error(self, client, logged_user, instrument):
        _put_in_cart(client, instrument.pk)
        instrument.stock = 0
        instrument.save()
        response = client.post(reverse("orders:checkout"), _checkout_post_data())
        assert response.status_code == 200
        assert not Order.objects.filter(customer=logged_user).exists()

    def test_invalid_cep_shows_error(self, client, logged_user, instrument):
        _put_in_cart(client, instrument.pk)
        data = _checkout_post_data()
        data["shipping_cep"] = fake.bothify("??#-###")
        response = client.post(reverse("orders:checkout"), data)
        assert response.status_code == 200
        assert response.context["form"].errors.get("shipping_cep")

    def test_saves_shipping_address(self, client, logged_user, instrument):
        _put_in_cart(client, instrument.pk)
        addr = _fake_address()
        client.post(reverse("orders:checkout"), {**addr, "payment_method": "pix"})
        order = Order.objects.get(customer=logged_user)
        assert order.shipping_name == addr["shipping_name"]
        assert order.shipping_city == addr["shipping_city"]
        assert order.shipping_state == addr["shipping_state"]


class TestOrderConfirmView:
    def test_requires_login(self, client, db):
        pk = fake.random_int(min=9000, max=9999)
        response = client.get(reverse("orders:order_confirm", kwargs={"pk": pk}))
        assert response.status_code == 302

    def test_shows_own_order(self, client, logged_user, instrument):
        _put_in_cart(client, instrument.pk)
        client.post(reverse("orders:checkout"), _checkout_post_data())
        order = Order.objects.get(customer=logged_user)
        response = client.get(reverse("orders:order_confirm", kwargs={"pk": order.pk}))
        assert response.status_code == 200
        assert response.context["order"] == order

    def test_other_user_order_returns_404(self, client, logged_user, db):
        other = User.objects.create_user(username=fake.user_name(), password=fake.password())
        order = Order.objects.create(customer=other, total_price=_fake_total())
        response = client.get(reverse("orders:order_confirm", kwargs={"pk": order.pk}))
        assert response.status_code == 404


class TestOrderListView:
    def test_requires_login(self, client, db):
        response = client.get(reverse("orders:order_list"))
        assert response.status_code == 302

    def test_shows_only_own_orders(self, client, logged_user, db):
        other = User.objects.create_user(username=fake.user_name(), password=fake.password())
        Order.objects.create(customer=logged_user, total_price=_fake_total())
        Order.objects.create(customer=other, total_price=_fake_total())
        response = client.get(reverse("orders:order_list"))
        assert response.status_code == 200
        assert all(o.customer == logged_user for o in response.context["orders"])

    def test_empty_orders(self, client, logged_user):
        response = client.get(reverse("orders:order_list"))
        assert response.status_code == 200
        assert list(response.context["orders"]) == []


class TestOrderDetailView:
    def test_requires_login(self, client, db):
        pk = fake.random_int(min=9000, max=9999)
        response = client.get(reverse("orders:order_detail", kwargs={"pk": pk}))
        assert response.status_code == 302

    def test_shows_own_order(self, client, logged_user, db):
        order = Order.objects.create(customer=logged_user, total_price=_fake_total())
        response = client.get(reverse("orders:order_detail", kwargs={"pk": order.pk}))
        assert response.status_code == 200
        assert response.context["order"] == order

    def test_other_user_order_returns_404(self, client, logged_user, db):
        other = User.objects.create_user(username=fake.user_name(), password=fake.password())
        order = Order.objects.create(customer=other, total_price=_fake_total())
        response = client.get(reverse("orders:order_detail", kwargs={"pk": order.pk}))
        assert response.status_code == 404


class TestCreateOrderFromCart:
    def test_empty_cart_raises(self, db, user):
        session = MockSession()
        with pytest.raises(ValueError, match="vazio"):
            create_order_from_cart(user, session, _fake_address())

    def test_out_of_stock_raises(self, db, user, instrument):
        session = MockSession()
        add_item(session, instrument.pk, qty=1)
        instrument.stock = 0
        instrument.save()
        with pytest.raises(OutOfStockError):
            create_order_from_cart(user, session, _fake_address())

    def test_order_total_matches_cart(self, db, user, instrument):
        session = MockSession()
        qty = fake.random_int(min=1, max=3)
        add_item(session, instrument.pk, qty=qty)
        expected_total = cart_total(session)
        order = create_order_from_cart(user, session, _fake_address())
        assert order.total_price == expected_total
