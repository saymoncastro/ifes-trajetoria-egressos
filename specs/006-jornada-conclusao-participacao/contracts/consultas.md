# Contrato: consulta da jornada

Módulo: `trajetoria.participacao.consultas`. Atende FR-047 a FR-050 e FR-040. As consultas
da 005 (`localizar_participacao`, `participacoes_da_conclusao`, `respostas_atuais`)
continuam iguais; `admite_escrita` passa a considerar a conclusão.

Nenhuma consulta grava nada, monta HTML, ViewModel, progresso ou percentual (FR-049).
Todas valem em qualquer estado da Campanha e da Participação.

## `situacao_da_jornada(participacao, *, agora=None) -> SituacaoDaJornada`

Lê, uma vez cada: a Participação (do banco, para `concluida_em` atual), a Versão aplicada
(`conteudo_da_versao`) e as Respostas (`respostas_atuais`). Toda a I/O fica aqui: monta
`respondidas` e entrega as estruturas já carregadas a `percorrer`
([percurso.md](percurso.md)), que é puro. Não recalcula nada em funções separadas.

**Leitura consistente.** Participação e Respostas são lidas numa transação, com a linha da
Participação em `FOR NO KEY UPDATE`: a consulta espera uma conclusão ou escrita em andamento
e nunca devolve um estado misturado. Nada é gravado.

**Leitura histórica — sem gate temporal.** A consulta funciona em qualquer estado da
Campanha (EM PREPARAÇÃO não ocorre com Participação; EM COLETA; ENCERRADA, há dias ou há
anos). O percurso é reconstruído **somente** pela Versão histórica da Campanha e pelas
Respostas preservadas; a data atual nunca o redefine. O estado temporal da Campanha é
gate de criação, escrita e conclusão, não de leitura:

- para Participação **concluída**, a consulta **não** consulta o estado da Campanha nem
  usa `agora`: `admite_escrita` é falso e `impedimentos` é vazio pela conclusão, não pela
  data. Uma Participação concluída em 2027 devolve, em 2030, as mesmas passagens, o mesmo
  `concluida_em` e as mesmas Respostas;
- para Participação **em rascunho**, `agora` só informa `admite_escrita` e o impedimento
  `COLETA_NAO_ADMITIDA`; passagens, pendências e `fora_do_percurso` não dependem dele.

```python
@dataclass(frozen=True)
class SituacaoDaJornada:
    participacao: Participacao
    concluida_em: datetime | None
    passagens: tuple[Passagem, ...]        # percurso determinado, na ordem
    finalizada: bool
    secao_atual: ConteudoSecao | None      # None ⇔ finalizada
    respostas: dict[UUID, Resposta]        # todas as atuais (005), ativas e inativas
    fora_do_percurso: frozenset[UUID]      # Perguntas com Resposta inativa
    impedimentos: tuple[Violacao, ...]     # o que impediria concluir agora
    admite_escrita: bool

    @property
    def pode_concluir(self) -> bool:       # concluida_em is None and not impedimentos
```

| Campo | Regra | FR-047 |
|-------|-------|--------|
| `concluida_em` | da Participação relida | b |
| `passagens` | `percorrer(conteudo, respondidas)`; cada passagem traz a Seção (com Perguntas na ordem), as pendentes e o destino | c, d |
| `finalizada`, `secao_atual` | `finalizada(passagens)`; senão, a Seção da última passagem | e |
| `respostas` | `respostas_atuais` (005); o valor de cada Pergunta está na coluna do seu tipo | c |
| `fora_do_percurso` | chaves de `respostas` que não estão em `perguntas_do_percurso(passagens)` | f |
| `impedimentos` | vazio se concluída (sem consultar a Campanha); senão `COLETA_NAO_ADMITIDA` (se a Campanha não está EM_COLETA em `agora`) + `pendencias(passagens)` | g |
| `admite_escrita` | falso se concluída (sem consultar a Campanha); senão Campanha EM_COLETA em `agora` | h |

**Estrutura não suportada** (FR-016, FR-047 i): a consulta rejeita com
`ParticipacaoRejeitada(ESTRUTURA_NAO_SUPORTADA)`, identificando a Seção — não há percurso
válido a devolver.

**Coerência das Respostas** (FR-045) é verificada só na conclusão (research R10):
`impedimentos` pode estar vazio e a conclusão ainda rejeitar uma Resposta gravada fora das
operações.

**Participação concluída** (FR-048): o percurso derivado é o final; `finalizada` é
verdadeiro, `fora_do_percurso` é vazio (as inativas foram removidas na conclusão),
`impedimentos` é vazio, `admite_escrita` é falso e `pode_concluir` é falso — em qualquer
data e qualquer estado da Campanha.

**Origem dos dados** (FR-050): `respostas` são declaradas; contexto acadêmico continua em
`participacao.conclusao` (institucional), nunca usado no percurso.

## `admite_escrita(participacao, *, agora=None) -> bool` — alterada

Participação inexistente → `False`. Senão, `concluida_em` relido do banco é nulo **e** `estado(participacao.campanha, agora=agora) is
EM_COLETA` (avaliado só quando não concluída). Verdadeiro não reserva nada: a escrita
verifica de novo, sob bloqueio.

## Uso pela futura interface

| Pergunta | Resposta |
|----------|----------|
| Qual Seção apresentar? | `situacao.secao_atual` (ou encerramento, se `finalizada`) |
| Quais Perguntas mostrar? | `situacao.secao_atual.perguntas` (todas, na ordem) |
| Quais respostas existem? | `situacao.respostas`, filtrando as do percurso, se preciso |
| A Seção pode avançar? | `situacao.passagens[-1].satisfeita` |
| Qual o próximo destino? | `situacao.passagens[-1].destino` (Seção, `FINALIZACAO` ou `INDETERMINADA`) |
| Revisar Seções anteriores? | `situacao.passagens[:-1]` |
| Há respostas guardadas de outro ramo? | `situacao.fora_do_percurso` |
| Pode concluir? | `situacao.pode_concluir`; motivos em `situacao.impedimentos` |
| Concluir | `operacoes.concluir(participacao, agora=…)` |
| Retomar | `iniciar_participacao` (005) → `situacao_da_jornada` |
