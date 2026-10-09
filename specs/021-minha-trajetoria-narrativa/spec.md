# Feature Specification: Minha Trajetória — narrativa visual personalizada

**Feature**: `021-minha-trajetoria-narrativa`

**Feature Branch**: `claude/academic-data-structure-c7318c` (a partir da `main` em
`ff12566`, com a 019 mergeada)

**Created**: 2026-10-04

**Status**: P1 e P2 implementadas na demonstração em 2026-10-04 (PR #30). A **P1 visual
foi reaberta** em 2026-10-05 pela
[auditoria de convergência visual](../../docs/auditorias/2026-10-04-021-convergencia-visual.md)
e **reimplementada no mesmo dia**: card editorial por zonas e página em capítulos,
seguindo a seção "Direção visual" e os critérios do SC-015. Os PNGs de referência foram
aprovados pelo solicitante em 2026-10-05. Falta a validação no celular real e no story de
teste (T031, T053). Evidências em [validacao.md](validacao.md).

**Input**: Solicitação da Feature 021 — Minha Trajetória: narrativa visual personalizada.

- Depois de participar, o egresso deixa de ver só "Obrigado por responder". Passa a ver
  sua trajetória acadêmica no Ifes, montada de forma determinística a partir de fatos
  institucionais confiáveis.
- O egresso pode baixar uma representação estática compartilhável.
- Nada é inventado: fatos, datas, eventos, estatísticas ou relações acadêmicas.
- A feature é organizada em P1 (dados de hoje), P2 (enriquecimento institucional
  simulado) e P3 (expansões).

## Contexto

A [auditoria da 021](../../docs/auditorias/2026-10-04-minha-trajetoria-narrativa.md)
inventariou o código, mapeou os dados disponíveis e futuros e criticou o storyboard. Ela
recomendou a arquitetura abaixo. Esta spec a transforma em comportamento.

```text
VIEW / CONSULTA ACADÊMICA (simulada hoje; pode ser uma única view larga no futuro)
        │  o adaptador separa a mesma linha em dois contratos
        │
        ├── FonteAcademica (001, inalterada; também serve à 018 e à 019)
        │      identidade + Conclusões ──► Pessoa / Conclusão Acadêmica
        │
        └── capacidade de contexto da trajetória (P2, separada; só a 021 conhece)
               complemento individual ──► Complemento da Conclusão         (ingresso)
               contexto agregado ───────► Contexto Institucional Agregado  (2 métricas)
                                                │
fatos institucionais + derivados + agregados ───┘
        │
        ▼
TrajetoriaNarrativa   (pura, determinística, serializável; não persistida)
        │
        ├──► página "Minha trajetória no Ifes"                         (P1)
        ├──► card vertical 9:16 → PNG para Instagram e redes sociais   (P1)
        └──► renderer de vídeo                                         (Feature 022, fora desta)
```

### Base existente e evidências

- **Fronteira acadêmica (001):**
  - `ConclusaoNaFonte` traz curso, unidade, nível, modalidade, forma de oferta, ano e data
    de conclusão.
  - Não há ingresso nem agregado.
  - O protocolo só obtém uma Pessoa ou uma Conclusão por identificador. Não lista o
    universo.
  - `CAMPOS_DE_CONTEXTO` deriva do contrato e alimenta a incorporação, a fonte simulada e
    o snapshot da 012.
- **Base local parcial:**
  - A incorporação é sob demanda.
  - A 018 nunca incorpora no login.
  - A 019 incorpora uma Conclusão por vez.
  - Contagem local não representa o universo institucional.
- **012:**
  - FR-040 congela exatamente sete atributos.
  - A research R5 manda falhar se a 001 ganhar atributo, para forçar uma decisão
    explícita.
  - Isso registra o estado atual. Não impede o domínio acadêmico de evoluir: 001 e 012
    podem ser revisadas juntas quando um fato acadêmico novo se mostrar estrutural.
- **Instrumento:**
  - Não há correspondência conceitual estável entre Versões (002 FR-033, 003 FR-012,
    009 FR-103, 012 FR-077, 013 FR-056; pendente em 002/DP-006).
- **Jornada:**
  - A confirmação é simples (008 FR-062/063).
  - A 014 FR-041 permite uma única ação, a ligação para a trajetória (`/formacoes/`,
    intitulada "Sua trajetória no Ifes").
- **Visual:**
  - Tokens da 015 inline, sem `staticfiles`, sem JavaScript.
  - Única marca: a assinatura, com uso fora do sistema pendente (D-03).
  - Nenhuma biblioteca de imagem no projeto.
- **Auditoria de 2026-10-02 (§5):** veda "Sua turma de 2017", comparação social, fatos
  históricos do período, fotos por campus e saudação pelo nome como recurso principal.

### Escolhas desta spec (confirmadas no clarify de 2026-10-04; continuam reversíveis)

- **E1 — Página própria, fora da jornada da pesquisa.**
  - A narrativa vive numa página "Minha trajetória no Ifes".
  - A confirmação continua com "Pesquisa concluída". Sua única ação passa a levar à
    narrativa.
  - O download fica na página nova, nunca na confirmação. A 008 FR-063 continua válida.
- **E2 — Grão: a Pessoa. Gatilho: a Participação concluída.**
  - A narrativa é da Pessoa e reúne todas as suas Conclusões Acadêmicas.
  - Uma Participação concluída ancorada em Conclusão Acadêmica dessa Pessoa libera o
    acesso. Não existe uma trajetória por Participação.
  - Antes da conclusão, a interface só pode antecipar o benefício, sem revelar conteúdo.
  - [Hipótese]
- **E3 — Narrativa derivada na consulta.**
  - É montada a cada consulta a partir dos fatos persistidos naquele momento e de uma
    data de referência explícita.
  - Se novas formações ou enriquecimentos forem incorporados, a próxima consulta fica mais
    rica.
  - O SVG/PNG baixado é o artefato. Não há histórico de narrativas, versão de card nem
    armazenamento de renders.
  - P1 não exige mudança de modelo.
- **E4 — Ingresso como complemento separado** do contexto fundamental (alternativa B da
  auditoria, §5). Fica fora de `CAMPOS_DE_CONTEXTO`, do snapshot, das exportações e dos
  critérios. A razão **não** é a 012 proibir atributo novo para sempre. A razão é que:
  - o ingresso não existe na fonte real conhecida;
  - não é necessário hoje para Campanha, Participação ou snapshot;
  - seu uso inicial é enriquecer a narrativa;
  - o núcleo acadêmico fundamental não deve ser alterado para satisfazer uma composição
    visual.

  Se a integração real mostrar que o ingresso é um fato estrutural usado por vários
  domínios, a decisão é revista junto com 001 e 012.
- **E5 — Agregados numa capacidade própria**, separada de Pessoa e de Conclusão.
  - Duas métricas fechadas, que contam Conclusões, não pessoas.
  - Persistidos e deduplicados.
  - Vêm só da fonte institucional e nunca são calculados da base local.
  - Uma apuração só é usada quando é a única conhecida para a métrica e o recorte.
- **E5a — Enriquecimento por fronteira separada da fonte acadêmica fundamental** (revisão
  do solicitante, 2026-10-04).
  - O complemento (ingresso) e os agregados chegam por uma capacidade de contexto da
    trajetória, distinta da `FonteAcademica`.
  - `obter_pessoa()` e `PessoaEncontrada`, que também servem à 018 e à 019, não mudam.
  - A carga do enriquecimento é separada da incorporação. Falha ou ausência dela nunca
    impede identidade, incorporação ou uso normal do sistema.
  - Um adaptador real pode ler uma única view larga e alimentar os dois contratos. Quem
    separa as responsabilidades é o adaptador, não o banco.
- **E6 — Compartilhar é levar a imagem para fora: salvar ou usar o compartilhamento do
  celular.**
  - O foco é a rede social em formato vertical, especialmente o story do Instagram (9:16).
  - O PNG é o artefato compartilhável principal.
  - O SVG é a representação-base, da qual o PNG é derivado.
  - Não há página pública, link permanente, URL compartilhável nem integração com a API de
    rede social.
  - A única escolha de privacidade é incluir ou não o nome.
- **E7 — Vídeo fica para a Feature 022.** A 021 fecha o contrato serializável que um
  renderer de vídeo consumirá.
- **E8 — Direção visual editorial** (auditoria de convergência visual, 2026-10-05). O card
  e a página são uma **peça editorial da trajetória**, não um relatório. A ambição visual é
  a do mockup de referência: retrospectiva personalizada, com rigor institucional e
  conteúdo determinístico. Ver a seção "Direção visual".

### Direção visual

O card é uma **composição editorial vertical** em zonas, de cima para baixo:

1. **Abertura:** imagem institucional em sangria total, que **absorve o espaço livre do
   quadro**. Leva legenda honesta ("Unidade X · ilustração") e a marca oficial.
2. **Título:** "Minha trajetória / no Ifes", com o nome opcional.
3. **Linha do tempo:** nós, traço, ano em destaque e curso.
4. **Destaques:** até um par de números institucionais em cartões.
5. **Fecho:** frase de pertencimento e hashtag.
6. **Rodapé discreto:** instituição, demonstração e proveniência.
7. **Faixa inferior:** grafismo, sem texto.

A página repete o mesmo vocabulário em **capítulos**:

- **Abertura.**
- **Sua formação.**
- **Sua continuidade no Ifes:** só com duas ou mais formações.
- **Naquele ano no Ifes:** só com agregado.
- **Seu card.**

Um capítulo sem dado não aparece.

**Mesmos dados, outra composição.** A `TrajetoriaNarrativa`, a montagem, a área segura, a
composição adaptativa, o nome opcional e a precisão semântica continuam. Mudam a
apresentação e o catálogo de formulações do card.

Protótipos de referência:
[auditoria, §4](../../docs/auditorias/2026-10-04-021-convergencia-visual.md#4-wireframe-estrutural-do-novo-card).

### Interpretação desta spec

- **"Trajetória" aqui é a trajetória acadêmica registrada pelo Ifes.**
  - Não é trajetória profissional.
  - Não é a resposta da pesquisa.
  - Não é a tela `/formacoes/`, que continua operacional.
- **"Fato institucional" é atributo de uma Conclusão Acadêmica incorporada**, ou de seu
  complemento (P2).
  - Formação Declarada não validada não é fato institucional.
  - Uma validação da 019 que cria Conclusão pelo acervo produz uma Pessoa própria, sem nome.
    A narrativa dela tem só essa Conclusão.
- **"Contexto agregado" é fato sobre um grupo.** Nunca é atributo da Pessoa nem da
  Conclusão.
- **A experiência privada e o card têm conjuntos de conteúdo diferentes.**
  - A página pode mostrar mais: nome, forma de oferta, data, tempo decorrido, ingresso.
  - O card usa só fatos acadêmicos institucionais, derivados seguros e contexto agregado
    seguro.
  - Respostas da pesquisa não entram em nenhum dos dois nesta feature.

## Clarifications

### Session 2026-10-04

- Q: Qual é o grão de "Minha Trajetória": a Pessoa ou a Participação? → A: A Pessoa. A
  Participação concluída é o gatilho de acesso. A narrativa reúne todas as Conclusões
  Acadêmicas da Pessoa. Não há uma trajetória por Participação (E2, FR-001, FR-016).
- Q: A narrativa é fotografia persistida ou visão derivada no momento da consulta? → A:
  Derivada na consulta. Nada de histórico de narrativas, versão de card ou armazenamento
  de renders. O arquivo baixado é o artefato (E3, FR-015).
- Q: Por que o ingresso fica fora de `ConclusaoAcademica`? → A: Porque não existe na fonte
  real conhecida, não é necessário a Campanha, Participação ou snapshot e serve
  inicialmente à narrativa. Não porque a 012 proíba para sempre. 001 e 012 podem ser
  revistas se o ingresso se mostrar estrutural (E4, FR-047).
- Q: Como os agregados devem ser enunciados? → A: Como contagens de Conclusões, nunca de
  pessoas. São vedados "sua turma", "sua geração", "X pessoas se formaram com você",
  "X estudantes estavam matriculados" e equivalentes (FR-024, FR-053, FR-061).
- Q: Qual apuração usar quando houver várias para a mesma métrica e recorte? → A: A menor
  regra determinística: usar o agregado só quando houver exatamente uma apuração conhecida
  para fonte, métrica e recorte. Com mais de uma, omitir. Não há "mais recente" por
  ordenação. A regra institucional de vigência é a DP-2109 (FR-059).
- Q: O nome entra no card? → A: Desmarcado por padrão. Só entra por escolha explícita no
  download. O card funciona sem nome enquanto a DP-2103 estiver aberta. Na página, o nome
  pode aparecer quando disponível (FR-025, FR-034).
- Q: Quando a experiência é liberada? → A: A experiência completa fica disponível depois de
  uma Participação concluída. Antes disso, a interface pode só antecipar o benefício, sem
  revelar conteúdo. O acesso não depende de contato, da 020 nem de compartilhar (FR-001,
  FR-009, FR-070).
- Q: Experiência privada e card têm o mesmo conteúdo? → A: Não. O card usa só fatos
  institucionais, derivados seguros e agregados seguros. Respostas ficam fora do card e da
  página nesta feature (FR-033, FR-035, FR-044).
- Q: O enriquecimento P2 (ingresso, agregados) pode vir na resposta de `obter_pessoa()`? →
  A: Não. `obter_pessoa()` e `PessoaEncontrada` também servem à 018. O enriquecimento vem
  por uma capacidade separada, carregada à parte, cuja falha nunca afeta identidade nem
  incorporação. Uma view larga única continua possível: quem separa é o adaptador (E5a,
  FR-046, FR-055, FR-071).
- Q: Qual é o foco do card? → A: Compartilhamento em rede social no formato vertical,
  especialmente o story do Instagram. Formato 9:16 (1080 × 1920) com área segura. O PNG é o
  artefato principal e o SVG é a representação-base. A prévia é a própria imagem, salvável
  no celular. "Compartilhar" pelo menu nativo é melhoria progressiva (E6, FR-031, FR-040,
  FR-072, FR-073).
- Q: O pior caso (nome longo, quatro cursos longos, agregados) não cabe inteiro na área
  segura com corpo de 40 px. Como o card deve se comportar? → A: Composição adaptativa. Até
  4 formações, tantas quantas couberem, mais "e mais N"; o par de agregados só se couber;
  nada é cortado (FR-033; validacao.md, Fase 3).

### Session 2026-10-05 (auditoria de convergência visual)

- Q: O card atual (texto empilhado, vazio no meio) atende à hipótese da 021? → A: Não. É um
  relatório diagramado. A P1 visual foi reaberta com a direção editorial (E8, FR-074 a
  FR-083, SC-015). A P2 já implementada não muda conceitualmente.
- Q: A marca do Ifes entra no card da demonstração? → A: Sim, a assinatura oficial que o
  sistema já exibe no cabeçalho, sobre pílula clara. A DP-2102 continua aberta para
  produção, com a ACS (FR-036, FR-075).
- Q: De onde vem a imagem institucional? → A: Ilustração vetorial própria e genérica, sem
  licença de terceiros, com legenda "Unidade X · ilustração". O catálogo por unidade fica
  pronto para fotografias licenciadas quando a ACS fornecer (FR-029, FR-076; DP-2106).
- Q: O card tem frase de fecho? → A: Sim. "Essa história também é minha." e a hashtag
  `#SouEgressoIfes`, ambas hipóteses de produto revisáveis. O uso em produção depende da
  ACS (FR-079; DP-2110).

## User Scenarios & Testing *(mandatory)*

### P1 — MVP com os dados existentes

### User Story 1 - Ver a própria trajetória depois de responder (Priority: P1)

A Maria (cenário C) conclui a pesquisa sobre TADS. A confirmação mostra "Pesquisa
concluída" e oferece "Ver minha trajetória no Ifes". Na página, ela vê:

- o que o Ifes registra: duas formações;
- TADS, unidade Serra, Graduação, Presencial, 2022;
- a Especialização em Informática na Educação, Cefor, Pós-graduação, A distância, 2025;
- a frase "Depois dessa formação, você também concluiu Especialização em Informática na
  Educação."

Nada sobre ingresso, turma, emprego ou respostas.

**Why this priority**: É o valor central. Substitui o "obrigado" isolado pelo
reconhecimento do que a instituição já sabe, só com dados que existem hoje.

**Independent Test**: Com a demonstração preparada, identificar a Maria, concluir uma
Participação e abrir a página. Comparar o texto visível com os fatos das duas Conclusões
dela na fonte simulada.

**Acceptance Scenarios**:

1. **Given** a Maria com uma Participação concluída, **When** ela abre a confirmação,
   **Then** vê "Pesquisa concluída", a frase de registro e uma única ação que leva a
   "Minha trajetória no Ifes".
2. **Given** a página aberta, **When** ela lê, **Then** vê as duas formações com os
   atributos informados pela fonte, a contagem "O Ifes registra 2 formações concluídas por
   você" e a frase de continuidade.
3. **Given** o Diego (três formações em 2012, 2017 e 2020), **When** abre a página,
   **Then** vê as três em ordem crescente de ano, com frases de continuidade entre anos
   distintos.
4. **Given** a Ana (uma formação), **When** abre a página, **Then** não há seção "Outras
   formações" nem frase de continuidade.
5. **Given** uma Pessoa identificada sem nenhuma Participação concluída, **When** tenta
   abrir a página, **Then** não a vê e é levada à escolha de formações (`/formacoes/`).
6. **Given** a página aberta, **When** a sessão expira, **Then** nada da narrativa é
   exibido e vale o comportamento de sessão expirada da 018.
7. **Given** a Maria, que concluiu só a Participação sobre TADS, **When** abre a página,
   **Then** a narrativa inclui também a Especialização. A trajetória é da Pessoa, não da
   Participação.
8. **Given** a Maria, que depois conclui também a Participação sobre a Especialização,
   **When** abre a página, **Then** continua existindo uma única narrativa, igual para as
   duas Participações.
9. **Given** um egresso antes de concluir, **When** está na entrada da pesquisa, **Then**
   pode ver um texto fixo da interface antecipando que ao final poderá ver sua trajetória
   no Ifes, sem nenhum conteúdo personalizado da narrativa.

---

### User Story 2 - Narrativa honesta: o que não há, não aparece (Priority: P1)

Uma Conclusão pode ter atributos ausentes: Técnico em Edificações do Bruno, sem data;
Pessoa SIM-P-0009, sem nome. Duas Conclusões podem ter o mesmo ano. Em todos esses casos a
narrativa omite o que falta e não estima nada.

**Why this priority**: A confiabilidade é a condição para a feature existir. Uma única
frase inventada compromete a credibilidade institucional.

**Independent Test**: Montar a narrativa para cenários com atributos ausentes, anos iguais
e data presente ou ausente. Verificar frase por frase contra o catálogo de formulações e a
lista de formulações vedadas.

**Acceptance Scenarios**:

1. **Given** uma Conclusão sem unidade, **When** a narrativa é montada, **Then** nenhuma
   frase menciona campus para ela e nenhum espaço vazio, traço ou "não informado" aparece
   no lugar.
2. **Given** duas Conclusões com o mesmo ano, ou uma sem ano, **When** a narrativa é
   montada, **Then** nenhuma frase diz "antes", "depois", "primeira" ou "em seguida" entre
   elas.
3. **Given** uma Conclusão só com ano (2022) e uma data de referência em 2025, **When** a
   narrativa é montada, **Then** o tempo aparece só pelo ano ("Concluída em 2022"), nunca
   como "há 3 anos".
4. **Given** uma Conclusão com data completa, **When** a narrativa é montada, **Then** o
   tempo decorrido conta anos completos até a data de referência.
5. **Given** uma Pessoa sem nome na fonte, **When** a narrativa é montada, **Then**
   nenhuma saudação ou texto supõe um nome.
6. **Given** a mesma entrada (fatos e data de referência), **When** a narrativa é montada
   duas vezes, **Then** o resultado é idêntico.
7. **Given** qualquer cenário, **When** a narrativa é montada, **Then** não aparece
   ingresso (em P1), período de estudo, turma, coorte, colegas, projeto, bolsa, emprego
   nem resposta da pesquisa.

---

### User Story 3 - Baixar um card da trajetória (Priority: P1)

Ao fim da página, a Maria vê a prévia do card, que é a própria imagem vertical (9:16) que
ela vai postar no story do Instagram. A prévia mostra curso, unidade e ano de cada formação
e, quando nem todas cabem, "e mais N formações registradas". *(Revisado pela convergência
visual, 2026-10-05: a linha com a contagem total de formações saiu do card; a contagem
continua no subconjunto compartilhável e na página.)* Ela pode:

- marcar "incluir meu nome" e atualizar a prévia;
- salvar a imagem no celular, tocando e segurando, ou pelo botão de baixar;
- se o navegador oferecer, tocar em "Compartilhar" e escolher o destino no menu do
  próprio celular. Os destinos dependem do dispositivo e dos aplicativos instalados. O
  sistema não garante que o Instagram apareça; nesse caso, ela salva a imagem e a anexa no
  aplicativo.

A imagem não tem brasão, selo, assinatura de autoridade, QR nem identificador. A assinatura
visual do Ifes (marca) entra pelo FR-075 e não é elemento de autenticação (FR-036; DP-2102).
Na demonstração, leva a indicação de dados fictícios.

**Why this priority**: É a primeira representação compartilhável e fecha o ciclo de
devolutiva. O valor de compartilhamento depende de a imagem caber, sem ajuste, no formato
vertical das redes sociais. Sem ela, a narrativa é só uma página.

**Independent Test**: Gerar o card com e sem nome. Verificar:

- o conteúdo contra o subconjunto compartilhável;
- a ausência de elementos de documento oficial;
- as dimensões 1080 × 1920;
- o conteúdo dentro da área segura;
- o nome neutro do arquivo;
- a identidade byte a byte do SVG para a mesma entrada.

Num celular, salvar a imagem e anexá-la a um story sem recorte.

**Acceptance Scenarios**:

1. **Given** a página da Maria, **When** ela baixa o card sem marcar o nome, **Then** o
   arquivo não contém o nome dela.
2. **Given** a opção "incluir meu nome" marcada e um nome informado pela fonte, **When**
   ela baixa, **Then** o card contém o nome exatamente como a fonte o informa.
3. **Given** uma Pessoa sem nome na fonte, **When** abre a página, **Then** a opção de
   incluir o nome não aparece.
4. **Given** qualquer card, **When** inspecionado, **Then** não contém forma de oferta,
   data completa, tempo decorrido, CPF, data de nascimento, resposta da pesquisa, contato,
   brasão, selo, assinatura de autoridade, QR, identificador nem data de emissão (a
   assinatura visual do Ifes do FR-075 é marca, não autenticação).
5. **Given** a mesma narrativa e a mesma escolha de nome, **When** o SVG é gerado duas
   vezes, **Then** os arquivos são idênticos.
6. **Given** o download, **When** concluído, **Then** o nome do arquivo não contém nome,
   CPF nem curso, e nada do card fica guardado no servidor.
7. **Given** a demonstração, **When** o card é gerado, **Then** ele indica de forma
   visível que os dados são fictícios.
8. **Given** qualquer card salvo no celular, **When** anexado a um story do Instagram,
   **Then** ocupa a tela inteira sem recorte (1080 × 1920, 9:16). Nenhum texto fica nas
   faixas superior e inferior cobertas pela interface do aplicativo.
10. **Given** um navegador com compartilhamento de arquivos, **When** a Maria toca em
    "Compartilhar", **Then** abre-se o menu de compartilhamento do sistema com a imagem.
    Quais destinos aparecem é decisão do dispositivo e não é critério de aceitação.
9. **Given** um celular sem suporte ao compartilhamento nativo, ou com JavaScript
   desligado, **When** a Maria abre a página, **Then** ela vê a imagem e consegue salvá-la
   ou baixá-la. O botão "Compartilhar" simplesmente não aparece.

---

### User Story 4 - A devolutiva não interfere na pesquisa (Priority: P1)

Ver a narrativa ou baixar o card não altera Participação, Respostas, Versão, situação
analítica, snapshot, exportação nem acompanhamento. A participação declarada da 019, sem
validação, não ganha narrativa.

**Why this priority**: Protege os invariantes do NIAE (Princípios I, III, VII e VIII) e
mantém a devolutiva fora do instrumento.

**Independent Test**: Comparar o estado do banco antes e depois de abrir a página e baixar
o card. Repetir o fluxo com uma participação declarada da 019.

**Acceptance Scenarios**:

1. **Given** uma Participação concluída, **When** o egresso abre a narrativa e baixa o
   card, **Then** nenhum registro de Participação, Resposta, Pessoa, Conclusão, snapshot
   ou exportação é criado ou alterado.
2. **Given** uma Participação ancorada em Formação Declarada sem validação, **When** ela é
   concluída, **Then** a confirmação da 019 continua igual e nenhuma narrativa é oferecida.
3. **Given** uma Pessoa criada pelo acervo histórico (019), sem nome, **When** ela tiver
   Participação concluída e abrir a página, **Then** a narrativa mostra só essa Conclusão
   e nenhum nome.
4. **Given** o egresso que não quer ver a narrativa, **When** fecha a confirmação,
   **Then** nada muda para a pesquisa. A narrativa nunca é condição de conclusão.

---

### P2 — Enriquecimento institucional simulado

### User Story 5 - Ingresso, quando a fonte o informa (Priority: P2)

A fonte simulada passa a informar, para algumas Conclusões, o ano de ingresso fictício da
matrícula que resultou nessa Conclusão. Para a Ana, a narrativa diz "Sua trajetória no
Ifes começou em 2019, em Tecnologia em Análise e Desenvolvimento de Sistemas." Para quem a
fonte não informa ingresso, a narrativa continua como em P1.

**Why this priority**: Prepara o contrato para uma futura integração real e valida a UX,
sem afirmar que a fonte real tem esse dado.

**Independent Test**: Incorporar Pessoas simuladas com e sem ingresso. Verificar a frase de
início e sua ausência. Verificar que snapshot, exportação, critérios e divergência de
contexto da 001 continuam iguais.

**Acceptance Scenarios**:

1. **Given** uma Conclusão com ingresso informado, **When** a narrativa é montada, **Then**
   a frase de início usa o ano de ingresso dessa Conclusão.
2. **Given** uma Conclusão sem ingresso, **When** a narrativa é montada, **Then** nenhuma
   frase de início aparece e nenhum ingresso é estimado a partir da duração do curso.
3. **Given** o complemento incorporado, **When** um snapshot da 012 é capturado ou uma
   exportação da 013 é gerada, **Then** o ingresso não aparece em nenhum dos dois e os
   formatos são idênticos aos de antes.
4. **Given** uma Conclusão já incorporada sem complemento, **When** a fonte passa a
   informá-lo, **Then** o complemento é acrescentado sem alterar o contexto da Conclusão.
5. **Given** um complemento já gravado e a fonte informando outro valor, **When** há nova
   carga do contexto, **Then** o valor gravado não muda e a divergência é sinalizada sem
   valores pessoais.
6. **Given** a capacidade de contexto indisponível, **When** uma Pessoa é incorporada e se
   identifica pela 018, **Then** a incorporação, o acesso e a resposta funcionam
   normalmente, e a narrativa aparece sem a frase de início.

---

### User Story 6 - Contexto institucional daquele ano (Priority: P2)

A fonte simulada informa, para TADS na Serra em 2022, a contagem fictícia de conclusões
reconhecidas e a contagem da unidade no ano. A narrativa da Ana mostra:

- "Em 2022, 27 conclusões de Tecnologia em Análise e Desenvolvimento de Sistemas foram
  registradas na unidade Serra, incluindo a sua."
- "Em 2022, 812 conclusões foram registradas na unidade Serra."

Com a referência da apuração. O valor é gravado uma vez e serve à Ana e à Maria. A
narrativa nunca diz "sua turma tinha 27 pessoas" nem "27 pessoas se formaram com você": a
métrica conta Conclusões, não pessoas.

**Why this priority**: Dá contexto sem inventar "turma", com semântica que não se confunde.
Prepara a futura view institucional, sem calcular nada a partir da base parcial.

**Independent Test**: Carregar agregados simulados. Verificar as frases, a deduplicação
(um registro por recorte e apuração), a ausência da seção sem agregado e a recusa de
agregado incoerente.

**Acceptance Scenarios**:

1. **Given** um agregado para o curso, a unidade e o ano de uma Conclusão da mesma fonte,
   **When** a narrativa é montada, **Then** a frase da métrica 1 aparece com o valor e a
   referência da apuração.
2. **Given** duas Pessoas com Conclusões do mesmo recorte, **When** os agregados são
   carregados, **Then** existe um único registro para aquele recorte e aquela apuração.
3. **Given** nenhum agregado para o recorte, **When** a narrativa é montada, **Then** a
   seção não aparece e nenhum número é calculado a partir das Conclusões locais.
4. **Given** um agregado com valor menor que o número de Conclusões da mesma fonte já
   incorporadas naquele recorte, **When** a narrativa é montada, **Then** ele não é exibido
   e a incoerência é sinalizada sem dados pessoais.
5. **Given** duas apurações conhecidas para a mesma fonte, métrica e recorte, **When** a
   narrativa é montada, **Then** aquele agregado é omitido, nenhuma apuração é escolhida
   por ordem temporal e nenhuma é alterada.
6. **Given** uma Conclusão do acervo histórico, **When** a narrativa é montada, **Then**
   nenhum agregado de outra fonte é aplicado a ela.
7. **Given** qualquer agregado, **When** exibido, **Then** nenhuma frase usa "turma",
   "geração", "coorte", "colegas", "pessoas se formaram com você", "matriculados",
   "ingressantes", percentual ou comparação.

---

### P3 — Expansões

### User Story 7 - Segundo tema visual do card (Priority: P3)

O egresso escolhe entre dois temas do card. Os temas compartilham componentes e diferem só
em tokens visuais (cor, composição), nunca em conteúdo.

**Why this priority**: Aumenta o apelo sem tocar o contrato. Depende de P1 estável.

**Independent Test**: Gerar o card da mesma narrativa nos dois temas e verificar que o
texto é idêntico e só os tokens mudam.

**Acceptance Scenarios**:

1. **Given** a mesma narrativa, **When** o card é gerado nos dois temas, **Then** o
   conteúdo textual é idêntico.
2. **Given** qualquer tema, **When** verificado, **Then** o contraste atende WCAG 2.1 AA.

### P3 — Direções registradas, sem requisito nesta feature

Cada direção abaixo exige spec própria, ou a resolução de uma decisão pendente, antes de
virar requisito:

- **Marcos de outras fontes institucionais** (pesquisa, iniciação científica, extensão,
  monitoria, estágio, bolsas, mobilidade): só quando existir fonte. A narrativa já prevê
  uma lista de marcos que fica vazia e não aparece (FR-012).
- **Dados declarados** na narrativa: dependem de correspondência conceitual estável entre
  Versões (DP-2107 = 002/DP-006).
- **Vídeo**: Feature 022, consumindo a mesma `TrajetoriaNarrativa`.
- **Segundo formato do card**: retrato 4:5 (1080 × 1350) para o feed, reutilizando o
  template. Hoje só o vertical 9:16.
- **Imagens institucionais decorativas**: dependem do DP-2106.

### Edge Cases

- **Pessoa com várias Participações concluídas** (uma por formação): uma única narrativa,
  com todas as Conclusões da Pessoa.
- **Participação concluída numa sessão e página aberta em outra sessão da mesma Pessoa**:
  a regra de acesso (E2) vale em qualquer sessão válida.
- **Conclusões com o mesmo curso e o mesmo ano** (por exemplo, dois registros): aparecem
  as duas, sem fusão e sem relação temporal.
- **Fonte informa nível ou curso com vocabulário próprio**: exibido como está, sem traduzir
  nem reclassificar (por exemplo, sem transformar "Pós-graduação" em "Especialização").
- **Data de referência anterior ao ano de conclusão** (relógio inconsistente ou dado
  errado): nenhum tempo decorrido é exibido.
- **Nome da fonte longo** no card: quebra de linha legível. O nome nunca é truncado de
  forma que o altere.
- **Card de Pessoa com muitas formações, ou com textos longos**: o card mostra até 4
  formações, tantas quantas couberem, e informa as demais em "e mais N". Nunca omite uma
  formação em silêncio (FR-033).
- **Agregado com valor 1** (só o egresso): usa a forma singular do catálogo ("1 conclusão
  de {curso} foi registrada na unidade {unidade}: a sua.").
- **Agregado sem referência de apuração**: não é exibido.
- **Várias apurações para a mesma fonte, métrica e recorte**: o agregado é omitido até a
  DP-2109 definir a regra de vigência. Nenhuma é escolhida por data.
- **Nova Conclusão incorporada depois de um download**: a próxima consulta mostra a
  narrativa mais rica. O arquivo já baixado não é rastreado nem atualizado.
- **Fonte de contexto indisponível no momento da carga de agregados ou complementos**: nada
  do enriquecimento é gravado. A Pessoa, as Conclusões e a sessão não são afetadas. A
  narrativa continua com o que já existe, e indisponível nunca vira zero.
- **Pessoa identificada pela 018 cujas Conclusões ainda não foram incorporadas**: não há
  Participação concluída e, portanto, não há narrativa (E2).
- **Participação concluída numa Campanha já encerrada**: a narrativa continua disponível.
  Ela depende da Pessoa e das Conclusões, não da Campanha.

## Requirements *(mandatory)*

Etiquetas de origem (Princípio XIII): [Arquitetura], [Hipótese], [Solicitante],
[Herdado], [PAEG], [Oportunidade].

### Functional Requirements

#### P1 — Acesso e lugar na experiência

- **FR-001**: A página "Minha trajetória no Ifes" DEVE estar disponível somente à Pessoa
  identificada na sessão (018) que tenha ao menos uma Participação concluída ancorada em
  Conclusão Acadêmica dessa Pessoa. A Participação concluída é só o gatilho: existe uma
  única narrativa por Pessoa, nunca uma por Participação. [Hipótese; Solicitante; E2]
- **FR-002**: Quem não atende ao FR-001 DEVE ser levado à escolha de formações, sem
  mensagem que revele a existência ou o conteúdo de uma narrativa. [Arquitetura; 018]
- **FR-003**: A confirmação de Participação concluída ancorada em Conclusão Acadêmica DEVE
  manter o título "Pesquisa concluída" e a frase de registro (014 FR-038). Sua única ação
  DEVE levar à página "Minha trajetória no Ifes". Revisa a 014 FR-041 quanto ao destino da
  ação. [Solicitante; E1]
- **FR-004**: A confirmação NÃO DEVE conter download, prévia do card nem trecho da
  narrativa. A 008 FR-063 permanece. [Herdado; 008 FR-063]
- **FR-005**: A escolha de formações (`/formacoes/`) DEVE oferecer uma ligação para a
  página quando o FR-001 for atendido. As demais regras da 014 FR-035 continuam valendo
  para aquela tela. [Arquitetura]
- **FR-006**: O título da página NÃO DEVE ser igual ao título da escolha de formações
  ("Sua trajetória no Ifes"). [Arquitetura]
- **FR-007**: A confirmação de Participação ancorada em Formação Declarada (019) NÃO DEVE
  mudar e NÃO DEVE oferecer narrativa. [Arquitetura; Const. III]
- **FR-008**: Abrir a página ou baixar o card NÃO DEVE criar nem alterar Participação,
  Resposta, Pessoa, Conclusão Acadêmica, Formação Declarada, validação, snapshot,
  exportação ou qualquer contagem de acompanhamento. [Const. I, VII, VIII]
- **FR-009**: A narrativa NÃO DEVE ser condição para concluir a Participação, NÃO DEVE
  fazer parte da Versão do instrumento e NÃO DEVE depender de contato, de mobilização nem
  da Feature 020. [Solicitante; Const. VII]
- **FR-010**: As respostas da página e do card DEVEM ser sem cache e restritas à sessão,
  como as demais telas do egresso. [Arquitetura; 018]
- **FR-070** *(acrescentado no clarify)*: Antes da conclusão, a interface PODE antecipar o
  benefício com texto fixo da interface (por exemplo, "Ao final, você poderá ver sua
  trajetória no Ifes."), com estas condições:
  - o texto NÃO DEVE fazer parte da Versão;
  - NÃO DEVE conter conteúdo personalizado da narrativa;
  - NÃO DEVE aparecer em Participação ancorada em Formação Declarada;
  - NÃO DEVE condicionar o benefício a contato, à 020 ou a compartilhamento.

  [Solicitante; Hipótese; Const. VII, XXIII]

#### P1 — Narrativa (`TrajetoriaNarrativa`)

- **FR-011**: A narrativa DEVE ser montada por uma função pura e determinística, a partir
  de: (a) a Pessoa e suas Conclusões Acadêmicas incorporadas; (b) em P2, complementos e
  agregados; (c) uma data de referência explícita. Mesma entrada, mesmo resultado.
  [Arquitetura; E3]
- **FR-012**: A narrativa DEVE conter, conceitualmente:
  - a identidade de exibição (nome opcional);
  - as formações;
  - os marcos (vazio nesta feature);
  - os derivados;
  - os contextos agregados (vazio em P1);
  - o subconjunto compartilhável.

  Cada elemento DEVE indicar sua origem: institucional, derivado ou agregado.
  [Arquitetura; Const. III, IV]
- **FR-013**: A narrativa NÃO DEVE conter identificadores técnicos ou de fonte (UUIDs, id
  externo, código da fonte), CPF, data de nascimento, momento de incorporação, Respostas ou
  dados de Formação Declarada. [Const. XVI]
- **FR-014**: A narrativa DEVE ser serializável num formato estruturado estável e
  documentado, consumível por renderizadores diferentes (página, card e, futuramente, a
  022) sem regra de dado no renderizador. [Arquitetura; E7]
- **FR-015**: A narrativa DEVE ser derivada no momento de cada consulta ou renderização, a
  partir dos fatos persistidos naquele momento. Fatos incorporados depois enriquecem a
  próxima consulta. Ficam vedados:
  - persistir a narrativa;
  - manter histórico de narrativas ou versão de card;
  - guardar render (SVG ou PNG) no servidor.

  O arquivo baixado é o único artefato. [Solicitante; Arquitetura; Const. XVI, XXII]
- **FR-016**: A narrativa DEVE reunir todas as Conclusões Acadêmicas da Pessoa da sessão,
  independentemente de qual Participação liberou o acesso, e somente elas. NÃO DEVE unir
  Conclusões de outras Pessoas, mesmo que de outra fonte ou com o mesmo nome.
  [Solicitante; Const. XI; 019]

#### P1 — Conteúdo, derivação e linguagem

- **FR-017**: Cada formação DEVE exibir somente os atributos informados pela fonte, com o
  valor exatamente como incorporado e com a granularidade temporal da fonte (001 FR-011).
  Atributo ausente é omitido, sem traço, sem "não informado" e sem frase que o pressuponha.
  A unidade é exibida como a fonte a informa. "Campus" NÃO DEVE ser acrescentado, porque
  unidades do Ifes incluem campus avançado e Cefor (PAEG, Art. 2º, parágrafo único).
  [Herdado; 001 FR-011; PAEG Art. 2º; Const. III]
- **FR-018**: O derivado "formações registradas" DEVE ser o número de Conclusões da Pessoa
  e DEVE ser enunciado como registro da instituição ("O Ifes registra N formações
  concluídas por você"). Nunca como total de estudos da pessoa. [Arquitetura; Const. III]
- **FR-019**: Uma formação só DEVE ser apresentada como anterior ou posterior a outra
  quando ambas tiverem ano de conclusão e os anos forem diferentes. Entre essas, a ordem
  DEVE ser crescente por ano. As demais aparecem sem relação temporal e sem ser "primeira".
  [Arquitetura]
- **FR-020**: O tempo desde a conclusão DEVE ser contado em anos completos só quando a
  data de conclusão for conhecida e não posterior à data de referência. Só com o ano, DEVE
  ser enunciado apenas pelo ano ("Concluída em AAAA"), sem contagem e sem frase que
  pressuponha o que aconteceu desde então. [Arquitetura; 001 FR-011]
- **FR-021**: Nenhum fato DEVE ser estimado ou inferido. Em especial: ingresso, período de
  estudo, duração do curso, idade, turma, coorte, colegas, eventos do campus, participação
  em projetos, bolsas, situação profissional e "verticalização". [Solicitante; Const.
  III, XXIX]
- **FR-022**: Toda frase da narrativa DEVE vir de um catálogo fechado de formulações. Cada
  formulação DEVE ter condição explícita de uso e DEVE ser preenchida só com valores
  presentes na narrativa. O catálogo DEVE ser revisável como texto, sem mudar
  comportamento. [Arquitetura; Const. XXII]
- **FR-023**: O catálogo inicial DEVE conter, no mínimo, formulações equivalentes a:
  - "Em AAAA, você concluiu {curso} na unidade {unidade}." — com variantes sem unidade ou sem ano;
  - "O Ifes registra N formações concluídas por você.";
  - "Depois dessa formação, você também concluiu {curso}." — sob o FR-019;
  - "Concluída em AAAA." ou "Há N anos desde essa conclusão." — sob o FR-020.

  [Solicitante]
- **FR-024**: A narrativa NÃO DEVE conter formulações como:
  - "Foi aqui que tudo começou" sem ingresso;
  - "Sua turma…", "Sua geração…";
  - "X pessoas se formaram com você", "X estudantes estavam matriculados" ou qualquer
    frase que converta contagem de Conclusões em contagem de pessoas;
  - "Você viveu uma época especial…";
  - "Você foi um dos N melhores…";
  - qualquer comparação com outras pessoas;
  - qualquer afirmação sem fonte.

  [Solicitante; auditoria 2026-10-02 §5]
- **FR-025**: Na página, o nome, quando presente, PODE aparecer de forma discreta. NÃO DEVE
  ser o principal recurso de personalização e NÃO DEVE ser exigido por nenhuma formulação.
  No card, vale o FR-034. [Solicitante; Herdado; auditoria 2026-10-02 §5; 001]

#### P1 — Página (story web)

- **FR-026** *(revisado em 2026-10-05)*: A página DEVE ser organizada em capítulos visuais,
  nesta ordem, cada um só quando houver dado que o sustente:
  1. **abertura:** imagem institucional, título, nome e "o que o Ifes registra";
  2. **sua formação:** primeira formação em destaque e, em P2, a frase de início;
  3. **sua continuidade no Ifes:** só com duas ou mais formações;
  4. **naquele ano no Ifes:** só com agregado selecionado;
  5. **seu card.**

  Um indicador de capítulo ("Capítulo 1 de N") é calculado sobre os capítulos presentes e
  some quando há só um. [Solicitante; E8]
- **FR-027**: Seção sem dado DEVE desaparecer por inteiro, sem título, placeholder,
  "em breve" ou indicação de conteúdo futuro. [Solicitante]
- **FR-028**: A página DEVE funcionar por completo sem JavaScript, em rolagem vertical.
  Melhoria progressiva é opcional, como o compartilhamento nativo do FR-073, e NÃO DEVE
  ser necessária para ler, salvar nem baixar. [Arquitetura; 015; Const. XX, XXI]
- **FR-029** *(revisado em 2026-10-05)*: A página DEVE usar o vocabulário visual da direção
  editorial (E8): imagem institucional, linha do tempo, cartões de destaque. Usa os tokens
  da 015 para texto e ações e o tema do card para os elementos editoriais. Não usa ativos
  externos (CDN). A imagem vem do catálogo do FR-076 e nunca afirma retratar o período do
  egresso. [Solicitante; 015; DP-801; DP-2106]
- **FR-030**: A página DEVE terminar com uma ligação de volta à escolha de formações.
  [Arquitetura]

#### P1 — Card estático

- **FR-031**: O card DEVE ser gerado sob demanda a partir do subconjunto compartilhável da
  narrativa. O vetor (SVG) é a representação-base. A imagem (PNG), derivada do mesmo vetor,
  é o artefato compartilhável principal: é o que a página mostra como prévia e o que o
  egresso salva, baixa ou compartilha. O SVG só é oferecido para download quando o PNG
  estiver indisponível. [Solicitante; Arquitetura]
- **FR-032**: O SVG DEVE ser idêntico byte a byte para a mesma narrativa, o mesmo tema e a
  mesma escolha de nome. O PNG DEVE ser reprodutível nas mesmas condições de geração.
  [Arquitetura]
- **FR-033**: A experiência privada e o card DEVEM ter conjuntos de conteúdo distintos. O
  subconjunto compartilhável padrão DEVE conter só:
  - curso, unidade, nível, modalidade e ano de conclusão de cada formação (fatos
    institucionais);
  - a contagem de formações registradas (derivado seguro);
  - em P2, os agregados exibíveis sob o DP-2105 (contexto agregado seguro). No card, no
    máximo um par de frases (métricas 1 e 2): o da primeira formação, na ordem de
    exibição, que tiver agregado selecionado, e só se couber depois das formações
    exibidas. A página mostra todos.

  **Composição adaptativa** (decisão do solicitante, 2026-10-04): o card mostra até 4
  formações, tantas quantas couberem na área segura com o corpo mínimo. As demais entram em
  "e mais N formações registradas", e nenhuma some sem aviso. Nome e cursos nunca são
  cortados.

  Não DEVE conter forma de oferta, data completa, tempo decorrido, ingresso nem qualquer
  Resposta da pesquisa. [Solicitante; Const. XVI]
- **FR-034**: O nome DEVE entrar no card somente quando o egresso marcar a opção de
  incluí-lo, ao atualizar a prévia ou ao baixar. Por padrão, não entra. A opção NÃO DEVE aparecer quando a
  fonte não informar nome. A escolha NÃO DEVE ser persistida. O card DEVE ser completo e
  gerável sem nome, enquanto a DP-2103 estiver aberta. [Solicitante; DP-2103]
- **FR-035**: O card NÃO DEVE conter Respostas, renda, emprego, situação profissional,
  deficiência, raça/cor, contato, CPF, data de nascimento ou qualquer dado de Formação
  Declarada. [Const. XVI]
- **FR-036** *(revisado em 2026-10-05)*: O card NÃO DEVE conter elemento de documento
  oficial: brasão, selo, assinatura de autoridade, QR, identificador, número, data de
  emissão ou palavras como "certificado", "comprovante" ou "declaração". A **marca do Ifes**
  (assinatura visual oficial) é identidade, não autenticação, e entra pelo FR-075.
  [Herdado; 008 FR-063; DP-2102]
- **FR-037**: Na demonstração, o card DEVE indicar visivelmente que os dados são
  fictícios. [Arquitetura; 016/018/019]
- **FR-038**: O nome do arquivo baixado DEVE ser neutro, sem nome, CPF, curso ou
  identificador. [Const. XVI]
- **FR-039**: O sistema NÃO DEVE oferecer página pública, link permanente, URL
  compartilhável, publicação em rede social nem integração com API de rede social.
  Compartilhar é ação do egresso, com a imagem salva ou pelo menu de compartilhamento do
  próprio celular. O sistema não envia nada a terceiros. [Arquitetura; E6; DP-2101]
- **FR-040** *(revisado em 2026-10-05)*: O card DEVE ter um tema em P1, **próprio e derivado
  da marca** (verde profundo, verde da marca, creme e branco), com contraste AA verificado,
  sem os hex de ação da 015. Formato único: **vertical 9:16, 1080 × 1920 px**, o formato de
  story do Instagram e de status de outras redes. [Solicitante; E8]
- **FR-072** *(revisão de 2026-10-04)*: Todo texto e todo elemento essencial do card DEVE
  ficar dentro de uma área segura central. As faixas superior e inferior, que a interface
  das redes sociais cobre no story, ficam só com fundo ou grafismo. As medidas das faixas
  são definidas no plan. [Solicitante]
- **FR-073** *(revisão de 2026-10-04)*: A página DEVE mostrar o card como imagem (a própria
  PNG, ou o SVG quando o PNG estiver indisponível) que o egresso consiga salvar no celular
  pelo gesto nativo de tocar e segurar, e DEVE oferecer um botão de baixar.
  - A escolha "incluir meu nome" DEVE poder atualizar a prévia antes de salvar, sem
    JavaScript.
  - A página PODE oferecer, como melhoria progressiva, um botão "Compartilhar" que abre o
    menu de compartilhamento do sistema do celular com o arquivo PNG.
    - Ele só aparece quando o navegador suportar compartilhar arquivos, e nunca é o único
      caminho.
    - Os destinos do menu são decididos pelo sistema do dispositivo. Nenhum requisito nem
      critério de aceitação DEVE depender de um aplicativo específico aparecer.
  - [Solicitante; Hipótese; Const. XX, XXI]
- **FR-041**: O card NÃO DEVE incluir foto pessoal, upload de imagem nem conteúdo gerado
  por IA. [Solicitante]

#### P1 — Direção visual editorial (revisão de 2026-10-05; auditoria de convergência visual)

- **FR-074**: O card DEVE ser composto pelas zonas da seção "Direção visual", nesta ordem:
  abertura, título, linha do tempo, destaques, fecho, rodapé, faixa inferior. Zona sem dado
  some (destaques sem agregado; nome sem escolha). As demais se reacomodam.
  [Solicitante; E8]
- **FR-075**: A abertura DEVE trazer a marca oficial do Ifes, a mesma assinatura que o
  sistema exibe no cabeçalho, sobre fundo claro que garanta leitura, dentro da área
  segura. Na demonstração, sim. Para produção, a DP-2102 decide. [Solicitante; DP-2102]
- **FR-076**: A imagem da abertura DEVE vir de um **catálogo de imagens institucionais**.
  - **Escolha:** cada imagem é escolhida pela unidade da primeira formação exibida, com uma
    imagem genérica do Ifes como alternativa obrigatória.
  - **Metadados:** cada entrada DEVE registrar unidade (ou "genérica"), tipo
    ("ilustração" ou "fotografia"), origem e licença.
  - **Legenda:** a imagem DEVE ter legenda visível no card e na página, no formato "Unidade
    X · ilustração" (ou "Ifes · ilustração"). Ela NUNCA traz ano, nem afirma retratar o
    período ou um momento do egresso.
  - **Na demonstração:** só a ilustração vetorial própria e genérica.
  - **Fotografias:** entram só com origem e licença registradas (DP-2106).

  [Solicitante; DP-2106]
- **FR-077**: As formações DEVEM ser apresentadas como **linha do tempo**:
  - um nó gráfico por formação exibida, com o ano em destaque quando houver;
  - curso em negrito e atributos (unidade · nível · modalidade) em texto secundário;
  - com duas ou mais formações, um traço ligando os nós.

  A ordem e as relações temporais seguem o FR-019. [Solicitante; E8]
- **FR-078**: Cada contexto agregado no card DEVE ser um **destaque**: número em corpo
  grande (≥ 80 px) e rótulo de no máximo duas linhas, com a mesma semântica do FR-061.
  Exemplos: "27 / conclusões deste curso / na unidade Serra em 2022" e "812 / conclusões
  registradas / na unidade Serra em 2022". O sujeito continua sendo "conclusões"; nunca
  pessoas, turma ou geração. A frase completa fica na página. A data de apuração vai para
  o rodapé do card. [Solicitante; FR-061]
- **FR-079**: O card DEVE terminar com o fecho fixo do catálogo, "Essa história também é
  minha.", e a hashtag `#SouEgressoIfes`. Ambos são texto fixo, sem dado pessoal, hipóteses
  de produto revisáveis. O uso em produção depende da ACS (DP-2110). [Solicitante;
  Hipótese]
- **FR-080**: O **quadro DEVE ser ocupado intencionalmente**.
  - A abertura absorve o espaço livre, entre um mínimo e um máximo definidos no plan.
  - Dentro da área segura, nenhuma faixa vazia contínua DEVE passar de 160 px nos casos de
    1 a 4 formações, com e sem agregados.

  [Solicitante; E8]
- **FR-081**: A hierarquia tipográfica do card DEVE ter pelo menos quatro níveis
  distintos:
  - título ≥ 80 px;
  - ano e número ≥ 44 px;
  - curso ≥ 40 px;
  - rodapé e proveniência ≤ 30 px.

  O corpo mínimo é de 40 px no conteúdo e de 26 px no rodapé. O texto de apoio (atributos,
  rótulos dos destaques, legenda e hashtag) fica entre 30 e 36 px, como no protótipo
  aprovado. A proveniência só aparece no rodapé. [Solicitante; E8]
- **FR-082**: A **ordem de corte** da composição adaptativa DEVE ser:
  1. encolher a abertura até o mínimo;
  2. retirar os destaques;
  3. converter formações em "e mais N" (até 4 exibidas, tantas quantas couberem).

  Nome, título, curso e fecho nunca são cortados. [Solicitante; FR-033]
- **FR-083**: A página DEVE usar o mesmo vocabulário visual do card:
  - abertura com a imagem e a legenda do FR-076;
  - linha do tempo com nós e traço (em CSS, sem JavaScript);
  - cartões de destaque com número grande seguido da frase completa do FR-061 e da
    apuração.

  Os capítulos se distinguem por bloco visual (fundo alternado), sem telas separadas nem
  espera artificial. [Solicitante; E8; FR-028]

#### P1 — Fronteiras com features existentes

- **FR-042**: Nenhum elemento introduzido pela 021 DEVE alterar `CAMPOS_DE_CONTEXTO`, o
  registro do snapshot da 012, as colunas da 013 ou os critérios da Campanha (004/017).
  [Arquitetura; 012 FR-040; 013 FR-065]
- **FR-043**: A narrativa NÃO DEVE ler snapshots da 012 nem dados de acompanhamento da
  011. [Arquitetura]
- **FR-044**: A narrativa NÃO DEVE ler Respostas. Dados declarados ficam fora desta
  feature (DP-2107; 008/DP-802 preservada). [Arquitetura; Const. III]
- **FR-045**: Logs da 021 NÃO DEVEM conter nome, CPF, curso associado a uma pessoa nem o
  conteúdo da narrativa. [Const. XVI; Observabilidade]

#### P2 — Complemento acadêmico individual (ingresso)

- **FR-046**: Uma capacidade de contexto da trajetória, separada da fronteira acadêmica
  fundamental (E5a), DEVE poder informar, por Conclusão, um complemento opcional com o ano
  de ingresso e, quando houver, a data de ingresso da matrícula que resultou nessa
  Conclusão. [Solicitante; Arquitetura; E4; Const. III, V]
- **FR-047**: O complemento NÃO DEVE fazer parte do contexto fundamental da Conclusão. Não
  entra em `CAMPOS_DE_CONTEXTO`, no snapshot, nas exportações, nos critérios nem na
  divergência de contexto. A razão é o estado atual: o ingresso não existe na fonte real
  conhecida, não é usado por Campanha, Participação ou snapshot e serve à narrativa. A
  razão não é uma proibição permanente da 012. Promovê-lo ao contexto fundamental exige
  revisão explícita de 001 e 012. [Solicitante; Arquitetura; E4]
- **FR-048**: O complemento DEVE ser gravado por uma carga do contexto da trajetória,
  separada da incorporação, ligado à Conclusão, com fonte e momento de obtenção.
  - Depois de gravado, NÃO DEVE ser alterado.
  - Valor diferente numa nova carga DEVE ser sinalizado sem valores pessoais.

  [Herdado; 001; Const. IV]
- **FR-049**: Complemento ausente numa Conclusão já incorporada PODE ser acrescentado
  quando a fonte passar a informá-lo, sem tocar o contexto da Conclusão. [Arquitetura]
- **FR-050**: Com ingresso disponível, a narrativa DEVE poder usar a formulação "Sua
  trajetória no Ifes começou em AAAA, em {curso}." Ela vale só para a formação de menor ano
  de ingresso e só quando esse ano for único. Sem ingresso, a formulação NÃO DEVE aparecer.
  [Solicitante; FR-021]
- **FR-051**: A coerência do complemento DEVE ser verificada: ingresso posterior ao ano de
  conclusão invalida o complemento para a narrativa e é sinalizado sem valores pessoais.
  [Arquitetura]

#### P2 — Contexto institucional agregado

- **FR-052**: O contexto agregado DEVE ser uma entidade própria. NÃO DEVE ser atributo da
  Pessoa nem da Conclusão. [Solicitante; E5]
- **FR-053**: Somente duas métricas DEVEM existir:
  - **(1) conclusões do curso na unidade no ano:** quantas Conclusões a fonte reconhece,
    pela mesma regra com que reconhece a Conclusão do egresso, para aquele curso, naquela
    unidade, com aquele ano de conclusão;
  - **(2) conclusões da unidade no ano:** a mesma regra, todos os cursos da unidade
    naquele ano.

  Ambas contam Conclusões, não pessoas. Ambas incluem a do egresso e não têm denominador.
  Uma métrica nova exige spec. Turma, geração, coorte, matriculados e ingressantes só
  poderão ser enunciados com dados e definições próprias, por spec futura.
  [Solicitante; Const. XXII]
- **FR-054**: Cada agregado DEVE registrar:
  - a fonte;
  - a métrica;
  - o recorte (curso, unidade e ano, ou unidade e ano);
  - o valor;
  - a referência temporal da apuração informada pela fonte;
  - o momento de obtenção.

  [Const. IV]
- **FR-055**: Os agregados DEVEM vir somente da fonte institucional, pela capacidade de
  contexto da trajetória (E5a), em estrutura própria distinta dos atributos da Conclusão.
  NÃO DEVEM ser calculados a partir das Conclusões incorporadas no NIAE. [Solicitante;
  Const. V]
- **FR-056**: Os agregados DEVEM ser gravados uma única vez por fonte, métrica, recorte e
  apuração, compartilhados por todas as narrativas do recorte. Uma nova apuração é um
  registro novo. Registros existentes NÃO DEVEM ser alterados. [Solicitante; E5]
- **FR-057**: Quando a fonte entregar os agregados repetidos em cada linha de Pessoa ou
  Conclusão, o adaptador DEVE separá-los e deduplicá-los. Valores diferentes para a mesma
  chave e a mesma apuração DEVEM ser tratados como erro de fonte, sem escolher um deles.
  [Solicitante; Const. V]
- **FR-058**: Um agregado só DEVE ser aplicado a Conclusão da mesma fonte, quando curso,
  unidade e ano da Conclusão coincidirem exatamente com o recorte. [Arquitetura]
- **FR-059**: Um agregado DEVE ser exibido somente quando houver **exatamente uma**
  apuração conhecida para a fonte, a métrica e o recorte.
  - Com mais de uma, ele DEVE ser omitido.
  - NÃO DEVE haver escolha por ordem temporal, por momento de obtenção nem por qualquer
    outra ordenação.
  - A regra institucional de vigência entre apurações é a DP-2109.
  - Ao exibir, a referência temporal da apuração DEVE acompanhar o valor.

  [Solicitante; Const. IV, XXIX]
- **FR-060**: Um agregado com valor menor que o número de Conclusões da mesma fonte já
  incorporadas naquele recorte NÃO DEVE ser exibido, e a incoerência DEVE ser sinalizada
  sem dados pessoais. Agregado sem referência de apuração NÃO DEVE ser exibido.
  [Arquitetura]
- **FR-061**: As frases dos agregados DEVEM usar só as formulações:
  - "Em AAAA, N conclusões de {curso} foram registradas na unidade {unidade}, incluindo a
    sua.";
  - "Em AAAA, N conclusões foram registradas na unidade {unidade}."

  Com singular quando N = 1. O sujeito da contagem DEVE ser sempre "conclusões", nunca
  pessoas, estudantes ou egressos. NÃO DEVEM usar turma, geração, coorte, colegas, "se
  formaram com você", matriculados, ingressantes, percentuais, taxas ou comparação.

  No card, a mesma semântica DEVE aparecer **decomposta em destaque** (FR-078), pelas
  formulações curtas do catálogo. [Solicitante]
- **FR-062**: Indisponibilidade da fonte na carga de complementos ou agregados NÃO DEVE
  gravar nada nem ser interpretada como zero ou ausência. [Herdado; 001 FR-025]
- **FR-071** *(revisão de 2026-10-04)*: A capacidade de contexto da trajetória DEVE ser
  isolada da fonte acadêmica fundamental:
  - `FonteAcademica.obter_pessoa()`, `PessoaEncontrada`, `ConclusaoNaFonte` e
    `CAMPOS_DE_CONTEXTO` NÃO DEVEM mudar;
  - a identificação e o acesso (018), a incorporação (001) e a validação (019) NÃO DEVEM
    importar, chamar nem depender dessa capacidade;
  - falha, indisponibilidade ou ausência do enriquecimento NÃO DEVE impedir identificação,
    incorporação da Pessoa, resposta à pesquisa nem a narrativa de P1.

  [Solicitante; Const. V, XXV]

#### P2 — Fonte simulada

- **FR-063**: A fonte simulada DEVE oferecer complementos e agregados fictícios
  determinísticos. Pelo menos uma Pessoa DEVE ter ingresso e pelo menos uma não. Pelo menos
  um recorte DEVE ter agregado e pelo menos um não. Os agregados simulados DEVEM ser
  coerentes com o FR-060. [Const. XXV; Desenvolvimento com dados simulados]
- **FR-064**: Documentação e mensagens NÃO DEVEM afirmar que a fonte acadêmica real
  fornece ingresso ou agregados. [Solicitante; DP-2104, DP-2105]

#### P3 — Temas

- **FR-065**: Um segundo tema do card PODE ser oferecido. Os temas DEVEM compartilhar
  componentes e diferir só em tokens visuais. O conteúdo DEVE ser idêntico entre temas.
  [Solicitante]

#### Acessibilidade e mobile

- **FR-066**: A página DEVE atender WCAG 2.1 AA e eMAG:
  - estrutura por títulos;
  - ordem de leitura igual à visual;
  - foco visível;
  - contraste;
  - a escolha do nome com rótulo;
  - os downloads com nome acessível e indicação do formato.

  [Const. XX]
- **FR-067**: Todo o conteúdo do card DEVE também estar disponível como texto na página.
  O card nunca é o único meio de leitura. O SVG DEVE ter título e descrição textuais, e a
  prévia em imagem DEVE ter texto alternativo. [Const. XX]
- **FR-068**: A página DEVE funcionar a partir de 320 px de largura, sem rolagem
  horizontal. [Const. XXI; 015]

#### Demonstração

- **FR-069**: A feature DEVE ficar restrita à demonstração, como a 018 e a 019, enquanto
  DP-2101, DP-2102, DP-2103, DP-2105, DP-2106 e DP-2110 não forem resolvidas.
  [Const. XXIX]

### Matriz mínima de verificação automatizada

| Invariante | Verificação |
|---|---|
| Determinismo | Mesma entrada → narrativa e SVG idênticos (FR-011, FR-032) |
| Nada inventado | Para cada cenário simulado, toda frase pertence ao catálogo e só usa valores presentes (FR-017, FR-021, FR-022) |
| Formulações vedadas | Varredura do texto da página e do card contra a lista do FR-024 e do FR-061 |
| Ordem temporal | Mesmo ano / ano ausente → nenhuma relação temporal (FR-019) |
| Tempo decorrido | Só ano → "Concluída em AAAA", sem contagem; data → anos completos (FR-020) |
| Sem efeito na pesquisa | Estado do banco idêntico antes e depois de abrir e baixar (FR-008) |
| Fronteiras | `CAMPOS_DE_CONTEXTO`, snapshot e colunas da 013 inalterados com P2 ativo (FR-042, FR-047) |
| Base parcial | Sem agregado da fonte → seção ausente, mesmo com Conclusões locais (FR-055) |
| Deduplicação | Um registro por chave e apuração (FR-056) |
| Apurações | Duas apurações do mesmo recorte → agregado omitido; nenhuma escolhida por data (FR-059) |
| Grão | Duas Participações concluídas da mesma Pessoa → uma única narrativa com todas as Conclusões (FR-001, FR-016) |
| Linguagem dos agregados | Sujeito sempre "conclusões"; nenhuma conversão em pessoas (FR-024, FR-061) |
| Isolamento 001/018 | `PessoaEncontrada`, `ConclusaoNaFonte` e `CAMPOS_DE_CONTEXTO` inalterados; acesso, incorporação e declaração não importam a capacidade de contexto; contexto indisponível não afeta identificação nem incorporação (FR-071) |
| Formato social | PNG 1080 × 1920; textos dentro da área segura; prévia salvável sem JavaScript (FR-040, FR-072, FR-073) |
| Composição editorial | Zonas na ordem; elemento visual ≥ 20% do quadro; nós por formação; destaques com número ≥ 80 px; nenhuma faixa vazia > 160 px; ≥ 4 níveis tipográficos; legenda "· ilustração" sem ano (FR-074 a FR-083; SC-015) |
| Coerência | Agregado < incorporados → não exibido (FR-060) |
| Privacidade do card | Ausência de campos vedados e nome só com opção marcada (FR-034, FR-035) |
| Acesso | Sem Participação concluída, ou outra Pessoa, ou sessão expirada → sem narrativa (FR-001, FR-002) |
| Declarada | Participação da 019 não validada → confirmação inalterada (FR-007) |

### Key Entities *(include if feature involves data)*

- **Pessoa** *(001, inalterada)*: indivíduo. Fornece só o nome opcional (institucional).
- **Conclusão Acadêmica** *(001, inalterada)*: fato institucional com o contexto
  fundamental (sete atributos).
- **Complemento da Conclusão** *(P2, novo)*: fato institucional individual opcional,
  ligado a uma Conclusão, com ano e, se houver, data de ingresso da matrícula que resultou
  nela, além de fonte e momento de obtenção. Imutável depois de gravado. Fora do contexto
  fundamental.
- **Contexto Institucional Agregado** *(P2, novo)*: fato institucional sobre um grupo, com
  fonte, métrica (enumeração fechada de duas), recorte, valor, referência de apuração e
  momento de obtenção. Gravado uma vez por chave e apuração. Não pertence a nenhuma Pessoa
  ou Conclusão.
- **TrajetoriaNarrativa** *(objeto de apresentação, não persistido)*: identidade de
  exibição, formações, marcos, derivados, contextos agregados e subconjunto
  compartilhável, cada elemento com sua origem. Montada sob demanda a partir dos fatos e de
  uma data de referência.
- **Card** *(artefato, não persistido)*: imagem vertical 9:16 (PNG, artefato principal)
  derivada de uma representação vetorial (SVG) do subconjunto compartilhável, num tema.
- **Capacidade de contexto da trajetória** *(P2, fronteira nova)*: fronteira separada da
  `FonteAcademica`, que informa complementos e agregados para Conclusões já conhecidas.
  Conhecida só pela 021.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem | Fonte ou regra de derivação | Tratamento de divergência |
|------|--------|-----------------------------|---------------------------|
| Nome | Institucional | `Pessoa.nome`, da fonte | Herdado da 001 (sinalizado, nunca sobrescrito) |
| Curso, unidade, nível, modalidade, forma de oferta, ano, data de conclusão | Institucional | Conclusão Acadêmica (001) | Herdado da 001 |
| Outras formações | Institucional | Conclusões da mesma Pessoa | — |
| Formações registradas | Derivado | Contagem das Conclusões da Pessoa | Não gravado |
| Ordem temporal | Derivado | Anos de conclusão conhecidos e distintos (FR-019) | Não gravado |
| Tempo desde a conclusão | Derivado | Data de conclusão × data de referência (FR-020) | Não gravado |
| Ano/data de ingresso (P2) | Institucional | Complemento da Conclusão, pela capacidade de contexto da trajetória | Gravado uma vez; diferença sinalizada (FR-048) |
| Conclusões do curso na unidade no ano (P2) | Institucional agregado | Capacidade de contexto da trajetória (FR-055, FR-071) | Nova apuração = novo registro; mais de uma apuração conhecida = omitido (FR-059); mesma apuração com valor diferente = erro de fonte (FR-057) |
| Conclusões da unidade no ano (P2) | Institucional agregado | Idem | Idem |
| Respostas | Declarado | — | **Não usadas** |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos cenários simulados, cada frase da página e do card pertence ao
  catálogo e é derivável dos dados, sem formulação vedada.
- **SC-002**: Um egresso que acaba de concluir chega à própria trajetória com uma única
  ação a partir da confirmação.
- **SC-003**: A página carrega e é legível em 320 px, sem JavaScript e sem rolagem
  horizontal, e passa nas verificações WCAG 2.1 AA aplicáveis.
- **SC-004**: Sem nome, o egresso salva, baixa ou compartilha o card com uma ação a partir
  da página. Com nome, faz isso em até três ações: marcar o nome, atualizar a prévia e
  salvar.
- **SC-005**: Para a mesma entrada, 100% das gerações produzem narrativa e SVG idênticos.
- **SC-006**: Nenhum registro de pesquisa, snapshot, exportação ou acompanhamento muda por
  causa da 021, verificado por comparação de estado.
- **SC-007**: Com P2 ativo, o snapshot da 012 e as exportações da 013 têm formato idêntico
  ao de antes da 021.
- **SC-008**: Com 500 narrativas do mesmo recorte, existe um único registro de agregado
  por métrica e apuração.
- **SC-009**: Em nenhum cenário um número de agregado é exibido sem vir da fonte
  institucional.
- **SC-010**: Nenhum card contém, sem a escolha explícita do egresso, o nome. Em nenhum
  caso contém dado de resposta ou identificador.
- **SC-011**: Em 100% dos cenários com mais de uma apuração conhecida para o mesmo
  recorte, nenhum valor daquele agregado é exibido.
- **SC-012**: Uma Pessoa com N Participações concluídas tem exatamente uma narrativa, e ela
  reúne todas as suas Conclusões.
- **SC-013**: 100% dos cards têm 1080 × 1920 px e todo o texto dentro da área segura,
  inclusive no pior caso (nome longo, quatro cursos longos, "e mais N" e um par de
  agregados), com o corpo mínimo de texto. A imagem salva, anexada a um story do Instagram,
  entra sem recorte nem redimensionamento. O card é entregue como PNG; só SVG não atende a
  este critério.
- **SC-014**: Com a capacidade de contexto indisponível, 100% dos fluxos de identificação,
  incorporação, resposta e narrativa de P1 continuam funcionando.
- **SC-015** *(critérios de aceitação visual; auditoria de convergência visual)*: em todos
  os casos de referência (1, 2, 3, 4 e mais de 4 formações; com e sem agregados; com e sem
  imagem da unidade; com e sem nome):
  1. um elemento visual não textual ocupa ≥ 20% da área do quadro;
  2. cada formação exibida tem nó gráfico; com 2 ou mais, há traço;
  3. nenhuma contagem aparece em parágrafo: número ≥ 80 px e rótulo ≤ 2 linhas;
  4. nenhuma faixa vazia contínua > 160 px dentro da área segura;
  5. há ≥ 4 níveis tipográficos e a proveniência só aparece no rodapé;
  6. todo texto fica na área segura, com contraste AA, sem sobreposição;
  7. a imagem tem legenda "· ilustração" (ou "· fotografia"), sem ano;
  8. nenhuma frase fora do catálogo e nenhum termo vedado;
  9. o solicitante aprova o conjunto de PNGs de referência antes do merge.

## Assumptions

- A demonstração (016/018/019) é o ambiente de validação. Os dados são fictícios.
- A sessão e a identificação da 018 são reutilizadas sem mudança.
- A data de referência dos derivados é a data corrente do servidor no momento da montagem.
  Nos testes, é fixada.
- O SVG é gerado no servidor. A conversão para PNG exige uma dependência de rasterização e
  uma fonte embutida de licença aberta, o que o plan justifica em Complexity Tracking. A
  fonte embutida não é servida ao navegador e não altera a decisão D-04 da 015.
- A carga de complementos e agregados é separada da incorporação. Na demonstração, o
  preparo a executa depois de incorporar as Pessoas. O gatilho real segue a mesma pendência
  da incorporação (001/DP-006).
- O story do Instagram usa 9:16 (1080 × 1920). As redes não aceitam SVG para postagem, e
  por isso o PNG é o artefato compartilhável. O menu de compartilhamento nativo depende do
  navegador do celular. Onde ele não existe, salvar a imagem continua funcionando.
- O vocabulário de curso, unidade e nível é o da fonte (001/DP-004, DP-007), exibido sem
  tradução.

## Relação com outras features

- **001**: P1 não muda. A `FonteAcademica` não muda em nenhuma fase. P2 acrescenta, ao
  lado dela, a capacidade de contexto da trajetória e as duas entidades.
- **006/007/008**: não mudam. A Participação concluída é só lida.
- **011/012/013**: não mudam. São protegidas por teste (FR-042).
- **014**: revisão pontual da FR-041 (destino da ação) e ligação em `/formacoes/`.
- **015**: tokens reutilizados. D-03 condiciona a marca.
- **018**: sessão reutilizada. "Minha Trajetória", antes fora de escopo, passa a esta
  feature. A 018 não conhece a capacidade de contexto da trajetória (FR-071).
- **019**: participação declarada não validada não tem narrativa. A Pessoa do acervo tem
  narrativa mínima.
- **020**: independente.
- **022 (futura)**: renderer de vídeo sobre a mesma `TrajetoriaNarrativa`.

### Impacto nas features anteriores (notas de revisão a aplicar com a 021)

- **014 FR-041**: "A ação única da confirmação de Participação ancorada em Conclusão
  Acadêmica leva a 'Minha trajetória no Ifes' (021 FR-003)." A 014 FR-035 permanece para
  `/formacoes/`, que ganha uma ligação (021 FR-005). A entrada da pesquisa pode receber o
  texto fixo de antecipação do FR-070, fora da Versão.
- **014 FR-030** *(proposto no plan, research R16; ponto de revisão)*: para cumprir o
  FR-006, o título de `/formacoes/` passa de "Sua trajetória no Ifes" a "Suas formações no
  Ifes", e a ligação de `aviso.html` passa a "Ver suas formações no Ifes".
- **001 FR-012** *(com P2)*: "O complemento da Conclusão (ingresso), fora do contexto
  mínimo, é admitido pela 021 (FR-046 a FR-051). Forma de ingresso e reserva de vagas
  continuam vedadas."
- **018 (Out of Scope, :768)**: "Minha Trajetória: especificada pela 021."
- **Auditoria 2026-10-02 §5**: a vedação de "comparação social / agregados" continua. As
  duas contagens institucionais de conclusões da 021 (FR-053, FR-061) não comparam pessoas
  nem expõem taxa de resposta. "Turma" continua vedada.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade**: a narrativa só lê. Nenhuma Participação, Resposta ou âncora é
  criada ou alterada (FR-008).
- **III — Institucional ≠ derivado ≠ declarado**:
  - cada elemento da narrativa indica sua origem;
  - os derivados não são gravados;
  - as Respostas não são usadas (FR-012, FR-044).
- **IV — Proveniência**: complementos e agregados levam fonte, apuração e momento de
  obtenção (FR-048, FR-054).
- **V — Integrações desacopladas**: o adaptador separa a linha larga entre a
  `FonteAcademica` e a capacidade de contexto da trajetória. Cada contrato expõe conceitos,
  não a view. A 018 não conhece a capacidade da 021 (FR-057, FR-071).
- **VII — Pesquisa, Versão, Campanha e Participação**: a narrativa não faz parte da Versão
  e não depende de Campanha (FR-009).
- **VIII — Preservação histórica**: o snapshot e as exportações não mudam (FR-042).
  Registros de complemento e agregado não são editados.
- **XI — Identidade única, contexto múltiplo**: a narrativa mostra todas as Conclusões da
  Pessoa, sem fundir Pessoas (FR-016).
- **XVI — Privacidade**:
  - subconjunto compartilhável conservador;
  - nome só por escolha;
  - nada persistido;
  - sem link público;
  - logs sem dados pessoais (FR-033 a FR-039, FR-045).
- **XIX — Não é BI**: duas métricas fechadas, sem framework de indicadores (FR-053).
- **XX/XXI — Acessibilidade e mobile**: FR-066 a FR-068.
- **XXII — YAGNI**:
  - narrativa e card não persistidos;
  - um tema em P1;
  - vídeo na 022;
  - nenhuma camada semântica do instrumento.
- **XXVII — Migrações**: P1 sem migração. P2 é aditivo (duas entidades novas) e não altera
  tabelas existentes.
- **XXIX — Hipóteses**: a regra de acesso (E2) e a escolha de nome são hipóteses
  reversíveis. As regras institucionais estão em Decisões Pendentes.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence ao domínio de acompanhamento?** Em parte. É devolutiva da participação,
   construída só com o contexto acadêmico que o NIAE já mantém (Conclusão Acadêmica). Não
   é perfil, rede social nem portal.
2. **É necessária ao ciclo de acompanhamento?** Não estritamente. É hipótese de produto
   para aumentar adesão e confiança (propósito: quantidade, representatividade e
   confiabilidade das respostas). Por isso é restrita à demonstração (FR-069).
3. **Existe solução institucional mais adequada?** O Portal do Egresso previsto na PAEG
   (Art. 10, I; Art. 13) poderia hospedar a experiência. A relação com ele é pendente
   (DP-2108).
4. **Integração seria suficiente?** O contrato serializável (FR-014) permite que outro
   sistema, inclusive o Portal, renderize a mesma narrativa sem absorver o domínio.
5. **Aumenta o acoplamento do núcleo?** Não:
   - P1 não toca o modelo;
   - P2 acrescenta entidades à margem da fronteira, fora do contexto fundamental e dos
     artefatos analíticos.

## Out of Scope *(mandatory)*

- Vídeo, animação renderizada, Remotion ou qualquer infraestrutura de fila ou worker
  (Feature 022).
- Uso de Respostas ou de qualquer dado declarado na narrativa.
- Camada de correspondência conceitual entre Versões do instrumento.
- Marcos de pesquisa, extensão, monitoria, IC, estágio, bolsas ou mobilidade, e simulação
  deles.
- Fotos pessoais e upload. Fotografia histórica ou qualquer imagem apresentada como do
  período do egresso. Na demonstração, fotografias de campus só entram com licença
  registrada (FR-076); hoje, só a ilustração vetorial.
- Tela de espera artificial ("Preparando sua trajetória") e telas separadas por capítulo.
- IA generativa.
- Página pública, permalink, publicação em redes sociais, integração com APIs de redes
  sociais (Instagram, LinkedIn, Lattes ou outras).
- Formatos de card além do vertical 9:16 (o 4:5 do feed é direção P3).
- Editor de privacidade além da escolha de incluir o nome.
- Turma, coorte, matriculados, ingressantes, taxas, percentuais ou métricas além das duas
  do FR-053.
- Cálculo de agregados a partir da base do NIAE.
- Uso de snapshots da 012 como fonte de contexto histórico.
- Forma de ingresso, cota ou reserva de vagas.
- Mais de um tema em P1. Mais de dois em toda a feature.
- Integração com a fonte acadêmica real.
- Persistência da narrativa ou dos cards.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

### Herdadas, explicitamente preservadas

- **001/DP-004, DP-007**: vocabulário de curso, unidade e nível. A narrativa exibe o valor
  da fonte sem traduzir.
- **001/DP-006**: gatilho da incorporação. Vale também para complementos e agregados.
- **002/DP-006**: comparabilidade entre Versões. Bloqueia dados declarados (DP-2107).
- **008/DP-801**: identidade visual definitiva. A 021 usa o tratamento provisório da 015.
- **008/DP-802**: ver as próprias respostas. Não afetada, porque a 021 não usa Respostas.
- **011/DP-1102**: definição de coorte. A 021 não usa coorte.
- **015/D-03**: uso da assinatura fora do sistema. Ver DP-2102.
- **018/DP-1805**: cadência de importação do material de verificação.

### Novas

- **DP-2101** — DECISÃO PENDENTE: se e como o egresso pode compartilhar uma representação
  da sua trajetória que traga o nome do Ifes, e com que orientação (base legal, uso da
  imagem institucional).
  - Instância competente: CPAEG/Proex, com a comunicação institucional (ACS) e o
    encarregado de dados.
  - Impacto: FR-031 a FR-041, FR-069.
  - Tratamento provisório: download apenas na demonstração; nenhuma publicação pelo
    sistema.
- **DP-2102** — DECISÃO PENDENTE: uso da marca (assinatura visual) do Ifes em peça
  compartilhável fora do sistema.
  - Instância competente: ACS.
  - Impacto: FR-036, FR-075.
  - Tratamento provisório: na demonstração, a assinatura oficial já usada no cabeçalho do
    sistema (decisão do solicitante, 2026-10-05). Produção bloqueada até a ACS.
- **DP-2103** — DECISÃO PENDENTE: nome exibido ao egresso e no card (nome civil × nome
  social; qual campo a fonte institucional fornece).
  - Instância competente: registro acadêmico, com o encarregado de dados.
  - Impacto: FR-025, FR-034.
  - Tratamento provisório: nome da fonte, discreto na página e no card só por escolha.
- **DP-2104** — DECISÃO PENDENTE: disponibilidade e definição de ingresso na fonte real
  (ingresso da matrícula que resultou na Conclusão; tratamento de reingresso,
  transferência e aproveitamento).
  - Instância competente: registro acadêmico/DTI (Portão A).
  - Impacto: FR-046 a FR-051.
  - Tratamento provisório: só a fonte simulada informa.
- **DP-2105** — DECISÃO PENDENTE: definição e autorização de exibição dos agregados na
  fonte real: o que conta como conclusão reconhecida, qual "ano" (conclusão, colação,
  expedição), se há limiar mínimo de exibição e se podem ir para o card.
  - Instância competente: CPAEG/Proex, com o registro acadêmico e o encarregado de dados.
  - Impacto: FR-033, FR-053 a FR-061.
  - Tratamento provisório: só a fonte simulada, só na demonstração, sem limiar inventado.
- **DP-2106** — DECISÃO PENDENTE: acervo de imagens institucionais por unidade (origem,
  direito de uso, metadados de unidade e período).
  - Instância competente: ACS, com as unidades.
  - Impacto: FR-029, FR-076.
  - Tratamento provisório: na demonstração, só a ilustração vetorial própria e genérica,
    com legenda "· ilustração" (decisão do solicitante, 2026-10-05). O catálogo aceita
    fotografias só com origem e licença registradas. Nenhuma imagem afirma o período do
    egresso.
- **DP-2107** — DECISÃO PENDENTE: correspondência conceitual estável entre Versões, que
  permitiria usar dados declarados (situação profissional, relação trabalho-formação).
  - Instância competente: CPAEG (= 002/DP-006).
  - Impacto: P3.
  - Tratamento provisório: nenhum dado declarado.
- **DP-2108** — DECISÃO PENDENTE: relação da devolutiva com o Portal do Egresso previsto
  na PAEG.
  - Instância competente: Proex/CPAEG (pendência constitucional).
  - Impacto: localização futura da página.
  - Tratamento provisório: página no NIAE, restrita à demonstração, com contrato
    serializável que permite outra renderização.
- **DP-2109** — DECISÃO PENDENTE: regra institucional de vigência quando há mais de uma
  apuração de uma métrica agregada para o mesmo recorte (por exemplo, data de corte
  oficial ou apuração designada pela fonte).
  - Instância competente: registro acadêmico/DTI, com CPAEG/Proex.
  - Impacto: FR-059.
  - Tratamento provisório: exibir só quando houver exatamente uma apuração conhecida;
    caso contrário, omitir. Na fonte simulada, há uma apuração por recorte.
- **DP-2110** — DECISÃO PENDENTE: frase de fecho e hashtag de campanha (`#SouEgressoIfes`)
  em peça compartilhável.
  - Instância competente: ACS, com a CPAEG/Proex.
  - Impacto: FR-079.
  - Tratamento provisório: ambas na demonstração, como texto fixo do catálogo (decisão do
    solicitante, 2026-10-05). Revisáveis sem mudar comportamento.


## Nota de revisão pela Feature 020 (2026-10-05)

FR-003: a ação da confirmação ancorada em Conclusão passa de "única" a **ação principal**. "Ver minha trajetória no Ifes" continua a primeira; abaixo, com menor destaque, vem o convite opcional de e-mail da 020 (FR-009, E7). A independência funcional se mantém: a narrativa, o card e o vídeo não dependem de contato e não mostram o convite, e `narrativa`, `video` e `contexto_trajetoria` não importam `contato` nem `mobilizacao` (FR-009, FR-070 inalterados). O impacto na tela de conclusão é compartilhado e foi revisto em conjunto.

Referência: [020 — Mobilização real, Lotes e contatos do egresso](../020-mobilizacao-real-lotes-contatos/spec.md).

## Nota de revisão pela Feature 024 (2026-10-07)

- **FR-001 e E2:** a hipótese foi revista pelo solicitante. A página "Minha trajetória no Ifes", o card e o vídeo ficam disponíveis à Pessoa identificada com ao menos uma Conclusão Acadêmica, **independentemente de participação em pesquisa** (024 FR-009). Não há mais gatilho de Participação. O grão continua sendo a Pessoa. A regra vale com ou sem o Portal.
- **FR-002:** só quem não tem Conclusão Acadêmica vai para a escolha de formações, sem mensagem que revele narrativa (024 FR-010).
- **FR-005:** a ligação para a trajetória em `/formacoes/` aparece para quem tem Conclusão, mesmo sem Participação.
- **FR-070:** a antecipação ("Ao final, você poderá ver sua trajetória no Ifes.") foi retirada, porque o benefício já está disponível. Em seu lugar, para a formação disponível para iniciar, aparece "A pesquisa tem no máximo N partes." (024 FR-013, FR-014).
- **Inalterados:** FR-003, FR-004, FR-007 e FR-008. A confirmação continua levando à trajetória, e a Participação ancorada em Formação Declarada continua sem narrativa.

Referência: [024 — Início do egresso e shell do Portal](../024-inicio-egresso-portal/spec.md); [ADR 0008](../../docs/adr/0008-portal-do-egresso-camada-de-relacionamento.md).

## Nota de correção: FR-068 com fonte a 200% (2026-10-08)

- **Defeito:** a 320 px, com a fonte do navegador a 200%, a página tinha rolagem horizontal (`scrollWidth` = 397). Era o achado A1 da [validação da 024](../024-inicio-egresso-portal/validacao.md). Os espaçamentos em `rem` deixavam cerca de 112 px para o texto. Palavras longas como "Desenvolvimento" alargavam os destaques de "Naquele ano no Ifes" até 382 px. A linha do tempo também transbordava, mas o transbordo maior dos destaques encobria esse.
- **Correção (só CSS, em `narrativa.css`):**
  - os capítulos e os destaques usam um respiro lateral de `min(1rem, 5vw)`, que mantém os 16 px com fonte a 100%;
  - nos capítulos, palavras longas hifenizam (`hyphens: auto`, `lang="pt-BR"`) ou quebram;
  - a grade dos destaques usa `minmax(0, 1fr)`.
- **Inalterados:** textos, dados, contrato da narrativa e card.
- **Verificação:** com Maria (SIM-P-0003), `scrollWidth` igual à largura a 320 px e a 375 px, com fonte a 100% e a 200%. Teste: `tests/narrativa/test_pagina.py::test_css_cabe_em_320px_com_fonte_a_200`.

## Nota de revisão pela Feature 028 (2026-10-09)

A [028](../028-camada-visual-portal/spec.md) aplica a decisão 5 da ADR 0009 ao FR-076:
a legenda usa a unidade da imagem efetivamente escolhida. A imagem genérica nunca é
atribuída à unidade da formação e usa “Ifes · ilustração”. A correção vale para todos
os consumidores da legenda, inclusive card e vídeo; pode alterar a geometria da
pílula da legenda. A página recebe a base visual nova só com o Portal ligado; conteúdo,
elegibilidade, opções do card e vídeo não mudam. DP-2106 continua pendente.
