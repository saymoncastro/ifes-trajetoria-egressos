# Feature Specification: Editor institucional de Pesquisa e Versão

**Feature Branch**: `claude/feature-009-research-editor-0de597`

**Created**: 2026-10-01

**Status**: Implementada e integrada à `main` em 2026-10-01 (PR #14).

**Input**: User description: "Feature 009 — Editor institucional de Pesquisa e Versão.
Primeira interface institucional para compor e editar uma Versão em rascunho sem editar
código: visualizar Pesquisas e suas Versões, criar Pesquisa, criar Versão em rascunho,
criar nova Versão a partir de outra, estruturar Seções, Perguntas e Opções, configurar as
capacidades já suportadas pela Feature 002, pré-visualizar o instrumento e identificar
os problemas que impediriam sua publicação. É uma interface sobre a Feature 002, sem
inventar capacidades do instrumento. Não é form builder genérico. Não publica: quem pode
publicar é Feature 010. Sem novos modelos de domínio, sem Campanha, dashboard ou
governança. Páginas geradas no servidor, sem SPA, API própria ou dependência de
JavaScript. Acessibilidade e responsividade básicas."

## Contexto

As oito primeiras features estabeleceram:

- **001** — **Pessoa → Conclusão Acadêmica**, com fonte acadêmica simulada.
- **002** — o modelo do instrumento: **Pesquisa → Versão (RASCUNHO | PUBLICADA) →
  Seções → Perguntas → Opções**. Ela também define:
  - quatro tipos de Pergunta e a obrigatoriedade;
  - a configuração de escala e a Opção com complemento textual;
  - o encaminhamento de Seção e a regra de navegação "se Pergunta X = Opção Y, ir para
    Seção Z / finalizar";
  - a criação de nova Versão a partir de outra;
  - as condições de completude exigidas para publicar e a imutabilidade total da Versão
    publicada.

  Tudo isso existe **apenas como operações internas**: a 002 deixou fora do escopo o
  "editor administrativo, interface de CRUD, tela ou ação de duplicar e de publicar".
- **003** — a baseline **"Formulário Egresso Ifes 2024 — referência migrada"**, na
  Pesquisa **"Pesquisa Institucional de Egressos"**.
  - Está materializada em **RASCUNHO**, com 13 Seções, 54 Perguntas, 385 Opções,
    11 escalas, 10 regras e 7 encaminhamentos.
  - A materialização é idempotente e **recusa** uma baseline existente que diverja da
    declarada (003 FR-031 a FR-033).
  - Q10–Q19 continuam perguntas declaradas (003/DP-307).
- **004** — Campanha. Abrir uma Campanha exige Versão PUBLICADA (004 FR-009).
- **005/006/007** — Participação, Respostas, jornada e conclusão, e entrada.
  - Para a 006, a **Seção é a unidade de navegação** e a regra é lida **ao deixar a
    Seção**, com a precedência: regra acionada, depois encaminhamento, depois ordem, depois
    finalização (006 FR-010 a FR-013).
  - Uma Versão com **mais de uma Pergunta com regra na mesma Seção** está fora da
    capacidade de execução da jornada (006 FR-016; 006/DP-604).
  - Essa limitação é da execução, não do modelo da 002. Hoje ela só é detectada quando
    a jornada é calculada.
- **008** — a interface navegável do egresso.
  - Páginas geradas no servidor e funcionando sem JavaScript.
  - Acessível desde o início.
  - Disponível apenas no **modo de demonstração** local e não produtivo, que é desligado
    por padrão e, quando desligado, faz toda página responder como inexistente.
  - A 008 excluiu explicitamente "painel administrativo, editor do instrumento,
    publicação por tela" (008 FR-093).

Até agora, compor ou alterar uma Versão exige escrever código que chame as operações da
002. Esta feature oferece a **primeira interface institucional para compor e editar uma
Versão em rascunho**, sem editar código, em contexto ainda não produtivo de governança.

### Princípio central desta spec

A Feature 009 é uma **interface sobre a Feature 002**. Ela não redefine o modelo de
questionário, não cria tipo, estado, regra de navegação ou atributo novo e não decide
quem pode publicar.

- Toda gravação usa as operações públicas da 002.
- As verificações do diagnóstico técnico reutilizam as capacidades que **já existem**:
  - as condições de completude da 002;
  - o limite de execução da 006.

  A interface não tem regras próprias de domínio, nem validador paralelo.
- O que a interface acrescenta é **apresentação**:
  - organização da edição;
  - linguagem compreensível;
  - tradução de rejeições;
  - pré-visualização somente de leitura.

### Termos usados nesta spec

Os nomes são conceituais; a nomenclatura concreta pertence ao plan.

- **Editor**: o conjunto de páginas desta feature.
- **Operador do editor**: quem usa o editor no contexto não produtivo desta feature.
  - Não é papel institucional: não é CPAEG, CSAEG, administrador nem perfil.
  - Não é usuário cadastrado.
  - Competência para elaborar e publicar continua pendente (DP-901; 002/DP-001,
    002/DP-002).
- **Estrutura da Versão**: visão de leitura que resume a Versão:
  - Seções em ordem, com título, encaminhamento e quantidade de Perguntas;
  - Perguntas em ordem, com tipo, obrigatoriedade e existência de desvio;
  - problemas do diagnóstico localizados.
- **Diagnóstico técnico**: consulta, sem gravação, que compõe **dois diagnósticos
  derivados** de uma Versão em rascunho e reúne todos os seus **problemas do
  diagnóstico**:
  - **A — Estrutura válida**: resultado das condições de completude da 002 (002
    FR-059), as mesmas que a operação de publicação aplicaria. Os problemas deste
    diagnóstico são chamados **problemas de estrutura**.
  - **B — Compatível com a jornada atual**: resultado da verificação de que a estrutura
    pode ser executada pela semântica que a 006 suporta hoje (006 FR-016: no máximo uma
    Pergunta com regra por Seção). Os problemas deste diagnóstico são chamados
    **incompatibilidades com a jornada atual**.
- **Situações do diagnóstico técnico**: uma Versão em rascunho está em exatamente uma
  destas situações, sempre derivadas e nunca gravadas:
  1. **com problemas de estrutura**: A não satisfeito. B também é apresentado, se houver
     incompatibilidades;
  2. **estrutura válida, mas incompatível com a jornada atual**: A satisfeito e B não;
  3. **sem impedimentos técnicos conhecidos**: A e B satisfeitos.

  A situação 3 significa **apenas** que nenhuma verificação técnica existente aponta
  impedimento. Ela **não** significa aprovada, homologada, autorizada, publicada nem
  "pronta institucionalmente":
  - não é estado da Versão;
  - não é aprovação;
  - não autoriza ninguém a publicar (Feature 010; 002/DP-001).
- **Pré-visualização**: apresentação somente de leitura do conteúdo de uma Versão como
  instrumento.
  - Mostra textos, Seções, Perguntas, controles correspondentes a cada tipo, Opções e
    escalas.
  - As regras e os encaminhamentos aparecem como anotações.
  - Não grava nada e não executa a navegação.
- **Baseline**: a Versão materializada pela 003.
  - Para o editor, ela é **uma Versão como outra qualquer**, sem exceção pelo nome.
  - Do ponto de vista do domínio, é uma Versão RASCUNHO normal e tecnicamente
    editável. O fluxo recomendado, de forma genérica, é criar uma nova Versão a partir
    dela e editar a cópia (DP-902).
- **Rejeição**: recusa de uma operação da 002. O editor a apresenta em linguagem
  operacional. Nada é gravado (002 FR-060).

### Decisões desta especificação

Escolhas de produto reversíveis, marcadas **[Hipótese]** nos requisitos, e decisões de
escopo:

1. **Acesso pela entrada não produtiva já existente** (FR-001 a FR-006).
   - O editor só está disponível quando o modo de demonstração local da 008 está ligado.
   - Não há cadastro, papel ou permissão.
   - Isso não é autorização institucional. A Feature 010 a substituirá.
2. **Sem ação de publicar** (FR-076 a FR-080).
   - O editor mostra o diagnóstico técnico e seus problemas.
   - O editor não publica.
3. **Diagnóstico técnico = A (completude da 002) + B (compatibilidade com a 006)**,
   ambos reutilizados e apresentados separadamente (FR-066 a FR-075).
   - B impede que uma Versão sem problemas de estrutura seja recusada depois pela
     jornada.
   - Nenhuma terceira regra é criada.
   - O resultado favorável é "sem impedimentos técnicos conhecidos", nunca "pronta
     para publicação".
4. **Edição em níveis** (FR-081 a FR-084):
   - Pesquisa → Versão (estrutura) → Seção (com suas Perguntas) → Pergunta (com suas
     Opções, escala e desvios).
   - Nunca o instrumento inteiro aberto para edição numa só página.
5. **Ordenação por "mover para cima / mover para baixo"**, sem arrastar e soltar
   (FR-061 a FR-064).
   - Elementos novos entram ao final do seu conjunto.
6. **Tipo escolhido na criação e exibido como fixo depois**, conforme 002 FR-062
   (FR-033 a FR-036).
   - Trocar o tipo é remover e criar outra Pergunta, e a interface diz isso.
7. **Remoções com confirmação explícita** que informa as consequências (FR-024, FR-037,
   FR-047).
   - Remoções só onde a 002 já define a semântica: Seção vazia e não referenciada;
     Pergunta e Opção em rascunho.
8. **Pré-visualização estrutural somente de leitura** (FR-085 a FR-093).
   - Reaproveita a apresentação por tipo da 008 quando isso não exigir Participação,
     Campanha nem Resposta.
   - Não simula os ramos.
9. **Mover Pergunta para outra Seção da mesma Versão** é oferecido, porque a 002 já tem
   essa operação (002 US2, cenário 6) e evita recriar Pergunta e Opções (FR-039).
   **[Hipótese]**
10. **Renomear Pesquisa não é oferecido** (FR-011).
    - A 002 tem a operação, mas não há consumidor nesta feature.
    - O nome da Pesquisa da baseline é usado pela materialização da 003.

## Clarifications

### Session 2026-10-01

Decisões consolidadas pelo solicitante após a aprovação da spec e antes do plan:

- Q: Como tratar a baseline da 003 ("Formulário Egresso Ifes 2024 — referência
  migrada") no editor? → A:
  - Ela continua sendo uma Versão RASCUNHO normal do ponto de vista do domínio.
  - NÃO é publicada automaticamente e NÃO é protegida por nome.
  - NÃO há marcação de "referência", estado especial, permissão especial nem bloqueio de
    edição por código fixo.
  - DP-902 continua aberta.
  - A interface PODE recomendar genericamente trabalhar sobre uma cópia ao partir de
    Versão existente.
  - Os testes da 009 NÃO modificam a baseline original.
  - Se a baseline for alterada manualmente no ambiente de demonstração, a recusa da
    materialização da 003 por divergência é comportamento esperado. A 009 não a
    contorna.

  (FR-009, FR-099, FR-100; Edge Cases)
- Q: O editor oferece mover Pergunta entre Seções? → A: Sim.
  - Justificativa: a 002 já tem a operação, há consumidor concreto e a operação não cria
    semântica nova.
  - A operação é simples, sem arrastar e soltar obrigatório, árvore visual,
    movimentação em massa ou mecanismo genérico de reorganização.

  (FR-039)
- Q: O editor oferece renomear Pesquisa? → A: Não.
  - A criação continua disponível. Depois de criada, o nome não é editável pela 009.
  - A 002 não é ampliada só para completar o CRUD.
  - Necessidade institucional concreta será especificada depois.

  (FR-011)
- Q: Como apresentar o resultado das verificações? → A: Como **dois diagnósticos
  derivados**:
  - **A — Estrutura válida**: completude e publicabilidade técnica da 002.
  - **B — Compatível com a jornada atual**: semântica suportada pela 006.

  As situações possíveis são:
  - com problemas de estrutura;
  - estrutura válida, mas incompatível com a jornada atual;
  - estrutura válida e compatível com a jornada atual.

  A última significa apenas **"sem impedimentos técnicos conhecidos"**. Não significa
  aprovada, homologada, autorizada, publicada nem pronta institucionalmente. Nada disso
  é persistido. A governança da publicação é da Feature 010.

  (Termos; US11; FR-066 a FR-075)

## User Scenarios & Testing *(mandatory)*

O ator de todas as histórias é o **operador do editor**, num ambiente local e não
produtivo. Ele conhece o instrumento, mas não o modelo relacional nem o código.

### User Story 1 - Listar Pesquisas e suas Versões (Priority: P1)

O operador abre o editor e vê as Pesquisas existentes. Ao escolher uma, vê suas Versões e
distingue claramente quais estão em rascunho e quais estão publicadas.

**Why this priority**: é o ponto de entrada do editor e a primeira distinção que o
operador precisa fazer (Princípio VII: Pesquisa ≠ Versão; Princípio VIII: publicada é
imutável).

**Independent Test**: com a baseline e uma cópia publicada no banco local, abrir o editor
e verificar:

- a Pesquisa aparece pelo nome;
- as duas Versões aparecem com designação, estado escrito por extenso e, quando
  aplicável, data de publicação e Versão de origem;
- nenhum identificador técnico aparece.

**Acceptance Scenarios**:

1. **Given** um banco com a Pesquisa "Pesquisa Institucional de Egressos", **When** o
   operador abre o editor, **Then** vê essa Pesquisa pelo nome e a quantidade de Versões
   que ela tem.
2. **Given** essa Pesquisa com a baseline em RASCUNHO e uma cópia PUBLICADA, **When** o
   operador abre a Pesquisa, **Then** vê as duas Versões, cada uma com:
   - a designação;
   - o estado escrito ("Rascunho" ou "Publicada"), sem depender só de cor;
   - a data de publicação, na publicada;
   - a Versão de origem, quando houver.
3. **Given** uma Pesquisa sem Versões, **When** o operador a abre, **Then** vê uma
   indicação explícita de que ainda não há Versões e a ação para criar a primeira.
4. **Given** qualquer página dessa história, **When** o conteúdo é inspecionado, **Then**
   não aparecem identificadores internos, nomes de classes, códigos de requisito ou
   códigos de rejeição.
5. **Given** um banco sem nenhuma Pesquisa, **When** o operador abre o editor, **Then**
   vê uma indicação explícita de que não há Pesquisas e a ação para criar uma.

---

### User Story 2 - Criar Pesquisa (Priority: P1)

O operador cria uma Pesquisa informando apenas o seu nome administrativo, que é o único
atributo que a 002 define para ela (002 FR-002).

**Why this priority**: sem criar Pesquisa não é possível compor um instrumento novo sem
código.

**Independent Test**: criar uma Pesquisa pelo editor e verificar:

- ela aparece na lista;
- ela não tem Versões;
- nenhum outro atributo foi pedido.

**Acceptance Scenarios**:

1. **Given** a lista de Pesquisas, **When** o operador cria a Pesquisa "Pesquisa de
   teste" informando o nome, **Then** ela passa a aparecer na lista, sem Versões.
2. **Given** o formulário de criação, **When** o operador envia o nome vazio ou só com
   espaços, **Then** a criação é recusada com mensagem associada ao campo, e nada é
   gravado.
3. **Given** uma Pesquisa já chamada "Pesquisa de teste", **When** o operador tenta criar
   outra com o mesmo nome, **Then** o editor avisa que já existe Pesquisa com esse nome e
   pede confirmação antes de criar. A 002 não proíbe nomes repetidos, e o editor não
   inventa essa proibição.
4. **Given** o formulário de criação, **When** é exibido, **Then** pede somente o nome:
   nada de descrição, público, período, unidade ou categoria.

---

### User Story 3 - Criar Versão em rascunho (Priority: P1)

O operador cria, numa Pesquisa, uma Versão nova e vazia, em rascunho, informando sua
designação.

**Why this priority**: é o início da composição de um instrumento do zero.

**Independent Test**: criar uma Versão numa Pesquisa e verificar:

- ela aparece em RASCUNHO, sem Seções;
- o diagnóstico técnico aponta a falta de Seções.

**Acceptance Scenarios**:

1. **Given** uma Pesquisa, **When** o operador cria a Versão "2026 — teste", **Then** ela
   aparece na lista da Pesquisa como "Rascunho", sem origem e sem Seções.
2. **Given** uma Pesquisa com a Versão "2026 — teste", **When** o operador tenta criar
   outra Versão com a mesma designação, **Then** a criação é recusada com mensagem
   operacional associada ao campo, como "Já existe uma Versão com esta designação nesta
   Pesquisa", e nada é gravado.
3. **Given** uma Versão recém-criada, **When** o operador a abre, **Then** vê a estrutura
   vazia e a ação para adicionar a primeira Seção.

---

### User Story 4 - Criar nova Versão a partir de uma Versão existente (Priority: P1)

O operador escolhe uma Versão existente, em rascunho ou publicada, e cria uma nova Versão
a partir dela. A cópia nasce em rascunho, com conteúdo equivalente, e pode ser editada
sem afetar a origem.

**Why this priority**: é o caminho seguro para evoluir o instrumento e para corrigir
qualquer coisa numa Versão publicada (002 FR-017 e FR-019). É também o fluxo recomendado
para trabalhar a partir da baseline sem modificá-la.

**Independent Test**: a partir da baseline, criar a Versão "Cópia de trabalho" e
verificar:

- 13 Seções, 54 Perguntas, regras e encaminhamentos equivalentes;
- RASCUNHO, com a baseline como origem;
- depois de editar a cópia, a baseline continua equivalente à declarada pela 003.

**Acceptance Scenarios**:

1. **Given** a baseline, **When** o operador escolhe "criar nova Versão a partir desta" e
   informa a designação "Cópia de trabalho", **Then** a nova Versão:
   - aparece em "Rascunho" na mesma Pesquisa;
   - indica que foi criada a partir da baseline;
   - tem a mesma estrutura, inclusive as regras e os encaminhamentos.
2. **Given** uma Versão PUBLICADA, **When** o operador cria uma nova Versão a partir
   dela, **Then** a nova Versão está em rascunho e é editável, e a publicada continua
   intacta.
3. **Given** a cópia, **When** o operador altera nela um texto de Pergunta, **Then** a
   origem não muda.
4. **Given** a designação de uma Versão já existente na Pesquisa, **When** o operador a
   usa para a cópia, **Then** a criação é recusada com mensagem operacional e nenhuma
   cópia parcial é criada.
5. **Given** a nova Versão, **When** a lista de Versões é consultada, **Then** nada indica
   correspondência entre Perguntas das duas Versões. Só a origem da Versão é informada
   (002 FR-023; 002/DP-006).

---

### User Story 5 - Visualizar a estrutura de uma Versão (Priority: P1)

O operador abre uma Versão e compreende rapidamente sua estrutura sem conhecer o modelo
relacional:

- quantas Seções há, em que ordem e com que título;
- as Perguntas de cada uma, com tipo e obrigatoriedade;
- onde há navegação;
- onde há problemas.

**Why this priority**: é o mapa a partir do qual toda edição acontece. Sem ele, a edição
por partes (Princípio XIV; FR-081) se perde.

**Independent Test**: abrir uma cópia da baseline e verificar:

- a página mostra 13 Seções na ordem, cada uma com título ou com indicação de Seção sem
  título, quantidade de Perguntas e encaminhamento;
- as Perguntas mostram tipo e obrigatoriedade em palavras;
- as Seções que contêm Perguntas com desvio estão sinalizadas;
- os totais de Seções e Perguntas estão corretos.

**Acceptance Scenarios**:

1. **Given** uma cópia da baseline, **When** o operador abre a Versão, **Then** vê no topo
   a Pesquisa, a designação, o estado e a origem, e logo abaixo:
   - o título apresentado, o texto de abertura e o texto de encerramento, ou a indicação
     explícita de ausência;
   - o total de Seções e de Perguntas.
2. **Given** a mesma Versão, **When** o operador percorre a estrutura, **Then** cada Seção
   aparece na ordem, com:
   - número de ordem e título, ou "Seção sem título";
   - quantidade de Perguntas;
   - destino depois da Seção: "segue a ordem", "segue para a Seção N — título" ou
     "finaliza".
3. **Given** a mesma Versão, **When** o operador consulta as Perguntas de uma Seção na
   estrutura, **Then** cada Pergunta mostra:
   - posição e texto;
   - tipo em palavras ("Escolha única", "Escolha múltipla", "Texto curto", "Escala");
   - "Obrigatória" ou "Opcional" escritos;
   - para escolha, a quantidade de Opções;
   - para escala, o intervalo;
   - se tem desvio de navegação.
4. **Given** uma Versão com problemas do diagnóstico, **When** o operador abre a estrutura,
   **Then** os elementos com problema estão sinalizados com texto e há acesso à lista
   completa do diagnóstico técnico.
5. **Given** uma Versão grande como a baseline, **When** a estrutura é exibida, **Then**
   nenhum campo de edição aparece nela. As Opções completas ficam na página da Pergunta e
   na pré-visualização, não na estrutura.

---

### User Story 6 - Criar, editar, ordenar e remover Seções em rascunho (Priority: P1)

Na Versão em rascunho, o operador:

- edita a designação e os textos da Versão (título apresentado, abertura, encerramento);
- adiciona Seções;
- edita título e texto introdutório de cada Seção;
- muda a ordem das Seções;
- remove Seções quando a 002 permite.

**Why this priority**: a Seção é a unidade de organização e de navegação (002 FR-027;
006 FR-010). Sem ela não há instrumento.

**Independent Test**: numa Versão vazia, criar três Seções, editar títulos, inverter a
ordem, tentar remover uma Seção com Perguntas (recusado) e remover uma Seção vazia
(aceito). A estrutura reflete cada passo.

**Acceptance Scenarios**:

1. **Given** uma Versão em rascunho, **When** o operador adiciona uma Seção, informando
   ou não título e texto introdutório, **Then** ela aparece ao final da ordem. Sem
   título, aparece como "Seção sem título", e nenhum título padrão é gravado.
2. **Given** uma Seção, **When** o operador altera o título, **Then** a alteração é
   gravada. **When** ele apaga o título, **Then** a Seção passa a não ter título.
3. **Given** três Seções, **When** o operador move a terceira "para cima" duas vezes,
   **Then** ela passa a ser a primeira e as outras mantêm a ordem relativa.
4. **Given** a primeira Seção, **When** a página é exibida, **Then** a ação "mover para
   cima" não é oferecida para ela, e o mesmo vale para "mover para baixo" na última.
5. **Given** uma Seção que contém Perguntas, **When** o operador tenta removê-la, **Then**
   a remoção é recusada com a explicação "remova ou mova as Perguntas desta Seção antes"
   e nada muda.
6. **Given** uma Seção vazia que é destino de regra ou de encaminhamento, **When** o
   operador tenta removê-la, **Then** a remoção é recusada. A explicação identifica, em
   linguagem operacional, o que aponta para ela: "é destino do encaminhamento da Seção 3"
   ou "é destino da Opção 'Não' da Pergunta 2 da Seção 1".
7. **Given** uma Seção vazia e não referenciada, **When** o operador confirma a remoção,
   **Then** ela deixa de existir e as demais mantêm a ordem.
8. **Given** a Versão em rascunho, **When** o operador altera a designação para uma já
   usada na Pesquisa, **Then** a alteração é recusada com mensagem operacional.
9. **Given** a Versão em rascunho, **When** o operador altera o texto de encerramento,
   **Then** a alteração é gravada e aparece na estrutura e na pré-visualização.

---

### User Story 7 - Criar, editar, ordenar e remover Perguntas dos quatro tipos (Priority: P1)

Numa Seção de Versão em rascunho, o operador:

- cria Perguntas de um dos quatro tipos;
- edita texto, texto explicativo e obrigatoriedade;
- muda a ordem;
- move uma Pergunta para outra Seção;
- remove Perguntas.

O tipo é escolhido na criação e não muda depois.

**Why this priority**: as Perguntas são o conteúdo do instrumento. Os quatro tipos são
exatamente os da 002 (002 FR-034).

**Independent Test**: numa Seção, criar uma Pergunta de cada tipo e verificar:

- só os quatro tipos são oferecidos;
- cada tipo pede só a configuração própria;
- o tipo aparece como fixo na edição;
- a reordenação e a remoção se refletem na estrutura.

**Acceptance Scenarios**:

1. **Given** uma Seção em rascunho, **When** o operador inicia a criação de Pergunta,
   **Then** escolhe o tipo entre exatamente quatro opções, cada uma com descrição curta:
   - escolha única: o respondente marca uma Opção;
   - escolha múltipla: marca nenhuma, uma ou várias;
   - texto curto: escreve um texto simples;
   - escala: marca um ponto de um intervalo numérico.
2. **Given** a escolha "texto curto", **When** o operador informa texto e obrigatoriedade
   e confirma, **Then** a Pergunta é criada ao final da Seção, sem Opções, escala ou
   desvio.
3. **Given** a escolha "escala", **When** o operador informa texto, obrigatoriedade e
   limites, **Then** a Pergunta é criada com essa escala (ver US9).
4. **Given** a escolha "escolha única" ou "escolha múltipla", **When** o operador cria a
   Pergunta, **Then** ela é criada sem Opções e o operador é levado a adicioná-las (US8).
   Até ter duas Opções, a Pergunta aparece como problema do diagnóstico.
5. **Given** uma Pergunta existente, **When** o operador abre sua edição, **Then**:
   - o tipo aparece como informação fixa, não como campo editável;
   - há a explicação: "o tipo não pode ser trocado; para usar outro tipo, crie uma nova
     Pergunta e remova esta";
   - nenhuma conversão entre tipos é oferecida.
6. **Given** uma Pergunta, **When** o operador altera texto, texto explicativo ou
   obrigatoriedade, **Then** a alteração é gravada. Remover o texto explicativo deixa a
   Pergunta sem ele. Texto da Pergunta vazio é recusado.
7. **Given** três Perguntas numa Seção, **When** o operador move a primeira "para baixo",
   **Then** a ordem passa a ser 2, 1, 3.
8. **Given** uma Pergunta com Opções e desvios, **When** o operador pede a remoção,
   **Then** a confirmação informa que as Opções e os desvios dela também serão removidos.
   Depois de confirmada, nada dela permanece.
9. **Given** uma Pergunta na Seção 2, **When** o operador a move para a Seção 4 da mesma
   Versão, **Then** ela passa ao final da Seção 4 com suas Opções, escala e desvios, e
   deixa de estar na Seção 2.
10. **Given** a criação de Pergunta, **When** o operador procura outro tipo (data, número,
    upload, matriz, grade), **Then** nenhum outro tipo existe na interface.

---

### User Story 8 - Criar, editar, ordenar e remover Opções (Priority: P1)

Numa Pergunta de escolha de Versão em rascunho, o operador:

- adiciona Opções;
- edita seus textos;
- muda a ordem;
- remove Opções;
- marca, no máximo, uma Opção como admitindo complemento textual ("Outro: …").

**Why this priority**: Opções carregam o significado das respostas (Princípio VIII). O
complemento textual é necessário a Q26, Q32 e Q45 (002 FR-042).

**Independent Test**: numa Pergunta de escolha múltipla:

- criar quatro Opções;
- marcar a última com complemento;
- tentar marcar outra (recusado);
- reordenar;
- tentar repetir um texto (recusado);
- remover uma Opção.

A Pergunta reflete cada passo.

**Acceptance Scenarios**:

1. **Given** uma Pergunta de escolha única, **When** o operador adiciona as Opções "Sim"
   e "Não", **Then** elas aparecem nessa ordem.
2. **Given** uma Opção, **When** o operador altera seu texto, **Then** a alteração é
   gravada, e a Opção mantém seu desvio de navegação, se houver (002 FR-041).
3. **Given** uma Pergunta com a Opção "Sim", **When** o operador tenta adicionar outra
   "Sim", **Then** a operação é recusada com "Já existe uma Opção com este texto nesta
   Pergunta".
4. **Given** uma Pergunta de escolha múltipla, **When** o operador marca a Opção "Outro"
   como admitindo complemento, **Then** a marcação é gravada e a Opção aparece como
   "aceita complemento escrito".
5. **Given** uma Pergunta que já tem Opção com complemento, **When** o operador tenta
   marcar outra, **Then** a operação é recusada com explicação:
   - só uma Opção por Pergunta pode aceitar complemento;
   - para trocar, desmarque a atual primeiro.
6. **Given** uma Opção com desvio de navegação, **When** o operador pede sua remoção,
   **Then** a confirmação informa que o desvio também será removido.
7. **Given** uma Pergunta de texto curto ou de escala, **When** sua edição é exibida,
   **Then** nenhuma ação de Opção é oferecida.
8. **Given** uma Pergunta com uma única Opção, **When** o diagnóstico técnico é
   feita, **Then** ela aparece com "precisa de pelo menos duas Opções".

---

### User Story 9 - Configurar escala (Priority: P1)

Para uma Pergunta de escala em Versão em rascunho, o operador configura exatamente o que
a 002 suporta:

- limite inicial;
- limite final;
- rótulo inicial e rótulo final, opcionais.

A interface explica o que essa configuração significa para o respondente.

**Why this priority**: 11 Perguntas da baseline são escalas. A configuração precisa ser
compreensível e fiel à 002 (002 FR-038).

**Independent Test**: criar uma escala de 1 a 5 com rótulos e verificar a explicação.
Tentar 5 a 1 e 3 a 3, que são recusados, e um valor não inteiro, também recusado.
Remover o rótulo inicial e verificar a explicação atualizada.

**Acceptance Scenarios**:

1. **Given** uma Pergunta de escala de 1 a 5, com rótulo inicial "Discordo totalmente" e
   rótulo final "Concordo totalmente", **When** a edição é exibida, **Then** a interface
   explica: "o respondente escolhe um ponto de 1 a 5 (5 pontos); 1 = 'Discordo
   totalmente'; 5 = 'Concordo totalmente'; os pontos intermediários aparecem só com o
   número".
2. **Given** a edição da escala, **When** o operador informa limite inicial maior ou
   igual ao final, **Then** a operação é recusada com explicação, e a escala anterior
   permanece.
3. **Given** a edição da escala, **When** o operador informa um limite que não é número
   inteiro, **Then** o valor é recusado com mensagem associada ao campo.
4. **Given** uma escala sem rótulo inicial, **When** é exibida, **Then** a explicação
   diz que o início não tem rótulo, e nenhum rótulo padrão é inventado.
5. **Given** a edição da escala, **When** é exibida, **Then** não há campos para rótulos
   intermediários, pesos, pontuação ou aparência.

---

### User Story 10 - Configurar navegação já suportada (Priority: P1)

Na Versão em rascunho, o operador configura:

- o **encaminhamento** de uma Seção: para qual Seção seguir quando nenhum desvio é
  acionado;
- para cada Opção de uma Pergunta de **escolha única**, um **desvio**: "ir para a
  Seção Z" ou "finalizar o instrumento".

A interface explica como a jornada atual aplica essa navegação e não oferece nada além
disso.

**Why this priority**: as ramificações fazem parte do significado metodológico do
instrumento (Princípio XIII). A interface não pode inventar semântica (Princípios XXIII e
XXIX; 006/DP-604).

**Independent Test**: cenário de navegação (ver "Cenários ponta a ponta"):

- Seção A com uma Pergunta de escolha única e Opções com desvio para C e sem desvio;
- Seção B com encaminhamento;
- Seção C.

A estrutura e a pré-visualização mostram os destinos.

**Acceptance Scenarios**:

1. **Given** uma Pergunta de escolha única na Seção A e uma Seção C posterior, **When** o
   operador define para a Opção "Sim" o desvio "ir para a Seção C", **Then** o desvio é
   gravado e aparece na Pergunta e na estrutura como "Sim → Seção C".
2. **Given** uma Opção com desvio para a Seção C, **When** o operador o troca para
   "finalizar o instrumento", **Then** a troca acontece de uma vez. Não há estado
   intermediário visível nem possível: em caso de recusa, o desvio anterior permanece.
3. **Given** uma Opção com desvio, **When** o operador escolhe "sem desvio", **Then** a
   Opção volta ao fluxo da Seção.
4. **Given** uma Pergunta de escolha múltipla, texto curto ou escala, **When** sua edição
   é exibida, **Then** nenhuma configuração de desvio é oferecida, e uma explicação diz
   que só Perguntas de escolha única podem ter desvio.
5. **Given** uma Seção, **When** o operador define seu encaminhamento para a Seção N,
   **Then** a estrutura passa a mostrar "depois desta Seção, segue para a Seção N"
   (quando nenhum desvio é acionado). **When** escolhe "seguir a ordem", **Then** o
   encaminhamento é removido.
6. **Given** a configuração de desvio ou de encaminhamento, **When** é exibida, **Then**
   a interface explica a semântica que a jornada atual executa (006 FR-010 a FR-013):
   - o desvio é aplicado quando o respondente conclui a Seção;
   - as demais Perguntas da mesma Seção continuam sendo apresentadas;
   - o desvio da Opção escolhida prevalece sobre o encaminhamento da Seção, que
     prevalece sobre a ordem;
   - Pergunta opcional sem resposta não aciona desvio.
7. **Given** uma Seção que já tem uma Pergunta com desvio, **When** o operador define
   desvio numa segunda Pergunta da mesma Seção, **Then**:
   - a 002 aceita, e o editor grava;
   - a Seção passa a exibir o problema "a jornada atual não consegue aplicar mais de uma
     Pergunta com desvio na mesma Seção";
   - o diagnóstico técnico o lista, como incompatibilidade com a jornada atual;
   - nenhuma prioridade entre os desvios é oferecida ou inventada.
8. **Given** um desvio ou encaminhamento para a própria Seção ou para Seção anterior,
   **When** é gravado em rascunho, **Then** é aceito, como a 002 aceita, e aparece como
   problema do diagnóstico: "o destino precisa ser uma Seção posterior".
9. **Given** qualquer tela de navegação, **When** é exibida, **Then** não há editor de
   condições, combinação E/OU, condição por mais de uma Pergunta, condição de exibição de
   Pergunta, prioridade de regras nem escolha do momento de aplicação.

---

### User Story 11 - Obter o diagnóstico técnico da Versão (Priority: P1)

O operador pede o diagnóstico técnico de uma Versão em rascunho e recebe dois
diagnósticos derivados, apresentados separadamente:

- **A — Estrutura válida** (002);
- **B — Compatível com a jornada atual** (006).

Ele recebe **todos** os problemas de uma vez, em linguagem compreensível, cada um
localizado e com acesso ao ponto de correção. Quando A e B não têm problemas, a Versão
aparece como **"sem impedimentos técnicos conhecidos"**. Isso não é publicação,
aprovação nem autorização.

**Why this priority**: o objetivo do editor é produzir Versões tecnicamente publicáveis
e executáveis pela jornada atual. O diagnóstico reutiliza o que já existe (002 FR-059;
006 FR-016) e não cria validador novo.

**Independent Test**: montar um rascunho com um problema de cada tipo e verificar:

- todos aparecem, separados entre A e B e localizados;
- nada foi gravado pelo diagnóstico;
- corrigindo só os problemas de estrutura, a situação passa a "estrutura válida, mas
  incompatível com a jornada atual";
- corrigindo também a incompatibilidade, a situação passa a "sem impedimentos técnicos
  conhecidos";
- a publicação pelo domínio, executada só no teste, é aceita;
- a verificação de compatibilidade da 006 não aponta nada.

**Acceptance Scenarios**:

1. **Given** uma Versão sem Seções, **When** o operador pede o diagnóstico, **Then** o
   diagnóstico A mostra "a Versão não tem Seções", e a situação é "com problemas de
   estrutura".
2. **Given** uma Versão com uma Seção sem Perguntas, uma Pergunta de escolha com uma
   Opção, um encaminhamento para Seção anterior e duas Perguntas com desvio na mesma
   Seção, **When** o operador pede o diagnóstico, **Then** os quatro problemas aparecem
   de uma vez. Os três primeiros aparecem no diagnóstico A e o último no B. Cada um:
   - identifica o elemento por posição e título ou texto;
   - dá acesso à página onde se corrige.
3. **Given** uma Versão sem problemas de estrutura e com duas Perguntas com desvio na
   mesma Seção, **When** o operador pede o diagnóstico, **Then** a situação é "estrutura
   válida, mas incompatível com a jornada atual". A explicação diz que a jornada atual
   não consegue aplicar mais de uma Pergunta com desvio na mesma Seção.
4. **Given** o diagnóstico concluído, **When** o banco é inspecionado, **Then** nenhum
   dado foi criado ou alterado e o estado da Versão continua RASCUNHO.
5. **Given** o operador corrige um dos problemas, **When** pede o diagnóstico de novo,
   **Then** esse problema não aparece mais e os demais continuam.
6. **Given** uma Versão sem nenhum problema em A e em B, **When** o operador pede o
   diagnóstico, **Then** vê "Sem impedimentos técnicos conhecidos". A mesma página
   explica que:
   - isso não significa aprovação, homologação, autorização nem publicação;
   - a publicação não está disponível neste editor, porque depende da definição
     institucional de quem pode publicar.
7. **Given** uma Versão sem impedimentos técnicos conhecidos, **When** o operador altera
   algo que cria um problema, **Then** o próximo diagnóstico, ou a estrutura, já mostra
   o problema. Nenhuma situação ficou gravada.
8. **Given** uma Versão publicada, **When** o operador a abre, **Then** não há
   diagnóstico técnico a pedir. Ela já está publicada, e o editor mostra a data de
   publicação.

---

### User Story 12 - Consultar Versão publicada sem poder editá-la (Priority: P2)

O operador abre uma Versão publicada, consulta sua estrutura e cada Seção e Pergunta,
pré-visualiza e cria nova Versão a partir dela. Nenhum controle de edição existe, e
qualquer tentativa de escrita é recusada.

**Why this priority**: preserva a imutabilidade histórica (Princípio VIII; 002 FR-016 e
FR-017). É P2 porque a garantia já existe no domínio. Aqui ela fica visível e protegida
também na interface.

**Independent Test**:

- abrir a cópia publicada de demonstração e verificar que nenhuma página dela oferece
  ação de edição, ordenação, remoção, desvio ou verificação;
- enviar diretamente ao editor uma requisição de alteração para essa Versão e verificar
  a recusa;
- confirmar que o conteúdo continua idêntico.

**Acceptance Scenarios**:

1. **Given** uma Versão publicada, **When** o operador a abre, **Then** vê a estrutura,
   a indicação "Publicada em <data> — não pode ser alterada" e as ações "pré-visualizar"
   e "criar nova Versão a partir desta". Nenhuma outra ação é oferecida.
2. **Given** uma Seção ou Pergunta de Versão publicada, **When** o operador a consulta,
   **Then** vê seu conteúdo somente para leitura.
3. **Given** uma requisição de alteração dirigida a qualquer elemento de Versão publicada
   (por exemplo, formulário antigo, endereço digitado ou Versão publicada por outra via
   enquanto a página estava aberta), **When** chega ao editor, **Then** ela é recusada com
   a mensagem: "esta Versão está publicada e não pode ser alterada; para mudar o
   instrumento, crie uma nova Versão a partir dela". Nada é gravado.
4. **Given** uma Versão publicada, **When** qualquer página do editor é exibida, **Then**
   não há "despublicar", "corrigir", "editar mesmo assim" nem exceção para nenhum
   operador.

---

### User Story 13 - Pré-visualizar a Versão (Priority: P2)

O operador pré-visualiza a Versão, em rascunho ou publicada, para conferir:

- textos e ordem;
- agrupamento em Seções;
- controles de cada tipo;
- Opções e escalas.

Os desvios aparecem como anotações. Nada é gravado, e a pré-visualização não finge ser
uma aplicação real.

**Why this priority**: a conferência visual reduz erros de composição. É P2 porque a
estrutura (US5) já permite conferir o conteúdo.

**Independent Test**: pré-visualizar uma cópia da baseline e verificar:

- todas as Seções aparecem na ordem, com textos, controles por tipo, Opções e escalas;
- os desvios aparecem como anotações;
- não há botão que envie respostas;
- nenhuma Participação, Campanha ou Resposta foi criada;
- nenhum dado foi alterado.

**Acceptance Scenarios**:

1. **Given** uma Versão, **When** o operador abre a pré-visualização, **Then** vê o
   título apresentado e o texto de abertura, as Seções na ordem e o texto de
   encerramento.
2. **Given** uma Pergunta de cada tipo, **When** é pré-visualizada, **Then** aparece com
   o controle correspondente ao que o respondente veria:
   - Opções exclusivas para escolha única;
   - caixas de marcação para escolha múltipla;
   - campo de texto para texto curto;
   - pontos numerados com rótulos de extremidade para escala.
3. **Given** a pré-visualização, **When** é exibida, **Then**:
   - em lugar visível e no título da página, está identificada como pré-visualização:
     "nada é gravado; os desvios não são executados";
   - não há ação de enviar, salvar ou concluir;
   - os controles não gravam nada.
4. **Given** uma Opção com desvio, **When** é pré-visualizada, **Then** aparece uma
   anotação como "→ segue para a Seção 4" ou "→ finaliza o instrumento". A Seção com
   encaminhamento também mostra uma anotação.
5. **Given** a pré-visualização de qualquer Versão, **When** o banco é inspecionado
   antes e depois, **Then** não houve criação nem alteração de Participação, Campanha,
   Resposta, Versão ou qualquer outro dado.
6. **Given** uma Seção sem título, **When** é pré-visualizada, **Then** aparece de forma
   compreensível e com hierarquia de cabeçalhos coerente.

---

### User Story 14 - Entender problemas e recusas em linguagem operacional (Priority: P2)

Toda recusa de operação e todo problema do diagnóstico aparecem para o operador:

- em português operacional;
- associados ao campo ou elemento envolvido;
- com o caminho para resolver.

Nunca aparecem como código, identificador técnico ou mensagem do sistema.

**Why this priority**: sem isso o editor exigiria conhecer o modelo interno, contrariando
o objetivo da feature e a 008 (FR-067/FR-068).

**Independent Test**: provocar pelo editor cada recusa que a 002 pode produzir nos fluxos
oferecidos e cada problema do diagnóstico. Verificar que cada mensagem:

- é operacional;
- localiza o elemento;
- não contém identificador interno, nome de classe, código de motivo ou código de
  requisito.

**Acceptance Scenarios**:

1. **Given** um formulário recusado, **When** a página volta, **Then**:
   - um resumo dos erros aparece no início do conteúdo principal;
   - cada erro está associado ao campo;
   - os valores digitados são preservados.
2. **Given** uma recusa causada por mudança concorrente (elemento removido, posição
   ocupada, Versão publicada nesse intervalo), **When** a página volta, **Then** a
   mensagem diz que o conteúdo mudou desde que a página foi aberta e mostra o estado
   atual. Nada é gravado parcialmente.
3. **Given** uma falha inesperada, **When** acontece, **Then** o operador vê uma
   mensagem genérica, sem detalhes técnicos, e nada é gravado parcialmente.

---

### User Story 15 - Acessibilidade e responsividade básicas (Priority: P3)

O editor pode ser usado só por teclado, com leitor de tela e em tela pequena com
razoável conforto.

**Why this priority**: acessibilidade é requisito, não acabamento (Princípio XX). É P3
porque o editor é usado por operadores em contexto não produtivo, e o requisito é
"básico", sem certificação.

**Independent Test**: percorrer o cenário principal só com teclado e verificar:

- foco visível;
- cabeçalhos hierárquicos;
- rótulos associados;
- erros associados;
- estados escritos em texto;
- ausência de rolagem horizontal em tela estreita.

**Acceptance Scenarios**:

1. **Given** qualquer página do editor, **When** navegada por teclado, **Then** todos os
   controles são alcançáveis em ordem lógica, com foco visível.
2. **Given** as ações "mover para cima/baixo" e "remover", **When** lidas por leitor de
   tela, **Then** cada uma identifica o elemento, por exemplo "Mover para cima a
   Pergunta 3: Qual sua idade?".
3. **Given** uma tela de 320 px de largura ou zoom de 200%, **When** qualquer página é
   exibida, **Then** não há rolagem horizontal da página, e o conteúdo continua legível
   e operável.
4. **Given** estados, tipos, obrigatoriedade e problemas, **When** exibidos, **Then**
   nunca dependem apenas de cor.

---

### Cenários ponta a ponta *(mandatory para esta feature)*

**Cenário principal** (tudo pela interface, sem editar código, banco ou console;
pré-condição: modo não produtivo ligado e baseline materializada):

1. O operador abre o editor e vê a lista de Pesquisas (US1).
2. Abre "Pesquisa Institucional de Egressos" e vê as Versões (US1).
3. Abre a baseline e consulta sua estrutura (US5).
4. Cria a Versão "Cópia de trabalho" a partir da baseline (US4).
5. Na cópia, altera o texto de uma Pergunta (US7).
6. Adiciona uma nova Pergunta de escolha única numa Seção (US7).
7. Cria duas Opções para ela (US8).
8. Muda a ordem: a nova Pergunta sobe uma posição e as Opções são invertidas (US7, US8).
9. Define a nova Pergunta como obrigatória (US7).
10. Consulta a estrutura e a pré-visualização da cópia (US5, US13).
11. Pede o diagnóstico técnico (US11).
12. Corrige um problema apontado. Para produzi-lo, por exemplo, adiciona antes uma
    Pergunta de escolha sem Opções, depois adiciona as Opções ou remove a Pergunta
    (US11).
13. Verifica de novo e obtém "sem impedimentos técnicos conhecidos" (US11).
14. Abre uma Versão publicada (a cópia de demonstração da 008, ou outra publicada
    previamente) e constata que nada pode ser editado (US12).

Ao final:

- a baseline continua equivalente à declarada pela 003;
- nenhuma Campanha, Participação ou Resposta foi criada;
- nenhuma Versão foi publicada pelo editor.

**Cenário de navegação** (numa Versão de teste, criada vazia ou a partir de outra):

1. Criar a Seção A, a Seção B e a Seção C, nessa ordem.
2. Na Seção A, criar uma Pergunta de escolha única com as Opções "Sim" e "Não".
3. Definir: "Não" → ir para a Seção C. "Sim" fica sem desvio, então segue a ordem para
   B.
4. Dar à Seção B e à Seção C ao menos uma Pergunta cada uma.
5. Conferir na estrutura e na pré-visualização:
   - "Não → Seção C";
   - "Sim" segue a ordem;
   - B segue a ordem para C;
   - C finaliza.
6. Pedir o diagnóstico técnico: sem impedimentos técnicos conhecidos.
7. Provocar e observar:
   - (a) uma segunda Pergunta de escolha única com desvio na Seção A: problema "a jornada
     atual não consegue aplicar…";
   - (b) mover a Seção C para antes da Seção A: o desvio de "Não" passa a apontar para
     Seção anterior, e aparece o problema "o destino precisa ser uma Seção posterior".
8. Desfazer (a) e (b) e obter de novo "sem impedimentos técnicos conhecidos".

Em nenhum momento a interface oferece condição composta, prioridade, momento de aplicação
ou motor novo.

### Telas e estados

A arquitetura visual pertence ao plan. Os estados abaixo são os mínimos a representar.

| Tela | Conteúdo essencial | Estados e variações |
|------|--------------------|---------------------|
| Lista de Pesquisas | Nome de cada Pesquisa, quantidade de Versões; ação "criar Pesquisa" | Sem Pesquisas; com Pesquisas; aviso de nome repetido na criação |
| Pesquisa | Nome; Versões com designação, estado escrito, data de publicação, origem; ações "criar Versão" e "criar nova Versão a partir desta" por Versão | Sem Versões; só rascunhos; só publicadas; misto |
| Versão: estrutura | Cabeçalho (Pesquisa, designação, estado, origem); textos da Versão; totais; Seções em ordem com suas Perguntas resumidas, destinos e sinais de problema | **Rascunho**: ações de edição, ordenação, remoção, adicionar Seção, verificar, pré-visualizar. **Publicada**: somente leitura, pré-visualizar, nova Versão a partir desta |
| Dados da Versão (rascunho) | Designação, título apresentado, texto de abertura, texto de encerramento | Edição; recusa por designação repetida |
| Seção | Título, texto introdutório, encaminhamento; lista das Perguntas com tipo, obrigatoriedade, desvio, mover, remover, editar; "adicionar Pergunta" | Rascunho (edição) ou publicada (leitura); Seção sem título; Seção sem Perguntas; problema do diagnóstico sinalizado |
| Criar Pergunta | Escolha entre os quatro tipos, com descrição; texto, texto explicativo, obrigatoriedade; para escala, limites e rótulos | Passo de escolha de tipo e passo de dados, ou um só passo; decisão do plan |
| Pergunta | Tipo fixo com explicação; texto, explicativo, obrigatoriedade; escala com explicação (se escala); Opções com mover, remover, complemento e desvio (se escolha); mover para outra Seção | Rascunho ou publicada; por tipo; sem Opções; problema sinalizado |
| Confirmação de remoção | Elemento a remover e consequências (Opções e desvios removidos junto) | Seção (só se vazia e não referenciada), Pergunta, Opção |
| Diagnóstico técnico | Diagnóstico A (estrutura válida) e diagnóstico B (compatível com a jornada atual), cada um com seus problemas localizados e acesso à correção; situação derivada; aviso de que o resultado não é aprovação e de que publicar não está disponível | Com problemas de estrutura; estrutura válida, mas incompatível com a jornada atual; sem impedimentos técnicos conhecidos |
| Pré-visualização | Título, abertura, Seções em ordem com controles por tipo, anotações de desvio e encaminhamento, encerramento; aviso permanente de pré-visualização | Rascunho ou publicada; Seção sem título; Pergunta com lista longa de Opções |
| Recusa e erro | Resumo de erros no topo; erro junto ao campo; valores preservados; mensagem de mudança concorrente; erro inesperado genérico | — |
| Indisponível | Editor desligado fora do modo não produtivo | Modo desligado: nada do editor responde |

### Edge Cases

- **Baseline em RASCUNHO**: editável como qualquer rascunho, sem exceção pelo nome
  (FR-009).
  - Editar a baseline no lugar faz a materialização da 003 recusar depois, por
    divergência explícita (003 FR-031 a FR-033), e com isso o preparo da demonstração
    da 008.
  - O editor recomenda, na página da Versão em rascunho, criar nova Versão a partir dela
    quando a intenção for experimentar. Essa recomendação é genérica, não específica da
    baseline.
  - Os testes desta feature nunca editam a baseline (FR-099).
  - Se ela for alterada manualmente no ambiente de demonstração, a recusa da
    materialização da 003 por divergência é **comportamento esperado**. A 009 não a
    contorna, não repara a baseline nem oferece "restaurar referência".
  - A proteção institucional da referência é DP-902, que continua aberta. Não há
    publicação automática, marcação de referência, estado especial, permissão especial
    nem bloqueio por código fixo.
- **Pesquisa com nome igual ao da baseline**: a 002 permite. A 003 recusa materializar
  se houver mais de uma Pesquisa com o nome da baseline (003 FR-031: recusa por nome ambíguo).
  - O aviso de nome repetido (FR-012) cobre esse caso de forma genérica.
  - O editor não proíbe.
- **Versão em rascunho referenciada por Campanha ainda não aberta**: a 004 permite
  Campanha com Versão em qualquer estado antes da abertura (004 FR-007, FR-008). O editor
  não consulta nem exibe Campanhas (FR-104). Editar esse rascunho é permitido, como na
  002.
- **Versão publicada usada por Campanha**: imutável como toda publicada. Nada muda.
- **Duas pessoas editando o mesmo rascunho**: cada operação é atômica e serializada pela
  002.
  - A última operação aceita prevalece.
  - Formulário baseado em estado antigo pode ser recusado, por exemplo por posição
    ocupada, elemento inexistente ou Versão publicada no intervalo. A recusa vem com a
    mensagem de mudança concorrente (US14, cenário 2).
  - Não há bloqueio de edição, sessão de edição nem histórico (FR-108).
- **Versão publicada enquanto a página de edição estava aberta** (por exemplo, pelo
  preparo da demonstração ou por teste): a próxima gravação é recusada como "Versão
  publicada" (US12, cenário 3).
- **Pergunta de escolha sem Opções**: aceita em rascunho; aparece como problema.
- **Seção sem Perguntas**: aceita em rascunho; aparece como problema. Remover a Seção é
  permitido se ela não for referenciada.
- **Seção sem título** (S13 da baseline): exibida como "Seção sem título", com posição e
  hierarquia coerente (auditoria UX-11).
- **Desvio cujo destino coincide com o fluxo padrão** (Q51): aceito e exibido como
  qualquer desvio. Não é problema (002, Edge Cases).
- **Desvio em Pergunta opcional**: aceito. A interface explica que, sem resposta, o
  desvio não é acionado (006 FR-012 c). Não é problema.
- **Pergunta com desvio no meio da Seção** (Q46 seguida de Q47 e Q48; Q33 como 14ª
  Pergunta da Seção): a interface explica que as demais Perguntas da Seção continuam
  sendo apresentadas. Não é problema (006 FR-011; 003/DP-302; 006/DP-604).
- **Encaminhamento para a própria Seção**: a 002 aceita em rascunho, e o diagnóstico A
  aponta. O editor PODE omitir a própria Seção da lista de destinos de encaminhamento
  sem com isso criar regra nova. Destino para Seção anterior continua possível e
  apontado.
- **Reordenar Seções invalida destinos**: a ordem nova é gravada. Desvios e
  encaminhamentos que deixarem de apontar para Seção posterior aparecem como problemas.
  O editor não corrige nem altera destinos automaticamente.
- **Mover Pergunta com desvio para uma Seção que já tem Pergunta com desvio**: aceito
  pela 002. Aparece como problema da jornada atual.
- **Mover Pergunta para a mesma Seção**: equivale a não mover. O editor PODE não oferecer
  a Seção atual como destino.
- **Trocar a Opção que aceita complemento**: desmarcar a atual e marcar a outra são duas
  ações. Tentar marcar a segunda primeiro é recusado com explicação (US8, cenário 5).
- **Opção "Outro:" com dois-pontos no texto**: o texto é gravado e exibido exatamente
  como informado. A pré-visualização não acrescenta pontuação (auditoria UX-14).
- **Listas extensas de Opções** (77 em Q19): a página da Pergunta continua utilizável.
  A pré-visualização PODE usar a mesma forma compacta que a 008 usa para listas longas.
  A estrutura mostra só a quantidade.
- **Erro de grafia em Versão publicada** ("Corcordo totalmente"): não corrigível. O
  caminho é nova Versão (002/DP-003).
- **Q1 (termos) e Q10–Q19**: tratadas como quaisquer Perguntas.
  - Não há marcação de consentimento, ocultação, preenchimento automático nem vínculo
    com Conclusão Acadêmica (FR-101, FR-102).
  - Na cópia, permanecem como na origem.
- **Texto só com espaços**: recusado para textos obrigatórios. Para textos opcionais, o
  editor trata campo vazio ou só com espaços como "sem texto", porque a 002 não aceita
  texto opcional vazio e representa ausência explicitamente (002 FR-010, FR-025). Isso
  é tradução de formulário, não regra nova. **[Hipótese]**
- **Limites de escala negativos ou zero**: aceitos se forem inteiros e o início for menor
  que o fim, como na 002. O editor não restringe além disso.
- **Endereço de elemento inexistente ou de outra Versão**: a página responde como
  inexistente, sem detalhes técnicos.
- **Editor com o modo não produtivo desligado**: nada do editor responde (FR-002).

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII):

- **[Const.]**: decorre da Constituição.
- **[002]**, **[003]**, **[006]**, **[008]**: decorre de feature anterior.
- **[Arquitetura]**: decisão arquitetural.
- **[Hipótese]**: escolha de produto reversível.
- **[Escopo]**: decisão de escopo desta feature, revisável por feature futura.

Nenhum requisito desta feature cria capacidade do instrumento, altera pergunta herdada ou
decide regra institucional.

### Functional Requirements

**Acesso e natureza não produtiva**

- **FR-001**: O editor DEVE estar disponível somente pela entrada interna não produtiva
  já usada pelo projeto (o modo de demonstração local da 008). Não DEVE haver mecanismo
  de acesso novo. [008; Const. — XV; XXII]
- **FR-002**: Com o modo não produtivo desligado, o padrão, nenhuma página do editor
  DEVE responder. O comportamento DEVE ser o mesmo das páginas da 008. [008; Const. —
  XVI]
- **FR-003**: Toda página do editor DEVE exibir aviso permanente de que:
  - é ambiente não produtivo;
  - não há autenticação;
  - o acesso ao editor **não** representa competência institucional para elaborar ou
    publicar o instrumento. [Const. — X; 008]
- **FR-004**: O editor NÃO DEVE criar usuário, cadastro, senha, papel, permissão, perfil
  CPAEG ou CSAEG, administrador por unidade, lista de acesso por Pesquisa nem qualquer
  modelo de autorização. Autorização institucional é da Feature 010 (DP-901). [Const. —
  X; XV; XXIX]
- **FR-005**: O editor NÃO DEVE exigir nem usar a seleção de Pessoa fictícia da entrada
  de demonstração da 008. Ele independe de Pessoa, Conclusão Acadêmica e Participação.
  [002 FR-065; Arquitetura]
- **FR-006**: O editor DEVE ser uma área distinta da jornada do egresso. A jornada da
  008 NÃO DEVE apresentar o editor como parte do fluxo do egresso. A documentação da
  feature DEVE declarar que o editor não deve ser habilitado em ambiente produtivo antes
  da Feature 010. [Const. — X; XVI]

**Pesquisas**

- **FR-007**: O editor DEVE listar as Pesquisas existentes pelo nome administrativo, com
  a quantidade de Versões de cada uma, e permitir abrir cada uma. [002 FR-001, FR-004]
- **FR-008**: O editor DEVE permitir criar Pesquisa informando somente o nome
  administrativo, pela operação de criação de Pesquisa da 002. NÃO DEVE pedir nem gravar
  outro atributo. [002 FR-002; Const. — XXII]
- **FR-009**: O editor NÃO DEVE conter exceção, tratamento especial, proteção ou
  ocultação baseada no nome de Pesquisa ou na designação de Versão, inclusive da
  baseline da 003. [Const. — XXII; Escopo]
- **FR-010**: O editor NÃO DEVE oferecer exclusão de Pesquisa nem de Versão. [002 FR-018]
- **FR-011**: O editor NÃO DEVE oferecer renomear Pesquisa nesta feature: não há
  consumidor, e o nome da Pesquisa da baseline é usado pela materialização da 003.
  [Escopo; Const. — XXII]
- **FR-012**: Ao criar Pesquisa com nome idêntico ao de uma Pesquisa existente, o editor
  DEVE avisar e pedir confirmação explícita antes de criar. Ele NÃO DEVE proibir a
  criação, porque a 002 não proíbe. [Hipótese]

**Versões**

- **FR-013**: Para uma Pesquisa, o editor DEVE listar suas Versões com:
  - designação;
  - estado escrito ("Rascunho" ou "Publicada"), sem depender só de cor;
  - data de publicação, quando publicada;
  - Versão de origem, quando houver.

  [002 FR-063; Const. — XX]
- **FR-014**: O editor DEVE permitir criar Versão vazia em RASCUNHO numa Pesquisa,
  informando a designação, pela operação de criação de Versão da 002. [002 FR-005,
  FR-006, FR-011]
- **FR-015**: O editor DEVE permitir criar nova Versão a partir de qualquer Versão
  existente, em rascunho ou publicada, informando a designação. Ele DEVE usar
  exclusivamente a operação da 002 de criar Versão a partir de outra. NÃO DEVE copiar
  elementos por conta própria. [002 FR-019 a FR-022]
- **FR-016**: O editor NÃO DEVE apresentar nem criar correspondência entre elementos de
  Versões diferentes. Ele só informa a Versão de origem. [002 FR-023; 002/DP-006]
- **FR-017**: O editor NÃO DEVE criar estado de Versão além de RASCUNHO e PUBLICADA, nem
  rótulo persistido como "pronta", "em aprovação", "aprovada", "homologada", "vigente" ou
  "arquivada". [002 FR-008, FR-011; Const. — X]

**Versão publicada**

- **FR-018**: Em Versão PUBLICADA, o editor DEVE permitir somente:
  - consultar a estrutura, as Seções e as Perguntas;
  - pré-visualizar;
  - criar nova Versão a partir dela.

  NÃO DEVE exibir nenhum controle de edição, ordenação, remoção, desvio, encaminhamento,
  complemento ou adição. [002 FR-016; Const. — VIII]
- **FR-019**: Toda requisição de escrita que chegue ao editor para Versão publicada ou
  seus elementos DEVE ser recusada, com mensagem que indica o caminho seguro de criar
  nova Versão a partir dela. Nada pode ser gravado. Isso vale também quando a página foi
  aberta antes da publicação. A recusa DEVE decorrer da regra da 002, e o editor NÃO
  DEVE reimplementá-la. [002 FR-016, FR-017; Const. — VIII]
- **FR-020**: O editor NÃO DEVE oferecer despublicar, voltar a rascunho, corrigir no
  lugar, "hotfix", alteração editorial pós-publicação, exceção de superusuário nem
  qualquer outro caminho de alteração de Versão publicada. [002 FR-013, FR-017;
  002/DP-003]

**Princípios de escrita em Versão em rascunho**

- **FR-021**: Toda gravação do editor DEVE ser feita pelas operações públicas da 002.
  - O editor NÃO DEVE gravar diretamente no armazenamento.
  - O editor NÃO DEVE criar camada de serviço paralela que duplique essas operações.
  - Pequenas composições de operações da 002 numa única ação são permitidas, desde que
    tudo-ou-nada: por exemplo, trocar o desvio de uma Opção ou reordenar a partir de
    "mover para cima". [Arquitetura; Const. — XXII]
- **FR-022**: O editor NÃO DEVE reimplementar nos formulários regras que pertencem ao
  domínio:
  - unicidade de designação;
  - texto obrigatório;
  - Opção repetida;
  - complemento único;
  - escala válida;
  - tipo compatível;
  - imutabilidade.

  A fonte da recusa DEVE ser sempre a operação da 002. O formulário PODE apenas
  converter a entrada para a forma esperada (por exemplo, número inteiro e campo vazio =
  ausente) e avisar sobre entrada que não pode ser convertida. [Arquitetura; Const. —
  XXII]
- **FR-023**: Toda ação de escrita DEVE ser tudo-ou-nada. Em caso de recusa, o estado
  consultado em seguida DEVE ser idêntico ao anterior. [002 FR-060]
- **FR-024**: Toda remoção DEVE exigir confirmação explícita numa etapa própria, que
  identifique o elemento e as consequências. [Hipótese; Const. — XIV]
- **FR-025**: Nenhuma consulta do editor (listas, estrutura, páginas de leitura,
  diagnóstico técnico, pré-visualização) DEVE gravar ou alterar dado. Escrita só
  ocorre por ação explícita de envio, com proteção contra requisição forjada como na
  008. [Arquitetura; 008]

**Dados da Versão**

- **FR-026**: Em rascunho, o editor DEVE permitir alterar a designação e os textos
  opcionais da Versão (título apresentado, texto de abertura, texto de encerramento),
  inclusive removê-los. Textos ausentes DEVEM aparecer como ausentes, sem valor padrão
  inventado. [002 FR-010, FR-012]

**Seções**

- **FR-027**: Em rascunho, o editor DEVE permitir adicionar Seção, com título e texto
  introdutório opcionais. A Seção nova entra ao final da ordem. [002 FR-024 a FR-026;
  Hipótese quanto à posição]
- **FR-028**: Em rascunho, o editor DEVE permitir alterar e remover o título e o texto
  introdutório de uma Seção. [002 FR-025]
- **FR-029**: Em rascunho, o editor DEVE permitir remover Seção conforme a 002: somente
  vazia e não referenciada por desvio ou encaminhamento. Quando a remoção for recusada,
  a explicação DEVE dizer o que impede, em linguagem operacional:
  - "remova ou mova as Perguntas antes";
  - ou a identificação dos desvios e encaminhamentos que apontam para ela.

  [002 FR-061]
- **FR-030**: O editor NÃO DEVE criar conceito de página, passo, bloco, componente,
  passagem ou assistente diferente de Seção. [002 FR-027; Const. — XXIII]

**Perguntas**

- **FR-031**: Em rascunho, o editor DEVE permitir criar Pergunta numa Seção, informando:
  - tipo;
  - texto;
  - obrigatoriedade;
  - texto explicativo, opcional;
  - para escala, a configuração da escala.

  A Pergunta nova entra ao final da Seção. [002 FR-028 a FR-030; Hipótese quanto à
  posição]
- **FR-032**: O editor DEVE oferecer **exatamente** os quatro tipos da 002 (escolha
  única, escolha múltipla, texto curto, escala), com descrição curta do que o
  respondente faz em cada um. Nenhum outro tipo, subtipo, validação de formato, máscara,
  limite de seleções ou variante de apresentação PODE ser oferecido. [002 FR-034 a
  FR-038; Const. — XXIII; 002/DP-005]
- **FR-033**: O tipo DEVE ser escolhido na criação e, depois, exibido como informação
  fixa, nunca como campo editável. [002 FR-062]
- **FR-034**: A edição de Pergunta DEVE explicar que o tipo não muda e que, para usar
  outro tipo, cria-se nova Pergunta e remove-se a atual. [002 FR-062; Const. — XIV]
- **FR-035**: O editor NÃO DEVE oferecer conversão entre tipos, nem automática nem
  assistida, nem "trocar tipo" que remova e recrie em uma ação. [002 FR-062; Escopo]
- **FR-036**: Em rascunho, o editor DEVE permitir alterar texto, texto explicativo
  (inclusive removê-lo) e obrigatoriedade. A obrigatoriedade DEVE aparecer como
  "Obrigatória" ou "Opcional" escritos. [002 FR-029 a FR-031]
- **FR-037**: Em rascunho, o editor DEVE permitir remover Pergunta. A confirmação DEVE
  informar que suas Opções, sua escala e seus desvios também serão removidos.
  [002 FR-061]
- **FR-038**: O editor NÃO DEVE atribuir à Pergunta numeração de apresentação gravada
  (Q1…), código, categoria, tag, indicador associado, origem de dado ou qualquer
  atributo sem consumidor. A posição exibida decorre da ordem. [002 FR-033; Const. —
  XXII]
- **FR-039**: Em rascunho, o editor DEVE permitir mover uma Pergunta para outra Seção da
  mesma Versão, pela operação da 002. A Pergunta entra ao final da Seção de destino e
  mantém suas Opções, escala e desvios. [002 US2 cenário 6; Hipótese]
- **FR-040**: O editor NÃO DEVE oferecer banco de perguntas, cópia de Pergunta entre
  Versões, modelos de Pergunta nem reutilização de Perguntas. [002 FR-032; Const. —
  XXIII]

**Opções**

- **FR-041**: Para Pergunta de escolha única ou múltipla em rascunho, o editor DEVE
  permitir adicionar Opção (ao final), alterar seu texto, mudar sua ordem e removê-la.
  Para Perguntas de texto curto e escala, nenhuma ação de Opção DEVE ser oferecida.
  [002 FR-040, FR-041]
- **FR-042**: O editor DEVE permitir marcar e desmarcar uma Opção como "aceita
  complemento escrito". A interface DEVE indicar qual Opção da Pergunta tem essa marca.
  A regra de no máximo uma por Pergunta é a da 002, e a recusa DEVE vir dela. [002
  FR-042]
- **FR-043**: Alterar o texto de uma Opção NÃO DEVE alterar seu desvio de navegação nem
  sua marca de complemento. [002 FR-041]
- **FR-044**: Os textos de Opção DEVEM ser gravados e exibidos exatamente como
  informados, sem acréscimo ou remoção de pontuação. [002 FR-039, FR-041]
- **FR-045**: O editor NÃO DEVE oferecer para Opção atributo além de texto, posição,
  complemento e desvio. Ficam excluídos, entre outros:
  - valor, código, peso e pontuação;
  - exclusividade e "nenhuma das anteriores";
  - Opção oculta;
  - lista compartilhada;
  - lista importada;
  - lista alimentada por fonte externa.

  [002 FR-036, FR-043; Const. — XXII; XXIII]
- **FR-046**: O editor NÃO DEVE limitar a quantidade de Opções de uma Pergunta. [002
  FR-044]
- **FR-047**: A confirmação de remoção de Opção com desvio DEVE informar que o desvio
  também será removido. [002 FR-061]

**Escala**

- **FR-048**: Para Pergunta de escala, o editor DEVE permitir configurar somente limite
  inicial, limite final, rótulo inicial e rótulo final. Os rótulos são opcionais. Na
  criação, os limites são obrigatórios. Em rascunho, eles PODEM ser alterados depois.
  [002 FR-038, FR-062]
- **FR-049**: A interface DEVE explicar a escala configurada em linguagem compreensível:
  - intervalo e quantidade de pontos;
  - qual rótulo corresponde a qual extremidade;
  - ausência de rótulo, quando for o caso;
  - pontos intermediários sem rótulo.

  [Const. — XIV]
- **FR-050**: O editor NÃO DEVE oferecer rótulos intermediários, pesos, pontuação,
  inversão, aparência (estrelas, emojis, deslizante) nem passo diferente de 1. [002
  FR-038; Const. — XXII]

**Navegação**

- **FR-051**: Para Pergunta de **escolha única** em rascunho, o editor DEVE permitir, por
  Opção, escolher entre três destinos:
  - "sem desvio";
  - "ir para a Seção …", entre as Seções da mesma Versão;
  - "finalizar o instrumento".

  Ele DEVE usar as operações de regra da 002. [002 FR-050 a FR-052]
- **FR-052**: A troca de destino de uma Opção que já tem desvio DEVE ser tudo-ou-nada.
  Ao final, a Opção tem exatamente o destino novo ou, em caso de recusa, o anterior.
  [002 FR-052, FR-060]
- **FR-053**: Para Perguntas de escolha múltipla, texto curto e escala, nenhuma
  configuração de desvio DEVE ser oferecida. Uma explicação DEVE informar que só
  escolha única admite desvio. [002 FR-050, FR-056]
- **FR-054**: Em rascunho, o editor DEVE permitir definir o encaminhamento de uma Seção
  para outra Seção da mesma Versão e removê-lo ("seguir a ordem"). [002 FR-049]
- **FR-055**: O editor NÃO DEVE restringir a lista de destinos por posição. A
  verificação de "destino posterior" pertence à 002 e aparece no diagnóstico (FR-067). A
  própria Seção PODE ser omitida da lista de destinos de encaminhamento, por não ter
  significado de destino. [002 FR-055, FR-059 d; Arquitetura]
- **FR-056**: Nas telas de navegação, o editor DEVE explicar a semântica que a jornada
  atual executa, sem criar outra:
  - o desvio é aplicado ao concluir a Seção que contém a Pergunta;
  - as demais Perguntas da Seção continuam sendo apresentadas;
  - precedência: desvio da Opção escolhida, depois encaminhamento da Seção, depois
    ordem, depois finalização;
  - Pergunta opcional sem resposta não aciona desvio.

  O texto DEVE deixar claro que essa é a semântica atual, e não regra permanente
  (006/DP-604). [006 FR-010 a FR-013; Const. — XXIX]
- **FR-057**: Quando uma Seção tiver mais de uma Pergunta com desvio, o editor DEVE
  aceitar a gravação, porque a 002 aceita, e DEVE apresentar o fato como
  incompatibilidade com a jornada atual (diagnóstico B). O editor NÃO DEVE:
  - escolher, ordenar ou priorizar desvios;
  - impedir a gravação;
  - interpretar silenciosamente a estrutura.

  [006 FR-016; 006/DP-604]
- **FR-058**: O editor NÃO DEVE criar:
  - editor de condições;
  - condição composta (E/OU);
  - condição sobre várias Perguntas;
  - condição sobre escolha múltipla, texto ou escala;
  - condição de exibição de Pergunta ou Seção;
  - prioridade de regras;
  - atributo de momento de aplicação;
  - salto imediato dentro da Seção;
  - variáveis, expressões ou linguagem de regras.

  [002 FR-053, FR-056, FR-057; 006 FR-013; Const. — XXIII]
- **FR-059**: O editor NÃO DEVE alterar destinos automaticamente quando Seções são
  reordenadas, movidas ou removidas. Destinos que se tornem inválidos aparecem como
  problemas do diagnóstico. [Const. — XXIX; Arquitetura]
- **FR-060**: A estrutura e a página da Seção DEVEM mostrar, em palavras, o destino de
  cada Opção com desvio e o encaminhamento de cada Seção. [Const. — XIV]

**Ordenação**

- **FR-061**: Em rascunho, o editor DEVE permitir mudar a ordem de Seções na Versão, de
  Perguntas na Seção e de Opções na Pergunta, pelo menos por "mover para cima" e "mover
  para baixo". [002 FR-045 a FR-047; Hipótese]
- **FR-062**: O editor PODE oferecer, adicionalmente, a indicação de posição explícita.
  NÃO DEVE exigir arrastar e soltar. Ordenação NÃO DEVE depender de biblioteca de
  terceiros. [Const. — XXII]
- **FR-063**: "Mover para cima" não DEVE ser oferecido para o primeiro elemento do
  conjunto, nem "mover para baixo" para o último. [Const. — XIV]
- **FR-064**: Cada ação de ordenação DEVE ter nome acessível que identifique o elemento e
  a direção. Depois da ação, o operador DEVERIA continuar no mesmo contexto da página,
  próximo ao elemento movido. [Const. — XX]

**Visão da estrutura**

- **FR-065**: A página da Versão DEVE apresentar a estrutura de leitura de US5:
  - cabeçalho;
  - textos da Versão;
  - totais de Seções e Perguntas;
  - Seções na ordem, com título ou "Seção sem título", quantidade de Perguntas e
    destino;
  - para cada Pergunta: posição, texto, tipo em palavras, obrigatoriedade escrita,
    quantidade de Opções ou intervalo da escala, e indicação de desvio;
  - sinais de problema do diagnóstico por elemento.

  NÃO DEVE conter campos de edição nem listar todas as Opções de todas as Perguntas.
  NÃO DEVE conter gráfico, indicador, contagem de respostas ou outro elemento de painel.
  [Const. — XIV; XIX; XXII]

**Diagnóstico técnico**

- **FR-066**: Para Versão em rascunho, o editor DEVE permitir pedir o diagnóstico
  técnico. Ele DEVE apresentar separadamente dois diagnósticos derivados, cada um com
  **todos** os seus problemas de uma vez:
  - **A — Estrutura válida**;
  - **B — Compatível com a jornada atual**.

  [002 FR-014; Const. — XIV]
- **FR-067**: O diagnóstico A e seus **problemas de estrutura** DEVEM ser obtidos
  exclusivamente da capacidade da 002 que verifica as condições de completude, a mesma
  que a publicação aplica:
  - Versão sem Seções;
  - Seção sem Perguntas;
  - Pergunta de escolha com menos de duas Opções;
  - desvio ou encaminhamento para a própria Seção ou para Seção anterior;
  - destino fora da Versão.

  O diagnóstico NÃO DEVE publicar nem gravar nada. [002 FR-059; Const. — XXII]
- **FR-068**: O diagnóstico B e suas **incompatibilidades com a jornada atual** DEVEM
  ser obtidos exclusivamente da verificação de suporte que a 006 já aplica: Seção com
  mais de uma Pergunta com desvio. O plan DEVE tornar essa verificação existente
  consultável sem duplicar sua lógica e sem alterar o comportamento da 006. [006
  FR-016; Arquitetura; Const. — XXII]
- **FR-069**: O editor NÃO DEVE acrescentar outros problemas além dos produzidos por
  essas duas capacidades. NÃO DEVE criar segundo validador, lista própria de regras,
  avisos de estilo ou heurísticas de qualidade. [Const. — XXII; XXIX]
- **FR-070**: Cada problema DEVE ser apresentado:
  - em linguagem operacional;
  - no diagnóstico de origem (A ou B);
  - com a localização do elemento por posição e título ou texto (por exemplo, "Seção 4 —
    Situação profissional", "Pergunta 2 da Seção 4: Qual sua ocupação?", "Opção 'Não'");
  - com acesso à página onde se corrige.

  A causa original DEVE permanecer rastreável no código, ligando a mensagem ao motivo
  da 002 ou da 006. Mesmo assim, a página NÃO DEVE exibir identificador interno, nome de
  classe, código de motivo ou código de requisito. [Const. — XIV; 008]
- **FR-071**: O editor DEVE apresentar exatamente uma das três situações derivadas:
  - "com problemas de estrutura";
  - "estrutura válida, mas incompatível com a jornada atual";
  - "sem impedimentos técnicos conhecidos".

  Na terceira, DEVE explicar que o resultado:
  - significa apenas que nenhuma verificação técnica existente aponta impedimento;
  - não é aprovação, homologação, autorização, publicação nem prontidão institucional;
  - não torna a publicação disponível no editor, porque ela depende da definição
    institucional de quem pode publicar.

  [Const. — X; 002/DP-001; 002/DP-002]
- **FR-072**: Diagnósticos e situação DEVEM ser **derivados** a cada consulta. NÃO
  DEVEM ser gravados como estado, marca, data, carimbo ou histórico. NÃO DEVE existir
  enumeração institucional de aprovação. [Const. — X; XXII]
- **FR-073**: Uma Versão na situação "sem impedimentos técnicos conhecidos" DEVE ser
  aceita pela operação de publicação da 002, sem nenhuma pendência de completude, e pela
  verificação de suporte da 006. As duas condições são verificáveis em teste. [002
  FR-059; 006 FR-016]
- **FR-074**: A página da Versão e as páginas de Seção e Pergunta DEVERIAM sinalizar os
  elementos com problema usando o mesmo resultado do diagnóstico, sem cálculo próprio.
  [Const. — XIV]
- **FR-075**: Para Versão publicada, nenhum diagnóstico técnico DEVE ser oferecido.
  [Escopo]

**Publicação**

- **FR-076**: O editor NÃO DEVE oferecer ação de publicar, nem como botão desabilitado.
  NÃO DEVE acionar a operação de publicação da 002 em nenhum fluxo. [Const. — X;
  002/DP-001; Escopo]
- **FR-077**: O editor NÃO DEVE criar pedido de publicação, envio para aprovação,
  fila, notificação, responsável, parecer ou qualquer etapa de fluxo de aprovação.
  [Const. — X; 002/DP-002]
- **FR-078**: O editor NÃO DEVE apresentar Versão "sem impedimentos técnicos
  conhecidos" como pronta para publicação, aprovada, homologada, autorizada ou
  vigente. [002 FR-008; Const. — X]
- **FR-079**: Versões publicadas que aparecem no editor foram publicadas por outros meios
  técnicos já existentes, como o preparo local da demonstração (008) ou os testes. O
  editor apenas as consulta. [008 FR-014; Escopo]
- **FR-080**: A spec da Feature 010 decidirá se e como a publicação será exposta. Esta
  feature NÃO DEVE criar estrutura antecipada para isso. [Const. — XXII; XXIX]

**Organização da edição**

- **FR-081**: A edição DEVE ser organizada em níveis navegáveis:
  1. Pesquisa;
  2. Versão (estrutura e dados da Versão);
  3. Seção (seus dados e a lista de suas Perguntas);
  4. Pergunta (seus dados, Opções, escala e desvios).

  Nenhuma página DEVE abrir para edição, ao mesmo tempo, campos de mais de uma Seção ou
  de mais de uma Pergunta. [Const. — XIV; XXII]
- **FR-082**: Toda página DEVE indicar onde o operador está (Pesquisa › Versão › Seção ›
  Pergunta) e permitir voltar aos níveis anteriores. O título principal DEVE ser o
  objeto atual. [Const. — XIV; auditoria UX-05/UX-07]
- **FR-083**: Quando uma página tiver mais de um formulário, cada ação DEVE deixar claro
  o que grava. O operador NÃO DEVE perder silenciosamente texto digitado ao acionar outra
  ação da mesma página. [Hipótese; auditoria UX-04]
- **FR-084**: A partir da página da Versão, qualquer Pergunta DEVE ser alcançável em no
  máximo duas ações de navegação. [Const. — XIV]

**Pré-visualização**

- **FR-085**: O editor DEVE oferecer pré-visualização de Versão em rascunho e de Versão
  publicada. [Escopo]
- **FR-086**: A pré-visualização DEVE apresentar:
  - título apresentado e texto de abertura;
  - Seções na ordem, com título e texto introdutório;
  - Perguntas na ordem, com texto, texto explicativo e indicação de obrigatoriedade;
  - controle correspondente ao tipo;
  - Opções na ordem, com indicação de complemento;
  - escalas com rótulos de extremidade;
  - texto de encerramento.

  [002 FR-064; Const. — XIV]
- **FR-087**: A pré-visualização DEVERIA reutilizar a apresentação por tipo da 008 quando
  isso não exigir Participação, Campanha, Pessoa ou Resposta. NÃO DEVE duplicar a
  jornada da 006 para oferecer simulação interativa. [008; Const. — XXII]
- **FR-088**: Desvios e encaminhamentos DEVEM aparecer como anotações textuais junto à
  Opção e à Seção. A pré-visualização NÃO DEVE executar a navegação nem simular ramos.
  Ela apresenta as Seções na ordem. [006/DP-604; Escopo]
- **FR-089**: A pré-visualização DEVE identificar-se como tal, de forma permanente e no
  título da página, com o aviso de que nada é gravado e de que os desvios não são
  executados. NÃO DEVE conter ação de enviar, salvar, avançar com gravação ou concluir.
  [Const. — XIV]
- **FR-090**: A pré-visualização NÃO DEVE criar, alterar ou consultar Participação,
  Campanha, Resposta, Pessoa ou Conclusão Acadêmica. NÃO DEVE gravar nada nem afetar
  indicador ou contagem. [Const. — VII; FR-025]
- **FR-091**: NÃO DEVE existir "Campanha de pré-visualização", Participação de teste,
  respondente fictício para pré-visualização nem armazenamento de respostas de
  pré-visualização. [Const. — VII; XXII]
- **FR-092**: A pré-visualização DEVE tratar Seção sem título e listas longas de Opções
  de forma legível. Ela PODE usar para listas longas a mesma forma compacta da 008.
  [008; auditoria UX-11]
- **FR-093**: A pré-visualização PODE apresentar todas as Seções numa página ou uma
  Seção por vez com navegação pela ordem. A escolha é do plan, respeitando FR-088 e
  FR-089. [Escopo]

**Linguagem e mensagens**

- **FR-094**: A interface DEVE usar os termos do domínio: Pesquisa, Versão, Seção,
  Pergunta, Opção, rascunho, publicada, desvio e encaminhamento. Os dois últimos DEVEM
  vir com explicação. A interface NÃO DEVE exibir:
  - identificadores internos;
  - nomes de classes ou de campos de armazenamento;
  - códigos de motivo ou de requisito;
  - rastros de erro;
  - detalhes de armazenamento.

  [Const. — XIV; 008]
- **FR-095**: Toda recusa possível nos fluxos do editor DEVE ter mensagem operacional
  própria, com o sentido indicado. Mudança concorrente e falha inesperada também.

  | Situação de recusa | Sentido da mensagem |
  |--------------------|---------------------|
  | Versão publicada | "Esta Versão está publicada e não pode ser alterada; crie uma nova Versão a partir dela" |
  | Designação repetida | "Já existe uma Versão com esta designação nesta Pesquisa" |
  | Texto obrigatório vazio | "Informe o texto" (associado ao campo) |
  | Opção repetida | "Já existe uma Opção com este texto nesta Pergunta" |
  | Segundo complemento | "Só uma Opção por Pergunta pode aceitar complemento escrito; desmarque a atual antes" |
  | Escala inválida | "O limite inicial precisa ser um número inteiro menor que o limite final" |
  | Seção com Perguntas | "Remova ou mova as Perguntas desta Seção antes de removê-la" |
  | Seção referenciada | "Esta Seção é destino de …; altere esses desvios ou encaminhamentos antes" |
  | Posição ocupada, ordem incompleta, elemento inexistente | "O conteúdo mudou desde que esta página foi aberta; confira o estado atual e tente de novo" |
  | Desvio já definido | Não ocorre na troca tudo-ou-nada (FR-052), que roda com a Versão bloqueada. Se ocorrer, é erro de programa: **não** é traduzido e propaga como falha inesperada |
  | Falha inesperada | Mensagem genérica, sem detalhe técnico |

  [Const. — XIV; 008]
- **FR-096**: Em formulário recusado, o editor DEVE:
  - apresentar o resumo dos erros no início do conteúdo principal, visível sem rolagem
    em tela pequena;
  - associar cada erro ao seu campo;
  - preservar os valores digitados.

  [Const. — XX; auditoria UX-01]
- **FR-097**: Depois de uma gravação aceita, o editor DEVE confirmar o resultado ao
  operador. Recarregar a página NÃO DEVE repetir a gravação. [008; Arquitetura]

**Tecnologia de interface**

- **FR-098**: O editor DEVE ser composto de páginas geradas no servidor. O fluxo completo
  DEVE funcionar sem JavaScript, inclusive criar, editar, ordenar, remover, configurar
  desvios, verificar e pré-visualizar. NÃO DEVE haver SPA, framework de frontend, API
  própria do editor (REST, GraphQL ou outra), etapa de build de frontend nem biblioteca
  de terceiros para ordenação ou edição. JavaScript PODE existir apenas como melhoria
  pequena e opcional. [Const. — XXII; XXIV; 008]

**Baseline e testes**

- **FR-099**: Testes e demonstrações desta feature DEVEM partir da consulta da baseline e
  de nova Versão criada a partir dela, ou de Versões próprias de teste. Eles NÃO DEVEM
  editar a baseline. Ao final de cada cenário, a baseline DEVE continuar equivalente à
  declarada pela 003. [003 FR-031 a FR-033; Escopo]
- **FR-100**: O editor DEVERIA recomendar, na página de qualquer Versão em rascunho, que
  experimentos sejam feitos numa nova Versão criada a partir dela. A recomendação é
  genérica, não específica da baseline. O editor NÃO DEVE contornar, reparar ou
  mascarar a recusa da materialização da 003 quando a baseline tiver sido alterada
  manualmente: essa recusa é comportamento esperado da 003. [Hipótese; DP-902; 003
  FR-031 a FR-033]

**Fronteiras do instrumento**

- **FR-101**: O editor NÃO DEVE remover, ocultar, marcar como "preenchida pelo sistema",
  pré-preencher ou vincular a Conclusão Acadêmica nenhuma Pergunta, inclusive Q10–Q19.
  Nenhuma alteração automática de conteúdo é feita. [003/DP-307; 007 FR-041; Const. —
  III; XIII]
- **FR-102**: O editor NÃO DEVE tratar Q1 nem qualquer Pergunta como registro de
  consentimento. Também NÃO DEVE criar marcação, tipo ou atributo de termo. Textos de
  termos são conteúdo comum de Seção e Pergunta. [002/DP-007; 005 FR-057; Const. — XVII]
- **FR-103**: O editor NÃO DEVE criar identidade global de Pergunta, chave estável,
  linhagem, catálogo, comparação semântica ou diferença metodológica entre Versões.
  [002/DP-006; 002 FR-032]
- **FR-104**: O editor NÃO DEVE criar, listar, consultar ou exibir Campanha, período de
  coleta, população elegível, respondentes, Participações, Respostas, taxas ou
  monitoramento. [Const. — VII; XIX; Escopo]
- **FR-105**: O editor NÃO DEVE conter dashboard, gráfico, indicador, análise de
  respostas, GeN ou exportação. [Const. — XIX; Escopo]
- **FR-106**: O editor NÃO DEVE conter scripting, plugins, fórmulas, campos calculados,
  variáveis, *piping*, pontuação, upload de arquivo, matriz ou grade, modelos genéricos,
  extensão por código do usuário, esquema alternativo de instrumento (por exemplo,
  importação ou exportação de definição) nem lógica sobre campos arbitrários. [Const. —
  XXII; XXIII]

**Persistência e independência**

- **FR-107**: Esta feature NÃO DEVE criar entidade de domínio, coluna ou estado novo. Isso
  exclui, entre outros:
  - sessão de edição;
  - rascunho de rascunho;
  - pré-visualização;
  - pedido de publicação;
  - aprovação;
  - modelo de pergunta;
  - componente;
  - preferência de interface;
  - marca de diagnóstico.

  Estado de interface DEVE ser derivado do endereço, do formulário e do conteúdo da
  Versão. [Const. — XXII; Escopo]
- **FR-108**: O editor NÃO DEVE ter salvamento automático, bloqueio de edição, edição
  colaborativa em tempo real, desfazer, histórico de alterações de rascunho nem
  versionamento próprio do editor. [002 Out of Scope; Const. — XXII; DP-903]
- **FR-109**: Esta feature NÃO DEVE alterar o comportamento nem os contratos das
  Features 001 a 008. A única adaptação admitida é tornar consultável a verificação de
  suporte já existente da 006 (FR-068), sem mudar seu resultado. [Escopo]

**Acessibilidade e responsividade**

- **FR-110**: Todas as páginas do editor DEVEM:
  - usar HTML semântico, com regiões principais e um título principal por página;
  - ter hierarquia de cabeçalhos coerente;
  - ter rótulo visível e associado em todo campo;
  - agrupar com legenda os conjuntos de opções;
  - ter foco visível e ordem de foco lógica;
  - ser operáveis só por teclado;
  - associar mensagens de erro aos campos;
  - ter título de página que identifique o objeto e indique erro quando houver.

  Referência: WCAG 2.1 AA e eMAG, como direção, sem certificação. [Const. — XX; 008]
- **FR-111**: Estado da Versão, tipo, obrigatoriedade, complemento, desvio e problemas
  NÃO DEVEM ser comunicados só por cor. [Const. — XX]
- **FR-112**: As páginas DEVEM funcionar em telas a partir de 320 px de largura e com zoom
  de 200%, sem rolagem horizontal da página, com contraste AA e alvos de toque
  confortáveis. [Const. — XXI; 008]

### Key Entities *(include if feature involves data)*

**Nenhuma entidade nova.** O editor opera sobre as entidades da 002, que representam
**configuração do instrumento**: não são dado pessoal nem dado institucional, derivado
ou declarado (Princípio III).

- **Pesquisa** (002): nome administrativo; 0..N Versões. O editor lista, cria e abre.
- **Versão da Pesquisa** (002): designação, estado, momento da publicação, origem e
  textos. O editor lista, cria, cria a partir de outra, consulta e, em rascunho, edita
  designação e textos.
- **Seção** (002): posição, título, texto introdutório e encaminhamento. O editor cria,
  edita, ordena, remove e define o encaminhamento, em rascunho.
- **Pergunta** (002): posição, tipo fixo, texto, texto explicativo, obrigatoriedade e
  escala. O editor cria, edita, ordena, move e remove, em rascunho.
- **Opção** (002): posição, texto, complemento e desvio. O editor cria, edita, ordena e
  remove, em rascunho.

**Valores derivados de leitura**, nunca gravados:

- **Resultado do diagnóstico técnico**: dois diagnósticos (A e B), a situação derivada e a lista de problemas, cada um com diagnóstico de origem,
  elemento localizado e explicação.
- **Estrutura apresentada**: resumo de leitura da Versão (US5).

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| Conteúdo da Versão (textos, Seções, Perguntas, Opções, escala, desvios) | Configuração do instrumento; nenhuma das três categorias | Leitura de conteúdo da 002 | Não aplicável |
| Problemas de estrutura (diagnóstico A) | Derivado (da configuração) | Condições de completude da 002 (002 FR-059) | Não aplicável |
| Incompatibilidades com a jornada atual (diagnóstico B) | Derivado (da configuração) | Verificação de suporte da 006 (006 FR-016) | Não aplicável |
| Estado da Versão e data de publicação | Configuração do instrumento | 002 | Não aplicável |

O editor não lê nem grava dado pessoal, dado institucional de Conclusão ou Resposta.

### Análise de persistência

- **Entidades novas**: zero.
- **Alterações de estrutura de armazenamento**: zero. Nenhuma migração é esperada.
- **Estado de interface**: derivado.
  - O elemento atual vem do endereço da página.
  - O diagnóstico é calculado a cada consulta.
  - A posição de inserção é calculada a partir do conteúdo ("ao final").
  - Mensagens de confirmação seguem o padrão já usado pela 008, sem armazenamento novo.
- Se o plan identificar necessidade de persistência nova só para estado de interface,
  ela DEVE ser rejeitada inicialmente em favor de solução derivada. Exceção exige
  justificativa em *Complexity Tracking*.

### Relação com as operações da Feature 002

Os nomes abaixo são referência aos contratos existentes (002 `contracts/operacoes.md` e
`contracts/conteudo.md`). Assinaturas e composição pertencem ao plan.

| Capacidade do editor | Capacidade existente reutilizada |
|----------------------|-----------------------------------|
| Criar Pesquisa | criação de Pesquisa (002) |
| Criar Versão vazia | criação de Versão (002) |
| Nova Versão a partir de outra | criação de Versão a partir de outra (002) |
| Editar designação e textos da Versão | alteração de Versão (002) |
| Adicionar, editar, remover Seção | adição, alteração, remoção de Seção (002) |
| Ordenar Seções | reordenação de Seções (002) |
| Encaminhamento | definição de encaminhamento (002) |
| Adicionar, editar, remover Pergunta | adição, alteração, remoção de Pergunta (002) |
| Ordenar Perguntas; mover para outra Seção | reordenação e movimentação de Pergunta (002) |
| Adicionar, editar, remover, ordenar Opção; complemento | adição, alteração, remoção, reordenação de Opção (002) |
| Desvio por Opção; troca de desvio | definição e remoção de regra (002), compostas tudo-ou-nada |
| Estrutura, páginas de leitura, pré-visualização | leitura do conteúdo da Versão (002) |
| Diagnóstico A — estrutura válida | verificação de completude (002), sem publicar |
| Diagnóstico B — compatível com a jornada atual | verificação de suporte da 006, tornada consultável sem duplicação |
| **Não usadas pelo editor** | publicação (002/DP-001); renomear Pesquisa (FR-011) |

Lacunas conhecidas, a resolver no plan sem nova regra de domínio:

- (a) A verificação de suporte da 006 hoje só é aplicada dentro do cálculo do percurso
  (FR-068).
- (b) A troca de desvio exige duas operações da 002 numa ação tudo-ou-nada (FR-052).
- (c) "Mover para cima/baixo" é expresso pela reordenação completa do conjunto (FR-061).
- (d) "Adicionar ao final" exige calcular a próxima posição livre (FR-027, FR-031,
  FR-041).

### Cobertura de verificação exigida

O plan e as tasks DEVEM prever verificação automatizada, no mínimo, para:

- listar Pesquisas;
- listar Versões com estados escritos;
- criar Pesquisa, inclusive o aviso de nome repetido;
- criar Versão;
- criar Versão a partir de outra, a partir de rascunho e de publicada;
- editar dados da Versão;
- recusa de toda escrita em Versão publicada, com conteúdo idêntico depois;
- Seções: criar, editar, remover (aceita e as duas recusas), reordenar e encaminhamento;
- Perguntas: criar dos quatro tipos, editar, remover com cascata, reordenar, mover entre
  Seções, ausência de troca de tipo;
- Opções: criar, editar, remover com desvio, reordenar, complemento único;
- escala: criação, alteração, recusas e explicação;
- navegação:
  - desvio para Seção, finalização, sem desvio e troca tudo-ou-nada;
  - ausência em tipos não compatíveis;
  - duas Perguntas com desvio na mesma Seção;
  - destino anterior;
- diagnóstico técnico:
  - todos os problemas de uma vez;
  - separação entre A (estrutura válida) e B (compatível com a jornada atual);
  - as três situações derivadas e a combinação dos dois diagnósticos;
  - correção de um problema seguida de novo diagnóstico;
  - localização sem identificadores;
  - nenhuma gravação;
  - "sem impedimentos técnicos conhecidos" ⇒ aceita pela publicação da 002 e pela
    verificação da 006;
  - ausência de qualquer texto de aprovação ou autorização;
- pré-visualização sem gravação, sem Participação, sem Campanha e sem Resposta;
- ausência de ação de publicar e de chamada à publicação;
- baseline equivalente à declarada ao final dos cenários;
- nenhuma Campanha criada;
- editor indisponível com o modo não produtivo desligado;
- semântica básica: rótulos, cabeçalhos, resumo de erros, nomes acessíveis das ações de
  ordenação, estados em texto;
- cenário principal e cenário de navegação completos sem JavaScript.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O cenário principal (14 passos) é executado integralmente pela interface,
  com 0 edições de código, banco ou console.
- **SC-002**: O cenário de navegação é executado integralmente pela interface. Os dois
  problemas provocados aparecem no diagnóstico correto: o (a) no B e o (b) no A. Depois
  de desfeitos, a Versão volta a "sem impedimentos técnicos conhecidos".
- **SC-003**: Para uma Versão publicada, 0 controles de edição são exibidos. 100% das
  requisições de escrita dirigidas a ela, pelo menos uma por tipo de ação do editor, são
  recusadas. O conteúdo consultado depois é idêntico ao anterior.
- **SC-004**: Para um rascunho preparado com pelo menos um caso de cada condição de
  completude da 002 e da limitação da 006, o diagnóstico lista 100% desses problemas numa
  única consulta, cada um no diagnóstico correto (A ou B). 0 problemas vêm de outra
  fonte. As três situações derivadas são alcançáveis e distinguíveis.
- **SC-005**: 100% das Versões na situação "sem impedimentos técnicos conhecidos" nos
  testes são aceitas pela operação de publicação da 002 sem pendência e pela verificação
  de suporte da 006. Nenhuma página exibe "pronta para publicação", "aprovada" ou
  equivalente.
- **SC-006**: Diagnóstico técnico, estrutura, páginas de leitura e pré-visualização
  produzem 0 criações ou alterações em qualquer entidade, inclusive Participação,
  Campanha, Resposta e Versão.
- **SC-007**: Em 100% das mensagens de recusa e de problema exibidas pelo editor nos
  testes, aparecem 0 identificadores internos, nomes de classe, códigos de motivo ou
  códigos de requisito. Cada mensagem localiza o elemento ou o campo.
- **SC-008**: Depois de todos os cenários e testes desta feature, a baseline continua
  equivalente à declarada pela 003. Uma nova materialização não faz nada e não recusa.
- **SC-009**: O cenário principal é concluído com JavaScript desabilitado.
- **SC-010**: O editor oferece exatamente 4 tipos de Pergunta, 2 estados de Versão, 3
  opções de destino por Opção (sem desvio, Seção, finalizar) e 0 ações de publicar.
  Nenhuma entidade de domínio nova é criada.
- **SC-011**: A partir da página de uma Versão do tamanho da baseline (13 Seções,
  54 Perguntas), qualquer Pergunta é alcançada em no máximo 2 ações de navegação.
- **SC-012**: Todas as páginas do editor passam pela verificação estrutural de
  acessibilidade:
  - título principal único;
  - rótulos associados;
  - resumo de erros no topo;
  - nomes acessíveis nas ações de ordenação e remoção;
  - estados em texto.

  Nenhuma página tem rolagem horizontal a 320 px.
- **SC-013**: Com o modo não produtivo desligado, 100% das páginas do editor respondem
  como inexistentes.

## Assumptions

Apenas suposições não institucionais. As regras institucionais em aberto estão em
"Decisões Pendentes".

- O operador conhece o conteúdo do instrumento e usa computador de mesa ou notebook na
  maior parte do tempo. O editor precisa funcionar razoavelmente em tela pequena, mas a
  experiência principal de celular continua sendo a do egresso (Princípio XXI).
- O volume é o da baseline (dezenas de Seções, centenas de Perguntas e Opções). Não há
  meta de desempenho além de páginas responsivas no ambiente local.
- O ambiente é local, não produtivo e com o modo de demonstração ligado. O editor não
  manipula dado pessoal: o instrumento é configuração.
- Usuários simultâneos são raros. A serialização por Versão da 002 basta, sem bloqueio
  de edição.
- O mecanismo de confirmação após gravação, a forma de mover para cima e para baixo, a
  divisão em passos da criação de Pergunta e a escolha entre pré-visualização numa ou em
  várias páginas pertencem ao plan.
- A identidade visual segue a da 008, neutra e acessível, enquanto 008/DP-801 estiver
  aberta.
- A verificação de suporte da 006 pode ser tornada consultável sem alterar seu
  resultado (FR-068, FR-109). Se o plan concluir que isso exige mudança de
  comportamento, a questão volta à spec.
- O preparo local da demonstração (008) continua sendo o meio de ter uma Versão publicada
  para consulta no ambiente local. Esta feature não cria outro.

## Relação com outras features

- **001**: não usada. O editor independe de Pessoa e Conclusão (FR-005).
- **002**: base desta feature. Todas as gravações usam suas operações (FR-021). Nenhuma
  regra dela é alterada ou duplicada (FR-022). A publicação existe, mas não é exposta
  (FR-076).
- **003**: a baseline é consultada e copiada, nunca editada nos testes (FR-099). Não há
  exceção pelo nome (FR-009). Q10–Q19 inalteradas (FR-101). A materialização continua
  idempotente e verificável (SC-008).
- **004**: não usada. Nenhuma Campanha é criada, listada ou exibida (FR-104). A
  exigência de Versão publicada para abrir Campanha continua sendo da 004.
- **005/007**: não usadas. Nenhuma Participação ou Resposta é criada (FR-090).
- **006**: sua semântica de navegação é explicada, não redefinida (FR-056). Sua
  verificação de suporte é reutilizada no diagnóstico (FR-068). Nada da jornada é
  duplicado para a pré-visualização (FR-087).
- **008**: mesma entrada não produtiva (FR-001), mesmos princípios de interface (FR-098,
  FR-110 a FR-112) e reaproveitamento da apresentação por tipo quando possível (FR-087).
  A jornada do egresso não muda (FR-109).
- **010** (futura): governança, papéis e escopos. Decidirá quem pode elaborar, editar e
  publicar, e se o editor e a publicação serão expostos em produção (DP-901; 002/DP-001,
  002/DP-002).

## Invariantes Constitucionais Afetados *(mandatory)*

- **VII — Pesquisa, Versão, Campanha e Participação distintas (NON-NEGOTIABLE)**: o
  editor trabalha com Pesquisa e Versão. Não cria nem exibe Campanha ou Participação
  (FR-104), e a pré-visualização não cria Participação (FR-090, FR-091).
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: Versão publicada sem nenhum
  controle de edição e com toda escrita recusada pela regra da 002 (FR-018 a FR-020). A
  evolução se dá só por nova Versão (FR-015). Não há correção no lugar (002/DP-003).
- **X — Tecnologia não redefine a governança (NON-NEGOTIABLE)**: sem ação de publicar
  (FR-076), sem fluxo de aprovação (FR-077), sem estados intermediários (FR-017), sem
  diagnóstico gravado (FR-072). O acesso não produtivo não confere competência
  institucional (FR-003, FR-004). Ter acesso ao editor não equivale a poder alterar
  instrumentos oficiais: isso é DP-901.
- **XIII — Instrumento atual é referência**: a baseline não é editada pelos testes nem
  tratada como exceção (FR-009, FR-099). Nenhuma Pergunta herdada é alterada
  automaticamente (FR-101). O editor não decide intenção metodológica (003/DP-302,
  003/DP-307).
- **XIV — Reduzir fricção**: edição em níveis (FR-081), estrutura legível (FR-065),
  linguagem operacional (FR-094 a FR-096), alcance de qualquer Pergunta em duas ações
  (FR-084). Aplica-se ao operador. A jornada do egresso não muda.
- **XX — Acessibilidade**: FR-110 a FR-112, FR-064. Estados em texto (FR-111).
- **XXI — Responsividade**: FR-112. O editor funciona em tela pequena, sem ser a
  experiência móvel principal.
- **XXII — Simplicidade e YAGNI**: zero entidades novas (FR-107), sem autosave ou
  histórico (FR-108), sem API ou SPA (FR-098), ordenação simples (FR-061, FR-062), sem
  renomear Pesquisa (FR-011), sem verificação própria (FR-069).
- **XXIII — Editor não é form builder universal**: exatamente os quatro tipos (FR-032),
  sem conversão de tipos (FR-035), sem editor de condições (FR-058), sem scripting,
  fórmulas, plugins, matriz, upload ou modelos (FR-106), sem banco de perguntas (FR-040).
- **XXVII — Evolução preserva significado**: nenhuma estrutura nova, nenhuma migração
  (Análise de persistência). Cópias preservam o conteúdo pelo contrato da 002 (FR-015),
  sem identidade global (FR-103).
- **XXIX — Hipóteses não viram requisitos (NON-NEGOTIABLE)**:
  - as escolhas reversíveis estão marcadas [Hipótese];
  - a semântica de navegação explicada é a atual, não permanente (FR-056; 006/DP-604);
  - a limitação da 006 aparece como problema, não como regra do modelo (FR-057);
  - as questões institucionais estão em Decisões Pendentes.
- **XVI — Privacidade**: não afetado materialmente. O editor não lê nem grava dado
  pessoal, fica desligado por padrão (FR-002) e não exibe dado de Pessoa (FR-005).
- **XVII — Consentimento**: Q1 não vira consentimento (FR-102).
- **III — Dado institucional não é resposta**: não afetado. Q10–Q19 inalteradas
  (FR-101).
- **I, II, XI — Longitudinalidade, egresso, identidade**: não afetados.

**Tensões identificadas (não são conflitos)**:

- **X × editor sem autorização**: qualquer pessoa com acesso ao ambiente local pode
  editar rascunhos, inclusive a baseline. Tratamento:
  - o editor existe só no modo não produtivo, desligado por padrão (FR-001, FR-002);
  - avisa permanentemente que não há autorização institucional (FR-003);
  - não publica (FR-076);
  - a competência de elaboração fica pendente (DP-901), e a proteção da baseline também
    (DP-902).
- **XXII × reutilizar a verificação da 006**: tornar consultável uma verificação hoje
  interna à jornada é a forma de não criar segundo validador. A alternativa, uma lista
  própria no editor, violaria FR-069.

Nenhum conflito com a Constituição ou com as Features 001 a 008 foi identificado.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence de fato ao domínio de acompanhamento?** Sim. Pesquisa e Versão estão na
   Fronteira do Domínio do NIAE. A Constituição prevê "manutenção de pesquisas sem
   alteração de código" (Princípio XXIII), com limites.
2. **É necessária ao ciclo de acompanhamento?** Sim. Novas Versões do instrumento
   (Princípio XIII: "revisões metodológicas PODEM ocorrer… de forma explícita, aprovada
   e versionada") exigem composição sem depender de desenvolvedor.
3. **Existe ou está prevista solução institucional mais adequada?** Não para Versões
   imutáveis e associadas ao modelo do NIAE. O Google Formulários não preserva Versões
   nem integra a cadeia longitudinal.
4. **Integração seria suficiente?** Não. Importar de ferramenta externa não preservaria
   o modelo da 002, e a ferramenta não é fonte canônica.
5. **A incorporação aumentaria desnecessariamente o acoplamento do núcleo?** Não. O
   editor é camada de interface sobre a 002, sem entidades novas (FR-107) e sem
   dependência de Pessoa, Campanha ou Participação (FR-005, FR-104).

## Out of Scope *(mandatory)*

- Publicar Versão por qualquer meio do editor. Também ficam fora pedido de publicação,
  aprovação, homologação e qualquer fluxo de elaboração (Feature 010; 002/DP-001,
  002/DP-002).
- Autenticação, usuários, papéis, permissões, perfis CPAEG e CSAEG, escopo por unidade,
  lista de acesso por Pesquisa e responsabilidade por publicação (Feature 010).
- Exposição do editor em ambiente produtivo.
- Despublicar, corrigir Versão publicada, alteração editorial pós-publicação e exceção
  de superusuário (002/DP-003).
- Excluir Pesquisa ou Versão; renomear Pesquisa.
- Tipos de Pergunta novos, subtipos, validação de formato, mínimo e máximo de seleções,
  exclusividade entre Opções, rótulos intermediários, pesos e pontuação (002/DP-005).
- Conversão de tipo de Pergunta.
- Editor de condições, condições compostas, condição de exibição, prioridade de regras,
  momento de aplicação configurável e salto imediato dentro da Seção (006/DP-604).
- Simulação executável dos ramos na pré-visualização; pré-visualização interativa
  completa.
- Campanha, período, população elegível, respondentes, Participação e Resposta.
- Dashboard, indicadores, gráficos, taxa de resposta, análise e exportação.
- Banco de perguntas, catálogo de Opções, modelos de Pergunta ou de Versão, identidade
  global de Pergunta, linhagem e comparação entre Versões (002/DP-006).
- Qualquer tratamento especial de Q1 (consentimento) ou de Q10–Q19 (003/DP-307;
  002/DP-007).
- Importação ou exportação da definição do instrumento (Google Formulários, JSON ou
  outro esquema).
- Arrastar e soltar obrigatório; SPA; API própria do editor; frontend com build;
  bibliotecas de terceiros de edição.
- Salvamento automático, bloqueio de edição, colaboração em tempo real, desfazer e
  histórico de edições (DP-903).
- Revisão metodológica ou editorial do instrumento (002/DP-004).
- Ajustes de UX da jornada do egresso apontados pela auditoria da 008. Eles pertencem a
  um ciclo próprio e não são incorporados a esta feature.
- Certificação formal de acessibilidade.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: decisões novas usam o prefixo 9 (DP-901…). As das features anteriores são
citadas como 00n/DP-nnn.

**Novas nesta feature**

- **DP-901** — DECISÃO PENDENTE: quem tem competência institucional para **elaborar e
  editar** Versões em rascunho do instrumento, e em que escopo. Essa competência é
  distinta da de publicar (002/DP-001).
  - A PAEG atribui à CPAEG elaborar o questionário com as áreas de ensino, pesquisa e
    extensão (Art. 21, VI) e às CSAEGs reportar atualizações necessárias (Art. 22, IV).
    *(Citação corrigida em 2026-10-05: o original dizia "Art. 22, III"; o reporte à CPAEG
    está no Art. 22, IV, como já registrado pela 010.)*
  - Instância competente: Proex/CPAEG; tratamento técnico na Feature 010.
  - Impacto: quem poderá usar o editor fora do ambiente não produtivo; se haverá escopo
    por Pesquisa ou unidade.
  - Tratamento provisório: editor disponível somente no modo não produtivo, sem
    autenticação, com aviso permanente de que o acesso não confere competência (FR-001
    a FR-006).
- **DP-902** — DECISÃO PENDENTE: estatuto da baseline migrada da 003 ("referência
  migrada", em RASCUNHO). A questão é se ela deve ficar protegida contra edição como
  referência metodológica, ser publicada como registro histórico ou continuar como
  rascunho comum.
  - Instância competente: CPAEG (natureza da referência). A publicação também depende de
    002/DP-001.
  - Impacto: editar a baseline no lugar faz a materialização da 003 recusar por
    divergência, e com ela o preparo da demonstração da 008. Isso é detectável, não
    silencioso.
  - Tratamento provisório: rascunho comum, sem exceção pelo nome (FR-009). Os testes
    nunca a editam (FR-099). O editor recomenda, de forma genérica, trabalhar em nova
    Versão criada a partir do rascunho (FR-100).
- **DP-903** — DECISÃO PENDENTE: se a elaboração de Versões exigirá rastreabilidade de
  autoria e histórico de alterações dos rascunhos (quem alterou o quê e quando), para
  fins de governança ou auditoria.
  - Instância competente: CPAEG/Proex; tratamento técnico com a Feature 010.
  - Impacto: possível persistência nova no futuro (Princípios IV e XVI: rastreabilidade
    proporcional ao risco).
  - Tratamento provisório: nenhum histórico nem autoria. A última operação aceita
    prevalece (FR-108).

**Herdadas e afetadas por esta feature**

- **002/DP-001** — quem pode publicar: continua aberta. O editor não publica (FR-076),
  apenas mostra o diagnóstico técnico derivado (FR-071, FR-072).
- **002/DP-002** — fluxo de elaboração e aprovação: continua aberta. Nenhum estado ou
  etapa intermediária (FR-017, FR-077).
- **002/DP-003** — correções editoriais pós-publicação: continua aberta. Imutabilidade
  total na interface (FR-018 a FR-020). O caminho é nova Versão.
- **002/DP-004** — melhorias metodológicas: continua aberta. O editor viabiliza compor
  Versões, mas não decide nem aplica melhoria alguma.
- **002/DP-005** — tipos e capacidades futuras: continua aberta. Exatamente os quatro
  tipos e as capacidades da 002 (FR-032, FR-045, FR-050, FR-058).
- **002/DP-006** — comparabilidade entre Versões: continua aberta. Só a origem da Versão
  é informada (FR-016, FR-103).
- **002/DP-007** — consentimento e documento: continua aberta. Q1 é conteúdo comum
  (FR-102).
- **003/DP-307** — Q10–Q19 como contexto institucional: continua aberta. Nenhuma
  alteração automática (FR-101).
- **006/DP-604** — semântica futura de navegação: continua aberta. O editor explica a
  semântica atual sem fixá-la como permanente (FR-056) e aponta como problema o que a
  jornada atual não executa (FR-057).

**Herdadas e ainda abertas** (não resolvidas por esta feature)

- **003/DP-301** (rótulo inicial das escalas), **003/DP-302** (Q47/Q48 e momento do
  desvio), **003/DP-303** a **003/DP-310**: questões do conteúdo da baseline. O editor
  permite compor Versões que as tratem, mas não as decide.
- **008/DP-801** — identidade visual e linguagem institucionais: o editor segue o padrão
  neutro da 008.
- **004/DP-402** — quem pode criar, abrir e encerrar Campanha: não afetada, porque o
  editor não trata Campanha.
