---

description: "Tasks da Feature 002 — Pesquisa, versão e estrutura do instrumento"
---

# Tasks: Pesquisa, versão e estrutura do instrumento

**Input**: Design documents from `specs/002-pesquisa-versao-instrumento/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Stack (confirmada; [ADR 0001](../../docs/adr/0001-stack-inicial.md))**: Python 3.13,
Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff. Nenhuma dependência
nova. A imutabilidade da Versão publicada é garantida **só pelas operações** e por
testes ([ADR 0002](../../docs/adr/0002-imutabilidade-versao-publicada.md) rejeitado nesta
fase): nenhum gatilho, hook de `save()`/`delete()`, sinal ou camada de permissões.

**Tests**: obrigatórios. Todas as histórias tocam invariantes constitucionais
(versionamento, preservação histórica, condicionais). Os testes vêm antes da
implementação e DEVEM falhar primeiro quando a história traz comportamento novo. Quando
a história só verifica comportamento já entregue (US9), os testes podem passar de
imediato; se falharem, a correção é no arquivo indicado.

**Organization**: tarefas agrupadas por história. `operacoes.py`,
`test_instrumento_estrutura.py`, `test_instrumento_modelo.py` e
`test_instrumento_navegacao.py` são compartilhados entre histórias: tarefas nesses
arquivos são sequenciais.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US9).

## Convenções para todas as tarefas

- Nada em `trajetoria/instrumento/` importa `trajetoria.academico` nem
  `trajetoria.fonte_academica` (FR-065). Nada da Feature 001 é alterado (FR-067).
- Toda operação de escrita segue o fluxo do [plan](plan.md#operações-e-rejeições):
  `transaction.atomic()` → `select_for_update()` na Versão → `VERSAO_PUBLICADA` se
  publicada → regras da operação na ordem do [contrato](contracts/operacoes.md) → grava.
- Rejeição é sempre `OperacaoRejeitada` com `Violacao(motivo, elemento, detalhe)`; o
  `detalhe` nunca contém dado pessoal (não há nenhum nesta feature).
- Textos são gravados exatamente como recebidos, sem `strip()` (R16). Texto vazio ou só
  com espaços é rejeitado com `TEXTO_VAZIO`; ausência é `None`.
- Testes de banco usam `pytestmark = pytest.mark.django_db`. Os auxiliares de teste
  são importados como `from tests.instrumento.construcao import …` (o `pythonpath = ["."]`
  do `pyproject.toml` torna `tests` importável).

## Limites desta lista (não criar)

- Campanha, Participação, Resposta, consentimento registrado, população, periodicidade.
- Admin, CRUD, URLs, API, comando de gestão, interface.
- Tabela de regras, motor de regras, expressões, condição de exibição.
- **Qualquer atributo, enumeração ou estratégia de momento de aplicação da regra**
  (FR-053) — por exemplo `AFTER_QUESTION`, `END_OF_SECTION`.
- Função de produção que execute o percurso (`proximo_passo` ou similar).
- JSON de configuração, JSON Schema, documento congelado por Versão.
- Tipos além dos quatro; validação de texto; mínimo/máximo de seleções; exclusividade.
- Banco global de perguntas ou Opções; códigos de pergunta; correspondência entre Versões.
- Estados além de `RASCUNHO` e `PUBLICADA`; histórico de edição; exclusão de Pesquisa ou
  Versão; correção editorial em Versão publicada.
- Datas de criação ou alteração nos modelos.
- Gatilhos PL/pgSQL, `RunSQL`, hooks de `save()`/`delete()`, sinais ou camada de
  permissões para imutabilidade (ADR 0002 rejeitado nesta fase).
- Mudança de tipo de pergunta (FR-062: tipo imutável; remover e recriar).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: app Django vazio, registrado e verificável.

- [X] T001 [P] Criar o esqueleto do app:
  - `trajetoria/instrumento/__init__.py` (vazio);
  - `trajetoria/instrumento/apps.py` com `InstrumentoConfig(AppConfig)`,
    `name = "trajetoria.instrumento"`, `verbose_name = "Instrumento de pesquisa"`;
  - `trajetoria/instrumento/migrations/__init__.py` (vazio);
  - diretório `tests/instrumento/` **sem** `__init__.py` (como `tests/`).
- [X] T002 Em `config/settings.py`, acrescentar `"trajetoria.instrumento"` a
  `INSTALLED_APPS` depois de `"trajetoria.academico"` e atualizar o comentário: continua
  sem admin, auth, sessions, contenttypes e messages (R17). Depende de T001. Verificar com
  `uv run python manage.py check`.

**Checkpoint**: `manage.py check` sem erros.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: modelos, migrações, vocabulário de rejeição, leitura e esqueleto das
operações, usados por todas as histórias.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T003 [P] Implementar `trajetoria/instrumento/models.py` conforme
  [data-model.md](data-model.md). Docstring do módulo citando o data-model e a regra
  "`NULL` = ausente; cadeia vazia proibida". Reusar o padrão `_nao_vazio(campo, nome)` de
  `trajetoria/academico/models.py`, copiando-o (não importar do app `academico`).
  - **Enums** (`models.TextChoices`):
    - `EstadoVersao`: `RASCUNHO`, `PUBLICADA` (valor = nome);
    - `TipoPergunta`: `ESCOLHA_UNICA`, `ESCOLHA_MULTIPLA`, `TEXTO_CURTO`, `ESCALA`
      (valor = nome).
  - **`Pesquisa`**: `id` UUID (`primary_key=True, default=uuid.uuid4,
    editable=False`); `nome` texto obrigatório. CHECK não vazio em `nome`. Sem unicidade
    de nome (R18).
  - **`Versao`**:
    - `id` UUID;
    - `pesquisa = ForeignKey(Pesquisa, on_delete=PROTECT, related_name="versoes")`;
    - `designacao` texto obrigatório;
    - `estado` texto com `choices=EstadoVersao.choices`, `default=RASCUNHO`;
    - `publicada_em` `DateTimeField(null=True)`;
    - `origem = ForeignKey("self", on_delete=PROTECT, null=True,
      related_name="derivadas")`;
    - `titulo`, `texto_abertura`, `texto_encerramento` texto `null=True`;
    - `UniqueConstraint(fields=["pesquisa", "designacao"])`;
    - CHECK `estado IN ('RASCUNHO', 'PUBLICADA')`;
    - CHECK "`(estado = 'PUBLICADA') = (publicada_em IS NOT NULL)`", escrito como
      `Q(estado="PUBLICADA", publicada_em__isnull=False) | Q(estado="RASCUNHO",
      publicada_em__isnull=True)`;
    - CHECK não vazio em `designacao`, `titulo`, `texto_abertura`, `texto_encerramento`;
    - CHECK `origem <> id` (`~Q(origem=F("id"))`);
    - `Meta.ordering = ["designacao"]` (só determinismo; FR-008).
  - **`Secao`**:
    - `id` UUID; `versao = ForeignKey(Versao, on_delete=PROTECT, related_name="secoes")`;
    - `posicao` `PositiveIntegerField()`;
    - `titulo`, `texto` texto `null=True`;
    - `encaminhamento = ForeignKey("self", on_delete=PROTECT, null=True,
      related_name="encaminhadas")`;
    - `UniqueConstraint(fields=["versao", "posicao"],
      deferrable=models.Deferrable.DEFERRED)`;
    - CHECK `posicao > 0`; CHECK não vazio em `titulo` e `texto`;
    - `Meta.ordering = ["posicao"]`.
  - **`Pergunta`**:
    - `id` UUID; `secao = ForeignKey(Secao, on_delete=PROTECT, related_name="perguntas")`;
    - `posicao` `PositiveIntegerField()`;
    - `tipo` texto com `choices=TipoPergunta.choices` (sem default);
    - `texto` texto obrigatório; `texto_explicativo` texto `null=True`;
    - `obrigatoria` `BooleanField()` sem default;
    - `escala_inicio`, `escala_fim` `IntegerField(null=True)`;
    - `escala_rotulo_inicio`, `escala_rotulo_fim` texto `null=True`;
    - `UniqueConstraint(fields=["secao", "posicao"], deferrable=DEFERRED)`;
    - CHECK `posicao > 0`;
    - CHECK `tipo IN (…quatro valores…)`;
    - CHECK de escala: `tipo = 'ESCALA'` ⇒ `escala_inicio` e `escala_fim` não nulos e
      `escala_inicio < escala_fim`; `tipo <> 'ESCALA'` ⇒ as quatro colunas de escala
      nulas. Escrever os `IS NOT NULL` explicitamente (comparação com `NULL` dá
      `UNKNOWN`, que o CHECK aceita — mesmo cuidado da 001);
    - CHECK não vazio em `texto`, `texto_explicativo`, `escala_rotulo_inicio`,
      `escala_rotulo_fim`;
    - `Meta.ordering = ["posicao"]`.
  - **`Opcao`**:
    - `id` UUID; `pergunta = ForeignKey(Pergunta, on_delete=CASCADE,
      related_name="opcoes")`;
    - `posicao` `PositiveIntegerField()`;
    - `texto` texto obrigatório;
    - `complemento_textual` `BooleanField(default=False)`;
    - `regra_destino = ForeignKey(Secao, on_delete=PROTECT, null=True,
      related_name="regras_que_apontam")`;
    - `regra_finaliza` `BooleanField(default=False)`;
    - `UniqueConstraint(fields=["pergunta", "posicao"], deferrable=DEFERRED)`;
    - `UniqueConstraint(fields=["pergunta", "texto"])`;
    - `UniqueConstraint(fields=["pergunta"], condition=Q(complemento_textual=True))`;
    - CHECK `NOT (regra_destino IS NOT NULL AND regra_finaliza)`;
    - CHECK `posicao > 0`; CHECK não vazio em `texto`;
    - `Meta.ordering = ["posicao"]`.
  - Nomes de restrição com prefixo da tabela (por exemplo `versao_designacao_unica`,
    `pergunta_escala_coerente`), para que os testes os reconheçam nas mensagens.
  - Nenhum campo de data de criação ou alteração; nenhum campo além dos listados.
- [X] T004 [P] Implementar `trajetoria/instrumento/regras.py`:
  - `class Motivo(Enum)` com **exatamente** os 22 valores da tabela "Motivos" de
    [contracts/operacoes.md](contracts/operacoes.md#motivos-motivo):
    `VERSAO_PUBLICADA`, `REFERENCIA_OUTRA_VERSAO`, `OPCAO_EM_TIPO_SEM_OPCOES`,
    `ESCALA_EM_TIPO_NAO_ESCALA`, `ESCALA_INVALIDA`, `REGRA_EM_TIPO_INCOMPATIVEL`,
    `OPCAO_DE_OUTRA_PERGUNTA`, `REGRA_JA_DEFINIDA`, `POSICAO_OCUPADA`,
    `ORDEM_INCOMPLETA`, `POSICAO_INVALIDA`, `TIPO_NAO_SUPORTADO`, `TEXTO_VAZIO`,
    `DESIGNACAO_REPETIDA`, `OPCAO_REPETIDA`, `COMPLEMENTO_REPETIDO`,
    `SECAO_COM_PERGUNTAS`, `SECAO_REFERENCIADA`,
    `SEM_SECOES`, `SECAO_SEM_PERGUNTAS`, `OPCOES_INSUFICIENTES`,
    `DESTINO_NAO_POSTERIOR`. Comentário em cada um com o requisito (FR-0xx);
  - `@dataclass(frozen=True) class Violacao: motivo: Motivo; elemento: UUID | None;
    detalhe: str`;
  - `class OperacaoRejeitada(Exception)` com atributo `violacoes: tuple[Violacao, ...]`
    (construtor exige ao menos uma) e `__str__` listando motivo e elemento;
  - `verificar_completude(versao) -> tuple[Violacao, ...]` fica para T022 (US5); não
    criar agora.
  - Sem importar `operacoes.py` (R8: consumidores importam `Motivo` sem as operações).
- [X] T005 Gerar `trajetoria/instrumento/migrations/0001_initial.py` com
  `uv run python manage.py makemigrations instrumento` (depende de T002 e T003).
  Conferir que contém as UNIQUE adiadas e a UNIQUE parcial. Verificar com
  `uv run python manage.py makemigrations --check --dry-run`.
- [X] T006 [P] Implementar `trajetoria/instrumento/conteudo.py` conforme
  [contracts/conteudo.md](contracts/conteudo.md) (depende de T003):
  - `@dataclass(frozen=True)`: `Escala(inicio: int, fim: int, rotulo_inicio: str |
    None = None, rotulo_fim: str | None = None)`, `RegraNavegacao(destino_secao_id: UUID
    | None, finaliza: bool)`, `ConteudoOpcao`, `ConteudoPergunta`, `ConteudoSecao`,
    `ConteudoVersao`, com exatamente os campos do contrato (coleções como `tuple`);
  - `conteudo_da_versao(versao) -> ConteudoVersao`: lê com `prefetch_related` e monta a
    árvore na ordem das posições. `ConteudoOpcao.regra` é `None` quando a Opção não tem
    regra; senão `RegraNavegacao(regra_destino_id, regra_finaliza)`. `escala` é `None`
    fora de `ESCALA`. `estado` e `tipo` como os enums de `models.py`;
  - **nenhum** campo de momento de aplicação da regra (FR-053).
- [X] T007 Criar o esqueleto de `trajetoria/instrumento/operacoes.py` (depende de T003,
  T004 e T006). Docstring citando [contracts/operacoes.md](contracts/operacoes.md).
  Só auxiliares privados, ainda sem operações públicas:
  - `_MANTER = object()` (sentinela de "não informado" nos `alterar_*`);
  - `_bloquear(versao) -> Versao`: relê com `select_for_update()`;
  - `_exigir_rascunho(versao)`: `VERSAO_PUBLICADA` se publicada;
  - `_rejeitar(motivo, elemento=None, detalhe="")`: levanta `OperacaoRejeitada`;
  - `_texto_obrigatorio(valor, elemento)` e `_texto_opcional(valor, elemento)`:
    `TEXTO_VAZIO` se `valor.strip() == ""`; o valor é devolvido **sem** `strip()`;
  - `_posicao(valor, elemento)`: `POSICAO_INVALIDA` se não for `int` (excluindo `bool`)
    ou for menor que 1;
  - `_posicao_livre(queryset, posicao, elemento)`: `POSICAO_OCUPADA` se já usada;
  - `_reordenar(queryset_do_conjunto, elementos_em_ordem, elemento)`:
    `ORDEM_INCOMPLETA` se os ids dados não forem exatamente os do conjunto, sem
    repetição; senão grava `posicao = 1..n` (a unicidade adiada permite a troca).
  - `__all__` vazio por enquanto; cada história acrescenta suas operações.

**Checkpoint**: `manage.py check`, `migrate` e `makemigrations --check` sem erros; a
suíte da 001 continua passando (`uv run pytest`).

---

## Phase 3: User Story 1 — Criar Pesquisa e primeira Versão em rascunho (Priority: P1) 🎯 MVP

**Goal**: Pesquisa e Versão distintas, Versão em `RASCUNHO`, várias Versões por
Pesquisa, sem depender de Pessoa.

**Independent Test**: criar uma Pesquisa e duas Versões; verificar identidades
distintas, mesma Pesquisa, estado `RASCUNHO` e banco sem nenhuma Pessoa.

### Tests for User Story 1 ⚠️

- [X] T008 [P] [US1] Criar `tests/instrumento/test_instrumento_estrutura.py` com os
  cenários de US1 da spec:
  - `criar_pesquisa("Pesquisa Institucional de Egressos")` cria Pesquisa sem Versões;
  - `criar_versao(p, "2024")` → `estado == RASCUNHO`, `publicada_em is None`,
    `origem is None`, pertence a `p`; segunda Versão `"2026"` → duas Versões com ids
    distintos;
  - designação repetida na mesma Pesquisa → `DESIGNACAO_REPETIDA`; a mesma designação
    em **outra** Pesquisa é aceita;
  - `renomear_pesquisa` muda só o nome;
  - `alterar_versao` com `titulo`, `texto_abertura`, `texto_encerramento`; `None`
    remove um texto; textos ausentes aparecem como `None` em `conteudo_da_versao`;
  - `TEXTO_VAZIO` para nome `""` e `"   "`, designação vazia e texto opcional vazio;
  - texto com espaços nas bordas é gravado sem alteração (R16);
  - `Pessoa.objects.count() == 0` e `ConclusaoAcademica.objects.count() == 0` durante
    todo o teste (FR-065). Este é o único lugar onde os testes desta feature importam
    modelos da 001.
- [X] T009 [P] [US1] Criar `tests/instrumento/test_instrumento_modelo.py` com as
  restrições de Pesquisa e Versão (escrita direta no ORM, `IntegrityError` dentro de
  `transaction.atomic()`, como `tests/test_modelo.py`):
  - `''` em `Pesquisa.nome`, `Versao.designacao`, `titulo`, `texto_abertura`,
    `texto_encerramento`;
  - (`pesquisa`, `designacao`) repetido;
  - `estado="PUBLICADA"` com `publicada_em=None` e `estado="RASCUNHO"` com
    `publicada_em` preenchido;
  - `estado` fora dos dois valores;
  - `ProtectedError` ao excluir Pesquisa com Versão;
  - o conjunto de campos de `Pesquisa` é exatamente `{id, nome}` e o de `Versao`
    exatamente `{id, pesquisa, designacao, estado, publicada_em, origem, titulo,
    texto_abertura, texto_encerramento}` (FR-002, FR-008).

### Implementation for User Story 1

- [X] T010 [US1] Em `trajetoria/instrumento/operacoes.py`, implementar
  `criar_pesquisa(nome)`, `renomear_pesquisa(pesquisa, nome)`,
  `criar_versao(pesquisa, designacao)` e `alterar_versao(versao, *, designacao=_MANTER,
  titulo=_MANTER, texto_abertura=_MANTER, texto_encerramento=_MANTER)` conforme a tabela
  "Versão" do contrato. `DESIGNACAO_REPETIDA` é verificado antes de gravar (não depender
  só do `IntegrityError`). `renomear_pesquisa` não bloqueia nem toca Versões (FR-003).
  Exportar em `__all__`.

**Checkpoint**: T008 e T009 passam.

---

## Phase 4: User Story 2 — Seções e Perguntas ordenadas (Priority: P1)

**Goal**: Seções e Perguntas com posições explícitas, ordem independente da criação,
reordenação, movimentação e remoção em rascunho.

**Independent Test**: criar Seções e Perguntas em ordem embaralhada e verificar que
`conteudo_da_versao` segue as posições.

### Tests for User Story 2 ⚠️

- [X] T011 [US2] Acrescentar a `tests/instrumento/test_instrumento_estrutura.py`
  (depende de T008):
  - Seções criadas nas posições 3, 1, 2 são lidas na ordem 1, 2, 3; o mesmo para
    Perguntas (SC-005); leitura repetida igual (`==`);
  - Seção sem título → `titulo is None`;
  - `reordenar_secoes` e `reordenar_perguntas` com a lista completa renumeram 1..n;
    lista incompleta, com elemento de outro conjunto ou com repetição →
    `ORDEM_INCOMPLETA`;
  - `POSICAO_OCUPADA` e `POSICAO_INVALIDA` (0, -1, `True`, `1.5`) em `adicionar_secao`
    e `adicionar_pergunta`;
  - `mover_pergunta` para outra Seção da mesma Versão mantém o `id`; para Seção de
    outra Versão → `REFERENCIA_OUTRA_VERSAO`;
  - `remover_pergunta` remove; `remover_secao` com Pergunta → `SECAO_COM_PERGUNTAS`;
    Seção vazia é removida;
  - `alterar_pergunta` muda `texto`, `texto_explicativo` e `obrigatoria` mantendo o
    `id`.
- [X] T012 [US2] Acrescentar a `tests/instrumento/test_instrumento_modelo.py` (depende
  de T009): posição `0` rejeitada em Seção e Pergunta; posição repetida rejeitada **no
  fim** da transação (`IntegrityError` ao sair do `atomic`) e aceita quando trocada
  dentro da mesma transação; `ProtectedError` ao excluir Seção com Pergunta.

### Implementation for User Story 2

- [X] T013 [US2] Em `trajetoria/instrumento/operacoes.py`, implementar
  `adicionar_secao`, `alterar_secao`, `remover_secao`, `reordenar_secoes`,
  `adicionar_pergunta(secao, posicao, tipo, texto, *, obrigatoria,
  texto_explicativo=None, escala=None)`, `alterar_pergunta` (só `texto`,
  `texto_explicativo`, `obrigatoria` nesta história), `mover_pergunta`,
  `remover_pergunta` e `reordenar_perguntas`, conforme as tabelas "Seção" e
  "Pergunta" do contrato. Em `remover_secao`, verificar também `SECAO_REFERENCIADA`
  (Seção que é `encaminhamento` de outra ou `regra_destino` de alguma Opção). Nesta
  história, `adicionar_pergunta` valida o `tipo` contra `TipoPergunta`
  (`TIPO_NAO_SUPORTADO`) e grava a escala informada; as regras completas de escala
  entram em T017. `alterar_pergunta` **não** tem parâmetro `tipo` (FR-062).

**Checkpoint**: T011 e T012 passam.

---

## Phase 5: User Story 3 — Os quatro tipos de pergunta (Priority: P1)

**Goal**: exatamente quatro tipos, cada um aceitando só sua configuração.

**Independent Test**: uma pergunta de cada tipo; quinto tipo rejeitado; escala inválida
rejeitada; tipo não alterável.

### Tests for User Story 3 ⚠️

- [X] T014 [US3] Acrescentar a `tests/instrumento/test_instrumento_estrutura.py`
  (depende de T011):
  - uma pergunta de cada tipo; `tipo="DATA"`, `"MATRIZ"`, `"UPLOAD"` →
    `TIPO_NAO_SUPORTADO`;
  - `ESCALA` com `Escala(1, 5, "Discordo totalmente", "Concordo totalmente")` lida
    igual; sem `escala` → `ESCALA_INVALIDA`; `Escala(5, 1)`, `Escala(3, 3)`,
    `Escala(1.0, 5)` → `ESCALA_INVALIDA`; rótulo `""` → `TEXTO_VAZIO`;
  - `escala` em `TEXTO_CURTO` ou escolha → `ESCALA_EM_TIPO_NAO_ESCALA`;
  - `obrigatoria` e `texto_explicativo` preservados em todos os tipos;
  - tipo imutável (FR-062): `"tipo" not in inspect.signature(alterar_pergunta).parameters`,
    e `alterar_pergunta(p, tipo=…)` levanta `TypeError`;
  - `alterar_pergunta(p, escala=Escala(0, 10))` em `ESCALA` altera a escala;
    `escala=None` em `ESCALA` → `ESCALA_INVALIDA`; `escala` em outro tipo →
    `ESCALA_EM_TIPO_NAO_ESCALA`.
- [X] T015 [US3] Acrescentar a `tests/instrumento/test_instrumento_modelo.py` (depende
  de T012): `tipo` fora dos quatro; `ESCALA` com `escala_inicio` ou `escala_fim` nulo;
  `escala_inicio >= escala_fim`; colunas de escala preenchidas em outro tipo; rótulo
  `''` — todos `IntegrityError`.

### Implementation for User Story 3

- [X] T016 [US3] Confirmar que `TipoPergunta` em `trajetoria/instrumento/models.py`
  tem exatamente quatro membros (nenhum código novo esperado).
- [X] T017 [US3] Em `trajetoria/instrumento/operacoes.py`, completar a validação de
  escala em `adicionar_pergunta` e acrescentar `escala=_MANTER` a `alterar_pergunta`
  (sem parâmetro `tipo`):
  - `escala` obrigatória se e somente se o tipo é `ESCALA`; limites `int` (não `bool`),
    início < fim (`ESCALA_INVALIDA`); rótulos via `_texto_opcional`;
  - `ESCALA_EM_TIPO_NAO_ESCALA` quando `escala` vem para outro tipo.

**Checkpoint**: T014 e T015 passam.

---

## Phase 6: User Story 4 — Opções e escalas com ordem e significado (Priority: P1)

**Goal**: Opções ordenadas com identidade independente do texto, complemento textual,
listas independentes entre perguntas.

**Independent Test**: Opções criadas em ordem embaralhada, uma com complemento; texto
alterado mantém o `id`; Q8/Q9 fictícias independentes.

### Tests for User Story 4 ⚠️

- [X] T018 [US4] Acrescentar a `tests/instrumento/test_instrumento_estrutura.py`
  (depende de T014):
  - Opções nas posições 2, 1 lidas como 1, 2, cada uma com `id` próprio;
  - `alterar_opcao(texto=…)` mantém `id`;
  - `complemento_textual=True` preservado em escolha única e múltipla; segunda →
    `COMPLEMENTO_REPETIDO`;
  - Opção em `TEXTO_CURTO` e em `ESCALA` → `OPCAO_EM_TIPO_SEM_OPCOES`;
  - texto repetido na mesma Pergunta → `OPCAO_REPETIDA`; o mesmo texto em outra
    Pergunta é aceito, e alterar uma não afeta a outra (Lista E de Q8/Q9);
  - textos preservados exatamente, inclusive "Corcordo totalmente" num rótulo de escala;
  - `reordenar_opcoes` completa e incompleta; `remover_opcao`; `remover_pergunta`
    remove as Opções (`Opcao.objects.filter(pergunta_id=…)` vazio);
  - 80 Opções numa pergunta são aceitas (FR-044).
- [X] T019 [US4] Acrescentar a `tests/instrumento/test_instrumento_modelo.py` (depende
  de T015): (`pergunta`, `texto`) repetido; duas Opções com `complemento_textual=True`
  na mesma Pergunta; `regra_destino` preenchido junto com `regra_finaliza=True`;
  `texto=''` — todos `IntegrityError`.

### Implementation for User Story 4

- [X] T020 [US4] Em `trajetoria/instrumento/operacoes.py`, implementar
  `adicionar_opcao(pergunta, posicao, texto, *, complemento_textual=False)`,
  `alterar_opcao(opcao, *, texto=_MANTER, complemento_textual=_MANTER)`,
  `remover_opcao` e `reordenar_opcoes`, conforme a tabela "Opção" do contrato.
  `OPCAO_REPETIDA` e `COMPLEMENTO_REPETIDO` verificados antes de gravar.

**Checkpoint**: T018 e T019 passam.

---

## Phase 7: User Story 5 — Publicar e impedir alterações (Priority: P1)

**Goal**: publicação com completude, `JA_PUBLICADA`, imutabilidade total nas operações
e no banco.

**Independent Test**: publicar uma Versão completa; tentar cada alteração; conteúdo
igual (`==`) ao lido na publicação.

### Tests for User Story 5 ⚠️

- [X] T021 [P] [US5] Criar `tests/instrumento/test_instrumento_publicacao.py`:
  - Versão completa → `publicar` devolve `SituacaoPublicacao.PUBLICADA`, `estado ==
    PUBLICADA`, `publicada_em` preenchido;
  - segunda chamada → `JA_PUBLICADA`, `publicada_em` inalterado;
  - Versão incompleta com **várias** pendências ao mesmo tempo (sem Seções; ou Seção
    vazia + pergunta de escolha com 1 Opção + encaminhamento para Seção anterior) →
    `OperacaoRejeitada` com **todas** as violações (`SEM_SECOES`;
    `SECAO_SEM_PERGUNTAS`, `OPCOES_INSUFICIENTES`, `DESTINO_NAO_POSTERIOR`), cada uma
    com o `elemento`; Versão continua `RASCUNHO` e com conteúdo igual;
  - `DESTINO_NAO_POSTERIOR` também para regra que aponta para a própria Seção da
    pergunta (usa `definir_regra`; skip até T029, retirado em T033);
  - **SC-002**, um teste por grupo; em cada tentativa, `antes =
    conteudo_da_versao(v)` lido após publicar, a operação levanta `VERSAO_PUBLICADA` e
    `conteudo_da_versao(v) == antes` ao final:
    - **editar a Versão publicada**: `alterar_versao` com cada um dos 4 campos;
    - **voltar a rascunho**: nenhuma função pública de `operacoes` tem parâmetro
      `estado` (varredura com `inspect.signature`); `publicar` de novo devolve
      `JA_PUBLICADA` e `estado`/`publicada_em` não mudam;
    - **Seção**: `adicionar_secao`, `alterar_secao`, `remover_secao`,
      `reordenar_secoes`, `definir_encaminhamento`;
    - **Pergunta**: `adicionar_pergunta`, `alterar_pergunta` (texto,
      texto_explicativo, obrigatoria, escala), `mover_pergunta`, `remover_pergunta`,
      `reordenar_perguntas`;
    - **Opção**: `adicionar_opcao`, `alterar_opcao` (texto, complemento),
      `remover_opcao`, `reordenar_opcoes`, `definir_regra`, `remover_regra`;
    - as operações de US7/US8 ficam em skip até T033;
    - a criação de nova Versão sem modificar a anterior é coberta em T024 (US6);
  - correção de grafia ("Corcordo" → "Concordo") também é rejeitada (FR-017);
  - `renomear_pesquisa` com Versão publicada é aceito e o conteúdo da Versão não muda
    (FR-003).

### Implementation for User Story 5

- [X] T022 [US5] Em `trajetoria/instrumento/regras.py`, implementar
  `verificar_completude(versao) -> tuple[Violacao, ...]` (FR-059), devolvendo **todas**
  as violações em ordem determinística (Seções por posição, Perguntas por posição):
  - `SEM_SECOES` (elemento = Versão);
  - `SECAO_SEM_PERGUNTAS` por Seção;
  - `OPCOES_INSUFICIENTES` por pergunta de escolha com menos de duas Opções;
  - `DESTINO_NAO_POSTERIOR` por encaminhamento e por Opção com `regra_destino` cuja
    Seção de destino tenha `posicao <=` a da Seção de origem (R15). Sem análise de grafo.
  Recebe o modelo `Versao` e lê pelo ORM; não importa `operacoes.py`.
- [X] T023 [US5] Em `trajetoria/instrumento/operacoes.py`, implementar
  `class SituacaoPublicacao(Enum)` (`PUBLICADA`, `JA_PUBLICADA`) e `publicar(versao)`
  exatamente pelos passos do contrato (bloquear; já publicada → `JA_PUBLICADA` sem
  gravar; completude; gravar `estado` e `publicada_em = timezone.now()`). `publicar` é a
  **única** função que escreve `estado`. Revisar todas as operações já existentes para
  garantir que chamam `_exigir_rascunho` depois de `_bloquear`. Nenhum gatilho, hook de
  modelo ou sinal (ADR 0002 rejeitado).

**Checkpoint**: T021 (exceto os skips) passa.

---

## Phase 8: User Story 6 — Nova Versão a partir de existente (Priority: P2)

**Goal**: cópia profunda sem compartilhamento, referências traduzidas, origem intocada
e registrada.

**Independent Test**: copiar uma Versão publicada, alterar a cópia, comparar a origem
(`==`) e conferir que nenhum `id` se repete.

### Tests for User Story 6 ⚠️

- [X] T024 [P] [US6] Criar `tests/instrumento/test_instrumento_nova_versao.py`:
  - origem publicada com textos da Versão, duas Seções, um de cada tipo de pergunta,
    escala com rótulos, Opção com complemento, encaminhamento e regras (as partes de
    regra/encaminhamento em skip até T033);
  - `criar_versao_a_partir_de(origem, "2026")` → mesma Pesquisa, `RASCUNHO`,
    `origem_id == origem.id`, `publicada_em is None`;
  - o conjunto de todos os `id` da árvore nova é disjunto do da origem (SC-003);
  - a árvore nova é igual à da origem **ignorando** `id`s, `estado`, `publicada_em`,
    `origem_id` e `designacao` (comparar por um auxiliar que remove esses campos);
  - todo `encaminhamento_id` e `destino_secao_id` da nova aponta para Seção da nova;
  - alterar texto de pergunta, Opção, escala e regra na nova mantém
    `conteudo_da_versao(origem) == antes`;
  - copiar a partir de origem em rascunho e depois alterar a origem não altera a cópia;
  - designação repetida → `DESIGNACAO_REPETIDA`, sem nenhuma linha criada.

### Implementation for User Story 6

- [X] T025 [US6] Em `trajetoria/instrumento/operacoes.py`, implementar
  `criar_versao_a_partir_de(origem, designacao)` pelos quatro passos de R11 (Versão;
  Seções sem encaminhamento; Perguntas e Opções sem regra; encaminhamentos e regras
  traduzidos por `dict[UUID, Secao]`). Bloquear a origem com `select_for_update()` só
  para leitura consistente; a origem nunca é escrita. Não registrar correspondência
  entre elementos (DP-006).

**Checkpoint**: T024 (exceto os skips) passa.

---

## Phase 9: User Story 7 — Navegação condicional entre Seções (Priority: P2)

**Goal**: regra "se X = Y, ir para Z" associada à Pergunta e à Opção; encaminhamento de
Seção; percursos de Seções deduzíveis; **sem** momento de aplicação.

**Independent Test**: padrões de Q14 (quatro ramos convergentes) e Q33 (ramo que salta
o outro) com textos fictícios; percursos de Seções enumerados iguais aos esperados.

### Tests for User Story 7 ⚠️

- [X] T026 [P] [US7] Criar `tests/instrumento/construcao.py` (auxiliar, não é teste):
  - `percursos_de_secoes(conteudo: ConteudoVersao) -> set[tuple[str, ...]]`: enumera
    os percursos de Seções segundo
    [contracts/conteudo.md](contracts/conteudo.md#percurso-de-seções). Cada percurso é
    uma tupla de rótulos (`titulo` da Seção, ou `"#<posicao>"`) terminada em `"FIM"`.
    Para cada Seção: se houver pergunta `ESCOLHA_UNICA` com Opções com regra, ramifica
    por Opção (Opção sem regra e "sem resposta" seguem a Seção seguinte padrão); senão
    segue a Seção seguinte padrão. Levanta `ValueError` se uma Seção tiver mais de uma
    pergunta com regras (R14: prevalência depende do momento de aplicação, fora do
    escopo) ou se um destino não for posterior (proteção contra ciclo);
  - `sem_identidades(conteudo)`: devolve a árvore com `id`s, `estado`, `publicada_em`,
    `origem_id` e `designacao` neutralizados (usado por T024).
- [X] T027 [US7] Criar `tests/instrumento/test_instrumento_navegacao.py` (depende de
  T026):
  - `definir_regra(x, y, z)` → `ConteudoOpcao.regra == RegraNavegacao(z.id, False)`;
    `remover_regra` → `None`;
  - **fluxo padrão**: três Seções sem regras → `{("A", "B", "C", "FIM")}`;
  - **padrão Q14**: Seção "Nível" com P (A/B/C/D) → Seções "A".."D", cada uma com
    `definir_encaminhamento` para "Comum" → quatro percursos convergindo em "Comum";
  - **padrão Q33**: P (Sim/Não), Sim → "Trabalha" (com encaminhamento para "Estudo"),
    Não → "Não trabalha" → dois percursos, um sem "Não trabalha";
  - **padrão Q51**: regra com destino igual ao fluxo padrão é aceita e o percurso não
    muda;
  - **pergunta opcional sem resposta**: percurso pela Seção seguinte padrão incluído;
  - **pergunta com regras no meio da Seção** (padrão Q46 seguida de duas perguntas):
    representável; `ConteudoOpcao.regra` tem apenas `destino_secao_id` e `finaliza`
    (verificar `dataclasses.fields(RegraNavegacao)` == esses dois) e nenhum modelo tem
    campo de momento de aplicação (verificar `Opcao._meta`/`Secao._meta`/
    `Pergunta._meta` sem campos além do data-model) (FR-053);
  - destino na própria Seção ou anterior é aceito em rascunho;
  - `definir_encaminhamento(s, None)` remove o encaminhamento.

### Implementation for User Story 7

- [X] T028 [US7] Em `trajetoria/instrumento/operacoes.py`, implementar
  `definir_encaminhamento(secao, destino)` (destino `Secao | None`;
  `REFERENCIA_OUTRA_VERSAO` se de outra Versão).
- [X] T029 [US7] Em `trajetoria/instrumento/operacoes.py`, implementar
  `definir_regra(pergunta, opcao, destino)` para destino `Secao`, e
  `remover_regra(pergunta, opcao)`, na ordem de verificação do contrato:
  `VERSAO_PUBLICADA`, `REGRA_EM_TIPO_INCOMPATIVEL`, `OPCAO_DE_OUTRA_PERGUNTA`,
  `REFERENCIA_OUTRA_VERSAO`, `REGRA_JA_DEFINIDA`. Nenhum parâmetro de momento de
  aplicação.

**Checkpoint**: T027 passa.

---

## Phase 10: User Story 8 — Finalização condicional (Priority: P2)

**Goal**: "se X = Y, finalizar"; última Seção finaliza pelo fluxo padrão; nenhuma Seção
de fim.

**Independent Test**: padrão Q1 (Sim/Não, Não → finalizar) e percursos terminando em
`"FIM"` sem Seção extra.

### Tests for User Story 8 ⚠️

- [X] T030 [US8] Acrescentar a `tests/instrumento/test_instrumento_navegacao.py`
  (depende de T027):
  - `definir_regra(q1, nao, FINALIZAR)` → `RegraNavegacao(None, True)`;
  - percursos: `("Termos", "FIM")` e `("Termos", …, "FIM")` para "Sim";
  - a última Seção sem encaminhamento termina em `"FIM"` sem regra;
  - nenhuma Seção sem perguntas é necessária: a Versão com texto de encerramento e
    regra de finalização é publicável;
  - `definir_regra` com `FINALIZAR` em Opção que já tem destino → `REGRA_JA_DEFINIDA`.

### Implementation for User Story 8

- [X] T031 [US8] Em `trajetoria/instrumento/operacoes.py`, implementar
  `class Finalizar` e a sentinela única `FINALIZAR = Finalizar()`, e aceitar
  `destino=FINALIZAR` em `definir_regra` (grava `regra_finaliza=True`,
  `regra_destino=None`). Exportar `FINALIZAR` em `__all__`.

**Checkpoint**: T030 passa.

---

## Phase 11: User Story 9 — Rejeição explícita de estruturas inválidas (Priority: P3)

**Goal**: cada `Motivo` provocado ao menos uma vez, com elemento identificado e estado
idêntico após a rejeição.

**Independent Test**: suíte parametrizada por `Motivo`.

### Tests for User Story 9 ⚠️

- [X] T032 [P] [US9] Criar `tests/instrumento/test_instrumento_rejeicoes.py`:
  - um caso por membro de `Motivo` (22), parametrizado com `pytest.param(…,
    id=motivo.name)`; um teste extra garante que o conjunto de casos cobre
    **exatamente** `set(Motivo)`;
  - cada caso: monta o estado, guarda `antes` (`conteudo_da_versao` de todas as Versões
    envolvidas e contagens de `Pesquisa`, `Versao`, `Secao`, `Pergunta`, `Opcao`),
    executa a operação, verifica `OperacaoRejeitada` com o `motivo` esperado e o
    `elemento` esperado, e confirma estado igual a `antes` (SC-004);
  - inclui os casos da lista "Estruturas inválidas" da descrição: pergunta de escolha
    sem Opções (publicação), Opção em tipo incompatível, escala inválida, regra em
    pergunta incompatível, regra para Seção de outra Versão, regra com Opção de outra
    Pergunta, posição duplicada, alteração em Versão publicada.

### Implementation for User Story 9

- [X] T033 [US9] Retirar todos os `pytest.mark.skip` deixados em T021 e T024 e
  corrigir em `trajetoria/instrumento/operacoes.py` ou `regras.py` qualquer falha de
  T032 (nenhum código novo esperado).

**Checkpoint**: `uv run pytest tests/instrumento` sem skips e sem falhas.

---

## Phase 12: Polish & Cross-Cutting Concerns

- [X] T034 Acrescentar a `tests/instrumento/construcao.py`
  `versao_de_demonstracao() -> Versao`, construída **só** pelas operações públicas, com
  textos fictícios e reduzidos (não o Formulário 2024), cobrindo toda linha de
  "intenção" da tabela "Cobertura estrutural" da spec: título, abertura e encerramento
  da Versão; Seção de termos com texto e regra "Não → FINALIZAR"; ramificação em
  quatro ramos com encaminhamento para Seção comum; ramo que salta o outro; uma
  pergunta de cada tipo; escala 1–5 com rótulos; Opção com complemento textual em
  escolha única e em múltipla; texto explicativo; pergunta opcional; listas iguais em
  duas perguntas; Seção sem título.
- [X] T035 Criar `tests/instrumento/test_instrumento_aceitacao.py` (depende de T034):
  - **SC-001**: `versao_de_demonstracao()` é publicável e `percursos_de_secoes` devolve
    exatamente o conjunto esperado (escrito à mão no teste);
  - **SC-006**: nenhum arquivo em `trajetoria/instrumento/` importa `trajetoria.academico`
    ou `trajetoria.fonte_academica` (varredura com `ast`); nenhum campo de modelo do app
    é FK para modelo de outro app;
  - **SC-007**: `len(TipoPergunta) == 4`, `len(EstadoVersao) == 2`;
    `apps.get_app_config("instrumento").get_models()` tem exatamente os cinco modelos;
    nenhum modelo registrado se chama `Campanha`, `Participacao` ou `Resposta`.
- [X] T036 Executar a validação completa do [quickstart](quickstart.md):
  `uv run ruff check .`, `uv run python manage.py check`,
  `uv run python manage.py makemigrations --check --dry-run`,
  `uv run python manage.py migrate` e `uv run pytest` (inclui a suíte da 001, que deve
  passar sem alteração — SC-006). Fazer a demonstração no shell descrita no quickstart.
- [X] T037 [P] Em `README.md`, acrescentar uma linha com o link para o
  [quickstart da Feature 002](quickstart.md), ao lado do da 001.
- [X] T038 Revisão final contra a Constituição e a spec, registrando o resultado em
  `specs/002-pesquisa-versao-instrumento/plan.md` (nota curta ao fim do Constitution
  Check):
  - Definition of Done: testes adequados ao risco, nenhuma interface exposta, nenhum
    dado pessoal, nenhum log novo;
  - DP-001 a DP-007 continuam abertas; nenhuma tarefa as resolveu;
  - nenhum item de "Limites desta lista" foi criado, em especial momento de aplicação da
    regra (FR-053);
  - git diff sem alterações em `trajetoria/academico/`, `trajetoria/fonte_academica/` e
    `tests/test_*.py` da 001 (FR-067);
  - ADR 0002 com status "Rejeitado nesta fase"; nenhum gatilho, `RunSQL`, hook de
    modelo ou sinal criado; uma única migração (`0001_initial.py`).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: T001, depois T002.
- **Foundational (Fase 2)**: depende da Fase 1 e bloqueia as histórias. T003 ∥ T004;
  T005 depois de T003; T006 depois de T003;
  T007 depois de T003, T004 e T006.
- **Histórias (Fases 3–11)**: dependem da Fase 2. Seguem a ordem de prioridade porque
  compartilham `operacoes.py` e três arquivos de teste.
- **Polish (Fase 12)**: depende de todas as histórias.

### User Story Dependencies

- **US1**: primeira; entrega Pesquisa e Versão.
- **US2**: depende de US1 (precisa de Versão).
- **US3**: depende de US2 (precisa de Seção e `adicionar_pergunta`).
- **US4**: depende de US3 (tipos definem onde há Opções).
- **US5**: depende de US1–US4 para a completude; os casos de regra e encaminhamento
  ficam em skip até US7/US8.
- **US6**: depende de US5 (copia Versão publicada); idem quanto a regras.
- **US7**: depende de US2 e US4 (Seções e Opções); independente de US5 e US6 em
  código, mas segue a ordem por compartilhar arquivos.
- **US8**: depende de US7 (`definir_regra`).
- **US9**: depende de todas (cobre todos os motivos) e retira os skips.

### Within Each User Story

- Testes antes da implementação; DEVEM falhar primeiro.
- Uma tarefa por arquivo compartilhado de cada vez.

### Parallel Opportunities

Só onde os arquivos são realmente independentes:

- **Fase 2**: T003 ∥ T004; depois T005 ∥ T006.
- **US1**: T008 ∥ T009.
- **US5**: T021 (arquivo novo) ∥ T022 (`regras.py`).
- **US6 com US7**: T024 (arquivo novo) ∥ T026 (`construcao.py`).
- **US9**: T032 (arquivo novo) pode ser escrito em paralelo com US7/US8, rodando ao fim.
- **Polish**: T037 ∥ T035.

---

## Parallel Example: Foundational e US1

```bash
# Fase 2 — arquivos independentes:
Task: "T003 modelos em trajetoria/instrumento/models.py"
Task: "T004 Motivo, Violacao, OperacaoRejeitada em trajetoria/instrumento/regras.py"

# US1 — testes em arquivos distintos:
Task: "T008 cenários de US1 em tests/instrumento/test_instrumento_estrutura.py"
Task: "T009 restrições de Pesquisa e Versão em tests/instrumento/test_instrumento_modelo.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Fases 1 e 2.
2. Fase 3 (US1): Pesquisa com Versões em rascunho.
3. **PARAR e VALIDAR** com `uv run pytest`.

### Incremental Delivery

1. Fases 1 e 2: fundação (modelos, migrações, leitura, rejeições).
2. US1–US5 (P1): estrutura completa e publicação imutável — já suficiente para a
   Feature 003 representar o instrumento sem ramificações.
3. US6–US8 (P2): evolução por nova Versão, navegação e finalização.
4. US9 (P3): cobertura total das rejeições.
5. Polish, revisão constitucional e PR.

---

## Decisões Pendentes preservadas

DP-001 a DP-007 permanecem **abertas**. Nenhuma tarefa as resolve. As soluções
provisórias são as do [plan](plan.md#decisões-pendentes). Em particular:

- `publicar` não é exposta por nenhum ponto de entrada (DP-001);
- a imutabilidade total é regra operacional provisória (DP-003);
- o momento de aplicação das regras não é modelado (FR-053; Feature 003 e jornada).

## Notes

- Total: **38 tarefas**. Código de produção em cinco módulos (`models.py`, `regras.py`,
  `operacoes.py`, `conteudo.py`, `apps.py`), uma migração e uma linha em
  `config/settings.py`. Tarefas de teste: T008, T009, T011, T012, T014, T015, T018,
  T019, T021, T024, T026, T027, T030, T032, T034, T035.
- Tarefas "nenhum código novo esperado" (T016, T033) deixam explícito onde corrigir.
- Fazer commit ao fim de cada fase.
