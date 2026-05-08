import pytest
from decimal import Decimal
from faker import Faker

from catalog.models import Instrument, StockMovement

fake = Faker("pt_BR")


@pytest.fixture
def stock_movement(db, instrument, user):
    return StockMovement.objects.create(
        instrument=instrument,
        quantity_change=20,
        movement_type=StockMovement.Type.RESTOCK,
        notes=fake.sentence(),
        created_by=user,
    )


class TestStockMovementModel:
    def test_creates_movement(self, db, instrument, user):
        qty = fake.random_int(min=1, max=100)
        mov = StockMovement.objects.create(
            instrument=instrument,
            quantity_change=qty,
            movement_type=StockMovement.Type.RESTOCK,
            created_by=user,
        )
        assert mov.pk is not None
        assert mov.quantity_change == qty
        assert mov.instrument == instrument

    def test_negative_quantity_allowed(self, db, instrument):
        mov = StockMovement.objects.create(
            instrument=instrument,
            quantity_change=-5,
            movement_type=StockMovement.Type.SALE,
        )
        assert mov.quantity_change == -5

    def test_str_positive(self, stock_movement):
        assert "+" in str(stock_movement)

    def test_str_negative(self, db, instrument):
        mov = StockMovement.objects.create(
            instrument=instrument,
            quantity_change=-3,
            movement_type=StockMovement.Type.SALE,
        )
        assert "-3" in str(mov)

    def test_ordering_newest_first(self, db, instrument):
        for _ in range(3):
            StockMovement.objects.create(
                instrument=instrument,
                quantity_change=fake.random_int(min=1, max=10),
                movement_type=StockMovement.Type.ADJUSTMENT,
            )
        movements = list(StockMovement.objects.filter(instrument=instrument))
        assert movements[0].created_at >= movements[-1].created_at

    def test_movement_type_choices(self):
        types = {t.value for t in StockMovement.Type}
        assert "restock" in types
        assert "adjustment" in types
        assert "sale" in types
        assert "return" in types

    def test_created_by_nullable(self, db, instrument):
        mov = StockMovement.objects.create(
            instrument=instrument,
            quantity_change=5,
            movement_type=StockMovement.Type.ADJUSTMENT,
            created_by=None,
        )
        assert mov.created_by is None

    def test_cascade_delete_with_instrument(self, db, instrument, user):
        StockMovement.objects.create(
            instrument=instrument,
            quantity_change=10,
            movement_type=StockMovement.Type.RESTOCK,
            created_by=user,
        )
        pk = instrument.pk
        instrument.delete()
        assert StockMovement.objects.filter(instrument_id=pk).count() == 0
