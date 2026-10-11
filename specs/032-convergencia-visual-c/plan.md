# Implementation Plan: Convergência visual C

**Branch**: `claude/032-convergencia-visual` (PR 1) | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

## Summary

Apresentação e navegação, sem modelo nem regra nova. PR 1: fontes locais, tokens e escala
do Portal, e a página pública na composição C. PR 2: Início na composição C, página
`/participacao/` e navegação com "Participação".

## Decisões técnicas

| # | Decisão | Por quê |
|---|---|---|
| R1 | Fontes em `trajetoria/portal/fontes/` (woff2 + OFL), servidas pela view `portal.views.fonte` em `/fontes/<nome>`, lista fechada, `Cache-Control: public, max-age=31536000, immutable` | O projeto não tem `staticfiles` nem `location /static/` no Nginx (implantação, seção 12); a mesma solução das imagens do card: a aplicação serve |
| R2 | Subconjunto latino em woff2, feito com `fonttools` fora do projeto (sem dependência nova); Bricolage instanciada em largura 100, tamanho óptico 72, peso 600 a 700 | 61 KB no total; nenhuma requisição externa |
| R3 | `@font-face` e tokens novos em `portal/visual.css`, que só as telas do Portal incluem | O shell da 015 e o instrumento não mudam (FR-002) |
| R4 | Página pública reescrita em `portal/publico.html` + `portal/publico.css`; dados de exemplo continuam em `portal/exemplo.py` | Mesma fronteira da 029 |
| R5 | Menu da página pública no bloco `navegacao` do template do Portal, como âncoras | O cabeçalho do núcleo não muda nem menciona o Portal |
| R6 | Linha da trajetória como `<ol>`; horizontal a partir de 768 px, vertical abaixo; marcador do "Hoje" com o vermelho e o rótulo | Ordem de leitura igual à visual; nada só por cor |
| R7 | PR 2: Início reorganizado em `inicio.py`/`inicio.html` com as consultas existentes (`itens_da_pessoa`, `situacao_de_entrada`, `da_pessoa`); encontro = primeiro item pertinente da categoria Eventos | Nenhuma inferência nova (FR-012) |
| R8 | PR 2: `/participacao/` reaproveita o mesmo trecho de template do Início | Uma fonte de verdade para os blocos |

## Constitution Check

Sem mudança de dado, regra, consentimento ou finalidade (XVI, XVII); acessibilidade e celular
como referência medidos (XX, XXI); escopo mínimo, só apresentação (XXII); spec antes do código
(XXVIII); pendências da ACS registradas (XXIX). Nenhuma dependência nova (`tests/dependencias.py`
intacto). **Aprovado.**

## Testes

- Fontes: rota só com o Portal ligado, lista fechada (404 fora dela), tipo e cache; shell da
  015 sem `@font-face`.
- Página pública: ordem, chamadas, âncoras, selos, nenhuma consulta, vocabulário e ajustes da
  spec; testes da 029 revisados onde a ordem e as chamadas mudam.
- Início (PR 2): ordem, estados vazios por bloco, "Hoje"/"Adiante", sem leitura de contato,
  navegação e `/participacao/`; testes da 024, 025 e 026 revisados com nota.
- Medidas no navegador (arnês da 029) e capturas reais a 375, 1024 e 1440 px.

## Riscos

- **Títulos grandes a 200%**: quebra de palavra (`overflow-wrap`) para não alargar a página.
- **Bricolage não aprovada pela ACS**: trocar por Open Sans só no `@font-face` (DP-3201).
- **Muitos testes da 024 presos à marcação**: revisados com nota, sem afrouxar o que verificam.
