# Contrato: `trajetoria.governanca`

App de domínio novo. Atende spec FR-001 a FR-035, FR-062 a FR-068. Nomes são proposta do
plan; as tasks podem ajustá-los sem mudar comportamento.

## Módulos

| Módulo | Conteúdo público |
|--------|------------------|
| `models.py` | `Papel`, `VinculoDeGovernanca` ([data-model](../data-model.md) §2–§3) |
| `regras.py` | `pode_consultar_publicado`, `pode_consultar_rascunho`, `pode_elaborar_instrumento` |
| `consultas.py` | `vinculos_ativos` |
| `operacoes.py` | `registrar_vinculo`, `desativar_vinculo`, `Motivo`, `VinculoRejeitado` |

Proibidos no app: `urls.py`, `views.py`, `admin.py`, `forms.py`, `middleware.py`,
`management/`, `templates/`. Proibidas importações de `django.contrib.auth`, de
`trajetoria.editor`, `trajetoria.demonstracao`, `trajetoria.interface` e de apps do
instrumento, da Campanha e da participação. Proibidas menções a `is_staff`,
`is_superuser`, `TRAJETORIA_DEMONSTRACAO` e nomes de publicação ou aprovação.

## Regras (`regras.py`)

Funções puras. Único parâmetro: `vinculos`, um iterável de `VinculoDeGovernanca`
(gravados ou não). Não acessam banco, requisição, settings ou relógio.

```text
pode_consultar_publicado(vinculos)  = any(v.ativo for v in vinculos)
pode_consultar_rascunho(vinculos)   = any(v.ativo and v.papel == Papel.CPAEG for v in vinculos)
pode_elaborar_instrumento(vinculos) = any(v.ativo and v.papel == Papel.CPAEG for v in vinculos)
```

- `pode_consultar_rascunho` e `pode_elaborar_instrumento` têm hoje o mesmo corpo, mas são
  regras distintas da spec (FR-028) e podem divergir por decisão futura (DP-1004).
- A unidade não participa de nenhuma regra (FR-017).
- Não existe regra de publicação (FR-033, FR-047).

## Consulta (`consultas.py`)

```text
vinculos_ativos(identificador: str | None) -> list[VinculoDeGovernanca]
```

- `None` ou `""` → `[]`, sem consulta ao banco.
- Caso contrário, uma consulta: `ativo=True` e `identificador_operador=identificador`,
  ordenados por `papel`, `unidade`.
- Não normaliza nem interpreta o identificador.

## Operações (`operacoes.py`)

Mecanismo técnico administrativo da spec (FR-062): usado por testes, pelo preparo da
demonstração e por quem opera o servidor (`manage.py shell`). **Não é processo oficial de
designação**: a docstring do módulo diz que o registro reflete designação feita fora do
sistema (portaria — PAEG Art. 17, Art. 18, III, Art. 24) e não a verifica (FR-065;
DP-1002).

### `registrar_vinculo(identificador: str, papel: Papel, unidade: str = "") -> VinculoDeGovernanca`

Validação, nesta ordem, antes de qualquer gravação:

| Condição | `Motivo` |
|----------|----------|
| `identificador` não é `str`, é vazio, só espaços ou tem espaços nas pontas | `IDENTIFICADOR_INVALIDO` |
| `papel` não é `Papel.CPAEG` nem `Papel.CSAEG` | `PAPEL_INVALIDO` |
| `unidade` não é `str` | `UNIDADE_INVALIDA` |
| `papel == CPAEG` e `unidade != ""` | `UNIDADE_PROIBIDA` |
| `papel == CSAEG` e `unidade.strip() == ""` | `UNIDADE_EXIGIDA` |
| `papel == CSAEG` e `unidade` com espaços nas pontas | `UNIDADE_INVALIDA` |

A unidade é gravada exatamente como informada: não há normalização (DP-1005).

Efeito, em `transaction.atomic()`, com `select_for_update` sobre a combinação:

| Situação da combinação (identificador, papel, unidade) | Resultado |
|--------------------------------------------------------|-----------|
| inexistente | cria com `ativo=True` |
| existente e inativa | `ativo=True` na mesma linha |
| existente e ativa | rejeição `JA_ATIVO`; nada muda |

Corrida entre duas criações simultâneas: a restrição `vinculo_unico` recusa a segunda;
a `IntegrityError` é convertida em `JA_ATIVO`.

### `desativar_vinculo(vinculo: VinculoDeGovernanca) -> None`

| Situação | Resultado |
|----------|-----------|
| ativo | `ativo=False` |
| inativo | rejeição `JA_INATIVO`; nada muda |

Relê a linha com `select_for_update` antes de decidir. Não apaga.

### Rejeição

```text
class Motivo(Enum): IDENTIFICADOR_INVALIDO, PAPEL_INVALIDO, UNIDADE_PROIBIDA,
                    UNIDADE_EXIGIDA, UNIDADE_INVALIDA, JA_ATIVO, JA_INATIVO
class VinculoRejeitado(Exception): motivo: Motivo
```

Não há operação de exclusão, troca de papel, troca de unidade nem edição de
identificador. Corrigir um vínculo é desativá-lo e registrar outro.

## O que não existe

Operador como modelo; papel ou permissão como tabela; escopo persistido; catálogo de
unidades; hierarquia; capacidade de publicar, aprovar, gerir Campanha ou consultar
respostas; histórico, autoria, datas, portaria; tela, rota ou comando de gestão.
