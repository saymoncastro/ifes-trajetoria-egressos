# Quickstart: validar a Feature 007

Guia para comprovar, de ponta a ponta, que a feature atende a spec. Pré-requisitos, banco
e variáveis são os mesmos da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos):
`uv`, PostgreSQL 16+ local e nenhuma variável obrigatória.

> **Somente dados fictícios.** 001/DP-009 e 005/DP-504 continuam bloqueando o uso com
> egressos reais. A 007 não identifica nem autentica ninguém: recebe uma Pessoa já
> resolvida e não é exposta por URL, view ou API.

## Preparar

```bash
uv sync --extra dev
```

```bash
uv run python manage.py migrate
```

A 007 **não tem migração**. O comando abaixo deve continuar sem nada a gerar:

```bash
uv run python manage.py makemigrations --check --dry-run
```

## Validar

Suíte completa, incluindo 001 a 006, que devem continuar passando **sem nenhuma alteração
em testes existentes** ([research R14](research.md#r14--testes-existentes-da-005006)):

```bash
uv run pytest
```

Só a entrada:

```bash
uv run pytest tests/participacao -k entrada
```

```bash
uv run ruff check .
```

| Arquivo de teste | O que comprova | Spec |
|------------------|----------------|------|
| `tests/participacao/test_entrada_situacao.py` | Formações da Pessoa com contexto lido da Conclusão e `None` preservado; ordem determinística; cinco situações por formação; resolução global por tabela (sem banco) e de ponta a ponta; concluídas e ambíguas informadas mas não contadas; ambiguidade local sem consultar Participação; Campanha EM PREPARAÇÃO/ENCERRADA e último dia do período; consulta não grava; no máximo 3 + N consultas | US1, US2, US3.1–3.4, US4.1–4.2, US7.1, US7.5, US9, US10.1, US10.4–10.5, FR-006–FR-027a, SC-002, SC-003a, SC-008, SC-012 |
| `tests/participacao/test_entrada_entrar.py` | casos S-A a S-L do solicitante (abaixo); entrada com formação informada em cada situação; formação de outra Pessoa rejeitada sem dados alheios; Pessoa/Conclusão não gravada → erro de uso; reavaliação no momento da entrada; Participação concluída entre a avaliação e o início → devolvida concluída; entrada repetida N vezes → uma Participação; nenhuma `Resposta` criada | US3–US8, US10.2–10.3, US11, FR-029–FR-046, SC-001, SC-003–SC-007, SC-009 |
| `tests/participacao/test_entrada_aceitacao.py` | As 12 perguntas de sucesso, ponta a ponta; zero modelos e migrações novos; app `participacao` com os mesmos três modelos; `entrada.py` não grava modelo diretamente, não importa percurso/jornada, fonte acadêmica, auth, sessão ou views; nenhum nome proibido; `operacoes.__all__` e `consultas.__all__` inalterados | FR-047–FR-053, SC-010, SC-011 |

### Casos S-A a S-L do solicitante

(Rótulos distintos dos "Casos de referência" A–O da spec; correspondência nas Notes do [tasks.md](tasks.md#notes).)

| Caso | Montagem | Esperado |
|------|----------|----------|
| S-A | 1 formação, sem Participação | `ENTRADA_RESOLVIDA`; `entrar(pessoa)` → Participação nova, `criada` |
| S-B | 1 formação, rascunho | `ENTRADA_RESOLVIDA`; `entrar(pessoa)` → mesma Participação, não `criada` |
| S-C | 1 formação, concluída | `SEM_ENTRADA_PENDENTE`; `entrar(pessoa)` → sem Participação; informando a formação → a concluída, inalterada |
| S-D | A concluída, B rascunho | `ENTRADA_RESOLVIDA` para B; A informada como `JA_CONCLUIDA`; `entrar(pessoa)` → rascunho de B |
| S-E | A concluída, B sem Participação | `ENTRADA_RESOLVIDA` para B; `entrar(pessoa)` → Participação nova de B |
| S-F | A e B em rascunho/sem Participação | `SELECAO_NECESSARIA`; `entrar(pessoa)` → sem Participação, nada criado |
| S-G | várias formações, nenhuma Campanha | `SEM_PESQUISA`; nada criado |
| S-H | Pessoa sem Conclusões | `SEM_FORMACAO`; nada criado |
| S-I | duas Campanhas para a mesma Conclusão (com e sem Participação numa delas) | formação `AMBIGUIDADE_OPERACIONAL` com as duas Campanhas; nada criado nem retomado |
| S-J | formação de outra Pessoa informada | `FormacaoDeOutraPessoa`; nada criado |
| S-K | Participação concluída em Campanha encerrada; nova Campanha aberta depois | `DISPONIVEL_PARA_INICIAR` pela nova; `entrar` → Participação nova; a anterior intacta |
| S-L | qualquer entrada | 0 Respostas; Q10–Q19 sem resposta; nada da Conclusão copiado |

Resultado esperado: todos os testes passam, sem rede e sem depender do relógio real; os
testes de 001 a 006 não foram tocados.

## Exploração manual (opcional)

No shell do Django, com o banco de desenvolvimento migrado e a fonte simulada incorporada
(quickstart da 001), é possível observar uma situação de entrada:

```bash
uv run python manage.py shell
```

Dentro do shell, obter uma `Pessoa` dos cenários simulados e chamar
`trajetoria.participacao.entrada.situacao_de_entrada(pessoa)`. Sem Campanha EM COLETA, a
resolução é `SEM_PESQUISA`. Nada é gravado.
