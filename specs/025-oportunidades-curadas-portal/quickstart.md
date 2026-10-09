# Quickstart — validação da Feature 025

> **Só depois da implementação, que ainda não está autorizada** (roadmap, Revisão 4). Este
> guia valida a feature ponta a ponta quando ela existir. O ponto de partida continua sendo o
> [ambiente local](../../docs/desenvolvimento/ambiente-local.md), seguido literalmente.

## 1. Preparar

O banco precisa ser exclusivo ou recriado: o catálogo depende da data `D` do preparo.

```bash
source .env && dropdb --force "$PGDATABASE" && createdb "$PGDATABASE" && uv run python manage.py migrate && uv run python manage.py preparar_demonstracao
```

Esperado: a saída de sempre. O catálogo fictício de
[contracts/pertinencia.md](contracts/pertinencia.md) é carregado pelo sinal do cenário.

```bash
source .env && uv run python manage.py runserver 127.0.0.1:8000
```

## 2. Egresso (navegador a 375×812)

| # | Ação | Esperado |
|---|---|---|
| 1 | Raiz → Ana (painel) | Início com o bloco "Oportunidades": destaque O2, explicação com TADS (Serra, 2022), "Ver as 2 oportunidades". Depois, o convite |
| 2 | "Oportunidades" na navegação | "Pela sua formação": O2. "Para todos os egressos": O1. Cada item com categoria, resumo, explicação, origem e domínio "site externo: oportunidades.example" |
| 3 | Sair → Maria | Grupo formação: O2, depois O3. **O5 não aparece** |
| 4 | Sair → Diego | O6, depois O3. Destaque no Início: O6 |
| 5 | Sair → Fernanda | Só O1, em "Para todos os egressos" |
| 6 | Em qualquer persona | O7 (Agendada), O8 (Encerrada), O9 (Retirada) e O10 (Rascunho) nunca aparecem |
| 7 | Medidas | Nenhuma rolagem horizontal de 320 a 1280 px, com fonte de 100% a 200%. Navegação com a mesma altura em todas as telas com navegação, a 375 px. Convite do Início ≤ 270 px abaixo da posição sem o bloco. `h1` e síntese acima da dobra |

A tabela completa de resultados por persona é o oráculo em
[contracts/pertinencia.md](contracts/pertinencia.md) (SC-002).

## 3. Operador

| # | Ação | Esperado |
|---|---|---|
| 1 | `/curadoria/oportunidades/` sem operador | Escolha de operador. Depois de escolher B, volta à curadoria |
| 2 | Operador B (CSAEG Vitória) | Lista só com O3, O4, O9 e O10 (unidade Vitória) |
| 3 | B: nova oportunidade com unidade Vitória, sem público, endereço `https://oportunidades.example/x` | Rascunho. Publicar mostra a prévia, "todos os egressos do Ifes" e o aviso de site externo. Depois, Ana a vê em "Para todos" |
| 4 | B tenta a unidade Serra | A opção não aparece. Um POST forjado é recusado com erro de campo |
| 5 | B tenta `http://…`, `https://user:pw@…` ou `https://10.0.0.1/` | Erros de campo; nada gravado |
| 6 | B retira O4 | Bruno deixa de vê-la na hora |
| 7 | Operador A (CPAEG) | Vê todas e usa "Ifes (institucional)" |
| 8 | Operador C (sem vínculo) | Recusa 403 |

## 4. Fronteiras

```bash
uv run pytest tests/portal
```

Esperado: os 12 casos do FR-043 e a revisão da 024 passam.

```bash
uv run pytest tests/portal/test_desabilitado.py
```

Esperado: `/oportunidades/` e `/curadoria/…` dão 404 e o caminho do convite não muda.

## 5. CI

```bash
uv run ruff check .
```

```bash
uv run python manage.py check
```

```bash
uv run python manage.py makemigrations --check --dry-run
```

Esperado: "No changes detected", com a migração `portal/0001` versionada.

```bash
uv run pytest
```
