---

description: "Tasks da Feature 014 — Polish consolidado da jornada do egresso"
---

# Tasks: Polish consolidado da jornada do egresso

**Input**: Design documents from `specs/014-polish-jornada-egresso/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/rodape-secao.md](contracts/rodape-secao.md),
[contracts/telas.md](contracts/telas.md), [quickstart.md](quickstart.md)

**Stack**: Python 3.13, Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff
([ADR 0001](../../docs/adr/0001-stack-inicial.md)). **Nenhuma dependência nova. Zero
modelos, zero migrações, zero JavaScript.** Só o app `trajetoria/interface/` muda.

**Tests**: obrigatórios e escritos **antes** da implementação correspondente
(Const. XXVI). A feature toca a associação de Respostas ("Salvar e sair" grava pela 005)
e a acessibilidade (Const. XX). Teste de comportamento novo DEVE falhar primeiro. Testes
existentes que fixam texto ou endereço antigo são **ajustados**, nunca removidos.

**Organization**: fases por história da spec, em ordem de prioridade: US1–US4 (P1),
US5, US6, US7, US10 (P2), US8, US9 (P3). `trajetoria/interface/templates/interface/secao.html`,
`views.py`, `mensagens.py` e `estilo.css` são editados por várias histórias, **em
sequência** (nunca em paralelo).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: história da spec (US1…US10)

## Convenções para todas as tarefas

- **Só apresentação** ([plan, Desenho](plan.md#desenho)): nenhuma chamada nova a
  operação de domínio. `views.py` continua chamando só o que já chama
  (`situacao_de_entrada`, `entrar`, `situacao_da_jornada`, `concluir`, `salvar_secao`).
  `formularios.py`, `gravacao.py` e `urls.py` **não mudam**.
- **Nada por Pergunta**: nenhuma referência a Q1…Q54, a texto de Pergunta/Opção ou a
  posição específica de Seção (008 FR-034).
- **Textos**: exatamente os de [contracts/telas.md](contracts/telas.md) e
  [data-model.md](data-model.md); os fixos ficam em `trajetoria/interface/mensagens.py`
  sempre que a view os escolhe. Todos provisórios (DP-801).
- **CSS** ([research R5–R7, R10](research.md)): regras novas só sob `.pergunta` ou em
  classes novas (`.acoes-secao`, `.saidas`, `.resumo-pendencias`, `.com-pendencia`,
  `.lista-secoes`, `.formacao`). **Nunca** alterar as regras globais existentes de
  `button`, `.acoes`, `.opcao`, `.lista-simples` (usadas por editor, acompanhamento e
  demonstração; FR-045).
- **Testes**: em `tests/interface/`, sem `__init__.py`, prefixo `test_interface_`;
  auxiliares de `tests/interface/construcao_interface.py` (`cenario_baseline`,
  `entrar_como`, `iniciar`, `participacao_de`, `secao_do_conteudo`, `dados_validos`,
  `texto_visivel`) e `tests/participacao/construcao.py` (`c.preencher`, `c.retrato`),
  **sem alterá-los**, salvo onde a tarefa disser. `pytestmark = pytest.mark.django_db`.
  Só Pessoas da fonte simulada.

## Limites desta lista (não criar)

- Modelo, migração, tabela, coluna, sessão Django, `messages`, cookie novo.
- `<script>`, `onclick`, `localStorage`, `beforeunload`, service worker, manifest, autosave.
- `autocomplete="off"` ou qualquer mudança para MF-03 (FR-047).
- Wizard, progresso, percentual, estimativa de tempo, componente genérico, design system.
- Reordenação de formações, `sorted(...)` sobre formações, rótulo "cronológico".
- Alteração de texto, ordem, tipo, obrigatoriedade ou regra da Versão; qualquer item [V],
  [Dec] ou [T].
- Mudança em `trajetoria/editor/`, `trajetoria/acompanhamento/`, `trajetoria/demonstracao/`
  ou nas features 001–007 e 009–013.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar a base e registrar o "antes" para a não regressão.

- [X] T001 Confirmar a base: `uv run pytest` verde, `uv run ruff check .` limpo e
  `uv run python manage.py makemigrations --check --dry-run` sem mudanças, na branch
  atualizada com `main` (`e89ca8d` ou posterior). Registrar o número de testes como
  referência no fechamento.
- [X] T002 [P] Capturar o "antes" visual para SC-014 (quickstart §2.6): com a demonstração
  no ar (quickstart "Preparar"), salvar no diretório de rascunho da sessão (fora do
  repositório) capturas a 375 e 1280 px de: lista de Pesquisas e edição de Pergunta (009),
  prévia de Seção (009), painel de uma Campanha (011), entrada e operador da demonstração.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o predicado de verdade das mensagens (FR-008), usado por US1 e US2.

**⚠️ CRITICAL**: US1 e US2 dependem desta fase.

- [X] T003 Em `trajetoria/interface/views.py`, criar a função privada
  `_ha_resposta_na_secao(jornada, secao) -> bool` que devolve
  `any(p.id in jornada.respostas for p in secao.perguntas)`
  ([research R3](research.md#r3--regra-de-verdade-das-mensagens-de-salvamento)). Sem
  chamada nova a domínio: `jornada.respostas` já é carregado por `situacao_da_jornada`.
  Ainda sem uso; comportamento inalterado.
- [X] T004 [P] Criar `tests/interface/test_interface_rodape.py` com `pytestmark`, as
  fixtures `cenario` e `relogio` herdadas de `conftest.py` e dois auxiliares locais:
  `_secao(client, pk, posicao, dados, *, sair=False)` (POST na Seção; com `sair=True`
  acrescenta `{"depois": "sair"}`) e `_ana_na_secao(client, cenario, posicao, escolhas)`
  (entra como Ana, inicia, preenche com `c.preencher` as Seções anteriores do percurso e
  devolve o `pk`). Sem testes ainda.

**Checkpoint**: base pronta; nenhum comportamento mudou.

---

## Phase 3: User Story 1 — Salvar o que já respondi, mesmo sem terminar a Seção (Priority: P1) 🎯 MVP

**Goal**: Seção incompleta pode ser salva e isso é dito; pendência deixa de parecer erro;
nenhuma frase afirma salvamento sem Resposta gravada (FR-001 a FR-008, FR-010).

**Independent Test**: Seção 2 de Ana com 3 de 8 Respostas → gravadas e reapresentadas como
pendência; Seção 1 vazia → nenhuma frase de salvamento.

### Tests for User Story 1 ⚠️

- [X] T005 [P] [US1] Em `tests/interface/test_interface_secao.py`, acrescentar testes
  (devem falhar):
  - (a) envio aceito com 3 de 8 na Seção 2 → `Location` exatamente
    `…/secoes/2/?pendencias=1` (sem `&salvo=1`);
  - (b) GET dessa URL → texto contém "Ainda faltam estas perguntas:" e "O que você
    respondeu nesta seção está salvo.", e **não** contém "Há problemas" nem "Erro";
  - (c) `<title>` começa por "Faltam respostas: ";
  - (d) cada Pergunta pendente mostra "Falta responder: Esta pergunta é obrigatória." e
    mantém `aria-invalid="true"` e o id `pN-erro`;
  - (e) Seção 1 enviada vazia → GET com pendências **sem** "está salvo";
  - (f) `?pendencias=1&salvo=1` numa Seção sem Resposta gravada → nenhuma frase de
    salvamento (o parâmetro é ignorado).
- [X] T006 [P] [US1] Em `tests/interface/test_interface_gravacao.py`, ajustar a
  verificação de "Há problemas nesta seção" para valer **só** para erro de forma (por
  exemplo, `p7-complemento` sem a Opção), com `<title>` começando por "Erro: " e marca
  "Erro: " na Pergunta (FR-004). Acrescentar: na reapresentação com erro de forma, não
  aparece "Ainda faltam" nem "Falta responder".
- [X] T007 [P] [US1] Em `tests/interface/test_interface_formacoes.py`, acrescentar o
  teste de que a entrada resolvida (Ana) e a seleção (Maria) mostram "Pode salvar a
  qualquer momento, mesmo sem terminar a seção, e continuar depois." (FR-002).
- [X] T008 [P] [US1] Em `tests/interface/test_interface_acessibilidade.py`, atualizar
  a regra do verificador ([research R4](research.md#r4--pendência-e-erro-de-forma-a-mesma-estrutura-com-outro-modo)):
  `tem_alerta == (titulo.startswith("Erro:") or titulo.startswith("Faltam respostas:"))`.
  Acrescentar ao fixture `telas` o estado `s1-pendencias-vazia` (Seção 1 enviada vazia e
  GET com `?pendencias=1`). Ajustar `test_telas_com_erros_tem_resumo_e_titulo_de_erro`
  para separar erro (prefixo "Erro:") de pendência (prefixo "Faltam respostas:").

### Implementation for User Story 1

- [X] T009 [US1] Em `trajetoria/interface/mensagens.py`, acrescentar as constantes
  `RESUMO_ERROS = "Há problemas nesta seção"`,
  `RESUMO_PENDENCIAS = "Ainda faltam estas perguntas:"`,
  `SECAO_SALVA = "O que você respondeu nesta seção está salvo."`,
  `PREFIXO_ERRO = "Erro:"`, `PREFIXO_PENDENCIA = "Falta responder:"`,
  `TITULO_ERRO = "Erro: "`, `TITULO_PENDENCIA = "Faltam respostas: "` e
  `ENTRADA_OPERACIONAL = "Você responde uma seção de cada vez. Pode salvar a qualquer
  momento, mesmo sem terminar a seção, e continuar depois."`.
- [X] T010 [US1] Em `trajetoria/interface/views.py`:
  - `_salvar`: o redirecionamento de pendências passa a ser `secao + "?pendencias=1"`;
  - `secao` (GET): deixa de ler `salvo`; calcula
    `salvo = bool(pendencias) and _ha_resposta_na_secao(jornada, passagem.secao)`;
  - `_tela_da_secao`: recebe e repassa `tipo_resumo`
    (`"pendencias"` quando chamado com pendências no GET; `"erros"` quando há erros de
    formulário ou de gravação no POST; `None` sem resumo), e passa `titulo_resumo`,
    `prefixo_titulo` e `prefixo_item` a partir das constantes de T009. `ha_erros` deixa
    de ser usado.
- [X] T011 [US1] Em `trajetoria/interface/templates/interface/base.html`, trocar
  `{% if ha_erros %}Erro: {% endif %}` por `{{ prefixo_titulo|default:"" }}`.
- [X] T012 [US1] Em `trajetoria/interface/templates/interface/secao.html`, o bloco do
  resumo:
  - usa `{{ titulo_resumo }}`;
  - tem a classe `resumo-erros` com `tipo_resumo == "erros"` e `resumo-erros
    resumo-pendencias` com `"pendencias"`;
  - mostra `<p>{{ frase_salvo }}</p>` só quando `salvo` (a view passa
    `frase_salvo = mensagens.SECAO_SALVA`);
  - mantém `role="alert"`, `aria-labelledby="titulo-erros"` e as ligações.
- [X] T013 [US1] Em `trajetoria/interface/templates/interface/perguntas/_cabecalho.html`,
  trocar o literal `Erro: ` por `{{ prefixo_item }} ` (variável de contexto do template
  da Seção). O padrão "Erro:" continua para quem não recebe a variável (prévia do editor):
  usar `{{ prefixo_item|default:"Erro:" }}`.
- [X] T014 [US1] Em `trajetoria/interface/templates/interface/estilo.css`:
  - `.resumo-pendencias { border-color: #1a4480; }`;
  - `.resumo-pendencias h2 { color: #1a4480; }`;
  - `.pergunta.com-pendencia { border-left-color: #1a4480; }`.

  Em `perguntas/escala.html`, `escolha_unica.html`, `escolha_multipla.html` e
  `texto_curto.html`, a classe da Pergunta com erros passa a ser
  `{% if item.erros %} {% if tipo_resumo == "pendencias" %}com-erro com-pendencia{% else %}com-erro{% endif %}{% endif %}`.
  Os quatro templates são reutilizados pela prévia do editor, onde `tipo_resumo` é vazio:
  nada muda lá.
- [X] T015 [US1] Em `trajetoria/interface/templates/interface/formacoes.html`, substituir
  a frase operacional atual ("Esta é a pesquisa do Ifes com seus egressos. Você responde…")
  por `{{ entrada_operacional }}`, que a view `formacoes` passa a partir de
  `mensagens.ENTRADA_OPERACIONAL`.
- [X] T016 [US1] Ajustar os testes existentes que fixam `?pendencias=1&salvo=1` para
  `?pendencias=1`: `tests/interface/test_interface_aceitacao.py` (linha com
  `secoes/2/?pendencias=1&salvo=1`) e `tests/interface/test_interface_navegacao.py`
  (`_url(ana, 2, "?pendencias=1&salvo=1")`). Rodar `uv run pytest tests/interface` e
  corrigir o que restar.

**Checkpoint**: US1 completa e testável sozinha (MVP).

---

## Phase 4: User Story 2 — Interromper com segurança: quatro ações claras (Priority: P1)

**Goal**: "Salvar e sair" (secundária), "Sair sem salvar esta seção" e "Voltar à seção
anterior" (terciárias), com mensagens verdadeiras e a Matriz de comportamento do rodapé
inteira (FR-009 a FR-015).

**Independent Test**: Maria, Seção 11: marcar e "Salvar e sair" → gravado e aviso de
salvamento; Seção vazia → aviso neutro; erro de forma → reapresentação, com a saída sem
salvar disponível.

### Tests for User Story 2 ⚠️

- [X] T017 [US2] Em `tests/interface/test_interface_rodape.py`, implementar a **Matriz de
  comportamento do rodapé** ([contrato](contracts/rodape-secao.md#post-participacoesparticipacaosecoesposicao)),
  um teste por célula, comparando `c.retrato(participacao)` antes e depois. Devem falhar
  onde há comportamento novo.
  - **Envio completo**: "Salvar e continuar" → destino da 006. "Salvar e sair" →
    `Location == "/formacoes/?aviso=salvo"`, Respostas gravadas.
  - **Incompleto com respostas válidas** (Seção 2, 3 de 8): "Salvar e sair" →
    `?aviso=salvo`, as 3 Respostas gravadas.
  - **Sem nenhuma Resposta** (Seção 2 vazia): "Salvar e sair" → `?aviso=saida`, retrato
    inalterado. Mesmo resultado numa Seção só com Perguntas opcionais vazia. E com todas
    as Respostas da Seção removidas por `pN-remover` → `?aviso=saida`.
  - **Erro de forma** (`p7-complemento` sem a Opção, Seção 8): os dois botões → 200, a
    mesma Seção, resumo de erros, retrato inalterado. A página contém a ligação "Sair sem
    salvar esta seção" para `/formacoes/`.
  - **Fora do percurso** (POST numa Seção não alcançada): os dois → 302 Seção atual
    `?aviso=percurso`, retrato inalterado.
  - **Coleta encerrada** (relógio `DEPOIS_DO_FIM`): os dois → 200 com "O período de
    resposta desta pesquisa foi encerrado.", retrato inalterado.
  - **Participação concluída**: os dois → 200 com "Esta pesquisa já foi respondida.".
  - **Repetição**: dois POSTs iguais de "Salvar e sair" → o mesmo `Location`, sem
    Resposta duplicada.
  - **Destino de finalização**: Seção 1 enviada com
    `ci.dados_validos(secao1, ci.escolhas_por_id(cenario.base, {"Q1": "Não"}))` e
    "Salvar e sair" → `?aviso=salvo`; GET `/participacoes/<pk>/` → 302 `/concluir/`. A
    referência a Q1 fica só no teste, nunca no código da interface.
  - **"depois" desconhecido**: `{"depois": "x"}` → igual a "Salvar e continuar".
- [X] T018 [P] [US2] Em `tests/interface/test_interface_rodape.py`, testes da tela:
  - ordem no HTML da Seção: botão "Salvar e continuar" (classe `primario`, sem `name`) →
    botão "Salvar e sair" (`name="depois" value="sair"`, classe `secundario`) →
    `div.saidas` com "Voltar à seção anterior" (só a partir da segunda Seção) e "Sair sem
    salvar esta seção" (`href="/formacoes/"`);
  - nota "O que já foi salvo antes continua guardado.";
  - o texto "Sair e continuar depois" não aparece mais.
- [X] T019 [P] [US2] Em `tests/interface/test_interface_formacoes.py`, testes de aviso:
  - `?aviso=salvo` → "O que você respondeu nesta seção está salvo. Você pode continuar a
    pesquisa quando quiser." com `role="status"`;
  - `?aviso=saida` → "Você pode continuar a pesquisa quando quiser." e **não** contém
    "salvo";
  - `?aviso=situacao` continua igual;
  - `?aviso=qualquer` → nenhum aviso.

### Implementation for User Story 2

- [X] T020 [US2] Em `trajetoria/interface/mensagens.py`, acrescentar a `AVISOS`:
  - `"salvo": "O que você respondeu nesta seção está salvo. Você pode continuar a
    pesquisa quando quiser."`;
  - `"saida": "Você pode continuar a pesquisa quando quiser."`.

  Acrescentar também `SAIR_SEM_SALVAR_NOTA = "O que já foi salvo antes continua guardado."`.
- [X] T021 [US2] Em `trajetoria/interface/views.py`:
  - `_aviso(request, *permitidos)` aceita vários códigos (devolve o texto se
    `request.GET.get("aviso")` está em `permitidos`);
  - `formacoes` usa `_aviso(request, "situacao", "salvo", "saida")`; `secao` continua
    com `"percurso"`;
  - em `_salvar`, logo depois de reler a jornada e obter a `passagem` (envio aceito),
    se `request.POST.get("depois") == "sair"`, retornar
    `redirect("/formacoes/?aviso=" + ("salvo" if _ha_resposta_na_secao(jornada,
    passagem.secao) else "saida"))` antes de qualquer outro destino.

  Nada muda antes desse ponto ([research R1](research.md#r1--salvar-e-sair-segundo-botão-de-envio-no-mesmo-formulário)).
- [X] T022 [US2] Em `trajetoria/interface/templates/interface/secao.html`, substituir o
  rodapé conforme o [contrato](contracts/rodape-secao.md#formulário-da-seção):
  - dentro do `<form>`: `<div class="acoes acoes-secao">` com
    `<button type="submit" class="primario">Salvar e continuar</button>` e
    `<button type="submit" name="depois" value="sair" class="secundario">Salvar e sair</button>`;
  - depois do `</form>`: `<div class="saidas">` com o parágrafo "Voltar à seção anterior"
    (quando `anterior`) e a nota atual, e o parágrafo
    `<a href="/formacoes/">Sair sem salvar esta seção</a>` com a nota
    `SAIR_SEM_SALVAR_NOTA` (passada pela view).
- [X] T023 [US2] Em `trajetoria/interface/templates/interface/estilo.css`, acrescentar
  ([research R10](research.md#r10--rodapé-hierarquia-largura-e-separação-mf-06-mf-14)):
  - `.acoes-secao { flex-direction: column; align-items: flex-start; }`;
  - `@media (max-width: 30em) { .acoes-secao, .acoes-secao button { width: 100%; }
    .acoes-secao { align-items: stretch; } }`;
  - `.saidas { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #565c65;
    font-size: 0.9375rem; }`.

  Não alterar `.acoes` nem `button`.

**Checkpoint**: US1 e US2 funcionam juntas; a matriz inteira passa.

---

## Phase 5: User Story 3 — Digitar sem enviar a Seção por acidente (Priority: P1)

**Goal**: Enter/"Ir" depois de digitar num campo de digitação não aciona nenhum envio
(FR-016, FR-017). *Corrigido após evidência de comportamento real do Chromium: Enter com
foco em rádio ou caixa fica fora (research R2).*

**Independent Test**: estrutura verificada por teste; comportamento verificado no
navegador (quickstart §2.1).

### Tests for User Story 3 ⚠️

- [X] T024 [US3] Em `tests/interface/test_interface_rodape.py`, teste estrutural: no
  `<form>` da Seção, o **primeiro** `button` com `type="submit"` (ou sem `type`) tem os
  atributos `disabled` e `hidden`, e nenhum `input type="submit"` o precede. Os botões
  visíveis seguintes não têm `disabled`. Vale para uma Seção com texto (Seção 3) e para
  a reapresentação com erro. Deve falhar.

### Implementation for User Story 3

- [X] T025 [US3] Em `trajetoria/interface/templates/interface/secao.html`, inserir como
  primeiro filho do `<form>`, logo depois de `{% csrf_token %}`:
  `<button type="submit" disabled hidden>Salvar</button>`
  ([research R2](research.md#r2--enterir-botão-de-envio-padrão-desabilitado)).
  Conferir que nenhuma regra de `estilo.css` dá `display` a `button` (o `[hidden]` do
  navegador deve prevalecer).
- [X] T026 [US3] Verificar no painel de navegador (Chromium) o quickstart §2.1, passos 1
  a 4 (Enter em campo de texto, na descrição de "Outro" e num rádio não envia; Enter e
  Espaço nos botões enviam). Registrar o resultado na descrição do PR.

**Checkpoint**: Enter bloqueado sem JavaScript.

---

## Phase 6: User Story 4 — Controles de escolha e escala: correção única (Priority: P1)

**Goal**: célula ou linha inteira tocável; escala de 1 a 5 numa linha até 200% e quebra
alinhada nas escalas longas; `radiogroup` só com as Opções (FR-018 a FR-022). **MF-04 +
MF-05 + UX-19 numa única entrega.**

**Independent Test**: estrutura acessível por teste; medidas pelo quickstart §2.2 e §2.3.

### Tests for User Story 4 ⚠️

- [X] T027 [P] [US4] Em `tests/interface/test_interface_secao.py`, testes de marcação
  ([contracts/telas.md](contracts/telas.md#controles-de-pergunta-perguntasthtml-também-na-prévia-do-editor)).
  Devem falhar.
  - Escolha única em rádios e escala:
    - o `fieldset.pergunta` **não** tem `role` nem `aria-required`;
    - a `legend` tem `id="pN-enunciado"`;
    - existe um elemento com `role="radiogroup"` e `aria-labelledby="pN-enunciado"`
      (com `aria-required="true"` se obrigatória) que contém **todos** os
      `input type="radio"` da Pergunta e **nenhum** `input` `pN-remover`;
    - o `pN-remover` continua dentro do `fieldset`;
    - `aria-invalid` e `aria-describedby` continuam no `fieldset`.
  - Escala: o `radiogroup` é o `div.escala`.
  - Escolha múltipla e lista suspensa: marcação inalterada.
- [X] T028 [P] [US4] Em `tests/editor/test_editor_previa.py`, confirmar que a prévia de
  Seção continua passando com a nova marcação. Acrescentar uma asserção de que a prévia
  contém `role="radiogroup"` só em volta das Opções de uma escala (a prévia reutiliza os
  controles; FR-045).

### Implementation for User Story 4

- [X] T029 [US4] Em `trajetoria/interface/templates/interface/perguntas/escala.html`
  ([research R7](research.md#r7--grupo-de-rádios-sem-a-caixa-de-remoção-ux-19)):
  - retirar `role="radiogroup"` e `aria-required` do `fieldset`;
  - dar `id="{{ item.nome }}-enunciado"` à `legend`;
  - no `<div class="escala">`, acrescentar `role="radiogroup"`,
    `aria-labelledby="{{ item.nome }}-enunciado"` e
    `{% if item.pergunta.obrigatoria %} aria-required="true"{% endif %}`.
- [X] T030 [US4] Em `trajetoria/interface/templates/interface/perguntas/escolha_unica.html`
  (ramo de rádios): as mesmas mudanças no `fieldset` e na `legend`; envolver o
  `{% for opcao %}` num `<div class="opcoes" role="radiogroup" aria-labelledby="{{ item.nome }}-enunciado"{% if item.pergunta.obrigatoria %} aria-required="true"{% endif %}>`.
  O include `_complemento_remover.html` fica **fora** desse `div` e dentro do `fieldset`.
- [X] T031 [US4] Em `trajetoria/interface/templates/interface/estilo.css`, acrescentar
  ([research R5, R6](research.md#r5--área-ativável-de-opções-e-pontos-mf-04)):
  - `.pergunta .opcao { position: relative; }`;
  - `.pergunta .opcao label::after { content: ""; position: absolute; inset: 0; }`;
  - `.pergunta .escala { display: grid; grid-template-columns: repeat(auto-fit, minmax(44px, 1fr)); gap: 0.25rem 0; max-width: 30rem; }`;
  - `.pergunta .escala .opcao { flex-direction: column; align-items: center; gap: 0.25rem; min-width: 0; }`;
  - `.pergunta .escala .opcao label { flex: none; text-align: center; padding: 0; }`.

  Substituir as regras antigas `.escala { display: flex; … }` e `.escala .opcao {
  min-width: 2.75rem; }` pelas novas: `class="escala"` só existe em
  `perguntas/escala.html` (o editor usa a palavra só como texto em `pergunta.html`).
  Reconfirmar com `grep -rn 'class="escala' trajetoria/`.
- [X] T032 [US4] Medir pelo quickstart §2.2 (área ativável, Seção 8 de Elisa a 375×667) e
  §2.3 (escala de 5 pontos numa linha em 320–430 px × 100–200%; escala de 11 pontos criada
  numa Versão de teste pelo editor sem rolagem horizontal). Ajustar o CSS de T031 até
  `[]` e `1` linha. Registrar o resultado na descrição do PR.

**Checkpoint**: controles corrigidos de forma genérica; a prévia do editor acompanha.

---

## Phase 7: User Story 5 — Saber em que Seção estou e sobre qual formação (Priority: P2)

**Goal**: `h1` = título da Seção; "Você está respondendo sobre:"; `h1` "Concluir a
pesquisa" (FR-023 a FR-025).

**Independent Test**: percurso de Diego com `h1` e linha de contexto verificados.

### Tests for User Story 5 ⚠️

- [X] T033 [P] [US5] Em `tests/interface/test_interface_secao.py` (devem falhar):
  - em toda Seção da baseline com título, o único `h1` é o título da Seção, e o título da
    Versão não é `h1`;
  - na Seção sem título, o `h1` é o título da Versão;
  - o `<title>` da Seção sem título continua "Seção 13 — …";
  - a linha de contexto contém "Você está respondendo sobre:" e não "Sobre a sua
    formação:".

  Ajustar o teste existente que procura "Sobre a sua formação" nas Seções.
- [X] T034 [P] [US5] Em `tests/interface/test_interface_conclusao.py`: o `h1` da tela de
  conclusão é "Concluir a pesquisa", e não há `h2` "Concluir a pesquisa". O contexto
  completo continua com o `h2` "Sobre a sua formação".

### Implementation for User Story 5

- [X] T035 [US5] Em `trajetoria/interface/templates/interface/secao.html`, trocar
  `<h1>{{ titulo_pesquisa }}</h1>` por
  `<h1>{% if passagem.secao.titulo %}{{ passagem.secao.titulo }}{% else %}{{ titulo_pesquisa }}{% endif %}</h1>`
  e remover o `<h2>` da Seção. Ordem final do topo conforme FR-024: aviso, `h1`, resumo,
  contexto, abertura, texto da Seção.
- [X] T036 [US5] Em `trajetoria/interface/templates/interface/contexto_compacto.html`,
  trocar o rótulo para "Você está respondendo sobre:" (mesmo `id="titulo-contexto"`).
- [X] T037 [US5] Em `trajetoria/interface/templates/interface/conclusao.html`, trocar
  `<h1>{{ titulo_pesquisa }}</h1>` e o `<h2>Concluir a pesquisa</h2>` por um único
  `<h1>Concluir a pesquisa</h1>`, antes do contexto. Não remover `titulo_pesquisa` do
  contexto da view, que pode continuar sem uso.

**Checkpoint**: títulos e contexto corretos.

---

## Phase 8: User Story 6 — Ver minha trajetória no Ifes e escolher a formação (Priority: P2)

**Goal**: "Sua trajetória no Ifes", formação compacta, entrada pelo fato, seleção sem
contagem, "sem pesquisa" omitido, ambiguidade mantida, ordem da 007 (FR-030 a FR-037).

**Independent Test**: Ana, Maria e Diego; Pessoa com formação em ambiguidade; formação sem
atributos.

### Tests for User Story 6 ⚠️

- [X] T038 [P] [US6] Em `tests/interface/test_interface_formacoes.py`, junto dos testes
  puros existentes (`test_contexto_com_todos_os_atributos_na_ordem`, sem banco), testar
  `complemento_da_formacao` com objeto simples (`types.SimpleNamespace`):
  - todos informados → `"Graduação · Presencial · Bacharelado"` (valores do teste);
  - parte ausente → só os presentes;
  - nenhum → `""`.
- [X] T039 [US6] Em `tests/interface/test_interface_formacoes.py`, testes (devem falhar):
  - (a) `h1` "Sua trajetória no Ifes" nas cinco situações (resolvida, seleção, sem
    entrada pendente, sem pesquisa, sem formação);
  - (b) entrada resolvida de Ana: "Você concluiu " + `resumo_da_formacao(conclusão)` +
    "." e "O Ifes quer saber como sua trajetória seguiu depois disso.";
  - (c) formação sem nenhum atributo: toda Conclusão da fonte simulada tem curso, então,
    com Ana, aplicar `monkeypatch.setattr("trajetoria.interface.views.resumo_da_formacao",
    lambda c: "")`. Esperado: "Encontramos uma formação sua no Ifes.", sem "Você concluiu"
    e sem texto truncado;
  - (d) nenhuma ocorrência de "campus" no texto da tela;
  - (e) seleção de Maria: "Cada formação tem sua própria pesquisa." sem número de
    formações; a ordem das formações no HTML é igual a `situacao_de_entrada(pessoa).pendentes`;
  - (f) Diego depois de concluir: nenhuma ocorrência de "Sem pesquisa disponível no
    momento." e "Pesquisa já respondida." presente;
  - (g) formação em ambiguidade operacional: "A pesquisa referente a esta formação não
    está disponível neste momento." presente;
  - (h) Maria: "Data de conclusão" ausente e o ano presente na linha;
  - (i) cada formação com complemento mostra a linha complementar.

  Ajustar os testes existentes que procuram "Sobre qual formação", "Suas formações" e
  "Esta pesquisa refere-se".
- [X] T040 [P] [US6] Em `tests/interface/test_interface_encerramento.py`, ajustar a
  verificação que espera "Sem pesquisa disponível no momento" por formação. A situação
  geral "No momento, não há pesquisa disponível para as suas formações." continua.

### Implementation for User Story 6

- [X] T041 [US6] Em `trajetoria/interface/apresentacao.py`, acrescentar
  `complemento_da_formacao(conclusao) -> str`: `" · ".join` de `nivel`, `modalidade`,
  `forma_oferta`, só os não `None`. Docstring citando FR-034 e 007/DP-702 (sem desempate,
  sem atributo deduzido).
- [X] T042 [US6] Em `trajetoria/interface/mensagens.py`:
  - `SITUACAO_DA_FORMACAO[SituacaoDaFormacao.SEM_PESQUISA] = None`, com comentário
    citando FR-036;
  - acrescentar `ENTRADA_FATO = "Você concluiu {linha}."`,
    `ENTRADA_SEM_ATRIBUTOS = "Encontramos uma formação sua no Ifes."`,
    `ENTRADA_CONTINUACAO = "O Ifes quer saber como sua trajetória seguiu depois disso."`,
    `SELECAO = "Cada formação tem sua própria pesquisa. Escolha por qual começar ou
    continuar; as outras continuam disponíveis aqui."` e
    `TITULO_TRAJETORIA = "Sua trajetória no Ifes"`.
- [X] T043 [US6] Em `trajetoria/interface/views.py`:
  - `_TELA_DE_FORMACOES`: título `mensagens.TITULO_TRAJETORIA` em todas as entradas,
    mantendo as mensagens de estado;
  - `_formacao_apresentada`: devolve `pk`, `linha` (`resumo_da_formacao`),
    `complemento` (`complemento_da_formacao`), `situacao` e `acao`; deixa de devolver
    `contexto`;
  - `formacoes`: passa `entrada_fato` (texto de `ENTRADA_FATO` com a linha da formação
    principal, ou `ENTRADA_SEM_ATRIBUTOS` se a linha for vazia), `entrada_continuacao` e
    `selecao`. Nenhuma ordenação (FR-035).
- [X] T044 [US6] Reescrever `trajetoria/interface/templates/interface/formacoes.html`
  conforme [contracts/telas.md](contracts/telas.md#trajetória-formacoeshtml):
  - aviso → `h1` → bloco por situação;
  - um `include` local (`interface/formacao.html`, novo, três linhas) para
    `<p class="formacao"><strong>{{ formacao.linha|default:"Dados da formação não informados pela fonte." }}</strong>{% if formacao.complemento %}<br><span class="nota">{{ formacao.complemento }}</span>{% endif %}</p>`;
  - situação em `<p>` só `{% if formacao.situacao %}`;
  - `h2` "Suas outras formações" mantido.
- [X] T045 [US6] Trocar o rótulo "Voltar às suas formações" por "Ver sua trajetória no
  Ifes" em `trajetoria/interface/templates/interface/aviso.html` e
  `trajetoria/interface/templates/interface/concluida.html`. Ajustar testes que procuram
  o rótulo antigo (`grep -rn "Voltar às suas formações" tests/`).

**Checkpoint**: trajetória pronta; ordem e regras da 007 intactas.

---

## Phase 9: User Story 7 — Erros e pendências encontráveis por leitor de tela (Priority: P2)

**Goal**: resumo recebe foco ao carregar, sem JavaScript, mantendo o anúncio (FR-027,
FR-028).

**Independent Test**: reapresentação com pendência e com erro tem o resumo com
`autofocus`, `tabindex="-1"` e `role="alert"`.

### Tests for User Story 7 ⚠️

- [X] T046 [P] [US7] Em `tests/interface/test_interface_acessibilidade.py`, teste (deve
  falhar): nas telas `s1-erros`, `s2-pendencias` e `s1-pendencias-vazia`, existe
  exatamente **um** elemento com `autofocus`. Ele é o resumo, tem `tabindex="-1"` e
  `role="alert"`, e contém as ligações para as Perguntas. Nenhuma outra tela da jornada
  tem `autofocus`.

### Implementation for User Story 7

- [X] T047 [US7] Em `trajetoria/interface/templates/interface/secao.html`, acrescentar
  `tabindex="-1" autofocus` ao `div` do resumo ([research R8](research.md#r8--foco-no-resumo-ao-carregar-sem-javascript-mf-10)),
  mantendo `role="alert"`.

**Checkpoint**: foco e anúncio; efeito em leitores fica para o roteiro [T].

---

## Phase 10: User Story 10 — Telas institucionais sem regressão (Priority: P2)

**Goal**: editor (009), acompanhamento (011) e demonstração sem mudança visível; prévia
acompanha os controles (FR-045; SC-014).

**Independent Test**: suítes verdes e capturas idênticas às de T002.

- [X] T048 [US10] Rodar `uv run pytest tests/editor tests/acompanhamento
  tests/interface/test_demonstracao_operador.py tests/interface/test_interface_demonstracao.py`
  e corrigir regressões **só** no CSS ou nos templates da interface (nunca nos apps do
  editor, do acompanhamento ou da demonstração).
- [X] T049 [US10] Repetir as capturas de T002 (quickstart §2.6) e comparar. Qualquer
  diferença fora da prévia de Seção é regressão: restringir o seletor em `estilo.css`.

**Checkpoint**: nenhuma regressão fora da jornada.

---

## Phase 11: User Story 8 — Encerramento que fecha a conversa (Priority: P3)

**Goal**: frase de registro com o curso; agradecimento único; só a ligação para a
trajetória (FR-038 a FR-041).

**Independent Test**: confirmação com e sem texto de encerramento e com curso ausente.

### Tests for User Story 8 ⚠️

- [X] T050 [P] [US8] Em `tests/interface/test_interface_conclusao.py`, testes (devem
  falhar):
  - (a) com curso: "Suas respostas sobre {curso} foram registradas.";
  - (b) sem curso: toda Conclusão da fonte simulada tem curso, então concluir a
    Participação de Ana e, antes do GET de confirmação, aplicar no banco de teste
    `ConclusaoAcademica.objects.filter(pk=ana.conclusao_id).update(curso=None)` (o campo
    aceita nulo; a restrição só proíbe texto vazio). Esperado: "Suas respostas foram
    registradas.", sem "sobre";
  - (c) Versão com `texto_encerramento`: "Obrigado pela sua participação." ausente e o
    texto da Versão presente;
  - (d) Versão sem `texto_encerramento`: "Obrigado pela sua participação." exatamente uma
    vez;
  - (e) única ligação do conteúdo principal é "Ver sua trajetória no Ifes";
  - (f) nenhuma frase de finalidade, contato ou periodicidade (sem "entrar em contato",
    "próxima", "anos").

  Ajustar o teste existente que procura "Obrigado".

### Implementation for User Story 8

- [X] T051 [US8] Em `trajetoria/interface/mensagens.py`, acrescentar
  `REGISTRADAS_CURSO = "Suas respostas sobre {curso} foram registradas."`,
  `REGISTRADAS = "Suas respostas foram registradas."` e
  `AGRADECIMENTO = "Obrigado pela sua participação."`.
- [X] T052 [US8] Em `trajetoria/interface/views.py`, `concluida`: passar
  `registro = REGISTRADAS_CURSO.format(curso=…)` se `participacao.conclusao.curso`,
  senão `REGISTRADAS`, e `agradecimento = AGRADECIMENTO` só se
  `not versao.texto_encerramento`.
- [X] T053 [US8] Em `trajetoria/interface/templates/interface/concluida.html`: `h1`
  "Pesquisa concluída"; `<p>{{ registro }}</p>`;
  `{% if agradecimento %}<p>{{ agradecimento }}</p>{% endif %}`; contexto e encerramento
  como hoje; ligação já renomeada em T045.

**Checkpoint**: confirmação com um agradecimento.

---

## Phase 12: User Story 9 — Pequenos alvos e instrução de falha de envio (Priority: P3)

**Goal**: ligações da conclusão com 44 px; página de CSRF sem "recarregue" (FR-026,
FR-029).

**Independent Test**: medição na tela de conclusão; texto da página de CSRF.

### Tests for User Story 9 ⚠️

- [X] T054 [P] [US9] Em `tests/interface/test_interface_conclusao.py`: a lista de Seções
  tem a classe `lista-secoes`.
- [X] T055 [P] [US9] Em `tests/interface/test_interface_fronteiras.py`, junto de
  `test_csrf_em_toda_escrita`: a resposta 403 de CSRF contém "Volte à página anterior e
  envie novamente." e **não** contém "recarregue".

### Implementation for User Story 9

- [X] T056 [US9] Em `trajetoria/interface/templates/interface/conclusao.html`, dar
  `class="lista-secoes"` à `<ul>` de Seções. Em `estilo.css`:
  `.lista-secoes { list-style: none; padding: 0; }` e
  `.lista-secoes a { display: block; min-height: 2.75rem; padding: 0.625rem 0; }`.
- [X] T057 [US9] Em `trajetoria/interface/templates/403_csrf.html`, trocar o parágrafo
  "Volte à página anterior, recarregue e tente novamente." por "Volte à página anterior e
  envie novamente.".
- [X] T058 [US9] Medir pelo quickstart §2.4: botões e separação do rodapé a 375 e 480 px
  (FR-015); ligações da conclusão ≥ 44 px (FR-026). Registrar na descrição do PR.

**Checkpoint**: todas as histórias entregues.

---

## Phase 13: Polish & Cross-Cutting Concerns

- [X] T059 Em `tests/interface/test_interface_acessibilidade.py`, acrescentar ao fixture
  `telas` os estados `formacoes-aviso-salvo`, `formacoes-aviso-saida` e
  `s8-rodape-erro` (Seção 8 com erro de forma) e confirmar
  `test_todas_as_telas_passam_no_verificador` e `test_titulos_distintos_por_tela` (SC-013).
- [X] T060 [P] Em `specs/008-interface-navegavel-pesquisa/spec.md`, acrescentar
  "*(Revisado pela 014 — ver `specs/014-polish-jornada-egresso/spec.md`)*" ao fim de
  FR-020, FR-021, FR-023, FR-032, FR-049, FR-050, FR-062, FR-071, FR-076 e FR-077, sem
  reescrever o texto original (mesmo padrão da revisão de FR-043).
- [X] T061 [P] Em `specs/008-interface-navegavel-pesquisa/contracts/rotas.md`, atualizar
  a seção da Seção:
  - itens 2 e 6 (`h1` da Seção, sem `h2`);
  - item 4 ("Você está respondendo sobre:");
  - itens 8 a 10 (rodapé com quatro ações, apontando para
    `specs/014-polish-jornada-egresso/contracts/rodape-secao.md`);
  - remover `&salvo=1` do texto de `?pendencias=1` e do passo 4 do POST.
- [X] T062 Executar o quickstart §2.5 (trajetória na primeira tela: Ana, Maria, Diego a
  375×667) e §2.7 (percurso de leitura). Registrar na descrição do PR.
- [X] T063 Verificações finais (SC-013):
  - `uv run pytest` (suíte completa) verde;
  - `uv run ruff check .` e `uv run ruff format --check .`;
  - `uv run python manage.py makemigrations --check --dry-run` sem mudanças;
  - `grep -rn "<script" trajetoria/interface/templates trajetoria/demonstracao/templates`
    vazio;
  - `grep -rn 'autocomplete' trajetoria/interface/templates` vazio (FR-047);
  - `grep -rn "sorted(" trajetoria/interface/views.py` sem ordenação de formações
    (FR-035).
- [X] T064 Revisão final da Matriz de comportamento do rodapé contra
  `tests/interface/test_interface_rodape.py`: cada célula do
  [contrato](contracts/rodape-secao.md) tem teste correspondente (SC-015). Conferir que o
  roteiro [T] do quickstart §3 está atualizado; ele é validação **posterior** e não
  bloqueia o fechamento (FR-050).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências.
- **Foundational (Phase 2)**: depende de T001; bloqueia US1 e US2.
- **US1 (Phase 3)** → **US2 (Phase 4)**: US2 usa os textos e o título de US1 e edita os
  mesmos arquivos (`secao.html`, `views.py`, `mensagens.py`, `estilo.css`).
- **US3 (Phase 5)**: depois de US2, porque o bloqueador precisa preceder os **dois**
  botões.
- **US4 (Phase 6)**: independe de US1–US3 no comportamento; edita `estilo.css` e
  `perguntas/escala.html` / `escolha_unica.html`, que T014 também tocou. Fazer depois de
  US1.
- **US5 (Phase 7)**: depois de US3 (`secao.html`).
- **US6 (Phase 8)**: depois de US1 (`formacoes.html`, T015) e US2 (avisos em
  `formacoes`, T021).
- **US7 (Phase 9)**: depois de US5 (`secao.html`).
- **US10 (Phase 10)**: depois de US1, US2 e US4 (todas as mudanças de CSS); repetir T048
  no fim.
- **US8 (Phase 11)**: depois de T045 (ligação em `concluida.html`).
- **US9 (Phase 12)**: depois de US5 (`conclusao.html`, T037).
- **Polish (Phase 13)**: depois de todas as histórias.

### User Story Dependencies

```text
T001 ─► T003/T004 ─► US1 ─► US2 ─► US3 ─► US5 ─► US7
                      │      │             └────► US9
                      │      └────────────────────► US6 ─► US8
                      └─► US4 ─► US10 (após US1, US2, US4)
                                         todas ─► Polish
```

### Within Each User Story

- Testes primeiro (devem falhar), depois implementação, depois a medição do quickstart
  quando houver.
- `mensagens.py` antes de `views.py`; `views.py` antes dos templates que usam as variáveis
  novas.

### Parallel Opportunities

- T002 em paralelo com T001.
- T004 em paralelo com T003.
- Em cada história, as tarefas de teste marcadas [P] (arquivos de teste diferentes).
- T038 (teste puro, sem banco) em paralelo com T040.
- T060 e T061 (documentos da 008) em paralelo entre si e com T062.

---

## Parallel Example: User Story 1

```text
# Testes de US1, em arquivos diferentes, juntos:
T005 tests/interface/test_interface_secao.py
T006 tests/interface/test_interface_gravacao.py
T007 tests/interface/test_interface_formacoes.py
T008 tests/interface/test_interface_acessibilidade.py
# Depois, em sequência: T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016
```

## Parallel Example: User Story 4

```text
T027 tests/interface/test_interface_secao.py
T028 tests/editor/test_editor_previa.py
# Depois: T029 → T030 → T031 → T032
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1 e Phase 2.
2. Phase 3 (US1): pendência ≠ erro, Seção incompleta comunicada, nenhuma mensagem falsa.
3. **Parar e validar**: `uv run pytest tests/interface`.

### Incremental Delivery

1. US1 → US2 (Salvar e sair + matriz) → US3 (Enter) → US4 (controles): entrega P1 completa,
   que resolve os achados P0/P1 da auditoria mobile.
2. US5, US6, US7 e US10: identidade, acessibilidade e não regressão.
3. US8, US9: refinamentos P3.
4. Polish: documentos da 008, quickstart, verificações finais.

### Fechamento

- Fecha com os testes automatizados (FR-049) e as medições do quickstart §2 registradas
  no PR.
- O roteiro em aparelho real (quickstart §3) é **posterior** e não bloqueia (FR-050).
- MF-03 continua fora (FR-047).
