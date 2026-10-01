# Quickstart: validar a Feature 006

Guia para comprovar, de ponta a ponta, que a feature atende a spec. Pré-requisitos, banco
e variáveis são os mesmos da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos):
`uv`, PostgreSQL 16+ local e nenhuma variável obrigatória.

> **Somente dados fictícios.** 005/DP-504 (base legal e consentimento) continua bloqueando
> o uso com egressos reais. Q1 = "Não" finaliza a jornada, mas não é registro de
> consentimento ou de recusa jurídica.

## Preparar

```bash
uv sync --extra dev
```

```bash
uv run python manage.py migrate
```

A migração `participacao.0002_participacao_concluida_em` acrescenta só a coluna anulável
`concluida_em`. Participações existentes ficam em rascunho. Nenhuma tabela nova.

```bash
uv run python manage.py makemigrations --check --dry-run
```

## Validar

Suíte completa, incluindo 001 a 005, que devem continuar passando (quatro asserções de
fronteira da 005 são ajustadas, como previsto por 005 FR-056 —
[research R16](research.md#r16--testes-de-fronteira-da-005-que-proíbem-a-conclusão)):

```bash
uv run pytest
```

Só a jornada:

```bash
uv run pytest tests/participacao -k jornada
```

```bash
uv run ruff check .
```

| Arquivo de teste | O que comprova | Spec |
|------------------|----------------|------|
| `tests/participacao/test_jornada_modelo.py` | `concluida_em` anulável, nulo ao iniciar; migração `0002` com um único `AddField`, sem backfill | FR-001, FR-002 |
| `tests/participacao/test_jornada_percurso.py` | `percorrer` puro, **sem banco** (Versões mínimas construídas em memória): linear; encaminhamento; regra para Seção; regra de finalização; última Seção finaliza; Pergunta com regra opcional sem resposta segue o padrão; obrigatória sem resposta → `INDETERMINADA`; pendências só da Seção atual; respostas fora do percurso ignoradas; determinismo; duas Perguntas com regra na mesma Seção → `ESTRUTURA_NAO_SUPORTADA` | US1–US3, US12, FR-010–FR-021 |
| `tests/participacao/test_jornada_baseline.py` | Sobre a baseline: 17 percursos do oráculo `PERCURSOS` da 003; Q1 Sim/Não; quatro destinos de Q14; Q33 Sim/Não; Q46 Sim/Não; Q46–Q48 juntas em S11, Q47 pendente com Q46 = "Não", Q48 nunca pendente; Q51 sem regra, saída de S12 pelo encaminhamento | US4, US5, US10, FR-022–FR-027, SC-001, SC-002 |
| `tests/participacao/test_jornada_situacao.py` | `situacao_da_jornada`: percurso parcial com destino indeterminado; Seção atual com destino já conhecido; retomada reproduz o percurso; troca de ramo mantém respostas antigas como fora do percurso; resposta fora do percurso não satisfaz nem gera pendência; voltar ao ramo reativa sem reescrever; Conclusão com nível diferente de Q14 não muda o percurso; consulta não grava; `admite_escrita` | US1, US8, US9.1, US9.3, FR-030, FR-047–FR-050, SC-009 |
| `tests/participacao/test_jornada_conclusao.py` | Conclusão válida grava `concluida_em = agora` e preserva respostas do percurso; remove respostas fora do percurso (inclusive seleções de múltipla); conclusão rejeitada não remove nada; pendências listadas; Q1 = "Não" deixa só Q1; obrigatória fora do percurso não bloqueia; obrigatória do percurso bloqueia; "Outro:" sem complemento conclui; Campanha encerrada (explícita e por data) bloqueia, último dia aceito; estrutura não suportada rejeitada; Resposta incoerente gravada por ORM rejeitada; todas as violações reunidas; mensagens sem valor declarado | US6, US9.2, US10, US11, US12, FR-022–FR-046, SC-003–SC-008 |
| `tests/participacao/test_jornada_imutabilidade.py` | Depois da conclusão: os quatro `responder_*` e `remover_resposta` → `PARTICIPACAO_CONCLUIDA`, com a Campanha EM_COLETA e encerrada; conclusão repetida → `JA_CONCLUIDA`, mesmo `concluida_em`, nada removido; `iniciar_participacao` → `JA_EXISTENTE`; `admite_escrita` falso | US7, FR-036, FR-038–FR-041, SC-005 |
| `tests/participacao/test_jornada_concorrencia.py` | Bloqueio determinístico: a primeira consulta de `concluir` é `SELECT … FOR UPDATE` na Participação, antes de ler Respostas (também na repetida); duas conclusões simultâneas (threads com barreira, estável em 10 execuções) → um `concluida_em`; conclusão × escrita → escrita antes considerada ou rejeitada; nunca Resposta depois de `concluida_em` | FR-043, SC-011 |
| `tests/participacao/test_jornada_aceitacao.py` | As 11 perguntas de sucesso do solicitante, ponta a ponta; o único campo novo é `Participacao.concluida_em`; nenhum modelo novo nem proibido; modelos 001–004 e `Resposta` sem colunas novas; publicar Versão posterior não muda percurso de Campanha anterior | SC-010, SC-012, FR-052, FR-053 |

Resultado esperado: todos os testes passam, sem rede e sem depender do relógio real.
Toda operação temporal recebe `agora` explícito.

## Ver a jornada no shell

```bash
uv run python manage.py shell
```

Roteiro (dados fictícios; a baseline continua RASCUNHO):

1. `materializar()` a baseline da 003; criar uma cópia com `criar_versao_a_partir_de` e
   publicá-la (só no banco local de desenvolvimento).
2. Criar uma Campanha com a cópia, definir período e abrir com `agora` no período.
3. Incorporar um cenário da fonte simulada e `iniciar_participacao`.
4. `situacao_da_jornada(p, agora=…)`: uma passagem (S1), pendente Q1, destino
   `INDETERMINADA`.
5. Responder Q1 = "Sim" e S2: a Seção atual passa a S3.
6. Responder até S8 com Q33 = "Sim" e parte de S9; trocar Q33 para "Não": as respostas de
   S9 aparecem em `fora_do_percurso`; voltar para "Sim": deixam de aparecer.
7. Completar o percurso até `finalizada`; `concluir(p, agora=…)` → `CONCLUIDA`; as
   respostas que estavam fora do percurso não existem mais.
8. Tentar `responder_texto` → `PARTICIPACAO_CONCLUIDA`; `concluir` de novo →
   `JA_CONCLUIDA`, mesmo `concluida_em`.
