# Feature Specification: Gestão mínima de Campanha

**Feature**: `017-gestao-minima-campanha`

**Feature Branch**: `claude/spec-017-campaign-management-e96f8f` (sincronizada com a main)

**Created**: 2026-10-03

**Status**: Implementada e validada em 2026-10-03; 43 tasks completas.

**Input**: Solicitação da Feature 017: expor, sobre as capacidades de domínio da 004, uma
interface administrativa simples e segura para consultar, criar, preparar, abrir e encerrar
Campanhas, sem segmentação de mobilização, workflow, scheduler, publicação de Versão ou nova
regra institucional. O caso principal é uma Campanha ampla: nome, Versão já PUBLICADA e
período; depois, abrir e encerrar a coleta explicitamente.

## Contexto

> Campanha é uma rodada institucional de observação. Campanha NÃO é lista de destinatários
> e NÃO é mecanismo de segmentação de mobilização (ADR 0004).

A 004 entregou a Campanha como domínio completo: criação, alteração enquanto nunca aberta,
período, critérios de abrangência, abertura explícita, encerramento antecipado explícito,
estado derivado e imutabilidade a partir da primeira abertura. Deliberadamente, nada disso
foi exposto a pessoas (004 FR-056), porque a competência para gerir Campanha está pendente
(004/DP-402). A 011 passou a exibir as Campanhas, a 016 acrescentou a comunicação simulada
ao detalhe, e ambas repetiram a proibição de gestão (011 FR-100; 016 FR-003).

Até hoje, Campanhas só nascem pelo preparo local da demonstração ou por testes. A 017 fecha
essa lacuna **somente no modo local de demonstração**, com operadores fictícios e uma
interpretação operacional explícita e reversível. Ela não resolve DP-402.

O caso principal desta feature:

```text
Nova Campanha                         EM PREPARAÇÃO
                                      Instrumento: Pesquisa … — v2027
Nome    [Pesquisa Institucional …]    Período: não definido
Versão  [Pesquisa … — v2027     ▾]    Para abrir a coleta: defina o período.
Início  [          ] (opcional)       [Editar configuração]
Fim     [          ] (opcional)
[Salvar]                              (com período 01/04/2027 – 30/06/2027, a partir de 01/04)
                                      [Editar configuração]  [Abrir coleta]

EM COLETA                             ENCERRADA
Aberta em: 01/04/2027 09:12           Aberta em: …  Encerrada em: … (antecipadamente | ao fim do período)
Encerramento previsto: 30/06/2027     somente leitura
indicadores da 011                    indicadores da 011
[Comunicação simulada]  [Encerrar coleta]

PERÍODO ENCERRADO — CAMPANHA NUNCA ABERTA
Não houve coleta. Para usar esta Campanha, corrija o período.
[Editar configuração]
```

### Base existente e evidências

Inspeção da `main` (revisão `5e50fec`, PR #26 / ADR 0004 mergeados) em 2026-10-03:
[Constituição](../../.specify/memory/constitution.md), [002](../002-pesquisa-versao-instrumento/spec.md),
[004](../004-campanhas-populacao-elegivel/spec.md), [005](../005-participacao-respostas-rascunho/spec.md),
[009](../009-editor-pesquisa-versao/spec.md), [010](../010-governanca-papeis-escopos/spec.md),
[011](../011-acompanhamento-operacional-coleta/spec.md), [016](../016-mobilizacao-comunicacao-simulada/spec.md)
e [ADR 0004](../../docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md).

| Fato atual | Evidência | Consequência para a 017 |
| --- | --- | --- |
| Criar (nome + Versão em qualquer estado), alterar nome/Versão, definir período, abrir, encerrar e remover já existem, com bloqueio de linha e rejeição explícita sem gravação parcial | `trajetoria/campanha/operacoes.py`; `regras.py` (`Motivo`, `CampanhaRejeitada`) | Só interface; nenhuma regra de Campanha é reescrita |
| Abertura exige Versão PUBLICADA, período definido e data de referência dentro do período; relata **todas** as condições não satisfeitas; nunca publica nem agenda | `abrir`; 004 FR-036, FR-009, FR-042 | Abrir só é possível dentro do período; antes do início, o operador volta no dia |
| Estado derivado: encerramento explícito → fim do período (aberta ou não) → abertura → preparação | `consultas.estado`, `encerramento` | Campanha nunca aberta e expirada aparece ENCERRADA, mas continua corrigível (004 FR-039, FR-043) |
| Imutabilidade controlada só por `aberta_em` | `_bloquear_nunca_aberta`; 004 FR-043 | "Editar configuração" existe enquanto nunca aberta, em qualquer estado temporal |
| Não há consulta de "impedimentos de abertura" sem gravar; a verificação vive dentro de `abrir` | `operacoes.abrir` | Comportamento novo mínimo: expor os impedimentos sem duplicar a regra (FR-016) |
| Versão tem só RASCUNHO e PUBLICADA; publicar é capacidade interna, sem superfície | 002 FR-011, FR-013, DP-001; 009 FR-076; 010 FR-047 | A 017 só lista Versões PUBLICADA; não publica |
| Única Versão publicada na demonstração é a cópia técnica "Demonstração — cópia da referência 2024"; a baseline 2024 continua em RASCUNHO | `demonstracao/cenario.py` | Demonstrável hoje; a "rodada em preparação" (baseline em rascunho) exibe o impedimento real de Versão não publicada |
| Rótulo legível de Versão: "Pesquisa — designação" | `acompanhamento/consultas.py`, `instrumento()` | Mesmo rótulo na escolha da Versão |
| Lista e detalhe de Campanhas, em todos os estados, com visibilidade por escopo; somente leitura e GET | 011 FR-001, FR-020 a FR-022, FR-040, FR-043; `acompanhamento/{views,acesso,consultas}.py` | A gestão se integra a essas páginas; não há módulo paralelo |
| Comunicação simulada entra pelo detalhe, em qualquer estado; simulação só fora de ENCERRADA | 016 FR-007; `campanha.html` | A 017 não altera a 016 |
| Papéis fechados CPAEG (institucional) e CSAEG (unidade); regras puras sobre vínculos ativos; nenhuma regra de Campanha | `governanca/{models,regras}.py`; 010 FR-033, FR-073 | Uma nova regra de capacidade, localizada e reversível (FR-003) |
| Modo de demonstração desligado torna toda a superfície administrativa inexistente; não há autenticação | `demonstracao/middleware.py`, `operador.py`; `config/settings.py` | A 017 só existe no modo de demonstração |
| Padrão de formulário administrativo: formulário só converte entrada; o domínio rejeita; motivos viram mensagens; sucesso redireciona com aviso fechado; ação destrutiva tem confirmação | `editor/{views,formularios,mensagens}.py` | Reutilizar o padrão; nenhuma validação de domínio repetida no formulário |

### Respostas da auditoria prévia

1. **O que já existe e só precisa de interface?** Na 004: `criar_campanha`, `alterar_campanha`
   (nome e Versão), `definir_periodo`, `abrir`, `encerrar`, `estado`, `encerramento` e o
   vocabulário de rejeição. Na 011: lista, detalhe, escopo e indicadores. Na 010:
   identificação do operador fictício e vínculos ativos. Na 016: o acesso à comunicação
   simulada pelo detalhe.
2. **O que é comportamento novo?** (a) uma regra de capacidade "gerir Campanha" (FR-003);
   (b) uma consulta sem gravação dos impedimentos de abertura, derivada da mesma regra que
   `abrir` aplica (FR-016); (c) as telas e ações: nova, editar, abrir e encerrar, com
   confirmação; (d) a restrição de **interface** à escolha de Versão PUBLICADA, mais estrita
   que o domínio (004 FR-007, FR-008), que continua aceitando qualquer Versão.
3. **Incompatibilidades?** Sim, uma, de governança: 004 FR-056, 010 FR-033/FR-073 e 011
   FR-001/FR-016/FR-100 proíbem expor gestão de Campanha enquanto DP-402 estiver aberta. A
   017 revisa essas cláusulas **apenas** para o modo de demonstração, por interpretação
   operacional identificada (FR-003, "Impacto nas features anteriores"). Entre 004, 011 e
   ADR 0004 não há conflito: a 011 não mostra critérios, e a 017 não os expõe. Há ainda
   uma diferença de leitura, não um conflito: "ENCERRADA → somente leitura" vale para
   Campanha **aberta**. A Campanha nunca aberta cujo período expirou continua editável
   (004 FR-039, FR-043) e é apresentada como "Período encerrado — Campanha nunca aberta"
   (FR-023a), sem novo estado de domínio.
4. **Como tratar DP-402?** DP-402 permanece aberta. A 017 adota a interpretação C1 (abaixo):
   na demonstração, só a CPAEG ativa gere Campanha. A regra fica num único ponto e não é
   competência produtiva.
5. **A ausência de publicação impede a 017?** Tecnicamente, não: a demonstração e os testes
   têm Versão publicada por meio técnico (009 FR-079). Operacionalmente, sim, para o piloto:
   sem caminho institucional de publicação (002/DP-001, DP-002), a nova Versão revisada
   nunca chegará a PUBLICADA, e nenhuma Campanha real poderá ser aberta com ela. Isso é
   registrado como dependência pré-piloto, não resolvido aqui.
6. **Campos mínimos**: nome e Versão (somente PUBLICADA) para criar; período (início e fim)
   pode ser informado já na criação ou depois, e é exigido só para abrir. Na
   consulta: estado, Versão, período, momento da abertura, momento e forma do encerramento,
   impedimentos de abertura e, quando existir, aviso de abrangência restrita definida fora
   da interface.
7. **Expor critérios de abrangência?** Não há consumidor concreto: a nova Versão é
   instrumento único (inclusive para formação declarada), e a ADR 0004 diz que a interface
   principal não deve expô-los. Ficam fora, sem tela "avançada". A transparência sobre
   critérios já existentes é tratada só por um aviso de leitura (FR-022).

### Interpretação operacional desta feature (Princípio XXIX)

Técnica, reversível e localizada. Não cria competência institucional e não resolve DP-402.

| # | Interpretação | Fundamento | Por que é interpretação |
| --- | --- | --- | --- |
| C1 | Na demonstração, criar, preparar, abrir e encerrar uma Campanha é a forma, no software, de **planejar, organizar e executar** as atividades da PAEG **no âmbito do Ifes**; cabe à CPAEG ativa, com escopo institucional | 010 A7 (Art. 21, I), A9 (Art. 21, V), B3 | A PAEG não fala de rodadas nem de sistema; quem abre e encerra a rodada real é DP-402 |
| C2 | A CSAEG **não** gere Campanha: uma Campanha ampla alcança todas as unidades e excede o escopo de unidade (010 B4). Campanha de unidade é DP-403, e recortar por unidade para mobilizar é o uso que a ADR 0004 proíbe | 010 B4; 011 B4; ADR 0004 | A PAEG não proíbe expressamente; menor privilégio (Const. XII, XVI) |
| C3 | A CPAEG gere a rodada, mas **não** decide por isso sua periodicidade, duração ou edição oficial. O período digitado na demonstração não é regra institucional | 010 A3 (Art. 10, II); 004/DP-401 | Periodicidade pertence a Proex/Proen |
| C4 | Gerir Campanha **não** inclui publicar Versão, aprovar instrumento, definir abrangência, mobilizar egressos, prorrogar ou reabrir | 002/DP-001; ADR 0004; 004/DP-405 | Ausência de competência expressa e de consumidor concreto |

Alternativas consideradas: **não expor nada** até DP-402 (mantém o produto sem caminho
demonstrável de Campanha e adia o aprendizado de UX necessário ao piloto); **CPAEG + CSAEG**
(contradiz C2). Adota-se C1 porque é o menor desenho que exercita o ciclo completo, usa o
escopo institucional já existente e pode ser revertido trocando uma única regra.

### Dependência pré-piloto: publicação da Versão

```text
nova Versão elaborada (009, RASCUNHO)
        │
        ▼
   ??????  ← 002/DP-001 (quem publica) e 002/DP-002 (como se aprova): ABERTAS
        │
        ▼
Versão PUBLICADA ──► Campanha (017) ──► coleta (005–008)
```

**A 017 não cria caminho de publicação.** Ela só oferece Versões já PUBLICADA. Enquanto
002/DP-001 permanecer aberta, Versões publicadas existem apenas por meio técnico (preparo
local, testes). A exposição institucional da publicação precisa ser decidida e
especificada **antes do piloto real**. Isso não bloqueia esta feature, mas bloqueia sua
aplicação a uma rodada real.

## Clarifications

### Session 2026-10-03

- Q: O período deve ser obrigatório para criar e salvar uma Campanha em preparação? → A:
  Não. A Campanha pode existir sem período; período completo e válido é exigido apenas para
  abrir a coleta. A configuração é progressiva. (FR-008, FR-010, FR-016)
- Q: Como apresentar a Campanha nunca aberta cujo período expirou, que o domínio deriva
  como ENCERRADA? → A: Sem novo estado de domínio. A interface a distingue claramente da
  Campanha que entrou em coleta e foi encerrada ("Período encerrado — Campanha nunca
  aberta") e oferece "Editar configuração", conforme a 004. (FR-017, FR-023a)
- Q: O que mostrar ao abrir quando já existem outras Campanhas em coleta? → A: Só um aviso
  informativo simples: os nomes das outras Campanhas em coleta e que alguns egressos podem
  encontrar mais de uma pesquisa disponível. Sem bloqueio, sem cálculo de interseção, sem
  previsão de impacto. (FR-019)
- Aprovadas sem alteração: gestão mínima; critérios de abrangência fora da interface; sem
  Lote; sem remoção; confirmação para abrir e encerrar; só Versões PUBLICADA; CPAEG como
  interpretação restrita à demonstração, com DP-402 aberta; publicação fora da 017;
  comunicação com os estados da 016; DP-1701 pré-piloto.

## User Scenarios & Testing *(mandatory)*

Todos os operadores e dados são fictícios e existem apenas no modo local de demonstração.
"Operador gestor" é o operador fictício com vínculo CPAEG ativo (C1). As quatro histórias
P1/P2 são necessárias para fechar a feature.

### User Story 1 - Criar uma Campanha ampla e prepará-la (Priority: P1)

Como operador gestor, na lista de Campanhas, aciono "Nova Campanha", informo nome e escolho
uma Versão publicada; posso informar o período já ou depois. Ao salvar, vejo o detalhe da
Campanha EM PREPARAÇÃO, sem nenhum critério de abrangência, com o que falta para abrir a
coleta.

**Why this priority**: é o primeiro passo de qualquer rodada e não existe hoje fora do
preparo técnico.

**Independent Test**: com uma Versão publicada, criar "Pesquisa Institucional de Egressos
2027" só com nome e Versão; conferir EM PREPARAÇÃO, sem critérios, com o impedimento
"período não definido" e sem botão de abrir. Depois, definir 01/04/2027 a 30/06/2027 e
conferir o impedimento "a coleta poderá ser aberta a partir de 01/04/2027".

**Acceptance Scenarios**:

1. **Given** operador gestor e ao menos uma Versão PUBLICADA, **When** salva nome e Versão,
   com ou sem período válido, **Then** a Campanha é criada sem critérios, aparece na lista
   e o detalhe mostra EM PREPARAÇÃO e os impedimentos de abertura que restam.
2. **Given** o formulário, **When** abre a escolha de Versão, **Then** só aparecem Versões
   PUBLICADA, rotuladas "Pesquisa — designação"; nenhum rascunho é oferecido.
3. **Given** nome em branco, só uma das datas ou início posterior ao fim, **When** salva,
   **Then** nada é gravado e cada problema aparece junto ao campo, com os valores
   digitados preservados.
4. **Given** nenhuma Versão PUBLICADA, **When** aciona "Nova Campanha", **Then** vê que não
   há Versão publicada disponível e que a publicação não é feita nesta interface
   (002/DP-001), sem formulário que inevitavelmente falharia.
5. **Given** o formulário, **When** o examina, **Then** não há campo de ano de conclusão,
   unidade, nível, modalidade, forma de oferta, público, lote ou divulgação.

---

### User Story 2 - Corrigir uma Campanha que nunca foi aberta (Priority: P1)

Como operador gestor, no detalhe de uma Campanha nunca aberta, aciono "Editar configuração"
e completo ou corrijo nome, Versão ou período. Isso vale também quando o período expirou
sem abertura.

**Why this priority**: a preparação admite correção até a abertura (004 FR-043); sem isso,
um erro de digitação exigiria outra Campanha.

**Independent Test**: editar "Demonstração — rodada em preparação" (Versão em rascunho,
sem período): escolher a Versão publicada e um período que inclua hoje; conferir que o
impedimento de Versão some e que "Abrir coleta" passa a ser oferecido.

**Acceptance Scenarios**:

1. **Given** Campanha nunca aberta, **When** altera nome, Versão e período válidos,
   **Then** as alterações são gravadas de uma vez e os impedimentos são recalculados.
2. **Given** Campanha nunca aberta cuja Versão atual está em RASCUNHO, **When** abre a
   edição, **Then** a Versão atual aparece pré-selecionada e identificada como "não
   publicada — impede a abertura"; nenhum outro rascunho é oferecido.
3. **Given** Campanha nunca aberta cujo período expirou, **When** consulta lista ou
   detalhe, **Then** vê "Período encerrado — Campanha nunca aberta", nunca apenas
   "Encerrada", e o aviso de que não houve coleta.
4. **Given** essa Campanha, **When** corrige o período para uma janela que inclui hoje,
   **Then** ela volta a EM PREPARAÇÃO; isso não é reabertura (004 FR-039).
5. **Given** Campanha já aberta (EM COLETA ou ENCERRADA), **When** consulta o detalhe,
   **Then** não há "Editar configuração". Se a edição for forçada por requisição direta,
   ela é recusada sem gravar nada.
6. **Given** Campanha nunca aberta com período definido, **When** apaga as duas datas e
   salva, **Then** nada é gravado e a mensagem diz que o período pode ser corrigido, mas
   não removido.
7. **Given** Campanha com critérios de abrangência definidos fora da interface, **When**
   edita, **Then** vê um aviso de leitura com esses critérios, e eles permanecem
   inalterados depois de salvar.

---

### User Story 3 - Abrir a coleta explicitamente (Priority: P1)

Como operador gestor, no detalhe de uma Campanha EM PREPARAÇÃO sem impedimentos, aciono
"Abrir coleta", confirmo e vejo a Campanha EM COLETA, fixada.

**Why this priority**: abrir é o ato que torna a pesquisa respondível; sem ele, a gestão
não tem efeito.

**Independent Test**: com Campanha de período que inclui hoje e Versão publicada, abrir e
conferir: estado EM COLETA, "Aberta em" registrado, "Editar configuração" ausente, "Encerrar coleta"
presente, e a Campanha aparecendo na entrada do egresso de demonstração para Conclusões na
sua abrangência.

**Acceptance Scenarios**:

1. **Given** nenhum impedimento, **When** aciona "Abrir coleta", **Then** vê uma confirmação
   que informa o que será fixado (nome, Versão, período), que a Campanha passa a aceitar
   respostas imediatamente e que não há reabertura nem prorrogação.
2. **Given** a confirmação, **When** confirma, **Then** a Campanha fica EM COLETA, e o
   detalhe mostra o aviso de sucesso e o momento da abertura.
3. **Given** a confirmação, **When** desiste, **Then** volta ao detalhe e nada muda.
4. **Given** qualquer impedimento conhecido (Versão não publicada, período não definido,
   hoje antes do início, período encerrado sem abertura), **When** consulta o detalhe, **Then** vê
   **todos** os impedimentos em linguagem clara, com o que fazer, e "Abrir coleta" não é
   oferecido.
5. **Given** outra Campanha EM COLETA, **When** chega à confirmação, **Then** vê o aviso
   "Já existem outras Campanhas em coleta. Isso pode fazer com que alguns egressos tenham
   mais de uma pesquisa disponível." e os nomes dessas Campanhas. A abertura não é
   bloqueada (004 FR-051; 004/DP-404).
6. **Given** a condição mudou entre a exibição e a confirmação (outro operador abriu ou
   editou, ou o dia virou), **When** confirma, **Then** a rejeição do domínio é mostrada
   com seus motivos e nada é gravado. Se a Campanha já estava aberta, a mensagem informa o
   estado atual (004 FR-037).

---

### User Story 4 - Encerrar a coleta antes do fim do período (Priority: P2)

Como operador gestor, no detalhe de uma Campanha EM COLETA, aciono "Encerrar coleta",
confirmo e vejo a Campanha ENCERRADA de forma explícita.

**Why this priority**: o fim natural já ocorre pelo período, sem ação; o encerramento
antecipado é necessário, mas menos frequente.

**Independent Test**: encerrar uma Campanha EM COLETA e conferir: ENCERRADA, "Encerrada em
… (explícito)", nenhuma ação de gestão, indicadores da 011 preservados, e nova Participação
recusada pela 005.

**Acceptance Scenarios**:

1. **Given** Campanha EM COLETA, **When** aciona "Encerrar coleta", **Then** vê uma
   confirmação que informa que novas respostas deixarão de ser aceitas, que não há
   reabertura nem prorrogação (004/DP-405) e que as Participações existentes são
   preservadas.
2. **Given** a confirmação, **When** confirma, **Then** a Campanha fica ENCERRADA, com
   momento e forma explícitos.
3. **Given** Campanha EM COLETA, **When** consulta o detalhe, **Then** vê "Encerramento
   previsto" com a data final do período e entende que, sem ação, ela se encerra ao fim
   desse dia.
4. **Given** Campanha ENCERRADA (explicitamente ou pelo período), **When** consulta,
   **Then** só há leitura, além da comunicação simulada definida pela 016.

---

### User Story 5 - Recusar quem não gere Campanha (Priority: P1)

Como operador sem a capacidade (CSAEG, sem vínculo ou sem operador escolhido), não vejo
ações de gestão e, se tentar acessá-las diretamente, sou recusado antes de qualquer dado ou
gravação.

**Why this priority**: a interpretação C1 só é segura se for verificada no servidor em toda
requisição.

**Independent Test**: com o operador B (CSAEG Vitória) e com o C (sem vínculo), acessar
lista e detalhe e chamar diretamente cada ação de gestão (GET e POST). Conferir: nenhuma
ação visível, recusas com o tratamento da 011, nenhuma gravação. Desativar o vínculo CPAEG
do operador A e conferir que a recusa vale na requisição seguinte.

**Acceptance Scenarios**:

1. **Given** CSAEG ativa, **When** consulta lista e detalhe, **Then** vê exatamente o que a
   011 já mostra, sem "Nova Campanha", "Editar configuração", "Abrir coleta" ou "Encerrar coleta".
2. **Given** qualquer operador sem a capacidade, **When** requisita diretamente uma ação de
   gestão, **Then** é recusado; sem operador, é encaminhado à escolha existente.
3. **Given** modo de demonstração desligado, **When** qualquer rota de gestão é requisitada,
   **Then** ela não existe.

---

### Edge Cases

- **Período inteiramente no passado na criação**: aceito pelo domínio. A Campanha nasce
  como "Período encerrado — Campanha nunca aberta", com o aviso "não houve coleta; para
  usar esta Campanha, corrija o período" e "Editar configuração" disponível.
- **Hoje antes do início**: nenhum agendamento; o detalhe informa a partir de quando a
  abertura será possível (004 FR-042).
- **Hoje igual ao fim**: a abertura é admitida (datas inclusivas). A confirmação informa que
  a coleta se encerra ao fim do próprio dia (FR-018).
- **Campanha sem período**: válida em preparação; impedimento "período não definido".
  Informar só uma das datas é rejeitado. Depois de definido, o período pode ser corrigido,
  mas não removido: a 004 não tem operação para isso e não há consumidor.
- **Nomes repetidos**: permitidos pela 004 (FR-002 a). A lista distingue as Campanhas pelo
  período e pelo instrumento; nenhuma unicidade é inventada.
- **Versão da Campanha despublicada**: impossível; a publicação é irreversível (002 FR-013).
- **Versão de outra Pesquisa**: permitida (004 FR-008); o rótulo mostra a Pesquisa.
- **Duas abas ou dois operadores**: o domínio bloqueia a linha e decide. A interface mostra
  a rejeição ou o estado atual, sem gravação parcial e sem segunda abertura.
- **Reenvio do formulário de abertura ou encerramento**: a segunda submissão não altera
  nada e informa o estado atual (004 FR-037, FR-040).
- **Vínculo revogado durante a confirmação**: a submissão é recusada na própria
  requisição.
- **Campanha com abrangência restrita** (só por meio técnico, como a "coleta sobreposta"
  da demonstração): o detalhe e a edição mostram o aviso de leitura (FR-022). Nada permite
  criá-la ou alterá-la pela interface.
- **Campanha criada por engano**: pode ser corrigida enquanto nunca aberta e permanece na
  lista. Remoção não é exposta (Out of Scope).

## Requirements *(mandatory)*

Origem: **[Solicitante]** pedido explícito; **[004/010/011/016]** contrato existente
reutilizado; **[Arquitetura]** fronteira ou preservação; **[Hipótese]** escolha de produto
reversível; **[Interpretação]** aplicação limitada à demonstração (C1–C4), sem competência
institucional. Nenhum requisito é **[Herdado]** do formulário 2024.

### Functional Requirements

#### Contexto e autorização

- **FR-001**: Toda superfície da 017 DEVE existir somente no modo local de demonstração,
  desligado por padrão; com o modo desligado, suas rotas DEVEM ser inexistentes.
  [008; 016 FR-001]
- **FR-002**: Toda rota de gestão, de leitura ou de escrita, DEVE verificar no servidor,
  a cada requisição, o operador fictício em uso e seus vínculos ativos, antes de expor
  dados ou chamar operação de domínio. Sem operador, DEVE encaminhar à escolha existente;
  sem a capacidade, DEVE recusar com o tratamento da 011. [010; 011]
- **FR-003**: A capacidade "gerir Campanha" DEVE ser concedida somente a quem tem vínculo
  CPAEG ativo, DEVE ser definida num único ponto, junto às demais regras de governança, e
  NÃO DEVE ser concedida a CSAEG, a operador sem vínculo, a privilégio técnico ou ao modo
  ligado em si. Revogar o vínculo DEVE surtir efeito na requisição seguinte.
  [Interpretação C1, C2; 004/DP-402; Const. — X]
- **FR-004**: A capacidade "gerir Campanha" NÃO DEVE conceder publicação de Versão, edição
  de instrumento, definição de abrangência, remoção de Campanha, mobilização, consulta de
  respostas identificadas ou qualquer capacidade além das ações de FR-008 a FR-021.
  [Interpretação C4]
- **FR-005**: Lista e detalhe da 011 DEVEM continuar como estão para quem não tem a
  capacidade: mesmas Campanhas visíveis, mesmos dados, mesmo escopo, nenhuma ação nova. A
  única mudança visível a todos é a apresentação da Campanha nunca aberta com período
  expirado (FR-023a). [011]

#### Integração ao shell administrativo

- **FR-006**: A gestão DEVE se integrar às páginas de Campanhas da 011, com o mesmo shell,
  trilha e estilos: "Nova Campanha" na lista; as ações de estado no detalhe. NÃO DEVE criar
  módulo, menu global ou painel administrativo paralelo. [Solicitante; 011; 016]
- **FR-007**: As páginas de lista e detalhe da 011 DEVEM continuar somente leitura. Toda
  gravação DEVE ocorrer em ações próprias da 017, que exigem confirmação ou submissão
  explícita. Nenhuma gravação DEVE ocorrer por GET. [011 FR-001; Arquitetura]

#### Criar e editar enquanto nunca aberta

- **FR-008**: O operador gestor DEVE poder criar uma Campanha informando **nome** e
  **Versão**, e, opcionalmente, o **período** (início e fim). A Campanha DEVE nascer sem
  critérios de abrangência (população ampla). Se o período for informado, criação e
  período DEVEM ser gravados juntos ou não ser gravados. [Solicitante; 004 FR-007, FR-013,
  FR-019, FR-035]
- **FR-009**: A escolha de Versão DEVE oferecer somente Versões PUBLICADA, de qualquer
  Pesquisa, rotuladas "Pesquisa — designação". Se nenhuma existir, a interface DEVE informar
  isso e que a publicação não é feita aqui, sem oferecer formulário de criação.
  [Solicitante; 002/DP-001; 009 FR-076]
- **FR-010**: O período DEVE ser opcional para criar e salvar, e exigido só para abrir
  (FR-016). Informado, DEVE ter as duas datas, com início anterior ou igual ao fim; só uma
  data DEVE ser rejeitada. Depois de definido, o período PODE ser corrigido, mas NÃO DEVE
  poder ser removido pela interface, e a tentativa DEVE ser explicada sem gravar nada. NÃO
  DEVE haver data ou duração padrão, nem sugestão de periodicidade. [Solicitante; 004
  FR-012 a FR-014; DP-401]
- **FR-011**: O operador gestor DEVE poder editar ("Editar configuração") nome, Versão e
  período de Campanha **nunca aberta**, em qualquer estado temporal, inclusive ENCERRADA pelo fim do período sem
  abertura. As alterações de uma submissão DEVEM ser gravadas juntas ou não ser gravadas.
  [004 FR-008, FR-013, FR-043]
- **FR-012**: Se a Versão atual de Campanha nunca aberta estiver em RASCUNHO, a edição DEVE
  mostrá-la pré-selecionada e identificada como não publicada e impeditiva da abertura;
  nenhum outro rascunho DEVE ser oferecido. [Hipótese; 004 FR-010]
- **FR-013**: Para Campanha já aberta, a interface NÃO DEVE oferecer edição, e qualquer
  tentativa direta DEVE ser recusada sem gravar nada, com a mensagem de que Campanha aberta
  não muda e de que mudanças exigem nova Campanha. [004 FR-043, FR-047; Const. — VIII]
- **FR-014**: Rejeições DEVEM vir do domínio da 004, sem reimplementação no formulário.
  Cada motivo DEVE virar mensagem clara junto ao campo correspondente, preservando os
  valores digitados. Formato de data inválido é erro de entrada, tratado antes do domínio.
  [004 FR-057; padrão do editor (009)]
- **FR-015**: Criar e editar NÃO DEVEM alterar critérios existentes, Versão, Pesquisa,
  Participação ou Resposta. [004 FR-006; ADR 0004]

#### Estado, impedimentos e ações

- **FR-016**: O detalhe DEVE mostrar ao operador gestor, para Campanha nunca aberta,
  **todos** os impedimentos de abertura no momento da consulta (Versão não publicada;
  período não definido; hoje antes do início, com a data a partir da qual será possível;
  período encerrado sem abertura), cada um com a correção possível. Os impedimentos DEVEM derivar da
  mesma regra que a abertura da 004 aplica, sem cópia independente, e consultá-los NÃO
  DEVE gravar nada. [Solicitante; 004 FR-036; Const. — XXII]
- **FR-017**: As ações oferecidas DEVEM depender do estado e da abertura histórica:

  | Situação | Ações de gestão oferecidas |
  | --- | --- |
  | Nunca aberta, sem impedimentos (EM PREPARAÇÃO) | Editar configuração, Abrir coleta |
  | Nunca aberta, com impedimentos (EM PREPARAÇÃO) | Editar configuração |
  | Período encerrado — Campanha nunca aberta | Editar configuração |
  | EM COLETA | Encerrar coleta |
  | ENCERRADA depois de aberta | nenhuma |

  Um controle que inevitavelmente falharia por condição conhecida no momento da exibição
  NÃO DEVE ser oferecido, nem desabilitado sem explicação. [Solicitante; 004 FR-034 a
  FR-044]
- **FR-018**: Abrir DEVE exigir confirmação explícita, que informe o que fica fixado, que a
  Campanha passa a aceitar respostas imediatamente e que não há reabertura nem prorrogação.
  Se a data de referência for o último dia do período, a confirmação DEVE informar que a
  coleta se encerra ao fim desse mesmo dia.
  Confirmado, DEVE chamar a abertura da 004 e nada mais. NÃO DEVE publicar Versão, agendar
  nem notificar. [004 FR-009, FR-036, FR-042; DP-405]
- **FR-019**: Se houver outras Campanhas EM COLETA, a confirmação de abertura DEVE mostrar
  um aviso informativo simples — "Já existem outras Campanhas em coleta. Isso pode fazer
  com que alguns egressos tenham mais de uma pesquisa disponível." — e os nomes dessas
  Campanhas. NÃO DEVE bloquear, priorizar, calcular interseção de abrangências nem prever
  impacto. [Solicitante; 004 FR-051; 004/DP-404]
- **FR-020**: Encerrar DEVE ser oferecido somente para Campanha EM COLETA e DEVE exigir
  confirmação explícita, que informe que novas respostas deixam de ser aceitas, que as
  Participações existentes são preservadas e que não há reabertura. Confirmado, DEVE chamar
  o encerramento da 004 e nada mais. [004 FR-038, FR-040; DP-405]
- **FR-021**: Quando a condição mudar entre exibição e submissão, a interface DEVE mostrar a
  rejeição ou o estado atual informados pelo domínio, sem gravação parcial. Repetir uma
  abertura ou um encerramento já feitos NÃO DEVE alterar nada e DEVE informar o estado atual.
  [004 FR-037, FR-040, FR-057]

#### Consulta e abrangência

- **FR-022**: O detalhe e a edição DEVEM mostrar, somente quando a Campanha tiver algum
  critério de abrangência definido, um aviso de leitura com os critérios, dizendo que
  expressam a abrangência do instrumento, que foram definidos fora desta interface e que
  não são alterados por ela. Campanha sem critério NÃO DEVE exibir seção de critérios nem
  de público. [ADR 0004; 004 FR-018, FR-045]
- **FR-023**: O detalhe DEVE mostrar, conforme o estado: Versão, período, momento da
  abertura, "Encerramento previsto" (data final do período) quando EM COLETA, e momento e
  forma do encerramento quando ENCERRADA depois de aberta. Os indicadores e a entrada da
  comunicação simulada da 011/016 DEVEM permanecer como estão. [004 FR-045; 011; 016]
- **FR-023a**: Campanha nunca aberta cujo período expirou DEVE ser apresentada, na lista e
  no detalhe, como "Período encerrado — Campanha nunca aberta", com o aviso de que não houve
  coleta, e nunca apenas como "Encerrada". Para o operador gestor, o detalhe DEVE oferecer
  "Editar configuração". Isso é só apresentação: o estado de domínio continua ENCERRADA
  (004 FR-034, FR-038), e as regras que dependem dele, inclusive as da 016, não mudam.
  [Solicitante; 004 FR-039, FR-043]
- **FR-024**: A interface NÃO DEVE oferecer critérios de abrangência, filtros de público,
  lote, coorte, foco de divulgação, lista de destinatários ou seleção de egressos, nem como
  opção "avançada". [Solicitante; ADR 0004; 004 FR-049]

#### Preservação e fronteiras

- **FR-025**: A 017 NÃO DEVE criar entidade, campo, estado ou migração. Campanha, Versão,
  Participação, Resposta e vínculos DEVEM permanecer com os modelos atuais. [Const. — XXII]
- **FR-026**: A 017 NÃO DEVE alterar o comportamento das operações e consultas da 004 nem
  as regras de admissão da 005 e de entrada da 007/008. Expor os impedimentos de abertura
  (FR-016) PODE reorganizar a verificação existente em uma consulta compartilhada, mantidos
  resultado, ordem e motivos das rejeições. [004; 005 FR-014; Arquitetura]
- **FR-027**: A 017 NÃO DEVE registrar autoria, histórico de alterações ou trilha de quem
  criou, abriu ou encerrou a Campanha. [004 FR-046; DP-1701]
- **FR-028**: Todas as mensagens ao operador DEVEM estar num vocabulário fechado, em
  português institucional, sem nomes técnicos de motivo, identificador interno ou dado
  pessoal. [009; 011; Const. — XX]
- **FR-029**: As páginas DEVEM ser acessíveis e responsivas como as da 011: rótulos
  associados aos campos, erros anunciados, foco no primeiro erro, ações por teclado e sem
  dependência de recurso externo. [Const. — XX, XXI; 015]

### Matriz mínima de verificação automatizada

| Verificação | Cobre |
| --- | --- |
| CPAEG cria Campanha ampla com nome e Versão, com e sem período; nada de critério gravado | FR-008, FR-009, FR-015 |
| Formulário não oferece rascunho nem campo de abrangência/público | FR-009, FR-024 |
| Rejeições de nome, período com uma só data, invertido ou removido viram mensagens por campo, sem gravação | FR-010, FR-014 |
| Edição de nunca aberta (inclusive expirada) grava; de aberta é recusada sem gravação | FR-011, FR-013 |
| Versão atual em rascunho aparece marcada e é a única não publicada | FR-012 |
| Impedimentos coincidem com os motivos de rejeição de `abrir` para os mesmos dados e momento | FR-016, FR-026 |
| Matriz de ações por situação; nunca aberta e expirada apresentada como "Período encerrado — Campanha nunca aberta" na lista e no detalhe | FR-017, FR-023a |
| Aviso de sobreposição aparece só com outra Campanha EM COLETA, lista nomes e não bloqueia | FR-019 |
| Abrir e encerrar só por POST confirmado; repetição não altera nada | FR-007, FR-018, FR-020, FR-021 |
| CSAEG, sem vínculo, sem operador, vínculo revogado e modo desligado: recusa/inexistência em toda rota | FR-001 a FR-005 |
| Lista e detalhe da 011 iguais para CSAEG antes e depois da 017, salvo o rótulo de FR-023a; suítes 004–016 inalteradas | FR-005, FR-026 |
| Nenhuma migração nova; nenhum campo ou registro de autoria | FR-025, FR-027 |
| Nenhuma tela de gestão mostra nome técnico de motivo nem identificador fora de links | FR-028 |

### Key Entities *(include if feature involves data)*

Nenhuma entidade nova.

- **Campanha** *(004, inalterada)*: nome, Versão, período, critérios de abrangência,
  momentos de abertura e encerramento; estado derivado. A 017 só a cria, edita enquanto
  nunca aberta, abre e encerra pelas operações da 004.
- **Versão da Pesquisa** e **Pesquisa** *(002, somente leitura)*: a 017 lista as Versões
  PUBLICADA e nunca altera estado ou conteúdo.
- **Vínculo de governança** *(010, somente leitura)*: decide a capacidade "gerir Campanha"
  (FR-003).
- **Impedimento de abertura** *(valor derivado, não persistido)*: condição da 004 FR-036
  não satisfeita no momento da consulta.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem | Fonte ou regra | Tratamento de divergência |
| --- | --- | --- | --- |
| Nome, Versão e período da Campanha | Configuração institucional (não é dado sobre egresso) | Informados pelo operador gestor fictício (C1); competência real em 004/DP-402 | Não se aplica; fixados na abertura (004 FR-043) |
| Estado, encerramento previsto e efetivo | Derivado | Regras da 004 sobre período, abertura e encerramento | Não persistido além de `aberta_em` e `encerrada_em` da 004 |
| Impedimentos de abertura | Derivado | Mesma regra da abertura da 004 | Recalculados a cada consulta e de novo na submissão |
| Versões disponíveis | Institucional (configuração do instrumento) | Versões PUBLICADA da 002 | Não se aplica |
| Capacidade do operador | Configuração de governança fictícia | Vínculos ativos da 010 | Relidos a cada requisição |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um operador gestor cria uma Campanha ampla com nome e Versão, ou já com o
  período, numa única tela e numa única submissão, em menos de 2 minutos na primeira
  tentativa; completar o período depois exige uma única edição.
- **SC-002**: Com a Campanha pronta, abrir a coleta exige no máximo duas ações (acionar e
  confirmar); o mesmo vale para encerrar.
- **SC-003**: Em 100% das situações da matriz de FR-017, só são oferecidas as ações
  admitidas. Nenhuma ação oferecida é rejeitada por condição já conhecida na exibição.
- **SC-004**: Em 100% das tentativas de gravar Campanha já aberta, nada é alterado.
- **SC-005**: Em 100% das requisições de gestão por operador sem a capacidade, ou com o modo
  desligado, nada é exposto nem gravado.
- **SC-006**: Toda Campanha criada pela interface tem zero critérios de abrangência, e
  nenhuma tela da 017 oferece campo de público, filtro ou lote.
- **SC-007**: Diante de um impedimento, o operador identifica a causa e a correção pela
  própria tela, sem consultar documentação: cada impedimento tem texto de causa e de ação.
- **SC-008**: Zero migrações, entidades ou estados novos; as suítes existentes das features
  001–016 continuam passando; os inventários de rotas da 011/016 passam a ser verificações
  semânticas de barreira e método, sem contagem de rotas.

## Assumptions

- **Base**: `main` em `5e50fec`, com a 016 e a ADR 0004. O shell administrativo da 011 e o
  padrão de formulários do editor (009) são reutilizados.
- **Escolha restrita a Versões PUBLICADA** [Hipótese; Solicitante]: mais estrita que a 004,
  só na interface. Preparar com rascunho continua possível por meio técnico, e uma Campanha
  assim continua editável pela 017 (FR-012).
- **Relógio do servidor**: "hoje" é a data de referência da 004, na timezone configurada.
  A disponibilidade de "Abrir coleta" é avaliada na exibição e de novo na submissão.
- **Granularidade diária**: herdada da 004; sem horário de abertura ou encerramento.
- **Rótulos de estado**: os da 011 ("Em preparação", "Em coleta", "Encerrada"), mais
  "Período encerrado — Campanha nunca aberta" para a Campanha nunca aberta com período
  expirado (FR-023a).
- **Demonstração**: o cenário existente basta. A "rodada em preparação" (Versão em
  rascunho, sem período) exercita impedimento e correção; a cópia publicada de 2024
  exercita criação e abertura. Nenhum dado novo do cenário é necessário.

## Relação com outras features

**002** — consumida sem alteração: só Versões PUBLICADA são oferecidas; publicar continua
sem superfície (002/DP-001).

**004** — consumida sem mudança de comportamento: a 017 é o primeiro consumidor de
interface de `criar_campanha`, `alterar_campanha`, `definir_periodo`, `abrir` e `encerrar`.
`definir_criterios` e `remover_campanha` não são expostos.

**005/007/008** — inalteradas: abrir torna a Campanha respondível pelas regras existentes;
encerrar faz a 005 recusar novas Participações.

**009** — inalterada; continua sem publicação.

**010** — uma regra de capacidade nova, CPAEG apenas (C1). Papéis, escopos e vínculos não
mudam.

**011** — lista e detalhe recebem pontos de entrada da 017 só para o operador gestor;
continuam somente leitura. A situação da Campanha nunca aberta com período expirado passa a
ser apresentada a todos como "Período encerrado — Campanha nunca aberta" (FR-023a).

**016** — inalterada; a entrada "Comunicação simulada" continua nos três estados, como na
016 FR-007. O esboço do solicitante, que a mostra só EM COLETA, é atendido pela 016 sem
mudança.

### Impacto nas features anteriores (notas de revisão a aplicar com a 017)

Nenhuma regra de domínio muda. Estas cláusulas recebem nota "*(Revisado pela 017)*",
restrita ao modo de demonstração:

| Cláusula | Nota de revisão |
| --- | --- |
| 004 FR-056; DP-402 (tratamento provisório) | Exposição limitada à demonstração, à CPAEG ativa, por interpretação C1; DP-402 continua aberta |
| 010 FR-033, FR-073 | A capacidade de gerir Campanha passa a existir só como regra de demonstração da 017 |
| 011 FR-001, FR-016, FR-100 | Lista e detalhe seguem somente leitura; a gestão pertence às ações da 017 |
| 011, rótulo de situação na lista e no detalhe | Nunca aberta com período expirado: "Período encerrado — Campanha nunca aberta" (FR-023a) |
| 016 FR-003 | Sem mudança: a comunicação continua não concedendo gestão; a 017 concede separadamente |

Os testes de inventário de rotas da 011/016 hoje fixam a quantidade de rotas. Eles passam
a verificar semanticamente barreira e métodos por rota, sem contagem: a quantidade de rotas
não é invariante de produto.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I, VII — Longitudinalidade; conceitos distintos**: a Campanha continua entidade própria,
  ligada a uma Versão; nenhuma Participação é criada, alterada ou consumida.
- **II — Definição de egresso**: a Campanha criada é ampla; nenhum critério redefine quem
  é egresso.
- **VIII — Preservação histórica**: só Versão PUBLICADA é oferecida; Campanha aberta não muda
  (FR-013); sem reabertura ou prorrogação.
- **IX — Periodicidade configurável**: nenhuma duração ou periodicidade padrão (FR-010);
  periodicidade real em DP-401.
- **X — Tecnologia não redefine governança**: a capacidade vem de interpretação identificada,
  limitada à demonstração (C1–C4); acesso técnico não autoriza; DP-402 e 002/DP-001 seguem
  abertas; nenhum workflow de aprovação.
- **XII, XVI — Escopos e menor privilégio**: CSAEG não gere rodada institucional (C2).
- **XIV — Redução de fricção**: abrir torna a pesquisa acessível sem convite, como na 004.
- **XIX, XX, XXI**: sem dashboard novo; telas acessíveis e responsivas no shell existente.
- **XXII — YAGNI**: zero entidade nova; reutiliza operações, páginas e padrão de formulários;
  critérios, remoção, lote e agendamento ficam fora por falta de consumidor.
- **XXIX — Hipóteses não viram requisitos**: escolhas reversíveis marcadas [Hipótese] e
  [Interpretação]; competências pendentes registradas.

**Tensão tratada**: expor gestão contraria a literalidade de 004 FR-056 e 011 FR-100. Essas
cláusulas são revisadas apenas para a demonstração, sem conclusão institucional, para que o
produto exercite o ciclo completo antes do piloto.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence ao acompanhamento?** Sim; Campanha está na fronteira do domínio do NIAE (004).
2. **É necessária ao ciclo?** Sim; sem abrir uma Campanha não há coleta.
3. **Existe solução institucional mais adequada?** Não para a rodada do NIAE.
4. **Integração seria suficiente?** Não; a operação é sobre o próprio domínio.
5. **Aumenta acoplamento?** Não: interface sobre operações existentes; o domínio não conhece
   a interface.

## Out of Scope *(mandatory)*

- Lote, coorte ou foco de mobilização; filtros de divulgação; mailing; lista de
  destinatários; comunicação real (a simulada segue na 016).
- Critérios de abrangência na interface, inclusive tela "avançada"; `definir_criterios`
  continua só técnico.
- Publicação de Versão, workflow de aprovação, novos estados de Versão, editor do
  instrumento.
- Agendamento, scheduler, job, abertura ou encerramento automáticos.
- Prorrogação, reabertura, suspensão, cancelamento, arquivamento, duplicação de Campanha.
- Remoção de Campanha nunca aberta (existe no domínio; sem consumidor concreto agora).
- Campanha de unidade ou gestão por CSAEG (DP-403).
- Autoria, histórico ou trilha de auditoria da gestão (DP-1701).
- Identidade real do egresso ou do operador; autenticação; `FormacaoDeclarada`.
- Alterações em Participação, Resposta, elegibilidade ou entrada; snapshot da população;
  exportação.
- Qualquer superfície fora do modo de demonstração.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Todas seguem abertas e não bloqueiam a demonstração. Indica-se quando bloqueiam o piloto.

### Herdadas, explicitamente preservadas

| Referência | DECISÃO PENDENTE | Tratamento da 017 |
| --- | --- | --- |
| **004/DP-402** | Quem cria, configura, abre, encerra e remove Campanha; Proex/CPAEG (Art. 26) | Interpretação C1 só na demonstração; **bloqueia o piloto** |
| **002/DP-001** | Quem publica Versão; Proex/CPAEG (Art. 26) | Só Versões já publicadas; nenhuma publicação; **bloqueia o piloto** (dependência pré-piloto) |
| **002/DP-002** | Processo de elaboração, revisão e aprovação da Versão | Nenhum workflow; **bloqueia o piloto** junto com DP-001 |
| **004/DP-401** | Periodicidade, duração e edição oficial das rodadas; Proex/Proen | Nenhum padrão; período digitado não é regra (C3) |
| **004/DP-403** | Campanhas de unidade | CSAEG não gere; nenhuma Campanha por unidade pela interface |
| **004/DP-404**, **007/DP-701** | Campanhas sobrepostas em coleta | Aviso na confirmação; sem bloqueio nem prioridade (FR-019) |
| **004/DP-405** | Prorrogação, reabertura, correção após abertura | Nada disso é oferecido; confirmações dizem isso |
| **010/DP-1001**, **DP-1002**, **DP-1003** | Identificação produtiva de operadores; registro de vínculos; atuação em nome da CPAEG | Operadores fictícios; nenhuma superfície produtiva |

### Nova

| ID | DECISÃO PENDENTE e instância competente | Impacto e tratamento provisório |
| --- | --- | --- |
| **DP-1701** | Se a instituição exige registro de quem criou, alterou, abriu ou encerrou uma Campanha, com que finalidade e retenção; CPAEG/Proex com DTI e encarregado | Sem operadores reais, a autoria não tem significado; nenhum registro (FR-027); decidir antes do piloto junto com 010/DP-1001 |

### Decisões do solicitante antes do `/speckit-plan`

Resolvidas em Clarifications (2026-10-03): período opcional até a abertura; apresentação
própria da Campanha nunca aberta com período expirado; aviso simples de sobreposição. As
demais escolhas foram aprovadas: governança CPAEG só na demonstração (C1, C2); remoção fora;
aviso de leitura dos critérios só quando houver restrição (FR-022); confirmação explícita
para abrir e encerrar (FR-018, FR-020). Nenhuma pergunta bloqueante permanece.
