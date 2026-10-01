# Contrato: Incorporação e leitura do núcleo acadêmico

Interface que as próximas features do NIAE consomem. Atende FR-015, FR-016, FR-031 a
FR-033 e FR-039.

## Incorporação

```python
def incorporar_pessoa(fonte: FonteAcademica, id_externo_pessoa: str) -> ResultadoIncorporacao
```

A fonte é recebida como argumento. Não há configuração global nem registro de fontes.

```python
ResultadoIncorporacao(
    situacao: SituacaoIncorporacao,      # INCORPORADA | SEM_CONCLUSAO_ELEGIVEL | PESSOA_INEXISTENTE
    pessoa: Pessoa | None,               # Pessoa do NIAE, quando existir
    pessoa_criada: bool,
    conclusoes_criadas: tuple[ConclusaoAcademica, ...],
    conclusoes_existentes: tuple[ConclusaoAcademica, ...],
    divergencias: tuple[Divergencia, ...],
)

Divergencia(tipo: TipoDivergencia, registro: Literal["pessoa", "conclusao"],
            fonte: str, id_externo: str, campos: tuple[str, ...])
# TipoDivergencia: ATRIBUTOS_DIFERENTES | CONCLUSAO_DE_OUTRA_PESSOA | AUSENTE_NA_FONTE
```

### Comportamento

| A fonte devolve | Já existe no NIAE? | Efeito | `situacao` |
|-----------------|--------------------|--------|------------|
| `PessoaEncontrada` com ≥ 1 conclusão | não | Cria a Pessoa e as Conclusões | `INCORPORADA` |
| `PessoaEncontrada` com ≥ 1 conclusão | sim | Cria só as conclusões novas e devolve as existentes, sem alterá-las | `INCORPORADA` |
| `PessoaEncontrada` sem conclusões | não | Nada é persistido (FR-039) | `SEM_CONCLUSAO_ELEGIVEL` |
| `PessoaEncontrada` sem conclusões | sim | Nada é alterado; as conclusões já incorporadas viram divergências `AUSENTE_NA_FONTE` | `SEM_CONCLUSAO_ELEGIVEL` |
| `PessoaInexistente` | não | Nada é persistido | `PESSOA_INEXISTENTE` |
| `PessoaInexistente` | sim | Nada é alterado; a Pessoa vira divergência `AUSENTE_NA_FONTE` | `PESSOA_INEXISTENTE` |
| exceção `FonteAcademicaIndisponivel` | — | Nada é persistido nem alterado; a exceção é propagada sem conversão | — |

### Divergências (FR-033)

Uma divergência é detectada quando:

- **`ATRIBUTOS_DIFERENTES`**: algum atributo de uma Pessoa ou Conclusão já incorporada
  difere do que a fonte devolveu, inclusive o nome (presente ↔ ausente também conta).
- **`CONCLUSAO_DE_OUTRA_PESSOA`**: a fonte devolve, para esta pessoa, uma conclusão já
  incorporada para outra Pessoa. A conclusão não é reatribuída nem duplicada.
- **`AUSENTE_NA_FONTE`**: uma conclusão já incorporada desta Pessoa não está entre as
  conclusões reconhecidas devolvidas, ou a própria Pessoa não existe mais na fonte.

Em todos os casos:

- nenhuma linha é atualizada ou removida;
- nenhuma duplicata é criada;
- a divergência aparece no resultado e num aviso de log (tipo, fonte, `id_externo` e
  nomes de campos, sem valores pessoais);
- nada sobre a divergência é persistido.

Resolução, fila, painel e aprovação ficam fora do escopo (DP-005, DP-006).

### Garantias

- **Idempotente**: repetir a chamada com a fonte inalterada não cria linhas e devolve as
  mesmas identidades internas.
- **Atômica**: a escrita ocorre em uma transação; a consulta à fonte ocorre antes dela.
- **Unicidade garantida pelo banco**: as restrições de unicidade decidem a criação, e
  quem perde uma eventual corrida reutiliza o registro existente. É uma garantia
  estrutural, sem teste dedicado de concorrência nesta feature (proporcional ao risco).
- A deduplicação usa somente (fonte, `id_externo`). Nome e demais atributos nunca são
  usados (FR-005, FR-031).

## Leitura pelos consumidores

Os consumidores leem diretamente os modelos `Pessoa` e `ConclusaoAcademica`, que formam a
interface de leitura do núcleo:

- **Trajetória acadêmica**: `pessoa.conclusoes`, em ordem determinística e sem
  significado de domínio (FR-015, FR-017).
- **Contexto de uma conclusão**: `ConclusaoAcademica` obtida por `id`, com
  `conclusao.pessoa` (FR-016).
- **Atributo ausente**: `None` significa "não informado pela fonte" (FR-010). Nunca é
  valor padrão nem inferido.
- **Proveniência**: `fonte`, `id_externo` e `incorporado_em` em ambos. `fonte = "simulada"`
  identifica a fonte simulada (FR-035).

Os consumidores NÃO DEVEM consultar a fonte acadêmica diretamente para obter contexto
já incorporado, nem conhecer qual fonte concreta está em uso (SC-008).
