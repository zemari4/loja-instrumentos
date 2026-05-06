import os

import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings_test")
os.environ.setdefault("DJANGO_ENV", "test")
os.environ.setdefault("DISABLE_CACHE", "True")
os.environ.setdefault("DISABLE_REDIS", "True")
os.environ.setdefault("ENABLE_S3_STORAGE", "False")
os.environ.setdefault("DISABLE_DEBUG_TOOLBAR", "True")


class MockSession(dict):
    """Dict que simula o objeto session do Django (tem atributo modified)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modified = False


@pytest.fixture
def session():
    return MockSession()


@pytest.fixture
def user(db):
    from django.contrib.auth.models import User

    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def category(db):
    from catalog.models import Category

    return Category.objects.create(name="Guitarras", slug="guitarras")


@pytest.fixture
def brand(db):
    from catalog.models import Brand

    return Brand.objects.create(name="Fender", slug="fender")


@pytest.fixture
def instrument(db, category, brand):
    from catalog.models import Instrument

    return Instrument.objects.create(
        category=category,
        brand=brand,
        name="Stratocaster",
        slug="fender-stratocaster",
        price="5000.00",
        stock=10,
        is_active=True,
        is_featured=True,
    )


@pytest.fixture
def inactive_instrument(db, category, brand):
    from catalog.models import Instrument

    return Instrument.objects.create(
        category=category,
        brand=brand,
        name="Telecaster Inativa",
        slug="fender-telecaster-inativa",
        price="4000.00",
        stock=5,
        is_active=False,
    )
