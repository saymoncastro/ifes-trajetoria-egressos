# Instruções para agentes

Trajetória Ifes: Django 5.2 + PostgreSQL 16, Python 3.13 gerenciado pelo `uv`.

## Subir o ambiente local

Siga **literalmente** [docs/desenvolvimento/ambiente-local.md](docs/desenvolvimento/ambiente-local.md),
do clone aos testes. Não use os quickstarts das features como ponto de partida: eles
validam features isoladas e alguns são anteriores ao modo de demonstração e às chaves.

Fatos que mais travam:

- **Sem `TRAJETORIA_DEMONSTRACAO=1`, toda página responde 404.** É proposital, não é defeito.
- **Nada lê `.env` automaticamente.** Cada chamada de ferramenta abre um shell novo:
  prefixe os comandos `manage.py` com `source .env &&`.
- As chaves do `.env` usadas no `preparar_demonstracao` precisam ser **as mesmas** do
  servidor. Não gere o `.env` de novo sobre um banco já preparado.
- Os testes não precisam de `.env`; precisam de PostgreSQL e de permissão para criar banco.

**Não altere código da aplicação para fazer o ambiente subir.** Se algo falhar, siga a
seção "Se o ambiente não subir" do documento acima.

## Verificações (as mesmas do CI)

```bash
uv run ruff check .
```

```bash
uv run python manage.py check
```

```bash
uv run python manage.py makemigrations --check --dry-run
```

```bash
uv run pytest
```

## Antes de mudar comportamento

- Leia a [Constituição](.specify/memory/constitution.md). Mudança funcional nasce de spec
  (`specs/`). Não invente regra institucional: registre como `DECISÃO PENDENTE`.
- Implantação em servidor: [docs/implantacao/datacenter-ubuntu.md](docs/implantacao/datacenter-ubuntu.md).
