---

description: "Tasks da Feature 006 — Jornada de resposta e conclusão da Participação"
---

# Tasks: Jornada de resposta e conclusão da Participação

**Input**: Design documents from `specs/006-jornada-conclusao-participacao/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Stack (confirmada; [ADR 0001](../../docs/adr/0001-stack-inicial.md))**: Python 3.13,
Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff. Nenhuma dependência
nova. Nenhum gatilho, função PostgreSQL, `RunSQL`, `RunPython`, `save()`/`delete()`
sobrescrito, sinal, serviço, repositório, job ou cache.

**Tests**: obrigatórios e escritos antes da implementação correspondente (test-first).
Todas as histórias tocam invariantes constitucionais (preservação histórica,
condicionais, associação de respostas, longitudinalidade). Testes de comportamento novo
DEVEM falhar primeiro. Histórias que só verificam comportamento já entregue por história
anterior (US4, US5, US8, US9, US10, US11) podem passar de imediato; se falharem, a
correção vai no arquivo indicado na tarefa condicional, sem criar regra especial.

**Organization**: tarefas agrupadas pelas histórias da spec (US1–US12). `percurso.py`,
`operacoes.py`, `consultas.py` e os arquivos de teste compartilhados são editados em
sequência.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US12).

## Convenções para todas as tarefas

- **Modelo**: a única alteração estrutural é `Participacao.concluida_em =
  models.DateTimeField(null=True)` — "`NULL` = em rascunho; preenchido = concluída.
  Gravado uma única vez, por `concluir`, com o momento de referência da conclusão
  aceita. Nunca alterado nem apagado" ([data-model](data-model.md#participacao-alterada)).
  Sem `default`, `auto_now`, índice, CHECK, enum ou backfill. Nenhum modelo novo;
  `Resposta` e `RespostaOpcao` sem colunas novas.
- **`percurso.py` é puro** ([contrato](contracts/percurso.md#pureza)): não importa
  `django.db`, modelos, `conteudo_da_versao` nem `respostas_atuais`; não executa query.
  Importa só os tipos de `trajetoria.instrumento.conteudo` (`ConteudoVersao`,
  `ConteudoSecao`, `ConteudoPergunta`, `ConteudoOpcao`, `RegraNavegacao`) e
  `trajetoria.participacao.regras`. Recebe `conteudo` e `respondidas: Mapping[UUID, UUID |
  None]` (Pergunta → Opção escolhida em escolha única; `None` nos demais tipos). Quem
  carrega dados é `consultas.py`/`operacoes.py`: `conteudo_da_versao(campanha.versao)` e
  `{pid: r.opcao_id for pid, r in respostas_atuais(p).items()}`. Nenhuma árvore paralela
  nem DTO novo.
- **Precedência de destino** (FR-012), exatamente: (1) regra acionada da Pergunta com
  regra respondida; (2) Pergunta com regra obrigatória sem Resposta → `INDETERMINADA`;
  (3) encaminhamento da Seção; (4) Seção seguinte na ordem; (5) `FINALIZACAO`. Nenhuma
  outra precedência; nenhuma regra especial para Q1, Q46 ou Q51.
- **Leitura histórica sem gate temporal** (research R18): o estado da Campanha
  (`estado` da 004) só é consultado para criar Participação (005), escrever Resposta
  (005) e concluir rascunho. `situacao_da_jornada` de Participação concluída **não**
  chama `estado`; para rascunho, `agora` só afeta `admite_escrita` e
  `COLETA_NAO_ADMITIDA`.
- **Ordem de `concluir`** ([contrato](contracts/conclusao.md#passos), aprovada): bloquear
  → já concluída devolve `JA_CONCLUIDA` (sem consultar Campanha, sem revalidar, sem
  limpar) → relógio → coleta → carregar Versão e Respostas → `percorrer` (estrutura) →
  `pendencias` → coerência das Respostas ativas → rejeitar com todas as violações → só
  então remover Respostas fora do percurso final → gravar `concluida_em`. Uma transação.
- **Rejeição**: sempre `ParticipacaoRejeitada` com `Violacao(motivo, campo, detalhe)`.
  `detalhe` cita Seção e Pergunta por `id` técnico, nunca valor declarado. Nenhum log.
- **Tempo**: `concluir` e `situacao_da_jornada` recebem `agora: datetime | None = None`,
  via `momento_de_referencia`/`estado` de `trajetoria.campanha.consultas`. Em `concluir`,
  o relógio padrão é lido depois do bloqueio. **Todo teste passa `agora` explícito**
  (`momento(...)`, `NO_PERIODO`, `ULTIMO_DIA`, `DEPOIS_DO_FIM` de
  `tests/participacao/construcao.py`).
- **Baseline**: a Versão da 003 (`materializar()`) **nunca** é publicada nem alterada.
  Testes puros usam a fixture `baseline` (`tests/instrumento/formulario_2024_esperado.py`,
  transação desfeita) e o oráculo `PERCURSOS` do mesmo módulo, que **não** vira código de
  produção. Testes de ponta a ponta usam uma **cópia** criada por
  `criar_versao_a_partir_de` e publicada só no banco de teste.
- **Testes**: `tests/participacao/` continua **sem** `__init__.py`; auxiliares via
  `from tests.participacao.construcao import …`; testes de banco com
  `pytestmark = pytest.mark.django_db`; testes unitários de `percurso.py` **sem**
  `django_db` (o pytest-django bloqueia acesso ao banco, o que prova a pureza).
- **Dados**: somente fictícios (005/DP-504).
- **Features 001–004**: nenhuma alteração em `trajetoria/academico/`,
  `trajetoria/fonte_academica/`, `trajetoria/instrumento/`, `trajetoria/formulario_2024/`,
  `trajetoria/campanha/`, `config/` nem nos testes dessas features. Se surgir necessidade,
  **parar** e demonstrar o bloqueio antes.
- **Feature 005**: só o previsto por 005 FR-056 (campo, passo 2a do esqueleto de escrita,
  `admite_escrita`), a extração sem mudança de comportamento de `_escala_da_pergunta` e
  três asserções de fronteira dos testes (research R16).

## Limites desta lista (não criar)

- Modelos ou entidades: Jornada/Journey, EstadoJornada/JourneyState, Passo/Step
  persistido, Transicao/Transition, Sessao/Session, Tentativa/Attempt,
  Submissao/Submission, Progresso/Progress, Percurso/Route persistido,
  RespostaAtiva/ActiveAnswer, Consentimento, Evento.
- Colunas `estado`, `concluida`, `submetida_em`, `secao_atual`, `posicao`, `progresso`,
  `atualizada_em`, `ativa`, `ramo`; momento por Seção ou por Resposta.
- Novo app Django; objeto de jornada com estado; máquina de estados; grafo persistido;
  cache de percurso; cursor; snapshot; event sourcing; histórico de ramos ou de conclusão.
- Motor genérico de regras, `RuleEngine`, prioridade configurável, atributo de momento de
  aplicação, condição de exibição, ValidatorRegistry, framework ou Strategy/visitor de
  validação.
- Operação de reabrir, desfazer conclusão, editar após concluir; prazo de graça;
  expiração ou limpeza automática de rascunhos; restrição das escritas ao percurso.
- Progresso, percentual, ViewModel, HTML, admin, URLs, API, comando de gestão.
- Detecção de ciclo; precedência entre duas Perguntas com regra na mesma Seção.
- Publicação ou alteração da baseline; transformar `PERCURSOS` em lógica de produção.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar a base. Nenhum app novo.

- [X] T001 Confirmar a base do branch: `git log --oneline main -1` está contido no branch
  (005 incorporada); rodar `uv run pytest`, `uv run ruff check .` e
  `uv run python manage.py makemigrations --check --dry-run` e registrar que estão verdes
  e limpos antes de qualquer mudança. Nada é criado.

**Checkpoint**: suíte 001–005 verde.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o campo `concluida_em`, os motivos novos, os ajustes de fronteira da 005 e os
auxiliares de teste usados por todas as histórias.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T002 [P] Escrever `tests/participacao/test_jornada_modelo.py` (test-first; DEVE
  falhar antes de T003):
  - `Participacao._meta.get_field("concluida_em")` é `DateTimeField` com `null=True`, sem
    `default` (`has_default()` falso), sem `auto_now`/`auto_now_add`;
  - `iniciar_participacao(campanha, conclusao, agora=NO_PERIODO)` cria Participação com
    `concluida_em is None`;
  - a migração `trajetoria/participacao/migrations/0002_participacao_concluida_em.py`
    (carregada por `django.db.migrations.loader.MigrationLoader`) depende de
    `("participacao", "0001_initial")` e tem **exatamente uma** operação, `AddField(
    model_name="participacao", name="concluida_em")`, sem `RunPython`/`RunSQL`.
- [X] T003 Em `trajetoria/participacao/models.py`, acrescentar a `Participacao`
  `concluida_em = models.DateTimeField(null=True)` com comentário "Momento de referência
  da conclusão aceita; `NULL` = em rascunho (006 FR-001). Gravado só por `concluir`."
  Atualizar a docstring da classe ("Sem estado: … em preenchimento (FR-055)") para
  "rascunho ou concluída, derivado de `concluida_em`; sem enum (006 FR-002)". Gerar
  `uv run python manage.py makemigrations participacao --name participacao_concluida_em`
  e conferir que o arquivo contém só o `AddField` (sem backfill). T002 passa.
- [X] T004 [P] Em `trajetoria/participacao/regras.py`, acrescentar a `Motivo`, com
  comentário de requisito: `PARTICIPACAO_CONCLUIDA = "participacao_concluida"` (006
  FR-038), `ESTRUTURA_NAO_SUPORTADA = "estrutura_nao_suportada"` (006 FR-016),
  `OBRIGATORIA_PENDENTE = "obrigatoria_pendente"` (006 FR-019, FR-037). Atualizar a
  docstring do módulo citando a 006.
- [X] T005 Ajustar só as asserções de fronteira da 005 que reservavam a conclusão à 006
  (research R16), sem enfraquecer outros invariantes:
  - `tests/participacao/test_participacao_aceitacao.py::test_10_nenhuma_jornada_ou_conclusao_antecipada`:
    retirar `"concluir"` e `"concluida"` de `proibidas` e `"concluida_em"` da tupla de
    atributos; manter `"submet"`, `"progresso"`, `"proxima"`, `"obrigat"`, `"naveg"`,
    `"estado"`, `"submetida_em"`; renomear para
    `test_10_nenhum_progresso_submissao_ou_estado` e citar 005 FR-056 / 006 R16 no
    comentário;
  - `tests/participacao/test_participacao_aceitacao.py::test_campos_dos_modelos_novos`:
    `Participacao` = `["id", "campanha", "conclusao", "iniciada_em", "concluida_em"]`;
    `Resposta` e `RespostaOpcao` inalterados;
  - `tests/participacao/test_participacao_rascunho.py::test_participacao_parcial_ou_completa_nao_e_conclusao`:
    o conjunto de campos inclui `"concluida_em"`, e o teste passa a afirmar que, depois
    de zero, algumas e todas as escritas, `Participacao.objects.get(pk=…).concluida_em is
    None` (escrever respostas nunca conclui).
- [X] T006 Acrescentar auxiliares (não testes) a `tests/participacao/construcao.py`.
  Imports de `trajetoria.participacao.percurso`, `consultas` e `operacoes` ficam
  **dentro das funções** que os usam:
  - **Versões em memória** (para testes sem banco), construindo diretamente os
    `dataclass` de `trajetoria.instrumento.conteudo` com `uuid4()`:
    `pergunta_mem(*, obrigatoria=True, tipo=TipoPergunta.ESCOLHA_UNICA, opcoes=("Sim",
    "Não"), regras=None)`, onde `regras` mapeia texto da Opção → índice (1-based) da
    Seção de destino ou `"FIM"`; `secao_mem(*perguntas, encaminhamento=None)`, com
    `encaminhamento` = índice da Seção; `versao_mem(*secoes) -> ConteudoVersao`, que
    resolve índices em `id` e numera posições; `opcao_id(conteudo, s, p, texto)` para
    obter o `id` de uma Opção por posição;
  - `respondidas(conteudo, escolhas: dict[tuple[int, int], str | None])` → `dict[UUID,
    UUID | None]` (`(seção, pergunta)` → texto da Opção ou `None`);
  - `rotulos(passagens)` → tupla de `secao.titulo or f"#{secao.posicao}"`, acrescida de
    `"FIM"` se `percurso.finalizada(passagens)` — mesmo formato de `PERCURSOS`;
  - **Versão publicada a partir da mesma descrição** (para testes de banco):
    `versao_publicada_de(*secoes_mem)` monta pelas operações da 002 (`criar_pesquisa`,
    `criar_versao`, `adicionar_secao`, `adicionar_pergunta`, `adicionar_opcao`,
    `definir_regra`, `definir_encaminhamento`, `publicar`) e devolve a `Versao`;
  - **Baseline**: `Baseline` (`dataclass` com `versao`, `q(n) -> Pergunta`, `s(n) ->
    Secao`, `opcao(n, texto) -> Opcao`, numeração Qn/Sn pela ordem (Seção, posição), como
    `perguntas_por_chave` da 003); `baseline_publicada() -> Baseline`:
    `materializar()` → `criar_versao_a_partir_de(versao, "Cópia de teste 006")` →
    `publicar(cópia)`; a baseline continua RASCUNHO;
  - `secoes_esperadas(q1, q14=None, q33=None, q46=None) -> list[int]`: oráculo de teste
    escrito à mão a partir da tabela "Percursos esperados" da 003 (Q1 "Não" → `[1]`;
    senão `[1, 2, 3, 4 + índice de Q14, 8, 9 ou 10, 11, (12), 13]`);
  - `escolhas_baseline(q1, q14=None, q33=None, q46=None) -> dict[str, str]`: textos das
    Opções de Q1, Q14, Q33 e Q46;
  - `respondidas_baseline(conteudo, escolhas, *, todas=True)`: respondidas em memória
    para **todas** as Perguntas da Versão (escolha única → Opção escolhida para Q1, Q14,
    Q33, Q46, senão a primeira; demais tipos → `None`), para provar que respostas fora do
    percurso não interferem;
  - `preencher(participacao, base, secoes, escolhas, *, agora=NO_PERIODO, exceto=())`:
    responde, pelas operações da 005, as Perguntas **obrigatórias** das Seções `secoes`
    (escolha única → Opção escolhida ou a primeira; múltipla → `{primeira}`; texto →
    `"resposta fictícia"`; escala → `escala_inicio`), pulando as chaves em `exceto`.

**Checkpoint**: `uv run pytest tests/participacao` verde (inclui T002 e T005);
`makemigrations --check` limpo.

---

## Phase 3: User Story 1 — Reconstruir o percurso atual de uma Participação (Priority: P1) 🎯 MVP

**Goal**: dado o conteúdo da Versão e as respostas atuais, derivar as passagens, a Seção
atual e a finalização; e expor isso na consulta da jornada, sem gravar nada.

**Independent Test**: Versões lineares em memória e publicadas; Participação sem
respostas, parcial e completa; consultas repetidas iguais e sem escrita.

### Tests for User Story 1 ⚠️

- [X] T007 [P] [US1] Criar `tests/participacao/test_jornada_percurso.py` (**sem**
  `django_db`), com Versões de `versao_mem`:
  - **pureza**: `trajetoria.participacao.percurso` não tem nos seus globais `models`,
    `connection`, `transaction`, `conteudo_da_versao`, `respostas_atuais`, nem módulos
    `django.db*` (inspecionar `vars(percurso)` e `sys.modules[...]` importados pelo
    módulo via `ast` do arquivo-fonte: nenhum `import`/`from` de `django.db`,
    `trajetoria.*.models`, `trajetoria.instrumento.conteudo.conteudo_da_versao` ou
    `trajetoria.participacao.consultas`/`operacoes`);
  - **linear** (3 Seções, sem regras nem encaminhamento, todas obrigatórias respondidas)
    → 3 passagens na ordem, `destino` das duas primeiras = `id` da seguinte, última
    `FINALIZACAO`, `finalizada` verdadeiro;
  - **sem respostas** → 1 passagem (S1), `pendentes` = obrigatórias de S1 na ordem,
    `finalizada` falso; Seções futuras ausentes;
  - **parcial** (S1 completa, S2 com uma obrigatória vazia) → passagens S1, S2; S2 é a
    atual; S3 ausente;
  - respostas a Perguntas de S3 presentes em `respondidas` não alteram o resultado
    parcial;
  - **determinismo**: dois `respondidas` iguais construídos em ordens diferentes → tuplas
    `==`; duas chamadas seguidas → `==`;
  - `perguntas_do_percurso(passagens)` = `id` de todas as Perguntas das Seções das
    passagens.
- [X] T008 [P] [US1] Criar `tests/participacao/test_jornada_situacao.py`
  (`django_db`), com uma Versão linear de `versao_publicada_de` aplicada a
  `campanha_aberta` e `iniciar_participacao`:
  - Participação sem respostas: `passagens` com só S1, `secao_atual` = S1,
    `finalizada` falso, `respostas == {}`, `fora_do_percurso == frozenset()`,
    `concluida_em is None`, `admite_escrita` verdadeiro em `NO_PERIODO`;
  - depois de responder S1: `secao_atual` = S2; `respostas` contém as de S1;
  - todas respondidas: `finalizada`, `secao_atual is None`;
  - `retrato(participacao)` idêntico antes e depois de `situacao_da_jornada` (nada
    gravado); duas consultas seguidas produzem `passagens` iguais;
  - `situacao_da_jornada` com instância desatualizada usa a Participação relida do banco.

### Implementation for User Story 1

- [X] T009 [US1] Criar `trajetoria/participacao/percurso.py` conforme
  [contracts/percurso.md](contracts/percurso.md), **puro**:
  - `class Saida(Enum)`: `FINALIZACAO = "finalizacao"`, `INDETERMINADA =
    "indeterminada"`;
  - `@dataclass(frozen=True) class Passagem`: `secao: ConteudoSecao`, `pendentes:
    tuple[UUID, ...]`, `destino: UUID | Saida`; propriedade `satisfeita` (`not
    pendentes`);
  - `percorrer(conteudo, respondidas) -> tuple[Passagem, ...]`: começa em
    `conteudo.secoes[0]`; `pendentes` = Perguntas `obrigatoria` sem chave em
    `respondidas`, na ordem; nesta história o destino é só (4) Seção seguinte ou (5)
    `FINALIZACAO`; para em pendentes ou `FINALIZACAO`;
  - `finalizada(passagens) -> bool`; `perguntas_do_percurso(passagens) ->
    frozenset[UUID]`.
  Docstring do módulo com a seção "Pureza" do contrato.
- [X] T010 [US1] Em `trajetoria/participacao/consultas.py`, acrescentar
  `SituacaoDaJornada` (`@dataclass(frozen=True)` com `participacao`, `concluida_em`,
  `passagens`, `finalizada`, `secao_atual: ConteudoSecao | None`, `respostas: dict[UUID,
  Resposta]`, `fora_do_percurso: frozenset[UUID]`, `impedimentos: tuple[Violacao, ...]`,
  `admite_escrita: bool` e propriedade `pode_concluir` = `concluida_em is None and not
  impedimentos`) e `situacao_da_jornada(participacao, *, agora=None)`
  ([contracts/consultas.md](contracts/consultas.md)):
  - relê a Participação (`select_related("campanha")`); carrega `conteudo_da_versao(
    participacao.campanha.versao)` e `respostas_atuais(participacao)` uma vez; monta
    `respondidas`; chama `percorrer`;
  - `fora_do_percurso` = chaves de `respostas` fora de `perguntas_do_percurso`;
  - se `concluida_em` preenchido: `admite_escrita=False`, `impedimentos=()`, **sem
    chamar `estado`**; senão: `admite_escrita` = `estado(…, agora=agora) is EM_COLETA`
    e `impedimentos` = `(COLETA_NAO_ADMITIDA,)` quando não está em coleta (pendências
    entram em US3);
  - acrescentar `"SituacaoDaJornada"` e `"situacao_da_jornada"` a `__all__`; atualizar a
    docstring do módulo (a 005 dizia "nada aqui calcula … próxima Pergunta"): a consulta
    da jornada deriva o percurso sem gravar nem montar tela.

**Checkpoint**: T007 e T008 verdes; nada gravado por consultas.

---

## Phase 4: User Story 2 — Avançar entre Seções conforme ordem e navegação (Priority: P1)

**Goal**: destino de cada Seção pela precedência regra → encaminhamento → ordem →
finalização, com destino indeterminado quando a Pergunta com regra obrigatória está sem
resposta.

**Independent Test**: Versões em memória com regras e encaminhamentos; tabela de
precedência exercitada caso a caso.

### Tests for User Story 2 ⚠️

- [X] T011 [US2] Acrescentar a `tests/participacao/test_jornada_percurso.py` (sem banco),
  um teste por linha da precedência (FR-012):
  - (1) regra "ir para S4" em S1 com encaminhamento S2 e Seção seguinte S2 → destino S4;
    S2 e S3 ausentes das passagens;
  - (1) regra `FIM` acionada → destino `FINALIZACAO`, `finalizada` verdadeiro mesmo com
    Seções restantes;
  - (2) Pergunta com regra **obrigatória** sem resposta → destino `INDETERMINADA`; o
    percurso para nela; nenhuma Seção futura aparece;
  - (3) Opção respondida **sem** regra numa Pergunta com regra → encaminhamento da Seção;
  - (3) Pergunta com regra **opcional** sem resposta → encaminhamento; sem
    encaminhamento → (4) Seção seguinte (002 FR-054);
  - (3) encaminhamento prevalece sobre a ordem (S1 → S3 pulando S2);
  - convergência: duas Seções alternativas com encaminhamento para a mesma Seção;
  - (5) última Seção satisfeita → `FINALIZACAO`;
  - Seção com Pergunta com regra respondida e outra obrigatória pendente → destino já
    determinado (id da Seção da regra), mas o percurso para nela;
  - Opção em `respondidas` que não pertence à Pergunta com regra → `ParticipacaoRejeitada`
    com `OPCAO_DE_OUTRA_PERGUNTA`, `campo="pergunta"`;
  - nenhuma precedência além dessas: com regra acionada, o encaminhamento é ignorado; sem
    regra acionada, a regra de outra Seção não influencia.

### Implementation for User Story 2

- [X] T012 [US2] Em `trajetoria/participacao/percurso.py`, implementar a função privada
  `_destino(conteudo, indice, secao, respondidas)` com a precedência (1)–(5) do
  [contrato](contracts/percurso.md) (seção 3)
  (Pergunta com regra = Pergunta com alguma `ConteudoOpcao.regra`; a primeira encontrada
  enquanto US12 não acrescentar a verificação de suporte); parar também em
  `INDETERMINADA`; Opção desconhecida → `OPCAO_DE_OUTRA_PERGUNTA` com o `id` da Pergunta
  no detalhe. Sem detecção de ciclo (FR-015).

**Checkpoint**: T007 e T011 verdes.

---

## Phase 5: User Story 3 — Validar obrigatoriedade da Seção atual (Priority: P1)

**Goal**: pendências como violações da Seção atual; opcionais e Seções fora do percurso
nunca exigidas.

**Independent Test**: Seções com obrigatórias e opcionais; troca de ramo; pendências só
no ponto alcançado.

### Tests for User Story 3 ⚠️

- [X] T013 [US3] Testes de obrigatoriedade:
  - em `tests/participacao/test_jornada_percurso.py` (sem banco): `pendencias(passagens)`
    → uma `Violacao(OBRIGATORIA_PENDENTE, "pergunta", …)` por Pergunta de
    `passagens[-1].pendentes`, na ordem, com `id` da Pergunta e da Seção no detalhe;
    vazio se `finalizada`; Perguntas opcionais nunca aparecem; obrigatórias de Seção
    pulada por regra nunca aparecem, mesmo sem resposta; nunca há pendência de Seção
    anterior; Seção só com obrigatória de escolha múltipla respondida (`None` em
    `respondidas`) está satisfeita;
  - em `tests/participacao/test_jornada_situacao.py` (banco): `impedimentos` de rascunho
    em coleta = pendências da Seção atual; com Campanha encerrada = `COLETA_NAO_ADMITIDA`
    + pendências; `pode_concluir` só com `impedimentos` vazio e `finalizada`.

### Implementation for User Story 3

- [X] T014 [US3] Em `trajetoria/participacao/percurso.py`, implementar
  `pendencias(passagens) -> tuple[Violacao, ...]`; em `trajetoria/participacao/consultas.py`,
  incluir `pendencias(passagens)` em `impedimentos` (depois de `COLETA_NAO_ADMITIDA`)
  para Participação em rascunho.

**Checkpoint**: US1–US3 verdes; o percurso puro está completo, exceto a verificação de
suporte (US12).

---

## Phase 6: User Story 4 — Resolver os ramos de Q1, Q14, Q33 e Q46 (Priority: P1)

**Goal**: provar, na estrutura real da baseline, todos os destinos e os 17 percursos da
003.

**Independent Test**: oráculo `PERCURSOS` da 003; cópia publicada da baseline.

### Tests for User Story 4 ⚠️

- [X] T015 [US4] Criar `tests/participacao/test_jornada_baseline.py`, importando
  `baseline` (fixture) e `PERCURSOS` de `tests/instrumento/formulario_2024_esperado.py`
  (com `# ruff: noqa: F401, F811`, como em `test_formulario_2024_navegacao.py`):
  - **puros** (fixture `baseline`, `respondidas_baseline` com **todas** as Perguntas
    respondidas): para cada uma das 17 combinações de Q1 × Q14 × Q33 × Q46,
    `rotulos(percorrer(...))` ∈ `PERCURSOS`; o conjunto obtido == `set(PERCURSOS)` e tem
    17 elementos (um único teste parametrizado ou um laço; nenhuma lógica por percurso);
  - Q1 "Sim" → segunda passagem é S2; Q1 "Não" → passagens só S1, `FINALIZACAO`;
  - Q14: cada uma das 4 Opções → S4, S5, S6, S7, seguida de S8;
  - Q33 "Sim"/"Não" → S9/S10, seguida de S11;
  - Q46 "Sim" → S12, S13, `FIM`; "Não" → S13, `FIM`;
  - **regressão Q51**: nenhuma `ConteudoOpcao` de Q51 tem `regra`; com cada Opção de Q51,
    o destino de S12 é S13 = `encaminhamento_id` de S12;
  - **ponta a ponta** (`django_db`, `baseline_publicada`, `campanha_aberta` com a cópia,
    uma Conclusão por combinação): `preencher` as Seções de `secoes_esperadas`; para as
    17 combinações, `situacao_da_jornada` está `finalizada` e `rotulos(passagens)` ==
    percurso esperado;
  - **dado institucional não decide o percurso** (US1.6, FR-007): Conclusão com
    `nivel="Graduação"` e Q14 = "Pós-Graduação" → S7.

### Implementation for User Story 4

- [X] T016 [US4] Condicional: se T015 falhar, corrigir em `trajetoria/participacao/percurso.py`
  pela precedência do contrato, sem regra especial por Pergunta, sem usar `PERCURSOS` em
  produção. Se a falha estiver na baseline ou na 002, **parar** e demonstrar.

**Checkpoint**: 17 percursos verdes, puros e de ponta a ponta.

---

## Phase 7: User Story 5 — Preservar Q47/Q48 antes do desvio de Q46 (Priority: P1)

**Goal**: Q46, Q47 e Q48 juntas em S11; a resposta a Q46 só decide a saída.

**Independent Test**: S11 com Q46 "Sim" e "Não", Q47 vazia ou respondida, Q48 vazia.

### Tests for User Story 5 ⚠️

- [X] T017 [US5] Acrescentar a `tests/participacao/test_jornada_baseline.py` (puros e um
  de ponta a ponta), demonstrando explicitamente:
  - Q46, Q47 e Q48 pertencem à passagem de S11, nas posições 1, 2, 3, e estão em
    `perguntas_do_percurso` com Q46 "Sim" e com "Não";
  - Q47 é obrigatória e Q48 opcional na Versão (`ConteudoPergunta.obrigatoria`);
  - Q46 respondida e Q47 vazia → a passagem de S11 é a última (não encerra a Seção
    imediatamente), `pendentes == (Q47,)`, e o destino já é S12 ("Sim") ou S13 ("Não");
    S12/S13 **não** aparecem nas passagens;
  - Q46 "Não", Q47 respondida, Q48 vazia → S11 satisfeita; a passagem seguinte é S13;
  - Q48 nunca aparece em `pendencias`;
  - só depois de S11 satisfeita a resposta a Q46 determina a passagem seguinte;
  - Q46 "Sim" com Q47 = {"Não estudei mais"} → nenhuma rejeição ou pendência extra.

### Implementation for User Story 5

- [X] T018 [US5] Condicional: se T017 falhar, corrigir em `trajetoria/participacao/percurso.py`
  mantendo a Seção como unidade (FR-010, FR-011); nenhum atributo de momento de
  aplicação.

**Checkpoint**: semântica de S11 protegida.

---

## Phase 8: User Story 6 — Concluir Participação válida (Priority: P1)

**Goal**: `concluir` grava `concluida_em`, remove Respostas fora do percurso final e
preserva as do percurso; rejeita jornada não finalizada sem alterar nada.

**Independent Test**: Versão publicada com um ramo; concluir válida, incompleta e com
respostas fora do percurso.

### Tests for User Story 6 ⚠️

- [X] T019 [US6] Criar `tests/participacao/test_jornada_conclusao.py` (`django_db`), com
  uma Versão de `versao_publicada_de` (S1: escolha única obrigatória "Sim"→S2 /
  "Não"→S3; S2: texto obrigatório + escolha múltipla com "Outro:" obrigatória + escala
  opcional; S3: texto obrigatório):
  - **válida**: percurso S1 "Sim", S2 → `concluir(p, agora=NO_PERIODO)` devolve
    `ResultadoConclusao(participacao, CONCLUIDA)`; `concluida_em == NO_PERIODO`;
    `iniciada_em`, `campanha`, `conclusao` inalterados; as Respostas do percurso idênticas
    (linhas de `retrato` antes/depois, sem as removidas);
  - **remove fora do percurso**: com S3 respondida antes de trocar S1 para "Sim", a
    conclusão remove a Resposta de S3 e mantém as de S1 e S2;
  - **pendência**: S2 com a obrigatória de texto vazia → `ParticipacaoRejeitada` com
    `OBRIGATORIA_PENDENTE` exatamente para essa Pergunta; `retrato` idêntico;
    `concluida_em is None`; a Resposta de S3 (fora do percurso) **continua** gravada;
  - **todas as violações reunidas**: Campanha encerrada (`encerrar(campanha,
    agora=…)`) + pendência → motivos `(COLETA_NAO_ADMITIDA, OBRIGATORIA_PENDENTE)`;
  - **obrigatória fora do percurso não bloqueia**: com S1 "Sim", S3 vazia, conclusão
    aceita;
  - **"Outro:" sem complemento** em obrigatória de escolha múltipla → conclusão aceita
    (FR-028);
  - escala opcional vazia → aceita;
  - `concluir("x")` → `TypeError`; Participação não gravada → `PARTICIPACAO_INEXISTENTE`;
  - nenhuma linha de `Campanha`, `ConclusaoAcademica`, `Versao`, `Secao`, `Pergunta` ou
    `Opcao` muda (comparar `values()` antes/depois).

### Implementation for User Story 6

- [X] T020 [US6] Em `trajetoria/participacao/operacoes.py`, acrescentar `class
  SituacaoConclusao(Enum)` (`CONCLUIDA = "concluida"`, `JA_CONCLUIDA = "ja_concluida"`),
  `class ResultadoConclusao(NamedTuple)` (`participacao`, `situacao`) e `concluir(
  participacao, *, agora=None)` com os passos do
  [contrato](contracts/conclusao.md#passos) **exceto** o 3 (US7) e o 9 (US12):
  `_exigir`; validar `agora` antes do banco; `transaction.atomic()`; `_bloquear`; relógio
  depois do bloqueio; violações acumuladas (`COLETA_NAO_ADMITIDA` por `estado`); carregar
  `conteudo_da_versao(participacao.campanha.versao)` e `respostas_atuais(participacao)`;
  `percorrer(conteudo, respondidas)`; `pendencias`; com violações →
  `ParticipacaoRejeitada(todas)`; senão `Resposta.objects.filter(participacao=p).exclude(
  pergunta_id__in=perguntas_do_percurso(passagens)).delete()` e
  `p.concluida_em = agora; p.save(update_fields=["concluida_em"])`. Se `percorrer`
  rejeitar, relançar com a violação de coleta (se houver) **e** as dele. Acrescentar os
  três nomes a `__all__` e atualizar a docstring do módulo (único caminho de escrita,
  agora com a conclusão).

**Checkpoint**: T019 verde; conclusão rejeitada não altera nada.

---

## Phase 9: User Story 7 — Bloquear edição após conclusão (Priority: P1)

**Goal**: Participação concluída imutável; conclusão repetida idempotente; concorrência
segura.

**Independent Test**: escritas e conclusão repetida depois de concluir, com a Campanha em
coleta e encerrada; duas conclusões simultâneas.

### Tests for User Story 7 ⚠️

- [X] T021 [P] [US7] Criar `tests/participacao/test_jornada_imutabilidade.py`
  (`django_db`), com uma Participação concluída em `NO_PERIODO`:
  - `responder_escolha_unica`, `responder_escolha_multipla`, `responder_texto`,
    `responder_escala` e `remover_resposta` → `PARTICIPACAO_CONCLUIDA` (e só ele) com a
    Campanha **EM_COLETA**; idem com `agora=DEPOIS_DO_FIM` (o motivo é a conclusão, não a
    coleta); `retrato` idêntico após cada tentativa;
  - `concluir` de novo → `JA_CONCLUIDA`, `concluida_em` igual ao original, `retrato`
    idêntico; idem com a Campanha encerrada;
  - na conclusão repetida, `estado`, `conteudo_da_versao` e `respostas_atuais` **não**
    são chamados (monkeypatch em `trajetoria.participacao.operacoes` que lança
    `AssertionError`) — a conclusão histórica não é revalidada;
  - `iniciar_participacao` do mesmo par → `JA_EXISTENTE`, mesma Participação, concluída;
  - `admite_escrita(p, agora=NO_PERIODO)` falso; `situacao_da_jornada(p,
    agora=NO_PERIODO).admite_escrita` e `.pode_concluir` falsos, `finalizada` verdadeiro,
    `fora_do_percurso` vazio;
  - nenhum nome em `operacoes.__all__` contém `reabr`, `desfaz`, `reverter` ou `editar`.
- [X] T022 [P] [US7] Criar `tests/participacao/test_jornada_concorrencia.py`:
  - determinístico: duas chamadas a `concluir` em sequência → `CONCLUIDA` e
    `JA_CONCLUIDA`; contar remoções com `monkeypatch` sobre o `QuerySet.delete` de
    `Resposta` (ou contar linhas) e provar que a segunda não remove nada;
  - escrita depois da conclusão → `PARTICIPACAO_CONCLUIDA`; escrita antes → considerada
    pela conclusão (a Resposta gravada aparece no percurso final);
  - **bloqueio verificado de forma determinística** (proteção principal de FR-043, que
    não depende do teste com threads): com `django.test.utils.CaptureQueriesContext`, a
    primeira consulta de `concluir` sobre `participacao_participacao` contém `FOR UPDATE`
    e ocorre **antes** de qualquer consulta a `participacao_resposta`; idem na conclusão
    repetida (o bloqueio precede o retorno `JA_CONCLUIDA`);
  - opcional (como 005 R17), `@pytest.mark.django_db(transaction=True)`: duas threads com
    `threading.Barrier(2)` chamam `concluir` → situações `["concluida", "ja_concluida"]`,
    um único `concluida_em`; `connection.close()` em cada thread; manter só se estável.

### Implementation for User Story 7

- [X] T023 [US7] Em `trajetoria/participacao/operacoes.py`:
  - em `_escrever`, logo após `_bloquear` e **antes** do relógio e da coleta: se
    `participacao.concluida_em is not None` → `_rejeitar(Motivo.PARTICIPACAO_CONCLUIDA,
    "participacao", "a Participação está concluída")` (passo 2a);
  - em `concluir`, logo após `_bloquear`: se `concluida_em` preenchido, devolver
    `ResultadoConclusao(participacao, SituacaoConclusao.JA_CONCLUIDA)` sem ler relógio,
    Campanha, Versão ou Respostas (passo 3).

  Em `trajetoria/participacao/consultas.py`, `admite_escrita`: relê `concluida_em` do
  banco (`Participacao.objects.filter(pk=…).values_list("concluida_em", flat=True)`);
  preenchido → `False` **sem** chamar `estado`; senão a regra da 005. Atualizar a
  docstring do esqueleto em `operacoes.py` (passos 2a e 3).

**Checkpoint**: T021 e T022 verdes; suíte da 005 verde.

---

## Phase 10: User Story 8 — Retomar Participação em rascunho (Priority: P2)

**Goal**: retomada reconstrói a mesma jornada a partir das respostas, sem sessão.

**Independent Test**: preencher parcialmente, "sair", localizar/iniciar de novo e
consultar.

### Tests for User Story 8 ⚠️

- [X] T024 [US8] Acrescentar a `tests/participacao/test_jornada_situacao.py`, com a cópia
  da baseline: preencher S1–S8 com Q33 "Sim" e parte de S9; depois
  `iniciar_participacao` (→ `JA_EXISTENTE`) e `situacao_da_jornada` com a instância
  devolvida e com `Participacao.objects.get(pk=…)`: `secao_atual` = S9, pendentes = as
  obrigatórias vazias de S9, `passagens[:-1]` = S1–S8 com as respostas dadas; as duas
  consultas produzem `passagens`, `fora_do_percurso` e `impedimentos` iguais; `retrato`
  idêntico (nenhuma sessão, posição ou momento gravado); `percurso`/consultas não
  expõem nada chamado `cursor`, `sessao`, `tentativa` ou `progresso`.

### Implementation for User Story 8

- [X] T025 [US8] Condicional: se T024 falhar, corrigir em
  `trajetoria/participacao/consultas.py` (carregamento) ou `percurso.py` (derivação), sem
  persistir nada.

**Checkpoint**: retomada derivada.

---

## Phase 11: User Story 9 — Remover respostas que ficaram fora do percurso após mudança de ramo (Priority: P2)

**Goal**: respostas de ramos abandonados ficam inativas no rascunho, podem voltar a valer
e são removidas só na conclusão aceita.

**Independent Test**: trocas de Q33 e Q14 na cópia da baseline, com e sem conclusão.

### Tests for User Story 9 ⚠️

- [X] T026 [US9] Com a cópia da baseline:
  - em `tests/participacao/test_jornada_situacao.py`: S9 respondida com Q33 "Sim"; trocar
    Q33 para "Não" → Q34–Q44 continuam em `respostas_atuais` (persistidas e
    recuperáveis), estão em `fora_do_percurso`, S9 não está nas passagens, nenhuma delas
    aparece em `impedimentos`, e a passagem de S10 tem `pendentes == (Q45,)` (não
    satisfeita por respostas de S9); trocar de volta para "Sim" → `fora_do_percurso`
    vazio e S9 satisfeita **sem** nova escrita em Q34–Q44; nenhuma coluna/flag
    `ativa` em `Resposta`;
  - em `tests/participacao/test_jornada_conclusao.py`: Q33 "Sim"→"Não", S10 e seguintes
    preenchidas, `concluir` → Respostas de Q34–Q44 não existem; as do percurso final
    idênticas; Q14 "Graduação"→"Pós-Graduação" → Q18 removida, Q19 preservada; Resposta
    de escolha múltipla fora do percurso removida junto com suas `RespostaOpcao`
    (contar linhas de `RespostaOpcao` da Resposta); conclusão **rejeitada** por pendência
    → nenhuma Resposta fora do percurso removida.

### Implementation for User Story 9

- [X] T027 [US9] Condicional: se T026 falhar, corrigir em `trajetoria/participacao/operacoes.py`
  (o `delete` por `exclude(pergunta_id__in=…)`) ou em `consultas.py`
  (`fora_do_percurso`), sem histórico nem flag.

**Checkpoint**: ramos abandonados nunca contaminam a concluída.

---

## Phase 12: User Story 10 — Finalizar corretamente por Q1 = Não (Priority: P2)

**Goal**: Q1 "Não" finaliza; conclusão só com o percurso reduzido; nada de
consentimento.

**Independent Test**: cenário completo na cópia da baseline.

### Tests for User Story 10 ⚠️

- [X] T028 [US10] Acrescentar a `tests/participacao/test_jornada_conclusao.py`, com a
  cópia da baseline, o cenário completo em sequência:
  1. Q1 "Sim" e respostas a Perguntas posteriores (S2 inteira; Q26, escolha múltipla com
     `RespostaOpcao`) existem no rascunho;
  2. Q1 passa para "Não";
  3. `situacao_da_jornada`: passagens só S1, `finalizada`, todas as outras em
     `fora_do_percurso`;
  4. `impedimentos` vazio (nenhuma pendência);
  5. `concluir` → `CONCLUIDA`;
  6. as Respostas fora do percurso e as `RespostaOpcao` de Q26 foram removidas na mesma
     operação;
  7. resta exatamente uma Resposta, a de Q1, com a Opção "Não".

  Além disso: Q1 "Não" sem outras respostas conclui com uma Resposta; nenhum modelo,
  campo ou registro de consentimento, recusa ou opt-out existe
  (`apps.get_app_config("participacao").get_models()` inalterado); a mesma Conclusão
  ainda pode iniciar Participação em outra Campanha aberta.

### Implementation for User Story 10

- [X] T029 [US10] Condicional: se T028 falhar, corrigir em `percurso.py` ou
  `operacoes.py` sem regra especial para Q1 (a finalização vem de `regra.finaliza`).

**Checkpoint**: recusa finaliza, sem efeito jurídico.

---

## Phase 13: User Story 11 — Impedir conclusão após encerramento da Campanha (Priority: P2)

**Goal**: rascunho não conclui depois da coleta; leitura (de rascunho e de concluída)
nunca depende do estado da Campanha.

**Independent Test**: encerramento explícito e por data; consulta anos depois.

### Tests for User Story 11 ⚠️

- [X] T030 [US11] Testes de encerramento e leitura histórica:
  - em `tests/participacao/test_jornada_conclusao.py`: jornada finalizada; `encerrar` a
    Campanha → `concluir` rejeita com `COLETA_NAO_ADMITIDA`, `retrato` idêntico
    (inclusive respostas fora do percurso); Campanha com fim em 30/06/2027:
    `concluir(agora=ULTIMO_DIA)` aceita; noutra Participação, `concluir(agora=
    DEPOIS_DO_FIM)` rejeita;
  - em `tests/participacao/test_jornada_situacao.py` — **rascunho de Campanha
    encerrada**: `situacao_da_jornada(agora=DEPOIS_DO_FIM)` funciona, `passagens`
    iguais às de antes do encerramento, `admite_escrita` falso, `impedimentos` contém
    `COLETA_NAO_ADMITIDA`; o rascunho não é apagado nem alterado;
  - **leitura histórica** (A–F): (A) concluir em `NO_PERIODO` (2027); (B) consultar com
    `agora=momento(2030, 1, 1)`, depois do encerramento; (C) `situacao_da_jornada`
    funciona; (D) `passagens` e `rotulos` iguais às da consulta de 2027; (E)
    `respostas_atuais` idênticas e `concluida_em == NO_PERIODO`; (F) `responder_texto`
    → `PARTICIPACAO_CONCLUIDA`;
  - para a concluída, `situacao_da_jornada` não chama `estado` (monkeypatch em
    `trajetoria.participacao.consultas.estado` que lança `AssertionError`) e
    `admite_escrita` também não.

### Implementation for User Story 11

- [X] T031 [US11] Condicional: se T030 falhar, corrigir em `trajetoria/participacao/consultas.py`
  para que nenhuma leitura dependa do estado da Campanha e que a concluída não o
  consulte; nenhuma mudança em `trajetoria/campanha/`.

**Checkpoint**: estado temporal é gate de escrita/conclusão, não de leitura.

---

## Phase 14: User Story 12 — Rejeitar estados inconsistentes (Priority: P3)

**Goal**: estrutura não suportada rejeitada explicitamente; Respostas incoerentes
detectadas na conclusão pelos validadores da 005.

**Independent Test**: Versão com duas Perguntas com regra na mesma Seção; Respostas
corrompidas por ORM.

### Tests for User Story 12 ⚠️

- [X] T032 [US12] Testes:
  - em `tests/participacao/test_jornada_percurso.py` (sem banco): Seção com duas Perguntas
    com regra → `ESTRUTURA_NAO_SUPORTADA`, uma violação por Seção (`campo="secao"`, `id`
    da Seção no detalhe), **mesmo que a Seção não seja alcançada** e sem nenhuma
    resposta; sem escolher primeira, última ou combinação (com respostas que levariam a
    destinos diferentes, o resultado é sempre a rejeição);
  - em `tests/participacao/test_jornada_conclusao.py` (banco; Versão publicada por
    `versao_publicada_de` com essa estrutura — a 002 permite publicá-la):
    `situacao_da_jornada` → `ESTRUTURA_NAO_SUPORTADA`; `concluir` → idem (com
    `COLETA_NAO_ADMITIDA` junto quando encerrada); `retrato` idêntico;
    `conteudo_da_versao` igual antes e depois (Versão intacta);
  - **Respostas incoerentes** gravadas por ORM (fora das operações), no percurso:
    escolha única com Opção de outra Pergunta → `OPCAO_DE_OUTRA_PERGUNTA`; escala fora
    dos limites (`Resposta.objects.filter(…).update(escala=9)`) →
    `ESCALA_FORA_DOS_LIMITES`; texto só com espaços → `VALOR_VAZIO`; cada uma com
    `campo="pergunta"` e o `id` da Pergunta no detalhe; nada removido; `concluida_em`
    nulo; várias incoerências → todas reunidas;
  - nenhuma mensagem (`str(erro)` e cada `detalhe`) contém o texto ou o inteiro
    declarados.
  - em `tests/participacao/test_participacao_respostas.py`: nenhuma alteração; os testes
    de escala da 005 continuam verdes após a extração (regressão de T034).

### Implementation for User Story 12

- [X] T033 [US12] Em `trajetoria/participacao/percurso.py`, no início de `percorrer`:
  verificar todas as Seções de `conteudo`; Seções com mais de uma Pergunta com regra →
  `ParticipacaoRejeitada` com uma `Violacao(ESTRUTURA_NAO_SUPORTADA, "secao", …)` por
  Seção. Em `_destino`, usar a única Pergunta com regra. Sem precedência entre regras.
- [X] T034 [US12] Em `trajetoria/participacao/operacoes.py`:
  - extrair de `responder_escala` a função `_escala_da_pergunta(pergunta, valor) -> int`
    (mesmas verificações e motivos: `VALOR_VAZIO`, `VALOR_INCOMPATIVEL` para não-`int` ou
    `bool`, `ESCALA_FORA_DOS_LIMITES`), usada por `responder_escala` sem mudar
    comportamento;
  - criar `_verificar_resposta_gravada(resposta, pergunta) -> None` que compõe os
    validadores existentes por tipo (`_opcao_da_pergunta` + `_complemento`;
    `_opcoes_da_pergunta(pergunta, list(resposta.opcoes.all()))` + `_complemento`;
    `_texto_declarado(resposta.texto, "texto")`; `_escala_da_pergunta`), sem regra nova;
  - em `concluir`, passo 9: para cada Resposta ativa (Pergunta em
    `perguntas_do_percurso`, relida com `select_related("secao")`), capturar
    `ParticipacaoRejeitada` e acumular `Violacao(v.motivo, "pergunta", f"Pergunta
    {pergunta.id}: {v.detalhe}")`; tudo antes de qualquer remoção.

**Checkpoint**: US1–US12 verdes; suíte da 005 verde.

---

## Phase 15: Aceitação ponta a ponta (cross-cutting, só testes)

**Purpose**: as 11 perguntas de sucesso e o escopo estrutural. Nenhuma funcionalidade.

- [X] T035 Criar `tests/participacao/test_jornada_aceitacao.py`:
  - as **11 perguntas de sucesso** do solicitante (spec, "Cobertura"), um teste cada,
    reaproveitando auxiliares;
  - escopo: `{m.__name__ for m in apps.get_app_config("participacao").get_models()} ==
    {"Participacao", "Resposta", "RespostaOpcao"}`; campos concretos de `Participacao` =
    `id, campanha, conclusao, iniciada_em, concluida_em`; `Resposta` e `RespostaOpcao`
    iguais à 005; campos de `Campanha`, `ConclusaoAcademica`, `Pergunta`, `Opcao`
    inalterados (mesmas listas de `test_participacao_aceitacao.py`); nenhum app novo em
    `INSTALLED_APPS`;
  - SC-010: Participação na Campanha da Versão "2027"; criar e publicar "2028" a partir
    dela com navegação diferente (`definir_regra` na nova) → `situacao_da_jornada` da
    Participação inalterada;
  - a baseline da 003 continua `RASCUNHO`.

---

## Phase 16: Polish & Cross-Cutting Concerns

**Purpose**: verificação e documentação. Nada de funcionalidade nova.

- [X] T036 [P] Atualizar `README.md` com "Jornada de resposta e conclusão:
  [quickstart da Feature 006](specs/006-jornada-conclusao-participacao/quickstart.md)" e
  conferir a tabela de arquivos de teste de
  `specs/006-jornada-conclusao-participacao/quickstart.md` contra os arquivos criados.
- [X] T037 Rodar e registrar:
  - `uv run pytest` (001–006 verdes);
  - `uv run ruff check .`;
  - `uv run python manage.py check`;
  - `uv run python manage.py makemigrations --check --dry-run`;
  - `git diff --stat main -- trajetoria/academico trajetoria/fonte_academica
    trajetoria/instrumento trajetoria/formulario_2024 trajetoria/campanha config
    tests/test_*.py tests/instrumento tests/campanha` vazio;
  - `git diff main -- trajetoria/participacao` limitado a `models.py`, `regras.py`,
    `percurso.py` (novo), `operacoes.py`, `consultas.py` e
    `migrations/0002_participacao_concluida_em.py`; nos testes da 005, só as três
    asserções de T005;
  - se o teste com threads de T022 falhar de forma intermitente, removê-lo e registrar.
- [X] T038 Conferir a Constituição e a Definition of Done e registrar em
  `specs/006-jornada-conclusao-participacao/plan.md` uma "Revisão pós-implementação":
  gate mantido; nada da lista "Limites" criado; `percurso.py` sem I/O; leitura histórica
  sem gate temporal; nenhum log nem valor declarado em mensagens; DP-601 a DP-604 e as
  herdadas abertas; Complexity Tracking vazio.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (T001)** → **Foundational (T002–T006)** → histórias → **Aceitação (T035)** →
  **Polish (T036–T038)**.
- Na Foundational: T002 e T004 em paralelo; T003 depois de T002; T005 depois de T003;
  T006 depois de T004.

### User Story Dependencies

- **US1** (T007–T010): Foundational.
- **US2** (T011–T012): US1 (`percorrer`).
- **US3** (T013–T014): US2.
- **US4** (T015–T016), **US5** (T017–T018): US3 (percurso completo); sequenciais por
  compartilharem `test_jornada_baseline.py`.
- **US6** (T019–T020): US3.
- **US7** (T021–T023): US6.
- **US8** (T024–T025): US3.
- **US9** (T026–T027): US6.
- **US10** (T028–T029): US6.
- **US11** (T030–T031): US7 (idempotência e leitura da concluída).
- **US12** (T032–T034): US6 (conclusão) e US2 (`_destino`).
- **Aceitação** (T035): US1–US12.

### Within Each User Story

- Testes primeiro; DEVEM falhar quando trazem comportamento novo.
- `percurso.py`, `operacoes.py`, `consultas.py`, `test_jornada_percurso.py`,
  `test_jornada_situacao.py`, `test_jornada_conclusao.py` e `test_jornada_baseline.py`
  são editados em sequência.

### Parallel Opportunities

- Foundational: T002 e T004.
- US1: T007 e T008 (arquivos distintos).
- US7: T021 e T022.
- Depois de US6: US8 (situação) pode correr em paralelo com US4/US5 (baseline), por
  arquivos distintos.
- Polish: T036 em paralelo com T037.

---

## Parallel Example: User Story 1

```bash
Task: "T007 Testes puros de percorrer em tests/participacao/test_jornada_percurso.py"
Task: "T008 Testes de situacao_da_jornada em tests/participacao/test_jornada_situacao.py"
```

## Parallel Example: User Story 7

```bash
Task: "T021 Imutabilidade em tests/participacao/test_jornada_imutabilidade.py"
Task: "T022 Concorrência em tests/participacao/test_jornada_concorrencia.py"
```

---

## Implementation Strategy

### MVP First

1. Setup + Foundational (T001–T006).
2. US1 → US7 (T007–T023): percurso, precedência, obrigatoriedade, baseline, Q46–Q48,
   conclusão e imutabilidade.
3. **STOP and VALIDATE**: `uv run pytest tests/participacao`.

### Incremental Delivery

4. US8 (retomada) → US9 (ramos) → US10 (Q1 = "Não") → US11 (encerramento e leitura
   histórica) → US12 (inconsistências).
5. Aceitação (T035) e Polish (T036–T038).

---

## Decisões Pendentes preservadas

Nenhuma task resolve DP-601 a DP-604 nem as herdadas (005/DP-501 a DP-508, 003/DP-302,
003/DP-303, 003/DP-304, 003/DP-307, 003/DP-309, 002/DP-001, 002/DP-006, 002/DP-007,
004/DP-404, 004/DP-406). Em particular:

- recusa (Q1 = "Não") é só o valor declarado; sem efeito fora da Participação (DP-601);
- complemento de "Outro:" não exigido (DP-602);
- concluída imutável, sem reabertura (DP-603);
- Seção como unidade; estrutura com duas Perguntas com regra rejeitada (DP-604);
- nenhuma conclusão fora de EM_COLETA (005/DP-502);
- rascunhos (inclusive respostas inativas) preservados, sem expiração (005/DP-503);
- Q1 não é consentimento; só dados fictícios (005/DP-504; 002/DP-007);
- nenhum ponto de entrada (005/DP-505);
- a baseline da 003 não é publicada (002/DP-001).

## Notes

- 38 tasks:
  - 16 escrevem testes: T002, T007, T008, T011, T013, T015, T017, T019, T021, T022,
    T024, T026, T028, T030, T032, T035;
  - 1 ajusta asserções de fronteira de testes da 005: T005;
  - 1 cria auxiliares de teste: T006;
  - 1 de base e 2 de verificação final: T001, T037, T038;
  - 17 de implementação ou documentação: T003, T004, T009, T010, T012, T014, T016,
    T018, T020, T023, T025, T027, T029, T031, T033, T034, T036. Seis delas são
    condicionais (T016, T018, T025, T027, T029, T031).
- Arquivos de produção: `models.py`, `regras.py`, `percurso.py` (novo), `operacoes.py`,
  `consultas.py`, `migrations/0002_participacao_concluida_em.py`.
- Desvio registrado na implementação: uma **quarta** asserção de fronteira da 005
  (`test_participacao_inicio.py::test_nao_existe_reinicio_nem_tentativa`) precisou do
  mesmo ajuste de T005 (research R16; plan, "Revisão pós-implementação").
- Commit após cada checkpoint.
