# Data Model: Dataset analítico institucional reprodutível (Feature 012)

App `trajetoria/analitico`. `NULL` significa "ausente", como na 001. Os nomes são os do
plan; a forma exata de cada linha de código pertence à implementação.

## 1. Persistência

Duas entidades novas e uma migration aditiva (`analitico/0001_initial`). Nenhuma tabela,
coluna, índice ou constraint das Features 001 a 011 é alterada.

### 1.1 `SnapshotAnalitico`

Fotografia imutável de uma Campanha encerrada que entrou em coleta (spec, Key Entities).

| Campo | Tipo | Nulo | Observação |
|-------|------|------|------------|
| `id` | UUID, PK, `default=uuid4` | não | Identidade do snapshot |
| `campanha` | FK → `campanha.Campanha`, `on_delete=PROTECT`, `related_name="+"` | não | Campanha de origem; Versão, critérios e encerramento são alcançados por ela |
| `capturado_em` | `DateTimeField` | não | Instante real da captura, gravado só pela operação (research R8); **sem** `default` nem `auto_now_add`, para que nenhuma criação fora da operação passe despercebida |

- `Meta.ordering = ["capturado_em", "id"]`: só determinismo, sem significado de
  autoridade (spec FR-063).
- **Sem** unicidade por Campanha: vários snapshots por Campanha (spec FR-060).
- **Sem** título, descrição, status, autor, motivo, observação, sequência ou totais.

### 1.2 `RegistroDoSnapshot`

Uma Conclusão Acadêmica no universo de um snapshot.

| Campo | Tipo | Nulo | Observação |
|-------|------|------|------------|
| `id` | UUID, PK, `default=uuid4` | não | Técnico |
| `snapshot` | FK → `SnapshotAnalitico`, `on_delete=CASCADE`, `related_name="registros"` | não | Parte do snapshot (research R6) |
| `conclusao` | FK → `academico.ConclusaoAcademica`, `on_delete=PROTECT`, `related_name="+"` | não | Referência técnica interna; não é identificador exportável (spec FR-047) |
| `elegivel_no_snapshot` | `BooleanField`, sem `default` | não | Resultado congelado da 004 no momento da captura |
| `curso` | `TextField` | sim | Contexto congelado (001) |
| `unidade` | `TextField` | sim | Contexto congelado (001) |
| `nivel` | `TextField` | sim | Contexto congelado (001) |
| `modalidade` | `TextField` | sim | Contexto congelado (001) |
| `forma_oferta` | `TextField` | sim | Contexto congelado (001) |
| `ano_conclusao` | `PositiveSmallIntegerField` | sim | Contexto congelado (001); atributo próprio, não derivado da data (research R4) |
| `data_conclusao` | `DateField` | sim | Contexto congelado (001) |

Os sete campos de contexto são **exatamente** `fonte_academica.contrato.CAMPOS_DE_CONTEXTO`,
com os mesmos tipos e nulabilidade de `ConclusaoAcademica` (research R5).

**Constraints**:

- `UniqueConstraint(fields=["snapshot", "conclusao"], name="registro_conclusao_unica_no_snapshot")`
  — grão: uma Conclusão no máximo uma vez por snapshot (spec FR-031). O índice dessa
  constraint também serve à leitura por snapshot.
- **Nenhum** CHECK de não vazio ou de coerência ano/data: a cópia não rejeita nem
  reinterpreta o que a origem guarda (research R5). A origem já tem esses CHECKs.
- `elegivel_no_snapshot` não nulo e sem default: um registro sem elegibilidade explícita
  não pode ser gravado (spec FR-021).

**Não existe**: `fonte`, `id_externo`, `pessoa`, `nome`, `incorporado_em`, motivo de
inelegibilidade, referência a Participação, cópia de Resposta.

### 1.3 Relações

```text
Campanha (004) ──PROTECT──< SnapshotAnalitico ──CASCADE──< RegistroDoSnapshot >──PROTECT── ConclusaoAcademica (001)
                                                                 ┆ (leitura, por campanha + conclusao_id)
                                                                 └┄┄ Participacao (005/006) ── Resposta (005) ── Pergunta/Opção (002)
```

A Participação **não** é referenciada pelo registro. Ela é única por (Campanha, Conclusão)
(`participacao_par_unico`), imutável depois do encerramento, e é encontrada na leitura pela
Campanha do snapshot e pela `conclusao_id` do registro.

> **Nota de revisão pela Feature 019 (registrada em 2026-10-05).** O parágrafo acima
> descreve o desenho da 012. A 019 acrescentou ao `RegistroDoSnapshot`, pela migração
> `analitico/0002_registro_participacao`:
>
> - `participacao` (FK → `participacao.Participacao`, anulável, `PROTECT`): o snapshot
>   passa a **congelar** qual Participação oficial pertence ao registro. A Conclusão de
>   uma Participação declarada validada só é conhecida depois da validação, e o par
>   (Campanha, Conclusão) deixou de bastar para encontrá-la;
> - `origem_formacao` (`institucional` | `declarada_validada_fonte_digital` |
>   `declarada_validada_acervo`, anulável), com o CHECK `registro_origem_com_participacao`:
>   os dois campos são ambos nulos (registro sem Participação) ou ambos preenchidos.
>
> A migração preenche os snapshots já existentes de forma determinística: até a 019, toda
> Participação era institucional (019 research R14). Participações em quarentena não
> entram no universo (019 FR-100 a FR-106). Fonte de verdade:
> `trajetoria/analitico/models.py`.

### 1.4 Imutabilidade

- Nenhuma operação altera ou remove snapshot ou registro (spec FR-050). A única escrita é a
  captura, que cria ambos numa transação.
- Mesmo regime da ADR 0002: garantido pela operação de domínio (único caminho de escrita)
  e por testes. Escrita direta no banco fora das operações não é protegida nesta fase.

## 2. Objetos de valor em memória

Todos `@dataclass(frozen=True)`, em `trajetoria/analitico/consultas.py`.

### 2.1 `ContextoCongelado`

`curso`, `unidade`, `nivel`, `modalidade`, `forma_oferta`, `ano_conclusao`,
`data_conclusao`, cada um possivelmente `None` ("não informado"). Categoria:
**institucional, no momento da captura** (spec FR-044).

### 2.2 `ParticipacaoNoDataset`

| Campo | Observação |
|-------|------------|
| `id` | Identificador técnico interno da Participação; não é identificador exportável |
| `iniciada_em` | Da 005 |
| `concluida_em` | Da 006; `None` = não concluída |

Propriedade `concluida -> bool`. Não guarda a instância de `Participacao`, para que nenhum
acesso leve a Conclusão ou Pessoa (research R12).

### 2.3 `RespostaNoDataset`

Uma Resposta preservada, na estrutura semântica da 005, **sem** a instância de `Resposta`
(que alcançaria Participação, Conclusão e Pessoa por `resposta.participacao`).

| Campo | Observação |
|-------|------------|
| `pergunta` | Instância de `Pergunta` da Versão aplicada (002, imutável). `Pergunta` não tem acessor reverso para Resposta (`related_name="+"`), então não leva à Participação |
| `opcao_id` | `UUID \| None`; escolha única. Mantido porque `percurso.respondidas` (006) lê só `opcao_id` |
| `opcao` | `Opcao \| None`; escolha única (002; sem acessor reverso para Resposta) |
| `opcoes` | `tuple[Opcao, ...]`; escolha múltipla, na ordem do instrumento; `()` nos demais tipos |
| `texto` | `str \| None`; texto curto |
| `escala` | `int \| None`; escala |
| `complemento` | `str \| None`; complemento textual da Opção que o admite |

Categoria: **declarado**. Nenhuma serialização, nenhum nome de coluna, nenhuma conversão
de escolha múltipla.

### 2.4 `LinhaDoDataset`

| Campo | Tipo | Observação |
|-------|------|------------|
| `conclusao_id` | UUID | Referência técnica interna (spec FR-047) |
| `elegivel_no_snapshot` | bool | Derivado, congelado |
| `contexto` | `ContextoCongelado` | Institucional, congelado |
| `participacao` | `ParticipacaoNoDataset \| None` | `None` = sem Participação |
| `respostas` | mapeamento imutável `id da Pergunta → RespostaNoDataset` | **Declarado**; todas as preservadas; vazio sem Participação |
| `fora_do_percurso` | `frozenset[UUID] \| None` | `∅` para concluída e para linha sem Participação; para não concluída, Perguntas com Resposta fora do percurso (006); `None` = percurso não determinável: estrutura não suportada ou Respostas rejeitadas pela 006 (research R9) |

Leitura de uma Resposta de rascunho: ativa no percurso se sua Pergunta não está em
`fora_do_percurso`; inativa (preservada fora do percurso) se está; não determinável se
`fora_do_percurso` é `None`. Nenhuma propriedade adicional.

Estes objetos são **semânticos e mínimos**. Não são schema tabular, definição de colunas,
serializador nem formato de exportação: tudo isso é da 013.

### 2.5 `IndicadoresDoSnapshot`

| Campo | Definição |
|-------|-----------|
| `elegiveis` | Registros com `elegivel_no_snapshot = True` — **denominador histórico** |
| `iniciadas_elegiveis` | Registros elegíveis com Participação |
| `iniciadas_nao_elegiveis` | Registros não elegíveis com Participação |
| `concluidas_elegiveis` | Registros elegíveis com Participação concluída |
| `concluidas_nao_elegiveis` | Registros não elegíveis com Participação concluída |

Propriedades derivadas: `iniciadas`, `concluidas`, `nao_concluidas` (e as mesmas por
elegibilidade); `registros = elegiveis + iniciadas_nao_elegiveis` (todo registro não
elegível tem Participação, por construção do universo, spec FR-030 e FR-034); `taxa_inicio = iniciadas ÷ elegiveis` e `taxa_conclusao = concluidas ÷
elegiveis`, `Decimal | None` (`None` com `elegiveis = 0`), sem teto e sem arredondamento.
Soma (`+`) definida para que a soma das linhas de um recorte seja comparável aos totais.

### 2.6 `RecorteDoSnapshot` (Enum) e `LinhaDoRecorte`

Seis valores fechados, com os campos congelados que formam a chave:

| Valor | Campos |
|-------|--------|
| `UNIDADE` | `unidade` |
| `CURSO` | `unidade`, `curso` |
| `NIVEL` | `nivel` |
| `MODALIDADE` | `modalidade` |
| `FORMA_OFERTA` | `forma_oferta` |
| `ANO_CONCLUSAO` | `ano_conclusao` |

`LinhaDoRecorte(chave: tuple, indicadores: IndicadoresDoSnapshot)`; `None` na chave =
não informado. Sem rótulos de apresentação (são da 013).

## 3. Regras de derivação

| Regra | Definição | Spec |
|-------|-----------|------|
| Universo | `populacao_no_momento(campanha) ∪ {Conclusões com Participação na Campanha}`, por Conclusão | FR-030 |
| Elegível no snapshot | `True` se a Conclusão veio de `populacao_no_momento(campanha)` lida pela captura; `False` se veio só das Conclusões com Participação | FR-020, FR-021 |
| Denominador histórico | `count(registros elegíveis)` = Conclusões da população da 004 lidas pela captura | FR-034 |
| Iniciada | Existe Participação (Campanha do snapshot, `conclusao_id` do registro) | FR-082 |
| Concluída | Essa Participação tem `concluida_em` | FR-082 |
| Fora do percurso (rascunho) | Funções puras da 006 sobre a Versão aplicada e as Respostas preservadas | FR-075 |

## 4. Estados

Nenhum. O snapshot existe completo ou não existe. Nenhuma máquina de estados, nenhum
status. A condição de captura usa só o estado derivado e o momento de abertura da 004.
