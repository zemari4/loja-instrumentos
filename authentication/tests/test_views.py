import pytest
from django.contrib.auth.models import User
from django.test import override_settings


@pytest.mark.django_db
class TestLoginView:
    @override_settings(RATELIMIT_ENABLE=False)
    def test_get_renders_form(self, client):
        response = client.get("/usuario/entrar")
        assert response.status_code == 200

    @override_settings(RATELIMIT_ENABLE=False)
    def test_post_valid_redirects(self, client, user):
        response = client.post("/usuario/entrar", {
            "username": "testuser",
            "password": "testpass123",
        })
        assert response.status_code == 302

    @override_settings(RATELIMIT_ENABLE=False)
    def test_post_invalid_stays_on_page(self, client, user):
        response = client.post("/usuario/entrar", {
            "username": "testuser",
            "password": "wrong",
        })
        assert response.status_code == 200

    @override_settings(RATELIMIT_ENABLE=False)
    def test_authenticated_redirects_to_home(self, client, user):
        client.force_login(user)
        response = client.get("/usuario/entrar")
        assert response.status_code == 302


@pytest.mark.django_db
class TestRegisterView:
    @override_settings(RATELIMIT_ENABLE=False)
    def test_get_renders_form(self, client):
        response = client.get("/usuario/cadastro")
        assert response.status_code == 200

    @override_settings(RATELIMIT_ENABLE=False)
    def test_post_valid_creates_user(self, client):
        response = client.post("/usuario/cadastro", {
            "first_name": "João",
            "last_name": "Silva",
            "email": "joao@example.com",
            "username": "joaosilva",
            "password1": "senhaSegura123",
            "password2": "senhaSegura123",
        })
        assert response.status_code == 302
        assert User.objects.filter(username="joaosilva").exists()

    @override_settings(RATELIMIT_ENABLE=False)
    def test_authenticated_redirects_to_home(self, client, user):
        client.force_login(user)
        response = client.get("/usuario/cadastro")
        assert response.status_code == 302


@pytest.mark.django_db
class TestProfileView:
    def test_anon_redirects_to_login(self, client):
        response = client.get("/usuario/perfil")
        assert response.status_code == 302
        assert "/usuario/entrar" in response["Location"]

    def test_authenticated_renders(self, client, user):
        client.force_login(user)
        response = client.get("/usuario/perfil")
        assert response.status_code == 200


@pytest.mark.django_db
class TestLogoutView:
    def test_logout_redirects(self, client, user):
        client.force_login(user)
        response = client.get("/usuario/sair")
        assert response.status_code == 302
        assert not response.wsgi_request.user.is_authenticated

    def test_session_invalidated_after_logout(self, client, user):
        client.force_login(user)
        client.get("/usuario/sair")
        follow_response = client.get("/usuario/perfil")
        assert follow_response.status_code == 302
