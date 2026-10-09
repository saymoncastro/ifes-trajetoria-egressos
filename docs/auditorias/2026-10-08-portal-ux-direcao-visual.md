# Portal do Egresso — auditoria de experiência e direção visual

Data: 2026-10-08. Auditoria por agente, sobre o código de `main` (`8a1fb4f`) e a
demonstração local navegada com as personas fictícias. Só diagnóstico e proposta: nada
foi implementado, nenhuma feature Spec Kit foi aberta e o instrumento não foi tocado.

> **Atualização de 2026-10-09 (depois do PR #49).** A Feature 025 (Oportunidades) foi
> integrada na `main` (`07b9cf9`) depois desta auditoria. A 025 está no shell atual.
> Medidas e capturas abaixo são de `8a1fb4f`, **antes** da 025, e não foram refeitas.
> O que a 025 muda neste documento está marcado com "Atualização 2026-10-09":
>
> - o Início ganhou o bloco "Oportunidades" entre as ações e o convite (025 FR-021), o que
>   empurra o convite mais para baixo (P3);
> - a navegação passou a ter cinco itens para quem tem trajetória (P8);
> - existe `/oportunidades/` para o egresso e `/curadoria/oportunidades/` para a operação
>   (§3);
> - a decisão 9 do §15 (ordem em relação à 025) ficou resolvida pelos fatos (§13).

Não é sessão com egresso e não substitui o Checkpoint 1. As afirmações sobre percepção
("parece", "lê-se como") são hipóteses do avaliador; as medidas e os trechos de código
são observações reproduzíveis.

## 1. Diagnóstico executivo

**A crítica está certa sobre o resultado e errada sobre a causa.** O Portal parece uma
aplicação de tarefa porque foi especificado para parecer uma. A interface implementada
não se distanciou da visão por descuido: ela cumpre, com fidelidade, decisões
registradas para outro produto, a jornada de resposta. Na 024, o Portal herdou essas
decisões.

O encadeamento:

1. A auditoria de identidade visual de 2026-10-03 definiu o Trajetória como "um serviço
   do Ifes, não um site do Ifes": branco, calmo, tipográfico, coluna única de 40 rem e
   sem hero, faixas, cards em grade nem aside
   ([§13](2026-10-03-identidade-visual.md); síntese no fim do documento). O §13 diz
   "Container 40 rem (640 px) **para a jornada**: manter". A decisão foi tomada para o
   preenchimento do questionário.
2. A 015 transformou isso em requisito para todo o shell: tokens, um breakpoint (480 px),
   sem sombras nem cards e uma coluna.
3. A 024 abriu o Portal sobre o mesmo shell e o mesmo vocabulário:
   - "O Início DEVE reaproveitar tokens e componentes da 015 [...] NÃO DEVE criar tokens
     novos [...] NÃO DEVE usar grade de cartões nem hero com saudação"
     ([024 FR-026](../../specs/024-inicio-egresso-portal/spec.md));
   - "Uma coluna, a mesma da 021"
     ([research](../../specs/024-inicio-egresso-portal/research.md)).
4. O roadmap leu o protótipo `portal_egresso.html` linha a linha e cortou quase toda a
   ambição visual dele: hero escuro, faixas, cartões, saudação pelo nome e fotografias.
   Cada corte tinha um motivo legítimo para um produto de tarefa
   ([roadmap, tabela do mockup](../roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md)).

O resultado medido: a 1440 px, o conteúdo usa 640 px (44% da largura). O Início a 1440 px
é **a mesma composição** da tela a 375 px, só que centralizada. Os dois têm a mesma ordem
e as mesmas proporções, e nenhum elemento muda de lugar.

Consequência prática: um redesenho **não é ajuste de CSS**. Antes de qualquer protótipo,
é preciso revogar ou delimitar explicitamente cinco decisões registradas (§9). Sem isso,
a próxima feature de interface vai esbarrar nos mesmos requisitos e reproduzir o padrão
atual, porque é isso que as specs mandam.

O que preservar é muito: a ordem "o que o Ifes sabe → de onde vem → o que você pode
fazer → convite", a proveniência explícita, a acessibilidade, a ausência de JavaScript e
o conteúdo da Minha trajetória (capítulos, números do ano e card), que é o material mais
forte do produto e hoje está escondido.

## 2. Método e limites

- Servidor local em `127.0.0.1:8000`, banco próprio (`trajetoria_auditoria_ux`) e dados
  fictícios do `preparar_demonstracao`.
- Capturas de página inteira via Chrome headless, com fator de escala 1, a 1440, 1280,
  1024, 768 e 375 px. A primeira tela foi capturada a 1440×900 e a 1280×720. Medidas por
  `getBoundingClientRect`.
- Personas: Ana (1 formação, pesquisa pendente) e Diego (3 formações). As capturas estão
  em [evidencias-2026-10-08-ux-portal/](evidencias-2026-10-08-ux-portal/).
- **Sem renderizador de vídeo** (`video/node_modules` ausente). Por isso a ação "Gerar o
  vídeo" não aparece; ela é condicionada a `renderizador.disponivel()` em
  `trajetoria/portal/inicio.py`. O vídeo não foi avaliado.
- **O protótipo `portal_egresso.html` não está no repositório.** O roadmap e a 024 o
  citam, e a avaliação por IA de 2026-10-08 já registrava a ausência. A comparação com a
  "visão original" (§7) usa o que o roadmap registrou sobre ele, não o arquivo.
- Elementos de demonstração descontados na análise:
  - a faixa amarela;
  - o painel "Dados fictícios para demonstração";
  - o sufixo "(demonstração)" do título e do rodapé;
  - a ilustração genérica, um provisório declarado
    ([imagens.py](../../trajetoria/narrativa/imagens.py), DP-2106).
- Não foram feitos teste com usuários, auditoria WCAG completa nem teste com leitor de
  tela. As restrições de acessibilidade vêm das specs e não foram reauditadas.

## 3. Inventário das telas

| Rota | Papel | Shell | Evidência |
|---|---|---|---|
| `/` | Redireciona: sem sessão para `/entrar/`, com sessão para `/inicio/` | — | `trajetoria/portal/views.py` (`entrada`) |
| `/entrar/` | Identificação (CPF e nascimento) que leva ao Início. **É a única página pública do Portal** | 015, sem navegação | `01-entrar-*.png` |
| `/inicio/` | Início autenticado | 015 + navegação | `03-*`, `04-*`, `05-*` |
| `/minha-trajetoria/` | Narrativa em 3 capítulos, card e vídeo | 015 + navegação | `06-*` |
| `/oportunidades/` | Oportunidades curadas (025). **Atualização 2026-10-09:** criada depois desta auditoria | 015 + navegação | — |
| `/meu-email/` | Contato | 015 + navegação | `07-*` |
| `/formacoes/` e seções | Instrumento (fora do escopo de mudança) | 015, sem navegação | `08-*` |

Todas usam o mesmo `interface/base.html`. A largura vem de
`.coluna { max-width: 40rem }` ([estilo.css:74](../../trajetoria/interface/templates/interface/estilo.css)).
A única folha própria do Portal tem 18 linhas
([inicio.css](../../trajetoria/portal/templates/portal/inicio.css)) e diz no comentário:
"sem token novo, sem grade de cartões".

## 4. Problemas identificados

As classes são: **C** concepção, **AI** arquitetura da informação, **ID** identidade
visual, **IMP** implementação e **COS** cosmético. "Observado" foi medido ou visto;
"hipótese" é leitura do avaliador.

### P1 — Não existe página pública do Portal (C, observado)

`/` redireciona direto para o formulário. Sem o painel de demonstração, a página pública
inteira tem um rótulo, um h1 ("Confirme seus dados para entrar no Portal do Egresso"),
uma frase, dois campos e um botão. Nenhum texto diz o que é o Portal, o que a pessoa
encontra lá ou por que vale entrar.

O roadmap nunca previu uma página pública. A entrada foi concebida como uma rota neutra
sobre a identificação da 018. Ou seja, isto não é um defeito de implementação: falta uma
decisão de produto.

*Evidência:* `01-entrar-1440.png`, `02-entrar-1440-primeira-tela.png` e `views.py`.

### P2 — O Portal herda a coluna do instrumento em todas as larguras (AI/ID, observado)

| Largura | Coluna | Uso da largura |
|---|---|---|
| 1440 | 640 px | 44% |
| 1280 | 640 px | 50% |
| 1024 | 640 px | 63% |
| 768 | 640 px | 83% |
| 375 | 375 px | 100% |

Do 375 ao 1440 não há reorganização: as capturas `03-inicio-ana-375.png` e
`03-inicio-ana-1440.png` têm a mesma sequência vertical. O cabeçalho também se alinha à
coluna de 640 px (auditoria §13: "o cabeçalho não deve 'abrir' para a largura total").
Por isso a 1440 px a assinatura e o nome do produto ficam soltos no meio de uma faixa
vazia.

O argumento original dos 40 rem é a linha de 70–80 caracteres contra os 150 do IFRN. Ele
continua certo **para texto corrido**, mas não exige coluna única. Uma grade larga com
blocos de texto limitados a cerca de 70 caracteres resolve as duas coisas.

### P3 — No desktop, a primeira tela do Início não mostra o que o Início promete (AI, observado)

| Viewport | O que cabe sem rolar |
|---|---|
| 1280×720 | Faixa de demonstração, cabeçalho, navegação, ilustração e h1. **Nenhum fato** de reconhecimento, nenhuma ação |
| 1440×900 | O mesmo, mais a frase-síntese e a primeira formação |

Na Ana a 1440 px, "O que você pode fazer" começa a 988 px e o convite a 1293 px.
Descontando a faixa de demonstração (~120 px), a 1280×720 continua sem nenhuma ação
visível. Cerca de 380 px da primeira tela vão para a ilustração genérica.

A 024 só exige a primeira tela a 375×812 (FR-032). Nada mede o desktop.

**Atualização 2026-10-09:** com a 025, o bloco "Oportunidades" fica entre as ações e o
convite. Para quem tem oportunidade pertinente, o convite desce ainda mais. A medida não
foi refeita.

*Evidência:* `04-inicio-ana-1280x720-primeira-tela.png` e
`04-inicio-ana-1440-primeira-tela.png`.

### P4 — As ações são uma lista de links sem distinção (AI, observado; impacto: hipótese)

"Ver minha trajetória", "Baixar o card da sua trajetória" e "Manter seu e-mail" são três
links iguais, com divisores (`.lista-simples`). Nada mostra a diferença de natureza entre
eles: uma narrativa, uma imagem para compartilhar e um cadastro.

O card já existe como imagem servida (`/minha-trajetoria/card.svg` e `card.png`), mas o
Início não o mostra. Ele só aparece a cerca de 2,5 telas de rolagem dentro da Minha
trajetória.

Hipótese, apoiada pela leitura alternativa já registrada na avaliação por IA: "O que você
pode fazer" seguido de "Pesquisa de acompanhamento" lê-se como lista de afazeres.

### P5 — O melhor conteúdo está fora do Início (C/AI, observado)

A Minha trajetória tem:

- o capítulo "Naquele ano no Ifes", com os números "27" conclusões do curso e "812" da
  unidade no ano;
- a linha do tempo;
- a prévia do card com "Essa história também é minha." e `#SouEgressoIfes`.

Esse é o material que faz a pessoa "perceber que sua trajetória tem valor". O Início
repete a formação em texto e manda para lá por um link.

*Evidência:* `06-minha-trajetoria-ana-1440.png` comparado com `03-inicio-ana-1440.png`.

### P6 — A imagem genérica leva o nome de uma unidade real (ID, observado)

O mesmo desenho aparece como "Unidade Serra · ilustração" para a Ana e como "Unidade Vila
Velha · ilustração" para o Diego. A legenda cumpre a regra ("· ilustração"). Ainda assim,
nomear uma unidade sobre um prédio inventado convida a lê-lo como retrato dessa unidade.

O desenho é provisório por decisão: o catálogo só aceita fotografia com origem e licença
registradas (DP-2106).

**A maior alavanca visual do Portal, fotografia institucional licenciada, depende da ACS
e não de engenharia.**

*Evidência:* `03-inicio-ana-1440.png` comparado com `05-inicio-diego-1440.png`.

### P7 — Presença da identidade Ifes (ID, observado; percepção: hipótese)

A identidade aparece em quatro elementos:

- a assinatura;
- o fio verde de 4 px;
- o fundo tonal `#eef7f0`;
- o título verde-escuro.

A cor de ação em uso é o azul do Padrão Digital de Governo (`#1351b4`), mantido como
**provisório** até a decisão D-02. A Direção A (verde `#195128`) é a recomendada pela 015
e nunca foi aplicada.

Somados ao `system-ui` e aos links azuis sublinhados, esses elementos produzem a leitura
de "serviço digital de governo" antes da leitura de "Ifes". Hipótese, coerente com o
diagnóstico de partida da própria auditoria de identidade ("gramática GOV.UK").

### P8 — "Pesquisa" é item de navegação par da trajetória (AI, observado; leitura: hipótese)

A navegação era Início, Minha trajetória, Pesquisa e Meu e-mail. **Atualização
2026-10-09:** com a 025, quem tem trajetória vê cinco itens (Início, Minha trajetória,
Oportunidades, Pesquisa, Meu e-mail; `trajetoria/portal/contexto.py`). Isso agrava a
quebra de linha no celular (A5), que não foi remedida. Com "Pesquisa" e "Meu
e-mail" no menu, o lugar pode ser lido como cadastro ou área do aluno; a avaliação por
IA de 2026-10-08 já registrou essa leitura. Isso reforça a crítica de que a pesquisa
define a identidade do Portal, embora a 024 a tenha posto no fim do Início.

### P9 — Separador órfão nos selos de origem (COS, observado)

`.inicio-origem` é `inline-block` com `::before { content: "· " }`. Quando quebra, a
linha começa com "· Registro do Ifes" (Diego a 1440 px) ou "· Calculado a partir dos
registros" (Ana a 375 px).

*Evidência:* `05-inicio-diego-1440.png` e `03-inicio-ana-375.png`.

### P10 — A entrada de demonstração é dominada pelo painel fictício (IMP de demonstração, observado)

A 1440 px, 13 linhas de credenciais com botão de 2 linhas cada levam a página a 2.601 px.
Não é produto, mas qualquer captura ou sessão de checkpoint vê essa página como "a
entrada do Portal". Isso contamina a percepção de quem avalia.

### P11 — Não há impedimento técnico (IMP, observado)

Não há pipeline de estáticos: o CSS é embutido via `{% include %}`. Uma camada visual do
Portal entra da mesma forma, sem dependência nova, sem JavaScript e sem backend novo. O
card já é servido em SVG e PNG.

A restrição técnica real está em outro lugar. o shell de `/acesso/` e das seções tem HTML protegido por
teste de igualdade (`test_shell_sem_navegacao_identico`, em `tests/portal/test_navegacao.py`,
contra `tests/portal/referencia_shell.html`), e a 024 SC-007 fixa a altura do shell nas
Seções. Além disso, a
Minha trajetória e o Meu e-mail existem também com o Portal desligado (`TRAJETORIA_PORTAL=0`).
O Portal precisa de um **base próprio** que não toque `interface/base.html`.

## 5. Avaliação da página pública

| Pergunta do escopo | Resposta | Base |
|---|---|---|
| Comunica a proposta de valor? | Não. Não há texto de proposta | P1 |
| Explica os benefícios? | Não | P1 |
| Desperta interesse em entrar? | Não há elemento para isso | P1 |
| Identidade institucional adequada? | Correta (assinatura oficial, regras da 015), mas mínima | P7 |
| Composição contemporânea? | Não há composição: é um formulário | P1, P2 |
| A autenticação deve ser o conteúdo principal? | Não. Ela deve ser a ação que fecha a página | — |

A recomendação é **reconceber, não restilizar**. Ao fazer isso, três restrições
registradas continuam válidas:

- A 018 veda apresentar a entrada como login, conta ou "acesso seguro". "Entrar no
  Portal" passa; "Acessar minha conta" não.
- Nada de área de fachada (024 FR-021). **Atualização 2026-10-09:** Oportunidades agora
  existe (025, só na demonstração). A página pública ainda não deve prometê-la como
  benefício garantido, porque o bloco só aparece com oportunidade pertinente publicada.
- O slogan "Sua história com o Ifes continua" **não está no repositório nem aprovado**. O
  nome "Portal do Egresso" é provisório (D2) e a linguagem definitiva é DP-801. Os dois
  dependem da ACS.

## 6. Avaliação da área autenticada

| Critério | Situação | Base |
|---|---|---|
| Personalização | Boa no conteúdo (formações, unidade, ano, proveniência); nula na forma | P2 |
| Destaque da trajetória | Fraco: o h1 promete história e entrega um registro | P5 |
| Card e vídeo | Card só como link; vídeo condicionado ao renderizador | P4 |
| Organização das funcionalidades | Lista de links iguais | P4 |
| Ações pendentes | O convite fica no fim (correto pela 024), mas no desktop sai da primeira tela | P3 |
| Relacionamento × pesquisa | Certo na ordem do Início; ambíguo na navegação | P8 |
| Uso do espaço no desktop | 44–50% a 1280–1440 px | P2 |
| Clareza da navegação | Boa: links visíveis, `aria-current`, sem menu escondido | — |
| Pertencimento institucional | Hipótese: baixo, pela imagem genérica e pelo azul PDG | P6, P7 |

Resposta à pergunta central: hoje o Início se comporta como **uma ficha seguida de uma
lista de funcionalidades**. O conteúdo para um portal de relacionamento já existe no
sistema, mas está noutra página (P5).

## 7. Desktop e responsividade

- **Desktop (1024–1440):** sem layout próprio (P2). A primeira tela não cumpre o papel do
  Início (P3).
- **Tablet (768):** idêntico ao desktop, com a coluna em 83%. Não é ruim, só é
  indistinto.
- **Celular (375):** a melhor das larguras, porque é a largura para a qual foi
  desenhado. Problemas já registrados que continuam:
  - convite a cerca de 1,6 tela;
  - navegação quebrando linha (A5);
  - "Em 2022… Há 3 anos" (A8).

  Com fonte a 200% e 320 px, a navegação ocupa 4 linhas.
- **Instrumento (`08-*`):** coerente com a decisão mobile-first. Fora de escopo e sem
  alteração recomendada.

## 8. Referências e a visão original

**O que o roadmap fez com o protótipo.** Pelo registro do próprio roadmap:

- adotou a legenda "Registro institucional × declarado" ("o melhor elemento do mockup");
- reabriu o veto a "hero, faixas, cartões" **apenas** para a abertura ilustrada;
- vetou a saudação "Olá, Marina", a "Memória do campus", a estimativa "cerca de 3
  minutos", o "Atualize" fora do instrumento e os três estilos de retrato.

A distância entre o protótipo e o produto é, portanto, **documentada e intencional**.
Não houve deriva.

**IFRN.** A auditoria de 2026-10-03 examinou 10 páginas do IFRN e decidiu, padrão a
padrão, o que adotar. Adotou as superfícies tonais sem sombra, o fio de marca e o link
verde sublinhado. Não adotou os cards em grade, o hero, o mega-menu e a falta de largura
máxima, com a justificativa "não há catálogo; produto de tarefa".

Essas rejeições estão certas para o instrumento. Para o Portal, a premissa mudou: ele é
em parte superfície de navegação, como a própria 024 reconhece em FR-026. Os princípios
do IFRN que passam a valer para o Portal:

- contraste forte entre título e corpo;
- superfícies tonais para agrupar sem sombra;
- grade com largura máxima (e não sem largura máxima, que era o erro do IFRN);
- fotografia como portadora de identidade.

**GOV.BR.** Manter o que a auditoria já decidiu: adotar princípios (hierarquia de ações,
base 8, mensagens redundantes), não clonar Rawline, botões em pílula nem caixa alta. A
barra gov.br e o VLibras continuam sendo decisão D-02.

## 9. Decisões registradas que um redesenho precisa revogar ou delimitar

Esta é a seção mais importante. Sem tratar cada linha, protótipo e implementação vão
colidir com specs vigentes.

| # | Decisão vigente | Onde | Proposta |
|---|---|---|---|
| R1 | Coluna única de 40 rem; um breakpoint de 480 px | Auditoria §13 ("para a jornada"); 015 FR-007; 024 research | **Delimitar:** vale para o instrumento e para `/acesso/`. O Portal ganha um container próprio (ex.: 72 rem) com grade e breakpoints adicionais. Texto corrido continua limitado a cerca de 70 caracteres |
| R2 | Sem cards, sem grade de cartões, sem hero | Auditoria §13 e §20; 015 FR-008; 024 FR-026 | **Revogar para o Portal**, com motivo: superfície de navegação e relacionamento. Manter para o instrumento |
| R3 | Sem tokens novos | 024 FR-026 | **Revogar para o Portal:** uma camada de tokens do Portal (superfícies, tamanho de display, espaçamentos maiores) sobre os da 015, sem alterar os existentes |
| R4 | Desktop não é presumido como ambiente principal | Constituição XXI ("a jornada do egresso") | **Interpretar, não emendar:** composição conduzida pelo desktop é compatível se o celular tiver a mesma qualidade e critérios medidos nas duas pontas. Se a CPAEG entender que "jornada" inclui o Portal, registrar a interpretação na Constituição |
| R5 | `system-ui`; Open Sans é a fonte da marca, não da interface; sem fonte externa nem CDN | Auditoria; 015 FR-005, FR-018 | **Decidir:** manter `system-ui`, ou usar Open Sans **auto-hospedada** (já está no repositório, licença OFL, em `narrativa/fontes`) só nos títulos do Portal. Nenhuma das duas opções viola o veto a CDN |
| R6 | Cor de ação provisória (azul PDG) | 015 FR-014, D-02 | **Decidir D-02.** A Direção A (verde `#195128`, 9,3:1) é a recomendada desde a 015 e é o meio mais barato de dar identidade Ifes ao Portal |
| R7 | Fotografias só com licença; memória do campus e fotos do período vetadas | 021 FR-076; DP-2106; roadmap | **Manter o veto à nostalgia; destravar a fotografia institucional:** um conjunto licenciado pela ACS (unidades, ambientes, pessoas com autorização de uso). Até lá, nenhuma legenda com nome de unidade sobre imagem genérica (P6) |
| R8 | Sem nome nem saudação no Início; vocabulário vedado ("conectad", "Oportunidade", "comunidade", "Olá"…). **Atualização 2026-10-09:** "Oportunidade" passou a ser admitida só dentro do bloco da 025 | 024 FR-019; contracts/inicio.md; 025 FR-021 | **Manter.** A proposta externa de "boas-vindas personalizadas" e "Continue conectado" colide com essas regras, e as regras têm motivo: o nome pode faltar (DP-2103) e não há área de fachada. Personalizar pelo contexto da formação, não pelo nome |
| R9 | Não há página pública; a entrada é a rota de identificação | Roadmap; 024 R2 | **Abrir escopo:** página pública só de conteúdo, sem regra de negócio nova. Respeitar a 018 (não é login nem conta) |
| R10 | Ordem do Início: reconhecimento → proveniência → ações → convite | 024 FR-016 | **Manter a ordem de leitura (DOM).** Uma coluna lateral pode antecipar visualmente a pendência no desktop; decidir se isso viola o espírito de "pesquisa por último" |

## 10. Duas direções visuais

Nas duas: a assinatura oficial sem alteração, o foco da 015, alvos de 44 px, nenhum
JavaScript obrigatório, nenhuma dependência nova e o instrumento intocado.

### Direção A — Institucional contemporânea

**Conceito.** O Portal como página do Ifes. Rigor, clareza e uma grade editorial,
próximo dos portais IF modernos, mas com largura máxima e contraste AA.

**Página pública.**
- Cabeçalho em largura total (fundo branco e fio verde), com conteúdo num container de
  72 rem.
- Hero dividido: à esquerda, h1 com a proposta, parágrafo e botão "Entrar no Portal";
  à direita, uma fotografia institucional licenciada.
- Abaixo, uma faixa de três blocos ("Sua trajetória", "Seu card", "Contato com o Ifes")
  e uma seção "Sua voz importa" explicando o acompanhamento.
- Rodapé institucional.

**Início.**
- Faixa de abertura com a fotografia da unidade da primeira formação, recortada larga e
  baixa (cerca de 240 px, contra 380 hoje), e o h1 sobre fundo tonal.
- Grade 8/4: à esquerda, formações e proveniência; à direita, ações em blocos.
- Convite em bloco de destaque no fim da coluna principal.

**Tipografia.** `system-ui`, com a escala da 015 acrescida de um display de 40/700 só no
h1 do Portal.

**Cor.** Direção A da 015 (ação verde), superfícies tonais verdes e branco dominante.

**Imagens.** Fotografia institucional licenciada; sem ilustração.

**Componentes.** Bloco de ação (título, uma linha de descrição, link), superfície tonal
e hero dividido.

**Navegação.** A mesma, horizontal, alinhada ao container largo.

**Pontos fortes.**
- Reconhecível como Ifes.
- Baixo risco de acessibilidade.
- Menor esforço.
- Reaproveita quase todo o vocabulário visual da 015.

**Limitações.**
- Depende das fotos da ACS para não parecer vazia.
- Pode continuar parecendo um site institucional, e não uma relação pessoal.
- A trajetória continua secundária.

### Direção B — Relacionamento e trajetória

**Conceito.** O Portal como o lugar da sua história com o Ifes. A trajetória e o card são
os protagonistas; a instituição aparece como quem reconhece.

**Página pública.**
- Hero com a proposta e um **card de exemplo**, identificado como exemplo, como objeto
  visual principal.
- Seção "Como funciona" em 3 passos (confirmar dados, ver sua trajetória, compartilhar).
- Seções "Reviva sua formação" (prévia de capítulos com números fictícios marcados como
  exemplo) e "Sua voz importa".

**Início.**
- Faixa de trajetória em largura total, com fundo `#0e3b23` (a paleta do card). Nela, a
  linha do tempo das formações em horizontal no desktop e os números "Naquele ano no
  Ifes".
- Abaixo, grade 8/4: à esquerda, a prévia do card (o SVG que já existe) com
  "Baixar/Compartilhar" e o link para a trajetória completa; à direita, pendências
  (convite) e contato.

**Tipografia.** Open Sans auto-hospedada nos títulos (a mesma do card, o que cria
continuidade entre a tela e a imagem compartilhada) e `system-ui` no corpo.

**Cor.** Verde-escuro do card como superfície de destaque e creme `#f6f2e8` como fundo
secundário; ação na Direção A.

**Imagens.** O card e a linha do tempo fazem o papel de imagem; a fotografia é opcional.

**Componentes.** Faixa de trajetória, prévia do card, bloco de pendência e linha do tempo
horizontal.

**Pontos fortes.**
- Torna visível o que o sistema já produz de mais forte.
- Funciona antes das fotos da ACS.
- Diferencia o Portal de um site institucional.

**Limitações.**
- Mais esforço.
- Leva a paleta do card (feita para imagem) para a interface, o que exige novos testes
  de contraste.
- Risco de redundância com a Minha trajetória (decidir o que fica só lá).
- Com uma única formação, a linha do tempo é magra (o caso da Ana).

## 11. Recomendação

**Uma combinação: a estrutura da A e o protagonismo da B, nesta ordem de dependência.**

1. **Da A:**
   - container de 72 rem;
   - cabeçalho largo;
   - grade 8/4 a partir de 1024 px e coluna única abaixo de 768 px;
   - Direção A da cor de ação (decidir D-02);
   - fotografia institucional quando a ACS liberar.

   É a base, e sem ela nada da B se sustenta no desktop.
2. **Da B, só no Início:**
   - a prévia do card na primeira tela (P4);
   - os números "Naquele ano no Ifes" e a linha do tempo antecipados da Minha trajetória
     (P5).

   Não levar a paleta escura do card para a interface inteira; ela entra como uma faixa.
3. **Página pública:** estrutura da A (proposta, três blocos, "Sua voz importa", entrada)
   com o card de exemplo da B como imagem principal enquanto não há fotografia.

Por que não a B pura: ela muda mais coisas de uma vez (fonte, paleta e componentes), e o
ganho principal dela, o card visível, cabe na estrutura da A. Por que não a A pura: com a
ilustração genérica no lugar da foto, a A desktop seria um portal institucional vazio,
que é exatamente a crítica de hoje.

Os protótipos de alta fidelidade devem mostrar as duas direções puras e a combinação,
nas duas telas, a 1440, 1024 e 375 px, para a decisão ser visual e não textual.

## 12. Priorização

| # | Problema | Classe | Experiência | Percepção institucional | Esforço | Dependência | Prioridade |
|---|---|---|---|---|---|---|---|
| P1 | Sem página pública | C | Alto | Alto | Médio | R9; textos da ACS | **Altíssima** |
| P2 | Coluna do instrumento no Portal | AI/ID | Alto | Alto | Médio | R1–R3; base próprio do Portal | **Altíssima** (é a base) |
| P3 | Primeira tela desktop sem fatos nem ações | AI | Alto | Médio | Baixo após P2 | P2 | Alta |
| P5 | Melhor conteúdo fora do Início | C/AI | Alto | Médio | Médio | P2; decidir redundância | Alta |
| P4 | Ações como links iguais | AI | Médio | Médio | Baixo | P2 | Alta |
| P7 | Pouca identidade Ifes (azul PDG) | ID | Médio | Alto | Baixíssimo (2 tokens) | D-02 | Alta, decisão imediata |
| P6 | Ilustração genérica com nome de unidade | ID | Baixo | Alto | Baixo (legenda) a alto (fotos) | DP-2106 / ACS | Alta (legenda); fotos em paralelo |
| P8 | "Pesquisa" na navegação | AI | Médio | Médio | Baixo | R10; Checkpoint 1 | Média (testar antes) |
| P10 | Painel fictício domina a entrada | IMP (demo) | Médio (para quem avalia) | Médio | Baixo | — | Média |
| P9 | Separador órfão | COS | Baixo | Baixo | Baixíssimo | — | Baixa |

## 13. Plano incremental (Etapa 3, depois dos protótipos aprovados)

Cada item é uma feature pequena, com captura a 1440/1280/1024/768/375 comparada ao
protótipo aprovado como parte da revisão.

0. **Decisões (sem código):**
   - R1–R10;
   - D-02;
   - pedido de fotos licenciadas à ACS (DP-2106);
   - texto da proposta de valor (ACS/CPAEG).

   Registrar numa spec de revisão da 015 e da 024, ou numa ADR de "camada visual do
   Portal".
1. **Base do Portal:**
   - `portal/base.html` próprio, com container largo, cabeçalho largo e tokens do Portal
     incluídos depois dos da 015;
   - Início, Minha trajetória, Meu e-mail e `/entrar/` passam a usá-lo quando o Portal
     está ligado;
   - `interface/base.html` e o teste `referencia_shell.html` ficam intactos.

   Sem mudança de view além da escolha do template.
2. **Página pública:**
   - `/` sem sessão passa a renderizar a página em vez de redirecionar;
   - `/entrar/` continua igual;
   - só conteúdo e o card de exemplo.
3. **Início:** grade 8/4, prévia do card (`card.svg` existente), faixa de trajetória e
   ações em blocos, com a ordem de leitura da 024 preservada.
4. **Entrada:** `/entrar/` no base novo; painel fictício recolhido num `<details>` ou numa
   rota própria de demonstração (P10).
5. **Harmonização:** Minha trajetória e Meu e-mail na grade nova, decidindo o que deixa de
   se repetir em relação ao Início.
6. **Acabamento:** responsividade, fonte a 200%, revisão perceptiva da ACS/CPAEG
   (015 FR-043) e P9.

**Coordenação com a 025 (Oportunidades).** As tasks da 025 mexem no Início ("compactação
sem perda"), e a implementação ainda não está autorizada. Decidir a ordem é necessário:
ou o passo 1 vem antes da 025, ou a 025 é implementada no shell atual e o passo 3 a
absorve. Fazer as duas em paralelo no mesmo template vai gerar retrabalho.

**Atualização 2026-10-09:** resolvido pelos fatos. A 025 foi implementada no shell atual
(PR #49), então o passo 3 absorve o bloco `section.inicio-oportunidades` e as variantes de
compactação (`compacto-1` a `compacto-3`, em `portal/inicio.css`). O passo 5 inclui
`/oportunidades/` na harmonização.

O plano não inclui backend novo, modelo, API, dependência Python, fila, framework de CSS
ou JavaScript obrigatório. Também não inclui funcionalidade nova.

## 14. Critérios objetivos de aceitação

**Página pública**
- A 1280×720, descontada a faixa de demonstração, sem rolar: o h1 da proposta de valor e
  a ação de entrar.
- O formulário de identificação não é o h1 de `/`.
- Nenhum link para área inexistente (024 FR-021).
- Nenhum termo de login, conta ou "acesso seguro" (018).

**Início**
- A 1440×900 e a 1280×720, descontada a faixa: o h1, o primeiro fato de reconhecimento e
  a prévia do card ou a ação principal.
- A 375×812: h1 e primeiro fato (024 FR-032 continua valendo).
- A ordem de leitura (DOM) continua a da 024 FR-016.

**Composição**
- Entre 1280 e 1440 px, a área de conteúdo tem pelo menos 1000 px.
- Nenhum bloco de texto corrido passa de cerca de 75 caracteres por linha.
- A partir de 1024 px há pelo menos duas colunas no Início; abaixo de 768 px, uma.

**Responsividade e acessibilidade**
- Sem rolagem horizontal de 320 a 1440 px, com fonte de 100% a 200%.
- Alvos ≥ 44×44 px.
- Contraste AA nos tokens novos, medido e registrado como na 015.
- Foco da 015.
- Um h1 por página.
- Nada comunicado só por cor.
- Funciona sem JavaScript.

**Fronteira**
- `tests/portal/referencia_shell.html` continua passando sem alteração.
- Nenhuma tela ou toque a mais no caminho do convite (024 SC-002).
- Sem dependência nova, CDN ou fonte externa.

**Revisão visual**
- O PR traz as capturas nas cinco larguras, lado a lado com o protótipo aprovado.

**Identidade**
- A assinatura sem alteração (015 FR-017).
- Nenhuma imagem genérica legendada com nome de unidade.

## 15. Decisões que precisam de aprovação antes dos protótipos

1. **Delimitar a 015 ao instrumento** e criar uma camada visual do Portal (R1, R2, R3).
   Ou seja: aceitar que o Portal e o instrumento têm padrões de layout diferentes sob a
   mesma identidade.
2. **Leitura da Constituição XXI** para o Portal (R4): interpretar ou emendar.
3. **D-02**: Direção A (verde) como cor de ação, ao menos no Portal.
4. **Fonte** (R5): `system-ui` em tudo, ou Open Sans auto-hospedada nos títulos do
   Portal.
5. **Fotografia institucional** (R7): pedir à ACS um conjunto licenciado e definir a
   regra de legenda até ele chegar.
6. **Página pública** (R9): abrir o escopo e definir quem aprova a proposta de valor e o
   slogan (ACS, D2 e DP-801).
7. **Vocabulário e saudação** (R8): confirmar que as vedações da 024 continuam valendo.
   Isso rejeita "boas-vindas personalizadas pelo nome" e "Continue conectado" na
   proposta externa.
8. **Pendência no desktop** (R10): pode ser antecipada visualmente numa coluna lateral?
9. ~~**Ordem em relação à 025**: base do Portal antes ou depois da implementação de
   Oportunidades.~~ **Atualização 2026-10-09:** resolvida, a 025 veio antes (§13).
10. **Escopo dos protótipos**: A, B e a combinação; duas telas; 1440, 1024 e 375 px.
