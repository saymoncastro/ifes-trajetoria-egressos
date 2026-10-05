# Data Model — Feature 020

Três tabelas novas em dois apps novos. Nenhuma tabela existente muda.

Convenções seguidas:

- UUID como PK;
- `related_name="+"` para FKs a features anteriores;
- `_nao_vazio` para textos obrigatórios;
- instantes gravados pelas operações, não por `auto_now_add`, para que os testes controlem
  o tempo;
- imutabilidade garantida nas operações, sem triggers.

## 1. `contato.ContatoDaPessoa`

Registro imutável. Nunca é atualizado nem removido pela 020 (a retenção é DP-2006).

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id` | UUID PK | — |
| `pessoa` | FK `academico.Pessoa`, `PROTECT`, `related_name="+"` | Dono |
| `canal` | Texto, choices `EMAIL` | Único valor na 020 (E1) |
| `valor` | Texto ≤ 254 | Normalizado (research R4). Legível **só na demonstração** (E2; R9; DP-2010) |
| `origem` | Texto, choices `FONTE_ACADEMICA` \| `EGRESSO` | Institucional ou declarado (Princípio III) |
| `fonte` | Texto, nulo | Obrigatório e não vazio se a origem for fonte; nulo se for egresso |
| `posicao` | Inteiro ≥ 0, nulo | Obrigatório se a origem for fonte (ordem do adaptador); nulo se for egresso |
| `obtido_em` | DateTime | Momento da observação (fonte) ou do informe (egresso) |

**Restrições**:

- `CHECK`: a origem fonte exige `fonte` e `posicao`; a origem egresso exige os dois nulos.
- `CHECK`: `valor` e `fonte` não vazios.
- `UNIQUE (pessoa, fonte, obtido_em, posicao)` com a condição `origem = FONTE_ACADEMICA`.
- Índice `(pessoa, origem, obtido_em)` para a política.

**Política de escolha (FR-008)**, função pura sobre os registros de uma Pessoa até o
instante *t*:

1. o registro `EGRESSO` de maior `obtido_em` cujo valor passe em `normalizar_email`;
2. senão, a observação `FONTE_ACADEMICA` mais recente, tomando os registros de maior
   `obtido_em` entre todas as fontes e, dentro dela, o de menor `posicao` válido;
3. senão, nenhum contato.

**Observação**: o conjunto de registros de uma Pessoa e fonte com o mesmo `obtido_em`. A
carga grava uma observação nova só quando a lista ordenada difere da última (R2).

## 2. `mobilizacao.LoteDeMobilizacao`

Imutável depois de criado. Não tem estado próprio: a situação é derivada dos membros.

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id` | UUID PK | — |
| `campanha` | FK `campanha.Campanha`, `PROTECT`, `related_name="+"` | — |
| `nome` | Texto ≤ 120, não vazio | Rótulo operacional |
| `unidades` | ArrayField de texto, nulo | NULL significa sem filtro; `[]` é proibido |
| `nivel` | Texto, nulo | — |
| `ano_minimo`, `ano_maximo` | Inteiro, nulo | `ano_minimo ≤ ano_maximo` quando ambos existem |
| `curso` | Texto, nulo | Igualdade textual |
| `escopo_institucional` | Booleano | Escopo do operador na confirmação |
| `escopo_unidades` | ArrayField de texto | Vazio se o escopo for institucional; não vazio caso contrário |
| `excluidas_por_mobilizacao` | Inteiro ≥ 0 | FR-024 |
| `confirmado_em` | DateTime | — |
| `operador` | Texto, não vazio | Identificador do operador (fictício na demonstração) |

**Restrições (CHECK)**:

- `unidades` é NULL ou não vazio;
- coerência dos anos;
- coerência do escopo: institucional ⇔ `escopo_unidades` vazio;
- se o escopo não é institucional, `unidades` não é nulo. Que `unidades ⊆ escopo_unidades`
  é verificado na operação.

**Situação derivada**:

| Situação | Condição |
| --- | --- |
| não enviado | Nenhum membro saiu de `NAO_TENTADO` e de `SEM_CONTATO` |
| envio parcial | Há membros `NAO_TENTADO` e algum já tentado |
| envio concluído | Nenhum `NAO_TENTADO` |

## 3. `mobilizacao.MembroDoLote`

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id` | UUID PK | — |
| `lote` | FK Lote, `PROTECT`, `related_name="membros"` | — |
| `campanha` | FK `campanha.Campanha`, `PROTECT`, `related_name="+"` | Igual a `lote.campanha`, verificado na criação; existe para a restrição do R6 |
| `pessoa` | FK `academico.Pessoa`, `PROTECT`, `related_name="+"` | — |
| `contato` | FK `contato.ContatoDaPessoa`, `PROTECT`, nulo, `related_name="+"` | Contato congelado (E6) |
| `situacao` | Texto, choices (abaixo) | — |
| `tentativa_iniciada_em` | DateTime, nulo | Gravado ao entrar em `EM_TENTATIVA` |
| `resultado_em` | DateTime, nulo | Gravado em `SUBMETIDO_AO_TRANSPORTE` ou `FALHA_DE_TRANSPORTE` |

**Restrições**:

- `UNIQUE (lote, pessoa)` (FR-018).
- `UNIQUE (campanha, pessoa)` com a condição `situacao <> 'SEM_CONTATO'`
  (`membro_uma_abordagem_por_campanha`; FR-024 e FR-025).
- `CHECK`: `situacao = SEM_CONTATO` ⇔ `contato IS NULL`.
- `CHECK` de coerência temporal:
  - `NAO_TENTADO` e `SEM_CONTATO` ⇒ os dois instantes nulos;
  - `EM_TENTATIVA` ⇒ só `tentativa_iniciada_em`;
  - finais ⇒ os dois instantes, com `resultado_em ≥ tentativa_iniciada_em`.
- A operação verifica que `contato.pessoa_id = pessoa_id`.

**Transições** (só pela operação de envio; nenhuma outra escrita):

```text
SEM_CONTATO                       (final, na criação)
NAO_TENTADO ──► EM_TENTATIVA ──► SUBMETIDO_AO_TRANSPORTE   (final)
                     │
                     └─────────► FALHA_DE_TRANSPORTE       (final)
EM_TENTATIVA sem resultado após a ação  ⇒  apresentado como "resultado incerto"; nunca volta
```

## 4. Efeitos em tabelas existentes

Nenhum. `Pessoa`, `ConclusaoAcademica`, `Campanha`, `Participacao`, os snapshots da 012,
os modelos da 019 e da 021 não mudam. A 016 não tinha tabelas.

## 5. Migrações

- `contato/0001_initial`: uma tabela.
- `mobilizacao/0001_initial`: duas tabelas, dependendo de `contato`, `academico` e
  `campanha`.

As duas são aditivas e reversíveis (Princípio XXVII) e não migram dados.
