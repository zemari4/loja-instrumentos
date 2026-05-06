from django.urls import path

from .views import CategoryView, InstrumentDetailView, InstrumentListView

app_name = "catalog"

urlpatterns = [
    path("produtos", InstrumentListView.as_view(), name="list"),
    path("busca", InstrumentListView.as_view(), name="search"),
    path("produto/<slug:slug>", InstrumentDetailView.as_view(), name="detail"),
    path("categoria/<slug:slug>", CategoryView.as_view(), name="category"),
]
