"""Issue #14: o rate limit usa um cache compartilhado (Redis) e o check do
django-ratelimit não fica silenciado.

Roda `manage.py` num subprocesso: as settings escolhem o módulo (dev ou prod) por
DJANGO_ENV na importação, e o ambiente do pytest já fixa backend.settings_test.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# Chave de teste, a mesma de backend/settings_test.py. Não é segredo de verdade.
TEST_ENCRYPTION_KEY = "XisV3giLTCZ3mTPzRMRT5zgMIjiADVRY38fU8iYwdfE="

PROD_ENV = {
    "DJANGO_ENV": "prod",
    "SECRET_KEY": "chave-de-teste-" + "x" * 50,
    "FIELD_ENCRYPTION_KEY": TEST_ENCRYPTION_KEY,
    # Host inexistente: o check não pode depender de um Redis de pé.
    "CACHE_LOCATION": "redis://redis.invalid:6379/0",
}

PRINT_CACHE_SETTINGS = (
    "import json; from django.conf import settings; "
    "c = settings.CACHES['default']; "
    "print(json.dumps({'backend': c['BACKEND'], 'location': c['LOCATION'], "
    "'password': c['OPTIONS']['PASSWORD'], "
    "'silenced': sorted(settings.SILENCED_SYSTEM_CHECKS), "
    "'ratelimit_cache': settings.RATELIMIT_USE_CACHE}))"
)


def _manage(*args, extra=None, drop=()):
    env = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE" and k not in drop}
    env.update(extra or {})
    return subprocess.run([sys.executable, "manage.py", *args], cwd=ROOT, env=env, capture_output=True, text=True)


def _cache_settings(extra=None):
    drop = ("CACHE_LOCATION", "TEST_CACHE_LOCATION", "REDIS_PASSWORD")
    result = _manage("shell", "-c", PRINT_CACHE_SETTINGS, extra={"DJANGO_ENV": "dev", **(extra or {})}, drop=drop)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def default_dev():
    # REDIS_PASSWORD vazia, como no .env.example
    return _cache_settings({"REDIS_PASSWORD": ""})


@pytest.fixture(scope="module")
def custom_location():
    return _cache_settings({"CACHE_LOCATION": "redis://cache.example:6380/3", "REDIS_PASSWORD": "test-password"})


@pytest.fixture(scope="module")
def prod_check():
    return _manage("check", "--deploy", extra=PROD_ENV)


class TestSharedCacheSettings:
    def test_default_cache_is_django_redis(self, default_dev):
        assert default_dev["backend"] == "django_redis.cache.RedisCache"

    def test_default_location_is_local_redis(self, default_dev):
        assert default_dev["location"] == "redis://127.0.0.1:6379/0"

    def test_location_comes_from_cache_location_env(self, custom_location):
        assert custom_location["location"] == "redis://cache.example:6380/3"

    def test_empty_redis_password_becomes_none(self, default_dev):
        assert default_dev["password"] is None

    def test_password_comes_from_redis_password_env(self, custom_location):
        assert custom_location["password"] == "test-password"

    def test_rate_limit_uses_the_default_cache(self, default_dev):
        assert default_dev["ratelimit_cache"] == "default"

    def test_only_the_deliberate_check_stays_silenced(self, default_dev):
        # security.W019: X_FRAME_OPTIONS = "SAMEORIGIN" é escolha deliberada do projeto.
        assert default_dev["silenced"] == ["security.W019"]


class TestProductionCache:
    def test_check_deploy_passes_without_ratelimit_errors(self, prod_check):
        output = prod_check.stdout + prod_check.stderr
        assert prod_check.returncode == 0, output
        assert "django_ratelimit" not in output, output

    def test_refuses_to_start_without_cache_location(self):
        result = _manage("check", extra={k: v for k, v in PROD_ENV.items() if k != "CACHE_LOCATION"},
                         drop=("CACHE_LOCATION",))
        assert result.returncode != 0
        assert "CACHE_LOCATION" in result.stderr
