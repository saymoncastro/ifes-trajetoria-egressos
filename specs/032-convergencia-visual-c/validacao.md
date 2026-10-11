# Validação — Feature 032, convergência visual C

## PR 1 — fundação visual e página pública (2026-10-11)

### Verificações

- `ruff check .`, `manage.py check` e `makemigrations --check --dry-run` passam.
- Suíte completa: 3353 testes aprovados, 40 ignorados (vídeo sem renderizador) e 2
  desmarcados.
- Testes novos ou revisados:
  - `tests/portal/test_fontes.py` (10): cada fonte servida com tipo, cache longo e conteúdo
    igual ao arquivo; nomes fora da lista dão 404; licenças junto dos arquivos; nenhuma
    fonte externa nem `<link>`; o instrumento e `/acesso/` sem `@font-face`; sem o Portal, a
    rota não existe.
  - `tests/portal/test_pagina_publica.py` (8), revisado conforme 032 FR-005 e FR-006:
    - ordem da página e das cinco etapas da linha;
    - chamadas, âncoras e menu da página, sem link além de `/entrar/` e das âncoras;
    - exemplos coerentes com o card;
    - finalidade do e-mail e da contribuição;
    - vocabulário vedado;
    - nenhuma consulta;
    - decoração fora da acessibilidade;
    - textos retirados dos mockups.

### Medidas da página servida

Geradas por [`evidencias/medir.py`](evidencias/medir.py), com o arnês dos protótipos.
Capturas em [`evidencias/capturas/`](evidencias/capturas/) e medidas em
[`evidencias/medidas.json`](evidencias/medidas.json).

| Critério | Resultado |
|---|---|
| Sem rolagem horizontal, 320 a 1440 px, fonte a 100% e 200% | nenhuma |
| 375×812: título, frase e "Conhecer o Portal" sem rolar | a chamada termina em 590 px |
| 1280×720: título, frase, chamada e início da linha (descontada a faixa de 50 px) | a chamada termina em 610 px e a linha começa em 692 px |
| Um h1; alvos ≥ 44 px | sim; nenhum alvo abaixo |
| Contraste dos pares novos | de 4,8:1 a 11,3:1 no texto; números grandes em `#2f9e41` (3,45:1) só em 40 px |
| Peso das fontes | 61 KB (três woff2), cache de um ano |

O Início atual, que só muda de fonte neste PR, também foi medido: sem rolagem horizontal e
sem alvo abaixo de 44 px.

### Fidelidade aos mockups C

Seguem a composição C:
- abertura com o título grande e a linha Ingresso → Adiante, com o "Hoje" em vermelho;
- três passos;
- faixa escura "Ninguém se forma sozinho" com as memórias;
- a ponte "Você concluiu → Aparece para você";
- a faixa verde-clara da contribuição com as formas numeradas;
- o card com a chamada final e o fio.

Ajustes, todos da tabela da spec:
- **Textos e marca:** sem "continua", "Comunidade", "conexão", "turma" e o padrão da marca;
  o card é o real da 021; "Conhecer o Portal" no lugar de "Entrar no meu espaço".
- **Encontro de exemplo:** entrou na faixa escura, para manter os dois exemplos da 029 FR-009.
- **Menu no celular:** abaixo de 480 px, mostra só "Entrar".

### Pendências

- DP-3201 (Bricolage) e DP-3202 (padrões da marca) com a ACS; D2 e DP-801 (textos).
- PR 2: Início, "Participação" e navegação.
- Checkpoint 1: NÃO APLICADO.
