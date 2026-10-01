# Data Model: Núcleo acadêmico longitudinal e fonte institucional simulada

**Feature**: [spec.md](spec.md) | **Research**: [research.md](research.md)

Esta feature cria apenas duas entidades persistidas. Os objetos trocados com a fonte
acadêmica estão em [contracts/fonte-academica.md](contracts/fonte-academica.md).

```text
Pessoa 1 ──── 0..N ConclusaoAcademica
(materializada só com ≥ 1 conclusão elegível — FR-039)
```

## Pessoa

| Campo | Tipo | Obrigatório | Origem | Regra |
|-------|------|-------------|--------|-------|
| `id` | UUID | sim | interno | Gerado pelo NIAE; chave primária; imutável (FR-001) |
| `fonte` | texto | sim | proveniência | Código da fonte que forneceu a Pessoa; não vazio. A fonte simulada usa o código `simulada`, o que basta para identificá-la (FR-035) |
| `id_externo` | texto | sim | proveniência | Identificador opaco atribuído pela fonte; não vazio (FR-006) |
| `nome` | texto | não | institucional | Apenas apresentação. `NULL` = não informado pela fonte; não vazio quando presente (FR-005) |
| `incorporado_em` | data e hora | sim | proveniência | Momento da primeira incorporação; nunca atualizado (FR-035, R7) |

**Restrições**:
- `UNIQUE (fonte, id_externo)` garante a idempotência da Pessoa (FR-004, FR-031).
- `CHECK` impede cadeia vazia em `fonte`, `id_externo` e `nome`.
- Não há nenhum campo acadêmico, como campus, curso ou nível (FR-003).
- O nome não tem restrição de unicidade e não participa de busca de identidade (FR-005).

## ConclusaoAcademica

| Campo | Tipo | Obrigatório | Origem | Regra |
|-------|------|-------------|--------|-------|
| `id` | UUID | sim | interno | Gerado pelo NIAE; estável; referência futura de Participações (FR-008, FR-038) |
| `pessoa` | FK → Pessoa | sim | interno | Exatamente uma Pessoa; exclusão protegida (FR-007) |
| `fonte` | texto | sim | proveniência | Não vazio |
| `id_externo` | texto | sim | proveniência | Identificador opaco da conclusão na fonte; não vazio |
| `curso` | texto | não | institucional | Denominação do curso; `NULL` = não informado pela fonte |
| `unidade` | texto | não | institucional | Campus, campus avançado ou Cefor; `NULL` = não informado |
| `nivel` | texto | não | institucional | Sem lista fechada (DP-007); `NULL` = não informado |
| `modalidade` | texto | não | institucional | Nunca deduzida do nome do curso (FR-010); `NULL` = não informado |
| `forma_oferta` | texto | não | institucional | `NULL` = não informado |
| `ano_conclusao` | inteiro | não | institucional | `NULL` = não informado |
| `data_conclusao` | data | não | institucional | Presente só se a fonte fornecer a data completa (FR-011) |
| `incorporado_em` | data e hora | sim | proveniência | Momento da primeira incorporação; nunca atualizado |

**Restrições**:
- `UNIQUE (fonte, id_externo)` garante a idempotência da Conclusão (FR-031).
- `CHECK` impede cadeia vazia em todos os campos de texto.
- `CHECK (data_conclusao IS NULL OR (ano_conclusao IS NOT NULL AND ano_conclusao = ano de
  data_conclusao))` (FR-011). O `ano_conclusao IS NOT NULL` explícito é necessário: sem ele,
  data preenchida com ano `NULL` faz a comparação resultar em `UNKNOWN`, e o PostgreSQL
  aceita a linha.
- A FK `pessoa` usa `PROTECT`: nenhuma remoção em cascata (Princípio VIII).
- Não há restrição entre conclusões da mesma Pessoa. Atributos iguais com referências
  diferentes são conclusões distintas (FR-014).

**Ordem**: as conclusões de uma Pessoa são lidas em ordem determinística, por ano e
depois por `id`. A ordem é só de apresentação, sem significado de domínio (FR-017).

## Invariantes e onde são garantidos

| Invariante | Garantia |
|------------|----------|
| Uma Pessoa por (fonte, id externo) | Unicidade no banco e incorporação com "obter ou criar" |
| Uma Conclusão por (fonte, id externo) | Unicidade no banco e incorporação com "obter ou criar" |
| Conclusão pertence a exatamente uma Pessoa | FK obrigatória; divergência de dono nunca reatribui (FR-033) |
| Só conclusões reconhecidas são persistidas | O contrato só transporta conclusões reconhecidas (R4) |
| Pessoa sem conclusão elegível não é persistida | Regra da incorporação (FR-039) |
| Ausência ≠ valor | `NULL` com semântica fixa; cadeia vazia proibida (R8) |
| Dados incorporados não são sobrescritos nem removidos por nova leitura | A incorporação nunca executa atualização ou remoção (R11) |
| Todo dado acadêmico é institucional | Não existe campo declarado nem derivado nesta feature (FR-036) |

## Ciclo de vida

Não há máquina de estados. Os registros são criados por incorporação e, nesta feature,
nunca alterados nem removidos. Correção e sincronização são DP-005 e DP-006.

## Fora do modelo (deliberadamente)

- Forma de ingresso, códigos de curso/unidade, tabelas de domínio de Curso e Unidade.
- Tabela separada de referências de origem (R6) e histórico de obtenções (R7).
- Registro persistido de divergências (R11).
- Qualquer entidade de Pesquisa, Versão, Campanha, Participação ou Resposta.
