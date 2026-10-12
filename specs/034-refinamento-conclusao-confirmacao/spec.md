# Feature Specification: Refinamento visual da conclusão e da confirmação

**Feature Branch**: `claude/034-refinamento-conclusao` (a partir da 033, que mexe na mesma tela)
**Created**: 2026-10-12
**Status**: Rascunho para aprovação do solicitante. A implementação só começa depois da
aprovação desta spec e das decisões B1 a B5.
**Input**: Solicitante, 2026-10-12: depois da 033, implementar o refinamento visual das
telas de conclusão e de confirmação, com o protótipo aprovado como referência
([auditoria](../../docs/auditorias/2026-10-12-conclusao-e-confirmacao.md), seção 4;
[protótipo](../../docs/prototipos/2026-10-12-conclusao/)). D1 (revisão recolhida antes do
botão), D2 (apresentação das Seções, "Parte X" mantido) e a simplificação da confirmação
foram aprovadas conceitualmente. D3 e D4 seguem pendentes, sem bloquear. Formulário
mobile-first, na coluna da jornada. Caber numa tela é resultado, não requisito.
Legibilidade, espaçamento e acessibilidade vêm primeiro. Verificar 320 px, fonte a 200%,
teclado e ausência de JavaScript. Sem promessas institucionais novas.

## Contexto

| Fato verificado | Fonte | Consequência |
|---|---|---|
| A conclusão de hoje mostra título, aviso, botão, a lista de revisão e, por último, a ficha completa da formação | 023 FR-027; `conclusao.html` | A ordem é revista aqui (FR-001) |
| A ordem atual veio da EF-23: o botão ficava a 1,7 tela, abaixo da ficha de 6 linhas | Auditoria de esforço, 2026-10-05 | O que empurrava o botão era a ficha, não a revisão. A revisão recolhida preserva o ganho |
| As telas de Seção já usam o contexto compacto ("Você está respondendo sobre: curso · unidade · ano") | `contexto_compacto.html`; 014 | Mesmo componente no topo da conclusão |
| A 033 acrescentou o marcador nos links da revisão e "Parte salva." na volta | [033](../033-retorno-revisao-conclusao/spec.md) FR-001, FR-007 | Os dois continuam valendo |
| A confirmação já mostra a navegação do Portal, com "Participação" atual | 024; 032 FR-011 | Não é preciso link novo "Voltar ao Portal" |
| A folha comum já tem `.botao` (link com aparência de botão) e `details.abertura` (recolhido sem JavaScript) | `estilo.css`; `jornada.css` (023 FR-025) | Nada novo de padrão visual; só composição |
| O título "Pesquisa concluída", a frase de registro e o texto de encerramento literal são requisitos | 014 FR-038, FR-040 | Não mudam |
| A confirmação não pode afirmar finalidade, uso futuro, contato ou periodicidade | 014 FR-039; DP-504 | Nenhuma frase nova desse tipo |
| A Seção 13 da Versão de 2024 não tem título | Inventário, E-11; auditoria D2 | Continua "Parte 9" (023 FR-015) |

## User Scenarios & Testing

Ana (TADS, Serra, 2022), percurso "trabalha e estuda", 9 partes. Diego, para a confirmação
com outra formação pendente. Uma declarante, para a confirmação da declarada.

### US1 — A conclusão contextualiza, oferece revisão e pede a decisão por último (P1)

**Independent Test:** por requisição, a ordem e os elementos da tela. Medidas e capturas a
375 px, 320 px, 375 px com fonte a 200% e 1280 px. Roteiro com teclado.

**Acceptance Scenarios:**

1. **Dado** Ana com a jornada finalizada, **quando** abre a conclusão, **então** vê, nesta
   ordem:
   - "Última etapa";
   - o título "Concluir a pesquisa";
   - "Você chegou ao fim da pesquisa. Falta só enviar suas respostas.";
   - o contexto compacto da formação;
   - "Revisar respostas antes de enviar · 9 partes", recolhido;
   - o aviso "Depois de concluída, a pesquisa não poderá ser alterada.", junto do botão;
   - "Concluir pesquisa".
2. **Dado** a revisão recolhida, **quando** Ana a abre (toque, Enter ou Espaço), **então** vê
   "Ao abrir uma parte, suas respostas aparecem como você deixou." e a lista: "Parte N" em
   texto discreto e o título da Seção como link, que abre a parte em revisão (033).
3. **Dado** a Parte 9, sem título na Versão, **então** o link diz "Parte 9", sem número
   repetido nem trecho de Pergunta.
4. **Dado** Ana voltando de uma revisão (033), **então** "Parte salva." aparece no topo e a
   revisão vem **aberta**, para ela conferir outra parte se quiser.
5. **Dado** a ficha completa da formação, **então** ela não aparece mais na conclusão.

### US2 — A confirmação registra, agradece com o texto da Versão e leva ao Portal (P1)

**Independent Test:** por requisição, para Ana, Diego e a declarante; medidas e capturas
como na US1.

**Acceptance Scenarios:**

1. **Dado** Ana depois de concluir, **então** vê, nesta ordem:
   - "Pesquisa concluída", com a frase de registro;
   - o texto de encerramento da Versão, literal;
   - o bloco "No Portal do Egresso", com "Ver minha trajetória no Ifes" com aparência de
     ação principal e, abaixo, o convite de e-mail.
2. **Dado** Diego, com outra formação pendente, **então** a próxima formação vem antes do
   bloco do Portal e continua sendo a única ação principal. "Ver minha trajetória no Ifes"
   volta a ter aparência de link.
3. **Dado** a confirmação, **então** a ficha completa da formação não aparece (B1), e nenhuma
   frase de finalidade, uso, contato ou periodicidade é acrescentada.
4. **Dado** a declarante, **então** a confirmação dela é a de hoje.

### US3 — Legível e utilizável em qualquer largura, com teclado e sem JavaScript (P1)

**Acceptance Scenarios:**

1. **Dado** 320 px, 375 px e 375 px com fonte a 200%, **então** nenhuma das duas telas tem
   rolagem horizontal, com a revisão aberta ou fechada.
2. **Dado** 1280 px, **então** a coluna é a da jornada, e a lista aberta usa duas colunas
   quando couber, voltando a uma quando a fonte cresce.
3. **Dado** o teclado, **então** a ordem é: resumo da revisão → (aberta) links das partes →
   "Concluir pesquisa". O resumo abre e fecha com Enter e Espaço, e o foco é sempre visível.
4. **Dado** JavaScript desligado, **então** tudo funciona igual. Sem suporte a `<details>`, a
   lista aparece aberta.

### Edge Cases

- **Formação sem curso, unidade ou ano:** o contexto compacto mostra o texto atual de "dados
  não informados".
- **Percurso com uma única parte** (Termos "Não"): o resumo diz "· 1 parte".
- **Declarada na conclusão:** o contexto compacto usa o rótulo da formação informada, como nas
  Seções.
- **Confirmação sem texto de encerramento na Versão:** o agradecimento fixo aparece uma vez
  (014 FR-040), antes do bloco do Portal.

## Requirements

**Conclusão** — revisa a 023 FR-027

- **FR-001**: A conclusão DEVE apresentar, nesta ordem:
  1. a confirmação "Parte salva." (033 FR-007), quando houver;
  2. "Última etapa";
  3. o título;
  4. a frase de fim;
  5. o contexto compacto da formação;
  6. a revisão recolhida com a contagem de partes;
  7. o aviso de irreversibilidade;
  8. o botão "Concluir pesquisa".

  A ficha completa da formação NÃO DEVE aparecer.
- **FR-002**: A revisão DEVE ser recolhida por padrão, sem JavaScript. Ela DEVE vir aberta
  quando a pessoa chega pela volta de uma revisão com "Parte salva." (B4). O resumo DEVE ter
  o marcador nativo de abrir e fechar e alvo de pelo menos 44 px.
- **FR-003**: Cada item da revisão DEVE ter "Parte N" fora do link, em texto discreto, e o
  título da Seção como texto do link. Para Seção sem título, o link diz "Parte N" e não há
  linha de número (023 FR-015). Os títulos são os da Versão (008 FR-033).
- **FR-004**: A partir de ~32 rem de largura útil, a lista aberta PODE usar duas colunas. Com
  fonte ampliada, ela DEVE voltar a uma coluna antes de criar rolagem horizontal.

**Confirmação** — revisa a 023 FR-028

- **FR-005**: A confirmação de Participação ancorada em Conclusão Acadêmica DEVE apresentar,
  nesta ordem:
  1. título e frase de registro (014 FR-038);
  2. texto de encerramento ou agradecimento (014 FR-040);
  3. próxima formação, quando houver (023 FR-011);
  4. o bloco "No Portal do Egresso", com "Ver minha trajetória no Ifes" e o convite de
     e-mail (020).

  A ficha completa da formação NÃO DEVE aparecer (B1).
- **FR-006**: "Ver minha trajetória no Ifes" DEVE ter aparência de ação principal quando não
  houver próxima formação, e de link quando houver. A tela tem uma única ação principal.
- **FR-007**: A confirmação da declarada NÃO DEVE mudar.

**Fronteiras**

- **FR-008**: Esta feature NÃO DEVE mudar texto da Versão, título "Pesquisa concluída", frase
  de registro, comportamento da 033, rotas ou dados. Ela NÃO DEVE acrescentar frase de
  finalidade, uso, contato ou periodicidade (014 FR-039), JavaScript, modelo ou migração.
- **FR-009**: A coluna, os tokens e o foco DEVEM ser os da jornada (015). Nenhum token novo.
- **FR-010**: O fechamento DEVE ter:
  - testes por requisição da ordem, da ausência da ficha, da revisão aberta só na volta, da
    ação principal única e da declarada inalterada;
  - capturas e medidas reais a 375, 320, 375 com fonte a 200% e 1280 px;
  - um roteiro com teclado registrado em `validacao.md`.

## Success Criteria

- **SC-001**: Sem rolagem horizontal nas duas telas, de 320 a 1280 px, com fonte a 100% e
  200%, com a revisão aberta e fechada.
- **SC-002**: A 375×812, "Concluir pesquisa" fica na primeira tela com a revisão fechada.
  Isso é referência, não meta: nenhum espaçamento, tamanho de fonte ou alvo é reduzido para
  cumpri-la.
- **SC-003**: Um h1 por tela; alvos ≥ 44 px; foco visível em todo elemento interativo; uma
  única ação principal por tela.
- **SC-004**: Os textos protegidos (título, registro, encerramento) estão iguais, e nenhuma
  frase de finalidade aparece. Verificado em teste.
- **SC-005**: A suíte completa passa. Os testes de requisitos revistos são atualizados com
  nota.

## Requisitos revisados

| Origem | Revisão |
|---|---|
| 023 FR-027 | Ordem da conclusão (FR-001); revisão recolhida (FR-002); ficha sai |
| 023 FR-028 | Ficha sai da confirmação; trajetória com peso de ação quando não há próxima formação (FR-005, FR-006) |
| 014 FR-041 (revista pela 020 e pela 023) | Inalterada no que permite; só a aparência da ligação da trajetória muda |

## Decisões para aprovação

| # | Decisão | Proposta |
|---|---|---|
| B1 | Ficha da formação na confirmação | **Retirar.** O curso já está na frase de registro, e a navegação do Portal leva à trajetória. Alternativa conservadora: contexto compacto no fim |
| B2 | "Última etapa" acima do título da conclusão | Manter, no estilo discreto da linha de parte das Seções |
| B3 | Frase de fim | "Você chegou ao fim da pesquisa. Falta só enviar suas respostas." (DP-801) |
| B4 | Revisão aberta na volta de uma revisão | Sim: abrir quando houver "Parte salva."; fechada nos demais casos |
| B5 | Foco do resumo da revisão | Manter o foco comum da jornada (contorno escuro com halo amarelo), como em todo elemento interativo (015). Integrar visualmente pela posição e pelo espaçamento, não trocando o indicador |

## Decisões Pendentes

- **DP-801:** textos definitivos ("Última etapa", frase de fim, "No Portal do Egresso").
- **D3, D4 (auditoria):** título da Seção 13 e texto de encerramento numa próxima Versão,
  institucionais. Enquanto não forem resolvidas, a lista mostra "Parte 9" e a confirmação
  mostra "Este formulário chegou ao fim!".

## Out of Scope

Comportamento da revisão (033); qualquer mudança na Versão; resumo de respostas;
composição desktop no estilo do Portal (a jornada continua mobile-first); leitor de tela
(segue no roteiro da versão C).
