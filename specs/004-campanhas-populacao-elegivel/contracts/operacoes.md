# Contrato: operações de Campanha

Interface de escrita. Módulo: `trajetoria.campanha.operacoes`. Atende FR-001 a FR-024,
FR-034 a FR-047 e FR-056 a FR-057. As consultas estão em [consultas.md](consultas.md).

Nomes de funções e parâmetros são a proposta do plan. A assinatura exata pode ser
ajustada nas tasks sem mudar o comportamento descrito aqui.

## Garantias comuns

- **Único caminho de escrita**: nenhum outro código grava `Campanha` (research R10).
- **Atômica e serializada**: cada operação roda numa transação e bloqueia a linha da
  Campanha antes de verificar. Ou tudo é gravado, ou nada (FR-057).
- **Imutável após a primeira abertura**: toda operação de escrita sobre Campanha com
  `aberta_em` presente, em qualquer estado temporal, é rejeitada com
  `CAMPANHA_JA_ABERTA` (FR-043, FR-044). Campanha nunca aberta é editável e removível
  mesmo com período expirado, quando seu estado é ENCERRADA. As exceções são `abrir` e
  `encerrar`, com regras próprias abaixo. O estado temporal controla a coleta; a
  abertura histórica controla a imutabilidade.
- **Nenhum efeito fora da Campanha**: nenhuma operação escreve em Versão, Pesquisa,
  Pessoa ou Conclusão Acadêmica, nem publica Versão (FR-006, FR-009).
- **Tempo**: só `abrir` e `encerrar` dependem do tempo e recebem
  `agora: datetime | None = None`. As operações de preparação não dependem do tempo. O
  padrão é o momento atual, e a data de referência é `agora` convertida para a timezone
  configurada do projeto (research R6). `agora` que não seja `datetime` com timezone
  (`date`, `datetime` ingênuo, texto) é `TypeError`.
- **Instância recebida**: toda operação relê a Campanha sob bloqueio, grava a cópia
  relida e copia os campos gravados para a instância recebida, inclusive `abrir` e
  `encerrar`. Quem segue usando a mesma instância vê o estado gravado, sem
  `refresh_from_db`. As operações de preparação devolvem essa instância.
- **Textos**: gravados exatamente como recebidos, sem `strip()`. Texto vazio ou só com
  espaços é rejeitado.
- **Tipo errado de argumento** (`nome` que não é `str`; `versao` que não é `Versao`;
  data que não é `date` ou é `datetime`; conjunto que é `str` ou não é coleção; valor de
  conjunto que não é `str`) é erro de programação: `TypeError` antes de qualquer escrita.
  `CampanhaRejeitada` fica para valores inválidos no domínio.

## Rejeição

```python
class CampanhaRejeitada(Exception):
    violacoes: tuple[Violacao, ...]      # sempre ≥ 1
    motivos: tuple[Motivo, ...]          # conveniência para testes

@dataclass(frozen=True)
class Violacao:
    motivo: Motivo
    campo: str | None                    # "nome", "inicio", "fim", "ano_minimo", "unidades", "versao"…
    detalhe: str                         # texto para pessoas; sem dado pessoal
```

`definir_periodo`, `definir_criterios` e `abrir` reúnem **todas** as violações numa
única rejeição (FR-012, FR-023, FR-036). As demais rejeitam na primeira.

### Motivos (`Motivo`)

| Motivo | Requisito | Quando |
|--------|-----------|--------|
| `NOME_VAZIO` | FR-002 a | Nome vazio ou só com espaços |
| `CAMPANHA_JA_ABERTA` | FR-043, FR-044 | Alterar, definir período ou critérios, ou remover Campanha com `aberta_em` presente (EM_COLETA ou ENCERRADA após abertura) |
| `PERIODO_INCOMPLETO` | FR-012 | Uma das datas ausente |
| `PERIODO_INVERTIDO` | FR-012 | `inicio > fim` |
| `ANO_INVALIDO` | FR-023 a | Ano que não é inteiro positivo (inclui `bool`, texto, número fracionário, ≤ 0) |
| `ANOS_INVERTIDOS` | FR-023 b | `ano_minimo > ano_maximo` |
| `CONJUNTO_VAZIO` | FR-023 c | Critério de conjunto informado como coleção vazia. Ausência é `None`, nunca `[]` |
| `VALOR_VAZIO` | FR-023 d | Valor de conjunto vazio ou só com espaços |
| `VERSAO_NAO_PUBLICADA` | FR-009, FR-036 a | Abertura com Versão em RASCUNHO |
| `PERIODO_NAO_DEFINIDO` | FR-036 b | Abertura sem período |
| `FORA_DO_PERIODO` | FR-036 d | Abertura com data de referência antes do início ou depois do encerramento |
| `ANTES_DA_ABERTURA` | FR-057 | Encerramento explícito com `agora` anterior a `aberta_em` |
| `CAMPANHA_NUNCA_ABERTA` | FR-040 | Encerramento explícito de Campanha nunca aberta, em qualquer estado temporal (inclusive ENCERRADA pelo tempo) |

A condição FR-036 c ("critérios válidos") não tem motivo próprio na abertura: critérios
só chegam ao banco válidos (`definir_criterios` e CHECKs). Um teste de modelo garante que
nenhuma escrita gera critério inválido.

## Operações

### `criar_campanha(nome: str, versao: Versao) -> Campanha`

Cria a Campanha EM_PREPARACAO, sem período e sem critérios, com população ampla
(FR-007, FR-019, FR-035). A Versão pode estar em qualquer estado.

Rejeições: `NOME_VAZIO`.

### `alterar_campanha(campanha, *, nome=MANTER, versao=MANTER) -> Campanha`

Troca nome e/ou Versão, inclusive por Versão de outra Pesquisa (FR-008). Parâmetro
omitido mantém o valor.

Rejeições: `CAMPANHA_JA_ABERTA`, `NOME_VAZIO`.

### `definir_periodo(campanha, inicio: date | None, fim: date | None) -> Campanha`

Grava o período, com as duas datas incluídas (FR-011 a FR-013). Não há período padrão
(FR-014).

Pode corrigir o período de Campanha nunca aberta e expirada. Isso a devolve a
EM_PREPARACAO quando o novo fim não passou, e não é reabertura (FR-039).

Rejeições (todas de uma vez): `CAMPANHA_JA_ABERTA` (sozinha, antes das demais),
`PERIODO_INCOMPLETO`, `PERIODO_INVERTIDO`.

### `definir_criterios(campanha, *, ano_minimo=None, ano_maximo=None, unidades=None, niveis=None, modalidades=None, formas_oferta=None) -> Campanha`

**Substitui** a definição inteira de critérios (research R11). `None` significa critério
não definido, gravado como `NULL`. Uma coleção vazia (`[]`, `()`, `set()`) é configuração
inválida (`CONJUNTO_VAZIO`), nunca equivalente a `None`. Sem argumentos, a população
volta a ser ampla. Conjuntos são gravados com os textos exatos, sem duplicatas e em ordem
lexicográfica, só para estabilidade e comparação.

Rejeições (todas de uma vez, com `campo` identificado): `CAMPANHA_JA_ABERTA` (sozinha),
`ANO_INVALIDO`, `ANOS_INVERTIDOS`, `CONJUNTO_VAZIO`, `VALOR_VAZIO`.

### `abrir(campanha, *, agora: datetime | None = None) -> SituacaoAbertura`

| Situação | Efeito | Retorno |
|----------|--------|---------|
| Nunca aberta, condições satisfeitas | grava `aberta_em = agora` → EM_COLETA | `ABERTA` |
| Nunca aberta, alguma condição falha (inclusive período já expirado, quando o estado já é ENCERRADA sem abertura) | nada | `CampanhaRejeitada` com todas as condições: `VERSAO_NAO_PUBLICADA`, `PERIODO_NAO_DEFINIDO`, `FORA_DO_PERIODO` |
| Já aberta, EM_COLETA | nada | `JA_EM_COLETA` (FR-037) |
| Já aberta, ENCERRADA | nada | `JA_ENCERRADA` (FR-037) |

Condições (FR-036): Versão PUBLICADA; período definido; `inicio ≤ hoje ≤ fim`.
`FORA_DO_PERIODO` só é verificada com período definido. A Versão é lida dentro da
transação. Como a publicação é irreversível (002 FR-013), não é preciso bloqueá-la.

Nunca publica a Versão (FR-009) e nunca agenda nada (FR-042).

### `encerrar(campanha, *, agora: datetime | None = None) -> SituacaoEncerramento`

| Situação na data de referência | Efeito | Retorno |
|--------------------------------|--------|---------|
| Aberta, EM_COLETA | grava `encerrada_em = agora` → ENCERRADA, forma EXPLICITA | `ENCERRADA` |
| Aberta, ENCERRADA (explícita ou por fim do período) | nada | `JA_ENCERRADA` (FR-040). `encerrada_em` já gravado nunca é sobrescrito, mesmo com `agora` anterior a ele |
| Aberta, `agora` anterior a `aberta_em` | nada | `CampanhaRejeitada(ANTES_DA_ABERTURA)` |
| Nunca aberta (EM_PREPARACAO ou ENCERRADA pelo tempo) | nada | `CampanhaRejeitada(CAMPANHA_NUNCA_ABERTA)` (FR-040) |

Não altera o período planejado (FR-045).

### `remover_campanha(campanha) -> None`

Remove Campanha nunca aberta, inclusive a ENCERRADA pelo tempo. Versão, Pesquisa e
Conclusões não são afetadas (FR-044).

Rejeições: `CAMPANHA_JA_ABERTA`.

## O que não existe

Nenhuma operação: muda `aberta_em` ou `encerrada_em` depois de gravados; reabre;
prorroga; altera Campanha aberta; publica Versão; grava população, contagem ou resultado
de elegibilidade; cria convite, destinatário ou agendamento. Não há sinal, gatilho ou
`save()` sobrescrito.
