# ADR 0010 — Nome de apresentação e origem do organizador visíveis a outros egressos

- **Status**: Aceito como hipótese de produto, só para a demonstração e só para a
  [Feature 031](../../specs/031-encontros-propostos-egressos/spec.md), que também é hipótese,
  com implementação condicionada aos Checkpoints 1 e 2. Decidido pelo solicitante em
  2026-10-11 (roadmap, revisão 14). O uso real depende de D9.
- **Data**: 2026-10-11
- **Contexto de origem**:
  - [Spec da 031](../../specs/031-encontros-propostos-egressos/spec.md) (FR-024, H-3106, antigo
    DP-3101)
  - [Alternativas de comunidade](../roadmap/2026-10-09-comunidade-alternativas.md), revisão de
    2026-10-11 (E1: "primeira vez que a camada mostra dado de um egresso a outro")
  - [ADR 0008](0008-portal-do-egresso-camada-de-relacionamento.md); Constituição XVI, XVII e
    XXIX

## Contexto

Até a 026, a camada do Portal só mostra a cada egresso os dados dele mesmo. As oportunidades
são do Ifes, e as contribuições vão só à unidade.

A 031 muda isso. Quem decide confirmar presença num encontro proposto por outro egresso
precisa saber quem propõe. Sem nenhuma indicação de autoria, a página pareceria anônima ou
institucional, e o Checkpoint 2 precisa testar a distinção entre "Evento do Ifes" e
"Encontro proposto por egresso" (CM-C1). É a primeira exposição de dado de um egresso a
outro. Por isso a regra fica registrada aqui, e não só na interface.

## Alternativas consideradas

- **Nenhuma identificação:** a página diz só "proposto por um egresso". Rejeitada: tira de
  quem confirma a informação mínima de confiança e esconde quem responde pelo encontro.
- **Só a origem acadêmica, sem nome:** "proposto por egresso de Licenciatura em Química (Vila
  Velha, 2017)". Possível, mas pode identificar a pessoa em cursos pequenos e, ainda assim, não
  diz com quem se vai conversar.
- **Nome do registro acadêmico:** usaria um dado que o egresso não escolheu mostrar. Contraria
  o cuidado da 021 com o nome (DP-2103: nome civil × nome social).
- **Nome de apresentação escolhido pelo organizador, com a origem de uma Conclusão:**
  **escolhida**.

## Decisão

**Campos exibidos**

| Campo | Origem | Regra |
|---|---|---|
| Nome de apresentação | Declarado pelo organizador, até 40 caracteres | Escolhido por ele, por exemplo só o primeiro nome e a inicial. A moderação o vê antes de publicar. A página o apresenta como "nome escolhido por quem propõe" |
| Origem acadêmica | Uma Conclusão Acadêmica escolhida pelo organizador: curso, unidade e ano de conclusão | Marcada "Registro do Ifes". As demais formações da pessoa não aparecem |

**Nunca exibidos**: nome do registro, CPF, data de nascimento, e-mail, telefone, outras
formações, fotografia, quem confirmou e quem denunciou.

**Destinatários**

- Pessoa identificada com ao menos uma Conclusão que abre a página do encontro, por lista ou
  por endereço recebido.
- O próprio organizador.
- A moderação responsável (031 FR-016).

**Fora do alcance**: página sem sessão, que é neutra (031 FR-022); arquivo `.ics`; qualquer
exportação, snapshot ou indicador; busca por pessoa; qualquer lista de organizadores.

**Finalidade.** Dizer a quem decide participar quem propõe e conduz o encontro. O dado não
serve a nenhuma outra tela nem a nenhum outro uso.

**Na direção oposta**: a confirmação de um egresso **não** é mostrada ao organizador nem a
ninguém. O organizador vê só a quantidade (031 FR-025).

**Ciclo**: o organizador vê esses campos na prévia e no termo antes de enviar (031 FR-006).
Pode mudá-los enquanto o encontro está em análise. Depois da publicação, a mudança passa por
nova análise (031 FR-008). Cancelado, recusado, retirado ou encerrado, o encontro sai das
listas. A página continua acessível a quem tem o endereço, e a retenção é D9.

## Consequências

- **Constituição e ADR 0008 não mudam.** O dado continua na camada, fora do dado analítico.
- **O E1 não herda esta decisão.** Diretório e pedido de contato mostram outros dados, a outros
  destinatários e com outra finalidade. Precisam de ADR própria, como prevê a revisão 12.
- **Para uso real, continuam pendentes:**
  - **D9:** base legal da exibição e retenção;
  - **DP-1808:** garantia de identidade do organizador. O nome de apresentação não é
    verificado, e a moderação reduz, mas não elimina, o risco de alguém se passar por outra
    pessoa;
  - **DP-2103:** relação com nome civil e nome social;
  - **D8:** critérios da moderação para o nome de apresentação.
- **Reversão.** Retirar o nome de apresentação, ou os dois campos, não exige migração no
  núcleo. A página passaria a dizer "proposto por um egresso", com a origem ou sem ela.
