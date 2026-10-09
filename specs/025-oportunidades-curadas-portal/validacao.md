# Validação — Feature 025

> **Checkpoint 1 da 024: NÃO APLICADO.** A implementação foi autorizada só na demonstração
> (roadmap, Revisão 5). Este documento registra verificações técnicas, não resultados com
> egressos.

## Linha de base (T002, 2026-10-08)

**Ambiente**
- base: `claude/025-plan` (inclui a 024 com os ajustes do PR #47);
- banco exclusivo `trajetoria_025`, recém-preparado;
- servidor em `127.0.0.1:8025`, porque a porta 8000 estava ocupada por outro projeto do
  solicitante;
- navegador do app a 375×812, fonte a 100%.

**Verificações:**

| Verificação | Resultado |
|---|---|
| `ruff check .` | sem erros |
| `manage.py check` | sem problemas |
| `makemigrations --check --dry-run` | "No changes detected" |
| `pytest` | **3028 passaram**, 3 pulados (5min25s) |

**Registro da 024** (navegação de quatro itens, sem bloco de Oportunidades). Documenta o
estado anterior e **não** é a referência do SC-008, que é medida na T046.

| Persona | `h1` | Síntese | Convite (`section.inicio-convite`) |
|---|---|---|---|
| Ana | 517 px | 564 px | 1.303 px |
| Maria | 517 px | 564 px | 1.434 px |
| Diego | 517 px | 564 px | 1.512 px |

| Tela (Ana) | Altura de `nav.navegacao` |
|---|---|
| `/inicio/` | 45 px |
| `/formacoes/` | 45 px |
| `/minha-trajetoria/` | **89 px** (o item atual em negrito quebra a linha; A5) |
| `/meu-email/` | 45 px |

A confirmação de Participação não foi medida: ela exige uma Participação concluída, e
nenhuma persona a tem num banco recém-preparado.

## Verificações do CI (T045)

| Verificação | Linha de base (T002) | Depois da 025 |
|---|---|---|
| `ruff check .` | sem erros | sem erros |
| `manage.py check` | sem problemas | sem problemas |
| `makemigrations --check --dry-run` | "No changes detected" | "No changes detected" (com `portal/0001_oportunidade`) |
| `pytest` | 3028 passaram, 3 pulados (5min25s) | **3268 passaram**, 3 pulados (5min32s) |

## P-270: destaque do Início (T046)

O deslocamento foi medido com o bloco escondido no próprio navegador, para que a referência
seja o mesmo Início com a navegação de cinco itens (research R9, "Interpretação do SC-008").
375×812, fonte a 100%.

| Variante | Diego (o destaque mais longo, O6) |
|---|---|
| Padrão (0) | 290 px — **passa de 270** |
| 1 (margens) | 290 px |
| 2 (+ tipo de 15 px) | 281 px |
| **3 (+ um parágrafo só)** | **253 px** |

**Adotada: variante 3** (`COMPACTACAO_DO_DESTAQUE = 3` em `trajetoria/portal/inicio.py`).
Medida com o template real:

| Persona | Convite sem o bloco | Convite com o bloco | Deslocamento |
|---|---|---|---|
| Ana | 1.347 px | 1.600 px | **253 px** |
| Maria | 1.478 px | 1.731 px | **253 px** |
| Diego | 1.556 px | 1.809 px | **253 px** |

A variante 3 mantém título, explicação completa, unidade responsável, origem do site e
domínio (teste `test_toda_variante_mantem_a_informacao_exigida`). Nada foi removido.
Capturas: [01](evidencias/01-inicio-topo-navegacao-5-itens-diego-375.jpg) e
[02](evidencias/02-inicio-destaque-diego-375.jpg).

## Navegação com cinco itens (T047; A5)

| Medida | Resultado |
|---|---|
| Altura de `nav.navegacao` a 375 px, fonte a 100% (Início, Minha trajetória, Oportunidades, Pesquisa e Meu e-mail; Maria) | **89 px em todas**, com os cinco itens nas mesmas posições. Antes, Minha trajetória quebrava diferente (A5) |
| Confirmação de Participação | Não medida no navegador (exige Participação concluída). O mesmo provedor e o mesmo include; coberta por `test_confirmacao_marca_a_pesquisa` |
| Alvos | 44 px de altura, largura de 44 a 116 px a 375 px; ≥ 44×44 a 320 px com fonte a 200% |
| `h1` e síntese do Início a 375×812 | 561 px e 608 px: acima da dobra (024 SC-004) |
| Rolagem horizontal a 320 px, fonte de 100% e 200% | Nenhuma em `/inicio/`, `/oportunidades/`, curadoria (lista, nova, publicar, retirar) |
| Rolagem horizontal a 1280 px, fonte de 100% e 200% | Nenhuma em `/inicio/` e `/oportunidades/` |

**Ajustes feitos durante a medida:**
- **Página e Início a 320 px com fonte a 200%.** O domínio `oportunidades.example` não
  quebrava e alargava a página em 14 px. Os textos da oportunidade ganharam
  `overflow-wrap: anywhere`, como na 021.
- **Lista da curadoria.** Os `span.visualmente-oculto` dentro da tabela com rolagem
  alargavam a página. Foram trocados por `aria-label` no link, com o mesmo nome acessível
  ("Retirar: título").
- **Títulos da curadoria a 200%.** "Nova oportunidade" estourava. As telas da curadoria
  ganharam uma folha própria que quebra títulos e textos. A tabela continua rolando dentro
  da região, como na 011.
- **Fora do escopo.** As telas de operação do núcleo (011 e 017) também vazam com fonte a
  200%: `/acompanhamento/` chega a 507 px a 320 px. É anterior à 025 e não foi alterado.

## Quickstart (T048)

Banco recém-preparado, catálogo carregado pelo sinal, servidor em `127.0.0.1:8025`.

| Passo | Resultado |
|---|---|
| Ana, Maria e Diego no Início | Destaques O2, O2 e O6; "Ver as 2 / 3 / 3 oportunidades" |
| Página de Maria | O2 e O3 em "Pela sua formação", O1 em "Para todos"; **O5 ausente** ([03](evidencias/03-pagina-maria-sem-o5-375.jpg)) |
| Curadoria sem operador | Leva à escolha com destino `curadoria`; depois da escolha, volta à curadoria |
| Operador B | Lista com O3, O4, O9 e O10 (Vitória) ([04](evidencias/04-curadoria-lista-operador-b-375.jpg)) |
| Confirmação de publicação | Prévia, público, período, domínio em destaque e aviso de site externo ([05](evidencias/05-curadoria-confirmar-publicacao-site-externo-375.jpg)) |
| Operador A retira O1 pela interface | Aviso "Oportunidade retirada da divulgação." |
| Fernanda depois da retirada | Início sem bloco; página com o estado vazio e "Voltar ao Início"; item na navegação ([06](evidencias/06-estado-vazio-fernanda-375.jpg)) |

## Teclado e acessibilidade (T049)

- **Ordem de foco em `/oportunidades/`.** Pular → Sair → Início → Minha trajetória →
  Oportunidades (atual, `aria-current="page"`). Contorno sólido de 3 px.
- **Árvore de acessibilidade.**
  - `navigation` "Portal do Egresso" com cinco links. O nome de cada item não é duplicado
    pelo `::after` (`visibility: hidden`).
  - `main` com um único `h1`.
  - O link de cada oportunidade tem como nome o título e "— site externo: {domínio}".
- **Ações da lista da curadoria.** O nome acessível inclui o título ("Retirar: Curso de
  extensão a distância em Ciência de Dados").
- **Formulário da curadoria.** `fieldset` e `legend` na categoria e nos três grupos do
  público; erros com `aria-describedby` e `aria-invalid`; foco no primeiro erro (testes).
- **Leitor de tela.** **Não executado** (P4 da 024 continua pendente).
