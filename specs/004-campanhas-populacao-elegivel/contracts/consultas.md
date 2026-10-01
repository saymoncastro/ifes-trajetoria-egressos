# Contrato: consultas de Campanha

Interface de leitura, consumida pelos testes desta feature e, no futuro, pela 005
(Participação e Respostas). Módulo: `trajetoria.campanha.consultas`. Atende FR-019, FR-025
a FR-033, FR-038, FR-045 e FR-050 a FR-053.

Nenhuma consulta grava nada (FR-030, FR-032).

## Tipos

```python
class EstadoCampanha(Enum):
    EM_PREPARACAO = "em_preparacao"
    EM_COLETA = "em_coleta"
    ENCERRADA = "encerrada"

class FormaEncerramento(Enum):
    EXPLICITA = "explicita"
    FIM_DO_PERIODO = "fim_do_periodo"

class Resultado(Enum):
    ELEGIVEL = "elegivel"
    NAO_ELEGIVEL = "nao_elegivel"

class Criterio(Enum):          # ordem de declaração = ordem das pendências
    ANO_CONCLUSAO = "ano_conclusao"
    UNIDADE = "unidade"
    NIVEL = "nivel"
    MODALIDADE = "modalidade"
    FORMA_OFERTA = "forma_oferta"

class MotivoPendencia(Enum):
    NAO_INFORMADO = "nao_informado"
    NAO_ATENDE = "nao_atende"

@dataclass(frozen=True)
class Pendencia:
    criterio: Criterio
    motivo: MotivoPendencia

@dataclass(frozen=True)
class Elegibilidade:
    pendencias: tuple[Pendencia, ...]    # vazia ⇔ ELEGIVEL

    @property
    def resultado(self) -> Resultado: ...   # derivado das pendências

    @property
    def elegivel(self) -> bool: ...
```

## Estado e encerramento

### `estado(campanha, *, agora: datetime | None = None) -> EstadoCampanha`

Derivado de `aberta_em`, `encerrada_em`, `fim` e da data de referência
([data-model](../data-model.md#estado-observável-derivado)), nesta precedência:

1. encerramento explícito → `ENCERRADA`;
2. data de referência posterior a `fim` → `ENCERRADA`, tenha havido abertura ou não;
3. abertura → `EM_COLETA`;
4. demais casos → `EM_PREPARACAO`.

Abertura e encerramento explícito só valem a partir do momento em que ocorreram: com
`agora` anterior a `aberta_em`, a Campanha ainda estava em preparação; com `agora`
anterior a `encerrada_em`, ainda estava em coleta. Responde às perguntas da
005 "esta Campanha está aceitando coleta nesta data?" (`EM_COLETA`) e "está encerrada?"
(`ENCERRADA`). Não grava nada.

### `encerramento(campanha, *, agora: datetime | None = None) -> tuple[FormaEncerramento, datetime] | None`

`None` se a Campanha não está ENCERRADA. Caso contrário, devolve a forma e o momento
efetivo:

- `EXPLICITA`: o momento é `encerrada_em`;
- `FIM_DO_PERIODO`: o momento é o fim do dia `fim` (início do dia seguinte) na
  timezone configurada do projeto. Vale também para Campanha nunca aberta; se houve
  coleta, o consumidor verifica `campanha.aberta_em`.

## Elegibilidade

### `avaliar(campanha, conclusao) -> Elegibilidade`

Função pura sobre as duas instâncias, sem acesso ao banco e sem data (FR-025). Ela não
depende do estado da Campanha, de outras Conclusões da Pessoa, de outras Campanhas, de
Participação ou de convite. Regras na [tabela do data-model](../data-model.md#elegibilidade-valor-não-persistido):

- conjunção de todos os critérios definidos; igualdade exata nos conjuntos (FR-020,
  FR-022);
- uma pendência por critério não atendido, na ordem de `Criterio`, com `NAO_INFORMADO`
  quando o atributo é `NULL` e `NAO_ATENDE` caso contrário (FR-026, FR-028);
- ano mínimo e máximo formam um único critério, `ANO_CONCLUSAO` (FR-027);
- Campanha de população ampla: sempre `ELEGIVEL`, sem pendências (FR-019).

## População

### `populacao_no_momento(campanha) -> QuerySet[ConclusaoAcademica]`

Conclusões Acadêmicas existentes **agora** que satisfazem os critérios (FR-031, FR-032).
Para contar, use `.count()`. Vale para qualquer estado da Campanha. O resultado:

- muda quando novas Conclusões são incorporadas;
- conta Conclusões, não Pessoas (FR-033);
- não é denominador histórico oficial (DP-408);
- não é guardado em lugar nenhum.

Garantia de consistência: para toda Conclusão `c`, `c ∈ populacao_no_momento(campanha)`
⇔ `avaliar(campanha, c).elegivel`.

## Campanhas aplicáveis e contrato com a 005

### `admite_participacao(campanha, conclusao, *, agora: datetime | None = None) -> bool`

`estado(campanha, agora=agora) is EM_COLETA and avaliar(campanha, conclusao).elegivel`
(FR-053). É condição **necessária**: a 005 pode acrescentar condições, como uma ou várias
Participações por Conclusão na mesma Campanha. Não consulta convite, envio nem
destinatário (FR-048).

### `campanhas_em_coleta_para(conclusao, *, agora: datetime | None = None) -> tuple[Campanha, ...]`

Todas as Campanhas EM_COLETA na data de referência em que a Conclusão é ELEGÍVEL: zero,
uma ou várias (FR-051, FR-052). A ordem `(inicio, id)` é determinística e **não**
significa preferência. Não há prioridade, ranking, "mais recente" nem exclusividade
(DP-404). É a base para uma futura URL institucional permanente resolver a Campanha sem
convite.
