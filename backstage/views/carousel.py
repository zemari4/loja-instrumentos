from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from backstage.forms import CarouselSlideForm
from backstage.mixins import BackstagePermissionMixin
from home.models import MAX_CAROUSEL_SLIDES, CarouselSlide


class CarouselListView(BackstagePermissionMixin, ListView):
    model = CarouselSlide
    template_name = "backstage/site_config/carousel/list.html"
    context_object_name = "slides"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["max_slides"] = MAX_CAROUSEL_SLIDES
        ctx["can_add"] = CarouselSlide.objects.count() < MAX_CAROUSEL_SLIDES
        return ctx


class CarouselCreateView(BackstagePermissionMixin, CreateView):
    model = CarouselSlide
    form_class = CarouselSlideForm
    template_name = "backstage/site_config/carousel/form.html"
    success_url = reverse_lazy("backstage:carousel_list")

    def get(self, request, *args, **kwargs):
        if CarouselSlide.objects.count() >= MAX_CAROUSEL_SLIDES:
            messages.error(request, f"Limite de {MAX_CAROUSEL_SLIDES} slides atingido.")
            return redirect("backstage:carousel_list")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Slide criado com sucesso.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Novo Slide"
        ctx["submit_label"] = "Criar slide"
        return ctx


class CarouselUpdateView(BackstagePermissionMixin, UpdateView):
    model = CarouselSlide
    form_class = CarouselSlideForm
    template_name = "backstage/site_config/carousel/form.html"
    success_url = reverse_lazy("backstage:carousel_list")

    def form_valid(self, form):
        messages.success(self.request, "Slide atualizado com sucesso.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = f"Editar Slide {self.object.order}"
        ctx["submit_label"] = "Salvar alterações"
        return ctx


class CarouselDeleteView(BackstagePermissionMixin, DeleteView):
    model = CarouselSlide
    template_name = "backstage/site_config/carousel/confirm_delete.html"
    success_url = reverse_lazy("backstage:carousel_list")

    def form_valid(self, form):
        messages.success(self.request, "Slide removido.")
        return super().form_valid(form)
