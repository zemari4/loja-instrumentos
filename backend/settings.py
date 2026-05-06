import os

env = os.environ.get("DJANGO_ENV", "dev")

if env == "prod":
    from backend.settings_prod import *
else:
    from backend.settings_dev import *
