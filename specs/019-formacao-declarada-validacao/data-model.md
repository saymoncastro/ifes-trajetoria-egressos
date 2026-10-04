# Data Model: Formação não localizada e validação posterior

Fase 1, revisada em 2026-10-04. Mudanças em relação à primeira versão:
- um app novo (`declaracao`) em vez de dois;
- conflito como **detectado** (pendente), não estado permanente;
- idempotência da criação;
- prova do preenchimento dos snapshots.

O app novo tem cinco modelos. `Participacao` e `RegistroDoSnapshot` ganham dois campos cada.
Pessoa, Conclusão, Resposta, Campanha e Versão não mudam. Toda escrita passa por operações
(contracts/operacoes.md). Nenhum modelo novo tem operação de edição.

## Modelos novos — app `declaracao`

### FormacaoDeclarada *(dado declarado; imutável)*

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id` | UUID | PK |
| `nome` | texto | não vazio |
| `unidade` | texto | não vazio; da lista de R20 |
| `nivel` | texto | não vazio; da lista de R20 |
| `curso` | texto | não vazio, gravado como digitado |
| `ano_conclusao` | inteiro positivo pequeno | 4 dígitos; não futuro na criação |
| `identificador_cpf` | texto | hex de 64; indexado; HMAC do CPF (chave de localização da 018) |
| `verificador` | texto | hex de 64; indexado; HMAC do par (chave de verificação da 018); só sessão e retomada |
| `chave_de_criacao` | UUID | `UNIQUE`; vem do selo de início; torna a criação idempotente (R6) |
| `declarada_em` | data e hora | momento de referência da criação |

- **Relações.** Referenciada por `Participacao.formacao_declarada` (1:1),
  `DadosConsultaAcervo` (1:1), `ValidacaoDaFormacao` (1:0..1) e
  `AcessoAosDadosDeConsulta` (1:N).
- **Nomes dos campos.** `unidade`, `nivel`, `curso` e `ano_conclusao` têm os nomes dos
  atributos da Conclusão. Por isso `avaliar` (004) e a divergência funcionam por `getattr`
  (R9).
- **CHECKs.** Textos não vazios; formato hex dos HMACs.

### DadosConsultaAcervo *(dado pessoal protegido; separável e descartável)*

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id` | UUID | PK |
| `formacao` | 1:1 → FormacaoDeclarada | `PROTECT` |
| `selado` | texto | token Fernet (chave B) com finalidade `acervo`, UUID da declaração, CPF e data (R5) |

- **Ciclo de vida.** Nasce na transação da declaração e antes de qualquer decisão.
  Descartar é remover a linha, sem efeito em nenhum outro registro (FR-118). Não há
  descarte na 019.
- **Nunca vai para** `repr`, log, exportação, snapshot ou acompanhamento.

### ValidacaoDaFormacao *(registro administrativo; imutável)*

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id` | UUID | PK |
| `formacao` | 1:1 → FormacaoDeclarada | `PROTECT`; no máximo uma decisão (FR-072) |
| `resultado` | lista fechada | `CONFIRMADA` ou `NAO_CONFIRMADA` |
| `conclusao` | FK → ConclusaoAcademica, anulável | `PROTECT`; preenchida ⇔ `CONFIRMADA` |
| `fora_da_abrangencia_na_validacao` | booleano | **fato congelado** (R3) |
| `conflito_detectado_na_validacao` | booleano | **fato da detecção** (R3). Pendente enquanto não houver resolução; na 019 não há resolução (DP-1907) |
| `registrada_em` | data e hora | — |
| `operador` | texto | identificador do operador (010), nunca dado pessoal dele |

**CHECKs.**
- `conclusao IS NOT NULL ⇔ resultado = CONFIRMADA`.
- Com `NAO_CONFIRMADA`, os dois booleanos são falsos.
- `conflito_detectado_na_validacao` implica `NOT fora_da_abrangencia_na_validacao`. Fora da
  abrangência não chega a disputar oficialidade.

### AcessoAosDadosDeConsulta *(trilha de auditoria)*

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id` | UUID | PK |
| `formacao` | FK → FormacaoDeclarada | `PROTECT` |
| `operador` | texto | identificador do operador |
| `acessado_em` | data e hora | — |

- **Sem valores revelados.** Uma linha por revelação (FR-116).
- **Uso.** Não é exportado nem exibido na 011. Consulta e retenção ficam em DP-1903.

### ReferenciaDeAcervo *(dado institucional da fonte `acervo_historico`; imutável)*

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id` | UUID | PK; base dos `id_externo` da fonte (R12) |
| `unidade` | texto | não vazio |
| `referencia` | texto | não vazio; espaços normalizados |
| `nivel`, `curso` | texto | não vazios |
| `ano_conclusao` | inteiro positivo pequeno | obrigatório |
| `modalidade`, `forma_oferta` | texto, anulável | só se o acervo informar; não vazio quando presente |
| `data_conclusao` | data, anulável | se presente, o ano coincide com `ano_conclusao` (001) |
| `registrada_em` | data e hora | — |
| `operador` | texto | identificador do operador |

- **Unicidade.** `UNIQUE (unidade, referencia)`. Registrar de novo com valores iguais
  reencontra a Referência; com valores diferentes, é recusado (FR-083).
- **Leitura.** Lida **somente** pelo adaptador `declaracao/acervo.py`
  (`FonteAcervoHistorico`). Pessoa e Conclusão nascem pela 001, com `fonte =
  "acervo_historico"`.
- **Separação do resto do app.** A Referência não tem FK para a declaração nem para a
  validação: é dado de fonte, não do caso.

## Mudanças em modelos existentes

### Participacao (005)

| Mudança | Regra |
| --- | --- |
| `conclusao` passa a anulável | Continua `PROTECT`, sem acessor reverso |
| novo `formacao_declarada` | 1:1 → `declaracao.FormacaoDeclarada`, anulável, `PROTECT`, `related_name="participacao"` |
| novo CHECK `participacao_ancora_unica` | Exatamente um entre `conclusao` e `formacao_declarada` |
| `UNIQUE (campanha, conclusao)` | Inalterado |
| propriedade `pessoa` | `None` quando a âncora é declarada |

Nenhuma operação altera a âncora depois da criação (FR-030). A migração é aditiva, e o
CHECK vale para todas as linhas existentes, que têm `conclusao`.

### RegistroDoSnapshot (012)

| Mudança | Regra |
| --- | --- |
| novo `participacao` | FK → Participacao, anulável, `PROTECT`; a oficial que compõe o registro na captura |
| novo `origem_formacao` | `institucional`, `declarada_validada_fonte_digital`, `declarada_validada_acervo`; `NULL` ⇔ `participacao` nula |

**Preenchimento dos registros existentes.** Determinístico, provado em research R14 por
quatro invariantes:
- `UNIQUE (campanha, conclusao)` desde `participacao/0001`;
- Participação não removível nem religável;
- captura só com a Campanha encerrada, sem reabertura;
- nenhuma âncora não institucional antes da 019.

A migração aborta, sem escolher nada, se encontrar um par com mais de uma Participação.
Esse caso é impossível pelo primeiro invariante e fica verificado explicitamente.

## Derivações (não persistidas)

| Derivação | Regra | Onde |
| --- | --- | --- |
| **Conflito pendente** | `conflito_detectado_na_validacao` e nenhuma resolução registrada. Na 019 não há resolução, então equivale ao detectado | `participacao/consultas.py` |
| **Oficial** | Âncora em Conclusão; **ou** validação `CONFIRMADA`, sem `fora_da_abrangencia_na_validacao` e sem conflito pendente | `participacoes_oficiais()` (R4) |
| **Situação analítica** | FR-050; `DECLARADA_EM_CONFLITO` = conflito pendente | idem |
| **Conclusão efetiva** | `Coalesce(conclusao_id, formacao_declarada__validacao__conclusao_id)` | idem |
| **Divergência** | Campos `unidade`, `nivel`, `curso` e `ano_conclusao` diferentes entre a declaração e a Conclusão vinculada | tela de validação |
| **Candidatas** | `MaterialDeVerificacao.identificador_cpf = FormacaoDeclarada.identificador_cpf`, mais as Conclusões dessas Pessoas | tela de validação |
| **Outras declarações do mesmo CPF** | Mesmo `identificador_cpf`, outra declaração; nunca pelo `verificador` | tela de validação |
| **Origem da formação** | `institucional` se a âncora é Conclusão; senão `declarada_validada_acervo` se `conclusao.fonte = "acervo_historico"`; senão `declarada_validada_fonte_digital` | captura do snapshot |

## Transições

```text
"Começar" (selo de início; chave_de_criacao única)
   → FormacaoDeclarada + DadosConsultaAcervo + Participacao   (uma transação)
        │ jornada 005/006 inalterada; concluida_em preenchido → entra na fila
        ▼
ValidacaoDaFormacao  (uma vez; imutável)
   NAO_CONFIRMADA ────────────────────────────────► DECLARADA_NAO_CONFIRMADA
   CONFIRMADA ─┬─ fora_da_abrangencia_na_validacao ► DECLARADA_FORA_DA_ABRANGENCIA
               ├─ conflito_detectado_na_validacao ─► DECLARADA_EM_CONFLITO (pendente)
               └─ ───────────────────────────────► DECLARADA_VALIDADA (oficial)
```

**Fora da 019.**
- **Resolução de conflito** (DP-1907): será um registro próprio que encerra a pendência
  sem alterar a decisão.
- **Reabertura** (DP-1905).
- **Descarte** (DP-1903).

## Dependências entre módulos

```text
declaracao.models     → academico (Conclusão)
participacao.models   → declaracao.models (âncora; FK por nome)
declaracao.acervo     → fonte_academica.contrato (implementa o protocolo)
declaracao.operacoes  → participacao, campanha, academico.incorporacao, acesso (chaves,
                        material, limitação), governanca, declaracao.acervo
analitico, exportacao, acompanhamento, participacao.entrada
                      → participacao.consultas.participacoes_oficiais
```

- `declaracao.models` não importa `participacao`. Não há ciclo de import.
- `fonte_academica` continua Python puro (001).
- `academico` continua conhecendo só o contrato.
- Os testes de fronteira passam a listar estas permissões.
