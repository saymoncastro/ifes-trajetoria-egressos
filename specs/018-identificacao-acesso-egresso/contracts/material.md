# Contrato — fonte acadêmica e importação do material

## Extensão da fronteira de dados acadêmicos (001)

`trajetoria/fonte_academica/contrato.py`:

```text
PessoaEncontrada(
    id_externo: str,
    nome: str | None,
    conclusoes: tuple[ConclusaoNaFonte, ...],
    cpf: str | None = None,             # repr=False
    data_nascimento: date | None = None,  # repr=False
)
```

| Regra | Origem |
| --- | --- |
| `cpf`, quando presente, tem exatamente 11 dígitos (forma canônica); senão, `ValueError` | 001 FR-023 (forma canônica na fronteira) |
| Cadeia vazia é proibida, como em todos os campos do contrato | 001 |
| O dígito verificador **não** é validado pelo contrato: CPF legado inválido é dado da fonte | research R4 |
| `cpf` e `data_nascimento` não aparecem em `repr` | FR-013 |
| A implementação da fonte DEVE entregar como **uma** `PessoaEncontrada` os registros que ela permita associar ao mesmo indivíduo (por exemplo, matrículas com o mesmo CPF), cada Conclusão com sua própria referência | FR-021 |
| `ConclusaoNaFonte`, `PessoaInexistente`, `obter_conclusao` e `FonteAcademicaIndisponivel` | Inalterados |

`FonteSimulada` repassa `cpf` e `data_nascimento` de `PessoaSimulada`, com os valores de
research R13, documentados na tabela "Dados de verificação — fictícios" de
`specs/001-nucleo-academico-fonte-simulada/contracts/cenarios-simulados.md`.

## Incorporação acadêmica (001), sem mudança de comportamento

`trajetoria/academico/incorporacao.py`:

| Função | Contrato |
| --- | --- |
| `incorporar_pessoa(fonte, id_externo)` | Inalterada: obtém, incorpora e sinaliza divergências. Ignora `cpf` e `data_nascimento` |
| `incorporar_encontrada(codigo, resposta) -> ResultadoIncorporacao` | **Nova, extraída.** É exatamente o trecho atual, dentro da transação, depois de obter `PessoaEncontrada`. Não abre a transação: quem chama abre. Devolve as divergências sem registrá-las |

## Importação com material (018)

`trajetoria/acesso/material.py`:

```text
incorporar_com_material(fonte, id_externo) -> ResultadoIncorporacao
```

| Passo | Contrato |
| --- | --- |
| 1 | `chaves_de_acesso()`. `ChavesInvalidas` é propagada **antes** de consultar a fonte ou gravar (US5.5) |
| 2 | `fonte.obter_pessoa(id_externo)`, com o mesmo tratamento de `incorporar_pessoa` para `PessoaInexistente`, resposta fora do contrato e `FonteAcademicaIndisponivel` |
| 3 | `transaction.atomic()`: `incorporar_encontrada(...)`; se `resultado.pessoa` existir, `registrar_material(pessoa, resposta.cpf, resposta.data_nascimento, chaves, agora)` |
| 4 | Depois do commit, registra as divergências acadêmicas (como a 001) e os sinais do material |

```text
registrar_material(pessoa, cpf, data, chaves, agora) -> list[SinalDoMaterial]
```

Aplica a tabela de research R6. "Igual" ou "diferente" é decidido pelas derivações,
nunca por valor guardado. Atualiza `atualizado_em` só quando há mudança.

`SinalDoMaterial` (para log; sem valores):

| Tipo | Quando | Campos |
| --- | --- | --- |
| `CPF_INUTILIZAVEL` | CPF presente com dígito verificador inválido ou dígitos iguais | — |
| `ALTERADO` | Material substituído | `("cpf",)` ou `("data_nascimento",)` |
| `AUSENTE_NA_FONTE` | Material existente e campo ausente na carga | `("cpf",)` ou `("data_nascimento",)` |
| `COLISAO` | Outra Pessoa com o mesmo identificador depois da gravação | — |

Cada sinal é registrado com a referência `fonte:id_externo` da Pessoa (como a 001) e o
nome dos campos. Nunca com CPF, data, identificador ou verificador.

**Invariantes:**

- **Sem valores em claro.** Nenhum valor em claro é atribuído a modelo, sessão, cache ou
  log.
- **Fidelidade da extração.** Pessoa e Conclusões incorporadas por
  `incorporar_com_material` são idênticas às de `incorporar_pessoa` para a mesma resposta.
- **Pessoa não materializada.** Se `incorporar_encontrada` não materializa a Pessoa (sem
  conclusão elegível, 001 FR-039), não há material.
- **Idempotência.** Reexecutar com a mesma resposta não altera nada.

## Preparo da demonstração

`demonstracao/cenario.preparar()` usa `incorporar_com_material` para cada
`cenarios.PESSOAS`. `ChavesInvalidas` vira `PreparoRecusado` com o texto: "As chaves de
acesso não estão configuradas. Defina TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO e
TRAJETORIA_CHAVE_ACESSO_VERIFICACAO (valores distintos, com pelo menos 32 caracteres)." As
demais recusas do preparo continuam iguais.
