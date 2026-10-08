# Validação — Feature 024

Data: 2026-10-07; passada de teclado em 2026-10-08.

> **Checkpoint 1: não aplicado.** Nenhuma sessão com egressos e nenhum teste com leitor de
> tela foram feitos. Este documento registra só verificações técnicas. Os resultados com
> egressos entram em outro PR, conforme o
> [protocolo](evidencias/protocolo-checkpoint-1.md).

- **Ambiente:** banco de demonstração recriado do zero (`preparar_demonstracao`), servidor
  local e navegador do app com viewport emulado.
- **Persona:** Maria (duas formações).
- **Capturas:** em [evidencias/](evidencias/).

## Verificações do CI (T044)

| Verificação | Linha de base (T001) | Depois da 024 |
|---|---|---|
| `ruff check .` | sem erros | sem erros |
| `manage.py check` | sem problemas | sem problemas |
| `makemigrations --check --dry-run` | sem mudanças | sem mudanças |
| `pytest` | 2921 passaram, 40 pulados (4min28s) | **2979 passaram**, 40 pulados (4min28s) |

## Medidas (T045)

| Critério | Medida | Resultado |
|---|---|---|
| SC-003: entrada pelo Portal | `/` → `/entrar/` → uma identificação → `/inicio/`. Do Início, trajetória, pesquisa e e-mail estão a um toque, pela navegação ou pelas ações | **Passa** |
| SC-004: acima da dobra a 375×812 | Com a faixa de demonstração e a navegação, o `h1` e a síntese ("O Ifes registra 2 formações…") ficam visíveis sem rolar ([02](evidencias/02-inicio-topo-375.jpg)). Não foi preciso mover a ilustração | **Passa** |
| SC-004: sem rolagem horizontal a 320 px | Início, formações, trajetória e e-mail: `scrollWidth` = 320 com fonte a 100%. Com fonte a 200%: Início, formações e e-mail = 320; trajetória = 320 depois da correção do achado A1 (2026-10-08) | **Passa** (A1 corrigido) |
| SC-007: Seções inalteradas | O HTML do cabeçalho de `/acesso/` e de uma Seção é idêntico ao gravado na T001 (`tests/portal/test_navegacao.py::test_shell_sem_navegacao_identico`). As Seções não têm navegação | **Passa** |
| SC-002: caminho do convite | `/acesso/` → `/formacoes/` → Seções, com os mesmos endereços e o mesmo número de telas e toques. A escolha de formações ganha a faixa de navegação, de cerca de 45 px, e a frase "A pesquisa tem no máximo 9 partes." O número bate com o "9 partes" previsto pela reauditoria R-02 ([04](evidencias/04-formacoes-navegacao-375.jpg)) | **Passa** (nenhuma tela nem toque a mais) |
| SC-005: Portal desligado | `tests/portal/test_desabilitado.py`: a raiz é a da 008, `/entrar/` e `/inicio/` dão 404, nenhuma tela tem `<nav`, e o convite funciona até a confirmação | **Passa** |
| SC-006: nada gravado | `tests/portal/test_fronteiras.py::test_portal_nao_grava` e `tests/portal/test_trajetoria_antes.py`. Só o pedido explícito de vídeo grava (`GeracaoDeVideo`) | **Passa** |

## Acessibilidade (T046)

- **Verificado por teste:**
  - um `h1` por página;
  - `nav` com nome acessível ("Portal do Egresso");
  - `aria-current="page"` no item atual;
  - origem dos fatos em texto, não em cor;
  - nenhum `<script>` na navegação.
- **Verificado no HTML e na folha de estilo, sem roteiro de teclado gravado:**
  - a ordem do documento é "Pular para o conteúdo" → "Sair" → cabeçalho → itens da navegação → conteúdo;
  - o foco é a regra global `:focus-visible` da 015, sem sobrescrita;
  - os itens da navegação e as ações do Início têm `min-height: var(--alvo)` (44 px).
- **Passada de teclado (2026-10-08, banco recriado, 375×812, persona Maria):**
  - **`/entrar/`.** Ordem de foco: "Pular para o conteúdo" → CPF → data → "Continuar" →
    botões do painel. Todos com o contorno de 3 px e o halo da 015.
  - **`/inicio/`.** Ordem de foco: "Pular para o conteúdo" → "Sair" → Início → Minha
    trajetória → Pesquisa → Meu e-mail → as três ações → "Escolher a formação". "Sair",
    os itens da navegação, as ações e o convite têm 44 px de altura. O link "Pular para o
    conteúdo" tem 40 px: é o mesmo da 015, anterior à 024, e fica acima do mínimo de
    24 px da WCAG 2.2, mas abaixo dos 44 px da 014. "Pular para o conteúdo" põe o foco em
    `main#conteudo`.
  - **Árvore de acessibilidade.** `banner`, `navigation` "Portal do Egresso" (item atual
    com `aria-current="page"`), `main`, duas `region` nomeadas pelos `h2`, `contentinfo`.
    Títulos h1 → h2 → h2. A ilustração não aparece na árvore; a legenda aparece como texto.
- **Não realizado:** teste com leitor de tela real (VoiceOver ou NVDA). Ver P4 em
  [checkpoint-1/preparacao-sessao.md](evidencias/checkpoint-1/preparacao-sessao.md).

## Ajustes feitos durante a validação

- **Nome do produto na entrada do Portal.** A tela `/entrar/` mostrava "Trajetória Ifes" no
  cabeçalho. O bloco neutro `produto` passou a aceitar o nome por contexto: `produto` e
  `produto_subtitulo`. A identificação recebe esse contexto do Portal sem conhecê-lo.
- **Origem repetida.** "Registro do Ifes" aparecia também na linha de atributos
  ("Graduação · Presencial"). Agora a linha de atributos herda a origem do fato anterior.
- **Rolagem a 200%.** O rótulo de origem tinha `white-space: nowrap` e transbordava a 320 px.
  O `nowrap` foi removido.
- **Borda dupla antes do convite.** Removida.
- **Dependência de ordem nos testes.** `config/urls.py` avaliava as rotas na importação.
  Importado pela primeira vez num teste com o Portal desligado, fixava as rotas sem o Portal
  para o resto da sessão. A função `rotas` foi para `config/rotas.py`, que não faz avaliação
  na importação.

## Achados fora do escopo

- **A1 — Rolagem horizontal na trajetória da 021 com fonte a 200% e 320 px. Corrigido em 2026-10-08.**
  - O que acontecia: os destaques numéricos de "Naquele ano no Ifes" (`.narrativa-numero` e
    as frases ao lado) chegavam a 382 px. A linha do tempo também transbordava, encoberta
    pelos destaques.
  - Origem: a folha da 021, anterior à 024. A navegação não participa.
  - Correção: só no CSS da 021. Respiro lateral `min(1rem, 5vw)`, hifenização de palavras
    longas e grade dos destaques com `minmax(0, 1fr)`. Detalhes na nota de correção da
    [spec da 021](../021-minha-trajetoria-narrativa/spec.md) e no PR #43.
  - Verificação: com Maria (SIM-P-0003), `scrollWidth` igual à largura a 320 px e a 375 px,
    com fonte a 100% e a 200%. Teste:
    `tests/narrativa/test_pagina.py::test_css_cabe_em_320px_com_fonte_a_200`.

## Revisão pós-avaliação por IA (2026-10-08)

**Origem.** Achados A1 a A4, A6 e A7 da
[avaliação por IA dos checkpoints](../../docs/auditorias/2026-10-08-portal-checkpoints-avaliacao-ia.md),
priorizados pelo solicitante antes da primeira sessão. Os requisitos estão na spec: FR-020 e
FR-024 revisados, e FR-034 a FR-036 novos.

**O Checkpoint 1 continua NÃO APLICADO.** Esta revisão só corrige inconsistências observáveis.

| Achado | O que mudou | Verificação no navegador (375×812, banco da avaliação) |
|---|---|---|
| A1 — nome do produto | "Portal do Egresso" no cabeçalho e no rodapé das cinco telas com navegação. "Trajetória Ifes" nas Seções, em concluir e em `/acesso/` | Início, formações, trajetória e e-mail: "Portal do Egresso". Seção de Diego e `/acesso/`: "Trajetória Ifes" |
| A2 — "Sair" | Nas telas com navegação, POST para `/sair/` → `/entrar/`. Nas Seções, continua `/acesso/sair/` | Sair no Início levou a "Confirme seus dados para entrar no Portal do Egresso". Na Seção, a ação é `/acesso/sair/` |
| A3/A4 — fim de página | "Voltar ao Início" no fim da trajetória e do e-mail ([02](evidencias/revisao-2026-10-08/02-trajetoria-fim-voltar-ao-inicio-375.jpg)) | Trajetória e e-mail de Diego: "Voltar ao Início" → `/inicio/` |
| A6 — alvo do "Sair" | `min-width` e `min-height` de 44 px | 44×44 px medidos |
| A7 — convite em andamento | "Você começou a responder a pesquisa sobre {curso}. Pode continuar de onde parou; …". A Seção exata continua em `/formacoes/`, porque o Início não lê Respostas (FR-017) ([01](evidencias/revisao-2026-10-08/01-inicio-convite-retomar-375.jpg)) | Diego, com rascunho no Mestrado: texto novo e "Continuar". O convite ficou na mesma posição (1.512 px) |

- **Sem o Portal** (`tests/portal/test_desabilitado.py::test_shell_saida_e_retorno_de_hoje`),
  ficam os de hoje:
  - o nome "Trajetória Ifes";
  - "Sair" por `/acesso/sair/`;
  - os links de fim de página;
  - `/sair/` responde 404.
- **Testes revisados com rastreabilidade:**
  - 015: `test_interface_identidade.py`, com nome e "Sair" por tela;
  - 018: `test_sessao.py`, com "Sair" em `/formacoes/`;
  - 021: `test_pagina.py`, com o fim da página;
  - 024: T039.
- **Ficam para depois:**
  - A5 (quebra da navegação a 375 px), com a 025;
  - A8 e A11 (textos da 021 e da 014), depois do teste.
