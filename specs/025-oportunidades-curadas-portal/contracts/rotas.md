# Contrato: rotas e pontos de extensão (025)

## Rotas novas (Portal ligado e modo de demonstração)

| Rota | Quem | Contrato |
|---|---|---|
| `/oportunidades/` | Egresso | [oportunidades-egresso.md](oportunidades-egresso.md) |
| `/curadoria/oportunidades/…` | Operador | [curadoria.md](curadoria.md) |

As rotas entram em `trajetoria/portal/urls.py`, que só é incluído com o Portal ligado
(`config/rotas.py`). Com o Portal desligado, respondem 404 (FR-039).

## Rotas existentes alteradas

| Rota | Mudança |
|---|---|
| `/inicio/` | Bloco de Oportunidades (FR-021) |
| Telas com navegação (024 FR-022) | Quinto item na navegação (FR-020) |
| `/demonstracao/operador/` e `…/escolher/` | Aceitam o destino `curadoria` quando o Portal o registrou (R3) |

Nenhuma outra rota muda. `/acesso/`, `/formacoes/`, as Seções, a Campanha, o snapshot e a
exportação ficam como estão.

## Pontos de extensão neutros no núcleo

Nenhum deles cita o Portal (teste `test_nucleo_nao_menciona_o_portal`).

| Ponto | Onde | Uso pelo Portal |
|---|---|---|
| `registrar_destino(chave, endereco, ativo)` | `trajetoria/demonstracao/views.py` | `"curadoria"` → `/curadoria/oportunidades/`, ativo só com o Portal ligado, verificado a cada pedido (R3) |
| Sinal `cenario_preparado` | `trajetoria/demonstracao/sinais.py`, enviado no fim de `cenario.preparar()` | Carrega o catálogo fictício (R4) |
| `data-rotulo` no include de navegação | `trajetoria/interface/templates/interface/_navegacao.html` | Largura estável dos itens (R10) |
| Slots `produto`, `acao_sair`, `retorno` | `interface/base.html` e templates (024, revisão de 2026-10-08) | Já existentes; `/oportunidades/` entra na lista fechada |

## Fronteiras verificadas por teste

1. Nenhum módulo do núcleo importa, lê ou cita a camada (FR-036).
2. `analitico` e `exportacao` não importam o `portal`. Snapshot e exportações são idênticos
   com e sem oportunidades (FR-038; SC-009).
3. As telas do egresso não gravam nada (FR-015, FR-037). As contagens de todas as tabelas,
   inclusive `portal_oportunidade`, ficam iguais.
4. A camada não escreve em tabelas do núcleo (FR-037).
5. O `portal` tem um único modelo, migrações só aditivas e nenhuma chave estrangeira para o
   núcleo (R1).
