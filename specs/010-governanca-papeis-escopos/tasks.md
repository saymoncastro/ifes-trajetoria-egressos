---

description: "Tasks da Feature 010 — Governança, papéis e escopos institucionais"
---

# Tasks: Governança, papéis e escopos institucionais

**Input**: design documents de `specs/010-governanca-papeis-escopos/`.

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/governanca.md](contracts/governanca.md),
[contracts/acesso-editor.md](contracts/acesso-editor.md),
[contracts/demonstracao-operador.md](contracts/demonstracao-operador.md),
[quickstart.md](quickstart.md).

**Stack** (confirmada; [ADR 0001](../../docs/adr/0001-stack-inicial.md)):

- Python 3.13, Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff.
- **Nenhuma dependência nova.** Nenhum `django.contrib.*` acrescentado.
- **Um modelo novo** (`VinculoDeGovernanca`) e **uma migração** aditiva.
- **Um app novo de domínio**: `trajetoria/governanca/`.
- Um módulo novo no editor (`acesso.py`) e um no adaptador de demonstração
  (`operador.py`).
- **Nenhuma alteração na 001–007** nem na jornada do egresso da 008.

**Tests**: obrigatórios e escritos antes da implementação correspondente (test-first). A
feature trata **autorização** (Princípio XXVI). Testes de comportamento novo DEVEM falhar
primeiro. Testes que só confirmam comportamento entregue por história anterior podem
passar de imediato; se falharem, a correção vai no módulo indicado.

**Segurança exaustiva, repetição não**: a proteção de **todas** as rotas é provada por
um teste estrutural (cada view declara a regra) mais um POST não autorizado parametrizado
pelas 17 rotas de escrita com um único perfil. Os demais perfis são testados numa rota
representativa, porque o mesmo decorador protege todas.

**Organization**: Setup, Foundational, uma fase por história da spec (US1–US12, na
ordem de prioridade) e Polish.

`trajetoria/editor/views.py`, `trajetoria/editor/acesso.py`, `tests/editor/conftest.py`
e cada arquivo de teste são editados **em sequência**. Tarefas no mesmo arquivo nunca têm
[P].

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US12).

## Convenções para todas as tarefas

- **Um modelo só**: `VinculoDeGovernanca`. Não crie Operador, Usuário, Conta,
  Identidade, Credencial, Role, Permission, Capability, RolePermission, Scope, Unidade,
  Organization, Tenant, Policy, ACL, AuditLog, histórico nem versionamento do vínculo.
- **Dois papéis só**: `CPAEG` e `CSAEG`. Nada de ADMIN, EDITOR, VIEWER, LEITOR, GESTOR,
  MANAGER, PUBLISHER, PUBLICADOR, APROVADOR.
- **Três regras só**, predicados explícitos passados diretamente ao gate:
  `pode_consultar_publicado`, `pode_consultar_rascunho`, `pode_elaborar_instrumento`.
  Nada de enum de capacidade, registro, composição de regras, `pode_publicar`.
- **Unidade**: texto **não nulo**. CPAEG ⇒ `unidade == ""`; CSAEG ⇒ unidade não vazia.
  Sem normalização, sem catálogo, sem entidade.
- **Sem autenticação**: nada de `django.contrib.auth`, `sessions`, `admin`, login, senha,
  conta, `is_staff`, `is_superuser`. O teste
  `tests/participacao/test_entrada_aceitacao.py::test_10_nenhum_mecanismo_de_autenticacao`
  **não é editado** e deve continuar verde.
- **Identificação ≠ autorização**: `trajetoria/editor/acesso.py` importa
  `operador_em_uso` de `trajetoria.demonstracao.operador` e de nenhum outro lugar; as
  regras de `trajetoria/governanca/regras.py` recebem só `vinculos`.
- **Nenhum identificador do cliente** fora do cookie assinado do modo de demonstração:
  nada por parâmetro de endereço, cabeçalho ou campo de formulário.
- **Ordem nas escritas**: identificar → vínculos → regra → só então objeto,
  `_exigir_rascunho` da 009, formulário e operação da 002. Recusa nunca valida
  formulário nem chama operação.
- **Textos de interface** em linguagem operacional, em `trajetoria/editor/mensagens.py`.
  Sem número de artigo da PAEG no texto principal; sem valor técnico de papel, código de
  rejeição, UUID nem identificador de operador. As comissões aparecem pelo nome por
  extenso da PAEG.
- **Publicação**: nenhuma rota, ação, botão, regra ou papel. `publicar` continua só no
  preparo da demonstração e em testes.
- **Sem escrita direta em modelo** fora de `trajetoria/governanca/operacoes.py`
  (nenhum `.save()`, `.create()`, `.update()`, `.delete()` em `editor` ou
  `demonstracao`). Nenhuma operação apaga vínculo.
- **Dados fictícios**: identificadores `demonstracao:operador-a`, `-b`, `-c`; nenhuma
  pessoa real, credencial padrão ou migração de dados.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: app novo registrado e pastas de teste.

- [X] T001 Criar o app `trajetoria/governanca/` com `__init__.py`, `apps.py`
  (`GovernancaConfig`, `name = "trajetoria.governanca"`, `verbose_name = "Governança
  institucional"`, no padrão de `trajetoria/editor/apps.py`), `migrations/__init__.py`, e
  acrescentar `"trajetoria.governanca"` a `INSTALLED_APPS` em `config/settings.py`. Não
  criar `urls.py`, `views.py`, `admin.py`, `forms.py`, `middleware.py`, `management/`
  nem `templates/` ([research R1](research.md))
- [X] T002 [P] Criar a pasta `tests/governanca/` (sem `__init__.py`, padrão do projeto)

**Checkpoint**: `uv run python manage.py check` passa.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o vínculo persistido, as três regras e a consulta de vínculos ativos, dos
quais todas as histórias dependem.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

### Tests for Foundational ⚠️

- [X] T003 [P] Escrever `tests/governanca/test_governanca_vinculo.py`, parte
  **restrições de banco** (gravando direto no modelo **só no teste**, cada caso em
  `pytest.raises(IntegrityError)` dentro de `transaction.atomic()`):
  `identificador_operador=""` recusado (`vinculo_identificador_nao_vazio`); `papel="ADMIN"`
  recusado (`vinculo_papel_valido`); CPAEG com `unidade="Vitória"` recusado e CSAEG com
  `unidade=""` recusado (`vinculo_unidade_conforme_papel`); duas linhas
  `("demonstracao:operador-a", "CPAEG", "")` recusadas e duas
  `("demonstracao:operador-b", "CSAEG", "Vitória")` recusadas (`vinculo_unico`), inclusive
  quando a primeira está inativa; CSAEG "Vitória" e CSAEG "Serra" do mesmo operador
  aceitos; dois operadores com CPAEG aceitos; `unidade` sem valor informado grava `""`
  ([data-model §3](data-model.md))
- [X] T004 [P] Escrever `tests/governanca/test_governanca_regras.py` com vínculos **não
  gravados** (`VinculoDeGovernanca(...)` em memória), matriz completa de
  [data-model §5](data-model.md): lista vazia → três `False`; CSAEG ativo → só
  `pode_consultar_publicado`; CSAEG de duas unidades → idem; CPAEG ativo → três `True`;
  CPAEG + CSAEG → três `True`; só vínculos inativos (CPAEG e CSAEG com `ativo=False`) →
  três `False`; a unidade não altera nenhum resultado; cada regra tem exatamente um
  parâmetro, `vinculos` (`inspect.signature`); resultado idêntico com
  `settings.TRAJETORIA_DEMONSTRACAO` `True` e `False`
- [X] T005 [P] Escrever `tests/governanca/test_governanca_consultas.py`:
  `vinculos_ativos(None)` e `vinculos_ativos("")` devolvem `[]` com
  `django_assert_num_queries(0)`; para um operador com CPAEG ativo, CSAEG "Vitória" ativo
  e CSAEG "Serra" inativo, devolve só os dois ativos, ordenados por `papel` e `unidade`,
  com uma consulta; outro operador não aparece; o identificador não é normalizado
  (`" demonstracao:operador-a"` não encontra nada)

### Implementation for Foundational

- [X] T006 Implementar `trajetoria/governanca/models.py`
  ([data-model §2–§3](data-model.md); [contrato](contracts/governanca.md)):
  - `class Papel(models.TextChoices)`: `CPAEG = "CPAEG", "Comissão Própria de
    Acompanhamento do Egresso (CPAEG)"` e `CSAEG = "CSAEG", "Comissão Setorial de
    Acompanhamento de Egressos (CSAEG)"`;
  - `class VinculoDeGovernanca(models.Model)` com exatamente: `id =
    UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`;
    `identificador_operador = TextField()`; `papel = TextField(choices=Papel.choices)`;
    `unidade = TextField(default="")` (**não nulo**); `ativo =
    BooleanField(default=True)`;
  - `Meta.ordering = ["identificador_operador", "papel", "unidade"]`;
  - `Meta.constraints`: `CheckConstraint(condition=~Q(identificador_operador=""),
    name="vinculo_identificador_nao_vazio")`;
    `CheckConstraint(condition=Q(papel__in=["CPAEG", "CSAEG"]),
    name="vinculo_papel_valido")`; `CheckConstraint(condition=Q(papel="CPAEG",
    unidade="") | (Q(papel="CSAEG") & ~Q(unidade="")),
    name="vinculo_unidade_conforme_papel")`; `UniqueConstraint(fields=
    ["identificador_operador", "papel", "unidade"], name="vinculo_unico")` (sem
    `nulls_distinct`, sem condição);
  - propriedade `rotulo_de_atuacao`: CPAEG → `"Comissão Própria de Acompanhamento do
    Egresso (CPAEG) — atuação institucional"`; CSAEG → `"Comissão Setorial de
    Acompanhamento de Egressos (CSAEG) — unidade {unidade}"`;
  - docstring: registro administrativo que reflete designação feita fora do sistema e
    não a verifica (spec FR-065; DP-1002); `ativo` responde só "este vínculo concede
    autorização agora?"; sem escopo persistido (derivado do papel)
- [X] T007 Gerar `trajetoria/governanca/migrations/0001_initial.py` com `uv run python
  manage.py makemigrations governanca` e conferir que só cria a tabela e as quatro
  restrições; `makemigrations --check --dry-run` passa (depende de T006)
- [X] T008 [P] Implementar `trajetoria/governanca/regras.py` com exatamente as três funções
  públicas de [contrato, Regras](contracts/governanca.md):
  `pode_consultar_publicado(vinculos) = any(v.ativo for v in vinculos)`;
  `pode_consultar_rascunho(vinculos)` e `pode_elaborar_instrumento(vinculos)` =
  `any(v.ativo and v.papel == Papel.CPAEG for v in vinculos)`. Sem acesso a banco,
  requisição ou settings. Docstrings com a fundamentação: elaborar = PAEG Art. 21, VI;
  consulta de publicadas pela CSAEG = Art. 22, IV, interpretação operacional B6; as duas
  regras de CPAEG são distintas por spec e podem divergir (DP-1004). `__all__` com as
  três (depende de T006)
- [X] T009 [P] Implementar `trajetoria/governanca/consultas.py`:
  `vinculos_ativos(identificador: str | None) -> list[VinculoDeGovernanca]` — `None` ou
  `""` → `[]` sem consulta; senão `list(VinculoDeGovernanca.objects.filter(
  identificador_operador=identificador, ativo=True).order_by("papel", "unidade"))`
  (depende de T006)

**Checkpoint**: `uv run pytest tests/governanca` verde.

---

## Phase 3: User Story 1 — Registrar o vínculo de governança (Priority: P1) 🎯 MVP

**Goal**: registrar, reativar e desativar vínculos por operação de aplicação, com as
recusas da spec.

**Independent Test**: só operações e consultas, sem interface
([contrato, Operações](contracts/governanca.md)).

### Tests for User Story 1 ⚠️

- [X] T010 [US1] Acrescentar a `tests/governanca/test_governanca_vinculo.py` a parte
  **operações**: `registrar_vinculo(id, Papel.CPAEG)` cria ativo com `unidade == ""`;
  `registrar_vinculo(id, Papel.CSAEG, "Vitória")` cria ativo; rejeições
  (`VinculoRejeitado.motivo`) sem gravar nada: `IDENTIFICADOR_INVALIDO` (`""`, `"  "`,
  `" x"`, não `str`), `PAPEL_INVALIDO` (`"ADMIN"`), `UNIDADE_PROIBIDA` (CPAEG com
  `"Vitória"`), `UNIDADE_EXIGIDA` (CSAEG com `""` e `"  "`), `UNIDADE_INVALIDA` (CSAEG com
  `" Vitória"` e unidade não `str`), `JA_ATIVO` (mesma combinação ativa);
  `desativar_vinculo` torna inativo sem apagar (contagem de linhas inalterada);
  `desativar_vinculo` de inativo → `JA_INATIVO`; `registrar_vinculo` sobre combinação
  inativa reativa **a mesma linha** (mesmo `pk`, contagem inalterada); dois operadores com
  CPAEG; o mesmo operador com CPAEG e CSAEG; a unidade é gravada exatamente como
  informada; o módulo não expõe operação de exclusão, troca de papel ou de unidade

### Implementation for User Story 1

- [X] T011 [US1] Implementar `trajetoria/governanca/operacoes.py`
  ([contrato, Operações](contracts/governanca.md)):
  - `class Motivo(Enum)`: `IDENTIFICADOR_INVALIDO`, `PAPEL_INVALIDO`, `UNIDADE_PROIBIDA`,
    `UNIDADE_EXIGIDA`, `UNIDADE_INVALIDA`, `JA_ATIVO`, `JA_INATIVO`;
  - `class VinculoRejeitado(Exception)` com atributo `motivo`;
  - `registrar_vinculo(identificador: str, papel: Papel, unidade: str = "")`: valida na
    ordem do contrato antes de gravar; em `transaction.atomic()`, busca a combinação com
    `select_for_update()`; inexistente → cria ativo; inativa → `ativo=True` na mesma
    linha; ativa → `JA_ATIVO`; `IntegrityError` de corrida → `JA_ATIVO`;
  - `desativar_vinculo(vinculo)`: relê com `select_for_update()`; ativo → `ativo=False`;
    inativo → `JA_INATIVO`;
  - docstring do módulo: mecanismo técnico administrativo (spec FR-062), usado por
    testes, pelo preparo da demonstração e por `manage.py shell`; **não** é processo
    oficial de designação; reflete designação externa (portaria) e não a verifica
    (FR-065; DP-1002). Sem exclusão
  (depende de T006)

**Checkpoint**: `uv run pytest tests/governanca` verde.

---

## Phase 4: User Story 2 — Atuar como operador fictício no modo de demonstração (Priority: P1)

**Goal**: identificar um dos três operadores fictícios, só no modo de demonstração; a
escolha identifica, o vínculo autoriza.

**Independent Test**: escolha, troca e recusa de identificador fora da lista, com o modo
ligado; nada responde com o modo desligado
([contrato](contracts/demonstracao-operador.md)).

### Tests for User Story 2 ⚠️

- [X] T012 [P] [US2] Escrever `tests/interface/test_demonstracao_operador.py`:
  - `operador_em_uso`: sem cookie → `None`; cookie assinado com
    `demonstracao:operador-a` → o identificador; cookie assinado com identificador fora de
    `OPERADORES_FICTICIOS` (por exemplo `"pessoa-real"`) → `None`; cookie adulterado →
    `None`; modo desligado com cookie válido → `None`;
  - `GET /demonstracao/operador/`: lista os três operadores com rótulos de apresentação;
    as atuações vêm dos vínculos (A: "Comissão Própria de Acompanhamento do Egresso
    (CPAEG) — atuação institucional"; B: "… (CSAEG) — unidade Vitória"; C: "Sem atuação
    institucional ativa"); depois de desativar o vínculo de A, A aparece sem atuação; a
    página diz que a escolha só identifica; nenhum identificador no texto visível;
  - `POST /demonstracao/operador/escolher/` com A → 302 para `/editor/`, cookie gravado;
    com `"pessoa-real"` → 404 e cookie não gravado;
  - troca de A para B: a requisição seguinte usa B;
  - `POST /demonstracao/operador/encerrar/` → cookie apagado, 302 para
    `/demonstracao/operador/`;
  - cookie da Pessoa fictícia (008) e cookie do operador são independentes;
  - `preparar()`: cria CPAEG ativo para A e CSAEG "Vitória" ativo para B, nada para C; é
    idempotente (duas execuções, mesmas três linhas no máximo); recusa com
    `PreparoRecusado` quando existe vínculo de identificador fora de
    `OPERADORES_FICTICIOS`; o `Resumo` devolvido não muda
- [X] T013 [P] [US2] Atualizar as fronteiras da 008: em
  `tests/interface/test_interface_demonstracao.py`, acrescentar
  `"/demonstracao/operador/"`, `"/demonstracao/operador/escolher/"` e
  `"/demonstracao/operador/encerrar/"` a `ROTAS` (modo desligado → 404); em
  `tests/interface/test_interface_fronteiras.py`, acrescentar
  `"trajetoria.governanca.operacoes"` a `SO_NO_CENARIO`. Nenhuma outra expectativa muda

### Implementation for User Story 2

- [X] T014 [US2] Criar `trajetoria/demonstracao/operador.py`
  ([contrato](contracts/demonstracao-operador.md)): `OperadorFicticio` (dataclass
  congelada `identificador`, `rotulo`); `OPERADORES_FICTICIOS` =
  `("demonstracao:operador-a", "Operador fictício A")`, `("demonstracao:operador-b",
  "Operador fictício B")`, `("demonstracao:operador-c", "Operador fictício C")`;
  `COOKIE = "trajetoria_demonstracao_operador"`, `SALT = "operador-de-demonstracao"`;
  `operador_em_uso(request) -> str | None` (modo desligado → `None` sem ler cookie; lê
  `get_signed_cookie`; aceita só identificador da tupla; memoriza na requisição; nunca
  levanta exceção); `operador_ficticio(identificador)`; `usar_operador(response,
  operador)` (`httponly=True`, `samesite="Lax"`, sem `max_age`; `ValueError` fora da
  tupla); `esquecer_operador(response)`. Docstring: adaptador temporário, não autentica,
  não é produção (DP-1001), no padrão de `trajetoria/demonstracao/entrada.py`
- [X] T015 [US2] Acrescentar a `trajetoria/demonstracao/views.py` as views
  `operadores` (`@require_GET`; para cada operador fictício,
  `vinculos_ativos(identificador)` e `rotulo_de_atuacao`, ou "Sem atuação institucional
  ativa"; indica o operador em uso), `escolher_operador` (`@require_POST`; fora da tupla
  → `Http404`; senão `redirect("/editor/")` + `usar_operador`) e `encerrar_operador`
  (`@require_POST`; `redirect("/demonstracao/operador/")` + `esquecer_operador`); e as
  três rotas em `trajetoria/demonstracao/urls.py` (`demonstracao/operador/`,
  `demonstracao/operador/escolher/`, `demonstracao/operador/encerrar/`) (depende de T014)
- [X] T016 [P] [US2] Criar `trajetoria/demonstracao/templates/demonstracao/operador.html`
  na mesma base, estilo e acessibilidade de `demonstracao/entrada.html`: título "Atuar
  como operador fictício", texto "A escolha identifica o operador apenas para
  demonstração. O que ele pode fazer no editor decorre dos vínculos de governança
  registrados, e não desta escolha.", um `<form method="post">` com `{% csrf_token %}` por
  operador, botão "Atuar como {rótulo}", atuações em lista, indicação do operador em uso,
  botão "Encerrar" e ligação "Ir para o editor". Identificador só em `value`. Sem
  `<script>` (depende de T014)
- [X] T017 [US2] Atualizar `trajetoria/demonstracao/cenario.py`: dentro da transação de
  `preparar()`, depois das Campanhas, (1) recusar com `PreparoRecusado("O banco contém
  vínculos de governança que não são fictícios. O cenário de demonstração só é preparado
  num banco local com dados fictícios.")` se houver `VinculoDeGovernanca` com
  `identificador_operador` fora de `OPERADORES_FICTICIOS`; (2) registrar, só se não
  houver ativo, `registrar_vinculo("demonstracao:operador-a", Papel.CPAEG)` e
  `registrar_vinculo("demonstracao:operador-b", Papel.CSAEG, "Vitória")`; nada para C;
  (3) tratar `VinculoRejeitado` como as demais recusas de operação do preparo. O
  `Resumo` não muda (depende de T011, T014)

**Checkpoint**: `uv run pytest tests/interface` verde.

---

## Phase 5: User Story 3 — Operador CPAEG acessa o editor e elabora rascunho (Priority: P1)

**Goal**: o gate central em todas as 25 views; para CPAEG, o editor é o da 009.

**Independent Test**: a suíte existente da 009, executada como operador A (CPAEG), passa
sem mudança de expectativa (SC-003).

### Tests for User Story 3 ⚠️

- [X] T018 [US3] Atualizar `tests/editor/conftest.py`: sobrescrever a fixture `client`
  para atuar como operador fictício A com vínculo CPAEG (fixture `db`;
  `registrar_vinculo("demonstracao:operador-a", Papel.CPAEG)`; cookie assinado com
  `COOKIE` e `SALT` de `trajetoria.demonstracao.operador`); acrescentar fixtures
  `cliente_csaeg` (operador B, CSAEG "Vitória"), `cliente_sem_vinculo` (operador C),
  `cliente_inativo` (operador A com o vínculo CPAEG desativado) e
  `cliente_nao_identificado` (sem cookie de operador). Docstring atualizada. Nenhum teste
  existente da 009 muda de expectativa
- [X] T019 [US3] Escrever `tests/editor/test_editor_autorizacao.py`, parte **CPAEG**:
  `client` (CPAEG) obtém 200 em `/editor/`, na Pesquisa (com rascunhos e publicadas), na
  estrutura, Seção, Pergunta, diagnóstico e prévia de um rascunho (`copia`), e na
  publicada (`publicada`); cria Pesquisa, cria Versão a partir de publicada, adiciona
  Pergunta numa cópia → 302 e gravação feita; o cabeçalho mostra "Atuação: Comissão
  Própria de Acompanhamento do Egresso (CPAEG) — atuação institucional" e a ligação
  "Trocar operador fictício"; o banner é `mensagens.BANNER`; POST em publicada → 409 da
  009 inalterado
- [X] T020 [US3] Atualizar `tests/editor/test_editor_fronteiras.py`: acrescentar a
  `PERMITIDOS` `"trajetoria.demonstracao.operador": {"operador_em_uso"}`,
  `"trajetoria.governanca.consultas": {"vinculos_ativos"}` e
  `"trajetoria.governanca.regras": {"pode_consultar_publicado", "pode_consultar_rascunho",
  "pode_elaborar_instrumento"}`; novo teste: `operador_em_uso` só é importado em
  `trajetoria/editor/acesso.py`; `trajetoria.governanca.operacoes` e
  `trajetoria.governanca.models` não são importados pelo editor. As proibições de
  `publicar` e de rotas de publicação continuam
- [X] T021 [US3] Atualizar `tests/editor/test_editor_acesso.py`: o teste de modo desligado
  passa a enviar também cookie assinado do operador A, cabeçalho `X-Operador:
  demonstracao:operador-a` e parâmetro `?operador=demonstracao:operador-a` → 404 em todas
  as rotas; o teste de banner continua por `mensagens.BANNER`

### Implementation for User Story 3

- [X] T022 [US3] Criar `trajetoria/editor/acesso.py`
  ([contrato](contracts/acesso-editor.md)):
  - `Atuacao` (dataclass congelada: `vinculos`, `consultar_publicado`,
    `consultar_rascunho`, `elaborar`, `rotulos`), sem identificador;
  - `exige(regra)`: aceita só as três funções de `governanca.regras` (outra → erro na
    importação); grava `envolvida.exige = regra`; em cada requisição: `operador_em_uso`
    → `None` → `redirect("/demonstracao/operador/")` sem parâmetro; `vinculos_ativos` →
    `[]` → recusa `sem_atuacao`; `not regra(vinculos)` → recusa `vinculo_nao_permite`
    (variante elaboração se a regra for `pode_elaborar_instrumento`, senão leitura de
    rascunho); senão anexa `request.atuacao` e chama a view;
  - `exigir_consulta(request, versao)`: rascunho sem `atuacao.consultar_rascunho` →
    levanta a interrupção com a recusa de leitura de rascunho (mesmo mecanismo
    `_Resposta`/`_respondendo` das views, movido ou importado sem duplicar);
  - `recusa(request, variante)`: `render("editor/recusa.html", status=403)`;
  - importa `operador_em_uso` de `trajetoria.demonstracao.operador` (único ponto) e nada
    de `governanca.operacoes`
- [X] T023 [P] [US3] Atualizar `trajetoria/editor/mensagens.py`: `BANNER = "Ambiente não
  produtivo de demonstração: a identificação é simulada por operador fictício, e os
  vínculos fictícios não representam designação institucional real. Este editor não está
  disponível para uso produtivo."`; textos de recusa `RECUSA_TITULO = "Acesso não
  permitido"`, `RECUSA_SEM_ATUACAO = "Não há vínculo institucional ativo para este
  operador. Sem vínculo ativo, o editor não pode ser usado."`, `RECUSA_RASCUNHO = "Seu
  vínculo permite consultar o instrumento publicado, mas não as Versões em rascunho."`,
  `RECUSA_ELABORACAO = "Seu vínculo institucional atual não permite editar este
  instrumento. Ele permite consultar o instrumento publicado."`, `SOMENTE_PUBLICADAS =
  "Somente Versões publicadas são exibidas para a sua atuação."`. Sem número de artigo
- [X] T024 [P] [US3] Criar `trajetoria/editor/templates/editor/recusa.html` (estende
  `editor/base.html`, sem trilha, `<h1>` com `RECUSA_TITULO`, parágrafo da variante,
  ligações "Voltar às Pesquisas" → `/editor/` só em `vinculo_nao_permite` e "Trocar
  operador fictício" → `/demonstracao/operador/`; sem `role="alert"`); e atualizar
  `trajetoria/editor/templates/editor/base.html` com a linha "Atuação: {rótulos separados
  por "; "}" quando houver `atuacao` e a ligação "Trocar operador fictício"
- [X] T025 [US3] Atualizar `trajetoria/editor/views.py`: importar `exige` de
  `trajetoria.editor.acesso` e aplicar `@exige(...)` como **decorador mais externo** das
  25 views conforme a tabela "Rota → regra" do
  [contrato](contracts/acesso-editor.md#rota--regra): `pode_consultar_publicado` em
  `pesquisas`, `pesquisa`, `versao`, `previa`, `previa_secao`, `secao`, `pergunta`;
  `pode_consultar_rascunho` em `diagnostico`; `pode_elaborar_instrumento` nas 17 demais;
  `_render` passa `atuacao` (de `request.atuacao`) ao contexto; docstring do módulo
  troca "não autentica nem autoriza (DP-901)" pela referência ao gate da 010. Nenhuma
  outra mudança de comportamento (depende de T022, T023, T024)

**Checkpoint**: `uv run pytest tests/editor` verde — a suíte da 009 passa como CPAEG.

---

## Phase 6: User Story 4 — Recusar acesso e escrita a quem não tem vínculo ativo (Priority: P1)

**Goal**: sem operador → escolha de operador; sem vínculo ativo → 403, antes de buscar
qualquer elemento.

**Independent Test**: perfis sem operador, sem vínculo e inativo numa rota de leitura e
numa de escrita.

### Tests for User Story 4 ⚠️

- [X] T026 [US4] Acrescentar a `tests/editor/test_editor_autorizacao.py`:
  `cliente_nao_identificado` em GET `/editor/` e em POST `/editor/pesquisas/nova/` → 302
  com `Location == "/demonstracao/operador/"` (sem parâmetro), nenhuma Pesquisa criada,
  conteúdo do instrumento ausente da resposta; `cliente_sem_vinculo` e `cliente_inativo`
  em GET `/editor/versoes/<copia>/` e em POST `/editor/pesquisas/nova/` → 403 com
  `RECUSA_SEM_ATUACAO`, nada gravado (`ce.retrato` e `ce.contagens` idênticos);
  `cliente_sem_vinculo` em GET de UUID inexistente → 403 (recusa precede a busca);
  `client` (CPAEG) no mesmo UUID → 404 da 009

### Implementation for User Story 4

- [X] T027 [US4] Ajustar `trajetoria/editor/acesso.py` só se T026 falhar (o
  comportamento vem de T022); nenhuma regra nova

**Checkpoint**: `uv run pytest tests/editor/test_editor_autorizacao.py` verde.

---

## Phase 7: User Story 5 — Proteger no servidor todas as rotas de escrita (Priority: P1)

**Goal**: prova estrutural de que toda rota tem gate e prova comportamental de que
nenhuma escrita passa sem elaborar.

**Independent Test**: teste estrutural + POST CSAEG nas 17 rotas de escrita.

### Tests for User Story 5 ⚠️

- [X] T028 [US5] Acrescentar a `tests/editor/test_editor_autorizacao.py` o teste
  **estrutural** (SC-001, FR-042): para cada padrão de `trajetoria.editor.urls`, a view
  tem `exige` e ele é uma das três regras; as 8 leituras (`pesquisas`, `pesquisa`,
  `versao`, `diagnostico`, `previa`, `previa_secao`, `secao`, `pergunta`) declaram
  `pode_consultar_publicado` (ou `pode_consultar_rascunho` em `diagnostico`); **toda**
  outra view declara `pode_elaborar_instrumento`; `len(urlpatterns) == 25`
- [X] T029 [US5] Acrescentar a `tests/editor/test_editor_autorizacao.py` o POST não
  autorizado **parametrizado pelas 17 rotas de escrita** com `cliente_csaeg` (SC-002):
  dados inválidos de propósito (`{"texto": "", "designacao": "", "nome": ""}`); `monkeypatch`
  de todas as funções de `trajetoria.instrumento.operacoes` usadas pelo editor para
  falhar se chamadas; resposta 403 com `RECUSA_ELABORACAO`; sem resumo de erros de
  formulário no corpo; `ce.retrato` e `ce.contagens` idênticos; e o mesmo para o GET das
  páginas de formulário e de confirmação de remoção dessas rotas
- [X] T030 [US5] Acrescentar o caso de desativação entre GET e POST (SC-005): `client`
  (CPAEG) abre `/editor/versoes/<copia>/dados/`; o vínculo é desativado por
  `desativar_vinculo`; o POST seguinte → 403 com `RECUSA_SEM_ATUACAO` e nada gravado

### Implementation for User Story 5

- [X] T031 [US5] Corrigir em `trajetoria/editor/views.py` qualquer view que T028–T030
  apontem sem gate ou com a regra errada; nenhuma outra mudança

**Checkpoint**: segurança das escritas provada.

---

## Phase 8: User Story 6 — Atuação de unidade sem poder institucional global (Priority: P1)

**Goal**: CSAEG consulta só o instrumento publicado; rascunhos não carregados nas listas.

**Independent Test**: `cliente_csaeg` nas listas, nas leituras por estado e no
diagnóstico.

### Tests for User Story 6 ⚠️

- [X] T032 [US6] Acrescentar a `tests/editor/test_editor_autorizacao.py`, parte
  **CSAEG**: `/editor/` mostra a contagem só de publicadas e `SOMENTE_PUBLICADAS`, sem
  "Nova Pesquisa"; a página da Pesquisa lista só a `publicada`, sem designações de
  rascunho no HTML e sem "Nova Versão"; Pesquisa sem Versão publicada aparece com
  "nenhuma Versão publicada"; estrutura, Seção, Pergunta, prévia e Seção da prévia da
  `publicada` → 200 sem controles e sem "Nova Versão a partir desta"; as mesmas cinco
  rotas na `copia` (rascunho) e o diagnóstico → 403 com `RECUSA_RASCUNHO`; cabeçalho
  "Atuação: Comissão Setorial de Acompanhamento de Egressos (CSAEG) — unidade Vitória";
  operadores CSAEG de "Vitória" e de "Serra" veem a mesma `publicada`

### Implementation for User Story 6

- [X] T033 [US6] Em `trajetoria/editor/views.py`, chamar `exigir_consulta(request,
  versao)` **depois** de carregar o elemento e antes de montar a página em `versao`,
  `previa`, `previa_secao`, `secao` e `pergunta` (depende de T022)
- [X] T034 [US6] Em `trajetoria/editor/views.py`, filtrar na consulta quando
  `not request.atuacao.consultar_rascunho`: em `pesquisas`,
  `Count("versoes", filter=Q(versoes__estado=EstadoVersao.PUBLICADA))`; em `pesquisa`,
  `.filter(estado=EstadoVersao.PUBLICADA)`; passar `somente_publicadas` ao contexto
  (acrescentar `EstadoVersao` a `PERMITIDOS["trajetoria.instrumento.models"]` em
  `tests/editor/test_editor_fronteiras.py`)
- [X] T035 [US6] Condicionar a `atuacao.elaborar` as ações "Nova Pesquisa" em
  `trajetoria/editor/templates/editor/pesquisas.html`, "Nova Versão" em
  `trajetoria/editor/templates/editor/pesquisa.html` e "Nova Versão a partir desta" em
  `trajetoria/editor/templates/editor/versao.html`; exibir `SOMENTE_PUBLICADAS` quando
  `somente_publicadas`

**Checkpoint**: `uv run pytest tests/editor` verde.

---

## Phase 9: User Story 7 — Preservar somente leitura e imutabilidade (Priority: P1)

**Goal**: consulta ≠ edição; elaborar não abre exceção à Versão publicada.

**Independent Test**: publicada para CPAEG e CSAEG; escrita em publicada pelos dois.

### Tests for User Story 7 ⚠️

- [X] T036 [US7] Acrescentar a `tests/editor/test_editor_autorizacao.py`: para a
  `publicada`, `client` (CPAEG) vê como única ação "Nova Versão a partir desta" e
  `cliente_csaeg` não vê nenhuma; POST de `/editor/versoes/<publicada>/dados/` por CPAEG
  → 409 da 009 e por CSAEG → 403 (autorização antes da verificação de publicada); em
  ambos, `ce.retrato(publicada)` idêntico. Implementação já entregue por US3/US6; se
  falhar, corrigir em `trajetoria/editor/views.py`

---

## Phase 10: User Story 8 — Operador com mais de um vínculo (Priority: P2)

**Goal**: capacidades = união dos vínculos ativos, sem "papel ativo".

- [X] T037 [US8] Acrescentar a `tests/editor/test_editor_autorizacao.py`: operador A com
  CPAEG e CSAEG "Vitória" ativos elabora e o cabeçalho mostra as duas atuações; após
  `desativar_vinculo` do CPAEG, a requisição seguinte só consulta publicadas; operador B
  com CSAEG "Vitória" e "Serra" continua sem rascunhos nem elaboração. Implementação já
  entregue (regras de T008); se falhar, corrigir em `trajetoria/governanca/regras.py`

---

## Phase 11: User Story 9 — Vínculo inativo e desativação (Priority: P2)

**Goal**: desativar sem apagar; efeito na requisição seguinte; reativar a mesma linha.

- [X] T038 [US9] Acrescentar a `tests/editor/test_editor_autorizacao.py`: `client`
  (CPAEG) com 200 em `/editor/`; `desativar_vinculo` → 403 `RECUSA_SEM_ATUACAO` na
  requisição seguinte; `registrar_vinculo` de novo → mesma linha reativada e 200 de novo,
  sem trocar cookie nem escolher operador outra vez. Implementação já entregue por
  T011/T022

---

## Phase 12: User Story 10 — Privilégio técnico não substitui governança (Priority: P2)

**Goal**: autorização depende exclusivamente do vínculo.

- [X] T039 [P] [US10] Escrever `tests/governanca/test_governanca_fronteiras.py`:
  `apps.get_app_config("governanca").get_models()` == `[VinculoDeGovernanca]`; campos ==
  `{"id", "identificador_operador", "papel", "unidade", "ativo"}`; `unidade.null is
  False`; `{p.value for p in Papel} == {"CPAEG", "CSAEG"}`; `regras` expõe exatamente as
  três funções públicas; nenhum arquivo `urls.py`, `views.py`, `admin.py`, `forms.py`,
  `middleware.py`, pasta `management/` ou `templates/` no app; nenhuma importação de
  `django.contrib.auth`, `trajetoria.editor`, `trajetoria.demonstracao`,
  `trajetoria.interface`, `trajetoria.instrumento`, `trajetoria.campanha`,
  `trajetoria.participacao`; pelos **nomes definidos** no app (funções, classes, membros
  de enum, via `ast`), nenhum contendo `publicar`, `aprov`, `homolog`, `admin`,
  `superuser`, `permission`, `policy`, `capab`, e nenhum membro de enum além de `CPAEG`,
  `CSAEG` e os sete de `Motivo` (texto livre de docstring não é verificado, para não
  confundir "administrativo" ou "publicadas"); pelo texto dos fontes do app e de
  `trajetoria/editor/acesso.py`, nenhuma ocorrência de `is_staff`, `is_superuser`,
  `request.user`, `TRAJETORIA_DEMONSTRACAO`, `django.contrib.auth`;
  `makemigrations --check --dry-run` passa
- [X] T040 [US10] Acrescentar a `tests/editor/test_editor_autorizacao.py`: com o modo de
  demonstração ligado e `cliente_sem_vinculo`, GET `/editor/` e POST
  `/editor/pesquisas/nova/` → 403 (o modo não autoriza; caso H), garantido em todas as
  rotas pelo teste estrutural T028

---

## Phase 13: User Story 11 — Publicação permanece indisponível (Priority: P2)

**Goal**: nenhuma superfície publica; 002/DP-001 aberta.

- [X] T041 [US11] Acrescentar a `tests/editor/test_editor_autorizacao.py`: com `client`
  (CPAEG) e um rascunho "sem impedimentos técnicos conhecidos", nenhuma página contém
  "Publicar", "publicar", "aprovação", "homologar" nem botão desabilitado de publicação;
  POST direto em `/editor/versoes/<v>/publicar/` → 404 e a Versão continua `RASCUNHO`.
  As proibições estruturais continuam em `tests/editor/test_editor_fronteiras.py` e
  T039

---

## Phase 14: User Story 12 — Recusas compreensíveis e acessíveis (Priority: P3)

**Goal**: recusas em linguagem operacional, sem detalhe técnico, acessíveis.

- [X] T042 [US12] Acrescentar a `tests/editor/test_editor_autorizacao.py`
  `test_textos_das_recusas` e `test_recusas_sem_termos_tecnicos` (SC-010, SC-011): cada
  variante mostra seu texto de `mensagens.py`; nenhuma contém "Art.", "role",
  "permission", "ACL", "policy", "scope", `"demonstracao:operador"`, nomes de `Motivo`,
  nomes de regra (`pode_`) nem UUID (`ce.padroes_tecnicos(resposta) == []`); as
  comissões aparecem só pelo nome por extenso com a sigla entre parênteses
- [X] T043 [P] [US12] Acrescentar a `tests/editor/test_editor_acessibilidade.py` as duas
  variantes de recusa (sem atuação; vínculo não permite, leitura e elaboração) e a
  `tests/interface/test_interface_acessibilidade.py` a página `/demonstracao/operador/`,
  pela função `verificar` da 008 (idioma, título, `<h1>`, rótulos, foco, sem `<script>`)

**Checkpoint**: `uv run pytest` verde.

---

## Phase 15: Polish & Cross-Cutting Concerns

- [X] T044 [P] Acrescentar ao `README.md` uma linha para o quickstart da 010, dizendo que o
  editor continua não produtivo enquanto DP-1001 estiver aberta
- [X] T045 Rodar a suíte completa e as verificações: `uv run pytest`, `uv run ruff check
  .`, `uv run ruff format --check .`, `uv run python manage.py makemigrations --check
  --dry-run`; confirmar que `tests/participacao/test_entrada_aceitacao.py` não foi
  editado e que `test_10_nenhum_mecanismo_de_autenticacao` passa
- [X] T046 Executar o roteiro manual de [quickstart.md](quickstart.md) (passos 1–14,
  inclusive desativar e reativar pelo `manage.py shell`) e o roteiro de 320 px nas
  recusas e na escolha de operador; registrar divergências antes de fechar
- [X] T047 **Over-engineering check** sobre o diff completo (`git diff main --stat` e
  leitura): confirmar ausência de segundo modelo, `django.contrib.auth`,
  django-guardian ou outra dependência, policy engine, ACL, hierarquia de escopo, tela ou
  CRUD de vínculos, auditoria, mandato, portaria, datas de vigência, publicação e fluxo de
  aprovação; remover o que aparecer sem requisito concreto
- [X] T048 Conferir coerência final: os textos de `trajetoria/editor/mensagens.py` e
  `contracts/acesso-editor.md` iguais; tabela "Rota → regra" do contrato igual ao que
  T028 verifica; atualizar `specs/010-governanca-papeis-escopos/checklists/requirements.md`
  se algo mudou

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** → **Foundational (Phase 2)** → histórias.
- **US1** (operações) depende só de Foundational.
- **US2** (operador fictício) depende de US1 (o preparo usa `registrar_vinculo`).
- **US3** (gate) depende de US2 (`operador_em_uso`) e de Foundational.
- **US4, US5, US6, US7** dependem de US3 (mesmo gate e mesmo arquivo de testes).
- **US8, US9** dependem de US3 (e US1 para desativar).
- **US10** (T039) depende só de Foundational e US1; T040 de US3.
- **US11, US12** dependem de US3 e US6.
- **Polish** depois de todas.

### Within Each User Story

- Testes primeiro, falhando; depois implementação.
- `tests/editor/test_editor_autorizacao.py` e `trajetoria/editor/views.py` recebem as
  tarefas em sequência (T019 → T026 → T028 → T029 → T030 → T032 → T036 → T037 → T038 →
  T040 → T041 → T042).

### Parallel Opportunities

- T002 com T001.
- T003, T004, T005 (arquivos de teste diferentes).
- T008 e T009 depois de T006.
- T012 e T013 (arquivos diferentes).
- T016 com T015 depois de T014.
- T023 e T024 com T022 em andamento; T020 e T021 com T019.
- T039 em qualquer momento depois de US1.
- T043 com T042; T044 com T045.

## Parallel Example: Phase 2

```bash
Task: "T003 tests/governanca/test_governanca_vinculo.py (restrições)"
Task: "T004 tests/governanca/test_governanca_regras.py"
Task: "T005 tests/governanca/test_governanca_consultas.py"
```

## Parallel Example: User Story 3

```bash
Task: "T023 trajetoria/editor/mensagens.py"
Task: "T024 trajetoria/editor/templates/editor/recusa.html + base.html"
Task: "T020 tests/editor/test_editor_fronteiras.py"
Task: "T021 tests/editor/test_editor_acesso.py"
```

---

## Implementation Strategy

### MVP First

1. Fases 1–2: vínculo, regras e consulta.
2. US1: registrar, reativar e desativar.
3. US2 + US3: operador fictício e gate; o editor da 009 funciona como CPAEG.
4. **STOP and VALIDATE**: `uv run pytest tests/governanca tests/editor tests/interface`.

### Incremental Delivery

1. US4 e US5: recusas e prova de proteção de todas as escritas.
2. US6 e US7: CSAEG somente leitura; imutabilidade preservada.
3. US8–US11: múltiplos vínculos, desativação, privilégio técnico, publicação ausente.
4. US12 e Polish.

---

## Decisões Pendentes preservadas

Nenhuma tarefa resolve, implementa ou contorna:

- **DP-1001**: identificação produtiva — só operador fictício no modo de demonstração;
  editor fechado fora dele.
- **DP-1002**: autorização e evidência do registro de vínculos — sem portaria, datas ou
  autor.
- **DP-1003**: quem atua pela CPAEG — o sistema não distingue.
- **DP-1004**: rascunhos ou reporte para a CSAEG — só publicadas.
- **DP-1005**: unidades canônicas — texto livre, sem catálogo.
- **DP-1006**: Proex, DIREC, Proen, Diretorias — não representadas.
- **009/DP-901**: parcialmente resolvida (elaborar = CPAEG); o restante segue nas
  DP-1001, DP-1003, DP-1004.
- **002/DP-001**: quem publica — nenhuma publicação.
- **002/DP-002**: fluxo de aprovação — só RASCUNHO e PUBLICADA.
- **009/DP-902**: baseline — rascunho comum, editável só por CPAEG.
- **009/DP-903**: autoria e histórico — nenhum.
- **004/DP-402, 004/DP-403, 005/DP-505**: Campanha e respostas — nenhuma superfície.

## Notes

- [P] = arquivos diferentes, sem dependência pendente.
- Testes existentes alterados: só `tests/editor/conftest.py`,
  `tests/editor/test_editor_fronteiras.py`, `tests/editor/test_editor_acesso.py`,
  `tests/editor/test_editor_acessibilidade.py`,
  `tests/interface/test_interface_demonstracao.py`,
  `tests/interface/test_interface_fronteiras.py` e
  `tests/interface/test_interface_acessibilidade.py` — fixtures e listas de fronteira,
  nunca expectativas de comportamento editorial ou da jornada.
- Commits por fase ou grupo lógico; ao fechar, o padrão do projeto (`docs(010): …` e
  `feat(010): …`).
- Se alguma tarefa parecer exigir segundo modelo, autenticação, sessão, tela de vínculos,
  enum de capacidade, policy, ACL, hierarquia, auditoria, datas, portaria, publicação ou
  aprovação, **pare** e volte ao plan com a justificativa.

## Divergências registradas na implementação

- `_exigir_consulta` ficou em `trajetoria/editor/views.py`, ao lado de `_exigir_rascunho`,
  para reutilizar `_Resposta` sem mover código da 009; `acesso.py` expõe `exige`, `Atuacao`
  e `recusa` (contrato atualizado).
- `Atuacao` guarda `rotulos`, `consultar_rascunho` e `elaborar`; `consultar_publicado` é
  implícito depois do gate (contrato atualizado).
- Texto de leitura de rascunho alinhado ao exemplo aprovado: "Seu vínculo institucional
  atual não permite consultar Versões em rascunho. Ele permite consultar o instrumento
  publicado." (contrato, research e quickstart atualizados).
- Testes existentes também alterados, além dos listados: `tests/editor/test_editor_erros.py`
  (dois testes criavam `Client()` cru, que agora vai para a escolha de operador; passaram a
  atuar como CPAEG) e `tests/editor/construcao_editor.py` (auxiliar `atuar_como`). Nenhuma
  expectativa de comportamento mudou.
- Para a CSAEG, a página da Pesquisa continua mostrando, como texto, a origem de uma Versão
  publicada ("criada a partir de «…»"), que pode ser a designação de um rascunho. O rascunho
  não é listado nem ligado; a origem é dado da Versão publicada (009 FR-013).

