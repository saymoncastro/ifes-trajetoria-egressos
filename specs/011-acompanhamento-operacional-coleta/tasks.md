---

description: "Tasks da Feature 011 — Acompanhamento operacional da coleta"
---

# Tasks: Acompanhamento operacional da coleta

**Input**: design documents de `specs/011-acompanhamento-operacional-coleta/`.

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/rotas.md](contracts/rotas.md),
[contracts/consultas.md](contracts/consultas.md),
[contracts/governanca.md](contracts/governanca.md), [quickstart.md](quickstart.md).

**Stack** ([ADR 0001](../../docs/adr/0001-stack-inicial.md)): Python 3.13, Django 5.2
LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff. **Nenhuma dependência nova.**

**Persistência**: **0 modelos, 0 migrations, 0 índices.** O app novo
`trajetoria/acompanhamento` **não tem** `models.py` nem `migrations/`.

**Tests**: obrigatórios e escritos **antes** da implementação correspondente
(test-first). A feature toca autorização, escopo por unidade, elegibilidade e privacidade
(Princípio XXVI). Teste de comportamento novo DEVE falhar primeiro. Teste que só confirma
comportamento entregue por história anterior pode passar de imediato; se falhar, a
correção vai no módulo indicado.

**Organization**: Setup, Foundational, uma fase por história da spec (US1–US13, na
ordem de prioridade), Demonstração e Polish. Tarefas no mesmo arquivo nunca têm [P].
`trajetoria/acompanhamento/consultas.py`, `apresentacao.py`, `views.py`, os templates e
cada arquivo de teste são editados **em sequência**, história após história.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US13).

## Convenções para todas as tarefas

**Escopo da feature**

- **Somente leitura.** Nenhuma view, consulta ou função grava. Nada de formulário,
  botão ou link para criar, editar, abrir, encerrar, reabrir ou excluir Campanha. Nada
  de convite, lembrete, e-mail ou lista de não respondentes.
- **Elegibilidade só pela 004**:
  - `trajetoria.campanha.consultas.populacao_no_momento(campanha)` é o **único**
    contrato usado.
  - Ele é refinado com `.filter(universo)`, `.count()` e
    `.values(...).annotate(...).order_by()`.
  - **Não altere** `trajetoria/campanha/`: não torne `_filtro` público e não chame
    `avaliar` em laço.

**Indicadores**

- Elegíveis atuais, iniciadas (Participações existentes), concluídas (`concluida_em`
  não nulo) e iniciadas não concluídas (iniciadas − concluídas).
- Taxas: `iniciadas/elegíveis` e `concluídas/elegíveis`.
  - `Decimal`, uma casa, `ROUND_HALF_UP`.
  - `None` quando elegíveis = 0, exibido como "—" com texto acessível "não se aplica".
  - Sem teto de 100%. O arredondamento é apresentação, não regra.
- **Não** acrescentar: não iniciadas, abandono, recusas, taxa de recusa, completude.
- Iniciadas e concluídas **não** são filtradas pela elegibilidade atual (FR-038).

**Escopo e governança**

- Escopo derivado de `escopo_de_acompanhamento(vinculos)`, nomeando `Papel.CPAEG` e
  `Papel.CSAEG`.
  - CPAEG ativo → institucional.
  - Vários CSAEG → união das unidades.
  - CPAEG + CSAEG → institucional.
- Aplicado **na consulta**, antes de contar:
  - `Q(unidade__in=escopo.unidades)` sobre a Conclusão;
  - `Q(conclusao__unidade__in=escopo.unidades)` sobre a Participação.
  - O universo depende **só do escopo do operador**. O critério de unidades da Campanha
    **nunca** entra em `universo`/`universo_participacao`: nos elegíveis ele já está em
    `populacao_no_momento`; nas Participações seria reavaliar elegibilidade (FR-023,
    FR-038).
  - `unidades_relevantes` (escopo ∩ critério) é **só apresentação**: linhas com zero do
    recorte por unidade, recortes oferecidos e coluna Unidade do recorte por curso.
- Nunca calcule o total institucional para esconder valores no template.
- Visibilidade:
  - `Q(unidades__isnull=True) | Q(unidades__overlap=sorted(escopo.unidades))`;
  - comparação textual exata, sem normalização;
  - total zero **não** esconde a Campanha.

**Dados lidos**

- **Nunca leia** `Resposta`, `RespostaOpcao`, `Pessoa`, `id_externo`, `fonte`,
  `data_conclusao`.
- Nenhum template recebe instância de Conclusão, Participação ou Pessoa.
- Só objetos de valor (data-model §2) e a Campanha (nome, período, datas).
- A única UUID na página é a da Campanha, no endereço.

**Consultas**

- Sem consulta por linha de recorte, por Conclusão ou por Participação.
- Uma consulta proporcional ao número de Campanhas na lista é **aceita**.
- Sem SQL bruto, `CASE` dinâmico, `UNION`, cache, Redis, Celery ou visão materializada.
- Orçamentos de consultas são **proteção contra regressão**, não requisito.

**Recortes**

- Exatamente seis valores fechados: `unidade`, `curso`, `nivel`, `modalidade`,
  `forma-oferta`, `ano-conclusao`.
- Um por vez, por GET. A chave de curso é `(unidade, curso)`.
- `None` vira linha "… não informado(a)", **por último**.
- Ordem textual previsível, ou ano crescente; nunca por indicador.
- Linhas com zero **só** no recorte por unidade, a partir do critério da Campanha ou
  das unidades relevantes da CSAEG.

**Tempo e textos**

- Funções de consulta e apresentação recebem `agora: datetime | None = None` e o
  repassam a `estado`/`encerramento` da 004. As views passam `None` (relógio do sistema).
- Testes de view constroem Campanhas com período relativo a `timezone.localdate()`.
- Testes de consulta pura podem passar `agora` explícito.
- Termos ausentes de toda página: "dashboard", "KPI", "funil", "abandono",
  "desistência", "ranking", "melhor", "pior", "questionários integralmente
  respondidos", "role", "permission", "scope".
- Rótulos obrigatórios: "Participações iniciadas" e "Participações concluídas".

**Over engineering — pare se aparecer**

Novo model, migration, índice, Snapshot, Dashboard, Widget, Metric, Dimension, QueryEngine,
ReportEngine, FilterBuilder, repositório, cache, Celery, API, exportação, gráficos,
`Permission`, registro de capacidades, seletor de atuação.

**Dados de teste**

- Somente fictícios.
- Conclusões por ORM com o helper novo `tests/acompanhamento/construcao.py::conclusao`, que
  aceita `unidade`, `curso`, `nivel`, `modalidade`, `forma_oferta` e `ano`.
- Campanhas pelas operações da 004.
- Participações por `iniciar_participacao`/`concluir` da 005/006, reutilizando
  `tests/participacao/construcao.py::instrumento` e `preencher_instrumento`.

---

## Phase 1: Setup

**Purpose**: o app vazio registrado e roteado, sem models.

- [X] T001 Criar o app `trajetoria/acompanhamento/`:
  - `__init__.py`;
  - `apps.py` com `AcompanhamentoConfig`, `name = "trajetoria.acompanhamento"`;
  - docstring do pacote: "leitura operacional agregada da coleta (Feature 011); sem
    models, sem migrations".
  - **Não** crie `models.py` nem `migrations/`.
- [X] T002 Registrar `"trajetoria.acompanhamento"` em `INSTALLED_APPS` de
  `config/settings.py`, depois de `"trajetoria.editor"`.
- [X] T003 Rotas:
  - Criar `trajetoria/acompanhamento/urls.py` com `urlpatterns = []` (preenchido em
    US1/US2).
  - Acrescentar `path("acompanhamento/", include("trajetoria.acompanhamento.urls"))` em
    `config/urls.py`, antes dos `include` de `""`.
  - Atualizar a docstring de `config/urls.py` e a de
    `trajetoria/demonstracao/middleware.py` para citar a área `/acompanhamento/`, sem
    mudar código do middleware.
- [X] T004 [P] Criar `tests/acompanhamento/__init__.py` e
  `tests/acompanhamento/test_acompanhamento_fronteiras.py` com
  `test_app_sem_modelos_nem_migrations`:
  - `apps.get_app_config("acompanhamento").get_models()` vazio;
  - `trajetoria/acompanhamento/migrations` inexistente;
  - `call_command("makemigrations", "--check", "--dry-run")` sem mudanças.

**Checkpoint**: `uv run pytest tests/acompanhamento` verde; suíte completa verde.

---

## Phase 2: Foundational

**Purpose**: regra de governança, objetos de valor, apresentação básica, gate de acesso
e cenário de teste. Bloqueia todas as histórias.

### Testes primeiro

- [X] T005 [P] Em `tests/governanca/test_governanca_regras.py`:
  - Testes **novos**:
    - `test_matriz_de_acompanhamento`, parametrizado com a tabela de
      `contracts/governanca.md`: nenhum; CSAEG {Vitória}; CSAEG {Vitória, Serra}; CPAEG;
      CPAEG + CSAEG; CPAEG inativo + CSAEG ativo; só inativos. Verifica
      `pode_acompanhar_coleta` e `escopo_de_acompanhamento`, este como
      `(institucional, unidades)` ou `None`;
    - `test_acompanhar_equivale_a_ter_escopo`, para toda linha da matriz;
    - `test_papel_nao_listado_nao_concede_acompanhamento`: vínculo em memória com
      `papel="OUTRO"` ativo → `False`/`None`. Prova que não é "qualquer vínculo";
    - `test_escopo_independe_do_modo_de_demonstracao`: alterna
      `settings.TRAJETORIA_DEMONSTRACAO`.
  - Ajustes:
    - acrescentar as duas funções à verificação de assinatura `["vinculos"]`;
    - atualizar o conjunto esperado em `regras.__all__`;
    - **não** mudar a matriz das três regras existentes.
- [X] T006 [P] Em `tests/governanca/test_governanca_fronteiras.py`: trocar "três regras"
  por "três regras do editor e a regra de acompanhamento" na docstring. Confirmar que o
  teste de nomes proibidos continua passando com `EscopoDeAcompanhamento`,
  `pode_acompanhar_coleta` e `escopo_de_acompanhamento`.
- [X] T007 [P] Criar `tests/acompanhamento/test_acompanhamento_apresentacao.py`, puro,
  sem banco:
  - `Indicadores`:
    - `nao_concluidas`;
    - `taxa_inicio` e `taxa_conclusao` com 1/8 → `Decimal("12.5")`, 1/3 → `33.3`,
      2/3 → `66.7`, 9/8 → `112.5`;
    - elegíveis 0 → `None`;
    - soma por `+`.
  - `percentual`: `None` → `None`; `Decimal("30.0")` → `"30,0%"`; `Decimal("112.5")` →
    `"112,5%"`.
  - `chave_de_ordem`:
    - `None` por último;
    - anos crescentes;
    - textos `["Viana", "Águia Branca", "alegre", "Alegre"]` ordenados por (dobrado,
      exato), sem fundir "alegre" e "Alegre".
  - `rotulo_nao_concluidas`: EM_COLETA → "Em andamento"; EM_PREPARACAO e ENCERRADA →
    "Iniciadas e não concluídas".

### Implementação

- [X] T008 Em `trajetoria/governanca/regras.py`, acrescentar (contracts/governanca.md):
  - `@dataclass(frozen=True) class EscopoDeAcompanhamento` com `institucional: bool` e
    `unidades: frozenset[str]`;
  - `pode_acompanhar_coleta(vinculos)` =
    `any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)`;
  - `escopo_de_acompanhamento(vinculos)`:
    - CPAEG ativo → `EscopoDeAcompanhamento(True, frozenset())`;
    - senão, CSAEG ativos → `EscopoDeAcompanhamento(False, frozenset(v.unidade ...))`;
    - senão → `None`.
  - Atualizar `__all__` e a docstring do módulo: PAEG Art. 21, I, III; Art. 22, I, IV;
    interpretação operacional B1–B4 da spec 011; não concede gestão de Campanha nem
    dado individual.
  - **Não** alterar as três regras existentes nem `trajetoria/editor/acesso.py`.
  - Depende de T005, T006.
- [X] T009 Criar `trajetoria/acompanhamento/apresentacao.py` (data-model §2.2; research
  R8, R9, R10):
  - `Indicadores` (frozen dataclass: `elegiveis`, `iniciadas`, `concluidas`; propriedades
    `nao_concluidas`, `taxa_inicio`, `taxa_conclusao`; `__add__`);
  - `percentual`, `chave_de_ordem`, `rotulo_nao_concluidas`;
  - as constantes de texto: definições curtas do resumo (contracts/rotas.md), avisos de
    estado (research R10), textos de recusa, "Instrumento ainda não publicado", texto
    permanente da lista.

  `Indicadores` fica em `apresentacao.py` porque não consulta o banco. `consultas.py`
  o importa. Depende de T007.
- [X] T010 [P] Criar `tests/acompanhamento/construcao.py` (somente dados fictícios):
  - `conclusao(*, unidade=None, curso=None, nivel=None, modalidade=None,
    forma_oferta=None, ano=None, pessoa=None)` por ORM, fonte `"teste-acompanhamento"`;
  - `campanha(versao, *, estado="em_coleta" | "em_preparacao" | "encerrada_explicita",
    nome=None, **criterios)`:
    - período relativo a `timezone.localdate()`: −10 a +30 dias para em coleta e
      encerrada; +10 a +40 para preparação;
    - criada, configurada, aberta e encerrada só pelas operações da 004, com `agora` omitido;
  - `iniciada(campanha, conclusao)` e `concluida(campanha, conclusao, inst)` via
    `iniciar_participacao`/`preencher_instrumento`/`concluir`, com `agora=None`
    **passado explicitamente** a `preencher_instrumento`, cujo padrão é `NO_PERIODO`
    (2027) e seria rejeitado numa Campanha com período relativo a hoje;
  - `com_texto_declarado(participacao, inst, texto)`: `responder_texto(participacao,
    inst.texto, texto, agora=None)`, para o teste de privacidade;
  - `concluida_por_recusa(campanha, conclusao, inst)`: responde Q1 = "Não" e conclui;
  - `atuar_como(cliente, identificador)`, reexportado de
    `tests/editor/construcao_editor.py`;
  - `A, B, C` = identificadores dos operadores fictícios da 010.
- [X] T011 Criar `tests/acompanhamento/conftest.py`:
  - fixture `autouse` que liga `TRAJETORIA_DEMONSTRACAO`;
  - `inst` = `tests.participacao.construcao.instrumento()`;
  - **cenário de referência** `ref`, montado em T010:
    - Conclusões elegíveis: Serra ×3 (curso "Técnico em Informática" ×2, "TADS" ×1),
      Vitória ×2 ("Técnico em Informática", "Engenharia Civil"), Cefor ×1, sem unidade
      ×1 (curso ausente), com `nivel`, `modalidade`, `forma_oferta`, `ano` variados e
      um "Graduação" + um "graduação";
    - Campanha **I** (em coleta, sem critério de unidade);
    - Campanha **R** (em coleta, `unidades=["Serra", "Cefor"]`);
    - Campanha **P** (preparação, Versão rascunho por
      `tests.campanha.construcao.versao_rascunho`);
    - Campanha **E** (encerrada explícita);
    - Participações em I: Serra 2 iniciadas (1 concluída), Vitória 1 concluída por
      recusa, sem unidade 1 iniciada. A Participação de Serra não concluída recebe, por
      `com_texto_declarado`, o valor fictício `"RESPOSTA-DECLARADA-FICTICIA-011"`;
    - Campanha **N** (em coleta, `ano_minimo` = ano de uma Conclusão de Vitória do
      `ref`), usada para simular 005/DP-507.
  - Clientes:
    - `cliente_cpaeg` (A, CPAEG);
    - `cliente_csaeg_vitoria` (B, CSAEG Vitória);
    - `cliente_csaeg_serra` (B, CSAEG Serra);
    - `cliente_duas_csaeg` (B, Serra + Vitória);
    - `cliente_cpaeg_e_csaeg` (A, CPAEG + CSAEG Serra);
    - `cliente_sem_vinculo` (C);
    - `cliente_nao_identificado`.
  - Vínculos por `trajetoria.governanca.operacoes.registrar_vinculo`. Depende de T010.
- [X] T012 Criar `trajetoria/acompanhamento/acesso.py` (research R12; contracts/rotas.md,
  ordem de verificação):
  - decorador `acompanhamento(view)`:
    1. `operador_em_uso(request)`; `None` →
       `redirect("/demonstracao/operador/?destino=acompanhamento")`;
    2. `vinculos_ativos`; vazio → `recusa(request, RECUSA_SEM_ATUACAO)`;
    3. `escopo_de_acompanhamento(vinculos)`; `None` → mesma recusa;
    4. define `request.escopo` e `request.atuacao` (rótulos dos vínculos e
       `pode_consultar_rascunho(vinculos)`);
    5. chama a view;
    6. marca `envolvida.acompanhamento = True`.
  - `recusa(request, texto)`: renderiza `acompanhamento/recusa.html` com status 403,
    sem dado de Campanha.
  - Nunca consulta `is_staff`, `is_superuser`, `request.user` nem
    `TRAJETORIA_DEMONSTRACAO`. Depende de T008, T009.
- [X] T013 [P] Criar os templates base:
  - `trajetoria/acompanhamento/templates/acompanhamento/base.html`:
    - `lang="pt-BR"`;
    - título `{% block titulo %} — Acompanhamento da coleta — Trajetória Ifes`;
    - `<style>` com `{% include "interface/estilo.css" %}`, `{% include "editor/estilo.css" %}`
      e um bloco pequeno para tabela e região rolável;
    - "Pular para o conteúdo";
    - faixa `role="note"` com o texto de ambiente não produtivo (o mesmo `BANNER` do
      editor, importado de `trajetoria.editor.mensagens` só para leitura);
    - cabeçalho com "Acompanhamento da coleta", "Atuação: …", "Editor do instrumento"
      e "Trocar operador fictício";
    - trilha `nav aria-label="Você está em"`;
    - um `main` e um `footer`;
    - **sem** `<script>`.
  - `trajetoria/acompanhamento/templates/acompanhamento/recusa.html`: `h1` "Acesso não
    permitido", texto e links de volta.

**Checkpoint**: `uv run pytest tests/governanca tests/acompanhamento` verde; editor
(009/010) inalterado.

---

## Phase 3: User Story 1 — CPAEG vê as Campanhas e seu andamento institucional (P1) 🎯 MVP

**Goal**: `/acompanhamento/` lista todas as Campanhas para o CPAEG, com instrumento,
período, situação, elegíveis atuais, iniciadas e concluídas.

**Independent Test**: cenário `ref` + `cliente_cpaeg`; abrir a lista e conferir os três
números de cada Campanha com contagem manual.

### Testes primeiro

- [X] T014 [P] [US1] Criar `tests/acompanhamento/test_acompanhamento_indicadores.py`, por
  consulta direta (`agora` explícito quando necessário):
  - `indicadores_da_campanha(I, institucional)` = (7 elegíveis, 4 iniciadas, 2
    concluídas), ajustados aos números do `ref`;
  - elegíveis = `populacao_no_momento(I).count()`;
  - Participação sem nenhuma Resposta conta como iniciada;
  - concluída por recusa (Q1 = "Não") conta como concluída;
  - Campanha sem Participações → 0/0/0;
  - nova Conclusão elegível incorporada entre duas chamadas → elegíveis +1;
  - Participação concluída entre duas chamadas → concluídas +1, não concluídas −1;
  - **taxa > 100%**: na Campanha **N** (critério `ano_minimo`), iniciar e concluir a
    Participação de uma Conclusão elegível e depois alterar por ORM, **só no teste**, o
    `ano_conclusao` dessa Conclusão para abaixo do mínimo (simula 001/DP-005, sem
    alterar a 001). Resultado: elegíveis diminui, a Participação continua em iniciadas e
    concluídas, e a taxa aparece como calculada (por exemplo, 1/0 → "—"; 2/1 → 200,0%),
    sem teto nem erro. Nenhum código específico para o caso.
- [X] T015 [P] [US1] Criar `tests/acompanhamento/test_acompanhamento_lista.py`:
  - CPAEG vê I, R, P e E, inclusive Campanha nunca aberta e expirada criada pelas
    operações da 004 com período passado;
  - cada linha com nome (link para `/acompanhamento/campanhas/<id>/`), "Pesquisa —
    designação", período "dd/mm/aaaa a dd/mm/aaaa" ou "Período não definido", situação
    por extenso, elegíveis, "Participações iniciadas", "Participações concluídas";
  - texto permanente de população atual e de contagem por formação;
  - **sem** taxa, sem `%`;
  - ordem determinística independente dos números;
  - lista vazia → "Nenhuma Campanha no escopo da sua atuação".

### Implementação

- [X] T016 [US1] Criar `trajetoria/acompanhamento/consultas.py` (contracts/consultas.md):
  - `campanhas_visiveis(escopo)`, só o ramo institucional nesta história:
    `Campanha.objects.select_related("versao__pesquisa")` ordenado por
    `(F("inicio").desc(nulls_last=True), "nome", "id")`;
  - `universo(escopo) -> Q` e `universo_participacao(escopo) -> Q`, com `Q()` no
    institucional. Dependem só do escopo, nunca da Campanha;
  - `indicadores_da_campanha(campanha, escopo) -> Indicadores`, com duas consultas:
    `populacao_no_momento(c).filter(universo).count()` e
    `Participacao.objects.filter(campanha=c).filter(universo_participacao).aggregate(iniciadas=Count("id"), concluidas=Count("id", filter=Q(concluida_em__isnull=False)))`;
  - `CampanhaAcompanhada` (frozen dataclass, data-model §2.5) e
    `campanhas_acompanhadas(escopo, *, pode_consultar_rascunho, agora=None)`.

  Não importa `Resposta`, `RespostaOpcao` nem `Pessoa`. Depende de T014, T015.
- [X] T017 [US1] Em `trajetoria/acompanhamento/apresentacao.py`:
  - `instrumento(campanha, *, pode_consultar_rascunho) -> Instrumento(texto, endereco)`
    (research R11): Versão `PUBLICADA` ou operador com rascunho →
    `"<Pesquisa.nome> — <Versao.designacao>"` + `/editor/versoes/<uuid>/`; senão,
    `"Instrumento ainda não publicado"`, `endereco=None`;
  - `situacao(estado)`: "Em preparação", "Em coleta", "Encerrada";
  - `periodo(campanha)`.
- [X] T018 [US1] Criar `trajetoria/acompanhamento/views.py` com
  `@require_GET @acompanhamento def campanhas(request)`, renderizando
  `acompanhamento/campanhas.html` com os objetos de valor. Registrar
  `path("", views.campanhas)` em `trajetoria/acompanhamento/urls.py`. Depende de T012,
  T016, T017.
- [X] T019 [US1] Criar `trajetoria/acompanhamento/templates/acompanhamento/campanhas.html`:
  - `h1` "Acompanhamento da coleta";
  - texto permanente;
  - `<table>` com `caption` e `th scope="col"`, nome da Campanha em `th scope="row"`;
  - colunas de contracts/rotas.md (Lista);
  - sem taxas.

**Checkpoint**: US1 testável sozinha com operador CPAEG.

---

## Phase 4: User Story 2 — CPAEG abre uma Campanha e vê os indicadores (P1)

**Goal**: `/acompanhamento/campanhas/<id>/` com cabeçalho e resumo dos seis indicadores
e suas definições.

**Independent Test**: abrir I, a Campanha sem Participações e uma com elegíveis = 0, e
conferir valores e "—".

### Testes primeiro

- [X] T020 [P] [US2] Criar `tests/acompanhamento/test_acompanhamento_detalhe.py`:
  - I mostra elegíveis, "Participações iniciadas", "Participações concluídas", "Em
    andamento", taxa de início e taxa de conclusão com os valores do `ref`, cada um com a
    definição curta de contracts/rotas.md;
  - Campanha sem Participações → 0 e taxas "0,0%";
  - elegíveis = 0 (Campanha com `unidades=["Inexistente"]`) → as duas taxas "—" com
    "não se aplica" no HTML e **nunca** "0%", "NaN", "inf" ou "∞";
  - texto "cada formação concluída conta separadamente";
  - "Participações concluídas" presente e "questionários integralmente respondidos"
    ausente;
  - sem "abandon", "desist", "expirad".

### Implementação

- [X] T021 [US2] Em `trajetoria/acompanhamento/consultas.py`: `campanha_acompanhada(
  campanha, escopo, *, pode_consultar_rascunho, recorte=None, agora=None)`, por enquanto
  só totais, estado e encerramento (004), instrumento. Depende de T020.
- [X] T022 [US2] Em `trajetoria/acompanhamento/views.py`:
  `@require_GET @acompanhamento def campanha(request, campanha)`:
  - `campanhas_visiveis(request.escopo).filter(pk=campanha).first()`;
  - inexistente → `Http404`;
  - renderiza `acompanhamento/campanha.html`.

  Registrar `path("campanhas/<uuid:campanha>/", views.campanha)`. A recusa de fora do
  escopo vem em US5.
- [X] T023 [US2] Criar `trajetoria/acompanhamento/templates/acompanhamento/campanha.html`:
  - trilha;
  - `h1` com o nome;
  - `<dl>` com instrumento (link só se `endereco`), período, situação, "Aberta em" e
    "Encerrada em" com a forma, quando houver;
  - resumo em `<dl>`, com taxa `None` como
    `<span aria-hidden="true">—</span><span class="visualmente-oculto">não se aplica</span>`;
  - rodapé "Números calculados em <data e hora locais>" (não gravado);
  - sem `<script>`.

**Checkpoint**: US1 + US2 = MVP institucional.

---

## Phase 5: User Story 3 — CSAEG vê somente Campanhas relevantes (P1)

**Goal**: visibilidade por critério de unidades × unidades do escopo.

**Independent Test**: CSAEG Vitória e CSAEG Serra abrem a lista do `ref`.

### Testes primeiro

- [X] T024 [P] [US3] Criar `tests/acompanhamento/test_acompanhamento_visibilidade.py`:
  - CSAEG Vitória vê I (sem critério) e **não** vê R ({Serra, Cefor});
  - CSAEG Serra vê I e R;
  - Campanha `unidades=["Serra"]` sem nenhuma Conclusão de Serra elegível → visível ao
    CSAEG Serra com 0;
  - Campanha sem critério de unidade e com `niveis=["Pós-graduação"]` → visível a CSAEG
    de qualquer unidade;
  - vínculo "Campus Serra" × critério "Serra" → não visível;
  - P (preparação) e E (encerrada) visíveis quando relevantes;
  - por consulta direta: `campanhas_visiveis` institucional = todas.

### Implementação

- [X] T025 [US3] Em `trajetoria/acompanhamento/consultas.py`: ramo de unidades de
  `campanhas_visiveis`:
  `filter(Q(unidades__isnull=True) | Q(unidades__overlap=sorted(escopo.unidades)))`.
  A lista e o detalhe usam a mesma função. Depende de T024.

---

## Phase 6: User Story 4 — CSAEG vê somente agregados da sua unidade (P1)

**Goal**: todo número no escopo de unidades é calculado só sobre as unidades relevantes.

**Independent Test**: comparar números de CPAEG e CSAEG Vitória em I.

### Testes primeiro

- [X] T026 [P] [US4] Em `tests/acompanhamento/test_acompanhamento_escopo.py`:
  - por consulta direta, `indicadores_da_campanha(I, CSAEG Vitória)` = só Vitória (2
    elegíveis, 1 iniciada, 1 concluída);
  - nenhuma Conclusão sem unidade entra;
  - Serra tem Participações em I, e elas **não** aparecem em iniciadas, concluídas nem
    não concluídas do CSAEG Vitória;
  - `unidades_relevantes`: sem critério → escopo; com critério → interseção;
    institucional → `None`;
  - **o universo não usa o critério da Campanha**: CSAEG de {Serra, Vitória} numa
    Campanha restrita a {Serra}. Uma Participação de Conclusão de Serra é alterada por
    ORM, só no teste, para Vitória (simula 005/DP-507). Ela continua em iniciadas e
    concluídas para esse CSAEG e para o CPAEG; elegíveis não a contam;
  - **escopo aplicado no SQL**: com `CaptureQueriesContext`, **toda** consulta do CSAEG
    sobre `academico_conclusaoacademica` ou `participacao_participacao` contém o filtro
    de unidade (`"unidade" IN`). Consultas de vínculo, visibilidade e Campanha não entram
    na verificação;
  - HTML do detalhe como CSAEG Vitória não contém "Serra", "Cefor" nem "não informada".

### Implementação

- [X] T027 [US4] Em `trajetoria/acompanhamento/consultas.py`:
  - ramo de unidades de `universo`/`universo_participacao`:
    `Q(unidade__in=escopo.unidades)` e `Q(conclusao__unidade__in=escopo.unidades)`,
    **sem** o critério de unidades da Campanha;
  - `unidades_relevantes(campanha, escopo)`, usada só em apresentação: linhas com zero,
    recortes oferecidos e coluna Unidade.

  Depende de T026.

---

## Phase 7: User Story 5 — URL direta não permite acesso fora do escopo (P1)

**Goal**: recusa antes de qualquer indicador.

**Independent Test**: CSAEG Vitória cola o endereço de R; operador C e não identificado
em todas as rotas.

### Testes primeiro

- [X] T028 [P] [US5] Criar `tests/acompanhamento/test_acompanhamento_acesso.py`:
  - CSAEG Vitória → detalhe de R, com e sem `?recorte=curso` → **403**; HTML sem nome,
    período, instrumento, unidades nem números de R. Com `CaptureQueriesContext`, nenhuma
    consulta a `participacao_participacao` nem a `academico_conclusaoacademica`;
  - operador C → 403 "sem atuação" na lista e no detalhe;
  - não identificado → 302 para `/demonstracao/operador/?destino=acompanhamento`;
  - UUID inexistente com vínculo → 404; sem vínculo → 403 antes;
  - modo desligado → 404 nas duas rotas;
  - POST → 405;
  - **teste estrutural**: toda rota de `trajetoria.acompanhamento.urls.urlpatterns` tem
    `callback.acompanhamento is True`.

### Implementação

- [X] T029 [US5] Em `trajetoria/acompanhamento/views.py`: na view `campanha`, buscar
  primeiro `Campanha.objects.filter(pk=campanha).exists()` (404 se não existe) e depois
  a visibilidade por `campanhas_visiveis(request.escopo)`. Não visível →
  `recusa(request, RECUSA_FORA_DO_ESCOPO)`, **antes** de `campanha_acompanhada`.
  Depende de T028.

---

## Phase 8: User Story 6 — Indicadores derivados, não persistidos (P1)

**Goal**: nenhuma escrita; nenhuma leitura de Resposta; atualização na consulta
seguinte.

**Independent Test**: comparar o banco antes e depois; capturar SQL.

### Testes primeiro

- [X] T030 [P] [US6] Criar `tests/acompanhamento/test_acompanhamento_consultas.py`:
  - **nenhuma escrita**: contagem de linhas de Pessoa, ConclusaoAcademica, Campanha,
    Versao, Participacao, Resposta, RespostaOpcao e VinculoDeGovernanca idêntica antes e
    depois de abrir lista, detalhe e os seis recortes, como CPAEG e CSAEG;
  - **nenhuma Resposta**: no SQL capturado de todas essas páginas, nenhuma ocorrência de
    `participacao_resposta` nem `participacao_respostaopcao`;
  - **anti-N+1 (proteção, não requisito)**: o detalhe com `?recorte=curso` faz o
    **mesmo** número de consultas com 3 e com 30 cursos distintos; a lista cresce no
    máximo 2 consultas por Campanha acrescentada (1 → 3 Campanhas). Comentário no teste:
    "protege o desenho atual contra N+1; não é contrato da spec".
- [X] T031 [P] [US6] Em `tests/acompanhamento/test_acompanhamento_fronteiras.py`:
  - **AST**: `trajetoria/acompanhamento` não importa `Pessoa`, `Resposta`,
    `RespostaOpcao` nem módulos `operacoes`;
  - nenhum nome definido contém `metric`, `dimension`, `dashboard`, `widget`,
    `snapshot`, `cache`, `ranking`, `permission`, `policy`, `capab`;
  - `trajetoria/campanha/consultas.py` não foi alterado: `_filtro` não está em
    `__all__` e não há nome público novo.

### Implementação

- [X] T032 [US6] Ajustar `trajetoria/acompanhamento/consultas.py` só se T030/T031
  falharem. Esperado: passam com o desenho de T016–T027.

---

## Phase 9: User Story 7 — Recorte por unidade para CPAEG (P2)

**Goal**: `?recorte=unidade`; tabela Unidade | Elegíveis | Iniciadas | Concluídas | Taxa
de conclusão.

**Independent Test**: I e R com CPAEG; soma = total.

### Testes primeiro

- [X] T033 [P] [US7] Criar `tests/acompanhamento/test_acompanhamento_recortes.py`, parte
  unidade:
  - I/CPAEG → linhas Cefor, Serra, Vitória, "Unidade não informada" (por último), valores
    do `ref`;
  - R/CPAEG → Cefor e Serra, inclusive Cefor com 0 e "—" se não houver elegível;
  - CSAEG de duas unidades em Campanha sem critério → as duas linhas, inclusive com 0;
  - CPAEG em Campanha sem critério → **nenhuma** linha de unidade inventada;
  - ordem textual, nunca por indicador (dados em que a ordem por taxa difere);
  - **soma das linhas = total** do resumo.

### Implementação

- [X] T034 [US7] Em `trajetoria/acompanhamento/consultas.py`:
  - `Recorte` (Enum fechado de seis membros, data-model §2.3, com `valor`, `rotulo`,
    `campos`, `rotulo_nao_informado`, `de_valor`);
  - `LinhaDeRecorte(chave, indicadores)`;
  - em `campanha_acompanhada`, as consultas (c) e (d) de contracts/consultas.md com
    `.order_by()` vazio, combinação por chave e linhas com zero **só** para `UNIDADE`
    (critério da Campanha; no escopo de unidades, as relevantes);
  - ordenação por `chave_de_ordem`;
  - `recortes_oferecidos(campanha, escopo)`.

  Depende de T033.
- [X] T035 [US7] Em `trajetoria/acompanhamento/views.py`:
  - ler `request.GET.getlist("recorte")`: mais de um valor ou valor fora de
    `Recorte.de_valor` → `Http404`; ausente → `UNIDADE` se oferecido, senão `CURSO`;
  - criar `trajetoria/acompanhamento/templates/acompanhamento/_tabela_recorte.html`:
    - `nav aria-label="Recortes"` com links `?recorte=…` e `aria-current="page"`;
    - região `role="region"` com `aria-label` e `tabindex="0"`, rolagem horizontal só
      nela;
    - `<table>` com `caption` "<Recorte> — dados do registro acadêmico institucional",
      `th scope="col"` e `th scope="row"`, e linha final de total;
  - incluir o template em `campanha.html`.

---

## Phase 10: User Story 8 — Recorte por curso dentro do escopo (P2)

**Goal**: chave `(unidade, curso)`, sem entidade de Curso.

**Independent Test**: "Técnico em Informática" em Serra e Vitória.

### Testes primeiro

- [X] T036 [P] [US8] Em `tests/acompanhamento/test_acompanhamento_recortes.py`, parte
  curso:
  - CPAEG → duas linhas "Técnico em Informática", Serra e Vitória;
  - Conclusão sem curso → "Curso não informado" na sua unidade;
  - Conclusão sem unidade → "Unidade não informada" na coluna de unidade;
  - CSAEG Serra → só cursos de Serra e **sem coluna Unidade** (uma unidade relevante);
  - CSAEG de duas unidades → coluna Unidade presente;
  - nenhum curso com 0 inventado;
  - soma = total.

### Implementação

- [X] T037 [US8] Em `trajetoria/acompanhamento/apresentacao.py`, `rotulo_da_chave(
  recorte, chave)`. Em `_tabela_recorte.html`, omitir a coluna Unidade do recorte por
  curso quando houver uma única unidade relevante. Sem entidade, catálogo, código
  sintético ou normalização de curso. Depende de T036.

---

## Phase 11: User Story 9 — Recortes adicionais (P2)

**Goal**: nível, modalidade, forma de oferta e ano de conclusão.

**Independent Test**: cada recorte com "não informado" e soma.

### Testes primeiro

- [X] T038 [P] [US9] Em `tests/acompanhamento/test_acompanhamento_recortes.py`, parte
  adicional:
  - `nivel`, `modalidade`, `forma-oferta`: valores como registrados, "Graduação" e
    "graduação" em linhas distintas, "… não informado(a)" por último;
  - `ano-conclusao`: ordem crescente, rótulo "Ano de conclusão" e nunca "coorte" no HTML;
  - recorte por nível com Participação cuja Q14 respondida difere do nível institucional
    → conta no nível da Conclusão;
  - `?recorte=coorte`, `?recorte=`, `?recorte=unidade&recorte=curso` → 404;
  - nenhum nível, modalidade ou forma de oferta com 0 inventado;
  - **soma = total** parametrizada pelos seis recortes × {CPAEG, CSAEG Vitória, duas
    CSAEG};
  - recortes oferecidos: seis para CPAEG e duas CSAEG; cinco (sem unidade) para CSAEG
    única, e `?recorte=unidade` ainda atendido para ela.

### Implementação

- [X] T039 [US9] Completar `rotulo_da_chave` e os membros restantes de `Recorte`, se
  T038 falhar. Esperado: o desenho de T034 já atende.

---

## Phase 12: User Story 10 — Campanha encerrada com aviso de população atual (P2)

**Goal**: E consultável, com aviso, encerramento e "iniciadas e não concluídas".

**Independent Test**: E e uma Campanha nunca aberta expirada.

### Testes primeiro

- [X] T040 [P] [US10] Criar `tests/acompanhamento/test_acompanhamento_estados.py`, parte
  encerrada:
  - E (encerramento explícito) → aviso exato "A população elegível apresentada
    corresponde aos dados institucionais atuais e pode diferir da população existente
    quando a coleta foi encerrada."; "Encerrada em" com a forma "antecipadamente";
    "Iniciadas e não concluídas";
  - encerrada por fim do período, por consulta direta com `agora` posterior ao fim →
    forma "fim do período" e o mesmo aviso;
  - nunca aberta expirada → "Esta Campanha não chegou a entrar em coleta.";
  - Conclusão elegível incorporada depois do encerramento → elegíveis +1, aviso
    presente.

### Implementação

- [X] T041 [US10] Em `trajetoria/acompanhamento/apresentacao.py`, `avisos_do_estado(
  campanha, estado, encerramento)` (research R10). Em `campanha.html`, exibir avisos,
  encerramento e o rótulo de `rotulo_nao_concluidas`. Depende de T040.

---

## Phase 13: User Story 11 — Campanha em preparação e em coleta; instrumento em rascunho (P2)

**Goal**: avisos de preparação e de coleta; "Instrumento ainda não publicado" para quem
não consulta rascunho.

**Independent Test**: P com CPAEG e CSAEG; I.

### Testes primeiro

- [X] T042 [P] [US11] Em `tests/acompanhamento/test_acompanhamento_estados.py`, parte
  preparação e coleta:
  - P → "A coleta ainda não começou.", elegíveis exibidos, iniciadas e concluídas 0;
  - I → "Em andamento" e "momento da consulta";
  - período não definido → "Período não definido";
  - **P/CSAEG** → "Instrumento ainda não publicado". HTML **sem** nome da Pesquisa,
    designação da Versão, `/editor/versoes/` e nenhum texto de Seção ou Pergunta. Vale
    na lista e no detalhe;
  - **P/CPAEG** → "Pesquisa — designação" e link `/editor/versoes/<uuid>/`;
  - Campanha com Versão publicada para CSAEG → identificação e link.

### Implementação

- [X] T043 [US11] Ajustar `instrumento`/`avisos_do_estado` e os templates se T042
  falhar. Esperado: T017 e T041 já atendem.

---

## Phase 14: User Story 12 — Múltiplos vínculos (P2)

**Goal**: união de unidades e precedência fixa do CPAEG, sem seletor.

**Independent Test**: `cliente_duas_csaeg` e `cliente_cpaeg_e_csaeg`.

### Testes primeiro

- [X] T044 [P] [US12] Em `tests/acompanhamento/test_acompanhamento_escopo.py`, parte
  múltiplos vínculos:
  - duas CSAEG (Serra + Vitória) → lista com Campanhas relevantes a qualquer das duas;
    números somam Serra e Vitória;
  - em Campanha `unidades=["Serra"]`, só Serra;
  - recorte por unidade com as duas unidades relevantes, ou só Serra na Campanha
    restrita;
  - CPAEG + CSAEG Serra → institucional;
  - desativar o CPAEG pelo `desativar_vinculo` da 010 → a requisição seguinte só com
    Serra (SC-013), sem nova escolha;
  - nenhum seletor de atuação no HTML;
  - só vínculo CSAEG inativo → 403 "sem atuação".

### Implementação

- [X] T045 [US12] Nenhuma implementação nova esperada (T008, T025, T027). Corrigir em
  `trajetoria/governanca/regras.py` ou `consultas.py` se T044 falhar.

---

## Phase 15: User Story 13 — Acessibilidade e responsividade (P3)

**Goal**: marcação acessível, sem JavaScript, sem depender de cor.

### Testes primeiro

- [X] T046 [P] [US13] Criar `tests/acompanhamento/test_acompanhamento_acessibilidade.py`,
  na lista, no detalhe com cada recorte e na recusa:
  - um único `h1`;
  - `lang="pt-BR"`;
  - link "Pular para o conteúdo" para `#conteudo`;
  - `caption` em toda `table`;
  - `th scope="col"` e `scope="row"`;
  - `nav aria-label="Recortes"` com um `aria-current="page"`;
  - região rolável com `role="region"`, `aria-label` e `tabindex="0"`;
  - "—" acompanhado de "não se aplica" visualmente oculto;
  - **nenhum `<script>`**;
  - nenhuma barra de progresso;
  - termos proibidos ausentes (lista das Convenções).

### Implementação

- [X] T047 [US13] Ajustar `base.html`, `campanhas.html`, `campanha.html`,
  `_tabela_recorte.html` e o bloco de estilo para 320 px e zoom de 200% (só a tabela
  rola). Corrigir o que T046 apontar.

---

## Phase 16: Demonstração (A/B/C preservados; cenário fictício próprio da 011)

**Purpose**: B (CSAEG Vitória) exercita a 011 no cenário do preparo, sem alterar a
010, a 007/008 nem regras de produção (spec FR-142; research R13, R14).

### Testes primeiro

- [X] T048 [P] Em `tests/interface/test_demonstracao_operador.py`:
  - **sem alterar** os testes existentes: `(A, CPAEG, "")` e `(B, CSAEG, "Vitória")`
    continuam esperados;
  - testes novos:
    - `GET /demonstracao/operador/?destino=acompanhamento` contém o campo oculto
      `destino`;
    - POST de escolha com `destino=acompanhamento` → 302 para `/acompanhamento/`;
    - com `destino=qualquer-coisa`, `destino=/externo/` ou ausente → `/editor/`;
    - a página lista links "Editor do instrumento" e "Acompanhamento da coleta" para o
      operador em uso.
- [X] T049 [P] Criar `tests/acompanhamento/test_acompanhamento_demonstracao.py`, com
  `call_command("preparar_demonstracao")`:
  - existe "Demonstração — acompanhamento Serra e Vitória": nunca aberta, sem período,
    Versão = baseline em RASCUNHO, `unidades == ["Serra", "Vitória"]`, demais critérios
    `None`, estado EM PREPARAÇÃO;
  - repetir o preparo não duplica Campanha nem vínculo;
  - vínculos exatamente A/CPAEG, B/CSAEG Vitória e C sem vínculo;
  - **regressão da jornada**:
    - `iniciar_participacao(campanha_demo, <Conclusão de Vitória>)` é rejeitada com
      `COLETA_NAO_ADMITIDA` e não grava nada;
    - `campanhas_em_coleta_para` das três Conclusões de Vitória (SIM-C-0002, -0003,
      -0012) **não** contém a Campanha nova;
    - `situacao_de_entrada` de Bruno (SIM-P-0002) e das duas Carla (SIM-P-0010,
      SIM-P-0011) igual à esperada hoje;
    - o teste existente
      `tests/interface/test_interface_cenario.py::test_situacoes_da_tabela_r17`, que roda
      o preparo, continua verde **sem alteração** e é a regressão da tabela R17 inteira;
  - como B: lista **só** com a Campanha de acompanhamento; detalhe com 3 elegíveis,
    "Instrumento ainda não publicado", "A coleta ainda não começou", sem opção de recorte
    por unidade; endereço de "Demonstração — coleta ampla" → 403;
  - como A: três Campanhas; "coleta ampla" com 9 elegíveis; a de acompanhamento com 6
    (Serra 3, Vitória 3) e instrumento identificado;
  - como C: 403.

### Implementação

- [X] T050 Em `trajetoria/demonstracao/cenario.py`:
  - acrescentar a constante
    `CAMPANHA_ACOMPANHAMENTO = ("Demonstração — acompanhamento Serra e Vitória", {"unidades": ["Serra", "Vitória"]})`, *(Revisado pela ADR 0004: hoje `("Demonstração — rodada em preparação", {})`.)*
    **separada** de `CAMPANHAS`, para que `_exigir_campanhas_em_coleta` não a verifique;
  - em `preparar()`, dentro da transação e depois de `_versao_de_demonstracao()`: se não
    existe Campanha com esse nome, `op_campanha.criar_campanha(nome, materializar().versao)`
    e `op_campanha.definir_criterios(campanha, **criterios)`. **Sem** período e **sem**
    `abrir`;
  - **não** alterar `VINCULOS`, `CAMPANHAS` nem dados acadêmicos;
  - atualizar a docstring do módulo (Feature 011: Campanha fictícia nunca aberta, para
    o acompanhamento por B/CSAEG Vitória; não admite Participação; não altera a
    jornada).

  Depende de T049.
- [X] T051 Em `trajetoria/demonstracao/views.py` e
  `trajetoria/demonstracao/templates/demonstracao/operador.html`:
  - `operadores` lê `request.GET.get("destino")` e só repassa ao template se for
    `"acompanhamento"`;
  - o formulário inclui `<input type="hidden" name="destino" value="acompanhamento">`
    nesse caso;
  - `escolher_operador` redireciona com
    `{"acompanhamento": "/acompanhamento/"}.get(request.POST.get("destino"), "/editor/")`;
  - a página mostra links "Editor do instrumento" (`/editor/`) e "Acompanhamento da
    coleta" (`/acompanhamento/`) quando há operador em uso;
  - atualizar o comentário "Sempre o início do editor" para "destino fechado: editor ou
    acompanhamento; sem endereço vindo do cliente".

  Depende de T048.

**Checkpoint**: `uv run pytest tests/interface tests/participacao tests/acompanhamento`
verde; jornada 007/008 inalterada.

---

## Phase 17: Polish & Cross-Cutting

- [X] T052 [P] Teste de privacidade em
  `tests/acompanhamento/test_acompanhamento_privacidade.py`. Com o `ref` e Pessoas
  fictícias de `nome` e `id_externo` conhecidos, o HTML de lista, detalhe (seis recortes)
  e recusa, para CPAEG, CSAEG Vitória e duas CSAEG, **não contém**:
  - nenhum `Pessoa.nome`;
  - nenhum `id_externo` de Pessoa ou Conclusão;
  - nenhuma UUID de Conclusão ou Participação;
  - nenhum valor declarado: o texto fictício `"RESPOSTA-DECLARADA-FICTICIA-011"`
    respondido no `ref`. Textos curtos e genéricos de Opção ("Sim", "A") não entram
    na verificação, para não gerar falso positivo;
  - nenhuma UUID além da Campanha;
  - nenhum link de drill-down.

  Também verifica que o contexto dos templates (`response.context`) não contém instância
  de `Pessoa`, `ConclusaoAcademica`, `Participacao` ou `Resposta`.
- [X] T053 [P] Teste de escopo negativo em
  `tests/acompanhamento/test_acompanhamento_fronteiras.py`. Nenhuma página do
  acompanhamento contém `<form method="post">`, nem textos "Criar Campanha", "Abrir",
  "Encerrar", "Reabrir", "Excluir", "Convite", "Lembrete", "E-mail", "WhatsApp",
  "não respondentes", "Exportar", "CSV", "XLSX".
- [X] T054 Registrar DP-1101 nos artefatos da implementação:
  - docstring de `trajetoria/acompanhamento/consultas.py`: "Recortes agregados sem
    supressão nem limiar (DP-1101 aberta). A exposição produtiva dos recortes finos
    (curso, ano) DEVE revisitar DP-1101 antes de ocorrer (010/DP-1001)";
  - o mesmo em `trajetoria/acompanhamento/apresentacao.py`, junto aos textos.
- [X] T055 [P] Atualizar a documentação, **sem** alterar a linha "Operador fictício B —
  CSAEG, unidade Vitória":
  - em `specs/010-governanca-papeis-escopos/quickstart.md`, a seção de preparo menciona
    a Campanha fictícia nunca aberta acrescentada pela 011;
  - em `README.md`, se houver lista de áreas da demonstração, acrescentar
    `/acompanhamento/`.
- [X] T056 Executar `uv run ruff check . && uv run ruff format --check .`,
  `uv run python manage.py makemigrations --check --dry-run` e `uv run pytest` (suíte
  completa 001–011). Corrigir regressões **sem** alterar regras da 001–010.
- [X] T057 Executar o roteiro manual de
  [quickstart.md](quickstart.md) (passos 1–15), incluindo 320 px, zoom de 200%, teclado
  e JavaScript desligado. Registrar divergências como correção nos arquivos da 011.
- [X] T058 Revisão final contra "Sinais de over engineering" do plan:
  - nenhum model, migration ou índice;
  - nenhuma alteração em `trajetoria/campanha/`, `trajetoria/participacao/`,
    `trajetoria/academico/`, `trajetoria/instrumento/`, `trajetoria/editor/` nem em
    `trajetoria/governanca/models.py` e `operacoes.py` (`git diff --stat main`);
  - Complexity Tracking continua vazio.

---

## Dependencies & Execution Order

**Fases**:

- Setup (T001–T004) → Foundational (T005–T013) → histórias.
- US1 (T014–T019) → US2 (T020–T023). O MVP institucional é US1 + US2.
- US3 (T024–T025) e US4 (T026–T027) dependem de US1/US2. Entre si, são sequenciais
  porque editam `consultas.py`.
- US5 (T028–T029) depende de US3, porque usa `campanhas_visiveis` no ramo de unidades.
- US6 (T030–T032) depende de US1–US5. As verificações cobrem todas as páginas existentes
  e são reexecutadas depois dos recortes (T056).
- US7 (T033–T035) → US8 (T036–T037) → US9 (T038–T039): recortes, em sequência.
- US10 (T040–T041) e US11 (T042–T043) dependem de US2. São sequenciais entre si porque
  compartilham `test_acompanhamento_estados.py` e `apresentacao.py`.
- US12 (T044–T045) depende de US3/US4.
- US13 (T046–T047) depende de US7 (tabela de recorte).
- Demonstração (T048–T051) depende de US1–US5 e US11. T050 e T051 tocam arquivos
  diferentes.
- Polish (T052–T058) por último.

**Dentro de cada história**: testes → implementação → checkpoint.

## Parallel Opportunities

- Foundational: T005, T006, T007 e T010 em paralelo (arquivos distintos). T013 em
  paralelo com T008–T012.
- US1: T014 ∥ T015.
- Testes de histórias diferentes em arquivos diferentes podem ser escritos em paralelo
  depois da Foundational: T024, T026, T028, T030, T031, T033, T040, T046, T048 e T049.
  A implementação continua sequencial nos arquivos compartilhados.
- Polish: T052 ∥ T053 ∥ T055.

```text
# Exemplo — depois da Foundational:
T014 test_acompanhamento_indicadores.py   ∥   T015 test_acompanhamento_lista.py
T024 test_acompanhamento_visibilidade.py  ∥   T028 test_acompanhamento_acesso.py
T048 test_demonstracao_operador.py        ∥   T049 test_acompanhamento_demonstracao.py
```

## Implementation Strategy

1. **MVP**: Setup + Foundational + US1 + US2. O CPAEG vê a lista e o detalhe com os
   quatro indicadores e as taxas.
2. **Escopo de unidade**: US3 → US4 → US5 → US12. Primeiro consumidor real da unidade do
   vínculo; recusa por URL direta.
3. **Garantias**: US6. Nenhuma escrita, nenhuma Resposta, anti-N+1.
4. **Recortes**: US7 → US8 → US9.
5. **Estados e instrumento**: US10, US11.
6. **Acessibilidade**: US13.
7. **Demonstração**: B/Vitória exercitável, com A/B/C intactos.
8. **Polish**: privacidade, escopo negativo, DP-1101 registrada, suíte completa,
   quickstart e revisão de over engineering.

Cada checkpoint mantém a suíte completa verde.

## Resumo

- **Total**: 58 tasks.
  - 4 de setup;
  - 9 de base;
  - 34 de histórias (US1–US13);
  - 4 de demonstração;
  - 7 de polish.
- **Tarefas de teste**: 22 (T004, T005, T006, T007, T014, T015, T020, T024, T026, T028,
  T030, T031, T033, T036, T038, T040, T042, T044, T046, T048, T049, T052; T053 estende
  um arquivo de teste).
- **Arquivos de produção novos** (`trajetoria/acompanhamento/`): `__init__.py`,
  `apps.py`, `consultas.py`, `apresentacao.py`, `acesso.py`, `views.py`, `urls.py` e
  cinco templates.
- **Arquivos de produção alterados**: `config/settings.py`, `config/urls.py`,
  `trajetoria/governanca/regras.py`, `trajetoria/demonstracao/cenario.py`,
  `trajetoria/demonstracao/views.py`,
  `trajetoria/demonstracao/templates/demonstracao/operador.html`, e a docstring de
  `trajetoria/demonstracao/middleware.py`.
- **Modelos/migrations/índices**: 0 / 0 / 0.

## Notas de implementação

Implementado em 2026-10-02. Todas as 58 tasks concluídas. Resultado: suíte completa com 1492
testes verdes (1321 anteriores + 171 novos), `ruff check` sem achados,
`makemigrations --check` sem mudanças, e roteiro manual do quickstart executado num banco local
de demonstração próprio (passos 1–5, 7–15).

Ajustes menores em relação ao texto das tasks, sem mudança de comportamento especificado:

- **Sem `tests/acompanhamento/__init__.py`** (T004): o repositório usa diretórios de teste sem
  `__init__.py`; os módulos têm prefixo único `test_acompanhamento_*`.
- **`Instrumento` e `instrumento()` ficaram em `consultas.py`**, junto de `CampanhaAcompanhada`
  (T017). Os avisos de estado são a propriedade `CampanhaAcompanhada.avisos`, e não uma função
  `avisos_do_estado` (T041). `Indicadores`, `percentual`, ordem e textos ficaram em
  `apresentacao.py`, como planejado.
- **`_universo(escopo)` e `_universo_participacao(escopo)` são privados** (T016/T027): dependem
  só do escopo, nunca do critério da Campanha (H1 da análise).
- **Rótulos de "não informado"** ficaram num dicionário `NAO_INFORMADO` por campo, em vez de um
  atributo do `Enum Recorte` (T034).
- **Faixa de ambiente própria** (`apresentacao.BANNER`), em vez de importar o texto do editor
  (T013): o texto do editor dizia "Este editor não está disponível…", impreciso no
  acompanhamento. O editor não mudou.
- **Templates auxiliares**: além dos cinco previstos, `_taxa.html`, `_periodo.html`,
  `_instrumento.html` e `estilo.css`, só para evitar repetição de marcação.
- **Campanha N** (simulação de 005/DP-507 e taxa > 100%) é montada dentro dos próprios testes
  (T014, T026), e não no cenário `ref`, para manter o `ref` estável.
- **Página de escolha de operador**: o texto passou a citar também o acompanhamento da coleta
  (T051), mantendo a frase verificada pelo teste da 010.

### Ajustes do code review (2026-10-02)

- **Oferta do recorte por unidade e coluna Unidade** passam a depender do escopo
  (institucional ou mais de uma unidade), e não das unidades relevantes da Campanha: com o
  universo pelo escopo (H1), uma Participação de outra unidade do escopo ficaria numa linha
  sem unidade. `unidades_relevantes` só define as linhas com zero.
- **Gate do acompanhamento** decide por `pode_acompanhar_coleta` (a regra nomeada) antes de
  derivar o escopo.
- **Identificação compartilhada**: `demonstracao.operador.vinculos_do_operador_em_uso` é o
  ponto único usado pelo editor e pelo acompanhamento (DP-1001 troca um lugar só). O editor
  mudou só nessas duas linhas; comportamento idêntico (suítes 009/010 verdes).
- **Recorte por curso**: unidade e curso são cabeçalhos de linha (`th scope="row"`).
- **Detalhe**: a Campanha visível é obtida numa consulta; a existência só é verificada na
  falta, para distinguir 404 de 403.
- **Um só "agora"** por requisição para o estado e para o momento exibido.
- **Preparo da demonstração**: `materializar()` uma vez; a baseline é repassada.
