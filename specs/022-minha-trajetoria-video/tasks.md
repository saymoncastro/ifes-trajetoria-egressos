---
description: "Tasks da Feature 022 — Minha Trajetória em vídeo"
---

# Tasks: Minha Trajetória em vídeo

**Input**: `specs/022-minha-trajetoria-video/`, com:

- spec (40 FRs, 8 SCs);
- plan;
- research R0–R18 (com o spike);
- data-model;
- contracts (`composicao-visual`, `renderizador`, `template-video`, `rotas`);
- quickstart;
- ADR 0007 (proposto).

Constituição 2.0.0.

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/.

**Tests**: Princípio XXVI e a "Matriz mínima de verificação automatizada" da spec. São
obrigatórios para:

- o SVG do card inalterado;
- os textos do vídeo iguais aos do card;
- o conteúdo vedado;
- o formato do arquivo;
- o quadro final igual ao card;
- a área segura em movimento;
- os quatro estados;
- a ausência de duplicata;
- a retenção;
- a entrega só à sessão;
- o isolamento do domínio;
- os logs sem dado pessoal.

Os testes de cada fase são escritos antes e falham antes da implementação. Cobertura não é
meta.

## Formato e convenções

- `- [ ] Tnnn [P?] [USn?] descrição com caminho`.
- **[P]:** arquivo diferente e sem dependência de task incompleta.
- **Ordem das fases:**
  1. A Fase 3 (US2, porta de decisão) prova o vídeo real no CI Linux antes de construir
     estado, rotas e página. O solicitante prefere provar o objetivo principal primeiro.
  2. Depois vêm US3 (casos extremos), US1 (fluxo do egresso) e US4 (espera e falha).
- **Fixtures e casos reutilizados:**
  - `tests/narrativa/construcao.py`: `compartilhavel`, `caso_maria`, `caso_ana`,
    `caso_diego`, `caso_quatro`, `pior_caso`, `caso_sem_imagem_propria`,
    `caso_sem_unidade`, `cenario_narrativa`, `entrar`;
  - `tests/narrativa/conftest.py`: `modo_demonstracao`, `relogio`, `cenario`.
- **Marcador:** os testes que precisam do Node usam `precisa_renderizador`
  (`tests/video/conftest.py`):
  - **sem renderizador:** são pulados, com o motivo;
  - **com `CI=true`:** a indisponibilidade **falha** o teste.
- **Proibido em todas as tasks:**
  - alterar `TrajetoriaNarrativa`, `Compartilhavel`, `serializar()` ou o SVG do card;
  - gravar em qualquer tabela de domínio;
  - logar composição, chave, nome, curso ou a saída do Node;
  - chamar `node`/`npx` fora de `trajetoria/video/renderizador.py`;
  - acessar a rede durante o render;
  - criar Celery, broker ou fila em arquivos.

---

## Fase 1 — Setup (6 tasks)

- [X] T001 Criar o projeto Node `video/` (research R1):
  - **`video/package.json`:**
    - `"name": "trajetoria-video"`, `"private": true`, `"type": "module"`;
    - `"engines": {"node": ">=22"}`;
    - dependências **exatas**: `remotion`, `@remotion/bundler`, `@remotion/renderer` e
      `@remotion/cli` em `4.0.533`; `react` e `react-dom` em `19.3.0`;
    - script `"garantir-navegador": "remotion browser ensure"`.
  - **`video/package-lock.json`:** gerado por `npm install --prefix video`.
  - **`video/tsconfig.json`:** `jsx: react-jsx`, `strict`, `module: esnext`,
    `moduleResolution: bundler`, `noEmit`.
  - **`video/README.md`:** o que é, `npm ci`, `browser ensure`, contrato do
    `renderizar.mjs`, licença (Remotion Free License para organizações sem fins lucrativos;
    DP-2201), proibição de rede no render.

- [X] T002 [P] Acrescentar `video/node_modules/` ao `.gitignore`, na seção "Python /
  ferramentas", com o comentário "Projeto de vídeo (Feature 022)".

- [X] T003 Criar o app `trajetoria/video/`:
  - `__init__.py`;
  - `apps.py` com `VideoConfig(name="trajetoria.video")`;
  - `urls.py` com `urlpatterns = []`;
  - `templates/video/`;
  - `management/__init__.py` e `management/commands/__init__.py`.

  Também:
  - em `config/settings.py`:
    - acrescentar `"trajetoria.video"` em `INSTALLED_APPS`, logo depois de
      `"trajetoria.contexto_trajetoria"`, com o comentário "Feature 022: vídeo (estado
      técnico)";
    - acrescentar as variáveis do data-model §4: `TRAJETORIA_VIDEO_PROJETO = BASE_DIR /
      "video"`, `TRAJETORIA_VIDEO_NODE` (padrão `shutil.which("node")`),
      `TRAJETORIA_VIDEO_NAVEGADOR` (padrão `""`), `TRAJETORIA_VIDEO_TEMPO_MAXIMO`
      (120 s), `TRAJETORIA_VIDEO_CONCORRENCIA` (2) e `TRAJETORIA_VIDEO_RETENCAO`
      (`timedelta(hours=2)`; recusar na carga valor acima de 24 h, DP-2202);
  - em `config/urls.py`, acrescentar `path("", include("trajetoria.video.urls"))` **antes**
    do `include` de `trajetoria.narrativa.urls` e citar a Feature 022 na docstring.

- [X] T004 [P] Em `pyproject.toml`, acrescentar a `[project.optional-dependencies].dev`
  `numpy>=2,<3` e `Pillow>=11,<12`, só para comparar quadros nos testes (research R14).
  Atualizar `uv.lock` com `uv lock`.

- [X] T005 [P] Criar `tests/video/__init__.py`, `tests/video/conftest.py` e
  `tests/video/construcao.py`:
  - **`conftest.py`:**
    - reexporta `modo_demonstracao`, `relogio` e `cenario` de `tests/narrativa/conftest.py`;
    - registra o marcador `precisa_renderizador`: pula com
      `"renderizador de vídeo indisponível"` quando `renderizador.disponivel()` é falso;
      com `os.environ.get("CI") == "true"`, chama `pytest.fail`;
    - fixture `renderizador_falso(monkeypatch)`: substitui `renderizador.renderizar` por
      uma função que devolve `b"\x00\x00\x00\x18ftypisom" + b"0" * 64` e registra as
      chamadas;
    - fixture `renderizador_com_falha(monkeypatch)`: levanta
      `FalhaDeRenderizacao("codigo_1")`.
  - **`construcao.py`:** `CASOS = {"maria": caso_maria, "ana": caso_ana, "diego":
    caso_diego, "quatro": caso_quatro, "pior": pior_caso, "sem_imagem":
    caso_sem_imagem_propria, "sem_unidade": caso_sem_unidade}`, a partir de
    `tests/narrativa/construcao.py`, e `composicao(caso, nome=None)`, que chama
    `composicao_visual(...)`.
  - Registrar o marcador em `pyproject.toml` (`markers`).

- [X] T006 [P] Em `.github/workflows/ci.yml`, no job `testes`, antes de `uv run pytest`
  (research R15):
  - `actions/setup-node@v4` com `node-version: "22"`, `cache: npm` e
    `cache-dependency-path: video/package-lock.json`;
  - `npm ci --prefix video`;
  - `npx --prefix video remotion browser ensure`;
  - `env: CI: "true"` no passo do pytest, para os testes de mídia serem obrigatórios.

  Não criar job novo: o ruleset da `main` exige `testes`.

---

## Fase 2 — Fundação: composição por zonas e fronteira (8 tasks)

**Bloqueia todas as histórias.**

### Testes

- [X] T007 Escrever `tests/narrativa/test_card_zonas.py` **antes** de alterar `card.py`
  (research R3; data-model §1):
  - **Regressão byte a byte:** para cada caso de `tests/video/construcao.CASOS`, com nome
    `None` e `"Maria Exemplo"`, o SHA-256 de `card.card_svg(...)` é igual a uma constante
    gravada no teste. As constantes são geradas com o código **atual da `main`**, antes da
    T010.
  - **Invariantes das zonas:**
    - as chaves de `compor(...).zonas` seguem a ordem de `ZONAS`: `fundo`, `abertura`,
      `marca`, `legenda`, `titulo`, `nome`, `traco`, `nos`, `mais`, `destaques`,
      `apuracao`, `fechamento`, `rodape`, só as presentes;
    - o multiconjunto dos elementos de todas as partes é igual a `compor(...).elementos`,
      sem falta nem repetição;
    - `len(zona("nos").partes) == compor(...).exibidas`;
    - `traco` presente só com 2 ou mais nós;
    - `mais` só com omitidas;
    - `destaques` com uma parte por cartão;
    - `apuracao` só com destaques;
    - `nome` só com nome.

- [X] T008 [P] Escrever `tests/video/test_composicao.py`
  (contracts/composicao-visual.md; FR-004 a FR-008, FR-020 a FR-022):
  - **Forma:** `versao_contrato == 1`, `template == "trajetoria-v1"`, `largura == 1080`,
    `altura == 1920`, `area_segura == [90, 270, 990, 1650]`; `traco` traz `y1 < y2`.
  - **Textos = card:** o conjunto de textos de todos os `<text>` das partes (via
    `xml.etree` sobre `<svg>…</svg>`) é igual ao conjunto de textos do `card_svg` do
    mesmo caso, sem `<title>`/`<desc>`.
  - **Vedados:**
    - nenhum texto contém termo de `catalogo.VEDADAS`, `"certificado"`, `"comprovante"`,
      `"declaração"`, padrão de CPF (`\d{3}\.\d{3}\.\d{3}-\d{2}`) ou data completa
      (`\d{2}/\d{2}/\d{4}` fora da linha de apuração);
    - nenhuma chave `id`, `cpf`, `data_nascimento`, `forma_oferta`, `ingresso` ou
      `data_conclusao` em nenhum nível.
  - **Nome:** presente só quando passado; `nome=None` → sem zona `nome` e sem o texto em
    nenhuma parte.
  - **Escape:** `nome='Ana <b>&amp; "Cia"'` aparece escapado (`&lt;b&gt;`, `&amp;amp;`,
    `&quot;`) e a parte continua XML válido.
  - **Determinismo:** duas chamadas dão o mesmo JSON canônico e a mesma
    `chave_da_composicao`; nome ligado e desligado dão chaves diferentes; trocar
    `TEMPLATE_DE_VIDEO` (monkeypatch) muda a chave.
  - **Sem dependências indevidas:** o módulo não importa `trajetoria.academico`,
    `participacao` nem `video`.

- [X] T009 [P] Escrever `tests/video/test_fronteira.py` (FR-027, FR-038;
  contracts/renderizador.md):
  - nenhum arquivo `.py` em `trajetoria/` além de `trajetoria/video/renderizador.py`
    contém `"node"` como executável, `"npx"`, `"remotion"` ou `subprocess` (busca
    textual, com lista explícita de exceções);
  - `renderizador.renderizar` com `TRAJETORIA_VIDEO_NODE` apontando para um script falso
    que ecoa a entrada no `stderr` e sai com código 1 levanta
    `FalhaDeRenderizacao("codigo_1")`, e `caplog` não contém o nome nem o curso;
  - script falso que dorme além de `TRAJETORIA_VIDEO_TEMPO_MAXIMO=1` →
    `FalhaDeRenderizacao("tempo_esgotado")`;
  - saída vazia ou sem `ftyp` → `saida_invalida`;
  - código 2 → `entrada_invalida`;
  - código 3 → `navegador_ausente`;
  - o diretório temporário não existe depois de cada caso;
  - `disponivel()` é falso sem `node`, sem `video/node_modules/remotion` ou sem o
    navegador provisionado.

### Implementação

- [X] T010 Alterar `trajetoria/narrativa/card.py` (data-model §1; research R3):
  - criar `@dataclass(frozen=True) class Zona: chave: str; partes: tuple[tuple[Elemento,
    ...], ...]` e a tupla `ZONAS` na ordem do data-model §1.4;
  - fazer as funções de zona produzirem também a parte: `linha_do_tempo` agrupa por nó
    (`no`, `no-centro`, `ano`, `curso`, `detalhe` do nó; `traco` e `mais` à parte);
    `destaques` agrupa por cartão; `fecho_e_rodape` separa `fechamento` (`fecho`,
    `hashtag-fundo`, `hashtag`), `rodape` (`rodape`) e `apuracao` (`apuracao`);
  - `Composicao` ganha `zonas: tuple[Zona, ...]`; `elementos` continua sendo produzido
    **exatamente na ordem atual**.
  - Nenhuma regra de layout muda. A T007 passa.

- [X] T011 Implementar `trajetoria/narrativa/composicao.py` (data-model §2;
  contracts/composicao-visual.md):
  - `TEMPLATE_DE_VIDEO = "trajetoria-v1"`, `VERSAO_CONTRATO = 1`;
  - `composicao_visual(compartilhavel, nome, demonstracao) -> dict`:
    - chama `card.compor`;
    - para cada parte, usa `render_to_string("narrativa/card.svg", {"largura": …,
      "altura": …, "elementos": parte, "titulo": "", "descricao": ""})` e extrai o trecho
      entre `</desc>` e `</svg>` (`strip`);
    - `traco` leva `y1`/`y2` do elemento `line`;
  - `canonico(dict) -> str`: `json.dumps(…, ensure_ascii=False, sort_keys=True,
    separators=(",", ":"))`;
  - `chave_da_composicao(dict) -> str`: SHA-256 hexadecimal de `canonico`;
  - docstring: "a chave nunca é exposta (research R6)".

  A T008 passa.

- [X] T012 Implementar `trajetoria/video/renderizador.py` (contracts/renderizador.md):
  - `class FalhaDeRenderizacao(Exception)` com o atributo `motivo`;
  - `disponivel()` com `functools.cache`: `TRAJETORIA_VIDEO_NODE` executável, `(PROJETO /
    "node_modules" / "remotion").is_dir()` e navegador provisionado
    (`TRAJETORIA_VIDEO_NAVEGADOR` existente, ou diretório
    `node_modules/.remotion/chrome-headless-shell` presente);
  - `renderizar(composicao) -> bytes` e `quadros(composicao, quadros) -> dict[str, bytes]`:
    - `tempfile.TemporaryDirectory()`;
    - `subprocess.run([node, "renderizar.mjs", entrada, saida, *extras], cwd=PROJETO,
      env={"PATH", "HOME", "TRAJETORIA_VIDEO_CONCORRENCIA", "TRAJETORIA_VIDEO_NAVEGADOR"},
      capture_output=True, timeout=TEMPO_MAXIMO)`;
    - mapeia os códigos 2 e 3, `TimeoutExpired` e a saída inválida para os motivos do
      contrato;
    - **nunca loga `stdout`/`stderr`**; loga só `logger.warning("video: falha na
      geração (%s)", motivo)` no logger `trajetoria.video`.

  A T009 passa. Acrescentar o logger `trajetoria.video` em `LOGGING`, se o
  `trajetoria` pai não cobrir.

- [X] T013 Implementar `video/renderizar.mjs` (contracts/renderizador.md; research R11,
  R12):
  - **Argumentos:** `entrada.json`, saída, `--quadros` opcional.
  - **Validações:** JSON inválido, `versao_contrato !== 1` ou `template !==
    'trajetoria-v1'` → `process.exit(2)`.
  - **Navegador:** ausente (verificar o executável de `TRAJETORIA_VIDEO_NAVEGADOR` ou o
    diretório `node_modules/.remotion/chrome-headless-shell`) → `exit(3)`, sem chamar
    `ensureBrowser`.
  - **Bundle e composição:** `bundle({entryPoint: 'src/index.ts', publicDir:
    '../trajetoria/narrativa/fontes'})`; `selectComposition({id: 'trajetoria-v1',
    inputProps: {composicao}})`.
  - **Vídeo:** `renderMedia({codec: 'h264', pixelFormat: 'yuv420p', colorSpace: 'bt709',
    muted: true, concurrency: Number(process.env.TRAJETORIA_VIDEO_CONCORRENCIA ?? 2),
    browserExecutable: process.env.TRAJETORIA_VIDEO_NAVEGADOR || null})`.
  - **`--quadros`:** `renderStill` por quadro, gravando `quadro-<n>.png`; `fim` =
    `durationInFrames - 1`.
  - **Erros:** qualquer exceção → `exit(1)`.

- [X] T014 Criar `video/src/index.ts` (`registerRoot(Root)`) e `video/src/Root.tsx`:
  - `<Composition id="trajetoria-v1" component={TrajetoriaV1} width={1080} height={1920}
    fps={30} durationInFrames={240} …/>`;
  - `calculateMetadata` com `durationInFrames = 240 + (nos === 4 ? 18 : 0)`, conforme
    contracts/template-video.md.

  O componente pode, nesta task, desenhar as zonas sem animação. A animação entra na T018.

---

## Fase 3 — US2: o vídeo é o card em movimento (P1, porta de decisão) (6 tasks)

**Goal**: um MP4 real, no formato pedido, cujo último quadro é o card, gerado no CI Linux.

**Independent Test**: para Maria, Ana e o caso de 4 formações, renderizar o MP4 e os
quadros-chave e comparar com o PNG do card.

**Porta de decisão**: se o CI Linux não atingir os critérios da T015 e da T016 (formato,
tempo ≤ 60 s, SSIM do quadro final), **parar e reportar ao solicitante** antes da Fase 4.
O fallback é o R17.

### Testes

- [X] T015 [P] [US2] Escrever `tests/video/test_midia.py`, todo com `precisa_renderizador`
  (FR-009, FR-010, FR-018; research R13, R14):
  - para `maria`, `ana` e `quatro`, chamar `renderizador.renderizar(composicao(...))` e
    gravar num `tmp_path`;
  - verificar com `npx --prefix video remotion ffprobe -v error -show_entries
    stream=codec_type,codec_name,pix_fmt,color_space,width,height,r_frame_rate,nb_frames:format=duration
    -of json`:
    - **exatamente um** stream, `codec_type == "video"`;
    - `h264`, `yuv420p`, `bt709`, 1080 × 1920, `30/1`;
    - `nb_frames` 240 (maria, ana) e 258 (quatro);
    - duração 8,0 ou 8,6 s ± 1/30;
  - o arquivo começa com `ftyp` no byte 4 e `moov` aparece antes de `mdat` (`faststart`);
  - **determinismo no mesmo ambiente:** duas renderizações de `maria` dão bytes idênticos;
  - **tempo:** cada render termina em menos de 60 s (SC-006); registrar o tempo medido no
    `print` para o `validacao.md`.

- [X] T016 [P] [US2] Escrever `tests/video/test_quadros.py`, parte "card", com
  `precisa_renderizador` (FR-013 a FR-015, FR-017; SC-002; research R14):
  - **Auxiliar `_ssim(a, b)`:** SSIM global por blocos 8 × 8 em tons de cinza, com
    numpy/Pillow, como no spike.
  - **Último quadro × PNG do card** (`rasterizacao.png_de(card.card_svg(...))`) para
    `maria` (com nome), `ana` e `quatro`: SSIM ≥ 0,98 e no máximo 3% dos pixels com
    diferença > 32.
  - **Estabilidade:** os quadros `fim − 30` e `fim` têm diferença máxima ≤ 2 níveis.
  - **Rodapé:** a região do rodapé (`y` da primeira linha de `rodape` − 8 até `BASE`) é
    igual (diferença ≤ 2) nos quadros 0, 30, 120, 189 e `fim`.
  - **Faixa inferior** (`y > BASE + 30`): igual em todos os quadros amostrados.
  - **Números estáticos:** em todo quadro amostrado depois da entrada dos destaques, a
    região de cada `numero` é igual à do último quadro.

### Implementação

- [X] T017 [US2] Implementar o carregamento das fontes em `video/src/TrajetoriaV1.tsx`:
  - `FontFace('Open Sans', url(staticFile('OpenSans-Regular.ttf')), {weight: '400'})` e
    a versão `700` com `OpenSans-Bold.ttf`;
  - `delayRender('fontes')` até `Promise.all(load)`; adicionar a `document.fonts`;
    `continueRender`;
  - em erro, `cancelRender(erro)` (render falha com código 1; não cai para fonte do
    sistema).

- [X] T018 [US2] Implementar a animação de `video/src/TrajetoriaV1.tsx` exatamente como em
  contracts/template-video.md:
  - `<AbsoluteFill style={{backgroundColor: '#f6f2e8'}}>` com `<svg width=1080
    height=1920 viewBox="0 0 1080 1920">`;
  - cada parte numa `<g dangerouslySetInnerHTML>`;
  - **estáticas desde o quadro 0:** `fundo` e `rodape`;
  - **janelas por zona, em quadros:**
    - `abertura` 0–21, com escala só no `<g>` da imagem (1,04 → 1,00 até o quadro 39,
      `transformOrigin: '540px 0px'`);
    - `marca` 4–21;
    - `legenda` 9–21, com +12 px;
    - `titulo` 21–39;
    - `nome` 33–51;
    - `nos[i]` a partir de 51 + i·p, com `p = (150 + extra − 51) / (nós + (mais ? 1 : 0))`
      e duração `min(p, 18)`;
    - `mais` logo depois;
    - `traco` revelado por `clipPath: inset(0 0 X% 0)` do início do primeiro nó até o fim
      do último;
    - `destaques[i]` a partir de 150 + extra + 8i, por 18 quadros;
    - `apuracao` com o primeiro destaque;
    - `fechamento` 189 + extra → 207 + extra, **só opacidade**;
  - translação +24 → 0 px nas zonas de texto;
  - *easing* `Easing.bezier(0.22, 1, 0.36, 1)` com `extrapolateLeft/Right: 'clamp'`;
  - sem `spring`, filtro, desfoque, 3D ou contador.

  As T015 e T016 passam.

- [X] T019 [US2] Rodar a porta de decisão:
  - `uv run pytest tests/video/test_midia.py tests/video/test_quadros.py` localmente e
    num push para o PR (CI Linux);
  - registrar em `specs/022-minha-trajetoria-video/validacao.md` (criar): tempos,
    `ffprobe`, SSIM medidos no macOS e no Linux, tamanho do `node_modules` e do navegador
    no CI, bibliotecas de sistema que faltaram (se alguma);
  - se algum critério falhar no Linux, **parar** e apresentar ao solicitante: o valor
    medido, a causa e o ajuste proposto (tolerância, `apt-get` ou fallback R17).

- [X] T020 [US2] Atualizar `docs/adr/0007-renderizacao-do-video.md` com o resultado do CI
  (seção "Resultado do spike", linha "CI ubuntu") e mudar o estado para **aceito**, se a
  porta passou.

---

## Fase 4 — US3: vídeo correto em todos os casos (P1) (4 tasks)

**Goal**: a matriz de casos extremos sem texto cortado, sobreposto ou fora da área segura,
sem bloco vazio nem zero inventado.

**Independent Test**: `uv run pytest tests/video/test_composicao.py
tests/video/test_quadros.py -k casos`.

### Testes

- [X] T021 [P] [US3] Ampliar `tests/video/test_composicao.py` com a matriz (FR-012,
  FR-013, FR-023, FR-039):
  - **1, 2, 3 e 4 nós:** `len(nos.partes)` igual às formações exibidas pelo card.
  - **Pior caso:** mesmas formações exibidas e mesmo texto "e mais N formações
    registradas" do card.
  - **Destaques:**
    - sem agregado: sem zonas `destaques` e `apuracao`, e nenhum `<text class="numero">`;
    - um destaque (apurações distintas): uma parte;
    - dois: duas partes, com os números e rótulos do card.
  - **Imagem e legenda:** `sem_imagem` traz a ilustração genérica e a legenda "Unidade X ·
    ilustração"; `sem_unidade` traz "Ifes · ilustração"; nenhuma legenda contém ano.
  - **Acentos:** "ç", "ã" e "é" preservados nas partes (UTF-8, `ensure_ascii=False`).
  - **Composição impossível:** forçar `card.compor` a não caber no mínimo (monkeypatch de
    `BASE` ou um título gigante) → `composicao_visual` levanta `ComposicaoImpossivel`. Não
    devolve composição cortada.

- [X] T022 [P] [US3] Ampliar `tests/video/test_quadros.py` com `-k casos` e
  `precisa_renderizador` (FR-017; SC-004):
  - para `diego` (3), `quatro` (4), `pior` e `ana` com nome longo
    (`"Maria Aparecida dos Santos Albuquerque de Oliveira"`), gerar quadros nas fronteiras
    das janelas: 21, 39, 51, cada início e fim de nó, 150, 168, 189, 207 e `fim` (com
    `extra`);
  - **máscara de texto em movimento** (analyze U1), para cada quadro *n* da lista:
    - renderizar, **no mesmo quadro *n***, a composição reduzida sem as zonas de texto
      animadas (`titulo`, `nome`, `nos`, `mais`, `destaques`, `apuracao`, `fechamento`),
      com `renderizador.quadros(composicao_reduzida, [n])`. As zonas ficam com a **mesma
      contagem de partes**, mas com marcação vazia: o tempo e a duração dependem do número
      de nós, e a abertura escala igual nos dois renders;
    - a máscara são os pixels com diferença > 32 entre o quadro completo e o reduzido;
  - verificar:
    - **nenhum pixel da máscara** com `x < 90`, `x > 990`, `y < 270` ou `y > 1650`, sem
      exceção. Marca e legenda ficam fora da máscara, porque estão nos dois renders;
    - **nenhum pixel da máscara** dentro da região do rodapé (`y` da primeira linha de
      `rodape` − 8 até `BASE`), o que prova que nenhum texto em movimento cobre o rodapé;
    - **rodapé intacto** em todos esses quadros.

### Implementação

- [X] T023 [US3] Em `trajetoria/narrativa/composicao.py`:
  - criar `class ComposicaoImpossivel(Exception)`;
  - levantá-la quando `card.compor` devolver `exibidas == 0` com formações no
    compartilhável, ou quando a soma das alturas mínimas não couber;
  - log técnico `"video: composição impossível"`, sem conteúdo (FR-039).
  - A T021 passa.

- [X] T024 [US3] Ajustar `video/src/TrajetoriaV1.tsx` só se a T022 falhar, mantendo
  contracts/template-video.md: reduzir a translação do componente que invade (nunca acima
  de 24 px) ou atrasar a entrada. Se o ajuste mudar tempo ou duração perceptível, atualizar
  o contrato e registrar no `validacao.md`.

---

## Fase 5 — US1: gerar e baixar o vídeo (P1) (9 tasks)

**Goal**: na página, o egresso pede o vídeo, acompanha o preparo, assiste à prévia, baixa
e compartilha.

**Independent Test**: com o renderizador falso, `POST` → `processar_videos --uma-vez` →
página "pronto" → `GET video.mp4` com `200` e `206`. Com o real, o quickstart, cenários 1
a 7.

### Testes

- [X] T025 [P] [US1] Escrever `tests/video/test_estado.py` (data-model §3; FR-028 a
  FR-032):
  - `solicitar` sem linha → `SOLICITADO` com `composicao` e `expira_em = solicitado_em +
    TRAJETORIA_VIDEO_RETENCAO`;
  - `solicitar` com `SOLICITADO`, `PROCESSANDO` ou `PRONTO` não vencido → nenhuma mudança e
    nenhuma linha nova;
  - `solicitar` com `FALHOU` ou vencida → volta a `SOLICITADO` com `motivo=""`,
    `video=None`, `iniciado_em` e `concluido_em` nulos, e novos `solicitado_em` e
    `expira_em`;
  - `estado_para`:
    - ausente ou vencida → `"nenhum"`;
    - `SOLICITADO` ou `PROCESSANDO` → `"preparando"`;
    - `PRONTO` → `"pronto"`;
    - `FALHOU` → `"falhou"`;
  - **`limpar()`** (data-model §3.1; analyze P1):
    - apaga as linhas com `expira_em < agora` **em qualquer estado**, inclusive
      `SOLICITADO` e `FALHOU`;
    - `PROCESSANDO` iniciado há mais de 5 min → `FALHOU("tempo_esgotado")` com
      `composicao=None`;
    - `SOLICITADO` há mais de 10 min → `FALHOU("sem_processador")` com `composicao=None`;
  - **Limpeza sem processador:** com o relógio avançado 11 min e **nenhum** processador,
    `estado_para(chave)` devolve `"falhou"` e a linha já tem `composicao is None`; avançado
    além da retenção, `estado_para` devolve `"nenhum"` e a linha não existe. Prova que
    `solicitar`, `estado_para` e `video_pronto` chamam `limpar()`;
  - **toda linha tem `expira_em`:** inserir sem ele → `IntegrityError` (`NOT NULL`);
  - `CheckConstraint`s rejeitam `PRONTO` sem vídeo, `FALHOU` sem motivo e `SOLICITADO`
    sem composição (`IntegrityError`);
  - a tabela não tem FK (`GeracaoDeVideo._meta.get_fields()` sem relação).

- [X] T026 [P] [US1] Escrever `tests/video/test_processador.py` com `renderizador_falso`
  (research R7):
  - `call_command("processar_videos", "--uma-vez")` processa o `SOLICITADO` mais antigo →
    `PRONTO` com `video`, `tamanho`, `concluido_em` e `expira_em = concluido_em +
    TRAJETORIA_VIDEO_RETENCAO`, e `composicao is None`;
  - **sem pedido:** termina sem erro;
  - **com `renderizador_com_falha`:** `FALHOU("codigo_1")` e `composicao is None`;
  - **um por ciclo:** com dois `SOLICITADO`, um `--uma-vez` processa só o mais antigo;
  - **`skip_locked`:** uma linha travada noutra transação não é tomada (teste com
    `transaction.atomic` e `select_for_update` em outra conexão, ou verificação da
    consulta);
  - **gravação condicionada** (analyze U2): com um renderizador falso que, durante o
    render, muda a linha (chama `solicitar` depois de forçá-la a `FALHOU`, simulando
    "Tentar novamente", ou apaga a linha), o resultado é **descartado**. A linha continua
    como a mudança a deixou, nenhum `PRONTO` é gravado e o log técnico
    `"video: resultado descartado"` aparece, sem conteúdo;
  - **`caplog`:** sem nome, curso nem chave.

- [X] T027 [P] [US1] Escrever `tests/video/test_rotas.py` com `renderizador_falso` e
  `cenario` (contracts/rotas.md; FR-001, FR-002, FR-021, FR-025, FR-026, FR-034, FR-035):
  - **Abrir a página:** `GET /minha-trajetoria/` não cria linha (FR-002); mostra "Gerar
    vídeo" com `renderizador.disponivel` forçado a verdadeiro.
  - **Pedir:**
    - `POST /minha-trajetoria/video/` sem CSRF → `403`; com CSRF (`Client(enforce_csrf_checks=True)`
      e token da página) → `303` para `/minha-trajetoria/#video` e uma linha `SOLICITADO`;
    - com `nome=1` → `303` para `/minha-trajetoria/?nome=1#video`, e a chave difere da
      sem nome.
  - **Preparo e prova:** a página mostra "Estamos preparando seu vídeo…"; depois de
    `processar_videos --uma-vez`, mostra `<video controls playsinline preload="metadata"`
    sem `autoplay`, `poster` igual ao `card.png` da mesma escolha e o link "Baixar vídeo
    (MP4)" com `download="minha-trajetoria-ifes.mp4"`.
  - **`GET /minha-trajetoria/video.mp4`:**
    - sem `Range` → `200`, `video/mp4`, `Accept-Ranges: bytes`,
      `Content-Disposition: inline; filename="minha-trajetoria-ifes.mp4"`,
      `Cache-Control` com `no-store`;
    - `Range: bytes=0-1` → `206`, `Content-Range: bytes 0-1/<total>` e 2 bytes;
    - `bytes=10-` e `bytes=-5` → `206` corretos;
    - `bytes=999999-` → `416` com `Content-Range: bytes */<total>`;
    - vários intervalos (`bytes=0-1,4-5`) → `200` completo;
    - sem `PRONTO` → `404`;
    - com `nome=1` sem vídeo da escolha com nome → `404`.
  - **Entrega só à sessão:** sem sessão → redireciona para `/acesso/`; outra Pessoa
    (Diego) não recebe o vídeo de Maria (`404`).
  - **Estado JSON:** `GET /minha-trajetoria/video/estado` → `{"estado": …}` nos quatro
    valores.
  - **Sem JavaScript:** todo o fluxo funciona só com `Client`, sem execução de script.
  - **Escolha do nome:** respeitada só com `Pessoa.nome` (FR-021).
  - **Modo de demonstração desligado** (FR-003; analyze C1): com
    `settings.TRAJETORIA_DEMONSTRACAO = False`, `POST /minha-trajetoria/video/`,
    `GET /minha-trajetoria/video.mp4` e `GET /minha-trajetoria/video/estado` → `404`, e
    nenhuma linha é criada.
  - **Acessibilidade do bloco** (FR-036; analyze C2):
    - o bloco `#video` tem `aria-live="polite"`;
    - o `<video>` tem `controls` e `aria-describedby` apontando para um elemento cujo texto
      é igual a `card.descricao(...)` da mesma escolha;
    - nenhum `autoplay`, `muted autoplay` ou `meta http-equiv="refresh"` na página;
    - o botão "Compartilhar vídeo" nasce com `hidden`;
    - "Gerar vídeo", "Tentar novamente" e "Atualizar" são `<button>` de formulário ou
      `<a href>`, ou seja, focáveis por teclado sem `tabindex` artificial.

### Implementação

- [X] T028 [US1] Implementar `trajetoria/video/models.py: GeracaoDeVideo` exatamente como no
  data-model §3:
  - **Campos:**
    - `chave = CharField(max_length=64)`;
    - `template = CharField(max_length=40)`;
    - `estado = CharField(max_length=12, choices=[SOLICITADO, PROCESSANDO, PRONTO,
      FALHOU])`;
    - `composicao = JSONField(null=True)`;
    - `video = BinaryField(null=True)`;
    - `tamanho = PositiveIntegerField(null=True)`;
    - `motivo = CharField(max_length=40, blank=True)`;
    - `solicitado_em = DateTimeField()`;
    - `iniciado_em` e `concluido_em = DateTimeField(null=True)`;
    - `expira_em = DateTimeField()` — **obrigatório**: "sempre definido, em toda
      transição, como momento da transição + `TRAJETORIA_VIDEO_RETENCAO`" (data-model §3;
      analyze P1).
  - **`Meta.constraints`:**
    - `UniqueConstraint(fields=["chave"])`;
    - `CheckConstraint`: `PRONTO` ⇒ `video__isnull=False`;
    - `CheckConstraint`: `FALHOU` ⇒ `motivo` não vazio;
    - `CheckConstraint`: `SOLICITADO` ⇒ `composicao__isnull=False`.
  - **`Meta.indexes`:** `Index(fields=["estado", "solicitado_em"])` e
    `Index(fields=["expira_em"])`.
  - **Docstring:** "estado técnico, não entidade de domínio; sem FK (FR-028; research
    R6)".
  - Gerar `trajetoria/video/migrations/0001_initial.py` com `makemigrations video`.

- [X] T029 [US1] Implementar `trajetoria/video/operacoes.py` (data-model §3.1 e §3.2):
  - **`solicitar(composicao) -> None`:** chama `limpar()`; depois `transaction.atomic` e
    `select_for_update` por `chave_da_composicao`; aplica a tabela de transições, sempre
    definindo `expira_em`.
  - **`estado_para(chave) -> str`:** chama `limpar()`; devolve `"nenhum"`,
    `"preparando"`, `"pronto"` ou `"falhou"` conforme o data-model §3.2.
  - **`processar_proximo() -> bool`:**
    - numa transação curta, toma o `SOLICITADO` mais antigo com
      `select_for_update(skip_locked=True)`, marca `PROCESSANDO` com `iniciado_em` e
      `expira_em`, guarda `id` e `iniciado_em` lidos e copia a `composicao` para a memória;
      confirma;
    - chama `renderizador.renderizar` **fora** da transação;
    - **gravação final condicionada** (analyze U2):
      `GeracaoDeVideo.objects.filter(id=id, estado=PROCESSANDO,
      iniciado_em=iniciado_em_lido).update(...)`, para `PRONTO` (`video`, `tamanho`,
      `concluido_em`, `expira_em`, `composicao=None`) ou `FALHOU(motivo)` (`concluido_em`,
      `expira_em`, `composicao=None`);
    - se o `update` afetar 0 linhas, descarta o resultado e loga só `"video: resultado
      descartado"`.
  - **`limpar() -> None`**, exatamente as três linhas de `limpar()` do data-model §3.1:
    - `DELETE` onde `expira_em < agora`;
    - `PROCESSANDO` há mais de 5 min → `FALHOU("tempo_esgotado")`;
    - `SOLICITADO` há mais de 10 min → `FALHOU("sem_processador")`;
    - nas duas conversões: `composicao=None` e novos `concluido_em`/`expira_em`.
  - **`video_pronto(chave) -> bytes | None`:** chama `limpar()` antes de ler.
  - Tempo por `django.utils.timezone.now()`.

  A T025 passa.

- [X] T030 [US1] Implementar
  `trajetoria/video/management/commands/processar_videos.py`:
  - opção `--uma-vez`;
  - laço `limpar()` → `processar_proximo()` → `time.sleep(1)` se não houve trabalho;
  - encerramento limpo em `KeyboardInterrupt`;
  - mensagem inicial no `stdout`: "Processador de vídeos (Feature 022) — Ctrl+C para
    sair";
  - sem renderizador disponível, avisa uma vez e continua. Os pedidos viram
    `FALHOU("sem_processador")` pela limpeza depois de 10 min.

  A T026 passa.

- [X] T031 [US1] Implementar `trajetoria/video/mensagens.py` com os textos de
  contracts/rotas.md:
  - `TITULO = "Vídeo da sua trajetória"`;
  - `CONVITE = "Um vídeo curto, sem som, com o seu card em movimento."`;
  - `GERAR = "Gerar vídeo"`;
  - `PREPARANDO = "Estamos preparando seu vídeo…"`;
  - `CONTINUAR = "Você pode continuar usando esta página."`;
  - `ATUALIZAR = "Atualizar"`;
  - `BAIXAR = "Baixar vídeo (MP4)"`;
  - `COMPARTILHAR = "Compartilhar vídeo"`;
  - `FALHOU = "Não foi possível preparar o vídeo agora. Seu card continua disponível."`;
  - `TENTAR = "Tentar novamente"`;
  - `ARQUIVO = "minha-trajetoria-ifes.mp4"`.

- [X] T032 [US1] Implementar `trajetoria/video/views.py` e `trajetoria/video/urls.py`
  (contracts/rotas.md):
  - **Composição da sessão:** reusar `narrativa.views._pessoa_e_narrativa` e
    `_nome_escolhido`. Se forem privados, expor em `narrativa/views.py` uma função
    pública `composicao_da_sessao(request) -> dict`, que redireciona como a 021.
  - **`solicitar_video`** (`POST /minha-trajetoria/video/`, `require_POST`, `never_cache`):
    `operacoes.solicitar(...)` só se `renderizador.disponivel()`; `303` para
    `/minha-trajetoria/{'?nome=1' se nome}#video`.
  - **`video_mp4`** (`GET /minha-trajetoria/video.mp4`): `video_pronto(chave)` ou `404`.
    Suporte a um único intervalo `Range` (R8): `200`/`206`/`416`, `Accept-Ranges: bytes`,
    `Content-Disposition` inline com `mensagens.ARQUIVO` e `never_cache`.
  - **`estado_video`** (`GET /minha-trajetoria/video/estado`): `JsonResponse({"estado":
    …})`.
  - A chave nunca vai para URL, HTML ou log.

- [X] T033 [US1] Criar `trajetoria/video/templates/video/bloco.html` e ligá-lo à página:
  - **Estrutura e estados:** `<div id="video" aria-live="polite">` com `<h3>` e os quatro
    estados de contracts/rotas.md.
  - **Formulários:** `POST` com `{% csrf_token %}` e `<input type="hidden" name="nome"
    value="1">` quando a prévia está com nome.
  - **Prévia:** `<video controls playsinline preload="metadata" poster="{{ card.arquivo
    }}" aria-describedby="video-descricao">`, com um `<p id="video-descricao"
    class="visualmente-oculto">` contendo `card.alt`.
  - **Download:** `<a class="botao" href="/minha-trajetoria/video.mp4{{ sufixo }}"
    download="minha-trajetoria-ifes.mp4">`.
  - **Compartilhar:** `<button … id="compartilhar-video" hidden>`.
  - **Script inline opcional:**
    - em `preparando`, consulta `/minha-trajetoria/video/estado{{ sufixo }}` a cada 3 s e
      faz `location.reload()` quando o estado muda;
    - mostra o botão de compartilhar só com `navigator.canShare({files: [new File([blob],
      …, {type: 'video/mp4'})]})`;
    - sem `meta refresh`.
  - **Na página:**
    - em `trajetoria/narrativa/views.py: minha_trajetoria`, acrescentar ao contexto
      `video = {"disponivel", "estado", "sufixo"}`, montado por uma função de
      `trajetoria/video/operacoes.py`;
    - em `trajetoria/narrativa/templates/narrativa/minha_trajetoria.html`, dentro do
      capítulo `seu_card`, depois das ações do card, `{% if video.disponivel %}{% include
      "video/bloco.html" %}{% endif %}`.
  - A T027 passa.

---

## Fase 6 — US4: espera e falha não atrapalham (P1) (4 tasks)

**Goal**: falha, indisponibilidade ou demora não afetam página, card, Participação nem
Respostas.

**Independent Test**: `uv run pytest tests/video/test_isolamento.py`.

### Testes

- [X] T034 [P] [US4] Escrever `tests/video/test_isolamento.py` (FR-033, FR-037; SC-005):
  - **Contagens:** para pedido, processamento pronto, processamento com falha e
    indisponível, as contagens de todos os models **exceto** `video.GeracaoDeVideo` e
    `sessions` são iguais antes e depois (mesmo padrão de
    `tests/narrativa/test_sem_efeito.py`).
  - **Página com falha:** com `FALHOU`, `GET /minha-trajetoria/` é `200`, contém a
    mensagem de falha e "Tentar novamente", e o `card.png` continua `200`.
  - **Tentar novamente:** `POST` volta a `SOLICITADO`.
  - **Renderizador indisponível:**
    - a página não contém o bloco `#video` e o restante do HTML é igual ao da 021 (o
      teste de página da 021 continua verde);
    - `POST` → `303` sem linha nova.
  - **Sem processador:** `SOLICITADO` há 11 min (relógio) → página em "falhou".
  - **Snapshot e exportação:** a 012 e a 013 não contêm nada da 022. Ampliar
    `tests/narrativa/test_fronteiras.py` ou repetir a verificação.
  - **`caplog`:** em todos os cenários, sem nome, curso nem chave.

- [X] T035 [P] [US4] Ampliar `tests/narrativa/test_fronteiras.py`:
  - **`test_so_a_rasterizacao_importa_resvg`** continua valendo;
  - **novo `test_so_o_renderizador_chama_node`**, que reaproveita a busca da T009;
  - **novo `test_001_018_019_nao_conhecem_a_022`:** `trajetoria/academico`, `acesso` e
    `declaracao` não importam `trajetoria.video`.

### Implementação

- [X] T036 [US4] Garantir em `trajetoria/video/operacoes.py` e `views.py` que exceções
  inesperadas da camada de vídeo, na montagem do bloco, viram `estado = "falhou"` com log
  técnico, sem derrubar `/minha-trajetoria/`. Envolver só a chamada de montagem do bloco em
  `narrativa/views.py`.

- [X] T037 [US4] Rodar `uv run pytest tests/narrativa tests/video` e corrigir regressões da
  021. Os testes de página, card, PNG, sem efeito e fronteiras da 021 precisam continuar
  verdes sem alteração de expectativa, exceto as ampliações das T035 e T034.

---

## Fase 7 — Polish e validação (7 tasks)

- [X] T038 [P] Criar `specs/022-minha-trajetoria-video/evidencias/gerar_referencias.py`,
  script avulso como o da 021:
  - para os casos de referência da 021 (Maria com e sem nome, Ana, Diego, 4 formações, pior
    caso, sem imagem própria), gerar o MP4 e os quadros em ~1 s (30), ~4 s (120) e no
    final;
  - gravar em `evidencias/referencia-<caso>.mp4` e `referencia-<caso>-q<n>.png`.

- [X] T039 Gerar as referências **no ambiente do CI** (Linux) ou registrar a plataforma
  usada. Calibrar o limite de SSIM ≥ 0,97 dos quadros de ~1 s e ~4 s contra as referências
  (research R14) e acrescentar esse teste a `tests/video/test_quadros.py`. Registrar os
  valores medidos no `validacao.md`.

- [X] T040 **Porta humana (SC-008):** apresentar ao solicitante os quadros-chave e os MP4 de
  referência para aprovação **antes do merge**. Registrar a aprovação, ou os ajustes
  pedidos, no `validacao.md`.

- [ ] T041 Validação manual no celular (SC-008; quickstart, cenário 11):
  - prévia inline no iPhone (Safari) e no Android (Chrome);
  - download;
  - compartilhamento pelo menu do sistema;
  - publicação como story numa conta de teste.

  Registrar aparelho, sistema e resultado no `validacao.md`. Se não for possível antes do
  merge, registrar como pendente, como as T031/T053 da 021.

- [X] T042 [P] Notas de revisão na 021, sem mudar comportamento:
  - **`specs/021-minha-trajetoria-narrativa/contracts/card.md`:** seção "Composição por
    zonas (Feature 022)", que aponta para contracts/composicao-visual.md e registra que o
    SVG não muda;
  - **`contracts/narrativa.md`:** a nota em "Evolução" diz que o vídeo consome a
    composição do card, derivada do contrato, e não o contrato bruto;
  - **`README.md`:** linha da Feature 022 com o quickstart, o processo
    `processar_videos` e "somente demonstração".

- [X] T043 [P] Atualizar `docs/auditorias/2026-10-05-022-video-trajetoria.md` com uma linha
  final "Implementação: ver specs/022…/validacao.md". Atualizar a seção de execução do
  quickstart, se os comandos mudaram.

- [X] T044 Rodar o quickstart inteiro (cenários 1 a 10 e 12) num banco novo e as verificações
  finais:
  - `uv run ruff check .`;
  - `uv run python manage.py check`;
  - `uv run python manage.py makemigrations --check --dry-run`;
  - `uv run pytest`.

  Registrar o resultado no `validacao.md`.

---

## Dependências e ordem

```text
Fase 1 (Setup)
   └─► Fase 2 (Fundação: zonas, composição, fronteira)
          └─► Fase 3 (US2 — PORTA DE DECISÃO no CI Linux) ──┐
                 └─► Fase 4 (US3 — casos extremos)          │ se a porta falhar: parar,
                        └─► Fase 5 (US1 — fluxo do egresso)  │ reportar e decidir (R17)
                               └─► Fase 6 (US4 — espera, falha, isolamento)
                                      └─► Fase 7 (Polish, referências, porta humana)
```

- **Fase 2:** a T007 vem antes da T010, porque as constantes de hash são capturadas antes
  da refatoração. As T008 e T009 podem ser escritas em paralelo à T007. A T011 depende da
  T010; a T012 é independente da T010 e da T011; as T013 e T014 dependem da T001.
- **Fase 3:** depende das T011 a T014.
- **Fase 4:** só a parte de composição (T021, T023) pode começar logo depois da Fase 2. A
  parte de quadros (T022, T024) depende da Fase 3.
- **Fase 5:** as T025 a T027 (testes) podem começar logo depois da Fase 2, porque usam o
  renderizador falso. A implementação segue T028 → T029 → T030; T031 → T032 → T033.
- **Fase 6:** depende da Fase 5.
- **Fase 7:** depende de todas. A T040 é bloqueante para o merge.

## Paralelismo

- **Fase 1:** T002, T004, T005 e T006 em paralelo depois da T001 e da T003.
- **Fase 2:** T008 e T009 em paralelo com T007. T012 em paralelo com T010/T011. T013 e T014
  em paralelo entre si.
- **Fase 3:** T015 e T016 em paralelo; depois T017 → T018.
- **Fase 4:** T021 e T022 em paralelo.
- **Fase 5:** T025, T026 e T027 em paralelo; T031 em paralelo com T028 a T030.
- **Fase 6:** T034 e T035 em paralelo.
- **Fase 7:** T038, T042 e T043 em paralelo.

Exemplo (Fase 5, testes):

```text
Task: "T025 [US1] tests/video/test_estado.py"
Task: "T026 [US1] tests/video/test_processador.py"
Task: "T027 [US1] tests/video/test_rotas.py"
```

## Estratégia de implementação

1. **MVP técnico (porta):** Fases 1 a 3. Um MP4 real igual ao card, provado no CI Linux. Se
   falhar, parar antes de construir estado, rotas e página.
2. **Conteúdo correto:** Fase 4. A matriz inteira, sem overflow silencioso.
3. **MVP de produto:** Fase 5. O egresso gera, assiste, baixa e compartilha.
4. **Robustez:** Fase 6. Falha e espera isoladas.
5. **Aprovação:** Fase 7. Referências aprovadas pelo solicitante, celular real e quickstart
   completo.

Commits ao fim, no padrão do projeto:

- `docs(022): spec, plan e tasks — Minha Trajetória em vídeo`;
- `feat(022): …`.

## Critérios de teste independentes por história

| História | Teste independente |
|---|---|
| US2 — card em movimento | MP4 real no formato pedido; último quadro × PNG do card com SSIM ≥ 0,98; rodapé intacto; quadro final estável (T015, T016) |
| US3 — todos os casos | Matriz de composição e quadros de fronteira sem texto fora da área segura (T021, T022) |
| US1 — gerar e baixar | Pedido → processador → página pronta → `GET` com `200`/`206`, com o renderizador falso (T025 a T027) |
| US4 — espera e falha | Contagens de domínio inalteradas; página e card funcionando em falha e indisponibilidade (T034, T035) |
