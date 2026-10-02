"""Dependências de produção aprovadas, numa lista só para todos os testes de fronteira.

Cada feature protege a regra "não acrescentar dependência" comparando `pyproject.toml` com
esta lista. Uma dependência nova entra aqui, uma vez, com a feature e a justificativa.
"""

DEPENDENCIAS_APROVADAS = [
    "Django>=5.2,<5.3",
    "psycopg[binary]>=3.2,<3.4",
    "XlsxWriter>=3.2,<4",  # Feature 013: escrita de XLSX (research R11)
]
