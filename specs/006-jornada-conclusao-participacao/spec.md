# Feature Specification: Jornada de resposta e conclusão da Participação

**Feature Branch**: `claude/feature-006-jornada-conclusao-726cf0`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "Feature 006 — Jornada de resposta e conclusão da
Participação. Conduzir uma Participação em rascunho pelo instrumento da Versão aplicada à
sua Campanha, respeitando ordem, navegação, obrigatoriedade e respostas existentes, e
permitir concluí-la com um momento de conclusão estável (`concluida_em`). A Seção é a
unidade de navegação; a regra condicional decide o destino ao final da Seção (Q47 e Q48
continuam no percurso de quem chega à Seção de Q46). Q1 = 'Não' finaliza a jornada sem
ser consentimento juridicamente operacional. Respostas fora do percurso não contaminam a
Participação concluída. Participação concluída é imutável. Campanha encerrada impede
conclusão tardia. Sem autenticação, Session, Attempt, Progress, Journey, Workflow ou motor
de regras."

## Contexto

As cinco primeiras features estabeleceram:

- **001** — **Pessoa → Conclusão Acadêmica**, com fonte acadêmica simulada;
- **002** — **Pesquisa → Versão → Seções → Perguntas → Opções**, com encaminhamento de
  Seção e regras "se X = Y, ir para Z | finalizar", sem executá-las e sem fixar o momento
  de aplicação (002 FR-053);
- **003** — a baseline do Formulário Egresso Ifes 2024, com 13 Seções, as regras de Q1,
  Q14, Q33 e Q46, os encaminhamentos S4–S7 → S8, S9–S10 → S11, S12 → S13, Q51 sem regra
  e 17 percursos esperados;
- **004** — **Campanha → Versão aplicada**, com estado temporal (EM PREPARAÇÃO, EM
  COLETA, ENCERRADA) e admissão;
- **005** — **Participação → Respostas em rascunho**: uma Participação por Campanha ×
  Conclusão, respostas validadas por tipo e por Versão, alteráveis enquanto houver coleta.
  A 005 deliberadamente não executa navegação, não verifica obrigatoriedade e não conclui.

A Feature 006 transforma essa estrutura em **jornada executável e determinística** e
fecha o ciclo da Participação:

```text
Participação (005)
  │ iniciada_em
  │ concluida_em ◄── novo: ausente = em rascunho; presente = concluída
  │
  ├─ Respostas atuais (005) ─┐
  │                          ├──► percurso derivado (006): Seções, Seção atual,
  └─ Campanha → Versão ──────┘    destinos, pendências, finalização
         (PUBLICADA, histórica)
```

### Princípio central desta spec

> **A jornada é derivada, não armazenada.**
>
> O percurso de uma Participação é sempre reconstruído a partir de duas coisas: a
> **Versão histórica aplicada pela sua Campanha** e as **respostas atuais**. A mesma
> Versão com as mesmas respostas produz sempre o mesmo percurso. Nada de posição, cursor,
> sessão, tentativa ou progresso é persistido.

O único dado novo persistido por esta feature é o **momento de conclusão** da
Participação.

### Princípios desta spec

1. **A Versão da Campanha é a única régua.** Ordem, encaminhamentos, regras e
   obrigatoriedade vêm exclusivamente da Versão aplicada, nunca da versão mais recente da
   Pesquisa, de configuração global ou de dado da Conclusão Acadêmica.
2. **A Seção é a unidade de navegação.** Todas as Perguntas de uma Seção do percurso
   pertencem ao percurso; a regra condicional decide para onde ir **ao sair** da Seção.
3. **Só se exige o que foi apresentado.** Obrigatoriedade vale para Perguntas das Seções
   do percurso; Seções fora dele não exigem nada.
4. **Concluir é um ato único e definitivo.** `concluida_em` é registrado uma vez; depois
   dele, nenhuma Resposta é registrada, substituída ou removida.
5. **A Participação concluída contém apenas o percurso final.** Respostas que ficaram
   fora do percurso são desconsideradas durante o rascunho e removidas no ato da
   conclusão.
6. **Finalizar a jornada não é consentir.** Q1 = "Não" encerra o percurso; nem "Sim" nem
   "Não" constituem registro de consentimento juridicamente operacional.

### Termos usados nesta spec

Os termos abaixo são **conceitos derivados** para descrever comportamento. Nenhum deles é
entidade, tabela ou registro persistido.

- **Versão aplicada**: a Versão referenciada pela Campanha da Participação (005).
- **Pergunta com regra**: Pergunta de escolha única da Versão aplicada que tem ao menos
  uma Opção com regra "ir para Seção" ou "finalizar" (002 FR-050).
- **Seção satisfeita**: Seção em que **todas** as Perguntas obrigatórias têm Resposta na
  Participação. "Ter Resposta" é o conceito da 005: existe Resposta para a Pergunta (não
  há Resposta vazia — 005 FR-025, FR-026).
- **Destino da Seção**: o que segue à Seção quando ela é deixada — outra Seção ou a
  finalização — calculado pela regra de saída (FR-012).
- **Percurso determinado**: a sequência de Seções obtida a partir da primeira Seção da
  Versão aplicada, avançando de cada Seção satisfeita para o seu destino, até encontrar a
  finalização ou uma Seção que ainda não pode ser deixada (FR-014).
- **Seção atual**: a última Seção do percurso determinado quando ele não terminou em
  finalização. É a Seção que a jornada apresentaria agora.
- **Jornada finalizada**: o percurso determinado terminou em finalização (por regra, por
  encaminhamento ou depois da última Seção).
- **Pergunta do percurso**: Pergunta que pertence a uma Seção do percurso determinado.
- **Resposta fora do percurso**: Resposta a Pergunta cuja Seção não pertence ao percurso
  determinado. Enquanto estiver fora do percurso, ela é **inativa** para a jornada
  (FR-030). "Fora do percurso" e "inativa" são condições derivadas, nunca gravadas.
- **Resposta ativa**: Resposta a Pergunta do percurso determinado. Só Respostas ativas
  participam da jornada.
- **Percurso final**: o percurso determinado de uma jornada finalizada; é o percurso
  efetivamente apresentado que fica associado à Participação concluída.
- **Momento de referência**: o instante da operação ou consulta, na timezone configurada
  do projeto, como na 004 e na 005.

### Decisões desta especificação

Escolhas desta spec que resolvem o que as features anteriores deixaram para a 006.
Nenhuma é regra institucional; todas são reversíveis por feature futura.

- **Momento de aplicação da regra → ao sair da Seção.** A unidade de navegação é a Seção.
  Todas as Perguntas da Seção atual pertencem ao percurso; a resposta à Pergunta com regra
  só decide o destino depois que a Seção é deixada. Para a baseline, isso reproduz o
  comportamento do instrumento vigente (inventário, "Semântica das condicionais"; O-15):
  Q47 e Q48 continuam no percurso de quem chega a S11, qualquer que seja a resposta a Q46.
  Não existe atributo, configuração ou estratégia de momento de aplicação. Resolve, para
  a execução, 002 FR-053 e a parte de 003/DP-302 atribuída à feature da jornada; a
  pergunta metodológica de 003/DP-302 (se é **intenção** do instrumento) continua com a
  CPAEG. (FR-010 a FR-013)
- **Respostas fora do percurso → desconsideradas no rascunho, removidas na conclusão.**
  Durante o rascunho, elas permanecem gravadas (o egresso pode voltar ao ramo anterior sem
  redigitar), mas não contam, não são exigidas e são identificadas como fora do percurso.
  No ato da conclusão, todas as Respostas a Perguntas fora do percurso final são removidas
  na mesma operação atômica que registra `concluida_em`. Não há histórico de ramos
  abandonados. (FR-030 a FR-033)
- **Conclusão repetida → devolve "já concluída" sem alterar nada**, em qualquer estado da
  Campanha, como o início repetido da 005 e a publicação repetida da 002. (FR-036)
- **Complemento de "Outro:" → continua opcional para concluir.** O inventário não registra
  que o instrumento vigente exigisse o texto, e a baseline não depende disso para ser
  concluída. Exigir é DP-602. (FR-028)
- **Estrutura fora da capacidade → não executada.** Uma Versão em que alguma Seção tenha
  mais de uma Pergunta com regra não é executada por esta feature: a precedência entre
  regras na mesma Seção não é inventada. A baseline não tem esse caso. (FR-016)

## Clarifications

### Session 2026-10-01

O solicitante confirmou que a feature segue sem `/speckit-clarify` e consolidou quatro
decisões antes do `/speckit-plan`. Elas deixam de ser hipóteses e passam a ser decisões
desta feature.

- **Respostas fora do percurso** → Confirmado. Durante o rascunho, respostas que deixam de
  pertencer ao percurso **não** são apagadas: o egresso pode responder um ramo, mudar uma
  resposta anterior, seguir outro ramo, voltar ao original e recuperar o que já digitou.
  Enquanto estiver fora do percurso, a Resposta é **inativa** para a jornada: não satisfaz
  obrigatoriedade, não gera pendência, não interfere na escolha de destino, não torna
  Seção completa ou incompleta, não permite conclusão e não é tratada como apresentada no
  percurso atual. Não há coluna, flag ou estado "ativa": a condição é derivada. Na
  conclusão, atomicamente: calcula-se o percurso final, identificam-se e removem-se as
  Respostas fora dele, valida-se o percurso final e registra-se `concluida_em`. Depois da
  conclusão, a Participação contém somente Respostas do percurso final, sem histórico de
  ramos abandonados. Rascunhos nunca concluídos podem continuar contendo respostas
  inativas; isso fica em 005/DP-503 (abandono e retenção), sem mecanismo de expiração
  nesta feature, e 005/DP-504 continua bloqueando o uso com dados reais. (FR-030 a FR-033)
- **Conclusão idempotente** → Confirmado. Se `concluida_em` já existe, concluir de novo
  devolve a Participação já concluída com a indicação de que ela já estava concluída, sem
  alterar `concluida_em`, sem reexecutar a limpeza, sem regravar Respostas e sem produzir
  nova submissão. (FR-036)
- **Mais de uma Pergunta com regra na mesma Seção** → Confirmado como **estrutura não
  suportada** nesta feature, rejeitada explicitamente. A jornada não escolhe a primeira
  nem a última, não usa a ordem das Perguntas como precedência, não combina regras e não
  cria prioridade configurável. A restrição existe porque nenhuma semântica institucional
  foi definida para esse cenário e a baseline não precisa dele. É **limitação da
  capacidade atual de execução**, não proibição permanente do modelo de instrumento: a
  002 continua permitindo representar essa estrutura. (FR-016; DP-604)
- **Semântica de navegação** → Confirmado. "Avaliar a regra ao sair da Seção" é a
  semântica de execução **suportada pela Feature 006** e suficiente para a baseline
  migrada. Esta spec **não** afirma que toda Versão futura do Trajetória Ifes deverá
  funcionar assim; evoluções seguem em DP-604. (FR-010 a FR-013)

## User Scenarios & Testing *(mandatory)*

<!--
  Os "usuários" desta feature são o próprio domínio, a futura interface pública da
  jornada (fora do escopo), que consumirá estas capacidades, e quem desenvolve e testa.
  Nenhuma interface, autenticação ou competência institucional é criada.

  A baseline da 003 está em RASCUNHO e não pode ser aplicada por Campanha aberta
  (004 FR-009; 002/DP-001). Os testes usam uma Versão PUBLICADA, apenas no ambiente de
  teste, com estrutura equivalente à baseline (mesmas Seções, Perguntas, obrigatoriedades,
  encaminhamentos e regras). Isso não é publicação institucional. Q1–Q54 e S1–S13 são
  chaves de rastreabilidade da 003, usadas aqui só para ilustrar.
-->

### User Story 1 - Reconstruir o percurso atual de uma Participação (Priority: P1)

Dada uma Participação, o domínio reconstrói, só a partir da Versão aplicada e das
respostas atuais, o percurso determinado: quais Seções o compõem, em que ordem, qual é a
Seção atual (ou se a jornada está finalizada) e quais Perguntas pertencem ao percurso.

**Why this priority**: tudo na feature depende disso — avançar, exigir, concluir e
descartar respostas fora do percurso. Sem percurso não há jornada.

**Independent Test**: com a Versão de teste equivalente à baseline, construir
Participações com conjuntos de respostas conhecidos e comparar o percurso reconstruído
com o esperado; repetir a reconstrução e verificar resultado idêntico e nada gravado.

**Acceptance Scenarios**:

1. **Given** uma Participação sem respostas, **When** o percurso é reconstruído, **Then**
   ele contém apenas S1, S1 é a Seção atual e a jornada não está finalizada.
2. **Given** Q1 = "Sim" e todas as obrigatórias de S2 respondidas, mas Q10 sem resposta,
   **When** o percurso é reconstruído, **Then** ele é S1 → S2 → S3 e a Seção atual é S3.
3. **Given** a mesma Participação reconstruída duas vezes, sem escrita entre elas,
   **When** os resultados são comparados, **Then** são idênticos e nenhuma das
   reconstruções gravou nada.
4. **Given** duas Participações na mesma Campanha com exatamente as mesmas respostas,
   escritas em ordens diferentes e com alterações intermediárias diferentes, **When** os
   percursos são reconstruídos, **Then** são iguais.
5. **Given** uma Participação numa Campanha com a Versão "2027" e a publicação posterior
   de uma Versão "2028" da mesma Pesquisa com navegação diferente, **When** o percurso é
   reconstruído, **Then** ele usa somente a Versão "2027".
6. **Given** uma Conclusão cujo nível institucional é "Graduação" e Q14 = "Pós-Graduação"
   na Participação, **When** o percurso é reconstruído, **Then** ele segue S7 conforme a
   resposta declarada; nenhum dado da Conclusão escolhe, pula ou antecipa Seção.

---

### User Story 2 - Avançar entre Seções conforme ordem e navegação (Priority: P1)

Para cada Seção do percurso, o domínio informa o destino ao deixá-la: a Seção indicada
pela regra acionada; senão, a Seção do encaminhamento; senão, a seguinte na ordem; e,
depois da última, a finalização. "Avançar" não é gravado: é a reconstrução do percurso
com as respostas atuais.

**Why this priority**: é a execução, finalmente, das capacidades de navegação da 002 e
dos encaminhamentos da baseline.

**Independent Test**: numa Versão de teste com Seções em ordem, encaminhamento e regras,
verificar o destino de cada Seção para cada resposta relevante.

**Acceptance Scenarios**:

1. **Given** S2 satisfeita e sem Pergunta com regra nem encaminhamento, **When** seu
   destino é consultado, **Then** é S3 (Seção seguinte na ordem).
2. **Given** S4 satisfeita, com encaminhamento para S8, **When** seu destino é consultado,
   **Then** é S8, e S5, S6 e S7 não pertencem ao percurso.
3. **Given** S8 satisfeita com Q33 = "Não", **When** seu destino é consultado, **Then** é
   S10, porque a regra acionada prevalece sobre o fluxo padrão (002 FR-054).
4. **Given** S13, última Seção, satisfeita, **When** seu destino é consultado, **Then** é
   a finalização, sem regra explícita.
5. **Given** a Seção atual não satisfeita, **When** se consulta se ela pode ser deixada,
   **Then** a resposta é "não", com as Perguntas obrigatórias pendentes; o percurso não
   avança além dela.
6. **Given** qualquer consulta de destino ou de percurso, **When** termina, **Then**
   nenhuma posição, Seção visitada, momento ou progresso foi gravado.

---

### User Story 3 - Validar obrigatoriedade da Seção atual (Priority: P1)

A Seção atual só pode ser deixada quando todas as suas Perguntas obrigatórias têm
Resposta. Perguntas opcionais nunca impedem o avanço. Perguntas de Seções fora do
percurso nunca são exigidas.

**Why this priority**: obrigatoriedade é configuração da Versão desde a 002 (FR-031), mas
nunca foi verificada; a 005 aceita remover resposta obrigatória.

**Independent Test**: em S9 (Q34–Q44, com Q42 e Q44 opcionais), responder todas exceto
uma obrigatória e verificar pendência só dela; responder todas as obrigatórias e deixar
Q42 e Q44 em branco e verificar Seção satisfeita.

**Acceptance Scenarios**:

1. **Given** S9 com todas as obrigatórias respondidas e Q42 e Q44 sem resposta, **When** a
   Seção é avaliada, **Then** está satisfeita.
2. **Given** S9 com Q43 sem resposta, **When** a Seção é avaliada, **Then** não está
   satisfeita e a pendência indica exatamente Q43.
3. **Given** S8 satisfeita com Q33 = "Não", **When** o percurso é avaliado, **Then** as
   obrigatórias de S9 não aparecem como pendência em nenhum momento.
4. **Given** uma Pergunta obrigatória de escolha múltipla, **When** ela tem Resposta com
   uma Opção, **Then** está respondida; sem Resposta, está pendente (não há "Resposta
   vazia" — 005 FR-025).
5. **Given** a configuração de obrigatoriedade da Versão, **When** a jornada é executada,
   **Then** ela não é alterada, relaxada nem complementada (por exemplo, Q42 e Q44 seguem
   opcionais — 003/DP-304).

---

### User Story 4 - Resolver os ramos de Q1, Q14, Q33 e Q46 (Priority: P1)

As quatro Perguntas com regra da baseline determinam o percurso como no instrumento
vigente. Para cada combinação de respostas, o percurso reconstruído é exatamente um dos
17 percursos esperados da 003.

**Why this priority**: as ramificações são o significado metodológico preservado pela
003 (Princípio XIII); executá-las corretamente é o critério de fidelidade da jornada.

**Independent Test**: para cada combinação de Q1, Q14 (4 Opções), Q33 (2) e Q46 (2),
preencher as obrigatórias do percurso e comparar o percurso final com a tabela "Percursos
esperados" da 003.

**Acceptance Scenarios**:

1. **Given** Q1 = "Sim" e S1 deixada, **When** o percurso é reconstruído, **Then** a
   próxima Seção é S2.
2. **Given** Q14 = "Ensino Médio/Técnico Integrado", "Técnico
   Concomitante/Subsequente/EJA-PROEJA", "Graduação" ou "Pós-Graduação", **When** S3 é
   deixada, **Then** o destino é, respectivamente, S4, S5, S6 ou S7, e a Seção escolhida
   converge para S8 pelo encaminhamento.
3. **Given** Q33 = "Sim" ou "Não", **When** S8 é deixada, **Then** o destino é S9 ou S10,
   e ambas convergem para S11.
4. **Given** Q46 = "Sim", **When** S11 é deixada, **Then** o percurso segue S12 → S13 →
   finalização; com Q46 = "Não", segue S13 → finalização.
5. **Given** Q51 respondida com qualquer Opção, inclusive "Instituição Privada", **When**
   S12 é deixada, **Then** o destino é S13 pelo encaminhamento da Seção; nenhuma regra é
   associada a Q51 nem criada pela jornada.
6. **Given** as 16 combinações com Q1 = "Sim" mais a de Q1 = "Não", **When** cada percurso
   final é reconstruído, **Then** os 17 percursos coincidem com os da 003, todos
   terminando em finalização.

---

### User Story 5 - Preservar Q47/Q48 antes do desvio de Q46 (Priority: P1)

Quem chega a S11 recebe Q46, Q47 e Q48, nessa ordem. A resposta a Q46 só decide o destino
depois que S11 é deixada. Q47, obrigatória, é exigida de todos que chegam a S11; Q48,
opcional, nunca é exigida.

**Why this priority**: é a decisão pendente explícita das features 002 e 003 (FR-053;
DP-302). Suprimir Q47 e Q48 em silêncio mudaria o significado da baseline.

**Independent Test**: com Q46 = "Sim" e com Q46 = "Não", verificar que Q47 e Q48 estão no
percurso, que S11 não pode ser deixada sem Q47 e que pode ser deixada sem Q48.

**Acceptance Scenarios**:

1. **Given** S11 no percurso e Q46 = "Não", **When** as Perguntas do percurso são
   consultadas, **Then** Q46, Q47 e Q48 pertencem ao percurso, na ordem 1, 2, 3.
2. **Given** S11 com Q46 = "Não" e Q47 sem resposta, **When** S11 é avaliada, **Then** não
   está satisfeita, a pendência é Q47, e o percurso não segue para S13.
3. **Given** S11 com Q46 = "Sim", Q47 respondida e Q48 sem resposta, **When** S11 é
   avaliada, **Then** está satisfeita e o destino é S12.
4. **Given** Q46 = "Sim" e Q47 = {"Não estudei mais"}, **When** S11 é avaliada, **Then**
   nada é rejeitado nem tratado como contradição: a jornada não cria exclusividade nem
   condição entre respostas (002/DP-005).
5. **Given** a Versão aplicada, **When** a jornada é executada, **Then** nenhuma Pergunta
   de S11 é suprimida, movida ou condicionada, e nenhum atributo de momento de aplicação
   é consultado ou criado.

---

### User Story 6 - Concluir Participação válida (Priority: P1)

Quando a jornada está finalizada, todas as obrigatórias do percurso final têm Resposta e
a Campanha ainda admite coleta, a Participação pode ser concluída. A conclusão registra
`concluida_em`, remove as respostas fora do percurso final e preserva as do percurso.

**Why this priority**: é o objetivo da feature. Sem conclusão, a Participação nunca vira
observação longitudinal consolidada.

**Independent Test**: preencher um percurso completo (por exemplo, Q1 = "Sim", Q14 =
"Graduação", Q33 = "Sim", Q46 = "Não"), concluir e verificar `concluida_em`, as respostas
do percurso intactas e nenhuma outra.

**Acceptance Scenarios**:

1. **Given** jornada finalizada, obrigatórias do percurso final respondidas e Campanha EM
   COLETA, **When** a Participação é concluída, **Then** `concluida_em` passa a ser o
   momento de referência, e todas as Respostas do percurso final permanecem idênticas.
2. **Given** jornada não finalizada (Seção atual não satisfeita), **When** a conclusão é
   solicitada, **Then** é rejeitada indicando a Seção atual e suas obrigatórias
   pendentes, e nada muda.
3. **Given** um percurso final com Q42 e Q44 sem resposta (opcionais), **When** a
   Participação é concluída, **Then** a conclusão é aceita.
4. **Given** uma Participação concluída, **When** é consultada, **Then** indica concluída,
   com `concluida_em`, e nenhuma outra marca de estado, submissão ou tentativa existe.
5. **Given** a conclusão aceita, **When** se procura uma segunda submissão, uma nova
   tentativa ou uma cópia da Participação, **Then** nada disso existe: a Participação é a
   mesma, com a mesma identidade e o mesmo momento de início.
6. **Given** a conclusão, **When** ela termina, **Then** nenhum dado de Conclusão, Pessoa,
   Campanha, Versão, Seção, Pergunta ou Opção foi alterado.

---

### User Story 7 - Bloquear edição após conclusão (Priority: P1)

Depois de concluída, a Participação é imutável: nenhuma Resposta é registrada, substituída
ou removida; `concluida_em` não muda; a Participação não volta a rascunho.

**Why this priority**: sem imutabilidade, "concluída" não teria significado histórico
(Princípio VIII).

**Independent Test**: concluir uma Participação com a Campanha ainda EM COLETA e tentar
cada operação de escrita da 005 (quatro tipos e remoção) e nova conclusão; verificar
rejeição ou "já concluída", e Participação idêntica.

**Acceptance Scenarios**:

1. **Given** uma Participação concluída e a Campanha ainda EM COLETA, **When** se tenta
   registrar, substituir ou remover qualquer Resposta, **Then** cada tentativa é rejeitada
   indicando Participação concluída, e nada muda.
2. **Given** uma Participação concluída, **When** a conclusão é solicitada de novo,
   **Then** nada muda, `concluida_em` permanece o mesmo e o resultado indica "já
   concluída".
3. **Given** uma Participação concluída, **When** se procura operação para reabrir,
   desfazer a conclusão ou apagar `concluida_em`, **Then** ela não existe.
4. **Given** uma Participação concluída, **When** o início da 005 é repetido para o mesmo
   par, **Then** a mesma Participação é devolvida como "já existente", concluída e sem
   alteração.
5. **Given** uma Participação concluída, **When** sua consulta indica se admite escrita,
   **Then** a resposta é "não", mesmo com a Campanha EM COLETA.

---

### User Story 8 - Retomar Participação em rascunho (Priority: P2)

Uma Participação em rascunho pode ser retomada a qualquer momento enquanto houver coleta.
A jornada é reconstruída pelas respostas atuais e indica a Seção atual, sem cursor,
sessão ou tentativa.

**Why this priority**: o egresso pode interromper e voltar; depende das histórias de
percurso.

**Independent Test**: responder até o meio de S9, "abandonar" (nenhuma ação), localizar ou
iniciar a Participação de novo e verificar que a jornada indica S9 como Seção atual, com
as respostas anteriores.

**Acceptance Scenarios**:

1. **Given** uma Participação em rascunho com S1–S8 satisfeitas, Q33 = "Sim" e S9
   parcialmente respondida, **When** ela é retomada, **Then** a Seção atual é S9 e as
   respostas já dadas aparecem.
2. **Given** a retomada, **When** se verifica o que foi gravado para isso, **Then** nada
   foi gravado: nenhuma sessão, tentativa, posição ou momento de retomada.
3. **Given** a retomada, **When** o egresso quer revisar uma Seção anterior do percurso,
   **Then** as Seções do percurso determinado e suas respostas estão disponíveis para
   consulta.
4. **Given** uma Participação em rascunho de Campanha ENCERRADA, **When** é retomada,
   **Then** a jornada é consultável, indica que a coleta não é mais admitida e que a
   conclusão não é possível.

---

### User Story 9 - Remover respostas que ficaram fora do percurso após mudança de ramo (Priority: P2)

Se o egresso responde um ramo e depois muda a resposta que escolhe o ramo, as respostas do
ramo abandonado deixam de pertencer ao percurso: são desconsideradas no rascunho e
removidas no ato da conclusão. A Participação concluída nunca contém resposta a Pergunta
que não esteve no percurso final.

**Why this priority**: evita que um ramo não apresentado contamine a observação
consolidada; depende das histórias de percurso e de conclusão.

**Independent Test**: responder S9 com Q33 = "Sim", trocar Q33 para "Não", responder S10,
concluir e verificar que nenhuma Resposta de S9 existe; repetir trocando de volta para
"Sim" antes de concluir e verificar que as respostas de S9 voltam a contar.

**Acceptance Scenarios**:

1. **Given** S9 respondida e Q33 trocada de "Sim" para "Não", **When** a jornada é
   reconstruída, **Then** S9 não pertence ao percurso, suas respostas aparecem como fora
   do percurso e nenhuma delas é exigida ou contada.
2. **Given** a situação anterior com S10 e as Seções seguintes satisfeitas, **When** a
   Participação é concluída, **Then** as Respostas de Q34–Q44 não existem mais, e as do
   percurso final permanecem idênticas.
3. **Given** Q33 trocada de "Sim" para "Não" e depois de volta para "Sim", antes de
   concluir, **When** a jornada é reconstruída, **Then** as respostas de S9 voltam a
   pertencer ao percurso sem precisar ser redigitadas.
4. **Given** Q14 trocada de "Graduação" para "Pós-Graduação", **When** a Participação é
   concluída, **Then** a resposta a Q18 é removida e a de Q19 é preservada.
5. **Given** a remoção na conclusão, **When** se procura o valor removido, **Then** não
   há histórico, ramo abandonado, cópia ou registro dele.
6. **Given** uma resposta fora do percurso, **When** a conclusão é rejeitada por qualquer
   motivo, **Then** a resposta continua gravada; só a conclusão aceita remove.

---

### User Story 10 - Finalizar corretamente por Q1 = Não (Priority: P2)

Q1 = "Não" finaliza a jornada ao deixar S1. A Participação pode ser concluída só com a
resposta a Q1; nenhuma Pergunta posterior é exigida, e respostas posteriores existentes
são removidas na conclusão. Isso é finalização da jornada, não registro de consentimento.

**Why this priority**: reproduz a regra de finalização da baseline (003 FR-023; inventário
O-17), mas é um ramo de uma única Pergunta.

**Independent Test**: responder Q1 = "Não" e concluir; depois, noutra Participação,
responder Q1 = "Sim", algumas Perguntas de S2, trocar Q1 para "Não" e concluir.

**Acceptance Scenarios**:

1. **Given** Q1 = "Não", **When** o percurso é reconstruído, **Then** é S1 → finalização,
   e a jornada está finalizada.
2. **Given** Q1 = "Não" e Campanha EM COLETA, **When** a Participação é concluída, **Then**
   a conclusão é aceita com uma única Resposta, a de Q1.
3. **Given** Q2–Q9 respondidas e Q1 trocada depois para "Não", **When** a Participação é
   concluída, **Then** apenas a Resposta de Q1 permanece.
4. **Given** uma Participação concluída com Q1 = "Não", **When** é consultada, **Then**
   nada a apresenta como consentimento negado, recusa jurídica, opt-out ou bloqueio de
   futuras Participações; a recusa é apenas o valor declarado de Q1.
5. **Given** uma Participação concluída com Q1 = "Sim", **When** é consultada, **Then**
   nada a apresenta como consentimento juridicamente válido; Q1 continua Resposta comum
   (005 FR-057).

---

### User Story 11 - Impedir conclusão após encerramento da Campanha (Priority: P2)

Quando a Campanha deixa de estar EM COLETA, a Participação em rascunho não pode mais ser
concluída. Não há prazo de graça. A Participação já concluída continua consultável.

**Why this priority**: preserva o significado temporal da rodada (Princípio VIII); usa o
estado já entregue pela 004.

**Independent Test**: preparar duas Participações completas; encerrar a Campanha
(explicitamente numa, por data noutra); tentar concluir; verificar rejeição e
Participações intactas.

**Acceptance Scenarios**:

1. **Given** jornada finalizada e Campanha ENCERRADA explicitamente, **When** a conclusão
   é solicitada, **Then** é rejeitada por coleta não admitida, e nada muda, inclusive as
   respostas fora do percurso.
2. **Given** uma Campanha com período até 30/06/2027, **When** a conclusão é solicitada em
   30/06/2027, **Then** é aceita; em 01/07/2027, é rejeitada.
3. **Given** uma Participação concluída antes do encerramento, **When** é consultada
   depois, **Then** continua concluída, com o mesmo `concluida_em` e as mesmas respostas.
4. **Given** uma Participação em rascunho de Campanha ENCERRADA, **When** o tempo passa,
   **Then** ela não é concluída, expirada, abandonada nem alterada automaticamente
   (005 FR-040; DP-503).

---

### User Story 12 - Rejeitar estados inconsistentes (Priority: P3)

A jornada e a conclusão recusam explicitamente o que não conseguem interpretar com
segurança: Versão fora da capacidade desta feature e Respostas incoerentes com a Versão
aplicada. Nunca concluem por aproximação.

**Why this priority**: as operações da 005 e a imutabilidade da Versão publicada já
impedem esses estados; esta história fixa o comportamento defensivo.

**Independent Test**: numa Versão de teste com duas Perguntas com regra na mesma Seção,
verificar que a jornada indica estrutura não suportada e que a conclusão é rejeitada;
inserir, por meio de teste, uma Resposta incoerente e verificar rejeição da conclusão.

**Acceptance Scenarios**:

1. **Given** uma Versão aplicada com uma Seção que contém duas Perguntas com regra,
   **When** a jornada é consultada, **Then** indica estrutura não suportada, identificando
   a Seção, e não escolhe uma regra.
2. **Given** a mesma Versão, **When** a conclusão é solicitada, **Then** é rejeitada pelo
   mesmo motivo, e nada muda.
3. **Given** uma Resposta do percurso incoerente com a Versão aplicada (por exemplo, Opção
   que não pertence à Pergunta), produzida fora das operações, **When** a conclusão é
   solicitada, **Then** é rejeitada identificando a Pergunta e o motivo, e nada muda.
4. **Given** qualquer rejeição, **When** ela é comunicada, **Then** não contém valor
   declarado (texto, inteiro ou complemento) do egresso.

---

### Cobertura das perguntas de sucesso do solicitante

| # | Pergunta | Resposta da spec |
|---|----------|------------------|
| 1 | O sistema sabe qual é o percurso atual de uma Participação? | Sim, derivado de Versão + respostas (US1; FR-014, FR-017) |
| 2 | Apenas Perguntas do percurso são exigidas? | Sim (US3; FR-019 a FR-021) |
| 3 | A navegação Q46/Q47/Q48 reproduz a semântica atual? | Sim, regra aplicada ao sair da Seção (US5; FR-010, FR-011, FR-025) |
| 4 | Q1 = Não encerra corretamente a jornada? | Sim, sem ser consentimento (US10; FR-022 a FR-024) |
| 5 | Uma Participação completa pode ser concluída? | Sim (US6; FR-034, FR-035) |
| 6 | `concluida_em` é preservado? | Sim, registrado uma vez (US7; FR-003, FR-036) |
| 7 | Uma Participação concluída fica imutável? | Sim (US7; FR-038 a FR-041) |
| 8 | Alterar um ramo remove/invalida respostas fora do percurso? | Desconsidera no rascunho, remove na conclusão (US9; FR-030 a FR-033) |
| 9 | A Campanha encerrada impede conclusão tardia? | Sim, sem prazo de graça (US11; FR-034 b, FR-042) |
| 10 | Nenhum conceito de sessão/workflow/progresso foi criado? | Nenhum (FR-005, FR-018, FR-052) |
| 11 | Autenticação continua fora do escopo? | Sim (FR-051) |

### Edge Cases

- **Participação sem nenhuma resposta**: percurso = S1, Seção atual S1; conclusão
  rejeitada por pendência de Q1 (FR-014, FR-034).
- **Resposta a Pergunta de Seção ainda não alcançada** (por exemplo, Q2 com Q1 sem
  resposta, permitido pela 005 FR-038): aceita e mantida; aparece como fora do percurso
  determinado até agora; volta a contar se a Seção entrar no percurso (FR-030).
- **Pergunta com regra obrigatória sem resposta**: a Seção não está satisfeita e o
  destino ainda não está determinado; o percurso para nela (FR-012, FR-014).
- **Pergunta com regra opcional sem resposta**: nenhuma regra é acionada; vale o
  encaminhamento ou o fluxo padrão (002 FR-054; FR-012). Não ocorre na baseline: Q1, Q14,
  Q33 e Q46 são obrigatórias.
- **Opção sem regra numa Pergunta com regra**: vale o encaminhamento ou o fluxo padrão
  (002 FR-052; FR-012).
- **Seção cujas Perguntas são todas opcionais**: fica satisfeita assim que alcançada; na
  reconstrução, o percurso passa por ela sem fazê-la Seção atual. Não ocorre na baseline:
  toda Seção tem ao menos uma obrigatória (Assumptions).
- **Q6 respondida com Q5 = "Não"**: Q6 pertence a S2 e ao percurso; a resposta é mantida.
  A jornada não cria condição entre Q5 e Q6 (003/DP-303).
- **Q48 respondida por quem marcou "Não estudei mais" em Q47**: mantida; a condição de Q48
  é só textual (003, O-15).
- **Q46 = "Sim" com Q47 = {"Não estudei mais"}**: aceito; nenhuma contradição é
  verificada (002/DP-005).
- **"Outro:" selecionada sem complemento em Pergunta obrigatória** (Q26, Q32, Q45): a
  Pergunta está respondida; a conclusão não exige complemento (FR-028; DP-602).
- **Troca de ramo e volta ao ramo original antes de concluir**: as respostas do ramo
  original voltam a contar, sem redigitação (FR-030).
- **Conclusão no último dia do período**: aceita; no dia seguinte, rejeitada (004
  FR-038 b; FR-034).
- **Conclusão repetida, inclusive com a Campanha já ENCERRADA**: devolve "já concluída",
  sem alterar nada (FR-036).
- **Conclusão e escrita de resposta simultâneas**: ou a escrita ocorre antes e é
  considerada pela conclusão, ou ocorre depois e é rejeitada; nunca há Resposta gravada
  depois de `concluida_em` (FR-043).
- **Duas conclusões simultâneas**: exatamente um `concluida_em`; a outra solicitação
  devolve "já concluída" ou o mesmo resultado (FR-043).
- **Conclusão rejeitada**: nada é removido nem gravado, inclusive respostas fora do
  percurso (FR-033, FR-044).
- **Participação concluída com Q1 = "Não"**: tem uma única Resposta; não bloqueia
  Participações em outras Campanhas nem é tratada como opt-out (FR-024; DP-601).
- **Pessoa com duas Conclusões elegíveis na mesma Campanha**: cada Participação tem sua
  própria jornada e conclusão; nada é compartilhado (005 FR-009; 005/DP-501).
- **Versão posterior publicada durante a coleta**: não afeta o percurso nem a conclusão
  de Participações da Campanha, que aplica a Versão anterior (FR-006).
- **Seção com duas Perguntas com regra**: estrutura não suportada; jornada e conclusão
  recusam (FR-016).
- **Resposta incoerente com a Versão** (só possível fora das operações): conclusão
  recusada (FR-045).

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII): **[Herdado]** comportamento do instrumento vigente
(inventário); **[PAEG]** com artigo; **[Const. — n]** decorre diretamente da
Constituição; **[00n FR-x]** decorre de contrato de feature anterior; **[Arquitetura]**
decisão de modelagem; **[Hipótese]** escolha reversível de produto; **[Escopo]**
delimitação desta feature.

### Functional Requirements

**Participação: rascunho e conclusão**

- **FR-001**: A Participação DEVE poder registrar um **momento de conclusão**
  (`concluida_em`). Ausente, a Participação está **em rascunho**; presente, está
  **concluída**. [Arquitetura; 005 FR-056]
- **FR-002**: NÃO DEVE existir enumeração, campo ou entidade de estado da Participação
  além do momento de conclusão. "Em rascunho" e "concluída" são derivados dele.
  [Const. — XXII]
- **FR-003**: O momento de conclusão DEVE ser registrado **uma única vez**, pela operação
  de conclusão, e NÃO DEVE ser alterado, apagado ou substituído depois. A Participação NÃO
  DEVE voltar a rascunho. [Const. — VIII]
- **FR-004**: O momento de conclusão DEVE ser o momento de referência da conclusão aceita.
  Ele é a referência temporal para interpretar as declarações consolidadas da
  Participação (005, Clarifications). O momento de início (005 FR-003) permanece
  inalterado. [Const. — I; 005 Clarifications]
- **FR-005**: NÃO DEVE ser registrado, na Participação ou fora dela: posição atual, Seção
  atual, Seções visitadas, cursor, progresso, percentual, momento por Seção ou por
  Resposta, sessão, tentativa, submissão ou histórico de conclusão. [Const. — XVI, XXII]

**Fonte única: a Versão aplicada**

- **FR-006**: Ordem de Seções e Perguntas, encaminhamentos, regras de navegação e
  obrigatoriedade DEVEM ser lidos exclusivamente da Versão aplicada pela Campanha da
  Participação. O sistema NÃO DEVE usar a versão mais recente da Pesquisa, a Versão de
  outra Campanha, configuração global ou regra fora da Versão. [Const. — VII, VIII;
  005 FR-020]
- **FR-007**: O percurso NÃO DEVE depender de dado institucional ou derivado. Dados da
  Conclusão Acadêmica NÃO DEVEM escolher, pular, antecipar ou pré-preencher Seção ou
  Pergunta (por exemplo, Q14 a partir do nível da Conclusão) (003/DP-307).
  [Const. — III]
- **FR-008**: O percurso NÃO DEVE depender de respostas de outra Participação, da mesma
  Conclusão ou de outra. [Const. — I]
- **FR-009**: Esta feature NÃO DEVE alterar a Versão aplicada nem qualquer elemento dela
  (Seções, Perguntas, Opções, obrigatoriedades, encaminhamentos, regras). [002 FR-016]

**Navegação: a Seção como unidade**

- **FR-010**: A unidade de navegação DEVE ser a **Seção**. Quando uma Seção pertence ao
  percurso, **todas** as suas Perguntas pertencem ao percurso, na ordem da Versão.
  [Herdado — inventário, "Semântica das condicionais"; Arquitetura]
- **FR-011**: A regra condicional acionada pela resposta a uma Pergunta com regra DEVE
  determinar o destino **ao final da Seção** que a contém. Ela NÃO DEVE retirar do
  percurso Perguntas posteriores da mesma Seção. [Herdado — O-15; resolve 002 FR-053 para
  a execução]
- **FR-012**: O **destino** de uma Seção DEVE ser determinado, nesta ordem:
  (a) se a Seção contém Pergunta com regra, essa Pergunta tem Resposta e a Opção
  respondida tem regra, o destino é a Seção indicada ou a finalização;
  (b) se a Pergunta com regra é **obrigatória** e não tem Resposta, o destino **ainda não
  está determinado**;
  (c) senão (sem Pergunta com regra, Opção respondida sem regra, ou Pergunta com regra
  opcional sem Resposta), se a Seção tem encaminhamento, o destino é a Seção do
  encaminhamento;
  (d) senão, se existe Seção seguinte na ordem, é ela;
  (e) senão, é a finalização.
  [002 FR-048 a FR-054]
- **FR-013**: NÃO DEVE existir atributo, configuração, enumeração ou estratégia de
  momento de aplicação de regra, nem desvio imediato dentro da Seção. A semântica de
  FR-010 a FR-012 é a semântica de execução **suportada por esta feature** e suficiente
  para a baseline; ela NÃO DEVE ser apresentada como regra obrigatória para toda Versão
  futura. Comportamento diferente exige nova capacidade especificada explicitamente
  (DP-604). [Const. — XXII, XXIII, XXIX]

**Percurso determinado**

- **FR-014**: O **percurso determinado** DEVE ser construído assim: começa na primeira
  Seção da Versão aplicada; cada Seção alcançada pertence ao percurso; se a Seção está
  satisfeita e seu destino está determinado, o percurso segue para o destino ou termina
  em finalização; caso contrário, o percurso para nessa Seção, que é a **Seção atual**.
  [Arquitetura]
- **FR-015**: Como a Versão aplicada é PUBLICADA, todo destino é Seção posterior
  (002 FR-055, FR-059 d) e todo percurso termina. Esta feature NÃO DEVE criar detecção de
  ciclos, retorno a Seção anterior ou repetição de Seção. [002 FR-055; Const. — XXII]
- **FR-016**: Se alguma Seção da Versão aplicada contém **mais de uma** Pergunta com
  regra, a Versão está fora da capacidade desta feature. A jornada DEVE indicar
  explicitamente "estrutura não suportada", identificando a Seção, e a conclusão DEVE ser
  rejeitada. O sistema NÃO DEVE escolher a primeira ou a última, usar a ordem das
  Perguntas como precedência, combinar regras, criar prioridade configurável nem
  modificar a Versão. É limitação da capacidade atual de execução, não proibição do
  modelo de instrumento da 002 (DP-604). [Const. — XXIX; 002 edge case "Mais de uma
  pergunta com regras na mesma Seção"; Clarifications]
- **FR-017**: O percurso DEVE ser **determinístico**: a mesma Versão aplicada com o mesmo
  conjunto de respostas atuais DEVE produzir o mesmo resultado, independentemente da
  ordem em que as respostas foram escritas, de alterações anteriores ou de quantas vezes
  é reconstruído. [Const. — VIII, XXVI]
- **FR-018**: O percurso DEVE ser **derivado** a cada consulta ou operação, sem ser
  persistido (FR-005). [Const. — XXII]

**Obrigatoriedade no percurso**

- **FR-019**: Uma Seção só pode ser deixada quando está **satisfeita**: todas as suas
  Perguntas obrigatórias têm Resposta. Perguntas opcionais NUNCA impedem o avanço.
  [002 FR-029, FR-031]
- **FR-020**: Perguntas obrigatórias de Seções fora do percurso NÃO DEVEM ser exigidas,
  em nenhum momento. [Escopo; Const. — XIV]
- **FR-021**: A obrigatoriedade DEVE ser a da Versão aplicada, sem relaxamento, reforço
  ou regra adicional (por exemplo, Q42 e Q44 continuam opcionais — 003/DP-304). NÃO DEVEM
  ser criadas condições entre respostas (exclusividade, coerência, mínimo ou máximo de
  seleções). [Const. — XIII; 002/DP-005]

**Q1 — finalização da jornada (não consentimento)**

- **FR-022**: Na baseline, Q1 = "Não" DEVE finalizar a jornada ao deixar S1, pela regra
  "finalizar" da Opção; Q1 = "Sim" leva a S2. Nenhuma regra especial para Q1 DEVE ser
  criada: é a aplicação de FR-012 à Versão. [Herdado — Q1; 003 FR-023]
- **FR-023**: Com Q1 = "Não", a Participação PODE ser concluída apenas com a Resposta a
  Q1; nenhuma Pergunta posterior é exigida, e Respostas posteriores existentes são
  removidas na conclusão (FR-032). [Herdado — O-17]
- **FR-024**: **Finalização da jornada ≠ consentimento juridicamente operacional.** A
  resposta a Q1 DEVE continuar Resposta comum de escolha única (005 FR-057). O sistema NÃO
  DEVE registrar, a partir de Q1, consentimento, recusa jurídica, termo aceito,
  opt-out, bloqueio de Participações futuras ou qualquer efeito fora desta Participação.
  A base legal e a forma do consentimento continuam pendentes (005/DP-504; 002/DP-007).
  [Const. — XVI, XVII, XXIX]

**Q46–Q48 e Q51 na baseline**

- **FR-025**: Na baseline, Q46, Q47 e Q48 DEVEM ser apresentadas juntas em S11. A
  resposta a Q46 DEVE determinar o destino (S12 ou S13) somente ao deixar S11. Q47
  (obrigatória) DEVE ser exigida de todo percurso que inclui S11; Q48 (opcional) NUNCA DEVE
  ser exigida. Q47 e Q48 NÃO DEVEM ser retiradas do percurso. [Herdado — O-15; 003/DP-302,
  tratamento provisório]
- **FR-026**: Na baseline, a saída de S12 DEVE seguir o encaminhamento da Seção (S13).
  NÃO DEVE ser recriada regra para Q51 nem tratamento especial para qualquer Opção dela.
  [003 FR-024, E-07]
- **FR-027**: Para a baseline, os percursos finais possíveis DEVEM ser exatamente os 17
  da tabela "Percursos esperados" da 003. [003, Percursos esperados]

**Complemento de "Outro:"**

- **FR-028**: Para concluir, o complemento de "Outro:" NÃO DEVE ser exigido: uma
  Pergunta respondida com "Outro:" sem complemento está respondida (005 FR-031). A
  jornada NÃO DEVE criar regra nova de complemento (DP-602). [Escopo; Hipótese]
- **FR-029**: As regras de complemento da 005 (FR-029, FR-030) continuam valendo para as
  escritas. [005 FR-029, FR-030]

**Respostas fora do percurso**

- **FR-030**: Durante o rascunho, Respostas fora do percurso determinado DEVEM
  permanecer gravadas e são **inativas** para a jornada: elas NÃO DEVEM satisfazer
  obrigatoriedade, gerar pendência, interferir na determinação de destino, tornar Seção
  satisfeita ou não satisfeita, permitir conclusão nem ser tratadas como apresentadas no
  percurso atual. Elas DEVEM ser identificadas como fora do percurso na consulta da
  jornada. Se a Seção voltar ao percurso, elas voltam a ser ativas sem nova escrita.
  "Ativa"/"inativa" NÃO DEVE ser gravado (nem coluna, flag ou estado na Resposta): é
  derivado do percurso. [Clarifications; Const. — XIV, XXII]
- **FR-031**: As escritas de resposta da 005 continuam aceitando qualquer Pergunta da
  Versão aplicada, dentro ou fora do percurso (005 FR-038). Esta feature NÃO DEVE
  restringi-las ao percurso. [Escopo; 005 FR-038]
- **FR-032**: Ao concluir, todas as Respostas a Perguntas fora do **percurso final** DEVEM
  ser removidas, na mesma operação atômica que registra o momento de conclusão. A
  Participação concluída DEVE conter somente Respostas a Perguntas do percurso final.
  [Arquitetura; Const. — VIII, XVI]
- **FR-033**: NÃO DEVE existir histórico, cópia, marcação de ramo abandonado ou registro
  das Respostas removidas. Conclusão rejeitada NÃO DEVE remover nada. Rascunhos nunca
  concluídos PODEM manter Respostas inativas; NÃO DEVE ser criado mecanismo de expiração
  ou limpeza automática (005/DP-503). [Const. — XVI, XXII; Clarifications]

**Concluir**

- **FR-034**: A operação de conclusão DEVE receber uma Participação e só DEVE concluí-la
  se, no momento de referência, todas as condições forem satisfeitas:
  (a) a Participação existe e está em rascunho;
  (b) a Campanha admite coleta (EM COLETA — 004 FR-038; 005 FR-039);
  (c) a Versão aplicada está dentro da capacidade desta feature (FR-016);
  (d) a jornada está finalizada, o que implica todas as Seções do percurso final
  satisfeitas;
  (e) todas as Respostas do percurso final são coerentes com a Versão aplicada (FR-045).
  [Escopo; Const. — VIII]
- **FR-035**: Conclusão aceita DEVE, atomicamente: remover as Respostas fora do percurso
  final (FR-032); registrar o momento de conclusão (FR-004); preservar sem alteração as
  Respostas do percurso final, a Campanha, a Conclusão e o momento de início.
  [Arquitetura]
- **FR-036**: Solicitar a conclusão de Participação já concluída DEVE devolver a
  Participação com a indicação de que ela já estava concluída, em qualquer estado da
  Campanha, sem alterar o momento de conclusão, sem reexecutar a remoção de Respostas,
  sem regravar Respostas e sem produzir nova submissão. [Arquitetura; Clarifications]
- **FR-037**: Conclusão rejeitada NÃO DEVE alterar nada e DEVE identificar **todas** as
  condições não satisfeitas entre (b), (c), (d) e (e). Para (d), DEVE identificar a Seção
  atual e suas Perguntas obrigatórias pendentes, ou que o destino da Seção atual ainda
  não está determinado. [Const. — XXVI]

**Imutabilidade após a conclusão**

- **FR-038**: Depois da conclusão, registrar, substituir ou remover Resposta DEVE ser
  rejeitado, indicando que a Participação está concluída, **mesmo com a Campanha EM
  COLETA**. A rejeição DEVE ser atômica e sem alteração. É a extensão prevista por
  005 FR-056 das operações de escrita da 005. [Const. — VIII; 005 FR-056]
- **FR-039**: NÃO DEVE existir operação de reabertura, desfazer conclusão, edição
  pós-conclusão, retificação, nova tentativa ou segunda submissão (DP-603). [Escopo]
- **FR-040**: A indicação de que a Participação admite escrita (005 FR-048) DEVE ser
  falsa para Participação concluída, qualquer que seja o estado da Campanha.
  [Arquitetura; 005 FR-048]
- **FR-041**: O início repetido da 005 para o par de uma Participação concluída DEVE
  devolver essa mesma Participação como "já existente", sem alteração (005 FR-013). NÃO
  DEVE ser criada outra Participação para o par. [005 FR-006, FR-013]

**Campanha sem coleta**

- **FR-042**: Participação em rascunho NÃO DEVE ser concluída depois que a Campanha deixa
  de admitir coleta. NÃO DEVE existir prazo de graça, tolerância ou exceção (005/DP-502).
  Participações em rascunho de Campanha encerrada NÃO DEVEM ser concluídas, expiradas ou
  alteradas automaticamente (005 FR-040; 005/DP-503). Participações concluídas DEVEM
  continuar integralmente consultáveis. [Const. — VIII, XXIX]

**Concorrência, coerência e rejeições**

- **FR-043**: Conclusão e escritas de resposta da mesma Participação DEVEM ser
  serializadas: uma escrita ocorre inteiramente antes da conclusão (e é considerada por
  ela) ou é rejeitada por Participação concluída. Conclusões simultâneas DEVEM resultar
  em exatamente um momento de conclusão. [Arquitetura; 005 FR-053]
- **FR-044**: A conclusão DEVE ser atômica: aceita por inteiro ou rejeitada sem nenhuma
  alteração. [Const. — XXVI]
- **FR-045**: Antes de concluir, cada Resposta do percurso final DEVE ser verificada pelas
  regras de valor e de referência já definidas na 005 (Pergunta da Versão aplicada,
  Opção da Pergunta, forma do tipo, limites de escala, complemento). Incoerência DEVE
  rejeitar a conclusão, identificando a Pergunta e o motivo. NÃO DEVE ser criada regra de
  validação nova. [005 FR-019 a FR-030, FR-054]
- **FR-046**: Rejeições e consultas NÃO DEVEM conter valores declarados (texto, inteiro,
  complemento) nem dados pessoais; podem citar motivo, Seção, Pergunta e identificadores
  técnicos. [Const. — XVI; 005 FR-059]

**Consulta da jornada**

- **FR-047**: Para uma Participação, DEVE ser possível consultar, em qualquer estado da
  Campanha e da Participação:
  (a) a Versão aplicada;
  (b) se está em rascunho ou concluída e, se concluída, o momento de conclusão;
  (c) o percurso determinado: as Seções, na ordem do percurso, e para cada uma suas
  Perguntas, na ordem da Versão, com as Respostas atuais (005 FR-047);
  (d) para cada Seção do percurso: se está satisfeita, quais obrigatórias estão
  pendentes e o destino (Seção, finalização ou ainda não determinado);
  (e) a Seção atual, ou que a jornada está finalizada;
  (f) as Respostas fora do percurso determinado;
  (g) se a Participação pode ser concluída agora e, se não, as condições não satisfeitas
  entre (b), (c) e (d) de FR-034; a coerência das Respostas (FR-034 e; FR-045) só pode
  falhar por escrita fora das operações e é verificada apenas na conclusão;
  (h) se admite escrita agora (FR-040);
  (i) a indicação de estrutura não suportada, quando for o caso (FR-016).
  [Arquitetura; Const. — XIV]
- **FR-048**: Para uma Participação concluída, a consulta DEVE refletir o percurso final:
  jornada finalizada, nenhuma Resposta fora do percurso, nenhuma pendência. [Const. — VIII]
- **FR-049**: Consultas NÃO DEVEM gravar nada nem produzir HTML, modelo de tela,
  ViewModel, progresso ou percentual. [Escopo; Const. — XXII]
- **FR-050**: A consulta DEVE manter a distinção de origem da 005: valores de Resposta são
  declarados; o contexto acadêmico vem da Conclusão e é institucional (005 FR-044).
  [Const. — III]

**Fronteiras**

- **FR-051**: A jornada DEVE receber uma Participação já identificada. NÃO DEVEM ser
  implementados login, token, OTP, cookie, sessão, SSO, Gov.br, seleção de Pessoa, seleção
  de Conclusão ou seleção de Campanha (004/DP-406). [Const. — XV; Escopo]
- **FR-052**: NÃO DEVEM ser criados, como entidade, modelo ou estado **persistido**:
  Journey, JourneyState, Session, Attempt, Step, Progress, Transition, RuleEngine,
  Workflow, Submission ou equivalentes; nem motor genérico de regras, expressões ou
  linguagem de condições. Valores **imutáveis de leitura**, recalculados a cada consulta a
  partir da Versão aplicada e das Respostas atuais e nunca gravados (no padrão de
  `ConteudoVersao` da 002 e `Elegibilidade` da 004), são permitidos para devolver o
  resultado da derivação. [Const. — XXII, XXIII]
- **FR-053**: Esta feature NÃO DEVE alterar modelos, operações, contratos ou dados das
  Features 001, 002, 003 e 004. Da Feature 005, DEVE alterar somente o que ela previu em
  FR-056: o momento de conclusão da Participação (FR-001), a rejeição de escrita após a
  conclusão (FR-038) e a indicação de escrita admitida (FR-040). Os demais requisitos da
  005 permanecem. [Escopo; 005 FR-056]
- **FR-054**: Capacidades de jornada e de conclusão são do domínio; NÃO DEVEM ser
  expostas a usuários ou perfis nem receber interface, URL ou API nesta feature
  (005/DP-505). [Const. — X, XVI]

### Key Entities *(include if feature involves data)*

- **Participação** *(005, ampliada)*: ganha o **momento de conclusão** (`concluida_em`),
  opcional e gravado uma única vez. Ausente = em rascunho; presente = concluída. Nenhum
  outro atributo novo.
- **Resposta** *(005, inalterada na forma)*: depois da conclusão, não pode ser registrada,
  substituída nem removida. Na conclusão, as que estão fora do percurso final são
  removidas.
- **Campanha** *(004, inalterada)*: fornece a Versão aplicada e o estado temporal (coleta
  admitida ou não).
- **Versão, Seção, Pergunta, Opção** *(002, inalteradas)*: ordem, encaminhamento de
  Seção, regras "ir para Seção | finalizar" nas Opções e obrigatoriedade — a única fonte
  do percurso.
- **Conclusão Acadêmica, Pessoa** *(001, inalteradas)*: não influenciam o percurso.

**Conceitos derivados, não persistidos**: percurso determinado, Seção atual, destino da
Seção, Seção satisfeita, pendências, jornada finalizada, percurso final, Resposta fora do
percurso, "pode concluir".

**Entidades deliberadamente não criadas**: Journey/Jornada, JourneyState, Session/Sessão,
Attempt/Tentativa, Step/Passo, Progress/Progresso, Transition/Transição, RuleEngine,
Workflow, Submission/Submissão, Cursor/Posição, histórico de ramos, histórico de
conclusão, estado enumerado da Participação, Consentimento.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| Momento de conclusão | Registro do sistema | Momento de referência da conclusão aceita (FR-004) | Não se aplica; imutável (FR-003) |
| Rascunho / concluída | Derivado | Presença do momento de conclusão (FR-001) | Não persistido além do momento |
| Percurso, Seção atual, destinos, pendências, jornada finalizada | Derivado | Versão aplicada + respostas atuais (FR-012, FR-014) | Não persistido |
| Respostas fora do percurso | Derivado (classificação) | Seção da Pergunta fora do percurso determinado (FR-030) | Removidas na conclusão (FR-032) |
| Pode concluir / admite escrita | Derivado | Estado da Campanha (004) + momento de conclusão + percurso | Não persistido |
| Valores das Respostas, inclusive Q1 | **Declarado** | 005, sem alteração | Coexistem com o institucional, sem sobrescrita (005 FR-043; 005/DP-508) |
| Contexto acadêmico | Institucional | Conclusão Acadêmica (001) | Não usado no percurso (FR-007) |

### Modelo conceitual

```text
Participação (005)
  ├─ Campanha ─► Versão aplicada (PUBLICADA, imutável)
  ├─ iniciada_em                (005)
  ├─ concluida_em  0..1         (006)   ausente → rascunho | presente → concluída
  └─ Respostas atuais 0..N      (005)

percurso(Participação) — derivado, nunca gravado:
  S ← primeira Seção da Versão aplicada
  repetir:
    S pertence ao percurso (todas as suas Perguntas pertencem ao percurso)
    se S não está satisfeita            → Seção atual = S; parar
    d ← destino(S)
    se d indeterminado                  → Seção atual = S; parar
    se d = finalização                  → jornada finalizada; parar
    S ← d

destino(S):
  X ← Pergunta com regra de S (no máximo uma — senão "estrutura não suportada")
  X respondida e Opção com regra        → Seção da regra | finalização
  X obrigatória e sem Resposta          → indeterminado
  S tem encaminhamento                  → Seção do encaminhamento
  existe Seção seguinte na ordem        → ela
  senão                                 → finalização

concluir(Participação):
  já concluída                          → "já concluída"; nada muda
  Campanha não EM COLETA                ┐
  estrutura não suportada               ├→ rejeita com todas as condições; nada muda
  jornada não finalizada (pendências)   │
  Resposta do percurso incoerente       ┘
  senão, atomicamente:
    remove Respostas fora do percurso final
    concluida_em ← momento de referência

escritas da 005 (registrar | substituir | remover):
  Participação concluída                → rejeita ("Participação concluída")
  senão                                 → regras da 005, inalteradas
```

**Baseline (Versão de teste equivalente) — percursos finais**:

```text
Q1 = Não → S1 → fim                                                    (1)
Q1 = Sim → S1 → S2 → S3 → {S4|S5|S6|S7}ᵠ¹⁴ → S8 → {S9|S10}ᵠ³³ → S11
           → {S12 → S13 | S13}ᵠ⁴⁶ → fim                               (16)
S11 sempre apresenta Q46, Q47 (obrigatória) e Q48 (opcional).
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Para as 17 combinações de respostas a Q1, Q14, Q33 e Q46 na Versão de teste
  equivalente à baseline, 100% dos percursos finais reconstruídos coincidem com os 17
  percursos esperados da 003.
- **SC-002**: Em 100% dos percursos que incluem S11, inclusive com Q46 = "Não", Q46, Q47 e
  Q48 pertencem ao percurso; a conclusão sem Q47 é rejeitada em 100% dos casos, e a
  conclusão sem Q48 é aceita quando o restante está completo.
- **SC-003**: Para cada percurso final de referência, omitir qualquer uma das Perguntas
  obrigatórias do percurso impede a conclusão e a rejeição aponta exatamente a pendência;
  com todas respondidas, a conclusão é aceita em 100% dos casos.
- **SC-004**: Em 100% dos casos de teste, nenhuma Pergunta obrigatória de Seção fora do
  percurso aparece como pendência ou impede a conclusão (por exemplo, Q34–Q44 com
  Q33 = "Não"; Q49–Q51 com Q46 = "Não"; Q2–Q54 com Q1 = "Não").
- **SC-005**: Depois da conclusão, 100% das tentativas de registrar, substituir ou remover
  Resposta, nos quatro tipos, são rejeitadas, inclusive com a Campanha EM COLETA, e as
  Respostas e o momento de conclusão permanecem idênticos após 2 ou mais solicitações
  repetidas de conclusão.
- **SC-006**: Em sequências de troca de ramo seguidas de conclusão, a Participação
  concluída tem zero Respostas a Perguntas fora do percurso final e 100% das Respostas do
  percurso final idênticas às existentes antes da conclusão.
- **SC-007**: Com Q1 = "Não", a conclusão é aceita e a Participação concluída tem
  exatamente 1 Resposta, mesmo quando havia Respostas posteriores no rascunho.
- **SC-008**: Depois do encerramento da Campanha, explícito ou por data, 100% das
  tentativas de concluir são rejeitadas sem alteração, e 100% das Participações já
  concluídas continuam consultáveis com o mesmo momento de conclusão.
- **SC-009**: Reconstruir a jornada da mesma Participação 2 ou mais vezes, ou de duas
  Participações com as mesmas respostas escritas em ordens diferentes, produz resultados
  idênticos em 100% dos casos, e nenhuma consulta grava dado.
- **SC-010**: Publicar uma Versão posterior da mesma Pesquisa não altera o percurso, as
  pendências nem a possibilidade de conclusão de nenhuma Participação de Campanha que
  aplica a Versão anterior.
- **SC-011**: Conclusões simultâneas, ou conclusão simultânea a escritas, resultam sempre
  em exatamente 1 momento de conclusão e em nenhuma Resposta gravada depois dele.
- **SC-012**: Ao final da feature, o único dado novo persistido é o momento de conclusão
  da Participação; não existe entidade, campo ou registro de sessão, tentativa, posição,
  progresso, transição, submissão, workflow, histórico de ramo ou estado enumerado, e
  nenhum dado ou contrato das Features 001 a 004 foi alterado.

## Assumptions

- **Versão de teste equivalente à baseline**: enquanto a baseline estiver em RASCUNHO
  (002/DP-001), os testes de fidelidade usam uma Versão PUBLICADA apenas no ambiente de
  teste, com estrutura equivalente à baseline. O plan define como obtê-la. Isso não
  publica nada institucionalmente.
- **Toda Seção da baseline tem ao menos uma Pergunta obrigatória** (003, Matriz de
  Migração): por isso, a reconstrução da Seção atual sem cursor é exata para a baseline.
  Para Versões futuras com Seção sem obrigatórias, essa Seção não vira Seção atual na
  reconstrução; a interface futura pode apresentá-la percorrendo o percurso determinado.
  [Hipótese]
- **Perguntas com regra da baseline são obrigatórias** (Q1, Q14, Q33, Q46): o caso
  "Pergunta com regra opcional sem resposta" segue 002 FR-054 e não ocorre na baseline.
- **Respostas fora do percurso mantidas até a conclusão**: preferido a removê-las a cada
  troca de ramo porque (a) com o percurso ainda incompleto não é possível saber se uma
  resposta adiante deixará de valer; (b) evita redigitação ao voltar ao ramo
  (Princípio XIV); (c) concentra a remoção num único ponto determinístico. Confirmado em
  Clarifications; ver "Tensões identificadas".
- **Conclusão idempotente**: escolhida em vez de rejeição, para que a futura interface
  possa repetir a solicitação sem efeito, como no início da 005. Confirmado em
  Clarifications.
- **Elegibilidade não é reavaliada na conclusão**: a elegibilidade é gate de entrada da
  Participação (005, Clarifications); concluir exige apenas coleta admitida.
- **Momento de referência**: como na 004 e na 005, é o instante da operação, na timezone
  configurada do projeto; o plan define como substituí-lo em testes.
- **Somente dados fictícios**: enquanto base legal, consentimento e retenção não forem
  definidos (005/DP-504), a feature é exercida apenas com a fonte simulada e respostas
  fictícias.

## Relação com outras features

**001** — consumida sem alteração; a Conclusão não influencia o percurso (FR-007).

**002** — consumida sem alteração. A 006 **executa** o que a 002 apenas descrevia:
fluxo padrão (FR-048), encaminhamento (FR-049), regras e precedência (FR-050 a FR-054),
garantia de término (FR-055). Resolve para a execução o momento de aplicação deixado em
aberto por FR-053: ao sair da Seção, sem atributo configurável. Mantém a restrição de
FR-056/FR-057 (sem motor de regras, sem condição de exibição).

**003** — consumida sem alteração. A 006 reproduz os 17 percursos esperados, mantém
Q47/Q48 em S11 (tratamento provisório de DP-302: não suprimir sem decisão explícita),
não recria regra para Q51 (E-07) e finaliza por Q1 = "Não". A pergunta metodológica de
DP-302 — se apresentar Q47/Q48 a todos é **intenção** ou acidente — continua com a CPAEG.
A 003 mencionava a "004" como responsável pela execução; a execução coube à 006.

**004** — consumida sem alteração: estado temporal da Campanha decide se a conclusão é
admitida (FR-034 b, FR-042).

**005** — ampliada somente onde ela mesma previu (005 FR-056):

- Participação ganha o momento de conclusão (supera, como previsto, a exclusão de
  "momento de conclusão" em 005 FR-003 e FR-055);
- escritas de resposta passam a rejeitar Participação concluída (FR-038);
- "admite escrita" considera a conclusão (FR-040).

Permanecem inalterados: unicidade por par, início idempotente, validação de valor por
tipo, complemento opcional, ausência de histórico, ausência de restrição de escrita por
percurso (005 FR-038), Q1 como Resposta comum (005 FR-057).

**Futuras** — a interface pública da jornada consumirá a consulta da jornada (FR-047) e a
conclusão; autenticação e identificação do egresso (próxima feature) entregarão a
Participação já identificada (FR-051).

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade (NON-NEGOTIABLE)**: a Participação ganha a referência temporal
  das declarações consolidadas (FR-004). Concluir uma Participação não altera nenhuma
  outra (FR-008, FR-053), e o início repetido nunca cria segunda Participação (FR-041).
- **III — Institucional ≠ declarado (NON-NEGOTIABLE)**: o percurso depende só de
  respostas declaradas e da Versão; nenhum dado da Conclusão escolhe, pula ou
  pré-preenche Seção ou Pergunta (FR-007). A distinção de origem continua na consulta
  (FR-050).
- **VII — Pesquisa, Versão, Campanha e Participação distintas (NON-NEGOTIABLE)**: o
  percurso é da Participação, a estrutura é da Versão aplicada pela Campanha (FR-006);
  nenhuma Jornada/Sessão funde esses conceitos (FR-052).
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: percurso pela Versão histórica,
  imutável (FR-006, FR-009); momento de conclusão gravado uma vez (FR-003); Participação
  concluída imutável (FR-038, FR-039); encerramento não apaga nem altera nada (FR-042).
- **XIII — Instrumento atual como referência**: preserva as condicionais relevantes (Q1,
  Q14, Q33, Q46) e o comportamento observado de S11, sem suprimir Q47/Q48 nem declarar que
  ele é a intenção metodológica (FR-010, FR-011, FR-025; 003/DP-302). Não recria a regra
  sem efeito de Q51 (FR-026).
- **XIV — Redução de fricção**: só se exige o que é apresentado (FR-020); obrigatórias
  fora do percurso nunca bloqueiam; trocar de ramo e voltar não obriga a redigitar
  (FR-030); retomar não depende de sessão (US8).
- **XV — Autenticação substituível**: nada nesta feature depende de mecanismo de
  identificação (FR-051).
- **XVI — Privacidade e minimização (NON-NEGOTIABLE)**: a Participação concluída guarda só
  o percurso final (FR-032); nada de posição, sessão ou metadados (FR-005); sem valores
  em rejeições (FR-046); sem exposição (FR-054).
- **XVII — Consentimento**: Q1 continua Resposta comum; finalizar a jornada não é
  consentimento (FR-024). Nada impede feature própria de relacionar termo, momento,
  Participação e manifestação.
- **XXII — Simplicidade e YAGNI**: um único dado novo, uma única operação nova de escrita
  (concluir), comportamento derivado; nenhum motor, workflow ou entidade de jornada
  (FR-002, FR-005, FR-052). Estrutura fora da baseline é recusada, não generalizada
  (FR-016).
- **XXIII — Não é form builder universal**: sem condição de exibição, sem expressões, sem
  momento de aplicação configurável (FR-013, FR-021, FR-052).
- **XXIX — Hipóteses explícitas (NON-NEGOTIABLE)**: consentimento, edição pós-conclusão,
  prazo de graça, abandono, complemento obrigatório, interpretação da recusa e semântica
  de Versões futuras ficam como `DECISÃO PENDENTE`; escolhas reversíveis estão marcadas
  [Hipótese].

**Tensões identificadas (não são conflitos)**:

- **XIII × adotar o comportamento do Google Formulários**: o inventário descreve a
  aplicação ao sair da Seção como "comportamento observado da ferramenta, não regra a
  reproduzir". Esta spec não afirma que ele é a intenção do instrumento; adota-o como
  semântica de **execução** da baseline porque é o que preserva comparabilidade com as
  respostas já coletadas e porque o tratamento provisório de 003/DP-302 proíbe suprimir
  Q47/Q48 sem decisão explícita. Mudança exige decisão da CPAEG e nova capacidade
  (DP-604).
- **VIII × remover Respostas fora do percurso na conclusão**: as Respostas removidas são
  valores de rascunho de Perguntas que não pertencem ao percurso final, ou seja, nunca
  integram a declaração consolidada. Isso segue a interpretação confirmada na 005:
  dentro da mesma Participação em preenchimento, alterar e remover é esperado, sem
  histórico. Depois da conclusão, nada é removido.
- **XVI × manter Respostas fora do percurso durante o rascunho**: uma Participação em
  rascunho nunca concluída pode guardar respostas de ramos abandonados — inclusive
  respostas sensíveis (Q2, Q4–Q6) dadas antes de trocar Q1 para "Não". O destino dessas
  Participações é 005/DP-503; o uso com dados reais segue bloqueado por 005/DP-504.
- **Direito de correção do titular × imutabilidade após a conclusão**: a imutabilidade é
  regra desta feature; como tratar pedidos de correção de dados declarados é DP-603.

Nenhum conflito com a Constituição ou com as Features 001 a 005 foi identificado. A
alteração da 005 limita-se ao ponto de extensão que ela própria previu (005 FR-056).

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. Pertence de fato ao domínio de acompanhamento? Sim. "Participação em Pesquisa e
   Respostas" e a aplicação do instrumento versionado estão na Fronteira do Domínio.
2. É necessária ao ciclo de acompanhamento? Sim. Sem conclusão, nenhuma observação é
   consolidada.
3. Existe ou está prevista solução institucional mais adequada? Não para executar a
   Versão histórica sobre a Participação. Identificação e autenticação ficam fora
   (FR-051).
4. Integração seria suficiente? Não para a jornada; sim, no futuro, para identidade.
5. A incorporação aumentaria desnecessariamente o acoplamento do núcleo? Não. A jornada
   depende apenas da Versão (002), da Campanha (004) e da Participação e Respostas (005).

## Out of Scope *(mandatory)*

- Autenticação, token, OTP, cookie, sessão, Gov.br, SSO; identificação do egresso;
  seleção de Pessoa, de Conclusão (formação) ou de Campanha.
- Página pública, HTML, CSS, telas, URL, API, ViewModel.
- Progresso, percentual, barra de progresso, estimativa de tempo.
- Editor administrativo; alteração de Pesquisa ou Versão; publicação da baseline.
- Dashboard, indicadores (concluídos, taxa de resposta), GeN, exportação.
- Comunicação, convite, lembrete.
- Integração acadêmica real; pré-preenchimento ou supressão de Perguntas por dado
  institucional (003/DP-307).
- Política definitiva de consentimento; termo versionado; efeito jurídico de Q1.
- Prazo de graça; reabertura de Participação; edição ou retificação pós-conclusão.
- Histórico de respostas, de ramos ou de conclusão; auditoria por edição.
- Desvio imediato dentro da Seção; várias Perguntas com regra na mesma Seção; condição de
  exibição por Pergunta; exclusividade ou coerência entre respostas.
- Tratamento de abandono, expiração ou remoção de Participações em rascunho.
- Qualquer alteração das Features 001 a 004.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: decisões novas usam o prefixo 6 (DP-601…). As das features anteriores são
citadas como 00n/DP-nnn.

**Novas nesta feature**

- **DP-601** — DECISÃO PENDENTE: interpretação operacional e analítica de Participação
  concluída por recusa (Q1 = "Não"): se conta como "concluída", "recusa" ou outra
  categoria em acompanhamento da coleta e indicadores, e se tem algum efeito sobre
  Participações em outras Campanhas. Instância competente: CPAEG/Proex, com o encarregado
  de dados. Impacto: FR-023, FR-024; indicadores futuros (Princípio XIX). Tratamento
  provisório: Participação concluída com uma única Resposta; a recusa é apenas o valor
  declarado de Q1; nenhum efeito fora da Participação.
- **DP-602** — DECISÃO PENDENTE: se, ao selecionar "Outro:" (Q26, Q32, Q45), o
  complemento textual deve ser exigido para concluir. O inventário não registra esse
  comportamento no instrumento vigente. Instância competente: CPAEG. Impacto: FR-028.
  Tratamento provisório: complemento opcional, como na 005.
- **DP-603** — DECISÃO PENDENTE: se e como uma Participação concluída pode ser corrigida
  (pedido do egresso, retificação por direito do titular, erro operacional), com que
  preservação do valor original. Instância competente: CPAEG, com o encarregado de dados.
  Impacto: FR-003, FR-038, FR-039; Princípios VIII e XVI. Tratamento provisório:
  Participação concluída imutável; nenhuma operação de reabertura ou edição.
- **DP-604** — DECISÃO PENDENTE: se Versões futuras precisarão de desvio imediato dentro
  da Seção, de mais de uma Pergunta com regra na mesma Seção, ou de outra semântica de
  navegação — inclusive a resposta metodológica de 003/DP-302 (se apresentar Q47/Q48 a
  quem estuda é intenção do instrumento). Instância competente: CPAEG (necessidade
  metodológica), seguida de spec própria (capacidade). Impacto: FR-010 a FR-013, FR-016.
  Tratamento provisório: Seção como unidade de navegação; regra aplicada ao sair da
  Seção; estrutura fora disso não é executada.

**Herdadas e afetadas por esta feature**

- **005/DP-502** — prazo de graça: agora também para concluir. Tratamento provisório
  mantido: nenhuma conclusão depois do fim da coleta (FR-042).
- **005/DP-503** — destino das Participações não concluídas: agora inclui as Respostas
  fora do percurso que permanecem em rascunhos nunca concluídos (Tensões identificadas).
  Tratamento provisório mantido: preservadas, sem remoção automática.
- **005/DP-504** e **002/DP-007** — base legal, consentimento e termo: Q1 continua Resposta
  comum; finalizar a jornada não é consentimento (FR-024). **Bloqueia o uso com dados
  reais.**
- **003/DP-302** — parte de execução resolvida por esta feature (Seção como unidade; regra
  ao sair da Seção); parte metodológica segue aberta em DP-604.

**Encaminhadas a features futuras** (escopo de feature, não regra institucional)

- Progresso exibido na interface, se houver, derivado do percurso e sem persistência.
- Interface pública da jornada, acessibilidade e responsividade (Princípios XX e XXI).
- Autenticação e identificação do egresso, com escolha de Conclusão e de Campanha
  (004/DP-406; 005/DP-501; 004/DP-404).
- Indicadores operacionais de coleta (iniciados, concluídos) a partir de `concluida_em`.

**Herdadas e ainda abertas** (não resolvidas por esta feature)

- **002/DP-001** — competência para publicar Versão (bloqueia aplicar a baseline).
- **002/DP-006** — comparabilidade entre Versões, inclusive de percursos de Versões
  diferentes do instrumento.
- **003/DP-303** — Q6 condicional a Q5.
- **003/DP-304** — opcionalidade de Q42 e Q44.
- **003/DP-307** — supressão de Perguntas acadêmicas por contexto institucional.
- **003/DP-309** — dados potencialmente sensíveis (Q2, Q4, Q5, Q6).
- **004/DP-404** — Campanhas EM COLETA sobrepostas.
- **004/DP-406** — forma de acesso do egresso e mecanismo de identificação.
- **005/DP-501** — várias Conclusões elegíveis da mesma Pessoa na mesma Campanha.
- **005/DP-505** — quem pode consultar Participações e respostas identificadas.
- **005/DP-506** — registro de respostas por intermediário.
- **005/DP-507** — efeito de correção acadêmica sobre Participação existente.
- **005/DP-508** — divergência entre resposta declarada e dado institucional.


## Nota de revisão pela Feature 019 (2026-10-04)

FR-035 preserva Campanha e âncora, institucional ou declarada. A jornada, o percurso, as Respostas e a conclusão são reaproveitados sem regra nova; a validação não altera nenhum deles.

Referência: [019 — Formação não localizada e validação posterior](../019-formacao-declarada-validacao/spec.md).
