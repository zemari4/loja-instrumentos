from django.db import models

MAX_CAROUSEL_SLIDES = 3


class CarouselSlide(models.Model):
    class TextAlignment(models.TextChoices):
        LEFT = "left", "Esquerda"
        CENTER = "center", "Centro"
        RIGHT = "right", "Direita"

    order = models.PositiveSmallIntegerField(
        verbose_name="Posição",
        choices=[(1, "1º slide"), (2, "2º slide"), (3, "3º slide")],
        unique=True,
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    image_desktop = models.ImageField(
        upload_to="carousel/desktop/",
        null=True,
        blank=True,
        verbose_name="Imagem desktop",
        help_text="Tamanho recomendado: 1440 × 400 px (proporção 16:4)",
    )
    image_mobile = models.ImageField(
        upload_to="carousel/mobile/",
        null=True,
        blank=True,
        verbose_name="Imagem mobile",
        help_text="Tamanho recomendado: 640 × 400 px (proporção 8:5)",
    )

    is_launch = models.BooleanField(default=False, verbose_name="Marcador Lançamento")
    is_promo = models.BooleanField(default=False, verbose_name="Marcador Promoção")

    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título",
        help_text="Texto grande. Aceita markdown: **negrito**, *itálico*",
    )
    subtitle = models.TextField(
        blank=True,
        verbose_name="Subtítulo",
        help_text="Texto abaixo do título. Aceita markdown: **negrito**, *itálico*",
    )
    text_alignment = models.CharField(
        max_length=10,
        choices=TextAlignment.choices,
        default=TextAlignment.LEFT,
        verbose_name="Posição do texto",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Slide do Carrossel"
        verbose_name_plural = "Slides do Carrossel"

    def __str__(self):
        return f"Slide {self.order}: {self.title or 'Sem título'}"
