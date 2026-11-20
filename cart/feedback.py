from django.contrib import messages


def avisar_itens_removidos(request, nomes):
    """Avisa o cliente de cada instrumento que saiu do carrinho por indisponibilidade."""
    for nome in nomes:
        messages.error(request, f'"{nome}" não está mais disponível e foi removido do carrinho.')
