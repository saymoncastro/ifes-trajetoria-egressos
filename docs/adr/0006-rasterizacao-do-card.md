# ADR 0006 — Rasterização do card da Minha trajetória

Data: 2026-10-04. Estado: spike aprovado no macOS arm64. **A verificação no CI (ubuntu,
Python 3.13) fica pendente até o primeiro push do PR da 021.**

## Contexto

A Feature 021 entrega um card vertical 9:16 (1080 × 1920) para o story do Instagram e de
outras redes. As redes não aceitam SVG. O artefato compartilhável precisa ser um PNG
derivado do mesmo SVG que serve de representação-base (021 FR-031) e reprodutível
(FR-032). O projeto não tinha biblioteca de imagem nem fonte no servidor: a interface usa
`system-ui` e não serve estáticos (015 D-04).

## Decisão

- **Biblioteca:** `resvg-py` (`>=0.5,<0.6`, MIT), binding do resvg 0.48.1 escrito em
  Rust. As *wheels* abi3 cobrem manylinux, musllinux e macOS e não dependem de biblioteca
  de sistema. O `uv.lock` fixa a *wheel* `manylinux_2_17_x86_64`.
- **Isolamento:** o uso fica só em `trajetoria/narrativa/rasterizacao.py: png_de(svg)`,
  com `font_files` explícitos e `skip_system_fonts=True`. O mesmo SVG dá o mesmo PNG no
  mesmo ambiente.
- **Fontes:** Open Sans **Regular e Bold** (SIL OFL 1.1), com `OFL.txt`, versionadas em
  `trajetoria/narrativa/fontes/`.
  - Origem: `googlefonts/opensans`, commit `bd7e37632246368c60fdcbd374dbf9bad11969b6`,
    arquivos `fonts/ttf/OpenSans-Regular.ttf` e `fonts/ttf/OpenSans-Bold.ttf`.
  - SHA-256:
    - Regular: `c53aceea2dcf5b4098099c0c4d0a061d17e178a049317b42a422b1a9f7f8eb59`;
    - Bold: `27da758f4dcac9a65abe914c13b463b42982b9909bc65713424099f4810bd1e6`.
  - É a fonte que já compõe a assinatura do Ifes.
  - Não é servida ao navegador, por isso a D-04 não muda.
- **Medidas de texto:** as larguras de avanço dos glifos foram extraídas uma vez das duas
  fontes para `trajetoria/narrativa/metricas.py`. A quebra de linha mede o texto real e
  não estima por número de caracteres. `fontTools` foi usada só para gerar a tabela e não
  é dependência.

## Resultado do spike (macOS arm64, 2026-10-04)

| Verificação | Resultado |
|---|---|
| Assinatura PNG e IHDR 1080 × 1920 | OK |
| Duas rasterizações do mesmo SVG | Bytes idênticos |
| Acentos e "ç" (Regular e Bold) | Renderizados com Open Sans |
| Tempo por card 1080 × 1920 | 28 ms (SVG simples) a 59 ms (pior caso) |
| `tests/narrativa/test_png.py` | 6 testes verdes |

**Pendente:** os mesmos testes no CI. Se falharem lá, a 021 para no card e a alternativa
vai ao solicitante: o fallback SVG mantém a página, mas não atende ao story.

## Alternativas rejeitadas

- **cairosvg ou pyvips:** exigem Cairo ou libvips no sistema, e Cairo foi vetado pelo
  solicitante.
- **Pillow desenhando o PNG:** cria um segundo renderizador, divergente do SVG.
- **Canvas no navegador:** depende do dispositivo e exige JavaScript para gerar.
- **Chromium headless:** é a infraestrutura reservada à Feature 022 (vídeo).

## Riscos

O binding tem um mantenedor e está na versão 0.5.0. O risco fica contido pelo módulo
único e pelo intervalo de versão fixo. Trocar de rasterizador só altera `png_de`.
