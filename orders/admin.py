from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("get_subtotal",)

    @admin.display(description="Subtotal")
    def get_subtotal(self, obj):
        return obj.subtotal


@admin.register(Order)
class OrderAdmin(SimpleHistoryAdmin):
    list_display = ("id", "customer", "status", "total_price", "created_at")
    list_filter = ("status",)
    search_fields = ("customer__username", "customer__email")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    list_display = ("id", "order", "status", "method", "amount", "paid_at")
    list_filter = ("status", "method")
    readonly_fields = ("created_at",)
