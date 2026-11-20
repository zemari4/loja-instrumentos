import os

import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings_test")
os.environ.setdefault("DJANGO_ENV", "test")
os.environ.setdefault("ENABLE_S3_STORAGE", "False")
os.environ.setdefault("DISABLE_DEBUG_TOOLBAR", "True")


class MockSession(dict):
    """Dict que simula o objeto session do Django (tem atributo modified)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modified = False


@pytest.fixture(scope="session", autouse=True)
def _require_redis():
    """O cache é Redis em todos os ambientes (ADR 0002): sem ele, para cedo e explica."""
    from django.conf import settings
    from django_redis import get_redis_connection

    try:
        get_redis_connection("default").ping()
    except Exception as error:
        pytest.exit(
            "Redis inacessível em "
            f"{settings.CACHES['default']['LOCATION']} ({error.__class__.__name__}).\n"
            "Suba um com: docker run -d --name loja-redis -p 127.0.0.1:6379:6379 redis:7-alpine",
            returncode=3,
        )


@pytest.fixture(autouse=True)
def _clean_cache(_require_redis):
    """Contadores do rate limit persistem no Redis: cada teste começa com o cache vazio."""
    from django.core.cache import cache

    cache.clear()


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
def second_instrument(db, category, brand):
    """Outro instrumento ativo, para testes com mais de um item."""
    from catalog.models import Instrument

    return Instrument.objects.create(
        category=category,
        brand=brand,
        name="Telecaster",
        slug="fender-telecaster",
        price="100.00",
        stock=5,
        is_active=True,
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
