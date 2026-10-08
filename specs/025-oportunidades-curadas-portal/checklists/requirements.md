# Specification Quality Checklist: Oportunidades curadas do Portal do Egresso

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-08
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

Validação em uma iteração (2026-10-08). **Só especificação**: a implementação aguarda a leitura
do Checkpoint 1 da 024.

- **Detalhes de implementação.**
  - A spec cita arquivos e telas existentes na "Verificação no código". Segue a prática das
    specs 021–024: são evidência do estado atual, não escolhas de implementação.
  - `https://`, `h1` e 44×44 px são requisitos observáveis de segurança e acessibilidade, como
    na 024.
  - Ficam para o plan:
    - os endereços das telas;
    - a organização interna do módulo;
    - onde fica a regra de curadoria;
    - os textos finais;
    - o domínio reservado do catálogo fictício.
- **Modularização.** A spec decide só o que decorre das responsabilidades: Oportunidade vive na
  camada de relacionamento, sem app novo (alternativa A). O resto fica para o plan.
- **Clarificações.** Nenhum marcador. As escolhas abertas são institucionais e estão em
  "Decisões Pendentes" (DP-2501 a DP-2506), nunca como suposição. As escolhas de produto estão
  marcadas como [Hipótese]:
  - as categorias;
  - a ordem;
  - os limites de tamanho;
  - o item de navegação estável;
  - as datas ocultas ao egresso.
- **Critérios de sucesso.**
  - SC-001 a SC-010 são verificáveis por teste ou medição. O SC-002 exige o oráculo por persona
    escrito antes da implementação.
  - SC-011 a SC-016 são a parte de Oportunidades do Checkpoint 2, definida antes do teste.
  - Clique, engajamento e conversão ficam explicitamente fora.
- **Rastreabilidade.** "Requisitos revisados" registra o antes e o depois dos requisitos da 024:
  FR-016, FR-021, FR-022, FR-023, FR-029 e o contrato do Início. Também lista o que **não** é
  revisado.
- **Numeração.** Os FR, SC e cenários começam em 001 nesta spec, como em todas as anteriores. As
  decisões pendentes novas usam o prefixo global da feature: DP-2501 a DP-2506.
- **Revisão 2 (2026-10-08), pedida pelo solicitante.** Todos os itens continuam passando.
  1. **Cursos.** Não há identificador estável de curso no contrato da fonte nem na
     Conclusão. A comparação continua exata, sem correspondência aproximada e sem catálogo.
     As grafias aparecem ao operador, e o código de curso fica como DP-2507. A regra agora
     diz explicitamente que uma **mesma** Conclusão satisfaz todos os critérios (FR-012),
     com cenário e teste.
  2. **Governança.** Administração e público são independentes (FR-026). A unidade
     administra só o que é dela, e o público é livre, como hipótese. O público não dá
     acesso a dado de egresso. DP-2502 foi reescrita.
  3. **Estados.** Tabela com os dois momentos gravados e seis regras:
     - a data nunca autoriza sozinha;
     - publicar autoriza;
     - início e fim são inclusivos;
     - a retirada prevalece e é definitiva;
     - encerrar antes do fim é retirar;
     - os momentos são coerentes.
  4. **Links.** Validação mínima da forma (sem usuário, sem IP, `https`, sem espaços,
     tamanho), classificação site do Ifes × externo só para exibição e parceiros como site
     externo (DP-2504).
  5. **Início.** As alternativas foram confrontadas com as capturas da 024 e com a
     reauditoria de esforço. O bloco passou de até três itens para **um** destaque.
     Ficaram como critério medível:
     - o convite desce no máximo 270 px;
     - o item "Pesquisa" fica em toda página;
     - a navegação de cinco itens quebra sem rolagem a 320 px com fonte a 200%;
     - o caminho do convite tem as mesmas telas, toques e rolagem (SC-008, SC-010).
  - **Coerência.** Conferida contra a Constituição 2.1.0 (X, XII, XVI, XXIX e "Camada de
    relacionamento"), o ADR 0008 (regras 1 a 4) e a 024 (FR-020 preservado; FR-016, FR-021,
    FR-022, FR-023 e FR-029 revisados com rastreabilidade).
- **Atributos do modelo.** Cada atributo hipotético do pedido foi confrontado com um fluxo
  (tabela "Modelo mínimo"):
  - entraram oito;
  - modalidade, forma de oferta e ano no público ficaram fora;
  - prazos, vagas e datas de evento ficaram fora;
  - autoria do cadastro e histórico ficaram fora;
  - imagem e métricas ficaram fora.
