# Contrato: operações do instrumento

Interface de escrita que as próximas features consomem (em primeiro lugar a Feature
003). Módulo: `trajetoria.instrumento.operacoes`. Atende FR-001 a FR-062. A leitura está
em [conteudo.md](conteudo.md).

Nomes de funções e parâmetros são a proposta do plan; a assinatura exata pode ser
ajustada nas tasks sem mudar o comportamento descrito aqui.

## Garantias comuns a todas as operações

- **Atômica**: cada operação roda numa transação. Ou tudo é gravado, ou nada (FR-060).
- **Serializada por Versão**: toda operação sobre uma Versão ou seus elementos bloqueia a
  linha da Versão antes de verificar (R12).
- **Rejeição explícita**: violação levanta `OperacaoRejeitada`; o estado após a exceção
  é idêntico ao anterior.
- **Versão publicada**: toda operação de escrita sobre ela ou seus elementos é rejeitada
  com `VERSAO_PUBLICADA` (FR-016), exceto `publicar`, que devolve `JA_PUBLICADA`.
- **Textos**: gravados exatamente como recebidos. Texto obrigatório vazio ou só com
  espaços é rejeitado com `TEXTO_VAZIO`. Texto opcional vazio ou só com espaços também é
  rejeitado; ausência é `None`.
- **Sem efeitos externos**: nenhuma operação acessa rede, Pessoa ou Conclusão Acadêmica.

## Rejeição

```python
class OperacaoRejeitada(Exception):
    violacoes: tuple[Violacao, ...]          # sempre ≥ 1

@dataclass(frozen=True)
class Violacao:
    motivo: Motivo
    elemento: UUID | None                    # elemento envolvido, quando houver
    detalhe: str                             # texto para pessoas; sem dado pessoal
```

`publicar` reúne **todas** as violações de completude numa única rejeição (FR-014). As
demais operações rejeitam na primeira violação.

### Motivos (`Motivo`)

| Motivo | Requisito | Quando |
|--------|-----------|--------|
| `VERSAO_PUBLICADA` | FR-016, FR-058 o | Escrita em Versão publicada ou em seus elementos |
| `REFERENCIA_OUTRA_VERSAO` | FR-058 a, g | Destino de regra ou encaminhamento, Seção de destino de movimentação, ou origem de cópia de outra Versão/Pesquisa |
| `OPCAO_EM_TIPO_SEM_OPCOES` | FR-040, FR-058 b | Opção em `TEXTO_CURTO` ou `ESCALA` |
| `ESCALA_EM_TIPO_NAO_ESCALA` | FR-058 c | Configuração de escala em tipo que não é `ESCALA` |
| `ESCALA_INVALIDA` | FR-038, FR-058 d | Escala sem limites, limite não inteiro ou início ≥ fim |
| `REGRA_EM_TIPO_INCOMPATIVEL` | FR-050, FR-058 e | Regra em pergunta que não é `ESCOLHA_UNICA` |
| `OPCAO_DE_OUTRA_PERGUNTA` | FR-058 f | Regra na Pergunta X com Opção que não é de X |
| `REGRA_JA_DEFINIDA` | FR-052, FR-058 h | Definir regra em Opção que já tem regra |
| `POSICAO_OCUPADA` | FR-047, FR-058 i | Inclusão ou movimentação para posição já usada |
| `ORDEM_INCOMPLETA` | FR-045, FR-047 | Reordenação sem exatamente todos os elementos do conjunto, ou com repetição |
| `POSICAO_INVALIDA` | FR-045 | Posição não inteira ou menor que 1 |
| `TIPO_NAO_SUPORTADO` | FR-034, FR-058 j | Tipo fora dos quatro |
| `TEXTO_VAZIO` | FR-058 k | Texto obrigatório ou opcional vazio ou só com espaços |
| `DESIGNACAO_REPETIDA` | FR-006, FR-058 l | Designação já usada na Pesquisa |
| `OPCAO_REPETIDA` | FR-058 m | Texto de Opção já usado na mesma Pergunta |
| `COMPLEMENTO_REPETIDO` | FR-042, FR-058 n | Segunda Opção com complemento textual na Pergunta |
| `SECAO_COM_PERGUNTAS` | FR-061 | Remover Seção que contém Perguntas |
| `SECAO_REFERENCIADA` | FR-061 | Remover Seção que é destino de regra ou encaminhamento |
| `SEM_SECOES` | FR-059 a | Publicar Versão sem Seções |
| `SECAO_SEM_PERGUNTAS` | FR-059 b | Publicar com Seção vazia (um por Seção) |
| `OPCOES_INSUFICIENTES` | FR-059 c | Publicar com pergunta de escolha com menos de duas Opções (um por Pergunta) |
| `DESTINO_NAO_POSTERIOR` | FR-055, FR-059 d | Publicar com regra ou encaminhamento para a própria Seção ou Seção anterior (um por ocorrência) |

## Pesquisa

| Operação | Efeito | Rejeições |
|----------|--------|-----------|
| `criar_pesquisa(nome) -> Pesquisa` | Cria Pesquisa sem Versões | `TEXTO_VAZIO` |
| `renomear_pesquisa(pesquisa, nome) -> Pesquisa` | Altera só o nome; nenhuma Versão é tocada (FR-003) | `TEXTO_VAZIO` |

## Versão

| Operação | Efeito | Rejeições |
|----------|--------|-----------|
| `criar_versao(pesquisa, designacao) -> Versao` | Nova Versão em `RASCUNHO`, sem conteúdo nem origem | `TEXTO_VAZIO`, `DESIGNACAO_REPETIDA` |
| `alterar_versao(versao, *, designacao=…, titulo=…, texto_abertura=…, texto_encerramento=…) -> Versao` | Altera só os campos informados; `None` remove um texto opcional | `VERSAO_PUBLICADA`, `TEXTO_VAZIO`, `DESIGNACAO_REPETIDA` |
| `criar_versao_a_partir_de(origem, designacao) -> Versao` | Cópia profunda (R11) na Pesquisa da origem; `RASCUNHO`; `origem` registrada; a origem pode estar em qualquer estado e não é alterada | `TEXTO_VAZIO`, `DESIGNACAO_REPETIDA` |
| `publicar(versao) -> SituacaoPublicacao` | Ver abaixo | Motivos de completude |

### `publicar`

```python
class SituacaoPublicacao(Enum):
    PUBLICADA = "publicada"          # transição feita agora; publicada_em registrado
    JA_PUBLICADA = "ja_publicada"    # nada mudou, nem publicada_em (FR-015)
```

1. Bloqueia a Versão.
2. Se já publicada, devolve `JA_PUBLICADA`.
3. Verifica a completude (FR-059) e reúne todas as violações. Havendo alguma, levanta
   `OperacaoRejeitada` com todas elas; a Versão continua em `RASCUNHO` (FR-014).
4. Grava `estado = PUBLICADA` e `publicada_em = agora` e devolve `PUBLICADA`.

Esta operação **não** verifica quem a chama: competência é DP-001. Nenhum ponto de
entrada (admin, comando, endpoint) a expõe nesta feature.

## Seção

| Operação | Efeito | Rejeições |
|----------|--------|-----------|
| `adicionar_secao(versao, posicao, *, titulo=None, texto=None) -> Secao` | Nova Seção na posição | `VERSAO_PUBLICADA`, `POSICAO_INVALIDA`, `POSICAO_OCUPADA`, `TEXTO_VAZIO` |
| `alterar_secao(secao, *, titulo=…, texto=…) -> Secao` | Altera textos; `None` remove | `VERSAO_PUBLICADA`, `TEXTO_VAZIO` |
| `remover_secao(secao) -> None` | Remove Seção vazia e não referenciada | `VERSAO_PUBLICADA`, `SECAO_COM_PERGUNTAS`, `SECAO_REFERENCIADA` |
| `reordenar_secoes(versao, secoes_em_ordem) -> None` | Renumera 1..n na ordem dada | `VERSAO_PUBLICADA`, `ORDEM_INCOMPLETA` |
| `definir_encaminhamento(secao, destino: Secao \| None) -> Secao` | Define ou remove o encaminhamento | `VERSAO_PUBLICADA`, `REFERENCIA_OUTRA_VERSAO` |

Encaminhamento para a própria Seção ou para Seção anterior é aceito em rascunho e
rejeitado na publicação (`DESTINO_NAO_POSTERIOR`).

## Pergunta

```python
class TipoPergunta(Enum):
    ESCOLHA_UNICA = "ESCOLHA_UNICA"
    ESCOLHA_MULTIPLA = "ESCOLHA_MULTIPLA"
    TEXTO_CURTO = "TEXTO_CURTO"
    ESCALA = "ESCALA"

@dataclass(frozen=True)
class Escala:
    inicio: int
    fim: int
    rotulo_inicio: str | None = None
    rotulo_fim: str | None = None
```

| Operação | Efeito | Rejeições |
|----------|--------|-----------|
| `adicionar_pergunta(secao, posicao, tipo, texto, *, obrigatoria, texto_explicativo=None, escala=None) -> Pergunta` | Nova Pergunta. `escala` é obrigatória se e somente se `tipo = ESCALA` | `VERSAO_PUBLICADA`, `POSICAO_INVALIDA`, `POSICAO_OCUPADA`, `TIPO_NAO_SUPORTADO`, `TEXTO_VAZIO`, `ESCALA_EM_TIPO_NAO_ESCALA`, `ESCALA_INVALIDA` |
| `alterar_pergunta(pergunta, *, texto=…, texto_explicativo=…, obrigatoria=…, escala=…) -> Pergunta` | Altera os campos informados; mantém a identidade. **Não há parâmetro de tipo** (FR-062). `escala` só em pergunta `ESCALA` | `VERSAO_PUBLICADA`, `TEXTO_VAZIO`, `ESCALA_EM_TIPO_NAO_ESCALA`, `ESCALA_INVALIDA` |
| `mover_pergunta(pergunta, secao_destino, posicao) -> Pergunta` | Move para outra Seção da mesma Versão (ou outra posição na mesma), mantendo identidade, Opções e regras | `VERSAO_PUBLICADA`, `REFERENCIA_OUTRA_VERSAO`, `POSICAO_INVALIDA`, `POSICAO_OCUPADA` |
| `remover_pergunta(pergunta) -> None` | Remove a Pergunta com suas Opções e regras (FR-061) | `VERSAO_PUBLICADA` |
| `reordenar_perguntas(secao, perguntas_em_ordem) -> None` | Renumera 1..n | `VERSAO_PUBLICADA`, `ORDEM_INCOMPLETA` |

**Tipo (FR-062)**: definido na criação e nunca alterado. Para mudar o tipo, remove-se a
Pergunta (com suas Opções e regras) e cria-se outra.

## Opção

| Operação | Efeito | Rejeições |
|----------|--------|-----------|
| `adicionar_opcao(pergunta, posicao, texto, *, complemento_textual=False) -> Opcao` | Nova Opção, sem regra | `VERSAO_PUBLICADA`, `OPCAO_EM_TIPO_SEM_OPCOES`, `POSICAO_INVALIDA`, `POSICAO_OCUPADA`, `TEXTO_VAZIO`, `OPCAO_REPETIDA`, `COMPLEMENTO_REPETIDO` |
| `alterar_opcao(opcao, *, texto=…, complemento_textual=…) -> Opcao` | Altera; identidade e regra preservadas (FR-041) | `VERSAO_PUBLICADA`, `TEXTO_VAZIO`, `OPCAO_REPETIDA`, `COMPLEMENTO_REPETIDO` |
| `remover_opcao(opcao) -> None` | Remove a Opção e sua regra (FR-061) | `VERSAO_PUBLICADA` |
| `reordenar_opcoes(pergunta, opcoes_em_ordem) -> None` | Renumera 1..n | `VERSAO_PUBLICADA`, `ORDEM_INCOMPLETA` |

## Regra de navegação condicional

```python
FINALIZAR = Finalizar()   # sentinela única: "finalizar o instrumento"
```

| Operação | Efeito | Rejeições |
|----------|--------|-----------|
| `definir_regra(pergunta, opcao, destino: Secao \| Finalizar) -> Opcao` | "Se `pergunta` = `opcao`, ir para `destino`" ou "…, finalizar" | `VERSAO_PUBLICADA`, `REGRA_EM_TIPO_INCOMPATIVEL`, `OPCAO_DE_OUTRA_PERGUNTA`, `REFERENCIA_OUTRA_VERSAO`, `REGRA_JA_DEFINIDA` |
| `remover_regra(pergunta, opcao) -> Opcao` | Remove a regra; a Opção volta ao fluxo padrão. Sem regra, nada muda | `VERSAO_PUBLICADA`, `OPCAO_DE_OUTRA_PERGUNTA` |

Para trocar o destino, remove-se a regra e define-se outra. Destino igual ao fluxo padrão
é aceito (spec, Edge Cases). Destino na própria Seção ou anterior é aceito em rascunho e
rejeitado na publicação.

## O que este contrato não oferece

Exclusão de Pesquisa ou Versão; volta de `PUBLICADA` para `RASCUNHO`; mudança da
Pesquisa de uma Versão; correção editorial em Versão publicada (DP-003); qualquer forma
de executar a navegação; verificação de quem chama (DP-001).
