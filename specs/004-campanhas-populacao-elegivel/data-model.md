# Data Model: Campanhas e população elegível

**Feature**: [spec.md](spec.md) | **Research**: [research.md](research.md)

Uma entidade persistida, `Campanha`, no novo app `trajetoria.campanha`. Nenhum modelo das
Features 001 e 002 é alterado.

```text
instrumento.Pesquisa 1 ── 0..N instrumento.Versao 1 ── 0..N campanha.Campanha
                                                            ┆
                                                            ┆ avaliar() / populacao_no_momento()
                                                            ┆ (calculado, nada persistido)
                                                            ▼
academico.Pessoa 1 ── 0..N academico.ConclusaoAcademica
```

Convenções (como na 001 e na 002):

- `id` é UUID gerado pelo NIAE.
- `NULL` significa "ausente". Cadeia vazia é proibida por CHECK.
- Regras que dependem de outra linha (Versão publicada) ou do tempo (data de referência
  dentro do período) ficam nas operações (research R10).

## Campanha

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | UUID | sim | Identidade própria (FR-001) |
| `nome` | texto | sim | Não vazio; sem unicidade; gravado como recebido (FR-002 a) |
| `versao` | FK → `instrumento.Versao` | sim | Exatamente uma; `PROTECT`; sem relação reversa (`related_name="+"`): a Versão não conhece a Campanha (FR-002 b, FR-007; R1) |
| `inicio` | data | não | Início do período, incluído (FR-011) |
| `fim` | data | não | Encerramento do período, incluído (FR-011) |
| `ano_minimo` | inteiro positivo pequeno | não | Critério (a); `NULL` = ausente (FR-018, FR-021) |
| `ano_maximo` | inteiro positivo pequeno | não | Critério (b); `NULL` = ausente |
| `unidades` | array de texto | não | Critério (c); `NULL` = não definido; ≥ 1 elemento quando presente; `[]` nunca gravado (FR-023 c) |
| `niveis` | array de texto | não | Critério (d); idem |
| `modalidades` | array de texto | não | Critério (e); idem |
| `formas_oferta` | array de texto | não | Critério (f); idem |
| `aberta_em` | data e hora | não | Momento da abertura; presente ⇔ a Campanha foi aberta (FR-036, FR-045) |
| `encerrada_em` | data e hora | não | Momento do encerramento **explícito**; ausente no encerramento por fim do período (FR-038) |

Nenhum outro campo. Não há `pesquisa`, `estado`, contagem de população, criador, datas de
criação ou alteração, descrição nem escopo de unidade: nenhum tem consumidor (FR-002;
research R2, R5, R12).

**Critério ausente × vazio** (research R3): `NULL` = critério não definido, não restringe;
array com ≥ 1 valor = valores permitidos; `[]` = configuração inválida, rejeitada pela
operação e pelo CHECK. Os valores são exatos (sem normalização), sem duplicatas e gravados
em ordem lexicográfica apenas para estabilidade e comparação.

**Propriedades** (sem coluna):

- `pesquisa` → `versao.pesquisa` (FR-003).
- `populacao_ampla` → os seis critérios são `NULL` (FR-019).

**Restrições (CHECK)**:

- `nome <> ''`.
- Período inteiro ou ausente, e coerente:
  `(inicio IS NULL AND fim IS NULL) OR (inicio IS NOT NULL AND fim IS NOT NULL AND inicio <= fim)`
  (FR-012). Os `IS NOT NULL` são explícitos para evitar `UNKNOWN`.
- `ano_minimo IS NULL OR ano_maximo IS NULL OR ano_minimo <= ano_maximo` (FR-023 b). A
  positividade vem do tipo.
- Para cada array: `col IS NULL OR cardinalidade(col) >= 1` (pelo `__len` do Django, que
  devolve 0 para vazio) e `NOT (col @> '{""}')` (FR-023 c, d).
- Aberta exige período: `aberta_em IS NULL OR (inicio IS NOT NULL AND fim IS NOT NULL)`.
- Encerrada exige aberta: `encerrada_em IS NULL OR aberta_em IS NOT NULL`.
- `encerrada_em IS NULL OR encerrada_em >= aberta_em`.

**Garantido pelas operações** (dependem de outra linha ou do tempo):

- Versão PUBLICADA na abertura (FR-036 a).
- Data de referência dentro do período na abertura (FR-036 d).
- Nenhuma alteração de `nome`, `versao`, período ou critérios com `aberta_em` presente,
  qualquer que seja o estado temporal (FR-043). Sem `aberta_em`, tudo é editável, mesmo
  com período expirado.
- Nenhuma remoção com `aberta_em` presente (FR-044). Sem `aberta_em`, remoção permitida
  em qualquer estado.
- `encerrada_em` só é gravado em Campanha aberta e EM_COLETA (FR-040).
- `aberta_em` e `encerrada_em` gravados uma única vez (FR-039).
- Valores de array sem espaço apenas, deduplicados e ordenados (research R11).

**Ordem de leitura**: `(inicio, id)`, apenas para determinismo, sem significado de
preferência (FR-052).

## Estado observável (derivado)

Função de `aberta_em`, `encerrada_em`, `fim` e da data de referência `hoje` (research R5).
Ordem de precedência: encerramento explícito → fim do período → abertura → preparação.

```text
                         abrir(agora)
                         [Versão PUBLICADA ∧ período definido ∧ inicio ≤ hoje ≤ fim]
EM_PREPARACAO ───────────────────────────────────────────────► EM_COLETA
  aberta_em = ∅                 grava aberta_em = agora          aberta_em ≠ ∅
  fim = ∅ ou hoje ≤ fim                                          encerrada_em = ∅
  │  ▲                                                           hoje ≤ fim
  │  └ criar, alterar, definir_periodo,                             │
  │    definir_criterios                                            │ encerrar(agora): grava encerrada_em
  ├ remover                                                         │ ou hoje > fim: nada é gravado
  │                                                                 ▼
  └──── hoje > fim (nunca aberta): nada é gravado ──────────►  ENCERRADA
                                                                forma = EXPLICITA     se encerrada_em ≠ ∅
                                                                        FIM_DO_PERIODO caso contrário
                                                                houve coleta? aberta_em ≠ ∅

Estado temporal controla a COLETA (abrir, admitir participação, encerrar).
Abertura histórica (aberta_em ≠ ∅) controla a IMUTABILIDADE:

| Situação | Estado | Editável e removível | Abrir | Encerrar |
|----------|--------|----------------------|-------|----------|
| Nunca aberta, dentro da janela ou antes dela | EM_PREPARACAO | sim | se Versão PUBLICADA e hoje ∈ período | rejeitado (`CAMPANHA_NUNCA_ABERTA`) |
| Nunca aberta, depois do fim | ENCERRADA | **sim** | rejeitado (`FORA_DO_PERIODO`) | rejeitado (`CAMPANHA_NUNCA_ABERTA`), nada gravado |
| Nunca aberta, depois do fim, período corrigido para o futuro | EM_PREPARACAO | sim | quando hoje ∈ novo período | rejeitado |
| Aberta, dentro da janela | EM_COLETA | não | `JA_EM_COLETA` | grava `encerrada_em` |
| Aberta, depois do fim | ENCERRADA (final) | não | `JA_ENCERRADA` | `JA_ENCERRADA` |
| Aberta e encerrada antecipadamente | ENCERRADA (final) | não | `JA_ENCERRADA` | `JA_ENCERRADA` |

ENCERRADA é final só para Campanha aberta. Para Campanha nunca aberta, o estado
acompanha o período, que ainda é corrigível. Isso não é reabertura (FR-039).
```

| # | Situação gravada | `hoje` | Estado | Forma do encerramento |
|---|------------------|--------|--------|-----------------------|
| 1 | `encerrada_em` presente | qualquer | ENCERRADA | EXPLICITA (momento = `encerrada_em`) |
| 2 | `encerrada_em` ausente, `fim` presente | `hoje > fim` | ENCERRADA | FIM_DO_PERIODO (momento = fim do dia `fim`), tenha sido aberta ou não |
| 3 | `aberta_em` presente | `hoje ≤ fim` | EM_COLETA | — |
| 4 | `aberta_em` ausente | sem `fim`, ou `hoje ≤ fim` | EM_PREPARACAO | — |

Casos exigidos nos testes: antes do início, nunca aberta → EM_PREPARACAO; no período,
nunca aberta → EM_PREPARACAO; no período, aberta → EM_COLETA; encerrada antecipadamente
→ ENCERRADA; depois do fim, aberta → ENCERRADA; depois do fim, nunca aberta → ENCERRADA.

Não existe coluna de estado, job, agendador ou processo que altere a linha quando o
período termina.

## Elegibilidade (valor, não persistido)

```text
Elegibilidade
  pendencias: tuple[Pendencia, ...]       # vazia ⇔ ELEGIVEL; em ordem fixa de critério
  resultado:  ELEGIVEL | NAO_ELEGIVEL     # derivado das pendências, não armazenado

Pendencia
  criterio: ANO_CONCLUSAO | UNIDADE | NIVEL | MODALIDADE | FORMA_OFERTA
  motivo:   NAO_INFORMADO | NAO_ATENDE
```

| Critério | Definido quando | Atributo da Conclusão | NAO_INFORMADO | NAO_ATENDE |
|----------|-----------------|-----------------------|---------------|------------|
| ANO_CONCLUSAO | `ano_minimo` ou `ano_maximo` presente | `ano_conclusao` | `ano_conclusao` é `NULL` | fora de `[ano_minimo, ano_maximo]` (limite ausente não restringe) |
| UNIDADE | `unidades` presente | `unidade` | `unidade` é `NULL` | `unidade` ∉ `unidades` (igualdade exata) |
| NIVEL | `niveis` presente | `nivel` | idem | idem |
| MODALIDADE | `modalidades` presente | `modalidade` | idem | idem |
| FORMA_OFERTA | `formas_oferta` presente | `forma_oferta` | idem | idem |

Critério não definido nunca gera pendência, mesmo com o atributo `NULL` (FR-028).

## População no momento da consulta (não persistida)

`ConclusaoAcademica.objects` filtrado pela conjunção dos critérios definidos. É o mesmo
predicado da tabela acima, avaliado no banco. Conclusões incorporadas depois da abertura
entram, se satisfizerem os critérios (FR-032). A contagem é de Conclusões (FR-033) e não é
denominador histórico (DP-408).

## Invariantes e onde são garantidos

| Invariante | Operação | Banco |
|------------|:--------:|:-----:|
| Exatamente uma Versão por Campanha (FR-002 b) | ✓ | FK `NOT NULL` |
| Pesquisa não diverge da Versão (FR-003) | — | Sem coluna (propriedade) |
| Período inteiro e `inicio ≤ fim` (FR-012) | ✓ | CHECK |
| `ano_minimo ≤ ano_maximo`; anos positivos (FR-023 a, b) | ✓ | CHECK e tipo |
| Conjunto de critério nunca vazio nem com cadeia vazia (FR-023 c, d) | ✓ | CHECK |
| Abertura só com Versão PUBLICADA (FR-009, FR-036 a) | ✓ | — |
| Abertura só com data de referência no período (FR-036 d) | ✓ | — |
| Aberta tem período (FR-036 b) | ✓ | CHECK |
| Encerrada foi aberta, depois da abertura (FR-038) | ✓ | CHECK |
| Imutável após abertura (FR-043) | ✓ | — |
| Não removível após abertura (FR-044) | ✓ | — |
| Versão usada não é removível | — | FK `PROTECT` (e a 002 não remove Versões) |
| EM_COLETA ⇒ `hoje` no período (FR-041) | ✓ (abertura) | derivação do estado |
| Nada de elegibilidade ou população persistido (FR-030, FR-032) | ✓ | sem colunas ou tabelas |

## Fora do modelo (deliberadamente)

- Segmento, Regra, Filtro, GrupoDeFiltros, tabela genérica de critérios, Populacao,
  MembroCampanha, Destinatario, Convite, Agendamento, HistoricoCampanha, VersaoCampanha.
- Catálogos de Unidade, Nível, Modalidade e Forma de Oferta (001/DP-007).
- Coluna de estado, contagem ou fotografia da população (DP-408).
- Participação e Resposta, ou qualquer marcador delas (FR-055).
- Prorrogação, reabertura, suspensão, cancelamento (DP-405).
- Qualquer coluna nova em `Versao`, `Pesquisa`, `Pessoa` ou `ConclusaoAcademica`.
