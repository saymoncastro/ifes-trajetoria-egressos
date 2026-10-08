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
| SC-004: sem rolagem horizontal a 320 px | Início, formações, trajetória e e-mail: `scrollWidth` = 320 com fonte a 100%. Com fonte a 200%: Início, formações e e-mail = 320 | **Passa** nas telas da 024 (ver achado A1) |
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

- **A1 — Rolagem horizontal na trajetória da 021 com fonte a 200% e 320 px.**
  - O que acontece: os destaques numéricos de "Naquele ano no Ifes" (`.narrativa-numero` e
    as frases ao lado) chegam a 382 px.
  - Origem: a folha da 021, anterior à 024. A navegação não participa.
  - Encaminhamento: tratar numa correção da 021, sem misturar com esta feature.
