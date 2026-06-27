import pytest
from django.contrib.auth.models import User
from faker import Faker

from home.models import MAX_CAROUSEL_SLIDES, CarouselSlide

fake = Faker("pt_BR")


def make_slide(**kwargs):
    defaults = {
        "order": 1,
        "is_active": True,
        "title": fake.sentence(nb_words=4),
        "subtitle": fake.sentence(nb_words=8),
        "text_alignment": CarouselSlide.TextAlignment.LEFT,
    }
    defaults.update(kwargs)
    return CarouselSlide.objects.create(**defaults)


@pytest.fixture
def staff_client(client):
    user = User.objects.create_user(
        username=fake.user_name(),
        email=fake.email(),
        password=fake.password(),
        is_staff=True,
    )
    client.force_login(user)
    return client


@pytest.mark.django_db
class TestCarouselSlideModel:
    def test_str_includes_order_and_title(self):
        slide = make_slide(order=1, title="Guitarras em oferta")
        assert "1" in str(slide)
        assert "Guitarras em oferta" in str(slide)

    def test_str_fallback_when_no_title(self):
        slide = make_slide(order=2, title="")
        assert "Sem título" in str(slide)

    def test_ordering_by_order(self):
        make_slide(order=3, title=fake.word())
        make_slide(order=1, title=fake.word())
        make_slide(order=2, title=fake.word())
        orders = list(CarouselSlide.objects.values_list("order", flat=True))
        assert orders == [1, 2, 3]

    def test_order_is_unique(self):
        from django.db import IntegrityError
        make_slide(order=1)
        with pytest.raises(IntegrityError):
            make_slide(order=1)

    def test_default_alignment_is_left(self):
        slide = CarouselSlide.objects.create(order=1)
        assert slide.text_alignment == CarouselSlide.TextAlignment.LEFT

    def test_is_active_defaults_true(self):
        slide = CarouselSlide.objects.create(order=1)
        assert slide.is_active is True

    def test_badges_default_false(self):
        slide = CarouselSlide.objects.create(order=1)
        assert slide.is_launch is False
        assert slide.is_promo is False


@pytest.mark.django_db
class TestHomeViewCarousel:
    def test_carousel_slides_in_context(self, client):
        make_slide(order=1)
        make_slide(order=2)
        response = client.get("/")
        assert "carousel_slides" in response.context

    def test_only_active_slides_returned(self, client):
        make_slide(order=1, is_active=True)
        make_slide(order=2, is_active=False)
        response = client.get("/")
        slides = list(response.context["carousel_slides"])
        assert len(slides) == 1
        assert slides[0].is_active is True

    def test_slides_ordered_by_position(self, client):
        make_slide(order=3)
        make_slide(order=1)
        make_slide(order=2)
        response = client.get("/")
        orders = [s.order for s in response.context["carousel_slides"]]
        assert orders == [1, 2, 3]

    def test_empty_carousel_context_when_no_slides(self, client):
        response = client.get("/")
        assert len(list(response.context["carousel_slides"])) == 0


@pytest.mark.django_db
class TestCarouselBackstageViews:
    def test_list_requires_staff(self, client):
        response = client.get("/manager/site/carrossel/")
        assert response.status_code == 302

    def test_list_accessible_by_staff(self, staff_client):
        response = staff_client.get("/manager/site/carrossel/")
        assert response.status_code == 200

    def test_list_shows_slides(self, staff_client):
        title = fake.sentence(nb_words=3)
        make_slide(order=1, title=title)
        response = staff_client.get("/manager/site/carrossel/")
        assert title in response.content.decode()

    def test_create_slide(self, staff_client):
        response = staff_client.post("/manager/site/carrossel/novo/", {
            "order": 1,
            "is_active": True,
            "is_launch": False,
            "is_promo": False,
            "title": fake.sentence(nb_words=4),
            "subtitle": fake.sentence(nb_words=6),
            "text_alignment": "left",
        })
        assert response.status_code == 302
        assert CarouselSlide.objects.count() == 1

    def test_cannot_exceed_max_slides(self, staff_client):
        for i in range(1, MAX_CAROUSEL_SLIDES + 1):
            make_slide(order=i)
        response = staff_client.get("/manager/site/carrossel/novo/")
        assert response.status_code == 302

    def test_update_slide(self, staff_client):
        slide = make_slide(order=1, title=fake.sentence())
        new_title = fake.sentence(nb_words=5)
        staff_client.post(f"/manager/site/carrossel/{slide.pk}/editar/", {
            "order": 1,
            "is_active": True,
            "is_launch": False,
            "is_promo": False,
            "title": new_title,
            "subtitle": fake.sentence(),
            "text_alignment": "center",
        })
        slide.refresh_from_db()
        assert slide.title == new_title
        assert slide.text_alignment == "center"

    def test_delete_slide(self, staff_client):
        slide = make_slide(order=1)
        staff_client.post(f"/manager/site/carrossel/{slide.pk}/excluir/")
        assert CarouselSlide.objects.count() == 0
