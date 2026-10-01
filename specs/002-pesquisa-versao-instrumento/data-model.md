# Data Model: Pesquisa, versão e estrutura do instrumento

**Feature**: [spec.md](spec.md) | **Research**: [research.md](research.md)

Cinco entidades persistidas, todas no app `trajetoria.instrumento`. Nenhuma tem dado
pessoal, nem dado institucional, derivado ou declarado: todas são configuração do
instrumento. Nenhuma referencia Pessoa ou Conclusão Acadêmica (FR-065).

```text
Pesquisa 1 ── 0..N Versao 1 ── 0..N Secao 1 ── 0..N Pergunta 1 ── 0..N Opcao
                     │  ▲                │  ▲                         │
                     └──┘ origem         └──┘ encaminhamento          └──► Secao (regra_destino)
```

Convenções (como na 001):

- `id` é UUID gerado pelo NIAE (R3).
- `NULL` significa "ausente"; cadeia vazia é proibida por CHECK (R16).
- Todas as FKs usam `PROTECT`, exceto `Opcao.pergunta` (`CASCADE`, FR-061).
- Imutabilidade da Versão publicada e referências na mesma Versão são garantidas pelas
  operações, não pelo banco (R9, [ADR 0002](../../docs/adr/0002-imutabilidade-versao-publicada.md)
  rejeitado nesta fase).

## Pesquisa

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | UUID | sim | Identidade (FR-001) |
| `nome` | texto | sim | Nome administrativo; não vazio; sem unicidade (FR-002, R18); alterável a qualquer momento (FR-003) |

Nenhum outro atributo (FR-002).

## Versao

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | UUID | sim | Identidade (FR-005) |
| `pesquisa` | FK → Pesquisa | sim | `PROTECT`; nunca alterada (FR-005) |
| `designacao` | texto | sim | Não vazia; única na Pesquisa (FR-006) |
| `estado` | texto | sim | `RASCUNHO` ou `PUBLICADA` (FR-011) |
| `publicada_em` | data e hora | não | Preenchida exatamente quando `estado = PUBLICADA` (FR-015) |
| `origem` | FK → Versao | não | Versão da mesma Pesquisa da qual foi criada (FR-023); `PROTECT` |
| `titulo` | texto | não | Título apresentado (FR-010) |
| `texto_abertura` | texto | não | FR-010 |
| `texto_encerramento` | texto | não | FR-010 |

**Restrições**:
- `UNIQUE (pesquisa, designacao)`.
- `CHECK estado IN ('RASCUNHO', 'PUBLICADA')`.
- `CHECK (estado = 'PUBLICADA') = (publicada_em IS NOT NULL)`.
- `CHECK` de não vazio em `designacao`, `titulo`, `texto_abertura` e
  `texto_encerramento`.
- `CHECK origem <> id`.
- "Origem da mesma Pesquisa" é verificado pela operação, que sempre cria a nova Versão
  na Pesquisa da origem (FR-019).

**Ordem de leitura**: por `designacao`, apenas para determinismo; sem significado de
domínio (FR-008).

## Secao

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | UUID | sim | Identidade (FR-024) |
| `versao` | FK → Versao | sim | `PROTECT` |
| `posicao` | inteiro positivo | sim | Ordem na Versão (FR-026) |
| `titulo` | texto | não | FR-025 |
| `texto` | texto | não | Texto introdutório (FR-025) |
| `encaminhamento` | FK → Secao | não | Seção seguinte quando nenhuma regra é acionada (FR-049); `PROTECT` |

**Restrições**:
- `UNIQUE (versao, posicao)` `DEFERRABLE INITIALLY DEFERRED` (R4).
- `CHECK posicao > 0`; `CHECK` de não vazio em `titulo` e `texto`.
- `encaminhamento` da mesma Versão: verificado pelas operações (`REFERENCIA_OUTRA_VERSAO`).
- "Encaminhamento para Seção posterior": exigido só na publicação (FR-059 d, R15).

## Pergunta

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | UUID | sim | Identidade independente de texto e posição (FR-028) |
| `secao` | FK → Secao | sim | `PROTECT` (remover Seção com Perguntas é rejeitado — FR-061) |
| `posicao` | inteiro positivo | sim | Ordem na Seção |
| `tipo` | texto | sim | `ESCOLHA_UNICA`, `ESCOLHA_MULTIPLA`, `TEXTO_CURTO` ou `ESCALA` (FR-034) |
| `texto` | texto | sim | Não vazio (FR-029) |
| `texto_explicativo` | texto | não | FR-030 |
| `obrigatoria` | booleano | sim | Sem valor padrão no domínio: informado na criação (FR-029, FR-031) |
| `escala_inicio` | inteiro | condicional | Só em `ESCALA` (R5) |
| `escala_fim` | inteiro | condicional | Só em `ESCALA`; maior que `escala_inicio` |
| `escala_rotulo_inicio` | texto | não | Só em `ESCALA` |
| `escala_rotulo_fim` | texto | não | Só em `ESCALA` |

**Restrições**:
- `UNIQUE (secao, posicao)` `DEFERRABLE INITIALLY DEFERRED`.
- `CHECK posicao > 0`.
- `CHECK tipo IN (…quatro valores…)` (FR-034, FR-058 j).
- `CHECK` de escala (FR-038, FR-058 c, d):
  - `tipo = 'ESCALA'` ⇒ `escala_inicio` e `escala_fim` não nulos e `escala_inicio <
    escala_fim`;
  - `tipo <> 'ESCALA'` ⇒ as quatro colunas de escala nulas.
- `CHECK` de não vazio em `texto`, `texto_explicativo` e nos rótulos.
- Mover Pergunta para Seção de outra Versão: rejeitado pela operação
  (`REFERENCIA_OUTRA_VERSAO`). O `tipo` é definido na criação e não muda (FR-062).

## Opcao

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | UUID | sim | Identidade independente do texto (FR-041) |
| `pergunta` | FK → Pergunta | sim | `CASCADE`: remover a Pergunta remove suas Opções e regras (FR-061) |
| `posicao` | inteiro positivo | sim | Ordem na Pergunta |
| `texto` | texto | sim | Texto apresentado; não vazio; preservado exatamente (FR-041, R16) |
| `complemento_textual` | booleano | sim | Admite texto livre ao ser selecionada (FR-042); padrão `false` |
| `regra_destino` | FK → Secao | não | Regra "ir para Seção" (FR-050, R6); `PROTECT` |
| `regra_finaliza` | booleano | sim | Regra "finalizar" (FR-050); padrão `false` |

**Restrições**:
- `UNIQUE (pergunta, posicao)` `DEFERRABLE INITIALLY DEFERRED`.
- `UNIQUE (pergunta, texto)` (FR-058 m).
- `UNIQUE (pergunta) WHERE complemento_textual` (FR-042, FR-058 n).
- `CHECK NOT (regra_destino IS NOT NULL AND regra_finaliza)`: no máximo uma regra
  (FR-052).
- `CHECK posicao > 0`; `CHECK` de não vazio em `texto`.
- `regra_destino` da mesma Versão: verificado pelas operações (`REFERENCIA_OUTRA_VERSAO`).
- Opções só em perguntas de escolha e regras só em escolha única: verificados pelas
  operações (FR-040, FR-050, FR-062), pois dependem do tipo da Pergunta.

**Regra de navegação**: a Opção **tem** regra se `regra_destino` não é nulo ("ir para
Seção") ou se `regra_finaliza` é verdadeiro ("finalizar"). Por estar na Opção, a regra
pertence à Pergunta e à Opção que a provocam (FR-051), e não pode haver duas regras por
Opção nem regra com Opção de outra Pergunta (R6).

## Estados da Versão

```text
            publicar (completude OK)
RASCUNHO ───────────────────────────► PUBLICADA
   ▲  │                                   │
   └──┘ edição (FR-012)                   └── nenhuma transição de saída (FR-013)
```

- Toda Versão nasce em `RASCUNHO` (`criar_versao` e `criar_versao_a_partir_de`).
- `publicar` em `RASCUNHO` incompleta: rejeitada com todas as pendências; nada muda
  (FR-014).
- `publicar` em `PUBLICADA`: nada muda; resultado `JA_PUBLICADA` (FR-015).

## Invariantes e onde são garantidos

| Invariante | Operação | Banco |
|------------|:--------:|:-----:|
| Versão publicada imutável e não removível (FR-016–FR-018) | ✓ | — |
| Toda Versão nasce em rascunho; não volta a rascunho (FR-011, FR-013) | ✓ (nenhuma operação muda o estado, exceto `publicar`) | CHECK de coerência `estado`/`publicada_em` |
| Nenhuma referência a outra Versão (FR-021, FR-058 a, g) | ✓ | — |
| Ordem sem empate (FR-047) | ✓ | UNIQUE adiada |
| Exatamente quatro tipos (FR-034) | ✓ | CHECK |
| Escala só em escala, com limites válidos (FR-038) | ✓ | CHECK |
| No máximo uma regra por Opção; Opção da própria Pergunta (FR-052, FR-058 f, h) | ✓ | Estrutura (R6) e CHECK |
| Opções só em escolha; regra só em escolha única (FR-040, FR-050) | ✓ | — |
| Designação única na Pesquisa; textos de Opção únicos na Pergunta (FR-058 l, m) | ✓ | UNIQUE |
| No máximo uma Opção com complemento por Pergunta (FR-058 n) | ✓ | UNIQUE parcial |
| Completude para publicar (FR-059) | ✓ | — |
| Remoção de Seção referenciada ou com Perguntas (FR-061) | ✓ | `PROTECT` |
| Tipo da Pergunta não muda (FR-062) | ✓ (sem parâmetro de tipo em `alterar_pergunta`) | — |

## Fora do modelo (deliberadamente)

- Qualquer vínculo com Pessoa, Conclusão Acadêmica, Campanha, Participação ou Resposta.
- Forma de apresentação (botões, lista suspensa), numeração de perguntas, categoria de
  origem do dado, indicador associado (FR-033, FR-035).
- Mínimo/máximo de seleções, exclusividade entre Opções, validação de texto (FR-036,
  FR-037).
- Tabela de regras, condição de exibição, expressões (FR-056, FR-057).
- Correspondência entre elementos de Versões (DP-006); histórico de edição de rascunho.
- Datas de criação e alteração: sem consumidor nesta feature.
