# Contrato: regra de acompanhamento da coleta (Feature 011 sobre a 010)

Acréscimo a `trajetoria/governanca/regras.py`. As três regras da 010 não mudam. Nenhum
modelo, campo, papel, operação ou migration da governança muda.

## Símbolos novos

```text
@dataclass(frozen=True)
class EscopoDeAcompanhamento:
    institucional: bool
    unidades: frozenset[str]

def pode_acompanhar_coleta(vinculos) -> bool
def escopo_de_acompanhamento(vinculos) -> EscopoDeAcompanhamento | None
```

`__all__` passa a ter cinco regras/funções e o dataclass.

## Semântica (explícita por atuação)

| Vínculos ativos do operador | `pode_acompanhar_coleta` | `escopo_de_acompanhamento` |
|-----------------------------|:------------------------:|----------------------------|
| nenhum (ou só inativos) | `False` | `None` |
| CSAEG {A} | `True` | `(False, {A})` |
| CSAEG {A}, CSAEG {B} | `True` | `(False, {A, B})` |
| CPAEG | `True` | `(True, ∅)` |
| CPAEG + CSAEG {A} | `True` | `(True, ∅)` |
| CPAEG inativo + CSAEG {A} ativo | `True` | `(False, {A})` |

Regras de implementação:

- As duas funções **nomeiam** `Papel.CPAEG` e `Papel.CSAEG`. Nenhuma usa "qualquer
  vínculo ativo", e um papel não listado não concede acompanhamento.
- Vínculo inativo é ignorado mesmo se recebido.
- As funções são puras: só recebem `vinculos`; não leem banco, requisição, settings,
  modo de demonstração nem marca técnica (010 FR-005, FR-067).
- A unidade é usada **somente** em `escopo_de_acompanhamento`. As três regras da 010
  continuam sem usá-la (010 FR-017).
- Invariante: `pode_acompanhar_coleta(v) == (escopo_de_acompanhamento(v) is not None)`.

Fundamentação na docstring: PAEG Art. 21, I e III (CPAEG, âmbito do Ifes); Art. 22, I e
IV (CSAEG, nas unidades; aplicar o questionário). Interpretação operacional B1 a B4 da
spec 011. Não é competência autônoma, não concede gestão de Campanha nem acesso a dado
individual.

## Testes da 010 atualizados

- `tests/governanca/test_governanca_regras.py`:
  - acrescenta a matriz acima;
  - acrescenta o invariante;
  - verifica que a assinatura tem só `vinculos`;
  - verifica a independência do modo de demonstração;
  - atualiza `regras.__all__`.
- `tests/governanca/test_governanca_fronteiras.py`: a docstring "três regras" passa a
  "três regras do editor e a regra de acompanhamento". Os nomes novos não contêm termos
  proibidos (`capab`, `permission`, `policy`, `admin`, …).
- `tests/editor/test_editor_autorizacao.py`: inalterado. O editor continua aceitando só
  as três regras.
