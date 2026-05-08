"""
Base settings para Music Mais — projeto local de estudo.
Simples, sem infraestrutura de produção (sem Celery, Redis, S3, Sentry).
"""
import logging
import os
import tomllib
import warnings
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    DJANGO_ENV=(str, "dev"),
    PRIMARY_HOST=(str, "*"),
    PRIMARY_ORIGIN=(str, None),
    BASE_URL=(str, "http://localhost:8000"),
    SECRET_KEY=(str, "change-me"),
    DATABASE_URL=(str, None),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    EMAIL_HOST_USER=(str, None),
    EMAIL_HOST_PASSWORD=(str, None),
    GA_ID=(str, None),
    GTM_ID=(str, None),
    ANTHROPIC_API_KEY=(str, None),
)


def _load_dotenv(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key:
                    os.environ.setdefault(key, val)
    except FileNotFoundError:
        pass


_load_dotenv(os.path.join(BASE_DIR, ".env"))

# Versão do projeto
with open(BASE_DIR / "pyproject.toml", "rb") as _f:
    APP_VERSION = tomllib.load(_f)["project"]["version"]

BASE_URL = env("BASE_URL")
SECRET_KEY = env("SECRET_KEY")
DEBUG = False  # sobrescrito nos settings_dev/prod

_env_hosts = env.list("ALLOWED_HOSTS", default=[])
ALLOWED_HOSTS = _env_hosts if _env_hosts else [env("PRIMARY_HOST", default="*")]

_env_csrf = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = _env_csrf if _env_csrf else list(filter(None, [
    env("PRIMARY_ORIGIN", default=None)
]))

GA_ID = env("GA_ID", default=None)
GTM_ID = env("GTM_ID", default=None)

# ── LOGGING ──────────────────────────────────────────────────────────────────

class ColorFormatter(logging.Formatter):
    RESET = "\033[0m"
    COLORS = {
        "DEBUG": "\033[36m", "INFO": "\033[32m",
        "WARNING": "\033[33m", "ERROR": "\033[31m", "CRITICAL": "\033[1;31m",
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        self._style._fmt = f"{color}{fmt}{self.RESET}"
        return super().format(record)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "color": {"()": ColorFormatter},
        "simple": {"format": "%(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "color"},
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "": {"handlers": ["console"], "level": "INFO"},
    },
}

# ── APPS ─────────────────────────────────────────────────────────────────────

DJANGO_APPS = [
    "jazzmin",
    "colorfield",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
]

THIRD_PARTY_APPS = [
    "django_htmx",
    "crispy_forms",
    "crispy_tailwind",
    "django_extensions",
    "django_filters",
    "django_user_agents",
    "simple_history",
    "tailwind",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "django_ratelimit",
    "markdownify",
    "import_export",
]

LOCAL_APPS = [
    "backend",
    "theme",
    "musicmaisCSS",
    "home",
    "authentification",
    "analytics",
    "catalog",
    "cart",
    "orders",
    "dashboard",
    "backstage",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ── MIDDLEWARE ────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "analytics.middleware.AttachRequestLogContext",
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

# ── TEMPLATES ─────────────────────────────────────────────────────────────────

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "backend.context_processors.site_settings",
                "cart.context_processors.cart",
            ],
        },
    },
]

SITE_ID = 1
WSGI_APPLICATION = "backend.wsgi.application"

# ── DATABASE ──────────────────────────────────────────────────────────────────

if env.str("DATABASE_URL", default=None):
    import dj_database_url
    DATABASES = {"default": dj_database_url.parse(env("DATABASE_URL"), conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── CACHE (local memory — sem Redis) ─────────────────────────────────────────

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "musicmais",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.db"

# ── RATELIMIT ────────────────────────────────────────────────────────────────

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = "default"
SILENCED_SYSTEM_CHECKS = ["security.W019", "django_ratelimit.W001", "django_ratelimit.E003"]

# ── AUTH / ALLAUTH ────────────────────────────────────────────────────────────

LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/usuario/entrar"
LOGIN_REDIRECT_URL = "/"
SOCIALACCOUNT_AUTO_SIGNUP = False

# ── FORMS ─────────────────────────────────────────────────────────────────────

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

MARKDOWNIFY = {
    "default": {
        "BLEACH": True,
        "STRIP": False,
        "WHITELIST_TAGS": [
            "a", "b", "blockquote", "code", "em", "i", "li", "ol", "p",
            "pre", "br", "strong", "ul", "h1", "h2", "h3", "h4",
        ],
        "WHITELIST_ATTRS": {"a": ["href", "title"]},
        "WHITELIST_PROTOCOLS": ["http", "https"],
        "MARKDOWN_EXTENSIONS": ["fenced_code", "tables", "nl2br"],
    }
}

# ── ADMIN (Jazzmin) ───────────────────────────────────────────────────────────

JAZZMIN_SETTINGS = {
    "site_title": "Music Mais Admin",
    "site_header": "Music Mais",
    "site_brand": "Music Mais",
    "welcome_sign": "Bem-vindo ao painel do Music Mais",
    "copyright": "Music Mais",
    "search_model": ["auth.User", "catalog.Instrument"],
    "topmenu_links": [
        {"name": "Loja", "url": "/", "icon": "fas fa-store"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
        "authentification": "fas fa-sign-in-alt",
        "catalog": "fas fa-guitar",
        "catalog.Instrument": "fas fa-guitar",
        "catalog.Category": "fas fa-tags",
        "catalog.Brand": "fas fa-trademark",
        "orders": "fas fa-shopping-bag",
        "orders.Order": "fas fa-receipt",
        "cart": "fas fa-shopping-cart",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_flat_style": True,
    "theme": "default",
    "default_theme_mode": "light",
    "actions_sticky_top": True,
}

# ── STATIC / MEDIA ────────────────────────────────────────────────────────────

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ── EMAIL (console em dev) ────────────────────────────────────────────────────

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default=None)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or "musicmais@localhost"

# ── TAILWIND ──────────────────────────────────────────────────────────────────

TAILWIND_APP_NAME = "musicmaisCSS"
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"

# ── I18N / TZ ─────────────────────────────────────────────────────────────────

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ── MISC ──────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
X_FRAME_OPTIONS = "SAMEORIGIN"

ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default=None)

warnings.filterwarnings("ignore", message="Invalid line.*")
