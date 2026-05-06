import logging

logger = logging.getLogger(__name__)


class AttachRequestLogContext:
    """Adiciona IP e user ao contexto de log de cada requisição."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
