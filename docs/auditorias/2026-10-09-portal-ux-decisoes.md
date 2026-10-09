# Portal do Egresso — registro das decisões de direção visual

Registro de trabalho das decisões do §15 da
[auditoria de experiência e direção visual](2026-10-08-portal-ux-direcao-visual.md).
Ao fim das nove decisões, este registro será consolidado numa única ADR (prevista como
0009, "camada visual do Portal"). Até lá, nenhuma decisão aqui altera spec, código ou o
instrumento.

| # | Decisão (§15) | Situação | Data |
|---|---|---|---|
| 1 | Layout e tokens próprios do Portal (R1, R2, R3) | **Aprovada** | 2026-10-09 |
| 2 | Leitura da Constituição XXI para o Portal (R4) | Em discussão | — |
| 3 | D-02: cor de ação | Pendente | — |
| 4 | Fonte (R5) | Pendente | — |
| 5 | Fotografia institucional (R7) | Pendente | — |
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
