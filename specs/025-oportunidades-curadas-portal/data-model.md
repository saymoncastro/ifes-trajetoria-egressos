# Data model — Feature 025

Há uma entidade nova, **Oportunidade**, no app `portal` (camada de relacionamento). Ela não
tem chave estrangeira para tabelas do núcleo, e nenhuma tabela existente muda.

## Oportunidade (`portal_oportunidade`)

| Campo | Tipo | Nulo | Regra | Requisito |
|---|---|---|---|---|
| `id` | UUID, PK | não | Gerado. No catálogo fictício, `uuid5` fixo (idempotência) | — |
| `titulo` | texto | não | 1 a 120 caracteres, sem só espaços; exibido sempre como texto | FR-002 |
| `resumo` | texto | não | 1 a 300 caracteres; texto simples | FR-002 |
| `categoria` | texto, lista fechada | não | `cursos`, `eventos`, `pesquisa_extensao`, `carreira`, `empreendedorismo`, `outras` | FR-003; DP-2505 |
| `unidade_responsavel` | texto | não (padrão `""`) | `""` = "Ifes (institucional)"; senão, a designação textual da unidade (DP-1005) | FR-005 |
| `endereco` | texto | não | Validação do R6 | FR-004 |
| `inicio` | data | não | ≤ `fim` | FR-006 |
| `fim` | data | não | ≥ `inicio` | FR-006 |
| `publico_unidades` | lista de texto | sim | `NULL` = critério ausente; nunca `[]` nem `""` | FR-007 |
| `publico_niveis` | lista de texto | sim | idem | FR-007 |
| `publico_cursos` | lista de texto | sim | idem | FR-007 |
| `publicada_em` | data e hora | sim | Preenchida só por `publicar` | FR-030, FR-033 |
| `publicada_por` | texto | sim | Identificador opaco do operador; presente se, e só se, há `publicada_em` | FR-033 |
| `retirada_em` | data e hora | sim | Preenchida só por `retirar`; ≥ `publicada_em` quando ambas existem | FR-031, FR-033 |
| `retirada_por` | texto | sim | Presente se, e só se, há `retirada_em` | FR-033 |

**Sem** coluna de estado, autor do cadastro, histórico, imagem, ordem nem contador.

**Restrições no banco (`CheckConstraint`),** no padrão da Campanha (004):
- título e resumo não vazios;
- tamanhos máximos de 120 e 300 caracteres;
- categoria na lista;
- `inicio <= fim`;
- cada lista de público é `NULL` ou tem pelo menos 1 item, sem `""`;
- pares (`publicada_em`, `publicada_por`) e (`retirada_em`, `retirada_por`) preenchidos juntos;
- `retirada_em >= publicada_em` quando ambas existem.

A validação do endereço (R6) e as regras que dependem de tempo ou escopo ficam em
`operacoes.py`.

**Ordenação do modelo:** `["-inicio", "titulo", "id"]`, só para determinismo. A ordem do
egresso é a da R7.

## Estado derivado (não gravado)

| Estado | `publicada_em` | `retirada_em` | Datas (hoje = data local do projeto) |
|---|---|---|---|
| Rascunho | — | — | quaisquer |
| Agendada | ✓ | — | hoje < `inicio` |
| Em divulgação | ✓ | — | `inicio` ≤ hoje ≤ `fim` |
| Encerrada | ✓ | — | hoje > `fim` |
| Retirada | qualquer | ✓ | quaisquer |

## Operações (único caminho de escrita: `portal/oportunidades/operacoes.py`)

| Operação | De | Para | Validações | Grava |
|---|---|---|---|---|
| `cadastrar(dados, operador, escopo, hoje)` | — | Rascunho | FR-002 a FR-007; unidade responsável no escopo (FR-026) | Todos os campos de conteúdo |
| `editar(id, dados, operador, escopo, hoje)` | Rascunho, Agendada, Em divulgação | o mesmo, ou Agendada ⇄ Em divulgação conforme as datas | As mesmas. Se publicada, `fim >= hoje` (FR-029) | Campos de conteúdo |
| `publicar(id, operador, escopo, agora)` | Rascunho | Agendada ou Em divulgação | `fim >= hoje` (FR-030) | `publicada_em`, `publicada_por` |
| `retirar(id, operador, escopo, agora)` | Rascunho, Agendada, Em divulgação | Retirada | — | `retirada_em`, `retirada_por` |

- **Concorrência.** Cada operação lê a linha com `select_for_update` e revalida o estado e o
  escopo. Estado incompatível vira `OportunidadeRejeitada(Motivo.ESTADO)`, que a view mostra
  como conflito (FR-034).
- **Escopo.** A CSAEG só opera se `unidade_responsavel` está nas suas unidades. A CPAEG opera
  em qualquer uma. O público é livre (FR-026; DP-2502).

## Leituras

| Consulta | Usada por | Lê |
|---|---|---|
| `em_divulgacao(hoje)` | Página do egresso, bloco do Início | `portal_oportunidade` |
| `pertinentes(oportunidades, conclusoes)` (função pura) | Página e Início | Conclusões da Pessoa (já ordenadas) |
| `da_curadoria(escopo)` | Lista do operador | `portal_oportunidade`, filtrada por `unidade_responsavel` |
| `opcoes_de_publico()` | Formulário | Valores distintos de `academico_conclusaoacademica` (`curso`, `nivel`, `unidade`) |

O egresso **não** lê Resposta, Formação Declarada, contato, Campanha nem Participação (FR-011;
teste por consultas, como na 024).
