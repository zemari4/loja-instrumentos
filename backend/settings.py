import os
from pathlib import Path


def _load_env():
    env_file = Path(__file__).resolve().parent.parent / ".env"
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key:
                    os.environ.setdefault(key, val)
    except FileNotFoundError:
        pass


_load_env()

_env = os.environ.get("DJANGO_ENV", "dev")

if _env == "prod":
    from backend.settings_prod import *
else:
    from backend.settings_dev import *
