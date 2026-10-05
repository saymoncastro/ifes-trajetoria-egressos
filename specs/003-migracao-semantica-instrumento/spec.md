# Feature Specification: Migração semântica do instrumento institucional vigente

**Feature Branch**: `claude/feature-003-semantic-migration-64c1ed`

**Created**: 2026-10-01

**Status**: Implementada e integrada à `main` em 2026-10-01 (PR #4).

> **Nota de numeração (registrada em 2026-10-05).** Quando esta spec foi escrita, a jornada
> de resposta estava prevista como "Feature 004". O roteiro foi reorganizado depois: a 004
> passou a ser *Campanhas e população elegível*, e a jornada foi especificada nas Features
> **005** (Participação e respostas em rascunho) e **006** (jornada e conclusão; inclui a
> semântica de execução das regras, DP-302). Leia "Feature 004 (jornada de resposta)" ao
> longo desta spec como 005/006. O texto original foi mantido.

**Input**: User description: "Feature 003 — Migração semântica do instrumento institucional
vigente. Transformar o Formulário Egresso do Ifes 2024, documentado no inventário, em uma
representação canônica, rastreável e semanticamente fiel, usando a estrutura da Feature
002: Pesquisa → Versão em RASCUNHO → Seções → Perguntas → Opções → escalas → navegação.
Matriz de migração completa Q1–Q54, sem revisão metodológica, sem jornada de resposta,
sem publicação."

## Contexto

A Feature 001 estabeleceu **Pessoa → Conclusão Acadêmica** com fonte simulada. A Feature
002 estabeleceu a estrutura do instrumento: **Pesquisa → Versão (RASCUNHO | PUBLICADA) →
Seções → Perguntas → Opções**, com escalas, encaminhamentos de Seção e regras de
navegação condicional "se Pergunta X = Opção Y, ir para Seção Z / finalizar". A 002
deliberadamente não cadastrou o instrumento atual e deixou para esta feature a decisão
item a item de como representá-lo.

O Princípio XIII define o **Formulário Egresso do Ifes 2024** como referência funcional
inicial. Ele está transcrito em
[`docs/referencias/formulario-egresso-ifes-2024-inventario.md`](../../docs/referencias/formulario-egresso-ifes-2024-inventario.md)
(doravante "inventário"; observações citadas como O-n).

Esta feature cria a **primeira representação estruturada desse instrumento dentro do
NIAE**: uma **baseline migrada**, em RASCUNHO, verificável e rastreável até cada uma das
54 perguntas originais. Ela é o ponto de partida inspecionável para a jornada de resposta
(Feature 004) e para qualquer revisão metodológica futura.

### Princípio central: migração semântica

Esta feature **não** é cópia mecânica do Google Formulários, **não** é revisão
metodológica, **não** moderniza o questionário e **não** implementa a jornada. Ela
preserva o significado institucional do instrumento e distingue explicitamente:

1. **conteúdo metodológico** — perguntas, alternativas, escalas, obrigatoriedades,
   ordem e ramificações intencionais: preservado;
2. **conteúdo editorial** — títulos, textos de abertura, termos e encerramento:
   preservado; correções só quando explícitas e aprovadas nesta spec;
3. **acidentes ou limitações da ferramenta atual** — não reproduzidos quando a 002 já os
   distingue ou quando não têm efeito; cada um é registrado;
4. **dados candidatos a contexto institucional** — preservados na baseline e
   identificados como candidatos;
5. **decisões ainda não fundamentadas** — preservadas como estão e registradas como
   `DECISÃO PENDENTE`.

### Regra de conservadorismo

Na dúvida entre alterar e preservar, **preservar**. Nenhuma pergunta, alternativa,
obrigatoriedade, escala, ordem ou significado é alterado silenciosamente. "Parece melhor"
não é justificativa. Toda diferença entre o instrumento original e a baseline está na
Matriz de Migração com categoria e justificativa.

### Resultado esperado

| Elemento | Valor na baseline |
|----------|-------------------|
| Pesquisa | nome administrativo **"Pesquisa Institucional de Egressos"** |
| Versão | **referência migrada do instrumento vigente** — designação "Formulário Egresso Ifes 2024 — referência migrada" (FR-004) |
| Estado | **RASCUNHO**; não publicada por esta feature |
| Seções | 13 (as 13 Seções com perguntas do original; a 14ª, tela final, vira texto de encerramento) |
| Perguntas | 54, na ordem original |
| Opções | 385, em 41 perguntas |
| Escalas | 11, de 1 a 5 |
| Regras de navegação | 10 (9 "ir para Seção" e 1 "finalizar") |
| Encaminhamentos de Seção | 7 |

### Termos usados nesta spec

- **Instrumento original**: o Formulário Egresso do Ifes 2024, tal como transcrito no
  inventário.
- **Baseline migrada** (ou "baseline"): a Pesquisa e a Versão em RASCUNHO criadas por esta
  feature, com todo o seu conteúdo.
- **Materialização**: a operação que cria a baseline a partir da especificação desta
  feature. O mecanismo técnico pertence ao plan (FR-030).
- **Matriz de Migração**: artefato de documentação desta feature que liga cada elemento do
  instrumento original à sua representação na baseline. **Não** é entidade de domínio.
- **Qn**: identificador legado da n-ésima pergunta do instrumento original (Q1…Q54). Existe
  apenas na documentação e nas verificações desta feature, nunca no domínio (FR-012).
- **Sn**: n-ésima Seção da baseline, na ordem da Versão. A numeração das Seções da baseline
  coincide com a do original de S1 a S13.
- **Candidata a contexto institucional**: pergunta que permanece na baseline, mas que
  poderá deixar de ser apresentada ao egresso quando o contexto acadêmico institucional
  estiver disponível com qualidade suficiente (Princípios III e XIV). A classificação é
  hipótese do inventário e não remove nada.

Abreviações das tabelas: **EU** escolha única; **EM** escolha múltipla; **TC** resposta
textual curta; **ESC** escala. No Google Formulários: **ME** múltipla escolha; **LS** lista
suspensa; **CS** caixas de seleção; **RC** resposta curta; **EL** escala linear. Origem
provável (inventário): **I** institucional; **D** derivável; **Dc** declarada; **I?** a
investigar. **Obr.**: S = obrigatória, N = opcional.

## User Scenarios & Testing *(mandatory)*

Os "usuários" desta feature são: (a) quem revisa a migração (equipe do NIAE e, quando
houver, a instância institucional competente), que precisa auditar a fidelidade; (b) a
Feature 004 (jornada de resposta), que consumirá a baseline; (c) quem desenvolve e testa o
NIAE. Não há interface com egressos nem com gestores.

### User Story 1 - Materializar a Pesquisa e a Versão RASCUNHO do instrumento vigente (Priority: P1)

A equipe do NIAE precisa que exista, de forma reprodutível, a Pesquisa "Pesquisa
Institucional de Egressos" com uma Versão em RASCUNHO que representa o instrumento
vigente.

**Why this priority**: sem a baseline não há o que verificar nem o que entregar à Feature
004. É a menor fatia que materializa o resultado da feature.

**Independent Test**: em ambiente sem nenhuma Pesquisa, executar a materialização e
verificar que existem exatamente 1 Pesquisa com o nome esperado e 1 Versão com a
designação esperada, em RASCUNHO, sem momento de publicação, sem Versão de origem e sem
nenhuma Pessoa, Conclusão Acadêmica, Participação ou Resposta envolvida.

**Acceptance Scenarios**:

1. **Given** um ambiente sem Pesquisas, **When** a baseline é materializada, **Then**
   existem 1 Pesquisa "Pesquisa Institucional de Egressos" e 1 Versão com a designação da
   baseline, em RASCUNHO.
2. **Given** a baseline materializada, **When** sua situação é consultada, **Then** ela não
   tem momento de publicação e não foi criada a partir de outra Versão.
3. **Given** a baseline materializada, **When** se verifica a completude estrutural exigida
   pela 002 para publicar (002, FR-059), **Then** nenhuma pendência é encontrada, e a
   Versão continua em RASCUNHO.
4. **Given** um ambiente sem nenhuma Pessoa nem Conclusão Acadêmica, **When** a baseline é
   materializada, **Then** a operação funciona normalmente.

---

### User Story 2 - Representar integralmente textos, Seções, Perguntas, Opções, escalas e obrigatoriedades (Priority: P1)

Quem revisa a migração precisa constatar que a baseline contém todo o conteúdo apresentado
ao egresso no instrumento original, com os mesmos textos, tipos, obrigatoriedades, Opções,
escalas e ordem.

**Why this priority**: é a fidelidade da migração. Perda de pergunta, de Opção ou de ordem
alteraria o significado das respostas futuras (Princípio VIII).

**Independent Test**: consultar o conteúdo completo da baseline e compará-lo, Seção a
Seção e pergunta a pergunta, com a Matriz de Migração: contagens, textos, tipos,
obrigatoriedades, Opções na ordem, configurações de escala e textos explicativos.

**Acceptance Scenarios**:

1. **Given** a baseline, **When** suas Seções são consultadas, **Then** são 13, na ordem e
   com os títulos e textos da tabela "Seções da baseline", e S13 tem título explicitamente
   ausente.
2. **Given** a baseline, **When** suas Perguntas são percorridas na ordem (Seção, posição),
   **Then** são 54 e a n-ésima corresponde a Qn, com o texto, o tipo e a obrigatoriedade da
   Matriz.
3. **Given** cada pergunta de escolha, **When** suas Opções são consultadas, **Then** têm a
   quantidade, os textos e a ordem da Matriz, inclusive as listas extensas (Q15: 33; Q17:
   47; Q18: 50; Q19: 77).
4. **Given** cada pergunta de escala, **When** é consultada, **Then** vai de 1 a 5, o
   rótulo final é o da Matriz e o rótulo inicial aparece explicitamente ausente (DP-301).
5. **Given** a Versão, **When** seus textos são consultados, **Then** título apresentado,
   texto de abertura e texto de encerramento correspondem aos do instrumento original.
6. **Given** Q10, Q32 e Q48, **When** são consultadas, **Then** cada uma tem o texto
   explicativo original; nenhuma outra pergunta tem texto explicativo.
7. **Given** Q26, Q32 e Q45, **When** suas Opções são consultadas, **Then** a última Opção
   ("Outro:") admite complemento textual, e nenhuma outra Opção da baseline admite.

---

### User Story 3 - Rastrear Q1–Q54 pela Matriz de Migração (Priority: P1)

Quem revisa parte de qualquer Qn e precisa descobrir onde ela está na baseline, se mudou,
por que mudou, se há pendência e se é candidata a contexto institucional.

**Why this priority**: a migração precisa ser auditável. Sem rastreabilidade, a baseline
seria uma reinterpretação não verificável.

**Independent Test**: escolher perguntas ao acaso (por exemplo, Q6, Q19, Q41, Q47, Q51 e
Q53) e, usando apenas a Matriz e a consulta da baseline, localizar cada uma, identificar sua
categoria e justificativa e conferir que a baseline corresponde ao registrado.

**Acceptance Scenarios**:

1. **Given** a Matriz, **When** se procura qualquer Qn de Q1 a Q54, **Then** há exatamente
   uma linha com Seção e posição na baseline, categoria de tratamento e justificativa.
2. **Given** uma Qn cuja representação difere do original (por exemplo, Q41 sem a nota
   interna, Q51 sem a regra redundante, Q53 com rótulo corrigido), **When** sua linha é
   lida, **Then** a diferença, a categoria e a justificativa estão explícitas.
3. **Given** a Matriz, **When** se somam as linhas por categoria, **Then** o total é 54 e
   coincide com a tabela "Contagens verificáveis".
4. **Given** os elementos que não são perguntas (textos da Versão, termos, tela final,
   notas internas, rótulos, regras), **When** se consulta a "Matriz de elementos", **Then**
   cada um tem tratamento e justificativa.

---

### User Story 4 - Representar a navegação semanticamente relevante (Priority: P1)

A Feature 004 precisa receber, na baseline, as ramificações e convergências do instrumento
original: recusa dos termos encerra o instrumento; o nível escolhe a lista de cursos; quem
trabalha e quem não trabalha seguem ramos distintos; quem estuda responde à Seção de
estudo atual.

**Why this priority**: ramificações fazem parte do significado metodológico (Princípio
XIII: preservar condicionais relevantes).

**Independent Test**: deduzir da consulta da baseline todos os percursos de Seções
possíveis e compará-los com os 17 percursos esperados (tabela "Percursos esperados").

**Acceptance Scenarios**:

1. **Given** Q1, **When** suas regras são consultadas, **Then** "Não" finaliza o
   instrumento e "Sim" leva a S2.
2. **Given** Q14, **When** suas regras são consultadas, **Then** cada uma das 4 Opções leva,
   na ordem, a S4, S5, S6 e S7, e S4–S7 convergem para S8.
3. **Given** Q33, **When** suas regras são consultadas, **Then** "Sim" leva a S9 e "Não" a
   S10, e S9 e S10 convergem para S11.
4. **Given** Q46, **When** suas regras são consultadas, **Then** "Sim" leva a S12 e "Não" a
   S13, e S12 segue para S13.
5. **Given** Q51, **When** suas Opções são consultadas, **Then** nenhuma tem regra.
6. **Given** a baseline, **When** os percursos são deduzidos, **Then** são exatamente os 17
   da tabela "Percursos esperados", todos terminando em finalização.
7. **Given** Q46 seguida de Q47 e Q48 em S11, **When** a baseline é consultada, **Then** as
   três estão em S11 nas posições 1, 2 e 3, as regras estão associadas a Q46, e a baseline
   não registra em que momento o desvio é aplicado (DP-302).

---

### User Story 5 - Excluir apenas conteúdo editorial interno (Priority: P2)

Quem revisa precisa constatar que as duas notas internas de edição não fazem parte do que
é apresentado ao egresso e que nenhuma outra coisa foi excluída por esse motivo.

**Why this priority**: notas internas apresentadas ao egresso seriam erro visível, mas a
exclusão precisa ser restrita e documentada. É P2 porque depende da baseline (US1, US2).

**Independent Test**: procurar os textos das duas notas em todos os textos da baseline
(Versão, Seções, Perguntas, textos explicativos, Opções e rótulos) e verificar que nenhum
os contém; verificar que a Matriz de elementos registra exatamente 2 exclusões dessa
categoria.

**Acceptance Scenarios**:

1. **Given** a baseline, **When** se procura "Tem que atualizar a lista de cursos,
   adicionando doutorado", **Then** o texto não aparece, e S7 tem texto introdutório
   explicitamente ausente.
2. **Given** a baseline, **When** se procura "Verificar lugar dessa pergunta", **Then** o
   texto não aparece, e Q41 tem texto explicativo ausente, mantendo a mesma posição.
3. **Given** a Lista 19, **When** comparada com a baseline, **Then** nenhum curso foi
   acrescentado (a sugestão da nota não foi executada).

---

### User Story 6 - Registrar explicitamente a correção editorial (Priority: P2)

Quem revisa precisa ver que a única correção de texto feita na migração é "Corcordo
totalmente" → "Concordo totalmente" nas escalas de Q52, Q53 e Q54, registrada e
justificada, e que nenhum outro texto foi "corrigido".

**Why this priority**: separa acidente editorial de decisão metodológica e impede
correções por inferência. É P2 porque se apoia em US2.

**Independent Test**: verificar o rótulo final de Q52–Q54; procurar "Corcordo" em toda a
baseline; conferir textos com grafia original preservada (por exemplo, "auxilio" em Q32 e
"concordo totalmente" em minúsculas em Q48).

**Acceptance Scenarios**:

1. **Given** Q52, Q53 e Q54, **When** consultadas, **Then** o rótulo final é "Concordo
   totalmente".
2. **Given** a baseline, **When** se procura "Corcordo", **Then** não há ocorrências.
3. **Given** textos com particularidades de grafia não aprovadas para correção (Matriz,
   E-10 e E-19), **When** consultados, **Then** permanecem exatamente como no instrumento
   original.

---

### User Story 7 - Identificar candidatas a contexto institucional sem removê-las (Priority: P2)

A futura feature de jornada contextualizada precisa saber quais perguntas poderão deixar de
ser apresentadas quando houver contexto acadêmico suficiente, mas a baseline precisa
continuar sendo referência completa do instrumento.

**Why this priority**: concretiza os Princípios III e XIV sem antecipá-los. É P2 porque a
decisão de retirar perguntas não pertence a esta feature.

**Independent Test**: verificar que Q3, Q10–Q19, Q22, Q23, Q24, Q27, Q31 e Q32 estão
presentes na baseline, com seus textos e Opções originais, e marcadas na Matriz como
candidatas, com a dependência que bloqueia sua retirada.

**Acceptance Scenarios**:

1. **Given** Q10–Q19, **When** a baseline é consultada, **Then** todas estão presentes,
   e nenhuma condição do tipo "perguntar só se a fonte não tiver" existe.
2. **Given** Q3, **When** consultada, **Then** é resposta textual curta, obrigatória, sem
   validação numérica, e a Matriz a marca como candidata a dado derivado.
3. **Given** Q22, Q23, Q24, Q27, Q31 e Q32, **When** consultadas, **Then** são perguntas
   declaradas da baseline, e a Matriz registra que a existência de fonte institucional
   não foi verificada.
4. **Given** as listas de cursos de Q15, Q17, Q18 e Q19, **When** a baseline é
   materializada, **Then** nenhum Curso, Conclusão Acadêmica ou catálogo acadêmico é
   criado ou alterado a partir delas.

---

### User Story 8 - Garantir materialização idempotente (Priority: P2)

A baseline precisa poder ser construída de novo, em qualquer ambiente, sem criar cópias
acidentais nem alterar silenciosamente uma baseline existente.

**Why this priority**: reprodutibilidade e segurança operacional. É P2 porque pressupõe
US1.

**Independent Test**: materializar duas vezes seguidas e verificar que as quantidades e as
identidades de Pesquisa, Versão, Seções, Perguntas e Opções são as mesmas da primeira
execução.

**Acceptance Scenarios**:

1. **Given** a baseline já materializada, **When** a materialização é executada de novo,
   **Then** a execução termina com sucesso sem nenhuma alteração: continua existindo
   exatamente 1 Pesquisa com o nome e 1 Versão com a designação da baseline, com as mesmas
   identidades e o mesmo conteúdo, e o resultado informa que a baseline já existia.
2. **Given** uma baseline existente cujo conteúdo difere em qualquer ponto do esperado
   (por exemplo, um texto de Opção editado em rascunho, uma Pergunta a menos ou uma regra a
   mais), **When** a materialização é executada, **Then** ela falha explicitamente,
   informa que há divergência, e nada é criado, alterado, completado, corrigido ou
   sobrescrito.
3. **Given** uma Pesquisa "Pesquisa Institucional de Egressos" já existente, sem a Versão da
   baseline, **When** a materialização é executada, **Then** a Versão é criada nessa
   Pesquisa, sem criar outra Pesquisa.
4. **Given** mais de uma Pesquisa com o nome "Pesquisa Institucional de Egressos", **When**
   a materialização é executada, **Then** ela é rejeitada explicitamente, sem criar nem
   alterar nada.
5. **Given** a Versão da baseline já publicada por decisão posterior, **When** a
   materialização é executada, **Then** nada é alterado: se o conteúdo for equivalente, a
   execução é um no-op; se divergir, falha como no cenário 2.

---

### User Story 9 - Demonstrar que nenhuma revisão metodológica foi aplicada silenciosamente (Priority: P3)

Quem revisa precisa confirmar que problemas metodológicos conhecidos foram preservados e
continuam visíveis como pendências.

**Why this priority**: protege o Princípio XXIX. É P3 porque decorre das histórias
anteriores; aqui ele é verificado de forma consolidada.

**Independent Test**: para cada observação metodológica do inventário (O-6, O-7, O-8,
O-10, O-12, O-13, O-14, O-15, O-18, O-19, O-20), verificar que a baseline preserva o
comportamento original e que a Matriz aponta a pendência correspondente.

**Acceptance Scenarios**:

1. **Given** Q38 e Q39, **When** consultadas, **Then** as faixas são exatamente as
   originais, inclusive a sobreposição de limites de Q38 e a ausência do valor 500 em Q39.
2. **Given** Q42 e Q44, **When** consultadas, **Then** são opcionais, e Q43 é obrigatória.
3. **Given** Q6, **When** consultada, **Then** é escolha única opcional, na mesma Seção de
   Q5, sem regra, sem Seção própria e sem condição de exibição.
4. **Given** Q40, **When** consultada, **Then** texto e Opções se referem ao "campus", como
   no original.
5. **Given** Q13, **When** consultada, **Then** mantém as três Opções originais, sem
   separação entre reserva de vagas e forma de ingresso.
6. **Given** a Seção "Decisões Pendentes", **When** lida, **Then** cada observação
   metodológica preservada tem uma `DECISÃO PENDENTE` própria ou herdada.

---

### Edge Cases

- **Baseline já existente e equivalente**: a execução é um no-op bem-sucedido; o
  resultado informa que já existia (FR-032).
- **Baseline existente com conteúdo divergente** (por exemplo, editada em rascunho depois
  da materialização): a execução falha explicitamente, sem criar, alterar, completar ou
  sobrescrever nada (FR-033). Não há merge nem reparo automático; a divergência exige
  análise humana, fora desta feature.
- **Baseline já publicada** por decisão institucional posterior: a materialização não a
  altera; equivalente → no-op, divergente → falha (FR-033). A imutabilidade é garantida
  pela 002.
- **Várias Pesquisas com o mesmo nome**: a 002 não exige nome único (002, FR-002). A
  materialização é rejeitada por ambiguidade (FR-031).
- **Outras Versões na mesma Pesquisa**: permitidas; a materialização só procura a Versão
  com a designação da baseline.
- **Texto que diverge entre o inventário e o PDF original** (descoberto na implementação):
  o inventário é a fonte versionada desta feature. A divergência é registrada na Matriz
  como pendência, sem correção silenciosa (FR-007).
- **Rótulo inicial das escalas truncado** ("Disc…"): representado como ausente; não é
  completado por suposição (FR-018, DP-301). Se o texto exato for recuperado de fonte
  institucional autorizada durante a execução, a fonte da confirmação é registrada (FR-019).
- **Rótulos de Q48 em minúsculas**: preservados; a correção aprovada é só "Corcordo"
  (FR-021).
- **Q6 "Se sim, qual a deficiência?"**: preservada como pergunta opcional sem condição. A
  002 permitiria simular a condição com nova Seção e regra, mas isso alteraria a estrutura
  do instrumento e anteciparia decisão metodológica (DP-303).
- **Q46 com perguntas posteriores na mesma Seção**: única pergunta com regras que não é a
  última da sua Seção. O momento de aplicação do desvio fica para a 004 (FR-026, DP-302).
- **Regra cujo destino coincide com a Seção seguinte** (Q1 "Sim", Q14 primeira Opção, Q33
  "Sim", Q46 "Sim"): mantida, porque pertence a ramificação com efeito; diferente de Q51,
  em que nenhuma resposta muda o percurso (FR-023, FR-024).
- **Q14 como candidata a contexto**: Q14 também decide o ramo de cursos (S4–S7). Retirá-la
  no futuro exige que a jornada contextualizada trate esse ramo; isso não é feito aqui
  (DP-307).
- **Opções "Não houve", "Não recebi", "Não estudei mais"** em escolha múltipla: preservadas
  sem exclusividade, como no original (002, FR-036; 002/DP-005).
- **Opção "Outro:"**: preservada com o texto transcrito e complemento textual; o sinal de
  dois-pontos não é removido por inferência.
- **Q1 = "Não"**: representada como finalização. O que é registrado quando alguém recusa
  (inventário, O-17) é questão da jornada (004) e do consentimento (002/DP-007).
- **Dados de contato no texto de abertura** (e-mail e telefone): preservados como
  transcritos. Sua atualidade não é verificada aqui; revisão antes de publicar pertence ao
  processo institucional (002/DP-002).
- **Configuração externa do Google Formulários** (coleta de e-mail, exigência de login —
  O-1): não verificada e não migrada; não faz parte do conteúdo do instrumento.

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII): **[Herdado]** requisito herdado do instrumento atual;
**[PAEG]** decorre da PAEG; **[Const.]** decorre da Constituição; **[Arquitetura]** decisão
arquitetural; **[Hipótese]** hipótese reversível; **[Escopo]** decisão de escopo desta
feature; **[Futuro]** oportunidade metodológica futura, registrada e não aplicada.

### Functional Requirements

**Baseline**

- **FR-001**: O sistema DEVE permitir materializar uma baseline do Formulário Egresso do
  Ifes 2024 composta por 1 Pesquisa e 1 Versão com todo o conteúdo descrito em
  "Representação da baseline" e na "Matriz de Migração". [Const. — XIII]
- **FR-002**: A Pesquisa da baseline DEVE ter o nome administrativo "Pesquisa
  Institucional de Egressos". [Escopo]
- **FR-003**: A Versão da baseline DEVE permanecer em **RASCUNHO**. A materialização NÃO
  DEVE acionar a publicação da 002, nem direta nem indiretamente. A publicação futura é
  decisão explícita, sujeita a 002/DP-001 e 002/DP-002. [Const. — X; Escopo]
- **FR-004**: A Versão da baseline DEVE ter a designação "Formulário Egresso Ifes 2024 —
  referência migrada", que identifica a baseline técnica produzida pela migração. A
  designação NÃO significa publicação institucional, aprovação metodológica nem versão em
  produção. Ao final desta feature a Versão permanece obrigatoriamente em RASCUNHO
  (FR-003). Eventual designação diferente para publicação acompanha 002/DP-001. [Escopo —
  decidido pelo solicitante em 2026-10-01]
- **FR-005**: A Versão da baseline NÃO DEVE ter Versão de origem: ela é a primeira
  representação do instrumento no NIAE. [Arquitetura]
- **FR-006**: A baseline DEVE satisfazer todas as condições de completude estrutural da
  002 (002, FR-059), de modo que uma eventual publicação futura não dependa de ajuste
  estrutural. Essa verificação NÃO DEVE publicar a Versão. [Arquitetura]

**Fidelidade de conteúdo**

- **FR-007**: A fonte versionada da migração é o inventário. Textos de Versão, Seções,
  Perguntas, textos explicativos, Opções e rótulos DEVEM ser reproduzidos **exatamente**
  como transcritos no inventário (grafia, pontuação, maiúsculas, aspas e espaços internos),
  exceto onde a Matriz registra tratamento diferente. Divergência descoberta entre o
  inventário e o PDF original durante a implementação DEVE ser registrada na Matriz como
  pendência, sem correção silenciosa. [Herdado; Const. — VIII, XXIX]
- **FR-008**: A baseline DEVE conter as 54 perguntas do instrumento original como 54
  Perguntas, sem fusão, divisão, acréscimo ou remoção. [Herdado; Const. — XIII]
- **FR-009**: A ordem DEVE ser preservada: Seções na ordem S1–S13; Perguntas na ordem
  original dentro de cada Seção; Opções na ordem do inventário. Percorrendo as Perguntas
  pela ordem (Seção, posição), a n-ésima Pergunta DEVE corresponder a Qn. [Herdado; Const.
  — VIII]
- **FR-010**: O tipo de cada Pergunta DEVE seguir a correspondência: múltipla escolha e
  lista suspensa → escolha única; caixas de seleção → escolha múltipla; resposta curta →
  resposta textual curta; escala linear → escala. A distinção entre botões e lista
  suspensa NÃO DEVE ser representada (002, FR-035). [Herdado; Arquitetura]
- **FR-011**: A obrigatoriedade de cada Pergunta DEVE ser a do original: 50 obrigatórias e
  4 opcionais (Q6, Q42, Q44 e Q48). Irregularidades conhecidas NÃO DEVEM ser "corrigidas"
  (DP-303, DP-304). [Herdado; Const. — XIII, XXIX]
- **FR-012**: Os identificadores Q1–Q54 NÃO DEVEM ser gravados como atributo de domínio,
  código, rótulo ou texto da baseline. A correspondência com Qn DEVE ser obtida pela ordem
  (FR-009) e pela Matriz. [Const. — XXII; 002, FR-033]
- **FR-013**: Os textos explicativos de Q10, Q32 e Q48 DEVEM ser preservados como texto
  explicativo da Pergunta. Nenhuma outra Pergunta DEVE ter texto explicativo. [Herdado]
- **FR-014**: As Opções "Outro:" de Q26, Q32 e Q45 DEVEM admitir complemento textual.
  Nenhuma outra Opção DEVE admitir. [Herdado]
- **FR-015**: Listas de Opções idênticas em perguntas diferentes (Lista E em Q8 e Q9)
  DEVEM ser Opções próprias de cada Pergunta (002, FR-043). [Arquitetura]

**Textos da Versão e Seções**

- **FR-016**: A Versão DEVE ter: título apresentado "Egresso Ifes"; texto de abertura com
  os quatro parágrafos do cabeçalho do original (a saudação é um deles); texto de encerramento com "Este formulário
  chegou ao fim!" seguido de "Agradecemos imensamente a atenção dispensada e a
  participação na pesquisa.", em parágrafos separados. A tela final do original NÃO DEVE
  ser representada como Seção (002, FR-010). [Herdado; Arquitetura]
- **FR-017**: As 13 Seções DEVEM ter os títulos e textos introdutórios da tabela "Seções
  da baseline". S1 DEVE ter título "Termos e condições" e, como texto introdutório, os dois
  parágrafos dos termos. S13 DEVE ter título explicitamente ausente. S7 DEVE ter texto
  introdutório ausente (FR-027). Nenhuma Seção DEVE receber título ou texto que o original
  não tenha. [Herdado]

**Escalas**

- **FR-018**: As 11 perguntas de escala (Q20, Q21, Q36, Q42, Q43, Q44, Q48, Q50, Q52, Q53,
  Q54) DEVEM ir de 1 a 5. O rótulo inicial DEVE ficar **explicitamente ausente** em todas,
  porque o texto exato não é legível na fonte versionada ("Disc…"). O sistema NÃO DEVE
  completar o rótulo por conhecimento presumido (por exemplo, "Discordo totalmente").
  [Herdado; Const. — XXIX; DP-301]
- **FR-019**: Se, durante a execução desta feature, o texto exato do rótulo inicial for
  recuperado de fonte institucional autorizada, ele PODE ser adotado desde que a Matriz
  registre a fonte da confirmação e o escopo (quais escalas). Sem essa confirmação, vale
  FR-018. [Const. — IV, XXIX]
- **FR-020**: O rótulo final DEVE ser "Concordo totalmente" em Q20, Q21, Q36, Q42, Q43,
  Q44 e Q50; "concordo totalmente" (minúsculas, como no original) em Q48; e "Concordo
  totalmente" em Q52, Q53 e Q54, por correção editorial explícita (FR-021). [Herdado]
- **FR-021**: A única correção editorial desta migração DEVE ser "Corcordo totalmente" →
  "Concordo totalmente" no rótulo final de Q52, Q53 e Q54. Ela é permitida porque a
  baseline é nova representação em RASCUNHO, não alteração de Versão já usada; não muda o
  significado; e está registrada na Matriz (E-08). Nenhum outro texto DEVE ser corrigido
  por inferência. A política de correções após publicação continua em 002/DP-003.
  [Escopo; Const. — VIII, XIII]

**Navegação**

- **FR-022**: A baseline DEVE representar exatamente as regras da tabela "Navegação da
  baseline": Q1 ("Sim" → S2; "Não" → finalizar); Q14 (quatro Opções → S4, S5, S6, S7, na
  ordem); Q33 ("Sim" → S9; "Não" → S10); Q46 ("Sim" → S12; "Não" → S13). Nenhuma outra
  Pergunta DEVE ter regra. [Herdado]
- **FR-023**: **Critério de preservação de regras**: toda Opção de pergunta cuja resposta
  muda o percurso (Q1, Q14, Q33, Q46) DEVE ter destino explícito, mesmo quando ele
  coincide com a Seção seguinte. Assim a ramificação fica completa e não depende da
  adjacência das Seções. [Arquitetura; Const. — XIII]
- **FR-024**: A regra de Q51 ("Instituição Privada" → Q52) NÃO DEVE ser reproduzida:
  nenhuma resposta a Q51 altera o percurso (inventário, O-16). Q51 e suas três Opções DEVEM
  ser preservadas. A omissão é remoção de acidente de implementação, não revisão
  metodológica, e está registrada na Matriz (E-07). [Const. — XIII]
- **FR-025**: A baseline DEVE ter os encaminhamentos de Seção da tabela "Navegação da
  baseline": S4, S5, S6 e S7 → S8; S9 e S10 → S11; S12 → S13. Toda Seção que encerra um
  ramo DEVE ter encaminhamento explícito para o ponto de convergência (mesmo critério de
  FR-023). As demais Seções seguem o fluxo padrão; S13 é a última e finaliza pelo fluxo
  padrão. [Herdado; Arquitetura]
- **FR-026**: Q46, Q47 e Q48 DEVEM permanecer em S11, nas posições 1, 2 e 3, sem
  reordenação. As regras DEVEM ficar associadas a Q46. A baseline NÃO DEVE registrar o
  momento de aplicação do desvio nem criar atributo, enumeração ou estratégia para isso
  (002, FR-053). Esta feature DEVE registrar, para a Feature 004, que no instrumento
  original Q47 e Q48 são apresentadas a todos que chegam a S11 (inventário, O-15) e que a
  004 NÃO DEVE deixar de apresentá-las apenas porque Q46 tem regras, sem decisão explícita
  (DP-302). [Herdado; Const. — XIII, XXIX]

**Conteúdo editorial interno**

- **FR-027**: As notas internas "Tem que atualizar a lista de cursos, adicionando
  doutorado" (descrição da Seção 7) e "Verificar lugar dessa pergunta" (descrição de Q41)
  NÃO DEVEM fazer parte de nenhum texto da baseline. Elas DEVEM permanecer registradas na
  Matriz (E-05, E-06). As sugestões nelas contidas NÃO DEVEM ser executadas: a Lista 19 e a
  posição de Q41 permanecem como no original (DP-310). [Const. — XIII; Escopo]
- **FR-028**: Nenhum outro conteúdo DEVE ser excluído da baseline por ser editorial ou
  interno. [Const. — XIII]

**Candidatas a contexto institucional**

- **FR-029**: Q3, Q10, Q11, Q12, Q13, Q14, Q15, Q16, Q17, Q18, Q19, Q22, Q23, Q24, Q27, Q31
  e Q32 DEVEM permanecer na baseline como perguntas declaradas, com seu conteúdo original,
  e DEVEM ser identificadas na Matriz como candidatas a contexto institucional (ou, em Q3,
  a dado derivado), com a dependência que bloqueia sua retirada. Esta feature NÃO DEVE:
  (a) retirá-las; (b) criar condição do tipo "perguntar só se a fonte não tiver"; (c)
  registrar dado institucional como resposta; (d) presumir a existência de fonte para
  extensão, monitoria, estágio, intercâmbio, iniciação científica ou bolsas. Q47, Q49 e
  Q51 são registradas como **parcialmente** candidatas, sem mudar sua categoria.
  [Const. — III, XIV, XXIX]
- **FR-030**: As Opções de Q11, Q15, Q17, Q18 e Q19 são alternativas históricas do
  instrumento. A materialização NÃO DEVE criar, alterar ou alimentar Curso, unidade,
  Conclusão Acadêmica, catálogo acadêmico ou a fonte simulada da 001 a partir delas, nem
  tratá-las como verdade institucional atual. [Const. — III, V; Escopo]

**Materialização e idempotência**

- **FR-031**: A materialização DEVE ser determinística e repetível. Ela DEVE usar a
  Pesquisa com o nome de FR-002 se existir exatamente uma; criá-la se não existir; e ser
  rejeitada explicitamente, sem criar nem alterar nada, se existir mais de uma.
  [Arquitetura]
- **FR-032**: Se a Versão com a designação de FR-004 não existir na Pesquisa, a
  materialização DEVE criá-la com todo o conteúdo, de forma atômica: ou a baseline inteira
  é criada, ou nada é. Se já existir com conteúdo **integralmente equivalente** ao
  esperado, a materialização DEVE ser um no-op bem-sucedido: não cria, não altera e
  informa que a baseline já existia. [Arquitetura; Const. — XXVI]
- **FR-033**: Se a baseline já existir com **qualquer** diferença em relação ao conteúdo
  esperado, a materialização DEVE falhar explicitamente, informando a divergência, e NÃO
  DEVE alterar, completar, corrigir ou sobrescrever nada. A divergência NÃO DEVE ser
  tratada como aviso que permita continuar. "Conteúdo" segue a definição da 002 (textos da
  Versão; Seções, Perguntas, Opções, escalas, obrigatoriedades, complementos, ordens,
  regras e encaminhamentos), comparado por valor, sem considerar identidades internas; o
  estado da Versão e o nome da Pesquisa não fazem parte dele. Um diagnóstico suficiente
  para localizar a divergência é desejável. Esta feature NÃO DEVE criar merge automático,
  mecanismo de reconciliação, workflow, painel, atualização incremental ou migração de
  conteúdo entre Versões. [Escopo — decidido pelo solicitante em 2026-10-01; Const. —
  VIII, XXIX]
- **FR-034**: O mecanismo de materialização (migração de dados, fixture, operação de
  inicialização, módulo declarativo ou outro) pertence ao plan. Qualquer que seja, ele DEVE
  construir a baseline exclusivamente pelas operações da 002, respeitando suas regras de
  integridade. [Const. — XXIV; Escopo]

**Rastreabilidade**

- **FR-035**: Esta feature DEVE manter a Matriz de Migração como artefato de documentação,
  com: uma linha por Qn (Q1–Q54) contendo Seção original, texto original, tipo original e
  na baseline, obrigatoriedade, Opções ou escala, navegação original e na baseline, origem
  provável, posição na baseline, categoria de tratamento e justificativa; e uma "Matriz de
  elementos" para o conteúdo que não é pergunta. [Const. — XXVIII]
- **FR-036**: As categorias de tratamento são artefatos de análise. Elas NÃO DEVEM existir
  como enumeração, tabela, atributo ou marcador no domínio. [Const. — XXII]
- **FR-037**: Cada pergunta DEVE ter exatamente uma categoria principal, pela precedência:
  CANDIDATA_A_CONTEXTO_INSTITUCIONAL > CORREÇÃO_EDITORIAL_EXPLÍCITA >
  MANTER_COM_OBSERVAÇÃO > MANTER. Tratamentos adicionais da mesma pergunta (nota excluída,
  regra omitida, pendência) DEVEM aparecer na coluna de justificativa e na Matriz de
  elementos. As categorias NÃO_MIGRAR_COMO_CONTEÚDO, NAVEGAÇÃO_REDUNDANTE e
  DECISÃO_PENDENTE aplicam-se a elementos, não a perguntas: nenhuma pergunta deixa de ser
  migrada. [Escopo]

**Verificação de fidelidade**

- **FR-038**: DEVEM existir verificações automatizadas que comprovem ao menos: existência
  de 1 Pesquisa; existência de exatamente 1 Versão com a designação da baseline; estado
  RASCUNHO; 54 Perguntas na correspondência Qn de FR-009; textos essenciais; tipos;
  obrigatoriedades; Opções (quantidade, textos e ordem por pergunta); ordem das Seções e
  das Perguntas; configuração das 11 escalas; textos explicativos; complemento textual;
  as 10 regras e os 7 encaminhamentos; finalização por Q1 = "Não"; os 17 percursos
  esperados; ausência de regra em Q51; ausência das notas internas em todos os textos;
  presença da correção aprovada e ausência de "Corcordo"; completude estrutural sem
  publicação (FR-006); idempotência (FR-031 a FR-033). [Const. — XXVI]
- **FR-039**: As verificações NÃO DEVEM depender exclusivamente da mesma declaração usada
  para materializar. Elas DEVEM conter expectativas independentes, derivadas desta spec,
  capazes de detectar perda de pergunta ou de Opção e alteração de ordem: no mínimo, as
  contagens de "Contagens verificáveis", a quantidade de Opções por pergunta e os textos de
  cada pergunta. A sequência completa dos textos de Opções de cada pergunta DEVE ser
  conferida contra uma fonte independente da declaração de materialização (por exemplo, o
  próprio inventário ou a Matriz), de modo que a troca de ordem de quaisquer duas Opções
  seja detectada. Instantâneos extensos e frágeis NÃO DEVERIAM substituir verificações
  estruturais claras. [Const. — XXVI]

**Limites em relação a outras features**

- **FR-040**: Esta feature NÃO DEVE alterar modelo, operações, regras ou contrato da
  Feature 002. A baseline DEVE ser representável apenas com as capacidades existentes da
  002 (ver "Suficiência da Feature 002"). [Escopo; Const. — XXII]
- **FR-041**: Esta feature NÃO DEVE alterar Pessoa, Conclusão Acadêmica, a fronteira de
  dados acadêmicos, a fonte simulada ou qualquer contrato da Feature 001; NÃO DEVE
  acrescentar forma de ingresso, reserva de vagas, data de nascimento ou atributos de
  extensão, estágio, monitoria, intercâmbio, iniciação científica ou bolsas. A necessidade
  prevista em 001, FR-012 ("forma de ingresso… quando a spec de migração demonstrar
  necessidade concreta") NÃO é demonstrada por esta feature, que mantém Q13 como pergunta
  declarada. [Escopo; Const. — XXII]
- **FR-042**: Esta feature NÃO DEVE criar Campanha, Participação, Resposta, consentimento
  registrado, sessão, progresso, autosave, validação de preenchimento, renderização ou
  página pública. [Const. — VII; Escopo]

### Key Entities *(include if feature involves data)*

Esta feature **não cria entidades de domínio**. Ela usa as entidades da Feature 002
(Pesquisa, Versão, Seção, Pergunta, Opção, configuração de escala, regra de navegação,
encaminhamento) para criar uma instância concreta: a baseline. Nenhum elemento da baseline
contém dado pessoal nem dado institucional, derivado ou declarado; todos são configuração
do instrumento.

Artefato de documentação (não é entidade de domínio):

- **Matriz de Migração**: relaciona cada Qn e cada elemento não-pergunta do instrumento
  original à representação na baseline, com categoria e justificativa. Vive na
  documentação desta feature e pode ser usada pelas verificações de fidelidade.

## Representação da baseline

### Textos da Versão

| Texto | Valor | Origem |
|-------|-------|--------|
| Título apresentado | Egresso Ifes | Título exibido (inventário, Visão geral) |
| Texto de abertura | Os quatro parágrafos "Prezado(a) egresso(a) do Ifes,", "É com muita satisfação …", "A sua participação na pesquisa é muito importante …" e "Se você tiver alguma dúvida … (27) 99527-0027.", transcritos integralmente no inventário (Seção 1, "Texto de abertura") | Cabeçalho do formulário |
| Texto de encerramento | "Este formulário chegou ao fim!" e, em parágrafo seguinte, "Agradecemos imensamente a atenção dispensada e a participação na pesquisa." | Seção 14 do original (inventário, "Seção 14 — Encerramento") |

### Seções da baseline

| Seção | Título | Texto introdutório | Perguntas (posições) | Encaminhamento |
|-------|--------|--------------------|----------------------|----------------|
| S1 | Termos e condições | Os dois parágrafos dos termos ("Para participar deste estudo, …" e "O Ifes tratará a sua identidade …"), transcritos no inventário | Q1 (1) | — (regras de Q1) |
| S2 | Informações Pessoais | ausente | Q2–Q9 (1–8) | — (fluxo padrão → S3) |
| S3 | Informações do curso | ausente | Q10–Q14 (1–5) | — (regras de Q14) |
| S4 | Ensino Médio/Técnico Integrado | ausente | Q15 (1) | → S8 |
| S5 | Técnico Concomitante / Subsequente /EJA - PROEJA | ausente | Q16, Q17 (1, 2) | → S8 |
| S6 | Graduação | ausente | Q18 (1) | → S8 |
| S7 | Pós-Graduação | ausente (nota interna excluída — E-05) | Q19 (1) | → S8 |
| S8 | Avaliação | ausente | Q20–Q33 (1–14) | — (regras de Q33) |
| S9 | Egresso que trabalha | ausente | Q34–Q44 (1–11) | → S11 |
| S10 | Egresso que não trabalha | ausente | Q45 (1) | → S11 |
| S11 | Estudo | ausente | Q46–Q48 (1–3) | — (regras de Q46) |
| S12 | Egresso que estuda | ausente | Q49–Q51 (1–3) | → S13 |
| S13 | ausente | ausente | Q52–Q54 (1–3) | — (última; finaliza pelo fluxo padrão) |

O título de S5 preserva o espaçamento original ("Concomitante / Subsequente /EJA -
PROEJA"), que difere do texto da Opção correspondente de Q14 ("Técnico
Concomitante/Subsequente/EJA-PROEJA"). Cada texto é preservado como está (FR-007).

### Navegação da baseline

| Origem | Condição | Destino | Original (inventário) | Tratamento |
|--------|----------|---------|-----------------------|------------|
| Q1 | "Sim" | S2 | "Sim" → seção 2 | Regra mantida (FR-023) |
| Q1 | "Não" | Finalizar | "Não" → seção 14 (tela final) | Regra mantida; tela final = encerramento da Versão (FR-016) |
| Q14 | "Ensino Médio/Técnico Integrado" | S4 | → Q15 | Regra mantida |
| Q14 | "Técnico Concomitante/Subsequente/EJA-PROEJA" | S5 | → Q16 | Regra mantida |
| Q14 | "Graduação" | S6 | → Q18 | Regra mantida |
| Q14 | "Pós-Graduação" | S7 | → Q19 | Regra mantida |
| Q33 | "Sim" | S9 | → Q34 | Regra mantida |
| Q33 | "Não" | S10 | → Q45 | Regra mantida |
| Q46 | "Sim" | S12 | → Q49 (aplicado ao sair da seção) | Regra mantida; momento de aplicação: DP-302 |
| Q46 | "Não" | S13 | → Q52 (aplicado ao sair da seção) | Regra mantida; momento de aplicação: DP-302 |
| Q51 | "Instituição Privada" | — | → Q52 (igual ao padrão) | **Não reproduzida** (E-07, FR-024) |
| S4, S5, S6, S7 | fim da Seção | S8 | → Q20 | Encaminhamento (FR-025) |
| S9, S10 | fim da Seção | S11 | → Q46 | Encaminhamento (FR-025) |
| S12 | fim da Seção | S13 | → Q52 (padrão da seção) | Encaminhamento (FR-025) |
| S13 | fim da Seção | Finalizar | → seção 14 | Fluxo padrão (última Seção) |

### Percursos esperados

Com Q1 = "Não": **S1 → fim** (1 percurso).

Com Q1 = "Sim": **S1 → S2 → S3 → {S4 | S5 | S6 | S7} → S8 → {S9 | S10} → S11 → {S12 → S13
| S13} → fim**, conforme Q14, Q33 e Q46: 4 × 2 × 2 = 16 percursos.

Total: **17 percursos**, todos terminando em finalização. Os percursos descrevem Seções
visitadas; quais Perguntas de S11 são apresentadas depende do momento de aplicação
(DP-302) e é tratado pela 004.

### Escalas

| Perguntas | Limites | Rótulo inicial | Rótulo final |
|-----------|---------|----------------|--------------|
| Q20, Q21, Q36, Q42, Q43, Q44, Q50 | 1 a 5 | ausente (DP-301) | Concordo totalmente |
| Q48 | 1 a 5 | ausente (DP-301) | concordo totalmente |
| Q52, Q53, Q54 | 1 a 5 | ausente (DP-301) | Concordo totalmente (corrigido de "Corcordo totalmente" — E-08) |

## Matriz de Migração Q1–Q54

Colunas: **Nº**; **Texto original** (integral, como no inventário); **Tipo** (Google
Formulários → baseline); **Obr.**; **Opções / escala** (as listas extensas estão
transcritas no inventário e são reproduzidas integralmente, na mesma ordem); **Navegação**
(original → baseline); **Orig.** (origem provável); **Pos.** (Seção·posição na baseline);
**Tratamento**; **Justificativa**.

Em todas as linhas, quando não indicado o contrário, texto, tipo, obrigatoriedade, Opções e
ordem são idênticos ao original.

### Seção 1 — Termos e condições

| Nº | Texto original | Tipo | Obr. | Opções / escala | Navegação | Orig. | Pos. | Tratamento | Justificativa |
|----|----------------|------|------|-----------------|-----------|-------|------|------------|---------------|
| Q1 | Você concorda com os termos acima? | ME → EU | S | Sim; Não (2) | "Não" → fim; "Sim" → S2 → mantidas | Dc | S1·1 | MANTER_COM_OBSERVAÇÃO | Representa o instrumento vigente, com termos e recusa que finaliza. **Não** é consentimento juridicamente rastreável, não resolve base legal e não define o consentimento do modelo longitudinal (002/DP-007; O-1, O-2, O-17). |

### Seção 2 — Informações Pessoais

| Nº | Texto original | Tipo | Obr. | Opções / escala | Navegação | Orig. | Pos. | Tratamento | Justificativa |
|----|----------------|------|------|-----------------|-----------|-------|------|------------|---------------|
| Q2 | Qual é o seu sexo/identidade de gênero? | LS → EU | S | Masculino; Feminino; Mulher trans/travesti; Homem trans; Pessoa não binária; Prefiro não responder (6) | — | Dc | S2·1 | MANTER_COM_OBSERVAÇÃO | Dado potencialmente sensível; classificação jurídica pendente (O-6; DP-309). |
| Q3 | Quantos anos você tem? | RC → TC | S | — | — | D / Dc | S2·2 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Candidata a **dado derivado** se houver data de nascimento institucional; a 001 não a tem (001, FR-005). Permanece textual, sem tipo numérico (002, FR-037; DP-307). |
| Q4 | Como você se autodeclara? | LS → EU | S | Branco(a); Preto(a); Pardo(a); Amarelo(a); Indígena (5) | — | Dc | S2·3 | MANTER_COM_OBSERVAÇÃO | Dado potencialmente sensível; sem "Prefiro não responder" e obrigatória (O-6, O-7; DP-309). |
| Q5 | Você é PcD (Pessoa com deficiência)? | ME → EU | S | Sim; Não (2) | — | Dc | S2·4 | MANTER_COM_OBSERVAÇÃO | Dado potencialmente sensível; sem "Prefiro não responder" (O-6, O-7; DP-309). |
| Q6 | Se sim, qual a deficiência? | ME → EU | N | Deficiência física; Deficiência visual; Deficiência intelectual; Deficiência auditiva (4) | sem condicional → sem condicional | Dc | S2·5 | MANTER_COM_OBSERVAÇÃO | Redação condicional sem condição técnica; opcional; escolha única sem "Outra" (O-8). Preservada sem criar Seção, regra ou condição de exibição (002, FR-057; DP-303). Dado sensível (DP-309). |
| Q7 | Qual o seu estado civil? | LS → EU | S | Solteiro(a); Casado(a); Divorciado(a); Separado(a); Viúvo(a) (5) | — | Dc | S2·6 | MANTER_COM_OBSERVAÇÃO | Sem "Prefiro não responder" e obrigatória (O-7; DP-309). |
| Q8 | Qual é o nível de escolaridade do seu pai? | LS → EU | S | Lista E (17) | — | Dc | S2·7 | MANTER | — |
| Q9 | Qual é o nível de escolaridade da sua mãe? | LS → EU | S | Lista E (17), Opções próprias (FR-015) | — | Dc | S2·8 | MANTER | — |

### Seção 3 — Informações do curso

| Nº | Texto original | Tipo | Obr. | Opções / escala | Navegação | Orig. | Pos. | Tratamento | Justificativa |
|----|----------------|------|------|-----------------|-----------|-------|------|------------|---------------|
| Q10 | Em que ano você concluiu o seu curso no Ifes? | RC → TC | S | — ; texto explicativo "Exemplo: 2020, 2021, 2022, etc." | — | I | S3·1 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Referência temporal da Conclusão existe na 001 (001, FR-009 g), mas a fonte é simulada e a qualidade da real é pendente (001/DP-001, 001/DP-004). Permanece textual (002, FR-037; DP-307). |
| Q11 | Em qual campus você concluiu seu curso? | LS → EU | S | Lista C (23) | — | I | S3·2 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Unidade existe na 001 (FR-009 c). Opções são alternativas históricas, não catálogo de unidades (FR-030; DP-307). |
| Q12 | Você é egresso(a) de qual modalidade? | LS → EU | S | Presencial; À distância (2) | — | I | S3·3 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Modalidade existe na 001 (FR-009 e); vocabulário pendente (001/DP-007; DP-307). Sobreposição com rótulos "EaD - …" das listas (O-14). |
| Q13 | Você foi admitido(a) ao curso do Ifes como estudante: | LS → EU | S | Cotista (vagas de cotas, ações afirmativas); Não cotista (vagas de ampla concorrência); Outros: transferência, remoção, reopção, reingresso, novo curso, etc. (3) | — | I | S3·4 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | **Não representada na 001** (forma de ingresso fora do contexto mínimo; 001, FR-012) e esta feature não a acrescenta (FR-041). Mistura reserva de vagas e forma de ingresso (O-12). Opções preservadas (DP-307). |
| Q14 | Indique o questionário que pretende preencher | ME → EU | S | Ensino Médio/Técnico Integrado; Técnico Concomitante/Subsequente/EJA-PROEJA; Graduação; Pós-Graduação (4) | → S4, S5, S6, S7 → mantidas | I | S3·5 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Nível existe na 001 (FR-009 d), com vocabulário pendente (001/DP-007). "Questionário" equivale a nível (O-13). Também decide o ramo de cursos: retirá-la exige tratar a navegação (DP-307). |

### Seções 4 a 7 — Curso por nível

| Nº | Texto original | Tipo | Obr. | Opções / escala | Navegação | Orig. | Pos. | Tratamento | Justificativa |
|----|----------------|------|------|-----------------|-----------|-------|------|------------|---------------|
| Q15 | Você é egresso(a) de qual Curso? | LS → EU | S | Lista 15 (33), de "Fiz apenas o Ensino Médio" a "Técnico em Zootecnia" | S4 → Q20 → encaminhamento S4 → S8 | I | S4·1 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Curso existe na 001 (FR-009 b). Lista histórica, não catálogo (FR-030; O-14; DP-307). |
| Q16 | Você é egresso(a) de qual forma de oferta? | LS → EU | S | Concomitante; Subsequente; EJA-PROEJA (3) | — | I | S5·1 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Forma de oferta existe na 001 (FR-009 f); vocabulário pendente (001/DP-007; DP-307). |
| Q17 | Você é egresso(a) de qual Curso? | LS → EU | S | Lista 17 (47), de "Técnico em Administração" a "Técnico em Treinamento e Instrução de Cães-Guia" | S5 → Q20 → encaminhamento S5 → S8 | I | S5·2 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Idem Q15. |
| Q18 | Você é egresso(a) de qual Curso? | LS → EU | S | Lista 18 (50), de "EaD - Complementação Pedagógica: Matemática, Física, Biologia e Química" a "Tecnologia em Sistemas para Internet" | S6 → Q20 → encaminhamento S6 → S8 | I | S6·1 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Idem Q15; modalidade embutida em rótulos "EaD - …" preservada (O-14). |
| Q19 | Você é egresso(a) de qual Curso? | LS → EU | S | Lista 19 (77), de "Aperfeiçoamento em Educação para o Trânsito" a "Mestrado Profissional em Tecnologias Sustentáveis" | S7 → Q20 → encaminhamento S7 → S8 | I | S7·1 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Idem Q15. A nota interna da Seção 7 não é migrada (E-05) e sua sugestão não é executada: nenhum curso acrescentado (O-3, O-5; DP-310). |

### Seção 8 — Avaliação

| Nº | Texto original | Tipo | Obr. | Opções / escala | Navegação | Orig. | Pos. | Tratamento | Justificativa |
|----|----------------|------|------|-----------------|-----------|-------|------|------------|---------------|
| Q20 | Indique o seu grau de concordância com a afirmação "Após o curso no Ifes, meu gosto por cultura, em geral, aumentou." | EL → ESC | S | 1–5; inicial ausente; final "Concordo totalmente" | — | Dc | S8·1 | MANTER_COM_OBSERVAÇÃO | Rótulo inicial não confirmado (E-09; DP-301). |
| Q21 | Indique o seu grau de concordância com a afirmação "Após o curso no Ifes, meu acesso à cultura, em geral, aumentou." | EL → ESC | S | idem Q20 | — | Dc | S8·2 | MANTER_COM_OBSERVAÇÃO | Idem Q20. |
| Q22 | Você participou de ações de extensão durante o curso? | LS → EU | S | Sim; Não (2) | — | I? | S8·3 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Fonte institucional de extensão não verificada; permanece declarada (O-11; DP-308). |
| Q23 | Você foi monitor(a) de disciplinas durante o curso? | LS → EU | S | Sim; Não (2) | — | I? | S8·4 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Idem Q22 (monitoria). |
| Q24 | Você fez algum tipo de estágio durante o curso? | LS → EU | S | Sim; Não (2) | — | I? | S8·5 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Idem Q22 (estágio). |
| Q25 | Você participou de atividades acadêmicas (seminários, feiras, jornadas, etc) durante o curso? | LS → EU | S | Sim; Não (2) | — | Dc | S8·6 | MANTER | — |
| Q26 | Que tipo de publicação você realizou durante o curso? | CS → EM | S | Artigos técnico científicos; Anais de Congresso; Livro; Capítulos de livro; Não houve; Outro: (6; "Outro:" com complemento textual) | — | Dc | S8·7 | MANTER_COM_OBSERVAÇÃO | "Não houve" não é exclusiva, como no original (002, FR-036; 002/DP-005). |
| Q27 | Você fez intercâmbio no exterior durante o curso? | LS → EU | S | Sim; Não (2) | — | I? | S8·8 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Idem Q22 (intercâmbio). |
| Q28 | Durante o curso, você participou das atividades de grupos de pesquisas e de estudos? | LS → EU | S | Sim; Não (2) | — | Dc | S8·9 | MANTER | — |
| Q29 | Você mantém algum vínculo com o curso, como participação em grupos de pesquisa ou de estudos? | LS → EU | S | Sim; Não (2) | — | Dc | S8·10 | MANTER | — |
| Q30 | Você foi membro de empresa júnior durante o curso no Ifes? | LS → EU | S | Sim; Não (2) | — | Dc | S8·11 | MANTER | — |
| Q31 | Você participou de iniciação científica? | LS → EU | S | Sim; Não (2) | — | I? | S8·12 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Idem Q22 (iniciação científica). |
| Q32 | Você recebeu algum tipo de bolsa? | CS → EM | S | Ensino; Pesquisa; Extensão; Não recebi; Outro: (5; "Outro:" com complemento textual); texto explicativo "Obs: Não considerar auxilio estudantil como bolsa." | — | I? | S8·13 | CANDIDATA_A_CONTEXTO_INSTITUCIONAL | Idem Q22 (bolsas). Grafia "auxilio" preservada (E-19). "Não recebi" não exclusiva (002/DP-005). |
| Q33 | Atualmente você trabalha? | ME → EU | S | Sim; Não (2) | "Sim" → Q34; "Não" → Q45 → S9; S10 | Dc | S8·14 | MANTER | Ramificação intencional preservada. |

### Seção 9 — Egresso que trabalha

| Nº | Texto original | Tipo | Obr. | Opções / escala | Navegação | Orig. | Pos. | Tratamento | Justificativa |
|----|----------------|------|------|-----------------|-----------|-------|------|------------|---------------|
| Q34 | Você trabalha no setor: | LS → EU | S | Misto; Público; Privado; Terceiro setor (cooperativas/sindicatos); Trabalho em mais de um setor (5) | — | Dc | S9·1 | MANTER | — |
| Q35 | O seu cargo/emprego exige como requisito o seguinte nível de escolaridade: | LS → EU | S | Nenhum nível de instrução; Ensino fundamental; Ensino médio/técnico; Graduação; Pós-graduação; Não sei dizer (6) | — | Dc | S9·2 | MANTER | — |
| Q36 | Indique o seu grau de concordância com a afirmação "O meu trabalho atual é na minha área de formação do curso do Ifes." | EL → ESC | S | idem Q20 | — | Dc | S9·3 | MANTER_COM_OBSERVAÇÃO | Idem Q20. |
| Q37 | Você exerce cargo de chefia ou de direção atualmente? | LS → EU | S | Sim; Não (2) | — | Dc | S9·4 | MANTER | — |
| Q38 | Qual é a remuneração bruta mensal do seu trabalho? | LS → EU | S | Até 1 salário mínimo; De 1 até 2,5 salários mínimos; De 2,5 até 5,5 salários mínimos; De 5,5 até 10 salários mínimos; Acima de 10 salários mínimos (5) | — | Dc | S9·5 | MANTER_COM_OBSERVAÇÃO | Limites sobrepostos preservados (O-18); comparação em salários mínimos depende do momento da Participação (O-19). Questão metodológica (DP-305). |
| Q39 | A organização na qual você trabalha é: | LS → EU | S | Micro empresa/organização (até 19 colaboradores); Pequena empresa/organização (de 20 a 99 colaboradores); Média empresa/organização (de 100 a 499 colaboradores); Grande empresa/organização (acima de 500 colaboradores); Não sei dizer (5) | — | Dc | S9·6 | MANTER_COM_OBSERVAÇÃO | Lacuna do valor 500 preservada (O-18; DP-305). |
| Q40 | Você trabalha atualmente: | LS → EU | S | Na mesma cidade do campus do Ifes onde fiz o curso; Em outra cidade, mas na mesma região do campus do Ifes onde fiz o curso; Em outra cidade e em outra região do campus do Ifes onde fiz o curso, mas ainda no estado do Espírito Santo; Em outro estado brasileiro; Em outro país (5) | — | Dc | S9·7 | MANTER_COM_OBSERVAÇÃO | Referência ao "campus" ambígua para EaD/Cefor; não substituída por polo ou município (O-20; DP-306). |
| Q41 | Como você avalia a oferta de vagas aos profissionais da sua área de formação no Ifes? | LS → EU | S | Não existem vagas de trabalho; Existem poucas vagas de trabalho; Existem muitas vagas de trabalho; Não sei dizer (4) | — | Dc | S9·8 | MANTER_COM_OBSERVAÇÃO | Descrição "Verificar lugar dessa pergunta" é nota interna: não migrada (E-06). Posição mantida; a sugestão não é executada (O-3; DP-310). |
| Q42 | Indique o seu grau de concordância com a afirmação "A realização de curso no Ifes foi indispensável para que eu conseguisse o meu trabalho atual. Sem ele, eu não teria o emprego que tenho hoje." | EL → ESC | **N** | idem Q20 | — | Dc | S9·9 | MANTER_COM_OBSERVAÇÃO | Opcional preservada, embora Q43 seja obrigatória (O-10; DP-304). Rótulo inicial (DP-301). |
| Q43 | Indique o seu grau de concordância com a afirmação "A minha experiência profissional anterior foi indispensável para que eu conseguisse o meu trabalho atual." | EL → ESC | S | idem Q20 | — | Dc | S9·10 | MANTER_COM_OBSERVAÇÃO | Rótulo inicial (DP-301). Obrigatoriedade não alterada para alinhar com Q42/Q44 (DP-304). |
| Q44 | Indique o seu grau de concordância com a afirmação "Eu usei as minhas redes de contato do Ifes para conseguir o meu trabalho atual." | EL → ESC | **N** | idem Q20 | — | Dc | S9·11 | MANTER_COM_OBSERVAÇÃO | Idem Q42. |

### Seção 10 — Egresso que não trabalha

| Nº | Texto original | Tipo | Obr. | Opções / escala | Navegação | Orig. | Pos. | Tratamento | Justificativa |
|----|----------------|------|------|-----------------|-----------|-------|------|------------|---------------|
| Q45 | Você não está trabalhando por qual motivo: | ME → EU | S | Não encontrei vaga de trabalho, mas estou à procura; Não estou à procura de vaga de trabalho no momento; Outro: (3; "Outro:" com complemento textual) | S10 → Q46 → encaminhamento S10 → S11 | Dc | S10·1 | MANTER | — |

### Seção 11 — Estudo

| Nº | Texto original | Tipo | Obr. | Opções / escala | Navegação | Orig. | Pos. | Tratamento | Justificativa |
|----|----------------|------|------|-----------------|-----------|-------|------|------------|---------------|
| Q46 | Atualmente você estuda? | ME → EU | S | Sim; Não (2) | "Sim" → Q49; "Não" → Q52, ao sair da seção → S12; S13, sem momento de aplicação | Dc | S11·1 | MANTER_COM_OBSERVAÇÃO | Única pergunta com regras seguida de outras na mesma Seção. Ordem preservada; momento de aplicação não fixado; requisito para a 004 (FR-026; O-15; DP-302). |
| Q47 | Após o curso, você: | CS → EM | S | Não estudei mais; Fiz cursos livres; Fiz curso técnico; Fiz curso de graduação; Fiz especialização lato sensu; Fiz mestrado; Fiz doutorado; Fiz pós-doutorado (8) | apresentada a todos que chegam a S11 → posição preservada | Dc / I? | S11·2 | MANTER_COM_OBSERVAÇÃO | No original é exibida a todos que chegam a S11 (O-15; DP-302). Parcialmente candidata se a formação posterior for no Ifes (DP-308). "Não estudei mais" não exclusiva (002/DP-005). |
| Q48 | Indique o seu grau de concordância com a afirmação "O curso que realizei, citado acima, estava totalmente relacionado à área do meu curso do Ifes." | EL → ESC | **N** | 1–5; inicial ausente; final "concordo totalmente"; texto explicativo "Caso não tenha estudado mais deixe essa resposta em branco." | condição só textual → idem | Dc | S11·3 | MANTER_COM_OBSERVAÇÃO | Condição textual preservada no texto explicativo, sem condição técnica (O-15; DP-302). Minúsculas preservadas (E-10). Rótulo inicial (DP-301). |

### Seção 12 — Egresso que estuda

| Nº | Texto original | Tipo | Obr. | Opções / escala | Navegação | Orig. | Pos. | Tratamento | Justificativa |
|----|----------------|------|------|-----------------|-----------|-------|------|------------|---------------|
| Q49 | Em qual categoria de estudante você se enquadra atualmente? | LS → EU | S | Sou estudante de curso técnico; Sou estudante de curso de graduação; Sou estudante de curso de especialização lato sensu; Sou estudante de mestrado; Sou estudante de doutorado; Sou estudante de pós-doutorado (6) | — | Dc / I? | S12·1 | MANTER_COM_OBSERVAÇÃO | Parcialmente candidata se o curso atual for no Ifes; fonte não verificada (DP-308). |
| Q50 | Indique o seu grau de concordância com a afirmação "O curso que estou realizando está totalmente relacionado à área do meu curso do Ifes." | EL → ESC | S | idem Q20 | — | Dc | S12·2 | MANTER_COM_OBSERVAÇÃO | Rótulo inicial (DP-301). |
| Q51 | A instituição na qual você está cursando é: | ME → EU | S | Ifes; Outra Instituição Pública; Instituição Privada (3) | "Instituição Privada" → Q52 (= padrão) → **sem regra**; S12 → S13 por encaminhamento | Dc / I? | S12·3 | MANTER_COM_OBSERVAÇÃO | Pergunta e Opções preservadas; regra sem efeito omitida (E-07; O-16; FR-024). Parcialmente candidata se "Ifes" (DP-308). |

### Seção 13 — (sem título)

| Nº | Texto original | Tipo | Obr. | Opções / escala | Navegação | Orig. | Pos. | Tratamento | Justificativa |
|----|----------------|------|------|-----------------|-----------|-------|------|------------|---------------|
| Q52 | Indique o seu grau de concordância com a afirmação "O meu curso no Ifes mudou a minha vida para melhor. Hoje, eu me considero uma pessoa diferente de quem eu era antes do Ifes." | EL → ESC | S | 1–5; inicial ausente; final "Corcordo totalmente" → "Concordo totalmente" | S13 → fim → fluxo padrão | Dc | S13·1 | CORREÇÃO_EDITORIAL_EXPLÍCITA | Grafia corrigida sem mudança de significado (E-08; FR-021; O-4). Rótulo inicial (DP-301). |
| Q53 | Indique o seu grau de concordância com a afirmação "A situação econômica da minha família melhorou após eu ter concluído o curso no Ifes." | EL → ESC | S | idem Q52 | — | Dc | S13·2 | CORREÇÃO_EDITORIAL_EXPLÍCITA | Idem Q52. |
| Q54 | Indique o seu grau de concordância com a afirmação "Eu acredito que sou exemplo e inspiração para outras pessoas (amigos, colegas, familiares) se espelharem e ampliarem seus horizontes de estudos e profissionais." | EL → ESC | S | idem Q52 | — | Dc | S13·3 | CORREÇÃO_EDITORIAL_EXPLÍCITA | Idem Q52. |

### Matriz de elementos (conteúdo que não é pergunta)

| ID | Elemento original | Representação na baseline | Categoria | Justificativa |
|----|-------------------|---------------------------|-----------|---------------|
| E-01 | Título exibido "Egresso Ifes" | Título apresentado da Versão | MANTER | 002, FR-010. |
| E-02 | Texto de abertura (convite, quatro parágrafos, com e-mail e telefone de contato) | Texto de abertura da Versão, integral | MANTER | Conteúdo editorial preservado. Atualidade dos contatos não verificada (Edge Cases). |
| E-03 | Seção 1 "Termos e condições" com o texto dos termos (dois parágrafos) | Título e texto introdutório de S1 | MANTER_COM_OBSERVAÇÃO | Texto preservado; não é termo de consentimento versionado nem registro de consentimento (002/DP-007). |
| E-04 | Seção 14 "Este formulário chegou ao fim!" + agradecimento | Texto de encerramento da Versão; **não** é Seção | MANTER | Tela final como Seção é acidente da ferramenta (002, FR-010; tabela de cobertura da 002). O conteúdo é preservado. |
| E-05 | Descrição da Seção 7: "Tem que atualizar a lista de cursos, adicionando doutorado" | Ausente; S7 sem texto introdutório | NÃO_MIGRAR_COMO_CONTEÚDO | Nota interna de edição, não dirigida ao egresso (O-3). Sugestão não executada (O-5; DP-310). |
| E-06 | Descrição de Q41: "Verificar lugar dessa pergunta" | Ausente; Q41 sem texto explicativo | NÃO_MIGRAR_COMO_CONTEÚDO | Nota interna de edição (O-3). Posição de Q41 mantida (DP-310). |
| E-07 | Regra de Q51: "Instituição Privada" → Q52 | Não reproduzida | NAVEGAÇÃO_REDUNDANTE | Nenhuma resposta a Q51 muda o percurso (O-16). |
| E-08 | Rótulo final "Corcordo totalmente" em Q52, Q53, Q54 | "Concordo totalmente" | CORREÇÃO_EDITORIAL_EXPLÍCITA | Grafia, sem mudança de significado; baseline nova em RASCUNHO (FR-021; O-4). |
| E-09 | Rótulo inicial truncado "Disc…" / "disc…" nas 11 escalas | Ausente | DECISÃO_PENDENTE | Texto exato não legível na fonte versionada; não é inventado (FR-018; DP-301). |
| E-10 | Rótulos de Q48 em minúsculas ("disc…" / "concordo totalmente") | Rótulo final "concordo totalmente" | MANTER | Sem correção por inferência (FR-021). |
| E-11 | Seção 13 sem título visível | S13 com título ausente | MANTER | 002, FR-025. Nenhum título inventado. |
| E-12 | Ramificação aplicada ao sair da Seção (Q46 seguida de Q47 e Q48) | Regras em Q46; ordem preservada; sem atributo de momento | DECISÃO_PENDENTE | Intenção vs. acidente não confirmada; execução pertence à 004 (FR-026; DP-302). |
| E-13 | Distinção "múltipla escolha" (botões) × "lista suspensa" | Ambas escolha única | MANTER | Forma de apresentação não é tipo (002, FR-035); significado preservado. |
| E-14 | Numeração Q1–Q54 | Não gravada; correspondência pela ordem | MANTER | FR-012; 002, FR-033. |
| E-15 | Opção "Outro:" com campo de texto em Q26, Q32, Q45 | Opção "Outro:" com complemento textual | MANTER | 002, FR-042. Texto transcrito preservado. |
| E-16 | Descrições de pergunta Q10, Q32, Q48 | Textos explicativos | MANTER | 002, FR-030. |
| E-17 | Navegação ao fim das Seções (convergências) | 7 encaminhamentos | MANTER | FR-025. |
| E-18 | Configuração externa do Google Formulários (coleta de e-mail, login) | Não representada | MANTER (fora do conteúdo) | Não verificada e não é conteúdo do instrumento (O-1). |
| E-19 | Particularidades de grafia no conteúdo apresentado (por exemplo, "auxilio" em Q32, "técnico científicos" em Q26, "Micro empresa" em Q39, "etc)" em Q25, espaçamento do título de S5) | Preservadas | MANTER | Somente E-08 foi aprovada como correção (FR-021). |

## Contagens verificáveis

**Instrumento original × baseline**

| Item | Original | Baseline |
|------|---------:|---------:|
| Perguntas | 54 | 54 |
| Seções com perguntas | 13 | 13 |
| Tela final como Seção | 1 | 0 (texto de encerramento) |
| Perguntas de escolha única (ME + LS) | 38 (8 + 30) | 38 |
| Perguntas de escolha múltipla | 3 | 3 |
| Perguntas de resposta textual curta | 2 | 2 |
| Perguntas de escala (1–5) | 11 | 11 |
| Perguntas obrigatórias / opcionais | 50 / 4 | 50 / 4 |
| Perguntas com Opções | 41 | 41 |
| Opções | 385 | 385 |
| Opções com complemento textual | 3 | 3 |
| Perguntas com texto explicativo | 4 (Q10, Q32, Q41, Q48) | 3 (Q41 sem a nota interna) |
| Seções com texto introdutório | 2 (S1, S7) | 1 (S1) |
| Seções sem título | 1 (S13) | 1 |
| Destinos por resposta registrados no inventário (Q1: 2, Q14: 4, Q33: 2, Q46: 2, Q51: 1) | 11 | 10 regras (Q51 omitida — E-07) |
| Encaminhamentos explícitos de Seção | — (não distinguíveis no inventário) | 7 |
| Percursos de Seções possíveis | 17 | 17 |

**Por tratamento (perguntas — categoria principal, FR-037)**

| Categoria | Qtd. | Perguntas |
|-----------|-----:|-----------|
| MANTER | 11 | Q8, Q9, Q25, Q28, Q29, Q30, Q33, Q34, Q35, Q37, Q45 |
| MANTER_COM_OBSERVAÇÃO | 23 | Q1, Q2, Q4, Q5, Q6, Q7, Q20, Q21, Q26, Q36, Q38, Q39, Q40, Q41, Q42, Q43, Q44, Q46, Q47, Q48, Q49, Q50, Q51 |
| CORREÇÃO_EDITORIAL_EXPLÍCITA | 3 | Q52, Q53, Q54 |
| CANDIDATA_A_CONTEXTO_INSTITUCIONAL | 17 | Q3, Q10–Q19, Q22, Q23, Q24, Q27, Q31, Q32 |
| NÃO_MIGRAR_COMO_CONTEÚDO | 0 | — (nenhuma pergunta deixa de ser migrada) |
| NAVEGAÇÃO_REDUNDANTE | 0 | — (aplica-se a elemento: E-07) |
| DECISÃO_PENDENTE | 0 | — (aplica-se a elementos: E-09, E-12) |
| **Total** | **54** | |

**Respostas às perguntas de contagem**

| Pergunta | Resposta |
|----------|----------|
| Perguntas originais | 54 |
| Representadas como Perguntas na baseline | 54 |
| Com apenas correção editorial | 3 (Q52–Q54; 1 correção aprovada, 3 ocorrências — E-08) |
| Conteúdos editoriais internos excluídos | 2 (E-05, E-06) |
| Regras de navegação omitidas por redundância | 1 (E-07, Q51) |
| Candidatas a contexto institucional | 17 (11 acadêmicas: Q10–Q19 + Q3 como derivada; 6 a investigar: Q22, Q23, Q24, Q27, Q31, Q32); mais 3 parcialmente candidatas (Q47, Q49, Q51) |
| Decisões pendentes | 10 novas (DP-301 a DP-310) e 10 herdadas que continuam abertas (ver "Decisões Pendentes") |

Esta feature não tem meta de redução de perguntas.

## Suficiência da Feature 002

Cada necessidade da baseline foi confrontada com uma capacidade existente da 002. **Nenhuma
limitação bloqueante foi encontrada.**

| Necessidade da baseline | Capacidade da 002 | Situação |
|-------------------------|-------------------|----------|
| Título, abertura e encerramento | Textos da Versão (FR-010) | Suficiente |
| Termos como texto de Seção | Título e texto introdutório de Seção (FR-025) | Suficiente |
| S13 sem título; S7 sem texto | Textos opcionais explicitamente ausentes (FR-025) | Suficiente |
| 4 tipos (EU, EM, TC, ESC) | Exatamente os 4 tipos (FR-034) | Suficiente |
| Listas de até 77 Opções | Sem limite de Opções (FR-044) | Suficiente |
| Textos de Opção únicos na pergunta | Restrição FR-058 (m) | Suficiente: as listas do inventário foram conferidas e não têm textos repetidos em nenhuma pergunta |
| "Outro:" com texto livre | Complemento textual, no máximo 1 por pergunta (FR-042) | Suficiente: Q26, Q32 e Q45 têm 1 cada |
| Escala 1–5 sem rótulo inicial | Rótulos opcionais (FR-038) | Suficiente |
| Q6, Q42, Q44, Q48 opcionais | Obrigatoriedade por Pergunta (FR-029) | Suficiente |
| Finalização por Q1 = "Não" | Regra "finalizar" (FR-050) | Suficiente |
| Ramificações Q14, Q33, Q46 | Regra por Opção, destino posterior (FR-050, FR-055) | Suficiente |
| Convergências | Encaminhamento de Seção (FR-049) | Suficiente |
| Momento de aplicação não fixado | FR-053 | Suficiente (por desenho) |
| Verificar completude sem publicar | Condições de completude (FR-059), verificáveis sem transição de estado | Suficiente |
| Rastreabilidade Qn sem atributo | Ordem explícita e total (FR-045, FR-046) | Suficiente |

Observações não bloqueantes (nenhum ajuste proposto à 002):

- A 002 não exige nome de Pesquisa único (002, FR-002). A ambiguidade é tratada na
  materialização (FR-031), sem alterar a 002.
- A forma de apresentação (botões × lista suspensa) não é representada (002, FR-035). Se a
  004 precisar dela, deverá demonstrar o caso concreto em spec própria.

## Relação com outras features

**Feature 001** — usada apenas como referência do que já tem representação canônica:
curso, unidade, nível, modalidade, forma de oferta e referência temporal da conclusão
(001, FR-009). Não há representação para forma de ingresso (Q13), data de nascimento (Q3)
nem atividades de Q22–Q32. Nada da 001 é alterado (FR-041). Permanecem abertas
001/DP-001, 001/DP-004 e 001/DP-007, que a 001 remetia à "spec de migração": esta spec
**não** as resolve, porque a fonte real e seu vocabulário continuam desconhecidos.

**Feature 002** — consumida integralmente, sem alteração (FR-040; "Suficiência da Feature
002").

**Feature 004 (jornada de resposta)** — recebe da 003:

- a baseline estruturada (textos, Seções, Perguntas, Opções, escalas, obrigatoriedades,
  ordem, regras e encaminhamentos);
- os 17 percursos esperados;
- o requisito de FR-026: no instrumento original, Q47 e Q48 são apresentadas a todos que
  chegam a S11; a 004 define o momento de aplicação das regras e NÃO DEVE suprimir Q47 e
  Q48 sem decisão explícita (DP-302);
- Q6 como pergunta opcional apresentada sem condição técnica (DP-303);
- Q48 com condição apenas textual;
- Q1 como representação do termo vigente, sem consentimento operacional (002/DP-007) e com
  o comportamento de recusa (O-17) a tratar na jornada;
- as decisões pendentes desta spec.

**Futura contextualização acadêmica** — decidirá, com base no contexto efetivamente
disponível, quais candidatas (Q3, Q10–Q19, Q22–Q24, Q27, Q31, Q32 e, parcialmente, Q47,
Q49, Q51) deixam de ser apresentadas, na cadeia **Pessoa → Conclusão Acadêmica → contexto
conhecido → apenas perguntas necessárias**, sem reescrever a baseline (DP-307, DP-308).
Isso deve ocorrer por nova Versão ou por mecanismo da jornada, não por edição retroativa de
Versão usada em coleta.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das 54 perguntas originais (Q1–Q54) têm exatamente uma linha na Matriz,
  com posição na baseline, categoria e justificativa, e a soma por categoria é 54.
- **SC-002**: A baseline materializada coincide com 100% das contagens de "Contagens
  verificáveis" (Seções, Perguntas por tipo, obrigatoriedades, Opções, complementos,
  escalas, textos explicativos, regras, encaminhamentos, percursos).
- **SC-003**: Para 100% das 41 perguntas com Opções, a quantidade, os textos e a ordem das
  Opções coincidem com a Matriz; remover ou trocar a ordem de qualquer Opção ou Pergunta na
  baseline faz pelo menos uma verificação automatizada falhar.
- **SC-004**: A dedução de percursos da baseline produz exatamente os 17 percursos
  esperados, e Q1 = "Não" leva à finalização sem nenhuma outra Seção.
- **SC-005**: 0 ocorrências, em todos os textos da baseline, das duas notas internas e de
  "Corcordo"; exatamente 3 rótulos finais corrigidos (Q52–Q54).
- **SC-006**: A Versão da baseline está em RASCUNHO em 100% das execuções da
  materialização e da verificação; nenhuma execução a publica.
- **SC-007**: Executar a materialização 2 ou mais vezes resulta em exatamente 1 Pesquisa
  com o nome e 1 Versão com a designação da baseline, com as mesmas identidades da primeira
  execução, e 0 duplicatas.
- **SC-008**: 0 alterações em modelo, operações ou contratos das Features 001 e 002; as
  verificações dessas features continuam passando sem alteração.
- **SC-009**: 0 entidades ou registros de Campanha, Participação, Resposta, Curso ou
  Conclusão Acadêmica criados pela materialização.
- **SC-010**: Cada observação metodológica preservada (O-6, O-7, O-8, O-10, O-12, O-13,
  O-14, O-15, O-18, O-19, O-20) aponta para uma `DECISÃO PENDENTE` própria ou herdada.
- **SC-011**: Cada um dos 12 critérios de sucesso da descrição original pode ser
  respondido com "sim" apontando requisitos, tabelas e cenários desta spec.

## Assumptions

Apenas suposições não institucionais. As regras institucionais em aberto estão em
Decisões Pendentes.

- O inventário versionado é a fonte desta migração. A exportação original em PDF é arquivo
  local não versionado (SHA-256 registrado no inventário); quando consultada, divergências
  são registradas, não corrigidas em silêncio (FR-007).
- A ordem das Opções no inventário reproduz a ordem do original.
- Seções e perguntas para as quais o inventário não registra descrição não têm descrição
  no original.
- O rótulo final das escalas de Q36, Q42–Q44 e Q50 é "Concordo totalmente", conforme a
  tabela "Tipos de pergunta usados" do inventário, que só registra exceções para Q48 e
  Q52–Q54.
- A designação da Versão (FR-004) é administrativa; o que é apresentado ao egresso é o
  título "Egresso Ifes".
- O volume é pequeno (1 Versão, 54 Perguntas, 385 Opções) e não há metas de desempenho.
- A dedução de percursos usada nas verificações segue as regras de precedência da 002
  (002, FR-048, FR-054) e não constitui execução da jornada.

Decisões de escopo confirmadas pelo solicitante em 2026-10-01 (antes hipóteses):

- **Designação da baseline**: "Formulário Egresso Ifes 2024 — referência migrada"; baseline
  técnica, não publicação nem aprovação institucional (FR-004).
- **Baseline existente divergente**: falha explícita sem nenhuma alteração; equivalente →
  no-op (FR-032, FR-033).

## Invariantes Constitucionais Afetados *(mandatory)*

- **III — Dado institucional não é resposta (NON-NEGOTIABLE)**: perguntas acadêmicas
  continuam perguntas declaradas e são apenas marcadas como candidatas (FR-029). Nenhuma
  lista do formulário vira dado institucional (FR-030). Nenhum mecanismo de "perguntar se a
  fonte não tiver" é criado.
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: textos, Opções, escalas, ordem e
  condicionais preservados e verificados (FR-007 a FR-026, FR-038, FR-039). A única
  correção é explícita e anterior a qualquer uso (FR-021).
- **X — Tecnologia não redefine a governança (NON-NEGOTIABLE)**: a Versão fica em RASCUNHO
  e não é publicada (FR-003). A competência para publicar continua em 002/DP-001.
- **XIII — Instrumento atual é referência inicial**: a migração preserva significado e
  separa acidentes (E-04, E-07, E-13) de intenção, com origem de cada requisito etiquetada.
- **XIV — Redução futura de fricção**: as candidatas a contexto estão identificadas
  (FR-029) para que feature futura reduza a jornada sem reescrever a baseline.
- **XVI — Privacidade e minimização (NON-NEGOTIABLE)**: nenhum dado pessoal é criado.
  Perguntas com dados potencialmente sensíveis são preservadas sem decidir seu tratamento
  (DP-309).
- **XVII — Consentimento**: Q1 e os termos são conteúdo do instrumento, não registro de
  consentimento (Q1, E-03; 002/DP-007).
- **XXII — Simplicidade/YAGNI**: nenhuma entidade, campo, enumeração ou tabela nova
  (FR-012, FR-036, FR-040). A materialização é idempotente sem mecanismo de reconciliação
  (FR-033).
- **XXIII — Não é form builder**: nenhuma condição de exibição, motor de regras ou novo
  tipo; Q6 e Q48 permanecem sem condição técnica.
- **XXVI — Testes protegem invariantes**: verificações de fidelidade independentes da
  declaração de materialização (FR-038, FR-039).
- **XXVIII — Desenvolvimento orientado por specs**: toda diferença em relação ao original
  está na Matriz (FR-035).
- **XXIX — Hipóteses não viram requisitos (NON-NEGOTIABLE)**: lacunas não são preenchidas
  (FR-018), irregularidades não são "corrigidas" (FR-011), e divergência da baseline
  interrompe a materialização em vez de ser resolvida por suposição (FR-033).
- **I, II, VII, XI — Longitudinalidade, egresso, conceitos distintos, identidade**: não
  afetados. Nenhuma Pessoa, Conclusão, Campanha, Participação ou Resposta é criada ou
  alterada (FR-041, FR-042).

Nenhum conflito com a Constituição, com a PAEG ou com as Features 001 e 002 foi
identificado.

## Out of Scope *(mandatory)*

- Jornada pública do egresso, formulário HTML, renderização, paginação.
- Resposta, Participação, Campanha, população elegível, periodicidade.
- Autosave, retomada, sessão, progresso, validação de preenchimento.
- Autenticação, OTP, login, identificação do respondente.
- Consentimento juridicamente operacional e associação Pessoa → Participação.
- Supressão dinâmica de perguntas por contexto acadêmico.
- Integração acadêmica real; alteração da Feature 001 (forma de ingresso, data de
  nascimento, atividades acadêmicas).
- Alteração da Feature 002, novos tipos de pergunta, condição de exibição por pergunta,
  motor de regras, atributo de momento de aplicação de regra.
- Editor administrativo, workflow de aprovação, publicação da Versão.
- Dashboard, indicadores, exportação.
- Importação de respostas históricas do Google Formulários.
- Revisão metodológica do instrumento e execução das sugestões das notas internas.
- Catálogo acadêmico derivado das listas do Google Formulários.
- Correspondência formal entre a baseline e o formulário do Google para séries históricas
  (002/DP-006).

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: as decisões novas usam o prefixo 3 (DP-301…) para não colidir com DP-001…
das Features 001 e 002, citadas como 001/DP-nnn e 002/DP-nnn.

**Novas nesta feature**

- **DP-301** — DECISÃO PENDENTE: texto exato do rótulo inicial das 11 escalas (truncado
  como "Disc…"/"disc…" na fonte), se é igual em todas e qual a caixa em Q48. Instância
  competente: confirmação documental na fonte original autorizada (responsáveis pelo
  formulário vigente — Proex/CPAEG). Impacto: E-09, FR-018, FR-019. Tratamento provisório:
  rótulo inicial ausente. A Versão permanece em RASCUNHO, de modo que a pendência não
  bloqueia esta feature, mas DEVERIA ser resolvida antes de qualquer publicação.
- **DP-302** — DECISÃO PENDENTE: se é intenção do instrumento que Q47 e Q48 sejam
  apresentadas a todos que chegam à Seção de estudo (como hoje) ou se isso é acidente da
  ferramenta; e, consequentemente, a semântica de execução das regras. Instância
  competente: CPAEG, para a intenção metodológica; Feature 004, para a semântica de
  execução. Impacto: FR-026, E-12. Tratamento provisório: ordem e regras preservadas, sem
  momento de aplicação registrado; a 004 não suprime Q47/Q48 sem decisão explícita.
- **DP-303** — DECISÃO PENDENTE: se Q6 deve ter condicional explícita a Q5 = "Sim".
  Instância competente: CPAEG. Impacto: Q6; eventual capacidade nova seria 002/DP-005.
  Tratamento provisório: Q6 opcional, sem condição, como no original.
- **DP-304** — DECISÃO PENDENTE: se a opcionalidade de Q42 e Q44 (com Q43 obrigatória) é
  intencional. Instância competente: CPAEG. Impacto: obrigatoriedade das três. Tratamento
  provisório: como no original.
- **DP-305** — DECISÃO PENDENTE: revisão das faixas de Q38 (limites sobrepostos) e de Q39
  (valor 500 sem faixa) e da referência em salários mínimos, considerando comparabilidade
  histórica. Instância competente: CPAEG. Impacto: Q38, Q39, séries históricas.
  Tratamento provisório: faixas originais.
- **DP-306** — DECISÃO PENDENTE: referência geográfica de Q40 para formações a distância
  (Cefor/EaD). Instância competente: CPAEG. Impacto: interpretação de Q40. Tratamento
  provisório: texto original com "campus".
- **DP-307** — DECISÃO PENDENTE: quais perguntas acadêmicas (Q10–Q19) e Q3 deixarão de
  ser apresentadas quando houver contexto institucional, incluindo como tratar Q13 (sem
  representação na 001), Q14 (que também decide o ramo de cursos) e a correspondência
  entre as Opções do formulário e o vocabulário canônico. Depende de 001/DP-001,
  001/DP-004 e 001/DP-007. Instância competente: CPAEG, com as áreas de ensino e quem
  administra a fonte acadêmica. Impacto: jornada contextualizada futura. Tratamento
  provisório: todas na baseline, como perguntas declaradas.
- **DP-308** — DECISÃO PENDENTE: existência e qualidade de fontes institucionais para
  extensão, monitoria, estágio, intercâmbio, iniciação científica e bolsas (Q22, Q23, Q24,
  Q27, Q31, Q32) e para formações e cursos atuais no Ifes (parte de Q47, Q49, Q51).
  Instância competente: a identificar (Proex, Proen, PRPPG e responsáveis pelos
  registros). Impacto: eventual substituição ou confirmação por fonte. Tratamento
  provisório: perguntas declaradas; nenhuma integração presumida.
- **DP-309** — DECISÃO PENDENTE: tratamento de dados potencialmente sensíveis (Q2, Q4, Q5,
  Q6) e da assimetria de "Prefiro não responder" (Q2 tem; Q4, Q5 e Q7 não têm e são
  obrigatórias). Instância competente: encarregado de dados e CPAEG. Impacto: Princípio
  XVI na jornada e na exportação. Tratamento provisório: perguntas e Opções originais.
- **DP-310** — DECISÃO PENDENTE: as preocupações registradas pelas notas internas — se
  a lista de Pós-Graduação (Q19) precisa ser atualizada (a nota pede doutorado, que já
  aparece uma vez — O-5) e se Q41 deve mudar de posição. Instância competente: CPAEG.
  Impacto: Q19, Q41 em Versão futura. Tratamento provisório: notas não migradas (E-05,
  E-06); lista e posição originais.

**Herdadas e ainda abertas** (não resolvidas por esta feature)

- **002/DP-001** — competência institucional para publicar uma Versão.
- **002/DP-002** — processo institucional de elaboração, revisão e aprovação.
- **002/DP-003** — política de correção editorial após publicação.
- **002/DP-004** — melhorias metodológicas do instrumento (inclui O-6 a O-20).
- **002/DP-005** — novas capacidades (exclusividade entre Opções, condição de exibição,
  validação de formato).
- **002/DP-006** — comparabilidade entre Versões e com o formulário histórico.
- **002/DP-007** — forma definitiva do consentimento e base legal.
- **001/DP-001** — fonte acadêmica oficial.
- **001/DP-004** — atributos de Q10–Q19 com qualidade suficiente na fonte real.
- **001/DP-007** — vocabulário canônico de nível, modalidade e forma de oferta.
