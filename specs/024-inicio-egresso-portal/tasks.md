---

description: "Tasks — Feature 024, Início do egresso e shell do Portal"
---

# Tasks: Início do egresso e shell do Portal

**Input**: Design documents from `specs/024-inicio-egresso-portal/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: obrigatórios (Const. XXVI; spec FR-033). A feature toca:

- autorização (só a Pessoa da sessão vê o Início; o declarante é encaminhado);
- a regra de acesso à trajetória;
- a independência da coleta (Constituição 2.1.0);
- a fronteira de dependência.

**Organization**: uma fase por história de usuário, na ordem de prioridade da spec. Cada
história termina com a suíte verde.

**Situação (2026-10-07)**: todas as tarefas concluídas. Os desvios de detalhe estão em
[plan.md, "Ajustes registrados na implementação"](plan.md); as medidas, em
[validacao.md](validacao.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo, porque os arquivos são diferentes e não há dependência
  pendente.
- **[Story]**: história da spec (US1–US5).

---

## Phase 1: Setup

- [X] T001 Confirmar a linha de base antes de qualquer mudança e registrar a duração da suíte para comparação: `uv run ruff check .`, `uv run python manage.py check`, `uv run python manage.py makemigrations --check --dry-run` e `uv run pytest`, todos verdes. Gravar também a referência do shell para a T014: o HTML
  de `<header>` até a abertura de `<main>` em `/acesso/` (sem sessão) e numa Seção da
  pesquisa (Pessoa de teste com rascunho), salvo em `tests/portal/referencia_shell.html`,
  com um bloco por página.
- [X] T002 Criar o app `trajetoria/portal/` com `__init__.py`, `apps.py` (`PortalConfig`, `name = "trajetoria.portal"`), `templates/portal/` vazio e **sem** `models.py` nem `migrations/` (research R1; data-model).
- [X] T003 Em `config/settings.py`, fazer três coisas:
  - acrescentar `TRAJETORIA_PORTAL = os.environ.get("TRAJETORIA_PORTAL") != "0"`, com comentário citando ADR 0008 e research R8 ("ligado salvo `0`; atrás do modo de demonstração");
  - incluir `"trajetoria.portal"` em `INSTALLED_APPS`, depois de `"trajetoria.contato"`;
  - incluir `"trajetoria.portal.contexto.navegacao"` em `TEMPLATES[0]["OPTIONS"]["context_processors"]`.

---

## Phase 2: Foundational (bloqueia as histórias)

- [X] T004 Em `config/urls.py`, trocar `urlpatterns` por uma função `rotas(com_portal: bool)` que devolve a lista atual e, quando `com_portal`, insere `path("", include("trajetoria.portal.urls"))` **antes** de `trajetoria.interface.urls`. Terminar com `urlpatterns = rotas(settings.TRAJETORIA_PORTAL)` e atualizar a docstring (024; contracts/rotas.md).
- [X] T005 Criar `trajetoria/portal/urls.py` com `""` (entrada), `"entrar/"` (identificação) e `"inicio/"` (Início), e `trajetoria/portal/views.py` com esqueletos que respondem 404 até as histórias.
- [X] T006 Criar `trajetoria/portal/contexto.py` com o context processor `navegacao(request)`, conforme contracts/navegacao.md:
  - devolve `{}` sem modo de demonstração, com `TRAJETORIA_PORTAL` falso, sem Pessoa na sessão ou com declarante;
  - nos demais casos, devolve `{"navegacao": [...], "navegacao_rotulo": "Portal do Egresso"}` com os itens Início, Minha trajetória (só se `narrativa.consultas.elegivel(pessoa)`), Pesquisa e Meu e-mail;
  - cada item tem `rotulo`, `endereco` e `atual`; em `/participacoes/<id>/concluida/`, o item atual é "Pesquisa";
  - os rótulos vêm de `trajetoria/portal/mensagens.py`.
- [X] T007 Criar `trajetoria/portal/mensagens.py` com os textos provisórios de contracts/inicio.md e contracts/navegacao.md:
  - produto "Portal do Egresso", subtítulo "Instituto Federal do Espírito Santo";
  - rótulo "Entrada do Portal do Egresso";
  - `h1` "Sua história com o Ifes";
  - nota de proveniência e "Registro do Ifes";
  - textos das ações e do convite por situação.
- [X] T008 Em `trajetoria/interface/templates/interface/base.html`, acrescentar dois blocos neutros, sem mencionar "portal":
  - `{% block produto %}`, envolvendo o conteúdo atual de `.produto-nome`, com o padrão "Trajetória Ifes" / "Acompanhamento de egressos" inalterado;
  - `{% block navegacao %}{% endblock %}`, entre `</header>` e `<main>`.

  Com os blocos vazios, o HTML gerado deve ser byte a byte o de hoje (SC-007; contracts/navegacao.md).
- [X] T009 Criar `trajetoria/interface/templates/interface/_navegacao.html`, que renderiza `navegacao` só se existir:
  - `<nav aria-label="{{ navegacao_rotulo }}"><ul>` com um `<li><a>` por item. O rótulo vem do contexto, para que o include neutro não contenha texto do Portal;
  - `aria-current="page"` no item atual.

  Acrescentar o estilo em `trajetoria/interface/templates/interface/jornada.css` com tokens da 015: lista que quebra linha, alvos de pelo menos 44×44 px, foco da 015 e sem rolagem horizontal a 320 px.
- [X] T010 Em `trajetoria/acesso/views.py`, extrair o corpo de `entrada` para uma função interna `identificar(request, *, destino, acao, titulo, rotulo=None, continuar=..., aviso_de_envio=True, contexto=None)` (pública; ver plan, "Ajustes registrados"). `entrada` chama `identificar(request, destino="/formacoes/", acao="/acesso/")`. A frase do envio guardado (`mensagens.ENVIO_GUARDADO`, em `_chegada`) só aparece com `aviso_de_envio=True` (research R3, R9).
- [X] T011 Em `trajetoria/acesso/templates/acesso/entrada.html`, trocar os três pontos fixos por variáveis:
  - `action="/acesso/"` dos dois formulários (principal e painel) por `{{ acao }}`;
  - o link fixo "Continuar para suas formações" por `continuar` (rótulo e endereço);
  - o rótulo opcional `rotulo` passa a aparecer acima do `h1`.

  Com os valores padrão de `/acesso/`, o HTML não muda.
- [X] T012 [P] Criar `tests/portal/__init__.py`, `tests/portal/urls_sem_portal.py` (`from config.rotas import rotas; urlpatterns = rotas(False)`) e `tests/portal/construcao.py`, com:
  - `pessoa_sem_conclusao()`: Pessoa da fonte simulada sem Conclusão, mais o material de verificação, pela construção existente de `tests/acesso`;
  - `entrar_pelo_portal(client, pessoa)`;
  - `entrar_pelo_convite(client, pessoa)`.

  Reutilizar `tests/narrativa/construcao.py` (`cenario_narrativa`, `entrar`).
- [X] T013 [P] Criar `tests/portal/test_fronteiras.py` (FR-028, FR-029):
  - nenhum arquivo `.py`, `.html` ou `.css` em `trajetoria/` fora de `trajetoria/portal/` contém `trajetoria.portal`, `portal/` ou a palavra "portal" (sem distinguir maiúsculas);
  - `trajetoria/portal/` não tem `models.py` nem `migrations/`;
  - `tests/dependencias.py` não muda;
  - **nenhuma gravação:** contagens de `Pessoa`, `ConclusaoAcademica`, `Participacao`, `Resposta`, `ContatoDaPessoa`, `FormacaoDeclarada` e `GeracaoDeVideo` iguais antes e depois de GET `/`, GET `/entrar/` e GET `/inicio/`, com e sem sessão (FR-029; FR-033, item 10; SC-006). Este caso entra depois das histórias US1, quando as rotas existirem; até lá, marcar como `xfail` estrito.
- [X] T014 [P] Teste de regressão do shell em `tests/portal/test_navegacao.py::test_shell_sem_navegacao_identico`: com o provedor devolvendo `{}`, `/acesso/` e uma Seção renderizam, de `<header>` até `<main>`, exatamente o HTML de `tests/portal/referencia_shell.html`, gravado na T001 (015 `contracts/shell.md`; SC-007).

**Checkpoint**: suíte verde; Portal roteado, mas sem telas; jornada idêntica.

---

## Phase 3: User Story 1 — Entrar pelo Portal e ser reconhecido (P1) 🎯 MVP

**Goal**: `/` → `/entrar/` → `/inicio/`, e um Início que reconhece antes de pedir.

**Independent Test**: Maria (duas Conclusões, Campanha em coleta) entra por `/` sem sessão e chega ao Início. As duas formações aparecem com "Registro do Ifes" antes de qualquer menção à pesquisa (spec US1).

### Tests

- [X] T015 [P] [US1] Em `tests/portal/test_entradas.py`, cobrir as entradas (contracts/rotas.md):
  - `/` sem sessão → 303 `/entrar/`;
  - `/` com Pessoa → `/inicio/`;
  - `/` com declarante → `/declaracao/`;
  - `/entrar/` GET sem sessão → 200 com "Entrada do Portal do Egresso" e formulário com `action="/entrar/"`;
  - `/entrar/` com Pessoa → `/inicio/`;
  - POST confirmado em `/entrar/` → 303 `/inicio/`;
  - POST "não confirmada" em `/entrar/` → mesmo selo e saída da 019 que `/acesso/`;
  - POST com formato inválido → mesma resposta de `/acesso/` (resumo de erros);
  - limite de tentativas → 429 com `Retry-After`;
  - parâmetros estranhos (`?destino=`, `?next=`, `?proximo=`) ignorados (FR-006);
  - com `settings.TRAJETORIA_DEMONSTRACAO = False`, `/`, `/entrar/` e `/inicio/` respondem 404 e o provedor de navegação devolve `{}` (FR-030).
- [X] T016 [US1] Em `tests/portal/test_entradas.py`, cobrir a sessão expirada (FR-007): `/inicio/` sem sujeito → `/entrar/`; com a sessão recém-expirada → `/entrar/?aviso=sessao`, só com a frase genérica da 023 FR-001, sem `ENVIO_GUARDADO`, mesmo havendo envio guardado.
- [X] T017 [P] [US1] Em `tests/portal/test_inicio.py`, cobrir o conteúdo do Início (contracts/inicio.md):
  - ordem do documento: abertura → `h1` → síntese → formações → derivados → proveniência → ações → convite;
  - toda formação acompanhada de "Registro do Ifes";
  - as três Conclusões de Diego na ordem da 007;
  - nenhum nome no `h1`;
  - vedações de vocabulário ("minuto", "%", "turma", "geração", "conectad", "Olá", "Oportunidade", "Volte ao Ifes", "comunidade");
  - "pesquisa" só no bloco do convite e na navegação;
  - todo `href` do Início responde 200 ou 302;
  - nenhuma consulta à tabela de Resposta nem de Contato (`django_assert_num_queries` ou `CaptureQueriesContext` filtrando por tabela).
- [X] T018 [US1] Em `tests/portal/test_inicio.py`, cobrir o convite por situação (FR-020): disponível para iniciar ("Responder"), retomar ("Continuar" com "onde parou"), `SELECAO_NECESSARIA`, `SEM_ENTRADA_PENDENTE`, `SEM_PESQUISA`. Toda ação leva a `/formacoes/`.
- [X] T019 [US1] Em `tests/portal/test_inicio.py`, cobrir os casos de borda (spec Edge Cases):
  - Pessoa sem Conclusão: frase de `SEM_FORMACAO`, só a ação "Meu e-mail", sem convite e sem item de trajetória;
  - falha da narrativa (monkeypatch de `montar` levantando exceção): página 200 sem os blocos 1, 3, 4 e 5 e log sem dado pessoal;
  - vídeo indisponível: sem o atalho do vídeo.

### Implementation

- [X] T020 [US1] Em `trajetoria/portal/views.py`, implementar `entrada` (GET `/`), conforme contracts/rotas.md: Pessoa → `/inicio/`; declarante → `/declaracao/`; sem sujeito → `/entrar/`.
- [X] T021 [US1] Em `trajetoria/portal/views.py`, implementar `entrar` (GET/POST `/entrar/`):
  - com Pessoa → `/inicio/`; com declarante → `/declaracao/`;
  - sem sujeito → `acesso.views.identificar(request, destino="/inicio/", acao="/entrar/", rotulo=mensagens.ROTULO_ENTRADA, continuar=None, aviso_de_envio=False)`. Com sessão, a view redireciona antes, então o link "Continuar" não tem uso no Portal;
  - `never_cache` e `require_http_methods(["GET", "POST"])`.
- [X] T022 [US1] Em `trajetoria/interface/mensagens.py`, tornar públicos os textos de estado da entrada que hoje estão no dicionário privado `_TELA_DE_FORMACOES` de `trajetoria/interface/views.py` (`SEM_FORMACAO`, `SEM_PESQUISA`, `SEM_ENTRADA_PENDENTE`), **sem mudar nenhum texto**. `interface/views.py` passa a importá-los de lá. Os testes de `/formacoes/` continuam verdes sem alteração.
- [X] T023 [US1] Criar `trajetoria/portal/inicio.py` com `montar_inicio(pessoa, referencia, demonstracao) -> dict` (research R6; data-model):
  - lê `narrativa.consultas.entrada_da_pessoa` + `narrativa.montagem.montar`, para a síntese (`secao("o_que_o_ifes_registra")`), as formações e até dois derivados;
  - lê `participacao.entrada.situacao_de_entrada`, para o convite;
  - lê `video.renderizador.disponivel()`, para o atalho do vídeo;
  - não lê Contato nem Resposta;
  - falha da narrativa → blocos omitidos e `logger.exception` só com o fato técnico;
  - Pessoa sem Conclusão → a frase de `SEM_FORMACAO`, importada de `interface.mensagens` (T022).
- [X] T024 [US1] Em `trajetoria/portal/views.py`, implementar `inicio` (GET `/inicio/`):
  - sem Pessoa → `/entrar/` ou `/entrar/?aviso=sessao` (usando `request._sessao_expirada`, já marcado por `pessoa_em_uso`);
  - declarante → `/declaracao/`;
  - Pessoa → `render("portal/inicio.html", montar_inicio(...))`;
  - `never_cache`, `require_GET`.
- [X] T025 [US1] Criar `trajetoria/portal/templates/portal/inicio.html`, que estende `interface/base.html` e:
  - sobrescreve `produto` com "Portal do Egresso" e o subtítulo;
  - inclui a navegação no bloco `navegacao`;
  - segue a ordem dos blocos de contracts/inicio.md, com um único `h1` e `h2` nos blocos 7 e 8;
  - reaproveita a abertura ilustrada da 021 (`narrativa.imagens`) e o padrão `interface/formacao.html`;
  - mostra "Registro do Ifes" como texto.
- [X] T026 [US1] Em `jornada.css`, estilos do Início com tokens da 015, sem tokens novos e sem grade de cartões: abertura, lista de formações com selo de origem, lista de ações e bloco do convite.

**Checkpoint**: US1 testável pelo quickstart, passo 1.

---

## Phase 4: User Story 2 — Trajetória, retrato e vídeo antes de responder (P1)

**Goal**: regra positiva (FR-009, FR-010) e `/formacoes/` sem antecipação, com o tamanho da pesquisa (FR-013, FR-014).

**Independent Test**: uma Pessoa com Conclusão e sem Participação abre `/minha-trajetoria/`, baixa `card.png` e pede o vídeo. As contagens de Participação, Resposta e contato não mudam (spec US2).

### Tests

- [X] T027 [P] [US2] Em `tests/narrativa/test_rotas.py`, substituir `test_sem_participacao_concluida_vai_para_formacoes` (revisão 021 FR-001/FR-002 pela 024) por dois testes:
  - `test_com_conclusao_sem_participacao_ve_a_pagina` (200, as duas formações de Maria);
  - `test_sem_conclusao_vai_para_formacoes` (302 `/formacoes/`, sem mencionar narrativa).

  Manter os testes de sessão ausente e de declarante.
- [X] T028 [P] [US2] Em `tests/portal/test_trajetoria_antes.py`:
  - `card.png`, `card.svg` e o pedido de vídeo funcionam sem Participação;
  - contagens de `Participacao`, `Resposta`, `ContatoDaPessoa` e `GeracaoDeVideo` antes e depois: só `GeracaoDeVideo` muda, e só pelo pedido explícito;
  - uma Participação em rascunho não muda;
  - a Participação ancorada em Formação Declarada continua sem narrativa (021 FR-007).
- [X] T029 [P] [US2] Em `tests/video/test_rotas.py`, ajustar os testes que pressupõem Participação concluída para a regra do FR-009, com a referência "revisão 022 FR-001 pela 024".
- [X] T030 [P] [US2] Em `tests/interface/test_interface_formacoes.py`, ajustar o teste da antecipação (linhas ~392–395):
  - a frase "Ao final, você poderá ver sua trajetória no Ifes." não aparece mais;
  - aparece "A pesquisa tem no máximo N partes.", com N = 1 + `maximo_restante` da primeira Seção, para a formação disponível para iniciar;
  - não aparece para a formação a retomar;
  - em `SELECAO_NECESSARIA`, aparece em cada formação disponível para iniciar;
  - a ligação "Ver minha trajetória no Ifes" aparece para quem tem Conclusão, mesmo sem Participação.
- [X] T031 [P] [US2] Em `tests/narrativa/test_catalogo.py`, retirar `mensagens.ANTECIPACAO` da lista de fontes e incluir a frase nova do tamanho.

### Implementation

- [X] T032 [US2] Em `trajetoria/narrativa/consultas.py`, mudar `elegivel(pessoa)` para `pessoa.conclusoes.exists()`, remover o import de `Participacao` e reescrever a docstring do módulo e da função: "regra positiva da 024 (FR-009); revisa 021 FR-001/E2; Formação Declarada fica fora por construção".
- [X] T033 [US2] Em `trajetoria/interface/mensagens.py`, remover `ANTECIPACAO` e acrescentar `TAMANHO_DA_PESQUISA = "A pesquisa tem no máximo {n} partes."`, com variante singular ("no máximo 1 parte") coerente com `apresentacao._restantes`.
- [X] T034 [US2] Em `trajetoria/interface/views.py` (`formacoes`) e `trajetoria/interface/templates/interface/formacoes.html`:
  - trocar `antecipacao` por `tamanho`, calculado para cada formação `DISPONIVEL_PARA_INICIAR` como 1 + `maximo_restante(conteudo, primeira_secao.id)`;
  - carregar o conteúdo da Versão da Campanha pela leitura existente da jornada (`participacao.consultas`), sem nova regra (research R5);
  - atualizar o comentário que citava 021 FR-070.

**Checkpoint**: quickstart, passos 2 e 3 (texto de `/formacoes/`).

---

## Phase 5: User Story 3 — Convite responde sem passar pelo Portal (P1)

**Goal**: o caminho A inalterado (FR-008), com evidência automatizada.

**Independent Test**: Diego segue `/acesso/`, confirma, chega a `/formacoes/`, responde e conclui, com os mesmos endereços e textos de hoje (spec US3).

### Tests

- [X] T035 [P] [US3] Em `tests/portal/test_entradas.py` (classe `TestCaminhoDoConvite`), com o Portal ativo:
  - POST confirmado em `/acesso/` → 303 `/formacoes/`;
  - rascunho → "Continuar a pesquisa" e "onde parou";
  - Participação concluída → sem entrada pendente e com ligação para a trajetória;
  - Campanha encerrada, fora da abrangência e sem pesquisa → mensagens da 007/014;
  - envio guardado com sessão expirada → nova identificação por `/acesso/` volta à Seção com as marcações (023 FR-006);
  - declarante → `/declaracao/`.
- [X] T036 [US3] Em `tests/portal/test_entradas.py` (classe `TestCaminhosEquivalentes`), cobrir rascunho, concluída, encerrada e sem pesquisa entrando por `/entrar/`:
  - o Início mostra o convite correspondente;
  - a ação leva a `/formacoes/`, que mostra o mesmo estado do caminho A;
  - com envio guardado, entrar pelo Portal e seguir o convite também restaura a Seção.
- [X] T037 [US3] Rodar `tests/interface`, `tests/participacao`, `tests/acesso`, `tests/declaracao` e `tests/comunicacao` com o Portal ativo. Corrigir só o que for efeito colateral da 024: não mudar comportamento da jornada.

**Checkpoint**: quickstart, passo 4.

---

## Phase 6: User Story 4 — Navegar entre o Portal e a pesquisa (P2)

**Goal**: navegação nas telas do FR-022 e só nelas.

**Independent Test**: com sessão, percorrer Início → Pesquisa → Início → Minha trajetória → Meu e-mail → Início só pela navegação (spec US4).

### Tests

- [X] T038 [P] [US4] Em `tests/portal/test_navegacao.py`, cobrir as telas (contracts/navegacao.md):
  - com navegação: `/inicio/`, `/formacoes/`, `/participacoes/<id>/concluida/`, `/minha-trajetoria/` e `/meu-email/`, com itens na ordem e `aria-current="page"` no item certo ("Pesquisa" na confirmação);
  - sem navegação: Seção, concluir, `aviso.html`, `/acesso/`, `/entrar/` e `/declaracao/`;
  - Pessoa sem Conclusão sem o item "Minha trajetória";
  - todo `href` da navegação responde 200;
  - nenhum `<script>`.
- [X] T039 [US4] Em `tests/portal/test_navegacao.py`, cobrir o cabeçalho: "Portal do Egresso" no `/inicio/`; "Trajetória Ifes" nas demais telas; assinatura e ordem do shell da 015 preservadas nos dois casos.

### Implementation

- [X] T040 [US4] Optar pela navegação com `{% block navegacao %}{% include "interface/_navegacao.html" %}{% endblock %}` em `trajetoria/interface/templates/interface/formacoes.html`, `trajetoria/interface/templates/interface/concluida.html`, `trajetoria/narrativa/templates/narrativa/minha_trajetoria.html` e `trajetoria/contato/templates/contato/meu_email.html`.

**Checkpoint**: quickstart, passo 3.

---

## Phase 7: User Story 5 — Coleta com o Portal desabilitado (P2)

**Goal**: FR-027 e SC-005.

**Independent Test**: com `TRAJETORIA_PORTAL=0`, o caminho do convite funciona, `/entrar/` e `/inicio/` respondem 404, e nenhuma tela tem navegação (spec US5).

### Tests

- [X] T041 [P] [US5] Criar `tests/portal/test_desabilitado.py`, com `pytestmark = [pytest.mark.urls("tests.portal.urls_sem_portal")]` e a fixture `settings.TRAJETORIA_PORTAL = False`:
  - `/` sem sessão → `/acesso/`; com Pessoa → `/formacoes/`; com declarante → `/declaracao/`;
  - `/entrar/` e `/inicio/` → 404;
  - `/formacoes/`, `/minha-trajetoria/` e `/meu-email/` sem `<nav`;
  - o caminho completo do convite até a confirmação funciona;
  - a trajetória abre para Pessoa com Conclusão e sem Participação (FR-009 independe do Portal).
- [X] T042 [US5] Em `tests/portal/test_desabilitado.py`, verificar que `config.urls.rotas(False)` não contém nenhum `URLResolver` de `trajetoria.portal.urls`.

### Implementation

- [X] T043 [US5] Conferir que `trajetoria/portal/contexto.py` lê `settings.TRAJETORIA_PORTAL` a cada requisição e que `config/urls.py` não importa `trajetoria.portal` quando `com_portal` é falso, usando `include` por string. Ajustar se os testes T041 e T042 falharem.

**Checkpoint**: quickstart, passo 6.

---

## Phase 8: Polish & Cross-Cutting

- [X] T044 Rodar as verificações do CI (`uv run ruff check .`, `uv run python manage.py check`, `uv run python manage.py makemigrations --check --dry-run`, `uv run pytest`) e corrigir. Comparar a duração com T001.
- [X] T045 Validação visual a 375×812 e 320 px, com fonte de 100% e 200%, seguindo o quickstart (passos 1 a 6):
  - medir SC-002 (telas e toques do caminho A iguais à reauditoria, cenário A), SC-003 (um toque do Início à trajetória, pesquisa e e-mail), SC-004 (`h1` e síntese acima da dobra; sem rolagem horizontal) e SC-007 (shell e primeira pergunta das Seções iguais à reauditoria);
  - capturas em `specs/024-inicio-egresso-portal/evidencias/` e resultados em `specs/024-inicio-egresso-portal/validacao.md`;
  - se a abertura ilustrada empurrar a síntese para baixo da dobra, aplicar a regra de contracts/inicio.md ("Medidas").
- [X] T046 [P] Acessibilidade em `tests/portal/test_inicio.py` e `tests/portal/test_navegacao.py`: um `h1` por página; títulos em ordem; `nav` com nome acessível; nenhum elemento interativo sem nome; foco visível pela folha da 015. Revisão manual com teclado registrada em `validacao.md`.
- [X] T047 Escrever o protocolo do Checkpoint 1 em `specs/024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md`, **antes** do teste:
  - personas e roteiro de tarefas;
  - perguntas abertas que mapeiam SC-008 a SC-016;
  - número de participantes e limiar de "maioria";
  - como o mockup é mostrado à parte para Oportunidades e Volte ao Ifes;
  - a regra de leitura do resultado (spec, Success Criteria).
- [X] T048 Notas de revisão "Nota de revisão pela Feature 024" em `specs/021-minha-trajetoria-narrativa/spec.md` (FR-001, FR-002, E2, FR-070), `specs/022-minha-trajetoria-video/spec.md` (FR-001), `specs/015-identidade-visual-jornada/contracts/shell.md` (blocos `produto` e `navegacao`) e `specs/008-interface-navegavel-pesquisa/spec.md` (raiz com o Portal ativo).
- [X] T049 [P] Atualizar `README.md` (linha da Feature 024), `docs/desenvolvimento/ambiente-local.md` (`TRAJETORIA_PORTAL`, ligado por padrão, `0` desliga; entrada `/`) e `.env.example` (comentário, sem valor obrigatório). Conferir com grep se `docs/documentacao/` cita a regra antiga da trajetória ou a frase de antecipação.
- [X] T050 Marcar no [roadmap](../../docs/roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md) a S1 como implementada e o Checkpoint 1 como próximo passo.

---

## Dependencies & Execution Order

- Setup (T001–T003) → Foundational (T004–T014) → histórias.
- US1 depende de T005, T007, T010 e T011. Dentro de US1, T022 vem antes de T023.
- US2 depende só da fundação e pode ser feita antes ou em paralelo com US1, porque toca `narrativa` e `interface/formacoes`. US1 usa `elegivel` (T032) para a ação "Ver minha trajetória": se US1 vier antes, os testes de ação condicional de T017 usam uma Pessoa já com Participação concluída até T032 entrar.
- US3 depende de US1 (rotas `/entrar/` e `/inicio/` para T036) e de US2 (texto de `/formacoes/`).
- US4 depende de T006, T008 e T009, e de US1 (o Início). T040 toca `formacoes.html`, também tocado por T034: fazer US2 antes de US4.
- US5 depende de T004 e T006, e pode correr depois da fundação. T041 fica completo depois de US2 (trajetória sem Participação).
- Polish depois de todas. T047 (protocolo) pode ser escrito a qualquer momento antes do teste.

### Parallel Opportunities

- T012, T013 e T014 em paralelo.
- Os testes de cada história ([P]) podem ser escritos antes da implementação, em paralelo:
  - US1: T015 (entradas) e T017 (Início), cada arquivo em sequência;
  - US2: T027–T031;
  - US3: T035 e T036 (mesmo arquivo, em sequência);
  - US4: T038 e T039 (mesmo arquivo, em sequência);
  - US5: T041 e T042 (mesmo arquivo, em sequência).
- US2 e US5 podem andar em paralelo com US1 depois da fundação.
- T046, T049 e T050 em paralelo no polimento.

## Implementation Strategy

**MVP**: Fases 1 a 4 (US1 + US2). É o mínimo que permite o Checkpoint 1: entrar pelo Portal,
ser reconhecido e ver a trajetória sem responder.

Depois:

- US3: a prova automatizada de que o convite não mudou, obrigatória antes do merge;
- US4: navegação nas telas existentes;
- US5: Portal desligado;
- o polimento, com medidas, protocolo do teste e notas de revisão.

Cada fase termina com a suíte verde. O merge só acontece com US1 a US5 completas, porque a
independência da coleta (US3, US5) é condição da Constituição 2.1.0.
