# Contrato: consultas do acompanhamento (Feature 011)

Módulo `trajetoria/acompanhamento/consultas.py`. Regras do módulo:

- Nada grava.
- Nenhuma função lê `Pessoa`, `Resposta` ou `RespostaOpcao`.
- Toda contagem é feita no banco (`Count`, `aggregate`, `values().annotate()`).
- Nenhum registro individual de Conclusão ou Participação é carregado.

Os objetos de valor estão em [../data-model.md](../data-model.md) §2.

## Dependências consumidas

| Origem | Símbolo | Uso |
|--------|---------|-----|
| 004 `campanha.consultas` | `populacao_no_momento(c) -> QuerySet[ConclusaoAcademica]` (**já público; sem mudança na 004**) | Única fonte de elegibilidade: refinada pelo escopo, contada e agrupada |
| 004 `campanha.consultas` | `estado`, `encerramento`, `EstadoCampanha`, `FormaEncerramento` | Situação e avisos |
| 005/006 `participacao.models` | `Participacao` (`campanha`, `conclusao`, `concluida_em`) | Iniciadas, concluídas |
| 010 `governanca.regras` | `EscopoDeAcompanhamento`, `pode_consultar_rascunho` | Escopo; instrumento em rascunho |

## Funções

### `campanhas_visiveis(escopo) -> QuerySet[Campanha]`

- Institucional: todas.
- Unidades: `Q(unidades__isnull=True) | Q(unidades__overlap=sorted(escopo.unidades))`.

Retorno com `select_related("versao__pesquisa")`. Não depende de número, estado nem
Participação (FR-022). Usada pela lista **e** pela verificação de escopo do detalhe.

### `unidades_relevantes(campanha, escopo) -> frozenset[str] | None`

- `None` no escopo institucional.
- Senão, `escopo.unidades` se `campanha.unidades is None`.
- Senão, `escopo.unidades ∩ set(campanha.unidades)`.

Nunca vazio para Campanha visível. **Só** define as linhas com zero do recorte por
unidade. **Nunca** entra em `universo` nem em `universo_participacao` (spec FR-023,
FR-038). A oferta do recorte por unidade e a coluna Unidade do recorte por curso dependem
do escopo (`_varias_unidades`: institucional ou mais de uma unidade).

### `universo(escopo) -> Q` e `universo_participacao(escopo) -> Q`

- Institucional: `Q()`.
- Unidades: `Q(unidade__in=escopo.unidades)` e
  `Q(conclusao__unidade__in=escopo.unidades)`.

Dependem só do escopo do operador, não da Campanha.

### `indicadores_da_campanha(campanha, escopo) -> Indicadores`

Totais de uma Campanha no escopo. Usada pela lista e pelo detalhe, com duas consultas:

| # | Consulta |
|---|----------|
| a | `populacao_no_momento(c).filter(universo).count()` |
| b | `Participacao.objects.filter(campanha=c).filter(universo_participacao).aggregate(iniciadas=Count("id"), concluidas=Count("id", filter=Q(concluida_em__isnull=False)))` |

Iniciadas e concluídas **não** passam pela elegibilidade (FR-038).

### `campanhas_acompanhadas(escopo, *, pode_consultar_rascunho) -> tuple[CampanhaAcompanhada, ...]`

Lista, sem recorte. Para cada Campanha de `campanhas_visiveis(escopo)`, chama
`indicadores_da_campanha`.

O número de consultas é proporcional ao número de Campanhas (≈ 2 por Campanha), o que é
aceito no MVP (research R6). Não há agregação de várias Campanhas numa expressão só.

### `campanha_acompanhada(campanha, escopo, *, pode_consultar_rascunho, recorte) -> CampanhaAcompanhada`

Detalhe. Pré-condição: a Campanha é visível para o escopo; a view garante com
`campanhas_visiveis`. Totais por `indicadores_da_campanha` (a, b) e, para o recorte, uma
consulta de cada lado, sem consulta por linha:

| # | Consulta |
|---|----------|
| c | `populacao_no_momento(c).filter(universo).values(*recorte.campos).annotate(n=Count("id")).order_by()` |
| d | `Participacao.objects.filter(campanha=c).filter(universo_participacao).values(*("conclusao__" + f for f in recorte.campos)).annotate(iniciadas=…, concluidas=…).order_by()` |

Depois das consultas:

- **Combinação em Python** por chave: dicionário `chave -> Indicadores`, com zeros onde
  só um dos lados tem a chave.
- **Linhas com zero** (research R8): no recorte por unidade, acrescenta as chaves
  conhecidas sem dado. São as unidades do critério da Campanha; no escopo de unidades,
  as unidades relevantes.
- **Ordenação** (research R8): `None` por último; ano crescente; texto por
  `(dobrado, exato)`.

O `.order_by()` vazio em (c) e (d) remove a ordenação padrão do modelo
(`ConclusaoAcademica.Meta.ordering`, `Participacao.Meta.ordering`), que, num
`values().annotate()`, entraria no `GROUP BY` e partiria os grupos.

### `recortes_oferecidos(escopo) -> tuple[Recorte, ...]`

- Os seis no escopo institucional ou com mais de uma unidade.
- Sem `UNIDADE` quando o escopo tem uma única unidade.

## Funções de apresentação (`trajetoria/acompanhamento/apresentacao.py`)

Puras, testáveis sem banco:

| Função | Contrato |
|--------|----------|
| `percentual(taxa: Decimal \| None) -> str \| None` | `None` → `None` (o template mostra "—" / "não se aplica"); `Decimal("30.0")` → `"30,0%"`; `Decimal("112.5")` → `"112,5%"` |
| `rotulo_nao_concluidas(estado) -> str` | EM COLETA → "Em andamento"; demais → "Iniciadas e não concluídas" |
| `aviso_do_estado(campanha, estado) -> tuple[str, ...]` | Research R10 |
| `instrumento(campanha, *, pode_consultar_rascunho) -> Instrumento` | Research R11 |
| `rotulo_da_chave(recorte, chave) -> tuple[str, ...]` | Valor como registrado, ou o rótulo "não informado" da dimensão; ano como inteiro em texto |
| `chave_de_ordem(chave) -> tuple` | Research R8 |

## Invariantes verificados por teste

1. `sum(linha.indicadores for linha in linhas) == indicadores` para os seis recortes e os
   três tipos de escopo (FR-052).
2. Elegíveis da lista == elegíveis do detalhe, para cada Campanha e escopo.
3. Elegíveis (escopo institucional) == `populacao_no_momento(c).count()` da 004.
4. A soma, pelas unidades relevantes, de cada CSAEG de unidade única é igual ao recorte
   por unidade do CPAEG naquelas linhas.
5. Participação de Conclusão hoje fora do critério de unidades da Campanha (simulação de
   005/DP-507), mas na unidade do operador, conta para a CSAEG como conta para a CPAEG.
6. Nenhum SQL capturado referencia as tabelas de `Resposta` ou `RespostaOpcao`.
7. Proteção contra N+1, não requisito: o detalhe faz o mesmo número de consultas com 3 e
   com 30 valores na dimensão; a lista cresce no máximo 2 consultas por Campanha.
