from django.conf import settings


def site_settings(request):
    return {
        "SITE_NAME": "Music Mais",
        "SITE_TAGLINE": "Sua loja de instrumentos musicais",
        "APP_VERSION": getattr(settings, "APP_VERSION", "0.1.0"),
        "GA_ID": getattr(settings, "GA_ID", None),
        "GTM_ID": getattr(settings, "GTM_ID", None),
    }
