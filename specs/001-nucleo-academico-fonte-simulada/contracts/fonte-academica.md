# Contrato: Fronteira de dados acadêmicos

Conceito constitucional: `AcademicDataProvider` (Princípio V). Atende FR-021 a FR-025.

O contrato fica num pacote Python puro (`trajetoria.fonte_academica.contrato`), que não
importa Django nem qualquer fonte concreta. Os nomes abaixo são os adotados por este
plan. As assinaturas indicam forma, não implementação.

## Operações

```python
class FonteAcademica(Protocol):
    codigo: str          # identifica a fonte na proveniência; não vazio (a simulada usa "simulada")

    def obter_pessoa(self, id_externo: str) -> PessoaEncontrada | PessoaInexistente: ...
    def obter_conclusao(self, id_externo: str) -> (
        ConclusaoEncontrada | RegistroNaoReconhecidoComoConclusao | ConclusaoInexistente
    ): ...
```

Qualquer operação PODE lançar `FonteAcademicaIndisponivel`. São só duas operações. Nada
mais é acrescentado sem caso de uso concreto.

## Objetos transportados (imutáveis)

```python
ConclusaoNaFonte(
    id_externo: str,
    curso: str | None, unidade: str | None, nivel: str | None,
    modalidade: str | None, forma_oferta: str | None,
    ano_conclusao: int | None, data_conclusao: date | None,
)

PessoaEncontrada(id_externo: str, nome: str | None,
                 conclusoes: tuple[ConclusaoNaFonte, ...])
PessoaInexistente(id_externo: str)

ConclusaoEncontrada(conclusao: ConclusaoNaFonte, id_externo_pessoa: str)
RegistroNaoReconhecidoComoConclusao(id_externo: str)
ConclusaoInexistente(id_externo: str)

class FonteAcademicaIndisponivel(Exception): ...
```

## Regras que toda implementação DEVE cumprir

1. `PessoaEncontrada.conclusoes` contém **somente** registros que a fonte reconhece como
   formação concluída (PAEG Art. 3º). O critério de reconhecimento é interno à
   implementação. Para a fonte real, ele depende de DP-008.
2. Uma pessoa conhecida sem conclusão reconhecida é `PessoaEncontrada` com
   `conclusoes == ()`, e não `PessoaInexistente`.
3. `obter_conclusao` sobre um registro existente e não reconhecido devolve
   `RegistroNaoReconhecidoComoConclusao`, nunca `ConclusaoInexistente`.
4. Atributo não fornecido é `None`. Cadeia vazia é proibida. Nenhum valor é deduzido
   de outro (por exemplo, a modalidade não vem do nome do curso).
5. Se `data_conclusao` vier preenchida, `ano_conclusao` DEVE estar preenchido e ser o ano
   dessa data. Só o ano significa granularidade anual.
6. Falha de acesso, tempo esgotado ou erro interno DEVEM lançar
   `FonteAcademicaIndisponivel`. Uma falha nunca vira resultado vazio ou parcial.
7. Os identificadores externos são opacos e estáveis para o mesmo registro. Códigos,
   tabelas e vocabulário próprios da fonte ficam dentro da implementação.
8. A mesma consulta à mesma fonte, sem mudança na fonte, devolve resultado igual. A
   ordem de `conclusoes` é determinística.

## Verificação

Uma suíte de contrato única (`tests/test_contrato_fonte.py`) é executada contra toda
implementação: hoje, a fonte simulada e uma implementação alternativa que existe só nos
testes. Uma implementação real futura DEVE passar na mesma suíte, alimentada pelos casos
que ela mesma declara.
