# Feature Specification: Exportações analíticas e contrato de dados para o GeN

**Feature Branch**: `claude/feature-013-analytics-exports-190965`

**Created**: 2026-10-02

**Status**: Draft

**Input**: User description: "Feature 013 — Exportações analíticas e contrato de dados para
o GeN. Disponibilizar os dados de um SnapshotAnalitico explicitamente informado em formato
tabular (CSV e XLSX), documentado (dicionário e metadados) e interoperável, para análise
institucional e consumo posterior pelo GeN, sem criar nova fonte de verdade, sem escolher
snapshot implicitamente, sem persistir exportações, sem job, sem BI e sem acoplar o
domínio a ferramenta downstream."

## Contexto

As doze primeiras features estabeleceram, entre outros:

- **002** — Versão PUBLICADA imutável, com Seções (posição), Perguntas (posição na Seção,
  tipo, texto, texto explicativo, obrigatoriedade, limites e rótulos de escala) e Opções
  (posição na Pergunta, texto único na Pergunta, no máximo uma Opção por Pergunta que
  admite complemento textual, regra de navegação "ir para Seção" ou "finaliza"). Cada
  Seção, Pergunta e Opção tem identificador técnico próprio, **local à Versão**: uma
  Versão derivada tem elementos novos, e nenhuma correspondência entre Versões existe
  (002/DP-006).
- **Tipos de Pergunta existentes**, e somente eles: **escolha única**, **escolha
  múltipla**, **texto curto** e **escala** (inteiro entre início e fim).
- **005** — **Resposta**: uma por Pergunta numa Participação. Forma do valor por tipo:
  Opção escolhida (escolha única); conjunto não vazio de Opções, sem ordem de seleção
  (escolha múltipla); texto gravado exatamente como recebido, nunca vazio (texto curto);
  inteiro dentro dos limites (escala). O **complemento** é texto não vazio e só existe
  quando a Opção escolhida (ou uma das escolhidas) admite complemento.
- **006** — Participação **concluída** (conclusão registrada, irreversível) ou **não
  concluída** (em rascunho no encerramento). Ao concluir, as Respostas fora do percurso
  são removidas; num rascunho, elas permanecem preservadas. Q1 = "Não" conclui a
  Participação, que conta como concluída (006/DP-601).
- **010** — atuações **CPAEG** (institucional) e **CSAEG** (unidade).
- **011** — "como está a coleta agora?", com agregados e elegíveis atuais.
- **012** — **snapshot analítico** imutável de Campanha encerrada: um **registro** por
  Conclusão Acadêmica do universo (elegíveis no momento da captura ∪ Conclusões com
  Participação), com elegibilidade congelada e contexto acadêmico congelado. Expõe uma
  **fronteira de leitura** que recebe o snapshot explicitamente e entrega, por registro:
  contexto congelado, elegibilidade, a Participação (início, conclusão) se existir, as
  Respostas na semântica da 005 e, para Participação não concluída, quais Respostas estão
  **fora do percurso** (ou que o percurso não é determinável). Formato, colunas,
  achatamento, serialização de escolha múltipla e identificadores expostos foram deixados
  para esta feature (012 FR-070, FR-074, FR-047).

Esta feature responde:

> **"Como disponibilizar os dados de um snapshot analítico em formato tabular,
> documentado e interoperável, para análise institucional e consumo posterior pelo
> GeN?"**

### Princípios desta spec

1. **Todo export tem um snapshot explicitamente informado.** Não existe "Campanha atual",
   "snapshot mais recente", "vigente" ou "oficial implícito".
2. **Zero nova verdade de domínio.** A exportação é uma **representação** da fotografia da
   012 e dos fatos historicamente imutáveis que ela referencia. Nada é recalculado,
   reconstruído, corrigido ou reinterpretado.
3. **Um dataset lógico, várias serializações.** CSV e XLSX diferem só em serialização.
4. **Máquina e humano.** Nomes técnicos estáveis para máquina; dicionário e metadados para
   o analista.
5. **Fiel à Versão.** Cada exportação é fiel à Versão da Campanha daquele snapshot; nenhuma
   comparabilidade entre Versões é inventada.
6. **Derivável, logo não persistido.** O snapshot é imutável; a exportação pode ser
   regenerada com o mesmo conteúdo.
7. **Contrato, não transporte.** A feature define o contrato de dados que o GeN poderá
   consumir; o mecanismo de entrega fica pendente.

### Verificação no código (Features 002, 005, 006 e 012)

| # | Fato verificado | Evidência | Consequência para a 013 |
|---|-----------------|-----------|--------------------------|
| C1 | Pergunta e Opção têm identificador técnico próprio, local à Versão; Seção, Pergunta e Opção têm posição positiva e única no pai | Modelos da 002; restrições de posição única | Chave técnica de coluna baseada no identificador da Pergunta/Opção (FR-031); ordem estrutural pelas posições (FR-081) |
| C2 | Texto da Opção é único **dentro da Pergunta**; textos de Pergunta **podem repetir** | Restrição "texto único" só em Opção | Rótulo da Opção é valor inequívoco numa coluna de escolha única (FR-034); texto de Pergunta nunca é chave (FR-031) |
| C3 | No máximo uma Opção por Pergunta admite complemento; complemento é atributo da Resposta, só presente com essa Opção escolhida | Restrição de complemento único; validação da 005 | Uma única coluna de complemento por Pergunta que a admita (FR-038) |
| C4 | Escala: inteiro, início < fim, rótulos de início e fim opcionais | Restrição de escala da 002; validação de limites da 005 | Valor inteiro na coluna; limites e rótulos no dicionário (FR-036) |
| C5 | Escolha múltipla: conjunto ≥ 1 Opção, sem ordem de seleção | 005 (tabela técnica sem posição) | Um indicador por Opção, sem delimitador (FR-037) |
| C6 | Texto curto, complemento e textos do instrumento nunca são cadeia vazia; texto é gravado sem `strip()` | Restrições "não vazio"; 005 grava como recebido | Ausência e valor vazio não se confundem: célula vazia = ausência (FR-045); espaços preservados (FR-035) |
| C7 | Contexto congelado (sete atributos) com ausência = "não informado"; ano e data independentes | 012 (registro do snapshot) | Exportado como congelado; ausência como célula vazia (FR-022, FR-045) |
| C8 | A 012 entrega Participação concluída com conjunto "fora do percurso" vazio, porque a 006 já removeu as inativas ao concluir | 012 (leitura do dataset); 006 FR-030 a FR-035 | Toda Resposta de Participação concluída é válida para o percurso (FR-042) |
| C9 | Para Participação não concluída, a 012 entrega as Perguntas com Resposta preservada fora do percurso, calculadas pelas regras puras da 006, ou "não determinável" (Versão com estrutura não suportada, 006 FR-016, ou Respostas que a 006 rejeita) | 012 (leitura do dataset) | Respostas fora do percurso nunca aparecem como válidas (FR-043); "não determinável" omite as Respostas da linha e é contado nos metadados (FR-044) |
| C10 | Nome da Pesquisa é mutável a qualquer tempo; designação e título da Versão e nome da Campanha são imutáveis depois da publicação/abertura | 002 FR-003; 004 FR-043; 012 Achado A2 | Nome da Pesquisa **não** é exportado: quebraria a reprodutibilidade (FR-063) |
| C11 | A leitura da 012 nunca lê Conclusão atual nem Pessoa, e não entrega objeto navegável até elas | 012 FR-076, FR-080 | A 013 consome só essa fronteira e o conteúdo imutável da Versão (FR-003) |
| C12 | Participação tem início e conclusão como instantes; timezone configurada é America/Sao_Paulo | 005, 006; configuração | Datas da Participação exportadas como data, na timezone institucional (FR-025) |
| C13 | Nome, período e Versão da Campanha só mudam com a Campanha nunca aberta; o momento de abertura é gravado uma única vez; designação, título e publicação da Versão só mudam em rascunho. O momento de encerramento explícito é gravado uma vez, mas pode estar ausente na captura (encerramento pelo fim do período) e ser gravado depois por chamada técnica com momento de referência retroativo | Operações da 004 (alterar, definir período, abrir, encerrar) e da 002 (alterar Versão exige rascunho) | Metadados só com valores fixos para o snapshot; encerramento explícito **omitido** (FR-063) |
| C14 | O identificador interno da Conclusão aparece na interface do egresso (valor da escolha de formação); o da Participação aparece em endereços da jornada | Interface da 008 (escolha de formação; rotas da Participação) | Identificador interno nunca é exportado; identificadores analíticos são derivados com chave (FR-027) |
| C15 | Pessoa é o registro do sistema (por fonte e identificador externo), e a Conclusão a referencia; nenhum caminho atual altera essa referência; reconciliação de identidade está pendente (001/DP-003) | 001 | `pessoa_analitica_id` identifica o registro de Pessoa do sistema, não uma identidade reconciliada (FR-028) |

**Achados**

- **A1 — Distinção "não respondeu" × "fora do percurso".** A 012 entrega, para
  Participação não concluída, as Perguntas com Resposta fora do percurso, mas não entrega,
  para nenhuma Participação, o conjunto de Perguntas **do percurso**. A coluna de
  aplicabilidade (FR-047) precisa desse conjunto. Ele é obtido pela **mesma composição de
  regras puras da 006** que a 012 já usa, aplicada também à Participação concluída, como
  acréscimo mínimo à fronteira de leitura da 012 (FR-134), sem implementação paralela da
  jornada.
- **A2 — Recusa em Q1.** Não há fato de domínio "recusa": há Participação concluída cuja
  Resposta a Q1 é a Opção "Não", que tem regra "finaliza". A exportação mostra exatamente
  isso (coluna de Q1 com "Não" e dicionário com a regra), sem coluna derivada (FR-041).
- **A3 — "Identificador permitido da pessoa" (Constituição, Qualidade das Exportações).**
  A análise longitudinal exige ligar a mesma Pessoa entre Conclusões e Campanhas
  (Princípio I). Os identificadores internos não servem: o da Conclusão já é visível na
  interface do egresso (C14) e nenhum deles é revogável. O "identificador permitido" desta
  exportação é, portanto, um **pseudônimo analítico derivado com chave** (FR-027). É a
  decisão consciente que a 012 deixou para feature futura (012 FR-122). Identificador de
  Participação continua não pertinente: a Participação é única por Campanha × Conclusão, e
  o par snapshot + `conclusao_analitica_id` já a identifica.

### Análise normativa

Fonte: PAEG — Resolução CS nº 177/2023, anexo
(`docs/referencias/paeg-resolucao-cs-177-2023-anexo.pdf`).

#### A. Competências previstas pela PAEG relevantes para esta feature

| # | Competência | Artigo |
|---|-------------|--------|
| A1 | Análise e sistematização dos dados coletados para geração de indicadores | Art. 10, III |
| A2 | Banco de dados que auxilie no aprimoramento dos PPCs; criar indicadores | Art. 8º, I, VI |
| A3 | **CPAEG**: planejar, organizar, executar e avaliar as atividades da PAEG no âmbito do Ifes | Art. 21, I |
| A4 | **CPAEG**: atualizar o banco de dados central para acompanhamento e análise | Art. 21, V |
| A5 | **CSAEG**: elaborar relatório com os resultados da Pesquisa do Egresso e reportá-los à CPAEG | Art. 22, V |
| A6 | **Proex**: Relatório Anual de Acompanhamento de Egressos | Art. 14 |

**O que a PAEG não diz**: quem pode gerar, receber, armazenar fora do sistema ou
compartilhar dados individualizados de Participações e Respostas; como os dados chegam ao
GeN; se Perguntas sensíveis devem ser excluídas de exportações.

#### B. Interpretação operacional adotada por esta feature

Técnica, reversível e localizada (Princípio XXIX). Não cria competência institucional.

| # | Interpretação | Fundamento |
|---|---------------|------------|
| B1 | Exportar o dataset individualizado de um snapshot é parte de sistematizar os dados coletados e de manter o banco central para análise | A1, A2, A4 |
| B2 | É capacidade **institucional e central**: quando exposta a operadores, compete à atuação **CPAEG** ativa | A3, A4; 012 FR-102 |
| B3 | O relatório de resultados da unidade (A5) não implica acesso da CSAEG ao dataset linha a linha. Agregados por unidade e dataset individualizado são capacidades diferentes; nenhuma é dada à CSAEG aqui | A5; 012 FR-103; 005/DP-505; 011/DP-1101 |
| B4 | Exportar um snapshot não o torna oficial nem o designa para publicação | A6; 012/DP-1201 |

#### C. Decisões institucionais não tomadas aqui

Ver "Decisões Pendentes": compartilhamento do dataset individualizado (DP-1301),
mecanismo de consumo pelo GeN (DP-1302), tratamento de respostas sensíveis e risco de
reidentificação (DP-1303), além das herdadas.

### Termos usados nesta spec

Os nomes são conceituais; a nomenclatura concreta pertence ao plan.

- **Exportação**: representação tabular, gerada sob demanda, de **um** snapshot
  explicitamente informado. Não é persistida.
- **Dataset lógico**: as três tabelas da exportação — **Dados**, **Dicionário** e
  **Metadados** — com seus valores tipados. É o conteúdo que CSV e XLSX serializam.
- **Dados**: a tabela principal, uma linha por registro do snapshot.
- **Colunas base**: colunas de Dados que não derivam de Pergunta (FR-020).
- **Colunas de Pergunta**: colunas de Dados derivadas de uma Pergunta da Versão (e, em
  escolha múltipla, de suas Opções).
- **Chave técnica**: nome de coluna determinístico, seguro e independente de texto.
- **Pseudônimo analítico**: `conclusao_analitica_id` ou `pessoa_analitica_id`, código
  opaco derivado do identificador interno com chave secreta dedicada (FR-027). Não é
  identificador interno, não é anônimo e não é reversível pelo consumidor.
- **Aplicabilidade**: se a Pergunta pertence ao percurso calculado pela 006 para a
  Participação da linha (FR-047).
- **Resposta válida para o percurso**: Resposta da Participação do registro que a 012 não
  classifica como fora do percurso. Para Participação concluída, todas; para não
  concluída, as que não estão fora do percurso; para percurso não determinável, nenhuma.
- **Contrato de exportação**: as regras desta spec (tabelas, colunas base, chaves técnicas,
  tipos, representação de ausência, ordem, serialização), identificado por uma **versão de
  contrato** constante.
- **Pacote CSV**: arquivo compactado com as três tabelas em CSV.
- **Pasta de trabalho XLSX**: arquivo com as três tabelas em abas.
- **GeN**: consumidor institucional a jusante (análise e painéis). Não é conceito de
  domínio.

### Decisões desta especificação

Escolhas reversíveis, marcadas **[Hipótese]**, **[Arquitetura]** ou **[Interpretação
B#]** nos requisitos:

1. **Fonte = um snapshot explícito** + fronteira de leitura da 012 + conteúdo imutável da
   Versão da Campanha do snapshot (FR-001 a FR-006).
2. **Geometria única: WIDE.** Uma linha por registro do snapshot (= Conclusão Acadêmica no
   universo), colunas base + colunas de Pergunta/Opção. Nenhum formato long paralelo
   (FR-010, FR-014).
3. **Catorze colunas base**: dois identificadores analíticos pseudonimizados
   (`conclusao_analitica_id`, `pessoa_analitica_id`, por HMAC-SHA-256 com chave dedicada),
   elegibilidade, sete atributos de contexto congelado, dois indicadores e duas datas da
   Participação (FR-020, FR-027). Nenhum identificador interno, PII ou hash de dado
   pessoal; nenhuma coluna constante por linha.
4. **Chave técnica da Pergunta = identificador técnico da Pergunta na Versão**, em
   hexadecimal minúsculo sem hífens: `pergunta_<id>`; Opção: `pergunta_<id>__opcao_<id>`;
   complemento: `pergunta_<id>__complemento`; aplicabilidade:
   `pergunta_<id>__aplicavel` (FR-031 a FR-033, FR-047).
5. **Tipos**: escolha única → rótulo da Opção; escolha múltipla → um indicador booleano
   por Opção; texto curto → texto como registrado; escala → inteiro; complemento → coluna
   própria (FR-034 a FR-038).
6. **Só Respostas válidas para o percurso** aparecem em Dados; fora do percurso e
   percurso não determinável nunca aparecem como valor (FR-042 a FR-044). Uma coluna de
   **aplicabilidade por Pergunta** distingue aplicável não respondida, fora do percurso e
   percurso não determinável (FR-046, FR-047).
7. **Ausência = célula vazia** em todas as serializações; "Não informado" não é gravado
   como valor (FR-045).
8. **Dicionário gerado da Versão imutável**, com proveniência por coluna e as regras de
   navegação (FR-050 a FR-058).
9. **Metadados sem `gerado_em`**: só valores fixos para o snapshot — fatos do snapshot,
   da Campanha fixados na abertura, da Versão publicada, contagens, versão do contrato e
   versão do esquema de pseudonimização; sem nome da Pesquisa e sem momento de
   encerramento explícito (FR-060 a FR-066).
10. **CSV**: UTF-8 sem BOM, vírgula, RFC 4180, `true`/`false`, ISO 8601, ausência = campo
    vazio, com **escape reversível** contra interpretação como fórmula como parte do
    contrato, em variante única. Pacote compactado
    com `dados.csv`, `dicionario.csv`, `metadados.csv` (FR-071 a FR-076).
11. **XLSX**: abas Dados, Dicionário, Metadados; valores tipados; texto sempre como texto,
    nunca fórmula; sem formatação além do necessário (FR-077 a FR-079).
12. **Sem interface, sem regra nova de autorização**: operação + testes. Quando exposta,
    só CPAEG (FR-100 a FR-104). A história P3 (interface mínima) **não** é adotada.
13. **Zero entidades novas, zero migrations, zero job** (FR-130 a FR-134).

## Clarifications

### Session 2026-10-02

Escopo restrito pelo solicitante a quatro pontos; as demais decisões permanecem.

- Q: Como gerar identificadores analíticos que permitam análise longitudinal (mesma
  Pessoa entre Conclusões e Campanhas) sem PII nem identificador interno? → A:
  **`pessoa_analitica_id` e `conclusao_analitica_id` por HMAC-SHA-256** sobre o
  identificador interno, com separação de domínio (`pessoa:<id>`, `conclusao:<id>`) e
  **chave secreta dedicada** à pseudonimização analítica, distinta do segredo da
  aplicação, fora do repositório e nunca persistida. Sem chave, a exportação falha; nunca
  recai no identificador interno. Estáveis enquanto a mesma chave vigorar; trocar a chave
  rompe a ligação com exportações anteriores. Metadados registram só a versão do esquema
  de pseudonimização. Custódia e rotação da chave em DP-1301. Dataset pseudonimizado,
  não anônimo. Sem modelo, migration, tabela de correspondência ou serviço de identidade.
  (FR-020, FR-026 a FR-029)
- Q: Como distinguir Pergunta aplicável não respondida, Pergunta fora do percurso e
  percurso não determinável? → A: **Uma coluna `pergunta_<id>__aplicavel` por Pergunta**,
  qualquer que seja o tipo: verdadeiro = pertence ao percurso calculado; falso = fora do
  percurso; vazio = percurso não determinável (ou sem Participação, distinguido por
  `possui_participacao`). Sem entidade, modelo ou framework. (FR-046, FR-047)
- Q: Os metadados descritivos são todos fixos para o snapshot? → A: **Verificado no
  código.** Nome, período e momento de abertura da Campanha estão fixados desde a
  abertura; designação, título e publicação da Versão, desde a publicação. O momento de
  **encerramento explícito** não é congelado no snapshot e ainda pode ser gravado depois
  da captura por chamada técnica com momento de referência retroativo; por isso é
  **omitido**, como o nome da Pesquisa. Nada novo é persistido para guardar rótulos.
  (C13, FR-060, FR-063)
- Q: Como tratar o escape contra fórmula no CSV? → A: **Parte explícita do contrato CSV,
  única variante** (sem `raw`/`safe`), perfeitamente reversível e descrita nos Metadados;
  XLSX grava texto como texto, sem escape. (FR-075, FR-076)

## User Scenarios & Testing *(mandatory)*

Os atores são a **CPAEG**, como responsável institucional pela análise (quando a
capacidade for exposta), o **analista institucional** que abre os arquivos e o **GeN**
como consumidor automatizado a jusante. Nesta feature, todas as histórias são
exercitadas por verificação automatizada com dados fictícios (FR-104, FR-115).

### User Story 1 - Exportar um snapshot explicitamente escolhido em CSV (Priority: P1)

A partir de um snapshot analítico informado explicitamente, gerar um pacote CSV com as
tabelas Dados, Dicionário e Metadados, adequado a processamento automatizado.

**Why this priority**: CSV é o formato mínimo obrigatório de interoperabilidade
(Constituição XVIII) e a base do contrato para o GeN.

**Independent Test**: capturar um snapshot de Campanha fictícia encerrada, exportar em
CSV, reabrir o pacote com um leitor CSV genérico e conferir tabelas, cabeçalhos, valores e
contagens.

**Acceptance Scenarios**:

1. **Given** um snapshot com 5 registros, **When** é exportado em CSV, **Then** o pacote
   contém exatamente as três tabelas, Dados tem 5 linhas de dados e um cabeçalho com
   nomes técnicos, e Metadados informa 5 registros.
2. **Given** dois snapshots da mesma Campanha, **When** cada um é exportado, **Then** cada
   exportação usa somente o snapshot informado e seus Metadados identificam esse snapshot.
3. **Given** uma chamada de exportação sem snapshot, ou com algo que não é snapshot
   gravado, **When** é executada, **Then** é recusada com erro explícito e nenhum arquivo é
   produzido.

---

### User Story 2 - Exportar o mesmo snapshot em XLSX com a mesma semântica (Priority: P1)

Gerar uma pasta de trabalho com abas Dados, Dicionário e Metadados, para uso humano, com o
mesmo dataset lógico do CSV.

**Why this priority**: o analista institucional usa planilha; duas semânticas seriam duas
verdades.

**Independent Test**: exportar o mesmo snapshot em CSV e XLSX, ler ambos, aplicar as
regras documentadas de serialização e comparar as três tabelas célula a célula.

**Acceptance Scenarios**:

1. **Given** um snapshot, **When** exportado em CSV e em XLSX, **Then** as três tabelas
   têm as mesmas colunas, na mesma ordem, as mesmas linhas, na mesma ordem, e os mesmos
   valores, diferindo só na representação física (tipos nativos no XLSX; texto e escape no
   CSV).
2. **Given** a pasta de trabalho, **When** aberta numa planilha, **Then** ela não contém
   fórmula, gráfico, macro, tabela dinâmica, filtro ou formatação condicional.

---

### User Story 3 - Uma linha por registro, inclusive sem Participação (Priority: P1)

Cada registro do snapshot produz exatamente uma linha: elegíveis sem Participação,
elegíveis com Participação e não elegíveis no snapshot com Participação.

**Why this priority**: sem as linhas de quem não participou não há denominador, taxa de
início, taxa de conclusão nem recorte da população.

**Independent Test**: snapshot com os casos A, B, C e D; conferir que o número de linhas é
igual ao de registros e que cada caso está representado com o estado correto.

**Acceptance Scenarios**:

1. **Given** uma Conclusão elegível sem Participação (caso A), **When** exportada, **Then**
   sua linha existe com `elegivel_no_snapshot` verdadeiro, `possui_participacao` falso e
   todas as colunas de Participação e de Pergunta vazias, inclusive as de aplicabilidade.
2. **Given** uma Conclusão não elegível no snapshot com Participação (caso D), **When**
   exportada, **Then** sua linha existe com `elegivel_no_snapshot` falso e a Participação
   e as Respostas válidas representadas; o denominador (elegíveis) não muda.
3. **Given** uma Pessoa com três Conclusões no universo, **When** exportada, **Then** há
   três linhas, sem consolidação, com o mesmo `pessoa_analitica_id` e três
   `conclusao_analitica_id` distintos.
4. **Given** os Dados exportados, **When** o analista calcula Participações ÷ elegíveis e
   concluídas ÷ elegíveis, **Then** os resultados coincidem com as taxas da 012 para o
   mesmo snapshot, inclusive quando superiores a 100%.

---

### User Story 4 - Contexto acadêmico congelado e estado da Participação (Priority: P1)

Cada linha traz o contexto institucional congelado no snapshot e o estado da Participação:
sem Participação, concluída ou iniciada e não concluída.

**Why this priority**: recortes e taxas dependem do contexto da época e do estado real da
Participação.

**Independent Test**: depois da captura, alterar o contexto acadêmico das Conclusões
fictícias; exportar; conferir que os valores são os congelados e que o estado da
Participação corresponde aos fatos registrados.

**Acceptance Scenarios**:

1. **Given** um snapshot capturado e a unidade de uma Conclusão alterada depois (caso Q),
   **When** exportado, **Then** a linha mostra a unidade congelada.
2. **Given** uma Participação concluída (caso B), **When** exportada, **Then**
   `possui_participacao` e `participacao_concluida` são verdadeiros e as duas datas estão
   preenchidas.
3. **Given** uma Participação iniciada e não concluída (caso C), **When** exportada,
   **Then** `possui_participacao` é verdadeiro, `participacao_concluida` é falso, a data de
   início está preenchida e a de conclusão está vazia.
4. **Given** dois cursos homônimos em unidades diferentes (caso P), **When** exportados,
   **Then** as linhas se distinguem pela coluna de unidade, sem código de curso.
5. **Given** uma Conclusão com curso não informado, **When** exportada, **Then** a célula
   de curso está vazia, e não "Não informado".

---

### User Story 5 - Representar corretamente os quatro tipos de Pergunta (Priority: P1)

Escolha única, escolha múltipla, texto curto e escala são representados sem ambiguidade,
com complemento em coluna própria.

**Why this priority**: é o conteúdo declarado, razão de existir da pesquisa.

**Independent Test**: Versão fictícia com os quatro tipos, Opção com complemento em escolha
única e em escolha múltipla, duas Perguntas com o mesmo texto e Opções de rótulos
parecidos; exportar e conferir cada célula.

**Acceptance Scenarios**:

1. **Given** Resposta de escolha única (caso E), **When** exportada, **Then** a coluna da
   Pergunta contém exatamente o texto da Opção escolhida na Versão.
2. **Given** Resposta de escolha múltipla com uma Opção (caso F) e com várias (caso G),
   **When** exportadas, **Then** cada coluna de Opção da Pergunta é verdadeira se a Opção
   foi escolhida e falsa se não foi, sem nenhum delimitador.
3. **Given** escolha múltipla com a Opção que admite complemento escolhida (caso H),
   **When** exportada, **Then** a coluna da Opção é verdadeira e a coluna de complemento da
   Pergunta contém o texto declarado, sem concatenação ao rótulo.
4. **Given** texto curto com acentos, emoji, espaços nas pontas e quebra de linha (caso I),
   **When** exportado e relido, **Then** o valor é idêntico ao registrado.
5. **Given** Resposta de escala (caso K), **When** exportada, **Then** a célula contém o
   inteiro, tipado como número, e o dicionário informa início, fim e rótulos existentes.
6. **Given** duas Perguntas com o mesmo texto (caso N), **When** exportadas, **Then** têm
   chaves técnicas diferentes e o dicionário as distingue por Seção e posição.
7. **Given** duas Opções de rótulos parecidos (caso O), **When** exportadas, **Then** têm
   colunas (escolha múltipla) ou valores (escolha única) distintos, iguais aos textos
   exatos da Versão.
8. **Given** uma Participação concluída em que uma Pergunta opcional do percurso ficou sem
   Resposta (caso M), **When** exportada, **Then** `pergunta_<id>__aplicavel` é verdadeiro
   e as colunas de valor da Pergunta estão vazias.
9. **Given** uma Pergunta fora do percurso da Participação — Seção não alcançada, ou
   Resposta de rascunho preservada fora do percurso (caso L) —, **When** exportada,
   **Then** `pergunta_<id>__aplicavel` é falso e as colunas de valor estão vazias.
10. **Given** uma Participação com percurso não determinável, **When** exportada, **Then**
    toda coluna de aplicabilidade da linha está vazia, assim como as de valor.

---

### User Story 6 - Dicionário de dados suficiente para interpretar todas as colunas (Priority: P1)

O dicionário, gerado da Versão imutável e das definições fixas das colunas base, explica
cada coluna de Dados: significado, tipo, proveniência e, para Perguntas, Seção, posição,
texto, tipo, obrigatoriedade, Opções, complemento, escala e regras de navegação.

**Why this priority**: sem ele, chaves técnicas são ilegíveis e o analista dependeria de
conhecimento implícito.

**Independent Test**: para cada coluna de Dados, encontrar exatamente uma linha de
dicionário correspondente, na mesma ordem; para cada Pergunta de escolha única, encontrar
a descrição de cada valor possível.

**Acceptance Scenarios**:

1. **Given** uma exportação, **When** se filtram as linhas de dicionário que descrevem
   colunas, **Then** elas correspondem, uma a uma e na mesma ordem, às colunas de Dados.
2. **Given** uma coluna de contexto (por exemplo, unidade), **When** consultada no
   dicionário, **Then** sua proveniência é "institucional, congelado no snapshot", e nunca
   "declarado".
3. **Given** uma Opção com regra "finaliza" ou "ir para Seção N", **When** consultada no
   dicionário, **Then** a regra aparece, referida pela posição da Seção de destino.
4. **Given** uma Pergunta que nenhuma Participação respondeu, **When** exportada, **Then**
   suas colunas e linhas de dicionário existem da mesma forma: o esquema depende da
   Versão, não dos dados.

---

### User Story 7 - Nunca contexto atual, nunca snapshot implícito (Priority: P1)

A exportação nunca consulta contexto acadêmico atual, população atual ou elegibilidade
atual, e nunca escolhe um snapshot por conta própria.

**Why this priority**: é o que torna a exportação historicamente fiel (Constituição VIII) e
preserva 012/DP-1201.

**Independent Test**: alterar Conclusões e incorporar novas elegíveis depois da captura;
exportar; conferir que nada mudou. Verificar que não existe operação de exportação que
receba Campanha.

**Acceptance Scenarios**:

1. **Given** um snapshot e Conclusões novas elegíveis incorporadas depois, **When**
   exportado, **Then** as novas Conclusões não aparecem.
2. **Given** uma Campanha com dois snapshots, **When** se procura uma forma de exportar "a
   Campanha", **Then** ela não existe: toda exportação recebe o snapshot.

---

### User Story 8 - Metadados para reprodução e rastreabilidade (Priority: P2)

Os Metadados respondem "de onde vieram esses dados?": snapshot, momento da captura,
Campanha, Versão, contagens e versão do contrato.

**Why this priority**: um arquivo vive fora do sistema e precisa carregar sua origem.

**Independent Test**: exportar e conferir que os Metadados permitem identificar o
snapshot, a Campanha, a Versão e o momento da captura, e que as contagens batem com Dados.

**Acceptance Scenarios**:

1. **Given** uma exportação, **When** lidos os Metadados, **Then** contêm identificador do
   snapshot, momento da captura, identificação, nome, período e momento de abertura da
   Campanha, identificação, designação e título da Versão, contagens, versão do contrato e
   versão do esquema de pseudonimização, e não contêm momento de geração, nome da
   Pesquisa, momento de encerramento explícito nem a chave de pseudonimização.
3. **Given** uma exportação, **When** o nome da Pesquisa é alterado e a Campanha recebe
   depois um registro técnico de encerramento, **Then** uma nova exportação do mesmo
   snapshot tem Metadados idênticos.
2. **Given** os Metadados, **When** comparadas suas contagens com as linhas de Dados,
   **Then** coincidem.

---

### User Story 9 - Unicode preservado e proteção contra fórmula (Priority: P2)

Texto declarado sobrevive ao round-trip e nunca vira fórmula executável ao abrir em
planilha.

**Why this priority**: o texto vem do egresso e pode conter qualquer caractere, inclusive
os que planilhas interpretam como fórmula.

**Independent Test**: textos fictícios iniciados por `=`, `+`, `-`, `@`, tabulação,
retorno de carro e apóstrofo, e textos com acentos, emoji e caracteres especiais; exportar
nos dois formatos; abrir o XLSX e conferir que nenhuma célula é fórmula; reverter o escape
do CSV e conferir igualdade exata.

**Acceptance Scenarios**:

1. **Given** um texto curto `=1+1` (caso J), **When** exportado em XLSX, **Then** a célula
   é texto com o valor `=1+1`, não fórmula.
2. **Given** o mesmo texto, **When** exportado em CSV, **Then** o campo é `'=1+1`, e a
   reversão documentada devolve `=1+1`.
3. **Given** um texto `'abc`, **When** exportado em CSV, **Then** o campo é `''abc` e a
   reversão devolve `'abc`.
4. **Given** um pacote CSV, **When** a reversão descrita nos Metadados é aplicada a todos
   os campos dos três arquivos, sem conhecer seus tipos, **Then** todos os valores voltam
   exatamente ao dataset lógico.

---

### User Story 10 - Ordem determinística e reprodutibilidade (Priority: P2)

Linhas e colunas têm ordem definida; exportar o mesmo snapshot com o mesmo contrato produz
o mesmo conteúdo analítico.

**Why this priority**: comparações, conferências e cargas a jusante dependem disso.

**Independent Test**: exportar o mesmo snapshot duas vezes, em momentos diferentes e
depois de alterar o nome da Pesquisa e o contexto atual das Conclusões; comparar as três
tabelas lidas.

**Acceptance Scenarios**:

1. **Given** uma Versão com Seções e Perguntas em posições variadas (caso T), **When**
   exportada, **Then** as colunas de Pergunta seguem a ordem Seção → Pergunta → Opção.
2. **Given** duas exportações do mesmo snapshot, **When** lidas, **Then** as três tabelas
   são idênticas, mesmo que os arquivos difiram em bytes (metadado interno do XLSX ou
   datas internas do pacote).

---

### User Story 11 - Contrato apropriado para consumo pelo GeN (Priority: P2)

O pacote CSV é um contrato estável e documentado que o GeN pode consumir, sem que o domínio
conheça o GeN, o Looker Studio ou qualquer mecanismo de transporte.

**Why this priority**: o GeN é o consumidor institucional previsto; o transporte não está
decidido.

**Independent Test**: carregar Dados do pacote CSV com leitor genérico, sem conhecer o
sistema, apenas com o Dicionário e os Metadados, e reproduzir as contagens dos Metadados.

**Acceptance Scenarios**:

1. **Given** o pacote CSV, **When** carregado por ferramenta genérica, **Then** todos os
   nomes de coluna são válidos como identificadores (letras minúsculas, dígitos e `_`,
   iniciando por letra) e os tipos são deduzíveis do Dicionário.
3. **Given** o pacote CSV, **When** inspecionado, **Then** não contém identificador
   interno: os identificadores analíticos são opacos e não contêm o identificador
   original.
2. **Given** o código e o contrato da exportação, **When** inspecionados, **Then** não há
   referência a Looker, Data Studio, Google, BigQuery ou painel.

---

### User Story 12 - Vínculo longitudinal por identificadores pseudonimizados (Priority: P2)

Cada linha traz `conclusao_analitica_id` e `pessoa_analitica_id`, opacos e estáveis
enquanto a chave de pseudonimização vigorar, para acompanhar a mesma formação e a mesma
Pessoa entre snapshots e Campanhas, sem PII e sem identificador interno.

**Why this priority**: o acompanhamento é longitudinal (Princípio I); sem vínculo, cada
exportação é uma ilha.

**Independent Test**: Pessoa fictícia com duas Conclusões, uma delas participante de duas
Campanhas; exportar snapshots das duas Campanhas com a mesma chave, com outra chave e sem
chave.

**Acceptance Scenarios**:

1. **Given** a mesma Conclusão em snapshots de duas Campanhas, **When** exportados com a
   mesma chave, **Then** as duas linhas têm o mesmo `conclusao_analitica_id` e o mesmo
   `pessoa_analitica_id`.
2. **Given** duas Conclusões da mesma Pessoa, **When** exportadas, **Then** têm o mesmo
   `pessoa_analitica_id` e `conclusao_analitica_id` diferentes.
3. **Given** a mesma exportação feita com outra chave, **When** comparada, **Then** nenhum
   identificador analítico coincide com os da chave anterior.
4. **Given** nenhuma chave de pseudonimização configurada, **When** se tenta exportar,
   **Then** a exportação é recusada com erro explícito e nenhum arquivo é produzido.
5. **Given** o identificador interno de uma Pessoa e o de uma Conclusão com o mesmo valor
   textual, **When** pseudonimizados, **Then** os resultados são diferentes (separação de
   domínio).

---

**História P3 (interface mínima de download) — não adotada nesta feature.** Não há
consumidor concreto: enquanto 001/DP-009 e 005/DP-504 estiverem abertas só existem dados
fictícios (FR-115), não há identificação produtiva de operadores (010/DP-1001), e a 012
também não expõe o snapshot (012 FR-100). A exportação é operação de domínio exercitada
por testes (FR-100).

### Casos importantes

| Caso | Situação | Requisitos | História |
|------|----------|------------|----------|
| A | Registro elegível sem Participação | FR-011, FR-024, FR-040 | US3 |
| B | Elegível com Participação concluída | FR-024, FR-042 | US4 |
| C | Elegível com Participação não concluída | FR-024, FR-043 | US4 |
| D | Não elegível no snapshot com Participação | FR-012 | US3 |
| E | Escolha única | FR-034 | US5 |
| F | Escolha múltipla com uma Opção | FR-037 | US5 |
| G | Escolha múltipla com várias Opções | FR-037 | US5 |
| H | Escolha múltipla com complemento | FR-038 | US5 |
| I | Texto curto com acentos | FR-035, FR-076 | US5, US9 |
| J | Texto começando com "=" | FR-075, FR-078 | US9 |
| K | Escala | FR-036 | US5 |
| L | Pergunta fora do percurso | FR-043, FR-047 | US5 |
| M | Pergunta não respondida | FR-046, FR-047 | US5 |
| N | Duas Perguntas com o mesmo texto | FR-031 | US5 |
| O | Duas Opções com rótulos parecidos | FR-034, FR-037 | US5 |
| P | Cursos homônimos em unidades diferentes | FR-023 | US4 |
| Q | Snapshot antigo depois de alteração acadêmica | FR-003, FR-022 | US4, US7 |
| R | Dois snapshots da mesma Campanha | FR-001, FR-002 | US1 |
| S | Exportação de cada snapshot explicitamente | FR-001 | US1, US7 |
| T | Versão com Seções e ordem variadas | FR-081 | US10 |
| U | Mesma Pessoa / mesma Conclusão em snapshots de Campanhas diferentes | FR-027 | US12 |
| V | Exportação sem chave de pseudonimização configurada | FR-027, FR-090 | US12 |

### Edge Cases

- **Snapshot com zero registros** (Campanha sem elegíveis e sem Participação): exportação
  válida; Dados só com cabeçalho; Dicionário completo; contagens zero.
- **Pergunta que ninguém respondeu**: colunas de valor presentes e vazias; aplicabilidade
  preenchida conforme o percurso de cada Participação (FR-032, FR-047).
- **Seção sem Pergunta**: não gera coluna; aparece no Dicionário apenas como destino de
  regra, pela posição.
- **Escolha única com Opção que admite complemento, não escolhida**: complemento vazio.
- **Participação não concluída sem Respostas**: linha com `possui_participacao`
  verdadeiro, `participacao_concluida` falso, colunas de valor vazias; aplicabilidade
  conforme o percurso calculado pela 006 sem Respostas (até a primeira Seção que não pode
  ser deixada): verdadeira nas Seções alcançadas, falsa nas demais.
- **Participação não concluída com Respostas fora do percurso** (caso L, por exemplo, Q34
  respondida e depois Q33 mudada para "Não"): as Respostas fora do percurso não aparecem e
  suas Perguntas têm aplicabilidade falsa; as do percurso aparecem.
- **Percurso não determinável** (Versão com estrutura não suportada pela 006, ou Respostas
  que a 006 rejeita): nenhuma Resposta da linha aparece e toda aplicabilidade da linha
  fica vazia; a linha e o estado da Participação permanecem; os Metadados contam essas
  Participações (FR-044).
- **Participação concluída por Q1 = "Não"**: `participacao_concluida` verdadeiro; Q1 com
  "Não"; Perguntas da Seção de Q1 com aplicabilidade verdadeira e as demais com falsa;
  demais valores vazios; nenhuma coluna de "recusa" (FR-041).
- **Rótulo de Opção contendo `;` ou `,`**: irrelevante para escolha múltipla (indicadores);
  em escolha única, preservado com aspas do CSV.
- **Texto com aspas, vírgulas, quebras de linha, tabulação ou só espaços nas pontas**:
  preservado (FR-035, FR-074).
- **Rótulo de Opção ou texto do contexto iniciado por `-` ou `+`** (por exemplo, "+ de 5
  salários"): mesmo escape no CSV que o texto declarado (FR-075).
- **Escala com limite negativo**: inteiro, nunca escapado (o escape só se aplica a texto).
- **Valor não representável no formato** (caractere de controle proibido no XLSX ou texto
  além do limite de célula): erro explícito na exportação desse formato; o valor nunca é
  truncado, removido ou alterado (FR-091).
- **Nome da Pesquisa alterado depois da captura**: exportação idêntica (C10).
- **Encerramento explícito gravado depois da captura** (chamada técnica retroativa):
  exportação idêntica, porque esse momento não é exportado (C13).
- **Chave de pseudonimização ausente ou vazia**: exportação recusada antes de produzir
  qualquer arquivo; nunca recai no identificador interno (FR-027).
- **Chave trocada entre duas exportações do mesmo snapshot**: identificadores analíticos
  diferentes; demais conteúdos idênticos (FR-084).
- **Resposta de forma incompatível com o tipo da Pergunta, ou Opção de outra Pergunta**
  (só por escrita fora das operações): erro explícito de inconsistência estrutural; nenhum
  arquivo parcial (FR-092).
- **Pergunta cujo identificador gera nome de coluna repetido** (impossível pelo modelo):
  verificação de unicidade dos nomes recusa a exportação (FR-092).
- **Snapshot com dezenas de milhares de registros e instrumento do tamanho do formulário
  2024**: exportação síncrona, proporcional ao snapshot (FR-133).

## Requirements *(mandatory)*

Cada requisito indica a origem entre colchetes: **[PAEG]**, **[Const.]**,
**[Arquitetura]**, **[Hipótese]**, **[Interpretação B#]**, **[00n]** (feature anterior),
**[Escopo]** ou DP.

### Functional Requirements

**Fonte e snapshot explícito**

- **FR-001**: Toda operação de exportação DEVE receber explicitamente **um** snapshot
  analítico. NÃO DEVE existir exportação por Campanha, por Pesquisa, por Versão ou sem
  snapshot, nem seleção de "snapshot atual", "vigente", "último", "mais recente" ou
  "oficial". [012 FR-061, FR-064; 012/DP-1201]
- **FR-002**: Cada exportação DEVE conter dados de um único snapshot. NÃO DEVE concatenar
  snapshots, Campanhas ou Versões. [Escopo; 002/DP-006]
- **FR-003**: A exportação DEVE obter registros, contexto, elegibilidade, Participações e
  Respostas **somente** pela fronteira de leitura da 012, e a estrutura do instrumento
  somente pelo conteúdo imutável da Versão da Campanha do snapshot (002). NÃO DEVE ler
  contexto da Conclusão Acadêmica atual, atributos de Pessoa, fonte acadêmica, população
  ou elegibilidade atuais (004), nem consultar a 011. Única exceção: a referência técnica
  da Conclusão à sua Pessoa, para derivar `pessoa_analitica_id` (FR-028). [012 FR-076,
  FR-080; Const. — VIII]
- **FR-004**: A exportação NÃO DEVE recalcular elegibilidade, reconstruir população,
  alterar ou completar Respostas, reinterpretar a jornada, nem resolver comparabilidade
  entre Versões. A classificação de Respostas fora do percurso e o conjunto de Perguntas
  do percurso são os calculados pelas regras puras da 006, pela fronteira da 012, sem
  implementação paralela da jornada. [Princípio 2; 006; 012 FR-075; Achado A1]
- **FR-005**: A exportação NÃO DEVE gravar nada: nenhum dado de domínio é criado,
  alterado ou removido, nem os dados transacionais originais (inclusive Respostas fora do
  percurso, que continuam preservadas). [Const. — VIII; 005/DP-503]
- **FR-006**: A exportação DEVERIA confiar nos invariantes da 012 (universo completo,
  unicidade por Conclusão, elegibilidade explícita) e NÃO DEVE repetir as verificações de
  captura. Suas validações são de representação, esquema e serialização (FR-090 a
  FR-092). [Arquitetura; 012 FR-053]

**Grão e universo**

- **FR-010**: Dados DEVE ter **exatamente uma linha por registro do snapshot**, isto é, por
  Conclusão Acadêmica no universo do snapshot. Pessoa NÃO DEVE ser grão, e Conclusões da
  mesma Pessoa NÃO DEVEM ser consolidadas; elas são ligáveis apenas pelo
  `pessoa_analitica_id` (FR-027). [Const. — I, XI; 012 FR-031]
- **FR-011**: Registro elegível sem Participação DEVE ter linha, com os identificadores
  analíticos, o contexto e `possui_participacao` preenchidos e as demais colunas de
  Participação e todas as de Pergunta (inclusive aplicabilidade) vazias. [Const. — XIX; 012
  FR-034]
- **FR-012**: Registro **não elegível no snapshot** com Participação DEVE ter linha, com
  sua Participação e Respostas válidas. NÃO DEVE ser eliminado nem fazer variar o
  denominador; taxas superiores a 100% decorrentes do snapshot DEVEM permanecer
  reproduzíveis. [012 FR-032, FR-083]
- **FR-013**: O número de linhas de Dados DEVE ser igual ao número de registros do
  snapshot, e os totais deriváveis de Dados (elegíveis, com Participação, concluídas,
  separados por elegibilidade) DEVEM coincidir com os indicadores da 012 para o mesmo
  snapshot. [012 FR-081]
- **FR-014**: A geometria DEVE ser **wide** (uma linha por registro, colunas por
  Pergunta/Opção). NÃO DEVE existir formato long paralelo nem tabela de Respostas
  separada. [Arquitetura; Escopo]

**Colunas base**

- **FR-020**: As colunas base DEVEM ser exatamente estas, nesta ordem, antes de qualquer
  coluna de Pergunta: [Arquitetura]

  | # | Coluna | Tipo | Proveniência | Consumidor analítico |
  |---|--------|------|--------------|----------------------|
  | 1 | `conclusao_analitica_id` | texto | pseudônimo analítico (derivado com chave) | acompanhar a mesma formação entre snapshots e Campanhas |
  | 2 | `pessoa_analitica_id` | texto | pseudônimo analítico (derivado com chave) | acompanhar a mesma Pessoa entre Conclusões e Campanhas |
  | 3 | `elegivel_no_snapshot` | booleano | derivado (congelado pela 012) | denominador; separação elegível × não elegível |
  | 4 | `unidade` | texto | institucional (congelado) | recorte por unidade |
  | 5 | `curso` | texto | institucional (congelado) | recorte por curso (com unidade) |
  | 6 | `nivel` | texto | institucional (congelado) | recorte por nível |
  | 7 | `modalidade` | texto | institucional (congelado) | recorte por modalidade |
  | 8 | `forma_oferta` | texto | institucional (congelado) | recorte por forma de oferta |
  | 9 | `ano_conclusao` | inteiro | institucional (congelado) | recorte por ano; tempo desde a conclusão |
  | 10 | `data_conclusao` | data | institucional (congelado) | referência temporal quando a fonte a fornece |
  | 11 | `possui_participacao` | booleano | coleta | taxa de início; distinguir "não participou" |
  | 12 | `participacao_concluida` | booleano | coleta | taxa de conclusão; separar respostas finais de rascunho |
  | 13 | `participacao_iniciada_em` | data | coleta | referência temporal das Respostas de rascunho |
  | 14 | `participacao_concluida_em` | data | coleta | referência temporal das Respostas declaradas (tempo entre conclusão do curso e resposta) |

- **FR-021**: NÃO DEVEM existir colunas base com valor constante em todas as linhas
  (snapshot, momento da captura, Campanha, Versão): elas pertencem aos Metadados (FR-060).
  Justificativa: não acrescentam informação dentro do arquivo e incentivariam
  concatenação de exportações de Versões diferentes, cujas colunas de Pergunta não
  correspondem. Se o mecanismo de consumo do GeN (DP-1302) transportar só a tabela Dados,
  essa decisão DEVE ser reavaliada lá. [Arquitetura; DP-1302]
- **FR-022**: As colunas 4 a 10 DEVEM conter exatamente os valores congelados no registro
  do snapshot, sem preencher, corrigir, normalizar grafia, traduzir ou derivar um do outro
  (ano e data são independentes). [012 FR-042, FR-043; Const. — III]
- **FR-023**: Curso DEVE ser interpretado com a unidade da mesma linha; NÃO DEVE ser criado
  código, catálogo ou identidade de Curso. O dicionário DEVE dizer isso. [012 FR-045;
  010/DP-1005]
- **FR-024**: Estado da Participação, sem categorias inventadas: [006; 012 FR-075, FR-082]
  - sem Participação: `possui_participacao` = falso; colunas 12 a 14 vazias;
  - concluída: `possui_participacao` = verdadeiro; `participacao_concluida` = verdadeiro;
    datas 13 e 14 preenchidas;
  - iniciada e não concluída: `possui_participacao` = verdadeiro; `participacao_concluida`
    = falso; data 13 preenchida; data 14 vazia.

  NÃO DEVE existir coluna ou valor de "abandono", "desistência", "recusa", "completa" ou
  "parcial". [005/DP-503; 006/DP-601; 007/DP-703]
- **FR-025**: As datas da Participação DEVEM ser a data civil, na timezone institucional
  configurada, dos instantes de início e de conclusão registrados. A precisão de dia é
  minimização deliberada: nenhum consumidor analítico concreto precisa do instante, e o
  instante facilita correlação com registros técnicos. [Const. — XVI; Hipótese]
- **FR-026**: NÃO DEVEM ser exportados identificadores internos de Pessoa, Conclusão
  Acadêmica, Participação, registro do snapshot ou Resposta, nem identificador externo,
  CPF, matrícula, e-mail, telefone, nem hash ou código derivado desses dados. Os únicos
  identificadores de linha exportados são os pseudônimos analíticos de FR-027. Nenhum
  identificador de Participação é exportado: o par snapshot + `conclusao_analitica_id` já
  a identifica. [C14; 012 FR-047; 005/DP-505; Const. — XVI]
- **FR-027**: **Pseudonimização analítica.** `conclusao_analitica_id` e
  `pessoa_analitica_id` DEVEM ser calculados assim: [Clarifications 2026-10-02; Const. —
  I, XVI; 012 FR-122]
  - algoritmo padronizado **HMAC-SHA-256**, com **separação de domínio**: a mensagem é
    `conclusao:<identificador interno da Conclusão>` ou `pessoa:<identificador interno da
    Pessoa>`, de modo que os dois espaços nunca colidem;
  - **chave secreta dedicada** à pseudonimização analítica, distinta de qualquer outro
    segredo da aplicação, fornecida pela configuração do ambiente, fora do repositório e
    nunca gravada no banco, em arquivo exportado, em log ou em mensagem;
  - chave **inadequada** também é recusada antes de qualquer leitura: menos de 32
    caracteres, ou igual ao segredo da aplicação. É salvaguarda técnica contra chave
    trivial ou reaproveitada [Hipótese];
  - resultado exportado **opaco**, de comprimento fixo, que não contém nem permite
    recuperar o identificador interno sem a chave;
  - **estável** entre exportações enquanto a mesma chave vigorar; troca deliberada da
    chave rompe a ligação com exportações produzidas com a anterior;
  - sem chave configurada (ausente ou vazia), a exportação DEVE falhar com erro explícito
    antes de produzir qualquer arquivo; NUNCA recai no identificador interno nem em outra
    derivação;
  - NÃO DEVE ser criado modelo, migration, tabela de correspondência, cache de
    pseudônimos ou serviço de identidade: o cálculo é refeito a cada exportação.
- **FR-028**: `pessoa_analitica_id` DEVE derivar da Pessoa referenciada pela Conclusão do
  registro, lida no momento da exportação apenas como referência técnica, sem nenhum
  atributo da Pessoa. Ele identifica o **registro de Pessoa do sistema**, não uma
  identidade reconciliada entre fontes (001/DP-003). Hoje a referência Conclusão → Pessoa
  não muda por nenhum caminho suportado; se uma reconciliação futura a alterar, a mesma
  exportação de um snapshot antigo passará a refletir a nova referência, e essa
  consequência DEVE ser tratada pela feature que resolver 001/DP-003. [C15; 001/DP-003]
- **FR-029**: Os identificadores analíticos NÃO tornam o dataset anônimo: ele é
  **pseudonimizado**, e a ligação entre exportações aumenta o risco de reidentificação.
  Custódia, acesso e rotação da chave são DP-1301. [Const. — XVI; DP-1301; DP-1303]

**Colunas de Pergunta**

- **FR-030**: Toda Pergunta da Versão da Campanha do snapshot DEVE gerar uma coluna de
  aplicabilidade (FR-047) e colunas de valor segundo seu tipo. A exportação DEVE suportar
  exatamente os quatro tipos existentes (escolha única, escolha múltipla, texto curto, escala) e NÃO DEVE antecipar outros (matriz,
  upload, data, número, fórmula, ranking, assinatura). Tipo desconhecido é inconsistência
  estrutural (FR-092). [002; Const. — XXIII]
- **FR-031**: A chave técnica da Pergunta DEVE ser `pergunta_` seguida do identificador
  técnico da Pergunta na Versão, em hexadecimal minúsculo sem separadores. NÃO DEVE ser
  derivada de texto, slug, posição ou nome da Pesquisa. Como o identificador é local à
  Versão, Perguntas de Versões diferentes nunca têm a mesma chave. [C1; 002/DP-006]
- **FR-032**: O conjunto e a ordem das colunas de Pergunta DEVEM depender somente da
  Versão: Perguntas sem nenhuma Resposta têm as mesmas colunas. Dois snapshots da mesma
  Campanha têm o mesmo cabeçalho. [Arquitetura]
- **FR-033**: Todo nome de coluna DEVE: usar só letras minúsculas sem acento, dígitos e
  `_`; começar por letra; ser único na tabela; e não depender de acentos ou texto do
  instrumento. O prefixo `pergunta_` é reservado às colunas de Pergunta. [Arquitetura]
- **FR-034**: **Escolha única**: uma coluna `pergunta_<id>`, com o texto exato da Opção
  escolhida, como definido na Versão. NÃO DEVE ser criado código global de Opção. O texto
  da Opção é inequívoco porque é único na Pergunta (C2). [C2; 002/DP-006]
- **FR-035**: **Texto curto**: uma coluna `pergunta_<id>`, com o texto exatamente como
  registrado, sem corrigir ortografia, caixa, acentos, espaços nas pontas ou conteúdo.
  [C6; Const. — III]
- **FR-036**: **Escala**: uma coluna `pergunta_<id>`, com o inteiro registrado, tipado como
  número, nunca convertido em texto ou rótulo. [C4]
- **FR-037**: **Escolha múltipla**: uma coluna booleana por Opção da Pergunta,
  `pergunta_<id>__opcao_<id da Opção>`, na ordem das Opções. Com Resposta válida: verdadeiro
  para cada Opção escolhida e falso para as demais. Sem Resposta válida: todas vazias,
  nunca falsas. NÃO DEVE existir coluna com Opções concatenadas ou delimitadas, nem tabela
  ou dimensão de Opções. [C5; Arquitetura]
- **FR-038**: **Complemento**: toda Pergunta de escolha (única ou múltipla) que tenha Opção
  que admita complemento DEVE ter uma coluna `pergunta_<id>__complemento`, imediatamente
  após as demais colunas da Pergunta, com o complemento declarado, ou vazia quando não
  houver. O complemento NÃO DEVE ser concatenado ao rótulo da Opção. [C3]
- **FR-039**: O texto da Pergunta NÃO DEVE aparecer no cabeçalho de Dados; ele está no
  Dicionário. [Arquitetura]

**Participação, percurso e ausência**

- **FR-040**: Linha sem Participação DEVE ter todas as colunas de Pergunta vazias,
  inclusive as de aplicabilidade.
- **FR-041**: Participação concluída por recusa (Q1 = "Não") DEVE ser exportada como
  concluída, com o valor declarado de Q1 e as demais Perguntas vazias. NÃO DEVE ser criada
  coluna de recusa, nem tratar "concluída" como "questionário completamente respondido". A
  identificação do caso é possível pelo valor de Q1 e pela regra "finaliza" publicada no
  Dicionário. Qualquer indicador derivado de recusa depende de 006/DP-601. [Achado A2;
  006/DP-601]
- **FR-042**: Para Participação concluída, todas as suas Respostas DEVEM ser exportadas
  (são todas válidas para o percurso, C8).
- **FR-043**: Para Participação não concluída com percurso determinável, DEVEM ser
  exportadas somente as Respostas que a 012 não classifica como fora do percurso. Resposta
  fora do percurso NÃO DEVE aparecer em Dados, nem como valor, nem como indicador. Ela
  continua preservada nos dados transacionais. [012 Achado A1, FR-075; 005/DP-503]
- **FR-044**: Para Participação não concluída com percurso **não determinável**, nenhuma
  Resposta DEVE aparecer em Dados; a linha e o estado da Participação permanecem, e os
  Metadados DEVEM informar quantas Participações estão nessa situação. A exportação NÃO
  DEVE interromper as demais linhas por isso. [C9; 012]
- **FR-045**: **Ausência** DEVE ser representada como célula vazia, em todas as tabelas e
  serializações: contexto não informado, coluna de Participação não aplicável, Pergunta sem
  Resposta válida, complemento ausente. Como o domínio proíbe cadeia vazia em texto
  declarado, complemento, contexto e textos do instrumento (C6), célula vazia nunca é
  valor declarado. "Não informado" é apresentação e NÃO DEVE ser gravado como valor. [C6;
  012 FR-043]
- **FR-046**: Toda célula vazia de valor de Pergunta DEVE ser interpretável, sem marcador
  textual nas células:

  | Situação | `possui_participacao` | `pergunta_<id>__aplicavel` | Colunas de valor |
  |----------|-----------------------|----------------------------|------------------|
  | Não há Participação | falso | vazio | vazias |
  | Percurso não determinável | verdadeiro | vazio | vazias |
  | Pergunta fora do percurso | verdadeiro | falso | vazias |
  | Pergunta aplicável não respondida | verdadeiro | verdadeiro | vazias |
  | Pergunta aplicável respondida | verdadeiro | verdadeiro | preenchidas |

  `participacao_concluida` diz se a situação é final ou de rascunho. Valor ausente de
  contexto ou de coluna base não aplicável é célula vazia com significado dado pelo
  Dicionário (FR-053).
- **FR-047**: **Aplicabilidade.** Toda Pergunta DEVE ter exatamente uma coluna booleana
  `pergunta_<id>__aplicavel`, qualquer que seja o tipo, como primeira coluna do grupo da
  Pergunta: [Clarifications 2026-10-02; Achado A1]
  - **verdadeiro**: a Pergunta pertence a uma Seção do percurso calculado pela 006 para as
    Respostas da Participação — percurso final, se concluída; até a Seção que ainda não
    podia ser deixada, se não concluída;
  - **falso**: a Pergunta está fora desse percurso (Seção não alcançada, ou Resposta de
    rascunho preservada fora do percurso);
  - **vazio**: sem Participação ou percurso não determinável (FR-044).

  Invariantes: valor preenchido ⇒ aplicabilidade verdadeira; aplicabilidade falsa ou vazia
  ⇒ colunas de valor vazias. A aplicabilidade é **derivada** (classificação pelas regras
  da 006), nunca declarada. NÃO DEVE ser criada entidade, modelo, cache ou implementação
  paralela da jornada para calculá-la.

**Dicionário de dados**

- **FR-050**: Toda exportação DEVE incluir a tabela Dicionário, gerada no momento da
  exportação a partir das definições fixas das colunas base e do conteúdo imutável da
  Versão. NÃO DEVE existir documentação manual separada, banco de metadados, entidade de
  coluna ou de esquema. [Const. — XVIII; Arquitetura]
- **FR-051**: O Dicionário DEVE ter uma linha de **coluna** para cada coluna de Dados, na
  mesma ordem, e, para cada Pergunta de escolha única, uma linha de **valor possível** por
  Opção, logo após a linha da coluna, na ordem das Opções. Um campo DEVE distinguir os dois
  tipos de linha. [Arquitetura]
- **FR-052**: Toda linha do Dicionário DEVE informar: nome técnico da coluna; tipo de
  valor (booleano, texto, inteiro, data); **proveniência** — `institucional` (contexto
  congelado), `derivado` (elegibilidade no snapshot, identificadores analíticos
  pseudonimizados, aplicabilidade), `coleta` (fatos da Participação) ou `declarado`
  (Respostas); e descrição em linguagem natural.

  `coleta` não cria categoria nova de dado. Designa **fatos registrados pelo próprio
  sistema durante a coleta** (existência, início e conclusão da Participação), o que a
  012 chamou de "fato do domínio": não são dado institucional da fonte acadêmica, não são
  derivados por regra e não são declarados pelo egresso (Const. — III). Os Metadados
  descrevem os quatro valores (FR-061). [Const. — III, IV, XVIII]
- **FR-053**: As linhas das colunas base DEVEM ter descrições fixas, parte do contrato,
  explicando, no mínimo: que os identificadores analíticos são pseudônimos opacos,
  estáveis apenas sob a mesma chave e não reversíveis pelo consumidor, e que
  `pessoa_analitica_id` identifica o registro de Pessoa do sistema; que o contexto é o da
  Conclusão Acadêmica **no momento da
  captura** e não declarado pelo egresso; que curso se interpreta com unidade; que ano e
  data são independentes; que elegível significa elegível no snapshot (não elegível
  atual); o significado de cada estado da Participação; que datas estão na timezone
  institucional; e que célula vazia é ausência. [Const. — III; 012 FR-090]
- **FR-054**: As linhas de colunas de Pergunta DEVEM informar, quando aplicável: posição e
  título da Seção; posição da Pergunta na Seção; texto e texto explicativo da Pergunta;
  tipo; obrigatoriedade; para Opção (coluna de escolha múltipla ou valor possível de
  escolha única), posição e texto da Opção e se admite complemento; para escala, início,
  fim e rótulos existentes; para complemento, a qual Pergunta e Opção se refere; para
  aplicabilidade, o significado de verdadeiro, falso e vazio (FR-047).
- **FR-055**: O Dicionário DEVE publicar as **regras de navegação** existentes na Versão:
  para cada Opção com regra, "finaliza" ou a posição da Seção de destino; para cada Seção
  com encaminhamento, a posição da Seção de destino, nas linhas das Perguntas dessa Seção.
  Nenhuma regra é interpretada ou simplificada. [Const. — VIII (condicionais
  recuperáveis); Achado A1]
- **FR-056**: O Dicionário DEVE identificar a Versão a que se refere. NÃO DEVE conter
  identificador canônico, código estável global, linhagem, correspondência por texto ou
  equivalência com Perguntas de outras Versões. [002/DP-006; 012 FR-077]
- **FR-057**: Textos do instrumento DEVEM ser exportados exatamente como na Versão.
- **FR-058**: O Dicionário NÃO DEVE classificar Perguntas por sensibilidade: o domínio não
  tem essa classificação (DP-1303). [Const. — XXIX]

**Metadados**

- **FR-060**: Toda exportação DEVE incluir a tabela Metadados, com pares chave–valor,
  contendo no mínimo: versão do contrato; versão do esquema de pseudonimização (FR-067);
  identificador do snapshot; momento da captura; identificador, nome, período e momento de
  abertura da Campanha; identificador, designação, título e momento de publicação da
  Versão; total de registros; elegíveis no snapshot; registros não elegíveis com
  Participação; registros com Participação; Participações concluídas; Participações com
  percurso não determinável (FR-044); número de colunas de Dados. [Const. — IV; 012
  FR-063]
- **FR-061**: Os Metadados DEVEM conter notas fixas, parte do contrato, declarando: que o
  snapshot foi escolhido por quem exportou e que nenhum snapshot é oficial (012/DP-1201);
  que os dados são individualizados, **pseudonimizados e não anônimos**; que linhas podem
  ser reidentificáveis por combinação de atributos e pela ligação entre exportações; os
  quatro valores de proveniência (FR-052); e as regras de representação (ausência,
  booleanos, datas, aplicabilidade e o escape do CSV com sua reversão, FR-075). As notas DEVEM ter o mesmo texto no CSV e no XLSX. [Const. — XVI; 012/DP-1201]
- **FR-062**: NÃO DEVE existir status institucional, oficial, aprovado ou vigente nos
  Metadados. [012 FR-061]
- **FR-063**: Todo valor dos Metadados e do Dicionário DEVE ser **fixo para o mesmo
  snapshot**, com a origem verificada no código (C10, C13): [Clarifications 2026-10-02;
  Reprodutibilidade]

  | Valor | Origem | Por que é fixo |
  |-------|--------|----------------|
  | Identificador do snapshot, momento da captura, contagens | Snapshot (012) e fatos que ele referencia | Snapshot imutável; Participações e Respostas imutáveis depois do encerramento |
  | Identificador, nome, período e momento de abertura da Campanha | Campanha (004) | Só alteráveis com a Campanha nunca aberta; abertura gravada uma vez; todo snapshot é de Campanha aberta |
  | Identificador, designação, título e publicação da Versão; Seções, Perguntas, Opções, textos e regras | Versão (002) | Só alteráveis em rascunho; a Versão de Campanha aberta é PUBLICADA |
  | Versões de contrato e de pseudonimização, notas | Constantes do contrato | Mudam só com nova versão de contrato |

  NÃO DEVEM ser exportados: o **nome da Pesquisa** (alterável a qualquer tempo, C10) e o
  **momento de encerramento explícito** da Campanha (não congelado no snapshot; pode ser
  gravado depois da captura, C13). NÃO DEVE ser criada persistência nova para guardar
  rótulos. [012 Achado A2]
- **FR-064**: NÃO DEVE existir momento de geração (`gerado_em`) no conteúdo. O momento
  historicamente relevante é o da captura. Nenhum horário de exportação DEVE escolher,
  filtrar ou reinterpretar dados. [Escopo]
- **FR-065**: A versão do contrato DEVE ser uma constante simples, alterada somente quando
  colunas base, nomes técnicos, tipos, representação ou tabelas mudarem de forma
  incompatível. Justificativa concreta: arquivos vivem fora do sistema e não são
  persistidos; sem a versão, um consumidor não sabe qual regra produziu um arquivo antigo.
  NÃO DEVE existir registro de esquemas. [Arquitetura; Const. — XXII]
- **FR-066**: Momentos (captura, abertura, publicação) DEVEM ser representados em ISO
  8601 com deslocamento explícito; datas, em ISO 8601 (`AAAA-MM-DD`). [Arquitetura]
- **FR-067**: A versão do esquema de pseudonimização DEVE ser uma constante que identifica
  algoritmo e regra de separação de domínio (FR-027). NÃO DEVE conter a chave, parte dela,
  impressão digital da chave nem qualquer material que permita derivar ou testar
  pseudônimos. [Clarifications 2026-10-02; Const. — XVI]

**Formatos e serialização**

- **FR-070**: CSV e XLSX DEVEM serializar o **mesmo dataset lógico**: mesmas tabelas,
  colunas, ordem, linhas e valores. Diferenças admitidas: tipos nativos no XLSX, texto e
  escape no CSV, e detalhes físicos do arquivo. NÃO DEVE existir semântica própria de um
  formato. [Const. — XVIII]
- **FR-071**: A exportação CSV DEVE produzir um **pacote compactado** contendo exatamente
  `dados.csv`, `dicionario.csv` e `metadados.csv`. NÃO DEVE existir formato proprietário,
  manifesto adicional ou arquivo além desses três. [Arquitetura; Const. — XVIII]
- **FR-072**: Cada CSV DEVE ser: UTF-8 sem marca de ordem de bytes; separador vírgula;
  aspas duplas conforme RFC 4180 (campos com vírgula, aspas ou quebra de linha entre
  aspas, aspas internas duplicadas); primeira linha com os nomes técnicos; independente de
  locale. [Arquitetura]
- **FR-073**: Representação de valores no CSV: booleano `true` / `false`; inteiro em
  decimal sem separador de milhar; data `AAAA-MM-DD`; momento ISO 8601 com deslocamento;
  ausência = campo vazio. [Arquitetura]
- **FR-074**: Texto DEVE ser preservado integralmente (Unicode, acentos, emoji, espaços,
  quebras de linha), sem transliteração, normalização ou corte. [Const. — VIII]
- **FR-075**: **Escape contra fórmula — parte do contrato CSV.** O CSV tem uma única
  variante, sempre com escape; NÃO DEVEM existir variantes "bruta" e "segura".
  [Clarifications 2026-10-02; Const. — XVI]
  - **Regra**: todo campo **textual** de `dados.csv`, `dicionario.csv` e `metadados.csv`
    cujo primeiro caractere seja `=`, `+`, `-`, `@`, tabulação, retorno de carro ou
    apóstrofo (`'`) recebe um apóstrofo inicial. Campos inteiros, de data, de momento e
    booleanos nunca são escapados, e nunca começam por apóstrofo. Cabeçalhos são nomes
    técnicos e nunca precisam de escape.
  - **Reversão**: em qualquer campo de qualquer dos três arquivos, se o primeiro caractere
    for apóstrofo, remover exatamente esse caractere. Não exige conhecer o tipo do campo e
    devolve o valor original em todos os casos, porque todo valor original iniciado por
    apóstrofo também é escapado.
  - **Documentação no próprio pacote**: as notas fixas dos Metadados DEVEM descrever a
    regra, os caracteres de gatilho e a reversão, e declarar que no XLSX não há escape.
  - O valor no domínio NÃO DEVE ser alterado.
- **FR-076**: Ler um CSV exportado e aplicar a reversão de FR-075 DEVE devolver valores
  idênticos aos do dataset lógico (round-trip), inclusive para textos que já começam por
  apóstrofo. [Const. — VIII]
- **FR-077**: A exportação XLSX DEVE produzir uma pasta de trabalho com exatamente três
  abas, nesta ordem: **Dados**, **Dicionário** e **Metadados**, cada uma com cabeçalho na
  primeira linha. [Arquitetura]
- **FR-078**: No XLSX, valores textuais DEVEM ser gravados como texto, nunca como fórmula,
  sem prefixo de escape (o valor é idêntico ao lógico); inteiros como número; booleanos
  como booleano; datas como data com exibição `AAAA-MM-DD`; momentos como texto ISO 8601;
  ausência como célula vazia. [Const. — XVI]
- **FR-079**: O XLSX NÃO DEVE conter fórmula, gráfico, macro, tabela dinâmica, filtro,
  formatação condicional, célula mesclada, aba oculta, validação de dados ou formatação
  além de destacar o cabeçalho. NÃO DEVE ser particionado por limites da planilha
  antecipadamente. [Escopo; Const. — XIX]
- **FR-080**: Nomes de arquivo PODEM conter um identificador curto do snapshot; NÃO DEVEM
  depender só do nome da Campanha ou da Pesquisa, nem conter pseudônimo ou identificador
  de Pessoa, Conclusão ou Participação. O nome de arquivo não é identidade: a identidade
  está nos Metadados. [Arquitetura]

**Ordem e reprodutibilidade**

- **FR-081**: Ordem das colunas de Dados: colunas base (FR-020); depois as Perguntas pela
  posição da Seção e, dentro dela, pela posição da Pergunta; dentro da Pergunta, primeiro a
  coluna de aplicabilidade, depois a coluna de valor (escolha única, texto curto, escala)
  ou as colunas de Opção pela posição da Opção (escolha múltipla), e por último o
  complemento. NÃO DEVE ordenar por texto ou
  identificador. [Arquitetura]
- **FR-082**: Ordem das linhas de Dados: a ordem técnica estável da fronteira de leitura
  da 012 (pela referência interna do registro), sem exportar o identificador interno e
  sem ordenar pelos pseudônimos (cuja ordem mudaria com a chave). NÃO DEVE depender da ordem acidental do banco.
  [Arquitetura; FR-026]
- **FR-083**: Ordem do Dicionário: a das colunas de Dados, com as linhas de valor
  possível após a coluna correspondente (FR-051). Ordem dos Metadados: fixa, definida
  pelo contrato.
- **FR-084**: Exportar o mesmo snapshot com a mesma versão de contrato DEVE produzir o
  **mesmo conteúdo analítico** (as três tabelas lidas são iguais), qualquer que seja o
  momento, o estado acadêmico atual, o nome atual da Pesquisa ou um encerramento
  explícito gravado depois da captura. Com outra chave de pseudonimização, só os
  identificadores analíticos mudam. Ressalva: a referência Conclusão → Pessoa (FR-028).
  Igualdade byte a byte de arquivos NÃO é exigida. [Const. — VIII; 012 FR-086]

**Erros**

- **FR-090**: DEVE ser recusada com erro explícito, sem produzir arquivo: exportação sem
  snapshot; com objeto que não é snapshot gravado; sem chave de pseudonimização
  configurada ou com chave inadequada (FR-027); e, se houver fronteira comum com parâmetro de formato, formato
  diferente de CSV ou XLSX. [Arquitetura]
- **FR-091**: Valor que o formato não consegue representar sem alteração (caractere
  proibido, limite de célula) DEVE causar erro explícito na exportação daquele formato.
  NÃO DEVE haver truncamento, remoção ou substituição silenciosa. [Const. — VIII]
- **FR-092**: Inconsistência estrutural inesperada DEVE causar erro explícito, sem arquivo
  parcial: Versão não publicada; tipo de Pergunta desconhecido; Resposta com forma
  incompatível com o tipo; Opção escolhida que não pertence à Pergunta; nome de coluna
  repetido. [Arquitetura]
- **FR-093**: Mensagens de erro DEVEM citar motivo, identificadores técnicos de snapshot,
  Pergunta ou Opção e contagens, nunca valores acadêmicos de uma Conclusão, conteúdo de
  Resposta, identificador interno de Pessoa ou Conclusão, pseudônimo nem a chave. NÃO DEVE existir máquina de estados de exportação. [Const. — XVI;
  Observabilidade; 012 FR-124]

**Governança e autorização**

- **FR-100**: Nesta feature, a exportação DEVE ser capacidade de domínio **não exposta** a
  operadores: sem tela, rota, API, comando ou ação na interface. É exercitada por testes.
  NÃO DEVE ser criado endpoint, UI, autenticação ou comando apenas para que exista forma de
  disparo. [Escopo; 010/DP-1001; 012 FR-100]
- **FR-101**: Nenhuma regra nova de autorização, papel ("exportador" ou outro), permissão,
  aprovação ou workflow DEVE ser criada. [Const. — X, XXII]
- **FR-102**: Quando uma feature futura expuser a exportação, ela DEVE ser restrita à
  atuação **CPAEG** ativa, em escopo institucional, e a decisão sobre quem recebe,
  armazena e compartilha os arquivos, e quem custodia e rotaciona a chave de
  pseudonimização, DEVE respeitar DP-1301. [Interpretação B1, B2; PAEG
  Art. 21, I, V]
- **FR-103**: A atuação CSAEG NÃO DEVE receber exportação do dataset individualizado, nem
  exportação filtrada por unidade, por esta feature. Agregados por unidade para o
  relatório da CSAEG (PAEG Art. 22, V) são capacidade distinta, de feature futura, com
  005/DP-505 e 011/DP-1101. [Interpretação B3; 012 FR-103]
- **FR-104**: A exportação NÃO DEVE registrar quem a solicitou nem manter histórico de
  downloads. [012 FR-104; Const. — XXII]

**Privacidade**

- **FR-110**: Nenhuma PII DEVE ser exportada: nome, CPF, matrícula, e-mail, telefone,
  endereço, identificador externo, nem hash ou código derivado deles. [Const. — XVI]
- **FR-111**: A finalidade do dataset DEVE ser declarada nos Metadados como **análise
  institucional** (PAEG Art. 10, III). NÃO é mailing, lista de destinatários nem base de
  comunicação. [Const. — XVI]
- **FR-112**: O dataset é **pseudonimizado** e NÃO DEVE ser descrito como anônimo ou
  anonimizado. Linhas podem ser reidentificáveis pela combinação de unidade, curso,
  ano/data de conclusão e Respostas (inclusive potencialmente sensíveis, como Q2, Q4, Q5 e
  Q6 do formulário 2024), e a ligação por `pessoa_analitica_id` entre Conclusões e
  exportações acumula atributos da mesma Pessoa. NÃO DEVE
  ser inventada anonimização, supressão, generalização ou limiar. [Const. — XVI;
  011/DP-1101; DP-1303]
- **FR-113**: As Respostas exportadas DEVEM ser as da Versão, sem filtro arbitrário de
  sensibilidade: o domínio não classifica Perguntas assim. A limitação fica registrada em
  DP-1303. [Const. — XXIX]
- **FR-114**: A exportação NÃO DEVE gravar arquivos no servidor, em log ou em diretório
  temporário persistente, nem registrar conteúdo de Resposta, contexto, pseudônimo ou a
  chave de pseudonimização em log. [Const. —
  XVI; Observabilidade]
- **FR-115**: Enquanto 001/DP-009 e 005/DP-504 estiverem abertas, exportações DEVEM ser
  produzidas somente com dados fictícios. [001/DP-009; 005/DP-504; 012 FR-125]

**Interoperabilidade e GeN**

- **FR-120**: O pacote CSV, com Dicionário e Metadados, É o contrato de dados para consumo
  a jusante, inclusive pelo GeN. O contrato DEVE ser compreensível sem acesso ao sistema.
  [Const. — XVIII]
- **FR-121**: NÃO DEVE ser implementado mecanismo de transporte: integração com Looker
  Studio, Data Studio, Google Sheets, BigQuery, armazenamento institucional, upload
  agendado, push, credencial de serviço, conector ou API pública. O transporte é DP-1302.
  [Const. — V, VI; Escopo]
- **FR-122**: Nenhum conceito, nome ou dependência de Looker, Data Studio, Google, BigQuery
  ou painel DEVE aparecer no domínio, no contrato ou nos nomes técnicos. [Const. — V]
- **FR-123**: Os nomes técnicos (FR-033) DEVEM ser válidos como identificadores de coluna
  em ferramentas tabulares comuns, sem depender de nenhuma em particular.

**Persistência, volume e simplicidade**

- **FR-130**: NÃO DEVE ser criada entidade, tabela ou migration: nem exportação, arquivo
  gerado, job, histórico, esquema, coluna ou dicionário persistido. A exportação é
  derivável do snapshot imutável. [Const. — XXII]
- **FR-131**: A exportação DEVE ser síncrona. NÃO DEVEM existir job, fila, worker,
  agendador, estado "processando", retry ou cache. [Const. — XXII]
- **FR-132**: NÃO DEVE ser criado framework: exportador base, registro de serializadores,
  plugins, adaptadores, data warehouse, star schema, ETL ou API genérica. Duas operações
  explícitas (CSV e XLSX) sobre o mesmo dataset lógico são suficientes. [Const. — XXII]
- **FR-133**: A exportação DEVE ler o snapshot uma vez por exportação, com número de
  consultas independente do número de registros, e memória proporcional ao snapshot. O
  CSV PODE ser produzido linha a linha; streaming NÃO É requisito. [012 FR-110;
  Arquitetura]
- **FR-134**: Nenhuma Feature 001 a 012 DEVE ser alterada, salvo acréscimo estritamente
  necessário à fronteira de leitura da 012, sem mudar seu comportamento, justificado no
  plan. Acréscimos: o conjunto de Perguntas do percurso de cada Participação, pela mesma
  composição de regras da 006 (FR-047), e o parâmetro opcional que reaproveita o conteúdo
  da Versão já lido. A referência técnica da Conclusão à
  Pessoa (FR-028) é lida pela própria exportação, sem atributo da Pessoa e sem alterar a
  leitura da 012. Nenhuma tabela ou migration. [Escopo; plan R1]

**Verificação**

- **FR-140**: Todos os casos A a V DEVEM ser verificados automaticamente com dados
  fictícios: criar snapshot, exportar nos dois formatos, reabrir, conferir Dados,
  Dicionário e Metadados. [Const. — XXV, XXVI]
- **FR-141**: O cenário de demonstração existente NÃO DEVE ser alterado. [012 FR-131]

### Key Entities *(include if feature involves data)*

**Novas persistidas**: nenhuma.

**Artefatos derivados, não persistidos**:

- **Dataset lógico de exportação**: Dados, Dicionário e Metadados de um snapshot,
  derivados a cada exportação.
- **Contrato de exportação**: as regras desta spec, identificadas por uma constante de
  versão.
- **Pseudônimos analíticos**: `conclusao_analitica_id` e `pessoa_analitica_id`,
  recalculados a cada exportação a partir dos identificadores internos e da chave; nunca
  persistidos.

**Configuração (não persistida no banco)**: chave secreta dedicada de pseudonimização
analítica, fornecida pelo ambiente (FR-027).

**Existentes, somente lidas**:

- **Snapshot analítico e registros** (012): pela fronteira de leitura.
- **Campanha** (004): identificação, nome, período e momento de abertura.
- **Conclusão Acadêmica** (001): somente a referência técnica à sua Pessoa (FR-028).
- **Versão, Seção, Pergunta, Opção** (002): estrutura, textos e regras.
- **Participação e Resposta** (005, 006): somente pela fronteira da 012.

**Não lidas**: atributos de Pessoa, contexto da Conclusão atual, fonte acadêmica,
população atual, vínculos de governança, nome da Pesquisa, momento de encerramento
explícito da Campanha.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado exportado | Origem | Fonte | Tratamento de divergência |
|----------------|--------|-------|---------------------------|
| Unidade, curso, nível, modalidade, forma de oferta, ano e data de conclusão | **Institucional**, congelado no snapshot | Registro do snapshot (012) | Nenhum recálculo; divergência com Resposta não tratada (005/DP-508) |
| `conclusao_analitica_id`, `pessoa_analitica_id` | **Derivado** (pseudônimo com chave) | HMAC-SHA-256 sobre identificadores internos (FR-027) | Estáveis sob a mesma chave; Pessoa sujeita a 001/DP-003 |
| Elegível no snapshot | **Derivado**, congelado | Registro do snapshot (012) | Não recalculado |
| Aplicabilidade por Pergunta | **Derivado** (classificação) | Regras puras da 006 sobre Versão e Respostas, pela 012 | Recalculável com o mesmo resultado |
| Possui Participação, concluída, datas | **Coleta** (fato do domínio) | Participação (005, 006), pela 012 | Imutáveis depois do encerramento |
| Colunas de Pergunta | **Declarado** | Respostas válidas para o percurso (005, 006, 012) | Nunca completadas ou corrigidas |
| Dicionário | Configuração do instrumento + definição do contrato | Versão (002) | Imutável |
| Metadados | Fatos do snapshot, da Campanha fixados na abertura e da Versão publicada; contagens derivadas; constantes do contrato | 012, 004, 002 | Fixos para o snapshot (FR-063) |

### Análise de persistência

- **O que se persiste**: nada. A exportação é derivável do snapshot imutável, da Versão
  imutável e dos fatos transacionais imutáveis depois do encerramento.
- **O que não se persiste e por quê**: arquivo gerado, histórico de exportação,
  solicitante, esquema, dicionário e pseudônimos (regeneráveis; sem consumidor; FR-104,
  FR-130); tabela de correspondência de pseudônimos (desnecessária com HMAC: o cálculo é
  determinístico sob a chave).
- **Migrations**: nenhuma.
- **Consequência**: não há retenção de arquivos a decidir no sistema; arquivos levados para
  fora são objeto de DP-1301.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Os 22 casos importantes (A a V) são demonstrados por verificação automatizada
  com dados fictícios, com 100% dos resultados conforme a spec.
- **SC-002**: Em 100% das exportações do conjunto de referência, o número de linhas de
  Dados é igual ao número de registros do snapshot, e os totais deriváveis de Dados
  coincidem com os indicadores da 012.
- **SC-003**: Em 100% das exportações, as três tabelas lidas do CSV (após a reversão de
  escape) e do XLSX são idênticas.
- **SC-004**: Duas exportações do mesmo snapshot, feitas antes e depois de alterar o
  contexto acadêmico de 100% das Conclusões, de incorporar Conclusões novas elegíveis e de
  renomear a Pesquisa, produzem tabelas idênticas.
- **SC-005**: 100% das colunas de Dados têm exatamente uma linha de coluna no Dicionário,
  na mesma ordem, e 100% dos nomes técnicos seguem a regra de FR-033 sem derivar de texto.
- **SC-006**: Nenhum arquivo exportado contém nome, CPF, matrícula, e-mail, telefone,
  endereço, identificador externo, identificador interno de Pessoa, Conclusão,
  Participação ou registro, nem a chave de pseudonimização, verificado sobre o conjunto de
  referência.
- **SC-007**: 100% dos textos iniciados por caracteres de fórmula abrem no XLSX como texto
  (zero fórmulas), e 100% dos valores do CSV voltam exatamente ao original pela reversão
  documentada.
- **SC-008**: 100% dos textos com acentos, emoji, aspas, vírgulas, quebras de linha e
  espaços nas pontas sobrevivem ao round-trip nos dois formatos.
- **SC-009**: Zero Respostas fora do percurso aparecem como valor ou indicador em Dados.
- **SC-010**: Um analista, só com o pacote CSV (sem acesso ao sistema), identifica de qual
  snapshot, Campanha, Versão e momento de captura os dados vieram, o significado de cada
  coluna e calcula taxa de início e de conclusão iguais às da 012.
- **SC-011**: Depois da feature, existem zero entidades e zero migrations novas, e nenhuma
  página, rota, comando ou regra de autorização nova.
- **SC-012**: Exportar um snapshot fictício de 20.000 registros com instrumento do tamanho
  do formulário 2024 termina em menos de 1 minuto em cada formato, no ambiente de
  desenvolvimento. [Hipótese]
- **SC-013**: Com a mesma chave, 100% das Conclusões e Pessoas presentes em exportações de
  snapshots diferentes têm o mesmo identificador analítico; com chaves diferentes, 0%
  coincidem; sem chave, 100% das tentativas falham sem arquivo.
- **SC-014**: Em 100% das linhas com Participação e percurso determinável, toda Pergunta
  tem aplicabilidade verdadeira ou falsa, e nenhuma célula de valor está preenchida com
  aplicabilidade falsa ou vazia.

## Assumptions

Apenas suposições não institucionais; as regras institucionais em aberto estão em
"Decisões Pendentes".

- O único escritor legítimo da base é o Trajetória Ifes, pelas operações de domínio (ADR
  0002); as imutabilidades garantidas pela 012 valem nesse regime.
- Volume: até dezenas de milhares de registros por snapshot e um instrumento da ordem de
  50 Perguntas e algumas centenas de colunas; exportações raras. [Hipótese]
- A fronteira de leitura da 012 (registros com contexto, elegibilidade, Participação,
  Respostas e classificação de percurso; indicadores) é suficiente, com o acréscimo mínimo
  de FR-134 (Perguntas do percurso); a referência Conclusão → Pessoa é lida pela 013.
- O ambiente de execução pode fornecer uma chave secreta dedicada, como já fornece os
  demais segredos de configuração; nos testes, uma chave fictícia. [Hipótese]
- A timezone institucional configurada (America/Sao_Paulo) é a referência das datas da
  Participação.
- Ferramentas tabulares comuns aceitam nomes de coluna de até ~90 caracteres (o mais longo
  é `pergunta_<32>__opcao_<32>`).

## Relação com outras features

- **001** — contexto não lido (vem congelado pela 012); só a referência Conclusão →
  Pessoa, para `pessoa_analitica_id` (FR-028). 001/DP-003 mantida.
- **002/003** — Versão lida para gerar colunas e Dicionário; nada alterado. 002/DP-006
  mantida.
- **004** — lida só para identificação, nome, período e abertura da Campanha nos
  Metadados; encerramento explícito, população e elegibilidade nunca consultados.
- **005/006** — Respostas e estado da Participação pela 012; classificação de percurso e
  Perguntas do percurso pelas regras puras da 006, via 012; nada alterado.
- **007/008/009** — sem efeito.
- **010** — nenhuma regra nova; interpretação CPAEG registrada para a feature que expuser.
- **011** — inalterada; agregados operacionais continuam lá.
- **012** — consumida pela fronteira pública de leitura; o snapshot é sempre explícito.
  Decisões que a 012 deixou para cá: achatamento (wide), serialização de escolha múltipla
  (indicadores), identificadores expostos (pseudônimos analíticos de Pessoa e Conclusão;
  nenhum interno; nenhum de Participação), rótulos e arquivos. A fronteira de leitura
  recebe um acréscimo mínimo (FR-134). A vedação de pseudônimo exportável da 012
  (012 FR-122) valia para o snapshot; esta é a decisão consciente que ela remeteu a
  feature futura.
- **Futura feature de comunicação** — nenhum dado desta exportação serve a mailing ou
  segmentação.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade (NON-NEGOTIABLE)**: grão Conclusão; nenhuma fusão de Conclusões
  ou Campanhas (FR-010, FR-002); mesma Conclusão e mesma Pessoa ligáveis entre exportações
  por pseudônimos estáveis sob a mesma chave (FR-027).
- **III — Dado institucional não é declarado (NON-NEGOTIABLE)**: proveniência por coluna no
  Dicionário (FR-052, FR-053); contexto nunca rotulado como Resposta.
- **IV — Proveniência**: Metadados com snapshot, captura, Campanha e Versão (FR-060).
- **V — Integrações desacopladas (NON-NEGOTIABLE)**: contrato sem Looker, Google ou
  transporte (FR-121, FR-122).
- **VII — Conceitos distintos (NON-NEGOTIABLE)**: snapshot, Campanha, Versão e
  Participação identificados separadamente nos Metadados.
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: valores congelados; textos exatos;
  reprodução determinística (FR-022, FR-074, FR-084).
- **X — Governança**: sem papel novo; CPAEG quando exposto (FR-101, FR-102).
- **XII — Base central; escopos**: nada à CSAEG (FR-103).
- **XVI — Privacidade (NON-NEGOTIABLE)**: sem PII, sem identificador interno, sem hash de
  dado pessoal; pseudônimos com chave dedicada fora do repositório; datas por dia;
  "pseudonimizado, não anônimo" declarado; somente dados fictícios (FR-026 a FR-029,
  FR-110 a FR-115).
- **XVIII — Exportabilidade**: CSV obrigatório, XLSX por conveniência, mesmo dataset
  lógico, Dicionário com proveniência (FR-070 a FR-079).
- **XIX — Não é BI**: sem gráficos, KPIs ou painéis (FR-079).
- **XXII — YAGNI**: zero entidades, zero job, zero framework (FR-130 a FR-132).
- **XXIII — Não é form builder**: só os quatro tipos existentes (FR-030).
- **XXIX — Hipóteses não viram requisitos (NON-NEGOTIABLE)**: sensibilidade, transporte e
  compartilhamento ficam pendentes.

**Tensões identificadas (não são conflitos)**:

- **"Qualidade das Exportações" × minimização**: a Constituição lista, "quando
  pertinente", "identificador permitido da pessoa" e identificador da participação. O
  identificador permitido é o pseudônimo analítico com chave (FR-027), não o interno nem
  derivado de dado pessoal; o de Participação não é pertinente (Achado A3). A ligação
  aumenta o risco de reidentificação, tratado como pseudonimização declarada e governança
  (DP-1301, DP-1303).
- **I × 001/DP-003**: `pessoa_analitica_id` liga registros de Pessoa do sistema, não
  identidades reconciliadas entre fontes (FR-028).
- **XVI × escape no CSV**: o escape altera a representação física do CSV, mas não o valor:
  é reversível e documentado (FR-075, FR-076).
- **XVIII ("combinar … conclusão acadêmica; datas") × minimização**: a Conclusão é o grão,
  representada pelo contexto congelado e pelo pseudônimo; datas da Participação por dia.
- **005/DP-503 × Respostas de rascunho**: Respostas válidas para o percurso de
  Participações não concluídas aparecem, marcadas por `participacao_concluida` falso; seu
  uso analítico continua pendente.

Nenhum conflito com a Constituição, com a PAEG ou com as Features 001 a 012 foi
identificado.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence ao domínio?** Sim: "exportação e disponibilização estruturada dos dados" está
   na Fronteira do Domínio.
2. **É necessária ao ciclo?** Sim: sem exportação, a análise (PAEG Art. 10, III) não sai do
   sistema.
3. **Existe solução mais adequada?** Para BI e painéis, sim (GeN), e por isso ficam fora.
   Para produzir dados fiéis ao instrumento e ao snapshot, não.
4. **Integração seria suficiente?** O GeN precisa de uma fonte; esta feature define o
   contrato; o transporte é DP-1302.
5. **Aumenta o acoplamento?** Não: nenhuma entidade nova; o domínio não conhece o
   consumidor.

## Out of Scope *(mandatory)*

- Escolha de snapshot oficial; junção de snapshots; comparação de Campanhas ou Versões.
- BI, dashboard, gráficos, KPIs, ranking, filtros interativos, pivot, estatística.
- Integração com Looker Studio, Google Sheets, BigQuery, armazenamento institucional;
  upload, push ou agendamento; API pública; credenciais de serviço.
- Job, fila, worker, cache, estado de processamento.
- Persistência de arquivos, histórico de exportações, registro de solicitante.
- Interface, rota, comando, download ou regra de autorização nova (história P3).
- Exportação por unidade ou para CSAEG; agregados por unidade.
- Formato long, tabela de Respostas, dimensão de Opções, star schema, ETL.
- Identificador global de Pergunta ou de Opção, linhagem, equivalência entre Versões.
- Identificadores internos de Pessoa, Conclusão, Participação ou registro; identificador
  de Participação; hash de CPF, matrícula, e-mail ou identificador externo; tabela de
  correspondência de pseudônimos; serviço de identidade; reconciliação de Pessoas.
- Anonimização, supressão de grupos pequenos, generalização, classificação de
  sensibilidade.
- Indicador derivado de recusa, completude ou abandono.
- Mailing, listas de destinatários, segmentação, pixel, rastreamento de clique.
- Dados nominais; identidade real; qualquer alteração das Features 001 a 012 além de
  FR-134.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: decisões novas usam o prefixo 13 (DP-1301…). As das features anteriores são
citadas como 00n/DP-nnn.

**Novas nesta feature**

- **DP-1301** — DECISÃO PENDENTE: **compartilhamento do dataset individualizado** — quem
  pode gerar e receber a exportação, onde arquivos podem ser armazenados fora do sistema,
  com quem podem ser compartilhados, por quanto tempo e sob qual termo de
  responsabilidade.
  - Instância competente: CPAEG/Proex, com o encarregado de dados.
  - Inclui: **quem administra, guarda e pode rotacionar a chave de pseudonimização
    analítica**, e quando a rotação (que rompe a ligação longitudinal com exportações
    anteriores) é admitida.
  - Impacto: FR-027, FR-029, FR-100 a FR-103; qualquer exposição da exportação.
  - Tratamento provisório: nada exposto; CPAEG como hipótese quando exposto; chave
    fictícia, só em ambiente não produtivo; somente dados fictícios.
- **DP-1302** — DECISÃO PENDENTE: **mecanismo concreto de consumo pelo GeN** — arquivo
  entregue manualmente, armazenamento institucional, planilha compartilhada, banco
  analítico ou outro; e se o transporte carrega as três tabelas ou só Dados (FR-021).
  - Instância competente: CPAEG/Proex, com a área de TI responsável pelo GeN.
  - Impacto: FR-120 a FR-123; FR-021.
  - Tratamento provisório: contrato de dados definido (pacote CSV); nenhum transporte.
- **DP-1303** — DECISÃO PENDENTE: **respostas sensíveis e risco de reidentificação** no
  dataset individualizado — se Perguntas potencialmente sensíveis (por exemplo, Q2, Q4,
  Q5, Q6) devem ser excluídas ou restritas, se a data de conclusão deve ser generalizada,
  se a pseudonimização adotada (FR-027) basta para cada finalidade ou se alguma exige
  anonimização, e se a ligação longitudinal por `pessoa_analitica_id` deve ser restrita a
  certas finalidades.
  - Instância competente: encarregado de dados, com CPAEG. Relaciona-se com 005/DP-504 e
    011/DP-1101.
  - Impacto: FR-058, FR-112, FR-113; contrato (mudança exigiria nova versão de contrato).
  - Tratamento provisório: todas as Perguntas da Versão exportadas; pseudônimos sempre
    presentes; nenhum filtro, generalização ou anonimização; "pseudonimizado, não
    anônimo" declarado; somente dados fictícios.

**Herdadas, afetadas e mantidas abertas**

- **012/DP-1201** — snapshot de referência para publicação: **mantida**; todo export
  recebe o snapshot (FR-001); nota nos Metadados (FR-061).
- **012/DP-1202** — retenção de snapshots: **mantida**; a 013 não persiste arquivos.
- **002/DP-006** — comparabilidade entre Versões: **mantida**; chaves locais à Versão
  (FR-031, FR-056).
- **005/DP-503** — uso analítico de Participações não concluídas: **mantida**; Respostas
  válidas aparecem marcadas, nunca misturadas silenciosamente (FR-043).
- **005/DP-504** e **001/DP-009** — base legal, consentimento, retenção: **mantidas**;
  bloqueiam uso com dados reais (FR-115).
- **005/DP-505** — consulta de dados identificados e Participações: **mantida**; nenhum
  identificador interno ou dado identificador exportado; só pseudônimos (FR-026, FR-027).
- **005/DP-508** — divergência entre resposta declarada e dado institucional: **mantida**;
  ambos exportados, sem comparação.
- **006/DP-601** — recusa: **mantida**; concluída, sem coluna derivada (FR-041).
- **007/DP-703** — "iniciada": **mantida**; `possui_participacao` = Participação existente.
- **010/DP-1001** — identificação produtiva: **mantida**; nada exposto (FR-100).
- **010/DP-1005** e **001/DP-007** — grafia das unidades: **mantidas**; valores como
  congelados.
- **011/DP-1101** — pequenos grupos: **mantida**; nenhum limiar; acesso restrito quando
  exposto (FR-102, FR-112).
- **011/DP-1102** — coorte: **mantida**; ano e data exportados, sem coorte.
- **001/DP-003** — reconciliação de identidade: **mantida**; `pessoa_analitica_id` liga
  registros de Pessoa do sistema, sem reconciliar fontes; efeito de reconciliação futura
  sobre o pseudônimo fica com quem resolver a DP (FR-028).
- **ADR 0002** e **ADR 0003** (Q14 declarada): respeitados.


## Nota de revisão pela Feature 019 (2026-10-04)

FR-010, FR-020 e FR-026 acrescentam origem_formacao, derivada, com valores institucional, declarada_validada_fonte_digital e declarada_validada_acervo, vazia sem Participação. FR-065: contrato versão 2. FR-021 trata colunas constantes por construção; uma origem igual em todas as linhas de uma campanha não justifica remover essa coluna variável. Nenhum dado da declaração ou da decisão é exportado.

Referência: [019 — Formação não localizada e validação posterior](../019-formacao-declarada-validacao/spec.md).
