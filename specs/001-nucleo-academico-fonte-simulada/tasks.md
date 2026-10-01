---

description: "Tasks da Feature 001 — Núcleo acadêmico longitudinal e fonte institucional simulada"
---

# Tasks: Núcleo acadêmico longitudinal e fonte institucional simulada

**Input**: Design documents from `specs/001-nucleo-academico-fonte-simulada/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Stack (confirmada; [ADR 0001](../../docs/adr/0001-stack-inicial.md))**: Python 3.13,
Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff.

**Tests**: obrigatórios. Todas as histórias tocam invariantes constitucionais (Pessoa ↔
Conclusão, múltiplas conclusões, elegibilidade, providers). Os testes cobrem a lista do
solicitante. Nenhum teste existe só para aumentar cobertura. Quando a história traz
comportamento novo, os testes vêm antes da implementação e DEVEM falhar primeiro.
Quando a história só verifica comportamento entregue antes (US2, US3, US6), os testes
podem passar de imediato. Se falharem, a correção é no arquivo indicado.

**Organization**: as tarefas estão agrupadas por história de usuário. As tarefas que
alteram o mesmo arquivo (`incorporacao.py`, `test_incorporacao.py`) são sequenciais.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US8).

## Limites desta lista (não criar)

Estes itens ficam fora:

- Pesquisa, Versão, Campanha, Participação, Resposta.
- Autenticação, permissões, admin, CRUD.
- API, frontend, exportação.
- Integração real, reconciliação entre fontes, sincronização.
- Repository pattern, service layer genérica, registry de providers.
- Event sourcing, CQRS, filas, jobs.
- Histórico por atributo, painel de divergências.
- Coluna `fonte_simulada` ou qualquer atributo de domínio que indique "mock".

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: projeto Django mínimo, executável e verificável.

- [X] T001 Criar `pyproject.toml` na raiz:
  - `requires-python = ">=3.13,<3.14"`;
  - dependências `Django>=5.2,<5.3` e `psycopg[binary]>=3.2,<3.4`;
  - extra `dev` com `pytest`, `pytest-django`, `ruff`;
  - `[tool.pytest.ini_options]` com `DJANGO_SETTINGS_MODULE = "config.settings"`,
    `testpaths = ["tests"]`, `pythonpath = ["."]`, `addopts = "--strict-markers"`;
  - `[tool.ruff]` com `target-version = "py313"`.

  Em seguida, gerar `uv.lock` com `uv sync --extra dev`.
- [X] T002 [P] Criar os pacotes vazios do plan:
  - `trajetoria/__init__.py`;
  - `trajetoria/academico/__init__.py` e `trajetoria/academico/apps.py` (AppConfig
    `trajetoria.academico`, `default_auto_field` irrelevante porque as chaves são UUID);
  - `trajetoria/academico/migrations/__init__.py`;
  - `trajetoria/fonte_academica/__init__.py`.
- [X] T003 [P] Criar `.env.example` só com `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`,
  `PGDATABASE` e `DJANGO_SECRET_KEY`, todos com valores de exemplo e sem segredo real.
  O arquivo é só referência: nada carrega `.env` automaticamente. As variáveis são
  exportadas no shell quando o padrão de T004 não servir.
  Acrescentar `.venv/`, `__pycache__/`, `.env` e `.pytest_cache/` ao `.gitignore`.
- [X] T004 Criar o esqueleto do Django (depende de T001 e T002):
  - `manage.py`;
  - `config/__init__.py`;
  - `config/settings.py`:
    - um único arquivo; lê `DJANGO_SECRET_KEY` e `PG*` do ambiente, com padrões de
      desenvolvimento local para rodar sem nenhuma variável exportada;
    - `SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insegura-apenas-desenvolvimento-local")`.
      A chave padrão é fictícia e marcada como insegura; não há ambiente de produção
      nesta feature;
    - `DATABASES` em PostgreSQL via `psycopg`:
      - `NAME = os.environ.get("PGDATABASE", "trajetoria")`;
      - `HOST`, `PORT`, `USER` e `PASSWORD` de `PGHOST`, `PGPORT`, `PGUSER` e
        `PGPASSWORD`, com padrão `""`, o que usa os padrões do libpq (socket local e
        usuário do sistema operacional);
    - `INSTALLED_APPS = ["trajetoria.academico"]`, sem admin, auth, sessions,
      contenttypes ou messages;
    - `USE_TZ = True`, `TIME_ZONE = "America/Sao_Paulo"`;
    - `LOGGING` com o logger `trajetoria` em nível WARNING no console;
  - `config/urls.py` com `urlpatterns = []`;
  - `config/wsgi.py`.

  Verificar com `uv run python manage.py check` e `uv run ruff check .`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: contrato da fronteira, os dois modelos e a fonte simulada completa. Todas
as histórias dependem disso.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T005 [P] Implementar `trajetoria/fonte_academica/contrato.py` conforme
  [contracts/fonte-academica.md](contracts/fonte-academica.md). O módulo NÃO importa
  Django. Conteúdo:
  - `Protocol` `FonteAcademica` com o atributo `codigo: str` e as operações
    `obter_pessoa(id_externo)` e `obter_conclusao(id_externo)`;
  - dataclasses `frozen` `ConclusaoNaFonte`, `PessoaEncontrada`, `PessoaInexistente`,
    `ConclusaoEncontrada`, `RegistroNaoReconhecidoComoConclusao` e
    `ConclusaoInexistente`;
  - exceção `FonteAcademicaIndisponivel`;
  - em `__post_init__`, rejeitar com `ValueError`:
    - cadeia vazia em qualquer campo de texto (regra 4);
    - `id_externo` vazio;
    - `data_conclusao` presente com `ano_conclusao` `None` ou diferente de
      `data_conclusao.year` (regra 5);
  - `PessoaEncontrada.conclusoes` como `tuple`.
- [X] T006 [P] Implementar `trajetoria/academico/models.py` exatamente conforme
  [data-model.md](data-model.md). Não criar `admin.py`.
  - **`Pessoa`**:
    - `id = UUIDField(primary_key=True, default=uuid4, editable=False)`;
    - `fonte` (texto, obrigatório);
    - `id_externo` (texto, obrigatório);
    - `nome` (texto, `null=True`; "`NULL` = não informado pela fonte");
    - `incorporado_em` (`auto_now_add`);
    - `UniqueConstraint(fields=["fonte", "id_externo"])`;
    - `CheckConstraint` impedindo `''` em `fonte`, `id_externo` e `nome`;
    - nenhum campo acadêmico.
  - **`ConclusaoAcademica`**:
    - UUID igual ao da Pessoa;
    - `pessoa = ForeignKey(Pessoa, on_delete=PROTECT, related_name="conclusoes")`;
    - `fonte`, `id_externo` (obrigatórios);
    - `curso`, `unidade`, `nivel`, `modalidade`, `forma_oferta` (texto, `null=True`);
    - `ano_conclusao` (`PositiveSmallIntegerField`, `null=True`);
    - `data_conclusao` (`DateField`, `null=True`);
    - `incorporado_em` (`auto_now_add`);
    - `UniqueConstraint(fields=["fonte", "id_externo"])`;
    - `CheckConstraint` impedindo `''` em todos os campos de texto;
    - `CheckConstraint(condition=Q(data_conclusao__isnull=True) | (Q(ano_conclusao__isnull=False) & Q(ano_conclusao=ExtractYear("data_conclusao"))))`.
      O `ano_conclusao IS NOT NULL` explícito é obrigatório: sem ele, data com ano `NULL`
      resulta em `UNKNOWN` e passa no PostgreSQL;
    - `Meta.ordering = ["ano_conclusao", "id"]` (só de apresentação, FR-017).
- [X] T007 Gerar `trajetoria/academico/migrations/0001_initial.py` com
  `uv run python manage.py makemigrations academico` (depende de T004 e T006).
  Verificar com `uv run python manage.py makemigrations --check --dry-run`.
- [X] T008 [P] Implementar `trajetoria/fonte_academica/cenarios.py`: o conjunto
  canônico **exatamente** como em
  [contracts/cenarios-simulados.md](contracts/cenarios-simulados.md).
  - Dataclasses internas `PessoaSimulada(id_externo, nome)` e
    `RegistroSimulado(id_externo, id_pessoa, situacao, curso, unidade, nivel,
    modalidade, forma_oferta, ano_conclusao, data_conclusao)`.
  - Tuplas `PESSOAS` (11 pessoas) e `REGISTROS` (19 registros).
  - Situações `concluida`, `matricula_ativa`, `evasao`, `transferencia`,
    `situacao_legada_x` e `None`.
  - Apenas dados fictícios: prefixo `SIM-` e sobrenome "Exemplo".
- [X] T009 Implementar `trajetoria/fonte_academica/simulada.py` (depende de T005 e
  T008). Classe `FonteSimulada` com:
  - `codigo = "simulada"`;
  - construtor `(pessoas=cenarios.PESSOAS, registros=cenarios.REGISTROS,
    indisponivel=False)`;
  - `obter_pessoa`: devolve `PessoaEncontrada` só com registros
    `situacao == "concluida"`, ordenados por `id_externo`, ou `PessoaInexistente`;
  - `obter_conclusao`: devolve `ConclusaoEncontrada`,
    `RegistroNaoReconhecidoComoConclusao` (qualquer outra situação, inclusive
    desconhecida ou `None`) ou `ConclusaoInexistente`;
  - lança `FonteAcademicaIndisponivel` em ambas as operações quando
    `indisponivel=True`.
- [X] T010 Criar `tests/conftest.py` (depende de T009) com a fixture `fonte_simulada`
  (`FonteSimulada()`) e a fixture `fonte_indisponivel`
  (`FonteSimulada(indisponivel=True)`). Nada além disso.

**Checkpoint**: `manage.py check` sem erros, migração gerada e fonte simulada importável.

---

## Phase 3: User Story 1 — Pessoa com sua Conclusão Acadêmica (Priority: P1) 🎯 MVP

**Goal**: incorporar uma Pessoa com uma conclusão reconhecida e ler seu contexto como
dado institucional.

**Independent Test**: incorporar SIM-P-0001 (Cenário A) e obter 1 Pessoa com 1
Conclusão cujos atributos são iguais aos da fonte.

### Tests for User Story 1 ⚠️

- [X] T011 [P] [US1] Criar `tests/test_modelo.py` (`@pytest.mark.django_db`) com as
  restrições de [data-model.md](data-model.md):
  - (a) `IntegrityError` ao repetir (`fonte`, `id_externo`) em Pessoa e em
    ConclusaoAcademica. O mesmo `id_externo` em **fontes diferentes** é aceito e gera
    duas Pessoas distintas: a unicidade é por par, e não há fusão entre fontes
    (FR-034);
  - (b) `IntegrityError` com `''` em `fonte`, `id_externo`, `nome`, `curso`;
  - (c) `IntegrityError` com `data_conclusao=2020-07-10` e `ano_conclusao=2019`, e
    também com `data_conclusao=2020-07-10` e `ano_conclusao=None` (caso `UNKNOWN`);
  - (d) `ProtectedError` ao excluir Pessoa com conclusão;
  - (e) o conjunto de campos de `Pessoa` é exatamente
    `{id, fonte, id_externo, nome, incorporado_em}`, sem campo acadêmico (FR-003) e sem
    `fonte_simulada`. O de `ConclusaoAcademica` é exatamente
    `{id, pessoa, fonte, id_externo, curso, unidade, nivel, modalidade, forma_oferta,
    ano_conclusao, data_conclusao, incorporado_em}`. Não há campo declarado nem
    derivado, então todo atributo acadêmico é institucional por definição (FR-036);
  - (f) `ConclusaoNaFonte` com `''`, com ano diferente do ano da data ou com data e
    ano `None` gera `ValueError` (T005).
- [X] T012 [P] [US1] Criar `tests/test_incorporacao.py` com o teste do Cenário A:
  - `incorporar_pessoa(fonte_simulada, "SIM-P-0001")` devolve `INCORPORADA` e
    `pessoa_criada=True`;
  - há 1 Pessoa e 1 ConclusaoAcademica;
  - curso, unidade, nível, modalidade, `ano_conclusao=2022` e
    `data_conclusao=2022-12-16` iguais ao catálogo;
  - `forma_oferta is None` (não informado pela fonte, sem valor padrão — FR-010).

  Acrescentar um teste com SIM-P-0002/SIM-C-0002: `ano_conclusao=2014` e
  `data_conclusao is None`, sem precisão fabricada (FR-011).

### Implementation for User Story 1

- [X] T013 [US1] Implementar `trajetoria/academico/incorporacao.py` (depende de T006,
  T009, T011, T012):
  - enum `SituacaoIncorporacao` (`INCORPORADA`, `SEM_CONCLUSAO_ELEGIVEL`,
    `PESSOA_INEXISTENTE`);
  - dataclass `ResultadoIncorporacao` com `situacao`, `pessoa`, `pessoa_criada`,
    `conclusoes_criadas`, `conclusoes_existentes` e `divergencias=()`, conforme
    [contracts/incorporacao.md](contracts/incorporacao.md);
  - `incorporar_pessoa(fonte, id_externo_pessoa)`:
    - chama `fonte.obter_pessoa` **antes** de abrir a transação;
    - para `PessoaEncontrada` com `conclusoes == ()`, devolve `SEM_CONCLUSAO_ELEGIVEL`
      sem criar nada (FR-039). O caso de Pessoa já incorporada que perde as conclusões
      fica para T029;
    - para `PessoaEncontrada` com conclusões, dentro de `transaction.atomic()`, faz
      `get_or_create` da Pessoa por (`fonte.codigo`, `id_externo`), com `nome` em
      `defaults`;
    - faz `get_or_create` de cada ConclusaoAcademica por (`fonte.codigo`,
      `id_externo`), com o contexto em `defaults`;
    - não executa `update` nem `delete` em nenhum caminho;
    - a deduplicação usa só (`fonte`, `id_externo`).

**Checkpoint**: US1 verde (`uv run pytest tests/test_modelo.py tests/test_incorporacao.py`).

---

## Phase 4: User Story 2 — Uma Pessoa, múltiplas Conclusões (Priority: P1)

**Goal**: uma única Pessoa por referência de origem, com todas as suas formações.

**Independent Test**: incorporar SIM-P-0002, SIM-P-0003 e SIM-P-0004 e obter uma Pessoa
cada, com 2, 2 e 3 conclusões.

### Tests for User Story 2 ⚠️

- [X] T014 [US2] Acrescentar a `tests/test_incorporacao.py` (depende de T012):
  - B, C e D geram 1 Pessoa cada, com 2, 2 e 3 Conclusões de UUIDs distintos;
  - em C, as unidades são "Serra" e "Cefor"; em D, os níveis são distintos;
  - **homônimos**: SIM-P-0010 e SIM-P-0011 ("Carla Exemplo") geram 2 Pessoas
    distintas;
  - **sem nome**: SIM-P-0009 é incorporada com `nome is None` e 1 conclusão (FR-005);
  - **sem fusão por semelhança** (FR-014): uma `FonteSimulada(pessoas=..., registros=...)`
    construída no teste, com duas conclusões `concluida` de mesmo curso e unidade e
    `id_externo` diferentes, gera 2 Conclusões.

### Implementation for User Story 2

- [X] T015 [US2] Nenhum código novo é esperado: o comportamento vem de T013. Se T014
  falhar, corrigir só `trajetoria/academico/incorporacao.py`, sem acrescentar busca por
  nome ou por atributos.

**Checkpoint**: US1 e US2 verdes.

---

## Phase 5: User Story 3 — Contexto próprio de cada conclusão (Priority: P1)

**Goal**: o consumidor distingue cada conclusão e seu contexto sem conhecer a fonte.

**Independent Test**: a trajetória de SIM-P-0004 mostra três conclusões, cada uma com o
contexto declarado para ela e nenhum atributo misturado (SC-002). A de SIM-P-0003
reproduz a "experiência esperada" (SC-008).

### Tests for User Story 3 ⚠️

- [X] T016 [P] [US3] Criar `tests/test_aceitacao.py` (`django_db`):
  - **(a) SC-002**: depois de incorporar SIM-P-0004 (Cenário D, 3 conclusões), há
    exatamente 1 Pessoa e 3 Conclusões. Cada item de `pessoa.conclusoes.all()` tem
    exatamente o curso, a unidade, o nível, a modalidade, a forma de oferta e o ano do
    seu registro no catálogo, e nenhum valor aparece em conclusão diferente daquela em
    que a fonte o declarou;
  - **(b)** `ConclusaoAcademica.objects.get(id=...)` devolve a conclusão e
    `conclusao.pessoa` (FR-016);
  - **(c)** a ordem das conclusões é a mesma em duas leituras (FR-017);
  - **(d) consumidor de demonstração** (SC-008), com SIM-P-0003:
    - a função local `descrever_trajetoria(pessoa)` recebe só a Pessoa, usa **apenas**
      os modelos e devolve as linhas da "experiência esperada" (TADS — Serra —
      Graduação — Presencial — 2022; Especialização em Informática na Educação — Cefor
      — Pós-graduação — A distância — 2025).

### Implementation for User Story 3

- [X] T017 [US3] Nenhum código novo é esperado: leitura pelos modelos (T006). Se
  T016 falhar, corrigir só `Meta.ordering` ou `related_name` em
  `trajetoria/academico/models.py`.

**Checkpoint**: histórias P1 completas. O MVP está demonstrável.

---

## Phase 6: User Story 4 — Fonte simulada e substituível (Priority: P2)

**Goal**: provar que a fonte simulada cumpre o contrato e que outra implementação
substitui a simulada sem mudar o domínio.

**Independent Test**: a mesma suíte de contrato passa contra `FonteSimulada` e contra
`FonteAlternativa`, e a incorporação funciona com ambas.

### Tests for User Story 4 ⚠️

- [X] T018 [P] [US4] Criar `tests/fontes_de_teste.py` com `FonteAlternativa`.
  - É outra implementação do `Protocol`, sem herdar nem reutilizar `FonteSimulada`.
  - Usa dicionários internos, `codigo = "teste-alternativa"`, parâmetro
    `indisponivel` e um conjunto fictício próprio (prefixo `ALT-`) com:
    - uma pessoa com 2 conclusões;
    - uma pessoa só com registro não reconhecido;
    - um registro com atributo `None`.
  - Para `FonteSimulada` e para `FonteAlternativa`, declarar um dicionário
    `CASOS_DE_CONTRATO` com os ids de: pessoa com conclusões, pessoa sem conclusão
    reconhecida, pessoa inexistente, conclusão reconhecida, registro não reconhecido e
    conclusão inexistente.
- [X] T019 [US4] Criar `tests/test_contrato_fonte.py` (depende de T018). A suíte é
  parametrizada sobre `[FonteSimulada, FonteAlternativa]` e cobre as regras 1 a 8 de
  [contracts/fonte-academica.md](contracts/fonte-academica.md):
  - só conclusões reconhecidas em `PessoaEncontrada`;
  - pessoa sem conclusão é `PessoaEncontrada(conclusoes=())`;
  - não reconhecido ≠ inexistente;
  - `None` em vez de `''`;
  - ano × data;
  - `FonteAcademicaIndisponivel` com `indisponivel=True`;
  - resultado igual em duas chamadas;
  - `codigo` não vazio.

  Incluir dois testes de fronteira por análise de `import` (módulo `ast`):
  - `trajetoria/fonte_academica/contrato.py` não importa `django`;
  - nenhum módulo de `trajetoria/academico/` importa `trajetoria.fonte_academica.simulada`
    (FR-021).
- [X] T020 [P] [US4] Criar `tests/test_fonte_simulada.py` (FR-026 a FR-029, SC-001,
  SC-009):
  - teste tabular com **cada linha** de
    [contracts/cenarios-simulados.md](contracts/cenarios-simulados.md): os resultados de
    `obter_pessoa` e `obter_conclusao` batem com a situação e os atributos declarados;
  - G: `SIM-P-9999` e `SIM-C-9999`;
  - H: `indisponivel=True`;
  - **dados fictícios**:
    - todo `id_externo` começa com `SIM-`;
    - todo nome é `None` ou termina em " Exemplo";
    - nenhum valor casa com padrão de CPF (`\d{3}\.?\d{3}\.?\d{3}-?\d{2}`) nem contém
      `@`;
  - nenhuma data de conclusão é posterior a 2026-09-30.
- [X] T021 [US4] Acrescentar a `tests/test_incorporacao.py` (depende de T014 e T018):
  incorporar a pessoa com 2 conclusões da `FonteAlternativa` com o mesmo
  `incorporar_pessoa`, sem nenhum ajuste no domínio. O resultado é 1 Pessoa e 2
  Conclusões com `fonte = "teste-alternativa"` (FR-024, SC-006).

### Implementation for User Story 4

- [X] T022 [US4] Nenhum código de produção novo é esperado. Se T019 ou T020 falharem,
  corrigir `trajetoria/fonte_academica/simulada.py` ou `cenarios.py`, nunca o
  contrato para acomodar a implementação.

**Checkpoint**: substituibilidade comprovada.

---

## Phase 7: User Story 5 — Repetição sem duplicidade e divergência sinalizada (Priority: P2)

**Goal**: a repetição não duplica, e o conteúdo divergente não sobrescreve, não destrói
nem duplica, mas é sinalizado.

**Independent Test**: incorporar o conjunto canônico 3× em ordens diferentes dá as
mesmas linhas e UUIDs, e as variantes de divergência produzem os tipos esperados sem
alterar o banco.

### Tests for User Story 5 ⚠️

- [X] T023 [US5] Acrescentar a `tests/fontes_de_teste.py` (depende de T018) a função
  `variante_canonica(...)`. Ela devolve `FonteSimulada(pessoas=..., registros=...)` com
  o mesmo `codigo = "simulada"` e uma das variantes do catálogo:
  - (i) curso de SIM-C-0001 alterado;
  - (ii) SIM-C-0003 ausente;
  - (iii) SIM-C-0002 atribuída a SIM-P-0001;
  - (iv) SIM-P-0009 passa a ter nome;
  - (v) uma nova conclusão `concluida` para SIM-P-0001;
  - (vi) SIM-C-0001 passa a `matricula_ativa`, e SIM-P-0001 fica sem conclusão
    reconhecida (usada em T028);
  - (vii) SIM-P-0001 e SIM-C-0001 ausentes (usada em T030).
- [X] T024 [US5] Acrescentar a `tests/test_incorporacao.py` (depende de T021 e T023).
  Pré-condição dos testes de variante: o conjunto canônico já foi incorporado com
  `FonteSimulada()` antes de incorporar a variante.
  - **repetição** (SC-003): incorporar todas as 11 pessoas do catálogo 3 vezes, em
    ordem direta, inversa e embaralhada com semente fixa. As contagens e o conjunto de
    UUIDs são iguais aos de uma incorporação, e a segunda chamada devolve
    `pessoa_criada=False` e `conclusoes_criadas=()`;
  - **conclusão repetida**: SIM-P-0005 (Cenário E) incorporada 2× mantém o mesmo UUID
    da Conclusão (FR-008);
  - **nova conclusão** (v): é associada à Pessoa existente, sem nova Pessoa (FR-032);
  - **divergências** (i) a (iv) produzem, respectivamente:
    - `ATRIBUTOS_DIFERENTES`, `registro="conclusao"`, `campos=("curso",)`;
    - `AUSENTE_NA_FONTE`, `registro="conclusao"`;
    - `CONCLUSAO_DE_OUTRA_PESSOA`, `registro="conclusao"`, sem reatribuição nem
      duplicata;
    - `ATRIBUTOS_DIFERENTES`, `registro="pessoa"`, `campos=("nome",)`;
  - em todas as divergências, um retrato de todas as linhas (valores e
    `incorporado_em`) antes e depois é idêntico;
  - **log**: `caplog` registra um WARNING por divergência contendo tipo, registro,
    fonte e `id_externo`, e nunca o nome da pessoa.

### Implementation for User Story 5

- [X] T025 [US5] Implementar a divergência em `trajetoria/academico/incorporacao.py`
  (depende de T024), conforme [contracts/incorporacao.md](contracts/incorporacao.md):
  - enum `TipoDivergencia` (`ATRIBUTOS_DIFERENTES`, `CONCLUSAO_DE_OUTRA_PESSOA`,
    `AUSENTE_NA_FONTE`) e dataclass
    `Divergencia(tipo, registro, fonte, id_externo, campos)`, com
    `registro: Literal["pessoa", "conclusao"]`;
  - comparar o nome da Pessoa existente e os atributos de cada Conclusão existente com
    os da fonte;
  - conclusão existente ligada a outra Pessoa: não criar nem mover;
  - conclusões locais desta Pessoa e desta fonte ausentes da resposta:
    `AUSENTE_NA_FONTE`;
  - nunca `update`/`delete`;
  - `logging.getLogger("trajetoria.academico")` com `.warning` e só os campos tipo,
    registro, fonte, `id_externo` e `campos`;
  - nada é persistido sobre a divergência.

**Checkpoint**: idempotência e divergência mínima verdes.

---

## Phase 8: User Story 6 — Proveniência mínima (Priority: P2)

**Goal**: fonte, identificador externo e momento de incorporação recuperáveis, e a fonte
simulada identificada pelo próprio código.

**Independent Test**: toda linha incorporada tem `fonte`, `id_externo` e
`incorporado_em`. As vindas da fonte simulada têm `fonte = "simulada"`.

### Tests for User Story 6 ⚠️

- [X] T026 [US6] Acrescentar a `tests/test_incorporacao.py` (depende de T024), cobrindo
  FR-035 e SC-005:
  - depois de incorporar o catálogo, 100% das Pessoas e Conclusões têm
    `fonte == "simulada"`, `id_externo` igual ao do catálogo e `incorporado_em`
    preenchido;
  - `incorporado_em` não muda após nova incorporação;
  - com `FonteAlternativa`, `fonte == "teste-alternativa"`.

### Implementation for User Story 6

- [X] T027 [US6] Nenhum código novo é esperado: os campos vêm de T006 e são
  preenchidos em T013. Se T026 falhar, corrigir só `trajetoria/academico/incorporacao.py`.
  Não acrescentar campo de proveniência.

**Checkpoint**: proveniência mínima comprovada.

---

## Phase 9: User Story 7 — Não concluído não vira Conclusão elegível (Priority: P2)

**Goal**: registros não concluídos nunca são materializados, e uma pessoa sem conclusão
elegível não é persistida.

**Independent Test**: F1 e F3 não geram nenhuma linha, F2 gera só SIM-C-0010, e nenhum
SIM-C-09xx existe no banco.

### Tests for User Story 7 ⚠️

- [X] T028 [US7] Acrescentar a `tests/test_incorporacao.py` (depende de T026), cobrindo
  FR-018, FR-019, FR-039 e SC-004:
  - SIM-P-0006 (F1, só `matricula_ativa`) e SIM-P-0008 (F3: evasão, transferência,
    desconhecida, não informada) devolvem `SEM_CONCLUSAO_ELEGIVEL`, com `pessoa is None`
    e 0 Pessoas e 0 Conclusões no banco;
  - SIM-P-0007 (F2) persiste só SIM-C-0010;
  - depois de incorporar o catálogo inteiro, `ConclusaoAcademica` não tem nenhum
    `id_externo` iniciado por `SIM-C-09`;
  - **pessoa que deixa de ter conclusões**: depois do catálogo canônico, a variante
    (vi) de T023 devolve `SEM_CONCLUSAO_ELEGIVEL`, a Pessoa existente e uma divergência
    `AUSENTE_NA_FONTE` (`registro="conclusao"`) para SIM-C-0001, com o retrato das
    linhas idêntico.

### Implementation for User Story 7

- [X] T029 [US7] Em `trajetoria/academico/incorporacao.py` (depende de T025 e T028),
  completar o caso `PessoaEncontrada` com `conclusoes == ()`. Não criar Pessoa já vem
  de T013; aqui, se a Pessoa já existir localmente, devolvê-la com as divergências
  `AUSENTE_NA_FONTE` de T025, sem alteração.

**Checkpoint**: elegibilidade protegida (Princípio II).

---

## Phase 10: User Story 8 — Inexistente e falha da fonte (Priority: P3)

**Goal**: resultados explícitos e distintos para inexistência e para falha. A falha não
tem efeito no banco.

**Independent Test**: G devolve `PESSOA_INEXISTENTE` sem linhas, e H propaga
`FonteAcademicaIndisponivel` sem escrita e sem alterar o que já foi incorporado.

### Tests for User Story 8 ⚠️

- [X] T030 [US8] Acrescentar a `tests/test_incorporacao.py` (depende de T028):
  - `SIM-P-9999` devolve `PESSOA_INEXISTENTE` com 0 linhas;
  - a variante (vii) de T023, depois de SIM-P-0001 ter sido incorporada, devolve
    `PESSOA_INEXISTENTE` com `AUSENTE_NA_FONTE` (`registro="pessoa"`) e nada removido;
  - `fonte_indisponivel` faz `pytest.raises(FonteAcademicaIndisponivel)` com 0 linhas;
  - depois de incorporar SIM-P-0001, uma nova chamada com `fonte_indisponivel` lança a
    exceção e o retrato das linhas é idêntico (FR-025).

### Implementation for User Story 8

- [X] T031 [US8] Em `trajetoria/academico/incorporacao.py` (depende de T030):
  - tratar `PessoaInexistente` conforme a tabela de
    [contracts/incorporacao.md](contracts/incorporacao.md);
  - garantir que `FonteAcademicaIndisponivel` se propaga sem captura nem conversão e
    antes de qualquer escrita.

**Checkpoint**: todas as histórias verdes.

---

## Phase 11: Polish & Cross-Cutting Concerns

- [X] T032 [P] Atualizar `README.md` com uma descrição de uma linha e um link para
  [quickstart.md](quickstart.md) e para a Constituição. Nada além disso.
- [X] T033 Validar o [quickstart.md](quickstart.md) de ponta a ponta:
  - `uv sync --extra dev`;
  - `uv run python manage.py check`;
  - `makemigrations --check --dry-run`;
  - `migrate`;
  - `uv run pytest`;
  - `uv run ruff check .`;
  - demonstração no shell com SIM-P-0003.

  Corrigir o quickstart se algum passo divergir.
- [X] T034 Revisão final contra a Constituição (Princípios XVI, XXII, XXIX e Definition
  of Done). Confirmar e registrar no PR que:
  - os logs não contêm nomes;
  - não existem `admin.py`, rotas ou endpoints (`config/urls.py` só com
    `urlpatterns = []`), coluna `fonte_simulada`, enum de nível ou modalidade,
    disparo de sincronização nem entidade de Pesquisa, Campanha ou Participação;
  - `INSTALLED_APPS` contém só o núcleo;
  - SC-007: a suíte passa sem acesso à rede nem a sistema acadêmico (nenhum cliente
    HTTP ou de banco externo nas dependências);
  - SC-010: cada uma das 8 perguntas de sucesso da descrição original é respondida com
    "sim", apontando requisito e teste;
  - DP-001 a DP-009 continuam abertas e nenhuma virou regra implícita.

Acessibilidade (XX) e responsividade (XXI): **N/A**, porque não há interface nesta
feature.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependências. T002 e T003 em paralelo depois de T001; T004
  depois de T001 e T002.
- **Foundational (Fase 2)**: depende da Fase 1 e bloqueia todas as histórias.
- **Histórias (Fases 3–10)**: dependem da Fase 2. Seguem a ordem de prioridade, porque
  compartilham `incorporacao.py` e `test_incorporacao.py`.
- **Polish (Fase 11)**: depende de todas as histórias.

### User Story Dependencies

- **US1**: primeira; entrega `incorporar_pessoa`.
- **US2, US3**: só verificam o que US1 entregou; US3 usa um arquivo próprio
  (`test_aceitacao.py`).
- **US4**: independente de US2 e US3; T021 depende de T014 só pela ordem no mesmo
  arquivo.
- **US5**: depende de US4 (`fontes_de_teste.py`).
- **US6**: só testes, depois de US5.
- **US7**: depende de US5, porque a pessoa já existente sem conclusões gera divergências.
- **US8**: depende de US5, porque a pessoa já existente que some gera divergências.

### Within Each User Story

- Testes antes da implementação. Onde há comportamento novo (US1, US5, US7, US8), eles
  DEVEM falhar primeiro.
- Uma tarefa por arquivo de cada vez nos arquivos compartilhados.

### Parallel Opportunities

Só onde os arquivos são realmente independentes:

- **Fase 1**: T002 ∥ T003.
- **Fase 2**: T005 ∥ T006 ∥ T008.
- **US1**: T011 ∥ T012.
- **US3 com US4**: T016 (`test_aceitacao.py`) pode rodar em paralelo com T018 e T020
  (`fontes_de_teste.py`, `test_fonte_simulada.py`).
- **US4**: T018 ∥ T020.

---

## Parallel Example: Foundational e US4

```bash
# Fase 2 — três arquivos independentes:
Task: "T005 contrato em trajetoria/fonte_academica/contrato.py"
Task: "T006 modelos em trajetoria/academico/models.py"
Task: "T008 catálogo em trajetoria/fonte_academica/cenarios.py"

# US4 — testes em arquivos distintos:
Task: "T018 FonteAlternativa em tests/fontes_de_teste.py"
Task: "T020 catálogo da fonte simulada em tests/test_fonte_simulada.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Fase 1 e Fase 2.
2. Fase 3 (US1): incorporar e ler SIM-P-0001.
3. **PARAR e VALIDAR** com `uv run pytest`.

### Incremental Delivery

1. Fases 1 e 2: fundação.
2. US1, US2, US3 (P1): núcleo Pessoa → Conclusão demonstrável.
3. US4, US5, US6, US7 (P2): substituibilidade, idempotência e divergência,
   proveniência, elegibilidade.
4. US8 (P3): inexistência e falha.
5. Polish e revisão constitucional antes do PR.

---

## Decisões Pendentes preservadas

DP-001 a DP-009 permanecem **abertas**. Nenhuma tarefa as resolve. As soluções
provisórias são as do [plan](plan.md#decisões-pendentes).

## Notes

- Total: **34 tarefas**. O código de produção fica em seis módulos centrais
  (`contrato.py`, `cenarios.py`, `simulada.py`, `models.py`, `incorporacao.py`,
  `apps.py`), além da configuração Django (`config/`, `manage.py`, `pyproject.toml`) e
  da migração `0001_initial.py`. Tarefas de teste: T011, T012, T014, T016, T018, T019, T020,
  T021, T023, T024, T026, T028, T030.
- Tarefas "nenhum código novo esperado" (T015, T017, T022, T027) existem para deixar
  explícito onde corrigir, sem criar camadas.
- Fazer commit ao fim de cada fase.
