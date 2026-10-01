"""Configuração do Trajetória Ifes.

Um único arquivo. Tudo vem do ambiente, com padrões de desenvolvimento local para que o
projeto rode sem nenhuma variável exportada. Nada lê `.env` automaticamente.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# A chave padrão é fictícia e insegura de propósito: não há ambiente de produção na 001.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insegura-apenas-desenvolvimento-local")
# Sempre False: nenhuma página mostra traceback (008 FR-068, FR-069). Falhas aparecem no
# console pelo logger `django.request`.
DEBUG = False
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]").split(",")
    if host.strip()
]

# Modo de demonstração (008): só "1" ativa. Destinado exclusivamente a ambiente local com
# dados fictícios; desligado, toda página responde 404 (FR-001, FR-002).
TRAJETORIA_DEMONSTRACAO = os.environ.get("TRAJETORIA_DEMONSTRACAO") == "1"

# Apps de domínio, sem admin, auth, sessions, contenttypes, messages ou staticfiles. As
# restrições de não exposição continuam valendo para egressos (001: FR-030, R15; 002: R17;
# 004: R13; 005: FR-058; 006: FR-054; 007: FR-049): a interface da 008 existe só em modo de
# demonstração, com Pessoas da fonte simulada. `demonstracao` é o adaptador temporário que
# faz as vezes da fronteira de identidade e sai quando ela existir.
INSTALLED_APPS = [
    "trajetoria.academico",
    "trajetoria.instrumento",
    "trajetoria.campanha",
    "trajetoria.participacao",
    "trajetoria.interface",
    "trajetoria.demonstracao",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "trajetoria.demonstracao.middleware.ModoDemonstracaoMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["trajetoria.demonstracao.contexto.demonstracao"]},
    }
]

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
    "loggers": {
        "trajetoria": {"handlers": ["console"], "level": "WARNING"},
        # Com DEBUG=False, falhas inesperadas só chegam ao console por aqui (008 R2).
        "django.request": {"handlers": ["console"], "level": "ERROR"},
    },
}
