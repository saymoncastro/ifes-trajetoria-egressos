# Contrato: `ComposicaoVisual` serializada (versão 1)

Entrada única do template de vídeo e base da chave técnica. É a **projeção mecânica** da
composição do card da 021 (FR-004 a FR-007; research R2, R3). Produzida por
`trajetoria/narrativa/composicao.py: composicao_visual(compartilhavel, nome, demonstracao)`.

## Garantias

- **Mesma fonte do PNG:**
  - os elementos, posições, textos, quebras e decisões de corte são os de
    `card.compor()`;
  - o último quadro do vídeo e o card são duas renderizações da mesma composição.
- **Sem regra no consumidor:** o template não mede, quebra, corta, formata nem gera texto.
  Ele só decide **quando** e **como** cada parte entra.
- **Determinismo:** mesma narrativa, mesma escolha de nome e mesma versão do template → mesmo
  JSON canônico → mesma chave.
- **Escape:**
  - texto e atributos chegam escapados pelo template Django do card;
  - a marcação de ativos (`interior`: ilustração, assinatura) é versionada no repositório.
- **Ausência:** zona ausente é omitida. Não existe zona vazia nem chave `null`.
- **Privacidade:** só o conteúdo do card. Nenhum identificador, Resposta, dado declarado,
  forma de oferta, data completa, tempo decorrido ou ingresso.

## Forma

```json
{
  "versao_contrato": 1,
  "template": "trajetoria-v1",
  "largura": 1080,
  "altura": 1920,
  "area_segura": [90, 270, 990, 1650],
  "zonas": [
    {"chave": "fundo",      "partes": ["<rect class=\"fundo\" …/>…"]},
    {"chave": "abertura",   "partes": ["<svg class=\"abertura\" …>…</svg><path class=\"onda\" …/>"]},
    {"chave": "marca",      "partes": ["…"]},
    {"chave": "legenda",    "partes": ["…"]},
    {"chave": "titulo",     "partes": ["<text class=\"titulo\" …>Minha trajetória</text>…"]},
    {"chave": "nome",       "partes": ["<text class=\"nome\" …>Maria Exemplo</text>"]},
    {"chave": "traco",      "partes": ["<line class=\"traco\" …/>"], "y1": 742, "y2": 972,
                            "paradas": [742, 972]},
    {"chave": "nos",        "partes": ["…nó 1…", "…nó 2…"]},
    {"chave": "mais",       "partes": ["<text class=\"mais\" …>e mais 4 formações registradas</text>"]},
    {"chave": "destaques",  "partes": ["…cartão 1…", "…cartão 2…"]},
    {"chave": "apuracao",   "partes": ["<text class=\"apuracao\" …>Dados institucionais apurados em 31/01/2026.</text>"]},
    {"chave": "fechamento", "partes": ["…"]},
    {"chave": "rodape",     "partes": ["…Instituto Federal do Espírito Santo · Demonstração — dados fictícios…"]}
  ]
}
```

## Campos

| Campo | Regra |
|---|---|
| `versao_contrato` | `1`. Mudar significado ou remover campo → `2` |
| `template` | `"trajetoria-v1"`. O renderizador recusa um template que não conhece (código 2) |
| `largura`, `altura` | 1080 × 1920, as do card |
| `area_segura` | A da 021 (FR-072), informativa para os testes de quadro |
| `zonas[]` | Ordem fixa de pintura (data-model §1.4); só as presentes |
| `zonas[].partes[]` | Marcação SVG de cada parte, sem o invólucro `<svg>` |
| `zonas[].y1`, `y2`, `paradas` | Só em `traco`: extremos do traço e o centro (`cy`) de cada nó, na ordem, para o traço chegar a cada nó quando ele entra. Valores copiados da composição do card |

## Evolução

- Zona nova opcional mantém a versão 1, e o template antigo a ignora.
- Novo template = novo valor em `template` = nova chave. Os vídeos anteriores nunca são
  reaproveitados (FR-019).
