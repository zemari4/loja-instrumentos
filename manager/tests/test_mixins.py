import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.views.generic import TemplateView
from faker import Faker

from manager.mixins import BackstagePermissionMixin

fake = Faker("pt_BR")


class _StaffRequiredView(BackstagePermissionMixin, TemplateView):
    template_name = "manager/dashboard.html"


@pytest.fixture
def staff_user(db):
    username = fake.user_name()
    return User.objects.create_user(
        username=username,
        email=fake.email(),
        password=fake.password(),
        is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    username = fake.user_name()
    return User.objects.create_user(
        username=username,
        email=fake.email(),
        password=fake.password(),
        is_staff=False,
    )


class TestBackstagePermissionMixin:
    def test_anonymous_user_is_redirected(self, db):
        factory = RequestFactory()
        request = factory.get("/backstage/")
        request.user = AnonymousUser()

        view = _StaffRequiredView.as_view()
        response = view(request)

        assert response.status_code == 302
        assert "/usuario/entrar" in response["Location"]

    def test_non_staff_user_is_redirected(self, regular_user):
        factory = RequestFactory()
        request = factory.get("/backstage/")
        request.user = regular_user

        view = _StaffRequiredView.as_view()
        response = view(request)

        assert response.status_code == 302

    def test_staff_user_is_allowed(self, staff_user, rf):
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.contrib.sessions.backends.db import SessionStore

        request = rf.get("/backstage/")
        request.user = staff_user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        view = _StaffRequiredView.as_view()
        response = view(request)

        assert response.status_code == 200
