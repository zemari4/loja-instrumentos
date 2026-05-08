from django.utils.text import slugify
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from .models import Brand, Category, Instrument


def _unique_slug(model, name):
    base = slugify(name)
    slug = base
    counter = 1
    while model.objects.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


class CategoryGetOrCreateWidget(ForeignKeyWidget):
    def clean(self, value, row=None, **kwargs):
        if not value:
            raise ValueError("Categoria é obrigatória")
        obj, _ = Category.objects.get_or_create(
            name=value,
            defaults={"slug": _unique_slug(Category, value)},
        )
        return obj


class BrandGetOrCreateWidget(ForeignKeyWidget):
    def clean(self, value, row=None, **kwargs):
        if not value:
            raise ValueError("Marca é obrigatória")
        obj, _ = Brand.objects.get_or_create(
            name=value,
            defaults={"slug": _unique_slug(Brand, value)},
        )
        return obj


class InstrumentResource(resources.ModelResource):
    category = fields.Field(
        column_name="categoria",
        attribute="category",
        widget=CategoryGetOrCreateWidget(Category, field="name"),
    )
    brand = fields.Field(
        column_name="marca",
        attribute="brand",
        widget=BrandGetOrCreateWidget(Brand, field="name"),
    )

    class Meta:
        model = Instrument
        fields = (
            "id", "name", "slug", "category", "brand",
            "price", "original_price", "stock",
            "is_active", "is_featured", "description",
        )
        export_order = (
            "id", "name", "category", "brand",
            "price", "original_price", "stock",
            "is_active", "is_featured", "description", "slug",
        )
        import_id_fields = ("id",)
