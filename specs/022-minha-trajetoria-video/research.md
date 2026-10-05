# Research: Minha Trajetória em vídeo

Fase 0 do plan. Cada decisão registra o que foi escolhido, por quê e as alternativas
descartadas. As referências de código são da `main` em `a65d7cb`.

## R0 — Spike do Remotion (2026-10-05, macOS arm64, Apple M5 Pro, 15 núcleos)

Feito no scratchpad da sessão, fora do repositório.

**Pipeline real:** `montar` → `card.compor()` → zonas agrupadas por classe → JSON →
template Remotion → MP4. Três casos de referência:

- Maria: 2 formações, 2 destaques, com nome;
- Ana: 1 formação, 2 destaques;
- pior caso: 5 formações longas → 1 exibida e "e mais 4".

| Medida | Resultado |
|---|---|
| Versões | `remotion` 4.0.533 (exata), React 19, Node 26.5 (local) |
| `npm install` | 17 s; `node_modules` 225 MB |
| Chrome Headless Shell | Baixado na **primeira** renderização: 193 MB em `node_modules/.remotion/`. Precisa ser provisionado antes (R12) |
| FFmpeg/ffprobe | Embutidos em `@remotion/compositor-<plataforma>` (17 MB); `libx264` |
| Total em disco | ~590 MB, incluindo navegador e caches |
| Primeira renderização (com download do navegador) | 24,6 s |
| Bundle por renderização | 0,5 s (2,3 s a frio) |
| Render de 240 quadros, concorrência padrão | **3,0 a 3,3 s** |
| Render com concorrência 4 / 2 / 1 | 3,7 s / 4,8 s / **8,8 s** |
| Memória máxima (processo Node) | ~0,9 GB. As abas do Chrome são processos à parte; medir no Linux |
| Arquivo | H.264 High, 1080 × 1920, 30/1, 240 quadros, 8,000 s, ~0,74–0,80 MB, sem faixa de áudio |
| Espaço de cor | Padrão `yuvj420p` (faixa completa). Com `colorSpace: 'bt709'`: `yuv420p`, `tv`, BT.709 |
| `faststart` | `moov` antes de `mdat` (padrão do Remotion) |
| Determinismo | Três renderizações (concorrência padrão, padrão e 1) → **MP4 idêntico byte a byte** (`md5`) |
| Quadro final × PNG do card | SSIM 0,988–0,991; PSNR 29–30 dB; 1,2–1,5% dos pixels com diferença > 32 |

**Natureza da diferença no quadro final:** só a suavização das bordas dos glifos (Chromium
× resvg). Não há deslocamento de layout nem de quebra de linha. Ver
`evidencias/spike-quadro-final-vs-card.png` e `evidencias/spike-mapa-de-diferencas.png`.

**Quadros-chave** (`evidencias/spike-quadros-chave.png`):

- 1 s: abertura e título;
- 4 s: linha do tempo em curso;
- final: o card.

O storyboard se confirma.

**Ajustes que o spike revelou:**

- A linha de apuração ("Dados institucionais apurados em…") aparecia desde o primeiro
  quadro, antes dos destaques que ela qualifica. Passa a entrar com os destaques (R10).
- O espaço de cor padrão é de faixa completa. Fixa-se BT.709 de faixa limitada (R11).
- O navegador é baixado na primeira renderização. Passa a ser provisionado na instalação
  (R12).

## R1 — Remotion como motor, projeto Node isolado em `video/`

- **Decisão:**
  - Remotion **4.0.533 com versão exata** e React 19, num projeto Node próprio em `video/`,
    na raiz do repositório.
  - Arquivos: `package.json` e `package-lock.json` versionados; `node_modules/` ignorado.
  - Dependências diretas: `remotion`, `@remotion/bundler`, `@remotion/renderer`,
    `@remotion/cli`, `react` e `react-dom`. Nenhuma outra.
  - Node **22 LTS** como referência (o spike rodou no 26). O `package.json` declara
    `"engines": {"node": ">=22"}`.
- **Justificativa:**
  - Decisão do solicitante (spec E1).
  - O projeto isolado mantém o Node fora do pacote Python (o wheel só empacota
    `trajetoria/`) e torna a fronteira visível no repositório.
  - A versão exata reproduz o template.
- **Alternativas descartadas:**
  - **Node dentro de `trajetoria/`:** iria parar no pacote Python.
  - **`npx remotion` sem lockfile:** não é reprodutível.
  - **Remotion Lambda/Cloud Run:** infraestrutura externa, envio de dado pessoal a
    terceiro e custo.
  - **`@remotion/web-renderer` (no navegador do egresso):** depende do dispositivo, exige
    JavaScript e não é determinístico.

## R2 — Entrada: `ComposicaoVisual`, zonas com partes em marcação SVG

- **Decisão:**
  - A entrada do template é a `ComposicaoVisual` (contrato em
    [composicao-visual.md](contracts/composicao-visual.md)).
  - Cada zona tem uma ou mais **partes**. Cada parte é a marcação SVG dos seus elementos,
    produzida pelo **mesmo template Django do card** (`narrativa/card.svg`), com o mesmo
    escape.
  - A linha do tempo tem uma parte por nó, o traço com suas coordenadas e o "e mais N".
  - Os destaques têm uma parte por cartão.
- **Justificativa:**
  - O template não precisa conhecer tag, atributo nem regra. Ele só posiciona camadas no
    tempo (FR-006).
  - A marcação é exatamente a do card. Os textos já chegam escapados pelo Django: um nome
    com `<`, `&` ou aspas vira entidade (teste).
- **Alternativas descartadas:**
  - **JSON estruturado (`tag`, `atributos`, `texto`) com React criando elementos:**
    - exige mapear `font-family`, `text-anchor` etc. para JSX;
    - continua precisando de marcação crua para os ativos (`interior`);
    - é um segundo "renderizador de elementos" sem ganho.
  - **`compartilhavel` cru:** obrigaria o template a refazer layout, que é a alternativa B,
    descartada.

## R3 — Mudança interna na 021: `compor()` agrupado por zonas

- **Decisão:**
  - As funções de zona de `card.py` passam a devolver seus elementos rotulados com a zona e
    a parte.
  - `Composicao` ganha `zonas: tuple[Zona, ...]`. `elementos` continua existindo como
    concatenação, **na mesma ordem de hoje**, para o `card_svg`.
  - A serialização da composição fica num módulo novo, `narrativa/composicao.py`, que usa
    `render_to_string("narrativa/card.svg", …)` por parte.
- **Garantia:** o SVG do card fica **byte a byte igual** ao de antes. Um teste de regressão
  compara o SHA-256 dos SVGs dos casos de referência gerados antes da refatoração com os de
  depois.
- **Alternativas descartadas:**
  - **Inferir zonas pela `class` no vídeo**, como no spike: frágil para nós e cartões.
  - **Segundo `compor()` só para o vídeo:** dois layouts.

## R4 — Fronteira Python ↔ Node: um script, um módulo

- **Decisão:**
  - **Node:** `video/renderizar.mjs` é o único ponto de entrada. Contrato em
    [renderizador.md](contracts/renderizador.md):
    - `node renderizar.mjs <entrada.json> <saida.mp4>`;
    - modo de teste: `--quadros 30,120,fim` grava PNGs.
  - **Python:** `trajetoria/video/renderizador.py` é o único módulo que chama o Node, por
    `subprocess.run`:
    - lista de argumentos, sem shell;
    - `cwd=video/`;
    - ambiente mínimo (`PATH`, `HOME`, `TRAJETORIA_VIDEO_NAVEGADOR` quando definido);
    - tempo máximo de `TRAJETORIA_VIDEO_TEMPO_MAXIMO` (padrão 120 s);
    - entrada e saída num `TemporaryDirectory` apagado ao fim.
  - **Resultado:** bytes do MP4 ou `FalhaDeRenderizacao(motivo)`, com motivo curto e
    técnico (`tempo_esgotado`, `saida_invalida`, `codigo_<n>`).
  - **`stdout` e `stderr` nunca são logados:** podem ecoar a composição, com nome.
- **Justificativa:**
  - FR-038: o domínio não conhece o Remotion.
  - É o mesmo padrão de `rasterizacao.py` (ADR 0006): módulo único, disponibilidade
    consultável e falha sem efeito colateral.
- **Alternativas descartadas:**
  - **`npx remotion render` com flags montadas em Python:** espalha opções do Remotion
    (codec, espaço de cor) pelo Django.
  - **Servidor HTTP Node permanente:** mais um serviço para operar.
  - **Biblioteca de ponte Python ↔ Node:** dependência sem necessidade.

## R5 — Execução: assíncrona, com estado técnico mínimo

- **Decisão:** a solução 2 da spec (E4, FR-030).
  - `POST` registra o pedido (`SOLICITADO`) e responde na hora.
  - Um comando de gerenciamento processa os pedidos fora da requisição.
- **Justificativa (números do R0):**
  - O tempo depende do hardware de forma relevante: 3 s (15 núcleos) a 8,8 s (um processo
    de render) numa máquina rápida. Numa VM institucional típica de 2 vCPU, a estimativa é
    de 15 a 30 s, na faixa do tempo-limite padrão de proxies e servidores WSGI (30 s).
    **Não é previsível** no sentido do FR-030.
  - A partida a frio do Chrome e do bundle soma até ~3 s.
  - O FR-032 exige limitar gerações simultâneas. Com render síncrono, cada requisição
    concorrente seguraria um worker WSGI e um Chrome, e seria preciso uma trava
    entre processos de qualquer forma. Um único processador de pedidos limita a
    concorrência por construção.
  - O usuário vê "Estamos preparando seu vídeo…" e pode continuar usando a página (FR-034).
- **Alternativas descartadas:**
  - **Síncrono:** imprevisível e sem limite de concorrência natural.
  - **Thread no processo web:** perde-se no reinício e não limita entre processos.
  - **Pasta de pedidos como fila:** rejeitada pelo solicitante (E4).
  - **Celery/RQ/broker:** infraestrutura nova sem caso que a justifique (ADR 0001).

## R6 — Estado técnico: `GeracaoDeVideo`, sem vínculo com Pessoa

- **Decisão:**
  - Um model técnico no app novo `trajetoria/video/` (detalhes no
    [data-model](data-model.md)).
  - **Identidade:** `chave` = SHA-256 do JSON canônico da `ComposicaoVisual` (que já traz a
    versão do template). Única.
  - **Sem FK para Pessoa, Conclusão ou Participação.**
  - **`composicao` (JSON):** só existe enquanto o pedido espera processamento. É apagada ao
    concluir ou falhar.
  - **`video` (bytes):** o MP4 pronto, até `expira_em`.
  - **Retenção:** `TRAJETORIA_VIDEO_RETENCAO` (variável de ambiente
    `TRAJETORIA_VIDEO_RETENCAO_MINUTOS`), padrão de **2 h** (DP-2202). A limpeza apaga
    a linha inteira.
- **Justificativa:**
  - A chave deriva só do conteúdo. Duas Pessoas com composição idêntica receberiam o mesmo
    arquivo, que é exatamente o conteúdo que cada uma já pode gerar. Não há vazamento, e a
    linha fica sem dado de identificação além do próprio conteúdo temporário.
  - **Abuso limitado por construção:** uma Pessoa só produz duas composições (com e sem
    nome) por versão de template.
  - **MP4 no banco (~0,8 MB, poucas horas):**
    - dispensa diretório de mídia compartilhado entre web e worker, permissões e limpeza
      de arquivos órfãos;
    - funciona com várias instâncias;
    - a limpeza é um `DELETE`.
  - A `chave` nunca aparece em URL, HTML nem log. Ela é um hash de conteúdo de baixa
    entropia (nome e cursos) e seria reversível por força bruta.
- **Alternativas descartadas:**
  - **FK para Pessoa:** vincula o derivado à identidade sem necessidade.
  - **MP4 em disco:** exige diretório compartilhado e varredura de órfãos.
  - **Histórico por Pessoa:** vedado (FR-028).

## R7 — Processador: `manage.py processar_videos`

- **Decisão:**
  - **Modos:** laço com espera de 1 s entre ciclos vazios; `--uma-vez` para testes e cron.
  - **Ciclo:**
    1. Apaga linhas vencidas (`expira_em < agora`).
    2. Marca como `FALHOU` (`tempo_esgotado`) pedidos em `PROCESSANDO` há mais que
       `max(5 min, TRAJETORIA_VIDEO_TEMPO_MAXIMO + 1 min)` (worker morto no meio).
    3. Toma o `SOLICITADO` mais antigo com `select_for_update(skip_locked=True)`, passa a
       `PROCESSANDO` e confirma.
    4. Renderiza.
    5. Grava `PRONTO`, com o vídeo e `expira_em`, ou `FALHOU`, com o motivo. Nos dois casos
       apaga a `composicao`.
  - **Um render por vez por processo.** `skip_locked` permite mais de um processo sem
    disputa, mas a demonstração usa um.
  - **Sem processador:** a limpeza, chamada também pelas rotas, converte um `SOLICITADO`
    com mais de 10 min em `FALHOU(sem_processador)` e apaga a composição. A página nunca
    espera para sempre, e o nome não fica guardado sem prazo (revisão do analyze, P1).
  - **Gravação final condicionada** a `estado = PROCESSANDO` e ao `iniciado_em` lido.
    Resultado de linha reiniciada ou apagada durante o render é descartado (analyze U2).
- **Justificativa:** o menor processo que cumpre os quatro estados (FR-031) com reinício
  seguro.
- **Alternativas descartadas:**
  - **Disparar o processador a partir da view (`Popen`):** concorrência sem controle.
  - **`LISTEN/NOTIFY`:** otimização sem necessidade com espera de 1 s.

## R8 — Entrega do arquivo: `Range`, `inline`, sem cache

- **Decisão:**
  - `GET /minha-trajetoria/video.mp4?nome=1` recalcula a composição pela sessão, procura a
    `chave` e, com `PRONTO` não vencido, responde:
    - `video/mp4`;
    - `Content-Disposition: inline; filename="minha-trajetoria-ifes.mp4"`;
    - `Cache-Control: no-store`;
    - `Accept-Ranges: bytes`.
  - **Suporte mínimo a `Range`:** um único intervalo `bytes=a-b`, `bytes=a-` ou
    `bytes=-n` → `206` com `Content-Range`; inválido → `416`; sem cabeçalho → `200`.
  - Qualquer outra situação → `404`.
- **Justificativa:**
  - O Safari no iOS não reproduz `<video>` cujo servidor ignora `Range`: ele pede
    `bytes=0-1` antes de tocar.
  - O Django não trata `Range` nativamente, nem no `FileResponse`.
  - O MP4 tem menos de 1 MB e já está em memória.
  - Recalcular pela sessão impede servir o vídeo de outro conteúdo (FR-025).
- **Alternativas descartadas:**
  - **Sem `Range`:** quebra a prévia no iPhone.
  - **URL com a chave:** expõe o hash e cria link compartilhável.

## R9 — Página: seção do vídeo no capítulo "Seu card"

- **Decisão:**
  - Dentro do capítulo "Seu card" da 021 entra um bloco `#video`, só quando
    `renderizador.disponivel()` (FR-037). Detalhes em [rotas.md](contracts/rotas.md).
  - **Fluxo sem JavaScript** (FR-035):
    - `POST /minha-trajetoria/video/` (CSRF; `nome` igual ao da prévia) e `303` de volta
      para `/minha-trajetoria/?nome=1#video`;
    - o estado aparece a cada carregamento, com "Atualizar" quando em preparo.
  - **Melhoria progressiva** num script inline curto, como o da 021:
    - consulta `GET /minha-trajetoria/video/estado?nome=1` a cada 3 s enquanto em preparo
      e recarrega o bloco ao mudar;
    - "Compartilhar vídeo" com `navigator.canShare({files})`.
    - Sem `meta refresh`, que é atualização não controlada pelo usuário (WCAG 2.2.1).
  - **Prévia:**
    - `<video controls playsinline preload="metadata" poster="card.png?…">`, sem
      `autoplay`;
    - o pôster é o PNG do card, que é o próprio quadro final;
    - a descrição textual do card é a alternativa equivalente (`aria-describedby`);
    - o estado fica em região `aria-live="polite"`.
- **Alternativas descartadas:**
  - **Página separada para o vídeo:** fragmenta a devolutiva.
  - **Gerar ao abrir a página:** vedado pelo FR-002.

## R10 — Template `trajetoria-v1`: tempo e movimento

- **Decisão:** detalhes em [template-video.md](contracts/template-video.md).
  - **Janelas do storyboard:** 0–0,7 / 0,7–1,7 / 1,7–5,0 / 5,0–6,3 / 6,3–8,0 s.
  - **Duração:** 240 quadros com até 3 nós. Com 4 nós, a janela da linha do tempo ganha
    0,6 s (258 quadros = 8,6 s). O card exibe no máximo 4, então 8,6 s é o máximo. Fica
    abaixo dos 10 s do FR-010.
  - **Estáticos desde o quadro 0:** fundo, faixa inferior e rodapé institucional com a
    marca de demonstração (FR-015).
  - **A linha de apuração** entra com os destaques (achado do spike).
  - **Movimento:**
    - **Zonas de texto:** opacidade de 0 a 1 e translação de **+24 px a 0** (de baixo para
      cima), com *easing* `bezier(0.22, 1, 0.36, 1)`.
    - **Fechamento:** só opacidade, porque o rodapé, já visível, está logo abaixo.
    - **Imagem da abertura:** escala de 1,04 a 1,00, só na imagem. Texto não escala.
    - **Traço:** revelação de cima para baixo por recorte.
  - **Sem contador:** números estáticos (E7).
  - **Estabilidade:** o último movimento termina em 6,9 s (ou 7,5 s com 4 nós). O quadro
    final fica estável por pelo menos 1,1 s (FR-014).
- **Justificativa:**
  - A translação de baixo para cima só alcança a área da zona seguinte, que ainda está
    invisível. Por isso não há sobreposição de textos visíveis (FR-017). O rodapé é
    estático, e o fechamento não se move.
- **Alternativas descartadas:**
  - **Roteiro de tempo em JSON compartilhado com o Python:** abstração sem consumidor.
  - **Molas (`spring`):** pouco previsíveis para validar janelas.

## R11 — Formato de saída

- **Decisão:** em `renderizar.mjs`:
  - `codec: 'h264'`;
  - `pixelFormat: 'yuv420p'`;
  - `colorSpace: 'bt709'`;
  - `muted: true`, sem faixa de áudio;
  - qualidade padrão do Remotion (CRF 18);
  - `faststart` padrão.
- **Justificativa:**
  - É o perfil aceito por stories e players móveis.
  - A faixa limitada BT.709 evita cores lavadas ou estouradas em players que ignoram
    `yuvj`.
  - O arquivo tem ~0,8 MB.
- **Verificação:** `ffprobe` nos testes (R14).

## R12 — Ativos, fontes e navegador conhecidos de antemão

- **Decisão:**
  - **Fontes:** `bundle({publicDir: 'trajetoria/narrativa/fontes'})`. Os mesmos arquivos do
    PNG, sem cópia.
  - **Carregamento:** `FontFace` com `delayRender`/`continueRender`. O render só começa com
    as duas fontes carregadas.
  - **Ilustração e assinatura:** vão inline na marcação das partes (R2).
  - **Navegador:** provisionado na instalação por `npm --prefix video run garantir-navegador`
    (`remotion browser ensure` executado dentro de `video/`; da raiz, o Remotion gravaria em
    `./.remotion`, achado da implementação).
    - `renderizar.mjs` recusa renderizar (código 3) se o navegador não estiver presente,
      para nunca baixá-lo durante um render.
    - `TRAJETORIA_VIDEO_NAVEGADOR` permite apontar um executável do sistema.
  - **Disponibilidade** (`renderizador.disponivel()`, em cache por processo): executável
    `node`, `video/node_modules` e navegador provisionado.
- **Justificativa:** FR-008. Nada é buscado na rede durante o render.

## R13 — Determinismo

- **Decisão:**
  - O FR-018 é verificado em dois níveis:
    - **mesmo ambiente:** duas renderizações da mesma composição dão **o mesmo arquivo**
      (o spike mostrou bytes idênticos, inclusive com concorrência diferente);
    - **entre ambientes:** só tolerância visual (R14).
  - A spec não exige bytes iguais. O teste exige no mesmo ambiente porque o spike mostrou
    que é estável. Se o CI desmentir, o teste cai para comparação de quadros, e a mudança
    fica registrada.

## R14 — Estratégia de testes

**Ferramentas:**

- `ffprobe` e `ffmpeg` embutidos, chamados por `npx remotion ffprobe` e `npx remotion
  ffmpeg` dentro de `video/`;
- `renderizar.mjs --quadros` para os quadros-chave;
- `numpy` e `Pillow` como **dependências de desenvolvimento**, só para comparar imagens.

| Camada | O que verifica | Precisa do Node |
|---|---|---|
| Composição (puro) | Zonas e partes por caso; textos da composição = textos do card; conteúdo vedado (`VEDADAS`, FR-020); nome só com escolha; escape; determinismo do JSON e da chave; regressão do SVG do card (R3) | Não |
| Estado e processador | Transições; sem duplicata; retenção; travado → falha; sem processador → lido como falha; composição apagada; tentar de novo; logs sem dado pessoal | Não (renderizador falso) |
| Rotas | Sessão, elegibilidade, CSRF, nome; `Range` 200/206/416; `404` sem pronto; nome de arquivo; `no-store`; estado JSON; fluxo sem JS; isolamento (contagens de Participação e Resposta) | Não |
| Integração de mídia | **MP4 completo** de 3 casos (1, 2 e 4 nós): `ffprobe` (codec, perfil, `yuv420p`, BT.709, 1080 × 1920, 30/1, nenhuma faixa de áudio, duração 8,0 ou 8,6 s ± 1 quadro); bytes iguais em duas renderizações | Sim |
| Quadros-chave | Para todos os casos da matriz, PNGs em ~1 s, ~4 s, fronteiras das janelas e últimos 31 quadros | Sim |

**Critérios dos quadros-chave:**

- **último quadro × PNG do card:** SSIM ≥ 0,98 e no máximo 3% dos pixels com diferença
  > 32. O spike mediu 0,988–0,991 e 1,2–1,5%;
- **estabilidade:** último quadro − 30 igual ao último (diferença máxima ≤ 2 níveis);
- **rodapé:** região idêntica em todos os quadros amostrados, o que prova que nada o cobre
  nem o retira;
- **faixas fora da área segura:** a faixa inferior é idêntica em todos os quadros. Na
  superior, só a imagem varia: a máscara de texto da área segura não tem pixels de texto
  fora dela;
- **referências aprovadas** em ~1 s e ~4 s: SSIM ≥ 0,97. O limite é calibrado no CI na
  implementação e os valores medidos ficam registrados. As referências são geradas no
  ambiente do CI (Linux) e aprovadas pelo solicitante (SC-008).

**Sem o renderizador** (máquina sem `video/node_modules`): as camadas de mídia são
**puladas** com motivo explícito, como o teste do PNG. No CI elas rodam sempre: um teste
falha se `CI=true` e o renderizador estiver indisponível.

**Custo estimado no CI:** 3 MP4 + ~40 PNGs ≈ 40–90 s.

## R15 — CI

- **Decisão:** no job `testes`, o mesmo exigido pelo ruleset da `main`, antes do `pytest`:
  1. `actions/setup-node@v4` com Node 22 e cache npm por `video/package-lock.json`;
  2. `npm ci --prefix video`;
  3. `npm --prefix video run garantir-navegador`.
- **Bibliotecas do Chrome no Linux:** o runner `ubuntu-latest` já traz o Google Chrome e
  suas dependências. Se faltar alguma, um `apt-get install` com a lista da documentação do
  Remotion. Isso é verificado na primeira execução da implementação.
- **Impacto estimado:** +1 a 3 min por execução (instalação com cache e renders).
- **Alternativa descartada:** um job separado e não obrigatório. A falha do vídeo passaria
  despercebida no merge.

## R16 — Deploy e operação (não há produção hoje)

**Requisitos para um ambiente futuro**, registrados no ADR 0007:

- **Base:**
  - Node ≥ 22;
  - `npm ci` em `video/`;
  - `npm --prefix video run garantir-navegador` na construção da imagem ou VM;
  - as bibliotecas do Chrome Headless Shell (Debian/Ubuntu; **Alpine não é suportado**).
- **Disco:** ~600 MB para `node_modules` e navegador.
- **Processos:** o servidor web e **um** `processar_videos` (systemd, supervisor ou outro
  contêiner com o mesmo código).
- **CPU e memória:** cada render usa os núcleos disponíveis por alguns segundos e ~1 GB.
  - Recomendação inicial: concorrência 2 e um processador.
  - `TRAJETORIA_VIDEO_CONCORRENCIA` ajusta, se preciso.
- **Segurança:**
  - o Chrome só abre o bundle local;
  - nenhum conteúdo externo;
  - atualizar o Remotion é atualizar o Chrome. Revisão periódica com a DTI (DP-2201).
- **Desenvolvimento local:**
  - `npm ci` e `browser ensure` uma vez;
  - um terminal a mais para `processar_videos`.
  - Sem isso, a página funciona sem a opção de vídeo (FR-037).

## R17 — Alternativa C (Python/resvg) como fallback documentado

- **Decisão:** não implementada.
  - O spike da auditoria fica como evidência de que a `ComposicaoVisual` basta para outro
    renderizador: ~106 ms por quadro, um núcleo, sem codificação.
  - Se a DP-2201 vetar o Remotion, a troca afeta só `video/` e `renderizador.py`. A
    composição, o estado, as rotas e os testes de quadro se mantêm.

## R18 — Privacidade operacional

- **Logs:** só fatos técnicos (`video: falha na geração (tempo_esgotado)`), sem chave,
  nome, curso nem saída do Node (FR-027).
- **Dado pessoal persistido:**
  - a `composicao` só existe entre o pedido e o processamento;
  - o MP4 só existe até `expira_em`.
- **Arquivos temporários:** `TemporaryDirectory`, apagados mesmo em falha.
- **Ausências:** nenhuma telemetria. O Remotion só envia telemetria com Company License;
  na Free License, nada é configurado. Nenhum envio a terceiros.
