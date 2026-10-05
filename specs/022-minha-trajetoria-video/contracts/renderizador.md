# Contrato: fronteira Python ↔ Node (renderizador de vídeo)

FR-038; research R4, R11, R12. Há um ponto de entrada de cada lado.

## Lado Node — `video/renderizar.mjs`

```text
node renderizar.mjs <entrada.json> <saida.mp4>
node renderizar.mjs <entrada.json> <diretorio> --quadros 30,120,fim
```

| Item | Regra |
|---|---|
| Entrada | Arquivo JSON no formato da [ComposicaoVisual](composicao-visual.md) |
| Composição Remotion | `trajetoria-v1`, a única registrada. `template` diferente → código 2 |
| Saída (vídeo) | MP4: H.264, `yuv420p`, BT.709 de faixa limitada, 30 fps, 1080 × 1920, sem faixa de áudio, `faststart`. Duração calculada pelo template ([template-video.md](template-video.md)) |
| Saída (`--quadros`) | `quadro-<n>.png` por quadro pedido. `fim` = último quadro. Só para testes e referências |
| Fontes | `publicDir` = `trajetoria/narrativa/fontes` (Open Sans Regular e Bold) |
| Bundle | Gerado uma vez por versão (hash de `src/`, `package-lock.json` e fontes) em `video/.bundle/`, com troca atômica; os renders seguintes o reaproveitam |
| Navegador | Provisionado antes (`npm --prefix video run garantir-navegador`) ou `TRAJETORIA_VIDEO_NAVEGADOR`. Ausente → código 3, sem tentar baixar |
| Concorrência | `TRAJETORIA_VIDEO_CONCORRENCIA` (padrão 2) |
| Rede | Nenhum acesso externo durante o render |
| `stdout`/`stderr` | Livres para diagnóstico local; **o Python não os loga** |

### Códigos de saída

| Código | Significado |
|---|---|
| 0 | Sucesso |
| 1 | Erro inesperado de renderização |
| 2 | Entrada inválida (JSON, versão do contrato ou template desconhecidos) |
| 3 | Navegador não provisionado |

## Lado Python — `trajetoria/video/renderizador.py`

| Função | Contrato |
|---|---|
| `disponivel() -> bool` | Em cache por processo. Verdadeiro se existem o executável `node`, `video/node_modules/remotion` e o navegador provisionado (R12) |
| `renderizar(composicao: dict) -> bytes` | Grava a entrada num `TemporaryDirectory`, chama `renderizar.mjs` com `subprocess.run` (lista de argumentos, sem shell, `cwd=video/`, ambiente mínimo, `timeout=TRAJETORIA_VIDEO_TEMPO_MAXIMO`) e devolve os bytes do MP4 |
| `quadros(composicao: dict, quadros) -> dict[str, bytes]` | Para testes e referências |
| `FalhaDeRenderizacao(motivo)` | Levantada em toda falha. `motivo` ∈ `indisponivel`, `tempo_esgotado`, `entrada_invalida`, `navegador_ausente`, `saida_invalida`, `codigo_<n>` |

**Garantias:**

- Nenhum outro módulo do projeto chama `node`, `npx` ou conhece opções do Remotion (teste
  de importação e busca textual).
- `saida_invalida` cobre arquivo ausente, vazio ou sem assinatura `ftyp`.
- O diretório temporário é apagado em qualquer caminho.
- Nenhum log contém conteúdo da composição, chave, `stdout` ou `stderr`.
