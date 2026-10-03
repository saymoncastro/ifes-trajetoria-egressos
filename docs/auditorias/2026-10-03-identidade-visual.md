# Auditoria de identidade visual — Trajetória Ifes

Data: 2026-10-03 · Base: `main` em `c7e9bd2` (após a Feature 014, PR #21)

Nada foi implementado; este documento é só diagnóstico e direção. É a quarta lente sobre a
interface do egresso e **não refaz** as anteriores:

1. [usabilidade da Feature 008](2026-10-01-ux-feature-008.md);
2. [identidade da experiência](2026-10-02-identidade-da-experiencia.md) (narrativa, voz,
   relação com o Ifes);
3. [mobile-first](2026-10-03-mobile-first-experiencia.md);
4. [Feature 014](../../specs/014-polish-jornada-egresso/spec.md), que consolidou as três;
5. esta: **como o Trajetória Ifes deve _parecer_ para ser reconhecido como um produto
   digital moderno, acessível e inequivocamente institucional do Ifes — com a menor
   linguagem visual necessária.**

**Convenções.** Nível de evidência: **[A]** observado na aplicação em execução (estilo
computado ou captura); **[C]** inspeção de código/CSS; **[R]** referência externa
consultada (URL e data); **[I]** interpretação desta auditoria. Achados **IV-nn** com
severidade **IV-CRÍTICO / IV-ALTO / IV-MÉDIO / IV-BAIXO / IV-PRESERVAR**. Nas fontes
externas: **[NORMA]** regra com fonte normativa; **[BOA PRÁTICA]** recomendação.

---

## 1. Resumo executivo

**O Trajetória hoje não parece um produto do Ifes.** Parece um formulário público
competente e acessível de _qualquer_ governo. A ausência de identidade é **deliberada e
documentada**: a folha de estilo declara-se "neutra e sóbria; sem identidade
institucional presumida (DP-801)" [C], e a 008 registrou a identidade visual definitiva
como decisão pendente (008/DP-801). O resultado, porém, não é neutro: a cor dominante é
um azul-marinho `#1a4480` sem origem no Ifes [C], o foco segue o padrão do GOV.UK
(preto + amarelo) e o cabeçalho é a palavra "Trajetória Ifes" em 16 px, do mesmo peso do
nome da pessoa ao lado [A]. Não há marca, não há verde, não há assinatura.

**O que já está bom é muito — e é a base certa.** A interface tem uma disciplina rara:
9 cores no total, 5 tamanhos de fonte, nenhuma sombra, nenhum card gratuito, nenhuma
biblioteca, contraste AA documentado, foco visível forte, alvos de 44 px, coluna única de
40 rem, nenhuma rolagem horizontal de 320 a 1280 px, e uma hierarquia de ações no rodapé
da Seção (014) que funciona [A]. Comparado aos portais de referência, o Trajetória é
**mais acessível** que o portal do IFRN (sem foco visível, botão primário a 2,67:1) e que
o portal do Ifes (sem foco visível, links a 3,89:1) [R]. **A identidade deve ser
acrescentada sem perder nada disso.**

**Onde a identidade se perde (principais achados):**

1. **IV-01 (CRÍTICO)** — o shell não tem nenhum sinal institucional do Ifes.
2. **IV-02 (ALTO)** — um azul sem origem faz ao mesmo tempo papel de marca, de ação, de
   contexto e de pendência; a 014 o chama de "azul institucional", mas ele não é do Ifes.
3. **IV-03 (ALTO)** — na pendência, a frase por Pergunta continua **vermelha** (a cor do
   erro), embora a 014 tenha decidido que pendência não é erro.
4. **IV-04 (ALTO)** — o questionário não tem ritmo: enunciado, opções e texto auxiliar
   diferem só por peso, e o espaço entre perguntas (28 px) é menor que a altura de uma
   linha de opção (44 px); 14 perguntas viram uma lista contínua.
5. **IV-05 (ALTO)** — três shells diferentes (jornada, editor, acompanhamento) e páginas
   de erro sem shell.

**Direção recomendada, em uma frase:** _um produto branco, calmo e tipográfico, em que o
verde do Ifes aparece onde o Ifes fala ou age — assinatura oficial no topo, fio de marca,
voz institucional (contexto da formação) e ação principal — e em nenhum outro lugar;
azul para informação/pendência, vermelho para erro, neutros para todo o resto._ A cor
da ação fica num token próprio: verde Ifes (Direção A) ou a cor do Padrão Digital de
Governo (Direção B), conforme o esclarecimento institucional de D-02 (seção 8).

A recomendação **não** é aumentar a quantidade de verde. É dar ao verde **um significado**
e tirar o azul do papel de marca que ele ocupa por acaso.

**Menor linguagem visual necessária:** 13 tokens de cor (8 já existem),
5 tamanhos de fonte (já existem), 7 passos de espaçamento, 2 larguras de container,
1 raio, 3 espessuras de borda, 0 sombras, 0 ou 3 ícones. Nenhuma dependência nova,
nenhuma fonte externa, nenhum framework.

**Gate:** aplicar essas foundations a 4 telas existentes (trajetória, Seção típica, Seção
com pendência/erro, conclusão/confirmação) e só propagar depois de validar mobile e
desktop **e** de obter a decisão institucional sobre marca e cor (DP-801).

---

## 2. Escopo e limites

**Dentro:** shell (cabeçalho, rodapé), trajetória, Seção (perguntas, controles, escala,
contexto, resumo de pendência/erro, rodapé de ações), conclusão, confirmação, avisos,
páginas de estado e de erro; tokens e foundations; benchmark IFRN; marca Ifes; padrão
GOV.BR como referência de robustez.

**Telas administrativas** (editor 009, acompanhamento 011, demonstração): inspecionadas
**só** para identificar shell e CSS compartilhados. Recomendação administrativa aparece
apenas quando (1) o componente é compartilhado, (2) o problema está no shell comum ou
(3) a mudança visual pode causar regressão transversal — e está marcada como tal.

**Fora (não reaberto):** tudo o que a 014 decidiu funcionalmente — quatro ações do
rodapé, pendência × erro, regra de verdade do salvamento, "Salvar e sair", "Sair sem
salvar esta seção", arquitetura e ordem da trajetória, 44 px, forma funcional da escala,
ramificação, validação, política sem JavaScript, retomada, instrumento; DP-307, DP-406,
DP-702, DP-802, DP-803. Esta auditoria diz **como devem parecer**, não **se** existem nem
**como** funcionam. Questões que parecem funcionais estão na seção 29.

---

## 3. Método

1. Leitura da Constituição (Posicionamento; XIV, XX, XXI, XXII, XXIII, XXIX), da 008
   (DP-801; research R13, R14), da 014 completa (spec, plan, research R1–R13, contratos
   `telas.md` e `rodape-secao.md`, quickstart) e das três auditorias anteriores.
2. Inspeção de todos os templates da jornada, das três folhas de estilo
   (`interface/estilo.css`, 162 linhas; `editor/estilo.css`, 35; `acompanhamento/estilo.css`,
   27) e dos templates base do editor, do acompanhamento e da demonstração [C].
3. Execução da aplicação com banco dedicado (`trajetoria_visual`) **só com dados
   fictícios** do cenário de demonstração (`preparar_demonstracao`).
4. Jornadas percorridas no navegador (Chromium, viewport emulada) [A]:
   - **Ana** (uma formação): trajetória a 390 e 430 px;
   - **Maria** (duas formações, escolha): trajetória; Seção 1 (Termos); Seção 2 em
     **pendência** (1 de 8 respondida); Seção 3 (lista suspensa); Seção 8 "Avaliação"
     (14 perguntas, 2 escalas, "Outro") com **erro de forma**; Seção 13 sem título;
     **conclusão**; **confirmação**; trajetória com "Pesquisa já respondida";
   - **Diego** (três formações, ambiguidade): trajetória; "Salvar e sair" → aviso de
     salvamento na trajetória;
   - larguras: 375, 390, 430 e 1280 px;
   - estilo computado (`getComputedStyle`) de cabeçalho, títulos, corpo, enunciados,
     controles, escala, botões, resumo, contexto, rodapé;
   - shell do editor, do acompanhamento e da escolha de operador (só identificação).
5. Benchmark IFRN (10 páginas de 6 tipos, desktop 1366 px e mobile 390 px, estilos
   computados e variáveis CSS) e consulta ao Manual da Marca IF, ao portal e às normas
   do Ifes, ao Padrão Digital de Governo e à legislação — seções 6 a 8 [R].
6. Contraste calculado pela fórmula da WCAG 2.x para cada cor proposta.
7. Revisão crítica (seção 30 do pedido): recomendações sem evidência ou que fossem gosto
   pessoal foram removidas ou rebaixadas a "a validar na PoC".

**Limites.** Sem aparelho real (iOS/Android); sem alto contraste do sistema; leitores de
tela não testados (não é o foco). O cabeçalho e a faixa de demonstração não existirão em
produção; as medidas de "primeira tela" os descontam, como na 014.

---

## 4. Baseline pós-014

A 014 é tratada como **baseline funcional**. O que dela importa visualmente:

| Elemento da 014 | Como está hoje [A/C] | Posição desta auditoria |
|---|---|---|
| Título principal = título da Seção | `h1` 28 px/700 | Preservar; ver IV-04 para o ritmo abaixo dele |
| "Você está respondendo sobre:" | faixa `#f5f7fa`, fio esquerdo 4 px `#1a4480`, 16 px | Preservar a **forma**; trocar o **token** de cor (IV-02) |
| Resumo de erro × pendência | mesma caixa 3 px; vermelho × azul; títulos distintos | Preservar a estrutura; corrigir a cor por Pergunta (IV-03) |
| Rodapé: primário / secundário / terciárias | preenchido / contorno / links com nota, divisor e ≥ 32 px; largura total ≤ 480 px | **Preservar** (IV-P1) |
| Linha e célula inteiras tocáveis; escala em grade | `label::after` cobrindo a área; colunas `minmax(44px,1fr)` | Preservar a mecânica; dar forma visível à área (IV-07) |
| Trajetória compacta | linha principal em negrito + complemento 15 px | Refinar o item (IV-09) sem mudar conteúdo nem ordem |
| Confirmação com um agradecimento | `h1` "Pesquisa concluída" + parágrafos | Dar sinal visual de conclusão (IV-06) |
| CSS restrito à jornada (FR-045) | classes próprias (`.acoes-secao`, `.saidas`) | Manter a mesma regra para tudo o que vier |

---

## 5. Estado visual atual

### 5.1 Inventário medido

| Dimensão | Valores encontrados [C, confirmados em A] |
|---|---|
| Fonte | `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`; base 16 px, entrelinha 1,5 |
| Tamanhos | 28 (h1) · 22 (h2) · 18 (h3, título do resumo, título do contexto) · 16 (corpo, enunciado, opções, botões) · 15 (`.nota`, rodapé) |
| Pesos | 400 · 600 (enunciados, botões, `dt`) · 700 (h1, nome do produto, `strong`) |
| Cores | `#1b1b1b` texto (17,2:1) · `#ffffff` fundo · `#1a4480` ação/link/contexto/pendência (9,6:1) · `#565c65` bordas e divisores (6,7:1) · `#b50909` erro (7,0:1) · `#f5f7fa` superfície do contexto · `#ffdd00` foco · `#fff1d2` faixa de demonstração. **Nenhum verde.** |
| Espaçamentos (rem) | 0,25 (13×) · 0,5 (24×) · 0,75 (9×) · 1 (21×) · 1,25 (6×) · 1,5 (7×) · 1,75 (4×) · 2 (5×); isolados: 0,125 · 0,625 |
| Bordas | 1 px (divisores) · 2 px (campos, botões, avisos) · 3 px (resumo, foco) · 4 px (fio lateral) — todas `#565c65`, `#1a4480` ou `#b50909` |
| Raio / sombra | 0 em tudo / nenhuma (só o anel de foco) |
| Container | jornada 40 rem (640 px); editor e acompanhamento 56 rem |
| Breakpoints | um: 480 px — escrito `30em` na jornada e `30rem` no acompanhamento |
| Ícones | nenhum |
| Controles de escolha | nativos, `accent-color: auto` (cor do sistema/navegador), 20 px |
| Alvos | botões, campos, linhas de opção: 44 px; célula da escala: 96×56 px no desktop |

### 5.2 Leitura geral

- **Sistema pequeno e coerente** — o problema não é excesso, é **falta de significado**:
  os valores existem, mas não carregam marca nem semântica.
- **Linguagem "GOV.UK"**: cantos retos, bordas escuras de 2 px, foco preto e amarelo,
  azul-marinho. É robusta e legível, mas é a gramática de outro governo; daí a sensação
  de "formulário genérico de serviço público".
- **Não parece "Django estilizado" no sentido pejorativo** (não há tabelas de admin, nem
  Bootstrap padrão, nem mensagens do framework). O que ainda lembra template é o
  **cabeçalho tipográfico mínimo** e os **divisores cinza-escuros** repetidos
  (cabeçalho, listas, saídas, rodapé), que dão aparência de documento HTML puro.
- **Não parece SaaS** — e não deve passar a parecer.

---

## 6. Identidade institucional do Ifes

### 6.1 O que é regra [R, consultado em 2026-10-03]

| Fonte | O que determina | Natureza |
|---|---|---|
| **Manual de Aplicação da Marca Instituto Federal, 3ª ed. (2015)** — instituído pela Portaria Setec/MEC nº 31/2015 — <https://redefederal.mec.gov.br/images/pdf/manual.pdf> | Símbolo (módulos + círculo) e assinaturas horizontal/vertical; **verde** RGB 50/160/65 (HEX publicado `#2f9e41`; o RGB converte para `#32a041` — discrepância do próprio manual), **vermelho** RGB 200/25/30 (HEX publicado `#cd191e`), preto; tipografia da marca **Open Sans** (Bold e Regular); área de proteção ≥ 1 módulo *x*; **redução mínima do símbolo 30 px**; versões monocromática, negativa, cinza; proibido distorcer, recolorir, contornar, estilizar, emoldurar, **criar novas aplicações** (composições não previstas); em fundo colorido, a marca vai sobre base branca; distância de 3*x* para marcas externas | [NORMA] |
| **Portaria Ifes nº 1.818/2012** ("Diretriz de criação de marcas"), via <https://www.ifes.edu.br/manuais-de-comunicacao> | Estruturas permanentes usam a marca do campus ou da Reitoria; **marcas setoriais não são atendidas**; programas, projetos e eventos **podem** ter marca própria **sem dispensar** a marca do campus/Reitoria; ações de mais de um campus usam a marca da **Reitoria** | [NORMA interna] |
| **Download de marcas do Ifes** — <https://www.ifes.edu.br/download-de-marcas> | Marca sistêmica/Reitoria e de cada campus (cor e P&B, horizontal e vertical); remete ao Manual da Rede; contato: Assessoria de Comunicação Social (acs@ifes.edu.br) | Fonte dos arquivos oficiais |
| "Institutos Federais, a cara do Brasil" (MEC/Setec, 2023–2025) | Identidade **de campanha** (fonte Aspira, paleta multicolor) | **Não** substitui a marca IF; não usar |

Não foi encontrado manual próprio do Ifes, nem norma sobre sistemas digitais ou sobre o
padrão "Nome do sistema + Ifes" [R].

### 6.2 O que o Ifes faz na prática digital [R, portal inspecionado em 2026-10-03]

- `www.ifes.edu.br`: Joomla 3 com o tema "Portal Padrão" (IDG v1) do Governo Federal;
  barra gov.br; Open Sans; cabeçalho verde-escuro **`#195128`** (9,34:1 com branco);
  faixa e rodapé `#00420c`; **não usa o verde puro da marca na interface**; nome
  "Ifes" em texto, sem o símbolo; **sem foco visível**; links `#0088cc` a 3,89:1.
- Sistemas listados em <https://www.ifes.edu.br/sistemas> (família SIG, Gedoc, Moodle)
  usam o nome do produto, sem marca de produto própria.

### 6.3 Interpretação para o Trajetória [I]

1. **O verde da marca não serve para texto nem para botão com texto branco**: `#2f9e41`
   tem 3,45:1. Serve para elementos gráficos (≥ 3:1, WCAG 1.4.11). Toda cor de **ação**
   precisa ser um verde mais escuro. O próprio Ifes já resolve isso com `#195128`:
   adotá-lo é **coerência com o Ifes**, não invenção.
2. **O vermelho da marca pertence ao círculo do símbolo.** Na interface ele colidiria
   com o vermelho de erro; deve aparecer **só dentro da marca**.
3. **"Trajetória Ifes" deve ser nome de produto em texto, não logotipo.** A Portaria
   1.818 admitiria marca de projeto, mas criar uma exigiria aprovação da ACS e competiria
   com a marca institucional — o oposto do pedido. Texto + assinatura oficial resolve.
4. **Assinatura a usar:** a da **Reitoria/sistêmica**, porque o produto atende egressos
   de todos os campi (Portaria 1.818, item e). Arquivo oficial, sem redesenho, em SVG
   inline (ver dependência D-03).
5. **Open Sans é a fonte da marca, não da interface.** Ela já está "dentro" do arquivo da
   assinatura. Não há regra que obrigue a interface a usá-la.

### 6.4 Respostas às perguntas da seção 8 do pedido

| Pergunta | Resposta |
|---|---|
| Reconhecível como Ifes? | **Não.** O único sinal é a palavra "Ifes" no nome [A] |
| Marca corretamente aplicada? | Não há marca aplicada |
| Relação marca × "Trajetória Ifes" clara? | Não existe relação: só o nome do produto |
| Excesso de verde? | Não há nenhum verde |
| Ausência de sinal institucional? | **Sim** (IV-01) |
| Elementos incompatíveis com a Rede? | Nenhum incompatível; o azul e o foco amarelo são apenas alheios |
| Parece produto oficial? | Parece serviço público, não do Ifes |
| Parece legado / genérico / template / SaaS? | Genérico, sim; legado, pouco (só os divisores); template, pouco; SaaS, não |
| Competição marca × produto? | Hoje não, porque não há marca. A proposta evita criar competição (6.3, item 3) |

**Quais elementos devem carregar a institucionalidade (e só eles):** (1) assinatura
oficial no cabeçalho; (2) fio de marca no topo; (3) a "voz do Ifes" — a linha "Você está
respondendo sobre:" e a ficha da formação, que são dados que **o Ifes** apresenta;
(4) a ação principal. Perguntas, opções, campos, listas e textos continuam neutros.

---

## 7. Benchmark IFRN

Páginas examinadas em 2026-10-03, desktop 1366 px e mobile 390 px [R]:

| URL | Tipo |
|---|---|
| <https://portal.ifrn.edu.br/> | Home |
| <https://portal.ifrn.edu.br/campus/reitoria/noticias/> | Listagem de notícias |
| <https://portal.ifrn.edu.br/campus/joaocamara/noticias/voz-da-terra-abertas-as-inscricoes-para-participacao-no-evento/> | Notícia |
| <https://portal.ifrn.edu.br/cursos/buscar/> | Cursos com filtros |
| <https://portal.ifrn.edu.br/cursos/tecnicos/tecnico-integrado/informatica/> | Página de curso |
| <https://portal.ifrn.edu.br/search/?query=egressos> | Busca |
| <https://portal.ifrn.edu.br/campus/> e <https://portal.ifrn.edu.br/campus/natalcentral/> | Campi |
| <https://portal.ifrn.edu.br/processos-seletivos/buscar/> | Processos seletivos |
| <https://portal.ifrn.edu.br/institucional/> | Institucional |

### 7.1 O que torna o IFRN contemporâneo (recorrente em vários tipos de página)

- **Contraste tipográfico forte**: `h1` 40 px/800 em verde-escuro `#1e482b` contra
  títulos de card 400 — recorrente em notícias, busca, cursos, campi, PS e
  institucional. Uma família só (Inter).
- **Rampa de verde com tokens** em `:root` (50…900; primária `#357e4b`; escura
  `#1e482b`) e famílias semânticas (info, success, warning, caution, danger) —
  arquitetura de tokens, não paleta solta.
- **Superfícies tonais sem sombra**: cards separados por fundo (`#f8fcf9`, `#edf7f0`,
  `#f7f7f7`), sem borda nem sombra; a única sombra é a do menu suspenso.
- **Dois níveis de raio** (6 px itens pequenos; 20 px cards) — recorrente.
- **Fio de marca**: o cabeçalho das páginas internas tem borda superior de 3 px
  `#357e4b` — recorrente nas páginas internas.
- **Links verdes sublinhados** no corpo — recorrente.
- **Metadados em `dl`** (rótulo 13 px cinza + valor 15 px/500) em curso e PS.

### 7.2 Fraquezas independentes (não seguir)

- **Sem foco visível** em lugar nenhum: reset global `* { outline: none }` — recorrente
  (falha WCAG 2.4.7).
- **Botão primário branco sobre `#4bb26a`: 2,67:1**, com texto de 12–13,5 px —
  recorrente (falha 1.4.3).
- Status, breadcrumb e badges abaixo de 4,5:1; ícones decorativos a 1,2–1,5:1.
- Sistema tipográfico frouxo: **7 variações de `h3` numa mesma página**; `h2` de 20, 25
  ou 27,5 px conforme a página; dois `h1` por página.
- Botões sem sistema (4+ alturas; raios 5, 14, 20, 50 px e assimétricos).
- **Corpo de 15 px também no mobile**; inputs de 13 px (provocam zoom no iOS); medida de
  linha de ~100–150 caracteres; container sem largura máxima; ~32 breakpoints ad hoc.
- Hambúrguer com 24×46 px; cabeçalho de ~194 px no desktop; rodapé de ~2.000 px com
  97 links.
- **O verde faz marca, ação e decoração ao mesmo tempo**, sem cor reservada para ação.

**Conclusão do benchmark.** O IFRN parece contemporâneo pela **tipografia confiante,
superfícies tonais e tokens**, e não pelos componentes. Em acessibilidade e consistência
de componentes, o Trajetória já está **acima** do IFRN. Aprender os princípios; não
importar a implementação. Tabela de decisões na seção 20.

---

## 8. Governo Digital como referência

| Fonte [R, 2026-10-03] | Uso nesta auditoria |
|---|---|
| **Portaria SECOM/MCom nº 7.508/2022** — <https://www.in.gov.br/web/dou/-/portaria-n-7.508-de-22-de-novembro-de-2022-446087089> | Art. 2º alcança administração "direta, **autárquica** e fundacional" (IFs são autarquias) e "sistemas"; Art. 3º, IV: o Padrão Digital de Governo (gov.br/ds) "deve ser atendido"; Art. 10, III: eMAG. **[NORMA]** O portal atual do Ifes não segue o DS (IDG v1), mas isso **não constitui exceção normativa**; nenhuma exceção formal para a Rede foi encontrada. **Como a obrigação se aplica ao Trajetória deve ser esclarecido institucionalmente (D-02, DP-801)** — a 008 já listou "padrão de governo eletrônico aplicável" em DP-801 |
| **Padrão de Governo Digital (Design System)** — Guia orientativo do SISP — <https://www.gov.br/governodigital/pt-br/estrategias-e-governanca-digital/sisp/guia-do-gestor/guia-orientativo-de-padroes-e-fluxos-das-tecnologias-de-transformacao-digital/padrao-de-governo-digital-design-system> (atualizado em 19/06/2026) | Padrões de interface "que devem ser seguidos por designers e desenvolvedores"; aplicabilidade explícita a **sistemas**, portais, painéis e aplicativos **com serviços para cidadão(ã)** — categoria em que o Trajetória se enquadra **[NORMA/orientação oficial]** |
| **Padrões Web em Governo Eletrônico** — <https://www.gov.br/governodigital/pt-br/acessibilidade-e-usuario/acessibilidade-digital/padroes-web-em-governo-eletronico> | Caracteriza o Padrão Digital como de adoção obrigatória "em todos os órgãos do Poder Executivo Federal" (a página ainda cita a Portaria 540/2020, revogada e substituída pela 7.508/2022) |
| **Design System gov.br 3.7** — <https://www.gov.br/ds> (cores, tipografia, espaçamento, estados, button, input, radio, message, header, footer) | Referência de **robustez**: hierarquia primária/secundária/terciária; primária "de forma limitada", só na ação principal; botão em bloco recomendado em toque; campos com rótulo acima; mensagens com ícone + cor + texto; espaçamento em múltiplos de 8; sem cor nova sem aprovação |
| **eMAG 3.1** — <https://emag.governoeletronico.gov.br/> | 4.1 contraste; 4.2 não usar só cor; 4.3 200% sem rolagem horizontal; 4.4 foco não removido, ≥ 2 px **[NORMA]** |
| **WCAG 2.2** — <https://www.w3.org/TR/WCAG22/> | 1.4.3 (4,5:1; 3:1 texto grande), 1.4.11 (3:1 não textual), 1.4.10 (reflow 320 px), 2.4.7 (foco visível), 2.4.11 (foco não encoberto), 2.5.8 (24 px; o projeto adota 44 px) |
| ABNT NBR 17225:2025 | Baseada na WCAG 2.2; obrigatoriedade federal **não verificada** [BOA PRÁTICA] |

**O que adotar do gov.br (princípios):** hierarquia de ênfase das ações (o Trajetória já
cumpre); mensagens com três redundâncias (cor + ícone + texto); escala de espaçamento em
base 8 com meio-passo de 4; rótulo acima do campo; botão em bloco no toque.

**O que não copiar:**
- **Rawline** (fonte externa por CDN — vedada pela 008 FR-082 e R14);
- botões em pílula e cabeçalho em caixa alta (assinatura visual do gov.br — viraria
  "clone do GOV.BR");
- foco tracejado dourado `#c2850c` (3,16:1, mais fraco que o atual, de 12,8:1);
- rádio e checkbox com borda `#cccccc` (**1,61:1, falha em 1.4.11** — fragilidade do
  próprio DS);
Esses desvios são recomendações de **qualidade e proporcionalidade**; se o Padrão Digital
se aplicar integralmente ao Trajetória, cada um deles também entra na margem a esclarecer
em D-02.

**Questão a esclarecer institucionalmente (não resolvida aqui).** Há evidência normativa
de que o Padrão Digital de Governo se aplica a sistemas com serviços ao cidadão na
Administração Pública Federal, inclusive autarquias (Portaria 7.508/2022; guia oficial
acima). Antes de adotar uma cor de interação **divergente** do padrão, deve-se esclarecer
como o PDG se aplica ao Trajetória e **qual margem existe para incorporar a identidade
visual do Ifes**. A escolha não é estética, e a prática atual do portal do Ifes não é
argumento de exceção. Por isso esta auditoria mantém **duas direções** para a cor de
ação, e não uma:

- **Direção A** — ação em verde Ifes `#195128` (coerente com o portal do Ifes e com a
  prática da Rede);
- **Direção B** — ação na cor de interação prescrita pelo Padrão Digital de Governo
  (hoje `#1351b4`), com o verde Ifes restrito à marca e à voz institucional.

A PoC deve permitir alternar A e B trocando **um único token** (`cor.acao` e sua variante
forte), sem duplicar componentes nem telas. A decisão vem depois, com a PoC como insumo
(seção 30).

---

## 9. Hierarquia visual

Verificação das sete perguntas do pedido, na Seção 8 de Maria (desktop e 375 px) [A]:

| A pessoa entende… | Hoje | Observação |
|---|---|---|
| 1. Onde está | Parcialmente | `h1` da Seção é claro; o produto e a instituição não aparecem (IV-01) |
| 2. Sobre qual formação responde | Sim | A faixa de contexto funciona; é o elemento mais "institucional" da tela |
| 3. O que precisa fazer | Parcialmente | Enunciados pouco destacados das opções; perguntas sem separação (IV-04) |
| 4. Qual é a ação principal | **Sim** | Botão preenchido, largura total no mobile (IV-P1) |
| 5. Quais ações são secundárias | **Sim** | Contorno; terciárias como links abaixo do divisor (IV-P1) |
| 6. Em que ponto qualitativo da tarefa está | Parcialmente | Só o título da Seção; sem mecanismo novo (não reabrir progresso). A conclusão e a confirmação não têm sinal visual próprio (IV-06) |
| 7. O que ocorreu após a submissão | Parcialmente | Pendência e erro bem estruturados, mas com sinal de cor contraditório (IV-03); "salvo" usa o mesmo aviso cinza de qualquer outro aviso (IV-06) |

---

## 10. Tipografia

**Inventário:** ver 5.1. **Existe uma escala real** (28/22/18/16/15 px; 1,25–1,5 de
entrelinha) — pequena, sem valores arbitrários acumulados. O problema está na
**aplicação**:

- **Enunciado × opção × auxiliar**: enunciado 16 px/600; opção 16 px/400; texto
  explicativo e descrição da escala 16 px/400 na **mesma cor do corpo** [A]. A única
  diferença é o peso. Em 14 perguntas seguidas, o olho não encontra o começo de cada
  pergunta (IV-04).
- **"(obrigatória)"** em 400, colado ao enunciado: legível, mas compete com o fim da
  frase; tratar como metadado (cor secundária), sem mudar o texto.
- **Labels não competem com enunciados** (não há labels separados nas Perguntas) — ok.
- **Textos auxiliares** (`.nota`, 15 px, `#1b1b1b`): legíveis; poderiam usar a cor de
  texto secundário (`#565c65`, 6,7:1) para descer na hierarquia sem perder AA.
- **Mobile**: proporções mantidas; `h1` 28 px a 375 px ocupa 1–2 linhas — adequado.
- **Desktop**: coluna de 640 px → ~70–80 caracteres por linha a 16 px — **dentro do
  ideal** (o IFRN chega a 150).
- **Nome do produto** no cabeçalho: 16 px/700, igual ao "Pessoa fictícia: …" ao lado —
  sem hierarquia de marca (IV-05).

**Precisa trocar a fonte? Não.** Justificativa:

| Critério | `system-ui` (atual) | Open Sans (marca IF) | Rawline (gov.br) | Inter (IFRN) |
|---|---|---|---|---|
| Disponibilidade sem dependência | Sim | Exige servir arquivos (sem `staticfiles` — R14) | CDN externa (vedado — FR-082) | CDN/arquivos |
| Performance | Zero bytes | +~100–200 kB | idem | idem |
| Legibilidade em celular | Excelente (SF, Roboto, Segoe) | Boa | Boa | Excelente |
| Identidade | Neutra | Coerente com a marca | Coerente com o gov.br | Do IFRN |
| Licença | — | OFL | OFL | OFL |

A identidade virá da assinatura oficial (que já contém Open Sans), da cor e da
hierarquia — **não** da fonte de texto. Reavaliar Open Sans só se, no futuro, o produto
passar a servir estáticos por outro motivo **e** a PoC mostrar ganho real (registro em
D-04).

---

## 11. Cores

### 11.1 Mapa semântico atual [C, A]

| Papel | Cor atual | Problema |
|---|---|---|
| Brand | — (nenhuma) | Ausente |
| Interaction (botão, link) | `#1a4480` | Azul sem origem no Ifes |
| Contexto institucional (fio) | `#1a4480` | Mesma cor da ação |
| Pending (resumo, fio da Pergunta, borda do campo) | `#1a4480` | Mesma cor da ação e do contexto |
| Pending (frase por Pergunta) | **`#b50909`** | **Cor de erro** (IV-03) |
| Error | `#b50909` | Ok (7,0:1, com "Erro:" e borda) |
| Success | — | Ausente: "salvo" e "concluída" sem semântica (IV-06) |
| Information / aviso | `#565c65` (borda) | Mesma borda para sucesso, neutro e atenção |
| Text / muted | `#1b1b1b` / — | Não há texto secundário em uso |
| Border | `#565c65` | Um cinza forte para controles **e** divisores (IV-08) |
| Surface | `#f5f7fa` | Só no contexto |
| Focus | `#1b1b1b` + `#ffdd00` | **Ótimo** (IV-P2) |
| Selected / hover / active / disabled | nativo / — / — / — | Sem definição (IV-07) |

### 11.2 Diagnóstico

- **Marca e interação confundidas — com uma cor que não é da marca.** A 014 (R4)
  escolheu "borda azul institucional" para a pendência; o adjetivo está errado: o azul
  não é do Ifes. Isso não invalida a decisão funcional, só exige renomear o papel
  ("informação/pendência").
- **Feedback não depende só de cor** (erro tem "Erro:", borda e título; pendência tem
  "Falta responder:" e título próprio) — bom. Mas a cor diz o contrário do texto na
  pendência (IV-03).
- **Cinzas**: um só (`#565c65`) — consistente, mas pesado demais para divisores.
- **Não há tons demais.** Há papéis de menos.

### 11.3 Paleta funcional proposta (detalhe na seção 25)

Regra: **verde = o Ifes (marca, voz institucional, ação); azul = informação e pendência;
vermelho = erro; neutros = todo o resto.** O vermelho da marca só existe dentro da
assinatura.

---

## 12. Espaçamento e ritmo

**Extraído do CSS:** 4 · 8 · 12 · 16 · 20 · 24 · 28 · 32 px dominam; 2 px e 10 px são
isolados [C]. A escala de fato já é base 4/8.

**Ritmo do questionário (Seção 8, desktop) [A]:**

| Distância | Medida | Leitura |
|---|---|---|
| Enunciado → primeira opção | 8 px (+ auxiliar 8 px) | Ok: proximidade indica pertença |
| Opção → opção | linhas de 44 px (sem gap) | Ok para toque; visualmente, cada linha "respira" 12 px acima e abaixo do texto |
| Pergunta → pergunta | **28 px** | **Menor que a altura de uma linha de opção.** Fim e começo de perguntas se confundem (IV-04) |
| Último campo → botões | 32 px | Ok |
| Botões → terciárias | 32 px + divisor | Ok (014) |
| Contexto → primeira pergunta | 24 px | Ok |

**Princípio (Gestalt/proximidade):** o espaço entre grupos deve ser claramente maior que
o espaço dentro do grupo. Hoje é o contrário.

**Escala suficiente:** **4 / 8 / 12 / 16 / 24 / 32 / 48**. Os seis primeiros já existem;
**48** entra só para separar Perguntas (e blocos maiores). 20 e 28 px desaparecem (28
vira 48 entre perguntas; 20 vira 24 nos botões ou 16). Não é preciso mais nada.

---

## 13. Layout

- **Container 40 rem (640 px) para a jornada: manter.** É o tamanho certo para um
  produto de tarefa (o IFRN, sem largura máxima, chega a 150 cpl). Editor e
  acompanhamento: 56 rem, manter.
- **Cabeçalho e conteúdo alinhados à mesma coluna** (hoje já estão) — manter; o
  cabeçalho não deve "abrir" para a largura total com conteúdo, só com o fundo/fio.
- **Grid:** coluna única; nenhuma grade de colunas é necessária. A única grade é a da
  escala (014) — manter.
- **Largura dos campos:** 100% da coluna para texto e lista — adequado ao celular; no
  desktop, um campo de "ano" com 608 px é longo, mas encurtar exigiria tratamento por
  Pergunta (vedado pela 008 FR-034). Manter.
- **Posição das ações:** abaixo do formulário, à esquerda, empilhadas — manter (014).
- **Gutter mobile 16 px** — manter (o gov.br usa 8 mínimo, o IFRN 30).
- **Não importar do portal:** hero, aside, faixas alternadas, cards em grade, mega-menu.

---

## 14. Superfícies

| Superfície atual | Semântica? | Decisão |
|---|---|---|
| Faixa de contexto (`#f5f7fa` + fio 4 px) | **Sim** — informação institucional, separada das Perguntas (014 FR-025) | Preservar; fio e fundo passam a ser a "voz do Ifes" (verde) |
| Ficha da formação (mesma faixa com `dl`) | Sim | Preservar; corrigir o `dl` no mobile (IV-11) |
| Resumo de erro/pendência (caixa 3 px) | **Sim** — estado | Preservar a caixa; unificar a espessura de acento em 4 px |
| Aviso (caixa cinza 2 px) | Sim — mas um só tipo para tudo | Dar variantes (IV-06) |
| Item da lista (`.lista-simples`, divisores 1 px) | Sim — agrupamento | Preservar; divisor mais leve (IV-08) |
| Pergunta com erro/pendência (fio 4 px) | Sim — estado | Preservar |
| Cards | — não existem | **Não criar.** Nada no produto pede card |
| Sombras | — não existem | **Não criar** |

**Linguagem que deve predominar:** _fundo branco + fios + uma superfície tonal_. A
superfície tonal é reservada para **informação institucional** (contexto/ficha); os
estados usam **fio de acento** (4 px) com a cor do estado. Nada mais.

---

## 15. Componentes

Inventário só do que existe [C, A]:

| Família | Variantes | Consistência / estados | O que já funciona | Oportunidade |
|---|---|---|---|---|
| **Botão** | `primario` (preenchido), `secundario` (contorno), botão-link do cabeçalho | default/foco ok; **hover, active, disabled ausentes** | Hierarquia e alvo de 44 px | Hover/active por escurecimento; largura total no mobile para **toda** ação principal da jornada (IV-10) |
| **Link** | corpo, terciárias com nota, lista de Seções (44 px) | sublinhado sempre | Clareza | Cor de interação nova; hover com sublinhado mais espesso |
| **Campo de texto / lista** | 44 px, borda 2 px, raio 0 | erro (borda vermelha), pendência (borda azul) | Altura, fonte 16 px (sem zoom no iOS) | Raio 4 px (a validar); foco já forte |
| **Rádio / caixa** | nativos 20 px em linha de 44 px | `accent-color` não definido → cor do navegador | Linha inteira tocável (014) | `accent-color` = interação; estado selecionado da linha (IV-07) |
| **Escala** | grade de células ≥ 44 px, número abaixo | célula sem forma visível; selecionado só pelo ponto nativo | Mecânica e reflow (014) | Célula visível discreta e estado selecionado (IV-07) |
| **Resumo (erro/pendência)** | duas cores | **frase por Pergunta sempre vermelha** | Estrutura, foco, links | IV-03 |
| **Aviso** | um | o mesmo para salvo, saída, situação, percurso | Posição antes do `h1` | IV-06 |
| **Contexto** | compacto (Seção) e ficha (`dl`) | ficha quebra mal no mobile | Fio + fundo como "voz do Ifes" | IV-11 |
| **Item de formação** | linha principal + complemento + situação + ação | situação em negrito compete com a linha; espaçamento assimétrico | Forma compacta (014) | IV-09 |
| **Cabeçalho / rodapé** | 3 variantes de cada | inconsistentes | — | IV-05 |
| **Estado vazio** | frases ("Dados da formação não informados pela fonte.") | ok | Texto honesto | Nenhuma |

Não há (e não devem ser criados): modal, tooltip, acordeão, stepper, badge, skeleton,
dropdown customizado.

---

## 16. Questionário como experiência central

**Visualmente hoje transmite:** clareza (sim), segurança (sim — ações claras, salvamento
honesto), simplicidade (parcial), **esforço administrável (não)** — a Seção 8 tem 14
perguntas idênticas em peso e espaço, numa página longa; continuidade (parcial);
institucionalidade (não).

**Soluções somente visuais (sem fragmentar, sem esconder, sem wizard):**

1. **Separar perguntas por espaço, não por caixas**: 48 px entre Perguntas, 8 px entre
   enunciado e resposta (IV-04). É a mudança de maior efeito por linha de CSS.
2. **Enunciado em 18 px/600**, opções em 16 px/400, auxiliar em 15 px na cor
   secundária. Três níveis distinguíveis em vez de um.
3. **Opcional (validar na PoC):** fio fino neutro de 1 px entre Perguntas, só se o
   espaço sozinho não bastar a 375 px. Nunca card por Pergunta (multiplicaria bordas e
   comprimiria o conteúdo no celular).
4. **Escala com célula visível** (IV-07): mostra que cada valor é um alvo, reduz a
   sensação de "linha de bolinhas".
5. **Estado selecionado visível** na linha de opção: depois de responder, a página
   mostra o que já foi feito — sensação de avanço sem mecanismo de progresso.
6. **Contexto da formação em verde Ifes**: a pessoa lê, no topo de cada Seção, que é o
   **Ifes** que pergunta sobre **aquele** curso.

---

## 17. Shell, cabeçalho e rodapé

### 17.1 Cabeçalho

**Hoje [A]:** jornada — `<span>` "Trajetória Ifes" 16 px/700 (≈ 49 px de altura sem a
demonstração); editor e acompanhamento — link "Trajetória Ifes — Editor do instrumento"
/ "… — Acompanhamento da coleta" em 16 px/400; páginas 403/404/500 — **sem cabeçalho e
sem rodapé**. Com a demonstração, faixa (98 px) + cabeçalho (133 px) = **231 px** a
375 px, mas isso não vai a produção.

**Proposta (hipótese a validar na PoC):**

```
┌──────────────────────────────────────────────────────────┐  fio de marca 4 px (verde da marca)
│ [assinatura oficial Ifes]  │  Trajetória Ifes             │
│                            │  Acompanhamento de egressos  │  ← só ≥ 480 px
└──────────────────────────────────────────────────────────┘  divisor 1 px suave
```

- **Fundo branco** (a versão colorida da assinatura é a principal e vai em branco —
  Manual, p. 19); nada de faixa verde cheia, que exigiria versão negativa e somaria
  verde sem significado.
- **Assinatura horizontal oficial da Reitoria**, símbolo ≥ 30 px (redução mínima do
  Manual), com área de proteção ≥ 1 módulo; SVG inline (D-03).
- **Separador vertical** de 1 px e o **nome do produto em texto**, 18 px/700; subtítulo
  "Acompanhamento de egressos" em 15 px, cor secundária, **só a partir de 480 px**.
- **Altura-alvo:** ≤ 64 px a 375 px; ≤ 80 px no desktop. Nunca a primeira tela inteira.
- **Sem navegação**: o produto é de tarefa; a única "navegação" do egresso é "Ver sua
  trajetória no Ifes" no conteúdo. Ajuda e "Sair" dependem de autenticação (QF-1).
- **Barra gov.br e VLibras**: decisão institucional (D-02); se entrarem, somam ~32 px e
  devem ficar acima do fio.
- **Mesmo cabeçalho em todas as telas do egresso, inclusive 403/404/500.** Editor e
  acompanhamento herdam a estrutura, trocando só o subtítulo (abrangência transversal —
  IV-05).

### 17.2 Rodapé

**Hoje:** "Trajetória Ifes — demonstração local com dados fictícios." (texto de ambiente,
não de produto), com borda 1 px escura.

**Isto ajuda quem está executando uma tarefa?** Pouco — por isso deve ser **mínimo**:

- "Instituto Federal do Espírito Santo" (texto, 15 px, cor secundária);
- quando existirem e forem aprovados: **Privacidade** (há dados pessoais e sensíveis no
  instrumento), **Acessibilidade** e **Contato** (o instrumento já cita
  egressos@ifes.edu.br) — conteúdo é dependência (QF-5), não decisão visual;
- divisor suave; sem colunas, sem redes sociais, sem banners, sem mapa do site.

Altura-alvo: ≤ 120 px no mobile.

---

## 18. Mobile (375 / 390 / 430 px)

Não se refaz a auditoria mobile; verifica-se se a direção visual se sustenta [A]:

| Pergunta | Hoje | Com a direção proposta |
|---|---|---|
| Identidade coerente a 375 px? | Não há identidade | Assinatura (~150–180 px de largura) + nome cabem em 343 px; validar na PoC |
| Cabeçalho institucional sem ser enorme? | 49 px em produção | ≤ 64 px |
| Tipografia proporcional? | Sim | Enunciado 18 px a 375 px: 3–4 linhas nas perguntas longas — medir na PoC |
| Spacing equilibrado? | Perguntas coladas | 48 px entre Perguntas aumenta a página (~+20 px por Pergunta: ~+280 px na Seção 8); aceitável — sem fragmentação |
| Ações com hierarquia? | Sim (Seção); não (trajetória, conclusão — IV-10) | Largura total para toda ação principal ≤ 480 px |
| Superfícies comprimem conteúdo? | A ficha `dl` comprime o curso em 4 linhas (IV-11) | Ficha empilhada ≤ 480 px |
| Escala legível? | Sim; 5 pontos numa linha de 320 a 430 px (014) | Célula visível não pode reduzir a área nem quebrar a linha única (SC-006 da 014) |
| Excesso de bordas? | Divisores fortes repetidos | Divisores suaves (IV-08) |
| Excesso de verde? | Nenhum | Verde em 4 lugares só (seção 23) |
| Mesmo produto no desktop e no celular? | Sim (mesmo CSS) | Manter: um único conjunto de tokens, um único breakpoint |

---

## 19. Acessibilidade visual

**Já garantido e a preservar [A, C]:** texto 17,2:1; ação 9,6:1; erro 7,0:1; bordas
de controle 6,7:1 (≥ 3:1, WCAG 1.4.11); foco preto 3 px + halo amarelo 6 px (12,8:1
contra o amarelo; visível sobre qualquer fundo); alvos ≥ 44 px; 16 px de base (sem zoom
no iOS); sem rolagem horizontal até 200% (014 SC-008); pendência e erro não dependem só
de cor.

**Pontos a observar na direção nova:**

- **Verde da marca `#2f9e41` (3,45:1)**: só como elemento gráfico (fio, símbolo). Nunca
  texto, nunca fundo de botão com texto.
- **Verde de ação `#195128`**: 9,34:1 com branco; link verde sublinhado sobre branco
  9,34:1.
- **Divisor suave** (`#c6cace`, 1,65:1): **só decorativo**. Nenhum controle, campo ou
  estado pode depender dele — bordas de campo e de rádio continuam `#565c65` (6,7:1).
- **Estado selecionado** da linha/célula: não pode depender só do fundo tonal (que fica
  abaixo de 3:1); a marca do próprio controle (ponto/visto) continua sendo o sinal
  principal, e a borda de acento da célula deve ter ≥ 3:1.
- **Foco programático do resumo** (014 FR-027, `autofocus`): no Chromium o resumo recebe
  foco **sem** `:focus-visible` → nenhum indicador visual [A]. Não é falha (o resumo é
  visualmente forte e é o topo do conteúdo), mas a PoC pode dar ao resumo um estilo de
  `:focus` equivalente ao de foco (IV-15).
- **Alto contraste do sistema** (`forced-colors`): bordas e fios atuais sobrevivem;
  fundos tonais e o estado selecionado por fundo **desaparecem** — por isso nenhum
  significado pode depender deles. Verificar na PoC.

---

## 20. O que aprender com o IFRN

Evidências: páginas da seção 7, observadas em 2026-10-03. "Adotar" = adotar o
**princípio**, não a implementação.

| Padrão | Evidência no IFRN | Por que funciona | Aplicabilidade no Trajetória | Decisão |
|---|---|---|---|---|
| Contraste forte título × corpo | `h1` 40/800 vs card 400; notícias, busca, cursos, campi, PS, institucional (recorrente) | Hierarquia legível à distância; sensação editorial contemporânea | O Trajetória precisa do **princípio** nos enunciados (16 → 18 px) e no nome do produto; 800 em `system-ui` varia muito entre plataformas | **Adaptar** (por tamanho e 600/700; sem 800) |
| Uma família tipográfica | Inter em tudo (recorrente) | Coesão | Já cumprido com `system-ui` | **Adotar** (já adotado) |
| Rampa de cor em tokens | `:root` com primary 50…900 + semânticas (recorrente) | Consistência e manutenção | Necessário, mas **mínimo**: 4 verdes, não 13 | **Adaptar** |
| Verde-escuro para títulos/marca, verde médio para links | `#1e482b`, `#357e4b` (recorrente) | Marca percebida sem saturar | Verde-escuro (`#195128`, o do Ifes) para ação e links | **Adaptar** |
| Verde claro como fundo de botão | `#4bb26a` com texto branco, 2,67:1 (recorrente) | — | Falha de contraste | **Não adotar** (contraexemplo) |
| Superfícies tonais sem sombra | cards em `#f8fcf9`/`#edf7f0`, sem sombra (recorrente) | Leveza; separação sem ruído | Uma única superfície tonal, reservada à informação institucional | **Adotar** |
| Fio de marca no topo do cabeçalho | borda superior 3 px `#357e4b` nas páginas internas (recorrente) | Sinal de marca barato, discreto, constante | Fio de 4 px no verde da marca | **Adotar** |
| Dois níveis de raio (6 e 20 px) | recorrente | Suaviza; diferencia tamanhos | Produto sem cards: **um** raio (4 px) basta | **Adaptar** (um nível, a validar) |
| Cards em grade | notícias, cursos, PS (recorrente) | Navegação de catálogo | Não há catálogo | **Não adotar** |
| Pílulas para filtros, contadores, badges | recorrente | Escaneabilidade de listas | Sem filtros nem badges no produto; status por texto | **Não adotar** |
| `dl` de metadados (rótulo pequeno + valor) | curso e PS | Leitura rápida de atributos | Ficha da formação já é `dl`; adaptar ao mobile empilhado | **Adaptar** (sem ícones) |
| Cabeçalho de ~194 px com redes sociais e busca | home e internas (recorrente) | Portal de conteúdo | Produto de tarefa | **Não adotar** |
| Mega-menu / dropdown de 2 colunas | "Campi" | Navegação extensa | Não há navegação | **Não adotar** |
| Hero em vídeo, carrossel, faixas coloridas | home (isolado à home) | Vitrine | Concorre com a tarefa | **Não adotar** |
| Rodapé de ~2.000 px, 97 links | recorrente | Mapa do site | Não ajuda a tarefa | **Não adotar** |
| Corpo 15 px também no mobile | recorrente | — | Pior legibilidade; inputs 13 px causam zoom no iOS | **Não adotar** (manter 16) |
| Sem largura máxima de container | recorrente | — | 100–150 cpl | **Não adotar** (manter 40 rem) |
| Reset `outline: none` (sem foco) | recorrente | — | Falha 2.4.7 | **Não adotar** (contraexemplo) |
| Modo escuro e alto contraste próprios | botões no cabeçalho | Escolha do usuário | Fora de proporção agora; respeitar `forced-colors` do sistema basta | **Não adotar** (registrar) |
| Ícones Material + ilustrações flat | cursos (recorrente) | Atração em portal | Decoração; ícones não substituem texto | **Não adotar** (no máximo 3 ícones de feedback) |
| Link verde sublinhado no corpo | recorrente | Reconhecível e acessível | Sim | **Adotar** |

---

## 21. O que preservar

| Código | Elemento | Por quê |
|---|---|---|
| **IV-P1** (IV-PRESERVAR) | Rodapé da Seção da 014: primário preenchido, secundário em contorno, terciárias como links com nota, divisor e ≥ 32 px; largura total ≤ 480 px | Hierarquia inequívoca, medida [A]; deve virar **padrão de ação** de toda a jornada (IV-10) |
| **IV-P2** | Foco: contorno 3 px `#1b1b1b` + halo 6 px `#ffdd00` | Mais forte que o gov.br, o IFRN e o portal do Ifes; funciona sobre branco, cinza, verde e azul |
| **IV-P3** | Coluna única de 40 rem; gutter 16 px; um breakpoint | Medida de linha ideal; produto de tarefa |
| **IV-P4** | `system-ui`, 16 px de base, entrelinha 1,5, escala 28/22/18/16/15 | Escala real, sem arbitrariedade; zero dependência |
| **IV-P5** | Alvos de 44 px; linha/célula inteira tocável; escala em grade | Decisão funcional da 014; só ganha forma visível |
| **IV-P6** | Erro com três redundâncias (título, "Erro:", fio/borda) e vermelho `#b50909` 7,0:1 | Acessível; não depende só de cor |
| **IV-P7** | Ausência de sombras, de cards, de ícones decorativos, de JS e de dependências | Base de um produto calmo; é diferencial, não falta |
| **IV-P8** | Faixa de contexto (fio lateral + fundo) | Melhor padrão de "voz institucional" do produto; muda só a cor |
| **IV-P9** | Contraste documentado no topo do CSS | Prática a manter para cada token novo |
| **IV-P10** | Resumo de pendência/erro no topo, com links e foco | Estrutura correta (014) |
| **IV-P11** | Telas de estado curtas ("já respondida", "encerrada") e textos honestos | Não precisam de redesenho, só do shell |

---

## 22. Achados priorizados

Formato: **Problema** → **Evidência** → **Princípio** → **Recomendação (solução
possível)**. Abrangência: **J** = só jornada do egresso (e prévia do editor, quando
controles); **T** = transversal (CSS ou shell compartilhado com editor/acompanhamento).

### IV-01 — IV-CRÍTICO — O shell não tem nenhum sinal institucional do Ifes

- **Tela/componente:** todas / cabeçalho, rodapé.
- **Problema:** nada identifica o Ifes além da palavra "Ifes" no nome do produto.
- **Evidência [A, C]:** cabeçalho = `<span>Trajetória Ifes</span>` 16 px/700, mesma
  medida do nome da pessoa; nenhuma imagem, nenhuma cor da marca; o CSS declara "sem
  identidade institucional presumida (DP-801)".
- **Princípio:** reconhecimento institucional por **assinatura oficial**, não por
  quantidade de cor; produto subordinado à instituição.
- **Impacto:** o egresso não reconhece de imediato quem pergunta — num instrumento que
  coleta dados pessoais e sensíveis, isso afeta confiança.
- **Recomendação:** cabeçalho da seção 17.1 — assinatura oficial da Reitoria em SVG
  inline, fio de marca, nome do produto em texto, subtítulo opcional; rodapé mínimo
  (17.2).
- **Abrangência:** T (base da jornada; editor e acompanhamento herdariam depois — IV-05).
- **Prioridade:** 1 (PoC).
- **Referência:** Manual da Marca IF (2015); Portaria Ifes 1.818/2012; IFRN (fio de
  marca).
- **Dependência:** **DP-801** (decisão de identidade); **D-03** (arquivo oficial e forma
  de inclusão sem `staticfiles`); aprovação da ACS.
- **Risco de regressão:** altura do cabeçalho no mobile (SC-010 da 014: primeira ação na
  primeira tela) — medir na PoC.

### IV-02 — IV-ALTO — Um azul sem origem faz papel de marca, ação, contexto e pendência

- **Tela/componente:** todas / botões, links, contexto, resumo e marca de pendência.
- **Problema:** `#1a4480` acumula quatro papéis; nenhum deles é "Ifes".
- **Evidência [C]:** 11 ocorrências; usado em `a`, `button`, `.contexto`,
  `.resumo-pendencias`, `.com-pendencia`; a 014 R4 chama-o "azul institucional".
- **Princípio:** cor de marca, cor de ação e cor de estado devem ser papéis distintos;
  a mesma cor para "aja aqui" e "falta algo" enfraquece os dois.
- **Impacto:** identidade alheia; semântica ambígua (a pendência "parece" um botão ou um
  contexto).
- **Recomendação:** paleta da seção 25: voz institucional em verde Ifes; ação em token
  próprio (`cor.acao`), verde Ifes escuro `#195128` na Direção A ou a cor de interação do
  Padrão Digital de Governo na Direção B (seção 8; D-02); o azul `#1a4480` **permanece**,
  mas só como informação/pendência
  (preserva a decisão da 014 e o contraste já validado); renomear o papel nos
  comentários/specs para "informação/pendência".
- **Abrangência:** T — `a` e `button` são globais e o editor/acompanhamento incluem a
  mesma folha. A PoC deve **restringir** a troca às telas do egresso (regra da 014
  FR-045) e só depois decidir o shell administrativo.
- **Prioridade:** 1 (PoC).
- **Dependência:** **D-02** (como o Padrão Digital de Governo se aplica ao Trajetória e
  qual margem existe para a identidade do Ifes — decide entre as Direções A e B); DP-801.
- **Risco:** regressão visual no editor/acompanhamento se aplicado globalmente.

### IV-03 — IV-ALTO — Na pendência, a frase por Pergunta continua na cor de erro

- **Tela/componente:** Seção reapresentada com pendências / `.erro` dentro de
  `.com-pendencia`.
- **Problema:** resumo e fio são azuis (pendência), mas "Falta responder: Esta pergunta é
  obrigatória." aparece em **vermelho** 600.
- **Evidência [A]:** Seção 2 de Maria, 1 de 8 respondida: `color: rgb(181, 9, 9)` na
  frase da Pergunta pendente, com `border-left: 4px solid rgb(26, 68, 128)`. A 014 R4
  trocou título, prefixo e borda, mas a classe `.erro` manteve a cor.
- **Princípio:** a cor deve dizer o mesmo que o texto; pendência ≠ erro (014 FR-003).
- **Impacto:** seis frases vermelhas numa Seção que foi salva com sucesso contradizem a
  mensagem "O que você respondeu nesta seção está salvo".
- **Recomendação:** a marca por Pergunta segue o modo do resumo (cor de
  informação/pendência na pendência; vermelho só no erro). Problema visual causado pela
  solução da 014 — dentro do escopo.
- **Abrangência:** J (e prévia do editor, que reutiliza os controles).
- **Prioridade:** **Etapa 0 — correção imediata**, em PR próprio, pequeno e independente
  da identidade visual. Não depende de DP-801, da marca, do benchmark nem da PoC: é a
  correção de um efeito colateral objetivo da 014 que contradiz "pendência ≠ erro".
- **Risco:** nenhum funcional; o verificador de acessibilidade da 008 não depende de cor.

### IV-04 — IV-ALTO — O questionário não tem ritmo nem hierarquia interna

- **Tela/componente:** toda Seção / `.pergunta`, `legend`, `.explicacao`,
  `.descricao-escala`.
- **Problema:** enunciado, opção e texto auxiliar diferem só por peso; o espaço entre
  Perguntas é menor que o de uma linha de opção.
- **Evidência [A]:** `legend` 16 px/600; opção 16 px/400; `.explicacao` 16 px
  `#1b1b1b`; `margin-bottom` da Pergunta 28 px contra linhas de 44 px; Seção 8 com 14
  Perguntas, Seção 2 com 8 Perguntas em 2.874 px de página no desktop.
- **Princípio:** proximidade (espaço entre grupos > espaço dentro do grupo); três níveis
  tipográficos distinguíveis.
- **Impacto:** sensação de "formulário administrativo com dezenas de perguntas"; mais
  esforço para achar o começo de cada Pergunta, principalmente no celular.
- **Recomendação:** 48 px entre Perguntas; enunciado 18 px/600 (entrelinha ~1,4);
  "(obrigatória)", explicação e descrição da escala em 15 px, cor de texto secundário;
  opções inalteradas. Fio entre Perguntas só se a PoC mostrar necessidade.
- **Abrangência:** J (e prévia do editor — desejável: o editor vê o que o egresso vê).
- **Prioridade:** 1 (PoC).
- **Risco:** página mais longa (~+280 px na Seção 8); enunciados longos ganham uma linha
  a 375 px. Aceitável; medir na PoC.

### IV-05 — IV-ALTO — Shell fragmentado entre jornada, editor, acompanhamento e erros

- **Tela/componente:** cabeçalho e rodapé de todas as telas; 403/404/500.
- **Problema:** três cabeçalhos (span 700; link 400 com sufixo; link 400 com outro
  sufixo), três rodapés com textos de ambiente; páginas de erro sem cabeçalho nem
  rodapé.
- **Evidência [C, A]:** `interface/base.html`, `editor/base.html`,
  `acompanhamento/base.html`; `403_csrf.html`, `404.html`, `500.html`.
- **Princípio:** um produto = um shell; o contexto (egresso, editor, acompanhamento)
  muda o subtítulo, não a estrutura.
- **Impacto:** o produto não parece "concebido como um todo"; a página de erro parece de
  outro sistema.
- **Recomendação:** um padrão de shell (17.1/17.2) com variação só de subtítulo. **Na
  PoC, só a jornada e as páginas de erro**; editor e acompanhamento depois (Etapa D do
  roadmap), sem redesenhar suas telas.
- **Abrangência:** **T** (registrado explicitamente: shell comum).
- **Prioridade:** 2 (jornada na PoC; administrativo depois).
- **Risco:** regressão nos testes de SC-014 da 014 (comparação visual do editor e do
  acompanhamento) — por isso fora da PoC.

### IV-06 — IV-MÉDIO — Feedback sem semântica visual: um único aviso para tudo e confirmação sem sinal

- **Tela/componente:** trajetória (`aviso` salvo / saída / situação), Seção (`aviso` de
  percurso), confirmação.
- **Problema:** sucesso ("está salvo"), neutro ("você pode continuar"), informação
  (mudança de situação) e atenção (percurso) usam a mesma caixa cinza de 2 px. A
  confirmação "Pesquisa concluída" é um `h1` igual a qualquer outro.
- **Evidência [A]:** Diego, "Salvar e sair" → caixa cinza; Maria, confirmação sem nenhum
  elemento de conclusão.
- **Princípio:** feedback com três redundâncias (cor + forma/ícone + texto); o fim de
  uma tarefa merece reconhecimento visual imediato.
- **Impacto:** o momento de maior alívio (salvou; concluiu) é visualmente indistinto.
- **Recomendação:** três variantes de aviso, todas com fio de acento à esquerda e
  texto atual: **sucesso** (verde de ação; salvo, concluída), **informação** (azul;
  situação, percurso, saída neutra), **erro/pendência** (já existentes). Na confirmação,
  um bloco de sucesso no topo (fio verde + ícone de visto **ao lado** do título, nunca
  no lugar do texto). Sem animação, sem ilustração.
- **Abrangência:** J (o `.aviso` do editor pode ficar como está).
- **Prioridade:** 2 (PoC: telas 1 e 4).
- **Dependência:** nenhuma funcional (o código do aviso já é de lista fechada — 014 N6).
- **Risco:** "sucesso" e "marca" no mesmo verde — mitigado porque sucesso sempre tem
  texto e ícone, e ocorre em só dois momentos.

### IV-07 — IV-MÉDIO — Controles de escolha e escala sem estados próprios

- **Tela/componente:** rádios, caixas, escala.
- **Problema:** cor do controle marcado vem do navegador (`accent-color: auto`); linha e
  célula não mostram hover nem selecionado; a célula da escala (até 96×56 px no
  desktop) é toda tocável, mas visualmente é só um círculo de 20 px.
- **Evidência [A]:** `accentColor: auto`, `appearance: auto`, controle de 20 px; célula
  96×56 px a 1280 px.
- **Princípio:** affordance — o alvo deve parecer do tamanho que tem; estado selecionado
  visível além do ponto nativo.
- **Recomendação:** `accent-color` = cor de ação; célula da escala com borda 1 px neutra
  forte (≥ 3:1) e raio pequeno; linha/célula marcada com borda de acento e fundo tonal
  leve; hover com fundo tonal. Só CSS (seletor de "contém controle marcado"), sem mudar
  marcação; sem suporte, cai no estado atual.
- **Abrangência:** J + prévia do editor (014 FR-045 já exige que a prévia acompanhe).
- **Prioridade:** 2 (PoC: tela 2).
- **Risco:** a borda da célula não pode reduzir a área nem quebrar a escala de 5 pontos
  numa linha de 320 a 430 px com fonte até 200% (014 SC-006, SC-007) — remedir.

### IV-08 — IV-MÉDIO — Um único cinza forte para controles e para divisores

- **Tela/componente:** cabeçalho, listas, `.saidas`, rodapé, campos.
- **Problema:** `#565c65` (6,7:1) é usado tanto em bordas de campo (precisa ≥ 3:1) quanto
  em divisores decorativos; no fim da Seção há dois fios escuros seguidos (`.saidas` e
  rodapé).
- **Evidência [C, A]:** 13 ocorrências de `#565c65`; captura do fim da Seção a 375 px.
- **Princípio:** peso visual proporcional à função; divisores separam, não emolduram.
- **Impacto:** aparência de documento burocrático; ruído.
- **Recomendação:** dois tokens de borda: **forte** (`#565c65`, controles e estados) e
  **suave** (≈ `#c6cace`, só divisores). Nenhum significado depende do suave.
- **Abrangência:** T se aplicado ao token global; PoC só nas telas do egresso.
- **Prioridade:** 2.

### IV-09 — IV-MÉDIO — Item de formação: a situação compete com a formação

- **Tela/componente:** trajetória / item de formação.
- **Problema:** "Pesquisa já respondida." e o texto de ambiguidade aparecem em negrito,
  com o mesmo peso da linha principal da formação; o espaço inferior do item é o dobro
  do superior (padding 16 + margem 16); com uma formação (Ana), a formação aparece só
  dentro de uma frase, sem o tratamento de item.
- **Evidência [A]:** Diego e Maria a 375 px; Ana a 390 e 430 px.
- **Princípio:** hierarquia identificação → metadado → estado → ação; espaçamento
  simétrico dentro do grupo.
- **Recomendação:** linha principal 600 (preto); complemento 15 px secundário; situação
  em texto regular com marca textual discreta (sem badge, sem ícone obrigatório) ou na
  cor do estado; ação abaixo. Na frase de entrada, destacar a linha da formação
  (negrito), sem mudar o texto.
- **Abrangência:** J.
- **Prioridade:** 2 (PoC: tela 1).
- **Dependência:** contrato `telas.md` da 014 (a frase de entrada é conteúdo — QF-3).

### IV-10 — IV-MÉDIO — Ação principal com larguras diferentes no mobile

- **Tela/componente:** trajetória ("Iniciar/Continuar a pesquisa"), conclusão ("Concluir
  pesquisa") × rodapé da Seção.
- **Problema:** na Seção, os botões ocupam 100% até 480 px (014); nas outras telas, a
  ação principal tem a largura do texto (175 px a 430 px).
- **Evidência [A]:** medição a 375, 390 e 430 px.
- **Princípio:** um padrão de ação para o mesmo papel; botão em bloco no toque
  (gov.br — boa prática).
- **Recomendação:** toda ação principal da jornada em largura total até 480 px.
- **Abrangência:** J.
- **Prioridade:** 2.

### IV-11 — IV-MÉDIO — Ficha da formação comprime o curso no mobile

- **Tela/componente:** conclusão, confirmação, telas de estado / `.contexto dl`.
- **Problema:** grade `max-content | 1fr` deixa ~150 px para o valor; "Tecnologia em
  Análise e Desenvolvimento de Sistemas" ocupa **4 linhas** a 375 px.
- **Evidência [A]:** captura da conclusão e da confirmação de Maria a 375 px.
- **Princípio:** reflow com legibilidade, não só sem rolagem.
- **Recomendação:** abaixo de 480 px, rótulo acima do valor (o acompanhamento já faz isso
  em `.dados` — reutilizar o padrão).
- **Abrangência:** J.
- **Prioridade:** 3 (PoC: tela 4).

### IV-12 — IV-BAIXO — Valores sem nome e unidades divergentes

- **Problema:** escala real, mas sem tokens nomeados; breakpoint em `30em` e `30rem`;
  espaçamentos isolados (0,125 e 0,625 rem); acento de estado ora 3 px, ora 4 px.
- **Evidência [C].**
- **Recomendação:** tokens mínimos da seção 25 como propriedades CSS no topo da folha,
  com contraste documentado; um breakpoint em `em`; acento sempre 4 px.
- **Abrangência:** T (folha compartilhada) — fazer na Etapa A, sem mudar aparência
  administrativa.

### IV-13 — IV-BAIXO — Cantos retos e bordas de 2 px: gramática de outro governo

- **Problema:** raio 0 em tudo + bordas escuras de 2 px + foco amarelo compõem a
  assinatura visual do GOV.UK.
- **Evidência [C].** Princípio: identidade própria sem competir com a marca.
- **Recomendação:** **um** raio de 4 px em campos, botões, avisos e células da escala — a
  validar na PoC (é a recomendação mais próxima de "gosto"; só fica se a PoC mostrar
  ganho de coerência). Manter bordas de 2 px nos campos (contraste e clareza) e o foco.
- **Abrangência:** J na PoC.

### IV-14 — IV-BAIXO — Iconografia: ausente, e assim deve continuar quase sempre

- **Problema:** nenhum; registrar a regra.
- **Recomendação:** no máximo **3 ícones** (visto, informação, alerta), SVG inline, traço
  uniforme, 20 px, sempre ao lado de texto, `aria-hidden`; só em avisos e resumos. Sem
  biblioteca. Opcional na PoC.

### IV-15 — IV-BAIXO — Resumo focado ao carregar sem indicador de foco

- **Evidência [A]:** `document.activeElement` = resumo; `:focus-visible` falso;
  `outline: none`.
- **Recomendação:** estilo de `:focus` no resumo equivalente ao de foco (contorno), sem
  mudar o comportamento da 014.
- **Abrangência:** J.

### IV-16 — IV-BAIXO — A demonstração distorce a percepção do shell

- **Problema:** faixa + cabeçalho de demonstração ocupam 231 px a 375 px.
- **Recomendação:** a PoC avalia o shell **de produção** e mantém a faixa de demonstração
  como camada separada e claramente "não produto" (cor `#fff1d2` só nela).

---

## 23. Foundations propostas

### 23.1 Uso da marca

- Assinatura horizontal oficial da **Reitoria/sistêmica**, versão colorida sobre branco,
  arquivo oficial sem alteração, símbolo ≥ 30 px, área de proteção ≥ 1 módulo.
- "Trajetória Ifes" em **texto** ao lado, separado por fio vertical; nunca composto
  dentro da assinatura (seria "nova aplicação", vedada pelo Manual).
- Vermelho da marca só dentro da assinatura. Verde da marca em elementos gráficos
  (fio de 4 px, assinatura) — nunca em texto.

### 23.2 Onde o verde aparece (e só ali)

1. Assinatura e fio de marca (verde da marca `#2f9e41`).
2. Voz institucional: fio e fundo da faixa de contexto e da ficha da formação (verde de
   ação no fio; fundo verde muito claro).
3. Ação principal e links (verde de ação `#195128` — **Direção A**; na Direção B, a ação
   segue o Padrão Digital de Governo e este item sai da lista).
4. Sucesso (verde de ação + ícone + texto), em dois momentos: salvo e concluída.

Perguntas, opções, campos, títulos e textos: neutros.

### 23.3 Demais foundations

| Foundation | Direção |
|---|---|
| **Cores** | Seção 25 (14 tokens) |
| **Tipografia** | `system-ui`; 28 / 22 / 18 / 16 / 15 px; pesos 400 / 600 / 700; entrelinha 1,5 (corpo), 1,4 (enunciado), 1,25 (títulos); nome do produto 18/700 |
| **Espaçamento** | 4 / 8 / 12 / 16 / 24 / 32 / 48 |
| **Container** | 40 rem (jornada), 56 rem (administração); gutter 16 px |
| **Grid** | coluna única; grade só na escala (014) |
| **Breakpoint** | um: 30 em (480 px) |
| **Raio** | 0 ou 4 px (a validar) |
| **Bordas** | 1 px suave (divisor) · 2 px forte (controle) · 4 px acento (estado/voz institucional) |
| **Sombras** | nenhuma |
| **Foco** | atual (IV-P2) |
| **Iconografia** | nenhuma ou 3 ícones de feedback |
| **Movimento** | nenhum |

---

## 24. Trajetória Ifes UI — mini sistema visual (conceitual)

> _Foundations + padrões visuais mínimos de **um** produto._ Não é design system
> institucional, não é biblioteca, não é pacote, não tem Storybook. Vive no topo da
> folha de estilo existente, como comentário + propriedades CSS, quando for
> implementado.

### Foundations
Seção 23.

### Famílias de componentes (só as existentes)

| Família | Padrão visual |
|---|---|
| **Botões** | Primário: fundo verde de ação, texto branco 16/600, 44 px, raio 4. Secundário: branco, borda 2 px e texto verde de ação. Hover: verde de ação mais escuro (`#00420c`). Ativo: idem + deslocamento zero (sem animação). Desabilitado: não usado na jornada (o único desabilitado é o bloqueador oculto da 014). Largura total ≤ 480 px para a ação principal |
| **Links** | Verde de ação, sempre sublinhados; hover: sublinhado mais espesso. Terciárias: link + nota 15 px secundária (014) |
| **Campos (texto, lista)** | 44 px, borda 2 px forte, raio 4, fonte 16; erro: borda vermelha; pendência: borda azul |
| **Escolha (rádio, caixa)** | Controle nativo com `accent-color` de ação; linha de 44 px; marcada: fio de acento à esquerda ou fundo tonal + controle marcado |
| **Escala** | Células ≥ 44 px com borda 1 px forte e raio 4; número abaixo; marcada: borda de acento 2 px + fundo tonal |
| **Feedback** | Aviso (sucesso / informação), resumo (erro / pendência): fio de acento 4 px à esquerda + título + texto (+ ícone opcional); fundo branco ou tonal muito claro |
| **Metadado contextual** | "Você está respondendo sobre:" — fio verde 4 px + fundo verde muito claro; texto 16/400 com rótulo 600 |
| **Item de formação** | Linha principal 16/600; complemento 15/400 secundário; situação 15/400 (cor do estado quando houver); ação; divisor suave entre itens; espaçamento simétrico (16 / 16) |
| **Resumo de erro/pendência** | Estrutura da 014; cor por modo também na frase da Pergunta |
| **Cabeçalho** | Seção 17.1 |
| **Rodapé** | Seção 17.2 |

### Padrões

| Padrão | Composição |
|---|---|
| **Shell** | fio de marca → cabeçalho → (aviso) → `h1` → conteúdo → rodapé mínimo |
| **Seção** | `h1` da Seção → (resumo) → contexto da formação → textos da Versão → Perguntas (48 px entre si) → ações (primária, secundária) → divisor → terciárias |
| **Pergunta** | enunciado 18/600 → auxiliar 15 secundário → resposta → (complemento, remover) |
| **Contexto da formação** | faixa compacta nas Seções; ficha empilhada ≤ 480 px nas telas finais |
| **Pendência** | resumo azul + fio azul + frase azul por Pergunta; frase de salvamento quando verdadeira (014) |
| **Erro** | resumo vermelho + fio vermelho + "Erro:" vermelho |
| **Confirmação** | bloco de sucesso (fio verde + visto + `h1`) → registro → ficha → texto de encerramento → link para a trajetória |
| **Trajetória** | `h1` → (aviso) → frase de entrada com a formação em destaque → ação principal em bloco → "Suas outras formações" → itens |

### Capacidade futura (Retrato de Egresso — só avaliação)
A linguagem proposta (superfície tonal institucional, item de formação, `dl` de
metadados, tipografia com três níveis, feedback de sucesso) **comporta** uma futura
devolutiva ao egresso sem nada novo nas foundations; componentes próprios (gráficos,
compartilhamento) seriam decisão futura própria e **não** são antecipados aqui.

---

## 25. Tokens sugeridos

Só o necessário. Nomes conceituais; a implementação decidirá a forma.

### Cor

| Token | Valor | Contraste | Uso |
|---|---|---|---|
| `cor.marca` | `#2f9e41` (HEX do Manual) | 3,45:1 com branco | Só gráfico: fio de marca. Nunca texto |
| `cor.acao` | `#195128` (verde do portal do Ifes) | 9,34:1 | Botão primário, link, `accent-color`, fio da voz institucional, sucesso |
| `cor.acao.forte` | `#00420c` (portal do Ifes) | 11,8:1 | Hover/ativo |
| `cor.institucional.fundo` | ≈ `#eef7f0` (verde muito claro, a calibrar) | texto 16:1 sobre ele | Faixa de contexto e ficha; seleção tonal |
| `cor.texto` | `#1b1b1b` | 17,2:1 | Corpo |
| `cor.texto.suave` | `#565c65` | 6,7:1 | Auxiliar, notas, complemento, subtítulo |
| `cor.fundo` | `#ffffff` | — | Página |
| `cor.borda.forte` | `#565c65` | 6,7:1 | Campos, células, controles |
| `cor.borda.suave` | ≈ `#c6cace` | 1,65:1 | Só divisores decorativos |
| `cor.info` (pendência) | `#1a4480` | 9,6:1 | Pendência, aviso informativo |
| `cor.erro` | `#b50909` | 7,0:1 | Erro |
| `cor.foco` | `#1b1b1b` + `#ffdd00` | 12,8:1 | Foco (inalterado) |
| `cor.demonstracao` | `#fff1d2` | — | Só a faixa de demonstração |

Removidos: `#f5f7fa` (substituído pelo fundo institucional) e `#fff` duplicado de
`#ffffff`. **Não** criar: rampa 50–900, warning amarelo (não há estado de alerta além de
erro/pendência), cores por campus.

**Calibrar na PoC:** `cor.institucional.fundo` e `cor.borda.suave` (valores aproximados);
`cor.acao` e `cor.acao.forte` são o **único ponto de troca entre as Direções A e B**
(seção 8): na B, assumem a cor de interação prescrita pelo Padrão Digital de Governo
(hoje `#1351b4`) e o verde fica em `cor.marca` + voz institucional. Nenhum componente ou
tela é duplicado para isso.

### Tipografia
`fonte.familia` (system-ui) · `fonte.tamanho` 28 / 22 / 18 / 16 / 15 · `fonte.peso`
400 / 600 / 700 · `fonte.entrelinha` 1,25 / 1,4 / 1,5.

### Espaço, forma, layout
`espaco` 4 / 8 / 12 / 16 / 24 / 32 / 48 · `raio` 4 (ou 0) · `borda` 1 / 2 / 4 ·
`container` 40 rem / 56 rem · `breakpoint` 30 em · `alvo` 44 px (px, não rem — 014 R6).

**Não viram token:** 3 px e 6 px do foco (pertencem a uma regra só), 6 rem/8 rem
isolados (`textarea`, `scroll-margin`), larguras de tabela do acompanhamento.

---

## 26. Proof of Concept recomendada

**Gate:** nenhuma propagação antes de aprovar estas 4 telas em 375 e 1280 px (e 390/430
nas medições). Pessoas fictícias da demonstração; shell de produção (faixa de
demonstração à parte).

| # | Tela existente | Por que | Componentes cobertos | Foundations testadas | Riscos que detecta |
|---|---|---|---|---|---|
| 1 | **Trajetória** — Maria (seleção, 2 formações) e Diego (outras formações, ambiguidade), com o aviso de "Salvar e sair" | Primeira impressão; onde a identidade institucional mais pesa | Cabeçalho, rodapé, `h1`/`h2`, frase de entrada, item de formação, botão em bloco, aviso de sucesso e informativo | Marca, verde de ação, tipografia, espaço, borda suave | Altura do cabeçalho a 375 px; primeira ação na primeira tela (014 SC-010); excesso de verde com várias ações |
| 2 | **Seção 8 "Avaliação"** (Maria/Elisa) — 14 Perguntas, 2 escalas, rádios, caixas, "Outro" | A Seção mais longa e mais variada: o "formulário com dezenas de perguntas" | Pergunta, enunciado, auxiliar, rádio, caixa, escala, complemento, contexto da formação, 4 ações do rodapé | Ritmo de 48 px, escala tipográfica, `accent-color`, estados selecionados, raio | Escala de 5 pontos a 320–430 px com 200% (014 SC-006/007); comprimento da página; contraste dos estados |
| 3 | **Seção 2 "Informações Pessoais" com pendências** + **Seção 8 com erro de forma** (variante) | O momento de maior ansiedade; IV-03 | Resumo nos dois modos, marca por Pergunta, frase de salvamento, campo em pendência e em erro | Cores de estado, borda de acento, foco do resumo | Confusão pendência × erro; cor contradizendo texto; foco visível |
| 4 | **"Concluir a pesquisa" → "Pesquisa concluída"** | Fim da tarefa; sinal de sucesso inexistente hoje | Ficha da formação, lista de Seções (44 px), botão de conclusão, bloco de sucesso, ícone opcional | Voz institucional, sucesso, ficha empilhada | Sucesso × marca no mesmo verde; ficha no mobile |

**Por que o conjunto basta:** cobre 100% das famílias de componentes da jornada, os
quatro estados (neutro, sucesso, pendência, erro), as duas densidades extremas (tela
curta e Seção de 14 Perguntas) e as duas pontas da tarefa. As demais telas (Seções
restantes, telas de estado, 403/404/500) são combinações desses mesmos componentes.

**Verificação de regressão obrigatória junto à PoC:** prévia de Seção do editor (que
reutiliza os controles) e as telas de SC-014 da 014 (lista de Pesquisas, edição de
Pergunta, painel de Campanha, entrada e operador da demonstração) **sem diferença
visual**.

**Critérios objetivos (verificáveis por medição ou inspeção):**
1. assinatura oficial do Ifes visível e legível na primeira viewport de 375 px,
   respeitando a redução mínima (símbolo ≥ 30 px) e a área de proteção do Manual;
2. verde presente apenas nos lugares da seção 23.2 (na Direção B, sem a ação);
3. todos os textos ≥ 4,5:1; controles e estados ≥ 3:1; foco visível em todos os
   elementos focáveis;
4. 014 SC-006 a SC-010 continuam válidos (remedidos);
5. sem rolagem horizontal de 320 a 1280 px com fonte até 200%;
6. pendência e erro distinguíveis em escala de cinza (só por texto e forma);
7. cabeçalho ≤ 64 px a 375 px;
8. as Direções A e B (seção 8) alternáveis pela troca de um único token, sem duplicar
   componentes nem telas, e ambas atendendo aos itens 1 a 7.

**Avaliação perceptiva (não é medição automatizada):** ao ver as telas sem contexto
prévio, a identidade deve ser prontamente reconhecida como de um produto do Ifes. Isso se
verifica em revisão visual com a ACS e a CPAEG/Proex (DP-801) e, se possível, com
pessoas egressas — nunca por CSS ou teste automatizado. Essa revisão precede qualquer
propagação.

---

## 27. Roadmap de aplicação (possível, não presumido)

A folha tem 162 linhas; uma sequência longa seria desproporcional. Sequência proposta:

| Etapa | Conteúdo | Observação |
|---|---|---|
| **0 — Correção imediata** | IV-03 (cor da frase de pendência) | PR próprio e minúsculo, separado da identidade visual; corrige um efeito colateral objetivo da 014 (pendência ≠ erro); não depende de DP-801 nem da PoC |
| **A — Foundations + PoC** (juntas) | Tokens da seção 25 restritos às telas do egresso; shell de produção da jornada; aplicar às 4 telas | Uma única entrega pequena; CSS e templates base, sem JS, sem dependência |
| **B — Validação e decisão** | Critérios da seção 26; revisão institucional (DP-801, D-01 a D-04) | **Gate**: se falhar, revisar foundations, não propagar |
| **C — Resto da jornada** | Demais Seções (automático, mesmos componentes), conclusão, telas de estado, 403/404/500 | Quase sem trabalho novo se A for bem feita |
| **D — Shell transversal** | Cabeçalho/rodapé do editor e do acompanhamento no mesmo padrão (só shell; telas internas intactas) | Respeitar SC-014 da 014 como regressão aceita explicitamente |
| **E — Resíduos** | Raio, ícones, `forced-colors`, unidades | Só se a PoC indicar |

---

## 28. Dependências

| Código | Dependência | Impacto |
|---|---|---|
| **D-01 / DP-801** | Identidade visual e linguagem definitivas (008/DP-801; instância: Proex/CPAEG com comunicação e TI) | Toda a direção desta auditoria é **proposta** para essa decisão; a PoC é o insumo para decidir |
| **D-02** | Esclarecimento institucional de **como** o Padrão Digital de Governo se aplica ao Trajetória (há evidência normativa de aplicabilidade a sistemas com serviços ao cidadão no Executivo Federal — seção 8) e **qual margem existe** para incorporar a identidade visual do Ifes; idem para barra gov.br/VLibras | Decide entre a Direção A (ação em verde Ifes) e a B (ação conforme o PDG) e os demais desvios da seção 8; não bloqueia a PoC, que compara A e B por um único token |
| **D-03** | Arquivo oficial da assinatura (Reitoria/sistêmica) via ACS/download de marcas; forma de inclusão sem `staticfiles` (008 R14) — SVG inline ou equivalente | Bloqueia IV-01 em publicação, propagação e produção; a PoC local, interna e não publicada pode usar o arquivo oficial público como insumo de prototipação, respeitando o Manual da Marca (seção 30) |
| **D-04** | Política de estáticos (008 R14; FR-082) | Mantém `system-ui` e impede fonte externa; reavaliar só se estáticos vierem por outro motivo |
| **D-05** | Regra da 014 FR-045 (estilo restrito à jornada) | Toda mudança de token deve ser escopada até a Etapa D |
| **D-06** | Contrato `telas.md` da 014 | Recomendações de trajetória e confirmação são visuais; mudar estrutura de conteúdo seria revisão do contrato |

---

## 29. Fora de escopo (e possíveis questões funcionais)

**Fora de escopo, não tratado:** domínio, instrumento, ordem e ramificação, persistência,
autenticação, campanhas, analytics, Retrato de Egresso (só a avaliação de capacidade em
24), compartilhamento, histórico, integrações, fluxos administrativos; DP-307, DP-406,
DP-702, DP-802, DP-803; decisões da 014.

**Possível questão funcional — fora do escopo desta auditoria** (registrada, sem
solução):

- **QF-1** — Identificação da pessoa e "Sair" no cabeçalho de produção dependem do
  mecanismo de acesso (004/DP-406; Constituição XV).
- **QF-2** — Seção sem título mostra "Egresso Ifes" como `h1` (Seção 13) — já registrado
  como [V] (ID-13).
- **QF-3** — Na entrada resolvida, a formação pendente existe só como frase, e as outras
  como itens; se a PoC mostrar que ela precisa do mesmo tratamento de item, é revisão do
  contrato da 014.
- **QF-4** — Conclusão e confirmação usam a ficha completa; as Seções, a linha compacta —
  escolha de conteúdo da 008/014.
- **QF-5** — Conteúdo do rodapé (aviso de privacidade, acessibilidade, contato) depende
  de textos e decisões existentes (005/DP-504).
- **QF-6** — Barra gov.br, VLibras, modo de alto contraste próprio: decisões
  institucionais/de produto (D-02).

---

## 30. Decisões pendentes (antes de uma PoC)

| # | Decisão | Quem | Recomendação desta auditoria |
|---|---|---|---|
| 1 | Usar a assinatura oficial da Reitoria/sistêmica no cabeçalho do produto | ACS + CPAEG/Proex (DP-801) | Sim, versão colorida sobre branco, sem marca própria do produto |
| 2 | Cor de ação: verde Ifes `#195128` (A) ou cor de interação do Padrão Digital de Governo (B) | DP-801 + TI, após esclarecer a aplicação do PDG (D-02) | Não decidir antes da PoC; preparar A e B pelo mesmo token e decidir com as duas versões lado a lado. A Direção A só é adotável se o esclarecimento de D-02 admitir essa margem |
| 3 | Barra gov.br / VLibras no produto | ACS + TI (D-02) | Não decidir na PoC; reservar espaço acima do fio |
| 4 | Pendência continua azul (014) | — (já decidida na 014) | Manter; só renomear o papel e corrigir IV-03 |
| 5 | Raio 4 px ou 0 | Equipe do produto, na PoC | Decidir pela comparação lado a lado |

Os itens 1 e 2 **precisam de aprovação antes** de qualquer propagação. Para uma PoC
local, interna e não publicada, pode-se utilizar o arquivo oficial disponibilizado
publicamente pelo Ifes como insumo de prototipação, respeitando integralmente as regras do
Manual da Marca. A validação institucional pela ACS e pela CPAEG/Proex é necessária antes
de publicação, propagação ou uso em produção.

---

## 31. Conclusão

### Respostas às perguntas do pedido

1. **Parece um produto do Ifes?** Não. Parece um serviço público acessível e genérico.
2. **Onde a identidade aparece?** Só no nome "Trajetória Ifes" e no conteúdo (curso,
   unidade, "Sua trajetória no Ifes").
3. **Onde se perde?** No cabeçalho, na cor de ação, no rodapé, nas páginas de erro.
4. **O que a faz parecer genérica?** Azul-marinho alheio, foco/raio de gramática GOV.UK,
   cabeçalho só de texto, divisores escuros repetidos.
5. **O que ainda parece "Django estilizado"?** Pouca coisa: cabeçalho tipográfico mínimo,
   divisores `#565c65` em tudo, páginas 403/404/500 sem shell, rodapé com texto de
   ambiente.
6. **O que torna o IFRN contemporâneo?** Tipografia confiante, superfícies tonais sem
   sombra, tokens, fio de marca, verde-escuro para marca.
7. **O que é transferível?** Contraste tipográfico (adaptado), uma superfície tonal,
   fio de marca, verde-escuro em links/ação, tokens mínimos, `dl` de metadados.
8. **O que não é?** Cabeçalho de portal, mega-menu, hero, cards, pílulas, rodapé
   gigante, corpo de 15 px, botão verde-claro, ausência de foco, container sem limite.
9. **Como modernizar sem descaracterizar?** Assinatura oficial + verde com significado +
   ritmo tipográfico + estados — sobre a base acessível atual.
10. **O verde está sendo usado corretamente?** Não está sendo usado. A proposta usa o
    verde da marca só como gráfico e, na Direção A (sujeita a D-02), um verde-escuro do
    próprio Ifes para ação.
11. **Paleta funcional:** seção 25.
12. **Escala tipográfica:** 28/22/18/16/15 (a atual), aplicada melhor.
13. **Escala de espaçamento:** 4/8/12/16/24/32/48.
14. **Superfícies:** branco + fios + uma superfície tonal institucional; sem cards, sem
    sombras.
15. **Container:** 40 rem (jornada), 56 rem (administração).
16. **Header:** branco, fio de marca, assinatura oficial, nome do produto em texto,
    ≤ 64 px no celular.
17. **Footer:** mínimo — instituição + links essenciais quando existirem.
18. **Componentes a consolidar:** aviso/feedback, item de formação, ação principal,
    escolha/escala (estados), shell.
19. **Componentes já bons:** rodapé da Seção, foco, campos, resumo, contexto (forma),
    telas de estado.
20. **Telas que precisam mudar:** trajetória, Seção (ritmo e estados), conclusão,
    confirmação, páginas de erro (shell).
21. **Telas que ficam praticamente iguais:** telas de estado ("já respondida",
    "encerrada"), 403 (só shell), editor e acompanhamento (só shell, depois).
22. **Elementos da 014 a preservar visualmente:** rodapé de 4 ações, separação das
    terciárias, alvos inteiros, escala em grade, resumo no topo com foco, linha de
    contexto, trajetória compacta.
23. **Menor conjunto de tokens:** 13 cores, 5 tamanhos, 3 pesos, 3 entrelinhas, 7
    espaços, 1 raio, 3 bordas, 2 containers, 1 breakpoint, 1 alvo.
24. **Menor "Trajetória Ifes UI":** seção 24 — 11 famílias existentes, 8 padrões.
25. **Telas da PoC:** trajetória; Seção 8; Seção 2 com pendência (+ erro); conclusão →
    confirmação.
26. **O que validar antes de propagar:** critérios da seção 26 + decisões 1 e 2 da
    seção 30.
27. **Ordem mais segura:** 0 → A (foundations + PoC) → B (gate) → C → D → E.

### Síntese

> O Trajetória Ifes deve parecer **um serviço do Ifes, não um site do Ifes**: branco,
> calmo, tipográfico e acessível como já é; reconhecível pela assinatura oficial e por
> um verde que significa "o Ifes está falando" ou "este é o próximo passo" — e por mais
> nada.

A menor linguagem visual necessária já está 70% escrita na folha atual. Falta dar nome e
papel às cores, criar ritmo no questionário, um shell institucional e três estados de
feedback. Tudo cabe na stack atual, sem dependência e sem JavaScript.
