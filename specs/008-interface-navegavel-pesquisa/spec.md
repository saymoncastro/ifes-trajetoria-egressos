# Feature Specification: Interface navegável mínima da pesquisa

**Feature Branch**: `claude/feature-008-interface-pesquisa-05dce9`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "Feature 008 — Interface navegável mínima da pesquisa. Primeiro
vertical slice navegável do Trajetória Ifes: no navegador, com dados integralmente
fictícios, entrar como uma Pessoa fictícia, contextualizar a formação, iniciar ou retomar
a Participação, preencher Seção a Seção, seguir as ramificações reais da baseline, retomar
o rascunho e concluir. A interface é uma camada fina e server-rendered sobre as Features
004–007: não implementa elegibilidade, navegação, obrigatoriedade nem conclusão. Entrada
somente de demonstração, explicitamente não produtiva e sem autenticação. Sem SPA, API
própria, framework de frontend, design system, dashboard, analytics ou novo modelo de
domínio. Funciona sem JavaScript. Acessibilidade (WCAG 2.1 AA/eMAG como direção) e
responsividade desde o início."

## Contexto

As sete primeiras features estabeleceram, apenas como domínio e operações internas:

- **001** — **Pessoa → Conclusão Acadêmica**, com fonte acadêmica simulada como único meio
  de fornecer Pessoas e Conclusões (001 FR-030), dados visivelmente fictícios (001 FR-028).
- **002/003** — **Pesquisa → Versão → Seções → Perguntas → Opções**, com a baseline do
  Formulário Egresso Ifes 2024 materializada em **RASCUNHO** (13 Seções, 54 Perguntas,
  regras em Q1, Q14, Q33 e Q46, 17 percursos esperados). Q10–Q19 continuam perguntas
  declaradas (003/DP-307).
- **004** — **Campanha**, com estado temporal (EM PREPARAÇÃO, EM COLETA, ENCERRADA),
  elegibilidade por Conclusão e consulta das Campanhas aplicáveis.
- **005** — **Participação → Respostas em rascunho**: uma Participação por par Campanha ×
  Conclusão; operações de registrar, substituir e remover Resposta, validadas por tipo.
- **006** — **Jornada e conclusão**: percurso derivado da Versão aplicada e das respostas
  atuais; a **Seção** é a unidade de navegação; Seção atual, pendências, destino,
  respostas fora do percurso, "pode concluir" e a operação de conclusão.
- **007** — **Contextualização da formação e entrada**: a partir de uma Pessoa resolvida,
  a situação de cada formação e a situação de entrada (sem formação, sem pesquisa, sem
  entrada pendente, entrada resolvida, seleção necessária) e a entrada que inicia ou
  retoma a Participação.

Todas essas capacidades declararam, até aqui, que **não seriam expostas** a usuários por
interface, URL ou API (005 FR-058; 006 FR-054; 007 FR-049), porque falta a fronteira real
de identidade (004/DP-406) e a definição de quem pode ver Participações (005/DP-505).

A Feature 008 cria o **primeiro sistema visível** do Trajetória Ifes, para ser
experimentado localmente com dados fictícios:

```text
entrada de demonstração (escolher Pessoa fictícia)        ← 008: adaptador temporário
  │
  ├─► situação das formações e entrada                     ← 007 (consulta / entrar)
  │     (005 inicia ou devolve a Participação)
  ├─► Seção atual, percurso, pendências, destino           ← 006 (consulta da jornada)
  ├─► salvar respostas da Seção                            ← 005 (registrar/substituir/remover)
  ├─► próximo estado da jornada                            ← 006 (consulta, de novo)
  └─► concluir                                             ← 006 (conclusão)
```

### Princípio central desta spec

> **A interface apresenta e encaminha; ela não decide.**
>
> Toda decisão de domínio — quem tem pesquisa, qual Campanha se aplica, qual Participação
> existe, que Seção vem a seguir, o que é obrigatório no percurso, se a coleta admite
> escrita, se é possível concluir — vem das Features 004 a 007. A interface só traduz
> resultados de domínio em telas e mensagens e traduz ações do egresso em chamadas às
> operações existentes.

### Princípios desta spec

1. **Camada fina.** Nenhuma regra de elegibilidade, Campanha, percurso, obrigatoriedade,
   coleta admitida ou conclusão é escrita na interface. Ela consome 007 (formação e
   entrada), 005 (respostas), 006 (jornada e conclusão) e, por meio delas, 004.
2. **Instrumento como única fonte de apresentação.** Textos, ordem, tipos, Opções,
   escalas, complementos e obrigatoriedade apresentados vêm da Versão aplicada. Nenhuma
   tela é específica de uma Pergunta.
3. **A Seção é a tela.** Cada tela de preenchimento apresenta uma Seção inteira do
   percurso, como a 006 a define.
4. **Demonstração é demonstração.** A entrada por Pessoa fictícia existe só em modo de
   demonstração explicitamente ativado, mostra-se como tal em todas as telas e nunca é
   apresentada como autenticação.
5. **Formação, nunca Campanha.** O egresso vê e escolhe formações; Campanha, Versão e
   identificadores técnicos não aparecem.
6. **Nada novo no domínio.** Nenhum modelo, tabela ou coluna nova. Nenhum estado de
   jornada, seleção, posição ou progresso é guardado.
7. **Funciona sem JavaScript.** Responder, navegar, salvar e concluir são páginas e
   formulários comuns.
8. **Acessível e responsiva desde a primeira tela.**

### Termos usados nesta spec

Conceitos de apresentação. Nenhum deles é entidade, tabela ou registro persistido.

- **Modo de demonstração**: configuração explícita do ambiente local de desenvolvimento ou
  teste que torna a interface desta feature disponível. Desativado por padrão.
- **Pessoa de demonstração**: Pessoa do NIAE incorporada da **fonte simulada** (001),
  escolhida na entrada de demonstração. Substitui provisoriamente a "Pessoa resolvida"
  que a 007 espera receber da futura fronteira de identidade (007 FR-001).
- **Entrada de demonstração**: tela em que se escolhe a Pessoa de demonstração. Não é
  login, não prova identidade e não é mecanismo de produção.
- **Tela de formações**: tela que apresenta a situação de entrada da 007 para a Pessoa de
  demonstração.
- **Tela da Seção**: tela que apresenta uma Seção do percurso determinado (006) com suas
  Perguntas e as Respostas atuais.
- **Tela de conclusão**: tela apresentada quando a 006 indica jornada finalizada, com a
  ação de concluir.
- **Confirmação**: tela apresentada depois da conclusão aceita.
- **Cenário de demonstração**: conjunto de dados fictícios preparado por um passo
  explícito, local, para exercitar as situações da 007 e a jornada da 006.
- **Erro de preenchimento**: valor recebido do formulário que não pode ser traduzido em
  operação válida da 005 (por exemplo, Opção que não pertence à Pergunta) ou que a 005
  rejeita.
- **Pendência**: Pergunta obrigatória sem Resposta na Seção, **conforme a 006**. Não é
  erro de preenchimento: as respostas válidas são salvas e a pendência é apresentada.

### Decisões desta especificação

Escolhas de produto e de arquitetura desta feature. Nenhuma é regra institucional; todas
são reversíveis. As marcadas **[Hipótese]** são escolhas de produto confirmadas pelo
solicitante (ver Clarifications); continuam reversíveis por feature futura.

- **Exposição somente em modo de demonstração.** As restrições de exposição da 005
  (FR-058), da 006 (FR-054) e da 007 (FR-049) protegem egressos reais e dados reais
  enquanto não houver fronteira de identidade. Esta feature as respeita: a interface
  inteira — não só a entrada — só existe com o modo de demonstração ativado, só aceita
  Pessoas da fonte simulada e nunca é oferecida a egressos. Fora desse modo, nenhuma
  página desta feature responde. A exposição real a egressos continua dependendo de
  004/DP-406 e 005/DP-505. (FR-001 a FR-006)
- **A Pessoa de demonstração vem da fonte simulada, e só dela.** A lista de escolha e a
  validação a cada requisição consideram exclusivamente Pessoas cuja origem é a fonte
  simulada. Mesmo que o modo de demonstração fosse ativado por engano sobre um banco com
  dados reais, nenhuma Pessoa real seria listada ou aceita. (FR-008, FR-010)
- **Entrar é uma ação explícita, não uma visita.** Ver a tela de formações nunca cria
  Participação. A Participação nasce (ou é retomada) somente quando o egresso aciona
  "Iniciar" ou "Continuar", pela entrada da 007. Com uma única formação pendente, essa ação
  é única e não pede escolha de formação. (FR-020, FR-029 a FR-031) **[Hipótese]**
- **Salvar a Seção grava rascunho mesmo com pendências.** Ao enviar uma Seção, as
  respostas válidas são gravadas pela 005, como rascunho, mesmo que ainda faltem
  obrigatórias. Em seguida a 006 é consultada: se a Seção não pode ser deixada, a mesma
  Seção é reapresentada com as pendências apontadas pela 006. Erros de preenchimento, ao
  contrário, impedem **qualquer** gravação daquela submissão. (FR-040 a FR-047)
  **[Hipótese]**
- **Depois de salvar, segue-se o destino da Seção calculado pela 006.** Se a Seção
  enviada pode ser deixada, a próxima tela é o seu destino na 006 (outra Seção ou a tela
  de conclusão). Ao entrar ou retomar, a tela é a Seção atual da 006. A interface nunca
  calcula destino. (FR-050 a FR-053) **[Hipótese]**
- **Seções anteriores do percurso podem ser revisitadas.** O egresso pode voltar a
  qualquer Seção do percurso determinado (006 US8.3), alterar respostas e seguir de novo
  pelos destinos que a 006 recalcular. Seções fora do percurso nunca são apresentadas.
  (FR-054, FR-055)
- **Concluir é uma tela própria.** Quando a 006 indica jornada finalizada, a interface
  apresenta uma tela que avisa que, depois de concluída, a pesquisa não poderá ser
  alterada, e oferece a ação de concluir. Não há resumo das respostas. (FR-056 a FR-061)
  **[Hipótese]**
- **Os textos de abertura e de encerramento são os da Versão.** Quando existem, o texto
  de abertura acompanha a primeira Seção, e o texto de encerramento acompanha a
  confirmação. Não são reescritos nem substituídos. (FR-032, FR-062)
- **Campo deixado em branco é ausência de resposta.** Texto vazio ou só com espaços,
  nenhuma Opção marcada ou nenhum ponto de escala escolhido significam "sem Resposta"; se
  havia Resposta, ela é removida pela 005. O texto não vazio é gravado exatamente como
  digitado. (FR-041, FR-042) **[Hipótese]**
- **Sem indicador de progresso.** Com ramificações, a quantidade de Seções restantes só é
  conhecida ao fim; um indicador seria impreciso e exigiria regra própria. A 006 deixou
  progresso para feature futura. (FR-095)
- **Cenário de demonstração por passo explícito e só pelas operações existentes.** Um
  passo local, executado deliberadamente por quem desenvolve, incorpora as Pessoas da
  fonte simulada (001), publica uma **cópia de demonstração** da baseline (002/003; a
  baseline continua em RASCUNHO) e abre Campanhas de demonstração (004). Nada disso entra
  em migração nem roda automaticamente. (FR-012 a FR-018)

## Clarifications

### Session 2026-10-01

Depois da especificação, o solicitante decidiu seguir diretamente para o `/speckit-plan`,
sem `/speckit-clarify`, aceitando as escolhas de produto marcadas **[Hipótese]**. Elas
passam a ser decisões desta feature, sem resolver nenhuma regra institucional e
reversíveis por feature futura:

- **Q: Ver a tela de formações já inicia a Participação quando há uma única formação
  pendente?** → **Não.** A Participação só nasce (ou é retomada) por ação explícita
  ("Iniciar a pesquisa"/"Continuar a pesquisa"), pela entrada da 007. Com uma única
  formação pendente, a ação é única e não pede escolha de formação. (FR-020, FR-029 a
  FR-031)
- **Q: Uma Seção com obrigatória em branco pode ser salva?** → **Sim, como rascunho.** As
  respostas válidas são gravadas pela 005 e a mesma Seção é reapresentada com as
  pendências calculadas pela 006. Erros de preenchimento impedem qualquer gravação da
  submissão. (FR-040 a FR-047)
- **Q: Depois de salvar uma Seção, qual é a próxima tela?** → **O destino daquela Seção
  calculado pela 006** (outra Seção ou a tela de conclusão), e não um salto para a Seção
  atual. Ao entrar ou retomar, a tela é a Seção atual. (FR-050 a FR-053)
- **Q: Concluir exige uma tela própria?** → **Sim.** A tela de conclusão avisa que a
  pesquisa não poderá ser alterada depois de concluída e permite revisar as Seções do
  percurso; não mostra resumo das respostas. (FR-056 a FR-061)
- **Q: Campo deixado em branco é resposta vazia?** → **Não; é ausência de Resposta.**
  Texto vazio ou só com espaços, nenhuma Opção marcada ou nenhum ponto de escala
  escolhido significam "sem Resposta" (se havia, é removida pela 005); texto não vazio é
  gravado exatamente como digitado. (FR-041, FR-042)

## User Scenarios & Testing *(mandatory)*

<!--
  Os usuários desta feature são quem desenvolve, testa e demonstra o Trajetória Ifes, no
  papel de um egresso fictício. Nenhum egresso real usa esta interface.

  Os testes de aceitação percorrem as páginas por requisições HTTP comuns, sem
  JavaScript, sobre as operações reais das Features 001 a 007 — sem dublês da camada de
  domínio. Como na 005 a 007, Versões são publicadas e Campanhas abertas apenas no
  ambiente local ou de teste; isso não é publicação institucional (002/DP-001).

  Q1–Q54 e S1–S13 são chaves de rastreabilidade da 003, usadas aqui só para ilustrar.
  Elas nunca aparecem na interface nem no código da interface.
-->

### User Story 1 - Entrar em modo de demonstração com uma Pessoa fictícia (Priority: P1)

Com o modo de demonstração ativado, quem demonstra abre o Trajetória Ifes no navegador,
vê um aviso claro de que é um ambiente de demonstração com dados fictícios e sem
autenticação, e escolhe uma das Pessoas fictícias pelo nome e por um resumo das suas
formações. A partir daí, todas as telas agem em nome dessa Pessoa, até que outra seja
escolhida ou a demonstração seja encerrada.

**Why this priority**: sem uma Pessoa não existe ponto de partida para a 007; a entrada
de demonstração substitui provisoriamente a fronteira de identidade.

**Independent Test**: com o cenário de demonstração preparado, abrir a entrada, escolher
"Maria Exemplo" e verificar que a tela de formações mostra as formações dela; trocar para
outra Pessoa e verificar a troca; desativar o modo de demonstração e verificar que
nenhuma página responde.

**Acceptance Scenarios**:

1. **Given** o modo de demonstração ativado e o cenário preparado, **When** a entrada de
   demonstração é aberta, **Then** ela lista as Pessoas fictícias incorporadas da fonte
   simulada, cada uma com o nome (ou a indicação de nome não informado) e um resumo das
   suas formações, sem UUID, código de origem, identificador externo, fonte ou Campanha.
2. **Given** a entrada de demonstração, **When** ela é exibida, **Then** um aviso
   permanente informa que se trata de demonstração com dados fictícios, que não há
   autenticação e que a escolha não comprova identidade; o mesmo aviso aparece em todas as
   telas desta feature.
3. **Given** a escolha de uma Pessoa, **When** a escolha é confirmada, **Then** o sistema
   apresenta a tela de formações daquela Pessoa, e nenhuma Participação, Resposta ou outro
   registro de domínio é criado.
4. **Given** duas Pessoas homônimas ("Carla Exemplo"), **When** a entrada é exibida,
   **Then** elas aparecem como itens distintos, distinguíveis pelo resumo das formações,
   sem identificadores técnicos.
5. **Given** uma Pessoa de demonstração em uso, **When** se aciona "trocar de pessoa" ou
   "encerrar demonstração", **Then** a entrada de demonstração volta a ser apresentada e
   a Pessoa anterior deixa de ser usada.
6. **Given** o modo de demonstração desativado, **When** qualquer página desta feature é
   solicitada, **Then** ela não existe (resposta de página não encontrada), sem revelar
   dados.

---

### User Story 2 - Ver as formações e resolver a formação com pesquisa pendente (Priority: P1)

Depois de escolhida a Pessoa, a tela de formações apresenta o resultado da consulta da
situação de entrada da 007. Com uma única formação pendente, a tela diz a que formação a
pesquisa se refere e oferece uma única ação ("Iniciar a pesquisa" ou "Continuar a
pesquisa"). Com duas ou mais, pergunta sobre qual formação o egresso responderá. Nos
demais casos, informa a situação em linguagem simples.

**Why this priority**: é a contextualização exigida pelo Princípio XIV e o ponto em que a
interface consome a 007 sem reimplementá-la.

**Independent Test**: preparar o cenário; para cada Pessoa de demonstração que representa
uma situação global da 007, abrir a tela de formações e comparar o que é apresentado com
a situação devolvida pela 007.

**Acceptance Scenarios**:

1. **Given** uma Pessoa com exatamente uma formação com entrada pendente (por exemplo,
   SIM-P-0001), **When** a tela de formações é aberta, **Then** ela apresenta "Esta
   pesquisa refere-se a …" com os atributos disponíveis da Conclusão (curso, unidade, ano
   de conclusão e, quando úteis, nível e modalidade) e uma única ação de iniciar ou
   continuar; nenhuma escolha de formação é pedida.
2. **Given** uma Pessoa com duas formações com entrada pendente (por exemplo,
   SIM-P-0003), **When** a tela é aberta, **Then** ela pergunta sobre qual formação o
   egresso responderá, lista as duas com seu contexto e uma ação para cada, em ordem
   determinística, sem nenhuma marcada como sugerida, principal ou mais recente.
3. **Given** uma Pessoa cujas formações não têm pesquisa (situação "sem pesquisa
   disponível"), **When** a tela é aberta, **Then** ela informa que não há pesquisa
   disponível para suas formações neste momento, lista as formações e não oferece ação de
   iniciar.
4. **Given** uma formação "já concluída", **When** a tela é aberta, **Then** essa formação
   aparece com a indicação "pesquisa já respondida", sem ação de abrir o formulário.
5. **Given** uma formação em "ambiguidade operacional", **When** a tela é aberta, **Then**
   essa formação aparece com a indicação de que a pesquisa referente a ela não está
   disponível neste momento, sem nomear Campanhas, sem pedir escolha de Campanha e sem
   ação de iniciar; outras formações não são afetadas (007 FR-027a).
6. **Given** a situação "sem entrada pendente" (formações concluídas e/ou ambíguas),
   **When** a tela é aberta, **Then** ela informa que não há pesquisa pendente neste
   momento e mostra a situação de cada formação.
7. **Given** a situação "sem formação disponível" (construída em teste, pois não ocorre
   pela fonte simulada), **When** a tela é aberta, **Then** ela informa, em linguagem
   simples, que não foram encontradas formações, sem tratar isso como erro.
8. **Given** qualquer uma dessas telas, **When** ela é apresentada, **Then** nada foi
   gravado (a consulta da 007 não grava — 007 FR-024).
9. **Given** um atributo da Conclusão não informado pela fonte, **When** a formação é
   apresentada, **Then** o atributo é omitido ou indicado como não informado, nunca
   preenchido com valor padrão ou deduzido.

---

### User Story 3 - Iniciar ou retomar a Participação (Priority: P1)

Ao acionar "Iniciar" (ou "Continuar"), a interface chama a entrada da 007 — com a
formação, quando houve escolha — e, se ela devolve uma Participação em rascunho (nova ou
existente), leva o egresso à Seção atual da jornada.

**Why this priority**: é a passagem da formação para o questionário.

**Independent Test**: com SIM-P-0001, acionar "Iniciar" e verificar que exatamente uma
Participação foi criada pela 005 e que a tela seguinte é a primeira Seção; acionar de
novo e verificar que nenhuma outra foi criada e que a Seção atual é apresentada.

**Acceptance Scenarios**:

1. **Given** uma formação "disponível para iniciar", **When** "Iniciar a pesquisa" é
   acionado, **Then** a Participação é criada pela entrada da 007 (que usa a 005) e a
   primeira Seção da Versão aplicada é apresentada, sem respostas.
2. **Given** uma formação "disponível para retomar", **When** "Continuar a pesquisa" é
   acionado, **Then** nenhuma Participação é criada e a Seção atual indicada pela 006 é
   apresentada com as respostas já gravadas.
3. **Given** a seleção de uma formação entre duas, **When** sua ação é acionada, **Then**
   a entrada é feita para aquela formação; a outra não é tocada.
4. **Given** que, entre a exibição da tela e a ação, a Campanha encerrou, a formação foi
   concluída noutra aba ou surgiu ambiguidade, **When** a ação é acionada, **Then** a
   interface apresenta a situação devolvida pela entrada da 007 (sem pesquisa, já
   respondida, indisponível) e nada é criado.
5. **Given** uma ação de entrada com uma formação que não pertence à Pessoa de
   demonstração (por exemplo, formulário adulterado), **When** ela é enviada, **Then** a
   interface informa que a formação não está disponível, sem revelar dado algum, e nada é
   criado.
6. **Given** recarregar a página depois de iniciar, **When** o navegador repete a
   navegação, **Then** nenhuma segunda Participação nem pedido de reenvio de formulário
   ocorre.

---

### User Story 4 - Visualizar e responder a Seção atual (Priority: P1)

A tela da Seção apresenta, na ordem da Versão, todas as Perguntas da Seção, com enunciado,
texto explicativo, Opções, escala e indicação de obrigatoriedade, e controles adequados a
cada um dos quatro tipos, incluindo o complemento de "Outro".

**Why this priority**: é o preenchimento propriamente dito.

**Independent Test**: com a Versão de demonstração, abrir as Seções que contêm os quatro
tipos (por exemplo, S2, S3, S8, S10, S11) e verificar controles, rótulos, ordem e
indicação de obrigatoriedade contra a Versão.

**Acceptance Scenarios**:

1. **Given** uma Seção de escolha única (por exemplo, S1), **When** apresentada, **Then**
   cada Opção é um item selecionável exclusivo, com o texto da Versão, na ordem da
   Versão, agrupado sob o enunciado da Pergunta.
2. **Given** uma Pergunta de escolha múltipla (por exemplo, Q47), **When** apresentada,
   **Then** cada Opção é marcável independentemente, sem mínimo, máximo nem
   exclusividade entre Opções (002/DP-005).
3. **Given** uma Pergunta de texto curto (por exemplo, Q3), **When** apresentada, **Then**
   há um campo de texto de uma linha, sem máscara nem validação de formato.
4. **Given** uma Pergunta de escala (por exemplo, Q20), **When** apresentada, **Then**
   cada ponto inteiro do início ao fim é selecionável, e os rótulos de extremidade
   aparecem quando a Versão os tem; rótulo ausente (003/DP-301) não é inventado.
5. **Given** uma Pergunta com a Opção que admite complemento (por exemplo, Q26, Q32,
   Q45), **When** apresentada, **Then** há um campo de texto associado a essa Opção,
   rotulado de forma que fique claro a que Opção se refere.
6. **Given** uma Pergunta obrigatória, **When** apresentada, **Then** a obrigatoriedade é
   indicada por texto (não só por cor ou símbolo) e de forma perceptível a tecnologias
   assistivas; uma Pergunta opcional não recebe essa indicação.
7. **Given** a Seção S11, **When** apresentada, **Then** Q46, Q47 e Q48 aparecem juntas,
   nessa ordem, qualquer que seja a resposta a Q46 (006 FR-025).
8. **Given** S3 (Q10–Q14), **When** apresentada, **Then** as Perguntas aparecem sem
   resposta pré-preenchida, sem sugestão e sem destaque derivados da Conclusão (003/DP-307;
   007 FR-041).
9. **Given** qualquer tela da Seção, **When** apresentada, **Then** o contexto da formação
   (curso, unidade, ano, quando disponíveis) é exibido como informação institucional,
   distinta das Perguntas, e a Seção tem título e texto introdutório da Versão quando
   existem.

---

### User Story 5 - Salvar respostas e avançar segundo a jornada (Priority: P1)

Ao enviar a Seção, a interface converte o formulário em registrar, substituir ou remover
Respostas pela 005 e consulta a 006. Se a Seção pode ser deixada, apresenta o destino
calculado pela 006; se há pendências, reapresenta a Seção com as pendências; se há erro
de preenchimento, reapresenta a Seção sem gravar nada.

**Why this priority**: é o ciclo central do preenchimento e a prova de que a navegação é
da 006.

**Independent Test**: preencher S1 com "Sim", enviar e verificar S2; deixar uma
obrigatória de S2 em branco, enviar e verificar a reapresentação de S2 com a pendência
apontada e as demais respostas gravadas; enviar um valor de Opção adulterado e verificar
que nada foi gravado.

**Acceptance Scenarios**:

1. **Given** a Seção atual com todas as obrigatórias respondidas, **When** é enviada,
   **Then** as Respostas são gravadas exclusivamente pelas operações da 005 e a tela
   seguinte é o destino da Seção segundo a 006.
2. **Given** a Seção com uma obrigatória em branco, **When** é enviada, **Then** as
   respostas válidas são gravadas, a mesma Seção é reapresentada com os valores
   informados, uma mensagem no topo resume as pendências e cada Pergunta pendente traz sua
   própria mensagem, conforme as pendências da 006.
3. **Given** a Seção com um valor inválido (Opção que não pertence à Pergunta, ponto fora
   da escala, complemento sem a Opção correspondente marcada), **When** é enviada,
   **Then** nenhuma Resposta da submissão é gravada, a Seção é reapresentada com os valores
   informados e cada erro é associado à sua Pergunta, em linguagem simples.
4. **Given** uma Pergunta respondida cujo campo é deixado em branco, **When** a Seção é
   enviada, **Then** a Resposta é removida pela 005.
5. **Given** a Seção enviada sem nenhuma alteração, **When** a 006 é consultada, **Then**
   o comportamento é o mesmo de uma Seção com as mesmas respostas: avança ou aponta
   pendências.
6. **Given** um envio bem-sucedido, **When** a página seguinte é recarregada, **Then** a
   gravação não se repete nem há pedido de reenvio.
7. **Given** campos enviados que não pertencem à Seção apresentada, **When** a Seção é
   processada, **Then** eles são desconsiderados e nada é gravado para eles.

---

### User Story 6 - Retomar um rascunho mantendo as respostas (Priority: P1)

O egresso pode sair a qualquer momento. Ao voltar — escolhendo de novo a Pessoa de
demonstração e a formação — a interface o leva à Seção atual da 006, com as respostas já
gravadas apresentadas nos campos.

**Why this priority**: retomada real é a promessa do rascunho (005) e da jornada derivada
(006).

**Independent Test**: responder até o meio de S9, sair (encerrar a demonstração ou fechar
o navegador), entrar de novo e verificar S9 como Seção atual, com as respostas de S9 nos
campos; voltar a S2 e verificar as respostas de S2.

**Acceptance Scenarios**:

1. **Given** uma Participação em rascunho com respostas nos quatro tipos e um complemento
   de "Outro", **When** a Seção que as contém é aberta, **Then** cada valor gravado aparece
   no seu controle: Opção marcada, Opções marcadas, texto exatamente como gravado, ponto
   da escala e complemento.
2. **Given** a retomada, **When** se verifica o que foi gravado para retomar, **Then**
   nada além das Respostas já existentes: nenhuma posição, sessão de jornada ou progresso
   (006 FR-005).
3. **Given** valores digitados e não enviados antes de sair, **When** o egresso volta,
   **Then** esses valores não existem; tudo o que foi enviado com sucesso está preservado.
4. **Given** respostas que ficaram fora do percurso por troca de ramo, **When** o ramo
   original volta ao percurso, **Then** as respostas daquele ramo reaparecem nos campos
   sem redigitação (006 FR-030).

---

### User Story 7 - Percorrer os ramos reais da baseline (Priority: P1)

Pela interface, os ramos de Q1, Q14, Q33 e Q46 levam às Seções que a 006 calcula, porque
a Versão de demonstração os contém — não porque a interface os conhece.

**Why this priority**: é a prova visível de que a baseline funciona por causa do modelo
de instrumento, e a principal garantia contra navegação codificada na interface.

**Independent Test**: dirigir a interface pelas 17 combinações de Q1, Q14, Q33 e Q46 e
comparar a sequência de Seções apresentadas com os percursos esperados da 003; repetir
com uma Versão de teste de estrutura diferente e verificar que a interface segue a 006
sem alteração da interface.

**Acceptance Scenarios**:

1. **Given** Q14 respondida com cada uma das quatro Opções, **When** S3 é enviada,
   **Then** a Seção seguinte é S4, S5, S6 ou S7, respectivamente, e depois S8.
2. **Given** Q33 = "Sim" ou "Não", **When** S8 é enviada, **Then** a Seção seguinte é S9
   ou S10, e depois S11.
3. **Given** Q46 = "Sim" ou "Não", **When** S11 (com Q47 respondida) é enviada, **Then** a
   Seção seguinte é S12 ou S13.
4. **Given** um percurso já preenchido até S11 e Q14 alterada ao revisitar S3, **When** S3
   é enviada, **Then** o destino apresentado é o novo ramo calculado pela 006, e as
   respostas do ramo anterior não aparecem no percurso.
5. **Given** uma Versão de teste diferente da baseline (outras Seções, regras e
   encaminhamentos), **When** uma Participação é percorrida pela interface, **Then** a
   sequência de telas coincide com o percurso da 006 para aquela Versão, sem qualquer
   mudança na interface.

---

### User Story 8 - Concluir a pesquisa (Priority: P1)

Quando a 006 indica jornada finalizada, a interface apresenta a tela de conclusão. A
conclusão é feita exclusivamente pela operação da 006.

**Why this priority**: sem conclusão a Participação nunca vira observação consolidada.

**Independent Test**: preencher um percurso completo, chegar à tela de conclusão,
concluir e verificar `concluida_em` registrado pela 006 e a confirmação apresentada.

**Acceptance Scenarios**:

1. **Given** a última Seção do percurso enviada e satisfeita, **When** a 006 indica
   jornada finalizada e que a Participação pode ser concluída, **Then** a tela de
   conclusão é apresentada, com o aviso de que, depois de concluída, a pesquisa não poderá
   ser alterada, a possibilidade de revisar Seções do percurso e a ação "Concluir
   pesquisa".
2. **Given** a tela de conclusão, **When** "Concluir pesquisa" é acionado, **Then** a
   operação de conclusão da 006 é chamada e, em sucesso, a confirmação é apresentada.
3. **Given** que a conclusão é rejeitada (por exemplo, a Campanha encerrou ou surgiu
   pendência por alteração em outra aba), **When** a rejeição volta, **Then** a interface
   apresenta a mensagem correspondente — período encerrado ou Seção com pendência — e nada
   muda.
4. **Given** a jornada não finalizada, **When** a tela de conclusão é solicitada
   diretamente, **Then** a interface apresenta a Seção atual da 006, sem oferecer a ação
   de concluir.
5. **Given** a ação de concluir repetida (duplo envio, recarga), **When** a 006 devolve
   "já concluída", **Then** a interface apresenta a mesma confirmação, sem erro.

---

### User Story 9 - Visualizar a confirmação de conclusão (Priority: P1)

Depois da conclusão aceita, a confirmação diz, de forma simples, que a pesquisa foi
concluída e agradece a participação, podendo mostrar o contexto da formação e o texto de
encerramento da Versão.

**Why this priority**: fecha a jornada para o egresso.

**Independent Test**: concluir e verificar a confirmação: mensagem de conclusão, contexto
da formação, nenhum valor declarado, nenhum controle de edição.

**Acceptance Scenarios**:

1. **Given** a conclusão aceita, **When** a confirmação é apresentada, **Then** ela
   contém "Pesquisa concluída" e um agradecimento, o contexto da formação e, se existir, o
   texto de encerramento da Versão.
2. **Given** a confirmação, **When** é inspecionada, **Then** não contém resumo de
   respostas, valores declarados, comprovante, certificado, arquivo para download,
   identificador técnico nem ação de editar ou reabrir.
3. **Given** a confirmação, **When** o egresso deseja continuar, **Then** há apenas o
   caminho de volta à tela de formações (onde a formação aparece como já respondida).

---

### User Story 10 - Informar Participação já concluída (Priority: P2)

Se o egresso volta a uma formação cuja Participação já está concluída — pela tela de
formações, por um endereço salvo ou por uma aba antiga —, a interface informa que a
pesquisa já foi respondida e não abre o formulário.

**Why this priority**: concluída é imutável (006 FR-038 a FR-041); a interface não pode
sugerir o contrário.

**Independent Test**: concluir; abrir a tela de formações, o endereço de uma Seção, o da
tela de conclusão e reenviar um formulário antigo; verificar em todos os casos a
mensagem de pesquisa já respondida e a Participação inalterada.

**Acceptance Scenarios**:

1. **Given** uma Participação concluída, **When** a tela de formações é aberta, **Then** a
   formação aparece como "pesquisa já respondida", sem ação de abrir.
2. **Given** uma Participação concluída, **When** o endereço de uma Seção dela é aberto,
   **Then** a interface informa que a pesquisa já foi respondida, sem formulário e sem
   valores declarados.
3. **Given** uma Seção aberta numa aba antes da conclusão feita noutra aba, **When** essa
   Seção é enviada, **Then** a 005/006 rejeita a escrita, nada muda e a interface informa
   que a pesquisa já foi respondida.
4. **Given** qualquer tela, **When** se procura ação de reabrir, editar ou responder de
   novo a mesma Campanha, **Then** ela não existe.

---

### User Story 11 - Informar ausência de pesquisa disponível (Priority: P2)

Para uma Pessoa sem pesquisa disponível — nenhuma Campanha aplicável, ou formações
inelegíveis —, a interface informa claramente e não oferece formulário.

**Why this priority**: será a situação mais comum fora das janelas de coleta.

**Independent Test**: com a Pessoa de demonstração do cenário "sem pesquisa", abrir a
tela de formações e verificar a mensagem, as formações listadas e nenhuma ação de
iniciar.

**Acceptance Scenarios**:

1. **Given** a situação "sem pesquisa disponível", **When** a tela de formações é aberta,
   **Then** a mensagem diz que não há pesquisa disponível para suas formações neste
   momento, sem expor critérios, Campanhas ou motivos de inelegibilidade (007 FR-015).
2. **Given** uma Participação em rascunho de Campanha já encerrada, **When** a tela de
   formações é aberta, **Then** a formação aparece sem pesquisa disponível, conforme a
   007, e o rascunho não é oferecido para continuar.

---

### User Story 12 - Tratar ambiguidade de formação/Campanha (Priority: P2)

Quando a 007 indica ambiguidade operacional numa formação, a interface informa que a
pesquisa daquela formação não está disponível neste momento, sem pedir escolha de
Campanha e sem bloquear outras formações.

**Why this priority**: preserva 004/DP-404 e 007/DP-701 na primeira apresentação ao
egresso.

**Independent Test**: com a Pessoa de demonstração do cenário de ambiguidade, abrir a
tela de formações; verificar a mensagem, nenhuma Campanha nomeada e, se houver outra
formação pendente, a ação dela disponível.

**Acceptance Scenarios**:

1. **Given** uma formação ambígua, **When** a tela é aberta, **Then** a mensagem é neutra
   ("a pesquisa referente a esta formação não está disponível neste momento"), sem nome,
   período ou quantidade de Campanhas.
2. **Given** uma formação ambígua e outra única pendente, **When** a tela é aberta,
   **Then** a ação de iniciar ou continuar da outra formação está disponível, sem escolha
   de formação (007 FR-027a).
3. **Given** uma ação de entrada para a formação ambígua (por exemplo, formulário
   adulterado), **When** é enviada, **Then** nada é criado e a mesma mensagem neutra é
   apresentada.

---

### User Story 13 - Tratar encerramento da Campanha durante o preenchimento (Priority: P2)

Se a Campanha deixa de admitir escrita entre duas requisições, a interface apresenta o
resultado das operações de domínio: informa que o período de resposta foi encerrado e
que o que já estava salvo foi preservado. Ela não tenta contornar nem conceder prazo.

**Why this priority**: preserva o significado temporal da rodada (005 FR-039 a FR-041;
006 FR-042) sem duplicar regra temporal.

**Independent Test**: com o momento de referência controlado em teste, abrir uma Seção
dentro do período, avançar o momento para depois do fim e enviar; verificar a mensagem,
nenhuma gravação e o rascunho intacto. Repetir com a tela de conclusão.

**Acceptance Scenarios**:

1. **Given** uma Seção aberta durante a coleta e a Campanha encerrada antes do envio,
   **When** a Seção é enviada, **Then** a 005 rejeita, nenhuma Resposta da submissão é
   gravada, as anteriores permanecem e a interface informa que o período de resposta foi
   encerrado e que as respostas salvas anteriormente foram preservadas.
2. **Given** a tela de conclusão e a Campanha encerrada antes da ação, **When** "Concluir"
   é acionado, **Then** a 006 rejeita e a interface apresenta a mesma mensagem; a
   Participação continua em rascunho.
3. **Given** a Campanha encerrada, **When** o egresso abre de novo uma Seção daquela
   Participação, **Then** a interface informa o encerramento, sem controles de edição.
4. **Given** o último dia do período, **When** a Seção é enviada, **Then** a gravação é
   aceita (a regra temporal é a da 004, não da interface).

---

### User Story 14 - Garantir acessibilidade e responsividade básicas (Priority: P3)

Todas as telas podem ser usadas apenas com teclado, com leitor de tela e em celular, com
estrutura semântica, rótulos associados, foco visível e mensagens associadas aos campos.

**Why this priority**: é requisito constitucional (Princípios XX e XXI) desde a primeira
interface; aparece como P3 apenas porque depende das telas das histórias anteriores. Não
é etapa de acabamento.

**Independent Test**: percorrer a jornada completa só com teclado; verificar rótulos,
agrupamentos, títulos e associação de erros por inspeção e por verificação automatizada
de acessibilidade; verificar as telas em largura de celular e com ampliação de texto.

**Acceptance Scenarios**:

1. **Given** qualquer tela, **When** percorrida só com teclado, **Then** todos os
   controles são alcançáveis numa ordem lógica, o foco é sempre visível e nenhuma ação
   exige mouse.
2. **Given** uma Pergunta de escolha ou de escala, **When** lida por tecnologia
   assistiva, **Then** o enunciado é anunciado como rótulo do grupo e cada Opção como
   rótulo do seu controle.
3. **Given** um envio com pendências ou erros, **When** a Seção é reapresentada, **Then**
   o resumo no topo recebe o foco ou é anunciado, cada item leva à Pergunta
   correspondente, cada mensagem está associada ao campo, e o título da página indica que
   há erros.
4. **Given** uma tela larga de 320 pixels CSS ou ampliação de texto de 200%, **When**
   qualquer tela é usada, **Then** não há rolagem horizontal da página nem conteúdo
   cortado, e os controles são confortáveis ao toque.
5. **Given** qualquer informação de estado (obrigatória, erro, já respondida,
   indisponível), **When** apresentada, **Then** não depende só de cor.

---

### Cenários ponta a ponta *(mandatory para esta feature)*

Executados por requisições HTTP comuns, sem JavaScript, sobre as Features reais 001 a
007, sem dublês de domínio. Cada um é, também, roteiro de demonstração manual.

**E2E-1 — Jornada principal com retomada e conclusão** (Pessoa de demonstração com
exatamente uma formação pendente):

1. Preparar o banco local com o cenário de demonstração.
2. Acessar a entrada de demonstração (aviso de demonstração visível).
3. Escolher a Pessoa fictícia.
4. A tela de formações mostra "Esta pesquisa refere-se a …" e uma única ação.
5. Acionar "Iniciar a pesquisa": a Participação é criada pela 007/005 e S1 é apresentada,
   com o texto de abertura da Versão.
6. Responder Q1 = "Sim" e enviar: S2 é apresentada.
7. Percorrer uma combinação real de ramos — por exemplo, Q14 = "Graduação" (S6),
   Q33 = "Sim" (S9), Q46 = "Sim" (S12) — enviando cada Seção; numa delas, deixar uma
   obrigatória em branco e verificar a pendência; numa Seção com escolha múltipla,
   marcar "Outro" com complemento.
8. Verificar que cada envio gravou as respostas.
9. No meio de S9, abandonar a página (encerrar a demonstração).
10. Retornar: escolher de novo a Pessoa.
11. A tela de formações oferece "Continuar a pesquisa"; ao acionar, S9 é apresentada com
    as respostas já gravadas, inclusive o complemento.
12. Continuar até S13.
13. Na tela de conclusão, acionar "Concluir pesquisa".
14. Ver a confirmação ("Pesquisa concluída", agradecimento, contexto da formação).
15. Tentar acessar de novo: pela tela de formações e pelo endereço de uma Seção.
16. Ver, em ambos, que a pesquisa já foi respondida, sem formulário, e verificar que a
    Participação concluída contém exatamente as Respostas do percurso final.

**E2E-2 — Q1 = Não**:

1. Com outra Pessoa de demonstração, iniciar a pesquisa.
2. Responder Q1 = "Não" e enviar.
3. A 006 indica jornada finalizada: a tela de conclusão é apresentada; nenhuma Seção
   posterior é apresentada.
4. Concluir: confirmação apresentada; a Participação tem exatamente uma Resposta (Q1).
5. Nenhuma tela ou mensagem descreve isso como consentimento negado, recusa jurídica ou
   bloqueio futuro (006 FR-024).
6. Variante: responder Q1 = "Sim", preencher parte de S2, voltar a S1, trocar Q1 para
   "Não", enviar e concluir; a Participação concluída tem só Q1 (006 FR-032).

**E2E-3 — Seleção entre formações**: com SIM-P-0003 (duas formações pendentes), a tela
pergunta sobre qual formação responder; iniciar pela primeira, responder S1, voltar à
tela de formações e verificar que agora a primeira aparece para continuar e a segunda
para iniciar, ainda em seleção (007 US4.2); iniciar a segunda e verificar duas
Participações independentes.

**E2E-4 — Encerramento durante o preenchimento** (somente em teste automatizado, com
momento de referência controlado): Seção aberta no período; envio depois do fim;
mensagem de período encerrado; nada gravado; rascunho intacto; tela de formações sem
pesquisa disponível para aquela formação.

### Telas e estados

| Tela / estado | Quando | Fonte da decisão | Ações oferecidas |
|---------------|--------|------------------|------------------|
| Entrada de demonstração | Modo de demonstração ativo, nenhuma Pessoa em uso | 008 (fonte simulada) | Escolher Pessoa |
| Formações — entrada resolvida | Uma formação pendente | 007 | Iniciar **ou** Continuar (uma) |
| Formações — seleção necessária | Duas ou mais pendentes | 007 | Uma ação por formação pendente |
| Formações — sem entrada pendente | Concluídas e/ou ambíguas | 007 | Nenhuma ação de preenchimento |
| Formações — sem pesquisa disponível | Nenhuma Campanha aplicável | 007 | Nenhuma |
| Formações — sem formação | Pessoa sem Conclusões | 007 | Nenhuma |
| Seção | Seção do percurso, Participação em rascunho, escrita admitida | 006 | Salvar e continuar; voltar a Seção anterior do percurso; sair |
| Seção com pendências | Seção não pode ser deixada | 006 | Idem, com mensagens |
| Seção com erros de preenchimento | Valor inválido ou rejeitado pela 005 | 008 (forma) / 005 (valor) | Idem, com mensagens; nada gravado |
| Conclusão | Jornada finalizada e pode concluir | 006 | Concluir; revisar Seções |
| Confirmação | Conclusão aceita ou "já concluída" | 006 | Voltar às formações |
| Pesquisa já respondida | Participação concluída | 006/007 | Voltar às formações |
| Período encerrado | Escrita/conclusão não admitida pela Campanha | 005/006 | Voltar às formações |
| Formação indisponível | Ambiguidade, formação alheia ou inexistente | 007 | Voltar às formações |
| Pesquisa indisponível | Estrutura não suportada (006 FR-016) | 006 | Voltar às formações |
| Página não encontrada | Modo desativado; recurso inexistente ou alheio | 008 | — |
| Erro inesperado | Falha não prevista | — | Voltar ao início |

### Edge Cases

- **Modo de demonstração desativado**: nenhuma página desta feature existe; o preparo do
  cenário recusa-se a executar (FR-001, FR-016).
- **Banco com Pessoas de outra fonte**: não aparecem na entrada nem são aceitas; o preparo
  do cenário recusa-se a executar sobre esse banco (FR-008, FR-017).
- **Pessoa de demonstração referenciada que deixou de existir** (banco recriado): a
  interface volta à entrada de demonstração, sem erro técnico.
- **Pessoa sem nome informado** (SIM-P-0009): aparece como "Pessoa fictícia sem nome
  informado", com o resumo das formações.
- **Homônimos**: distinguíveis pelo resumo das formações; o nome não participa de nada.
- **Formações com atributos idênticos ou sem atributos**: continuam itens distintos, cada
  um com sua ação; nenhum rótulo é fabricado (007/DP-702).
- **Endereço de Participação de outra Pessoa de demonstração**: tratado como inexistente
  (mesma resposta), sem revelar nada (FR-090).
- **Endereço de Seção fora do percurso determinado** (ramo não escolhido, Seção ainda não
  alcançada, adulteração): não é apresentada; a interface leva à Seção atual (FR-055).
- **Envio de Seção que saiu do percurso** (troca de ramo noutra aba): nada é gravado; a
  interface leva à Seção atual com aviso simples (FR-047).
- **Envio de Seção com campos de outra Seção ou Perguntas inexistentes**: desconsiderados
  (FR-046).
- **Escolha única que precisa voltar a ficar sem resposta** (por exemplo, Q48 opcional,
  "deixe em branco"): a interface oferece meio de remover a resposta, sem JavaScript e
  sem apresentá-lo como Opção do instrumento (FR-043).
- **"Outro" marcado sem complemento**: aceito; o complemento é opcional (006 FR-028;
  006/DP-602).
- **Complemento preenchido com "Outro" desmarcado**: erro de preenchimento associado à
  Pergunta; nada da submissão é gravado (005 FR-030).
- **Texto só com espaços**: tratado como campo em branco (FR-041).
- **Q47 = "Não estudei mais" com Q46 = "Sim"**: aceito, sem aviso de contradição
  (002/DP-005).
- **Q6 respondida com Q5 = "Não"**: aceito, sem condição (003/DP-303).
- **Duplo clique em "Salvar" ou "Concluir"**: resultado único; operações idempotentes ou
  atômicas da 005/006; a interface apresenta o estado resultante.
- **Recarregar após envio**: sem repetição de gravação (FR-048).
- **Voltar do navegador para uma Seção já enviada**: a página reapresentada reflete o
  estado atual ao ser solicitada de novo; envio antigo segue as regras acima.
- **Duas abas da mesma Participação**: cada envio é avaliado pela 005/006 no seu momento;
  a última escrita aceita prevalece (005 FR-053); conclusão serializada (006 FR-043).
- **Campanha encerrada entre requisições**: mensagem de período encerrado; nada gravado
  (US13).
- **Participação em rascunho de Campanha encerrada aberta por endereço salvo**: mensagem
  de período encerrado, sem controles de edição.
- **Versão com estrutura não suportada pela 006** (não ocorre na baseline): "pesquisa
  indisponível no momento", sem detalhes técnicos.
- **Seção sem título na Versão** (S13): a página mantém estrutura de títulos coerente sem
  inventar título como se fosse conteúdo do instrumento.
- **Texto explicativo com orientação condicional** (Q48: "deixe em branco"): apresentado
  como texto da Versão; a interface não o transforma em regra.
- **Listas longas de Opções** (por exemplo, cursos em S4–S7): apresentadas de forma
  acessível; a forma de apresentação deriva do tipo e da quantidade de Opções, nunca da
  identidade da Pergunta (FR-036).
- **JavaScript desativado**: todas as histórias P1 e P2 funcionam.

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII): **[Herdado]** comportamento do instrumento vigente
(inventário); **[PAEG]** com artigo; **[Const. — n]** decorre diretamente da
Constituição; **[00n FR-x]** decorre de contrato de feature anterior; **[Arquitetura]**
decisão de modelagem; **[Hipótese]** escolha reversível de produto; **[Escopo]**
delimitação desta feature; **[Solicitante]** requisito explícito do pedido desta feature.

### Functional Requirements

**Modo de demonstração e fronteira de exposição**

- **FR-001**: Toda a interface desta feature — entrada de demonstração, formações,
  Seções, conclusão, confirmação e mensagens — DEVE existir somente quando o **modo de
  demonstração** estiver explicitamente ativado na configuração do ambiente. Ele DEVE
  estar desativado por padrão. Desativado, nenhuma página desta feature DEVE responder
  (página não encontrada). [Const. — XV, XVI; 005 FR-058; 006 FR-054; 007 FR-049]
- **FR-002**: O modo de demonstração DEVE ser destinado exclusivamente a ambiente local de
  desenvolvimento, teste ou demonstração interna com dados fictícios. A documentação DEVE
  declarar que ele NÃO DEVE ser ativado em ambiente acessível a egressos ou com dados
  reais. [Const. — XVI; 001/DP-009; 005/DP-504]
- **FR-003**: Todas as telas desta feature DEVEM exibir, de forma permanente e
  perceptível também por tecnologia assistiva, que se trata de **ambiente de
  demonstração com dados fictícios, sem autenticação**, e que a escolha de Pessoa não
  comprova identidade. [Solicitante; Const. — XV]
- **FR-004**: A entrada de demonstração NÃO DEVE ser apresentada, nomeada ou estruturada
  como login, cadastro, conta ou autenticação. NÃO DEVEM existir senha, CPF, e-mail,
  matrícula, OTP, link mágico, Gov.br, SSO, recuperação de acesso nem qualquer campo para
  identificar-se. [Solicitante; Const. — XV; 007 FR-002]
    *(Revisado pela 018)* A entrada passa a confirmar CPF e nascimento fictícios, com
  advertência explícita sobre sua garantia (018 FR-060, FR-061).

- **FR-005**: A entrada de demonstração DEVE ser um **adaptador substituível**: o restante
  da interface DEVE depender apenas de "qual é a Pessoa resolvida", de modo que uma futura
  fronteira de identidade a substitua sem alterar Participação, Jornada, Respostas,
  Campanha nem as telas de formações, Seção, conclusão e confirmação. [Const. — XV;
  007 FR-001]
- **FR-006**: Esta feature NÃO DEVE criar modelo de usuário, conta, perfil, papel,
  permissão, vínculo usuário ↔ Pessoa nem qualquer estrutura desenhada em torno da
  entrada de demonstração. [Solicitante; Const. — XV, XXII; 007 FR-048]

**Entrada de demonstração (Pessoa fictícia)**

- **FR-007**: A entrada de demonstração DEVE listar as Pessoas do NIAE disponíveis para
  demonstração e permitir escolher uma. Para cada uma DEVE mostrar apenas informação
  humana suficiente para distingui-las: o nome, quando informado (senão, "Pessoa fictícia
  sem nome informado"), e um resumo das suas formações a partir dos atributos das
  Conclusões. NÃO DEVEM ser mostrados UUID, fonte, identificador externo, código
  `SIM-…`, Campanha ou qualquer identificador técnico. [Solicitante; Const. — XVI;
  001 FR-005]
    *(Revisado pela 018)* O seletor é substituído pelo formulário de confirmação e pelo painel
  de credenciais da fonte simulada (018 FR-060).

- **FR-008**: Somente Pessoas incorporadas da **fonte simulada** DEVEM ser listadas e
  aceitas como Pessoa de demonstração. Pessoa de qualquer outra fonte NÃO DEVE ser
  listada nem aceita, ainda que referenciada diretamente. [Const. — XVI; 001 FR-028;
  Arquitetura]
    *(Revisado pela 018)* A entrada recusa qualquer base com Pessoa de fonte diferente da
  simulada, preservando a barreira da demonstração (018 FR-005).

- **FR-009**: A escolha da Pessoa de demonstração NÃO DEVE criar nem alterar registro de
  domínio. O único estado mantido entre requisições pela entrada de demonstração DEVE ser
  a referência à Pessoa de demonstração em uso. Esse estado NÃO DEVE ser modelo de
  domínio nem tabela nova; NÃO DEVE conter formação, Campanha, Participação, Seção,
  posição, seleção ou progresso. O mecanismo concreto pertence ao plan.
  [Solicitante; Const. — XVI, XXII; 006 FR-005; 007 FR-037]
- **FR-010**: A cada requisição, a Pessoa de demonstração referenciada DEVE ser
  revalidada (existe e é da fonte simulada). Se não for válida, a interface DEVE voltar à
  entrada de demonstração, sem erro técnico. [Arquitetura; Const. — XVI]
- **FR-011**: DEVE existir forma de trocar de Pessoa de demonstração e de encerrar a
  demonstração a partir de qualquer tela. [Solicitante]

**Cenário de demonstração (dados fictícios)**

- **FR-012**: DEVE existir um passo **explícito, local e documentado** para preparar o
  cenário de demonstração num banco local. Ele NÃO DEVE ser executado automaticamente
  (por migração, inicialização da aplicação, primeira requisição ou implantação) e NÃO
  DEVE fazer parte de migrações de domínio. [Solicitante; Const. — XXVII]
- **FR-013**: O preparo DEVE usar exclusivamente as operações existentes: incorporação
  pela fonte simulada (001), materialização da baseline (003), cópia e publicação de
  Versão (002), criação, configuração e abertura de Campanha (004). NÃO DEVE criar
  Pessoa, Conclusão, Participação ou Resposta por outro meio nem gravar Respostas
  fictícias. [001 FR-030; Const. — XXII]
- **FR-014**: O instrumento de demonstração DEVE ser uma **cópia publicada** da baseline
  migrada (003), com as mesmas Seções, Perguntas, Opções, obrigatoriedades,
  encaminhamentos e regras, identificada como de demonstração. A baseline institucional
  DEVE permanecer em RASCUNHO. Essa publicação é técnica e local, como nos testes da 005
  a 007, e NÃO DEVE ser apresentada como publicação institucional. [002/DP-001;
  003 FR-003; Const. — X]
- **FR-015**: O cenário DEVE permitir demonstrar, no mínimo, pela interface:
  (a) uma Pessoa com exatamente uma formação com entrada pendente (entrada resolvida);
  (b) uma Pessoa com duas ou mais formações com entrada pendente (seleção necessária);
  (c) uma Pessoa com formações e nenhuma pesquisa disponível;
  (d) uma formação em ambiguidade operacional (duas Campanhas aplicáveis);
  (e) Pessoas suficientes para demonstrar, sem recriar o banco, a jornada principal e a
  jornada Q1 = "Não".
  As situações "disponível para retomar" e "já concluída" DEVEM ser alcançáveis usando a
  própria interface. A combinação de Campanhas e critérios que produz essas situações
  pertence ao plan. [Solicitante; 007 casos de referência]
- **FR-016**: O preparo DEVE recusar-se a executar quando o modo de demonstração não
  estiver ativado. [Solicitante; Const. — XVI]
- **FR-017**: O preparo DEVE recusar-se a executar quando o banco contiver Pessoas ou
  Conclusões de fonte diferente da simulada, sem alterar nada. [Const. — XVI; Arquitetura]
- **FR-018**: Repetir o preparo NÃO DEVE duplicar Pessoas, Versões ou Campanhas de
  demonstração. Reiniciar a demonstração do zero DEVE ser feito recriando o banco local;
  NÃO DEVE ser criada operação que remova Participações ou Respostas (005 FR-017;
  005/DP-503). Campanhas e Versão de demonstração DEVEM ser identificáveis como de
  demonstração por quem inspeciona o banco. [Const. — VIII, XXII]

**Tela de formações (consumo da 007)**

- **FR-019**: Com uma Pessoa de demonstração em uso, a tela de formações DEVE apresentar
  o resultado da **consulta da situação de entrada da 007**, sem recalcular, filtrar ou
  reclassificar formações, Campanhas aplicáveis ou situações. [007 FR-017 a FR-023;
  Const. — XXII]
- **FR-020**: **Entrada resolvida**: a tela DEVE contextualizar a formação pendente
  ("Esta pesquisa refere-se a …") e oferecer **uma única** ação — "Iniciar a pesquisa"
  quando disponível para iniciar, "Continuar a pesquisa" quando disponível para retomar —
  sem pedir escolha de formação. Outras formações da Pessoa PODEM aparecer como
  informação, com sua situação, sem ação. [Solicitante; 007 FR-020; Const. — XIV] *(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`.)*
- **FR-021**: **Seleção necessária**: a tela DEVE perguntar sobre qual formação o egresso
  responderá e oferecer uma ação para cada formação com entrada pendente, na ordem
  devolvida pela 007, sem destaque, pré-seleção, sugestão ou ranking. Formações
  concluídas ou ambíguas PODEM aparecer como informação, sem ação. [007 FR-021] *(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`.)*
- **FR-022**: **Sem entrada pendente**, **sem pesquisa disponível** e **sem formação
  disponível**: a tela DEVE informar a situação em linguagem simples, sem ação de
  preenchimento e sem tratá-la como erro. [007 FR-018, FR-019, FR-022]
- **FR-023**: A situação de cada formação DEVE ser apresentada assim: já concluída →
  "pesquisa já respondida"; ambiguidade operacional → "a pesquisa referente a esta
  formação não está disponível neste momento"; sem pesquisa → "sem pesquisa disponível
  no momento". NÃO DEVEM ser nomeadas, contadas ou descritas Campanhas, nem expostos
  critérios ou motivos de inelegibilidade. [007 FR-015, FR-028; 007/DP-701] *(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`.)*
- **FR-024**: A apresentação DEVE ser sempre da **formação**. NÃO DEVE ser pedido ao
  egresso que escolha Campanha nem mostrado nome, período, identificador ou existência
  de Campanha. [Const. — VII, XIV; 007 FR-028]

**Contexto da formação**

- **FR-025**: O contexto de uma formação DEVE ser lido da Conclusão Acadêmica, usando os
  atributos disponíveis: curso, unidade, ano (ou data) de conclusão e, quando úteis para
  distinguir, nível e modalidade (e forma de oferta). [Solicitante; 007 FR-007;
  Const. — XI, XIV]
- **FR-026**: Atributo não informado DEVE ser omitido ou indicado como não informado.
  NÃO DEVE ser preenchido com valor padrão, deduzido de outro atributo ou de outra
  formação, nem substituído por texto fabricado. Formação sem nenhum atributo informado
  continua apresentável e distinta, com texto neutro. [007 FR-009, FR-010; 007/DP-702]
- **FR-027**: O contexto da formação DEVE aparecer também nas telas de Seção, de
  conclusão e de confirmação, visualmente e semanticamente separado das Perguntas, como
  informação institucional. [Const. — III, XIV; 005 FR-044]
- **FR-028**: O contexto da formação NÃO DEVE ser gravado como Resposta, usado para
  pré-preencher, sugerir, destacar, ocultar ou pular Perguntas (em particular Q10–Q19),
  nem comparado com respostas declaradas. [Const. — III; 003/DP-307; 005 FR-042;
  006 FR-007; 007 FR-040 a FR-042]

**Entrada na Participação (consumo da 007/005)**

- **FR-029**: As ações de iniciar ou continuar DEVEM chamar exclusivamente a **entrada
  da 007** — sem formação quando a situação é "entrada resolvida"; com a formação
  escolhida quando é "seleção necessária". A interface NÃO DEVE criar Participação nem
  chamar a operação de início da 005 diretamente. [Solicitante; 007 FR-029 a FR-033]
- **FR-030**: Conforme o resultado da entrada: **iniciada** ou **em rascunho** → levar à
  Seção atual da 006; **concluída** → tela "pesquisa já respondida"; situação sem
  Participação (sem pesquisa, ambiguidade, seleção necessária, sem entrada pendente) →
  tela de formações com a situação atual; formação que não pertence à Pessoa → "formação
  não disponível", sem detalhe; rejeição da 005 propagada (coleta não admitida) →
  "período de resposta encerrado". [007 FR-030, FR-031, FR-034, FR-044, FR-046]
- **FR-031**: Ver a tela de formações, abrir uma Seção ou recarregar páginas NUNCA DEVE
  criar Participação. Somente as ações explícitas de iniciar ou continuar podem levar à
  entrada. [Const. — XVI; 007 FR-024; Arquitetura]

**Apresentação da Seção**

- **FR-032**: A tela de Seção DEVE apresentar uma Seção do percurso determinado da 006,
  com o título e o texto introdutório da Seção quando existirem e, em seguida, **todas**
  as suas Perguntas, na ordem da Versão aplicada. Na primeira Seção da Versão, o texto de
  abertura da Versão, quando existir, DEVE acompanhá-la. [006 FR-010, FR-047 c;
  Herdado — texto de abertura; Const. — XIII] *(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`.)*
- **FR-033**: Textos de Versão, Seção, Pergunta, Opção, texto explicativo e rótulos de
  escala DEVEM ser apresentados exatamente como na Versão aplicada, inclusive grafias
  preservadas pela 003, e escapados como texto. Rótulo ausente NÃO DEVE ser inventado
  (003/DP-301). NÃO DEVE ser mostrada numeração Q1…Q54. [Const. — VIII, XIII; 002 FR-033]
- **FR-034**: A renderização DEVE derivar exclusivamente do tipo e dos dados de cada
  Pergunta da Versão. NÃO DEVE existir tela, componente, texto, condição ou
  comportamento específico de uma Pergunta, Seção ou Opção particular (por exemplo, Q1,
  Q14, Q33, Q46). [Solicitante; Const. — XXIII]
- **FR-035**: Os quatro tipos DEVEM ter controles próprios: **escolha única** — uma
  seleção exclusiva entre as Opções; **escolha múltipla** — seleções independentes;
  **texto curto** — campo de uma linha, sem máscara nem validação de formato; **escala**
  — seleção exclusiva entre os pontos inteiros do início ao fim, com os rótulos de
  extremidade existentes. [002 FR-034 a FR-038; 005 FR-023 a FR-027]
- **FR-036**: A forma visual do controle de escolha única PODE variar conforme a
  quantidade de Opções, por critério genérico definido no plan, para reduzir carga em
  listas longas. O critério NÃO DEVE depender da identidade da Pergunta e DEVE manter
  acessibilidade e funcionamento sem JavaScript. [Const. — XIV, XX; 002 FR-035]
- **FR-037**: A Opção que admite complemento textual DEVE ter um campo de texto associado
  a ela, identificado como complemento daquela Opção. [Herdado — Q26, Q32, Q45;
  002 FR-042; 005 FR-029]
- **FR-038**: A obrigatoriedade de cada Pergunta DEVE ser indicada conforme a Versão, por
  texto e de forma exposta a tecnologias assistivas, sem depender de cor. A indicação é
  informativa: NÃO DEVE impedir o envio da Seção nem constituir verificação própria de
  obrigatoriedade. [Solicitante; 006 FR-019, FR-021]
- **FR-039**: Ao abrir uma Seção de Participação em rascunho, cada Resposta atual DEVE
  aparecer no seu controle: Opção, conjunto de Opções, complemento, texto exatamente como
  gravado e ponto de escala. Perguntas sem Resposta aparecem sem valor. [Solicitante;
  005 FR-047; 006 FR-047 c]

**Salvar a Seção (consumo da 005) e erros de preenchimento**

- **FR-040**: O envio de uma Seção DEVE ser traduzido, para cada Pergunta da Seção, em
  exatamente uma das operações da 005 — registrar/substituir com o valor recebido, ou
  remover — ou em nenhuma, quando nada mudou. NÃO DEVE haver gravação de Resposta por
  outro meio. [Solicitante; 005 FR-033; 006 FR-031]
- **FR-041**: Campo de texto vazio ou contendo apenas espaços, escolha múltipla sem
  Opção marcada e escolha única ou escala sem seleção DEVEM significar **ausência de
  Resposta**: se havia Resposta, ela DEVE ser removida pela 005; se não havia, nada é
  feito. [Hipótese; 005 FR-025, FR-026]
- **FR-042**: Texto não vazio DEVE ser enviado à 005 exatamente como recebido, sem
  aparar, normalizar ou converter. [005 FR-026]
- **FR-043**: DEVE ser possível deixar sem Resposta qualquer Pergunta **não obrigatória**,
  inclusive de escolha única e de escala, sem JavaScript — também antes de gravar, para
  desfazer uma marcação por engano. O meio de remoção NÃO DEVE ser apresentado como Opção
  do instrumento nem gravado como Resposta. Em Pergunta obrigatória, a Resposta é trocada
  pelo próprio controle; remover só produziria uma pendência. [Const. — XIII, XIV;
  005 FR-033 c] *(Revisado após a auditoria de UX de 2026-10-01, UX-02/UX-03: oferecida
  em toda Pergunta respondida, a caixa poluía as Seções revisitadas e, nas obrigatórias,
  só levava a erro.)*
- **FR-044**: A interface DEVE validar a **forma** dos dados recebidos antes de chamar a
  005 (Opção pertencente à Pergunta apresentada, ponto de escala existente, complemento
  só com a Opção correspondente marcada, valores bem formados). Essa validação NÃO DEVE
  acrescentar regra à 005: o que a 005 aceita, a interface aceita; o que a 005 rejeita é
  apresentado como erro de preenchimento. [Solicitante; 005 FR-023 a FR-030, FR-054]
- **FR-045**: A submissão de uma Seção DEVE ser **atômica**: se houver qualquer erro de
  preenchimento ou rejeição da 005 (inclusive coleta não admitida ou Participação
  concluída), **nenhuma** Resposta daquela submissão DEVE ficar gravada. Respostas
  gravadas antes da submissão DEVEM permanecer intactas. [Solicitante; 005 FR-051;
  Const. — XXVI]
- **FR-046**: Somente Perguntas da Seção apresentada DEVEM ser processadas. Campos que
  não correspondam a Perguntas dessa Seção DEVEM ser desconsiderados. Nenhum campo
  oculto ou valor enviado pelo navegador DEVE ser usado para decidir Pessoa,
  Participação, Campanha, Versão, percurso ou autorização. [Solicitante; Const. — XVI]
- **FR-047**: Uma submissão só DEVE ser aceita para Seção que pertença ao percurso
  determinado da Participação **no momento da submissão**, segundo a 006. Caso contrário,
  nada DEVE ser gravado e a interface DEVE levar à Seção atual com aviso simples.
  [006 FR-047; Arquitetura]
- **FR-048**: Após um envio aceito, recarregar ou navegar de volta NÃO DEVE repetir a
  gravação nem pedir reenvio de formulário. [Arquitetura]
- **FR-049**: Em caso de erro de preenchimento, pendência ou rejeição, a mesma Seção DEVE
  ser reapresentada com os valores informados na submissão, um resumo no topo com
  ligações para as Perguntas afetadas e uma mensagem compreensível associada a cada
  Pergunta. [Solicitante; Const. — XX] *(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`.)*

**Obrigatoriedade e navegação (consumo da 006)**

- **FR-050**: Após cada envio aceito, a interface DEVE consultar a **jornada da 006** e
  agir somente sobre o resultado: se a Seção enviada não pode ser deixada, reapresentá-la
  com as **pendências indicadas pela 006**; se pode, apresentar o **destino** dessa Seção
  calculado pela 006 — outra Seção ou, quando o destino é a finalização, a tela de
  conclusão. [Solicitante; 006 FR-012, FR-014, FR-019, FR-047 d] *(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`.)*
- **FR-051**: A interface NÃO DEVE calcular destino, avaliar regra, encaminhamento ou
  ordem de Seções, nem decidir obrigatoriedade no percurso. NÃO DEVE existir, no código
  ou nos modelos de tela da interface, condição sobre resposta a Pergunta específica
  (por exemplo, "se Q14 = …", "se Q33 = …", "se Q46 = …", "se Q1 = Não"). [Solicitante;
  006 FR-006, FR-012, FR-013; Const. — XXIII]
- **FR-052**: Ao entrar ou retomar, e sempre que nenhuma Seção específica for pedida, a
  interface DEVE apresentar a **Seção atual** da 006 ou, se a jornada estiver finalizada,
  a tela de conclusão. [006 FR-047 e; 006 US8]
- **FR-053**: Mensagens de pendência DEVEM corresponder exatamente às Perguntas
  pendentes indicadas pela 006 para a Seção. Perguntas obrigatórias de Seções fora do
  percurso NUNCA DEVEM ser apresentadas nem cobradas. [006 FR-020, FR-030]
- **FR-054**: O egresso DEVE poder voltar a qualquer Seção do percurso determinado
  anterior à atual, revisar e alterar respostas, e seguir de novo pelos destinos
  calculados pela 006. A interface DEVE deixar claro se voltar grava ou não as alterações
  não enviadas da Seção em tela; respostas já gravadas NUNCA DEVEM ser perdidas por
  navegação. [006 US8.3; Const. — XIV]
- **FR-055**: Seções fora do percurso determinado NÃO DEVEM ser apresentadas, nem suas
  Respostas (inativas). Pedido de Seção fora do percurso DEVE levar à Seção atual.
  [006 FR-030, FR-047 f]

**Conclusão (consumo da 006)**

- **FR-056**: A tela de conclusão DEVE ser apresentada somente quando a 006 indicar
  jornada finalizada para Participação em rascunho. Pedido da tela de conclusão com a
  jornada não finalizada DEVE levar à Seção atual. [006 FR-047 e, g]
- **FR-057**: A ação "Concluir pesquisa" DEVE chamar exclusivamente a **operação de
  conclusão da 006**. A interface NÃO DEVE registrar momento de conclusão, remover
  respostas fora do percurso nem validar o percurso por conta própria. [Solicitante;
  006 FR-034, FR-035]
- **FR-058**: Conclusão aceita ou "já concluída" DEVE levar à confirmação. Conclusão
  rejeitada DEVE ser traduzida em mensagem: coleta não admitida → período encerrado;
  pendência → Seção atual com pendências; estrutura não suportada ou incoerência →
  pesquisa indisponível no momento, sem detalhe técnico. [006 FR-036, FR-037]
- **FR-059**: Para Q1 = "Não", a interface DEVE apenas seguir a 006: jornada finalizada
  → tela de conclusão → confirmação. NENHUMA tela ou mensagem DEVE apresentar isso como
  consentimento negado, recusa jurídica, opt-out ou bloqueio futuro, nem a resposta "Sim"
  como consentimento juridicamente válido. [006 FR-022 a FR-024; 005 FR-057;
  Const. — XVII, XXIX]
- **FR-060**: A tela de conclusão DEVE informar, em linguagem simples, que depois de
  concluída a pesquisa não poderá ser alterada e DEVE permitir revisar Seções do percurso
  antes de concluir. [Hipótese; Const. — XIV; 006 FR-039]
- **FR-061**: A tela de conclusão NÃO DEVE apresentar resumo das respostas declaradas.
  [Solicitante; Const. — XVI]

**Confirmação e Participação concluída**

- **FR-062**: A confirmação DEVE ser simples: "Pesquisa concluída", agradecimento, o
  contexto da formação e, se existir, o texto de encerramento da Versão. [Solicitante;
  Herdado — texto de encerramento] *(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`.)*
- **FR-063**: A confirmação NÃO DEVE conter resumo de respostas, valores declarados,
  certificado, comprovante, protocolo, PDF, download, identificador técnico, nem ação de
  editar ou reabrir. [Solicitante; Const. — XVI; 006/DP-603]
- **FR-064**: Para Participação concluída, toda tela de Seção, de conclusão ou ação de
  envio DEVE resultar na informação "pesquisa já respondida", sem formulário e sem
  valores declarados. NÃO DEVE existir controle de edição, botão de reabrir nem caminho
  para nova Participação na mesma Campanha. [Solicitante; 006 FR-038 a FR-041;
  006/DP-603]

**Campanha que deixa de admitir escrita**

- **FR-065**: A interface NÃO DEVE avaliar período, estado de Campanha ou prazo. Quando a
  005 ou a 006 rejeitar por coleta não admitida, ou a jornada indicar que a escrita não é
  admitida, a interface DEVE informar que o período de resposta foi encerrado e que as
  respostas salvas anteriormente foram preservadas, sem controles de edição.
  [Solicitante; 005 FR-039, FR-041; 006 FR-040, FR-042]
- **FR-066**: NÃO DEVE existir prazo adicional, tolerância, gravação local para envio
  posterior ou qualquer contorno do encerramento. [005/DP-502; Const. — XXIX]

**Mensagens, erros e estados vazios**

- **FR-067**: Toda mensagem ao egresso DEVE usar linguagem simples, em português, e
  indicar o que aconteceu e o que é possível fazer em seguida. [Solicitante;
  Const. — XIV, XX]
- **FR-068**: Mensagens e páginas NÃO DEVEM expor rastreamento de erro (traceback),
  nomes de modelos, motivos ou códigos internos de rejeição, UUID, identificadores
  externos, nomes de Campanha ou detalhes de banco. Resultados previstos (rejeições,
  estados vazios, situações da 007) NUNCA DEVEM resultar em página de erro técnico.
  [Solicitante; Const. — XVI]
- **FR-069**: Falha inesperada DEVE resultar em página genérica, com caminho de volta ao
  início, sem detalhes técnicos, quando a aplicação não estiver em modo de depuração. O
  registro técnico da falha segue FR-085. [Solicitante]
- **FR-070**: Erros de preenchimento DEVEM ser específicos do tipo: escolha inválida →
  "selecione uma das opções apresentadas"; ponto de escala inválido → "selecione um valor
  da escala"; complemento sem a Opção → indicar que é preciso marcar a Opção a que o
  complemento se refere, nomeando-a pelo texto da Versão; pendência → "esta pergunta é
  obrigatória". O texto exato pertence ao plan e à revisão de linguagem (DP-801).
  [Arquitetura]

**Acessibilidade e responsividade**

- **FR-071**: Toda página DEVE declarar o idioma português, ter título de página único que
  identifique a etapa (e indique a existência de erros, quando houver) e estrutura de
  títulos em hierarquia coerente. [Const. — XX; WCAG 2.1 AA] *(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`.)*
- **FR-072**: DEVE ser usado HTML semântico: regiões de cabeçalho, conteúdo principal e
  rodapé; formulários com botões reais; Perguntas de escolha e de escala agrupadas com o
  enunciado como legenda do grupo; listas para listas. [Const. — XX]
- **FR-073**: Todo controle DEVE ter rótulo visível e programaticamente associado. Texto
  explicativo e mensagens de erro DEVEM estar associados ao controle ou grupo a que se
  referem. [Const. — XX]
- **FR-074**: Toda funcionalidade DEVE ser operável só por teclado, em ordem lógica, sem
  armadilha de foco, com **foco sempre visível**. DEVE existir atalho para pular ao
  conteúdo principal. [Const. — XX]
- **FR-075**: Informação NÃO DEVE depender somente de cor. O contraste de texto e de
  componentes DEVE atender WCAG 2.1 AA. [Const. — XX]
- **FR-076**: Ao reapresentar uma Seção com erros ou pendências, o resumo DEVE ser
  anunciado a tecnologias assistivas ou receber o foco, e cada item DEVE levar à Pergunta
  correspondente. [Const. — XX] *(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`.)*
- **FR-077**: As páginas DEVEM ser responsivas: utilizáveis de 320 pixels CSS de largura
  até desktop, sem rolagem horizontal da página, com largura de linha confortável para
  leitura, controles com área de toque adequada e suporte a ampliação de texto até 200%
  sem perda de conteúdo ou função. [Const. — XXI; WCAG 2.1 AA] *(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`.)*
- **FR-078**: A interface DEVE ser compatível razoavelmente com leitores de tela
  correntes; a verificação é por inspeção, verificação automatizada de acessibilidade e
  roteiro manual de teclado e leitor de tela, sem auditoria completa nesta feature.
  [Solicitante; Const. — XX]

**Natureza técnica da interface**

- **FR-079**: A interface DEVE ser composta de páginas geradas no servidor pela aplicação
  existente, com formulários e navegação comuns. NÃO DEVEM ser criados aplicação cliente
  separada, SPA, React, Vue, Angular, API REST ou GraphQL para alimentar a própria
  interface, nem pipeline de build de frontend. [Solicitante; Const. — XXII, XXIV;
  ADR 0001]
- **FR-080**: Responder, navegar, salvar, concluir, escolher Pessoa e escolher formação
  DEVEM funcionar com JavaScript desativado. Esta feature NÃO DEVE depender de
  JavaScript. [Solicitante]
- **FR-081**: A aparência DEVE ser institucional, neutra e sóbria, sem presumir
  identidade visual do Ifes não documentada no projeto, sem copiar visual de sites
  externos, sem biblioteca de componentes, design system, tema configurável,
  personalização por unidade, animações ou microinterações. [Solicitante; Const. — XXII;
  DP-801]
- **FR-082**: As páginas NÃO DEVEM carregar recursos de terceiros (fontes, folhas de
  estilo, scripts, imagens ou serviços externos). [Const. — XVI; Arquitetura]

**Segurança de formulário**

- **FR-083**: Toda ação que grava ou altera estado (escolher ou trocar Pessoa de
  demonstração, iniciar/continuar, salvar Seção, remover resposta, concluir) DEVE usar
  método de requisição que não seja de consulta e DEVE ter proteção contra requisição
  forjada entre sites. Consultas NÃO DEVEM gravar. Métodos não apropriados DEVEM ser
  recusados. [Solicitante; Const. — XVI]
- **FR-084**: Toda entrada DEVE ser validada no servidor; todo conteúdo — inclusive
  textos do instrumento e valores declarados reapresentados — DEVE ser escapado na
  apresentação. NÃO DEVE ser criado framework próprio de segurança. [Solicitante;
  Const. — XXII]

**Privacidade e observabilidade**

- **FR-085**: Valores declarados, nomes de Pessoas e atributos acadêmicos NÃO DEVEM
  aparecer em logs, endereços (URL), parâmetros de consulta ou mensagens técnicas. Os
  logs técnicos normais da aplicação são suficientes. [Const. — XVI, Observabilidade;
  005 FR-059; 006 FR-046]
- **FR-086**: Endereços NÃO DEVEM conter dados pessoais, nomes, curso, unidade ou
  respostas. Identificadores técnicos opacos PODEM compor endereços quando necessários,
  mas NUNCA DEVEM ser apresentados como conteúdo nem bastar para autorizar acesso. O
  formato dos endereços pertence ao plan. [Solicitante; Const. — XVI]
- **FR-087**: NÃO DEVEM ser adicionados analytics, rastreamento de página, eventos de
  produto, funil, telemetria, Google Analytics, Matomo ou equivalentes. [Solicitante;
  Const. — XVI, XIX; DP-803]
- **FR-088**: Páginas que apresentam valores declarados NÃO DEVERIAM ser armazenadas em
  caches compartilhados. [Const. — XVI]

**Autorização mínima da demonstração**

- **FR-089**: Toda tela e ação sobre uma formação ou Participação DEVE verificar, no
  servidor e a cada requisição, que a formação é da Pessoa de demonstração em uso e que a
  Participação pertence a uma formação dela. [Const. — I, XVI; 007 FR-044]
- **FR-090**: Formação ou Participação que não pertença à Pessoa de demonstração DEVE
  receber a mesma resposta que uma inexistente, sem revelar existência ou atributos.
  A interface NÃO DEVE tentar resolver segurança de identidade por obscuridade de
  identificadores. [Solicitante; 007 FR-044, FR-045]

**Persistência e fronteiras**

- **FR-091**: Esta feature NÃO DEVE criar modelo, tabela ou coluna de domínio. NÃO DEVEM
  ser persistidos: sessão de jornada, cursor, posição, Seção atual, Seções visitadas,
  progresso, contexto de entrada, formação selecionada, Campanha escolhida, rascunho de
  formulário não enviado, usuário de demonstração adicional ou qualquer registro de
  acesso. [Solicitante; Const. — XXII; 006 FR-005, FR-052; 007 FR-037, FR-047]
- **FR-092**: Esta feature NÃO DEVE alterar modelos, operações, contratos ou dados das
  Features 001 a 007. Se o plan identificar lacuna nos contratos para a interface (por
  exemplo, uma consulta de leitura ausente), ela DEVE ser registrada e justificada no
  plan; NÃO DEVE ser suprida com regra de domínio na interface. [Escopo; Const. — XXII]
- **FR-093**: NÃO DEVEM ser criados painel administrativo, telas para CPAEG ou CSAEG,
  gestão de Campanha, editor de instrumento, publicação por tela, indicadores, tabelas
  administrativas, exportação ou funcionalidade do GeN. [Solicitante; Const. — VI, XIX;
  004/DP-402; 002/DP-001]
- **FR-094**: NÃO DEVE ser criado mecanismo real de autenticação, identidade, conta ou
  sessão autenticada, nem integração com Portal do Egresso ou fonte acadêmica real.
  [Solicitante; Const. — V, XV; 004/DP-406]
- **FR-095**: NÃO DEVE ser apresentado indicador de progresso, percentual ou estimativa de
  tempo. [Escopo; 006 "Encaminhadas a features futuras"]
- **FR-096**: Esta feature NÃO DEVE criar framework de wizard, form builder, workflow de
  interface, motor de telas ou abstração genérica de componentes. Os controles dos
  quatro tipos de Pergunta são os únicos elementos reutilizáveis justificados.
  [Solicitante; Const. — XXII, XXIII]

**Testabilidade**

- **FR-097**: Os cenários ponta a ponta E2E-1 a E2E-4 DEVEM ser automatizados por
  requisições HTTP comuns, sem JavaScript, usando as operações reais das Features 001 a
  007, sem dublês da camada de domínio, sem dependência de sistema externo e com momento
  de referência controlável onde a 004 a 006 já o permitem. [Solicitante; Const. — XXV,
  XXVI]
- **FR-098**: DEVE existir verificação automatizada de que a interface segue a 006 para
  uma Versão de teste com estrutura **diferente** da baseline, sem alteração da
  interface. [Solicitante; Const. — XXIII, XXVI]

### Key Entities *(include if feature involves data)*

Nenhuma entidade nova. Entidades consumidas, todas inalteradas:

- **Pessoa** *(001)*: a Pessoa de demonstração, sempre da fonte simulada. Só o nome é
  apresentado.
- **Conclusão Acadêmica** *(001)*: a formação apresentada; fonte do contexto
  institucional exibido.
- **Pesquisa, Versão, Seção, Pergunta, Opção** *(002/003)*: única fonte de textos,
  tipos, ordem e obrigatoriedade apresentados. A Versão de demonstração é uma cópia
  publicada da baseline, criada pelo preparo do cenário.
- **Campanha** *(004)*: nunca apresentada; Campanhas de demonstração criadas pelo preparo
  do cenário.
- **Participação, Resposta** *(005/006)*: criadas, alteradas e concluídas somente pelas
  operações existentes.

**Estado de apresentação, não de domínio**: referência à Pessoa de demonstração em uso
(FR-009). Nenhum outro estado entre requisições.

**Valores derivados, não persistidos**: situação de entrada (007), jornada, Seção atual,
destino, pendências e "pode concluir" (006), estados de tela.

**Entidades deliberadamente não criadas**: Usuario, Conta, Login, Credencial, Perfil,
UsuarioDemo, SessaoDeJornada, Cursor, Progresso, PosicaoAtual, SecaoVisitada,
ContextoDeEntrada, SelecaoDeFormacao, RascunhoDeFormulario, Comprovante, EventoDeUso,
Tela/Passo/Wizard como entidade.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado apresentado ou coletado | Origem (institucional / derivado / declarado) | Fonte | Tratamento |
|------------------------------|-----------------------------------------------|-------|------------|
| Nome da Pessoa de demonstração | Institucional (fictício) | Pessoa (001), fonte simulada | Só apresentação; não identifica |
| Curso, unidade, nível, modalidade, ano/data | Institucional | Conclusão (001) | Lido, nunca copiado para Resposta (FR-028) |
| Situação da formação / de entrada | Derivado | 007 | Não persistido |
| Textos, Opções, escalas, obrigatoriedade | Instrumento | Versão aplicada (002/003) | Exatamente como na Versão (FR-033) |
| Seção atual, destino, pendências, pode concluir | Derivado | 006 | Não persistido |
| Valores informados nos campos | **Declarado** | Egresso fictício, pela interface | Gravados só pela 005 (FR-040) |
| Momento de conclusão | Registro do sistema | 006 | Nunca apresentado como comprovante |
| Pessoa de demonstração em uso | Estado de apresentação | Escolha na entrada de demonstração | Só a referência; revalidada (FR-009, FR-010) |

### Análise de persistência

| Informação que a interface precisa | Pode ser derivada? | De onde | Persistir? |
|------------------------------------|--------------------|---------|------------|
| Quem é a Pessoa em uso | Não (é escolha do demonstrador) | Entrada de demonstração | Só a referência, fora do domínio (FR-009) |
| Formações e situações | Sim | 007 | Não |
| Qual Participação está em preenchimento | Sim | Entrada da 007 / Participação da formação | Não |
| Seção atual / próxima Seção | Sim | 006 | Não |
| Respostas a apresentar nos campos | Sim | 005 | Já persistidas |
| Pendências | Sim | 006 | Não |
| Valores não enviados | Não precisam sobreviver | — | Não (perdem-se ao sair) |
| Estado "concluída" | Sim | `concluida_em` (006) | Já persistido |

**Conclusão**: nenhuma persistência de domínio nova. O único estado entre requisições é
a referência à Pessoa de demonstração, que desaparece com a futura fronteira de
identidade.

### Modelo conceitual

```text
[modo de demonstração ativo?] ── não ──► página não encontrada
        │ sim
        ▼
Entrada de demonstração ── escolhe Pessoa (fonte simulada) ──► referência guardada
        │
        ▼
Formações  ◄── situacao_de_entrada(Pessoa)                         (007, só leitura)
  ├─ sem formação | sem pesquisa | sem entrada pendente → mensagem, sem ação
  ├─ entrada resolvida  → [Iniciar | Continuar]  ─┐
  └─ seleção necessária → [ação por formação]     ─┤
                                                  ▼
                           entrar(Pessoa, formação?)                (007 → 005)
  ├─ iniciada | em rascunho ──────────────────────► Seção atual (006)
  ├─ concluída ───────────────────────────────────► "pesquisa já respondida"
  └─ situação / rejeição ─────────────────────────► mensagem correspondente

Seção S (do percurso, 006) ── enviar ──►
  forma inválida ou rejeição da 005 ──► nada gravado; S reapresentada com erros
  senão: registrar/substituir/remover por Pergunta (005), atomicamente
         jornada ← situacao_da_jornada(Participação)               (006)
         S não pode ser deixada ──► S reapresentada com pendências (006)
         destino(S) = Seção T  ──► T
         destino(S) = finalização ──► Tela de conclusão

Tela de conclusão ── concluir ──► concluir(Participação)          (006)
  concluída | já concluída ──► Confirmação
  coleta não admitida ──► "período encerrado"
  pendência ──► Seção atual com pendências
  estrutura/incoerência ──► "pesquisa indisponível"
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Seguindo apenas o quickstart, quem desenvolve consegue, a partir de um banco
  vazio, preparar o cenário e abrir a entrada de demonstração no navegador com no máximo
  3 comandos além da instalação de dependências.
- **SC-002**: O cenário E2E-1 (16 passos) passa em 100% das execuções automatizadas, sem
  JavaScript e sem dublês de domínio; ao final, a Participação concluída contém
  exatamente as Respostas do percurso final.
- **SC-003**: O cenário E2E-2 passa em 100% das execuções: a Participação concluída por
  Q1 = "Não" tem exatamente 1 Resposta e nenhuma Seção posterior a S1 foi apresentada.
- **SC-004**: Para as 17 combinações de Q1, Q14, Q33 e Q46, a sequência de Seções
  apresentadas pela interface coincide em 100% com os percursos esperados da 003.
- **SC-005**: Para uma Versão de teste com estrutura diferente da baseline, a sequência
  de telas coincide em 100% com o percurso da 006, sem nenhuma alteração da interface.
- **SC-006**: O código e os modelos de tela da interface contêm 0 referências a número,
  texto ou Opção de Pergunta específica e 0 cálculos de destino, elegibilidade, período
  ou obrigatoriedade (verificado em revisão e por busca automatizada de padrões).
- **SC-007**: 100% das gravações de Participação, Resposta e conclusão feitas pela
  interface passam pelas operações da 005, 006 e 007; 0 escritas diretas nos modelos.
- **SC-008**: Ao retomar um rascunho, 100% das Respostas gravadas (nos quatro tipos e
  complementos) aparecem nos seus controles.
- **SC-009**: Em 100% das submissões com erro de preenchimento ou rejeição da 005, o
  banco fica inalterado e os valores informados são reapresentados com mensagem
  associada a cada Pergunta afetada.
- **SC-010**: Depois da conclusão, 100% das tentativas de abrir Seção, abrir a tela de
  conclusão ou reenviar formulário resultam em "pesquisa já respondida", sem controles de
  edição, com a Participação inalterada.
- **SC-011**: Com a Campanha encerrada entre requisições (inclusive no dia seguinte ao fim
  do período), 100% dos envios e conclusões resultam em "período encerrado", com 0
  alterações no rascunho; no último dia do período, os envios são aceitos.
- **SC-012**: Com o modo de demonstração desativado, 100% das páginas desta feature
  respondem "não encontrada" e o preparo do cenário recusa-se a executar; com Pessoas de
  outra fonte no banco, 0 delas aparecem ou são aceitas e o preparo recusa-se.
- **SC-013**: O texto apresentado em 100% das telas contém 0 UUIDs, identificadores
  externos (`SIM-…`), nomes de Campanha, nomes de modelo, códigos de rejeição ou
  tracebacks.
- **SC-014**: 100% dos fluxos P1 e P2 são completados só com teclado; 100% dos controles
  têm rótulo associado; 100% das mensagens de erro e pendência estão associadas aos
  campos; a verificação estrutural automatizada de acessibilidade (idioma, título único,
  um `h1` e hierarquia de títulos, atalho para o conteúdo, rótulos, agrupamento com
  legenda, associações por `aria-describedby`, `aria-invalid`, resumo de erros com
  ligações válidas, ausência de scripts e de recursos externos) passa em 100% das telas,
  com 0 falhas.
- **SC-015**: Todas as telas são utilizáveis a 320 pixels CSS de largura e com texto
  ampliado a 200%, sem rolagem horizontal da página.
- **SC-016**: 0 valores declarados, nomes ou atributos acadêmicos aparecem em logs ou
  endereços durante a execução dos cenários E2E.
- **SC-017**: Ao final da feature, existem 0 modelos, tabelas ou colunas de domínio novas;
  0 alterações em contratos das Features 001 a 007; e 0 mecanismos de autenticação,
  dashboards, editores, APIs próprias, dependências de JavaScript, analytics ou
  recursos de terceiros.

## Assumptions

- **Stack existente**: aplicação Django existente (ADR 0001), com páginas e formulários
  gerados no servidor. A configuração hoje não tem camada web (sem rotas, modelos de
  página, middleware ou arquivos estáticos); acrescentá-la é parte do plan, sem
  frameworks adicionais além do justificado em Complexity Tracking.
- **Somente dados fictícios**: 001/DP-009 e 005/DP-504 continuam bloqueando dados reais;
  a feature é exercida exclusivamente com a fonte simulada e respostas fictícias.
- **Pessoas da fonte simulada**: os cenários de 001 (SIM-P-0001 a SIM-P-0011, com
  homônimos e Pessoa sem nome) bastam para as situações de FR-015; "sem formação" não
  ocorre pela fonte simulada (001 FR-039) e é verificada só em teste automatizado.
- **Versão de demonstração**: a cópia publicada da baseline é obtida pelas operações da
  002, como já fazem os testes da 005 a 007.
- **Período das Campanhas de demonstração**: abrange a data do preparo e uma janela
  razoável definida no plan; vencida a janela, a demonstração é reiniciada recriando o
  banco local.
- **Encerramento durante o preenchimento**: demonstrado por teste automatizado com
  momento de referência controlado; demonstração manual é opcional e, se houver, usa a
  operação de encerramento da 004 fora da interface.
- **Uma pessoa por navegador**: a demonstração considera uma Pessoa de demonstração em
  uso por navegador; abas diferentes compartilham essa escolha.
- **Momento de referência**: o relógio do ambiente, na timezone do projeto, como na 004 a
  007; os testes o controlam como já fazem as features anteriores.

## Relação com outras features

**001** — consumida sem alteração: Pessoas e Conclusões da fonte simulada; nome só para
apresentação; atributos para contexto; incorporação no preparo do cenário.

**002/003** — consumidas sem alteração: a interface renderiza a Versão aplicada; a baseline
continua em RASCUNHO; a demonstração usa cópia publicada local. Q10–Q19 continuam
Perguntas declaradas, apresentadas sem pré-preenchimento (003/DP-307). Q47/Q48 aparecem
com Q46 em S11 (003/DP-302, tratamento da 006).

**004** — consumida indiretamente pela 007, 005 e 006; operações de Campanha usadas só no
preparo do cenário, nunca expostas na interface (004/DP-402).

**005** — consumida sem alteração: única via de gravação e remoção de Respostas.

**006** — consumida sem alteração: jornada (Seção atual, percurso, destino, pendências,
pode concluir, admite escrita) e conclusão.

**007** — consumida sem alteração: consulta da situação de entrada e entrada. A 008 é a
"interface pública de entrada" que a 007 encaminhou a feature futura, em versão de
demonstração.

**Esta feature e as restrições de exposição** (005 FR-058, 006 FR-054, 007 FR-049): elas
continuam válidas para exposição a egressos. A 008 não as revoga: expõe as capacidades
somente em modo de demonstração, com Pessoas da fonte simulada, sem egressos reais
(Decisões desta especificação; FR-001, FR-008).

**Futuras**:

- **Identidade / acesso** substituirá a entrada de demonstração pela fronteira real
  (FR-005), decidindo 004/DP-406 e 005/DP-505.
- **Contextualização do instrumento** (003/DP-307) poderá retirar Q10–Q19 numa Versão
  futura; a interface já apresenta o contexto da formação.
- **Acompanhamento da coleta** e eventuais métricas de uso, se aprovadas (DP-803).

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade (NON-NEGOTIABLE)**: a interface só alcança Participações pela
  007/005; nunca cria segunda Participação para o par nem reutiliza a de outra Campanha
  (FR-029, FR-064).
- **III — Institucional ≠ declarado (NON-NEGOTIABLE)**: o contexto da formação é exibido
  como informação institucional, separado das Perguntas, e nunca vira Resposta, sugestão
  ou pré-preenchimento (FR-027, FR-028).
- **V — Integrações desacopladas (NON-NEGOTIABLE)**: a entrada de demonstração é
  adaptador substituível; nada depende de mecanismo de identidade (FR-005, FR-094).
- **VII — Conceitos distintos (NON-NEGOTIABLE)**: o egresso vê formação; Campanha,
  Versão e Participação não são fundidas nem apresentadas como escolha (FR-024).
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: textos exatamente como na Versão;
  concluída imutável; nenhuma operação de remover Participação (FR-033, FR-064, FR-018).
- **XIII — Instrumento como referência**: renderização derivada do instrumento, sem
  telas por Pergunta, sem alterar textos, obrigatoriedade ou navegação (FR-033, FR-034,
  FR-051); textos de abertura e encerramento preservados (FR-032, FR-062).
- **XIV — Redução de fricção**: uma única formação pendente dispensa escolha (FR-020);
  contextualização em vez de pergunta sobre a formação (FR-025); retomada sem
  redigitação (FR-039); pendências claras (FR-049).
- **XV — Identidade substituível**: nenhuma autenticação; entrada demo isolada e
  substituível (FR-004 a FR-006).
- **XVI — Privacidade (NON-NEGOTIABLE)**: só fonte simulada (FR-008); modo desativado por
  padrão (FR-001); nada em logs ou URLs (FR-085, FR-086); sem analytics ou terceiros
  (FR-082, FR-087); sem resumo de respostas (FR-061, FR-063).
- **XVII — Consentimento**: Q1 apresentada e tratada como Pergunta comum; nada a
  apresenta como consentimento (FR-059).
- **XX — Acessibilidade**: requisitos desde a primeira tela (FR-071 a FR-078).
- **XXI — Responsividade**: 320 px a desktop, zoom 200% (FR-077).
- **XXII — YAGNI**: sem modelo, API, SPA, design system, wizard ou progresso (FR-079,
  FR-081, FR-091, FR-095, FR-096).
- **XXIII — Não é form builder**: só os quatro tipos existentes; nenhum construtor de
  telas (FR-034, FR-096).
- **XXV — Testável sem sistemas externos**: E2E sobre operações reais e fonte simulada
  (FR-097).
- **XXIX — Hipóteses explícitas (NON-NEGOTIABLE)**: escolhas de produto marcadas
  [Hipótese]; consentimento, identidade, edição pós-conclusão, abandono, Q10–Q19,
  analytics e design definitivo permanecem pendentes.

**Tensões identificadas (não são conflitos)**:

- **Exposição × 005 FR-058 / 006 FR-054 / 007 FR-049**: a 008 expõe capacidades em
  páginas. A compatibilidade decorre de que a exposição é só em modo de demonstração,
  local, com Pessoas da fonte simulada, sem egressos reais (FR-001, FR-002, FR-008). Se o
  solicitante entender que mesmo essa exposição exige revisão dessas restrições, a
  correção é documental nas specs anteriores, não de comportamento.
- **XIV × Q10–Q19 perguntadas depois da contextualização**: a tela diz a que curso e
  unidade a pesquisa se refere e, depois, S3 pergunta curso e campus. É deliberado:
  003/DP-307 não foi decidida (007, mesma tensão).
- **XIV × conclusão em tela própria**: acrescenta uma tela, mas evita concluir sem aviso
  de que a pesquisa ficará imutável (006 FR-039) [Hipótese].
- **XVI × rascunho com respostas de ramos abandonados**: a interface não as apresenta
  (FR-055), mas elas continuam gravadas até a conclusão (006 FR-030; 005/DP-503).
- **XX × "sem auditoria completa"**: a feature cumpre requisitos verificáveis de
  acessibilidade, sem certificar conformidade total com WCAG 2.1 AA/eMAG.

Nenhum conflito com a Constituição ou com as Features 001 a 007 foi identificado.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. Pertence de fato ao domínio de acompanhamento? Sim. Apresentar o instrumento versionado
   e conduzir a Participação até a conclusão é a face visível do acompanhamento. A
   entrada de demonstração não pertence ao domínio: é adaptador temporário.
2. É necessária ao ciclo de acompanhamento? Sim. Sem interface, nenhuma Participação é
   respondida.
3. Existe ou está prevista solução institucional mais adequada? Para identidade e Portal
   do Egresso, sim (PAEG Art. 10, I; Art. 13) — por isso ficam fora. Para apresentar a
   Versão histórica e conduzir a jornada, não.
4. Integração seria suficiente? Para identidade, no futuro. Para a jornada, não.
5. A incorporação aumentaria desnecessariamente o acoplamento do núcleo? Não. A
   interface depende só dos contratos das 005 a 007; o domínio não depende da interface.

## Out of Scope *(mandatory)*

- Autenticação, login, senha, CPF, e-mail, OTP, link mágico, Gov.br, SSO, conta, perfil.
- Portal do Egresso; integração acadêmica real; dados reais.
- Aplicação frontend separada, SPA, React, Vue, Angular, API REST ou GraphQL própria,
  pipeline de build de frontend, dependência de JavaScript.
- Design system, biblioteca de componentes, tema, personalização por unidade, identidade
  visual institucional definitiva, animações.
- Painel administrativo, CPAEG, CSAEG, gestão de Campanha, editor, publicação por tela,
  indicadores, tabelas administrativas, exportação, GeN.
- Resumo de respostas, comprovante, certificado, PDF, download.
- Edição pós-conclusão, reabertura, nova tentativa.
- Progresso, percentual, estimativa de tempo.
- Analytics, rastreamento, telemetria, funil.
- Pré-preenchimento ou supressão de Q10–Q19 ou de qualquer Pergunta; alteração da
  baseline, de textos, obrigatoriedade ou navegação.
- Comunicação, convite, lembrete, e-mail.
- Tradução para outros idiomas.
- Novos modelos de domínio; alteração das Features 001 a 007.
- Auditoria completa de acessibilidade.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Numeração: decisões novas usam o prefixo 8 (DP-801…). As das features anteriores são
citadas como 00n/DP-nnn.

**Novas nesta feature**

- **DP-801** — DECISÃO PENDENTE: identidade visual e linguagem institucionais definitivas
  da interface do egresso (marca, cores, tipografia, padrão de governo eletrônico
  aplicável, tom e textos das mensagens). Instância competente: Proex/CPAEG, com a
  comunicação institucional e a área de TI. Impacto: FR-067, FR-070, FR-081. Tratamento
  provisório: interface neutra, sóbria e acessível; mensagens em linguagem simples
  revisáveis sem mudança de comportamento.
- **DP-802** — DECISÃO PENDENTE: se e como o egresso poderá ver ou obter suas próprias
  respostas depois da conclusão (resumo, cópia, comprovante), considerando direito de
  acesso do titular e risco de exposição de dados sensíveis. Instância competente:
  encarregado de dados, com CPAEG. Impacto: FR-061, FR-063. Tratamento provisório:
  nenhum resumo, comprovante ou cópia.
- **DP-803** — DECISÃO PENDENTE: se haverá métricas de uso da jornada (abandono por
  Seção, tempo de preenchimento, funil) e com que base legal, finalidade e ferramenta.
  Instância competente: CPAEG/Proex, com o encarregado de dados. Impacto: FR-087.
  Tratamento provisório: nenhuma métrica; apenas logs técnicos.

**Herdadas e afetadas por esta feature**

- **004/DP-406** e **005/DP-505** — acesso do egresso e quem vê Participações: a 008 usa
  entrada de demonstração restrita a dados fictícios (FR-001 a FR-010). Mantidas abertas.
- **005/DP-504**, **002/DP-007**, **001/DP-009** — base legal, consentimento, termo e
  dados reais: Q1 apresentada como Pergunta comum; nada é registrado como consentimento
  (FR-059). **Continuam bloqueando o uso com dados reais.**
- **006/DP-601** — interpretação da conclusão por Q1 = "Não": a confirmação é a mesma,
  neutra, sem categoria de recusa (FR-059).
- **006/DP-602** — complemento de "Outro" obrigatório: continua opcional na interface.
- **006/DP-603** — edição pós-conclusão: nenhuma (FR-064).
- **005/DP-503** — abandono e retenção de rascunhos: a interface não expira nem remove
  nada; reiniciar a demonstração recria o banco local (FR-018).
- **005/DP-502** — prazo de graça: nenhum (FR-066).
- **007/DP-701** — comunicação da ambiguidade: mensagem neutra provisória (FR-023).
- **007/DP-702** — distinção de formações com atributos insuficientes: só atributos
  existentes, sem rótulo fabricado (FR-026).
- **003/DP-307** — Q10–Q19: continuam Perguntas declaradas, sem pré-preenchimento
  (FR-028).
- **003/DP-301** — rótulo inicial das escalas: não inventado (FR-033).
- **003/DP-302** e **006/DP-604** — Q47/Q48 com Q46: apresentadas juntas, como a 006
  determina.
- **002/DP-001** — publicação de Versão: só cópia local de demonstração (FR-014).

**Herdadas e ainda abertas** (não resolvidas por esta feature)

- **004/DP-404** — Campanhas sobrepostas.
- **005/DP-501** — várias formações elegíveis na mesma Campanha.
- **003/DP-303**, **DP-304**, **DP-309** — Q6, Q42/Q44, dados sensíveis.
- **001/DP-001**, **DP-003** — fonte acadêmica oficial e reconciliação de identidade.
