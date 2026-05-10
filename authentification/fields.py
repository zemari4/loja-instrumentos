from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


class EncryptedCharField(models.TextField):
    """TextField que armazena o valor criptografado com Fernet.

    Se FIELD_ENCRYPTION_KEY não estiver configurado, armazena em texto claro
    (compatível com ambiente de desenvolvimento sem a chave configurada).
    Valores já existentes em texto claro são retornados sem erro (migração gradual).
    """

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        key = getattr(settings, "FIELD_ENCRYPTION_KEY", None)
        if not key:
            return value
        try:
            return Fernet(key.encode()).decrypt(value.encode()).decode()
        except InvalidToken:
            return value
        except Exception:
            return ""

    def get_prep_value(self, value):
        if not value:
            return value
        key = getattr(settings, "FIELD_ENCRYPTION_KEY", None)
        if not key:
            return value
        return Fernet(key.encode()).encrypt(value.encode()).decode()
