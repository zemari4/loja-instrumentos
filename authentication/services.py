from django.conf import settings
from django.contrib.auth.models import User

from .models import LoginHistory, UserProfile


def get_client_ip(request) -> str | None:
    """IP do cliente para o LoginHistory.

    X-Forwarded-For é enviado pelo cliente: sem um proxy confiável na frente que
    o sobrescreva, qualquer um forja o valor e polui a trilha de auditoria. Por
    isso o header só é considerado quando TRUST_X_FORWARDED_FOR estiver ligado —
    e esse setting só deve ser ligado onde existir de fato um proxy sanitizando
    o header.
    """
    if getattr(settings, "TRUST_X_FORWARDED_FOR", False):
        encaminhado = request.META.get("HTTP_X_FORWARDED_FOR")
        if encaminhado:
            return encaminhado.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def record_login(request, user: User, success: bool = True) -> None:
    LoginHistory.objects.create(
        user=user,
        ip=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        success=success,
    )


def get_or_create_profile(user: User) -> UserProfile:
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile
