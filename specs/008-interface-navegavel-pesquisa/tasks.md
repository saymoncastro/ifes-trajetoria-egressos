---

description: "Tasks da Feature 008 — Interface navegável mínima da pesquisa"
---

# Tasks: Interface navegável mínima da pesquisa

**Input**: Design documents from `specs/008-interface-navegavel-pesquisa/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/rotas.md](contracts/rotas.md),
[contracts/formulario-secao.md](contracts/formulario-secao.md),
[contracts/demonstracao.md](contracts/demonstracao.md), [quickstart.md](quickstart.md)

**Stack (confirmada; [ADR 0001](../../docs/adr/0001-stack-inicial.md))**: Python 3.13,
Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff. **Nenhuma dependência
nova. Zero modelos, zero migrações.** Dois apps novos sem `models.py`:
`trajetoria/interface/` e `trajetoria/demonstracao/`.

**Tests**: obrigatórios e escritos antes da implementação correspondente (test-first). A
feature toca invariantes constitucionais (associação de respostas, longitudinalidade,
condicionais, dado institucional ≠ declarado, privacidade, autorização da demonstração).
Testes de comportamento novo DEVEM falhar primeiro. Histórias que só verificam
comportamento entregue por história anterior (US6, US10, US11, US12, parte de US7) podem
passar de imediato; se falharem, a correção vai no módulo indicado, sem regra especial.

**Organization**: fases por história da spec (US1–US14), depois aceitação ponta a ponta,
fronteiras e polish. `trajetoria/interface/views.py` e cada arquivo de teste são editados
em sequência (um arquivo por vez).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US14).

## Convenções para todas as tarefas

- **Camada fina** ([research R1, R7, R8](research.md)): a interface chama **somente**
  `situacao_de_entrada` e `entrar` (007), `situacao_da_jornada` (006), `concluir` (006),
  `responder_escolha_unica`, `responder_escolha_multipla`, `responder_texto`,
  `responder_escala`, `remover_resposta` (005), e lê `conteudo_da_versao` (002),
  `Pergunta`/`Opcao`/`TipoPergunta` (002), `Participacao` (005) e `Pessoa`/
  `ConclusaoAcademica` (001). Usa `Saida` (de `percurso`) só para interpretar o destino.
  **Nunca** importa `trajetoria.campanha.*`, `trajetoria.fonte_academica.*`,
  `instrumento.operacoes`, `iniciar_participacao`, `percorrer`, `pendencias`; nunca chama
  `save`, `create`, `update`, `delete` em modelo; nunca passa `agora`.
- **Nada de regra por Pergunta**: nenhuma referência a Q1…Q54, a texto de Pergunta ou de
  Opção, a posição específica de Seção ou Pergunta, no código ou nos templates
  (FR-034, FR-051).
- **Nada persistido** além do que 005/006/007 gravam. Único estado entre requisições: o
  cookie `trajetoria_demonstracao_pessoa` (`set_signed_cookie`, `httponly=True`,
  `samesite="Lax"`, sem `max_age`) com o `pk` da Pessoa — "Revalidado a cada requisição:
  existe **e** `fonte == "simulada"`; senão é ignorado" ([data-model §2](data-model.md#2-estado-de-apresentação-entre-requisições)).
- **Formulário** ([contrato](contracts/formulario-secao.md)): campos `p<n>`,
  `p<n>-complemento`, `p<n>-remover`, por **posição** da Pergunta; valores de Opção =
  posição da Opção; **todos `required=False`**; `CharField(strip=False)`; "só espaços =
  ausente"; escolha única com "> 10 Opções" → lista suspensa com `("", "Selecione…")`
  primeiro (`LIMITE_RADIOS = 10`); `p<n>-remover` "só para `ESCOLHA_UNICA` em rádios e
  `ESCALA`, **com Resposta gravada**".
- **Textos ao egresso**: os de [data-model §4](data-model.md#4-mapeamento-de-estados-de-domínio-para-telas)
  e [contracts/rotas.md](contracts/rotas.md), literalmente; mensagens de campo em
  `trajetoria/interface/mensagens.py`. Nenhum UUID, `SIM-…`, nome de Campanha, nome de
  `Motivo` ou de modelo no texto renderizado.
- **Tempo**: a interface lê o relógio pelas operações. Nos testes, a fixture `relogio`
  (T008) substitui `django.utils.timezone.now`; padrão `NO_PERIODO`. Nenhum teste depende
  do relógio real.
- **Testes**: `tests/interface/` **sem** `__init__.py`; módulos com prefixo
  `test_interface_` (já existe `tests/test_aceitacao.py`); auxiliares em
  `tests/interface/construcao_interface.py`, que reutilizam
  `from tests.participacao import construcao as c` e
  `from tests.participacao import construcao_entrada as ce` **sem alterá-los**. Banco com
  `pytestmark = pytest.mark.django_db`. Pessoas sempre da **fonte simulada**
  (`ce.incorporar(FonteSimulada(), …)`), pois é a única aceita. Somente dados fictícios.

## Limites desta lista (não criar)

- Modelo, migração, tabela, coluna; `django.contrib.auth`, `sessions`, `messages`,
  `admin`, `staticfiles`, `contenttypes`.
- Login, senha, CPF, e-mail, OTP, link mágico, Gov.br, SSO, conta, usuário, perfil,
  `UsuarioDemo`, provedor ou resolvedor de identidade.
- SPA, React, Vue, Angular, API REST/GraphQL própria, `<script>`, bundler, framework CSS,
  design system, biblioteca de componentes, fonte ou recurso externo, animação.
- Sessão de jornada, cursor, progresso, percentual, Seção visitada, seleção ou formação
  persistida, rascunho de formulário não enviado.
- Wizard, form builder, motor de telas, componente genérico além dos quatro templates de
  tipo de Pergunta.
- Painel, CPAEG/CSAEG, gestão de Campanha, editor, publicação por tela, indicador,
  exportação, GeN, analytics, telemetria.
- Resumo de respostas, comprovante, certificado, PDF, download; reabrir, editar após
  concluir, nova tentativa; indicador de progresso.
- Pré-preenchimento, sugestão, ocultação ou remoção de Q10–Q19 ou de qualquer Pergunta.
- Alteração de código ou contrato das Features 001–007. **Única exceção em testes**:
  T003 (ajuste de `test_10` da 007).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar a base.

- [X] T001 Confirmar a base do branch: `git log --oneline -1 origin/main` contido no
  branch (007 incorporada — saymoncastro/ifes-trajetoria-egressos#9); rodar
  `uv run pytest`, `uv run ruff check .`, `uv run python manage.py check` e
  `uv run python manage.py makemigrations --check --dry-run`, registrar que estão verdes e
  limpos e anotar o número de testes e a lista `ls trajetoria/*/migrations/0*.py` para
  comparação em T049.

**Checkpoint**: suíte 001–007 verde.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: camada web mínima, apps vazios, modo de demonstração, template base,
apresentação do contexto e auxiliares de teste.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T002 Criar os pacotes dos apps, sem `models.py`:
  `trajetoria/demonstracao/{__init__.py,apps.py,urls.py}` (`DemonstracaoConfig`,
  `name="trajetoria.demonstracao"`, `urlpatterns = []`) e
  `trajetoria/interface/{__init__.py,apps.py,urls.py}` (`InterfaceConfig`,
  `name="trajetoria.interface"`, `urlpatterns = []`), mais
  `trajetoria/demonstracao/middleware.py` com `ModoDemonstracaoMiddleware`: para toda
  requisição, `if not settings.TRAJETORIA_DEMONSTRACAO: raise Http404` — "Nenhuma outra
  responsabilidade" ([contrato](contracts/demonstracao.md#trajetoriademonstracaomiddlewaremododemonstracaomiddleware)).
- [X] T003 [P] Ajustar `tests/participacao/test_entrada_aceitacao.py::test_10_nenhum_mecanismo_de_autenticacao`:
  restringir **somente** o laço `for app in RAIZ.glob("trajetoria/*/")` aos apps de domínio
  `("academico", "instrumento", "campanha", "participacao", "fonte_academica",
  "formulario_2024")`, com comentário citando a 008 (plan, "Necessidade de voltar…");
  manter intactas as demais asserções (sem `auth`/`sessions`; middleware sem "session" e
  "auth"; nenhuma rota `trajetoria.participacao`; `__all__` sem nomes proibidos).
- [X] T004 Alterar `config/settings.py` ([research R2](research.md#r2--camada-web-mínima-na-configuração)):
  `INSTALLED_APPS += ["trajetoria.interface", "trajetoria.demonstracao"]` (nenhum
  `django.contrib.*`) e comentário atualizado (restrições de não exposição continuam para
  egressos; a 008 expõe só em modo de demonstração); `MIDDLEWARE = [
  "django.middleware.security.SecurityMiddleware",
  "trajetoria.demonstracao.middleware.ModoDemonstracaoMiddleware",
  "django.middleware.common.CommonMiddleware",
  "django.middleware.csrf.CsrfViewMiddleware",
  "django.middleware.clickjacking.XFrameOptionsMiddleware"]`; `TEMPLATES` com
  `DjangoTemplates`, `APP_DIRS=True`, `context_processors=
  ["trajetoria.demonstracao.contexto.demonstracao"]`; `ALLOWED_HOSTS` de
  `DJANGO_ALLOWED_HOSTS` (padrão `"localhost,127.0.0.1,[::1]"`, separado por vírgula);
  `TRAJETORIA_DEMONSTRACAO = os.environ.get("TRAJETORIA_DEMONSTRACAO") == "1"`;
  `DEBUG = False` mantido; logger `"django.request": {"handlers": ["console"], "level":
  "ERROR"}`. Alterar `config/urls.py` para `urlpatterns = [path("",
  include("trajetoria.demonstracao.urls")), path("", include("trajetoria.interface.urls"))]`.
  Criar `trajetoria/demonstracao/contexto.py` com `demonstracao(request)` devolvendo
  `{}` quando `settings.TRAJETORIA_DEMONSTRACAO` é falso (sem ler cookie nem consultar o
  banco) e, ligado, `{"modo_demonstracao": True, "pessoa_demonstracao":
  pessoa_em_uso(request)}`; e
  `trajetoria/demonstracao/entrada.py` com o esqueleto de `pessoa_em_uso` (implementado em
  T012) devolvendo `None`. `uv run python manage.py check` limpo.
- [X] T005 [P] Criar `trajetoria/interface/templates/interface/estilo.css` ([R13, R14](research.md#r14--estilo-uma-folha-css-inline-sem-staticfiles)):
  coluna única `max-width: 40rem`, fluida, `font-family: system-ui, sans-serif`, base
  `1rem`, unidades relativas, sem larguras fixas acima de 320px; alvos de toque ≥ 44px
  (rótulos de rádio/caixa em bloco com área clicável); paleta: texto `#1b1b1b` sobre
  `#ffffff`; botão primário `#ffffff` sobre `#1a4480`; erro `#b50909`; faixa de
  demonstração `#1b1b1b` sobre `#fff1d2`; bordas `#565c65`; `:focus-visible` com contorno
  escuro + halo amarelo; erros com borda e texto (não só cor); sem animações, `@import` ou
  fontes externas.
- [X] T006 Criar `trajetoria/interface/templates/interface/base.html`: `<html
  lang="pt-BR">`; `<title>{% block titulo %}{% endblock %} — Trajetória Ifes
  (demonstração)</title>` (blocos permitem o prefixo "Erro: "); `<style>{% include
  "interface/estilo.css" %}</style>`; primeiro focável "Pular para o conteúdo" → `#conteudo`;
  faixa `role="note"` com o texto exato de [contracts/demonstracao.md](contracts/demonstracao.md#faixa-de-demonstração-template-base);
  `<header>` com nome da `pessoa_demonstracao` (ou nada) e formulários POST "Trocar de
  pessoa" e "Encerrar demonstração" para `/demonstracao/encerrar/` com `{% csrf_token %}`;
  `<main id="conteudo">{% block conteudo %}`; `<footer>`. Nenhum `<script>`. Criar também
  `trajetoria/interface/templates/interface/aviso.html` (estende a base; blocos de título
  e mensagem; ligação "Voltar às suas formações" → `/formacoes/`) e os templates de erro
  **autônomos** — não herdam `interface/base.html`, sem faixa de demonstração, sem
  cabeçalho de Pessoa, sem variáveis do processador de contexto; cada um com `<html
  lang="pt-BR">`, `<title>`, atalho "Pular para o conteúdo", `<main id="conteudo">` com
  um `h1`, a folha `estilo.css` incluída e uma ligação para `/` (passam no verificador de
  T037):
  `trajetoria/interface/templates/404.html` ("Página não encontrada."), `500.html`
  (estático, sem contexto: "Não foi possível concluir a operação. Tente novamente.") e
  `403_csrf.html` ("Não foi possível confirmar o envio. Volte à página anterior,
  recarregue e tente novamente.").
- [X] T007 [P] Criar `trajetoria/interface/apresentacao.py` com
  `contexto_da_formacao(conclusao) -> list[tuple[str, str]]` — pares "**só** para
  atributos informados, nesta ordem: Curso, Unidade, Ano de conclusão (ou data, se
  informada), Nível, Modalidade, Forma de oferta. Atributo `None` é omitido"
  ([data-model §3](data-model.md#itemcontexto-contexto-da-formação)); data formatada
  `dd/mm/aaaa`. E o teste puro (sem banco, com `ConclusaoAcademica` não gravada) no início
  de `tests/interface/test_interface_formacoes.py`: todos os atributos; nenhum (lista
  vazia); só curso; data prevalece sobre ano; nenhum valor inventado.
- [X] T008 [P] Criar `tests/interface/conftest.py` e `tests/interface/construcao_interface.py`:
  - fixture **autouse** `modo_demonstracao(settings)` → `settings.TRAJETORIA_DEMONSTRACAO =
    True`;
  - fixture `relogio(monkeypatch)` → objeto com `.agora` (padrão `c.NO_PERIODO`) e
    `monkeypatch.setattr("django.utils.timezone.now", lambda: relogio.agora)`;
  - `entrar_como(client, pessoa)` → POST `/demonstracao/escolher/`;
  - `cenario_baseline()` → `c.baseline_publicada()` + `c.campanha_aberta(base.versao)`
    (população ampla) + incorporação `ce.incorporar(FonteSimulada(), "SIM-P-0001",
    "SIM-P-0003", "SIM-P-0010", "SIM-P-0011")`; devolve objeto com `base`, `campanha` e
    `pessoa(id_externo)`;
  - `dados_validos(secao, escolhas=None)` → `dict` de POST que responde **todas** as
    Perguntas obrigatórias de um `ConteudoSecao` (primeira Opção, ponto inicial da escala,
    texto `"Resposta fictícia"`), substituindo as escolhas indicadas por texto de Opção
    (`{"Q14": "Graduação"}` é traduzido para a posição pela `Baseline` dos testes — o
    mapeamento Q→Pergunta existe **só** nos testes);
  - `percorrer_pela_interface(client, participacao, escolhas)` → envia Seção a Seção,
    seguindo os `Location`, e devolve a lista de posições de Seção apresentadas e a última
    URL;
  - `texto_visivel(resposta)` → texto do HTML sem tags, via `html.parser`;
  - `PADROES_TECNICOS` (regex de UUID, `SIM-`, nomes de `Motivo`, `"simulada"`,
    `"Demonstração — coleta"`).

**Checkpoint**: `uv run python manage.py check` limpo; com o modo ligado, `/` responde 404
(sem rotas ainda); suíte 001–007 verde com T003.

---

## Phase 3: User Story 1 — Entrar em modo de demonstração com uma Pessoa fictícia (Priority: P1) 🎯 MVP

**Goal**: entrada de demonstração com Pessoas da fonte simulada, cookie revalidado, modo
desligado = 404, e o cenário de demonstração preparado por comando.

**Independent Test**: preparar o cenário; abrir `/demonstracao/`; escolher "Maria
Exemplo"; ver `/formacoes/` dela; trocar; desligar o modo e ver 404 em tudo.

### Tests for User Story 1 ⚠️

- [X] T009 [P] [US1] Criar `tests/interface/test_interface_demonstracao.py` (test-first):
  - **modo desligado** (`settings.TRAJETORIA_DEMONSTRACAO = False`): GET e POST em `/`,
    `/demonstracao/`, `/demonstracao/escolher/`, `/demonstracao/encerrar/`, `/formacoes/`,
    `/formacoes/entrar/`, `/participacoes/<uuid4>/`, `.../secoes/1/`, `.../concluir/`,
    `.../concluida/` → 404, sem nada do domínio no corpo; **com um cookie válido de Pessoa
    de demonstração** (gravado com o modo ligado e reaproveitado com o modo desligado), o
    404 não contém o nome da Pessoa, a faixa "Ambiente de demonstração" nem "Trocar de
    pessoa", e o processador de contexto não consulta o banco
    (`django_assert_num_queries(0)` na requisição);
  - `/demonstracao/` lista só Pessoas `fonte == "simulada"` (criar uma `Pessoa(fonte=
    "teste-interface")` e verificar ausência); ordem por nome e `pk`; SIM-P-0009 aparece
    como "Pessoa fictícia sem nome informado"; as duas "Carla Exemplo" distintas pelo
    resumo das formações; faixa "Ambiente de demonstração." em todas as páginas;
    `texto_visivel` sem `PADROES_TECNICOS`; sem Pessoas → mensagem de preparo;
  - POST `/demonstracao/escolher/` com Pessoa simulada → 302 `/formacoes/`, cookie
    presente, `ce.linhas()` inalterado; com Pessoa de outra fonte ou `pk` inexistente/
    malformado → 404, sem cookie; GET → 405;
  - `/` sem cookie → 302 `/demonstracao/`; com cookie → 302 `/formacoes/`;
  - `/formacoes/` com cookie adulterado, de Pessoa removida ou de Pessoa de outra fonte
    (cookie assinado forjado com `django.core.signing`) → 302 `/demonstracao/`;
  - POST `/demonstracao/encerrar/` → cookie apagado, 302 `/demonstracao/`.
- [X] T010 [P] [US1] Criar `tests/interface/test_interface_cenario.py` (test-first) para
  `manage.py preparar_demonstracao` (via `call_command`, com `relogio`):
  - modo desligado → `CommandError` com a mensagem do contrato; nada criado;
  - banco com `Pessoa` ou `ConclusaoAcademica` de outra fonte → `CommandError`; nada
    alterado;
  - execução: 9 Pessoas simuladas materializadas (SIM-P-0006 e SIM-P-0008 não); baseline
    da 003 continua `RASCUNHO`; Versão `"Demonstração — cópia da referência 2024"`
    `PUBLICADA`; as duas Campanhas EM COLETA, período `hoje`…`hoje + 180 dias`, critérios
    exatamente os do contrato; 0 `Participacao`, 0 `Resposta`;
  - situações (pela 007, `situacao_de_entrada`) iguais à tabela de
    [research R17](research.md#r17--cenário-de-demonstração-comando-preparar_demonstracao):
    Ana `ENTRADA_RESOLVIDA`; Maria `SELECAO_NECESSARIA`; Diego `ENTRADA_RESOLVIDA` com
    Mestrado `AMBIGUIDADE_OPERACIONAL` e Técnico `SEM_PESQUISA`; Bruno e Carla
    (Pedagogia) `SEM_PESQUISA`; Carla (Redes), Elisa, Fernanda e sem nome
    `ENTRADA_RESOLVIDA`;
  - idempotência: segunda execução não muda as contagens de `Pessoa`, `ConclusaoAcademica`,
    `Versao`, `Campanha`;
  - Campanha de demonstração encerrada (`encerrar` da 004) → nova execução recusa com a
    mensagem "Recrie o banco local…";
  - a saída impressa contém os nomes e nenhum `PADROES_TECNICOS`.

### Implementation for User Story 1

- [X] T011 [US1] Implementar `trajetoria/demonstracao/entrada.py` conforme
  [contrato](contracts/demonstracao.md#trajetoriademonstracaoentrada): `COOKIE`,
  `pessoa_em_uso(request)` (`get_signed_cookie(COOKIE, default=None, salt=…)`; Pessoa por
  `pk` válido com `fonte == FonteSimulada.codigo`; qualquer falha → `None`, sem exceção),
  `pessoas_de_demonstracao()` (fonte simulada, `prefetch_related("conclusoes")`, ordem
  `F("nome").asc(nulls_last=True), "pk"`), `usar(response, pessoa)` (`ValueError` se outra
  fonte) e `esquecer(response)`.
- [X] T012 [US1] Implementar `trajetoria/demonstracao/views.py`, `urls.py` e
  `templates/demonstracao/entrada.html`: `entrada` (`require_GET`; lista com
  `nome_apresentado` e resumos "curso · unidade · ano" a partir de
  `contexto_da_formacao`; um formulário POST por Pessoa com `pessoa=<pk>` e botão "Entrar
  como <nome>"; mensagem quando vazia); `escolher` (`require_POST`; 404 se não for da
  fonte simulada; `usar`; 302 `/formacoes/`); `encerrar` (`require_POST`; `esquecer`; 302
  `/demonstracao/`); `inicio` em `trajetoria/interface/views.py` (`require_GET`, `/`).
  T009 passa.
- [X] T013 [US1] Implementar `trajetoria/demonstracao/cenario.py` (`preparar() -> Resumo`)
  e `trajetoria/demonstracao/management/{__init__.py,commands/__init__.py,
  commands/preparar_demonstracao.py}` conforme
  [contrato](contracts/demonstracao.md#comando-managepy-preparar_demonstracao): recusas
  antes de qualquer escrita; `incorporar_pessoa(FonteSimulada(), id)` para
  `cenarios.PESSOAS`; `materializar()`; cópia + `publicar` se ausente; Campanhas por nome
  com `criar_campanha`, `definir_periodo(hoje, hoje + timedelta(days=180))` (`hoje =
  timezone.localdate()`), `definir_criterios`, `abrir`; Campanha existente fora de
  `EM_COLETA` → recusa; resumo com nome e situação calculada por `situacao_de_entrada`. O
  comando só traduz `Resumo` em texto e recusas em `CommandError`. T010 passa.

**Checkpoint**: `TRAJETORIA_DEMONSTRACAO=1 manage.py preparar_demonstracao` + `runserver`
mostram a entrada de demonstração com as Pessoas fictícias.

---

## Phase 4: User Story 2 — Ver as formações e resolver a formação com pesquisa pendente (Priority: P1)

**Goal**: a tela de formações reproduz a situação de entrada da 007.

**Independent Test**: para Pessoas em cada situação global, a tela coincide com
`situacao_de_entrada`; nada é gravado.

### Tests for User Story 2 ⚠️

- [X] T014 [US2] Acrescentar a `tests/interface/test_interface_formacoes.py` (após os
  testes puros de T007), com Pessoas da fonte simulada e Campanhas montadas por
  `c.campanha_aberta(versao, **criterios)`:
  - `ENTRADA_RESOLVIDA` (SIM-P-0001, população ampla): "Esta pesquisa refere-se à sua
    formação:" + contexto (Curso, Unidade, Ano); **um** botão "Iniciar a pesquisa", sem
    campo `formacao`; com Participação em rascunho (via `ce.participacao_em_rascunho`) o
    botão é "Continuar a pesquisa";
  - `SELECAO_NECESSARIA` (SIM-P-0003): "Sobre qual formação do Ifes você responderá esta
    pesquisa?"; um botão por formação, cada um com `formacao=<pk>` oculto, na ordem da 007;
    nenhuma palavra "sugerida", "principal", "recomendada";
  - `SEM_PESQUISA` (sem Campanha): "No momento, não há pesquisa disponível para as suas
    formações."; formações listadas; nenhum botão de entrada;
  - `SEM_ENTRADA_PENDENTE` (única formação concluída via `ce.participacao_concluida`):
    "Não há pesquisa pendente para você neste momento."; "Pesquisa já respondida.";
  - outras formações em "Suas outras formações" com os textos de
    [data-model §4](data-model.md#situação-de-entrada-007--tela-de-formações);
  - `SEM_FORMACAO` (Pessoa simulada sem Conclusões, criada por ORM com `fonte="simulada"`
    só neste teste): "Não encontramos formações concluídas no Ifes associadas a você.";
  - atributo `None` omitido; nome da Campanha e `PADROES_TECNICOS` ausentes do texto;
  - GET não grava (`ce.linhas()` antes/depois); `?aviso=situacao` mostra a faixa; `?aviso=x`
    é ignorado; POST → 405; `Cache-Control` com `no-store`; sem Pessoa → 302
    `/demonstracao/`;
  - `django_assert_max_num_queries` com teto fixo (definido na implementação, ≤ 15) para
    Pessoa de 3 formações.

### Implementation for User Story 2

- [X] T015 [US2] Implementar em `trajetoria/interface/views.py` a view `formacoes`
  (`require_GET`, `never_cache`; Pessoa por `pessoa_em_uso` ou 302 `/demonstracao/`;
  `situacao_de_entrada(pessoa)`; contexto: resolução, `pendentes`, demais formações, cada
  uma com `contexto_da_formacao` e texto de situação) e
  `trajetoria/interface/templates/interface/formacoes.html` com as cinco variações e os
  formulários POST para `/formacoes/entrar/`; rota `formacoes/` em
  `trajetoria/interface/urls.py`. T014 passa.

---

## Phase 5: User Story 3 — Iniciar ou retomar a Participação (Priority: P1)

**Goal**: "Iniciar"/"Continuar" chamam só `entrar` (007) e levam à Seção atual.

**Independent Test**: com SIM-P-0001, iniciar cria exatamente uma Participação e leva à
Seção 1; repetir não cria outra.

### Tests for User Story 3 ⚠️

- [X] T016 [US3] Criar `tests/interface/test_interface_entrada.py` (test-first):
  - POST `/formacoes/entrar/` sem `formacao` (entrada resolvida) → 1 Participação do par →
    302 `/participacoes/<id>/` → 302 `.../secoes/1/`; repetir → mesma Participação,
    contagem 1;
  - seleção: com `formacao` de cada formação de SIM-P-0003 → duas Participações distintas;
  - `formacao` de outra Pessoa, inexistente ou malformada → 404 "Formação não disponível",
    `ce.linhas()` inalterado, sem dados da outra formação no corpo;
  - entrada sem formação em `SELECAO_NECESSARIA` ou com formação `SEM_PESQUISA` → 302
    `/formacoes/?aviso=situacao`, nada criado;
  - formação já concluída informada → 200 "Esta pesquisa já foi respondida.", nada criado;
  - Campanha encerrada entre a tela e a ação (`relogio.agora = c.DEPOIS_DO_FIM`) → 302
    `/formacoes/?aviso=situacao`, nada criado;
  - mapeamento de `ParticipacaoRejeitada` (só a tradução; `monkeypatch` de
    `trajetoria.interface.views.entrar` levantando `ParticipacaoRejeitada((coleta_nao_admitida(),))`)
    → 200 "O período de resposta desta pesquisa foi encerrado.";
  - GET `/formacoes/entrar/` → 405; POST sem CSRF com `Client(enforce_csrf_checks=True)` →
    403 com o texto de `403_csrf.html`;
  - GET `/participacoes/<id>/` de Participação alheia ou inexistente → 404; concluída →
    302 `/concluida/`; jornada finalizada → 302 `/concluir/`; Campanha encerrada → 200
    "período encerrado".

### Implementation for User Story 3

- [X] T017 [US3] Implementar em `trajetoria/interface/views.py`: auxiliar
  `_participacao_da_pessoa(request, pk)` (Pessoa ou redirecionamento;
  `Participacao.objects.select_related("campanha__versao", "conclusao").filter(pk=pk,
  conclusao__pessoa=pessoa).first()` ou `Http404`); `_jornada(participacao)` (chama
  `situacao_da_jornada`; `ParticipacaoRejeitada` com `ESTRUTURA_NAO_SUPORTADA` →
  resposta "Esta pesquisa não está disponível no momento."); `_aviso(request, tipo)` que
  renderiza `interface/aviso.html` com os textos "já respondida", "período encerrado",
  "pesquisa indisponível", "formação não disponível" (404); view `entrar_view`
  (`require_POST`, `never_cache`; mapeamento exato de
  [contracts/rotas.md](contracts/rotas.md#post-formacoesentrar--exige-pessoa));
  view `participacao` (`require_GET`; tabela de
  [GET /participacoes/<participacao>/](contracts/rotas.md#get-participacoesparticipacao));
  rotas `formacoes/entrar/` e `participacoes/<uuid:participacao>/`. T016 passa.

---

## Phase 6: User Story 4 — Visualizar e responder a Seção atual (Priority: P1)

**Goal**: a Seção do percurso é apresentada com os quatro tipos, complemento,
obrigatoriedade e contexto, derivada só do instrumento.

**Independent Test**: com a cópia publicada da baseline, abrir S1, S2, S3, S8, S10 e S11
(alcançadas gravando respostas pela 005) e conferir controles e textos.

### Tests for User Story 4 ⚠️

- [X] T018 [US4] Criar `tests/interface/test_interface_secao.py` (test-first), com
  `cenario_baseline()` e respostas gravadas pela 005 para alcançar cada Seção:
  - S1: `h1` com o título da Versão; `texto_abertura` presente (só na primeira Seção);
    Q1 como `fieldset` + `legend` com o enunciado e "(obrigatória)"; rádios "Sim"/"Não";
    nenhum "Q1" no texto;
  - escolha múltipla com "Outro:" (S8): caixas de seleção + campo `p<n>-complemento`
    rotulado "Descreva: «Outro:»"; escala (S8): rádios `1..5`, descrição "5 = Concordo
    totalmente", **nenhum** rótulo para o ponto 1 (rótulo inicial ausente); texto curto
    (S3, Q10): `label for` + `input` de uma linha;
  - escolha única com mais de 10 Opções (S3 ou S6): `<select>` com "Selecione…"; com até
    10: rádios;
  - texto explicativo (Q10, Q32, Q48) associado por `aria-describedby`;
  - S11: Q46, Q47, Q48 juntas, nessa ordem, com Q46 = "Não" gravada;
  - S3: nenhum `checked`/`selected`/`value` vindo da Conclusão (unidade "Serra", curso,
    ano não pré-preenchidos); região "Sobre a sua formação" separada das Perguntas;
  - Seção sem título (S13): sem `h2` inventado;
  - `p<n>-remover` presente só para escolha única em rádio/escala com Resposta gravada;
  - Seção fora do percurso (S9 com Q33 = "Não") e posição inexistente (99) → 302 Seção
    atual com `?aviso=percurso`; faixa do aviso exibida;
  - "Salvar e continuar" é o **primeiro** `<button type="submit">` do formulário;
  - Participação alheia → 404; `Cache-Control` `no-store`; `<form method="post">` com
    `csrfmiddlewaretoken`.

### Implementation for User Story 4

- [X] T019 [US4] Implementar `trajetoria/interface/formularios.py`: `LIMITE_RADIOS = 10`;
  `FormularioDaSecao(secao: ConteudoSecao, respostas: dict, data=None)` construindo os
  campos de [contracts/formulario-secao.md](contracts/formulario-secao.md#campos)
  (`ChoiceField`/`MultipleChoiceField`/`CharField(strip=False)`/`TypedChoiceField(coerce=int)`,
  todos `required=False`; `initial` só de `respostas`); validação de forma em
  `clean()`: Opção/ponto inexistente → mensagens de `mensagens.py`; "Complemento presente
  sem a Opção que o admite marcada (inclusive sem nenhuma Opção)" → "Para descrever,
  marque a opção «<texto da Opção>»."; "só espaços = ausente" para texto e complemento;
  método `perguntas()` que devolve, por Pergunta, o `ConteudoPergunta`, os
  `BoundField`s e o modo de apresentação (rádio, lista, caixas, texto, escala). Criar
  `trajetoria/interface/mensagens.py` com os textos de
  [data-model §4](data-model.md#rejeições-da-005006--mensagens).
- [X] T020 [US4] Implementar a view `secao` (GET) em `trajetoria/interface/views.py` e os
  templates `trajetoria/interface/templates/interface/secao.html` e
  `interface/perguntas/{escolha_unica,escolha_multipla,texto_curto,escala}.html`
  ([R13](research.md#r13--acessibilidade-padrões-html-sem-javascript)): `require_http_methods(["GET",
  "POST"])` (POST em T025), `never_cache`; tabela de
  [GET secoes](contracts/rotas.md#get-participacoesparticipacaosecoesposicao); `conteudo_da_versao`
  para título e `texto_abertura` (`linebreaks`); elemento `id="p<n>"` por Pergunta;
  `aria-describedby` para explicativo, descrição da escala e erro; `aria-required` nos
  obrigatórios; `aria-invalid` com erro; faixa `?aviso=percurso`; ligação "Sair e
  continuar depois" → `/formacoes/` com a nota do contrato; rota
  `participacoes/<uuid:participacao>/secoes/<int:posicao>/`. T018 passa.

---

## Phase 7: User Story 5 — Salvar respostas e avançar segundo a jornada (Priority: P1)

**Goal**: o envio vira operações da 005 (atômicas), e a próxima tela vem da 006.

**Independent Test**: S1 = "Sim" → S2; obrigatória em branco em S2 → S2 com pendência e
demais respostas gravadas; valor adulterado → nada gravado.

### Tests for User Story 5 ⚠️

- [X] T021 [P] [US5] Criar `tests/interface/test_interface_gravacao.py` (test-first) para
  `salvar_secao` diretamente e pela rota:
  - registrar, substituir e remover nos quatro tipos, com e sem complemento; o valor
    gravado é exatamente o enviado (texto com espaços nas bordas preservado);
  - "Só espaços" em texto/complemento = ausente; nenhuma Opção = remoção;
    `p<n>-remover` remove mesmo com Opção marcada;
  - reenviar a Seção sem mudança → nenhuma operação (espiar `responder_*`/`remover_resposta`
    com `monkeypatch` que repassa a chamada e conta) e `c.retrato()` igual;
  - **atomicidade pela 005**: chamar `salvar_secao` com valores limpos forjados — primeira
    Pergunta válida, segunda escala `99` — → `erros_por_pergunta` com a posição da
    segunda, `retrato()` igual ao anterior (a primeira **não** ficou gravada);
  - todos os erros de uma vez (duas Perguntas inválidas → duas mensagens);
  - complemento sem a Opção (com e sem nenhuma Opção) → mensagem com «Outro:», nada
    gravado;
  - pela rota: Opção adulterada (`p1=99`) → 200, valores reapresentados, resumo "Há
    problemas nesta seção" com ligações `#p<n>`, título começando com "Erro:", `retrato()`
    igual;
  - campos alheios (`p99`, `p1-x`, `formacao`) ignorados;
  - POST de Seção fora do percurso → 302 Seção atual `?aviso=percurso`, nada gravado;
  - Participação concluída entre GET e POST → 200 "já respondida", nada gravado.
- [X] T022 [P] [US5] Criar `tests/interface/test_interface_navegacao.py` (test-first) com a
  parte de avanço:
  - S1 = "Sim" → 302 `.../secoes/2/`; seguir o `Location` não regrava (`retrato()` igual
    após GET);
  - S2 com uma obrigatória em branco → 302 `.../secoes/2/?pendencias=1`; o GET mostra
    "Esta pergunta é obrigatória." **exatamente** nas Perguntas de `Passagem.pendentes` e as
    demais respostas gravadas;
  - `?pendencias=1` numa Seção satisfeita ou não atual → nenhuma pendência mostrada;
  - destino da Seção enviada = destino da 006 (comparar com
    `situacao_da_jornada(p).passagens`), inclusive encaminhamento S6 → S8;
  - última Seção satisfeita → 302 `/concluir/`.

### Implementation for User Story 5

- [X] T023 [US5] Implementar `trajetoria/interface/gravacao.py`:
  `ResultadoDaGravacao(erros_por_pergunta: dict[int, list[str]], motivo_global: Motivo |
  None, operacoes: int)` e `salvar_secao(participacao, secao, limpos, respostas)` conforme
  [contrato](contracts/formulario-secao.md#gravação-salvar_secaoparticipacao-secao-limpos-respostas---resultadodagravacao):
  leitura de `Pergunta`/`Opcao` por posição; decisão de no máximo uma operação por
  Pergunta; comparação com a Resposta atual (Opção, conjunto, texto, inteiro **e**
  complemento); `transaction.atomic()` externo; `ParticipacaoRejeitada` capturada por
  Pergunta fora do bloco interno; motivos globais interrompem; qualquer erro →
  `transaction.set_rollback(True)` e `operacoes = 0`; sem `agora`.
- [X] T024 [US5] Implementar o POST da view `secao` em `trajetoria/interface/views.py`
  seguindo os passos 1–4 de
  [POST secoes](contracts/rotas.md#post-participacoesparticipacaosecoesposicao):
  jornada; formulário; `salvar_secao`; jornada de novo; `Passagem` da Seção → `?pendencias=1`,
  Seção de destino (posição pelo `ConteudoVersao`) ou `/concluir/` via `Saida.FINALIZACAO`;
  e o GET com `?pendencias=1` (pendências só se a Seção é a última de `passagens` e tem
  `pendentes`). T021 e T022 passam.

**Checkpoint**: MVP navegável — entrar, iniciar, responder e avançar pela baseline.

---

## Phase 8: User Story 6 — Retomar um rascunho mantendo as respostas (Priority: P1)

**Goal**: sair e voltar devolve a Seção atual com as respostas gravadas.

**Independent Test**: responder até o meio de S9, encerrar a demonstração, voltar e ver
S9 com as respostas.

### Tests for User Story 6 ⚠️

- [X] T025 [US6] Acrescentar a `tests/interface/test_interface_secao.py`:
  - valores restaurados nos quatro tipos e no complemento (Opção `checked`, Opções
    `checked`, `value` do texto exatamente como gravado, ponto da escala `checked`,
    `<option selected>` na lista, complemento);
  - fluxo: responder até S9 parcialmente → POST `/demonstracao/encerrar/` → escolher a mesma
    Pessoa → `/formacoes/` mostra "Continuar a pesquisa" → POST → S9 com as respostas;
    `ce.linhas()` igual antes e depois da retomada;
  - troca de ramo e volta (Q33 "Sim" → "Não" → "Sim" por revisita de S8) → respostas de S9
    reaparecem sem redigitação;
  - valores digitados e não enviados não existem após sair.

### Implementation for User Story 6

- [X] T026 [US6] Se algum teste de T025 falhar, corrigir `initial` em
  `trajetoria/interface/formularios.py` ou o template do tipo correspondente em
  `trajetoria/interface/templates/interface/perguntas/`; nenhuma regra nova.

---

## Phase 9: User Story 7 — Percorrer os ramos reais da baseline (Priority: P1)

**Goal**: os ramos de Q1, Q14, Q33 e Q46 vêm da 006 porque estão na Versão.

**Independent Test**: as 17 combinações pela interface coincidem com os percursos da 003;
uma Versão diferente também é seguida sem mudança da interface.

### Tests for User Story 7 ⚠️

- [X] T027 [US7] Acrescentar a `tests/interface/test_interface_navegacao.py`:
  - **SC-004**: `@pytest.mark.parametrize` sobre as 17 combinações (Q1 = "Não"; Q1 = "Sim"
    × Q14 ∈ 4 Opções × Q33 ∈ {"Sim", "Não"} × Q46 ∈ {"Sim", "Não"}), com
    `percorrer_pela_interface` e `dados_validos`; a lista de Seções apresentadas é igual a
    `c.secoes_esperadas(**escolhas)` e termina em `/concluir/`;
  - **SC-005**: com `c.instrumento()` da 005 (regra de finalização em S1, duas Seções,
    quatro tipos), uma Campanha e uma Pessoa simulada, a sequência de telas segue
    `situacao_da_jornada` (finaliza em S1 com "Não"; vai a S2 com "Sim"), sem mudança da
    interface;
  - revisitar S3 e trocar Q14 de "Graduação" para "Pós-Graduação" → destino S7; as
    respostas de S6 não aparecem no percurso nem na tela;
  - "Voltar à seção anterior" aponta para a Passagem anterior em `passagens` (S8 → S6 no
    ramo Graduação), ausente na primeira Seção, com a nota "Alterações não salvas nesta
    página serão descartadas."; seguir a ligação não grava.

### Implementation for User Story 7

- [X] T028 [US7] Acrescentar à view `secao` (GET) em `trajetoria/interface/views.py` a
  Seção anterior do percurso (Passagem anterior em `passagens`, nunca ordem da Versão) e,
  em `trajetoria/interface/templates/interface/secao.html`, a ligação "Voltar à seção
  anterior" com a nota do contrato. T027 passa.

---

## Phase 10: User Story 8 — Concluir a pesquisa (Priority: P1)

**Goal**: tela de conclusão quando a 006 indica jornada finalizada; conclusão só por
`concluir`.

**Independent Test**: percurso completo → tela de conclusão → concluir → `concluida_em`
gravado pela 006.

### Tests for User Story 8 ⚠️

- [X] T029 [US8] Criar `tests/interface/test_interface_conclusao.py` (test-first):
  - GET `/concluir/` com jornada não finalizada → 302 Seção atual; finalizada → 200 com
    "Você chegou ao fim da pesquisa. Depois de concluída, ela não poderá ser alterada.",
    lista de Seções de `passagens` com ligações (S13 como "Seção 13"), botão "Concluir
    pesquisa", contexto da formação, **nenhum** valor declarado (texto fictício digitado
    ausente do corpo);
  - POST → `concluida_em` preenchido, Respostas fora do percurso removidas (pela 006),
    302 `/concluida/`; segundo POST → 302 `/concluida/`, `concluida_em` igual;
  - pendência criada entre GET e POST (remover uma obrigatória pela 005) → 302 Seção atual
    `?pendencias=1`, nada concluído;
  - Versão com duas Perguntas com regra na mesma Seção (`c.versao_publicada_de(secao_mem(
    pergunta_mem(regras=…), pergunta_mem(regras=…)), …)`) → GET Seção/concluir → "Esta
    pesquisa não está disponível no momento.", sem traceback;
  - Q1 = "Não" → S1 enviada → 302 `/concluir/` → concluir → 1 Resposta; nenhuma tela com
    "consentimento", "recusa", "opt-out".

### Implementation for User Story 8

- [X] T030 [US8] Implementar a view `concluir_view` (GET/POST, `never_cache`) em
  `trajetoria/interface/views.py` e
  `trajetoria/interface/templates/interface/conclusao.html` conforme
  [GET](contracts/rotas.md#get-participacoesparticipacaoconcluir) e
  [POST](contracts/rotas.md#post-participacoesparticipacaoconcluir) (precedência coleta →
  estrutura/incoerência → pendência); rota `participacoes/<uuid:participacao>/concluir/`.
  T029 passa.

---

## Phase 11: User Story 9 — Visualizar a confirmação de conclusão (Priority: P1)

**Goal**: confirmação simples, sem respostas nem comprovante.

**Independent Test**: concluir e ver "Pesquisa concluída", agradecimento, contexto e
texto de encerramento; nada mais.

### Tests for User Story 9 ⚠️

- [X] T031 [US9] Acrescentar a `tests/interface/test_interface_conclusao.py`: GET
  `/concluida/` de concluída → "Pesquisa concluída", "Obrigado pela sua participação.",
  contexto da formação, `texto_encerramento` da Versão; sem valores declarados, sem
  data/hora de conclusão, sem "comprovante", "certificado", "protocolo", "download",
  "editar", "reabrir"; ligação única "Voltar às suas formações"; rascunho → 302
  `/participacoes/<id>/`.

### Implementation for User Story 9

- [X] T032 [US9] Implementar a view `concluida` (`require_GET`, `never_cache`) em
  `trajetoria/interface/views.py` e
  `trajetoria/interface/templates/interface/concluida.html` conforme
  [contrato](contracts/rotas.md#get-participacoesparticipacaoconcluida); rota
  `participacoes/<uuid:participacao>/concluida/`. T031 passa.

**Checkpoint**: todas as histórias P1 entregues.

---

## Phase 12: User Story 10 — Informar Participação já concluída (Priority: P2)

**Goal**: concluída nunca reabre formulário.

**Independent Test**: após concluir, todas as rotas informam "já respondida" e a
Participação fica idêntica.

### Tests for User Story 10 ⚠️

- [X] T033 [US10] Acrescentar a `tests/interface/test_interface_conclusao.py`, após
  concluir: `/formacoes/` → "Pesquisa já respondida." sem botão para a formação; GET de
  cada Seção do percurso → "Esta pesquisa já foi respondida.", sem `<form>` de Seção nem
  valores; POST de Seção com dados antigos → mesma mensagem, `c.retrato()` igual; GET
  `/concluir/` → 302 `/concluida/`; POST `/formacoes/entrar/` com a formação → "já
  respondida", nenhuma Participação nova; nenhuma ligação "reabrir"/"editar" em nenhuma
  tela. Se falhar, corrigir em `trajetoria/interface/views.py` (T017/T024/T030), sem
  regra nova.

---

## Phase 13: User Story 11 — Informar ausência de pesquisa disponível (Priority: P2)

**Goal**: sem pesquisa, mensagem clara e nenhum formulário.

**Independent Test**: Pessoa sem Campanha aplicável → mensagem e nenhuma ação.

### Tests for User Story 11 ⚠️

- [X] T034 [US11] Acrescentar a `tests/interface/test_interface_formacoes.py`: Campanha
  com critério que exclui a Pessoa (`unidades=["Vitória"]` para SIM-P-0001) → mesma
  mensagem de "sem Campanha", sem critério, unidade da Campanha ou motivo no texto;
  Participação em rascunho de Campanha encerrada (relógio após o fim) → formação "Sem
  pesquisa disponível no momento.", sem "Continuar". Se falhar, corrigir em
  `trajetoria/interface/views.py` (T015).

---

## Phase 14: User Story 12 — Tratar ambiguidade de formação/Campanha (Priority: P2)

**Goal**: ambiguidade com mensagem neutra, sem escolha de Campanha.

**Independent Test**: Pessoa com uma formação ambígua e outra pendente → mensagem neutra
e ação só para a outra.

### Tests for User Story 12 ⚠️

- [X] T035 [US12] Acrescentar a `tests/interface/test_interface_formacoes.py`: duas
  Campanhas sobrepostas sobre uma formação de SIM-P-0003 (critério por unidade) e uma
  única Campanha sobre a outra → `ENTRADA_RESOLVIDA` para a outra, com um botão sem
  `formacao`; a ambígua com "A pesquisa referente a esta formação não está disponível
  neste momento.", sem nome, período ou quantidade de Campanhas; só ambígua →
  "Não há pesquisa pendente…"; POST `/formacoes/entrar/` com a ambígua → 302
  `?aviso=situacao`, nada criado. Se falhar, corrigir em `trajetoria/interface/views.py`
  (T015/T017).

---

## Phase 15: User Story 13 — Tratar encerramento da Campanha durante o preenchimento (Priority: P2)

**Goal**: rejeição da 005/006 por coleta → "período encerrado", rascunho preservado.

**Independent Test**: Seção aberta no período, envio depois do fim → mensagem, nada
gravado.

### Tests for User Story 13 ⚠️

- [X] T036 [US13] Criar `tests/interface/test_interface_encerramento.py` (E2E-4):
  GET da Seção com `relogio.agora = c.NO_PERIODO`; `relogio.agora = c.DEPOIS_DO_FIM`; POST
  com respostas novas → 200 "O período de resposta desta pesquisa foi encerrado. As
  respostas salvas anteriormente foram preservadas.", `c.retrato()` igual, sem
  formulário; GET da Seção e de `/participacoes/<id>/` → mesma mensagem; `/concluir/`
  (GET e POST) → mesma mensagem, `concluida_em` vazio; `/formacoes/` → formação sem
  pesquisa; com `c.ULTIMO_DIA` o envio é aceito; encerramento explícito
  (`encerrar(campanha, agora=…)` da 004) produz o mesmo resultado; nenhuma tela oferece
  prazo ou "salvar para enviar depois". Se falhar, corrigir em
  `trajetoria/interface/views.py` (sem avaliar período na interface).

---

## Phase 16: User Story 14 — Garantir acessibilidade e responsividade básicas (Priority: P3)

**Goal**: verificação estrutural automatizada de todas as telas.

**Independent Test**: o verificador estrutural passa em todas as telas; roteiro manual do
quickstart.

### Tests for User Story 14 ⚠️

- [X] T037 [US14] Criar `tests/interface/test_interface_acessibilidade.py` com um
  verificador sobre `html.parser`, aplicado às telas: entrada de demonstração; formações
  (cinco situações); Seções S1, S3, S8, S10, S11, S13 (sem e com erros, com pendências);
  conclusão; confirmação; avisos; 404; 403 de CSRF. Regras: `<html lang="pt-BR">`; um
  `<title>` não vazio e distinto por tela, começando por "Erro:" quando há erros ou
  pendências; exatamente um `h1`; níveis de título sem saltos; primeiro elemento focável é
  "Pular para o conteúdo" apontando para `main#conteudo`; todo `input`/`select`
  (exceto `hidden`, `submit`) com `label for` correspondente ou dentro de `label`; todo
  grupo de rádios/caixas dentro de `fieldset` com `legend` não vazia; todo
  `aria-describedby` aponta para `id` existente; todo `id` único; campo com erro tem
  `aria-invalid="true"`; resumo de erros com `role="alert"` e ligações para `#p<n>`
  existentes; nenhum `<script>`, `style=` com largura fixa, `http://`/`https://` em `src`
  ou `href` de recurso; botões com texto.

### Implementation for User Story 14

- [X] T038 [US14] Corrigir `trajetoria/interface/templates/**` e `estilo.css` até T037
  passar; revisar o CSS contra [R13/R14](research.md#r13--acessibilidade-padrões-html-sem-javascript)
  (foco visível em rádios, caixas, ligações e botões; nada só por cor; quebra de linha de
  textos longos de Opção; `<select>` e campos com `width: 100%`; nenhuma rolagem
  horizontal a 320px).

---

## Phase 17: Aceitação ponta a ponta e fronteiras

**Purpose**: cenários E2E da spec e invariantes estruturais (SC-002, SC-003, SC-006,
SC-007, SC-012, SC-013, SC-016, SC-017).

- [X] T039 Criar `tests/interface/test_interface_aceitacao.py` com **E2E-1** (16 passos da
  spec, com Pessoa SIM-P-0001 e `cenario_baseline()`; ao final, as Respostas da
  Participação concluída são exatamente as Perguntas de `perguntas_do_percurso` do
  percurso final; passo 7 inclui uma pendência e um complemento de "Outro:" em S8; passo
  9 encerra a demonstração), **E2E-2** (Q1 = "Não" e a variante "Sim → parte de S2 → volta
  a S1 → Não"; 1 Resposta) e **E2E-3** (SIM-P-0003: seleção, início da primeira, volta às
  formações ainda em seleção com "Continuar"/"Iniciar", duas Participações). Todos por
  `client`, sem dublês de domínio.
- [X] T040 [P] Criar `tests/interface/test_interface_fronteiras.py`:
  - importações de todos os módulos de `trajetoria/interface/` e `trajetoria/demonstracao/`
    via `ast`, contra a lista de permitidas/proibidas de
    [R19](research.md#r19--estratégia-de-testes); `iniciar_participacao` nunca importada na
    interface; `campanha.*`, `instrumento.operacoes`, `formulario_2024`,
    `academico.incorporacao` só em `trajetoria/demonstracao/cenario.py`;
    `trajetoria.interface.apresentacao` só em `trajetoria/demonstracao/views.py` (e nenhum
    outro módulo da interface importado pela demonstração);
  - nenhum texto de Pergunta ou de Opção da baseline (de
    `trajetoria.formulario_2024.declaracao`, textos com ≥ 12 caracteres) e nenhum padrão
    `\bQ\d{1,2}\b` em `.py` e `.html` de `trajetoria/interface/` e
    `trajetoria/demonstracao/` (exceto `cenario.py` para textos de Campanha);
  - nenhum `.save(`, `.create(`, `.update(`, `.delete(`, `objects.bulk_` nos dois apps;
    nenhum `models.py`; `apps.get_app_config("interface").get_models()` e o da
    `demonstracao` vazios;
  - nenhuma dependência nova em `pyproject.toml` (lista de dependências igual à da `main`);
  - `Client(enforce_csrf_checks=True)`: POST sem token em escolher, encerrar, entrar,
    Seção e concluir → 403;
  - métodos: GET em rotas só-POST → 405; PUT/DELETE → 405;
  - E2E-1 executado com `caplog` em nível DEBUG: nenhum texto declarado, nome de Pessoa ou
    atributo acadêmico nos registros; nenhum desses valores em `Location` de
    redirecionamento nem na URL de qualquer requisição;
  - varredura de `texto_visivel` de todas as telas do E2E-1 contra `PADROES_TECNICOS`
    (SC-013);
  - **falha inesperada** (FR-069): `django.views.defaults.server_error(RequestFactory().get("/"))`
    devolve 500 com "Não foi possível concluir a operação. Tente novamente." e ligação
    para `/`, sem "Traceback", "Exception", "Error", caminho de arquivo, nome de modelo ou
    da faixa de demonstração; o `404.html` renderizado pelo handler padrão
    (`django.views.defaults.page_not_found`) é igualmente autônomo; e, com
    `settings.DEBUG` no valor configurado (`False`), uma view de teste que levanta
    exceção — registrada só no teste via `@pytest.mark.urls` num módulo de URLs de teste —
    responde com o `500.html` pelo `Client(raise_request_exception=False)`, e o logger
    `django.request` registra o erro (`caplog`) sem valores declarados.

---

## Phase 18: Polish & Cross-Cutting Concerns

- [X] T041 [P] Atualizar `README.md` (uma linha apontando para
  [quickstart da 008](quickstart.md)) e `.env.example` (`TRAJETORIA_DEMONSTRACAO=` com
  comentário "1 ativa a demonstração local com dados fictícios; nunca em ambiente acessível
  a egressos" e `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,[::1]`).
- [X] T042 [P] Revisar docstrings de módulo de `trajetoria/interface/*.py` e
  `trajetoria/demonstracao/*.py`: camada fina (007/006/005), nada persistido além do
  cookie, adaptador temporário substituível (FR-005), origem dos dados (contexto
  institucional × respostas declaradas).
- [X] T043 Medir o número de consultas das telas de formações e de Seção (S8, a maior) e
  fixar os tetos em `test_interface_formacoes.py` e `test_interface_secao.py` com
  `django_assert_max_num_queries` (sem crescer com a quantidade de Respostas).
- [X] T044 Rodar o [quickstart](quickstart.md) num banco local dedicado
  (`trajetoria_demo`): os três comandos; roteiros E2E-1, E2E-2, E2E-3 e "Outras situações"
  no navegador **com e sem JavaScript**; largura de 320px e zoom de 200%; teclado; registrar
  o resultado e qualquer ajuste no plan.
- [X] T045 Rodar `uv run ruff check .`, `uv run python manage.py check`,
  `uv run python manage.py makemigrations --check --dry-run` e `uv run pytest`; tudo verde
  e limpo.
- [X] T046 Revisão final contra a spec: FR-001 a FR-098 e SC-001 a SC-017 rastreados para
  tasks/testes; Decisões Pendentes DP-801 a DP-803 e herdadas sem regra implícita;
  `git diff origin/main --stat` sem alterações em `trajetoria/{academico,instrumento,campanha,participacao,fonte_academica,formulario_2024}/`
  nem em testes existentes além de T003; comparar com o baseline anotado em T001 (mesmas
  migrações).
- [X] T047 Acrescentar ao [plan.md](plan.md) a "Revisão pós-implementação" (como na 007):
  gate mantido, número de testes, arquivos novos, consultas medidas, resultado do
  quickstart manual.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (T001)** → **Foundational (T002–T008)** → histórias → **Aceitação (T039–T040)** →
  **Polish (T041–T047)**.
- Na Foundational: T002 primeiro; T004 depois de T002; T003, T005, T007 e T008 em paralelo
  com T004; T006 depois de T005.

### User Story Dependencies

- **US1** (T009–T013): Foundational.
- **US2** (T014–T015): US1 (cookie e Pessoa em uso).
- **US3** (T016–T017): US2 (tela de formações).
- **US4** (T018–T020): US3 (`_participacao_da_pessoa`, `_jornada`, avisos). Os testes de
  US4 criam a Participação pela 005, sem depender da tela de formações.
- **US5** (T021–T024): US4.
- **US6** (T025–T026): US5.
- **US7** (T027–T028): US5.
- **US8** (T029–T030): US5.
- **US9** (T031–T032): US8.
- **US10** (T033): US9.
- **US11** (T034), **US12** (T035): US3.
- **US13** (T036): US8.
- **US14** (T037–T038): US1–US13 (todas as telas existem).
- **Aceitação** (T039–T040): US1–US14.

### Within Each User Story

- Testes primeiro; DEVEM falhar quando trazem comportamento novo (US1–US5, US7–US9, US14).
- `trajetoria/interface/views.py`, `test_interface_formacoes.py`, `test_interface_secao.py`,
  `test_interface_navegacao.py` e `test_interface_conclusao.py` são editados em sequência.

### Parallel Opportunities

- Foundational: T003, T005, T007, T008.
- US1: T009 e T010 (arquivos distintos); T011 → T012; T013 independente de T012.
- US5: T021 e T022.
- Após US5: US6, US7 e US8 em paralelo por desenvolvedores distintos **se** coordenarem
  `views.py` (T028 e T030 tocam o mesmo arquivo); US11 e US12 só acrescentam testes.
- Aceitação: T040 em paralelo com T039.
- Polish: T041 e T042.

---

## Parallel Example: Foundational

```bash
Task: "T003 Ajustar test_10 da 007 em tests/participacao/test_entrada_aceitacao.py"
Task: "T005 Folha de estilo em trajetoria/interface/templates/interface/estilo.css"
Task: "T007 contexto_da_formacao em trajetoria/interface/apresentacao.py"
Task: "T008 conftest e auxiliares em tests/interface/"
```

## Parallel Example: User Story 1

```bash
Task: "T009 Testes da entrada de demonstração em tests/interface/test_interface_demonstracao.py"
Task: "T010 Testes do comando preparar_demonstracao em tests/interface/test_interface_cenario.py"
```

## Parallel Example: User Story 5

```bash
Task: "T021 Testes de gravação em tests/interface/test_interface_gravacao.py"
Task: "T022 Testes de avanço em tests/interface/test_interface_navegacao.py"
```

---

## Implementation Strategy

### MVP First

1. Setup + Foundational (T001–T008).
2. US1 → US5 (T009–T024): demonstração, formações, entrada, Seção, salvar e avançar.
3. **STOP and VALIDATE**: `uv run pytest tests/interface` e, no navegador, Ana Exemplo de
   S1 até a última Seção.

### Incremental Delivery

4. US6 (retomada) → US7 (ramos, 17 percursos, Versão diferente) → US8/US9 (conclusão e
   confirmação) — fim das histórias P1.
5. US10–US13 (P2): concluída, sem pesquisa, ambiguidade, encerramento.
6. US14 (P3): verificação estrutural de acessibilidade e ajustes.
7. Aceitação (T039–T040) e Polish (T041–T047).

---

## Decisões Pendentes preservadas

Nenhuma task resolve DP-801, DP-802, DP-803 nem as herdadas 004/DP-406, 005/DP-505,
005/DP-504, 002/DP-007, 001/DP-009, 006/DP-601, 006/DP-602, 006/DP-603, 005/DP-502,
005/DP-503, 007/DP-701, 007/DP-702, 003/DP-301, 003/DP-302, 006/DP-604, 003/DP-307,
002/DP-001, 004/DP-404, 005/DP-501. Em particular: nenhuma autenticação, nenhum resumo
ou comprovante, nenhuma métrica, nenhum prazo de graça, nenhuma edição pós-conclusão,
nenhuma escolha de Campanha, nenhuma alteração de Q10–Q19 ou do instrumento.

## Notes

- **Rastreabilidade dos cenários da spec**:

  | Cenário / critério | Tasks |
  |--------------------|-------|
  | E2E-1 | T039 (e T025 para a retomada) |
  | E2E-2 | T039, T029 |
  | E2E-3 | T039, T016 |
  | E2E-4 | T036 |
  | SC-001 | T010, T044 |
  | SC-004 (17 percursos) | T027 |
  | SC-005 (Versão diferente) | T027 |
  | SC-006, SC-007 | T040 |
  | SC-008 | T025 |
  | SC-009 | T021 |
  | SC-010 | T033 |
  | SC-011 | T036 |
  | SC-012 | T009, T010 |
  | SC-013 | T009, T014, T040 |
  | SC-014 | T037, T044 |
  | SC-015 | T038, T044 |
  | SC-016 | T040 |
  | SC-017 | T040, T045, T046 |

- **Contagem**: 47 tasks — 18 de teste (T009, T010, T014, T016, T018, T021, T022, T025,
  T027, T029, T031, T033, T034, T035, T036, T037, T039, T040); 19 de implementação (T002,
  T004–T007, T011–T013, T015, T017, T019, T020, T023, T024, T026, T028, T030, T032, T038 —
  T007 inclui seus testes puros); 10 de setup, auxiliares, ajuste de teste existente,
  documentação e validação (T001, T003, T008, T041–T047).
- Commits seguem o padrão do projeto (`docs(008): …` para spec/plan/tasks; `feat(008): …`
  para a implementação), com o trailer de coautoria.
