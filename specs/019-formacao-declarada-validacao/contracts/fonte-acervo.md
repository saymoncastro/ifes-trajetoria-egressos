# Contrato: fonte acadêmica de acervo histórico

Adaptador `declaracao.acervo.FonteAcervoHistorico`. Implementa o protocolo
`FonteAcademica` (`fonte_academica/contrato.py`), o mesmo da fonte simulada e da futura
fonte real (Princípio V).

O adaptador fica em `declaracao` porque só a validação produz Referências, com a mesma
capacidade e sem ciclo de vida próprio (research R1). `fonte_academica` continua Python
puro, como a 001 definiu. Trocar o acervo por uma fonte digital (DP-1911) é trocar o
adaptador passado à incorporação. Os testes de contrato da fonte (`tests/test_contrato_fonte.py`) passam a
incluí-lo.

## Registro

A operação é `declaracao.acervo.registrar_referencia(dados, *, operador, agora)` →
`ReferenciaDeAcervo`.

**Campos.**
- Obrigatórios: `unidade`, `referencia`, `nivel`, `curso` e `ano_conclusao`.
- Opcionais: `modalidade`, `forma_oferta` e `data_conclusao`, só quando o acervo informar.
  Se houver data, o ano coincide.

**Unicidade e convergência.**
- A chave é `(unidade, referencia)`, com espaços normalizados.
- Mesma chave e mesmos valores: devolve a existente.
- Mesma chave e valores diferentes: levanta `ReferenciaDivergente`.

**Imutável.** Não há edição nem exclusão (DP-1905).

## Leitura pela fronteira

| Chamada | Resposta |
| --- | --- |
| `codigo` | `"acervo_historico"` |
| `obter_pessoa("acervo:<uuid>")` | `PessoaEncontrada(id_externo="acervo:<uuid>", nome=None, cpf=None, data_nascimento=None, conclusoes=(ConclusaoNaFonte(id_externo="<uuid>", unidade, nivel, curso, modalidade, forma_oferta, ano_conclusao, data_conclusao),))` |
| `obter_pessoa(outro)` | `PessoaInexistente` |
| `obter_conclusao("<uuid>")` | `ConclusaoEncontrada(conclusao, id_externo_pessoa="acervo:<uuid>")` ou `ConclusaoInexistente` |

## O que a fonte não faz

- **Não entrega CPF nem data.** A Pessoa do acervo não ganha material de acesso (DP-1909).
- **Não agrupa referências diferentes numa Pessoa** e não associa a Pessoas de outras
  fontes (FR-084).
- **Não lê a Formação Declarada.** O dado da fonte é só o que o operador registrou como
  encontrado no acervo (FR-013, FR-082).

## Demonstração

- A barreira `base_somente_simulada` admite as fontes `simulada` e `acervo_historico`
  (FR-131).
- A fonte de acervo começa vazia.
