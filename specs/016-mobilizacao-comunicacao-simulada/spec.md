# Feature Specification: Mobilização e comunicação simulada da pesquisa

**Feature**: `016-mobilizacao-comunicacao-simulada`

**Feature Branch**: `016-mobilizacao-comunicacao-simulada` (sincronizada com a main)

**Created**: 2026-10-03

**Status**: Conceito aprovado; implementação autorizada e validada localmente em 2026-10-03;
sem aprovação institucional de comunicação real. Evidências em [quickstart.md](quickstart.md).

**Input**: Solicitação da Feature 016: preparar, visualizar e simular convite institucional
por e-mail para o público atual de uma Campanha, somente com contatos fictícios e transporte
local; preservar a população dinâmica por Conclusão Acadêmica, comunicar uma vez por Pessoa,
não criar Participação, não resolver acesso real nem antecipar arquitetura de produção.

## Contexto

> Campanha é uma rodada institucional de observação. Campanha NÃO é lista de destinatários.

A 016 consome a população da 004 para demonstrar mobilização. Não define outra população,
não transforma elegibilidade em convite e não assume responsabilidade institucional por
comunicação real. “Preparar” significa conferir público e mensagem fixa; não criar mailing,
rascunho editável ou configuração gravada na Campanha.

*(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)* O público usado na simulação funciona apenas como substituto temporário para
exercitar a comunicação antes da existência de Lote. Ele não modela nem antecipa a
semântica do futuro Lote de mobilização, que será uma seleção operacional própria, e não
define exclusividade de participação: qualquer egresso cuja formação esteja na abrangência
da Campanha pode responder, contatado ou não. Os critérios da Campanha expressam a abrangência do instrumento e não devem ser
usados para recortar a divulgação.

### Base existente e evidências

Inspeção da `main`, revisão `0c911b5` (PR #24, Feature 015 mergeada), em 2026-10-03. Referências de especificação:
[Constituição](../../.specify/memory/constitution.md),
[001](../001-nucleo-academico-fonte-simulada/spec.md),
[004](../004-campanhas-populacao-elegivel/spec.md),
[005](../005-participacao-respostas-rascunho/spec.md),
[006](../006-jornada-conclusao-participacao/spec.md),
[007](../007-contextualizacao-formacao-entrada/spec.md),
[008](../008-interface-navegavel-pesquisa/spec.md),
[010](../010-governanca-papeis-escopos/spec.md),
[011](../011-acompanhamento-operacional-coleta/spec.md) e
[014](../014-polish-jornada-egresso/spec.md) e
[015](../015-identidade-visual-jornada/spec.md).

| Fato atual | Evidência no código | Consequência |
| --- | --- | --- |
| Pessoa tem identidade interna, fonte, identificador externo e nome opcional; não tem e-mail | `trajetoria/academico/models.py`, `Pessoa` | Nenhum campo de contato será acrescentado; nome não deduplica |
| Conclusão pertence a uma Pessoa; unidade pertence à Conclusão | `trajetoria/academico/models.py`, `ConclusaoAcademica` | Aplicar escopo às Conclusões antes de obter Pessoas distintas |
| População é consulta sobre Conclusões incorporadas, com seis critérios; ausências não satisfazem critérios definidos | `trajetoria/campanha/consultas.py`, `populacao_no_momento`, `avaliar` | Consumir a 004 sem copiar sua regra; nenhum congelamento |
| Elegibilidade independe do estado temporal; EM COLETA controla admissão | `trajetoria/campanha/consultas.py`, `estado`, `admite_participacao` | Distinguir consulta de público de disponibilidade da simulação |
| Participação tem unicidade Campanha × Conclusão e conclusão por `concluida_em` | `trajetoria/participacao/models.py`, `operacoes.py` | Comunicação não modifica nem substitui Participação |
| Consultar entrada não grava; `entrar` inicia ou retoma pela 005 | `trajetoria/participacao/entrada.py` | Link neutro não chama a entrada nem escolhe formação |
| Vínculos ativos CPAEG/CSAEG decidem capacidade; CPAEG institucional, CSAEG união de unidades | `trajetoria/governanca/{models,consultas,regras}.py` | Reutilizar vínculos; não criar papéis nem permissões configuráveis |
| Campanhas visíveis e universo de unidade já estão definidos na 011 | `trajetoria/acompanhamento/{acesso,consultas,views}.py` | Mesma visibilidade e escopo, verificados no servidor |
| Detalhe da Campanha já fornece contexto e navegação administrativa | `trajetoria/acompanhamento/templates/acompanhamento/campanha.html` | Ação Comunicação pertence ao detalhe, sem dashboard separado |
| Pessoas e operadores são escolhidos por adaptadores fictícios separados | `trajetoria/demonstracao/{entrada,operador,views}.py` | Cookie de Pessoa não concede acesso institucional; não é autenticação |
| Modo desligado bloqueia todas as páginas; não há auth/admin/sessions nem configuração explícita de e-mail | `config/{settings,urls}.py`, `demonstracao/middleware.py`, `.env.example` | Não depender dos padrões de e-mail do framework; exigir transporte seguro explícito |
| Preparo explícito usa operações existentes e recusa bases com outra fonte ou vínculos não fictícios | `trajetoria/demonstracao/cenario.py`, comando `preparar_demonstracao` | Reutilizar o preparo; contatos fictícios ficam fora dos modelos acadêmicos |
| Operador B é CSAEG Vitória; a Campanha visível Serra/Vitória está em preparação, e as duas abertas não incluem Vitória | `trajetoria/demonstracao/cenario.py`, `CAMPANHAS`, `VINCULOS` | Usar essa Campanha EM PREPARAÇÃO para verificação pré-operacional, preservando a jornada |

**015 é a baseline atual.** Foundations e contratos de shell aprovados são preservados.
O acompanhamento mantém sua base administrativa e estilos compartilhados; o shell da
jornada não é propagado para ele. Configuração e cenário de demonstração permanecem
os existentes. Não se reabrem decisões da 015.

### Escolhas pequenas e limites de governança

A 010 não concede comunicação: suas capacidades iniciais eram editoriais. A 011 acrescentou
acompanhamento como ação concreta e interpretação operacional da PAEG. A 016 acrescenta
**preparar e simular comunicação**, exclusivamente fictícia, com o mesmo desenho de escopo.
Não toma a capacidade de acompanhar como autorização implícita de envio.

- CPAEG: preparar, consultar público, ver prévia e simular no âmbito institucional.
- CSAEG: as mesmas ações, somente sobre Conclusões de suas unidades ativas e Campanhas
  visíveis segundo a 011. Várias unidades somam escopo; não somam poder institucional.
- CPAEG + CSAEG: âmbito institucional enquanto houver CPAEG ativo; desativado, restam as
  unidades CSAEG na requisição seguinte.
- Sem vínculo ativo: nenhuma dessas ações. Privilégio técnico e modo ligado não autorizam.

Esta escolha é **interpretação operacional reversível para demonstração**: a fundamentação
já analisada na 010/011 é planejamento e execução institucional (Art. 21, I e III) e
aplicação nas unidades (Art. 22, I e IV). Esses dispositivos não determinam quem autoriza
um disparo real, seu conteúdo, base legal ou canal. Isso permanece em 004/DP-407 e DP-1602.
Não há conclusão nova sobre legislação vigente nem aprovação de competência produtiva.

A alternativa CPAEG exclusiva reduziria a demonstração da atuação por unidade, mesmo
havendo um recorte já definido e aplicável sem atribuir unidade à Pessoa. A alternativa
CSAEG com público institucional violaria o escopo da 010/011. Adota-se a simulação por
unidade porque usa a fronteira existente e permite verificar esse limite concretamente.
A leitura de nome/contato fictício fica restrita à nova prévia; a 011 continua agregada,
sem lista de Pessoas ou acesso a Participações e Respostas identificadas.

### Regras definitivas desta versão

| Questão | Decisão da 016 |
| --- | --- |
| Qual Campanha? | Público e prévia de qualquer Campanha visível, em qualquer estado; simulação local em EM PREPARAÇÃO e EM COLETA; ENCERRADA somente consulta/prévia [Solicitante] |
| Quem compõe o público? | Pessoas de demonstração com ao menos uma Conclusão atualmente elegível no escopo; nenhuma filtragem por Participação |
| Múltiplas formações? | Uma mensagem por identidade interna de Pessoa e por execução; nenhuma escolha de curso |
| Conteúdo? | Um convite institucional fixo, não editável, parametrizado apenas por nome opcional, nome da Campanha e URL neutra |
| Sem contato? | Pessoa contada como sem contato, nenhuma mensagem; nenhuma exclusão da população da Campanha |
| Simulado? | Mensagens efetivamente submetidas a uma caixa SMTP local isolada; nunca entrega ao egresso |
| Persistência? | Nenhuma nova no Trajetória; caixa local guarda mensagens para inspeção, sem histórico de domínio |
| Link? | Mesma URL local `/demonstracao/` para todos, sem identidade, formação ou Campanha |
| Repetir? | Nova simulação pode gerar novamente as mensagens; limite por execução, sem deduplicação histórica |

Estado de Participação não é necessário ao convite institucional inicial. Separar “sem
Participação”, “em andamento” e “todas concluídas” só seria necessário para selecionar
lembretes ou evitar contatos futuros. A 016 não consulta esses estados para comunicação,
não exclui quem concluiu e não classifica recusa como opt-out. Essa necessidade é DP-1605.
Pessoas distintas não são fundidas por nome nem por endereço; cada mensagem tem um único
destinatário. A demonstração deve atribuir contatos diferentes às Pessoas de seu cenário.

## User Scenarios & Testing *(mandatory)*

Todos os atores, contatos e dados são fictícios. As prioridades ordenam a entrega; as
quatro histórias são obrigatórias para fechar a feature. Cada história tem verificação
própria, com as fronteiras de que precisa disponíveis no ambiente de teste.

### User Story 1 - Conferir o público atual da Campanha (Priority: P1)

Como operador autorizado, abro Comunicação no detalhe da Campanha e vejo quantas
Conclusões são elegíveis agora, quantas Pessoas correspondem a elas, quantas têm contato,
quantas não têm e quantas mensagens seriam produzidas, no meu escopo.

**Why this priority**: comprova a população correta sem congelá-la nem confundi-la com
quantidade de pessoas ou de mensagens.

**Independent Test**: consultar uma Campanha sobre quatro Conclusões: três de A e uma de
B. A possui contato e B não; conferir 4 Conclusões, 2 Pessoas, 1 com contato, 1 sem e 1
mensagem prevista, sem gravação.

**Acceptance Scenarios**:

1. **Given** esse conjunto, **When** CPAEG consulta o público, **Then** aparecem os cinco
   números acima, escopo institucional e momento da consulta.
2. **Given** A com uma Conclusão na Serra e duas no Cefor e B somente no Cefor, **When**
   CSAEG Serra consulta, **Then** vê 1 Conclusão, 1 Pessoa, 1 contato, 0 sem e 1 mensagem;
   nenhum atributo ou total do Cefor é apresentado.
3. **Given** três Conclusões da mesma Pessoa, uma inelegível, **When** consulta, **Then**
   conta apenas as duas elegíveis e uma Pessoa.
4. **Given** novas Conclusões incorporadas após a consulta, **When** consulta novamente,
   **Then** os números refletem a população atual; a Campanha permanece igual.
5. **Given** zero elegíveis ou nenhum contato, **When** consulta, **Then** vê zeros
   coerentes e explicação, sem erro nem destinatário fabricado.

### User Story 2 - Conferir o convite antes da simulação (Priority: P1)

Como operador autorizado, vejo a mensagem fixa com destinatário fictício representativo,
remetente, assunto, texto, HTML, chamada para ação e URL local, sem precisar editar conteúdo.

**Why this priority**: torna a ação reviewável e comprova exatamente o conteúdo produzido.

**Independent Test**: renderizar a prévia de uma Pessoa com contato no escopo e comparar
assunto, texto e HTML com a mensagem gerada para ela na simulação, com os mesmos dados.

**Acceptance Scenarios**:

1. **Given** uma Pessoa com contato no público, **When** abro a prévia, **Then** vejo
   destinatário `.invalid`, assunto com nome da Campanha, saudação e ambas as versões.
2. **Given** Pessoa sem nome, **When** a mensagem é renderizada, **Then** a saudação é
   “Olá!”; com nome informado, “Olá, {nome}!”, escapado no HTML, sem inferência de gênero.
3. **Given** Pessoa com várias formações, **When** vejo a prévia, **Then** não há curso,
   unidade de formação ou escolha de formação; o destino é a entrada neutra local.
4. **Given** nenhum contato disponível, **When** abro a prévia, **Then** não existe
   destinatário representativo; vejo o modelo genérico com saudação “Olá!”, explicitamente
   sem destinatário e sem incluir uma Pessoa fora do público.
5. **Given** uma Campanha em preparação ou encerrada, **When** abro a prévia, **Then**
   ela é identificada como prévia e não submete mensagem; preparação permite simulação
   explícita pré-operacional, encerrada informa que nova simulação está indisponível.

### User Story 3 - Simular o convite e compreender o resultado (Priority: P1)

Como operador autorizado, aciono “Simular envio”. O sistema reavalia público e escopo,
resolve contatos e submete no máximo uma mensagem por Pessoa ao transporte local. Vejo
contagens e falhas compreensíveis, sem afirmação de entrega ao egresso.

**Why this priority**: demonstra a mobilização completa mantendo as garantias de domínio.

**Independent Test**: simular com o backend de memória; conferir destinatários, conteúdo,
contagens e invariância do banco. Exercitar falha técnica controlada separadamente.

**Acceptance Scenarios**:

1. **Given** A com três Conclusões elegíveis e contato e B com uma sem contato, **When**
   simulo, **Then** há uma mensagem para A e nenhuma para B; 2 Pessoas, 1 com contato,
   1 sem, 1 submetida, 1 aceita pelo transporte local e 0 falhas.
2. **Given** uma prévia anterior e posterior incorporação de C elegível com contato,
   **When** simulo, **Then** C entra na execução; não é usada a lista anterior da prévia.
3. **Given** falha de transporte em uma de duas mensagens, **When** a execução termina,
   **Then** apresenta 2 submetidas, 1 aceita e 1 falha de transporte; não anuncia sucesso
   total, não repete automaticamente e conserva o domínio.
4. **Given** simulação concluída, **When** aciono outra simulação explícita, **Then**
   pode haver nova mensagem para cada Pessoa alcançável; Campanha, Participações e
   Respostas permanecem idênticas e nenhum histórico de envio surge no Trajetória.
5. **Given** Campanha encerrada entre prévia e ação, **When** simulo, **Then** a ação é
   recusada com estado atual, zero submissões e nenhuma abertura ou prorrogação.
6. **Given** zero contatos, **When** simulo em Campanha EM PREPARAÇÃO ou EM COLETA e ambiente seguro,
   **Then** informa zero mensagens submetidas, sem abrir conexão de transporte.

### User Story 4 - Inspecionar a caixa local com isolamento e governança (Priority: P2)

Como responsável pela demonstração, executo o roteiro local, inspeciono o convite na
caixa SMTP e sigo o link. Como operador CSAEG, verifico que URL direta não amplia escopo.

**Why this priority**: valida o transporte real local e os limites de acesso e identidade
sem tornar a caixa local uma dependência dos testes automatizados.

**Independent Test**: executar o roteiro manual de caixa local e os casos automatizados
negativos de configuração, autorização e URL direta.

**Acceptance Scenarios**:

1. **Given** ambiente local seguro, **When** simulo e abro Mailpit, **Then** vejo assunto,
   remetente fictício, destinatário fictício, texto, HTML e link correspondentes à prévia.
2. **Given** navegador sem Pessoa escolhida, **When** clico no link, **Then** chego à escolha
   de Pessoa fictícia; nenhuma Pessoa é identificada pelo endereço e nada é criado.
3. **Given** navegador com Pessoa fictícia já escolhida, **When** clico, **Then** continuo
   na entrada de demonstração; o link não escolhe nem troca Pessoa e não inicia pesquisa.
4. **Given** CSAEG Serra e Campanha restrita ao Cefor, **When** acesso diretamente público,
   prévia ou submissão, **Then** há recusa sem nome, conteúdo ou números da Campanha e
   zero mensagens; com vínculo inativo também há recusa.
5. **Given** configuração de transporte externo, credencial real, contato fora de
   `.invalid` ou modo desligado, **When** tento simular, **Then** há bloqueio explícito
   antes de qualquer conexão ou submissão, inclusive por chamada direta da operação.

### Edge Cases

- Pessoa com formações em várias unidades: limitar Conclusões ao escopo antes de
  deduplicar; incluir Pessoa uma vez se ao menos uma Conclusão elegível estiver no escopo.
- Conclusão sem unidade: visível no âmbito CPAEG se elegível; fora do universo CSAEG.
- Vários vínculos CSAEG: união exata de unidades, sem contar Pessoa duas vezes.
- Grafia diferente de unidade: mesma igualdade exata da 010/011; nenhum alias inferido.
- Contato ausente: ausência normal. Contato malformado, externo ou fonte não permitida:
  erro de segurança/configuração, bloqueio integral; não disfarçar como “sem contato”.
- Falha na resolução de contatos: não tratar como ausência; interromper antes do
  transporte e informar falha de preparação, sem simulação parcial.
- Falha depois de submissão parcial: SMTP não é transação de banco; mensagens já aceitas
  ficam na caixa. Não prometer rollback, entrega ou ausência na caixa quando houve erro.
- Aceite SMTP sem retorno confirmável por erro: registrar como falha de transporte e
  avisar que a caixa local pode conter a mensagem; nunca repetir automaticamente.
- Atualização entre consulta e ação: recalcular, mostrar momento e números da execução;
  a prévia anterior não reserva público, identidade, contato nem autorização.
- Duas ações explícitas simultâneas: duas execuções independentes, cada uma com limite de
  uma mensagem por Pessoa; não inventar garantia de envio único entre requisições.
- Campanhas sobrepostas: cada execução refere-se à Campanha aberta pelo operador; o link
  não desempata as Campanhas da jornada nem supera 004/DP-404 ou 007/DP-701.

## Requirements *(mandatory)*

Origem: **[Solicitante]** pedido explícito; **[004/010/011]** contratos existentes;
**[Arquitetura]** fronteira ou preservação; **[Hipótese]** produto reversível;
**[Interpretação]** aplicação limitada à demonstração, sem competência de envio real.
Nenhuma mudança do instrumento ou regra institucional é presumida.

### Functional Requirements

#### Contexto e autorização

- **FR-001**: A comunicação DEVE existir somente no modo local de demonstração
  explicitamente ativado, desligado por padrão; modo desligado torna suas páginas
  inexistentes e bloqueia a operação de simulação. [Solicitante; 008]
- **FR-002**: Toda rota de público, prévia, ação e resultado DEVE verificar no servidor a
  identificação fictícia do operador e seus vínculos ativos, antes de expor dados ou
  submeter mensagens. Sem operador, encaminhar à escolha existente; sem vínculo,
  recusar. Cookie de Pessoa e privilégio técnico não concedem capacidade. [010]
- **FR-003**: A capacidade fixa de preparar e simular DEVE ser concedida somente a CPAEG
  e CSAEG ativos, no desenho limitado de demonstração descrito no Contexto. NÃO DEVE
  conceder gestão de Campanha, edição/publicação de instrumento, consulta de respostas
  identificadas ou envio real. [Interpretação; 004/DP-402; 004/DP-407]
- **FR-004**: Visibilidade de Campanha e universo de Conclusões DEVEM seguir a 011:
  CPAEG vê todas; CSAEG vê Campanha sem critério de unidades ou com interseção de suas
  unidades, contando somente Conclusões dessas unidades. Unidade ausente não pertence
  a CSAEG; comparação textual é exata. [010/011]
- **FR-005**: Vínculos DEVEM ser relidos em cada requisição, inclusive na ação; múltiplas
  CSAEG somam unidades e CPAEG ativo concede âmbito institucional. Revogação DEVE surtir
  efeito na próxima requisição. [010]
- **FR-006**: Campanha fora do escopo DEVE produzir recusa sem conteúdo da Campanha nem
  contagens; URL direta NÃO DEVE contornar autorização. Campanha inexistente, depois de
  autorização de capacidade, DEVE produzir página inexistente. [011]
- **FR-007**: Público e prévia DEVEM estar disponíveis em EM PREPARAÇÃO, EM COLETA e
  ENCERRADA. Simulação local DEVE ser permitida em EM PREPARAÇÃO e EM COLETA; ENCERRADA
  DEVE recusar nova simulação. Reavaliar o estado da 004 na ação, sem abrir coleta
  para testar Mailpit e sem antecipar regra de envio real. [Solicitante]

#### Público atual e fronteira de contato

- **FR-008**: A população DEVE vir da consulta de população no momento da 004 sobre
  Conclusões incorporadas, refinada pelo escopo. NÃO DEVE reimplementar elegibilidade,
  consultar fonte acadêmica real nem congelar a população. [004; Arquitetura]
- **FR-009**: As Pessoas do público DEVEM ser as identidades internas distintas
  relacionadas às Conclusões de FR-008, DEPOIS do recorte autorizado. Ordem obrigatória:
  Conclusões elegíveis da Campanha → restrição pelo escopo institucional do operador
  → Pessoas distintas → resolução de contato fictício → mensagens. Uma ou várias
  Conclusões da mesma Pessoa DEVEM
  produzir no máximo uma mensagem por execução. Nome, contato e curso não deduplicam
  nem reconciliam Pessoas. [Solicitante; 001]
- **FR-010**: A interface DEVE mostrar momento da consulta, escopo, Conclusões elegíveis
  atuais, Pessoas distintas, Pessoas com contato fictício, sem contato e mensagens
  previstas. Com contatos válidos: Pessoas = com + sem; previstas = com contato.
  São contagens atuais, não denominador histórico nem taxa de mobilização. [Solicitante]
- **FR-011**: A fronteira substituível de contato DEVE receber uma Pessoa e devolver
  zero ou um endereço utilizável, distinguindo ausência normal de falha técnica ou
  contato inválido. A aplicação NÃO DEVE conhecer como o adaptador obtém o contato.
  NÃO DEVE adicionar e-mail a Pessoa ou Conclusão. [Solicitante; Const. V, XVI]
- **FR-012**: Só o adaptador de demonstração DEVE fornecer contatos nesta feature,
  determinísticos e explicitamente fictícios, exclusivamente no domínio reservado
  `example.invalid`. A associação usa referências estáveis dos dados fictícios, nunca
  inferência a partir do nome nem cadastro vindo do navegador. Pessoa não mapeada tem
  contato ausente. Consulta, prévia e ação DEVEM recusar base com Pessoas ou Conclusões
  de origem diferente da fonte simulada, sem mostrar dados nem reduzir silenciosamente
  a população da 004. Origem real é DP-1601. [Solicitante; Arquitetura]
- **FR-013**: Pessoa sem contato DEVE permanecer nas contagens de Pessoas elegíveis,
  com zero mensagens para ela; ausência NÃO DEVE alterar sua elegibilidade ou acesso
  espontâneo. [Solicitante; 004]
- **FR-014**: O convite inicial NÃO DEVE filtrar, distinguir ou personalizar por estado
  de Participação ou Resposta, inclusive Q1; o público abrange quem não começou, está
  em andamento ou concluiu. Lembretes ficam em DP-1605. [Escopo; 006]

#### Mensagem e prévia

- **FR-015**: DEVE existir somente um MODELO INSTITUCIONAL NÃO EDITÁVEL de convite, sem campos
  de edição. Assunto DEVE identificar o convite e o nome da Campanha; conteúdo DEVE
  convidar à pesquisa, explicar a natureza fictícia/local, oferecer CTA “Abrir a
  demonstração” e assinatura “Trajetória Ifes — demonstração institucional”. NÃO DEVE
  prometer periodicidade, finalidade jurídica aprovada, entrega ou autenticação. Texto
  definitivo é revisão editorial, sob 008/DP-801. [Hipótese; Solicitação]
- **FR-016**: Personalização DEVE limitar-se ao nome informado da Pessoa e nome da
  Campanha e URL neutra da entrada de demonstração. Não criar editor de assunto ou corpo.
  Saudação com nome: “Olá, {nome}!”; sem nome: “Olá!”. NÃO DEVE citar curso,
  escolher formação, inferir gênero ou incluir dados de Resposta. [Solicitante]
- **FR-017**: Toda mensagem DEVE conter versão texto e alternativa HTML equivalentes
  em sentido, com CTA e URL também na versão texto; remetente DEVE ter nome institucional
  de demonstração e endereço fictício `trajetoria@example.invalid`. Cada mensagem DEVE
  ter exatamente um destinatário fictício, sem CC/BCC ou anexos. Destinatário usa endereço
  simples sem display name; remetente admite somente o nome institucional fixo e o
  mailbox fixo, validados separadamente antes da composição de From. [Solicitante]
- **FR-018**: HTML DEVE ser simples, em português, responsivo, com ordem de leitura
  coerente, contraste WCAG 2.1 AA e link textual descritivo utilizável sem imagens.
  Conteúdo dinâmico DEVE ser escapado. NÃO DEVE carregar fontes, imagens, scripts,
  estilos ou rastreadores externos; imagens, se houver, exigem texto alternativo.
  Não é necessário logotipo nem reproduzir o portal institucional. [Const. XX, XXI, XVI]
- **FR-019**: A prévia DEVE mostrar remetente, destinatário representativo do público
  com contato, assunto, texto, HTML, CTA e URL. Escolha DEVE ser determinística, sem
  significado de preferência. Sem contato, mostrar modelo genérico sem destinatário e
  informar a ausência. Não oferecer lista individual de elegíveis. [Solicitante; Hipótese]
- **FR-020**: Prévia e mensagem submetida DEVEM usar o mesmo renderer. Para os mesmos
  dados e parâmetros, assunto, texto, HTML, remetente e destino DEVEM coincidir.
  A prévia NÃO DEVE executar transporte ou persistir configuração. [Solicitante]
- **FR-021**: O destino DEVE ser a URL absoluta local da entrada existente
  `/demonstracao/`, igual para todos, sem query ou fragmento de identidade, token,
  Pessoa, Conclusão, Participação ou Campanha. DEVE ser configuração neutra substituível,
  validada como local; NÃO DEVE ser construído confiando no host enviado pelo cliente.
  [Solicitante; 004/DP-406; Arquitetura]
    *(Revisado pela 018)* A URL neutra local passa a apontar para `/acesso/`, sem identidade ou
  preenchimento (018 FR-053).

- **FR-022**: Abrir a mensagem ou seguir seu link NÃO DEVE autenticar, identificar,
  autorizar, selecionar Pessoa/formação/Campanha, iniciar/retomar Participação ou criar
  Resposta. Escolha fictícia e ação explícita da 007/005 continuam separadas. [004–008]

#### Ação e resultado operacional

- **FR-023**: “Simular envio” DEVE ser ação explícita POST com proteção CSRF, disponível
  junto ao público e à prévia antes de acionada. GET, abrir prévia ou visitar páginas
  NÃO DEVE submeter mensagem. Métodos inadequados DEVEM ser recusados. [008; Solicitação]
- **FR-024**: A ação DEVE revalidar capacidade, visibilidade, estado, segurança, população
  atual e contatos no seu próprio momento; NÃO DEVE aceitar lista, contagem, conteúdo,
  destinatário, remetente ou URL enviados pelo cliente como decisão de execução.
  [Solicitante; 010/011]
- **FR-025**: Com preparação segura e válida, a ação DEVE gerar uma mensagem por Pessoa
  com contato, usando o renderer comum, e submetê-la ao backend de e-mail do Django.
  Desenvolvimento/demonstração: SMTP local para Mailpit; testes: `locmem` e
  `mail.outbox`. NÃO DEVE haver API HTTP do Mailpit nem consulta à caixa para obter
  estado ou resultado de domínio. [Solicitante; Arquitetura]
- **FR-026**: O resultado DEVE mostrar momento, escopo, Pessoas elegíveis distintas,
  com contato, sem contato, mensagens submetidas ao transporte, aceitas pelo transporte
  local e falhas de transporte. “Submetidas” conta tentativas efetivamente encaminhadas
  ao backend; “aceitas” conta retorno positivo do backend, sem consulta à caixa;
  “falhas” conta retorno sem aceite ou exceção. Em execução completa, submetidas =
  aceitas + falhas = com contato. NÃO DEVE usar “entregue”, “recebido”, “aberto” ou
  “lido” como estado ou garantia. Resultado interno contém apenas PK/situação por Pessoa
  e agregados; a view entrega ao template somente instante, escopo e totais/categorias,
  sem coleção individual, nomes, contatos ou exceção bruta. Nada é persistido. [Solicitante]
- **FR-027**: Cada mensagem DEVE ter no máximo uma tentativa por execução. Falha técnica
  DEVE ser apresentada como “falha de transporte”; as demais mensagens podem ser
  tentadas uma vez, e o resultado DEVE refletir os retornos conhecidos, sem sucesso
  total fictício. NÃO DEVE haver retry automático, fila ou promessa de rollback SMTP.
  Resultado incerto DEVE avisar que a caixa pode conter a mensagem. [Hipótese]
- **FR-028**: Falha de preparação/segurança DEVE bloquear toda submissão antes de conectar,
  informar a categoria do problema e zero tentativas; ausência de contato NÃO é falha.
  Zero contatos válidos DEVE resultar em zero tentativas sem conexão. [Solicitante]
- **FR-029**: Repetir explicitamente a ação DEVE recalcular o público e pode gerar novas
  mensagens, com o mesmo limite por Pessoa em cada execução. A interface DEVE avisar
  dessa repetição; recarregar o resultado NÃO DEVE reenviar automaticamente.
  Resultado NÃO DEVE exigir histórico em banco, sessão, cache ou cookie; pode ser a
  resposta da própria ação, com aviso para não confirmar reenvio do POST. [Hipótese]

#### Isolamento do transporte e preservação

- **FR-030**: A operação DEVE bloquear configurações não permitidas antes de qualquer
  conexão: modo desligado, backend não autorizado, host SMTP fora de loopback, porta
  fora da configuração local aprovada, credenciais SMTP não vazias, remetente ou
  destinatário fora de `example.invalid`, URL não local ou adaptador de contato real.
  SMTP local é permitido apenas na demonstração; `locmem` apenas nos testes. Padrões
  implícitos de SMTP NÃO DEVEM habilitar simulação. A própria operação DEVE rejeitar
  todo destinatário cujo domínio não seja exatamente `example.invalid`, antes de qualquer
  mensagem, independentemente de EMAIL_HOST/Mailpit ou de configuração SMTP incorreta.
  Destinatário e transporte são barreiras independentes de defesa em profundidade,
  específicas da demonstração 016; não definem política de produção futura. [Solicitante]
- **FR-031**: Configuração e roteiro DEVEM manter Mailpit e aplicação em ambiente local,
  sem credenciais reais, sem relay, encaminhamento, liberação de mensagens para SMTP
  externo ou recursos externos no conteúdo. A caixa DEVE aceitar/capturar SMTP e permitir
  inspeção local somente; domínio reservado sozinho NÃO é defesa suficiente. NÃO DEVE
  existir modo de produção, fallback externo ou configuração produtiva nesta feature.
  [Solicitante]
- **FR-032**: Nenhuma ação da comunicação DEVE criar ou alterar Pessoa, Conclusão,
  Campanha, Pesquisa, Versão, Participação ou Resposta. NÃO DEVE exigir convite para
  participar, materializar membros/elegíveis, selecionar formação ou alterar período,
  estado e critérios. [004–007; Solicitação]
- **FR-033**: NÃO DEVE existir modelo, tabela, coluna ou migração nova; NÃO DEVEM ser
  persistidos público, destinatários, convites, mensagens, execuções, números, prévia,
  texto editável, histórico ou auditoria simulada no Trajetória. O resultado é transitório;
  mensagens guardadas na caixa local são artefatos de infraestrutura de demonstração,
  nunca fonte de estado da Campanha. [Solicitante; Const. IV, XXII]
- **FR-034**: A solução DEVE limitar-se à fronteira mínima de contato fictício, um
  renderer institucional e o backend de e-mail existente no Django; NÃO DEVE criar
  NotificationService, EventBus, provider registry, canais/plugins/strategies genéricos,
  engine de automação, motor próprio de templates ou arquitetura antecipada de produção.
  `EmailMultiAlternatives` é uma opção técnica suficiente a avaliar no plan, não uma
  nova entidade de domínio. [Solicitante; Const. XXII]

#### Interface e verificabilidade

- **FR-035**: A navegação DEVE partir do detalhe de Campanha no acompanhamento existente:
  Campanha → Comunicação → público/prévia → ação explícita → resultado. DEVE manter
  caminho de volta, contexto de atuação e aviso permanente de demonstração sem envio
  real, sem redesenhar editor, acompanhamento ou jornada e sem dashboard independente.
  [Solicitante; 010/011]
- **FR-036**: Telas DEVEM funcionar sem JavaScript, ser operáveis por teclado, com foco
  visível, rótulos e títulos coerentes, mensagens sem depender só de cor, utilizáveis
  de 320 px até desktop e com texto ampliado a 200%. Usar o shell administrativo atual;
  preservar as foundations e os limites de shell da baseline 015. [008/014/015; Const. XX, XXI]
- **FR-037**: A suíte DEVE usar `locmem`, nunca Mailpit, cobrir histórias, matriz mínima
  abaixo e todas as rotas de comunicação para autorização/escopo. Logs e erros NÃO DEVEM
  expor nomes, endereços, conteúdo das mensagens, respostas, credenciais ou tracebacks
  ao operador; não adicionar tracking ou analytics. [Solicitante; Const. XVI, XXVI]
- **FR-038**: A documentação posterior DEVE oferecer roteiro inteiramente fictício:
  iniciar PostgreSQL e Mailpit local sem relay; configurar Django SMTP local; preparar
  dados/contatos e operador; consultar Campanha EM PREPARAÇÃO ou EM COLETA; público; prévia;
  simulação; caixa; conferir assunto/remetente/texto/HTML/destinatários/links; seguir
  link neutro e verificar que não autentica nem inicia. Não usa conta real nem API da
  caixa. O cenário DEVE preservar A, B (CSAEG Vitória) e C e seus vínculos existentes,
  conforme a decisão da 011, e tornar exercitável a simulação no escopo de B sem
  modificar os cenários da jornada ou exigir abertura da coleta. O quickstart do plan
  deve usar Serra e Vitória em preparação. A implementação foi autorizada posteriormente
  pelo solicitante em 2026-10-03; isso não autoriza envio real ou uso produtivo.
  [Solicitante]

### Matriz mínima de verificação automatizada

| Caso | Evidência esperada | Requisitos |
| --- | --- | --- |
| Uma Pessoa com uma Conclusão | Uma mensagem e números exatos | FR-008–010, FR-025–026 |
| Uma Pessoa com três Conclusões elegíveis | Uma mensagem; três Conclusões e uma Pessoa | FR-009 |
| Elegíveis e inelegíveis da mesma Pessoa | Só elegíveis contam, sem multiplicar mensagem | FR-008–009 |
| Pessoa sem contato | Zero mensagem para ela e contagem correta | FR-011–013 |
| Contato fictício conhecido | Destinatário exato e único, sem CC/BCC | FR-012, FR-017 |
| Sem nome, nome com caracteres de HTML | Fallback e escape corretos | FR-016, FR-018 |
| Conteúdo | Assunto, texto, HTML, CTA, remetente e URL neutra; equivalência com prévia | FR-015–022 |
| Sem contato no público | Modelo genérico sem destinatário; nenhuma conexão na ação | FR-019, FR-028 |
| Incorporar elegível entre prévia e ação | Recalcula e inclui nova Pessoa; nenhuma lista anterior usada | FR-024 |
| CPAEG, uma CSAEG, várias CSAEG, vínculo misto | Visibilidade e contagens exatas; deduplicação após escopo | FR-003–005 |
| Sem vínculo, vínculo inativo, só Pessoa escolhida | Recusa antes de dados e transporte | FR-002–006 |
| URL/POST direto fora do escopo | Recusa em todas as rotas; zero vazamento/submissões | FR-006, FR-037 |
| Revogar CPAEG após prévia | Próxima ação usa somente CSAEG remanescente ou recusa | FR-005, FR-024 |
| Preparação, encerramento explícito, fim por data | Consulta/prévia nos três estados; ação em preparação/coleta, recusa em encerrada; Campanha igual | FR-007 |
| GET da ação, POST sem CSRF | Zero mensagens | FR-023 |
| Backend retorna zero, lança exceção ou falha parcial | Contagens coerentes, “falha de transporte”, sem retry | FR-026–028 |
| Repetir ação e abrir link com/sem escolha fictícia | Nenhuma Participação/Resposta criada; nenhum domínio alterado | FR-022, FR-029, FR-032 |
| Snapshot antes/depois das ações | Mesmas linhas, valores, relações e momentos de domínio | FR-032–033 |
| SMTP externo, credencial, backend indevido, URL externa, modo desligado | Bloqueio antes de conectar, zero mensagens | FR-030–031 |
| Contato inválido/externo, mesmo com SMTP incorreto, ou falha do adaptador | Barreira da operação; bloqueio integral antes de conectar; não contabilizar ausência normal | FR-011–012, FR-028 |
| Endereço externo injetado por cliente | Nunca usado; conjunto de destinos continua fictício e calculado | FR-024, FR-030 |
| Inventário de mensagens | Zero destinatários externos e zero links de identidade/tracking | FR-017, FR-021, FR-030 |

Testes de conteúdo e domínio usam o backend de memória; casos de configuração insegura
verificam que nenhuma conexão é aberta, sem depender de SMTP real. A caixa local entra
somente no roteiro manual. A comparação de banco também inclui a relação das Opções das
Respostas: contagem igual sozinha não comprova ausência de alteração.

### Key Entities *(include if feature involves data)*

**Nenhuma entidade persistente nova**, pois não há consumidor de histórico ou de lista
persistida. Campanha permanece inalterada. Pessoa é lida para deduplicação e saudação;
Conclusão é lida para população/escopo; vínculo de governança é lido para autorização.
Participação e Resposta são preservadas, sem leitura para selecionar comunicação.

Conceitos transitórios: público atual, contato resolvido, mensagem renderizada e resultado
operacional. Não possuem identidade de domínio nem relação persistida com Campanha. A
fronteira de contato é um contrato de aplicação, não um catálogo ou vínculo de identidade.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem | Fonte/regra | Divergência/ausência |
| --- | --- | --- | --- |
| Nome da Pessoa | Institucional simulado | Pessoa incorporada pela 001 | Ausente → “Olá!”; não inferir identidade |
| Unidade e elegibilidade | Institucional simulado / derivado | Conclusão × critérios da 004 e escopo 010/011 | Ausência segue 004; unidade ausente fora de CSAEG |
| Nome, período e estado da Campanha | Configuração institucional / derivado | Campanha e estado da 004 | Somente leitura; estado reavaliado na ação |
| Contato | Dado fictício do adaptador de demonstração, não acadêmico nem declaração | Fronteira zero ou um e-mail | Ausente → sem contato; inválido/falha → bloqueio explícito |
| Contagens | Derivado | Público atual no escopo e contatos | Recalculadas; não persistidas |
| Assunto, texto, HTML, CTA, remetente | Conteúdo fixo de demonstração com parâmetros existentes | Mesmo renderer para prévia e ação | Escape e fallback; sem edição livre |
| URL | Configuração local de demonstração | Entrada neutra existente | URL não local bloqueia; sem identidade |
| Resultado de transporte | Retorno operacional transitório | Backend local ou memória de teste | Falha não é entrega nem ausência comprovada na caixa |

Nenhum dado declarado pelo egresso é lido, inferido ou produzido.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos conjuntos de referência, os cinco números do público coincidem
  com contagem manual no escopo; uma Pessoa com três formações produz exatamente uma
  mensagem em cada execução bem-sucedida, e Pessoa sem contato produz zero.
- **SC-002**: Em 100% das mensagens verificadas, destinatário, remetente, assunto, texto,
  HTML, CTA e destino correspondem ao convite definido; prévia e mensagem são idênticas
  para os mesmos parâmetros, inclusive com nome ausente e caracteres especiais.
- **SC-003**: Em 100% das tentativas não autorizadas ou fora do escopo, nenhum dado da
  Campanha/público é revelado e nenhuma mensagem é submetida, inclusive por URL direta,
  revogação de vínculo e envio direto da ação.
- **SC-004**: Em 100% dos casos de configuração insegura previstos na matriz, zero
  conexões de transporte e zero mensagens são produzidas. Em todas as execuções válidas,
  zero destinatários ou recursos de conteúdo externos; a operação rejeita domínio
  diferente de `example.invalid` mesmo com SMTP incorreto.
- **SC-005**: Depois de consulta, prévia, simulação bem-sucedida, falha parcial, repetição
  e clique no link, zero registros de domínio novos ou alterados; nenhuma formação
  escolhida pelo convite e nenhuma identidade concedida por ele.
- **SC-006**: Em 100% das execuções completas, tentativas = aceites + falhas e os números
  correspondem aos retornos observados; falha parcial nunca aparece como sucesso total
  ou entrega, e gera zero novas tentativas automáticas.
- **SC-007**: Uma incorporação elegível entre prévia e ação aparece no público da execução
  em 100% dos testes; preparação/coleta permitem simulação local; encerramento
  nesse intervalo impede 100% das submissões. Consulta/prévia continuam nos três estados.
- **SC-008**: Um roteiro local completo permite inspecionar todas as versões do convite
  e seguir seu link para a entrada neutra, inclusive antes de abrir coleta, usando
  zero contas/endereços reais e sem
  conceder identidade ou criar Participação; documentado e executado manualmente.
- **SC-009**: Público, prévia e ação são utilizáveis sem JavaScript e só por teclado;
  a 320 px e texto a 200%, nenhuma função ou conteúdo é perdido. Verificação manual de
  teclado e medição em navegador; nenhuma mudança visual nas áreas existentes além da
  ligação contextual Comunicação.
- **SC-010**: Ao fechar a feature, zero estruturas persistentes de comunicação, zero
  campos de contato acadêmico, zero histórico de disparo e zero canais além de e-mail.

## Assumptions

- O cenário fictício é pequeno; simulação síncrona é suficiente. Não há meta de escala,
  fila, cache, rate limit ou performance inventada como regra institucional.
- Público/prévia nos três estados e simulação local em preparação/coleta são decisões
  explícitas do solicitante para a 016, sem restringir a elegibilidade da 004 nem definir quando uma
  instituição pode anunciar uma pesquisa real.
- Modelo fixo e prévia representativa determinística bastam para validar mobilização;
  “preparar” não implica edição ou salvamento. Revisão de texto não cria versionador.
- Mailpit local será executado sem relay/encaminhamento e sem publicação na rede externa.
  Sua disponibilidade não é necessária para consultar público, renderizar prévia ou
  executar a suíte; ausência ao simular é falha de transporte.
- Resultado transitório na resposta da ação evita persistir sessão/histórico. O plan
  poderá decidir apresentação equivalente que respeite FR-029/033, sem armazenar uma
  execução só para viabilizar redirecionamento.
- O cenário Serra e Vitória em preparação já permite validar CSAEG sem abrir coleta.
  Contatos ausentes, nome ausente e múltiplas formações são cobertos pela fronteira
  fictícia e testes; preparo explícito/idempotente preserva campanhas e vínculos.

## Relação com outras features

- **001/004**: modelos, incorporação e elegibilidade intactos; contato separado; público
  dinâmico consumido. “Alcançável” significa ter contato fictício utilizável na simulação.
- **005/006/007**: nenhuma participação, resposta, consulta de estado para comunicação,
  seleção ou chamada de entrada; DP-501 e sobreposição continuam abertas.
- **008/014**: entrada neutra de demonstração e jornada preservadas; sem autenticação;
  acessibilidade/linguagem simples aproveitadas sem implementar outro polish.
- **010**: nova capacidade fixa de simulação sobre vínculos existentes, sem expandir
  capacidade editorial, gestão de Campanha ou acesso produtivo.
- **011**: ligação contextual e mesmos limites de visibilidade/escopo; seus indicadores
  continuam por Conclusão e suas páginas continuam agregadas. Público da 016 não é
  indicador de resposta nem drill-down de Participações.
- **015**: baseline atual mergeada no PR #24; preservar foundations, shell e demonstração.
- **012/013**: a 016 não consome dataset ou exportação como mailing e não cria snapshot
  de comunicação. Decisões analíticas não constituem autorização de contato real.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I, VII, VIII**: a cadeia longitudinal não muda; Campanha, Participação e Resposta
  permanecem distintas e intactas; elegibilidade por Conclusão, mensagem por Pessoa.
- **II, III, IV**: população vem das Conclusões reconhecidas e dos critérios existentes;
  contatos são fictícios e não acadêmicos; números derivados não viram dados declarados;
  não há trilha desproporcional ou histórico fabricado.
- **V, VI**: contato substituível e transporte por fronteira técnica existente; domínio
  desconhece Mailpit; demonstração não absorve serviço institucional de comunicação.
- **X, XI, XII**: capacidade e limites de escopo explícitos; unidade da Conclusão precede
  deduplicação; nenhuma unidade permanente da Pessoa; envio real continua pendente.
- **IX, XIV, XV**: nenhuma periodicidade, dependência de convite ou identificação por
  link; acesso espontâneo e escolha de formação continuam nas features existentes.
- **XVI, XVII**: dados exclusivamente fictícios e transporte isolado; Q1 não autoriza
  comunicação, não vira consentimento nem opt-out; decisões legais seguem abertas.
- **XIX, XX, XXI**: números operacionais atuais sem funil/analytics; interface e mensagem
  acessíveis, responsivas, sem dependência de recurso externo.
- **XXII, XXIII, XXV, XXVI, XXVII**: zero migrações/modelos, sem framework de notificação
  ou marketing; testes independentes com memória, segurança e invariância verificáveis.
- **XXIX**: hipóteses de produto identificadas e competências reais preservadas como
  DECISÃO PENDENTE; simulação não transforma lacuna institucional em padrão produtivo.

**Tensões tratadas:** a 011 não lê Pessoa nem expõe dados individuais; a 016 tem consumidor
concreto de identidade/nome/contato fictícios, limitado à composição e prévia protegidas,
sem mudar a 011. A 004 não prevê comunicação no seu escopo original; a 016 acrescenta um
consumidor separado e não uma alteração da Campanha. A simulação repetida pode produzir
mensagens repetidas na caixa; evita-se inventar histórico ou idempotência entre execuções.
Aceite de transporte não é prova de entrega, e falha SMTP não permite rollback garantido.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence de fato ao acompanhamento?** Mobilizar uma rodada tem relação com coleta,
   mas comunicação massiva é capacidade potencialmente externa segundo a Constituição.
   Esta feature demonstra composição local, sem reivindicar domínio de comunicação real.
2. **É necessária ao ciclo?** Não é pré-requisito de participação; é útil para verificar
   operacionalmente alcance e convite associados à Campanha.
3. **Existe solução institucional mais adequada?** Pode existir; 004/DP-407 decide a
   responsabilidade entre Trajetória e serviço externo. Nenhuma escolha é presumida.
4. **Integração seria suficiente?** Sim, para contato e transporte; nesta demonstração,
   contrato mínimo de contato e backend de e-mail atendem ao consumidor concreto.
5. **Aumenta acoplamento desnecessariamente?** Não sob estes limites: Campanha não conhece
   contato/caixa, o domínio não conhece Mailpit e não surge plataforma de comunicação.

## Out of Scope *(mandatory)*

- Envio real; SMTP institucional ou externo; SES, SendGrid, Mailgun, Resend e serviços
  externos; credenciais reais, configuração/provedor/modo de produção.
- WhatsApp, SMS, push, Telegram, redes sociais, mala direta, telefonia e múltiplos canais;
  preferência ou escolha automática de canal.
- Origem/catálogo real de e-mails; sincronização, importação acadêmica real, atualização
  pelo egresso, verificação de e-mail, diretório institucional ou Portal do Egresso.
- Magic link, token secreto/assinado, login, OTP, CPF, matrícula, autenticação,
  identificação por e-mail ou URL individual; resolver DP-406.
- Editor WYSIWYG/Markdown/visual, drag-and-drop, anexos, biblioteca/versionador de
  templates, CSS complexo ou engine própria de mensagens.
- Agendamento, scheduler, Celery, RabbitMQ, fila distribuída, retries automáticos,
  automação, workflow, EventBus, plugins/canais/providers genéricos.
- Histórico de disparo; listas persistidas de elegíveis/destinatários; Convite,
  Mailing, Disparo, Entrega, membros de Campanha, fotografia permanente da população.
- Bounce, complaint, unsubscribe/opt-out implementado, tracking pixel, abertura, leitura,
  clique rastreado, analytics, conversão ou funil; solução definitiva de base legal/LGPD.
- Lembretes, seleção de não respondentes ou segmentação por estado/respostas;
  supor recusa a Q1 como bloqueio de comunicação.
- Gestão de Campanha, publicação de Versão, alteração da pesquisa/jornada,
  Retrato do Egresso, compartilhamento social, exportação de contatos ou dataset mailing.
- Integração HTTP/API de Mailpit, leitura da caixa como estado de domínio.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Decisões institucionais dependem da instância competente, não do desenvolvimento. Todas
seguem abertas; não bloqueiam a demonstração fictícia. Bloqueiam uso real quando indicado.
Numeração nova: DP-1601 em diante.

### Herdadas, explicitamente preservadas

| Referência | DECISÃO PENDENTE | Tratamento da 016 |
| --- | --- | --- |
| **004/DP-406** | Acesso definitivo do egresso e mecanismo de identificação; Proex/DTI e responsáveis pela relação com Portal, a confirmar | URL neutra local sem identidade; bloqueia solução de acesso real |
| **004/DP-407** | Canais de divulgação/comunicação individual e responsabilidade NIAE × serviço externo; Proex/DIREC/comunicação institucional, a identificar | Só simulação de e-mail; não decide responsabilidade produtiva nem canais institucionais |
| **001/DP-009** | Base legal, finalidade e retenção de dados pessoais acadêmicos; encarregado e instâncias institucionais | Só dados fictícios; bloqueia dados reais |
| **005/DP-504**, **002/DP-007** | Base legal, consentimento, retenção de respostas e termo institucional | Nenhuma leitura de respostas/termo ou uso de Q1 para contato; simulação não resolve base legal |
| **005/DP-505** | Consulta de Participações/respostas identificadas | Não concede nem expõe esse acesso |
| **010/DP-1001** | Identificação produtiva de operadores | Operadores fictícios existentes; nenhuma superfície produtiva |
| **010/DP-1002**, **DP-1003**, **DP-1006** | Registro legítimo de vínculos, atuação em nome das comissões e outros órgãos | Nenhum papel, designação ou competência nova de produção |
| **010/DP-1005**, **001/DP-007** | Designações canônicas de unidades e vocabulário acadêmico | Igualdade textual existente, sem normalização |
| **004/DP-402**, **DP-403**, **DP-405** | Gestão/rodadas de unidade, prorrogação e reabertura | Nenhuma operação de gestão exposta |
| **004/DP-404**, **007/DP-701** | Sobreposição e comunicação da ambiguidade | Link não escolhe Campanha nem promete jornada disponível para toda formação |
| **005/DP-501** | Responder várias formações e eventual compartilhamento | Deduplicar e-mail não funde jornadas nem responde decisão metodológica |
| **004/DP-408** | Fotografia da população | 016 não cria fotografia; consumidor de comunicação usa população atual, não dataset histórico |
| **008/DP-801** | Linguagem/identidade institucional definitiva | Texto de demonstração e shell atual; baseline 015 preservada |

### Novas, relacionadas à comunicação futura

| ID | DECISÃO PENDENTE e instância competente | Impacto e tratamento provisório |
| --- | --- | --- |
| **DP-1601** | Origem real dos contatos, qualidade, responsabilidade pela atualização e acesso; Proex/DIREC, DTI, responsáveis pela fonte e encarregado, a confirmar | Define adaptador real futuro; somente mapeamento fictício zero ou um contato na 016; bloqueia contato real |
| **DP-1602** | Governança institucional do envio: quem prepara, aprova conteúdo e autoriza comunicação real institucional/por unidade; CPAEG/Proex com DIREC/CSAEGs/comunicação, a confirmar | Simulação para CPAEG/CSAEG no escopo existente é interpretação local; nenhum workflow ou autorização produtiva; relacionada a DP-407 |
| **DP-1603** | Aplicação de base legal, finalidade, transparência, retenção e minimização à obtenção/uso de contato e mensagem real; encarregado e instâncias institucionais | 001/DP-009 e 005/DP-504 não autorizam automaticamente comunicação; apenas fictícios; bloqueia comunicação real |
| **DP-1604** | SMTP/provedor de produção, infraestrutura, credenciais e responsável pela operação; DTI e instância responsável definida por DP-407 | Nenhuma configuração produtiva; SMTP loopback isolado e memória de teste |
| **DP-1605** | Necessidade e público de lembretes: sem Participação, em andamento, tudo concluído, frequência e efeito de recusa; CPAEG/Proex com CSAEGs/encarregado | Convite institucional inclui todas as Pessoas do público com contato; nenhuma consulta/segmentação por estado e nenhuma periodicidade |
| **DP-1606** | Aplicabilidade institucional de unsubscribe/opt-out, preferência, oposição e efeitos sobre contatos futuros; encarregado/CPAEG/Proex/comunicação | Não implementar nem inferir de Q1; bloqueia definição produtiva desses comportamentos |
| **DP-1607** | Necessidade futura de histórico de disparos, finalidade, granularidade e retenção; responsável por comunicação de DP-407 com encarregado e DTI | Sem consumidor concreto agora; nenhuma entidade de execução/mensagem/destinatário/auditoria |
| **DP-1608** | Necessidade de WhatsApp/outros canais e responsabilidade de integração; instância de DP-407 com comunicação/DTI/encarregado | Só e-mail; não criar arquitetura multicanal |

### Decisões necessárias do solicitante antes do `/speckit-plan`

**Nenhuma pergunta bloqueante identificada para o escopo fictício solicitado.** Esta spec
adota explicitamente: simulação CPAEG/CSAEG no escopo existente, prévia em qualquer estado,
ação local em preparação/coleta, convite institucional não editável, nenhuma segmentação por Participação e nenhuma
persistência nova. São escolhas limitadas e revisáveis; não encerram as decisões
institucionais acima. O plan posterior deve resolver apenas a defesa técnica concreta,
a apresentação transitória do resultado, o cenário CSAEG exercitável e o roteiro local,
sem ampliar o escopo ou implementar produção. Plan aprovado em conceito e tasks autorizadas após as precisões; implementação permanece fora desta etapa.

## Clarifications

### Session 2026-10-03

- Main `0c911b5`, Feature 015 (PR #24): baseline sincronizada, decisões preservadas.
- Prévia nos três estados; simulação local em preparação/coleta; encerrada somente consulta/prévia.
- Deduplicação por Pessoa após escopo das Conclusões.
- Operação rejeita domínio diferente de `example.invalid`, independentemente do SMTP.
- Modelo institucional não editável: nome opcional, Campanha, URL neutra; fallback “Olá!”.
- Nenhuma entidade/migração, Convite, Destinatário, Disparo ou Evento de entrega persistido;
  Campanha e Participação intactas. Mailpit, locmem e resultado transitório bastam.

### Precisões aprovadas antes de tasks — 2026-10-03

- “Público” significa público-alvo da Campanha. Todas as telas/endpoints da 016 são
  administrativos/institucionais: modo demo, operador fictício, governança 010/011 e
  escopo CPAEG/CSAEG obrigatórios. Nenhum egresso acessa Comunicação; cookie de Pessoa
  não autoriza acesso. A entrada neutra de demonstração continua fora da tela administrativa.
- FR-029: cada POST legítimo de “Simular envio” é nova execução independente. Não existe
  “já enviado”, deduplicação entre execuções, histórico ou idempotência entre simulações
  distintas. Duas execuções podem produzir duas mensagens para a mesma Pessoa no Mailpit.
  Não criar chave de idempotência, tabela, cookie ou estado persistido para impedir isso.
- FR-026/027: cada Pessoa do público recebe resultado apenas em memória: “submetida ao
  transporte” (aceite local confirmado), “falha de transporte” (tentativa sem confirmação)
  ou “sem contato” (zero tentativa). Tentativas e aceites continuam contadores distintos;
  totais por situação aparecem na resposta. Interrupção inesperada acrescenta “não tentada”
  às Pessoas com contato ainda não processadas, sem inferir sucesso. Não apresentar lista
  nominal nem persistir esses resultados. Mensagens anteriores não são desfeitas. Não
  envolver SMTP em transação de banco; não fazer retry automático.
- FR-022/038: Serra/Vitória permanece EM PREPARAÇÃO. CTA pode chegar à entrada neutra
  sem tornar essa Campanha respondível. Não abrir Campanha, criar Participação ou contornar
  004/007 para demonstrar e-mail; outras Campanhas já respondíveis seguem suas próprias regras.
