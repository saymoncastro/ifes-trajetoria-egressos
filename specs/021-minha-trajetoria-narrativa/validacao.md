# Validação — Feature 021

Este arquivo registra as portas de decisão e as verificações manuais. Todos os dados são
fictícios.

## Fase 3 — porta de decisão: PNG e pior caso do card (2026-10-04)

### T007 — Rasterização (ver [ADR 0006](../../docs/adr/0006-rasterizacao-do-card.md))

- **macOS arm64: aprovado.**
  - PNG 1080 × 1920.
  - Bytes idênticos em duas gerações.
  - Acentos com Open Sans.
  - 28–59 ms por card.
- **CI (ubuntu, Python 3.13): pendente.** Exige o push do PR. O `uv.lock` já fixa a *wheel*
  manylinux.

### T012 — Pior caso visual

O pior caso usado:

- nome de 61 caracteres;
- 4 cursos de 51 a 80 caracteres, todos na unidade "Cachoeiro de Itapemirim";
- 3 formações além das 4 (total de 7);
- um par de agregados com o curso mais longo;
- a marca de demonstração.

**Achado.** Com o corpo mínimo do contrato (40 px; título 64 px) e a área segura de 1300
px (y 270–1570), o pior caso **não cabe inteiro**:

- com tudo, ocupa cerca de 1.885 px;
- sem agregados, cerca de 1.470 px.

**Composição adaptativa implementada para avaliação:**

- o card mostra **até 4** formações, **tantas quantas couberem**;
- as demais entram em "e mais N formações registradas", e nenhuma some sem aviso;
- o par de agregados entra só se couber depois das formações;
- nome e cursos nunca são cortados.

| Caso | Formações exibidas | Agregados no card | Evidência |
|---|---|---|---|
| Pior caso (7 formações, nome longo) | 3 + "e mais 4" | Não (não cabem) | [card-pior-caso.png](evidencias/card-pior-caso.png) |
| Maria (2 formações, com nome e agregados) | 2 | Sim | [card-maria.png](evidencias/card-maria.png) |
| Maria sem nome | 2 | Sim | [card-maria-sem-nome.png](evidencias/card-maria-sem-nome.png) |

- Todos os textos estão dentro da área segura e com corpo mínimo (verificado em
  `tests/narrativa/test_card.py`).
- A legibilidade foi conferida pela imagem em tamanho real.

**Decisão do solicitante (2026-10-04):** a composição adaptativa foi aprovada. A spec
(FR-033), o contrato do card e os testes foram atualizados. O CI do PNG roda só no PR
final.

## Fase 7 — página e card no navegador (2026-10-04)

Ambiente: demonstração local (banco `trajetoria_demo_021`, dados fictícios), navegador do
app em 375 × 812. A Participação concluída foi marcada direto no banco de demonstração,
para chegar à página sem responder às 13 Seções. O fluxo completo pela interface está
coberto pelos testes.

| Verificação | Resultado | Evidência |
|---|---|---|
| `/formacoes/` com título "Suas formações no Ifes", ligação "Ver minha trajetória no Ifes" e antecipação | OK | — |
| Página da Maria: duas formações, "Há 1 ano desde essa conclusão." só para a data completa, frase "Depois dessa formação…" | OK | [pagina-375-topo.jpg](evidencias/pagina-375-topo.jpg) |
| Sem rolagem horizontal em 375 px (`scrollWidth` = 375) | OK | — |
| Prévia é a PNG 1080 × 1920 | OK | [pagina-375-card.jpg](evidencias/pagina-375-card.jpg) |
| "Incluir meu nome" + "Atualizar prévia" sem JavaScript (`?nome=1#card`) | OK; nome só com a opção | [pagina-375-card-com-nome.jpg](evidencias/pagina-375-card-com-nome.jpg) |
| "Compartilhar imagem" onde não há `navigator.canShare` | Oculto (esperado) | — |

**Pendente com o solicitante (T031):**

- celular real com Safari no iOS e Chrome no Android;
- tocar e segurar para salvar;
- "Baixar imagem";
- menu de compartilhamento (registrar quais destinos aparecem);
- anexar a PNG a um story de teste e conferir que não há recorte nem texto sob a interface.

**Pendente no CI:** o spike do PNG no ubuntu, no PR final.

## P2 — ingresso e agregados simulados (2026-10-04)

O banco de demonstração foi migrado (`contexto_trajetoria/0001`) e preparado de novo. O
preparo carregou 1 complemento (Ana) e 2 agregados (TADS · Serra · 2022 e Serra · 2022).

| Verificação | Resultado | Evidência |
|---|---|---|
| Ana: "Sua trajetória no Ifes começou em 2019, em Tecnologia em Análise e Desenvolvimento de Sistemas." | OK | [pagina-375-ana-p2.jpg](evidencias/pagina-375-ana-p2.jpg) |
| Ana: seção "Naquele ano no Ifes" com "27 conclusões de …", "812 conclusões …" e a apuração 31/01/2026 | OK | idem |
| Card da Ana: agregados dentro da área segura, sem ingresso | OK | [card-ana-p2.png](evidencias/card-ana-p2.png) |
| Agregado com duas apurações, valor incoerente, outra fonte ou base sem carga | Omitido (testes) | `tests/narrativa/test_agregados.py` |
| Contexto indisponível: preparo, login, resposta e narrativa P1 | OK (testes) | `tests/contexto_trajetoria/test_isolamento.py` |

As evidências da Fase 3 (`card-pior-caso.png`, `card-maria*.png`) foram regeneradas com as
faixas em `--cor-texto`.

## Fase 12 — larguras e acabamento (2026-10-04)

| Verificação | Resultado | Evidência |
|---|---|---|
| 320 px (Ana): sem rolagem horizontal (`scrollWidth` = 320), prévia com 270 px | OK | [pagina-320-ana.jpg](evidencias/pagina-320-ana.jpg) |
| 1280 px: sem rolagem horizontal, prévia com 270 px na coluna | OK | — |
| Sessão expirada (30 min de inatividade) leva a `/acesso/` | OK, observado na própria demonstração | — |
| Sem JavaScript | Coberto por testes: página, prévia, nome e baixar funcionam sem script; "Compartilhar" nasce oculto | `tests/narrativa/test_pagina_card.py` |
| Varredura de termos vedados nos templates e textos novos | OK | `tests/narrativa/test_catalogo.py` |

**Continua pendente com o solicitante:** celular real com Safari no iOS e Chrome no
Android; toque longo; menu de compartilhamento; story de teste no Instagram.

**Continua pendente no CI:** o spike do PNG no ubuntu, no PR.
