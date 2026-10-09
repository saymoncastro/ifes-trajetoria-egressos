# Portal do Egresso — registro das decisões de direção visual

Registro de trabalho das decisões do §15 da
[auditoria de experiência e direção visual](2026-10-08-portal-ux-direcao-visual.md).
Ao fim das nove decisões, este registro será consolidado numa única ADR (prevista como
0009, "camada visual do Portal"). Até lá, nenhuma decisão aqui altera spec, código ou o
instrumento.

| # | Decisão (§15) | Situação | Data |
|---|---|---|---|
| 1 | Layout e tokens próprios do Portal (R1, R2, R3) | **Aprovada** | 2026-10-09 |
| 2 | Leitura da Constituição XXI para o Portal (R4) | **Aprovada** (interpretação, sem emenda) | 2026-10-09 |
| 3 | D-02: cor de ação | **Aprovada** (tratamento provisório no Portal; D-02 definitiva segue institucional) | 2026-10-09 |
| 4 | Fonte (R5) | **Aprovada** (`system-ui` + tamanho de destaque) | 2026-10-09 |
| 5 | Fotografia institucional (R7) | **Aprovada** | 2026-10-09 |
| 6 | Página pública (R9) | Pendente | — |
| 7 | Vocabulário e saudação (R8) | Pendente | — |
| 8 | Pendência no desktop (R10) | Pendente | — |
| 9 | Ordem em relação à 025 | Resolvida pelos fatos (a 025 veio antes; auditoria §13) | 2026-10-09 |
| 10 | Escopo dos protótipos | Pendente | — |

## Decisão 1 — Layout e tokens próprios do Portal

**Aprovada pelo solicitante em 2026-10-09**, nos termos abaixo.

- **R1 (delimitar).** A coluna única de 40 rem e o breakpoint único de 480 px passam a
  valer só para o instrumento e para `/acesso/`. O Portal ganha um container próprio
  (referência: cerca de 72 rem), com grade e breakpoints adicionais. Texto corrido continua
  limitado a cerca de 70 caracteres por linha.
- **R2 (revogar para o Portal).** A vedação a cards, grade de cartões e hero deixa de
  valer para o Portal. Continua valendo para o instrumento.
- **R3 (revogar para o Portal).** O Portal pode ter uma camada própria de tokens,
  acrescentada depois dos tokens da 015, sem alterar os existentes.

**Preservado:**

- o instrumento e o `interface/base.html`;
- o teste de igualdade do shell (`tests/portal/referencia_shell.html`);
- o layout de Minha trajetória e Meu e-mail com o Portal desligado
  (`TRAJETORIA_PORTAL=0`). O layout novo só vale com o Portal ligado.

**A revogar formalmente na ADR:** 015 FR-007 e FR-008 (para o Portal), 024 FR-026 e a
leitura "para a jornada" do §13 da
[auditoria de identidade visual](2026-10-03-identidade-visual.md).

## Decisão 2 — Leitura do Princípio XXI para o Portal

**Aprovada pelo solicitante em 2026-10-09**, como interpretação. A Constituição não será
emendada.

- O Portal faz parte da "jornada do egresso". O Princípio XXI vale integralmente para ele.
- O XXI veda presumir o desktop como ambiente principal. Ele não veda uma composição
  própria para o desktop.
- A ADR registra: **composição adequada a cada faixa de largura, com o celular como
  referência de qualidade**. Essa formulação substitui a expressão "composição conduzida
  pelo desktop" da auditoria (R4), que não deve ser usada.

**Critérios de aceitação a registrar na ADR:**

- Celular (mantidos da 024, sem afrouxar):
  - a 375×812, título e primeiro fato de reconhecimento sem rolar (024 FR-032, SC-004);
  - sem rolagem horizontal de 320 a 1440 px, com fonte de 100% a 200%.
- Desktop (acrescentados, auditoria §14):
  - entre 1280 e 1440 px, área de conteúdo de pelo menos 1000 px;
  - a partir de 1024 px, pelo menos duas colunas no Início; abaixo de 768 px, uma;
  - a 1280×720 e a 1440×900, descontada a faixa de demonstração: título, primeiro fato e
    prévia do card ou ação principal.
- Avaliação dos protótipos: a tela de 375 px é avaliada primeiro. Um protótipo que só
  funciona no desktop é descartado.

Uma emenda de esclarecimento (PATCH) que cite o Portal no texto do XXI fica a critério da
CPAEG e não é pré-requisito.

## Decisão 3 — Cor de ação no Portal (tratamento provisório de D-02)

**Aprovada pelo solicitante em 2026-10-09.**

- **No Portal:** Direção A da 015, verde `#195128` (9,3:1) e variante forte `#00420c`
  (11,8:1), como hipótese da demonstração. Entra pela camada de tokens do Portal
  (decisão 1), redefinindo só `--cor-acao` e `--cor-acao-forte` no base do Portal.
- **No instrumento:** continua a Direção B (azul do Padrão Digital de Governo, `#1351b4`),
  como manda a 015 FR-014, até a decisão de D-02.
- **Por que não contraria a 015 FR-014:** a regra evita levar à produção uma divergência
  do PDG. O Portal é restrito à demonstração (ADR 0008), então a divergência não chega à
  produção. O instrumento, que vai ao piloto, não muda.
- **Custo aceito:** a cor de ação muda na passagem do Portal para o instrumento (por
  exemplo, o botão do convite no Início e "Continuar" na pesquisa). Os protótipos devem
  mostrar essa passagem.
- **D-02 definitiva:** continua com Proex/CPAEG, TI e ACS (015, "Decisões pendentes").
  Decidida, uma só direção permanece no código (015 FR-013): verde no instrumento também,
  ou o Portal volta ao azul.

## Decisão 4 — Fonte do Portal

**Aprovada pelo solicitante em 2026-10-09.**

- O Portal mantém `system-ui` (015 FR-005). Nenhuma fonte é servida pela aplicação; a
  015 FR-018 continua sem exceção.
- A camada de tokens do Portal acrescenta **um** tamanho de destaque, **40 px, peso
  700**, só para o título principal (h1) das telas do Portal. Os tamanhos da 015 não
  mudam.
- A tipografia da marca (Open Sans) aparece no Portal só por meio da imagem do card, que
  já é gerada com as fontes embutidas (`narrativa/fontes`, OFL).
- **Reversível:** se os protótipos ou a implementação parecerem genéricos, Open Sans
  servida pela própria aplicação, sem CDN e só nos títulos do Portal, pode ser reavaliada.
  Isso exigiria demonstrar a necessidade (015 FR-018).

## Decisão 5 — Fotografia institucional

**Aprovada pelo solicitante em 2026-10-09**, nas quatro partes abaixo.

1. **Veto à nostalgia mantido.** Continuam fora "memória do campus", fotos do período do
   egresso e qualquer imagem que afirme retratar a época dele (021 FR-076).
2. **Correção da legenda.** A unidade só aparece na legenda quando a imagem é daquela
   unidade (`imagem.unidade == unidade`). A imagem genérica tem sempre a legenda
   "Ifes · ilustração" (`LEGENDA_SEM_UNIDADE`). Vale para o Início, a Minha trajetória e o
   card, que usam a mesma função (`trajetoria/narrativa/imagens.py`, `legenda`).
   - Revisa a leitura da 021 FR-076: a ADR registra a revisão.
   - Os PNGs de referência do card com unidade mudam e são revistos pelo solicitante.
   - Entra na primeira etapa de implementação, sem esperar as fotos.
3. **Pedido de fotografias à ACS** (ação do solicitante ou da CPAEG, não da engenharia):
   fachadas e ambientes por unidade e algumas gerais do Ifes; pessoas só com autorização
   de uso de imagem; licença que cubra também o card que o egresso publica nas redes
   sociais, e não só a tela do sistema.
4. **Protótipos sem fotos reais.** Nem imagens do site do Ifes nem de bancos de imagem. O
   espaço da foto aparece marcado como "fotografia institucional — aguarda ACS", para que
   a dependência da Direção A fique visível.
