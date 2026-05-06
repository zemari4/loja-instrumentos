from backend.settings_base import *

DEBUG = True
ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

EMAIL_BACKEND = "django.core.backends.dummy.EmailBackend"
