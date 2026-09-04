from django.conf import settings
from django.core import checks

# Marcado como Warning, não Error, para não impedir um ambiente recém-clonado de
# subir. settings_prod.py já levanta ImproperlyConfigured quando a chave falta,
# então produção continua sem poder rodar sem cifra.
CHAVE_AUSENTE = checks.Warning(
    "FIELD_ENCRYPTION_KEY não está definida: campos cifrados serão gravados em "
    "texto claro.",
    hint=(
        "O CPF em authentication.UserProfile é dado pessoal sob LGPD. Gere uma "
        'chave com: python -c "from cryptography.fernet import Fernet; '
        'print(Fernet.generate_key().decode())" e defina FIELD_ENCRYPTION_KEY '
        "no .env."
    ),
    id="authentication.W001",
)


@checks.register(checks.Tags.security)
def check_field_encryption_key(app_configs, **kwargs):
    if not getattr(settings, "FIELD_ENCRYPTION_KEY", None):
        return [CHAVE_AUSENTE]
    return []
