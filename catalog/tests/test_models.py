import pytest
from decimal import Decimal


@pytest.mark.django_db
class TestInstrumentProperties:
    def test_discount_percent_with_original_price(self, instrument):
        instrument.original_price = Decimal("10000.00")
        instrument.price = Decimal("8000.00")
        assert instrument.discount_percent == 20

    def test_discount_percent_no_original_price(self, instrument):
        instrument.original_price = None
        assert instrument.discount_percent is None

    def test_discount_percent_original_lower_than_price(self, instrument):
        instrument.original_price = Decimal("3000.00")
        instrument.price = Decimal("5000.00")
        assert instrument.discount_percent is None

    def test_price_installment(self, instrument):
        instrument.price = Decimal("1200.00")
        assert instrument.price_installment == Decimal("100.00")

    def test_in_stock_true(self, instrument):
        instrument.stock = 5
        assert instrument.in_stock is True

    def test_in_stock_false(self, instrument):
        instrument.stock = 0
        assert instrument.in_stock is False

    def test_main_image_no_images(self, instrument):
        assert instrument.main_image is None

    def test_str(self, instrument):
        assert str(instrument) == "Fender — Stratocaster"


@pytest.mark.django_db
class TestCategory:
    def test_str(self, category):
        assert str(category) == "Guitarras"

    def test_get_absolute_url(self, category):
        assert category.get_absolute_url() == "/categoria/guitarras"

    def test_hierarchical_parent(self, db, category):
        from catalog.models import Category

        child = Category.objects.create(name="Elétricas", slug="eletricas", parent=category)
        assert child.parent == category
        assert category.children.first() == child


@pytest.mark.django_db
class TestBrand:
    def test_str(self, brand):
        assert str(brand) == "Fender"
