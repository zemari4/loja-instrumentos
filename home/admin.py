from django.contrib import admin

from home.models import CarouselSlide


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ["order", "title", "is_active", "is_launch", "is_promo", "text_alignment"]
    list_editable = ["is_active"]
    ordering = ["order"]

