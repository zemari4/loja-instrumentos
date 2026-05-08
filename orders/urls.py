from django.urls import path

from .views import CheckoutView, OrderConfirmView, OrderDetailView, OrderListView

app_name = "orders"

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("pedido/<int:pk>/confirmacao/", OrderConfirmView.as_view(), name="order_confirm"),
    path("minha-conta/pedidos/", OrderListView.as_view(), name="order_list"),
    path("minha-conta/pedidos/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
]
