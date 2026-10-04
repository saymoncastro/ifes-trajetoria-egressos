# Specification Quality Checklist: Gestão mínima de Campanha

**Purpose**: Validar completude e qualidade da especificação antes do planejamento.

**Created**: 2026-10-03

**Feature**: [spec.md](../spec.md)

**Marker Semantics**: `[x]` significa requisito revisado quanto à qualidade; não significa
implementação, teste executado ou aprovação institucional.

## Content Quality

- [x] Sem desenho de implementação: nomes de operações da 004 aparecem só como evidência
  do que já existe; rotas, módulos e schema ficam para o plan.
- [x] Foco no valor para o operador: criar, corrigir, abrir e encerrar uma rodada com
  impedimentos compreensíveis.
- [x] Texto compreensível para responsáveis pelo produto.
- [x] Todas as seções obrigatórias do template ativo preenchidas.

## Requirement Completeness

- [x] Nenhum marcador [NEEDS CLARIFICATION] permanece; as escolhas reversíveis estão listadas
  em "Decisões do solicitante antes do `/speckit-plan`".
- [x] Requisitos testáveis e inequívocos: 30 FRs (inclui FR-023a) e uma matriz de ações por situação.
- [x] Critérios de sucesso mensuráveis: 8 SCs.
- [x] Critérios de sucesso descrevem resultados observáveis, sem tecnologia.
- [x] Cenários de aceitação definidos nas cinco histórias.
- [x] Bordas incluem período passado, véspera, último dia, sem período, concorrência,
  reenvio, revogação, abrangência restrita e Campanha criada por engano.
- [x] Escopo delimitado: sem Lote, critérios, publicação, agendamento, remoção ou
  reabertura.
- [x] Dependências e suposições identificadas, inclusive a dependência pré-piloto da
  publicação (002/DP-001, DP-002).

## Feature Readiness

- [x] Todos os FRs têm verificação nas histórias, na matriz ou nos SCs.
- [x] Histórias cobrem criação, correção, abertura, encerramento e recusa.
- [x] Resultados permitem demonstrar o ciclo completo sem alterar o domínio.
- [x] Nenhuma solução técnica antecipada além da exigência de regra única para impedimentos.

## Notes

- Base: main `5e50fec` (PR #26, ADR 0004). Lidos: Constituição, 002 (DP-001), 004 e
  ADR 0004 integralmente, 005 (admissão), 009 (ausência de publicação), 010, 011 e 016.
- Governança: interpretação C1 (CPAEG, só na demonstração). DP-402 continua aberta. A 017
  revisa por nota 004 FR-056, 010 FR-033/FR-073 e 011 FR-001/FR-016/FR-100.
