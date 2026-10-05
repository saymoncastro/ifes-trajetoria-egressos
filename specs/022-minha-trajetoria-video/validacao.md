# Validação — Feature 022 (Minha Trajetória em vídeo)

Registro das verificações da implementação. Dados sempre fictícios.

**Estado em 2026-10-05:**

- implementação concluída, validada localmente (macOS arm64) e **no CI Linux** (PR #33,
  mergeado);
- **referências regeneradas no Linux** (T039), pelo workflow `referencias-video.yml`;
- **pendentes:**
  - a aprovação humana das referências (T040);
  - o teste em celular real (T041).

## Porta de decisão (T019) — macOS arm64, Apple M5 Pro, Node 26.5

| Verificação | Resultado |
|---|---|
| Formato (`ffprobe`) | `h264`, `yuv420p`, `bt709`, 1080 × 1920, `30/1`, uma única faixa (sem áudio) |
| Duração | 240 quadros (8,000 s) com até 3 nós; 258 quadros (8,600 s) com 4 nós |
| Contêiner | `ftyp` no byte 4; `moov` antes de `mdat` (`faststart`) |
| Determinismo no mesmo ambiente | Duas renderizações de Maria com nome → bytes idênticos |
| Tempo por render (concorrência 2, com bundle e abertura do navegador) | Maria 10,7 s (primeiro, a frio), Ana 5,7 s, 4 nós 6,0 s. Todos abaixo de 60 s (SC-006) |
| Último quadro × PNG do card | Maria (com nome): SSIM 0,9894, 1,48% dos pixels com diferença > 32. Ana: SSIM 0,9908, 1,16%. 4 nós: SSIM 0,9910, 1,07%. Limite: ≥ 0,98 e ≤ 3% |
| Estabilidade do final | Quadros `fim − 30` e `fim` com diferença máxima ≤ 2 |
| Rodapé de demonstração | Região idêntica em todos os quadros amostrados, presente no quadro 0 |
| Texto em movimento | Nenhum pixel de texto fora da área segura nem sobre o rodapé nas fronteiras das janelas (Diego, 4 nós, pior caso, Ana com nome longo, Maria com nome) |
| Quadros de ~1 s e ~4 s × referências | SSIM 1,0000 no mesmo ambiente (8 comparações) |
| Disco | `video/node_modules` 225 MB + Chrome Headless Shell 193 MB |

### CI Linux — porta aprovada (T019)

**Job `testes` do PR #33** (run `37315845369`, ubuntu-latest, Python 3.13, Node 22.23.3):

| Passo | Resultado |
|---|---|
| `npm ci --prefix video` | 7 s (252 pacotes, cache do npm) |
| `garantir-navegador` | 4 s; Chrome Headless Shell `linux64` de 91,9 MB baixado na primeira execução. **Nenhuma biblioteca de sistema faltou** no runner |
| `pytest` (suíte completa) | **2.789 aprovados**, 11 pulados e 2 desmarcados, em 20 min 07 s. Os 11 pulados são os 3 de antes da 022 mais as 8 comparações com as referências do macOS (pulo removido nesta revisão; ver abaixo). Os testes de mídia **rodaram**: com `CI=true`, a ausência do renderizador seria falha |
| Job inteiro | ~21 min. Antes da 022, o job era dominado pelo `pytest` da suíte sem vídeo |

**Workflow `referencias-video.yml`** (run `37319654190`, mesmo runner):

| Verificação | Linux | macOS (local) |
|---|---|---|
| Render por vídeo (concorrência 2, com o navegador a frio) | 10,7–11,5 s | 5,1–10,7 s |
| Último quadro × PNG do card | SSIM **0,9978–0,9980**; 0,19–0,27% dos pixels com diferença > 32 | SSIM 0,9894–0,9910; 1,07–1,48% |
| Testes de mídia e de quadros | 29 aprovados em 1 min 40 s | — |

**Referências e plataforma (T039).** As 7 referências foram regeneradas no Linux e
versionadas (`referencias-plataforma.txt` = `Linux-x86_64`). Entre macOS e Linux, os
quadros de ~1 s, ~4 s e final dão SSIM de **0,991 a 0,997** (só antisserrilhado dos
glifos). Isso tem folga para o limite de 0,97, e o pulo por plataforma, uma cautela do code
review, foi removido. A comparação com as referências agora roda no CI e localmente: no
macOS, contra as do Linux, deu SSIM de 0,994 a 0,997.

## Achados da implementação

- **O navegador é gravado conforme o diretório atual.** `npx --prefix video remotion browser
  ensure`, rodado da raiz, gravou em `./.remotion`. O provisionamento passou a ser `npm
  --prefix video run garantir-navegador`, que roda dentro de `video/`. Quickstart, CI,
  research e ADR foram atualizados.
- **O caso `quatro` da 021 exibe 3 nós.** O quarto vira "e mais 1" pela regra do card. Para
  testar 4 nós e os 8,6 s, foi criado o caso `quatro_curtos` (quatro cursos de nome curto).
- **Conteúdo que não cabe nem no mínimo.** O `compor()` da 021 mantinha a abertura no mínimo
  e deixava o conteúdo transbordar em silêncio. `Composicao.cabe` expõe isso: o card não
  muda, e o vídeo recusa com `ComposicaoImpossivel` (FR-039).
- **O traço corria na frente dos nós.** A primeira versão revelava o traço numa única curva,
  do primeiro ao último nó, e ele chegava ao fim antes de os nós aparecerem. A composição
  passou a levar `paradas` (o centro de cada nó), e o traço desce trecho a trecho, chegando
  a cada nó quando ele entra (contracts/composicao-visual.md e template-video.md).
- **Render reduzido da máscara.** Remover as zonas de texto mudava a duração com 4 nós. O
  render reduzido mantém a contagem de partes com marcação vazia (T022).
- **Testes da 021 com o Node instalado.** Numa máquina com o renderizador, o bloco de vídeo
  aparece na página e muda o número de scripts. Uma fixture `autouse` em
  `tests/narrativa/conftest.py` deixa o renderizador indisponível nesses testes, que
  passaram a provar que, sem vídeo, a página é a da 021 (FR-037). O bloco tem testes
  próprios.
- **CSS:** a 021 proíbe `nowrap`. A classe `.visualmente-oculto` foi escrita sem ele.

## Correções do code review (2026-10-05)

- **Prazos derivados do tempo máximo.** Os prazos de travado e de vencimento dos estados
  intermediários passaram a derivar de `TRAJETORIA_VIDEO_TEMPO_MAXIMO`. Um render longo, ou
  uma retenção curta, deixou de ser dado como travado ou apagado por uma leitura
  concorrente.
- **Node pelo PATH.** `TRAJETORIA_VIDEO_NODE` aceita o nome do comando (`node`), resolvido
  pelo PATH.
- **Referências e plataforma.** As referências de quadros passaram a registrar a plataforma
  em que foram geradas (`evidencias/referencias-plataforma.txt`), e o teste era pulado em
  outra plataforma. *Revisto depois do CI:* a diferença medida entre macOS e Linux é pequena
  (SSIM ≥ 0,991), e o pulo foi removido (seção "CI Linux").
- **Zonas fora do card.** As zonas do card são calculadas só quando o vídeo pede: uma
  classe nova no card da 021 não o quebra, e só o vídeo recusa (`ComposicaoImpossivel`).
- **Menos trabalho por requisição.**
  - Limpeza nas leituras no máximo a cada 30 s por processo.
  - Composição montada só com o renderizador disponível.
  - `solicitar` sem carregar o vídeo do banco.
- **Bundle reaproveitado.** O bundle do Remotion é gerado uma vez por versão
  (`video/.bundle/`), não a cada render.
- **Compartilhar sob demanda.** O vídeo só é baixado quando o egresso toca em "Compartilhar
  vídeo".
- **CI.** Cache do Chrome Headless Shell, chaveado pelo `package-lock.json`.

## Quickstart de ponta a ponta (T044) — banco novo `trajetoria_demo_022`

Ambiente:

- `migrate` e `preparar_demonstracao`;
- pesquisa da Maria concluída pelo caminho da interface (auxiliares de teste da 008, via
  `Client`);
- `runserver` e `processar_videos` reais;
- navegador embutido do app (Chromium 152).

| # | Cenário | Resultado |
|---|---|---|
| 1 | Abrir a página | Bloco "Vídeo da sua trajetória" com "Gerar vídeo"; nenhuma linha criada |
| 2 | Gerar vídeo | `POST` → `303`; "Estamos preparando seu vídeo…" e "Atualizar" |
| 3 | Aguardar | O script consultou `/estado` a cada 3 s e recarregou sozinho em ~9 s. A prévia mostra o pôster do card, sem `autoplay`, com `controls` |
| 4 | Reproduzir | `duration` 8 s, 1080 × 1920; `play()` ok; H.264 suportado; o servidor respondeu `206` aos pedidos parciais |
| 5 | Baixar | `download="minha-trajetoria-ifes.mp4"` |
| 6 | Com nome | Segundo vídeo (`?nome=1`), com pôster e arquivo da escolha. O último quadro é o card com "Maria Exemplo" |
| 7 | Mesma escolha de novo | Coberto por teste (`test_sem_duplicata`, `test_estado.py`) |
| 8 | Sem processador | Coberto por teste (`test_sem_processador_vira_falha`) |
| 9 | Sem JavaScript | Coberto por teste (`test_fluxo_sem_javascript`) |
| 10 | Sem `video/node_modules` | Coberto por teste (`test_sem_renderizador_a_pagina_e_a_da_021`) |
| 11 | Celular real e story | **Pendente** (T041) |
| 12 | 320 px e teclado | Sem rolagem horizontal (`scrollWidth` 320); vídeo com 254 px; vídeo e "Baixar vídeo" focáveis. O "Compartilhar vídeo" fica oculto neste navegador, que não compartilha arquivos. Falta o leitor de tela no celular (T041) |

**Banco técnico depois do roteiro:** duas linhas `PRONTO` (com e sem nome), ambas com
`composicao` nula, ~0,73 MB cada e retenção de 2 h. Nenhuma linha de log com nome, curso ou
CPF (`servidor.log`, `processador.log`).

## Verificações finais

- `uv run ruff check .`: sem erros.
- `uv run python manage.py check`: sem problemas.
- `uv run python manage.py makemigrations --check --dry-run`: sem mudanças.
- `uv run pytest` (suíte completa, com o renderizador): **2.797 aprovados**, 3 pulados (os
  mesmos de antes da 022) e 2 desmarcados (marcador `volume`), em 4 min 58 s, depois das
  correções do code review.
  - Testes novos da 022: 164 em `tests/video/`, 58 em `tests/narrativa/test_card_zonas.py` e
    7 em `tests/narrativa/test_fronteiras.py`.

## Aprovação humana (T040) — pendente (referências do Linux)

Referências para revisão em `evidencias/`. Para cada caso: `referencia-<caso>.mp4`, os
quadros `-q30`, `-q120` e `-qfim` e uma folha de contato com 9 instantes (`-folha.png`).
Casos:

- Maria sem nome;
- Maria com nome;
- Ana;
- Diego;
- 4 formações;
- pior caso;
- unidade sem imagem própria.
