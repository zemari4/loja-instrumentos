import pytest


@pytest.mark.django_db
class TestGetFeaturedProducts:
    def test_returns_featured_active_only(self, instrument, inactive_instrument, category, brand):
        from catalog.models import Instrument
        from catalog.services import get_featured_products

        Instrument.objects.create(
            category=category, brand=brand, name="Não featured",
            slug="nao-featured", price="1000.00", stock=1,
            is_active=True, is_featured=False,
        )
        results = list(get_featured_products())
        assert instrument in results
        assert inactive_instrument not in results
        assert all(i.is_featured and i.is_active for i in results)

    def test_respects_limit(self, category, brand):
        from catalog.models import Instrument
        from catalog.services import get_featured_products

        for i in range(5):
            Instrument.objects.create(
                category=category, brand=brand, name=f"Instr {i}",
                slug=f"instr-{i}", price="1000.00", stock=1,
                is_active=True, is_featured=True,
            )
        assert len(list(get_featured_products(limit=3))) == 3


@pytest.mark.django_db
class TestGetMostViewed:
    def test_returns_active_only(self, instrument, inactive_instrument):
        from catalog.services import get_most_viewed

        results = list(get_most_viewed())
        assert instrument in results
        assert inactive_instrument not in results

    def test_ordered_by_views(self, category, brand):
        from catalog.models import Instrument
        from catalog.services import get_most_viewed

        high = Instrument.objects.create(
            category=category, brand=brand, name="Popular",
            slug="popular", price="1000.00", stock=1, is_active=True, views_count=100,
        )
        low = Instrument.objects.create(
            category=category, brand=brand, name="Pouco visto",
            slug="pouco-visto", price="1000.00", stock=1, is_active=True, views_count=1,
        )
        results = list(get_most_viewed())
        assert results.index(high) < results.index(low)


@pytest.mark.django_db
class TestIncrementViews:
    def test_increments_views_count(self, instrument):
        from catalog.services import increment_views

        initial = instrument.views_count
        increment_views(instrument)
        instrument.refresh_from_db()
        assert instrument.views_count == initial + 1

    def test_does_not_update_other_instruments(self, instrument, category, brand):
        from catalog.models import Instrument
        from catalog.services import increment_views

        other = Instrument.objects.create(
            category=category, brand=brand, name="Outro",
            slug="outro", price="1000.00", stock=1, is_active=True,
        )
        increment_views(instrument)
        other.refresh_from_db()
        assert other.views_count == 0
