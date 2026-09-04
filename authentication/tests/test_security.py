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


CHAVE_TESTE = "XisV3giLTCZ3mTPzRMRT5zgMIjiADVRY38fU8iYwdfE="
OUTRA_CHAVE = "d3Vf1PBmWzKhFCkX_QeAlWSoBQjuxK8L1mFvA-nRLzE="


@pytest.mark.django_db
class TestCpfMigracaoGradual:
    """Registros gravados antes da cifra precisam continuar legíveis (issue #17)."""

    def _grava_texto_claro(self, user, valor):
        from django.db import connection

        from authentication.models import UserProfile

        profile = UserProfile.objects.create(user=user)
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE authentication_userprofile SET cpf = %s WHERE id = %s",
                [valor, profile.pk],
            )
        return profile

    @override_settings(FIELD_ENCRYPTION_KEY=CHAVE_TESTE)
    def test_valor_legado_em_texto_claro_continua_legivel(self, user):
        from authentication.models import UserProfile

        profile = self._grava_texto_claro(user, "52998224725")
        assert UserProfile.objects.get(pk=profile.pk).cpf == "52998224725"

    @override_settings(FIELD_ENCRYPTION_KEY=CHAVE_TESTE)
    def test_valor_legado_e_reescrito_cifrado_no_proximo_save(self, user):
        from django.db import connection

        from authentication.models import UserProfile

        profile = self._grava_texto_claro(user, "52998224725")
        recarregado = UserProfile.objects.get(pk=profile.pk)
        recarregado.save()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cpf FROM authentication_userprofile WHERE id = %s", [profile.pk]
            )
            bruto = cursor.fetchone()[0]
        assert bruto.startswith("gAAAAA")

    @override_settings(FIELD_ENCRYPTION_KEY=OUTRA_CHAVE)
    def test_valor_cifrado_com_outra_chave_nao_derruba_a_leitura(self, user):
        """Troca de chave não pode transformar leitura em erro 500."""
        from authentication.models import UserProfile

        profile = self._grava_texto_claro(user, "gAAAAAB-token-de-outra-chave")
        assert UserProfile.objects.get(pk=profile.pk).cpf is not None


@pytest.mark.django_db
class TestCpfFalhaNaoApagaDado:
    """Antes, qualquer exceção inesperada virava string vazia — o dado sumia da
    aplicação e podia ser sobrescrito com vazio no save seguinte (issue #17)."""

    @override_settings(FIELD_ENCRYPTION_KEY=CHAVE_TESTE)
    def test_erro_inesperado_propaga_em_vez_de_retornar_vazio(self, user):
        from unittest.mock import patch

        from authentication.models import UserProfile

        UserProfile.objects.create(user=user, cpf="52998224725")

        with patch("authentication.fields.get_fernet") as mock:
            mock.return_value.decrypt.side_effect = RuntimeError("falha no cofre")
            with pytest.raises(RuntimeError):
                UserProfile.objects.get(user=user)


class TestChaveDeCifra:
    def test_chave_invalida_falha_alto(self):
        from django.core.exceptions import ImproperlyConfigured

        from authentication.fields import get_fernet

        with override_settings(FIELD_ENCRYPTION_KEY="isto-nao-e-uma-chave-fernet"):
            with pytest.raises(ImproperlyConfigured):
                get_fernet()

    def test_sem_chave_retorna_none(self):
        from authentication.fields import get_fernet

        with override_settings(FIELD_ENCRYPTION_KEY=None):
            assert get_fernet() is None

    def test_check_avisa_quando_chave_ausente(self):
        from authentication.checks import check_field_encryption_key

        with override_settings(FIELD_ENCRYPTION_KEY=None):
            resultado = check_field_encryption_key(None)
        assert [aviso.id for aviso in resultado] == ["authentication.W001"]

    def test_check_silencioso_quando_chave_presente(self):
        from authentication.checks import check_field_encryption_key

        with override_settings(FIELD_ENCRYPTION_KEY=CHAVE_TESTE):
            assert check_field_encryption_key(None) == []


@pytest.mark.django_db
class TestCpfNaoEPesquisavel:
    """Fixa a limitação documentada no docstring do campo: o Fernet embute IV
    aleatório, então o mesmo CPF gera textos cifrados diferentes e a busca por
    igualdade nunca casa. Se algum dia isso mudar, este teste avisa."""

    @override_settings(FIELD_ENCRYPTION_KEY=CHAVE_TESTE)
    def test_busca_por_igualdade_nao_encontra(self, user):
        from authentication.models import UserProfile

        UserProfile.objects.create(user=user, cpf="52998224725")
        assert not UserProfile.objects.filter(cpf="52998224725").exists()

    @override_settings(FIELD_ENCRYPTION_KEY=CHAVE_TESTE)
    def test_mesmo_cpf_gera_textos_cifrados_diferentes(self):
        from authentication.fields import get_fernet

        fernet = get_fernet()
        assert fernet.encrypt(b"52998224725") != fernet.encrypt(b"52998224725")
