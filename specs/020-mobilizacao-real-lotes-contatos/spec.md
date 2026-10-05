# Feature Specification: Mobilização real, Lotes e contatos do egresso

**Feature**: `020-mobilizacao-real-lotes-contatos`

**Feature Branch**: `claude/feature-020-audit-8056d5` (atualizada com a `main` em
`04efabd`, com 019, 021 e 022 mergeadas)

**Created**: 2026-10-04

**Status**: Esclarecida em 2026-10-05. Revisada no mesmo dia, depois da atualização com a
`main` (021 e 022): contato importado por capacidade separada (FR-005 a FR-007) e convite
secundário na conclusão (FR-009, E7). Escolhas E1 a E7 decididas pelo solicitante (ver
Clarifications). Plan, tasks e `/speckit-analyze` concluídos em 2026-10-05, com os achados
críticos corrigidos. Especificada; não implementada; envio real **não habilitado** (Gates A
e B).

**Input**: "Feature 020 — Mobilização real, Lotes e contatos do egresso", com base na
[auditoria da 020](../../docs/auditorias/2026-10-04-mobilizacao-real-lotes-contatos.md)
(§22).

## Contexto

> Mobilizar um grupo não significa restringir quem pode responder.

A 016 exercitou a comunicação com um público recalculado a cada execução, contatos fixos no
código e nada persistido. Ela mesma declarou que esse público era "substituto temporário
… antes da existência de Lote" (016, Contexto; ADR 0004).

A 020 introduz três coisas:

1. o **contato de e-mail da Pessoa**, com proveniência;
2. o **Lote de Mobilização**, uma onda operacional e reproduzível de abordagem dentro de
   uma Campanha;
3. o **envio por e-mail** dos membros do Lote, com registro honesto do resultado.

O envio real fica desativado até as decisões institucionais do Gate B.

**Dados.** O sistema não está conectado à base acadêmica real. Esta spec não pressupõe
cobertura, formato, atualidade ou multiplicidade de contatos na fonte, nem que ela ofereça
telefone. Tudo isso é Gate A (ver "Gates").

**Invariantes de produto**:

- Lote não é população da pesquisa e não altera a abrangência da Campanha (ADR 0004).
- Lote não cria Participação, não concede identidade e não concede acesso.
- Uma Pessoa fora de qualquer Lote responde normalmente se a formação estiver na
  abrangência.
- O link do convite é neutro, igual para todos, sem token nem identificador
  (016 FR-021/022; 018 FR-053).
- Pertencer a um Lote não prova que a comunicação causou uma resposta.

### Escolhas desta spec (decididas em 2026-10-05)

| # | Escolha | Alternativa preterida | Fundamento | Decisão |
| --- | --- | --- | --- | --- |
| E1 | Só e-mail; telefone/WhatsApp não coletados | Coletar telefone declarado já | Sem consumidor (Const. XVI); canal fora de escopo (DP-1608) | Confirmada; WhatsApp pendente até haver finalidade e uso concreto (DP-2009) |
| E2 | E-mail guardado legível, protegido por controles de aplicação e de infraestrutura | Criptografia de aplicação como a ADR 0005 | E-mail não é fator de verificação; cifragem seria analogia com CPF, não risco equivalente (auditoria §5.5) | Aceita **só na demonstração**; o plan justifica os controles; revisão obrigatória antes do uso real (DP-2010, Gate B) |
| E3 | Lote nasce congelado a partir de uma prévia transitória | Rascunho de Lote persistido | Sem caso concreto para retomar preparação; evita um estado | Mantida |
| E4 | Membro sem contato pode entrar num Lote posterior da mesma Campanha; demais situações não | Excluir qualquer membro anterior | Ninguém foi abordado; permite alcançar quem informar e-mail depois | Mantida |
| E5 | O egresso não vê o contato guardado | Mostrar e permitir editar | O acesso da 018 é proporcional à pesquisa, não a cadastro; evita revelação de dado pessoal | Mantida |
| E6 | O contato usado no envio é o congelado no Lote | Contato vigente no instante do envio | Histórico não depende do momento do clique | Mantida |
| E7 | Convite de e-mail como ação secundária na tela de conclusão, abaixo de "Ver minha trajetória no Ifes"; a 021 FR-003 passa de "única ação" a "ação principal" | Convite dentro da Minha Trajetória; ou só em `/formacoes/` | Mantém o convite logo após a conclusão sem acoplar contato à devolutiva (021 FR-009) nem disputar a ação principal (auditoria §7.1) | Confirmada; impacto compartilhado na tela de conclusão explicitado (ver Clarifications e Relação) |

### Base existente

Inventário completo na auditoria (§§2–4). Fatos que decidem esta spec:

| Fato | Evidência | Consequência |
| --- | --- | --- |
| `Pessoa` não tem contato; o contrato da fonte também não | `academico/models.py`, `fonte_academica/contrato.py` | Contato é registro próprio |
| A 021 enriqueceu por capacidade separada da `FonteAcademica`, com carga própria, sem tocar `PessoaEncontrada` nem a incorporação (021 FR-071) | `fonte_academica/contexto_da_trajetoria.py`, `contexto_trajetoria/carga.py` | Contato importado segue o mesmo precedente: capacidade e carga separadas |
| A conclusão ancorada em Conclusão tem uma única ação, "Ver minha trajetória no Ifes" (021 FR-003) | `interface/templates/interface/concluida.html` | Convite de e-mail é secundário; revisão pontual da 021 FR-003 (E7) |
| 021 e 022 declaram "020: independente" (021 FR-009, FR-070) | specs 021 e 022 | Nenhum benefício depende de contato, e o contato não depende da narrativa |
| Único contato existente é um mapa fictício fixo | `comunicacao/contatos.py:5-23` | Passa ao adaptador simulado de contatos |
| Seleção da 016: abrangência → escopo → Pessoas distintas → contato | `comunicacao/consultas.py:35-52` | Base da seleção do Lote |
| Renderer, validação de conteúdo e barreiras de transporte da 016 | `comunicacao/convite.py`, `seguranca.py` | Reutilizados como modo demonstração |
| Estado da Campanha é derivado | `campanha/consultas.py:40-74` | O Lote não copia estado; revalida em cada ação |
| 012 e 013 sem Pessoa, nome, e-mail ou telefone, com testes de fronteira | `tests/analitico/test_analitico_fronteiras.py:57-68`, `tests/exportacao/test_exportacao_fronteiras.py` | Contato e Lote ficam fora por construção |
| Sessão do egresso guarda só a Pessoa | `acesso/sessao.py:21-27` | Atualização de e-mail usa a Pessoa da sessão |
| Sessão de declarante (019) não tem Pessoa | `interface/views.py:98-108` | Oferta de contato não aparece para declarante |

## Clarifications

### Session 2026-10-05

- Q: E1 — a 020 coleta só e-mail ou também telefone/WhatsApp? → A: Só e-mail.
  WhatsApp e telefone ficam pendentes até haver finalidade e uso concreto (DP-2009).
- Q: E2 — o e-mail pode ficar guardado legível? → A: Sim, **somente na demonstração**.
  - O plan DEVE justificar os controles de proteção (acesso só por operações nomeadas,
    ausência em saídas, testes de fronteira, nenhuma tela com endereço).
  - Antes de qualquer uso real, a proteção em repouso DEVE ser revista e a decisão
    registrada (DP-2010, item do Gate B, FR-033).
- Q: E3 a E6 continuam como propostas? → A: Sim, mantidas sem alteração.
- Q: E7 — o convite de e-mail fica na tela de conclusão como ação secundária? → A: Sim.
  - A independência **funcional** de 021 e 022 continua: nenhum benefício depende de
    contato, e o contato não depende da narrativa ou do vídeo.
  - Essa independência **não elimina o impacto compartilhado** da 020 na tela de
    Participação concluída, que a 014 e a 021 também definem.
  - A 020 faz revisão pontual da **021 FR-003** ("única ação" → "ação principal") e, por
    consequência, da **014 FR-041**. A 020 registra essas notas de revisão nas duas specs
    ao implementar.
- Q: Como a documentação institucional deve tratar a 020? → A: Atualizar já, na
  consolidação da spec, distinguindo três estados: **especificada** (agora), **implementada**
  (após a implementação, restrita à demonstração) e **habilitada para uso real** (só depois
  dos Gates A e B).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preparar e confirmar um Lote de Mobilização (Priority: P1)

Uma operadora CPAEG abre uma Campanha e entra em "Lotes de mobilização". Ela escolhe
filtros (unidades, nível, faixa de ano de conclusão e, opcionalmente, curso) e vê uma prévia:

- Pessoas distintas selecionadas;
- com contato;
- sem contato;
- excluídas por já terem sido mobilizadas nesta Campanha.

Ela dá um nome curto e confirma. O Lote fica gravado com seus membros e o contato escolhido
para cada um.

**Why this priority**: sem seleção congelada não há histórico reproduzível nem proteção
contra disparo repetido. É o núcleo da 020.

**Independent Test**: na demonstração, confirmar um Lote e verificar membros, contatos
escolhidos e contagens, sem enviar nada.

**Acceptance Scenarios**:

1. **Given** uma Campanha EM PREPARAÇÃO ou EM COLETA visível à operadora, **When** ela
   ajusta os filtros, **Then** a prévia é recalculada e nada é gravado.
2. **Given** uma Pessoa com duas Conclusões que satisfazem os filtros, **When** o Lote é
   confirmado, **Then** ela é um único membro.
3. **Given** uma Pessoa com uma Conclusão em Serra e outra em Vitória, e uma operadora CSAEG
   Serra, **When** a operadora confirma um Lote, **Then** a Pessoa entra uma vez, pela
   Conclusão de Serra, e nenhuma informação de Vitória aparece.
4. **Given** uma Pessoa sem contato utilizável, **When** o Lote é confirmado, **Then** ela é
   membro na situação "sem contato" e continua podendo responder espontaneamente.
5. **Given** uma Campanha ENCERRADA, **When** a operadora tenta confirmar um Lote, **Then**
   a ação é recusada.
6. **Given** um Lote confirmado, **When** alguém tenta alterar filtros ou membros, **Then**
   não há ação disponível e o servidor recusa.

---

### User Story 2 - Enviar um Lote e entender o resultado (Priority: P1)

Com a Campanha EM COLETA, a operadora aciona "Enviar Lote". O sistema tenta uma mensagem
por membro com contato e registra a situação de cada um. O resultado mostra:

- membros;
- sem contato;
- submetidos ao transporte;
- falhas de transporte;
- não tentados;
- resultado incerto.

A tela avisa que aceite do transporte não comprova entrega nem causa resposta.

**Why this priority**: é a mobilização propriamente dita.

**Independent Test**: em teste e em demonstração, enviar um Lote e conferir mensagens
capturadas, situações persistidas e contagens.

**Acceptance Scenarios**:

1. **Given** um Lote confirmado e a Campanha EM COLETA, **When** a operadora envia,
   **Then** cada membro com contato recebe no máximo uma tentativa, e a situação de cada
   membro é gravada no momento da tentativa.
2. **Given** um envio interrompido no meio, **When** a operadora aciona a ação de novo,
   **Then** apenas membros "não tentados" são processados, e ninguém recebe segunda
   mensagem.
3. **Given** um membro cuja tentativa começou e cujo resultado não foi registrado, **When**
   o envio é retomado, **Then** ele aparece como "resultado incerto" e não é tentado de
   novo.
4. **Given** a Campanha EM PREPARAÇÃO ou ENCERRADA, **When** a operadora tenta enviar,
   **Then** a ação é recusada e os membros permanecem "não tentados".
5. **Given** a mensagem enviada, **When** o destinatário segue o link, **Then** chega à
   entrada neutra, que não identifica, autentica, seleciona formação nem cria Participação.
6. **Given** o modo real desativado, **When** qualquer operadora tenta enviar fora de teste
   e demonstração, **Then** nada é transmitido e o motivo é informado por categoria.

---

### User Story 3 - Evitar mobilização duplicada na mesma Campanha (Priority: P1)

A operadora prepara um segundo Lote da mesma Campanha com filtros que se sobrepõem ao
primeiro. Quem já foi abordado ou está aguardando envio no primeiro Lote não entra no
segundo. Quem ficou sem contato no primeiro pode entrar.

**Why this priority**: disparo repetido para a mesma Pessoa é o erro operacional mais
provável e mais visível.

**Independent Test**: confirmar dois Lotes sobrepostos e verificar exclusões e contagem de
excluídos.

**Acceptance Scenarios**:

1. **Given** P membro "submetido" do Lote A da Campanha X, **When** o Lote B de X é
   confirmado com filtros que incluem P, **Then** P não é membro de B, e B conta P entre
   os "já mobilizados nesta Campanha".
2. **Given** P membro "não tentado", "falha", "em tentativa" ou "incerto" em A, **When** B
   é confirmado, **Then** P também é excluído.
3. **Given** P membro "sem contato" em A e que depois informou e-mail, **When** B é
   confirmado, **Then** P é membro de B com o e-mail informado.
4. **Given** P mobilizado na Campanha X, **When** um Lote da Campanha Y é confirmado,
   **Then** a mobilização em X não exclui P.
5. **Given** dois Lotes de X confirmados em concorrência com P em ambos, **When** os dois
   são enviados, **Then** P recebe no máximo uma mensagem em X.

---

### User Story 4 - Egresso atualiza voluntariamente seu e-mail (Priority: P2)

Ao concluir a pesquisa, o egresso vê como ação principal "Ver minha trajetória no Ifes"
(021) e, abaixo, com menor destaque, um convite opcional: "Quer manter seu e-mail
atualizado com o Ifes?". Se aceitar, informa um e-mail numa página própria, que explica a
finalidade e que o e-mail não será público. "Agora não" encerra sem consequência.

**Why this priority**: é a única forma de melhorar contatos antes do Gate A e não depende
dele. Não bloqueia os Lotes.

**Independent Test**: concluir uma Participação na demonstração, informar e-mail e verificar
o registro com origem "egresso" e o contato anterior preservado.

**Acceptance Scenarios**:

1. **Given** um egresso com sessão da 018 na tela de Participação concluída, **When** a tela
   é exibida, **Then** "Ver minha trajetória no Ifes" continua a ação principal e há,
   abaixo e com menor destaque, um convite opcional para atualizar o e-mail, separado da
   confirmação e das Respostas.
2. **Given** o egresso na página de e-mail, **When** informa um endereço válido, **Then** um
   novo contato de origem "egresso" é gravado, com o momento, e o contato importado
   permanece.
3. **Given** o egresso informa um endereço inválido, **When** salva, **Then** recebe erro
   compreensível e nada é gravado.
4. **Given** um declarante da 019 (sem Pessoa), **When** conclui, **Then** a oferta não
   aparece.
5. **Given** a página de e-mail, **When** é exibida, **Then** não mostra nenhum contato
   guardado.
6. **Given** um egresso que não informa e-mail, **When** sai, **Then** nada muda em
   Participação, acesso ou elegibilidade.
7. **Given** o egresso que ignora o convite, **When** segue para a Minha Trajetória, **Then**
   a narrativa e o card estão disponíveis como antes, sem nenhuma etapa intermediária.

---

### User Story 5 - Histórico reproduzível de quem foi mobilizado e por qual contato (Priority: P2)

Depois de enviado um Lote, o egresso informa um e-mail novo. Ao consultar o Lote, a
operadora vê as mesmas contagens. O registro interno continua apontando o contato
efetivamente usado, com a origem e o momento de obtenção.

**Why this priority**: reprodutibilidade é requisito de auditoria e de interpretação, mas
não muda a operação diária.

**Independent Test**: congelar um Lote, acrescentar contato, enviar e verificar que a
mensagem foi para o contato congelado e que o registro não mudou.

**Acceptance Scenarios**:

1. **Given** o Lote A congelado em 04/10 com `antigo@…` para P, **When** P informa
   `novo@…` em 05/10 e A é enviado em 06/10, **Then** a mensagem de A vai para `antigo@…`,
   e o registro de A continua apontando `antigo@…` e sua origem.
2. **Given** um Lote B confirmado depois de 05/10, **When** P não foi mobilizado nesta
   Campanha, **Then** B usa `novo@…`.
3. **Given** qualquer Lote, **When** consultado, **Then** a interface mostra filtros,
   momento de confirmação, quem confirmou e contagens, sem lista individual, nomes ou
   endereços.

---

### User Story 6 - Contato importado da fonte acadêmica (Priority: P2)

Quando a fonte acadêmica fornece e-mail para uma Pessoa já incorporada, uma carga de
contatos, separada da incorporação, grava esse contato com origem "fonte acadêmica",
código da fonte e momento. Uma nova carga com valor novo acrescenta um registro, sem apagar
o anterior. Falha da carga nunca afeta acesso, incorporação ou resposta.

**Why this priority**: prepara o adaptador real sem depender dele. A demonstração usa só
endereços fictícios.

**Independent Test**: preparar a demonstração, verificar contatos importados fictícios,
a idempotência de uma nova carga e o isolamento diante de fonte de contatos
indisponível.

**Acceptance Scenarios**:

1. **Given** a fonte simulada de contatos com e-mail fictício para SIM-P-0001, **When** a
   carga de contatos roda depois da incorporação, **Then** existe um contato de origem
   "fonte acadêmica" com o endereço fictício.
2. **Given** a mesma observação, **When** a carga roda de novo, **Then** nenhum contato
   duplicado é criado.
3. **Given** a fonte passa a informar outro e-mail, **When** a carga roda, **Then** um novo
   contato é acrescentado, e o anterior é preservado.
4. **Given** a fonte não informa e-mail, **When** a carga roda, **Then** nenhum contato é
   criado e a Pessoa continua incorporada normalmente.
5. **Given** a fonte de contatos indisponível, **When** a demonstração é preparada ou o
   egresso acessa, **Then** a incorporação e o acesso (018) funcionam, nada de contato é
   gravado e a indisponibilidade não é tratada como "sem contato".

---

### User Story 7 - Governança e escopo dos Lotes (Priority: P2)

A CPAEG prepara e envia Lotes institucionais. A CSAEG prepara e envia Lotes restritos às
suas unidades e só vê esses Lotes. Quem apenas acompanha a coleta não prepara nem envia.

**Why this priority**: o envio é ação de risco e não pode decorrer de acesso técnico.

**Independent Test**: exercitar todas as rotas de Lote com cada perfil fictício.

**Acceptance Scenarios**:

1. **Given** uma CSAEG Vitória, **When** prepara um Lote, **Then** o filtro de unidade é
   obrigatório e limitado às suas unidades.
2. **Given** uma CSAEG Vitória, **When** lista os Lotes da Campanha, **Then** não vê Lotes
   que incluem outras unidades.
3. **Given** um operador sem vínculo ativo, **When** acessa qualquer rota de Lote, **Then**
   é recusado no servidor.
4. **Given** um vínculo desativado entre a confirmação e o envio, **When** a operadora
   tenta enviar, **Then** a capacidade é reavaliada e a ação é recusada.

### Edge Cases

- **Campanha encerra entre a confirmação e o envio**: o envio é recusado, e os membros
  permanecem "não tentados", sem nova situação.
- **Campanha sem critério e operadora CPAEG sem filtro**: o Lote abrange todas as Pessoas
  da população. A prévia exige confirmação explícita do número.
- **Prévia e confirmação divergem** (incorporação ou envio concorrente no intervalo): vale a
  seleção calculada na confirmação, e o resultado mostra as contagens efetivas.
- **Lote com zero membros**: não é confirmado; a interface explica o motivo (filtros vazios
  ou todos já mobilizados).
- **Pessoa com Conclusão fora da abrangência e outra dentro**: entra pela que está dentro.
  Abrangência é sempre o primeiro recorte.
- **Vários e-mails importados na mesma observação**: vale a ordem declarada pelo
  adaptador. Todos ficam registrados.
- **Contato importado sintaticamente inválido**: não é utilizável; a política passa ao
  próximo candidato e, sem candidato, a Pessoa fica "sem contato".
- **E-mail informado igual ao importado**: grava registro de origem "egresso". Origem é
  fato, não duplicata.
- **Egresso informa e-mail várias vezes**: vale o mais recente; todos permanecem.
- **Falha de transporte**: sem retry; a Pessoa não entra em novos Lotes da mesma Campanha
  (reenvio é DP-2005).
- **Erro do processo depois do submit**: "resultado incerto", nunca reenviado
  automaticamente.
- **Configuração de transporte inválida**: nenhuma conexão, nenhuma situação alterada,
  recusa por categoria.
- **Base com dados simulados no modo real, ou dados reais no modo demonstração**: recusa
  antes de qualquer mensagem.
- **Membro cuja Pessoa deixou de estar na população depois da confirmação**: o envio segue
  o congelado. O convite é neutro e a admissão continua decidida pela 004 na entrada.

## Requirements *(mandatory)*

### Functional Requirements

#### Contato da Pessoa

- **FR-001**: O sistema DEVE manter contatos de e-mail como registros próprios ligados à
  Pessoa, separados de `Pessoa` e de `ConclusaoAcademica`, com canal, valor, origem
  (`FONTE_ACADEMICA` ou `EGRESSO`), código da fonte quando importado e momento de
  obtenção. NÃO DEVE acrescentar contato a Pessoa ou Conclusão. [Arquitetura; Const. III,
  IV]
- **FR-002**: Registro de contato DEVE ser imutável. Informe do egresso ou observação nova
  da fonte DEVE acrescentar registro, nunca alterar ou apagar outro.
  - Uma **observação** é a lista ordenada de e-mails que a fonte informou para a Pessoa
    num momento.
  - Repetir a mesma lista, na mesma ordem e da mesma fonte, NÃO DEVE gravar nada.
  - Informe do egresso igual ao seu contato `EGRESSO` mais recente NÃO DEVE gravar nada.
  - Lista vazia NÃO DEVE gravar nem apagar.

  *(Precisão do plan, research R2: a idempotência é por observação, não por valor, para
  preservar a ordem do adaptador.)* [Arquitetura; Const. III]
- **FR-003**: O registro NÃO DEVE carregar qualidade, verificação, atualidade, "principal"
  ou "ativo". Origem não significa qualidade, e contato importado tem verificação e
  atualidade desconhecidas. [Const. XXII; Solicitante]
- **FR-004**: O único canal da 020 é e-mail. Telefone, celular e WhatsApp NÃO DEVEM ser
  coletados, importados ou armazenados. [Const. XVI; E1; DP-2009]

#### Contato importado

- **FR-005**: DEVE existir uma capacidade de contatos da fonte, separada da fronteira
  acadêmica. Para Pessoas já incorporadas, ela informa zero ou mais e-mails por Pessoa, na
  ordem de preferência declarada pelo adaptador, e distingue indisponibilidade de ausência.
  Peculiaridades da fonte ficam no adaptador.

  `FonteAcademica`, `PessoaEncontrada`, `ConclusaoNaFonte`, `CAMPOS_DE_CONTEXTO` e a
  incorporação da 001 NÃO DEVEM mudar. Acesso (018), incorporação (001), declaração e
  validação (019) NÃO DEVEM importar, chamar nem depender dessa capacidade. [Const. V; 021
  FR-071 como precedente; Arquitetura]
- **FR-006**: Uma carga de contatos, à parte da incorporação, DEVE gravar cada e-mail
  observado como contato de origem `FONTE_ACADEMICA`, com código da fonte, posição na ordem
  e momento.
  - A consulta à fonte DEVE ocorrer fora da transação de gravação.
  - Indisponibilidade NÃO DEVE gravar nada nem ser tratada como "sem contato".
  - Falha de uma Pessoa NÃO DEVE interromper as demais nem desfazer incorporações.
  - Ausência ou falha de contato NÃO DEVE impedir identificação, incorporação, resposta ou
    narrativa.

  [Arquitetura; Const. XXV]
- **FR-007**: O adaptador simulado de contatos DEVE fornecer apenas endereços fictícios no
  domínio `example.invalid`, determinísticos por referência estável, com ao menos uma
  Pessoa sem contato e ao menos uma com dois e-mails. O preparo da demonstração DEVE
  executar a carga depois da incorporação. O acervo histórico (019) NÃO DEVE fornecer
  contato. [016 FR-012; Const. XXV]

#### Política de escolha do contato

- **FR-008**: O contato utilizável de uma Pessoa num instante DEVE ser, nesta ordem:
  1. o contato `EGRESSO` mais recente;
  2. senão, o primeiro na ordem do adaptador entre os contatos `FONTE_ACADEMICA` da
     observação mais recente;
  3. senão, nenhum.

  Registro com endereço que não passa na validação sintática NÃO DEVE ser utilizável, e a
  política passa ao próximo candidato. NÃO DEVE haver aleatoriedade, score ou combinação.
  [Arquitetura; Solicitante]

#### Atualização voluntária pelo egresso

- **FR-009**: A tela de Participação concluída ancorada em Conclusão Acadêmica DEVE
  oferecer, para sessão de egresso com Pessoa (018), um convite opcional para informar
  e-mail.
  - O convite é ação secundária, depois e com menor destaque que "Ver minha trajetória no
    Ifes", que continua a ação principal (revisa a 021 FR-003 de "única ação" para "ação
    principal").
  - NÃO DEVE ser tela intermediária entre a conclusão e a Minha Trajetória.
  - NÃO DEVE aparecer na página da Minha Trajetória nem no card ou vídeo (021 FR-009; 022).
  - NÃO DEVE aparecer para sessão de declarante sem Pessoa (019), cuja tela de conclusão
    não muda.

  [Hipótese; E7; 018; 019; 021]
- **FR-010**: A página de e-mail DEVE estar fora do percurso do instrumento. NÃO DEVE
  depender de Versão ou Resposta, NÃO DEVE alterar Participação e NÃO DEVE ser condição de
  conclusão, acesso ou qualquer benefício — inclusive a Minha Trajetória (021 FR-009).
  "Agora não" DEVE ter o mesmo destaque de "Salvar". Depois de salvar ou recusar, a
  página DEVE oferecer a Minha Trajetória, quando disponível (021 FR-001), e a escolha de
  formações. [Const. XIV; Solicitante; 021]
- **FR-011**: A página DEVE identificar a Pessoa apenas pela sessão da 018, nunca por dado
  enviado pelo cliente, e DEVE exigir POST com CSRF para gravar. [018; Arquitetura]
- **FR-012**: A página DEVE explicar a finalidade (contato do Ifes sobre pesquisas de
  acompanhamento de egressos) e dizer que o e-mail não será público. O texto é provisório
  (DP-2003). NÃO DEVE prometer frequência, confirmação ou benefício. [Const. XVI, XXIX]
- **FR-013**: A página NÃO DEVE exibir contato guardado, de nenhuma origem. Depois de
  salvar, DEVE confirmar sem repetir o endereço. [E5; Const. XVI]
- **FR-014**: Endereço inválido DEVE ser recusado com mensagem compreensível, sem gravar.
  NÃO DEVE haver confirmação por link ou código nesta feature (DP-2004). [Const. XXII]

#### Lote de Mobilização

- **FR-015**: Um Lote DEVE pertencer a exatamente uma Campanha e registrar:
  - nome curto;
  - filtros;
  - escopo aplicado;
  - momento da confirmação;
  - operador que confirmou;
  - membros.

  NÃO DEVE copiar estado, período ou critérios da Campanha. [ADR 0004; Arquitetura]
- **FR-016**: Filtros DEVEM ser opcionais e limitados a: unidades, nível, ano mínimo e
  máximo de conclusão, e curso por igualdade textual. Situação de contato, modalidade,
  forma de oferta e estado de Participação NÃO DEVEM ser filtros. [Arquitetura; 010/DP-1005;
  016 FR-014]
- **FR-017**: A seleção DEVE seguir, nesta ordem:
  1. Conclusões na abrangência da Campanha (população da 004 no momento);
  2. restrição ao escopo do operador;
  3. filtros;
  4. Pessoas distintas pela identidade interna;
  5. exclusão das já mobilizadas na Campanha (FR-024);
  6. escolha do contato (FR-008).

  NÃO DEVE reimplementar elegibilidade nem deduplicar por nome ou e-mail. [004; 016 FR-009;
  Solicitante]
- **FR-018**: O membro DEVE ter grão Pessoa: uma Pessoa no máximo uma vez por Lote,
  independentemente do número de Conclusões. [Solicitante; 016]
- **FR-019**: A prévia DEVE ser transitória: recalculada a cada ajuste, sem gravar nada. Ela
  mostra Conclusões no recorte, Pessoas distintas, com contato, sem contato e excluídas por
  mobilização anterior. [E3; Arquitetura]
- **FR-020**: "Confirmar Lote" DEVE ser POST explícito com CSRF. A seleção DEVE ser
  recalculada no servidor naquele momento; NÃO DEVE aceitar lista, contagem ou contato
  enviados pelo cliente. DEVE gravar Lote e membros numa só operação. Lote com zero membros
  NÃO DEVE ser gravado. [016 FR-024; Arquitetura]
- **FR-021**: Cada membro DEVE gravar uma referência ao registro de contato escolhido, ou
  nenhum, e a situação inicial: `SEM_CONTATO` ou `NAO_TENTADO`. [Solicitante; E6]
- **FR-022**: Lote confirmado e seus membros NÃO DEVEM ter filtros, membros ou contato
  escolhido alterados nem ser apagados. Só a situação de envio dos membros evolui
  (FR-028). [Const. IV, VIII]
- **FR-023**: Confirmar Lote DEVE ser permitido com a Campanha EM PREPARAÇÃO ou EM COLETA e
  recusado ENCERRADA, verificando o estado no momento da ação. [Arquitetura]

#### Duplicidade

- **FR-024**: Na confirmação, uma Pessoa DEVE ser excluída se já for membro de outro Lote da
  mesma Campanha em situação diferente de `SEM_CONTATO`. Lotes de outras Campanhas NÃO DEVEM
  influir. O número de excluídas DEVE aparecer na prévia e no Lote. [Solicitante; E4]
- **FR-025**: DEVE ser estruturalmente impossível existir, para a mesma Pessoa e Campanha,
  mais de um membro em situação diferente de `SEM_CONTATO`. Isso vale mesmo sob
  confirmações ou envios concorrentes e não pode depender só da seleção. Uma tentativa de
  criar o segundo membro DEVE ser recusada sem gravação parcial.

  *(Revisto no analyze de 2026-10-05: a garantia passou a ser do banco (research R6), e a
  verificação "bloqueado" antes de cada envio ficou inalcançável e foi retirada.)*
  [Arquitetura]

#### Envio

- **FR-026**: "Enviar Lote" DEVE ser POST explícito com CSRF que revalida:
  - capacidade;
  - escopo;
  - estado da Campanha (somente EM COLETA);
  - modo e configuração de transporte;
  - origem da base.

  Só então processa membros `NAO_TENTADO`, com uma tentativa cada. [016 FR-023/024;
  Arquitetura]
- **FR-027**: A mensagem DEVE usar o contato congelado no membro, o renderer comum da prévia
  e do envio, versão texto e HTML equivalentes, um único destinatário, sem CC/BCC nem
  anexos, sem recursos externos nem rastreadores, e o link neutro configurado. NÃO DEVE
  conter CPF, identificador acadêmico, de Pessoa, de Lote ou de membro, nem token. [016
  FR-016…022; 018 FR-053]
- **FR-028**: A situação de cada membro DEVE ser gravada no momento:
  - `EM_TENTATIVA`, antes da submissão;
  - `SUBMETIDO_AO_TRANSPORTE`, se o transporte aceitar;
  - `FALHA_DE_TRANSPORTE`, se recusar ou falhar.

  Membro deixado `EM_TENTATIVA` por interrupção DEVE ser apresentado como resultado
  incerto e NUNCA ser tentado de novo automaticamente. [Solicitante; Arquitetura]
- **FR-029**: Acionar o envio de novo DEVE processar apenas membros `NAO_TENTADO` e ser
  seguro contra reenvio. A implementação PODE limitar quantos membros cada acionamento
  processa, com ação "continuar envio". NÃO DEVE haver fila, scheduler, worker em segundo
  plano nem retry automático. [Const. XXII]
- **FR-030**: NÃO DEVEM existir situações "entregue", "recebido", "aberto", "lido",
  "clicado" ou "bounce", nem pixel, tracking ou URL individual. [016 FR-026; Solicitante]
- **FR-031**: A situação do Lote — não enviado, envio parcial, envio concluído — DEVE ser
  derivada dos membros, sem campo próprio. [Const. XXII]

#### Transporte e modos

- **FR-032**: DEVE existir uma fronteira de transporte com três modos explícitos e
  exclusivos. Nenhum padrão implícito habilita envio.
  - **teste**: memória, só sob marcador de teste;
  - **demonstração**: as barreiras da 016 FR-030/031 (loopback, sem credenciais, remetente
    e destinatários `example.invalid`, URL local);
  - **real**.

  [016; Arquitetura]
- **FR-033**: O modo real DEVE ficar desativado por padrão e só ser ativável por
  configuração explícita de ambiente. Ativado, DEVE exigir antes de qualquer conexão:
  - transporte com TLS;
  - credenciais só por ambiente;
  - remetente institucional configurado;
  - URL neutra `https` configurada;
  - base sem dados simulados;
  - modo demonstração desligado.

  Faltando qualquer item, DEVE recusar sem transmitir. A ativação em produção depende do
  Gate B, inclusive da revisão registrada da proteção em repouso dos contatos (E2,
  DP-2010). [DP-1604; DP-2002; DP-2010; Const. XVI, XXIX]
- **FR-034**: O fornecedor NÃO DEVE ser codificado no domínio. A troca de SMTP por provedor
  DEVE ficar limitada à fronteira de transporte. [Const. V]
- **FR-035**: O modo demonstração DEVE manter o texto de demonstração da 016. O modo real
  DEVE usar um texto institucional provisório, não editável, identificado como pendente de
  aprovação (DP-2003). NÃO DEVE haver editor de mensagem. [008/DP-801; 016 FR-015]

#### Governança

- **FR-036**: DEVEM existir três capacidades nomeadas, reavaliadas a cada requisição:
  - consultar Lotes;
  - preparar e confirmar Lote;
  - enviar Lote.

  Na interpretação local reversível: CPAEG no âmbito institucional; CSAEG somente nas suas
  unidades ativas. Acompanhar coleta (011) e gerir Campanha (017) NÃO DEVEM concedê-las.
  [010; 016; DP-2001]
- **FR-037**: Lote preparado por CSAEG DEVE ter filtro de unidades não vazio e contido nas
  unidades da operadora. A CSAEG DEVE ver apenas Lotes cujas unidades estejam contidas nas
  suas. Lote sem filtro de unidade é institucional e visível só à CPAEG. [010/011]
- **FR-038**: Nenhuma interface DEVE listar membros individualmente, mostrar nomes ou
  endereços, ou permitir baixar destinatários. Apenas filtros, metadados e contagens.
  [Const. XVI; 016]

#### Privacidade e fronteiras

- **FR-039**: Contatos NÃO DEVEM aparecer em URLs, logs, mensagens de erro, indicadores da
  011, snapshots da 012, exportações da 013, telas públicas ou administrativas. Erros de
  transporte DEVEM ser apresentados só por categoria. [Const. XVI; Observabilidade]
- **FR-040**: Lote, membro, situação de envio e contato NÃO DEVEM entrar em admissão,
  entrada (007), Participação, snapshot (012) ou exportação (013). Snapshots existentes
  NÃO DEVEM ser alterados. [ADR 0004; 012; Const. VIII]
- **FR-041**: Nenhuma ação desta feature DEVE criar ou alterar Pessoa, Conclusão, Campanha,
  Versão, Participação, Resposta ou Formação Declarada. [Const. I, VII]
- **FR-042**: A tela do Lote DEVE nomear as contagens como operacionais e dizer que aceite
  do transporte não comprova entrega e que pertencer ao Lote não prova que a comunicação
  causou resposta. NÃO DEVE usar "alcance", "entregues" ou "conversão". [Solicitante;
  Const. XIX]

#### Substituição da 016 e interface

- **FR-043**: A tela "Comunicação simulada", sua ação e a capacidade de simular da 016
  DEVEM ser retiradas. O detalhe da Campanha passa a oferecer "Lotes de mobilização". O
  renderer e as barreiras da 016 DEVEM ser preservados no modo demonstração. [016;
  Arquitetura]
- **FR-044**: O formulário da Campanha (017) NÃO DEVE ganhar campo de Lote, foco, público,
  curso ou campus a mobilizar, nem contato. [017 FR-024; ADR 0004]
- **FR-045**: Telas novas DEVEM funcionar sem JavaScript, ser operáveis por teclado, com
  foco visível, rótulos, mensagens que não dependem só de cor, e funcionar de 320 px a
  desktop e com texto a 200%. A página do egresso usa o shell da jornada; as de Lote, o
  shell administrativo. [Const. XX, XXI; 015]
- **FR-046**: A demonstração DEVE permitir, inteiramente com dados fictícios e caixa local,
  exercitar:
  - importação de contatos;
  - atualização pelo egresso;
  - preparação, confirmação, duplicidade e envio de Lote;
  - retomada após interrupção.

  [Const. XXV]

### Matriz mínima de verificação automatizada

| Tema | Verificação |
| --- | --- |
| Contato | Imutabilidade; idempotência da carga; acréscimo por novo valor; política FR-008 em cada ramo |
| Isolamento | Contrato acadêmico e incorporação inalterados; 018, 001 e 019 não importam a capacidade de contatos; fonte de contatos indisponível não afeta acesso, incorporação, resposta nem narrativa |
| Conclusão e 021 | Ação principal "Ver minha trajetória no Ifes" preservada e primeira; convite secundário só com Pessoa; ausente na página da narrativa, no card, no vídeo e na conclusão declarada |
| Egresso | Oferta só com Pessoa; ausência para declarante; não exibe contato; POST/CSRF; Pessoa da sessão; Participação intacta |
| Seleção | Ordem FR-017; grão Pessoa; várias Conclusões; escopo CSAEG antes de filtro; sem contato permanece membro |
| Congelamento | Contato do envio = congelado; registro inalterado após novo contato; Lote imutável |
| Duplicidade | FR-024 para cada situação; outra Campanha não influi; FR-025 em concorrência |
| Envio | EM COLETA apenas; uma tentativa; retomada só de não tentados; `EM_TENTATIVA` vira incerto e não é retentado; falha sem retry |
| Modos | Teste só com marcador; demonstração com barreiras da 016; real desativado por padrão; cada exigência de FR-033 recusa isoladamente |
| Governança | Todas as rotas por perfil; CSAEG limitada; reavaliação por requisição |
| Fronteiras | Sem contato em 011/012/013, logs, erros e telas; snapshots preservados; link neutro sem identificadores |

### Key Entities *(include if feature involves data)*

- **Contato da Pessoa**: um endereço de e-mail ligado a uma Pessoa, com origem
  (`FONTE_ACADEMICA` — dado institucional; `EGRESSO` — dado declarado), código da fonte
  quando importado, posição na ordem do adaptador e momento de obtenção. É imutável, e
  vários podem coexistir.
- **Lote de Mobilização**: onda operacional de abordagem pertencente a uma Campanha. Guarda
  nome, filtros, escopo, operador e momento da confirmação. Imutável depois de confirmado.
  Não é população nem critério.
- **Membro do Lote**: uma Pessoa num Lote, com a referência ao contato escolhido (ou
  nenhum), a situação de envio e os instantes da tentativa.
- **Campanha, Pessoa, Conclusão Acadêmica**: existentes, inalteradas.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem | Fonte ou regra | Tratamento de divergência |
| --- | --- | --- | --- |
| E-mail importado | Institucional | Capacidade de contatos da fonte (adaptador), separada da fronteira acadêmica | Novo valor acrescenta registro; nenhum apagado |
| E-mail do egresso | Declarado | Página de atualização voluntária | Coexiste com o importado; a precedência de uso (FR-008) não apaga nenhum |
| Contato utilizável | Derivado | Política FR-008 no instante | Explicável pelos registros e momentos |
| Membros do Lote | Derivado e congelado | FR-017 no momento da confirmação | Nunca recalculado |
| Situação de envio | Operacional | Retorno do transporte | Sem inferência de entrega |
| Abrangência | Derivado (004) | População no momento | Lote não altera |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos cenários verificados, nenhuma Pessoa recebe mais de uma mensagem
  por Campanha, inclusive com Lotes sobrepostos, retomada e confirmação concorrente.
- **SC-002**: Para qualquer Lote enviado, é possível dizer, para cada membro, qual endereço
  foi usado, de que origem e obtido quando — mesmo depois de novos contatos.
- **SC-003**: Um egresso informa seu e-mail em no máximo uma página e uma ação depois de
  concluir. Recusar não exige nenhuma ação além de "Agora não".
- **SC-004**: Zero ocorrências de endereço de e-mail em logs, mensagens de erro, URLs,
  indicadores, snapshots, exportações e telas administrativas, verificadas por testes de
  fronteira.
- **SC-005**: Zero mensagens transmitidas fora de teste e demonstração enquanto o modo real
  não for ativado; cada exigência do modo real recusa isoladamente.
- **SC-006**: A operadora prepara, confirma e envia um Lote na demonstração em menos de 5
  minutos, entendendo pelas contagens quantos foram tentados, aceitos, falharam ou ficaram
  sem contato.
- **SC-007**: Uma Pessoa que nunca pertenceu a Lote continua iniciando e concluindo
  Participação na abrangência da Campanha em 100% dos cenários.
- **SC-008**: Snapshots da 012 gerados antes da 020 permanecem idênticos.

## Assumptions

- A demonstração continua a ser o único ambiente de uso. Nenhum dado pessoal real é criado.
- O número de membros num piloto controlado permite processar o envio em ações síncronas
  retomáveis. O plan define o limite por acionamento.
- O backend de e-mail do framework é fronteira de transporte suficiente até o Gate B.
- A sessão do egresso da 018 é a única identificação para informar e-mail.
- Contatos de Pessoas já incorporadas na demonstração são obtidos pelo preparo existente.

## Relação com outras features

Notas de revisão a aplicar com a implementação da 020:

- **001**: o contrato acadêmico e a incorporação não mudam. A vedação de incorporar e-mail
  ganha nota: e-mail admitido pela 020, por capacidade separada e com consumidor concreto
  (como a 018 fez com CPF e a 021 com ingresso).
- **004 / ADR 0004**: nota "Lote especificado na 020"; sem mudança de critério ou admissão.
- **010**: FR-028 (revisão de 2026-10-05) passa a listar as capacidades de Lote no lugar de
  `pode_simular_comunicacao`.
- **011 / 017**: o detalhe da Campanha troca "Comunicação simulada" por "Lotes de
  mobilização"; o formulário da Campanha não muda.
- **014 FR-041 / 021 FR-003**: a ação da conclusão ancorada em Conclusão passa de "única"
  a "principal", com o convite de e-mail secundário (E7). A 021 FR-004, FR-007, FR-009 e
  FR-070 permanecem. **A independência funcional de 021/022 não elimina este impacto
  compartilhado**: a tela de conclusão é definida por 014, 021 e 020, e uma mudança nela
  exige conferir as três.
- **016**: tela, ação e capacidade de simulação retiradas; renderer e barreiras preservados
  no modo demonstração; FR-033 revista; DP-1607 resolvida no limite do Lote.
- **018**: sessão reutilizada para informar e-mail; FR-053 preservado.
- **019**: nenhuma alteração.
- **022**: independente; o vídeo já veda e-mail e telefone.
- **Documentação institucional** (`docs/documentacao/index.html`): atualizada na
  consolidação desta spec para "especificada". Os estados "implementada" (restrita à
  demonstração) e "habilitada para uso real" (após os Gates A e B) são marcados quando
  ocorrerem.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I / VII**: Lote e envio não criam nem alteram Participação; Campanha, Versão e
  Participação seguem distintas (FR-041).
- **II / ADR 0004**: mobilização não define egresso nem elegibilidade; Lote ⊆ abrangência e
  não exclui ninguém (FR-017, FR-040, SC-007).
- **III / IV**: contato importado (institucional) e informado (declarado) são registros
  distintos, com origem e momento, sem sobrescrita (FR-001, FR-002, FR-008).
- **V**: contato chega por capacidade de fonte separada e substituível, sem tocar o
  contrato acadêmico; transporte por fronteira substituível (FR-005, FR-034).
- **VIII**: Lotes e membros congelados; snapshots intocados (FR-022, FR-040, SC-008).
- **X / Governança de Permissões**: capacidades explícitas, separando preparar de enviar,
  sem competência normativa inventada (FR-036, DP-2001).
- **XI / XII**: grão Pessoa, escopo pela Conclusão; CSAEG limitada às suas unidades
  (FR-018, FR-037).
- **XIV**: atualização opcional, em uma página, fora do instrumento (FR-010).
- **XV**: nenhum mecanismo novo de autenticação; e-mail não vira credencial.
- **XVI / Observabilidade**: só e-mail; finalidade declarada; nenhum contato em saídas
  (FR-004, FR-012, FR-039, FR-038).
- **XIX**: métricas operacionais, sem conversão (FR-042).
- **XX / XXI**: FR-045.
- **XXII**: sem rascunho, score, fila, retry, multicanal ou editor (E1–E6; Out of Scope).
- **XXIX**: envio real desativado até o Gate B; DPs explícitas.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence ao domínio de acompanhamento?** Em parte. Convidar egressos para uma Campanha
   é aplicação do questionário (PAEG Art. 22, IV). Comunicação massiva genérica não é, e a
   020 se limita a convites de Campanha.
2. **É necessária ao ciclo?** Sim: sem mobilização não há resposta representativa, e o
   histórico de quem foi abordado é necessário para interpretar a coleta.
3. **Existe solução institucional mais adequada?** Pode existir (004/DP-407). A fronteira
   de transporte permite usar serviço institucional sem mudar o domínio.
4. **Integração seria suficiente?** Para o transporte, sim (FR-034). A seleção, o
   congelamento e o histórico dependem de Campanha e população e pertencem ao NIAE.
5. **Aumenta o acoplamento?** Não: contato é registro lateral à Pessoa, e Lote é lateral à
   Campanha. Nada entra em admissão, Participação ou dados analíticos.

## Gates

### Gate A — profiling futuro da fonte real de contatos (não executado)

Roteiro na [auditoria §18](../../docs/auditorias/2026-10-04-mobilizacao-real-lotes-contatos.md#18-gate-a--profiling-futuro-da-fonte-real-de-contatos):

- existência de campos;
- relação com identificadores;
- cobertura por coorte, unidade e nível;
- sintaxe;
- multiplicidade e compartilhamento;
- institucional × pessoal;
- atualidade;
- telefone;
- variação histórica.

Somente agregados, em ambiente autorizado. Os resultados são **desconhecidos** nesta spec e
só refinam o adaptador real e a ordem de preferência, sem mudar a arquitetura.

### Gate B — antes da ativação do modo real

O modo real (FR-033) permanece desativado até estarem registrados:

- base legal e finalidade (DP-1603);
- textos de transparência (DP-2003);
- remetente institucional (DP-2002);
- provedor, SMTP e credenciais (DP-1604);
- retenção (DP-2006);
- governança de envio (DP-2001, DP-1602, 004/DP-407);
- opt-out e preferência (DP-1606);
- suporte (DP-2007);
- observabilidade (DP-2008);
- fonte real de contatos e adaptador (DP-1601);
- identificação produtiva de operadores (010/DP-1001);
- revisão registrada da proteção em repouso dos contatos (E2, DP-2010).

## Out of Scope *(mandatory)*

- WhatsApp, SMS, push, telefone, LinkedIn, Lattes, perfil, Portal, diretório e networking.
- Confirmação de e-mail por link ou código; exibição, edição ou remoção do contato pelo
  egresso.
- Opt-out, preferência de comunicação e oposição (DP-1606).
- Lembretes, reenvio deliberado, segmentação por estado de Participação (DP-1605,
  DP-2005).
- Scheduler, automação recorrente, fila, worker, retry automático.
- Webhooks, bounce, entrega, abertura, clique, pixel, URL individual, atribuição de resposta.
- Editor de mensagem, personalização além do nome e da Campanha, A/B.
- Rascunho de Lote persistido, edição ou exclusão de Lote confirmado.
- Lista ou exportação de destinatários; indicador de "convidados" no painel da 011.
- Profiling da fonte real e adaptador real (Gate A, DP-1601).
- Ativação do envio real (Gate B).
- Qualquer alteração da 019.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

### Novas

- **DP-2001** — DECISÃO PENDENTE: quem prepara e quem envia Lotes em produção, institucional
  e por unidade (refina DP-1602). Instância: CPAEG/Proex com DIREC e CSAEGs, a confirmar.
  Impacto: FR-036. Tratamento provisório: CPAEG e CSAEG no escopo, só em demonstração.
- **DP-2002** — DECISÃO PENDENTE: remetente institucional (endereço, nome, domínio,
  autenticação do domínio). Instância: DTI e comunicação institucional. Impacto: FR-033.
  Tratamento provisório: remetente fictício na demonstração; bloqueia o modo real.
- **DP-2003** — DECISÃO PENDENTE: texto do convite real e da página de atualização de
  e-mail, incluindo transparência. Instância: Proex, comunicação e encarregado. Impacto:
  FR-012, FR-035. Tratamento provisório: texto provisório identificado; bloqueia o modo
  real.
- **DP-2004** — DECISÃO PENDENTE: necessidade de confirmar o e-mail informado. Instância:
  CPAEG e encarregado. Impacto: FR-014. Tratamento provisório: sem confirmação; risco de
  convite neutro desviado aceito na demonstração.
- **DP-2005** — DECISÃO PENDENTE: reenvio deliberado (falha, incerto, nova onda) e quem o
  autoriza. Instância: a de DP-2001. Impacto: FR-024, FR-028. Tratamento provisório:
  nenhum reenvio na mesma Campanha.
- **DP-2006** — DECISÃO PENDENTE: retenção e expurgo de contatos, Lotes e registros de
  envio. Instância: encarregado e CPAEG. Impacto: FR-002, FR-022. Tratamento provisório:
  nada é apagado; bloqueia o modo real.
- **DP-2007** — DECISÃO PENDENTE: suporte ao egresso e caixa de resposta. Instância: DIREC
  e CSAEGs. Impacto: Gate B. Tratamento provisório: nenhum.
- **DP-2008** — DECISÃO PENDENTE: observabilidade do envio real sem dado pessoal.
  Instância: DTI. Impacto: Gate B. Tratamento provisório: logs só por categoria.
- **DP-2009** — DECISÃO PENDENTE: telefone ou WhatsApp como canal, com finalidade (refina
  DP-1608). Instância: a de 004/DP-407, com encarregado. Impacto: FR-004. Tratamento
  provisório: não coletado.
- **DP-2010** — DECISÃO PENDENTE: proteção em repouso dos contatos para uso real
  (manter legível com controles de infraestrutura ou adotar criptografia de aplicação).
  Instância: DTI e encarregado. Impacto: FR-001, FR-033. Tratamento provisório: legível,
  somente na demonstração (E2); bloqueia o modo real até revisão registrada.

### Herdadas, preservadas

| ID | Efeito na 020 |
| --- | --- |
| **016/DP-1601** | Fonte real de contatos e qualidade. A 020 define o contrato; o adaptador real depende do Gate A. Bloqueia contato real. |
| **016/DP-1602**, **004/DP-407** | Governança e canais. Refinada por DP-2001. |
| **016/DP-1603**, **001/DP-009**, **005/DP-504** | Base legal. Bloqueia o modo real. |
| **016/DP-1604** | Provedor e credenciais. Bloqueia o modo real. |
| **016/DP-1605** | Lembretes. Fora de escopo. |
| **016/DP-1606** | Opt-out. Fora de escopo; bloqueia o modo real. |
| **016/DP-1607** | Histórico de disparos: **resolvida no limite do Lote** (membros e situações); granularidade adicional e retenção seguem em DP-2006. |
| **016/DP-1608** | Outros canais. Refinada por DP-2009. |
| **004/DP-406**, **018/DP-1801…1803** | Acesso real do egresso; a página de e-mail herda os mesmos limites. |
| **004/DP-408** | Fotografia da população. O Lote congela membros, não população. |
| **010/DP-1001**, **010/DP-1005** | Operadores reais; vocabulário de unidade e curso (filtros por igualdade textual). |
| **017/DP-1701** | Autoria de gestão de Campanha. A 020 registra o operador do Lote por necessidade própria, sem resolver DP-1701. |
| **019/DP-1908** | Notificação do declarante. A 020 não a resolve. |
| **008/DP-801** | Linguagem institucional. |
