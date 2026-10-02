# Data Model: Governança, papéis e escopos institucionais

**Feature**: 010 | **Spec**: [spec.md](spec.md) | **Research**: [research.md](research.md)

## 1. Resumo

| Item | Quantidade |
|------|-----------|
| Entidades novas | **1** — `VinculoDeGovernanca` |
| Enumerações novas | 1 — `Papel` (`CPAEG`, `CSAEG`) |
| Entidades existentes alteradas | **0** |
| Migrações | 1, aditiva (`governanca/0001_initial`) |
| Migrações de dados | 0 (vínculos fictícios só pelo preparo da demonstração e por testes) |

Não existem: Operador, Usuário, Conta, Identidade, Credencial, Papel como tabela,
Permissão, Papel-Permissão, Escopo, Unidade, Organização, Tenant, Política, ACL, registro
de auditoria, histórico do vínculo.

## 2. `Papel` (enumeração, `TextChoices`)

| Valor | Rótulo na interface |
|-------|---------------------|
| `CPAEG` | Comissão Própria de Acompanhamento do Egresso (CPAEG) |
| `CSAEG` | Comissão Setorial de Acompanhamento de Egressos (CSAEG) |

Lista fechada (spec FR-010, FR-013). Os rótulos seguem a PAEG (Art. 16; Art. 18, III).
O valor em código nunca aparece na interface; só o rótulo.

## 3. `VinculoDeGovernanca` (app `trajetoria.governanca`)

Registro administrativo de que um operador atua institucionalmente. Reflete designação
feita fora do sistema e **não** a verifica (spec FR-065; DP-1002). Não é dado sobre o
egresso.

| Campo | Tipo | Nulo | Regra |
|-------|------|------|-------|
| `id` | UUID, chave primária, padrão `uuid4` | não | Padrão do projeto |
| `identificador_operador` | texto | não | Opaco; não vazio; sem espaços nas pontas (operação) |
| `papel` | texto, `Papel.choices` | não | `CPAEG` ou `CSAEG` |
| `unidade` | texto, padrão `""` | **não** | Vazia (`""`) se CPAEG; não vazia e sem espaços nas pontas se CSAEG. Mesma designação textual da fonte acadêmica e dos critérios de Campanha; sem catálogo nem normalização (DP-1005) |
| `ativo` | booleano, padrão verdadeiro | não | Responde só "este vínculo concede autorização agora?" |

**Sem** nome, e-mail, CPF, matrícula, credencial, datas de vigência, portaria, documento,
observação, autor, carimbo de criação ou alteração (spec FR-009, FR-026;
Clarifications).

**Escopo derivado, não persistido**: CPAEG ⇒ institucional; CSAEG ⇒ unidade `unidade`.
A propriedade de leitura `rotulo_de_atuacao` monta o texto exibido:

- CPAEG → "Comissão Própria de Acompanhamento do Egresso (CPAEG) — atuação institucional";
- CSAEG → "Comissão Setorial de Acompanhamento de Egressos (CSAEG) — unidade {unidade}".

### Restrições de banco

Todas locais à linha. Sem trigger e sem dependência de outra tabela.

| Nome | Tipo | Expressão |
|------|------|-----------|
| `vinculo_identificador_nao_vazio` | CHECK | `NOT (identificador_operador = '')` |
| `vinculo_papel_valido` | CHECK | `papel IN ('CPAEG', 'CSAEG')` |
| `vinculo_unidade_conforme_papel` | CHECK | `(papel = 'CPAEG' AND unidade = '') OR (papel = 'CSAEG' AND NOT (unidade = ''))` |
| `vinculo_unico` | UNIQUE | `(identificador_operador, papel, unidade)` |

Como `unidade` nunca é nula, a unicidade vale diretamente para CPAEG
(`unidade = ''`), sem recurso específico de nulo do PostgreSQL.

`Meta.ordering`: `["identificador_operador", "papel", "unidade"]`, só determinismo.

### Ciclo de vida

```text
            registrar_vinculo                    desativar_vinculo
(inexistente) ─────────────▶ ATIVO ◀──────────────────────────▶ INATIVO
                               ▲      registrar_vinculo (reativa)  │
                               └───────────────────────────────────┘
```

- Sem exclusão como fluxo normal. Nenhuma operação apaga.
- Sem outro estado. `ativo` não é framework de exclusão lógica: é só a condição da
  autorização.
- Efeito imediato: a próxima requisição consulta os vínculos atuais (spec FR-024).

## 4. Operações (`trajetoria.governanca.operacoes`)

Contrato completo em [contracts/governanca.md](contracts/governanca.md).

| Operação | Efeito | Rejeições |
|----------|--------|-----------|
| `registrar_vinculo(identificador, papel, unidade="")` | Cria ativo; ou reativa a mesma linha se inativa | `IDENTIFICADOR_INVALIDO`, `PAPEL_INVALIDO`, `UNIDADE_EXIGIDA`, `UNIDADE_PROIBIDA`, `UNIDADE_INVALIDA`, `JA_ATIVO` |
| `desativar_vinculo(vinculo)` | Ativo → inativo | `JA_INATIVO` |

Tudo-ou-nada: rejeição não grava nada. Cada operação roda em `transaction.atomic()` e
trava a linha (`select_for_update`) quando ela existe.

## 5. Consulta e regras

| Função | Módulo | Natureza | Retorno |
|--------|--------|----------|---------|
| `vinculos_ativos(identificador)` | `consultas` | 1 consulta; 0 se `identificador` for `None` ou vazio | lista de vínculos ativos, em ordem |
| `pode_consultar_publicado(vinculos)` | `regras` | pura | algum vínculo **ativo** |
| `pode_consultar_rascunho(vinculos)` | `regras` | pura | algum vínculo **ativo** CPAEG |
| `pode_elaborar_instrumento(vinculos)` | `regras` | pura | algum vínculo **ativo** CPAEG |

Matriz resultante (spec, "Matriz mínima de capacidades"):

| Vínculos ativos | publicado | rascunho | elaborar |
|-----------------|:---------:|:--------:|:--------:|
| nenhum | não | não | não |
| CSAEG (uma ou mais unidades) | sim | não | não |
| CPAEG | sim | sim | sim |
| CPAEG + CSAEG | sim | sim | sim |

Publicar: inexistente para todos.

## 6. Valores sem persistência

- **Operador identificado**: `str | None` devolvido pela identificação
  (`demonstracao.operador.operador_em_uso` nesta feature). Nunca gravado além do vínculo.
- **Atuação resolvida da requisição**: vínculos ativos e os três resultados das regras,
  anexados à requisição pelo gate do editor para as páginas. Calculada a cada
  requisição.
- **Operadores fictícios**: tupla fixa no código do adaptador de demonstração
  (`OPERADORES_FICTICIOS`), com identificador e rótulo de apresentação. Não é tabela.
- **Operador fictício em uso**: cookie assinado do navegador, só no modo de
  demonstração, revalidado contra a tupla a cada requisição.

## 7. Origem dos dados

| Dado | Origem | Observação |
|------|--------|-----------|
| `papel`, `unidade` | Registro administrativo de designação externa | Não verificado pelo sistema (DP-1002) |
| `ativo` | Registro administrativo | — |
| `identificador_operador` | Identificação (fictícia nesta feature) | Correspondência com identidade institucional: DP-1001 |
| Capacidades | Derivado | Regras puras sobre vínculos ativos |

## 8. Migração

`trajetoria/governanca/migrations/0001_initial.py`: cria a tabela e as quatro restrições.
Aditiva, sem dados, sem efeito sobre tabelas existentes, reversível por migração para
`zero` (Const. XXVII).
