# Feature Specification: Participação em Campanha e respostas em rascunho

**Feature Branch**: `claude/feature-005-participacao-campanha-f29c06`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "Feature 005 — Participação em Campanha e respostas em
rascunho. Registrar que uma Conclusão Acadêmica participa de uma Campanha (no máximo uma
Participação por Campanha × Conclusão, várias ao longo do tempo) e armazenar, enquanto a
Campanha admite coleta, as respostas declaradas às Perguntas da Versão aplicada, nos quatro
tipos existentes, com complemento de 'Outro', alteração e remoção em rascunho, consulta do
estado atual e rejeição de referências e valores incompatíveis. Sem conclusão definitiva,
navegação, obrigatoriedade, autenticação, convite, histórico de edições ou motor genérico
de respostas."

## Contexto

As quatro primeiras features estabeleceram:

- **001** — **Pessoa → Conclusão Acadêmica**, com fonte acadêmica simulada e
  substituível;
- **002** — **Pesquisa → Versão → Seções → Perguntas → Opções**, com quatro tipos de
  pergunta e Versão PUBLICADA imutável;
- **003** — a baseline migrada do Formulário Egresso Ifes 2024 (em RASCUNHO);
- **004** — **Campanha → Versão aplicada**, com período de coleta, população elegível por
  critérios e o contrato de admissão: uma Campanha admite nova Participação de uma
  Conclusão se, e somente se, está EM COLETA e a Conclusão é ELEGÍVEL (004 FR-053).

Falta o elo que fecha a cadeia longitudinal da Constituição (Princípio I):

```text
Pessoa ─────────────── 1 ── 0..N Conclusão Acadêmica                 (001)
                                     │
                                     │ 1
                                     ▼ 0..N
Campanha ── 1 ── 0..N ──────► Participação ◄── no máximo 1 por par    (005)
   │                                 │        Campanha × Conclusão
   │ exatamente 1                    │ 1
   ▼                                 ▼ 0..N
Versão (PUBLICADA) ─► Seção ─► Pergunta ◄─── 1 ── Resposta            (005)
                                  └─► Opção ◄─── referida pela Resposta
                                                 de escolha
```

### Princípio central desta spec

> **Participação não é Resposta.**
>
> A Participação é a ocorrência longitudinal: *"esta Conclusão Acadêmica está sendo
> observada nesta Campanha"*. A Resposta é o valor declarado para uma Pergunta no contexto
> daquela Participação.

E, nesta feature:

> **Toda Participação está em preenchimento.** A 005 entrega persistência segura de
> respostas em rascunho. Concluir o questionário pertence à Feature 006 — Jornada de
> resposta.

### Princípios desta spec

1. **A Participação só conhece a Campanha e a Conclusão.** Pessoa, Pesquisa, Versão e
   contexto acadêmico são obtidos por elas, nunca copiados.
2. **Uma por par, várias no tempo.** Campanha × Conclusão tem no máximo uma Participação;
   a mesma Conclusão participa de quantas Campanhas forem aplicáveis.
3. **A Versão da Campanha é a única régua.** Toda Resposta é validada e interpretada pela
   estrutura histórica da Versão aplicada, nunca pela "versão atual" da Pesquisa.
4. **Declarado não se mistura com institucional.** Responder não altera a Conclusão; a
   Conclusão não preenche respostas.
5. **Rascunho tem só o valor atual.** Adicionar, substituir e remover sem histórico de
   edições, enquanto a Campanha admitir coleta.
6. **Validar tipo, não percurso.** A 005 verifica se o valor cabe na Pergunta; não decide
   quais Perguntas deveriam ter sido apresentadas, nem se faltam respostas.

### Termos usados nesta spec

- **Par**: a combinação de uma Campanha e uma Conclusão Acadêmica.
- **Iniciar**: operação que recebe um par e devolve a sua Participação, criando-a quando
  ainda não existe e a admissão da 004 é satisfeita.
- **Coleta admitida**: a Campanha está EM COLETA no momento de referência, segundo o
  estado derivado da 004 (004 FR-034, FR-038).
- **Momento de referência**: o instante da operação ou consulta, na timezone configurada
  do projeto, como na 004.
- **Versão aplicada**: a Versão referenciada pela Campanha da Participação.
- **Valor**: o conteúdo de uma Resposta, cuja forma depende do tipo da Pergunta (FR-023 a
  FR-027).
- **Escrita de resposta**: registrar, substituir ou remover uma Resposta.
- **Pergunta não respondida**: Pergunta da Versão aplicada para a qual a Participação não
  tem Resposta.

## Clarifications

### Session 2026-10-01

Cinco escolhas da primeira redação foram confirmadas pelo solicitante antes do
`/speckit-plan`, dispensando `/speckit-clarify`. Elas deixam de ser hipóteses e passam a
ser decisões desta feature.

- **Início idempotente** → Confirmado. Para cada par Campanha × Conclusão existe no
  máximo uma Participação. Se ela não existe, é criada somente se a Campanha admite coleta
  e a Conclusão é elegível. Se já existe, é devolvida com a indicação de que já existia,
  sem criar outra e sem modificar nada, **mesmo que a Campanha esteja encerrada**. Nesse
  caso, a devolução é só leitura/idempotência e não autoriza escrita de respostas.
  (FR-011 a FR-013, FR-039)
- **Elegibilidade como gate de entrada** → Confirmado. A elegibilidade é avaliada só na
  criação da Participação. Depois de criada legitimamente, a Participação não tem a
  elegibilidade reavaliada a cada escrita, não é invalidada, apagada ou desassociada por
  correção acadêmica posterior, e não recebe fotografia da elegibilidade. As escritas
  verificam apenas se a Campanha ainda admite coleta. Isso preserva o fato histórico de
  que a Participação foi admitida naquele momento. A consequência de correção acadêmica
  continua em DP-507. (FR-034)
- **Escolha múltipla vazia** → Confirmado. Conjunto não vazio = existe Resposta; remover
  todas as Opções = remover a Resposta; Resposta com conjunto vazio nunca é gravada. "Não
  respondida" e "resposta com zero Opções" não são estados distintos nesta feature, e não
  há marcador para isso. (FR-025)
- **Referência temporal** → Confirmado com refinamento. A 005 registra apenas o momento
  de início da Participação. Não há momento por resposta, histórico de atualização,
  momento de cada edição nem fotografia temporal de valores. Enquanto em rascunho, as
  respostas são valores correntes ainda não consolidados como observação longitudinal
  definitiva. A 006 introduzirá o momento de conclusão, que será a principal referência
  temporal para interpretar as declarações consolidadas (emprego atual, renda, situação de
  estudo, percepções atuais). A 005 não o antecipa. (FR-003, FR-055, FR-056)
- **Preservação histórica e edição de rascunho** → Confirmado. O Princípio VIII protege
  Participações diferentes umas das outras (Participação 2027 ≠ Participação 2029): uma
  posterior nunca sobrescreve respostas de outra. Dentro da **mesma** Participação em
  rascunho, registrar, substituir e remover são o comportamento esperado, sem histórico. A
  imutabilidade após a conclusão será definida pela 006. (FR-008, FR-033, FR-035)

## User Scenarios & Testing *(mandatory)*

<!--
  Os "usuários" desta feature são o próprio domínio, a futura Feature 006 (jornada de
  resposta), que consumirá estas operações, e quem desenvolve e testa. Nenhuma interface
  é criada e nenhuma competência institucional é atribuída. Cada história é verificável
  por operações e consultas de domínio, com a fonte acadêmica simulada (001), Versões
  publicadas de teste (002) e Campanhas (004).

  Cenários mencionam perguntas da baseline da 003 (Q11, Q33, Q47…) apenas como
  ilustração. A baseline está em RASCUNHO e não pode ser aplicada por Campanha aberta
  (004 FR-009); os testes usam Versões publicadas equivalentes.
-->

### User Story 1 - Iniciar Participação para uma Conclusão elegível em Campanha aberta (Priority: P1)

Dado um par Campanha × Conclusão, o domínio inicia a Participação quando a Campanha está
EM COLETA e a Conclusão é ELEGÍVEL, sem convite, autenticação ou qualquer outro
pré-requisito. A Participação registra o momento de início e nasce sem respostas.

**Why this priority**: é o elo Conclusão → Participação da cadeia longitudinal e a porta
de entrada de toda Resposta.

**Independent Test**: com a fonte simulada, uma Versão publicada e uma Campanha aberta,
iniciar a Participação de uma Conclusão elegível e verificar que ela existe, aponta para a
Campanha e a Conclusão, tem momento de início e nenhuma resposta; tentar com Conclusão
não elegível e com Campanha não aberta e verificar rejeição sem nada criado.

**Acceptance Scenarios**:

1. **Given** uma Campanha EM COLETA e uma Conclusão ELEGÍVEL sem Participação nessa
   Campanha, **When** a Participação é iniciada, **Then** existe uma Participação com
   identidade própria, a Campanha e a Conclusão indicadas, o momento de início e zero
   respostas.
2. **Given** a Participação criada, **When** são consultadas sua Pessoa, Pesquisa e Versão,
   **Then** elas são obtidas pela Conclusão e pela Campanha, e coincidem com as delas.
3. **Given** uma Campanha EM COLETA e uma Conclusão NÃO ELEGÍVEL, **When** a Participação é
   iniciada, **Then** a operação é rejeitada indicando a não elegibilidade, com as
   pendências da avaliação da 004, e nenhuma Participação é criada.
4. **Given** uma Campanha EM PREPARAÇÃO ou ENCERRADA e uma Conclusão que seria ELEGÍVEL,
   **When** a Participação é iniciada, **Then** a operação é rejeitada indicando que a
   Campanha não admite coleta, e nada é criado.
5. **Given** uma Campanha ENCERRADA e uma Conclusão NÃO ELEGÍVEL, **When** a Participação é
   iniciada, **Then** a rejeição indica as duas condições não satisfeitas.
6. **Given** uma Campanha EM COLETA e uma Conclusão ELEGÍVEL, **When** a Participação é
   iniciada, **Then** nenhum convite, destinatário, token ou sessão existe ou é
   consultado.

---

### User Story 2 - Garantir uma única Participação por Campanha × Conclusão (Priority: P1)

Repetir o início para o mesmo par nunca cria duplicata. A operação devolve a Participação
existente, sem alterá-la, e indica que ela já existia.

**Why this priority**: a futura jornada poderá iniciar a mesma Participação várias vezes
(retorno do egresso, recarga de página, nova visita). Sem esta garantia, respostas se
espalhariam por Participações paralelas e a leitura longitudinal se perderia.

**Independent Test**: iniciar a Participação de um par várias vezes, inclusive de forma
simultânea, e verificar que existe uma única Participação, com a mesma identidade, o
mesmo momento de início e as mesmas respostas.

**Acceptance Scenarios**:

1. **Given** uma Participação existente para o par, **When** o início é repetido, **Then**
   nenhuma nova Participação é criada, a existente é devolvida com a indicação "já
   existente", e seu momento de início e suas respostas permanecem os mesmos.
2. **Given** um par sem Participação, **When** duas solicitações de início chegam ao mesmo
   tempo, **Then** ao final existe exatamente uma Participação para o par, e ambas as
   solicitações devolvem essa mesma Participação.
3. **Given** uma Participação existente com respostas e uma Campanha já ENCERRADA, **When**
   o início é repetido, **Then** a Participação existente é devolvida, sem alteração e sem
   que a Campanha volte a admitir escrita.
4. **Given** uma Participação existente, **When** se busca qualquer forma de nova tentativa,
   reinício ou segunda Participação do mesmo par, **Then** essa forma não existe.

---

### User Story 3 - Registrar resposta de escolha única (Priority: P1)

Para uma Pergunta de escolha única da Versão aplicada, a Participação registra exatamente
uma Opção válida daquela Pergunta, identificada pela identidade da Opção, e não pelo seu
texto.

**Why this priority**: escolha única é o tipo mais frequente do instrumento vigente e o
único que carrega regras de navegação que a 006 precisará ler.

**Independent Test**: registrar uma Opção válida numa pergunta de escolha única e
consultá-la; tentar registrar nenhuma Opção, duas Opções, Opção de outra Pergunta e texto
livre, verificando rejeição sem alteração.

**Acceptance Scenarios**:

1. **Given** uma Participação em Campanha EM COLETA e uma Pergunta de escolha única da
   Versão aplicada, **When** uma de suas Opções é registrada, **Then** a Pergunta passa a
   respondida, com referência àquela Opção.
2. **Given** a mesma Pergunta, **When** se tenta registrar duas Opções, nenhuma Opção, uma
   Opção de outra Pergunta ou um texto no lugar da Opção, **Then** cada tentativa é
   rejeitada com o motivo correspondente e nada é gravado.
3. **Given** duas Perguntas diferentes com Opções de mesmo texto ("Sim"), **When** a Opção
   "Sim" da primeira é registrada como resposta à segunda, **Then** o registro é rejeitado,
   porque a Opção não pertence àquela Pergunta.
4. **Given** uma Opção selecionada que tem regra de navegação (por exemplo, "Não" em Q33),
   **When** ela é registrada, **Then** nenhuma outra Resposta é criada, alterada ou
   removida e nenhuma Seção é marcada como apresentada ou pulada.

---

### User Story 4 - Registrar resposta de escolha múltipla (Priority: P1)

Para uma Pergunta de escolha múltipla, a Participação registra um conjunto de uma ou mais
Opções válidas daquela Pergunta. A resposta é uma só, com semântica de conjunto: sem
duplicatas, e a ordem em que as Opções foram informadas não tem significado.

**Why this priority**: o instrumento vigente usa escolha múltipla em perguntas centrais
(Q26, Q32, Q47), e a identidade "uma resposta por Pergunta" precisa valer também aqui.

**Independent Test**: registrar {A, C} e {C, A} em duas Participações e verificar
significados iguais; registrar {A, A} e verificar que equivale a {A}; tentar conjunto
vazio e conjunto com Opção estranha e verificar rejeição integral.

**Acceptance Scenarios**:

1. **Given** uma Pergunta de escolha múltipla com Opções A, B e C, **When** {A, C} é
   registrado, **Then** a Pergunta tem uma única Resposta, cujo valor é o conjunto {A, C}.
2. **Given** duas Participações, **When** uma registra {A, C} e a outra {C, A}, **Then** os
   valores consultados são iguais e nenhuma ordem de seleção é apresentada como
   informação.
3. **Given** a mesma Pergunta, **When** a seleção é informada como {A, A}, **Then** o valor
   registrado é {A}.
4. **Given** a mesma Pergunta, **When** se tenta registrar um conjunto vazio, **Then** a
   tentativa é rejeitada; "nenhuma Opção selecionada" é representado pela ausência de
   Resposta, e não por uma Resposta vazia.
5. **Given** a mesma Pergunta, **When** se tenta registrar {A, X}, sendo X Opção de outra
   Pergunta ou de outra Versão, **Then** a tentativa inteira é rejeitada e nem A é
   gravada.
6. **Given** Q47 ("Após o curso, você:"), **When** "Não estudei mais" é registrada junto com
   "Fiz mestrado", **Then** o registro é aceito; a 005 não cria exclusividade entre Opções
   (002 FR-036, 002/DP-005).

---

### User Story 5 - Registrar resposta textual (Priority: P1)

Para uma Pergunta de texto curto, a Participação registra o texto declarado, exatamente
como recebido, sem validação de formato.

**Why this priority**: perguntas abertas do instrumento vigente (Q3, Q10) e os
complementos dependem de texto; a resposta precisa ser preservada sem reinterpretação.

**Independent Test**: registrar textos com espaços, acentos e números e verificar a
consulta idêntica; tentar texto vazio e verificar que a Pergunta continua não respondida.

**Acceptance Scenarios**:

1. **Given** uma Pergunta de texto curto, **When** o texto "  27 anos " é registrado,
   **Then** o valor consultado é exatamente "  27 anos ", sem aparar, converter ou
   interpretar como número.
2. **Given** Q10 ("Em que ano você concluiu o seu curso no Ifes?"), **When** "2020/2" é
   registrado, **Then** o valor é aceito como texto; não há validação de ano, data ou
   regex.
3. **Given** uma Pergunta de texto curto, **When** se tenta registrar texto vazio ou só com
   espaços, **Then** a tentativa é rejeitada e a Pergunta continua não respondida.
4. **Given** uma Pergunta de texto curto, **When** se tenta registrar uma Opção ou um
   número de escala, **Then** a tentativa é rejeitada por valor incompatível com o tipo.

---

### User Story 6 - Registrar resposta de escala (Priority: P1)

Para uma Pergunta de escala, a Participação registra um inteiro entre os limites
definidos na Pergunta, inclusive. Valores fora da escala ou não inteiros são rejeitados.
O valor declarado é preservado como foi registrado.

**Why this priority**: onze perguntas do instrumento vigente são escalas de 1 a 5
(003 FR-018); são a base de indicadores de percepção.

**Independent Test**: numa escala de 1 a 5, registrar 1, 3 e 5 e verificar aceitação;
tentar 0, 6, 2.5 e "3" e verificar rejeição.

**Acceptance Scenarios**:

1. **Given** uma Pergunta de escala de 1 a 5, **When** 1, 3 ou 5 é registrado, **Then** o
   valor consultado é exatamente o inteiro registrado.
2. **Given** a mesma Pergunta, **When** 0 ou 6 é registrado, **Then** a tentativa é
   rejeitada por valor fora dos limites e nada muda.
3. **Given** a mesma Pergunta, **When** 2,5, um texto ou um valor lógico é registrado,
   **Then** a tentativa é rejeitada por valor incompatível com o tipo.
4. **Given** uma escala com rótulo final "Concordo totalmente", **When** 5 é registrado,
   **Then** o valor guardado é 5, e não o rótulo nem um valor normalizado ou ponderado.

---

### User Story 7 - Alterar e remover respostas em rascunho (Priority: P1)

Enquanto a Campanha admitir coleta, a resposta a qualquer Pergunta pode ser registrada,
substituída por outro valor completo ou removida. Só o valor atual existe; nenhum
histórico de edições é mantido.

**Why this priority**: a futura jornada precisa permitir que o egresso volte, corrija e
desmarque respostas antes de concluir. Sem isso, toda resposta seria definitiva no
primeiro clique.

**Independent Test**: registrar, substituir e remover respostas dos quatro tipos e
verificar que a consulta mostra sempre e somente o último valor aceito, e que a Pergunta
removida volta a não respondida.

**Acceptance Scenarios**:

1. **Given** uma Pergunta de escolha única respondida com A, **When** B é registrado,
   **Then** a Pergunta tem uma única Resposta, com B, e A não aparece em nenhuma consulta.
2. **Given** uma Pergunta de escolha múltipla respondida com {A, B}, **When** {C} é
   registrado, **Then** o valor é {C}; a substituição é integral, sem mesclar com o valor
   anterior.
3. **Given** uma Pergunta respondida, **When** a Resposta é removida, **Then** a Pergunta
   volta a não respondida.
4. **Given** uma Pergunta não respondida, **When** a remoção é solicitada, **Then** nada
   muda e o resultado indica que não havia Resposta.
5. **Given** uma Pergunta obrigatória respondida, **When** a Resposta é removida, **Then** a
   remoção é aceita; a obrigatoriedade não é verificada nesta feature.
6. **Given** uma Participação com zero, algumas ou todas as Perguntas respondidas, **When**
   ela é consultada, **Then** nada a caracteriza como concluída, completa ou com
   progresso.

---

### User Story 8 - Registrar complemento textual de "Outro" (Priority: P2)

Quando a Opção selecionada admite complemento textual (002 FR-042, como "Outro:" em Q26,
Q32 e Q45), a Resposta pode trazer o texto livre do egresso. O complemento pertence à
Resposta daquela Pergunta e só é aceito junto da Opção que o admite.

**Why this priority**: necessário para três perguntas do instrumento vigente, mas
depende das histórias de escolha.

**Independent Test**: em escolha única e em escolha múltipla com "Outro:", registrar a
Opção com e sem complemento; tentar complemento com Opção que não o admite e em pergunta de
texto ou escala.

**Acceptance Scenarios**:

1. **Given** Q45 com a Opção "Outro:" que admite complemento, **When** "Outro:" é
   registrada com o complemento "Cuidando de familiar", **Then** a Resposta contém a Opção
   e o complemento, exatamente como recebido.
2. **Given** Q32 (escolha múltipla) com "Outro:", **When** {Bolsa de extensão, Outro:} é
   registrado com complemento, **Then** a Resposta única contém o conjunto e o complemento
   associado a "Outro:".
3. **Given** uma seleção que não inclui a Opção com complemento, **When** um complemento é
   informado, **Then** a tentativa inteira é rejeitada.
4. **Given** uma Pergunta de texto curto ou de escala, **When** um complemento é informado,
   **Then** a tentativa é rejeitada.
5. **Given** "Outro:" registrada com complemento, **When** a resposta é substituída por
   outra Opção, **Then** o complemento deixa de existir junto com a seleção anterior.
6. **Given** "Outro:" selecionada sem complemento, **When** é registrada, **Then** é aceita;
   exigir o complemento é decisão de obrigatoriedade da 006.
7. **Given** "Outro:" selecionada, **When** o complemento informado é vazio ou só com
   espaços, **Then** a tentativa é rejeitada; complemento ausente é a ausência de texto.

---

### User Story 9 - Recuperar o estado atual de uma Participação (Priority: P2)

Dada uma Participação, ou um par Campanha × Conclusão, o domínio devolve o necessário para
a futura jornada reconstruir o preenchimento: Campanha, Conclusão, momento de início, se a
coleta é admitida agora e, para cada Pergunta da Versão aplicada, se está respondida e com
qual valor.

**Why this priority**: sem consulta, nada do que foi gravado é utilizável pela 006. Vem
depois das escritas, das quais depende.

**Independent Test**: registrar respostas dos quatro tipos e um complemento; consultar a
Participação e verificar, Pergunta a Pergunta, respondida ou não e o valor tipado;
localizar o par sem Participação e verificar ausência sem criação.

**Acceptance Scenarios**:

1. **Given** uma Participação com respostas a algumas Perguntas, **When** ela é consultada,
   **Then** cada Pergunta da Versão aplicada aparece como não respondida ou respondida e,
   quando respondida, com a Opção, o conjunto de Opções, o complemento, o texto ou o
   inteiro, conforme o tipo.
2. **Given** um par sem Participação, **When** ela é localizada, **Then** o resultado indica
   ausência e nenhuma Participação é criada, em qualquer estado da Campanha.
3. **Given** uma Participação de Campanha ENCERRADA, **When** é consultada, **Then** todas
   as respostas aparecem, e a consulta indica que a coleta não é mais admitida.
4. **Given** uma Participação, **When** é consultada, **Then** o contexto acadêmico (por
   exemplo, unidade e curso) vem da Conclusão e é identificado como institucional, e os
   valores das respostas são identificados como declarados.
5. **Given** qualquer consulta, **When** ela termina, **Then** nada foi gravado, e nenhum
   progresso, próxima Pergunta ou ordem de apresentação foi calculado.

---

### User Story 10 - Permitir a mesma Conclusão em Campanhas diferentes (Priority: P2)

A mesma Conclusão Acadêmica pode ter uma Participação em cada Campanha aplicável, ao longo
do tempo ou simultaneamente. Nenhuma Participação posterior substitui, encerra ou altera
uma anterior.

**Why this priority**: é o que torna o acompanhamento longitudinal possível
(Princípio I). Depende das histórias de início e de escrita.

**Independent Test**: com a Conclusão ADS — 2024, participar das Campanhas 2025, 2027 e
2030 (cada uma aberta em seu período), responder em cada uma e verificar três
Participações independentes, com respostas que não se afetam.

**Acceptance Scenarios**:

1. **Given** a Conclusão ADS — 2024 com Participação na Campanha 2025, **When** ela inicia
   Participação na Campanha 2027 e depois na 2030, **Then** existem três Participações
   distintas, cada uma com sua Campanha, seu momento de início e suas respostas.
2. **Given** essas Participações, **When** uma resposta é alterada na de 2030, **Then** as
   respostas de 2025 e 2027 permanecem idênticas.
3. **Given** uma nova Participação, **When** ela é criada, **Then** nenhuma resposta é
   copiada, herdada ou pré-preenchida a partir de Participação anterior.
4. **Given** uma Conclusão, **When** suas Participações são consultadas, **Then** todas são
   devolvidas, em ordem determinística, sem que alguma seja apresentada como "a atual".
5. **Given** a Pessoa A com Conclusões de ADS — Serra e de Especialização — Cefor, ambas
   ELEGÍVEIS na mesma Campanha, **When** cada uma inicia Participação, **Then** existem
   duas Participações independentes, uma por Conclusão, sem respostas compartilhadas
   (DP-501).

---

### User Story 11 - Bloquear alterações quando a Campanha não admite mais coleta (Priority: P2)

Quando a Campanha deixa de estar EM COLETA (encerramento explícito ou fim do período),
nenhuma Participação nova é criada e nenhuma Resposta é registrada, substituída ou
removida. O que já existe permanece intacto e consultável; nada é apagado
automaticamente.

**Why this priority**: preserva o significado da rodada encerrada (Princípio VIII). Usa o
estado temporal já entregue pela 004.

**Independent Test**: registrar respostas, encerrar a Campanha (explicitamente, em uma; por
data, em outra) e tentar cada escrita; verificar rejeição, ausência de qualquer mudança e
consulta íntegra.

**Acceptance Scenarios**:

1. **Given** uma Participação com respostas e uma Campanha encerrada explicitamente,
   **When** se tenta registrar, substituir ou remover qualquer Resposta, **Then** cada
   tentativa é rejeitada por coleta não admitida e nada muda.
2. **Given** uma Campanha cujo período terminou em 30/06/2027, **When** uma escrita é
   tentada em 01/07/2027, **Then** ela é rejeitada, sem que nenhum processo agendado tenha
   sido executado.
3. **Given** a mesma Campanha, **When** uma Conclusão ELEGÍVEL sem Participação tenta
   iniciar, **Then** a operação é rejeitada e nada é criado.
4. **Given** a Campanha encerrada, **When** suas Participações em preenchimento são
   consultadas, **Then** continuam existindo com todas as respostas, sem marca de
   abandonadas, concluídas ou expiradas.
5. **Given** uma escrita com momento de referência no último dia do período, **When** ela é
   feita, **Then** é aceita; no dia seguinte, a mesma escrita é rejeitada.

---

### User Story 12 - Rejeitar referências e valores incompatíveis (Priority: P3)

Toda escrita que referencia elemento fora da Versão aplicada, ou cujo valor não cabe no
tipo da Pergunta, é rejeitada explicitamente, sem alteração parcial.

**Why this priority**: os comportamentos já decorrem das histórias P1 e P2; esta história
reúne os casos de borda e as referências cruzadas entre domínios.

**Independent Test**: com duas Versões da mesma Pesquisa ("2027" e "2028", criada a partir
da primeira, com textos idênticos), uma Campanha com 2027 e uma Participação nela,
submeter cada referência e valor inválido da lista mínima (FR-052) e verificar rejeição e
ausência de mudança.

**Acceptance Scenarios**:

1. **Given** uma Participação na Campanha com a Versão 2027, **When** se tenta responder
   Pergunta da Versão 2028, mesmo com texto idêntico, **Then** a tentativa é rejeitada por
   Pergunta de outra Versão.
2. **Given** a mesma Participação, **When** se tenta registrar, numa Pergunta da Versão
   2027, Opção da Pergunta correspondente na Versão 2028, **Then** a tentativa é rejeitada
   porque a Opção não pertence à Pergunta.
3. **Given** a publicação de uma Versão 2028 posterior, **When** as respostas da Campanha
   2027 são consultadas ou validadas, **Then** continuam interpretadas pela Versão 2027,
   sem nenhuma mudança.
4. **Given** uma substituição inválida sobre uma Pergunta já respondida, **When** ela é
   rejeitada, **Then** o valor anterior permanece intacto.
5. **Given** cada item da lista mínima de rejeições (FR-052), **When** é submetido,
   **Then** a rejeição identifica o motivo e nada é gravado.

---

### Cobertura das perguntas de sucesso do solicitante

| # | Pergunta | Resposta da spec |
|---|----------|------------------|
| 1 | Uma Conclusão elegível consegue iniciar uma Participação? | Sim, com Campanha EM COLETA (US1; FR-011) |
| 2 | Repetir o início não cria duplicata? | Não cria; devolve a existente (US2; FR-006, FR-013) |
| 3 | A mesma Conclusão pode participar de Campanhas diferentes? | Sim, de forma independente (US10; FR-007, FR-008) |
| 4 | Os quatro tipos de resposta são representáveis? | Sim (US3–US6; FR-023 a FR-027) |
| 5 | Resposta inválida para o tipo é rejeitada? | Sim (US3–US6, US12; FR-023, FR-052) |
| 6 | Pergunta ou Opção de outra Versão é rejeitada? | Sim (US12; FR-019, FR-024, FR-025) |
| 7 | O egresso pode modificar respostas em rascunho? | Sim, enquanto houver coleta (US7; FR-033) |
| 8 | Declarado e institucional permanecem distintos? | Sim (US9.4; FR-042 a FR-045) |
| 9 | O encerramento impede novas alterações? | Sim, sem apagar nada (US11; FR-039, FR-040) |
| 10 | Nenhuma lógica de jornada ou conclusão foi antecipada? | Nenhuma (FR-037, FR-038, FR-055) |
| 11 | Nenhuma abstração genérica de formulário foi criada? | Nenhuma (FR-054; Key Entities) |

### Edge Cases

- **Início simultâneo do mesmo par**: resulta em exatamente uma Participação, devolvida a
  ambas as solicitações (FR-006, FR-053).
- **Início repetido com Campanha ENCERRADA**: devolve a Participação existente, sem
  alteração; não reabre escrita (FR-013, FR-039).
- **Início repetido depois de a Conclusão deixar de ser elegível** (por correção futura de
  dado acadêmico — 001/DP-005): devolve a Participação existente; a elegibilidade só é
  verificada na criação (FR-013, FR-034, DP-507).
- **Pessoa com duas Conclusões elegíveis na mesma Campanha**: duas Participações
  independentes; a 005 não escolhe entre elas nem compartilha respostas (FR-009, DP-501).
- **Conclusão elegível em duas Campanhas EM COLETA sobrepostas**: pode ter uma Participação
  em cada; a 005 não prioriza (FR-007, 004/DP-404).
- **Mudança de resposta em Pergunta com regra** (Q1, Q14, Q33, Q46): as respostas de
  Seções que deixariam de fazer parte do percurso permanecem; manter ou descartar é
  decisão da 006 (FR-038).
- **Resposta a Pergunta que o percurso não apresentaria** (por exemplo, Q34 com Q33 =
  "Não", ou Q2 com Q1 = "Não"): aceita estruturalmente; o percurso é da 006 (FR-038).
- **Escolha múltipla com todas as Opções**: aceita; não há máximo (002 FR-036).
- **Escolha múltipla "desmarcada" por completo**: é remoção da Resposta, não registro de
  conjunto vazio (FR-025).
- **Valor idêntico ao atual**: aceito sem mudança de significado (FR-036).
- **Remoção de Resposta inexistente**: nada muda; o resultado informa que não havia
  Resposta (FR-036).
- **Escrita no último dia do período**: aceita; no dia seguinte, rejeitada, porque a
  Campanha está ENCERRADA (004 FR-038 b; FR-039).
- **Escrita concorrente sobre a mesma Pergunta**: o resultado final é um dos valores
  completos submetidos, nunca uma mistura (FR-053).
- **Participação sem nenhuma resposta ao fim da Campanha**: continua existindo e
  consultável; o tratamento de abandono é DP-503 (FR-040).
- **Complemento com a Opção "Outro:" fora da seleção de escolha múltipla**: rejeitado
  inteiro (FR-030).
- **Opções de texto igual em Perguntas ou Versões diferentes**: nunca se confundem; a
  Resposta guarda a identidade da Opção (FR-028).
- **Resposta à pergunta de campus (Q11) divergente da unidade da Conclusão**: ambas
  coexistem, cada uma com sua origem; nada é sobrescrito, comparado ou sinalizado
  (FR-043, DP-508).
- **Q1 = "Não" registrada e outras respostas registradas depois**: aceitas
  estruturalmente; finalização e efeitos da recusa são da 006 (FR-055, FR-057).
- **Campanha removida**: impossível com Participação, porque só Campanha nunca aberta pode
  ser removida (004 FR-044) e só Campanha aberta admite Participação (FR-011).

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII): **[PAEG]** com artigo; **[Const. — n]** quando o
requisito decorre diretamente da Constituição; **[00n FR-x]** quando decorre de contrato
de feature anterior; **[Arquitetura]** decisão de modelagem; **[Hipótese]** escolha
reversível de produto; **[Escopo]** delimitação desta feature. O único requisito
**[Herdado]** do instrumento vigente é o complemento de "Outro:" (FR-029): a ferramenta
atual não tem conceito de Participação nem de rascunho.

### Functional Requirements

**Participação**

- **FR-001**: O sistema DEVE representar a Participação como entidade própria, com
  identidade estável e distinta de Campanha, Conclusão Acadêmica, Pessoa e Resposta.
  [Const. — VII, Terminologia]
- **FR-002**: Toda Participação DEVE estar vinculada a exatamente uma Campanha e a
  exatamente uma Conclusão Acadêmica, ambas obrigatórias e nunca alteradas depois da
  criação. [Const. — I, VII; 004 FR-054]
- **FR-003**: A Participação DEVE registrar o **momento de início**, que é seu contexto
  temporal nesta feature. Nenhum outro atributo é exigido: não há estado, progresso, data
  de última alteração, momento por resposta ou por edição, momento de conclusão, canal,
  dispositivo, endereço de acesso nem dado de sessão. O momento de conclusão, referência
  temporal das declarações consolidadas, pertence à 006 (Clarifications).
  [Const. — I, XVI, XXII]
- **FR-004**: A Pessoa DEVE ser obtida pela Conclusão; a Versão e a Pesquisa, pela
  Campanha. Nenhuma delas DEVE ser registrada na Participação de forma que possa divergir.
  [Const. — VII; Arquitetura]
- **FR-005**: O contexto acadêmico da Participação (curso, unidade, nível, ano de
  conclusão etc.) DEVE ser o da Conclusão, obtido dela. Ele NÃO DEVE ser copiado para a
  Participação nem para as Respostas. [Const. — III, XI]

**Unicidade e longitudinalidade**

- **FR-006**: Para cada par Campanha × Conclusão DEVE existir no máximo uma Participação,
  também sob solicitações simultâneas. [Escopo; Const. — VII]
- **FR-007**: A mesma Conclusão Acadêmica PODE ter Participações em Campanhas diferentes,
  sucessivas ou simultâneas, sem limite definido pela 005. [Const. — I; 004 FR-050,
  FR-051]
- **FR-008**: Criar uma Participação, ou escrever respostas nela, NÃO DEVE criar, alterar,
  substituir, encerrar ou condicionar qualquer outra Participação, da mesma Conclusão ou de
  outra. Respostas NÃO DEVEM ser copiadas, herdadas ou pré-preenchidas de outra
  Participação. [Const. — I, VIII]
- **FR-009**: Conclusões diferentes da mesma Pessoa, elegíveis na mesma Campanha, DEVEM
  ter Participações distintas e independentes, sem respostas compartilhadas (DP-501).
  [Const. — I, XI]
- **FR-010**: NÃO DEVEM existir tentativas, reinícios, sessões ou várias Participações do
  mesmo par. [Escopo; Const. — XXII]

**Iniciar Participação**

- **FR-011**: A operação de início DEVE receber uma Campanha e uma Conclusão. Se o par não
  tem Participação, ela DEVE ser criada somente se, no momento de referência, a Campanha
  admite nova Participação daquela Conclusão segundo a 004 (Campanha EM COLETA e Conclusão
  ELEGÍVEL — 004 FR-053), registrando o momento de início. [Const. — I; 004 FR-053]
- **FR-012**: Se a admissão falhar, o início DEVE ser rejeitado informando **todas** as
  condições não satisfeitas — coleta não admitida e/ou Conclusão não elegível, esta com as
  pendências da avaliação da 004 — e nada DEVE ser criado. [Arquitetura; 004 FR-026]
- **FR-013**: Se o par já tem Participação, o início NÃO DEVE criar outra nem alterar a
  existente. Ele DEVE devolver a existente e indicar que ela já existia. Isso vale em
  qualquer estado da Campanha e independentemente da elegibilidade atual, porque nada é
  gravado. Devolver a Participação não torna a escrita admitida (FR-039). [Arquitetura]
- **FR-014**: Estado da Campanha, elegibilidade e admissão DEVEM ser os contratos da 004.
  Esta feature NÃO DEVE reimplementar, ampliar ou relaxar essas regras. [Arquitetura;
  Const. — XXII]
- **FR-015**: O início NÃO DEVE depender de convite, destinatário, comunicação, token,
  sessão, login, OTP, Gov.br, SSO ou URL. Como o egresso chega à Campanha e à Conclusão é
  responsabilidade de feature futura (004/DP-406). [Const. — VI, XV; 004 FR-048]
- **FR-016**: Participações NÃO DEVEM ser criadas automaticamente nem em lote para a
  população elegível. Cada Participação nasce de um início explícito para um par.
  [Const. — XXII; 004 FR-032]
- **FR-017**: Nenhuma operação desta feature DEVE remover Participação (DP-503).
  [Const. — VIII]

**Resposta: pertinência à Participação e à Versão**

- **FR-018**: Toda Resposta DEVE pertencer a exatamente uma Participação e a exatamente uma
  Pergunta. Para cada Participação e Pergunta DEVE existir no máximo uma Resposta, que é o
  valor atual. [Const. — VII, Terminologia]
- **FR-019**: A Pergunta DEVE pertencer à Versão aplicada pela Campanha da Participação.
  Pergunta de outra Versão, da mesma Pesquisa ou de outra, anterior ou posterior, DEVE ser
  rejeitada, ainda que tenha texto idêntico. [Const. — VII, VIII]
- **FR-020**: Toda validação DEVE usar a estrutura da Versão aplicada. O sistema NÃO DEVE
  buscar a versão "atual", "mais recente" ou "vigente" da Pesquisa, nem a Versão de outra
  Campanha. [Const. — VIII; 002 FR-008]
- **FR-021**: A Versão aplicada a uma Campanha que admite coleta é PUBLICADA e imutável
  (004 FR-010; 002 FR-016). Por isso os textos, as Opções, os limites de escala e as
  regras que interpretam uma Resposta não mudam depois de registrada. Esta feature NÃO
  DEVE copiar, fotografar ou duplicar Perguntas e Opções. [Const. — VIII, XXII]
- **FR-022**: A Versão de uma Resposta DEVE ser determinável a partir da Participação
  (pela Campanha) e coincidir com a Versão da Pergunta (FR-019). Ela NÃO DEVE ser
  registrada de forma independente que possa divergir. A forma técnica de garantir a
  coincidência pertence ao plan. [Arquitetura; Const. — VII]

**Valor conforme o tipo da Pergunta**

- **FR-023**: O valor DEVE ter a forma do tipo da Pergunta, entre os quatro tipos da 002.
  Valor de forma incompatível DEVE ser rejeitado: por exemplo, texto para escolha, Opção
  para texto curto ou escala, várias Opções para escolha única, número para escolha. NÃO
  DEVEM ser criados tipos novos. [002 FR-034; Const. — XXIII]
- **FR-024**: A resposta a **escolha única** DEVE referenciar exatamente uma Opção da
  própria Pergunta, pela identidade da Opção. DEVEM ser rejeitados: nenhuma Opção; mais de
  uma Opção; Opção de outra Pergunta, inclusive de outra Versão; texto livre no lugar da
  Opção. [002 FR-035, FR-041]
- **FR-025**: A resposta a **escolha múltipla** DEVE ser um conjunto de uma ou mais Opções
  distintas da própria Pergunta, por identidade, e é uma única Resposta à Pergunta.
  Repetir uma Opção não acrescenta seleção. A ordem de informação NÃO DEVE ter significado
  nem ser apresentada como informação. Conjunto vazio NÃO é Resposta: "nenhuma Opção
  selecionada" é a ausência de Resposta. Opção de outra Pergunta ou Versão DEVE ser
  rejeitada, e a tentativa inteira com ela. NÃO DEVEM ser criados mínimo, máximo ou
  exclusividade de seleções. Remover todas as Opções é remover a Resposta; não há marcador
  de "resposta com zero Opções" (Clarifications). [002 FR-036; 002/DP-005]
- **FR-026**: A resposta a **texto curto** DEVE ser um texto não vazio, preservado
  exatamente como recebido, sem aparar, normalizar, converter ou interpretar. Texto vazio
  ou só com espaços DEVE ser rejeitado; a ausência de resposta é a ausência de Resposta.
  NÃO DEVEM existir regex, máscara, validação genérica, subtipo numérico ou de data, nem
  sanitização metodológica. [002 FR-037; Const. — XIII]
- **FR-027**: A resposta a **escala** DEVE ser um inteiro entre o limite inicial e o limite
  final da Pergunta, inclusive. Valor fora dos limites DEVE ser rejeitado como fora da
  escala; valor não inteiro (fracionário, texto, lógico) DEVE ser rejeitado como
  incompatível com o tipo. O valor DEVE ser preservado como declarado, sem conversão em
  rótulo, peso, pontuação ou normalização. NÃO DEVE ser criada entidade de escala.
  [002 FR-038]
- **FR-028**: Respostas de escolha DEVEM preservar a identidade da Opção da Versão
  aplicada, não apenas seu texto. Opções de mesmo texto em Perguntas ou Versões diferentes
  NÃO DEVEM ser confundidas. [Const. — VIII; 002 FR-041, FR-043]

**Complemento de "Outro"**

- **FR-029**: Quando a resposta de escolha (única ou múltipla) inclui a Opção que admite
  complemento textual (002 FR-042), a Resposta PODE conter um complemento. O complemento
  pertence à Resposta daquela Pergunta e está associado à seleção daquela Opção.
  [Herdado — Q26, Q32, Q45; 002 FR-042]
- **FR-030**: O complemento DEVE ser rejeitado, com a tentativa inteira, quando: (a)
  nenhuma Opção selecionada admite complemento; (b) a Pergunta é de texto curto ou de
  escala; (c) é vazio ou só com espaços. Quando aceito, DEVE ser preservado exatamente
  como recebido. [Arquitetura]
- **FR-031**: O complemento é opcional nesta feature. Exigi-lo ao selecionar "Outro:" é
  regra de obrigatoriedade da 006. [Escopo]
- **FR-032**: NÃO DEVE ser criado tipo genérico de resposta composta. O complemento é
  parte da Resposta de escolha e nada mais. [002 FR-042; Const. — XXIII]

**Rascunho: registrar, substituir e remover**

- **FR-033**: Enquanto a Campanha da Participação admitir coleta no momento de referência,
  DEVE ser possível: (a) **registrar** Resposta a Pergunta não respondida; (b)
  **substituir** a Resposta por novo valor completo — a substituição é integral, sem
  mesclagem, e o valor anterior, inclusive seu complemento, deixa de existir; (c)
  **remover** a Resposta, e a Pergunta volta a não respondida. [Escopo]
- **FR-034**: A escrita de resposta DEVE exigir apenas que a Participação exista e que a
  Campanha admita coleta. A elegibilidade NÃO DEVE ser reavaliada depois do início, a
  Participação NÃO DEVE ser invalidada, apagada ou desassociada por correção acadêmica
  posterior, e NÃO DEVE ser gravada fotografia da elegibilidade (DP-507; Clarifications).
  [Arquitetura]
- **FR-035**: Valores substituídos ou removidos NÃO DEVEM ser preservados em histórico,
  versão de resposta, log de edições, evento ou qualquer outro registro. Existe somente o
  valor atual. [Escopo; Const. — XXII; ver "Tensões identificadas"]
- **FR-036**: Remover Resposta inexistente NÃO DEVE alterar nada e DEVE indicar que não
  havia Resposta. Registrar valor igual ao atual DEVE ser aceito sem mudança de
  significado. [Arquitetura]
- **FR-037**: A Participação PODE ter zero, algumas ou todas as Respostas estruturalmente
  possíveis. Nenhuma quantidade de respostas DEVE significar conclusão. A obrigatoriedade
  das Perguntas NÃO DEVE ser verificada; remover a Resposta de Pergunta obrigatória é
  aceito. [Escopo; 002 FR-031]
- **FR-038**: Regras de navegação e encaminhamentos NÃO DEVEM ser verificados nem
  aplicados. Qualquer Pergunta da Versão aplicada PODE ser respondida, independentemente
  de outras respostas. Alterar a resposta a Pergunta com regra (Q1, Q14, Q33, Q46) NÃO
  DEVE remover, invalidar ou alterar outras Respostas. Percurso, Perguntas apresentadas e
  tratamento de respostas fora do percurso pertencem à 006. [Escopo]

**Campanha sem coleta admitida**

- **FR-039**: Quando a Campanha não está EM COLETA no momento de referência — EM
  PREPARAÇÃO, ou ENCERRADA por ato explícito ou pelo fim do período (004 FR-038) — NÃO
  DEVE ser criada Participação e NÃO DEVE ser registrada, substituída ou removida
  Resposta. A tentativa DEVE ser rejeitada sem alteração. [Const. — VIII; 004 FR-053]
- **FR-040**: Participações e Respostas existentes DEVEM permanecer integralmente
  consultáveis depois do encerramento. Elas NÃO DEVEM ser apagadas, marcadas como
  abandonadas, expiradas ou concluídas, nem alteradas automaticamente. Não há processo,
  agendamento ou job sobre elas. [Const. — VIII; DP-503]
- **FR-041**: NÃO DEVE existir prazo de graça, tolerância ou exceção que admita escrita
  depois do fim da coleta (DP-502). [Escopo; Const. — XXIX]

**Proveniência: declarado ≠ institucional**

- **FR-042**: Toda Resposta DEVE ser dado **declarado** (Princípio III, categoria C). O
  sistema NÃO DEVE registrar dado institucional ou derivado como Resposta. Em particular,
  NÃO DEVE criar nem pré-preencher Resposta a partir da Conclusão (por exemplo, a
  pergunta de campus a partir da unidade, ou a de ano a partir do ano de conclusão).
  [Const. — III]
- **FR-043**: Escrever Respostas NÃO DEVE alterar Conclusão, Pessoa, Campanha, Versão,
  Pergunta ou Opção. Dados da Conclusão NÃO DEVEM alterar Respostas. Uma Conclusão com
  unidade "Serra" e uma resposta à pergunta "Em qual campus você concluiu seu curso?" com
  outra Opção coexistem, cada uma com sua origem, sem sobrescrita, comparação automática ou
  sinalização (DP-508). [Const. — III, IV]
- **FR-044**: A origem DEVE ser identificável na consulta: valores de Resposta são
  declarados; o contexto acadêmico da Participação é institucional, obtido da Conclusão.
  A consulta NÃO DEVE apresentar os dois como a mesma categoria de dado. [Const. — III,
  IV, XVIII]
- **FR-045**: A proveniência "declarado" decorre da natureza da Resposta. Esta feature NÃO
  DEVE registrar, por Resposta, autor, canal, endereço de acesso, dispositivo ou momento
  de cada edição (DP-506). [Const. — IV, XVI]

**Consulta**

- **FR-046**: DEVE ser possível localizar a Participação de um par sem criá-la. O
  resultado é a Participação ou a indicação de que ela não existe, em qualquer estado da
  Campanha. [Arquitetura]
- **FR-047**: DEVE ser possível recuperar uma Participação com: Campanha (e, por ela,
  Versão e Pesquisa); Conclusão (e, por ela, Pessoa e contexto acadêmico); momento de
  início; Respostas atuais. Para cada Pergunta da Versão aplicada, a consulta DEVE
  distinguir não respondida de respondida e, se respondida, dar o valor conforme o tipo:
  identidade da Opção; conjunto de identidades de Opções; complemento, se houver; texto;
  inteiro. Isso DEVE bastar para a 006 reconstruir o preenchimento atual.
  [Const. — VII, VIII]
- **FR-048**: A consulta DEVE permitir saber se a Participação admite escrita no momento
  de referência, pelo estado da Campanha (004). [Arquitetura]
- **FR-049**: Para uma Conclusão, DEVE ser possível listar suas Participações — zero, uma
  ou várias — em ordem determinística, sem significado de preferência e sem apresentar
  qualquer uma como "estado atual" da Conclusão ou da Pessoa. [Const. — I]
- **FR-050**: Consultas NÃO DEVEM gravar nada nem produzir modelo de tela, progresso,
  percentual, próxima Pergunta ou ordem de apresentação. [Escopo; Const. — XXII]

**Atomicidade e rejeições**

- **FR-051**: Toda operação de escrita DEVE ser atômica: aceita por inteiro ou rejeitada
  sem nenhuma alteração. Escolha múltipla com uma Opção válida e uma inválida não grava
  nenhuma. Substituição rejeitada mantém o valor anterior intacto. [Const. — XXVI]
- **FR-052**: Toda rejeição DEVE ser explícita e identificar o motivo. DEVEM ser
  rejeitados, no mínimo:
  (a) início ou escrita com Campanha sem coleta admitida;
  (b) início com Conclusão não elegível para a Campanha;
  (c) escrita em Participação inexistente;
  (d) Pergunta de outra Versão;
  (e) Opção que não pertence à Pergunta, inclusive Opção de outra Versão;
  (f) valor de forma incompatível com o tipo da Pergunta;
  (g) valor de escala fora dos limites;
  (h) complemento incompatível com a seleção ou com o tipo;
  (i) valor vazio: texto vazio, conjunto vazio de Opções ou complemento vazio.
  Opção de outra Versão é necessariamente Opção de outra Pergunta; os dois casos PODEM
  ter o mesmo motivo, mas DEVEM ser verificados separadamente. [Const. — XXVI]
- **FR-053**: Escritas concorrentes sobre o mesmo par ou a mesma Resposta DEVEM resultar
  em estado coerente: uma Participação por par, uma Resposta por Pergunta e, como valor
  final, um dos valores completos submetidos, nunca uma mistura. [Arquitetura]
- **FR-054**: NÃO DEVEM ser criados framework genérico de validação, motor universal de
  respostas, tipo genérico de valor ou registro de tipos de resposta. A validação são as
  regras explícitas dos quatro tipos e das referências. [Const. — XXII, XXIII]

**Fronteira com a Feature 006**

- **FR-055**: Esta feature NÃO DEVE criar: conclusão ou submissão do questionário; estado
  CONCLUÍDA ou qualquer outro estado de Participação; momento de conclusão; verificação
  global de obrigatoriedade; progresso; determinação da próxima Pergunta; aplicação de
  regras de navegação; finalização por Q1 = "Não". [Escopo]
- **FR-056**: Nada nesta feature DEVE impedir que a 006 acrescente a conclusão da
  Participação, o momento da conclusão e a restrição de escritas depois dela, sem alterar
  os requisitos FR-001 a FR-054. [Arquitetura]
- **FR-057**: A resposta à pergunta dos termos (Q1) DEVE ser tratada como Resposta comum de
  escolha única. Ela NÃO DEVE ser tratada como registro de consentimento, nem condicionar o
  registro das demais Respostas (002/DP-007, DP-504). [Const. — XVII, XXIX]

**Privacidade e governança**

- **FR-058**: Iniciar, escrever e consultar são capacidades do domínio. Elas NÃO DEVEM ser
  expostas a usuários ou perfis nem receber interface, URL ou API nesta feature (DP-505).
  [Const. — X, XVI]
- **FR-059**: Valores declarados NÃO DEVEM aparecer em logs, mensagens de rejeição ou
  outros rastros técnicos. [Const. — XVI; Observabilidade]
- **FR-060**: Esta feature NÃO DEVE alterar modelos, operações, contratos ou dados das
  Features 001, 002, 003 e 004. [Escopo]

### Key Entities *(include if feature involves data)*

- **Participação** *(nova)*: ocorrência de acompanhamento de uma Conclusão Acadêmica em uma
  Campanha. Atributos: Campanha (exatamente uma); Conclusão Acadêmica (exatamente uma);
  momento de início. No máximo uma por par. Não tem estado nesta feature: está sempre em
  preenchimento. Pessoa, Pesquisa, Versão e contexto acadêmico são obtidos, não
  registrados.
- **Resposta** *(nova)*: valor declarado atual de uma Pergunta numa Participação.
  Pertence a exatamente uma Participação e a exatamente uma Pergunta da Versão aplicada.
  No máximo uma por Participação e Pergunta. O valor tem uma de quatro formas, conforme o
  tipo da Pergunta: uma Opção; um conjunto não vazio de Opções; um texto não vazio; um
  inteiro dentro dos limites. Nas formas de escolha, há também um complemento textual
  opcional, só quando a Opção que o admite está selecionada. Dado **declarado**.
- **Campanha** *(004, inalterada)*: fornece Versão aplicada, estado temporal (coleta
  admitida ou não) e avaliação de elegibilidade.
- **Conclusão Acadêmica** *(001, inalterada)*: participa; fornece Pessoa e contexto
  acadêmico **institucional**.
- **Versão, Seção, Pergunta, Opção** *(002, inalteradas)*: estrutura histórica que valida
  e interpreta as Respostas: tipo, Opções, complemento admitido e limites de escala.

Entidades deliberadamente **não** criadas: Submission/Submissão, Attempt/Tentativa,
Session/Sessão, AnswerVersion, AnswerHistory/Histórico de Resposta, ResponseValue/Valor
genérico, ResponseType/Tipo de Resposta, Draft/Rascunho como entidade, Progress/Progresso,
QuestionSnapshot/Fotografia de Pergunta, Convite, Token, Consentimento, Evento de edição.

Se a representação de escolha múltipla exigir estrutura auxiliar para relacionar a
Resposta às Opções selecionadas, isso é detalhe técnico do plan e NÃO DEVE ganhar
identidade ou significado de domínio próprios: a Resposta continua sendo uma por
Pergunta.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| Vínculo Participação → Campanha, Conclusão | Registro do sistema | Operação de início (FR-011) | Não se aplica; imutável (FR-002) |
| Momento de início | Registro do sistema | Momento da operação de início | Não se aplica |
| Valor da Resposta (Opção, Opções, texto, inteiro) | **Declarado** | Informado pelo egresso, por meio da futura jornada (006) | Coexiste com o dado institucional, sem sobrescrita (FR-043; DP-508) |
| Complemento de "Outro:" | **Declarado** | Informado com a Opção que o admite | Não se aplica |
| Contexto acadêmico da Participação (curso, unidade, nível, ano…) | Institucional | Conclusão Acadêmica (001), lida, nunca copiada | Divergência com resposta declarada: preservadas ambas, sem tratamento automático (DP-508; 001/DP-005) |
| Pessoa, Pesquisa, Versão da Participação | Registro do sistema (relações) | Obtidas por Conclusão e Campanha (FR-004) | Não se aplica |
| Coleta admitida; elegibilidade | Derivado | Contratos da 004, no momento de referência | Não persistido |
| Pergunta respondida / não respondida | Derivado | Existência de Resposta (FR-047) | Não persistido |

### Modelo conceitual

```text
Pessoa 1 ── 0..N Conclusão Acadêmica 1 ── 0..N Participação N ── 1 Campanha N ── 1 Versão
                                                    │ momento de início         (PUBLICADA,
                                                    │ (sem estado: sempre        imutável)
                                                    │  em preenchimento)            │
                                                    │                               ▼
                                                    │ 1                          Seção
                                                    ▼ 0..N                          │
                                                 Resposta N ─────────────── 1 Pergunta
                                                    │  valor atual, conforme tipo:  │
                                                    │   ESCOLHA_UNICA    → 1 Opção ─┤
                                                    │   ESCOLHA_MULTIPLA → {Opção}+ ┤ (da própria
                                                    │   TEXTO_CURTO      → texto     │  Pergunta)
                                                    │   ESCALA           → inteiro ∈ [início, fim]
                                                    │  + complemento (só com a Opção que o admite)
                                                    ▼
                                               dado DECLARADO

Restrições:
  ∀ par (Campanha, Conclusão): no máximo 1 Participação
  ∀ (Participação, Pergunta): no máximo 1 Resposta
  Resposta.Pergunta.Versão = Resposta.Participação.Campanha.Versão
  Opções da Resposta ⊆ Opções da Pergunta

Operações:
  iniciar(Campanha, Conclusão)
    ├─ par já tem Participação  → devolve a existente ("já existente"); nada grava
    ├─ admite (004 FR-053)      → cria; registra momento de início
    └─ senão                    → rejeita (coleta não admitida e/ou não elegível)

  registrar | substituir | remover Resposta   ⇐ Campanha EM COLETA no momento de referência
  localizar(par) · consultar(Participação) · Participações(Conclusão)   — em qualquer estado

Futuro (006): concluir, percurso, obrigatoriedade efetiva, Q1/Q46–Q48, progresso.
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Num conjunto de referência de pares, 100% dos inícios com Campanha EM COLETA e
  Conclusão ELEGÍVEL criam exatamente uma Participação, e 100% dos inícios com Campanha sem
  coleta ou Conclusão não elegível são rejeitados sem criar nada.
- **SC-002**: Repetir o início de um mesmo par 2 ou mais vezes, inclusive de forma
  simultânea, resulta sempre em exatamente 1 Participação, com a mesma identidade, o mesmo
  momento de início e as mesmas respostas.
- **SC-003**: Uma Conclusão com Participações em 3 Campanhas tem 3 Participações
  independentes. Alterar respostas em qualquer uma deixa 100% das respostas das demais
  inalteradas.
- **SC-004**: Para cada um dos quatro tipos de pergunta, e para o complemento de "Outro:",
  100% dos valores válidos de referência são aceitos e devolvidos pela consulta
  idênticos ao que foi registrado (texto exato, inteiro exato, mesmas Opções por
  identidade).
- **SC-005**: Cada item da lista mínima de rejeições (FR-052, itens a–i) tem pelo menos um
  caso de teste, e 100% deles são rejeitados com motivo identificado e nenhuma alteração.
- **SC-006**: Com duas Versões de mesma Pesquisa e textos idênticos, 100% das tentativas de
  usar Pergunta ou Opção da Versão não aplicada são rejeitadas, e nenhuma Resposta
  referencia elemento fora da Versão aplicada.
- **SC-007**: Em sequências arbitrárias de registrar, substituir e remover, a consulta
  reflete, em 100% das Perguntas, exatamente o último valor aceito, e Perguntas removidas
  aparecem como não respondidas.
- **SC-008**: Depois do encerramento, explícito ou por data, 100% das tentativas de iniciar
  ou de escrever são rejeitadas, e 100% das Participações e Respostas existentes continuam
  consultáveis e idênticas.
- **SC-009**: Em 100% dos casos de teste, escrever Respostas não modifica nenhum dado de
  Conclusão, Pessoa, Campanha ou Versão. Uma resposta de campus divergente da unidade da
  Conclusão é recuperável lado a lado com ela, cada uma com sua origem.
- **SC-010**: Publicar uma Versão posterior da mesma Pesquisa não altera a validação nem a
  interpretação de nenhuma Resposta de Campanha que aplica a Versão anterior.
- **SC-011**: Ao final da feature, não existe nenhum estado, campo ou entidade de
  conclusão, progresso, tentativa, sessão, histórico de resposta, fotografia de pergunta,
  convite ou token, e nenhum dado das Features 001 a 004 é alterado.

## Assumptions

- **Momento de referência**: como na 004, é o instante da operação, na timezone
  configurada do projeto. O plan define como ele é obtido e substituído em testes.
- **Contexto temporal da Participação**: o momento de início é o único registro temporal
  da 005. O momento de conclusão, principal referência para interpretar declarações
  consolidadas (por exemplo, remuneração em salários mínimos — 003, O-19), será
  introduzido pela 006. Confirmado em Clarifications.
- **Escala inteira**: pela 002, a escala tem pontos inteiros consecutivos entre os limites
  (002 FR-038), então o valor é um inteiro.
- **Conjunto vazio de Opções = ausência de Resposta**: 002 FR-036 admite zero seleções em
  escolha múltipla opcional. Nesta feature, isso é representado pela ausência de Resposta,
  e não por uma Resposta vazia. Se a 006 precisar distinguir "vista e deixada em branco"
  de "não vista", isso é informação de percurso, não de valor. Confirmado em
  Clarifications.
- **Sem limite de domínio para texto**: a 002 não define limite para texto curto. Um
  limite técnico de proteção, se necessário, pertence ao plan e não é regra metodológica.
  [Hipótese]
- **Elegibilidade verificada só no início**: confirmado em Clarifications como gate de
  entrada. Pela 001, a incorporação não altera Conclusões existentes, então a
  elegibilidade não muda hoje. Se uma política de correção for adotada (001/DP-005), o
  efeito sobre Participação existente é DP-507.
- **Somente dados fictícios**: enquanto base legal, consentimento e retenção não forem
  definidos (DP-504; 001/DP-009), a feature é exercida apenas com a fonte simulada e
  respostas fictícias.
- **Respostas por canal único**: toda Resposta registrada é declarada pelo próprio egresso,
  por meio da futura jornada. Registro por intermediário é DP-506.
- **Início repetido devolve a existente**: escolhido em vez de rejeitar, porque permite à
  006 usar uma única operação para "localizar ou iniciar", e não grava nada. Confirmado em
  Clarifications, inclusive com Campanha encerrada.

## Relação com outras features

**001** — consumida sem alteração: Conclusão Acadêmica como objeto da Participação e
fonte do contexto institucional; Pessoa obtida pela Conclusão.

**002** — consumida sem alteração: tipos de pergunta (FR-034 a FR-038), identidade de
Opção (FR-041), complemento textual (FR-042), imutabilidade da Versão publicada (FR-016).
A 002 dizia que validar respostas pertence à "futura jornada" (002 FR-031): a 005 valida
o **valor** (tipo e referências); a 006 validará o **percurso** (obrigatoriedade e
navegação).

**003** — não alterada. A baseline está em RASCUNHO e não pode ser aplicada por Campanha
aberta enquanto não for publicada (002/DP-001, 003/DP-301). A 003 encaminhava à "jornada"
DP-302 (Q46–Q48), Q1/recusa, Q6 e Q48; esses itens seguem para a **006**, não para a 005.

**004** — consumida sem alteração: estado temporal da Campanha, avaliação de elegibilidade
e condição de admissão (004 FR-053). A 004 deixou para a 005 "uma ou várias Participações
por Conclusão na mesma Campanha": a resposta é **no máximo uma** (FR-006). A política para
Campanhas sobrepostas continua em 004/DP-404, e a 005 não escolhe entre elas.

**006 (prevista — Jornada de resposta)** — recebe desta feature:

- iniciar ou localizar a Participação de um par (FR-011 a FR-013, FR-046);
- consultar as respostas atuais, Pergunta a Pergunta (FR-047);
- registrar, substituir e remover respostas, com validação de valor (FR-023 a FR-036);
- saber se a coleta é admitida (FR-048);
- a garantia de que nada na 005 impede a conclusão (FR-056).

E permanece responsável por: determinar quais Perguntas apresentar, aplicar navegação,
verificar obrigatoriedade no percurso efetivo, tratar Q46–Q48 (003/DP-302), finalizar por
Q1 = "Não", decidir o que fazer com respostas fora do percurso, exigir ou não complemento
de "Outro:", concluir a Participação e restringir escritas após a conclusão.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade (NON-NEGOTIABLE)**: a cadeia Pessoa → Conclusão → Participação →
  Respostas passa a existir (FR-002, FR-018). A mesma Conclusão participa de várias
  Campanhas (FR-007), e nenhuma Participação substitui ou altera outra (FR-008). Toda
  Participação tem contexto temporal (FR-003) e identifica inequivocamente a Conclusão
  observada (FR-002).
- **III — Dado institucional não é declarado (NON-NEGOTIABLE)**: Respostas são só
  declaradas (FR-042); nenhuma é criada a partir da Conclusão; nada é sobrescrito em
  nenhuma direção (FR-043); a origem é identificável na consulta (FR-044).
- **IV — Proveniência**: proporcional — a categoria "declarado" decorre da Resposta, e o
  institucional, da Conclusão (FR-044, FR-045), sem trilhas por edição.
- **VII — Pesquisa, Versão, Campanha e Participação distintas (NON-NEGOTIABLE)**:
  Participação é entidade própria (FR-001). A Resposta fica associada à Participação e,
  por ela, à Versão efetivamente aplicada (FR-019, FR-022), sem redundância (FR-004).
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: a validação usa a Versão histórica da
  Campanha (FR-020), que é imutável (FR-021). Escolhas guardam a identidade da Opção
  (FR-028). Nada é apagado ao encerrar (FR-040), e a Participação não é removível
  (FR-017).
- **XI — Pessoa única, contextos múltiplos**: uma Participação por Conclusão, não por
  Pessoa (FR-009). O contexto da unidade vem da Conclusão (FR-005).
- **XIV — Redução de fricção**: o início não depende de convite (FR-015); o rascunho
  permite corrigir antes de concluir (FR-033). A repetição de perguntas entre Conclusões
  da mesma Pessoa fica em DP-501.
- **XVI — Privacidade e minimização (NON-NEGOTIABLE)**: só o valor atual (FR-035), sem
  metadados de acesso (FR-003, FR-045), sem valores em logs (FR-059), sem exposição a
  perfis (FR-058). O uso com dados reais depende de DP-504 e DP-505.
- **XVII — Consentimento**: a 005 não registra consentimento nem trata Q1 como tal
  (FR-057). Nada impede a 006, ou feature própria, de relacionar termo, momento,
  Participação e manifestação (DP-504; 002/DP-007).
- **XXII — Simplicidade e YAGNI**: duas entidades novas, quatro formas de valor, nenhum
  estado, nenhum histórico, nenhum motor de validação (FR-054; Key Entities).
- **XXIII — Não é form builder universal**: só os quatro tipos existentes; complemento não
  vira resposta composta genérica (FR-023, FR-032).
- **XXIX — Hipóteses não viram requisitos (NON-NEGOTIABLE)**: prazo de graça, abandono,
  consentimento, acesso, registro por terceiros, múltiplas Conclusões e divergência
  ficam como `DECISÃO PENDENTE`. As escolhas reversíveis estão marcadas como [Hipótese].

**Tensões identificadas (não são conflitos)**:

- **VIII ("Respostas anteriores NÃO DEVEM ser sobrescritas por respostas posteriores") ×
  substituição em rascunho (FR-033, FR-035)**: esta spec interpreta o princípio, em
  conjunto com o Princípio I, como proteção entre **momentos de acompanhamento**
  (Participações diferentes): nenhuma Participação nova altera respostas de outra
  (FR-008). Dentro de uma mesma Participação em preenchimento, substituir o valor é o
  próprio egresso formulando sua declaração antes de concluí-la; o valor atual em
  rascunho é suficiente, sem histórico. A imutabilidade depois da conclusão é questão da
  006. Interpretação confirmada pelo solicitante (Clarifications).
- **XVII × respostas sem consentimento operacional**: respostas, inclusive a Q1 e a
  perguntas sensíveis (Q2, Q4–Q6), podem ser gravadas sem registro de consentimento.
  Isso é aceitável apenas com dados fictícios (Assumptions; DP-504) e não antecipa a
  forma do consentimento.
- **XIX (indicadores operacionais "iniciados") × ausência de estado**: a existência de
  Participação permite, no futuro, contar "iniciados" por Campanha; esta feature não
  calcula nada (Out of Scope).

Nenhum conflito com a Constituição ou com as Features 001 a 004 foi identificado.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. Pertence de fato ao domínio de acompanhamento? Sim. "Participação em Pesquisa e
   Respostas" está listada na Fronteira do Domínio do NIAE.
2. É necessária ao ciclo de acompanhamento? Sim. Sem Participação e Respostas não há
   observação longitudinal.
3. Existe ou está prevista solução institucional mais adequada? Não para as respostas
   associadas à Participação. Identificação e autenticação podem ser externas e ficam
   fora (FR-015).
4. Integração seria suficiente? Não para o registro das respostas. Sim, no futuro, para
   identidade e acesso.
5. A incorporação aumentaria desnecessariamente o acoplamento do núcleo? Não. A
   Participação depende apenas de Campanha (004) e de Conclusão (001); a Resposta, de
   Pergunta e Opção (002).

## Out of Scope *(mandatory)*

- Conclusão ou submissão definitiva, estado CONCLUÍDA, momento de conclusão, edição após
  conclusão.
- Progresso, percentual, próxima Pergunta, navegação, encaminhamentos, regras de
  finalização (Q1 = "Não"), semântica de Q46–Q48.
- Obrigatoriedade no percurso efetivo, exigência de complemento.
- Interface pública, HTML, telas, URL, API.
- Autenticação, identificação do egresso, OTP, token, sessão, Gov.br, SSO.
- Consentimento juridicamente operacional, termo versionado.
- Criação ou alteração de Campanha; convites, destinatários e comunicação.
- Editor de instrumento; novos tipos de pergunta; validação de formato de texto.
- Dashboard, indicadores, contagem de iniciados ou taxa de resposta, GeN, exportações.
- Integração acadêmica real.
- Autosave periódico por job, processos agendados sobre Participações.
- Histórico de alterações, event sourcing, auditoria por edição.
- Pré-preenchimento ou contextualização a partir de dados institucionais (DP-307 da 003).
- Remoção de Participação, política de abandono, anonimização e pseudonimização.
- Qualquer alteração das Features 001 a 004.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: decisões novas usam o prefixo 5 (DP-501…). As das features anteriores são
citadas como 00n/DP-nnn.

**Novas nesta feature**

- **DP-501** — DECISÃO PENDENTE: quando uma Pessoa tem mais de uma Conclusão elegível na
  mesma Campanha, se ela responde uma vez por Conclusão (várias Participações completas)
  ou se respostas sobre a situação atual da Pessoa (trabalho, estudo) devem ser
  compartilhadas ou apresentadas uma só vez. Instância competente: CPAEG. Impacto:
  FR-009, carga do egresso (Princípio XIV), jornada da 006, interpretação analítica.
  Tratamento provisório: uma Participação por Conclusão, independentes, sem compartilhar
  respostas; a 005 não escolhe entre Conclusões.
- **DP-502** — DECISÃO PENDENTE: se haverá prazo de graça para concluir ou alterar
  respostas depois do fim da coleta. Instância competente: CPAEG/Proex. Impacto: FR-039 a
  FR-041. Tratamento provisório: nenhuma escrita depois do fim, sem exceção.
- **DP-503** — DECISÃO PENDENTE: destino das Participações não concluídas — retenção,
  abandono, uso analítico de respostas parciais, eliminação. Instância competente: CPAEG,
  com o encarregado de dados. Impacto: FR-017, FR-040; acompanhamento da coleta;
  exportações. Tratamento provisório: preservadas e consultáveis, sem remoção e sem uso
  analítico definido.
- **DP-504** — DECISÃO PENDENTE: base legal, consentimento e retenção das respostas
  declaradas, em especial das potencialmente sensíveis (Q2, Q4, Q5, Q6), e relação entre
  o termo (002/DP-007), a resposta a Q1 e a Participação. Instância competente: encarregado
  de dados, com CPAEG. Impacto: Princípios XVI e XVII; uso com egressos reais. Tratamento
  provisório: Q1 é Resposta comum (FR-057); apenas dados fictícios. **Bloqueia o uso com
  dados reais.**
- **DP-505** — DECISÃO PENDENTE: quem pode consultar respostas identificadas e
  Participações, em qual escopo (institucional ou por unidade) e com qual finalidade.
  Instância competente: CPAEG/Proex, com o encarregado de dados. Impacto: FR-058; perfis
  e exportações futuras. Tratamento provisório: capacidades do domínio, sem exposição.
- **DP-506** — DECISÃO PENDENTE: se respostas poderão ser registradas por intermediário
  (por exemplo, CSAEG em contato telefônico) e, nesse caso, como identificar essa
  proveniência. Instância competente: CPAEG. Impacto: FR-042, FR-045; Princípio IV.
  Tratamento provisório: não suportado; toda Resposta é declarada pelo egresso.
- **DP-507** — DECISÃO PENDENTE: efeito, sobre Participação existente, de correção de dado
  acadêmico ou de mudança de elegibilidade da Conclusão. Depende de 001/DP-005. Instância
  competente: CPAEG, com o registro acadêmico. Impacto: FR-013, FR-034. Tratamento
  provisório: elegibilidade verificada só no início; a Participação existente continua
  válida e editável enquanto houver coleta.
- **DP-508** — DECISÃO PENDENTE: tratamento de divergência entre resposta declarada a
  pergunta acadêmica (campus, curso, ano, modalidade — Q10 a Q16) e o dado institucional
  da Conclusão: só registrar, sinalizar, ou alimentar correção na fonte. Depende de
  001/DP-005 e 003/DP-307. Instância competente: CPAEG, com o registro acadêmico. Impacto:
  FR-043; Princípio III. Tratamento provisório: ambos preservados, sem comparação nem
  sinalização.

**Encaminhadas à Feature 006** (escopo de feature, não regra institucional)

- Conclusão da Participação, momento de conclusão e edição depois dela.
- Percurso efetivo, Perguntas apresentadas e obrigatoriedade no percurso.
- Destino de respostas fora do percurso após mudança em Q1, Q14, Q33 ou Q46.
- Exigência de complemento ao selecionar "Outro:".
- Escolha entre Campanhas sobrepostas (004/DP-404) e entre Conclusões da mesma Pessoa
  (DP-501) na apresentação ao egresso.

**Herdadas e ainda abertas** (não resolvidas por esta feature)

- **003/DP-302** — Q46–Q48 e semântica de execução das regras: da 006.
- **003/DP-303** — Q6 condicional a Q5.
- **003/DP-309** — dados potencialmente sensíveis (Q2, Q4, Q5, Q6).
- **002/DP-001** — competência para publicar Versão (bloqueia aplicar a baseline).
- **002/DP-006** — comparabilidade entre Versões (interpretação longitudinal das
  Respostas entre Campanhas com Versões diferentes).
- **002/DP-007** — forma institucional do termo de consentimento.
- **004/DP-404** — Campanhas EM COLETA sobrepostas.
- **004/DP-406** — forma de acesso do egresso e mecanismo de identificação.
- **004/DP-408** — população de referência para indicadores (denominador).
- **001/DP-005** — correção de dado acadêmico.
- **001/DP-009** — base legal e retenção de dados pessoais da fonte acadêmica.
