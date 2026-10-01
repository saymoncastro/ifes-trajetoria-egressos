# Contrato: conclusão e bloqueio de escrita

Módulo: `trajetoria.participacao.operacoes` (único caminho de escrita, 005). Atende FR-001
a FR-005, FR-022 a FR-024, FR-028, FR-031 a FR-046 e FR-053.

As garantias comuns da 005 continuam valendo ([005 contracts/operacoes.md](../../005-participacao-respostas-rascunho/contracts/operacoes.md#garantias-comuns)):
atomicidade, bloqueio da Participação, verdade do banco, nenhum efeito fora do app,
`agora` com timezone, erro de programação × domínio, nenhum valor declarado em rastros.

## Motivos novos (`trajetoria.participacao.regras.Motivo`)

| Motivo | Requisito | Quando |
|--------|-----------|--------|
| `PARTICIPACAO_CONCLUIDA` | FR-038 | Registrar, substituir ou remover Resposta em Participação com `concluida_em` |
| `ESTRUTURA_NAO_SUPORTADA` | FR-016 | Versão aplicada com Seção que tem mais de uma Pergunta com regra (contracts/percurso.md) |
| `OBRIGATORIA_PENDENTE` | FR-019, FR-034 d, FR-037 | Pergunta obrigatória da Seção atual sem Resposta, numa jornada não finalizada |

Os motivos da 005 continuam; `COLETA_NAO_ADMITIDA` e os de valor (`OPCAO_DE_OUTRA_PERGUNTA`,
`VALOR_INCOMPATIVEL`, `VALOR_VAZIO`, `ESCALA_FORA_DOS_LIMITES`, `COMPLEMENTO_NAO_ADMITIDO`)
também são usados pela conclusão.

## `concluir(participacao, *, agora=None) -> ResultadoConclusao`

```python
class SituacaoConclusao(Enum):
    CONCLUIDA = "concluida"          # concluida_em gravado agora
    JA_CONCLUIDA = "ja_concluida"    # nada foi lido além da Participação; nada mudou

class ResultadoConclusao(NamedTuple):
    participacao: Participacao       # relida, com concluida_em
    situacao: SituacaoConclusao
```

### Passos

| # | Passo | Falha |
|---|-------|-------|
| 1 | `participacao` não é `Participacao` → `TypeError`; `agora` inválido → `TypeError`, antes do banco | erro de programação |
| 2 | Transação; bloqueia a Participação (`select_for_update(of=("self",))`) | sem linha → `PARTICIPACAO_INEXISTENTE` |
| 3 | `concluida_em` preenchido → devolve `(participacao, JA_CONCLUIDA)` | — (FR-036: sem consultar a Campanha, sem reconstruir nem revalidar o percurso, sem limpeza, sem regravar; a conclusão histórica já ocorreu) |
| 4 | `agora = momento_de_referencia(agora)`, lido depois do bloqueio | — |
| 5 | `estado(campanha, agora=agora) is not EM_COLETA` → violação `COLETA_NAO_ADMITIDA` | acumula |
| 6 | Carrega `conteudo_da_versao(campanha.versao)` e `respostas_atuais(participacao)`; monta `respondidas` (toda a I/O fica na operação; `percorrer` é puro) | — |
| 7 | `percorrer(conteudo, respondidas)` | `ESTRUTURA_NAO_SUPORTADA` (ou `OPCAO_DE_OUTRA_PERGUNTA` em X): rejeita com elas **e** a do passo 5, se houver |
| 8 | `pendencias(passagens)` | acumula `OBRIGATORIA_PENDENTE` |
| 9 | Para cada Resposta ativa (Pergunta em `perguntas_do_percurso`): `_verificar_resposta_gravada` (validadores da 005) | acumula o motivo da 005, `campo="pergunta"` |
| 10 | Alguma violação → `ParticipacaoRejeitada` com **todas**; nada gravado, nada removido | — (FR-037, FR-044) |
| 11 | Remove as Respostas da Participação cujas Perguntas não estão em `perguntas_do_percurso` (inclui seleções, por `CASCADE`) | — |
| 12 | `concluida_em = agora`; `save(update_fields=["concluida_em"])` | — |
| 13 | Devolve `(participacao, CONCLUIDA)` | — |

Não reavalia elegibilidade (005, Clarifications). Não exige complemento de "Outro:"
(FR-028; DP-602). Q1 = "Não" é só a regra de finalização da Versão: a conclusão aceita deixa
apenas a Resposta de Q1 (FR-023); nada de consentimento é registrado (FR-024).

### `_verificar_resposta_gravada(resposta, pergunta)` (privada, R10)

Compõe os validadores da 005 com os valores gravados, sem regra nova:

| Tipo | Validadores |
|------|-------------|
| `ESCOLHA_UNICA` | `_opcao_da_pergunta(pergunta, resposta.opcao)`; `_complemento(resposta.complemento, [opcao])` |
| `ESCOLHA_MULTIPLA` | `_opcoes_da_pergunta(pergunta, resposta.opcoes.all())`; `_complemento(resposta.complemento, opcoes)` |
| `TEXTO_CURTO` | `_texto_declarado(resposta.texto, "texto")` |
| `ESCALA` | `_escala_da_pergunta(pergunta, resposta.escala)` — extraída de `responder_escala`, mesmo comportamento |

A rejeição é reembalada como `Violacao(motivo da 005, "pergunta", "Pergunta <id>: <detalhe
da 005>")`.

## Escritas de resposta da 005 — alteração

No esqueleto comum ([005 contrato](../../005-participacao-respostas-rascunho/contracts/operacoes.md#esqueleto-comum-das-escritas-de-resposta)),
entre os passos 2 (bloqueio) e 3 (coleta):

> **2a.** `participacao.concluida_em is not None` → `PARTICIPACAO_CONCLUIDA`
> (`campo="participacao"`).

Vale para `responder_escolha_unica`, `responder_escolha_multipla`, `responder_texto`,
`responder_escala` e `remover_resposta`, com a Campanha em qualquer estado. Nenhum outro
passo muda. As escritas continuam aceitando qualquer Pergunta da Versão aplicada, dentro ou
fora do percurso (FR-031).

`iniciar_participacao` não muda: para o par de uma Participação concluída devolve
`(existente, JA_EXISTENTE)`, sem alteração (FR-041).

## Concorrência (R12)

| Situação | Resultado |
|----------|-----------|
| Duas `concluir` simultâneas | A segunda espera o bloqueio, relê `concluida_em` → `JA_CONCLUIDA`; um único `concluida_em`; uma única limpeza |
| `concluir` e escrita simultâneas | Escrita antes: considerada pela conclusão. Escrita depois: `PARTICIPACAO_CONCLUIDA` |

## O que não existe

Reabrir, desfazer conclusão, editar após concluir, retificar, nova tentativa, segunda
submissão; gravar posição, Seção atual, progresso ou histórico; remover Respostas fora de
uma conclusão aceita; expirar rascunhos; gatilho PostgreSQL; registro de consentimento.
