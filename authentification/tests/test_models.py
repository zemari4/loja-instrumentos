import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestUserProfile:
    def test_str_with_full_name(self, user):
        from authentification.models import UserProfile

        profile = UserProfile.objects.create(user=user)
        assert str(profile) == "Perfil de Test User"

    def test_str_with_username_fallback(self, db):
        from authentification.models import UserProfile

        u = User.objects.create_user(username="noname", password="pass")
        profile = UserProfile.objects.create(user=u)
        assert str(profile) == "Perfil de noname"

    def test_get_or_create_idempotent(self, user):
        from authentification.models import UserProfile

        p1 = UserProfile.objects.create(user=user)
        p2, created = UserProfile.objects.get_or_create(user=user)
        assert not created
        assert p1.pk == p2.pk


@pytest.mark.django_db
class TestLoginHistory:
    def test_str_success(self, user):
        from authentification.models import LoginHistory

        entry = LoginHistory.objects.create(user=user, success=True)
        assert "testuser" in str(entry)
        assert "OK" in str(entry)

    def test_str_failure(self, user):
        from authentification.models import LoginHistory

        entry = LoginHistory.objects.create(user=user, success=False)
        assert "FALHOU" in str(entry)

    def test_ordering_newest_first(self, user):
        from authentification.models import LoginHistory

        e1 = LoginHistory.objects.create(user=user)
        e2 = LoginHistory.objects.create(user=user)
        entries = list(LoginHistory.objects.filter(user=user))
        assert entries[0].pk == e2.pk
