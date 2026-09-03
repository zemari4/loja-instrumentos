from django import forms
from django.utils.text import slugify

from catalog.models import Instrument, ProductImage, StockMovement
from home.models import CarouselSlide, MAX_CAROUSEL_SLIDES


class BRDecimalField(forms.DecimalField):
    """DecimalField que aceita formato brasileiro (4.200,59) e padrão (4200.59)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", forms.TextInput(attrs={"inputmode": "decimal"}))
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, str) and "," in value:
            value = value.replace(".", "").replace(",", ".")
        return super().to_python(value)


class InstrumentForm(forms.ModelForm):
    price = BRDecimalField(max_digits=10, decimal_places=2, label="Preço (R$)")
    original_price = BRDecimalField(
        max_digits=10, decimal_places=2, required=False, label="Preço original (R$)"
    )

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


class ProductImageForm(forms.ModelForm):
    """Valida no servidor cada imagem enviada para um produto.

    A view criava ProductImage direto de request.FILES com objects.create(), que
    não chama full_clean() — nenhuma validação de ImageField chegava a rodar. A
    filtragem por tipo existia só no cliente, e cliente não valida nada.

    Passando por este ModelForm, o forms.ImageField abre o arquivo com Pillow e
    rejeita o que não for imagem de verdade, independente do nome ou do
    content-type declarado pelo navegador.
    """

    MAX_UPLOAD_SIZE = 5 * 1024 * 1024
    EXTENSOES_ACEITAS = {"jpg", "jpeg", "png", "webp"}

    class Meta:
        model = ProductImage
        fields = ["image"]

    def clean_image(self):
        arquivo = self.cleaned_data["image"]

        if arquivo.size > self.MAX_UPLOAD_SIZE:
            limite_mb = self.MAX_UPLOAD_SIZE // (1024 * 1024)
            atual_mb = arquivo.size / (1024 * 1024)
            raise forms.ValidationError(
                f"Imagem de {atual_mb:.1f} MB excede o limite de {limite_mb} MB."
            )

        _, _, extensao = arquivo.name.rpartition(".")
        extensao = extensao.lower()
        if extensao not in self.EXTENSOES_ACEITAS:
            aceitas = ", ".join(sorted(self.EXTENSOES_ACEITAS))
            raise forms.ValidationError(
                f"Extensão .{extensao or '(sem extensão)'} não aceita. Use: {aceitas}."
            )

        return arquivo


class CarouselSlideForm(forms.ModelForm):
    class Meta:
        model = CarouselSlide
        fields = [
            "order", "is_active",
            "image_desktop", "image_mobile",
            "is_launch", "is_promo",
            "title", "subtitle", "text_alignment",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Ex: **Guitarras** até 30% OFF"}),
            "subtitle": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Ex: Os melhores instrumentos das marcas que você ama.",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk:
            if CarouselSlide.objects.count() >= MAX_CAROUSEL_SLIDES:
                raise forms.ValidationError(
                    f"Limite de {MAX_CAROUSEL_SLIDES} slides atingido. "
                    "Remova um slide antes de adicionar outro."
                )
        return cleaned_data
