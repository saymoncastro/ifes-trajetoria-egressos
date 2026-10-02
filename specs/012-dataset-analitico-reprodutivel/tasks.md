---

description: "Tasks da Feature 012 — Dataset analítico institucional reprodutível"
---

# Tasks: Dataset analítico institucional reprodutível

**Input**: design documents de `specs/012-dataset-analitico-reprodutivel/`.

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/operacoes.md](contracts/operacoes.md),
[contracts/consultas.md](contracts/consultas.md), [quickstart.md](quickstart.md).

**Stack** ([ADR 0001](../../docs/adr/0001-stack-inicial.md)): Python 3.13, Django 5.2
LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff. **Nenhuma dependência nova.**

**Persistência**: **2 modelos, 1 migration aditiva** (`analitico/0001_initial`).
**0 views, 0 urls, 0 templates, 0 management commands, 0 jobs.** Nenhuma alteração em
`trajetoria/` fora de `trajetoria/analitico/`, exceto uma linha em `config/settings.py`.

**Tests**: obrigatórios e escritos **antes** da implementação correspondente
(test-first). A feature toca preservação histórica, elegibilidade, longitudinalidade,
associação de respostas e migração (Princípio XXVI). Teste de comportamento novo DEVE
falhar primeiro. Teste que só confirma comportamento entregue por história anterior pode
passar de imediato; se falhar, a correção vai no módulo indicado.

**Organization**: Setup, Foundational, uma fase por história da spec (US1–US13, na ordem
de prioridade) e Polish. Tarefas no mesmo arquivo nunca têm [P].
`trajetoria/analitico/operacoes.py`, `consultas.py` e cada arquivo de teste são editados
**em sequência**, história após história.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US13).

## Convenções para todas as tarefas

**Escopo**

- Só `capturar_snapshot` grava. Nenhuma operação edita, corrige, recalcula, completa ou
  remove snapshot ou registro (spec FR-050). Nenhuma operação toca Campanha, Conclusão,
  Pessoa, Participação, Resposta, Versão, Pesquisa ou vínculo (spec FR-002).
- Sem UI, view, rota, template, admin, endpoint, management command, regra de governança
  (`pode_capturar_snapshot` **não** existe), job, cache, visão materializada, lock,
  nível de isolamento alterado, SQL manual, query builder, serializador, schema tabular,
  nomes de coluna, CSV ou GeN.
- **Não altere** `trajetoria/campanha/`, `participacao/`, `academico/`, `instrumento/`,
  `fonte_academica/`, `governanca/`, `acompanhamento/`, `demonstracao/`, `interface/`,
  `editor/` nem o cenário de demonstração.

**Elegibilidade e universo** (research R7)

- Elegibilidade **só** por `trajetoria.campanha.consultas.populacao_no_momento(campanha)`.
  Não tornar `_filtro` público, não ler critérios da Campanha, não chamar `avaliar` em
  laço na produção (`avaliar` só aparece em teste de equivalência).
- Universo = (1) `populacao_no_momento(campanha).values_list("pk", *CAMPOS_DE_CONTEXTO)`
  → `elegivel_no_snapshot=True`; (2)
  `ConclusaoAcademica.objects.filter(pk__in=Participacao.objects.filter(campanha=campanha).values("conclusao_id")).values_list("pk", *CAMPOS_DE_CONTEXTO)`
  → para cada `pk` ausente de (1), `elegivel_no_snapshot=False`; união deduplicada por
  `pk` da Conclusão, (1) prevalece. Nunca por Pessoa.
- `CAMPOS_DE_CONTEXTO` vem de `trajetoria.fonte_academica.contrato` (curso, unidade,
  nivel, modalidade, forma_oferta, ano_conclusao, data_conclusao). Valores copiados
  **como lidos**: sem `strip`, normalização, preenchimento, correção ou consulta à fonte.

**Atomicidade e momento** (research R8)

- Tudo em `transaction.atomic()`: snapshot e **todos** os registros, ou nada. Sem estado
  "processando"/"falhou". Sem REPEATABLE READ, SERIALIZABLE, `select_for_update` na
  Campanha, advisory lock.
- `capturado_em = momento_de_referencia(None)`, lido **uma vez**, dentro da transação.
  `capturar_snapshot` **não** tem parâmetro de momento. `capturado_em` é o momento técnico
  da captura, não instante de leitura isolada.

**Leitura** (research R11, R12)

- Toda leitura recebe o snapshot explicitamente. **Nenhuma** função "atual", "vigente",
  "último", "mais recente" (spec FR-061, FR-064).
- Reprodução (indicadores, recortes, dataset) **nunca** lê tabela de `academico`
  (Conclusão, Pessoa). Indicadores e recortes também não leem Resposta.
- Objetos de valor `@dataclass(frozen=True)`, pequenos; nunca expõem instâncias de
  `ConclusaoAcademica`, `Pessoa`, `Participacao` ou `RegistroDoSnapshot`.
- Linguagem de docstrings: "elegíveis no snapshot", nunca "elegíveis atuais".

**Dados de teste** (research R15)

- Somente dados fictícios. Conclusões por ORM (como nos testes da 004/005/011); Campanhas,
  Participações e Respostas **pelas operações** da 004/005/006.
- A captura usa o relógio real: as Campanhas de teste têm coleta **no passado** (relativo a
  `timezone.localdate()`), e as operações de coleta recebem `agora=` dentro desse passado.
  Não usar as constantes de 2027 de `tests/participacao/construcao.py` para coleta de
  Campanha a capturar.
- Alteração acadêmica posterior (casos G, J, K): **somente** por
  `ConclusaoAcademica.objects.filter(...).update(...)` dentro do teste, com comentário
  "simula 001/DP-005". Nenhuma operação de correção é criada.

**Privacidade**: mensagens de `SnapshotRecusado` e `CapturaInconsistente` citam motivo,
`id` da Campanha/snapshot e contagens; nunca valores acadêmicos nem Respostas. Nenhum log
novo.

---

## Phase 1: Setup

**Purpose**: app vazio registrado e auxiliares de teste.

- [X] T001 Criar o app `trajetoria/analitico/` com `__init__.py` e `apps.py`
  (`AnaliticoConfig`, `name = "trajetoria.analitico"`, `default_auto_field` igual ao dos
  outros apps) e `migrations/__init__.py`, sem `views.py`, `urls.py`, `admin.py`,
  `templates/` nem `management/`; docstring do pacote em `trajetoria/analitico/__init__.py`
  descrevendo o app como snapshot analítico imutável da Feature 012 (spec), sem interface.
- [X] T002 Acrescentar `"trajetoria.analitico"` ao fim de `INSTALLED_APPS` em
  `config/settings.py`, sem outra alteração.
- [X] T003 [P] Criar `tests/analitico/__init__.py` e `tests/analitico/construcao.py`
  (auxiliares, não testes), com:
  - `conclusao(*, unidade=None, curso=None, nivel=None, modalidade=None,
    forma_oferta=None, ano=None, data=None, pessoa=None)`: Pessoa e Conclusão fictícias por
    ORM (`fonte="teste-analitico"`, `id_externo` sequencial), como em
    `tests/acompanhamento/construcao.py`, com `data_conclusao=data` (com data, `ano` DEVE
    ser o ano da data, pela restrição da 001);
  - `NA_COLETA`: `momento_em(hoje() − 20 dias)` (de `tests.acompanhamento.construcao`);
  - `campanha_encerrada_por_periodo(versao, **criterios)`: período de hoje−40 a hoje−5,
    `abrir(agora=momento_em(hoje−30))`;
  - `campanha_encerrada_explicitamente(versao, **criterios)`: período de hoje−40 a
    hoje+30, `abrir(agora=momento_em(hoje−30))`, depois `encerrar(agora=momento_em(hoje−10))`
    — chamado **depois** de criar as Participações, por isso separado em
    `campanha_aberta_no_passado(...)` + `encerrar_no_passado(campanha)`;
  - `campanha_em_coleta(versao, **criterios)` e `campanha_nunca_aberta(versao, *, expirada)`
    reutilizando `tests.acompanhamento.construcao.campanha` (`em_coleta`, `em_preparacao`,
    `expirada_sem_abertura`);
  - `iniciada(campanha, conclusao)`, `concluida(campanha, conclusao, inst)`,
    `concluida_por_recusa(campanha, conclusao, inst)` e
    `rascunho_com_resposta_fora_do_percurso(campanha, conclusao, inst)` (responde "Sim" à
    Pergunta `inst.unica`, responde o "Comentário" da Seção 2, depois troca `inst.unica`
    para "Não", que finaliza na Seção 1: o Comentário fica fora do percurso), todos com
    `agora=NA_COLETA`, pelas operações da 005/006 e `tests.participacao.construcao`
    (`instrumento()`, `preencher_instrumento`);
  - `simular_correcao(conclusao, **atributos)`: `ConclusaoAcademica.objects.filter(pk=…)
    .update(**atributos)` com docstring "simula 001/DP-005; nenhuma operação de produção";
  - `retrato(snapshot)`: `{conclusao_id: (elegivel_no_snapshot, *contexto)}` lido de
    `RegistroDoSnapshot`, para comparar antes e depois.
- [X] T004 [P] Criar `tests/analitico/conftest.py` com o cenário de referência fictício
  (spec, "Dados de referência"): Conclusões em Serra, Vitória, Cefor e sem unidade; curso
  "Técnico em Informática" na Serra **e** em Vitória; instrumento de teste publicado
  (`tests.participacao.construcao.instrumento()`); fixtures `campanha_e` (critério de
  unidades {Serra, Vitória}, com elegíveis sem Participação, uma concluída, uma concluída
  por recusa e um rascunho com Resposta fora do percurso, encerrada), `campanha_v`
  (encerrada, sem Participações), `campanha_c` (em coleta), `campanha_p` (nunca aberta),
  `campanha_x` (nunca aberta, expirada). Imports de `trajetoria.analitico.*` **dentro** das
  funções, para o módulo importar antes de os modelos existirem.

**Checkpoint**: `uv run pytest` verde (nenhum teste novo ainda);
`uv run python manage.py check` sem erro.

---

## Phase 2: Foundational

**Purpose**: os dois modelos, a migration e o vocabulário de recusa. Bloqueia todas as
histórias.

### Testes primeiro

- [X] T005 [P] Escrever `tests/analitico/test_analitico_modelo.py`:
  - campos exatos de `SnapshotAnalitico`: `{"id", "campanha", "capturado_em"}`;
  - campos exatos de `RegistroDoSnapshot`: `{"id", "snapshot", "conclusao",
    "elegivel_no_snapshot", *CAMPOS_DE_CONTEXTO}`;
  - os campos de contexto do registro são **iguais** a
    `trajetoria.fonte_academica.contrato.CAMPOS_DE_CONTEXTO` e têm o mesmo tipo de campo e
    `null=True` que em `ConclusaoAcademica`;
  - `capturado_em`: `null=False`, sem `default`, sem `auto_now`/`auto_now_add`;
  - `elegivel_no_snapshot`: `BooleanField`, `null=False`, sem `default`
    (`NOT_PROVIDED`);
  - `on_delete`: `SnapshotAnalitico.campanha` = `PROTECT`;
    `RegistroDoSnapshot.snapshot` = `CASCADE`; `RegistroDoSnapshot.conclusao` = `PROTECT`;
    `related_name` `"+"` nas FKs para Campanha e Conclusão, `"registros"` no snapshot;
  - constraint `UniqueConstraint(fields=["snapshot", "conclusao"],
    name="registro_conclusao_unica_no_snapshot")` existe, e inserir dois registros iguais
    levanta `IntegrityError`;
  - **nenhuma** outra constraint (sem CHECK de não vazio nem de coerência ano/data);
  - nenhuma unicidade por Campanha: dois `SnapshotAnalitico` da mesma Campanha gravam;
  - `SnapshotAnalitico.Meta.ordering == ["capturado_em", "id"]`;
  - nenhuma FK de nenhum dos dois modelos aponta para `Pessoa`, `Participacao`,
    `Resposta`, `Versao`, `Secao`, `Pergunta` ou `Opcao`.
- [X] T006 [P] Escrever `tests/analitico/test_analitico_regras.py`: `Motivo` tem
  exatamente `CAMPANHA_NUNCA_ABERTA = "campanha_nunca_aberta"` e
  `COLETA_NAO_ENCERRADA = "coleta_nao_encerrada"`; `SnapshotRecusado(motivo,
  campanha_id)` expõe `.motivo` e `.campanha_id`; seu `str` contém o texto do motivo da
  spec ("a coleta ainda não terminou" para `COLETA_NAO_ENCERRADA`; "a Campanha nunca
  entrou em coleta" para `CAMPANHA_NUNCA_ABERTA`; spec US2.1, US2.2) e o `id` da Campanha;
  `CapturaInconsistente` é exceção distinta de `SnapshotRecusado`.

### Implementação

- [X] T007 [P] Implementar `trajetoria/analitico/regras.py` (padrão de
  `trajetoria/campanha/regras.py`): `Motivo` (Enum de dois valores, com comentário da FR
  da spec), `SnapshotRecusado(Exception)` com `.motivo` e `.campanha_id` e `str` com o
  texto do motivo ("a coleta ainda não terminou" / "a Campanha nunca entrou em coleta")
  e o `id` da Campanha, e
  `CapturaInconsistente(Exception)`; docstring: nada é gravado em nenhuma das duas; sem
  valores acadêmicos nas mensagens (spec FR-124).
- [X] T008 Implementar `trajetoria/analitico/models.py` conforme
  [data-model.md §1](data-model.md#1-persistência):
  - `SnapshotAnalitico`: `id` UUID PK `default=uuid.uuid4, editable=False`; `campanha`
    FK `"campanha.Campanha"`, `on_delete=models.PROTECT`, `related_name="+"`;
    `capturado_em = models.DateTimeField()` ("sem `default` nem `auto_now_add`, para que
    nenhuma criação fora da operação passe despercebida"); `Meta.ordering =
    ["capturado_em", "id"]` com comentário "só determinismo, sem significado de
    autoridade (spec FR-063)";
  - `RegistroDoSnapshot`: `id` UUID PK; `snapshot` FK `SnapshotAnalitico`,
    `on_delete=models.CASCADE`, `related_name="registros"`; `conclusao` FK
    `"academico.ConclusaoAcademica"`, `on_delete=models.PROTECT`, `related_name="+"`;
    `elegivel_no_snapshot = models.BooleanField()` (não nulo, sem default);
    `curso`, `unidade`, `nivel`, `modalidade`, `forma_oferta` = `TextField(null=True)`;
    `ano_conclusao = PositiveSmallIntegerField(null=True)`;
    `data_conclusao = DateField(null=True)`; `Meta.constraints =
    [UniqueConstraint(fields=["snapshot", "conclusao"],
    name="registro_conclusao_unica_no_snapshot")]`;
  - docstring do módulo: `NULL` = não informado; o contexto é **institucional, no momento
    da captura** (spec FR-044); ano e data são atributos independentes da 001 (research
    R4); nenhum CHECK da 001 é repetido (research R5); `on_delete` e consequência para
    DP-1202 (research R6: `PROTECT` na Conclusão preserva rastreabilidade e a associação
    com os fatos transacionais e fará qualquer eliminação futura exigir decisão
    explícita); escrita só por `operacoes.py` (ADR 0002).
- [X] T009 Gerar `trajetoria/analitico/migrations/0001_initial.py` com
  `uv run python manage.py makemigrations analitico` e revisar: só `CreateModel` dos dois
  modelos e a constraint; nenhuma operação sobre tabelas de outros apps.

**Checkpoint**: T005 e T006 verdes; `uv run python manage.py makemigrations --check
--dry-run` → `No changes detected`; suíte completa verde.

---

## Phase 3: User Story 1 — Capturar snapshot de Campanha encerrada válida (P1) 🎯 MVP

**Goal**: `capturar_snapshot(campanha)` cria o snapshot completo e atômico, com o momento
definido pela operação.

**Independent Test**: capturar a Campanha E e verificar snapshot, Campanha, momento e um
registro por Conclusão do universo.

### Testes primeiro

- [X] T010 [US1] Escrever `tests/analitico/test_analitico_captura.py` (parte US1):
  - Campanha aberta e encerrada explicitamente → devolve `SnapshotAnalitico` gravado, com
    `campanha_id` da Campanha e `antes ≤ capturado_em ≤ depois` (relógio real lido antes e
    depois da chamada);
  - Campanha aberta e encerrada pelo fim do período (`encerrada_em` nulo) → aceita;
  - a assinatura de `capturar_snapshot` tem um único parâmetro posicional e nenhum
    parâmetro de momento (`inspect.signature`);
  - argumento que não é `Campanha` → `TypeError`, sem consulta ao banco
    (`django_assert_num_queries(0)`);
  - `campanha_v` (sem Participações) → todos os registros elegíveis; nenhuma Participação
    na Campanha (caso B);
  - Campanha encerrada com população vazia e sem Participações → snapshot com zero
    registros, sem erro;
  - **rollback**: com `RegistroDoSnapshot.objects.bulk_create` substituído no teste
    (`monkeypatch` do atributo do manager, como em
    `tests/participacao/test_participacao_concorrencia.py`) por função que levanta
    exceção → a exceção propaga e não existe nenhum `SnapshotAnalitico` nem
    `RegistroDoSnapshot`;
  - **rollback na verificação final**: com o auxiliar privado `_universo` envolvido no
    teste (`monkeypatch`) por função que chama o original e, em seguida, cria por ORM uma
    `Participacao` da Campanha para uma Conclusão fora do universo, com `iniciada_em` no
    período de coleta (simula escrita concorrente iniciada antes do encerramento e
    confirmada depois da leitura) → `CapturaInconsistente`; nenhum snapshot nem registro;
  - Versão da Campanha forçada a RASCUNHO por `Versao.objects.filter(...).update(...)` no
    teste → `CapturaInconsistente`; nada gravado;
  - a captura não altera nenhuma linha de Campanha, Conclusão, Participação ou Resposta
    (comparação de retratos antes e depois).

### Implementação

- [X] T011 [US1] Implementar `trajetoria/analitico/operacoes.py` conforme
  [contracts/operacoes.md](contracts/operacoes.md), com `__all__ = ["capturar_snapshot"]`:
  - `capturar_snapshot(campanha) -> SnapshotAnalitico`: `TypeError` para não-`Campanha`
    antes de qualquer acesso ao banco; `with transaction.atomic():`
    `capturado_em = momento_de_referencia(None)`; Campanha relida pelo `pk`
    (`ValueError` se inexistente); Versão relida e `estado == EstadoVersao.PUBLICADA`,
    senão `CapturaInconsistente`; universo; `SnapshotAnalitico.objects.create(...)`;
    `RegistroDoSnapshot.objects.bulk_create(registros, batch_size=_LOTE)` com
    `_LOTE = 1000` (constante do módulo); verificações; `return snapshot`;
  - auxiliares privados `_elegiveis(campanha)` (`values_list("pk", *CAMPOS_DE_CONTEXTO)`)
    e `_participantes(campanha)` (só `conclusao_id`), e `_universo` que os compõe num
    `dict` por `pk` (elegíveis primeiro, `True`; o contexto é lido de novo só dos
    participantes ausentes, `False`) — ajuste da revisão de código;
  - verificação (spec FR-053 d): `not Participacao.objects.filter(campanha=campanha).exclude(
    conclusao_id__in=RegistroDoSnapshot.objects.filter(snapshot=s).values("conclusao_id")
    ).exists()`; falha → `CapturaInconsistente` com contagens e `id`s;
  - docstring do módulo: único caminho de escrita; atomicidade = snapshot e todos os
    registros ou nada; o corte é o que foi lido (spec FR-054), sem leitura isolada nem
    lock; escrita concorrente iniciada antes do encerramento detectada pela verificação
    final; desvio consciente do padrão `agora=` (research R8); nenhuma exposição a
    operadores — quando exposta, a competência CPAEG precisará ser aplicada por quem expuser
    (spec FR-102; research R14).

  Nesta história a condição de captura ainda não é verificada (US2).

**Checkpoint**: T010 verde; suíte completa verde.

---

## Phase 4: User Story 2 — Recusar captura fora do momento permitido (P1)

**Goal**: só Campanha aberta e encerrada é capturada.

**Independent Test**: capturar C, P e X e verificar recusa sem gravação.

### Testes primeiro

- [X] T012 [US2] Acrescentar a `tests/analitico/test_analitico_captura.py`:
  - `campanha_c` (em coleta) → `SnapshotRecusado` com `COLETA_NAO_ENCERRADA`; zero
    snapshots e registros (caso L);
  - `campanha_p` (nunca aberta, em preparação) → `CAMPANHA_NUNCA_ABERTA`; nada gravado;
  - `campanha_x` (nunca aberta, ENCERRADA pelo fim do período) → `CAMPANHA_NUNCA_ABERTA`,
    **não** `COLETA_NAO_ENCERRADA` (caso M);
  - Campanha aberta com `aberta_em` futura em relação ao relógio (aberta com `agora=`
    futuro pelas operações da 004) → `COLETA_NAO_ENCERRADA`;
  - mensagem da recusa contém o texto do motivo da spec ("a coleta ainda não terminou" /
    "a Campanha nunca entrou em coleta"), o `id` da Campanha e nenhum valor acadêmico.

### Implementação

- [X] T013 [US2] Em `trajetoria/analitico/operacoes.py`, verificar a condição antes da
  Versão e de qualquer gravação, com o mesmo instante `capturado_em`: `aberta_em is None`
  → `SnapshotRecusado(Motivo.CAMPANHA_NUNCA_ABERTA, …)`; senão
  `estado(campanha, agora=capturado_em) is not EstadoCampanha.ENCERRADA` →
  `SnapshotRecusado(Motivo.COLETA_NAO_ENCERRADA, …)` (research R10). Sem estado novo.

**Checkpoint**: T010 e T012 verdes.

---

## Phase 5: User Story 3 — Congelar a população elegível do momento (P1)

**Goal**: registros elegíveis = população da 004 lida na captura.

**Independent Test**: comparar com `populacao_no_momento`; incorporar depois e verificar
que o snapshot não muda.

### Testes primeiro

- [X] T014 [US3] Escrever `tests/analitico/test_analitico_universo.py` (parte US3):
  - número de registros elegíveis == `populacao_no_momento(campanha).count()`, e o
    conjunto de `conclusao_id` elegíveis == conjunto de `pk` da população;
  - para **cada** registro, `elegivel_no_snapshot == avaliar(campanha,
    conclusao).elegivel` (equivalência com a função pura da 004);
  - elegível sem Participação → registro elegível (caso F);
  - Campanha sem critérios (população ampla) → universo = todas as Conclusões, todas
    elegíveis;
  - duas Conclusões da mesma Pessoa elegíveis → dois registros;
  - Conclusão incorporada (criada por ORM) depois do encerramento e antes da captura,
    satisfazendo os critérios → registro elegível;
  - depois da captura, criar Conclusões novas que satisfazem os critérios →
    `retrato(snapshot)` idêntico; `populacao_no_momento(campanha).count()` maior;
  - sem N+1: o número de consultas de `capturar_snapshot` é o mesmo com 3 e com 30
    Conclusões elegíveis (`CaptureQueriesContext`, comparação, sem orçamento fixo).

### Implementação

- [X] T015 [US3] Nenhum código novo esperado (entregue por T011). Se algum teste de T014
  falhar, corrigir somente `_elegiveis`/`_universo` em `trajetoria/analitico/operacoes.py`,
  sem tocar `trajetoria/campanha/`.

**Checkpoint**: T014 verde.

---

## Phase 6: User Story 4 — Congelar o contexto acadêmico (P1)

**Goal**: sete atributos copiados como estavam, ausência preservada.

**Independent Test**: capturar, simular correção, comparar registro.

### Testes primeiro

- [X] T016 [P] [US4] Escrever `tests/analitico/test_analitico_contexto.py`:
  - os sete atributos do registro são iguais aos da Conclusão no momento da captura
    (Conclusão Serra, "Técnico em Informática", Técnico, Presencial, Subsequente, 2022);
  - atributos ausentes (unidade e forma de oferta `None`) → `None` no registro (caso H);
  - ano sem data → `ano_conclusao` congelado, `data_conclusao is None`;
  - ano e data → ambos congelados;
  - grafia como registrada (`" Serra "`, `"técnico em INFORMÁTICA"`) → idêntica, sem
    `strip` nem normalização;
  - cursos homônimos na Serra e em Vitória → registros distintos com o mesmo `curso` e
    `unidade` diferente (caso I; o recorte é verificado em US9);
  - depois de `simular_correcao` de todos os sete atributos → registro inalterado.

### Implementação

- [X] T017 [US4] Nenhum código novo esperado (entregue por T011). Se falhar, corrigir a
  cópia em `trajetoria/analitico/operacoes.py` para usar exatamente
  `CAMPOS_DE_CONTEXTO`, sem transformação.

**Checkpoint**: T016 verde.

---

## Phase 7: User Story 5 — Preservar Participações fora da população congelada (P1)

**Goal**: toda Participação tem registro; a não elegível no snapshot fica marcada `False`.

**Independent Test**: simular que a Conclusão de uma Participação deixou de satisfazer os
critérios, capturar, verificar.

### Testes primeiro

- [X] T018 [US5] Acrescentar a `tests/analitico/test_analitico_universo.py`:
  - universo == elegíveis ∪ Conclusões com Participação (conjunto exato de
    `conclusao_id`);
  - Participação concluída cuja Conclusão foi movida por `simular_correcao` para unidade
    fora do critério (antes da captura) → registro com `elegivel_no_snapshot=False`, com o
    contexto já corrigido (o lido na captura) (caso G);
  - Conclusão elegível **com** Participação → exatamente um registro, elegível
    (deduplicação por Conclusão);
  - Participação elegível → registro elegível;
  - nenhuma Participação da Campanha sem registro, em todos os cenários de referência;
  - a captura não remove nem altera a Participação não elegível.

### Implementação

- [X] T019 [US5] Nenhum código novo esperado (entregue por T011). Se falhar, corrigir
  `_participantes`/`_universo` em `trajetoria/analitico/operacoes.py`.

**Checkpoint**: T014 e T018 verdes.

---

## Phase 8: User Story 6 — Ler um snapshot sem depender do estado acadêmico atual (P1)

**Goal**: o que foi gravado não muda com a fonte.

**Independent Test**: capturar, alterar Conclusões, incorporar novas, comparar retratos.

### Testes primeiro

- [X] T020 [P] [US6] Escrever `tests/analitico/test_analitico_reproducao.py` (parte US6):
  - captura de E; depois `simular_correcao` de unidade, curso, nível, modalidade, forma de
    oferta e ano de **todas** as Conclusões do universo e criação de Conclusões novas
    elegíveis → `retrato(snapshot)` idêntico ao de antes (casos J, K);
  - nenhuma Conclusão nova aparece no snapshot já capturado.

  (Indicadores, recortes e dataset depois da alteração são verificados em US7–US9, nos
  mesmos arquivos.)

### Implementação

- [X] T021 [US6] Nenhum código novo esperado: garantido pela persistência (T008) e pela
  ausência de operação de alteração. Se falhar, investigar escrita indevida em
  `trajetoria/analitico/`.

**Checkpoint**: T020 verde. **MVP P1 completo** (US1–US6).

---

## Phase 9: User Story 7 — Dataset do snapshot com Participações e Respostas (P2)

**Goal**: fronteira de leitura mínima, sem copiar nada.

**Independent Test**: percorrer `linhas_do_dataset` de E e conferir linha a linha.

### Testes primeiro

- [X] T022 [P] [US7] Escrever `tests/analitico/test_analitico_dataset.py`:
  - uma `LinhaDoDataset` por registro, em ordem de `conclusao_id`;
  - Participação concluída normalmente (caso C) → `participacao.concluida`, `respostas`
    com todas as Respostas gravadas, `fora_do_percurso == frozenset()`;
  - concluída por Q1 = "Não" (caso D) → concluída, só com a Resposta registrada; nenhuma
    categoria de recusa;
  - rascunho com Resposta fora do percurso (caso E) → `participacao.concluida is False`;
    `respostas` inclui a do "Comentário"; `fora_do_percurso ==
    situacao_da_jornada(participacao).fora_do_percurso` (equivalência com a 006) e contém
    a Pergunta "Comentário"; a Resposta ativa (Pergunta fora de `fora_do_percurso`) e a
    inativa são distinguíveis;
  - rascunho numa Versão com estrutura não suportada (duas Perguntas com regra na mesma
    Seção, montada por `versao_publicada_de` de `tests.participacao.construcao`) →
    `fora_do_percurso is None`; Respostas preservadas;
  - elegível sem Participação (caso F) → `participacao is None`, `respostas` vazio;
  - toda entrada de `respostas` é `RespostaNoDataset` com os valores gravados (Pergunta,
    `opcao_id`/`opcao`, `opcoes`, `texto`, `escala`, `complemento`);
  - escolha múltipla → `respostas[pergunta_id].opcoes` é a tupla das Opções selecionadas,
    na ordem do instrumento (estrutura da 005), sem serialização;
  - **Q14** (spec US7.5): Campanha encerrada com a baseline publicada
    (`tests.participacao.construcao.baseline_publicada()`), Participação que responde Q14
    pelas operações da 005 com `agora=NA_COLETA` → a Resposta de Q14 está em `respostas`,
    separada de `contexto.nivel`, e nenhum valor de uma substitui o outro (FR-073; ADR
    0003);
  - Pergunta "Em qual campus você concluiu seu curso?" respondida → em `respostas`,
    separada de `contexto.unidade`;
  - toda Resposta tem `pergunta.secao.versao_id == campanha.versao_id` (caso O);
  - depois de `simular_correcao`, `contexto` de cada linha é o congelado, e o
    `CaptureQueriesContext` da iteração não contém a tabela de
    `ConclusaoAcademica` nem de `Pessoa`;
  - **sem navegação ao estado atual** (spec FR-076): percorrendo recursivamente os
    `dataclasses.fields` de `LinhaDoDataset`, `ParticipacaoNoDataset`, `ContextoCongelado`
    e de cada `RespostaNoDataset` (e os itens de tuplas e mapeamentos), nenhum valor é
    instância de `Resposta`, `RespostaOpcao`, `Participacao`, `RegistroDoSnapshot`,
    `ConclusaoAcademica` ou `Pessoa`; e os objetos `Pergunta` e `Opcao` entregues não têm
    atributo de relação reversa para `Resposta` (verificado por `_meta.related_objects`);
  - sem N+1: número de consultas para consumir o iterador igual com 3 e com 30 registros;
  - nada é gravado (contagens de todas as tabelas antes/depois).

### Implementação

- [X] T023 [US7] Criar `trajetoria/analitico/consultas.py` com a parte do dataset conforme
  [contracts/consultas.md](contracts/consultas.md) e [data-model.md §2](data-model.md#2-objetos-de-valor-em-memória):
  - `ContextoCongelado` (sete campos de `CAMPOS_DE_CONTEXTO`), `ParticipacaoNoDataset`
    (`id`, `iniciada_em`, `concluida_em`; propriedade `concluida`), `RespostaNoDataset`
    (`pergunta: Pergunta`, `opcao_id: UUID | None`, `opcao: Opcao | None`,
    `opcoes: tuple[Opcao, ...]`, `texto: str | None`, `escala: int | None`,
    `complemento: str | None`) e `LinhaDoDataset` (`conclusao_id`,
    `elegivel_no_snapshot`, `contexto`, `participacao`, `respostas` como
    `MappingProxyType` `id da Pergunta → RespostaNoDataset`, `fora_do_percurso:
    frozenset | None`), todos `@dataclass(frozen=True)`, sem outras propriedades
    ([data-model.md §2.1–2.4](data-model.md#2-objetos-de-valor-em-memória));
  - `linhas_do_dataset(snapshot) -> Iterator[LinhaDoDataset]`: `conteudo_da_versao` da
    Versão da Campanha uma vez; registros do snapshot por `values_list`, ordem
    `conclusao_id`; uma consulta de Participações da Campanha; uma de Respostas dessas
    Participações com `select_related("pergunta", "opcao")` e `prefetch_related("opcoes")`;
    cada `Resposta` convertida em `RespostaNoDataset` (`opcoes=tuple(r.opcoes.all())`) —
    nenhuma instância de `Resposta` sai da função;
    concluída → `fora_do_percurso=frozenset()` sem recálculo; não concluída →
    `frozenset(respostas) - perguntas_do_percurso(percorrer(conteudo,
    respondidas(respostas)))` (funções de `trajetoria.participacao.percurso`; `respondidas`
    lê só `opcao_id`, presente em `RespostaNoDataset`);
    `ParticipacaoRejeitada` com `ESTRUTURA_NAO_SUPORTADA` → `None`;
  - docstring: fronteira **mínima**, não é a 013 (sem schema, colunas, serializador,
    achatamento, nomes externos, CSV, GeN); `conclusao_id` e `participacao.id` são
    referências técnicas internas, não identificadores exportáveis (spec FR-047; 005/DP-505);
    Respostas lidas das tabelas da 005, nunca gravadas de novo (FR-121); nenhum objeto
    entregue leva à Conclusão atual, à Pessoa ou à Participação transacional (FR-076); o
    snapshot é recebido explicitamente (FR-064); **volume**: Participações e Respostas da
    Campanha são carregadas numa só passada, e a leitura em blocos, se o volume real
    exigir, é mudança local, sem alterar o contrato (research R12).

**Checkpoint**: T022 verde.

---

## Phase 10: User Story 8 — Reproduzir os indicadores básicos (P2)

**Goal**: indicadores sobre o denominador histórico.

**Independent Test**: comparar com contagem manual do cenário de referência.

### Testes primeiro

- [X] T024 [US8] Acrescentar a `tests/analitico/test_analitico_reproducao.py`:
  - `indicadores_do_snapshot(snapshot_e)` == contagem manual: `elegiveis`,
    `iniciadas_elegiveis`, `iniciadas_nao_elegiveis`, `concluidas_elegiveis`,
    `concluidas_nao_elegiveis`; propriedades `iniciadas`, `concluidas`, `nao_concluidas`;
  - concluída por recusa conta como concluída;
  - snapshot com Participação não elegível (caso G) → conta no numerador, não no
    denominador; cenário com taxa > 100% → `taxa_inicio > 1`, sem truncamento;
  - zero elegíveis → `taxa_inicio is None` e `taxa_conclusao is None`;
  - depois de `simular_correcao` e de incorporação nova → indicadores idênticos;
  - logo após a captura, sem deriva → `elegiveis`, `iniciadas`, `concluidas` iguais aos
    de `trajetoria.acompanhamento.consultas.indicadores_da_campanha(campanha,
    EscopoDeAcompanhamento(institucional=True, unidades=frozenset()))` (011, importada só
    no teste);
  - `CaptureQueriesContext` da chamada: nenhuma tabela de `academico` nem de Resposta no
    SQL; uma consulta.

### Implementação

- [X] T025 [US8] Em `trajetoria/analitico/consultas.py`: `IndicadoresDoSnapshot`
  (`@dataclass(frozen=True)` com os cinco contadores; propriedades derivadas `iniciadas`,
  `concluidas`, `nao_concluidas` e as mesmas por elegibilidade; `registros =
  elegiveis + iniciadas_nao_elegiveis` (todo registro não elegível tem Participação, por
  construção); `taxa_inicio` e
  `taxa_conclusao` `Decimal | None`, sem teto, sem arredondamento; `__add__`) e
  `indicadores_do_snapshot(snapshot)`: um `aggregate` sobre
  `RegistroDoSnapshot.objects.filter(snapshot=snapshot)` anotado com `Exists` de
  `Participacao(campanha_id=snapshot.campanha_id, conclusao_id=OuterRef("conclusao_id"))`
  e da mesma com `concluida_em__isnull=False`, usando `Count("id", filter=…)`. Docstring:
  denominador = elegíveis no snapshot; numerador = todas as Participações das Conclusões
  representadas (spec FR-083).

**Checkpoint**: T024 verde.

---

## Phase 11: User Story 9 — Reproduzir os seis recortes com valores congelados (P2)

**Goal**: os seis recortes da 011 sobre o contexto congelado.

**Independent Test**: cada recorte contra contagem manual, antes e depois da alteração.

### Testes primeiro

- [X] T026 [US9] Acrescentar a `tests/analitico/test_analitico_reproducao.py`:
  - `RecorteDoSnapshot` tem exatamente seis membros e os campos de cada um são iguais aos
    `campos` da `Recorte` da 011 de mesmo nome (`trajetoria.acompanhamento.consultas`,
    importada só no teste);
  - para cada recorte, soma das linhas == `indicadores_do_snapshot`;
  - cada linha == contagem manual sobre os valores congelados;
  - atributo ausente → linha com `None` na chave;
  - recorte por curso: chave `(unidade, curso)`; homônimos da Serra e de Vitória em linhas
    distintas (caso I);
  - registros não elegíveis com Participação contam nas Participações da linha e não no
    denominador da linha;
  - depois de `simular_correcao` dos seis atributos → todos os recortes idênticos;
  - logo após a captura, sem deriva → para cada recorte, as linhas com alguma contagem
    não nula coincidem com `campanha_acompanhada(campanha, EscopoDeAcompanhamento(
    institucional=True, unidades=frozenset()), pode_consultar_rascunho=True,
    recorte=<Recorte da 011 de mesmo nome>).linhas` (função pública da 011; as linhas com
    zero da 011 são apresentação dela);
  - `CaptureQueriesContext`: uma consulta por recorte, sem tabela de `academico` nem de
    Resposta.

### Implementação

- [X] T027 [US9] Em `trajetoria/analitico/consultas.py`: `RecorteDoSnapshot` (Enum fechado:
  `UNIDADE ("unidade",)`, `CURSO ("unidade", "curso")`, `NIVEL ("nivel",)`,
  `MODALIDADE ("modalidade",)`, `FORMA_OFERTA ("forma_oferta",)`,
  `ANO_CONCLUSAO ("ano_conclusao",)`), `LinhaDoRecorte(chave: tuple, indicadores:
  IndicadoresDoSnapshot)` e `recorte_do_snapshot(snapshot, recorte)`: uma consulta
  `values(*recorte.campos).annotate(...)` com `order_by()` vazio e as mesmas anotações de
  T025; linhas em ordem determinística pela chave, `None` por último; sem linhas com zero
  acrescentadas; sem rótulos. Não importar `trajetoria.acompanhamento`.

**Checkpoint**: T024 e T026 verdes.

---

## Phase 12: User Story 10 — Distinguir elegibilidade congelada da atual (P2)

**Goal**: a 011 continua mostrando elegíveis atuais e aviso; o snapshot fala em elegíveis
no snapshot.

**Independent Test**: com snapshot existente, comparar 011 e snapshot depois de deriva.

### Testes primeiro

- [X] T028 [US10] Acrescentar a `tests/analitico/test_analitico_reproducao.py`:
  - com snapshot de E e Conclusões novas elegíveis criadas depois →
    `indicadores_da_campanha` da 011 mostra elegíveis atuais maiores; o snapshot mantém
    os seus;
  - `campanha_acompanhada(...)` da 011 para E continua com `AVISO_POPULACAO_ATUAL` em
    `avisos` (a 011 não passa a usar snapshot);
  - nenhum módulo de nenhum outro app de `trajetoria/` (`academico`, `campanha`,
    `participacao`, `instrumento`, `fonte_academica`, `formulario_2024`, `governanca`,
    `interface`, `editor`, `demonstracao`, `acompanhamento`) importa `trajetoria.analitico`
    (inspeção estrutural dos imports por `ast`; spec FR-023).

### Implementação

- [X] T029 [US10] Revisar docstrings de `trajetoria/analitico/consultas.py` e
  `operacoes.py`: denominador sempre "elegíveis no snapshot" (ou "do snapshot de
  <momento da captura>"), nunca "elegíveis atuais", "população atual" ou "população da
  Campanha" (spec FR-090). Nenhuma mudança na 011.

**Checkpoint**: T028 verde; `uv run pytest tests/acompanhamento` verde sem alteração.

---

## Phase 13: User Story 11 — Vários snapshots imutáveis e independentes (P2)

**Goal**: A e B coexistem; nenhum é escolhido implicitamente.

**Independent Test**: capturar A, simular correção, capturar B, comparar.

### Testes primeiro

- [X] T030 [P] [US11] Escrever `tests/analitico/test_analitico_multiplos.py`:
  - A; `simular_correcao`; B → B reflete o novo contexto/elegibilidade; `retrato(A)`
    idêntico ao de antes de B;
  - A e B da mesma Campanha coexistem, com conjuntos de registros independentes
    (`registros` de A ∩ de B = ∅ por `id`);
  - `snapshots_da_campanha(campanha)` devolve A e B, em ordem `(capturado_em, id)`, e só
    os da Campanha;
  - duas capturas seguidas sem mudança → dois snapshots distintos e equivalentes
    (retratos iguais), sem deduplicação;
  - `set(consultas.__all__)` é exatamente o conjunto do contrato
    ([contracts/consultas.md](contracts/consultas.md)), o que prova estruturalmente que
    não existe função de "snapshot atual/vigente/último";
  - `set(operacoes.__all__) == {"capturar_snapshot"}`;
  - **concorrência determinística** (caso N; spec FR-062, SC-007): com o auxiliar privado
    `_universo` envolvido no teste (`monkeypatch`) para que, na primeira chamada, execute
    uma captura completa da mesma Campanha antes de devolver o universo original → ao
    final existem dois snapshots completos (cada um com o número esperado de registros),
    com conjuntos de registros independentes e sem erro; é a proteção principal, sem
    depender de escalonamento de threads;
  - **opcional** (`@pytest.mark.django_db(transaction=True)`, threads com
    `threading.Barrier`, mesmo padrão de `test_inicios_simultaneos_em_threads...` da 005):
    duas capturas simultâneas → dois snapshots completos, cada um com o número esperado de
    registros (caso N). Remover se instável no CI.

### Implementação

- [X] T031 [US11] Em `trajetoria/analitico/consultas.py`: `snapshots_da_campanha(campanha)
  -> QuerySet[SnapshotAnalitico]` (filtro pela Campanha, `order_by("capturado_em", "id")`)
  com docstring "ordem administrativa, sem autoridade institucional (DP-1201); nenhum
  consumidor deve tomar o primeiro ou o último como autoritativo". Definir `__all__` com
  exatamente: `ContextoCongelado`, `IndicadoresDoSnapshot`, `LinhaDoDataset`,
  `LinhaDoRecorte`, `ParticipacaoNoDataset`, `RecorteDoSnapshot`, `RespostaNoDataset`,
  `indicadores_do_snapshot`, `linhas_do_dataset`, `recorte_do_snapshot`,
  `snapshots_da_campanha`.

**Checkpoint**: T030 verde.

---

## Phase 14: User Story 12 — Snapshot referencia a Versão publicada sem copiá-la (P2)

**Goal**: nenhuma cópia do instrumento.

**Independent Test**: inspecionar modelos e dataset.

### Testes primeiro

- [X] T032 [P] [US12] Escrever `tests/analitico/test_analitico_fronteiras.py` (parte
  US12): o app `analitico` tem exatamente dois modelos (`apps.get_app_config("analitico")
  .get_models()`); nenhum campo dos dois modelos guarda texto do instrumento, Seção,
  Pergunta, Opção ou Versão (conjunto exato de campos, já em T005, aqui como invariante de
  fronteira); a Versão alcançada por `snapshot.campanha.versao` é a PUBLICADA da Campanha;
  dois snapshots de Campanhas com Versões diferentes não oferecem nenhuma correspondência
  entre Perguntas (nenhuma função ou campo de equivalência no `__all__`).

### Implementação

- [X] T033 [US12] Nenhum código novo esperado. Se falhar, remover a cópia indevida de
  `trajetoria/analitico/`.

**Checkpoint**: T032 verde.

---

## Phase 15: User Story 13 — Metadados mínimos do snapshot (P3)

**Goal**: listar snapshots com totais, sem dado individual, sem função nova.

**Independent Test**: `snapshots_da_campanha` + `indicadores_do_snapshot`.

### Testes primeiro

- [X] T034 [US13] Acrescentar a `tests/analitico/test_analitico_multiplos.py`: para cada
  snapshot de `snapshots_da_campanha(E)`, `id`, `campanha_id`, `capturado_em` e
  `indicadores_do_snapshot` dão os totais (`registros` igual a
  `snapshot.registros.count()`, elegíveis, Participações, concluídas); o resultado não contém nenhum `conclusao_id` nem Resposta; o momento do
  encerramento da Campanha continua consultável por
  `trajetoria.campanha.consultas.encerramento(campanha)` ao lado de `capturado_em`.

### Implementação

- [X] T035 [US13] Nenhum código novo esperado (composição de T025 e T031). Não criar
  função de metadados.

**Checkpoint**: T034 verde.

---

## Phase 16: Polish & Cross-Cutting

**Purpose**: fronteiras, privacidade, integridade referencial, documentação, suíte.

- [X] T036 [P] Acrescentar a `tests/analitico/test_analitico_fronteiras.py`
  (integridade referencial, só por ORM no teste, sem operação de produção):
  - excluir uma Conclusão **sem** Participação referenciada por um registro →
    `ProtectedError`; snapshot e registros intactos;
  - excluir a Campanha de um snapshot → `ProtectedError`;
  - excluir um `SnapshotAnalitico` → seus registros desaparecem (`CASCADE`); os de outro
    snapshot permanecem.
- [X] T037 [P] Acrescentar a `tests/analitico/test_analitico_fronteiras.py` (privacidade e
  escopo, estruturais):
  - nenhum campo dos dois modelos se chama ou guarda `nome`, `cpf`, `email`, `telefone`,
    `matricula`, `endereco`, `fonte`, `id_externo`, `pessoa`, hash ou pseudônimo (conjunto
    exato de campos);
  - nenhuma FK para `Pessoa`;
  - os imports dos módulos de `trajetoria/analitico/` (por `ast`) vêm só de stdlib,
    `django` e `trajetoria.{analitico, campanha, participacao, academico, instrumento,
    fonte_academica}`: nada de `acompanhamento`, `interface`, `editor`, `demonstracao`,
    `governanca`;
  - `importlib.util.find_spec` não encontra `trajetoria.analitico.views`, `.urls`,
    `.admin`, `.management`; não há `trajetoria/analitico/templates/`;
  - nenhum padrão de URL do projeto resolve para módulo de `trajetoria.analitico`;
  - `pyproject.toml` sem dependência nova (lista de `dependencies` igual à atual:
    Django e psycopg);
  - `governanca.regras.__all__` inalterado (nenhuma regra nova);
  - captura nunca automática (spec FR-015): nenhum módulo de `trajetoria/analitico/`
    importa `django.db.models.signals`, `django.dispatch` ou `receiver` (por `ast`), e
    `apps.py` não define `ready()`.
- [X] T038 [P] Atualizar o docstring de `trajetoria/analitico/__init__.py` com a relação com
  as DPs: DP-1201 (nenhum snapshot oficial; leitura sempre explícita), DP-1202 (retenção;
  `PROTECT` na Conclusão), 004/DP-408 e 005/DP-507 parcialmente resolvidas, 011/DP-1101
  (sem supressão interna), 002/DP-006 (sem correspondência entre Versões), 005/DP-503,
  006/DP-601, 007/DP-703.
- [X] T039 Executar `uv run ruff check .` e `uv run ruff format --check .` e corrigir só
  arquivos de `trajetoria/analitico/` e `tests/analitico/`.
- [X] T040 Executar `uv run python manage.py makemigrations --check --dry-run` (`No changes
  detected`) e `uv run pytest` (suíte completa verde, inclusive `tests/acompanhamento`
  sem alteração).
- [X] T041 Validar [quickstart.md](quickstart.md) de ponta a ponta e ajustar o texto se um
  passo divergir do implementado.
- [X] T042 Revisão final contra "Sinais de over engineering" de [plan.md](plan.md): 2
  modelos, 1 migration, 0 views/urls/templates/commands/jobs; nenhum terceiro modelo,
  serializador, schema, lock, cache, função "atual"; `git diff --stat main` só com
  `trajetoria/analitico/`, `tests/analitico/`, `config/settings.py` e
  `specs/012-dataset-analitico-reprodutivel/`, mais o ajuste de escopo do teste
  `test_12_nada_de_gen_ou_dashboard` da 007 (`tests/participacao/test_entrada_aceitacao.py`),
  registrado em plan.md, "Alterações em features anteriores".

---

## Dependencies & Execution Order

**Fases**:

- Setup (T001–T004) → Foundational (T005–T009) → histórias.
- US1 (T010–T011) → US2 (T012–T013): mesma operação e mesmo arquivo de teste.
- US3 (T014–T015), US4 (T016–T017), US5 (T018–T019) e US6 (T020–T021) dependem de US1.
  US3 e US5 são sequenciais (mesmo arquivo de teste); US4 e US6 podem correr em paralelo
  com elas.
- US7 (T022–T023) depende de US1; cria `consultas.py`.
- US8 (T024–T025) → US9 (T026–T027) → US10 (T028–T029): mesmo arquivo de teste e
  `consultas.py`.
- US11 (T030–T031) depende de US7 (`consultas.py` já existe). US13 (T034–T035) depende de
  US8 e US11.
- US12 (T032–T033) depende da Foundational e de US1.
- Polish (T036–T042) por último; T036 e T037 depois de T032 (mesmo arquivo).

**Dentro de cada história**: testes → implementação → checkpoint.

## Parallel Opportunities

- Setup: T003 ∥ T004.
- Foundational: T005 ∥ T006 ∥ T007 ∥ T008 (arquivos distintos; `models.py` não importa
  `regras.py`); T009 depois de T008.
- Depois de US1: T014 (universo) ∥ T016 (contexto) ∥ T020 (reprodução) ∥ T022 (dataset)
  ∥ T032 (fronteiras), arquivos distintos.
- Polish: T038 ∥ (T036 → T037).

```text
# Exemplo — depois de US1 e US2:
T014 test_analitico_universo.py   ∥   T016 test_analitico_contexto.py
T020 test_analitico_reproducao.py ∥   T022 test_analitico_dataset.py
T032 test_analitico_fronteiras.py
```

## Implementation Strategy

1. **MVP (P1)**: Setup + Foundational + US1–US6. Captura válida e atômica, recusas,
   população e contexto congelados, Participações fora da população preservadas,
   snapshot imune à fonte.
2. **Leitura (P2)**: US7 (dataset mínimo) → US8 (indicadores) → US9 (recortes) → US10
   (distinção da 011).
3. **Multiplicidade e instrumento (P2)**: US11, US12.
4. **Metadados (P3)**: US13, sem função nova.
5. **Polish**: integridade referencial, privacidade, fronteiras, suíte, quickstart,
   revisão de over engineering.

Cada checkpoint mantém a suíte completa verde.

## Resumo

- **Total**: 42 tasks.
  - 4 de setup;
  - 5 de base (2 de teste, 3 de implementação);
  - 26 de histórias (13 de teste, 13 de implementação ou verificação);
  - 7 de polish (2 de teste).
- **Tasks de teste**: 17 (T005, T006, T010, T012, T014, T016, T018, T020, T022, T024,
  T026, T028, T030, T032, T034, T036, T037).
- **Arquivos de produção**: `trajetoria/analitico/{__init__,apps,models,regras,operacoes,
  consultas}.py`, `trajetoria/analitico/migrations/{__init__,0001_initial}.py`,
  `config/settings.py` (uma linha).
- **Arquivos de teste**: `tests/analitico/{__init__,conftest,construcao}.py` e
  `test_analitico_{modelo,regras,captura,universo,contexto,reproducao,dataset,multiplos,
  fronteiras}.py`.
