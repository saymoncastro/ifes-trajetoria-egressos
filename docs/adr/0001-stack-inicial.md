# ADR 0001 — Stack inicial do Trajetória Ifes

- **Status**: Aceito. Proposto no `/speckit-plan` da Feature 001 e confirmado
  explicitamente pelo solicitante em 2026-09-30.
- **Data**: 2026-09-30
- **Contexto de origem**: [plan da Feature 001](../../specs/001-nucleo-academico-fonte-simulada/plan.md),
  [research R1, R2, R16](../../specs/001-nucleo-academico-fonte-simulada/research.md)

## Contexto

A Constituição não fixa stack (Princípio XXIV). A escolha deve privilegiar simplicidade,
manutenibilidade, segurança, capacidade da equipe, ambiente institucional, operação,
integração, testabilidade e longevidade, com preferência por aplicação modular simples.
A Feature 001 é a primeira do sistema. As seguintes serão aplicações web com
persistência relacional: jornada do egresso, gestão de pesquisas e campanhas, exportação
CSV.

## Decisão

- Python 3.13, Django 5.2 LTS e PostgreSQL 16+, num único projeto monolítico e modular.
- Ferramentas: uv, ruff, pytest e pytest-django.
- Microserviços, filas, cache e frameworks adicionais só entram com caso concreto e
  justificativa em Complexity Tracking.

A stack foi inicialmente inferida da prática da equipe e depois confirmada
explicitamente. Não é mais hipótese.

## Consequências

- Esta é a mesma base usada em outros sistemas desenvolvidos no Ifes pela equipe, o que
  reduz curva de aprendizado e custo operacional.
- Restrições de integridade e unicidade ficam no banco, o que sustenta as invariantes de
  identidade do domínio.
- Migração para o próximo Django LTS antes de abril de 2028.
- Revisar este ADR se a equipe responsável pela operação institucional adotar outra
  plataforma.
