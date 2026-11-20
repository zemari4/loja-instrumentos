import pytest
from django.test import RequestFactory, override_settings

from authentication.models import LoginHistory, UserProfile
from authentication.services import get_client_ip, get_or_create_profile, record_login


class TestGetClientIp:
    def test_returns_remote_addr(self):
        rf = RequestFactory()
        request = rf.get("/", REMOTE_ADDR="1.2.3.4")
        assert get_client_ip(request) == "1.2.3.4"

    @override_settings(TRUST_X_FORWARDED_FOR=True)
    def test_usa_x_forwarded_for_quando_ha_proxy_confiavel(self):
        rf = RequestFactory()
        request = rf.get("/", HTTP_X_FORWARDED_FOR="5.6.7.8, 9.9.9.9", REMOTE_ADDR="1.2.3.4")
        assert get_client_ip(request) == "5.6.7.8"

    @override_settings(TRUST_X_FORWARDED_FOR=False)
    def test_ignora_x_forwarded_for_sem_proxy_confiavel(self):
        """Sem proxy à frente, o header vem do cliente e é forjável."""
        rf = RequestFactory()
        request = rf.get("/", HTTP_X_FORWARDED_FOR="5.6.7.8", REMOTE_ADDR="1.2.3.4")
        assert get_client_ip(request) == "1.2.3.4"

    def test_padrao_do_projeto_e_nao_confiar(self):
        from django.conf import settings

        assert getattr(settings, "TRUST_X_FORWARDED_FOR", False) is False


@pytest.mark.django_db
class TestRecordLogin:
    def test_creates_login_history_success(self, user):
        rf = RequestFactory()
        request = rf.post("/", REMOTE_ADDR="1.2.3.4")
        record_login(request, user, success=True)

        entry = LoginHistory.objects.get(user=user)
        assert entry.success is True
        assert entry.ip == "1.2.3.4"

    def test_creates_login_history_failure(self, user):
        rf = RequestFactory()
        request = rf.post("/", REMOTE_ADDR="1.2.3.4")
        record_login(request, user, success=False)

        entry = LoginHistory.objects.get(user=user)
        assert entry.success is False


@pytest.mark.django_db
class TestGetOrCreateProfile:
    def test_creates_profile_if_missing(self, user):
        profile = get_or_create_profile(user)
        assert profile.user == user

    def test_returns_existing_profile(self, user):
        existing = UserProfile.objects.create(user=user, telefone="11999999999")
        returned = get_or_create_profile(user)
        assert returned.pk == existing.pk
        assert returned.telefone == "11999999999"
