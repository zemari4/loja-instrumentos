import pytest
from django.contrib.messages import get_messages

from cart.services import add_item


@pytest.mark.django_db
class TestCartView:
    def test_get_returns_200(self, client):
        response = client.get("/carrinho/")
        assert response.status_code == 200

    def test_context_has_items_and_total(self, client):
        response = client.get("/carrinho/")
        assert "items" in response.context
        assert "total" in response.context


@pytest.mark.django_db
class TestAddToCartView:
    def test_post_valid_product_redirects(self, client, instrument):
        response = client.post(f"/carrinho/adicionar/{instrument.pk}/", {"qty": "1"})
        assert response.status_code == 302

    def test_post_adds_to_session(self, client, instrument):
        client.post(f"/carrinho/adicionar/{instrument.pk}/", {"qty": "2"})
        session = client.session
        cart = session.get("cart", {})
        assert str(instrument.pk) in cart
        assert cart[str(instrument.pk)]["qty"] == 2

    def test_post_inactive_returns_404(self, client, inactive_instrument):
        response = client.post(f"/carrinho/adicionar/{inactive_instrument.pk}/", {"qty": "1"})
        assert response.status_code == 404

    def test_post_invalid_qty_defaults_to_1(self, client, instrument):
        client.post(f"/carrinho/adicionar/{instrument.pk}/", {"qty": "abc"})
        session = client.session
        cart = session.get("cart", {})
        assert cart[str(instrument.pk)]["qty"] == 1


@pytest.mark.django_db
class TestRemoveFromCartView:
    def test_removes_item_and_redirects(self, client, instrument):
        client.post(f"/carrinho/adicionar/{instrument.pk}/", {"qty": "1"})
        response = client.post(f"/carrinho/remover/{instrument.pk}/")
        assert response.status_code == 302
        cart = client.session.get("cart", {})
        assert str(instrument.pk) not in cart


@pytest.mark.django_db
class TestUpdateCartView:
    def test_updates_quantity_and_redirects(self, client, instrument):
        client.post(f"/carrinho/adicionar/{instrument.pk}/", {"qty": "1"})
        response = client.post(f"/carrinho/atualizar/{instrument.pk}/", {"qty": "3"})
        assert response.status_code == 302

    def test_zero_qty_removes_item(self, client, instrument):
        client.post(f"/carrinho/adicionar/{instrument.pk}/", {"qty": "1"})
        client.post(f"/carrinho/atualizar/{instrument.pk}/", {"qty": "0"})
        cart = client.session.get("cart", {})
        assert str(instrument.pk) not in cart


def _no_carrinho(client, instrument, qty=1):
    """Põe o item no carrinho da sessão do client."""
    sess = client.session
    add_item(sess, instrument.pk, qty=qty)
    sess.save()


def _avisos(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


@pytest.mark.django_db
class TestCartViewItemIndisponivel:
    """Issue #24: instrumento desativado depois de entrar no carrinho."""

    def test_item_desativado_sai_do_carrinho_com_aviso(self, client, instrument):
        _no_carrinho(client, instrument)
        instrument.is_active = False
        instrument.save()
        response = client.get("/carrinho/")
        assert response.status_code == 200
        assert response.context["items"] == []
        assert _avisos(response) == [
            f'"{instrument.name}" não está mais disponível e foi removido do carrinho.'
        ]
        assert client.session.get("cart") == {}

    def test_sem_item_indisponivel_nao_ha_aviso(self, client, instrument):
        _no_carrinho(client, instrument)
        response = client.get("/carrinho/")
        assert _avisos(response) == []
        assert [i["pk"] for i in response.context["items"]] == [instrument.pk]

    def test_aviso_aparece_uma_vez_so(self, client, instrument):
        _no_carrinho(client, instrument)
        instrument.is_active = False
        instrument.save()
        client.get("/carrinho/")
        segunda = client.get("/carrinho/")
        assert _avisos(segunda) == []
