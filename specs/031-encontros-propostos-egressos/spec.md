# Feature Specification: Encontros propostos por egressos

**Feature Branch**: `claude/feature-031-encontros-egressos-96e37e` (só documentos)
**Created**: 2026-10-11
**Status**: **Hipótese.** Spec e [protótipo estático](prototipo/index.html) antecipados antes dos
checkpoints, por autorização do solicitante
([roadmap, revisão 14](../../docs/roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md)).
**Não há plan, tasks, código nem migração.** A implementação depende da leitura do Checkpoint 1
e do Checkpoint 2, em especial do bloco Comunidade. Os dois estão **NÃO APLICADOS**. A escolha
entre 031 e 030 continua com o solicitante depois deles (roadmap, §13.5). Se autorizada, a
implementação vale só para a demonstração.
**Revisão de produto (2026-10-11, solicitante)**: Denúncia mínima aceita, sem sistema de
atendimento; público como contexto de descoberta; nome e origem do organizador registrados na
[ADR 0010](../../docs/adr/0010-dado-de-egresso-visivel-a-outros-egressos.md); edição depois da
publicação separada entre correção operacional e mudança substancial com nova análise; Q8
decidida como observações exploratórias, sem limiar.
**Input**: Solicitante, 2026-10-11. Um egresso propõe um encontro virtual para outros egressos.
O Ifes modera antes de publicar. Outros egressos descobrem o encontro, confirmam e recebem o
link. É a alternativa **F** da
[visão da Comunidade](../../docs/roadmap/2026-10-09-comunidade-alternativas.md#direção-registrada-por-capacidade):
a primeira capacidade do Portal em que um egresso produz valor para outros egressos.

## Contexto e dependências

| Fato verificado | Fonte | Consequência para a 031 |
|---|---|---|
| A direção de F (MVP, público, moderação, identidade, privacidade, dado operacional, fora do MVP) é insumo, não requisito aprovado | Alternativas, revisão de 2026-10-11; roadmap §13.5 | Esta spec confirma, revê ou registra como pendente cada ponto |
| O que a demonstração mostra hoje como encontro é a alternativa **A**: uma Oportunidade da categoria "Eventos", divulgada pela unidade, com link oficial. No Início, ela aparece em "Ninguém se forma sozinho." | 025 FR-003; 032 FR-008; `portal/mensagens.py` (`ENCONTROS_TEXTO`) | A continua como está. F é capacidade distinta, com rótulo próprio |
| A Oportunidade não tem data de evento, local nem autor egresso, por regra | 025 FR-001 | F não reaproveita a Oportunidade (ver "Fatos novos") |
| A pertinência da 025 usa só unidades, níveis e cursos das Conclusões, por igualdade exata, com uma mesma Conclusão satisfazendo todos os critérios. Não existe área do conhecimento no domínio | 025 FR-007, FR-012; DP-2507 | Mesma regra para F, sem tema nem área como critério |
| Escopos de governança: CSAEG nas unidades do vínculo, CPAEG institucional; competências nomeadas; operadores fictícios | 010; 025 FR-025; DP-1001 | Base da hipótese de moderação |
| A PAEG fundamenta eventos entre egressos (Art. 12; Art. 8, II) e o apoio da CSAEG a eventos (Art. 22, VII), mas não atribui a ninguém a moderação de encontros propostos por egressos | Alternativas, "Fundamentação conferida" | Quem modera é **D8**. Na demonstração, hipótese H-3102 |
| A identificação do egresso é por conhecimento (CPF e data de nascimento), sem garantia forte | 018; DP-1808 | Identidade, vínculo e moderação são controles distintos (FR-030) |
| O e-mail da Pessoa tem finalidade de pesquisa; o da contribuição, de resposta sobre a contribuição | 020 FR-012; 026 D-2602 | A 031 não lê, não pede e não guarda e-mail (FR-034) |
| A camada do Portal tem dois fatos (Oportunidade e Manifestação); o núcleo não a importa; os fatos da camada ficam fora do dado analítico | ADR 0008; `tests/portal/test_fronteiras.py`; 026 FR-015, FR-016 | Encontro, Confirmação e Denúncia vivem na camada |
| Toda tela do egresso sem sessão leva à entrada, com destino fixo: nenhum valor do cliente decide para onde a pessoa vai | `portal/destinos.py`; 024 FR-006 | O endereço compartilhado precisa de um destino preservado por lista fechada (FR-022) |
| "Comunidade" é vedada nas telas servidas e entra com F ou E1, por revisão explícita | ADR 0009, decisão 7; 024 FR-021; 029 FR-007; 032 SC-005; revisão 12 | Revisões de vocabulário listadas, para a implementação |
| Sem JavaScript nas telas do egresso | 015; 024 FR-025; 032 SC-003 | Compartilhar mostra o endereço; o `.ics` é um download |
| Os PRs #62 (revisão 13, kits dos checkpoints) e #63 (roteiro com teclado da versão C) estão **integrados** na `main` (`f5c4035`). Não havia PR aberto sobre o tema. O teste com leitor de tela não foi executado | `git log`; roadmap §13.2 | Esta spec parte do que está integrado. Nada dela depende de proposta aberta |
| Os achados de acessibilidade A-01 a A-04 da versão C não foram corrigidos | 032, validação | Fora desta tarefa. O protótipo não os corrige nem os reproduz como regra |

## O percurso completo

```text
 ORGANIZADOR (egresso)          MODERAÇÃO (CSAEG ou CPAEG)       PARTICIPANTE (outro egresso)
 ──────────────────────────     ──────────────────────────       ──────────────────────────
 1. Propõe: título, descrição,
    data, início e término,
    público, link da reunião,
    nome de apresentação e
    formação de origem
 2. Lê quem vai analisar e o
    termo do organizador;
    envia → "Em análise"
                                3. Analisa no seu escopo e
                                   publica, ou recusa com motivo
 4. Vê a decisão. Se publicado,
    copia o endereço e
    compartilha
                                                                 5. Descobre o encontro (Início
                                                                    ou Encontros) pela formação,
                                                                    ou pelo endereço recebido
                                                                 6. Lê quem propõe, quem moderou
                                                                    e quem fica sabendo; marca
                                                                    "Vou participar"
                                                                 7. Vê o link da reunião e baixa
                                                                    o .ics, que aponta para a
                                                                    página; pode cancelar
 8. Vê quantas pessoas
    confirmaram (só o número);
    pode mudar data e horário
    ou cancelar
                                9. Recebe denúncias; retira com
                                   motivo, se for o caso
 10. O encontro acontece fora do Portal, na plataforma do link. Depois do término, a página
     diz "Encontro encerrado" e o link some.
```

**O que o sistema não faz:** não cria sala, não envia convite, lembrete nem notificação, não
mostra quem confirmou, não registra presença, não abre conversa entre pessoas e não
transforma o encontro em grupo permanente.

## User Scenarios & Testing

As histórias usam as personas fictícias da demonstração. O
[protótipo](prototipo/index.html) mostra cada uma.

### US1 — Propor um encontro (P1)

Maria concluiu Tecnologia em Análise e Desenvolvimento de Sistemas (Serra, 2022) e a
Especialização em Informática na Educação (Cefor, 2025). Ela propõe "Tecnologia na sala de
aula: o que funciona de verdade", para egressos da Especialização e da Licenciatura em
Química (Vila Velha), curso que ela não fez.

**Independent Test**: com a persona Maria, enviar uma proposta e conferir o Encontro em análise,
com a versão do termo, o momento e a moderação responsável (CPAEG, porque o público abrange
mais de uma unidade).

1. **Dado** uma Pessoa com sessão e ao menos uma Conclusão, **quando** abre "Propor um
   encontro", **então** vê o formulário com público, origem e nome de apresentação.
2. **Dado** um campo inválido, **quando** envia, **então** vê o resumo de erros e cada erro
   junto do campo, com o que digitou preservado, e nada é gravado.
3. **Dado** uma proposta válida, **quando** chega a "Confira e envie", **então** vê como a
   página vai aparecer, quem vai analisar e o termo do organizador, com a versão.
4. **Dado** que enviou, **então** o encontro fica "Em análise" em "Seus encontros", sem
   aparecer a ninguém, e a tela diz que não há prazo garantido de análise.

### US2 — Moderar antes da publicação (P1)

**Independent Test**: com operadores fictícios CSAEG Serra, CSAEG Vila Velha e CPAEG, conferir
que cada um vê só os encontros que lhe cabem e que publicar, recusar e retirar registram
momento, operador e motivo.

1. **Dado** um encontro em análise no escopo do operador, **quando** abre a análise, **então**
   vê a prévia, o público em linguagem simples, o domínio do link com aviso de site externo e
   a origem do organizador. Não vê CPF, data de nascimento, contato nem quem confirmou.
2. **Dado** a análise, **quando** confirma "Publicar", **então** o encontro passa a aparecer a
   quem tem formação no público.
3. **Dado** a análise, **quando** recusa com um motivo da lista, **então** o organizador vê
   "Recusado", com o motivo e o complemento. A recusa é definitiva.
4. **Dado** um encontro publicado, com ou sem denúncias, **quando** o operador o retira com
   motivo, **então** ele some das listas, a página diz "Retirado pela moderação" e o link
   some.
5. **Dado** um operador fora do escopo, **quando** tenta abrir a análise, **então** recebe a
   recusa do padrão de governança.

### US3 — Descobrir e confirmar (P1)

Diego concluiu a Licenciatura em Química (Vila Velha, 2017). No Início, vê o encontro de Maria
ao lado de um evento da unidade Vila Velha, cada um com seu rótulo.

**Independent Test**: com Diego, confirmar, ver o link, baixar o `.ics`, cancelar e conferir
que o link sumiu e que o organizador vê o número diminuir.

1. **Dado** um encontro publicado cujo público inclui uma formação de Diego, **então** ele o
   vê com "Proposto por egresso" e a explicação "Aparece porque você concluiu Licenciatura em
   Química (Vila Velha, 2017)".
2. **Dado** a página do encontro, **quando** Diego lê a área "Vou participar", **então** fica
   sabendo, antes de confirmar, que o organizador vê só a quantidade, que ninguém vê o nome
   dele, que o link aparece depois de confirmar e que não há notificação.
3. **Dado** que confirmou, **então** vê o link da reunião, com o domínio e a origem do site, e
   "Adicionar ao calendário (.ics)", com o aviso de que mudanças não atualizam o arquivo já
   baixado.
4. **Dado** uma confirmação ativa antes do início, **quando** cancela e confirma o
   cancelamento, **então** o link some e a página volta a oferecer "Vou participar".

### US4 — Acompanhar e cancelar como organizador (P2)

1. **Dado** um encontro publicado, **quando** Maria abre "Seus encontros", **então** vê a
   situação e "N pessoas confirmaram", sem nomes.
2. **Dado** um encontro publicado antes do início, **quando** Maria muda a data ou o horário,
   **então** a página passa a mostrar "Data alterada em …", as confirmações continuam e a tela
   avisa que ninguém é notificado e que calendários já baixados não mudam.
3. **Dado** um encontro publicado cujo link não funciona, **quando** Maria informa uma nova sala
   na mesma plataforma, **então** o novo link vale na hora, com "Link atualizado em …". Se o
   novo link for de outra plataforma, a mudança passa por nova análise (FR-008).
4. **Dado** um encontro publicado, **quando** Maria muda o título, a descrição ou o público,
   **então** lê antes que o encontro sai das listas e o link deixa de aparecer até a nova
   análise, e que as confirmações continuam.
5. **Dado** um encontro em análise ou publicado, **quando** Maria cancela e confirma, **então**
   a página diz "Cancelado pelo organizador", o link some e o encontro sai das listas.

### US5 — Compartilhar e denunciar (P2)

1. **Dado** um encontro publicado, **quando** alguém abre o endereço sem sessão, **então** vê
   só que há um encontro no Portal do Egresso e a ação "Confirme seus dados para ver". Depois
   da identificação, volta à página do encontro.
2. **Dado** um egresso identificado fora do público, **quando** abre o endereço, **então** vê o
   encontro, com "Você recebeu este endereço: o encontro foi proposto para …", e pode
   confirmar.
3. **Dado** a página de um encontro publicado, **quando** um egresso escolhe "Denunciar este
   encontro", **então** escolhe um motivo, escreve um complemento opcional, envia e vê que a
   moderação foi avisada, sem prazo prometido.

### US6 — Estados vazios e encerrados (P2)

1. **Dado** nenhum encontro pertinente, **então** a página Encontros diz isso numa frase
   verdadeira e oferece "Propor um encontro". No Início, a seção não existe.
2. **Dado** um organizador sem encontros, **então** "Seus encontros" diz isso e oferece propor.
3. **Dado** a fila da moderação vazia, **então** a lista diz que não há encontros para análise.
4. **Dado** um encontro depois do término, **então** a página diz "Encontro encerrado", sem
   link, sem confirmação e sem cancelamento, e ele sai das listas.
5. **Dado** um encontro em análise cujo início chegou, **então** ele fica "Não analisado a
   tempo" e nunca é publicado.

### Edge Cases

- **Organizador com várias formações:** escolhe uma como origem. A origem não limita o público.
- **Público que não inclui a formação do organizador:** admitido (encontro temático).
- **Público sem ninguém:** admitido. Nem o organizador nem a moderação veem quantos egressos
  casam com o público (como na 025, FR-026).
- **Endereço repassado a quem está fora do público:** a página abre para qualquer egresso
  identificado com Conclusão (US5.2). O público é **contexto de descoberta**, e não
  exclusividade nem controle de acesso (FR-004). O formulário e a página dizem isso, e o
  Checkpoint 2 observa se a diferença é entendida (CM-F5).
- **Link da reunião repassado por quem confirmou:** o sistema não impede. O termo do
  organizador diz isso.
- **Confirmar duas vezes:** só uma confirmação ativa por pessoa e encontro. Depois de cancelar,
  confirmar de novo cria outra confirmação; a cancelada não é reativada.
- **Decisão concorrente:** se a situação mudou entre a exibição e a ação (retirado enquanto
  alguém confirmava; publicado enquanto o organizador editava), a ação é recusada com página
  de conflito e nada é gravado (padrão da 017 e da 025, FR-034).
- **Pessoa sem Conclusão, ou só com Formação Declarada:** não vê Encontros nem propõe. Ao
  abrir um endereço, lê que os encontros são para egressos com formação concluída registrada
  no Ifes.
- **Portal desligado:** todas as rotas respondem "não encontrado"; os dados ficam preservados;
  a coleta não muda.

## Fatos novos e por que existem

Cada atributo responde a um fluxo, como na 025. Nada genérico: não há Comunidade, Grupo,
Interação, Evento nem Perfil.

**Encontro.** A proposta precisa existir entre o envio, a decisão da moderação e a descoberta
por outras pessoas. Ela tem um autor egresso, uma data e um ciclo próprio.

- **Por que não é Oportunidade (025):** a Oportunidade é conteúdo institucional que aponta para
  a página oficial de quem oferece, e a regra veda data de evento e autor egresso (FR-001).
  Encaixar F nela misturaria "Evento do Ifes" e "Encontro proposto por egresso", que o
  Checkpoint 2 precisa distinguir (CM-C1).
- **Por que não é Manifestação (026):** a Manifestação é uma mensagem privada à unidade, nunca
  publicada.

| Atributo | Fluxo que exige |
|---|---|
| Organizador (Pessoa) e Conclusão de origem | Autoria, "Seus encontros", origem mostrada como registro do Ifes |
| Nome de apresentação | Quem confirma precisa saber quem propõe. Escolhido pelo organizador; o nome do registro não é usado (DP-2103) |
| Título e descrição curta | Descobrir e decidir. Texto simples |
| Data, início e término | Página, `.ics`, encerramento automático |
| Público: unidades, níveis e cursos, opcional | Descoberta e explicação (FR-011 a FR-013) e responsabilidade de moderação (FR-016) |
| Link da reunião | Acesso de quem confirmou |
| Versão do termo do organizador e momento do envio | XVII |
| Publicação (a primeira e a última), recusa e retirada: momento, operador opaco e, nas duas últimas, motivo e complemento | Moderação e prestação de contas ao organizador |
| Cancelamento: momento | Página e listas |
| Data alterada em; link atualizado em | Avisos na página e sequência do `.ics` (FR-008) |
| Reenvio para nova análise: momento e nomes dos campos alterados | Mudança substancial depois da publicação (FR-008); a moderação sabe o que conferir |

**Fica fora do Encontro:** local, vagas, imagem, tema ou área, etiquetas, recorrência,
co-organizadores, contato, contagem gravada e histórico de edições.

**Confirmação.** Sem ela, não há como mostrar o link só a quem confirmou, permitir cancelar nem
dizer ao organizador quantas pessoas vão.

| Atributo | Fluxo que exige |
|---|---|
| Encontro e Pessoa | Mostrar o link e o estado só à própria pessoa; uma ativa por pessoa |
| Versão da ciência apresentada e momento | XVII |
| Cancelada em | Cancelamento; a contagem só conta as ativas |

**Fica fora da Confirmação:** presença, comentário, avaliação, nome exibido e contato.

**Denúncia** (registro mínimo, aceito na revisão de produto). O percurso de moderação precisa
que a denúncia chegue à moderação responsável, e não há canal institucional integrado à
demonstração. A Denúncia **não** é sistema de atendimento: não tem situação, atribuição,
resposta, prazo nem histórico. A moderação lê as denúncias ao analisar o encontro e decide
retirá-lo ou não (FR-017).

| Dado | Para quê | Quem consulta |
|---|---|---|
| Encontro | Levar a denúncia à moderação responsável (FR-016) | Moderação |
| Motivo, da lista fechada | Dizer o problema sem texto obrigatório | Moderação |
| Complemento opcional, até 300 caracteres | Detalhar quando preciso; a tela orienta a não incluir dados pessoais | Moderação |
| Momento | Ordenar e situar a denúncia | Moderação |
| Pessoa que denunciou | Só impedir duas denúncias da mesma pessoa sobre o mesmo encontro e mostrar a ela "Você denunciou este encontro em …" | **Ninguém** na interface: nem a moderação, nem o organizador |

O organizador não vê denúncias, nem a quantidade delas. Se o encontro for retirado, ele vê o
motivo da retirada (FR-017).

**Alternativa de canal externo** (para uso real, se D8 a escolher, por exemplo a ouvidoria):
"Denunciar este encontro" passa a mostrar o canal institucional e o endereço da página, para a
pessoa citar; o Portal não grava nada; a moderação recebe pelo canal e retira pela própria
tela. A Denúncia sai do modelo sem afetar Encontro e Confirmação.

## Requirements

### Functional Requirements

**Proposta**

- **FR-001 [Arquitetura]**: Só a Pessoa identificada com ao menos uma Conclusão Acadêmica pode
  propor. A Formação Declarada (019) não basta, como na 026 (D-2603).
- **FR-002 [Hipótese, H-3101]**: Campos e limites:
  - título, até 90 caracteres;
  - descrição, até 400;
  - nome de apresentação, até 40;
  - data entre 2 e 90 dias depois do envio, com início e término no mesmo dia e até 3 horas de
    duração;
  - público;
  - link da reunião;
  - Conclusão de origem.

  Tudo texto simples, exibido como texto.
- **FR-003 [Arquitetura]**: O link da reunião passa pela validação mínima da 025: absoluto em
  `https://`, sem usuário nem senha, sem IP como destino, sem espaços e com até 500
  caracteres. O domínio é classificado só para exibição (site do Ifes ou site externo). O
  sistema não busca nem verifica o conteúdo do endereço e não acrescenta parâmetros.
- **FR-004 [Arquitetura]**: O público segue a forma da 025 (FR-007): até três critérios
  opcionais (unidades, níveis e cursos), com valores escolhidos entre os já registrados nas
  Conclusões, exatamente como escritos. Sem critério, o encontro é aberto a todos os egressos.
  Tema e área não são critérios: ficam no título e na descrição. O público é **contexto de
  descoberta**: decide em que listas o encontro aparece e com qual explicação. Não é
  exclusividade nem controle de acesso: quem recebe o endereço e está identificado, com
  Conclusão, pode confirmar. O formulário diz "Para quem o encontro aparece", e a página diz
  "Proposto para … Quem receber o endereço também pode participar" [Hipótese, H-3108].
- **FR-005 [Arquitetura]**: O público **não** é derivado nem limitado pela formação do
  organizador. A Conclusão de origem só identifica de onde ele vem.
- **FR-006 [Arquitetura]**: Antes de enviar, a tela mostra a prévia, o público em linguagem
  simples, quem vai analisar (FR-016) e o **termo do organizador** versionado. O termo diz:
  - que o organizador conduz o encontro e que o Ifes revisa, mas não organiza;
  - o que aparece na página e para quem (FR-024);
  - que só a quantidade de confirmações chega ao organizador;
  - que o link pode ser repassado por quem confirmou;
  - que a análise não tem prazo garantido, que a recusa e a retirada têm motivo e que não há
    notificação.

  A versão apresentada e o momento ficam no Encontro (XVII). O termo **não** define a base
  legal (D9).
- **FR-007 [Arquitetura]**: Erros aparecem num resumo no topo e junto de cada campo, com
  vocabulário fechado. O que a pessoa digitou volta ao campo e o foco vai ao resumo. Nada é
  gravado.

**Edição, cancelamento e encerramento**

- **FR-008 [Hipótese, H-3103]**: Em análise, o organizador pode editar tudo; a moderação vê
  sempre a versão atual. Depois da publicação, até o início, há dois tipos de mudança:
  - **Correção operacional, sem nova análise**, com aviso na página a todos:
    - data, início e término, dentro dos limites do FR-002 ("Data alterada em …");
    - link da reunião **no mesmo domínio** do link analisado, por exemplo uma nova sala na
      mesma plataforma ("Link atualizado em …"). A moderação avaliou a plataforma, e uma sala
      nova nela não muda o que foi avaliado.
  - **Mudança substancial, com nova análise**: título, descrição, público, nome de
    apresentação, origem ou link para **outro domínio**.
    - Antes de enviar, o organizador lê o efeito: até a nova decisão, o encontro sai das
      listas, a página diz "Em revisão depois de uma alteração", o link não aparece, e as
      confirmações continuam.
    - Publicado de novo, volta às listas com "Alterado em …".
    - Se a moderação recusar a alteração, o encontro fica Retirado, com o motivo. Não há
      versão anterior guardada para restaurar.

  As confirmações sempre continuam. Ninguém é notificado: os avisos aparecem só na página.
- **FR-009 [Arquitetura]**: O organizador pode cancelar em análise ou publicado, até o início,
  com confirmação explícita. O cancelamento é definitivo e não tem texto livre.
- **FR-010 [Arquitetura]**: As situações são derivadas dos momentos e das datas, sem coluna de
  estado. Nenhum processo agendado é necessário.

  | Situação | Condição |
  |---|---|
  | Em análise | enviado, sem decisão nem cancelamento, antes do início |
  | Não analisado a tempo | enviado, sem decisão, início já passou |
  | Publicado | publicado, sem retirada nem cancelamento, sem reenvio pendente, antes do término |
  | Em revisão depois de uma alteração | publicado, reenviado depois da última publicação, sem nova decisão, antes do início |
  | Alteração não analisada a tempo | publicado, reenviado, sem nova decisão, início já passou. Não acontece pelo Portal |
  | Encerrado | publicado, sem retirada nem cancelamento, depois do término |
  | Recusado | recusado |
  | Retirado | retirado depois de publicado, inclusive por recusa de alteração |
  | Cancelado | cancelado pelo organizador |

  Recusado, Retirado e Cancelado são definitivos. "Propor de novo com estes dados" cria outro
  Encontro, com o formulário preenchido.

**Descoberta e pertinência**

- **FR-011 [Arquitetura]**: Um encontro aparece nas listas de uma Pessoa se estiver Publicado e
  não tiver público, ou se ao menos **uma mesma** Conclusão dela satisfizer todos os critérios
  definidos, por igualdade exata. É a regra da 025, FR-012, sem combinar critérios entre
  formações. Resposta, Formação Declarada, contato, nome e comportamento não entram.
- **FR-012 [Arquitetura]**: Cada item traz a explicação gerada pela regra, como na 025, FR-013:
  "Aparece porque você concluiu …" ou "Aberto a todos os egressos do Ifes".
- **FR-013 [Hipótese, H-3105]**: Onde aparece:
  - **página Encontros**, em dois grupos com rótulo próprio: "Propostos por egressos", pela
    data do encontro, e "Eventos do Ifes", os itens da categoria "Eventos" (A) na ordem da 025.
    Os itens A vêm da 025 sem mudança. Como a Oportunidade não tem data de evento (025
    FR-001), os dois grupos não se misturam numa agenda;
  - **Início**: na seção de encontros (032 FR-008), o próximo encontro proposto por egresso e o
    próximo evento do Ifes, quando houver. Sem nenhum, a seção não existe.

  A ordem é determinística, sem ranking nem recomendação, e consultar não grava nada.
- **FR-014 [Arquitetura]**: A distinção é visível e textual, nunca só por cor:
  - "Encontro proposto por egresso", com "Proposto por {nome}" e a origem;
  - "Evento do Ifes", com "Divulgado pela unidade {unidade}".

  A página de F diz que o Ifes revisou a proposta, mas não organiza o encontro.

**Moderação**

- **FR-015 [Arquitetura]**: Nenhum encontro aparece a outras pessoas sem publicação explícita de
  quem tem a competência nomeada **moderar encontros**. Publicar é o ato de autorização, com
  confirmação, momento e operador opaco. Não há segunda aprovação.
- **FR-016 [Hipótese, H-3102; D8]**: **Hipótese da demonstração, e não competência
  institucional aprovada**: a PAEG não atribui a moderação desses encontros a ninguém. A
  responsabilidade sai do público:
  - **CSAEG da unidade**, quando o critério de unidades tem exatamente uma unidade;
  - **CPAEG**, em todos os outros casos: várias unidades, nenhum critério de unidade (só
    cursos ou níveis) ou aberto a todos.

  A CPAEG também vê os de unidade única, como na 025 (DP-2501). Nenhum outro papel nem perfil
  técnico recebe a competência. Quem modera aparece ao organizador antes do envio.
- **FR-017 [Hipótese, H-3104; D8]**: Recusa e retirada exigem um motivo de lista fechada e um
  complemento opcional, obrigatório em "Outro motivo". O organizador vê os dois. A página
  retirada diz só "Retirado pela moderação". Motivos provisórios:
  - fora da finalidade dos encontros entre egressos;
  - divulgação comercial ou venda;
  - link da reunião inadequado;
  - informação incompleta ou que pode ser confundida com evento oficial do Ifes;
  - desrespeito a pessoas ou à lei;
  - outro motivo.
- **FR-018 [Arquitetura]**: A análise mostra a prévia, o público, a data, o link completo e o
  domínio, com aviso de site externo, a origem e o nome de apresentação. **Não** mostra CPF,
  data de nascimento, contato, quem confirmou nem quem denunciou. Mostra a quantidade de
  confirmações e as denúncias (motivo, complemento e data). Na nova análise (FR-008), mostra
  também os campos alterados e a data do reenvio.
- **FR-019 [Arquitetura]**: As telas da moderação seguem o padrão das telas de operação (017,
  025): lista do escopo com estado vazio, confirmação explícita, conflito, operador fictício,
  sem Django admin.

**Página do encontro e confirmação**

- **FR-020 [Arquitetura]**: "Vou participar" só aparece a Pessoa identificada com Conclusão, em
  encontro Publicado antes do início. Antes do botão, a **ciência da participação** versionada
  diz:
  - quem fica sabendo: o organizador e a moderação veem só a quantidade, e ninguém vê o nome
    da pessoa;
  - que o link aparece depois de confirmar;
  - que confirmar não é inscrição nem comprova presença;
  - que a pessoa pode cancelar até o início;
  - que não há e-mail nem notificação;
  - que o encontro acontece fora do Portal.

  A versão e o momento ficam na Confirmação (XVII).
- **FR-021 [Arquitetura]**: O link da reunião só é exibido, e só sai do servidor, para:
  - a Pessoa com Confirmação ativa e sessão;
  - o organizador;
  - a moderação.

  Ele nunca é exibido sem sessão, depois do término, em encontro cancelado, retirado ou em
  revisão depois de uma alteração, nem no `.ics`.
- **FR-022 [Arquitetura]**: Sem sessão, o endereço do encontro mostra uma página neutra, sem
  título, data, nome nem origem, com "Confirme seus dados para ver". Depois da identificação,
  a pessoa volta a esse encontro. O destino é preservado por **lista fechada** (só o padrão de
  rota de encontro, com identificador existente), nunca por URL livre (ADR 0008, item 5).
- **FR-023 [Arquitetura]**: O participante cancela a própria confirmação até o início, com
  confirmação explícita. O link deixa de aparecer imediatamente.
- **FR-024 [Hipótese, H-3106; ADR 0010]**: A página mostra a egressos identificados com
  Conclusão:
  - título, descrição, data, horário, público em linguagem simples e situação;
  - nome de apresentação ("nome escolhido por quem propõe") e origem (curso, unidade e ano,
    marcados como registro do Ifes), conforme os campos, destinatários e finalidade da
    [ADR 0010](../../docs/adr/0010-dado-de-egresso-visivel-a-outros-egressos.md);
  - quem moderou ("Publicado após análise da CPAEG" ou "da CSAEG {unidade}").

  Nunca mostra lista de quem confirmou, quantidade de confirmações a quem não organiza, nem
  contato.

**Organizador**

- **FR-025 [Arquitetura]**: "Seus encontros" lista os encontros da Pessoa como organizadora,
  com a situação, o motivo quando houver e, nos publicados e encerrados, "N pessoas
  confirmaram", só com o número.
- **FR-026 [Arquitetura]**: O organizador vê o link e o endereço da página para compartilhar,
  mesmo sem confirmar. Compartilhar é mostrar o endereço em texto selecionável, sem
  JavaScript nem botão de rede social.

**Calendário**

- **FR-027 [Arquitetura]**: Quem confirmou e o organizador podem baixar um `.ics` com:
  - título, início e término, com fuso;
  - o endereço da página como `URL` e na descrição;
  - um identificador estável;
  - uma sequência que aumenta quando a data muda ou o encontro é cancelado.

  Ele **não** traz o link da reunião, o nome do organizador, a origem nem dado de quem baixa.
- **FR-028 [Arquitetura]**: Junto do download, a tela diz: "Se a data mudar ou o encontro for
  cancelado, o calendário que você baixou não muda sozinho. Confira esta página antes do
  encontro." O mesmo aviso aparece quando a data foi alterada.

**Denúncia**

- **FR-029 [Hipótese, H-3107; D8]**: "Denunciar este encontro" aparece a Pessoa identificada com
  Conclusão, em encontro Publicado ou Encerrado.
  - Motivos provisórios: link suspeito ou que não funciona; divulgação comercial; desrespeito
    a pessoas; parece evento oficial do Ifes; outro motivo.
  - Complemento de até 300 caracteres, com orientação para não incluir dados pessoais.
  - Uma denúncia por pessoa e encontro.
  - A confirmação diz que a moderação responsável foi avisada, sem prazo nem resposta
    prometidos.
  - Dados, finalidade e quem consulta: tabela da Denúncia em "Fatos novos". Sem situação,
    atribuição nem resposta.

**Identidade, vínculo e moderação**

- **FR-030 [Arquitetura]**: São três controles distintos, e nenhum substitui outro:
  - **identificação** (quem é): a da 018, por conhecimento, sem garantia forte;
  - **vínculo acadêmico** (se é egresso): ao menos uma Conclusão Acadêmica;
  - **moderação** (o que é publicado): decisão sobre o conteúdo, antes da publicação.

  A garantia exigida do organizador para uso real é proporcional ao risco e está em DP-1808.
  Nenhum mecanismo é presumido.

**Fronteira e dados**

- **FR-031 [Arquitetura]**: Encontro, Confirmação e Denúncia vivem na camada do Portal. O
  núcleo não as importa nem cita. Desligar ou remover a camada não exige migração no núcleo.
  Isso é verificado no teste de fronteira (ADR 0008).
- **FR-032 [Arquitetura]**: Nenhum dos três entra em snapshot, exportação, indicador ou tela de
  acompanhamento da coleta. Confirmações **não** têm exportação, nem para o organizador nem
  para a moderação.
- **FR-033 [Arquitetura]**: A coleta não muda. Nada passa por `/acesso/`, pela escolha de
  formações ou pelas Seções. Encontros não leem Participação, Resposta nem contato.
- **FR-034 [Arquitetura]**: A 031 não pede, não guarda e não lê e-mail nem telefone. O e-mail
  de pesquisas (020) e o da contribuição (026) **não** são reutilizados.
- **FR-035 [Arquitetura]**: Migrações só aditivas, sem dependência nova. Toda a feature fica
  restrita ao modo de demonstração e ao Portal ligado.

**Experiência**

- **FR-036 [Arquitetura]**: Identidade C (ADR 0009, revisão de 2026-10-11), com o celular como
  referência:
  - a 375×812, o título e a data do encontro sem rolar;
  - sem rolagem horizontal de 320 a 1440 px, com fonte a 100% e a 200%;
  - alvos de 44 px, um h1 por tela, foco da 015, contraste AA;
  - sem JavaScript.
- **FR-037 [Hipótese, H-3105]**: A navegação ganha "Encontros", para quem tem Conclusão, entre
  "Oportunidades" e "Participação". "Propor um encontro" e "Seus encontros" ficam na página
  Encontros.

### Finalidade, visibilidade e retenção

| Dado | Finalidade | Quem vê | Retenção |
|---|---|---|---|
| Encontro: título, descrição, data, público | Divulgar e permitir a participação | Egressos identificados com Conclusão; organizador; moderação | D9. Na demonstração, sem exclusão |
| Nome de apresentação e origem | Dizer quem propõe ([ADR 0010](../../docs/adr/0010-dado-de-egresso-visivel-a-outros-egressos.md)) | Os mesmos. Nunca sem sessão nem no `.ics` | D9 |
| Link da reunião | Acesso de quem confirmou | Quem confirmou (com sessão), organizador, moderação | D9 |
| Confirmação | Mostrar o link a quem confirmou; informar a quantidade | A própria pessoa. Organizador e moderação veem só o número | D9. A avaliar: não guardar depois do encerramento |
| Motivos de recusa e retirada | Prestar contas ao organizador | Organizador; moderação | D9 |
| Denúncia | Levar o problema à moderação | Moderação, sem saber quem denunciou. O denunciante vê que denunciou. O organizador não vê | D9 |

A base legal de cada tratamento (organização, confirmação, denúncia) é **D9** e não é
presumida. Termo e ciência registram que a pessoa foi informada, e só isso.

### Requisitos revisados (na implementação, se autorizada)

As telas servidas **não** mudam nesta tarefa. A implementação terá de revisar, de forma
explícita:

| Origem | Revisão necessária |
|---|---|
| ADR 0009, decisão 7; 024 FR-021 ("comunidade" vedada) | "Comunidade" admitida **só** na página Encontros e na seção de encontros do Início, ligada à experiência concreta (revisão 12). Continua vedada na página pública, em Oportunidades, Minha trajetória, card e Participação |
| 029 FR-007; 032 FR-005 a FR-007, SC-005 (página pública) | A página pública só passa a citar encontros propostos por egressos quando F existir na demonstração, sempre com selo de exemplo. "Comunidade" continua fora dela |
| 032 FR-008; `ENCONTROS_TEXTO` ("Encontros de egressos divulgados pelo Ifes…") | O texto precisa cobrir F, que **não** é divulgado nem organizado pelo Ifes: "Encontros com outros egressos: alguns propostos por egressos, outros divulgados pelo Ifes." |
| 032 FR-011; 024 FR-022, FR-023 (navegação) | Quinto item "Encontros" (H-3105). Os testes de largura da navegação da 025 (cinco itens) voltam a valer |
| 024 FR-006; `portal/destinos.py` (destinos fixos) | Destino preservado por lista fechada, só para a página de encontro (FR-022) |
| 024 FR-029; 025 FR-037; 026 (escritas da camada) | Escritas novas do egresso (Encontro, Confirmação, Denúncia) e da moderação (publicar, recusar, retirar) |
| `tests/portal/test_fronteiras.py` | Três modelos novos na camada |
| ADR 0009, decisão 7 (contagens de egressos) | "N pessoas confirmaram" é admitido só para o organizador e a moderação. Nunca é contador público |
| Vocabulário de F | "Vou participar", "Você vai participar", "Cancelar minha participação", "Proposto por egresso". A confirmação nunca é chamada de "inscrição", nem quem confirmou de "inscrito", e nada diz que ela registra "presença" (o texto pode negar as duas coisas, como na ciência). F nunca é "evento oficial". Continuam vedados "turma", "geração", "conectad"; "seguidores" e "grupo" também ficam fora |
| Rótulo de A nos contextos de encontros | "Evento do Ifes". Em Oportunidades, a categoria "Eventos" não muda |

## Success Criteria

### Medidos (na implementação)

- **SC-001**: Nenhum encontro aparece a outra pessoa sem publicação registrada, com operador.
- **SC-002**: O link da reunião não aparece no HTML de quem não confirmou, sem sessão, no `.ics`
  nem depois do término (teste sobre a resposta).
- **SC-003**: O organizador vê só a quantidade de confirmações. Nenhuma tela ou arquivo traz
  quem confirmou.
- **SC-004**: Cada operador vê só os encontros do seu escopo (FR-016); fora dele, recusa.
- **SC-005**: Recusa e retirada sempre com motivo; o organizador vê o motivo.
- **SC-006**: Encontro, Confirmação e Denúncia fora de snapshot, exportação e indicador; o núcleo
  não importa a camada (teste de fronteira).
- **SC-007**: Com o Portal desligado, nenhuma rota da 031 existe e a coleta não muda.
- **SC-008**: A 031 não lê nem grava e-mail, telefone ou `ContatoDaPessoa`.
- **SC-009**: Medidas de FR-036 nas telas do egresso.

### Qualitativos (Checkpoint 2)

Ver "Critérios que o Checkpoint 2 deve avaliar", abaixo.

### Verificação do protótipo (feita nesta tarefa, sem valor de validação)

Sem rolagem horizontal de 320 a 1440 px com fonte a 100% e 200%, um h1 por tela, alvos de
44 px e título e data a 375×812, medidos com o arnês dos protótipos da ADR 0009.
Resultados em [`prototipo/medidas.json`](prototipo/medidas.json) e no
[índice do protótipo](prototipo/index.html). São verificações técnicas. **Não são validação com
egressos.**

## Critérios que o Checkpoint 2 deve avaliar

O bloco Comunidade do [protocolo](../../docs/validacao/checkpoint-2/protocolo.md) já tem os
critérios abaixo. O protótipo da 031 é o material das tarefas F1 a F4:

| Critério | Tarefa | Tela do protótipo | "Sim" quando a pessoa… |
|---|---|---|---|
| CM-C1: proposto por egresso × evento do Ifes | F1 | Encontros (lista) | diz quem organiza cada um e que publicar não faz do Ifes o organizador |
| CM-C2: quem vê a confirmação e o link | F2 | Página do encontro, antes e depois de confirmar | diz que a confirmação não é pública e que o link só aparece a quem confirmou |
| CM-C4: nenhuma função inexistente | Fechamento | Todas | não atribui mensagens, lista de participantes, lembretes ou sala do Ifes |
| CM-U1: proporia | F4 | Propor um encontro | registro: sobre o quê e para quem |
| CM-U2: participaria | F3 | Página do encontro | registro: de qual tipo |

**Observações exploratórias desta spec** (Q8 da
[preparação](../../docs/validacao/checkpoint-2/preparacao-sessao.md), decidida na revisão de
produto de 2026-10-11). São anotadas como **sim**, **parcial** ou **não**, com a frase
literal, mas **não têm limiar** e não aprovam nem reprovam nada nesta rodada. A pergunta
primeiro é se as pessoas entendem os encontros, se proporiam e se participariam.

| Observação | Pergunta sugerida | Tela | Anotar se a pessoa… |
|---|---|---|---|
| CM-F1: por que aparece | "Por que este encontro aparece para você?" | Encontros (lista) | explica pela formação que concluiu, ou diz que é aberto a todos |
| CM-F2: análise antes de publicar | Como organizadora: "Depois de enviar, quem vê este encontro? E se o Ifes não aceitar?" | Confira e envie; Em análise | diz que ninguém o vê antes da análise e que a recusa vem com motivo |
| CM-F3: o calendário não se atualiza | "Se a data mudar depois que você baixou o calendário, o que acontece?" | Confirmado | diz que o arquivo não muda e que é preciso conferir a página |
| CM-F4: cancelar | "Se você não puder ir, o que faz? E se quem propôs desistir?" | Confirmado; Cancelado | diz que pode cancelar a própria confirmação e que a página mostra o cancelamento |
| CM-F5: público é descoberta, não exclusividade | Na página de um encontro proposto para outra formação: "Você poderia participar deste? Por quê?" | Fora do público (p7) | diz que o encontro foi pensado para certas formações, mas que quem recebe o endereço também pode participar |

**Como ler.** CM-C1 e CM-C2 seguem a leitura já escrita no protocolo, com o limiar de Q1. As
observações CM-F1 a CM-F5 informam, sem limiar, o que a spec e o protótipo precisam rever
antes de qualquer implementação. Elas não são taxa de adesão. CM-U1 e CM-U2 informam a escolha
entre 031 e 030.

**Seleção para a sessão.** As 33 telas cobrem a spec; a sessão do Checkpoint 2 usa um
percurso curto, a escolher no preparo do material do bloco Comunidade (roadmap, §13.3, passo
5), com as telas que produzem evidência para essas perguntas.

**Não cobertos por este protótipo:** CM-C3 e CM-U3 (diretório, E1) e CM-U4 (histórias, 030).
O bloco Comunidade continua precisando do material de Histórias e de Encontre colegas
(roadmap, §13.3, passo 5).

## Invariantes Constitucionais Afetados

- **II, III, IV:** só Conclusões institucionais habilitam e definem pertinência e origem; nome
  de apresentação e textos são declarados pelo organizador e apresentados como dele.
- **VI:** respondida em "Fronteira do NIAE".
- **X, Governança de Permissões:** "moderar encontros" é competência nomeada, com hipótese de
  escopo (H-3102), sem fluxo inventado: uma decisão, sem segunda aprovação.
- **XV:** a identificação é a da 018, substituível. DP-1808 continua aberta.
- **XVI:** sem e-mail, sem lista nominal, sem contagem pública, link restrito, denunciante não
  identificado à moderação; exposição do organizador limitada pela ADR 0010; base legal e
  retenção pendentes.
- **XVII:** termo do organizador e ciência da participação versionados, com momento.
- **XX, XXI:** FR-036.
- **XXII:** três fatos específicos, sem entidade genérica, sem notificação nem integração.
- **XXIX:** H-3101 a H-3108 são hipóteses da demonstração, reversíveis e localizadas. Nenhuma
  delas é competência institucional aprovada.
- **ADR 0008:** dependência num só sentido; fatos fora do dado analítico; coleta independente.

## Fronteira do NIAE

1. **Pertence ao acompanhamento?** Não. É relacionamento, na camada do Portal (ADR 0008).
2. **É necessária ao ciclo de acompanhamento?** Não. A coleta funciona igual sem ela.
3. **Existe ou está prevista solução institucional mais adequada?**
   - A Constituição VI lista "eventos" e "comunidade de ex-alunos" entre as capacidades que
     deveriam ficar externas quando houver solução adequada.
   - Conhecidas: o aplicativo da DIREC voltado a estudantes e egressos, os grupos de ex-alunos
     autogeridos e os encontros anuais em campi.
   - Nenhuma é conhecida por moderar encontros virtuais propostos por egressos. Isso não foi
     verificado com a DIREC, por decisão do solicitante.
   - Ponto de atenção para uso real (D10). Não bloqueia a demonstração.
4. **Integração bastaria?** Para videoconferência, sim: o link é externo e não há integração.
   Para moderação e confirmação, não há sistema de destino conhecido.
5. **Aumenta o acoplamento do núcleo?** Não. Só a camada muda, e ela é desligável.

## Out of Scope

- Encontros presenciais: continuam pela alternativa A, com apoio da CSAEG (Art. 22, VII).
- Chat, comentários, curtidas, reações, contador público e lista nominal pública.
- Notificações e lembretes automáticos, por qualquer canal.
- Integração com videoconferência e criação de sala, inclusive ConferênciaWeb/RNP.
- Contato exposto, mensagens entre egressos e perfil público.
- Recorrência, co-organização, limite de vagas, avaliação depois do encontro, exportação de
  confirmações e suspensão de organizador.
- Histórias de egressos (030) e Encontre colegas (E1).
- Correção dos achados A-01 a A-04. Plan e tasks.

## Decisões Pendentes

**Bloqueiam o uso real, não a demonstração** (roadmap §11.2):

- **D8 — DECISÃO PENDENTE (CPAEG, com as CSAEG e a Proex):**
  - quem modera cada recorte de público;
  - critérios de publicação, recusa e retirada;
  - prazo de análise;
  - quem recebe denúncias e por qual canal;
  - o que fazer com organizador reincidente.
- **D9 — DECISÃO PENDENTE (encarregado de dados, com a CPAEG):** base legal da organização, da
  confirmação, da denúncia e da exibição do nome e da origem do organizador a outros egressos;
  retenção de cada um.
- **D10 — DECISÃO PENDENTE (Proex, DIREC e CPAEG):** complementaridade com o aplicativo da
  DIREC, com associações e com grupos de ex-alunos.
- **DP-1808 — DECISÃO PENDENTE (Proex, DTI e encarregado):** garantia de identidade exigida do
  organizador e, se for o caso, do participante.
- **D2, DP-801:** nome e textos definitivos, inclusive termo, ciência e motivos.

**Novas desta spec:**

- **DP-3101 — Resolvida para a demonstração** (revisão de produto de 2026-10-11): a primeira
  exposição de dado de um egresso a outro (nome de apresentação e origem do organizador) está
  na [ADR 0010](../../docs/adr/0010-dado-de-egresso-visivel-a-outros-egressos.md), com
  campos, destinatários e finalidade. Para uso real, continua dependendo de D9, DP-1808 e
  DP-2103. O E1 precisa de ADR própria.
- **DP-3102 — DECISÃO PENDENTE (solicitante):** se a página sem sessão continua neutra (FR-022)
  ou mostra título e data para quem recebe o endereço. A neutra é mais restritiva e tem
  pré-visualização pobre em aplicativos de mensagem.

**Hipóteses da demonstração (reversíveis, XXIX):**

| # | Hipótese | Onde | Revisão por |
|---|---|---|---|
| H-3101 | Limites de texto, de 2 a 90 dias de antecedência, até 3 h | FR-002 | Checkpoint 2; D8 |
| H-3102 | CSAEG para unidade única; CPAEG nos demais casos. Não é competência institucional aprovada | FR-016 | D8 |
| H-3103 | Depois de publicado: data, horário e link no mesmo domínio são correção operacional; o resto, e link de outro domínio, pede nova análise | FR-008 | Checkpoint 2; D8 |
| H-3104 | Motivos de recusa e retirada | FR-017 | D8 |
| H-3105 | Item "Encontros" na navegação; F e A na mesma página, em grupos separados | FR-013, FR-037 | Checkpoint 2 |
| H-3106 | Nome de apresentação escolhido pelo organizador, com a origem | FR-024; ADR 0010 | D9; DP-1808; DP-2103 |
| H-3107 | Denúncia como registro mínimo na camada, sem atendimento | FR-029 | D8 (canal externo possível) |
| H-3108 | Público como contexto de descoberta, sem restringir quem confirma | FR-004 | Checkpoint 2 (CM-F5); D8 |

**Checkpoints.** O Checkpoint 1 e o Checkpoint 2 estão **NÃO APLICADOS**. Esta spec não os
substitui e não presume seus resultados.
