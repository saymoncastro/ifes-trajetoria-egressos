---

description: "Tasks da Feature 004 — Campanhas e população elegível"
---

# Tasks: Campanhas e população elegível

**Input**: Design documents from `specs/004-campanhas-populacao-elegivel/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Stack (confirmada; [ADR 0001](../../docs/adr/0001-stack-inicial.md))**: Python 3.13,
Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff. Nenhuma dependência
nova. `ArrayField` vem de `django.contrib.postgres` (sem incluir esse app em
`INSTALLED_APPS`). A imutabilidade após a abertura é garantida **só pelas operações** e
por testes, como na 002: nenhum gatilho, `RunSQL`, `save()` ou `delete()` sobrescrito,
sinal ou camada de permissões.

**Tests**: obrigatórios. Todas as histórias tocam invariantes constitucionais
(elegibilidade, longitudinalidade, preservação histórica). Os testes vêm antes da
implementação e DEVEM falhar primeiro quando a história traz comportamento novo. Quando
a história só verifica comportamento já entregue (US5, US9, US11), os testes podem passar
de imediato; se falharem, a correção vai no arquivo indicado.

**Organization**: tarefas agrupadas por história da spec (US1–US11). `operacoes.py`,
`consultas.py` e os arquivos de teste compartilhados entre histórias são sequenciais.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US11).

## Convenções para todas as tarefas

- **Um único modelo novo**: `Campanha`, em `trajetoria/campanha/models.py`.
- **Nada muda** em `trajetoria/academico/`, `trajetoria/fonte_academica/`,
  `trajetoria/instrumento/`, `trajetoria/formulario_2024/` nem nos testes das Features
  001–003. A única linha alterada fora do app novo é `INSTALLED_APPS` (mais o link no
  README, no polish). Se surgir necessidade real de mudar 001–003, **parar** e demonstrar
  o bloqueio antes.
- **Escrita**: toda escrita segue o fluxo do [plan](plan.md#operações-e-rejeições):
  1. `transaction.atomic()`;
  2. `Campanha.objects.select_for_update().get(pk=…)`;
  3. se `aberta_em` está presente, rejeita `CAMPANHA_JA_ABERTA`, qualquer que seja o
     estado temporal (exceto `abrir` e `encerrar`);
  4. regras da operação na ordem do [contrato](contracts/operacoes.md);
  5. grava com `save(update_fields=[…])`.
- **Rejeição**: sempre `CampanhaRejeitada` com `Violacao(motivo, campo, detalhe)`. O
  `detalhe` nunca contém dado pessoal. Argumento de tipo errado é `TypeError` antes de
  qualquer escrita.
- **Tempo**:
  - toda função sensível ao tempo recebe `agora: datetime | None = None`;
  - só o auxiliar privado `_hoje(agora)` em `trajetoria/campanha/consultas.py` chama
    `timezone.now()`, e ele devolve `timezone.localdate(agora)`, na timezone configurada
    do projeto, sem fuso nominal no código;
  - **todo teste passa `agora` explícito** pelo auxiliar `momento(...)`;
  - nenhum teste depende do relógio real.
- **Precedência do estado** (data-model): `encerrada_em` → ENCERRADA; senão
  `fim` presente e `hoje > fim` → ENCERRADA (aberta ou não); senão `aberta_em` →
  EM_COLETA; senão EM_PREPARACAO.
- **Estado temporal controla a coleta; abertura histórica controla a imutabilidade.** A
  escrita nunca é decidida por `estado(...)`, só por `aberta_em`. Campanha nunca aberta,
  mesmo ENCERRADA pelo tempo, é editável e removível. Corrigir seu período não é
  reabertura. Só `abrir`, `encerrar` e as consultas recebem `agora`.
- **Critérios multivalorados**:
  - `NULL` = critério não definido, não restringe;
  - array com ≥ 1 valor = valores permitidos;
  - `[]` = inválido, nunca gravado;
  - valores exatos, sem normalização, sem duplicatas, gravados em `sorted(set(valores))`.
- **Versões nos testes**: Versão publicada mínima construída pelas operações da 002 e
  publicada com `trajetoria.instrumento.operacoes.publicar`. A baseline da 003
  (`materializar()`) é usada só onde se exige RASCUNHO e **nunca** é publicada.
- **Testes de banco**: usam `pytestmark = pytest.mark.django_db`. Os auxiliares são
  importados como `from tests.campanha.construcao import …`.

## Limites desta lista (não criar)

- Segmento, Critério, GrupoCritério, Regra, Filtro, População, MembroCampanha, Convite,
  Destinatário, Agendamento, Snapshot, Histórico, VersaoCampanha, Participação, Resposta.
- Coluna `estado`, coluna `pesquisa`, contagem de população gravada, datas de criação ou
  alteração, criador, descrição.
- Tabelas auxiliares por critério ou catálogos de Unidade, Nível, Modalidade e Forma de
  Oferta; normalização de valores.
- Estado AGENDADA ou EXPIRADA; prorrogação; reabertura; prioridade entre Campanhas.
- Job, Celery, cron, scheduler, cache, sinais, serviço ou repositório; abstração genérica
  de Clock; `freezegun`.
- Admin, URLs, API, comando de gestão, interface.
- Publicação da baseline da 003; qualquer escrita em `Versao` além das usadas para
  construir a Versão de teste.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: app Django vazio, registrado e verificável.

- [X] T001 Criar o esqueleto do app e registrá-lo:
  - `trajetoria/campanha/__init__.py` (vazio);
  - `trajetoria/campanha/apps.py` com `CampanhaConfig(AppConfig)`,
    `name = "trajetoria.campanha"`, `verbose_name = "Campanhas"`;
  - `trajetoria/campanha/migrations/__init__.py` (vazio);
  - diretório `tests/campanha/` **sem** `__init__.py` (como `tests/instrumento/`);
  - em `config/settings.py`, acrescentar `"trajetoria.campanha"` a `INSTALLED_APPS`
    depois de `"trajetoria.instrumento"`.

  Verificar com `uv run python manage.py check`.

**Checkpoint**: `manage.py check` sem erros.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: modelo, migração, vocabulário de rejeição, estado derivado e auxiliares de
teste, usados por todas as histórias.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T002 [P] Escrever `tests/campanha/construcao.py` (auxiliares, não testes):
  - `momento(ano, mes, dia, hora=12) -> datetime`: `timezone.make_aware(datetime(…))` na
    timezone corrente do Django, sem fuso nominal;
  - `versao_publicada(designacao="teste") -> Versao`: instrumento mínimo pelas operações
    da 002 (`criar_pesquisa`, `criar_versao`, `adicionar_secao(versao, 1)`,
    `adicionar_pergunta(secao, 1, "TEXTO_CURTO", "Pergunta de teste",
    obrigatoria=True)`), publicado com `publicar`;
  - `versao_rascunho(designacao="rascunho") -> Versao`: idem, sem publicar;
  - `conclusao(*, ano=None, unidade=None, nivel=None, modalidade=None, forma_oferta=None,
    pessoa=None) -> ConclusaoAcademica`: cria por ORM uma `Pessoa` (se não informada) e
    uma `ConclusaoAcademica` com `fonte="teste-campanha"` e `id_externo` único. Isso
    cobre atributos ausentes específicos sem tocar os cenários da 001 (research R14);
  - `incorporar_cenarios(fonte, ids=None)`: chama `incorporar_pessoa` para cada Pessoa
    de `cenarios.PESSOAS` (ou só os `ids`);
  - `rejeita(motivos, operacao, *args, **kwargs)`: exige `CampanhaRejeitada` cujos
    `motivos` sejam exatamente a tupla dada e devolve as violações;
  - `linha(campanha) -> dict`: `Campanha.objects.filter(pk=…).values().get()`, para
    comparar a linha antes e depois.
- [X] T003 Escrever `tests/campanha/conftest.py` (depende de T002) com as fixtures `versao_publicada`,
  `versao_rascunho` (dos auxiliares de T002) e `fonte_simulada` herdada de
  `tests/conftest.py` (sem redefinir).
- [X] T004 [P] Escrever `tests/campanha/test_campanha_modelo.py`, que DEVE falhar antes de
  T005. Usa escrita direta no ORM, fora das operações, e verifica cada CHECK do
  [data-model](data-model.md#campanha) com `IntegrityError`, cada um em
  `transaction.atomic()`:
  - `nome` vazio;
  - período com só uma data; `inicio > fim`; período de um dia aceito;
  - `ano_maximo < ano_minimo`;
  - para cada array: `[]` rejeitado; `[""]` rejeitado; `NULL` aceito; `["Serra"]`
    aceito;
  - `aberta_em` sem período;
  - `encerrada_em` sem `aberta_em`; `encerrada_em < aberta_em`;
  - remover a `Versao` referenciada levanta `ProtectedError`.
- [X] T005 Implementar `trajetoria/campanha/models.py` conforme
  [data-model.md](data-model.md). Docstring citando o data-model e as regras "`NULL` =
  ausente; `[]` nunca gravado". Copiar o padrão `_nao_vazio(campo, nome)` dos outros
  apps, sem importar. Campos:
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`;
  - `nome = TextField()`;
  - `versao = ForeignKey("instrumento.Versao", on_delete=PROTECT, related_name="+")`
    (sem relação reversa: a Versão não conhece a Campanha — research R1; exigido pelo
    teste SC-006 da 002);
  - `inicio`, `fim` `DateField(null=True)`;
  - `ano_minimo`, `ano_maximo` `PositiveSmallIntegerField(null=True)`;
  - `unidades`, `niveis`, `modalidades`, `formas_oferta`
    `ArrayField(TextField(), null=True)`;
  - `aberta_em`, `encerrada_em` `DateTimeField(null=True)`.

  `Meta.ordering = ["inicio", "id"]` (só determinismo). CHECKs, com `IS NOT NULL`
  explícito onde houver comparação:
  - `nome <> ''`;
  - `(inicio IS NULL AND fim IS NULL) OR (inicio IS NOT NULL AND fim IS NOT NULL AND
    inicio <= fim)`;
  - `ano_minimo IS NULL OR ano_maximo IS NULL OR ano_minimo <= ano_maximo`;
  - para cada array: `Q(col__isnull=True) | Q(col__len__gte=1)` e
    `~Q(col__contains=[""])`;
  - `aberta_em IS NULL OR (inicio IS NOT NULL AND fim IS NOT NULL)`;
  - `encerrada_em IS NULL OR aberta_em IS NOT NULL`;
  - `encerrada_em IS NULL OR encerrada_em >= aberta_em`.

  Propriedades:
  - `pesquisa` → `self.versao.pesquisa`;
  - `populacao_ampla` → os seis critérios são `None`.

  Nenhuma coluna `estado`, `pesquisa` ou de contagem. Depende de T001.
- [X] T006 Gerar `trajetoria/campanha/migrations/0001_initial.py` com
  `uv run python manage.py makemigrations campanha`. Conferir que ela cria só a tabela
  `campanha_campanha` e depende das migrações iniciais de `instrumento`, sem `RunSQL`.
  Rodar `uv run pytest tests/campanha/test_campanha_modelo.py`: DEVE passar. Depende de
  T005.
- [X] T007 [P] Implementar `trajetoria/campanha/regras.py`, separado de `operacoes.py`
  para que consultas e testes importem o vocabulário sem importar as operações:
  - `Motivo(Enum)` com os valores do
    [contrato](contracts/operacoes.md#motivos-motivo): `NOME_VAZIO`,
    `CAMPANHA_JA_ABERTA`, `PERIODO_INCOMPLETO`, `PERIODO_INVERTIDO`,
    `ANO_INVALIDO`, `ANOS_INVERTIDOS`, `CONJUNTO_VAZIO`, `VALOR_VAZIO`,
    `VERSAO_NAO_PUBLICADA`, `PERIODO_NAO_DEFINIDO`, `FORA_DO_PERIODO`,
    `CAMPANHA_NUNCA_ABERTA`;
  - `Violacao(motivo, campo: str | None, detalhe: str)` (`dataclass(frozen=True)`);
  - `CampanhaRejeitada(Exception)` com `violacoes` (≥ 1, senão `ValueError`), a
    propriedade `motivos` e `__str__` legível, no padrão de
    `trajetoria/instrumento/regras.py`.
- [X] T008 [P] Escrever em `tests/campanha/test_campanha_ciclo.py` os testes de estado
  derivado (DEVEM falhar antes de T009), com Campanhas criadas por ORM e período de
  01/04/2027 a 30/06/2027:
  - **E1**: antes do início, nunca aberta → `EM_PREPARACAO`;
  - **E2**: dentro do período, nunca aberta → `EM_PREPARACAO`;
  - **E3**: dentro do período, `aberta_em` presente → `EM_COLETA`;
  - **E4**: `encerrada_em` presente → `ENCERRADA`, inclusive com `agora` dentro do
    período;
  - **E5**: depois do fim, aberta → `ENCERRADA`;
  - **E6**: depois do fim, nunca aberta → `ENCERRADA`;
  - sem período → `EM_PREPARACAO` em qualquer `agora`;
  - último dia → ainda `EM_COLETA`; primeiro dia seguinte → `ENCERRADA`;
  - em todos os casos, `linha(campanha)` idêntica antes e depois da consulta (nenhuma
    escrita, nenhum job).
- [X] T009 Implementar em `trajetoria/campanha/consultas.py` (docstring citando
  [contracts/consultas.md](contracts/consultas.md)):
  - `EstadoCampanha(Enum)` com `EM_PREPARACAO`, `EM_COLETA`, `ENCERRADA`;
  - `_hoje(agora)`: o único ponto que chama `timezone.now()`;
  - `estado(campanha, *, agora=None)`, com a precedência das convenções.

  `uv run pytest tests/campanha/test_campanha_ciclo.py` DEVE passar. Depende de T005.

**Checkpoint**: modelo migrado; CHECKs e estados E1–E6 verdes.

---

## Phase 3: User Story 1 — Criar Campanha vinculada a uma Versão (Priority: P1) 🎯 MVP

**Goal**: Campanha com identidade própria, nome e exatamente uma Versão; nasce
EM_PREPARACAO; Pesquisa derivada.

**Independent Test**: duas Campanhas com a mesma Versão, identidades distintas, Versão
inalterada.

### Tests for User Story 1 ⚠️

- [X] T010 [US1] Escrever em `tests/campanha/test_campanha_preparacao.py` (DEVEM falhar
  antes de T011):
  - criar com Versão PUBLICADA e com Versão RASCUNHO, inclusive a baseline da 003 via
    `materializar()`. Em todos os casos: `EM_PREPARACAO`, `populacao_ampla` verdadeiro,
    período ausente, `campanha.pesquisa == versao.pesquisa`, e a Versão continua no
    estado e no `publicada_em` anteriores;
  - duas Campanhas com a mesma Versão têm `id` distintos;
  - nome vazio ou só com espaços → `NOME_VAZIO`, nada criado; nome gravado sem `strip()`;
  - `versao` que não é `Versao` → `TypeError`;
  - `alterar_campanha(versao=…)` para Versão de outra Pesquisa troca Versão e Pesquisa;
    `alterar_campanha(nome=…)` troca o nome; o parâmetro omitido é mantido;
  - `remover_campanha` em preparação remove a linha e a Versão permanece.

### Implementation for User Story 1

- [X] T011 [US1] Implementar em `trajetoria/campanha/operacoes.py` (docstring citando
  [contracts/operacoes.md](contracts/operacoes.md) e "único caminho de escrita"):
  - o sentinela `_MANTER`;
  - `_bloquear_nunca_aberta(campanha) -> Campanha`: lock, depois `CAMPANHA_JA_ABERTA`
    se `aberta_em` está presente. Não consulta `estado` nem o relógio;
  - `_texto(nome)`: `TypeError` se não for `str`; `NOME_VAZIO` se vazio ou só com
    espaços;
  - `criar_campanha(nome, versao)`;
  - `alterar_campanha(campanha, *, nome=_MANTER, versao=_MANTER)`;
  - `remover_campanha(campanha)`.

  `uv run pytest tests/campanha/test_campanha_preparacao.py` DEVE passar.

**Checkpoint**: US1 funcional.

---

## Phase 4: User Story 2 — Definir período de coleta válido (Priority: P1)

**Goal**: período com duas datas incluídas, sem padrão.

**Independent Test**: períodos válidos e inválidos numa Campanha EM_PREPARACAO.

### Tests for User Story 2 ⚠️

- [X] T012 [US2] Acrescentar a `tests/campanha/test_campanha_preparacao.py` (DEVEM falhar
  antes de T013):
  - 01/04/2027 a 30/06/2027 gravado exatamente; período de um dia aceito;
  - `(None, fim)` e `(inicio, None)` → `PERIODO_INCOMPLETO`;
  - `inicio > fim` → `PERIODO_INVERTIDO`;
  - em cada rejeição, o período anterior é mantido (`linha` igual);
  - `datetime` no lugar de `date` → `TypeError`;
  - Campanha recém-criada tem `inicio` e `fim` nulos;
  - redefinir em preparação substitui o período.

### Implementation for User Story 2

- [X] T013 [US2] Implementar `definir_periodo(campanha, inicio, fim)` em
  `trajetoria/campanha/operacoes.py`:
  - tipo: `None` ou `type(x) is date`, rejeitando `datetime`;
  - acumula as violações e rejeita de uma vez;
  - grava `inicio` e `fim`.

  Testes de T012 DEVEM passar.

**Checkpoint**: US1 e US2 funcionais.

---

## Phase 5: User Story 3 — População ampla de todos os egressos (Priority: P1)

**Goal**: Campanha sem critérios abrange todas as Conclusões; avaliação e população no
momento da consulta.

**Independent Test**: com a fonte simulada incorporada, toda Conclusão é ELEGÍVEL e a
contagem é o total.

### Tests for User Story 3 ⚠️

- [X] T014 [US3] Escrever `tests/campanha/test_campanha_elegibilidade.py` (DEVEM falhar
  antes de T015):
  - com `incorporar_cenarios(fonte_simulada)` mais uma `conclusao()` sem nenhum
    atributo, a Campanha sem critérios avalia cada Conclusão como `ELEGIVEL`, com
    `pendencias == ()`;
  - `populacao_no_momento(c).count() == ConclusaoAcademica.objects.count()`;
  - `populacao_ampla` verdadeiro.

### Implementation for User Story 3

- [X] T015 [US3] Acrescentar a `trajetoria/campanha/consultas.py`:
  - os tipos do contrato: `Resultado`, `Criterio` (ordem `ANO_CONCLUSAO, UNIDADE, NIVEL,
    MODALIDADE, FORMA_OFERTA`), `MotivoPendencia` (`NAO_INFORMADO`, `NAO_ATENDE`),
    `Pendencia` e `Elegibilidade` com a propriedade `elegivel`;
  - `avaliar(campanha, conclusao)`: função pura, sem acesso ao banco e sem data,
    estruturada como uma lista de verificações por critério;
  - `populacao_no_momento(campanha)`: devolve
    `ConclusaoAcademica.objects.filter(_filtro(campanha))`, com `_filtro` devolvendo
    `Q()` quando não há critérios.

  Nada é gravado. Testes de T014 DEVEM passar.

**Checkpoint**: população ampla demonstrável (caso A).

---

## Phase 6: User Story 4 — População por período de conclusão (Priority: P1)

**Goal**: anos mínimo e máximo absolutos e inclusivos; definição de critérios com
validação completa.

**Independent Test**: Conclusões de 1998, 2019, 2020, 2024, 2025, 2031 e sem ano contra
2020–2024, só mínimo e só máximo.

### Tests for User Story 4 ⚠️

- [X] T016 [US4] Acrescentar (DEVEM falhar antes de T017):
  - em `tests/campanha/test_campanha_elegibilidade.py`:
    - **intervalo** 2020–2024: 2019 ✗, 2020 ✓, 2024 ✓, 2025 ✗ (`ANO_CONCLUSAO`,
      `NAO_ATENDE`);
    - **só mínimo** 2020: 2019 ✗, 2031 ✓;
    - **só máximo** 2024: 1998 ✓, 2025 ✗;
    - com `ano_minimo == ano_maximo`, só aquele ano;
    - `populacao_no_momento` coincide com cada caso;
  - em `tests/campanha/test_campanha_preparacao.py`:
    - `ano_minimo > ano_maximo` → `ANOS_INVERTIDOS`, critérios anteriores mantidos;
    - `definir_criterios()` sem argumentos volta a `populacao_ampla`;
    - os anos gravados não mudam quando consultados com `agora` anos depois (FR-021).

### Implementation for User Story 4

- [X] T017 [US4] Implementar
  `definir_criterios(campanha, *, ano_minimo=None, ano_maximo=None, unidades=None,
  niveis=None, modalidades=None, formas_oferta=None)` em
  `trajetoria/campanha/operacoes.py`. Ela **substitui** a definição inteira e acumula
  **todas** as violações com `campo`:
  - **anos**: `None` ou `type(x) is int and 0 < x <= 32767`, senão `ANO_INVALIDO`
    (inclui `bool`, `str`, `float`); `ANOS_INVERTIDOS` quando os dois são válidos e
    mínimo > máximo;
  - **conjuntos**: `None` grava `NULL`. `str` ou não iterável → `TypeError`. Elemento
    que não é `str` → `TypeError`. Coleção vazia → `CONJUNTO_VAZIO`. Elemento vazio ou só
    com espaços → `VALOR_VAZIO`. Válido grava `sorted(set(valores))`, textos intactos.

  Em `trajetoria/campanha/consultas.py`, acrescentar o critério `ANO_CONCLUSAO` a
  `avaliar`:
  - `NAO_INFORMADO` se `ano_conclusao is None`;
  - `NAO_ATENDE` se fora de `[ano_minimo, ano_maximo]`, com limite ausente sem
    restringir.

  Acrescentar também a `_filtro` os `ano_conclusao__gte` e `__lte`. Testes de T016
  DEVEM passar.

**Checkpoint**: casos B e recorte temporal sem janela relativa.

---

## Phase 7: User Story 5 — Determinar e explicar a elegibilidade (Priority: P1)

**Goal**: resultado determinístico, por Conclusão, com todas as pendências.

**Independent Test**: Pessoa C (Serra 2022 / Cefor 2025) contra 2020–2024.

### Tests for User Story 5 ⚠️

- [X] T018 [US5] Acrescentar a `tests/campanha/test_campanha_elegibilidade.py`:
  - **Pessoa C** (`SIM-P-0003` incorporada): a Conclusão de Serra 2022 é `ELEGIVEL`; a de
    Cefor 2025 é `NAO_ELEGIVEL` com `(ANO_CONCLUSAO, NAO_ATENDE)`. Não existe função de
    elegibilidade que receba Pessoa;
  - **determinismo**: a mesma Campanha e Conclusão avaliadas com a Campanha em
    preparação, em coleta (por ORM) e encerrada dão resultados iguais (`==`);
  - **nada gravado**: `django_assert_num_queries(0)` em torno de `avaliar` com instâncias
    já carregadas.

### Implementation for User Story 5

- [X] T019 [US5] Sem código novo esperado. Se T018 falhar, corrigir `avaliar` em
  `trajetoria/campanha/consultas.py`, mantendo-a pura.

**Checkpoint**: caso F; avaliação explicável e determinística.

---

## Phase 8: User Story 6 — Abrir a coleta; Versão RASCUNHO impede (Priority: P1)

**Goal**: abertura explícita com todas as condições; nunca publica Versão.

**Independent Test**: baseline 003 (RASCUNHO) rejeitada; Versão de teste publicada
abre no período.

### Tests for User Story 6 ⚠️

- [X] T020 [US6] Acrescentar a `tests/campanha/test_campanha_ciclo.py` (DEVEM falhar
  antes de T021), com período de 01/04/2027 a 30/06/2027:
  - **Versão RASCUNHO**: `abrir` com a baseline de `materializar()` → `rejeita(
    (VERSAO_NAO_PUBLICADA,), …)`; a baseline continua `RASCUNHO` e `publicada_em` nulo;
  - **Versão PUBLICADA**: `versao_publicada()`, `agora=momento(2027,4,1)` → `ABERTA`,
    `aberta_em == agora`, `estado == EM_COLETA`;
  - **período não definido**: `PERIODO_NAO_DEFINIDO`. Rascunho e sem período juntos →
    as duas violações numa rejeição;
  - **período incompleto ou inválido** não pode existir na Campanha (rejeitado em
    `definir_periodo`, T012), então a abertura só vê período ausente;
  - **antes do início** (31/03) → `FORA_DO_PERIODO`;
  - **dentro**: primeiro dia, dia intermediário e último dia → aceita;
  - **após o fim** (01/07, nunca aberta, estado já ENCERRADA) → `FORA_DO_PERIODO`;
  - **segunda abertura** em coleta → `JA_EM_COLETA`, `aberta_em` inalterado;
  - **abertura de Campanha aberta e já encerrada** → `JA_ENCERRADA`;
  - em todas as rejeições, `linha` e a Versão inalteradas; nenhuma Versão muda de
    estado por operação de Campanha.

### Implementation for User Story 6

- [X] T021 [US6] Implementar `SituacaoAbertura(Enum)` (`ABERTA`, `JA_EM_COLETA`,
  `JA_ENCERRADA`) e `abrir(campanha, *, agora=None)` em
  `trajetoria/campanha/operacoes.py`, conforme a seção `abrir` de
  [contracts/operacoes.md](contracts/operacoes.md):
  - lock da Campanha;
  - se `aberta_em` presente, devolve `JA_EM_COLETA` ou `JA_ENCERRADA` pelo `estado`;
  - senão, acumula `VERSAO_NAO_PUBLICADA` (Versão relida), `PERIODO_NAO_DEFINIDO` e,
    com período, `FORA_DO_PERIODO` se `not inicio <= hoje <= fim`;
  - rejeita tudo junto, ou grava `aberta_em = agora`.

  Nunca chama `publicar`. Testes de T020 DEVEM passar.

**Checkpoint**: MVP P1 completo (US1–US6): casos A, B, F, H, I.

---

## Phase 9: User Story 7 — Recortes por unidade, nível, modalidade e forma de oferta (Priority: P2)

**Goal**: os quatro critérios de conjunto: OR dentro do critério, AND entre critérios,
igualdade exata.

**Independent Test**: Conclusões de Serra, Vitória e Cefor, de níveis distintos.

### Tests for User Story 7 ⚠️

- [X] T022 [US7] Acrescentar a `tests/campanha/test_campanha_elegibilidade.py` (DEVEM
  falhar antes de T023), com os cenários da 001 incorporados:
  - **unidade**: sem critério, todas as unidades atendem. `{Serra}` → Serra ✓, Cefor ✗
    (`UNIDADE`, `NAO_ATENDE`). Pessoa C com `{Serra}`: só a de Serra;
  - **OR dentro**: `{Serra, Vitória}` → Serra ✓, Vitória ✓, Cefor ✗;
  - **nível** `{Técnico}`; **modalidade** `{A distância}`; **forma de oferta**
    `{Integrado}`: cada um com um caso ✓ e um ✗;
  - **AND entre**: nível `{Graduação}` + anos 2020–2024. Conclusão de Graduação 2017 ✗
    só por `ANO_CONCLUSAO`; Técnico 2021 ✗ só por `NIVEL`; Técnico 2014 ✗ com as duas
    pendências na ordem `ANO_CONCLUSAO, NIVEL`;
  - **igualdade exata**: `{Serra}` × Conclusões com unidade "serra" e "Campus Serra" →
    `NAO_ATENDE`.
- [X] T023 [US7] Escrever o teste de coerência em
  `tests/campanha/test_campanha_elegibilidade.py`. Para um conjunto de Campanhas de
  referência (ampla, intervalo, só mínimo, só máximo, cada critério de conjunto,
  combinação) e todas as Conclusões (cenários + `conclusao()` com atributos ausentes),
  verificar
  `set(populacao_no_momento(c)) == {x for x in todas if avaliar(c, x).elegivel}`.

### Implementation for User Story 7

- [X] T024 [US7] Em `trajetoria/campanha/consultas.py`, acrescentar a `avaliar` os
  critérios `UNIDADE`, `NIVEL`, `MODALIDADE` e `FORMA_OFERTA`, por uma tabela única
  `(Criterio, campo_da_campanha, atributo_da_conclusao)` percorrida em ordem:
  - `NAO_INFORMADO` se o atributo é `None`;
  - `NAO_ATENDE` se não está no conjunto.

  Acrescentar a `_filtro` os `atributo__in=lista`, a partir da mesma tabela, para não
  haver duas semânticas independentes. Testes de T022 e T023 DEVEM passar.

**Checkpoint**: casos C, D, E; coerência entre avaliação e consulta.

---

## Phase 10: User Story 8 — Encerrar preservando o significado (Priority: P2)

**Goal**: encerramento antecipado explícito e encerramento efetivo por fim do período.

**Independent Test**: encerrar antes do fim; consultar depois do fim sem nenhuma ação.

### Tests for User Story 8 ⚠️

- [X] T025 [US8] Acrescentar a `tests/campanha/test_campanha_ciclo.py` (DEVEM falhar
  antes de T026):
  - **encerramento antecipado** em 15/05/2027 → `ENCERRADA`, `encerrada_em == agora`,
    período intacto; `encerramento(c, agora=…) == (EXPLICITA, agora)`;
  - **fim do período** sem ação → `encerramento == (FIM_DO_PERIODO, início do dia
    01/07/2027 na timezone corrente)`, para Campanha aberta e para nunca aberta;
  - `encerrar` em Campanha aberta e `ENCERRADA` (explícita ou por data) →
    `JA_ENCERRADA`, sem escrita;
  - `encerrar` em Campanha **nunca aberta** → rejeição `CAMPANHA_NUNCA_ABERTA`, sem
    escrita (`encerrada_em` continua nulo), tanto com período em curso ou futuro
    (EM_PREPARACAO) quanto com período expirado (ENCERRADA pelo tempo);
  - após encerrar: Versão, Pesquisa, período, critérios e `aberta_em` consultáveis e
    iguais aos anteriores;
  - `encerramento` devolve `None` fora de `ENCERRADA`.

### Implementation for User Story 8

- [X] T026 [US8] Implementar `SituacaoEncerramento(Enum)` (`ENCERRADA`, `JA_ENCERRADA`) e
  `encerrar(campanha, *, agora=None)` em `trajetoria/campanha/operacoes.py`:
  - lock;
  - `aberta_em` ausente → rejeita `CAMPANHA_NUNCA_ABERTA`, em qualquer estado temporal;
  - aberta e `estado` `ENCERRADA` → `JA_ENCERRADA`;
  - aberta e `EM_COLETA` → grava `encerrada_em = agora`.

  Implementar `FormaEncerramento(Enum)` e `encerramento(campanha, *, agora=None)` em
  `trajetoria/campanha/consultas.py`. Testes de T025 DEVEM passar.

**Checkpoint**: estados D, E, F e encerramento sem job.

---

## Phase 11: User Story 9 — Impedir alteração silenciosa (Priority: P2)

**Goal**: depois da primeira abertura, nenhuma alteração nem remoção. Antes dela, tudo
é corrigível, mesmo com período expirado.

**Independent Test**: os casos M-A a M-F de estado × imutabilidade.

### Tests for User Story 9 ⚠️

- [X] T027 [US9] Escrever `tests/campanha/test_campanha_imutabilidade.py` com os casos
  de separação entre estado temporal e imutabilidade (período de 01/03/2027 a
  31/03/2027):
  - **M-A** — nunca aberta, `agora` dentro da janela: `EM_PREPARACAO`; cada escrita abaixo
    é aceita; `remover_campanha` aceita;
  - **M-B** — nunca aberta, `agora` 10/04/2027: `ENCERRADA`; `aberta_em` nulo; `abrir` →
    `FORA_DO_PERIODO`; `encerrar`
    → `CAMPANHA_NUNCA_ABERTA`, sem gravar; nome, Versão, período e critérios
    **editáveis**; **removível**;
  - **M-C** — caso M-B com `definir_periodo(01/06/2027, 30/06/2027)`: com `agora`
    10/04/2027, `EM_PREPARACAO` e `aberta_em` nulo (não é reabertura); `abrir` com
    `agora` 01/06/2027 é aceito;
  - **M-D** — aberta em 10/03/2027: `aberta_em` registrado; imutável;
  - **M-E** — M-D consultada em 10/04/2027: `ENCERRADA`; imutável;
  - **M-F** — M-D encerrada antecipadamente em 20/03/2027: `ENCERRADA`; imutável.

  Nos casos M-D, M-E e M-F, cada tentativa abaixo é rejeitada com `CAMPANHA_JA_ABERTA` e
  `linha(campanha)` fica idêntica:
  - `alterar_campanha(nome=…)`, `alterar_campanha(versao=outra_publicada)`;
  - `definir_periodo` alterando só `inicio`, só `fim` e ambos;
  - `definir_criterios` alterando cada um dos seis critérios isoladamente
    (`ano_minimo`, `ano_maximo`, `unidades`, `niveis`, `modalidades`, `formas_oferta`)
    e voltando à população ampla;
  - `remover_campanha`;
  - **combinação válida + inválida** (por exemplo, nome válido em Campanha aberta): nada
    aplicado.

  Em M-D (EM_COLETA), `encerrar` continua permitido. O "não admite participação" do
  caso M-B é verificado em T029 (US10), onde `admite_participacao` existe.

### Implementation for User Story 9

- [X] T028 [US9] Sem código novo esperado (guarda de T011, `definir_periodo` e
  `definir_criterios` já chamam `_bloquear_nunca_aberta`). Se T027 falhar, corrigir a
  operação faltante em `trajetoria/campanha/operacoes.py`.

**Checkpoint**: caso J.

---

## Phase 12: User Story 10 — Mesma Conclusão em várias Campanhas, sem convite (Priority: P2)

**Goal**: longitudinalidade, Campanhas sobrepostas sem prioridade, contrato para a 005,
população dinâmica.

**Independent Test**: três Campanhas em períodos distintos; duas sobrepostas; nova
incorporação durante a coleta.

### Tests for User Story 10 ⚠️

- [X] T029 [US10] Escrever `tests/campanha/test_campanha_longitudinal.py` (DEVEM falhar
  antes de T030):
  - **várias Campanhas**: 2025, 2027 e 2030 incluem a Conclusão ADS 2024
    (`conclusao(ano=2024, …)`), que é `ELEGIVEL` nas três; avaliar uma não altera as
    outras;
  - **sobrepostas**: duas Campanhas abertas, com critérios que incluem a mesma Conclusão
    → `campanhas_em_coleta_para(conclusao, agora=…)` devolve ambas, ordenadas por
    `(inicio, id)`, sem filtro de prioridade;
  - uma Conclusão sem Campanha aplicável → `()`;
  - uma Campanha encerrada e uma em preparação não aparecem;
  - **sem convite**: Campanha EM_COLETA + Conclusão ELEGIVEL →
    `admite_participacao(...)` verdadeiro. Também falso para Campanha nunca aberta e
    expirada (caso M-B de T027: período de 01/03 a 31/03/2027, `agora` 10/04/2027).
    Asserção de que o app não define nenhum modelo
    além de `Campanha` (`apps.get_app_config("campanha").get_models()`). Falso em
    EM_PREPARACAO, ENCERRADA e para Conclusão NAO_ELEGIVEL;
  - **população dinâmica**: com `FonteSimulada` incorporada só em parte (sem
    `SIM-P-0005`, Técnico Alegre 2019), uma Campanha de nível `{Técnico}` é aberta em
    01/04/2027 e contada. Em seguida, `incorporar_pessoa(fonte, "SIM-P-0005")`. Em
    15/04/2027, a nova Conclusão está em `populacao_no_momento`, a contagem cresceu 1,
    `admite_participacao` é verdadeiro e `linha(campanha)` não mudou (nenhuma associação
    gravada).

### Implementation for User Story 10

- [X] T030 [US10] Implementar em `trajetoria/campanha/consultas.py`:
  - `admite_participacao(campanha, conclusao, *, agora=None)`:
    `estado(...) is EM_COLETA and avaliar(...).elegivel`;
  - `campanhas_em_coleta_para(conclusao, *, agora=None)`:
    `Campanha.objects.filter(aberta_em__isnull=False, encerrada_em__isnull=True,
    fim__gte=_hoje(agora)).order_by("inicio", "id")`, filtrado por `avaliar`, devolvido
    como tupla.

  Sem prioridade, ranking ou exclusividade (DP-404). Testes de T029 DEVEM passar.

**Checkpoint**: casos K e L; contrato para a 005 completo.

---

## Phase 13: User Story 11 — Dados ausentes e configurações inválidas (Priority: P3)

**Goal**: `NAO_INFORMADO` conservador; configurações inválidas com todas as pendências;
`NULL` × `[]` inequívocos.

**Independent Test**: Conclusões sem unidade, nível, modalidade, forma de oferta ou ano;
definições inválidas.

### Tests for User Story 11 ⚠️

- [X] T031 [P] [US11] Acrescentar a `tests/campanha/test_campanha_elegibilidade.py`:
  - **atributo ausente** com critério definido: para cada um dos cinco critérios,
    `conclusao()` sem o atributo → `NAO_ELEGIVEL` com `(criterio, NAO_INFORMADO)`. O
    valor não é deduzido de curso nem de outra Conclusão da mesma Pessoa
    (`conclusao(pessoa=…)` com o atributo presente);
  - **sem critério**: o mesmo atributo ausente não tem efeito;
  - **NAO_INFORMADO × NAO_ATENDE**: uma Conclusão com unidade ausente e ano fora do
    intervalo → `(ANO_CONCLUSAO, NAO_ATENDE), (UNIDADE, NAO_INFORMADO)`, nessa ordem;
  - a Conclusão sem o atributo não aparece em `populacao_no_momento`.
- [X] T032 [P] [US11] Acrescentar a `tests/campanha/test_campanha_preparacao.py`:
  - **todas as violações numa rejeição**: `unidades=[]`, `niveis=["  "]`,
    `ano_minimo="2020"`, `ano_maximo=True` → `CONJUNTO_VAZIO` (campo `unidades`),
    `VALOR_VAZIO` (`niveis`) e dois `ANO_INVALIDO`; critérios anteriores mantidos;
    `ano_minimo=0` → `ANO_INVALIDO`;
  - **`NULL` × `[]`**: `unidades=None` grava `NULL` e não restringe; `unidades=[]` é
    rejeitado e nunca gravado;
  - **conjunto**: `["Vitória", "Serra", "Serra"]` grava `["Serra", "Vitória"]`;
    `[" Serra"]` é gravado exatamente, sem normalização;
  - **tipos**: `unidades="Serra"` (str) e `unidades=[1]` → `TypeError`.

### Implementation for User Story 11

- [X] T033 [US11] Sem código novo esperado. Se T031 ou T032 falharem, corrigir `avaliar`
  ou `_filtro` em `trajetoria/campanha/consultas.py`, ou `definir_criterios` em
  `trajetoria/campanha/operacoes.py`.

**Checkpoint**: caso G; todas as histórias verdes.

---

## Phase 14: Polish & Cross-Cutting Concerns

**Purpose**: aceitação ponta a ponta e verificação. Nenhuma funcionalidade nova.

- [X] T034 Escrever `tests/campanha/test_campanha_aceitacao.py`:
  - **casos A–L** da spec, um teste cada, reaproveitando auxiliares e com nomes que
    citam o caso;
  - **SC-009**:
    - o app `campanha` tem exatamente um modelo;
    - nenhum modelo do projeto se chama Participacao, Resposta, Convite, Destinatario,
      Segmento, Regra, Agendamento, MembroCampanha, Populacao ou Snapshot;
    - os campos de `Versao` e de `ConclusaoAcademica` são exatamente os listados nos
      data-models da 002 e da 001;
  - a baseline da 003 continua `RASCUNHO` depois de toda a suíte da Campanha.
- [X] T035 [P] Atualizar `README.md` com o link "Campanhas e população elegível:
  [quickstart da Feature 004](specs/004-campanhas-populacao-elegivel/quickstart.md)".
  Ajustar `specs/004-campanhas-populacao-elegivel/quickstart.md` só se nomes de
  arquivos de teste mudarem na implementação. A tabela atual tem 7 arquivos.
  População e coerência ficam em `test_campanha_elegibilidade.py`, e a população
  dinâmica em `test_campanha_longitudinal.py`.
- [X] T036 Rodar e registrar o resultado:
  - `uv run pytest` (suíte completa: 001, 002, 003 e 004 verdes, sem alteração nos testes
    anteriores);
  - `uv run ruff check .`;
  - `uv run python manage.py check`;
  - `uv run python manage.py makemigrations --check --dry-run`;
  - `git diff --stat main -- trajetoria/academico trajetoria/fonte_academica
    trajetoria/instrumento trajetoria/formulario_2024 tests/test_*.py tests/instrumento`
    vazio.
- [X] T037 Conferir a Constitution e a Definition of Done e registrar em
  `specs/004-campanhas-populacao-elegivel/plan.md` uma "Revisão pós-implementação":
  - gate mantido;
  - nada da lista "Limites" foi criado;
  - nenhum log ou dado pessoal novo;
  - DP-401 a DP-409 e as herdadas continuam abertas, sem regra implícita;
  - Complexity Tracking continua vazio.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (T001)** → **Foundational (T002–T009)** → histórias → **Polish (T034–T037)**.
- Na Foundational:
  - T002, T004 e T007 em paralelo; T003 depois de T002;
  - T005 depende de T001; T006 de T005;
  - T008 em paralelo com T005; T009 depende de T005 (e T008 deve falhar antes).

### User Story Dependencies

- **US1** (T010–T011): só da Foundational.
- **US2** (T012–T013): US1 (usa `criar_campanha` e o guarda).
- **US3** (T014–T015): Foundational e US1.
- **US4** (T016–T017): US3 (estende `avaliar` e `_filtro`).
- **US5** (T018–T019): US4.
- **US6** (T020–T021): US2 (período) e US1.
- **US7** (T022–T024): US4 (estende a tabela de critérios).
- **US8** (T025–T026): US6.
- **US9** (T027–T028): US2, US4, US6 e US8.
- **US10** (T029–T030): US6 e US7.
- **US11** (T031–T033): US4 e US7.

### Within Each User Story

- Testes primeiro; DEVEM falhar quando trazem comportamento novo.
- `consultas.py` e `operacoes.py` são editados sequencialmente entre histórias.

### Parallel Opportunities

- Foundational: T002, T004, T007 (arquivos distintos).
- Depois de US6: as trilhas US7 → US11 e US8 → US9 podem andar em paralelo, mas
  `consultas.py`, `operacoes.py` e `test_campanha_elegibilidade.py` exigem coordenação.
- US11: T031 e T032 (arquivos distintos).
- Polish: T035 em paralelo com T034.

---

## Parallel Example: Foundational

```bash
Task: "T002 Auxiliares em tests/campanha/construcao.py"
Task: "T004 Testes de CHECK em tests/campanha/test_campanha_modelo.py"
Task: "T007 Vocabulário de rejeição em trajetoria/campanha/regras.py"
```

---

## Implementation Strategy

### MVP First

1. Setup + Foundational (T001–T009).
2. US1 → US6 (T010–T021): Campanha criada, período, população ampla e por ano,
   elegibilidade explicável, abertura protegida contra RASCUNHO.
3. **STOP and VALIDATE**: `uv run pytest tests/campanha`.

### Incremental Delivery

4. US7 (recortes + coerência) → US8 (encerramento) → US9 (imutabilidade) → US10
   (longitudinal, sem convite, população dinâmica, contrato para a 005) → US11 (bordas).
5. Polish (T034–T037).

---

## Decisões Pendentes preservadas

Nenhuma task resolve DP-401 a DP-409, 002/DP-001, 002/DP-002, 003/DP-301, 003/DP-302,
001/DP-001, 001/DP-004, 001/DP-005, 001/DP-007 ou 001/DP-008. Em particular:

- não há prioridade entre Campanhas (DP-404);
- não há fotografia da população (DP-408);
- não há prorrogação nem reabertura (DP-405);
- não há ponto de entrada para as operações (DP-402);
- a baseline da 003 não é publicada (002/DP-001).

## Notes

- 37 tasks:
  - 16 escrevem testes;
  - 2 criam auxiliares e fixtures de teste;
  - 2 são de verificação final;
  - 17 são de implementação, configuração ou documentação. Três delas (T019, T028, T033)
    são condicionais: só corrigem se os testes da história falharem. Os
  arquivos de produção são `apps.py`, `models.py`, `regras.py`, `operacoes.py`,
  `consultas.py` e `0001_initial.py`.
- **Complexity check dos módulos**:
  - `regras.py` tem consumidor em `operacoes.py` e nos testes (motivos), no mesmo padrão
    do `instrumento`;
  - `consultas.py` é consumido por `operacoes.py` (`estado`), pelos testes e pela futura
    005;
  - `operacoes.py` é o único caminho de escrita.

  Fundir qualquer um deles misturaria escrita e leitura sem ganho. Nenhum serviço
  adicional.
- Commit após cada checkpoint.
