# Quickstart: validar a Feature 002

Guia para comprovar, de ponta a ponta, que a feature atende a spec. Pré-requisitos,
banco e variáveis são os mesmos da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos):
`uv`, PostgreSQL 16+ local e nenhuma variável obrigatória.

## Preparar

```bash
uv sync --extra dev
```

```bash
uv run python manage.py migrate
```

A migração cria as tabelas do app `instrumento`. Não há gatilhos no banco: a imutabilidade
é garantida pelas operações (research, R9).

Para confirmar que modelos e migrações estão sincronizados:

```bash
uv run python manage.py makemigrations --check --dry-run
```

## Validar

Suíte completa, incluindo a da Feature 001, que deve continuar passando sem alteração
(SC-006):

```bash
uv run pytest
```

Só esta feature:

```bash
uv run pytest tests/instrumento
```

Lint:

```bash
uv run ruff check .
```

| Arquivo de teste | O que comprova | Spec |
|------------------|----------------|------|
| `tests/instrumento/test_instrumento_modelo.py` | Restrições do [modelo](data-model.md) (CHECK, UNIQUE, `PROTECT`), por escrita direta no ORM | FR-034, FR-038, FR-047, FR-058 |
| `tests/instrumento/test_instrumento_estrutura.py` | Pesquisa, Versão, Seções, Perguntas, quatro tipos (tipo imutável), Opções, complemento textual, escala, ordem independente da criação, movimentação e remoção em rascunho | US1–US4, FR-001–FR-047, FR-061, FR-062, SC-005 |
| `tests/instrumento/test_instrumento_publicacao.py` | Publicação, completude com todas as pendências, `JA_PUBLICADA`, nenhuma volta a rascunho, rejeição de cada alteração em Versão, Seção, Pergunta e Opção publicadas e igualdade do conteúdo antes e depois | US5, FR-011–FR-018, FR-059, SC-002 |
| `tests/instrumento/test_instrumento_nova_versao.py` | Cópia profunda, identidades novas, referências traduzidas, origem intocada e registrada | US6, FR-019–FR-023, SC-003 |
| `tests/instrumento/test_instrumento_navegacao.py` | Regras, encaminhamentos, fluxo padrão, finalização e precedência de destino, verificados pelos percursos de Seções enumerados; nenhum atributo de momento de aplicação | US7, US8, FR-048–FR-055 |
| `tests/instrumento/test_instrumento_rejeicoes.py` | Cada `Motivo` do [contrato](contracts/operacoes.md#motivos-motivo) provocado ao menos uma vez, com elemento identificado e estado idêntico após a rejeição | US9, FR-058–FR-062, SC-004 |
| `tests/instrumento/test_instrumento_aceitacao.py` | Versão de demonstração cobrindo as características de "intenção" da tabela de cobertura; independência de Pessoa e Conclusão; exatamente 4 tipos e 2 estados | SC-001, SC-006, SC-007 |

Resultado esperado: todos os testes passam, sem acesso à rede e sem nenhuma Pessoa ou
Conclusão Acadêmica no banco.

## Ver o instrumento de demonstração

A Versão de demonstração é construída por um auxiliar de teste
(`tests/instrumento/construcao.py`), com textos fictícios e reduzidos. Ela **não** é o
Formulário Egresso do Ifes 2024, cuja representação é a Feature 003.

```bash
uv run python manage.py shell
```

No shell, importe o auxiliar, construa e publique a Versão de demonstração e leia
`conteudo_da_versao(versao)`. Verifique:

- as Seções em ordem, com a Seção de termos, as Seções de ramo com encaminhamento para a
  Seção comum e nenhuma Seção de "fim";
- a regra "Não → finalizar" na primeira Pergunta;
- uma pergunta de cada tipo, uma escala com rótulos e uma Opção com complemento textual;
- que uma tentativa de `alterar_opcao` na Versão publicada levanta `OperacaoRejeitada`
  com `VERSAO_PUBLICADA`, e que uma nova leitura é igual (`==`) à anterior.
