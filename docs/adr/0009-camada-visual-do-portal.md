# ADR 0009 — Camada visual própria do Portal do Egresso, com o instrumento preservado

- **Status**: Aceito como hipótese de produto, só para a demonstração. Decidido pelo
  solicitante em 2026-10-09, decisão por decisão. A identidade visual para produção continua
  pendente (DP-801, D-02, D-03, D2, DP-2106).
- **Data**: 2026-10-09
- **Contexto de origem**:
  - [Auditoria de experiência e direção visual do Portal](../auditorias/2026-10-08-portal-ux-direcao-visual.md)
    (§9, R1–R10; §14, critérios; §15, decisões)
  - [Registro das decisões](../auditorias/2026-10-09-portal-ux-decisoes.md), com o texto
    aprovado de cada uma
  - [ADR 0008](0008-portal-do-egresso-camada-de-relacionamento.md) (Portal só na
    demonstração; coleta independente)
  - Specs [015](../../specs/015-identidade-visual-jornada/spec.md),
    [018](../../specs/018-identificacao-acesso-egresso/spec.md),
    [021](../../specs/021-minha-trajetoria-narrativa/spec.md),
    [024](../../specs/024-inicio-egresso-portal/spec.md) e
    [025](../../specs/025-oportunidades-curadas-portal/spec.md)

## Contexto

O Portal parece uma tela de tarefa porque foi especificado como uma. A
[auditoria de identidade visual](../auditorias/2026-10-03-identidade-visual.md) definiu, **para
a jornada de resposta**, uma coluna única de 40 rem, um breakpoint, nenhum card nem hero. A
015 tornou isso requisito do shell inteiro. A 024 abriu o Portal sobre o mesmo shell e
proibiu tokens novos, grade de cartões e hero (FR-026).

O resultado medido em 2026-10-08:

- a 1440 px, o conteúdo usa 640 px (44% da largura);
- o desktop repete a composição do celular, centralizada;
- a 1280×720, a primeira tela do Início não mostra nenhum fato nem ação;
- não existe página pública: `/` leva direto ao formulário;
- o card e os números do ano, o conteúdo mais forte, ficam fora do Início.

Um redesenho não é ajuste de CSS: sem revogar ou delimitar as decisões vigentes, a próxima
feature de interface reproduziria o padrão atual.

## Alternativas consideradas

- **Restilizar dentro das regras atuais** (coluna de 40 rem, sem cards). Rejeitada: não
  resolve P1, P2, P3 nem P5 da auditoria.
- **Um único padrão novo para todo o sistema**, instrumento incluído. Rejeitada: o
  instrumento funciona, foi validado (014, 015, 023) e vai ao piloto. Redesenhá-lo não é
  necessário para o Portal.
- **Emendar a Constituição** para tratar o Portal à parte no Princípio XXI. Rejeitada: o
  texto atual acomoda o redesenho, e a emenda exigiria o rito de versão sem mudar regra.
- **Camada visual própria do Portal, com o instrumento intacto.** Escolhida.

## Decisão

### 1. Layout e tokens próprios do Portal

- A coluna única de 40 rem e o breakpoint único de 480 px valem só para o instrumento e
  para `/acesso/`.
- O Portal tem container próprio (referência: cerca de 72 rem), com grade e breakpoints
  adicionais. Texto corrido continua limitado a cerca de 70 caracteres por linha.
- No Portal são admitidos cards, grade de cartões e hero. A vedação continua no
  instrumento.
- O Portal tem uma camada de tokens incluída depois dos tokens da 015, que não mudam.
- **Preservados:** o instrumento; `interface/base.html`; o teste de igualdade do shell
  (`tests/portal/referencia_shell.html`); o layout de Minha trajetória e Meu e-mail com o
  Portal desligado (`TRAJETORIA_PORTAL=0`). O layout novo vale só com o Portal ligado.

### 2. Princípio XXI: interpretação, sem emenda

- O Portal faz parte da jornada do egresso. O XXI vale integralmente para ele.
- O XXI veda presumir o desktop como ambiente principal. Ele não veda composição própria
  para o desktop.
- Regra: **composição adequada a cada faixa de largura, com o celular como referência de
  qualidade.** A expressão "composição conduzida pelo desktop" não é usada.
- Uma emenda de esclarecimento (PATCH) que cite o Portal no XXI fica a critério da CPAEG e
  não é pré-requisito.

### 3. Cor de ação: verde só no Portal, como tratamento provisório de D-02

- No Portal: Direção A da 015, `--cor-acao: #195128` (9,3:1) e `--cor-acao-forte: #00420c`
  (11,8:1), pela camada de tokens do Portal.
- No instrumento: Direção B (`#1351b4`), como manda a 015 FR-014, até a decisão de D-02.
- A 015 FR-014 evita levar à produção uma divergência do Padrão Digital de Governo. O
  Portal é restrito à demonstração (ADR 0008), e o instrumento não muda.
- Custo aceito: a cor de ação muda na passagem do Portal para o instrumento.
- D-02 definitiva: Proex/CPAEG, TI e ACS. Decidida, uma só direção permanece no código (015
  FR-013).

### 4. Fonte: `system-ui` e um tamanho de destaque

- O Portal mantém `system-ui` (015 FR-005). Nenhuma fonte é servida pela aplicação (015
  FR-018).
- A camada do Portal acrescenta **um** tamanho de destaque, 40 px e peso 700, só para o h1
  das telas do Portal.
- **Esclarecimento (2026-10-09, solicitante):** os 40 px valem a partir de 768 px de
  largura. No celular, o h1 mantém os 28 px da 015, para que título e primeiro fato caibam
  na primeira tela (critério do celular, decisão 2). É o comportamento da Feature 028.
- A tipografia da marca (Open Sans) aparece por meio da imagem do card, que já a embute.
- Reversível: Open Sans servida pela aplicação, só nos títulos, pode ser reavaliada se os
  protótipos ou a implementação parecerem genéricos, demonstrando a necessidade (015
  FR-018).

### 5. Fotografia institucional

- Mantido o veto à nostalgia: sem "memória do campus", fotos do período do egresso ou
  imagem que afirme retratar a época dele (021 FR-076).
- **Legenda.** A unidade só aparece na legenda quando a imagem é daquela unidade. A imagem
  genérica tem sempre a legenda "Ifes · ilustração". Vale para o Início, a Minha trajetória
  e o card, que usam a mesma função (`trajetoria/narrativa/imagens.py`, `legenda`).
- Pedido de fotografias à ACS, a cargo do solicitante ou da CPAEG: fachadas e ambientes por
  unidade e algumas gerais; pessoas só com autorização de uso de imagem; licença que cubra
  também o card publicado pelo egresso nas redes sociais.
- Protótipos sem fotografia real: o espaço aparece marcado como "fotografia institucional —
  aguarda ACS".

### 6. Página pública

- `/` sem sessão mostra uma página pública; com sessão, continua levando ao Início.
  `/entrar/` não muda. A 024 FR-005 continua atendida: a página é a entrada do Portal.
- O convite não passa por ela: `/acesso/` segue direto para a identificação e o
  instrumento (D7; 024 SC-002).
- Só conteúdo: sem regra de negócio, dado pessoal nem JavaScript; só com o Portal ligado.
- Só o que existe: trajetória, card, oportunidades divulgadas pelo Ifes, contato e
  pesquisa. Oportunidades não aparecem como benefício garantido.
- Linguagem da 018 FR-061: sem "login", "conta" ou "acesso seguro". "Entrar no Portal" e
  "Confirme seus dados" são admitidos.
- Imagem principal, enquanto não houver fotografia: um card de exemplo com persona
  fictícia e o selo "Exemplo com dados fictícios".
- Textos: provisórios da equipe na demonstração, sem slogan. Para uso real, a ACS aprova
  com a CPAEG, incluindo o nome (D2) e a linguagem (DP-801).

### 7. Vocabulário e saudação

- O Início reconhece a pessoa pela formação (curso, unidade, ano e números do ano), e não
  pelo nome. O nome continua discreto na Minha trajetória e no card por escolha (DP-2103).
- Mantidas as vedações verificadas em teste da 024 (FR-019, FR-021): sem nome no Início;
  sem "minuto", "%", "turma", "geração", "conectad", "Olá", "Volte ao Ifes", "comunidade";
  "Oportunidade" só no bloco da 025; "pesquisa" só no convite, na navegação e no cabeçalho
  do produto.
- Na página pública valem as mesmas vedações, exceto "Oportunidades" e "pesquisa", que
  podem aparecer.

### 8. A pesquisa pendente no desktop

- A ordem visual é igual à ordem de leitura (024 FR-016, FR-020) em todas as larguras. O
  convite vem depois do reconhecimento, das ações e de Oportunidades. Nenhuma coluna lateral
  o antecipa.
- Motivos: a hipótese do Portal (024 SC-014, SC-016), a ordem de foco (WCAG 2.4.3) e o item
  "Pesquisa" na navegação (SC-012).
- Revisão: se o Checkpoint 1 mostrar que as pessoas não encontram a pesquisa (SC-012
  falha), a posição volta à discussão.

### 9. Ordem em relação à 025

Resolvida pelos fatos: a 025 foi integrada no shell atual (PR #49). O redesenho do Início
absorve o bloco `section.inicio-oportunidades` e suas variantes de compactação; a página
`/oportunidades/` entra na harmonização.

### 10. Escopo dos protótipos

- Três direções: A (institucional), B (trajetória) e a combinação, todas dentro das
  decisões 1 a 8.
- Nove telas: página pública, Início da Ana (uma formação) e Início do Diego (três
  formações), em cada direção.
- Larguras 375, 1024 e 1440 px; primeira tela a 1280×720; 320 px com fonte a 200%.
  Avaliação pelo celular primeiro.
- Uma prancha da passagem do Portal para o instrumento (decisão 3).
- HTML estático com os tokens reais, sem JavaScript, com dados das personas fictícias.
- Entrega: página de comparação lado a lado e tabela com os critérios abaixo medidos. O
  solicitante escolhe; pode mostrar à ACS e à CPAEG antes.
- Fora: Minha trajetória, Meu e-mail, Oportunidades e `/entrar/`, que entram na
  harmonização, na direção escolhida.

### Critérios de aceitação da camada visual

**Celular** (mantidos da 024, sem afrouxar):

- a 375×812, título e primeiro fato de reconhecimento sem rolar (024 FR-032, SC-004);
- sem rolagem horizontal de 320 a 1440 px, com fonte de 100% a 200%.

**Desktop:**

- entre 1280 e 1440 px, área de conteúdo de pelo menos 1000 px;
- a partir de 1024 px, pelo menos duas colunas no Início; abaixo de 768 px, uma;
- a 1280×720 e a 1440×900, descontada a faixa de demonstração: título, primeiro fato e
  prévia do card ou ação principal.

**Página pública:**

- a 1280×720, descontada a faixa, a proposta e a ação de entrar sem rolar;
- o formulário de identificação não é o h1 de `/`;
- nenhum link para área inexistente (024 FR-021).

**Acessibilidade e fronteira:**

- alvos de pelo menos 44×44 px; foco da 015; um h1 por página; nada comunicado só por cor;
  funciona sem JavaScript;
- contraste AA nos tokens novos, medido e registrado como na 015;
- `tests/portal/referencia_shell.html` passa sem alteração;
- nenhuma tela ou toque a mais no caminho do convite (024 SC-002);
- sem dependência nova, CDN ou fonte externa;
- assinatura sem alteração (015 FR-017); nenhuma imagem genérica legendada com nome de
  unidade.

**Revisão visual:** cada PR de implementação traz capturas nas larguras acima, lado a lado
com o protótipo aprovado.

## Consequências

- **Constituição.** Não muda. A decisão 2 é interpretação do Princípio XXI.
- **Requisitos que as specs de implementação devem revisar, de forma explícita** (seção
  "Requisitos revisados", como na 025):
  - 015 FR-007 e FR-008: delimitados ao instrumento e a `/acesso/` (decisão 1);
  - 015 FR-014: verde no Portal como tratamento provisório (decisão 3);
  - 024 FR-026: tokens, grade de cartões e hero admitidos no Portal (decisão 1);
  - 024 FR-005 e a rota `entrada`: página pública em `/` sem sessão (decisão 6);
  - 021 FR-076, legenda: unidade só quando a imagem é daquela unidade (decisão 5).
- **A leitura "para a jornada"** do §13 da auditoria de identidade de 2026-10-03 fica
  delimitada ao instrumento.
- **Ordem do trabalho** (auditoria §13):
  1. protótipos (decisão 10) e escolha da direção;
  2. spec da camada visual e implementação em etapas: base do Portal, página pública,
     Início, `/entrar/` (painel fictício recolhido, P10), harmonização das demais telas e
     acabamento;
  3. a correção da legenda (decisão 5) entra na primeira etapa, sem esperar as fotos.
- **Ações externas, sem bloquear a demonstração:** fotografias (ACS), D-02 (Proex/CPAEG, TI
  e ACS), textos da página pública e nome (ACS com CPAEG; D2, DP-801).
- **Checkpoint 1** continua NÃO APLICADO. Esta ADR não o substitui. A decisão 8 depende do
  resultado dele para ser revista.
- **Reversão.** A camada visual vive no base e nos tokens do Portal. Removê-la devolve o
  Portal ao shell da 015, sem tocar o instrumento nem o núcleo.
