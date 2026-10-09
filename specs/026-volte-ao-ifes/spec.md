# Feature Specification: Volte ao Ifes — o egresso se oferece para contribuir

**Feature Branch**: `claude/029-pagina-publica` (documentos); a implementação terá branch própria
**Created**: 2026-10-09
**Status**: Especificação, com as decisões D-2601 a D-2603 tomadas para a demonstração em
2026-10-09. [Plan](plan.md), [tasks](tasks.md) e [protótipos](prototipo/index.html) prontos.
**Implementação autorizada em 2026-10-09, só na demonstração** (T001; roadmap, revisão 10),
em branch e PR próprios. O Checkpoint 1 continua **NÃO APLICADO** e será aplicado depois,
sobre a experiência implementada. D4 e D5 continuam `DECISÃO PENDENTE` e precisam ser
resolvidas antes de uso real.
**Input**: Solicitante, 2026-10-09: o Portal é uma relação nos dois sentidos. Hoje só existe o
sentido Ifes → egresso (oportunidades da 025). Esta feature abre o sentido egresso → Ifes:
o egresso diz como quer contribuir, sabe quem recebe e o que acontece depois. Corresponde à
S3 do [roadmap do Portal](../../docs/roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md)
("Volte ao Ifes: manifestação de interesse").

## Contexto e dependências

| Fato verificado | Fonte | Consequência para a 026 |
|---|---|---|
| A S3 prevê um fato novo, a **Manifestação de interesse**: forma de contribuição em lista fechada, formação de referência, mensagem curta opcional, versão do texto de ciência, momento e retirada | Roadmap §6, S3; ADR 0008 | É o núcleo desta spec |
| Fora da S3: workflow de atendimento (estados, atribuição, prazos), programa de mentoria, agenda, pareamento, perfil público, coleta de currículo ou de história | Roadmap §6, S3 | Mantido fora |
| Riscos nomeados: expectativa frustrada (ninguém responde) e base legal | Roadmap S3; D4 e D5 | Viram requisitos de texto honesto e decisões pendentes |
| A PAEG atribui à CSAEG a gestão do Portal na unidade; a atuação institucional (CPAEG) tem fundamentação mais fraca | PAEG Art. 13, parágrafo único; Art. 22, III; 025 (DP-2501) | Quem recebe é a CSAEG da unidade da formação de referência; CPAEG como hipótese |
| Escopo de governança: CPAEG institucional; CSAEG nas próprias unidades; operadores fictícios na demonstração | `trajetoria/governanca/`; 010; 025 | Reaproveitado |
| Telas de operação no padrão do acompanhamento e da 017: lista, formulário, confirmação explícita, conflito; sem Django admin | 025; 017 | Reaproveitado para a lista da unidade |
| O e-mail da Pessoa já existe (`ContatoDaPessoa`), com finalidade declarada de **contato sobre pesquisas**; a tela promete que ele "não será usado para outra finalidade"; o registro é imutável e todo e-mail da Pessoa entra na política de convites | 020 FR-012; `contato/models.py`; `meu_email.html` | Usá-lo para responder a uma contribuição seria outra finalidade, e cadastrar e-mail ali para contribuir obrigaria a aceitar convites. A contribuição guarda **o próprio e-mail**, informado pela pessoa, com finalidade própria (D-2602) |
| Consentimento: quando houver termo, relacionar versão, momento e manifestação; regra jurídica não definida não é inferida | Constituição XVII, XVI | Texto de ciência versionado; base legal é `DECISÃO PENDENTE` |
| O Portal tem hoje um só modelo (`Oportunidade`), sem chave estrangeira para o núcleo, e as telas do egresso não gravam nada | `tests/portal/test_fronteiras.py`; 024 FR-029; 025 | A 026 é a **primeira escrita do egresso** na camada. Revisa essas regras de forma explícita |
| A camada é desligável; a reversão não pode exigir migração no núcleo | ADR 0008 | O núcleo não passa a depender da Manifestação |
| O roadmap punha a S3 depois do Checkpoint 1, que continua **NÃO APLICADO**. Em 2026-10-09 o solicitante antecipou a 026 na demonstração, como fez com a 025 (revisão 5) | Roadmap §8; revisão 10 | Implementação autorizada só na demonstração; o Checkpoint 1 vem depois, sobre a experiência implementada |
| O Checkpoint 2 avalia valor e reciprocidade: entender quem recebe, o que acontece depois e que pode retirar | Roadmap §7 | Critérios qualitativos já escritos; esta spec os usa |

## O percurso completo da contribuição

```text
 EGRESSO                          SISTEMA                          IFES (unidade)
 ─────────────────────────────    ─────────────────────────────    ─────────────────────────────
 1. Abre "Contribuir com o Ifes"
    (Início ou navegação)
 2. Escolhe como quer contribuir
    (lista fechada) e a formação
    de referência
 3. Escreve uma mensagem curta,
    se quiser
 4. Lê para quem vai, o que
    acontece depois e como o
    e-mail será usado; confirma   → registra a Manifestação, com a
                                    versão do texto de ciência e
                                    o momento
 5. Vê a confirmação: o que       ← mostra a unidade que recebe e o
    enviou, para quem e o que       que esperar (texto honesto,
    esperar                         sem prazo prometido)
                                                                   6. CSAEG da unidade vê a lista
                                                                      do seu escopo, com a forma,
                                                                      a formação, a mensagem e o
                                                                      contato autorizado; exporta
                                                                      CSV
                                                                   7. Faz o contato fora do sistema
                                                                      (e-mail), pelos canais da
                                                                      unidade
                                                                   8. Registra "contato feito" na
                                                                      manifestação (D-2601)
 9. Em "Suas contribuições", vê o
    que enviou, se a unidade já
    registrou contato, e pode
    retirar a qualquer momento    → registra a retirada; a
                                    manifestação sai da lista e do
                                    CSV da unidade
```

**O que o sistema não faz:** não encaminha automaticamente, não envia notificação, não
controla prazo nem atendimento, não junta pessoas entre si. O contato (passo 7) acontece fora
do sistema. A única continuidade registrada é o marco "contato feito" (passo 8, D-2601), que
o egresso vê.

## User Scenarios & Testing

### US1 — Oferecer uma contribuição em poucos passos (P1)

Diego, egresso de Química na unidade Vila Velha, quer conversar com estudantes sobre a
carreira dele. No Portal, escolhe "Compartilhar experiência", indica a Licenciatura em
Química como formação de referência e escreve duas linhas. Antes de confirmar, lê que a
unidade Vila Velha recebe, que o Ifes pode usar o e-mail dele para responder sobre essa
contribuição e que ele pode retirar quando quiser.

**Why this priority**: é o primeiro caminho egresso → Ifes no produto.

**Independent Test**: com a persona Diego (três formações), registrar uma manifestação e
conferir a gravação com forma, formação, mensagem, versão do texto de ciência e momento.

1. **Dado** um egresso com sessão e ao menos uma Conclusão, **quando** abre "Contribuir com
   o Ifes", **então** vê as formas de contribuição da lista fechada e as próprias formações.
2. **Dado** que escolheu forma e formação, **quando** chega à confirmação, **então** lê a
   unidade que recebe, o que acontece depois e como o e-mail será usado, antes de confirmar.
3. **Dado** a confirmação, **quando** o egresso a vê, **então** informa um e-mail para a
   resposta sobre a contribuição. O campo é obrigatório e vem vazio, com a finalidade escrita
   ao lado: só para o Ifes responder sobre esta contribuição, sem incluir a pessoa em
   convites de pesquisa (D-2602).
4. **Dado** que confirmou, **quando** a gravação termina, **então** vê o resumo do que enviou
   e para quem.

### US2 — Saber o que enviou e poder retirar (P1)

**Independent Test**: registrar, ver em "Suas contribuições", retirar e conferir que a
manifestação sai da lista da unidade e fica registrada como retirada.

1. **Dado** um egresso com manifestações, **quando** abre "Suas contribuições", **então** vê
   cada uma com forma, formação, unidade, data e situação: enviada, contato registrado pela
   unidade (com a data) ou retirada.
2. **Dado** uma manifestação ativa, **quando** confirma a retirada, **então** ela fica
   registrada como retirada, com o momento, e some da lista e do CSV da unidade.
3. **Dado** uma manifestação retirada, **quando** o egresso quiser contribuir de novo,
   **então** registra uma nova; a retirada não é desfeita (imutabilidade do registro).

### US3 — A unidade recebe e dá seguimento (P1)

Uma operadora CSAEG da unidade Vila Velha abre a lista de manifestações do seu escopo, vê a
de Diego e exporta o CSV para fazer o contato.

**Independent Test**: com operadores fictícios CSAEG de unidades diferentes e CPAEG,
conferir que cada um vê só o próprio escopo e que o CSV traz só as ativas.

1. **Dado** uma operadora CSAEG, **quando** abre a lista, **então** vê só manifestações
   ativas cuja formação de referência é de uma unidade do seu vínculo.
2. **Dado** a lista, **quando** exporta o CSV, **então** o arquivo traz forma, formação,
   unidade, mensagem, data, o e-mail informado para a contribuição e a situação, sem CPF nem
   data de nascimento.
3. **Dado** uma manifestação ativa sem contato registrado, **quando** a operadora confirma
   "Registrar contato feito", **então** o marco é gravado com o momento e o operador, uma
   única vez, e o egresso passa a vê-lo.
4. **Dado** um operador sem vínculo com a unidade, **quando** tenta acessar a manifestação,
   **então** recebe a recusa do padrão de governança.

### Edge Cases

- **Várias formações em unidades diferentes:** a formação de referência escolhida define a
  unidade que recebe. Uma manifestação, uma unidade.
- **A mesma forma de novo para a mesma formação:** não duplica; o egresso vê que já tem uma
  ativa e pode retirá-la ou mantê-la.
- **Formação declarada (019):** não serve como formação de referência, validada ou não
  (D-2603). Só Conclusões Acadêmicas da Pessoa identificada.
- **Pessoa sem Conclusão:** não vê "Contribuir com o Ifes"; o Início segue a 024.
- **E-mail da contribuição × e-mail do contato:** são registros separados. Mudar o e-mail
  em Meu e-mail não muda o da contribuição, e informar o da contribuição não cadastra contato
  para pesquisas.
- **Portal desligado:** nada aparece; a coleta não é afetada (ADR 0008).
- **Mensagem com dado sensível:** a mensagem é curta e livre; o texto da tela orienta a não
  incluir dados pessoais além do necessário.

## Requirements

### Functional Requirements

**Manifestação**

- **FR-001 [Arquitetura]**: DEVE existir um fato novo, **Manifestação de interesse**, com:
  Pessoa; formação de referência (uma Conclusão Acadêmica da Pessoa); forma de contribuição;
  mensagem opcional; e-mail para a resposta; versão do texto de ciência apresentado; momento
  do registro; contato registrado pela unidade (momento e operador), quando houver; momento
  da retirada, quando houver.
- **FR-002 [Hipótese]**: A forma de contribuição DEVE vir de uma **lista fechada**: mentoria;
  compartilhar experiência (conversa, palestra, roda com estudantes); oferecer oportunidade
  (vaga, estágio, curso ou programa da organização em que atua); pesquisa e extensão;
  parceria com organização; contar a própria história. A redação final é da CPAEG (DP-801).
- **FR-003 [Arquitetura]**: A mensagem DEVE ser opcional e curta (limite definido no plan) e
  a tela DEVE orientar a não incluir dados pessoais além do necessário.
- **FR-004 [Arquitetura]**: O e-mail para a resposta DEVE ser informado pela pessoa no fluxo,
  obrigatório e sem pré-preenchimento, e guardado **na manifestação**, com a finalidade
  "resposta do Ifes sobre esta contribuição" (D-2602). NÃO DEVE gravar nem alterar
  `ContatoDaPessoa`, nem entrar na política de convites da 020.
- **FR-005 [Arquitetura]**: A retirada DEVE ser feita pela própria Pessoa, a qualquer
  momento, e registrada com o momento. Manifestação retirada não é reativada e sai da lista e
  do CSV da unidade. A retenção do registro e do e-mail depois da retirada é D5.
- **FR-005a [Arquitetura]**: O marco **"contato feito"** DEVE ser registrado pela unidade
  (operador do escopo), uma única vez por manifestação ativa, com momento e identificador
  opaco do operador (precedente da 019 e da 025). Não há outros estados, atribuição nem prazo
  (D-2601). O egresso vê o marco com a data e a unidade.
- **FR-006 [Arquitetura]**: NÃO DEVE haver duas manifestações ativas com a mesma Pessoa,
  forma e formação de referência.

**Ciência e finalidade**

- **FR-007 [Arquitetura]**: Antes de confirmar, a tela DEVE mostrar um **texto de ciência
  versionado** com: a unidade que recebe; que o e-mail informado é usado só para o Ifes
  responder **sobre esta contribuição** e não inclui a pessoa em convites de pesquisa; o que
  acontece depois, sem prazo prometido; que a unidade pode registrar o contato feito; e como
  retirar. A versão apresentada é registrada na manifestação (XVII).
- **FR-008 [Arquitetura]**: O e-mail da contribuição DEVE ter finalidade própria, distinta do
  contato sobre pesquisas (020), e NÃO DEVE ser lido pela mobilização nem por nenhuma
  exportação além da lista da unidade. Enquanto a base legal não for definida (D5), o
  tratamento é só de demonstração.

**Quem recebe**

- **FR-009 [Hipótese]**: Recebe a **CSAEG da unidade** da formação de referência (PAEG Art.
  13, parágrafo único). A **CPAEG** vê todas, como hipótese (DP-2501).
- **FR-010 [Arquitetura]**: A lista da unidade DEVE seguir o padrão das telas de operação
  (017, 025): só o escopo do vínculo, recusa fora dele, confirmação explícita para registrar
  contato, sem Django admin. Exportação CSV só das manifestações ativas do escopo, com o
  e-mail da contribuição, sem CPF nem data de nascimento, protegida contra fórmulas.

**Experiência do egresso**

- **FR-011 [Hipótese]**: "Contribuir com o Ifes" DEVE aparecer no Início, como bloco próprio
  depois de Oportunidades e antes do convite à pesquisa, e na navegação, só para Pessoa com
  Conclusão. A ordem revisada fica: reconhecimento → proveniência → ações → Oportunidades →
  Contribuir → convite (revisa 024 FR-016).
- **FR-012 [Arquitetura]**: O fluxo DEVE ter no máximo três telas (escolha, confirmação com
  ciência, resultado) e funcionar sem JavaScript, com a acessibilidade da 015 e os tokens da
  ADR 0009.
- **FR-013 [Arquitetura]**: "Suas contribuições" DEVE listar as manifestações da própria
  Pessoa, com situação (enviada, contato registrado em data, retirada) e ação de retirar.
- **FR-013a [Arquitetura]**: A formação de referência DEVE ser uma Conclusão Acadêmica da
  Pessoa identificada; Formação Declarada (019) não é oferecida (D-2603).
- **FR-014 [Arquitetura]**: Os textos NÃO DEVEM prometer resposta, prazo, vaga, remuneração
  ou certificado. Vocabulário da ADR 0009 (decisão 7) e da 025.

**Fronteira**

- **FR-015 [Arquitetura]**: A Manifestação vive na camada do Portal. O núcleo NÃO DEVE
  depender dela, e desligar ou remover a camada não exige migração no núcleo (ADR 0008). Se
  a Manifestação referencia Pessoa e Conclusão por chave estrangeira ou por identificador, é
  decisão do plan. As duas opções revisam o teste de fronteira atual.
- **FR-016 [Arquitetura]**: A Manifestação NÃO DEVE entrar no dado analítico nem nas
  exportações da pesquisa (roadmap: "nada do anel de relacionamento entra no dado
  analítico").
- **FR-017 [Arquitetura]**: Migrações só aditivas (XXVII). Nenhuma dependência nova.

### Requisitos revisados (a confirmar no plan)

| Origem | Revisão |
|---|---|
| 024 FR-016 | Ordem do Início ganha o bloco Contribuir entre Oportunidades e o convite |
| 024 FR-029; 025 (telas do egresso não gravam) | A tela de contribuição grava a Manifestação e a retirada; a unidade grava o marco "contato feito". As demais telas do egresso continuam sem gravar |
| `tests/portal/test_fronteiras.py` | Passa a admitir dois modelos na camada, `Oportunidade` e `Manifestação`, com a forma de referência ao núcleo decidida no plan |
| 024 FR-022/FR-023 e 025 (navegação) | Navegação ganha "Contribuir" para quem tem Conclusão |

### Key Entities

- **Manifestação de interesse** (nova, camada do Portal): ato da Pessoa, com forma, formação
  de referência, mensagem opcional, ciência versionada, momento, retirada.
- **Pessoa, Conclusão Acadêmica, VinculoDeGovernanca** (existentes, lidos). `ContatoDaPessoa`
  não é lido nem gravado (D-2602).

## Success Criteria

### Medidos

- **SC-001**: Do Início à confirmação em no máximo três telas, sem JavaScript.
- **SC-002**: Toda manifestação gravada tem a versão do texto de ciência e o momento.
- **SC-003**: Operador CSAEG vê só o próprio escopo; fora dele, recusa. CSV sem CPF nem data
  de nascimento, só manifestações ativas.
- **SC-004**: Retirada registrada com momento; a manifestação some da lista e do CSV.
- **SC-004a**: "Contato feito" só pelo operador do escopo, uma vez, com momento e operador; o
  egresso vê a data. Contribuir não grava nem altera `ContatoDaPessoa`, e o e-mail da
  contribuição não aparece na política de convites (teste).
- **SC-005**: Nenhuma Manifestação aparece em dado analítico ou exportação da pesquisa.
- **SC-006**: Com o Portal desligado, nada da 026 aparece e a coleta não muda.
- **SC-007**: Texto visível sem promessa de resposta, prazo, vaga ou certificado, verificado
  em teste.

### Qualitativos (Checkpoint 2, já escrito no roadmap §7)

A pessoa entende o que acontece depois e quem recebe; entende que pode retirar; registra
sem dúvida sobre o uso do contato; não confunde contribuir com a pesquisa.

## Invariantes Constitucionais Afetados

- **XVI, XVII:** finalidade própria para o e-mail da contribuição, separado do contato de
  pesquisas; ciência versionada; base legal e retenção pendentes; minimização (só o e-mail
  necessário à resposta, mensagem curta).
- **III, IV:** a manifestação é ato declarado da Pessoa, separado do dado institucional.
- **VI, ADR 0008:** fato da camada; núcleo não depende dele; desligável.
- **XXVII:** migração aditiva.
- **XXII, XXIX:** sem workflow, sem pareamento; formas de contribuição e textos como hipótese.

## Fronteira do NIAE

1. Pertence ao acompanhamento? Não; é relacionamento (camada do Portal, ADR 0008).
2. É necessária à coleta? Não.
3. Há solução institucional definitiva? Não para o Portal (DP-406, DP-2108).
4. Integração basta? Não há sistema de destino; a unidade recebe por lista e CSV.
5. Aumenta acoplamento? Só na camada; o núcleo não muda.

## Out of Scope

Workflow de atendimento (estados, atribuição, prazos); notificação por e-mail ou outro canal;
programa de mentoria, agenda, pareamento ou contato entre egressos; perfil público; coleta de
currículo ou de história; publicação de histórias (ver alternativas de comunidade);
contribuição de quem não tem Conclusão.

## Decisões Pendentes

- **D4 — DECISÃO PENDENTE (Proex/CPAEG):** quem recebe na operação real: CSAEG da unidade,
  CPAEG ou outro setor por forma de contribuição (por exemplo, parcerias pela extensão).
- **D5 — DECISÃO PENDENTE (Proex/CPAEG com a área jurídica e de proteção de dados):** base
  legal do uso do e-mail para responder sobre a contribuição e retenção das manifestações.
- **D-2601 — Decidido (solicitante, 2026-10-09, demonstração):** a unidade registra um marco
  único "contato feito", visível ao egresso. Sem workflow de atendimento.
- **D-2602 — Decidido (solicitante, 2026-10-09, demonstração):** e-mail obrigatório para
  concluir, com finalidade própria, guardado na manifestação. Contribuir não inclui a pessoa
  em convites de pesquisa.
- **D-2603 — Decidido (solicitante, 2026-10-09, demonstração):** só Conclusões Acadêmicas da
  Pessoa identificada. Formação Declarada fica para revisão posterior.
- **DP-801:** redação final das formas e dos textos, com a CPAEG e a ACS.
- **Checkpoint 1 NÃO APLICADO.** A implementação na demonstração foi autorizada em
  2026-10-09 (T001) antes dele; o checkpoint será aplicado depois da 026 e da 029
  implementadas. Se mostrar falha de compreensão, o Início e a navegação são corrigidos
  primeiro, já com a 026 na camada desligável.
