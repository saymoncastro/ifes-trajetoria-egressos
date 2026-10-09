# Protótipos da camada visual do Portal (ADR 0009, decisão 10)

Abra [`index.html`](index.html) no navegador: as três direções lado a lado, por tela e
largura, com os critérios da ADR 0009 medidos e o contraste dos tokens novos.

- `a-*`, `b-*`, `c-*`: Direção A (institucional), Direção B (trajetória) e combinação.
- `*-publico`, `*-inicio-ana`, `*-inicio-diego`: página pública e Início das personas
  fictícias (uma e três formações).
- `card-*.png`: cards gerados pelo código da 021, com a legenda da decisão 5.
- `instrumento-formacoes-diego.html`: retrato de `/formacoes/` na `main` `07b9cf9` (depois
  da 025), para a prancha da passagem do Portal para o instrumento.
- `capturas/`: 375, 1024 e 1440 px (página inteira) e primeiras telas a 375×812 e
  1280×720.

Protótipo, não produto: HTML estático, sem JavaScript, com os tokens da 015 e a camada do
Portal. Nada aqui é importado pela aplicação.

Para regerar, na raiz do repositório:

```bash
uv run python docs/prototipos/2026-10-09-portal/gerar.py
```

```bash
python3 docs/prototipos/2026-10-09-portal/medir.py
```

`medir.py` usa o Google Chrome instalado no macOS e o `sips`.
