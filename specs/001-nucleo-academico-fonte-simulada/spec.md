# Feature Specification: Núcleo acadêmico longitudinal e fonte institucional simulada

**Feature Branch**: `claude/feature-001-nucleo-academico-fc2889`

**Created**: 2026-09-30

**Status**: Approved. Aprovada pelo solicitante em 2026-09-30, após `/speckit-plan` e
`/speckit-tasks`, com as correções de revisão (SC-004).

**Input**: User description: "Feature 001 — Núcleo acadêmico longitudinal e fonte
institucional simulada. Estabelecer a fundação de domínio para que o NIAE represente
Pessoa → uma ou várias Conclusões Acadêmicas e obtenha esse contexto acadêmico por meio
de uma fonte institucional abstrata e substituível, inicialmente simulada, sem depender
do sistema acadêmico real."

## Contexto

O Formulário Egresso do Ifes 2024 pede ao respondente informações sobre a própria
formação que provavelmente já pertencem ao Ifes. Em Q10–Q19 aparecem ano de conclusão,
campus, modalidade, forma de ingresso, nível, forma de oferta e curso (ver
`docs/referencias/formulario-egresso-ifes-2024-inventario.md`). O NIAE deverá
futuramente usar dados institucionais para contextualizar a pesquisa em vez de perguntar
de novo (Princípios III e XIV). Ainda não se conhecem, porém, a fonte acadêmica oficial,
seus identificadores e seu esquema.

Esta feature estabelece a fundação **Pessoa → Conclusão Acadêmica**. O contexto
acadêmico é obtido por uma fronteira explícita e substituível, que nesta feature tem uma
implementação simulada e determinística. O objetivo é que as próximas features recebam
algo conceitualmente equivalente a:

> **Pessoa**: (nome fictício, se fornecido pela fonte)
>
> **Conclusões Acadêmicas**:
> 1. Tecnologia em Análise e Desenvolvimento de Sistemas — Campus Serra — Graduação —
>    Presencial — concluída em 2022
> 2. Especialização em Informática na Educação — Cefor — Pós-graduação — a distância —
>    concluída em 2025

sem precisar saber de onde e como esses dados foram obtidos.

> Nota: o exemplo da descrição original indicava conclusão em 2028, data posterior à
> desta spec. Como a fonte simulada só pode declarar conclusões já ocorridas, o exemplo
> foi ajustado para datas passadas, sem alterar seu propósito.

**Termos usados nesta spec** (conceituais; a nomenclatura concreta pertence ao plan):

- **Fronteira de dados acadêmicos**: contrato pelo qual o domínio obtém dados
  acadêmicos. Corresponde ao `AcademicDataProvider` da Constituição (Princípio V).
- **Fonte simulada**: implementação dessa fronteira com dados fictícios e
  determinísticos. Corresponde ao `MockAcademicDataProvider`.
- **Referência de origem**: o par (fonte, identificador que aquela fonte atribui ao
  registro).
- **Incorporação**: ato pelo qual o NIAE reconhece em seu domínio uma Pessoa ou uma
  Conclusão Acadêmica obtida de uma fonte e lhe atribui identidade interna própria.
- **Registro reconhecido como conclusão**: registro que a fonte declara explicitamente
  como formação concluída, no sentido do Art. 3º da PAEG.
- **Conclusão Acadêmica elegível**: nesta spec, sinônimo de conclusão reconhecida, ou
  seja, elegível como egresso (Princípio II). Não se refere a elegibilidade de
  campanha, que será tratada em feature própria.

## User Scenarios & Testing *(mandatory)*

Os "usuários" desta feature são as **funcionalidades consumidoras do NIAE** (as
próximas features) e quem as desenvolve e testa. Esta feature não tem interface com o
egresso nem com gestores.

### User Story 1 - Representar uma Pessoa com sua Conclusão Acadêmica (Priority: P1)

Uma funcionalidade consumidora precisa conhecer uma Pessoa e a formação que ela
concluiu no Ifes: curso, unidade, nível, modalidade, forma de oferta e período de
conclusão. Esse contexto deve vir como dado institucional, sem ser perguntado ao egresso.

**Why this priority**: é a menor fatia que entrega a fundação Pessoa → Conclusão
Acadêmica, da qual dependem todas as features posteriores (Princípio I).

**Independent Test**: incorporar a Pessoa do Cenário A da fonte simulada e consultar sua
trajetória acadêmica. Deve existir uma Pessoa com exatamente uma Conclusão Acadêmica, e
cada atributo deve ser igual ao declarado pela fonte.

**Acceptance Scenarios**:

1. **Given** a fonte simulada contém a Pessoa do Cenário A com uma conclusão reconhecida,
   **When** essa Pessoa é incorporada, **Then** o NIAE passa a ter uma Pessoa com
   identidade interna própria e uma Conclusão Acadêmica associada a ela.
2. **Given** a Pessoa do Cenário A foi incorporada, **When** sua trajetória acadêmica é
   consultada, **Then** a conclusão retornada tem curso, unidade, nível, modalidade,
   forma de oferta e referência temporal iguais aos declarados pela fonte.
3. **Given** a fonte não informa um dos atributos do contexto mínimo de determinada
   conclusão, **When** a conclusão é consultada, **Then** o atributo aparece
   explicitamente como "não informado pela fonte", e não com valor inferido ou padrão.

---

### User Story 2 - Uma única Pessoa com múltiplas Conclusões Acadêmicas (Priority: P1)

Uma Pessoa que concluiu mais de uma formação no Ifes deve ser uma única Pessoa no NIAE,
com uma Conclusão Acadêmica para cada formação. Isso vale para formações no mesmo campus
ou em unidades diferentes, em níveis diferentes ou em períodos diferentes.

**Why this priority**: é critério central da feature e invariante constitucional
(Princípios I e XI). Um modelo que duplica a Pessoa ou funde formações compromete toda
a longitudinalidade futura.

**Independent Test**: incorporar as Pessoas dos Cenários B, C e D e verificar que cada
uma existe uma única vez, com o número de conclusões declarado pela fonte.

**Acceptance Scenarios**:

1. **Given** a Pessoa do Cenário B tem duas conclusões reconhecidas no mesmo campus,
   **When** é incorporada, **Then** existe uma Pessoa com duas Conclusões Acadêmicas
   distintas.
2. **Given** a Pessoa do Cenário C tem conclusões em unidades diferentes, **When** é
   incorporada, **Then** existe uma Pessoa, e cada Conclusão Acadêmica carrega sua
   própria unidade.
3. **Given** a Pessoa do Cenário D tem formações em níveis diferentes, **When** é
   incorporada, **Then** existe uma Pessoa, e cada Conclusão Acadêmica carrega seu
   próprio nível.
4. **Given** uma Pessoa com três conclusões reconhecidas, **When** sua trajetória é
   consultada, **Then** o resultado contém uma Pessoa e três Conclusões Acadêmicas, cada
   uma com identidade própria.

---

### User Story 3 - Distinguir o contexto próprio de cada conclusão (Priority: P1)

Ao consultar a trajetória de uma Pessoa com várias formações, uma funcionalidade
consumidora deve conseguir distinguir sem ambiguidade cada Conclusão Acadêmica e seu
contexto. Isso permite que, no futuro, uma Participação se refira inequivocamente a uma
formação específica.

**Why this priority**: sem essa distinção, uma participação futura referente ao Curso A
(Campus Serra) poderia ser atribuída ao contexto do Curso B (Cefor). Isso viola os
Princípios I e XI.

**Independent Test**: consultar a trajetória da Pessoa do Cenário C e verificar que
nenhum atributo de uma conclusão aparece em outra e que cada conclusão pode ser
consultada isoladamente pela sua identidade.

**Acceptance Scenarios**:

1. **Given** uma Pessoa com conclusões no Campus Serra e no Cefor, **When** a trajetória
   é consultada, **Then** cada conclusão apresenta o curso, a unidade, o nível, a
   modalidade, a forma de oferta e a referência temporal declarados pela fonte para
   aquela formação específica.
2. **Given** a identidade de uma Conclusão Acadêmica, **When** o contexto dessa conclusão
   é consultado isoladamente, **Then** retorna-se exatamente aquela conclusão e a Pessoa
   à qual ela pertence.
3. **Given** uma Pessoa com várias conclusões, **When** se pergunta "qual é o campus
   desta Pessoa", **Then** o modelo não oferece essa informação como atributo da Pessoa.
   Unidade, curso, nível e modalidade só existem no contexto de uma conclusão.
4. **Given** duas conclusões da mesma Pessoa com atributos parecidos (por exemplo, mesmo
   curso e unidade) e referências de origem diferentes, **When** ambas são incorporadas,
   **Then** permanecem duas Conclusões Acadêmicas distintas e não são fundidas por
   semelhança.

---

### User Story 4 - Obter o contexto acadêmico por fonte simulada e substituível (Priority: P2)

Quem desenvolve as próximas features precisa de dados acadêmicos realistas sem acesso ao
sistema acadêmico real. Também precisa da garantia de que trocar a fonte simulada por
uma fonte real não exigirá mudar o domínio nem as funcionalidades consumidoras.

**Why this priority**: sem isso o projeto fica bloqueado pela fonte real (Princípios V e
XXV). A prioridade é P2 porque as histórias P1 definem o que a fronteira precisa
entregar.

**Independent Test**: executar todas as verificações das histórias P1 tendo a fonte
simulada como única fonte, em ambiente sem acesso a sistemas acadêmicos. Em seguida,
executar a mesma verificação de contrato contra uma segunda implementação da fronteira,
com outro conjunto de dados fictícios, e verificar que as verificações do domínio passam
sem alteração.

**Acceptance Scenarios**:

1. **Given** um ambiente sem acesso a nenhum sistema acadêmico real, **When** os
   cenários da fonte simulada são consultados, **Then** todos retornam os resultados
   declarados.
2. **Given** a mesma consulta feita várias vezes à fonte simulada, **When** os resultados
   são comparados, **Then** são idênticos, independentemente de horário, ordem das
   consultas ou ambiente.
3. **Given** uma segunda implementação da fronteira que obedece ao mesmo contrato,
   **When** substitui a fonte simulada, **Then** o domínio e as funcionalidades
   consumidoras funcionam sem modificação.
4. **Given** uma funcionalidade consumidora, **When** ela obtém a trajetória acadêmica de
   uma Pessoa, **Then** não precisa conhecer qual fonte forneceu os dados, nem seu
   esquema, vocabulário ou identificadores.

---

### User Story 5 - Repetir a obtenção sem criar duplicidade (Priority: P2)

Os mesmos dados acadêmicos podem ser obtidos várias vezes da mesma fonte, em momentos
diferentes. O NIAE deve reconhecer que se trata do mesmo registro e não criar Pessoas ou
Conclusões duplicadas.

**Why this priority**: a duplicação destruiria a unicidade da Pessoa (Princípio XI) e a
estabilidade da Conclusão observada (Princípio I). Também inviabilizaria que uma mesma
Conclusão seja acompanhada várias vezes no futuro (Cenário E).

**Independent Test**: incorporar todo o conjunto da fonte simulada três vezes, em ordens
diferentes, e verificar que as quantidades de Pessoas e Conclusões e suas identidades
internas são iguais às de uma única incorporação.

**Acceptance Scenarios**:

1. **Given** a Pessoa do Cenário A já incorporada, **When** ela é obtida e incorporada
   novamente da mesma fonte, **Then** continua existindo uma única Pessoa com a mesma
   identidade interna e uma única Conclusão com a mesma identidade interna.
2. **Given** a Pessoa do Cenário E incorporada em um momento, **When** é obtida de novo
   em outro momento, **Then** sua Conclusão Acadêmica mantém a mesma identidade interna.
   Assim, participações futuras poderão se referir a ela.
3. **Given** uma Pessoa já incorporada com uma conclusão, **When** a mesma fonte passa a
   declarar uma segunda conclusão reconhecida dessa Pessoa, **Then** a nova conclusão é
   associada à Pessoa existente, sem criar outra Pessoa.
4. **Given** um registro já incorporado, **When** a mesma fonte devolve para a mesma
   referência de origem um conteúdo diferente do incorporado, **Then** nenhuma
   duplicata é criada, o conteúdo anterior não é sobrescrito em silêncio e a
   divergência é sinalizada explicitamente (tratamento definitivo: DP-005).

---

### User Story 6 - Preservar a proveniência do registro institucional (Priority: P2)

Para Pessoas e Conclusões Acadêmicas, deve ser possível saber, quando necessário, qual
fonte forneceu o dado, que identificador essa fonte atribuiu ao registro e uma
referência temporal suficiente da obtenção. O dado deve continuar identificável como
institucional, e dados simulados nunca devem ser confundidos com dados institucionais
reais. Basta reconhecer a origem: não há linhagem por atributo nem histórico de
versões dos dados recebidos (FR-037).

**Why this priority**: a proveniência sustenta a idempotência (US5) e a auditoria
(Princípio IV), além de manter distintos o dado institucional e a resposta declarada
(Princípio III).

**Independent Test**: para cada Pessoa e Conclusão incorporada da fonte simulada,
recuperar fonte, identificador na fonte, referência temporal da obtenção e categoria de
dado.
Verificar que a fonte aparece identificada como simulada.

**Acceptance Scenarios**:

1. **Given** uma Conclusão Acadêmica incorporada, **When** sua proveniência é
   consultada, **Then** é possível saber qual fonte a forneceu, o identificador da
   conclusão nessa fonte e uma referência temporal da obtenção.
2. **Given** uma Pessoa incorporada, **When** sua proveniência é consultada, **Then** é
   possível saber de qual fonte e com qual identificador da fonte ela foi obtida.
3. **Given** dados vindos da fonte simulada, **When** sua proveniência é consultada,
   **Then** a fonte aparece explicitamente como simulada.
4. **Given** qualquer atributo acadêmico incorporado, **When** se verifica sua
   categoria, **Then** ela é "institucional" por definição. O modelo desta feature não
   tem nenhum campo declarado ou derivado, então não há como um atributo acadêmico ser
   registrado como resposta ou cálculo.

---

### User Story 7 - Não tratar situação não concluída como Conclusão Acadêmica elegível (Priority: P2)

Registros acadêmicos que não correspondem a formação concluída não podem ser
materializados como Conclusão Acadêmica nem tratados, explícita ou implicitamente, como
egresso. Exemplos: matrícula ativa, abandono, evasão, transferência ou situação
desconhecida.

**Why this priority**: a descrição original propunha P3. A prioridade foi elevada para
P2 porque o Princípio II é NON-NEGOTIABLE e porque essa distinção precisa existir no
contrato da fronteira desde o início. Acrescentá-la depois alteraria o contrato que as
demais features já consomem.

**Independent Test**: consultar e incorporar as Pessoas e os registros do Cenário F e
verificar que nenhum registro não concluído aparece como Conclusão Acadêmica e que a
consulta direta a cada um informa explicitamente que ele não é reconhecido como
conclusão.

**Acceptance Scenarios**:

1. **Given** um registro que a fonte declara como matrícula ativa, abandono, evasão ou
   transferência, **When** a trajetória da Pessoa é consultada ou incorporada, **Then**
   esse registro não aparece como Conclusão Acadêmica.
2. **Given** um registro cuja situação a fonte não informa, ou informa de forma não
   reconhecível, **When** é obtido, **Then** não é materializado como Conclusão
   Acadêmica. O NIAE não presume conclusão.
3. **Given** uma Pessoa com uma conclusão reconhecida e outro registro em matrícula
   ativa, **When** sua trajetória é consultada, **Then** apenas a conclusão reconhecida é
   retornada.
4. **Given** a referência de origem de um registro não concluído, **When** o contexto
   desse registro é consultado como conclusão, **Then** o resultado informa
   explicitamente que o registro existe e não é reconhecido como conclusão. Esse
   resultado é distinto de "inexistente".
5. **Given** uma pessoa que a fonte conhece apenas com matrícula ativa em graduação, sem
   nenhuma conclusão, **When** ela é localizada e se tenta incorporá-la, **Then** o
   resultado é "pessoa localizada, sem conclusões acadêmicas elegíveis" e nenhuma
   Pessoa é materializada no NIAE (FR-039).

---

### User Story 8 - Tratar explicitamente consulta a pessoa ou conclusão inexistente (Priority: P3)

Consultas a pessoas ou conclusões desconhecidas devem ter resultado explícito e
distinguível. O mesmo vale para falhas da fonte, que nunca podem ser confundidas com
inexistência.

**Why this priority**: protege as features consumidoras de interpretar errado a
ausência de dado. A prioridade é P3 porque não bloqueia o núcleo, embora deva estar no
contrato.

**Independent Test**: consultar identificadores desconhecidos (Cenário G) e simular uma
falha da fonte (Cenário H), verificando que cada caso tem um resultado próprio e que
nada é incorporado.

**Acceptance Scenarios**:

1. **Given** um identificador de pessoa que a fonte não conhece, **When** a pessoa é
   localizada, **Then** o resultado é explicitamente "pessoa inexistente na fonte" e
   nenhuma Pessoa é incorporada.
2. **Given** um identificador de conclusão que a fonte não conhece, **When** o contexto
   da conclusão é consultado, **Then** o resultado é explicitamente "conclusão
   inexistente na fonte".
3. **Given** a fonte está indisponível ou falha durante a consulta, **When** uma pessoa
   ou conclusão é consultada, **Then** o resultado é explicitamente uma falha da fonte.
   Ele não é "inexistente", não é "sem conclusões" e não é um resultado parcial
   apresentado como completo.
4. **Given** um registro já incorporado, **When** uma consulta posterior falha, **Then**
   a falha não remove nem altera o que já foi incorporado.

---

### Edge Cases

- **Pessoa localizada sem nenhuma conclusão reconhecida** (por exemplo, só com matrícula
  ativa): a consulta à fronteira informa "pessoa localizada, sem conclusões
  reconhecidas", e essa Pessoa não é materializada no NIAE nesta feature (FR-039).
- **Pessoa sem nome informado pela fonte**: o modelo continua válido. A Pessoa é
  incorporada normalmente, porque o nome não participa da identidade (FR-005).
- **Duas pessoas com o mesmo nome**: continuam sendo duas Pessoas, já que identidade e
  deduplicação dependem apenas da referência de origem (FR-031).
- **Duas conclusões com mesmo curso e mesma unidade** e referências de origem distintas
  (por exemplo, o mesmo curso concluído duas vezes): permanecem distintas, porque o NIAE
  não funde por semelhança de atributos.
- **Atributo do contexto mínimo ausente na fonte**: aparece como "não informado pela
  fonte". O NIAE não o infere de outro atributo. Por exemplo, a modalidade não é
  deduzida do prefixo "EaD -" no nome do curso (inventário, O-14), e o nível não é
  deduzido do nome do curso.
- **Referência temporal só com o ano**: o ano é preservado sem fabricar dia ou mês. Se a
  fonte fornecer a data completa, a data completa é preservada.
- **Mesma referência de origem com conteúdo diferente em nova obtenção**: não duplica e
  não sobrescreve em silêncio; a divergência é sinalizada (DP-005).
- **Conclusão já incorporada que deixa de aparecer ou passa a outra situação na fonte**:
  não é removida nem alterada em silêncio; a divergência é sinalizada (DP-005, DP-006).
- **Mesma referência de conclusão associada pela fonte a outra pessoa**: a conclusão não
  é reatribuída em silêncio; a divergência é sinalizada (DP-005).
- **Registros de fontes diferentes que parecem da mesma pessoa**: não são fundidos nem
  declarados iguais (DP-003). Nesta feature só existe uma fonte ativa.
- **Fonte declara como concluída uma formação com data de conclusão posterior à data da
  consulta**: o NIAE não reclassifica a situação por regra própria. A validação de
  consistência dos dados da fonte real está em DP-005. A fonte simulada não contém esse
  caso.
- **Falha da fonte no meio de uma obtenção**: nenhum resultado parcial é tratado como
  completo, e o que já foi incorporado continua inalterado.

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII): **[Const.]** decorre diretamente da Constituição;
**[PAEG]** decorre da PAEG; **[Arquitetura]** é decisão arquitetural; **[Hipótese]** é
hipótese de produto reversível; **[Escopo]** é decisão de escopo desta feature,
confirmada pelo solicitante e revisável por feature futura; **[Herdado]** vem do
instrumento atual como referência de valores. Nenhum requisito desta feature altera
perguntas do instrumento.

### Functional Requirements

**Pessoa**

- **FR-001**: O sistema DEVE representar a Pessoa como indivíduo único no domínio do NIAE,
  com identidade interna própria e independente de qualquer identificador fornecido por
  fontes. [Const. — Terminologia; XI]
- **FR-002**: O sistema DEVE permitir que uma Pessoa tenha nenhuma, uma ou várias
  Conclusões Acadêmicas. [Const. — Terminologia; XI]
- **FR-003**: O sistema NÃO DEVE atribuir à Pessoa campus, unidade, curso, nível,
  modalidade, forma de oferta ou período de conclusão. Esses atributos existem apenas no
  contexto de uma Conclusão Acadêmica. [Const. — XI]
- **FR-004**: O sistema NÃO DEVE criar mais de uma Pessoa para a mesma referência de
  origem de pessoa (critério detalhado em FR-031), ainda que ela tenha várias formações em cursos, unidades, níveis ou
  períodos diferentes. [Const. — XI]
- **FR-005**: A Pessoa é composta por identidade interna e referências de origem. A
  fonte PODE fornecer o **nome** como atributo institucional **opcional**, apenas para
  apresentação. O nome:
  - NÃO identifica a Pessoa;
  - NÃO participa da deduplicação;
  - NÃO DEVE ser usado para reconciliação;
  - quando ausente, NÃO invalida a Pessoa.

  O sistema NÃO DEVE incorporar CPF, e-mail, data de nascimento, telefone, documentos ou
  outros dados pessoais nesta feature. Eles só entram quando uma feature com consumidor
  concreto precisar deles. [Escopo; Const. — XVI, XXII]
    *(Revisado pela 018)* CPF e nascimento têm consumidor concreto na capacidade separada de
  acesso, sem alterar a identidade interna (018 FR-010, FR-016, FR-020).

- **FR-006**: O sistema NÃO DEVE presumir que algum identificador da fonte (CPF,
  matrícula ou outro) é a chave da Pessoa, nem que a Pessoa tem uma única matrícula. Os
  identificadores de fonte DEVEM ser tratados como referências opacas. O modelo NÃO DEVE
  impedir que uma Pessoa tenha mais de uma referência de origem no futuro. [Const. —
  Terminologia, Pessoa]

    *(Revisado pela 018)* CPF permanece fora da identidade da Pessoa; o agrupamento por
  indivíduo cabe à fonte (018 FR-021).

**Conclusão Acadêmica**

- **FR-007**: O sistema DEVE representar a Conclusão Acadêmica como fato institucional:
  "determinada Pessoa concluiu determinada formação, em determinado contexto
  institucional e temporal". Cada Conclusão Acadêmica pertence a exatamente uma Pessoa.
  [Const. — Terminologia]
- **FR-008**: Cada Conclusão Acadêmica DEVE ter identidade interna própria e estável, que
  não mude entre obtenções sucessivas nem ao longo do tempo. Assim, funcionalidades
  futuras podem referenciá-la inequivocamente. [Const. — I]
- **FR-009**: O contexto mínimo da Conclusão Acadêmica DEVE comportar: (a) referência de
  origem da conclusão (obrigatória); (b) identificação e/ou denominação do curso;
  (c) unidade (campus, campus avançado ou Cefor — PAEG, Art. 2º, parágrafo único);
  (d) nível da formação; (e) modalidade; (f) forma de oferta; (g) referência temporal da
  conclusão. Os itens (b) a (g) são preenchidos quando disponíveis na fonte. [Const. —
  Terminologia; PAEG Art. 2º]
- **FR-010**: Um atributo do contexto mínimo não fornecido pela fonte DEVE ser
  representado explicitamente como "não informado pela fonte". Ele NÃO DEVE ser
  preenchido com valor padrão, inferido de outros atributos ou herdado de outra
  conclusão ou da Pessoa. [Const. — III, XXIX]
- **FR-011**: A referência temporal da conclusão DEVE preservar a granularidade fornecida
  pela fonte (ano, ou data completa) sem fabricar precisão. [Const. — I, IV]
- **FR-012**: O sistema NÃO DEVE incluir no modelo desta feature forma de ingresso,
  reserva de vagas ou outros atributos acadêmicos além do contexto mínimo. Eles poderão
  ser acrescentados quando a spec de migração do instrumento demonstrar necessidade
  concreta. [Const. — XXII]
- **FR-013**: Cada Conclusão Acadêmica DEVE conservar seu próprio contexto. A
  incorporação, consulta ou divergência de uma conclusão NÃO DEVE alterar o contexto de
  outra conclusão da mesma Pessoa. [Const. — I, XI]
- **FR-014**: O sistema NÃO DEVE fundir Conclusões Acadêmicas com referências de origem
  distintas, mesmo que tenham atributos iguais ou semelhantes. [Const. — I]

**Consulta da trajetória acadêmica**

- **FR-015**: O sistema DEVE permitir consultar a trajetória acadêmica de uma Pessoa. A
  consulta retorna a Pessoa e todas as suas Conclusões Acadêmicas reconhecidas, cada uma
  com identidade e contexto completo, distinguíveis entre si. [Const. — XI, XIV]
- **FR-016**: O sistema DEVE permitir consultar isoladamente o contexto de uma Conclusão
  Acadêmica pela sua identidade e obter também a Pessoa à qual ela pertence. [Const. — I]
- **FR-017**: A ordem em que as conclusões são retornadas NÃO DEVE ter significado de
  domínio, como "formação principal" ou "formação atual". A fonte simulada DEVE
  retorná-las em ordem determinística. [Const. — I, XXV]

**Elegibilidade como egresso**

- **FR-018**: Somente registros que a fonte declara explicitamente como formação
  concluída, no sentido do Art. 3º da PAEG, DEVEM ser materializados como Conclusão
  Acadêmica. [PAEG Art. 3º; Const. — II]
- **FR-019**: Registros em matrícula ativa, abandono, evasão, transferência, outra
  situação não concluída, situação desconhecida ou situação não informada NÃO DEVEM ser
  materializados como Conclusão Acadêmica, nem tratados explícita ou implicitamente como
  egresso. [Const. — II]
- **FR-020**: O NIAE NÃO DEVE criar regra acadêmica própria para decidir se houve
  conclusão (por exemplo, a partir de datas, carga horária ou outros atributos). A
  correspondência entre as situações de uma fonte e o reconhecimento de conclusão
  pertence à implementação daquela fonte. Para a fonte real, ela depende de critério
  institucional (DP-008). Na fonte simulada, cada registro declara explicitamente se é
  conclusão reconhecida. [Const. — II, V, XXIX]

**Fronteira de dados acadêmicos**

- **FR-021**: O domínio DEVE obter dados acadêmicos exclusivamente por uma fronteira
  explícita. Nenhuma parte do domínio ou das funcionalidades consumidoras DEVE depender
  da estrutura, do vocabulário, dos códigos ou da semântica de identificadores de uma
  fonte específica. [Const. — V]
- **FR-022**: A fronteira DEVE oferecer comportamento suficiente para:
  (a) localizar uma pessoa a partir do identificador que a fonte lhe atribui;
  (b) obter as conclusões reconhecidas dessa pessoa;
  (c) obter o contexto de uma conclusão a partir do identificador que a fonte lhe
  atribui;
  (d) distinguir, em cada consulta, os resultados: encontrado; inexistente na fonte;
  existente mas não reconhecido como conclusão; pessoa localizada sem conclusões
  reconhecidas; falha da fonte. [Const. — V; Arquitetura]
- **FR-023**: A fronteira DEVE entregar os dados já na forma canônica do NIAE.
  Peculiaridades de cada fonte (códigos, nomes de campos, situações próprias) DEVEM ficar
  na implementação daquela fonte. [Const. — V]
- **FR-024**: Toda implementação da fronteira, simulada ou real, DEVE obedecer ao mesmo
  contrato e ser verificável pela mesma verificação de contrato. Substituir uma
  implementação por outra NÃO DEVE exigir alteração do domínio nem das funcionalidades
  consumidoras. [Const. — V, XXV, XXVI]
- **FR-025**: Uma falha ou indisponibilidade da fonte NÃO DEVE ser interpretada como
  inexistência, como ausência de conclusões ou como resultado completo. Ela também NÃO
  DEVE alterar o que já foi incorporado. [Const. — II, XXIX; Arquitetura]

**Fonte simulada**

- **FR-026**: A primeira implementação da fronteira DEVE ser uma fonte simulada
  determinística. A mesma consulta DEVE produzir sempre o mesmo resultado,
  independentemente de horário, ordem de execução ou ambiente. [Const. — Desenvolvimento
  Inicial com Dados Simulados; XXV]
- **FR-027**: A fonte simulada DEVE conter, pelo menos, os cenários abaixo. Cada cenário
  DEVE ser identificável e documentado com o resultado esperado:
  - **A** — Pessoa com uma única Conclusão Acadêmica;
  - **B** — Pessoa com duas Conclusões Acadêmicas no mesmo campus, concluídas em períodos
    diferentes;
  - **C** — Pessoa com Conclusões Acadêmicas em unidades diferentes (incluindo o Cefor);
  - **D** — Pessoa com formações em níveis diferentes;
  - **E** — Pessoa cuja Conclusão Acadêmica, concluída há tempo suficiente para ser
    acompanhada em momentos diferentes, é usada para demonstrar estabilidade de
    identidade entre obtenções. Nenhuma Participação é criada;
  - **F** — registros que não correspondem a formação concluída, cobrindo, de forma
    declarada: matrícula ativa; abandono ou evasão; transferência; situação desconhecida
    ou não informada. Inclui ao menos uma Pessoa só com registros não concluídos e uma
    Pessoa com conclusão reconhecida e também registro não concluído;
  - **G** — identificador de pessoa desconhecido e identificador de conclusão
    desconhecido;
  - **H** — falha da fonte, que pode ser provocada de forma controlada para verificar
    FR-025.

  Pelo menos uma Pessoa DEVE ter três ou mais Conclusões Acadêmicas, e pelo menos uma
  conclusão DEVE ter um atributo do contexto mínimo "não informado pela fonte". [Const. —
  Desenvolvimento Inicial com Dados Simulados]
- **FR-028**: Os dados da fonte simulada DEVEM ser fictícios. Eles NÃO DEVEM conter CPF,
  e-mail, matrícula, telefone ou outro dado de pessoas reais. Os identificadores DEVEM
  ser visivelmente fictícios. [Const. — XVI]
    *(Revisado pela 018)* Os cenários incluem CPF com dígitos verificadores válidos e
  nascimento exclusivamente fictícios (018 FR-026).

- **FR-029**: Os dados da fonte simulada DEVERIAM ser realistas. Unidades, cursos, níveis
  e modalidades DEVERIAM ser plausíveis no Ifes, por exemplo usando as unidades e os
  cursos que aparecem no instrumento atual, e as datas de conclusão DEVEM ser passadas.
  Isso não constitui declaração de quais valores existem na fonte real. [Herdado — como
  referência de valores; Hipótese]
- **FR-030**: A fonte simulada DEVE ser o único meio de fornecer Pessoas e Conclusões
  Acadêmicas nesta feature. O sistema NÃO DEVE oferecer cadastro, edição ou exclusão
  manual de Pessoa ou Conclusão Acadêmica. [Const. — V, XXII]

**Idempotência e identidade na mesma fonte**

- **FR-031**: Uma Pessoa DEVE ser reconhecida como a mesma quando a fonte e o
  identificador da pessoa naquela fonte forem os mesmos. O mesmo vale para a Conclusão
  Acadêmica, com o identificador da conclusão naquela fonte. Incorporar de novo uma
  referência já incorporada DEVE resultar na mesma identidade interna, qualquer que seja
  o número de repetições, a ordem ou o intervalo entre elas. A deduplicação DEVE usar
  exclusivamente a referência de origem. Nome ou outros atributos nunca entram nesse
  critério. [Const. — IV, XI]
- **FR-032**: Uma nova conclusão reconhecida de uma Pessoa já incorporada DEVE ser
  associada a essa Pessoa, sem criar outra. [Const. — XI]
- **FR-033**: Quando uma referência já incorporada voltar da mesma fonte com conteúdo
  diferente do incorporado, o sistema NÃO DEVE criar duplicata e NÃO DEVE sobrescrever
  em silêncio o conteúdo anterior. Isso inclui atributos alterados, conclusão associada a
  outra pessoa, conclusão que deixa de ser reconhecida e registro que deixa de existir. A
  divergência NÃO DEVE ser interpretada como novo registro nem destruir o estado
  anteriormente incorporado. Ela DEVE ser sinalizada explicitamente no resultado da
  incorporação. Esta feature NÃO DEVE especificar nem construir:
  - workflow de resolução;
  - fila ou painel de inconsistências;
  - aprovação humana;
  - event sourcing;
  - mecanismo sofisticado de sincronização.

  O tratamento definitivo fica em DP-005 e DP-006. [Const. — III, XXII, XXIX; Hipótese
  provisória]
    *(Revisado pela 018)* A atualização de material de verificação segue regra própria,
  preservando os dados acadêmicos incorporados (018 FR-024).

- **FR-034**: O sistema NÃO DEVE resolver nem presumir identidade entre registros de
  fontes diferentes. [Const. — Terminologia, Pessoa; XXIX]

**Proveniência e categoria do dado**

- **FR-035**: Para cada Pessoa e cada Conclusão Acadêmica, o sistema DEVE permitir
  determinar:
  - a fonte que a forneceu, incluindo se é simulada;
  - o identificador atribuído por essa fonte;
  - uma referência temporal suficiente da obtenção (por exemplo, momento da
    incorporação ou da última obtenção; a escolha pertence ao plan).

  [Const. — IV]
- **FR-036**: Todo atributo acadêmico incorporado nesta feature DEVE ser identificável
  como dado **institucional**. Esta feature NÃO DEVE criar dado declarado nem dado
  derivado, como idade, tempo desde a conclusão ou coorte. [Const. — III]
- **FR-037**: A proveniência DEVE ser proporcional, limitada a fonte, identificador
  externo e referência temporal, no necessário para reconhecer a origem (FR-031 a
  FR-035). Esta feature NÃO DEVE introduzir:
  - sistema genérico de linhagem de dados;
  - proveniência ou histórico por atributo;
  - versionamento completo dos dados recebidos da fonte;
  - trilha de todas as obtenções.

  [Const. — IV, XXII]

**Longitudinalidade**

- **FR-038**: Nenhuma decisão desta feature DEVE impedir que uma mesma Conclusão
  Acadêmica tenha, no futuro, várias Participações em Pesquisa ao longo do tempo. Esta
  feature NÃO DEVE criar entidades, campos ou marcadores provisórios de Pesquisa, Versão,
  Campanha, Participação ou Resposta. [Const. — I, VII, XXII]

**Pessoa sem conclusão elegível**

- **FR-039**: Nesta feature, uma pessoa localizada pela fonte sem nenhuma Conclusão
  Acadêmica elegível NÃO DEVE ser materializada nem persistida no NIAE. A fronteira
  informa "pessoa localizada, sem conclusões acadêmicas elegíveis" (FR-022). Isso não
  altera a cardinalidade conceitual Pessoa 0..N Conclusões (FR-002) e não impede que uma
  feature futura trate estudantes ainda não egressos, se houver necessidade
  institucional (por exemplo, PAEG Art. 9º). [Escopo; Const. — II, XVI, XXII]

### Key Entities *(include if feature involves data)*

- **Pessoa**: indivíduo único no domínio do NIAE. Atributos: identidade interna;
  referências de origem (uma nesta feature, sem impedir várias no futuro); nome
  opcional, apenas de apresentação, quando fornecido pela fonte (institucional; não é
  identificador nem critério de deduplicação — FR-005). Relação: 0..N Conclusões
  Acadêmicas. Nesta feature só são materializadas Pessoas com ao menos uma conclusão
  elegível (FR-039). Não tem atributos acadêmicos.
- **Conclusão Acadêmica**: fato institucional de conclusão de uma formação. Atributos,
  todos institucionais: identidade interna; referência de origem; curso; unidade; nível;
  modalidade; forma de oferta; referência temporal da conclusão com sua granularidade.
  Cada atributo pode estar "não informado pela fonte". Relação: pertence a exatamente
  uma Pessoa. Futuramente receberá 0..N Participações, que não são criadas aqui.
- **Referência de origem**: par (fonte, identificador atribuído pela fonte), com uma
  referência temporal da obtenção. Sustenta idempotência e proveniência. A fonte é identificada
  inclusive quanto a ser simulada.
- **Fronteira de dados acadêmicos** (conceito de contrato, não entidade de dados):
  define as consultas e os resultados distinguíveis de FR-022.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| Identidade interna da Pessoa | Interno do NIAE (não é dado acadêmico) | Atribuída na incorporação | Não se aplica |
| Nome da Pessoa (opcional, apresentação) | Institucional | Fronteira de dados acadêmicos (fonte simulada nesta feature) | FR-033; política definitiva DP-005 |
| Referência de origem (Pessoa e Conclusão) | Institucional (metadado de proveniência) | Fronteira de dados acadêmicos | FR-033 |
| Referência temporal da obtenção | Interno do NIAE (metadado de proveniência) | Registrada na incorporação/obtenção | Não se aplica |
| Curso, unidade, nível, modalidade, forma de oferta | Institucional | Fronteira de dados acadêmicos | FR-033; DP-005 |
| Referência temporal da conclusão | Institucional | Fronteira de dados acadêmicos | FR-033; DP-005 |
| Reconhecimento como conclusão | Institucional (declarado pela fonte, não calculado pelo NIAE) | Implementação da fonte; critério real em DP-008 | FR-033; DP-005 |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Todos os cenários A a H da fonte simulada produzem o resultado documentado
  em 100% das execuções da verificação automatizada.
- **SC-002**: Para a Pessoa com três ou mais conclusões, a consulta da trajetória retorna
  exatamente 1 Pessoa e o número de Conclusões declarado pela fonte. Nenhum atributo
  aparece em conclusão diferente daquela em que a fonte o declarou.
- **SC-003**: Incorporar o conjunto completo da fonte simulada 3 vezes, em ordens
  diferentes, resulta exatamente nas mesmas quantidades e nas mesmas identidades
  internas de Pessoas e Conclusões de uma única incorporação, com 0 duplicatas.
- **SC-004**: 0 registros **não concluídos** do Cenário F aparecem como Conclusão
  Acadêmica, e 100% das consultas diretas a eles informam "não reconhecido como
  conclusão". A conclusão reconhecida da Pessoa F2 é persistida normalmente.
- **SC-005**: 100% das Pessoas e Conclusões incorporadas têm fonte, identificador na
  fonte e referência temporal da obtenção recuperáveis. 100% das obtidas da fonte simulada
  aparecem identificadas como simuladas.
- **SC-006**: Uma segunda implementação da fronteira, com outro conjunto fictício, passa
  na mesma verificação de contrato. As verificações do domínio e das funcionalidades
  consumidoras passam sem nenhuma alteração.
- **SC-007**: Todas as verificações desta feature executam com sucesso em ambiente sem
  acesso a qualquer sistema acadêmico real.
- **SC-008**: Uma funcionalidade consumidora de demonstração obtém a trajetória
  acadêmica completa de uma Pessoa com duas formações, no formato da "experiência
  esperada" descrita no Contexto, usando apenas o domínio e a fronteira, sem referência à
  fonte concreta.
- **SC-009**: A revisão do conjunto simulado encontra 0 dados pessoais reais.
- **SC-010**: Cada uma das 8 perguntas de sucesso da descrição original pode ser
  respondida com "sim" apontando requisitos e cenários desta spec.

## Assumptions

Apenas suposições não institucionais. As regras institucionais em aberto estão em
Decisões Pendentes.

- Os consumidores desta feature são outras funcionalidades do NIAE e quem as desenvolve.
  Não há interface para egressos ou gestores.
- Nesta feature existe uma única fonte ativa, a simulada. A segunda implementação
  exigida por SC-006 serve apenas para verificar a substituibilidade.
- O volume de dados simulados é pequeno, e esta feature não tem metas de desempenho.
- O conjunto simulado é versionado com o projeto e revisável, para permitir SC-009.
- O momento em que a incorporação é disparada (sob demanda, em lote ou por evento) não é
  definido aqui. Basta que a capacidade exista e seja idempotente. A estratégia com a
  fonte real é DP-006.

Decisões de escopo confirmadas pelo solicitante em 2026-09-30 (antes hipóteses H-1 e H-2):

- **Pessoa sem conclusão elegível (antiga H-1)**: não é materializada nesta feature
  (FR-039). A DP-010 foi encerrada como decisão de escopo da Feature 001, não como
  decisão institucional.
- **Nome da Pessoa (antiga H-2, ajustada)**: atributo institucional opcional, apenas de
  apresentação. Não é obrigatório, não identifica, não deduplica e não reconcilia
  (FR-005, FR-031).

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade (NON-NEGOTIABLE)**: a cadeia começa por Pessoa → Conclusão
  Acadêmica. A Conclusão tem identidade estável (FR-008, FR-031) e nada limita futuras
  Participações (FR-038). Formações não são fundidas (FR-014). Não há placeholders das
  etapas seguintes.
- **II — Definição institucional de egresso (NON-NEGOTIABLE)**: só registros declarados
  pela fonte como concluídos viram Conclusão Acadêmica (FR-018, FR-019). O NIAE não
  inventa regra de conclusão (FR-020) e não confunde falha da fonte com ausência de
  conclusão (FR-025).
- **III — Dado institucional não é resposta (NON-NEGOTIABLE)**: todo dado acadêmico é
  institucional e identificável como tal (FR-036). Não há dado declarado nem derivado.
  Ausências não são preenchidas por inferência (FR-010). Divergências não sobrescrevem em
  silêncio (FR-033).
- **IV — Proveniência**: fonte, identificador na fonte e referência temporal da
  obtenção são recuperáveis (FR-035), com nível proporcional e sem linhagem por atributo
  (FR-037).
- **V — Integrações desacopladas (NON-NEGOTIABLE)**: há uma fronteira explícita (FR-021,
  FR-022), a forma canônica é entregue pela implementação da fonte (FR-023) e o mesmo
  contrato vale para simulada e real (FR-024).
- **XI — Identidade única, contexto múltiplo**: a Pessoa não tem atributos acadêmicos
  (FR-003), não é duplicada (FR-004, FR-031) e cada Conclusão conserva seu contexto
  (FR-013). Identificadores de fonte são opacos e potencialmente múltiplos (FR-006).
- **XII — Base institucional central**: Pessoas e Conclusões de todas as unidades
  compõem uma única base. A unidade é atributo da Conclusão, não critério de separação de
  dados. Escopos de acesso por unidade ficam para spec própria.
- **XVI — Privacidade e minimização (NON-NEGOTIABLE)**: só dados fictícios (FR-028),
  nome apenas opcional e sem papel de identidade (FR-005) e nenhuma materialização de
  quem não tem conclusão elegível (FR-039). A base legal para dados reais é DP-009.
- **XXII — Simplicidade/YAGNI**: o contexto é mínimo (FR-012), sem CRUD manual (FR-030),
  sem linhagem nem histórico por atributo (FR-037), sem mecanismo de resolução de
  divergências (FR-033) e sem entidades das features seguintes (FR-038).
- **XXV — Testabilidade independente**: a fonte simulada é determinística (FR-026), com
  cenários documentados (FR-027) e execução sem sistema real (SC-007).
- **XXVI — Testes de invariantes**: SC-001 a SC-006 cobrem Pessoa ↔ Conclusão, múltiplas
  conclusões, não duplicação, elegibilidade, proveniência e contrato da fronteira.
- **XXIX — Hipóteses não viram requisitos (NON-NEGOTIABLE)**: as hipóteses estão
  identificadas (FR-029, FR-033), as decisões de escopo estão marcadas como [Escopo]
  (FR-005, FR-039) e as regras institucionais ficam em Decisões Pendentes.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

Esta feature consome dados de um domínio externo, o sistema acadêmico, sem absorvê-lo.

1. Pertence de fato ao domínio de acompanhamento? Sim. Pessoa e Conclusão Acadêmica
   estão na Fronteira do Domínio do NIAE. O registro acadêmico em si continua externo.
2. É necessária ao ciclo de acompanhamento? Sim. Toda Participação futura depende de uma
   Conclusão Acadêmica identificável (Princípio I).
3. Existe ou está prevista solução institucional mais adequada? Sim, para os dados de
   origem: o sistema acadêmico, cuja integração é DP-001. Por isso o NIAE apenas consome
   esses dados por uma fronteira, e não os mantém manualmente (FR-030).
4. Integração seria suficiente? Sim. É exatamente o que a fronteira modela.
5. A incorporação aumentaria desnecessariamente o acoplamento do núcleo? Não. O núcleo
   depende só do contrato (FR-021 a FR-024).

## Out of Scope *(mandatory)*

- Pesquisa, Versão da Pesquisa, perguntas, respostas, condicionais do questionário,
  editor de pesquisa.
- Migração do instrumento atual, incluindo decidir quais perguntas de Q10–Q19 serão
  removidas, confirmadas ou mantidas.
- Campanha, Participação em Pesquisa, periodicidade, coortes, elegibilidade de campanhas.
- Dados derivados (idade, tempo desde a conclusão, coorte) e dados declarados.
- Forma de ingresso, reserva de vagas e outros atributos acadêmicos além do contexto
  mínimo.
- Consentimento, autenticação, OTP, login, Gov.br, Portal do Egresso.
- Comunicação por e-mail e notificações.
- Dashboard, indicadores, CSV, XLSX, BI, API pública genérica.
- Interface administrativa e cadastro, edição ou exclusão manual de Pessoa ou Conclusão
  Acadêmica.
- Permissões institucionais e perfis de sistema (CPAEG, CSAEG, DIREC etc.).
- Integração real com o Q-Acadêmico ou outra fonte acadêmica.
- Reconciliação de identidade entre fontes distintas.
- Política de correção, divergência e sincronização com a fonte real, que tem aqui
  apenas tratamento provisório. Ficam de fora workflow de resolução, fila ou painel de
  inconsistências, aprovação humana, event sourcing e mecanismo sofisticado de
  sincronização.
- Linhagem genérica de dados, proveniência por atributo e versionamento completo dos
  dados recebidos da fonte.
- CPF, e-mail, data de nascimento, telefone e demais dados pessoais além do nome
  opcional.
- Materialização de pessoas sem conclusão elegível, incluindo estudantes não egressos
  em atividades preparatórias (PAEG, Art. 9º), que dependem de spec própria.
- Importação de respostas históricas do Google Formulários.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

- **DP-001** — DECISÃO PENDENTE: qual será a fonte acadêmica oficial (Q-Acadêmico, outra
  base ou composição de fontes) e qual será o mecanismo institucional de acesso.
  Instância competente: a identificar (Proen, Proex e área de TI institucional).
  Impacto: define a implementação real da fronteira. Tratamento provisório: fonte
  simulada (FR-026); o domínio não depende da escolha (FR-021).
- **DP-002** — DECISÃO PENDENTE: quais identificadores a fonte real fornece para pessoa e
  para conclusão, e se são estáveis ao longo do tempo. Instância competente: a
  identificar, com quem administra a fonte. Impacto: FR-031 depende de identificadores
  estáveis por fonte. Se a fonte real não tiver identificador estável de conclusão, a
  implementação daquela fonte precisará resolver isso sem alterar o contrato.
  Tratamento provisório: identificadores fictícios, opacos e estáveis na fonte simulada.
- **DP-003** — DECISÃO PENDENTE: se haverá resolução ou reconciliação de identidade entre
  fontes distintas e como ela ocorrerá. Instância competente: a identificar. Impacto:
  nenhum nesta feature, que tem fonte única. Tratamento provisório: nenhuma fusão entre
  fontes (FR-034), e o modelo admite várias referências por Pessoa (FR-006).
- **DP-004** — DECISÃO PENDENTE: quais atributos de Q10–Q19 existem com qualidade
  suficiente na fonte real. Instância competente: CPAEG, com as áreas de ensino e quem
  administra a fonte, na spec de migração do instrumento. Impacto: quais atributos do
  contexto mínimo estarão de fato preenchidos. Tratamento provisório: todos opcionais,
  exceto a referência de origem, com "não informado pela fonte" explícito (FR-009,
  FR-010).
- **DP-005** — DECISÃO PENDENTE: política para divergência, inconsistência ou correção de
  dado acadêmico vindo da fonte real. Isso inclui conteúdo alterado, conclusão
  reatribuída, conclusão que deixa de ser reconhecida, registro que deixa de existir e
  data de conclusão inconsistente. Instância competente: a identificar (CPAEG e
  responsáveis pelo registro acadêmico; PAEG Art. 26 para casos omissos). Impacto:
  FR-033. Tratamento provisório: não duplicar, não sobrescrever em silêncio e sinalizar
  a divergência.
- **DP-006** — DECISÃO PENDENTE: estratégia definitiva de atualização e sincronização com
  a fonte real (sob demanda, periódica, por evento). Instância competente: a identificar.
  Impacto: quando a incorporação é disparada. Tratamento provisório: capacidade de
  incorporação idempotente, sem estratégia de disparo definida.
- **DP-007** — DECISÃO PENDENTE: vocabulário canônico de nível, modalidade e forma de
  oferta e sua correspondência com as categorias do instrumento atual. O instrumento
  mistura nível e forma de oferta em Q14 e embute a modalidade no nome do curso
  (inventário, O-13 e O-14). Instância competente: CPAEG, com as áreas de ensino, na spec
  de migração. Impacto: comparabilidade entre conclusões e fontes. Tratamento
  provisório: valores plausíveis na fonte simulada (FR-029), sem lista fechada como regra
  de domínio.
- **DP-008** — DECISÃO PENDENTE: critério operacional que, na fonte real, identifica uma
  formação como concluída nos termos do Art. 3º da PAEG ("efetivamente concluiu os
  requisitos [...] e [...] está apto a receber ou já recebeu o diploma e/ou certificado").
  Instância competente: Proen e registro acadêmico, com a CPAEG (PAEG Art. 26). Impacto:
  FR-018 a FR-020 para a fonte real. Tratamento provisório: na fonte simulada, cada
  registro declara explicitamente sua situação.
- **DP-009** — DECISÃO PENDENTE: base legal, finalidade e retenção do tratamento de dados
  pessoais obtidos da fonte acadêmica real, a começar pelo nome. Instância competente: a
  identificar (encarregado de dados e instâncias institucionais). Impacto: nome opcional
  (FR-005) e qualquer atributo pessoal futuro. Tratamento provisório: apenas dados
  fictícios nesta feature, sem bloqueá-la. Bloqueia o uso de dados reais.

DP-010 (pessoas sem conclusão elegível) foi **encerrada** em 2026-09-30 como decisão de
escopo da Feature 001 (FR-039). Ela não é decisão institucional pendente. Uma feature
futura que precise tratar estudantes ainda não egressos deve abrir sua própria
especificação.


## Nota de revisão pela Feature 019 (2026-10-04)

FR-030 continua vedando cadastro manual. A fonte institucional de acervo histórico entrega Referências de acervo pelo mesmo contrato; Pessoa e Conclusão nascem somente pela incorporação. A validação é um disparo explícito da incorporação (DP-006), sem fundir Pessoas de fontes diferentes.

Referência: [019 — Formação não localizada e validação posterior](../019-formacao-declarada-validacao/spec.md).
