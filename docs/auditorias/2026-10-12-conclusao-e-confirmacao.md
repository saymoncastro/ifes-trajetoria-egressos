# Auditoria das telas de conclusão e confirmação da pesquisa

Data: 2026-10-12 · Base: `main` em `1d6935f` (PR #67 integrado) · Revisão 2 (mesmo dia),
depois da avaliação das decisões pelo solicitante

Esta auditoria responde a uma avaliação de UX da tela "Concluir a pesquisa". A avaliação
propõe organizar o encerramento em contextualização, revisão e envio, e tornar a confirmação
mais acolhedora e ligada ao Portal. Antes de qualquer mudança, cada ponto foi confrontado com
os requisitos vigentes e com o código, e o desenho proposto cabe nas regras atuais. **Nada
foi implementado.** O protótipo é estático e não é importado pela aplicação.

- **Telas:** `/participacoes/<id>/concluir/` ([conclusao.html](../../trajetoria/interface/templates/interface/conclusao.html))
  e `/participacoes/<id>/concluida/` ([concluida.html](../../trajetoria/interface/templates/interface/concluida.html)).
- **Cenário:** Ana (TADS, Serra, 2022), percurso "trabalha e estuda", 9 partes.
- **Protótipo e medidas:** [`docs/prototipos/2026-10-12-conclusao/`](../prototipos/2026-10-12-conclusao/).
  `gerar.py` produz as telas com o shell e as folhas reais da jornada; `capturar.py` captura
  e mede a 375 px, a 320 px, a 375 px com fonte a 200% e a 1280 px (`capturas/`,
  `medidas.json`).

## 1. Resultado em uma frase

**O principal achado é funcional, não visual: quem revisa uma parte a partir da conclusão
precisa refazer, envio por envio, todas as partes seguintes (D5).** A avaliação de UX acerta
no diagnóstico visual (contexto no fim, "Parte 9", lista que parece estrutura interna,
confirmação seca), mas três das suas propostas colidem com requisitos vigentes. O protótipo
atende ao essencial sem modelo, sem JavaScript e sem mudar o instrumento.

## 2. O que os requisitos determinam hoje

| Requisito | O que determina | Origem |
|---|---|---|
| 023 FR-027 | Conclusão, nesta ordem: título; frase de fim com o aviso de irreversibilidade; botão; convite a revisar com a lista de Seções; contexto da formação | EF-23: o botão ficava abaixo de 6 linhas de contexto, a 1,7 tela |
| 023 FR-015 | Seção sem título vira "Parte X" na lista de revisão; nunca "Seção {posição}" | UX-11 |
| 023 FR-013 | Toda Seção mostra "Parte X · faltam no máximo N partes" | EF-07 |
| 014 FR-038 | A confirmação mantém o título "Pesquisa concluída" e diz que as respostas sobre o curso foram registradas | ID-09 |
| 014 FR-039 | A confirmação **não** afirma finalidade, uso futuro, novo contato ou periodicidade | Const. IX; DP-504 |
| 014 FR-040 | Havendo texto de encerramento na Versão, ele é o agradecimento, exibido exatamente como na Versão | UX-18 |
| 023 FR-028 | Confirmação: registro; encerramento; próxima formação; "Ver minha trajetória no Ifes"; convite de e-mail; contexto | EF-26 |
| 014 FR-011, FR-012 | "Salvar e sair" com a mesma validação e gravação de "Salvar e continuar"; só o destino muda | — |
| 006 FR-014 | O próximo passo é o que o percurso determina com as Respostas gravadas | — |
| 023 FR-033 a FR-035 | Não mudar o instrumento, não criar modelo, não acrescentar JavaScript | Const. XIII, XXII; 008 FR-080 |
| 008 FR-033 | Textos do instrumento exibidos como na Versão | Const. VIII |

## 3. Ponto a ponto

| # | Ponto da avaliação | Veredito | Por quê |
|---|---|---|---|
| 1 | O botão aparece cedo demais | **Em conflito com a 023 FR-027**, mas resolvível | A ordem atual é deliberada: na auditoria de esforço, a ação ficava a 1,7 tela. O que empurrava o botão era a ficha de 6 linhas, não a ideia de revisar antes. Com a revisão **recolhida** (`<details>`, nativo, sem JavaScript), a ordem lógica volta e o botão fica a 666 px a 375 px |
| 2 | A lista parece estrutura interna | **Parcial** | "Egresso que trabalha", "Estudo" e "Egresso que estuda" são títulos da própria Versão de 2024, exibidos literalmente (008 FR-033). A apresentação pode melhorar (número da parte, divisores, duas colunas no desktop). Renomear exige nova Versão |
| 3 | "Parte 9" não comunica nada | **Confirmado; a correção é institucional** | É a Seção 13 do original, sem título no PDF (inventário, E-11). A ID-13 já pedia um título na próxima Versão. Ver D2 e D3 |
| 4 | O cartão de formação está deslocado | **Confirmado** | A ficha completa vem por último (FR-027). As telas de Seção já usam o contexto compacto ("Você está respondendo sobre: curso · unidade · ano"); reusá-lo no topo contextualiza em 2 linhas |
| 5 | A página desperdiça espaço no desktop | **Discordo da solução** | A coluna de 40 rem é a da jornada inteira (015; Const. XXI), e a própria avaliação mantém o formulário mobile-first. O vazio vem da lista empilhada com alvos de 44 px. No desktop, só a revisão aberta passa a usar duas colunas dentro da mesma coluna |
| 6 | "Sua participação ajuda o Ifes a conhecer… e aprimorar suas ações" | **Em conflito com a 014 FR-039** | Afirma finalidade e uso futuro. Depende da DP-504 (institucional) |
| 7 | Título "Obrigado por compartilhar sua trajetória!" | **Em conflito com a 014 FR-038** | O título "Pesquisa concluída" é requisito. O agradecimento já existe: é o texto de encerramento da Versão (FR-040) |
| 8 | "Voltar ao Portal do Egresso" depois de concluir | **Já existe em parte** | Desde a 024/032, a confirmação mostra a navegação do Portal, com "Participação" atual. Falta dar peso de ação a "Ver minha trajetória no Ifes", que hoje é um link comum |
| 9 | Voltar preserva as respostas? Os rótulos vêm da Versão da participação? | **Sim, nos dois** | A lista vem de `jornada.passagens` (o percurso atual da 006) e os títulos de `participacao.campanha.versao`. As Respostas gravadas reaparecem preenchidas |

### Achado principal: revisar custa refazer o caminho (D5)

A avaliação parte da premissa de que "a revisão pode continuar acontecendo nas seções
originais". Ela acontece, mas **não volta para a conclusão**. Ao abrir a Parte 2 e enviar, a
pessoa segue para a Parte 3 e passa de novo por todas as partes seguintes até chegar à
conclusão ([views.py, `_salvar`](../../trajetoria/interface/views.py)). As respostas estão
preenchidas, mas, no percurso de Ana, corrigir uma resposta da Parte 1 custa 8 envios a
mais. A tela de conclusão de hoje não avisa isso. É o maior custo evitável do encerramento,
maior que a posição do botão. A proposta para uma spec própria está na seção 6.

### Achado secundário: o encerramento da Versão repete o título

Na confirmação, depois de "Pesquisa concluída", aparece "Este formulário chegou ao fim!",
primeira frase do texto de encerramento da Versão de 2024 (Seção 14 do original, E-04). A
interface exibe o texto como está (FR-040) e assim continua. Ajustar a frase é decisão
institucional para uma próxima Versão (D4).

## 4. Proposta visual (protótipo)

### Conclusão

1. "Última etapa", discreto, no lugar da linha de parte das Seções; título "Concluir a
   pesquisa".
2. "Você chegou ao fim da pesquisa. Falta só enviar suas respostas."
3. Contexto compacto da formação, o mesmo componente das Seções.
4. **"Revisar respostas antes de enviar · 9 partes"**, recolhido. Aberto, mostra "Ao abrir
   uma parte, suas respostas aparecem como você deixou." e a lista: "Parte 1" em texto
   discreto e o título da Seção como link. Passa a duas colunas a partir de ~32 rem e volta a
   uma coluna quando a fonte cresce.
5. Aviso de irreversibilidade **junto do botão**, no momento da decisão: "Depois de
   concluída, a pesquisa não poderá ser alterada." → **Concluir pesquisa**.

Não há "Voltar à pesquisa": a revisão já é a volta, e um segundo botão competiria com o
envio.

### Confirmação

1. "Pesquisa concluída" com a frase de registro (014 FR-038, sem mudança).
2. Texto de encerramento da Versão (FR-040, sem mudança).
3. Próxima formação, quando houver (023 FR-011, sem mudança; continua sendo a ação principal).
4. Bloco **"No Portal do Egresso"**: "Ver minha trajetória no Ifes" com aparência de ação
   principal e, abaixo, o convite de e-mail, secundário. Com uma próxima formação na tela, a
   trajetória volta a ser link, para haver uma única ação principal.
5. A ficha completa da formação sai: o curso já está na frase de registro, e a navegação do
   Portal leva ao resto. Alternativa conservadora: contexto compacto no fim.
6. Nenhuma frase nova de finalidade, uso ou contato (014 FR-039).
7. A declarada não muda (sem Portal; "Ver suas formações informadas").

### Medidas

Sem a faixa "Protótipo". A primeira tela de referência tem 812 px. **Caber numa tela é um
resultado, não um requisito:** legibilidade, espaçamento e alvos de 44 px vêm antes de
evitar rolagem.

| Tela | 375 px: ação / conteúdo | 320 px: ação / conteúdo | 375 px, fonte 200%: ação / conteúdo | Rolagem horizontal |
|---|---:|---:|---:|---|
| Conclusão, hoje | 409 / 1.312 | 448 / 1.375 | 1.331 / 3.425 | não |
| Conclusão, proposta (recolhida) | 666 / 714 | 729 / 777 | 2.178 / 2.274 | não |
| Conclusão, proposta (aberta) | 1.424 / 1.472 | 1.487 / 1.535 | 3.370 / 3.466 | não |
| Confirmação, hoje | 595 / 1.064 | 717 / 1.208 | 2.056 / 3.229 | não |
| Confirmação, proposta | 694 / 789 | 816 / 933 | 2.344 / 2.578 | não |

Leitura: o botão desce, mas continua na primeira tela a 375 e a 320 px. Com a fonte a 200%,
ele fica mais abaixo do que hoje (2.178 contra 1.331 px), porque agora vem depois do contexto
e da revisão. Em troca, a página encolhe um terço e o aviso fica colado ao botão. Na primeira
versão do protótipo, a lista em duas colunas gerava rolagem horizontal com fonte a 200%
(coluna mínima de 15 rem). Foi corrigida com `minmax(min(15rem, 100%), 1fr)`.

### Acessibilidade e ausência de JavaScript

- **Sem JavaScript:** `<details>`/`<summary>` são nativos, e nenhuma tela do protótipo tem
  script. Sem suporte a `<details>`, a lista aparece aberta.
- **Teclado** (navegador do app): a ordem de Tab é "Pular para o conteúdo" → "Sair" →
  resumo da revisão → (aberta) links das partes → "Concluir pesquisa". Enter e Espaço abrem e
  fecham o resumo. O foco visível é o da folha comum (contorno e halo amarelo).
- **Evidência:** o resumo tem marcador nativo (▸/▾), cor de ação, peso médio, divisores
  acima e abaixo e a contagem "· 9 partes". Na implementação, o marcador nativo deve ser
  mantido (`display: flex` no `summary` o remove, como em `details.abertura`).
- **Nome acessível dos links:** na primeira versão, "Parte 1" ficava dentro do link e o nome
  saía colado ("Parte 1Termos e condições"). O número saiu do link: o nome é só o título da
  Seção.
- **Não verificado:** leitor de tela (VoiceOver/NVDA). Fica para o roteiro de leitor de tela
  da versão C (PR #63), no fechamento da implementação.

## 5. Matriz de rastreabilidade

Legenda: **Preservado** (o requisito vale como está), **Revisão** (a mudança exige revisar o
requisito na spec da entrega), **Novo** (comportamento que hoje não existe).

| Mudança proposta | Requisito vigente | Situação |
|---|---|---|
| Revisão recolhida antes do botão; aviso junto do botão | 023 FR-027 (ordem) | **Revisão** |
| Contexto compacto no topo da conclusão, no lugar da ficha no fim | 023 FR-027 (contexto por último) | **Revisão** |
| "Última etapa" acima do título da conclusão | 023 FR-013 (só Seções) | Preservado (não é Seção) |
| Lista com "Parte X" fora do link e título como link | 023 FR-015; 008 FR-033 | Preservado |
| Seção sem título continua "Parte 9" | 023 FR-015 | Preservado |
| Títulos das Seções sem alteração | 008 FR-033; 023 FR-033 | Preservado |
| Irreversibilidade dita antes do envio | 006 (Participação concluída não reabre) | Preservado |
| Título "Pesquisa concluída" e frase de registro | 014 FR-038 | Preservado |
| Nenhuma frase de finalidade ou uso | 014 FR-039 | Preservado |
| Texto de encerramento literal | 014 FR-040; 008 FR-033 | Preservado |
| Próxima formação antes das demais ações | 023 FR-011, FR-028 | Preservado |
| "Ver minha trajetória" com peso de ação principal | 023 FR-028; 021 FR-003 | Preservado (muda o estilo, não a ordem) |
| Ficha completa da formação sai da confirmação | 023 FR-028 (contexto por último) | **Revisão** |
| Declarada sem mudança | 019; 023 FR-028 | Preservado |
| Sem modelo, migração, rota ou JavaScript | 023 FR-034, FR-035 | Preservado |
| Voltar direto à conclusão depois de revisar (D5) | 006 FR-014; 014 FR-011, FR-012; 023 FR-013 | **Novo** (spec própria) |

## 6. D5 — Retorno à conclusão depois de revisar (proposta para spec própria)

**Problema.** Na conclusão, a pessoa abre uma parte, corrige e envia. Hoje ela segue para a
parte seguinte e precisa enviar de novo todas as partes até a conclusão.

**Condições** (do solicitante):

1. O preenchimento normal não muda.
2. O retorno direto só acontece quando a participação continua apta à conclusão, pelas
   validações existentes.
3. Nenhuma etapa obrigatória ou validação é contornada.

**Solução proposta, sem estado novo:**

- Os links da revisão levam à Seção com um marcador de origem no endereço (por exemplo,
  `secoes/2/?revisao=1`). A Seção aberta assim leva o marcador num campo oculto do
  formulário, e o botão principal diz **"Salvar e voltar à conclusão"**. Sem marcador, a
  Seção é exatamente a de hoje (condição 1).
- O envio passa pelas mesmas etapas de hoje: forma → gravação da 005 → percurso da 006. Só o
  destino muda, como já acontece com "Salvar e sair" (014 FR-011, FR-012). Erro de forma ou
  pendência reapresenta a Seção, como hoje (condição 3).
- Depois de gravar, o percurso é recalculado. O retorno direto só acontece se **as duas**
  condições valerem:
  - a jornada continua finalizada (`jornada.finalizada`, 006);
  - o percurso novo não tem Seção que não estava no percurso de antes do envio. Os dois
    percursos são conhecidos na própria requisição, sem guardar nada.

  Se alguma falhar (por exemplo, a resposta de "Você trabalha?" mudou e "Egresso que
  trabalha" entrou no caminho), vale o fluxo normal, que leva à próxima Seção (condição 2).
- A segunda condição existe porque o percurso da 006 avança sozinho por Seções sem
  obrigatórias pendentes. Uma Seção nova só com Perguntas opcionais deixaria a jornada
  "finalizada" sem que a pessoa a tivesse visto. Com a condição, ela é apresentada.
- A tela de conclusão continua validando tudo no GET e no POST (`concluir_view` e
  `concluir` da 006). O marcador não autoriza nada. Um marcador forjado no preenchimento
  normal não pula nenhuma etapa: sem as duas condições, o destino é o de hoje. Para que elas
  valham, todo o percurso já precisa estar respondido, e esse é justamente o caso da revisão.

**Perguntas para a spec:**

- Linha da parte em modo revisão: manter "Parte 2 · faltam no máximo 7 partes" (FR-013) ou
  trocar por "Revisando a parte 2 · depois de salvar, você volta à conclusão"?
- "Voltar à seção anterior" em modo revisão: manter ou trocar por "Voltar à conclusão sem
  salvar"?
- "Salvar e sair" em modo revisão: manter, como hoje.
- Envio pendente restaurado depois de a sessão expirar (023 FR-002 a FR-009): o marcador
  pode se perder. A proposta aceita voltar ao fluxo normal nesse caso.
- Testes por requisição: retorno direto com percurso igual; fluxo normal quando entra Seção
  nova (com e sem obrigatórias); erro de forma em modo revisão; marcador forjado no
  preenchimento normal; Seção sem marcador idêntica à de hoje.

**Fora da proposta:** salvar várias partes de uma vez, resumo de respostas, edição na
própria tela de conclusão, qualquer mudança na Versão.

## 7. Decisões

| # | Decisão | Natureza | Situação |
|---|---|---|---|
| D1 | Revisão recolhida antes do botão (revisa a FR-027) | Produto | **Aprovada conceitualmente** (2026-10-12), com validação de acessibilidade, teclado, ausência de JavaScript e larguras menores (seção 4) |
| D2 | Apresentação das Seções na revisão, sem mudar o instrumento; "Parte X" mantido para Seção sem título | Produto | **Aprovada com ressalva** (2026-10-12). A opção de usar o trecho da primeira Pergunta foi **descartada**: o enunciado literal da Q52 começa por "Indique o seu grau de concordância com a afirmação…", igual ao de outras Perguntas de escala, e não identifica a parte. Extrair só a afirmação seria editar o texto da Versão. Além disso, a Q52 cobre só uma das três afirmações da Seção (vida, situação econômica da família, exemplo para outras pessoas) |
| D3 | Título da Seção 13 numa próxima Versão (a ID-13 sugere "Impactos da formação") | **DECISÃO PENDENTE** institucional | Mantida pendente; não bloqueia D1, D2 nem D5 |
| D4 | Texto de encerramento de uma próxima Versão sem "Este formulário chegou ao fim!" | **DECISÃO PENDENTE** institucional | Mantida pendente; o texto vigente segue literal |
| D5 | Retorno direto à conclusão depois de revisar (seção 6) | Produto (comportamento) | **Priorizada** (2026-10-12): spec própria, antes do refinamento visual |
| D6 | Frase de finalidade na confirmação | Depende da DP-504 | Não usar |

## 8. Sequência

1. **Este PR, só documentos:** auditoria, protótipo, medidas e decisões.
2. **D5:** spec curta, plano, tarefas e implementação do retorno à conclusão, numa entrega
   própria.
3. **Refinamento visual** da conclusão e da confirmação (D1, D2 e seção 4), de preferência
   com a D5 já integrada, em outra entrega, com capturas a 375×812 e 320 px e fonte a 200% no
   fechamento.

D3 e D4 seguem como pendências de uma próxima Versão e não bloqueiam nenhuma das entregas.
