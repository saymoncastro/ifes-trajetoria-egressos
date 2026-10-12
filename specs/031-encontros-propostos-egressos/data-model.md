# Modelo de dados — Feature 031

Três modelos novos no app `trajetoria/portal`, com uma migração aditiva. Nenhuma chave
estrangeira para o núcleo; chaves internas à camada só para o Encontro (research R2). Por
que cada fato existe: spec, "Fatos novos e por que existem".

## Encontro (`portal_encontro`)

| Campo | Tipo | Regra | Requisito |
|---|---|---|---|
| `id` | UUID | chave; vai no endereço da página | FR-022 |
| `pessoa_id` | UUID | organizador; obrigatório; sem FK | FR-001 |
| `conclusao_origem_id` | UUID | Conclusão da Pessoa, verificada na escrita | FR-002 |
| `origem_curso`, `origem_unidade`, `origem_ano` | texto, texto, inteiro | copiados da Conclusão no envio e em cada reenvio (R3) | FR-024; ADR 0010 |
| `nome_apresentacao` | texto | 1 a 40 caracteres | FR-002; ADR 0010 |
| `titulo` | texto | 1 a 90 | FR-002 |
| `descricao` | texto | 1 a 400 | FR-002 |
| `inicio`, `termino` | data e hora com fuso | mesmo dia; `termino` > `inicio`; até 3 h | FR-002; R4 |
| `publico_unidades`, `publico_niveis`, `publico_cursos` | lista de texto ou `NULL` | como a Oportunidade: `NULL` = critério ausente; nunca `[]` nem `""` | FR-004; R6 |
| `link` | texto | validação da 025; até 500 | FR-003; R7 |
| `versao_do_termo` | texto | obrigatório | FR-006; XVII |
| `enviado_em` | data e hora | obrigatório | FR-010 |
| `primeira_publicacao_em` | data e hora ou nulo | preenchido uma vez | FR-010 |
| `publicado_em`, `publicado_por` | data e hora, texto (operador opaco) | a última publicação, em par | FR-015 |
| `publicado_por_escopo` | texto | com `publicado_em`: `institucional` (CPAEG) ou a unidade da CSAEG que publicou; a página diz quem moderou a partir dele | FR-024 |
| `recusado_em`, `recusado_por`, `recusado_por_escopo` | idem, e o escopo de quem recusou | em trio; só sem publicação; a página diz quem recusou (code review do PR #67) | FR-017 |
| `retirado_em`, `retirado_por` | idem | em par; só depois de publicado | FR-017 |
| `motivo`, `complemento` | texto (`choices`), texto | só com recusa ou retirada; complemento até 300, obrigatório com `outro` | FR-017 |
| `cancelado_em` | data e hora ou nulo | só pelo organizador, antes do início | FR-009 |
| `reenviado_em`, `campos_alterados` | data e hora, lista de texto | mudança substancial depois da publicação | FR-008 |
| `data_alterada_em`, `link_atualizado_em` | data e hora ou nulo | correções operacionais | FR-008; FR-027 |

**Situação** (derivada; `regras.situacao(encontro, agora)`; FR-010). Avaliada nesta ordem:

| Ordem | Situação | Condição |
|---|---|---|
| 1 | Cancelado | `cancelado_em` |
| 2 | Retirado | `retirado_em` |
| 3 | Recusado | `recusado_em` |
| 4 | Em revisão depois de uma alteração | `publicado_em` e `reenviado_em` > `publicado_em` e `agora` < `inicio` |
| 5 | Alteração não analisada a tempo | `publicado_em` e `reenviado_em` > `publicado_em` e `agora` ≥ `inicio` |
| 6 | Encerrado | `publicado_em` e `agora` ≥ `termino` |
| 7 | Publicado | `publicado_em` e `agora` < `termino` |
| 8 | Em análise | sem `publicado_em` e `agora` < `inicio` |
| 9 | Não analisado a tempo | sem `publicado_em` e `agora` ≥ `inicio` |

**Ativo** (limite de 3, R9): Em análise, Em revisão ou Publicado.

**Transições** (só por `encontros/operacoes.py`):

| Ação | De | Para | Quem |
|---|---|---|---|
| propor | — | Em análise | Pessoa com Conclusão, abaixo do limite |
| editar | Em análise | Em análise | organizador |
| publicar | Em análise; Em revisão | Publicado | moderação no escopo |
| recusar | Em análise | Recusado | moderação no escopo |
| recusar alteração | Em revisão | Retirado (motivo) | moderação no escopo |
| retirar | Publicado; Em revisão | Retirado | moderação no escopo |
| corrigir data | Publicado, antes do início | Publicado (`data_alterada_em`) | organizador |
| corrigir link, mesmo domínio | Publicado, antes do início | Publicado (`link_atualizado_em`) | organizador |
| alterar | Publicado, antes do início | Em revisão (`reenviado_em`, `campos_alterados`) | organizador |
| cancelar | Em análise; Publicado; Em revisão; antes do início | Cancelado | organizador |

## Confirmação (`portal_confirmacao`)

| Campo | Tipo | Regra | Requisito |
|---|---|---|---|
| `id` | UUID | chave | — |
| `encontro` | FK → Encontro, `PROTECT` | interna à camada (R2) | FR-020 |
| `pessoa_id` | UUID | sem FK; Pessoa com Conclusão | FR-020 |
| `versao_da_ciencia` | texto | obrigatório | FR-020; XVII |
| `confirmada_em` | data e hora | obrigatório | FR-020 |
| `cancelada_em` | data e hora ou nulo | só antes do início | FR-023 |

- **Unicidade parcial:** uma ativa por (`encontro`, `pessoa_id`) com `cancelada_em IS NULL`.
- Confirmar exige Encontro Publicado antes do início. O organizador não confirma o próprio
  encontro, porque já vê o link (FR-021).
- **Contagem:** confirmações sem `cancelada_em`. Só o organizador e a moderação a veem
  (FR-025).
- **Nunca exportada** (FR-032).

## Denúncia (`portal_denuncia`)

| Campo | Tipo | Regra | Requisito |
|---|---|---|---|
| `id` | UUID | chave | — |
| `encontro` | FK → Encontro, `PROTECT` | interna à camada | FR-029 |
| `pessoa_id` | UUID | só para unicidade e "Você denunciou…"; **nunca exibido** | FR-029; spec, tabela da Denúncia |
| `motivo` | texto (`choices`) | lista fechada (H-3107) | FR-029 |
| `complemento` | texto | opcional; até 300 | FR-029 |
| `denunciada_em` | data e hora | obrigatório | FR-029 |

- **Unicidade:** uma por (`encontro`, `pessoa_id`).
- **Sem situação, atribuição ou resposta.** A moderação lê as denúncias na análise do
  encontro.

## Leituras do núcleo (sem escrita)

- **Pessoa:** sessão da 018.
- **ConclusaoAcademica:** curso, nível, unidade e ano, para propor (origem), descobrir
  (pertinência) e ver a explicação.
- **VinculoDeGovernanca:** moderação.

`ContatoDaPessoa`, Participação, Resposta e Formação Declarada não são lidos.
