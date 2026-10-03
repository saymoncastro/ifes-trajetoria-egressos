# Contrato: tokens visuais da jornada

Única fonte dos valores visuais da jornada (FR-001). Definidos uma vez, no `:root` de
`trajetoria/interface/templates/interface/estilo.css`, com o contraste em comentário.
Valores "a calibrar" podem variar na implementação dentro do papel e do contraste
indicados (spec, Assumptions).

## Cor

| Token | Valor | Contraste | Papel / uso permitido | Muda entre A e B? |
|---|---|---|---|---|
| `--cor-marca` | `#2f9e41` | 3,45:1 (gráfico) | Fio do cabeçalho; fio do contexto e da ficha. **Nunca** `color` nem `background` | Não |
| `--cor-acao` | **B (mergeado):** `#1351b4` · A: `#195128` | 7,3:1 · 9,3:1 | Ligações, botão principal, contorno/texto do secundário, `accent-color`, marca de selecionado | **Sim** |
| `--cor-acao-forte` | **B (mergeado):** `#0c326f` · A: `#00420c` | 12,3:1 · 11,8:1 | Hover/ativo de botões e ligações | **Sim** |
| `--cor-sucesso` | `#195128` | 9,3:1 | Aviso `salvo`; topo da confirmação | Não |
| `--cor-institucional` | ≈ `#eef7f0` (a calibrar) | texto sobre ele ≥ 15:1 | Fundo do contexto e da ficha da formação | Não |
| `--cor-selecao` | tonal claro, derivado de `--cor-institucional` ou neutro (a calibrar) | — (complementar) | Fundo de linha/célula marcada e hover | Não |
| `--cor-texto` | `#1b1b1b` | 17,2:1 | Corpo | Não |
| `--cor-texto-suave` | `#565c65` | 6,7:1 | Auxiliar, notas, complemento, subtítulo, rodapé | Não |
| `--cor-fundo` | `#ffffff` | — | Página | Não |
| `--cor-borda-forte` | `#565c65` | 6,7:1 | Campos, células da escala, contornos de controle | Não |
| `--cor-borda-suave` | ≈ `#c6cace` (a calibrar) | < 3:1 | **Só divisores decorativos** | Não |
| `--cor-info` | `#1a4480` | 9,6:1 | Pendência; aviso informativo | Não |
| `--cor-erro` | `#b50909` | 7,0:1 | Erro | Não |
| `--cor-foco` / `--cor-foco-halo` | `#1b1b1b` / `#ffdd00` | 12,8:1 | Foco (regra atual, inalterada) | Não |
| `--cor-demonstracao` | `#fff1d2` | — | Só a faixa de demonstração | Não |

**Troca A/B (FR-011, SC-010):** gerar a outra direção = editar **exclusivamente os dois
tokens de ação**, `--cor-acao` e `--cor-acao-forte`; nenhuma abstração adicional para
reduzi-los a um. Os valores hex dessas duas linhas não aparecem em
nenhum outro lugar das folhas, exceto `#195128` como valor próprio de `--cor-sucesso`.

## Tipografia

| Token | Valor |
|---|---|
| `--fonte` | `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` (inalterada) |
| `--fonte-1` … `--fonte-5` | 28 / 22 / 18 / 16 / 15 px (em rem) |
| `--peso-normal` / `--peso-medio` / `--peso-forte` | 400 / 600 / 700 |
| `--entrelinha-titulo` / `--entrelinha-enunciado` / `--entrelinha-corpo` | 1,25 / 1,4 / 1,5 |

## Espaço, forma e layout

| Token | Valor |
|---|---|
| `--espaco-1` … `--espaco-7` | 4 / 8 / 12 / 16 / 24 / 32 / 48 px (em rem) |
| `--raio` | 4 px na rodada 1; 0 ou 4 após o gate (R11) |
| `--borda-fina` / `--borda-controle` / `--borda-acento` | 1 / 2 / 4 px |
| `--coluna` | 40 rem (jornada) |
| `--alvo` | 44 px (px, não rem — 014 R6) |
| Breakpoint | `30em` (480 px), numa única unidade em todas as folhas da jornada |

## Não são tokens

Espessuras do foco (3 px + 6 px; uma regra só), `scroll-margin` do resumo, alturas
mínimas de `textarea` e larguras do editor/acompanhamento (auditoria §25).
