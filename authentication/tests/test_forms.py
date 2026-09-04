import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory


@pytest.mark.django_db
class TestLoginForm:
    def test_valid_with_username(self, user):
        from authentication.forms import LoginForm

        rf = RequestFactory()
        request = rf.post("/")
        form = LoginForm(
            data={"username": "testuser", "password": "testpass123"},
            request=request,
        )
        assert form.is_valid()
        assert form.get_user() == user

    def test_valid_with_email(self, user):
        from authentication.forms import LoginForm

        rf = RequestFactory()
        request = rf.post("/")
        form = LoginForm(
            data={"username": "test@example.com", "password": "testpass123"},
            request=request,
        )
        assert form.is_valid()
        assert form.get_user() == user

    def test_invalid_password(self, user):
        from authentication.forms import LoginForm

        rf = RequestFactory()
        request = rf.post("/")
        form = LoginForm(
            data={"username": "testuser", "password": "wrongpass"},
            request=request,
        )
        assert not form.is_valid()
        assert "Usuário ou senha inválidos." in str(form.errors)

    def test_inactive_user(self, user):
        from authentication.forms import LoginForm

        user.is_active = False
        user.save()
        rf = RequestFactory()
        request = rf.post("/")
        form = LoginForm(
            data={"username": "testuser", "password": "testpass123"},
            request=request,
        )
        assert not form.is_valid()


@pytest.mark.django_db
class TestRegisterForm:
    def test_valid_registration(self, db):
        from authentication.forms import RegisterForm

        form = RegisterForm(
            data={
                "first_name": "João",
                "last_name": "Silva",
                "email": "joao@example.com",
                "username": "joaosilva",
                "password1": "senhaSegura123",
                "password2": "senhaSegura123",
            }
        )
        assert form.is_valid(), form.errors

    def test_duplicate_email(self, user):
        from authentication.forms import RegisterForm

        form = RegisterForm(
            data={
                "first_name": "Outro",
                "last_name": "User",
                "email": "test@example.com",
                "username": "outro",
                "password1": "senhaSegura123",
                "password2": "senhaSegura123",
            }
        )
        assert not form.is_valid()
        assert "e-mail já está cadastrado" in str(form.errors)

    def test_password_mismatch(self, db):
        from authentication.forms import RegisterForm

        form = RegisterForm(
            data={
                "first_name": "João",
                "last_name": "Silva",
                "email": "joao2@example.com",
                "username": "joao2",
                "password1": "senha123",
                "password2": "diferente",
            }
        )
        assert not form.is_valid()
        assert "não coincidem" in str(form.errors)

    def test_save_sets_password(self, db):
        from authentication.forms import RegisterForm

        form = RegisterForm(
            data={
                "first_name": "João",
                "last_name": "Silva",
                "email": "joao3@example.com",
                "username": "joao3",
                "password1": "senhaSegura123",
                "password2": "senhaSegura123",
            }
        )
        assert form.is_valid()
        u = form.save()
        assert u.check_password("senhaSegura123")


@pytest.mark.django_db
class TestProfileForm:
    def test_save_updates_user_fields(self, user):
        from authentication.forms import ProfileForm
        from authentication.models import UserProfile

        profile = UserProfile.objects.create(user=user)
        form = ProfileForm(
            data={
                "first_name": "Novo",
                "last_name": "Nome",
                "email": "novo@example.com",
                "telefone": "11999999999",
                "cpf": "",
            },
            instance=profile,
            user=user,
        )
        assert form.is_valid(), form.errors
        form.save()
        user.refresh_from_db()
        assert user.first_name == "Novo"
        assert user.email == "novo@example.com"


@pytest.mark.django_db
class TestRegisterFormPasswordPolicy:
    """Cobre a politica de senha do cadastro (issue #13).

    Antes desta politica o RegisterForm aceitava qualquer senha, incluindo "1":
    AUTH_PASSWORD_VALIDATORS nao estava definido e o form nunca chamava
    validate_password(). Cada teste abaixo fixa um dos validadores agora ativos.
    """

    BASE = {
        "first_name": "João",
        "last_name": "Silva",
        "email": "politica@example.com",
        "username": "joaosilva",
    }

    def _form(self, senha):
        from authentication.forms import RegisterForm

        return RegisterForm(data={**self.BASE, "password1": senha, "password2": senha})

    @pytest.mark.parametrize("senha", ["1", "123", "senha", "12345678", "aaaaaaaa"])
    def test_rejeita_senha_curta(self, db, senha):
        form = self._form(senha)
        assert not form.is_valid()
        assert "password1" in form.errors

    def test_rejeita_senha_comum(self, db):
        form = self._form("12345678901")
        assert not form.is_valid()
        assert "comum" in str(form.errors["password1"])

    def test_rejeita_senha_inteiramente_numerica(self, db):
        form = self._form("48219573064")
        assert not form.is_valid()
        assert "numérica" in str(form.errors["password1"])

    def test_rejeita_senha_parecida_com_usuario(self, db):
        # Este caso so passa porque clean() monta um User com os dados enviados.
        # self.instance ainda esta vazio nesse ponto do ciclo do ModelForm.
        form = self._form("joaosilva1")
        assert not form.is_valid()
        assert "parecida" in str(form.errors["password1"])

    def test_aceita_senha_forte(self, db):
        form = self._form("senhaSegura123")
        assert form.is_valid(), form.errors

    def test_erro_de_divergencia_tem_prioridade(self, db):
        """Senhas diferentes devem reportar divergencia, nao forca de senha."""
        from authentication.forms import RegisterForm

        form = RegisterForm(data={**self.BASE, "password1": "senha123", "password2": "diferente"})
        assert not form.is_valid()
        assert "não coincidem" in str(form.errors)
        assert "password1" not in form.errors

    def test_senha_forte_e_gravada_com_hash(self, db):
        form = self._form("senhaSegura123")
        assert form.is_valid(), form.errors
        u = form.save()
        assert u.password != "senhaSegura123"
        assert u.check_password("senhaSegura123")


class TestPasswordHashers:
    """Cobre a configuracao de hashers (issue #25).

    Le settings_base diretamente porque settings_test sobrescreve PASSWORD_HASHERS
    com MD5 para nao penalizar a suite — logo, o valor ativo durante os testes nao
    reflete o que roda em dev e producao.
    """

    def test_argon2_e_o_hasher_primario(self):
        from backend import settings_base

        assert settings_base.PASSWORD_HASHERS[0].endswith("Argon2PasswordHasher")

    def test_mantem_pbkdf2_como_fallback(self):
        """Sem PBKDF2 na lista, todo hash ja gravado deixaria de validar."""
        from backend import settings_base

        assert any("PBKDF2PasswordHasher" in h for h in settings_base.PASSWORD_HASHERS)

    def test_suite_usa_hasher_rapido(self):
        """A suite nao deve herdar Argon2, que e deliberadamente lento."""
        from django.conf import settings

        assert "MD5PasswordHasher" in settings.PASSWORD_HASHERS[0]
