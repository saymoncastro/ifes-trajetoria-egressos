# Contrato: operações de exportação (Feature 013)

Pacote `trajetoria/exportacao/`, que não é app Django (research R2). **Nada aqui grava**:
nem banco, nem disco, nem log de conteúdo (spec FR-005, FR-114). Toda operação **recebe o
snapshot explicitamente** (spec FR-001).

**Não existe**, por decisão (012/DP-1201):

- `exportar_campanha`, `exportar_ultimo`, `exportar_atual` ou qualquer função que escolha
  snapshot;
- parâmetro de formato: são duas funções explícitas, CSV e XLSX (spec FR-132);
- view, rota, URL, comando, API ou regra de governança (spec FR-100, FR-101).

## `dataset_exportado(snapshot) -> DatasetExportado`

Módulo `dataset.py`. Monta o dataset lógico (Dados, Dicionário, Metadados) de
[data-model.md](../data-model.md), com valores Python tipados. É a única fonte dos dois
formatos.

**Passos**:

1. Exigir `SnapshotAnalitico`; caso contrário, `TypeError`, sem consulta.
2. Exigir snapshot gravado; caso contrário, `ExportacaoRecusada(SNAPSHOT_NAO_GRAVADO)`.
3. Ler e validar a chave de pseudonimização; caso falhe, `ExportacaoRecusada(CHAVE_AUSENTE
   | CHAVE_INADEQUADA)`, antes de ler qualquer linha.
4. Ler a Campanha do snapshot e o conteúdo da sua Versão. Versão não PUBLICADA gera
   `ExportacaoInconsistente`.
5. Montar as colunas a partir da Versão e verificar a unicidade dos nomes.
6. Ler a referência Conclusão → Pessoa dos registros do snapshot, numa consulta.
7. Percorrer `linhas_do_dataset(snapshot, conteudo=conteudo)` (012), reutilizando o conteúdo
   já lido no passo 4 e montar cada linha (data-model §1.3). Toda
   inconsistência gera `ExportacaoInconsistente`.
8. Montar Metadados (contagens derivadas das linhas) e Dicionário.

**Garantias**:

- **Reprodutibilidade**: `dataset_exportado(s) == dataset_exportado(s)` com a mesma chave,
  qualquer que seja o estado acadêmico atual, o nome da Pesquisa ou um encerramento gravado
  depois da captura.
- **Consultas**: número fixo, independente do número de registros.
- **Nunca lê**: atributo de Pessoa, contexto da Conclusão atual, população atual (004),
  `encerrada_em`, nome da Pesquisa.

## `exportar_csv(snapshot) -> bytes`

Módulo `formatos.py`. Devolve o **pacote ZIP** com `dados.csv`, `dicionario.csv` e
`metadados.csv`, na forma de [pacote-de-dados.md](pacote-de-dados.md).

- Serializa `dataset_exportado(snapshot)`, sem decidir nenhum valor.
- Aplica o escape contra fórmula em todo campo textual.
- O mesmo snapshot com a mesma chave gera bytes idênticos (entradas do ZIP com data fixa).

## `csv_do_dataset(dataset)` e `xlsx_do_dataset(dataset) -> bytes`

Serializam um `DatasetExportado` já montado. `exportar_csv(snapshot)` e
`exportar_xlsx(snapshot)` são exatamente `csv_do_dataset(dataset_exportado(snapshot))` e
`xlsx_do_dataset(dataset_exportado(snapshot))`.

- Servem a quem precisa dos dois formatos do mesmo snapshot sem ler e montar tudo de novo.
- O dataset só nasce de `dataset_exportado(snapshot)`, então o snapshot continua explícito.
- Qualquer argumento que não seja `DatasetExportado` gera `TypeError`.

## `exportar_xlsx(snapshot) -> bytes`

Módulo `formatos.py`. Devolve a pasta de trabalho com as abas `Dados`, `Dicionário` e
`Metadados`, na forma de [pacote-de-dados.md](pacote-de-dados.md#xlsx).

- Serializa `dataset_exportado(snapshot)`.
- Grava texto como texto (nunca fórmula), sem escape.
- Valor não representável sem alteração gera `ValorNaoRepresentavel` (research R12).

## Vocabulário de erro (`regras.py`)

| Exceção | Motivo / quando | Grava algo? |
|---------|-----------------|-------------|
| `TypeError` | argumento não é `SnapshotAnalitico` | não |
| `ExportacaoRecusada` | `Motivo.SNAPSHOT_NAO_GRAVADO`, `Motivo.CHAVE_AUSENTE`, `Motivo.CHAVE_INADEQUADA` | não |
| `ExportacaoInconsistente` | Versão não publicada; tipo de Pergunta desconhecido; forma de Resposta incompatível com o tipo; Opção alheia à Pergunta; complemento sem Opção que o admita; concluída com percurso não determinável ou com Resposta fora do percurso; nome de coluna repetido | não |
| `ValorNaoRepresentavel` (subclasse de `ExportacaoInconsistente`) | texto com mais de 32.767 caracteres ou com caractere proibido no XLSX | não |

**Mensagens** citam motivo, identificador do snapshot, identificador de Pergunta ou Opção,
nome de coluna, número de linha e contagens. Nunca citam valor acadêmico, conteúdo de
Resposta, identificador interno de Pessoa ou Conclusão, pseudônimo ou chave (spec FR-093).

## Configuração

| Variável de ambiente | Uso | Ausente |
|----------------------|-----|---------|
| `TRAJETORIA_CHAVE_PSEUDONIMIZACAO` | Chave do HMAC dos pseudônimos analíticos; ≥ 32 caracteres; diferente de `DJANGO_SECRET_KEY` | Toda exportação é recusada (`CHAVE_AUSENTE`) |

Quem administra, guarda e rotaciona a chave é **DP-1301**. Trocar a chave rompe a ligação
com exportações anteriores, por definição (spec FR-027).

## Exposição futura (não implementada)

A feature que expuser estas operações:

- DEVE restringi-las à atuação **CPAEG** ativa, em escopo institucional (spec FR-102);
- NÃO DEVE oferecê-las à CSAEG (FR-103);
- decide nome de arquivo, que PODE conter um prefixo curto do snapshot e nunca pseudônimo
  ou identificador de Pessoa, Conclusão ou Participação (FR-080);
- decide entrega, por exemplo resposta HTTP sem gravar em disco (FR-114);
- respeita DP-1301 e DP-1302.
