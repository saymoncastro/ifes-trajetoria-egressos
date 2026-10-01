# Contrato: situação de entrada e entrada na pesquisa

Módulo: `trajetoria.participacao.entrada` (novo). Atende FR-001 a FR-053. Consumido pelos
testes desta feature e, no futuro, pela fronteira de identidade e pela interface pública
de entrada (fora do escopo).

Nomes de funções, tipos e parâmetros são a proposta do plan. A assinatura exata pode ser
ajustada nas tasks sem mudar o comportamento descrito aqui.

## Dependências permitidas

| Importa | De | Para |
|---------|----|------|
| `Pessoa`, `ConclusaoAcademica` | `trajetoria.academico.models` (001) | tipos e leitura das Conclusões da Pessoa |
| `Campanha` | `trajetoria.campanha.models` (004) | tipo |
| `campanhas_em_coleta_para`, `momento_de_referencia` | `trajetoria.campanha.consultas` (004) | Campanhas aplicáveis e tempo |
| `Participacao` | `trajetoria.participacao.models` (005/006) | uma leitura dos pares (R4) |
| `iniciar_participacao`, `SituacaoInicio` | `trajetoria.participacao.operacoes` (005) | única escrita |

**Não importa** (regra de desenho conferida na revisão de código — T025 —, não por
teste de inspeção do código-fonte): `campanha.consultas.avaliar`/`estado`/`_filtro` para reavaliar
critérios; `campanha.operacoes`; `participacao.percurso`; `consultas.situacao_da_jornada`;
`concluir`; `fonte_academica`; `academico.incorporacao`; nada de `django.contrib.auth`,
sessão, cookie, request, URL ou view.

`entrada.py` não persiste modelo algum por conta própria: a única escrita possível é a de
`iniciar_participacao`. Isso é verificado por comportamento (consulta sem alteração de
linhas; dublê de `iniciar_participacao` que não grava não resulta em `Participacao`
nova), não por inspeção do código-fonte.

## Tipos

Cada estrutura tem consumidor e significado próprios; simplificações por YAGNI em
[data-model](../data-model.md#simplificações-por-yagni-em-relação-ao-primeiro-desenho-do-plan).

```python
class SituacaoDaFormacao(Enum):
    SEM_PESQUISA = "sem_pesquisa"
    DISPONIVEL_PARA_INICIAR = "disponivel_para_iniciar"
    DISPONIVEL_PARA_RETOMAR = "disponivel_para_retomar"
    JA_CONCLUIDA = "ja_concluida"
    AMBIGUIDADE_OPERACIONAL = "ambiguidade_operacional"

    @property
    def pendente(self) -> bool: ...                  # INICIAR ou RETOMAR

@dataclass(frozen=True)
class Formacao:
    conclusao: ConclusaoAcademica           # contexto lido daqui; None = não informado
    situacao: SituacaoDaFormacao
    campanhas: tuple[Campanha, ...]         # aplicáveis (004), ordem (inicio, id)
    participacao: Participacao | None       # só em RETOMAR e JA_CONCLUIDA

    @property
    def campanha(self) -> Campanha | None: ...       # a única, se len(campanhas) == 1

class ResolucaoDaEntrada(Enum):
    SEM_FORMACAO = "sem_formacao"
    SEM_PESQUISA = "sem_pesquisa"
    SEM_ENTRADA_PENDENTE = "sem_entrada_pendente"
    ENTRADA_RESOLVIDA = "entrada_resolvida"
    SELECAO_NECESSARIA = "selecao_necessaria"

@dataclass(frozen=True)
class SituacaoDeEntrada:
    formacoes: tuple[Formacao, ...]         # todas as Conclusões da Pessoa
    resolucao: ResolucaoDaEntrada

    @property
    def pendentes(self) -> tuple[Formacao, ...]: ... # resolvida = pendentes[0]

@dataclass(frozen=True)
class Entrada:
    situacao: SituacaoDeEntrada             # reavaliada no momento da entrada
    participacao: Participacao | None       # None ⇔ nada iniciado nem retomado
    criada: bool                            # a 005 devolveu CRIADA

class FormacaoDeOutraPessoa(Exception): ...
```

Indicações de FR-034, derivadas sem enum: **iniciada** = `criada`; **em rascunho** =
Participação presente, não `criada`, `concluida_em` nulo; **concluída** =
`participacao.concluida_em` preenchido; **não realizada** = `participacao is None`.

## `situacao_de_entrada(pessoa, *, agora=None) -> SituacaoDeEntrada`

Nunca grava (FR-024).

| # | Passo | Consultas |
|---|-------|-----------|
| 1 | `pessoa` que não é `Pessoa` → `TypeError`; `agora` inválido → `TypeError` (por `momento_de_referencia`) | — |
| 2 | `pessoa` não gravada → `ValueError` (FR-003) | 1 (`exists`) |
| 3 | `agora = momento_de_referencia(agora)` | — |
| 4 | Conclusões da Pessoa, na ordem padrão da 001 | 1 |
| 5 | Para cada Conclusão: `campanhas_em_coleta_para(conclusao, agora=agora)` | N (uma por Conclusão) |
| 6 | Pares com exatamente 1 Campanha: `Participacao.objects.filter(conclusao__in=…, campanha__in=…)`, indexadas por `(campanha_id, conclusao_id)`; omitida se não houver par | 0 ou 1 |
| 7 | Classificação por formação (pura; [data-model](../data-model.md#situacaodaformacao-enum)) | — |
| 8 | Resolução global (pura; [data-model](../data-model.md#resolucaodaentrada-enum)) | — |

Total: **3 + N** consultas no máximo, com N = número de Conclusões da Pessoa (R3, R4).
Verificado em teste com `django_assert_max_num_queries`.

Garantias:

- **Todas** as formações são devolvidas, inclusive `SEM_PESQUISA`, `JA_CONCLUIDA` e
  `AMBIGUIDADE_OPERACIONAL` (FR-017).
- Formações `JA_CONCLUIDA` e `AMBIGUIDADE_OPERACIONAL` não contam para
  `ENTRADA_RESOLVIDA`/`SELECAO_NECESSARIA` (FR-020 a FR-022).
- Em `AMBIGUIDADE_OPERACIONAL`, a Participação não é consultada nem informada; nenhuma
  Campanha é preferida (FR-025 a FR-027a).
- Em `SEM_PESQUISA`, nada sobre critérios ou pendências da 004 é exposto (FR-015).
- Nenhuma ordenação nova: formações na ordem da 001, Campanhas na da 004 (FR-011, FR-021,
  FR-026).
- Mesma entrada (Pessoa, `agora`, banco) ⇒ resultado igual.

## `entrar(pessoa, formacao=None, *, agora=None) -> Entrada`

Único ponto que pode resultar em gravação, e só por `iniciar_participacao` (FR-033,
FR-037). Nunca confia em consulta anterior: não há token nem snapshot da resolução.

| # | Passo | Resultado |
|---|-------|-----------|
| 1 | `formacao` informada que não é `ConclusaoAcademica` → `TypeError` | erro de uso |
| 2 | `situacao = situacao_de_entrada(pessoa, agora=momento_de_referencia(agora))` (reavaliada — FR-032) | erros de uso dos passos 1–2 da consulta |
| 3 | Sem `formacao`: `situacao.resolucao` ≠ `ENTRADA_RESOLVIDA` → `Entrada(situacao, None, False)`; senão `f = situacao.pendentes[0]` | nada criado |
| 4 | Com `formacao`: `f` = a formação de `situacao.formacoes` com o mesmo `pk`; se não houver → `FormacaoDeOutraPessoa`, seja de outra Pessoa, seja inexistente (mesma rejeição, sem consulta que distinga — FR-045) — **antes** de qualquer chamada à 005 | nada criado |
| 5 | `f.situacao` é `SEM_PESQUISA` ou `AMBIGUIDADE_OPERACIONAL` → `Entrada(situacao, None, False)` | nada criado nem retomado |
| 6 | `f.situacao` é `JA_CONCLUIDA` → `Entrada(situacao, f.participacao, False)`, sem chamar a 005 | nada criado nem alterado |
| 7 | `f.situacao.pendente` → `inicio = iniciar_participacao(f.campanha, f.conclusao, agora=agora)` (005; `agora` original, possivelmente `None`) | cria ou devolve a existente (inclusive concluída em paralelo) |
| 8 | `Entrada(situacao, inicio.participacao, inicio.situacao is SituacaoInicio.CRIADA)` | — |

No passo 7, a 005 recebe o `agora` **original**: sem `agora` explícito, ela lê o relógio
no instante do início, e não no da avaliação. `ParticipacaoRejeitada` da 005 (só por
mudança da Campanha entre a avaliação e o início) é propagada sem conversão (FR-046).

Garantias:

- **Sem seleção artificial**: com uma única formação pendente, a entrada procede sem
  `formacao`, mesmo com outras `JA_CONCLUIDA` ou ambíguas (FR-020, FR-030).
- **Ambiguidade local**: uma formação ambígua não impede a resolução da única pendente;
  continua ambígua em `situacao.formacoes`; nada dela é criado nem retomado (FR-027a).
- **Sem escolha inventada**: com 2+ pendentes, sem `formacao` nada é criado (FR-021).
- **Reavaliação**: encerramento de Campanha, nova Campanha que torna a formação ambígua ou
  Participação criada/concluída em outra requisição entre a consulta e a entrada são
  respeitados (FR-032).
- **Sem duplicação**: entradas repetidas ou simultâneas → uma Participação por par
  (005 FR-006).
- **Sem reabertura**: Participação concluída nunca é alterada (FR-035).
- **Longitudinal**: a Participação é sempre a do par (Campanha aplicável agora, Conclusão);
  Participações de Campanhas anteriores não são consultadas nem reutilizadas (FR-038).
- **Institucional ≠ declarado**: nenhuma `Resposta` é criada; nada da Conclusão é copiado
  (FR-040, FR-041).
- **Sem jornada**: não chama a 006; a Participação devolvida segue para
  `situacao_da_jornada` por quem chamar (FR-036).

## Uso pela futura interface (fora do escopo)

| Pergunta | Resposta |
|----------|----------|
| Quais formações mostrar? | `situacao.formacoes` (todas), com o contexto de `f.conclusao` |
| Sobre qual formação perguntar ("Sobre qual formação do Ifes você responderá esta pesquisa?")? | `situacao.pendentes`, quando `SELECAO_NECESSARIA` |
| Pode seguir direto? | `situacao.resolucao is ENTRADA_RESOLVIDA` → `entrar(pessoa)`; a formação é `situacao.pendentes[0]` |
| Já respondeu? | formações `JA_CONCLUIDA` |
| Há problema de configuração? | formações `AMBIGUIDADE_OPERACIONAL` (comunicação: DP-701) |
| Nada a fazer? | `SEM_FORMACAO`, `SEM_PESQUISA`, `SEM_ENTRADA_PENDENTE` |
| Depois de entrar | `situacao_da_jornada(entrada.participacao)` (006) |

Textos, telas, rótulos e ordem de apresentação pertencem à interface (FR-050; DP-702).
