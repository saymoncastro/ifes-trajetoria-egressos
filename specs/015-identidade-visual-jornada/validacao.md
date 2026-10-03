# Registro de validação — Feature 015 (gate)

Formato: [contracts/registro-validacao.md](contracts/registro-validacao.md). **Só texto.**
As capturas **não são versionadas**: ficam fora do repositório e serão anexadas ao PR pelos
identificadores abaixo (`R{rodada}-G{situação}-{A|B}-{largura}-{fonte}`).

> **Estado (2026-10-03, rodada 3, final): gate de critérios objetivos APROVADO — 46/46 tasks.**
> Identidade visual implementada e tecnicamente validada para a jornada; validação
> institucional para produção pendente (DP-801, D-02, D-03).
>
> - Rodada 3 (revisão do solicitante): assinatura com símbolo de 36 px a partir de 352 px
>   (cabeçalho de 68 px; FR-016 atualizado com o limite medido) e 48 px entre a
>   confirmação e a ficha (FR-029). Verde do fio × verde do ativo: pergunta para a ACS em
>   D-03 (c), sem mudança.
> - T015 (assinatura) e T041 (rodada final) concluídas com o SVG **derivado do EPS
>   oficial e aceito pelo solicitante** (research R3; SHA-256 `bb357837…387fc7`). Não é um
>   SVG fornecido pela ACS.
> - **D-03 continua aberta**: validação do ativo e do uso em publicação/produção pela ACS;
>   as cores do ativo diferem dos HEX do Manual (registrado, não alterado).
> - **Revisão perceptiva pendente** (ACS, CPAEG/Proex; se possível, egressos) — não
>   bloqueia o merge (FR-043), mas não foi feita.
> - Direção B mergeável como valor provisório (D-02 aberta); A comparada.
> - Propagação para editor, acompanhamento e 403/404/500: decisão posterior ao merge.

**Situação do gate: APROVADO na rodada 2 (critérios objetivos SC-001 a SC-014).** A
rodada 1 foi feita sem a assinatura e ficou bloqueada por D-03; a rodada 2 repetiu tudo com
o ativo aceito pelo solicitante. Revisão perceptiva e validação do ativo pela ACS seguem
pendentes (não bloqueiam o merge).

---

## Rodada 1 — 2026-10-03 (sem a assinatura; histórico)

### Cabeçalho

| Item | Valor |
|---|---|
| Código medido | `claude/feature-015-identidade-visual` = `main` `b4476ce` + alterações não commitadas da 015 (working tree) |
| Navegador | Chromium do painel do Claude Code, viewport emulada; larguras por iframe de largura fixa com o HTML servido; "fonte a 200%" = `font-size: 200%` no elemento raiz |
| Banco | `trajetoria_015`, só Pessoas fictícias (`preparar_demonstracao`) |
| Direção mergeada | **B** (`--cor-acao: #1351b4`, `--cor-acao-forte: #0c326f`) |
| `--raio` medido | 4 px (comparado com 0 px — ver Comparações) |
| Divisor entre Perguntas | ausente (comparado com presente — ver Comparações) |
| Assinatura | **Bloqueada por D-03**: o ZIP oficial (`marca-ifes.zip`, SHA-256 `3834b6e8…58121a12`) não contém SVG; nada a substitui no cabeçalho |

### Estados medidos

| Id | Situação | Estado |
|---|---|---|
| G1a | Trajetória — Maria | Seleção entre duas formações |
| G1b | Trajetória — Diego | Aviso `salvo` após "Salvar e sair"; outras formações com ambiguidade |
| G2 | Seção 8 "Avaliação" — Elisa | 14 Perguntas, escalas, rádios, caixas, "Outro"; Opção e ponto marcados nas capturas |
| G3p | Seção 2 com pendências — Ana | 1 Pergunta respondida, envio aceito |
| G3e | Seção 8 com erro de forma — Elisa | Descrição de "Outro" sem a Opção |
| G4c / G4f | "Concluir a pesquisa" → "Pesquisa concluída" — Maria | Fim da jornada |

### Medidas (Direção B)

Larguras 375, 390, 430 e 1280 px a 100%; 320, 375, 390, 430 e 1280 px a 200%.

| Critério | Resultado | Medida |
|---|---|---|
| SC-001 — assinatura na 1ª viewport, símbolo ≥ 30 px, área de proteção | **⛔ impossível (D-03)** | Sem ativo oficial em SVG |
| SC-002 — cabeçalho ≤ 64 / ≤ 80 px; rodapé ≤ 120 px | **Parcial** | Cabeçalho **sem a assinatura**: 52 px (375–430) e 53 px (1280). Rodapé sem a linha de demonstração: 76 px. A altura com a assinatura só pode ser medida com o ativo (research R3 estima ≈ 62–64 px a 375 px) |
| SC-003 — texto ≥ 4,5:1; contornos e estados ≥ 3:1; verde da marca nunca texto | Aprovado | Texto: mínimo **6,74:1** em todas as telas e larguras (nenhum abaixo). Contornos de campo, lista, célula da escala e botão: mínimo **6,74:1**. Verde da marca só em bordas (inventário abaixo) |
| SC-004 — foco visível, inclusive resumo focado ao carregar | Aprovado (regra) | Foco inalterado (`:focus-visible` 3 px + halo 6 px); `.resumo-erros:focus` com o mesmo contorno e halo (teste `test_resumo_focado_ao_carregar_tem_foco_visivel`) |
| SC-005 — sem rolagem horizontal, 320–1280 px, 100–200% | Aprovado **após correção** | Reprovado inicialmente em G3p a 320 px/200%: o `h1` "Informações Pessoais" (palavra "Informações") excedia a coluna (`scrollWidth` 354 em 320). Causa anterior à 015 (`h1` e coluna inalterados). Correção na mesma branch: `h1, h2 { overflow-wrap: break-word; hyphens: auto }` em `jornada.css` (teste primeiro). Remedido: 0 rolagem em todas as combinações |
| SC-006 — 014 SC-006 a SC-010 | Aprovado | Escala 1–5 numa linha em 320, 375, 390, 430 px a 100% e 200% (célula mínima 45×114 px a 320/200%); linhas de Opção ≥ 44 px (88 px a 200%); botões do rodapé em largura total ≤ 480 px (inalterado); primeira ação na 1ª tela de 375×667 descontada a faixa: Maria 492 px, Diego 469 px |
| SC-007 — pendência × erro sem depender de cor | Aprovado | Títulos ("Ainda faltam estas perguntas:" × "Há problemas nesta seção"), prefixos ("Falta responder:" × "Erro:") e título da aba distintos; forma igual (fio de 4 px + contorno) |
| SC-008 — 48 px entre Perguntas; enunciado 18/600; auxiliar 15 px suave; sem card | Aprovado | Testes `test_ritmo…`, `test_tipografia…`, `test_pergunta_sem_card_nem_sombra`; captura `R1-G2-B-375-100` |
| SC-009 — estados selecionados; células delimitadas | Aprovado | `:has(input:checked)` com acento de 4 px + fundo de seleção; células com contorno 1 px `#565c65` (6,74:1); capturas `R1-G2-B-375-100`, `R1-G2-A-375-100` |
| SC-010 — A↔B só nos dois tokens de ação | Aprovado | Diff A × B = exatamente as linhas de `--cor-acao` e `--cor-acao-forte`; B restaurada (diff vazio contra a cópia B) |
| SC-011 — inventário do verde | Aprovado | B: fio do cabeçalho (marca), fio e fundo do contexto/ficha (marca, institucional), acento do aviso `salvo` e da confirmação (sucesso). Nenhum vermelho da marca na interface |
| SC-012 — editor e acompanhamento sem mudança não intencional | Aprovado | Impressão digital de estilos computados (22 propriedades + geometria de cada elemento) antes × depois, 375 e 1280 px: lista de Pesquisas, edição de Pergunta, estrutura da Versão (009), painel de Campanha (011) **idênticos**. Prévia de Seção (009): diferenças **só dentro das Perguntas**; espaço entre Perguntas continua 8 px (composição do editor) |
| SC-013 — suíte; sem JS, modelo, migração, recurso externo | Aprovado | `uv run pytest`: 1842 passed; `ruff check` limpo; `makemigrations --check`: sem mudanças; nenhum `<script>`, `<link>`, `src/href` externo, `@import` ou `url(` externo nas telas da jornada (teste) |

**Peso inline (T044):** `jornada.css` 6.103 bytes (alvo ≤ 6 KB = 6.144 bytes); `estilo.css`
11.830 bytes (era 7.257); SVG da assinatura: ⛔ não medível (D-03).

**Medidas a 200%** (informativas; os limites de SC-002 valem a 100%): cabeçalho 98–101 px,
rodapé 150–195 px.

### Comparações

- **Direção A × B** — mesmos estados, CSS servido com as duas linhas de token trocadas
  (`#195128` / `#00420c`) e depois restaurado:
  - contraste: texto ≥ 6,74:1 nas duas; contornos ≥ 6,74:1 (B) e ≥ 6,74:1 (A; botões
    9,34:1);
  - verde: na A, além dos lugares da B, ligações, botões, `accent-color` e estado
    selecionado — exatamente o item (3) de FR-004;
  - observação para a decisão: na A, o aviso `salvo` e o botão principal usam o mesmo
    verde (sucesso = ação), sempre acompanhados de texto;
  - pares de captura: `R1-G1b-B-375-100` × `R1-G1b-A-375-100`; `R1-G2-B-375-100` ×
    `R1-G2-A-375-100`; `R1-G4f-B-375-100` × `R1-G4f-A-375-100`.
- **Raio 0 × 4 px** (G3e a 375 px): `R1-G3e-B-375-100-raio0` × `R1-G3e-B-375-100`. Com
  0 px a tela volta à gramática de cantos retos que a auditoria quis atenuar (IV-13); com
  4 px só nas células da escala, campos e botões ficavam retos — incoerente. **Decisão:
  4 px**, aplicado ao mesmo token em campos, listas, células da escala e botões da jornada
  (teste `test_raio_unico_nos_controles`). Avisos, resumos e contexto continuam retos (são
  superfícies com fio lateral).
- **Divisor entre Perguntas** (G2 a 375 px): `R1-G2-B-375-100-com-divisor` ×
  `R1-G2-B-375-100-sem-divisor`. Os 48 px já separam as Perguntas; o divisor só acrescenta
  linhas (excesso de bordas, IV-08). **Decisão: sem divisor.**
- **Ícones:** não avaliados nesta rodada; nenhum ícone na implementação (FR-030 opcional).

### Observações (não são critérios)

- Na confirmação, o fio de sucesso (`#195128`) fica logo acima do fio da ficha (verde da
  marca `#2f9e41`): dois verdes vizinhos. Coerente com os papéis, mas vale olhar na revisão
  perceptiva.
- Capturas a 375 px foram feitas a partir do cabeçalho do produto (a faixa de demonstração
  fica acima, fora do enquadramento), que é o que o gate mede.

### Capturas desta rodada (fora do repositório)

`R1-G1a-B-375-100`, `R1-G1b-B-375-100`, `R1-G1b-B-1280-100`, `R1-G1b-A-375-100`,
`R1-G2-B-375-100`, `R1-G2-A-375-100`, `R1-G2-B-375-100-com-divisor`,
`R1-G2-B-375-100-sem-divisor`, `R1-G3p-B-375-100`, `R1-G3p-perguntas-B-375-100`,
`R1-G3p-B-1280-100`, `R1-G3e-B-375-100`, `R1-G3e-B-375-100-raio0`, `R1-G4c-B-375-100`,
`R1-G4f-B-375-100`, `R1-G4f-B-1280-100`, `R1-G4f-A-375-100`.

### Resultado da rodada 1

- Critérios objetivos sem a assinatura: **aprovados** (SC-003 a SC-013), após a correção de
  SC-005.
- **SC-001: impossível sem o SVG oficial (D-03). SC-002: só parcialmente medível.**
- **Gate: NÃO APROVADO** — aguarda o SVG oficial (tasks T015) e a rodada final (T041).
- **Revisão perceptiva:** pendente (ACS, CPAEG/Proex; se possível, egressos). Não
  automatizada; não bloqueia o fechamento, mas também não foi feita.
- **Itens para a propagação futura:** shell em 403/404/500 (handlers globais — research
  R5); shell do editor e do acompanhamento.

---

## Rodada 2 — 2026-10-03 (final, com a assinatura)

### Cabeçalho

| Item | Valor |
|---|---|
| Código medido | `claude/feature-015-identidade-visual` em `20bc38b` + T015 (working tree antes do commit da rodada) |
| Navegador e banco | Os mesmos da rodada 1 |
| Direção mergeada | **B** |
| Assinatura | `interface/assinatura.svg` = `ifes-horizontal-cor.svg` **derivado do EPS oficial, aceito pelo solicitante**, byte a byte (SHA-256 `bb35783718560dca4ce1a6a20a8fca283881b9371fceb1b4a72f57ce7f387fc7`, 28.063 bytes), incluído inline (research R3) |
| Estados | Os mesmos de G1a a G4f, com o `<style>` e o `<header>` atuais servidos pelo sistema (o cabeçalho é o mesmo template em todas as telas) |

### Medidas

| Critério | Resultado | Medida |
|---|---|---|
| SC-001 — assinatura na 1ª viewport a 375 px, símbolo ≥ 30 px, área de proteção | **Aprovado** | Altura do ativo 54 px → **símbolo 31 px**; módulo 6,7 px; margens do próprio ativo 7,8–12,3 px em todos os lados (≥ 1 módulo), nada dentro delas. A 375 × 667 com a faixa de demonstração acima, a assinatura ocupa y 170–224 px (na 1ª viewport). A 375 px com fonte a 200%, só a faixa de demonstração (674 px de altura) a empurra para fora da dobra; sem a faixa (produção), fica no topo |
| SC-002 — cabeçalho ≤ 64 / ≤ 80 px; rodapé ≤ 120 px | **Aprovado** | Cabeçalho **59 px** a 375, 390, 430 e 1280 px; rodapé 76 px (a 200%: cabeçalho 85–181 px, com o nome abaixo da assinatura a ≤ 430 px; informativo) |
| SC-003 — contraste | Aprovado | Texto ≥ 6,74:1 e contornos ≥ 6,74:1 em 7 estados × 9 combinações; 0 abaixo |
| SC-004 — foco | Aprovado | Regras inalteradas desde a rodada 1 |
| SC-005 — sem rolagem horizontal | Aprovado | 0 em 320–1280 px, 100–200%, nos 7 estados |
| SC-006 — 014 SC-006 a SC-010 | Aprovado | Primeira ação na 1ª tela de 375 × 667 descontada a faixa: Maria 499 px, Diego 476 px; escala e alvos inalterados |
| SC-007 a SC-011 | Aprovados | Sem mudança desde a rodada 1; inventário do verde idêntico (fio do cabeçalho, contexto e ficha, sucesso); vermelho da marca só dentro da assinatura |
| SC-012 — administração | Aprovado | Impressões de estilos computados repetidas com o código final: editor e acompanhamento **idênticos**; prévia muda só dentro das Perguntas (8 px entre Perguntas mantidos) |
| SC-013 — suíte e fronteiras | Aprovado | `uv run pytest`: **1846 passed**; `ruff check` limpo; sem migração, JavaScript ou recurso externo; ativo idêntico ao recebido (teste por SHA-256) |
| SC-014 — registro completo | Aprovado | Este documento (rodadas 1 e 2), com A × B, raio, divisor e estado da revisão perceptiva |

**Peso inline:** assinatura 28.063 bytes (alvo ≤ 30 KB); `jornada.css` ≈ 6,5 KB após o
dimensionamento da assinatura (alvo de ≤ 6 KB ultrapassado em ≈ 0,4 KB — hipótese de plan,
não critério de sucesso; registrado).

### Comparação A × B com a assinatura

Mesma troca exclusiva de `--cor-acao`/`--cor-acao-forte` aplicada ao CSS servido:
`R2-G1b-A-375-100` × `R1-G1b-B-375-100` (o cabeçalho é idêntico nas duas direções — a
assinatura e o fio não dependem da cor de ação).

### Observações para a revisão perceptiva

- No tamanho mínimo do Manual (símbolo de 31 px), o lettering do próprio ativo
  ("INSTITUTO FEDERAL / Espírito Santo") fica **muito pequeno** a 375 px. Aumentá-lo
  exigiria passar do limite de 64 px do cabeçalho (FR-016, hipótese reversível). Decisão
  de produto/ACS.
- As cores do ativo (verde `#37a033`, vermelho `#cf181f`) diferem levemente do verde da
  marca usado no fio (`#2f9e41`), que vem do Manual.
- Mantêm-se as observações da rodada 1 (dois verdes vizinhos na confirmação).

### Capturas desta rodada (fora do repositório)

`R2-G1a-B-375-100`, `R2-G4f-B-375-100`, `R2-G1b-A-375-100`, `R2-G3p-B-1280-100` (mais as da
rodada 1 para os aspectos que não dependem da assinatura).

### Resultado da rodada 2

- **Critérios objetivos SC-001 a SC-014: aprovados. Gate aprovado → 015 pronta para PR.**
- Revisão perceptiva: **pendente**.
- D-03 (validação do ativo e uso em publicação/produção pela ACS) e D-02 (aplicação do
  PDG): **abertas**.
- Itens para a propagação futura: shell em 403/404/500; shell do editor e do
  acompanhamento.

---

## Rodada 3 — 2026-10-03 (final; revisão do solicitante: assinatura, shell e confirmação)

Refinamento na mesma branch depois da revisão das capturas das rodadas 1 e 2. Foco:
assinatura, shell e confirmação; os demais critérios foram repetidos nos 7 estados.

### Cabeçalho

| Item | Valor |
|---|---|
| Código medido | `claude/feature-015-identidade-visual` em `ad612a8` + rodada 3 (working tree antes do commit) |
| Navegador e banco | Os mesmos das rodadas 1 e 2 (painel do navegador do app; `trajetoria_015`, dados fictícios). Capturas nítidas com Chromium headless a 2× |
| Direção mergeada | **B** |
| Assinatura | O mesmo ativo da rodada 2 (SHA-256 inalterado); só a altura de exibição muda |
| Estados | G1a a G4f com o `<style>` servido pelo sistema; G1a e G4f recapturados ao vivo (Maria já concluiu uma formação, então G1a mostra a entrada direta) |

### Comparação da assinatura: símbolo de 31 × 36 × 38 px

Medida com a mesma página e o mesmo CSS, trocando só a altura do ativo (54, 63 e 66 px).
"Conjunto" = da borda esquerda da assinatura ao fim do nome do produto; a coluna útil tem
343 px a 375 e 288 px a 320.

| Medida | Símbolo 31 px (54 px) | Símbolo 36 px (63 px) | Símbolo 38 px (66 px) |
|---|---|---|---|
| Símbolo real | 31,0 px | 36,1 px | 37,8 px |
| Largura da assinatura | 134,8 px | 157,3 px | 164,8 px |
| Cabeçalho a 375 / 1280 px, fonte 100% | 59 / 59 px | 68 / 68 px | 71 / 71 px |
| "Trajetória Ifes" a 375 px, 100% | ao lado, 1 linha | ao lado, 1 linha | ao lado, 1 linha |
| Conjunto a 375 px, 100% | 286 px | 309 px | 316 px |
| A 320 px, 100% | ao lado, 1 linha; conjunto 286 px; cabeçalho 59 px | **nome abaixo da assinatura**, com o separador solto à esquerda; cabeçalho 107 px | **nome abaixo**; cabeçalho 110 px |
| A 375 px, 200% | nome abaixo, 1 linha; cabeçalho 136 px | nome abaixo, 1 linha; 145 px | nome abaixo, 1 linha; 148 px |
| A 320 px, 200% | nome abaixo, 2 linhas ("Trajetória" / "Ifes"); 181 px | igual; 190 px | igual; 193 px |
| A 1280 px, 200% | ao lado; 85 px | ao lado; 85 px | ao lado; 85 px |
| Sobreposição | nenhuma | nenhuma | nenhuma |
| Rolagem horizontal | nenhuma | nenhuma | nenhuma |
| Assinatura na 1ª viewport a 375 × 667, 100%, com a faixa | y até 224 px | y até 233 px | y até 236 px |
| Primeira ação de Maria a 375 × 667, sem a faixa | 499 px | 508 px | 511 px |
| Leitura do texto da assinatura a 375 px (2×) | "Espírito Santo" no limite, parece miniatura | legível, sem parecer miniatura | legível; ganho pequeno sobre 36 px |

**Escolha: símbolo de 36 px (63 px de altura) a partir de 22em (352 px); 31 px abaixo
disso.**

- 36 px é o menor tamanho em que o texto da assinatura deixa de parecer miniatura; 38 px
  quase não melhora a leitura e aumenta o cabeçalho em mais 3 px.
- A 320 px, 36 e 38 px empurram o nome para baixo da assinatura, com o separador solto à
  esquerda: visualmente inadequado, embora caiba. Por isso, abaixo de 352 px a assinatura
  continua com 54 px (símbolo de 31 px, acima do mínimo de 30 px) e o nome fica ao lado.
  Com 63 px, o conjunto precisa de 341 px de largura; 352 px deixa folga para fontes do
  sistema mais largas.
- FR-016 passa de 64 px (hipótese) para **68 px**, o valor medido; o teto experimental de
  72 px não foi usado.
- O SVG e o texto do nome do produto não mudaram.

Capturas: `R3-assinatura-31-36-38-375`, `R3-assinatura-31-36-38-320`,
`R3-assinatura-31-36-38-375-200`.

### Confirmação: separação entre o bloco de sucesso e a ficha

Comparadas 24 px (atual), 32 px e 48 px a 375 px (`R3-G4f-separacao-24-32-48`). Com 24 e
32 px, os fios de sucesso e da marca, alinhados na mesma coluna, ainda parecem uma linha
interrompida; com 48 px leem como dois blocos.

**Escolha: 48 px** (`--espaco-7`, a mesma separação usada entre Perguntas), aplicada só
ao bloco de sucesso quando a ficha vem logo abaixo (`.confirmacao:has(+ .contexto)`). A
ficha, suas cores, o fio e a paleta não mudam. Quando a Versão não tem texto de
encerramento, o agradecimento fica entre os dois blocos e a separação continua de 24 px.
Medido: 48 px a 320–1280 px com fonte a 100% (96 px a 200%, porque o token é em rem).
Teste: `test_confirmacao_separada_da_ficha_sem_mudar_a_ficha`.

### Verde do fio × verde do ativo

Nada alterado. Pergunta registrada em D-03 (c) para a ACS: "O fio de marca do produto deve
usar o HEX #2f9e41 publicado no Manual ou o #37a033 efetivamente presente no arquivo
oficial EPS utilizado para derivar a assinatura SVG?"

### Medidas

7 estados (G1a, G1b, G2, G3p, G3e, G4c, G4f) × 320, 360, 375, 390, 430 e 1280 px × fonte
100% e 200% (84 combinações).

| Critério | Resultado | Medida |
|---|---|---|
| SC-001 — assinatura | **Aprovado** | Símbolo 36,1 px a ≥ 352 px e 31 px a 320 px (≥ 30 px); módulo 7,8 px coberto pelas margens do ativo; a 375 × 667, assinatura até y = 233 px mesmo com a faixa de demonstração |
| SC-002 — cabeçalho ≤ 68 / ≤ 80 px; rodapé ≤ 120 px | **Aprovado** | Cabeçalho **68 px** a 360, 375, 390, 430 e 1280 px; **59 px** a 320 px; rodapé 76 px. A 200% (informativo): 145 px a 360–430 px e 181 px a 320 px, com o nome abaixo da assinatura (como na rodada 2); 85 px a 1280 px |
| Nome do produto | Aprovado | 0 sobreposições em 84 combinações; com fonte a 100%, "Trajetória Ifes" fica ao lado da assinatura, em 1 linha, em todas as larguras |
| SC-003 — contraste | Aprovado | Texto ≥ 6,74:1 e contornos ≥ 6,74:1; 0 abaixo |
| SC-004 — foco | Aprovado | Regras de foco inalteradas; nenhum elemento focável no cabeçalho; teste do foco do resumo verde |
| SC-005 — sem rolagem horizontal | Aprovado | 0 nas 84 combinações |
| SC-006 — primeira ação na 1ª tela (014 SC-010) | Aprovado | A 375 × 667, descontada a faixa: Maria 508 px, Diego 485 px (≤ 667) |
| SC-007 a SC-011 | Aprovados | Inventário do verde idêntico ao da rodada 2 (fio do cabeçalho, contexto e ficha, sucesso) |
| Confirmação (FR-029) | Aprovado | 48 px entre o bloco de sucesso e a ficha; ficha inalterada |
| SC-012 — administração | Aprovado | Impressões de estilos computados contra a base anterior à 015: editor e acompanhamento **idênticos** a 375 e 1280 px; prévia muda só dentro das Perguntas (8 px entre Perguntas mantidos) |
| SC-013 — suíte e fronteiras | Aprovado | `uv run pytest`: **1848 passed**; `ruff check` limpo; `makemigrations --check` sem mudanças; sem JavaScript nem recurso externo; ativo idêntico ao recebido |
| SC-014 — registro completo | Aprovado | Este documento (rodadas 1 a 3) |

**Peso inline:** `jornada.css` ≈ 7,0 KB (era ≈ 6,5 KB; o acréscimo é quase todo de
comentários que registram as decisões desta rodada).

### Observações para a revisão perceptiva

- Com fonte a 200%, o nome do produto passa para baixo da assinatura e o separador
  vertical fica à esquerda dele, sem nada ao lado. Já era assim na rodada 2 e não depende
  do tamanho escolhido; o spec permite o nome abaixo da assinatura nesse caso.
- Com a fonte padrão do navegador aumentada (e não só a da página), a regra de 22em passa
  a valer em larguras maiores; nas larguras menores a assinatura fica em 54 px. Os dois
  tamanhos atendem aos critérios.

### Capturas desta rodada (fora do repositório)

`R3-G1a-B-375-100`, `R3-G1a-B-320-100`, `R3-G1b-B-375-100`, `R3-G4f-B-375-100`,
`R3-G1a-B-375-200-cabecalho`, `R3-G1a-B-1280-100`, `R3-assinatura-31-36-38-375`,
`R3-assinatura-31-36-38-320`, `R3-assinatura-31-36-38-375-200`,
`R3-G4f-separacao-24-32-48`.

### Resultado da rodada 3

- **Critérios objetivos SC-001 a SC-014: aprovados. Gate aprovado. Rodada final da 015.**
- Situação: identidade visual **implementada e tecnicamente validada** para a jornada do
  egresso; a validação institucional para produção continua pendente em DP-801, D-02 e
  D-03. Não é identidade definitiva aprovada institucionalmente.
- Revisão perceptiva: **pendente**.
- D-03 (validação do ativo, uso em publicação/produção e verde do fio) e D-02 (aplicação
  do PDG): **abertas**. Direção B continua o valor provisório.
