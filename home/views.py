from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from home.models import CarouselSlide


class HomeView(View):
    def get(self, request):
        from catalog.services import get_most_viewed
        cart = request.session.get("cart", {})
        ctx = {
            "cart_count": sum(item.get("qty", 0) for item in cart.values()),
            "featured_products": get_most_viewed(6),
            "carousel_slides": CarouselSlide.objects.filter(is_active=True).order_by("order"),
        }
        return render(request, "home/index.html", ctx)


class RobotsTxtView(View):
    def get(self, request):
        lines = [
            "User-agent: *",
            "Disallow: /admin/",
            "Disallow: /manager/",
            "Disallow: /api/",
            f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        ]
        return HttpResponse("\n".join(lines), content_type="text/plain")


def page_not_found(request, exception=None):
    return render(request, "errors/404.html", status=404)


def server_error(request):
    return render(request, "errors/500.html", status=500)


def permission_denied(request, exception=None):
    return render(request, "errors/403.html", status=403)
