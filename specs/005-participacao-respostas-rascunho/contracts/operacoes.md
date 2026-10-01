# Contrato: operações de Participação e Resposta

Interface de escrita, consumida pelos testes desta feature e, no futuro, pela 006
(Jornada de resposta). Módulo: `trajetoria.participacao.operacoes`. Atende FR-006 a
FR-041, FR-051 a FR-054 e FR-059. As consultas estão em [consultas.md](consultas.md).

Nomes de funções e parâmetros são a proposta do plan. A assinatura exata pode ser
ajustada nas tasks sem mudar o comportamento descrito aqui.

## Garantias comuns

- **Único caminho de escrita**: nenhum outro código grava `Participacao`, `Resposta` ou
  `RespostaOpcao`. Não há `save()` exposto como contrato, CRUD genérico, sinal, gatilho
  ou `save()` sobrescrito.
- **Atômica**: cada operação roda numa transação. Toda validação vem antes da primeira
  gravação; ou tudo é gravado, ou nada (FR-051, R12).
- **Serializada por Participação**: as escritas de resposta bloqueiam a linha da
  Participação (`select_for_update(of=("self",))`) antes de ler ou gravar (FR-053, R11).
- **Verdade do banco**: Participação, Campanha, Pergunta e Opções são relidas do banco;
  atributos das instâncias recebidas não são confiados (R9).
- **Sem efeito fora do app**: nenhuma operação escreve em Campanha, Conclusão, Pessoa,
  Versão, Seção, Pergunta ou Opção (FR-043, FR-060).
- **Tempo**: `iniciar_participacao` e as escritas recebem `agora: datetime | None =
  None`, interpretado por `momento_de_referencia` e `estado` da 004 (R13). `agora` que
  não seja `datetime` com timezone é `TypeError`.
- **Textos**: gravados exatamente como recebidos, sem `strip()`. Vazio ou só com espaços
  é rejeitado.
- **Erro de programação × domínio** (R8): argumento estrutural de classe errada
  (`campanha`, `conclusao`, `participacao`, `pergunta`, `agora`) é `TypeError` antes de
  qualquer escrita. Valor declarado de forma ou conteúdo inválido é
  `ParticipacaoRejeitada`.
- **Sem dado declarado em rastros**: `Violacao.detalhe` cita motivo, campo e UUIDs
  técnicos, nunca texto, inteiro ou complemento declarados. Nenhum log (FR-059, R15).

## Rejeição

```python
class ParticipacaoRejeitada(Exception):
    violacoes: tuple[Violacao, ...]      # sempre ≥ 1
    motivos: tuple[Motivo, ...]          # conveniência para testes

@dataclass(frozen=True)
class Violacao:
    motivo: Motivo
    campo: str | None                    # "campanha", "conclusao", "pergunta", "opcao",
                                         # "opcoes", "texto", "escala", "complemento"
    detalhe: str                         # para pessoas; sem dado declarado ou pessoal
```

Módulo `trajetoria.participacao.regras`, no mesmo padrão de `campanha.regras` e
`instrumento.regras`. `iniciar_participacao` reúne as duas condições de admissão numa
única rejeição (FR-012). As escritas rejeitam na primeira violação, na ordem do
esqueleto (abaixo).

### Motivos (`Motivo`)

| Motivo | FR-052 | Requisito | Quando |
|--------|:------:|-----------|--------|
| `COLETA_NAO_ADMITIDA` | a | FR-011, FR-039 | Iniciar ou escrever com a Campanha fora de `EM_COLETA` no momento de referência |
| `CONCLUSAO_NAO_ELEGIVEL` | b | FR-011, FR-012 | Iniciar com `avaliar` NÃO ELEGÍVEL; `detalhe` lista os critérios e motivos da 004 (sem valores da Conclusão) |
| `PARTICIPACAO_INEXISTENTE` | c | FR-052 c | Escrever em Participação sem linha gravada |
| `PERGUNTA_DE_OUTRA_VERSAO` | d | FR-019, FR-020 | Pergunta cuja Versão não é a da Campanha da Participação |
| `OPCAO_DE_OUTRA_PERGUNTA` | e | FR-024, FR-025, FR-028 | Opção que não pertence à Pergunta, inclusive Opção de outra Versão |
| `VALOR_INCOMPATIVEL` | f | FR-023, FR-024, FR-027 | Operação de um tipo para Pergunta de outro tipo; valor de forma errada (texto no lugar de Opção, coleção em escolha única, `str`, Opção isolada ou não coleção em múltipla, não-`str` em texto, não-`int` ou `bool` em escala) |
| `ESCALA_FORA_DOS_LIMITES` | g | FR-027 | Inteiro abaixo de `escala_inicio` ou acima de `escala_fim` |
| `COMPLEMENTO_NAO_ADMITIDO` | h | FR-030 a, b | Complemento sem a Opção que o admite selecionada |
| `VALOR_VAZIO` | i | FR-024–FR-027, FR-030 c | Valor ausente ou vazio em qualquer operação de resposta: `None` como valor (Opção, conjunto, texto ou escala); conjunto vazio; texto vazio ou só espaços; complemento vazio ou só espaços (`campo` identifica qual). Ausência de resposta só se registra por `remover_resposta` |

Complemento em texto curto ou escala não é parâmetro das operações desses tipos: não
pode ser informado (FR-030 b é garantido pela assinatura).

**Ausência × vazio (regra uniforme)**: nenhuma operação `responder_*` grava Resposta
vazia nem interpreta valor ausente como remoção. `None`, `""`, `"   "` e coleção vazia
são sempre `VALOR_VAZIO`, verificado **antes** da forma do valor. "Pergunta não
respondida" é exatamente "não existe Resposta", e só `remover_resposta` volta a esse
estado. `complemento=None` não é valor vazio: é "sem complemento".

## Operações

### `iniciar_participacao(campanha, conclusao, *, agora=None) -> Inicio`

```python
class SituacaoInicio(Enum):
    CRIADA = "criada"
    JA_EXISTENTE = "ja_existente"

class Inicio(NamedTuple):
    participacao: Participacao
    situacao: SituacaoInicio
```

| Situação | Efeito | Retorno |
|----------|--------|---------|
| Par já tem Participação (qualquer estado da Campanha, qualquer elegibilidade atual) | nada | `(existente, JA_EXISTENTE)` (FR-013) |
| Par sem Participação e `admite_participacao(campanha, conclusao, agora=…)` | cria com `iniciada_em = momento_de_referencia(agora)` | `(nova, CRIADA)` (FR-011) |
| Par sem Participação e admissão falha | nada | `ParticipacaoRejeitada` com `COLETA_NAO_ADMITIDA` e/ou `CONCLUSAO_NAO_ELEGIVEL` (FR-012) |
| Insert concorrente perde a corrida (`IntegrityError` na unicidade) | nada | `(a outra, JA_EXISTENTE)` (R11) |

Diagnóstico da falha: `estado(campanha, agora=…) is not EM_COLETA` →
`COLETA_NAO_ADMITIDA`; `not avaliar(campanha, conclusao).elegivel` →
`CONCLUSAO_NAO_ELEGIVEL`. Nenhuma regra de estado, período ou critério é reescrita
(FR-014). `JA_EXISTENTE` não autoriza escrita: as escritas verificam a coleta por conta
própria.

### Esqueleto comum das escritas de resposta

1. `TypeError` para argumentos estruturais de classe errada.
2. Abre transação; bloqueia a Participação (`PARTICIPACAO_INEXISTENTE` se não há linha).
3. `estado(participacao.campanha, agora=…) is EM_COLETA`, senão `COLETA_NAO_ADMITIDA`.
   Elegibilidade **não** é reavaliada (FR-034).
4. Relê a Pergunta; se `pergunta.secao.versao_id != campanha.versao_id`,
   `PERGUNTA_DE_OUTRA_VERSAO`.
5. Se `pergunta.tipo` não é o tipo da operação, `VALOR_INCOMPATIVEL`.
6. Valida o valor (por tipo, abaixo).
7. Grava o valor inteiro na Resposta do par `(participacao, pergunta)`, criando-a se não
   existe ou atualizando a existente no lugar (mesmo `id`). Colunas das outras formas e
   o complemento ausente ficam `NULL`.

Retorno: a `Resposta` gravada, com `opcoes` recarregadas quando for escolha múltipla.

### `responder_escolha_unica(participacao, pergunta, opcao, *, complemento=None, agora=None) -> Resposta`

- `opcao is None` → `VALOR_VAZIO` (`opcao`).
- `opcao` que não é `Opcao` (texto, coleção, número) → `VALOR_INCOMPATIVEL`.
- Opção que não está em `Opcao.objects.filter(pergunta=pergunta)` →
  `OPCAO_DE_OUTRA_PERGUNTA`.
- `complemento` informado: vazio ou só espaços → `VALOR_VAZIO` (`complemento`); Opção sem
  `complemento_textual` → `COMPLEMENTO_NAO_ADMITIDO`; `complemento` que não é `str` →
  `VALOR_INCOMPATIVEL`.
- Grava `opcao`, `complemento`; apaga seleções e zera `texto`, `escala` (defensivo).

### `responder_escolha_multipla(participacao, pergunta, opcoes, *, complemento=None, agora=None) -> Resposta`

- `opcoes is None` → `VALOR_VAZIO` (`opcoes`).
- `opcoes` deve ser coleção iterável de `Opcao` que não seja `str` nem `Opcao` isolada;
  senão `VALOR_INCOMPATIVEL`.
- Deduplicada por identidade; ordem descartada (FR-025).
- Conjunto vazio → `VALOR_VAZIO` (`opcoes`). Para "desmarcar tudo", usar
  `remover_resposta` (Clarifications).
- Alguma Opção fora da Pergunta → `OPCAO_DE_OUTRA_PERGUNTA`, sem gravar nenhuma.
- `complemento` informado: vazio → `VALOR_VAZIO`; a Opção com `complemento_textual` da
  Pergunta não está no conjunto → `COMPLEMENTO_NAO_ADMITIDO`.
- Grava a Resposta (com `opcao`, `texto`, `escala` `NULL`) e substitui o conjunto:
  apaga as linhas de `RespostaOpcao` da Resposta e insere as novas, na mesma transação
  (R12).

### `responder_texto(participacao, pergunta, texto, *, agora=None) -> Resposta`

- `texto is None`, vazio ou só espaços → `VALOR_VAZIO` (`texto`).
- `texto` que não é `str` → `VALOR_INCOMPATIVEL`.
- Grava exatamente como recebido; sem regex, máscara, conversão ou limite de domínio
  (FR-026).

### `responder_escala(participacao, pergunta, valor, *, agora=None) -> Resposta`

- `valor is None` → `VALOR_VAZIO` (`escala`).
- `valor` que não é `int`, ou é `bool` → `VALOR_INCOMPATIVEL`.
- Fora de `[pergunta.escala_inicio, pergunta.escala_fim]` → `ESCALA_FORA_DOS_LIMITES`.
- Grava o inteiro, sem rótulo, peso ou normalização (FR-027).

### `remover_resposta(participacao, pergunta, *, agora=None) -> SituacaoRemocao`

```python
class SituacaoRemocao(Enum):
    REMOVIDA = "removida"
    INEXISTENTE = "inexistente"
```

Passos 1 a 4 do esqueleto (coleta e Versão verificadas; tipo indiferente). Remove a
Resposta (e, por `CASCADE`, suas seleções) → `REMOVIDA`; sem Resposta → `INEXISTENTE`,
nada muda (FR-036). Obrigatoriedade não é verificada (FR-037).

## O que não existe

Nenhuma operação: remove ou altera Participação; muda `campanha`, `conclusao` ou
`iniciada_em`; grava histórico, evento ou momento por edição; conclui, submete ou marca
estado; calcula progresso; verifica obrigatoriedade ou navegação; cria Resposta a partir
de dado da Conclusão; escreve em modelos das Features 001–004; registra consentimento;
recebe autenticação, sessão ou token.
