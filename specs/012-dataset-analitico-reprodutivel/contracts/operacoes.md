# Contrato: operação de captura (Feature 012)

Módulo `trajetoria/analitico/operacoes.py`: **único caminho de escrita** do app. Vocabulário
de recusa em `trajetoria/analitico/regras.py`.

Nenhuma rota, view, endpoint, management command ou regra de governança chama esta
operação nesta feature (spec FR-100, FR-101). Quando houver exposição institucional, a
competência (CPAEG; spec FR-102) precisará ser aplicada por quem expuser.

## `capturar_snapshot(campanha) -> SnapshotAnalitico`

**Entrada**: uma `Campanha` gravada. Nenhum outro parâmetro; em particular, **nenhum
momento** (spec FR-016).

**Saída**: o `SnapshotAnalitico` criado, completo.

### Passos

Todos dentro de uma única `transaction.atomic()`.

1. `campanha` não é `Campanha` → `TypeError`, antes de qualquer acesso ao banco.
2. `capturado_em = momento_de_referencia(None)`: relógio do sistema, lido **uma vez**
   (004).
3. Releitura da Campanha pelo `pk` (inexistente → `ValueError`; atributos da instância
   recebida não são confiados).
4. Condição de captura, com o instante `capturado_em`:
   - `aberta_em is None` → `SnapshotRecusado(CAMPANHA_NUNCA_ABERTA)`, inclusive se
     ENCERRADA pelo fim do período;
   - `estado(campanha, agora=capturado_em) is not ENCERRADA` →
     `SnapshotRecusado(COLETA_NAO_ENCERRADA)`.
5. Versão relida; estado ≠ PUBLICADA → `CapturaInconsistente` (guarda de integridade;
   impossível pelas operações da 004; spec FR-053 b).
6. Universo (research R7):
   - população pela 004: `populacao_no_momento(campanha)` com `pk` e
     `CAMPOS_DE_CONTEXTO` → elegíveis;
   - Conclusões com Participação na Campanha, só pelo `pk`; o contexto é lido de novo
     somente das que não estão entre as elegíveis, que entram como não elegíveis;
   - união deduplicada por `pk` da Conclusão.
7. Criação do `SnapshotAnalitico(campanha, capturado_em)` e dos registros com um
   `bulk_create` (`batch_size` constante do módulo).
8. Verificação de integridade na mesma transação (spec FR-053 d): nenhuma Participação da
   Campanha cuja Conclusão não tenha registro no snapshot. O total de registros (FR-053 c)
   não é verificado à parte: o `bulk_create` grava todos ou levanta, e o
   `UNIQUE (snapshot, conclusao)` impede duplicata (ajuste da revisão de código de 2026-10-02).

   Falha → `CapturaInconsistente`.
9. Devolve o snapshot.

### Garantias

| Garantia | Como | Spec |
|----------|------|------|
| Tudo ou nada | Uma transação; qualquer exceção (recusa, inconsistência, erro de banco) desfaz cabeçalho e registros | FR-052 |
| Recusa não grava | Passos 4 e 5 antes do passo 6 | FR-014 |
| Corte histórico | Os valores efetivamente lidos e copiados; sem leitura isolada entre consultas, sem nível de isolamento nem lock adicional | FR-054 |
| Escrita concorrente iniciada antes do encerramento | Detectada pela verificação do passo 8; captura desfeita inteira, pode ser repetida | FR-053 d, FR-054 |
| Grão | Deduplicação por `pk` da Conclusão e `UNIQUE (snapshot, conclusao)` | FR-031, FR-053 c |
| Elegibilidade explícita | Valor definido pela consulta de origem; coluna não nula | FR-021, FR-053 e |
| Elegíveis = população lida | Por construção: os elegíveis gravados são os lidos da 004 | FR-034, FR-053 f |
| Participações representadas | Universo inclui todas; verificação do passo 8 | FR-032, FR-053 d |
| Elegibilidade só da 004 | `populacao_no_momento`; nenhum critério lido | FR-020 |
| Contexto como registrado | Cópia direta de `CAMPOS_DE_CONTEXTO`, sem transformação | FR-040 a FR-043 |
| Nada existente é alterado | A operação só cria `SnapshotAnalitico` e `RegistroDoSnapshot` | FR-002 |
| Concorrência | Sem lock; capturas simultâneas são transações independentes e geram snapshots independentes | FR-062 |
| Volume | Duas consultas de leitura (mais uma só para participantes fora da população) e um `bulk_create`; sem consulta nem `INSERT` por Conclusão | FR-110 |
| `capturado_em` | Momento técnico da captura, lido pela operação; não é instante de leitura isolada | FR-016 |

## Vocabulário (`regras.py`)

```text
Motivo (Enum)
  CAMPANHA_NUNCA_ABERTA  = "campanha_nunca_aberta"   # spec FR-012
  COLETA_NAO_ENCERRADA   = "coleta_nao_encerrada"    # spec FR-011

SnapshotRecusado(Exception)       # recusa de domínio; nada gravado
  .motivo: Motivo
  str(): motivo e id da Campanha; nunca valores acadêmicos

CapturaInconsistente(Exception)   # integridade; nada gravado
  str(): qual verificação falhou, id da Campanha, contagens; nunca valores acadêmicos
```

Uma única recusa por vez basta: as duas condições são mutuamente exclusivas na ordem
acima.

## O que não existe

- Operação para editar, corrigir, recalcular, completar, remover ou "oficializar"
  snapshot ou registro (spec FR-050, FR-061).
- Parâmetro de momento, de população, de lista de Conclusões ou de atributos (spec FR-016).
- Captura automática, agendada ou disparada por leitura (spec FR-015).
- Registro de quem solicitou (spec FR-104).
