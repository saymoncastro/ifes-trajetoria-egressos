# Feature Specification: Início do egresso e shell do Portal

**Feature Branch**: `claude/024-inicio-egresso-portal`

**Created**: 2026-10-07

**Status**: Draft

**Input**: User description: "Feature 024 — Início do Egresso e Shell do Portal. Primeira
spec do Portal do Egresso (roadmap docs/roadmap/2026-10-07-portal-do-egresso-arquitetura-e-
roadmap.md, S1; ADR 0008; Constituição 2.1.0, 'Camada de relacionamento'). Entregar uma
experiência de Portal perceptivelmente diferente da atual, com página inicial que reconhece a
história do egresso a partir de informações institucionais existentes, shell e navegação do
Portal reutilizando o design system da 015, Minha trajetória (com card e vídeo) acessível a
qualquer Pessoa identificada com ao menos uma Conclusão Acadêmica independentemente de
participação em pesquisa (regra positiva que revisa explicitamente 021 FR-001/FR-002/E2 e 022
FR-001), acesso às campanhas e instrumentos existentes, coleta independente do Portal
(caminho do convite /acesso/ → /formacoes/ preservado; Portal com entrada própria neutra;
comparar com destino de lista fechada; funcionamento com Portal desabilitado), tratamento de
pessoas sem conclusão acadêmica, testes de integração dos dois caminhos, critérios
observáveis do Checkpoint 1 (compreensão e navegação). Restrições: não alterar o modelo de
campanhas, não criar outro questionário, não modificar o instrumento 2024, sem entidades
novas sem necessidade, sem Oportunidades ou Volte ao Ifes, sem comprometer a jornada
mobile-first auditada. Mockup portal_egresso.html como referência conceitual. Só
especificação e checklist de qualidade; sem implementação."

## Contexto

Hoje o egresso entra e cai numa lista de pesquisas. A identificação leva sempre à escolha de
formações (`/formacoes/`). A única devolutiva, a página Minha trajetória no Ifes, com card e
vídeo, só abre depois de uma Participação concluída. A experiência inteira diz "responda a
pesquisa".

O [roadmap do Portal](../../docs/roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md)
testa a hipótese contrária: o egresso é reconhecido e recebe algo antes de ser chamado a
responder. Esta é a primeira spec desse roadmap (S1). Ela responde:

> **"Ao entrar, o egresso reconhece que existe um espaço dele com o Ifes, e não apenas uma
> pesquisa, sem que a coleta passe a depender desse espaço?"**

A feature resolve três coisas e nada além delas:

1. **Acesso.** O egresso pode entrar pelo Portal ou diretamente pelo instrumento.
2. **Experiência.** Um Início reconhece a história do egresso.
3. **Integração.** O Início dá acesso à trajetória, ao retrato e às Campanhas existentes,
   sem duplicar funcionalidade.

### Decisões do solicitante (2026-10-07)

| # | Assunto | Decisão |
|---|---|---|
| S1 | Fronteira | O Portal é uma camada de relacionamento sobre o núcleo, só na demonstração, com dependência num único sentido ([ADR 0008](../../docs/adr/0008-portal-do-egresso-camada-de-relacionamento.md); Constituição 2.1.0) |
| S2 | Trajetória antes da pesquisa (D3) | Tudo aberto, inclusive card e vídeo, por **regra positiva**: a Pessoa identificada com ao menos uma Conclusão Acadêmica pode acessar sua trajetória institucional independentemente de participação em pesquisa |
| S3 | Nome (D2) | "Portal do Egresso" é o nome provisório da experiência na demonstração. "Trajetória Ifes" continua sendo o nome da capacidade de acompanhamento |
| S4 | Caminho do convite | O caminho `/acesso/` → `/formacoes/` dos convites (016, 018) é preservado. O mecanismo do Portal deve ser o mais simples, sem mudar os contratos existentes |
| S5 | Escopo | Não é redesenho da aplicação. Fora: Oportunidades, Volte ao Ifes, comunidade, interesses. Os critérios de teste são definidos antes do teste |

### Princípios desta spec

1. **A coleta não muda e não depende do Portal.**
   - Não mudam Campanha, Versão, instrumento 2024, Participação, Resposta, resolução da
     entrada (007), jornada (008/014/023), convite (016/020) nem identificação (018).
   - Com o Portal desabilitado, tudo funciona como hoje.
2. **Reconhecer antes de pedir.**
   - O Início mostra primeiro o que o Ifes registra sobre a pessoa e de onde vem cada
     informação.
   - A pesquisa aparece depois, uma única vez, como convite.
3. **Só o que é verdade e só o que existe.**
   - Nenhum dado inventado: sem marco declarado, fato do período, comunidade ou indicador
     social.
   - Nenhuma área sem função: sem link ou menu de Oportunidades ou de Volte ao Ifes.
   - Nenhuma estimativa de tempo (008 FR-095).
   - Vale a regra de verdade das mensagens (014 FR-008).
4. **Reaproveitar, não redesenhar.**
   - Tokens, assinatura e componentes da 015.
   - Composição editorial da página da 021.
   - A jornada da pesquisa fica visualmente igual à de hoje.
5. **Sem JavaScript, mobile primeiro, acessível** (008 FR-080; Princípios XX e XXI).

### Verificação no código (base `claude/portal-egresso-architecture-de1fec`, sobre `main` em `598ee32`)

| Fato | Onde |
|---|---|
| A identificação confirmada sempre redireciona para `/formacoes/` | `trajetoria/acesso/views.py` (`entrada`) |
| A raiz `/` vai para `/formacoes/` (Pessoa), `/declaracao/` (declarante) ou `/acesso/` | `trajetoria/interface/views.py` (`inicio`) |
| O convite leva a `/acesso/`, sem identidade, token, formação ou Campanha | 016 FR-021/FR-022; 018 FR-053; `trajetoria/comunicacao/transporte.py` |
| Não existe link específico de Campanha nem preservação de destino | — |
| Uma tela sem sujeito vai para `/acesso/` ou `/acesso/?aviso=sessao` | `trajetoria/acesso/sessao.py` (`destino_da_entrada`; 023 FR-001) |
| O envio guardado com a sessão expirada é retomado a partir de `/formacoes/` | `trajetoria/interface/views.py` (`formacoes`; 023 FR-006) |
| A trajetória só abre com Participação concluída ancorada em Conclusão. É o **único** ponto que lê Participação | `trajetoria/narrativa/consultas.py` (`elegivel`) |
| A narrativa não lê Respostas, e nenhum texto dela ou do card menciona a pesquisa | 021 FR-044; `trajetoria/narrativa/` |
| O vídeo usa a composição do card e as condições de acesso da 021 | 022 FR-001; `trajetoria/narrativa/views.py` (`composicao_da_sessao`) |
| O vídeo só é gerado por ação explícita | 022 FR-002 |
| `/formacoes/` antecipa o benefício ("Ao final, você poderá ver sua trajetória no Ifes.") | `trajetoria/interface/mensagens.py` (`ANTECIPACAO`); 021 FR-070 |
| O shell é único, sem navegação, e se chama "Trajetória Ifes — Acompanhamento de egressos" | `interface/templates/interface/base.html`; 015 `contracts/shell.md` |
| Precedente de destino fechado: "nunca um endereço vindo do cliente" | `trajetoria/demonstracao/views.py` (011 R13) |

### Como o Portal entra: alternativas comparadas

| Critério | **A — Entradas neutras distintas** | B — Destino de lista fechada |
|---|---|---|
| Como funciona | O convite mantém `/acesso/` → `/formacoes/`. O Portal tem um endereço próprio e neutro que identifica, quando necessário, e leva ao Início | Uma única identificação recebe um código de destino de lista fechada e segue para ele. O padrão passa a ser o Início |
| Contratos existentes (016, 018 FR-053, 023 FR-001/FR-006) | **Intactos** | `/acesso/` e o redirecionamento da sessão expirada mudam. O convite precisa carregar o destino "pesquisa", ou a pesquisa deixa de ser o padrão |
| Redirecionamento arbitrário | Impossível: cada entrada tem destino fixo | Evitado só pela lista fechada |
| Dado no endereço | Nenhum | Um código de destino (não pessoal) |
| Sessão expirada numa página do Portal | Volta à entrada do Portal → Início | Volta à página exata |
| Sessão expirada numa página compartilhada (trajetória, e-mail) | Segue como hoje: `/acesso/` → `/formacoes/`, onde a navegação leva ao Início | Volta à página exata |
| Tamanho da mudança | Pequeno e aditivo | Maior, porque toca o fluxo comum de identificação |

**Escolha: A.** [Arquitetura; Solicitante S4] Ela preserva todos os contratos e não abre
nenhuma forma de redirecionamento. O custo é uma limitação aceita: quem tem a sessão expirada
numa página compartilhada volta pelo caminho da pesquisa, a um toque do Início. B fica
registrada como evolução possível se o Checkpoint 1 mostrar que essa limitação atrapalha.

### Os dois caminhos

```text
Caminho A — convite de Campanha (inalterado)
  e-mail ──► /acesso/ ──► identificação ──► /formacoes/ ──► pesquisa
                                                  │
                                                  └─ com o Portal ativo: navegação para o Início

Caminho B — Portal do Egresso (novo)
  entrada do Portal ──► identificação, se não houver sessão ──► Início
                                                                 ├─► Minha trajetória (card e vídeo)
                                                                 ├─► pesquisa (= /formacoes/, a mesma resolução)
                                                                 └─► Meu e-mail

Sessão identificada: navega entre as duas experiências; cada tela mantém suas regras de acesso.
Portal desabilitado: Caminho B não existe; Caminho A e a trajetória funcionam como descrito.
```

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Entrar pelo Portal e ser reconhecido antes de qualquer pedido (Priority: P1)

Marina acessa o endereço do Portal, sem ter recebido convite nenhum. Ela confirma CPF e data
de nascimento e chega a um Início. A primeira coisa que vê é o que o Ifes registra sobre ela:
as formações concluídas, com curso, unidade, nível e ano, marcadas como registro do Ifes. Na
sequência vêm o que ela pode fazer ali (ver a trajetória, o retrato e o vídeo, manter o
e-mail) e, por último, o convite para a pesquisa aberta, se houver uma.

**Why this priority**: é a hipótese central do roadmap. Sem ela, não há o que testar no
Checkpoint 1.

**Independent Test**: com uma Pessoa fictícia de duas Conclusões e uma Campanha em coleta,
entrar pelo endereço do Portal sem sessão e confirmar os dados. A pessoa deve chegar ao
Início, ver as duas formações com a origem identificada antes do convite e não ver nenhuma
pergunta do instrumento.

**Acceptance Scenarios**:

1. **Given** nenhuma sessão, **When** a pessoa abre a entrada do Portal, **Then** vê a
   identificação da 018 (mesmos campos, mensagens, limites e saídas), identificada como
   entrada do Portal do Egresso.
2. **Given** a identificação confirmada pela entrada do Portal, **When** a resposta chega,
   **Then** a pessoa está no Início, e não em `/formacoes/`.
3. **Given** uma Pessoa com sessão válida, **When** abre a entrada do Portal, **Then** vai
   direto ao Início, sem nova identificação.
4. **Given** o Início de uma Pessoa com Conclusões, **When** a página é lida na ordem do
   documento, **Then** o reconhecimento da trajetória vem antes de qualquer menção à
   pesquisa.
5. **Given** uma Pessoa com três Conclusões, **When** abre o Início, **Then** as três
   aparecem, na ordem da 007, cada uma com a indicação de que é registro do Ifes.
6. **Given** a identificação "não confirmada" pela entrada do Portal, **When** a pessoa
   escolhe informar a formação, **Then** segue o fluxo da 019, sem mudança.
7. **Given** uma sessão de declarante (019), **When** abre a entrada do Portal, **Then** vai
   para `/declaracao/`, como a raiz faz hoje.

---

### User Story 2 — Ver a própria trajetória, o retrato e o vídeo antes de responder (Priority: P1)

Ana nunca respondeu à pesquisa. Pelo Início, ela abre Minha trajetória no Ifes, baixa o card
e pede o vídeo. Nada disso exige uma Participação concluída.

**Why this priority**: é a essência do experimento "valor antes da coleta" (S2). Manter a
trajetória como prêmio posterior enfraqueceria o Checkpoint 1.

**Independent Test**: com uma Pessoa fictícia com Conclusão e sem nenhuma Participação,
abrir a trajetória, baixar o card e pedir o vídeo. Os três devem funcionar, e nenhuma
Participação, Resposta ou contagem pode mudar.

**Acceptance Scenarios**:

1. **Given** uma Pessoa com ao menos uma Conclusão Acadêmica e nenhuma Participação,
   **When** abre Minha trajetória, **Then** vê a mesma narrativa que veria depois de
   participar.
2. **Given** a mesma Pessoa, **When** baixa o card e pede o vídeo, **Then** ambos funcionam
   com as regras de nome e de ação explícita da 021 e da 022.
3. **Given** uma Pessoa sem nenhuma Conclusão Acadêmica, **When** pede a trajetória, **Then**
   segue o encaminhamento atual para a escolha de formações, sem mensagem que revele
   narrativa.
4. **Given** a pessoa com Participação em rascunho, **When** abre a trajetória, **Then** o
   rascunho não muda.
5. **Given** a confirmação "Pesquisa concluída", **When** exibida, **Then** sua ação continua
   levando à trajetória (021 FR-003).

---

### User Story 3 — Chegar pelo convite e responder sem passar pelo Portal (Priority: P1)

Diego recebe o convite da Campanha por e-mail, segue o link, confirma os dados e cai na
escolha de formações, exatamente como hoje. Ele responde, conclui e segue para a próxima
formação (023). O Portal não se interpõe em nenhum momento.

**Why this priority**: é a independência exigida pela Constituição 2.1.0 e pelo ADR 0008.
Se ela quebrar, a coleta passa a depender do Portal.

**Independent Test**: seguir o endereço do convite, confirmar, responder e concluir. O
percurso, os endereços e os textos da jornada devem ser os de hoje. A única diferença
admitida, com o Portal ativo, é a navegação nas telas fora das Seções (FR-022).

**Acceptance Scenarios**:

1. **Given** o endereço do convite, **When** a pessoa confirma os dados, **Then** chega a
   `/formacoes/`, e não ao Início.
2. **Given** uma Participação em rascunho, **When** a pessoa entra pelo convite, **Then** vê
   "Continuar a pesquisa" e "onde parou", como hoje.
3. **Given** uma Participação concluída na Campanha em coleta, **When** a pessoa entra pelo
   convite, **Then** vê o estado de hoje (sem entrada pendente) e o caminho para a
   trajetória.
4. **Given** uma Campanha encerrada, ou uma pessoa fora da abrangência ou sem pesquisa
   disponível, **When** entra pelo convite, **Then** vê a mesma mensagem de hoje (007/014).
5. **Given** um envio guardado por sessão expirada (023), **When** a pessoa se identifica
   de novo pela entrada do convite, **Then** volta à Seção com as marcações restauradas, como
   na 023 FR-006.

---

### User Story 4 — Navegar entre o Portal e a pesquisa numa mesma sessão (Priority: P2)

Com a sessão identificada, a pessoa vai do Início à pesquisa e da escolha de formações ao
Início pela navegação do Portal. Cada tela mantém suas próprias regras.

**Why this priority**: une os dois caminhos sem fundi-los. A pessoa que chegou pelo convite
descobre o Portal, e a que chegou pelo Portal acha a pesquisa.

**Independent Test**: com o Portal ativo e uma sessão, percorrer Início → pesquisa → Início
→ trajetória → e-mail → Início só pela navegação, sem digitar endereço.

**Acceptance Scenarios**:

1. **Given** o Portal ativo e a pessoa em `/formacoes/`, **When** usa a navegação, **Then**
   chega ao Início.
2. **Given** a pessoa numa Seção da pesquisa, **When** a página é exibida, **Then** o shell
   é o de hoje, sem a navegação do Portal (FR-022).
3. **Given** uma página do Portal com a sessão expirada, **When** a pessoa pede a página,
   **Then** volta à entrada do Portal com o aviso de sessão encerrada da 023 e, depois de se
   identificar, chega ao Início.

---

### User Story 5 — A coleta funciona com o Portal desabilitado (Priority: P2)

A equipe técnica desliga o Portal. A raiz, o convite, a jornada, a trajetória e o e-mail
funcionam como antes desta feature. Duas exceções são intencionais: a trajetória continua
aberta antes da pesquisa (é regra da trajetória, não do Portal) e o texto de antecipação
continua revisado.

**Why this priority**: é a garantia verificável de que o Portal é uma camada adicional
(Constituição 2.1.0).

**Independent Test**: com o Portal desabilitado, rodar o percurso da User Story 3 e abrir os
endereços do Portal. O percurso deve funcionar, e os endereços do Portal devem estar
indisponíveis.

**Acceptance Scenarios**:

1. **Given** o Portal desabilitado, **When** se abre a entrada do Portal ou o Início, **Then**
   a resposta é "não encontrado", como para qualquer funcionalidade indisponível.
2. **Given** o Portal desabilitado, **When** se abre a raiz, **Then** o comportamento é o de
   hoje.
3. **Given** o Portal desabilitado, **When** se percorre qualquer tela do egresso, **Then**
   não há navegação do Portal, e o shell é o da 015.

---

### Edge Cases

- **Pessoa identificada sem nenhuma Conclusão Acadêmica.** O Início mostra, com a regra de
  verdade, que nenhuma formação concluída foi encontrada, com o mesmo texto da 007 para
  `SEM_FORMACAO`. Não há reconhecimento de formação, item "Minha trajetória", card nem
  convite. Ficam disponíveis Meu e-mail e Sair. Nenhum fluxo novo é criado.
- **Nome ausente na fonte.** O Início não depende do nome, porque não o exibe (FR-019).
- **Várias Campanhas aplicáveis (ambiguidade operacional, 004/DP-404).** O convite do Início
  só diz que há pesquisa e leva a `/formacoes/`, que trata o caso como hoje.
- **Várias formações com pesquisa pendente (`SELECAO_NECESSARIA`).** O convite é um só e
  leva a `/formacoes/`. O Início não repete a escolha.
- **Sessão expirada no Início ou na entrada do Portal com envio guardado.** O envio guardado
  pertence à jornada. Ele é retomado na escolha de formações (023 FR-006), à qual o convite
  do Início leva.
- **Falha ao montar a narrativa** (por exemplo, composição impossível). O Início omite o
  bloco afetado e continua mostrando as formações e as ações. A página não cai.
- **Vídeo indisponível** (sem renderizador). O atalho para o vídeo some, como o bloco da 022
  (FR-037).
- **"Sair" no Portal.** Encerra a sessão exatamente como hoje (018).
- **Recarregar o Início ou abri-lo em outra aba.** Nada é gravado. Abrir o Início não altera
  nenhum dado.
- **Pessoa de fonte não admitida na demonstração.** Vale a barreira da 018 (fonte simulada).
- **Endereço de entrada do Portal com parâmetros estranhos.** São ignorados. Nenhum
  parâmetro decide destino.

## Requirements *(mandatory)*

### Functional Requirements

#### Entrada e caminhos de acesso

- **FR-001**: DEVE existir uma **entrada do Portal**, com endereço neutro, estável e
  divulgável. O endereço NÃO DEVE conter identidade, token, formação, Campanha nem código
  de destino. [Arquitetura; ADR 0008]
- **FR-002**: Sem sessão, a entrada do Portal DEVE oferecer a mesma identificação da 018:
  - mesma verificação, campos, mensagens, limites de tentativa e espera;
  - mesmo painel de pessoas fictícias da demonstração;
  - mesmas saídas para "não confirmada" (019);
  - mesma regra da 023 FR-022.

  A página DEVE se identificar como entrada do Portal do Egresso. [Arquitetura; 018]
- **FR-003**: Identificação confirmada pela entrada do Portal DEVE levar ao Início.
  Identificação confirmada por `/acesso/` DEVE continuar levando a `/formacoes/`.
  [Arquitetura; Solicitante S4]
- **FR-004**: Com sessão de Pessoa válida, a entrada do Portal DEVE levar ao Início. Com
  sessão de declarante (019), DEVE levar a `/declaracao/`. [Arquitetura]
- **FR-005**: Com o Portal ativo, a raiz do site DEVE se comportar como a entrada do Portal
  (acesso espontâneo). O endereço do convite (`/acesso/`) NÃO DEVE mudar. [Arquitetura;
  revisa 008, raiz]
- **FR-006**: Nenhum valor vindo do cliente DEVE decidir o destino depois da identificação.
  Cada entrada tem destino fixo. [Arquitetura; Const. XVI]
- **FR-007**: Uma página do Portal pedida sem sujeito válido DEVE levar à entrada do Portal,
  com o aviso genérico de sessão encerrada da 023 (FR-001) quando a sessão acabou de
  expirar. A frase de envio guardado da 023 (FR-003) NÃO DEVE aparecer na entrada do
  Portal: o envio guardado nasce na jornada, que manda para `/acesso/`, e só volta na
  escolha de formações. As páginas da pesquisa, da trajetória e do e-mail mantêm o
  encaminhamento de hoje (`/acesso/`). [Arquitetura; 023; regra de verdade]
- **FR-008**: O percurso do convite DEVE ser preservado em todos os casos abaixo, com os
  mesmos endereços, estados e textos de hoje:
  - identificação → escolha de formações → Seções → conclusão → confirmação → próxima
    formação;
  - Participação em rascunho;
  - Participação concluída;
  - Campanha encerrada;
  - fora da abrangência;
  - sem pesquisa;
  - ambiguidade;
  - envio guardado (023 FR-006).

  A única diferença admitida é a do FR-022. [Const. 2.1.0; ADR 0008]

  *(Revisado em 2026-10-08.)* Nas telas com a navegação do Portal, também são admitidos o
  nome do produto (FR-024), o destino de "Sair" (FR-034) e a ligação de fim de página
  (FR-035). Endereços, estados, telas e toques do percurso continuam os de hoje.

#### Minha trajetória antes da pesquisa (regra positiva)

- **FR-009**: **A Pessoa identificada com ao menos uma Conclusão Acadêmica DEVE poder
  acessar sua trajetória institucional — a página Minha trajetória no Ifes, o card e o
  vídeo — independentemente de participação em pesquisa.** É uma regra da trajetória e não
  depende de o Portal estar ativo. [Solicitante S2; Hipótese]
- **FR-010**: A Pessoa identificada sem nenhuma Conclusão Acadêmica NÃO tem trajetória
  institucional. Ao pedi-la, DEVE seguir o encaminhamento atual para a escolha de
  formações, sem mensagem que revele narrativa. [Arquitetura; 021 FR-002 preservado nesse
  ponto]
- **FR-011**: Abrir a trajetória, baixar o card ou pedir o vídeo NÃO DEVE criar nem alterar
  Participação, Resposta, Pessoa, Conclusão, Formação Declarada, validação, snapshot,
  exportação ou contagem. O vídeo continua sendo gerado só por ação explícita (022 FR-002).
  [Const. I, VII, VIII; 021 FR-008]
- **FR-012**: A confirmação de Participação ancorada em Formação Declarada (019) continua
  sem oferecer narrativa (021 FR-007). [Const. III]
- **FR-013**: A escolha de formações NÃO DEVE mais antecipar a trajetória como benefício
  futuro, porque ela já está disponível. A frase "Ao final, você poderá ver sua trajetória
  no Ifes." deixa de ser exibida. A ligação para a trajetória (021 FR-005) aparece sempre
  que o FR-009 for atendido. [Arquitetura; regra de verdade, 014 FR-008]
- **FR-014**: No lugar da antecipação, para cada formação **disponível para iniciar**, a
  escolha de formações DEVE dizer, antes do primeiro toque, quantas partes a pesquisa tem no
  máximo, pela mesma regra do indicador da 023 ("no máximo N"). Para a formação a retomar,
  vale o "onde parou" da 023, sem essa frase. [Reauditoria R-02; 023]

#### Início do Portal

- **FR-015**: O Início DEVE estar disponível só à Pessoa identificada na sessão (018), só
  com o Portal ativo e só no modo de demonstração. [Const. 2.1.0; XXIX]
- **FR-016**: O Início DEVE apresentar, nesta ordem:
  1. **reconhecimento**: o que o Ifes registra sobre a pessoa;
  2. **proveniência**: de onde vêm essas informações;
  3. **o que a pessoa pode fazer**: trajetória, retrato e vídeo, e-mail;
  4. **convite à pesquisa**, quando houver.

  [Hipótese; roadmap S1]
- **FR-017**: O reconhecimento DEVE usar só fatos institucionais e derivados que a narrativa
  da 021 já produz para a Pessoa:
  - formações: curso, unidade, nível, ano, na ordem da 007;
  - número de formações registradas;
  - tempo desde a conclusão;
  - primeira formação, quando única.

  Deve haver uma única fonte de montagem, sem segunda regra de fatos. NÃO DEVE usar
  Respostas, Formação Declarada, contato nem agregados de comunidade. [Arquitetura; 021
  FR-044; Const. III]
- **FR-018**: Cada fato institucional DEVE indicar que é registro do Ifes. Cada derivado
  DEVE ser apresentado como derivado, com a explicação de que a 021 já dispõe. O Início
  DEVE ter uma frase curta que explique a origem das informações e diga que nada ali foi
  respondido pela pessoa. [Const. III, IV]
- **FR-019**: O Início NÃO DEVE exibir o nome da pessoa, nem como saudação nem como
  título. O reconhecimento vem do contexto da formação. Na trajetória, o nome continua
  seguindo a 021 (DP-2103). [Auditoria 2026-10-02 §5]
- **FR-020**: O convite à pesquisa DEVE:
  - aparecer uma única vez, depois do reconhecimento e das ações;
  - refletir a situação da resolução da entrada (007), sem recalculá-la;
  - levar à escolha de formações, que decide e conduz como hoje.

  O texto por situação:

  | Situação | Texto | Ação |
  |---|---|---|
  | Há pesquisa a iniciar | Diz que há uma pesquisa de acompanhamento aberta para a(s) formação(ões) e que respondê-la é como a pessoa atualiza sua trajetória com o Ifes | "Responder" |
  | Há pesquisa a retomar | Diz que a pessoa já começou a responder e pode continuar de onde parou. A Seção exata ("Você parou em «…»", 023) aparece na escolha de formações, a um toque, porque sai das Respostas, que o Início não lê (FR-017) *(revisado em 2026-10-08, avaliação por IA, A7)* | "Continuar" |
  | Sem entrada pendente ou sem pesquisa | Frase de estado verdadeira, sem cobrança | Nenhuma |
  | Sem formação | Nenhum convite | Nenhuma |

  O convite NÃO DEVE conter estimativa de tempo, percentual, contagem de colegas nem
  urgência. Os textos finais ficam no plan, sujeitos à regra de verdade. [Hipótese; 008
  FR-095; 014 FR-008]
- **FR-021**: O Início NÃO DEVE conter:
  - Oportunidades, Volte ao Ifes, comunidade, interesses ou memória do campus;
  - indicador social ("conectados", "geração", "turma");
  - estimativa de tempo;
  - progresso de perfil;
  - ligação ou área sem função.

  [Roadmap §3.3; Solicitante S5]

#### Shell e navegação

- **FR-022**: Com o Portal ativo, as páginas do Portal e as telas do egresso fora das Seções
  DEVEM exibir a navegação do Portal. As telas com navegação são:
  - o Início;
  - a escolha de formações;
  - a confirmação;
  - Minha trajetória;
  - Meu e-mail.

  As Seções, a tela de concluir e as telas de declaração (019) NÃO DEVEM exibir a
  navegação. Essas telas mantêm o shell da 015, para não alterar a jornada auditada.
  [Arquitetura; reauditoria 2026-10-06]
- **FR-023**: A navegação DEVE ter só destinos que existem para aquela pessoa:
  - Início;
  - Minha trajetória (só se o FR-009 for atendido);
  - a pesquisa (escolha de formações);
  - Meu e-mail.

  A navegação DEVE indicar a página atual de forma acessível. [Arquitetura]
- **FR-024**: No shell do Portal, o cabeçalho DEVE manter assinatura, ordem e regras da 015
  (FR-015 a FR-017; `contracts/shell.md`). O nome do produto passa a ser "Portal do Egresso"
  nas páginas do Portal, com nome provisório registrado (S3). "Trajetória Ifes" DEVE
  continuar identificando a pesquisa de acompanhamento onde ela é oferecida. A faixa de
  demonstração e o "Sair" não mudam. [Solicitante S3; 015]

  *(Revisado em 2026-10-08, avaliação por IA, A1.)* "Páginas do Portal" são **todas as
  telas que exibem a navegação do Portal** (FR-022): Início, escolha de formações,
  confirmação, Minha trajetória e Meu e-mail. Nelas, o cabeçalho e o rodapé dizem "Portal do
  Egresso". As Seções, a tela de concluir, `/acesso/` e a declaração mantêm "Trajetória
  Ifes". Sem o Portal, nada muda. O destino de "Sair" é o do FR-034.
- **FR-025**: A navegação DEVE:
  - funcionar sem JavaScript;
  - caber a partir de 320 px sem rolagem horizontal, com fonte de 100% a 200%;
  - ter alvos de toque de pelo menos 44×44 px CSS (014);
  - ser operável por teclado, com foco visível (015).

  [Const. XX, XXI; 008 FR-080]
- **FR-026**: O Início DEVE reaproveitar tokens e componentes da 015 e a composição
  editorial da página da 021, como a abertura com ilustração e legenda e a lista de
  formações. NÃO DEVE criar tokens novos. O veto da auditoria de identidade visual a "hero,
  faixas alternadas, cards em grade" é reaberto **apenas** para o Início, com o motivo
  registrado: o Início é, em parte, superfície de navegação. Mesmo assim, NÃO DEVE usar
  grade de cartões nem hero com saudação. [Arquitetura; roadmap §3.3]

#### Portal desabilitado e fronteira

- **FR-027**: DEVE ser possível desabilitar o Portal por configuração de ambiente,
  independentemente do modo de demonstração. Desabilitado:
  - entrada do Portal e Início respondem "não encontrado";
  - a raiz se comporta como hoje;
  - nenhuma tela mostra navegação do Portal;
  - convite, jornada, trajetória (com o FR-009) e e-mail funcionam.

  [Const. 2.1.0; ADR 0008]
- **FR-028**: Nenhum componente do núcleo DEVE depender da camada do Portal. A dependência
  vai só do Portal para o núcleo, e isso DEVE ser verificado por teste de fronteira. A
  divisão física em módulos é decisão do plan. [Const. 2.1.0]
- **FR-029**: A camada do Portal NÃO DEVE gravar nada. Esta feature não cria entidade,
  tabela nem migração. [Const. 2.1.0; XXII]
- **FR-030**: Como a 018 a 023, toda a feature DEVE ficar restrita ao modo de demonstração.
  [Const. 2.1.0; XXIX]

#### Acessibilidade e mobile

- **FR-031**: Início e entrada do Portal DEVEM atender a WCAG 2.1 AA e ao eMAG:
  - HTML semântico, com um único `h1`;
  - ordem lógica;
  - contraste dos tokens 015;
  - foco visível;
  - nomes acessíveis;
  - nenhuma informação só por cor (a origem "registro do Ifes" é texto).

  [Const. XX]
- **FR-032**: A 375×812 px, o título e o primeiro fato de reconhecimento DEVEM aparecer sem
  rolar. A 320 px, não pode haver rolagem horizontal. [Const. XXI]

#### Verificação automatizada

- **FR-033**: A feature DEVE ter testes de integração para cada um destes casos:
  1. acesso espontâneo ao Portal (entrada sem sessão → identificação → Início; com sessão →
     Início; declarante → `/declaracao/`);
  2. acesso direto ao instrumento pelo endereço do convite (identificação →
     `/formacoes/`);
  3. caminho de entrada preservado depois da identificação, inclusive com sessão expirada
     e envio guardado da 023;
  4. Participação em andamento e Participação concluída, pelos dois caminhos;
  5. Campanha encerrada, pessoa fora da abrangência e sem pesquisa, pelos dois caminhos;
  6. Pessoa sem Conclusão Acadêmica (Início, trajetória e navegação);
  7. trajetória, card e vídeo antes de qualquer Participação, sem efeito colateral;
  8. Trajetória Ifes com o Portal desabilitado (FR-027);
  9. nenhum parâmetro do cliente decide destino (FR-006);
  10. fronteira de dependência (FR-028) e ausência de gravação (FR-029);
  11. *(revisão de 2026-10-08)* nome do produto por tela, destino de "Sair", ligação de fim
      de página e convite de retomada (FR-020, FR-024, FR-034 a FR-036), com o Portal ligado
      e desligado.

  [Const. XXVI; ADR 0008]

#### Revisão pós-avaliação por IA (2026-10-08)

Origem: [avaliação por IA dos checkpoints](../../docs/auditorias/2026-10-08-portal-checkpoints-avaliacao-ia.md),
achados A1 a A4, A6 e A7, priorizados pelo solicitante antes da primeira sessão do Checkpoint
1. A avaliação não aplica o Checkpoint 1, que continua **não aplicado**.

- **FR-034**: Com o Portal ativo, "Sair" nas telas com a navegação do Portal (FR-022) DEVE
  encerrar a sessão como a 018 e levar à entrada do Portal. Nas demais telas (Seções,
  concluir, declaração), DEVE continuar levando a `/acesso/`. O destino é fixo por tela,
  sem valor vindo do cliente (FR-006). Sem o Portal, "Sair" é o de hoje. [Arquitetura;
  avaliação A2]
- **FR-035**: Com o Portal ativo, a ligação de fim de página de Minha trajetória e de Meu
  e-mail DEVE ser "Voltar ao Início". Sem o Portal, continuam "Voltar às suas formações" e
  "Ver suas formações no Ifes". [Hipótese; avaliação A3, A4]
- **FR-036**: O botão "Sair" da faixa de demonstração DEVE ter alvo de pelo menos 44×44 px
  CSS (014). [Const. XX; avaliação A6]

Ficam para depois:
- A5 (quebra da navegação), junto com a 025, que acrescenta o quinto item;
- A8 e A11 (textos da 021 e da 014), depois do teste.

### Requisitos revisados

Esta feature revisa requisitos anteriores. A rastreabilidade fica aqui e, na
implementação, numa nota de revisão em cada spec afetada.

| Requisito | Antes | Depois (024) |
|---|---|---|
| **021 FR-001** | Página só para a Pessoa com Participação concluída ancorada em Conclusão (gatilho E2) | Pessoa identificada com ao menos uma Conclusão Acadêmica, independentemente de pesquisa (FR-009) |
| **021 FR-002** | Quem não tem Participação concluída é levado à escolha de formações | Só quem não tem Conclusão Acadêmica é levado à escolha de formações (FR-010) |
| **021 E2** | "Grão: a Pessoa. Gatilho: a Participação concluída." [Hipótese] | Grão: a Pessoa. **Sem gatilho de Participação.** A hipótese foi revista pelo solicitante (S2) |
| **021 FR-070** | `/formacoes/` PODE antecipar o benefício ("Ao final, você poderá ver…") | Antecipação retirada, porque o benefício já está disponível. Em seu lugar, o tamanho máximo da pesquisa (FR-013, FR-014) |
| **022 FR-001** | Vídeo nas condições de acesso da 021 (sessão e Participação concluída) | Vídeo nas condições do FR-009 |
| **015 shell** | "Sem navegação"; produto "Trajetória Ifes" | Com o Portal ativo: navegação nas telas do FR-022 e nome "Portal do Egresso" nas páginas do Portal (FR-024). Sem o Portal: inalterado |
| **015 shell** (revisão de 2026-10-08) | Com o Portal ativo: "Portal do Egresso" só no Início; "Sair" sempre para `/acesso/` | "Portal do Egresso" em toda tela com a navegação do Portal (FR-024, revisado); "Sair" dessas telas para a entrada do Portal (FR-034); alvo de 44×44 px (FR-036) |
| **021, fim da página** (sem FR próprio) | "Voltar às suas formações" | Com o Portal ativo: "Voltar ao Início" (FR-035) |
| **020, `/meu-email/`** (sem FR próprio) | "Ver suas formações no Ifes" | Com o Portal ativo: "Voltar ao Início" (FR-035) |
| **008, raiz `/`** | Pessoa → `/formacoes/`; declarante → `/declaracao/`; sem sessão → `/acesso/` | Com o Portal ativo: entrada do Portal (FR-005). Sem o Portal: inalterado |

**Não são revisados:**

- 016 FR-021/FR-022 e 018 FR-053: o convite continua neutro e em `/acesso/`;
- 023 FR-001 e FR-006;
- 021 FR-003, FR-004, FR-007 e FR-008;
- 022 FR-002 em diante;
- o modelo de Campanha;
- o instrumento 2024.

### Key Entities *(include if feature involves data)*

**Nenhuma entidade nova.** A feature só lê:

- **Pessoa** (sessão da 018);
- **Conclusão Acadêmica** e seu complemento (021 P2), pela narrativa;
- a **situação da resolução da entrada** (007), para o convite;
- o **Contato da Pessoa** (020) **não** é lido: o atalho "Meu e-mail" tem rótulo fixo
  (minimização, Princípio XVI; research R6).

Nenhuma Resposta é lida.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem | Fonte ou regra de derivação | Tratamento de divergência |
|---|---|---|---|
| Curso, unidade, nível, ano de conclusão | Institucional | Conclusão Acadêmica (001), via narrativa (021) | Exibido como na fonte (001/DP-004) |
| Número de formações registradas, tempo desde a conclusão, primeira formação | Derivado | Regras da 021, com explicação | Omitido quando a 021 omite |
| Situação da pesquisa (iniciar, retomar, sem pendência) | Derivado | Resolução da entrada (007) | Não recalculado no Portal |

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Verificáveis automaticamente ou por medição** (gate da feature):

- **SC-001**: Os dez casos do FR-033 passam. Os testes das features 007, 008, 014, 016,
  018, 019, 020, 021, 022 e 023 continuam passando, exceto os que verificam requisitos
  revisados, que são atualizados com rastreabilidade.
- **SC-002**: Pelo convite, uma pessoa chega à primeira Seção com o mesmo número de telas e
  toques de hoje (reauditoria 2026-10-06, cenário A).
- **SC-003**: Pela entrada do Portal, uma pessoa sem sessão chega ao Início com uma
  identificação. Do Início, chega à trajetória, à pesquisa ou ao e-mail com **um** toque.
- **SC-004**: A 375×812 px, o título e o primeiro fato de reconhecimento do Início aparecem
  sem rolar. Nenhuma página nova tem rolagem horizontal de 320 a 1280 px, com fonte de 100%
  a 200%.
- **SC-005**: Com o Portal desabilitado, o percurso do convite e as telas do egresso
  respondem como na base `598ee32`, salvo FR-009, FR-013 e FR-014.
- **SC-006**: Zero gravações causadas pelo Portal, pela trajetória, pelo card ou pelo
  vídeo. As contagens de Participação, Resposta e contato ficam iguais antes e depois.
- **SC-007**: Nas Seções da pesquisa, a altura do shell e a posição da primeira pergunta são
  iguais às da reauditoria de 2026-10-06.

**Checkpoint 1 — teste moderado** (definidos antes do teste; ver roadmap §7):

O teste usa personas fictícias e só as capacidades reais desta feature. Oportunidades e
Volte ao Ifes não aparecem no produto. Se forem exploradas, é com o mockup conceitual,
mostrado à parte e identificado como protótipo. Taxa de resposta, engajamento e conversão
**não** são critério de sucesso.

*Compreensão (modelo mental).* A maioria dos participantes:

- **SC-008**: descreve o Início como um espaço dela com o Ifes, e não como "uma pesquisa"
  ou "um formulário";
- **SC-009**: diz, sem ajuda, o que o Ifes já sabe sobre a trajetória dela;
- **SC-010**: distingue o que é registro do Ifes do que ela responderia na pesquisa;
- **SC-011**: percebe que pode ver a trajetória, o retrato e o vídeo sem responder nada;
- **SC-012**: sabe onde atualizar a trajetória quando houver pesquisa disponível.

*Comportamento (navegação).* A maioria dos participantes:

- **SC-013**: chega a Minha trajetória sem ajuda;
- **SC-014**: trata a pesquisa como convite, e não como a finalidade do ambiente;
- **SC-015**: localiza Retrato, vídeo e Meu e-mail;
- **SC-016**: não lê o Início como painel administrativo de pendências.

Leitura do resultado:

- **Os critérios de compreensão falham.** A S1 é corrigida antes da S2 e da S3.
- **Só os de navegação falham.** O ajuste é de navegação ou de texto, dentro desta feature.

O número de participantes e o limiar de "maioria" são definidos no protocolo do teste,
antes de aplicá-lo.

## Assumptions

- **Personas e dados.** O teste e a demonstração usam as Pessoas fictícias do
  `preparar_demonstracao`, inclusive alguma sem Participação e, se a fonte simulada tiver,
  alguma sem Conclusão. Se faltar uma dessas pessoas, o plan acrescenta um cenário fictício
  pelos mecanismos já existentes da demonstração, sem mudar o modelo.
- **Endereço da entrada do Portal.** É definido no plan, com estas restrições: neutro,
  estável e diferente de `/acesso/`.
- **Microcopy.** Os textos finais do Início, do convite e da navegação ficam no plan,
  sujeitos à regra de verdade e a captura de tela, como na 021 e na 023.
- **Mockup.** O `portal_egresso.html` é referência conceitual de tom e estrutura, não
  contrato visual. O que ele contradiz está listado no roadmap §3.3 e não é adotado.
- **Desabilitar o Portal.** É uma configuração técnica de ambiente, como o modo de
  demonstração. Não é governança nem autorização.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I, VII, VIII — Longitudinalidade e preservação.** Nada é criado nem alterado por abrir
  o Portal, a trajetória, o card ou o vídeo (FR-011, FR-029). A Participação e a jornada
  não mudam.
- **III, IV — Institucional × declarado e proveniência.** O Início usa só fatos
  institucionais e derivados, cada um com a origem indicada (FR-017, FR-018). Nenhuma
  Resposta é lida.
- **VI e Fronteira (Camada de relacionamento, 2.1.0).**
  - Dependência num só sentido (FR-028).
  - Nada gravado (FR-029).
  - Coleta independente (FR-008, FR-027).
  - Dados da camada fora do analítico: não há dado da camada.
- **XIV — Menos fricção.** O caminho do convite não ganha telas nem toques (SC-002). O
  Portal chega à trajetória em um toque (SC-003).
- **XV — Autenticação substituível.** A entrada do Portal reaproveita a identificação da
  018, sem mecanismo novo.
- **XVI — Privacidade.**
  - Sem dado pessoal no endereço.
  - Sem destino vindo do cliente (FR-006).
  - O Início não lê o contato da pessoa.
  - Sem agregados de comunidade.
- **XX, XXI — Acessibilidade e mobile.** FR-025, FR-031 e FR-032. Sem JavaScript.
- **XXII — YAGNI.**
  - Sem entidade.
  - Sem mecanismo genérico de destino (alternativa A).
  - Sem área de fachada.
- **XXIX — Hipóteses.** O FR-009 e a ordem do Início são hipóteses do solicitante,
  reversíveis e testadas no Checkpoint 1. O nome é provisório.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence ao domínio de acompanhamento?** Não diretamente. É a camada de relacionamento
   admitida pela Constituição 2.1.0, só na demonstração (ADR 0008).
2. **É necessária ao ciclo de acompanhamento?** Não. É hipótese de produto para melhorar a
   relação e, por consequência, a adesão. Por isso o ciclo funciona sem ela (FR-027).
3. **Existe solução institucional mais adequada?** O Portal do Egresso da PAEG (Art. 10, I;
   Art. 13) ainda não existe. A relação continua pendente para o uso real.
4. **Integração seria suficiente?** Para um Portal externo, sim: o contrato serializável da
   narrativa (021) e a sessão (018) são as fronteiras. Aqui a camada consome o núcleo pelos
   mesmos contratos internos.
5. **Aumenta o acoplamento do núcleo?** Não. A dependência é num só sentido e verificada
   (FR-028). Não há escrita nem entidade. A única regra alterada no núcleo, o acesso à
   trajetória, é regra da própria trajetória e independe do Portal (FR-009).

## Out of Scope *(mandatory)*

- Oportunidades, Volte ao Ifes, comunidade, interesses, memória do campus: nem como link,
  área de fachada ou "em breve" (S2 e S3 do roadmap).
- Qualquer entidade, tabela, migração ou gravação nova.
- Mudança em Campanha, Versão, instrumento 2024, resolução da entrada, jornada das Seções,
  convite, mobilização ou identificação.
- Mecanismo genérico de preservação de destino (alternativa B).
- "Conte só o que mudou" e qualquer formulário fora do instrumento.
- Respostas, Formação Declarada ou marcos declarados no Início ou na trajetória (DP-2107).
- Indicadores sociais, agregados de comunidade, estimativa de tempo, percentual,
  gamificação.
- Novo tema, estilo de retrato ou formato de card.
- Reentrada com menos atrito (link por e-mail, Gov.br): DP-1808 e Portão A.
- Ajustes R-01 (seção × parte) e R-05 (lista do declarante) da reauditoria. O roadmap os
  sugeria junto com a S1, mas o solicitante limitou a 024 a acesso, experiência e
  integração. Só o R-02 entra, porque substitui a antecipação revista (FR-014).
- Link para o Relatório Anual de Acompanhamento de Egressos (quick win do roadmap): exige
  URL oficial existente e fica para quando houver uma.
- Uso fora do modo de demonstração.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

### Herdadas e preservadas

- **DP-2108** (relação da devolutiva com o Portal) e **D1 (produção)** do roadmap. A relação
  institucional com o Portal da PAEG é da Proex, da CPAEG e da DTI. Tratamento: camada só na
  demonstração (ADR 0008).
- **D2 (definitivo)**: nome institucional da experiência. Instância: ACS, com a Proex.
  Tratamento: "Portal do Egresso" provisório (FR-024).
- **DP-2103**: nome exibido (civil × social). Tratamento: o da 021.
- **DP-2101, DP-2102, DP-2105, DP-2106, DP-2110**: compartilhamento, marca, agregados,
  imagens, fecho. Continuam restringindo card e vídeo à demonstração (021 FR-069). O FR-009
  amplia quem pode ver, mas não amplia onde.
- **DP-1808 / Portão A**: mecanismo de identificação para uso real.

### Novas

- **DP-2401** — DECISÃO PENDENTE: se, no uso real, abrir a trajetória institucional antes de
  qualquer participação é compatível com a finalidade e a base legal do tratamento definidas
  para o acompanhamento.
  - Instância competente: encarregado de dados, com CPAEG/Proex.
  - Impacto: FR-009.
  - Tratamento provisório: só na demonstração. Os dados são os mesmos que a pessoa já vê
    na escolha de formações.
