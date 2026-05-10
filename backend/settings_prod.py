from backend.settings_base import *

DEBUG = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ALLOWED_HOSTS = list(filter(None, [
    env("PRIMARY_HOST", default=None),
    "musicmais.com.br",
    "www.musicmais.com.br",
])) or ["*"]

CSRF_TRUSTED_ORIGINS = list(filter(None, [
    env("PRIMARY_ORIGIN", default=None),
    "https://musicmais.com.br",
]))

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtpout.secureserver.net"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
