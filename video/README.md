# video/ — renderizador do vídeo da Minha trajetória (Feature 022)

Projeto Node isolado que transforma a **composição visual do card** da 021 num MP4 vertical
de ~8 s, sem áudio. Ele **só anima**: não mede texto, não quebra linhas, não decide o que
aparece e não gera frase. Tudo isso vem pronto do Python
(`trajetoria/narrativa/composicao.py`).

- Contratos: [composição visual](../specs/022-minha-trajetoria-video/contracts/composicao-visual.md),
  [renderizador](../specs/022-minha-trajetoria-video/contracts/renderizador.md) e
  [template](../specs/022-minha-trajetoria-video/contracts/template-video.md).
- Decisão: [ADR 0007](../docs/adr/0007-renderizacao-do-video.md).

## Instalação (uma vez)

Requer Node ≥ 22. Ocupa ~600 MB com o navegador.

```bash
npm ci --prefix video
```

```bash
npm --prefix video run garantir-navegador
```

O navegador (Chrome Headless Shell) fica em `video/node_modules/.remotion/`. Ele é
provisionado **antes**: o `renderizar.mjs` recusa renderizar sem ele (código 3) e nunca o
baixa durante um render. Para usar um Chrome do sistema, defina
`TRAJETORIA_VIDEO_NAVEGADOR` com o caminho do executável.

Ao atualizar o Remotion, confira se esse caminho mudou: `renderizar.mjs` e
`trajetoria/video/renderizador.py` dependem dele.

## Uso

Só o Python chama este projeto, por `trajetoria/video/renderizador.py`.

```text
node renderizar.mjs <entrada.json> <saida.mp4>
node renderizar.mjs <entrada.json> <diretorio> --quadros 30,120,fim
```

| Código | Significado |
|---|---|
| 0 | Sucesso |
| 1 | Erro de renderização |
| 2 | Entrada inválida (JSON, versão do contrato ou template) |
| 3 | Navegador não provisionado |

Nenhum acesso à rede durante o render. As fontes vêm de `trajetoria/narrativa/fontes/`
(Open Sans, SIL OFL 1.1). A ilustração e a assinatura chegam inline na composição.

## Licença

O Remotion é *source-available*. A Free License cobre organizações *non-profit* ou
*not-for-profit*, segundo a documentação atual. O FFmpeg embutido usa `libx264` (GPL). O
aceite institucional dos dois é a **DP-2201**, antes de qualquer uso em produção. Hoje o
uso é só na demonstração.
