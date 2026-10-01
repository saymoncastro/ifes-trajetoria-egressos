# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`

**Created**: [DATE]

**Status**: Draft

**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.

  Constituição, Princípio XIII: quando aplicável, cada requisito DEVE indicar sua
  origem com uma das etiquetas:
    [Herdado]     requisito herdado do instrumento/formulário atual
    [PAEG]        requisito decorrente da PAEG (Resolução CS nº 177/2023) — citar o artigo
    [Arquitetura] decisão arquitetural
    [Hipótese]    hipótese de produto (reversível; não é regra institucional)
    [Oportunidade] oportunidade metodológica futura (fora do escopo até aprovação)
  Mudança de significado de pergunta herdada NÃO é permitida sem revisão
  metodológica explícita, aprovada e versionada. Ao herdar comportamento do
  instrumento atual, distinga INTENÇÃO DO INSTRUMENTO de LIMITAÇÃO/ACIDENTE DA
  IMPLEMENTAÇÃO ATUAL; correções do segundo tipo DEVEM ser identificadas
  explicitamente na spec.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

<!--
  Use a Terminologia Fundamental da Constituição (Pessoa, Conclusão Acadêmica,
  Pesquisa, Versão da Pesquisa, Campanha, Participação em Pesquisa, Resposta) sem
  fundir conceitos. Para cada dado relevante, indique a origem:
  institucional | derivado | declarado (Princípio III).
-->

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| [dado] | [origem] | [provider, cálculo ou pergunta] | [como divergência é explicitada, se aplicável] |

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.

  Constituição, Princípio XXIX: suposições sobre REGRAS INSTITUCIONAIS
  (periodicidade, população elegível, múltiplas formações, papéis, aprovação,
  autenticação, retenção, consentimento, LGPD, publicação, compartilhamento,
  integração institucional, fonte acadêmica oficial, responsabilidades do Portal
  do Egresso etc.) NÃO podem ser registradas aqui como padrão razoável. Elas vão
  para "Decisões Pendentes".
-->

- [Assumption about target users, e.g., "Users have stable internet connectivity"]
- [Assumption about scope boundaries, e.g., "Mobile support is out of scope for v1"]
- [Assumption about data/environment, e.g., "Existing authentication system will be reused"]
- [Dependency on existing system/service, e.g., "Requires access to the existing user profile API"]

## Invariantes Constitucionais Afetados *(mandatory)*

<!--
  Liste os princípios da Constituição que esta feature toca e como o
  comportamento especificado os preserva. Ex.: "I — nova participação não
  sobrescreve participação anterior da mesma Conclusão Acadêmica".
  Se nenhum invariante for afetado, declare explicitamente e justifique.
-->

- **[Princípio]**: [como a feature preserva o invariante]

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

<!--
  Princípio VI: responda às cinco perguntas antes de incorporar funcionalidade
  fora do acompanhamento longitudinal.
-->

1. Pertence de fato ao domínio de acompanhamento? [resposta]
2. É necessária ao ciclo de acompanhamento? [resposta]
3. Existe ou está prevista solução institucional mais adequada? [resposta]
4. Integração seria suficiente? [resposta]
5. A incorporação aumentaria desnecessariamente o acoplamento do núcleo? [resposta]

## Out of Scope *(mandatory)*

- [O que esta feature explicitamente NÃO faz]

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

<!--
  Princípio XXIX: registre aqui toda regra institucional ainda não definida.
  Diferença em relação a [NEEDS CLARIFICATION]:
  - [NEEDS CLARIFICATION] = dúvida de especificação que o solicitante pode
    responder durante /speckit-clarify.
  - DECISÃO PENDENTE = regra que depende de instância institucional competente.
    NÃO conta no limite de marcadores [NEEDS CLARIFICATION], NÃO pode ser
    substituída por "informed guess" ou padrão de mercado e só é removida quando
    houver decisão institucional registrada.
-->

- **DP-001** — DECISÃO PENDENTE: [assunto]. Instância competente: [se conhecida ou "a
  identificar"]. Impacto na feature: [impacto]. Tratamento provisório: [hipótese
  reversível, ou "bloqueia o requisito FR-XXX"].
