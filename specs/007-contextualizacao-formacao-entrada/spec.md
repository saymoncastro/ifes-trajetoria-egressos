# Feature Specification: Contextualização da formação e entrada na pesquisa

**Feature Branch**: `claude/feature-007-contextualizacao-formacao-ca197a`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "Feature 007 — Contextualização da formação e entrada na
pesquisa. A partir de uma Pessoa já resolvida por uma fronteira confiável, obter suas
Conclusões Acadêmicas, determinar quais têm pesquisa disponível agora (pela Feature 004),
distinguir zero, uma ou várias formações aplicáveis, tratar Campanhas sobrepostas sobre a
mesma formação como ambiguidade operacional sem prioridade, e iniciar ou retomar a
Participação correspondente (pela Feature 005), entregando-a à jornada da Feature 006. O
egresso escolhe uma formação, nunca uma Campanha. Sem autenticação, sem reconciliação de
Pessoas, sem alterar a baseline (Q10–Q19), sem pré-preenchimento, sem dashboard e, de
preferência, sem novo modelo persistente."

## Contexto

As seis primeiras features estabeleceram:

- **001** — **Pessoa → Conclusão Acadêmica**, com fonte acadêmica simulada. Curso,
  unidade, nível, modalidade, forma de oferta e ano/data de conclusão pertencem à
  Conclusão, nunca à Pessoa (001 FR-003). A ordem das Conclusões não tem significado
  (001 FR-017).
- **002/003** — **Pesquisa → Versão → instrumento**, com a baseline do Formulário Egresso
  Ifes 2024. Q10–Q19 foram preservadas como perguntas declaradas e marcadas como
  **candidatas a contexto institucional**; a retirada depende de 003/DP-307.
- **004** — **Campanha → população elegível**, com estado temporal e as consultas "esta
  Campanha admite Participação desta Conclusão agora?" e "quais Campanhas EM COLETA
  consideram esta Conclusão elegível?" (004 FR-052, FR-053). Campanhas sobrepostas são
  permitidas e nunca priorizadas (004 FR-051; 004/DP-404).
- **005** — **Conclusão Acadêmica + Campanha → Participação → Respostas**: no máximo uma
  Participação por par; o início devolve a existente sem duplicar (005 FR-006, FR-013).
- **006** — **Jornada e conclusão da Participação**: a jornada recebe uma Participação já
  identificada (006 FR-051); concluída, ela é imutável.

Todas elas recebem Pessoa, Conclusão, Campanha ou Participação **já conhecidas**. Falta o
elo entre "sabemos quem é a Pessoa" e "temos a Participação certa em mãos":

```text
Pessoa já resolvida (fronteira confiável — fora do escopo)
  │
  ├─► quais Conclusões Acadêmicas ela possui?                 (001, leitura)
  ├─► quais delas têm pesquisa disponível agora?             (004, consulta)
  ├─► qual formação está sendo acompanhada?                  (007: resolução ou seleção)
  ├─► já existe Participação para o par?                     (005, consulta)
  └─► iniciar ou retomar a Participação → entregar à jornada (005 → 006)
```

### Princípio central desta spec

> **O egresso escolhe uma formação; a Campanha é consequência.**
>
> A entrada no acompanhamento é resolvida sobre a **Conclusão Acadêmica**, nunca sobre a
> Pessoa e nunca sobre a Campanha. A Campanha aplicável é determinada pelo domínio, a
> partir da Feature 004. Quando o domínio não consegue determiná-la sem inventar
> prioridade, ele **declara a ambiguidade** em vez de escolher.

### Princípios desta spec

1. **Contexto é sempre uma Conclusão Acadêmica.** A Pessoa é ponto de partida, não
   contexto. Toda Participação alcançada pela entrada pertence a exatamente uma
   Conclusão da Pessoa.
2. **Composição, não reimplementação.** Formações vêm da 001; pesquisa disponível, da
   004; Participação, da 005; jornada, da 006. Esta feature apenas as compõe.
3. **Sem escolha inventada.** Nenhuma formação e nenhuma Campanha é escolhida por
   recência, unidade, nível, ordem, data ou qualquer ranking.
4. **Sem escolha artificial.** Quando há exatamente uma formação com entrada pendente, a
   entrada é resolvida sem pedir seleção ao egresso.
5. **Minimizar escolhas sem esconder informação.** Uma formação já concluída na Campanha
   aplicável é informação histórica, não alternativa de ação: aparece na consulta com seu
   estado, mas não conta entre as formações a escolher.
6. **Consultar não grava.** Descobrir a situação de entrada nunca cria Participação nem
   qualquer registro. A Participação só nasce na entrada explícita, pela 005.
7. **Contexto institucional identifica; não responde.** Curso, unidade, ano, nível e
   modalidade servem para apresentar, verificar e contextualizar a formação. Nunca viram
   Resposta.
8. **Nada novo persistido.** Tudo nesta feature é derivado dos modelos existentes.

### Termos usados nesta spec

Os termos abaixo são **conceitos derivados** para descrever comportamento. Nenhum deles é
entidade, tabela ou registro persistido.

- **Pessoa resolvida**: Pessoa do NIAE (001) entregue por uma fronteira confiável. Como
  ela foi identificada está fora do escopo (FR-001).
- **Formação**: termo de apresentação para uma **Conclusão Acadêmica** da Pessoa. Não é
  conceito novo: "escolher uma formação" é escolher uma Conclusão Acadêmica.
- **Campanha aplicável** a uma Conclusão: Campanha EM COLETA no momento de referência na
  qual a Conclusão é ELEGÍVEL, exatamente como devolvido pela 004 (004 FR-052).
- **Situação da formação**: para cada Conclusão da Pessoa, exatamente uma de cinco
  (FR-014):
  - **sem pesquisa** — nenhuma Campanha aplicável;
  - **disponível para iniciar** — exatamente uma Campanha aplicável e nenhuma
    Participação do par;
  - **disponível para retomar** — exatamente uma Campanha aplicável e Participação do par
    em rascunho;
  - **já concluída** — exatamente uma Campanha aplicável e Participação do par concluída;
  - **ambiguidade operacional** — duas ou mais Campanhas aplicáveis.
- **Formação com pesquisa aplicável**: Conclusão com ao menos uma Campanha aplicável
  (disponível para iniciar, disponível para retomar, já concluída ou ambiguidade
  operacional).
- **Formação com entrada pendente**: Conclusão "disponível para iniciar" ou "disponível
  para retomar". É a única alternativa de ação: só ela conta para decidir entre
  resolução automática e seleção. Formação "já concluída" ou com "ambiguidade
  operacional" tem pesquisa aplicável, mas **não** tem entrada pendente.
- **Situação de entrada**: classificação global, para a Pessoa e o momento de referência,
  derivada das situações de todas as suas formações (FR-017).
- **Entrada**: ato explícito de iniciar ou retomar a Participação de uma formação com
  entrada pendente (FR-029).
- **Momento de referência**: o instante da consulta ou da entrada, na timezone
  configurada do projeto, como na 004, na 005 e na 006.

### Decisões desta especificação

Escolhas desta spec que resolvem o que as features anteriores deixaram para a feature de
entrada. Nenhuma é regra institucional; todas são reversíveis por feature futura.

- **Pesquisa aplicável ≠ entrada pendente.** Quais Campanhas são aplicáveis a uma
  formação vem só da 004 (EM COLETA ∧ ELEGÍVEL). Se a formação tem **entrada pendente**
  depende, além disso, da Participação do par: inexistente ou em rascunho → pendente;
  concluída → não pendente. A decisão entre resolução automática e seleção conta
  **somente** formações com entrada pendente. Formações já concluídas continuam na
  consulta, com seu estado, mas não aumentam o número de alternativas. Confirmado em
  Clarifications. (FR-014, FR-019 a FR-022)
- **Ambiguidade operacional é local à formação.** Uma formação com duas ou mais Campanhas
  aplicáveis fica marcada como ambígua, com as Campanhas envolvidas. Ela não é entrada
  pendente (não há Participação determinável para iniciar ou retomar) e, por isso, não
  impede a resolução automática de **outra** formação com entrada pendente; também não
  é escondida. O estado da Participação nunca é usado para resolver a ambiguidade.
  Confirmado em Clarifications. (FR-025 a FR-028)
- **Consulta e entrada são separadas.** A consulta da situação de entrada nunca grava. A
  entrada é o único ponto em que uma Participação pode nascer, e só pela operação de
  início da 005. (FR-024, FR-029)
- **A entrada pode ser solicitada sem formação informada.** Nesse caso, ela só procede
  quando há exatamente uma formação com entrada pendente; caso contrário, devolve a
  situação sem criar nada. É assim que o caso de uma única alternativa dispensa seleção
  artificial sem que o domínio escolha entre opções. (FR-030)
- **A entrada reavalia tudo no seu próprio momento de referência.** Ela não confia em
  resultado de consulta anterior: entre consultar e entrar, uma Campanha pode encerrar ou
  outra pode abrir. (FR-032)
- **Pessoa não registrada no NIAE é erro de uso da fronteira, não situação de domínio.**
  A fronteira confiável entrega uma Pessoa do NIAE; se não entrega, a falha é dela.
  "Pessoa sem formação" é coisa diferente: Pessoa registrada sem Conclusões. (FR-003,
  FR-018)

## Clarifications

### Session 2026-10-01

O solicitante revisou a hipótese sobre Participações concluídas antes do `/speckit-plan`.
A decisão abaixo substitui a hipótese anterior ("formação concluída conta para seleção")
e deixa de ser hipótese.

- **Q: Uma formação cuja Participação na Campanha aplicável já está concluída conta para
  decidir se o egresso precisa escolher uma formação?** → **Não.** Distinguem-se
  *formação com pesquisa aplicável* e *formação com entrada pendente*. Com exatamente uma
  Campanha aplicável: sem Participação → entrada pendente (iniciar); Participação em
  rascunho → entrada pendente (retomar); Participação concluída → pesquisa já concluída,
  **sem** entrada pendente. A formação concluída continua na consulta com seu estado (não
  se elimina informação), mas não entra no conjunto de alternativas. Exatamente uma
  entrada pendente → resolução automática, mesmo que a Pessoa tenha outras formações já
  concluídas (por exemplo, A concluída e B em rascunho → retomar B diretamente). Duas ou
  mais → seleção explícita, sem ranking. Nenhuma entrada pendente, havendo pesquisa
  aplicável → "nenhuma pesquisa pendente para entrada", sem seleção, preservando quais
  formações estão concluídas. (FR-014, FR-019 a FR-023, FR-030)
- **Q: A ambiguidade de uma formação bloqueia as demais? Existe ambiguidade global?** →
  **Não e não** (confirmado após o plan). A ambiguidade pertence à Conclusão afetada: a
  formação continua explicitamente ambígua no resultado, nenhuma Campanha dela é escolhida
  e nenhuma Participação dela é criada ou retomada, mas outra formação que seja a única
  com entrada pendente é resolvida automaticamente. Não há situação global de
  ambiguidade. As situações globais são exatamente: sem formação disponível (zero
  formações); sem pesquisa disponível (formações, nenhuma Campanha aplicável); entrada
  resolvida (uma pendente); seleção necessária (duas ou mais pendentes); sem entrada
  pendente (pesquisa aplicável e zero pendentes — concluídas, ambíguas, ou mistura,
  com ou sem formações sem pesquisa). (FR-020 a FR-023, FR-027a)
- **Q: O estado da Participação pode resolver Campanhas sobrepostas?** → **Não.** Mais de
  uma Campanha aplicável à mesma Conclusão continua sendo ambiguidade operacional, local à
  formação afetada; não se escolhe a Campanha com Participação, nem a ainda não
  respondida, nem a mais recente. 004/DP-404 preservada. (FR-025 a FR-028)

## User Scenarios & Testing *(mandatory)*

<!--
  Os "usuários" desta feature são o próprio domínio, a futura fronteira de identidade e a
  futura interface pública de entrada (ambas fora do escopo), que consumirão estas
  capacidades, e quem desenvolve e testa. Nenhuma interface, autenticação ou competência
  institucional é criada.

  Os testes usam a fonte simulada (001) e Campanhas com Versões PUBLICADAS apenas no
  ambiente de teste, como na 005 e na 006. Isso não é publicação institucional.
-->

### User Story 1 - Listar as formações de uma Pessoa (Priority: P1)

Dada uma Pessoa resolvida, o domínio obtém todas as suas Conclusões Acadêmicas, cada uma
com identidade própria e com o contexto institucional disponível (curso, unidade, nível,
modalidade, forma de oferta, ano ou data de conclusão), preservando "não informado pela
fonte".

**Why this priority**: sem a lista de formações não há o que contextualizar nem escolher.
É também a garantia de que contexto acadêmico vem da Conclusão, não da Pessoa.

**Independent Test**: para as Pessoas dos cenários A a E da fonte simulada, consultar a
situação de entrada sem nenhuma Campanha existente e verificar que todas as Conclusões
aparecem, distintas, com seus atributos e nenhum valor inventado.

**Acceptance Scenarios**:

1. **Given** a Pessoa SIM-P-0004 (três Conclusões em Vila Velha: técnico, licenciatura,
   mestrado), **When** a situação de entrada é consultada, **Then** as três formações
   aparecem, cada uma com sua identidade e seu contexto.
2. **Given** uma Conclusão com forma de oferta não informada pela fonte, **When** ela é
   listada, **Then** o atributo aparece como "não informado", sem valor padrão nem
   dedução.
3. **Given** a Pessoa SIM-P-0003 (ADS na Serra e especialização no Cefor), **When** as
   formações são listadas, **Then** cada uma traz sua própria unidade; a Pessoa não
   recebe unidade, curso ou nível.
4. **Given** a mesma consulta repetida, **When** os resultados são comparados, **Then** a
   ordem das formações é a mesma e não indica formação "principal", "atual" ou "mais
   relevante".
5. **Given** a consulta, **When** ela termina, **Then** nenhuma Pessoa, Conclusão,
   Campanha, Participação ou Resposta foi criada ou alterada.

---

### User Story 2 - Determinar a situação de cada formação (Priority: P1)

Para cada formação, o domínio determina, pela 004, as Campanhas aplicáveis no momento de
referência e, pela 005/006, a Participação do par quando há exatamente uma Campanha
aplicável. A formação é classificada como "sem pesquisa", "disponível para iniciar",
"disponível para retomar", "já concluída" ou "ambiguidade operacional".

**Why this priority**: é o que transforma uma lista de formações em possibilidade de
acompanhamento e distingue pesquisa aplicável de entrada pendente. Sem isso não há
entrada.

**Independent Test**: com a Pessoa SIM-P-0004 e uma Campanha EM COLETA restrita ao nível
"Pós-graduação", verificar que apenas o mestrado tem pesquisa aplicável; criar, depois
concluir, a Participação do mestrado e verificar a passagem de "disponível para iniciar"
a "disponível para retomar" e a "já concluída"; repetir com a Campanha em preparação e
encerrada e verificar que nenhuma formação tem pesquisa.

**Acceptance Scenarios**:

1. **Given** uma Campanha EM COLETA cujos critérios só o mestrado de SIM-P-0004 atende e
   nenhuma Participação, **When** a situação de entrada é consultada, **Then** o mestrado
   está "disponível para iniciar" e as outras duas, "sem pesquisa".
2. **Given** a Participação do mestrado em rascunho, **When** a situação é consultada,
   **Then** o mestrado está "disponível para retomar"; concluída a Participação, está
   "já concluída".
3. **Given** a mesma Campanha EM PREPARAÇÃO ou ENCERRADA, **When** a situação é
   consultada, **Then** todas as formações estão "sem pesquisa".
4. **Given** uma Campanha cujo período termina em 30/06/2027, **When** a situação é
   consultada em 30/06/2027 e em 01/07/2027, **Then** a formação elegível tem pesquisa
   aplicável na primeira data e está "sem pesquisa" na segunda.
5. **Given** uma formação cuja elegibilidade depende de atributo "não informado" usado no
   critério da Campanha, **When** a situação é consultada, **Then** a formação está "sem
   pesquisa", conforme a avaliação da 004, sem regra nova.
6. **Given** a classificação, **When** se verifica como foi obtida, **Then** estado,
   período e elegibilidade vieram exclusivamente das consultas da 004, a situação da
   Participação veio da 005/006, e nada foi gravado.

---

### User Story 3 - Resolver automaticamente a única entrada pendente (Priority: P1)

Quando a Pessoa tem exatamente uma formação com entrada pendente, a situação de entrada é
"entrada resolvida" e a entrada pode prosseguir sem que nenhuma formação seja informada.
Isso vale mesmo que a Pessoa tenha outras formações já concluídas, sem pesquisa ou com
ambiguidade operacional: elas continuam informadas, mas não são alternativas de ação.

**Why this priority**: é o caso mais comum (cenário A) e o que mais reduz fricção
(Princípio XIV). Pedir seleção com uma única alternativa seria escolha artificial.

**Independent Test**: com a Pessoa SIM-P-0001 (uma Conclusão) e uma Campanha EM COLETA de
população ampla, consultar a situação e entrar sem informar formação; verificar que a
Participação do par certo foi criada. Com SIM-P-0003, concluir a Participação de uma
formação e verificar que a outra é resolvida sem seleção.

**Acceptance Scenarios**:

1. **Given** SIM-P-0001 com uma Conclusão "disponível para iniciar", **When** a situação
   é consultada, **Then** ela é "entrada resolvida", identificando a Conclusão e a
   Campanha aplicável.
2. **Given** a mesma situação, **When** a entrada é solicitada sem formação informada,
   **Then** a Participação do par (Campanha aplicável, Conclusão) é iniciada.
3. **Given** a Pessoa SIM-P-0004 (três Conclusões) com apenas uma com pesquisa aplicável
   (cenário B), **When** a situação é consultada, **Then** ela é "entrada resolvida" para
   essa formação; as outras duas aparecem "sem pesquisa".
4. **Given** SIM-P-0003 com a formação A "já concluída" e a formação B "disponível para
   retomar", na mesma Campanha, **When** a situação é consultada, **Then** ela é "entrada
   resolvida" para B, e A continua listada como "já concluída"; a entrada sem formação
   informada devolve a Participação em rascunho de B.
5. **Given** SIM-P-0003 com A "já concluída" e B "disponível para iniciar", **When** a
   entrada é solicitada sem formação informada, **Then** a Participação de B é iniciada
   sem seleção.
6. **Given** a situação "entrada resolvida", **When** a entrada é solicitada informando
   essa mesma formação, **Then** o resultado é idêntico ao da entrada sem formação
   informada.

---

### User Story 4 - Exigir seleção quando houver múltiplas entradas pendentes (Priority: P1)

Quando duas ou mais formações da Pessoa têm entrada pendente, a situação de entrada é
"seleção necessária". O domínio não escolhe nenhuma: a entrada só prossegue com uma
formação informada explicitamente.

**Why this priority**: escolher automaticamente fundiria ou ocultaria formações
(Princípios I e XI) e inventaria regra institucional (XXIX; 005/DP-501).

**Independent Test**: com a Pessoa SIM-P-0003 e uma Campanha de população ampla, consultar
a situação e verificar "seleção necessária" com as duas formações; solicitar entrada sem
formação e verificar que nada é criado; entrar informando cada uma e verificar duas
Participações independentes.

**Acceptance Scenarios**:

1. **Given** SIM-P-0003 com as duas formações "disponível para iniciar" na mesma Campanha
   (cenário C), **When** a situação é consultada, **Then** ela é "seleção necessária",
   indicando as duas formações com entrada pendente, cada uma com seu contexto.
2. **Given** uma formação "disponível para retomar" e outra "disponível para iniciar",
   **When** a situação é consultada, **Then** ela é "seleção necessária": rascunho não tem
   prioridade sobre formação ainda não iniciada, nem o contrário.
3. **Given** a situação "seleção necessária", **When** a entrada é solicitada sem
   formação informada, **Then** nada é criado e o resultado é "seleção necessária".
4. **Given** a mesma situação, **When** se verifica a ordem das formações, **Then** ela é
   determinística e não representa preferência; nenhuma é marcada como "mais recente",
   "principal" ou "sugerida".
5. **Given** duas formações com entrada pendente, cada uma em uma Campanha diferente,
   **When** a situação é consultada, **Then** ela continua "seleção necessária": o que se
   escolhe é a formação, não a Campanha.
6. **Given** a seleção da formação A e a entrada, **When** depois a formação B é
   selecionada, **Then** cada uma tem sua própria Participação; nada é compartilhado
   (005 FR-009).
7. **Given** duas formações com entrada pendente e uma terceira "já concluída", **When** a
   situação é consultada, **Then** ela é "seleção necessária" entre as duas pendentes; a
   concluída é informada, mas não aumenta o número de alternativas.

---

### User Story 5 - Iniciar Participação para a formação selecionada (Priority: P1)

Depois de resolvida (diretamente ou por seleção) uma formação "disponível para iniciar",
a entrada inicia a Participação pela operação de início da
005 e a devolve, pronta para a jornada da 006.

**Why this priority**: é o objetivo da feature: entregar a Participação certa.

**Independent Test**: entrar numa formação "disponível para iniciar";
verificar Participação nova para o par (Campanha aplicável, Conclusão selecionada), sem
Respostas, e a jornada da 006 consultável sobre ela.

**Acceptance Scenarios**:

1. **Given** uma formação "disponível para iniciar", **When** a entrada
   é solicitada, **Then** a Participação do par é criada pela 005, com o momento de
   início da 005, e o resultado indica "iniciada".
2. **Given** a Participação recém-criada, **When** suas Respostas são consultadas,
   **Then** não há nenhuma: curso, unidade, ano, nível e modalidade da Conclusão não foram
   gravados como Resposta (Q10–Q19 continuam sem resposta).
3. **Given** a Participação recém-criada, **When** a jornada da 006 é consultada, **Then**
   ela começa pela primeira Seção da Versão aplicada, sem Seção pulada ou pré-preenchida.
4. **Given** duas entradas simultâneas para a mesma formação, **When** ambas terminam,
   **Then** existe exatamente uma Participação para o par (005 FR-006).

---

### User Story 6 - Retomar Participação existente (Priority: P1)

Se a formação resolvida está "disponível para retomar" (Participação em rascunho na
Campanha aplicável), a entrada devolve essa mesma Participação, sem criar outra, para que a jornada da 006 seja
retomada.

**Why this priority**: o egresso interrompe e volta; duplicar a Participação quebraria a
unicidade do par e a longitudinalidade.

**Independent Test**: iniciar, responder algumas Perguntas, entrar de novo pela mesma
formação; verificar a mesma Participação, com as mesmas Respostas, e nenhuma nova.

**Acceptance Scenarios**:

1. **Given** uma Participação em rascunho para o par, **When** a entrada é repetida,
   **Then** a mesma Participação é devolvida, com o resultado "em rascunho", e nada é
   criado ou alterado.
2. **Given** a entrada repetida N vezes, **When** as Participações do par são contadas,
   **Then** existe exatamente uma.
3. **Given** a Participação retomada, **When** a jornada da 006 é consultada, **Then** a
   Seção atual e as Respostas são as já existentes; a 007 não executa nem altera a
   jornada.
4. **Given** a situação de entrada, **When** a formação tem Participação em rascunho,
   **Then** a consulta a informa como "disponível para retomar", sem gravar nada.

---

### User Story 7 - Informar que a Participação já foi concluída (Priority: P2)

Uma formação cuja Participação na Campanha aplicável já está concluída aparece na consulta
como "já concluída": é informação histórica, não alternativa de ação. Ela não conta para
decidir entre resolução automática e seleção. Se a entrada for solicitada informando essa
formação, devolve a Participação com a indicação explícita de que está concluída. Nada é
criado nem reaberto.

**Why this priority**: evita duplicação, reabertura e seleção artificial; depende de US5
e US6.

**Independent Test**: concluir a Participação de uma formação (006); consultar a situação
e verificar "já concluída" e nenhuma entrada pendente; entrar informando a formação e
verificar o resultado "concluída", a mesma Participação, o mesmo momento de conclusão e
nenhuma Participação nova.

**Acceptance Scenarios**:

1. **Given** SIM-P-0001 com a única formação "já concluída" e a Campanha ainda EM COLETA,
   **When** a situação é consultada, **Then** ela é "sem entrada pendente", e a formação
   aparece como "já concluída", com sua Participação.
2. **Given** a mesma situação, **When** a entrada é solicitada sem formação informada,
   **Then** nada é criado e o resultado é "sem entrada pendente"; nenhuma seleção é
   exigida.
3. **Given** a mesma situação, **When** a entrada é solicitada informando a formação,
   **Then** o resultado é "concluída", com a mesma Participação e o mesmo momento de
   conclusão, e nada é criado.
4. **Given** a mesma situação, **When** se procura operação de reabertura, edição ou nova
   tentativa pela entrada, **Then** ela não existe (006 FR-039; 006/DP-603).
5. **Given** SIM-P-0003 com as duas formações "já concluídas" na mesma Campanha, **When**
   a situação é consultada, **Then** ela é "sem entrada pendente", com as duas formações
   informadas como concluídas e nenhuma seleção exigida.
6. **Given** SIM-P-0003 com a formação A "já concluída" e a formação B com entrada
   pendente, **When** a situação é consultada, **Then** ela é "entrada resolvida" para B
   (US3.4, US3.5), e A continua informada como concluída.

---

### User Story 8 - Tratar Pessoa sem Conclusão Acadêmica disponível (Priority: P2)

Uma Pessoa resolvida sem nenhuma Conclusão Acadêmica no NIAE recebe a situação "sem
formação disponível", distinta de Pessoa não registrada, de "sem pesquisa disponível" e de
Conclusão inelegível. Nenhuma formação é inventada.

**Why this priority**: resultado normal e explícito; não ocorre no fluxo atual de
incorporação (001 FR-039), mas a cardinalidade conceitual é 0..N (001 FR-002).

**Independent Test**: com uma Pessoa registrada sem Conclusões (construída no teste),
consultar a situação e solicitar a entrada; verificar "sem formação disponível" e nada
criado; solicitar com Pessoa não registrada e verificar erro de uso, não situação de
domínio.

**Acceptance Scenarios**:

1. **Given** uma Pessoa registrada sem Conclusões, **When** a situação é consultada,
   **Then** ela é "sem formação disponível", sem formação manual, provisória ou padrão.
2. **Given** a mesma Pessoa, **When** a entrada é solicitada, **Then** nada é criado e o
   resultado é "sem formação disponível".
3. **Given** uma Pessoa não registrada no NIAE, **When** a consulta ou a entrada é
   solicitada, **Then** a solicitação é recusada como erro de uso da fronteira, e não
   como "sem formação" nem "sem pesquisa".
4. **Given** "sem formação disponível", **When** o resultado é comunicado, **Then** ele
   não indica erro de identidade nem de dados acadêmicos.

---

### User Story 9 - Tratar Pessoa com formações, mas nenhuma pesquisa disponível (Priority: P2)

Uma Pessoa com Conclusões, nenhuma delas com Campanha aplicável no momento, recebe a
situação "nenhuma pesquisa disponível para suas formações neste momento". É resultado
normal.

**Why this priority**: será a situação mais frequente fora das janelas de coleta; deve ser
distinguível de erro.

**Independent Test**: com a Pessoa SIM-P-0002 e nenhuma Campanha EM COLETA (ou só
Campanhas que não a elegem), consultar e entrar; verificar a situação e nada criado.

**Acceptance Scenarios**:

1. **Given** SIM-P-0002 com duas Conclusões e nenhuma Campanha EM COLETA (cenário E),
   **When** a situação é consultada, **Then** ela é "sem pesquisa disponível", listando as
   duas formações, cada uma "sem pesquisa".
2. **Given** Campanhas EM COLETA em que nenhuma das formações é elegível, **When** a
   situação é consultada, **Then** o resultado é o mesmo, sem expor critérios ou
   pendências de elegibilidade.
3. **Given** uma formação com Participação em rascunho numa Campanha já ENCERRADA, **When**
   a situação é consultada, **Then** a formação está "sem pesquisa"; a
   Participação antiga continua existindo e consultável pela 005/006, mas não é oferecida
   para escrita.
4. **Given** a situação "sem pesquisa disponível", **When** a entrada é solicitada,
   **Then** nada é criado.

---

### User Story 10 - Tratar múltiplas Campanhas aplicáveis à mesma formação como ambiguidade (Priority: P2)

Se uma formação tem duas ou mais Campanhas aplicáveis ao mesmo tempo, o domínio não
escolhe: marca **essa formação** com ambiguidade operacional, identificando as Campanhas
envolvidas para a governança, e não inicia nem retoma Participação por ela. A ambiguidade
é local: não é resolvida pelo estado da Participação, não é escondida e não impede a
resolução de outra formação com entrada pendente.

**Why this priority**: é a decisão pendente explícita da 004 (DP-404). Escolher a mais
recente, a primeira, a já respondida, a ainda não respondida ou por prioridade seria regra
inventada.

**Independent Test**: abrir duas Campanhas de população ampla com períodos sobrepostos;
consultar a situação de SIM-P-0001 e entrar; verificar a formação marcada como ambígua, as
duas Campanhas identificadas e nada criado.

**Acceptance Scenarios**:

1. **Given** SIM-P-0001 e duas Campanhas aplicáveis à sua Conclusão (cenário F), **When**
   a situação é consultada, **Then** a formação está em "ambiguidade operacional",
   identificando as duas Campanhas sem indicar nenhuma como preferida, e a situação de
   entrada é "sem entrada pendente".
2. **Given** a mesma situação, **When** a entrada é solicitada (com ou sem formação
   informada), **Then** nada é criado nem retomado; com a formação informada, o resultado
   é "ambiguidade operacional".
3. **Given** a mesma situação e uma Participação já existente — em rascunho ou concluída
   — para a formação numa das duas Campanhas, **When** a situação é consultada ou a
   entrada é solicitada, **Then** a formação continua em "ambiguidade operacional": a
   existência, a ausência ou o estado de Participação não desempata.
4. **Given** SIM-P-0003 com a formação A ambígua e a formação B "disponível para
   iniciar", **When** a situação é consultada, **Then** ela é "entrada resolvida" para B,
   e A continua listada em "ambiguidade operacional" com suas Campanhas; informar A na
   entrada resulta em "ambiguidade operacional", sem criar nada.
5. **Given** uma Pessoa com a formação A ambígua e as formações B e C com entrada
   pendente, **When** a situação é consultada, **Then** ela é "seleção necessária" entre B
   e C; A é informada como ambígua.
6. **Given** a ambiguidade, **When** se procura o que o egresso deveria escolher, **Then**
   nenhuma escolha de Campanha é pedida a ele.

---

### User Story 11 - Preservar proveniência e rejeitar associações inconsistentes (Priority: P3)

A entrada só aceita formação que pertença à Pessoa resolvida. A Participação alcançada
sempre aponta para a Conclusão selecionada e para a Campanha aplicável a ela. Nenhum dado
institucional é copiado ou transformado em Resposta.

**Why this priority**: proteção defensiva; a futura interface receberá identificadores
vindos de fora e não pode permitir entrar na formação de outra Pessoa.

**Independent Test**: solicitar a entrada da Pessoa X informando uma Conclusão da Pessoa
Y; verificar rejeição sem dados de Y e nada criado.

**Acceptance Scenarios**:

1. **Given** a Pessoa SIM-P-0010 e uma Conclusão de SIM-P-0011 (homônimas), **When** a
   entrada é solicitada, **Then** é rejeitada como formação que não pertence à Pessoa,
   sem revelar atributos da Conclusão alheia, e nada é criado.
2. **Given** a entrada aceita, **When** a Participação é inspecionada, **Then** sua
   Conclusão é a selecionada, sua Campanha é a aplicável, e a Pessoa é obtida pela
   Conclusão (005 FR-004).
3. **Given** qualquer entrada, **When** ela termina, **Then** nenhuma Resposta foi criada,
   e nenhum atributo foi copiado da Conclusão para a Participação, a Pessoa ou a
   Campanha.
4. **Given** duas Pessoas homônimas, **When** cada uma consulta sua situação, **Then** cada
   uma vê apenas as próprias formações; o nome não participa de nada.

---

### Cobertura dos critérios de sucesso do solicitante

| # | Pergunta | Resposta da spec |
|---|----------|------------------|
| 1 | Dada uma Pessoa, sabemos quais formações ela concluiu? | Sim, pelas Conclusões da 001 (US1; FR-006 a FR-011) |
| 2 | Sabemos quais têm pesquisa disponível agora? | Sim, pela 004, no momento de referência, distinguindo pesquisa aplicável de entrada pendente (US2; FR-012 a FR-016) |
| 3 | Uma única formação aplicável segue sem escolha artificial? | Sim: com uma única entrada pendente, "entrada resolvida" e entrada sem formação informada, mesmo com outras formações já concluídas (US3; FR-020, FR-030) |
| 4 | Múltiplas formações continuam distintas? | Sim, cada uma com identidade e Participação próprias, todas devolvidas pela consulta (US4; FR-008, FR-017, FR-021, FR-039) |
| 5 | O egresso escolhe uma formação, não uma Campanha? | Sim (US4, US10; FR-021, FR-028) |
| 6 | Campanhas sobrepostas não recebem prioridade inventada? | Sim, ambiguidade operacional (US10; FR-025 a FR-028) |
| 7 | A Participação existente é retomada sem duplicação? | Sim, pela 005 (US6; FR-033, FR-034) |
| 8 | Nova Campanha futura gera nova Participação para a mesma formação? | Sim (FR-038, FR-039; caso J) |
| 9 | Nenhum dado institucional virou resposta declarada? | Sim (US11; FR-040 a FR-043) |
| 10 | Nenhum mecanismo de autenticação foi criado? | Sim (FR-001, FR-002, FR-049) |
| 11 | Nenhum modelo novo foi criado sem necessidade? | Nenhum modelo novo (FR-047; Análise de persistência) |
| 12 | Nada do GeN/dashboard foi reconstruído? | Nada (FR-051) |

### Casos de referência

| Caso | Situação das formações | Situação de entrada esperada | Entrada sem formação informada |
|------|------------------------|------------------------------|--------------------------------|
| A | 1 Conclusão, disponível para iniciar | entrada resolvida | "iniciada" (nova, pela 005) |
| B | 3 Conclusões, só 1 com pesquisa aplicável | entrada resolvida; outras "sem pesquisa" | idem A |
| C | 2 Conclusões com entrada pendente | seleção necessária | nada criado; só com formação informada |
| D | Pessoa sem Conclusões | sem formação disponível | nada criado |
| E | Conclusões, nenhuma Campanha aplicável | sem pesquisa disponível | nada criado |
| F | 1 Conclusão com 2 Campanhas aplicáveis | sem entrada pendente; formação em ambiguidade operacional | nada criado nem retomado |
| G | 1 formação disponível para iniciar | entrada resolvida | "iniciada" |
| H | 1 formação disponível para retomar | entrada resolvida | "em rascunho" (mesma Participação) |
| I | 1 formação já concluída | sem entrada pendente; formação "já concluída" | nada criado; informando a formação: "concluída" |
| J | mesma Conclusão: 2025 concluída (ENCERRADA), 2030 EM COLETA | entrada resolvida pela Campanha 2030 (disponível para iniciar) | nova Participação para 2030; a de 2025 intacta |
| K | atributos incompletos | formações distintas pela identidade; "não informado" preservado | igual aos demais casos |
| L | Conclusões em unidades diferentes | cada formação com sua unidade | Participação com o contexto da Conclusão escolhida |
| M | A já concluída, B disponível para retomar | entrada resolvida para B; A informada | "em rascunho" (Participação de B) |
| N | A já concluída, B disponível para iniciar | entrada resolvida para B; A informada | "iniciada" (Participação de B) |
| O | A ambígua, B com entrada pendente | entrada resolvida para B; A informada como ambígua | Participação de B |

### Edge Cases

- **Pessoa não registrada no NIAE**: erro de uso da fronteira, não situação de domínio
  (FR-003). Diferente de "sem formação disponível" (FR-018).
- **Pessoa que a fonte localiza sem conclusão elegível** (001, "sem conclusão
  elegível"): não é materializada no NIAE (001 FR-039); portanto não chega à 007 como
  Pessoa resolvida. A forma de comunicar isso ao egresso pertence à fronteira de
  identidade (004/DP-406).
- **Pessoa registrada sem Conclusões**: não ocorre pela incorporação atual (001 FR-039),
  mas é representada como "sem formação disponível" (FR-018).
- **Formação inelegível em todas as Campanhas EM COLETA**: "sem pesquisa" para essa
  formação; motivos e critérios não são expostos (FR-015).
- **Atributo não informado usado como critério**: a 004 avalia NÃO ELEGÍVEL (NAO_INFORMADO);
  a formação fica "sem pesquisa" (004/DP-409).
- **Duas formações com atributos idênticos** (por exemplo, mesmo curso, unidade e ano):
  continuam duas formações, distintas pela identidade; não são fundidas nem
  deduplicadas (001 FR-014). Como apresentá-las de forma distinguível ao egresso é DP-702.
- **Formação sem nenhum atributo descritivo informado**: continua formação válida e
  selecionável; o domínio não fabrica rótulo (FR-010; DP-702).
- **Formação A já concluída e B com entrada pendente**: "entrada resolvida" para B; A
  informada como concluída (Clarifications; US3.4, US3.5).
- **Todas as formações com pesquisa aplicável já concluídas**: "sem entrada pendente",
  com cada formação informada como "já concluída"; nenhuma seleção é exigida e nada é
  criado. Informar uma delas na entrada devolve "concluída" (US7).
- **Formação ambígua e uma única outra com entrada pendente**: "entrada resolvida" para a
  outra; a ambígua continua informada (US10.4). Com duas ou mais outras pendentes,
  "seleção necessária" entre elas (US10.5).
- **Nenhuma formação com entrada pendente, mas alguma com pesquisa aplicável** (todas
  concluídas; só ambíguas; concluídas e ambíguas; qualquer delas com outras "sem
  pesquisa"): "sem entrada pendente", sem situação global específica para cada
  combinação; cada formação informada com sua situação (US7, US10.1; FR-022).
- **Ambiguidade com Participação já existente numa das Campanhas** (por exemplo, a
  segunda Campanha abriu depois do início): continua ambiguidade, qualquer que seja o
  estado dessa Participação; ela é preservada, mas não é retomada por esta feature
  enquanto a ambiguidade persistir (FR-027; 004/DP-404).
- **Formação concluída entre a consulta e a entrada** (por exemplo, em outro dispositivo):
  a entrada reavalia e devolve "concluída", sem criar nem reabrir (FR-032).
- **Participação em rascunho de Campanha encerrada**: não é oferecida pela entrada
  (formação "sem pesquisa" para essa Campanha); continua consultável pela 005/006
  (006 FR-042).
- **Campanha encerra entre a consulta e a entrada**: a entrada reavalia no seu momento e
  devolve a situação atual (por exemplo, "sem pesquisa"), sem criar nada (FR-032).
- **Nova Campanha abre entre a consulta e a entrada, criando sobreposição**: a formação
  passa a "ambiguidade operacional" e a entrada por ela não cria nada (FR-032).
- **Elegibilidade que muda durante a coleta**: na configuração atual não ocorre, porque
  Campanha aberta é imutável (004 FR-043) e a incorporação não altera Conclusões (001).
  Se correção acadêmica futura a provocar, o efeito sobre Participação existente é
  005/DP-507; esta feature segue a 004 sem regra própria.
- **Entradas simultâneas para a mesma formação**: exatamente uma Participação (005 FR-006).
- **Formação de outra Pessoa informada**: rejeitada sem dados da Conclusão alheia
  (FR-044, FR-045).
- **Conclusão informada que não existe no NIAE**: mesma rejeição da formação de outra
  Pessoa, indistinguível dela, para não revelar se um identificador é Conclusão de
  alguém (FR-044, FR-045; ajuste do code review).
- **Pessoa com várias formações pendentes em Campanhas diferentes ao mesmo tempo**:
  "seleção necessária"; a seleção é da formação, e cada formação leva à sua Campanha
  (US4.5).
- **Homônimos**: o nome não participa de nada (001 FR-005).

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII): **[Herdado]** comportamento do instrumento vigente
(inventário); **[PAEG]** com artigo; **[Const. — n]** decorre diretamente da
Constituição; **[00n FR-x]** decorre de contrato de feature anterior; **[Arquitetura]**
decisão de modelagem; **[Hipótese]** escolha reversível de produto; **[Escopo]**
delimitação desta feature.

### Functional Requirements

**Entrada e fronteira de identidade**

- **FR-001**: As capacidades desta feature DEVEM receber uma **Pessoa do NIAE já
  resolvida** e um momento de referência. A forma como a Pessoa foi identificada
  (Portal do Egresso, identidade institucional, Gov.br, OTP ou outro) está fora do
  escopo e NÃO DEVE ser presumida. [Const. — XV; 004/DP-406]
- **FR-002**: Esta feature NÃO DEVE criar busca de Pessoa nem entrada por CPF, e-mail,
  matrícula, nome ou qualquer outro identificador. NÃO DEVE criar usuário, conta,
  credencial, login, senha, OTP, link mágico, sessão autenticada, vínculo Pessoa ↔ e-mail
  ou CPF normalizado. [Const. — XV, XVI, XXII; Escopo]
    *(Revisado pela 018)* A entrada por CPF e nascimento pertence à capacidade separada da 018,
  que entrega a Pessoa resolvida à jornada (018 FR-044, FR-050).

- **FR-003**: Pessoa não registrada no NIAE, ou argumento de natureza errada, DEVE ser
  recusada como **erro de uso**, antes de qualquer gravação, e NÃO DEVE ser confundida
  com situação de domínio ("sem formação", "sem pesquisa"). Conclusão informada que não
  é da Pessoa — inclusive inexistente — segue FR-044.
  [Arquitetura; padrão de erro de uso da 005]
- **FR-004**: Esta feature NÃO DEVE reconciliar, fundir, deduplicar ou comparar Pessoas,
  nem tratar fontes divergentes, CPF ou nome divergente, nem matching probabilístico.
  NÃO DEVE existir componente genérico de resolução de Pessoa ou de identidade.
  [Const. — XXII; 001/DP-003]
- **FR-005**: Identificadores já existentes na 001 (referências de origem) PODEM ser
  lidos conforme o contrato da 001, mas NÃO DEVEM ser ampliados, usados como mecanismo
  de acesso nem expostos ao egresso por esta feature. [001 FR-006; Const. — XVI]

**Formações da Pessoa**

- **FR-006**: DEVE ser possível obter todas as Conclusões Acadêmicas da Pessoa
  registradas no NIAE (001 FR-015), cada uma com sua identidade própria. Somente
  Conclusões da Pessoa resolvida DEVEM ser consideradas. [001 FR-015; Const. — XI]
- **FR-007**: O contexto de cada formação DEVE ser lido da própria Conclusão, somente com
  os atributos já existentes na 001: curso, unidade, nível, modalidade, forma de oferta,
  ano de conclusão e data de conclusão, quando disponíveis. NÃO DEVE ser acrescentado
  atributo à Conclusão nem à Pessoa. [001 FR-009, FR-012; Const. — XI]
- **FR-008**: Cada formação DEVE ser identificada pela identidade da Conclusão, nunca por
  combinação de atributos. Formações com atributos iguais ou semelhantes DEVEM permanecer
  distintas. [001 FR-014; Const. — I]
- **FR-009**: Atributo não informado pela fonte DEVE permanecer "não informado". NÃO DEVE
  ser preenchido por padrão, deduzido de outro atributo ou de outra formação. [001 FR-010;
  Const. — III]
- **FR-010**: Esta feature NÃO DEVE fabricar rótulo, nome de exibição ou descrição da
  formação a partir de dados que não existem. NÃO DEVE criar formação manual, provisória
  ou declarada, nem formulário de cadastro de formação. [Const. — III, XXIX; Escopo]
- **FR-011**: A ordem das formações DEVE ser determinística e NÃO DEVE ter significado de
  domínio ("principal", "atual", "mais recente", "sugerida"). [001 FR-017]

**Pesquisa aplicável e entrada pendente**

- **FR-012**: Para cada formação, as **Campanhas aplicáveis** DEVEM ser exatamente as
  devolvidas pela consulta da 004 de Campanhas EM COLETA nas quais a Conclusão é
  ELEGÍVEL, no momento de referência (004 FR-052). A existência ou o estado de
  Participação NÃO DEVE alterar quais Campanhas são aplicáveis. [004 FR-052, FR-053]
- **FR-013**: Esta feature NÃO DEVE reimplementar, ampliar ou relaxar estado de Campanha,
  período, critérios ou elegibilidade. NÃO DEVE criar regra própria de período, janela,
  prazo de graça ou "Campanha vigente". [005 FR-014; Const. — IX, XXII]
- **FR-014**: Cada formação DEVE ser classificada, no momento de referência, em
  exatamente uma situação:
  (a) **sem pesquisa** — zero Campanhas aplicáveis;
  (b) **disponível para iniciar** — exatamente uma Campanha aplicável e nenhuma
  Participação do par;
  (c) **disponível para retomar** — exatamente uma Campanha aplicável e Participação do
  par em rascunho;
  (d) **já concluída** — exatamente uma Campanha aplicável e Participação do par
  concluída (006 FR-001);
  (e) **ambiguidade operacional** — duas ou mais Campanhas aplicáveis, qualquer que seja
  a existência ou o estado de Participações.
  Somente (b) e (c) são **entrada pendente**. (b) a (e) são **pesquisa aplicável**.
  [Arquitetura; Clarifications]
- **FR-015**: Para formação "sem pesquisa", o resultado NÃO DEVE expor critérios de
  Campanha, pendências de elegibilidade nem distinguir "não há Campanha em coleta" de
  "não é elegível". [Const. — XVI, XXII; Escopo]
- **FR-016**: A situação da Participação do par DEVE ser obtida com a mesma semântica da
  consulta de localização da 005 (localizar sem criar — 005 FR-046) e pelo momento de
  conclusão da 006, sem criar nem alterar nada. Para (c) e (d), o resultado DEVE incluir a Participação existente.
  [005 FR-046; 006 FR-001]

**Situação de entrada**

- **FR-017**: DEVE existir uma **consulta da situação de entrada** que, para a Pessoa e o
  momento de referência, devolva **todas** as formações da Pessoa — inclusive as "sem
  pesquisa", "já concluída" e em "ambiguidade operacional" —, cada uma com seu contexto
  (FR-007), sua situação (FR-014) e, quando houver, a Campanha aplicável, as Campanhas da
  ambiguidade e a Participação existente; e exatamente uma das situações globais de
  FR-018 a FR-022. Nenhuma formação DEVE ser omitida por causa da sua situação.
  [Arquitetura; Clarifications]
- **FR-018**: **Sem formação disponível**: a Pessoa não tem nenhuma Conclusão Acadêmica no
  NIAE. NÃO DEVE ser tratada como erro de identidade, de dados acadêmicos, de Pessoa
  inexistente nem como "sem pesquisa". [Escopo; 001 FR-002]
- **FR-019**: **Sem pesquisa disponível**: a Pessoa tem formações e todas estão "sem
  pesquisa" — "nenhuma pesquisa disponível para suas formações neste momento" —,
  resultado normal, sem erro de identidade ou de dados acadêmicos. [Escopo]
- **FR-020**: **Entrada resolvida**: exatamente uma formação tem entrada pendente. A
  situação DEVE identificar essa formação, sua Campanha aplicável e, se houver, a
  Participação em rascunho. NÃO DEVE exigir seleção, ainda que existam outras formações
  "sem pesquisa", "já concluída" ou em "ambiguidade operacional". [Const. — XIV;
  Clarifications]
- **FR-021**: **Seleção necessária**: duas ou mais formações têm entrada pendente. O
  domínio NÃO DEVE escolher nenhuma. Formações "já concluída" e em "ambiguidade
  operacional" NÃO DEVEM ser contadas como alternativas nem aumentar o número de
  alternativas. NÃO DEVE existir prioridade, ranking, sugestão ou preferência por
  recência, ano, unidade, nível, modalidade, ordem de incorporação ou situação da
  Participação (rascunho não precede "disponível para iniciar", nem o contrário). A
  escolha DEVE ser de **formação** (Conclusão), nunca de Campanha. [Const. — I, XI,
  XXIX; 005/DP-501]
- **FR-022**: **Sem entrada pendente**: ao menos uma formação tem pesquisa aplicável e
  nenhuma tem entrada pendente. Inclui, entre outras combinações: todas as formações com
  pesquisa aplicável "já concluída"; somente formações em "ambiguidade operacional";
  mistura de concluídas e ambíguas; e qualquer uma dessas acompanhada de formações "sem
  pesquisa". NÃO DEVE exigir seleção. NÃO DEVEM ser criadas situações globais para
  distinguir essas combinações: o detalhe está na situação de cada formação devolvida,
  que DEVE ser preservada. [Clarifications; 004/DP-404]
- **FR-023**: As situações globais DEVEM ser mutuamente exclusivas e cobrir todos os
  casos: sem formação disponível; sem pesquisa disponível; sem entrada pendente; entrada
  resolvida; seleção necessária. Elas DEVEM ser derivadas exclusivamente das situações
  das formações (FR-014). [Arquitetura; Const. — XXVI]
- **FR-024**: A consulta da situação de entrada NÃO DEVE gravar nada: nem Participação,
  nem associação entre Conclusão e Campanha, nem seleção, nem registro de acesso.
  [Const. — XVI, XXII]

**Ambiguidade de Campanhas sobre a mesma formação**

- **FR-025**: Quando uma formação tem duas ou mais Campanhas aplicáveis, o sistema NÃO
  DEVE escolher a mais recente, a primeira, a de período mais curto, a de critério mais
  restritivo, nem aplicar qualquer prioridade. [004 FR-051; 004/DP-404]
- **FR-026**: A ambiguidade DEVE identificar a formação e todas as Campanhas aplicáveis
  envolvidas, para diagnóstico e governança. A ordem dessas Campanhas é a determinística
  da 004 e NÃO DEVE significar preferência. [004 FR-052]
- **FR-027**: Enquanto houver ambiguidade sobre uma formação, a entrada por ela NÃO DEVE
  iniciar nem retomar Participação, mesmo que exista Participação numa das Campanhas
  envolvidas. A existência, a ausência ou o estado de Participação NÃO DEVE desempatar:
  NÃO DEVE ser escolhida a Campanha com Participação, nem a ainda não respondida.
  [004/DP-404; Const. — XXIX; Clarifications]
- **FR-027a**: A ambiguidade DEVE ser **local à formação afetada**: a formação continua
  devolvida pela consulta, marcada como ambígua, e a ambiguidade NÃO DEVE impedir a
  resolução automática nem a seleção de outras formações com entrada pendente.
  [Clarifications; Const. — XIV]
- **FR-028**: NÃO DEVE ser pedido ao egresso que escolha entre Campanhas, nem que
  compreenda identificadores, nomes ou períodos internos de Campanha. A resolução da
  ambiguidade é de governança e configuração futuras (004/DP-404; DP-701). [Const. — X,
  XIV]

**Entrada: resolução e Participação**

- **FR-029**: DEVE existir uma **entrada** que receba a Pessoa resolvida, o momento de
  referência e, opcionalmente, uma formação, e que entregue a Participação correspondente
  ou a situação que impede a entrada. [Arquitetura]
- **FR-030**: Sem formação informada, a entrada DEVE proceder somente quando a situação
  de entrada é **entrada resolvida**, usando a única formação com entrada pendente. Em
  qualquer outra situação (seleção necessária, sem entrada pendente, sem pesquisa
  disponível, sem formação disponível), DEVE devolvê-la sem criar nada. [Const. — XIV,
  XXIX; Clarifications]
- **FR-031**: Com formação informada, a entrada DEVE: (a) recusar formação que não
  pertence à Pessoa (FR-044); (b) se a formação está "sem pesquisa", devolver isso sem
  criar nada; (c) se está em "ambiguidade operacional", devolver a ambiguidade sem criar
  nem retomar nada; (d) se está "já concluída", devolver a Participação concluída com a
  indicação "concluída", sem criar nem alterar nada; (e) se tem entrada pendente,
  prosseguir com a Campanha aplicável (FR-033). [Arquitetura]
- **FR-032**: A entrada DEVE reavaliar formações, Campanhas aplicáveis e Participação no
  seu próprio momento de referência, sem depender de resultado de consulta anterior.
  Sem momento de referência explícito, a admissão pela 005 DEVE usar o relógio no
  instante do início, e não o da avaliação: uma Campanha encerrada entre os dois instantes
  rejeita o início (FR-046).
  [Const. — XXVI; Arquitetura]
- **FR-033**: Para formação com entrada pendente, a entrada DEVE usar a operação de
  início da 005 com a Campanha aplicável e a Conclusão selecionada, que cria a
  Participação se o par não a tem ou devolve a existente sem alterá-la (005 FR-011,
  FR-013). Esta feature NÃO DEVE duplicar, contornar ou reimplementar o início.
  [005 FR-011, FR-013, FR-014]
- **FR-034**: O resultado da entrada DEVE indicar: **iniciada** (Participação criada
  agora); **em rascunho** (Participação existente, não concluída); ou **concluída**
  (Participação existente com momento de conclusão — 006 FR-001, inclusive quando a
  conclusão ocorreu entre a avaliação e o início). Em todos os casos, a Participação
  devolvida é a do par. [005 FR-013; 006 FR-001]
- **FR-035**: Para Participação **concluída**, a entrada NÃO DEVE criar outra, reabrir,
  desfazer a conclusão nem permitir edição. Se Participação concluída pode ser editada é
  006/DP-603. [006 FR-039, FR-041]
- **FR-036**: A entrada NÃO DEVE executar a jornada: não responde, não navega, não
  conclui, não calcula percurso. Ela entrega a Participação para a 006 (006 FR-051).
  [Escopo; 006 FR-051]
- **FR-037**: A entrada NÃO DEVE gravar nada além do que a operação de início da 005
  grava. NÃO DEVE persistir seleção, associação entre Conclusão e Campanha, momento de
  acesso ou origem da entrada. [Const. — XVI, XXII]

**Longitudinalidade**

- **FR-038**: Participação anterior da mesma Conclusão, em outra Campanha, concluída ou
  não, NÃO DEVE impedir, condicionar nem ser reutilizada pela entrada numa Campanha
  posterior. A Participação devolvida DEVE ser sempre a do par (Campanha aplicável,
  Conclusão). [Const. — I; 004 FR-050; 005 FR-007, FR-008]
- **FR-039**: Formações diferentes da mesma Pessoa DEVEM levar a Participações distintas
  e independentes. Entrar por uma formação NÃO DEVE criar, alterar ou condicionar a
  Participação de outra. [Const. — I, XI; 005 FR-009]

**Contexto institucional ≠ resposta declarada**

- **FR-040**: Os atributos da Conclusão PODEM ser usados para identificar a formação,
  verificar elegibilidade (pela 004) e contextualizar a Participação (pela própria
  Conclusão). Eles NÃO DEVEM ser gravados como Respostas, nem copiados para a
  Participação, as Respostas, a Pessoa ou a Campanha. [Const. — III; 005 FR-005]
- **FR-041**: Esta feature NÃO DEVE remover, ocultar, pular, pré-preencher ou condicionar
  Perguntas da Versão aplicada, em particular Q10–Q19. A decisão sobre Q10–Q19 como
  pergunta ou contexto institucional permanece 003/DP-307. [Herdado — Q10–Q19 na
  baseline; 003/DP-307; 006 FR-007]
- **FR-042**: Esta feature NÃO DEVE comparar atributos da Conclusão com respostas
  declaradas, nem sinalizar divergência (005/DP-508). [005 FR-043]
- **FR-043**: O contexto institucional da Participação DEVE continuar a ser o da sua
  Conclusão, lido dela, para que a unidade, o curso e demais dimensões de uma
  Participação decorram da formação acompanhada. [Const. — XI; 005 FR-005]

**Rejeições, privacidade e consistência**

- **FR-044**: Entrada com formação que não pertence à Pessoa resolvida — de outra Pessoa
  ou inexistente — DEVE ser rejeitada explicitamente, sem criar nada, com a mesma
  rejeição nos dois casos (sem oráculo de existência). [Const. — I, XVI; Arquitetura]
- **FR-045**: Rejeições e resultados NÃO DEVEM revelar atributos, nome ou Participações de
  outra Pessoa, nem registrar em log dados pessoais ou atributos acadêmicos; PODEM citar
  motivo e identificadores técnicos. [Const. — XVI; Observabilidade]
- **FR-046**: Toda rejeição DEVE ser explícita, identificar o motivo e não produzir
  alteração. Rejeições da operação de início da 005 que ocorram apesar da reavaliação
  (por exemplo, por mudança simultânea de estado) DEVEM ser propagadas de forma explícita,
  sem criar nada. [004 FR-057; 005 FR-012]

**Modelo e fronteiras**

- **FR-047**: Esta feature NÃO DEVE criar modelo, tabela, coluna ou registro persistido.
  NÃO DEVEM ser criados, como entidade persistida: opção de formação, contexto de
  entrada, resolução, pesquisa disponível, seleção, sessão de entrada, escolha de
  matrícula, associação Campanha ↔ Conclusão ou atribuição de Campanha. Valores
  **imutáveis de leitura**, recalculados a cada consulta e nunca gravados (no padrão de
  `Elegibilidade` da 004 e `SituacaoDaJornada` da 006), são permitidos para devolver o
  resultado. [Const. — XXII; Escopo]
- **FR-048**: NÃO DEVEM ser criados provedor de identidade ou autenticação, resolvedor de
  Pessoa ou de identidade, sessão de contexto ou de entrada, usuário de portal ou
  abstração sem consumidor nesta feature. [Const. — XV, XXII]
- **FR-049**: As capacidades desta feature são do domínio. Elas NÃO DEVEM ser expostas a
  egressos ou usuários — interface, URL, API, página — antes da existência da fronteira
  de identidade, porque a entrada cria Participação em nome da Pessoa (005/DP-505;
  004/DP-406). [Const. — X, XV, XVI]
- **FR-050**: Os resultados DEVEM ser de domínio ou de aplicação. NÃO DEVEM ser produzidos
  HTML, modelo de tela, ViewModel, textos de interface ou mensagens ao egresso.
  [Escopo; Const. — XXII]
- **FR-051**: Esta feature NÃO DEVE criar dashboard, indicador, agregação, contagem,
  snapshot, dataset analítico, exportação, gráfico, nem reproduzir funcionalidade do GeN
  ou de painel institucional existente (Looker Studio). [Const. — VI, XIX; Escopo]
- **FR-052**: Esta feature NÃO DEVE alterar modelos, operações, contratos ou dados das
  Features 001 a 006. [Escopo]
- **FR-053**: Esta feature NÃO DEVE consultar a fonte acadêmica diretamente nem disparar
  incorporação: lê as Conclusões já incorporadas no NIAE (001, "Leitura pelos
  consumidores"). Quando a incorporação deve ocorrer antes da entrada é 001/DP-006.
  [001 SC-008; Const. — V]

### Key Entities *(include if feature involves data)*

Nenhuma entidade nova. Entidades consumidas, todas inalteradas:

- **Pessoa** *(001)*: ponto de partida, já resolvida. Não tem atributo acadêmico.
- **Conclusão Acadêmica** *(001)*: a **formação**. Unidade de escolha e de contexto.
  Atributos institucionais: curso, unidade, nível, modalidade, forma de oferta, ano e
  data de conclusão, com "não informado" explícito.
- **Campanha** *(004)*: aplicável ou não a cada Conclusão no momento de referência;
  nunca escolhida pelo egresso.
- **Participação** *(005, com conclusão da 006)*: criada ou devolvida pela operação de
  início da 005; situação derivada: inexistente, em rascunho, concluída.

**Valores derivados, não persistidos**: Campanhas aplicáveis de uma formação, situação da
formação, situação da Participação do par, situação de entrada, resultado da entrada.

**Entidades deliberadamente não criadas**: Usuario, Conta, Credential, Login, Identity,
CandidateIdentity, IdentityProvider, AuthenticationProvider, PersonResolver,
IdentityResolver, PersonMatcher, ContextSession, EntrySession, EnrollmentChoice,
EligibleCampaignMembership, CampaignAssignment, Selection, PortalUser, OpcaoDeFormacao,
ContextoDeEntrada, Resolucao, PesquisaDisponivel.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| Formações da Pessoa | Institucional | Conclusões Acadêmicas da Pessoa (001) | Divergência com a fonte é da 001 (001/DP-005); não tratada aqui |
| Curso, unidade, nível, modalidade, forma de oferta, ano/data | Institucional | Atributos da Conclusão (001), lidos, nunca copiados | Não comparados com respostas (FR-042; 005/DP-508) |
| Campanhas aplicáveis | Derivado | Consulta da 004 no momento de referência | Não persistido |
| Situação da formação e situação de entrada | Derivado | Campanhas aplicáveis + Participação do par; contagem de entradas pendentes (FR-014, FR-017) | Não persistido |
| Situação da Participação do par | Derivado | Existência (005) e momento de conclusão (006) | Não persistido |
| Participação | Registro do sistema | Operação de início da 005 | Unicidade do par (005 FR-006) |
| Respostas | Declarado | Somente pela jornada (005/006); nenhuma criada aqui | — |

### Análise de persistência

O solicitante pediu demonstrar, antes de propor entidade nova, qual informação precisaria
persistir e por que não poderia ser derivada.

| Informação | Pode ser derivada? | De onde | Persistir? |
|------------|--------------------|---------|------------|
| Formações da Pessoa | Sim | Conclusões da Pessoa (001) | Não |
| Contexto de cada formação | Sim | Atributos da Conclusão (001) | Não |
| Campanhas aplicáveis | Sim | 004, no momento de referência | Não — mudaria com o tempo; gravar criaria cópia desatualizável |
| Situação da formação (sem pesquisa, iniciar, retomar, concluída, ambígua) | Sim | Campanhas aplicáveis + Participação do par | Não |
| Entrada pendente | Sim | Situação da formação | Não |
| Participação existente e sua situação | Sim | 005 (par) e 006 (momento de conclusão) | Já persistida pela 005/006 |
| Formação selecionada | Sim | Conclusão da Participação criada | Não — a Participação já a registra (005 FR-002) |
| Campanha da entrada | Sim | Campanha da Participação | Não — idem |
| Seleção temporária antes da entrada | Não precisa existir | Parâmetro da entrada | Não — sem consumidor |

**Conclusão**: nenhuma informação nova precisa persistir. A única gravação possível é a
Participação, já modelada pela 005.

### Modelo conceitual

```text
situacao_de_entrada(Pessoa, agora)                        — consulta; nunca grava
  formações ← Conclusões da Pessoa (001), ordem sem significado
  para cada formação f:
    C(f) ← Campanhas EM COLETA em que f é ELEGÍVEL (004), em agora
    |C(f)| = 0                          → SEM PESQUISA
    |C(f)| ≥ 2                          → AMBIGUIDADE OPERACIONAL (C(f), sem preferência;
                                           Participações não consultadas para desempatar)
    |C(f)| = 1 (Campanha c):
      p ← Participação do par (c, f)    (005, localizar sem criar)
      p inexistente                     → DISPONÍVEL PARA INICIAR     ┐ entrada
      p sem momento de conclusão        → DISPONÍVEL PARA RETOMAR (p) ┘ pendente
      p com momento de conclusão        → JÁ CONCLUÍDA (p)
  P ← formações com entrada pendente
  formações = ∅                         → SEM FORMAÇÃO DISPONÍVEL
  todas SEM PESQUISA                    → SEM PESQUISA DISPONÍVEL
  |P| = 0                               → SEM ENTRADA PENDENTE   (concluídas/ambíguas informadas)
  |P| = 1                               → ENTRADA RESOLVIDA (f ∈ P)
  |P| ≥ 2                               → SELEÇÃO NECESSÁRIA (P)
  (todas as formações são sempre devolvidas, com sua situação)

entrar(Pessoa, agora, formação?)                          — único ponto de escrita
  formação informada e não é da Pessoa  → rejeita; nada criado
  s ← situacao_de_entrada(Pessoa, agora)                  (reavaliada; FR-032)
  sem formação informada:
    s ≠ ENTRADA RESOLVIDA               → devolve s; nada criado
    f ← a única formação com entrada pendente
  f SEM PESQUISA                        → devolve "sem pesquisa"; nada criado
  f AMBIGUIDADE OPERACIONAL             → devolve ambiguidade; nada criado nem retomado
  f JÁ CONCLUÍDA (p)                    → CONCLUÍDA (p); nada criado nem alterado
  f com entrada pendente (c):
    (p, criada?) ← iniciar_participacao(c, f, agora)      (005; cria ou devolve)
    criada                              → INICIADA (p)
    p sem momento de conclusão          → EM RASCUNHO (p)
    p com momento de conclusão          → CONCLUÍDA (p)    (concluída em paralelo)
  → a Participação segue para a jornada (006)
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Para os 15 casos de referência (A a O), 100% das situações de entrada e dos
  resultados de entrada coincidem com a tabela "Casos de referência".
- **SC-002**: Para cada Pessoa dos cenários da fonte simulada, 100% das suas Conclusões
  aparecem na consulta, cada uma uma única vez, com 0 atributos inventados e 0 atributos
  atribuídos à Pessoa.
- **SC-003**: Com exatamente 1 formação com entrada pendente — inclusive quando há outras
  formações já concluídas ou ambíguas —, a entrada se completa sem nenhuma formação
  informada em 100% dos testes; com 2 ou mais formações com entrada pendente, 0 entradas
  sem formação informada criam Participação.
- **SC-003a**: Em 100% dos testes, formações "já concluída" e em "ambiguidade
  operacional" aparecem na consulta com sua situação e nunca são contadas como
  alternativas: com 0 entradas pendentes, nenhuma seleção é exigida e 0 Participações
  são criadas.
- **SC-004**: Em 100% dos casos com 2 ou mais Campanhas aplicáveis à mesma formação, a
  formação fica em ambiguidade operacional — com ou sem Participação, em rascunho ou
  concluída, em alguma das Campanhas —, 0 Participações são criadas ou retomadas por essa
  formação e 0 Campanhas são indicadas como preferidas.
- **SC-005**: Repetir a entrada da mesma formação 2 ou mais vezes, inclusive de forma
  simultânea, resulta em exatamente 1 Participação para o par.
- **SC-006**: Para uma Conclusão com Participação concluída numa Campanha anterior, uma
  nova Campanha aplicável leva a 1 nova Participação, e a anterior permanece com o mesmo
  momento de início, momento de conclusão e Respostas.
- **SC-007**: Após qualquer consulta ou entrada, o número de Respostas criadas é 0, e
  nenhum atributo de Conclusão aparece copiado em Participação, Resposta, Pessoa ou
  Campanha.
- **SC-008**: 100% das consultas da situação de entrada deixam o banco inalterado
  (mesmas linhas em todas as tabelas antes e depois).
- **SC-009**: 100% das entradas com formação de outra Pessoa são rejeitadas sem criar nada
  e sem revelar atributos da Conclusão alheia.
- **SC-010**: Ao final da feature, 0 modelos, tabelas ou colunas novas existem, e 0
  modelos, operações ou contratos das Features 001 a 006 foram alterados.
- **SC-011**: Ao final da feature, não existe nenhum mecanismo de autenticação, sessão,
  credencial, busca de Pessoa, reconciliação de identidade, interface, URL, API,
  indicador, exportação ou painel.
- **SC-012**: Dois momentos de referência distintos (dentro e fora do período de uma
  Campanha) produzem situações de entrada coerentes com o estado da 004 em 100% dos
  testes, inclusive no último dia do período e no dia seguinte.

## Assumptions

- **Pessoa já incorporada**: a Pessoa resolvida e suas Conclusões já estão no NIAE. Quando
  e como a incorporação é disparada antes da entrada pertence à fronteira de identidade e
  a 001/DP-006 (FR-053).
- **Pessoa sem Conclusões não ocorre pela incorporação atual** (001 FR-039). A situação
  "sem formação disponível" é mantida porque a cardinalidade conceitual é 0..N
  (001 FR-002) e porque fontes ou features futuras podem produzi-la; nos testes, a Pessoa
  é construída diretamente. É uma verificação, não uma abstração.
- **Elegibilidade estável durante a coleta**: Campanha aberta é imutável (004 FR-043) e a
  incorporação não altera Conclusões (001). Assim, uma Participação existente numa
  Campanha EM COLETA corresponde sempre a uma formação que segue elegível. Correção
  acadêmica futura é 005/DP-507.
- **Participação criada na entrada**: a entrada cria a Participação pela 005 no momento em
  que é solicitada, como a 005 já define. O significado operacional de Participação sem
  Respostas é DP-703.
- **Momento de referência**: como na 004, 005 e 006; o plan define como substituí-lo em
  testes.
- **Somente dados fictícios**: enquanto 005/DP-504 e 001/DP-009 estiverem abertas, a
  feature é exercida apenas com a fonte simulada.
- **Versões publicadas apenas no ambiente de teste**: como na 005 e na 006, para que haja
  Campanhas EM COLETA nos testes (002/DP-001).

## Relação com outras features

**001** — consumida sem alteração: lista de Conclusões da Pessoa e seus atributos
(FR-015, FR-016); ordem sem significado (FR-017); "não informado" (FR-010). A 007 não
consulta a fonte nem dispara incorporação.

**002/003** — consumidas sem alteração. Q10–Q19 continuam perguntas declaradas da
baseline; a 007 não as oculta nem pré-preenche (FR-041; 003/DP-307).

**004** — consumida sem alteração: a consulta de Campanhas EM COLETA aplicáveis a uma
Conclusão (FR-052) é a única fonte de "pesquisa disponível". A 004 previu que essa
consulta permitiria "resolver a Campanha sem convite"; a 007 a usa e preserva DP-404 ao
declarar ambiguidade em vez de escolher.

**005** — consumida sem alteração: localizar Participação do par (FR-046) e iniciar
(FR-011, FR-013). A 005 encaminhou à "feature seguinte" a escolha entre Campanhas
sobrepostas (004/DP-404) e entre Conclusões da mesma Pessoa (DP-501) na apresentação ao
egresso: a 007 trata ambas **sem decidir a regra institucional** — Conclusões são
selecionadas pelo egresso; Campanhas sobrepostas viram ambiguidade.

**006** — consumida sem alteração: a 007 entrega a Participação já identificada que a
jornada exige (006 FR-051) e lê o momento de conclusão para informar "concluída".

**Futuras**:

- **Identidade / acesso**: entregará a Pessoa resolvida (FR-001) e decidirá como a
  entrada é exposta (FR-049; 004/DP-406).
- **Interface pública de entrada**: apresentará as formações ("Sobre qual formação do Ifes
  você responderá esta pesquisa?"), com acessibilidade e responsividade (Princípios XX e
  XXI), a partir da consulta (FR-017).
- **Contextualização do instrumento**: se 003/DP-307 for decidida, uma Versão futura
  poderá retirar Q10–Q19 da jornada, usando o contexto da Conclusão já associado à
  Participação.
- **Acompanhamento da coleta e análises**: Participação → Conclusão → contexto
  institucional já basta para dimensões por unidade, curso, nível e coorte (FR-043).

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade (NON-NEGOTIABLE)**: a entrada sempre alcança a Participação do
  par (Campanha aplicável, Conclusão); Participações anteriores não são reutilizadas nem
  impedem novas (FR-038); formações não são fundidas (FR-008, FR-039).
- **III — Institucional ≠ declarado (NON-NEGOTIABLE)**: atributos da Conclusão
  identificam e contextualizam, nunca viram Resposta (FR-040); Q10–Q19 não são
  pré-preenchidas nem ocultadas (FR-041).
- **IV — Proveniência**: a formação é a própria Conclusão, com fonte e referência de
  origem da 001; o contexto da Participação é lido da Conclusão, nunca copiado (FR-043).
- **V — Integrações desacopladas (NON-NEGOTIABLE)**: a entrada parte de uma Pessoa do NIAE,
  independente do mecanismo de identidade (FR-001); não consulta a fonte acadêmica
  (FR-053).
- **VI — Composição sem expansão de escopo**: compõe 001, 004, 005 e 006; não absorve
  identidade, Portal ou BI (FR-048, FR-049, FR-051).
- **VII — Conceitos distintos (NON-NEGOTIABLE)**: o egresso escolhe a formação
  (Conclusão); a Campanha é determinada pelo domínio; a Participação é a do par
  (FR-021, FR-028, FR-033).
- **XI — Pessoa única, contextos múltiplos**: nenhuma unidade, curso ou nível é atribuído
  à Pessoa (FR-007); cada formação conserva sua unidade (caso L).
- **XIV — Redução de fricção**: uma única entrada pendente dispensa seleção, mesmo com
  outras formações concluídas ou ambíguas (FR-020, FR-030); formações concluídas não
  aumentam as alternativas (FR-021); o egresso nunca precisa entender Campanha (FR-028).
- **XV — Identidade substituível**: nenhum mecanismo de identidade ou autenticação
  (FR-001, FR-002, FR-048).
- **XVI — Privacidade (NON-NEGOTIABLE)**: só formações da própria Pessoa (FR-006);
  rejeição sem dados alheios (FR-045); nada gravado na consulta (FR-024); nada exposto sem
  fronteira de identidade (FR-049).
- **XIX — Não é BI**: nenhum indicador ou painel (FR-051).
- **XXII — YAGNI**: nenhum modelo novo (FR-047; Análise de persistência); nenhuma
  abstração sem consumidor (FR-048).
- **XXIX — Hipóteses explícitas (NON-NEGOTIABLE)**: Campanhas sobrepostas, várias
  formações, Q10–Q19, identidade e edição pós-conclusão continuam pendentes. As escolhas
  de produto desta feature foram confirmadas pelo solicitante (Clarifications) e não
  resolvem nenhuma regra institucional.

**Tensões identificadas (não são conflitos)**:

- **XIV × Q10–Q19 perguntadas depois da contextualização**: a futura interface poderá
  dizer "esta pesquisa refere-se ao curso X, Campus Y" e, em seguida, a jornada ainda
  perguntará curso e campus. Isso é deliberado: 003/DP-307 não foi decidida e o
  instrumento não pode ser alterado silenciosamente (Princípio XIII).
- **XIV × ambiguidade bloqueia o egresso**: enquanto houver Campanhas sobrepostas sobre
  uma formação, o egresso não consegue entrar por ela (as demais formações não são
  afetadas, pois a ambiguidade é local). É o efeito correto de 004/DP-404:
  a governança deve evitar ou resolver a sobreposição.
- **001 FR-039 × "sem formação disponível"**: a situação não ocorre com a incorporação
  atual; é mantida como ramo explícito, sem abstração, porque o solicitante a pediu e a
  cardinalidade conceitual a admite.

Nenhum conflito com a Constituição ou com as Features 001 a 006 foi identificado.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. Pertence de fato ao domínio de acompanhamento? Sim. Associar a Participação à
   Conclusão Acadêmica correta é o núcleo do acompanhamento longitudinal (Princípio I).
   Identificar a Pessoa não pertence e fica fora (FR-001).
2. É necessária ao ciclo de acompanhamento? Sim. Sem ela, nenhuma Participação é
   alcançada a partir de uma Pessoa.
3. Existe ou está prevista solução institucional mais adequada? Para identidade, sim:
   Portal do Egresso (PAEG Art. 10, I; Art. 13), identidade institucional, Gov.br — por
   isso ficam fora. Para a escolha da formação acompanhada, não.
4. Integração seria suficiente? Para identidade, sim, no futuro. Para resolver formação,
   Campanha e Participação, não: são regras do domínio do NIAE.
5. A incorporação aumentaria desnecessariamente o acoplamento do núcleo? Não. A feature
   depende apenas de 001, 004, 005 e 006, e de uma Pessoa do NIAE, compatível com
   qualquer mecanismo de identidade futuro.

## Out of Scope *(mandatory)*

- Autenticação, autorização do egresso, OTP, senha, Gov.br, SSO, link mágico, sessão;
  CPF ou e-mail como mecanismo de acesso.
- Busca de Pessoa; entrada por CPF, e-mail, matrícula ou nome.
- Portal do Egresso; integração acadêmica real; disparo de incorporação.
- Reconciliação, fusão ou deduplicação de Pessoas; matching.
- Cadastro ou formulário de formação; alteração ou correção de Conclusão Acadêmica.
- Remoção, ocultação ou pré-preenchimento de Q10–Q19 ou de qualquer Pergunta.
- Execução da jornada; resposta; conclusão; edição pós-conclusão.
- Política para Campanhas sobrepostas; prioridade entre Campanhas.
- Regra para Pessoa com várias formações (responder por todas, ordem, compartilhamento).
- Interface, HTML, URL, API, ViewModel, textos ao egresso.
- Editor, governança, comunicação, convite, lembrete.
- Dashboard, GeN, Looker Studio, indicadores, agregações, snapshot, exportação.
- Qualquer alteração das Features 001 a 006.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: decisões novas usam o prefixo 7 (DP-701…). As das features anteriores são
citadas como 00n/DP-nnn.

**Novas nesta feature**

- **DP-701** — DECISÃO PENDENTE: como uma ambiguidade operacional (duas ou mais Campanhas
  aplicáveis à mesma formação) é comunicada ao egresso e encaminhada a quem configura as
  Campanhas — mensagem, canal de suporte, responsável. Instância competente: Proex/CPAEG,
  com DIREC/CSAEG. Impacto: FR-026 a FR-028; futura interface. Tratamento provisório: o
  domínio devolve a ambiguidade com a formação e as Campanhas envolvidas; nada é
  notificado nem registrado. A regra que evita ou resolve a sobreposição continua em
  004/DP-404.
- **DP-702** — DECISÃO PENDENTE: quais informações podem ser apresentadas ao egresso para
  distinguir formações quando os atributos institucionais disponíveis não bastam (por
  exemplo, mesmo curso, unidade e ano, ou atributos não informados), e se isso exige
  ampliar o contexto mínimo da 001 (por exemplo, período de ingresso ou identificador de
  matrícula). Instância competente: CPAEG, com o registro acadêmico e o encarregado de
  dados. Depende de 001/DP-004 e 001/DP-007. Impacto: FR-008 a FR-010; futura interface.
  Tratamento provisório: formações distintas pela identidade; só atributos existentes;
  nenhum rótulo fabricado; nenhum atributo acrescentado.
- **DP-703** — DECISÃO PENDENTE: significado, para o acompanhamento da coleta, de
  Participação criada na entrada e ainda sem Respostas (conta como "iniciada"?), dado que
  a entrada cria a Participação ao ser solicitada. Instância competente: CPAEG/Proex.
  Impacto: indicadores operacionais futuros (Princípio XIX). Tratamento provisório:
  Participação criada pela 005 na entrada; nenhuma métrica nesta feature.

**Herdadas e afetadas por esta feature**

- **004/DP-404** — Campanhas EM COLETA sobrepostas: a 007 não escolhe; devolve
  ambiguidade operacional e não inicia nem retoma Participação pela formação ambígua
  (FR-025 a FR-028). Mantida aberta.
- **004/DP-406** — forma de acesso e mecanismo de identificação: a 007 parte de Pessoa
  resolvida e não é exposta sem essa fronteira (FR-001, FR-049). Mantida aberta.
- **005/DP-501** — várias Conclusões elegíveis da mesma Pessoa na mesma Campanha: a 007
  exige seleção de formação, uma Participação por formação, sem compartilhamento nem
  prioridade (FR-021, FR-039). Se a Pessoa deve responder por todas, em que ordem ou com
  respostas compartilhadas continua pendente.
- **003/DP-307** — Q10–Q19 como pergunta ou contexto institucional: a 007 apenas associa a
  formação à Participação; não remove, oculta nem pré-preenche (FR-041).
- **005/DP-508** — divergência entre resposta declarada e dado institucional: não tratada
  (FR-042).
- **006/DP-603** — edição pós-conclusão: a entrada informa "concluída" e não reabre
  (FR-035).
- **005/DP-507** e **001/DP-005** — correção de dado acadêmico e seu efeito sobre
  Participação: a 007 segue a 004 no momento de referência, sem regra própria.
- **001/DP-003** — reconciliação de identidade entre fontes: nada nesta feature (FR-004).
- **001/DP-006** — quando a incorporação ocorre: a 007 lê o que já foi incorporado
  (FR-053).
- **004/DP-409** — exclusão de Conclusão por atributo não informado: reflete-se como "sem
  pesquisa" (Edge Cases).

**Herdadas e ainda abertas** (não resolvidas por esta feature)

- **001/DP-001**, **001/DP-002** — fonte acadêmica oficial e seus identificadores.
- **001/DP-009**, **005/DP-504** — base legal, consentimento e retenção. **Bloqueiam o uso
  com dados reais.**
- **002/DP-001** — competência para publicar Versão.
- **005/DP-505** — quem pode consultar Participações identificadas.

**Encaminhadas a features futuras** (escopo de feature, não regra institucional)

- Fronteira de identidade que entrega a Pessoa resolvida.
- Interface pública de entrada e de seleção de formação, com acessibilidade e
  responsividade.
- Acompanhamento operacional da coleta (inclusive DP-703).
