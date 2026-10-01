# Quickstart: validar a Feature 004

Guia para comprovar, de ponta a ponta, que a feature atende a spec. Pré-requisitos, banco
e variáveis são os mesmos da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos):
`uv`, PostgreSQL 16+ local e nenhuma variável obrigatória.

## Preparar

```bash
uv sync --extra dev
```

```bash
uv run python manage.py migrate
```

A migração cria só a tabela do app `campanha`. Nenhuma tabela das Features 001 e 002 é
alterada. Não há gatilhos nem tarefas agendadas (research R5, R10).

```bash
uv run python manage.py makemigrations --check --dry-run
```

## Validar

Suíte completa, incluindo 001, 002 e 003, que devem continuar passando sem alteração:

```bash
uv run pytest
```

Só esta feature:

```bash
uv run pytest tests/campanha
```

```bash
uv run ruff check .
```

| Arquivo de teste | O que comprova | Spec |
|------------------|----------------|------|
| `tests/campanha/test_campanha_modelo.py` | CHECKs do [modelo](data-model.md) por escrita direta no ORM: período inteiro e ordenado, anos ordenados, conjunto vazio ou com cadeia vazia rejeitado, encerrada exige aberta, `PROTECT` na Versão | FR-012, FR-023 |
| `tests/campanha/test_campanha_preparacao.py` | Criação com Versão em qualquer estado; mesma Versão em duas Campanhas; troca de Versão; Pesquisa derivada; período válido, de um dia, incompleto e invertido; critérios definidos e substituídos; todas as pendências numa rejeição; sem período padrão | US1, US2, FR-001–FR-014, FR-023, FR-024 |
| `tests/campanha/test_campanha_elegibilidade.py` | Contagem igual ao total sem critérios e coerência QuerySet ⇔ `avaliar` em todas as Campanhas de referência; população ampla; intervalo de anos; só mínimo; só máximo; unidade; várias unidades; nível; modalidade; forma de oferta; combinações; Pessoa com duas Conclusões e só uma elegível; atributo ausente → `NAO_INFORMADO`; fora do critério → `NAO_ATENDE`; todas as pendências na ordem; igualdade exata sem normalização; resultado igual em qualquer estado e data; nada gravado | US3, US4, US5, US7, US11, FR-015–FR-030 |
| `tests/campanha/test_campanha_ciclo.py` | Estados com precedência temporal, inclusive nunca aberta e expirada; separação entre estado temporal e imutabilidade (nunca aberta e expirada continua editável e removível); abertura rejeitada com Versão RASCUNHO (inclusive a baseline da 003, que continua RASCUNHO); aceita com Versão PUBLICADA; rejeitada antes do início e depois do fim; aceita no primeiro e no último dia; todas as pendências; `JA_EM_COLETA`, `JA_ENCERRADA`; encerramento antecipado com momento registrado; ENCERRADA no dia seguinte ao fim sem nenhuma escrita; encerrar em preparação rejeitado; nenhuma Versão muda de estado | US6, US8, FR-034–FR-042, SC-006 |
| `tests/campanha/test_campanha_imutabilidade.py` | Casos M-A a M-F de estado × imutabilidade. Em EM_COLETA e em ENCERRADA após abertura, alterar nome, trocar Versão, alterar período, alterar critérios e remover são rejeitados, com a linha idêntica antes e depois; remoção de Campanha nunca aberta aceita, inclusive expirada | US9, FR-043–FR-047, SC-005 |
| `tests/campanha/test_campanha_longitudinal.py` | População dinâmica: Conclusão incorporada durante a coleta entra na população e na contagem, sem nada gravado na Campanha; mesma Conclusão elegível em Campanhas 2025, 2027 e 2030; duas Campanhas sobrepostas devolvidas sem prioridade; consulta vazia sem erro; `admite_participacao` sem qualquer convite; ENCERRADA e EM_PREPARACAO não admitem | US10, FR-048–FR-054 |
| `tests/campanha/test_campanha_aceitacao.py` | Casos A–L ponta a ponta; exatamente um modelo novo; nenhum modelo de Participação, Resposta, Convite, Destinatário, Segmento, Regra ou Agendamento; nenhuma coluna nova em `Versao` ou `ConclusaoAcademica` | SC-001, SC-009 |

Resultado esperado: todos os testes passam, sem rede e sem depender do relógio real.
Toda operação ou consulta temporal recebe `agora` explícito nos testes.

## Ver uma Campanha no shell

```bash
uv run python manage.py shell
```

No shell:

1. Incorpore os cenários da fonte simulada com `incorporar_pessoa`.
2. Construa uma Versão publicada mínima com `versao_publicada()` de
   `tests/campanha/construcao.py` (instrumento de teste publicado pelas operações da 002).
3. Crie uma Campanha com essa Versão, período de 01/04/2027 a 30/06/2027 e anos de 2020 a
   2024.

Verifique, passando `agora` explícito:

- `estado(...)` é `EM_PREPARACAO` antes de `abrir`. `abrir` com `agora` em 15/03/2027
  levanta `FORA_DO_PERIODO`; com `agora` em 01/04/2027, devolve `ABERTA`.
- `avaliar` da Conclusão Serra 2022 da Pessoa C é `ELEGIVEL`. A de Cefor 2025 é
  `NAO_ELEGIVEL`, com `(ANO_CONCLUSAO, NAO_ATENDE)`.
- `populacao_no_momento(campanha).count()` muda depois de incorporar uma nova Pessoa com
  conclusão em 2021, sem nenhuma ação sobre a Campanha.
- `estado(...)` com `agora` em 01/07/2027 é `ENCERRADA`, e a linha da Campanha não mudou.
- `definir_criterios` na Campanha aberta levanta `CAMPANHA_JA_ABERTA`, mesmo depois de
  encerrada.
- Outra Campanha, criada e nunca aberta, com o mesmo período: `estado(...)` em 01/07/2027
  também é `ENCERRADA`, mas `definir_periodo` para junho de 2028 é aceito e o estado
  volta a `EM_PREPARACAO` (não é reabertura).
