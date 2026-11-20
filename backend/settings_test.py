from backend.settings_base import *

DEBUG = True
ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]
FIELD_ENCRYPTION_KEY = "XisV3giLTCZ3mTPzRMRT5zgMIjiADVRY38fU8iYwdfE="

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "allauth.socialaccount.providers.google"]

# Redis real também nos testes, no banco 15 para não tocar nos dados de desenvolvimento.
CACHES = {
    "default": {
        **CACHES["default"],
        "LOCATION": env("TEST_CACHE_LOCATION", default="redis://127.0.0.1:6379/15"),
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

EMAIL_BACKEND = "django.core.backends.dummy.EmailBackend"
