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
