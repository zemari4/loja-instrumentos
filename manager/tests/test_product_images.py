import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from faker import Faker

from catalog.models import Instrument, ProductImage

fake = Faker("pt_BR")

TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


def make_image():
    return SimpleUploadedFile(
        f"{fake.slug()}.png",
        TINY_PNG,
        content_type="image/png",
    )


@pytest.fixture(autouse=True)
def use_tmp_media(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username=fake.user_name(),
        password=fake.password(),
        is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username=fake.user_name(),
        password=fake.password(),
        is_staff=False,
    )


@pytest.fixture
def product_image(db, instrument):
    return ProductImage.objects.create(
        instrument=instrument,
        image=make_image(),
        is_main=True,
        order=0,
    )


class TestProductImageUploadView:
    def test_upload_single_image_saves_and_redirects(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert response.status_code == 302
        assert instrument.images.count() == 1

    def test_redirect_goes_to_product_update_page(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert response["Location"] == reverse("manager:inventory_update", kwargs={"pk": instrument.pk})

    def test_first_uploaded_image_becomes_main(self, client, staff_user, instrument):
        client.force_login(staff_user)
        client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert instrument.images.filter(is_main=True).count() == 1

    def test_upload_multiple_images(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": [make_image() for _ in range(3)]},
        )
        assert response.status_code == 302
        assert instrument.images.count() == 3

    def test_respects_max_5_limit(self, client, staff_user, instrument):
        client.force_login(staff_user)
        for i in range(3):
            ProductImage.objects.create(instrument=instrument, image=make_image(), order=i)
        client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": [make_image() for _ in range(4)]},
        )
        assert instrument.images.count() == 5

    def test_upload_when_at_max_does_not_add_images(self, client, staff_user, instrument):
        client.force_login(staff_user)
        for i in range(5):
            ProductImage.objects.create(instrument=instrument, image=make_image(), order=i)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert response.status_code == 302
        assert instrument.images.count() == 5

    def test_subsequent_upload_does_not_override_main(self, client, staff_user, instrument):
        client.force_login(staff_user)
        ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=True, order=0)
        client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert instrument.images.filter(is_main=True).count() == 1

    def test_no_files_redirects_without_saving(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {},
        )
        assert response.status_code == 302
        assert instrument.images.count() == 0

    def test_requires_staff(self, client, regular_user, instrument):
        client.force_login(regular_user)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert response.status_code == 302
        assert instrument.images.count() == 0


HTMX_HEADERS = {"HTTP_HX_REQUEST": "true"}


class TestProductImageDeleteView:
    def test_htmx_delete_returns_partial(self, client, staff_user, product_image, instrument):
        client.force_login(staff_user)
        pk = product_image.pk
        response = client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": pk}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 200
        assert not ProductImage.objects.filter(pk=pk).exists()

    def test_non_htmx_delete_redirects(self, client, staff_user, product_image, instrument):
        client.force_login(staff_user)
        pk = product_image.pk
        response = client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": pk})
        )
        assert response.status_code == 302
        assert not ProductImage.objects.filter(pk=pk).exists()

    def test_missing_image_htmx_returns_204(self, client, staff_user):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": 99999}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 204

    def test_deleting_main_promotes_next_by_order(self, client, staff_user, instrument):
        client.force_login(staff_user)
        main_img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=True, order=0)
        other_img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=False, order=1)
        client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": main_img.pk}),
            **HTMX_HEADERS,
        )
        other_img.refresh_from_db()
        assert other_img.is_main is True

    def test_deleting_non_main_preserves_main(self, client, staff_user, instrument):
        client.force_login(staff_user)
        main_img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=True, order=0)
        other_img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=False, order=1)
        client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": other_img.pk}),
            **HTMX_HEADERS,
        )
        main_img.refresh_from_db()
        assert main_img.is_main is True

    def test_deleting_last_image_leaves_no_main(self, client, staff_user, instrument):
        client.force_login(staff_user)
        only_img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=True, order=0)
        client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": only_img.pk}),
            **HTMX_HEADERS,
        )
        assert instrument.images.count() == 0

    def test_requires_staff(self, client, regular_user, product_image):
        client.force_login(regular_user)
        response = client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": product_image.pk}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 302
        assert ProductImage.objects.filter(pk=product_image.pk).exists()


class TestProductImageSetMainView:
    def test_htmx_set_main_returns_partial(self, client, staff_user, instrument):
        client.force_login(staff_user)
        img1 = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=True, order=0)
        img2 = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=False, order=1)
        response = client.post(
            reverse("manager:product_image_set_main", kwargs={"image_pk": img2.pk}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 200
        img1.refresh_from_db()
        img2.refresh_from_db()
        assert img2.is_main is True
        assert img1.is_main is False

    def test_non_htmx_set_main_redirects(self, client, staff_user, instrument):
        client.force_login(staff_user)
        img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=False, order=0)
        response = client.post(
            reverse("manager:product_image_set_main", kwargs={"image_pk": img.pk})
        )
        assert response.status_code == 302

    def test_missing_image_htmx_returns_204(self, client, staff_user):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_set_main", kwargs={"image_pk": 99999}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 204

    def test_only_one_image_is_main(self, client, staff_user, instrument):
        client.force_login(staff_user)
        images = [
            ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=(i == 0), order=i)
            for i in range(3)
        ]
        client.post(
            reverse("manager:product_image_set_main", kwargs={"image_pk": images[2].pk}),
            **HTMX_HEADERS,
        )
        assert instrument.images.filter(is_main=True).count() == 1

    def test_requires_staff(self, client, regular_user, product_image):
        client.force_login(regular_user)
        response = client.post(
            reverse("manager:product_image_set_main", kwargs={"image_pk": product_image.pk}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 302
