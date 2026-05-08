from django.urls import path

from .views.analytics import AnalyticsView
from .views.customers import CustomerListView
from .views.dashboard import (
    DashboardView,
    MostViewedTableView,
    RecentOrdersTableView,
    TopProductsTableView,
)
from .views.orders import OrderDetailView, OrderListView, UpdateOrderStatusView
from .views.products import (
    EditStockView,
    InventoryListView,
    ProductCreateView,
    ProductDeleteView,
    ProductExportView,
    ProductImportView,
    ProductUpdateView,
    StockAdjustmentView,
    StockHistoryView,
    UpdateStockView,
)

app_name = "backstage"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    # HTMX partials — dashboard
    path("_tabelas/pedidos-recentes/", RecentOrdersTableView.as_view(), name="recent_orders_table"),
    path("_tabelas/top-produtos/", TopProductsTableView.as_view(), name="top_products_table"),
    path("_tabelas/mais-vistos/", MostViewedTableView.as_view(), name="most_viewed_table"),
    # Estoque — lista e inline HTMX
    path("estoque/", InventoryListView.as_view(), name="inventory"),
    path("estoque/<int:pk>/editar/", EditStockView.as_view(), name="edit_stock"),
    path("estoque/<int:pk>/atualizar/", UpdateStockView.as_view(), name="update_stock"),
    # Estoque — CRUD completo
    path("estoque/novo/", ProductCreateView.as_view(), name="inventory_create"),
    path("estoque/<int:pk>/produto/", ProductUpdateView.as_view(), name="inventory_update"),
    path("estoque/<int:pk>/excluir/", ProductDeleteView.as_view(), name="inventory_delete"),
    path("estoque/<int:pk>/ajustar/", StockAdjustmentView.as_view(), name="stock_adjust"),
    path("estoque/<int:pk>/historico/", StockHistoryView.as_view(), name="stock_history"),
    path("estoque/importar/", ProductImportView.as_view(), name="inventory_import"),
    path("estoque/exportar/", ProductExportView.as_view(), name="inventory_export"),
    # Pedidos
    path("pedidos/", OrderListView.as_view(), name="orders"),
    path("pedidos/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("pedidos/<int:pk>/status/", UpdateOrderStatusView.as_view(), name="update_order_status"),
    # Clientes
    path("clientes/", CustomerListView.as_view(), name="customers"),
    # Analytics
    path("analytics/", AnalyticsView.as_view(), name="analytics"),
]
