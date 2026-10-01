# Quickstart: validar a Feature 003

Guia para comprovar que a baseline do Formulário Egresso Ifes 2024 é materializada com
fidelidade, em RASCUNHO e de forma idempotente. Pré-requisitos, banco e variáveis são os
mesmos da [Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos):
`uv`, PostgreSQL 16+ local e nenhuma variável obrigatória.

## Preparar

```bash
uv sync --extra dev
```

```bash
uv run python manage.py migrate
```

Nenhuma migração nova: a feature não altera modelos. Para confirmar:

```bash
uv run python manage.py makemigrations --check --dry-run
```

## Validar

Suíte completa; as das Features 001 e 002 devem continuar passando sem alteração:

```bash
uv run pytest
```

Só esta feature:

```bash
uv run pytest tests/instrumento -k formulario_2024
```

Lint:

```bash
uv run ruff check .
```

| Arquivo de teste | O que comprova | Spec |
|------------------|----------------|------|
| `tests/instrumento/test_formulario_2024_fidelidade.py` | Textos, Seções, 54 Perguntas (Qn pela ordem), tipos, obrigatoriedades, 385 Opções em ordem, listas extensas (quantidade, extremidades e sequência documentada no inventário), escalas, textos explicativos, complementos, correção E-08, ausência das notas E-05/E-06, preservações de US9, contagens | US2, US5, US6, US7, US9; FR-007–FR-021, FR-027–FR-030, FR-038, FR-039 |
| `tests/instrumento/test_formulario_2024_navegacao.py` | 10 regras, 7 encaminhamentos, Q51 sem regra, Q1 = "Não" finaliza, Q46–Q48 em S11, 17 percursos, completude da 002 sem publicar | US1 (cenário 3), US4; FR-006, FR-022–FR-026 |
| `tests/instrumento/test_formulario_2024_materializacao.py` | Criação em RASCUNHO, reexecução sem alteração, divergência sem alteração, Pesquisa reutilizada ou ambígua, atomicidade, baseline publicada, nada na 001, nenhum modelo ou migração novos | US1, US8; FR-001–FR-005, FR-031–FR-034, FR-040–FR-042 |

## Materializar em um ambiente

A 002 não oferece exclusão de Versão: num banco de desenvolvimento, a baseline criada
permanece. Para só experimentar, use um banco descartável (`createdb`/`dropdb` com
`PGDATABASE`).

A operação é explícita; nada a executa no `migrate` ([research R1, R12](research.md#r1--mecanismo-de-materialização)).

```bash
uv run python manage.py shell -c "from trajetoria.formulario_2024 import materializar; print(materializar())"
```

Resultado esperado:

- primeira execução: `Resultado(…, criada=True)`; a Versão "Formulário Egresso Ifes 2024 —
  referência migrada" existe em RASCUNHO;
- execuções seguintes: `Resultado(…, criada=False)`; nada é alterado;
- se a baseline existente tiver sido editada: `BaselineDivergente` com o local da primeira
  diferença; nada é alterado. A divergência exige análise humana.

A operação nunca publica a Versão (002/DP-001).

## Inspecionar

Contagens rápidas de uma baseline já materializada. O comando só lê: procura a Versão pelo
nome da Pesquisa e pela designação, sem chamar `materializar()` (que criaria a baseline
se ela não existisse):

```bash
uv run python manage.py shell -c "from trajetoria.formulario_2024.declaracao import DESIGNACAO, NOME_PESQUISA; from trajetoria.instrumento.models import Versao; from trajetoria.instrumento.conteudo import conteudo_da_versao; c = conteudo_da_versao(Versao.objects.get(pesquisa__nome=NOME_PESQUISA, designacao=DESIGNACAO)); print(c.estado, len(c.secoes), sum(len(s.perguntas) for s in c.secoes), sum(len(p.opcoes) for s in c.secoes for p in s.perguntas))"
```

Esperado: `RASCUNHO 13 54 385`.

Para auditar uma pergunta, parta da linha Qn da
[Matriz de Migração](spec.md#matriz-de-migração-q1q54), localize a mesma chave em
`trajetoria/formulario_2024/declaracao.py` e a verificação correspondente nos testes.
