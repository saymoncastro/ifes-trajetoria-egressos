# Data Model: Exportações analíticas e contrato de dados para o GeN (Feature 013)

**Nenhuma entidade persistida, nenhuma migration** (spec FR-130). Este documento descreve o
**dataset lógico** produzido a cada exportação, os objetos de valor em memória, o único
campo novo na fronteira da 012 e a configuração da chave.

Os tipos lógicos são `booleano`, `texto`, `inteiro`, `data` e `momento`. A representação
de cada um em CSV e XLSX está em [research.md R3](research.md#r3--dataset-lógico-três-tabelas-de-valores-python-tipados)
e em [contracts/pacote-de-dados.md](contracts/pacote-de-dados.md).

---

## 0. Objetos de valor (em memória, nunca gravados)

| Objeto | Campos | Observação |
|--------|--------|------------|
| `Tabela` | `cabecalho: tuple[str, ...]`; `linhas: tuple[tuple, ...]` | Imutável; cada linha tem o comprimento do cabeçalho |
| `DatasetExportado` | `dados: Tabela`; `dicionario: Tabela`; `metadados: Tabela`; `capturado_em: datetime` (timezone institucional; o mesmo valor dos Metadados) | Resultado de `dataset_exportado(snapshot)`; comparável por `==` (reprodutibilidade). `capturado_em` serve aos formatos (propriedade de criação do XLSX) sem que eles leiam a tabela de Metadados |

**Acréscimo na 012** (`trajetoria/analitico/consultas.py`, `LinhaDoDataset`):

| Campo | Tipo | Valor |
|-------|------|-------|
| `perguntas_do_percurso` | `frozenset[UUID] \| None`, padrão `None`, último campo | Perguntas das Seções do percurso da 006 para as Respostas da Participação. `None` sem Participação ou com percurso não determinável. Calculado para Participação concluída **e** não concluída (research R6) |

Os demais campos de `LinhaDoDataset` não mudam, inclusive `fora_do_percurso`.
`linhas_do_dataset(snapshot, *, conteudo=None)` aceita, opcionalmente, o conteúdo da Versão
já lido por quem chama, para não relê-lo. Se ele não for o da Versão da Campanha do
snapshot, a função levanta `ValueError` (revisão de código).

**Configuração** (não persistida): `TRAJETORIA_CHAVE_PSEUDONIMIZACAO`, lida do ambiente.
Ela é obrigatória, tem pelo menos 32 caracteres e é diferente de `SECRET_KEY` (research
R5).

---

## 1. Dados

Uma linha por registro do snapshot, na ordem da fronteira da 012 (spec FR-010, FR-082).

### 1.1 Colunas base (ordem fixa)

| # | Coluna | Tipo | Proveniência | Valor |
|---|--------|------|--------------|-------|
| 1 | `conclusao_analitica_id` | texto | derivado | HMAC-SHA-256 de `conclusao:<UUID da Conclusão>`, 64 hexadecimais |
| 2 | `pessoa_analitica_id` | texto | derivado | HMAC-SHA-256 de `pessoa:<UUID da Pessoa referenciada pela Conclusão>` |
| 3 | `elegivel_no_snapshot` | booleano | derivado | `LinhaDoDataset.elegivel_no_snapshot` |
| 4 | `unidade` | texto | institucional | `contexto.unidade` |
| 5 | `curso` | texto | institucional | `contexto.curso` |
| 6 | `nivel` | texto | institucional | `contexto.nivel` |
| 7 | `modalidade` | texto | institucional | `contexto.modalidade` |
| 8 | `forma_oferta` | texto | institucional | `contexto.forma_oferta` |
| 9 | `ano_conclusao` | inteiro | institucional | `contexto.ano_conclusao` |
| 10 | `data_conclusao` | data | institucional | `contexto.data_conclusao` |
| 11 | `possui_participacao` | booleano | coleta | `participacao is not None` |
| 12 | `participacao_concluida` | booleano | coleta | `participacao.concluida`; `None` sem Participação |
| 13 | `participacao_iniciada_em` | data | coleta | `localtime(participacao.iniciada_em).date()`; `None` sem Participação |
| 14 | `participacao_concluida_em` | data | coleta | `localtime(participacao.concluida_em).date()`; `None` se ausente |
| 15 | `origem_formacao` | texto | derivado | *(Acrescentada pela 019, contrato v2.)* `institucional`, `declarada_validada_fonte_digital` ou `declarada_validada_acervo`, conforme o registro do snapshot; `None` sem Participação |

### 1.2 Colunas de Pergunta

Ordem: Seção (posição) → Pergunta (posição) → as colunas abaixo, na ordem listada. `<p>` e
`<o>` são `UUID.hex` da Pergunta e da Opção.

| Tipo da Pergunta | Colunas, em ordem | Tipo de valor |
|------------------|-------------------|---------------|
| todos | `pergunta_<p>__aplicavel` | booleano |
| escolha única | `pergunta_<p>` | texto (texto da Opção) |
| escolha múltipla | `pergunta_<p>__opcao_<o>` para cada Opção, por posição | booleano |
| texto curto | `pergunta_<p>` | texto |
| escala | `pergunta_<p>` | inteiro |
| escolha (única ou múltipla) com Opção que admite complemento | `pergunta_<p>__complemento`, por último | texto |

### 1.3 Regras de preenchimento por linha

Sejam `L` a linha da 012, `P = L.perguntas_do_percurso` e `R = L.respostas`.

| Condição | Aplicabilidade | Colunas de valor |
|----------|----------------|------------------|
| `L.participacao is None` | `None` | `None` |
| Não concluída e `P is None` | `None` | `None`; conta em `participacoes_com_percurso_nao_determinavel` |
| Concluída e `P is None` | — | `ExportacaoInconsistente` |
| Concluída e `R.keys() ⊄ P` | — | `ExportacaoInconsistente` |
| Pergunta ∉ `P` | `False` | `None` (inclusive Resposta de rascunho preservada fora do percurso) |
| Pergunta ∈ `P`, sem Resposta | `True` | `None` (múltipla: todas `None`, nunca `False`) |
| Pergunta ∈ `P`, com Resposta | `True` | conforme o tipo (research R7); múltipla: `True`/`False` por Opção; complemento ou `None` |

**Invariantes** (verificadas em teste sobre todo o conjunto de referência):

- valor preenchido ⇒ aplicabilidade `True`;
- aplicabilidade `False` ou `None` ⇒ todas as colunas de valor `None`;
- `possui_participacao = False` ⇒ colunas 12 a 14 e todas as colunas de Pergunta `None`;
- nenhum texto vazio (`""`) em nenhuma célula: ausência é sempre `None`.

---

## 2. Dicionário

Cabeçalho fixo (24 colunas), nesta ordem:

| # | Coluna | Tipo | Preenchida em |
|---|--------|------|---------------|
| 1 | `elemento` | texto | todas: `coluna` ou `valor_possivel` |
| 2 | `coluna` | texto | todas: nome técnico da coluna de Dados |
| 3 | `ordem` | inteiro | todas: posição 1-based da coluna em Dados |
| 4 | `tipo_valor` | texto | todas: `booleano`, `texto`, `inteiro` ou `data` |
| 5 | `proveniencia` | texto | todas: `institucional`, `derivado`, `coleta` ou `declarado` |
| 6 | `descricao` | texto | todas |
| 7 | `versao` | texto | todas: identificador da Versão (forma canônica) |
| 8 | `secao_posicao` | inteiro | colunas de Pergunta e valores possíveis |
| 9 | `secao_titulo` | texto | idem, quando a Seção tem título |
| 10 | `secao_encaminhamento_destino` | inteiro | idem, quando a Seção tem encaminhamento: posição da Seção de destino |
| 11 | `pergunta_posicao` | inteiro | colunas de Pergunta e valores possíveis |
| 12 | `pergunta_tipo` | texto | idem: `escolha_unica`, `escolha_multipla`, `texto_curto`, `escala` |
| 13 | `pergunta_texto` | texto | idem |
| 14 | `pergunta_texto_explicativo` | texto | idem, quando existe |
| 15 | `pergunta_obrigatoria` | booleano | idem |
| 16 | `opcao_posicao` | inteiro | colunas de Opção, de complemento e valores possíveis |
| 17 | `opcao_texto` | texto | idem |
| 18 | `opcao_admite_complemento` | booleano | idem |
| 19 | `opcao_regra_finaliza` | booleano | idem |
| 20 | `opcao_regra_destino_secao` | inteiro | idem, quando a regra é "ir para Seção": posição da Seção |
| 21 | `escala_inicio` | inteiro | colunas de escala |
| 22 | `escala_fim` | inteiro | colunas de escala |
| 23 | `escala_rotulo_inicio` | texto | colunas de escala, quando existe |
| 24 | `escala_rotulo_fim` | texto | colunas de escala, quando existe |

**Linhas**:

- Uma linha `coluna` para cada coluna de Dados, na ordem de Dados.
- Para cada Pergunta de escolha única, logo após a linha `coluna` de `pergunta_<p>`, uma
  linha `valor_possivel` por Opção, na ordem das Opções, com:
  - `coluna = pergunta_<p>`, `ordem` igual à da coluna, `tipo_valor = texto`,
    `proveniencia = declarado`;
  - `descricao` = "Valor possível da coluna: o texto da Opção";
  - campos de Opção preenchidos.
- **Linhas de complemento**: campos de Opção da Opção que admite complemento.
- **Linhas de aplicabilidade**: campos de Seção e Pergunta preenchidos, campos de Opção
  vazios.

**Proveniência por coluna**:

| Proveniência | Colunas |
|--------------|---------|
| `derivado` | 1 a 3, 15 (desde a 019) e aplicabilidade |
| `institucional` | 4 a 10 |
| `coleta` | 11 a 14 (fatos registrados pelo sistema durante a coleta; não é dado institucional, derivado nem declarado) |
| `declarado` | valor, Opção e complemento |

**Descrições**: texto fixo do contrato para as colunas base
([contracts/pacote-de-dados.md](contracts/pacote-de-dados.md#descrições-das-colunas-base)).
Para as colunas de Pergunta, modelo fixo por papel:

- **aplicabilidade**: "Indica se a Pergunta pertence ao percurso calculado da Participação:
  verdadeiro = pertence; falso = fora do percurso; vazio = sem Participação ou percurso não
  determinável."
- **valor**: "Resposta declarada à Pergunta (ver pergunta_texto)."
- **Opção**: "Indica se a Opção foi escolhida: verdadeiro = escolhida; falso = não
  escolhida; vazio = sem Resposta válida."
- **complemento**: "Complemento textual declarado com a Opção que o admite."

---

## 3. Metadados

Cabeçalho: `chave`, `valor`, `tipo`. O `tipo` é um de `texto`, `inteiro`, `data`,
`momento`. As linhas seguem esta ordem fixa:

| # | `chave` | `tipo` | Origem | Fixo para o snapshot porque |
|---|---------|--------|--------|------------------------------|
| 1 | `contrato_versao` | inteiro | constante `VERSAO_CONTRATO` (1 na 013; 2 desde a 019) | constante |
| 2 | `pseudonimizacao_esquema` | texto | constante `hmac-sha256-v1` | constante |
| 3 | `finalidade` | texto | nota fixa | constante |
| 4 | `snapshot` | texto | `snapshot.id` | imutável (012) |
| 5 | `capturado_em` | momento | `snapshot.capturado_em` | imutável (012) |
| 6 | `campanha` | texto | `campanha.id` | imutável |
| 7 | `campanha_nome` | texto | `campanha.nome` | só alterável nunca aberta (004) |
| 8 | `campanha_inicio` | data | `campanha.inicio` | idem |
| 9 | `campanha_fim` | data | `campanha.fim` | idem |
| 10 | `campanha_aberta_em` | momento | `campanha.aberta_em` | gravado uma vez (004) |
| 11 | `versao` | texto | `conteudo.id` | imutável |
| 12 | `versao_designacao` | texto | `conteudo.designacao` | só alterável em rascunho (002) |
| 13 | `versao_titulo` | texto | `conteudo.titulo` (pode ser vazio) | idem |
| 14 | `versao_publicada_em` | momento | `conteudo.publicada_em` | gravado na publicação |
| 15 | `registros` | inteiro | linhas de Dados | snapshot imutável |
| 16 | `elegiveis_no_snapshot` | inteiro | linhas com `elegivel_no_snapshot` | idem |
| 17 | `nao_elegiveis_com_participacao` | inteiro | linhas não elegíveis com Participação | idem + Participação imutável |
| 18 | `com_participacao` | inteiro | linhas com Participação | idem |
| 19 | `participacoes_concluidas` | inteiro | linhas com Participação concluída | idem |

As contagens 15 a 19 são derivadas das próprias linhas montadas, com as definições da 012
(iniciada = Participação existente; concluída inclusive por recusa). Os testes conferem que
são iguais a `indicadores_do_snapshot` (012), sem uma consulta a mais por exportação.
| 20 | `participacoes_com_percurso_nao_determinavel` | inteiro | construção de Dados (§1.3) | idem + Versão e Respostas imutáveis |
| 21 | `colunas_de_dados` | inteiro | `len(dados.cabecalho)` | depende só da Versão |
| 22 | `nota_snapshot` | texto | nota fixa | constante |
| 23 | `nota_privacidade` | texto | nota fixa | constante |
| 24 | `nota_representacao` | texto | nota fixa | constante |
| 25 | `nota_proveniencia` | texto | nota fixa | constante |
| 26 | `nota_aplicabilidade` | texto | nota fixa | constante |
| 27 | `nota_escape_csv` | texto | nota fixa | constante |

**Ausentes por decisão**:

- nome da Pesquisa (mutável);
- `encerrada_em` (não congelado; research R8);
- momento da exportação;
- chave ou qualquer derivação dela;
- nome ou identificador de quem exportou.

Os textos exatos das notas estão em
[contracts/pacote-de-dados.md](contracts/pacote-de-dados.md#notas-fixas).

---

## 4. Derivações e validações (resumo)

| Derivação/validação | Regra | Spec |
|---------------------|-------|------|
| Pseudônimos | HMAC-SHA-256, chave dedicada, domínio `conclusao`/`pessoa`, hexadecimal | FR-027, FR-028 |
| Aplicabilidade | `pergunta.id in perguntas_do_percurso` | FR-047 |
| Datas da Participação | `localtime(...).date()`, timezone institucional | FR-025 |
| Forma da Resposta | research R7 | FR-092 |
| Unicidade de nomes de coluna | conjunto = lista | FR-033, FR-092 |
| Representabilidade no XLSX | research R12 | FR-091 |
| Contagens dos Metadados × Dados | iguais (verificado em teste) | FR-013 |
