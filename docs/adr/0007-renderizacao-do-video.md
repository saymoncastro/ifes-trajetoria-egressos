# ADR 0007 — Renderização do vídeo da Minha trajetória

Data: 2026-10-05. Estado: **aceito**. Spike local aprovado (macOS arm64) e validação no CI
(ubuntu-latest, Node 22) aprovada no PR #33. O uso em produção continua dependendo da
DP-2201.

## Contexto

A Feature 022 entrega um MP4 vertical de ~8 s, sem áudio, que é o card da 021 em movimento.
O ADR 0006 reservou o Chromium headless para o vídeo. O solicitante escolheu o Remotion
animando a composição já produzida pela 021 (alternativa A da
[auditoria](../auditorias/2026-10-05-022-video-trajetoria.md)), sem segundo layout.

## Decisão

- **Motor:** Remotion **4.0.533 com versão exata**, React 19, Node ≥ 22, num projeto
  isolado em `video/`, com `package-lock.json` versionado.
- **Entrada:** a `ComposicaoVisual`, que é o card da 021 agrupado por zonas, com marcação
  SVG por parte. O template só anima.
- **Fronteira:**
  - Node: `video/renderizar.mjs`;
  - Python: `trajetoria/video/renderizador.py`, único módulo que chama o Node
    (`subprocess`, sem shell, tempo máximo e saída não logada).
- **Saída:** H.264, `yuv420p`, BT.709 de faixa limitada, 30 fps, 1080 × 1920, sem áudio,
  `faststart`.
- **Execução:** assíncrona, com estado técnico (`GeracaoDeVideo`) e um processador
  `manage.py processar_videos`. Sem broker.
- **Navegador:** Chrome Headless Shell provisionado na instalação
  (`npm --prefix video run garantir-navegador`), nunca baixado durante um render.
- **Fontes:** as mesmas do PNG (Open Sans, OFL), por `publicDir`.

## Resultado do spike (2026-10-05, Apple M5 Pro)

| Verificação | Resultado |
|---|---|
| Render de 240 quadros | 3,0–3,3 s (concorrência padrão); 8,8 s (concorrência 1) |
| Arquivo | H.264 High, 1080 × 1920, 30/1, 8,000 s, ~0,8 MB, sem áudio |
| Determinismo no mesmo ambiente | MP4 idêntico byte a byte em 3 renderizações |
| Quadro final × PNG do card | SSIM 0,988–0,991; diferenças só no antisserrilhado dos glifos |
| Disco | `node_modules` 225 MB + navegador 193 MB (~590 MB com caches) |
| Memória (processo Node) | ~0,9 GB |

**CI ubuntu-latest (PR #33, 2026-10-05):**

- Chrome Headless Shell de 91,9 MB, sem biblioteca de sistema extra;
- render de 10,7 a 11,5 s por vídeo (concorrência 2);
- último quadro × card com SSIM de 0,998;
- suíte completa com 2.789 aprovados, em 20 min de `pytest`.

## Consequências

- **Primeira dependência de runtime fora do Python.** O ambiente precisa de:
  - Node;
  - o navegador provisionado;
  - as bibliotecas do Chrome (Debian/Ubuntu; Alpine não é suportado);
  - um processo a mais (`processar_videos`).
- **CI:** o job `testes` ganha `setup-node`, `npm ci` e `garantir-navegador` (+1 a 3 min).
- **Sem o renderizador,** a página da 021 funciona igual, sem a opção de vídeo.
- **Atualizar o Remotion** é também atualizar o Chrome: revisão periódica pela DTI.
- **Licença:**
  - Remotion é *source-available*;
  - a Free License cobre organizações *non-profit/not-for-profit* segundo a documentação
    atual;
  - o aceite institucional, junto com o de codec H.264 (`libx264`, GPL, embutido), é a
    **DP-2201**, antes de qualquer produção.

## Alternativas rejeitadas

- **Python anima e rasteriza com resvg, FFmpeg codifica (alternativa C):** começaria um
  motor de animação próprio. Fica como fallback documentado. A troca só afetaria `video/` e
  `renderizador.py`.
- **Layout próprio em React (alternativa B):** dois layouts divergentes.
- **Renderização no navegador do egresso:** depende do dispositivo, exige JavaScript e não
  é determinística.
- **Remotion Lambda/serviço externo:** envio de dado pessoal a terceiro e custo.
- **Render síncrono na requisição:** tempo dependente do hardware (3 a 30 s estimados) e
  sem limite natural de concorrência.

## Riscos

- O Chromium no servidor é superfície de segurança.
  - **Mitigação:** só bundle local, sem rede, versão fixa e atualização deliberada.
- O consumo de CPU por render é relevante.
  - **Mitigação:** um processador, concorrência 2 e no máximo duas composições por Pessoa.
- Mudança de licença na versão 5.0 do Remotion.
  - **Mitigação:** versão 4 fixada e DP-2201.
