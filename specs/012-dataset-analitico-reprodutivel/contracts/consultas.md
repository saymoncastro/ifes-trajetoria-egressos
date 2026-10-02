# Contrato: consultas do snapshot (Feature 012)

Módulo `trajetoria/analitico/consultas.py`. **Nada aqui grava.** Toda função que lê um
snapshot **recebe o snapshot explicitamente** (spec FR-064). Objetos de valor em
[data-model.md](../data-model.md#2-objetos-de-valor-em-memória).

`__all__` = `ContextoCongelado`, `IndicadoresDoSnapshot`, `LinhaDoDataset`,
`LinhaDoRecorte`, `ParticipacaoNoDataset`, `RecorteDoSnapshot`, `RespostaNoDataset`,
`indicadores_do_snapshot`, `linhas_do_dataset`, `recorte_do_snapshot`,
`snapshots_da_campanha`.

**Não existe**, por decisão (Clarifications 2026-10-02; DP-1201): `snapshot_atual`,
`snapshot_vigente`, `ultimo_snapshot`, `snapshot_mais_recente` ou qualquer função que
escolha um snapshot.

## Regras comuns de leitura

- **Nunca a Conclusão atual**: nenhuma consulta desta seção lê tabela da 001 (Conclusão ou
  Pessoa). Verificado em teste pelas consultas SQL executadas (spec FR-076, FR-080; SC-010).
- **Participação é lida pela Campanha do snapshot e pela `conclusao_id` do registro**,
  nunca pela Conclusão.
- **Determinismo**: o mesmo snapshot devolve sempre o mesmo resultado, qualquer que seja o
  estado posterior da fonte acadêmica (spec FR-086).
- **Linguagem**: o denominador é "elegíveis no snapshot", nunca "elegíveis atuais" (spec
  FR-090). Esta camada não tem textos de interface; docstrings usam esse vocabulário.

## `snapshots_da_campanha(campanha) -> QuerySet[SnapshotAnalitico]`

Todos os snapshots da Campanha, em ordem `(capturado_em, id)`. **Ordem administrativa, sem
autoridade institucional** (spec FR-063). Não filtra, não deduplica, não marca nenhum.
Junto com `encerramento(campanha)` da 004, permite ver a distância entre encerramento e
captura.

## `indicadores_do_snapshot(snapshot) -> IndicadoresDoSnapshot`

Uma consulta agrupada pela elegibilidade sobre os registros do snapshot, com um `Exists`
de Participação e um de Participação concluída, cada um **uma vez** no SQL; a separação
por elegibilidade vem do agrupamento, não de filtros repetidos (research R11) (ajuste da revisão de código de 2026-10-02).

| Indicador | Definição | Spec |
|-----------|-----------|------|
| `elegiveis` | registros com `elegivel_no_snapshot` | FR-034, FR-081 |
| `iniciadas_*` | registros com Participação, por elegibilidade | FR-081, FR-082 |
| `concluidas_*` | registros com Participação concluída, por elegibilidade | FR-081, FR-082 |
| `taxa_inicio`, `taxa_conclusao` | todas as iniciadas/concluídas ÷ `elegiveis`; `None` se `elegiveis = 0`; sem teto | FR-083 |

Nenhuma Resposta é lida (spec FR-112). Contagens de Conclusões e Participações, nunca de
Pessoas (spec FR-084).

## `recorte_do_snapshot(snapshot, recorte: RecorteDoSnapshot) -> tuple[LinhaDoRecorte, ...]`

Uma consulta agrupada por `recorte.campos` e pela elegibilidade, com os mesmos dois
`Exists` (uma vez cada) e `order_by()` vazio; nenhuma consulta por linha (spec FR-112).
`RecorteDoSnapshot` tem identificador próprio por membro e `campos` como atributo, para
que dois recortes com os mesmos campos nunca virem aliases do Enum.

- A chave usa **somente** os campos congelados; curso é `(unidade, curso)` (spec FR-045,
  FR-085).
- `None` na chave = não informado; forma uma linha própria.
- Ordem das linhas: determinística pela chave, com `None` por último. Sem significado.
- Soma das linhas = `indicadores_do_snapshot(snapshot)` (spec FR-085).
- Sem linhas com zero acrescentadas: só valores presentes nos registros. As linhas com
  zero da 011 são apresentação dela.

## `linhas_do_dataset(snapshot) -> Iterator[LinhaDoDataset]`

A fronteira de leitura **mínima** que a 013 poderá consumir (spec FR-070 a FR-077). Ela
prova que o snapshot se combina com os fatos históricos preservados; não define formato.

**Comportamento**:

1. Carrega uma vez a Versão aplicada (`snapshot.campanha.versao`) e seu conteúdo
   (`conteudo_da_versao`, 002).
2. Lê os registros do snapshot em ordem `conclusao_id` (só determinismo).
3. Uma consulta de Participações da Campanha do snapshot; uma consulta de Respostas
   dessas Participações, com Pergunta e Opção (`select_related`) e Opções selecionadas
   (`prefetch_related`). Nenhuma consulta por linha.
4. Converte cada `Resposta` lida em `RespostaNoDataset` (Pergunta, `opcao_id`, Opção,
   Opções selecionadas em tupla, texto, escala, complemento). Nenhuma instância de
   `Resposta` sai da função.
5. Para cada registro, produz `LinhaDoDataset`:
   - sem Participação → `participacao=None`, `respostas` vazio, `fora_do_percurso=∅`;
   - Participação concluída → `respostas` = todas as preservadas (todas do percurso final;
     006 FR-032), `fora_do_percurso=∅`, sem recálculo;
   - Participação não concluída → `respostas` = todas as preservadas; `fora_do_percurso` =
     `frozenset(respostas) − perguntas_do_percurso(percorrer(conteudo,
     respondidas(respostas)))`, pelas funções puras da 006 (`respondidas` lê só
     `opcao_id`, presente em `RespostaNoDataset`); `None` (não determinável) se a Versão
     tiver estrutura não suportada — verificado **uma vez** por leitura, com
     `secoes_nao_suportadas` — ou se `percorrer` rejeitar as Respostas daquela
     Participação (só por escrita fora das operações). A leitura das demais linhas nunca é
     interrompida (ajuste da revisão de código de 2026-10-02).

**Volume**: a leitura carrega as Participações e Respostas da Campanha numa só passada.
Leitura em blocos só se justifica com evidência de volume real e, se vier, é mudança local
à função, sem alterar o contrato (research R12).

**Garantias**:

| Garantia | Spec |
|----------|------|
| Nada é gravado nem copiado; a combinação existe só em memória | FR-070, FR-071 |
| Respostas associadas à Pergunta da Versão aplicada | FR-072 |
| Contexto (institucional), Respostas (declarado) e elegibilidade/situação (derivado) em campos separados; nenhum substitui o outro; Q14 continua Resposta | FR-073 |
| Respostas na estrutura da 005; sem colunas por Pergunta, sem serializar escolha múltipla | FR-074 |
| Concluída × não concluída distinguíveis; Respostas fora do percurso de rascunho preservadas e distinguíveis, nunca como de concluída; sem "abandono" ou "recusa" | FR-075 |
| Nenhuma leitura da Conclusão atual nem da Pessoa; nenhum objeto entregue (nem aninhado) permite navegar até Conclusão, Pessoa ou Participação: sem instâncias de `Resposta`, `Participacao`, `RegistroDoSnapshot`, `ConclusaoAcademica` ou `Pessoa`; `Pergunta` e `Opcao` não têm acessor reverso para Resposta | FR-076 |
| Nenhuma correspondência entre Perguntas de Versões diferentes | FR-077 |
| Número de consultas independente do número de Conclusões (sem N+1) | FR-110 |
| Mínima: nenhum schema, coluna, serializador, achatamento, nome externo, CSV ou GeN | FR-070, FR-074 |

**Identificadores**: `conclusao_id` e `participacao.id` são **referências técnicas
internas**. Não são identificadores exportáveis. Expor qualquer identificador é decisão
da 013, sob 005/DP-505 (spec FR-047).

**Respostas sensíveis**: lidas das tabelas da 005 e entregues como `RespostaNoDataset`, em
memória, sem nenhuma nova gravação. Governança e minimização da
exportação são da 013 (spec FR-121).
