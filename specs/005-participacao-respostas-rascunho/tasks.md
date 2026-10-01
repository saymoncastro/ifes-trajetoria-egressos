---

description: "Tasks da Feature 005 — Participação em Campanha e respostas em rascunho"
---

# Tasks: Participação em Campanha e respostas em rascunho

**Input**: Design documents from `specs/005-participacao-respostas-rascunho/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Stack (confirmada; [ADR 0001](../../docs/adr/0001-stack-inicial.md))**: Python 3.13,
Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff. Nenhuma dependência
nova. Regras entre tabelas são garantidas **só pelas operações** e por testes: nenhum
gatilho, função PostgreSQL, `RunSQL`, `save()` ou `delete()` sobrescrito, sinal, serviço
ou repositório.

**Tests**: obrigatórios e escritos antes da implementação (test-first). Todas as
histórias tocam invariantes constitucionais (longitudinalidade, preservação histórica,
declarado ≠ institucional). Os testes DEVEM falhar primeiro quando a história traz
comportamento novo. Quando a história só verifica comportamento já entregue (US10, US11,
US12), os testes podem passar de imediato; se falharem, a correção vai no arquivo
indicado.

**Organization**: tarefas agrupadas pelas histórias da spec (US1–US12). `operacoes.py`,
`consultas.py` e os arquivos de teste compartilhados entre histórias são editados em
sequência.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US12).

## Convenções para todas as tarefas

- **Modelos**: dois de domínio, `Participacao` e `Resposta`, e um técnico,
  `RespostaOpcao`, em `trajetoria/participacao/models.py`. `RespostaOpcao` não tem
  operação, consulta, posição, timestamp nem significado próprios.
- **Nada muda** em `trajetoria/academico/`, `trajetoria/fonte_academica/`,
  `trajetoria/instrumento/`, `trajetoria/formulario_2024/`, `trajetoria/campanha/` nem
  nos testes das Features 001–004 (a correção de escopo do teste da 004 já está na
  `main` — T002). Fora do app novo, só mudam `INSTALLED_APPS` e o link no README. Se surgir
  necessidade real de mudar 001–004, **parar** e demonstrar o bloqueio antes.
- **FKs para modelos anteriores**: sempre `on_delete=PROTECT` e `related_name="+"`
  (research R2). Nenhum acessor reverso em `Campanha`, `ConclusaoAcademica`, `Pergunta`
  ou `Opcao`.
- **CHECKs**: só invariantes verificáveis com as colunas da própria linha. Tipo da
  Pergunta, pertença da Opção, Versão da Campanha, limites da escala, ≥ 1 seleção e
  "complemento só em escolha e com a Opção que o admite" ficam **nas operações**. Não
  copiar o tipo da Pergunta para `Resposta`.
- **Esqueleto das escritas de resposta** ([contrato](contracts/operacoes.md#esqueleto-comum-das-escritas-de-resposta)):
  1. `TypeError` para `participacao` que não é `Participacao`, `pergunta` que não é
     `Pergunta`, `agora` que não é `datetime` com timezone;
  2. `transaction.atomic()`; `Participacao.objects.select_for_update(of=("self",))
     .select_related("campanha").filter(pk=…).first()`, senão
     `PARTICIPACAO_INEXISTENTE`;
  3. `estado(campanha, agora=agora) is EstadoCampanha.EM_COLETA`, senão
     `COLETA_NAO_ADMITIDA` — **sem reavaliar elegibilidade**;
  4. Pergunta relida do banco com `secao__versao_id`; se diferente de
     `campanha.versao_id`, `PERGUNTA_DE_OUTRA_VERSAO`;
  5. `pergunta.tipo` diferente do tipo da operação → `VALOR_INCOMPATIVEL`;
  6. validação do valor (por tipo), com Opções relidas por
     `Opcao.objects.filter(pk__in=…, pergunta=pergunta)`;
  7. grava o valor inteiro: atualiza no lugar a Resposta de `(participacao, pergunta)`
     (mesmo `id`) ou a cria; colunas das outras formas e complemento ausente ficam
     `NULL`; em escolha múltipla, apaga as `RespostaOpcao` da Resposta e insere as novas.
- **Rejeição**: sempre `ParticipacaoRejeitada` com `Violacao(motivo, campo, detalhe)`. O
  `detalhe` cita motivo, campo e UUIDs técnicos, **nunca** texto, inteiro ou complemento
  declarados, nem atributos da Conclusão. Nenhum log.
- **Tempo**: `iniciar_participacao`, as escritas e `admite_escrita` recebem
  `agora: datetime | None = None` e usam `momento_de_referencia` e `estado` de
  `trajetoria.campanha.consultas`. Nenhum relógio novo. **Todo teste passa `agora`
  explícito** pelo auxiliar `momento(...)`.
- **Gates da 004**: criar Participação usa a admissão da 004 por `estado` e `avaliar`,
  avaliada uma vez e equivalente a `admite_participacao` (teste de equivalência). Nenhuma regra de estado, período ou critério reescrita.
- **Instrumentos nos testes**: montados e publicados pelas operações da 002. A baseline
  da 003 (`materializar()`) **nunca** é publicada nem alterada.
- **Ausência × vazio (regra uniforme)**: em toda operação `responder_*`, `None`, `""`,
  `"   "` e coleção vazia como valor são `VALOR_VAZIO`, verificado **antes** da forma do
  valor ([contrato](contracts/operacoes.md#motivos-motivo)). Nenhuma Resposta vazia é
  gravada e nenhum valor ausente vira remoção implícita: "não respondida" = "não existe
  Resposta", e só `remover_resposta` volta a esse estado. `complemento=None` significa
  "sem complemento".
- **Dados**: somente fictícios (DP-504).
- **Testes de banco**: `pytestmark = pytest.mark.django_db`; diretório
  `tests/participacao/` **sem** `__init__.py` (como `tests/campanha/`); auxiliares
  importados como `from tests.participacao.construcao import …`.

## Limites desta lista (não criar)

- Submissão, Tentativa, Sessão, Rascunho (entidade), VersaoResposta, HistoricoResposta,
  ValorResposta, TipoResposta, Progresso, FotografiaPergunta, VersaoParticipacao,
  Convite, Token, Consentimento, Evento.
- Colunas `estado`, `concluida_em`, `atualizada_em`, `respondida_em`, `pessoa`,
  `versao`, `pesquisa`, `tipo` em `Participacao` ou `Resposta`; posição ou timestamp em
  `RespostaOpcao`.
- `JSONField`, tabela por tipo, herança ou polimorfismo de Resposta.
- Conclusão, submissão, obrigatoriedade, próxima Pergunta, progresso, navegação,
  finalização por Q1, congelamento pós-conclusão.
- Remoção de Participação; prazo de graça; pré-preenchimento a partir da Conclusão.
- Framework de validação ou de locking, `SERIALIZABLE`, advisory lock, abstração de
  relógio, `freezegun`, job, cache.
- Admin, URLs, API, comando de gestão, interface.
- Publicação ou alteração da baseline da 003; escrita em modelos das Features 001–004.
- Proibição global de nomes de modelo em testes: verificar escopo **por app** (R16).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: app Django vazio e registrado; suíte da 004 compatível.

- [X] T001 Criar o esqueleto do app e registrá-lo:
  - `trajetoria/participacao/__init__.py` (vazio);
  - `trajetoria/participacao/apps.py` com `ParticipacaoConfig(AppConfig)`,
    `name = "trajetoria.participacao"`, `verbose_name = "Participações"`;
  - `trajetoria/participacao/migrations/__init__.py` (vazio);
  - diretório `tests/participacao/` sem `__init__.py`;
  - em `config/settings.py`, acrescentar `"trajetoria.participacao"` a
    `INSTALLED_APPS` depois de `"trajetoria.campanha"`.

  Verificar com `uv run python manage.py check`.
- [X] T002 Pré-condição satisfeita: a correção de escopo do teste SC-009 da 004
  (`tests/campanha/test_campanha_aceitacao.py`, agora
  `test_app_campanha_tem_somente_o_modelo_campanha`, que exige que o app `campanha` tenha
  exatamente `["Campanha"]`, sem lista global de nomes) entrou na `main` pela própria
  Feature 004, em
  [saymoncastro/ifes-trajetoria-egressos#6](https://github.com/saymoncastro/ifes-trajetoria-egressos/pull/6)
  (research R16). O branch da 005 foi atualizado sobre essa `main` e **não** altera
  esse arquivo. Nada a fazer nesta feature.

**Checkpoint**: `manage.py check` sem erros; suíte da 004 verde.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: modelos, migração, vocabulário de rejeição e auxiliares de teste, usados por
todas as histórias.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T003 Escrever `tests/participacao/construcao.py` (auxiliares, não testes; depende
  de T006 por `ParticipacaoRejeitada`). Imports de `trajetoria.participacao.models` e
  `trajetoria.participacao.operacoes` ficam **dentro das funções** que os usam
  (`retrato`), para que o módulo importe antes de T007 e T010; imports das Features
  001–004 e de `regras` podem ficar no topo:
  - `momento(ano, mes, dia, hora=12) -> datetime`: `timezone.make_aware(datetime(…))`,
    sem fuso nominal (como `tests/campanha/construcao.py`, sem importar dele);
  - `instrumento(designacao="2027") -> Instrumento`: monta pelas operações da 002
    (`criar_pesquisa`, `criar_versao`, `adicionar_secao`, `adicionar_pergunta`,
    `adicionar_opcao`, `definir_regra`, `publicar`) uma Versão **publicada** com:
    - Seção 1:
      1. `unica` — `ESCOLHA_UNICA`, obrigatória, Opções "Sim" e "Não", com regra
         "Não" → `FINALIZAR` (para provar que navegação não é aplicada);
      2. `unica_outro` — `ESCOLHA_UNICA`, obrigatória, Opções "A", "B" e "Outro:"
         (`complemento_textual=True`);
      3. `multipla` — `ESCOLHA_MULTIPLA`, opcional, Opções "A", "B", "C" e "Outro:"
         (`complemento_textual=True`);
      4. `texto` — `TEXTO_CURTO`, obrigatória;
      5. `escala` — `ESCALA`, obrigatória, `Escala(inicio=1, fim=5,
         rotulo_fim="Concordo totalmente")` (de `trajetoria.instrumento.conteudo`);
      6. `campus` — `ESCOLHA_UNICA`, obrigatória, Opções "Campus Serra" e "Campus
         Vitória" (para o teste de proveniência);
    - Seção 2: `posterior` — `TEXTO_CURTO`, opcional (Pergunta "pulada" quando
      `unica = "Não"`).

    `Instrumento` é um `dataclass` com `versao`, as Perguntas acima e
    `opcao(pergunta, texto) -> Opcao` (busca por texto, só para os testes);
  - `instrumento_derivado(origem: Instrumento, designacao="2028") -> Instrumento`:
    `criar_versao_a_partir_de` + `publicar`, com textos idênticos e Perguntas e Opções
    novas (research R9; US12);
  - `conclusao(*, ano=2022, unidade="Serra", pessoa=None) -> ConclusaoAcademica`: cria
    por ORM `Pessoa` (se não informada) e `ConclusaoAcademica` com
    `fonte="teste-participacao"` e `id_externo` único (dados fictícios);
  - `campanha_aberta(versao, *, inicio=date(2027, 4, 1), fim=date(2027, 6, 30),
    abrir_em=momento(2027, 4, 1), **criterios) -> Campanha`: pelas operações da 004
    (`criar_campanha`, `definir_periodo`, `definir_criterios`, `abrir`);
  - `campanha_em_preparacao(versao) -> Campanha`: criada com período, sem abrir;
  - constantes `NO_PERIODO = momento(2027, 5, 1)`, `ULTIMO_DIA = momento(2027, 6, 30,
    23)`, `DEPOIS_DO_FIM = momento(2027, 7, 1)`;
  - `rejeita(motivos, operacao, *args, **kwargs)`: exige `ParticipacaoRejeitada` com
    `motivos` exatamente iguais à tupla dada e devolve as violações;
  - `retrato(participacao) -> dict`: a linha da Participação, as linhas das suas
    Respostas e das suas `RespostaOpcao` (por `values()`, ordenadas), para comparar
    antes e depois.
- [X] T004 Escrever `tests/participacao/conftest.py` (depende de T003) com as fixtures
  `inst` (`instrumento()`), `campanha` (`campanha_aberta(inst.versao,
  ano_minimo=2020)`), `conclusao` (`conclusao(ano=2022)`, elegível) e `participacao`
  (`iniciar_participacao(campanha, conclusao, agora=NO_PERIODO).participacao` —
  usada a partir de US3; `from trajetoria.participacao.operacoes import
  iniciar_participacao` **dentro da fixture**, porque `operacoes.py` só existe a partir
  de T010 e o `conftest.py` não pode quebrar a coleta dos testes da Fase 2).
  `fonte_simulada` vem de `tests/conftest.py`, sem redefinir.
- [X] T005 [P] Escrever `tests/participacao/test_participacao_modelo.py`, que DEVE falhar
  antes de T007. Escrita direta no ORM, cada caso em `transaction.atomic()`, esperando
  `IntegrityError`:
  - duas `Participacao` com a mesma `(campanha, conclusao)`;
  - duas `Resposta` com a mesma `(participacao, pergunta)`;
  - `Resposta` com `opcao` e `texto`; `opcao` e `escala`; `texto` e `escala`;
  - `Resposta.texto = ""`; `Resposta.complemento = ""`;
  - duas `RespostaOpcao` com a mesma `(resposta, opcao)`;

  e, sem erro:
  - `Resposta` só com `escala`, só com `texto`, só com `opcao`, sem nenhum dos três
    (escolha múltipla); `complemento` com `opcao` ou sem valor direto;
  - **limite documentado**: o banco aceita `Resposta` de múltipla sem `RespostaOpcao` e
    complemento ao lado de `texto` — essas regras são das operações (comentário no
    teste citando data-model);

  e as políticas de remoção:
  - remover `Campanha`, `ConclusaoAcademica`, `Pergunta` ou `Opcao` referenciadas →
    `ProtectedError`;
  - remover `Resposta` apaga suas `RespostaOpcao` (`CASCADE`).
- [X] T006 [P] Implementar `trajetoria/participacao/regras.py`, no padrão de
  `trajetoria/campanha/regras.py` (sem importar dele):
  - `Motivo(Enum)` com `COLETA_NAO_ADMITIDA`, `CONCLUSAO_NAO_ELEGIVEL`,
    `PARTICIPACAO_INEXISTENTE`, `PERGUNTA_DE_OUTRA_VERSAO`, `OPCAO_DE_OUTRA_PERGUNTA`,
    `VALOR_INCOMPATIVEL`, `ESCALA_FORA_DOS_LIMITES`, `COMPLEMENTO_NAO_ADMITIDO`,
    `VALOR_VAZIO`, cada um comentado com o item de FR-052;
  - `Violacao(motivo, campo: str | None, detalhe: str)` (`dataclass(frozen=True)`);
  - `ParticipacaoRejeitada(Exception)` com `violacoes` (≥ 1, senão `ValueError`), a
    propriedade `motivos` e `__str__` legível.
- [X] T007 Implementar `trajetoria/participacao/models.py` conforme
  [data-model.md](data-model.md) (depende de T001). Docstring citando o data-model e a
  regra "CHECKs só de colunas da própria linha; regras entre tabelas nas operações".
  Copiar o padrão `_nao_vazio(campo, nome)` dos outros apps, sem importar.
  - **`Participacao`**:
    - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`;
    - `campanha = ForeignKey("campanha.Campanha", on_delete=PROTECT, related_name="+")`;
    - `conclusao = ForeignKey("academico.ConclusaoAcademica", on_delete=PROTECT,
      related_name="+")`;
    - `iniciada_em = DateTimeField()` (sem `auto_now_add`: recebe o momento de
      referência);
    - `Meta.ordering = ["iniciada_em", "id"]`;
      `UniqueConstraint(fields=["campanha", "conclusao"], name="participacao_par_unico")`;
    - propriedades `pessoa` (`self.conclusao.pessoa`), `versao`
      (`self.campanha.versao`), `pesquisa` (`self.campanha.versao.pesquisa`).
  - **`Resposta`**:
    - `id` UUID como acima;
    - `participacao = ForeignKey(Participacao, on_delete=PROTECT,
      related_name="respostas")`;
    - `pergunta = ForeignKey("instrumento.Pergunta", on_delete=PROTECT,
      related_name="+")`;
    - `opcao = ForeignKey("instrumento.Opcao", on_delete=PROTECT, null=True,
      related_name="+")`;
    - `texto = TextField(null=True)`; `escala = IntegerField(null=True)`;
      `complemento = TextField(null=True)`;
    - `opcoes = ManyToManyField("instrumento.Opcao", through="RespostaOpcao",
      related_name="+")`;
    - constraints: `UniqueConstraint(fields=["participacao", "pergunta"],
      name="resposta_pergunta_unica")`; `_nao_vazio("texto",
      "resposta_texto_nao_vazio")`; `_nao_vazio("complemento",
      "resposta_complemento_nao_vazio")`; `CheckConstraint` "no máximo um valor
      direto" (`resposta_um_valor_direto`): nega cada par
      `(opcao, texto)`, `(opcao, escala)`, `(texto, escala)` com ambos
      `__isnull=False`. **Nenhum** CHECK sobre complemento × tipo.
  - **`RespostaOpcao`** (docstring: "tabela técnica do conjunto da escolha múltipla;
    sem significado de domínio"):
    - `id` UUID; `resposta = ForeignKey(Resposta, on_delete=CASCADE,
      related_name="+")`; `opcao = ForeignKey("instrumento.Opcao", on_delete=PROTECT,
      related_name="+")`;
    - `UniqueConstraint(fields=["resposta", "opcao"], name="resposta_opcao_unica")`;
    - sem posição, timestamp ou outro campo.
- [X] T008 Gerar `trajetoria/participacao/migrations/0001_initial.py` com
  `uv run python manage.py makemigrations participacao`. Conferir que cria só as três
  tabelas do app, depende das migrações de `campanha`, `academico` e `instrumento`, e
  não tem `RunSQL`. Rodar `uv run pytest tests/participacao/test_participacao_modelo.py`
  (DEVE passar) e `uv run pytest tests/instrumento tests/campanha` (continuam verdes:
  `related_name="+"` mantém o teste de isolamento da 002). Depende de T007.

**Checkpoint**: modelos e migração prontos; suítes 001–004 verdes.

---

## Phase 3: User Story 1 — Iniciar Participação para uma Conclusão elegível em Campanha aberta (Priority: P1) 🎯 MVP

**Goal**: criar a Participação de um par admitido pela 004, com momento de início, sem
convite nem autenticação.

**Independent Test**: Campanha aberta + Conclusão elegível → `CRIADA`; Conclusão não
elegível ou Campanha fora de coleta → rejeição sem nada criado.

- [X] T009 [US1] Escrever `tests/participacao/test_participacao_inicio.py` (DEVE falhar
  antes de T010):
  - início válido: `situacao is CRIADA`; `campanha`, `conclusao` e `iniciada_em ==
    NO_PERIODO`; `respostas_atuais` ainda não existe — verificar zero linhas em
    `Resposta` por ORM; `pessoa`, `versao` e `pesquisa` derivadas iguais às da Conclusão
    e da Campanha (US1.1, US1.2);
  - Conclusão não elegível (`ano=2010` numa Campanha com `ano_minimo=2020`) →
    `CONCLUSAO_NAO_ELEGIVEL`, `detalhe` cita o critério `ano_conclusao` e não contém
    `2010`; nenhuma linha (US1.3);
  - Campanha em preparação; encerrada explicitamente (`encerrar` da 004); com `agora =
    DEPOIS_DO_FIM` → `COLETA_NAO_ADMITIDA`, nada criado (US1.4);
  - Campanha encerrada **e** Conclusão não elegível → as duas violações, nessa ordem
    (US1.5, FR-012);
  - sem convite: o teste não cria nada além de Campanha e Conclusão (US1.6);
  - `TypeError` para `campanha` ou `conclusao` de classe errada e para `agora` ingênuo
    ou `date`, sem nenhuma linha criada.
- [X] T010 [US1] Implementar em `trajetoria/participacao/operacoes.py` (docstring citando
  [contracts/operacoes.md](contracts/operacoes.md); `__all__` explícito):
  - `SituacaoInicio(Enum)` (`CRIADA`, `JA_EXISTENTE`) e `Inicio(NamedTuple)`
    (`participacao`, `situacao`);
  - `iniciar_participacao(campanha, conclusao, *, agora=None) -> Inicio`: tipos →
    `momento_de_referencia(agora)` → relê Campanha e Conclusão do banco →
    `admite_participacao(campanha, conclusao, agora=…)`; se falso, reúne
    `COLETA_NAO_ADMITIDA` (`estado(…) is not EM_COLETA`) e `CONCLUSAO_NAO_ELEGIVEL`
    (`avaliar(…).pendencias`, só nomes de critério e motivo no `detalhe`) numa única
    `ParticipacaoRejeitada`; se verdadeiro, cria com `iniciada_em = agora` e devolve
    `CRIADA`. Tudo em `transaction.atomic()`. (Idempotência vem em US2.)

**Checkpoint**: `uv run pytest tests/participacao/test_participacao_inicio.py` verde.

---

## Phase 4: User Story 2 — Garantir uma única Participação por Campanha × Conclusão (Priority: P1)

**Goal**: início idempotente, inclusive com Campanha encerrada e sob corrida.

**Independent Test**: iniciar o mesmo par várias vezes → uma linha, mesmo `id`, mesmo
`iniciada_em`; ramo de corrida forçado → `JA_EXISTENTE`.

- [X] T011 [US2] Acrescentar a `tests/participacao/test_participacao_inicio.py` (DEVEM
  falhar antes de T013):
  - repetição → `JA_EXISTENTE`, mesmo `id` e `iniciada_em`, `retrato` idêntico, uma
    linha (US2.1, SC-002);
  - repetição com `agora = DEPOIS_DO_FIM` (Campanha encerrada pela data) e depois de
    `encerrar` explícito → devolve a existente, sem alteração; a escrita continua
    bloqueada (verificada em US11) (US2.3, FR-013);
  - repetição depois de a Conclusão sair dos critérios (alterar `ano_conclusao` por ORM
    para 2010, simulando 001/DP-005) → `JA_EXISTENTE` (FR-034, DP-507);
  - não existe operação de reinício, tentativa ou nova Participação do par (US2.4):
    `operacoes.__all__` é exatamente o conjunto do contrato.
- [X] T012 [P] [US2] Escrever `tests/participacao/test_participacao_concorrencia.py`
  (DEVE falhar antes de T013), **determinístico**: cria a Participação do par por ORM e
  faz `monkeypatch` de `operacoes._participacao_existente` para devolver `None` na
  primeira chamada; `iniciar_participacao` deve cair no `IntegrityError` do savepoint,
  reler e devolver `JA_EXISTENTE` com a Participação já gravada; ao final, uma linha
  (R11, R17, FR-006).
- [X] T013 [US2] Em `trajetoria/participacao/operacoes.py`, completar
  `iniciar_participacao`:
  - auxiliar privado `_participacao_existente(campanha, conclusao) ->
    Participacao | None` (ponto do `monkeypatch` de T012);
  - par existente → `(existente, JA_EXISTENTE)`, sem consultar estado nem elegibilidade
    e sem gravar;
  - criação dentro de `transaction.atomic()` aninhado (savepoint); `IntegrityError` →
    relê pelo par; se encontrar, devolve `JA_EXISTENTE`; se **não** encontrar (o
    `IntegrityError` não veio da unicidade do par), relança o `IntegrityError`
    original. Sem bloqueio da Campanha, sem retry, sem framework de locking.
- [X] T014 [US2] (Opcional, R17) Acrescentar a
  `tests/participacao/test_participacao_concorrencia.py` um teste real com
  `@pytest.mark.django_db(transaction=True)`, `threading.Barrier(2)` e duas threads
  chamando `iniciar_participacao` no mesmo par (cada thread fecha sua conexão em
  `finally`): exatamente uma linha e o mesmo `id` nas duas threads. **Se for instável no
  CI, remover** — o teste determinístico de T012 é a proteção suficiente. Depende de
  T013.

**Checkpoint**: início idempotente; `tests/participacao/test_participacao_inicio.py` e
`test_participacao_concorrencia.py` verdes.

---

## Phase 5: User Story 3 — Registrar resposta de escolha única (Priority: P1)

**Goal**: esqueleto comum das escritas + escolha única por identidade da Opção.

**Independent Test**: registrar uma Opção válida e consultá-la por ORM; Opção de outra
Pergunta, nenhuma Opção, coleção ou texto → rejeitados sem gravar.

- [X] T015 [US3] Escrever `tests/participacao/test_participacao_respostas.py` (seção
  escolha única; DEVE falhar antes de T016):
  - "Sim" em `inst.unica` → uma Resposta com `opcao` = "Sim", `texto`, `escala`,
    `complemento` nulos, nenhuma `RespostaOpcao` (US3.1);
  - Opção de **outra Pergunta com o mesmo texto**: a Opção "A" de `inst.multipla`
    respondida em `inst.unica_outro` (que também tem "A") → `OPCAO_DE_OUTRA_PERGUNTA`
    (US3.3, FR-028); "Campus Serra" de `inst.campus` respondida em `inst.unica` → idem;
  - `opcao=None` → `VALOR_VAZIO` (`campo="opcao"`); lista com uma Opção →
    `VALOR_INCOMPATIVEL`; texto `"Sim"` → `VALOR_INCOMPATIVEL` (US3.2);
  - `responder_escolha_unica` em `inst.texto` (Pergunta de outro tipo) →
    `VALOR_INCOMPATIVEL`;
  - responder "Não" (Opção com regra `FINALIZAR`) não cria, altera nem remove outras
    Respostas (US3.4, FR-038);
  - registrar duas vezes a mesma Pergunta → uma linha (FR-018); registrar de novo o
    **mesmo valor** → aceito, mesmo `id`, `retrato` idêntico (FR-036);
  - `TypeError` para `participacao` ou `pergunta` de classe errada e `agora` ingênuo;
  - em toda rejeição, `retrato` idêntico antes e depois.
- [X] T016 [US3] Em `trajetoria/participacao/operacoes.py`, implementar o esqueleto
  privado das escritas (`_escrever(participacao, pergunta, tipo, agora, gravar)` ou
  equivalente simples, passos 1–5 e 7 das convenções) e
  `responder_escolha_unica(participacao, pergunta, opcao, *, agora=None) -> Resposta`
  (passo 6: `None` → `VALOR_VAZIO`; não `Opcao` → `VALOR_INCOMPATIVEL`; fora da Pergunta
  pelo banco → `OPCAO_DE_OUTRA_PERGUNTA`). Gravação: `opcao` preenchida; `texto`,
  `escala`, `complemento` nulos; apaga `RespostaOpcao` da Resposta (defensivo). O
  parâmetro `complemento` entra em US8.

**Checkpoint**: escolha única verde; esqueleto pronto para os demais tipos.

---

## Phase 6: User Story 4 — Registrar resposta de escolha múltipla (Priority: P1)

**Goal**: conjunto não vazio de Opções da Pergunta, numa única Resposta.

**Independent Test**: `{A, C}` e `{C, A}` iguais; `{A, A}` = `{A}`; vazio e `{A, X}`
rejeitados sem gravar.

- [X] T017 [US4] Acrescentar a `tests/participacao/test_participacao_respostas.py` (seção
  escolha múltipla; DEVEM falhar antes de T018):
  - `{A, C}` → uma Resposta; `opcao`, `texto`, `escala` nulos; duas `RespostaOpcao`
    (US4.1);
  - `[C, A]` em outra Participação (outra Conclusão) → mesmo conjunto; leitura de
    `resposta.opcoes.all()` na ordem do instrumento (A, C) (US4.2);
  - `[A, A]` → `{A}`, uma `RespostaOpcao` (US4.3);
  - `[]` e `set()` → `VALOR_VAZIO` (`campo="opcoes"`), nenhuma linha (US4.4);
  - `[A, X]` com X Opção de `inst.unica` → `OPCAO_DE_OUTRA_PERGUNTA`, nem A gravada
    (US4.5);
  - todas as Opções aceitas (sem máximo nem exclusividade) (US4.6);
  - `None` → `VALOR_VAZIO` (`campo="opcoes"`);
  - `"A"` (str) e uma `Opcao` isolada → `VALOR_INCOMPATIVEL`;
  - `responder_escolha_multipla` em `inst.unica` → `VALOR_INCOMPATIVEL`.
- [X] T018 [US4] Implementar em `trajetoria/participacao/operacoes.py`
  `responder_escolha_multipla(participacao, pergunta, opcoes, *, agora=None) ->
  Resposta`: `None` → `VALOR_VAZIO`; aceita coleção iterável (não `str`, não `Opcao`)
  de `Opcao`; deduplica por `pk`; vazio → `VALOR_VAZIO`; confere pelo banco que todas são da Pergunta; grava a
  Resposta com valores diretos nulos e substitui o conjunto (apaga e `bulk_create` de
  `RespostaOpcao`) na mesma transação. Devolve a Resposta relida.

**Checkpoint**: escolha múltipla verde.

---

## Phase 7: User Story 5 — Registrar resposta textual (Priority: P1)

**Goal**: texto não vazio, preservado exatamente.

**Independent Test**: `"  27 anos "` volta idêntico; vazio rejeitado.

- [X] T019 [US5] Acrescentar a `tests/participacao/test_participacao_respostas.py` (seção
  texto; DEVEM falhar antes de T020):
  - `"  27 anos "` gravado e lido exatamente (US5.1);
  - `"2020/2"` aceito, sem validação de ano (US5.2);
  - `None`, `""` e `"   "` → `VALOR_VAZIO` (`campo="texto"`), Pergunta continua sem Resposta
    (US5.3);
  - `3` e uma `Opcao` → `VALOR_INCOMPATIVEL`; `responder_texto` em
    `inst.escala` → `VALOR_INCOMPATIVEL` (US5.4).
- [X] T020 [US5] Implementar em `trajetoria/participacao/operacoes.py`
  `responder_texto(participacao, pergunta, texto, *, agora=None) -> Resposta`: `None`
  → `VALOR_VAZIO`; não `str` → `VALOR_INCOMPATIVEL`; `not texto.strip()` →
  `VALOR_VAZIO`; grava sem
  `strip()`, sem limite, regex ou conversão.

**Checkpoint**: texto verde.

---

## Phase 8: User Story 6 — Registrar resposta de escala (Priority: P1)

**Goal**: inteiro dentro dos limites da Pergunta histórica.

**Independent Test**: 1, 3, 5 aceitos; 0, 6 fora dos limites; `2.5`, `"3"`, `True`
incompatíveis.

- [X] T021 [US6] Acrescentar a `tests/participacao/test_participacao_respostas.py` (seção
  escala; DEVEM falhar antes de T022):
  - 1, 3 e 5 → `escala` igual ao inteiro; nenhum rótulo gravado (US6.1, US6.4);
  - 0 e 6 → `ESCALA_FORA_DOS_LIMITES` (US6.2);
  - `2.5`, `"3"` e `True` → `VALOR_INCOMPATIVEL` (US6.3);
  - `None` → `VALOR_VAZIO` (`campo="escala"`), Pergunta continua sem Resposta;
  - `responder_escala` em `inst.texto` → `VALOR_INCOMPATIVEL`.
- [X] T022 [US6] Implementar em `trajetoria/participacao/operacoes.py`
  `responder_escala(participacao, pergunta, valor, *, agora=None) -> Resposta`:
  `None` → `VALOR_VAZIO`; `type(valor) is not int` → `VALOR_INCOMPATIVEL` (exclui
  `bool`); fora de
  `[pergunta.escala_inicio, pergunta.escala_fim]` (Pergunta relida) →
  `ESCALA_FORA_DOS_LIMITES`; grava o inteiro.

**Checkpoint**: os quatro tipos verdes (`tests/participacao/test_participacao_respostas.py`).

---

## Phase 9: User Story 7 — Alterar e remover respostas em rascunho (Priority: P1)

**Goal**: substituição integral no lugar e remoção, sem histórico.

**Independent Test**: sequências de registrar/substituir/remover deixam só o último
valor; remover volta a não respondida.

- [X] T023 [US7] Escrever `tests/participacao/test_participacao_rascunho.py` (DEVE falhar
  antes de T024 nas partes de remoção):
  - "Sim" → "Não" em `unica`: mesmo `id` de Resposta, `opcao` = "Não", uma linha
    (US7.1, FR-018);
  - `{A, B}` → `{C}` em `multipla`: conjunto `{C}`, sem resto de A ou B (US7.2);
  - `remover_resposta` → `REMOVIDA`, nenhuma linha de Resposta nem de `RespostaOpcao`
    da Pergunta (US7.3); "limpar" a múltipla é remover (Clarifications);
  - remover inexistente → `INEXISTENTE`, `retrato` idêntico (US7.4);
  - remover Resposta de Pergunta obrigatória → aceito (US7.5);
  - Participação com zero, algumas e todas as Respostas: nenhum campo ou consulta de
    conclusão ou progresso existe (US7.6) — `Participacao` sem atributo `concluida_em`
    ou `estado`;
  - **atomicidade da múltipla**: `{A, B}` gravado; `[C, X]` (X de outra Pergunta)
    rejeitado → continua `{A, B}`, mesmo `id` (FR-051, US12.4);
  - navegação não aplicada: responder `unica = "Não"` (regra `FINALIZAR`) e depois
    `posterior` (Seção 2) → aceito; mudar `unica` de "Sim" para "Não" mantém a Resposta
    de `posterior` (FR-038);
  - `remover_resposta` com Pergunta de outra Versão → `PERGUNTA_DE_OUTRA_VERSAO`.
- [X] T024 [US7] Implementar em `trajetoria/participacao/operacoes.py`
  `SituacaoRemocao(Enum)` (`REMOVIDA`, `INEXISTENTE`) e
  `remover_resposta(participacao, pergunta, *, agora=None) -> SituacaoRemocao`
  (passos 1–4 do esqueleto; apaga a Resposta — `CASCADE` leva as `RespostaOpcao`).
  Nenhum histórico, evento ou log.

**Checkpoint**: rascunho editável; MVP P1 completo.

---

## Phase 10: User Story 8 — Registrar complemento textual de "Outro" (Priority: P2)

**Goal**: complemento só com a Opção que o admite selecionada, numa coluna única.

**Independent Test**: "Outro:" com complemento aceito em única e múltipla; sem a Opção,
vazio ou em outro tipo → rejeitado.

- [X] T025 [US8] Acrescentar a `tests/participacao/test_participacao_respostas.py` (seção
  complemento; DEVEM falhar antes de T026):
  - `unica_outro` = "Outro:" com `complemento="Cuidando de familiar"` → gravado
    exatamente (US8.1);
  - `multipla` = `{A, Outro:}` com complemento → uma Resposta, conjunto e complemento
    (US8.2);
  - `unica_outro` = "A" com complemento; `multipla` = `{A, B}` com complemento →
    `COMPLEMENTO_NAO_ADMITIDO`, nada gravado (US8.3);
  - complemento `""` ou `"  "` → `VALOR_VAZIO` (`campo="complemento"`); complemento
    não `str` → `VALOR_INCOMPATIVEL` (US8.7);
  - "Outro:" sem complemento → aceito, `complemento` nulo (US8.6);
  - "Outro:" com complemento substituído por "A" sem complemento → `complemento` nulo
    (US8.5);
  - `responder_texto` e `responder_escala` não aceitam o parâmetro `complemento`
    (`TypeError` de Python por argumento inesperado) — FR-030 b pela assinatura
    (US8.4).
- [X] T026 [US8] Em `trajetoria/participacao/operacoes.py`, acrescentar
  `complemento=None` a `responder_escolha_unica` e `responder_escolha_multipla`:
  vazio → `VALOR_VAZIO`; não `str` → `VALOR_INCOMPATIVEL`; Opção com
  `complemento_textual` não selecionada (`opcao` em única; ausente do conjunto em
  múltipla, verificado pelas Opções relidas) → `COMPLEMENTO_NAO_ADMITIDO`; validação
  **antes** de gravar; grava a coluna `complemento` (ou `NULL`). Sem generalizar para
  outros tipos.

**Checkpoint**: complemento verde.

---

## Phase 11: User Story 9 — Recuperar o estado atual de uma Participação (Priority: P2)

**Goal**: consultas suficientes para a 006, sem modelo de tela.

**Independent Test**: respostas dos quatro tipos e complemento → `respostas_atuais`
distingue não respondida e dá o valor tipado; `localizar_participacao` não cria.

- [X] T027 [US9] Escrever `tests/participacao/test_participacao_consulta.py` (DEVE falhar
  antes de T028):
  - `respostas_atuais` com algumas Perguntas respondidas: chaves = ids das Perguntas
    respondidas; Pergunta não respondida ausente; valores por tipo (`opcao`,
    `set(opcoes.all())`, `complemento`, `texto`, `escala`) (US9.1, FR-047);
  - percorrer as Perguntas de `participacao.versao` e classificar cada uma em
    respondida/não respondida pelo dicionário;
  - `localizar_participacao` de par sem Participação → `None`, nenhuma linha criada, em
    EM_PREPARACAO, EM_COLETA e ENCERRADA (US9.2);
  - `admite_escrita` verdadeiro em `NO_PERIODO`, falso em `DEPOIS_DO_FIM` (US9.3);
  - **proveniência**: Conclusão com `unidade="Serra"` e resposta "Campus Vitória" em
    `inst.campus` coexistem; `participacao.conclusao.unidade == "Serra"`; a linha da
    Conclusão é idêntica antes e depois de todas as escritas; nenhuma Resposta é criada
    a partir da Conclusão (US9.4, FR-042–FR-044, SC-009);
  - consultas não gravam: `retrato` idêntico antes e depois (US9.5);
  - `respostas_atuais` não faz consultas por Resposta além do pré-carregamento
    (`django_assert_max_num_queries`), apenas como proteção de uso.
- [X] T028 [US9] Implementar `trajetoria/participacao/consultas.py` (docstring citando
  [contracts/consultas.md](contracts/consultas.md); `__all__` explícito):
  - `localizar_participacao(campanha, conclusao) -> Participacao | None`;
  - `participacoes_da_conclusao(conclusao) -> tuple[Participacao, ...]`, ordem
    `(iniciada_em, id)`;
  - `admite_escrita(participacao, *, agora=None) -> bool` = `estado(…) is EM_COLETA`;
  - `respostas_atuais(participacao) -> dict[UUID, Resposta]`, com
    `select_related("pergunta", "opcao")` e `prefetch_related("opcoes")`, chave
    `pergunta_id`.

  Nada grava, nada calcula progresso, próxima Pergunta ou obrigatoriedade.

**Checkpoint**: consultas verdes.

---

## Phase 12: User Story 10 — Permitir a mesma Conclusão em Campanhas diferentes (Priority: P2)

**Goal**: Participações independentes ao longo do tempo.

**Independent Test**: a mesma Conclusão em Campanhas 2025, 2027 e 2030 → três
Participações; alterar uma não muda as outras.

- [X] T029 [P] [US10] Escrever `tests/participacao/test_participacao_longitudinal.py`
  (comportamento já entregue; pode passar de imediato):
  - Conclusão ADS — 2024 (fictícia) com Participações em três Campanhas com períodos
    2025, 2027 e 2030, cada uma iniciada com `agora` no próprio período (US10.1);
  - alterar resposta na de 2030 → `retrato` das de 2025 e 2027 idêntico (US10.2,
    SC-003);
  - nova Participação nasce sem Respostas, nada copiado (US10.3);
  - `participacoes_da_conclusao` devolve as três em ordem `(iniciada_em, id)` (US10.4);
  - Pessoa com duas Conclusões elegíveis na mesma Campanha → duas Participações
    independentes (US10.5, FR-009);
  - duas Campanhas sobrepostas EM_COLETA com a mesma Conclusão → uma Participação em
    cada (FR-007).
- [X] T030 [US10] Se T029 falhar, corrigir em `trajetoria/participacao/operacoes.py` ou
  `trajetoria/participacao/consultas.py` sem novo conceito; senão, nada a fazer.

---

## Phase 13: User Story 11 — Bloquear alterações quando a Campanha não admite mais coleta (Priority: P2)

**Goal**: nenhuma escrita fora de EM_COLETA; leitura e dados intactos.

**Independent Test**: depois do encerramento (explícito e por data), toda escrita é
rejeitada e o `retrato` não muda.

- [X] T031 [P] [US11] Escrever `tests/participacao/test_participacao_coleta.py`
  (comportamento já entregue; pode passar de imediato):
  - Respostas registradas; Campanha encerrada com `encerrar` da 004 → registrar (cada
    um dos quatro tipos), substituir e remover → `COLETA_NAO_ADMITIDA`; `retrato`
    idêntico (US11.1, SC-008);
  - o mesmo com `agora = DEPOIS_DO_FIM`, sem nenhum processo (US11.2);
  - escrita com `agora = ULTIMO_DIA` aceita; com `DEPOIS_DO_FIM`, rejeitada (US11.5);
  - nova Participação de Conclusão elegível depois do fim → `COLETA_NAO_ADMITIDA`
    (US11.3);
  - leitura depois do encerramento: `respostas_atuais` e `localizar_participacao`
    iguais às de antes; `admite_escrita` falso; nada apagado ou marcado (US11.4, FR-040);
  - início repetido depois do encerramento devolve a existente e a escrita seguinte
    continua rejeitada (FR-013, FR-039);
  - **elegibilidade só no início**: Participação criada; `ano_conclusao` da Conclusão
    alterado por ORM para fora dos critérios; `responder_texto` continua aceito durante
    a coleta (FR-034, DP-507).
- [X] T032 [US11] Se T031 falhar, corrigir o passo 3 do esqueleto em
  `trajetoria/participacao/operacoes.py`; senão, nada a fazer. Sem prazo de graça
  (DP-502).

---

## Phase 14: User Story 12 — Rejeitar referências e valores incompatíveis (Priority: P3)

**Goal**: nenhuma referência fora da Versão aplicada; lista mínima de rejeições coberta.

**Independent Test**: Versões 2027 e 2028 (textos idênticos) → toda referência a 2028
numa Participação de 2027 é rejeitada; cada item de FR-052 tem caso de teste.

- [X] T033 [P] [US12] Escrever `tests/participacao/test_participacao_versao.py`
  (comportamento já entregue; pode passar de imediato):
  - `inst28 = instrumento_derivado(inst)`; Participação na Campanha de 2027;
    `inst28.texto` → `PERGUNTA_DE_OUTRA_VERSAO` (US12.1);
  - Opção "Sim" de `inst28.unica` em `inst.unica` → `OPCAO_DE_OUTRA_PERGUNTA`; o mesmo
    em escolha múltipla (US12.2, SC-006);
  - Respostas de 2027 gravadas antes e depois de criar e publicar 2028: `retrato`
    idêntico e validação continua pela Versão 2027 (US12.3, SC-010);
  - tabela FR-052 a–i, um caso por item, cada um com `retrato` idêntico (US12.5,
    SC-005); `PARTICIPACAO_INEXISTENTE` com instância de `Participacao` não gravada;
  - nenhuma mensagem (`str(erro)` e `detalhe`) contém texto, inteiro ou complemento
    declarados (FR-059).
- [X] T034 [US12] Se T033 falhar, corrigir em `trajetoria/participacao/operacoes.py`;
  senão, nada a fazer.

---

## Phase 15: Polish & Cross-Cutting Concerns

**Purpose**: aceitação ponta a ponta, escopo e verificação final. Nenhuma funcionalidade
nova.

- [X] T035 Escrever `tests/participacao/test_participacao_aceitacao.py`:
  - as **11 perguntas de sucesso** do solicitante (spec, tabela de cobertura), um teste
    cada, reaproveitando auxiliares;
  - **escopo por app e por modelo, sem proibição global por nome** (R16):
    - `{m.__name__ for m in apps.get_app_config("participacao").get_models()} ==
      {"Participacao", "Resposta", "RespostaOpcao"}`;
    - campos concretos exatos: `Participacao` = `id, campanha, conclusao,
      iniciada_em`; `Resposta` = `id, participacao, pergunta, opcao, texto, escala,
      complemento`; `RespostaOpcao` = `id, resposta, opcao`;
    - campos concretos de `Campanha`, `ConclusaoAcademica`, `Pergunta` e `Opcao`
      inalterados (listas dos data-models da 004, 001 e 002);
  - a baseline da 003 continua `RASCUNHO`.
- [X] T036 [P] Atualizar `README.md` com o link "Participação e respostas em rascunho:
  [quickstart da Feature 005](specs/005-participacao-respostas-rascunho/quickstart.md)".
  Ajustar a tabela de `specs/005-participacao-respostas-rascunho/quickstart.md` se
  nomes de arquivos de teste mudarem (hoje: 10 arquivos; consulta em
  `test_participacao_consulta.py`; Versão em `test_participacao_versao.py`).
- [X] T037 Rodar e registrar o resultado:
  - `uv run pytest` (suíte completa: 001–005 verdes);
  - `uv run ruff check .`;
  - `uv run python manage.py check`;
  - `uv run python manage.py makemigrations --check --dry-run`;
  - `git diff --stat main -- trajetoria/academico trajetoria/fonte_academica
    trajetoria/instrumento trajetoria/formulario_2024 trajetoria/campanha tests/test_*.py
    tests/instrumento tests/campanha config/urls.py` vazio (a correção de T002 chega pela
    `main`); em `config/`, só a linha de `INSTALLED_APPS`; nenhum `admin.py`, `urls.py`
    ou `management/` em `trajetoria/participacao/` (FR-058);
  - se o teste com threads de T014 falhar de forma intermitente, removê-lo e registrar.
- [X] T038 Conferir a Constitution e a Definition of Done e registrar em
  `specs/005-participacao-respostas-rascunho/plan.md` uma "Revisão pós-implementação":
  - gate mantido; nada da lista "Limites" criado;
  - nenhum log ou dado declarado em mensagens;
  - DP-501 a DP-508 e as herdadas continuam abertas, sem regra implícita;
  - Complexity Tracking continua vazio.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (T001; T002 já feito)** → **Foundational (T003–T008)** → histórias →
  **Polish (T035–T038)**.
- Na Foundational:
  - T005 e T006 em paralelo; T003 depois de T006; T004 depois de T003;
  - T007 depende de T001; T008 de T007 (e T005 deve falhar antes).

### User Story Dependencies

- **US1** (T009–T010): Foundational.
- **US2** (T011–T014): US1 (completa `iniciar_participacao`).
- **US3** (T015–T016): US2 (fixture `participacao` usa o início idempotente) — cria o
  esqueleto das escritas.
- **US4** (T017–T018), **US5** (T019–T020), **US6** (T021–T022): US3 (esqueleto);
  sequenciais entre si por compartilharem `operacoes.py` e
  `test_participacao_respostas.py`.
- **US7** (T023–T024): US3 e US4.
- **US8** (T025–T026): US3 e US4.
- **US9** (T027–T028): US3–US8 (consulta todos os tipos e complemento).
- **US10** (T029–T030): US9 (`participacoes_da_conclusao`).
- **US11** (T031–T032): US7 e US9 (`admite_escrita`).
- **US12** (T033–T034): US3–US8.

### Within Each User Story

- Testes primeiro; DEVEM falhar quando trazem comportamento novo.
- `operacoes.py` e `test_participacao_respostas.py` são editados sequencialmente.

### Parallel Opportunities

- Foundational: T005 e T006 (arquivos distintos).
- US2: T012 em paralelo com T011.
- Depois de US9: T029, T031 e T033 (arquivos distintos).
- Polish: T036 em paralelo com T035.

---

## Parallel Example: depois de US9

```bash
Task: "T029 Longitudinal em tests/participacao/test_participacao_longitudinal.py"
Task: "T031 Encerramento em tests/participacao/test_participacao_coleta.py"
Task: "T033 Versão e rejeições em tests/participacao/test_participacao_versao.py"
```

---

## Implementation Strategy

### MVP First

1. Setup + Foundational (T001–T008).
2. US1 → US7 (T009–T024): início idempotente, quatro tipos, substituição e remoção.
3. **STOP and VALIDATE**: `uv run pytest tests/participacao`.

### Incremental Delivery

4. US8 (complemento) → US9 (consultas) → US10 (longitudinal) → US11 (encerramento) →
   US12 (Versão e rejeições).
5. Polish (T035–T038).

---

## Decisões Pendentes preservadas

Nenhuma task resolve DP-501 a DP-508, 001/DP-005, 001/DP-009, 002/DP-001, 002/DP-006,
002/DP-007, 003/DP-302, 003/DP-303, 003/DP-309, 004/DP-404, 004/DP-406 ou 004/DP-408. Em
particular:

- uma Participação por Conclusão, sem compartilhar respostas (DP-501);
- nenhuma escrita fora de EM_COLETA (DP-502);
- nenhuma remoção de Participação (DP-503);
- Q1 é Resposta comum; só dados fictícios (DP-504);
- nenhum ponto de entrada (DP-505);
- elegibilidade só no início (DP-507);
- divergência declarado × institucional preservada, sem tratamento (DP-508);
- a baseline da 003 não é publicada (002/DP-001).

## Notes

- 38 tasks (T002 já concluída):
  - 16 escrevem testes: T005, T009, T011, T012, T014 (opcional), T015, T017, T019,
    T021, T023, T025, T027, T029, T031, T033, T035;
  - 2 criam auxiliares e fixtures de teste: T003, T004;
  - 2 são de verificação final: T037, T038;
  - 18 são de implementação, configuração ou documentação: T001, T002, T006, T007,
    T008, T010, T013, T016, T018, T020, T022, T024, T026, T028, T030, T032, T034,
    T036. Três delas (T030, T032, T034) são condicionais.
- Arquivos de produção: `apps.py`, `models.py`, `regras.py`, `operacoes.py`,
  `consultas.py`, `0001_initial.py`.
- Commit após cada checkpoint.
