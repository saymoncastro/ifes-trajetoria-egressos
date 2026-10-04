# Data Model: Gestão mínima de Campanha

**Nenhuma entidade, campo, estado ou migração nova** (FR-025). A 017 lê e escreve só pelos
modelos e operações existentes.

## Entidades consumidas

| Entidade | Origem | Uso na 017 |
| --- | --- | --- |
| `Campanha` | 004 | Criada, editada enquanto `aberta_em` é nulo, aberta e encerrada só por `trajetoria/campanha/operacoes.py`. Critérios lidos, nunca gravados |
| `Versao`, `Pesquisa` | 002 | Leitura: Versões `PUBLICADA` para escolha; Versão atual em rascunho só como opção marcada na edição |
| `VinculoDeGovernanca` | 010 | Leitura por `vinculos_do_operador_em_uso`; decide `pode_gerir_campanha` |

## Valores derivados (não persistidos)

### Impedimento de abertura

`impedimentos_de_abertura(campanha, agora) -> tuple[Violacao, ...]` (004, extraída de
`abrir`). Ordem e motivos idênticos aos de `abrir`:

| Motivo (004) | Condição | Texto ao operador (causa → correção) |
| --- | --- | --- |
| `VERSAO_NAO_PUBLICADA` | Versão relida não está PUBLICADA | "A Versão escolhida ainda não foi publicada." → havendo Versão publicada: "Escolha uma Versão publicada em Editar configuração. A publicação não é feita aqui."; não havendo nenhuma: "Ainda não há Versão publicada disponível. A publicação não é feita aqui." (mesmo texto de FR-009) |
| `PERIODO_NAO_DEFINIDO` | `inicio` nulo | "O período de coleta não foi definido." → "Defina início e fim em Editar configuração." |
| `FORA_DO_PERIODO`, hoje < `inicio` | antes do início | "A coleta poderá ser aberta a partir de dd/mm/aaaa." → (nenhuma; voltar na data) |
| `FORA_DO_PERIODO`, hoje > `fim` | período encerrado | "O período terminou sem que a coleta fosse aberta." → "Para usar esta Campanha, corrija o período em Editar configuração." |

Calculado só para Campanha nunca aberta; para Campanha aberta não há impedimento a mostrar.

### Painel de gestão (apresentação, por Campanha)

| Campo | Regra |
| --- | --- |
| `situacao_gestao` | `nunca_aberta_pronta` (sem impedimentos, EM PREPARAÇÃO), `nunca_aberta_impedida` (EM PREPARAÇÃO com impedimentos), `periodo_encerrado_nunca_aberta` (ENCERRADA e `aberta_em` nulo), `em_coleta`, `encerrada_apos_coleta` |
| `acoes` | Matriz de FR-017: Editar configuração / Abrir coleta / Encerrar coleta / nenhuma |
| `impedimentos` | Textos da tabela acima |
| `encerramento_previsto` | `fim`, só EM COLETA |
| `abrangencia_restrita` | Lista legível dos critérios definidos, só se algum critério não for nulo (FR-022); vazia em Campanha ampla |

### Rótulo de situação (011, todos os operadores)

| Estado (004) | `aberta_em` | Rótulo |
| --- | --- | --- |
| EM PREPARAÇÃO | nulo | Em preparação |
| EM COLETA | preenchido | Em coleta |
| ENCERRADA | preenchido | Encerrada |
| ENCERRADA | nulo | Período encerrado — Campanha nunca aberta |

## Entrada dos formulários

| Campo | Criar | Editar | Conversão | Quem rejeita |
| --- | --- | --- | --- | --- |
| `nome` | obrigatório | obrigatório | texto como digitado | 004 `NOME_VAZIO` |
| `versao` | Versões PUBLICADA | PUBLICADA + atual em rascunho (marcada) | pk → `Versao` | interface (escolha inválida) |
| `inicio`, `fim` | opcionais | opcionais | data ISO → `date`; vazio → `None` | 004 `PERIODO_INCOMPLETO`, `PERIODO_INVERTIDO`; interface: formato inválido; remoção de período existente |

Ambas as datas vazias: na criação, nenhum período; na edição de Campanha sem período, nada
muda; na edição de Campanha com período, rejeição "o período pode ser corrigido, mas não
removido". Rejeição de Campanha já aberta (`CAMPANHA_JA_ABERTA`) → página 409, não erro de
campo.

## Transições usadas (todas da 004)

```text
(criar) ──► nunca aberta ──(abrir, dentro do período)──► EM COLETA ──(encerrar)──► ENCERRADA
               ▲   │                                         │
               │   └── fim do período ──► "Período encerrado │── fim do período ──► ENCERRADA
               │        — nunca aberta"                       │
               └──(editar período) ◄──────┘
```

Nenhuma transição nova; corrigir o período de Campanha nunca aberta não é reabertura
(004 FR-039).
