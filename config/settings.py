"""Configuração do Trajetória Ifes.

Um único arquivo. Tudo vem do ambiente, com padrões de desenvolvimento local para que o
projeto rode sem nenhuma variável exportada. Nada lê `.env` automaticamente.
"""

import os
from datetime import timedelta
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
# dados fictícios; desligado, toda página responde 404 (FR-001, FR-002). O editor
# institucional do instrumento (009, `/editor/`) também só existe neste modo não produtivo.
# Esta flag é um interruptor técnico de ambiente, NÃO governança: não autentica nem
# autoriza ninguém. Nela, o operador do editor é escolhido entre operadores fictícios; o que
# ele pode fazer vem só dos vínculos de governança (010). Ninguém publica (002/DP-001).
TRAJETORIA_DEMONSTRACAO = os.environ.get("TRAJETORIA_DEMONSTRACAO") == "1"

# Chave dedicada da pseudonimização analítica das exportações (Feature 013, FR-027): deriva
# `conclusao_analitica_id` e `pessoa_analitica_id` por HMAC-SHA-256. Distinta de SECRET_KEY,
# fora do repositório e sem valor padrão utilizável: vazia, toda exportação é recusada.
# Trocá-la rompe a ligação com exportações anteriores; custódia e rotação em DP-1301.
TRAJETORIA_CHAVE_PSEUDONIMIZACAO = os.environ.get("TRAJETORIA_CHAVE_PSEUDONIMIZACAO", "")

# Apps de domínio, sem admin, auth, contenttypes, messages ou staticfiles. As
# restrições de não exposição continuam valendo para egressos (001: FR-030, R15; 002: R17;
# 004: R13; 005: FR-058; 006: FR-054; 007: FR-049): a interface da 008 existe só em modo de
# demonstração, com Pessoas da fonte simulada. `demonstracao` controla o ambiente fictício;
# `acesso` (018) confirma a Pessoa e mantém sua sessão. `governanca` (010) guarda
# os vínculos CPAEG/CSAEG que autorizam o editor; não é autenticação.
INSTALLED_APPS = [
    "django.contrib.sessions",  # 018 R9: revogação da sessão no servidor.
    "trajetoria.acesso",
    "trajetoria.academico",
    "trajetoria.instrumento",
    "trajetoria.campanha",
    "trajetoria.participacao",
    "trajetoria.governanca",
    "trajetoria.interface",
    "trajetoria.demonstracao",
    "trajetoria.editor",
    "trajetoria.acompanhamento",
    "trajetoria.analitico",
    "trajetoria.comunicacao",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "trajetoria.demonstracao.middleware.ModoDemonstracaoMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
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

TRAJETORIA_URL_ENTRADA_DEMONSTRACAO = os.environ.get(
    "TRAJETORIA_URL_ENTRADA_DEMONSTRACAO", "http://127.0.0.1:8000/acesso/"
)

# Comunicação simulada 016: só configuração SMTP local explícita habilita transporte.
# A operação aplica guards independentes antes de construir qualquer backend.
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "127.0.0.1")
_email_porta = os.environ.get("EMAIL_PORT", "1025")
EMAIL_PORT = int(_email_porta) if _email_porta.isdigit() else -1
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
# Valores não reconhecidos são tratados como ativação e recusados, sem default permissivo.
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "0") not in ("", "0")
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "0") not in ("", "0")
EMAIL_TIMEOUT = 5
DEFAULT_FROM_EMAIL = "trajetoria@example.invalid"
# Sem variável pública de ambiente: locmem só é permitido por override_settings na suíte.
TRAJETORIA_COMUNICACAO_TESTE = False

# 018 R3: segredos independentes; não há valores padrão utilizáveis.
TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO = os.environ.get("TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO", "")
TRAJETORIA_CHAVE_ACESSO_VERIFICACAO = os.environ.get("TRAJETORIA_CHAVE_ACESSO_VERIFICACAO", "")
# 018 R9: inatividade e duração máxima no servidor; cookie termina com o navegador.
TRAJETORIA_SESSAO_INATIVIDADE = timedelta(
    minutes=int(os.environ.get("TRAJETORIA_SESSAO_INATIVIDADE", "30"))
)
TRAJETORIA_SESSAO_DURACAO_MAXIMA = timedelta(
    minutes=int(os.environ.get("TRAJETORIA_SESSAO_DURACAO_MAXIMA", "480"))
)
SESSION_COOKIE_NAME = "trajetoria_sessao_egresso"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = os.environ.get("TRAJETORIA_COOKIE_SEGURO") == "1"
# 018 R8 / DP-1803: cache por processo, exclusivamente demonstração local.
CACHES = {
    nome: {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": nome}
    for nome in ("default", "acesso")
}
TRAJETORIA_ACESSO_LIMITES = {
    "origem": {"livres": 30, "janela": 900},
    "cpf": {"livres": 3, "janela": 3600},
    "espera_base": 5,
    "fator": 3,
    "espera_maxima": 300,
}
