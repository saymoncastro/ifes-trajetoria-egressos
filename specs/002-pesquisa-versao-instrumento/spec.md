# Feature Specification: Pesquisa, versão e estrutura do instrumento

**Feature Branch**: `claude/feature-002-pesquisa-versao-6b2c5d`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "Feature 002 — Pesquisa, versão e estrutura do instrumento.
Estabelecer o modelo canônico do instrumento de pesquisa do NIAE: Pesquisa → Versão da
Pesquisa → Seções → Perguntas → Opções → regras mínimas de navegação condicional, de forma
estruturada, versionável e historicamente preservável, suficiente para que a Feature 003
migre semanticamente o Formulário Egresso do Ifes 2024. Sem cadastrar o formulário atual,
sem respostas, sem Campanhas, sem Participações e sem editor administrativo."

## Contexto

A Feature 001 estabeleceu **Pessoa → Conclusão Acadêmica** com fonte institucional
abstrata. A Constituição exige a cadeia completa **Pessoa → Conclusão Acadêmica →
Participação em Pesquisa → Respostas** (Princípio I) e determina que Pesquisa, Versão,
Campanha e Participação são conceitos distintos (Princípio VII). Toda Resposta futura
precisará permanecer associada à Versão efetivamente apresentada.

Antes de criar Campanhas ou Participações, o NIAE precisa representar de forma
historicamente estável **o instrumento que será aplicado**. Esta feature estabelece esse
modelo:

```text
Pesquisa
  └── Versão da Pesquisa (RASCUNHO | PUBLICADA)
        ├── textos da Versão (título apresentado, abertura, encerramento)
        └── Seções ordenadas
              ├── textos da Seção (título, texto introdutório)
              ├── encaminhamento da Seção (opcional)
              └── Perguntas ordenadas
                    ├── tipo, texto, texto explicativo, obrigatoriedade
                    ├── Opções ordenadas (escolha única / escolha múltipla)
                    ├── configuração de escala (escala)
                    └── regras de navegação condicional (escolha única)
```

A referência funcional é o Formulário Egresso do Ifes 2024, descrito em
`docs/referencias/formulario-egresso-ifes-2024-inventario.md` (doravante "inventário").
Esta feature modela a **intenção** do instrumento, não os acidentes do Google
Formulários, e **não** decide como cada pergunta atual será representada: isso pertence à
Feature 003 ("Migração semântica do instrumento institucional vigente").

**Termos usados nesta spec** (conceituais; a nomenclatura concreta pertence ao plan):

- **Elemento da Versão**: Seção, Pergunta, Opção, configuração de escala, regra de
  navegação condicional, encaminhamento de Seção e textos da Versão.
- **Conteúdo da Versão**: o conjunto de todos os elementos da Versão, com seus textos,
  tipos, obrigatoriedades, ordens e referências. É o que precisa ser preservado para
  interpretar respostas futuras.
- **Alteração material**: qualquer alteração do conteúdo da Versão. Enquanto a política
  de correções editoriais estiver pendente (DP-003), **toda** alteração do conteúdo de
  uma Versão publicada é tratada como material.
- **Percurso de Seções**: a sequência de Seções que um respondente futuro percorreria
  conforme a ordem, os encaminhamentos e as regras. Nesta feature ele é apenas
  **descrito** pela estrutura; não é executado. Em que momento da jornada uma regra
  acionada é aplicada — e, portanto, se as Perguntas posteriores a X na mesma Seção são
  apresentadas — **não** é definido por esta feature (FR-053).
- **Finalização**: término do percurso do instrumento. Após a finalização, nenhuma outra
  Seção é apresentada; o texto de encerramento da Versão, se houver, é o que encerra o
  instrumento.

## User Scenarios & Testing *(mandatory)*

Os "usuários" desta feature são as **funcionalidades consumidoras do NIAE** — em
primeiro lugar a Feature 003, que representará o instrumento vigente com esta estrutura,
e depois Campanha, jornada de resposta e exportação — e quem as desenvolve e testa. Esta
feature não tem interface com o egresso nem com gestores. As operações descritas são
capacidades do domínio.

### User Story 1 - Criar uma Pesquisa e uma primeira Versão em rascunho (Priority: P1)

Uma funcionalidade consumidora precisa registrar o instrumento lógico "Pesquisa
Institucional de Egressos" e iniciar a preparação de uma Versão dele, ainda editável.

**Why this priority**: é a menor fatia que materializa a distinção entre Pesquisa e
Versão (Princípio VII), da qual todas as demais histórias dependem.

**Independent Test**: criar uma Pesquisa e duas Versões em rascunho e verificar que são
entidades distintas, que ambas as Versões pertencem à mesma Pesquisa e que nenhuma
Pessoa ou Conclusão Acadêmica precisa existir.

**Acceptance Scenarios**:

1. **Given** nenhuma Pesquisa existente, **When** uma Pesquisa é criada com um nome
   administrativo, **Then** ela passa a existir com identidade própria e sem nenhuma
   Versão.
2. **Given** uma Pesquisa existente, **When** uma Versão é criada para ela com uma
   designação (por exemplo, "2024"), **Then** a Versão tem identidade própria, pertence
   a essa Pesquisa e está em RASCUNHO.
3. **Given** uma Pesquisa com uma Versão "2024", **When** outra Versão é criada com a
   designação "2026", **Then** a Pesquisa passa a ter duas Versões distintas.
4. **Given** uma Pesquisa com uma Versão "2024", **When** se tenta criar outra Versão da
   mesma Pesquisa também designada "2024", **Then** a criação é rejeitada explicitamente.
5. **Given** um ambiente sem nenhuma Pessoa nem Conclusão Acadêmica, **When** Pesquisas e
   Versões são criadas, **Then** todas as operações funcionam normalmente.

---

### User Story 2 - Estruturar uma Versão com Seções e Perguntas ordenadas (Priority: P1)

A Versão em rascunho precisa ser organizada em Seções ordenadas, cada uma com título e
texto introdutório opcionais e com Perguntas ordenadas. A Versão também precisa preservar
seus textos de abertura e encerramento.

**Why this priority**: sem estrutura ordenada não há instrumento interpretável. A ordem é
parte do significado (Princípio VIII).

**Independent Test**: criar Seções e Perguntas em ordem de criação embaralhada, atribuir
posições explícitas e consultar a Versão. O resultado deve seguir as posições atribuídas,
e não a ordem de criação.

**Acceptance Scenarios**:

1. **Given** uma Versão em rascunho, **When** três Seções são adicionadas com posições
   explícitas, **Then** a consulta da Versão retorna as Seções na ordem dessas posições.
2. **Given** uma Seção, **When** Perguntas são adicionadas em posições explícitas,
   **Then** a consulta da Seção retorna as Perguntas na ordem dessas posições, que é
   independente da ordem de criação e de qualquer identificador.
3. **Given** uma Seção sem título, **When** ela é consultada, **Then** o título aparece
   explicitamente ausente, sem título padrão inventado.
4. **Given** uma Versão em rascunho, **When** recebe título apresentado, texto de
   abertura e texto de encerramento, **Then** esses textos são consultáveis como parte da
   Versão.
5. **Given** uma Versão em rascunho, **When** uma Seção ou Pergunta é reposicionada,
   **Then** a nova ordem é refletida na consulta sem ambiguidade.
6. **Given** uma Pergunta em uma Seção de rascunho, **When** ela é movida para outra
   Seção da mesma Versão, **Then** passa a pertencer apenas à Seção de destino.

---

### User Story 3 - Representar os quatro tipos de pergunta do instrumento atual (Priority: P1)

A Versão precisa representar perguntas de escolha única, escolha múltipla, resposta
textual curta e escala, que são os tipos de que o instrumento atual realmente precisa.

**Why this priority**: sem esses tipos a Feature 003 não consegue representar o
formulário vigente. Limitar a esses quatro evita um form builder genérico (Princípios
XXII e XXIII).

**Independent Test**: criar uma pergunta de cada tipo e verificar que cada uma aceita
apenas a configuração própria do seu tipo e que nenhum outro tipo pode ser criado.

**Acceptance Scenarios**:

1. **Given** uma Seção em rascunho, **When** uma pergunta de escolha única é criada,
   **Then** ela admite Opções ordenadas e não admite configuração de escala.
2. **Given** uma Seção em rascunho, **When** uma pergunta de escolha múltipla é criada,
   **Then** ela admite Opções ordenadas e não admite configuração de escala nem regra de
   navegação.
3. **Given** uma Seção em rascunho, **When** uma pergunta de resposta textual curta é
   criada, **Then** ela não admite Opções, configuração de escala, validação de formato
   nem regra de navegação.
4. **Given** uma Seção em rascunho, **When** uma pergunta de escala é criada com limite
   inicial 1, limite final 5 e rótulos de extremidade, **Then** esses dados são
   preservados, e a pergunta não admite Opções.
5. **Given** qualquer tentativa de criar pergunta de tipo diferente dos quatro (por
   exemplo, data, upload ou matriz), **When** a operação é executada, **Then** ela é
   rejeitada explicitamente.
6. **Given** perguntas de qualquer tipo, **When** são marcadas como obrigatórias ou
   opcionais e recebem texto explicativo, **Then** esses dados são preservados.

---

### User Story 4 - Representar Opções e escalas preservando ordem e significado (Priority: P1)

Perguntas de escolha precisam de Opções ordenadas, com identidade própria independente do
texto. Algumas opções do instrumento atual admitem complemento textual ("Outro:").
Escalas precisam preservar limites e rótulos de extremidade.

**Why this priority**: Opções e escalas carregam o significado das respostas futuras
(Princípio VIII). Sem identidade própria, a correção de um texto poderia confundir-se com
a troca de uma alternativa.

**Independent Test**: criar uma pergunta de escolha com Opções em ordem embaralhada,
uma das quais com complemento textual, e uma pergunta de escala com rótulos; consultar e
verificar ordem, textos, identidades e configuração.

**Acceptance Scenarios**:

1. **Given** uma pergunta de escolha única, **When** Opções "Sim" e "Não" são criadas com
   posições explícitas, **Then** a consulta retorna as Opções nessa ordem, cada uma com
   identidade própria dentro da Versão.
2. **Given** uma Opção existente em rascunho, **When** seu texto é alterado, **Then** ela
   mantém a mesma identidade, e as regras que a referenciam continuam válidas.
3. **Given** uma pergunta de escolha múltipla, **When** uma Opção "Outro" é marcada como
   admitindo complemento textual, **Then** essa característica é preservada e consultável.
4. **Given** uma pergunta de escala de 1 a 5 com rótulo inicial e rótulo final, **When**
   é consultada, **Then** retornam exatamente os limites e os rótulos registrados.
5. **Given** uma pergunta de escala sem rótulo inicial, **When** é consultada, **Then** o
   rótulo inicial aparece explicitamente ausente.
6. **Given** duas perguntas da mesma Versão com listas de Opções de mesmo texto (como Q8
   e Q9 do instrumento atual), **When** uma Opção de uma delas é alterada, **Then** a
   outra pergunta não é afetada.

---

### User Story 5 - Publicar uma Versão e impedir alterações materiais posteriores (Priority: P1)

Uma Versão pronta precisa ser publicada, passando a representar um instrumento
historicamente estável. Depois disso, nenhum elemento do seu conteúdo pode ser alterado.

**Why this priority**: é a garantia de preservação histórica (Princípio VIII,
NON-NEGOTIABLE) da qual dependerão Campanhas, Respostas e exportações.

**Independent Test**: publicar uma Versão completa, tentar alterar cada tipo de elemento
e verificar que todas as tentativas são rejeitadas e que o conteúdo consultado depois é
integralmente idêntico ao consultado no momento da publicação.

**Acceptance Scenarios**:

1. **Given** uma Versão em rascunho estruturalmente completa, **When** é publicada,
   **Then** passa ao estado PUBLICADA e o momento da publicação fica registrado.
2. **Given** uma Versão em rascunho incompleta (por exemplo, com pergunta de escolha sem
   Opções), **When** se tenta publicá-la, **Then** a publicação é rejeitada, todas as
   pendências são informadas com o elemento envolvido, e a Versão permanece em RASCUNHO
   e inalterada.
3. **Given** uma Versão publicada, **When** se tenta alterar texto de pergunta, Opção,
   escala, obrigatoriedade, regra, encaminhamento, ordem, texto de Seção ou texto da
   Versão, ou adicionar ou remover qualquer elemento, **Then** cada tentativa é rejeitada
   explicitamente e o conteúdo permanece integralmente idêntico.
4. **Given** uma Versão publicada, **When** se tenta devolvê-la a RASCUNHO, **Then** a
   operação é rejeitada.
5. **Given** uma Versão publicada, **When** se tenta publicá-la novamente, **Then** nada
   muda (nem o momento da publicação) e o resultado informa que ela já está publicada.
6. **Given** uma Pesquisa com uma Versão publicada, **When** o nome administrativo da
   Pesquisa é alterado, **Then** o conteúdo da Versão publicada permanece idêntico.

---

### User Story 6 - Criar nova Versão a partir de uma Versão existente (Priority: P2)

O instrumento evolui: a versão 2026 deve poder partir da 2024 sem editar
retrospectivamente o que já foi publicado.

**Why this priority**: viabiliza a evolução do instrumento sem violar a preservação
histórica. É P2 porque depende de Versões estruturadas e publicadas (US2–US5).

**Independent Test**: criar nova Versão a partir de uma Versão publicada, alterar na nova
cada tipo de elemento, e verificar que a Versão de origem continua integralmente idêntica
e que nenhum elemento é compartilhado entre as duas.

**Acceptance Scenarios**:

1. **Given** uma Versão publicada "2024", **When** uma nova Versão "2026" é criada a
   partir dela, **Then** a nova Versão pertence à mesma Pesquisa, está em RASCUNHO, tem
   identidade própria e conteúdo equivalente ao da origem.
2. **Given** a nova Versão "2026", **When** seus elementos são consultados, **Then**
   todas as Seções, Perguntas e Opções têm identidades próprias, distintas das de "2024".
3. **Given** a nova Versão "2026", **When** suas regras de navegação são consultadas,
   **Then** cada regra referencia a Pergunta, a Opção e a Seção correspondentes **da
   própria Versão "2026"**, e nunca elementos de "2024".
4. **Given** a nova Versão "2026", **When** um texto de pergunta, uma Opção, uma escala
   e uma regra são alterados, **Then** a Versão "2024" permanece integralmente idêntica.
5. **Given** a nova Versão "2026", **When** sua origem é consultada, **Then** é possível
   saber que ela foi criada a partir de "2024".

---

### User Story 7 - Representar navegação condicional simples entre Seções (Priority: P2)

O instrumento atual tem ramificações: conforme a resposta a uma pergunta de escolha única,
o percurso segue para Seções diferentes, e depois converge. A Versão precisa representar
essa intenção sem executar a navegação.

**Why this priority**: as ramificações são parte do significado metodológico do
instrumento (Princípio XIII: preservar condicionais relevantes). É P2 porque se apoia na
estrutura das histórias P1.

**Independent Test**: montar uma Versão com o padrão de ramificação de Q14 (quatro
opções levando a quatro Seções que convergem para uma quinta) e o padrão de Q33 (duas
opções, com a Seção de um ramo saltando a do outro), consultar a estrutura e verificar
que cada percurso de Seções possível é deduzível sem ambiguidade.

**Acceptance Scenarios**:

1. **Given** uma pergunta de escolha única X com Opção Y e uma Seção Z posterior,
   **When** se registra "se X = Y, ir para Z", **Then** a regra fica associada à Pergunta
   X e à Opção Y e é consultável como tal.
2. **Given** uma Seção sem encaminhamento e uma resposta que não aciona regra, **When** o
   percurso de Seções é deduzido, **Then** a próxima Seção é a seguinte na ordem, sem necessidade
   de regra explícita.
3. **Given** quatro Seções alternativas que devem convergir para uma mesma Seção
   posterior, **When** cada uma recebe encaminhamento para essa Seção, **Then** o
   percurso de cada ramo é deduzível sem ambiguidade.
4. **Given** uma Opção sem regra, **When** o percurso de Seções é deduzido, **Then**
   prevalece o encaminhamento da Seção ou o fluxo padrão.
5. **Given** uma regra cujo destino coincide com o fluxo padrão (como Q51 do instrumento
   atual), **When** é registrada, **Then** é aceita e preservada; decidir se ela é
   mantida pertence à Feature 003.
6. **Given** uma pergunta com regras situada no meio de uma Seção (como Q46, seguida
   por Q47 e Q48), **When** a Versão é consultada, **Then** a regra aparece associada à
   Pergunta X e à Opção Y com seu destino, e a Versão não registra em que momento da
   jornada o desvio é aplicado (FR-053).

---

### User Story 8 - Representar finalização condicional do instrumento (Priority: P2)

O instrumento atual encerra o percurso quando o respondente não concorda com os termos
(Q1 = "Não"). A Versão precisa representar que determinada resposta finaliza o
instrumento.

**Why this priority**: necessário para representar a recusa aos termos, sem implementar
consentimento ou Participação. É P2 pelos mesmos motivos de US7.

**Independent Test**: registrar uma regra "se X = Y, finalizar" e verificar que o
percurso deduzido termina, sem apresentar nenhuma outra Seção, e que nenhuma Seção
artificial de "fim" foi necessária.

**Acceptance Scenarios**:

1. **Given** uma pergunta de escolha única de concordância com Opções "Sim" e "Não",
   **When** se registra "se resposta = Não, finalizar", **Then** a regra é consultável
   como finalização associada a essa Pergunta e Opção.
2. **Given** a regra de finalização, **When** o percurso é deduzido para a Opção "Não",
   **Then** ele termina sem apresentar nenhuma outra Seção.
3. **Given** a última Seção na ordem, sem encaminhamento, **When** o percurso a
   atravessa, **Then** o instrumento é finalizado pelo fluxo padrão, sem regra explícita.
4. **Given** uma Versão com texto de encerramento, **When** o percurso é finalizado por
   regra ou pelo fluxo padrão, **Then** o encerramento é o mesmo; nenhuma Seção sem
   perguntas é necessária para representá-lo.

---

### User Story 9 - Rejeitar explicitamente estruturas inválidas (Priority: P3)

Toda operação que produziria estrutura inválida, ambígua ou incompatível deve ser
rejeitada com motivo explícito, sem alteração parcial.

**Why this priority**: protege a integridade do instrumento e dá à Feature 003
segurança de que uma representação aceita é coerente. É P3 porque as histórias
anteriores já exigem parte dessas verificações nos seus próprios cenários.

**Independent Test**: executar cada caso da lista de estruturas inválidas (FR-058 e
FR-059) e verificar que todos são rejeitados com motivo identificável e que o estado
consultado após cada rejeição é idêntico ao anterior.

**Acceptance Scenarios**:

1. **Given** uma Versão em rascunho com pergunta de escolha sem Opções, **When** se
   tenta publicá-la, **Then** a publicação é rejeitada indicando a pergunta.
2. **Given** uma pergunta de resposta textual curta ou de escala, **When** se tenta
   adicionar-lhe uma Opção, **Then** a operação é rejeitada.
3. **Given** uma pergunta de escala, **When** se tenta registrá-la com limite inicial
   maior ou igual ao final, ou com limite não inteiro, **Then** a operação é rejeitada.
4. **Given** uma pergunta de escolha múltipla, texto curto ou escala, **When** se tenta
   associar-lhe regra de navegação, **Then** a operação é rejeitada.
5. **Given** duas Versões, **When** se tenta criar regra cuja Seção de destino pertence
   à outra Versão, **Then** a operação é rejeitada.
6. **Given** uma pergunta X e uma Opção pertencente a outra pergunta, **When** se tenta
   criar regra em X baseada nessa Opção, **Then** a operação é rejeitada.
7. **Given** uma Seção com uma Pergunta na posição 3, **When** se tenta colocar outra
   Pergunta na mesma posição da mesma Seção, **Then** a operação é rejeitada.
8. **Given** uma Versão publicada, **When** se tenta qualquer alteração do seu conteúdo,
   **Then** a operação é rejeitada.
9. **Given** qualquer rejeição, **When** o estado é consultado em seguida, **Then** ele é
   idêntico ao anterior à tentativa.

---

### Edge Cases

- **Pesquisa sem nenhuma Versão**: válida. Uma Pesquisa recém-criada pode existir sem
  Versões.
- **Várias Versões em rascunho na mesma Pesquisa**: permitidas. Não há regra de "uma
  Versão em preparação por vez" (FR-007).
- **Várias Versões publicadas na mesma Pesquisa**: permitidas e esperadas (2024, 2026,
  2027). Esta feature não define "Versão vigente"; escolher qual Versão é aplicada
  pertence à futura Campanha (FR-008).
- **Pergunta de escolha com uma única Opção**: aceita em rascunho; impede a publicação
  (FR-059).
- **Seção sem perguntas**: aceita em rascunho; impede a publicação. A tela final do
  Google Formulários (Seção 14) não é Seção no NIAE, e sim texto de encerramento da
  Versão (FR-010, FR-059).
- **Regra cujo destino é igual ao fluxo padrão** (Q51, inventário O-16): aceita e
  preservada. Não é erro estrutural; a Feature 003 decide se a mantém.
- **Regra apontando para a própria Seção da pergunta ou para Seção anterior**: aceita
  em rascunho, pois a ordem pode mudar durante a edição; impede a publicação (FR-059).
  Isso garante que todo percurso avance e não haja ciclos.
- **Pergunta com regras situada no meio da Seção** (como Q46, seguida por Q47 e Q48):
  representável. Esta feature não decide se Q47 e Q48 são apresentadas antes de o desvio
  ser efetivado: não se sabe se a forma atual é intenção do instrumento ou limitação do
  Google Formulários. A Feature 003 decide como representar essa ramificação concreta, e
  a feature da jornada de resposta define quando o desvio é aplicado (FR-053).
- **Mais de uma pergunta com regras na mesma Seção**: representável. Qual regra
  prevalece quando ambas são acionadas depende do momento de aplicação, que está fora do
  escopo (FR-053). O instrumento atual não tem esse caso: cada Seção tem no máximo uma
  pergunta com ramificação.
- **Pergunta opcional de escolha única com regras**: se futuramente não for respondida,
  nenhuma regra é acionada e prevalece o fluxo padrão (FR-054).
- **Pergunta do tipo "Se sim, qual...?" sem condicional técnica** (Q6, inventário O-8):
  representável tal como está. Se a Feature 003 decidir representar a intenção
  condicional, poderá fazê-lo com Seções e regras. Esta feature não cria condição de
  exibição por pergunta (FR-057).
- **Opção de complemento textual em pergunta de escolha única** (Q45): permitida, assim
  como em escolha múltipla (Q26, Q32). No máximo uma por pergunta (FR-042).
- **Opções mutuamente exclusivas em escolha múltipla** ("Não houve", "Não recebi"): não
  modeladas. O instrumento atual não impõe exclusividade; se isso for intenção
  metodológica, a Feature 003 ou spec futura deverá tratar.
- **Duas Opções com o mesmo texto na mesma pergunta**: rejeitadas, pois o significado
  ficaria ambíguo para o respondente (FR-058).
- **Mesmo texto de Opção em perguntas diferentes** (Lista E em Q8 e Q9): cada pergunta
  tem suas próprias Opções, independentes (FR-043).
- **Listas extensas de Opções** (77 opções em Q19): representáveis. Esta feature não
  impõe limite de quantidade nem cria catálogo de cursos.
- **Textos com erro de grafia** ("Corcordo totalmente", inventário O-4): preservados
  exatamente como registrados. Depois da publicação, nem correção de grafia é aceita
  enquanto DP-003 estiver pendente.
- **Mudança de tipo de pergunta em rascunho**: não é oferecida. Para mudar o tipo,
  remove-se a Pergunta e cria-se outra (FR-062).
- **Remoção em rascunho de Seção que é destino de regra ou encaminhamento**: rejeitada
  enquanto houver referência (FR-061).
- **Criar nova Versão a partir de Versão em rascunho**: permitida; a origem continua
  editável e independente da nova (FR-021).
- **Nome administrativo da Pesquisa alterado após publicação de Versão**: permitido,
  pois o nome não integra o conteúdo de nenhuma Versão (FR-003).

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII): **[Const.]** decorre diretamente da Constituição;
**[PAEG]** decorre da PAEG; **[Herdado]** a capacidade é exigida pelo instrumento atual
(inventário); **[Arquitetura]** é decisão arquitetural; **[Hipótese]** é hipótese de
produto reversível; **[Escopo]** é decisão de escopo desta feature, revisável por feature
futura. Nenhum requisito desta feature altera, corrige ou cadastra perguntas do
instrumento atual.

### Functional Requirements

**Pesquisa**

- **FR-001**: O sistema DEVE representar a Pesquisa como o instrumento lógico de coleta
  ao longo do tempo, com identidade própria. A Pesquisa NÃO DEVE conter diretamente
  Seções, Perguntas, Opções ou respostas; todo conteúdo pertence a uma Versão. [Const. —
  Terminologia; VII]
- **FR-002**: A Pesquisa DEVE ter um **nome administrativo** obrigatório e não vazio, que
  permite reconhecê-la (por exemplo, "Pesquisa Institucional de Egressos"). Esta feature
  NÃO DEVE acrescentar outros atributos à Pesquisa, como descrição, público, período,
  periodicidade, unidade responsável ou categoria. [Const. — XXII; IX]
- **FR-003**: O nome administrativo da Pesquisa NÃO integra o conteúdo de nenhuma Versão
  e PODE ser alterado sem afetar Versões publicadas. O que é apresentado ao respondente
  pertence à Versão (FR-010). [Arquitetura; Const. — VIII]
- **FR-004**: Uma Pesquisa PODE ter nenhuma, uma ou várias Versões. [Const. — VII]

**Versão da Pesquisa**

- **FR-005**: O sistema DEVE representar a Versão da Pesquisa como configuração
  historicamente identificável de uma Pesquisa, com identidade própria. Cada Versão
  pertence a exatamente uma Pesquisa, e essa relação NÃO DEVE mudar. [Const. —
  Terminologia; VII]
- **FR-006**: Cada Versão DEVE ter uma **designação** obrigatória e não vazia (por
  exemplo, "2024"), única entre as Versões da mesma Pesquisa, que permite distingui-la
  administrativamente. A designação não implica período de aplicação. [Arquitetura]
- **FR-007**: Uma Pesquisa PODE ter simultaneamente várias Versões em RASCUNHO e várias
  Versões PUBLICADAS. [Escopo; Const. — XXII]
- **FR-008**: Esta feature NÃO DEVE definir "Versão vigente", "Versão atual" ou qualquer
  vínculo entre Versão e período, população ou unidade. A escolha de qual Versão é
  aplicada pertence à futura Campanha. [Const. — VII; IX]
- **FR-009**: A Versão DEVE organizar seu conteúdo em Seções ordenadas (FR-024 a
  FR-027). [Const. — VIII; Herdado]
- **FR-010**: A Versão DEVE poder conter, opcionalmente: (a) **título apresentado** (por
  exemplo, "Egresso Ifes"); (b) **texto de abertura** (por exemplo, o convite inicial do
  instrumento atual); (c) **texto de encerramento** (por exemplo, "Este formulário chegou
  ao fim!" e agradecimento). Textos ausentes DEVEM aparecer explicitamente ausentes, sem
  valor padrão. [Herdado; Const. — VIII]

**Estados e publicação**

- **FR-011**: Toda Versão DEVE estar em exatamente um de dois estados: **RASCUNHO** ou
  **PUBLICADA**. Toda Versão nasce em RASCUNHO. Esta feature NÃO DEVE criar outros
  estados (revisão, homologação, aprovada, arquivada, suspensa ou equivalentes).
  [Const. — X; XXII]
- **FR-012**: Uma Versão em RASCUNHO PODE ter seu conteúdo e sua designação criados,
  alterados, reordenados e removidos, respeitando as regras de integridade (FR-058).
  [Escopo]
- **FR-013**: **Publicar** uma Versão significa fixar definitivamente seu conteúdo e sua
  designação. A transição é única e irreversível: de RASCUNHO para PUBLICADA. NÃO DEVE
  existir transição de PUBLICADA para RASCUNHO. [Const. — VIII]
- **FR-014**: A publicação DEVE ser rejeitada se a Versão não satisfizer as condições de
  completude (FR-059). A rejeição DEVE informar **todas** as pendências encontradas, cada
  uma com o elemento envolvido, e a Versão DEVE permanecer em RASCUNHO e inalterada.
  [Arquitetura]
- **FR-015**: Na publicação, o sistema DEVE registrar o momento em que ela ocorreu.
  Tentar publicar uma Versão já publicada NÃO DEVE alterar nada, inclusive esse momento, e
  o resultado DEVE informar que ela já está publicada. [Const. — VIII; Arquitetura]
- **FR-016**: Uma Versão PUBLICADA NÃO DEVE sofrer nenhuma alteração do seu conteúdo nem
  da sua designação. Isso inclui: textos da Versão; Seções, seus textos, sua ordem e seus
  encaminhamentos; Perguntas, seus textos, textos explicativos, tipos, obrigatoriedades e
  ordem; Opções, seus textos, ordem e complemento textual; configuração de escala; regras
  de navegação; inclusão, remoção ou movimentação de qualquer elemento. Toda tentativa
  DEVE ser rejeitada explicitamente, sem alteração parcial. [Const. — VIII]
- **FR-017**: Enquanto a política de correções editoriais estiver pendente (DP-003), a
  imutabilidade de FR-016 é **total**: nem correções de grafia são aceitas em Versão
  publicada. Qualquer mudança DEVE resultar em nova Versão (FR-019). Essa é a **regra
  operacional segura desta feature**, não decisão institucional definitiva de que
  correção editorial controlada jamais será permitida. Se uma política vier a ser
  definida, ela DEVE ser tratada por nova spec e preservar a interpretação histórica das
  Versões publicadas. [Const. — VIII; XXIX]
- **FR-018**: Esta feature NÃO DEVE oferecer exclusão de Pesquisa nem de Versão. Uma
  Versão publicada NÃO DEVE ser excluída por nenhum meio do domínio. [Const. — VIII;
  Escopo]

**Nova Versão a partir de Versão existente**

- **FR-019**: O sistema DEVE permitir criar uma nova Versão a partir de uma Versão
  existente da mesma Pesquisa, informando a designação da nova Versão (FR-006). [Const. —
  VIII]
- **FR-020**: A nova Versão DEVE nascer em RASCUNHO, com identidade própria e conteúdo
  equivalente ao da origem: textos da Versão, Seções, Perguntas, Opções, configurações de
  escala, obrigatoriedades, ordens, encaminhamentos e regras de navegação. [Const. — VIII]
- **FR-021**: Todos os elementos da nova Versão DEVEM ter identidades próprias, distintas
  das da origem. Nenhum elemento PODE ser compartilhado entre Versões. Toda referência
  interna (regra → Pergunta, Opção e Seção de destino; encaminhamento → Seção de destino)
  DEVE apontar para o elemento correspondente **da nova Versão**. A origem PODE estar em
  RASCUNHO ou PUBLICADA. [Const. — VIII]
- **FR-022**: Nenhuma alteração posterior na nova Versão PODE alterar a Versão de origem,
  e vice-versa enquanto a origem estiver em RASCUNHO. [Const. — VIII]
- **FR-023**: A nova Versão DEVE registrar de qual Versão foi criada. Esta feature NÃO
  DEVE estabelecer correspondência entre elementos de Versões diferentes (por exemplo,
  "a Pergunta X de 2026 corresponde à Pergunta Y de 2024"); isso é DP-006. [Arquitetura;
  Const. — XXII]

**Seções**

- **FR-024**: Cada Seção DEVE pertencer a exatamente uma Versão e ter identidade própria
  dentro dela. [Const. — VIII]
- **FR-025**: Cada Seção DEVE poder ter, opcionalmente, **título** e **texto
  introdutório** (por exemplo, "Termos e condições" e o texto dos termos). Ausência
  DEVE aparecer explicitamente, sem valor padrão. [Herdado]
- **FR-026**: Cada Seção DEVE ter posição explícita entre as Seções da sua Versão e
  conter um conjunto ordenado de Perguntas. [Const. — VIII; Herdado]
- **FR-027**: A Seção é unidade de organização e de navegação do instrumento. Esta
  feature NÃO DEVE definir como Seções serão paginadas ou apresentadas, nem criar blocos,
  componentes de página ou conteúdo genérico. [Const. — XXIII; Escopo]

**Perguntas**

- **FR-028**: Cada Pergunta DEVE pertencer a exatamente uma Seção da sua Versão e ter
  identidade própria dentro da Versão, independente do texto e da posição. [Const. —
  VIII]
- **FR-029**: Cada Pergunta DEVE ter: **texto** obrigatório e não vazio; **tipo**
  (FR-034); **obrigatoriedade** (obrigatória ou opcional); **posição** explícita na
  Seção. [Herdado; Const. — VIII]
- **FR-030**: Cada Pergunta DEVE poder ter, opcionalmente, **texto explicativo**
  apresentado junto a ela. Ele é necessário à interpretação de perguntas do instrumento
  atual (por exemplo, Q32: "Não considerar auxilio estudantil como bolsa"). [Herdado;
  Const. — VIII]
- **FR-031**: A obrigatoriedade é configuração do instrumento. Esta feature NÃO DEVE
  validar respostas; isso pertence à futura jornada de resposta. [Escopo]
- **FR-032**: Perguntas de Versões diferentes DEVEM ser sempre independentes, mesmo com
  texto idêntico. Esta feature NÃO DEVE criar banco ou biblioteca global de perguntas,
  tags, categorias, códigos globais ou reutilização de perguntas entre Versões. [Const. —
  VIII; XXII; XXIII]
- **FR-033**: Esta feature NÃO DEVE atribuir à Pergunta numeração de apresentação (Q1,
  Q2…), categoria de origem do dado, indicador associado nem outros atributos sem
  consumidor nesta feature. [Const. — XXII]

**Tipos de pergunta**

- **FR-034**: O sistema DEVE suportar **exatamente** quatro tipos de pergunta: **escolha
  única**, **escolha múltipla**, **resposta textual curta** e **escala**. Qualquer outro
  tipo DEVE ser rejeitado. Novos tipos só podem surgir por spec própria com consumidor
  concreto (DP-005). [Herdado; Const. — XXII; XXIII]
- **FR-035**: **Escolha única** DEVE ter um conjunto ordenado de Opções, das quais,
  futuramente, no máximo uma poderá ser selecionada (exatamente uma, se obrigatória). É o
  único tipo que admite regras de navegação condicional. "Múltipla escolha" e "lista
  suspensa" do Google Formulários são, ambas, escolha única: a forma de apresentação NÃO
  DEVE ser distinguida como tipo nem como atributo da Pergunta nesta feature. [Herdado;
  Arquitetura]
- **FR-036**: **Escolha múltipla** DEVE ter um conjunto ordenado de Opções, das quais,
  futuramente, zero, uma ou várias poderão ser selecionadas, conforme a obrigatoriedade.
  Esta feature NÃO DEVE criar mínimo ou máximo de seleções nem exclusividade entre
  Opções. [Herdado; Const. — XXII]
- **FR-037**: **Resposta textual curta** representa pergunta cuja resposta futura será
  um texto simples. Ela NÃO DEVE ter Opções, configuração de escala, regra de navegação,
  validação de formato, expressão regular, limite configurável ou subtipo (numérico, ano,
  e-mail). O fato de Q3 (idade) e Q10 (ano) usarem texto no instrumento atual NÃO DEVE
  levar à inferência de tipo numérico ou de data. [Herdado; Const. — XXII; XIII]
- **FR-038**: **Escala** DEVE ter configuração com: **limite inicial** e **limite final**,
  ambos inteiros e obrigatórios, com o inicial menor que o final; **rótulo inicial** e
  **rótulo final**, opcionais, associados às extremidades. A escala é de pontos inteiros
  consecutivos entre os limites. Ela NÃO DEVE ter Opções, regra de navegação, rótulos de
  pontos intermediários, pesos, cálculos ou pontuação. [Herdado; Const. — XXII]
- **FR-039**: A configuração da escala integra o conteúdo da Versão e DEVE ser preservada
  exatamente como registrada, inclusive grafia dos rótulos. [Const. — VIII]

**Opções**

- **FR-040**: Somente perguntas de escolha única e de escolha múltipla PODEM ter Opções.
  [Herdado; Arquitetura]
- **FR-041**: Cada Opção DEVE pertencer a exatamente uma Pergunta e ter: identidade
  própria dentro da Versão, independente do texto apresentado e da posição; **texto
  apresentado** obrigatório e não vazio; **posição** explícita entre as Opções da
  Pergunta. Alterar o texto de uma Opção em rascunho NÃO DEVE alterar sua identidade.
  [Const. — VIII]
- **FR-042**: Uma Opção PODE ser marcada como **admitindo complemento textual**: quando
  selecionada futuramente, o respondente poderá acrescentar texto livre a ela. Esse é o
  mínimo necessário para representar "Outro: (texto)" de Q26, Q32 e Q45. Cada Pergunta
  PODE ter no máximo uma Opção com complemento textual. Esta feature NÃO DEVE exigir que
  essa Opção seja a última nem lhe atribuir texto padrão, e NÃO DEVE criar tipo genérico
  de resposta composta. [Herdado; Hipótese]
- **FR-043**: Esta feature NÃO DEVE criar catálogo global de Opções, listas
  compartilhadas entre perguntas ou listas dinâmicas alimentadas por fonte externa (por
  exemplo, cursos ou campi). Listas iguais em perguntas diferentes são Opções distintas.
  [Const. — VIII; XXII]
- **FR-044**: Esta feature NÃO DEVE limitar a quantidade de Opções de uma pergunta.
  [Herdado]

**Ordem**

- **FR-045**: A ordem das Seções na Versão, das Perguntas na Seção e das Opções na
  Pergunta DEVE ser explícita, total e inequívoca. [Const. — VIII]
- **FR-046**: A ordem NÃO DEVE depender de identificador, data ou sequência de criação.
  Consultar a mesma Versão DEVE produzir sempre a mesma ordem. [Const. — VIII; XXVI]
- **FR-047**: Dois elementos do mesmo conjunto ordenado NÃO PODEM ocupar a mesma posição.
  Operação que produziria esse empate DEVE ser rejeitada. [Const. — VIII]

**Fluxo padrão, encaminhamento e navegação condicional**

- **FR-048**: **Fluxo padrão**: dentro de uma Seção, as Perguntas seguem sua ordem. Ao
  sair de uma Seção, o percurso segue para a Seção seguinte na ordem; depois da última
  Seção, o instrumento é finalizado. Esse fluxo NÃO DEVE exigir regra explícita.
  [Herdado; Const. — XXII]
- **FR-049**: Uma Seção PODE ter um **encaminhamento**: indicação de qual Seção da mesma
  Versão segue a ela quando nenhuma regra condicional for acionada, substituindo o fluxo
  padrão apenas para essa Seção. O encaminhamento é necessário para representar a
  convergência dos ramos do instrumento atual (Seções 4–7 → Seção 8; Seção 9 → Seção 11),
  que a ordem sozinha não expressa. Seções sem encaminhamento seguem o fluxo padrão.
  [Herdado; Arquitetura]
- **FR-050**: Uma **regra de navegação condicional** DEVE ter a forma "se a resposta à
  Pergunta X for a Opção Y, então ir para a Seção Z" ou "se a resposta à Pergunta X for a
  Opção Y, então finalizar o instrumento". X DEVE ser pergunta de escolha única; Y DEVE
  ser Opção de X; Z DEVE ser Seção da mesma Versão. [Herdado; Const. — XXIII]
- **FR-051**: A regra DEVE estar semanticamente associada à Pergunta X e à Opção Y, e NÃO
  à Seção que contém X. [Herdado — intenção; Const. — XIII]
- **FR-052**: Cada Opção PODE ter no máximo uma regra. Opções sem regra seguem o fluxo
  padrão ou o encaminhamento da Seção. [Arquitetura]
- **FR-053**: **Momento de aplicação fora do escopo**: a regra representa apenas que a
  resposta Y à Pergunta X determina o destino (Seção Z ou finalização). Esta feature NÃO
  DEVE fixar em que momento da jornada o desvio é aplicado — por exemplo, imediatamente
  após X ou ao sair da Seção que contém X — nem, portanto, se as Perguntas posteriores a X
  na mesma Seção são apresentadas. Ela NÃO DEVE criar atributo, enumeração ou estratégia
  configurável de momento de aplicação. Assim, não fossiliza a limitação do Google
  Formulários (aplicar ao sair da Seção; inventário, O-15) nem presume a intenção oposta.
  A Feature 003 decide como representar cada ramificação concreta; a feature da jornada
  de resposta define a semântica de execução. [Escopo; Const. — XIII; XXIX]
- **FR-054**: **Precedência de destino**: o destino de uma regra acionada prevalece
  sobre o encaminhamento da Seção que contém X e sobre o fluxo padrão. Sem regra acionada
  (Opção sem regra ou pergunta opcional sem resposta), a Seção seguinte é a do
  encaminhamento, se houver; senão, a do fluxo padrão. Depois de chegar a Z, o percurso
  segue a partir dela pelas mesmas regras. [Arquitetura]
- **FR-055**: Todo destino de regra ou de encaminhamento DEVE ser Seção **posterior**, na
  ordem, à Seção de origem (a que contém X, ou a que tem o encaminhamento). Isso garante
  que todo percurso avance e termine. A condição é verificada na publicação (FR-059). É
  restrição desta feature, suficiente para o instrumento atual, que não tem ciclos nem
  retorno a Seções anteriores; não é impossibilidade constitucional, e feature futura
  pode ampliá-la diante de necessidade institucional concreta. [Escopo; Const. — XXII]
- **FR-056**: Esta feature NÃO DEVE executar a navegação, nem ter respostas, motor
  genérico de regras, expressões booleanas, AND/OR, condições sobre várias perguntas,
  condições sobre escolha múltipla, texto ou escala, scripts, fórmulas ou linguagem de
  regras. [Const. — XXII; XXIII]
- **FR-057**: Esta feature NÃO DEVE criar condição de exibição por Pergunta nem por
  Seção. Intenções condicionais do instrumento atual DEVEM ser representáveis com Seções,
  encaminhamentos e regras (FR-048 a FR-055). [Const. — XXII; XXIII]

**Integridade, completude e rejeição de estruturas inválidas**

- **FR-058**: **Regras de integridade**, verificadas em toda operação, inclusive em
  rascunho. O sistema DEVE rejeitar explicitamente a operação que produziria:
  (a) elemento de uma Versão referenciando Seção, Pergunta ou Opção de outra Versão;
  (b) Opção em pergunta de resposta textual curta ou de escala;
  (c) configuração de escala em pergunta que não seja de escala;
  (d) pergunta de escala sem limites, com limite não inteiro ou com limite inicial maior
  ou igual ao final;
  (e) regra de navegação em pergunta que não seja de escolha única;
  (f) regra baseada em Opção que não pertence à Pergunta da regra;
  (g) regra ou encaminhamento cujo destino não é Seção da mesma Versão;
  (h) mais de uma regra para a mesma Opção;
  (i) posições empatadas no mesmo conjunto ordenado (FR-047);
  (j) tipo de pergunta fora dos quatro suportados (FR-034);
  (k) texto obrigatório vazio (nome da Pesquisa, designação da Versão, texto de Pergunta
  ou de Opção);
  (l) designação de Versão repetida na mesma Pesquisa;
  (m) duas Opções com o mesmo texto apresentado na mesma Pergunta;
  (n) mais de uma Opção com complemento textual na mesma Pergunta;
  (o) qualquer alteração do conteúdo de Versão publicada (FR-016).
  [Const. — VIII; XXVI; Arquitetura]
- **FR-059**: **Condições de completude**, exigidas para publicar. A publicação DEVE ser
  rejeitada se a Versão tiver:
  (a) nenhuma Seção;
  (b) Seção sem nenhuma Pergunta;
  (c) pergunta de escolha única ou múltipla com menos de duas Opções;
  (d) regra ou encaminhamento cujo destino seja a própria Seção de origem ou Seção
  anterior a ela (FR-055).
  [Arquitetura; Hipótese em (b) e (c)]
- **FR-060**: Toda rejeição DEVE ser explícita, identificar a regra violada e o elemento
  envolvido, e NÃO DEVE deixar alteração parcial: o estado após a rejeição DEVE ser
  idêntico ao anterior. Esta feature NÃO DEVE criar framework genérico de validação.
  [Const. — XXII; XXVI]
- **FR-061**: Em rascunho, remover uma Pergunta remove também suas Opções, sua
  configuração e suas regras; remover uma Opção remove também a regra associada a ela.
  Remover uma Seção que ainda contém Perguntas, ou que é destino de regra ou de
  encaminhamento, DEVE ser rejeitado enquanto essas dependências existirem. [Arquitetura]
- **FR-062**: O tipo de uma Pergunta é definido na criação e NÃO PODE ser alterado,
  nem em rascunho. Para mudar o tipo, remove-se a Pergunta e cria-se outra. Assim, nenhuma
  configuração (Opções, escala, regras) fica incompatível com o tipo nem é descartada em
  silêncio. Texto, texto explicativo, obrigatoriedade e, em escala, a configuração de
  escala continuam alteráveis em rascunho. [Escopo; Const. — XXII]

**Consulta**

- **FR-063**: O sistema DEVE permitir consultar as Versões de uma Pesquisa, com
  designação, estado, momento da publicação (se publicada) e Versão de origem (se houver).
  [Const. — VIII]
- **FR-064**: O sistema DEVE permitir consultar o conteúdo completo de uma Versão, com
  todos os elementos, na ordem definida, incluindo regras e encaminhamentos, de forma
  suficiente para deduzir sem ambiguidade todos os percursos possíveis. [Const. — VIII;
  XXVI]

**Independência em relação a outras features**

- **FR-065**: Pesquisa, Versão e seus elementos NÃO DEVEM depender da existência de
  Pessoa ou Conclusão Acadêmica, nem referenciá-las. [Const. — VII; Escopo]
- **FR-066**: Esta feature NÃO DEVE criar entidades, campos ou marcadores provisórios de
  Campanha, Participação, Resposta, consentimento registrado, população elegível ou
  periodicidade. [Const. — VII; IX; XXII]
- **FR-067**: Esta feature NÃO DEVE alterar o comportamento nem o contrato da Feature
  001. [Escopo]

### Key Entities *(include if feature involves data)*

Nenhuma entidade desta feature contém dado pessoal nem dado institucional, derivado ou
declarado (Princípio III). Todas representam **configuração do instrumento**.

- **Pesquisa**: instrumento lógico ao longo do tempo. Atributos: identidade; nome
  administrativo. Relação: 0..N Versões.
- **Versão da Pesquisa**: configuração historicamente identificável da Pesquisa.
  Atributos: identidade; designação (única na Pesquisa); estado (RASCUNHO | PUBLICADA);
  momento da publicação; Versão de origem (opcional); título apresentado, texto de
  abertura e texto de encerramento (opcionais). Relação: pertence a exatamente 1
  Pesquisa; contém 0..N Seções (≥1 para publicar).
- **Seção**: unidade de organização e de navegação. Atributos: identidade; posição;
  título e texto introdutório (opcionais); encaminhamento (opcional, para Seção posterior
  da mesma Versão). Relação: pertence a 1 Versão; contém 0..N Perguntas (≥1 para
  publicar).
- **Pergunta**: item do instrumento. Atributos: identidade; posição; texto; texto
  explicativo (opcional); tipo (escolha única | escolha múltipla | resposta textual curta
  | escala); obrigatoriedade. Relação: pertence a 1 Seção; tem 0..N Opções (somente
  escolha; ≥2 para publicar); tem 0..1 configuração de escala (exatamente 1 se escala).
- **Opção**: alternativa de uma pergunta de escolha. Atributos: identidade (independente
  do texto); posição; texto apresentado; admite complemento textual (sim/não). Relação:
  pertence a 1 Pergunta; tem 0..1 regra de navegação.
- **Configuração de escala**: parte da Pergunta de escala. Atributos: limite inicial;
  limite final; rótulo inicial e rótulo final (opcionais).
- **Regra de navegação condicional**: "se Pergunta X = Opção Y, ir para Seção Z" ou
  "…, finalizar". Atributos: Pergunta (escolha única); Opção (de X); destino (Seção
  posterior da mesma Versão, ou finalização).

## Cobertura estrutural do instrumento atual

Demonstra que a estrutura é suficiente para a Feature 003 sem cadastrar as 54 perguntas.
A coluna **Natureza** distingue intenção do instrumento de acidente da ferramenta
(Princípio XIII). A decisão item a item pertence à Feature 003.

| Característica observada (inventário) | Exemplo | Representação na 002 | Natureza |
|---------------------------------------|---------|----------------------|----------|
| Título exibido | "Egresso Ifes" | Título apresentado da Versão (FR-010) | Intenção |
| Texto de abertura | Convite inicial | Texto de abertura da Versão (FR-010) | Intenção |
| Termos e condições | Seção 1 | Título e texto introdutório de Seção (FR-025) | Intenção |
| Recusa encerra o instrumento | Q1 = "Não" → fim | Escolha única + regra de finalização (FR-050) | Intenção |
| Tela final como "Seção 14" | "Este formulário chegou ao fim!" | Texto de encerramento da Versão; **não** é Seção (FR-010, FR-059) | Acidente da ferramenta |
| Seções com título e descrição; Seção sem título | Seções 2–12; Seção 13 | Título e texto opcionais (FR-025) | Intenção |
| "Múltipla escolha" e "Lista suspensa" | Q1, Q5; Q2, Q4 | Ambas escolha única; apresentação não é tipo (FR-035) | Acidente da ferramenta |
| Caixas de seleção | Q26, Q32, Q47 | Escolha múltipla (FR-036) | Intenção |
| Resposta curta | Q3, Q10 | Resposta textual curta, sem validação (FR-037) | Intenção (tipo de dado: Feature 003) |
| Escala linear 1–5 com rótulos | Q20, Q36, Q52 | Escala com limites e rótulos (FR-038) | Intenção |
| "Outro: (texto)" | Q26, Q32, Q45 | Opção com complemento textual (FR-042) | Intenção |
| Descrição de pergunta | Q10, Q32, Q48 | Texto explicativo da Pergunta (FR-030) | Intenção (notas internas, O-3: Feature 003) |
| Obrigatoriedade por pergunta | Q42 e Q44 opcionais (O-10) | Obrigatoriedade por Pergunta (FR-029) | Intenção ou acidente: Feature 003 |
| Ramificação em quatro ramos | Q14 → Seções 4–7 | Uma regra por Opção (FR-050, FR-052) | Intenção |
| Convergência dos ramos | Seções 4–7 → Seção 8 | Encaminhamento de Seção (FR-049) | Intenção |
| Ramo que salta o outro | Q33; Seção 9 → Seção 11 | Regra + encaminhamento (FR-049, FR-050) | Intenção |
| Ramificação aplicada ao sair da Seção | Q46 seguida de Q47, Q48 (O-15) | Regra associada à Pergunta e à Opção; momento de aplicação não fixado (FR-051, FR-053) | Intenção ou acidente: Feature 003; execução: jornada de resposta |
| Ramificação sem efeito prático | Q51 (O-16) | Representável e aceita (Edge Cases) | Feature 003 decide |
| "Se sim, qual?" sem condicional | Q6 (O-8) | Representável como está, ou com Seções e regra (FR-057) | Feature 003 decide |
| Listas iguais em perguntas diferentes | Lista E em Q8 e Q9 | Opções próprias por pergunta (FR-043) | Intenção |
| Listas extensas | Lista 19 (77 opções) | Opções ordenadas, sem limite (FR-044) | Intenção (origem institucional: Feature 003) |
| Numeração Q1–Q54 | — | Não é atributo; decorre da ordem, se necessária (FR-033) | Apresentação |
| Erros de grafia | "Corcordo totalmente" (O-4) | Preservados; política de correção em DP-003 (FR-017) | Feature 003 decide |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Uma Versão de demonstração, com conteúdo fictício e reduzido (não as 54
  perguntas), representa 100% das características estruturais da tabela "Cobertura
  estrutural do instrumento atual" classificadas como intenção. Todos os percursos de
  Seções possíveis dela podem ser deduzidos da consulta (FR-064) sem ambiguidade.
- **SC-002**: Para uma Versão publicada, 100% das tentativas de alteração listadas em
  FR-016 (pelo menos uma por tipo de elemento e de atributo) são rejeitadas, e o conteúdo
  consultado depois é integralmente idêntico ao consultado no momento da publicação.
- **SC-003**: Uma nova Versão criada a partir de uma Versão publicada tem 0 elementos
  compartilhados com a origem e 0 referências a elementos da origem. Após alterar pelo
  menos um elemento de cada tipo na nova Versão, a origem permanece integralmente
  idêntica.
- **SC-004**: 100% dos casos de FR-058 e FR-059 são rejeitados com motivo que identifica
  a regra e o elemento, e em 100% deles o estado após a rejeição é idêntico ao anterior.
- **SC-005**: Elementos criados em ordem embaralhada são consultados na ordem das
  posições atribuídas em 100% das consultas repetidas.
- **SC-006**: Todas as verificações desta feature executam com sucesso sem nenhuma
  Pessoa ou Conclusão Acadêmica existente, e as verificações da Feature 001 continuam
  passando sem alteração.
- **SC-007**: O modelo tem exatamente 4 tipos de pergunta, 2 estados de Versão e 0
  entidades de Campanha, Participação ou Resposta.
- **SC-008**: Cada uma das 10 perguntas de sucesso da descrição original pode ser
  respondida com "sim", apontando requisitos e cenários desta spec.

## Assumptions

Apenas suposições não institucionais. As regras institucionais em aberto estão em
Decisões Pendentes.

- Os consumidores desta feature são outras funcionalidades do NIAE e quem as desenvolve.
  Não há interface para egressos ou gestores; as operações são capacidades do domínio.
- O volume é pequeno (dezenas de Seções, centenas de Perguntas e Opções por Versão) e
  esta feature não tem metas de desempenho.
- A imutabilidade da Versão publicada é mais estrita que o mínimo constitucional
  (Princípio VIII exige nova Versão para mudanças de significado; aqui toda mudança é
  bloqueada). Essa é a regra operacional segura enquanto DP-003 estiver pendente, não
  decisão institucional definitiva; pode ser flexibilizada por nova spec, sem perda
  histórica (FR-017).
- "Destinos somente posteriores" (FR-055) é restrição desta feature, suficiente para o
  instrumento atual, e pode ser ampliada por feature futura com necessidade concreta.
- As condições "Seção com ao menos uma Pergunta" e "pergunta de escolha com ao menos duas
  Opções" (FR-059 b, c) são hipóteses de integridade compatíveis com todo o instrumento
  atual. Podem ser revistas se surgir consumidor concreto.
- "No máximo uma Opção com complemento textual por pergunta" (FR-042) corresponde a todo
  o instrumento atual e pode ser revisto se surgir consumidor concreto.
- Esta feature não cria Versão de demonstração permanente nem cadastra o instrumento
  atual. A Versão de SC-001 serve apenas à verificação.

## Invariantes Constitucionais Afetados *(mandatory)*

- **VII — Pesquisa, Versão, Campanha e Participação distintas (NON-NEGOTIABLE)**: Pesquisa
  e Versão são entidades distintas (FR-001, FR-005). O conteúdo pertence só à Versão
  (FR-001). Não há "Versão vigente" nem vínculo com período ou público, que pertencem à
  Campanha (FR-008). Não há placeholders de Campanha, Participação ou Resposta (FR-066).
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: a Versão publicada é integralmente
  imutável (FR-016, FR-017) e não pode ser excluída (FR-018). Texto, Opções, escala,
  condicionais e ordem permanecem recuperáveis (FR-064). A evolução ocorre por nova
  Versão, sem elementos compartilhados (FR-019 a FR-022). A identidade das Opções não
  depende do texto (FR-041). A ordem é explícita (FR-045 a FR-047).
- **X — Tecnologia não redefine a governança (NON-NEGOTIABLE)**: só dois estados, sem
  workflow de aprovação (FR-011). A publicação existe apenas como capacidade do domínio.
  Esta feature não a expõe a nenhum perfil ou interface; quem pode publicar é DP-001.
  Ver "Tensões" abaixo.
- **XIII — Instrumento atual é referência, não limite**: a estrutura modela a intenção, e
  os acidentes do Google Formulários são identificados e não reproduzidos: tela final
  como Seção, lista suspensa como tipo, regra presa à Seção (tabela de cobertura,
  FR-051). O momento de aplicação da regra não é fixado, para não fossilizar a limitação
  da ferramenta nem presumir intenção não confirmada (FR-053). Nenhuma pergunta é
  alterada ou corrigida; as decisões de representação ficam para a Feature 003.
- **XXII — Simplicidade e YAGNI**: quatro tipos (FR-034), dois estados (FR-011), regra
  de uma pergunta e uma Opção (FR-050), encaminhamento só onde a ordem não basta
  (FR-049), sem catálogo de perguntas ou Opções (FR-032, FR-043) e sem atributos sem
  consumidor (FR-002, FR-033). Cada capacidade criada tem consumidor na tabela de
  cobertura.
- **XXIII — Editor não é form builder universal**: sem scripting, expressões, condição de
  exibição, apresentação configurável ou tipos customizados (FR-035, FR-056, FR-057).
- **XXVI — Testes protegem invariantes**: SC-002 a SC-005 cobrem versionamento,
  preservação histórica, condicionais e ordem.
- **XXVIII — Desenvolvimento orientado por specs**: novos tipos e capacidades só por
  spec (FR-034, DP-005).
- **XXIX — Hipóteses não viram requisitos (NON-NEGOTIABLE)**: as hipóteses estão marcadas
  (FR-042, FR-059) e as regras institucionais estão em Decisões Pendentes.
- **III — Dado institucional não é resposta**: não afetado. Esta feature não registra
  dado de nenhuma das três categorias. Qual pergunta atual sai da jornada por ser
  institucional é decisão da Feature 003.
- **I, II, XI — Longitudinalidade, egresso, identidade**: não afetados. A feature é
  independente de Pessoa e Conclusão Acadêmica (FR-065).

**Tensões identificadas (não são conflitos)**:

- **Princípio X × publicação**: a Constituição veda que a publicação decorra apenas de
  permissão técnica. Esta feature especifica o **efeito** da publicação (fixar o
  conteúdo), mas não quem pode publicar. Até DP-001 ser resolvida, nenhuma feature DEVE
  expor a publicação a usuários com base apenas em acesso ao sistema.
- **Princípio XVII × termo de consentimento**: o texto dos termos fica preservado na
  Versão (Seção 1) e Q1 é representável como escolha única com finalização. Isso **não**
  é registro de consentimento, que exige Participação e pertence a feature futura
  (DP-007).

Nenhum conflito real com a Constituição ou com a Feature 001 foi identificado.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. Pertence de fato ao domínio de acompanhamento? Sim. Pesquisa e Versão da Pesquisa
   estão na Fronteira do Domínio do NIAE.
2. É necessária ao ciclo de acompanhamento? Sim. Campanha, Participação e Resposta
   dependem de uma Versão identificável e estável (Princípios VII e VIII).
3. Existe ou está prevista solução institucional mais adequada? Não para o
   versionamento com preservação histórica. O Google Formulários, usado hoje, não oferece
   Versões imutáveis nem associação com Conclusão Acadêmica.
4. Integração seria suficiente? Não. Importar do Google Formulários está fora do escopo,
   e a ferramenta não é fonte canônica do instrumento.
5. A incorporação aumentaria desnecessariamente o acoplamento do núcleo? Não. A
   estrutura é independente de Pessoa, Conclusão e integrações (FR-065), e limitada ao
   que o instrumento atual exige (tabela de cobertura).

## Out of Scope *(mandatory)*

- Cadastro ou migração das 54 perguntas do Formulário Egresso do Ifes 2024 e qualquer
  decisão sobre sua representação, inclusive a classificação de cada condicional e
  peculiaridade como intenção ou acidente (Feature 003).
- Alteração, correção ou revisão metodológica do instrumento.
- Editor administrativo, interface de CRUD, tela ou ação de "duplicar" e de "publicar".
- Resposta, Participação, Campanha, população elegível, periodicidade.
- Execução da navegação, renderização pública, paginação, progresso, autosave,
  retomada, validação de preenchimento, sessão de usuário.
- Momento em que uma regra acionada é aplicada na jornada (logo após a pergunta, ao sair
  da Seção ou outro) e qualquer atributo ou estratégia para configurá-lo (FR-053).
- Consentimento registrado.
- Pessoa e Conclusão Acadêmica (nenhuma alteração à Feature 001).
- Autenticação, permissões, perfis CPAEG/CSAEG, workflow de elaboração ou aprovação,
  estados além de RASCUNHO e PUBLICADA.
- Dashboard, indicadores, exportação, API pública, integração acadêmica real,
  notificações, comunicação, Portal do Egresso.
- Importação do Google Formulários.
- Form builder genérico, scripting, plugins, fórmulas, expressões, lógica arbitrária,
  condições compostas, condição de exibição de pergunta ou Seção.
- Tipos de pergunta além dos quatro (data, hora, upload, matriz, assinatura, rich text,
  fórmula, ranking, geolocalização, customizados).
- Validação de formato de texto, mínimo e máximo de seleções, exclusividade entre Opções,
  pesos ou pontuação de escala.
- Banco global de perguntas, catálogo global de Opções, listas dinâmicas de cursos ou
  campi.
- Correspondência entre elementos de Versões diferentes (DP-006).
- Tradução e i18n do questionário.
- Colaboração simultânea e histórico de cada edição de rascunho.
- Exclusão de Pesquisa ou Versão.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

- **DP-001** — DECISÃO PENDENTE: quem tem competência institucional para publicar uma
  Versão. A PAEG atribui à CPAEG elaborar o questionário com as áreas de ensino, pesquisa
  e extensão (Art. 21, VI) e às CSAEGs aplicá-lo (Art. 22, IV), mas não define quem
  aprova a publicação. Instância competente: Proex/CPAEG (PAEG Art. 26 para casos
  omissos). Impacto: quem poderá acionar FR-013. Tratamento provisório: publicação apenas
  como capacidade do domínio, sem exposição a usuários (ver "Tensões").
- **DP-002** — DECISÃO PENDENTE: workflow institucional de elaboração, revisão e
  aprovação do instrumento. Instância competente: CPAEG, com Proex e Proen. Impacto:
  eventuais estados intermediários. Tratamento provisório: apenas RASCUNHO e PUBLICADA
  (FR-011), sem impedir que spec futura acrescente etapas antes da publicação.
- **DP-003** — DECISÃO PENDENTE: política para correções puramente editoriais (grafia,
  pontuação) após a publicação, se alguma exceção for desejada. A imutabilidade total de
  FR-017 é regra operacional provisória, não decisão institucional; uma política futura
  será tratada por nova spec e DEVE preservar a interpretação histórica. Inclui o caso
  "Corcordo totalmente" (inventário, O-4). Instância competente: CPAEG. Impacto: FR-016 e
  FR-017. Tratamento provisório: imutabilidade total; qualquer correção exige nova
  Versão.
- **DP-004** — DECISÃO PENDENTE: quais melhorias metodológicas serão feitas no
  instrumento atual (O-6 a O-20 do inventário). Instância competente: CPAEG, com as áreas
  de ensino, pesquisa e extensão. Impacto: nenhum na estrutura desta feature; afeta o
  conteúdo da Feature 003 e de Versões futuras. Tratamento provisório: nenhuma alteração.
- **DP-005** — DECISÃO PENDENTE: eventual necessidade futura de novos tipos de pergunta
  ou de novas capacidades (por exemplo, exclusividade entre Opções, condição de exibição
  por pergunta, validação de formato). Instância competente: CPAEG, para a necessidade
  metodológica; spec própria, para a capacidade. Impacto: FR-034, FR-036, FR-037, FR-057.
  Tratamento provisório: apenas os quatro tipos e as capacidades desta spec.
- **DP-006** — DECISÃO PENDENTE: critério de comparabilidade entre Versões, isto é,
  quando uma pergunta de uma Versão é considerada "a mesma" de outra Versão para fins de
  série histórica e exportação. Instância competente: CPAEG. Impacto: exportações e
  indicadores futuros (Princípio XVIII); nenhum nesta feature. Tratamento provisório:
  só se registra de qual Versão a nova foi criada (FR-023), sem correspondência entre
  elementos.
- **DP-007** — DECISÃO PENDENTE: forma institucional do termo de consentimento — se ele
  permanece como texto e pergunta dentro da Versão do instrumento ou passa a ser
  artefato próprio com versionamento independente — e sua base legal. Instância
  competente: a identificar (encarregado de dados, CPAEG). Impacto: Princípio XVII na
  futura Participação; nenhum na estrutura desta feature. Tratamento provisório: o texto
  dos termos é representável como texto de Seção e Q1 como escolha única com
  finalização, sem registro de consentimento.
