# Data Model: Jornada de resposta e conclusão da Participação

**Feature**: [spec.md](spec.md) | **Research**: [research.md](research.md)

Uma única alteração persistida: o campo `concluida_em` em `Participacao`. Nenhum modelo
novo. Nenhuma alteração em `Resposta`, `RespostaOpcao` nem em modelos das Features 001 a
004. O restante da feature é comportamento derivado (R1, R3).

```text
Participacao (005)                          ConteudoVersao (002, leitura imutável)
  id · campanha · conclusao                   Seções em ordem
  iniciada_em                                  ├─ encaminhamento_id
  concluida_em  ◄── NOVO (anulável)            └─ Perguntas em ordem
  │                                                 ├─ obrigatoria
  └─ Resposta 0..N (005, inalterada)                └─ Opções ─ regra (destino | finaliza)
         │
         └──────────────┐            ┌─────────────────┘
                        ▼            ▼
      percorrer(conteudo, respondidas)  →  passagens  (puro; derivado, nunca gravado)
```

## Participacao (alterada)

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | UUID | sim | 005, inalterado |
| `campanha` | FK → `campanha.Campanha` | sim | 005, inalterado |
| `conclusao` | FK → `academico.ConclusaoAcademica` | sim | 005, inalterado |
| `iniciada_em` | data e hora | sim | 005, inalterado |
| `concluida_em` | data e hora | **não** | **Novo.** `NULL` = em rascunho; preenchido = concluída (FR-001). Gravado uma única vez, por `concluir`, com o momento de referência da conclusão aceita (FR-003, FR-004). Nunca alterado nem apagado |

**Restrições**: as da 005, inalteradas (`UNIQUE (campanha, conclusao)`). Nenhum CHECK novo
(R2).

**Estado derivado** (sem coluna — FR-002):

| `concluida_em` | Situação | Escrita de Resposta | `concluir` |
|----------------|----------|---------------------|------------|
| `NULL` | em rascunho | regras da 005 (coleta admitida) | avalia e conclui ou rejeita |
| preenchido | concluída | rejeitada (`PARTICIPACAO_CONCLUIDA`) | `JA_CONCLUIDA`, nada muda |

**Migração**: `trajetoria/participacao/migrations/0002_participacao_concluida_em.py`, com um
único `AddField` anulável. Aditiva e reversível; Participações existentes ficam em
rascunho (Princípio XXVII).

**Não existe**: `estado`, `concluida` (booleano), `submetida_em`, `secao_atual`,
`posicao`, `progresso`, `atualizada_em`, momento por Seção ou por Resposta, histórico de
conclusão (FR-005).

## Resposta e RespostaOpcao (inalteradas)

Mesmas colunas e restrições da 005. Nenhuma coluna `ativa`, `apresentada`,
`fora_do_percurso` ou `ramo` (FR-030). Mudanças apenas de comportamento:

- depois de `concluida_em`, nenhuma operação registra, substitui ou remove Resposta
  (FR-038);
- na conclusão aceita, as Respostas fora do percurso final são removidas; suas seleções
  de escolha múltipla saem pelo `CASCADE` já existente (R7).

## Valores derivados (não persistidos)

Definidos em [contracts/percurso.md](contracts/percurso.md) e
[contracts/consultas.md](contracts/consultas.md). São valores imutáveis de leitura, no
padrão de `ConteudoVersao` (002) e `Elegibilidade` (004). Não são entidades.

| Valor | Conteúdo | Origem |
|-------|----------|--------|
| `Saida` | `FINALIZACAO`, `INDETERMINADA` | enumeração do destino que não é Seção |
| `Passagem` | `secao` (`ConteudoSecao`), `pendentes` (ids de Perguntas obrigatórias sem Resposta), `destino` (id de Seção ou `Saida`) | uma Seção do percurso determinado |
| `SituacaoDaJornada` | Participação, `concluida_em`, `passagens`, `finalizada`, `secao_atual`, `respostas`, `fora_do_percurso`, `impedimentos`, `admite_escrita`, `pode_concluir` | resposta única às perguntas de FR-047 |

## Ciclo de vida

```text
                       iniciar (005)
(não existe) ─────────────────────────────► RASCUNHO (concluida_em NULL)
                                              │  responder_* / remover_resposta (005):
                                              │    Campanha EM_COLETA; qualquer Pergunta
                                              │    da Versão; percurso não restringe
                                              │
                                              │  concluir(agora):
                                              │    Campanha EM_COLETA
                                              │    Versão suportada
                                              │    jornada finalizada, sem pendências
                                              │    Respostas ativas coerentes
                                              │    → remove inativas; concluida_em ← agora
                                              ▼
                                           CONCLUÍDA (concluida_em preenchido)
                                              │  concluir → JA_CONCLUIDA (nada muda)
                                              │  responder_* / remover → PARTICIPACAO_CONCLUIDA
                                              │  iniciar (005) → JA_EXISTENTE
                                              └─ nenhuma transição de saída (FR-039)
```

Campanha encerrada: rascunho continua rascunho, sem conclusão possível e sem alteração
automática; concluída continua concluída (FR-042).

**Leitura histórica**: o estado temporal da Campanha controla criação, escrita e
conclusão, nunca leitura. Participação concluída é reconstruída pela Versão histórica e
pelas Respostas preservadas, em qualquer data, sem consultar a Campanha (FR-042, FR-048;
research R18).

## Invariantes e onde são garantidos

| Invariante | Operação | Banco |
|------------|:--------:|:-----:|
| `concluida_em` gravado uma vez, nunca alterado (FR-003) | ✓ (só `concluir` escreve; idempotente) | — |
| Rascunho/concluída derivado de um campo (FR-002) | ✓ | coluna anulável |
| Nenhuma escrita de Resposta após a conclusão (FR-038) | ✓ (`_escrever`, sob bloqueio) | — |
| Concluída contém só Respostas do percurso final (FR-032) | ✓ (`DELETE … exclude` na mesma transação) | `CASCADE` de `RespostaOpcao` |
| Conclusão rejeitada não altera nada (FR-044) | ✓ (validação antes de qualquer escrita; `transaction.atomic`) | — |
| Um `concluida_em` sob concorrência (FR-043) | ✓ (`select_for_update(of=("self",))`) | — |
| Percurso só pela Versão aplicada e respostas (FR-006–FR-008) | ✓ (`percorrer` puro, sem acesso a Conclusão ou a outra Participação) | — |
| Nada da jornada é persistido (FR-005, FR-018) | ✓ | nenhuma coluna ou tabela nova além de `concluida_em` |
| Modelos 001–004 inalterados (FR-053) | ✓ | — |

## Fora do modelo (deliberadamente)

Jornada, EstadoJornada, Sessão, Tentativa, Passo persistido, Transição, Submissão,
Progresso, Percurso persistido, RespostaAtiva, cursor, grafo, cache de percurso,
snapshot, evento, histórico de ramos ou de conclusão; colunas `estado`, `ativa`,
`secao_atual`, `submetida_em`.
