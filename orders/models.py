from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendente"),
        (STATUS_PAID, "Pago"),
        (STATUS_SHIPPED, "Enviado"),
        (STATUS_DELIVERED, "Entregue"),
        (STATUS_CANCELLED, "Cancelado"),
    ]

    STATUS_CSS = {
        STATUS_PENDING: "bg-yellow-100 text-yellow-800",
        STATUS_PAID: "bg-blue-100 text-blue-800",
        STATUS_SHIPPED: "bg-purple-100 text-purple-800",
        STATUS_DELIVERED: "bg-green-100 text-green-800",
        STATUS_CANCELLED: "bg-red-100 text-red-800",
    }

    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pedido #{self.pk} — {self.customer.username}"

    @property
    def status_css(self):
        return self.STATUS_CSS.get(self.status, "bg-gray-100 text-gray-800")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    instrument = models.ForeignKey(
        "catalog.Instrument", on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"

    def __str__(self):
        return f"{self.quantity}x {self.instrument.name}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("approved", "Aprovado"),
        ("rejected", "Rejeitado"),
        ("refunded", "Reembolsado"),
    ]

    METHOD_CHOICES = [
        ("credit_card", "Cartão de Crédito"),
        ("pix", "PIX"),
        ("boleto", "Boleto"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    gateway_reference = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"

    def __str__(self):
        return f"Pagamento do Pedido #{self.order_id}"
