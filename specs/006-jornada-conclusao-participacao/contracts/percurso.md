# Contrato: derivação do percurso

Módulo: `trajetoria.participacao.percurso`. Atende FR-006 a FR-021, FR-025 a FR-027 e
FR-030. Consumido por `consultas.situacao_da_jornada` e por `operacoes.concluir`.

## Pureza

O módulo é regra de domínio sem I/O:

- **não** acessa o ORM: não busca Participação, Versão, Seção, Pergunta, Opção nem
  Resposta, e não executa query;
- **não** chama `conteudo_da_versao` (002), `respostas_atuais` (005) nem qualquer
  consulta ou operação Django;
- **não** conhece Campanha, Conclusão, relógio ou outra Participação.

Quem chama (`consultas.py`, `operacoes.py`) carrega os dados e entrega estruturas já em
memória: a árvore imutável da 002 (`ConteudoVersao` e seus `ConteudoSecao`,
`ConteudoPergunta`, `ConteudoOpcao`, `RegraNavegacao`, reutilizados sem cópia nem árvore
paralela) e um mapeamento simples das respostas atuais. O módulo importa apenas esses
tipos (`trajetoria.instrumento.conteudo`) e o vocabulário de rejeição
(`trajetoria.participacao.regras`). Por isso seus testes constroem `ConteudoVersao` em
memória e rodam sem banco.

Nomes de funções e tipos são a proposta do plan; a assinatura exata pode ser ajustada nas
tasks sem mudar o comportamento.

## Tipos

```python
class Saida(Enum):
    FINALIZACAO = "finalizacao"      # o percurso termina ao deixar a Seção
    INDETERMINADA = "indeterminada"  # Pergunta com regra obrigatória ainda sem Resposta

@dataclass(frozen=True)
class Passagem:
    secao: ConteudoSecao                  # da Versão aplicada (002, conteudo_da_versao)
    pendentes: tuple[UUID, ...]           # Perguntas obrigatórias da Seção sem Resposta,
                                          # na ordem da Seção
    destino: UUID | Saida                 # id da Seção seguinte ou Saida

    @property
    def satisfeita(self) -> bool:         # not pendentes
```

## `percorrer(conteudo: ConteudoVersao, respondidas: Mapping[UUID, UUID | None]) -> tuple[Passagem, ...]`

- `conteudo`: árvore da Versão aplicada, já carregada por quem chama
  (`conteudo_da_versao(participacao.versao)`).
- `respondidas`: `id` da Pergunta → `id` da Opção escolhida, para cada Pergunta com
  Resposta atual. O valor é a Opção em escolha única e `None` nos demais tipos. Presença
  da chave = Pergunta respondida. Quem chama o monta a partir de `respostas_atuais`
  (005): `{pergunta_id: resposta.opcao_id for …}`. Nenhum objeto do ORM entra no
  cálculo.

### 1. Suporte da Versão (FR-016)

Se alguma Seção de `conteudo` tem mais de uma Pergunta com regra (Pergunta com ao menos uma
Opção com `regra`), rejeita com `ParticipacaoRejeitada`, uma `Violacao` por Seção:

| Motivo | Campo | Detalhe |
|--------|-------|---------|
| `ESTRUTURA_NAO_SUPORTADA` | `"secao"` | `id` da Seção e quantas Perguntas com regra ela tem |

Sem precedência, sem escolha da primeira ou da última, sem combinação. Nada é modificado.

### 2. Percurso

```text
S ← primeira Seção de conteudo
repetir:
    pendentes ← Perguntas de S com obrigatoria e sem chave em respondidas
    destino   ← destino(S)
    acrescenta Passagem(S, pendentes, destino)
    se pendentes ou destino ∈ {FINALIZACAO, INDETERMINADA}: parar
    S ← Seção de id destino
```

### 3. `destino(S)` — precedência (FR-012; 002 FR-048 a FR-054)

| # | Condição | Destino |
|---|----------|---------|
| 1 | S tem Pergunta com regra X, X respondida, Opção respondida tem regra | `regra.destino_secao_id` ou `FINALIZACAO` se `regra.finaliza` |
| 2 | X existe, é obrigatória e não tem Resposta | `INDETERMINADA` |
| 3 | S tem `encaminhamento_id` | `encaminhamento_id` |
| 4 | existe Seção seguinte na ordem | `id` da seguinte |
| 5 | — | `FINALIZACAO` |

Casos que caem em 3–5: S sem Pergunta com regra; Opção respondida sem regra; X opcional
sem Resposta. Se a Opção registrada para X em `respondidas` é `None` (`VALOR_VAZIO`) ou não é Opção de X (só possível fora das
operações), rejeita com `OPCAO_DE_OUTRA_PERGUNTA` (`campo="pergunta"`, `id` de X no
detalhe), em vez de escolher um destino.

### Garantias

- **Seção como unidade** (FR-010, FR-011): toda Pergunta de uma Seção de uma passagem
  pertence ao percurso; a regra só decide o destino da passagem. Em S11 da baseline, Q46,
  Q47 e Q48 são lidas para pendências antes de qualquer desvio.
- **Inatividade por construção** (FR-030): só Perguntas da Seção da passagem são lidas.
  Respostas a Perguntas de Seções fora das passagens não satisfazem, não geram
  pendência, não decidem destino.
- **Determinismo** (FR-017): mesmo `conteudo` e mesmo `respondidas` ⇒
  tuplas iguais (`==`).
- **Término** (FR-015): a Versão aplicada é PUBLICADA, então todo destino é Seção
  posterior (002 FR-055, FR-059 d). Sem detecção de ciclo.
- **Sem dado institucional** (FR-007): a função não recebe Conclusão nem Participação.
- **Sem tempo** (FR-006, FR-017): nada depende da data atual nem do estado da Campanha; o
  mesmo conteúdo com as mesmas respostas reconstrói o mesmo percurso em qualquer data.
- **Sem regra especial** para Q1, Q46 ou Q51 (FR-022, FR-026): tudo sai da tabela acima.

## Funções auxiliares sobre as passagens

Puras, sem I/O; usadas pela consulta e pela conclusão para não recalcular o
percurso.

| Função | Resultado |
|--------|-----------|
| `finalizada(passagens) -> bool` | última passagem satisfeita com destino `FINALIZACAO` |
| `perguntas_do_percurso(passagens) -> frozenset[UUID]` | `id` de todas as Perguntas das Seções das passagens |
| `respondidas(respostas) -> dict[UUID, UUID \| None]` | converte o dicionário de `respostas_atuais` (carregado por quem chama) em `respondidas`, lendo só `opcao_id`; sem I/O |
| `pendencias(passagens) -> tuple[Violacao, ...]` | se não finalizada, uma `OBRIGATORIA_PENDENTE` (`campo="pergunta"`, `id` da Pergunta e da Seção no detalhe) por Pergunta de `passagens[-1].pendentes`; senão, vazio |

`pendencias` nunca tem item de Seção anterior (satisfeitas por construção) nem de Seção
posterior (ainda não determinada) — R8.

## Baseline (Versão equivalente)

| Respostas | Passagens (Seções) | Última passagem |
|-----------|--------------------|-----------------|
| nenhuma | S1 | pendente Q1; destino `INDETERMINADA` |
| Q1 = "Não" | S1 | destino `FINALIZACAO` → finalizada |
| Q1 = "Sim", S2 completa, Q10 vazia | S1, S2, S3 | pendente Q10 (e Q14, se vazia → `INDETERMINADA`) |
| … S8 com Q33 = "Não" | …, S8, S10, … | S9 nunca aparece |
| … S11 com Q46 = "Não", Q47 vazia | …, S11 | pendente Q47; destino S13 já conhecido |
| … S11 com Q46 = "Sim", Q47 respondida, Q48 vazia | …, S11, S12, … | Q48 nunca é pendente |
| percurso completo | um dos 17 percursos da 003 | destino `FINALIZACAO` |
