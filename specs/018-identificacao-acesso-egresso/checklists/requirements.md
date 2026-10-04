# Specification Quality Checklist: Identificação e acesso do egresso por dados acadêmicos

**Purpose**: Validar completude e qualidade da especificação antes do planejamento.

**Created**: 2026-10-04

**Feature**: [spec.md](../spec.md)

**Marker Semantics**: `[x]` significa requisito revisado quanto à qualidade. Não significa
implementação, teste executado nem aprovação institucional.

## Content Quality

- [x] Sem desenho de implementação: rotas, módulos, schema, armazenamento dos contadores e
  da sessão ficam para o plan. HMAC e chaves distintas aparecem porque são **decisões
  fechadas do solicitante**, não escolha técnica da spec.
- [x] Foco no valor para o egresso (acesso com baixa fricção) e para a instituição
  (confiabilidade das respostas, privacidade).
- [x] Texto compreensível para responsáveis pelo produto.
- [x] Todas as seções obrigatórias do template ativo preenchidas.

## Requirement Completeness

- [x] Nenhum marcador [NEEDS CLARIFICATION]. As 7 escolhas reversíveis foram decididas no
  clarify de 2026-10-04 (seção Clarifications).
- [x] Requisitos testáveis e inequívocos: 43 FRs e uma matriz de verificação.
- [x] Critérios de sucesso mensuráveis: 8 SCs.
- [x] Critérios de sucesso descrevem resultados observáveis.
- [x] Cenários de aceitação definidos nas cinco histórias.
- [x] Bordas: formatação de CPF, DV inválido, datas impossíveis ou coringa, colisão,
  matrículas múltiplas, recém-formado não importado, abas concorrentes, GET com dados,
  troca de chave, modo desligado e operador no mesmo navegador.
- [x] Escopo delimitado: a 019 recebe só o ponto de saída `NAO_CONFIRMADA`. Nada de
  Gov.br, SSO, OTP, CAPTCHA, declaração ou validação.
- [x] Dependências e suposições identificadas: 019 como pré-requisito do piloto, profiling
  em paralelo e ativação real bloqueada por DP-1801 a DP-1803.

## Feature Readiness

- [x] Todos os FRs têm verificação nas histórias, na matriz ou nos SCs.
- [x] As histórias cobrem confirmação, não confirmação, limitação, sessão e importação.
- [x] Os resultados permitem demonstrar o caminho completo com dados fictícios, sem alterar
  a jornada.
- [x] Nenhuma solução técnica antecipada além das decisões fechadas do solicitante.

## Notes

- Base: `main` `05d5469` (017 mergeada no PR #27; nenhum módulo citado foi alterado por ela).
  Lidos: Constituição; 001, 004–008, 010, 016; ADR 0004; auditoria de 2026-10-03 com o
  adendo de 2026-10-04.
- Notas de revisão a aplicar com a 018: 001 FR-005, FR-006, FR-028, FR-033; 007 FR-002;
  008 FR-004, FR-007, FR-008; 016 FR-021.
- Decisões pendentes novas: DP-1801 a DP-1809. As três primeiras bloqueiam o uso real.
