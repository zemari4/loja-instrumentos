import tablib
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from manager.forms import InstrumentForm, ProductImportForm, StockAdjustmentForm
from manager.mixins import BackstagePermissionMixin
from catalog.models import Brand, Category, Instrument, ProductImage, StockMovement
from catalog.resources import InstrumentResource
from dashboard.services.inventory import LOW_STOCK_THRESHOLD

MAX_PRODUCT_IMAGES = 5


class InventoryListView(BackstagePermissionMixin, ListView):
    template_name = "manager/inventory/list.html"
    context_object_name = "instruments"
    paginate_by = 30

    def get_queryset(self):
        qs = Instrument.objects.select_related("category", "brand").order_by("name")
        category = self.request.GET.get("categoria")
        brand = self.request.GET.get("marca")
        search = self.request.GET.get("q")
        if category:
            qs = qs.filter(category__slug=category)
        if brand:
            qs = qs.filter(brand__slug=brand)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.order_by("name")
        ctx["brands"] = Brand.objects.order_by("name")
        ctx["low_stock_threshold"] = LOW_STOCK_THRESHOLD
        ctx["selected_category"] = self.request.GET.get("categoria", "")
        ctx["selected_brand"] = self.request.GET.get("marca", "")
        ctx["search"] = self.request.GET.get("q", "")
        return ctx


class ProductCreateView(BackstagePermissionMixin, CreateView):
    model = Instrument
    form_class = InstrumentForm
    template_name = "manager/inventory/form.html"
    success_url = reverse_lazy("manager:inventory")

    def form_valid(self, form):
        messages.success(self.request, f'Produto "{form.instance.name}" criado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Novo Produto"
        ctx["submit_label"] = "Criar produto"
        return ctx


class ProductUpdateView(BackstagePermissionMixin, UpdateView):
    model = Instrument
    form_class = InstrumentForm
    template_name = "manager/inventory/form.html"
    success_url = reverse_lazy("manager:inventory")

    def form_valid(self, form):
        messages.success(self.request, f'Produto "{form.instance.name}" atualizado.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = f"Editar — {self.object.name}"
        ctx["submit_label"] = "Salvar alterações"
        return ctx


class ProductDeleteView(BackstagePermissionMixin, DeleteView):
    model = Instrument
    template_name = "manager/inventory/confirm_delete.html"
    success_url = reverse_lazy("manager:inventory")

    def form_valid(self, form):
        messages.success(self.request, f'Produto "{self.object.name}" removido.')
        return super().form_valid(form)


class StockAdjustmentView(BackstagePermissionMixin, View):
    template_name = "manager/inventory/adjust_stock.html"

    def get(self, request, pk):
        instrument = get_object_or_404(Instrument, pk=pk)
        form = StockAdjustmentForm()
        return render(request, self.template_name, {"instrument": instrument, "form": form})

    def post(self, request, pk):
        instrument = get_object_or_404(Instrument, pk=pk)
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data["quantity_change"]
            new_stock = max(0, instrument.stock + qty)
            StockMovement.objects.create(
                instrument=instrument,
                quantity_change=qty,
                movement_type=form.cleaned_data["movement_type"],
                notes=form.cleaned_data.get("notes", ""),
                created_by=request.user,
            )
            instrument.stock = new_stock
            instrument.save(update_fields=["stock", "updated_at"])
            sign = f"+{qty}" if qty >= 0 else str(qty)
            messages.success(request, f"Estoque ajustado ({sign}). Total: {new_stock} unidades.")
            return redirect("manager:inventory")
        return render(request, self.template_name, {"instrument": instrument, "form": form})


class StockHistoryView(BackstagePermissionMixin, ListView):
    template_name = "manager/inventory/stock_history.html"
    context_object_name = "movements"
    paginate_by = 20

    def get_queryset(self):
        self.instrument = get_object_or_404(Instrument, pk=self.kwargs["pk"])
        return StockMovement.objects.filter(
            instrument=self.instrument
        ).select_related("created_by").order_by("-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["instrument"] = self.instrument
        return ctx


class ProductImportView(BackstagePermissionMixin, View):
    template_name = "manager/inventory/import.html"

    def get(self, request):
        form = ProductImportForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProductImportForm(request.POST, request.FILES)
        if form.is_valid():
            import_file = request.FILES["import_file"]
            ext = import_file.name.rsplit(".", 1)[-1].lower()
            resource = InstrumentResource()
            dataset = tablib.Dataset()
            try:
                content = import_file.read()
                if ext == "csv":
                    dataset.csv = content.decode("utf-8")
                elif ext in ("xlsx", "xls"):
                    dataset.xlsx = content
                else:
                    form.add_error("import_file", "Formato não suportado. Use CSV ou XLSX.")
                    return render(request, self.template_name, {"form": form})

                result = resource.import_data(dataset, dry_run=True, raise_errors=False)
                if result.has_errors():
                    row_errors = []
                    for base_err in result.base_errors:
                        row_errors.append(str(base_err.error))
                    for row_num, errors in result.row_errors():
                        for error in errors:
                            row_errors.append(f"Linha {row_num}: {error.error}")
                    return render(request, self.template_name, {"form": form, "row_errors": row_errors})

                resource.import_data(dataset, dry_run=False, raise_errors=True)
                messages.success(request, f"Importação concluída: {result.total_rows} produto(s) processado(s).")
                return redirect("manager:inventory")
            except Exception as exc:
                form.add_error("import_file", f"Erro ao processar arquivo: {exc}")
        return render(request, self.template_name, {"form": form})


class ProductExportView(BackstagePermissionMixin, View):
    def get(self, request):
        resource = InstrumentResource()
        queryset = Instrument.objects.select_related("category", "brand").all()
        dataset = resource.export(queryset)
        fmt = request.GET.get("formato", "xlsx")
        if fmt == "csv":
            response = HttpResponse(dataset.csv, content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = 'attachment; filename="produtos.csv"'
        else:
            response = HttpResponse(
                dataset.xlsx,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = 'attachment; filename="produtos.xlsx"'
        return response


class EditStockView(BackstagePermissionMixin, View):
    def get(self, request, pk):
        instrument = get_object_or_404(Instrument, pk=pk)
        return render(request, "manager/partials/stock_edit_form.html", {"instrument": instrument})


class UpdateStockView(BackstagePermissionMixin, View):
    def _render_cell(self, request, instrument):
        return render(
            request,
            "manager/partials/stock_cell.html",
            {"instrument": instrument, "low_stock_threshold": LOW_STOCK_THRESHOLD},
        )

    def get(self, request, pk):
        instrument = get_object_or_404(Instrument, pk=pk)
        return self._render_cell(request, instrument)

    def post(self, request, pk):
        instrument = get_object_or_404(Instrument, pk=pk)
        try:
            stock = int(request.POST.get("stock", 0))
            if stock < 0:
                raise ValueError("Estoque não pode ser negativo")
            instrument.stock = stock
            instrument.save(update_fields=["stock", "updated_at"])
        except (ValueError, TypeError):
            pass
        return self._render_cell(request, instrument)


class _ImageActionMixin:
    """Mixin para as views de gerenciamento de imagens de produto."""

    def _images_response(self, instrument):
        if self.request.htmx:
            return render(self.request, "manager/partials/product_images.html", {
                "instrument": instrument,
                "images": list(instrument.images.all()),
                "max_images": MAX_PRODUCT_IMAGES,
            })
        return redirect("manager:inventory_update", pk=instrument.pk)

    def _get_image(self, image_pk):
        """Retorna (image, None) ou (None, resposta de erro) se não encontrada."""
        try:
            return ProductImage.objects.select_related("instrument").get(pk=image_pk), None
        except ProductImage.DoesNotExist:
            if self.request.htmx:
                return None, HttpResponse(status=204)
            return None, redirect("manager:inventory_update", pk=0)


class ProductImageUploadView(BackstagePermissionMixin, View):
    def post(self, request, pk):
        instrument = get_object_or_404(Instrument, pk=pk)
        files = request.FILES.getlist("images")
        existing = instrument.images.count()
        slots = MAX_PRODUCT_IMAGES - existing

        if files and slots > 0:
            count = min(len(files), slots)
            for i, f in enumerate(files[:slots]):
                ProductImage.objects.create(
                    instrument=instrument,
                    image=f,
                    is_main=(existing == 0 and i == 0),
                    order=existing + i,
                )
            messages.success(request, f"{count} foto(s) adicionada(s) com sucesso.")
        elif not files:
            messages.error(request, "Nenhuma imagem selecionada.")
        else:
            messages.warning(request, f"Limite de {MAX_PRODUCT_IMAGES} fotos atingido.")

        return redirect("manager:inventory_update", pk=pk)


class ProductImageDeleteView(_ImageActionMixin, BackstagePermissionMixin, View):
    def post(self, request, image_pk):
        image, err = self._get_image(image_pk)
        if err:
            return err
        instrument = image.instrument
        was_main = image.is_main
        image.image.delete(save=False)
        image.delete()
        if was_main:
            first = instrument.images.order_by("order").first()
            if first:
                first.is_main = True
                first.save(update_fields=["is_main"])
        if not request.htmx:
            messages.success(request, "Imagem removida.")
        return self._images_response(instrument)


class ProductImageSetMainView(_ImageActionMixin, BackstagePermissionMixin, View):
    def post(self, request, image_pk):
        image, err = self._get_image(image_pk)
        if err:
            return err
        instrument = image.instrument
        instrument.images.update(is_main=False)
        image.is_main = True
        image.save(update_fields=["is_main"])
        if not request.htmx:
            messages.success(request, "Foto principal atualizada.")
        return self._images_response(instrument)
