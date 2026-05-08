from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("backstage/", include("backstage.urls", namespace="backstage")),
    path("", include("home.urls")),
    path("", include("authentification.urls")),
    path("", include("catalog.urls")),
    path("", include("cart.urls")),
    path("", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns = [path("__debug__/", include("debug_toolbar.urls"))] + urlpatterns

if "django_browser_reload" in settings.INSTALLED_APPS:
    urlpatterns = [path("__reload__/", include("django_browser_reload.urls"))] + urlpatterns
