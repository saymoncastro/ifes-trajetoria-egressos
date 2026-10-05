# Data Model: Participação em Campanha e respostas em rascunho

**Feature**: [spec.md](spec.md) | **Research**: [research.md](research.md)

Duas entidades de domínio novas, **Participacao** e **Resposta**, e uma tabela técnica,
**RespostaOpcao**, todas no app `trajetoria.participacao` (R1). Nenhum modelo das Features
001 a 004 é alterado; todas as FKs para eles usam `related_name="+"` (R2).

```text
academico.ConclusaoAcademica ◄─┐                ┌─► campanha.Campanha ─► instrumento.Versao
            (001)              │ PROTECT        │ PROTECT        (004)          (002)
                               │                │
                          ┌────┴────────────────┴────┐
                          │       Participacao        │  UNIQUE (campanha, conclusao)
                          │  id · iniciada_em         │
                          └────────────┬──────────────┘
                                       │ 1
                                       │ PROTECT
                                       ▼ 0..N
                          ┌───────────────────────────┐
                          │         Resposta          │  UNIQUE (participacao, pergunta)
                          │  id · opcao · texto ·     │──PROTECT──► instrumento.Pergunta
                          │  escala · complemento     │──PROTECT──► instrumento.Opcao (única)
                          └────────────┬──────────────┘
                                       │ 1  CASCADE
                                       ▼ 0..N (≥ 1 em escolha múltipla)
                          ┌───────────────────────────┐
                          │  RespostaOpcao (técnica)  │  UNIQUE (resposta, opcao)
                          │  id                       │──PROTECT──► instrumento.Opcao
                          └───────────────────────────┘
```

Convenções (como nas features anteriores):

- `id` é UUID gerado pelo NIAE.
- `NULL` significa "ausente"; cadeia vazia é proibida por CHECK. Texto só com espaços é
  rejeitado pela operação, não pelo banco (mesma divisão da 002 e da 004).
- Regras que dependem de outra linha (tipo da Pergunta, pertença à Versão, pertença da
  Opção, limites de escala, estado da Campanha, ≥ 1 seleção) são garantidas pelas
  operações, único caminho de escrita (R4, R9).

## Participacao

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | UUID | sim | Identidade (FR-001) |
| `campanha` | FK → `campanha.Campanha` | sim | `PROTECT`, `related_name="+"`; nunca alterada (FR-002) |
| `conclusao` | FK → `academico.ConclusaoAcademica` | sim | `PROTECT`, `related_name="+"`; nunca alterada (FR-002) |
| `iniciada_em` | data e hora | sim | Momento de referência da criação (FR-003, R3) |

**Restrições**:

- `UNIQUE (campanha, conclusao)` — no máximo uma Participação por par (FR-006), também
  sob concorrência (R11).

**Propriedades derivadas** (sem coluna — FR-004):

- `pessoa` → `conclusao.pessoa`;
- `versao` → `campanha.versao`;
- `pesquisa` → `campanha.versao.pesquisa`.

**Ordem de leitura**: `(iniciada_em, id)`, só para determinismo; sem significado de
preferência ou de "atual" (FR-049).

**Não existe**: estado, `concluida_em`, `atualizada_em`, progresso, Pessoa, Versão,
Pesquisa, canal, dispositivo, endereço de acesso, sessão, token, fotografia de
elegibilidade (FR-003, FR-055; Clarifications).

> **Nota de revisão (2026-10-05): estado atual do modelo.** Esta seção descreve a
> Participação como desenhada na 005. Features posteriores acrescentaram, por migração
> aditiva, dois campos:
>
> - `concluida_em` (data e hora, anulável), da **006**: ausente = rascunho; gravado uma
>   única vez por `concluir` (006 FR-001 a FR-003). Migração
>   `participacao/0002_participacao_concluida_em`.
> - `formacao_declarada` (OneToOne → `declaracao.FormacaoDeclarada`, anulável,
>   `PROTECT`), da **019**. Com ela, `conclusao` passou a ser **anulável**, e o CHECK
>   `participacao_ancora_unica` exige exatamente uma âncora: Conclusão ou Formação
>   Declarada. `UNIQUE (campanha, conclusao)` permanece. `pessoa` devolve `None`
>   quando a âncora é declarada. Migração `participacao/0003`.
>
> Fonte de verdade: `trajetoria/participacao/models.py`.

**Remoção**: nenhuma operação remove Participação (FR-017). `PROTECT` nas FKs impede que
a remoção de Campanha ou Conclusão a apague; pela 004, só Campanha nunca aberta é
removível, e ela não tem Participação.

## Resposta

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | UUID | sim | Identidade; estável entre substituições (R7) |
| `participacao` | FK → `Participacao` | sim | `PROTECT`, `related_name="respostas"` |
| `pergunta` | FK → `instrumento.Pergunta` | sim | `PROTECT`, `related_name="+"`; da Versão da Campanha (operação) |
| `opcao` | FK → `instrumento.Opcao` | não | `PROTECT`, `related_name="+"`; valor de `ESCOLHA_UNICA` |
| `texto` | texto | não | Valor de `TEXTO_CURTO`; exatamente como recebido |
| `escala` | inteiro | não | Valor de `ESCALA` |
| `complemento` | texto | não | Complemento de "Outro" em escolha (R6) |
| `opcoes` | M2M → `instrumento.Opcao` via `RespostaOpcao` | — | Valor de `ESCOLHA_MULTIPLA`; `related_name="+"` |

**Restrições** (banco):

- `UNIQUE (participacao, pergunta)` — uma Resposta por Pergunta (FR-018).
- `CHECK` no máximo um valor direto: não há duas colunas preenchidas entre `opcao`,
  `texto` e `escala`.
- `CHECK texto <> ''`; `CHECK complemento <> ''`.

Os CHECKs protegem só invariantes verificáveis com as colunas da própria linha. Regras
que dependem do tipo da Pergunta, da pertença da Opção, da Versão da Campanha ou dos
limites da escala — inclusive "complemento só em Pergunta de escolha e só com a Opção que
o admite selecionada" — ficam nas operações. Sem tipo copiado da Pergunta, gatilho ou
função PostgreSQL.

**Forma do valor por tipo** (operação — FR-023 a FR-030):

| Tipo da Pergunta | `opcao` | `opcoes` | `texto` | `escala` | `complemento` |
|------------------|:-------:|:--------:|:-------:|:--------:|:-------------:|
| `ESCOLHA_UNICA` | 1 Opção da Pergunta | vazio | `NULL` | `NULL` | só se `opcao.complemento_textual` |
| `ESCOLHA_MULTIPLA` | `NULL` | ≥ 1 Opção da Pergunta, sem repetição | `NULL` | `NULL` | só se a Opção com complemento está em `opcoes` |
| `TEXTO_CURTO` | `NULL` | vazio | não vazio, não só espaços | `NULL` | `NULL` |
| `ESCALA` | `NULL` | vazio | `NULL` | inteiro em `[escala_inicio, escala_fim]` | `NULL` |

**Pergunta não respondida**: não existe linha de Resposta para `(participacao,
pergunta)`. Não há Resposta "vazia" (texto vazio, conjunto vazio) — Clarifications.

**Versão da Resposta**: `participacao.campanha.versao`, igual a
`pergunta.secao.versao` (FR-019, FR-022). Não é coluna.

**Interpretação histórica**: a Versão aplicada a uma Campanha que admitiu coleta é
PUBLICADA e imutável (004 FR-010; 002 FR-016), então `pergunta`, `opcao` e `opcoes`
apontam para conteúdo que não muda. Nada é copiado (FR-021).

## RespostaOpcao (técnica)

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | UUID | sim | Só técnico, sem uso de domínio |
| `resposta` | FK → `Resposta` | sim | `CASCADE`: o conjunto é parte do valor (R5) |
| `opcao` | FK → `instrumento.Opcao` | sim | `PROTECT`, `related_name="+"` |

**Restrições**: `UNIQUE (resposta, opcao)` — sem duplicata (FR-025).

Sem coluna de ordem nem timestamp: a ordem de seleção não é informação (FR-025). Lida
pela ordem do instrumento (`Opcao.posicao`). Sem operação própria nem identidade de
domínio: só a Resposta é endereçada; o `id` existe só porque toda tabela precisa de
chave.

## Ciclo de vida

```text
Participacao
  (não existe) ──iniciar: admite_participacao (004) ──► existe, para sempre (sem estado)
                 início repetido ─────────────────────► devolve a existente, nada grava

Resposta (por Participação × Pergunta), só com a Campanha EM_COLETA no momento de referência:

  (não respondida) ──responder_*──► (respondida: valor V1)
                                        │  responder_* (mesma Pergunta) → valor V2, mesma linha
                                        │  remover_resposta → (não respondida)
  Campanha fora de EM_COLETA: nenhuma transição; leitura continua
```

Nenhuma transição grava histórico, evento ou momento por edição (FR-035, FR-045).

## Invariantes e onde são garantidos

| Invariante | Operação | Banco |
|------------|:--------:|:-----:|
| Uma Participação por Campanha × Conclusão (FR-006) | ✓ (`JA_EXISTENTE`) | `UNIQUE` |
| Participação nasce só com coleta admitida e Conclusão elegível (FR-011) | ✓ (`admite_participacao`) | — |
| Campanha e Conclusão da Participação nunca mudam (FR-002) | ✓ (nenhuma operação as altera) | — |
| Uma Resposta por Participação × Pergunta (FR-018) | ✓ (atualiza no lugar) | `UNIQUE` |
| Pergunta da Versão da Campanha (FR-019) | ✓ | — |
| Opção da própria Pergunta (FR-024, FR-025) | ✓ | — |
| Valor na coluna do tipo da Pergunta (FR-023) | ✓ | CHECK "no máximo um valor direto" (parcial) |
| Escala dentro dos limites (FR-027) | ✓ | — |
| Escolha múltipla com ≥ 1 Opção, sem repetição (FR-025) | ✓ | `UNIQUE (resposta, opcao)` (sem repetição) |
| Complemento só em escolha e com a Opção que o admite selecionada (FR-029, FR-030) | ✓ | — |
| Sem texto ou complemento vazio (FR-026, FR-030) | ✓ (inclui só espaços) | CHECK `<> ''` |
| Escrita só com Campanha EM_COLETA (FR-033, FR-039) | ✓ (`estado`) | — |
| Escrita atômica (FR-051) | ✓ (`transaction.atomic`) | — |
| Opção referida não é apagada (FR-028) | — | `PROTECT` |
| Nenhum dado das Features 001–004 alterado (FR-043, FR-060) | ✓ | `related_name="+"` (nenhuma coluna ou reverso novo) |

## Fora do modelo (deliberadamente)

Submissão, Tentativa, Sessão, Rascunho como entidade, VersaoResposta, HistoricoResposta,
Valor genérico, TipoResposta, Progresso, FotografiaPergunta, VersaoParticipacao, Convite,
Token, Consentimento, Evento; colunas `estado`, `concluida_em`, `atualizada_em`,
`respondida_em`, `tipo` copiado da Pergunta, `versao` ou `pessoa` copiados.
