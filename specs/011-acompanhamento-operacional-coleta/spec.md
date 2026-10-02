# Feature Specification: Acompanhamento operacional da coleta

**Feature Branch**: `claude/feature-011-acompanhamento-coleta-20772c`

**Created**: 2026-10-02

**Status**: Approved (consolidado em 2026-10-02)

**Input**: User description: "Feature 011 — Acompanhamento operacional da coleta. Permitir
que operadores institucionais autorizados acompanhem, durante e após uma Campanha,
indicadores operacionais básicos da coleta: população elegível atual, Participações
iniciadas, concluídas e em andamento, taxas operacionais de início e de conclusão, e sua
distribuição em recortes acadêmicos simples já existentes na Conclusão Acadêmica. CPAEG
com visão institucional; CSAEG restrita às unidades de seus vínculos (Feature 010).
Indicadores derivados dos dados transacionais, sem modelos novos, sem migrations, sem
snapshot, sem BI, sem exportação, sem comunicação, sem ranking, sem metas, sem dados
individuais."

## Contexto

As dez primeiras features estabeleceram:

- **001** — **Pessoa → Conclusão Acadêmica**. A Conclusão traz, cada um possivelmente
  não informado: curso, unidade, nível, modalidade, forma de oferta, ano de conclusão (e
  data, quando a fonte fornece). Todos são texto livre da fonte, sem catálogo nem código
  (001 FR-009 a FR-011; DP-007).
- **002/003** — Pesquisa e Versão (RASCUNHO | PUBLICADA); baseline migrada em RASCUNHO.
- **004** — **Campanha**: nome, exatamente uma Versão, período, seis critérios opcionais
  (ano mínimo, ano máximo, unidades, níveis, modalidades, formas de oferta), estado
  derivado **EM PREPARAÇÃO | EM COLETA | ENCERRADA**. A população elegível é **dinâmica**:
  as Conclusões que satisfazem os critérios **no momento da consulta**, nunca congelada nem
  materializada, e **não** é denominador histórico oficial (004 FR-031, FR-032; DP-408).
- **005** — **Participação**: criada explicitamente pela operação "iniciar"
  (Campanha, Conclusão), somente com a Campanha EM COLETA e a Conclusão ELEGÍVEL. No
  máximo uma por par Campanha × Conclusão. Nunca removida, nunca expirada, nunca
  "abandonada". A elegibilidade é verificada só na entrada (DP-507).
- **006** — **conclusão** da Participação: registrada uma única vez, irreversível; sem
  ela, a Participação está em rascunho. Uma Participação pode ser concluída só com a
  resposta "Não" a Q1 (recusa), e o significado disso para indicadores é **006/DP-601**.
- **007** — a entrada do egresso cria a Participação ao ser solicitada, antes de qualquer
  Resposta. Se isso conta como "iniciada" é **007/DP-703**.
- **008/009** — interfaces geradas no servidor, sem JavaScript obrigatório, acessíveis,
  somente no modo de demonstração.
- **010** — **governança**: vínculo de governança (operador, atuação CPAEG | CSAEG,
  unidade, ativo). CPAEG atua no âmbito institucional; CSAEG numa unidade explícita. A 010
  registrou que a 011 seria a primeira superfície por unidade e que ela "DEVE usar a
  unidade do vínculo explicitamente" (010 FR-017; DP-1005).

Até aqui, nenhuma superfície responde:

> **"Como está a coleta desta Campanha?"**

Esta feature introduz essa visão, **operacional e agregada**, para os operadores
institucionais autorizados.

### Princípios desta spec

1. **Calcular, não guardar.** Todo número é derivado, no momento da consulta, de
   Conclusão Acadêmica, Campanha e Participação. Nada novo é persistido.
2. **Denominador atual, não histórico.** A população elegível é sempre apresentada como
   **atual**. A fotografia histórica continua pendente (004/DP-408) e reservada à feature
   de dataset analítico.
3. **Agregado, nunca individual.** Nenhuma Pessoa, Conclusão, Participação ou Resposta
   individual é exposta, nem por drill-down.
4. **Informar, não avaliar.** Sem ranking, meta, semáforo, previsão ou comparação.
5. **Escopo aplicado no servidor.** A unidade do vínculo restringe o que é calculado, não
   apenas o que é mostrado.
6. **Contexto institucional, não resposta declarada.** Todo recorte usa atributos da
   Conclusão Acadêmica.

### Análise normativa

Fonte: PAEG — Resolução CS nº 177/2023, anexo
(`docs/referencias/paeg-resolucao-cs-177-2023-anexo.pdf`).

#### A. Competências previstas pela PAEG relevantes para esta feature

| # | Competência | Artigo |
|---|-------------|--------|
| A1 | **CPAEG**: planejar, organizar, executar e **avaliar** as atividades da PAEG **no âmbito do Ifes** | Art. 21, I |
| A2 | **CPAEG**: desenvolver as atividades **em consonância com as CSAEGs** das unidades | Art. 21, III |
| A3 | **CPAEG**: elaborar o relatório anual de suas atividades e apresentá-lo à Proex | Art. 21, IV |
| A4 | **CSAEG**: planejar, organizar, executar e **avaliar** as atividades da política **nas unidades** | Art. 22, I |
| A5 | **CSAEG**: **aplicar o questionário** de avaliação do egresso e reportar atualizações necessárias à CPAEG | Art. 22, IV |
| A6 | **Proex**: coordenação geral e **monitoramento** da implementação, execução e avaliação; Relatório Anual compilado a partir das CSAEGs | Art. 14 |

**O que a PAEG não diz**: não define indicadores operacionais de coleta, metas de
participação, quem consulta dados individuais, acesso de uma CSAEG a outra unidade,
nem quem cria, abre ou encerra uma rodada de coleta.

#### B. Interpretação operacional adotada por esta feature

Técnica, reversível e localizada (Princípio XXIX). Não cria competência institucional.

| # | Interpretação | Fundamento |
|---|---------------|------------|
| B1 | Acompanhar agregados de andamento da coleta é parte de **executar e avaliar** as atividades da PAEG: no âmbito do Ifes para a CPAEG, na unidade para a CSAEG | A1, A4 |
| B2 | A CSAEG, que **aplica** o questionário na unidade, precisa saber como a coleta avança **na sua unidade** | A5 |
| B3 | A CPAEG, que atua em consonância com as CSAEGs, vê os agregados **de todas as unidades** | A1, A2 |
| B4 | A CSAEG **não** vê agregados de outra unidade: nada na PAEG atribui a uma unidade a avaliação de outra; menor privilégio (Const. XII, XVI) | A4 |
| B5 | Acompanhar **não** inclui gerir Campanha, consultar dados individuais nem comunicar-se com egressos | Ausência de competência expressa; 004/DP-402; 005/DP-505; 004/DP-407 |
| B6 | O monitoramento pela **Proex** (A6) não é representado: a Proex não é atuação no sistema (010/DP-1006) | A6 |

#### C. Decisões institucionais não tomadas aqui

Ver "Decisões Pendentes": quem gere Campanhas (004/DP-402), fotografia da população
(004/DP-408), significado de "iniciada" (007/DP-703), concluída por recusa (006/DP-601),
acesso a dados individuais (005/DP-505), pequenos grupos (DP-1101), coorte (DP-1102),
atuação da Proex (010/DP-1006), identificação produtiva (010/DP-1001).

### Termos usados nesta spec

Os nomes são conceituais; a nomenclatura concreta pertence ao plan.

- **Acompanhamento da coleta** (ou **acompanhamento**): consulta agregada do andamento de
  uma Campanha. Não altera nada.
- **Momento da consulta**: o instante da requisição; para o estado da Campanha, a data
  de referência da 004 (timezone configurada).
- **Escopo de acompanhamento** do operador, derivado dos seus vínculos **ativos**:
  - **institucional**, se houver ao menos um vínculo CPAEG ativo;
  - senão, o **conjunto das unidades** dos seus vínculos CSAEG ativos;
  - senão, **nenhum** (sem acompanhamento).
- **Universo do escopo**: as Conclusões Acadêmicas que o operador pode ver agregadas:
  todas, no escopo institucional; senão, as Conclusões cuja unidade é **igual**, por
  comparação textual exata, a uma das unidades do escopo.
- **Campanha visível**: Campanha que aparece para o operador (FR-020 a FR-023).
- **Indicadores**: os números definidos em FR-030 a FR-039.
- **Recorte**: tabela que distribui os indicadores pelos valores de **um único** atributo
  acadêmico da Conclusão (FR-050 a FR-061).
- **Não informado**: atributo ausente na Conclusão (001 FR-010).

### Decisões desta especificação

Escolhas reversíveis, marcadas **[Hipótese]** ou **[Interpretação B#]** nos requisitos:

1. **Uma capacidade nova, "acompanhar a coleta"**, com semântica explícita por atuação
   (CPAEG ativo → institucional; CSAEG ativo → suas unidades; sem vínculo ativo → não),
   com escopo derivado dos vínculos (FR-010 a FR-016). Nenhum modelo de papel, permissão
   ou escopo.
2. **Indicadores com definição fixa** (FR-030 a FR-039), contando **Conclusões
   Acadêmicas e Participações**, nunca Pessoas.
3. **"Iniciadas" é o fato do domínio: Participação existente.** Inclui Participações
   ainda sem Resposta. Isso é tratamento operacional provisório e explícito, não decisão
   de 007/DP-703 (FR-032).
4. **"Concluídas" inclui conclusões por recusa (Q1 = "Não")**, porque distingui-las
   exigiria ler Respostas. 006/DP-601 permanece aberta (FR-033).
5. **Numerador e denominador são calculados com regras diferentes e isso é declarado**:
   iniciadas e concluídas não são filtradas pela elegibilidade atual; por isso uma taxa
   pode, em situação hoje impossível, passar de 100% (FR-038; 005/DP-507).
6. **Seis recortes de uma dimensão**: unidade, curso (por unidade), nível, modalidade,
   forma de oferta e ano de conclusão. Um por vez. Sem combinação livre (FR-050 a FR-061).
7. **"Ano de conclusão", não "coorte"** (DP-1102).
8. **Duas telas**: lista de Campanhas e detalhe operacional da Campanha, com um recorte
   selecionável por vez (seção "Telas e estados").
9. **Somente no modo de demonstração**, como o editor, enquanto a identificação produtiva
   de operadores estiver pendente (010/DP-1001).
10. **Zero modelos, zero migrations** (seção "Análise de persistência").

## Clarifications

### Session 2026-10-02

Decisões consolidadas pelo solicitante na aprovação da spec, antes do plan. Deixam de ser
hipóteses e passam a ser decisões desta feature.

- Q: As taxas usam Participações filtradas pela elegibilidade atual? → A: **Não.**
  Elegíveis atuais vêm da 004; iniciadas são as Participações existentes; concluídas são
  as Participações concluídas pela 006. Nada é filtrado retroativamente para manter a taxa
  ≤ 100%. Num cenário futuro de correção acadêmica, a taxa pode passar de 100% e NÃO DEVE
  ser truncada, corrigida, tratada como erro nem motivar snapshot. A interface deixa claro
  que o denominador é a **população elegível atual**. A reconciliação histórica pertence à
  Feature 012. Hoje, pela 001, o cenário não ocorre, e nenhuma infraestrutura é criada
  para ele (nem detecção, nem nota condicional). (FR-035, FR-038)
- Q: Qual é a chave do recorte por curso? → A: **(unidade, curso)**, enquanto não houver
  identificador institucional de Curso. Sem modelo, catálogo, código sintético,
  normalização ou identidade de curso. Na visão institucional, a unidade aparece para
  desambiguar; na visão de uma única unidade, PODE ser omitida da apresentação. (FR-050,
  FR-051)
- Q: CSAEG vê Campanha com Versão em RASCUNHO? → A: **A Campanha, sim; o rascunho, não.**
  O instrumento aparece apenas como "Instrumento ainda não publicado": sem nome ou
  designação da Versão, sem link, estrutura, diagnóstico ou qualquer conteúdo do
  rascunho. Não concede acesso ao rascunho nem altera a autorização da 010. (FR-042)
- Q: "Não iniciadas" entra? → A: **Não, fora do MVP.** O número seria derivável dos
  agregados (elegíveis atuais − iniciadas); fica fora apenas porque não é necessário às
  perguntas centrais da 011 e não se quer ampliar o conjunto de indicadores agora.
- Q: Como expressar a regra de acompanhamento? → A: **Uma regra concreta**, equivalente a
  "pode acompanhar a coleta", com semântica explícita por atuação: vínculo CPAEG ativo →
  acompanha no âmbito institucional; vínculo CSAEG ativo → acompanha dentro de suas
  unidades; sem vínculo ativo → não acompanha. NÃO DEVE ser modelada como "qualquer
  vínculo, presente ou futuro, concede acompanhamento". Sem Permission, registro de
  capacidades, RolePermission ou motor de políticas; a 010 continua com papéis fixos.
  (FR-011, FR-012)
- **Não é necessário `/speckit-clarify`.**

Ajustes consolidados na aprovação do plan:

- Q: O número de consultas é requisito? → A: **Não.** A prioridade é reutilizar
  exatamente a elegibilidade da 004, não carregar objetos desnecessários, não consultar
  por linha de recorte e não ler Resposta. Uma consulta proporcional ao número de
  Campanhas na lista é aceitável. Orçamentos de consultas são só proteção contra
  regressão do desenho. (FR-072)
- Q: O operador fictício B pode mudar de unidade para a demonstração? → A: **Não.** A, B
  (CSAEG Vitória) e C da 010 são preservados; a 011 acrescenta cenário fictício próprio.
  (FR-142)
- Q: Qual é o contrato público de elegibilidade da 004? → A: o **menor contrato
  semanticamente correto**, que expresse "a população atualmente elegível desta
  Campanha", sem duplicar a regra e sem expor detalhe interno para otimização. A 004
  continua dona da pergunta "esta Conclusão pertence à população atual desta Campanha?".
  (FR-030, FR-140)

## User Scenarios & Testing *(mandatory)*

Atores (todos fictícios nos cenários):

- **Operador CPAEG**: vínculo ativo CPAEG; escopo institucional.
- **Operador CSAEG**: vínculo(s) ativo(s) CSAEG; escopo das unidades dos vínculos.
- **Operador sem vínculo ativo**: identificado, sem atuação.
- **Pessoa não identificada**: requisição sem operador.

Dados de referência usados nos cenários (fictícios):

- Unidades presentes nas Conclusões: **Serra**, **Vitória**, **Cefor**, e algumas
  Conclusões **sem unidade informada**.
- **Campanha I** (institucional): sem critério de unidade; EM COLETA.
- **Campanha R** (restrita): critério de unidades {Serra, Cefor}; EM COLETA.
- **Campanha P**: EM PREPARAÇÃO, nunca aberta.
- **Campanha E**: ENCERRADA após abertura.

### User Story 1 - Operador CPAEG vê as Campanhas e seu andamento institucional (Priority: P1)

O operador CPAEG abre o acompanhamento da coleta e vê todas as Campanhas, em qualquer
estado, cada uma com: nome, instrumento aplicado (Pesquisa e Versão), período, situação
(EM PREPARAÇÃO, EM COLETA, ENCERRADA), elegíveis atuais, iniciadas e concluídas, no
âmbito institucional.

**Why this priority**: é a resposta mínima a "como está a coleta?" para quem planeja e
avalia a PAEG no âmbito do Ifes [PAEG Art. 21, I; Interpretação B1, B3].

**Independent Test**: com os dados de referência e operador CPAEG, abrir a lista e
conferir, para cada Campanha, os três números com contagem manual sobre os dados.

**Acceptance Scenarios**:

1. **Given** operador CPAEG e as Campanhas I, R, P e E, **When** abre a lista, **Then** vê
   as quatro, cada uma com nome, Pesquisa e Versão, período, situação, elegíveis atuais,
   iniciadas e concluídas.
2. **Given** a Campanha I com 40 Conclusões elegíveis no momento, 12 Participações, 5
   delas concluídas, **When** a lista é aberta, **Then** a linha de I mostra 40, 12 e 5.
3. **Given** a lista, **When** é lida, **Then** não mostra taxa, meta, cor de desempenho,
   posição, destaque de "melhor" ou "pior", nem ordenação por indicador.
4. **Given** uma Campanha sem período definido, **When** listada, **Then** o período
   aparece como "não definido".
5. **Given** a lista, **When** é aberta, **Then** informa que os números foram calculados
   no momento da consulta e que "elegíveis" é a população **atual**.

---

### User Story 2 - Operador CPAEG abre uma Campanha e vê os indicadores operacionais (Priority: P1)

Ao abrir uma Campanha, o operador CPAEG vê o instrumento aplicado, o período, a situação
e os indicadores: elegíveis atuais, iniciadas, concluídas, em andamento, taxa de início
e taxa de conclusão, com as definições de cada um em linguagem operacional.

**Why this priority**: é a pergunta central da feature [PAEG Art. 21, I; Const. XIX].

**Independent Test**: com operador CPAEG, abrir a Campanha I e conferir os seis valores
contra cálculo manual; repetir com a Campanha sem Participações e com elegíveis = 0.

**Acceptance Scenarios**:

1. **Given** a Campanha I com 40 elegíveis atuais, 12 iniciadas e 5 concluídas, **When**
   o detalhe é aberto, **Then** mostra: elegíveis atuais 40; iniciadas 12; concluídas 5;
   em andamento 7; taxa de início 30,0%; taxa de conclusão 12,5%.
2. **Given** qualquer Campanha, **When** o detalhe é aberto, **Then** cada indicador vem
   acompanhado de sua definição curta (por exemplo, "Concluídas: Participações com
   conclusão registrada").
3. **Given** uma Campanha sem nenhuma Participação (caso H), **When** o detalhe é aberto,
   **Then** iniciadas, concluídas e em andamento são 0 e as taxas são 0,0% se houver
   elegíveis.
4. **Given** uma Campanha com elegíveis atuais = 0 (caso I), **When** o detalhe é aberto,
   **Then** as duas taxas aparecem como "—", com a explicação "não se aplica: nenhuma
   formação elegível no momento", sem erro, "NaN", "∞" ou 0%.
5. **Given** uma Campanha com Participações iniciadas e nenhuma concluída (caso J),
   **When** o detalhe é aberto, **Then** concluídas é 0, em andamento é igual a iniciadas
   e nenhuma Participação é chamada de abandonada, expirada ou desistente.
6. **Given** o detalhe, **When** é lido, **Then** informa que as contagens são de
   formações concluídas (Conclusões Acadêmicas), e não de pessoas: uma pessoa com duas
   formações elegíveis conta duas vezes.

---

### User Story 3 - Operador CSAEG vê somente Campanhas relevantes para sua unidade (Priority: P1)

O operador CSAEG vê na lista somente as Campanhas que não restringem unidades ou cujo
critério de unidades inclui alguma unidade do seu escopo. A Campanha não desaparece
quando o número de elegíveis da unidade é zero.

**Why this priority**: é o primeiro consumidor concreto do escopo de unidade da 010 (010
FR-017) [PAEG Art. 22, I, IV; Interpretação B2, B4].

**Independent Test**: com operadores CSAEG de Serra, de Vitória e sem unidade
correspondente a nenhuma Conclusão, abrir a lista e conferir quais Campanhas aparecem.

**Acceptance Scenarios**:

1. **Given** operador CSAEG da unidade Vitória (caso E), **When** abre a lista, **Then** vê
   I, P e E (se não restringem unidades) e **não** vê R, restrita a {Serra, Cefor}.
2. **Given** operador CSAEG da unidade Serra (caso D), **When** abre a lista, **Then** vê
   I e R.
3. **Given** uma Campanha restrita a {Serra} e nenhuma Conclusão de Serra elegível no
   momento, **When** o operador CSAEG de Serra abre a lista, **Then** a Campanha aparece,
   com elegíveis atuais 0.
4. **Given** uma Campanha sem critério de unidade mas restrita a um nível, **When** um
   operador CSAEG de qualquer unidade abre a lista, **Then** ela aparece; a relevância
   depende só do critério de unidade.
5. **Given** um vínculo CSAEG cuja unidade está escrita de forma diferente da Campanha
   (por exemplo, "Campus Serra" × "Serra"), **When** a lista é aberta, **Then** a Campanha
   restrita a "Serra" não aparece: não há normalização (004 FR-022; 010/DP-1005).

---

### User Story 4 - Operador CSAEG vê somente agregados da sua unidade (Priority: P1)

Para o operador CSAEG, todo número — na lista, no detalhe e nos recortes — é calculado
somente sobre Conclusões das unidades do seu escopo e sobre Participações dessas
Conclusões.

**Why this priority**: sem isso, o escopo seria só aparência [Const. XII, XVI;
Interpretação B4].

**Independent Test**: com a Campanha I (Serra 20, Vitória 15, Cefor 3, sem unidade 2
elegíveis), comparar os números vistos por CPAEG e por CSAEG de Vitória.

**Acceptance Scenarios**:

1. **Given** a Campanha I e operador CSAEG de Vitória, **When** abre o detalhe, **Then**
   elegíveis atuais = 15, e iniciadas, concluídas e em andamento contam só Participações
   de Conclusões de Vitória.
2. **Given** o mesmo operador, **When** abre qualquer recorte, **Then** nenhuma linha,
   total ou valor de outra unidade aparece, nem a linha "unidade não informada".
3. **Given** o mesmo operador, **When** se inspeciona o cálculo, **Then** ele foi restrito
   às unidades do escopo antes de contar; nenhum valor de outra unidade foi calculado e
   escondido na apresentação (FR-071).
4. **Given** operador CSAEG de unidade única, **When** abre o detalhe, **Then** o recorte
   "por unidade" não é oferecido como opção (seria uma linha só).

---

### User Story 5 - URL direta não permite acesso fora do escopo (Priority: P1)

Conhecer o endereço de uma Campanha, de um recorte ou de qualquer página do
acompanhamento não dá acesso a nada fora do escopo do operador.

**Why this priority**: a proteção é a verificação no servidor, não a ausência de link
(caso N) [Const. XVI; 010 FR-041].

**Independent Test**: com operador CSAEG de Vitória, solicitar diretamente o detalhe da
Campanha R e cada recorte dela; com operador sem vínculo e sem identificação, solicitar
todas as páginas.

**Acceptance Scenarios**:

1. **Given** operador CSAEG de Vitória, **When** solicita diretamente o detalhe da
   Campanha R, **Then** recebe recusa de acesso, sem nome, período, instrumento ou número
   da Campanha.
2. **Given** o mesmo operador, **When** solicita diretamente um recorte da Campanha R,
   **Then** recebe a mesma recusa.
3. **Given** operador sem vínculo ativo, **When** solicita qualquer página do
   acompanhamento, **Then** recebe recusa "sem atuação institucional ativa".
4. **Given** nenhuma identificação no modo de demonstração, **When** solicita qualquer
   página do acompanhamento, **Then** é levado à escolha de operador fictício, sem ver
   conteúdo.
5. **Given** o modo de demonstração desligado, **When** qualquer página do acompanhamento
   é solicitada, **Then** nada responde (como na 008, 009 e 010).
6. **Given** operador CSAEG de Vitória e um identificador de Campanha inexistente,
   **When** o solicita, **Then** a resposta é "inexistente"; a verificação de vínculo
   ocorre antes.

---

### User Story 6 - Indicadores derivados, não persistidos (Priority: P1)

Nenhum indicador, contagem, taxa, população, recorte ou momento de cálculo é gravado. Abrir
o acompanhamento não altera Campanha, Conclusão, Participação, Resposta nem vínculo.
Uma mudança nos dados transacionais aparece na consulta seguinte.

**Why this priority**: é o princípio estrutural da feature e a proteção contra snapshot
implícito (004 FR-032; Const. XXII).

**Independent Test**: medir as estruturas persistidas antes e depois; consultar,
iniciar uma Participação pelas operações da 005, consultar de novo e ver a diferença; ver
que nenhuma Resposta foi lida no cálculo.

**Acceptance Scenarios**:

1. **Given** o banco antes e depois de abrir lista, detalhe e todos os recortes, **When**
   são comparados, **Then** são idênticos.
2. **Given** um detalhe consultado, **When** uma nova Conclusão elegível é incorporada e
   a página é consultada de novo, **Then** elegíveis atuais aumenta em 1.
3. **Given** um detalhe consultado, **When** uma Participação é concluída pelas operações
   da 006 e a página é consultada de novo, **Then** concluídas aumenta em 1 e em andamento
   diminui em 1.
4. **Given** o cálculo de qualquer indicador ou recorte, **When** é inspecionado, **Then**
   não lê Resposta nem seleção de Opção.
5. **Given** a feature implementada, **When** as estruturas persistidas são listadas,
   **Then** não há modelo, tabela, coluna nem migration nova.

---

### User Story 7 - Recorte por unidade para CPAEG (Priority: P2)

O operador CPAEG vê, numa Campanha, uma tabela por unidade: Unidade | Elegíveis atuais |
Iniciadas | Concluídas | Taxa de conclusão.

**Why this priority**: a CPAEG atua em consonância com as CSAEGs (Art. 21, III) e precisa
ver a distribuição entre unidades; depende das histórias P1.

**Independent Test**: com a Campanha I e a Campanha R, conferir linhas, valores e soma.

**Acceptance Scenarios**:

1. **Given** a Campanha I, **When** o recorte por unidade é aberto, **Then** há uma linha
   por unidade que aparece nas Conclusões elegíveis ou nas Participações (Serra, Vitória,
   Cefor) e uma linha "Unidade não informada", e a soma das linhas é igual aos totais do
   detalhe.
2. **Given** a Campanha R, restrita a {Serra, Cefor}, e nenhuma Conclusão elegível de
   Cefor no momento, **When** o recorte é aberto, **Then** Cefor aparece com 0 e "—",
   porque é unidade do critério da Campanha.
3. **Given** o recorte, **When** é lido, **Then** as linhas estão em ordem alfabética da
   designação, com "não informada" por último, e nunca ordenadas por indicador.
4. **Given** o recorte, **When** é lido, **Then** não há posição, destaque, cor, ícone ou
   texto de desempenho.

---

### User Story 8 - Recorte por curso dentro do escopo autorizado (Priority: P2)

O operador vê uma tabela por curso: Unidade | Curso | Elegíveis atuais | Iniciadas |
Concluídas | Taxa de conclusão. Cada linha é um curso **numa unidade**: o mesmo nome de
curso em unidades diferentes forma linhas diferentes.

**Why this priority**: o curso é o recorte mais útil para a CSAEG aplicar o questionário
na unidade; depende das histórias P1.

**Independent Test**: com dois cursos de mesmo nome em Serra e Vitória e um curso não
informado, conferir linhas para CPAEG e para CSAEG de Serra.

**Acceptance Scenarios**:

1. **Given** "Técnico em Informática" em Serra e em Vitória, **When** o CPAEG abre o
   recorte por curso, **Then** há duas linhas distintas, uma por unidade.
2. **Given** o operador CSAEG de Serra, **When** abre o recorte por curso, **Then** vê
   somente cursos de Serra.
3. **Given** Conclusões elegíveis sem curso informado (caso M), **When** o recorte é
   aberto, **Then** aparecem numa linha "Curso não informado" da respectiva unidade; o
   curso não é deduzido de nenhum outro dado.
4. **Given** o recorte, **When** é lido, **Then** a soma das linhas é igual aos totais do
   detalhe no escopo do operador.

---

### User Story 9 - Recortes adicionais já sustentados pela Conclusão Acadêmica (Priority: P2)

O operador pode ver, um de cada vez, os recortes por nível, modalidade, forma de oferta e
ano de conclusão, todos lidos da Conclusão Acadêmica, com a mesma estrutura de tabela.

**Why this priority**: esses atributos já existem e são os mesmos dos critérios da 004;
dependem das histórias P1.

**Independent Test**: para cada recorte, conferir linhas, linha "não informado" e soma.

**Acceptance Scenarios**:

1. **Given** a Campanha I, **When** o recorte por nível é aberto, **Then** há uma linha
   por valor de nível registrado nas Conclusões (como escrito na fonte) e uma linha "Nível
   não informado", se houver.
2. **Given** uma Conclusão com nível institucional "Graduação" e uma Resposta à Q14 com
   outro valor, **When** o recorte por nível é aberto, **Then** a Conclusão conta em
   "Graduação"; a Q14 não é lida (ADR 0003).
3. **Given** o recorte por ano de conclusão, **When** é aberto, **Then** as linhas estão
   em ordem crescente de ano, com "Ano não informado" por último, e o recorte se chama
   "Ano de conclusão", não "coorte".
4. **Given** qualquer recorte, **When** é aberto, **Then** indica que os valores vêm do
   registro acadêmico institucional.
5. **Given** um pedido de recorte por dimensão que não está na lista fixa, ou de dois
   atributos combinados, **When** é feito, **Then** não é atendido.

---

### User Story 10 - Campanha encerrada permanece consultável com aviso de população atual (Priority: P2)

Uma Campanha ENCERRADA continua na lista e no detalhe. A página avisa que "elegíveis
atuais" é calculado com os dados acadêmicos de hoje e pode diferir da população existente
na data de encerramento.

**Why this priority**: o acompanhamento serve também depois da coleta, mas o denominador
não pode parecer histórico (004/DP-408); depende das histórias P1.

**Independent Test**: encerrar uma Campanha, incorporar uma nova Conclusão elegível e
verificar que elegíveis atuais muda, com o aviso presente.

**Acceptance Scenarios**:

1. **Given** a Campanha E, **When** o detalhe é aberto, **Then** mostra o encerramento
   (data e forma: antecipado ou fim do período) e o aviso de que a população elegível é
   a atual, não a da data de encerramento.
2. **Given** a Campanha E e uma Conclusão elegível incorporada depois do encerramento,
   **When** o detalhe é consultado, **Then** elegíveis atuais inclui essa Conclusão, as
   taxas mudam e o aviso continua presente.
3. **Given** a Campanha E com Participações em rascunho, **When** o detalhe é aberto,
   **Then** elas são apresentadas como "iniciadas e não concluídas", com a observação de
   que a coleta foi encerrada; nunca como "abandonadas", "expiradas" ou "desistências".
4. **Given** uma Campanha ENCERRADA que nunca foi aberta, **When** o detalhe é aberto,
   **Then** a página informa que ela não chegou a entrar em coleta.

---

### User Story 11 - Campanha em preparação e em coleta (Priority: P2)

Uma Campanha EM PREPARAÇÃO aparece com a indicação de que a coleta ainda não começou; os
números seguem os dados reais. Uma Campanha EM COLETA informa que os números
correspondem ao estado atual.

**Why this priority**: evita leitura equivocada de zeros e de números em movimento;
depende das histórias P1.

**Independent Test**: abrir a Campanha P e a Campanha I e conferir avisos e números.

**Acceptance Scenarios**:

1. **Given** a Campanha P com 30 Conclusões elegíveis, **When** o detalhe é aberto,
   **Then** mostra "A coleta ainda não começou", elegíveis atuais 30 e iniciadas e
   concluídas 0.
2. **Given** a Campanha P com Versão em RASCUNHO e operador CSAEG, **When** o detalhe é
   aberto, **Then** o instrumento é apresentado como "Instrumento ainda não publicado", sem a
   designação nem o conteúdo da Versão (010 FR-036).
3. **Given** a Campanha I, **When** o detalhe é aberto, **Then** informa que os números
   correspondem aos dados no momento da consulta e mostra esse momento; nada é gravado.

---

### User Story 12 - Múltiplos vínculos (Priority: P2)

O escopo de acompanhamento combina os vínculos ativos do operador sem escolha de perfil:
CPAEG ativo concede visão institucional; vários CSAEG somam unidades.

**Why this priority**: casos F e G; segue a união de capacidades da 010 (010 FR-021).

**Independent Test**: operador com CSAEG Serra + CSAEG Vitória; operador com CPAEG + CSAEG
Serra; desativar vínculos e consultar de novo.

**Acceptance Scenarios**:

1. **Given** operador com CSAEG Serra e CSAEG Vitória ativos (caso F), **When** abre a
   lista, **Then** vê as Campanhas relevantes para Serra **ou** Vitória, e os números
   somam Serra e Vitória.
2. **Given** o mesmo operador e uma Campanha restrita a {Serra}, **When** abre o detalhe,
   **Then** vê só os números de Serra; o recorte por unidade mostra Serra (e não Vitória,
   que não é unidade da Campanha).
3. **Given** operador com CPAEG e CSAEG Serra ativos (caso G), **When** abre o
   acompanhamento, **Then** tem visão institucional completa, sem escolher papel.
4. **Given** o operador do cenário 3, **When** o vínculo CPAEG é desativado, **Then** na
   requisição seguinte passa a ver somente Serra.
5. **Given** operador com vínculo CSAEG inativo e nenhum outro, **When** abre o
   acompanhamento, **Then** recebe recusa "sem atuação institucional ativa".

---

### User Story 13 - Refinamentos de responsividade e acessibilidade (Priority: P3)

Lista, detalhe e recortes são compreensíveis por teclado, leitor de tela e em tela de
320 px, sem JavaScript e sem depender de cor.

**Why this priority**: acessibilidade é requisito (Const. XX, XXI); a base já decorre das
convenções da 008–010; esta história trata dos detalhes de tabela.

**Independent Test**: navegar por teclado e leitor de tela; abrir em 320 px e zoom de
200%; desligar JavaScript.

**Acceptance Scenarios**:

1. **Given** uma tabela de recorte, **When** lida por leitor de tela, **Then** tem legenda,
   cabeçalhos de coluna e de linha associados, e cada célula é anunciada com seu
   cabeçalho.
2. **Given** tela de 320 px, **When** a lista e um recorte com cinco colunas são abertos,
   **Then** o conteúdo é legível sem rolagem horizontal da página.
3. **Given** uma taxa "—", **When** lida por leitor de tela, **Then** é anunciada como
   "não se aplica", e não como traço.
4. **Given** uma barra de progresso, se existir, **When** a página é lida sem cor ou sem
   a barra, **Then** o número e o percentual continuam escritos.
5. **Given** JavaScript desligado, **When** o operador troca de recorte, **Then** a troca
   funciona por link ou formulário comum.

---

### Cenários ponta a ponta *(mandatory para esta feature)*

Correspondem aos casos A a N da solicitação.

| Caso | Situação | Resultado esperado | Histórias |
|------|----------|--------------------|-----------|
| A | Campanha institucional em coleta com várias unidades | CPAEG vê totais institucionais e recorte por unidade com todas as unidades presentes e "não informada" | US1, US2, US7 |
| B | Campanha restrita a determinadas unidades | Recorte por unidade mostra as unidades do critério, inclusive com 0 | US7 |
| C | CPAEG consultando a visão institucional | Lista com todas as Campanhas; detalhe e recortes sem restrição de unidade | US1, US2 |
| D | CSAEG de unidade incluída na Campanha | Campanha visível; números só da unidade | US3, US4 |
| E | CSAEG de unidade não incluída na Campanha | Campanha não aparece; URL direta → recusa | US3, US5 |
| F | Operador com dois vínculos CSAEG | União das unidades; Campanhas relevantes a qualquer delas | US12 |
| G | Operador com CPAEG + CSAEG | Visão institucional, sem escolha de papel | US12 |
| H | Campanha sem Participações | Iniciadas, concluídas, em andamento = 0; taxas 0,0% se há elegíveis | US2 |
| I | Elegíveis atuais = 0 | Taxas "—" com "não se aplica"; Campanha continua visível | US2, US3 |
| J | Iniciadas e nenhuma concluída | Concluídas 0; em andamento = iniciadas; sem "abandono" | US2 |
| K | Participações concluídas | Concluídas contadas pela conclusão registrada (006), inclusive por recusa (DP-601) | US2, US6 |
| L | Campanha encerrada | Consultável; aviso de população atual; "iniciadas e não concluídas" | US10 |
| M | Conclusão com atributo acadêmico ausente | Linha "não informado" no recorte correspondente; sem inferência; fora do universo de CSAEG quando a unidade é ausente | US8, US9, US4 |
| N | Tentativa direta de abrir Campanha fora do escopo | Recusa, sem dado da Campanha | US5 |

Roteiro único de demonstração:

1. Ligar o modo de demonstração e preparar os dados locais.
2. Abrir o acompanhamento sem operador → levado à escolha de operador fictício.
3. Escolher o operador sem vínculo → recusa.
4. Escolher o operador CPAEG → lista com todas as Campanhas; abrir uma; ver recortes por
   unidade e por curso.
5. Escolher o operador CSAEG → só Campanhas relevantes à sua unidade; números só da
   unidade; abrir por endereço uma Campanha fora do escopo → recusa.
6. Iniciar e concluir uma Participação pela jornada da 008 → consultar de novo e ver os
   números mudarem.
7. Desligar o modo → nada responde.

### Telas e estados

Duas telas novas, mais a recusa:

- **Lista de Campanhas do acompanhamento**: uma linha por Campanha visível, com nome,
  Pesquisa e Versão, período, situação, elegíveis atuais, iniciadas e concluídas. Texto
  permanente: números calculados no momento da consulta; elegíveis é a população atual.
  Lista vazia: "Nenhuma Campanha no escopo da sua atuação".
- **Detalhe operacional da Campanha**:
  - cabeçalho: nome, instrumento aplicado, período, situação, abertura e encerramento
    quando houver, e o aviso pertinente ao estado (FR-043 a FR-046);
  - **resumo**: elegíveis atuais, iniciadas, concluídas, em andamento, taxa de início,
    taxa de conclusão, cada um com definição curta;
  - **recorte**: escolha, por links comuns, de **um** recorte entre os oferecidos ao
    operador, e a tabela correspondente. Recorte inicial: por unidade, quando oferecido;
    senão, por curso.
- **Recusa de acesso**: mesma natureza da 010 (título, explicação operacional, caminho de
  volta). Variantes: sem atuação ativa; Campanha fora do escopo de acompanhamento.
- **Contexto de atuação e aviso de ambiente não produtivo**: como no editor da 010.

Não há tela de gestão de Campanha, de lista de egressos, de respostas, de exportação nem
de configuração do painel.

### Edge Cases

- **Participação de Conclusão que deixou de ser elegível** (hoje impossível, pois a 001
  não altera Conclusões; possível se 001/DP-005 adotar correção): continua contada em
  iniciadas e concluídas, na unidade atual da Conclusão; a taxa pode passar de 100% e é
  mostrada como calculada, sem truncar nem corrigir; o denominador é rotulado como
  população elegível atual (FR-038; 005/DP-507).
- **Conclusão sem unidade**: entra nos totais e na linha "Unidade não informada" para
  CPAEG; não pertence ao universo de nenhuma CSAEG (FR-015). A quem cabe acompanhá-la
  segue 004/DP-409 e 001/DP-004.
- **Vínculo CSAEG cuja unidade não aparece em nenhuma Conclusão**: o operador vê as
  Campanhas sem critério de unidade, com zeros; nada é inferido (010/DP-1005).
- **Campanha restrita a unidade sem Conclusões** (por exemplo, grafia diferente): visível
  à CSAEG dessa unidade, com zeros; o recorte por unidade do CPAEG mostra a linha com 0.
- **Duas Campanhas EM COLETA com populações sobrepostas**: cada uma tem seus indicadores;
  a mesma Conclusão conta em ambas; nada é somado entre Campanhas (004/DP-404).
- **Pessoa com várias Conclusões elegíveis na mesma Campanha**: cada Conclusão conta uma
  vez; a contagem não é de Pessoas (004 FR-033; 005/DP-501).
- **Participação criada na entrada e sem nenhuma Resposta**: conta como iniciada e em
  andamento (FR-032; 007/DP-703).
- **Participação concluída por recusa (Q1 = "Não")**: conta como concluída (FR-033;
  006/DP-601).
- **Campanha sem período definido**: período "não definido"; estado EM PREPARAÇÃO.
- **Campanha nunca aberta e ENCERRADA pelo tempo**: aparece, com a informação de que não
  chegou a entrar em coleta; números seguem os dados (iniciadas = 0).
- **Campanha removida durante a preparação** (004 FR-044): deixa de aparecer; um
  endereço antigo responde "inexistente".
- **Campanha com Versão em RASCUNHO** (só possível nunca aberta): para quem não consulta
  rascunhos, "Instrumento ainda não publicado", sem designação nem link (FR-042).
- **Valores de atributo com grafia variada** ("Graduação" e "graduação"): linhas
  distintas, sem normalização (001/DP-007).
- **Campanha aberta durante a consulta** ou Participação criada entre duas consultas: a
  consulta seguinte reflete o novo estado; não há atualização automática da página.
- **Arredondamento**: duas taxas diferentes podem aparecer iguais depois de arredondadas;
  os números absolutos sempre ficam ao lado (FR-037).
- **Grupos muito pequenos** (por exemplo, curso com 1 elegível e 1 concluída): exibidos
  como qualquer linha; o risco é registrado em DP-1101, sem supressão nesta feature.
- **Recorte solicitado que não é oferecido ao operador** (por exemplo, por unidade, para
  CSAEG de unidade única): se solicitado por endereço, PODE ser apresentado, pois contém
  só dados do escopo; nunca amplia o escopo.

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII):

- **[PAEG Art. n]**: decorre da PAEG (Análise normativa, A).
- **[Interpretação Bn]**: interpretação operacional da categoria B.
- **[Const. — n]**: decorre da Constituição.
- **[00n]**: decorre de feature anterior.
- **[Arquitetura]**: decisão arquitetural.
- **[Hipótese]**: escolha de produto reversível.
- **[Escopo]**: delimitação desta feature.

Nenhum requisito é **[Herdado]** do formulário: o instrumento atual não tem acompanhamento
da coleta.

### Functional Requirements

**Natureza da feature**

- **FR-001**: O acompanhamento DEVE ser somente leitura. Nenhuma página, consulta ou
  cálculo DEVE criar, alterar ou remover Campanha, Conclusão, Pessoa, Participação,
  Resposta, Versão ou vínculo. [Const. — XIX; Escopo]
- **FR-002**: O acompanhamento DEVE ser agregado: somente contagens e taxas, nunca
  registros individuais (FR-080 a FR-084). [Const. — XVI]
- **FR-003**: O acompanhamento NÃO DEVE ser apresentado como relatório estatístico
  oficial, dataset analítico, indicador da PAEG (Art. 10, III) ou Relatório Anual
  (Art. 14). Ele informa o andamento da coleta. [Const. — XIX; Escopo]

**Capacidade e escopo de acompanhamento**

- **FR-010**: DEVE existir exatamente uma capacidade nova, **acompanhar a coleta**,
  expressa como regra fixa e nomeada sobre os vínculos ativos do operador, no mesmo
  padrão das três regras da 010 (010 FR-034). NÃO DEVE ser criado modelo de permissão,
  papel, escopo, organização, ACL, motor de políticas nem configuração por ambiente.
  [Const. — XXII; 010 FR-025, FR-034]
- **FR-011**: A capacidade **acompanhar a coleta** DEVE ter semântica explícita por
  atuação: vínculo **CPAEG** ativo → acompanha no âmbito institucional; vínculo **CSAEG**
  ativo → acompanha dentro de suas unidades; sem vínculo ativo (nenhum ou só inativos)
  → não acompanha. A regra DEVE nomear as duas atuações; NÃO DEVE conceder
  acompanhamento a "qualquer vínculo", de modo que uma atuação futura não o receba
  implicitamente. [PAEG Art. 21, I; Art. 22, I, IV; Interpretação B1, B2; Clarifications
  2026-10-02]
- **FR-012**: O **escopo de acompanhamento** DEVE ser derivado dos vínculos ativos, a
  cada requisição:
  - (a) existindo ao menos um vínculo **CPAEG** ativo → **institucional**;
  - (b) senão, existindo vínculos **CSAEG** ativos → o **conjunto das unidades** desses
    vínculos (a união);
  - (c) senão → nenhum, e o acompanhamento é recusado.

  [PAEG Art. 21, I; Art. 22, I; Interpretação B3, B4; 010 FR-021]
- **FR-013**: NÃO DEVE existir seleção de "perfil atual", "papel ativo", "unidade ativa"
  nem precedência configurável. A precedência de (a) sobre (b) é fixa: CPAEG concede
  visão institucional, que contém as unidades. [010 FR-021; Const. — XXII]
- **FR-014**: Vínculos CSAEG de várias unidades NÃO DEVEM conceder visão institucional:
  apenas somam unidades. [010 US8.3; Const. — XII]
- **FR-015**: O **universo do escopo** DEVE ser: no escopo institucional, todas as
  Conclusões Acadêmicas; no escopo de unidades, as Conclusões cuja unidade é **igual**,
  por comparação textual exata, a uma das unidades do escopo. Conclusão sem unidade
  informada NÃO DEVE pertencer ao universo de nenhuma CSAEG. [004 FR-022; 010 FR-015;
  Const. — III, XXIX; DP-1005]
- **FR-016**: Esta capacidade NÃO DEVE conceder gestão de Campanha, acesso a dado
  individual, acesso a Resposta, comunicação com egressos nem acesso a outra unidade.
  Ela NÃO DEVE alterar as três capacidades da 010 nem o que cada atuação faz no editor.
  [Interpretação B5; 010 FR-030, FR-031]

**Campanhas visíveis**

- **FR-020**: No escopo institucional, DEVEM ser visíveis **todas** as Campanhas, em
  qualquer estado. [Interpretação B3]
- **FR-021**: No escopo de unidades, uma Campanha DEVE ser visível se, e somente se:
  - (a) ela **não define** critério de unidades; ou
  - (b) seu critério de unidades contém, por igualdade textual exata, **ao menos uma**
    unidade do escopo.

  [004 FR-018 c, FR-019, FR-020, FR-022; Interpretação B2]
- **FR-022**: A visibilidade NÃO DEVE depender de haver Conclusão elegível, Participação
  ou qualquer número diferente de zero, nem do estado da Campanha. [Escopo]
- **FR-023**: Todos os números de uma Campanha, para um escopo de unidades, DEVEM ser
  calculados somente sobre o **universo do escopo** (FR-015): Conclusões das unidades do
  operador e Participações dessas Conclusões. O critério de unidades da Campanha NÃO
  DEVE ser reaplicado pelo acompanhamento: ele já está na população da 004 (FR-030) e
  NÃO DEVE filtrar Participações (FR-038). As **unidades relevantes** — todas as unidades
  do escopo, se a Campanha não define critério de unidades; senão, a interseção entre as
  unidades do escopo e as do critério — servem **só** para as linhas com zero do recorte
  por unidade (FR-055). A oferta do recorte por unidade (FR-057) e a coluna Unidade do
  recorte por curso dependem do **escopo** (mais de uma unidade ou institucional), porque
  as Participações são contadas por todas as unidades do escopo. [Interpretação B4;
  004 FR-025; code review 2026-10-02]

**Indicadores — definições**

Para uma Campanha **C** e um operador com universo **U** (FR-015, FR-023), no momento da
consulta:

- **FR-030**: **ELEGÍVEIS ATUAIS** DEVE ser o número de Conclusões Acadêmicas que, no
  momento da consulta, satisfazem os critérios de C segundo a avaliação da 004 **e**
  pertencem a U. DEVE usar exatamente a
  mesma regra de elegibilidade da 004, sem regra paralela. [004 FR-025, FR-031, FR-032,
  FR-033]

- **FR-031**: Elegíveis atuais DEVE ser apresentado sempre como **população atual**
  ("elegíveis atuais", "no momento da consulta"). NÃO DEVE ser chamado de população da
  Campanha, público, base, universo oficial ou denominador histórico. [004 FR-031;
  DP-408]
- **FR-032**: **INICIADAS** DEVE ser o número de Participações existentes de C cuja
  Conclusão pertence a U, pela unidade institucional da Conclusão, sem reavaliar
  elegibilidade nem critério da Campanha (FR-038). Inclui Participações sem nenhuma
  Resposta, porque o domínio registra o início na operação "iniciar" da 005, e não na
  primeira Resposta. A interface DEVE dizer isso ("inclui Participações ainda sem
  respostas"). Esta definição é **tratamento operacional provisório**; o significado
  institucional de "iniciada" continua em 007/DP-703. [005 FR-011; 007/DP-703;
  Hipótese]
- **FR-033**: **CONCLUÍDAS** DEVE ser o número das Participações contadas em INICIADAS
  que têm conclusão registrada pela 006. Inclui as concluídas por recusa (Q1 = "Não"),
  porque distingui-las exigiria ler Respostas (FR-090). A interface DEVE definir
  concluídas como "Participações com conclusão registrada" (rótulo "Participações
  concluídas"), e NÃO DEVE usar "questionários integralmente respondidos" ou
  equivalente. 006/DP-601 continua aberta.
  [006 FR-001, FR-003; 006/DP-601; Hipótese]
- **FR-034**: **EM ANDAMENTO** DEVE ser INICIADAS − CONCLUÍDAS: Participações iniciadas e
  sem conclusão registrada. Enquanto a Campanha está EM COLETA, a interface DEVE chamá-lo
  "em andamento". Fora de EM COLETA, DEVE apresentá-lo como "iniciadas e não concluídas",
  com a observação de que a coleta não está aberta. Isso é rótulo, não estado: NÃO DEVEM
  ser usados "abandonada", "desistência", "expirada", "evasão" ou equivalente.
  [005 FR-040; 005/DP-503; Const. — XXIX]
- **FR-035**: **TAXA DE INÍCIO** DEVE ser INICIADAS ÷ ELEGÍVEIS ATUAIS. **TAXA DE
  CONCLUSÃO** DEVE ser CONCLUÍDAS ÷ ELEGÍVEIS ATUAIS. Ambas são calculadas sobre o mesmo
  universo U e o mesmo recorte da linha em que aparecem.
  [Const. — XIX]
- **FR-036**: Com ELEGÍVEIS ATUAIS = 0, as taxas DEVEM ser apresentadas como "—" com o
  significado "não se aplica" (texto acessível e explicação), nunca como 0%, erro,
  "NaN", "∞" ou célula vazia sem explicação. [Escopo]
- **FR-037**: As taxas DEVEM ser apresentadas como percentual com uma casa decimal e
  sempre acompanhadas, na mesma linha, dos números absolutos de que derivam.
  [Hipótese]
- **FR-038**: INICIADAS e CONCLUÍDAS NÃO DEVEM ser filtradas pela elegibilidade atual: a
  Participação é fato registrado, e a elegibilidade é verificada só no início (005;
  005/DP-507). Pela 001, Conclusões não mudam, então hoje toda Participação contada é de
  Conclusão elegível. Se uma correção acadêmica futura (001/DP-005) quebrar isso, a taxa
  PODE passar de 100%; ela DEVE ser mostrada como calculada: sem truncamento, correção
  artificial, erro ou snapshot. O rótulo permanente "população elegível atual" basta;
  NÃO DEVE ser criada detecção, nota condicional ou outra infraestrutura para esse
  cenário, que hoje não ocorre. A reconciliação histórica pertence à Feature 012.
  [Clarifications 2026-10-02]
  [005/DP-507; 004/DP-408; Const. — XXIX]
- **FR-039**: Nenhum indicador DEVE contar Pessoas. Toda contagem é de Conclusões
  Acadêmicas ou de Participações, e a interface DEVE dizer isso. [004 FR-033;
  Const. — I, XI]

**Lista de Campanhas**

- **FR-040**: A lista DEVE mostrar, para cada Campanha visível: nome; Pesquisa e Versão
  aplicadas (com FR-042); período (ou "não definido"); situação da 004 (EM PREPARAÇÃO,
  EM COLETA, ENCERRADA); elegíveis atuais; iniciadas; concluídas — todos calculados no
  escopo do operador. Nada mais é exigido. [Escopo]
- **FR-041**: A ordem da lista DEVE ser determinística e sem significado de
  preferência, desempenho ou prioridade (por exemplo, pelo período e depois pelo nome).
  NÃO DEVE ser ordenada por indicador. [004 FR-052; Const. — XXII]
- **FR-042**: Para operador que não tem a capacidade **consultar rascunhos** da 010, uma
  Campanha cuja Versão está em RASCUNHO DEVE mostrar o instrumento **apenas** como
  "Instrumento ainda não publicado": sem nome ou designação da Versão, sem link, sem
  estrutura, sem diagnóstico e sem qualquer conteúdo do rascunho. Isso não concede acesso
  ao rascunho nem altera a autorização da 010. Para Versão publicada, ou para quem
  consulta rascunhos, Pesquisa e Versão são identificadas; um link para o editor PODE
  existir somente quando o operador puder consultar a Versão. [010 FR-031, FR-036;
  Clarifications 2026-10-02]

**Detalhe da Campanha**

- **FR-043**: O detalhe DEVE mostrar: nome; Pesquisa e Versão (com FR-042); período;
  situação; momento da abertura, se houve; momento e forma do encerramento, se houve; e
  os seis indicadores (FR-030 a FR-035), cada um com definição curta. [004 FR-045]
- **FR-044**: Campanha EM PREPARAÇÃO DEVE informar que a coleta ainda não começou.
  Campanha ENCERRADA nunca aberta DEVE informar que não chegou a entrar em coleta.
  Nenhum estado adicional DEVE ser criado. [004 FR-034, FR-038]
- **FR-045**: Toda página DEVE informar que os números correspondem aos dados **no
  momento da consulta** e PODE mostrar esse momento. Esse momento NÃO DEVE ser gravado.
  [Const. — XXII]
- **FR-046**: Campanha ENCERRADA DEVE exibir aviso de que "elegíveis atuais" é calculado
  com os dados acadêmicos atuais e pode diferir da população existente na data de
  encerramento. A interface NÃO DEVE sugerir que o denominador atual é o denominador da
  data de encerramento. [004 FR-031; DP-408]

**Recortes**

- **FR-050**: Os recortes DEVEM ser exatamente estes, todos lidos da Conclusão Acadêmica:
  - (a) **unidade**;
  - (b) **curso**, identificado pelo par unidade + curso;
  - (c) **nível**;
  - (d) **modalidade**;
  - (e) **forma de oferta**;
  - (f) **ano de conclusão**.

  Nenhum outro recorte DEVE existir nesta feature. [001 FR-009; 004 FR-018; Escopo]
- **FR-051**: Cada recorte DEVE ser uma tabela com uma linha por valor da dimensão e as
  colunas: valor da dimensão (no recorte por curso: unidade e curso), elegíveis atuais,
  iniciadas, concluídas, taxa de conclusão. A taxa de início PODE ser incluída. Os
  indicadores de cada linha DEVEM seguir FR-030 a FR-039 restritos às Conclusões com
  aquele valor. [Escopo]
- **FR-052**: Uma Conclusão (e suas Participações) DEVE pertencer a exatamente uma linha
  de cada recorte, de modo que a soma das linhas seja igual aos totais do detalhe no
  escopo do operador. [Const. — XXVI]
- **FR-053**: Atributo ausente DEVE formar a linha "<dimensão> não informado(a)". O
  valor NÃO DEVE ser inferido de curso, de outra Conclusão da Pessoa, de Resposta ou de
  qualquer padrão. [001 FR-010; 004 FR-028; Const. — III]
- **FR-054**: Os valores DEVEM ser apresentados como registrados na Conclusão, sem
  normalização de caixa, espaços, sinônimos ou abreviações. [004 FR-022; 001/DP-007]
- **FR-055**: As linhas DEVEM existir para os valores presentes nas Conclusões elegíveis
  ou nas Participações contadas. No recorte por unidade, DEVEM aparecer mesmo com zero:
  no escopo institucional, as unidades do critério da Campanha; no escopo de unidades,
  as unidades relevantes (FR-023). Nos demais recortes, nenhuma linha com zero DEVE ser
  criada. Nenhuma lista de unidades, cursos ou valores DEVE ser criada ou mantida para isso.
  [Const. — XXII; 001 R10]
- **FR-056**: As linhas DEVEM ser ordenadas pelo valor da dimensão (ordem alfabética do
  texto; ano em ordem crescente; no recorte por curso, unidade e depois curso), com
  "não informado" por último. NÃO DEVEM ser ordenadas por indicador nem permitir essa
  ordenação. [Const. — XXII; Escopo]
- **FR-057**: O recorte por unidade DEVE ser oferecido ao escopo institucional e ao
  escopo com mais de uma unidade. Para escopo com uma única unidade, ele PODE ser omitido
  das opções; o mesmo critério decide a coluna Unidade do recorte por curso. [Escopo]
- **FR-058**: O recorte (f) DEVE chamar-se "ano de conclusão". NÃO DEVE ser chamado
  "coorte" nem agrupar anos em faixas, enquanto DP-1102 estiver aberta. [001 FR-036;
  Const. — XXIX]
- **FR-059**: Somente **um** recorte DEVE ser apresentado por vez, escolhido entre os
  oferecidos por links ou formulários comuns. NÃO DEVEM existir combinação de dimensões,
  filtros arbitrários, grupos de filtros, dimensões configuráveis, tabela dinâmica,
  drill-down para indivíduos nem visões salvas. Pedido de dimensão fora da lista DEVE
  ser tratado como inexistente. [Const. — XXII, XXIII; Escopo]
- **FR-060**: Todo recorte DEVE identificar que seus valores vêm do **registro acadêmico
  institucional** da Conclusão. [ADR 0003; Const. — III, IV]
- **FR-061**: O recorte por nível DEVE usar o nível da Conclusão Acadêmica, nunca a
  Resposta à Q14 nem outra Resposta, mesmo quando houver divergência. O mesmo vale para
  unidade (sem usar Resposta sobre campus), curso, modalidade, forma de oferta e ano.
  [Const. — III; ADR 0003; 003/DP-307; 005/DP-508]

**Proveniência e fontes de cálculo**

- **FR-070**: Os indicadores DEVEM ser calculados somente a partir de: critérios e estado
  da Campanha (004); atributos institucionais da Conclusão Acadêmica (001); existência e
  conclusão registrada da Participação (005, 006); vínculos de governança (010).
  [Const. — III, IV]
- **FR-071**: O escopo DEVE ser aplicado **no cálculo**, antes de contar. NÃO DEVE ser
  calculado o conjunto institucional e depois escondido na apresentação. [Const. — XII,
  XVI]
- **FR-072**: O cálculo DEVE usar agregação proporcional: o número de leituras ao banco
  para um detalhe ou recorte NÃO DEVE crescer com o número de linhas do recorte
  (unidades, cursos, valores) nem com o número de Conclusões ou Participações; e NÃO DEVE
  carregar registros individuais para contar fora do banco. Na lista, o custo PODE
  crescer com o número de Campanhas listadas, não com o de linhas internas. [Arquitetura]
- **FR-073**: NÃO DEVEM ser introduzidos cache, visão materializada, tabela de agregação,
  fila, job, processamento assíncrono nem serviço externo para o acompanhamento, salvo
  evidência concreta de necessidade registrada no plan (*Complexity Tracking*).
  [Const. — XXII]

**Dados individuais e privacidade**

- **FR-080**: O acompanhamento NÃO DEVE apresentar: nome, identificador ou qualquer
  atributo de Pessoa; identificador de Conclusão ou de Participação; lista de egressos,
  de formações ou de Participações; respostas ou seu conteúdo; quem respondeu ou não
  respondeu. [Const. — XVI; 005/DP-505]
- **FR-081**: NÃO DEVE existir drill-down de um número agregado para indivíduos, nem
  lista de não respondentes. O indicador "não iniciadas" fica fora do MVP por
  escopo (Clarifications 2026-10-02). [Const. — XVI; Escopo]
- **FR-082**: Os recortes NÃO DEVEM suprimir, arredondar para faixa nem agrupar linhas
  pequenas nesta feature: não há requisito institucional definido (DP-1101). A
  exposição continua restrita a agregados, a operadores com vínculo ativo e ao seu
  escopo. [Const. — XVI, XXIX]
- **FR-083**: Registros técnicos (logs) do acompanhamento NÃO DEVEM conter dado pessoal
  além do identificador de operador. [Const. — Observabilidade; 010 FR-074]
- **FR-084**: Esta feature NÃO DEVE criar consulta de Participações ou Respostas
  identificadas. 005/DP-505 continua aberta. [005/DP-505]

**Respostas não são lidas**

- **FR-090**: Nenhum indicador, recorte, visibilidade ou recusa DEVE ler Resposta,
  seleção de Opção, complemento ou valor declarado. A existência e a conclusão da
  Participação bastam. [Const. — III, XVI, XXII]

**Gestão de Campanha e comunicação**

- **FR-100**: Esta feature NÃO DEVE criar tela, ação ou rota para criar, editar, alterar
  critérios, abrir, encerrar, reabrir, prorrogar ou remover Campanha. A competência
  continua pendente (004/DP-402, DP-405) e nenhuma decisão anterior a resolveu.
  [004 FR-056; Const. — X]
- **FR-101**: Esta feature NÃO DEVE criar envio de e-mail, WhatsApp, SMS, lembrete,
  convite, lista de destinatários ou de não respondentes, nem entidade Convite.
  [004 FR-048, FR-049; 004/DP-407; Const. — VI]

**Sem avaliação de desempenho**

- **FR-110**: NÃO DEVEM existir ranking, posição, ordenação por indicador, "melhor",
  "pior", "alto/baixo desempenho", destaque, ícone ou cor de desempenho, semáforo, meta,
  objetivo percentual, previsão ou tendência. [Const. — X, XXII; Escopo]
- **FR-111**: NÃO DEVEM existir comparações entre Campanhas, entre anos, entre unidade e
  instituição ao longo do tempo, nem variação desde a consulta anterior. [Escopo]

**Interface, linguagem e acessibilidade**

- **FR-120**: As páginas DEVEM ser geradas no servidor e ser plenamente compreensíveis e
  operáveis sem JavaScript. NÃO DEVE ser exigida biblioteca de gráficos. [008; 009
  FR-098; 010 FR-078]
- **FR-121**: Números-resumo e tabelas DEVEM ser a forma principal. Barra de progresso
  PODE ser usada somente como complemento de um número e percentual escritos, e nunca
  como único meio da informação. [Const. — XX]
- **FR-122**: As páginas DEVEM seguir os requisitos de acessibilidade e responsividade
  da 008–010 (009 FR-110 a FR-112; 010 FR-077): HTML semântico, um título principal e
  hierarquia de títulos, teclado, foco visível, contraste AA, nada só por cor,
  funcionamento a partir de 320 px e com zoom de 200%. [Const. — XX, XXI]
- **FR-123**: Tabelas DEVEM ter legenda e cabeçalhos de coluna e de linha associados; em
  telas estreitas, NÃO DEVEM causar rolagem horizontal da página (a tabela PODE rolar
  dentro de sua própria área, com indicação acessível). [Const. — XX, XXI]
- **FR-124**: "—" DEVE ter equivalente textual acessível ("não se aplica").
  [Const. — XX]
- **FR-125**: A linguagem DEVE ser operacional: "Comissão Própria de Acompanhamento do
  Egresso (CPAEG)", "Comissão Setorial de Acompanhamento de Egressos (CSAEG)",
  "unidade", "Campanha", "Participação", "elegíveis atuais", "formações". NÃO DEVEM
  aparecer "dashboard", "KPI", "funil", "churn", "abandono", "scope", "role",
  "permission", "tenant" nem identificadores técnicos. "Painel" PODE ser usado como
  nome da interface operacional. [010 FR-076; Const. — XIV]

**Persistência**

- **FR-130**: Esta feature NÃO DEVE criar modelo, tabela, coluna, índice obrigatório ou
  migration. Se o plan concluir que um índice é necessário, DEVE demonstrá-lo com
  evidência em *Complexity Tracking*. [Const. — XXII, XXVII]
- **FR-131**: NÃO DEVEM ser criados: snapshot, CampaignMember, EligiblePopulationSnapshot,
  tabela materializada, cópia de Conclusões, contador gravado, momento de atualização
  gravado, Dashboard, Widget, Metric, Dimension, DashboardLayout, ChartConfiguration,
  SavedView, FilterBuilder, QueryBuilder ou linguagem de filtros. [Const. — XXII;
  004 FR-032]

**Preservação das features anteriores**

- **FR-140**: As regras de 001 a 010 NÃO DEVEM mudar. Em particular, a avaliação de
  elegibilidade da 004 DEVE ser reutilizada, não reimplementada com outra semântica.
  [004 FR-025; Arquitetura]
- **FR-141**: As três capacidades da 010 e a matriz do editor NÃO DEVEM mudar. A
  capacidade **acompanhar a coleta** é acrescentada; o "exatamente três capacidades" da
  010 (SC-008) passa a "três capacidades do editor e uma do acompanhamento".
  [010 FR-028, FR-033, FR-073]
- **FR-142**: O preparo local da demonstração DEVE permitir exercitar o escopo CSAEG com
  os dados do próprio cenário: o operador CSAEG fictício precisa ver ao menos uma
  Campanha relevante. Os operadores fictícios da 010 DEVEM ser preservados (A = CPAEG;
  B = CSAEG Vitória; C = sem vínculo). A 011 DEVE acrescentar o menor dado fictício
  próprio necessário (por exemplo, uma Campanha fictícia relevante para Vitória), sem
  alterar a jornada consolidada da 007/008, as regras de produção nem o significado dos
  operadores, mantendo o preparo idempotente. NÃO DEVE mudar regra de visibilidade nem
  criar dado real. [Clarifications 2026-10-02; 010 FR-058, FR-060]

**Acesso, recusa e proteção no servidor**

- **FR-150**: Toda página do acompanhamento DEVE verificar no servidor, antes de
  qualquer consulta ou cálculo: (1) operador identificado; (2) vínculo ativo; (3) para
  páginas de Campanha, existência da Campanha; (4) Campanha visível para o escopo.
  [Const. — XII, XVI; 010 FR-037]
- **FR-151**: Sem operador identificado, NÃO DEVE ser apresentado conteúdo: no modo de
  demonstração, quem usa é levado à escolha de operador fictício (010 FR-055); fora dele,
  nada responde. [010 FR-053, FR-054]
- **FR-152**: Operador identificado sem vínculo ativo DEVE receber recusa de acesso
  "sem atuação institucional ativa". [010 FR-043]
- **FR-153**: Campanha existente e não visível para o escopo DEVE receber recusa de
  acesso que diga, em linguagem operacional, que a Campanha não está no escopo de
  acompanhamento da atuação, **sem** apresentar nome, período, instrumento, critério ou
  número da Campanha. A recusa vale igualmente para detalhe e recortes. [Const. — XVI;
  caso N]
- **FR-154**: Campanha inexistente, para operador com vínculo ativo, DEVE responder
  "inexistente". [010 FR-045]
- **FR-155**: As recusas DEVEM seguir 010 FR-043 e FR-044: título, explicação
  operacional, caminho de volta; sem identificador técnico, nome de regra, papel técnico,
  lista de vínculos ou de unidades de outros operadores. [010]
- **FR-156**: Ocultar Campanhas ou recortes na apresentação DEVE ser apenas
  conveniência; a proteção DEVE ser sempre a verificação no servidor. DEVE existir
  verificação automatizada que percorra **todas** as rotas do acompanhamento e falhe se
  alguma não exigir a capacidade **acompanhar a coleta** e a verificação de escopo
  correspondente. [010 FR-041, FR-042; Const. — XXVI]
- **FR-157**: O acompanhamento DEVE existir somente com o modo de demonstração ligado,
  com a mesma identificação não produtiva da 010, enquanto 010/DP-1001 estiver aberta.
  Nenhum identificador vindo do cliente DEVE ser aceito fora do modo. [010 FR-053, FR-054;
  Escopo]
- **FR-158**: As páginas do acompanhamento DEVEM mostrar o contexto de atuação e o
  aviso de ambiente não produtivo, como o editor da 010. [010 FR-046, FR-061]

### Matriz de acesso ao acompanhamento

| Situação do operador | Lista | Detalhe/recorte de Campanha visível | Campanha fora do escopo | Unidades vistas |
|----------------------|-------|-------------------------------------|-------------------------|-----------------|
| Sem identificação (modo ligado) | Escolha de operador | Escolha de operador | Escolha de operador | — |
| Sem vínculo ativo | Recusa | Recusa | Recusa | — |
| CPAEG | Todas as Campanhas | Sim | Não ocorre | Todas, inclusive "não informada" |
| CSAEG (uma unidade) | Campanhas sem critério de unidade ou que incluem a unidade | Sim, só a unidade | Recusa | A unidade |
| CSAEG (várias) | Relevantes a qualquer das unidades | Sim, só as unidades relevantes | Recusa | União das unidades relevantes |
| CPAEG + CSAEG | Todas | Sim | Não ocorre | Todas |
| Modo desligado | Não responde | Não responde | Não responde | — |

### Key Entities *(include if feature involves data)*

**Nenhuma entidade nova.**

Entidades existentes, somente lidas:

- **Campanha** (004): nome, Versão, período, critérios (em especial o critério de
  unidades, para visibilidade), estado derivado, abertura e encerramento.
- **Conclusão Acadêmica** (001): unidade de contagem de elegíveis; fornece unidade,
  curso, nível, modalidade, forma de oferta e ano de conclusão para escopo e recortes.
  Dado institucional.
- **Participação** (005, 006): existência (iniciada) e conclusão registrada.
- **Vínculo de governança** (010): atuação e unidade, para capacidade e escopo.
- **Pesquisa e Versão** (002): somente para identificar o instrumento aplicado.
- **Pessoa** e **Resposta**: **não** são lidas.

Conceitos sem persistência (valores calculados a cada consulta): escopo de
acompanhamento, universo do escopo, unidades relevantes, indicadores, taxas, linhas de
recorte.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| Unidade, curso, nível, modalidade, forma de oferta, ano de conclusão | Institucional | Conclusão Acadêmica (001) | Lido como está; ausência é "não informado"; divergência com Resposta não é tratada aqui (005/DP-508; ADR 0003) |
| Critérios, período e estado da Campanha | Configuração institucional / derivado (estado) | Campanha (004) | Não se aplica |
| Elegíveis atuais | Derivado | Avaliação da 004 sobre as Conclusões existentes no momento, no escopo | Não persistido; pode variar (DP-408) |
| Iniciadas, concluídas, em andamento | Derivado | Contagem de Participações (005) e de conclusões registradas (006), no escopo | Não persistido; não filtra elegibilidade atual (FR-038) |
| Taxas | Derivado | Razões de FR-035 | Não persistido; "—" com denominador zero |
| Escopo de acompanhamento | Derivado | Vínculos ativos (010) | Não persistido; recalculado a cada requisição |
| Respostas | Declarado | **Não lidas** | Não se aplica |

### Análise de persistência

- **Modelos novos**: nenhum. **Migrations**: nenhuma.
- Todo indicador é função do estado atual de Campanha, Conclusão, Participação e vínculo;
  não há fato novo a registrar.
- **Fotografia da população**: não criada; é exatamente a decisão pendente 004/DP-408 e
  pertence à feature de dataset analítico.
- **Momento da consulta**: exibido, não gravado.
- **Escolha do recorte**: parâmetro da requisição, não preferência gravada.
- **Desempenho**: o volume atual (fictício) não justifica índice, cache ou agregação
  gravada. Se dados reais mostrarem necessidade, o plan registra a evidência (FR-073,
  FR-130).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Os 14 casos importantes (A a N) são demonstrados por verificação
  automatizada com dados fictícios, com 100% dos resultados conforme a spec.
- **SC-002**: Para um conjunto de referência de Campanhas, Conclusões, Participações e
  vínculos, 100% dos indicadores exibidos (totais e cada linha de cada recorte) coincidem
  com a contagem manual esperada, para CPAEG, CSAEG de uma unidade e CSAEG de duas
  unidades.
- **SC-003**: Em 100% dos recortes, a soma das linhas é igual aos totais do detalhe no
  mesmo escopo.
- **SC-004**: Em 100% dos acessos diretos de operador CSAEG a Campanha fora do escopo
  (detalhe e cada recorte), a resposta é recusa e nenhum nome, período, instrumento ou
  número da Campanha aparece.
- **SC-005**: Nenhuma página do acompanhamento, para nenhum operador, contém nome ou
  identificador de Pessoa, Conclusão ou Participação, nem conteúdo de Resposta,
  verificado sobre os dados fictícios de referência.
- **SC-006**: Em 100% dos casos com denominador zero, a taxa aparece como "não se aplica",
  sem erro, "NaN", "∞" ou 0%.
- **SC-007**: Depois da feature, existem zero modelos, tabelas, colunas e migrations
  novos, e nenhuma consulta do acompanhamento grava dado.
- **SC-008**: O cálculo de indicadores e recortes não lê nenhuma Resposta, verificado
  automaticamente.
- **SC-009**: A quantidade de leituras ao banco para abrir o detalhe com qualquer recorte
  é a mesma com 3 ou com 30 unidades/cursos no recorte.
- **SC-010**: Um operador que nunca usou o acompanhamento responde, a partir da lista e
  em menos de 1 minuto, "quantas formações são elegíveis agora, quantas Participações
  começaram e quantas foram concluídas" para uma Campanha, em revisão do roteiro de
  demonstração.
- **SC-011**: Lista, detalhe e recortes são operáveis só por teclado, legíveis em 320 px
  sem rolagem horizontal da página e compreensíveis com JavaScript desligado.
- **SC-012**: Nenhuma página exibe ranking, ordenação por indicador, meta, semáforo,
  termo de desempenho ou termo técnico de autorização.
- **SC-013**: Desativar o vínculo CPAEG de um operador que também é CSAEG faz a requisição
  seguinte mostrar somente a unidade CSAEG, sem nova escolha de operador.

## Assumptions

Apenas suposições não institucionais. As regras institucionais em aberto estão em
"Decisões Pendentes".

- Volume: dezenas de Campanhas, até dezenas de milhares de Conclusões e Participações no
  futuro; poucas consultas simultâneas. Agregações sob demanda são suficientes.
- A avaliação de elegibilidade da 004 já tem forma aplicável a muitas Conclusões de uma
  vez (população no momento), reutilizável pelo acompanhamento.
- A identificação de operador fictício da 010 é suficiente para a demonstração; o
  acompanhamento não é exposto em produção (010/DP-1001).
- O preparo da demonstração pode receber dados fictícios adicionais para os cenários
  (FR-142), sem alterar regras.
- Percentual com uma casa decimal é suficiente para leitura operacional. [Hipótese]
- O acompanhamento é página separada do editor, acessível ao mesmo operador fictício;
  a forma de navegação entre eles pertence ao plan.

## Relação com outras features

- **001** — consumida sem alteração: atributos institucionais da Conclusão, ausência como
  "não informado", sem catálogo de unidade ou curso.
- **002/003** — Pesquisa e Versão apenas identificadas; nada muda.
- **004** — consumida sem alteração: avaliação de elegibilidade e população no momento,
  estado, abertura e encerramento. 004/DP-402 (gestão de Campanha) **não** é resolvida;
  nenhuma ação de Campanha é exposta. 004/DP-408 (fotografia) continua aberta e é a
  razão do rótulo "elegíveis atuais".
- **005/006** — consumidas sem alteração: existência e conclusão registrada da
  Participação. Nenhuma Resposta é lida. 005/DP-503, DP-505, DP-507 e 006/DP-601 continuam
  abertas, com os tratamentos provisórios declarados em FR-032 a FR-038.
- **007** — 007/DP-703 continua aberta; FR-032 declara o tratamento provisório.
- **008/009** — mesma base de interface e acessibilidade; editor inalterado.
- **010** — primeiro consumidor concreto do escopo de unidade (010 FR-017). Acrescenta uma
  regra fixa (FR-010, FR-141), sem nova estrutura. A 010 FR-073 ("nenhum painel") era
  escopo negativo da própria 010; esta feature é a feature futura que ela previu.
  010/DP-1005 passa a ter impacto concreto (grafia da unidade do vínculo).
- **012 (prevista — dataset analítico)** — recebe a reprodução histórica, a fotografia
  da população e eventuais definições de coorte.
- **013 (prevista — exportação)** — recebe CSV/XLSX.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade (NON-NEGOTIABLE)**: contagens por Campanha, sem fundir
  Participações de Campanhas diferentes nem eleger "a mais recente" (FR-111). A mesma
  Conclusão conta em cada Campanha em que participa.
- **II — Definição de egresso (NON-NEGOTIABLE)**: elegíveis vêm da avaliação da 004 sobre
  Conclusões reconhecidas (FR-030, FR-140).
- **III — Dado institucional não é declarado (NON-NEGOTIABLE)**: recortes só com
  atributos institucionais (FR-060, FR-061); Respostas não lidas (FR-090).
- **IV — Proveniência**: cada recorte declara a fonte institucional (FR-060); indicadores
  derivados não persistidos (Origem dos Dados).
- **VII — Conceitos distintos (NON-NEGOTIABLE)**: Campanha, Versão e Participação
  continuam separadas; o acompanhamento é por Campanha.
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: nada é alterado (FR-001); o aviso de
  população atual evita reinterpretação do passado (FR-046).
- **X — Tecnologia não redefine governança (NON-NEGOTIABLE)**: capacidade fundada na PAEG
  e marcada como interpretação (B1–B6); nenhuma gestão de Campanha (FR-100); Proex não
  representada (DP-1006).
- **XI — Pessoa única, contexto múltiplo**: unidade e curso vêm da Conclusão (FR-015,
  FR-050); contagens de Conclusões, não de Pessoas (FR-039).
- **XII — Base central; escopos por unidade**: visão institucional para CPAEG, escopo de
  unidade para CSAEG, aplicado no cálculo (FR-012, FR-071), sem tenant nem base por
  unidade (FR-010).
- **XVI — Privacidade (NON-NEGOTIABLE)**: só agregados (FR-080 a FR-084); recusa sem
  dados (FR-153); risco de pequenos grupos registrado (DP-1101).
- **XIX — Acompanha a coleta, não é BI**: indicadores operacionais e distribuição por
  unidade, curso e ano, sem BI (FR-003, FR-131).
- **XX, XXI — Acessibilidade e responsividade**: FR-120 a FR-125.
- **XXII — YAGNI**: zero modelos (FR-130), uma regra (FR-010), duas telas, recortes de
  uma dimensão (FR-059), sem cache (FR-073).
- **XXIX — Hipóteses não viram requisitos (NON-NEGOTIABLE)**: "iniciada", "concluída por
  recusa", denominador e pequenos grupos ficam como tratamentos provisórios declarados,
  com as DPs abertas.

**Tensões identificadas (não são conflitos)**:

- **XIX × denominador dinâmico**: taxas sobre população atual podem variar depois do
  encerramento. Tratamento: rótulo "atual" e aviso (FR-031, FR-046); fotografia em
  DP-408.
- **XIX × "não iniciados"**: a Constituição lista "não iniciados" entre indicadores
  possíveis. O número seria derivável dos agregados (elegíveis atuais − iniciadas), mas
  fica fora do MVP porque não é necessário às perguntas centrais da 011 e não se quer
  ampliar o conjunto de indicadores agora (Clarifications 2026-10-02).
- **XVI × recortes por curso**: grupos pequenos podem permitir inferir a participação de
  alguém conhecido. Tratamento: agregados restritos a operadores autorizados e a seu
  escopo; DP-1101.
- **X × capacidade nova**: a 010 tinha três capacidades fechadas. A quarta tem consumidor
  concreto e fundamento na PAEG (Art. 21, I; Art. 22, I, IV), e é interpretação
  operacional (B1–B4), não competência autônoma.

Nenhum conflito com a Constituição, com a PAEG ou com as Features 001 a 010 foi
identificado.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence de fato ao domínio de acompanhamento?** Sim. "Acompanhamento operacional da
   coleta" está listado na Fronteira do Domínio do NIAE.
2. **É necessária ao ciclo de acompanhamento?** Sim. Sem ela, quem aplica e avalia a
   coleta não sabe como ela avança.
3. **Existe ou está prevista solução institucional mais adequada?** Para BI e análise
   estatística, sim (GeN/Looker Studio, a jusante), e por isso ficam fora. Para o
   andamento operacional sobre os dados do próprio NIAE, não.
4. **Integração seria suficiente?** Não para o andamento em tempo de consulta; sim, no
   futuro, para análises (012, 013).
5. **A incorporação aumentaria desnecessariamente o acoplamento do núcleo?** Não. Só
   leitura, sem modelos, sem alterar o núcleo.

## Out of Scope *(mandatory)*

- Criar, editar, alterar critérios, abrir, encerrar, reabrir, prorrogar ou remover
  Campanha (004/DP-402, DP-405).
- Mailing, convites, lembretes, comunicação com egressos, lista de não respondentes
  (004/DP-407).
- Dados individuais: lista de egressos, de formações ou de Participações; Pessoa;
  identificadores; respostas individuais ou seu conteúdo (005/DP-505).
- Indicador "não iniciadas" (derivável, mas desnecessário às perguntas centrais) e
  qualquer cruzamento que identifique elegíveis sem Participação.
- Distinção de concluídas por recusa (006/DP-601) e de Participações sem Respostas
  (007/DP-703).
- Snapshot, fotografia ou denominador histórico da população (004/DP-408).
- Dataset analítico, tabela fato, dimensão, star schema, ETL (Feature 012).
- Exportação CSV/XLSX, endpoint de download, API analítica (Feature 013).
- BI, GeN, Looker Studio, gráficos como requisito.
- Cache, visão materializada, tabela de agregação, jobs, filas, Redis, Celery.
- Alertas, metas, semáforos, rankings, previsão, tendências, comparações históricas.
- Coorte com definição metodológica (DP-1102); faixas de ano.
- Supressão estatística de pequenos grupos (DP-1101).
- Combinação de dimensões, filtros arbitrários, tabela dinâmica, visões salvas.
- Métricas de uso da jornada (abandono por Seção, funil, tempo — 008/DP-803).
- Atuação de Proex, DIREC, Proen ou Diretorias (010/DP-1006).
- Exposição em ambiente produtivo (010/DP-1001).
- Qualquer alteração de regra das Features 001 a 010.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: decisões novas usam o prefixo 11 (DP-1101…). As das features anteriores são
citadas como 00n/DP-nnn.

**Novas nesta feature**

- **DP-1101** — DECISÃO PENDENTE: **tratamento de grupos pequenos** nos recortes
  agregados (supressão, agrupamento ou nenhum tratamento), considerando que, num curso
  com poucos elegíveis, saber quantos concluíram pode permitir inferir a participação de
  alguém conhecido.
  - Instância competente: CPAEG/Proex, com o encarregado de dados.
  - Impacto: FR-082; recortes por curso e por ano; futura exportação.
  - Tratamento provisório: nenhuma supressão; nenhum limiar inventado; exposição
    restrita a agregados, a operadores com vínculo ativo e ao seu escopo, num ambiente
    não produtivo com dados fictícios (010/DP-1001; 005/DP-504).
- **DP-1102** — DECISÃO PENDENTE: **definição institucional de coorte** para o
  acompanhamento e as análises (ano de conclusão, ano de ingresso, faixas, tempo desde a
  conclusão na data da Campanha ou outra).
  - Instância competente: CPAEG/Proex.
  - Impacto: FR-058; Feature 012.
  - Tratamento provisório: recorte "ano de conclusão", lido da Conclusão, sem o nome
    "coorte" e sem faixas.

**Herdadas, afetadas e mantidas abertas**

- **004/DP-408** — fotografia da população como denominador estável: **mantida**. Esta
  feature é o primeiro consumidor e adota "elegíveis atuais" com aviso (FR-031, FR-046).
- **007/DP-703** — Participação sem Respostas conta como "iniciada"?: **mantida**.
  Tratamento operacional provisório e declarado: conta (FR-032).
- **006/DP-601** — concluída por recusa: **mantida**. Tratamento provisório declarado:
  conta como concluída, sem distinção (FR-033).
- **005/DP-503** — destino das Participações não concluídas: **mantida**. Rótulo "em
  andamento" / "iniciadas e não concluídas", sem "abandono" (FR-034).
- **005/DP-505** — consulta de Participações e respostas identificadas: **mantida**.
  Nada identificado é exposto (FR-080, FR-084).
- **005/DP-507** — efeito de correção acadêmica sobre Participação existente:
  **mantida**. Consequência declarada em FR-038.
- **010/DP-1005** — designação canônica das unidades: **mantida, agora com impacto
  concreto**: grafias diferentes entre vínculo, Campanha e Conclusão fazem uma Campanha
  não aparecer ou aparecer com zeros (US3.5).
- **010/DP-1006** — atuação de Proex, DIREC, Proen, Diretorias: **mantida**. O
  monitoramento da Proex (Art. 14) não é representado.
- **010/DP-1001** — identificação produtiva de operadores: **mantida**. O acompanhamento
  só existe no modo de demonstração (FR-157).
- **004/DP-402** — quem cria, configura, abre, encerra e remove Campanha: **mantida**.
  Nenhuma decisão anterior autorizou essas ações a uma atuação; nada é exposto (FR-100).
- **004/DP-401** — periodicidade: **mantida**. Nada é inferido do período das Campanhas.
- **004/DP-404** — Campanhas sobrepostas: **mantida**. Indicadores por Campanha, sem
  somar nem priorizar.
- **004/DP-405** — prorrogação e reabertura: **mantida**.
- **004/DP-407** — comunicação e canais: **mantida** (FR-101).
- **004/DP-409** e **001/DP-004** — Conclusões com atributo não informado: **mantidas**.
  Linha "não informado" nos recortes; Conclusão sem unidade fora do universo de CSAEG.
- **001/DP-005** — correção de dado acadêmico: **mantida**; afeta a estabilidade de
  "elegíveis atuais" e FR-038.
- **001/DP-007** — vocabulário canônico de nível, modalidade e forma de oferta:
  **mantida**; valores exibidos como registrados (FR-054).
- **005/DP-501** — várias Conclusões elegíveis da mesma Pessoa: **mantida**; contagem por
  Conclusão.
- **005/DP-504** e **001/DP-009** — base legal, consentimento, retenção: **mantidas**;
  bloqueiam uso com dados reais.
- **008/DP-803** — métricas de uso da jornada: **mantida**; nada criado.
- **002/DP-001** — publicação de Versão: **mantida**; o acompanhamento não publica nem
  sugere publicação.
- **002/DP-006** — comparabilidade entre Versões: **mantida**; sem comparação entre
  Campanhas (FR-111).
- **ADR 0003** (Q14 permanece declarada): respeitada; recorte por nível institucional
  declara a fonte (FR-060, FR-061).
