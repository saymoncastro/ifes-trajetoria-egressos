# Fontes do Portal (Feature 032; ADR 0009, revisão de 2026-10-11)

Servidas pela própria aplicação em `/fontes/<arquivo>` (`portal.views.fonte`), só com o Portal
ligado. Nenhuma requisição a terceiros.

| Arquivo | Família | Origem | Licença |
|---|---|---|---|
| `atkinson-hyperlegible-regular.woff2`, `atkinson-hyperlegible-bold.woff2` | Atkinson Hyperlegible (Braille Institute of America) | `google/fonts`, `ofl/atkinsonhyperlegible` | SIL OFL 1.1 (`OFL-atkinson-hyperlegible.txt`) |
| `bricolage-grotesque-600-700.woff2` | Bricolage Grotesque (The Bricolage Grotesque Project Authors) | `google/fonts`, `ofl/bricolagegrotesque` | SIL OFL 1.1 (`OFL-bricolage-grotesque.txt`) |

Baixadas em 2026-10-11. As licenças não declaram nome de fonte reservado. Versões modificadas
só por subconjunto de caracteres e, na Bricolage, por instância dos eixos:

- caracteres: U+0000-00FF, U+0131, U+0152-0153, U+02C6, U+02DA, U+02DC, U+2013-2014,
  U+2018-201A, U+201C-201E, U+2022, U+2026, U+2032-2033, U+20AC, U+2122, U+2190-2193, U+2212;
- Bricolage: `fonttools varLib.instancer … wdth=100 opsz=72 wght=600:700`;
- todas: `pyftsubset --flavor=woff2`, com `kern`, `liga` e `locl`.

A Bricolage é provisória (DP-3201, ACS). Alternativa: Open Sans.
