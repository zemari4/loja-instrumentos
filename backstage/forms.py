from django import forms
from django.utils.text import slugify

from catalog.models import Instrument, StockMovement


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = Instrument
        fields = [
            "category", "brand", "name", "slug", "description",
            "price", "original_price", "stock",
            "is_active", "is_featured",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "slug": forms.TextInput(attrs={"placeholder": "Deixe em branco para gerar automaticamente"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        if not slug:
            name = self.cleaned_data.get("name", "")
            slug = slugify(name)
        return slug


class StockAdjustmentForm(forms.Form):
    quantity_change = forms.IntegerField(
        label="Quantidade",
        help_text="Use valores negativos para reduzir o estoque",
    )
    movement_type = forms.ChoiceField(
        label="Tipo de movimentação",
        choices=StockMovement.Type.choices,
    )
    notes = forms.CharField(
        label="Observações",
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Motivo, nota fiscal, referência…"}),
    )


class ProductImportForm(forms.Form):
    import_file = forms.FileField(
        label="Arquivo CSV ou XLSX",
        help_text="Formatos aceitos: .csv, .xlsx",
    )
