---

description: "Tasks da Feature 013 — Exportações analíticas e contrato de dados para o GeN"
---

# Tasks: Exportações analíticas e contrato de dados para o GeN

**Input**: design documents de `specs/013-exportacoes-analiticas-gen/`.

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/exportacao.md](contracts/exportacao.md),
[contracts/pacote-de-dados.md](contracts/pacote-de-dados.md), [quickstart.md](quickstart.md).

**Stack** ([ADR 0001](../../docs/adr/0001-stack-inicial.md)): Python 3.13, Django 5.2 LTS,
PostgreSQL 16+, uv, pytest + pytest-django, ruff.

- **Dependências novas**: `XlsxWriter>=3.2,<4` (produção) e `openpyxl>=3.1,<4` (só `dev`)
  (research R11).

**Persistência**: **0 modelos, 0 migrations**.

- **0 views, 0 urls, 0 templates, 0 management commands, 0 jobs**.
- O pacote `trajetoria/exportacao/` **não** é app Django e **não** entra em
  `INSTALLED_APPS` (research R2).
- Fora dele, as únicas alterações são:
  - um campo em `trajetoria/analitico/consultas.py`;
  - uma variável em `config/settings.py`;
  - `pyproject.toml` e `uv.lock`;
  - a lista de dependências esperada em três testes de fronteira (008, 009, 012);
  - a fixture `cenario` da 012 extraída para `tests/analitico/construcao.py`, sem mudar
    comportamento;
  - testes acrescentados em `tests/analitico/test_analitico_dataset.py`
    (plan, "Alterações em features anteriores").

**Tests**: obrigatórios e escritos **antes** da implementação correspondente
(test-first). A feature toca exportações, preservação histórica, longitudinalidade,
associação de respostas e privacidade (Princípio XXVI).

- Teste de comportamento novo DEVE falhar primeiro.
- Teste que só confirma o que uma história anterior já entregou pode passar de imediato.
  Se falhar, a correção vai no módulo indicado.

**Organization**: Setup, Foundational, uma fase por história da spec (US1–US12, na ordem
de prioridade) e Polish. Tarefas no mesmo arquivo nunca têm [P].
`trajetoria/exportacao/dataset.py`, `formatos.py` e `contrato.py` são editados **em
sequência**, história após história.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US12).

## Convenções para todas as tarefas

**Escopo**

- Nada grava: nem banco, nem disco, nem log de conteúdo (spec FR-005, FR-114). As funções
  devolvem objetos de valor ou `bytes`.
- Toda função pública recebe o **snapshot** explicitamente. NÃO criar
  `exportar_campanha`, "último", "atual", "vigente" nem parâmetro de formato (FR-001,
  FR-132).
- Sem UI, view, rota, template, admin, endpoint, management command, regra de governança
  ("pode exportar" **não** existe), job, cache, classe base de exportador, registro de
  serializadores, formato long, tabela de Respostas, dimensão de Opções.
- **Não altere** `trajetoria/academico/`, `instrumento/`, `campanha/`, `participacao/`,
  `fonte_academica/`, `governanca/`, `acompanhamento/`, `demonstracao/`, `interface/`,
  `editor/`. Em `trajetoria/analitico/`, só o acréscimo de T005.

**Fonte** (research R1)

- Registros, contexto, elegibilidade, Participação, Respostas e percurso vêm **só** de
  `trajetoria.analitico.consultas.linhas_do_dataset(snapshot)`.
- As contagens vêm de `indicadores_do_snapshot(snapshot)`.
- A estrutura vem de `trajetoria.instrumento.conteudo.conteudo_da_versao(snapshot.campanha.versao)`.
- A Campanha vem de `snapshot.campanha`, só os campos `id`, `nome`, `inicio`, `fim` e
  `aberta_em`. **Nunca** `encerrada_em` nem o nome da Pesquisa.
- **Única** leitura da 001: `RegistroDoSnapshot.objects.filter(snapshot=snapshot).values_list("conclusao_id", "conclusao__pessoa_id")`
  (research R5). `exportacao` **não** importa `trajetoria.academico`,
  `trajetoria.participacao` nem `trajetoria.campanha`.

**Valores lógicos** (research R3): `None` (ausência), `bool`, `int`, `datetime.date`,
`datetime.datetime` com fuso (via `django.utils.timezone.localtime`) e `str`.

- Nunca `""` como valor.
- Nos formatos, testar `bool` **antes** de `int`.

**Dados de teste** (research R17)

- Somente dados fictícios, com chave fictícia.
- Cenários construídos com `tests/analitico/construcao.py`, com as Campanhas de coleta
  no passado e `capturar_snapshot`. Usar o instrumento `tests/participacao/construcao.instrumento()`:
  - Seção 1:
    - `unica` com regra "Não" → finaliza;
    - `unica_outro` com "Outro:" (complemento);
    - `multipla` (A, B, C, "Outro:"; opcional);
    - `texto`;
    - `escala` 1–5;
    - `campus`.
  - Seção 2: `posterior` (texto opcional).
- Alteração acadêmica e `encerrada_em` retroativo **só** por `update` direto no teste, com
  o comentário "simula 001/DP-005" ou "simula encerramento retroativo (spec C13)".

**Privacidade**: mensagens de erro citam motivo, `id` de snapshot, Pergunta ou Opção, nome
de coluna, número de linha e contagens. Nunca citam valor acadêmico, Resposta,
identificador interno de Pessoa ou Conclusão, pseudônimo nem chave. Nenhum log novo.

---

## Phase 1: Setup

**Purpose**: dependências, configuração e pacote vazio.

- [X] T001 Acrescentar `"XlsxWriter>=3.2,<4"` a `[project].dependencies` e `"openpyxl>=3.1,<4"` a
  `[project.optional-dependencies].dev` em `pyproject.toml`. No mesmo arquivo:
  - registrar o marcador em `[tool.pytest.ini_options]`:
    `markers = ["volume: medição de volume (SC-012), fora da suíte padrão"]`;
  - estender `addopts` para `"--strict-markers -m 'not volume'"`;
  - rodar `uv lock` e `uv sync --extra dev` para atualizar `uv.lock`;
  - **no mesmo passo**, para a suíte continuar verde, atualizar a lista esperada para
    `["Django>=5.2,<5.3", "psycopg[binary]>=3.2,<3.4", "XlsxWriter>=3.2,<4"]` nos três
    testes que a comparam literalmente:
    - `tests/interface/test_interface_fronteiras.py::test_sem_dependencia_nova_nem_script`
      (008);
    - `tests/editor/test_editor_fronteiras.py::test_sem_script_recurso_externo_nem_dependencia_nova`
      (009);
    - `tests/analitico/test_analitico_fronteiras.py::test_sem_dependencia_nova` (012);
  - em cada um, o comentário "XlsxWriter introduzida pela Feature 013 (research R11);
    esta feature não acrescenta dependência". O resto de cada teste (scripts, recursos
    externos) fica inalterado.
- [X] T002 Acrescentar a `config/settings.py`, logo após `TRAJETORIA_DEMONSTRACAO`:
  - a linha `TRAJETORIA_CHAVE_PSEUDONIMIZACAO = os.environ.get("TRAJETORIA_CHAVE_PSEUDONIMIZACAO", "")`;
  - um comentário: chave dedicada da pseudonimização analítica (Feature 013, FR-027),
    distinta de `SECRET_KEY`, fora do repositório, sem valor padrão utilizável;
    custódia e rotação em DP-1301.
- [X] T003 Criar `trajetoria/exportacao/__init__.py`, só com docstring e **sem**
  `apps.py`, `models.py` ou `migrations/`. A docstring descreve:
  - exportação analítica de um snapshot explícito (spec 013);
  - CSV + XLSX do mesmo dataset lógico;
  - sem interface, e quem expuser restringe à CPAEG ativa e nada dá à CSAEG
    (FR-102, FR-103);
  - decisões pendentes respeitadas: DP-1201, DP-1301, DP-1302, DP-1303, 002/DP-006,
    005/DP-503, 006/DP-601.
- [X] T004 [P] Criar `tests/exportacao/__init__.py` e `tests/exportacao/leitura.py`
  (auxiliares, não testes), com:
  - `reverter(campo: str) -> str`: remove um `'` inicial, se houver;
  - `ler_csv(pacote: bytes) -> dict[str, list[list[str]]]`:
    - abre o ZIP;
    - exige exatamente `["dados.csv", "dicionario.csv", "metadados.csv"]`, nessa ordem;
    - decodifica UTF-8 estrito, falhando se houver BOM;
    - lê com `csv.reader` e aplica `reverter` a todo campo;
  - `ler_xlsx(conteudo: bytes) -> dict[str, list[list]]`: `openpyxl.load_workbook`; exige
    as abas `["Dados", "Dicionário", "Metadados"]`;
  - `formulas(conteudo: bytes) -> list[str]`: coordenadas de células com
    `data_type == "f"`;
  - `normalizar_csv(tabelas)` e `normalizar_xlsx(tabelas)`: convertem as três tabelas lidas
    para os valores lógicos de data-model, com `None`, `bool`, `int`, `date` e `str`
    (momentos comparados como texto ISO). No CSV, o tipo de cada campo vem do próprio
    pacote:
    - Dados: `tipo_valor` da linha `elemento == "coluna"` do Dicionário com o mesmo nome;
    - Metadados: a coluna `tipo` de cada linha;
    - Dicionário: os tipos fixos de data-model §2 (`contrato.CABECALHO_DICIONARIO`, com os
      tipos ao lado).

**Checkpoint**: `uv run pytest` verde; `uv run python manage.py check` sem erro;
`makemigrations --check` sem mudanças.

---

## Phase 2: Foundational

**Purpose**: o acréscimo na 012, o vocabulário de erro, as constantes do contrato e a
pseudonimização. Bloqueia todas as histórias.

### Testes primeiro

- [X] T005 Escrever em `tests/analitico/test_analitico_dataset.py` os testes de
  `LinhaDoDataset.perguntas_do_percurso`, com o cenário `cenario` de
  `tests/analitico/conftest.py`:
  - é o último campo, com padrão `None`;
  - **concluída** (`serra_info`): "Sim" em `unica` não tem regra, então o percurso segue
    para a Seção 2 e contém as Perguntas das Seções 1 e 2 (inclusive `inst.posterior`);
  - **recusa** (`vitoria_info`): as Perguntas da Seção 1;
  - **rascunho com Resposta fora do percurso** (`serra_eng`): as Perguntas da Seção 1, e
    `inst.posterior` está em `fora_do_percurso` e **não** em `perguntas_do_percurso`;
  - **sem Participação**: `None`;
  - **Versão com estrutura não suportada**, rascunho (mesma construção do teste existente
    de `fora_do_percurso = None`): `None`;
  - todos os testes existentes de `fora_do_percurso` continuam passando sem alteração.
- [X] T006 [P] Escrever `tests/exportacao/test_exportacao_regras.py`:
  - `Motivo` tem exatamente `SNAPSHOT_NAO_GRAVADO = "snapshot_nao_gravado"`,
    `CHAVE_AUSENTE = "chave_ausente"` e `CHAVE_INADEQUADA = "chave_inadequada"`;
  - `ExportacaoRecusada(motivo)` expõe `.motivo`;
  - `ExportacaoInconsistente` é distinta de `ExportacaoRecusada`;
  - `ValorNaoRepresentavel` é subclasse de `ExportacaoInconsistente` e expõe `.formato`,
    `.tabela`, `.coluna` e `.linha`;
  - o `str` de nenhuma delas contém o valor problemático (passar um valor sentinela e
    verificar que ele não aparece).
- [X] T007 [P] Escrever `tests/exportacao/test_exportacao_pseudonimos.py` (parte de
  fundação):
  - `pseudonimo("conclusao", uuid, chave)` é igual a
    `hmac.new(chave.encode(), f"conclusao:{uuid}".encode(), hashlib.sha256).hexdigest()`,
    num vetor fixo com UUID e chave literais;
  - o resultado tem 64 caracteres `[0-9a-f]` e não contém `uuid.hex` nem `str(uuid)`;
  - os domínios `pessoa` e `conclusao` dão resultados diferentes para o mesmo UUID;
  - domínio fora de {`pessoa`, `conclusao`} levanta `ValueError`;
  - `chave_de_pseudonimizacao()`, com a fixture `settings` do pytest-django:
    - valor vazio → `ExportacaoRecusada(CHAVE_AUSENTE)`;
    - 31 caracteres → `CHAVE_INADEQUADA`;
    - igual a `settings.SECRET_KEY` → `CHAVE_INADEQUADA`;
    - 32 ou mais caracteres → devolve a chave;
  - `ESQUEMA_PSEUDONIMIZACAO == "hmac-sha256-v1"`.

### Implementação

- [X] T008 Implementar em `trajetoria/analitico/consultas.py` o campo
  `perguntas_do_percurso: frozenset | None = None` como **último** campo de
  `LinhaDoDataset`, e atualizar a docstring:
  - substituir `_fora_do_percurso` por `_percurso(conteudo, respostas) -> frozenset | None`,
    que faz `percorrer(conteudo, respondidas(respostas))` → `perguntas_do_percurso(...)` e
    devolve `None` em `ParticipacaoRejeitada`;
  - em `linhas_do_dataset`, para toda Participação, calcular
    `percurso = _percurso(...) if percurso_executavel else None`;
  - manter `fora` como hoje: concluída → `frozenset()`; não concluída →
    `None if percurso is None else frozenset(da_participacao) - percurso`;
  - sem Participação → `perguntas_do_percurso=None`;
  - **nenhuma** consulta nova; nenhuma alteração em indicadores ou recortes.

  Fazer T005 passar.
- [X] T009 [P] Implementar `trajetoria/exportacao/regras.py`, no padrão de
  `trajetoria/analitico/regras.py`:
  - `Motivo` (Enum de três valores, com comentário da FR);
  - `ExportacaoRecusada(Exception)` com `.motivo` e um texto por motivo;
  - `ExportacaoInconsistente(Exception)`;
  - `ValorNaoRepresentavel(ExportacaoInconsistente)` com `formato`, `tabela`, `coluna` e
    `linha` (inteiro 1-based de dados), mensagem sem o valor;
  - docstring: nada é devolvido nem gravado quando qualquer uma é levantada.

  Fazer T006 passar.
- [X] T010 [P] Implementar `trajetoria/exportacao/contrato.py`, só com constantes, sem
  função de negócio:
  - `VERSAO_CONTRATO = 1`;
  - `ESQUEMA_PSEUDONIMIZACAO = "hmac-sha256-v1"`;
  - `GATILHOS_DE_ESCAPE = ("=", "+", "-", "@", "\t", "\r", "'")`;
  - `COLUNAS_BASE`: tupla de 14 `ColunaBase(nome, tipo_valor, proveniencia, descricao)`,
    com `@dataclass(frozen=True)`, na ordem e com as descrições **literais** de
    contracts/pacote-de-dados.md, "Descrições das colunas base";
  - `CABECALHO_DICIONARIO`: os 24 nomes de data-model §2, na ordem;
  - `CABECALHO_METADADOS = ("chave", "valor", "tipo")`;
  - `NOTAS`: dicionário ordenado `chave → texto` com `finalidade`, `nota_snapshot`,
    `nota_privacidade`, `nota_representacao`, `nota_proveniencia`, `nota_aplicabilidade` e
    `nota_escape_csv`,
    com os textos **literais** de contracts/pacote-de-dados.md, "Notas fixas";
  - os quatro modelos de descrição das colunas de Pergunta de data-model §2;
  - `TIPOS_DE_PERGUNTA`: `TipoPergunta → "escolha_unica" | "escolha_multipla" |
    "texto_curto" | "escala"`.
- [X] T011 Implementar `trajetoria/exportacao/pseudonimos.py`:
  - `chave_de_pseudonimizacao() -> str`: lê `settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO` e
    aplica as regras de T007;
  - `pseudonimo(dominio: str, identificador: UUID, chave: str) -> str`: HMAC-SHA-256 sobre
    `f"{dominio}:{identificador}"` em UTF-8, com `.hexdigest()`;
  - só `hmac`, `hashlib` e `django.conf.settings`; sem cache, sem persistência, sem log.

  Fazer T007 passar.

**Checkpoint**: `uv run pytest tests/analitico tests/exportacao` verde; a suíte da 012
inteira passa sem alteração além de T005.

---

## Phase 3: User Story 1 — Exportar um snapshot explicitamente escolhido em CSV (P1) 🎯 MVP

**Goal**: `dataset_exportado(snapshot)` com as três tabelas, de início com colunas base,
Dicionário das colunas base e Metadados de identificação e contagens, e
`exportar_csv(snapshot)` com o pacote ZIP.

**Independent Test**: capturar o `cenario` da 012, exportar em CSV, ler com
`leitura.ler_csv` e conferir as três tabelas, os cabeçalhos das colunas base e
`registros` = número de linhas.

### Testes primeiro

- [X] T012 [US1] Escrever `tests/exportacao/conftest.py`:
  - fixture `autouse` que define `settings.TRAJETORIA_CHAVE_PSEUDONIMIZACAO` como uma chave
    fictícia de 48 caracteres;
  - mover o corpo da fixture `cenario` de `tests/analitico/conftest.py`, com a dataclass
    `Cenario`, para `tests/analitico/construcao.py::cenario_de_referencia(inst) -> Cenario`.
    A fixture da 012 passa a ser só `return c.cenario_de_referencia(inst)`, sem mudar
    comportamento; rodar `uv run pytest tests/analitico` e manter verde;
  - fixtures próprias `inst` (`instrumento()`) e `cenario` (`cenario_de_referencia(inst)`)
    em `tests/exportacao/conftest.py`, **sem** importar de outro `conftest.py`;
  - fixture `snapshot` = `capturar_snapshot(cenario.campanha)`.
- [X] T013 [US1] Escrever `tests/exportacao/test_exportacao_formatos.py` (parte CSV):
  - `exportar_csv(snapshot)` devolve `bytes` de um ZIP com exatamente `dados.csv`,
    `dicionario.csv` e `metadados.csv`, nessa ordem;
  - cada arquivo é UTF-8 sem BOM (os bytes não começam com `EF BB BF`) e tem linhas
    terminadas em `\r\n`;
  - o cabeçalho de `dados.csv` começa com os 14 nomes de `COLUNAS_BASE`;
  - `dicionario.csv` tem o cabeçalho de 24 colunas e uma linha `coluna` por coluna de
    Dados, na mesma ordem;
  - `metadados.csv` tem cabeçalho `chave,valor,tipo`, e as chaves `snapshot`,
    `capturado_em` e `registros` batem com o snapshot;
  - número de linhas de Dados = `indicadores_do_snapshot(snapshot).registros`;
  - booleanos `true`/`false`; ausência = campo vazio; nenhum campo é `""` entre aspas;
  - chamada sem argumento ou com `cenario.campanha` → `TypeError`;
  - `SnapshotAnalitico(campanha=...)` não gravado → `ExportacaoRecusada(SNAPSHOT_NAO_GRAVADO)`;
  - sem chave → `ExportacaoRecusada(CHAVE_AUSENTE)`, sem consultar os registros
    (verificado com `CaptureQueriesContext`: nenhuma consulta a `analitico_registrodosnapshot`).

### Implementação

- [X] T014 [US1] Implementar `trajetoria/exportacao/dataset.py`:
  - `Tabela(cabecalho, linhas)` e `DatasetExportado(dados, dicionario, metadados)`, com
    `@dataclass(frozen=True)` e tuplas;
  - `dataset_exportado(snapshot)`, com os passos 1 a 8 de contracts/exportacao.md:
    - `TypeError` se não for `SnapshotAnalitico`;
    - `ExportacaoRecusada(SNAPSHOT_NAO_GRAVADO)` se `snapshot.pk` for `None` ou o snapshot
      não existir;
    - a chave via `chave_de_pseudonimizacao()` **antes** de qualquer consulta de registros;
    - Versão via `conteudo_da_versao`; não PUBLICADA → `ExportacaoInconsistente`;
    - mapa `conclusao_id → pessoa_id` numa consulta (Convenções, "Fonte");
    - para cada `LinhaDoDataset`, a linha com as colunas 1 a 10 (pseudônimos com
      `pseudonimo("conclusao", ...)` e `pseudonimo("pessoa", ...)`; elegibilidade;
      contexto) e 11 (`possui_participacao`). As colunas 12 a 14 ficam `None` até US4;
    - Dicionário: uma linha `coluna` por coluna base, com `ordem`, `tipo_valor`,
      `proveniencia`, `descricao` e `versao = str(conteudo.id)`; demais campos `None`;
    - Metadados, por enquanto, com `contrato_versao`, `pseudonimizacao_esquema`,
      `snapshot`, `capturado_em` (`localtime`), `campanha`, `versao` e `registros`, como
      tuplas `(chave, valor, tipo)`.
- [X] T015 [US1] Implementar `exportar_csv(snapshot) -> bytes` em
  `trajetoria/exportacao/formatos.py`:
  - `io.BytesIO` + `zipfile.ZipFile(..., "w", ZIP_DEFLATED)`;
  - uma entrada por tabela, com `ZipInfo(nome, date_time=(1980, 1, 1, 0, 0, 0))`,
    `compress_type=ZIP_DEFLATED` e `external_attr = 0o644 << 16`;
  - escrita por `io.TextIOWrapper(zip.open(info, "w"), encoding="utf-8", newline="")` e
    `csv.writer(delimiter=",", quotechar='"', doublequote=True, quoting=csv.QUOTE_MINIMAL,
    lineterminator="\r\n")`;
  - formatação por tipo em `_campo_csv(valor) -> str`:
    - `None` → `""`;
    - `bool` → `"true"`/`"false"`;
    - `int` → `str`;
    - `date`/`datetime` → `.isoformat()`;
    - `str` → o próprio valor. O escape entra em US9;
  - nenhum arquivo em disco.

  Fazer T013 passar.

**Checkpoint**: MVP — um snapshot exportado em CSV com as três tabelas.

---

## Phase 4: User Story 2 — Mesmo snapshot em XLSX com a mesma semântica (P1)

**Goal**: `exportar_xlsx(snapshot)` com as abas `Dados`, `Dicionário` e `Metadados`, com o
mesmo dataset lógico do CSV.

**Independent Test**: exportar o mesmo snapshot nos dois formatos, normalizar com
`leitura.py` e comparar com `dataset_exportado(snapshot)`.

### Testes primeiro

- [X] T016 [US2] Acrescentar a `tests/exportacao/test_exportacao_formatos.py` (parte
  XLSX):
  - `exportar_xlsx(snapshot)` tem exatamente as abas `["Dados", "Dicionário",
    "Metadados"]`, com o cabeçalho na linha 1;
  - booleanos lidos como `bool`, inteiros como `int`, datas como data, ausência como
    célula vazia (`None`);
  - `leitura.formulas(...) == []`;
  - nenhuma aba oculta, célula mesclada, filtro, validação ou formatação condicional
    (atributos do openpyxl);
  - **equivalência**: `normalizar_csv(ler_csv(...)) == normalizar_xlsx(ler_xlsx(...))`
    `== dataset_exportado(snapshot)`, tabela a tabela.

### Implementação

- [X] T017 [US2] Implementar `exportar_xlsx(snapshot) -> bytes` em
  `trajetoria/exportacao/formatos.py`:
  - `xlsxwriter.Workbook(buffer, {"in_memory": True, "strings_to_formulas": False,
    "strings_to_numbers": False, "strings_to_urls": False})`;
  - abas na ordem `Dados`, `Dicionário`, `Metadados`;
  - cabeçalho com um único `add_format({"bold": True})`;
  - `_escrever_celula(aba, linha, coluna, valor)`:
    - `None` → nada;
    - `bool` → `write_boolean`;
    - `int` → `write_number`;
    - `date` → `write_datetime` com formato `yyyy-mm-dd`;
    - `datetime` → `write_string(valor.isoformat())`;
    - `str` → `write_string`;
  - **nunca** `write()` genérico nem fórmula; sem gráficos, filtros, painéis congelados ou
    larguras;
  - devolver `buffer.getvalue()`.

  Fazer T016 passar.

**Checkpoint**: dois formatos, um dataset lógico.

---

## Phase 5: User Story 3 — Uma linha por registro, inclusive sem Participação (P1)

**Goal**: o universo completo do snapshot em Dados, com totais iguais aos da 012.

**Independent Test**: casos A, B, C e D, mais uma Pessoa com três Conclusões; contar
linhas e conferir os totais contra `indicadores_do_snapshot`.

### Testes primeiro

- [X] T018 [P] [US3] Escrever `tests/exportacao/test_exportacao_grao.py`:
  - Dados tem uma linha por registro, e o conjunto de `conclusao_analitica_id` é igual a
    `{pseudonimo("conclusao", id, chave)}` dos `conclusao_id` do snapshot;
  - **elegível sem Participação** (`serra_sem_participacao`): `possui_participacao =
    False`; Participação e Perguntas `None`; contexto e pseudônimos preenchidos;
  - **não elegível com Participação**: como em `tests/analitico/test_analitico_universo.py`,
    aplicar `simular_correcao` **antes** da captura, para tirar do critério uma Conclusão
    que já tem Participação. A linha existe com `elegivel_no_snapshot = False`, e a taxa
    calculada a partir de Dados pode passar de 1;
  - **Pessoa com três Conclusões** elegíveis (`conclusao(pessoa=p)` três vezes): três
    linhas, mesmo `pessoa_analitica_id`, três `conclusao_analitica_id` distintos;
  - totais derivados de Dados (elegíveis; com Participação; concluídas, separados por
    elegibilidade) iguais a `indicadores_do_snapshot`.

### Implementação

- [X] T019 [US3] Verificar `trajetoria/exportacao/dataset.py` contra T018. A implementação
  de T014 já itera todos os registros; corrigir aí se falhar. Não criar filtro de linhas.

**Checkpoint**: denominador preservado.

---

## Phase 6: User Story 4 — Contexto congelado e estado da Participação (P1)

**Goal**: colunas 4 a 14 exatamente conforme data-model §1.1 e spec FR-022 a FR-025.

**Independent Test**: alterar o contexto depois da captura; conferir valores congelados e
estados (concluída, rascunho, sem Participação) com as datas.

### Testes primeiro

- [X] T020 [P] [US4] Escrever `tests/exportacao/test_exportacao_contexto.py`:
  - **caso Q**: depois de `capturar_snapshot`, `simular_correcao` em todas as Conclusões
    do universo (unidade, curso, nível, modalidade, forma de oferta, ano); a exportação
    mostra os valores congelados (`retrato(snapshot)`);
  - Conclusões novas elegíveis criadas depois da captura não aparecem;
  - atributo não informado → `None`, nunca `"Não informado"`;
  - **caso P**: cursos homônimos ("Técnico em Informática" em Serra e Vitória) em duas
    linhas, distinguíveis só pela unidade; nenhuma coluna de código de curso;
  - **concluída** (`serra_info`): `True`, `True`, as duas datas como
    `timezone.localtime(...).date()`;
  - **rascunho** (`serra_eng`): `True`, `False`, data de início, conclusão `None`;
  - **sem Participação**: `False` e colunas 12 a 14 `None`;
  - **SQL**: em `CaptureQueriesContext` durante `dataset_exportado`, a única consulta que
    menciona `academico_conclusaoacademica` é a junção da referência à Pessoa, e nenhuma
    menciona `academico_pessoa`, nem colunas de contexto da Conclusão.

### Implementação

- [X] T021 [US4] Completar `trajetoria/exportacao/dataset.py`:
  - colunas 12 a 14 conforme spec FR-024;
  - `participacao_concluida = participacao.concluida` (`None` sem Participação);
  - datas com `timezone.localtime(instante).date()`.

  Fazer T020 passar.

---

## Phase 7: User Story 5 — Os quatro tipos de Pergunta e a aplicabilidade (P1)

**Goal**: colunas de Pergunta (data-model §1.2), preenchimento por linha (§1.3) e
validação de forma (research R7).

**Independent Test**: o instrumento de teste tem os quatro tipos, complemento em escolha
única e múltipla, regra "finaliza" e Seção 2. Conferir cada célula e as invariantes de
§1.3.

### Testes primeiro

- [X] T022 [P] [US5] Escrever `tests/exportacao/test_exportacao_perguntas.py`:
  - **cabeçalho exato** de Dados = os 14 nomes de `COLUNAS_BASE` + as colunas de Pergunta
    abaixo, nada além (nenhuma coluna constante de snapshot, Campanha ou Versão; spec
    FR-021);
  - **colunas, para cada Pergunta** de `inst`, na ordem Seção → Pergunta:
    - `pergunta_<hex>__aplicavel`;
    - escolha única/texto/escala: `pergunta_<hex>`;
    - múltipla: `pergunta_<hex>__opcao_<hex>` para A, B, C e "Outro:" na ordem;
    - `__complemento` por último em `unica_outro` e `multipla`;
  - **caso E**: a concluída tem `pergunta_<unica_outro>` = `"A"`, o texto exato da Opção;
  - **casos F e G**: com uma Participação concluída que responde `multipla` com [A] e
    outra com [A, C, "Outro:"] + complemento (caso H), as colunas de Opção são
    `True`/`False`, sem delimitador, e o complemento fica em `__complemento`;
  - escolha única com "Outro:" + complemento: valor `"Outro:"`, complemento na coluna
    própria;
  - **caso I**: texto com acentos, emoji, aspas, vírgula, `;`, quebra de linha e espaços
    nas pontas, idêntico no dataset;
  - **caso K**: escala `3` como `int`;
  - **caso M** (aplicável não respondida): `multipla` não respondida na concluída →
    `__aplicavel = True` e todas as colunas de Opção `None`, nunca `False`;
  - **caso L**: no rascunho `serra_eng`, `posterior` tem `__aplicavel = False` e valor
    `None`, embora a Resposta exista preservada;
  - na concluída `serra_info` ("Sim" segue para a Seção 2), `posterior` tem
    `__aplicavel = True` e valor `None` (outro exemplo do caso M);
  - **recusa** (`vitoria_info`): `pergunta_<unica> = "Não"`; Perguntas da Seção 1 com
    `True`; `posterior` com `False`; `participacao_concluida = True`;
  - **percurso não determinável**: rascunho numa Versão com estrutura não suportada,
    construída como no teste da 012 → aplicabilidade e valores `None`; Metadados com
    `participacoes_com_percurso_nao_determinavel = 1`;
  - **caso N**: Versão publicada com duas Perguntas de mesmo texto
    (`versao_publicada_de`) → chaves diferentes;
  - **caso O**: Opções "Sim" e "Sim, parcialmente" → colunas ou valores distintos;
  - **Versão derivada** (`instrumento_derivado(inst)`): nenhum nome de coluna de Pergunta
    em comum com `inst`;
  - **invariantes de §1.3** sobre todas as linhas do cenário;
  - **inconsistências** forçadas por ORM no teste, cada uma gerando
    `ExportacaoInconsistente` sem o valor na mensagem:
    - Resposta de escala com `texto` preenchido;
    - Opção de outra Pergunta em `opcao`;
    - Resposta da concluída numa Pergunta de `posterior`;
    - complemento preenchido numa Resposta cuja Opção escolhida não admite complemento;
    - Versão da Campanha devolvida ao estado `RASCUNHO` por `update` direto (forçado);
    - `tipo` de uma Pergunta alterado por `update` para valor fora de `TipoPergunta`.

### Implementação

- [X] T023 [US5] Completar `trajetoria/exportacao/dataset.py`:
  - **colunas de Pergunta** a partir de `conteudo.secoes` → `perguntas` → `opcoes`, com
    nomes `f"pergunta_{p.id.hex}"`, `__aplicavel`, `__opcao_{o.id.hex}` e
    `__complemento` (só se `any(o.complemento_textual for o in p.opcoes)`);
  - **unicidade**: `len(set(nomes)) == len(nomes)`, senão `ExportacaoInconsistente`;
  - **tipo** fora de `TipoPergunta` → `ExportacaoInconsistente`;
  - **preenchimento** conforme a tabela de data-model §1.3, com `P =
    linha.perguntas_do_percurso`;
  - **concluída** com `P is None` ou `respostas.keys() - P` não vazio →
    `ExportacaoInconsistente`;
  - **contagem** de não concluídas com `P is None` para os Metadados;
  - **validação de forma** de research R7 (`opcao_id` e `opcao` da Pergunta; `opcoes`
    não vazio e da Pergunta; `texto`, `escala` e `complemento` coerentes), sem revalidar
    os limites da escala.

  Fazer T022 passar.

**Checkpoint**: P1 de conteúdo declarado completa.

---

## Phase 8: User Story 6 — Dicionário suficiente para interpretar todas as colunas (P1)

**Goal**: Dicionário completo de data-model §2.

**Independent Test**: a correspondência um-para-um com Dados, os valores possíveis da
escolha única e as regras de navegação por posição.

### Testes primeiro

- [X] T024 [US6] Escrever `tests/exportacao/test_exportacao_dicionario.py`:
  - as linhas `elemento == "coluna"`, em ordem, têm `coluna` igual ao cabeçalho de Dados e
    `ordem` 1..n;
  - cada coluna de escolha única é seguida de uma linha `valor_possivel` por Opção, na
    ordem, com `opcao_texto` exato, `proveniencia = "declarado"` e `tipo_valor = "texto"`;
  - `unica`, Opção "Não": `opcao_regra_finaliza = True` e `opcao_regra_destino_secao =
    None`;
  - com uma Versão de teste com regra "ir para Seção 3" e encaminhamento de Seção
    (`versao_publicada_de` com `encaminhamento=`), `opcao_regra_destino_secao = 3` e
    `secao_encaminhamento_destino` igual à posição;
  - escala: `escala_inicio = 1`, `escala_fim = 5`, `escala_rotulo_fim = "Concordo
    totalmente"`, `escala_rotulo_inicio = None`;
  - proveniência: 1 a 3 e aplicabilidade `derivado`; 4 a 10 `institucional`; 11 a 14
    `coleta`; valores, Opções e complemento `declarado`;
  - as descrições das colunas base são iguais a `COLUNAS_BASE`;
  - `pergunta_tipo` ∈ os quatro valores;
  - `versao` é constante e igual a `str(inst.versao.id)`;
  - **nenhum** cabeçalho contém `sensib`, `canonic`, `global`, `linhagem` ou
    `equivalen`;
  - uma Pergunta sem nenhuma Resposta tem as mesmas linhas.

### Implementação

- [X] T025 [US6] Completar o Dicionário em `trajetoria/exportacao/dataset.py`:
  - linhas por coluna de Pergunta, com os campos de data-model §2;
  - `secao_encaminhamento_destino` e `opcao_regra_destino_secao` resolvidos por um mapa
    `id da Seção → posição` do próprio `conteudo`;
  - descrições pelos modelos de `contrato.py`;
  - linhas `valor_possivel` após a coluna de escolha única.

  Fazer T024 passar.

---

## Phase 9: User Story 7 — Nunca contexto atual, nunca snapshot implícito (P1)

**Goal**: garantir por teste FR-001 a FR-004.

**Independent Test**: assinaturas públicas e reprodução depois de mudanças na fonte.

### Testes primeiro

- [X] T026 [US7] Acrescentar a `tests/exportacao/test_exportacao_grao.py`:
  - as funções públicas de `trajetoria.exportacao.dataset` e `formatos` são exatamente
    `dataset_exportado`, `exportar_csv` e `exportar_xlsx` (por `__all__`), cada uma com um
    único parâmetro posicional `snapshot` (`inspect.signature`);
  - nenhum nome do pacote contém `atual`, `vigente`, `ultimo`, `recente` ou `campanha`
    como função pública;
  - **casos R e S**: dois snapshots da mesma Campanha, com uma Conclusão nova elegível
    entre eles, exportados um a um. Cada um reflete só o seu universo, e os cabeçalhos de
    Dados são iguais;
  - incorporar Conclusões novas elegíveis depois da captura não muda
    `dataset_exportado(snapshot)` (`==`).

### Implementação

- [X] T027 [US7] Declarar `__all__` em `trajetoria/exportacao/dataset.py`
  (`["DatasetExportado", "Tabela", "dataset_exportado"]`) e em
  `trajetoria/exportacao/formatos.py` (`["exportar_csv", "exportar_xlsx"]`). Corrigir o
  que T026 apontar.

**Checkpoint**: todas as histórias P1 entregues.

---

## Phase 10: User Story 8 — Metadados para reprodução e rastreabilidade (P2)

**Goal**: Metadados completos e fixos (data-model §3; research R8).

**Independent Test**: chaves, ordem, tipos e ausências; igualdade depois de renomear a
Pesquisa e gravar `encerrada_em` retroativo.

### Testes primeiro

- [X] T028 [US8] Escrever `tests/exportacao/test_exportacao_metadados.py`:
  - as chaves são exatamente as 27 de data-model §3, na ordem, com o `tipo` indicado;
  - os valores de Campanha (`id`, `nome`, `inicio`, `fim`, `aberta_em`), Versão (`id`,
    `designacao`, `titulo`, `publicada_em`) e snapshot (`id`, `capturado_em`) batem;
  - os momentos com `localtime` têm deslocamento explícito;
  - as contagens são iguais às derivadas de Dados e a `indicadores_do_snapshot`;
    `colunas_de_dados == len(dados.cabecalho)`;
  - as notas são iguais a `contrato.NOTAS`;
  - **ausentes**: o nome da Pesquisa (o valor `inst.versao.pesquisa.nome` não aparece em
    nenhuma célula), `encerrada_em`, qualquer chave com `gerado`, `export` ou `chave`, e o
    valor da chave de pseudonimização em qualquer célula;
  - **reprodutibilidade**: depois de `renomear_pesquisa(...)` e de
    `Campanha.objects.filter(pk=...).update(encerrada_em=...)` (simula encerramento
    retroativo, spec C13), `dataset_exportado(snapshot)` é igual ao de antes.

### Implementação

- [X] T029 [US8] Completar os Metadados em `trajetoria/exportacao/dataset.py`, com as 27
  linhas de data-model §3:
  - contagens de `indicadores_do_snapshot`, mais a contagem de percurso não determinável
    de US5;
  - notas e finalidade de `contrato.NOTAS`;
  - `versao_titulo` pode ser `None`;
  - nenhuma leitura de `encerrada_em` nem do nome da Pesquisa.

  Fazer T028 passar.

---

## Phase 11: User Story 9 — Unicode preservado e proteção contra fórmula (P2)

**Goal**: escape universal no CSV; XLSX sem fórmulas; valores não representáveis
recusados (research R10, R12).

**Independent Test**: textos com gatilhos, apóstrofo, acentos e emoji; round-trip nos dois
formatos.

### Testes primeiro

- [X] T030 [P] [US9] Escrever `tests/exportacao/test_exportacao_seguranca.py`, criando
  Participações concluídas com textos curtos `=1+1`, `+55 27`, `-abc`, `@x`, `\tabc`,
  `\rabc`, `'abc`, `ação 😀 "x", y` e `abc`:
  - **CSV bruto**, sem `reverter`:
    - os campos aparecem como `'=1+1`, `'+55 27`, `'-abc`, `'@x`, `'\tabc`, `'\rabc`,
      `''abc`; os sem gatilho, sem prefixo;
    - nenhum campo de nenhuma das três tabelas começa por gatilho não escapado;
  - com uma Pergunta de escala de início negativo (`versao_publicada_de`), o valor `-2`
    aparece **sem** apóstrofo;
  - **reversão universal** (`leitura.reverter` em todos os campos, sem tipo) devolve o
    dataset lógico exato;
  - **XLSX**: `formulas(...) == []`; a célula `=1+1` é texto `"=1+1"` sem apóstrofo;
  - a nota `nota_escape_csv` existe e descreve gatilhos e reversão;
  - **valor não representável** no XLSX (texto com `\x01` e texto de 32.768 caracteres,
    gravados por ORM no teste): `exportar_xlsx` → `ValorNaoRepresentavel(formato="xlsx")`
    sem o valor na mensagem; `exportar_csv` do mesmo snapshot funciona e preserva o
    valor;
  - texto literal `_x0041_`: round-trip XLSX intacto **ou** `ValorNaoRepresentavel`,
    conforme o comportamento verificado (research R12). Fixar no teste o comportamento
    escolhido e **registrar a decisão em research R12** (seção "Decisão tomada na
    implementação"), no mesmo commit.

### Implementação

- [X] T031 [US9] Em `trajetoria/exportacao/formatos.py`:
  - `_campo_csv` aplica a `str` o escape `"'" + valor if valor and
    valor[0] in GATILHOS_DE_ESCAPE else valor`;
  - antes de cada `write_string` do XLSX, `_verificar_xlsx(valor, tabela, coluna, linha)`
    levanta `ValorNaoRepresentavel` se `len(valor) > 32767` ou se houver caractere em
    U+0000–U+0008, U+000B, U+000C, U+000E–U+001F, U+FFFE ou U+FFFF (e, se T030 decidir,
    o padrão `_x[0-9A-Fa-f]{4}_`);
  - o retorno de `write_string` diferente de `0` também vira `ValorNaoRepresentavel`.

  Fazer T030 passar.

---

## Phase 12: User Story 10 — Ordem determinística e reprodutibilidade (P2)

**Goal**: ordem de linhas e colunas e igualdade entre exportações (research R4, R13).

**Independent Test**: Versão com posições variadas (caso T); duas exportações comparadas.

### Testes primeiro

- [X] T032 [US10] Acrescentar a `tests/exportacao/test_exportacao_formatos.py`:
  - **caso T**: Versão publicada (`versao_publicada_de`) com três Seções e Perguntas
    criadas fora de ordem e reordenadas pelas operações da 002 antes de publicar → colunas
    na ordem Seção → Pergunta → Opção, nunca por texto ou UUID;
  - linhas na ordem dos `conclusao_id` do snapshot, verificada pelos pseudônimos
    recalculados;
  - `exportar_csv` chamado duas vezes → bytes idênticos;
  - `exportar_xlsx` duas vezes → tabelas lidas idênticas;
  - `openpyxl` `wb.properties.created` == `capturado_em` em UTC, até o segundo;
  - **com outra chave**: só as duas colunas de pseudônimo diferem; o resto é idêntico.

### Implementação

- [X] T033 [US10] Em `exportar_xlsx` de `trajetoria/exportacao/formatos.py`, chamar
  `workbook.set_properties({"created": <capturado_em em UTC, sem tzinfo>})`. Corrigir a
  ordem em `dataset.py` se T032 falhar.

---

## Phase 13: User Story 11 — Contrato apropriado para consumo pelo GeN (P2)

**Goal**: fronteiras e neutralidade do contrato (spec FR-120 a FR-123, FR-100, FR-130).

**Independent Test**: inspeção estrutural do pacote e dos arquivos produzidos.

### Testes primeiro

- [X] T034 [P] [US11] Escrever `tests/exportacao/test_exportacao_fronteiras.py`:
  - **nomes de coluna**: todos casam com `^[a-z][a-z0-9_]*$`, com no máximo 81
    caracteres;
  - **imports** (AST) dos módulos de `trajetoria/exportacao/` só de:
    `trajetoria.exportacao`, `trajetoria.analitico`, `trajetoria.instrumento`, `django`,
    `xlsxwriter` e a biblioteca padrão. **Nenhum** de `trajetoria.academico`,
    `participacao`, `campanha`, `governanca`, `interface`, `editor`, `acompanhamento` ou
    `demonstracao`;
  - **identificadores** (AST: nomes de função, classe, variável, atributo e constante; sem
    comentários) não contêm `looker`, `google`, `bigquery`, `datastudio`, `sheets` nem
    `dashboard`;
  - o pacote não está em `INSTALLED_APPS` e não tem `apps.py`, `models.py`,
    `migrations/`, `views.py`, `urls.py`, `admin.py`, `management/` nem `templates/`;
  - nenhuma rota leva a `exportacao` (mesmo padrão de
    `tests/analitico/test_analitico_fronteiras.py`);
  - `trajetoria.governanca.regras.__all__` inalterado;
  - `call_command("makemigrations", "--check", "--dry-run")` sem mudanças;
  - **conteúdo dos arquivos** do `cenario`, nos dois formatos: nenhum `str(uuid)` nem
    `uuid.hex` de Pessoa, Conclusão, Participação ou registro; nenhum `id_externo`;
    nenhum nome de Pessoa; nenhuma ocorrência da chave;
  - **reconstrução sem o sistema**: com só `ler_csv`, calcular as taxas de início e de
    conclusão a partir de Dados e conferir com `indicadores_do_snapshot`.

### Implementação

- [X] T035 [US11] Corrigir em `trajetoria/exportacao/` o que T034 apontar. Não acrescentar
  módulo nem função.

---

## Phase 14: User Story 12 — Vínculo longitudinal por identificadores pseudonimizados (P2)

**Goal**: estabilidade, rotação e recusa (spec FR-026 a FR-029; casos U, V).

**Independent Test**: a mesma Conclusão em snapshots de duas Campanhas, com a mesma chave e
com outra; exportação sem chave.

### Testes primeiro

- [X] T036 [P] [US12] Acrescentar a `tests/exportacao/test_exportacao_pseudonimos.py`:
  - **caso U**: Conclusões com Participação em duas Campanhas encerradas (duas
    `campanha_aberta_no_passado` com o mesmo critério), capturadas e exportadas com a
    mesma chave → mesmos `conclusao_analitica_id` e `pessoa_analitica_id`;
  - com outra chave, a interseção dos pseudônimos das duas exportações é vazia;
  - **caso V**: com a chave vazia, curta ou igual a `SECRET_KEY`, `exportar_csv` e
    `exportar_xlsx` levantam `ExportacaoRecusada` e não devolvem nada;
  - Pessoa com duas Conclusões → mesmo `pessoa_analitica_id`;
  - nenhum valor de pseudônimo aparece em mensagem de erro.

### Implementação

- [X] T037 [US12] Corrigir em `trajetoria/exportacao/dataset.py` ou `pseudonimos.py` o que
  T036 apontar. Não criar cache, tabela nem persistência de pseudônimos.

---

## Phase 15: Polish & Cross-Cutting

- [X] T038 [P] Escrever `tests/exportacao/test_exportacao_consultas.py`:
  - o número de consultas de `dataset_exportado` é igual num snapshot com 3 e com 30
    registros (`CaptureQueriesContext`), sem orçamento fixo;
  - com `CaptureQueriesContext`, nenhuma consulta é `INSERT`, `UPDATE` ou `DELETE`;
  - `contagens()` de `tests/analitico/construcao.py` é igual antes e depois de exportar
    nos dois formatos.
- [X] T039 [P] Escrever `tests/exportacao/test_exportacao_volume.py`, com
  `pytestmark = pytest.mark.volume`:
  - 20.000 Conclusões fictícias criadas por `bulk_create`;
  - um instrumento de porte do formulário 2024 (a baseline de
    `tests/participacao/construcao.baseline_publicada()`), numa Campanha aberta no
    passado (`campanha_aberta_no_passado`);
  - **uma** Participação preenchida e concluída pelas operações da 005/006, como molde;
  - outras 3.999 Participações concluídas (20% do total) criadas por `bulk_create`, com as
    mesmas Respostas e seleções do molde (`Resposta` e `RespostaOpcao` copiadas por
    `bulk_create`). É dado fictício, escrito direto **só neste teste**, com o comentário
    "preparação de volume; só a exportação é medida";
  - `capturar_snapshot`, fora da medição;
  - medir `exportar_csv` e `exportar_xlsx` com `time.perf_counter`, cada um abaixo de 60
    segundos (SC-012, hipótese).
- [X] T040 Acrescentar a `tests/exportacao/test_exportacao_consultas.py` a verificação de
  **nada em disco** (spec FR-114):
  - com `monkeypatch`, substituir `tempfile.mkstemp`, `tempfile.NamedTemporaryFile`,
    `tempfile.TemporaryFile` e `tempfile.mkdtemp` por funções que falham;
  - rodar `exportar_csv` e `exportar_xlsx`: ambas completam sem acionar nenhuma delas;
  - com `monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))`, `tmp_path` continua vazio
    depois das duas exportações;
  - com `caplog` em nível `DEBUG`, nenhum registro de log contém valor de Resposta,
    contexto, pseudônimo ou a chave.
- [X] T041 Rodar `uv run ruff check .` e `uv run ruff format --check .` e corrigir.
- [X] T042 Rodar `uv run pytest` (suíte inteira, sem `volume`) e `uv run pytest -m volume
  tests/exportacao`, e seguir [quickstart.md](quickstart.md) do início ao fim. Registrar
  divergência, se houver, e corrigir.
- [X] T043 Revisar o diff contra "Sinais de over engineering" do [plan.md](plan.md) e as
  Convenções deste arquivo. Se aparecer modelo, migration, view, comando, cache, classe
  base, parâmetro de formato, leitura de `encerrada_em` ou do nome da Pesquisa, ou
  alteração em feature anterior além de T001 (lista de dependências nos três testes),
  T005, T008 e T012 (extração de `cenario_de_referencia`), remover. Conferir
  `git diff --stat main -- trajetoria/demonstracao trajetoria/governanca` vazio (spec
  FR-141).
- [X] T044 Marcar as tasks concluídas neste `tasks.md` e conferir que
  `checklists/requirements.md` continua válido.

---

## Dependencies & Execution Order

**Fases**:

- Setup (T001–T004) → Foundational (T005–T011) → histórias.
- **US1 (T012–T015)** cria `conftest.py`, `dataset.py` e `formatos.py`. Todas as histórias
  dependem dela.
- **US2 (T016–T017)** depende de US1 (mesmo arquivo de teste e `formatos.py`).
- **Arquivos de teste próprios, em paralelo com outras histórias**:
  - US3 (T018–T019), US4 (T020–T021) e US5 (T022–T023) dependem de US1;
  - US8 (T028–T029) depende de US5 (contagem de percurso não determinável);
  - US9 (T030–T031) depende de US2;
  - US11 (T034–T035) depende de US2;
  - US12 (T036–T037) depende de US1.
- **Mesmo arquivo de produção**: US3, US4 e US5 editam `dataset.py` **em sequência**
  (US3 → US4 → US5), embora os testes possam ser escritos em paralelo.
- **US6 (T024–T025)** depende de US5 (colunas de Pergunta).
- **US7 (T026–T027)** usa `test_exportacao_grao.py`, depois de US3.
- **US10 (T032–T033)** depende de US2 e US5 e usa `test_exportacao_formatos.py`, depois
  de US2.
- Polish (T038–T044) por último. T040 depois de T038 (mesmo arquivo).

**Dentro de cada história**: testes → implementação → checkpoint.

## Parallel Opportunities

- **Setup**: T004 ∥ T001–T003.
- **Foundational**: T006 ∥ T007 ∥ T009 ∥ T010 (arquivos distintos); T005 → T008; T007 →
  T011.
- **Depois de US1 (testes)**: T018 ∥ T020 ∥ T022 ∥ T036, em arquivos distintos.
- **Depois de US2 (testes)**: T030 ∥ T034.
- **Polish**: T038 ∥ T039; T040 depois de T038.

```text
# Exemplo — depois de US1:
T018 test_exportacao_grao.py       ∥   T020 test_exportacao_contexto.py
T022 test_exportacao_perguntas.py  ∥   T036 test_exportacao_pseudonimos.py
# implementação em dataset.py, em sequência: T019 → T021 → T023
```

## Implementation Strategy

1. **MVP (P1, US1)**: snapshot explícito → pacote CSV com Dados (colunas base),
   Dicionário (colunas base) e Metadados mínimos.
2. **P1 completo** (US2–US7):
   - XLSX equivalente;
   - universo integral;
   - contexto e estado;
   - quatro tipos e aplicabilidade;
   - Dicionário completo;
   - garantias de snapshot explícito.
3. **P2** (US8–US12):
   - Metadados completos e fixos;
   - escape e valores não representáveis;
   - reprodutibilidade;
   - contrato neutro para o GeN;
   - pseudônimos longitudinais.
4. **Polish**: consultas, volume, dependência no teste da 012, lint, suíte, quickstart,
   revisão de over engineering.

Cada checkpoint mantém a suíte completa verde.

## Resumo

- **Total**: 44 tasks.
  - 4 de setup;
  - 7 de base (3 de teste, 4 de implementação);
  - 26 de histórias (13 de teste, incluindo o `conftest.py`, e 13 de implementação ou
    verificação);
  - 7 de polish (3 de teste, incluindo a de volume, e 4 de verificação).
- **Tasks de teste**: 18 (T005, T006, T007, T012, T013, T016, T018, T020, T022, T024,
  T026, T028, T030, T032, T034, T036, T038, T040), mais T039 (volume).
- **Arquivos de produção**:
  - `trajetoria/exportacao/{__init__,contrato,regras,pseudonimos,dataset,formatos}.py`;
  - `trajetoria/analitico/consultas.py` (um campo);
  - `config/settings.py` (uma variável);
  - `pyproject.toml` e `uv.lock`.
- **Arquivos de teste**:
  - `tests/exportacao/{__init__,conftest,leitura}.py`;
  - `test_exportacao_{regras,pseudonimos,formatos,grao,contexto,perguntas,dicionario,
    metadados,seguranca,fronteiras,consultas,volume}.py`;
  - acréscimos e ajustes em `tests/analitico/{conftest,construcao,test_analitico_dataset,
    test_analitico_fronteiras}.py`, `tests/interface/test_interface_fronteiras.py` e
    `tests/editor/test_editor_fronteiras.py`.
