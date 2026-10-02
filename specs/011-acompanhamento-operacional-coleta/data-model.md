# Data Model: Acompanhamento operacional da coleta (Feature 011)

## 1. Persistência

**Nenhuma entidade, tabela, coluna, índice ou migration nova** (spec FR-130; research R1).

Entidades existentes, **somente lidas**, e os campos efetivamente usados:

| Entidade (feature) | Campos lidos | Para quê |
|--------------------|--------------|----------|
| `Campanha` (004) | `id`, `nome`, `versao`, `inicio`, `fim`, `ano_minimo`, `ano_maximo`, `unidades`, `niveis`, `modalidades`, `formas_oferta`, `aberta_em`, `encerrada_em` | visibilidade, critério de população, estado, cabeçalho |
| `Versao`, `Pesquisa` (002) | `designacao`, `estado`; `nome` | instrumento aplicado (R11) |
| `ConclusaoAcademica` (001) | `id` (só em `Count`), `unidade`, `curso`, `nivel`, `modalidade`, `forma_oferta`, `ano_conclusao` | elegíveis atuais, escopo, recortes |
| `Participacao` (005/006) | `id` (só em `Count`), `campanha`, `conclusao` (só para a junção com os atributos acima), `concluida_em` | iniciadas, concluídas |
| `VinculoDeGovernanca` (010) | `papel`, `unidade`, `ativo` | capacidade e escopo |

**Nunca lidas**: `Pessoa`, `ConclusaoAcademica.id_externo`, `ConclusaoAcademica.fonte`,
`ConclusaoAcademica.data_conclusao`, `Resposta`, `RespostaOpcao`, `Secao`, `Pergunta`,
`Opcao`.

## 2. Objetos de valor em memória

Todos são `dataclass(frozen=True)`, recalculados a cada requisição e nunca gravados. Cada
um tem consumidor real: views, templates e testes.

### 2.1 `EscopoDeAcompanhamento` (`trajetoria/governanca/regras.py`)

| Campo | Tipo | Significado |
|-------|------|-------------|
| `institucional` | `bool` | `True` se há vínculo CPAEG ativo |
| `unidades` | `frozenset[str]` | Unidades dos vínculos CSAEG ativos; vazio quando institucional |

Invariantes:

- `institucional ⇒ unidades == ∅`;
- `¬institucional ⇒ unidades ≠ ∅`.

O escopo inexistente é representado por `None` (sem acompanhamento).

### 2.2 `Indicadores` (`trajetoria/acompanhamento/consultas.py`)

| Campo / propriedade | Tipo | Definição (spec) |
|---------------------|------|------------------|
| `elegiveis` | `int` | FR-030 |
| `iniciadas` | `int` | FR-032 |
| `concluidas` | `int` | FR-033 |
| `nao_concluidas` (prop.) | `int` | `iniciadas − concluidas` (FR-034) |
| `taxa_inicio` (prop.) | `Decimal \| None` | `None` se `elegiveis == 0`; senão `iniciadas × 100 ÷ elegiveis`, `ROUND_HALF_UP`, 1 casa (FR-035 a FR-037) |
| `taxa_conclusao` (prop.) | `Decimal \| None` | idem com `concluidas` |

Regras:

- Sem limite superior: a taxa pode passar de 100 (FR-038).
- `Indicadores` soma por `+`, para os testes de "soma das linhas = total" e para montar
  linhas.

### 2.3 `Recorte` (`Enum`, `trajetoria/acompanhamento/consultas.py`)

Vocabulário fechado de seis membros (research R7). Cada membro guarda:

- `valor` (GET);
- `rotulo`;
- `campos` (tupla de nomes de campo da Conclusão);
- `rotulo_nao_informado`.

| Membro | `valor` | `campos` | `rotulo_nao_informado` |
|--------|---------|----------|------------------------|
| `UNIDADE` | `unidade` | `("unidade",)` | "Unidade não informada" |
| `CURSO` | `curso` | `("unidade", "curso")` | "Curso não informado" (e "Unidade não informada" na primeira posição, se for o caso) |
| `NIVEL` | `nivel` | `("nivel",)` | "Nível não informado" |
| `MODALIDADE` | `modalidade` | `("modalidade",)` | "Modalidade não informada" |
| `FORMA_OFERTA` | `forma-oferta` | `("forma_oferta",)` | "Forma de oferta não informada" |
| `ANO_CONCLUSAO` | `ano-conclusao` | `("ano_conclusao",)` | "Ano de conclusão não informado" |

`Recorte.de_valor(texto) -> Recorte | None` devolve `None` para valor fora da lista, e a
view responde 404.

### 2.4 `LinhaDeRecorte`

| Campo | Tipo | Significado |
|-------|------|-------------|
| `chave` | `tuple[str \| int \| None, ...]` | Valores dos `campos` do recorte, como registrados; `None` = não informado |
| `indicadores` | `Indicadores` | Contagens da linha |

Uma Conclusão (e suas Participações) cai em exatamente uma chave, então
`sum(linhas) == totais` (FR-052).

### 2.5 `CampanhaAcompanhada`

Usado na lista (sem recorte) e no detalhe (com recorte).

| Campo | Tipo | Origem |
|-------|------|--------|
| `campanha` | `Campanha` | só para `id`, `nome`, `inicio`, `fim`, `aberta_em`, `encerrada_em` e critérios |
| `estado` | `EstadoCampanha` | `campanha.consultas.estado` (004) |
| `encerramento` | `(FormaEncerramento, datetime) \| None` | `campanha.consultas.encerramento` (004) |
| `instrumento` | `Instrumento` (texto + link opcional) | research R11 |
| `indicadores` | `Indicadores` | totais no escopo |
| `recorte` | `Recorte \| None` | só no detalhe |
| `linhas` | `tuple[LinhaDeRecorte, ...]` | só no detalhe, já ordenadas (R8) |
| `recortes_oferecidos` | `tuple[Recorte, ...]` | só no detalhe (FR-057) |

`Instrumento`: `texto: str`, `endereco: str | None`.

## 3. Funções de consulta (contrato interno)

Detalhadas em [contracts/consultas.md](contracts/consultas.md). Em resumo:

```text
campanhas_visiveis(escopo) -> QuerySet[Campanha]
campanhas_acompanhadas(escopo, atuacao) -> tuple[CampanhaAcompanhada, ...]       # lista
campanha_acompanhada(campanha, escopo, atuacao, recorte) -> CampanhaAcompanhada  # detalhe
unidades_relevantes(campanha, escopo) -> frozenset[str] | None                   # só apresentação; None = institucional
```

## 4. Regras de derivação

```text
Escopo (por requisição):
  CPAEG ativo                → institucional
  senão CSAEG ativos         → unidades = { v.unidade }
  senão                      → None (recusa)

Visível(C, escopo):
  institucional              → sim
  C.unidades IS NULL         → sim
  C.unidades && escopo       → sim         (overlap, igualdade exata)
  senão                      → não

Universo(escopo) sobre ConclusaoAcademica:     (não depende da Campanha)
  institucional              → Q()
  unidades                   → Q(unidade__in = escopo.unidades)

Relevantes(C, escopo):        (só no escopo de unidades; SÓ apresentação:
                               linhas com zero, recortes oferecidos, coluna Unidade)
  C.unidades IS NULL         → escopo.unidades
  senão                      → escopo.unidades ∩ C.unidades

Elegíveis(C)  = populacao_no_momento(C).filter(Universo).count()      # predicado só da 004
Iniciadas(C)  = count(Participacao WHERE campanha = C AND conclusao ∈ Universo)
Concluídas(C) = count(Participacao WHERE campanha = C AND conclusao ∈ Universo AND concluida_em IS NOT NULL)
```

Iniciadas e concluídas **não** são filtradas pela população da 004 nem pelo critério de
unidades da Campanha (FR-023, FR-038). O critério da Campanha entra nos números apenas
por `populacao_no_momento`.

## 5. Estados

Nenhum estado novo. Os rótulos dependem do `EstadoCampanha` da 004 e de `aberta_em`
(research R10).
