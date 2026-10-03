---

description: "Tasks da Feature 015 — Foundations e validação da identidade visual da jornada do egresso"
---

# Tasks: Foundations e validação da identidade visual da jornada do egresso

> **Estado (2026-10-03): Feature 015 INCOMPLETA — NÃO pronta para merge.**
>
> - **44/46 tasks concluídas.**
> - **T015 BLOQUEADA por D-03** (assinatura oficial: o ZIP oficial do Ifes não contém SVG;
>   nenhum substituto, PNG ou EPS convertido é usado).
> - **T041 BLOQUEADA por D-03** (rodada final do gate depende da assinatura).
> - **Gate final NÃO aprovado.** SC-001 é impossível e SC-002 só parcialmente medível sem o
>   ativo oficial.
> - As capturas e medições atuais foram feitas **sem a assinatura oficial** e validam
>   **apenas** os aspectos que não dependem dela ([validacao.md](validacao.md)).
> - Ao receber o SVG: retomar nesta branch → T015 → T041 (remedir SC-001 e SC-002 com o
>   ativo real) → suíte completa e regressões → atualizar `validacao.md` → só então o PR.

**Input**: Design documents from `specs/015-identidade-visual-jornada/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/tokens.md](contracts/tokens.md),
[contracts/shell.md](contracts/shell.md), [contracts/telas.md](contracts/telas.md),
[contracts/registro-validacao.md](contracts/registro-validacao.md),
[quickstart.md](quickstart.md)

**Stack**: Python 3.13, Django 5.2 LTS, PostgreSQL 16+, uv, pytest + pytest-django, ruff
([ADR 0001](../../docs/adr/0001-stack-inicial.md)). **Nenhuma dependência nova. Zero
modelos, zero migrações, zero JavaScript, zero recurso externo.** Só o app
`trajetoria/interface/` muda (mais testes).

**Tests**: obrigatórios e escritos **antes** da implementação correspondente
(Const. XXVI; spec FR-046). Teste de regra nova DEVE falhar primeiro. Testes existentes
que fixam marcação alterada de propósito são **ajustados**, nunca removidos. Medidas
visuais (alturas, contraste renderizado, reflow, capturas) são do **gate** (Phase 9), não
de teste automatizado.

**Organization**: fases por história da spec: US1, US2, US3 (P1); US4, US5, US6 (P2);
depois o gate e o fechamento. Arquivos editados por várias histórias, **sempre em
sequência**: `interface/estilo.css`, `interface/jornada.css`, `interface/base.html`,
`interface/views.py`, `interface/mensagens.py`, `interface/formacoes.html`,
`tests/interface/test_interface_identidade.py`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: história da spec (US1…US6)
- **⛔ D-03**: bloqueada até a ACS fornecer o SVG oficial da assinatura (research R3)

## Convenções para todas as tarefas

- **Duas camadas de estilo** ([research R1](research.md#r1--onde-vivem-as-foundations-e-como-a-mudança-fica-restrita-à-jornada)):
  - `trajetoria/interface/templates/interface/estilo.css` (compartilhada com editor,
    acompanhamento e 403/404/500) recebe **só**: o `:root` com os tokens; regras sob
    `.pergunta` / `.escala` / `.opcoes`; regras de classes **exclusivas** da jornada
    (`.com-pendencia`, `.resumo-pendencias`).
  - **Nunca** alterar em `estilo.css` as regras de seletores usados pelo editor ou pelo
    acompanhamento: `a`, `button`, `.primario`, `.secundario`, `.botao`, `h1`–`h3`,
    `body`, `input`, `select`, `footer`, `.cabecalho`, `.faixa-demonstracao`, `.aviso`,
    `.lista-simples`, `.acoes`, `.nota`, `.resumo-erros`, `.erro`, `.com-erro`,
    `.explicacao`, `.opcao` (fora de `.pergunta`), `.texto-secao`. Refinamentos desses
    seletores na jornada vão em `jornada.css`; para Perguntas, sob `.pergunta …` em
    `estilo.css` (valem também para a prévia, FR-040).
  - `trajetoria/interface/templates/interface/jornada.css` é incluída **só** por
    `interface/base.html`.
- **Tokens**: nomes e valores exatamente os de [contracts/tokens.md](contracts/tokens.md);
  toda cor nova no CSS é `var(--…)`; contraste em comentário ao lado de cada token de cor.
  **Valor mergeado da ação: Direção B** (`--cor-acao: #1351b4`,
  `--cor-acao-forte: #0c326f`).
- **Só apresentação**: textos, ordem, rotas, comportamento, `name`/`value` de formulário,
  `role`/`aria-*` exigidos pela 014/008 **não mudam** (FR-036). Únicas mudanças de
  marcação: controles de demonstração na faixa; cabeçalho/rodapé novos; classe de
  variante do aviso; `<strong>` na linha da frase de entrada; `span.situacao`; wrapper do
  topo da confirmação ([contracts/telas.md](contracts/telas.md)).
- **Nada por Pergunta** (008 FR-034): nenhuma regra visual por Pergunta, Seção ou Opção
  específicas.
- **Testes**: em `tests/interface/` (e `tests/editor/test_editor_previa.py` para a
  prévia), prefixo `test_interface_`, sem `__init__.py`, `pytestmark =
  pytest.mark.django_db`, auxiliares de `tests/interface/construcao_interface.py`. Só
  Pessoas da fonte simulada.
- **Capturas** do gate: **nunca** versionadas; salvas fora do repositório (diretório de
  rascunho da sessão) e anexadas ao PR, com identificador
  `R{rodada}-G{situação}-{A|B}-{largura}-{fonte}` (R10).

## Limites desta lista (não criar)

- Modelo, migração, tabela, coluna, `<script>`, JavaScript, dependência, fonte externa,
  `staticfiles`, `@import`, `url(` externo, CDN.
- Feature flag, configuração, variável de ambiente, preferência, parâmetro de endereço,
  opção administrativa ou condicional de qualquer tipo para a Direção A/B (FR-012).
- Tema temporário, folha duplicada, HTML paralelo, página fictícia (FR-038); duplicação
  ou condicional para isolar as quatro situações do gate (FR-039).
- Marca substituta, desenho provisório, PNG/EPS convertido ou redesenho da assinatura
  (research R3; D-03).
- Cards, sombras, ícones, biblioteca, componente genérico, design system (FR-008,
  FR-030 nesta versão, FR-041).
- Qualquer mudança em `trajetoria/editor/`, `trajetoria/acompanhamento/`,
  `403_csrf.html`, `404.html`, `500.html`, modelos e features 001–014. Em
  `trajetoria/demonstracao/`, só o mínimo exigido por D7 (ver T045), sem mudança funcional.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmar a base e registrar o "antes" para a não regressão.

- [X] T001 Confirmar a base na branch `claude/feature-015-identidade-visual` sincronizada
  com `main` (`b4476ce` ou posterior): `uv run pytest` verde (referência: 1807 passed),
  `uv run ruff check .` limpo, `uv run python manage.py makemigrations --check --dry-run`
  sem mudanças. Registrar o número de testes para o fechamento.
- [X] T002 [P] Capturar o "antes" administrativo para SC-012 (quickstart §6), com a
  demonstração no ar (quickstart §1, banco `trajetoria_015`): lista de Pesquisas, edição
  de Pergunta e prévia de Seção (009), painel de uma Campanha (011), a 375 e 1280 px,
  identificadores `R0-ADM-{tela}-{largura}`, salvas **fora do repositório**.
- [X] T003 [P] Capturar o "antes" das situações G1–G4 (quickstart §3) a 375 e 1280 px,
  identificadores `R0-G{n}-ATUAL-{largura}-100`, fora do repositório (referência para a
  comparação do registro).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: tokens, camadas de estilo e utilitários de teste. **Nenhuma mudança
visual** ao fim desta fase.

- [X] T004 Mover o leitor de cascata do IV-03 de `tests/interface/test_interface_secao.py`
  para `tests/interface/construcao_interface.py`, generalizado:
  `folhas(html) -> str` (concatena os `<style>` da página, sem comentários);
  `tokens(html) -> dict[str, str]` (propriedades do `:root`);
  `valor(html, ancestrais: set[str], classe: str, tag: str = "", propriedade: str = "color") -> str`
  (última regra de maior especificidade de classes que casa, resolvendo `var(--x)` pelos
  tokens). Atualizar `test_interface_secao.py` para usá-lo; os três testes do IV-03
  continuam verdes.
- [X] T005 Escrever (deve falhar) em `tests/interface/test_interface_identidade.py` os
  testes de tokens ([contracts/tokens.md](contracts/tokens.md)): todos os tokens do
  contrato definidos **uma vez** no `:root` de `estilo.css`; `--cor-acao` = `#1351b4` e
  `--cor-acao-forte` = `#0c326f` (Direção B, FR-014); `--cor-sucesso` = `#195128` e
  `--cor-marca` = `#2f9e41`; cada token de cor com comentário de contraste na mesma
  linha; os hex `#1351b4`, `#0c326f`, `#00420c` aparecem **só** nas definições de
  `--cor-acao`/`--cor-acao-forte` (ou em comentário delas), e `#195128` só em
  `--cor-sucesso` (FR-011, SC-010).
- [X] T006 Escrever (deve falhar onde aplicável) em `test_interface_identidade.py`:
  nenhum arquivo `.py` nem template em `trajetoria/` referencia `cor-acao`, "direcao" de
  cor ou valores das Direções (FR-012); `--cor-marca` nunca aparece em `color:` nem em
  `background` em nenhuma folha (FR-003); em `estilo.css`, nenhuma regra dos seletores
  compartilhados listados nas Convenções usa `var(--` (R1).
- [X] T007 Implementar o `:root` em `trajetoria/interface/templates/interface/estilo.css`
  com todos os tokens de [contracts/tokens.md](contracts/tokens.md) e contraste em
  comentário; **nenhuma regra existente muda** nesta tarefa. T005 e T006 passam.
- [X] T008 Escrever (deve falhar) em `test_interface_identidade.py` a matriz de inclusão
  ([contracts/telas.md](contracts/telas.md#matriz-de-inclusão-das-folhas)): o texto de
  `jornada.css` (marcador de cabeçalho da folha) está no `<style>` de trajetória, Seção,
  conclusão, confirmação, tela de estado, entrada e operador da demonstração; **não** está
  no de lista de Pesquisas e prévia de Seção (009), painel de Campanha (011), 403, 404 e
  500.
- [X] T009 Criar `trajetoria/interface/templates/interface/jornada.css` (comentário de
  cabeçalho com o propósito e a regra de inclusão; sem regras ainda) e incluí-la inline em
  `trajetoria/interface/templates/interface/base.html`, depois de `estilo.css`. T008 passa;
  suíte completa verde.

**Checkpoint**: tokens e camadas prontos; nenhuma mudança visual; editor e
acompanhamento intactos por construção.

---

## Phase 3: User Story 1 — Reconhecer o Ifes ao abrir qualquer tela da jornada (Priority: P1) 🎯 MVP

**Goal**: shell institucional da jornada (faixa, cabeçalho, rodapé) e os elementos de
ação da jornada em tokens.

**Independent Test**: trajetória de Maria, Seção 8 e confirmação a 375 e 1280 px;
cabeçalho, faixa e rodapé conforme [contracts/shell.md](contracts/shell.md).

### Tests for User Story 1 ⚠️

- [X] T010 [US1] Escrever (deve falhar) em `test_interface_identidade.py`: em toda tela da
  jornada, o `<header>` contém "Trajetória Ifes" como texto (fora de `h1` e de `<a>`) e
  "Acompanhamento de egressos"; "Pessoa fictícia: …", "Trocar de pessoa" e o formulário
  "Encerrar demonstração" ficam **dentro de `.faixa-demonstracao`** e **fora** do
  `<header>`, com os mesmos textos, destinos e CSRF; o rodapé contém "Instituto Federal do
  Espírito Santo" e, em demonstração, a linha de ambiente fictício; nenhuma página da
  jornada tem `<script>`, `<link rel=stylesheet>`, `<img src="http`, `@import` ou
  `url(` externo (FR-018, FR-037).
- [X] T011 [US1] Escrever (deve falhar) em `test_interface_identidade.py`, pelo leitor de
  cascata: borda superior do cabeçalho = `--cor-marca` com 4 px; divisores do cabeçalho e
  do rodapé = `--cor-borda-suave`; ligações (`a`) da jornada = `--cor-acao`;
  `button.primario` com fundo `--cor-acao`; `button.secundario` com borda e texto
  `--cor-acao`; hover/ativo = `--cor-acao-forte`; faixa com `--cor-demonstracao` e sem
  `--cor-marca`/`--cor-acao` (FR-021).

### Implementation for User Story 1

- [X] T012 [US1] Reestruturar `trajetoria/interface/templates/interface/base.html`
  conforme [contracts/shell.md](contracts/shell.md): controles de demonstração movidos
  para a faixa (textos, destinos e formulário inalterados); cabeçalho novo **sem** a
  assinatura (nenhum substituto — ⛔ D-03 em T015); rodapé novo. Título da página,
  "Pular para o conteúdo" e `<main>` inalterados.
- [X] T013 [US1] Regras de shell em `trajetoria/interface/templates/interface/jornada.css`:
  faixa (layout dos controles), cabeçalho (fio 4 px `--cor-marca`, fundo branco,
  `flex-wrap`, separador 1 px suave, nome 18/700, subtítulo 15 px suave só a partir de
  `30em`), rodapé (15 px suave, divisor suave); ligações e botões da jornada com tokens de
  ação, hover/ativo com `--cor-acao-forte`. T010 e T011 passam.
- [X] T014 [US1] Rodar `tests/interface` e `tests/editor`; ajustar **só** asserções que
  fixavam a posição antiga dos controles de demonstração (ex.:
  `tests/interface/test_interface_demonstracao.py`), sem remover verificação.
- [ ] T015 ⛔ BLOCKED D-03 [US1] Assinatura oficial, **somente após** a ACS fornecer o SVG
  horizontal colorido da marca sistêmica: (a) registrar em `research.md` R3 nome,
  origem e SHA-256 do arquivo recebido; (b) escrever teste (deve falhar) em
  `test_interface_identidade.py`: toda tela da jornada contém o SVG dentro de um elemento
  com `role="img"` e nome acessível "Instituto Federal do Espírito Santo", antes do nome
  do produto; o SHA-256 de `interface/assinatura.svg` é igual ao registrado; nenhuma tela
  administrativa nem 403/404/500 o contém; (c) adicionar
  `trajetoria/interface/templates/interface/assinatura.svg` **exatamente como recebido** e
  incluí-lo por `{% include %}` no cabeçalho de `base.html`; (d) dimensionar em
  `jornada.css` para símbolo ≥ 30 px e área de proteção ≥ 1 módulo, sem recorte.

**Checkpoint**: shell em toda a jornada; editor, acompanhamento e 403/404/500 sem mudança;
SC-001 pendente até T015.

---

## Phase 4: User Story 2 — Responder uma Seção longa com ritmo e estados visíveis (Priority: P1)

**Goal**: ritmo, tipografia e estados das Perguntas (jornada e prévia).

**Independent Test**: Seção 8 a 375, 390, 430 e 1280 px; 014 SC-006/SC-007 remedidos.

### Tests for User Story 2 ⚠️

- [X] T016 [US2] Escrever (deve falhar) em `test_interface_identidade.py`, na Seção 8, pelo
  leitor de cascata: `.pergunta` com `margin-bottom` = `--espaco-7` (48 px); enunciado
  (`legend`, `label.enunciado`) com 18 px, peso 600, entrelinha 1,4; `.explicacao`,
  `.descricao-escala`, `.obrigatoria` e a `.nota` do enunciado **sob `.pergunta`** com
  15 px e `--cor-texto-suave`; `accent-color` = `--cor-acao` em `.pergunta input`; existe
  regra de estado selecionado para `.pergunta .opcao:has(input:checked)` com acento de
  4 px em `--cor-acao`; `.escala .opcao` com contorno 1 px `--cor-borda-forte` e
  `border-radius: var(--raio)`; nenhuma regra sob `.pergunta` com `box-shadow` de
  elevação nem fundo de card (FR-022 a FR-025).
- [X] T017 [P] [US2] Escrever (deve falhar) em `tests/editor/test_editor_previa.py`: a prévia
  de Seção **não** inclui `jornada.css`; o enunciado na prévia tem 18 px/600 e o
  `accent-color` de ação (herdados de `.pergunta`); o `margin-bottom` efetivo de
  `.previa .pergunta` continua `0.5rem` (composição do editor preservada — FR-040).

### Implementation for User Story 2

- [X] T018 [US2] Em `trajetoria/interface/templates/interface/estilo.css`, regras sob
  `.pergunta`: ritmo (48 px entre Perguntas; 8 px enunciado → resposta); tipografia do
  enunciado; auxiliares 15 px suave (`.pergunta .explicacao`, `.pergunta
  .descricao-escala`, `.pergunta .obrigatoria`, `.pergunta legend .nota`). Não tocar
  `.explicacao`, `.erro`, `.nota` globais. T016 (parte de ritmo/tipografia) e T017
  passam.
- [X] T019 [US2] Em `estilo.css`, estados sob `.pergunta`: `accent-color: var(--cor-acao)`;
  selecionado por `:has(input:checked)` com acento 4 px sem deslocar o conteúdo e fundo
  `--cor-selecao`; hover só em `@media (hover: hover)`; células da escala com contorno
  1 px forte, `--raio` e vão horizontal de 4 px. Área ativável inalterada (014 R5/R6).
  T016 passa.
- [X] T020 [US2] Verificação rápida (antes de seguir): quickstart §3, G2 a 320, 375 e
  430 px com fonte a 100% e 200% — escala de 1 a 5 numa linha, sem rolagem horizontal,
  células e linhas ≥ 44×44 px e inteiramente ativáveis (014 SC-006, SC-007). Se falhar,
  corrigir T019 antes de continuar.

**Checkpoint**: Seções com ritmo e estados; prévia com tipografia e estados, composição
do editor intacta.

---

## Phase 5: User Story 3 — Entender pendência, erro, salvamento e conclusão (Priority: P1)

**Goal**: variantes de aviso, cores de estado por token, foco do resumo, topo de sucesso
na confirmação.

**Independent Test**: Seção 2 com pendências; Seção 8 com erro de forma; "Salvar e sair"
com e sem Resposta; aviso de situação e de percurso; confirmação.

### Tests for User Story 3 ⚠️

- [X] T021 [US3] Escrever (deve falhar) em `test_interface_identidade.py`:
  `mensagens.VARIANTE_DO_AVISO` tem exatamente as chaves de `mensagens.AVISOS`, com
  `salvo` → `sucesso` e `saida`, `situacao`, `percurso` → `informacao`; trajetória com
  `?aviso=salvo` tem `aviso aviso-sucesso` e acento `--cor-sucesso`; com `saida` e
  `situacao`, `aviso aviso-informacao` e acento `--cor-info`; Seção com `?aviso=percurso`,
  `aviso aviso-informacao`; textos dos avisos idênticos aos de `AVISOS` (FR-026).
- [X] T022 [US3] Escrever (deve falhar) em `test_interface_identidade.py`: na pendência,
  título do resumo, fio e frase por Pergunta e borda do campo resolvem para `--cor-info`;
  no erro de forma, para `--cor-erro`; acento lateral de 4 px nos dois resumos; existe
  regra `.resumo-erros:focus` (em `jornada.css`) com o mesmo contorno e halo de
  `:focus-visible`; o topo de "Pesquisa concluída" tem acento `--cor-sucesso`, com o
  título e a frase de registro inalterados (FR-027 a FR-029).

### Implementation for User Story 3

- [X] T023 [US3] Em `trajetoria/interface/mensagens.py`, acrescentar
  `VARIANTE_DO_AVISO` ao lado de `AVISOS` (mapa fixo, [data-model](data-model.md)).
- [X] T024 [US3] Em `trajetoria/interface/views.py`, passar ao template a variante junto
  com o aviso, nas telas de formações e de Seção, sem mudar quais códigos cada tela aceita
  nem os textos.
- [X] T025 [US3] Em `trajetoria/interface/templates/interface/formacoes.html` e
  `secao.html`, classe `aviso aviso-{{ variante }}` no aviso; em `concluida.html`, wrapper
  do topo (`h1` + frase de registro) com classe própria, textos inalterados. T021 passa.
- [X] T026 [US3] Em `estilo.css`, trocar por tokens as cores das regras **exclusivas** da
  jornada (`.resumo-pendencias`, `.com-pendencia …`, incluindo a regra do IV-03); em
  `jornada.css`: variantes `.aviso-sucesso`/`.aviso-informacao` (acento 4 px), forma do
  resumo na jornada (acento lateral 4 px + contorno 1 px na cor do estado; erro com
  `--cor-erro`), `.resumo-erros:focus`, topo da confirmação com acento `--cor-sucesso`.
  Não alterar `.resumo-erros`, `.erro`, `.com-erro` globais (editor). T022 passa; testes
  do IV-03 continuam verdes.

**Checkpoint**: estados com semântica visual; pendência ≠ erro sem depender de cor.

---

## Phase 6: User Story 4 — Ver a trajetória com hierarquia clara (Priority: P2)

**Goal**: item de formação, frase de entrada, contexto e ficha, ação principal em largura
total, divisores suaves.

**Independent Test**: trajetória de Ana, Maria e Diego a 375 e 1280 px; conclusão e
confirmação (ficha).

### Tests for User Story 4 ⚠️

- [X] T027 [US4] Escrever (deve falhar) em `test_interface_identidade.py`: a frase de entrada
  de Ana, sem tags, é idêntica à atual ("Você concluiu {linha}. O Ifes quer saber…") e a
  linha está dentro de `<strong>`; sem linha informada, a frase neutra atual, sem
  `<strong>` vazio; em "Suas outras formações", a situação vem em `span.situacao` (não
  `<strong>`), com o mesmo texto; pelo leitor de cascata: `.formacao strong` peso 600,
  `.situacao` peso 400, complemento 15 px suave, `.lista-simples > li` com divisor
  `--cor-borda-suave` na jornada; `.contexto` com fio 4 px `--cor-marca` e fundo
  `--cor-institucional`; existe regra sob `@media (max-width: 30em)` que empilha
  `.contexto dl` e põe `button.primario` dos formulários da trajetória e da conclusão em
  largura total (FR-031 a FR-035).

### Implementation for User Story 4

- [X] T028 [US4] Em `trajetoria/interface/views.py`, separar `mensagens.ENTRADA_FATO` em
  prefixo, linha e sufixo para o template (sem mudar a constante nem o texto final);
  manter o caminho atual quando não há linha.
- [X] T029 [US4] Em `trajetoria/interface/templates/interface/formacoes.html` e
  `formacao.html`: `<strong>` na linha da frase de entrada; `span.situacao` no lugar de
  `<strong>` da situação; nada mais.
- [X] T030 [US4] Em `jornada.css`: item de formação (pesos, complemento, situação, espaço
  simétrico 16/16, divisor suave); `.contexto` e ficha (fio marca, fundo institucional,
  `dl` empilhada até `30em`); ação principal em largura total até `30em`; `.saidas` com
  divisor suave. T027 passa; testes da 014 de trajetória continuam verdes.

**Checkpoint**: trajetória com hierarquia; conteúdo e ordem da 014 intactos.

---

## Phase 7: User Story 5 — Comparar as Direções A e B (Priority: P2)

**Goal**: comprovar que a troca A × B altera exclusivamente os dois tokens de ação
(`--cor-acao` e `--cor-acao-forte`) e documentá-la sem mecanismo de execução.

**Independent Test**: trocar só `--cor-acao`/`--cor-acao-forte`; G1–G4 mudam por inteiro;
nada mais muda.

- [X] T031 [US5] Confirmar que T005/T006 continuam verdes com todas as fases anteriores
  (nenhum hex de ação fora dos tokens; nenhum mecanismo de alternância).
- [X] T032 [US5] Gerar a Direção A **só localmente** (quickstart §4): editar as duas linhas
  em `estilo.css` para `#195128`/`#00420c`; capturar G1–G4 a 375 e 1280 px
  (`R{n}-G{k}-A-{largura}-100`); medir contrastes; **restaurar B** e conferir com
  `git diff` que as duas linhas voltaram (nenhum commit com A).

**Checkpoint**: A e B documentáveis pela troca exclusiva dos dois tokens de ação
(`--cor-acao` e `--cor-acao-forte`).

---

## Phase 8: User Story 6 — Editor e acompanhamento sem mudança (Priority: P2)

**Goal**: editor e acompanhamento sem mudança visual não intencional; a prévia de Seção do editor é a única exceção deliberada, limitada a tipografia, estados e tratamento visual interno da Pergunta e dos controles compartilhados (FR-040); shell, ritmo de página, espaçamento entre Perguntas e composição do editor inalterados.

**Independent Test**: capturas antes (T002) × depois; suítes da 009 e da 011.

- [X] T033 [US6] Rodar `uv run pytest tests/editor tests/acompanhamento` e
  `tests/interface/test_demonstracao_operador.py`; nenhuma asserção administrativa ajustada
  (exceto as de T017, que são novas).
- [X] T034 [US6] Capturar o "depois" das mesmas telas de T002 (`R{n}-ADM-{tela}-{largura}`)
  e comparar: 0 mudanças visuais não intencionais nas telas do editor e do
  acompanhamento; a prévia de Seção é a única exceção deliberada, limitada a tipografia,
  estados e tratamento visual interno da Pergunta e dos controles compartilhados
  (FR-040); shell, ritmo de página, espaçamento entre Perguntas e composição do editor
  inalterados.

**Checkpoint**: nenhuma mudança visual não intencional fora da jornada; a prévia muda só
no que FR-040 permite.

---

## Phase 9: Gate de validação (aceite da 015)

**Purpose**: registro textual do gate ([contracts/registro-validacao.md](contracts/registro-validacao.md)).
A 015 só fica pronta para merge com uma rodada aprovada (FR-042).

- [X] T035 Criar `specs/015-identidade-visual-jornada/validacao.md` (só texto) com a
  estrutura do contrato.
- [X] T036 Rodada 1 (quickstart §3): G1–G4 a 375, 390, 430 e 1280 px, fonte a 100% e
  200%; medir SC-001 a SC-011 e SC-013; capturas identificadas e guardadas fora do
  repositório; SC-001 registrado como **pendente (⛔ D-03)** enquanto T015 não estiver
  feita.
- [X] T037 Comparação de raio 0 × 4 px (quickstart §5): G2 e G3 a 375 px; decidir, deixar
  só o valor escolhido em `--raio` e registrar o motivo (FR-044).
- [X] T038 Comparação do divisor entre Perguntas (quickstart §5): G2 a 375 px com e sem;
  manter só se necessário, registrando o motivo (FR-024).
- [X] T039 Registrar a comparação A × B (T032) e a regressão administrativa (T034) no
  `validacao.md`.
- [X] T040 Para cada critério reprovado: corrigir na mesma branch (na tarefa/arquivo de
  origem), rodar a suíte e abrir nova rodada no `validacao.md`. Repetir até todos os
  critérios objetivos passarem, exceto SC-001 se T015 ainda estiver bloqueada.
- [ ] T041 ⛔ BLOCKED D-03 Depois de T015: rodada final com SC-001 e SC-002 (cabeçalho com a
  assinatura, ≤ 64/80 px) e repetição dos demais critérios em G1–G4; **gate aprovado só
  aqui**.
- [X] T042 Registrar a revisão perceptiva como **pendente** (ou realizada, com quem e
  observações) e os itens para a propagação futura (403/404/500; shell administrativo)
  (FR-043, FR-045).

**Checkpoint**: gate aprovado (critérios objetivos) → 015 pronta para merge.

---

## Phase 10: Polish & Cross-Cutting Concerns

- [X] T043 `uv run ruff check .` e `uv run ruff format --check .`; `uv run pytest`
  completo; `makemigrations --check --dry-run`; `grep -rn "<script"` nos templates da
  jornada e da demonstração; busca por `http`, `@import`, `url(` nas folhas.
- [X] T044 [P] Medir e registrar no `validacao.md` o peso inline de `jornada.css` (alvo
  ≤ 6 KB) e, após T015, do SVG (alvo ≤ 30 KB).
- [X] T045 [P] Conferir com `git diff --stat main...` que nenhum arquivo de
  `trajetoria/editor/`, `trajetoria/acompanhamento/`, `403_csrf.html`, `404.html` e
  `500.html` foi alterado. Em `trajetoria/demonstracao/`, só é permitido o mínimo
  necessário para mover os controles de demonstração para a faixa e permitir o shell
  compartilhado (D7): nenhuma alteração funcional, nenhuma mudança visual não prevista,
  textos, destinos, permissões e comportamento idênticos.
- [X] T046 Atualizar `plan.md` ("Necessidade de voltar à spec") e `research.md` com o que
  o gate decidiu (raio, divisor, eventuais calibrações de `--cor-institucional`,
  `--cor-selecao`, `--cor-borda-suave`).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências; T002 e T003 em paralelo com T001.
- **Foundational (Phase 2)**: depende de T001; bloqueia todas as histórias.
- **US1 (Phase 3)**: depois da Phase 2. T015 é **independente do resto** e só começa com
  o SVG oficial (⛔ D-03).
- **US2 (Phase 4)**: depois da Phase 2; pode seguir depois de US1 (edita `estilo.css`,
  que a Phase 2 também editou; sem conflito com `jornada.css`).
- **US3 (Phase 5)**: depois de US1 (`jornada.css`, `base.html`) e de US2 (`estilo.css`).
- **US4 (Phase 6)**: depois de US3 (`views.py`, `formacoes.html`, `jornada.css`).
- **US5 (Phase 7)**: depois de US1–US4 (todas as ações em tokens).
- **US6 (Phase 8)**: depois de US1–US4; T034 repete-se após correções do gate.
- **Gate (Phase 9)**: depois de US1–US6; T041 depende de T015.
- **Polish (Phase 10)**: depois do gate (T044/T046 parcialmente antes de T041).

### User Story Dependencies

```text
T001 ─► Phase 2 (T004→T005/T006→T007→T008→T009)
          └─► US1 (T010/T011→T012→T013→T014) ─► US2 (T016/T017→T018→T019→T020)
                 │                                 └─► US3 (T021/T022→T023→T024→T025→T026)
                 │                                         └─► US4 (T027→T028→T029→T030)
                 │                                                 └─► US5, US6 ─► Gate ─► Polish
                 └─► T015 ⛔ D-03 ─────────────────────────────────────────► T041
```

### Within Each User Story

- Testes primeiro (devem falhar), depois implementação.
- `mensagens.py` → `views.py` → templates → folhas.
- Toda tarefa que edita `estilo.css` termina com a suíte de `tests/editor` verde.

### Arquivos com execução serial

`interface/estilo.css` (T007, T018, T019, T026, T037), `interface/jornada.css` (T009,
T013, T015d, T026, T030), `interface/base.html` (T009, T012, T015c),
`interface/views.py` (T024, T028), `interface/formacoes.html` (T025, T029),
`tests/interface/test_interface_identidade.py` (T005, T006, T008, T010, T011, T015b,
T016, T021, T022, T027).

### Parallel Opportunities

- T002 e T003 entre si e com T001.
- T017 (`tests/editor/test_editor_previa.py`) em paralelo com T016.
- T044 e T045 entre si.
- T015 pode ser feita a qualquer momento depois de T012, assim que o SVG chegar.

---

## Parallel Example: User Story 2

```text
T016 tests/interface/test_interface_identidade.py
T017 tests/editor/test_editor_previa.py
# Depois, em sequência: T018 → T019 → T020
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phases 1 e 2 (sem mudança visual).
2. Phase 3 (US1) sem T015: shell com nome do produto, faixa e rodapé.
3. **Parar e validar**: `uv run pytest`; captura rápida de G1 a 375 px.

### Incremental Delivery

US1 → US2 → US3 → US4 → US5/US6 → gate → polish. Cada história termina com a suíte verde
e com o editor/acompanhamento intactos.

### Gate e merge

- Rodadas do gate na mesma branch até os critérios objetivos passarem (FR-042).
- **Sem o SVG oficial (D-03), o gate não fecha** (SC-001): a branch pode ficar pronta em
  tudo o mais, mas a 015 **não** é mergeada até T015 e T041.
- Capturas anexadas ao PR pelos identificadores do registro; nada binário versionado.

### Fechamento

Padrão do repositório: commit `docs(015): spec, plan e tasks — …` e commit
`feat(015): …`; PR "Feature 015 — …" com as seções habituais (Resumo,
Persistência/Modelo, Features anteriores, Decisões pendentes, Validação) e as capturas do
gate anexadas.
