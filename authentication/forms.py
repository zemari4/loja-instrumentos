import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

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
            # suporte a login por e-mail.
            # User.email não é único no modelo padrão do Django, e nem o admin nem
            # o fluxo social do allauth passam pela validação do RegisterForm. Um
            # .get() aqui levantaria MultipleObjectsReturned — não tratado, virava
            # HTTP 500 e travava o login dos dois usuários envolvidos.
            if "@" in username:
                correspondente = (
                    User.objects.filter(email__iexact=username).order_by("pk").first()
                )
                if correspondente:
                    username = correspondente.username
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
        return self.cleaned_data["email"].lower()

    def clean(self):
        cd = super().clean()

        # A checagem de e-mail duplicado fica aqui, e não em clean_email, para que
        # o erro seja não-field. Preso ao campo, o próprio destaque do e-mail já
        # confirmaria que o endereço existe na base, por mais genérico que fosse
        # o texto. A mensagem também não diz qual dado está em conflito.
        email = cd.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            self.add_error(
                None,
                "Não foi possível concluir o cadastro. Verifique os dados informados.",
            )

        p1, p2 = cd.get("password1"), cd.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "As senhas não coincidem.")
        elif p1:
            # Neste ponto self.instance ainda não tem username/email — um ModelForm
            # só os preenche em _post_clean(), que roda depois do clean(). Sem um
            # usuário preenchido, o validador de similaridade não teria o que comparar.
            candidato = User(
                username=cd.get("username") or "",
                email=cd.get("email") or "",
                first_name=cd.get("first_name") or "",
                last_name=cd.get("last_name") or "",
            )
            try:
                validate_password(p1, candidato)
            except forms.ValidationError as exc:
                self.add_error("password1", exc)
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

    def clean_cpf(self):
        cpf = re.sub(r"\D", "", self.cleaned_data.get("cpf", ""))
        if not cpf:
            return ""
        if len(cpf) != 11 or len(set(cpf)) == 1:
            raise forms.ValidationError("CPF inválido.")
        for i, peso_inicial in enumerate([10, 11]):
            total = sum(int(d) * (peso_inicial - j) for j, d in enumerate(cpf[:9 + i]))
            resto = (total * 10) % 11
            if resto >= 10:
                resto = 0
            if resto != int(cpf[9 + i]):
                raise forms.ValidationError("CPF inválido.")
        return cpf

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
