from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, UpdateView

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import LoginHistory
from .services import get_or_create_profile, record_login


@method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True), name="post")
class LoginView(FormView):
    template_name = "authentification/login.html"
    form_class = LoginForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        record_login(self.request, user, success=True)
        login(self.request, user)
        messages.success(self.request, f"Bem-vindo de volta, {user.first_name or user.username}!")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        username = form.data.get("username", "")
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username)
            record_login(self.request, user, success=False)
        except User.DoesNotExist:
            pass
        return super().form_invalid(form)

    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            return next_url
        return "/"


@method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True), name="post")
class RegisterView(FormView):
    template_name = "authentification/register.html"
    form_class = RegisterForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        get_or_create_profile(user)
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(self.request, "Cadastro realizado com sucesso!")
        return redirect("/")


class ProfileView(LoginRequiredMixin, FormView):
    template_name = "authentification/profile.html"
    form_class = ProfileForm
    login_url = "/usuario/entrar"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile = get_or_create_profile(self.request.user)
        kwargs["instance"] = profile
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["login_history"] = LoginHistory.objects.filter(
            user=self.request.user
        ).order_by("-timestamp")[:10]
        return ctx

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Perfil atualizado com sucesso!")
        return redirect("/usuario/perfil")


class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Você saiu da sua conta.")
        return redirect("/")
