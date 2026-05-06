from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("carrinho/", views.CartView.as_view(), name="cart"),
    path("carrinho/adicionar/<int:pk>/", views.AddToCartView.as_view(), name="add"),
    path("carrinho/remover/<int:pk>/", views.RemoveFromCartView.as_view(), name="remove"),
    path("carrinho/atualizar/<int:pk>/", views.UpdateCartView.as_view(), name="update"),
]
