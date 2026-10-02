# Feature Specification: Dataset analítico institucional reprodutível

**Feature Branch**: `claude/feature-012-dataset-analitico-bdc50a`

**Created**: 2026-10-02

**Status**: Approved (consolidado em 2026-10-02)

**Input**: User description: "Feature 012 — Dataset analítico institucional reprodutível.
Introduzir um snapshot analítico institucional imutável de uma Campanha encerrada que
efetivamente entrou em coleta, congelando somente o que pode derivar — pertencimento à
população analítica e contexto acadêmico usado na análise — e referenciando Campanha,
Versão, Participação e Respostas, já historicamente imutáveis. Grão: Conclusão Acadêmica.
Universo: elegíveis no momento da captura ∪ Conclusões com Participação na Campanha, com
elegibilidade congelada explícita. Sem CSV, XLSX, GeN, dashboard, data warehouse, ETL,
materialized view, jobs, comunicação ou dados individuais navegáveis."

## Contexto

As onze primeiras features estabeleceram:

- **001** — **Pessoa → Conclusão Acadêmica**. A Conclusão traz, cada um possivelmente não
  informado: curso, unidade, nível, modalidade, forma de oferta, ano de conclusão e data
  de conclusão (com data, o ano é obrigatório e coerente). É o **contexto acadêmico** da
  001 (001 FR-009 a FR-011). A incorporação é idempotente e **nunca atualiza nem remove**:
  divergências com a fonte são só sinalizadas (001 FR-033; DP-005, DP-006).
- **002/003** — Pesquisa e Versão (RASCUNHO → PUBLICADA, irreversível). Versão publicada,
  com Seções, Perguntas e Opções, é integralmente imutável (002 FR-013, FR-016, FR-017),
  garantida pelas operações de domínio (ADR 0002).
- **004** — **Campanha**: exatamente uma Versão, período, seis critérios, estado derivado
  **EM PREPARAÇÃO | EM COLETA | ENCERRADA**. A primeira abertura registra o momento de
  abertura e fixa Versão, período, critérios e nome (004 FR-043). O encerramento ocorre
  explicitamente ou pelo fim do período; nenhuma reabertura (004/DP-405). A **população
  elegível é dinâmica**: as Conclusões que satisfazem os critérios **no momento da
  consulta**, sem lista materializada e sem denominador histórico (004 FR-031, FR-032;
  **DP-408**).
- **005/006** — **Participação** por par Campanha × Conclusão, criada só com a Campanha EM
  COLETA e a Conclusão ELEGÍVEL; nunca removida (005 FR-017). Respostas escritas só com a
  Campanha EM COLETA e a Participação não concluída. A conclusão é registrada uma única
  vez, só em coleta, e é irreversível (006 FR-003, FR-038).
- **007/008/009** — entrada do egresso, interface e editor.
- **010** — governança: vínculos CPAEG (institucional) e CSAEG (unidade).
- **011** — acompanhamento operacional: responde **"como está a coleta agora?"** com
  **elegíveis atuais**, Participações existentes e seis recortes, e avisa, para Campanha
  encerrada, que a população atual pode diferir da população do encerramento.

Até aqui, nenhuma capacidade responde:

> **"Qual conjunto de dados sustentava esta análise institucional em determinado
> momento?"**

nem permite reproduzir um resultado sem depender do estado futuro da fonte acadêmica.
Esta feature introduz essa base, como **snapshot analítico** imutável de uma Campanha
encerrada.

### Princípios desta spec

1. **Congelar somente o que pode derivar.** O que já é historicamente imutável é
   referenciado, nunca copiado.
2. **Snapshot ≠ Campanha.** A Campanha continua sendo a execução transacional; o
   snapshot é uma fotografia produzida a partir dela. A Campanha não ganha atributo
   analítico.
3. **O corte é o que a captura leu.** O conteúdo congelado é o conjunto de valores
   efetivamente lidos e copiados pela operação de captura, que é atômica: o snapshot
   existe completo ou não existe.
4. **Imutável e completo, ou inexistente.** Sem edição, sem correção, sem estado
   intermediário.
5. **Grão: Conclusão Acadêmica, não Pessoa.**
6. **Numerador histórico não desaparece.** Participação existente permanece representada,
   mesmo fora da população congelada.
7. **Fronteira de leitura, não formato de exportação.** A 013 decide como os dados viram
   arquivos.

### Verificação de imutabilidade no código

Antes de propor persistência, cada dado foi verificado no código das Features 001 a 011
(único caminho de escrita: as operações de domínio de cada feature; ADR 0002).

| # | Dado | Pode mudar depois do encerramento da Campanha? | Evidência | Consequência para a 012 |
|---|------|-------------------------------------------------|-----------|--------------------------|
| V1 | Versão PUBLICADA e suas Seções, Perguntas, Opções, regras e textos | **Não** | Toda operação do instrumento exige Versão em rascunho; publicação irreversível (002 FR-013, FR-016, FR-017; ADR 0002) | **Referenciar** pela Campanha. Nada é copiado |
| V2 | Campanha: Versão, período, critérios, nome | **Não**, desde a primeira abertura | Toda operação de preparação exige Campanha nunca aberta (004 FR-043) | **Referenciar** |
| V3 | Momentos de abertura e de encerramento explícito | **Não** | Gravados uma única vez (004 FR-036, FR-040) | **Referenciar** |
| V4 | Estado ENCERRADA de Campanha que foi aberta | **Não** volta a EM COLETA | Fim do período fixo desde a abertura; encerramento explícito gravado uma vez; reabertura inexistente (004/DP-405) | Condição de captura estável |
| V5 | Existência de Participação | **Não** | Criação exige EM COLETA (004 FR-053; 005 FR-011); nenhuma remoção (005 FR-017) | **Referenciar** |
| V6 | Início e conclusão registrados da Participação | **Não** | Início gravado na criação; conclusão gravada uma vez, só em coleta (006 FR-003, FR-038) | **Referenciar** |
| V7 | Respostas e seleções de escolha múltipla | **Não** | Escrever, remover e concluir exigem EM COLETA; concluída é imutável em qualquer estado (005 FR-039; 006 FR-038) | **Referenciar**. Nenhuma cópia |
| V8 | Respostas de Participação em rascunho no encerramento que ficaram **fora do percurso** | **Não**, mas existem | A limpeza das Respostas inativas só ocorre ao concluir (006 FR-030, FR-032, FR-035); depois do encerramento não há conclusão | Ver **Achado A1** |
| V9 | Nome da Pesquisa | **Sim**, a qualquer tempo | Renomear Pesquisa não toca Versão (002 FR-003) | Não é atributo analítico nem contexto acadêmico; ver **Achado A2** |
| V10 | Atributos acadêmicos da Conclusão | **Hoje não**, por tratamento provisório | Incorporação nunca atualiza; divergência só sinalizada (001 FR-033). A estabilidade decorre de 001/DP-005 e DP-006 **abertas**, não de invariante | **Congelar**. Ver **Achado A3** |
| V11 | Pertencimento à população elegível da Campanha | **Sim, hoje** | Conclusões incorporadas depois do encerramento que satisfaçam os critérios entram na população (004 FR-032); correções futuras também a alteram (001/DP-005) | **Congelar**. Ver **Achado A4** |
| V12 | Pessoa | Fora do grão | — | **Não** é lida nem copiada |

**Achados**

- **A1 — Respostas fora do percurso em rascunho.** Uma Participação que estava em
  rascunho quando a Campanha encerrou conserva todas as Respostas gravadas, inclusive as
  que o percurso final tornaria inativas, porque a remoção das inativas só acontece na
  conclusão, e rascunhos nunca concluídos as mantêm, sem limpeza automática (006 FR-030,
  FR-032, FR-033). Esse conjunto **não muda** depois do encerramento, e quais Respostas
  estão fora do percurso é **derivável** pelas regras puras da 006 a partir da Versão e
  das Respostas, ambas imutáveis. Logo, **não há o que congelar**; o que a 012 DEVE
  garantir é que o dataset derivado não apresente essas Respostas como se fossem de
  Participação concluída (FR-075). Como representá-las numa exportação é da 013, e seu
  uso analítico é **005/DP-503**.
- **A2 — Nome da Pesquisa é mutável.** O nome da Pesquisa pode ser alterado a qualquer
  tempo e não integra a Versão (002 FR-003). Ele é rótulo do instrumento lógico, não dado
  do egresso nem contexto acadêmico. O snapshot identifica o instrumento pela Campanha e
  pela Versão (designação imutável depois da publicação) e **não** congela o nome. Se a
  013 precisar do rótulo histórico do instrumento, deve decidir isso lá.
- **A3 — Contexto acadêmico hoje estável, mas não por invariante.** Pelo código atual,
  nenhum caminho suportado altera curso, unidade, nível, modalidade, forma de oferta, ano
  ou data de uma Conclusão. Isso é o **tratamento provisório** de 001/DP-005 (correção) e
  001/DP-006 (sincronização), que a 004, a 005 (DP-507) e a 011 (FR-038) declaram que
  **pode mudar**. Congelar esses atributos é, portanto, a proteção exata contra uma
  deriva anunciada, e não duplicação de dado imutável.
- **A4 — A população já deriva hoje.** Mesmo sem correção acadêmica, a população atual
  de uma Campanha encerrada cresce quando Conclusões que satisfazem os critérios são
  incorporadas depois do encerramento (004 FR-032). É a deriva **presente e concreta** que
  a 011 avisa e que esta feature congela.
- **A5 — Hoje, toda Participação é de Conclusão elegível.** A elegibilidade é verificada
  na criação, os critérios são fixos desde a abertura e os atributos não mudam (A3). Logo,
  com o código atual, o conjunto "Participação de Conclusão não elegível no snapshot" é
  sempre vazio. A 012 o especifica (FR-030 a FR-034) porque a correção futura o tornará
  possível, sem criar detecção, alerta ou infraestrutura para ele. Os casos G, J e K são
  verificados com dados fictícios preparados diretamente no teste, simulando a correção
  futura, **sem** criar operação de correção.

Nenhum dado presumido imutável se mostrou mutável de forma que exija cópia. Por isso a
persistência proposta se limita a V10 e V11.

### Análise normativa

Fonte: PAEG — Resolução CS nº 177/2023, anexo
(`docs/referencias/paeg-resolucao-cs-177-2023-anexo.pdf`).

#### A. Competências previstas pela PAEG relevantes para esta feature

| # | Competência | Artigo |
|---|-------------|--------|
| A1 | Execução mínima da PAEG: **análise e sistematização dos dados coletados** para geração de indicadores (empregabilidade, verticalização, realização profissional, retenção no emprego, educação continuada, entre outros) | Art. 10, III |
| A2 | Objetivo: **banco de dados** que auxilie no aprimoramento dos PPCs; **criar indicadores** de avaliação contínua | Art. 8º, I, VI |
| A3 | **CPAEG**: planejar, organizar, executar e **avaliar** as atividades da PAEG **no âmbito do Ifes** | Art. 21, I |
| A4 | **CPAEG**: **atualizar o banco de dados central** contendo as informações necessárias para o acompanhamento e **análise** do desenvolvimento profissional e acadêmico do egresso | Art. 21, V |
| A5 | **CPAEG**: elaborar o relatório anual de suas atividades e apresentá-lo à Proex | Art. 21, IV |
| A6 | **CSAEG**: elaborar relatório com os **resultados da Pesquisa do Egresso** e reportá-los à CPAEG | Art. 22, V |
| A7 | **Proex**: Relatório Anual de Acompanhamento de Egressos, compilado a partir das CSAEGs | Art. 14 |

**O que a PAEG não diz**: não define quando uma rodada de coleta é "fechada" para análise,
qual fotografia sustenta um relatório, por quanto tempo dados analíticos são retidos, nem
quem acessa registros individuais.

#### B. Interpretação operacional adotada por esta feature

Técnica, reversível e localizada (Princípio XXIX). Não cria competência institucional.

| # | Interpretação | Fundamento |
|---|---------------|------------|
| B1 | Produzir uma fotografia estável dos dados de uma Campanha encerrada é parte de **sistematizar os dados coletados** e de manter o **banco de dados central** para análise | A1, A2, A4 |
| B2 | Essa capacidade é **institucional e central**: compete à atuação **CPAEG**, quando vier a ser exposta a operadores | A3, A4 |
| B3 | A CSAEG **não** produz snapshot e **não** recebe acesso a registros analíticos individuais por esta feature. O relatório de resultados da unidade (A6) pode futuramente se apoiar em **agregados** de um snapshot, mas nenhuma superfície o consome nesta feature | A6; 005/DP-505; DP-1101 |
| B4 | A existência do snapshot não decide qual fotografia sustenta o Relatório Anual ou outra publicação | A5, A7; DP-1201 |

#### C. Decisões institucionais não tomadas aqui

Ver "Decisões Pendentes": qual snapshot sustenta publicação (DP-1201), retenção de
snapshots (DP-1202), acesso a dados individuais (005/DP-505), pequenos grupos
(011/DP-1101), coorte (011/DP-1102), comparabilidade entre Versões (002/DP-006),
correção acadêmica (001/DP-005; 005/DP-507), recusa (006/DP-601), "iniciada"
(007/DP-703), base legal e retenção (001/DP-009; 005/DP-504).

### Termos usados nesta spec

Os nomes são conceituais; a nomenclatura concreta pertence ao plan.

- **Snapshot analítico** (ou **snapshot**; "fotografia" em 004/DP-408): registro
  imutável, produzido explicitamente a partir de **uma** Campanha encerrada que entrou
  em coleta, que fixa, **num único momento de captura**, (a) o universo de Conclusões
  Acadêmicas relevante para a Campanha, (b) para cada uma, se pertencia à população
  elegível naquele momento e (c) o contexto acadêmico institucional de cada uma naquele
  momento. Campanha, Versão, Participação e Respostas são referenciadas, não copiadas.
- **Captura**: a operação que produz um snapshot.
- **Momento da captura**: o momento técnico em que a captura foi produzida, definido pela
  própria operação. Não é promessa de leitura simultânea e isolada de todas as tabelas.
- **Registro do snapshot** (ou **registro**): a representação de uma Conclusão Acadêmica
  no universo de um snapshot.
- **Universo do snapshot**: o conjunto de Conclusões com registro (FR-030).
- **Elegível no snapshot**: Conclusão que pertencia à população elegível da Campanha,
  segundo a 004, no momento da captura. Distinto de **elegível atual** (011).
- **Denominador histórico do snapshot** (ou **elegíveis do snapshot**): o número de
  registros elegíveis no snapshot.
- **Contexto acadêmico congelado**: os atributos de contexto acadêmico da Conclusão
  (001), com os valores que tinham no momento da captura.
- **Dataset do snapshot**: a visão de leitura que combina o snapshot com Campanha, Versão,
  Participação e Respostas (FR-070). Não é tabela nem arquivo.
- **Não informado**: atributo ausente na Conclusão no momento da captura (001 FR-010).

### Decisões desta especificação

Escolhas reversíveis, marcadas **[Hipótese]**, **[Arquitetura]** ou **[Interpretação
B#]** nos requisitos:

1. **Captura somente de Campanha ENCERRADA que foi aberta** (FR-010 a FR-014). Nenhum
   snapshot parcial, periódico ou durante a coleta: isso é função da 011.
2. **Captura explícita**, nunca automática: o encerramento pelo fim do período é
   derivado e não é um evento, e nada é agendado (FR-015).
3. **Universo = elegíveis no momento da captura ∪ Conclusões com Participação na
   Campanha**, uma linha por Conclusão, com elegibilidade explícita (FR-030 a FR-034).
4. **Congelar somente**: elegibilidade no snapshot e os sete atributos de contexto
   acadêmico da 001 (FR-040 a FR-046). Nada de Pessoa, identificadores externos,
   Participação, Respostas, Versão ou critérios.
5. **Vários snapshots imutáveis por Campanha**, independentes, identificados pelo momento
   de captura, **sem** status de oficial, vigente, aprovado ou substituído (FR-060 a
   FR-063). Qual sustenta uma publicação é **DP-1201**.
6. **Duas entidades novas**: snapshot e registro do snapshot (Key Entities). Nenhuma
   terceira.
7. **Sem interface e sem regra nova de autorização**: a captura é capacidade de domínio
   não exposta a operadores, como as operações de Campanha da 004 (004/DP-402). Quando
   for exposta, DEVE ser restrita à CPAEG (FR-100 a FR-104). [Interpretação B2, B3]
8. **Leitura reprodutível** dos indicadores básicos e dos seis recortes da 011 sobre os
   valores congelados (FR-080 a FR-087), sem tocar a 011.
9. **Dataset estruturado, não achatado**: Respostas na estrutura semântica existente,
   sem colunas por Pergunta nem serialização de escolha múltipla (FR-070 a FR-077).

## Clarifications

### Session 2026-10-02

Decisões consolidadas pelo solicitante na aprovação da spec, antes do plan. Deixam de ser
hipóteses e passam a ser decisões desta feature. **Não é necessário `/speckit-clarify`.**

- Q: Pode haver mais de um snapshot por Campanha? → A: **Sim.** Uma Campanha encerrada
  pode ter vários snapshots imutáveis; cada um é fotografia independente do estado
  institucional no seu momento de captura. Uma nova captura não altera nem invalida as
  anteriores. Sem oficial, vigente, aprovado, substituído, principal, status ou workflow.
  (FR-060, FR-061)
- Q: Algum consumidor pode presumir "o snapshot mais recente"? → A: **Não.** Enquanto
  DP-1201 estiver aberta, NÃO existe regra implícita de usar o snapshot mais recente.
  Todo consumidor futuro (013, relatório, GeN) DEVE receber ou selecionar explicitamente o
  snapshot usado. Nenhuma função de negócio do tipo "snapshot atual", "vigente" ou
  "último" é criada. Uma consulta administrativa PODE ordenar snapshots por momento da
  captura, mas ordem temporal não é autoridade institucional. (FR-061, FR-063, FR-064)
- Q: Ano e data de conclusão: congelar ambos? → A: **Congelar o que for atributo real do
  domínio, sem duplicar derivação.** Verificado no código e na 001: ano e data são
  **atributos persistidos independentes**. A fonte pode fornecer só o ano (001 FR-011,
  "ano, ou data completa"), e com data o ano é obrigatório e coerente (restrição da 001).
  O ano não é derivado da data. Logo, **ambos são congelados**, como registrados, sem
  reinterpretar nem corrigir valores. (FR-040 a FR-042)
- Q: A 012 tem interface? → A: **Não.** O núcleo expõe uma operação explícita de captura
  (nome concreto no plan) que valida a Campanha, calcula o universo, avalia a
  elegibilidade pela 004, congela o contexto, grava tudo atomicamente e devolve o
  snapshot criado. Sem endpoint HTTP, UI administrativa ou autenticação. Management
  command só se houver consumidor concreto (quickstart, demonstração ou operação técnica
  controlada); não é requisito funcional. (FR-100)
- Q: O momento da captura pode ser informado pelo chamador? → A: **Não.** O momento da
  captura é definido pela própria operação, no instante real da captura. O chamador NÃO
  DEVE poder informar data histórica arbitrária. Testes controlam o relógio pelo
  mecanismo de teste. (FR-016)
- Q: Qual a semântica da referência à Conclusão de origem? → A: Uma operação futura sobre
  o dado acadêmico de origem NÃO PODE destruir silenciosamente um snapshot histórico. A
  escolha concreta (e sua consequência para retenção, DP-1202) é registrada no plan, sem
  framework de retenção e sem copiar identificadores externos ou PII para evitar a
  referência. (FR-047, FR-048)

Precisões consolidadas na aprovação do plan:

- Q: A captura precisa ser feita "em uma única consulta"? → A: **Não.** O requisito é: a
  004 é a única fonte da elegibilidade; o universo é elegíveis ∪ Conclusões com
  Participação; cada Conclusão aparece no máximo uma vez. Consultas separadas, compostas
  na mesma operação, são aceitáveis. Sem UNION elaborado, SQL manual ou query builder;
  evitar só consulta por Conclusão e reimplementação dos critérios. (FR-020, FR-030)
- Q: A atomicidade inclui leitura isolada de todas as tabelas? → A: **Não.** Atomicidade
  é "o snapshot e todos os seus registros são gravados, ou nada é". O corte é o que a
  captura leu e copiou. Sem REPEATABLE READ, SERIALIZABLE, locks globais ou advisory
  locks. A escrita concorrente iniciada antes do encerramento é detectada pela
  verificação final e desfaz a captura inteira. `capturado_em` é o momento técnico da
  captura, não instante de leitura isolada. (FR-016, FR-052 a FR-054, FR-062)
- Q: A fronteira de leitura é a 013? → A: **Não.** Ela é mínima e semântica: contexto
  congelado, elegibilidade, estado da Participação e Respostas na semântica existente.
  Formato, colunas, serialização, escolha múltipla e nomes externos são da 013. (FR-070
  a FR-077)

## User Scenarios & Testing *(mandatory)*

Atores:

- **Instituição (CPAEG)**: destinatária institucional da capacidade (Interpretação B2).
  Nesta feature não há tela: a captura e a leitura são exercitadas por mecanismo técnico
  e por testes com dados fictícios.
- **Feature 013 (consumidora técnica futura)**: lê o dataset do snapshot para exportar.

Dados de referência usados nos cenários (todos fictícios):

- Unidades: **Serra**, **Vitória**, **Cefor**; algumas Conclusões **sem unidade**.
- Curso **"Técnico em Informática"** existe na Serra **e** em Vitória (homônimos).
- **Campanha E**: aberta, depois ENCERRADA, critério de unidades {Serra, Vitória}, com
  Conclusões elegíveis com e sem Participação; Participações concluídas normalmente, por
  Q1 = "Não" e em rascunho no encerramento.
- **Campanha V**: aberta e ENCERRADA, sem nenhuma Participação.
- **Campanha C**: EM COLETA.
- **Campanha P**: nunca aberta, EM PREPARAÇÃO.
- **Campanha X**: nunca aberta, com período já expirado (ENCERRADA pelo tempo).

### User Story 1 - Capturar snapshot de Campanha encerrada válida (Priority: P1)

A instituição captura um snapshot da Campanha E depois do encerramento. O snapshot nasce
completo, identifica a Campanha e o momento da captura, e não pode ser alterado.

**Why this priority**: é a capacidade central; sem ela nada é reprodutível.

**Independent Test**: capturar o snapshot da Campanha E e verificar que ele existe, aponta
para E, tem momento de captura e um registro por Conclusão do universo.

**Acceptance Scenarios**:

1. **Given** a Campanha E encerrada após abertura, **When** a captura é solicitada,
   **Then** um snapshot é criado com identificador, referência a E e momento da captura,
   e com todos os seus registros (caso A).
2. **Given** a Campanha V encerrada e sem Participações, **When** a captura é solicitada,
   **Then** o snapshot é criado; todos os registros são elegíveis e nenhum tem
   Participação (caso B).
3. **Given** uma Campanha encerrada cuja população no momento da captura é vazia e que
   não tem Participações, **When** a captura é solicitada, **Then** o snapshot é criado
   com zero registros, e isso é um resultado válido, não um erro.
4. **Given** um snapshot capturado, **When** qualquer tentativa de alterar sua
   população, elegibilidade, contexto congelado ou momento da captura é feita, **Then**
   não existe operação para isso e nada muda (FR-050).
5. **Given** uma falha qualquer durante a captura, **When** a captura termina, **Then**
   não existe snapshot algum dessa tentativa — nem cabeçalho, nem registros parciais
   (FR-052).

---

### User Story 2 - Recusar captura fora do momento permitido (Priority: P1)

Snapshot analítico final só existe para Campanha cuja coleta efetivamente ocorreu e
terminou.

**Why this priority**: evita fotografias de coleta em andamento (duplicando a 011) ou de
coleta que nunca houve.

**Independent Test**: solicitar captura para C, P e X e verificar recusa sem gravação.

**Acceptance Scenarios**:

1. **Given** a Campanha C EM COLETA, **When** a captura é solicitada, **Then** é recusada
   com motivo "a coleta ainda não terminou", e nada é gravado (caso L).
2. **Given** a Campanha P nunca aberta, **When** a captura é solicitada, **Then** é
   recusada com motivo "a Campanha nunca entrou em coleta", e nada é gravado (caso M).
3. **Given** a Campanha X, nunca aberta mas ENCERRADA pelo fim do período, **When** a
   captura é solicitada, **Then** é recusada com o mesmo motivo de M: data expirada não
   produz snapshot (caso M).
4. **Given** a Campanha E encerrada pelo fim do período, sem encerramento explícito,
   **When** a captura é solicitada depois do fim, **Then** é aceita.

---

### User Story 3 - Congelar a população elegível do momento (Priority: P1)

O snapshot registra, para cada Conclusão do universo, se ela era elegível no momento da
captura, segundo a regra da 004.

**Why this priority**: é o denominador histórico que a 011 não oferece (004/DP-408).

**Independent Test**: comparar os registros elegíveis com a população da 004 no momento da
captura; depois, incorporar novas Conclusões que satisfazem os critérios e verificar que
o snapshot não muda.

**Acceptance Scenarios**:

1. **Given** a Campanha E, **When** o snapshot é capturado, **Then** o número de
   registros elegíveis é exatamente o número de Conclusões da população elegível da 004
   naquele momento, e cada uma delas tem registro elegível (caso F inclui elegíveis sem
   Participação).
2. **Given** um snapshot de E, **When** uma nova Conclusão que satisfaz os critérios é
   incorporada depois da captura, **Then** a população atual da 004 e os elegíveis atuais
   da 011 aumentam, e o snapshot continua com o mesmo número de elegíveis.
3. **Given** a regra de elegibilidade da 004, **When** o snapshot é capturado, **Then**
   a elegibilidade de cada registro vem dessa regra, sem nenhum critério reimplementado
   (FR-020).

---

### User Story 4 - Congelar o contexto acadêmico para recortes históricos (Priority: P1)

Cada registro guarda o contexto acadêmico institucional da Conclusão no momento da
captura, com proveniência explícita.

**Why this priority**: sem isso, os recortes de uma Campanha encerrada mudam quando a
fonte acadêmica é corrigida.

**Independent Test**: capturar, alterar diretamente (simulando correção futura) unidade e
curso de uma Conclusão, e verificar que o registro mantém os valores originais.

**Acceptance Scenarios**:

1. **Given** uma Conclusão da Serra, curso "Técnico em Informática", nível Técnico,
   modalidade Presencial, forma de oferta Subsequente, conclusão em 2022, **When** o
   snapshot é capturado, **Then** o registro guarda exatamente esses valores, marcados
   como contexto institucional no momento da captura.
2. **Given** uma Conclusão sem unidade e sem forma de oferta informadas, **When** o
   snapshot é capturado, **Then** o registro guarda esses atributos como **não
   informados**, sem preenchimento, inferência ou correção (caso H).
3. **Given** duas Conclusões com curso "Técnico em Informática", uma na Serra e outra em
   Vitória, **When** o recorte por curso é reproduzido, **Then** elas aparecem em linhas
   distintas, identificadas por (unidade, curso) (caso I).
4. **Given** um registro, **When** ele é lido, **Then** nenhum nome, CPF, e-mail,
   matrícula, telefone ou identificador externo da Pessoa ou da Conclusão está presente.

---

### User Story 5 - Preservar Participações fora da população congelada (Priority: P1)

Uma Participação existente na Campanha nunca desaparece do snapshot, mesmo que sua
Conclusão não seja elegível no momento da captura.

**Why this priority**: eliminar o numerador para caber em 100% falsificaria a história.

**Independent Test**: com dados fictícios em que a Conclusão de uma Participação deixou de
satisfazer os critérios (simulando correção futura), capturar e verificar o registro.

**Acceptance Scenarios**:

1. **Given** uma Participação concluída de E cuja Conclusão, no momento da captura, não
   satisfaz mais os critérios, **When** o snapshot é capturado, **Then** existe um
   registro para essa Conclusão, marcado **não elegível no snapshot**, com seu contexto
   congelado e com a Participação combinável no dataset (caso G).
2. **Given** esse snapshot, **When** os indicadores são reproduzidos, **Then** a
   Participação conta em iniciadas e concluídas, não conta no denominador, e a taxa é
   apresentada como calculada, mesmo acima de 100%, sem truncamento.
3. **Given** uma Conclusão elegível com Participação, **When** o snapshot é capturado,
   **Then** existe um só registro para ela, elegível — nunca dois.

---

### User Story 6 - Ler um snapshot sem depender do estado acadêmico atual (Priority: P1)

Depois de criado, o snapshot é lido somente a partir dos valores congelados e dos dados
transacionais historicamente imutáveis.

**Why this priority**: é o que torna o resultado reprodutível.

**Independent Test**: capturar, alterar diretamente atributos das Conclusões e incorporar
Conclusões novas, e verificar que toda leitura do snapshot devolve exatamente o mesmo
resultado de antes.

**Acceptance Scenarios**:

1. **Given** um snapshot de E, **When** unidade, curso, nível, modalidade, forma de oferta
   e ano de Conclusões do universo são alterados depois da captura (caso J), **Then** a
   leitura do snapshot — registros, indicadores e recortes — é idêntica à leitura feita
   antes da alteração (caso K).
2. **Given** um snapshot, **When** recortes históricos são produzidos, **Then** nenhum
   atributo acadêmico é lido da Conclusão atual.

---

### User Story 7 - Dataset do snapshot com Participações e Respostas (Priority: P2)

A leitura do snapshot combina cada registro com a Participação e as Respostas
historicamente associadas, na Versão aplicada, sem copiá-las.

**Why this priority**: é a fronteira que a 013 consumirá.

**Independent Test**: para E, percorrer o dataset e conferir, registro a registro, a
Participação e as Respostas preservadas.

**Acceptance Scenarios**:

1. **Given** uma Participação concluída normalmente (caso C), **When** o dataset é lido,
   **Then** o registro traz o contexto congelado, a elegibilidade no snapshot, a
   Participação (início e conclusão registrados) e suas Respostas, cada uma ligada à
   Pergunta da Versão aplicada.
2. **Given** uma Participação concluída por Q1 = "Não" (caso D), **When** o dataset é
   lido, **Then** ela aparece como concluída, com a única Resposta registrada, sem
   categoria nova de "recusa" (006/DP-601).
3. **Given** uma Participação em rascunho no encerramento (caso E), **When** o dataset é
   lido, **Then** ela aparece como **não concluída**, com as Respostas preservadas, e o
   dataset permite distinguir as que estão fora do percurso, sem descartá-las e sem
   apresentá-las como de Participação concluída (Achado A1).
4. **Given** uma Conclusão elegível sem Participação (caso F), **When** o dataset é lido,
   **Then** o registro aparece sem Participação e sem Respostas.
5. **Given** a Pergunta Q14 respondida, **When** o dataset é lido, **Then** ela permanece
   Resposta declarada, separada do nível institucional congelado (ADR 0003).
6. **Given** uma Resposta de escolha múltipla, **When** o dataset é lido, **Then** ela
   vem como o conjunto de Opções da estrutura existente, sem serialização em texto ou em
   colunas.

---

### User Story 8 - Reproduzir os indicadores básicos (Priority: P2)

Dado um snapshot, recalcular elegíveis, iniciadas, concluídas, iniciadas e não concluídas
e as taxas, sobre o denominador histórico.

**Why this priority**: é a primeira análise que precisa sobreviver à deriva da fonte.

**Independent Test**: conferir os números contra contagem manual do conjunto de referência.

**Acceptance Scenarios**:

1. **Given** um snapshot de E, **When** os indicadores são reproduzidos, **Then**
   elegíveis do snapshot, iniciadas, concluídas, iniciadas e não concluídas, taxa de início
   e taxa de conclusão coincidem com a contagem manual.
2. **Given** um snapshot capturado sem nenhuma deriva entre o momento da captura e a
   consulta, **When** os indicadores do snapshot e os da 011 em escopo institucional são
   comparados, **Then** os números coincidem (só os rótulos diferem).
3. **Given** um snapshot com zero elegíveis, **When** as taxas são reproduzidas, **Then**
   elas são "não se aplica", nunca 0%, erro ou infinito.

---

### User Story 9 - Reproduzir os seis recortes da 011 com valores congelados (Priority: P2)

Unidade, curso (por unidade), nível, modalidade, forma de oferta e ano de conclusão,
reproduzidos a partir do contexto congelado.

**Why this priority**: recortes históricos são o caso concreto do congelamento.

**Independent Test**: comparar cada recorte com contagem manual, antes e depois de
alterações acadêmicas posteriores.

**Acceptance Scenarios**:

1. **Given** um snapshot de E, **When** cada um dos seis recortes é reproduzido, **Then**
   a soma das linhas é igual aos totais do snapshot e cada linha coincide com a contagem
   manual sobre os valores congelados.
2. **Given** registros com atributo não informado, **When** o recorte correspondente é
   reproduzido, **Then** eles formam a linha "não informado".
3. **Given** registros não elegíveis com Participação, **When** um recorte é reproduzido,
   **Then** eles contam nas Participações da sua linha e não no denominador da linha.

---

### User Story 10 - Distinguir elegibilidade congelada de elegibilidade atual (Priority: P2)

A linguagem do snapshot nunca confunde "elegíveis do snapshot" com "elegíveis atuais".

**Why this priority**: é o que permite, no futuro, dispensar o aviso de população atual
quando a análise se basear explicitamente num snapshot.

**Independent Test**: inspecionar os rótulos e as descrições das leituras do snapshot.

**Acceptance Scenarios**:

1. **Given** a leitura de um snapshot, **When** o denominador é descrito, **Then** ele é
   identificado como "elegíveis no snapshot de <momento da captura>", nunca como
   "elegíveis atuais", "população atual" ou "população da Campanha".
2. **Given** a 011, **When** o mesmo snapshot existe, **Then** a 011 continua mostrando
   elegíveis atuais e seu aviso de população atual, inalterada.

---

### User Story 11 - Vários snapshots imutáveis e independentes (Priority: P2)

Uma nova captura da mesma Campanha produz um novo snapshot, sem alterar nem substituir o
anterior.

**Why this priority**: é o que permite refletir uma correção acadêmica sem perder a
fotografia que sustentou uma análise anterior.

**Independent Test**: capturar S1, alterar dados acadêmicos, capturar S2 e comparar.

**Acceptance Scenarios**:

1. **Given** S1 de E, **When** um dado acadêmico é corrigido e uma nova captura é feita,
   **Then** existe S2 refletindo o novo estado e S1 permanece idêntico.
2. **Given** S1 e S2, **When** os snapshots de E são consultados, **Then** ambos aparecem,
   identificados pelo momento de captura, em ordem determinística, sem nenhum rótulo de
   oficial, vigente, aprovado, mais recente ou substituído.
3. **Given** duas solicitações de captura simultâneas para E, **When** ambas terminam,
   **Then** existem dois snapshots completos e independentes; nenhum fica parcial, nenhum
   mistura registros do outro (caso N).

---

### User Story 12 - Snapshot referencia a Versão publicada sem copiá-la (Priority: P2)

O snapshot alcança a Versão pela Campanha, e a estrutura da Versão continua sendo a da
002.

**Why this priority**: evita uma segunda cópia do instrumento.

**Independent Test**: verificar que o snapshot não contém Seção, Pergunta, Opção ou texto,
e que o dataset resolve cada Resposta pela Pergunta da Versão aplicada.

**Acceptance Scenarios**:

1. **Given** um snapshot de E, **When** a Versão aplicada é consultada, **Then** é a
   Versão PUBLICADA da Campanha, e sua estrutura vem da 002, inalterada (caso O).
2. **Given** dois snapshots de Campanhas com Versões diferentes, **When** são lidos,
   **Then** nenhuma correspondência entre Perguntas de Versões diferentes é oferecida
   (002/DP-006).

---

### User Story 13 - Metadados mínimos do snapshot (Priority: P3)

Para uma Campanha, listar os snapshots e, para cada um, momento da captura, número de
registros, elegíveis, Participações e Participações concluídas.

**Why this priority**: útil para a 013 escolher o snapshot; não há tela nesta feature.

**Independent Test**: consultar os metadados dos snapshots de E.

**Acceptance Scenarios**:

1. **Given** os snapshots de E, **When** os metadados são consultados, **Then** cada um
   traz identificador, Campanha, momento da captura e totais derivados dos registros.
2. **Given** os metadados, **When** são produzidos, **Then** nenhum dado individual é
   devolvido.

---

### Casos importantes

| Caso | Situação | Coberto por |
|------|----------|-------------|
| A | Campanha encerrada com população e Participações | US1.1, US7, US8 |
| B | Campanha encerrada sem Participações | US1.2 |
| C | Participação concluída normalmente | US7.1 |
| D | Participação concluída por Q1 = "Não" | US7.2 |
| E | Participação iniciada e não concluída no encerramento | US7.3 |
| F | Conclusão elegível sem Participação | US3.1, US7.4 |
| G | Participação cuja Conclusão não é elegível no snapshot | US5 |
| H | Conclusão com atributo ausente | US4.2, US9.2 |
| I | Cursos homônimos em unidades diferentes | US4.3 |
| J | Dados acadêmicos alterados depois da captura | US6.1, US11.1 |
| K | Consulta do snapshot depois da alteração | US6.1 |
| L | Captura de Campanha em coleta | US2.1 |
| M | Captura de Campanha nunca aberta (inclusive expirada) | US2.2, US2.3 |
| N | Duas solicitações simultâneas | US11.3 |
| O | Versão publicada referenciada e preservada | US12 |

### Edge Cases

- **Conclusão incorporada depois do encerramento e antes da captura**, que satisfaz os
  critérios: é **elegível no snapshot**, porque o snapshot congela a população no momento
  da captura, não no encerramento. A distância entre encerramento e captura fica
  visível, porque ambos os momentos são consultáveis (FR-063). Se o denominador oficial
  deve ser o do encerramento é **DP-1201**.
- **Participação sem nenhuma Resposta** (criada na entrada): é Participação iniciada e não
  concluída; aparece no dataset sem Respostas. Seu significado é **007/DP-703**.
- **Participação em rascunho com todas as Respostas fora do percurso**: aparece com as
  Respostas preservadas e distinguíveis (Achado A1).
- **Mesma Pessoa com duas Conclusões no universo**: dois registros, sem consolidação, sem
  marca de "mesma Pessoa" (FR-031; Const. I, XI).
- **Mesma Conclusão em snapshots de Campanhas diferentes**: registros independentes, um
  por snapshot.
- **Campanha com critério de unidades e Participação de Conclusão de outra unidade**: só
  possível após correção futura; vira registro não elegível (caso G).
- **Conclusão com data e ano**: ambos congelados juntos; nunca ano congelado com data
  atual (FR-042).
- **Campanha cuja Versão não está publicada**: impossível para Campanha aberta (004
  FR-036); se encontrada, a captura é recusada como inconsistência (FR-053).
- **Nome da Pesquisa alterado depois da captura**: o snapshot não muda; o nome não faz
  parte dele (Achado A2).
- **Captura solicitada repetidas vezes sem mudança de dados**: produz snapshots
  equivalentes e distintos; nenhum é deduplicado nem eleito (FR-061).
- **Volume**: a captura de uma Campanha com dezenas de milhares de Conclusões usa memória
  proporcional ao universo da Campanha, sem consulta por Conclusão; numa população ampla,
  o universo é a instituição (FR-110).

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII):

- **[PAEG Art. n]**: decorre da PAEG (Análise normativa, A).
- **[Interpretação Bn]**: interpretação operacional da categoria B.
- **[Const. — n]**: decorre da Constituição.
- **[00n]**: decorre de feature anterior.
- **[Arquitetura]**: decisão arquitetural.
- **[Hipótese]**: escolha de produto reversível.
- **[Escopo]**: delimitação desta feature.

Nenhum requisito é **[Herdado]** do formulário: o instrumento atual não tem dataset
analítico próprio.

### Functional Requirements

**Natureza da feature**

- **FR-001**: O snapshot analítico DEVE ser uma entidade própria, distinta da Campanha. A
  Campanha NÃO DEVE receber atributo, estado, contador ou marca relacionados a snapshot.
  [Const. — VII; Arquitetura]
- **FR-002**: A captura DEVE ser a única operação que grava nesta feature. Ela NÃO DEVE
  criar, alterar ou remover Campanha, Conclusão, Pessoa, Participação, Resposta, Versão,
  Pesquisa ou vínculo. [Const. — VIII; Escopo]
- **FR-003**: Toda leitura de snapshot DEVE ser somente leitura. [Escopo]
- **FR-004**: O snapshot NÃO DEVE ser apresentado como relatório oficial, indicador da
  PAEG (Art. 10, III) ou Relatório Anual (Art. 14). Ele é a base de dados congelada sobre
  a qual análises podem ser feitas. [Interpretação B4; Const. — XIX]

**Momento da captura**

- **FR-010**: A captura DEVE ser aceita somente para Campanha que, no momento da
  solicitação, está **ENCERRADA** segundo a 004 **e** tem momento de abertura registrado.
  [004 FR-034, FR-036, FR-040; Const. — XXIX]
- **FR-011**: Campanha EM COLETA DEVE ser recusada ("a coleta ainda não terminou"). A
  012 NÃO DEVE produzir snapshot parcial, provisório ou periódico durante a coleta: o
  acompanhamento atual é da 011. [Escopo; 011]
- **FR-012**: Campanha nunca aberta DEVE ser recusada ("a Campanha nunca entrou em
  coleta"), **inclusive** quando ENCERRADA pelo fim do período. Data expirada não
  equivale a coleta ocorrida. [004 FR-040]
- **FR-013**: Os estados e fatos usados DEVEM ser os da 004 (estado derivado, momento de
  abertura, forma e momento do encerramento). NÃO DEVE ser criado estado novo de
  Campanha, como "fechada para análise" ou "consolidada". [004; Const. — XXII]
- **FR-014**: A recusa DEVE informar o motivo e NÃO DEVE gravar nada. [Escopo]
- **FR-015**: A captura DEVE ser **explícita**. NÃO DEVE ser disparada automaticamente
  pelo encerramento, por agendamento, por consulta da 011 nem por leitura de snapshot.
  [Arquitetura; Const. — XXII]
- **FR-016**: O momento da captura DEVE ser definido pela operação de captura, no instante
  real em que ocorre, e DEVE ser o mesmo instante usado para verificar o estado da
  Campanha. O chamador NÃO DEVE poder informar o momento da captura.
  [Clarifications 2026-10-02; Const. — IV, VIII]

**Elegibilidade no snapshot**

- **FR-020**: A elegibilidade de cada registro DEVE ser obtida exclusivamente pelo
  contrato público de população elegível da 004 ("esta Conclusão pertence à população
  atual desta Campanha?"), avaliado no momento da captura. NENHUM critério de
  elegibilidade DEVE ser copiado, reescrito ou reinterpretado pela 012. [004 FR-025,
  FR-031; 011 FR-140]
- **FR-021**: O snapshot DEVE congelar o **resultado** dessa avaliação, como valor
  explícito por registro: **elegível no snapshot = sim | não**. Ausência de valor NÃO
  DEVE ser admitida. [Const. — IV]
- **FR-022**: O snapshot NÃO DEVE guardar o motivo da não elegibilidade nem as
  pendências por critério: não há consumidor nesta feature. [Const. — XXII]
- **FR-023**: A população elegível **da Campanha** continua dinâmica (004 FR-032). O
  snapshot NÃO DEVE ser usado pela 004, pela 005, pela 007 ou pela 011 para decidir
  elegibilidade, admissão de Participação ou indicadores operacionais. [004 FR-032; 011]

**Universo e grão**

- **FR-030**: O universo de um snapshot DEVE ser a **união** de:
  - (a) as Conclusões que pertencem à população elegível da Campanha no momento da
    captura (FR-020);
  - (b) as Conclusões que possuem Participação na Campanha.

  [Const. — I, VIII]
- **FR-031**: O grão DEVE ser a **Conclusão Acadêmica**: exatamente um registro por
  Conclusão do universo, em cada snapshot. Conclusões da mesma Pessoa NÃO DEVEM ser
  consolidadas, agrupadas nem marcadas como relacionadas. [Const. — I, XI; 004 FR-033]
- **FR-032**: Toda Conclusão com Participação na Campanha DEVE ter registro, seja qual for
  sua elegibilidade no snapshot. Participação NÃO DEVE ser excluída para manter taxa
  ≤ 100%. [Const. — VIII; 011 FR-038]
- **FR-033**: Para uma Conclusão em (b) e fora de (a), o registro DEVE ser **não elegível
  no snapshot**, com contexto congelado, e DEVE permanecer combinável com sua
  Participação (FR-071). [005/DP-507]
- **FR-034**: Para um snapshot, DEVE valer: número de registros elegíveis = tamanho da
  população elegível da Campanha no momento da captura = **denominador histórico do
  snapshot**. Os registros com Participação PODEM ser elegíveis ou não elegíveis; os
  registros sem Participação são sempre elegíveis. [Const. — XIX]

**Contexto acadêmico congelado**

- **FR-040**: Cada registro DEVE congelar, com os valores do momento da captura, os
  atributos de contexto acadêmico da Conclusão definidos pela 001: **unidade, curso,
  nível, modalidade, forma de oferta, ano de conclusão e data de conclusão**. Nenhum
  outro atributo acadêmico DEVE ser congelado, e NENHUM atributo novo DEVE ser criado na
  Conclusão. [001 FR-009; Arquitetura]
- **FR-041**: A justificativa do conjunto DEVE permanecer registrada: os seis primeiros
  sustentam os seis recortes da 011 (FR-085); a data de conclusão integra, com o ano, a
  mesma referência temporal da 001 e é listada pela Constituição entre o contexto de
  exportações (Qualidade das Exportações), consumidas pela 013. [001 FR-011; Const. —
  XVIII]
- **FR-042**: Ano e data de conclusão são atributos independentes da 001 (a fonte pode
  fornecer só o ano; com data, o ano é coerente) e DEVEM ser congelados juntos, como
  registrados, sem derivar um do outro, reinterpretar ou corrigir valores. Nenhuma leitura de snapshot DEVE combinar valor congelado com valor
  atual da mesma Conclusão. [001 FR-011; Const. — VIII]
- **FR-043**: Atributo ausente DEVE ser congelado como **ausente** ("não informado"). A
  captura NÃO DEVE preencher, inferir, normalizar, corrigir grafia nem consultar a fonte
  acadêmica. [001 FR-010; 004 FR-028; Const. — III]
- **FR-044**: Os valores congelados DEVEM ser identificados como **contexto
  institucional da Conclusão Acadêmica no momento da captura**: categoria
  **institucional** (Const. III, A), nunca declarada nem derivada. [Const. — III, IV]
- **FR-045**: Curso DEVE ser interpretável junto com a unidade congelada do mesmo
  registro, para que cursos homônimos de unidades diferentes não se confundam. NÃO DEVE
  ser criada entidade, catálogo, código ou identidade de Curso. [011 FR-050, FR-051;
  010/DP-1005]
- **FR-046**: A fonte e o identificador externo da Conclusão, o nome e os identificadores
  da Pessoa, e o momento de incorporação NÃO DEVEM ser copiados para o registro. A
  proveniência da fonte continua alcançável pela referência interna à Conclusão
  (FR-047), sem cópia. [Const. — IV, XVI]
- **FR-047**: Cada registro DEVE manter **referência técnica interna** à Conclusão de
  origem, para rastreabilidade e para combinação com Participação. Essa referência NÃO
  DEVE ser tratada como identificador analítico exportável; a exposição de qualquer
  identificador é decisão da 013, sob 005/DP-505. [Const. — IV, XVI; Escopo]
- **FR-048**: Nenhuma operação sobre a Conclusão de origem DEVE poder remover ou alterar
  silenciosamente um snapshot ou seus registros. Hoje não há exclusão de Conclusão (001);
  se vier a existir, ela DEVE ser impedida enquanto houver registro que a referencie, até
  decisão explícita de retenção (DP-1202). [Clarifications 2026-10-02; Const. — VIII]

**Imutabilidade, integridade e validação**

- **FR-050**: Um snapshot criado DEVE ser imutável. NÃO DEVE existir operação para
  editar, corrigir, recalcular, completar, renomear, mover ou remover snapshot ou
  registro, nem para alterar população, elegibilidade, contexto congelado ou momento da
  captura. [Const. — VIII; Escopo]
- **FR-051**: Uma nova fotografia NÃO DEVE sobrescrever, substituir nem invalidar
  snapshot anterior (FR-060). [Const. — VIII]
- **FR-052**: A captura DEVE ser **atômica**: ou o snapshot existe completo, com todos os
  registros do universo, ou nada dela existe. NÃO DEVE existir estado "em andamento",
  "parcial", "pendente" ou "inválido", nem snapshot observável antes de completo.
  [Arquitetura; Const. — XXII]
- **FR-053**: Antes de concluir, a captura DEVE verificar, e recusar sem gravar nada em
  caso de falha:
  - (a) Campanha válida para captura (FR-010);
  - (b) Versão da Campanha PUBLICADA;
  - (c) exatamente um registro por Conclusão do universo;
  - (d) toda Conclusão com Participação na Campanha tem registro;
  - (e) elegibilidade explícita em todo registro;
  - (f) número de registros elegíveis = número de Conclusões da população elegível lida
    pela captura (FR-034).

  Falha em (b) a (f) é inconsistência, não decisão de domínio, e NÃO DEVE gerar estado
  de validação. [Arquitetura]
- **FR-054**: O corte histórico de um snapshot DEVE ser definido pelos valores
  efetivamente lidos e copiados pela operação de captura. A captura NÃO DEVE prometer
  leitura isolada e simultânea de todas as tabelas, nem introduzir nível de isolamento
  mais forte, lock global ou advisory lock sem cenário concreto. Como a Campanha já está
  encerrada, novas escritas de Participação e Resposta já são bloqueadas pela 004/005/006;
  o caso estreito de escrita concorrente iniciada antes do encerramento DEVE ser detectado
  pela verificação final (FR-053 d) e fazer toda a captura falhar, sem resto, podendo ser
  repetida. [Arquitetura; Clarifications 2026-10-02]

**Vários snapshots**

- **FR-060**: PODEM existir vários snapshots da mesma Campanha. Cada um DEVE ser
  independente, imutável e identificado por identificador próprio e momento da captura.
  [Hipótese; Const. — VIII]
- **FR-061**: NÃO DEVE existir status, marca ou conceito de snapshot oficial, aprovado,
  vigente, mais recente, válido ou substituído, nem deduplicação de capturas
  equivalentes, nem workflow em torno disso. Qual snapshot sustenta uma publicação é
  **DP-1201**. Enquanto DP-1201 estiver aberta, NÃO DEVE existir regra, consulta ou
  função de negócio que escolha implicitamente um snapshot ("atual", "vigente", "último",
  "mais recente"). [Const. — X, XXIX; Clarifications 2026-10-02]
- **FR-062**: Duas capturas simultâneas da mesma Campanha DEVEM produzir dois snapshots
  completos e independentes (FR-052), sem interferência mútua e sem lock para
  deduplicá-los. A solução DEVE ser proporcional, sem lock distribuído, fila ou worker.
  [Arquitetura]
- **FR-063**: A consulta dos snapshots de uma Campanha DEVE devolver todos, em ordem
  determinística pelo momento da captura, sem significado de preferência. O momento do
  encerramento da Campanha (004) DEVE continuar consultável junto, para que a distância
  entre encerramento e captura seja visível. [004 FR-040; Escopo]
- **FR-064**: Toda leitura de snapshot (dataset, indicadores, recortes, metadados de um
  snapshot) DEVE receber explicitamente o snapshot a ler. A ordem temporal da consulta de
  FR-063 é administrativa e NÃO DEVE ser usada como critério de autoridade.
  [Clarifications 2026-10-02; DP-1201]

**Dataset do snapshot (fronteira de leitura)**

- **FR-070**: DEVE existir uma leitura do snapshot que produza, para cada registro: o
  contexto acadêmico congelado; a elegibilidade no snapshot; a Participação da Conclusão
  na Campanha, se existir; e as Respostas dessa Participação. Essa leitura PODE ser
  consulta, iterador ou objeto de leitura; NÃO precisa ser tabela. Ela é **mínima**:
  existe para provar que o snapshot se combina com os fatos históricos preservados, e
  NÃO DEVE definir schema tabular, definição de colunas, serializador, achatamento, nomes
  externos, representação CSV ou adaptação ao GeN, que são da 013. [Arquitetura;
  Clarifications 2026-10-02]
- **FR-071**: Participação, início e conclusão registrados e Respostas DEVEM ser lidos
  dos dados transacionais existentes (005, 006), **não copiados** para o snapshot. Eles
  são historicamente imutáveis depois do encerramento (Verificação V5 a V7).
  [Const. — XXII; 005; 006]
- **FR-072**: Campanha, Versão e estrutura do instrumento DEVEM ser alcançados pela
  referência do snapshot à Campanha. Seções, Perguntas, Opções e textos NÃO DEVEM ser
  copiados. Cada Resposta DEVE ser associada à Pergunta da Versão efetivamente aplicada
  pela Campanha. [Const. — VII, VIII; 002]
- **FR-073**: O dataset DEVE preservar a separação das três categorias de dado: contexto
  acadêmico congelado (**institucional**), Respostas (**declarado**), e elegibilidade no
  snapshot, indicadores e situação da Participação (**derivado** ou fato do domínio). Uma
  Resposta NÃO DEVE ser substituída, completada ou validada pelo contexto congelado, nem o
  contexto pela Resposta; Q14 continua declarada. [Const. — III; ADR 0003; 005/DP-508]
- **FR-074**: As Respostas DEVEM ser entregues na estrutura semântica existente (valor do
  tipo da Pergunta, Opção, conjunto de Opções, texto, escala, complemento). O dataset NÃO
  DEVE achatar Perguntas em colunas, criar códigos de coluna (Q01, Q02…), serializar
  escolha múltipla nem definir esquema tabular de exportação ou do GeN. [Escopo; 013]
- **FR-075**: O dataset DEVE informar, por Participação, se ela foi **concluída** ou **não
  concluída** (rascunho no encerramento). Para Participação não concluída, DEVE permitir
  distinguir as Respostas fora do percurso final, pelas regras existentes da 006, sem
  descartá-las e sem apresentá-las como de Participação concluída. NÃO DEVE criar
  categoria de "abandono", "desistência" ou "recusa". [Achado A1; 005/DP-503;
  006/DP-601; 007/DP-703]
- **FR-076**: O dataset NÃO DEVE ler a Conclusão atual para contexto acadêmico, nem a
  Pessoa, e NÃO DEVE entregar objeto a partir do qual se alcance, por navegação, a
  Conclusão, a Pessoa ou a Participação transacional (por exemplo, instância de Resposta,
  de Participação ou de registro). É a aplicação ao dataset da regra geral de FR-080.
  [Const. — XVI; FR-080]
- **FR-077**: Dentro de um snapshot, a comparação de Respostas fica limitada à Versão da
  Campanha. NÃO DEVE ser criado identificador global de pergunta, pergunta canônica,
  linhagem ou equivalência semântica entre Versões. [002/DP-006]

**Reprodução**

- **FR-080**: Depois da captura, toda reprodução histórica (indicadores, recortes e, pela
  FR-076, o dataset) DEVE usar somente os valores congelados do snapshot e os dados
  transacionais historicamente imutáveis. Nenhum atributo acadêmico DEVE ser lido da
  Conclusão atual, e a população atual da 004 NÃO DEVE ser consultada. [Const. — VIII]
- **FR-081**: Dado um snapshot, DEVEM ser reproduzíveis: **elegíveis do snapshot**;
  **iniciadas** (registros com Participação); **concluídas** (registros com Participação
  concluída); **iniciadas e não concluídas**; e cada uma das três últimas separada em
  elegíveis e não elegíveis no snapshot. [Const. — XIX; 011 FR-030 a FR-034]
- **FR-082**: As definições de iniciadas e concluídas DEVEM ser as mesmas da 011
  (Participação existente; conclusão registrada, inclusive por recusa), como tratamento
  provisório das mesmas DPs (007/DP-703; 006/DP-601). [011 FR-032, FR-033]
- **FR-083**: **Taxa de início** e **taxa de conclusão** do snapshot DEVEM ser iniciadas ÷
  elegíveis do snapshot e concluídas ÷ elegíveis do snapshot, com todas as Participações
  no numerador, inclusive as não elegíveis. A taxa PODE passar de 100% e DEVE ser
  apresentada como calculada, sem truncamento. Com denominador zero, DEVE ser "não se
  aplica". [011 FR-035, FR-036, FR-038]
- **FR-084**: Toda contagem DEVE ser de Conclusões ou de Participações, nunca de Pessoas.
  [Const. — I, XI]
- **FR-085**: DEVEM ser reproduzíveis os seis recortes de uma dimensão da 011 — unidade,
  curso (chave unidade + curso), nível, modalidade, forma de oferta e ano de conclusão —
  sobre os valores congelados, com linha "não informado" para ausência, e com a soma das
  linhas igual aos totais do snapshot. NÃO DEVE ser criada dimensão genérica nem
  combinação livre de recortes. [011 FR-050 a FR-059]
- **FR-086**: A reprodução DEVE ser determinística: a mesma leitura do mesmo snapshot
  devolve sempre o mesmo resultado, qualquer que seja o estado posterior da fonte
  acadêmica. [Const. — VIII]
- **FR-087**: Imediatamente após a captura, sem deriva entre a captura e a consulta, os
  totais e os seis recortes reproduzidos DEVEM coincidir com os números da 011 em escopo
  institucional. [011]

**Linguagem e relação com a 011**

- **FR-090**: Toda leitura de snapshot que descreva o denominador DEVE usar "elegíveis no
  snapshot" (ou "elegíveis do snapshot de <momento da captura>"), e NÃO DEVE usar
  "elegíveis atuais", "população atual", "população da Campanha" ou "denominador
  oficial". [004 FR-031; 011 FR-031]
- **FR-091**: Uma análise baseada explicitamente num snapshot PODE dispensar o aviso de
  população atual da 011, desde que identifique o snapshot e seu momento de captura. A
  012 NÃO DEVE alterar a 011: suas consultas, rótulos e avisos permanecem como estão.
  [011 FR-046; Escopo]

**Governança e autorização**

- **FR-100**: Nesta feature, a captura e a leitura do snapshot DEVEM ser capacidades de
  domínio **não expostas** a operadores: sem tela, rota, API ou ação na interface. Elas
  são exercitadas por testes e, só se houver consumidor concreto, por mecanismo técnico
  administrativo explícito, como as operações de Campanha da 004 (004/DP-402). NÃO DEVE
  ser criado endpoint HTTP, UI administrativa ou autenticação apenas para que exista uma
  forma de disparo. [Escopo; 010/DP-1001; Clarifications 2026-10-02]
- **FR-101**: Nenhuma regra nova de autorização, papel, permissão, gestor de snapshot,
  aprovação ou workflow DEVE ser criada nesta feature. [Const. — X, XXII]
- **FR-102**: Quando uma feature futura expuser a captura a operadores, ela DEVE ser
  restrita à atuação **CPAEG** ativa. [Interpretação B1, B2; PAEG Art. 21, I, V]
- **FR-103**: A atuação CSAEG NÃO DEVE receber, por esta feature, capacidade de captura
  nem acesso a registros individuais do snapshot. Eventual acesso a **agregados** de
  snapshot por unidade (PAEG Art. 22, V) DEVE ser decidido pela feature que o expuser,
  com 005/DP-505 e 011/DP-1101. [Interpretação B3]
- **FR-104**: O snapshot NÃO DEVE registrar quem solicitou a captura: não há operador
  identificado em ambiente produtivo (010/DP-1001) nem consumidor institucional dessa
  informação. A rastreabilidade básica é dada por identificador, Campanha e momento da
  captura. NÃO DEVE ser criado log de auditoria genérico. [Const. — IV, XXII]

**Volume e proporcionalidade**

- **FR-110**: A captura DEVE operar de forma proporcional ao **universo da Campanha**:
  sem consulta nem gravação por Conclusão, e sem ler Conclusões fora do universo. A
  memória usada é proporcional a esse universo. Numa Campanha sem critérios (população
  ampla), o universo pode ser toda a instituição, e carregá-lo é aceito no volume previsto
  (Assumptions). Leitura ou gravação em blocos só se justifica com evidência de volume
  real. [Arquitetura; Clarifications 2026-10-02]
- **FR-111**: NÃO DEVEM ser introduzidos worker, fila, job, agendador, Redis, Celery,
  framework de streaming, materialized view, cache ou tabela de agregação. A persistência
  existe por reprodutibilidade, não por desempenho. [Const. — XXII]
- **FR-112**: A reprodução de indicadores e recortes DEVE ser feita por agregação sobre os
  registros, sem consulta por linha de recorte e sem ler Respostas. [011 FR-072;
  Arquitetura]

**Privacidade**

- **FR-120**: Nenhuma PII DEVE ser copiada para o snapshot: nome, CPF, e-mail, matrícula,
  telefone, identificador externo de Pessoa ou de Conclusão. [Const. — XVI]
- **FR-121**: Nenhuma Resposta, inclusive as potencialmente sensíveis (Q2, Q4, Q5, Q6),
  DEVE ser copiada: o dataset as referencia. [Const. — XVI; 005/DP-504]
- **FR-122**: NÃO DEVEM ser criados hash de CPF, pseudônimo exportável, mapa de
  identidade nem identificador analítico externo. A correlação entre Conclusões da mesma
  Pessoa, se necessária, é decisão consciente de feature futura. [Const. — XVI, XXII;
  001/DP-003]
- **FR-123**: A captura interna NÃO DEVE suprimir registros por grupos pequenos; a
  supressão para visualização, publicação, exportação ou GeN continua em **011/DP-1101**,
  sem limiar inventado. [011/DP-1101]
- **FR-124**: Mensagens de recusa, de erro e de diagnóstico DEVEM citar só motivos,
  identificadores técnicos de Campanha e de snapshot e contagens, nunca valores
  acadêmicos de uma Conclusão nem conteúdo de Resposta. [Const. — XVI; Observabilidade]
- **FR-125**: Enquanto 001/DP-009 e 005/DP-504 estiverem abertas, snapshots DEVEM ser
  produzidos somente com dados fictícios. [001/DP-009; 005/DP-504]

**Demonstração e testes**

- **FR-130**: A feature DEVE ser exercitável com dados fictícios por verificação
  automatizada, com o menor conjunto suficiente para os casos A a O. [Const. — XXV, XXVI]
- **FR-131**: O cenário de demonstração existente NÃO DEVE ser alterado: ele não cria
  Participação nem Resposta e não tem Campanha encerrada com coleta. Nenhuma Campanha,
  Pessoa ou Conclusão fictícia permanente DEVE ser acrescentada só para alimentar o
  snapshot. [Escopo; 011 FR-142]
- **FR-132**: Os casos que dependem de correção acadêmica futura (G, J, K) DEVEM ser
  verificados alterando os dados fictícios diretamente no teste, como simulação de
  001/DP-005. NENHUMA operação de correção acadêmica DEVE ser criada. [Achado A5]

### Key Entities *(include if feature involves data)*

**Novas** (duas; nenhuma terceira):

- **Snapshot analítico**: fotografia imutável de uma Campanha. Atributos: identificador;
  Campanha de origem; momento da captura. Nada mais: Versão, critérios, período, estado e
  encerramento são alcançados pela Campanha; totais são derivados dos registros.
- **Registro do snapshot**: uma Conclusão Acadêmica no universo de um snapshot.
  Atributos: snapshot; referência técnica interna à Conclusão de origem; elegível no
  snapshot (sim | não); unidade, curso, nível, modalidade, forma de oferta, ano de
  conclusão e data de conclusão congelados, cada um possivelmente não informado. Único
  por (snapshot, Conclusão).

**Existentes, somente lidas**:

- **Campanha** (004): condição de captura; Versão; momento do encerramento.
- **Conclusão Acadêmica** (001): somente **na captura**, para o contexto acadêmico;
  depois, apenas como alvo da referência técnica.
- **Participação** (005, 006): existência, início e conclusão registrados.
- **Resposta** (005): somente no dataset, nunca copiada.
- **Versão, Seção, Pergunta, Opção** (002): somente para interpretar Respostas.

**Não lidas**: Pessoa, vínculos de governança.

**Explicitamente não criados**: cópia de Resposta, de Opção selecionada, de Pergunta, de
Seção ou de Versão; fato, dimensão, cubo, data mart; modelo de status, aprovação, job,
lote, log de auditoria ou validação.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| Unidade, curso, nível, modalidade, forma de oferta, ano e data de conclusão congelados | **Institucional**, no momento da captura | Conclusão Acadêmica (001), lida uma vez na captura | Congelados como estavam; correção posterior não altera o snapshot (001/DP-005); divergência com Resposta não tratada (005/DP-508) |
| Elegível no snapshot | **Derivado**, congelado | Avaliação da 004 no momento da captura | Não recalculado; nova captura reflete novo estado |
| Momento da captura | Derivado (fato técnico do domínio) | Instante da captura | Imutável |
| Participação, início e conclusão registrados | Fato do domínio | 005, 006, referenciados | Imutáveis depois do encerramento |
| Respostas | **Declarado** | 005, referenciadas, na Versão aplicada | Imutáveis depois do encerramento; não comparadas com o contexto |
| Respostas fora do percurso (rascunho) | Derivado (classificação) | Regras puras da 006 sobre Versão e Respostas | Recalculável a qualquer tempo com o mesmo resultado |
| Indicadores, taxas, recortes do snapshot | Derivado | FR-081 a FR-085 sobre os registros | Não persistidos |
| Versão e estrutura | Configuração institucional | 002, pela Campanha | Imutáveis |

### Análise de persistência

- **Por que persistir**: o pertencimento à população (V11) já muda hoje (Achado A4) e o
  contexto acadêmico (V10) está anunciado como mutável (Achado A3). Sem persistência,
  não há reprodução.
- **O que se persiste**: duas entidades (Key Entities): cabeçalho mínimo e um registro por
  Conclusão do universo, com elegibilidade e sete atributos.
- **O que não se persiste e por quê**: Campanha, Versão e instrumento (V1 a V4);
  Participação e Respostas (V5 a V8); nome da Pesquisa (A2); Pessoa e identificadores
  (privacidade); totais (deriváveis dos registros); motivos de inelegibilidade (sem
  consumidor).
- **Migrations**: aditivas, sem alterar tabelas existentes. [Const. — XXVII]
- **Sem**: materialized view, cache, tabela de agregação, banco analítico separado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Os 15 casos importantes (A a O) são demonstrados por verificação
  automatizada com dados fictícios, com 100% dos resultados conforme a spec.
- **SC-002**: Em 100% dos snapshots do conjunto de referência, o número de registros
  elegíveis é igual ao tamanho da população elegível da 004 no momento da captura, e
  toda Conclusão com Participação na Campanha tem exatamente um registro.
- **SC-003**: Depois de alterar unidade, curso, nível, modalidade, forma de oferta e ano
  de 100% das Conclusões do universo e de incorporar Conclusões novas elegíveis, 100% das
  leituras do snapshot (registros, indicadores e seis recortes) são idênticas às feitas
  antes das alterações.
- **SC-004**: Imediatamente após a captura, sem deriva, os totais e as linhas dos seis
  recortes do snapshot coincidem 100% com os da 011 em escopo institucional.
- **SC-005**: Em 100% das tentativas de captura de Campanha em coleta, em preparação ou
  nunca aberta, nada é gravado e o motivo é informado.
- **SC-006**: Em 100% das capturas interrompidas por falha simulada, não resta nenhum
  snapshot nem registro da tentativa.
- **SC-007**: Duas capturas simultâneas da mesma Campanha resultam sempre em dois
  snapshots completos e independentes.
- **SC-008**: Nenhum snapshot ou registro contém nome, CPF, e-mail, matrícula, telefone,
  identificador externo, Resposta, Pergunta, Opção ou texto do instrumento, verificado
  sobre o conjunto de referência.
- **SC-009**: Depois da feature, existem exatamente duas entidades novas; nenhuma tabela,
  coluna ou migration altera entidades das Features 001 a 011; nenhuma página, rota ou
  regra de autorização nova existe.
- **SC-010**: A reprodução de indicadores e recortes de um snapshot não lê nenhuma
  Resposta, nenhuma Conclusão atual e nenhuma Pessoa, verificado automaticamente.
- **SC-011**: Uma pessoa que leia a spec e a documentação da leitura responde, sem
  ambiguidade, "qual era o denominador desta análise e em que momento foi fixado", a
  partir do identificador do snapshot.
- **SC-012**: A 011 continua com 100% dos seus testes de aceitação passando, sem
  alteração.

## Assumptions

Apenas suposições não institucionais. As regras institucionais em aberto estão em
"Decisões Pendentes".

- O único escritor legítimo da base é o Trajetória Ifes, pelas operações de domínio (ADR
  0002). As imutabilidades V1 a V7 valem nesse regime; escrita direta no banco fora das
  operações não é protegida, como nas features anteriores.
- Volume: dezenas de Campanhas, até dezenas de milhares de Conclusões por Campanha,
  capturas raras (uma ou poucas por Campanha encerrada).
- O contrato de população da 004 (população no momento) é aplicável a todas as Conclusões
  de uma vez e é o mesmo usado pela 011.
- Momento da captura com precisão de instante, na timezone configurada, é suficiente para
  ordenar administrativamente os snapshots (FR-063); a identidade é o identificador.
  [Hipótese]
- A 013 será a consumidora da fronteira de leitura; a forma concreta dessa fronteira
  pertence ao plan.

## Relação com outras features

- **001** — consumida sem alteração. Atributos de contexto lidos uma vez, na captura.
  001/DP-005 (correção) e DP-006 (sincronização) continuam abertas e são a razão do
  congelamento do contexto.
- **002/003** — Versão referenciada pela Campanha; nada copiado. 002/DP-006 mantida.
- **004** — contrato de população consumido sem alteração; estado e fatos de abertura e
  encerramento usados como condição. FR-032 da 004 continua valendo: a população da
  Campanha não é congelada; o snapshot é artefato separado. **DP-408 parcialmente
  resolvida** (ver Decisões Pendentes).
- **005/006** — Participação e Respostas referenciadas, imutáveis depois do encerramento.
  Nenhuma operação nova.
- **007** — sem efeito; 007/DP-703 mantida com o mesmo tratamento provisório da 011.
- **008/009** — sem efeito; nenhuma interface.
- **010** — nenhuma regra nova. A interpretação de que a captura é institucional (CPAEG)
  fica registrada para a feature que a expuser.
- **011** — **inalterada e independente**. Continua respondendo "como está a coleta
  agora?", com elegíveis atuais e aviso. A 012 responde "o que sustentava esta análise
  naquele momento?".
- **013 (prevista — exportações e GeN)** — consumirá a fronteira de leitura (FR-070 a
  FR-077) e decidirá: achatamento de Respostas, serialização de escolha múltipla,
  identificadores expostos, supressão de pequenos grupos, rótulos e arquivos.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade (NON-NEGOTIABLE)**: grão Conclusão (FR-031); snapshot por
  Campanha; Participações de Campanhas diferentes nunca fundidas; Conclusões da mesma
  Pessoa nunca consolidadas.
- **II — Definição de egresso (NON-NEGOTIABLE)**: elegibilidade só pela 004, sobre
  Conclusões reconhecidas (FR-020).
- **III — Dado institucional não é declarado (NON-NEGOTIABLE)**: contexto congelado
  marcado institucional (FR-044); separação das três categorias no dataset (FR-073).
- **IV — Proveniência**: contexto identificado como "institucional, no momento da
  captura"; referência à Conclusão de origem (FR-047); elegibilidade derivada e
  congelada explícita (FR-021).
- **VII — Conceitos distintos (NON-NEGOTIABLE)**: snapshot distinto de Campanha (FR-001);
  Resposta associada à Participação e à Versão aplicada (FR-072).
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: snapshot imutável (FR-050), sem
  sobrescrita (FR-051), reprodução determinística (FR-086); nada existente é alterado
  (FR-002).
- **XI — Pessoa única, contexto múltiplo**: contexto da Conclusão, nunca da Pessoa.
- **XII — Base central; escopos por unidade**: capacidade institucional; nada exposto à
  CSAEG (FR-103).
- **XVI — Privacidade (NON-NEGOTIABLE)**: minimização desde a origem (FR-120 a FR-125);
  nenhuma cópia de Resposta ou PII; DPs de base legal e retenção mantidas.
- **XVIII — Exportabilidade**: fronteira de leitura estável para a 013, preservando as
  categorias de dado (FR-070 a FR-077), sem antecipar formato.
- **XIX — Acompanha a coleta, não é BI**: o snapshot não é BI, painel nem indicador da
  PAEG (FR-004); reproduz só os indicadores operacionais já definidos.
- **XXII — YAGNI**: duas entidades; sem UI; sem regra nova; sem warehouse, ETL, job ou
  cache (FR-101, FR-111).
- **XXVII — Migrações**: aditivas, sem reinterpretar dados existentes.
- **XXIX — Hipóteses não viram requisitos (NON-NEGOTIABLE)**: múltiplos snapshots sem
  oficial (DP-1201); retenção (DP-1202); "iniciada" e "recusa" com tratamento provisório
  declarado.

**Tensões identificadas (não são conflitos)**:

- **004 FR-032 × snapshot**: a 004 proíbe materializar lista de elegíveis **na
  Campanha** e congelar a população na abertura. O snapshot não muda a população da
  Campanha, não é lista de destinatários e não é usado por nenhuma regra transacional
  (FR-023); é o artefato que a própria 004 deixou para DP-408.
- **XVI × universo com elegíveis sem Participação**: o snapshot guarda contexto de
  Conclusões que não participaram, o que a 011 nunca expõe individualmente. Tratamento:
  nada exposto; sem PII; referência só interna; retenção em DP-1202.
- **XXII × data de conclusão**: a data não tem recorte na 011. Ela entra porque integra a
  mesma referência temporal do ano (FR-042) e o contexto de exportação da Constituição;
  congelar só o ano exporia a mistura de valor congelado e atual que FR-080 proíbe.
- **VIII × Respostas em rascunho fora do percurso**: preservadas como estão, sem limpeza
  retroativa (Achado A1).

Nenhum conflito com a Constituição, com a PAEG ou com as Features 001 a 011 foi
identificado.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence de fato ao domínio de acompanhamento?** Sim: "estruturação dos dados
   coletados", "proveniência", "histórico longitudinal" e "disponibilização de dados
   necessários à produção de indicadores" estão na Fronteira do Domínio.
2. **É necessária ao ciclo de acompanhamento?** Sim: sem fotografia estável, nenhuma
   análise de uma Campanha encerrada é reprodutível (PAEG Art. 10, III).
3. **Existe solução institucional mais adequada?** Para análise estatística e BI, sim
   (GeN/Looker, a jusante), e por isso ficam fora. Para fixar o que o NIAE sabia sobre a
   própria Campanha, não.
4. **Integração seria suficiente?** Não: a fonte externa não conhece Participações nem
   elegibilidade da Campanha.
5. **Aumenta o acoplamento do núcleo?** Não: duas entidades a jusante; nenhum conceito
   existente depende delas.

## Out of Scope *(mandatory)*

- Exportação CSV, XLSX, ZIP, download, API pública ou analítica (Feature 013).
- GeN, Looker Studio, BI, dashboard, gráficos.
- Data warehouse, fato, dimensão, star schema, snowflake, cubo, data mart, banco
  analítico separado.
- ETL, pipeline, extractor, transformer, loader, DAG, agendador, framework genérico de
  snapshot, tabelas de histórico genéricas, event sourcing, banco temporal.
- Materialized view, cache, tabela de agregação, jobs, filas, Redis, Celery, workers.
- Snapshot durante a coleta, periódico ou automático no encerramento.
- Snapshot oficial, aprovado, vigente ou substituído; workflow de aprovação.
- Edição, correção, remoção ou reprocessamento de snapshot.
- Cópia de Respostas, de Opções selecionadas, de Perguntas, de Seções ou de Versões.
- Achatamento de Respostas em colunas; serialização de escolha múltipla; esquema GeN.
- Identidade global de pergunta, linhagem, equivalência semântica entre Versões.
- Hash de CPF, pseudônimo, mapa de identidade, identificador analítico externo.
- Navegador de registros, drill-down nominal, lista de egressos.
- Interface, rota, tela ou regra de autorização nova.
- Registro de quem solicitou a captura; log de auditoria genérico.
- Comunicação, e-mail, pixel, clique, segmentação, mailing.
- Correção de dado acadêmico; catálogo de cursos ou de unidades; identidade real.
- Supressão de pequenos grupos; definição de coorte.
- Qualquer alteração das Features 001 a 011, incluindo o cenário de demonstração.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: decisões novas usam o prefixo 12 (DP-1201…). As das features anteriores são
citadas como 00n/DP-nnn.

**Novas nesta feature**

- **DP-1201** — DECISÃO PENDENTE: **qual fotografia sustenta uma publicação
  institucional** (Relatório Anual — PAEG Art. 14; relatório da CPAEG — Art. 21, IV;
  relatórios das CSAEGs — Art. 22, V), inclusive se o denominador de referência deve ser
  o da captura imediatamente após o encerramento, o de uma data fixada ou outro, e se a
  instituição precisa designar um snapshot "de referência".
  - Instância competente: CPAEG/Proex.
  - Impacto: FR-060, FR-061; a 013 e qualquer publicação.
  - Tratamento provisório: vários snapshots independentes, sem status; cada análise
    identifica o snapshot que usou.
- **DP-1202** — DECISÃO PENDENTE: **retenção e eliminação de snapshots**, que guardam
  contexto acadêmico por Conclusão, inclusive de quem não participou.
  - Instância competente: encarregado de dados, com CPAEG. Depende de 001/DP-009 e
    005/DP-504.
  - Impacto: FR-050 (nenhuma remoção); volume acumulado de capturas.
  - Tratamento provisório: nenhuma remoção; somente dados fictícios (FR-125).

**Herdadas e resolvidas parcialmente**

- **004/DP-408** — fotografia da população como denominador estável: **parcialmente
  resolvida**.
  - **Resolvido** (capacidade): existe fotografia imutável da população elegível, como
    entidade separada da Campanha, produzida depois do encerramento de Campanha que entrou
    em coleta, que serve como denominador histórico explícito (FR-010, FR-030 a FR-034).
  - **Continua pendente**: se a instituição precisa de fotografia na **abertura**; qual
    fotografia é a de referência para relatórios (DP-1201).
- **005/DP-507** — efeito de correção acadêmica sobre Participação existente:
  **parcialmente resolvida no escopo analítico**.
  - **Resolvido**: num snapshot, Participação existente nunca desaparece; se a Conclusão
    não for elegível no momento da captura, ela é registrada como não elegível no
    snapshot (FR-032, FR-033); correções posteriores não alteram snapshot existente
    (FR-050, FR-080).
  - **Continua pendente**: efeito transacional da correção sobre a Participação
    (validade, escrita) e a própria correção (001/DP-005).

**Herdadas, afetadas e mantidas abertas**

- **001/DP-005** — correção de dado acadêmico: **mantida**; é a razão do congelamento do
  contexto. Nenhuma operação de correção é criada.
- **001/DP-006** — sincronização com a fonte: **mantida**; incorporações depois do
  encerramento afetam capturas posteriores, nunca anteriores.
- **001/DP-003** — reconciliação de identidade: **mantida**; nenhuma correlação entre
  Conclusões da mesma Pessoa (FR-122).
- **001/DP-007** e **010/DP-1005** — vocabulário canônico e grafia das unidades:
  **mantidas**; valores congelados como registrados.
- **002/DP-006** — comparabilidade entre Versões: **mantida**; nenhuma correspondência
  entre Perguntas (FR-077).
- **005/DP-503** — destino e uso analítico de Participações não concluídas: **mantida**;
  preservadas e distinguíveis no dataset (FR-075).
- **005/DP-505** — consulta de dados identificados: **mantida**; nada exposto.
- **005/DP-508** — divergência entre resposta declarada e dado institucional:
  **mantida**; ambos preservados, sem comparação (FR-073).
- **006/DP-601** — concluída por recusa: **mantida**; conta como concluída (FR-082).
- **007/DP-703** — "iniciada": **mantida**; Participação existente (FR-082).
- **010/DP-1001** — identificação produtiva de operadores: **mantida**; nada exposto
  (FR-100, FR-104).
- **004/DP-402** — gestão de Campanha: **mantida**; a captura não gere Campanha.
- **011/DP-1101** — pequenos grupos: **mantida**; nenhuma supressão interna (FR-123).
- **011/DP-1102** — coorte: **mantida**; ano e data congelados, sem coorte.
- **001/DP-009** e **005/DP-504** — base legal, consentimento, retenção: **mantidas**;
  bloqueiam uso com dados reais (FR-125).
- **ADR 0002** (imutabilidade garantida pelas operações) e **ADR 0003** (Q14 declarada):
  respeitados.
