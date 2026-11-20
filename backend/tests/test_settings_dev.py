"""Issue #26: em desenvolvimento, a debug toolbar só aparece para IP interno.

Cada cenário roda num subprocesso porque settings_dev altera listas importadas de
settings_base (INSTALLED_APPS, MIDDLEWARE) ao ser importado, o que contaminaria
os demais testes, e porque INTERNAL_IP é lida na importação.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

SCRIPT = """
import json
import socket

# O toolbar tem um atalho para Docker que resolve host.docker.internal.
# Neutraliza para o resultado não depender da rede.
def _sem_docker(host):
    raise socket.gaierror(host)
socket.gethostbyname = _sem_docker

import django
from django.conf import settings
import backend.settings_dev as dev

settings.configure(**{nome: getattr(dev, nome) for nome in dir(dev) if nome.isupper()})
django.setup()

from debug_toolbar.settings import get_config
from django.test import RequestFactory
from django.utils.module_loading import import_string

# O padrão da biblioteca vem como caminho em texto; o middleware o resolve assim.
callback = get_config()["SHOW_TOOLBAR_CALLBACK"]
if isinstance(callback, str):
    callback = import_string(callback)
rf = RequestFactory()
print(json.dumps({
    "internal_ips": getattr(dev, "INTERNAL_IPS", None),
    "callback_proprio": "SHOW_TOOLBAR_CALLBACK" in dev.DEBUG_TOOLBAR_CONFIG,
    "visivel": {ip: bool(callback(rf.get("/", REMOTE_ADDR=ip))) for ip in ("127.0.0.1", "172.18.0.1", "10.0.0.5")},
}))
"""


def _rodar_settings_dev(internal_ip=None):
    env = {k: v for k, v in os.environ.items() if k not in ("INTERNAL_IP", "DJANGO_SETTINGS_MODULE")}
    if internal_ip is not None:
        env["INTERNAL_IP"] = internal_ip
    saida = subprocess.run([sys.executable, "-c", SCRIPT], cwd=ROOT, env=env, capture_output=True, text=True)
    assert saida.returncode == 0, f"settings_dev não carregou:\n{saida.stderr}"
    return json.loads(saida.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def padrao():
    return _rodar_settings_dev()


@pytest.fixture(scope="module")
def com_dois_ips():
    return _rodar_settings_dev("127.0.0.1,172.18.0.1")


class TestDebugToolbarEmDev:
    def test_internal_ips_default_is_localhost(self, padrao):
        assert padrao["internal_ips"] == ["127.0.0.1"]

    def test_always_true_callback_was_removed(self, padrao):
        assert padrao["callback_proprio"] is False

    def test_shown_for_localhost(self, padrao):
        assert padrao["visivel"]["127.0.0.1"] is True

    def test_hidden_for_other_ips(self, padrao):
        assert padrao["visivel"]["172.18.0.1"] is False
        assert padrao["visivel"]["10.0.0.5"] is False

    def test_internal_ip_env_var_accepts_a_comma_separated_list(self, com_dois_ips):
        assert com_dois_ips["internal_ips"] == ["127.0.0.1", "172.18.0.1"]

    def test_shown_for_ips_from_env_and_hidden_for_the_rest(self, com_dois_ips):
        assert com_dois_ips["visivel"]["172.18.0.1"] is True
        assert com_dois_ips["visivel"]["10.0.0.5"] is False
