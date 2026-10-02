# Specification Quality Checklist: Editor institucional de Pesquisa e Versão

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-01
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- **Iterações**: a validação levou 2 iterações.
  - Na primeira foram corrigidas uma referência cruzada (decisão 7: remoção de Pergunta
    → FR-037) e um nome de exceção de código citado nos Edge Cases, trocado por
    descrição em linguagem de domínio.
  - FR-001 a FR-112 estão em numeração contínua, sem referência a FR inexistente.
- **Detalhes técnicos mencionados de propósito**:
  - A spec cita "páginas geradas no servidor", "sem JavaScript obrigatório", "sem
    SPA/REST/GraphQL/build de frontend", "sem biblioteca de terceiros para ordenação" e
    "proteção contra requisição forjada".
  - São **restrições explícitas do solicitante**, da Constituição (XXII, XXIV) e da 008,
    não escolhas de implementação.
- **Contratos citados**:
  - A seção "Relação com as operações da Feature 002" cita capacidades existentes da 002
    e da 006 só como referência aos contratos, porque o solicitante pediu explicitamente
    essa relação.
  - Assinaturas, composição e a forma de tornar consultável a verificação de suporte da
    006 ficam para o plan.
- **Sem marcadores [NEEDS CLARIFICATION]**.
  - Escolhas reversíveis estão marcadas **[Hipótese]**:
    - posição "ao final";
    - mover para cima/baixo;
    - confirmação de remoção;
    - aviso de nome repetido de Pesquisa;
    - mover Pergunta entre Seções;
    - campo vazio = ausente;
    - recomendação genérica de trabalhar em cópia.
  - Regras institucionais estão em "Decisões Pendentes":
    - novas: DP-901 (competência de elaboração), DP-902 (estatuto da baseline em
      RASCUNHO) e DP-903 (autoria e histórico de rascunhos);
    - herdadas: 002/DP-001 a DP-007, 003/DP-307, 006/DP-604 e demais.
- **Tensões registradas, sem conflito**:
  - X × editor sem autorização: tratada por modo não produtivo, aviso permanente e
    ausência de publicação.
  - XXII × reutilização da verificação da 006: evita segundo validador.
- **Zero entidades novas e zero migrações esperadas** (ver "Análise de persistência").
- **Consolidação pré-plan (2026-10-01, seção Clarifications)**: quatro decisões do
  solicitante incorporadas.
  - (1) A baseline é um RASCUNHO normal, sem proteção por nome; DP-902 aberta; testes não
    a editam; a recusa da 003 é esperada.
  - (2) Mover Pergunta entre Seções confirmado, de forma simples.
  - (3) Renomear Pesquisa não é oferecido.
  - (4) "Prontidão" foi substituída por dois diagnósticos derivados: A — estrutura
    válida (002) e B — compatível com a jornada atual (006). Há três situações, e o
    resultado favorável é "sem impedimentos técnicos conhecidos", nunca "pronta para
    publicação" nem aprovação.
  - Revalidado: FR-001 a FR-112 contínuos, todos os itens continuam aprovados.
- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`
