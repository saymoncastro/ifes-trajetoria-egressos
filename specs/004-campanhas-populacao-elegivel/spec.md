# Feature Specification: Campanhas e população elegível

**Feature Branch**: `claude/feature-004-campanhas-463fe9`

**Created**: 2026-10-01

**Status**: Implementada e integrada à `main` em 2026-10-01 (PR #5).

**Input**: User description: "Feature 004 — Campanhas e população elegível. Campanha como
rodada institucional de aplicação de uma Versão publicada, com período de coleta,
população elegível definida sobre Conclusão Acadêmica por critérios simples e explícitos
(ano de conclusão, unidade, nível, modalidade, forma de oferta), avaliação determinística
e explicável de elegibilidade, tratamento conservador de dados ausentes, estados mínimos
(preparação, coleta, encerrada), imutabilidade após abertura, independência de convite,
múltiplas campanhas e longitudinalidade. Sem Participação, Resposta, autenticação,
comunicação ou motor de regras."

## Contexto

As três primeiras features encerraram a etapa estrutural do produto:

- **001** — quem é o egresso e qual formação: **Pessoa → Conclusão Acadêmica**, com fonte
  acadêmica simulada e substituível;
- **002** — como um instrumento é representado: **Pesquisa → Versão (RASCUNHO |
  PUBLICADA) → Seções → Perguntas → Opções**;
- **003** — qual é o instrumento institucional de referência: a baseline migrada do
  Formulário Egresso Ifes 2024, em RASCUNHO.

Falta responder: **esta Versão da Pesquisa será aplicada quando, a quais egressos e em
qual rodada institucional de acompanhamento?** A 002 deixou essa resposta explicitamente
para a Campanha (002, FR-008: não existe "Versão vigente"; a escolha da Versão aplicada
pertence à Campanha).

A PAEG prevê a aplicação de questionário eletrônico "com periodicidade a ser definida
pela Proex e Proen e/ou órgão competente" (Art. 10, II) e atribui às CSAEGs a aplicação
do questionário nas unidades (Art. 22, IV). A experiência atual do Ifes mostra uma
pesquisa com período definido de coleta, ampla divulgação institucional e acesso
espontâneo dos egressos durante o período, **sem** lista de convites individualmente
controlada.

Por isso, nesta spec:

> **Campanha é uma rodada institucional de observação.**
> **Campanha não é lista de destinatários.**

```text
Pesquisa ─────────── instrumento lógico                  (002)
  └── Versão ─────── configuração histórica              (002)
        ▲
        │ exatamente uma
        │
     Campanha ────── rodada de aplicação                 (004)
        ├── período de coleta (início, encerramento)
        ├── critérios de população (conjunto fixo e limitado)
        └── estado observável (EM PREPARAÇÃO | EM COLETA | ENCERRADA)
        ┆
        ┆ avalia (sem persistir)
        ▼
Conclusão Acadêmica ─ unidade de elegibilidade           (001)
  ▲
Pessoa ───────────── NÃO é unidade de elegibilidade       (001)

Futuro (005): Campanha 1 ── 0..N Participação N ── 1 Conclusão Acadêmica
```

> **Revisão semântica — ADR 0004 (2026-10-03).** Os critérios desta spec expressam a
> **abrangência do instrumento**: "esta Versão se aplica a estas formações". Nesta spec,
> ELEGÍVEL significa **na abrangência da Campanha** — não é a definição de egresso
> (Const. — II) nem pertença a uma coorte que se quer mobilizar. Foco de mobilização
> (coorte, campus, curso, situação de contato) não é configuração de Campanha e nunca
> decide quem pode responder; pertencerá ao futuro Lote de mobilização. A Campanha sem
> critério (população ampla) é o padrão. Comportamento, modelo e contratos permanecem os
> mesmos. *(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)*

### Princípios desta spec

1. **A população é definida por critérios, não por lista.** A Campanha preserva a
   *definição* de quem pertence à população; ela não guarda um rol de pessoas ou de
   conclusões e não exige convite. *(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)*
2. **A elegibilidade é avaliada sobre a Conclusão Acadêmica.** A mesma Pessoa pode ter uma
   conclusão elegível e outra não.
3. **Critérios explícitos e poucos.** Seis campos opcionais com semântica fixa substituem
   qualquer motor de regras.
4. **Conservadorismo diante de dado ausente.** "Não informado" nunca satisfaz um critério e
   nunca é inferido.
5. **Abrir é fixar.** Quando a coleta começa, Versão, período, critérios e nome da
   Campanha deixam de poder ser alterados.

### Termos usados nesta spec

- **Critérios de população**: o conjunto fixo de restrições opcionais da Campanha
  (FR-018). "Critério definido" é um critério com valor; "critério ausente" não restringe.
  Expressam a abrangência do instrumento, nunca foco de mobilização. *(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)*
- **População ampla**: Campanha sem nenhum critério definido; abrange todas as Conclusões
  Acadêmicas existentes no NIAE.
- **População conhecida**: as Conclusões Acadêmicas existentes no NIAE que, num dado
  momento, satisfazem os critérios da Campanha.
- **Abertura**: ato explícito que inicia a coleta e fixa a Campanha.
- **Data corrente** (ou **data de referência**): a data civil do momento da operação ou
  consulta, na timezone configurada do projeto (Assumptions).

## Clarifications

### Session 2026-10-01

Três escolhas de modelagem da primeira redação foram confirmadas pelo solicitante antes
do `/speckit-plan`. Elas deixam de ser hipóteses e passam a ser decisões desta feature.

- **Abertura** → Confirmada: a Campanha pode ser preparada antes do início do período;
  não existe estado AGENDADA; a abertura é sempre explícita e só pode ocorrer quando a
  data de referência está dentro do período. Não há scheduler, job ou abertura
  automática. Abertura agendada, se houver necessidade operacional real, será tratada por
  feature própria. (FR-034, FR-036, FR-042)
- **Encerramento** → Confirmado: a Campanha pode ser encerrada explicitamente antes da data
  final. Ao passar a data final, ela é **efetivamente** ENCERRADA, por estado derivado da
  data de referência, sem job ou processo que altere registros. Prorrogação e reabertura
  não existem nesta feature (DP-405 permanece aberta). (FR-038, FR-039)
- **População elegível dinâmica** → Confirmada com esta interpretação: nesta feature,
  "população elegível" é **o conjunto de Conclusões Acadêmicas que satisfaz os critérios
  da Campanha no momento da avaliação**. A população não é congelada na abertura e não é
  materializada (sem membros, destinatários, público ou lista de elegíveis). Conclusões
  incorporadas durante a coleta podem se tornar elegíveis. Correções futuras de dados
  acadêmicos podem alterar o resultado da avaliação. Toda contagem é "no momento da
  consulta" e **não** é denominador histórico oficial de taxa de resposta. A população de
  referência para indicadores continua em DP-408, a resolver quando houver consumidor
  concreto (monitoramento, dataset analítico ou indicadores). (FR-031 a FR-033)
- **Precedência temporal do estado** → Decidido na revisão do plan: o fim do período
  encerra a Campanha **tenha ela sido aberta ou não**. A regra é:
  1. houve encerramento antecipado → ENCERRADA;
  2. senão, a data de referência é posterior ao fim → ENCERRADA;
  3. senão, houve abertura → EM COLETA;
  4. senão → EM PREPARAÇÃO.

  Uma Campanha nunca aberta cuja janela expirou não continua parecendo acionável. Não
  existe estado EXPIRADA. (FR-034, FR-038)
- **Estado temporal × imutabilidade histórica** → Decidido antes do implement: são
  conceitos separados.
  - O **estado temporal** responde "esta Campanha aceita coleta agora?". Ele controla
    abertura, admissão de Participação e encerramento.
  - A **abertura histórica** (`aberta_em` registrado) responde "esta Campanha já entrou
    em coleta alguma vez?". Ela controla a imutabilidade.

  Antes da primeira abertura, a Campanha é preparação administrativa: pode ser corrigida
  ou removida, mesmo que seu período já tenha expirado e seu estado seja ENCERRADA. Se o
  período de uma Campanha nunca aberta e expirada for corrigido para uma janela futura,
  ela volta a EM PREPARAÇÃO, e isso **não** é reabertura, porque nunca houve abertura.
  Depois da primeira abertura, nome, Versão, período e critérios ficam imutáveis, e a
  Campanha não pode ser removida. Reabertura só existe conceitualmente para Campanha já
  aberta e continua fora do escopo (DP-405). (FR-039, FR-040, FR-043, FR-044)
- **Critério ausente × conjunto vazio** → Confirmado: critério não definido e critério
  definido sem nenhum valor são estados distintos. O primeiro não restringe; o segundo é
  configuração inválida e nunca é gravado. (FR-019, FR-023)
- **Timezone** → Confirmado: a data de referência usa a timezone configurada do projeto,
  não um fuso nominal fixado pela feature. (Assumptions)

## User Scenarios & Testing *(mandatory)*

<!--
  Os "usuários" desta feature são, por ora, o próprio domínio e quem o desenvolve e
  testa: nenhuma interface é criada e nenhuma competência institucional é atribuída
  (DP-402). Cada história é verificável por operações e consultas de domínio, com a
  fonte acadêmica simulada da 001 e Versões da 002.
-->

### User Story 1 - Criar uma Campanha vinculada a uma Versão (Priority: P1)

Quem prepara uma rodada institucional cria uma Campanha com um nome (por exemplo,
"Pesquisa Institucional de Egressos 2027") e a vincula a exatamente uma Versão de uma
Pesquisa. A Campanha nasce EM PREPARAÇÃO, tem identidade própria e não altera a Versão
nem a Pesquisa.

**Why this priority**: sem a Campanha não há como dizer qual Versão é aplicada em qual
rodada. É a base de todas as outras histórias e de toda Participação futura.

**Independent Test**: criar Pesquisa e Versão (002), criar duas Campanhas com a mesma
Versão e verificar identidades distintas, estado EM PREPARAÇÃO, Pesquisa obtida a partir
da Versão e Versão inalterada.

**Acceptance Scenarios**:

1. **Given** uma Versão PUBLICADA, **When** uma Campanha é criada com nome e essa Versão,
   **Then** a Campanha existe com identidade própria, estado EM PREPARAÇÃO, a Versão
   indicada e a Pesquisa dessa Versão.
2. **Given** uma Versão em RASCUNHO, **When** uma Campanha é criada com ela, **Then** a
   criação é aceita, a Campanha fica EM PREPARAÇÃO e a Versão continua em RASCUNHO e
   editável segundo as regras da 002.
3. **Given** uma Campanha existente com a Versão V, **When** outra Campanha é criada com a
   mesma Versão V, **Then** existem duas Campanhas distintas que usam V.
4. **Given** uma tentativa de criar Campanha sem Versão ou com nome vazio, **When** a
   criação é solicitada, **Then** ela é rejeitada e nada é criado.
5. **Given** uma Campanha EM PREPARAÇÃO com a Versão V1, **When** a Versão é trocada por
   V2 (de qualquer Pesquisa), **Then** a Campanha passa a referenciar apenas V2 e a
   Pesquisa de V2.

---

### User Story 2 - Definir período de coleta válido (Priority: P1)

A Campanha recebe um período institucional de coleta: data de início e data de
encerramento, ambas incluídas. O sistema não presume duração, periodicidade nem
calendário.

**Why this priority**: a rodada só tem significado institucional com "quando". O período
é pré-requisito da abertura e da futura admissão de Participações.

**Independent Test**: definir períodos válidos e inválidos numa Campanha EM PREPARAÇÃO e
verificar aceitação, rejeição sem alteração parcial e ausência de qualquer valor padrão.

**Acceptance Scenarios**:

1. **Given** uma Campanha EM PREPARAÇÃO, **When** o período 01/04/2027 a 30/06/2027 é
   definido, **Then** ele é registrado exatamente assim.
2. **Given** uma Campanha EM PREPARAÇÃO, **When** é definido um período com início igual
   ao encerramento, **Then** ele é aceito (coleta de um único dia).
3. **Given** uma Campanha EM PREPARAÇÃO, **When** é definido um período com início
   posterior ao encerramento, ou com uma das datas ausente, **Then** a definição é
   rejeitada, informando o problema, e o período anterior permanece inalterado.
4. **Given** uma Campanha recém-criada, **When** ela é consultada, **Then** o período
   aparece como não definido; nenhum período ou duração é atribuído automaticamente.

---

### User Story 3 - Definir população ampla de todos os egressos (Priority: P1)

Uma Campanha sem nenhum critério de população abrange todas as Conclusões Acadêmicas
existentes no NIAE, reproduzindo rodadas amplas como a experiência atual do Ifes, sem
configuração artificial de filtros.

**Why this priority**: é o caso institucional mais comum hoje e o caso padrão da
Campanha.

**Independent Test**: com a fonte simulada carregada, criar Campanha sem critérios e
verificar que toda Conclusão Acadêmica existente é ELEGÍVEL, inclusive as que têm
atributos não informados, e que a contagem da população é igual ao total de Conclusões.

**Acceptance Scenarios**:

1. **Given** uma Campanha sem critérios, **When** sua população é descrita, **Then** ela é
   apresentada como "todas as Conclusões Acadêmicas existentes no NIAE".
2. **Given** uma Campanha sem critérios e N Conclusões no NIAE, **When** a população
   conhecida é contada, **Then** o resultado é N.
3. **Given** uma Campanha sem critérios e uma Conclusão com unidade, nível e ano não
   informados, **When** a elegibilidade é avaliada, **Then** o resultado é ELEGÍVEL.

---

### User Story 4 - Definir população por período de conclusão (Priority: P1)

A Campanha pode restringir a população por ano de conclusão com limites absolutos e
inclusivos: ano mínimo, ano máximo, ambos ou nenhum. Recortes relativos ("últimos 5
anos") não são armazenados; a instituição converte-os em anos concretos, e a Campanha
histórica continua significando a mesma população.

**Why this priority**: o recorte temporal é o critério mais provável de uma rodada de
acompanhamento e precisa ser historicamente estável. *(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)* O recorte por ano só é critério
de Campanha quando o instrumento se aplica apenas àquelas formações; concentrar a
divulgação em uma coorte é foco de mobilização e não restringe quem responde.

**Independent Test**: avaliar Conclusões de 2019, 2020, 2024, 2025 e sem ano contra
Campanhas com limites 2020–2024, "a partir de 2020", "até 2024" e sem limites.

**Acceptance Scenarios**:

1. **Given** uma Campanha com ano mínimo 2020 e máximo 2024, **When** são avaliadas
   Conclusões de 2019, 2020, 2024 e 2025, **Then** 2020 e 2024 são ELEGÍVEIS e 2019 e 2025
   são NÃO ELEGÍVEIS pelo critério de ano de conclusão.
2. **Given** uma Campanha só com ano mínimo 2020, **When** são avaliadas Conclusões de
   2019 e 2031, **Then** 2019 é NÃO ELEGÍVEL e 2031 é ELEGÍVEL.
3. **Given** uma Campanha só com ano máximo 2024, **When** são avaliadas Conclusões de
   1998 e 2025, **Then** 1998 é ELEGÍVEL e 2025 é NÃO ELEGÍVEL.
4. **Given** uma Campanha com ano mínimo 2025 e máximo 2020, **When** os critérios são
   definidos, **Then** a definição é rejeitada e os critérios anteriores permanecem.
5. **Given** uma Campanha criada com anos 2020–2024, **When** ela é consultada anos depois,
   **Then** os limites continuam 2020–2024; nada no sistema os recalcula a partir da data
   corrente.

---

### User Story 5 - Determinar e explicar se uma Conclusão é elegível (Priority: P1)

Dada uma Campanha e uma Conclusão Acadêmica, o domínio responde de forma determinística
ELEGÍVEL ou NÃO ELEGÍVEL e, quando NÃO ELEGÍVEL, lista todos os critérios não atendidos e
o motivo de cada um. A avaliação é feita por Conclusão, nunca por Pessoa.

**Why this priority**: é o núcleo da feature e o contrato que a futura Participação
consumirá.

**Independent Test**: Pessoa A com Conclusão de ADS — Serra — 2021 e Especialização —
Cefor — 2026; Campanha 2020–2024; verificar a primeira ELEGÍVEL, a segunda NÃO ELEGÍVEL
pelo ano, e que repetir a avaliação dá sempre o mesmo resultado.

**Acceptance Scenarios**:

1. **Given** a Pessoa A com as duas Conclusões acima e uma Campanha de 2020 a 2024,
   **When** cada Conclusão é avaliada, **Then** ADS 2021 é ELEGÍVEL e Especialização 2026
   é NÃO ELEGÍVEL, com o critério de ano de conclusão e o motivo NÃO ATENDE.
2. **Given** uma Conclusão que não atende a dois critérios definidos, **When** é avaliada,
   **Then** o resultado lista os dois critérios, cada um com seu motivo.
3. **Given** os mesmos critérios e a mesma Conclusão, **When** a avaliação é repetida em
   momentos e estados diferentes da Campanha, **Then** o resultado é idêntico.
4. **Given** uma avaliação qualquer, **When** ela termina, **Then** nada foi persistido:
   nem resultado, nem trilha de auditoria, nem marcação na Conclusão ou na Pessoa.

---

### User Story 6 - Abrir a coleta e impedir abertura com Versão em RASCUNHO (Priority: P1)

A coleta começa por um ato explícito de abertura. A abertura exige Versão PUBLICADA,
período definido e válido, critérios válidos e data corrente dentro do período. Se
qualquer condição falhar, a abertura é rejeitada com todas as pendências e nada muda. A
abertura nunca publica a Versão.

**Why this priority**: impede que respostas futuras fiquem associadas a um instrumento
ainda mutável (Princípio VIII) e fixa o significado da rodada.

**Independent Test**: tentar abrir uma Campanha com a baseline da 003 (RASCUNHO) e
verificar rejeição; publicar outra Versão de teste, associá-la e abrir dentro do período.

**Acceptance Scenarios**:

1. **Given** uma Campanha EM PREPARAÇÃO com Versão em RASCUNHO e período válido que contém
   a data corrente, **When** a abertura é solicitada, **Then** ela é rejeitada com a
   pendência "Versão não publicada", a Campanha continua EM PREPARAÇÃO e a Versão continua
   em RASCUNHO.
2. **Given** uma Campanha EM PREPARAÇÃO com Versão PUBLICADA, período válido que contém a
   data corrente e critérios válidos, **When** a abertura é solicitada, **Then** a
   Campanha passa a EM COLETA e o momento da abertura é registrado.
3. **Given** uma Campanha com Versão em RASCUNHO, sem período e com data corrente
   qualquer, **When** a abertura é solicitada, **Then** a rejeição lista todas as
   pendências (Versão não publicada e período não definido), não apenas a primeira.
4. **Given** uma Campanha nunca aberta cujo período começa depois da data corrente, ou
   já terminou (e que, por isso, já é ENCERRADA — FR-038 b), **When** a abertura é
   solicitada, **Then** ela é rejeitada indicando que a data corrente está fora do
   período.
5. **Given** uma Campanha já aberta, EM COLETA ou ENCERRADA, **When** a abertura é
   solicitada, **Then** nada muda e o resultado informa o estado atual.

---

### User Story 7 - Aplicar recortes simples por unidade, nível, modalidade e forma de oferta (Priority: P2)

Quando a rodada tiver recorte institucional, a Campanha pode restringir a população a um
conjunto de unidades, de níveis, de modalidades e/ou de formas de oferta. Dentro de um
critério, basta coincidir com um dos valores; entre critérios, todos os definidos
precisam ser atendidos. Não existe outra composição.

**Why this priority**: recortes por unidade ou nível são plausíveis (inclusive por
aplicação das CSAEGs), mas não são o caso da experiência atual. Por isso vêm depois da
população ampla e do recorte temporal. *(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)* Só valem como abrangência do instrumento (por
exemplo, um questionário próprio da pós-graduação). A atuação da CSAEG por unidade é
escopo de governança (010), não critério de Campanha.

**Independent Test**: com a fonte simulada, avaliar Conclusões de Serra, Vitória e Cefor,
de níveis distintos, contra Campanhas restritas a uma unidade, a várias unidades e a um
nível, e verificar resultados e motivos.

**Acceptance Scenarios**:

1. **Given** uma Campanha sem critério de unidade, **When** são avaliadas Conclusões de
   várias unidades, **Then** todas atendem a esse critério (Campanha institucional).
2. **Given** uma Campanha restrita às unidades {Serra, Vitória}, **When** são avaliadas
   Conclusões de Serra, Vitória e Cefor, **Then** Serra e Vitória são ELEGÍVEIS e Cefor é
   NÃO ELEGÍVEL pelo critério de unidade.
3. **Given** uma Campanha restrita à unidade {Serra}, **When** uma Pessoa tem uma Conclusão
   em Serra e outra no Cefor, **Then** apenas a de Serra é ELEGÍVEL.
4. **Given** uma Campanha restrita a um nível e a um intervalo de anos, **When** uma
   Conclusão é do nível certo e de ano fora do intervalo, **Then** ela é NÃO ELEGÍVEL
   apenas pelo critério de ano.
5. **Given** uma Campanha restrita à unidade "Serra", **When** é avaliada uma Conclusão
   cuja unidade está registrada como "serra" ou "Campus Serra", **Then** ela é NÃO
   ELEGÍVEL por NÃO ATENDE; o sistema não normaliza nem deduz equivalências (001/DP-007).

---

### User Story 8 - Encerrar uma Campanha preservando seu significado histórico (Priority: P2)

A Campanha EM COLETA passa a ENCERRADA quando seu período termina ou por ato explícito de
encerramento antes disso. Encerrada, ela não admite novas Participações futuras, e todo
o seu contexto permanece consultável.

**Why this priority**: necessário para o contrato da 005 e para a leitura histórica das
rodadas; depende das histórias P1.

**Independent Test**: abrir uma Campanha, consultar o estado após o último dia do período
sem nenhuma ação e verificar ENCERRADA; em outra Campanha, encerrar explicitamente antes
do fim e verificar o momento registrado e o período planejado intacto.

**Acceptance Scenarios**:

1. **Given** uma Campanha EM COLETA com encerramento em 30/06/2027, **When** o estado é
   consultado com data corrente 01/07/2027, **Then** ela é ENCERRADA, sem que nenhuma
   ação ou processo agendado tenha sido executado.
2. **Given** uma Campanha EM COLETA, **When** o encerramento explícito é solicitado antes
   do fim do período, **Then** ela fica ENCERRADA, o momento do encerramento é registrado
   e o período planejado permanece o originalmente definido.
3. **Given** uma Campanha ENCERRADA, **When** são consultados Versão, Pesquisa, período,
   critérios, momento de abertura e momento e forma de encerramento, **Then** todos estão
   disponíveis exatamente como eram.
4. **Given** uma Campanha ENCERRADA, **When** se verifica se ela admite nova Participação
   para uma Conclusão ELEGÍVEL, **Then** a resposta é não.
5. **Given** uma Campanha nunca aberta, com período em curso, futuro ou já expirado,
   **When** o encerramento explícito é solicitado, **Then** ele é rejeitado sem gravar
   nada.
6. **Given** uma Campanha nunca aberta com período de 01/04/2027 a 30/06/2027, **When** o
   estado é consultado com data corrente 01/07/2027, **Then** ela é ENCERRADA, sem nenhuma
   ação ou escrita. Ela não admite Participação e não pode ser aberta com esse período,
   mas continua editável e removível.
7. **Given** a Campanha do cenário 6, **When** seu período é alterado para 01/06/2028 a
   30/06/2028 e o estado é consultado em 01/07/2027, **Then** ela é EM PREPARAÇÃO e
   continua nunca aberta.

---

### User Story 9 - Impedir alteração silenciosa de Campanha aberta (Priority: P2)

Depois da primeira abertura, não é possível alterar Versão, período, critérios ou nome,
nem remover a Campanha, esteja ela EM COLETA ou ENCERRADA. Mudança de intenção
institucional exige nova Campanha. Campanha nunca aberta continua editável e removível,
qualquer que seja seu estado temporal.

**Why this priority**: protege o significado histórico das Participações e análises
futuras (Princípio VIII) com a menor regra possível: imutabilidade, sem histórico nem
versionamento de Campanha.

**Independent Test**: abrir uma Campanha e tentar cada alteração e a remoção, em EM
COLETA e em ENCERRADA após abertura, verificando rejeição integral e Campanha idêntica à
anterior; numa Campanha nunca aberta e expirada, verificar que as mesmas operações são
aceitas.

**Acceptance Scenarios**:

1. **Given** uma Campanha EM COLETA, **When** se tenta trocar a Versão, alterar o período,
   alterar qualquer critério ou alterar o nome, **Then** cada tentativa é rejeitada e a
   Campanha permanece idêntica.
2. **Given** uma Campanha ENCERRADA após abertura (explicitamente ou pelo fim do
   período), **When** as mesmas tentativas são feitas, **Then** o resultado é o mesmo.
3. **Given** uma Campanha já aberta, EM COLETA ou ENCERRADA após abertura, **When** se
   tenta removê-la, **Then** a remoção é rejeitada.
4. **Given** uma Campanha EM PREPARAÇÃO, **When** ela é removida, **Then** a remoção é
   aceita e a Versão associada não é afetada.
5. **Given** uma alteração rejeitada que combinava uma mudança válida e uma inválida,
   **When** a Campanha é consultada, **Then** nenhuma das mudanças foi aplicada.
6. **Given** uma Campanha nunca aberta cujo período já expirou (ENCERRADA pelo tempo),
   **When** seu nome, Versão, período ou critérios são alterados, ou ela é removida,
   **Then** cada operação é aceita, porque não há significado histórico a preservar.

---

### User Story 10 - Acompanhar a mesma Conclusão em várias Campanhas, sem convite (Priority: P2)

A mesma Conclusão Acadêmica pode ser elegível em Campanhas de momentos distintos (por
exemplo, 2025, 2027 e 2030) e, eventualmente, em Campanhas simultâneas. Para qualquer
Conclusão, é possível saber em quais Campanhas EM COLETA ela é elegível, sem depender de
convite, lista ou comunicação prévia.

**Why this priority**: é o que torna o acompanhamento longitudinal possível (Princípio I)
e o que permitirá, no futuro, uma URL institucional permanente resolver a Campanha
aplicável.

**Independent Test**: criar três Campanhas com populações que incluem a mesma Conclusão
de ADS — 2024, em períodos distintos, e verificar elegibilidade nas três; abrir duas
Campanhas sobrepostas e verificar que a consulta por Conclusão devolve ambas, sem
prioridade.

**Acceptance Scenarios**:

1. **Given** Campanhas 2025, 2027 e 2030 cujos critérios incluem a Conclusão ADS — 2024,
   **When** a Conclusão é avaliada em cada uma, **Then** é ELEGÍVEL nas três, e nenhuma
   avaliação afeta as demais.
2. **Given** duas Campanhas EM COLETA cujas populações incluem a mesma Conclusão, **When**
   se consultam as Campanhas EM COLETA em que ela é elegível, **Then** ambas são
   devolvidas, sem indicação de preferência.
3. **Given** uma Conclusão para a qual nenhuma Campanha EM COLETA é aplicável, **When** a
   mesma consulta é feita, **Then** o resultado é vazio, sem erro.
4. **Given** qualquer Campanha EM COLETA e qualquer Conclusão ELEGÍVEL, **When** se
   verifica se ela admite nova Participação, **Then** a resposta é sim, sem que exista ou
   seja consultado qualquer convite, destinatário ou envio.

---

### User Story 11 - Tratar dados acadêmicos ausentes e configurações inválidas (Priority: P3)

Quando um critério definido depende de um atributo que a fonte não informou, a Conclusão
é NÃO ELEGÍVEL com o motivo NÃO INFORMADO, distinto de NÃO ATENDE. Configurações de
critérios ou de período inválidas são rejeitadas com todas as pendências e sem alteração
parcial.

**Why this priority**: os comportamentos já decorrem das regras P1 e P2; esta história
torna explícitos os casos de borda.

**Independent Test**: avaliar Conclusões sem unidade, sem nível e sem ano contra
Campanhas que filtram e que não filtram esses atributos; submeter configurações
inválidas.

**Acceptance Scenarios**:

1. **Given** uma Campanha restrita ao nível {Graduação} e uma Conclusão com nível não
   informado, **When** ela é avaliada, **Then** é NÃO ELEGÍVEL com critério nível e motivo
   NÃO INFORMADO.
2. **Given** uma Campanha sem critério de nível e a mesma Conclusão, **When** ela é
   avaliada, **Then** a ausência do nível não tem efeito.
3. **Given** uma Campanha com ano mínimo 2020 e uma Conclusão sem ano informado, **When**
   ela é avaliada, **Then** é NÃO ELEGÍVEL por NÃO INFORMADO; o ano não é deduzido do
   curso, de outra Conclusão da mesma Pessoa nem de qualquer outro dado.
4. **Given** uma definição de critérios com conjunto de unidades vazio, valor em branco,
   ano não inteiro ou mínimo maior que máximo, **When** ela é submetida, **Then** é
   rejeitada listando todos os problemas, e os critérios anteriores permanecem.

---

### Cobertura dos casos importantes

| Caso | Descrição | Coberto por |
|------|-----------|-------------|
| A | Campanha para todos os egressos | US3; FR-019 |
| B | Conclusões entre dois anos | US4.1; FR-021 |
| C | Campanha institucional com várias unidades | US7.1, US7.2; FR-019, FR-020 |
| D | Campanha restrita a uma unidade | US7.3; FR-020 |
| E | Campanha restrita a determinado nível | US7.4, US11.1 |
| F | Pessoa com duas Conclusões, apenas uma elegível | US5.1, US7.3; FR-016, FR-029 |
| G | Atributo ausente necessário ao critério | US11.1–US11.3; FR-028 |
| H | Abrir com Versão RASCUNHO | US6.1, US6.3; FR-036 |
| I | Período inválido | US2.3; FR-012 |
| J | Alterar significado de Campanha aberta | US9; FR-043, FR-044 |
| K | Duas Campanhas em momentos distintos, mesma Conclusão | US10.1; FR-050 |
| L | Acesso não depende de convite | US10.4; FR-048, FR-053 |

### Edge Cases

- **Mesma data de início e encerramento**: válido; a coleta dura um dia (US2.2).
- **Abertura no último dia do período**: permitida; no dia seguinte a Campanha está
  ENCERRADA (FR-036 d, FR-038 b).
- **Abertura antes do início do período**: rejeitada; não existe estado "agendada"
  (FR-036 d). A abertura depois do início, ainda dentro do período, é permitida, e o
  momento real fica registrado ao lado do período planejado (FR-036, FR-045).
- **Campanha nunca aberta cujo período já terminou**: é ENCERRADA pela precedência
  temporal (FR-038 b). Não admite Participação, não pode ser aberta com esse período e o
  encerramento explícito é rejeitado. Continua editável e removível, porque nunca entrou
  em coleta. Corrigido o período para uma janela futura, volta a EM PREPARAÇÃO; isso não
  é reabertura (FR-039).
- **Campanha sem período definido**: nunca expira; permanece EM PREPARAÇÃO até ter
  período e ser aberta.
- **Versão em RASCUNHO publicada depois da associação**: a abertura passa a ser possível,
  pois a condição é verificada no momento da abertura.
- **Mesma Versão em várias Campanhas, inclusive simultâneas**: permitido (FR-004).
- **Campanha cujo valor de critério não corresponde a nenhuma Conclusão existente** (por
  exemplo, unidade digitada de forma diferente da fonte): a configuração é válida e a
  população conhecida pode ser zero. O sistema não corrige nem sugere equivalências; a
  contagem (FR-031) é o instrumento de diagnóstico.
- **Abertura com população conhecida igual a zero**: permitida. Os dados acadêmicos podem
  chegar depois, e proibir seria regra institucional não fundamentada.
- **Conclusão incorporada depois da abertura**: se satisfaz os critérios, pertence à
  população da Campanha (FR-032). A Campanha preserva a definição, não um rol.
- **Conclusão concluída depois do período**, numa Campanha sem ano máximo: é ELEGÍVEL pela
  definição, mas não admite Participação numa Campanha ENCERRADA (FR-053).
- **Duas Campanhas EM COLETA com populações sobrepostas**: permitido. O sistema devolve
  ambas e não escolhe (FR-051, DP-404).
- **Encerramento explícito de Campanha aberta e já ENCERRADA por data**: nada muda; o
  resultado informa que ela já está encerrada. Se a Campanha nunca foi aberta, o pedido é
  rejeitado sem gravar nada, mesmo que ela já seja ENCERRADA pelo tempo (FR-040).
- **Abertura repetida**: nada muda; o resultado informa o estado atual (FR-037).
- **Conjunto de critério com valores repetidos**: tratado como conjunto; a repetição não
  altera o resultado nem é preservada como valor distinto.
- **Pessoa com várias Conclusões elegíveis na mesma Campanha**: cada Conclusão é avaliada
  e contada separadamente (FR-029, FR-033). Como a Participação futura se organiza nesse
  caso pertence à 005.

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII): **[PAEG]** com artigo; **[Const. — n]** quando o
requisito decorre diretamente da Constituição; **[Arquitetura]** decisão de modelagem;
**[Hipótese]** escolha reversível de produto; **[Escopo]** delimitação desta feature.
Nenhum requisito é **[Herdado]** do formulário: o instrumento atual não tem conceito de
Campanha; a experiência do Ifes (período de coleta e acesso espontâneo) é usada como caso
a ser representável, não como regra.

### Functional Requirements

**Campanha e distinção de conceitos**

- **FR-001**: O sistema DEVE representar a Campanha como entidade própria, com identidade
  estável e distinta de Pesquisa e de Versão. [Const. — VII, Terminologia]
- **FR-002**: A Campanha DEVE ter: (a) **nome** — obrigatório e não vazio, sem exigência
  de unicidade; (b) exatamente uma **Versão**; (c) **período de coleta** (FR-011);
  (d) **critérios de população** (FR-018); (e) **estado observável** (FR-034); (f)
  **momento da abertura**, quando aberta; (g) **momento e forma do encerramento**, quando
  encerrada. Nenhum outro atributo é exigido nesta feature. [Arquitetura; Const. — XXII]
- **FR-003**: A Pesquisa da Campanha DEVE ser a Pesquisa da Versão referenciada. Ela NÃO
  DEVE ser registrada de forma independente que possa divergir da Versão. [Arquitetura]
- **FR-004**: A mesma Versão PODE ser usada por várias Campanhas, inclusive simultâneas, e
  a mesma Pesquisa PODE ter Campanhas em períodos diferentes. [Const. — VII]
- **FR-005**: O sistema NÃO DEVE representar periodicidade, recorrência, duração padrão,
  calendário de rodadas, "próxima Campanha" ou série de Campanhas. Cada Campanha é uma
  rodada concreta, definida por quem a prepara. [PAEG Art. 10, II; Const. — IX, X]
- **FR-006**: Associar, trocar ou usar uma Versão numa Campanha NÃO DEVE alterar a Versão
  nem a Pesquisa, NÃO DEVE marcar a Versão como "vigente" e NÃO DEVE alterar nenhuma regra
  da 002. [Const. — VII; 002 FR-008]

**Versão aplicada**

- **FR-007**: A criação de Campanha DEVE exigir uma Versão existente, em qualquer estado.
  Não existe Campanha sem Versão. [Arquitetura]
- **FR-008**: Enquanto a Campanha nunca tiver sido aberta (FR-043), sua Versão PODE ser
  trocada por qualquer outra Versão existente, inclusive de outra Pesquisa.
  [Arquitetura]
- **FR-009**: A abertura DEVE exigir Versão PUBLICADA (FR-036 a). A Campanha NÃO DEVE
  publicar a Versão, nem implicitamente nem como efeito da abertura; a competência para
  publicar continua pendente (002/DP-001). [Const. — VIII, X]
- **FR-010**: Toda Campanha já aberta (EM COLETA ou ENCERRADA após abertura) DEVE
  referenciar uma Versão PUBLICADA. Isso decorre de FR-009, de FR-043 e da
  irreversibilidade da publicação (002 FR-013). Campanha nunca aberta, inclusive a
  ENCERRADA pelo tempo, pode referenciar Versão em RASCUNHO.
  [Const. — VIII]

**Período de coleta**

- **FR-011**: O período de coleta DEVE ser composto por **data de início** e **data de
  encerramento**, datas civis, ambas incluídas. [Arquitetura]
- **FR-012**: Um período DEVE ter as duas datas, com início anterior ou igual ao
  encerramento. Período com data ausente ou com início posterior ao encerramento DEVE ser
  rejeitado, informando o problema, sem alterar o período anterior. [Arquitetura]
- **FR-013**: Enquanto a Campanha nunca tiver sido aberta (FR-043), o período PODE estar
  indefinido e PODE ser redefinido, inclusive depois de expirado. A abertura exige
  período definido (FR-036 b). [Arquitetura]
- **FR-014**: O sistema NÃO DEVE atribuir período ou duração padrão, NÃO DEVE presumir
  Campanha anual e NÃO DEVE limitar a duração do período. [PAEG Art. 10, II;
  Const. — IX]

**Critérios de população**

- **FR-015**: A população da Campanha DEVE ser definida por critérios, não por lista de
  Pessoas, de Conclusões ou de destinatários. [Const. — XXII; Escopo]
- **FR-016**: A unidade de elegibilidade DEVE ser a **Conclusão Acadêmica**. NÃO DEVE
  existir elegibilidade atribuída à Pessoa. [Const. — I, XI]
- **FR-017**: O universo avaliável DEVE ser o das Conclusões Acadêmicas existentes no
  NIAE, que, pela 001, são apenas formações reconhecidas como concluídas (001 FR-018,
  FR-019). Nenhum critério DEVE poder incluir quem não tem Conclusão Acadêmica.
  [PAEG Art. 3º; Const. — II]
- **FR-018**: Os critérios de população DEVEM ser exatamente estes, todos opcionais:
  (a) **ano de conclusão mínimo**; (b) **ano de conclusão máximo**; (c) **unidades**;
  (d) **níveis**; (e) **modalidades**; (f) **formas de oferta**. Os itens (c) a (f) são
  conjuntos de valores. Nenhum outro critério DEVE existir nesta feature. [Arquitetura;
  Const. — XXII] *(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)* Os critérios DEVEM ser usados só para expressar a abrangência do
  instrumento e NÃO DEVEM ser apresentados nem documentados como mecanismo de segmentação
  da divulgação.
- **FR-019**: Critério ausente NÃO DEVE restringir a população. Campanha sem nenhum
  critério definido DEVE ser válida e abranger todas as Conclusões Acadêmicas existentes
  no NIAE (**população ampla**), e DEVE ser descrita como tal. [Const. — XXII; Escopo]
- **FR-020**: A semântica de composição DEVE ser fixa: uma Conclusão satisfaz os critérios
  se, e somente se, satisfaz **todos** os critérios definidos; um critério de conjunto é
  satisfeito quando o valor da Conclusão é **igual a um** dos valores do conjunto. NÃO
  DEVEM existir alternância entre critérios, negação, exclusão de valores, grupos
  aninhados, expressões ou regras sobre outros atributos. [Const. — XXII, XXIII]
- **FR-021**: Os critérios de ano DEVEM usar o ano de conclusão da Conclusão Acadêmica e
  ser inclusivos: mínimo ≤ ano, ano ≤ máximo. Os anos DEVEM ser absolutos. NÃO DEVEM ser
  armazenados recortes relativos à data corrente (por exemplo, "últimos 5 anos"); recortes
  desejados pela instituição são convertidos em anos concretos ao configurar a Campanha.
  [Const. — VIII, IX]
- **FR-022**: Os valores de unidade, nível, modalidade e forma de oferta DEVEM ser
  comparados por igualdade exata com o valor registrado na Conclusão, sem normalização de
  caixa ou espaços, sinônimos, abreviações ou dedução. O vocabulário canônico permanece
  pendente (001/DP-007). [Const. — III, XXIX]
- **FR-023**: Uma definição de critérios DEVE ser rejeitada integralmente, informando
  **todos** os problemas, quando: (a) um ano não for inteiro positivo; (b) mínimo e máximo
  estiverem definidos e o mínimo for maior que o máximo; (c) um critério de conjunto
  estiver definido com conjunto vazio; (d) algum valor de conjunto for vazio ou em branco.
  Conjunto vazio é rejeitado para não ser confundido com critério ausente. [Arquitetura]
- **FR-024**: Os critérios PODEM ser definidos e redefinidos somente enquanto a Campanha
  nunca tiver sido aberta (FR-043). Critério ausente e conjunto vazio NÃO DEVEM ser
  representados pelo mesmo estado gravado: ausente não restringe; vazio é inválido e nunca
  é gravado (FR-023 c). [Const. — VIII; Arquitetura]

**Avaliação de elegibilidade**

- **FR-025**: Dada uma Campanha e uma Conclusão Acadêmica, o sistema DEVE responder
  **ELEGÍVEL** ou **NÃO ELEGÍVEL**. O resultado DEVE depender apenas dos critérios da
  Campanha e dos atributos da Conclusão, e NÃO DEVE depender do estado da Campanha, da data
  corrente, de outras Conclusões da mesma Pessoa, de outras Campanhas, de Participações ou
  de convites. Para as mesmas entradas, o resultado DEVE ser sempre o mesmo.
  [Const. — I, XXVI]
- **FR-026**: O resultado NÃO ELEGÍVEL DEVE listar **todos** os critérios não atendidos,
  cada um com: (a) o critério (ano de conclusão, unidade, nível, modalidade ou forma de
  oferta); (b) o motivo — **NÃO ATENDE** (o atributo está informado e fica fora do
  critério) ou **NÃO INFORMADO** (o atributo não foi informado pela fonte). O resultado
  ELEGÍVEL não tem pendências. [Escopo]
- **FR-027**: Para fins de explicação, os critérios de ano mínimo e ano máximo DEVEM ser
  tratados como um único critério, **ano de conclusão**. [Arquitetura]
- **FR-028**: Quando um critério definido depende de atributo não informado na Conclusão,
  o critério NÃO DEVE ser considerado satisfeito, e o motivo DEVE ser NÃO INFORMADO. O
  valor NÃO DEVE ser inferido do nome do curso, de outra Conclusão da mesma Pessoa, de
  outro atributo ou de qualquer padrão. Quando o critério não está definido, a ausência do
  atributo NÃO DEVE ter efeito. [Const. — II, III, XXIX; 001 FR-010]
- **FR-029**: As Conclusões de uma mesma Pessoa DEVEM ser avaliadas independentemente. A
  elegibilidade de uma NÃO DEVE se estender a outra. [Const. — I, XI]
- **FR-030**: A avaliação NÃO DEVE persistir resultado, marcação, trilha de auditoria ou
  qualquer outro registro. [Const. — IV, XXII]

**População conhecida**

- **FR-031**: Para qualquer Campanha, em qualquer estado, o sistema DEVE permitir
  enumerar e contar as Conclusões Acadêmicas ELEGÍVEIS a partir dos dados existentes no
  momento da consulta. O resultado DEVE ser identificado como população **no momento da
  consulta** e NÃO DEVE ser apresentado como denominador histórico oficial (DP-408).
  [Const. — XIX]
- **FR-032**: A população é **definida pelos critérios** e avaliada no momento da consulta.
  Conclusões incorporadas depois da criação ou da abertura que satisfaçam os critérios
  DEVEM pertencer à população. Se dados acadêmicos forem corrigidos no futuro
  (001/DP-005), o resultado da avaliação PODE mudar. O sistema NÃO DEVE congelar a
  população na abertura, materializar lista de Conclusões elegíveis, criar membros,
  destinatários ou público da Campanha, nem guardar a contagem na Campanha (DP-408).
  [Arquitetura; Const. — XXII]
- **FR-033**: A contagem DEVE ser de Conclusões Acadêmicas, não de Pessoas. [Const. — I]

**Estados e ciclo de vida**

- **FR-034**: A Campanha DEVE ter exatamente três estados observáveis: **EM PREPARAÇÃO**,
  **EM COLETA** e **ENCERRADA**. NÃO DEVEM existir estados de aprovação, homologação,
  agendamento, suspensão, cancelamento, arquivamento ou reabertura. [Const. — X, XXII]
- **FR-035**: Toda Campanha DEVE nascer EM PREPARAÇÃO. [Arquitetura]
- **FR-036**: A **abertura** DEVE levar a Campanha de EM PREPARAÇÃO para EM COLETA e
  registrar o momento da abertura, somente se: (a) a Versão está PUBLICADA; (b) o período
  está definido e é válido; (c) os critérios são válidos (FR-023); (d) a data corrente está
  dentro do período, entre o início e o encerramento, inclusive. Se qualquer condição
  falhar, a abertura DEVE ser rejeitada, informando **todas** as condições não
  satisfeitas, e a Campanha DEVE permanecer inalterada. [Const. — VIII; Arquitetura]
- **FR-037**: A abertura de Campanha já aberta (EM COLETA ou ENCERRADA depois de aberta)
  NÃO DEVE alterar nada e DEVE informar o estado atual. A abertura de Campanha nunca
  aberta cujo período já terminou DEVE ser rejeitada pela condição FR-036 d.
  [Arquitetura]
- **FR-038**: Uma Campanha DEVE ser ENCERRADA: (a) por **encerramento explícito**, a
  partir de EM COLETA, que registra o momento do encerramento; ou (b) quando a data
  corrente for posterior à data de encerramento do período, **tenha ela sido aberta ou
  não**. Nesse caso, o encerramento ocorre ao fim do último dia do período. Ele é
  **estado efetivo derivado** da data de referência e do período, sem processo,
  agendamento ou ação que altere registros. A precedência é: encerramento explícito; fim
  do período; abertura; preparação. A forma do encerramento (explícito ou por fim do
  período) e se houve abertura DEVEM ser identificáveis. [Arquitetura; Escopo]
- **FR-039**: Para Campanha já aberta, ENCERRADA DEVE ser estado final, sem transição de
  saída (sem reabertura — DP-405). Para Campanha nunca aberta, o estado continua derivado
  do período, que ainda pode ser corrigido (FR-043). Corrigir o período de Campanha nunca
  aberta e expirada NÃO é reabertura. [Const. — VIII; DP-405]
- **FR-040**: O encerramento explícito de Campanha nunca aberta DEVE ser rejeitado sem
  gravar nada, qualquer que seja seu estado temporal. O de Campanha aberta e já ENCERRADA
  NÃO DEVE alterar nada e DEVE informar que ela já está encerrada. Uma Campanha nunca
  aberta que passou do fim NÃO DEVE receber registro de encerramento: sua condição de
  ENCERRADA é só derivada do tempo. [Arquitetura]
- **FR-041**: Uma Campanha EM COLETA DEVE ter sempre a data corrente dentro do seu período
  de coleta. Esse invariante decorre de FR-036 d e FR-038 b. [Arquitetura]
- **FR-042**: A abertura DEVE ser sempre um ato explícito. NÃO DEVEM existir abertura
  automática, agendador, job, fila ou notificação nesta feature. [Escopo; Const. — XXII]

**Preservação histórica**

- **FR-043**: A fronteira histórica é a **primeira abertura**, não o estado temporal. A
  partir dela, NÃO DEVEM ser alterados nome, Versão, período ou critérios da Campanha.
  Toda tentativa, em EM COLETA ou ENCERRADA, DEVE ser rejeitada integralmente, sem
  alteração parcial. O encerramento antecipado é a única mudança de ciclo de vida admitida
  depois da abertura. Campanha nunca aberta PODE ter nome, Versão, período e critérios
  corrigidos, mesmo que seu período já tenha expirado. [Const. — VIII]
- **FR-044**: Campanha já aberta, EM COLETA ou ENCERRADA, NÃO DEVE ser removida por
  nenhum meio do domínio. Campanha nunca aberta PODE ser removida, qualquer que seja seu
  estado temporal, sem efeito sobre Versão, Pesquisa ou Conclusões.
  [Const. — VIII; Arquitetura]
- **FR-045**: De toda Campanha aberta DEVEM permanecer consultáveis: Versão e Pesquisa,
  período planejado, critérios, momento da abertura e, se encerrada, momento e forma do
  encerramento. [Const. — VIII]
- **FR-046**: O sistema NÃO DEVE versionar a Campanha nem registrar histórico de alterações
  feitas durante a preparação. [Const. — XXII]
- **FR-047**: Mudança de Versão, período, população ou nome depois da abertura DEVE ser
  feita por nova Campanha, com identidade própria. NÃO DEVE haver reinterpretação de
  Campanha existente. [Const. — VIII]

**Independência de convite**

- **FR-048**: A admissão futura de Participação NÃO DEVE depender de convite, envio,
  destinatário ou comunicação prévia. A Campanha NÃO DEVE ter rol de destinatários.
  [Const. — VI, XIV; Escopo]
- **FR-049**: Esta feature NÃO DEVE criar Convite, Mailing, Destinatário, Disparo, envio de
  e-mail ou WhatsApp, Notificação, CRM ou rastreamento de campanha de marketing.
  [Const. — VI, XXII]

**Múltiplas Campanhas e longitudinalidade**

- **FR-050**: O sistema DEVE permitir várias Campanhas ao longo do tempo. A mesma
  Conclusão Acadêmica DEVE poder ser elegível em Campanhas diferentes. Elegibilidade numa
  Campanha NÃO DEVE consumir, excluir ou condicionar elegibilidade em outra. [Const. — I]
- **FR-051**: Duas ou mais Campanhas EM COLETA PODEM coexistir, inclusive com populações
  sobrepostas. O sistema NÃO DEVE proibir essa coexistência, nem estabelecer prioridade ou
  escolher automaticamente entre elas (DP-404). [Const. — XXIX]
- **FR-052**: Para qualquer Conclusão Acadêmica, o sistema DEVE permitir consultar as
  Campanhas EM COLETA nas quais ela é ELEGÍVEL (zero, uma ou várias). A ordem do resultado
  DEVE ser determinística e NÃO DEVE significar preferência. [Const. — I, XIV]

**Contrato para a futura Participação**

- **FR-053**: Uma Campanha DEVE ser considerada apta a admitir nova Participação de uma
  Conclusão somente se estiver EM COLETA **e** a Conclusão for ELEGÍVEL. Campanha EM
  PREPARAÇÃO ou ENCERRADA NÃO DEVE admitir nova Participação. Condições adicionais (por
  exemplo, uma ou várias Participações por Conclusão na mesma Campanha) pertencem à 005.
  [Const. — I, VII] *(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)* ELEGÍVEL aqui é compatibilidade da formação com a abrangência da
  Campanha; uma resposta espontânea fora do foco de mobilização é admitida.
- **FR-054**: Nada nesta feature DEVE impedir a relação futura: Campanha 1 — 0..N
  Participações; cada Participação com exatamente uma Campanha e exatamente uma Conclusão
  Acadêmica. [Const. — I, VII]
- **FR-055**: Esta feature NÃO DEVE criar Participação, Resposta ou campos, contadores e
  marcadores provisórios relacionados a elas. [Const. — XXII; Escopo]

**Governança e rejeições**

- **FR-056**: Criar, alterar, abrir, encerrar e remover Campanha são capacidades do
  domínio. Elas NÃO DEVEM ser expostas a usuários com base apenas em acesso técnico, nem
  atribuídas a qualquer perfil, enquanto DP-402 estiver aberta. NÃO DEVE ser criado
  workflow de aprovação. [Const. — X; Governança de Permissões]
  *(Revisado pela 017 — interpretação C1 restrita à demonstração; DP-402 aberta)* A 017 permite gestão mínima pela CPAEG ativa somente na demonstração, sem publicação, critérios ou remoção; a competência produtiva continua pendente.
- **FR-057**: Toda rejeição DEVE ser explícita, identificar o motivo e não produzir
  alteração parcial. [Const. — XXVI]

### Key Entities *(include if feature involves data)*

- **Campanha** *(nova)*: rodada institucional de aplicação de uma Versão. Atributos: nome;
  Versão (exatamente uma); período de coleta (início, encerramento); critérios de
  população; estado observável; momento da abertura; momento e forma do encerramento. Não
  contém dado pessoal nem dado sobre egressos: é configuração institucional.
- **Critérios de população** *(parte da Campanha, não entidade independente)*: seis campos
  opcionais com semântica fixa (FR-018 a FR-023): ano mínimo, ano máximo, unidades,
  níveis, modalidades, formas de oferta.
- **Resultado de elegibilidade** *(valor calculado, não persistido)*: ELEGÍVEL ou NÃO
  ELEGÍVEL, com a lista de pendências (critério e motivo NÃO ATENDE ou NÃO INFORMADO).
  É dado **derivado** (Princípio III).
- **Versão da Pesquisa** e **Pesquisa** *(002, inalteradas)*: a Campanha referencia a
  Versão; a Pesquisa decorre dela.
- **Conclusão Acadêmica** *(001, inalterada)*: unidade de elegibilidade; fornece ano de
  conclusão, unidade, nível, modalidade e forma de oferta, cada um possivelmente não
  informado.
- **Pessoa** *(001, inalterada)*: não participa da avaliação; agrupa Conclusões avaliadas
  independentemente.

Entidades deliberadamente **não** criadas: Segmento, Público/Audience, Grupo de Filtros,
Regra, Expressão, Membro de Campanha, Destinatário, Convite, Agendamento, Workflow,
Versão de Campanha, Participação, Resposta.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| Nome, Versão, período, critérios da Campanha | Configuração institucional (não é dado sobre o egresso) | Definidos por quem prepara a Campanha (competência: DP-402) | Não se aplica; fixados na abertura (FR-043) |
| Momento da abertura e do encerramento explícito | Registro do sistema | Momento da operação | Não se aplica |
| Encerramento por fim do período | Derivado | Data de encerramento do período e data corrente (FR-038 b) | Não se aplica |
| Ano de conclusão, unidade, nível, modalidade, forma de oferta | Institucional | Conclusão Acadêmica (001), obtida da fonte acadêmica | Lido como está; ausência é NÃO INFORMADO, nunca inferida (FR-028); correção é 001/DP-005 |
| Resultado de elegibilidade e pendências | Derivado | Critérios × atributos da Conclusão (FR-020 a FR-028) | Não persistido (FR-030) |
| População conhecida e contagem | Derivado | Conclusões existentes que satisfazem os critérios (FR-031) | Não persistida; pode variar com novas incorporações (FR-032, DP-408) |

Nenhum dado declarado é lido ou produzido.

### Modelo conceitual

```text
Pesquisa 1 ── 0..N Versão 1 ── 0..N Campanha
                                      │ nome
                                      │ período: início, encerramento (opcional em preparação)
                                      │ critérios (todos opcionais):
                                      │   ano mínimo, ano máximo,
                                      │   {unidades}, {níveis}, {modalidades}, {formas de oferta}
                                      │ estado: EM PREPARAÇÃO | EM COLETA | ENCERRADA
                                      │ aberta em; encerrada em / forma
                                      │
                                      ┆ elegibilidade(Campanha, Conclusão) → ELEGÍVEL | NÃO ELEGÍVEL + pendências
                                      ┆ (calculada, não persistida)
                                      ▼
Pessoa 1 ── 0..N Conclusão Acadêmica

Ciclo de vida:

                abrir (Versão PUBLICADA, período válido,
                       critérios válidos, data corrente ∈ período)
EM PREPARAÇÃO ─────────────────────────────────────────────► EM COLETA
   │  ▲  │                                                       │
   │  │  │ data corrente > encerramento                          │ encerrar explicitamente
   │  │  ▼ (nunca aberta)                                        │ ou data corrente > encerramento
   │  │ ENCERRADA sem abertura ── corrigir período ─► (volta a   ▼
   │  │ (editável, removível)     para janela futura  EM PREP.)  ENCERRADA após abertura
   │  └── editar nome, Versão, período, critérios                (final, imutável)
   └── remover

Precedência do estado: encerramento explícito → fim do período → abertura → preparação.
Estado temporal controla a coleta; a primeira abertura (aberta_em) controla a imutabilidade.

Contrato com a 005:
  admite nova Participação(Campanha, Conclusão) ⇐ estado = EM COLETA ∧ elegibilidade = ELEGÍVEL
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Os 12 casos importantes (A a L) são demonstrados por testes automatizados
  com a fonte simulada, com 100% de resultados conforme a spec.
- **SC-002**: Para um conjunto de referência de Conclusões e Campanhas, cada avaliação de
  elegibilidade repetida produz resultado idêntico em 100% das repetições, independentemente
  do estado da Campanha e da data corrente.
- **SC-003**: Todo resultado NÃO ELEGÍVEL do conjunto de referência identifica 100% dos
  critérios não atendidos e distingue NÃO ATENDE de NÃO INFORMADO, sem nenhum caso em que
  um atributo não informado satisfaça um critério.
- **SC-004**: Uma Campanha de população ampla é configurada informando apenas nome e
  Versão (e período, para abrir), sem nenhum critério, e sua contagem é igual ao total de
  Conclusões existentes.
- **SC-005**: 100% das tentativas de alterar nome, Versão, período ou critérios, ou de
  remover Campanha já aberta (EM COLETA ou ENCERRADA após abertura), são rejeitadas sem
  alteração parcial. 100% das mesmas operações em Campanha nunca aberta, inclusive
  expirada, são aceitas.
- **SC-006**: 100% das tentativas de abrir Campanha com Versão em RASCUNHO são rejeitadas,
  e nenhuma Versão muda de estado por efeito de operação de Campanha.
- **SC-007**: A contagem da população conhecida coincide exatamente com a contagem
  esperada calculada manualmente sobre os cenários da fonte simulada, para cada Campanha
  de referência.
- **SC-008**: Uma Campanha configurada com anos absolutos mantém a mesma definição de
  população quando consultada com qualquer data corrente posterior.
- **SC-009**: Após a feature, não existe nenhuma entidade, campo ou registro de
  Participação, Resposta, Convite, Destinatário, Segmento, Regra ou Agendamento, e nenhum
  dado das Features 001, 002 e 003 é alterado.

## Assumptions

- **Timezone de referência**: as datas do período e a data corrente são interpretadas na
  timezone configurada do projeto. A feature não fixa um fuso nominal. O plan define como
  a data corrente é obtida e substituída em testes.
- **Granularidade diária**: o período usa datas civis, sem hora. Se a instituição precisar
  de horários de abertura ou encerramento, isso será tratado por spec futura. [Hipótese]
- **Ano como única referência temporal de critério**: a 001 garante ano sempre que há data
  completa (001 FR-011). Recorte por data completa (por exemplo, semestre) não tem
  consumidor e fica fora do escopo. [Hipótese]
- **Atributos da Conclusão hoje estáveis**: pela 001, a incorporação nunca altera
  Conclusões existentes, então a elegibilidade de uma Conclusão numa Campanha hoje não
  muda. Se uma política de correção for adotada (001/DP-005), o resultado poderá mudar.
  Isso é aceito pela interpretação dinâmica da população (Clarifications).
- **Valores de critério escritos como na fonte**: até existir vocabulário canônico
  (001/DP-007), quem configura a Campanha precisa usar os valores tais como registrados
  nas Conclusões. A contagem da população é o meio de verificar a configuração.
- **Remoção em preparação**: remover Campanha nunca aberta não tem impacto histórico, e
  evita estados "cancelada" ou "arquivada". [Arquitetura]
- **Encerramento antecipado explícito**: é permitido porque não altera Versão, período
  planejado nem população, apenas registra o fim efetivo. Prorrogação e reabertura não são
  permitidas (DP-405). Confirmado em Clarifications.
- **Consultas sem interface**: avaliação, contagem e consulta por Conclusão são
  capacidades do domínio, verificadas por testes, sem tela, relatório ou exportação.
- **Conclusões "existentes no NIAE"**: população ampla significa todas as Conclusões
  incorporadas pela fronteira acadêmica da 001. A fonte oficial continua 001/DP-001.

## Relação com outras features

**001** — consumida sem alteração: Conclusão Acadêmica como unidade de elegibilidade e
seus atributos opcionais (001 FR-009 a FR-011). A garantia de que só formações
reconhecidas viram Conclusão (001 FR-018 a FR-020) assegura que a população é composta
por egressos (PAEG Art. 3º). Esta feature não cria regra acadêmica de conclusão.

**002** — consumida sem alteração: a Campanha é o lugar da escolha da Versão aplicada
(002 FR-008). A publicação continua capacidade da 002, e sua competência continua
pendente (002/DP-001).

**003** — não alterada. A baseline migrada está em RASCUNHO e, portanto, **não pode ser
usada para abrir Campanha** até ser publicada por decisão institucional (002/DP-001,
003/DP-301). A 003 se referia a "Feature 004 (jornada de resposta)". Com a reorganização
do roteiro, os itens que a 003 encaminhava à jornada (semântica de execução das regras,
DP-302, Q1/consentimento, Q6, Q47/Q48) passam à feature que criar Participação e
Respostas (prevista como 005). Esta spec não os resolve.

**005 (prevista — Participação e Respostas)** — recebe desta feature:

- Campanha com Versão, período, critérios e estado;
- a avaliação de elegibilidade por Conclusão (FR-025 a FR-029);
- a condição necessária de admissão (FR-053);
- a consulta das Campanhas EM COLETA aplicáveis a uma Conclusão (FR-052), base para uma
  futura URL institucional permanente (por exemplo, `/egressos/pesquisa`), sem convite;
- a decisão, ainda aberta, sobre o que fazer quando há mais de uma Campanha aplicável
  (DP-404) e se uma Conclusão pode ter mais de uma Participação na mesma Campanha.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade (NON-NEGOTIABLE)**: a mesma Conclusão pode ser elegível em
  várias Campanhas ao longo do tempo (FR-050). Nenhuma Campanha consome a Conclusão. A
  relação futura com Participação é preservada (FR-054).
- **II — Definição institucional de egresso (NON-NEGOTIABLE)**: o universo avaliável é o
  das Conclusões Acadêmicas reconhecidas (FR-017). Nenhum critério redefine egresso ou
  inclui não egressos.
- **III — Dado institucional não é declarado (NON-NEGOTIABLE)**: a avaliação lê apenas
  dado institucional e produz dado derivado não persistido. "Não informado" nunca é
  preenchido (FR-028).
- **VII — Pesquisa, Versão, Campanha e Participação distintas (NON-NEGOTIABLE)**: Campanha
  é entidade própria (FR-001). A Pesquisa decorre da Versão (FR-003). Periodicidade e
  população ficam na Campanha, não na Versão (FR-006). Participação não é criada (FR-055).
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: coleta só com Versão PUBLICADA
  (FR-009, FR-010). Campanha aberta é imutável e não removível (FR-043, FR-044). Os anos
  são absolutos (FR-021). Mudança exige nova Campanha (FR-047).
- **IX — Periodicidade configurável (NON-NEGOTIABLE)**: nenhuma periodicidade, duração ou
  janela relativa é codificada (FR-005, FR-014, FR-021). Critérios pertencem à Campanha,
  como determina o princípio.
- **X — Tecnologia não redefine governança (NON-NEGOTIABLE)**: a Campanha não publica
  Versão (FR-009). Nenhum perfil recebe competência de criar, abrir ou encerrar Campanha
  (FR-056). Não há workflow de aprovação (FR-034).
- **XI — Pessoa única, múltiplas Conclusões**: elegibilidade por Conclusão,
  independentemente das demais Conclusões da Pessoa (FR-016, FR-029). A unidade vem da
  Conclusão, não da Pessoa.
- **XII — Base central; escopos por unidade**: Campanha institucional é o caso sem
  critério de unidade. O recorte por unidade é opcional (FR-018 c), sem base ou Campanha
  separada por campus como requisito.
- **XIV — Redução de fricção**: acesso não depende de convite (FR-048), e a consulta por
  Conclusão (FR-052) permite que a futura jornada contextualize em vez de perguntar.
- **XIX — Acompanha a coleta, não é BI**: a população conhecida é contável (FR-031), sem
  dashboard, fotografia ou indicador.
- **XXII — Simplicidade e YAGNI**: seis campos de critério com semântica fixa (FR-018,
  FR-020), três estados (FR-034), imutabilidade em vez de versionamento (FR-043, FR-046).
  Nenhuma entidade de segmentação, convite ou agendamento (Key Entities).
- **XXIX — Hipóteses não viram requisitos (NON-NEGOTIABLE)**: periodicidade, competência,
  sobreposição, prorrogação, fotografia da população e acesso ficam como `DECISÃO
  PENDENTE`. As escolhas reversíveis estão marcadas como [Hipótese].

**Tensões identificadas (não são conflitos)**:

- **PAEG Art. 22, IV × Campanha institucional**: a PAEG atribui às CSAEGs a aplicação do
  questionário nas unidades e à CPAEG sua elaboração (Art. 21, VI). Esta spec permite
  Campanha institucional e Campanha com recorte de unidade, sem decidir qual instância
  cria qual (DP-402, DP-403).
- **Princípio XIX × população dinâmica**: indicadores operacionais como taxa de resposta
  precisarão de denominador estável. A população por critérios muda quando novas
  Conclusões são incorporadas. A fotografia da população fica pendente (DP-408), sem
  bloquear esta feature.

Nenhum conflito com a Constituição ou com as Features 001, 002 e 003 foi identificado.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. Pertence de fato ao domínio de acompanhamento? Sim. Campanha e critérios de
   elegibilidade estão listados na Fronteira do Domínio do NIAE.
2. É necessária ao ciclo de acompanhamento? Sim. Sem Campanha não há como associar
   Participação a uma rodada e a uma Versão (Princípio VII).
3. Existe ou está prevista solução institucional mais adequada? Não para a rodada de
   acompanhamento. Comunicação, divulgação e convites podem pertencer a soluções externas
   e ficam fora (FR-049).
4. Integração seria suficiente? Não para a definição da Campanha. Sim, no futuro, para
   comunicação.
5. A incorporação aumentaria desnecessariamente o acoplamento do núcleo? Não. A Campanha
   depende só de Versão (002) e de atributos já existentes da Conclusão (001).

## Out of Scope *(mandatory)*

- Participação, Resposta, respostas ao questionário e qualquer marcador provisório delas.
- Formulário público, jornada do egresso, URL institucional permanente, resolução de qual
  Campanha apresentar.
- Autenticação, OTP, login, identificação do egresso.
- Convite, mailing, lista de destinatários, comunicação, e-mail, WhatsApp, notificações,
  CRM, rastreamento de abertura ou clique.
- Editor de pesquisa, interface administrativa de Campanha, dashboard, relatórios.
- GeN, Looker Studio, dataset analítico, exportações.
- Integração acadêmica real.
- Perfis e permissões (CPAEG, CSAEG, Proex, DIREC), workflow de aprovação.
- Cálculo de indicadores da PAEG, taxa de resposta, fotografia da população.
- Agendador de abertura ou encerramento, jobs, filas.
- Segmentação genérica, motor de regras, critérios por outros atributos (curso, forma de
  ingresso, idade, situação declarada), critérios relativos à data corrente, recorte por
  data completa de conclusão.
- Prorrogação, reabertura, suspensão ou cancelamento de Campanha.
- Política de prioridade entre Campanhas sobrepostas.
- Normalização de vocabulário de unidade, nível, modalidade e forma de oferta.
- Qualquer alteração das Features 001, 002 e 003, inclusive a publicação da baseline.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: decisões novas usam o prefixo 4 (DP-401…). As das features anteriores são
citadas como 00n/DP-nnn.

**Novas nesta feature**

- **DP-401** — DECISÃO PENDENTE: periodicidade institucional das rodadas, duração dos
  períodos de coleta e critérios oficiais de população de cada edição (incluindo eventuais
  janelas como "egressos dos últimos N anos"). Instância competente: Proex e Proen e/ou
  órgão competente (PAEG Art. 10, II). Impacto: conteúdo de cada Campanha; nenhum na
  estrutura. Tratamento provisório: nenhum valor padrão (FR-005, FR-014); janelas
  convertidas em anos absolutos (FR-021).
- **DP-402** — DECISÃO PENDENTE: quem pode criar, configurar, abrir, encerrar e remover
  Campanha e definir sua população. A PAEG atribui a elaboração do questionário à CPAEG
  (Art. 21, VI) e sua aplicação às CSAEGs (Art. 22, IV), sem tratar de rodadas. Instância
  competente: Proex/CPAEG (PAEG Art. 26). Impacto: FR-056; perfis de feature futura.
  Tratamento provisório: capacidades do domínio sem exposição a usuários.
  *(Revisado pela 017 — interpretação C1 restrita à demonstração; DP-402 aberta)* A 017 permite gestão mínima pela CPAEG ativa somente na demonstração, sem publicação, critérios ou remoção; a competência produtiva continua pendente.
- **DP-403** — DECISÃO PENDENTE: se haverá Campanhas próprias de unidade (CSAEG) além das
  institucionais, e como elas se relacionam com a Campanha institucional (complementar,
  substituta ou simultânea). Instância competente: CPAEG, com Proex. Impacto: uso do
  critério de unidade, DP-404. Tratamento provisório: ambos os desenhos são
  representáveis; nenhum é obrigatório.
- **DP-404** — DECISÃO PENDENTE: política para Campanhas EM COLETA com populações
  sobrepostas — proibir, priorizar ou deixar o egresso escolher. Instância competente:
  CPAEG. Impacto: jornada da 005 e consulta FR-052. Tratamento provisório: coexistência
  permitida; o sistema devolve todas, sem prioridade (FR-051, FR-052); a 005 NÃO DEVE
  escolher automaticamente sem decisão.
- **DP-405** — DECISÃO PENDENTE: prorrogação do período, reabertura de Campanha encerrada
  e correção editorial do nome após a abertura. Instância competente: CPAEG/Proex.
  Impacto: FR-039, FR-043. Tratamento provisório: nada disso é permitido. Prorrogar exige
  nova Campanha; o encerramento antecipado explícito é permitido (Assumptions).
- **DP-406** — DECISÃO PENDENTE: forma definitiva de acesso do egresso à Campanha (URL
  institucional permanente, Portal do Egresso, outro canal) e mecanismo de identificação.
  Instância competente: a identificar (Proex, DTI; relação com o Portal do Egresso é
  pendência da Constituição). Impacto: 005 e features de acesso. Tratamento provisório:
  nada nesta feature depende de convite ou canal (FR-048); a consulta FR-052 viabiliza
  qualquer forma.
- **DP-407** — DECISÃO PENDENTE: canais de divulgação e eventual comunicação individual
  (e-mail, WhatsApp, convites) e se pertencem ao NIAE ou a solução institucional externa.
  Instância competente: a identificar (Proex, DIREC, comunicação institucional). Impacto:
  nenhum nesta feature (FR-049). Tratamento provisório: inexistente.
- **DP-408** — DECISÃO PENDENTE: se a instituição precisa de uma fotografia da população
  (por exemplo, na abertura ou no encerramento) como denominador estável de indicadores
  operacionais e relatórios (Princípio XIX; Relatório Anual — PAEG Art. 14). Instância
  competente: Proex/CPAEG. Impacto: FR-032; feature de acompanhamento da coleta.
  Tratamento provisório: população calculada sob demanda a partir dos critérios, sem
  fotografia.
- **DP-409** — DECISÃO PENDENTE: tratamento institucional de Conclusões que ficam fora de
  uma Campanha apenas porque um atributo usado no critério não foi informado pela fonte
  (aceitar a exclusão, corrigir o dado na origem ou outra política). Instância
  competente: CPAEG, com responsáveis pelo registro acadêmico. Depende de 001/DP-004 e
  001/DP-005. Impacto: alcance real de Campanhas com recorte. Tratamento provisório:
  exclusão conservadora com motivo NÃO INFORMADO (FR-028), sem processo de correção.

**Herdadas e ainda abertas** (não resolvidas por esta feature)

- **002/DP-001** — competência para publicar Versão. Bloqueia, na prática, a abertura de
  Campanha com a baseline da 003.
- **002/DP-002** — processo institucional de elaboração, revisão e aprovação.
- **003/DP-301** — rótulo inicial das escalas, a resolver antes de publicar a baseline.
- **003/DP-302** — semântica de execução das regras do instrumento, transferida da
  "Feature 004 (jornada)" para a feature de Participação e Respostas.
- **001/DP-001** — fonte acadêmica oficial (define o universo real de Conclusões).
- **001/DP-004** — atributos com qualidade suficiente na fonte real.
- **001/DP-005** — correção de dado acadêmico (afeta a estabilidade da elegibilidade).
- **001/DP-007** — vocabulário canônico de nível, modalidade e forma de oferta (afeta a
  comparação exata de FR-022).
- **001/DP-008** — critério operacional de conclusão na fonte real (define quem entra no
  universo de FR-017).


## Nota de revisão pela Feature 019 (2026-10-04)

FR-016, FR-017 e FR-053 continuam definindo população e elegibilidade sobre Conclusões. A entrada declarada tem compatibilidade provisória própria, sobre unidade, nível e ano, sem excluir por atributos não coletados; a confirmação usa a elegibilidade definitiva da Conclusão. Declarações não integram a população.

Referência: [019 — Formação não localizada e validação posterior](../019-formacao-declarada-validacao/spec.md).


## Nota de revisão pela Feature 020 (2026-10-05)

O Lote de mobilização previsto pela ADR 0004 foi especificado e implementado pela 020, só na demonstração. O Lote é sempre um subconjunto da população no momento (FR-031) restrito ao escopo do operador. Ele não altera critérios, não participa de `admite_participacao` nem da entrada (007) e não exclui ninguém (020 FR-040, SC-007).

Referência: [020 — Mobilização real, Lotes e contatos do egresso](../020-mobilizacao-real-lotes-contatos/spec.md).
