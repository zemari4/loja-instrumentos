import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from faker import Faker

from orders.models import Order, OrderItem, Payment

fake = Faker("pt_BR")


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username=fake.user_name(),
        email=fake.email(),
        password=fake.password(),
        is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username=fake.user_name(),
        email=fake.email(),
        password=fake.password(),
        is_staff=False,
    )


@pytest.fixture
def order(db, staff_user, instrument):
    return Order.objects.create(
        customer=staff_user,
        status=Order.STATUS_PENDING,
        total_price=Decimal("5000.00"),
    )


class TestDashboardView:
    def test_redirect_anonymous(self, client):
        response = client.get(reverse("manager:dashboard"))
        assert response.status_code == 302

    def test_redirect_non_staff(self, client, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("manager:dashboard"))
        assert response.status_code == 302

    def test_staff_can_access(self, client, staff_user):
        client.force_login(staff_user)
        response = client.get(reverse("manager:dashboard"))
        assert response.status_code == 200
        assert "total" in response.context

    def test_kpi_context_keys_present(self, client, staff_user):
        client.force_login(staff_user)
        response = client.get(reverse("manager:dashboard"))
        for key in ("total", "paid", "cancelled", "revenue", "avg_ticket", "low_stock_count"):
            assert key in response.context, f"Chave '{key}' ausente no contexto"


class TestInventoryListView:
    def test_requires_staff(self, client, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("manager:inventory"))
        assert response.status_code == 302

    def test_staff_sees_instruments(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.get(reverse("manager:inventory"))
        assert response.status_code == 200
        assert instrument in response.context["instruments"]

    def test_filter_by_category(self, client, staff_user, instrument, category):
        client.force_login(staff_user)
        response = client.get(
            reverse("manager:inventory"), {"categoria": category.slug}
        )
        assert response.status_code == 200
        assert instrument in response.context["instruments"]

    def test_filter_excludes_wrong_category(self, client, staff_user, instrument, db):
        from catalog.models import Category
        other = Category.objects.create(
            name=fake.word(), slug=fake.slug()
        )
        client.force_login(staff_user)
        response = client.get(
            reverse("manager:inventory"), {"categoria": other.slug}
        )
        assert instrument not in response.context["instruments"]


class TestOrderListView:
    def test_requires_staff(self, client, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("manager:orders"))
        assert response.status_code == 302

    def test_staff_sees_orders(self, client, staff_user, order):
        client.force_login(staff_user)
        response = client.get(reverse("manager:orders"))
        assert response.status_code == 200
        assert order in response.context["orders"]

    def test_filter_by_status(self, client, staff_user, order):
        client.force_login(staff_user)
        response = client.get(
            reverse("manager:orders"), {"status": Order.STATUS_PENDING}
        )
        assert order in response.context["orders"]

    def test_filter_excludes_other_status(self, client, staff_user, order):
        client.force_login(staff_user)
        response = client.get(
            reverse("manager:orders"), {"status": Order.STATUS_CANCELLED}
        )
        assert order not in response.context["orders"]


class TestOrderDetailView:
    def test_staff_sees_order_detail(self, client, staff_user, order):
        client.force_login(staff_user)
        response = client.get(reverse("manager:order_detail", kwargs={"pk": order.pk}))
        assert response.status_code == 200
        assert response.context["order"] == order

    def test_404_for_invalid_pk(self, client, staff_user):
        client.force_login(staff_user)
        response = client.get(reverse("manager:order_detail", kwargs={"pk": 99999}))
        assert response.status_code == 404


class TestUpdateOrderStatusView:
    def test_update_status(self, client, staff_user, order):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:update_order_status", kwargs={"pk": order.pk}),
            {"status": Order.STATUS_PAID},
        )
        order.refresh_from_db()
        assert order.status == Order.STATUS_PAID
        assert response.status_code == 302

    def test_invalid_status_ignored(self, client, staff_user, order):
        original_status = order.status
        client.force_login(staff_user)
        client.post(
            reverse("manager:update_order_status", kwargs={"pk": order.pk}),
            {"status": "invalid_status"},
        )
        order.refresh_from_db()
        assert order.status == original_status


class TestAnalyticsView:
    def test_staff_can_access(self, client, staff_user):
        client.force_login(staff_user)
        response = client.get(reverse("manager:analytics"))
        assert response.status_code == 200
        assert "overview" in response.context
        assert "most_viewed" in response.context

    def test_requires_staff(self, client, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("manager:analytics"))
        assert response.status_code == 302


class TestCustomerListView:
    def test_staff_can_access(self, client, staff_user):
        client.force_login(staff_user)
        response = client.get(reverse("manager:customers"))
        assert response.status_code == 200
        assert "customers" in response.context

    def test_requires_staff(self, client, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("manager:customers"))
        assert response.status_code == 302
