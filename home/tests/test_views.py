import pytest


@pytest.mark.django_db
class TestHomeView:
    def test_get_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_context_has_featured_products(self, client):
        response = client.get("/")
        assert "featured_products" in response.context

    def test_context_has_cart_count(self, client):
        response = client.get("/")
        assert "cart_count" in response.context

    def test_cart_count_reflects_session(self, client, instrument):
        client.post(f"/carrinho/adicionar/{instrument.pk}/", {"qty": "3"})
        response = client.get("/")
        assert response.context["cart_count"] == 3


@pytest.mark.django_db
class TestRobotsTxtView:
    def test_returns_200(self, client):
        response = client.get("/robots.txt")
        assert response.status_code == 200

    def test_content_type(self, client):
        response = client.get("/robots.txt")
        assert "text/plain" in response["Content-Type"]

    def test_disallows_admin(self, client):
        response = client.get("/robots.txt")
        assert "Disallow: /admin/" in response.content.decode()
