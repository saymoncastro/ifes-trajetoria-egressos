# Quickstart: validar a Feature 013

Este guia mostra que a exportação atende a spec. Pré-requisitos e banco são os da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos).

> **Núcleo de domínio, sem interface.**
>
> - Não há tela, rota, endpoint nem management command. As exportações são exercitadas por
>   testes automatizados com dados fictícios (research R16, R17).
> - O cenário de demonstração **não muda** (spec FR-141).
> - Somente dados fictícios e chave fictícia (001/DP-009; 005/DP-504; DP-1301).

## Preparar

```bash
uv sync --extra dev
```

Esperado: instala `XlsxWriter` (produção) e `openpyxl` (desenvolvimento), as únicas
dependências novas (research R11).

```bash
uv run python manage.py makemigrations --check --dry-run
```

Esperado: `No changes detected`. A feature não tem modelo nem migration (spec FR-130).

## Rodar a verificação da feature

```bash
uv run pytest tests/exportacao
```

Esperado: todos os testes passam. Eles cobrem os casos A a V da spec, com a chave fictícia
definida por fixture.

```bash
uv run pytest tests/analitico
```

Esperado: a suíte da 012 continua passando, inclusive os testes novos de
`perguntas_do_percurso` e do parâmetro `conteudo`, e a lista única de dependências
aprovadas em `tests/dependencias.py` (research R11, R18).

```bash
uv run pytest
```

Esperado: a suíte inteira passa. Nenhuma feature anterior muda de comportamento.

## O que observar (mapa para a spec)

| Verificação | Onde está provada | Spec |
|-------------|-------------------|------|
| Uma linha por registro, inclusive sem Participação e não elegível com Participação | testes de grão | US3; FR-010 a FR-013 |
| Contexto congelado depois de alteração acadêmica simulada | testes de reprodução | US4, US7; FR-003, FR-022 |
| Quatro tipos, múltipla por indicador, complemento em coluna própria | testes de Perguntas | US5; FR-034 a FR-038 |
| Aplicabilidade: verdadeiro / falso / vazio e invariantes | testes de percurso | US5; FR-046, FR-047; SC-014 |
| Dicionário um-para-um com Dados; valores possíveis; regras de navegação | testes de dicionário | US6; FR-050 a FR-058 |
| Metadados fixos, sem `gerado_em`, sem nome da Pesquisa, sem `encerrada_em` | testes de metadados | US8; FR-060 a FR-067 |
| CSV × XLSX idênticos depois de lidos | testes de formatos | US2; FR-070; SC-003 |
| Escape e reversão universal; XLSX sem fórmulas | testes de segurança | US9; FR-075 a FR-078; SC-007 |
| Pseudônimos estáveis sob a mesma chave, diferentes com outra, recusa sem chave | testes de pseudonimização | US12; FR-026 a FR-029; SC-013 |
| Nenhuma PII nem identificador interno nos arquivos | testes de privacidade | FR-026, FR-110; SC-006 |
| Nenhum modelo, rota, comando; imports permitidos; sem nomes de ferramentas downstream | testes de fronteira | FR-100, FR-122, FR-130; SC-011 |

## Inspecionar um pacote manualmente (opcional)

Num shell de teste, com banco de desenvolvimento e chave fictícia:

```bash
TRAJETORIA_CHAVE_PSEUDONIMIZACAO=chave-ficticia-apenas-para-desenvolvimento-local-0001 uv run python manage.py shell
```

- Crie um cenário fictício com as funções de `tests/analitico/construcao.py`, capture com
  `capturar_snapshot(campanha)` e chame `exportar_csv(snapshot)` ou
  `exportar_xlsx(snapshot)` (contracts/exportacao.md).
- Grave os bytes **fora do repositório** para abrir numa planilha.
- Confira:
  - abas e arquivos esperados;
  - nenhum valor iniciado por `=` virou fórmula no XLSX;
  - textos com acento intactos;
  - colunas `__aplicavel`;
  - Metadados com `capturado_em` e sem momento de exportação.

Nunca use dados ou chave reais (FR-115; DP-1301).

## Volume (SC-012)

```bash
uv run pytest tests/exportacao -m volume
```

Esperado: com 20.000 registros fictícios e um instrumento do porte do formulário 2024, cada
formato termina em menos de 1 minuto no ambiente de desenvolvimento. O teste fica fora da
suíte padrão (research R15). O resultado é medição, não garantia de produção.
