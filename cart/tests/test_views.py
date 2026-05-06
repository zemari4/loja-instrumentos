import pytest


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
