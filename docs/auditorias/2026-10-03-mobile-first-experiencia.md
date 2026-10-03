# Auditoria mobile-first da experiência de resposta

Data: 2026-10-03 · Base: `main` em `fc39510` (após a auditoria de identidade, PR #19)

Nada foi implementado; este documento é só o diagnóstico. É a terceira lente de UX do
projeto e não substitui as anteriores:

1. [usabilidade da Feature 008](2026-10-01-ux-feature-008.md) (parcialmente corrigida
   pelo polish `226ca93`);
2. [identidade da experiência](2026-10-02-identidade-da-experiencia.md);
3. esta: **a jornada funciona excepcionalmente bem para um egresso que abre a pesquisa no
   celular, responde em condições reais, pode ser interrompido e precisa continuar
   depois?**

**Convenções.** Cada teste ou achado tem um **nível de evidência**: **[A]** observado em
execução real; **[B]** simulado/aproximado; **[C]** inspeção de código, DOM ou CSS;
**[D]** não testável no ambiente atual. E um **pertencimento**: **[I]** interface atual;
**[V]** exige mudança da Versão do instrumento; **[Dec]** depende de decisão pendente
(escrito "Dec" para não confundir com o nível [D]); **[T]** precisa de validação em
aparelho real. Prioridade: **P0** bloqueia ou compromete seriamente o uso no celular;
**P1** ganho relevante; **P2** refinamento.

## 1. Resumo executivo

- **O que já é sólido no celular.** Não há rolagem horizontal de 320 a 430 px, nem com
  fonte a 200%. Campos com fonte de 16 px (o iOS não amplia a página ao focar). Zoom por
  pinça permitido. Nenhum elemento fixo que o teclado possa esconder. E, sobretudo, o
  **servidor é robusto a rede ruim**: toques duplos, reenvio automático do navegador e
  resposta perdida depois de gravar não geraram nenhuma duplicidade nem perda do que
  chegou ao servidor (verificado no banco) [A].
- **O que impede chamar a experiência de mobile-first é um único problema, comprovado:**
  o único ponto de persistência é o botão no fim da Seção. Recarregar a página ou abrir o
  endereço de novo **descarta em silêncio tudo o que foi marcado na Seção** [A]. Nas
  Seções "Avaliação" (14 perguntas) e "Egresso que trabalha" (11), o botão fica a mais de
  5 telas do topo num celular de 375×667 e a mais de 6 telas em 320×568. O sistema
  **já salva Seções incompletas** quando a pessoa toca em "Salvar e continuar", mas
  ninguém diz isso, e o resultado aparece como "Há problemas nesta seção" (MF-01).
- **Cinco fricções relevantes, todas pequenas de corrigir:** Enter/"Ir" num campo de
  texto envia a Seção inteira (MF-02); voltar pelo histórico pode reapresentar e regravar
  respostas antigas (MF-03); a área realmente tocável das opções e da escala é menor do
  que parece (MF-04); a escala 1–5 quebra em "4 + 1" com fonte do sistema só 15% maior
  (MF-05); "Voltar à seção anterior", que descarta o que não foi salvo, fica a 19 px do
  botão principal (MF-06).
- **Nada aqui pede arquitetura nova.** Os achados [I] se resolvem em CSS, template e
  texto. Nenhum exige JavaScript, autosave, PWA ou service worker. O tamanho das Seções
  longas é [V] e fica como evidência para a revisão do instrumento.

## 2. Escopo e limites

**Auditado:** ergonomia em telas estreitas, uso com uma mão, alvos de toque, rolagem e
comprimento dos blocos, os quatro controles (rádio, caixas, escala, lista suspensa),
campos de texto, erros e validação, "Salvar e continuar", "Voltar", "Sair", Voltar do
navegador, recarregar, interrupção e retomada, rede lenta ou perdida durante o envio,
teclado virtual (simulado), fonte ampliada, zoom, orientação horizontal, foco e semântica.

**Fora do escopo (não avaliado como solução):** abertura por WhatsApp ou e-mail
(004/DP-406), métricas de abandono (DP-803), retrato, cópia ou compartilhamento das
respostas (DP-802), identidade visual e linguagem definitivas (DP-801). Também não se
propõe reordenar, dividir ou criar Seções, alterar Perguntas, wizard, uma pergunta por
tela, progresso percentual, estimativa de tempo ou telas de respiro.

**Limite importante do ambiente:** não há aparelho físico, simulador iOS (sem Xcode) nem
emulador Android nesta máquina. Tudo o que depende de teclado real, leitor de tela real,
descarte de aba pelo sistema ou navegador embutido está marcado [B], [C] ou [D], com o
roteiro de validação na seção 15.

## 3. Método e ambientes utilizados

- **Aplicação real**, banco local dedicado `trajetoria_mobile`, preparado com
  `preparar_demonstracao` e servido com `TRAJETORIA_DEMONSTRACAO=1`; só dados fictícios.
- **Navegador:** o painel de navegador do aplicativo Claude (motor Chromium), com
  emulação de viewport; abaixo de 768 px ele também emula agente de usuário Android e
  toque. Os cliques da ferramenta são eventos de ponteiro precisos, **não toques com dedo**:
  o "ajuste de toque" do Chrome Android, que aproxima um toque impreciso do alvo mais
  próximo, não foi exercitado.
- **Medições:** posições e tamanhos lidos do DOM (`getBoundingClientRect`) em cada tela;
  persistência conferida direto no banco (`participacao_resposta`).
- **Rede:** um proxy local de teste, fora do repositório (diretório temporário da
  sessão), entre o navegador e o servidor, com quatro modos aplicados só a POST: atraso
  antes de encaminhar, atraso da resposta, queda antes de chegar ao servidor e queda
  depois de o servidor gravar.
- **Teclado virtual:** simulado reduzindo a altura útil para 376 px (375×667 menos um
  teclado de cerca de 291 px) e focando os campos. Enter testado com teclado físico.
- **Fonte ampliada:** simulada alterando o tamanho da fonte raiz (115%, 130%, 150%,
  175%, 200%). Aproxima a escala de fonte do Android e o zoom de página; não equivale ao
  "Texto Dinâmico" do iOS, que não afeta páginas com fonte em `rem`.

## 4. Matriz de dispositivos/viewports e nível de evidência

| Viewport (CSS px) | Equivale a | Usado para | Evidência |
|---|---|---|---|
| 320×568 | iPhone SE 1ª geração, Android compacto | Seção longa, fonte ampliada, resumo de erros | [B] |
| 360×640 | Android de entrada | Seção longa, escala com fonte ampliada | [B] |
| 375×667 | iPhone SE 2ª/3ª geração | **Jornada completa** de todas as pessoas, rede, erros, alvos | [B] para layout; [A] para comportamento do servidor e do histórico |
| 375×376 | 375×667 com teclado aberto | Visibilidade de rótulo e campo | [B] |
| 390×844 | iPhone 12–15 | Seção longa, fonte ampliada | [B] |
| 412×915 | Pixel, Galaxy | Seção longa | [B] |
| 430×932 | iPhone Pro Max | Seção longa | [B] |
| 667×375 | 375×667 na horizontal | Primeira tela de Seção | [B] |
| 768×1024, 1280×900 | Tablet, desktop | Regressão (sem rolagem horizontal) | [B] |
| iOS Safari, Chrome Android, aparelho físico, VoiceOver, TalkBack, navegador do WhatsApp | — | — | [D] |

O comportamento do **servidor** (o que é gravado, redirecionamentos, idempotência) e do
**histórico do Chromium** é [A] em qualquer viewport. O que depende do aparelho é [B] no
máximo.

## 5. Jornada exercitada

| Pessoa fictícia | Formações | Percurso | O que foi exercitado |
|---|---|---|---|
| Ana | 1 (TADS, Serra, 2022) | Termos → Pessoais → Curso → Graduação → Avaliação (**trabalha**) → Egresso que trabalha → Estudo (**estuda**) → Egresso que estuda → Seção 13 → Concluir → Concluída | Jornada completa; recarregar; reabrir o endereço; Voltar/Avançar do navegador; salvamento parcial; histórico antigo; queda de rede antes e depois de gravar; conclusão com rede lenta |
| Maria | 2 (TADS e Especialização) | Escolha de formação → … → Avaliação (**não trabalha**) → Egresso que não trabalha → Estudo (**não estuda**) | Toque duplo em "Iniciar" com rede lenta; complemento "Outro" com erro de forma; Enter em campo de texto; recarregar página de erro vinda de POST; **"Sair e continuar depois" e retomada** |
| Elisa | 1 (Técnico Integrado) | … → Ensino Médio/Técnico Integrado → Avaliação (**não trabalha**) | Erro distante do topo numa Seção longa; zonas mortas de toque; varredura 320–430 px; fonte ampliada; horizontal; teclado simulado; falha de CSRF |
| Diego | 3 (Técnico, Licenciatura, Mestrado) | Entrada com várias formações → Termos → Pessoais → Curso | Enter no campo "ano", primeira pergunta da Seção 3 |

Ramos cobertos: Q14 Graduação e Integrado; Q33 Sim e Não; Q46 Sim e Não; complemento
"Outro". Não repetidos aqui por já cobertos na auditoria da 008: Técnico
Concomitante/Subsequente, Pós-Graduação, Q1 = Não, Campanha encerrada.

### Tamanho de cada Seção no celular (375×667, Ana)

As alturas incluem cerca de 231 px da faixa e do cabeçalho **de demonstração** (98 + 133
px), que não existirão em produção. Descontá-los muda pouco as conclusões (cerca de 0,35
tela).

| Seção | Perguntas | Altura (px) | "Salvar e continuar" em | Telas até o botão |
|---|---|---|---|---|
| 1 Termos e condições | 1 | 1.972 | 1.659 | 2,5 |
| 2 Informações Pessoais | 8 | 2.600 | 2.199 | 3,3 |
| 3 Informações do curso | 5 | 1.840 | 1.439 | 2,2 |
| 6 Graduação | 1 (lista de 50) | 1.000 | 599 | 0,9 |
| **8 Avaliação** | **14** | **3.924** | **3.523** | **5,3** |
| **9 Egresso que trabalha** | **11** | **3.964** | **3.563** | **5,3** |
| 10 Egresso que não trabalha | 1 | 1.200 | 799 | 1,2 |
| 11 Estudo | 3 | 1.772 | 1.371 | 2,1 |
| 12 Egresso que estuda | 3 | 1.660 | 1.259 | 1,9 |
| 13 (sem título) | 3 | 1.520 | 1.118 | 1,7 |
| Concluir a pesquisa | — | 1.216 | 1.014 | 1,5 |

## 6. Achados P0

### MF-01 — Interromper no meio de uma Seção descarta tudo o que foi marcado; o salvamento parcial existe, mas está escondido e aparece como erro

- **Evidência:** [A] para o mecanismo e a magnitude; [T] para a frequência no aparelho.
- **Viewport/dispositivo:** 375×667, Chromium; vale para qualquer largura.
- **Cenário e observação:**
  1. Ana, Seção 2: marcou Q1, digitou "34" em Q2 e marcou Q3, sem salvar. **Recarregar**
     a página: os três campos voltaram vazios. **Abrir o mesmo endereço de novo**: idem.
     As páginas são `Cache-Control: no-store` (`never_cache`), e o Chromium não restaurou
     o estado ao recarregar.
  2. Maria, Seção 11: marcou "Atualmente você estuda?" e tocou em "Sair e continuar
     depois". Ao entrar de novo, "Continuar a pesquisa" levou à Seção certa (11), com o
     campo vazio. O aviso da nota (corrigido no polish, UX-04) é honesto, mas só ajuda
     quem sai pelo link no fim da página.
  3. **Contraprova:** Ana tocou em "Salvar e continuar" com 3 de 8 perguntas
     respondidas. As 3 respostas **foram gravadas** (conferido no banco) e a página
     voltou com "Há problemas nesta seção / O que já foi preenchido nesta seção foi
     salvo", em vermelho, com as 4 obrigatórias restantes listadas como problemas.
- **Problema:** no celular, a interrupção típica não é tocar em "Sair": é trocar de
  aplicativo, atender uma ligação, bloquear a tela. Se o sistema descarta a aba nesse
  intervalo, ao voltar a página é recarregada, e então vale o item 1. A pessoa não tem
  como saber que tocar em "Salvar e continuar" com a Seção incompleta guarda o que já
  respondeu; quando faz isso, o sistema responde como se ela tivesse errado.
- **Impacto:** nas Seções 8 e 9, até 14 respostas e mais de 5 telas de trabalho (6,5
  telas em 320×568, 19 telas com fonte a 200%) dependem de um único toque no fim.
  Perder isso no meio da Seção é o cenário mais provável de abandono no celular.
- **Risco:** alto para o objetivo mobile-first; nenhum para a integridade dos dados (o
  que foi gravado nunca se perde).
- **Recomendação mínima [I]:** tornar visível o que já existe, sem mecanismo novo:
  - dizer que salvar com a Seção incompleta é permitido e guarda o que foi respondido
    (na frase de entrada, que hoje diz "o que for salvo fica guardado", e na nota de
    "Sair": "Para guardar o que marcou, toque antes em Salvar e continuar, mesmo que a
    seção esteja incompleta");
  - quando o envio só tem **pendências** (o redirecionamento `?pendencias=1&salvo=1`),
    trocar "Há problemas nesta seção" por um título neutro, "O que você respondeu foi
    salvo. Ainda faltam estas perguntas:", e reservar "problemas" para erros de forma.
    Mesma família de UX-12/UX-13.
  - Opcional, a decidir: um segundo botão "Salvar e sair" (já aventado em UX-04), útil
    para a interrupção voluntária.
- **Não recomendado agora:** autosave, rascunho no `localStorage` ou aviso
  `beforeunload`. Só se a validação em aparelho (seção 15, item 1) mostrar que o
  recarregamento ao voltar de outro aplicativo é frequente; e, mesmo então, como decisão
  explícita sobre o FR-080 (a interface não depende de JavaScript).
- **Pertence:** [I] para a comunicação; **[V]** para o tamanho das Seções 8 e 9 (seção
  14); [T] para a frequência real de descarte de aba.

## 7. Achados P1

### MF-02 — Enter/"Ir" num campo de texto envia a Seção inteira

- **Evidência:** [A] com Enter de teclado físico; [T] para a tecla do teclado virtual.
- **Cenário:** Diego, Seção 3: tocou em "Em que ano você concluiu…?" (a **primeira**
  pergunta da Seção), digitou 2017 e apertou Enter. A Seção foi enviada; a página voltou
  com "Erro:" no título e 4 "problemas" para perguntas que ele ainda nem tinha visto. O
  mesmo com o complemento "Descreva: «Outro»" (Maria, Seção 10) e vale para a idade
  (Seção 2, segunda pergunta).
- **Problema:** é envio implícito de formulário (o HTML envia ao apertar Enter num campo
  de texto quando existe botão de envio). No celular, a tecla de retorno de um campo num
  formulário costuma aparecer como "Ir", e tocá-la é o gesto natural de "terminei de
  digitar".
- **Impacto:** a pessoa é jogada ao topo, com um resumo vermelho, logo no início de
  uma Seção. Nada se perde (o ano foi salvo), mas é a pior forma de começar a Seção.
- **Recomendação mínima [I], só HTML:** bloquear o envio implícito colocando, como
  primeiro elemento do `<form>`, um botão de envio desabilitado e oculto (a especificação
  manda não enviar quando o botão padrão está desabilitado). Validar em iOS e Android
  qual rótulo a tecla passa a mostrar e se o foco avança (seção 15, item 3).
- **Prioridade:** P1.

### MF-03 — Voltar pelo histórico até uma entrada antiga reapresenta respostas desatualizadas, e salvar as regrava

- **Evidência:** [A] no Chromium; [T] no Safari iOS.
- **Cenário:** Ana salvou "Estado civil = Solteiro(a)" na Seção 2. Depois voltou à Seção
  2 pelo link "Voltar à seção anterior", trocou para "Casado(a)" e salvou. Em seguida usou
  o Voltar do navegador três vezes. A entrada antiga da Seção 2 exibiu **"Solteiro(a)"
  marcado**, embora o servidor tenha enviado "Casado(a)" (`defaultChecked`). O Chromium
  restaurou o estado do formulário guardado no histórico por cima do HTML novo. Um toque
  em "Salvar e continuar" regravaria a resposta antiga.
- **Problema:** no celular, voltar é um gesto (deslizar da borda, botão Voltar do
  Android), muito mais usado do que o link no fim da página. A restauração é boa no caso
  comum (o MF-06 depende dela), mas, numa entrada antiga, mostra uma resposta que não é a
  gravada, sem nenhum aviso.
- **Impacto:** resposta correta silenciosamente substituída por uma anterior. É raro:
  exige mudar uma Seção já salva e depois voltar várias vezes pelo histórico.
- **Recomendação mínima [I]:** `autocomplete="off"` no formulário da Seção desliga a
  restauração do navegador e faz a tela sempre mostrar o que está gravado. Custo: o
  Voltar do navegador também deixa de recuperar marcações **não salvas**. Por isso deve
  vir junto com MF-06. Validar no Safari iOS (seção 15, item 4).
- **Prioridade:** P1 (integridade da resposta, mesmo sendo rara).

### MF-04 — A área que de fato recebe o toque é menor do que a linha ou célula visual

- **Evidência:** [A] para as medidas e para os cliques precisos; [B] para o efeito com o
  dedo (o ajuste de toque do Chrome Android pode compensar parte; o Safari, menos).
- **Medidas (375 px):**
  - **Escala 1–5:** cada ponto ocupa uma célula de 44×44 px, mas só o círculo (20×20) e o
    número (16×28) respondem; o vão de 8 px entre eles e as faixas acima e abaixo não
    respondem. Cerca de **44% da célula** é tocável. Cliques no vão entre o círculo e o
    número "4", e logo abaixo do círculo, **não marcaram nada**; no círculo, marcou.
  - **Rádio e caixa de seleção:** o rótulo ocupa a largura toda (bom para as duas mãos),
    mas tem 28 px de altura numa linha de 44 px; os 16 px restantes não respondem.
- **Problema:** a pesquisa decidiu "alvos de toque ≥ 44px" (008, research R14) e a
  auditoria da 008 registrou "alvo de toque confortável". O **visual** tem 44 px; a
  **área de toque** não. Esta auditoria revisa aquela observação com medida.
- **Impacto:** toques que "não fazem nada", principalmente na escala, que aparece em 11
  perguntas no percurso de Ana. Não há risco de marcar a opção vizinha (o vão separa),
  só de toque perdido.
- **Recomendação mínima [I], só CSS:** fazer o rótulo cobrir a célula inteira (por
  exemplo `.opcao { position: relative }` e um `label::after` com `inset: 0`), sem mudar
  o HTML. Vale para os três tipos de controle.
- **Prioridade:** P1.

### MF-05 — Com fonte do sistema um pouco maior, a escala 1–5 quebra em "4 + 1"

- **Evidência:** [B] (fonte raiz ampliada; equivale à escala de fonte do Android e ao
  zoom de página); [T] em aparelho.
- **Medidas:** com fonte normal, os 5 pontos cabem numa linha de 320 a 430 px [B]
  (confirma a auditoria da 008). Mas:

  | Largura | 115% | 130% | 150% | 200% |
  |---|---|---|---|---|
  | 320 px | — | 2 linhas | 2 linhas | 3 linhas (2-2-1) |
  | 360 px | **2 linhas (4 + 1)** | 2 linhas (4 + 1) | 2 linhas (3 + 2) | 3 linhas (2-2-1) |
  | 390 px | — | 2 linhas | 2 linhas | 3 linhas |

  115% é a opção "Grande" da fonte do Android. Sem rolagem horizontal em nenhum caso.
- **Problema:** o "5" isolado na segunda linha, embaixo do "1", desfaz a leitura de uma
  escala ordenada e equidistante. É exatamente o público que aumenta a fonte que mais
  depende da forma visual da escala. Também cumpre só formalmente o FR-077 e o SC-015
  ("utilizável" com 200%, mas sem preservar a forma).
- **Recomendação mínima [I], só CSS:** número **abaixo** do círculo, em colunas iguais
  numa única linha (`grid-auto-flow: column; grid-auto-columns: 1fr`), sem depender da
  quantidade de pontos (segue a escala da Versão, sem tratamento por Pergunta). Em 320 px
  com 200%, cada coluna fica com cerca de 57 px, o que cabe. Junto com MF-04, a coluna
  inteira vira o alvo. A escala, a ordem e o significado não mudam.
- **Prioridade:** P1.

### MF-06 — "Voltar à seção anterior", que descarta o que não foi salvo, fica a 19 px do botão principal

- **Evidência:** [A] para as medidas e a navegação; [B] para o toque acidental.
- **Medidas (375 px, Seção 8):** "Salvar e continuar" de 16 a 196 px na horizontal,
  terminando em y = 355; o link "Voltar à seção anterior" começa em y = 374, alinhado à
  esquerda, com 163 px de largura. Um toque cerca de 5 mm abaixo do botão cai no link.
- **Problema:** o link é um GET que sai da página sem salvar. A nota abaixo dele avisa
  ("Alterações não salvas nesta página serão descartadas"), mas o aviso não protege de
  um toque errado. No Chromium, o Voltar do navegador recupera as marcações [A]; no Safari,
  não se sabe [T]; e se MF-03 for corrigido com `autocomplete="off"`, deixa de recuperar.
- **Impacto:** a Seção inteira (até 14 respostas) descartada por um toque impreciso, no
  ponto onde o polegar está.
- **Recomendação mínima [I], só CSS:** afastar o par "Voltar"/"Sair" do botão (2 a 3 rem
  a mais) ou separá-los visualmente, por exemplo com uma borda. "Voltar" e "Sair" já não
  competem visualmente com a ação principal (são links), só estão perto demais.
- **Prioridade:** P1.

## 8. Achados P2

**MF-07 — Nenhum retorno na página durante o envio; o servidor, porém, é robusto.**
Evidência [A]. Com 5 s de atraso, o botão "Concluir pesquisa" continuou ativo e igual;
só o indicador do próprio navegador mostrava carregamento. Toque duplo em "Iniciar a
pesquisa desta formação" (Maria): **2 POSTs chegaram ao servidor e devolveram a mesma
Participação** (restrição única campanha + conclusão). Com queda depois de gravar, o
Chromium **reenviou o POST sozinho**; as respostas da Seção 13 ficaram gravadas uma única
vez (restrição única participação + pergunta; comparação com o valor gravado). A pessoa,
porém, não fica sabendo que salvou. Recomendação: **não criar infraestrutura**; o servidor
já resolve duplicidade. Um aviso "Salvando…" exigiria JavaScript (decisão sobre o
FR-080) e só vale a pena se a validação em rede real (seção 15, item 6) mostrar toques
repetidos por falta de retorno. [I]

**MF-08 — Erros de forma voltam como resposta de POST; recarregar reenvia.** Evidência
[A] para o reenvio; [B]/[T] para o diálogo. Pendências seguem o padrão POST →
redirecionamento → GET, e recarregar é seguro. Já "Para descrever, marque a opção
«Outro»" e as rejeições da 005 são renderizadas na própria resposta do POST: recarregar
reenvia o formulário (no celular, aparece o diálogo nativo "Reenviar formulário?").
Inofensivo para os dados (validação de novo, nada gravado), mas confuso. Recomendação:
aceitar por ora; só uniformizar se o polish mexer nessa view. [I]

**MF-09 — A página "Envio não confirmado" (CSRF) manda recarregar, o que descarta as
respostas.** Evidência [A]. Com o cookie `csrftoken` apagado, o envio levou à página
"Não foi possível confirmar o envio. Volte à página anterior, recarregue e tente
novamente." Seguir a instrução ao pé da letra (recarregar) perde tudo; voltar e tocar em
"Salvar" de novo funcionou, com as marcações restauradas pelo Chromium. A página não tem
cabeçalho nem ligação para a Seção, só "Ir para o início". É raro (cookie com validade
de um ano), mas acontece com limpeza de dados ou modo privado. Recomendação: texto "Volte
à página anterior e toque em Salvar de novo", sem "recarregue". [I]

**MF-10 — O foco não vai para o resumo de erros nem para a pergunta.** Evidência [A]
para o foco; [C]/[T] para o leitor de tela. Depois do envio com pendências, o foco fica no
`body`; o anúncio depende de `role="alert"` presente no carregamento da página, que leitores
de tela móveis nem sempre anunciam. Tocar num item do resumo leva a Pergunta ao topo da tela
(correto), mas o foco continua no `body`. O FR-076 aceita "anunciado **ou** foco"; no
celular, o anúncio não está garantido. Recomendação: a âncora `#titulo-erros` no
redirecionamento, já sugerida em UX-01 e não adotada no polish, ou `autofocus` no resumo,
nos dois casos sem JavaScript. Validar com VoiceOver e TalkBack. [I][T]

**MF-11 — Idade e ano abrem o teclado alfabético.** Evidência [C] (`type="text"`, sem
`inputmode`); [T] no aparelho. Q2 (idade, Seção 2) e Q10 (ano, Seção 3) são do tipo
texto curto, porque o instrumento não tem tipo numérico, e a interface não pode tratar
uma Pergunta específica (FR-034). A auditoria da 008 já registrou que Q2 aceita "abc".
Recomendação: insumo para a revisão do instrumento; não tratar na interface. [V]

**MF-12 — Lista suspensa fechada corta o nome do curso.** Evidência [B]. Na Seção
"Graduação", 8 dos 50 cursos não cabem na caixa a 375 px: "Tecnologia em Análise e
Desenvolvimento de Sistemas" aparece como "…Análise e Desenvolvimento". Não há dois cursos
que fiquem iguais depois de cortados. O seletor nativo aberto mostra o nome inteiro no
Android e, provavelmente, no iOS [T]. Não há correção mínima sem JavaScript; a solução de
verdade é não perguntar o que o Ifes já sabe (D-1/ID-01, DP-307). [Dec]

**MF-13 — Ligações da tela "Concluir a pesquisa" pequenas e próximas.** Evidência [A]
para as medidas. As 9 ligações para revisar Seções têm 19 px de altura e 5 px de
intervalo; "Estudo" e "Seção 13" têm cerca de 50 px de largura. Cumprem o mínimo da WCAG
2.2 (24 px com espaçamento) no limite; um toque errado leva à Seção vizinha, sem dano.
Recomendação: espaçamento vertical na lista (CSS). [I]

**MF-14 — Botão principal estreito e à esquerda.** Evidência [A] para as medidas; [B]
para o alcance. "Salvar e continuar" tem 180×44 px, de x = 16 a 196 numa tela de 375.
Como a página rola, o botão sempre pode ser trazido para a altura do polegar; o problema
é só horizontal, para a mão direita, e cresce a 430 px. Recomendação: largura total abaixo
de cerca de 30 rem (CSS), o que também afasta o alvo de MF-06. [I]

## 9. Interrupção e retomada

| Situação | Observado | O que fica persistido | Evidência |
|---|---|---|---|
| Responder parte da Seção e **recarregar** | Tudo o que foi marcado some | Só o que foi salvo antes | [A] |
| Responder parte e **abrir o endereço de novo** (aba fechada e reaberta, link de novo) | Idem | Idem | [A] |
| Responder parte e **"Sair e continuar depois"** | Nota avisa o descarte; retomada vai à Seção certa, vazia | Idem | [A] |
| Responder parte e **tocar em "Salvar e continuar"** | Salva o respondido; volta com "Há problemas nesta seção" | O que foi respondido, mesmo sem completar | [A] (banco) |
| **Voltar** do navegador e **Avançar** | Chromium restaura as marcações não salvas (página recarregada do servidor, estado de formulário restaurado; não é bfcache) | Nada novo | [A] Chromium; [T] Safari |
| Voltar até uma **entrada antiga** | Mostra a resposta antiga, não a gravada (MF-03) | Risco de regravar a antiga | [A] Chromium |
| Usar o link **"Voltar à seção anterior"** | Descarta o não salvo (avisado) | Idem | [A] |
| Interromper **entre Seções** | Nada se perde; "Continuar a pesquisa" leva à Seção atual da 006 | Todas as Seções salvas | [A] |
| Interromper **depois de tocar em Salvar**, com a rede caindo | Nada gravado se caiu antes; tudo gravado se caiu depois; nos dois casos, nenhuma mensagem do sistema | Depende do momento; nunca duplicado | [A] |
| **Fechar o navegador** e reabrir | Na demonstração, o cookie de sessão encerra a escolha da pessoa; em produção depende da forma de acesso | Tudo o que foi salvo | [C]; [Dec] 004/DP-406 |
| Sistema **descarta a aba** em segundo plano | Não reproduzível aqui | — | [D]/[T] |

**Respostas condicionais.** Mudar Q33 e sair sem salvar não altera nada; mudar e salvar
troca o ramo conforme a 006, e as respostas do ramo anterior continuam guardadas e
reaparecem se a pessoa voltar a ele (já observado na 008). Na retomada, a Seção apresentada
é sempre a atual calculada pela 006 [A].

**Duplicidade.** Nenhuma, em nenhum teste [A]: as restrições únicas (`participacao_par_unico`,
`resposta_pergunta_unica`), o bloqueio da Participação na gravação e a comparação com o
valor gravado tornam reenvios inofensivos. A conclusão repetida redireciona para "Pesquisa
concluída" [C].

**Clareza para a pessoa.** Ela sabe que "o que for salvo fica guardado" (tela de entrada,
nota de "Sair"). Não sabe que **pode salvar uma Seção incompleta**, e, quando faz isso,
recebe uma mensagem de erro (MF-01).

## 10. Teclado virtual

| Verificação | Resultado | Evidência |
|---|---|---|
| Campo ativo e rótulo visíveis com o teclado aberto | Sim: com 376 px de altura útil, o rótulo de Q2 fica em y = 134 e o campo entre 166 e 210 | [B] |
| Teclado cobrindo botão necessário | Não há botão fixo; "Salvar" fica abaixo do conteúdo, a 1.308 px do campo de idade, e só importa quando a Seção termina | [B]/[C] |
| Ampliação automática ao focar (iOS) | Não deve ocorrer: campos e listas com 16 px | [C]; [T] |
| Mensagem de erro escondida | Não: o erro fica **acima** do campo, dentro da pergunta, e aparece junto do rótulo | [C]/[B] |
| Tipo de teclado | Alfabético para idade e ano (MF-11) | [C]; [T] |
| Enter/"Ir" | Envia a Seção (MF-02) | [A] Enter; [T] tecla virtual |
| Barra "anterior/próximo" do iOS | Pode pular de Q2 (idade) direto para Q7 (lista), sem passar pelos rádios Q3–Q6 | [D]/[T] |
| Teclado em orientação horizontal | Não reproduzido | [D]/[T] |

## 11. Uso com uma mão

- **Seleção:** rádios e caixas têm o rótulo em toda a largura, alcançável pelas duas mãos
  [A]. A escala ocupa os 260 px da esquerda; o "5" fica em cerca de x = 270, alcançável.
  O ponto fraco é a área tocável (MF-04), não o alcance.
- **Avançar:** a página rola e o botão segue o conteúdo, então pode ser trazido à altura
  do polegar; não há controle fixo fora do alcance. O botão é estreito e à esquerda
  (MF-14).
- **Corrigir uma resposta anterior** numa Seção longa exige rolar de volta até 5 telas;
  no envio com pendências, o resumo no topo leva à Pergunta com um toque [A]. Depois
  disso é preciso rolar de novo até o botão: na Avaliação de Elisa, as pendências ficaram
  em y = 3.024 e 3.668, numa página de 4.254 px.
- **"Voltar" e "Sair" não competem visualmente** com a ação principal (são links), mas
  ficam perto demais dela (MF-06).
- **Toque acidental:** o risco real é cair no link "Voltar" (MF-06), não marcar a opção
  vizinha.
- **Opções longas** (por exemplo "Cotista (vagas de cotas, ações…") quebram em várias
  linhas e o rótulo inteiro é tocável [A].
- Navegação inferior fixa **não** é recomendada: nada aqui a justifica.

## 12. Rede lenta/perdida

| Cenário | O que aconteceu | A pessoa sabe se salvou? | Duplicidade | Perde respostas? | Evidência |
|---|---|---|---|---|---|
| Lento (5 s) em "Concluir pesquisa" | Botão continua ativo, sem mudança na página; conclusão correta após 5 s | Só pelo indicador do navegador | Não | Não | [A] |
| Lento (3 s) + toque duplo em "Iniciar" | 2 POSTs processados; mesma Participação | Sim, ao chegar à Seção 1 | **Não** (banco: 1 Participação) | Não | [A] |
| Queda **antes** de chegar ao servidor (Seção 13) | O Chromium reenviou o POST uma vez e também caiu; o painel recarregou a Seção por GET, com os campos vazios | Não | Não | **Sim, as marcações da página** | [A] servidor; [B] apresentação (um navegador móvel mostraria a própria página de erro) |
| Queda **depois** de o servidor gravar | Gravado; o Chromium reenviou o POST (idempotente); a pessoa voltou a ver a mesma Seção, já preenchida | **Não**: nenhuma mensagem | **Não** (banco: 3 respostas) | Não | [A] |
| Recarregar depois do erro | Página de erro de POST: reenvio (MF-08); página de pendências: seguro | — | Não | Depende de restauração do navegador | [A]/[B] |
| Tempo esgotado do navegador móvel | Não reproduzido | — | — | — | [D] |

Conclusão: **não há evidência de que se precise de offline-first, fila local ou
service worker.** O servidor já é idempotente. A lacuna é só de comunicação (MF-07), e a
perda real é a mesma de MF-01: o que está na página e ainda não chegou ao servidor.

## 13. Acessibilidade mobile

**O que a marcação já garante [C]:** `lang="pt-BR"`; "Pular para o conteúdo"; regiões
`header`, `main` e `footer`; `fieldset` + `legend` em escolha e escala; `label for` em
texto e lista; explicação, descrição da escala e erro ligados por `aria-describedby`;
`aria-invalid` e `aria-required`; "(obrigatória)" e "Erro:" em texto; título da aba com
"Erro:"; contraste AA documentado; zoom por pinça permitido (sem `user-scalable=no`);
nenhuma orientação travada; reflow sem rolagem horizontal de 320 px até 200% de fonte [B].

**Lacunas:**

- foco depois de erro (MF-10);
- **escala:** cada ponto é anunciado só como "1", "2"…; o significado ("5 = Concordo
  totalmente") está na descrição do grupo, que leitores móveis podem não ler ao entrar
  num rádio. O rótulo ausente do ponto 1 é do instrumento (E-09/DP-301) e não é achado
  novo;
- a caixa "Deixar esta pergunta sem resposta" dentro de `role="radiogroup"` (UX-19, ainda
  aberto);
- alvos de toque (MF-04) e forma da escala com fonte ampliada (MF-05).

**Leitores de tela não foram testados** [D]. Roteiro na seção 15, itens 7 e 8.

## 14. Blocos longos e componentes críticos

Evidência para a futura revisão do instrumento [V], **sem propor divisão aqui**.

**Seção 8 "Avaliação" (14 perguntas: 10 de escolha única, 2 de escala, 2 de caixas; Q33,
que ramifica, é a última).** Em Elisa:

| Viewport | Altura (px) | "Salvar" em | Telas até o botão |
|---|---|---|---|
| 320×568 | 4.076 | 3.675 | 6,5 |
| 360×640 | 3.948 | 3.547 | 5,5 |
| 375×667 | 3.900 | 3.499 | 5,2 |
| 390×844 | 3.852 | 3.475 | 4,1 |
| 412×915 | 3.780 | 3.427 | 3,7 |
| 430×932 | 3.710 | 3.379 | 3,6 |
| 320×568, fonte 200% | 12.201 | 10.976 | 19,3 |
| 667×375 (horizontal) | 3.390 | 3.059 | 8,2 |

- **Perda de contexto:** perguntas de "durante o curso" seguidas, no fim, de "Atualmente
  você trabalha?", a 5 telas do contexto da formação no topo (ver ID-06).
- **Erro distante:** com 2 obrigatórias em branco, a página cresce para 4.254 px e as
  pendências ficam a 4,5 e 5,5 telas do resumo. A ligação do resumo funciona [A].
- **Efeito do teclado:** pequeno nessa Seção (só os complementos de "Outro" são texto),
  mas, nas caixas de "publicação" e "bolsa", o complemento sempre visível acrescenta cerca
  de 70 px a cada uma, mesmo sem "Outro" marcado.
- **Exposição a perda (MF-01):** é a Seção onde uma interrupção custa mais.

**Seção 9 "Egresso que trabalha"** (11 perguntas, 4 de escala, opções longas): 3.964 px e
5,3 telas a 375×667, a mais alta da jornada.

**Componentes críticos:**

| Componente | Situação no celular | Achado |
|---|---|---|
| Escala 1–5 | Uma linha com fonte normal; quebra com fonte ampliada; área tocável de 44% da célula | MF-04, MF-05 |
| Rádio | Rótulo em toda a largura; 16 px mortos por linha | MF-04 |
| Caixas | Idem; complemento sempre visível | MF-04 |
| Lista suspensa | Seletor nativo, bom para uma mão; caixa fechada corta nomes longos | MF-12 |
| Texto | 16 px, rótulo e erro acima; teclado alfabético; Enter envia | MF-02, MF-11 |
| "Salvar e continuar" | 180×44, à esquerda, a até 6,5 telas do topo | MF-01, MF-14 |
| "Voltar" / "Sair" | Links de 19 px; "Voltar" a 19 px do botão | MF-06 |
| Resumo de erros | Na primeira tela até 320×568 (começa em y = 362 com a faixa de demonstração) [B]; sem foco | MF-10 |

**Orientação horizontal (667×375):** a primeira pergunta começa em y = 363, ou seja,
fora da primeira tela; 175 px são da faixa e do cabeçalho de demonstração, o resto é o h1
"Egresso Ifes", a linha de contexto e o título da Seção [B]. É o mesmo problema de UX-05,
UX-07 e ID-05, agravado; não é achado novo.

## 15. O que não foi possível testar

Roteiro mínimo para validação em aparelho, **antes de aceitar um polish mobile**:

| # | O que testar | Dispositivo/sistema | Comportamento a observar |
|---|---|---|---|
| 1 | Marcar metade da Seção 8, trocar para WhatsApp e câmera por 2 a 10 min, voltar | iPhone com Safari (iOS 17+); Android de entrada com 3–4 GB de RAM e Chrome | A página recarrega? As marcações voltam? (decide se MF-01 precisa de algo além de texto) |
| 2 | Fechar a aba e reabrir pelo histórico; fechar o navegador e reabrir | Os mesmos | Marcações e identificação da pessoa (depende de DP-406) |
| 3 | Digitar o ano na Seção 3 e tocar na tecla de retorno | iOS Safari; Gboard e teclado Samsung no Chrome | Rótulo da tecla ("Ir"/"Próximo"); a Seção é enviada? Depois de MF-02: o foco avança? |
| 4 | Repetir o cenário de MF-03 com gestos de voltar | iOS Safari (deslizar da borda); Android (gesto ou botão) | Aparece a resposta antiga ou a gravada? Com `autocomplete="off"`? |
| 5 | Tocar com o polegar entre o círculo e o número da escala e abaixo do rótulo das opções | iPhone e Android, uma mão | Taxa de toques perdidos (MF-04) |
| 6 | Responder com rede 3G lenta e com queda (modo avião no meio do envio) | Os dois | Mensagem do navegador; a pessoa toca de novo? Entende que salvou? |
| 7 | Seção 8 com **VoiceOver**: entrar numa escala, ouvir o rótulo; enviar com pendência | iPhone, Safari | O enunciado é anunciado? "5 = Concordo totalmente" é lido? O resumo de erros é anunciado ao carregar? Para onde vai o foco ao tocar no item do resumo? |
| 8 | O mesmo com **TalkBack** | Android, Chrome | Idem; e se "(obrigatória)" e "Erro:" são lidos |
| 9 | Fonte do sistema em "Grande" e "Máxima" | Android (tamanho da fonte e zoom de página do Chrome); iOS (zoom de página aA) | A escala quebra em 4 + 1 (MF-05)? |
| 10 | Seletor nativo com os 50 cursos e os 78 de pós-graduação | iOS e Android | O nome inteiro aparece no seletor aberto? |
| 11 | Barra "anterior/próximo" do teclado iOS na Seção 2 | iPhone | Pula os rádios? |
| 12 | Abrir o link dentro do WhatsApp/Instagram | Os dois | **Só depois de DP-406** (seção 16) |

Também não testados: tempo esgotado real de rede móvel; economia de dados; desempenho em
aparelho lento (a página tem cerca de 14 KB de HTML com CSS embutido e nenhum JavaScript,
o que torna improvável um problema [C]).

## 16. Dependências que ficaram deliberadamente fora

| Tema | Depende de | Por que não foi avaliado |
|---|---|---|
| Abertura por WhatsApp ou e-mail, navegador embutido de aplicativo, persistência da identificação ao fechar e reabrir | 004/DP-406 (forma de acesso e identificação) | Sem a forma de acesso, não há o que observar; o cookie de demonstração não representa produção |
| Medir onde e quanto se abandona | DP-803 | Sem decisão de base legal e finalidade, nenhuma instrumentação |
| Ver, copiar ou compartilhar as próprias respostas, retrato | DP-802 | Fora da jornada de resposta |
| Linguagem e identidade visual definitivas | DP-801 | Os textos sugeridos aqui são funcionais e revisáveis |
| Não perguntar o que o Ifes já sabe (Seções 3 e 6) | 003/DP-307 | Resolveria MF-12 e reduziria a Seção 3, mas é decisão de domínio |

Nenhum desses itens gerou tela, requisito ou recomendação de arquitetura.

## 17. Relação com as auditorias de usabilidade e identidade

| Item anterior | Situação hoje no celular | Nesta auditoria |
|---|---|---|
| UX-01 resumo de erros fora da primeira tela | **Corrigido** na posição; o foco continua no `body` | MF-10 (só o foco) |
| UX-04 "Sair" descarta em silêncio | **Corrigido** o texto | MF-01 amplia para a interrupção involuntária e o salvamento parcial |
| UX-05 / UX-07 contexto e título | Contexto compacto feito; h1 continua "Egresso Ifes" | Evidência na horizontal (seção 14); não duplicado |
| UX-12 / UX-13 resumo de erros | Parcialmente feito | MF-01 propõe o título neutro para pendências |
| UX-19 caixa "Remover" dentro do grupo de rádio | Aberto | Citado na seção 13 |
| 008: "escalas cabem numa linha em 320 px" | Verdadeiro só com fonte normal | **Revisado** por MF-05 |
| 008: "campos e opções com alvo de toque confortável"; R14 "alvos ≥ 44px" | O visual tem 44 px; a área tocável, não | **Revisado** por MF-04 |
| 008: "Q2 aceita abc" | Aberto (instrumento) | MF-11 acrescenta o teclado |
| D-1 / ID-01 mostrar e depois perguntar | Aberto (DP-307) | MF-12 é sintoma |
| ID-06 "durante o curso" sem âncora | Aberto | Agravado pela altura da Seção 8 (seção 14) |
| ID-14 escolha de formação abaixo da dobra | Confirmado (primeiro botão em y = 857 a 375×667) | Não duplicado |
| Identidade, seção 6: blocos curtos [V] | — | Seção 14 fornece as medidas |

## 18. Recomendações para consolidação das três lentes

1. **Um único polish de interface [I] para as três lentes**, porque os achados mexem nos
   mesmos arquivos (`secao.html`, `estilo.css`, `formacoes.html`, `mensagens.py`) e,
   separados, se desfariam uns aos outros:
   - **mobile:** MF-01 (textos e título neutro para pendências), MF-02, MF-03 + MF-06
     juntos, MF-04 + MF-05 juntos, MF-09, MF-10, MF-13, MF-14;
   - **identidade:** ID-03, ID-04, ID-06, ID-09, ID-11, ID-12, ID-14;
   - **usabilidade remanescente:** UX-07 (h1), UX-19.

   Tudo em CSS, template e texto fixo, sem JavaScript, sem modelo novo. O critério de
   aceite inclui o roteiro da seção 15, itens 1, 3, 4, 5 e 9, num iPhone e num Android
   reais.
2. **Decidir explicitamente, antes desse polish,** só duas coisas: se entra o botão
   "Salvar e sair" (MF-01, UX-04); e se `autocomplete="off"` (MF-03) vale perder a
   recuperação pelo Voltar do navegador, o que fica aceitável com MF-06 resolvido.
3. **Pacote da Versão [V]** para a primeira revisão do instrumento, com as medidas da
   seção 14: tamanho e composição das Seções 8 e 9; tipo numérico para idade e ano
   (MF-11); rótulo do ponto 1 das escalas (E-09/DP-301); títulos (ID-05, ID-13); ordem
   (ID-07).
4. **Pacote de decisão [Dec]**, já identificado pela identidade e reforçado aqui:
   DP-307 (resolveria MF-12 e encurtaria a Seção 3), DP-702 e o histórico de
   Participações. DP-406 é pré-requisito para a próxima auditoria mobile, de abertura e
   retorno pelo link.
5. **Não fazer agora:** autosave, rascunho local, `beforeunload`, PWA, service worker,
   offline-first, navegação inferior fixa, framework JS, wizard. Só reabrir se a validação
   em aparelho (seção 15, item 1) mostrar recarregamento frequente ao voltar de outro
   aplicativo, e mesmo então começar pelo menor passo possível.

## Conclusão

**O que, comprovadamente, impede hoje que a experiência seja considerada mobile-first?**

Um único ponto: **MF-01**. Interrompida no meio de uma Seção, a pessoa perde tudo o que
marcou se a página for recarregada ou reaberta, o que foi reproduzido [A]. Nas Seções
"Avaliação" e "Egresso que trabalha" isso pode chegar a 14 respostas e 5 a 6,5 telas de
trabalho num celular comum. O sistema já guarda Seções incompletas, mas não diz isso e
apresenta o salvamento parcial como erro. Para um egresso que "pode ser interrompido e
precisa conseguir continuar depois", essa é a lacuna central. A correção mínima é de
comunicação [I]; o tamanho dessas duas Seções é da Versão [V]; a frequência com que o
celular recarrega a aba ainda precisa de confirmação em aparelho [T].

Nada mais **impede** o uso: a jornada completa funciona de 320 a 430 px, sem rolagem
horizontal, com fonte até 200%, e é robusta a toques duplos e a rede instável, sem
duplicar nem perder o que chegou ao servidor.

**O que seria apenas melhoria desejável?**

- **Ganho relevante (P1), todos pequenos:** impedir que Enter/"Ir" envie a Seção
  (MF-02); evitar que o Voltar do navegador reapresente respostas antigas (MF-03); fazer o
  toque valer na célula inteira (MF-04); manter a escala numa linha com fonte ampliada
  (MF-05); afastar "Voltar" do botão principal (MF-06).
- **Refinamento (P2):** retorno durante o envio (MF-07), reenvio de POST (MF-08), texto
  da página de CSRF (MF-09), foco no resumo de erros (MF-10), teclado numérico (MF-11,
  [V]), listas longas (MF-12, [Dec]), ligações da tela de conclusão (MF-13) e largura do
  botão (MF-14).
