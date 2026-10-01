# Quickstart: validar a Feature 001

Guia para comprovar, de ponta a ponta, que a feature atende a spec. Não exige acesso a
nenhum sistema acadêmico real (SC-007).

## Pré-requisitos

- `uv` instalado. O Python 3.13 é provisionado pelo próprio `uv`.
- PostgreSQL 16 ou superior acessível localmente, com um usuário que possa criar bancos
  (o pytest cria o banco de teste).
- Sem nenhuma variável, a aplicação usa o banco `trajetoria` no PostgreSQL local, por
  socket e com o usuário do sistema operacional.
- Para outro servidor, **exporte no shell** as variáveis padrão do PostgreSQL (`PGHOST`,
  `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`). Nada lê `.env` automaticamente; o
  `.env.example` só lista as variáveis. Nenhum segredo é versionado.
- O banco `trajetoria` precisa existir para `migrate` (`createdb trajetoria`). O banco
  de teste é criado pelo pytest.

## Preparar

```bash
uv sync --extra dev
```

```bash
uv run python manage.py migrate
```

## Validar

Suíte completa:

```bash
uv run pytest
```

Lint:

```bash
uv run ruff check .
```

| Arquivo de teste | O que comprova | Spec |
|------------------|----------------|------|
| `tests/test_contrato_fonte.py` | Contrato da fronteira, executado contra a fonte simulada **e** a implementação alternativa | FR-021–FR-025, SC-006 |
| `tests/test_fonte_simulada.py` | Cada cenário do [catálogo](contracts/cenarios-simulados.md) devolve o resultado declarado; determinismo; dados fictícios | FR-026–FR-029, SC-001, SC-009 |
| `tests/test_modelo.py` | Restrições do [modelo](data-model.md): unicidade, cadeia vazia, ano × data, `PROTECT`, ausência de atributos acadêmicos na Pessoa | FR-003, FR-010, FR-011 |
| `tests/test_incorporacao.py` | Idempotência, não materialização de pessoa sem conclusão, divergências sem sobrescrita, falha sem efeito, proveniência, homônimos, pessoa sem nome | FR-031–FR-039, SC-003–SC-005 |
| `tests/test_aceitacao.py` | US3: contextos sem mistura na Pessoa com 3 conclusões (SIM-P-0004), contexto isolado de uma conclusão, ordem estável e consumidor de demonstração da "experiência esperada" (SIM-P-0003). As demais histórias estão em `test_incorporacao.py` | SC-002, SC-008 |

Resultado esperado: todos os testes passam, com zero acesso à rede.

## Ver a trajetória da "experiência esperada"

Demonstração interativa no banco de desenvolvimento:

```bash
uv run python manage.py shell
```

No shell, importe `incorporar_pessoa` e a fonte simulada e incorpore `SIM-P-0003`.
Depois, percorra `resultado.pessoa.conclusoes`. Devem aparecer duas conclusões: TADS no
Campus Serra (Graduação, Presencial, 2022) e Especialização em Informática na Educação
no Cefor (Pós-graduação, A distância, 2025). Cada uma tem `fonte = "simulada"` e seu
`id_externo`. Repetir a incorporação não cria linhas.
