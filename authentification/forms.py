from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import UserProfile


class LoginForm(forms.Form):
    username = forms.CharField(
        label="E-mail ou usuário",
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": "seu@email.com"}),
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
    )

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self._user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cd = super().clean()
        username = cd.get("username", "").strip()
        password = cd.get("password", "")
        if username and password:
            # suporte a login por e-mail
            if "@" in username:
                try:
                    username = User.objects.get(email__iexact=username).username
                except User.DoesNotExist:
                    pass
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                raise forms.ValidationError("Usuário ou senha inválidos.")
            if not user.is_active:
                raise forms.ValidationError("Esta conta está desativada.")
            self._user = user
        return cd

    def get_user(self):
        return self._user


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}))
    password2 = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]
        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
            "username": "Nome de usuário",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "João"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Silva"}),
            "email": forms.EmailInput(attrs={"placeholder": "seu@email.com"}),
            "username": forms.TextInput(attrs={"placeholder": "joaosilva"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email.lower()

    def clean(self):
        cd = super().clean()
        p1, p2 = cd.get("password1"), cd.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "As senhas não coincidem.")
        return cd

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="Nome", required=False)
    last_name = forms.CharField(label="Sobrenome", required=False)
    email = forms.EmailField(label="E-mail")

    class Meta:
        model = UserProfile
        fields = ["telefone", "cpf", "avatar"]
        labels = {"telefone": "Telefone", "cpf": "CPF", "avatar": "Foto de perfil"}
        widgets = {
            "telefone": forms.TextInput(attrs={"placeholder": "(11) 99999-9999"}),
            "cpf": forms.TextInput(attrs={"placeholder": "000.000.000-00"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
        self._user = user

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self._user:
            self._user.first_name = self.cleaned_data.get("first_name", "")
            self._user.last_name = self.cleaned_data.get("last_name", "")
            self._user.email = self.cleaned_data.get("email", "")
            if commit:
                self._user.save()
        if commit:
            profile.save()
        return profile
