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

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    "SHOW_COLLAPSED": True,
}
