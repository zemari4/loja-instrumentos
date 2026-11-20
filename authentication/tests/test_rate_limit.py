"""Issue #14: o contador do rate limit mora num cache compartilhado (Redis).

Limites em authentication/views.py: login 10/min e cadastro 5/min, por IP.
Comportamento com o Redis fora do ar: docs/adr/0002-redis-como-cache-compartilhado.md.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from django.conf import settings
from django.core.cache import cache
from django.test import Client, override_settings
from django_redis import get_redis_connection

ROOT = Path(__file__).resolve().parents[2]

LOGIN_URL = "/usuario/entrar"
REGISTER_URL = "/usuario/cadastro"
CART_URL = "/carrinho/"

# Lê, noutro processo, o valor que este processo gravou no cache.
PROBE = (
    "import django; django.setup(); "
    "from django.core.cache import cache; print(cache.get('shared-probe'))"
)

UNREACHABLE_REDIS = "redis://127.0.0.1:1/0"


def _login_attempt(client):
    return client.post(LOGIN_URL, {"username": "ninguem", "password": "senha-errada"})


def _register_attempt(client):
    return client.post(REGISTER_URL, {})


@pytest.mark.django_db
class TestLoginRateLimit:
    def test_blocks_the_eleventh_attempt_from_the_same_ip(self, client):
        for _ in range(10):
            assert _login_attempt(client).status_code != 403
        assert _login_attempt(client).status_code == 403


@pytest.mark.django_db
class TestRegisterRateLimit:
    def test_blocks_the_sixth_attempt_from_the_same_ip(self, client):
        for _ in range(5):
            assert _register_attempt(client).status_code != 403
        assert _register_attempt(client).status_code == 403


class TestCounterStorage:
    @pytest.mark.django_db
    def test_counter_is_stored_in_redis(self, client):
        _login_attempt(client)
        assert get_redis_connection("default").keys("*rl:*")

    def test_cache_is_shared_across_processes(self):
        # Com o cache em memória, outro processo não enxerga o valor e o teste falha.
        cache.set("shared-probe", "set-by-the-test-process", timeout=60)
        result = subprocess.run(
            [sys.executable, "-c", PROBE], cwd=ROOT, env=os.environ.copy(), capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "set-by-the-test-process"


class TestRedisDown:
    """Redis fora do ar: o django-ratelimit falha "fechado" (RATELIMIT_FAIL_OPEN = False).

    O 500 fica fixado aqui para que mudar esse comportamento seja uma decisão
    deliberada (issue #46), não um efeito colateral. Os testes de POST usam
    `django_db`: sem ele o acesso ao banco é bloqueado e o 500 viria dele, não do Redis.
    """

    @pytest.fixture
    def redis_down(self):
        unreachable = {"default": {**settings.CACHES["default"], "LOCATION": UNREACHABLE_REDIS}}
        with override_settings(CACHES=unreachable):
            yield

    @pytest.mark.django_db
    def test_login_post_returns_500(self, redis_down):
        response = Client(raise_request_exception=False).post(LOGIN_URL, {"username": "a", "password": "b"})
        assert response.status_code == 500

    @pytest.mark.django_db
    def test_register_post_returns_500(self, redis_down):
        assert Client(raise_request_exception=False).post(REGISTER_URL, {}).status_code == 500

    @pytest.mark.django_db
    def test_read_pages_keep_working(self, redis_down):
        client = Client(raise_request_exception=False)
        assert client.get(LOGIN_URL).status_code == 200
        assert client.get(CART_URL).status_code == 200
