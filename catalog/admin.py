from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Brand, Category, Instrument, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "parent", "order"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "is_main", "order"]


@admin.register(Instrument)
class InstrumentAdmin(SimpleHistoryAdmin):
    list_display = ["name", "brand", "category", "price", "stock", "is_active", "is_featured", "views_count"]
    list_filter = ["is_active", "is_featured", "category", "brand"]
    list_editable = ["is_active", "is_featured", "stock"]
    search_fields = ["name", "brand__name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["views_count", "created_at", "updated_at"]
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {"fields": ("category", "brand", "name", "slug", "description")}),
        ("Preço e Estoque", {"fields": ("price", "original_price", "stock")}),
        ("Visibilidade", {"fields": ("is_active", "is_featured")}),
        ("Métricas", {"fields": ("views_count", "created_at", "updated_at")}),
    )
