# Quickstart: validar a Feature 012

Este guia mostra que o snapshot analítico atende a spec. Pré-requisitos e banco são os da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos).

> **Núcleo de domínio, sem interface.**
>
> - Não há tela, rota, endpoint nem management command: a captura e a leitura são
>   exercitadas por testes automatizados com dados fictícios (research R14, R15).
> - O cenário de demonstração **não muda** (spec FR-131).
> - Somente dados fictícios (001/DP-009; 005/DP-504).

## Preparar

```bash
uv sync --extra dev
```

```bash
uv run python manage.py migrate
```

Esperado: aplica `analitico.0001_initial`, a única migration nova, aditiva.

```bash
uv run python manage.py makemigrations --check --dry-run
```

Esperado: `No changes detected`.

## Validar

```bash
uv run pytest tests/analitico
```

Cada cenário abaixo corresponde a testes em `tests/analitico/` ([plan](plan.md#estratégia-de-testes)).

| # | Cenário | Esperado |
|---|---------|----------|
| 1 | Campanha aberta e encerrada; captura | Snapshot com `capturado_em` entre o antes e o depois da chamada; um registro por Conclusão do universo |
| 2 | Campanha EM COLETA | `SnapshotRecusado(COLETA_NAO_ENCERRADA)`; nenhum snapshot |
| 3 | Campanha nunca aberta, inclusive com período expirado | `SnapshotRecusado(CAMPANHA_NUNCA_ABERTA)`; nenhum snapshot |
| 4 | Falha simulada durante a gravação dos registros ou na verificação final | Nenhum snapshot e nenhum registro órfão |
| 5 | Elegíveis sem Participação, Participação elegível, Participação de Conclusão que deixou de satisfazer os critérios (alteração simulada no teste) | Registros elegível / elegível / não elegível; denominador = população da 004 |
| 6 | Atributo ausente; cursos homônimos na Serra e em Vitória | `None` preservado; duas linhas no recorte por curso |
| 7 | Captura, depois alteração direta das Conclusões e incorporação de novas | Registros, indicadores e seis recortes idênticos aos de antes |
| 8 | Segunda captura depois da alteração | Snapshot B reflete o novo estado; A permanece idêntico; ambos listados |
| 9 | Duas capturas simultâneas | Dois snapshots completos e independentes |
| 10 | Indicadores e recortes logo após a captura | Iguais aos da 011 em escopo institucional |
| 11 | Dataset | Concluída, concluída por Q1 = "Não", rascunho com Respostas fora do percurso e sem Participação, distinguíveis |
| 12 | Fronteiras | Campos exatos dos dois modelos; nenhuma PII; nenhuma tabela da 001 nem de Resposta no SQL da reprodução |

## Não regressão

```bash
uv run pytest
```

Esperado: toda a suíte passa, inclusive `tests/acompanhamento` (011), sem alteração.

## Leitura do snapshot

Para quem for consumir a fronteira (Feature 013): [contracts/consultas.md](contracts/consultas.md).
Toda leitura recebe o snapshot explicitamente; não existe "snapshot atual" (DP-1201).
