import logging
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

logger = logging.getLogger(__name__)


@lru_cache(maxsize=4)
def _fernet(chave: str) -> Fernet:
    """Constrói o Fernet uma vez por chave.

    O cache é indexado pela própria chave, então override_settings em testes
    passa a usar outra entrada em vez de reaproveitar a anterior.
    """
    try:
        return Fernet(chave.encode())
    except (ValueError, TypeError) as exc:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY não é uma chave Fernet válida. Gere uma com: "
            'python -c "from cryptography.fernet import Fernet; '
            'print(Fernet.generate_key().decode())"'
        ) from exc


def get_fernet():
    """Retorna o Fernet configurado, ou None quando não há chave definida."""
    chave = getattr(settings, "FIELD_ENCRYPTION_KEY", None)
    return _fernet(chave) if chave else None


class EncryptedCharField(models.TextField):
    """TextField que grava o valor cifrado com Fernet.

    Sem FIELD_ENCRYPTION_KEY definida, grava em texto claro. Esse fallback existe
    para não travar um ambiente recém-clonado, mas é modo degradado: a checagem
    de sistema `authentication.W001` avisa sempre que ele estiver em vigor.

    Valores em texto claro já existentes continuam legíveis — a leitura os devolve
    sem erro, o que permite migrar aos poucos. São reescritos cifrados no próximo
    save do registro.

    Limitação relevante: o Fernet não é determinístico, porque embute IV aleatório
    e timestamp. Dois registros com o mesmo CPF produzem textos cifrados
    diferentes, então este campo não é pesquisável por igualdade nem por
    `__in`, `__contains` e afins — `filter(cpf="529...")` nunca casa. Para buscar,
    é preciso carregar e comparar em Python, ou manter um hash determinístico à
    parte, num campo próprio.
    """

    def from_db_value(self, value, expression, connection):
        if not value:
            return value

        fernet = get_fernet()
        if fernet is None:
            return value

        try:
            return fernet.decrypt(value.encode()).decode()
        except InvalidToken:
            # Registro anterior à cifra, ou gravado com outra chave. Devolver o
            # valor como está é o que permite a migração gradual.
            logger.warning(
                "Valor de %s não pôde ser decifrado com a chave atual; "
                "tratado como texto claro legado.",
                self.name or "EncryptedCharField",
            )
            return value
        except Exception:
            # Antes esta cláusula devolvia "", o que apagava o dado do ponto de
            # vista da aplicação e podia sobrescrever o registro com vazio no save
            # seguinte. Falhar alto é preferível a destruir dado em silêncio.
            logger.exception(
                "Falha inesperada ao decifrar %s.", self.name or "EncryptedCharField"
            )
            raise

    def get_prep_value(self, value):
        if not value:
            return value

        fernet = get_fernet()
        if fernet is None:
            return value

        return fernet.encrypt(value.encode()).decode()
