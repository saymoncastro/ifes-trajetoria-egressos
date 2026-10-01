---

description: "Tasks da Feature 007 — Contextualização da formação e entrada na pesquisa"
---

# Tasks: Contextualização da formação e entrada na pesquisa

**Input**: Design documents from `specs/007-contextualizacao-formacao-entrada/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/entrada.md](contracts/entrada.md),
[quickstart.md](quickstart.md)

**Stack (confirmada; [ADR 0001](../../docs/adr/0001-stack-inicial.md))**: Python 3.13,
Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff. Nenhuma dependência
nova. **Zero modelos novos, zero migrações**, nenhum app novo, nenhum gatilho, sinal,
cache, serviço, repositório ou job.

**Tests**: obrigatórios e escritos antes da implementação correspondente (test-first). A
feature toca invariantes constitucionais (Pessoa ↔ Conclusão Acadêmica, múltiplas
conclusões e participações, longitudinalidade, elegibilidade, dado institucional ≠
declarado). Testes de comportamento novo DEVEM falhar primeiro. Histórias que só
verificam comportamento já entregue por história anterior (US5, US6, US8, US9, US11 em
parte) podem passar de imediato; se falharem, a correção vai em
`trajetoria/participacao/entrada.py`, sem regra especial.

**Organization**: tarefas agrupadas pelas histórias da spec (US1–US11).
`trajetoria/participacao/entrada.py` e cada arquivo de teste são editados em sequência.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US11).

## Convenções para todas as tarefas

- **Um único módulo de produção novo**: `trajetoria/participacao/entrada.py`. Nenhum
  arquivo existente de `trajetoria/` é alterado (FR-052). `operacoes.py`, `consultas.py`,
  `models.py`, `regras.py`, `percurso.py` e `migrations/` da `participacao` ficam
  intactos.
- **Composição, não reimplementação** ([contrato](contracts/entrada.md#dependências-permitidas)):
  `entrada.py` importa só `Pessoa`, `ConclusaoAcademica` (001), `Campanha`,
  `campanhas_em_coleta_para`, `momento_de_referencia` (004), `Participacao` (leitura) e
  `iniciar_participacao`, `SituacaoInicio` (005). **Não** importa `avaliar`, `estado`,
  `_filtro`, `_campanhas_que_admitem`, `campanha.operacoes`, `percurso`,
  `situacao_da_jornada`, `concluir`, `fonte_academica`, `academico.incorporacao`,
  `django.contrib.auth`, `django.http`, `django.urls`. Não persiste nenhum modelo por
  conta própria: a única escrita possível é a de `iniciar_participacao` (verificado por
  comportamento em T023, não por inspeção do código-fonte). Nenhum log.
- **Estruturas finais (YAGNI)** — exatamente estas, sem outras
  ([data-model](data-model.md#valores-derivados-não-persistidos)):
  - `SituacaoDaFormacao(Enum)`: `SEM_PESQUISA`, `DISPONIVEL_PARA_INICIAR`,
    `DISPONIVEL_PARA_RETOMAR`, `JA_CONCLUIDA`, `AMBIGUIDADE_OPERACIONAL`; propriedade
    `pendente` — "verdadeira só para as duas situações 'disponível'";
  - `Formacao` (`@dataclass(frozen=True)`): `conclusao: ConclusaoAcademica`,
    `situacao: SituacaoDaFormacao`, `campanhas: tuple[Campanha, ...]` ("Campanhas
    aplicáveis, na ordem `(inicio, id)` da 004, sem preferência; vazia em
    `SEM_PESQUISA`, todas em `AMBIGUIDADE_OPERACIONAL`"), `participacao: Participacao |
    None` ("Presente só em `DISPONIVEL_PARA_RETOMAR` e `JA_CONCLUIDA`"); propriedade
    `campanha` ("a única Campanha aplicável, ou `None` fora de 1");
  - `ResolucaoDaEntrada(Enum)`: `SEM_FORMACAO`, `SEM_PESQUISA`, `SEM_ENTRADA_PENDENTE`,
    `ENTRADA_RESOLVIDA`, `SELECAO_NECESSARIA`;
  - `SituacaoDeEntrada` (`frozen`): `formacoes: tuple[Formacao, ...]` ("**Todas** as
    Conclusões da Pessoa, na ordem da 001"), `resolucao: ResolucaoDaEntrada`;
    propriedade `pendentes`;
  - `Entrada` (`frozen`): `situacao: SituacaoDeEntrada`, `participacao: Participacao |
    None` ("`None` ⇔ nada a iniciar ou retomar"), `criada: bool` ("Verdadeiro só quando a
    005 devolveu `CRIADA`");
  - `FormacaoDeOutraPessoa(Exception)`.

  **Não criar**: `DesfechoDaEntrada`, `Entrada.formacao`, `SituacaoDeEntrada.pessoa`,
  `.momento`, `.resolvida`, `Formacao.entrada_pendente`, rótulo/descrição de formação,
  campos copiados da Conclusão.
- **Tempo**: `situacao_de_entrada` e `entrar` recebem `agora: datetime | None = None`,
  resolvido **uma vez** por `momento_de_referencia` e repassado à 004 e à 005. **Todo
  teste passa `agora` explícito** (`momento(...)`, `NO_PERIODO`, `ULTIMO_DIA`,
  `DEPOIS_DO_FIM` de `tests/participacao/construcao.py`).
- **Testes**: `tests/participacao/` continua **sem** `__init__.py`; auxiliares via
  `from tests.participacao.construcao import …` e
  `from tests.participacao.construcao_entrada import …`. `tests/participacao/construcao.py`
  e `conftest.py` **não** são alterados. Testes de banco com `@pytest.mark.django_db`
  (ou `pytestmark` no módulo); testes puros de classificação **sem** `django_db`.
  Somente dados fictícios.

## Limites desta lista (não criar)

- App novo; modelo; migração; coluna; índice; tabela auxiliar; cache; materialização;
  snapshot ou token da resolução.
- EntrySession, ContextSession, Context, Selection, EnrollmentChoice, EnrollmentOption,
  EligibleFormation, EligibleCampaignMembership, CampaignAssignment, CampaignResolver
  genérico, PortalUser, Usuario, Conta, Credential, Login, Identity, IdentityProvider,
  AuthenticationProvider, PersonResolver, IdentityResolver, PersonMatcher; máquina de
  estados; workflow.
- Busca de Pessoa; entrada por CPF, e-mail, matrícula ou nome; sessão; OTP; Gov.br.
- Cópia dos filtros/critérios da 004; regra nova de período, elegibilidade ou prioridade;
  escolha automática entre Campanhas sobrepostas; desempate pela Participação.
- Criação direta de `Participacao`; reabertura ou edição de Participação concluída.
- Resposta criada a partir da Conclusão; alteração, ocultação ou pré-preenchimento de
  Q10–Q19.
- Interface, HTML, ViewModel, URL, view, admin, API, comando de gestão; dashboard,
  indicador, exportação, GeN.
- Alteração em código, contrato ou teste das Features 001–006.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar a base. Nada é criado.

- [X] T001 Confirmar a base do branch: `git log --oneline main -1` está contido no branch
  (006 incorporada — saymoncastro/ifes-trajetoria-egressos#8); rodar `uv run pytest`,
  `uv run ruff check .` e `uv run python manage.py makemigrations --check --dry-run` e
  registrar que estão verdes e limpos antes de qualquer mudança. Anotar o número de
  testes e a lista de migrações existentes
  (`ls trajetoria/*/migrations/0*.py`) para comparação em T034.

**Checkpoint**: suíte 001–006 verde.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: tipos e regras puras de classificação, e auxiliares de teste usados por
todas as histórias.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T002 [P] Criar `tests/participacao/test_entrada_situacao.py` com a seção de testes
  **puros, sem `django_db`** (test-first; DEVE falhar por `ImportError`), sobre as funções
  privadas `_classificar(conclusao, campanhas, participacao)` e `_resolver(formacoes)` de
  `trajetoria.participacao.entrada`, usando instâncias **não gravadas** de `Campanha`,
  `ConclusaoAcademica` e `Participacao` (`Participacao(concluida_em=None)` e
  `Participacao(concluida_em=momento(...))`):
  - **classificação por formação**, um teste por linha: 0 Campanhas → `SEM_PESQUISA`,
    `pendente` falso; 1 Campanha + `None` → `DISPONIVEL_PARA_INICIAR`, `pendente`
    verdadeiro; 1 + rascunho → `DISPONIVEL_PARA_RETOMAR`, `pendente` verdadeiro, com a
    Participação; 1 + concluída → `JA_CONCLUIDA`, `pendente` falso, com a Participação;
    2 e 3 Campanhas → `AMBIGUIDADE_OPERACIONAL`, `pendente` falso, `participacao is None`
    **mesmo quando uma Participação (rascunho ou concluída) é passada** — a ambiguidade
    nunca é resolvida pelo estado de Participação;
  - `Formacao.campanha`: a única com 1; `None` com 0 e com 2+; `campanhas` preserva a
    ordem recebida;
  - **resolução global**, casos explícitos do solicitante: (A) uma pendente →
    `ENTRADA_RESOLVIDA`, `pendentes == (f,)`; (B) concluída + pendente → resolvida a
    pendente; (C) ambígua + pendente → resolvida a pendente e a ambígua presente em
    `formacoes`; (D) duas pendentes (iniciar+iniciar, iniciar+retomar, retomar+retomar) →
    `SELECAO_NECESSARIA`, `pendentes` com as duas na ordem de `formacoes`; (E) todas
    concluídas → `SEM_ENTRADA_PENDENTE`; (F) todas sem Campanha → `SEM_PESQUISA`; (G)
    concluídas + ambíguas, nenhuma pendente → `SEM_ENTRADA_PENDENTE`; e ainda: tupla
    vazia → `SEM_FORMACAO`; todas ambíguas → `SEM_ENTRADA_PENDENTE`; concluída + sem
    pesquisa → `SEM_ENTRADA_PENDENTE`; ambígua + sem pesquisa → `SEM_ENTRADA_PENDENTE`;
    duas pendentes + concluída + ambígua → `SELECAO_NECESSARIA` com só as duas
    pendentes;
  - **exaustividade e exclusividade**: para todas as combinações de 0 a 3 formações sobre
    as cinco situações, `_resolver` devolve exatamente um valor de `ResolucaoDaEntrada`,
    coerente com a tabela do
    [data-model](data-model.md#resolucaodaentrada-enum); formações concluídas e ambíguas
    nunca alteram a contagem de alternativas;
  - `Formacao`, `SituacaoDeEntrada` e `Entrada` são imutáveis (atribuir campo →
    `FrozenInstanceError`).
- [X] T003 Criar `trajetoria/participacao/entrada.py` com docstring de módulo (composição
  de 001, 004, 005 e 006; nada persistido; origem dos dados: contexto institucional lido
  da Conclusão, nunca copiado; nenhuma Resposta criada), `__all__` com os seis tipos e as
  duas funções públicas, os tipos exatamente como em "Convenções" e as funções privadas
  puras:
  - `_classificar(conclusao: ConclusaoAcademica, campanhas: tuple[Campanha, ...],
    participacao: Participacao | None) -> Formacao`, pura (não acessa o banco):
    `len == 0` → `SEM_PESQUISA` (Participação `None`); `len >= 2` →
    `AMBIGUIDADE_OPERACIONAL` com Participação **descartada** (`None`);
    `participacao is None` → `DISPONIVEL_PARA_INICIAR`; `participacao.concluida_em is
    None` → `DISPONIVEL_PARA_RETOMAR`; senão `JA_CONCLUIDA`;
  - `_resolver(formacoes) -> ResolucaoDaEntrada`, nesta ordem: vazio → `SEM_FORMACAO`;
    1 pendente → `ENTRADA_RESOLVIDA`; 2+ → `SELECAO_NECESSARIA`; todas `SEM_PESQUISA` →
    `SEM_PESQUISA`; senão → `SEM_ENTRADA_PENDENTE`. Sem ordenação nova, sem pontuação.

  `situacao_de_entrada` e `entrar` ficam declaradas levantando `NotImplementedError` até
  US1/US3. T002 passa.
- [X] T004 [P] Criar `tests/participacao/construcao_entrada.py` (auxiliares, não testes;
  sem alterar `construcao.py`): `pessoa()` (Pessoa fictícia por ORM, `fonte =
  "teste-entrada"`, `id_externo` sequencial); `formacao(pessoa, *, ano=2022,
  unidade="Serra")` (delegando a `construcao.conclusao(pessoa=…)`);
  `participacao_em_rascunho(campanha, conclusao, agora=NO_PERIODO)` (via
  `iniciar_participacao`); `participacao_concluida(campanha, conclusao, inst,
  agora=NO_PERIODO)` (via `iniciar_participacao` + `construcao.preencher_instrumento` +
  `operacoes.concluir`, como a 006); `linhas()` — contagem e conteúdo de todas as linhas
  de `Pessoa`, `ConclusaoAcademica`, `Campanha`, `Participacao`, `Resposta` e
  `RespostaOpcao`, para comparar antes e depois; `incorporar(fonte, *ids)` reutilizando
  `tests.campanha.construcao.incorporar_cenarios`.

**Checkpoint**: tipos e regras puras prontos e testados sem banco.

---

## Phase 3: User Story 1 — Listar as formações de uma Pessoa (Priority: P1) 🎯 MVP

**Goal**: dada uma Pessoa, todas as suas Conclusões, com contexto da 001 e sem nada
gravado.

**Independent Test**: SIM-P-0003 e SIM-P-0004 incorporadas, sem Campanha: todas as
formações aparecem, com atributos e `None` preservados, ordem estável, banco inalterado.

### Tests for User Story 1 ⚠️

- [X] T005 [US1] Acrescentar a `tests/participacao/test_entrada_situacao.py` (com
  `django_db`), usando `fonte_simulada` e `construcao_entrada.incorporar`:
  - SIM-P-0004 → 3 formações; `formacao.conclusao` é uma `ConclusaoAcademica` com o
    mesmo `pk` da gravada, sem cópia de atributos para outro tipo; ordem igual a
    `list(pessoa.conclusoes.all())` (ordem padrão da 001) e igual em duas chamadas;
  - **todas as Pessoas dos cenários** (SC-002): incorporar todas (`incorporar_cenarios`)
    e, para cada `Pessoa` gravada, o conjunto de `pk` das formações é exatamente o de
    `pessoa.conclusoes`, cada uma uma única vez;
  - **atributos idênticos não fundem formações** (FR-008; caso K da spec): duas
    Conclusões da mesma Pessoa com mesmo curso, unidade e ano (via
    `construcao_entrada.formacao`) → duas formações, `pk` distintos, ambas devolvidas, sem
    rótulo; com Campanha ampla EM COLETA, ambas `DISPONIVEL_PARA_INICIAR` →
    `SELECAO_NECESSARIA` (nenhuma escolhida); Conclusão sem nenhum atributo descritivo
    (`curso`, `unidade`, `nivel`, `modalidade`, `forma_oferta`, `ano_conclusao` todos
    `None`) continua formação válida, com os `None` preservados;
  - SIM-P-0003 → 2 formações com unidades distintas (Serra e Cefor), lidas da Conclusão;
    `Pessoa` sem atributo acadêmico novo;
  - Conclusão com `forma_oferta` `None` → continua `None` na formação;
  - sem Campanhas → todas `SEM_PESQUISA`, resolução `SEM_PESQUISA`;
  - **a consulta não grava nada**: `construcao_entrada.linhas()` idêntico antes e depois
    (também nos testes de US2, US7 e US10 com Participações existentes);
  - `TypeError` para `pessoa` que não é `Pessoa` e para `agora` ingênuo ou `date`;
    `ValueError` para `Pessoa` não gravada.

### Implementation for User Story 1

- [X] T006 [US1] Em `trajetoria/participacao/entrada.py`, implementar
  `situacao_de_entrada(pessoa, *, agora=None)` — passos 1–4 e 7–8 do
  [contrato](contracts/entrada.md#situacao_de_entradapessoa--agoranone---situacaodeentrada):
  `TypeError` para classe errada; `agora = momento_de_referencia(agora)`; `ValueError` se
  `not Pessoa.objects.filter(pk=pessoa.pk).exists()`; Conclusões por
  `ConclusaoAcademica.objects.filter(pessoa=pessoa)` (ordem padrão da 001); por enquanto,
  cada formação com `campanhas=()`; resolução por `_resolver`. Nenhuma escrita.

**Checkpoint**: formações listadas; T005 passa.

---

## Phase 4: User Story 2 — Determinar a situação de cada formação (Priority: P1)

**Goal**: Campanhas aplicáveis pela 004 e Participação do par pela leitura única;
cinco situações.

**Independent Test**: SIM-P-0004 com Campanha só para o mestrado: iniciar → retomar →
concluída; Campanha em preparação/encerrada; limites do período; consultas contadas.

### Tests for User Story 2 ⚠️

- [X] T007 [US2] Acrescentar a `tests/participacao/test_entrada_situacao.py`, com
  `inst` (fixture de `tests/participacao/conftest.py`) e `construcao.campanha_aberta`:
  - SIM-P-0004 + Campanha `ano_minimo=2020, ano_maximo=2020` (só o mestrado, SIM-C-0008)
    → mestrado `DISPONIVEL_PARA_INICIAR` com `campanhas == (campanha,)`, outras
    `SEM_PESQUISA`; com Participação em rascunho → `DISPONIVEL_PARA_RETOMAR` com a
    Participação; concluída (`construcao_entrada.participacao_concluida`) →
    `JA_CONCLUIDA` com a mesma Participação e `concluida_em`;
  - a mesma Campanha em preparação (`campanha_em_preparacao`) e encerrada
    (`op_campanha.encerrar` e `DEPOIS_DO_FIM`) → todas `SEM_PESQUISA`;
  - `ULTIMO_DIA` → aplicável; `DEPOIS_DO_FIM` → `SEM_PESQUISA`;
  - critério de unidade com a Conclusão de `unidade=None` → `SEM_PESQUISA` (pela 004,
    sem regra nova); o resultado não expõe critérios nem pendências da 004;
  - Participação de **outra** Campanha (encerrada) da mesma Conclusão não é informada
    como Participação da formação (só o par da Campanha aplicável);
  - **contagem de consultas**: com N = 3 Conclusões, `django_assert_max_num_queries(3 +
    N)` para `situacao_de_entrada`;
  - garantia de composição (elegibilidade só pela 004): `monkeypatch` de
    `trajetoria.participacao.entrada.campanhas_em_coleta_para` por um dublê que registra
    chamadas e **devolve tuplas controladas** por Conclusão (0, 1 e 2 Campanhas gravadas,
    escolhidas pelo teste independentemente dos critérios delas) → chamado exatamente uma
    vez por Conclusão, com o mesmo `agora` resolvido, e a classificação segue
    exclusivamente o que o dublê devolveu (`SEM_PESQUISA`, `DISPONIVEL_PARA_INICIAR`,
    `AMBIGUIDADE_OPERACIONAL`), sem filtro próprio sobre critérios, período ou estado.

### Implementation for User Story 2

- [X] T008 [US2] Em `trajetoria/participacao/entrada.py`, completar
  `situacao_de_entrada` (passos 5–6 do contrato): para cada Conclusão,
  `campanhas_em_coleta_para(conclusao, agora=agora)`; para as Conclusões com exatamente
  1 Campanha, **uma** consulta `Participacao.objects.filter(conclusao__in=…,
  campanha__in=…)` (omitida se não houver par), indexada por `(campanha_id,
  conclusao_id)`; formações ambíguas e sem pesquisa **não** entram nessa consulta;
  `Formacao` montada com `_classificar`. Nenhum filtro da 004 copiado; nenhuma
  ordenação nova.

**Checkpoint**: cinco situações derivadas no banco; T007 passa.

---

## Phase 5: User Story 3 — Resolver automaticamente a única entrada pendente (Priority: P1)

**Goal**: `entrar(pessoa)` sem formação informada procede quando há exatamente uma
pendente, mesmo com concluídas, ambíguas ou sem pesquisa ao lado.

**Independent Test**: SIM-P-0001 entra sem informar formação; SIM-P-0003 com A concluída
e B pendente entra direto em B.

### Tests for User Story 3 ⚠️

- [X] T009 [P] [US3] Criar `tests/participacao/test_entrada_entrar.py` (`django_db`)
  com:
  - **caso S-A**: 1 formação sem Participação → `situacao.resolucao is
    ENTRADA_RESOLVIDA`; `entrar(pessoa, agora=NO_PERIODO)` → `participacao` do par
    (Campanha aplicável, Conclusão), `criada` verdadeiro;
  - SIM-P-0004 com uma única formação aplicável → resolvida essa; as outras `SEM_PESQUISA`
    em `situacao.formacoes`;
  - **caso S-D**: A concluída + B rascunho, mesma Campanha → `ENTRADA_RESOLVIDA`,
    `pendentes == (B,)`; `entrar(pessoa)` devolve o rascunho de B, `criada` falso;
    A presente como `JA_CONCLUIDA`; Participação de A inalterada;
  - **caso S-E**: A concluída + B sem Participação → `entrar(pessoa)` cria a de B
    (`criada`), nenhuma nova para A;
  - **ambígua + pendente**: A com duas Campanhas aplicáveis (critérios que só A atende na
    segunda), B com uma → `ENTRADA_RESOLVIDA` para B; A presente como
    `AMBIGUIDADE_OPERACIONAL` com as duas Campanhas; `entrar(pessoa)` cria/retoma só a de
    B; **nenhuma** Participação nova em qualquer Campanha de A;
  - entrar informando a mesma formação resolvida → mesmo resultado que sem informar;
  - `entrar` chama `iniciar_participacao` (dublê via `monkeypatch` em
    `trajetoria.participacao.entrada.iniciar_participacao` registrando chamadas) com
    `(f.campanha, f.conclusao, agora=…)`, e nunca cria `Participacao` por outro caminho.

### Implementation for User Story 3

- [X] T010 [US3] Em `trajetoria/participacao/entrada.py`, implementar
  `entrar(pessoa, formacao=None, *, agora=None)` — passos 2, 3, 7 e 8 do
  [contrato](contracts/entrada.md#entrarpessoa-formacaonone--agoranone---entrada):
  `agora` resolvido uma vez; `situacao = situacao_de_entrada(pessoa, agora=agora)`
  **sempre reavaliada** (sem token, snapshot ou reaproveitamento de consulta anterior);
  sem `formacao`: resolução ≠ `ENTRADA_RESOLVIDA` → `Entrada(situacao, None, False)`;
  senão `f = situacao.pendentes[0]`; pendente → `inicio = iniciar_participacao(
  f.campanha, f.conclusao, agora=agora)`; `Entrada(situacao, inicio.participacao,
  inicio.situacao is SituacaoInicio.CRIADA)`. `ParticipacaoRejeitada` propagada sem
  conversão.

**Checkpoint**: resolução automática ponta a ponta; T009 passa.

---

## Phase 6: User Story 4 — Exigir seleção quando houver múltiplas entradas pendentes (Priority: P1)

**Goal**: 2+ pendentes → `SELECAO_NECESSARIA`; sem formação nada é criado; com formação
informada, entra nela.

**Independent Test**: SIM-P-0003 com Campanha ampla: seleção necessária, entrada sem
formação não cria nada, cada formação informada gera sua Participação.

### Tests for User Story 4 ⚠️

- [X] T011 [US4] Acrescentar a `tests/participacao/test_entrada_entrar.py`:
  - **caso S-F**: A e B pendentes nas combinações iniciar+iniciar, iniciar+retomar,
    retomar+retomar → `SELECAO_NECESSARIA`, `pendentes == (A, B)` na ordem da 001;
    `entrar(pessoa)` → `participacao is None`, `construcao_entrada.linhas()` inalterado;
  - entrar informando A e depois B → duas Participações independentes, uma por par; nada
    compartilhado;
  - duas pendentes em Campanhas diferentes (critério de unidade distinto) → ainda
    `SELECAO_NECESSARIA`; cada formação leva à sua Campanha;
  - duas pendentes + uma concluída → `pendentes` com só as duas;
  - nenhuma ordenação nova: invertendo `ano_conclusao` das Conclusões, a ordem de
    `pendentes` acompanha a ordem padrão da 001, sem "mais recente primeiro" por regra
    própria.

### Implementation for User Story 4

- [X] T012 [US4] Em `trajetoria/participacao/entrada.py`, completar `entrar` com o
  passo 4 (só a parte positiva): com `formacao` informada (`TypeError` se não é
  `ConclusaoAcademica`), `f` = formação de `situacao.formacoes` com o mesmo `pk`; se
  pendente, segue para o passo 7. A rejeição de formação ausente vem em T030.

**Checkpoint**: seleção explícita funcionando; T011 passa.

---

## Phase 7: User Story 5 — Iniciar Participação para a formação selecionada (Priority: P1)

**Goal**: Participação criada pela 005, sem Respostas, pronta para a 006.

**Independent Test**: entrar numa formação `DISPONIVEL_PARA_INICIAR`; Participação nova,
sem Respostas, jornada da 006 na primeira Seção.

### Tests for User Story 5 ⚠️

- [X] T013 [US5] Acrescentar a `tests/participacao/test_entrada_entrar.py`:
  - Participação criada com `iniciada_em == agora` (momento da 005), `concluida_em is
    None`, `campanha`/`conclusao` do par;
  - **caso S-L**: depois da consulta e da entrada, `Resposta.objects.filter(participacao=…)`
    vazio e nenhuma `Resposta` nova no banco, para nenhuma Pergunta da Versão (inclusive
    a Pergunta `campus` do instrumento de teste, análoga a Q11, cuja resposta seria a
    unidade da Conclusão); os campos concretos de `Participacao` continuam exatamente
    {`id`, `campanha`, `conclusao`, `iniciada_em`, `concluida_em`};
  - `situacao_da_jornada(entrada.participacao, agora=…)` (006) começa na primeira Seção
    da Versão aplicada, sem Seção pulada;
  - entrada repetida 3 vezes → exatamente 1 Participação para o par;
  - entradas simultâneas (duas threads com barreira, `django_db(transaction=True)`) → 1
    Participação; **manter só se estável em 10 execuções**, como na 006; senão remover e
    registrar que a garantia é a da 005 (`test_participacao_concorrencia.py`).

**Checkpoint**: início pela 005 verificado (sem implementação nova esperada).

---

## Phase 8: User Story 6 — Retomar Participação existente (Priority: P1)

**Goal**: rascunho devolvido sem duplicar; Participação criada em outra requisição
respeitada.

**Independent Test**: iniciar, responder, entrar de novo: mesma Participação, mesmas
Respostas.

### Tests for User Story 6 ⚠️

- [X] T014 [US6] Acrescentar a `tests/participacao/test_entrada_entrar.py`:
  - **caso S-B**: 1 formação em rascunho com uma Resposta → `ENTRADA_RESOLVIDA`;
    `entrar(pessoa)` → mesma Participação, `criada` falso,
    `construcao.retrato(participacao)` idêntico antes e depois;
  - **resultado muda entre consulta e entrada (Participação criada em outra requisição)**:
    `s = situacao_de_entrada(...)` mostra `DISPONIVEL_PARA_INICIAR`; outra chamada a
    `iniciar_participacao` cria a Participação; `entrar(pessoa)` devolve **essa** mesma
    Participação, `criada` falso, e não cria outra;
  - consulta informa `DISPONIVEL_PARA_RETOMAR` com a Participação, sem gravar.

**Checkpoint**: retomada sem duplicação.

---

## Phase 9: User Story 7 — Informar que a Participação já foi concluída (Priority: P2)

**Goal**: concluída é informação, não alternativa; nunca reaberta.

**Independent Test**: concluir pela 006; consulta `SEM_ENTRADA_PENDENTE`; entrada
informando a formação devolve a concluída inalterada.

### Tests for User Story 7 ⚠️

- [X] T015 [US7] Acrescentar a `tests/participacao/test_entrada_entrar.py`:
  - **caso S-C**: 1 formação concluída (Campanha ainda EM COLETA) →
    `SEM_ENTRADA_PENDENTE`, formação `JA_CONCLUIDA` com a Participação;
    `entrar(pessoa)` → `participacao is None`, nada criado;
  - informando a formação → `entrada.participacao` é a concluída, `criada` falso,
    `concluida_em` igual, `construcao.retrato` idêntico; `iniciar_participacao` **não** é
    chamada (dublê que falha se chamado);
  - **todas concluídas** (SIM-P-0003, duas formações concluídas) → `SEM_ENTRADA_PENDENTE`,
    nenhuma seleção (`pendentes == ()`), ambas `JA_CONCLUIDA`;
  - **Participação concluída nunca é reaberta**: após várias entradas (com e sem
    formação informada), `concluida_em` inalterado e `admite_escrita` (005/006) falso;
    nenhuma operação de reabertura existe em `entrada.__all__`;
  - **concluída entre a avaliação e o início**: `monkeypatch` de
    `trajetoria.participacao.entrada.situacao_de_entrada` devolvendo a situação anterior
    (formação `DISPONIVEL_PARA_RETOMAR`) enquanto o banco já tem a Participação
    concluída → `entrar` devolve a Participação com `concluida_em` preenchido, `criada`
    falso, nada alterado.

### Implementation for User Story 7

- [X] T016 [US7] Em `trajetoria/participacao/entrada.py`, completar `entrar` com o passo
  6: formação informada `JA_CONCLUIDA` → `Entrada(situacao, f.participacao, False)` sem
  chamar a 005.

**Checkpoint**: concluídas informadas, nunca contadas, nunca reabertas.

---

## Phase 10: User Story 8 — Tratar Pessoa sem Conclusão Acadêmica disponível (Priority: P2)

**Goal**: `SEM_FORMACAO` distinto de erro de uso, de "sem pesquisa" e de inelegível.

**Independent Test**: Pessoa gravada sem Conclusões → `SEM_FORMACAO`; não gravada →
`ValueError`.

### Tests for User Story 8 ⚠️

- [X] T017 [US8] Acrescentar a `tests/participacao/test_entrada_entrar.py`:
  - **caso S-H**: `construcao_entrada.pessoa()` sem Conclusões → `SEM_FORMACAO`,
    `formacoes == ()`; `entrar(pessoa)` → `participacao is None`, nada criado;
  - `Pessoa` não gravada e Pessoa removida → `ValueError` na consulta e na entrada (não
    `SEM_FORMACAO`);
  - Pessoa com Conclusão inelegível em Campanha EM COLETA → `SEM_PESQUISA`, não
    `SEM_FORMACAO`.

**Checkpoint**: situações de "nada a fazer" distinguíveis.

---

## Phase 11: User Story 9 — Tratar Pessoa com formações, mas nenhuma pesquisa disponível (Priority: P2)

**Goal**: `SEM_PESQUISA` normal; encerramento entre consulta e entrada respeitado.

**Independent Test**: SIM-P-0002 sem Campanha EM COLETA: `SEM_PESQUISA`, nada criado.

### Tests for User Story 9 ⚠️

- [X] T018 [US9] Acrescentar a `tests/participacao/test_entrada_entrar.py`:
  - **caso S-G**: SIM-P-0002 (duas formações) sem Campanha → `SEM_PESQUISA`, ambas
    `SEM_PESQUISA`; com Campanhas que não as elegem → igual; `entrar` com e sem formação
    → `participacao is None`;
  - rascunho numa Campanha já ENCERRADA → formação `SEM_PESQUISA`; a Participação antiga
    continua existindo e não é devolvida pela entrada;
  - **resultado muda entre consulta e entrada (encerramento)**: consulta em `NO_PERIODO`
    mostra `ENTRADA_RESOLVIDA`; `op_campanha.encerrar(campanha, agora=…)`; `entrar` em
    momento posterior → `participacao is None`, nenhuma Participação criada.

**Checkpoint**: ausência de pesquisa tratada como resultado normal.

---

## Phase 12: User Story 10 — Múltiplas Campanhas aplicáveis à mesma formação como ambiguidade (Priority: P2)

**Goal**: ambiguidade local; nenhuma Campanha escolhida; nada criado nem retomado pela
formação ambígua.

**Independent Test**: duas Campanhas sobrepostas para SIM-P-0001: formação ambígua com as
duas, nada criado.

### Tests for User Story 10 ⚠️

- [X] T019 [US10] Acrescentar a `tests/participacao/test_entrada_entrar.py`:
  - **caso S-I**: duas Campanhas de população ampla com períodos sobrepostos →
    formação `AMBIGUIDADE_OPERACIONAL` com `campanhas` nas duas, na ordem `(inicio, id)`
    da 004; `participacao is None`; resolução `SEM_ENTRADA_PENDENTE`; `entrar` com e sem
    formação → `participacao is None`, nada criado;
  - **Campanha sobreposta nunca é escolhida automaticamente**, com Participação existente
    numa das Campanhas em cada estado — rascunho e concluída — e sem Participação: sempre
    `AMBIGUIDADE_OPERACIONAL`, `participacao is None`, `entrar` informando a formação não
    devolve nem cria Participação; a existente permanece idêntica (`retrato`); variar a
    ordem de criação e de `inicio` das Campanhas não muda o resultado;
  - **todas ambíguas** (duas formações, cada uma com duas Campanhas) →
    `SEM_ENTRADA_PENDENTE`, `pendentes == ()`;
  - ambígua + concluída → `SEM_ENTRADA_PENDENTE`;
  - ambígua + duas pendentes → `SELECAO_NECESSARIA` entre as duas pendentes; informar a
    ambígua → nada criado;
  - **resultado muda entre consulta e entrada (nova Campanha)**: consulta mostra
    `DISPONIVEL_PARA_INICIAR`; abre-se segunda Campanha aplicável; `entrar` informando a
    formação → `participacao is None`, nada criado, formação agora ambígua em
    `entrada.situacao`.

### Implementation for User Story 10

- [X] T020 [US10] Em `trajetoria/participacao/entrada.py`, completar `entrar` com o passo
  5: formação informada `SEM_PESQUISA` ou `AMBIGUIDADE_OPERACIONAL` →
  `Entrada(situacao, None, False)`, sem chamar a 005.

**Checkpoint**: ambiguidade local e nunca desempatada.

---

## Phase 13: User Story 11 — Preservar proveniência e rejeitar associações inconsistentes (Priority: P3)

**Goal**: formação de outra Pessoa rejeitada antes da 005; contexto sem cópia;
longitudinalidade.

**Independent Test**: Pessoa X informando Conclusão de Y → `FormacaoDeOutraPessoa`, nada
criado.

### Tests for User Story 11 ⚠️

- [X] T021 [US11] Acrescentar a `tests/participacao/test_entrada_entrar.py`:
  - **caso S-J**: homônimas SIM-P-0010 e SIM-P-0011; SIM-P-0010 informando SIM-C-0013 →
    `FormacaoDeOutraPessoa`; `iniciar_participacao` **não** chamada (dublê que falha);
    `str(erro)` sem curso, unidade, nome, `id_externo` nem `pk` da Conclusão ou da
    Pessoa alheia; nada criado — mesmo com a Conclusão alheia elegível numa Campanha EM
    COLETA;
  - Conclusão inexistente → a mesma `FormacaoDeOutraPessoa`, com a mesma mensagem da
    alheia; `formacao` que não é `ConclusaoAcademica` → `TypeError`;
  - entrada aceita: `participacao.conclusao_id` é a formação e `participacao.campanha_id`
    a Campanha aplicável; `participacao.pessoa` é a Pessoa (via Conclusão — 005 FR-004);
  - **caso S-K** (longitudinal): Participação concluída numa Campanha 2027 encerrada; nova
    Campanha 2030 aberta e aplicável → `DISPONIVEL_PARA_INICIAR`; `entrar` cria nova
    Participação para 2030; a de 2027 com mesmos `iniciada_em`, `concluida_em` e Respostas
    (`retrato`).

### Implementation for User Story 11

- [X] T022 [US11] Em `trajetoria/participacao/entrada.py`, completar o passo 4 de
  `entrar`: formação informada ausente de `situacao.formacoes` → `FormacaoDeOutraPessoa`
  (mensagem fixa, sem dados), seja de outra Pessoa, seja inexistente; sempre **antes** de
  qualquer chamada à 005. *(Ajustado pelo code review: a versão inicial distinguia
  inexistente com `ValueError`, o que revelava a existência de UUIDs.)*

**Checkpoint**: todas as histórias entregues.

---

## Phase 14: Aceitação e fronteiras

- [X] T023 Criar `tests/participacao/test_entrada_aceitacao.py` (`django_db` onde
  preciso):
  - **as 12 perguntas de sucesso do solicitante** (spec, "Cobertura"), uma função por
    pergunta, ponta a ponta;
  - **zero modelos e migrações**: `apps.get_app_config("participacao").get_models()` ==
    {`Participacao`, `Resposta`, `RespostaOpcao`}; nenhum modelo em nenhum app com nome
    proibido (lista "Limites"); `makemigrations --check` sem mudanças
    (`call_command("makemigrations", "--check", "--dry-run")`); arquivos de migração da
    `participacao` exatamente `0001_initial.py` e `0002_participacao_concluida_em.py`;
  - **escrita protegida por comportamento** (sem inspeção do código-fonte, sem AST, sem
    busca de palavras ou chamadas no arquivo):
    1. *consulta sem escrita*: para cada montagem dos casos A–L,
       `construcao_entrada.linhas()` idêntico antes e depois de `situacao_de_entrada`;
    2. *nenhum caminho próprio de persistência*: com
       `trajetoria.participacao.entrada.iniciar_participacao` substituída (`monkeypatch`)
       por um dublê que **não grava** e devolve `Inicio(<Participação já existente de
       outro par>, JA_EXISTENTE)`, `entrar` numa formação `DISPONIVEL_PARA_INICIAR` não
       acrescenta nenhuma linha de `Participacao` (contagem igual) e devolve exatamente a
       Participação do dublê — logo, `entrar` não persiste por conta própria;
    3. *delegação determinística*: com um dublê que registra chamadas e delega à função
       real, `entrar` em `DISPONIVEL_PARA_INICIAR` e em `DISPONIVEL_PARA_RETOMAR` chama
       `iniciar_participacao` exatamente uma vez com `(f.campanha, f.conclusao,
       agora=<o mesmo agora>)`; a única linha nova de `Participacao` é a devolvida pela
       005;
    4. *nada a iniciar, nada chamado*: com um dublê que falha se chamado, `entrar` em
       `SEM_FORMACAO`, `SEM_PESQUISA`, `SEM_ENTRADA_PENDENTE`, `SELECAO_NECESSARIA` (sem
       formação), formação `SEM_PESQUISA`, `AMBIGUIDADE_OPERACIONAL`, `JA_CONCLUIDA` e de
       outra Pessoa não chama a 005, e `linhas()` fica idêntico;
  - **YAGNI das estruturas**: `entrada.__all__` é exatamente {`SituacaoDaFormacao`,
    `Formacao`, `ResolucaoDaEntrada`, `SituacaoDeEntrada`, `Entrada`,
    `FormacaoDeOutraPessoa`, `situacao_de_entrada`, `entrar`}; os campos das dataclasses
    são exatamente os da "Convenção"; os valores dos dois enums são exatamente os cinco
    de cada; nenhum nome público contém `reabr`, `sessao`, `selecao`, `token`, `login`,
    `usuario`, `prioridade`, `ranking`, `campanha_escolhida`;
  - `operacoes.__all__` e `consultas.__all__` da `participacao` inalterados (mesmos
    conjuntos que os testes da 005/006 já fixam);
  - nenhum arquivo `urls.py`, `views.py`, `admin.py` ou `management/` novo em
    `trajetoria/participacao/`.

**Checkpoint**: aceitação e fronteiras verdes.

---

## Phase 15: Polish & Cross-Cutting Concerns

- [X] T024 [P] Acrescentar ao `README.md` a linha "Contextualização da formação e entrada
  na pesquisa: [quickstart da Feature 007](specs/007-contextualizacao-formacao-entrada/quickstart.md)".
- [X] T025 [P] Revisar `trajetoria/participacao/entrada.py`: importa só o permitido em
  [Dependências permitidas](contracts/entrada.md#dependências-permitidas) (regra de desenho
  conferida aqui, sem teste de inspeção do código-fonte); docstrings citando os FRs e
  as decisões (ambiguidade local; concluída não é alternativa; reavaliação sem snapshot);
  nenhum comentário prometendo autenticação, interface ou otimização futura; `ruff check`
  limpo.
- [X] T026 Rodar o [quickstart](quickstart.md) inteiro: `uv run pytest` (suíte completa,
  001–006 sem nenhum teste alterado), `uv run pytest tests/participacao -k entrada`,
  `uv run ruff check .`, `uv run python manage.py makemigrations --check --dry-run`;
  conferir com `git diff --stat main -- trajetoria/ tests/ config/` que só existem
  `trajetoria/participacao/entrada.py` e os quatro arquivos novos de
  `tests/participacao/` (`test_entrada_situacao.py`, `test_entrada_entrar.py`,
  `test_entrada_aceitacao.py`, `construcao_entrada.py`); registrar no
  [plan.md](plan.md) uma "Revisão pós-implementação" (número de testes, contagem de
  consultas observada, se o teste com threads foi mantido, Complexity Tracking ainda
  vazio, DPs abertas).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (T001)** → **Foundational (T002–T004)** → histórias → **Aceitação (T023)** →
  **Polish (T024–T026)**.
- Na Foundational: T002 e T004 em paralelo; T003 depois de T002.

### User Story Dependencies

- **US1** (T005–T006): Foundational.
- **US2** (T007–T008): US1.
- **US3** (T009–T010): US2.
- **US4** (T011–T012): US3.
- **US5** (T013), **US6** (T014): US3.
- **US7** (T015–T016): US4 (formação informada).
- **US8** (T017), **US9** (T018): US3.
- **US10** (T019–T020): US4.
- **US11** (T021–T022): US4.
- **Aceitação** (T023): US1–US11.

### Within Each User Story

- Testes primeiro; DEVEM falhar quando trazem comportamento novo (US1, US2, US3, US4, US7,
  US10, US11).
- `trajetoria/participacao/entrada.py`, `test_entrada_situacao.py` e
  `test_entrada_entrar.py` são editados em sequência (um arquivo por vez).

### Parallel Opportunities

- Foundational: T002 e T004.
- T009 cria `test_entrada_entrar.py` e pode ser escrito em paralelo com T008 (arquivos
  distintos), antes de T010.
- Polish: T024 e T025.
- Fora disso, a maior parte é sequencial por compartilhar `entrada.py` e
  `test_entrada_entrar.py` — custo aceitável para uma feature de um módulo.

---

## Parallel Example: Foundational

```bash
Task: "T002 Testes puros de _classificar e _resolver em tests/participacao/test_entrada_situacao.py"
Task: "T004 Auxiliares em tests/participacao/construcao_entrada.py"
```

## Parallel Example: User Story 3

```bash
Task: "T008 Campanhas aplicáveis e Participações em trajetoria/participacao/entrada.py"
Task: "T009 Testes de resolução automática em tests/participacao/test_entrada_entrar.py"
```

---

## Implementation Strategy

### MVP First

1. Setup + Foundational (T001–T004).
2. US1 → US3 (T005–T010): formações, situação por formação, resolução automática e
   início/retomada pela 005.
3. **STOP and VALIDATE**: `uv run pytest tests/participacao -k entrada`.

### Incremental Delivery

4. US4 (seleção) → US5/US6 (início e retomada) → US7 (concluídas) → US8/US9 (nada a
   fazer) → US10 (ambiguidade) → US11 (formação alheia, longitudinalidade).
5. Aceitação (T023) e Polish (T024–T026).

---

## Decisões Pendentes preservadas

Nenhuma task resolve DP-701, DP-702, DP-703 nem as herdadas 004/DP-404, 004/DP-406,
005/DP-501, 003/DP-307, 005/DP-507, 005/DP-508, 006/DP-603, 001/DP-003, 001/DP-005,
001/DP-006, 004/DP-409, 001/DP-009, 005/DP-504. Em particular: nenhuma prioridade entre
Campanhas, nenhum rótulo de formação, nenhuma métrica de Participação sem Respostas,
nenhuma alteração de Q10–Q19, nenhum mecanismo de identidade.

## Notes

- **Rótulos de casos**: "S-A" a "S-L" são os casos de teste do solicitante (plan,
  "Estratégia de testes"; quickstart). "A" a "O" são os "Casos de referência" da spec,
  medidos pelo SC-001. Correspondência:

  | Caso da spec | Conteúdo | Tasks |
  |--------------|----------|-------|
  | A | 1 Conclusão, disponível para iniciar | T009 (S-A) |
  | B | 3 Conclusões, só 1 com pesquisa aplicável | T009 (SIM-P-0004) |
  | C | 2 Conclusões com entrada pendente | T011 (S-F) |
  | D | Pessoa sem Conclusões | T017 (S-H) |
  | E | Conclusões, nenhuma Campanha aplicável | T018 (S-G) |
  | F | 1 Conclusão com 2 Campanhas aplicáveis | T019 (S-I) |
  | G | disponível para iniciar → iniciada | T009, T013 |
  | H | disponível para retomar → mesma Participação | T014 (S-B) |
  | I | já concluída → sem entrada pendente | T015 (S-C) |
  | J | mesma Conclusão em Campanha futura | T021 (S-K) |
  | K | atributos incompletos/idênticos | T005 |
  | L | Conclusões em unidades diferentes | T005 (SIM-P-0003) |
  | M | A concluída + B retomar | T009 (S-D) |
  | N | A concluída + B iniciar | T009 (S-E) |
  | O | A ambígua + B pendente | T009, T019 |

- **Contagem**: 26 tasks; 13 de teste (T002, T005, T007, T009, T011, T013, T014, T015,
  T017, T018, T019, T021, T023); 9 de implementação em `entrada.py` (T003, T006, T008,
  T010, T012, T016, T020, T022, T025); 1 de auxiliares de teste (T004); 3 de
  setup/documentação/validação (T001, T024, T026).
- Complexity Tracking continua vazio.
- Commits por história, com o trailer de coautoria do projeto.
- **Code review (2026-10-01)**: oito achados; sete corrigidos — `agora` original repassado
  à 005 (teste de regressão com Campanha encerrada entre a avaliação e o início);
  rejeição única para formação alheia ou inexistente; `test_12` sem a substring "gen";
  `test_10` verificando apps, middleware, backends e rotas do projeto inteiro; remoção da
  repetição dos `__all__` da 005/006; `_exigir` reutilizado da 005; condição "uma
  Campanha" sem repetição. Um mantido por desenho: a releitura da Participação pela 005
  em `entrar` (reutilização deliberada de `iniciar_participacao`, R7).

