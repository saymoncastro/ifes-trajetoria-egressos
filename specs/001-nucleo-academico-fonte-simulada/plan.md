# Implementation Plan: Núcleo acadêmico longitudinal e fonte institucional simulada

**Branch**: `claude/feature-001-nucleo-academico-fc2889` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-nucleo-academico-fonte-simulada/spec.md`

## Summary

A 001 entrega a base **Pessoa → Conclusão Acadêmica → fronteira substituível → fonte
simulada determinística**, e nada além disso. Os quatro elementos técnicos são:

- **Projeto Django único** (Python 3.13, Django 5.2 LTS, PostgreSQL), com um app de
  núcleo acadêmico que tem **dois modelos**: `Pessoa` e `ConclusaoAcademica`.
- **Fronteira de dados acadêmicos**: um `Protocol` em Python puro com **duas
  operações** (obter pessoa, obter conclusão). Os resultados são tipados, e a falha da
  fonte é uma exceção.
- **Fonte simulada**: implementa esse contrato sobre registros fictícios declarados em
  código, e é quem decide o que é conclusão reconhecida.
- **Função `incorporar_pessoa(fonte, id)`**:
  - é idempotente por restrições de unicidade em (fonte, id externo);
  - não persiste pessoa sem conclusão elegível;
  - sinaliza divergências no resultado, sem alterar ou remover nada.

A substituibilidade é provada por uma suíte de contrato executada contra a fonte
simulada e contra uma segunda implementação que existe só nos testes. Decisões e
alternativas estão em [research.md](research.md).

## Technical Context

> **Stack confirmada** pelo solicitante em 2026-09-30, após este plan. Python 3.13,
> Django 5.2 LTS, PostgreSQL 16+, uv, pytest e ruff são decisão aceita, registrada em
> [ADR 0001](../../docs/adr/0001-stack-inicial.md), e não apenas inferida.

- **Language/Version**: Python 3.13.
- **Primary Dependencies**: Django 5.2 LTS e psycopg 3. Não há outras dependências de
  execução (R1, R16).
- **Storage**: PostgreSQL 16+, acessado pelo ORM do Django. Idempotência e integridade
  ficam em restrições do banco (R2).
- **Testing**: pytest, pytest-django e ruff. Os testes rodam em PostgreSQL, sem rede e
  sem sistema acadêmico.
- **Target Platform**: servidor Linux, para operação futura. Nesta feature há só
  execução local e CI.
- **Project Type**: aplicação web monolítica (Django), por ora sem camada web, sem
  interface e sem API.
- **Performance Goals**: N/A. Não há metas de desempenho nesta feature (spec,
  Assumptions).
- **Constraints**:
  - sem acesso a sistemas externos;
  - dados exclusivamente fictícios;
  - logs sem dados pessoais (nomes nunca são registrados).
- **Scale/Scope**: cerca de 11 pessoas e 19 registros simulados, 2 modelos, 2 operações
  de fronteira e 1 função de serviço.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ | ✅ | Conclusão com UUID estável e FK `PROTECT`; nenhum placeholder de etapas posteriores ([data-model](data-model.md), R5) |
| 2 | Pessoa versus Conclusão Acadêmica (campus/curso no contexto da conclusão) | I, XI | ✅ | ✅ | Pessoa sem nenhum campo acadêmico ([data-model](data-model.md#pessoa)) |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | ✅ | ✅ | Unicidade só por (fonte, id externo); nenhuma restrição por atributos (FR-014) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | N/A | N/A | Participação fora do escopo; a identidade estável da Conclusão não impede N participações futuras |
| 5 | Definição institucional de egresso respeitada | II | ✅ | ✅ | Reconhecimento decidido pela fonte; o contrato só transporta conclusões reconhecidas; pessoa sem conclusão não é persistida (R4, FR-039) |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | A incorporação nunca atualiza nem remove; `PROTECT`; migração inicial sem dados existentes (R11) |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | N/A | N/A | Nenhum desses conceitos é criado nesta feature |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | ✅ | ✅ | `fonte`, `id_externo`, `incorporado_em`; a fonte simulada é identificada pelo código `simulada`; sem linhagem nem histórico (R6, R7) |
| 9 | Separação entre dado institucional, derivado e declarado; divergências explícitas | III | ✅ | ✅ | Só dado institucional; nenhum derivado ou declarado; divergências no resultado (R11) |
| 10 | Desacoplamento de integrações (providers/adaptadores, mock com mesmo contrato) | V, XV, XXV | ✅ | ✅ | `Protocol` em pacote sem Django; fonte recebida por argumento; suíte de contrato sobre duas implementações (R3, R13) |
| 11 | Fronteira do NIAE (5 perguntas do Princípio VI, se aplicável) | VI | ✅ | ✅ | Respondidas na spec; o NIAE consome dados acadêmicos e não os mantém (sem CRUD) |
| 12 | Governança institucional (periodicidade, publicação, competências normativas) | IX, X | N/A | N/A | Nenhuma periodicidade, publicação ou perfil nesta feature |
| 13 | Escopo por unidade e visão institucional consolidada | XII | ✅ | ✅ | Base única; unidade é atributo da Conclusão, não critério de partição |
| 14 | Privacidade, minimização e dados pessoais em logs/exportações | XVI, XVII | ✅ | ✅ | Dados fictícios; nome opcional; logs só com tipo, fonte, id externo e nomes de campo; dados reais bloqueados por DP-009 |
| 15 | Autorização (menor privilégio; competência técnica ≠ normativa) | X, XII | N/A | N/A | Sem interface, API, admin ou acesso de usuário; nenhum ponto de entrada exposto (R15) |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG, quando houver interface) | XX | N/A | N/A | Sem interface |
| 17 | Responsividade e jornada móvel | XIV, XXI | N/A | N/A | Sem jornada |
| 18 | Testes proporcionais ao risco cobrindo invariantes afetados | XXV, XXVI | ✅ | ✅ | Matriz em [Testes](#estratégia-de-testes); executáveis sem integração real |
| 19 | Risco de over engineering (YAGNI; sem form builder universal) | XXII, XXIII, XXIV | ✅ | ✅ | 2 modelos, 2 operações, 1 função; nada da lista de restrições do solicitante; ver Complexity Tracking |
| 20 | Exportabilidade e semântica das exportações (se aplicável) | XVIII | N/A | N/A | Exportação fora do escopo; campos com semântica documentada facilitam o uso futuro |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ | ✅ | DP-001 a DP-009 preservadas abaixo; vocabulários em texto livre (R10) |

**Resultado do gate**: APROVADO (pré-Fase 0 e pós-Fase 1).

**Conflitos identificados**: nenhum.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-001 | Fonte acadêmica oficial e mecanismo de acesso | A identificar (Proen, Proex, TI) | Só a fonte simulada | Nova implementação do `Protocol`; o núcleo não muda |
| DP-002 | Identificadores reais e sua estabilidade | A identificar | `id_externo` opaco e estável (`SIM-…`) | O adaptador real produz identificador estável; o contrato não muda |
| DP-003 | Reconciliação entre fontes | A identificar | Nenhuma fusão; unicidade por (fonte, id externo) | Migração aditiva para tabela de referências (R6) e spec própria |
| DP-004 | Atributos de Q10–Q19 com qualidade na fonte real | CPAEG, áreas de ensino | Todos os atributos opcionais (`NULL` = não informado) | Tornar obrigatório por migração, quando decidido |
| DP-005 | Divergência ou correção de dado da fonte | A identificar; PAEG Art. 26 | Detecta, devolve no resultado e registra em log; nada é alterado | Substituir só o tratamento em `incorporacao.py` |
| DP-006 | Atualização e sincronização | A identificar | Só a função; sem disparo; `incorporado_em` sem "última obtenção" | Acrescentar disparo e campo por spec própria |
| DP-007 | Vocabulário de nível, modalidade e forma de oferta (inclui "não informado" × "não se aplica") | CPAEG, áreas de ensino | Texto livre, sem lista fechada | Migração para vocabulário controlado |
| DP-008 | Critério de "conclusão" na fonte real | Proen, registro acadêmico, CPAEG | Situação declarada por registro na fonte simulada | Implementado no adaptador real; o núcleo não muda |
| DP-009 | Base legal e retenção de dados pessoais reais | A identificar (encarregado de dados) | Só dados fictícios; nome opcional | Bloqueia o uso de fonte real até a decisão |

## Desenho

### Representação (item 2 do resultado esperado)

São dois modelos Django, `Pessoa` e `ConclusaoAcademica`, descritos em
[data-model.md](data-model.md). Pontos principais:

- **Identidade**: UUID interno.
- **Referência de origem**: em colunas da própria tabela.
- **Ausência de valor**: `NULL` significa "não informado pela fonte", e cadeia vazia é
  proibida.
- **Conclusão**: guarda o ano e, opcionalmente, a data completa.
- **Nome da Pessoa**: opcional, fora de qualquer critério de identidade.

### Fronteira acadêmica (item 3)

[contracts/fonte-academica.md](contracts/fonte-academica.md) define:

- duas operações;
- resultados que distinguem encontrado, inexistente, não reconhecido como conclusão e
  pessoa sem conclusões;
- exceção para falha.

O núcleo importa somente `contrato.py`. A fonte concreta chega como argumento.

### Fonte simulada (item 4)

- `FonteSimulada` mapeia a situação declarada de cada registro para o contrato (R12).
- Os dados ficam em `cenarios.py`, conforme o
  [catálogo de cenários](contracts/cenarios-simulados.md).
- O construtor aceita:
  - `indisponivel=True`, para o Cenário H;
  - um conjunto alternativo de registros, para os testes de divergência.

### Idempotência (item 5)

- `incorporar_pessoa` consulta a fonte **antes** de abrir a transação.
- Dentro da transação, usa "obter ou criar" por (fonte, id externo) para a Pessoa e
  para cada Conclusão.
- A unicidade no banco garante a idempotência também sob concorrência.
- A função não executa atualização nem remoção. Comportamento completo em
  [contracts/incorporacao.md](contracts/incorporacao.md).

### Proveniência mínima (item 6)

Três campos por registro: `fonte`, `id_externo` e `incorporado_em`, este último gravado
só na criação. O código de fonte `simulada` identifica os dados simulados. Não há atributo
de domínio para "mock" (R6, R7).

## Estratégia de testes

Item 7 do resultado esperado. O foco são os invariantes, não um percentual de
cobertura. Cada teste vem da lista do solicitante, com cenário e requisito:

| Teste | Cenário / dado | Requisito |
|-------|----------------|-----------|
| Pessoa com uma conclusão | A | US1, FR-007, FR-009 |
| Pessoa com múltiplas conclusões, uma única Pessoa | B, C, D | US2, FR-004 |
| Contextos acadêmicos distintos, sem mistura | C, D | US3, FR-013 |
| Mesmo nome para pessoas diferentes | Homônimos | FR-005, FR-031 |
| Pessoa sem nome | SIM-P-0009 | FR-005 |
| Repetição da mesma origem sem duplicar a Pessoa | conjunto 3× em ordens diferentes | US5, FR-031, SC-003 |
| Conclusão repetida sem duplicação; UUID estável | E | US5, FR-008 |
| Nova conclusão associada à Pessoa existente | variante só nos testes | FR-032 |
| Registro não concluído não materializado | F2, F3; `obter_conclusao` em SIM-C-09xx | US7, FR-018, FR-019, SC-004 |
| Pessoa localizada sem conclusão elegível não persistida | F1, F3 | FR-039 |
| Pessoa e conclusão inexistentes | G | US8 |
| Falha da fonte ≠ inexistência; nada é escrito; o já incorporado fica intacto | H | FR-025 |
| Proveniência mínima (fonte `simulada`, id externo, momento) | todos | US6, FR-035, SC-005 |
| Divergência sem sobrescrita nem duplicação (quatro tipos) | variantes só nos testes | FR-033 |
| Substituição do provider sem mudar o domínio | suíte de contrato e incorporação com duas implementações | FR-024, SC-006 |
| Atributo ausente ≠ valor; data × ano | A, B, restrições do modelo | FR-010, FR-011 |
| Consumidor de demonstração (experiência esperada) | C | SC-008 |
| Dados fictícios (prefixo `SIM-`, sem padrão de CPF ou e-mail) | conjunto canônico | FR-028, SC-009 |

## Project Structure

### Documentation (this feature)

```text
specs/001-nucleo-academico-fonte-simulada/
├── spec.md
├── plan.md               # este arquivo
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── fonte-academica.md
│   ├── incorporacao.md
│   └── cenarios-simulados.md
├── checklists/requirements.md
└── tasks.md              # gerado por /speckit-tasks (não por este comando)
```

### Source Code (repository root)

```text
pyproject.toml            # dependências, pytest, ruff
uv.lock
manage.py
.env.example              # variáveis PG*, sem segredos
config/
├── settings.py           # um arquivo; lê o ambiente; INSTALLED_APPS só com o núcleo
├── urls.py               # vazio nesta feature
└── wsgi.py
trajetoria/
├── __init__.py
├── academico/            # app Django: o núcleo
│   ├── apps.py
│   ├── models.py         # Pessoa, ConclusaoAcademica
│   ├── incorporacao.py   # incorporar_pessoa, ResultadoIncorporacao, Divergencia
│   └── migrations/0001_initial.py
└── fonte_academica/      # Python puro; não importa Django
    ├── __init__.py
    ├── contrato.py       # Protocol, objetos transportados, exceção
    ├── simulada.py       # FonteSimulada
    └── cenarios.py       # dados fictícios declarados
tests/
├── conftest.py
├── fontes_de_teste.py    # implementação alternativa e variantes de divergência
├── test_contrato_fonte.py
├── test_fonte_simulada.py
├── test_modelo.py
├── test_incorporacao.py
└── test_aceitacao.py
docs/adr/0001-stack-inicial.md   # ADR aceito
```

**Structure Decision**:

- Há um projeto Django na raiz do repositório e um pacote `trajetoria`.
- O núcleo (`academico`) depende só de `fonte_academica.contrato`.
- A fonte simulada fica ao lado do contrato porque é uma implementação real dele, e não
  código de teste.
- Os testes ficam num diretório plano: cinco arquivos não justificam subpastas.
- Não há `frontend/`, `api/` nem `services/` genéricos. As próximas features
  acrescentam apps conforme seus casos concretos.

## Complexity Tracking

Nenhuma violação a justificar.

Itens da lista de restrições do solicitante considerados e **não** adotados:

- microserviços, event sourcing, CQRS, broker, filas, jobs, cache, workflow;
- sincronização genérica, reconciliação de identidade;
- framework, registry ou plugins de providers;
- API pública;
- abstração multifonte além do `Protocol`;
- histórico por atributo, linhagem;
- painel ou administração de divergências;
- CRUD, autenticação, permissões.

Também foram avaliados e rejeitados, por YAGNI:

- repository pattern;
- tabela de referências de origem;
- tabelas de Curso e Unidade;
- comando de gestão;
- segunda fonte em produção.

Ver [research.md](research.md), R3, R6, R10, R13 e R14.

## Para specs futuras (item 8)

- **Reservado a features próprias**: Pesquisa, Versão, Campanha, Participação, Resposta,
  jornada, autenticação, exportação e permissões.
- **Dependem da integração real**: disparo e sincronização da incorporação (DP-006),
  tratamento operacional de divergências (DP-005) e adaptador real (DP-001, DP-002,
  DP-008).
- **Spec de migração do instrumento**: vocabulário canônico (DP-007) e obrigatoriedade
  de atributos (DP-004).
- **Spec própria, se houver necessidade**: materialização de não egressos.
