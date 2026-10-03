# Registro de validação — Feature 015 (gate)

Formato: [contracts/registro-validacao.md](contracts/registro-validacao.md). **Só texto.**
As capturas **não são versionadas**: ficam fora do repositório e serão anexadas ao PR pelos
identificadores abaixo (`R{rodada}-G{situação}-{A|B}-{largura}-{fonte}`).

> **Estado (2026-10-03): Feature 015 INCOMPLETA — NÃO pronta para merge.**
>
> - **44/46 tasks concluídas.**
> - **T015 BLOQUEADA por D-03** (assinatura oficial: o ZIP oficial do Ifes não contém SVG;
>   nenhum substituto, PNG ou EPS convertido é usado).
> - **T041 BLOQUEADA por D-03** (rodada final do gate depende da assinatura).
> - **Gate final NÃO aprovado.** SC-001 é impossível e SC-002 só parcialmente medível sem o
>   ativo oficial.
> - As capturas e medições atuais foram feitas **sem a assinatura oficial** e validam
>   **apenas** os aspectos que não dependem dela ([validacao.md](validacao.md)).
> - Ao receber o SVG: retomar nesta branch → T015 → T041 (remedir SC-001 e SC-002 com o
>   ativo real) → suíte completa e regressões → atualizar `validacao.md` → só então o PR.

**Situação do gate: NÃO APROVADO — bloqueado por D-03.** Todos os critérios objetivos
mensuráveis sem a assinatura passaram na rodada 1 (após uma correção na própria branch);
SC-001 e a parte de SC-002 que depende da assinatura são **impossíveis** sem o SVG oficial
(research R3). A 015 não está pronta para merge.

---

## Rodada 1 — 2026-10-03

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
