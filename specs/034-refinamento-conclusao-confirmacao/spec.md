# Feature Specification: Refinamento visual da conclusão e da confirmação

**Feature Branch**: `claude/034-refinamento-conclusao` (a partir da 033, que mexe na mesma tela)
**Created**: 2026-10-12
**Status**: Revisão 1 **aprovada** pelo solicitante em 2026-10-12, incluindo B1 e B4
ajustadas e B6. Plano, tarefas e implementação na demonstração estão autorizados **depois da
integração da 033 (#69)**, que fica com o solicitante. O PR é aberto para revisão. Merge da
034 e uso real exigem nova autorização. A verificação com leitor de tela pode ficar como
pendência explícita no PR, mas precisa ser concluída antes da aprovação final.
**Input**: Solicitante, 2026-10-12: depois da 033, implementar o refinamento visual das
telas de conclusão e de confirmação, com o protótipo aprovado como referência
([auditoria](../../docs/auditorias/2026-10-12-conclusao-e-confirmacao.md), seção 4;
[protótipo](../../docs/prototipos/2026-10-12-conclusao/)). D1 (revisão recolhida antes do
botão), D2 (apresentação das Seções, "Parte X" mantido) e a simplificação da confirmação
foram aprovadas conceitualmente. D3 e D4 seguem pendentes, sem bloquear. Formulário
mobile-first, na coluna da jornada. Caber numa tela é resultado, não requisito.
Legibilidade, espaçamento e acessibilidade vêm primeiro. Verificar 320 px, fonte a 200%,
teclado e ausência de JavaScript. Sem promessas institucionais novas.

**Revisão 1 (solicitante, 2026-10-12):**
- B1 ajustada: a ficha completa sai da confirmação, mas curso, unidade e ano ficam num
  contexto compacto, com redação de pesquisa já concluída;
- B4 ajustada: a revisão volta recolhida também depois de salvar, com "Parte salva."
  visível;
- acessibilidade: entram uma verificação breve com leitor de tela, ordem coerente nas duas
  colunas, foco sem cortes e testes separados de fonte a 200% e de zoom/refluxo;
- registro da ressalva da 033 sobre o aviso de mudança de caminho (B6).

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
| O curso sozinho pode não distinguir duas formações da mesma Pessoa | 007 (várias formações); `resumo_da_formacao` já combina curso, unidade e ano | A confirmação mantém a identificação compacta (FR-005, B1) |
| O aviso da 033 "Sua resposta mudou o caminho da pesquisa…" também aparece numa parte só de opcionais já vista e deixada em branco, quando o percurso pode não ter mudado | 033 FR-004, FR-006 e edge case "parte já vista e deixada em branco" | Redação neutra proposta (FR-011, B6), sem mudar a regra de destino |

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
   revisão vem **recolhida**, como nos demais casos. O botão fica onde fica com a revisão
   fechada, e ela pode reabrir a lista se quiser revisar outra parte (B4).
5. **Dado** a ficha completa da formação, **então** ela não aparece mais na conclusão.

### US2 — A confirmação registra, agradece com o texto da Versão e leva ao Portal (P1)

**Independent Test:** por requisição, para Ana, Diego e a declarante; medidas e capturas
como na US1.

**Acceptance Scenarios:**

1. **Dado** Ana depois de concluir, **então** vê, nesta ordem:
   - "Pesquisa concluída", com a frase de registro;
   - a identificação compacta da formação, com curso, unidade e ano (texto provisório:
     "Formação: Tecnologia em Análise e Desenvolvimento de Sistemas · Serra · 2022");
   - o texto de encerramento da Versão, literal;
   - o bloco "No Portal do Egresso", com "Ver minha trajetória no Ifes" com aparência de
     ação principal e, abaixo, o convite de e-mail.
2. **Dado** Diego, com outra formação pendente, **então** a próxima formação vem antes do
   bloco do Portal e continua sendo a única ação principal. "Ver minha trajetória no Ifes"
   volta a ter aparência de link.
3. **Dado** a confirmação, **então** a ficha completa da formação (nível, modalidade, data
   completa) não aparece, mas a identificação compacta sim (B1). Ela não usa "Você está
   respondendo". Nenhuma frase de finalidade, uso, contato ou periodicidade é acrescentada.
4. **Dado** a declarante, **então** a confirmação dela é a de hoje.

### US3 — Legível e utilizável em qualquer largura, com teclado, leitor de tela e sem JavaScript (P1)

**Acceptance Scenarios:**

1. **Fonte a 200%** (só o tamanho do texto, a 375 px e a 1280 px): **então**, nas duas telas,
   com a revisão aberta e fechada:
   - todo o conteúdo e toda a função continuam disponíveis;
   - nenhum texto é cortado ou sobreposto;
   - não há rolagem horizontal.

   (WCAG 2.2, 1.4.4.)
2. **Zoom/refluxo** (largura equivalente a 320 CSS px, como 1280 px com zoom de 400%):
   **então**, nas duas telas, o conteúdo reflui numa coluna, sem rolagem em duas dimensões e
   sem perda de conteúdo ou função (WCAG 2.2, 1.4.10). A ausência de rolagem horizontal
   sozinha não basta: a verificação confere também que cada elemento esperado está visível e
   utilizável.
3. **Dado** 1280 px, **então** a coluna é a da jornada. A lista aberta usa duas colunas quando
   couber, e a sequência das partes segue de cima para baixo na primeira coluna e depois na
   segunda, igual à ordem de leitura e de teclado.
4. **Dado** o teclado, **então** a ordem é: resumo da revisão → (aberta) links das partes, em
   ordem numérica → "Concluir pesquisa". O resumo abre e fecha com Enter e Espaço. O foco é
   sempre visível e nunca cortado por borda, divisor ou coluna. O marcador nativo e os alvos
   de 44 px se mantêm.
5. **Leitor de tela** (verificação breve, VoiceOver ou NVDA): **então**:
   - o resumo é anunciado como controle expansível, com o estado aberto ou fechado;
   - cada link diz o título da parte (ou "Parte N"), precedido pelo número lido como texto;
   - "Parte salva." é anunciado ao chegar;
   - na confirmação, título, registro e ação principal são anunciados em ordem.
6. **Dado** JavaScript desligado, **então** tudo funciona igual. Sem suporte a `<details>`, a
   lista aparece aberta.

### Edge Cases

- **Formação sem curso, unidade ou ano:** na conclusão, o contexto compacto mostra o texto
  atual de "dados não informados". Na confirmação, a identificação mostra só os dados
  informados e não aparece quando não há nenhum (a frase de registro já cobre esse caso, 014
  FR-038).
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
- **FR-002**: A revisão DEVE vir recolhida sempre, inclusive na volta de uma revisão com
  "Parte salva." (B4), e abrir sem JavaScript. O resumo DEVE ter o marcador nativo de abrir e
  fechar e alvo de pelo menos 44 px.
- **FR-003**: Cada item da revisão DEVE ter "Parte N" fora do link, em texto discreto, e o
  título da Seção como texto do link. Para Seção sem título, o link diz "Parte N" e não há
  linha de número (023 FR-015). Os títulos são os da Versão (008 FR-033).
- **FR-004**: A partir de ~32 rem de largura útil, a lista aberta PODE usar duas colunas, com
  a sequência de cima para baixo na primeira coluna e depois na segunda, igual à ordem do
  documento (leitura e teclado). Com fonte ampliada ou largura de refluxo, ela DEVE voltar a
  uma coluna antes de criar rolagem horizontal ou cortar conteúdo.

**Confirmação** — revisa a 023 FR-028

- **FR-005**: A confirmação de Participação ancorada em Conclusão Acadêmica DEVE apresentar,
  nesta ordem:
  1. título e frase de registro (014 FR-038);
  2. a identificação compacta da formação, com curso, unidade e ano, quando informados
     (o mesmo resumo das Seções), com redação de pesquisa concluída e sem "Você está
     respondendo" (B1);
  3. texto de encerramento ou agradecimento (014 FR-040);
  4. próxima formação, quando houver (023 FR-011);
  5. o bloco "No Portal do Egresso", com "Ver minha trajetória no Ifes" e o convite de
     e-mail (020).

  A ficha completa da formação (rótulos e valores de curso, unidade, data, nível,
  modalidade e forma de oferta) NÃO DEVE aparecer.
- **FR-006**: "Ver minha trajetória no Ifes" DEVE ter aparência de ação principal quando não
  houver próxima formação, e de link quando houver. A tela tem uma única ação principal.
- **FR-007**: A confirmação da declarada NÃO DEVE mudar.

**Fronteiras**

- **FR-008**: Esta feature NÃO DEVE mudar texto da Versão, título "Pesquisa concluída", frase
  de registro, comportamento da 033, rotas ou dados. Ela NÃO DEVE acrescentar frase de
  finalidade, uso, contato ou periodicidade (014 FR-039), JavaScript, modelo ou migração.
- **FR-009**: A coluna, os tokens e o foco DEVEM ser os da jornada (015). Nenhum token novo.
  O espaçamento em torno do resumo, dos links e do botão DEVE deixar o contorno e o halo do
  foco inteiros (B5).
- **FR-010**: O fechamento DEVE ter, registrado em `validacao.md`:
  - o aviso da B6 verificado nos dois casos: parte nova no percurso e parte só de opcionais
    já visitada e deixada em branco;
  - as garantias da 033, a confirmação da declarada e os textos protegidos da Versão
    preservados;
  - testes por requisição da ordem, da ausência da ficha, da identificação compacta na
    confirmação, da revisão sempre recolhida, da ação principal única e da declarada
    inalterada;
  - capturas e medidas reais, refeitas na implementação (as do protótipo são só
    referência), a 375 px, a 1280 px e com fonte a 200%;
  - um teste de refluxo separado, a 320 CSS px, que confira a presença e o uso de cada
    elemento esperado, além da ausência de rolagem horizontal;
  - um roteiro com teclado (ordem, foco inteiro, Enter e Espaço no resumo);
  - a verificação breve com leitor de tela da US3.5. Se não puder ser executada no ambiente
    de implementação, o fechamento a registra como pendente e o PR diz isso.
- **FR-011**: O aviso da 033 ao levar a uma parte que pede atenção DEVE ter redação neutra,
  verdadeira tanto para uma parte nova no caminho quanto para uma parte só de opcionais já
  vista e deixada em branco (B6). A regra de destino da 033 (FR-004) NÃO DEVE mudar.

## Success Criteria

- **SC-001**: Com fonte a 200% e no refluxo a 320 CSS px, as duas telas, com a revisão
  aberta e fechada, mantêm todo o conteúdo e toda a função, sem corte, sobreposição ou
  rolagem horizontal. As duas verificações são registradas separadamente.
- **SC-002**: A 375×812, "Concluir pesquisa" fica na primeira tela com a revisão fechada.
  Isso é referência, não meta: nenhum espaçamento, tamanho de fonte ou alvo é reduzido para
  cumpri-la.
- **SC-003**: Um h1 por tela; alvos ≥ 44 px; foco visível e inteiro em todo elemento
  interativo; uma única ação principal por tela; ordem visual das partes igual à ordem de
  leitura e de teclado.
- **SC-004**: Os textos protegidos (título, registro, encerramento) estão iguais, e nenhuma
  frase de finalidade aparece. Verificado em teste.
- **SC-005**: A suíte completa passa. Os testes de requisitos revistos são atualizados com
  nota.
- **SC-006**: A verificação com leitor de tela da US3.5 está registrada, executada ou
  declarada pendente.

## Requisitos revisados

| Origem | Revisão |
|---|---|
| 023 FR-027 | Ordem da conclusão (FR-001); revisão recolhida (FR-002); ficha sai |
| 023 FR-028 | Ficha sai da confirmação; trajetória com peso de ação quando não há próxima formação (FR-005, FR-006) |
| 014 FR-041 (revista pela 020 e pela 023) | Inalterada no que permite; só a aparência da ligação da trajetória muda |
| 033 FR-006 (texto do aviso) | Redação neutra (FR-011, B6); a regra de destino não muda |

## Decisões

| # | Decisão | Situação |
|---|---|---|
| B1 | Ficha da formação na confirmação | **Ajustada** (2026-10-12): a ficha completa sai; curso, unidade e ano ficam numa identificação compacta logo depois da frase de registro. Texto provisório: "Formação: curso · unidade · ano" (DP-801) |
| B2 | "Última etapa" acima do título da conclusão | **Aprovada**: discreto e legível, no estilo da linha de parte das Seções |
| B3 | Frase de fim | **Aprovada**: "Você chegou ao fim da pesquisa. Falta só enviar suas respostas." (DP-801), com o aviso de irreversibilidade junto do botão |
| B4 | Revisão na volta de uma revisão | **Ajustada** (2026-10-12): recolhida, com "Parte salva." visível. No protótipo, a 375 px, o botão termina a 666 px fechada e a 1.424 px aberta; a implementação mede de novo |
| B5 | Foco do resumo da revisão | **Aprovada**: o foco comum da jornada, com espaçamento que não corte o contorno nem o halo |
| B6 | Redação do aviso da 033 | **Aprovada** (2026-10-12): "Confira esta parte antes de concluir: ela pode ter perguntas ainda sem resposta." Vale para a parte nova e para a parte só de opcionais já vista e deixada em branco, sem afirmar que o caminho mudou. A regra de destino não muda |

## Decisões Pendentes

- **DP-801:** textos definitivos ("Última etapa", frase de fim, "Formação:", "No Portal do
  Egresso", aviso da B6).
- **D3, D4 (auditoria):** título da Seção 13 e texto de encerramento numa próxima Versão,
  institucionais. Enquanto não forem resolvidas, a lista mostra "Parte 9" e a confirmação
  mostra "Este formulário chegou ao fim!".

## Out of Scope

Regra de destino da revisão (033); qualquer mudança na Versão; resumo de respostas;
composição desktop no estilo do Portal (a jornada continua mobile-first); auditoria
completa com leitor de tela das demais telas (segue no roteiro da versão C; aqui entra só a
verificação breve da US3.5).
