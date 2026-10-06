# Data Model — Feature 023

Nenhum modelo, tabela, coluna ou migração. Há um valor transitório, uma leitura derivada e
um campo de leitura acrescentado a um valor existente.

## Envio pendente (transitório)

Registro no armazenamento de sessões, separado da sessão do sujeito (research R1).

| Campo | Tipo | Regra |
|---|---|---|
| `participacao` | UUID (texto) | Do endereço da Seção enviada |
| `posicao` | inteiro | Posição da Seção na Versão (endereço) |
| `dados` | `{campo: [texto]}` | Só `p<n>`, `p<n>-complemento`, `p<n>-remover` das Perguntas da Seção; cada valor com até 2 000 caracteres |
| `em` | instante ISO 8601 | Momento do envio |

Ponteiro: a sessão do navegador guarda só `pendente.envio` = chave do registro.

**Ciclo de vida**

```text
(sem sujeito) POST de Seção ──guardar──▶ GUARDADO (validade 30 min)
GUARDADO ──confirmação de outro sujeito / "Sair" / validade──▶ DESCARTADO
GUARDADO ──o dono abre a Seção──▶ RESTAURADO (tela preenchida, nada gravado)
RESTAURADO ──envio aceito daquela Seção──▶ DESCARTADO (Respostas gravadas pela 005)
GUARDADO|RESTAURADO ──Seção fora do percurso / Participação concluída / coleta encerrada──▶ DESCARTADO
```

Invariantes: nunca contém CPF, data ou material de verificação; nunca vai à URL nem à tela
de confirmação de dados; nunca grava Resposta; existe no máximo um por navegador.

## Parte e máximo restante (derivado, não persistido)

| Valor | Regra |
|---|---|
| `parte` | Índice da passagem da Seção exibida no percurso determinado (006) + 1 |
| `maximo_restante` | `percurso.maximo_restante(conteudo, secao_id)`: maior número de Seções depois da exibida no grafo da Versão (research R8) |
| Rótulo de Seção sem título | `"Parte {parte}"` |

## `SituacaoDaJornada` (006) — campo acrescentado

| Campo | Tipo | Observação |
|---|---|---|
| `conteudo` | `ConteudoVersao` | A árvore já carregada por `situacao_da_jornada`; só leitura |

## Inalterados

Pessoa, Conclusão Acadêmica, Formação Declarada, Campanha, Pesquisa, Versão, Seção,
Pergunta, Opção, Participação, Resposta, material de verificação, selos.
