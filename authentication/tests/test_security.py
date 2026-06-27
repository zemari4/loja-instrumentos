import pytest
from django.test import override_settings
from faker import Faker

fake = Faker("pt_BR")


@pytest.mark.django_db
class TestOpenRedirectLogin:
    @override_settings(RATELIMIT_ENABLE=False)
    def test_next_externo_ignorado(self, client, user):
        response = client.post(
            f"/usuario/entrar?next=https://evil.com",
            {"username": user.username, "password": "testpass123"},
        )
        assert response.status_code == 302
        assert "evil.com" not in response["Location"]

    @override_settings(RATELIMIT_ENABLE=False)
    def test_next_interno_permitido(self, client, user):
        response = client.post(
            "/usuario/entrar?next=/catalogo/",
            {"username": user.username, "password": "testpass123"},
        )
        assert response.status_code == 302
        assert response["Location"] == "/catalogo/"

    @override_settings(RATELIMIT_ENABLE=False)
    def test_next_vazio_vai_para_home(self, client, user):
        response = client.post(
            "/usuario/entrar",
            {"username": user.username, "password": "testpass123"},
        )
        assert response.status_code == 302
        assert response["Location"] == "/"

    @override_settings(RATELIMIT_ENABLE=False)
    def test_next_protocolo_javascript_bloqueado(self, client, user):
        response = client.post(
            "/usuario/entrar?next=javascript:alert(1)",
            {"username": user.username, "password": "testpass123"},
        )
        assert response.status_code == 302
        assert "javascript" not in response["Location"]


@pytest.mark.django_db
class TestOpenRedirectCart:
    def test_next_externo_ignorado(self, client, instrument):
        response = client.post(
            f"/carrinho/adicionar/{instrument.pk}/",
            {"qty": "1", "next": "https://evil.com"},
        )
        assert response.status_code == 302
        assert "evil.com" not in response["Location"]

    def test_next_interno_permitido(self, client, instrument):
        response = client.post(
            f"/carrinho/adicionar/{instrument.pk}/",
            {"qty": "1", "next": "/carrinho/"},
        )
        assert response.status_code == 302
        assert response["Location"] == "/carrinho/"

    def test_referer_externo_ignorado(self, client, instrument):
        response = client.post(
            f"/carrinho/adicionar/{instrument.pk}/",
            {"qty": "1"},
            HTTP_REFERER="https://evil.com/phishing",
        )
        assert response.status_code == 302
        assert "evil.com" not in response["Location"]


@pytest.mark.django_db
class TestCpfEncryption:
    @override_settings(FIELD_ENCRYPTION_KEY="XisV3giLTCZ3mTPzRMRT5zgMIjiADVRY38fU8iYwdfE=")
    def test_cpf_armazenado_criptografado(self, user):
        from authentication.models import UserProfile
        from django.db import connection

        profile = UserProfile.objects.create(user=user, cpf="52998224725")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cpf FROM authentication_userprofile WHERE id = %s",
                [profile.pk],
            )
            raw = cursor.fetchone()[0]

        assert raw != "52998224725"
        assert raw.startswith("gAAAAA")

    @override_settings(FIELD_ENCRYPTION_KEY="XisV3giLTCZ3mTPzRMRT5zgMIjiADVRY38fU8iYwdfE=")
    def test_cpf_descriptografado_ao_ler(self, user):
        from authentication.models import UserProfile

        UserProfile.objects.create(user=user, cpf="52998224725")
        profile = UserProfile.objects.get(user=user)
        assert profile.cpf == "52998224725"

    @override_settings(FIELD_ENCRYPTION_KEY="XisV3giLTCZ3mTPzRMRT5zgMIjiADVRY38fU8iYwdfE=")
    def test_cpf_vazio_nao_criptografado(self, user):
        from authentication.models import UserProfile

        profile = UserProfile.objects.create(user=user, cpf="")
        profile_reload = UserProfile.objects.get(pk=profile.pk)
        assert profile_reload.cpf == ""


@pytest.mark.django_db
class TestCpfValidation:
    def test_cpf_valido_aceito(self):
        from authentication.forms import ProfileForm

        form = ProfileForm(data={"cpf": "529.982.247-25", "email": fake.email()})
        form.is_valid()
        assert "cpf" not in form.errors

    def test_cpf_invalido_rejeitado(self):
        from authentication.forms import ProfileForm

        form = ProfileForm(data={"cpf": "111.111.111-11", "email": fake.email()})
        form.is_valid()
        assert "cpf" in form.errors

    def test_cpf_curto_rejeitado(self):
        from authentication.forms import ProfileForm

        form = ProfileForm(data={"cpf": "123.456", "email": fake.email()})
        form.is_valid()
        assert "cpf" in form.errors

    def test_cpf_vazio_aceito(self):
        from authentication.forms import ProfileForm

        form = ProfileForm(data={"cpf": "", "email": fake.email()})
        form.is_valid()
        assert "cpf" not in form.errors
