import pytest
from django.db.models.query import QuerySet

from catalog.models import Category, Instrument


@pytest.mark.django_db
class TestInstrumentListView:
    def test_returns_200(self, client, instrument):
        response = client.get("/produtos")
        assert response.status_code == 200

    def test_shows_active_products(self, client, instrument, inactive_instrument):
        response = client.get("/produtos")
        products = list(response.context["products"])
        assert instrument in products
        assert inactive_instrument not in products

    def test_search_by_name(self, client, instrument):
        response = client.get("/busca?q=Stratocaster")
        assert instrument in list(response.context["products"])

    def test_search_by_brand(self, client, instrument):
        response = client.get("/busca?q=Fender")
        assert instrument in list(response.context["products"])

    def test_search_no_match(self, client, instrument):
        response = client.get("/busca?q=xyzxyz")
        assert list(response.context["products"]) == []

    def test_sort_price_asc(self, client, instrument, category, brand):
        Instrument.objects.create(
            category=category, brand=brand, name="Barato",
            slug="barato", price="100.00", stock=1, is_active=True,
        )
        response = client.get("/produtos?sort=price_asc")
        products = list(response.context["products"])
        prices = [p.price for p in products]
        assert prices == sorted(prices)


@pytest.mark.django_db
class TestCategoryView:
    def test_returns_200_for_valid_category(self, client, category, instrument):
        response = client.get(f"/categoria/{category.slug}")
        assert response.status_code == 200

    def test_returns_404_for_invalid_slug(self, client):
        response = client.get("/categoria/nao-existe")
        assert response.status_code == 404

    def test_shows_instruments_in_category(self, client, category, instrument):
        response = client.get(f"/categoria/{category.slug}")
        assert instrument in list(response.context["products"])

    def test_includes_subcategory_instruments(self, client, category, brand):
        subcategory = Category.objects.create(name="Sub", slug="sub", parent=category)
        sub_instrument = Instrument.objects.create(
            category=subcategory, brand=brand, name="Sub Instr",
            slug="sub-instr", price="1000.00", stock=1, is_active=True,
        )
        response = client.get(f"/categoria/{category.slug}")
        assert sub_instrument in list(response.context["products"])


@pytest.mark.django_db
class TestInstrumentDetailView:
    def test_returns_200_for_active(self, client, instrument):
        response = client.get(f"/produto/{instrument.slug}")
        assert response.status_code == 200

    def test_returns_404_for_inactive(self, client, inactive_instrument):
        response = client.get(f"/produto/{inactive_instrument.slug}")
        assert response.status_code == 404

    def test_increments_views(self, client, instrument):
        initial = instrument.views_count
        client.get(f"/produto/{instrument.slug}")
        instrument.refresh_from_db()
        assert instrument.views_count == initial + 1

    def test_context_has_related(self, client, instrument):
        response = client.get(f"/produto/{instrument.slug}")
        assert isinstance(response.context["related"], QuerySet)
