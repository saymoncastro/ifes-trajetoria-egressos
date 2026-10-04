# Feature Specification: Governança, papéis e escopos institucionais

**Feature Branch**: `claude/feature-010-governanca-d28809`

**Created**: 2026-10-01

**Status**: Approved (clarificado em 2026-10-01)

**Input**: User description: "Feature 010 — Governança, papéis e escopos institucionais.
Introduzir o mínimo necessário de governança e autorização institucional para as
capacidades já existentes, a começar pelo editor da Feature 009. Responder 'dado um
operador institucional já identificado, o que ele pode fazer e em qual escopo?', sem
responder ainda 'como esse operador prova sua identidade?'. Usar a PAEG como limite,
distinguindo competência prevista, interpretação operacional e decisão institucional
ainda não definida. Atuação central associada à CPAEG; atuação de unidade associada à
CSAEG. Escopo institucional × unidade, sem árvore de organizações nem multi-tenancy. No
máximo uma estrutura persistida de vínculo operador → papel → escopo. Proteger no
servidor todas as rotas do editor. Publicação somente se houver fundamento normativo
claro; caso contrário, indisponível e pendente. Sem workflow de aprovação, sem RBAC
genérico, sem login, sem gestão de Campanha, sem auditoria completa, sem nova capacidade
editorial."

## Contexto

As nove primeiras features estabeleceram:

- **001** — **Pessoa → Conclusão Acadêmica**, com fonte acadêmica simulada. A unidade
  de uma Conclusão é uma designação textual vinda da fonte acadêmica; não existe entidade
  própria de unidade.
- **002** — **Pesquisa → Versão (RASCUNHO | PUBLICADA) → Seções → Perguntas → Opções**,
  com operações internas, inclusive `publicar`. A 002 não expõe nenhuma operação a
  perfil ou interface e registra que quem pode publicar é **002/DP-001**.
- **003** — a baseline "Formulário Egresso Ifes 2024 — referência migrada", em
  RASCUNHO.
- **004** — Campanha. Abrir Campanha exige Versão PUBLICADA. Quem cria, abre e encerra
  Campanha é **004/DP-402**.
- **005/006/007** — Participação, Respostas, jornada, conclusão e entrada do egresso.
- **008** — interface navegável do egresso, disponível somente no **modo de
  demonstração** local e não produtivo, desligado por padrão. Desligado, toda página
  responde como inexistente.
- **009** — **editor institucional de Pesquisa e Versão**: listar Pesquisas e Versões,
  criar Pesquisa e Versão, criar Versão a partir de outra, editar rascunhos (Seções,
  Perguntas, Opções, escala, desvios, encaminhamentos), diagnóstico técnico,
  pré-visualização e consulta de Versão publicada.
  - O editor existe só no modo de demonstração e **não identifica quem o usa**.
  - Toda página avisa que o acesso **não** confere competência institucional
    (009 FR-003).
  - O editor **não publica** (009 FR-076) e delegou a esta feature decidir se e como a
    publicação seria exposta (009 FR-080).
  - Ficou pendente quem pode elaborar e editar rascunhos (**009/DP-901**).

Hoje, portanto, **qualquer pessoa que alcance o ambiente de demonstração pode alterar o
instrumento**, inclusive a baseline. O único controle é o modo de demonstração, que é
uma chave de ambiente, não uma regra de governança.

A aplicação também **não tem hoje nenhum conceito de usuário, conta, sessão autenticada,
superusuário ou administração técnica por interface**. O único ator modelado é a Pessoa
egressa, e somente na demonstração.

Esta feature introduz o **mínimo necessário de governança institucional** para que as
capacidades já existentes, em especial as do editor, passem a ser decididas por uma
regra de autorização explícita, fundada na PAEG, e não pelo modo de demonstração.

### Princípio central desta spec

**Autorização não é autenticação.**

Esta feature responde:

> "Dado um operador institucional **já identificado**, o que ele pode fazer e em qual
> escopo?"

Ela **não** responde:

> "Como esse operador prova sua identidade?"

- A regra de autorização recebe, conceitualmente, um operador já identificado, ou a
  ausência de operador.
- O mecanismo que identifica o operador é uma fronteira substituível (Princípio XV).
  Nesta feature existe **somente** um mecanismo não produtivo, de demonstração e teste.
- Nenhum mecanismo de autenticação (senha, OTP, Gov.br, SSO, LDAP, login institucional)
  é criado.
- Governança controla **quem pode executar** as operações que já existem. Ela não cria
  operação, estado, etapa ou fluxo novo.

### Análise normativa

Fonte: **PAEG — Resolução CS nº 177/2023, anexo**
(`docs/referencias/paeg-resolucao-cs-177-2023-anexo.pdf`), lida integralmente.

A análise separa três categorias. Somente a categoria A é tratada como competência
institucional. A categoria B é interpretação técnica reversível. A categoria C não é
decidida por esta feature.

#### A. Competências claramente previstas pela PAEG

| # | Competência | Artigo |
|---|-------------|--------|
| A1 | A PAEG é atribuição, em conjunto, das **Unidades** e da **Proex**, em especial pela DIREC | Art. 2º |
| A2 | **Unidades** são os campi, o campus avançado e o Cefor | Art. 2º, parágrafo único |
| A3 | Questionário eletrônico com **periodicidade definida pela Proex e Proen** e/ou órgão competente | Art. 10, II |
| A4 | **Proex**: coordenação geral, monitoramento da implementação, execução e avaliação da política; Relatório Anual compilado a partir das CSAEGs | Art. 14 |
| A5 | **CPAEG** ("Comissão **Própria** de Acompanhamento do Egresso"), presidida pelo Pró-Reitor de Extensão ou representante da Proex | Art. 16 |
| A6 | Membros da CPAEG **nomeados por portaria do Reitor**; composição mínima recomendada, com mais de um membro | Art. 17; Art. 24 |
| A7 | **CPAEG**: planejar, organizar, executar e avaliar as atividades da PAEG **no âmbito do Ifes** | Art. 21, I |
| A8 | **CPAEG**: desenvolver as atividades em consonância com as CSAEGs | Art. 21, III |
| A9 | **CPAEG**: atualizar o **banco de dados central** | Art. 21, V |
| A10 | **CPAEG**: **elaborar o questionário de pesquisa, em conjunto com as áreas de ensino, pesquisa e extensão** | Art. 21, VI |
| A11 | Na unidade, a PAEG é gerenciada pela Diretoria de Pesquisa, Pós-Graduação e Extensão (ou equivalente), que **indica a CSAEG** | Art. 18, I e III |
| A12 | **CSAEG** nomeada pelo Diretor-Geral da unidade, por portaria; composição mínima recomendada, com mais de um membro | Art. 19; Art. 24 |
| A13 | **CSAEG**: planejar, organizar, executar e avaliar as atividades da política **nas unidades** | Art. 22, I |
| A14 | **CSAEG**: gestão do Portal do Egresso na respectiva unidade e atualização do seu banco de dados | Art. 13, parágrafo único; Art. 22, III |
| A15 | **CSAEG**: **aplicar o questionário** de avaliação do egresso e **reportar atualizações necessárias à CPAEG** | Art. 22, IV |
| A16 | Casos omissos resolvidos pela **CPAEG em conjunto com a Pró-reitoria** competente | Art. 26 |

**O que a PAEG não diz** (relevante para esta feature):

- **Não** define quem aprova, autoriza, homologa ou publica uma Versão do questionário,
  nem quando o questionário elaborado passa a valer.
- **Não** define fluxo de elaboração, revisão ou aprovação.
- **Não** atribui a nenhuma instância a operação de sistemas, nem distingue membro de
  comissão de pessoa que opera em seu nome.
- **Não** define acesso de uma CSAEG a dados de outra unidade, nem acesso a dados
  identificados de egressos.
- **Não** exige registro de autoria ou histórico de alterações do questionário.

#### B. Interpretação operacional adotada por esta feature

Cada interpretação abaixo é **técnica, reversível e localizada** (Princípio XXIX). Ela
não cria competência institucional; apenas traduz uma competência da categoria A em
ação concreta do software.

| # | Interpretação | Fundamento | Por que é interpretação |
|---|---------------|------------|-------------------------|
| B1 | Elaborar e editar Versões **em rascunho** no editor (criar Pesquisa, criar Versão, criar Versão a partir de outra, editar Seções, Perguntas, Opções, escala, desvios e encaminhamentos) é a forma, no software, de "elaborar o questionário" | A10 | A PAEG fala em elaborar o questionário, não em operar um editor; rascunho é conceito do software (002) |
| B2 | Consultar rascunhos, obter o diagnóstico técnico e pré-visualizar rascunhos acompanham a elaboração | A10 | Mesmo motivo de B1 |
| B3 | A atuação da CPAEG tem **escopo institucional**, sem unidade | A7 ("no âmbito do Ifes"), A9 | "Escopo" é conceito do software |
| B4 | A atuação da CSAEG tem **escopo de uma unidade explícita** | A11, A12, A13 | Idem |
| B5 | A CSAEG **não altera** o instrumento: o caminho previsto é **reportar** atualizações à CPAEG | A15, contraposto a A10 | A PAEG não proíbe expressamente; ela atribui a elaboração a outra instância e prevê o reporte |
| B6 | A CSAEG pode **consultar e pré-visualizar Versões publicadas**, porque aplica o questionário e reporta atualizações necessárias | A15 | A PAEG não fala em acesso a sistema; a consulta do instrumento vigente é o mínimo para aplicar e reportar. **Confirmada** em Clarifications 2026-10-01 como interpretação operacional, não competência autônoma |
| B7 | A CSAEG **não** consulta rascunhos nem diagnóstico | Menor privilégio (Const. XII, XVI); nenhuma competência de elaboração | Ampliação depende de decisão (DP-1004) |
| B8 | A participação conjunta das áreas de ensino, pesquisa e extensão na elaboração ocorre **institucionalmente, fora do software** | A10 | Não há requisito institucional de coautoria no sistema (DP-1003) |
| B9 | O registro de um vínculo **reflete** uma designação institucional feita fora do sistema (portaria); o sistema não verifica nem substitui essa designação | A6, A12, Art. 24 | O meio e a evidência do registro não estão definidos (DP-1002) |

#### C. Decisões institucionais ainda não definidas

Registradas em "Decisões Pendentes":

- quem publica uma Versão (**002/DP-001**, mantida) — a PAEG indica apenas **quem resolve
  a omissão** (Art. 26), não a resposta;
- fluxo de elaboração e aprovação (**002/DP-002**, mantida);
- quem, além dos membros nomeados, pode atuar pela CPAEG no sistema (**DP-1003**);
- se a CSAEG terá acesso a rascunhos ou forma de propor alterações (**DP-1004**);
- como operadores institucionais serão identificados em produção (**DP-1001**);
- quem autoriza o registro de vínculos e com qual evidência (**DP-1002**);
- designação canônica das unidades (**DP-1005**);
- atuação de Proex, DIREC, Proen e Diretorias de unidade no sistema (**DP-1006**);
- autoria e histórico de alterações (**009/DP-903**, mantida).

#### Observações sobre o texto normativo

- O nome da comissão central na PAEG é **"Comissão Própria de Acompanhamento do
  Egresso (CPAEG)"** (Art. 16; Art. 24: "comissões própria (CPAEG) e setorial
  (CSAEG)"). A interface DEVE usar o nome da norma, e não "Comissão Permanente". A
  CSAEG aparece como "Comissão Setorial de Acompanhamento de Egressos" (Art. 18, III) e
  "do Egresso" (Art. 13); a interface usa a forma do Art. 18, III.
- A 009/DP-901 cita "Art. 22, III" para o reporte de atualizações à CPAEG. O reporte
  está no **Art. 22, IV**. Esta spec usa a citação correta.
- O Art. 21, VI fala em "questionário de pesquisa" e o Art. 22, IV em "questionário de
  avaliação do egresso". Esta spec trata ambos como o mesmo instrumento, representado
  por Pesquisa e Versão (002). Essa leitura é a mesma das features anteriores.

### Termos usados nesta spec

Os nomes são conceituais; a nomenclatura concreta pertence ao plan.

- **Operador institucional** (ou **operador**): pessoa que usa as superfícies
  institucionais do sistema, identificada por um **identificador de operador**.
  - Não é Pessoa egressa, Conclusão Acadêmica nem Participação (Princípio III; FR-008).
  - Não tem senha, credencial nem cadastro criado por esta feature.
  - O identificador é **opaco** para a regra de autorização: nada é inferido do seu
    formato (por exemplo, unidade a partir de e-mail).
- **Identificação do operador**: o ato, externo à regra, de determinar qual operador
  faz a requisição. Nesta feature existe somente a **identificação não produtiva** (modo
  de demonstração e testes). A identificação produtiva é DP-1001.
- **Atuação institucional**: uma de exatamente duas opções:
  - **CPAEG** — atuação central associada à Comissão Própria de Acompanhamento do
    Egresso;
  - **CSAEG** — atuação de unidade associada à Comissão Setorial de Acompanhamento de
    Egressos.
- **Escopo**: decorre da atuação e não é escolhido à parte.
  - **Institucional** para CPAEG, sem unidade.
  - **Unidade** para CSAEG, com exatamente uma unidade explícita.
- **Unidade**: campus, campus avançado ou Cefor (PAEG Art. 2º, parágrafo único),
  designada da mesma forma que a fonte acadêmica designa a unidade de uma Conclusão
  (001). Não é entidade, tenant nem nó de árvore.
- **Vínculo de governança** (ou **vínculo**): registro de que um operador tem
  determinada atuação, no escopo correspondente, e se o vínculo está **ativo** ou
  **inativo**. É a única estrutura persistida nova desta feature.
- **Capacidade**: ação concreta que já existe no sistema e que a regra de autorização
  permite ou recusa. Não é "permissão" configurável.
- **Recusa de acesso**: resposta explícita a uma ação não permitida. Distinta de
  "página inexistente" e de "rejeição" de operação da 002.
- **Operador fictício**: operador de demonstração e teste, com identificador e vínculos
  fictícios, que nunca corresponde a pessoa real.

### Decisões desta especificação

Escolhas reversíveis, marcadas **[Hipótese]** ou **[Interpretação B#]** nos requisitos,
e decisões de escopo:

1. **Exatamente duas atuações: CPAEG e CSAEG** (FR-010 a FR-013).
   - Usam a terminologia da PAEG.
   - Proex, DIREC, Proen e Diretorias de unidade não viram papéis, porque nenhuma
     superfície existente as consome (DP-1006).
   - Nenhum papel técnico genérico (administrador, editor, leitor, gestor, publicador).
2. **O escopo decorre da atuação** (FR-014 a FR-017).
   - CPAEG ⇒ institucional, sem unidade.
   - CSAEG ⇒ unidade obrigatória.
   - Não há escolha livre de escopo, hierarquia nem herança.
3. **Uma única estrutura persistida: o vínculo de governança** (FR-018 a FR-027).
   - Operador, atuação, unidade quando houver, situação ativo/inativo.
   - Nenhuma tabela de papéis, permissões, escopos, organizações ou operadores, salvo
     justificativa concreta do plan (FR-025).
4. **Três capacidades concretas** sobre as ações já existentes do editor (FR-028 a
   FR-036):
   - **consultar o instrumento publicado** (Versões publicadas e sua pré-visualização);
   - **consultar rascunhos** (estrutura, diagnóstico técnico e pré-visualização de
     rascunho);
   - **elaborar** (toda escrita do editor).

   "Acessar o editor" é ter ao menos uma delas.
5. **CPAEG tem as três capacidades; CSAEG tem somente a primeira** [Interpretação B1,
   B2, B5, B6, B7].
6. **Publicação continua indisponível** (FR-047 a FR-052). A PAEG não define quem
   publica. Nenhuma capacidade, papel ou estrutura de publicação é criada.
7. **Identificação somente não produtiva nesta feature** (FR-053 a FR-061).
   - No modo de demonstração, quem usa escolhe um operador fictício, como a 008 faz com
     a Pessoa fictícia.
   - A escolha identifica; **não autoriza**. A autorização é sempre a regra desta
     feature, com os vínculos registrados.
   - Fora do modo de demonstração o editor continua indisponível, agora porque não há
     identificação produtiva (DP-1001), não por falta de regra de autorização.
8. **Registro de vínculos por mecanismo técnico administrativo controlado, sem tela**
   (FR-062 a FR-066).
9. **Recusa explícita, não "página inexistente"** (FR-037 a FR-046).
10. **Sem auditoria nova**: 009/DP-903 continua aberta (FR-074).

## Clarifications

### Session 2026-10-01

Decisões consolidadas pelo solicitante após a aprovação da spec e antes do plan:

- Q: A CSAEG pode consultar Versões publicadas? → A: **Sim.**
  - É **interpretação operacional** da PAEG (B6), não competência normativa autônoma: a
    CSAEG aplica o questionário na unidade (Art. 22, IV), e consultar o instrumento
    efetivamente publicado é necessário para compreender o que está sendo aplicado.
  - Isso não implica competência para elaborar, editar ou publicar.
  - Matriz confirmada: CPAEG consulta publicadas, consulta rascunhos e elabora; CSAEG
    consulta publicadas e **não** consulta rascunhos nem elabora.
  - Nenhum acesso parcial a rascunhos para a CSAEG nesta feature. DP-1004 continua
    aberta.

  (B6; FR-030, FR-031; Matriz mínima de capacidades; DP-1004)
- Q: Vínculo encerrado é apagado ou desativado? → A: **Desativado.**
  - O vínculo tem condição ativo/inativo. Quando uma designação deixa de produzir
    autorização no sistema, o vínculo é marcado inativo; inativo não concede nenhuma
    capacidade; apagar não é fluxo normal.
  - `ativo` existe **somente** para responder "este vínculo concede autorização agora?".
  - NÃO são criados: histórico de alterações, período de vigência, início/fim de
    mandato, número de portaria, documento de designação, autor da alteração, registro
    de auditoria nem versionamento do vínculo.

  (FR-018, FR-023, FR-026; US9)
- Q: O editor fica disponível em produção depois desta feature? → A: **Não.**
  - Esta feature implementa **autorização**, não autenticação nem identificação
    confiável do operador.
  - Depois dela, as regras de governança estão prontas, testáveis com operadores
    fictícios e utilizáveis no modo de demonstração; o editor **não** é considerado
    disponível para uso produtivo enquanto DP-1001 estiver aberta.
  - Nenhum destes mecanismos constitui identificação produtiva confiável, e nenhum
    DEVE ser usado para isso: parâmetro de endereço, cabeçalho arbitrário, cookie não
    autenticado, superusuário, marca de equipe técnica ou modo de demonstração.

  (FR-054; DP-1001)
- Q: A publicação é resolvida? → A: **Não.** A PAEG sustenta a elaboração pela CPAEG,
  mas não estabelece de forma inequívoca quem executa ou autoriza a publicação. A
  operação `publicar` da 002 continua existindo tecnicamente; a 009 e a 010 não a
  expõem; não há papel publicador; não se presume que a CPAEG publica porque elabora;
  não há fluxo de aprovação; 002/DP-001 continua aberta. O Art. 26 indica quem deve
  resolver a omissão institucionalmente, mas **não autoriza o software a resolvê-la**.

  (FR-047 a FR-052)

### Session 2026-10-02

Ajustes consolidados pelo solicitante após a aprovação do plan e antes das tasks:

- Q: Como representar a unidade de um vínculo CPAEG? → A: `unidade` é texto **não nulo**.
  CPAEG ⇒ unidade **vazia**; CSAEG ⇒ unidade **não vazia**. Assim a unicidade de
  (operador, papel, unidade) vale diretamente também para CPAEG, sem depender da
  semântica de nulo. Sem normalização e sem entidade de unidade.

  (FR-014, FR-018, FR-019; Key Entities)
- Q: Como expressar as capacidades? → A: como as **três regras fixas** derivadas dos
  vínculos ativos (consultar publicado, consultar rascunho, elaborar), por predicados
  explícitos. Sem modelo, registro, composição ou motor de permissões ou políticas, nem
  ACL.

  (FR-028, FR-034, FR-035)
- Q: No modo de demonstração, sem operador escolhido, o editor recusa? → A: **Não.**
  Quem usa é **levado à escolha de operador fictício** e, depois da escolha, volta ao
  início do editor. Sem autenticação, login, sessão de identidade, conta de demonstração
  nem mecanismo genérico de retorno ao endereço original. Depois de identificado:
  autorizado segue; identificado sem capacidade recebe recusa. Com o modo desligado, o
  editor continua sem responder e nenhum identificador vindo do cliente é aceito.

  (US2, US4; FR-037, FR-054, FR-055)
- Q: A recusa cita artigos da PAEG? → A: **Não no texto principal.** A recusa usa
  linguagem operacional (por exemplo, "Seu vínculo permite consultar o instrumento
  publicado, mas não editar rascunhos."). A fundamentação normativa fica na spec, nos
  testes, na documentação e nas regras. Referência normativa na interface, se houver, é
  complementar e não necessária para compreender a recusa.

  (US12; FR-043, FR-044; SC-010)

## User Scenarios & Testing *(mandatory)*

Atores:

- **Operador com atuação CPAEG**: elabora o instrumento (escopo institucional).
- **Operador com atuação CSAEG**: atua numa unidade; consulta o instrumento vigente.
- **Operador sem vínculo ativo**: identificado, mas sem atuação institucional válida.
- **Pessoa não identificada**: requisição sem operador identificado.
- **Responsável técnico**: quem opera o ambiente e registra vínculos pelo mecanismo
  administrativo. Não é papel institucional.

Todos os operadores dos cenários são **fictícios**.

### User Story 1 - Registrar o vínculo de governança de um operador (Priority: P1)

O responsável técnico registra, por mecanismo administrativo controlado, que um operador
atua pela CPAEG, ou pela CSAEG de uma unidade, refletindo uma designação institucional
feita fora do sistema. Também consulta os vínculos existentes e desativa um vínculo.

**Why this priority**: sem vínculo representado não há como decidir nada. É o núcleo da
feature: operador → atuação → escopo (Princípio X; Governança de Permissões).

**Independent Test**: registrar, consultar e desativar vínculos pelo mecanismo
administrativo e verificar as recusas de registro inválido, sem nenhuma interface.

**Acceptance Scenarios**:

1. **Given** um operador fictício sem vínculo, **When** o responsável técnico registra
   atuação CPAEG sem unidade, **Then** o vínculo fica ativo com escopo institucional.
2. **Given** um operador fictício, **When** registra atuação CSAEG com a unidade A
   (uma unidade dos dados simulados), **Then** o vínculo fica ativo com escopo dessa unidade.
3. **Given** um registro de CPAEG **com** unidade, **When** é submetido, **Then** é
   recusado com explicação, e nada é gravado.
4. **Given** um registro de CSAEG **sem** unidade, **When** é submetido, **Then** é
   recusado, e nada é gravado.
5. **Given** um operador com vínculo ativo CSAEG na unidade A, **When** se tenta
   registrar outro vínculo ativo CSAEG na mesma unidade A, **Then** é recusado como
   duplicado.
6. **Given** dois operadores diferentes, **When** ambos recebem atuação CPAEG, **Then**
   ambos os vínculos ficam ativos: não há titular único.
7. **Given** um vínculo ativo, **When** o responsável técnico o desativa, **Then** ele
   passa a inativo, continua consultável como inativo e deixa de conferir qualquer
   capacidade.
8. **Given** qualquer registro, **When** é consultado, **Then** mostra operador,
   atuação, unidade (quando CSAEG) e situação, e nada mais.

---

### User Story 2 - Atuar como operador fictício no modo de demonstração (Priority: P1)

No ambiente local de demonstração, quem usa o editor escolhe um operador fictício
preparado para a demonstração. O sistema passa a tratar as requisições como desse
operador, e a regra de autorização decide o que ele pode fazer.

**Why this priority**: sem identificação, o editor da 009 ficaria inutilizável na
demonstração depois desta feature. A escolha substitui o acesso sem identificação da 009
por um operador concreto, sem criar login (Princípio XV).

**Independent Test**: com o modo de demonstração ligado, escolher cada operador fictício
e verificar o que o editor oferece; com o modo desligado, verificar que a escolha não
existe.

**Acceptance Scenarios**:

1. **Given** modo de demonstração ligado e nenhum operador escolhido, **When** se abre
   qualquer página do editor, **Then** quem usa é levado à escolha de operador fictício,
   sem ver conteúdo do instrumento; depois da escolha, volta ao início do editor.
2. **Given** modo ligado, **When** se escolhe o operador fictício com vínculo CPAEG,
   **Then** o editor mostra o contexto de atuação ("Comissão Própria de Acompanhamento
   do Egresso (CPAEG) — atuação institucional") e oferece as ações de elaboração.
3. **Given** modo ligado, **When** se escolhe o operador fictício com vínculo CSAEG da
   unidade A, **Then** o editor mostra a atuação de unidade e oferece somente consulta
   de Versões publicadas.
4. **Given** modo ligado, **When** se escolhe o operador fictício sem vínculo ativo,
   **Then** toda página do editor responde com recusa de acesso.
5. **Given** modo ligado, **When** se tenta escolher um identificador que não pertence
   aos operadores fictícios preparados, **Then** a escolha é recusada.
6. **Given** modo desligado, **When** se tenta acessar a escolha de operador ou o
   editor, **Then** nada responde, como na 008 e na 009.
7. **Given** modo ligado, **When** se troca de operador fictício, **Then** a requisição
   seguinte usa o novo operador, sem nenhuma capacidade residual do anterior.

---

### User Story 3 - Operador CPAEG acessa o editor e elabora rascunho (Priority: P1)

O operador com atuação CPAEG abre o editor, vê todas as Pesquisas e Versões (rascunhos
e publicadas), cria Pesquisa e Versão, cria Versão a partir de outra e edita rascunhos
com todas as ações da 009, além de consultar diagnóstico e pré-visualização.

**Why this priority**: é o consumidor imediato: o editor da 009 passa a ser usado sob
autorização real, fundada em A10 (Art. 21, VI) [Interpretação B1, B2].

**Independent Test**: com operador CPAEG, executar o roteiro de verificação da 009 e
obter o mesmo resultado funcional.

**Acceptance Scenarios**:

1. **Given** operador CPAEG, **When** abre o editor, **Then** vê a lista de Pesquisas com
   todas as Versões, como na 009.
2. **Given** operador CPAEG e uma Versão em rascunho, **When** adiciona Seção, Pergunta,
   Opção, escala, desvio ou encaminhamento, **Then** a gravação ocorre pela operação da
   002, exatamente como na 009.
3. **Given** operador CPAEG, **When** cria nova Versão a partir de uma publicada,
   **Then** a cópia é criada em rascunho, como na 009.
4. **Given** operador CPAEG e um rascunho, **When** consulta o diagnóstico técnico e a
   pré-visualização, **Then** obtém os mesmos resultados da 009.
5. **Given** operador CPAEG e uma Versão publicada, **When** tenta gravar nela, **Then**
   a recusa por Versão publicada da 009 continua idêntica: autorização não abre exceção
   à imutabilidade.
6. **Given** operador CPAEG, **When** procura a ação de publicar, **Then** ela não
   existe, como na 009.

---

### User Story 4 - Recusar acesso e escrita a quem não tem vínculo ativo (Priority: P1)

Uma requisição sem operador identificado, ou de operador sem vínculo ativo, é recusada
em toda página do editor, de leitura ou escrita, antes de qualquer gravação.

**Why this priority**: fecha a lacuna da 009 em que acesso ao ambiente equivalia a poder
editar (Princípio X; Governança de Permissões).

**Independent Test**: percorrer todas as rotas do editor sem operador e com operador sem
vínculo ativo; verificar recusa em todas e conteúdo idêntico antes e depois.

**Acceptance Scenarios**:

1. **Given** nenhuma identificação, **When** qualquer página do editor é solicitada,
   **Then** nenhum conteúdo do instrumento é apresentado e nada é gravado: no modo de
   demonstração, quem usa é levado à escolha de operador fictício; fora dele, o editor não
   responde.
2. **Given** operador identificado e sem nenhum vínculo, **When** abre o editor, **Then**
   a recusa explica que não há atuação institucional registrada para ele.
3. **Given** operador cujo único vínculo está inativo, **When** abre o editor, **Then** a
   recusa é a mesma do caso sem vínculo.
4. **Given** operador sem vínculo ativo, **When** envia diretamente uma gravação de
   qualquer rota de escrita, **Then** a resposta é recusa, nada é gravado e o conteúdo
   consultado depois é idêntico ao anterior.

---

### User Story 5 - Proteger no servidor todas as rotas de escrita (Priority: P1)

Toda rota do editor que grava verifica, no servidor, a identificação, o vínculo ativo e
a capacidade de elaborar, antes de validar o formulário e antes de qualquer gravação.
Esconder botões é conveniência; a proteção é a verificação no servidor.

**Why this priority**: autorização apenas na apresentação é contornável por envio direto
(caso J).

**Independent Test**: para cada rota de escrita da 009, enviar a gravação diretamente,
sem passar pela página, com operador sem vínculo, com operador CSAEG e com operador
CPAEG; só o último grava.

**Acceptance Scenarios**:

1. **Given** operador CSAEG e um rascunho, **When** envia diretamente a gravação de
   "adicionar Pergunta", **Then** recebe recusa, e nada é gravado.
2. **Given** operador CSAEG, **When** envia diretamente "criar Pesquisa", **Then** recebe
   recusa, e nenhuma Pesquisa é criada.
3. **Given** operador sem vínculo e uma gravação com dados inválidos, **When** a envia,
   **Then** recebe recusa de acesso, e **não** os erros de validação do formulário.
4. **Given** uma nova rota de escrita acrescentada ao editor, **When** a verificação
   automatizada de cobertura é executada, **Then** ela falha se a rota não estiver
   protegida pela capacidade de elaborar.
5. **Given** operador CPAEG cujo vínculo é desativado entre abrir o formulário e
   enviá-lo, **When** envia, **Then** recebe recusa, e nada é gravado.

---

### User Story 6 - Atuação de unidade sem poder institucional global (Priority: P1)

O operador com atuação CSAEG consulta as Versões publicadas e sua pré-visualização, para
aplicar o questionário e reportar atualizações à CPAEG. Ele não vê rascunhos, não obtém
diagnóstico e não grava nada no instrumento institucional.

**Why this priority**: diferencia atuação central e de unidade (caso D) com o menor
privilégio sustentado [Interpretação B5, B6, B7].

**Independent Test**: com operador CSAEG, verificar o que aparece nas listas e a recusa
em toda página de rascunho, diagnóstico e escrita.

**Acceptance Scenarios**:

1. **Given** operador CSAEG, **When** abre a lista de Pesquisas, **Then** vê as
   Pesquisas e, em cada uma, somente as Versões publicadas, com aviso de que rascunhos não
   são exibidos para sua atuação.
2. **Given** operador CSAEG, **When** abre uma Versão publicada e sua pré-visualização,
   **Then** vê o conteúdo em leitura, sem nenhuma ação de escrita, inclusive sem "criar
   nova Versão a partir desta".
3. **Given** operador CSAEG, **When** abre diretamente o endereço de um rascunho, de seu
   diagnóstico ou de sua pré-visualização, **Then** recebe recusa que explica que seu
   vínculo permite consultar o instrumento publicado, mas não as Versões em rascunho.
4. **Given** operadores CSAEG das unidades A e B, **When** consultam a mesma Versão
   publicada, **Then** veem o mesmo conteúdo: o instrumento é institucional e não
   pertence a unidade.
5. **Given** operador CSAEG da unidade A, **When** qualquer ação é avaliada, **Then** a
   unidade do vínculo não lhe confere nenhuma capacidade adicional nem acesso a dado de
   qualquer unidade.

---

### User Story 7 - Preservar somente leitura e imutabilidade (Priority: P1)

Quem pode consultar não necessariamente pode editar. A consulta de Versão publicada
continua sem controles de edição, para qualquer atuação. Para a CPAEG, as recusas por
Versão publicada da 009 permanecem idênticas.

**Why this priority**: separa visualização de edição (orientação 10) e preserva o
Princípio VIII.

**Independent Test**: comparar as páginas de Versão publicada para CPAEG e CSAEG e as
recusas de escrita em Versão publicada com as da 009.

**Acceptance Scenarios**:

1. **Given** operador CPAEG e Versão publicada (caso E), **When** a consulta, **Then** vê
   estrutura e pré-visualização, e a única ação disponível é criar nova Versão a partir
   dela.
2. **Given** operador CSAEG e a mesma Versão, **When** a consulta, **Then** vê a mesma
   estrutura, sem nenhuma ação.
3. **Given** qualquer atuação, **When** há gravação dirigida a Versão publicada, **Then**
   nada é gravado. Para CSAEG, a recusa é de acesso. Para CPAEG, a recusa é a da 009.

---

### User Story 8 - Operador com mais de um vínculo (Priority: P2)

Um operador pode ter mais de um vínculo ativo, por exemplo CPAEG e CSAEG de uma unidade,
ou CSAEG de duas unidades. Suas capacidades são a união das capacidades dos vínculos
ativos.

**Why this priority**: a PAEG não impede que a mesma pessoa integre a CPAEG e uma CSAEG
(caso G). Não há consumidor para "trocar de papel ativo".

**Independent Test**: registrar dois vínculos para o mesmo operador e verificar
capacidades; desativar um e verificar de novo.

**Acceptance Scenarios**:

1. **Given** operador com CPAEG e CSAEG (unidade A) ativos, **When** usa o editor,
   **Then** tem as capacidades da CPAEG, sem precisar escolher papel.
2. **Given** o mesmo operador, **When** o vínculo CPAEG é desativado, **Then** passa a
   ter somente as capacidades da CSAEG na requisição seguinte.
3. **Given** operador com CSAEG das unidades A e B, **When** usa o editor, **Then** tem
   as mesmas capacidades de um operador CSAEG: duas unidades não somam poder
   institucional.
4. **Given** operador com vários vínculos, **When** o contexto de atuação é exibido,
   **Then** todas as atuações ativas aparecem.

---

### User Story 9 - Vínculo inativo e desativação (Priority: P2)

Um vínculo pode ser desativado sem ser apagado. Vínculo inativo não confere nenhuma
capacidade, e o efeito é imediato.

**Why this priority**: designações institucionais terminam (nova portaria). O sistema
precisa refletir o fim sem perder a informação de que o vínculo existiu.

**Independent Test**: desativar vínculo de operador em uso e verificar recusa na
requisição seguinte; reativar e verificar de novo.

**Acceptance Scenarios**:

1. **Given** vínculo CPAEG ativo, **When** é desativado, **Then** a próxima requisição
   do operador ao editor é recusada.
2. **Given** vínculo inativo, **When** o responsável técnico o reativa, **Then** as
   capacidades voltam na requisição seguinte. **[Hipótese]**
3. **Given** vínculo inativo de CSAEG na unidade A, **When** se registra vínculo ativo
   CSAEG na mesma unidade para o mesmo operador, **Then** o sistema trata isso como
   reativação ou recusa por duplicidade, conforme o plan, mas nunca deixa dois vínculos
   iguais ativos.

---

### User Story 10 - Privilégio técnico não substitui governança (Priority: P2)

Nenhuma condição técnica — conta de superusuário, membro de equipe técnica, acesso à
administração técnica, acesso ao banco, controle do servidor ou modo de demonstração —
confere capacidade funcional. Somente vínculo ativo confere.

**Why this priority**: separa competência técnica de competência normativa (Princípio X;
Governança de Permissões; caso F).

**Independent Test**: com qualquer condição técnica disponível e sem vínculo,
verificar recusa em todo o editor.

**Acceptance Scenarios**:

1. **Given** um operador com privilégio técnico máximo e sem vínculo, **When** usa o
   editor, **Then** recebe recusa, como qualquer operador sem vínculo.
2. **Given** modo de demonstração ligado e operador sem vínculo, **When** usa o editor,
   **Then** recebe recusa: o modo não autoriza (caso H).
3. **Given** a regra de autorização, **When** é inspecionada, **Then** não consulta
   nenhuma marca técnica (superusuário, equipe, administração) nem o modo de
   demonstração.

---

### User Story 11 - Publicação permanece indisponível (Priority: P2)

Mesmo com governança, nenhuma atuação publica Versão pelo sistema, porque a PAEG não
define quem tem essa competência. A decisão é registrada como pendente, com a indicação
normativa de quem resolve a omissão (Art. 26).

**Why this priority**: é o ponto mais sensível. Expor publicação sem fundamento
transformaria ausência normativa em regra de software (Princípio X; XXIX; casos K e L).

**Independent Test**: verificar que nenhuma página, rota ou atuação aciona a publicação
e que nenhuma estrutura de publicação foi criada.

**Acceptance Scenarios**:

1. **Given** operador CPAEG e rascunho "sem impedimentos técnicos conhecidos", **When**
   procura publicar, **Then** não há ação, botão desabilitado, pedido, envio para
   aprovação ou aviso de "pronta para publicar" (caso K).
2. **Given** qualquer operador, **When** envia diretamente uma requisição que tente
   publicar, **Then** nenhuma rota a aceita, e a Versão continua em RASCUNHO.
3. **Given** o conjunto de atuações e capacidades, **When** é inspecionado, **Then** não
   existe capacidade, atuação ou situação de vínculo associada a publicar.

---

### User Story 12 - Recusas compreensíveis e acessíveis (Priority: P3)

Toda recusa usa linguagem operacional, diz o que o vínculo atual não permite, sem expor
detalhes internos, e é acessível.

**Why this priority**: recusa explícita ajuda o diagnóstico administrativo (orientação
17) sem expor estrutura interna (Princípio XVI).

**Independent Test**: revisar o texto e a marcação de cada tipo de recusa.

**Acceptance Scenarios**:

1. **Given** operador CSAEG tentando editar, **When** recebe a recusa, **Then** lê, em
   linguagem operacional, que seu vínculo permite consultar o instrumento publicado,
   mas não editar rascunhos. A compreensão não depende de referência a artigo da PAEG.
2. **Given** qualquer recusa, **When** exibida, **Then** não mostra identificador
   técnico, nome de regra, nome de papel técnico, código de permissão nem detalhe de
   implementação.
3. **Given** uma recusa, **When** navegada por teclado e leitor de tela, **Then** o
   título, a explicação e o caminho de volta são anunciados e alcançáveis.

---

### Cenários ponta a ponta *(mandatory para esta feature)*

Correspondem aos casos A a L da solicitação.

| Caso | Situação | Resultado esperado | Histórias |
|------|----------|--------------------|-----------|
| A | Operador CPAEG acessa o editor | Acesso completo da 009, com contexto de atuação | US3 |
| B | Operador CPAEG edita rascunho | Gravação pela operação da 002, como na 009 | US3 |
| C | Operador sem vínculo tenta editar | Recusa de acesso; nada gravado | US4 |
| D | Operador CSAEG tenta ação institucional global (criar Pesquisa, editar rascunho, criar Versão a partir de outra) | Recusa de acesso; nada gravado | US5, US6 |
| E | Operador CPAEG consulta Versão publicada | Leitura e pré-visualização; somente "criar nova Versão a partir desta" | US7 |
| F | Privilégio técnico máximo sem vínculo | Recusa, igual à do operador sem vínculo | US10 |
| G | Operador com mais de um vínculo ativo | União das capacidades ativas | US8 |
| H | Modo de demonstração ligado | Escolha de operador fictício disponível; autorização pela regra | US2, US10 |
| I | Modo de demonstração desligado | Nenhuma página responde; nenhum operador é identificado; regra inalterada | US2 |
| J | Envio direto de gravação sem autorização | Recusa antes de validação e de gravação | US5 |
| K | Publicação sem competência definida | Indisponível; nenhuma estrutura criada; DP mantida | US11 |
| L | Publicação com fundamento normativo suficiente | **Não ocorre**: a análise normativa não encontrou fundamento (ver "Análise normativa", A e C). Se a instância competente decidir, uma feature futura especifica a menor autorização correspondente | US11 |

Roteiro único de demonstração:

1. Ligar o modo de demonstração e preparar os dados locais (baseline e operadores
   fictícios).
2. Abrir o editor sem operador → levado à escolha de operador fictício.
3. Escolher o operador fictício sem vínculo → recusa em todas as páginas.
4. Escolher o operador CSAEG da unidade A → só Versões publicadas; abrir rascunho por
   endereço → recusa; enviar gravação direta → recusa, nada gravado.
5. Escolher o operador CPAEG → editor completo da 009; criar Versão a partir da baseline
   e editar a cópia; diagnóstico e pré-visualização; nenhuma ação de publicar.
6. Desativar o vínculo CPAEG pelo mecanismo administrativo → próxima requisição
   recusada.
7. Desligar o modo → nada responde.

### Telas e estados

Nenhuma tela nova de gestão. Apenas:

- **Escolha de operador fictício** (somente modo de demonstração): lista dos operadores
  fictícios preparados, com suas atuações escritas por extenso.
- **Contexto de atuação** em toda página do editor: atuações ativas do operador
  (por exemplo, "CPAEG — atuação institucional"; "CSAEG — unidade Serra"), e o
  aviso de ambiente não produtivo com identificação simulada.
- **Recusa de acesso**: página própria com título, explicação em linguagem institucional
  e caminho de volta. Variantes: sem atuação ativa; vínculo atual não permite a ação.
  Sem operador identificado no modo de demonstração não há recusa: há encaminhamento à
  escolha de operador fictício.
- **Páginas da 009**: as mesmas, com ações e itens filtrados pelas capacidades.

### Edge Cases

- **Vínculo desativado durante o uso**: a requisição seguinte é avaliada com os vínculos
  atuais; um formulário aberto antes não grava (US5, cenário 5).
- **Dois operadores CPAEG editando o mesmo rascunho**: comportamento da 009, sem bloqueio
  de edição; a última operação aceita prevalece. Autoria e histórico continuam fora
  (009/DP-903). Esta feature não cria coautoria, bloqueio, comentário nem revisão.
- **Operador CSAEG e elemento inexistente**: a verificação de vínculo ocorre antes da
  consulta ao elemento; sem vínculo ativo, a resposta é recusa, e não "inexistente".
  Com vínculo ativo, elemento inexistente continua "inexistente", como na 009.
- **Operador CSAEG e endereço de rascunho**: recusa de acesso, e não "inexistente". O
  instrumento é configuração, não dado pessoal; revelar que o endereço é de um rascunho
  não expõe dado sensível e ajuda o diagnóstico.
- **Gravação dirigida a Versão publicada**: para quem não pode elaborar, recusa de
  acesso; para CPAEG, a recusa da 009. A autorização é verificada antes.
- **Vínculo CSAEG com unidade sem nenhuma Conclusão Acadêmica**: permitido. A unidade é
  designação institucional e não depende de haver egresso registrado.
- **Unidade escrita de formas diferentes** (por exemplo, abreviada): nesta feature
  nenhuma capacidade depende da unidade; a consistência da designação é DP-1005.
- **Identificador de operador igual a dado de Pessoa egressa**: irrelevante; operador e
  Pessoa são conceitos separados e nunca são associados (FR-008).
- **Operador com vínculo CPAEG e CSAEG**: as capacidades da CPAEG prevalecem por união,
  e não por "papel ativo".
- **Modo de demonstração ligado por engano em ambiente com vínculos reais**: a escolha
  de operador oferece somente operadores fictícios preparados (FR-057), e nunca vínculos
  registrados para operadores reais.
- **Página de recusa com o modo de demonstração desligado**: não ocorre; com o modo
  desligado nada responde (I).
- **Baseline da 003**: somente operador CPAEG pode editá-la, como qualquer rascunho
  (009 FR-009). Esta feature não cria proteção pelo nome (009/DP-902).
- **Registro de vínculo para identificador vazio ou com espaços apenas**: recusado.

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII):

- **[PAEG Art. n]**: decorre da PAEG (categoria A da Análise normativa).
- **[Interpretação Bn]**: interpretação operacional da categoria B.
- **[Const.]**: decorre da Constituição.
- **[002]**, **[008]**, **[009]**: decorre de feature anterior.
- **[Arquitetura]**: decisão arquitetural.
- **[Hipótese]**: escolha de produto reversível.
- **[Escopo]**: decisão de escopo desta feature, revisável por feature futura.

Nenhum requisito desta feature cria competência institucional não prevista na PAEG,
capacidade nova do instrumento ou etapa de fluxo.

### Functional Requirements

**Natureza e fronteira**

- **FR-001**: A regra de autorização DEVE receber, conceitualmente, um operador já
  identificado ou a ausência de operador, e decidir somente com base nos vínculos ativos
  desse operador e na ação solicitada. [Const. — X, XV; Arquitetura]
- **FR-002**: A regra de autorização NÃO DEVE depender de mecanismo de identificação
  específico. Trocar a identificação não produtiva por uma produtiva NÃO DEVE exigir
  alterar a regra, as atuações, as capacidades nem os vínculos. [Const. — V, XV]
- **FR-003**: Esta feature NÃO DEVE criar senha, credencial, OTP, integração com Gov.br,
  SSO, LDAP, provedor de identidade, tela de login, recuperação de acesso nem cadastro de
  operadores com credencial. [Const. — XV, XXII; Escopo]
- **FR-004**: A regra de autorização DEVE ser verificável por testes automatizados com
  operadores fictícios, sem provedor externo de identidade. [Const. — XXV, XXVI]
- **FR-005**: A regra NÃO DEVE consultar o modo de demonstração. O modo decide apenas se
  a identificação não produtiva existe (FR-053), nunca o que um operador pode fazer.
  [Const. — X]

**Operador institucional**

- **FR-006**: O operador DEVE ser identificado por um identificador de operador, único
  entre operadores, sem significado interpretado pela regra. [Arquitetura]
- **FR-007**: A regra NÃO DEVE inferir atuação, unidade ou capacidade do formato do
  identificador, de curso, de e-mail, de último acesso, de Conclusão Acadêmica ou de
  qualquer outro dado que não seja o vínculo. [Const. — XII; XVI]
- **FR-008**: Operador institucional NÃO DEVE ser representado por Pessoa, Conclusão
  Acadêmica, Participação ou qualquer estrutura do egresso, nem associado a elas.
  Ser egresso não confere nem retira capacidade institucional. [Const. — Terminologia;
  VI; XV]
- **FR-009**: Esta feature NÃO DEVE gravar dado pessoal do operador além do
  identificador de operador. Nome, e-mail, matrícula, cargo e lotação NÃO DEVEM ser
  gravados. [Const. — XVI; Hipótese quanto à suficiência do identificador]

**Atuações institucionais**

- **FR-010**: DEVEM existir exatamente duas atuações institucionais:
  - **CPAEG** — Comissão Própria de Acompanhamento do Egresso [PAEG Art. 16, Art. 21];
  - **CSAEG** — Comissão Setorial de Acompanhamento de Egressos [PAEG Art. 18, III;
    Art. 22].
- **FR-011**: NÃO DEVEM ser criados papéis genéricos ou paralelos à PAEG, como
  administrador, superadministrador, gestor, editor, leitor, publicador, aprovador ou
  revisor. [Const. — X, XXII; Escopo]
- **FR-012**: Proex, DIREC, Proen, Diretorias de unidade e Reitoria NÃO DEVEM ser
  representadas como atuações nesta feature, porque nenhuma superfície existente as
  consome. Isso não nega suas competências (PAEG Art. 2º, Art. 10, II, Art. 14,
  Art. 15, Art. 18); apenas não as modela sem consumidor (DP-1006). [Const. — XXII,
  XXIX; Escopo]
- **FR-013**: A lista de atuações DEVE ser fechada e definida pela especificação. NÃO
  DEVE ser possível criar atuação nova por configuração ou cadastro. [Const. — XXII,
  XXIII]

**Escopos**

- **FR-014**: O escopo DEVE decorrer da atuação:
  - CPAEG ⇒ escopo **institucional**, sem unidade [PAEG Art. 21, I, V;
    Interpretação B3];
  - CSAEG ⇒ escopo de **exatamente uma unidade** explícita [PAEG Art. 18, Art. 22, I;
    Interpretação B4].
- **FR-015**: A unidade de um vínculo CSAEG DEVE usar a mesma designação textual de
  unidade que a fonte acadêmica usa nas Conclusões (001) e que os critérios de unidade
  da Campanha usam (004). Esta feature NÃO DEVE criar entidade, catálogo, árvore ou
  hierarquia de unidades, mantendo a decisão da 001 (R10) e da 004 de não ter tabela de
  unidade. [001; 004; Const. — XXII; DP-1005]
- **FR-016**: NÃO DEVEM ser criados organização, tenant, departamento, hierarquia de
  escopos, herança de escopo, escopo por Pesquisa, escopo por curso nem lista de acesso
  por objeto. [Const. — XII, XXII; Escopo]
- **FR-017**: Escopo de unidade NÃO DEVE conferir capacidade sobre o instrumento
  institucional, sobre outra unidade nem, nesta feature, sobre qualquer dado de unidade,
  porque não há superfície por unidade. Feature futura que criar superfície por unidade
  DEVE usar a unidade do vínculo explicitamente. [Const. — XII; Escopo]

**Vínculo de governança**

- **FR-018**: O vínculo DEVE registrar somente: o identificador do operador; a atuação;
  a unidade, quando CSAEG; a situação (ativo ou inativo). [Const. — XXII; Hipótese quanto
  à situação]
- **FR-019**: Vínculo CPAEG com unidade e vínculo CSAEG sem unidade DEVEM ser recusados.
  "Sem unidade" é representado por unidade vazia, nunca por ausência de valor, para que
  a regra de unicidade (FR-020) valha igualmente para CPAEG. [Clarifications 2026-10-02]
  [FR-014]
- **FR-020**: NÃO DEVEM coexistir dois vínculos **ativos** com o mesmo operador, a mesma
  atuação e a mesma unidade (para CPAEG: o mesmo operador e a atuação). [Arquitetura]
- **FR-021**: Um mesmo operador PODE ter vários vínculos ativos de atuações ou unidades
  diferentes. Suas capacidades DEVEM ser a união das capacidades de seus vínculos ativos.
  NÃO DEVE existir seleção de "papel ativo". [Escopo; Hipótese]
- **FR-022**: Vários operadores PODEM ter vínculo ativo com a mesma atuação e a mesma
  unidade. NÃO DEVE existir titular, presidente, mandato, eleição, substituição,
  suplência nem limite de quantidade. [PAEG Art. 17, Art. 19 (composição colegiada);
  Escopo]
- **FR-023**: Vínculo inativo NÃO DEVE conferir nenhuma capacidade. A desativação NÃO
  DEVE apagar o vínculo, e a exclusão NÃO DEVE ser oferecida como fluxo normal. A
  condição ativo/inativo serve somente para responder se o vínculo concede autorização
  agora. [Clarifications 2026-10-01]
- **FR-024**: Toda decisão de autorização DEVE considerar os vínculos vigentes no momento
  da requisição. Desativação ou registro DEVE ter efeito na requisição seguinte, sem
  depender de novo login, nova escolha de operador ou reinício. [Const. — XII, XVI]
- **FR-025**: O vínculo DEVE ser a única estrutura persistida nova. Operador separado,
  papel, permissão, papel-permissão, escopo, organização, política ou lista de acesso
  NÃO DEVEM ser criados. Se o plan concluir que precisa de outra estrutura, DEVE
  demonstrar o consumidor concreto em *Complexity Tracking*. [Const. — XXII; Escopo]
- **FR-026**: O vínculo NÃO DEVE ter datas de início e fim, número de portaria,
  fundamento, documento de designação, observação, histórico de alterações, autor do
  registro nem versionamento nesta feature (DP-1002; 009/DP-903). [Const. — XXII, XXIX;
  Clarifications 2026-10-01]
- **FR-027**: O vínculo NÃO DEVE afetar Pesquisa, Versão, Campanha, Participação,
  Resposta, Pessoa ou Conclusão Acadêmica. Nenhuma estrutura existente DEVE ser alterada
  por esta feature. [Const. — VII, XXVII]

**Capacidades**

- **FR-028**: DEVEM existir exatamente três capacidades, todas sobre ações que já
  existem na 009:
  - **consultar o instrumento publicado**: listar Pesquisas com suas Versões publicadas;
    consultar estrutura, Seções e Perguntas de Versão publicada; pré-visualizar Versão
    publicada;
  - **consultar rascunhos**: listar Versões em rascunho; consultar estrutura, Seções e
    Perguntas de rascunho; obter diagnóstico técnico; pré-visualizar rascunho;
  - **elaborar**: toda ação de escrita do editor, inclusive criar Pesquisa, criar
    Versão, criar Versão a partir de outra (de rascunho ou publicada), alterar dados da
    Versão, e criar, alterar, ordenar, mover e remover Seções, Perguntas e Opções, escala,
    complemento, desvios e encaminhamentos, além das páginas de formulário e de
    confirmação dessas ações.

  [009; Escopo]
- **FR-029**: **Acessar o editor** DEVE significar ter ao menos uma capacidade. Não é
  capacidade à parte. [Escopo]
- **FR-030**: A atuação **CPAEG** DEVE conferir as três capacidades. [PAEG Art. 21, VI;
  Interpretação B1, B2]
- **FR-031**: A atuação **CSAEG** DEVE conferir somente **consultar o instrumento
  publicado**. [PAEG Art. 22, IV; Interpretação B5, B6, B7]
- **FR-032**: A capacidade **elaborar** NÃO DEVE abrir exceção à imutabilidade da Versão
  publicada. As recusas da 009 para escrita em Versão publicada DEVEM continuar
  idênticas para quem pode elaborar. [002 FR-016, FR-017; 009 FR-018 a FR-020; Const. —
  VIII]
- **FR-033**: NÃO DEVE existir capacidade de publicar, aprovar, homologar, despublicar,
  gerir vínculos pela interface, gerir Campanha, consultar Participação ou Resposta, nem
  qualquer outra sem ação existente que a consuma. [Const. — X, XXII; FR-047]
- **FR-034**: As capacidades DEVEM ser regras explícitas e nomeadas por ação concreta
  (equivalentes a "pode consultar instrumento publicado", "pode consultar rascunhos",
  "pode elaborar"). NÃO DEVE ser criado motor de políticas, registro de permissões,
  matriz configurável, permissão por objeto, ABAC ou biblioteca genérica de autorização.
  [Const. — XXII; Escopo]
- **FR-035**: A associação entre atuação e capacidades DEVE ser fixa na especificação,
  não configurável por cadastro ou por ambiente. [Const. — X, XXII]
- **FR-036**: Quem não tem **consultar rascunhos** NÃO DEVE ver rascunhos em listas nem
  em contagens. A página DEVE informar que somente Versões publicadas são exibidas para
  a sua atuação. Uma Pesquisa sem Versão publicada DEVE aparecer com essa indicação.
  [Hipótese; Const. — XVI]
  *(Revisado pela 017 — interpretação C1 restrita à demonstração; DP-402 aberta)* A 017 permite gestão mínima pela CPAEG ativa somente na demonstração, sem publicação, critérios ou remoção; a competência produtiva continua pendente.

**Aplicação no editor e recusas**

- **FR-037**: Toda rota do editor, de leitura ou escrita, DEVE verificar no servidor,
  antes de qualquer outra coisa, se há operador identificado e se ele tem vínculo ativo.
  - Sem operador identificado, nenhum conteúdo DEVE ser apresentado e nada gravado: no
    modo de demonstração, quem usa DEVE ser levado à escolha de operador fictício
    (FR-055); fora dele, o editor não responde (FR-054).
  - Com operador identificado e sem vínculo ativo, a resposta DEVE ser recusa de acesso.

  [Const. — XII, XVI; Clarifications 2026-10-02]
- **FR-038**: Toda rota de leitura DEVE verificar a capacidade correspondente ao estado
  da Versão consultada (publicada ou rascunho) antes de apresentar conteúdo. [FR-028]
- **FR-039**: Toda rota de escrita, inclusive páginas de formulário e de confirmação de
  remoção, DEVE verificar a capacidade **elaborar** antes de validar o formulário, antes
  da verificação de Versão publicada da 009 e antes de qualquer gravação. A recusa NÃO
  DEVE revelar erros de validação. [Const. — XVI; caso J]
- **FR-040**: Nenhuma recusa de acesso DEVE gravar, alterar ou criar dado. O conteúdo
  consultado depois DEVE ser idêntico ao anterior. [009 FR-023]
- **FR-041**: Ocultar ações na apresentação DEVE ser apenas conveniência: as páginas
  NÃO DEVEM oferecer ações que o operador não pode executar, e a proteção DEVE ser
  sempre a verificação no servidor (FR-037 a FR-039). [Arquitetura]
- **FR-042**: DEVE existir verificação automatizada que percorra **todas** as rotas do
  editor e falhe se alguma não estiver associada a uma capacidade, ou se alguma rota de
  escrita não exigir **elaborar**. [Const. — XXVI]
- **FR-043**: A recusa de acesso DEVE ser explícita e distinta de "página inexistente"
  e de "rejeição" de operação da 002. Ela DEVE:
  - ter título e explicação em linguagem operacional;
  - dizer qual situação impede a ação: sem atuação institucional ativa; ou o vínculo
    atual não permite a ação (por exemplo, "Seu vínculo permite consultar o instrumento
    publicado, mas não editar rascunhos.");
  - oferecer caminho de volta.

  O texto principal NÃO DEVE depender de números de artigos da PAEG. Referência
  normativa, se houver, é complementar. [Const. — XIV, XX; orientação 17;
  Clarifications 2026-10-02]
- **FR-044**: A recusa NÃO DEVE expor identificador técnico, nome de regra, papel
  técnico, código de permissão, lista de vínculos, nome de outros operadores nem
  detalhes internos. [Const. — XVI]
- **FR-045**: Elemento inexistente, para operador com vínculo ativo, DEVE continuar com
  o comportamento da 009. Para quem não tem vínculo ativo, a recusa precede a consulta
  ao elemento (FR-037). [009; Const. — XVI]
- **FR-046**: Toda página do editor DEVE mostrar o contexto de atuação do operador: as
  atuações ativas por extenso, com a unidade quando CSAEG. [Const. — XIV, XX]

**Publicação**

- **FR-047**: A ação de publicar Versão DEVE continuar indisponível em toda superfície,
  para qualquer atuação, inclusive como botão desabilitado. A análise normativa não
  encontrou na PAEG quem publica ou aprova uma Versão (A; C). [Const. — X, XXIX;
  002/DP-001; 009 FR-076]
- **FR-048**: NÃO DEVE ser criada atuação, capacidade, vínculo ou marcação de
  "publicador", "aprovador" ou equivalente para contornar a lacuna. [Const. — X, XXIX]
- **FR-049**: NÃO DEVEM ser criados estados além de RASCUNHO e PUBLICADA (por exemplo,
  em aprovação, aprovada, rejeitada, homologada), pedido de publicação, aprovação,
  assinatura, tramitação, parecer, fila, notificação ou múltiplos aprovadores.
  [002 FR-011; 009 FR-017, FR-077; Const. — X]
- **FR-050**: NÃO DEVE ser criada estrutura antecipada para publicação futura. Quando a
  instância competente decidir (Art. 26), uma feature futura especificará a menor
  autorização correspondente. [Const. — XXII, XXIX]
- **FR-051**: A operação de publicar da 002 DEVE continuar como capacidade interna do
  domínio, usada somente pelos meios técnicos já existentes (preparo da demonstração e
  testes). Esta feature NÃO DEVE criar outro meio. [002; 008; 009 FR-079]
- **FR-052**: O diagnóstico "sem impedimentos técnicos conhecidos" DEVE continuar sem
  significar pronta, aprovada ou autorizada, inclusive para operador CPAEG. [009 FR-078]

**Identificação não produtiva e modo de demonstração**

- **FR-053**: A identificação não produtiva DEVE existir somente com o modo de
  demonstração ligado. Desligado, ela NÃO DEVE existir nem responder. [008; Const. —
  XVI]
- **FR-054**: Com o modo de demonstração desligado, o editor DEVE continuar sem
  responder, como na 009, porque não há identificação produtiva (DP-1001). Esta feature
  NÃO DEVE expor o editor em ambiente produtivo nem criar entrada alternativa. Nenhum
  identificador de operador fornecido pelo cliente (parâmetro de endereço, cabeçalho,
  cookie não autenticado) DEVE ser aceito como identificação fora do modo de
  demonstração. [009 FR-002, FR-006; Escopo; Clarifications 2026-10-01]
- **FR-055**: No modo de demonstração, quem usa DEVE poder escolher, entre os
  operadores fictícios preparados, como qual operador atua, e trocar essa escolha. A
  escolha DEVE ser independente da escolha de Pessoa fictícia da 008. [008; 009 FR-005;
  Hipótese]
- **FR-056**: A escolha de operador fictício DEVE apenas identificar. Toda capacidade
  DEVE decorrer dos vínculos do operador escolhido, pela mesma regra usada em qualquer
  ambiente. [Const. — X; FR-005]
- **FR-057**: A escolha DEVE oferecer e aceitar **somente** operadores fictícios
  preparados para a demonstração. Ela NÃO DEVE permitir informar identificador
  arbitrário nem selecionar operador cujo vínculo foi registrado pelo mecanismo
  administrativo para pessoa real. O plan define como distinguir operadores fictícios
  sem criar atuação, papel ou atributo institucional. [Const. — XVI; Arquitetura]
- **FR-058**: O preparo local da demonstração DEVERIA disponibilizar, no mínimo:
  operador fictício CPAEG; operador fictício CSAEG de uma unidade presente nos dados
  simulados; e operador fictício sem vínculo ativo. [Hipótese; FR-060]
- **FR-059**: O modo de demonstração NÃO DEVE ser atuação, papel, vínculo nem
  capacidade. Ligado, ele NÃO DEVE conceder nada a quem não escolheu operador ou
  escolheu operador sem vínculo ativo. [Const. — X; caso H]
- **FR-060**: Operadores fictícios DEVEM usar identificadores evidentemente fictícios,
  que não correspondam a pessoa real. Unidades PODEM ser as designações já usadas nos
  dados simulados, porque unidade não é dado pessoal. NÃO DEVEM existir pessoa real
  codificada, credencial padrão,
  operador padrão com acesso garantido nem vínculo criado automaticamente fora do
  preparo da demonstração e dos testes. [Const. — XVI; orientação 23]
- **FR-061**: O aviso permanente das páginas do editor (009 FR-003) DEVE passar a dizer
  que o ambiente é não produtivo, que a identificação é simulada por operador fictício
  e que os vínculos fictícios não representam designação institucional real. A
  afirmação "não há autenticação nem autorização" DEVE ser substituída, porque agora há
  autorização. [009 FR-003; Const. — X]

**Registro de vínculos**

- **FR-062**: Vínculos DEVEM ser registrados, consultados, desativados e reativados por
  um mecanismo técnico administrativo controlado, disponível somente a quem opera o
  ambiente. O plan escolhe o mecanismo. [Escopo; Arquitetura]
- **FR-063**: Esta feature NÃO DEVE criar tela, painel ou CRUD de governança, nem
  interface de gestão de papéis. Qualquer interface nova exige justificativa no plan.
  [Const. — XXII; orientação 22]
- **FR-064**: O mecanismo de registro DEVE aplicar FR-018 a FR-020 e recusar
  identificador vazio. Toda recusa DEVE ser tudo-ou-nada. [Arquitetura]
- **FR-065**: Registrar um vínculo NÃO DEVE ser apresentado como designação
  institucional. O mecanismo DEVE deixar claro que registra, no sistema, designação feita
  fora dele (Art. 17, Art. 18, III, Art. 24), e que o sistema não a verifica.
  [Interpretação B9; Const. — X; DP-1002]
- **FR-066**: Poder operar o mecanismo de registro NÃO DEVE conferir, por si, nenhuma
  capacidade funcional. Quem opera o ambiente só atua no editor se tiver vínculo ativo,
  como qualquer operador. [Const. — X; Governança de Permissões]

**Privilégio técnico**

- **FR-067**: Nenhuma condição técnica DEVE conferir capacidade: conta de
  superusuário, marca de equipe técnica, acesso à administração técnica, acesso ao
  banco de dados, controle do servidor, modo de demonstração ou acesso ao mecanismo de
  registro. A regra NÃO DEVE consultar essas condições. [Const. — X; Governança de
  Permissões; caso F]
- **FR-068**: Se uma feature futura introduzir contas técnicas ou administração técnica
  por interface, elas NÃO DEVEM ser usadas como atalho de autorização funcional.
  [Const. — X]

**Preservação da Feature 009**

- **FR-069**: Para operador com atuação CPAEG, o editor DEVE continuar funcionalmente
  idêntico ao da 009: mesmas páginas, ações, recusas, mensagens, diagnóstico,
  pré-visualização e imutabilidade, exceto o contexto de atuação (FR-046) e o aviso
  (FR-061). [009; Escopo]
- **FR-070**: Esta feature NÃO DEVE acrescentar capacidade editorial: nenhum tipo,
  operação, campo, estado, renomeação, exclusão, publicação, comentário, coautoria,
  bloqueio de edição, revisão por pares ou atribuição de responsável. [009; Const. —
  XXIII; orientação 13]
- **FR-071**: As regras da 002 e da 006 e as rejeições traduzidas pela 009 NÃO DEVEM
  mudar. [002; 006; 009 FR-109]
- **FR-072**: A jornada do egresso da 008 NÃO DEVE mudar nem depender de operador
  institucional. [008; Const. — Terminologia]

**Escopo negativo verificável**

- **FR-073**: Esta feature NÃO DEVE criar tela, ação, rota ou regra de Campanha,
  população elegível, monitoramento, painel, exportação ou consulta de Participação e
  Resposta. [004/DP-402; Escopo; orientação 19 e 20]
- **FR-074**: Esta feature NÃO DEVE criar registro de auditoria, histórico de ações,
  trilha de eventos nem autoria de alterações. O registro técnico de eventos segue a
  seção "Observabilidade" da Constituição e NÃO DEVE conter dado pessoal além do
  identificador de operador. [Const. — Observabilidade, XVI, XXII; 009/DP-903]
- **FR-075**: Esta feature NÃO DEVE criar multi-tenancy: base por unidade, banco por
  campus, endereço por unidade nem configuração por unidade. [Const. — XII]
  *(Revisado pela 017 — interpretação C1 restrita à demonstração; DP-402 aberta)* A 017 permite gestão mínima pela CPAEG ativa somente na demonstração, sem publicação, critérios ou remoção; a competência produtiva continua pendente.

**Interface, linguagem e acessibilidade**

- **FR-076**: A interface DEVE usar os termos: "Comissão Própria de Acompanhamento do
  Egresso (CPAEG)", "Comissão Setorial de Acompanhamento de Egressos (CSAEG)",
  "unidade", "atuação institucional". NÃO DEVE mostrar "role", "permission", "ACL",
  "policy", "scope", nomes de regra nem identificadores técnicos. [PAEG Art. 16, Art. 18,
  III; orientação 30]
- **FR-077**: A escolha de operador fictício, o contexto de atuação e as recusas DEVEM
  seguir os mesmos requisitos de acessibilidade e responsividade das páginas da 009
  (009 FR-110 a FR-112): HTML semântico, teclado, foco visível, contraste, estados em
  texto e funcionamento a partir de 320 px. [Const. — XX, XXI]
- **FR-078**: As páginas novas DEVEM ser geradas no servidor e funcionar sem JavaScript,
  como as da 008 e da 009. [008; 009 FR-098]

### Matriz mínima de capacidades

| Ação existente (009) | Capacidade | CPAEG | CSAEG | Sem vínculo ativo / sem identificação |
|----------------------|-----------|:-----:|:-----:|:-------------------------------------:|
| Listar Pesquisas e Versões publicadas | consultar o instrumento publicado | Sim | Sim | Recusa |
| Consultar Versão publicada (estrutura, Seção, Pergunta) | consultar o instrumento publicado | Sim | Sim | Recusa |
| Pré-visualizar Versão publicada | consultar o instrumento publicado | Sim | Sim | Recusa |
| Listar e consultar rascunhos | consultar rascunhos | Sim | Recusa | Recusa |
| Diagnóstico técnico (só rascunho) | consultar rascunhos | Sim | Recusa | Recusa |
| Pré-visualizar rascunho | consultar rascunhos | Sim | Recusa | Recusa |
| Criar Pesquisa | elaborar | Sim | Recusa | Recusa |
| Criar Versão; criar Versão a partir de outra | elaborar | Sim | Recusa | Recusa |
| Editar rascunho (dados, Seções, Perguntas, Opções, escala, desvios, encaminhamentos; ordenar, mover, remover) | elaborar | Sim | Recusa | Recusa |
| Gravar em Versão publicada | — | Recusa da 009 (imutável) | Recusa | Recusa |
| Publicar | — | Indisponível | Indisponível | Indisponível |

### Key Entities *(include if feature involves data)*

**Uma entidade nova.**

- **Vínculo de governança**: registro de que um operador atua institucionalmente.
  - Atributos: identificador do operador; atuação (CPAEG | CSAEG); unidade (não vazia
    para CSAEG, vazia para CPAEG); situação (ativo | inativo).
  - Regras: FR-018 a FR-024.
  - Relações: nenhuma com as entidades existentes. A unidade é a mesma designação textual
    da fonte acadêmica, sem chave para outra entidade (FR-015).
  - Não é dado sobre o egresso. É registro administrativo de governança.

**Conceitos sem persistência própria**:

- **Operador institucional**: existe pelo identificador presente nos vínculos e pela
  identificação da requisição. Não há cadastro de operador (FR-025). Um operador sem
  nenhum vínculo é apenas um identificador sem atuação.
- **Atuação**, **escopo** e **capacidade**: valores e regras fixos da especificação
  (FR-010, FR-014, FR-028, FR-035), não cadastros.
- **Operador fictício**: operador com identificador fictício, usado no preparo da
  demonstração e nos testes.

**Entidades existentes**: nenhuma alterada (FR-027).

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| Atuação e unidade do vínculo | Registro administrativo que reflete designação institucional externa (portaria) | Mecanismo administrativo (FR-062); designação pela Reitoria ou Diretor-Geral (PAEG Art. 17, Art. 24) | O sistema não verifica a designação (FR-065; DP-1002). Divergência é corrigida desativando ou registrando vínculo |
| Situação do vínculo | Registro administrativo | Mecanismo administrativo | Não aplicável |
| Identificador do operador | Identificação do operador (fora da regra) | Nesta feature, somente fictício (FR-055, FR-060) | Não aplicável |
| Capacidades do operador | Derivado | União das capacidades das atuações dos vínculos ativos (FR-021, FR-030, FR-031) | Não aplicável; calculado a cada requisição |

Nenhum dado de egresso, institucional acadêmico ou declarado é lido ou gravado por esta
feature.

### Análise de persistência

- **Entidades novas**: uma (vínculo de governança). Justificativa: é o único fato que
  não pode ser derivado de nada existente; sem ele não há como saber quem atua pela
  CPAEG ou pela CSAEG.
- **Por que não mais de uma**:
  - operador separado: não há atributo do operador a guardar além do identificador
    (FR-009), e o identificador vive no vínculo;
  - papel, permissão e escopo: são listas fechadas da spec (FR-013, FR-035);
  - unidade: já existe como designação da fonte acadêmica (FR-015).
- **Alterações em estruturas existentes**: nenhuma.
- **Estado de interface**: a escolha de operador fictício segue o mesmo tipo de
  mecanismo não persistente da escolha de Pessoa fictícia da 008; o plan decide.
- **Migração**: aditiva, sem impacto histórico (Princípio XXVII).

### Cobertura de verificação exigida

O plan e as tasks DEVEM prever verificação automatizada, no mínimo, para:

- registro de vínculos: CPAEG sem unidade; CSAEG com unidade; recusas de CPAEG com
  unidade, CSAEG sem unidade, identificador vazio e duplicidade ativa; vários
  operadores com a mesma atuação; desativação e reativação;
- regra de autorização, de forma isolada: sem operador; operador sem vínculo; vínculo
  inativo; CPAEG; CSAEG; CPAEG + CSAEG; CSAEG de duas unidades; efeito imediato da
  desativação;
- independência da regra: mesmo resultado com o modo de demonstração ligado e desligado
  quando a regra é avaliada diretamente; nenhuma condição técnica consultada;
- cobertura de **todas** as rotas do editor (FR-042);
- para cada rota de escrita: envio direto sem operador, sem vínculo, CSAEG → recusa,
  nada gravado, sem erros de validação; CPAEG → comportamento da 009;
- para cada rota de leitura: CSAEG em publicada → permitido; CSAEG em rascunho e
  diagnóstico → recusa; listas sem rascunhos para CSAEG;
- recusa por Versão publicada da 009 inalterada para CPAEG;
- ausência de qualquer ação ou rota de publicação;
- escolha de operador fictício: só com o modo ligado; só operadores fictícios; troca;
  identificador arbitrário recusado;
- conteúdo das recusas: termos institucionais; ausência de termos e identificadores
  técnicos; marcação acessível;
- regressão: a suíte de verificação da 009, executada com operador CPAEG, continua
  passando; a jornada da 008 não muda.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das rotas do editor estão associadas a uma capacidade, e 100% das
  rotas de escrita exigem **elaborar**, comprovado por verificação automatizada que
  falha diante de rota nova não protegida.
- **SC-002**: Em 100% dos envios diretos de gravação sem operador, sem vínculo ativo ou
  com atuação CSAEG, nada é gravado, e o conteúdo consultado depois é idêntico ao
  anterior.
- **SC-003**: Com atuação CPAEG, 100% dos cenários de verificação da 009 produzem o mesmo
  resultado funcional de antes desta feature.
- **SC-004**: Um operador com privilégio técnico e sem vínculo ativo obtém exatamente as
  mesmas recusas que um operador comum sem vínculo, em 100% das rotas.
- **SC-005**: Desativar um vínculo faz a requisição seguinte do operador ser avaliada sem
  ele, sem reinício, nova escolha ou intervenção adicional.
- **SC-006**: Zero ações, rotas, estados, atuações ou capacidades de publicação,
  aprovação ou fluxo existem depois desta feature.
- **SC-007**: Exatamente uma estrutura persistida nova existe, e nenhuma estrutura
  existente foi alterada.
- **SC-008**: Exatamente duas atuações e três capacidades existem, todas nomeadas pela
  especificação e nenhuma configurável.
- **SC-009**: Com o modo de demonstração desligado, nenhuma página do editor nem da
  escolha de operador responde.
- **SC-010**: Uma pessoa que nunca usou o editor, diante de uma recusa, identifica
  corretamente se não tem atuação ativa ou se seu vínculo não permite a ação, em revisão
  do roteiro de demonstração, sem consultar documentação técnica nem a PAEG.
- **SC-011**: Nenhuma página ou recusa exibe termo técnico de autorização ("role",
  "permission", "ACL", "policy", "scope") nem identificador técnico.

## Assumptions

Apenas suposições não institucionais. As regras institucionais em aberto estão em
"Decisões Pendentes".

- O volume de operadores é pequeno (dezenas), e as comissões são colegiadas. Não há meta
  de desempenho além de páginas responsivas no ambiente local.
- Verificar vínculos a cada requisição é aceitável nesse volume.
- O mecanismo administrativo de registro é operado por quem já controla o ambiente; não
  há requisito de autosserviço.
- A escolha de operador fictício pode seguir o mesmo tipo de mecanismo da escolha de
  Pessoa fictícia da 008, sem sessão autenticada.
- A designação textual de unidade da fonte acadêmica simulada basta para os vínculos
  fictícios.
- A identificação não produtiva não exige incluir mecanismo de autenticação, conta ou
  sessão autenticada na aplicação: a 008 já identifica a Pessoa fictícia sem eles. Se o
  plan concluir o contrário, DEVE justificar, porque a verificação automatizada da 005
  hoje proíbe esses mecanismos.
- O preparo da demonstração da 008 continua sendo o meio de ter dados locais, agora
  também com operadores fictícios.

## Relação com outras features

- **001**: a designação de unidade é reutilizada sem nova entidade (FR-015). Pessoa e
  Conclusão não são operadores (FR-008).
- **002**: nenhuma regra muda (FR-071). `publicar` continua interna (FR-051).
  002/DP-001 e 002/DP-002 continuam abertas.
- **003**: a baseline só pode ser editada por CPAEG, como qualquer rascunho; sem
  proteção por nome (009/DP-902).
- **004**: não usada. Nenhuma regra de Campanha (FR-073). 004/DP-402 não é afetada; a
  regra de autorização desta feature não é antecipada para Campanha.
- **005/006/007**: não usadas. Nenhum acesso a Participação ou Resposta (FR-073).
- **008**: a jornada do egresso não muda (FR-072). O modo de demonstração continua
  sendo a chave do ambiente não produtivo e passa a oferecer também a escolha de
  operador fictício (FR-053, FR-055).
- **ADR 0002** (imutabilidade da Versão publicada garantida pelas operações da
  aplicação): continua suficiente. Esta feature acrescenta operadores, mas toda escrita
  continua passando pelas operações da 002 (FR-071), sem novo escritor fora delas.
- **009**: consumidor imediato. O editor passa a respeitar a regra de autorização
  (FR-037 a FR-046) e fica funcionalmente idêntico para CPAEG (FR-069). FR-003, FR-004
  e FR-080 da 009 são substituídos por esta feature conforme FR-061, FR-010 a FR-035 e
  FR-047 a FR-050. 009/DP-901 fica parcialmente resolvida (ver Decisões Pendentes).
- **011** (futura, monitoramento e gestão da coleta): poderá usar atuação e unidade dos
  vínculos para superfícies por unidade (FR-017). Esta feature não antecipa nada para
  ela.
- **Identidade e Portal** (futuras): a identificação produtiva de operadores (DP-1001) e
  a identidade do egresso são features separadas. Uma não usa a outra.

## Invariantes Constitucionais Afetados *(mandatory)*

- **X — Tecnologia não redefine a governança (NON-NEGOTIABLE)**:
  - as atuações são as da PAEG (FR-010), com as capacidades derivadas das competências
    da categoria A e das interpretações explicitadas na categoria B;
  - a publicação não recebe autoridade inventada (FR-047, FR-048);
  - não há workflow de aprovação (FR-049);
  - privilégio técnico não confere competência (FR-066, FR-067);
  - o registro de vínculo não se apresenta como designação (FR-065).
- **XII — Base central; escopos por unidade**: escopo institucional e de unidade
  explícitos (FR-014), sem banco ou configuração por unidade (FR-075), com menor
  privilégio (FR-031, FR-036) e sem acesso irrestrito por base central.
- **XV — Identidade substituível**: regra independente da identificação (FR-001,
  FR-002), sem nenhum mecanismo de autenticação (FR-003).
- **XVI — Privacidade (NON-NEGOTIABLE)**: só o identificador do operador é gravado
  (FR-009); recusas sem detalhes internos (FR-044); verificação antes de qualquer
  conteúdo (FR-037); sem leitura de dado de egresso.
- **XXII — YAGNI**: uma entidade (FR-025), duas atuações (FR-010), três capacidades
  (FR-028), sem motor genérico (FR-034), sem tela de gestão (FR-063), sem auditoria
  (FR-074), sem nada para Campanha (FR-073).
- **XXIX — Hipóteses não viram requisitos (NON-NEGOTIABLE)**: as interpretações estão
  na categoria B, marcadas [Interpretação Bn]; as decisões não tomadas estão em
  Decisões Pendentes; a publicação não é decidida.
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: elaborar não abre exceção à
  imutabilidade (FR-032).
- **VII — Conceitos distintos (NON-NEGOTIABLE)**: nenhuma alteração em Pesquisa, Versão,
  Campanha ou Participação (FR-027).
- **XXV, XXVI — Testabilidade**: regra testável com operadores fictícios (FR-004) e
  cobertura de todas as rotas (FR-042).
- **XX, XXI — Acessibilidade e responsividade**: FR-077, FR-078.
- **Governança de Permissões (seção)**: competências modeladas explicitamente (FR-028 a
  FR-031); acesso técnico não equivale a poder alterar instrumento ou publicar (FR-047,
  FR-067).
- **I, II, III, XI, XVII — Longitudinalidade, egresso, origem dos dados, identidade da
  Pessoa, consentimento**: não afetados. Esta feature não toca dados de egresso.

**Tensões identificadas (não são conflitos)**:

- **X × registro de vínculo por responsável técnico**: quem opera o ambiente pode
  registrar vínculo para si. Tratamento: o registro não confere competência por si
  (FR-066), declara que apenas reflete designação externa (FR-065), e a autorização e a
  evidência do registro ficam pendentes (DP-1002). Sem identificação produtiva, o
  editor não está exposto em produção (FR-054).
- **XV × editor ainda não produtivo**: a regra de autorização fica pronta, mas o editor
  continua sem uso produtivo até existir identificação produtiva (DP-1001). Isso é
  consequência de manter autenticação fora do escopo, não lacuna da autorização.
- **XXII × situação ativo/inativo**: é um atributo além do mínimo absoluto. Justifica-se
  porque designações terminam e a desativação sem perda da informação é o requisito mais
  simples para refletir isso (US9). Reversível.
- **Menor privilégio × CSAEG consultar publicadas**: é interpretação (B6), não
  competência expressa. Reversível e restrita a conteúdo sem dado pessoal.

Nenhum conflito com a Constituição, com a PAEG ou com as Features 001 a 009 foi
identificado.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence de fato ao domínio de acompanhamento?** Parcialmente. Gestão geral de
   identidade e autenticação **não** pertence (Princípio VI) e fica fora (FR-003).
   Autorização das superfícies do próprio NIAE, conforme a PAEG, pertence: o Princípio X
   e a seção "Governança de Permissões" exigem que competências sejam modeladas
   explicitamente.
2. **É necessária ao ciclo de acompanhamento?** Sim. Sem ela, alterar o instrumento
   depende apenas de acesso ao ambiente.
3. **Existe ou está prevista solução institucional mais adequada?** Para identificação,
   sim, possivelmente (DP-1001), e por isso ela fica fora. Para as competências da PAEG
   dentro do NIAE, não.
4. **Integração seria suficiente?** Para identificação, sim, no futuro. Para decidir o
   que CPAEG e CSAEG fazem no NIAE, não: isso é regra deste domínio.
5. **A incorporação aumentaria desnecessariamente o acoplamento do núcleo?** Não. Uma
   entidade isolada, sem relação com o núcleo longitudinal (FR-027), e uma regra
   independente da identificação (FR-002).

## Out of Scope *(mandatory)*

- Autenticação e identificação produtiva: senha, OTP, Gov.br, SSO, LDAP, provedor de
  identidade, login institucional, recuperação de acesso (DP-1001).
- Contas de egresso, Portal do Egresso, identidade do egresso.
- Publicação de Versão por qualquer superfície (002/DP-001).
- Workflow de elaboração, revisão ou aprovação; estados intermediários; assinatura;
  tramitação; múltiplos aprovadores (002/DP-002).
- Colaboração editorial: coautoria, bloqueio de edição, comentários, revisão por pares,
  atribuição de responsável.
- Auditoria, histórico de ações, autoria de alterações (009/DP-903).
- Tela ou CRUD de governança; gestão de papéis pela interface; autosserviço.
- Papéis para Proex, DIREC, Proen, Reitoria ou Diretorias de unidade (DP-1006).
- Acesso da CSAEG a rascunhos ou proposta de alteração pelo sistema (DP-1004).
- Gestão de Campanha, monitoramento, dashboards, exportações, consulta de Participações e
  Respostas (Feature 011 e seguintes; 004/DP-402).
- Catálogo ou árvore de unidades; organização; tenant; multi-tenancy.
- Permissões configuráveis, RBAC ou ABAC genéricos, ACL por objeto, motor de políticas,
  bibliotecas de autorização genéricas.
- Mandato, eleição, titularidade, suplência, presidência das comissões.
- Registro de portaria, fundamento ou datas de vigência no vínculo (DP-1002).
- Exposição do editor em ambiente produtivo.
- Nova capacidade editorial de qualquer tipo.
- GeN.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: decisões novas usam o prefixo 10 (DP-1001…). As das features anteriores são
citadas como 00n/DP-nnn.

**Novas nesta feature**

- **DP-1001** — DECISÃO PENDENTE: como operadores institucionais serão **identificados
  em ambiente produtivo** (mecanismo institucional de identidade, autenticação e
  correspondência entre a identidade institucional e o identificador de operador).
  - Instância competente: Ifes (DTI, com Proex), conforme solução institucional de
    identidade.
  - Impacto: enquanto pendente, o editor não é exposto em produção (FR-054). A regra de
    autorização não muda quando a decisão vier (FR-002).
  - Tratamento provisório: identificação somente não produtiva, por operador fictício,
    no modo de demonstração (FR-053 a FR-060).
- **DP-1002** — DECISÃO PENDENTE: **quem autoriza o registro** de um vínculo no sistema e
  **com qual evidência** (por exemplo, a portaria de nomeação da CPAEG pelo Reitor ou da
  CSAEG pelo Diretor-Geral — PAEG Art. 17, Art. 24; indicação da CSAEG pela Diretoria
  da unidade — Art. 18, III), e se o vínculo deve guardar essa referência ou datas de
  vigência.
  - Instância competente: Proex/CPAEG, para a CPAEG; Diretorias das unidades, para as
    CSAEGs.
  - Impacto: possível atributo novo no vínculo e possível restrição sobre quem opera o
    mecanismo de registro.
  - Tratamento provisório: registro técnico que declara apenas refletir designação
    externa (FR-065), sem referência nem datas (FR-026).
- **DP-1003** — DECISÃO PENDENTE: **quem atua pela CPAEG no sistema**: somente membros
  nomeados, ou também servidores de apoio e representantes das áreas de ensino, pesquisa
  e extensão com quem a CPAEG elabora o questionário (PAEG Art. 21, VI).
  - Instância competente: CPAEG, com Proex.
  - Impacto: quem recebe vínculo CPAEG; eventual atuação distinta para participação
    conjunta.
  - Tratamento provisório: o sistema não distingue membro de quem atua em nome da
    comissão; recebe vínculo CPAEG quem a instituição indicar (B8, B9).
- **DP-1004** — DECISÃO PENDENTE: se as CSAEGs devem **consultar rascunhos** ou dispor de
  meio, no sistema, para **reportar atualizações necessárias** à CPAEG (PAEG Art. 22, IV).
  - Instância competente: CPAEG.
  - Impacto: possível extensão da capacidade "consultar rascunhos" à CSAEG, ou feature
    própria de reporte.
  - Tratamento provisório: CSAEG consulta somente Versões publicadas (FR-031, B6, B7); o
    reporte ocorre fora do sistema.
- **DP-1005** — DECISÃO PENDENTE: **designação canônica das unidades** (lista oficial de
  campi, campus avançado e Cefor e sua grafia), para que a unidade do vínculo e a unidade
  das Conclusões coincidam de forma verificável.
  - Instância competente: Ifes (fonte acadêmica oficial; ver também a fonte acadêmica
    real da 001).
  - Impacto: nenhuma capacidade depende da unidade nesta feature (FR-017); a primeira
    superfície por unidade (Feature 011) dependerá.
  - Tratamento provisório: mesma designação textual da fonte acadêmica (FR-015), sem
    validação contra catálogo.
- **DP-1006** — DECISÃO PENDENTE: se e como **Proex, DIREC, Proen, Reitoria e Diretorias
  de unidade** terão atuação no sistema (coordenação geral e monitoramento — Art. 14;
  periodicidade — Art. 10, II; gerência na unidade — Art. 18).
  - Instância competente: Proex.
  - Impacto: possíveis atuações novas quando houver superfície que as consuma
    (monitoramento, Campanha).
  - Tratamento provisório: não representadas (FR-012).

**Herdadas e afetadas por esta feature**

- **009/DP-901** — quem pode elaborar e editar rascunhos: **parcialmente resolvida**.
  - **Resolvido** (categoria A): a competência de elaborar o questionário é da CPAEG
    (PAEG Art. 21, VI). A CSAEG aplica o questionário e reporta atualizações à CPAEG
    (Art. 22, IV), o que não inclui elaborá-lo. Esta feature atribui a capacidade
    **elaborar** somente à atuação CPAEG (FR-030, FR-031) [Interpretação B1, B5].
  - **Continua pendente**: quem atua pela CPAEG no sistema (DP-1003); participação das
    áreas de ensino, pesquisa e extensão; acesso de CSAEG a rascunhos (DP-1004);
    identificação produtiva (DP-1001).
  - Correção de citação: o reporte de atualizações está no Art. 22, **IV**, e não no
    Art. 22, III, como registrado na 009.
- **002/DP-001** — quem pode publicar: **continua aberta**.
  - A PAEG não atribui a nenhuma instância a aprovação ou publicação de Versão. A
    elaboração (Art. 21, VI) não implica publicação.
  - A PAEG indica **quem resolve a omissão**: a CPAEG em conjunto com a Pró-reitoria
    competente (Art. 26). Essa indicação já constava da 002 e não decide a questão.
  - Tratamento: publicação indisponível (FR-047 a FR-051).
- **002/DP-002** — fluxo de elaboração e aprovação: **continua aberta**. Nenhum estado,
  etapa ou pedido (FR-049).
- **009/DP-903** — autoria e histórico das alterações: **continua aberta**. A PAEG não
  exige registro de autoria, e nenhuma superfície consome esse registro. Com operadores
  identificados, o registro passa a ser tecnicamente possível, mas não é criado
  (FR-074). Instância competente: CPAEG/Proex.
- **009/DP-902** — estatuto da baseline: **continua aberta**. Agora apenas CPAEG pode
  editá-la, como qualquer rascunho.

**Herdadas e não afetadas**

- **004/DP-402** — quem cria, abre e encerra Campanha: não afetada. Nenhuma regra de
  Campanha é criada (FR-073).
- **004/DP-403** — Campanhas próprias de unidade (CSAEG): não afetada. A atuação CSAEG
  desta feature não confere nenhuma capacidade sobre Campanha.
- **004/DP-406** — acesso e identificação do **egresso**: não afetada e distinta da
  DP-1001, que trata de operadores institucionais.
- **005/DP-505** — quem consulta respostas identificadas e Participações, e em qual
  escopo: **continua aberta**. Nenhuma superfície existente expõe respostas a operador
  institucional, e esta feature não cria nenhuma (FR-033, FR-073). A atuação e a unidade
  do vínculo poderão ser usadas quando essa decisão vier.
- **005/DP-506** — registro de respostas por intermediário (por exemplo, CSAEG em
  contato telefônico): não afetada.
- **007/DP-701** — encaminhamento de ambiguidade operacional a quem configura
  Campanhas: não afetada.
- **002/DP-003** a **002/DP-007**, **003/DP-301** a **003/DP-310**, **006/DP-604**,
  **008/DP-801**: não afetadas.
- Demais decisões de identidade e autenticação do egresso das features 005 a 008:
  não afetadas; operador e egresso continuam separados (FR-008, FR-072).


## Nota de revisão pela Feature 019 (2026-10-04)

A capacidade nomeada pode_validar_formacao admite CPAEG e CSAEG ativos na demonstração. CSAEG atua pela unidade declarada e só vincula Conclusão ou acervo das unidades do vínculo. DP-1901 e DP-1902 preservam a competência de atestar e o acesso real como decisões institucionais pendentes.

Referência: [019 — Formação não localizada e validação posterior](../019-formacao-declarada-validacao/spec.md).
