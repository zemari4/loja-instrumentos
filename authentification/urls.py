from django.urls import path

from .views import LoginView, LogoutView, ProfileView, RegisterView

app_name = "authentification"

urlpatterns = [
    path("usuario/entrar", LoginView.as_view(), name="login"),
    path("usuario/cadastro", RegisterView.as_view(), name="register"),
    path("usuario/perfil", ProfileView.as_view(), name="profile"),
    path("usuario/sair", LogoutView.as_view(), name="logout"),
]
