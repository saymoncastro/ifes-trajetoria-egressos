# Data Model: Foundations e validação da identidade visual da jornada do egresso

## Entidades persistidas

**Nenhuma entidade, campo, tabela ou migração nova** (FR-037; SC-013). Nada é gravado
por esta feature. As entidades existentes só são apresentadas, sem mudança de conteúdo:

| Entidade | Onde aparece | Mudança |
|---|---|---|
| Conclusão Acadêmica (001) | Trajetória, contexto compacto, ficha da formação | Só apresentação (voz institucional; destaque da linha na frase de entrada) |
| Versão da Pesquisa (002) | Títulos, textos e Perguntas das Seções | Só apresentação (ritmo, tipografia, estados) |
| Participação em Pesquisa (005/006) | Pendência, erro, salvamento, conclusão | Só apresentação (variantes de feedback) |

## Origem dos dados

Nenhum dado novo é lido, derivado ou coletado. O único valor novo transmitido ao template
é a **variante visual do aviso**, derivada de forma fixa do código de aviso já existente
(lista fechada em `mensagens.py`):

| Código de aviso (existente) | Variante visual (nova, derivada) |
|---|---|
| `salvo` | `sucesso` |
| `saida` | `informacao` |
| `situacao` | `informacao` |
| `percurso` | `informacao` |

## Modelo visual (não persistido)

Os "dados" desta feature são os **tokens** — ver [contracts/tokens.md](contracts/tokens.md).
Relações relevantes:

- **Papel → token**: cada papel de cor da spec (FR-002) mapeia para exatamente um token.
- **Direção → tokens**: a Direção (A ou B) determina só `--cor-acao` e
  `--cor-acao-forte`; nenhum outro token depende dela.
- **Componente → tokens**: [contracts/telas.md](contracts/telas.md) e
  [contracts/shell.md](contracts/shell.md).
