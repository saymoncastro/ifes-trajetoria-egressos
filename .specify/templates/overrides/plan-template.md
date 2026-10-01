# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.

  Constituição, Princípio XXIV: a stack NÃO é fixada pela Constituição. Toda
  escolha tecnológica feita aqui DEVE ser justificada (simplicidade,
  manutenibilidade, segurança, capacidade da equipe, ambiente institucional,
  operação, integração, testabilidade, longevidade) e, quando estrutural,
  registrada em ADR. Preferir aplicação modular simples; não adotar
  microserviços por padrão.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

<!--
  ACTION REQUIRED: Preencha a tabela a partir de `.specify/memory/constitution.md`
  (seção "Constitution Check Obrigatório"). Regras:
  - Nenhuma linha pode ser removida; itens não pertinentes recebem "N/A" com motivo.
  - Status permitidos: ✅ Conforme | N/A | ⚠ Violação | ⏸ DECISÃO PENDENTE.
  - "Evidência" aponta para a seção da spec/plan/design que demonstra a conformidade.
  - Violação de princípio NON-NEGOTIABLE (I, II, III, V, VII, VIII, IX, X, XVI, XXIX)
    BLOQUEIA o plan: corrigir a feature/escopo ou propor emenda constitucional.
  - Violação de princípio não NON-NEGOTIABLE só avança se justificada em
    "Complexity Tracking" e aceita em revisão.
-->

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | [status] | [status] | [ref] |
| 2 | Pessoa versus Conclusão Acadêmica (campus/curso no contexto da conclusão) | I, XI | [status] | [status] | [ref] |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | [status] | [status] | [ref] |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | [status] | [status] | [ref] |
| 5 | Definição institucional de egresso respeitada | II | [status] | [status] | [ref] |
| 6 | Preservação histórica | VIII, XXVII | [status] | [status] | [ref] |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | [status] | [status] | [ref] |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | [status] | [status] | [ref] |
| 9 | Separação entre dado institucional, derivado e declarado; divergências explícitas | III | [status] | [status] | [ref] |
| 10 | Desacoplamento de integrações (providers/adaptadores, mock com mesmo contrato) | V, XV, XXV | [status] | [status] | [ref] |
| 11 | Fronteira do NIAE (5 perguntas do Princípio VI, se aplicável) | VI | [status] | [status] | [ref] |
| 12 | Governança institucional (periodicidade, publicação, competências normativas) | IX, X | [status] | [status] | [ref] |
| 13 | Escopo por unidade e visão institucional consolidada | XII | [status] | [status] | [ref] |
| 14 | Privacidade, minimização e dados pessoais em logs/exportações | XVI, XVII | [status] | [status] | [ref] |
| 15 | Autorização (menor privilégio; competência técnica ≠ normativa) | X, XII | [status] | [status] | [ref] |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG, quando houver interface) | XX | [status] | [status] | [ref] |
| 17 | Responsividade e jornada móvel | XIV, XXI | [status] | [status] | [ref] |
| 18 | Testes proporcionais ao risco cobrindo invariantes afetados | XXV, XXVI | [status] | [status] | [ref] |
| 19 | Risco de over engineering (YAGNI; sem form builder universal) | XXII, XXIII, XXIV | [status] | [status] | [ref] |
| 20 | Exportabilidade e semântica das exportações (se aplicável) | XVIII | [status] | [status] | [ref] |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | [status] | [status] | [ref] |

**Resultado do gate**: [APROVADO | BLOQUEADO — motivo]

**Conflitos identificados** (ordem obrigatória de análise: 1. a feature está incorreta?
2. o escopo está excessivo? 3. existe alternativa compatível? 4. a Constituição precisa
evoluir? — somente no item 4 cabe emenda):

- [Nenhum | descrever conflito, análise pelos quatro passos e encaminhamento]

## Decisões Pendentes

<!--
  Liste toda regra institucional ainda não definida que afeta este plan
  (Princípio XXIX). Para cada uma, descreva a solução provisória adotada, que
  DEVE ser reversível, localizada, desacoplada e identificada como hipótese.
  Remova esta seção somente se não houver nenhuma.
-->

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-001 | [assunto] | [ex.: Proex, CPAEG, CSAEG ou "a identificar"] | [hipótese reversível] | [estratégia] |

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**
>
> Apenas princípios **não** marcados como NON-NEGOTIABLE admitem justificativa aqui.
> Violação de princípio NON-NEGOTIABLE não é justificável neste plan: exige correção
> da feature ou emenda constitucional.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
