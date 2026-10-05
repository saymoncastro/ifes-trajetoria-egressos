---
description: "Tasks da Feature 021 — Minha Trajetória: narrativa visual personalizada"
---

# Tasks: Minha Trajetória — narrativa visual personalizada

**Input**: `specs/021-minha-trajetoria-narrativa/`, com:

- spec (83 FRs, 15 SCs; revisada em 2026-10-05; esta lista registrava 73 FRs e 14 SCs antes da revisão editorial);
- plan;
- research R1–R21;
- data-model;
- contracts (`narrativa`, `catalogo`, `rotas`, `card`, `contexto-da-trajetoria`);
- quickstart.

Constituição 2.0.0.

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/.

**Tests**: Princípio XXVI. São obrigatórios para:

- determinismo e "nada inventado";
- não interferência na pesquisa;
- fronteiras 001/012/013/018/019;
- isolamento da capacidade de contexto;
- privacidade do card;
- área segura do formato vertical;
- seleção de apuração e base parcial.

Os testes de cada fase são escritos antes e falham antes da implementação. Cobertura não é
meta.

## Formato e convenções

- `- [ ] Tnnn [P?] [USn?] descrição com caminho`.
- **[P]:** arquivo diferente e sem dependência de task incompleta.
- **Ordem das fases** (revisada em 2026-10-04, a pedido do solicitante):
  1. Primeiro, comprovar PNG e pior caso do layout (Fase 3, porta de decisão).
  2. Depois, a narrativa pura (US2), a página (US1), as fronteiras (US4) e o card na página.
  3. P1 é entregue e validada sem P2.
  4. A fundação P2 precede US5 e US6.
- **Fixtures reutilizadas:**
  - `tests/conftest.py`: `fonte_simulada`, chaves de acesso e de declaração.
  - `tests/interface/conftest.py`: `modo_demonstracao`, `relogio`, `cenario`.
  - `tests/interface/construcao_interface.py`: `entrar_como`, `iniciar`,
    `percorrer_pela_interface`, `texto_visivel`, `tokens`.
- **Restrições de modelo e de contrato:** citadas literalmente do data-model.md.
- **Proibido em todas as tasks:**
  - alterar `trajetoria/fonte_academica/contrato.py`, `trajetoria/fonte_academica/simulada.py`,
    `trajetoria/academico/`, `trajetoria/acesso/` ou `trajetoria/declaracao/`;
  - gravar a narrativa ou o card;
  - ler `Resposta`.

---

## Fase 1 — Setup (2 tasks)

- [X] T001 Criar o app `trajetoria/narrativa/`:
  - `__init__.py`;
  - `apps.py` com `NarrativaConfig(name="trajetoria.narrativa")`;
  - `urls.py` com `urlpatterns = []`;
  - pasta `templates/narrativa/`.

  Também:
  - acrescentar `"trajetoria.narrativa"` em `INSTALLED_APPS` de `config/settings.py`,
    logo depois de `"trajetoria.interface"`;
  - em `config/urls.py`, acrescentar `path("", include("trajetoria.narrativa.urls"))` antes
    do `include` de `trajetoria.interface.urls` e atualizar a docstring com a Feature 021
    (`/minha-trajetoria/`).

- [X] T002 [P] Criar `tests/narrativa/__init__.py`, `tests/narrativa/conftest.py` e
  `tests/narrativa/construcao.py`.
  - **`conftest.py`:** fixtures `modo_demonstracao` (autouse, como em
    `tests/interface/conftest.py`) e `referencia` (`date(2026, 10, 4)`).
  - **`construcao.py`:**
    - `fato(**atributos)`, que constrói `FatoDaFormacao`;
    - `entrada(formacoes, nome=None, agregados=(), referencia=…, demonstracao=True)`;
    - `entradas_dos_cenarios()`, que converte `cenarios.PESSOAS`/`REGISTROS`
      reconhecidos em `EntradaDaNarrativa`, sem banco, na ordem (`ano_conclusao`,
      `id_externo`);
    - `concluir(client, id_externo)`, que entra pela 018 e conclui uma Participação
      usando os auxiliares de `tests/interface/construcao_interface.py`.

---

## Fase 2 — Fundação: contrato e catálogo da narrativa (4 tasks)

**Bloqueia todas as histórias de P1.**

### Testes

- [X] T003 [P] Escrever `tests/narrativa/test_contrato.py` (FR-012 a FR-014;
  contracts/narrativa.md):
  - todas as dataclasses são congeladas;
  - `serializar()` emite `versao_contrato: 1`, as chaves na ordem do contrato e nenhuma
    chave com `None` para fato ausente;
  - nenhuma chave `id`, `fonte`, `id_externo`, `incorporado_em`, `cpf` ou
    `data_nascimento` em nenhum nível;
  - `json.dumps(serializar(n), ensure_ascii=False)` é idêntico em duas montagens da mesma
    entrada (use uma narrativa construída à mão).

- [X] T004 [P] Escrever `tests/narrativa/test_catalogo.py`, parte estrutural (FR-022 a
  FR-024, FR-061; contracts/catalogo.md):
  - toda formulação tem só placeholders do conjunto `{curso}`, `{unidade}`, `{ano}`, `{n}`,
    `{nome}`, `{apuracao}`;
  - nenhuma formulação contém "Campus";
  - as formulações de unidade usam "na unidade {unidade}";
  - `VEDADAS` contém todos os termos da seção "Formulações vedadas" do contrato;
  - existem formas singular e plural para `registradas`, `ha_anos`, `card_mais` e
    `agregado_curso`.

### Implementação

- [X] T005 Implementar `trajetoria/narrativa/contrato.py` conforme data-model §3 e
  contracts/narrativa.md:
  - **Entrada:**
    - `FatoDaFormacao`: `curso`, `unidade`, `nivel`, `modalidade`, `forma_oferta`,
      `ano_conclusao`, `data_conclusao`, `ingresso_ano=None`, `ingresso_data=None`;
    - `ContextoSelecionado`: `metrica`, `curso`, `unidade`, `ano`, `valor`, `apurado_em`;
    - `EntradaDaNarrativa`: `nome`, `formacoes`, `agregados`, `referencia`,
      `demonstracao`.
  - **Saída:** `Formacao`, `Relacao`, `Derivado`, `ContextoAgregado`, `Frase(texto,
    origem)`, `Secao(chave, titulo, frases)`, `Compartilhavel` (`formacoes` com `linhas`,
    `formacoes_omitidas`, `formacoes_registradas`, `contextos_agregados`,
    `nome_disponivel`) e `TrajetoriaNarrativa`.
  - **`serializar(narrativa) -> dict`:** ordem e omissão de ausentes do contrato. Python
    puro, sem import de Django.

- [X] T006 Implementar `trajetoria/narrativa/catalogo.py`:
  - todas as formulações de contracts/catalogo.md (P1 e P2), como constantes de texto com
    placeholders nomeados, em linguagem simples, com a docstring citando DP-801;
  - títulos das seções (`o_que_o_ifes_registra`, `trajetoria_academica`,
    `outras_formacoes`, `naquele_ano`, `card`);
  - `TITULO = "Minha trajetória no Ifes"`;
  - `VEDADAS: tuple[str, ...]`.

---

## Fase 3 — US3: validação antecipada do PNG e do pior caso do card (P1, porta de decisão) (6 tasks)

**Goal:** antes de construir página e narrativa, provar que o objetivo principal é
alcançável:

- o PNG 1080 × 1920 é gerado no CI e no macOS de forma reprodutível;
- o pior caso do layout cabe na área segura com boa leitura.

O SVG sozinho não comprova a entrega para stories (FR-031, FR-032, FR-040, FR-072;
SC-013; research R10, R11).

**Independent Test:** `pytest tests/narrativa/test_png.py tests/narrativa/test_card.py` no
macOS e no CI, mais a inspeção visual do PNG do pior caso.

**Porta:** se T007 (PNG) ou T012 (pior caso visual) falhar, parar e decidir com o
solicitante antes das fases seguintes.

- [X] T007 [US3] **Spike de rasterização (porta de decisão; primeira task depois da
  fundação):**
  1. Acrescentar `"resvg-py>=0.5,<0.6"` em `pyproject.toml`. Rodar `uv lock`. Em
     `tests/dependencias.py`, acrescentar a linha
     `"resvg-py>=0.5,<0.6",  # Feature 021: PNG do card a partir do SVG (research R11)`.
  2. Criar `trajetoria/narrativa/fontes/` com `OpenSans-Regular.ttf`, `OpenSans-Bold.ttf`
     e `OFL.txt`, obtidos do repositório oficial `googlefonts/opensans`. Registrar a URL e
     a versão na ADR. **Só esses dois pesos.**
  3. Escrever `tests/narrativa/test_png.py`:
     - os bytes começam pela assinatura PNG;
     - o IHDR indica 1080 × 1920;
     - duas rasterizações do mesmo SVG dão bytes idênticos;
     - um SVG com "Formação · Educação" renderizado com `font_files` difere de um SVG sem
       texto, o que prova que o texto foi desenhado;
     - o tempo de rasterização é medido e registrado.
  4. Rodar localmente (macOS arm64) e no CI (ubuntu, Python 3.13), pelo PR.
  5. Escrever `docs/adr/0006-rasterizacao-do-card.md` com o resultado.
  6. **Porta de decisão: se falhar, parar.** Registrar a razão na ADR e levar a questão ao
     solicitante antes de qualquer outra task do card. O fallback SVG mantém a página,
     mas não cumpre o objetivo do story: as redes não aceitam SVG.

- [X] T008 [P] [US3] Escrever `tests/narrativa/test_card.py` (contracts/card.md; SC-005,
  SC-010, SC-013). A montagem ainda não existe: construa `Compartilhavel` à mão com
  `card.quebrar_linhas`.
  - **Determinismo e formato:**
    - mesmo `compartilhavel`, tema e nome → bytes idênticos;
    - `width="1080" height="1920"` e `viewBox="0 0 1080 1920"`.
  - **Área segura e legibilidade** (parse com `xml.etree.ElementTree`):
    - todo `<text>`/`<tspan>` tem `y` entre 270 e 1570 (subtraindo o `font-size` para o
      topo) e `x` entre 90 e 990;
    - `font-size` mínimo de 40, e de 64 no título;
    - **pior caso**: nome de 60 caracteres, 4 formações com o curso mais longo de
      `cenarios.py` e outro com mais de 70 caracteres, "e mais 3" e **um par de agregados
      fictícios** com o curso longo.
  - **Nome:** presente só quando `nome` é passado.
  - **Conteúdo:**
    - "Demonstração — dados fictícios" com `demonstracao=True`;
    - nenhuma ocorrência de forma de oferta, data `dd/mm/aaaa`, "Há ", ingresso,
      "certificado", "comprovante", "declaração", QR ou `<image>`;
    - `<title>` e `<desc>` presentes;
    - `font-family` começa por "Open Sans".
  - **Contraste:** os pares de tokens texto/fundo do `TEMA_PADRAO` têm razão de contraste
    ≥ 4,5 (calcular pela fórmula WCAG).

- [X] T009 [US3] Completar `trajetoria/narrativa/card.py`:
  - **`TEMA_PADRAO`:** dicionário de tokens com os valores de
    `interface/templates/interface/estilo.css` (cor de marca só em grafismo, nunca em
    texto).
  - **Constantes:** `AREA_SEGURA = (90, 270, 990, 1570)`, `LIMITES` (caracteres por linha
    por tamanho) e posições.
  - **`quebrar_linhas(texto, tamanho) -> tuple[str, ...]`:**
    - quebra por palavras dentro de `LIMITES[tamanho]`, sem cortar palavra nem truncar;
    - uma palavra maior que o limite ocupa a linha inteira;
    - usada pelo card e, na Fase 4, pela montagem.
  - **`card_svg(compartilhavel, tema=TEMA_PADRAO, nome=None, demonstracao=True) ->
    str`:** usa `render_to_string("narrativa/card.svg", …)`.

- [X] T010 [US3] Criar `trajetoria/narrativa/templates/narrativa/card.svg`:
  - **Raiz e acessibilidade:** `<svg xmlns=… width="1080" height="1920" viewBox="0 0 1080
    1920" role="img">`, com `<title>` e `<desc>` (resumo textual das formações).
  - **Fundo e faixas:** fundo do tema; faixas de topo (0–270) e base (1570–1920) só com
    grafismo.
  - **Conteúdo, dentro da área segura:**
    - título;
    - nome, opcional;
    - até 4 formações, com o curso em negrito e "unidade · nível · modalidade · ano";
    - "e mais N formações registradas";
    - "N formações registradas no Ifes";
    - bloco de agregados (no máximo um par), desenhado quando
      `compartilhavel.contextos_agregados` não estiver vazio. Em P1 a narrativa não o
      preenche, mas o pior caso é testado com um par fictício desde já;
    - rodapé e marca de demonstração.
  - **Sem brasão nem assinatura** (DP-2102). Sem atributos variáveis (nenhum id gerado).

- [X] T011 [US3] Implementar `trajetoria/narrativa/rasterizacao.py`:
  - `png_de(svg: str) -> bytes | None`:
    - importação de `resvg_py` protegida (`ImportError` → `None`);
    - `svg_to_bytes(svg_string=svg, font_files=[caminhos absolutos das duas fontes],
      skip_system_fonts=True)`;
    - erro de rasterização → log sem dado pessoal e `None`.
  - `rasterizacao_disponivel() -> bool`.
  - Único módulo do projeto que importa `resvg_py` (acrescentar a verificação em
    `test_fronteiras.py`).

- [X] T012 [US3] **Validação visual do pior caso (porta de decisão):**
  - Gerar com `card_svg` + `png_de` o PNG do pior caso do T008 e salvá-lo em
    `specs/021-minha-trajetoria-narrativa/evidencias/card-pior-caso.png`. O pior caso tem
    nome longo, 4 cursos longos, "e mais 3", um par de agregados e a marca de
    demonstração.
  - Abrir o PNG num celular, ou exibi-lo com 375 px de largura, e conferir:
    - legibilidade de todos os textos;
    - nada nas faixas de topo e base;
    - hierarquia clara entre título, cursos e rodapé.
  - Registrar o resultado em `specs/021-minha-trajetoria-narrativa/validacao.md`.
  - **Se não couber com boa leitura: parar** e levar a questão ao solicitante, sem reduzir
    o limite de 4 formações e sem cortar o nome.

**Checkpoint:** PNG e layout comprovados.

---

## Fase 4 — US2: narrativa honesta, o que não há não aparece (P1) (3 tasks)

**Goal:** `montar(entrada)` puro e determinístico, que só emite frases do catálogo
derivadas dos dados (FR-011, FR-015 a FR-025).

**Independent Test:** `pytest tests/narrativa/test_montagem.py
tests/narrativa/test_catalogo.py`, sem banco.

### Testes

- [X] T013 [P] [US2] Escrever `tests/narrativa/test_montagem.py` (FR-016 a FR-021,
  FR-025; research R5, R6; US2):
  - **Ordem e continuidade:**
    - Diego (2012, 2017, 2020): três formações em ordem e duas frases `depois`;
    - Maria: uma frase `depois` na Especialização;
    - Ana: nenhuma;
    - dois com o mesmo ano: nenhuma relação nem "primeira";
    - ano ausente: sem relação;
    - grupo anterior com duas formações: sem frase.
  - **Tempo:**
    - só ano → `desde` ("Concluída em AAAA"), nunca "Há";
    - com data → anos completos (Bruno 2020-07-10, referência 2026-10-04 → 6);
    - N = 0 → nada;
    - referência anterior à conclusão → nada.
  - **Ausências:**
    - sem unidade → frase `concluiu_sem_unidade` e nenhum "unidade";
    - nada de "—" nem "não informado".
  - **Nome:** `None` → nenhuma frase com nome; presente → só `nome_registros`.
  - **Pessoa do acervo** (uma formação de unidade e ano, sem curso nem nome): narrativa
    mínima válida, sem frase inventada.
  - **Derivados:** `formacoes_registradas`; `primeira_formacao` só com menor ano único.
  - **P1:** nenhum ingresso quando `ingresso_ano` é `None`.
  - **`compartilhavel`:**
    - não contém nome, forma de oferta, data, tempo nem ingresso;
    - com 5 formações, contém 4 e `formacoes_omitidas == 1`;
    - `linhas` vêm de `card.quebrar_linhas`, nunca cortam palavra e nunca truncam o
      texto.
  - **Determinismo:** mesma entrada → `serializar` igual. `montar` não chama
    `timezone.now` nem consulta o banco (rode sem `db`).

- [X] T014 [P] [US2] Completar `tests/narrativa/test_catalogo.py` com a varredura (SC-001):
  - para cada entrada de `entradas_dos_cenarios()`, toda `Frase.texto` corresponde a uma
    formulação do catálogo preenchida só com valores da entrada (casar por regex gerada
    das formulações);
  - nenhum texto de `secoes` nem de `compartilhavel` contém termo de `VEDADAS` (sem
    diferenciar maiúsculas).

### Implementação

- [X] T015 [US2] Implementar `trajetoria/narrativa/montagem.py: montar(entrada) ->
  TrajetoriaNarrativa`:
  - **Seções:** na ordem do FR-026, só as que têm frase (FR-027).
  - **Relação e continuidade:** research R5.
  - **Tempo:** research R6.
  - **Variantes:** pela ausência de atributos.
  - **Derivados:** `formacoes_registradas`, `tempo_desde_conclusao` (só com data) e
    `primeira_formacao` (menor ano único).
  - **`compartilhavel`:**
    - até 4 formações;
    - `formacoes_omitidas`;
    - quebra de linha por `card.quebrar_linhas` (Fase 3);
    - `nome_disponivel = entrada.nome is not None`.
  - Sem banco, relógio nem log.

**Checkpoint:** a narrativa pura está completa e verificada.

---

## Fase 5 — US1: ver a própria trajetória depois de responder (P1, MVP) (7 tasks)

**Goal:** página "Minha trajetória no Ifes" para a Pessoa elegível; confirmação e
`/formacoes/` levam até ela (FR-001 a FR-010, FR-026 a FR-030, FR-070).

**Independent Test:** demonstração preparada. Concluir como a Maria e abrir a página
(quickstart P1, itens 1 a 3).

### Testes

- [X] T016 [P] [US1] Escrever `tests/narrativa/test_rotas.py` (FR-001, FR-002, FR-010,
  FR-016, FR-069; SC-002, SC-012):
  - **Maria depois de concluir a Participação de TADS:** 200, com as duas formações e
    "O Ifes registra 2 formações concluídas por você.".
  - **Maria sem Participação concluída:** 302 para `/formacoes/`, sem texto sobre
    narrativa.
  - **Sem sessão:** 302 para `/acesso/`.
  - **Sessão de declarante (019):** 302 para `/acesso/`.
  - **Sessão expirada** (avançar o `relogio`): comportamento da 018.
  - `Cache-Control` contém `no-store`.
  - Com `TRAJETORIA_DEMONSTRACAO` desligado: 404.
  - **Maria com as duas Participações concluídas:** o corpo da página é idêntico ao de uma
    Participação concluída (uma narrativa).
  - Diego: três formações em ordem. Ana: sem seção "Outras formações".

- [X] T017 [P] [US1] Escrever `tests/narrativa/test_pagina.py` (FR-026 a FR-030, FR-066):
  - um único `h1` "Minha trajetória no Ifes";
  - `section` com `h2` só para seções presentes;
  - formações em `ol`;
  - nome no máximo uma vez;
  - ligação final "Voltar às suas formações" para `/formacoes/`;
  - nenhum placeholder ("em breve", "—");
  - nenhum recurso externo (`http`) no HTML;
  - hierarquia de títulos sem saltos;
  - `narrativa.css` não define largura fixa maior que 320 px nem `white-space: nowrap` em
    texto corrido (proxy automatizado do SC-003; a verificação visual em 320 px fica no
    T053).

- [X] T018 [P] [US1] Ajustar `tests/interface/test_interface_conclusao.py` (FR-003, FR-004;
  revisa 014 FR-041):
  - nas linhas 143 e 256, a única ligação do conteúdo principal da confirmação
    institucional é "Ver minha trajetória no Ifes" com `href="/minha-trajetoria/"`;
  - nenhuma imagem, download ou trecho da narrativa na confirmação;
  - a confirmação declarada continua com "Ver suas formações informadas" para
    `/declaracao/` (FR-007).

- [X] T019 [P] [US1] Ajustar `tests/interface/test_interface_formacoes.py` (FR-005, FR-006,
  FR-070; research R15, R16):
  - nas linhas 319 a 324, `h1` "Suas formações no Ifes";
  - ligação "Ver minha trajetória no Ifes" só quando a Pessoa tem Participação concluída
    institucional;
  - frase "Ao final, você poderá ver sua trajetória no Ifes." só quando há pesquisa
    disponível para iniciar ou retomar;
  - em `aviso.html`, ligação "Ver suas formações no Ifes".

### Implementação

- [X] T020 [US1] Implementar `trajetoria/narrativa/consultas.py`:
  - `elegivel(pessoa) -> bool`, conforme research R2;
  - `entrada_da_pessoa(pessoa, referencia, demonstracao) -> EntradaDaNarrativa`:
    - Conclusões de `pessoa.conclusoes` na ordem do model;
    - atributos como valores, sem `id`/`fonte`/`id_externo`;
    - `agregados=()` e ingresso vazio até a Fase 9/10.

- [X] T021 [US1] Implementar `trajetoria/narrativa/views.py: minha_trajetoria` e a rota
  `minha-trajetoria/` em `trajetoria/narrativa/urls.py`:
  - **View:** `require_GET` e `never_cache`. Usa `pessoa_em_uso`; sem Pessoa, vai para
    `/acesso/`; inelegível, para `/formacoes/`. Monta com `timezone.localdate()` e
    `demonstracao=settings.TRAJETORIA_DEMONSTRACAO`.
  - **Template** `templates/narrativa/minha_trajetoria.html`: estende
    `interface/base.html` e renderiza `secoes`. Inclui `templates/narrativa/narrativa.css`
    no bloco de estilo, só com tokens da 015 (`var(--…)`), marcador de linha do tempo em
    CSS e legibilidade a partir de 320 px.
  - **Sem seção do card nesta task**, que fica para a Fase 7.

- [X] T022 [US1] Ajustes em `trajetoria/interface/`:
  - `mensagens.py`:
    - `TITULO_TRAJETORIA = "Suas formações no Ifes"`, com comentário "014 FR-030 revisado
      pela 021 (FR-006)";
    - `ANTECIPACAO = "Ao final, você poderá ver sua trajetória no Ifes."`;
    - `LIGACAO_NARRATIVA = "Ver minha trajetória no Ifes"`;
    - `LIGACAO_FORMACOES = "Ver suas formações no Ifes"`.
  - `templates/interface/concluida.html`: a ligação não declarada passa a
    `/minha-trajetoria/` com `LIGACAO_NARRATIVA`.
  - `templates/interface/aviso.html`: `LIGACAO_FORMACOES`.
  - `views.py: formacoes`: acrescenta ao contexto `narrativa_disponivel`
    (`narrativa.consultas.elegivel`) e `antecipacao` (só com pendentes).
  - `templates/interface/formacoes.html`: renderiza ambos.
  - Atualizar a docstring de `views.concluida` (FR-062/063 + 021 FR-003).

**Checkpoint:** MVP navegável sem a seção do card.

---

## Fase 6 — US4: a devolutiva não interfere na pesquisa (P1) (3 tasks)

**Goal:** provar a não interferência e as fronteiras (FR-007, FR-008, FR-042 a FR-045,
FR-071; SC-006, SC-007).

**Independent Test:** `pytest tests/narrativa/test_sem_efeito.py
tests/narrativa/test_fronteiras.py tests/narrativa/test_declarada.py`.

- [X] T023 [P] [US4] Escrever `tests/narrativa/test_sem_efeito.py`:
  - para todos os models de `django.apps.apps.get_models()`, contagem de linhas idêntica
    antes e depois de `GET /minha-trajetoria/`, `GET /minha-trajetoria/card.svg` e
    `GET /minha-trajetoria/card.png` (quando disponível);
  - os testes das rotas de card ficam `xfail(strict=False)` até a Fase 7.

- [X] T024 [P] [US4] Escrever `tests/narrativa/test_fronteiras.py`:
  - **Contratos fixos:**
    - `CAMPOS_DE_CONTEXTO == ("curso", "unidade", "nivel", "modalidade", "forma_oferta",
      "ano_conclusao", "data_conclusao")`;
    - nomes de `fields(PessoaEncontrada) == ("id_externo", "nome", "conclusoes", "cpf",
      "data_nascimento")`;
    - campos de `analitico.RegistroDoSnapshot` iguais aos atuais (lista literal);
    - `exportacao.contrato.VERSAO_CONTRATO == 2` e nomes de `COLUNAS_BASE` iguais aos
      atuais.
  - **Varredura AST de imports:**
    - `trajetoria/narrativa/**` não importa `trajetoria.analitico`,
      `trajetoria.acompanhamento` nem `trajetoria.exportacao`, e não referencia o nome
      `Resposta`;
    - `trajetoria/acesso/**`, `trajetoria/declaracao/**` e `trajetoria/academico/**` não
      importam `trajetoria.narrativa`, `trajetoria.contexto_trajetoria` nem
      `trajetoria.fonte_academica.contexto_da_trajetoria`/`contexto_simulado` (FR-071).
  - **Logs:** com `caplog`, abrir a página e baixar o card não registra o nome, o CPF nem
    o curso da Pessoa.

- [X] T025 [P] [US4] Escrever `tests/narrativa/test_declarada.py` (FR-007; US4, cenário 2):
  - concluir pelo caminho da 019 (`tests/declaracao/construcao.py`);
  - confirmação idêntica à de antes (nenhuma ligação para `/minha-trajetoria/`);
  - `GET /minha-trajetoria/` com a sessão do declarante → `/acesso/`.

---

## Fase 7 — US3: entrega do card na página — rotas, prévia, salvar, baixar e compartilhar (P1) (6 tasks)

**Goal:** a PNG validada na Fase 3 vira a prévia e o arquivo levado ao story. O egresso
salva com um toque longo, baixa, ou compartilha pelo menu do celular, cujos destinos
dependem do dispositivo (FR-031, FR-034, FR-039, FR-073; research R8, R9).

**Independent Test:** `pytest tests/narrativa/test_pagina_card.py
tests/narrativa/test_acessibilidade.py` e o quickstart P1, item 5, num celular.

- [X] T026 [US3] Em `trajetoria/narrativa/views.py`, a rota `minha-trajetoria/card.svg`:
  - mesma checagem de acesso da página;
  - `nome=1` só com `Pessoa.nome`;
  - `image/svg+xml; charset=utf-8`;
  - `Content-Disposition: attachment; filename="minha-trajetoria-ifes.svg"`;
  - `never_cache`.

  Registrar a rota em `urls.py`. Remover o `xfail` correspondente em `test_sem_efeito.py`.

- [X] T027 [US3] Em `trajetoria/narrativa/views.py`, a rota `minha-trajetoria/card.png`:
  - mesma checagem;
  - `nome=1`;
  - `image/png`;
  - `Content-Disposition: inline; filename="minha-trajetoria-ifes.png"`;
  - `never_cache`;
  - 404 quando `png_de` devolver `None`.

  Registrar a rota em `urls.py`. Remover o `xfail` restante em `test_sem_efeito.py`.

- [X] T028 [P] [US3] Escrever `tests/narrativa/test_pagina_card.py` (FR-031, FR-034,
  FR-073; SC-004):
  - **Seção e prévia:**
    - seção `id="card"`;
    - a prévia é `<img src="/minha-trajetoria/card.png">` com `alt` que descreve o
      conteúdo e `width`/`height` na proporção 9:16.
  - **Nome:**
    - formulário GET com a caixa "Incluir meu nome no card" (só quando houver nome) e o
      botão "Atualizar prévia";
    - `GET /minha-trajetoria/?nome=1` faz a prévia e o link de baixar apontarem para
      `card.png?nome=1`.
  - **Baixar:** link "Baixar imagem" com `download="minha-trajetoria-ifes.png"`.
  - **Compartilhar:**
    - `<button … hidden>` "Compartilhar" presente;
    - um único `<script>` inline, sem `src` e sem URL `http`;
    - nenhum `<script>` em outras telas (`/formacoes/` e a confirmação).
  - **Fallback:** com `rasterizacao.png_de` monkeypatched para `None`, a prévia é o SVG
    inline e o link baixa `card.svg`; não há botão "Compartilhar".

- [X] T029 [US3] Acrescentar a seção "Seu card" a
  `trajetoria/narrativa/templates/narrativa/minha_trajetoria.html` e ao contexto da view:
  - **Prévia:** `<img>` da PNG (ou SVG inline no fallback), com largura limitada pela
    coluna e `aspect-ratio: 9 / 16` em `narrativa.css`.
  - **Formulário:** GET para `/minha-trajetoria/#card` com a caixa `nome` (valor `1`) e
    "Atualizar prévia".
  - **Baixar:** link com `download`.
  - **Compartilhar:** botão `hidden` e o script inline de cerca de 20 linhas.
    - Se `navigator.canShare` existir e
      `navigator.canShare({files: [new File([], "x.png", {type: "image/png"})]})` for
      verdadeiro, remove `hidden`.
    - No clique, `fetch` da mesma URL da prévia, `new File([blob],
      "minha-trajetoria-ifes.png", {type: "image/png"})` e `navigator.share({files:
      [file]})`.
    - Erros e cancelamento são silenciosos.
  - Nenhum outro JavaScript. O script não fica em `base.html`.

- [X] T030 [P] [US3] Completar `tests/narrativa/test_acessibilidade.py` (FR-066 a FR-068):
  - a caixa do nome tem `label` associado;
  - os botões e o link têm nome acessível que indica o formato ("imagem");
  - a prévia tem `alt` não vazio;
  - todo texto do card (`compartilhavel`) também aparece no texto da página.

- [ ] T031 [US3] Validar manualmente num celular (Safari no iOS e Chrome no Android) e
  registrar em `specs/021-minha-trajetoria-narrativa/validacao.md`:
  - tocar e segurar salva a PNG;
  - "Baixar imagem" salva o arquivo;
  - "Compartilhar" abre o menu de compartilhamento do sistema com a imagem. Registrar quais
    destinos apareceram em cada aparelho; a ausência do Instagram não é falha, porque o
    menu é do dispositivo;
  - a imagem num story de teste não sofre recorte e nenhum texto fica sob a interface do
    aplicativo.

**Checkpoint:** P1 completo (US1 a US4). Parar para validação no celular antes da P2.

---

## Fase 8 — Fundação P2: capacidade de contexto da trajetória e carga (10 tasks)

**Bloqueia US5 e US6.** Nada aqui altera `fonte_academica/contrato.py`, `simulada.py`,
`academico/`, `acesso/` nem `declaracao/` (FR-071).

### Testes

- [X] T032 [P] Escrever `tests/contexto_trajetoria/__init__.py` e
  `tests/contexto_trajetoria/test_contrato.py` (data-model §1):
  - **`ComplementoNaFonte`:** recusa `id_externo_conclusao` vazio e `data_ingresso.year !=
    ano_ingresso`.
  - **`AgregadoNaFonte`:**
    - "`curso` Obrigatório na métrica 1; `None` na métrica 2";
    - "`valor` `>= 0`";
    - `unidade` não vazia;
    - nenhuma cadeia vazia.
  - **`ContextoDaTrajetoriaNaFonte`:** recusa `id_externo_conclusao` repetido e chave
    (métrica, curso, unidade, ano, apurado_em) repetida.
  - **`MetricaAgregada`:** exatamente dois membros.
  - O módulo não importa Django.
  - `trajetoria/fonte_academica/contrato.py` não contém nenhum dos novos nomes.

- [X] T033 [P] Escrever `tests/contexto_trajetoria/test_contexto_simulado.py` (R18;
  FR-063, FR-064):
  - `ContextoSimulado().codigo == "simulada"`;
  - **Ana** (`SIM-C-0001`): complemento com ingresso 2019 e os agregados TADS·Serra·2022 =
    27 e Serra·2022 = 812, apurados em 2026-01-31;
  - **Maria** (`SIM-C-0004`, `SIM-C-0005`): sem complemento; os mesmos dois agregados da
    Serra; nada para Cefor;
  - **Diego:** nada;
  - complementos só para ids pedidos;
  - `ContextoSimulado(indisponivel=True)` lança `ContextoIndisponivel`;
  - determinístico;
  - agregados coerentes com o FR-060 (valor maior ou igual ao número de conclusões
    simuladas no recorte).

- [X] T034 [P] Escrever `tests/contexto_trajetoria/test_modelos.py` (data-model §2):
  - **`ComplementoDaConclusao`:** um por Conclusão; `ano_ingresso` obrigatório; CHECK
    "Se presente, `data_ingresso.year == ano_ingresso`".
  - **`ContextoInstitucionalAgregado`:**
    - `UniqueConstraint(fonte, metrica, curso, unidade, ano, apurado_em,
      nulls_distinct=False)`: duas linhas da métrica 2 com `curso` nulo e a mesma chave
      falham;
    - CHECK de curso conforme a métrica;
    - textos não vazios;
    - `valor` não negativo.

- [X] T035 [P] Escrever `tests/contexto_trajetoria/test_carga.py`, um caso para cada linha
  da tabela "Carga" de contracts/contexto-da-trajetoria.md:
  - **Pessoa sem Conclusões daquela fonte:** `SEM_CONCLUSOES`, sem chamada à fonte (fonte
    espiã).
  - **Indisponível:** `INDISPONIVEL`, nada gravado, sem exceção, Pessoa e Conclusões
    intactas.
  - **Complementos:** novo → cria; igual → nada; diferente → divergência em log (sem
    valores pessoais) e nada muda; acréscimo posterior numa Conclusão sem complemento.
  - **Agregados:**
    - chave nova → cria;
    - mesma chave e valor → nada (duas Pessoas do mesmo recorte → um registro);
    - mesma chave e valor diferente → log de erro de fonte (só fonte, métrica e recorte) e
      nada gravado;
    - nova `apurado_em` → registro novo, sem alterar o anterior.
  - Logs emitidos só depois do commit.

- [X] T036 [P] Escrever `tests/contexto_trajetoria/test_isolamento.py` (FR-071; SC-014):
  - `preparar()` com fonte de contexto indisponível conclui sem erro e sem nenhum registro
    de contexto;
  - a Maria entra pela 018, responde, conclui e abre `/minha-trajetoria/` com a narrativa
    P1;
  - `incorporar_com_material` e `incorporar_pessoa` não chamam a fonte de contexto (espiã
    sem chamadas).

### Implementação

- [X] T037 Criar `trajetoria/fonte_academica/contexto_da_trajetoria.py` conforme data-model
  §1 e contracts/contexto-da-trajetoria.md:
  - estruturas: `ComplementoNaFonte`, `MetricaAgregada` (`Enum` com os valores
    `"conclusoes_curso_unidade_ano"` e `"conclusoes_unidade_ano"`), `AgregadoNaFonte` e
    `ContextoDaTrajetoriaNaFonte`;
  - `ContextoIndisponivel(Exception)`;
  - `FonteDeContextoDaTrajetoria(Protocol)`;
  - validações no `__post_init__` reutilizando o padrão "Atributo ausente é `None`; cadeia
    vazia é proibida" (sem importar funções privadas de `contrato.py`: duplicar os dois
    auxiliares de três linhas).

  Python puro.

- [X] T038 Em `trajetoria/fonte_academica/cenarios.py`, acrescentar `COMPLEMENTOS` e
  `AGREGADOS` com os valores de R18, com o comentário "fictícios; não afirmam que a fonte
  real fornece ingresso ou agregados (021 FR-064)". Criar
  `trajetoria/fonte_academica/contexto_simulado.py: ContextoSimulado`:
  - `codigo = "simulada"`;
  - `indisponivel=False`;
  - `obter_contexto(ids)` devolve complementos dos ids pedidos e agregados dos recortes
    (curso+unidade+ano; unidade+ano) das conclusões reconhecidas pedidas, sem repetir
    chave, em ordem determinística.

- [X] T039 Criar o app `trajetoria/contexto_trajetoria/` (`apps.py`, `models.py`,
  `migrations/`) e acrescentar `"trajetoria.contexto_trajetoria"` em `INSTALLED_APPS`.
  - **`ComplementoDaConclusao`:**
    - `conclusao = OneToOneField(ConclusaoAcademica, on_delete=PROTECT, primary_key=True,
      related_name="complemento")`;
    - `ano_ingresso = PositiveSmallIntegerField()`;
    - `data_ingresso = DateField(null=True)`;
    - `obtido_em = DateTimeField(auto_now_add=True)`;
    - CHECK no padrão de `conclusao_ano_coerente_com_data`.
  - **`ContextoInstitucionalAgregado`:**
    - `id` UUID;
    - `fonte`, `metrica` (choices de `MetricaAgregada`), `curso` (nulo), `unidade`, `ano`,
      `valor` (`PositiveIntegerField`), `apurado_em`, `obtido_em`;
    - `UniqueConstraint(fields=["fonte", "metrica", "curso", "unidade", "ano",
      "apurado_em"], nulls_distinct=False, name="agregado_chave_unica")`;
    - CHECKs de curso conforme a métrica e de textos não vazios.
  - Gerar `0001_initial.py` (aditiva).

- [X] T040 Implementar `trajetoria/contexto_trajetoria/carga.py: carregar_contexto(
  fonte_de_contexto, pessoa) -> ResultadoDaCarga`, conforme data-model §2.3 e a tabela do
  contrato:
  - consulta fora da transação;
  - `transaction.atomic()` própria;
  - `on_commit` para os logs (`logger = logging.getLogger("trajetoria.contexto_trajetoria")`);
  - nunca propaga `ContextoIndisponivel`.

- [X] T041 Em `trajetoria/demonstracao/cenario.py: preparar()`, depois do laço de
  incorporação:
  - para cada Pessoa preparada, chamar `carregar_contexto(fonte_de_contexto, pessoa)`
    dentro de `transaction.atomic()` (*savepoint*). O preparo já roda numa transação
    externa, então ali a consulta à fonte simulada (em memória) fica dentro dela. Fora do
    preparo vale a regra "consulta fora da transação" do T040;
  - capturar qualquer exceção com `logger.warning` sem dado pessoal e seguir;
  - aceitar o parâmetro `fonte_de_contexto=None` (padrão `ContextoSimulado()`) para os
    testes;
  - incluir no `Resumo` a contagem de contextos carregados, se o `Resumo` listar
    contagens.

  Ajustar o teste do preparo existente que verifica o resumo, se houver.

---

## Fase 9 — US5: ingresso, quando a fonte o informa (P2) (3 tasks)

**Goal:** frase de início com ingresso coerente; nada sem ingresso; 012/013 intactas
(FR-046 a FR-051).

**Independent Test:** `pytest tests/narrativa/test_ingresso.py`; quickstart P2, item 1.

- [X] T042 [P] [US5] Escrever `tests/narrativa/test_ingresso.py`:
  - **Frase de início:**
    - Ana → "Sua trajetória no Ifes começou em 2019, em Tecnologia em Análise e
      Desenvolvimento de Sistemas.";
    - Maria → nenhuma;
    - dois ingressos com o mesmo menor ano → nenhuma.
  - **Coerência:** ingresso posterior ao ano de conclusão (fonte de teste) → omitido e log
    sem dado pessoal.
  - **Card:** nunca contém ingresso.
  - **012 e 013** (SC-007): com o complemento carregado, capturar um snapshot (012) e gerar
    uma exportação (013). Nenhum campo ou coluna novo e nenhum valor de ingresso.

- [X] T043 [US5] Em `trajetoria/narrativa/consultas.py: entrada_da_pessoa`:
  - ler o complemento (`select_related("complemento")`, tolerando ausência);
  - validar a coerência (FR-051) e, se incoerente, registrar log sem dado pessoal (fonte e
    id externo da Conclusão) e não repassar;
  - preencher `FatoDaFormacao.ingresso_ano`/`ingresso_data`.

- [X] T044 [US5] Em `trajetoria/narrativa/montagem.py`:
  - formulação `inicio` (FR-050) só para a formação de menor `ingresso_ano`, quando único,
    na seção "Sua trajetória acadêmica";
  - `Formacao.ingresso` na serialização;
  - o `compartilhavel` continua sem ingresso.

---

## Fase 10 — US6: contexto institucional daquele ano (P2) (5 tasks)

**Goal:** duas métricas, com sujeito "conclusões", só com exatamente uma apuração
coerente, nunca calculadas da base local (FR-052 a FR-061).

**Independent Test:** `pytest tests/narrativa/test_agregados.py`; quickstart P2, itens 1 a
3.

- [X] T045 [P] [US6] Escrever `tests/narrativa/test_agregados.py`:
  - **Ana:** "Em 2022, 27 conclusões de Tecnologia em Análise e Desenvolvimento de Sistemas
    foram registradas na unidade Serra, incluindo a sua.", "Em 2022, 812 conclusões foram
    registradas na unidade Serra." e "Dados institucionais apurados em 31/01/2026.".
  - **Maria:** as mesmas frases para TADS; nada para o Cefor; a métrica 2 sem repetição.
  - **Diego:** seção ausente.
  - **Duas apurações do mesmo recorte:** ambas omitidas (SC-011).
  - **Coerência:** valor menor que as Conclusões da mesma fonte no recorte → omitido e log
    só com fonte, métrica e recorte.
  - **Fonte diferente:** agregado de outra fonte não se aplica.
  - **Base parcial:** sem agregado carregado, nenhuma seção, mesmo com várias Conclusões
    locais no recorte (SC-009).
  - **N = 1:** forma singular.
  - **Linguagem:** todas as frases têm "conclus" como sujeito da contagem e nenhum termo de
    `VEDADAS`.
  - **Card:**
    - o SVG contém no máximo um par de frases de agregado, o da primeira formação com
      agregado (FR-033);
    - Diego, com mais de uma formação com agregado num cenário de teste, mostra só o par
      da primeira;
    - tudo fica dentro da área segura no pior caso (nome + 4 formações + "e mais N" + um
      par de agregados).

- [X] T046 [P] [US6] Escrever `tests/contexto_trajetoria/test_volume.py` (SC-008):
  `carregar_contexto` para N Pessoas fictícias do mesmo recorte resulta em exatamente um
  registro por métrica e apuração.
  - N = 20 na suíte padrão.
  - N = 500 com `@pytest.mark.volume`.

- [X] T047 [US6] Em `trajetoria/narrativa/consultas.py`, implementar a seleção (research
  R14):
  - para cada Conclusão com curso, unidade e ano: agregados da mesma fonte e recorte
    exato; exatamente um → segue; senão omite;
  - contagem de `ConclusaoAcademica` da mesma fonte no recorte maior que o valor → omite e
    registra log;
  - deduplicar a métrica 2 por (unidade, ano);
  - preencher `EntradaDaNarrativa.agregados` em ordem determinística (pela ordem das
    formações e depois métrica 1 antes da 2).

- [X] T048 [US6] Em `trajetoria/narrativa/montagem.py`:
  - seção `naquele_ano` com `agregado_curso`/`agregado_unidade` + `apuracao` (data em
    `dd/mm/aaaa`);
  - `contextos_agregados` serializados com `origem: "agregado"`;
  - `compartilhavel.contextos_agregados` com no máximo um par (o da primeira formação, na
    ordem de exibição, com agregado), com as frases e as linhas quebradas.

- [X] T049 [US6] Em `trajetoria/narrativa/templates/narrativa/card.svg` e `card.py`,
  ligar o bloco de agregados, já desenhado e validado no pior caso da Fase 3, aos dados
  reais de `compartilhavel.contextos_agregados`. Se o pior caso do T045 deixar de caber,
  parar e levar a questão ao solicitante, sem reduzir o limite de 4 formações.

---

## Fase 11 — US7: segundo tema visual (P3) — fora desta entrega (0 tasks)

O plan deixa a P3 fora desta entrega. O template do card já recebe `tema`, que é o ponto de
extensão do FR-065. O formato 4:5 para o feed também é direção P3. Uma spec ou um pedido
explícito abre as tasks.

---

## Fase 12 — Acabamento e verificações transversais (6 tasks)

- [X] T050 [P] Notas de revisão nas features anteriores, no formato usado pela 019:
  - **`specs/014-polish-jornada-egresso/spec.md`:**
    - FR-030 passa a "Suas formações no Ifes" (021 FR-006);
    - FR-041: a ação única leva a "Minha trajetória no Ifes" (021 FR-003);
    - entrada com `ANTECIPACAO` (021 FR-070).
  - **`specs/018-identificacao-acesso-egresso/spec.md:768`:** "Minha Trajetória:
    especificada pela 021".
  - **`specs/001-nucleo-academico-fonte-simulada/contracts/fonte-academica.md`:** nota
    "a capacidade de contexto da trajetória é separada; ver 021
    contracts/contexto-da-trajetoria.md".
  - **`specs/001-nucleo-academico-fonte-simulada/contracts/cenarios-simulados.md`:** seção
    "Contexto da trajetória (021)" com os valores fictícios de R18.

- [X] T051 [P] Se o `README.md` listar rotas ou passos da demonstração, acrescentar
  `/minha-trajetoria/` e a nota de que a fonte de contexto simulada é carregada pelo
  `preparar_demonstracao`.

- [X] T052 Rodar e deixar verde:
  - `uv run ruff check .`;
  - `uv run python manage.py check`;
  - `uv run python manage.py makemigrations --check --dry-run`;
  - `uv run pytest`;
  - `uv run pytest -m volume tests/narrativa tests/contexto_trajetoria`.

- [ ] T053 Executar o [quickstart](quickstart.md) manual (P1 e P2) em 320, 375 e 1280 px,
  sem JavaScript e com JavaScript. Salvar capturas em
  `specs/021-minha-trajetoria-narrativa/evidencias/`:
  - página e card (com e sem nome);
  - card no story de teste.

  Completar `validacao.md`.

- [X] T054 [P] Varredura final de linguagem: rodar a varredura de `VEDADAS` (T014/T045)
  também sobre os templates da 021 e sobre os textos novos de `interface/mensagens.py`.

- [X] T055 Atualizar o **Status** de `spec.md` e o registro de implementação ao fim deste
  arquivo.

## Fase 13 — Convergência visual: card editorial e página em capítulos (P1 visual reaberta) (10 tasks)

**Origem:** [auditoria de convergência visual](../../docs/auditorias/2026-10-04-021-convergencia-visual.md),
com as decisões do solicitante de 2026-10-05:

- **V1:** assinatura oficial no card de demonstração;
- **V2:** ilustração vetorial própria;
- **V3:** fecho com `#SouEgressoIfes`.

**Goal:** o card e a página passam de relatório textual a peça editorial da trajetória
(E8, FR-074 a FR-083, SC-015), com os mesmos dados. Domínio, montagem das frases, P2 e
rotas não mudam.

**Porta:** o solicitante revisa o conjunto de PNGs de referência (T064) antes do merge do
PR #30. Esta fase vem antes de qualquer outra mudança da P2.

**Superadas na composição** (o pipeline, a área segura e a quebra por largura real
continuam): T008 a T010 (card em texto empilhado), T029 (seção do card na página, que só
muda de lugar) e a estrutura de seções do T021.

### Testes

- [X] T056 [P] [US3] Escrever `tests/narrativa/test_card_editorial.py` (SC-015, FR-074 a
  FR-082). **Casos de referência:**
  - 1, 2, 3, 4 e mais de 4 formações;
  - com e sem agregados;
  - com e sem nome;
  - unidade sem imagem própria (cai na genérica).

  **Para cada caso**, a partir do SVG gerado:
  - **(a) Ordem das zonas:** abertura → título → linha do tempo → destaques → fecho →
    rodapé, conferida pela coordenada y.
  - **(b) Elemento dominante:** a abertura ocupa ≥ 20% da área do quadro.
  - **(c) Linha do tempo:** um nó (`circle` da classe do nó) por formação exibida; traço
    quando há 2 ou mais.
  - **(d) Destaques:** número com `font-size` ≥ 80; rótulo com no máximo 2 linhas.
  - **(e) Ocupação:** nenhuma faixa vazia contínua > 160 px entre elementos dentro de y
    270–1650.
  - **(f) Hierarquia e proveniência:**
    - ≥ 4 tamanhos de fonte distintos;
    - título ≥ 80;
    - "Dados institucionais apurados" só abaixo do fecho, com tamanho ≤ 30.
  - **(g) Área segura e legibilidade:**
    - todo `<text>` dentro de x 90–990 e y 270–1650 (topo pelo tamanho, base pelo
      descendente);
    - sem sobreposição de caixas de texto;
    - conteúdo ≥ 40 e rodapé ≥ 26.
  - **(h) Legenda:** casa com "^(Unidade .+|Ifes) · (ilustração|fotografia)$" e não
    contém ano de 4 dígitos.
  - **(i) Catálogo e vedações:** nenhuma frase fora do catálogo e nenhum termo de
    `VEDADAS`.
  - **(j) Fecho e hashtag:** "Essa história também é minha." e "#SouEgressoIfes"
    presentes.
  - **(k) Determinismo:** a mesma entrada gera o mesmo SVG.
  - **(l) Contraste:** AA de todo par texto/fundo do `TEMA_CARD`.
  - **(m) Hex de ação da 015:** ausentes de `card.py` e do template.

- [X] T057 [P] [US3] Escrever `tests/narrativa/test_imagens.py` (FR-076, R20):
  - existe exatamente uma entrada genérica (`unidade is None`);
  - toda entrada tem `tipo` em {"ilustração", "fotografia"} e `origem` e `licenca` não
    vazios;
  - o arquivo existe, é SVG válido e não contém `<text>`;
  - a escolha é pela unidade da primeira formação exibida e cai na genérica;
  - a legenda é "Unidade Serra · ilustração", ou "Ifes · ilustração" sem unidade.

### Implementação

- [X] T058 [US3] Criar `trajetoria/narrativa/imagens/ifes-generica.svg`:
  - ilustração vetorial **própria**, sem texto e sem reproduzir prédio real;
  - prédio, palmeiras e gramado estilizados na paleta do card, como no protótipo da
    auditoria.

  Criar também `trajetoria/narrativa/imagens.py` com a tupla `CATALOGO` (entradas
  `ImagemInstitucional(unidade, arquivo, tipo, origem, licenca)`), `imagem_para(unidade)` e
  `legenda(imagem, unidade)` (R20).

- [X] T059 [US3] Em `trajetoria/narrativa/catalogo.py`, acrescentar as formulações do card
  editorial de contracts/catalogo.md:
  - `DESTAQUE_CURSO` e `DESTAQUE_UNIDADE` (rótulos singular/plural em 2 linhas);
  - `CARD_APURACAO`, `LEGENDA`, `FECHO`, `HASHTAG`, `CAPITULO`;
  - os títulos de capítulo.

  Atualizar `FORMULACOES` e o teste estrutural do catálogo.

- [X] T060 [US3] Em `trajetoria/narrativa/contrato.py` e `montagem.py`:
  - `ContextoCompartilhavel` passa a `metrica`, `numero`, `rotulo: tuple[str, ...]`;
  - `Compartilhavel` ganha `apuracao: str | None` (texto do rodapé) e `unidade_da_imagem`
    (a unidade da primeira formação exibida).

  A semântica não muda (FR-078): o mesmo par da primeira formação com agregado. Atualizar
  `serializar`, contracts/narrativa.md (a versão do contrato continua 1, porque ainda não
  foi publicado fora do PR) e os testes da montagem e do contrato.

- [X] T061 [US3] Reescrever a composição de `trajetoria/narrativa/card.py` por zonas (R19)
  e o template `templates/narrativa/card.svg`:
  - **Zonas:** `marca` (a `interface/assinatura.svg` embutida), `abertura` (imagem do
    catálogo + legenda + borda em onda), `titulo`, `linha_do_tempo`/`no`, `destaques`,
    `fecho` (frase + pílula da hashtag), `rodape`, `faixa_inferior`.
  - **Constantes:** `TEMA_CARD`, `AREA_SEGURA = (90, 270, 990, 1650)`, mínimo e máximo da
    abertura.
  - **Medidas:** uma única tabela para medir e desenhar.
  - **Comportamento:** ocupação pela abertura e ordem de corte do FR-082.
  - **Preservar:** `largura`, `quebrar_linhas`, `quebrar_atributos`, `descricao`
    (`<title>`/`<desc>`) e `rasterizacao.py` sem mudança.
  - **Testes antigos:** atualizar `tests/narrativa/test_card.py` onde ele fixava a
    composição antiga (linha "N formações registradas no Ifes", rodapé em 1570).

- [X] T062 [US1] Reestruturar a página em capítulos (FR-026, FR-083, R21):
  - **`views.py`:** distribui as seções da narrativa em abertura e capítulos e calcula
    "Capítulo k de N".
  - **`minha_trajetoria.html`:**
    - abertura com a imagem inline e a legenda;
    - capítulos em blocos de largura total, com fundo alternado;
    - linha do tempo com nó e traço em CSS;
    - cartões de destaque com número grande + frase completa + apuração;
    - seção do card no fim.
  - **`narrativa.css`:** com os tokens do tema do card para os elementos editoriais.
  - **Sem JavaScript novo.**
  - **Testes:** atualizar `tests/narrativa/test_pagina.py`, `test_pagina_card.py`,
    `test_acessibilidade.py` e `test_rotas.py` onde fixavam os títulos antigos. Acrescentar
    os testes:
    - indicador só com 2 ou mais capítulos;
    - legenda sem ano;
    - capítulo de continuidade só com 2 ou mais formações;
    - capítulo "Naquele ano" só com agregado.

- [X] T063 [US3] Criar `specs/021-minha-trajetoria-narrativa/evidencias/gerar_referencias.py`,
  script avulso que usa o **renderer real**. Ele gera
  `evidencias/referencia-{caso}.png` para os casos do T056:
  - Ana (1 formação + agregados);
  - Maria (2 + agregados, com e sem nome);
  - Diego (3, sem agregados);
  - 4 formações;
  - pior caso (mais de 4, nomes longos);
  - unidade sem imagem própria.

### Validação e porta

- [X] T064 Porta de revisão do solicitante:
  - rodar a suíte completa e o ruff;
  - verificar a página em 320, 375 e 1280 px no navegador do app;
  - enviar os PNGs de referência ao solicitante;
  - registrar a aprovação, ou os ajustes pedidos, em `validacao.md`.

  **Sem aprovação, o PR #30 continua em rascunho.**

- [X] T065 Atualizar o status da spec, a descrição do PR #30, as evidências e este registro.
  Fazer o push. O CI do PNG (T007) roda nesse push.

---

## Dependências

```text
Fase 1 → Fase 2 → Fase 3 (PNG + pior caso; PORTA) → Fase 4 US2 → Fase 5 US1 → Fase 6 US4
                                                                          └→ Fase 7 (card na página)
P1 completo + validação no celular → Fase 8 (fundação P2) → Fase 9 US5 ─┐
                                                       └→ Fase 10 US6 ─┴→ Fase 12
```

- A Fase 3 depende só da Fase 2 (`Compartilhavel`). O card é testado com dados montados à
  mão.
- US5 e US6 são independentes entre si. As duas dependem da Fase 8.

## Paralelismo

| Momento | Pode rodar em paralelo |
|---|---|
| Fase 2 | T003 e T004 |
| Fase 3 | T008 enquanto o spike T007 roda no CI |
| Fase 4 | T013 e T014 |
| Fase 5 | T016 a T019 |
| Fase 6 | T023 a T025 |
| Fase 7 | T028 e T030 |
| Fase 8 | T032 a T036 (testes); depois T037 e T038, antes de T039 a T041 |
| Fases 9 e 10 | Em paralelo entre si |

## Estratégia

1. **Primeiro, comprovar o objetivo (Fases 1 a 3):** PNG no CI e pior caso legível.
   Porta de decisão.
2. **MVP (Fases 4 a 6):** narrativa honesta, página e fronteiras. Já substitui o
   "obrigado" isolado.
3. **Card na página (Fase 7):** prévia, salvar, baixar e compartilhar. Fecha a P1. Parar
   para validação no celular.
4. **P2 (Fases 8 a 10):** enriquecimento simulado, isolado de 001, 018 e 019, depois que a
   experiência P1 estiver funcionando.
5. **Acabamento:** notas, quickstart e evidências.

## Registro de implementação

- **2026-10-04 — Fases 1 e 2:** concluídas (T001 a T006).
- **2026-10-04 — Fase 3 (porta de decisão):**
  - **T008 a T011:** concluídas. O card SVG 9:16 tem área segura e mede o texto com as
    larguras reais das fontes (`metricas.py`, gerado uma vez). A rasterização está
    isolada.
  - **Mudança em relação ao texto da task:** o `card.py` mede largura real em vez de usar
    `LIMITES` por número de caracteres. Também quebra os atributos só entre " · "
    (`quebrar_atributos`). O rodapé do card passou a "Instituto Federal do Espírito
    Santo", porque o título já diz "Minha trajetória no Ifes".
  - **T007 (spike):** aprovado no macOS arm64. **CI pendente** até o push do PR (ADR
    0006).
  - **T012 (pior caso):** o pior caso **não cabe inteiro** com corpo ≥ 40 px na área
    segura. Foi implementada para avaliação uma composição adaptativa: até 4 formações,
    tantas quantas couberem, mais "e mais N"; agregados só se couberem. Evidências em
    `validacao.md`. **Decisão do solicitante: composição adaptativa aprovada.** O CI do PNG
    fica para o PR final.
- **2026-10-04 — Fases 4 a 7:** concluídas (T013 a T030).
  - **Narrativa pura:** sem banco nem relógio.
  - **Página:** "Minha trajetória no Ifes"; `/formacoes/` passa a "Suas formações no
    Ifes", com ligação e antecipação; a confirmação leva à narrativa.
  - **Fronteiras:** testes de 001/012/013/018/019.
  - **Card:** rotas PNG (inline) e SVG (attachment); prévia `<img>` 9:16; nome por GET sem
    JavaScript; "Baixar imagem (PNG)"; "Compartilhar imagem" oculto e revelado só com
    `navigator.canShare({files})` (arquivo preparado antes do toque); fallback SVG.
  - **Ajustes fora do texto das tasks:**
    - `interface/base.html` ganhou um `{% block estilo %}` vazio;
    - as faixas do card usam `--cor-texto` (a 015 veda os hex de ação no código);
    - `tests/interface/test_interface_fronteiras.py` admite
      `trajetoria.narrativa.consultas.elegivel` na interface.
  - **Suíte completa:** 2.372 testes verdes. ruff e `makemigrations --check` limpos.
- **T031 (validação no celular):** parcial. Verificado no navegador do app em 375 px
  (Maria): sem rolagem horizontal, prévia PNG 1080 × 1920, nome só com a opção marcada,
  "Compartilhar" oculto onde não há compartilhamento de arquivos. **Pendente com o
  solicitante:** aparelho real (iOS/Android), toque longo, menu de compartilhamento e story
  de teste.
- **2026-10-04 — Fases 8 a 10 (P2):** concluídas (T032 a T049).
  - **Capacidade de contexto separada da `FonteAcademica`:**
    `fonte_academica/contexto_da_trajetoria.py` (contrato puro) e `contexto_simulado.py`.
    `contrato.py`, `simulada.py`, `academico/`, `acesso/` e `declaracao/` não foram tocados.
  - **App `contexto_trajetoria`:** dois models, migração `0001` aditiva e
    `carga.carregar_contexto` (consulta fora da transação; indisponível não grava nem
    propaga; sinais só depois do commit).
  - **Preparo da demonstração:** carrega o contexto depois da incorporação, num savepoint
    por Pessoa.
  - **Narrativa:** frase de início com ingresso coerente; seleção dos agregados com
    exatamente uma apuração, trava pela base local e métrica por unidade sem repetição.
    A montagem e o card já tratavam ambos.
  - **Testes:** isolamento (preparo, login, resposta e narrativa com contexto
    indisponível), 012/013 intactas com complemento carregado, volume (20 na suíte, 500
    marcado `volume`).
- **2026-10-04 — Fase 12:**
  - **Concluídas:**
    - T050: notas de revisão em 014, 018 e nos contratos 001 (`fonte-academica.md`,
      `cenarios-simulados.md`);
    - T051: README;
    - T052: verificação completa;
    - T054: varredura de termos vedados nos templates e textos novos;
    - T055: status.
  - **T053 parcial:** 320, 375 e 1280 px verificados no navegador do app. Falta o celular
    real e o story de teste (solicitante).
  - **Ficam abertas:**
    - **T007:** CI do PNG no PR.
    - **T031 e T053:** validação no celular, com o solicitante.
- **2026-10-05 — Pausa e reabertura da P1 visual:**
  - A auditoria de convergência visual comparou o mockup, os PNGs atuais e os artefatos.
  - O card foi considerado um relatório diagramado e a P1 visual foi reaberta. Decisões V1
    a V3 do solicitante.
  - Spec (E8, FR-026/029/036/040 revisados, FR-074 a FR-083, SC-015, DP-2102/2106
    atualizadas, DP-2110), research (R10 revisado, R19 a R21), plan, contratos (`card.md`
    reescrito, `catalogo.md`, `rotas.md`) e a Fase 13 (T056 a T065) foram atualizados.
  - PR #30 convertido em rascunho.
  - **Renderer ainda não alterado:** a revisão da direção visual pelo solicitante vem
    antes.
- **2026-10-05 — T007:** spike do PNG aprovado também no CI (ubuntu, Python 3.13): check
  `testes` do PR #30 verde. ADR 0006 atualizada.
- **2026-10-05 — Fase 13, T056 a T063 implementadas:**
  - **Card editorial (T061):** `card.py` reescrito por zonas, com uma função por zona que
    mede e desenha (marca, abertura, título, linha do tempo, destaques, fecho, rodapé,
    faixa inferior). Abertura entre y = 420 e y = 890; ordem de corte do FR-082.
  - **Decisões de medida na implementação** (registradas em `contracts/card.md`, FR-081 e
    R19):
    - texto de apoio entre 30 e 36 px, como no protótipo aprovado;
    - legenda na faixa da marca quando não colide com ela;
    - destaques lado a lado ou empilhados, conforme os rótulos cabem; sem caber, saem;
    - token `marca_escura` (`#257a33`) para o ano: no celular, 44 px viram ~15 px, texto
      comum, e o verde da marca daria 3,1:1;
    - acima do máximo da abertura, a sobra se divide em volta do conteúdo.
  - **Contrato (T060):** `ContextoCompartilhavel(metrica, numero, rotulo)`;
    `Compartilhavel.apuracao` e `unidade_da_imagem`. Par com apurações distintas fica só
    com o primeiro destaque. A linha "N formações registradas no Ifes" saiu do card.
  - **Página (T062):** abertura com imagem e legenda, capítulos com indicador, linha do
    tempo e cartões de destaque em CSS, sem JavaScript novo.
  - **Testes:** `test_card_editorial.py` (critérios a–m em 8 casos), `test_imagens.py` e
    os ajustes dos testes antigos. Checagem por mutação: contraste, ocupação e
    sobreposição de nó com texto são detectados.
  - **Referências (T063):** `evidencias/referencia-*.png`, 7 casos, pelo pipeline real.
- **2026-10-05 — T064 e T065:** suíte completa (2563 aprovados, 3 pulados) e ruff limpos;
  página verificada a 320, 375 e 1280 px; PNGs de referência **aprovados pelo solicitante**
  sem ajustes. Status da spec, evidências e descrição do PR #30 atualizados; push feito.
  Continuam abertas só T031 e T053 (celular real e story de teste, com o solicitante).
