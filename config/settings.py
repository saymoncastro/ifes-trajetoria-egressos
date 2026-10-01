"""Configuração do Trajetória Ifes.

Um único arquivo. Tudo vem do ambiente, com padrões de desenvolvimento local para que o
projeto rode sem nenhuma variável exportada. Nada lê `.env` automaticamente.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# A chave padrão é fictícia e insegura de propósito: não há ambiente de produção na 001.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insegura-apenas-desenvolvimento-local")
DEBUG = False
ALLOWED_HOSTS: list[str] = []

# Só os apps de domínio: sem admin, auth, sessions, contenttypes ou messages (001: FR-030,
# R15; 002: R17 — nenhuma interface expõe edição ou publicação do instrumento).
INSTALLED_APPS = ["trajetoria.academico", "trajetoria.instrumento"]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# Valores vazios deixam o libpq usar seus padrões (socket local, usuário do sistema).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PGDATABASE", "trajetoria"),
        "HOST": os.environ.get("PGHOST", ""),
        "PORT": os.environ.get("PGPORT", ""),
        "USER": os.environ.get("PGUSER", ""),
        "PASSWORD": os.environ.get("PGPASSWORD", ""),
    }
}

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"trajetoria": {"handlers": ["console"], "level": "WARNING"}},
}
