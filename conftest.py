import os
import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
os.environ.setdefault("DJANGO_ENV", "dev")
os.environ.setdefault("DISABLE_CACHE", "True")
os.environ.setdefault("DISABLE_REDIS", "True")
os.environ.setdefault("ENABLE_S3_STORAGE", "False")
os.environ.setdefault("DISABLE_DEBUG_TOOLBAR", "True")


@pytest.fixture(scope="session")
def django_db_setup():
    pass
