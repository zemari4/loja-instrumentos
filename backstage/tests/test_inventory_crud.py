import io
import pytest
from decimal import Decimal
from faker import Faker

from django.contrib.auth.models import User
from django.urls import reverse

from catalog.models import Brand, Category, Instrument, StockMovement

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


class TestProductCreateView:
    def test_get_renders_form(self, client, staff_user):
        client.force_login(staff_user)
        response = client.get(reverse("backstage:inventory_create"))
        assert response.status_code == 200
        assert "form" in response.context

    def test_requires_staff(self, client, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("backstage:inventory_create"))
        assert response.status_code == 302

    def test_creates_instrument(self, client, staff_user, category, brand):
        client.force_login(staff_user)
        name = fake.word().capitalize()
        data = {
            "name": name,
            "slug": "",
            "category": category.pk,
            "brand": brand.pk,
            "price": "1500.00",
            "original_price": "",
            "stock": 10,
            "description": "",
            "is_active": "on",
            "is_featured": "",
        }
        response = client.post(reverse("backstage:inventory_create"), data)
        assert response.status_code == 302
        assert Instrument.objects.filter(name=name).exists()

    def test_auto_generates_slug(self, client, staff_user, category, brand):
        client.force_login(staff_user)
        name = "Guitarra Elétrica Teste"
        data = {
            "name": name,
            "slug": "",
            "category": category.pk,
            "brand": brand.pk,
            "price": "2000.00",
            "original_price": "",
            "stock": 5,
            "description": "",
            "is_active": "on",
        }
        client.post(reverse("backstage:inventory_create"), data)
        instrument = Instrument.objects.filter(name=name).first()
        assert instrument is not None
        assert instrument.slug != ""

    def test_invalid_form_rerenders(self, client, staff_user):
        client.force_login(staff_user)
        response = client.post(reverse("backstage:inventory_create"), {})
        assert response.status_code == 200
        assert "form" in response.context


class TestProductUpdateView:
    def test_get_renders_form(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.get(reverse("backstage:inventory_update", kwargs={"pk": instrument.pk}))
        assert response.status_code == 200
        assert response.context["form"].instance == instrument

    def test_requires_staff(self, client, regular_user, instrument):
        client.force_login(regular_user)
        response = client.get(reverse("backstage:inventory_update", kwargs={"pk": instrument.pk}))
        assert response.status_code == 302

    def test_updates_instrument(self, client, staff_user, instrument):
        client.force_login(staff_user)
        new_price = fake.pydecimal(left_digits=4, right_digits=2, positive=True)
        data = {
            "name": instrument.name,
            "slug": instrument.slug,
            "category": instrument.category.pk,
            "brand": instrument.brand.pk,
            "price": str(new_price),
            "original_price": "",
            "stock": instrument.stock,
            "description": instrument.description,
            "is_active": "on",
        }
        response = client.post(reverse("backstage:inventory_update", kwargs={"pk": instrument.pk}), data)
        assert response.status_code == 302
        instrument.refresh_from_db()
        assert instrument.price == Decimal(str(new_price)).quantize(Decimal("0.01"))

    def test_404_for_unknown_pk(self, client, staff_user):
        client.force_login(staff_user)
        response = client.get(reverse("backstage:inventory_update", kwargs={"pk": 99999}))
        assert response.status_code == 404


class TestProductDeleteView:
    def test_get_shows_confirmation(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.get(reverse("backstage:inventory_delete", kwargs={"pk": instrument.pk}))
        assert response.status_code == 200
        assert response.context["object"] == instrument

    def test_post_deletes_instrument(self, client, staff_user, instrument):
        client.force_login(staff_user)
        pk = instrument.pk
        response = client.post(reverse("backstage:inventory_delete", kwargs={"pk": pk}))
        assert response.status_code == 302
        assert not Instrument.objects.filter(pk=pk).exists()

    def test_requires_staff(self, client, regular_user, instrument):
        client.force_login(regular_user)
        response = client.post(reverse("backstage:inventory_delete", kwargs={"pk": instrument.pk}))
        assert response.status_code == 302
        assert Instrument.objects.filter(pk=instrument.pk).exists()


class TestStockAdjustmentView:
    def test_get_renders_form(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.get(reverse("backstage:stock_adjust", kwargs={"pk": instrument.pk}))
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["instrument"] == instrument

    def test_positive_adjustment_increases_stock(self, client, staff_user, instrument):
        client.force_login(staff_user)
        initial = instrument.stock
        qty = fake.random_int(min=1, max=20)
        client.post(
            reverse("backstage:stock_adjust", kwargs={"pk": instrument.pk}),
            {"quantity_change": qty, "movement_type": StockMovement.Type.RESTOCK, "notes": ""},
        )
        instrument.refresh_from_db()
        assert instrument.stock == initial + qty

    def test_negative_adjustment_decreases_stock(self, client, staff_user, instrument):
        client.force_login(staff_user)
        instrument.stock = 20
        instrument.save()
        qty = fake.random_int(min=1, max=5)
        client.post(
            reverse("backstage:stock_adjust", kwargs={"pk": instrument.pk}),
            {"quantity_change": -qty, "movement_type": StockMovement.Type.SALE, "notes": ""},
        )
        instrument.refresh_from_db()
        assert instrument.stock == 20 - qty

    def test_stock_never_goes_below_zero(self, client, staff_user, instrument):
        client.force_login(staff_user)
        instrument.stock = 2
        instrument.save()
        client.post(
            reverse("backstage:stock_adjust", kwargs={"pk": instrument.pk}),
            {"quantity_change": -999, "movement_type": StockMovement.Type.SALE, "notes": ""},
        )
        instrument.refresh_from_db()
        assert instrument.stock == 0

    def test_creates_stock_movement_record(self, client, staff_user, instrument):
        client.force_login(staff_user)
        before = StockMovement.objects.filter(instrument=instrument).count()
        note = fake.sentence()
        client.post(
            reverse("backstage:stock_adjust", kwargs={"pk": instrument.pk}),
            {"quantity_change": 5, "movement_type": StockMovement.Type.RESTOCK, "notes": note},
        )
        assert StockMovement.objects.filter(instrument=instrument).count() == before + 1
        mov = StockMovement.objects.filter(instrument=instrument).latest("created_at")
        assert mov.notes == note
        assert mov.created_by == staff_user

    def test_requires_staff(self, client, regular_user, instrument):
        client.force_login(regular_user)
        response = client.get(reverse("backstage:stock_adjust", kwargs={"pk": instrument.pk}))
        assert response.status_code == 302


class TestStockHistoryView:
    def test_shows_movements(self, client, staff_user, instrument):
        client.force_login(staff_user)
        StockMovement.objects.create(
            instrument=instrument,
            quantity_change=fake.random_int(min=1, max=50),
            movement_type=StockMovement.Type.RESTOCK,
            created_by=staff_user,
        )
        response = client.get(reverse("backstage:stock_history", kwargs={"pk": instrument.pk}))
        assert response.status_code == 200
        assert "movements" in response.context
        assert response.context["instrument"] == instrument

    def test_empty_history(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.get(reverse("backstage:stock_history", kwargs={"pk": instrument.pk}))
        assert response.status_code == 200
        assert list(response.context["movements"]) == []

    def test_requires_staff(self, client, regular_user, instrument):
        client.force_login(regular_user)
        response = client.get(reverse("backstage:stock_history", kwargs={"pk": instrument.pk}))
        assert response.status_code == 302


class TestProductExportView:
    def test_export_xlsx(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.get(reverse("backstage:inventory_export") + "?formato=xlsx")
        assert response.status_code == 200
        assert "spreadsheetml" in response["Content-Type"]
        assert response["Content-Disposition"].endswith('"produtos.xlsx"')

    def test_export_csv(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.get(reverse("backstage:inventory_export") + "?formato=csv")
        assert response.status_code == 200
        assert "text/csv" in response["Content-Type"]

    def test_requires_staff(self, client, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("backstage:inventory_export"))
        assert response.status_code == 302


class TestProductImportView:
    def test_get_renders_form(self, client, staff_user):
        client.force_login(staff_user)
        response = client.get(reverse("backstage:inventory_import"))
        assert response.status_code == 200
        assert "form" in response.context

    def test_import_valid_csv(self, client, staff_user, category, brand):
        client.force_login(staff_user)
        name = fake.word().capitalize()
        csv_content = (
            "id,name,slug,categoria,marca,price,original_price,stock,is_active,is_featured,description\n"
            f",{name},slug-importado-01,{category.name},{brand.name},999.00,,15,True,False,\n"
        )
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        csv_file.name = "produtos.csv"
        response = client.post(
            reverse("backstage:inventory_import"),
            {"import_file": csv_file},
        )
        assert response.status_code == 302

    def test_unsupported_format_shows_error(self, client, staff_user):
        client.force_login(staff_user)
        txt_file = io.BytesIO(b"invalid")
        txt_file.name = "arquivo.txt"
        response = client.post(
            reverse("backstage:inventory_import"),
            {"import_file": txt_file},
        )
        assert response.status_code == 200
        assert "form" in response.context

    def test_import_creates_missing_brand(self, client, staff_user, category):
        client.force_login(staff_user)
        new_brand_name = fake.company()
        csv_content = (
            "id,name,slug,categoria,marca,price,original_price,stock,is_active,is_featured,description\n"
            f",{fake.word()},slug-nova-marca,{category.name},{new_brand_name},799.00,,5,True,False,\n"
        )
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        csv_file.name = "produtos.csv"
        client.post(reverse("backstage:inventory_import"), {"import_file": csv_file})
        from catalog.models import Brand
        assert Brand.objects.filter(name=new_brand_name).exists()

    def test_import_creates_missing_category(self, client, staff_user, brand):
        client.force_login(staff_user)
        new_cat_name = fake.word().capitalize()
        csv_content = (
            "id,name,slug,categoria,marca,price,original_price,stock,is_active,is_featured,description\n"
            f",{fake.word()},slug-nova-cat,{new_cat_name},{brand.name},599.00,,3,True,False,\n"
        )
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        csv_file.name = "produtos.csv"
        client.post(reverse("backstage:inventory_import"), {"import_file": csv_file})
        from catalog.models import Category
        assert Category.objects.filter(name=new_cat_name).exists()

    def test_requires_staff(self, client, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("backstage:inventory_import"))
        assert response.status_code == 302
