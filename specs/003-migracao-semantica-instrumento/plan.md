# Implementation Plan: Migração semântica do instrumento institucional vigente

**Branch**: `claude/feature-003-semantic-migration-64c1ed` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-migracao-semantica-instrumento/spec.md`

## Summary

A 003 é **conteúdo estruturado + uma operação de materialização + testes**. Não há
domínio novo:

- **Zero modelos, campos ou migrações.** A baseline é uma instância das entidades da 002
  (1 Pesquisa, 1 Versão em RASCUNHO, 13 Seções, 54 Perguntas, 385 Opções, 10 regras,
  7 encaminhamentos).
- **Declaração em Python** (`trajetoria/formulario_2024/declaracao.py`): duas dataclasses
  mínimas e constantes, com as chaves Q1–Q54 e S1–S13 apenas em memória, e as listas
  extensas um item por linha (R3).
- **Operação explícita `materializar()`** (`trajetoria/formulario_2024/materializacao.py`):
  constrói a baseline **só pelas operações da 002**, em uma transação (R4, R7);
  identifica a baseline pela Pesquisa e pela designação aprovadas (R5); compara por
  valor a baseline existente com a declaração; se forem equivalentes, não faz nada; se
  divergirem, falha sem alterar nada (R6). Nunca publica.
- **Fidelidade provada por um oráculo independente da declaração**: manifesto explícito
  de expectativas nos testes, transcrito da Matriz, e leitura do inventário apenas como
  texto bruto para confirmar que cada texto e cada lista extensa estão documentados. A
  declaração é a única fonte executável; o inventário não é parseado (R10).

Decisões e alternativas estão em [research.md](research.md).

## Technical Context

- **Language/Version**: Python 3.13 ([ADR 0001](../../docs/adr/0001-stack-inicial.md)).
- **Primary Dependencies**: Django 5.2 LTS e psycopg 3. Nenhuma dependência nova.
- **Storage**: PostgreSQL 16+. Nenhuma alteração de esquema. Só linhas nas tabelas da
  002.
- **Testing**: pytest, pytest-django e ruff, em PostgreSQL, sem rede. Os testes leem o
  inventário versionado em `docs/referencias/` apenas como texto bruto (R10).
- **Target Platform**: servidor Linux, para operação futura; nesta feature, execução local
  e CI.
- **Project Type**: aplicação web monolítica (Django), ainda sem camada web.
- **Performance Goals**: N/A. Uma materialização são cerca de 470 operações da 002;
  os testes de leitura materializam uma vez por módulo (R11).
- **Constraints**:
  - escrita só pelas operações da 002;
  - textos exatamente como na declaração, que segue o inventário;
  - nenhuma alteração em `trajetoria/instrumento/`, `trajetoria/academico/`,
    `trajetoria/fonte_academica/` nem nos testes das Features 001 e 002;
  - Versão sempre em RASCUNHO;
  - nenhum ponto de entrada novo (R12).
- **Scale/Scope**: 1 pacote com 3 módulos; 3 arquivos de teste e 1 manifesto; 0 migrações.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | N/A | N/A | Nenhum elo criado. A baseline é uma Versão que Respostas futuras poderão referenciar |
| 2 | Pessoa versus Conclusão Acadêmica | I, XI | N/A | N/A | Nada importado de `academico`; teste garante 0 linhas de Pessoa/Conclusão após materializar (SC-009) |
| 3 | Múltiplas formações sem fusão | I, XI | N/A | N/A | Fora do escopo. A baseline conserva "uma formação por resposta" do original (O-9) só como conteúdo |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | N/A | N/A | Participação fora do escopo |
| 5 | Definição institucional de egresso | II | N/A | N/A | Fora do escopo |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | Conteúdo do original preservado e verificado por manifesto independente e pelo texto do inventário (R10). Única correção explícita (E-08) antes de qualquer uso. Nenhuma migração de esquema nem de dados; nada existente é alterado; divergência interrompe sem escrever (R6) |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ | ✅ | Usa Pesquisa e Versão da 002; nenhuma Campanha ou Participação |
| 8 | Proveniência proporcional | IV | ✅ | ✅ | Rastreabilidade Q1–Q54 na Matriz, na declaração e nos testes, sem metadado persistido (R9). Designação identifica a baseline |
| 9 | Dado institucional ≠ derivado ≠ declarado | III | ✅ | ✅ | As 17 candidatas continuam perguntas declaradas; nenhum vínculo Pergunta → atributo acadêmico; listas de cursos não alimentam a 001 (FR-029, FR-030; R13) |
| 10 | Desacoplamento de integrações | V, XV, XXV | N/A | N/A | Sem integração. Importação do Google Formulários fora do escopo |
| 11 | Fronteira do NIAE | VI | N/A | N/A | Conteúdo do instrumento, dentro do domínio já aprovado na 002 |
| 12 | Governança institucional (publicação, elaboração do instrumento) | IX, X | ⏸ | ⏸ | `materializar()` nunca publica; sem ponto de entrada novo (R12). Designação e baseline não equivalem a aprovação (FR-004). Publicação: 002/DP-001 e DP-002 |
| 13 | Escopo por unidade / visão institucional | XII | N/A | N/A | Pesquisa institucional única |
| 14 | Privacidade, minimização, consentimento | XVI, XVII | ✅ | ✅ | Nenhum dado pessoal. Termos e Q1 como conteúdo, sem registro de consentimento (002/DP-007). Perguntas sensíveis preservadas sem decidir tratamento (DP-309). Mensagens de erro sem dado pessoal |
| 15 | Autorização | X, XII | N/A | N/A | Sem interface, comando, admin ou API |
| 16 | Acessibilidade | XX | N/A | N/A | Sem interface. Textos e rótulos ficam disponíveis para a 004; rótulo inicial ausente registrado em DP-301 |
| 17 | Responsividade e jornada móvel | XIV, XXI | N/A | N/A | Sem jornada. Candidatas a contexto identificadas para reduzir fricção no futuro (FR-029) |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ | ✅ | Fidelidade independente da declaração (R10), navegação, idempotência, divergência e atomicidade ([Estratégia de testes](#estratégia-de-testes)) |
| 19 | Over engineering (YAGNI; sem form builder) | XXII, XXIII, XXIV | ✅ | ✅ | Pacote sem app; duas dataclasses; uma operação; nenhuma DSL, parser de produção, motor de diff, framework de seed ou condição de exibição (R13). [Complexity Tracking](#complexity-tracking) vazio |
| 20 | Exportabilidade | XVIII | N/A | N/A | Fora do escopo |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ | ✅ | DP-301 a DP-310 e herdadas preservadas ([Decisões Pendentes](#decisões-pendentes)). Lacunas como `None`, irregularidades preservadas, sem atributo de momento de regra |

**Resultado do gate**: APROVADO (pré-Fase 0 e pós-Fase 1). O item 12 permanece como
DECISÃO PENDENTE, sem violação: nada é publicado.

**Tensões registradas** (não são conflitos):

- **XIII × XIV**: o Princípio XIV pede "contextualizar em vez de perguntar", mas a baseline
  mantém Q10–Q19 e outras candidatas como perguntas. Isso é intencional: o XIII veda
  revisão silenciosa e a contextualização depende de fonte real (DP-307). A redução fica
  para feature futura, sem reescrever a baseline.
- **XX × DP-301**: escalas sem rótulo inicial seriam pior para acessibilidade se
  apresentadas assim. A Versão não é publicada nem apresentada nesta feature; DP-301
  DEVERIA ser resolvida antes de publicar.
- **XVII**: Q1 com finalização reproduz o termo vigente, mas não é consentimento
  rastreável. A 004 não pode tratá-lo como tal sem 002/DP-007.

## Decisões Pendentes

Todas permanecem abertas. Nenhuma é resolvida por código.

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória na baseline | Como reverter |
|----|------------------|----------------------|-------------------------------|---------------|
| DP-301 | Texto exato do rótulo inicial das escalas | Confirmação na fonte original autorizada (Proex/CPAEG) | `rotulo_inicio = None` nas 11 escalas | Em RASCUNHO: ajustar a declaração e a baseline existente (a reexecução acusará divergência até que ambas coincidam). Depois de publicada: nova Versão |
| DP-302 | Q47/Q48 apresentadas a todos em S11: intenção ou acidente; momento de aplicação das regras | CPAEG (intenção); Feature 004 (execução) | Ordem Q46, Q47, Q48 em S11; regras em Q46; sem atributo de momento | Feature 004 define a execução; mudança de estrutura, se houver, em nova Versão |
| DP-303 | Condicional explícita de Q6 | CPAEG | Q6 opcional, sem condição | Nova Versão (e 002/DP-005, se exigir capacidade nova) |
| DP-304 | Obrigatoriedade de Q42 e Q44 | CPAEG | Opcionais; Q43 obrigatória | Nova Versão |
| DP-305 | Faixas de Q38 e Q39 | CPAEG | Faixas originais | Nova Versão, com análise de comparabilidade (002/DP-006) |
| DP-306 | "Campus" em Q40 para EaD/Cefor | CPAEG | Texto original | Nova Versão |
| DP-307 | Quais perguntas acadêmicas e Q3 saem da jornada | CPAEG, áreas de ensino, gestor da fonte (depende de 001/DP-001, DP-004, DP-007) | Todas como perguntas declaradas | Feature de jornada contextualizada |
| DP-308 | Fontes para Q22–Q24, Q27, Q31, Q32 (e parte de Q47, Q49, Q51) | A identificar | Perguntas declaradas | Feature futura com fonte verificada |
| DP-309 | Dados sensíveis (Q2, Q4–Q6) e assimetria de "Prefiro não responder" | Encarregado de dados, CPAEG | Perguntas e Opções originais | Nova Versão e regras de exportação |
| DP-310 | Preocupações das notas internas (lista de Pós-Graduação; posição de Q41) | CPAEG | Notas não migradas; lista e posição originais | Nova Versão |
| 002/DP-001 a DP-007 | Publicação, workflow, correção pós-publicação, melhorias metodológicas, novas capacidades, comparabilidade, consentimento | Ver 002 | Como na 002 | Ver 002 |
| 001/DP-001, DP-004, DP-007 | Fonte acadêmica oficial, qualidade de Q10–Q19, vocabulário canônico | Ver 001 | Como na 001 | Ver 001 |

## Desenho

### Onde fica o conteúdo

`trajetoria/formulario_2024/declaracao.py` ([data-model](data-model.md#declaração-em-código-não-persistida)):

```text
NOME_PESQUISA, DESIGNACAO
TITULO, TEXTO_ABERTURA, TEXTO_ENCERRAMENTO, TEXTO_TERMOS
LISTA_C, LISTA_E, LISTA_15, LISTA_17, LISTA_18, LISTA_19   # um item por linha
SECOES = (
    SecaoDeclarada("S1", "Termos e condições", TEXTO_TERMOS, perguntas=(
        PerguntaDeclarada("Q1", ESCOLHA_UNICA, "Você concorda com os termos acima?",
                          obrigatoria=True, opcoes=("Sim", "Não"),
                          regras=(("Sim", "S2"), ("Não", FINALIZAR))),
    )),
    ...
    SecaoDeclarada("S12", "Egresso que estuda", None, encaminhamento="S13", perguntas=(
        ...,
        PerguntaDeclarada("Q51", ...),  # E-07: regra redundante não reproduzida
    )),
    SecaoDeclarada("S13", None, None, perguntas=(...)),  # E-08 nos rótulos de Q52–Q54
)
```

A ordem das tuplas é a ordem da baseline. A forma acima é ilustrativa; o conteúdo é o da
[Matriz](spec.md#matriz-de-migração-q1q54).

### Como é materializado

`materializar()` ([contrato](contracts/materializacao.md)):

1. abre `transaction.atomic()`;
2. localiza ou cria a Pesquisa; recusa se o nome estiver repetido (`PesquisaAmbigua`);
3. se a Versão com a designação existe: compara `forma_da_versao` com `forma_esperada`;
   iguais → retorna `criada=False`; diferentes → `BaselineDivergente`;
4. senão: `criar_versao`, `alterar_versao`; Seções, Perguntas e Opções na ordem; depois
   encaminhamentos e regras; compara a forma criada com a esperada (pós-condição);
   retorna `criada=True`.

Qualquer exceção desfaz a transação inteira. Nenhum passo chama `publicar`.

### Como a divergência é detectada

Por valor, sobre uma forma em tuplas que ignora identidades, estado, origem, designação e
nome da Pesquisa ([R6](research.md#r6--equivalência-e-divergência)). O diagnóstico aponta
a primeira diferença (`S9·8: texto explicativo difere`). Não há diff completo,
reconciliação nem reparo.

### Como Q1–Q54 continuam auditáveis

Matriz da spec → chave `Qn` na declaração → teste que localiza a n-ésima Pergunta da
baseline e cita a linha da Matriz ([R9](research.md#r9--rastreabilidade-q1q54)). Nada disso
é persistido.

### Grandes listas

Constantes com um item por linha. Nos testes: quantidade e extremidades no manifesto, e a
sequência completa, unida por `"; "`, encontrada literalmente no texto do inventário. Sem
catálogo, deduplicação global ou vínculo com a 001
([R3](research.md#r3--forma-da-declaração), [R10](research.md#r10--prova-de-fidelidade-independente-da-declaração)).

## Estratégia de testes

Foco em fidelidade e regressão (XXVI). Verificações tabulares que reúnem todas as
diferenças numa única falha legível, em vez de dezenas de testes de uma asserção, e sem
snapshot monolítico.

Oráculo ([R10](research.md#r10--prova-de-fidelidade-independente-da-declaração)): um
**manifesto de expectativas** em `tests/instrumento/formulario_2024_esperado.py`
(dados de teste e fixtures, não é teste), transcrito da Matriz, e uma fixture que lê o
inventário **como texto bruto** (espaços colapsados, sem
`> `) só para verificar ocorrência literal. Nenhum parser de Markdown. Os testes de
navegação reutilizam `percursos_de_secoes` de `tests/instrumento/construcao.py` (002) sem alterá-lo.

**`test_formulario_2024_fidelidade.py`** (fixture de módulo, materializa uma vez — R11)

| Verificação | Fonte da expectativa | Requisito |
|-------------|----------------------|-----------|
| A declaração tem S1–S13 e Q1–Q54 únicas e em ordem | Declaração | FR-009, FR-012 |
| 13 Seções com títulos e textos; S13 sem título; S7 sem texto; textos da Versão | Manifesto (tabela "Seções da baseline") | FR-016, FR-017 |
| Para cada Qn: Seção, posição, tipo, obrigatoriedade, Opções em ordem (ou lista nomeada) | Manifesto (Matriz) | FR-008–FR-011, SC-003 |
| Listas C, E, 15, 17, 18, 19 em Q8, Q9, Q11, Q15, Q17, Q18, Q19: quantidade e extremidades; sequência completa unida por `"; "` ocorre literalmente no texto bruto do inventário; Q8 e Q9 com Opções distintas | Manifesto + inventário (texto bruto) | FR-007, FR-015, FR-030 |
| Todo texto da baseline ocorre literalmente no texto bruto do inventário (exceto o rótulo E-08) | Inventário (texto bruto) | FR-007 |
| Contagens: 54 Perguntas (38/3/2/11), 50/4, 41 com Opções, 385 Opções, 3 complementos, 3 textos explicativos, 11 escalas | "Contagens verificáveis" | SC-002 |
| Escalas 1–5; rótulo inicial `None` (não cadeia vazia) nas 11; finais por pergunta; Q48 minúsculo | Tabela "Escalas" | FR-018–FR-020 |
| Q52–Q54 com "Concordo totalmente"; nenhum "Corcordo" em nenhum texto | E-08 | FR-021, SC-005 |
| Notas E-05 e E-06 ausentes de todos os textos; S7 sem texto; Q41 sem texto explicativo; Lista 19 sem acréscimo | E-05, E-06 | FR-027, FR-028 |
| Textos explicativos só em Q10, Q32 ("auxilio" preservado), Q48 | Matriz | FR-013 |
| Complemento só no "Outro:" de Q26, Q32, Q45 | Matriz | FR-014 |
| Preservações de US9: Q38/Q39 faixas, Q40 "campus", Q13 três Opções, Q6 opcional sem regra, Q42/Q44 opcionais e Q43 obrigatória, Q3 e Q10 texto curto | Matriz | FR-011, FR-029, SC-010 |

**`test_formulario_2024_navegacao.py`** (mesma fixture de módulo)

| Verificação | Requisito |
|-------------|-----------|
| Exatamente 10 regras: Q1 (Sim → S2, Não → finalizar), Q14 (→ S4, S5, S6, S7), Q33 (→ S9, S10), Q46 (→ S12, S13); nenhuma outra pergunta com regra | FR-022, FR-023 |
| Q51 sem regra em nenhuma Opção | FR-024 (E-07) |
| Exatamente 7 encaminhamentos: S4–S7 → S8; S9, S10 → S11; S12 → S13 | FR-025 |
| `percursos_de_secoes` produz exatamente os 17 percursos da spec; Q1 = "Não" termina em S1 | US4, SC-004 |
| Q46, Q47, Q48 em S11, posições 1–3; Q46 é a única pergunta com regras seguida de outras na Seção | FR-026 |
| `verificar_completude` da 002 devolve nenhuma violação, e a Versão continua em RASCUNHO | FR-006 |

**`test_formulario_2024_materializacao.py`** (materializa por teste)

| Cenário | Verificação | Requisito |
|---------|-------------|-----------|
| A. Primeira execução | `criada=True`; 1 Pesquisa com o nome; 1 Versão com a designação; RASCUNHO; sem `publicada_em` nem `origem`; forma igual à esperada | US1, FR-001–FR-005 |
| B. Segunda execução | `criada=False`; mesmas identidades (Pesquisa, Versão, Seções, Perguntas, Opções); `conteudo_da_versao` igual (`==`); contagens iguais | US8, FR-032, SC-007 |
| C. Divergência | Após cada alteração por operação da 002 (texto de Opção, Pergunta removida, regra acrescentada, texto da Versão, obrigatoriedade): `BaselineDivergente` com local da diferença e `conteudo_da_versao` igual ao de antes da chamada | FR-033 |
| Pesquisa existente sem a Versão | Versão criada nela; nenhuma Pesquisa nova | FR-031 |
| Pesquisa homônima repetida | `PesquisaAmbigua`; nenhuma linha nova | FR-031 |
| Baseline publicada no teste | Reexecução equivalente é no-op; não altera estado nem `publicada_em` | US8 (cenário 5) |
| Atomicidade | Operação da 002 forçada a falhar (monkeypatch) na última etapa: nenhuma Pesquisa, Versão, Seção, Pergunta ou Opção nova | FR-032 |
| Commit real | `django_db(transaction=True)`: materializar e confirmar; unicidade adiada aceita | FR-032 |
| Sem efeito na 001 | 0 Pessoas e 0 Conclusões antes e depois | FR-030, FR-041, SC-009 |
| Sem modelo ou migração novos | `instrumento` com 5 modelos e só `0001_initial`; `academico` só com `0001_initial`; `formulario_2024` não é app e não importa `academico` nem `fonte_academica` | FR-040, FR-041, SC-008 |

Os testes das Features 001 e 002 não são alterados e devem continuar passando.

## Project Structure

### Documentation (this feature)

```text
specs/003-migracao-semantica-instrumento/
├── spec.md                 # inclui a Matriz de Migração Q1–Q54
├── plan.md                 # este arquivo
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── materializacao.md
├── checklists/requirements.md
└── tasks.md                # gerado por /speckit-tasks (não por este comando)
```

### Source Code (repository root)

```text
trajetoria/
├── academico/              # Feature 001 — não alterado
├── fonte_academica/        # Feature 001 — não alterado
├── instrumento/            # Feature 002 — não alterado
└── formulario_2024/        # esta feature; pacote Python, não app Django
    ├── __init__.py         # reexporta materializar, Resultado e exceções
    ├── declaracao.py       # SecaoDeclarada, PerguntaDeclarada, constantes, listas, SECOES
    └── materializacao.py   # materializar, forma_esperada, forma_da_versao, exceções
tests/
├── (arquivos das Features 001 e 002 — não alterados)
└── instrumento/
    ├── formulario_2024_esperado.py             # manifesto + fixtures (sem parser)
    ├── test_formulario_2024_fidelidade.py
    ├── test_formulario_2024_navegacao.py
    └── test_formulario_2024_materializacao.py
```

**Structure Decision**:

- Um pacote, sem app, sem `INSTALLED_APPS`, sem migração (R2).
- Testes em `tests/instrumento/` porque consomem as fixtures e auxiliares de lá
  (`construcao.percursos_de_secoes`); prefixo `test_formulario_2024_` evita colisão.
- `config/settings.py`, `pyproject.toml` e CI não mudam: `trajetoria` já é o pacote do
  wheel, e o CI já roda `pytest`, `ruff` e `makemigrations --check`.

## Complexity Tracking

Nenhuma violação a justificar. Nenhuma estrutura da lista de exceção (novo modelo,
framework de seed, DSL, parser customizado, catálogo acadêmico, engine de regras, diff
engine, sincronização, editor, interface administrativa, API) é criada.

Complexidade mínima adotada, com justificativa (não é violação):

- **Duas dataclasses de declaração**: tipam a declaração; alternativa (dicionários)
  deixaria erros para a execução (R3).
- **Forma por valor + diagnóstico da primeira diferença**: exigida por FR-033; percorre
  duas tuplas em paralelo, sem diff completo (R6).
- **Manifesto de expectativas nos testes**: oráculo independente da declaração (FR-039);
  o inventário é lido só como texto bruto, sem parser (R10).

## Revisão pós-implementação (2026-10-01, T031)

Gate mantido. Definition of Done atendida:

- 42 testes novos (fidelidade, navegação, materialização); suíte completa com 318
  testes passando, sem alteração nos testes das Features 001 e 002;
- `git diff` contra `main` vazio em `trajetoria/instrumento`, `trajetoria/academico`,
  `trajetoria/fonte_academica`, `config`, `pyproject.toml`, `uv.lock`, `.github` e nos
  testes da 001/002; `makemigrations --check` sem mudanças;
- produção em 3 arquivos novos (`trajetoria/formulario_2024/`), dos quais só
  `materializacao.py` tem comportamento; nenhum modelo, migração, app, comando, admin ou
  API;
- a Versão termina em RASCUNHO; nenhuma chamada a `publicar` em produção (verificado por
  AST no teste);
- nenhum dado pessoal; nenhum log novo;
- o oráculo detectou 5 mutações provocadas na declaração (troca de itens da Lista 19,
  troca de textos Q8/Q9, Opção removida em Q35, "auxilio" acentuado, texto de Q53
  alterado);
- DP-301 a DP-310 e as herdadas continuam abertas; nenhuma virou regra implícita;
- uma correção de contagem na spec (texto de abertura com 4 parágrafos), registrada em
  [tasks.md](tasks.md#notas-de-implementação).

## Necessidade de voltar à spec

Nenhuma. Todas as linhas da Matriz são representáveis com a 002 sem ajuste. Durante o
desenho, só uma precisão foi feita no plan, sem mudar a spec: o "conteúdo" comparado em
FR-033 é o da tabela de equivalência do [contrato](contracts/materializacao.md#equivalência).

## Para specs futuras

- **Feature 004 (jornada)**: consome `materializar()` ou a Versão já existente; define o
  momento de aplicação das regras sem suprimir Q47/Q48 por omissão (DP-302); trata Q1 sem
  presumir consentimento operacional (002/DP-007); define a apresentação (botões ou lista).
- **Publicação da baseline**: depende de 002/DP-001 e, recomendavelmente, de DP-301.
- **Contextualização acadêmica**: decide quais candidatas saem da jornada (DP-307,
  DP-308), sem reescrever a baseline.
