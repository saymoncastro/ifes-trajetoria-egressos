---

description: "Tasks da Feature 009 — Editor institucional de Pesquisa e Versão"
---

# Tasks: Editor institucional de Pesquisa e Versão

**Input**: design documents de `specs/009-editor-pesquisa-versao/`.

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/rotas.md](contracts/rotas.md),
[contracts/diagnostico.md](contracts/diagnostico.md), [quickstart.md](quickstart.md).

**Stack** (confirmada; [ADR 0001](../../docs/adr/0001-stack-inicial.md)):

- Python 3.13, Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff.
- **Nenhuma dependência nova.**
- **Zero modelos, zero migrações.**
- Um app novo **sem `models.py`**: `trajetoria/editor/`.
- Uma extração pública e pura na 006 (`secoes_nao_suportadas`).
- **Nenhuma alteração na 002.**

**Tests**: obrigatórios e escritos antes da implementação correspondente (test-first). A
feature toca invariantes constitucionais: preservação histórica e imutabilidade da
publicada, versionamento, condicionais, governança e fronteiras. Testes de comportamento
novo DEVEM falhar primeiro. Testes que só confirmam comportamento entregue por história
anterior podem passar de imediato. Se falharem, a correção vai no módulo indicado, sem
regra especial.

**Organization**:

- Phase 1 (Setup) e Phase 2 (Foundational);
- uma fase por história da spec (US1–US15, na ordem de prioridade);
- aceitação ponta a ponta e fronteiras;
- polish.

`trajetoria/editor/views.py`, `urls.py`, `formularios.py` e cada arquivo de teste são
editados **em sequência**, um arquivo por vez. Por isso tarefas no mesmo arquivo nunca
têm [P].

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US15).

## Convenções para todas as tarefas

- **Escrita só pela 002** ([research R3](research.md); [rotas](contracts/rotas.md)).
  Toda escrita do instrumento chama uma função de `trajetoria.instrumento.operacoes`:
  - `criar_pesquisa`, `criar_versao`, `criar_versao_a_partir_de`, `alterar_versao`;
  - `adicionar_secao`, `alterar_secao`, `definir_encaminhamento`, `reordenar_secoes`,
    `remover_secao`;
  - `adicionar_pergunta`, `alterar_pergunta`, `mover_pergunta`, `reordenar_perguntas`,
    `remover_pergunta`;
  - `adicionar_opcao`, `alterar_opcao`, `reordenar_opcoes`, `remover_opcao`;
  - `definir_regra`, `remover_regra`, com `FINALIZAR`.

  Nunca há `.save()`, `.create()`, `.update()`, `.delete()` nem `bulk_*` em modelo
  dentro de `trajetoria/editor/`. **Nunca** são importados ou chamados `publicar` nem
  `renomear_pesquisa`.
- **Leituras permitidas**:
  - `conteudo_da_versao` (002 `conteudo.py`);
  - `verificar_completude`, `Motivo`, `OperacaoRejeitada` (002 `regras.py`);
  - `Pesquisa`, `Versao`, `Secao`, `Pergunta`, `Opcao`, `TipoPergunta` (002 `models.py`,
    só leitura);
  - `secoes_nao_suportadas` (006 `percurso.py`);
  - `Motivo` (006 `participacao/regras.py`, só como causa interna);
  - `FormularioDaSecao` (008 `interface/formularios.py`, só na prévia).

  **Nada** de `campanha`, `academico`, `formulario_2024`, `demonstracao`,
  `participacao.operacoes`, `participacao.consultas`, `participacao.entrada`,
  `participacao.models`, `percorrer` nem `concluir`.
- **Formulários só convertem** ([research R11](research.md)):
  - textos `forms.CharField(required=False, strip=False)`;
  - texto obrigatório vazio é enviado como está, e a 002 rejeita com `TEXTO_VAZIO`;
  - "texto opcional vazio ou só com espaços vira `None`";
  - limites de escala `forms.IntegerField(required=False)`, e ausência ou início ≥ fim é
    recusada pela 002 (`ESCALA_INVALIDA`);
  - nenhum `ModelForm`;
  - o tipo da Pergunta nunca é campo editável depois da criação.
- **Mapeamentos de rejeição locais** ([research R10](research.md)):
  - cada view mapeia só os `Motivo` que a operação chamada pode devolver;
  - motivo **não mapeado** é relançado e vira 500, sem mascarar como validação;
  - `VERSAO_PUBLICADA` → tela 409;
  - `POSICAO_OCUPADA` e `ORDEM_INCOMPLETA` → conflito ("o conteúdo mudou desde que esta
    página foi aberta").
- **Sem identificadores visíveis**: UUIDs só em `href`, `action` e `value`. O texto
  visível usa **ordinais** derivados da ordem ("Seção 4", "Pergunta 2 da Seção 4"),
  nunca `posicao` crua nem UUID ([research R7, R9](research.md)).
- **Nenhuma regra por nome**: nenhuma referência a Q1…Q54, ao nome
  "Pesquisa Institucional de Egressos", à designação
  "Formulário Egresso Ifes 2024 — referência migrada" ou a textos da baseline, no código
  e nos templates do editor (spec FR-009).
- **Baseline intocada nos testes**:
  - nenhum teste chama operação de escrita sobre a Versão devolvida por
    `trajetoria.formulario_2024.materializar()`;
  - quando o cenário precisa de conteúdo real, usa
    `criar_versao_a_partir_de(baseline, "<designação de teste>")`;
  - os demais testes usam Pesquisa e Versão próprias, com nome fictício diferente do da
    baseline.
- **Páginas** ([research R8](research.md)):
  - páginas de lista e consulta não têm campo de texto, só links e botões isolados de
    Subir, Descer e afins;
  - páginas de formulário têm **um** `<form>`;
  - todo POST com `{% csrf_token %}`;
  - `@never_cache` em todas as views;
  - PRG com `?aviso=<código>` de lista fechada (`mensagens.AVISOS`) e âncora
    (`#secao-N`, `#pergunta-N`, `#opcao-N`).
- **Versão publicada** ([research R12](research.md)): toda view de escrita chama
  `_exigir_rascunho(request, versao)` **antes** de qualquer operação:
  - GET de formulário → 302 para a página de consulta com `?aviso=publicada`;
  - POST → 409 com `editor/aviso.html`.
- **Não crie**:
  - `GenericEditorView`, CRUD framework, metaprogramação ou registro de entidades;
  - gerador de forms;
  - `JourneyValidator`, UnitOfWork, service layer;
  - enum de situação ou aprovação;
  - modelo, sessão de edição, autosave, histórico;
  - API, `<script>`.
- **Comportamento compartilhado só onde a semântica é igual**:
  - Subir e Descer das três listas usam o mesmo helper `acoes.mover` e o partial
    `_ordem.html`;
  - as três remoções usam `confirmar_remocao.html`;
  - formulários simples usam `formulario.html`.
- **Contagens não são meta**: os números de views, forms e templates do plan são
  estimativas.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: app vazio montado, configuração e fixtures de teste.

- [X] T001 Create the app skeleton without models:
  - `trajetoria/editor/__init__.py`, empty;
  - `trajetoria/editor/apps.py`: `EditorConfig`, `name = "trajetoria.editor"`,
    `default_auto_field` like `trajetoria/interface/apps.py`;
  - `trajetoria/editor/urls.py` with `urlpatterns = []`;
  - the empty directory `trajetoria/editor/templates/editor/`.

  Do **not** create `models.py` (research R1; Django does not require it).
- [X] T002 Wire the app:
  - in `config/settings.py`, append `"trajetoria.editor"` to `INSTALLED_APPS`;
  - extend the comment above `TRAJETORIA_DEMONSTRACAO` to say the institutional editor
    (009) is available only in this non-productive mode and that the flag is **not**
    governance (DP-901);
  - in `config/urls.py`, add `path("editor/", include("trajetoria.editor.urls"))` and
    update the module docstring.
- [X] T003 [P] Update only the docstring of `trajetoria/demonstracao/middleware.py`:
  - every request, including the editor routes under `/editor/`, is 404 when the mode is
    off;
  - do not change code.
- [X] T004 [P] Create `tests/editor/conftest.py`, with no `__init__.py` in `tests/editor/`:
  - autouse fixture `modo_demonstracao(settings)` setting
    `settings.TRAJETORIA_DEMONSTRACAO = True`;
  - fixtures `pesquisa` (via `op.criar_pesquisa("Pesquisa fictícia de teste")`);
  - `versao` (via `op.criar_versao(pesquisa, "Teste 1")`);
  - `baseline` (via `trajetoria.formulario_2024.materializar().versao`, read-only by
    convention);
  - `copia` (via `op.criar_versao_a_partir_de(baseline, "Cópia de teste")`);
  - `publicada` (copy of the baseline published by `op.publicar` **in the test arrange
    only**).
- [X] T005 [P] Create `tests/editor/construcao_editor.py`, with helpers that are not tests:
  - `retrato(versao)`: returns `(Versao.objects.filter(pk=versao.pk).values().get(),
    conteudo_da_versao(versao))`;
  - `contagens()`: returns `{model.__name__: model.objects.count()}` for every model in
    `django.apps.apps.get_models()`;
  - `texto_visivel(resposta)`: the HTML text without tags or attributes, via
    `html.parser`;
  - `PADROES_TECNICOS`: UUID regex; `\bFR-\d{3}\b`; `Traceback|OperacaoRejeitada|ParticipacaoRejeitada`;
    every `trajetoria.instrumento.regras.Motivo` name and `ESTRUTURA_NAO_SUPORTADA`;
  - `sem_padroes_tecnicos(resposta)`;
  - small builders that create Seção, Pergunta and Opção through `trajetoria.instrumento.operacoes`
    for arranging test Versões, such as `secao(versao, titulo=None)` and
    `pergunta(secao, tipo, texto, opcoes=(), regras={}, obrigatoria=True)`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the 006 extraction and the pure helpers used by every story: presentation,
actions, messages, base layout and the publicada guard.

**⚠️ CRITICAL**: no user-story work starts before this phase is complete.

### Tests for Foundational ⚠️

- [X] T006 [P] Add `test_secoes_nao_suportadas_publica` to `tests/participacao/test_jornada_percurso.py`,
  reusing the in-memory builders `versao_mem`, `secao_mem`, `pergunta_mem` from `tests/participacao/construcao.py` (already imported there):
  - a supported Versão returns `()`;
  - two unsupported Seções are returned in order;
  - for the same content, `[v.detalhe for v in excinfo.violacoes]` from `percorrer`
    corresponds one-to-one to the returned Seções;
  - `"secoes_nao_suportadas" in percurso.__all__`.

  Do **not** modify the existing tests (contracts/diagnostico.md §1).
- [X] T007 [P] Create `tests/editor/test_editor_apresentacao.py` with pure tests, no
  database, over in-memory `ConteudoVersao` built with `versao_mem`, `secao_mem`, `pergunta_mem` from `tests/participacao/construcao.py`. Cover:
  - `ordinais`: ordinals ignore gaps in `posicao`;
  - `rotulo_secao`: "Seção 4 — Título" and "Seção 13 (sem título)";
  - `rotulo_pergunta`: truncation at about 80 characters;
  - `rotulo_opcao`;
  - `TIPOS`: exactly the 4 `TipoPergunta` values with name and description;
  - `descrever_escala`:
    - with both labels: "De 1 a 5 (5 pontos). 1 = «…»; 5 = «…». Pontos intermediários
      aparecem só com o número.";
    - without the start label, saying so explicitly;
  - `destino_da_secao` / `destino_da_opcao`:
    - "segue a ordem (Seção N)" / "segue para a Seção N — …";
    - "finaliza o instrumento";
  - `localizador`: id → `Localizacao(rotulo, endereco)` for Versão, Seções, Perguntas and
    Opções, with addresses `/editor/versoes/<v>/`, `/editor/secoes/<s>/`,
    `/editor/perguntas/<q>/` and `/editor/opcoes/<o>/`;
  - `referencias_a`: encaminhamentos and Opção desvios pointing to a Seção.
- [X] T008 [P] Create `tests/editor/test_editor_acoes.py` with database tests, using own
  Pesquisa and Versão. Cover:
  - `proxima_posicao` returns `(max(posicao) or 0) + 1`, including on an empty set;
  - `mover`:
    - first item "cima" → `None`;
    - last item "baixo" → `None`;
    - middle items swap with the neighbour;
    - after `reordenar_*` with the result, positions are `1..n` with no duplicates;
  - `definir_desvio`, the full table of contracts/diagnostico.md §3:
    - same destination → no operation called, checked with a spy;
    - `None` → rule removed;
    - no rule → defined;
    - other rule → replaced;
    - **injected failure**: monkeypatch `trajetoria.instrumento.operacoes.definir_regra`
      to raise `OperacaoRejeitada` after `remover_regra`. The call raises, and
      `conteudo_da_versao` still shows the **original** rule (FR-052).

### Implementation for Foundational

- [X] T009 In `trajetoria/participacao/percurso.py`:
  - add the pure public `secoes_nao_suportadas(conteudo: ConteudoVersao) ->
    tuple[ConteudoSecao, ...]`, returning the Seções, in order, where
    `len(_com_regra(secao)) > 1`;
  - rewrite `_exigir_suporte` to build exactly the same `Violacao(Motivo.ESTRUTURA_NAO_SUPORTADA,
    "secao", f"Seção {secao.id} tem {quantas} Perguntas com regra de navegação")` from
    it;
  - add the name to `__all__`.

  No observable change: run `uv run pytest tests/participacao tests/interface` and make
  T006 pass.
- [X] T010 [P] Create `trajetoria/editor/apresentacao.py` with the pure functions of T007:
  - `Localizacao` frozen dataclass `(rotulo, endereco)`;
  - `ordinais(conteudo)`;
  - `rotulo_secao`, `rotulo_pergunta`, `rotulo_opcao`;
  - `TIPOS`;
  - `descrever_escala`;
  - `destino_da_secao`, `destino_da_opcao`;
  - `localizador`;
  - `referencias_a`.

  Input is only `trajetoria.instrumento.conteudo` values. Make T007 pass.
- [X] T011 [P] Create `trajetoria/editor/acoes.py`:
  - `proxima_posicao(conjunto)` via `aggregate(Max("posicao"))`;
  - `mover(em_ordem, elemento, direcao)` returning the swapped list or `None`;
  - `definir_desvio(pergunta, opcao, destino)` inside `transaction.atomic()`, calling only
    `op.remover_regra` and `op.definir_regra` (research R6, R7).

  No other helpers. Make T008 pass.
- [X] T012 [P] Create `trajetoria/editor/mensagens.py` with **texts only**, no universal
  mapping:
  - `BANNER`: non-productive, no authentication, access does not confer institutional
    competence to elaborate or publish (FR-003);
  - `SEMANTICA_NAVEGACAO`:
    - the desvio applies when the respondent concludes the Seção;
    - the other Perguntas of the Seção are still presented;
    - precedence: desvio, then encaminhamento, then order;
    - an optional Pergunta without answer triggers nothing;
    - "semântica atual da jornada" (FR-056; 006/DP-604);
  - `TIPO_FIXO` (FR-034);
  - `SEM_IMPEDIMENTOS`: it is not approval, homologation, authorization or publication,
    and publishing is not available in the editor (FR-071);
  - `TRABALHE_EM_COPIA`: generic recommendation (FR-100);
  - `PUBLICADA_409` (FR-095);
  - `CONFLITO`;
  - `INCOMPATIVEL_COM_A_JORNADA`;
  - `AVISOS`: the closed dict with codes `pesquisa-criada`, `versao-criada`,
    `dados-salvos`, `secao-criada`, `secao-removida`, `pergunta-criada`,
    `adicione-opcoes`, `pergunta-movida`, `pergunta-removida`, `opcao-criada`,
    `opcao-removida`, `sem-movimento`, `publicada`;
  - field texts for `DESIGNACAO_REPETIDA`, `TEXTO_VAZIO`, `OPCAO_REPETIDA`,
    `COMPLEMENTO_REPETIDO`, `ESCALA_INVALIDA`, `SECAO_COM_PERGUNTAS` and
    `SECAO_REFERENCIADA` (with `{referencias}`).
- [X] T013 [P] Create the base layout and partials:
  - `trajetoria/editor/templates/editor/base.html`:
    - `lang="pt-BR"`;
    - `<title>{% if ha_erros %}Erro: {% endif %}{% block titulo %}{% endblock %} — Editor — Trajetória Ifes</title>`;
    - "Pular para o conteúdo";
    - `role="note"` banner with `mensagens.BANNER`;
    - header "Trajetória Ifes — Editor do instrumento" with a link to `/editor/` and
      **no** Pessoa fictícia;
    - `<main id="conteudo" tabindex="-1">`;
    - inline `<style>{% include "interface/estilo.css" %}{% include "editor/estilo.css" %}</style>`;
  - `editor/estilo.css`:
    - structure list or table, compact Subir/Descer buttons and text state badges;
    - no fixed widths above 320px;
  - `_trilha.html`: `<nav aria-label="Você está em"><ol>`;
  - `_erros.html`: `role="alert"` summary with links to field ids, placed first in
    `main`. It is the **only** place in the editor that uses `role="alert"`, and it is
    rendered only together with `ha_erros=True`, so the `<title>` starts with "Erro:".
    The 008 `verificar` (T060) fails on any `role="alert"` without that prefix;
  - `_campo.html`: visible label, `aria-describedby`, `aria-invalid`, error next to the
    field (error element id `<campo>-erro`, the convention checked by `verificar`).
    Choice fields rendered as radios (`obrigatoria`, `tipo`, `desvio`, `encaminhamento`
    when shown as radios) go inside `<fieldset>` with a non-empty `<legend>` carrying
    the field label. An isolated checkbox (`complemento`, `confirmar_nome_repetido`)
    uses a wrapping or `for` label and no fieldset;
  - `_ordem.html`: Subir/Descer as separate POST forms with `csrf_token`. The visible
    text is short and `aria-label` is full, for example "Subir a Pergunta 3: …". It
    omits **only** the invalid button: no Subir on the first element and no Descer on
    the last (FR-063);
  - `aviso.html`: 409 or 404 message with a link to continue. It uses `role="status"`,
    **never** `role="alert"`, and its title has no "Erro:" prefix.
- [X] T014 Create the foundations of `trajetoria/editor/views.py`, with no route yet:
  - `_aviso(request)`: reads the closed `mensagens.AVISOS`;
  - `_exigir_rascunho(request, versao, consulta)`:
    - published + GET → `redirect(consulta + "?aviso=publicada")`;
    - published + POST → `render("editor/aviso.html", status=409)` via an internal
      `_Resposta` exception, like `trajetoria/interface/views.py`;
  - `_conflito(request, endereco)` → 409;
  - `_sem_elemento_post(request)` → 404 with "o conteúdo mudou";
  - `_aplicar_rejeicao(formulario, erro, mapa_local)`:
    - adds field or `None` errors **only** for motives in `mapa_local`;
    - re-raises otherwise;
    - `VERSAO_PUBLICADA` → 409;
    - `POSICAO_OCUPADA` / `ORDEM_INCOMPLETA` → conflict;
  - `_mover_e_voltar(...)`, shared by the three Subir/Descer views:
    - loads the current order;
    - calls `acoes.mover`;
    - `None` → `?aviso=sem-movimento`;
    - otherwise calls the given `reordenar_*` and redirects to the anchor.
  - **Anchors** must be unique on the page they target, because `verificar` rejects
    repeated ids:
    - `#secao-N` on `versao.html`;
    - `#pergunta-N` on `secao.html`;
    - `#opcao-N` on `pergunta.html`.

    On `versao.html` the Perguntas listed inside each Seção, if they carry an id, use
    the composite `s<N>-p<M>` (Seção ordinal, Pergunta ordinal), never `pergunta-M`.

**Checkpoint**: 006 exposure done, existing suites green, helpers tested. Story work can
start.

---

## Phase 3: User Story 1 — Listar Pesquisas e suas Versões (Priority: P1) 🎯 MVP

**Goal**: o operador vê as Pesquisas e, em cada uma, as Versões com o estado escrito,
a data de publicação e a origem.

**Independent Test**: com a baseline e a cópia publicada, `/editor/` lista a Pesquisa e
`/editor/pesquisas/<p>/` lista as duas Versões com "Rascunho" e "Publicada em …", sem
nenhum identificador técnico.

### Tests for User Story 1 ⚠️

- [X] T015 [P] [US1] Create `tests/editor/test_editor_pesquisas.py` with the listing
  tests:
  - `/editor/` shows each Pesquisa name and its number of Versões;
  - an empty database shows "ainda não há Pesquisas" and the create link;
  - `sem_padroes_tecnicos` holds.
- [X] T016 [P] [US1] Create `tests/editor/test_editor_versoes.py` with the listing tests
  for `/editor/pesquisas/<p>/`:
  - designation;
  - state written as "Rascunho" / "Publicada em dd/mm/aaaa";
  - origin ("criada a partir de …");
  - empty Pesquisa shows "ainda não há Versões" and the create link;
  - unknown UUID → 404.

### Implementation for User Story 1

- [X] T017 [US1] Add views `pesquisas` (`require_GET`) and `pesquisa` (`require_GET`) to
  `trajetoria/editor/views.py`, and their routes to `trajetoria/editor/urls.py`, as in
  [rotas](contracts/rotas.md#pesquisas-e-versões). Both are ORM read-only.
- [X] T018 [P] [US1] Create `trajetoria/editor/templates/editor/pesquisas.html` and
  `pesquisa.html`:
  - `h1` is the current object;
  - `_trilha.html`;
  - one action per Versão: "Abrir" and "Criar nova Versão a partir desta";
  - "Criar Versão" per Pesquisa;
  - state badges as text.

**Checkpoint**: navegação Pesquisas → Versões funcional.

---

## Phase 4: User Story 2 — Criar Pesquisa (Priority: P1)

**Goal**: criar uma Pesquisa informando só o nome.

**Independent Test**: a Pesquisa criada aparece na lista sem Versões. Nome vazio é
recusado no campo. Nome repetido pede confirmação e cria quando confirmado.

### Tests for User Story 2 ⚠️

- [X] T019 [US2] Extend `tests/editor/test_editor_pesquisas.py`:
  - the creation page asks **only** `nome`;
  - a valid POST redirects to `/editor/pesquisas/<p>/?aviso=pesquisa-criada`;
  - empty or whitespace-only `nome` → 200, field error from `TEXTO_VAZIO`, nothing
    written (`contagens()` unchanged);
  - duplicate exact name without confirmation → 200 with the warning and the "Criar mesmo
    assim" checkbox, nothing written;
  - with confirmation → created, two Pesquisas with the same name;
  - no rename or delete route exists, so `/editor/pesquisas/<p>/editar/` → 404.

### Implementation for User Story 2

- [X] T020 [US2] Add `PesquisaForm` to `trajetoria/editor/formularios.py`:
  - `nome = CharField(required=False, strip=False)`;
  - `confirmar_nome_repetido = BooleanField(required=False)` (research R11).
- [X] T021 [US2] Add the view `pesquisa_nova` (GET, POST) to `trajetoria/editor/views.py`
  and its route:
  - exact-equality duplicate check by read only;
  - `op.criar_pesquisa(nome)`;
  - local map `{TEXTO_VAZIO: "nome"}`.
- [X] T022 [P] [US2] Create `trajetoria/editor/templates/editor/formulario.html`. It is a
  generic **page** for simple forms, not a form generator, and receives:
  - `titulo`;
  - optional `introducao`;
  - optional `aviso_nome_repetido`;
  - the bound form rendered field by field with `_campo.html`;
  - `rotulo_envio`;
  - `cancelar` link.

  It includes `_erros.html` first.

---

## Phase 5: User Story 3 — Criar Versão em rascunho (Priority: P1)

**Goal**: criar uma Versão vazia em RASCUNHO numa Pesquisa.

**Independent Test**: a Versão criada aparece como "Rascunho" e sem origem. Designação
repetida é recusada no campo.

### Tests for User Story 3 ⚠️

- [X] T023 [US3] Extend `tests/editor/test_editor_versoes.py`:
  - POST `/editor/pesquisas/<p>/versoes/nova/` creates a RASCUNHO without Seções and
    redirects to `/editor/versoes/<v>/?aviso=versao-criada`;
  - repeated designation → 200 with the field message "Já existe uma Versão com esta
    designação nesta Pesquisa", nothing written;
  - empty designation → field error.

### Implementation for User Story 3

- [X] T024 [US3] Add `DesignacaoForm` (`designacao = CharField(required=False,
  strip=False)`) to `trajetoria/editor/formularios.py`.
- [X] T025 [US3] Add the view `versao_nova` (GET, POST) and its route to
  `trajetoria/editor/views.py` / `urls.py`:
  - `op.criar_versao(pesquisa, designacao)`;
  - local map `{DESIGNACAO_REPETIDA: "designacao", TEXTO_VAZIO: "designacao"}`;
  - renders `formulario.html`.

---

## Phase 6: User Story 4 — Criar nova Versão a partir de uma Versão existente (Priority: P1)

**Goal**: duplicar uma Versão, em rascunho ou publicada, pela operação da 002.

**Independent Test**: a cópia da baseline tem conteúdo equivalente
(`sem_identidades(conteudo)` igual), é RASCUNHO e mostra a origem. Depois de editar a
cópia, a origem fica intacta.

### Tests for User Story 4 ⚠️

- [X] T026 [US4] Extend `tests/editor/test_editor_versoes.py`:
  - POST `/editor/versoes/<baseline>/nova-a-partir/` with "Cópia de trabalho" creates a
    RASCUNHO in the same Pesquisa;
  - `tests/instrumento/construcao.sem_identidades` of both contents is equal;
  - the list shows "criada a partir de …";
  - from `publicada` works and leaves it intact (`retrato` equal);
  - repeated designation → field error and no partial copy (Versão count unchanged);
  - no question-to-question correspondence is shown;
  - **after** changing a Pergunta text in the copy through the editor, `retrato(baseline)`
    is unchanged.

### Implementation for User Story 4

- [X] T027 [US4] Add the view `versao_a_partir` (GET, POST) and its route:
  - `op.criar_versao_a_partir_de(origem, designacao)` only, with no element copying;
  - same local map as T025;
  - `formulario.html` with an introduction explaining that the copy is independent and
    starts as a draft.

---

## Phase 7: User Story 5 — Visualizar a estrutura de uma Versão (Priority: P1)

**Goal**: página de leitura com Seções em ordem, Perguntas resumidas, destinos e totais,
sem campos de edição.

**Independent Test**: na cópia da baseline:

- 13 Seções na ordem, incluindo uma "(sem título)";
- 54 Perguntas no total;
- tipos e obrigatoriedade escritos;
- destinos em palavras;
- nenhuma `<input>`, `<textarea>` ou `<select>`;
- nenhuma lista completa de Opções.

### Tests for User Story 5 ⚠️

- [X] T028 [P] [US5] Create `tests/editor/test_editor_estrutura.py`:
  - header shows Pesquisa, designation, "Rascunho" and origin;
  - Versão texts shown, or "sem título apresentado" / "sem texto de abertura";
  - totals "13 Seções" and "54 Perguntas";
  - each Seção shows ordinal, title or "(sem título)", number of Perguntas and
    destination text;
  - each Pergunta shows ordinal, text, type word, "Obrigatória"/"Opcional", Option count
    or scale interval, and a desvio marker;
  - the page has no `input`, `textarea` or `select`;
  - links to `/editor/secoes/<s>/` exist;
  - `django_assert_max_num_queries` bound independent of the number of Perguntas;
  - `sem_padroes_tecnicos`.

### Implementation for User Story 5

- [X] T029 [US5] Add the view `versao` (`require_GET`) and its route:
  - context from `conteudo_da_versao` plus `apresentacao` (ordinals, labels, TIPOS,
    destinations);
  - `editavel = not versao.publicada`;
  - `aviso`.
- [X] T030 [P] [US5] Create `trajetoria/editor/templates/editor/versao.html` with the
  structure as `<ol>` of Seções with nested `<ol>` of Perguntas. When `editavel`, it
  shows:
  - "Editar dados da Versão";
  - "Adicionar Seção";
  - `_ordem.html` per Seção;
  - "Remover";
  - "Diagnóstico técnico";
  - "Pré-visualizar";
  - "Criar nova Versão a partir desta";
  - `mensagens.TRABALHE_EM_COPIA`.

  Without `editavel`, only the last three.

  Ids: Seções get `id="secao-N"`. Perguntas listed inside Seções, if they carry an id,
  get the composite `id="s<N>-p<M>"`. No id repeats on the page (`verificar`).

---

## Phase 8: User Story 6 — Criar, editar, ordenar e remover Seções em rascunho (Priority: P1)

**Goal**: dados da Versão e CRUD-de-domínio das Seções, só pelas operações da 002.

**Independent Test**: numa Versão própria:

- criar três Seções (ao final);
- editar o título e apagá-lo;
- Subir e Descer, sem a ação nas pontas;
- remoção de Seção com Perguntas recusada com explicação;
- remoção de Seção referenciada recusada com a lista de referências;
- remoção de Seção vazia confirmada;
- dados da Versão alterados.

### Tests for User Story 6 ⚠️

- [X] T031 [P] [US6] Create `tests/editor/test_editor_secoes.py`:
  - **nova**: Seção at the end (`posicao == max+1`); without a title → shown "(sem
    título)", stored `None`;
  - **editar**: title changed; title cleared → `None`;
  - **subir/descer**:
    - the first has no Subir and the last no Descer (HTML);
    - a middle item swaps;
    - a forged POST "cima" on the first → `?aviso=sem-movimento` and unchanged order;
    - positions 1..n with no duplicates;
  - **remover**:
    - with Perguntas → GET shows the confirmation (no UI pre-check, so the 002 rule
      FR-061 is not duplicated in the interface); POST → 200 with the
      `SECAO_COM_PERGUNTAS` explanation and **no** "Remover" button, nothing removed;
    - referenced by an encaminhamento or a desvio → explanation lists "encaminhamento da
      Seção N" / "Opção «…» da Pergunta M da Seção N" (`referencias_a`);
    - empty → confirmation page then POST removes and redirects with
      `?aviso=secao-removida`;
  - **dados da Versão**: change designation, title, opening and closing texts; clear
    optional text → `None`; repeated designation → field error.

### Implementation for User Story 6

- [X] T032 [US6] Add to `trajetoria/editor/formularios.py`:
  - `DadosVersaoForm` (`designacao`, `titulo`, `texto_abertura`, `texto_encerramento`;
    optional empty → `None`);
  - `SecaoForm(versao, secao=None)` with `titulo`, `texto`. The encaminhamento field is
    added in US10.
- [X] T033 [US6] Add the views and routes, each calling `_exigir_rascunho` first:
  - `versao_dados` (GET, POST): `op.alterar_versao`, `formulario.html`;
  - `secao_nova` (GET, POST): `op.adicionar_secao(versao, acoes.proxima_posicao(versao.secoes.all()), titulo=, texto=)`;
  - `secao` (`require_GET`): read page;
  - `secao_editar` (GET, POST): `op.alterar_secao`;
  - `secao_mover` (`require_POST`): `_mover_e_voltar` with `op.reordenar_secoes`;
  - `secao_remover` (GET confirm, POST): `op.remover_secao`, local map
    `{SECAO_COM_PERGUNTAS, SECAO_REFERENCIADA}` with `referencias_a`.
- [X] T034 [P] [US6] Create templates in `trajetoria/editor/templates/editor/`:
  - `secao.html`: read data, destination text, Perguntas with type, obligation and
    desvio, `_ordem.html`, "Editar", "Remover", "Adicionar Pergunta"; actions only if
    `editavel`;
  - `secao_form.html`: one form;
  - `confirmar_remocao.html`: shared by Seção, Pergunta and Opção. It receives
    `elemento`, `consequencias`, `impedimentos` and `acao`. With `impedimentos` it shows
    no submit button.

---

## Phase 9: User Story 7 — Perguntas dos quatro tipos (Priority: P1)

**Goal**: criar (tipo na criação), editar sem trocar tipo, Subir/Descer, mover para
outra Seção e remover com cascata.

**Independent Test**: criar uma Pergunta de cada tipo. Só os 4 tipos são oferecidos. A
edição mostra o tipo fixo, sem campo. Mover para outra Seção mantém Opções e desvios.
Remover leva Opções e desvios.

### Tests for User Story 7 ⚠️

- [X] T035 [P] [US7] Create `tests/editor/test_editor_perguntas.py`:
  - the type step lists **exactly** the 4 `TipoPergunta` with descriptions;
  - `?tipo=DATA` or any other value → back to the type step, no write;
  - create each type at the end of the Seção:
    - escolha → redirect to the Pergunta with `?aviso=adicione-opcoes`;
    - escala needs limits, here valid;
  - the edit page has **no** `tipo` field and shows `mensagens.TIPO_FIXO`;
  - edit text, explanatory text (cleared → `None`) and "Obrigatória"/"Opcional" (text
    shown);
  - empty text → field error `TEXTO_VAZIO`;
  - POST without choosing "Obrigatória"/"Opcional" (field absent) → 200 with a field
    error on `obrigatoria` ("Indique se a Pergunta é obrigatória ou opcional"),
    **no** 500 and nothing written;
  - Subir/Descer, including the ends;
  - **mover para outra Seção** (`/trocar-secao/`):
    - the select lists the other Seções of the same Versão only;
    - the Pergunta goes to the end of the destination with its Options and desvios;
    - it leaves the origin;
  - **remover**: the confirmation cites Options, scale and desvios; after the POST
    nothing of it remains;
  - no route to change the type exists.

### Implementation for User Story 7

- [X] T036 [US7] Add to `trajetoria/editor/formularios.py`:
  - `TipoPerguntaForm`, `tipo` radio with `TipoPergunta.choices`;
  - `PerguntaForm(tipo, ...)`:
    - `texto`, `texto_explicativo`;
    - `obrigatoria` as `ChoiceField(required=True)` with the choices "Obrigatória" and
      "Opcional", radios in `fieldset`/`legend`, converted to `bool` in `clean`.
      `required=True` here is **input conversion**: the 002 operation demands a `bool`
      and raises `TypeError` otherwise. It is not a domain rule. In edit mode the
      initial value is the current one. In create mode there is no preselection. The
      message is "Indique se a Pergunta é obrigatória ou opcional";
    - **only when** `tipo == ESCALA`, also `inicio`, `fim` as
      `IntegerField(required=False)` and `rotulo_inicio`, `rotulo_fim`;
    - `escala()` builds `trajetoria.instrumento.conteudo.Escala`;
  - `MoverPerguntaForm(pergunta)`: `secao` choices = other Seções of the Versão, value
    UUID, label = `rotulo_secao`.
- [X] T037 [US7] Add the views and routes, each calling `_exigir_rascunho` first:
  - `pergunta_nova`:
    - GET without `tipo` → `pergunta_tipo.html`;
    - GET/POST with a valid `tipo` → `op.adicionar_pergunta(secao, acoes.proxima_posicao(secao.perguntas.all()), tipo, texto, obrigatoria=, texto_explicativo=, escala=)`;
    - local map `{TEXTO_VAZIO: "texto", ESCALA_INVALIDA: "inicio"}`;
  - `pergunta` (`require_GET`);
  - `pergunta_editar`: `op.alterar_pergunta`, with no type argument;
  - `pergunta_mover`: `_mover_e_voltar` with `op.reordenar_perguntas`;
  - `pergunta_trocar_secao`: `op.mover_pergunta(pergunta, destino, acoes.proxima_posicao(destino.perguntas.all()))`,
    `formulario.html`;
  - `pergunta_remover`: `op.remover_pergunta`.
- [X] T038 [P] [US7] Create templates:
  - `pergunta_tipo.html`: one GET form with the 4 radios in a `fieldset`/`legend`;
  - `pergunta_form.html`: fixed type shown as text with `TIPO_FIXO` in edit mode; scale
    fields only for escala;
  - `pergunta.html`: read data; the Options list for choice types (filled in US8); scale
    explanation for escala (US9); actions only if `editavel`.

---

## Phase 10: User Story 8 — Opções e complemento (Priority: P1)

**Goal**: adicionar, editar, Subir/Descer e remover Opções de Perguntas de escolha;
complemento único.

**Independent Test**: numa Pergunta de escolha múltipla:

- quatro Opções;
- complemento na última;
- segundo complemento recusado com orientação;
- texto repetido recusado;
- reordenar;
- remover com desvio.

Em texto curto e escala não há ações de Opção.

### Tests for User Story 8 ⚠️

- [X] T039 [P] [US8] Create `tests/editor/test_editor_opcoes.py`:
  - add at the end;
  - "Adicionar e incluir outra" → back to `opcoes/nova/?aviso=opcao-criada`;
  - edit text, keeping the desvio (arranged via `op.definir_regra`) and the complement;
  - text stored exactly as typed, for example "Outro:" without trimming the colon;
  - repeated text → field message `OPCAO_REPETIDA`;
  - complement mark and unmark; a second complement → field message telling to unmark
    the current one first; the Pergunta page indicates which Option accepts complement;
  - Subir/Descer, including the ends;
  - remove with desvio → the confirmation cites the desvio, after POST it is gone;
  - for texto curto and escala:
    - the Pergunta page shows no Option actions;
    - `/editor/perguntas/<q>/opcoes/nova/` → 404;
  - no Option count limit is enforced.

### Implementation for User Story 8

- [X] T040 [US8] Add `OpcaoForm(pergunta, opcao=None)` to `trajetoria/editor/formularios.py`:
  - `texto`;
  - `complemento = BooleanField(required=False)`;
  - two submit names: `adicionar` and `adicionar_outra`.

  The `desvio` field is added in US10.
- [X] T041 [US8] Add the views and routes, each calling `_exigir_rascunho` first:
  - `opcao_nova`:
    - 404 unless the Pergunta type is `ESCOLHA_UNICA` or `ESCOLHA_MULTIPLA`;
    - `op.adicionar_opcao(pergunta, acoes.proxima_posicao(pergunta.opcoes.all()), texto, complemento_textual=)`;
  - `opcao_editar`: `op.alterar_opcao`;
  - local map for both: `{TEXTO_VAZIO: "texto", OPCAO_REPETIDA: "texto",
    COMPLEMENTO_REPETIDO: "complemento"}`;
  - `opcao_mover`: `_mover_e_voltar` with `op.reordenar_opcoes`;
  - `opcao_remover`: `op.remover_opcao`.
- [X] T042 [P] [US8] Create `trajetoria/editor/templates/editor/opcao_form.html`, a single
  form, and fill the Options list in `pergunta.html`:
  - per Option: text, "aceita complemento escrito", desvio text, `_ordem.html`,
    "Editar", "Remover";
  - "Adicionar Opção" only for choice types and only if `editavel`.

---

## Phase 11: User Story 9 — Configurar escala (Priority: P1)

**Goal**: configurar limites e rótulos da escala e explicá-los.

**Independent Test**: escala 1–5 com rótulos explicada. 5→1, 3→3, não inteiro e vazio
recusados no campo, com valores preservados. Sem rótulo inicial, a explicação diz isso.

### Tests for User Story 9 ⚠️

- [X] T043 [P] [US9] Create `tests/editor/test_editor_escala.py`:
  - the explanation on the Pergunta page and the edit page matches `descrever_escala`;
  - edit changes the limits;
  - start ≥ end → field `inicio` gets the `ESCALA_INVALIDA` text, the previous scale is
    kept and the typed values are kept;
  - non-integer → field error from the `IntegerField` conversion;
  - empty limit → `ESCALA_INVALIDA` from the 002;
  - start label removed → explanation says "sem rótulo";
  - the form has no intermediate-label, weight or appearance fields;
  - negative integers are accepted.

### Implementation for User Story 9

- [X] T044 [US9] In `trajetoria/editor/views.py`:
  - `pergunta_editar` passes `escala=` only for escala;
  - add `ESCALA_INVALIDA: "inicio"` to its local map;
  - both views put `descrever_escala` in the context.

  Render the explanation in `pergunta.html` and `pergunta_form.html` (FR-049).

---

## Phase 12: User Story 10 — Navegação já suportada (Priority: P1)

**Goal**: encaminhamento de Seção e desvio por Opção de escolha única, com troca
tudo-ou-nada e a explicação da semântica atual.

**Independent Test**: cenário A/B/C da spec.

- "Não → Seção C" e "Sim" sem desvio aparecem na estrutura.
- Trocar o desvio de C para finalizar é uma ação.
- Escolha múltipla, texto e escala não oferecem desvio.

### Tests for User Story 10 ⚠️

- [X] T045 [P] [US10] Create `tests/editor/test_editor_navegacao.py`:
  - desvio choices for escolha única = "sem desvio", every Seção of the Versão (labels
    by ordinal, **no** position filter) and "finalizar o instrumento";
  - set → Seção, set → finalizar, set → sem desvio;
  - **replace** Seção C → finalizar in one POST;
  - **atomic replace** through the view: monkeypatch `op.definir_regra` to raise → the
    view does not leave the Option without its original desvio (`retrato` unchanged)
    and the error propagates, because the motive is unmapped;
  - escolha múltipla, texto and escala pages/forms have no `desvio` field and show the
    "só escolha única" explanation;
  - encaminhamento:
    - set to Seção N → "segue para a Seção N" on structure and Seção pages;
    - "seguir a ordem" → `None`;
    - the Seção itself is not listed;
  - `mensagens.SEMANTICA_NAVEGACAO` shown on the Option and Seção forms;
  - a second Pergunta with a desvio in the same Seção is accepted by the editor (written);
  - a backward destination is accepted (written);
  - no condition editor, priority or timing field in any form.

### Implementation for User Story 10

- [X] T046 [US10] In `trajetoria/editor/formularios.py`:
  - add `encaminhamento` to `SecaoForm`: choices "seguir a ordem" plus the other Seções
    by ordinal and UUID value;
  - add `desvio` to `OpcaoForm` **only** when the Pergunta is `ESCOLHA_UNICA`: "sem",
    "finalizar", plus every Seção UUID;
  - add the converters `destino()` → `Secao | FINALIZAR | None`.
- [X] T047 [US10] In `trajetoria/editor/views.py`:
  - `secao_nova` and `secao_editar` call `op.definir_encaminhamento` in the **same**
    `transaction.atomic()` as `adicionar_secao` / `alterar_secao`;
  - `opcao_nova` and `opcao_editar` call `acoes.definir_desvio` in the **same**
    `transaction.atomic()` as `adicionar_opcao` / `alterar_opcao`.
- [X] T048 [P] [US10] Render `mensagens.SEMANTICA_NAVEGACAO` and the destination texts
  (`destino_da_secao`, `destino_da_opcao`) in `secao_form.html`, `opcao_form.html`,
  `secao.html`, `pergunta.html` and `versao.html`.

---

## Phase 13: User Story 11 — Diagnóstico técnico (Priority: P1)

**Goal**: diagnóstico A (002) e B (006) com **todos os problemas concretos**, acionáveis
e localizados. As três situações são derivadas. Nada é persistido.

**Independent Test**:

- Um rascunho com um problema de cada tipo mostra todos, separados em A e B, com o
  texto "onde + o que corrigir" e links.
- Corrigindo por operações reais, o diagnóstico seguinte muda.
- "Sem impedimentos técnicos conhecidos" implica `publicar` aceita (no teste) e
  `secoes_nao_suportadas == ()`.

### Tests for User Story 11 ⚠️

- [X] T049 [P] [US11] Create `tests/editor/test_editor_diagnostico.py`:
  - **unit, `diagnosticar`**:
    - A has **one `Problema` per `Violacao`** of the real `verificar_completude` on the
      same Versão, in the same order, with `causa` equal to its `motivo`;
    - B has one per Seção of `secoes_nao_suportadas`, with `causa is participacao.regras.Motivo.ESTRUTURA_NAO_SUPORTADA`;
    - the booleans are derived (`estrutura_valida == (not estrutura)`);
    - **no replica**: the test compares with the real 002 call, never with a hand-written
      list of rules;
  - **cases**:
    - Versão without Seções;
    - Seção without Perguntas;
    - choice Pergunta with 1 Option, text like "A Pergunta «…» (Pergunta N da Seção M)
      precisa ter pelo menos duas Opções.";
    - encaminhamento to an earlier Seção;
    - desvio to its own Seção;
    - two Perguntas with desvio in one Seção (B);
  - **both at once**: all of them listed in one GET, A before B;
  - **three situations**:
    - "Com problemas de estrutura";
    - "Estrutura válida, mas incompatível com a jornada atual";
    - "Sem impedimentos técnicos conhecidos" plus `mensagens.SEM_IMPEDIMENTOS`;
  - **correction and recalculation**: add the missing Option and remove the second desvio
    through editor POSTs → the next GET no longer lists them;
  - **no write**: `retrato` and `contagens()` equal before and after the GET;
  - **coherence**: in the favourable case, `op.publicar(versao)` in the test does not
    raise and `secoes_nao_suportadas(conteudo_da_versao(versao)) == ()`;
  - **no approval language**: the visible text never contains "pronta para publicação",
    "aprovada", "homologada" or "autorizada" (except inside the negation of
    `SEM_IMPEDIMENTOS`, asserted literally);
  - each problem links to the element page;
  - published Versão → `/diagnostico/` redirects with `?aviso=publicada`;
  - `sem_padroes_tecnicos`.

### Implementation for User Story 11

- [X] T050 [US11] Create `trajetoria/editor/diagnostico.py`:
  - `Problema` frozen dataclass `(origem, causa, elemento: Localizacao, texto)`;
  - `Diagnostico` frozen dataclass with `estrutura: tuple[Problema, ...]`,
    `jornada: tuple[Problema, ...]` and the properties `estrutura_valida`,
    `compativel_com_jornada`, `sem_impedimentos_conhecidos`;
  - `diagnosticar(versao)`, which reads `conteudo_da_versao` once, calls
    `verificar_completude(versao)` and `secoes_nao_suportadas(conteudo)`, and builds the
    texts with a **local** map of the 5 completude motives (`SEM_SECOES`,
    `SECAO_SEM_PERGUNTAS`, `OPCOES_INSUFICIENTES`, `DESTINO_NAO_POSTERIOR`,
    `REFERENCIA_OUTRA_VERSAO`) composed with the element label.

  There is no enum, no persistence and no other source (contracts/diagnostico.md §2).
- [X] T051 [US11] Add the view `diagnostico` (`require_GET`) and its route; published →
  302 `?aviso=publicada`. Call `diagnosticar` also in `versao` (rascunho only), `secao`
  and `pergunta` for the per-element marks (FR-074).
- [X] T052 [P] [US11] Create `trajetoria/editor/templates/editor/_diagnostico.html` and
  `diagnostico.html`:
  - "Estrutura válida" section listing every A problem (`texto` plus link to
    `elemento.endereco`) or "nenhum problema de estrutura";
  - "Compatível com a jornada atual" section with B or "nenhuma incompatibilidade",
    plus `SEMANTICA_NAVEGACAO`;
  - the derived situation, plus `SEM_IMPEDIMENTOS` in the favourable case;
  - `causa` never rendered;
  - include the summary partial in `versao.html` and add the text marks
    "Problema: …" in `versao.html`, `secao.html` and `pergunta.html`;
  - **no `role="alert"`** in the diagnóstico, the summary or the marks, because they are
    not form errors and the title has no "Erro:" prefix. Use plain headings and lists,
    or `role="status"` for the situation line. This keeps T060 (`verificar`) green.

---

## Phase 14: User Story 12 — Versão publicada somente leitura (Priority: P2)

**Goal**: consultar a publicada sem nenhum controle de edição, com recusa no servidor e a
002 como proteção definitiva.

**Independent Test**:

- **UI**: nenhuma ação de edição em nenhuma página da publicada.
- **Servidor**: POST direto em **cada** rota de escrita → 409, operação **não chamada**,
  retrato igual.
- **Domínio**: com o guard da view desativado, a 002 ainda recusa.

### Tests for User Story 12 ⚠️

- [X] T053 [P] [US12] Create `tests/editor/test_editor_publicada.py`:
  - **UI**:
    - the Versão, Seção and Pergunta pages of `publicada` contain no form or link for
      editar, remover, Subir/Descer, adicionar, desvio, encaminhamento, complemento or
      diagnóstico;
    - they show "Publicada em … — não pode ser alterada", "Pré-visualizar" and "Criar
      nova Versão a partir desta";
  - **GET** of each form page (dados, secoes/nova, secoes/<s>/editar, remover pages,
    perguntas/nova, perguntas/<q>/editar, trocar-secao, opcoes/nova, opcoes/<o>/) → 302
    with `?aviso=publicada`;
  - **server**: for **every** write route of contracts/rotas.md, POST with valid data →
    409 with `mensagens.PUBLICADA_409`, a spy on every `trajetoria.instrumento.operacoes`
    write function records **zero** calls, and `retrato(publicada)` is equal;
  - **domain**: monkeypatch `trajetoria.editor.views._exigir_rascunho` to a no-op, then
    POST to edit a Pergunta → the 002 rejects `VERSAO_PUBLICADA`, the view shows 409,
    and `retrato` is equal;
  - no despublicar, corrigir or "editar mesmo assim" text anywhere.

### Implementation for User Story 12

- [X] T054 [US12] Review every write view in `trajetoria/editor/views.py`:
  - each calls `_exigir_rascunho` before any form binding or operation;
  - every template uses `editavel` to hide actions;
  - fix any gap found by T053.

  No new behavior beyond research R12.

---

## Phase 15: User Story 13 — Pré-visualizar a Versão (Priority: P2)

**Goal**: prévia de leitura, uma Seção por página, com os controles por tipo da 008,
anotações estruturais e navegação por links GET na ordem. Não é jornada.

**Independent Test**: percorrer a prévia inteira da cópia da baseline:

- controles por tipo e anotações aparecem;
- não há `<form>` nem botão de envio;
- anterior e próxima seguem a ordem, mesmo onde um desvio apontaria para outra Seção;
- nada é escrito nem contado;
- `concluir` e `percorrer` nunca são chamados.

### Tests for User Story 13 ⚠️

- [X] T055 [P] [US13] Create `tests/editor/test_editor_previa.py`:
  - `/previa/`: title, opening text, Seção index links and closing text, plus the
    permanent "Pré-visualização — nada é gravado; os desvios não são executados";
    `<title>` and `h1` start with "Pré-visualização";
  - `/previa/secoes/<n>/` for each ordinal of the copy:
    - controls per type: radio or `select` above `LIMITE_RADIOS`, checkboxes, text,
      scale points with end labels;
    - **no `<form>`** and no `type="submit"`;
    - annotation "Se «Não» for escolhida na aplicação real, a próxima seção será: …" /
      "…, o instrumento é finalizado" and the Seção encaminhamento annotation;
    - previous and next links are `<a href>` to `n-1` / `n+1` (**structural order**),
      including on a Seção whose desvio points elsewhere;
    - an untitled Seção is rendered with a coherent heading;
    - out-of-range `n` → 404;
  - **read-only**:
    - `retrato(copia)` and `contagens()` (Pesquisa, Versão, Seção, Pergunta, Opção,
      Campanha, Participação, Resposta and all others) are equal before and after
      visiting every preview page;
    - monkeypatch `trajetoria.participacao.operacoes.concluir`,
      `trajetoria.participacao.percurso.percorrer` and
      `trajetoria.participacao.consultas.situacao_da_jornada` to raise if called;
    - no cookie is set by the responses;
  - works for `publicada` too;
  - no Pessoa fictícia in the header.

### Implementation for User Story 13

- [X] T056 [US13] Add the views `previa` and `previa_secao` (`require_GET`) and their
  routes:
  - `previa_secao` takes the `n`-th Seção by order from `conteudo_da_versao` and builds
    `FormularioDaSecao(secao, {}).itens()` (008);
  - annotations come from `apresentacao.destino_da_opcao` / `destino_da_secao`;
  - previous and next are `n-1` / `n+1` only;
  - there is no cursor, cookie, session or state parameter, and nothing from the 006 is
    used (research R13).
- [X] T057 [P] [US13] Create `trajetoria/editor/templates/editor/previa.html` and
  `previa_secao.html`:
  - per-item dispatch on `item.modo`, the same as
    `trajetoria/interface/templates/interface/secao.html`, including
    `interface/perguntas/{texto_curto,escolha_unica,escolha_multipla,escala}.html`;
  - **outside any `<form>`**;
  - the annotations as a list under each Pergunta;
  - the permanent preview notice;
  - "Seção anterior/seguinte na ordem" links;
  - "Voltar à estrutura".

---

## Phase 16: User Story 14 — Problemas e recusas em linguagem operacional (Priority: P2)

**Goal**: recusas no campo ou no topo, conflito explicado, falha inesperada continua
sendo erro.

**Independent Test**:

- formulário recusado volta com o resumo no topo, o erro junto ao campo e os valores
  preservados;
- conflito concorrente → 409 com `CONFLITO`;
- motivo não mapeado e exceção inesperada propagam (500), sem virar mensagem de
  validação.

### Tests for User Story 14 ⚠️

- [X] T058 [P] [US14] Create `tests/editor/test_editor_erros.py`:
  - **refused form**, for example a repeated Option:
    - `_erros.html` is the first child of `main`;
    - the error is next to the field with `aria-invalid` and `aria-describedby`;
    - the typed values are preserved;
    - the `<title>` starts with "Erro:";
  - **conflict**:
    - Subir with `trajetoria.instrumento.operacoes.reordenar_secoes` monkeypatched
      to raise `OperacaoRejeitada((Violacao(Motivo.ORDEM_INCOMPLETA, None, ""),))`,
      simulating a concurrent change inside the same request, → 409 `CONFLITO`, and the
      order is unchanged. `_mover_e_voltar` reads the current order in the POST itself,
      so an element added **before** the POST does not produce a conflict; the test
      must not rely on that;
    - Seção creation with `trajetoria.editor.acoes.proxima_posicao` monkeypatched to
      return an occupied position, which the real `adicionar_secao` rejects with
      `POSICAO_OCUPADA`, → 409 `CONFLITO`, and the Seção count is unchanged;
  - POST to a removed element → 404 with "o conteúdo mudou";
  - **unmapped motive**: monkeypatch an operation to raise
    `OperacaoRejeitada(TIPO_NAO_SUPORTADO)` → the exception propagates
    (`client.raise_request_exception=False` → 500), **not** a 200 with a field
    message;
  - **unexpected exception** (`RuntimeError`) → 500 with the 008 page, no traceback in
    the body;
  - `sem_padroes_tecnicos` on every response above.

### Implementation for User Story 14

- [X] T059 [US14] Adjust `trajetoria/editor/views.py` and `_erros.html` until T058 passes:
  - the local maps stay local and small;
  - `_aplicar_rejeicao` re-raises unmapped motives;
  - there is no catch-all `except Exception`.

---

## Phase 17: User Story 15 — Acessibilidade e responsividade básicas (Priority: P3)

**Goal**: estrutura acessível em todas as telas do editor.

**Independent Test**: a verificação estrutural da 008 (`verificar`) passa em todas as
telas, inclusive com erro. Subir, Descer e Remover têm nomes acessíveis completos. Os
estados aparecem em texto.

### Tests for User Story 15 ⚠️

- [X] T060 [P] [US15] Create `tests/editor/test_editor_acessibilidade.py`:
  - import `verificar` from `tests.interface.test_interface_acessibilidade`, without
    changing that file;
  - run it on every editor page, both draft and published variants, plus one form with
    errors, the diagnóstico in each situation, both preview pages and `aviso.html`;
  - every `_ordem.html` button has an `aria-label` naming the element and direction;
  - every removal link names the element;
  - "Rascunho", "Publicada", "Obrigatória" and "Opcional" appear as text;
  - one `h1` per page;
  - the trail `nav[aria-label="Você está em"]` is present.

### Implementation for User Story 15

- [X] T061 [US15] Fix templates and `editor/estilo.css` until T060 passes:
  - no fixed widths above 320px;
  - focus inherited from `interface/estilo.css`;
  - touch targets at least 44px for Subir, Descer and Remover.

  No redesign of the 008 and no second UX audit.

---

## Phase 18: Aceitação ponta a ponta, baseline, acesso e fronteiras

**Purpose**: os cenários da spec por HTTP e as invariantes estruturais (SC-001, SC-002,
SC-008, SC-010, SC-011, SC-013, FR-009, FR-076, FR-107).

- [X] T062 [P] Create `tests/editor/test_editor_aceitacao.py`:
  - **`test_cenario_principal`**: the 14 steps of spec "Cenários ponta a ponta" **only via
    `client`**:
    - list;
    - open the Pesquisa;
    - open the baseline structure, GET only;
    - create "Cópia de trabalho";
    - change a Pergunta text;
    - add an escolha única Pergunta;
    - add 2 Options;
    - Subir the Pergunta and swap the Options;
    - "Obrigatória";
    - structure and preview;
    - diagnóstico;
    - add a choice Pergunta without Options, see the A problem, fix it;
    - "Sem impedimentos técnicos conhecidos";
    - open `publicada` and get 409 on a write POST.

    At the end: `materializar()` returns `criada=False` without raising, no new
    Campanha, and `Versao.objects.filter(estado="PUBLICADA").count()` unchanged.
  - **`test_cenario_navegacao`**: A/B/C plus problems (a) and (b) and undo, as in the
    quickstart E2E-2.
  - **`test_duas_acoes_ate_qualquer_pergunta`** (SC-011): from the copy structure page,
    every Pergunta page is reachable via the Seção link then the Pergunta link.
- [X] T063 [P] Create `tests/editor/test_editor_baseline.py`:
  - the baseline structure page offers edit controls exactly like any draft (GET only,
    no POST), with **no** name-based protection;
  - after the editor flows on a copy, `materializar()` returns `criada=False` without
    `BaselineDivergente`;
  - no source file under `trajetoria/editor/` contains:
    - the baseline Pesquisa name or designation;
    - `\bQ\d{1,2}\b`;
    - any text of at least 12 characters from `trajetoria.formulario_2024.declaracao`.
- [X] T064 [P] Create `tests/editor/test_editor_acesso.py`:
  - **all routes** (SC-013), in a **single** test function, no per-route
    parametrization:
    - iterate `trajetoria.editor.urls.urlpatterns`;
    - build each path with a random UUID for `<uuid:…>` converters and `1` for
      `<int:…>`;
    - with `settings.TRAJETORIA_DEMONSTRACAO = False`, assert 404 for GET and POST on
      every path;
    - no database arrangement is needed, because the middleware answers before
      resolving the URL;
  - **control**: with the mode on, one representative GET per family (`/editor/`,
    Pesquisa, Versão, Seção, Pergunta, Opção, diagnóstico, prévia, using real objects) →
    200;
  - the banner text is present;
  - no `pessoa_demonstracao` name in the header even with the demo cookie set.

  The gate is central (middleware). The loop covers every route at once, without
  multiplying tests.
- [X] T065 [P] Create `tests/editor/test_editor_fronteiras.py`:
  - **imports**, via `ast`, of every `.py` in `trajetoria/editor/` ⊆ the allowed table of
    the plan ("Desenho → Camadas");
  - no `publicar` and no `renomear_pesquisa` name anywhere;
  - no `\.(save|create|update|delete|bulk_\w+)\(`;
  - no `models.py`, and `apps.get_app_config("editor").get_models() == []`;
  - `call_command("makemigrations", "--check", "--dry-run")` passes;
  - no `<script` and no external `src`/`href` in the editor templates;
  - `pyproject.toml` dependencies unchanged;
  - **CSRF**: `Client(enforce_csrf_checks=True)` POST to one route per write family →
    403;
  - no route path contains `publicar`, `despublicar`, `aprovar`, `homologar`, `api`,
    `exportar`, `importar`, `campanha`, `excluir` or `apagar`;
  - **no deletion of Pesquisa or Versão** (FR-010): no pattern whose path starts with
    `pesquisas/<uuid:…>/` or `versoes/<uuid:…>/` ends in `remover/`. `remover/` exists
    only under `secoes/`, `perguntas/` and `opcoes/`;
  - no `renomear` or `editar` route under `pesquisas/` (FR-011);
  - no class named like `*View` subclassing a generic CRUD view, and no `ModelForm` in
    `formularios.py`.

---

## Phase 19: Polish & Cross-Cutting Concerns

**Purpose**: documentação, validação final e Definition of Done.

- [X] T066 [P] Add one line to `README.md` pointing to
  `specs/009-editor-pesquisa-versao/quickstart.md`. The line states that:
  - the editor exists only in the local non-productive mode (`TRAJETORIA_DEMONSTRACAO=1`);
  - it **must not be enabled in a productive environment before Feature 010** defines
    governance, roles and authorization (spec FR-006; DP-901);
  - it does not publish;
  - access to it is not institutional authorization.
- [X] T067 Run the full validation and fix any failure in the module that caused it:
  - `uv run pytest`: every 001–008 suite stays green **without editing existing tests**;
    only the new 006 test was added;
  - `uv run ruff check .`;
  - `uv run python manage.py check`;
  - `uv run python manage.py makemigrations --check --dry-run`.
- [X] T068 Walk the manual quickstart (E2E-1, E2E-2, "Outras situações", accessibility at
  320px and 200% zoom, JavaScript disabled) in `specs/009-editor-pesquisa-versao/quickstart.md`
  and record any deviation as a fix in the responsible template or view.
- [X] T069 Definition of Done review against `.specify/memory/constitution.md`:
  - 0 models and 0 migrations;
  - 002 untouched; 006 change limited to `secoes_nao_suportadas`; 008 only reused and
    the docstring;
  - no publish path;
  - no persisted diagnosis;
  - baseline untouched;
  - over-engineering list absent: no CRUD framework, form builder, state machine,
    approval, PublicationRequest, graph editor, API, SPA, autosave, edit history or
    semantic diff;
  - every DECISÃO PENDENTE (DP-901–DP-903, 002/DP-001–DP-007, 003/DP-307, 006/DP-604,
    008/DP-801) is still pending and not implemented implicitly.

  Record the result in the PR description.

---

## Notas de implementação (divergências registradas)

- **Templates de formulário consolidados (YAGNI)**: Seção (nova/editar), Pergunta
  (nova/editar), Opção (nova/editar), mover Pergunta, dados da Versão, nova Versão e nova
  Pesquisa usam o mesmo `formulario.html` (uma página, um `<form>`, um envio + envio extra
  opcional). As explicações (tipo fixo, escala atual, semântica de navegação, só escolha
  única) entram como parágrafos de introdução. `secao_form.html`, `pergunta_form.html` e
  `opcao_form.html` (T034, T038, T042) não foram criados.
- **Checkbox isolado em `fieldset`/`legend`** (T013): a verificação estrutural herdada da
  008 (`verificar`, inalterada) exige grupo para todo checkbox; o rótulo do campo vira a
  `legend` e a opção é "Sim".
- **Remoção de Seção sem pré-verificação na interface** (T031, T033): a regra de remoção
  é da 002 (FR-061); a interface mostra a confirmação e explica a recusa da 002 depois do
  POST, sem botão "Remover".
- **Botões Subir/Descer** usam `name="direcao"` no próprio `<button>` (sem campo oculto).
- **Ajuste de CSS** durante o roteiro manual (T068): `.lista-acoes` alinha verticalmente
  links e botões.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: imediato.
- **Foundational (Phase 2)**: depende do Setup e **bloqueia** todas as histórias.
  - T009 (006) depende de T006.
  - T010, T011, T012 e T013 são independentes entre si.
  - T014 depende de T011, T012 e T013.
- **US1 → US2 → US3 → US4**: compartilham `views.py`, `urls.py`, `formularios.py`,
  `formulario.html` e `test_editor_versoes.py` e `test_editor_pesquisas.py`. Ficam em
  sequência.
- **US5** depende de US3, porque precisa de Versão criável.
- **US6** depende de US5.
- **US7** depende de US6.
- **US8** depende de US7.
- **US9** depende de US7.
- **US10** depende de US6 e US8.
- **US11** depende de US5, mais US6–US10 para os cenários de correção.
- **US12** depende de todas as views de escrita: US2–US10.
- **US13** depende de US5. Os testes usam a cópia da baseline.
- **US14** depende de US6–US8, cujas views são exercitadas.
- **US15** depende de todas as telas.
- **Phase 18** depende de US1–US15. **Phase 19** vem por último.

### User Story Dependencies

As histórias formam uma cadeia natural, porque cada nível do editor (Pesquisa → Versão
→ Seção → Pergunta → Opção) é navegado a partir do anterior. Ainda assim, cada uma é
**testável isoladamente**: os testes arranjam o estado pelas operações da 002 (via
`construcao_editor`), sem depender das views de outra história.

### Within Each User Story

- O teste vem antes: ele DEVE falhar primeiro quando o comportamento é novo.
- Depois: formulário, depois view e rota, depois template.
- Um arquivo por vez para `views.py`, `urls.py` e `formularios.py`.

### Parallel Opportunities

- **Setup**: T003, T004 e T005.
- **Foundational**:
  - testes T006, T007 e T008;
  - implementações T010, T011, T012 e T013, depois de T009, ou em paralelo, porque são
    arquivos diferentes.
- **Em cada história**: o arquivo de teste [P] e o template [P] podem ser escritos em
  paralelo com a view.
- **Phase 18**: T062, T063, T064 e T065, todos arquivos novos.

---

## Parallel Example: Foundational

```bash
Task: "T006 test_secoes_nao_suportadas_publica in tests/participacao/test_jornada_percurso.py"
Task: "T007 pure presentation tests in tests/editor/test_editor_apresentacao.py"
Task: "T008 action helper tests in tests/editor/test_editor_acoes.py"
Task: "T012 texts in trajetoria/editor/mensagens.py"
Task: "T013 base layout and partials in trajetoria/editor/templates/editor/"
```

## Parallel Example: User Story 11

```bash
Task: "T049 diagnosis tests in tests/editor/test_editor_diagnostico.py"
Task: "T052 _diagnostico.html and diagnostico.html templates"
# then, sequentially: T050 diagnostico.py → T051 view/route in views.py/urls.py
```

## Parallel Example: Phase 18

```bash
Task: "T062 tests/editor/test_editor_aceitacao.py"
Task: "T063 tests/editor/test_editor_baseline.py"
Task: "T064 tests/editor/test_editor_acesso.py"
Task: "T065 tests/editor/test_editor_fronteiras.py"
```

---

## Implementation Strategy

### MVP First

1. Fases 1–2: app montado, extração da 006, helpers.
2. US1–US5: listar, criar Pesquisa e Versão, duplicar, ver a estrutura. É o editor
   **de leitura e duplicação**, já útil para consultar a baseline e criar cópias.
3. **STOP and VALIDATE**: `uv run pytest tests/editor tests/participacao`.

### Incremental Delivery

1. Edição estrutural: US6 Seções → US7 Perguntas → US8 Opções → US9 Escala → US10
   Navegação.
2. US11 Diagnóstico: a primeira versão "compor e verificar" completa.
3. US12 Publicada blindada → US13 Prévia → US14 Erros → US15 Acessibilidade.
4. Aceitação, fronteiras e polish.

---

## Decisões Pendentes preservadas

Nenhuma tarefa resolve, implementa ou contorna:

- **DP-901**: competência de elaboração; acesso só não produtivo.
- **DP-902**: estatuto da baseline; rascunho comum, sem exceção.
- **DP-903**: autoria e histórico; nenhum.
- **002/DP-001**: quem publica; o editor não publica.
- **002/DP-002**: fluxo de aprovação; sem estados intermediários.
- **002/DP-003**: correção pós-publicação; imutável.
- **002/DP-004**: melhorias metodológicas.
- **002/DP-005**: tipos e capacidades; só os 4 tipos.
- **002/DP-006**: comparabilidade; só a origem.
- **002/DP-007**: consentimento; Q1 é conteúdo comum.
- **003/DP-307**: Q10–Q19 inalteradas.
- **006/DP-604**: semântica explicada como "atual".
- **008/DP-801**: linguagem e identidade visual neutras.

## Notes

- [P] = arquivos diferentes, sem dependência pendente.
- Os testes da 001–008 **não são editados**. O único teste acrescentado fora de
  `tests/editor/` é T006, na 006.
- Commits por fase ou grupo lógico.
- Pare em qualquer checkpoint para validar a história isoladamente.
- Se alguma tarefa parecer exigir modelo, migração, CRUD genérico, form builder, máquina
  de estados, aprovação, pedido de publicação, editor de grafo, API, SPA, autosave,
  histórico ou diff semântico, **pare** e volte ao plan com a justificativa.
