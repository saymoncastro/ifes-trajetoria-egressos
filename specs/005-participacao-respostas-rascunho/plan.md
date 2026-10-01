# Implementation Plan: Participação em Campanha e respostas em rascunho

**Branch**: `claude/feature-005-participacao-campanha-f29c06` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-participacao-respostas-rascunho/spec.md`

## Summary

A 005 entrega a camada de persistência e integridade do rascunho:
**Conclusão → Participação → Campanha → Versão** e **Participação → Respostas →
Perguntas/Opções da Versão**. Ela não executa a jornada.

- **Duas entidades de domínio novas** no novo app `trajetoria.participacao` (R1):
  - `Participacao(campanha, conclusao, iniciada_em)`, com `UNIQUE (campanha,
    conclusao)`. Pessoa, Versão e Pesquisa são propriedades derivadas (R3);
  - `Resposta(participacao, pergunta, opcao, texto, escala, complemento)`, com `UNIQUE
    (participacao, pergunta)` e colunas tipadas, uma forma de valor por tipo (R4).
- **Uma tabela técnica**, `RespostaOpcao(resposta, opcao)`, com `UNIQUE (resposta,
  opcao)`, para o conjunto da escolha múltipla, sem identidade de domínio (R5).
- **Complemento de "Outro"** como coluna da Resposta, referida à única Opção da Pergunta
  que o admite (002 FR-042), em escolha única ou múltipla (R6).
- **Operações explícitas por tipo**: `iniciar_participacao`, `responder_escolha_unica`,
  `responder_escolha_multipla`, `responder_texto`, `responder_escala`,
  `remover_resposta`. Sem valor genérico nem CRUD (R7).
- **Gates da 004, sem replicar regra** (R10): criar exige `admite_participacao`;
  escrever exige só `estado(…) is EM_COLETA`; início repetido devolve a existente.
- **Concorrência proporcional** (R11): `UNIQUE` + savepoint para inícios simultâneos;
  `select_for_update(of=("self",))` da Participação para escritas.
- **Atomicidade** por `transaction.atomic()`, com validação antes de gravar (R12).
- **Consultas** sem modelo de tela: `localizar_participacao`,
  `participacoes_da_conclusao`, `admite_escrita`, `respostas_atuais` (R14).

As Features 001 a 004 não mudam em código de produção. Um teste da 004, excessivamente
amplo, teve o escopo corrigido (R16; [Necessidade de voltar](#necessidade-de-voltar-à-spec-ou-às-features-anteriores)).

## Technical Context

- **Language/Version**: Python 3.13 ([ADR 0001](../../docs/adr/0001-stack-inicial.md)).
- **Primary Dependencies**: Django 5.2 LTS e psycopg 3. Nenhuma dependência nova.
- **Storage**: PostgreSQL 16+. Três tabelas novas, com UNIQUEs e CHECKs locais. Regras
  entre linhas (tipo da Pergunta, pertença à Versão e à Pergunta, limites, estado da
  Campanha) ficam nas operações.
- **Testing**: pytest, pytest-django e ruff, em PostgreSQL, sem rede, com `agora`
  explícito. A concorrência é protegida por teste determinístico do ramo `IntegrityError`;
  um teste com threads só permanece se for estável (R17).
- **Target Platform**: servidor Linux, para operação futura; nesta feature, execução
  local e CI.
- **Project Type**: aplicação web monolítica (Django), ainda sem camada web, interface ou
  API.
- **Performance Goals**: N/A. Uma rodada institucional tem dezenas de milhares de
  Participações e algumas dezenas de Respostas por Participação; os índices das FKs e
  das UNIQUEs bastam.
- **Constraints**:
  - nenhuma alteração em modelos, operações, contratos ou dados das Features 001–004;
  - nenhuma interface, URL, admin ou comando expõe as operações (DP-505);
  - nenhum processo agendado; nenhum log com valor declarado;
  - somente dados fictícios (DP-504).
- **Scale/Scope**: 2 modelos de domínio + 1 técnico, 1 migração, 6 operações de escrita,
  4 consultas, 9 motivos de rejeição.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ | ✅ | A cadeia passa a existir: `Participacao.conclusao`, `Resposta.participacao`. `iniciada_em` dá contexto temporal. Várias Participações por Conclusão em Campanhas diferentes; nenhuma operação toca outra Participação ([data-model](data-model.md)) |
| 2 | Pessoa versus Conclusão Acadêmica (campus/curso no contexto da conclusão) | I, XI | ✅ | ✅ | Participação aponta para a Conclusão, não para a Pessoa; contexto acadêmico lido de `participacao.conclusao`, nunca copiado (R3, R14) |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | ✅ | ✅ | Uma Participação por Conclusão; duas Conclusões elegíveis na mesma Campanha → duas Participações independentes (FR-009; DP-501) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | ✅ | ✅ | `UNIQUE (campanha, conclusao)` permite N Campanhas por Conclusão; escritas bloqueiam e alteram só a própria Participação; nada é copiado entre Participações (FR-008) |
| 5 | Definição institucional de egresso respeitada | II | ✅ | ✅ | Admissão pela elegibilidade da 004 sobre Conclusões da 001 (só formações reconhecidas) |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | Validação pela Versão da Campanha, PUBLICADA e imutável; FKs `PROTECT` para Pergunta e Opção; Participação não removível; nada apagado ao encerrar. Edição em rascunho dentro da mesma Participação é o comportamento confirmado (spec, Clarifications). Migração só cria tabelas novas |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ | ✅ | Participação e Resposta são modelos próprios; Versão e Pesquisa derivadas pela Campanha, sem coluna (R3); Pergunta verificada contra `campanha.versao_id` (R9) |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | ✅ | ✅ | "Declarado" decorre da natureza da Resposta; institucional, da Conclusão. Sem autor, canal, IP ou momento por edição (FR-045). Registro por intermediário em DP-506 |
| 9 | Separação entre dado institucional, derivado e declarado; divergências explícitas | III | ✅ | ✅ | Nenhuma Resposta criada a partir da Conclusão; nenhuma escrita na Conclusão; divergência preservada lado a lado, sem tratamento automático (DP-508). Teste da resposta de campus divergente |
| 10 | Desacoplamento de integrações (providers/adaptadores, mock com mesmo contrato) | V, XV, XXV | ✅ | ✅ | Nenhuma integração. Sem autenticação, sessão ou token: as operações recebem Campanha e Conclusão (FR-015). Testes com a fonte simulada |
| 11 | Fronteira do NIAE (5 perguntas do Princípio VI, se aplicável) | VI | ✅ | ✅ | Respondidas na spec: Participação e Respostas estão na Fronteira do Domínio |
| 12 | Governança institucional (periodicidade, publicação, competências normativas) | IX, X | ✅ | ✅ | Nada sobre periodicidade ou publicação. Q1 não é consentimento (FR-057). Nenhuma competência atribuída |
| 13 | Escopo por unidade e visão institucional consolidada | XII | N/A | N/A | Sem consulta por unidade nem autorização nesta feature; escopos de acesso em DP-505 |
| 14 | Privacidade, minimização e dados pessoais em logs/exportações | XVI, XVII | ⏸ | ⏸ | Mínimo de colunas; só o valor atual; nenhum log; rejeições sem valor declarado (R15). **DP-504 bloqueia uso real** (base legal, consentimento, retenção); DP-503 (abandono) e DP-505 (acesso) abertas. Sem violação: a feature só roda com dados fictícios |
| 15 | Autorização (menor privilégio; competência técnica ≠ normativa) | X, XII | N/A | N/A | Sem interface, admin, URL, comando ou API (FR-058); autorização virá com DP-505 |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG, quando houver interface) | XX | N/A | N/A | Sem interface |
| 17 | Responsividade e jornada móvel | XIV, XXI | N/A | N/A | Sem jornada. Início sem convite e rascunho editável preparam a 006 (XIV) |
| 18 | Testes proporcionais ao risco cobrindo invariantes afetados | XXV, XXVI | ✅ | ✅ | [Estratégia de testes](#estratégia-de-testes): unicidade, longitudinalidade, quatro tipos, Versão, coleta, atomicidade, concorrência, proveniência |
| 19 | Risco de over engineering (YAGNI; sem form builder universal) | XXII, XXIII, XXIV | ✅ | ✅ | 2 modelos de domínio + 1 tabela técnica; colunas tipadas, sem JSON, sem polimorfismo, sem tabela por tipo; sem estado, histórico, serviço, repositório, sinais ou framework de validação ou de locking. Complexity Tracking vazio |
| 20 | Exportabilidade e semântica das exportações (se aplicável) | XVIII | N/A | N/A | Exportação fora do escopo. Colunas tipadas e FKs para Opção facilitam exportação futura; comparabilidade entre Versões em 002/DP-006 |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ | ✅ | DP-501 a DP-508 e herdadas abaixo; as cinco escolhas de modelagem foram confirmadas pelo solicitante (Clarifications) |

**Resultado do gate**: APROVADO (pré-Fase 0 e pós-Fase 1). O item 14 está como DECISÃO
PENDENTE, sem violação: a capacidade é construída e testada só com dados fictícios, e o
uso real fica bloqueado por DP-504.

**Conflitos identificados**: nenhum com a Constituição. Tensões registradas na spec e
resolvidas por decisão do solicitante:

- Princípio VIII × substituição em rascunho: o princípio protege Participações
  diferentes; dentro da mesma Participação em rascunho, só o valor atual (Clarifications).
- Princípio XVII × respostas sem consentimento operacional: só dados fictícios (DP-504).

Um teste da 004 proibia globalmente os nomes dos novos modelos. Foi corrigido pelo
escopo do app (R16), sem efeito sobre a Constituição nem sobre requisitos da 004.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-501 | Pessoa com várias Conclusões elegíveis na mesma Campanha | CPAEG | Uma Participação por Conclusão, independentes, sem compartilhar respostas | Compartilhamento, se decidido, pela jornada (006) ou por regra nova; o modelo por Conclusão não muda |
| DP-502 | Prazo de graça após o fim da coleta | CPAEG/Proex | Nenhuma escrita fora de `EM_COLETA` | Gate localizado no passo 3 do esqueleto das escritas |
| DP-503 | Destino de Participações não concluídas | CPAEG + encarregado de dados | Preservadas e consultáveis; nenhuma remoção | Operação aditiva por spec própria |
| DP-504 | Base legal, consentimento e retenção das respostas | Encarregado de dados + CPAEG | Q1 é Resposta comum; **só dados fictícios** | Feature própria relaciona termo, momento, Participação e manifestação (XVII) |
| DP-505 | Quem consulta respostas identificadas e em qual escopo | CPAEG/Proex + encarregado de dados | Operações e consultas sem ponto de entrada | Autorização no ponto de entrada futuro; o domínio não muda |
| DP-506 | Registro por intermediário | CPAEG | Não suportado; toda Resposta é declarada pelo egresso | Proveniência de canal, aditiva, se aprovada |
| DP-507 | Efeito de correção acadêmica ou de mudança de elegibilidade sobre Participação existente | CPAEG + registro acadêmico | Elegibilidade só na criação; Participação continua válida | Regra localizada, se decidida; sem fotografia |
| DP-508 | Divergência entre resposta acadêmica declarada e Conclusão | CPAEG + registro acadêmico | Ambas preservadas; sem comparação | Consulta ou sinalização aditiva, sem mudar Respostas |
| 004/DP-404, 004/DP-406 | Campanhas sobrepostas; acesso e identificação | CPAEG; a identificar | A 005 não escolhe Campanha; recebe o par pronto | 006 / feature de acesso |
| 002/DP-007, 003/DP-302, 003/DP-309 | Termo de consentimento; Q46–Q48; dados sensíveis | Encarregado de dados, CPAEG | Fora da 005; nenhuma regra de jornada | 006 e features próprias |

Também continuam abertas 001/DP-005, 001/DP-009, 002/DP-001, 002/DP-006, 003/DP-303 e
004/DP-408 (spec, Decisões Pendentes).

## Desenho

### Modelos

Em [data-model.md](data-model.md):

- **Participacao**: `id`, `campanha` (FK `PROTECT`), `conclusao` (FK `PROTECT`),
  `iniciada_em`; `UNIQUE (campanha, conclusao)`; propriedades `pessoa`, `versao`,
  `pesquisa`.
- **Resposta**: `id`, `participacao` (FK `PROTECT`), `pergunta` (FK `PROTECT`), `opcao`
  (FK `PROTECT`, anulável), `texto`, `escala`, `complemento` (anuláveis), `opcoes` (M2M
  via `RespostaOpcao`); `UNIQUE (participacao, pergunta)`; CHECKs só de colunas da
  própria linha: no máximo um valor direto entre `opcao`, `texto` e `escala`; `texto` e
  `complemento` nunca cadeia vazia.
- **RespostaOpcao** (técnica): `id`, `resposta` (FK `CASCADE`), `opcao` (FK `PROTECT`);
  `UNIQUE (resposta, opcao)`.

Toda FK para modelo de feature anterior usa `related_name="+"` (R2).

### Representação por tipo

| Tipo | Representação |
|------|---------------|
| Escolha única | `Resposta.opcao` |
| Escolha múltipla | linhas de `RespostaOpcao` (conjunto; sem ordem; ≥ 1 pela operação) |
| Texto curto | `Resposta.texto` |
| Escala | `Resposta.escala` |
| Complemento de "Outro" | `Resposta.complemento`, válido só com a Opção de `complemento_textual` selecionada |

### Operações e rejeições

[contracts/operacoes.md](contracts/operacoes.md). Esqueleto das escritas de resposta:

1. `TypeError` para argumentos estruturais de classe errada;
2. transação; bloqueia a Participação (`select_for_update(of=("self",))`);
3. `estado(campanha, agora=…) is EM_COLETA`, sem reavaliar elegibilidade;
4. Pergunta relida pertence à Versão da Campanha;
5. tipo da Pergunta = tipo da operação;
6. valor válido para o tipo (Opções relidas do banco, limites de escala, complemento);
7. grava o valor inteiro no lugar (mesmo `id`) ou cria; substitui o conjunto de
   `RespostaOpcao` quando múltipla.

`iniciar_participacao`: busca → se existe, `JA_EXISTENTE` → senão
`admite_participacao` → insere em savepoint → `IntegrityError` ⇒ `JA_EXISTENTE`.
Rejeição de início reúne `COLETA_NAO_ADMITIDA` e `CONCLUSAO_NAO_ELEGIVEL`.

Exceção local `ParticipacaoRejeitada` com `Violacao(motivo, campo, detalhe)`, no padrão
de `campanha.regras` e `instrumento.regras`.

### Unicidade e concorrência

| Garantia | Mecanismo |
|----------|-----------|
| Campanha × Conclusão | `UNIQUE (campanha, conclusao)`; savepoint + `IntegrityError` → `JA_EXISTENTE` (R11) |
| Participação × Pergunta | `UNIQUE (participacao, pergunta)`; escritas serializadas pelo bloqueio da Participação |
| Resposta × Opção (múltipla) | `UNIQUE (resposta, opcao)`; deduplicação na operação |
| Escrita × encerramento explícito | Sem bloqueio da Campanha; vale o estado no momento de referência da escrita (R11) |

### Tempo

`agora` opcional em `iniciar_participacao`, nas escritas e em `admite_escrita`,
interpretado por `momento_de_referencia` e `estado` da 004. `iniciada_em` recebe o
momento de referência. Nenhum relógio novo (R13).

### Consultas

[contracts/consultas.md](contracts/consultas.md): `localizar_participacao`,
`participacoes_da_conclusao`, `admite_escrita`, `respostas_atuais` (dicionário por
Pergunta; ausência = não respondida).

### Contrato para a 006

A 006 recebe localizar/iniciar, consulta de respostas atuais, escrita validada e o gate
de coleta. Para acrescentar a conclusão, ela poderá adicionar à Participação um
`concluida_em` e verificá-lo no passo 3 do esqueleto, sem alterar as demais regras
(FR-056). Nada disso é criado aqui.

## Project Structure

### Documentation (this feature)

```text
specs/005-participacao-respostas-rascunho/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # R1–R17
├── data-model.md        # Participacao, Resposta, RespostaOpcao
├── quickstart.md        # validação
├── contracts/
│   ├── operacoes.md     # escrita e rejeições
│   └── consultas.md     # leitura e uso pela 006
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks (não criado por este comando)
```

### Source Code (repository root)

```text
trajetoria/
├── participacao/                     # NOVO app
│   ├── __init__.py
│   ├── apps.py                       # ParticipacaoConfig
│   ├── models.py                     # Participacao, Resposta, RespostaOpcao (técnica)
│   ├── regras.py                     # Motivo, Violacao, ParticipacaoRejeitada
│   ├── operacoes.py                  # iniciar_participacao, responder_escolha_unica,
│   │                                 # responder_escolha_multipla, responder_texto,
│   │                                 # responder_escala, remover_resposta
│   ├── consultas.py                  # localizar_participacao, participacoes_da_conclusao,
│   │                                 # admite_escrita, respostas_atuais
│   └── migrations/
│       ├── __init__.py
│       └── 0001_initial.py
├── campanha/                         # inalterado (consumido: estado, avaliar, admite_participacao,
│                                     # momento_de_referencia)
├── academico/                        # inalterado
├── instrumento/                      # inalterado
├── fonte_academica/                  # inalterado
└── formulario_2024/                  # inalterado (baseline continua RASCUNHO)

config/settings.py                    # + "trajetoria.participacao" em INSTALLED_APPS

tests/participacao/                   # NOVO
├── conftest.py                       # instrumento de teste publicado, Campanha aberta, Conclusões fictícias
├── construcao.py                     # momento(), instrumento com os quatro tipos e "Outro:",
│                                     # campanha_aberta(), rejeita(), linha()
├── test_participacao_modelo.py
├── test_participacao_inicio.py
├── test_participacao_respostas.py
├── test_participacao_rascunho.py
├── test_participacao_coleta.py
├── test_participacao_longitudinal.py
├── test_participacao_versao.py
├── test_participacao_consulta.py
├── test_participacao_concorrencia.py
└── test_participacao_aceitacao.py

tests/campanha/test_campanha_aceitacao.py   # inalterado pela 005 (correção R16 já na main, PR #6)

README.md                             # + link para o quickstart da 005
```

**Structure Decision**: um app Django novo no monolito, no padrão de `campanha` e
`instrumento`: modelos, vocabulário de rejeição, operações e consultas. Sem camada de
serviço, repositório, sinais ou tarefas. O app depende de `campanha`, `academico` e
`instrumento`; nenhum deles depende dele.

## Estratégia de testes

O foco são os invariantes (XXVI). Todo teste temporal passa `agora` explícito. Os
instrumentos de teste são montados e publicados pelas operações da 002 (uma Seção com
escolha única "Sim/Não", escolha única com "Outro:", escolha múltipla com "Outro:", texto
curto e escala 1–5); a baseline da 003 não é publicada nem alterada. Conclusões vêm da
fonte simulada ou do ORM com dados fictícios.

| Teste | Requisito |
|-------|-----------|
| Iniciar Participação válida: `CRIADA`, Campanha, Conclusão, `iniciada_em = agora`, zero respostas; Pessoa, Versão e Pesquisa derivadas | US1.1, US1.2, FR-002–FR-004, FR-011 |
| Início repetido: `JA_EXISTENTE`, mesmo `id`, mesmo `iniciada_em`, mesmas respostas, uma linha | US2.1, FR-013, SC-002 |
| Início repetido depois de Campanha encerrada devolve a existente e não habilita escrita | US2.3, FR-013, FR-039 |
| Nova Participação em Campanha encerrada (explícita e por data) ou em preparação: `COLETA_NAO_ADMITIDA`, nada criado | US1.4, US11.3, FR-039 |
| Conclusão não elegível: `CONCLUSAO_NAO_ELEGIVEL` com critérios no detalhe; com Campanha encerrada, as duas violações | US1.3, US1.5, FR-012 |
| Mesma Conclusão em duas (e três) Campanhas: Participações independentes; escrita em uma não muda as outras; nada copiado | US10, FR-007, FR-008, SC-003 |
| Duas Conclusões da mesma Pessoa na mesma Campanha: duas Participações | US10.5, FR-009 |
| Escolha única válida; Opção de outra Pergunta (mesmo texto "Sim"); `None`; lista; texto | US3, FR-024, FR-028 |
| Escolha múltipla válida; `{A, A}` → `{A}`; `{A, C}` = `{C, A}`; vazia → `VALOR_VAZIO`; `{A, X}` rejeita tudo; todas as Opções aceitas; "Não estudei mais" + outra aceito | US4, FR-025 |
| Limpar múltipla removendo a Resposta → Pergunta não respondida | US7.3, FR-025, FR-033 c |
| Texto válido preservado exatamente (espaços); vazio e só espaços rejeitados; Opção ou inteiro em texto → `VALOR_INCOMPATIVEL` | US5, FR-026 |
| Escala 1, 3, 5 aceitas; 0 e 6 → `ESCALA_FORA_DOS_LIMITES`; `2.5`, `"3"`, `True` → `VALOR_INCOMPATIVEL` | US6, FR-027 |
| Complemento "Outro" válido em única e em múltipla; sem a Opção que o admite → `COMPLEMENTO_NAO_ADMITIDO`; vazio → `VALOR_VAZIO`; "Outro" sem complemento aceito; substituição por outra Opção apaga o complemento | US8, FR-029–FR-031 |
| Substituir Resposta: mesmo `id`, valor novo integral, valor anterior sem rastro | US7.1, US7.2, FR-033 b, FR-035 |
| Remover Resposta: `REMOVIDA`; remover inexistente: `INEXISTENTE`; obrigatória removível | US7.3–US7.5, FR-036, FR-037 |
| Atomicidade da substituição de múltipla: `{A, B}` gravado; `{C, X}` rejeitado → continua `{A, B}`; complemento inválido → valor anterior intacto | US12.4, FR-051 |
| Mudar resposta de Pergunta com regra não altera outras Respostas; Pergunta de Seção "pulada" aceita | FR-038 |
| Leitura depois do encerramento: Participação e Respostas idênticas e consultáveis; `admite_escrita` falso | US11.4, FR-040, FR-048 |
| Escrita depois do encerramento (explícito e por data): registrar, substituir e remover → `COLETA_NAO_ADMITIDA`, linhas idênticas; último dia aceito | US11.1, US11.2, US11.5, FR-039, SC-008 |
| Pergunta de outra Versão (2028 criada de 2027, textos idênticos) → `PERGUNTA_DE_OUTRA_VERSAO`; Opção da Pergunta correspondente de 2028 → `OPCAO_DE_OUTRA_PERGUNTA`; publicar 2028 não muda nada em 2027 | US12, FR-019–FR-021, SC-006, SC-010 |
| Elegibilidade não reavaliada: Participação criada; a Conclusão é alterada por ORM para ficar fora dos critérios (simula 001/DP-005); escrita continua aceita, início repetido devolve a existente | FR-034, DP-507 |
| Concorrência de criação, determinística: busca não encontra, insert viola a unicidade → `JA_EXISTENTE`, uma linha, mesmo `id` | FR-006, FR-053, SC-002 |
| Concorrência real (opcional, R17): duas threads com barreira, banco transacional → uma Participação; removido se instável no CI | FR-006, FR-053 |
| Escritas serializadas: a operação bloqueia a Participação (`select_for_update(of=("self",))`); uma Resposta por Pergunta mesmo após escritas repetidas | FR-018, FR-053 |
| Proveniência: Conclusão com unidade "Serra" e resposta de campus com outra Opção coexistem; linha da Conclusão idêntica antes e depois de todas as escritas | US9.4, FR-042, FR-043, SC-009 |
| `respostas_atuais`: não respondida ausente; valores por tipo; `localizar_participacao` sem criar | US9, FR-046, FR-047 |
| Mensagens de rejeição não contêm texto, inteiro ou complemento declarados | FR-059 |
| CHECKs e UNIQUEs por escrita direta no ORM; `PROTECT` em Opção referida | data-model |
| Exatamente `{Participacao, Resposta, RespostaOpcao}` no app; nenhum modelo proibido (Submissao, Tentativa, Sessao, Rascunho, HistoricoResposta, VersaoResposta, Progresso, FotografiaPergunta, Convite, Token, Consentimento…); `Campanha`, `ConclusaoAcademica`, `Pergunta`, `Opcao` sem colunas novas; nenhum campo de conclusão ou estado | SC-011, FR-055 |

## Complexity Tracking

Vazio. Nenhuma violação a justificar: dois modelos de domínio, uma tabela técnica de
junção com `PROTECT`, colunas tipadas, sem dependência nova e sem infraestrutura.

## Necessidade de voltar à spec ou às features anteriores

**Spec**: nenhuma mudança de comportamento. Precisões do plan que não alteram requisitos:

- FR-052 (f) "valor de forma incompatível" cobre também chamar a operação de um tipo
  para Pergunta de outro tipo, porque as operações são por tipo (R7).
- FR-030 (b) "complemento em texto ou escala" é impossível pela assinatura das
  operações desses tipos, e não precisa de motivo próprio.
- O banco não garante "≥ 1 Opção" em escolha múltipla; a operação garante (R5).

**Feature 004 — correção de escopo de teste (R16), já na `main`** (pela própria 004, em
saymoncastro/ifes-trajetoria-egressos#6; fora do diff da 005): o antigo
`test_um_unico_modelo_novo_e_nenhum_proibido` proibia, no projeto inteiro, modelos
chamados `Participacao`, `Resposta`, `Convite` etc. Era excessivamente amplo: a intenção
de 004 SC-009 é que o **app `campanha`** tenha só `Campanha`, não impedir features
posteriores. Ele virou `test_app_campanha_tem_somente_o_modelo_campanha`, com a igualdade
dos modelos do app e sem lista global de nomes. Não é mudança de requisito da 004 e
nenhum código de produção da 004 mudou. Suíte da 004: 225 testes verdes; ruff limpo.

**Constraints de Resposta**: o CHECK "complemento só em escolha" descrito na primeira
versão deste plan foi retirado. Embora usasse só colunas da linha, ele exprimia uma regra
que depende do tipo da Pergunta; a regra fica inteira nas operações (complemento só em
Pergunta de escolha e só com a Opção que o admite selecionada).

**Base do branch**: a 004 entrou em `main` (PR #5, 2026-10-01). Este branch foi
atualizado contra a nova `main` (fast-forward, sem diferença de conteúdo). Antes de abrir
ou finalizar o PR da 005, atualizar de novo contra `main`.
