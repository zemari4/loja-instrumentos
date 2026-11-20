"""Issue #14: o contador do rate limit mora num cache compartilhado (Redis).

Limites em authentication/views.py: login 10/min e cadastro 5/min, por IP.
"""
import pytest
from django.core.cache import caches
from django_redis import get_redis_connection

LOGIN_URL = "/usuario/entrar"
REGISTER_URL = "/usuario/cadastro"


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

    def test_counter_is_stored_in_redis(self, client):
        _login_attempt(client)
        assert get_redis_connection("default").keys("*rl:*")

    def test_counter_survives_closing_the_cache_connection(self, client):
        # Simula um restart do processo: a conexão cai, o contador continua no Redis.
        for _ in range(10):
            _login_attempt(client)
        caches.close_all()
        assert _login_attempt(client).status_code == 403


@pytest.mark.django_db
class TestRegisterRateLimit:
    def test_blocks_the_sixth_attempt_from_the_same_ip(self, client):
        for _ in range(5):
            assert _register_attempt(client).status_code != 403
        assert _register_attempt(client).status_code == 403
