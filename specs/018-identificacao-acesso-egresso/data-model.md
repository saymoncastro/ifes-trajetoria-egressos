# Data Model: Identificação e acesso do egresso por dados acadêmicos

**Feature**: [spec.md](spec.md) | **Research**: [research.md](research.md)

A feature cria **uma** entidade de domínio, o material de verificação, no novo app
`acesso`. Ela usa a tabela de sessão do framework e um cache transitório. Pessoa,
Conclusão, Participação e Resposta não mudam.

```text
Pessoa (001, inalterada) 1 ──── 0..1 MaterialDeVerificacao (acesso)
                                      identificador_cpf  (não único; colisão possível)
                                      verificador        (anulável)

Sessão do egresso (framework) ──► Pessoa.id      (só o UUID; técnica, transitória)
Contadores de limitação (cache) ──► chaves derivadas (técnicos, expiram sozinhos)
```

## MaterialDeVerificacao *(novo — `trajetoria.acesso`)*

| Campo | Tipo | Obrigatório | Origem | Regra |
| --- | --- | --- | --- | --- |
| `id` | UUID | sim | interno | Chave primária |
| `pessoa` | 1:1 → `academico.Pessoa` | sim | interno | Uma linha por Pessoa, no máximo. `PROTECT`; `related_name="+"`: a Pessoa não conhece o material (FR-016) |
| `identificador_cpf` | texto (64 hex) | sim | derivado | `HMAC(K_loc, "cpf:" + cpf11)`. Indexado. **Não único** (colisão, FR-025) |
| `verificador` | texto (64 hex) | não | derivado | `HMAC(K_ver, "cpf-nascimento:" + cpf11 + ":" + AAAA-MM-DD)`. `NULL` = a fonte não forneceu data, ou a data foi invalidada por troca de CPF (R6) |
| `atualizado_em` | data e hora | sim | técnico | Momento da última mudança do material. Serve de versão para invalidar sessões (FR-041). Inalterado quando a carga não muda nada |

**Restrições:**

- `UNIQUE (pessoa)`.
- `CHECK`: `identificador_cpf` e `verificador`, quando presentes, têm exatamente 64
  caracteres hexadecimais minúsculos.
- Nenhuma coluna guarda CPF, data ou outro valor em claro (FR-010).
- Não há `UNIQUE` em `identificador_cpf`.

**Estados derivados**, sem coluna de estado:

| Situação | Condição | Efeito no acesso |
| --- | --- | --- |
| Sem material | não há linha | `NAO_CONFIRMADA` |
| Só identificador | `verificador IS NULL` | `NAO_CONFIRMADA` |
| Completo | ambos presentes | Confirmável, se for o único com esse identificador |
| Em colisão | outra linha com o mesmo `identificador_cpf` | `NAO_CONFIRMADA` para esse CPF |

**Escrita**: somente por `acesso.material.registrar_material`, chamada dentro de
`incorporar_com_material`. A regra completa está em
[contracts/material.md](contracts/material.md) e em research R6. Nunca há remoção nem
histórico.

**Ciclo de vida:**

```text
(nenhum) ──carga com CPF utilizável──► só identificador | completo
só identificador ──carga traz data──► completo
completo ──carga com data diferente──► completo (verificador novo)
completo ──carga com CPF diferente e sem data──► só identificador (verificador anulado)
qualquer ──carga sem CPF / sem data──► inalterado (ausência não apaga)
```

## Sessão do egresso *(técnica — `django.contrib.sessions`)*

| Chave na sessão | Conteúdo | Uso |
| --- | --- | --- |
| `acesso.pessoa` | UUID da Pessoa | Única identificação |
| `acesso.confirmada_em` | instante ISO | Duração máxima |
| `acesso.ultimo_uso` | instante ISO | Inatividade; renovado no máximo uma vez por minuto |
| `acesso.versao_material` | `atualizado_em` do material, ISO, ou `null` | Invalidação quando o material muda (FR-041) |

**Vedado na sessão**: formação, Campanha, Participação, CPF, data, identificador e
verificador (FR-040).

**Duração**: a inatividade e o máximo vêm de `TRAJETORIA_SESSAO_INATIVIDADE` e
`TRAJETORIA_SESSAO_DURACAO_MAXIMA`, com padrões de 30 min e 8 h (FR-042). O cookie expira
ao fechar o navegador (`SESSION_EXPIRE_AT_BROWSER_CLOSE`). A tabela
`django_session` é do framework e é limpa com `clearsessions`.

## Contadores de limitação *(técnicos — cache `acesso`)*

| Chave | Valor | Expira |
| --- | --- | --- |
| `acesso:origem:<HMAC(K_loc, "origem:" + endereço)>` (`:inicio`, `:n`, `:ate`) | início da janela; número de submissões, descontadas as confirmações; instante até o qual a avaliação espera | 15 min fixos desde a primeira contagem |
| `acesso:cpf:<identificador_cpf>` (`:inicio`, `:n`, `:ate`, `:trava`) | início da janela; número de falhas de credencial; instante de espera; trava da verificação em andamento (10 s) | 60 min fixos desde a primeira contagem |

Os contadores não são registro de domínio nem trilha (FR-031). Os parâmetros ficam em
`TRAJETORIA_ACESSO_LIMITES` (research R8).

## Resultado da verificação *(conceito de contrato, não persistido)*

| Externo | Representação interna | Causa interna |
| --- | --- | --- |
| `CONFIRMADA` | `Confirmada(pessoa, versao_material)` | — |
| `NAO_CONFIRMADA` | `NaoConfirmada()` | **não representada** (FR-035) |
| `VERIFICACAO_INDISPONIVEL` | `Indisponivel(causa)` | `CHAVE_NAO_CONFIGURADA` · `LIMITE_TEMPORARIO` · `FALHA_TECNICA` |
| *(não é resultado)* | `FormatoInvalido(campos)` | Campos `cpf` e/ou `data_nascimento` |

## Mudanças em entidades e contratos existentes

| Onde | Mudança | Compatibilidade |
| --- | --- | --- |
| `fonte_academica.contrato.PessoaEncontrada` | `+ cpf: str \| None`, `+ data_nascimento: date \| None` (padrão `None`, `repr=False`); CPF presente exige 11 dígitos | Construções existentes continuam válidas |
| `fonte_academica.cenarios.PessoaSimulada` | Os mesmos dois campos, com os valores de research R13 | Contagens e registros inalterados |
| `academico.incorporacao` | `incorporar_encontrada(codigo, resposta)` extraída; `incorporar_pessoa` a usa | Sem mudança de comportamento |
| `academico.Pessoa`, `ConclusaoAcademica` | **Nenhuma** | — |
| `participacao.*`, `campanha.*`, `instrumento.*` | **Nenhuma** | — |

## Origem e categoria dos dados

| Dado | Categoria (Princípio III) | Persistido? |
| --- | --- | --- |
| CPF e data da fonte | Institucional | Não; só na pilha da incorporação |
| `identificador_cpf`, `verificador` | Derivado (técnico, de acesso); dado pessoal pseudonimizado (FR-015) | Sim, no material |
| CPF e data digitados | Dado de acesso; não é Resposta nem dado declarado | Não; só no corpo da requisição e na reapresentação do formulário |
| Sessão | Técnico | Sim, tabela do framework, com expiração |
| Contadores | Técnico | Não; cache transitório |
