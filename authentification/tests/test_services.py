import pytest
from django.test import RequestFactory

from authentification.models import LoginHistory, UserProfile
from authentification.services import get_client_ip, get_or_create_profile, record_login


class TestGetClientIp:
    def test_returns_remote_addr(self):
        rf = RequestFactory()
        request = rf.get("/", REMOTE_ADDR="1.2.3.4")
        assert get_client_ip(request) == "1.2.3.4"

    def test_prefers_x_forwarded_for(self):
        rf = RequestFactory()
        request = rf.get("/", HTTP_X_FORWARDED_FOR="5.6.7.8, 9.9.9.9", REMOTE_ADDR="1.2.3.4")
        assert get_client_ip(request) == "5.6.7.8"


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
