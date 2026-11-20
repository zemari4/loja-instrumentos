from backend.settings_base import *

DEBUG = True

ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://127.0.0.1"]

INSTALLED_APPS += [
    "debug_toolbar",
    "django_browser_reload",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE + [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

# A toolbar expõe configuração, SQL e estado interno. O callback padrão da biblioteca
# só a mostra com DEBUG ligado e quando o IP de origem está em INTERNAL_IPS.
# INTERNAL_IP aceita vários IPs separados por vírgula (ex.: o gateway do Docker).
INTERNAL_IPS = env.list("INTERNAL_IP", default=["127.0.0.1"])

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_COLLAPSED": True,
}
