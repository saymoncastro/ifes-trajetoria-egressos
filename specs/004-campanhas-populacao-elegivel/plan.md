# Implementation Plan: Campanhas e população elegível

**Branch**: `claude/feature-004-campanhas-463fe9` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-campanhas-populacao-elegivel/spec.md`

## Summary

A 004 entrega a **Campanha**: rodada institucional que aplica uma Versão publicada,
durante um período, a uma população definida por critérios sobre a Conclusão Acadêmica.
Não cria Participação, Resposta, convite nem comunicação.

- **Um modelo novo**, `Campanha`, no novo app `trajetoria.campanha` (R1, R2):
  - nome;
  - FK `versao`, com Pesquisa derivada (R12);
  - `inicio` e `fim`;
  - seis critérios opcionais em colunas: `ano_minimo`, `ano_maximo` e quatro
    `ArrayField(TextField)` (`unidades`, `niveis`, `modalidades`, `formas_oferta`)
    (R3, R4);
  - os fatos `aberta_em` e `encerrada_em`.
- **Estado derivado, não gravado** (R5), com o tempo tendo precedência:
  1. com `encerrada_em` → ENCERRADA;
  2. senão, data de referência posterior a `fim` → ENCERRADA, aberta ou não;
  3. senão, com `aberta_em` → EM_COLETA;
  4. senão → EM_PREPARACAO.

  O encerramento por fim do período é cálculo, não job. Uma Campanha nunca aberta cuja
  janela expirou é ENCERRADA, não fica "em preparação" para sempre.
- **Estado temporal controla a coleta; abertura histórica controla a imutabilidade.** A
  escrita é bloqueada só por `aberta_em` presente. Campanha nunca aberta, mesmo
  ENCERRADA pelo tempo, continua editável e removível.
- **Tempo injetável por parâmetro** `agora`, com padrão `timezone.now()` e convertido
  para data pela timezone configurada do projeto, sem fuso fixado pela feature. Sem
  framework de relógio (R6).
- **Elegibilidade pura** (`avaliar`): ELEGIVEL ou NAO_ELEGIVEL, com pendências
  `(critério, NAO_INFORMADO | NAO_ATENDE)` em ordem fixa e nada persistido (R7).
- **População no momento da consulta**: QuerySet equivalente, com teste de consistência
  contra `avaliar`. Sem fotografia, membros ou contagem gravada (R8; DP-408).
- **Contrato para a 005**: `estado`, `admite_participacao` e
  `campanhas_em_coleta_para` (R9).
- **Imutabilidade após abertura** pelas operações, único caminho de escrita, e por
  testes. Sem gatilhos (R10, ADR 0002).

As Features 001, 002 e 003 não mudam. Decisões e alternativas estão em
[research.md](research.md).

## Technical Context

- **Language/Version**: Python 3.13 ([ADR 0001](../../docs/adr/0001-stack-inicial.md)).
- **Primary Dependencies**: Django 5.2 LTS e psycopg 3. Nenhuma dependência nova:
  `ArrayField` vem de `django.contrib.postgres`, já incluído no Django (R3).
- **Storage**: PostgreSQL 16+. Uma tabela nova, com CHECKs locais. Regras entre linhas
  (Versão publicada) e temporais (data no período) ficam nas operações (R10).
- **Testing**: pytest, pytest-django e ruff, em PostgreSQL, sem rede e com `agora`
  explícito.
- **Target Platform**: servidor Linux, para operação futura; nesta feature, execução local
  e CI.
- **Project Type**: aplicação web monolítica (Django), ainda sem camada web, interface ou
  API.
- **Performance Goals**: N/A. A população é um filtro indexável sobre `ConclusaoAcademica`;
  o volume institucional (dezenas de milhares de Conclusões) não exige otimização nesta
  feature.
- **Constraints**:
  - nenhuma alteração em modelos, operações ou cenários das Features 001, 002 e 003;
  - nenhuma interface expõe operações de Campanha (DP-402);
  - nenhum processo agendado;
  - nenhum dado pessoal novo.
- **Scale/Scope**: 1 modelo, 1 migração, 7 operações de escrita, 6 consultas e 13
  motivos de rejeição.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ | ✅ | A Campanha não consome a Conclusão: a mesma Conclusão é elegível em várias Campanhas (FR-050). `campanhas_em_coleta_para` devolve 0..N. A relação futura Campanha 1—0..N Participação ↔ 1 Conclusão não é bloqueada ([consultas](contracts/consultas.md)) |
| 2 | Pessoa versus Conclusão Acadêmica (campus/curso no contexto da conclusão) | I, XI | ✅ | ✅ | `avaliar` recebe Conclusão, nunca Pessoa. Unidade, nível, modalidade e forma de oferta são lidos da Conclusão (R7) |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | ✅ | ✅ | Cada Conclusão avaliada isoladamente. Teste da Pessoa C (Serra 2022 elegível, Cefor 2025 não) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | N/A | N/A | Participação fora do escopo (FR-055). Nada impede várias Campanhas por Conclusão |
| 5 | Definição institucional de egresso respeitada | II | ✅ | ✅ | Universo = Conclusões da 001, que só materializa formações reconhecidas. Nenhum critério inclui não egressos (FR-017) |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | Abertura só com Versão PUBLICADA. Campanha aberta imutável e não removível pelas operações. `aberta_em` e `encerrada_em` gravados uma vez. Anos absolutos. Migração só cria tabela nova (R5, R10) |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ | ✅ | `Campanha` é modelo próprio com FK para `Versao`. Sem coluna `pesquisa` (R12) e sem coluna nova em `Versao`. Sem Participação |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | ✅ | ✅ | Momentos de abertura e de encerramento explícito gravados. Sem trilha de auditoria de elegibilidade (FR-030) nem histórico de preparação (FR-046) |
| 9 | Separação entre dado institucional, derivado e declarado; divergências explícitas | III | ✅ | ✅ | Lê só dado institucional da Conclusão. Elegibilidade e população são derivadas e não persistidas. `NULL` → `NAO_INFORMADO`, nunca inferido (R7) |
| 10 | Desacoplamento de integrações (providers/adaptadores, mock com mesmo contrato) | V, XV, XXV | ✅ | ✅ | Nenhuma integração nova. A população depende do modelo canônico da 001, não da fonte. Testes usam a fonte simulada e o caminho real de incorporação |
| 11 | Fronteira do NIAE (5 perguntas do Princípio VI, se aplicável) | VI | ✅ | ✅ | Respondidas na spec. Comunicação e convites fora (FR-049) |
| 12 | Governança institucional (periodicidade, publicação, competências normativas) | IX, X | ⏸ | ⏸ | Sem periodicidade, duração padrão ou janela relativa (FR-005, FR-014, FR-021). A Campanha não publica Versão. Competência para operar Campanha em DP-402: operações sem ponto de entrada (R13) |
| 13 | Escopo por unidade e visão institucional consolidada | XII | ✅ | ✅ | Base única. Campanha institucional = sem critério de unidade; recorte por unidade opcional. Nenhuma Campanha ou tabela por campus. Relação CPAEG/CSAEG em DP-403 |
| 14 | Privacidade, minimização e dados pessoais em logs/exportações | XVI, XVII | ✅ | ✅ | A Campanha não contém dado pessoal. Nenhum log novo. A população é consultada, não copiada (sem lista materializada) |
| 15 | Autorização (menor privilégio; competência técnica ≠ normativa) | X, XII | N/A | N/A | Sem interface, admin, comando ou API (R13). Autorização virá com DP-402 |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG, quando houver interface) | XX | N/A | N/A | Sem interface |
| 17 | Responsividade e jornada móvel | XIV, XXI | N/A | N/A | Sem jornada. `campanhas_em_coleta_para` permite à futura jornada contextualizar sem convite (XIV) |
| 18 | Testes proporcionais ao risco cobrindo invariantes afetados | XXV, XXVI | ✅ | ✅ | [Estratégia de testes](#estratégia-de-testes): elegibilidade, ciclo, imutabilidade, população dinâmica, longitudinalidade; tempo determinístico (R6) |
| 19 | Risco de over engineering (YAGNI; sem form builder universal) | XXII, XXIII, XXIV | ✅ | ✅ | 1 modelo; seis colunas de critério com semântica fixa; estado derivado; sem tabela de critérios, membros, fotografia, agendador, sinais, serviço ou repositório. Complexity Tracking vazio |
| 20 | Exportabilidade e semântica das exportações (se aplicável) | XVIII | N/A | N/A | Exportação fora do escopo. Colunas explícitas e UUID estável facilitam exportação futura por Campanha |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ | ✅ | DP-401 a DP-409 e herdadas abaixo. Hipóteses reversíveis: timezone do projeto, granularidade diária, igualdade exata, coexistência de Campanhas |

**Resultado do gate**: APROVADO (pré-Fase 0 e pós-Fase 1). O item 12 está como DECISÃO
PENDENTE, sem violação: a feature especifica capacidades e efeitos, não quem as exerce.

**Conflitos identificados**: nenhum. Duas tensões estão registradas na spec, sem
conflito:

- PAEG Art. 22, IV × Campanha institucional: tratada em DP-402 e DP-403.
- Princípio XIX × população dinâmica: tratada em DP-408. A contagem é rotulada "no
  momento da consulta" (FR-031).

**Revisão pós-implementação (2026-10-01, T037)**: gate mantido. Definition of Done
atendida:

- 215 testes novos cobrem os invariantes; a suíte completa tem 537 testes, todos
  verdes;
- ruff, `manage.py check` e `makemigrations --check` estão limpos;
- um único modelo (`Campanha`) e uma única migração (`0001_initial.py`), sem `RunSQL`,
  gatilho, sinal, `save()` sobrescrito, job ou scheduler;
- `Campanha.versao` usa `related_name="+"`: a Versão não conhece a Campanha (R1), o que
  mantém verde o teste SC-006 da 002;
- só `consultas.momento_de_referencia` consulta o relógio; os testes passam `agora`
  explícito;
- nada da lista "Limites" de tasks.md foi criado; nenhuma interface, admin, URL ou
  comando; nenhum log ou dado pessoal novo;
- DP-401 a DP-409 e as herdadas continuam abertas; a baseline da 003 continua RASCUNHO;
- **exceção aprovada pelo solicitante**: uma linha de
  `tests/instrumento/test_instrumento_aceitacao.py` (SC-007 da 002). A asserção "nenhum
  modelo do projeto se chama Campanha, Participacao ou Resposta" passou a valer só para o
  app `instrumento`. Preserva a intenção de 002 FR-066 (a 002 não cria esses conceitos),
  mas tornava impossível qualquer Feature 004. Nenhum código de produção das features
  001–003 foi alterado;
- Complexity Tracking continua vazio.

**Revisão de código (2026-10-01)**: nove achados corrigidos, com testes de regressão
(547 testes no total):

- `encerrar` com `agora` anterior à abertura é rejeitado (`ANTES_DA_ABERTURA`);
- `encerrada_em` gravado nunca é sobrescrito;
- abertura e encerramento só valem a partir do momento em que ocorreram;
- `agora` de tipo errado é `TypeError`;
- as operações atualizam a instância recebida;
- `alterar_campanha` valida tipos antes do bloqueio;
- `Elegibilidade.resultado` é derivado das pendências;
- `campanhas_em_coleta_para` filtra no banco;
- o teste do caso K compara o resultado inteiro;
- a asserção redundante do SC-007 da 002 foi removida, porque a igualdade dos cinco
  modelos já garante FR-066.

**Correção de escopo de teste (2026-10-01, após o merge)**: o teste SC-009
`test_um_unico_modelo_novo_e_nenhum_proibido` proibia, no projeto inteiro, modelos
chamados `Participacao`, `Resposta`, `Convite` etc. Era excessivamente amplo: SC-009
trata do escopo da 004 (o app `campanha` não cria esses conceitos), não de features
posteriores. Ele virou `test_app_campanha_tem_somente_o_modelo_campanha`, que exige que
os modelos do app `campanha` sejam exatamente `["Campanha"]`, sem lista global de nomes.
Não é mudança de requisito da 004 e nenhum código de produção mudou. Motivação: a
Feature 005 cria `Participacao` e `Resposta` no app `participacao`.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-401 | Periodicidade, duração e critérios oficiais de cada edição | Proex e Proen e/ou órgão competente (PAEG Art. 10, II) | Nenhum padrão; cada Campanha recebe período e critérios explícitos | Nada a reverter: o conteúdo de cada Campanha é dado, não código |
| DP-402 | Quem cria, configura, abre, encerra e remove Campanha | Proex/CPAEG (PAEG Art. 26) | Operações só como funções de domínio, sem ponto de entrada | Feature futura acrescenta autorização no ponto de entrada; operações não mudam |
| DP-403 | Campanhas próprias de unidade (CSAEG) e relação com a institucional | CPAEG, Proex | Critério de unidade opcional; nenhum desenho obrigatório | Regra de escopo, se decidida, por spec própria |
| DP-404 | Campanhas EM_COLETA com populações sobrepostas | CPAEG | Coexistência permitida; `campanhas_em_coleta_para` devolve todas, sem prioridade | Restrição na abertura ou regra de escolha na 005, localizada em uma função |
| DP-405 | Prorrogação, reabertura, correção do nome após abertura | CPAEG/Proex | Não existem; `aberta_em` e `encerrada_em` gravados uma vez | Operação nova, aditiva, por spec própria |
| DP-406 | Forma de acesso do egresso e identificação | A identificar (Proex, DTI) | Nada depende de convite; consulta por Conclusão disponível | Jornada futura consome `campanhas_em_coleta_para` |
| DP-407 | Canais de divulgação e comunicação individual | A identificar (Proex, DIREC) | Inexistentes | Integração externa futura, fora da Campanha |
| DP-408 | Fotografia ou população de referência para indicadores | Proex/CPAEG | População calculada no momento da consulta; nada gravado | Fotografia aditiva (tabela ou coluna), quando houver consumidor |
| DP-409 | Conclusões excluídas só por atributo não informado | CPAEG e registro acadêmico | Exclusão conservadora com `NAO_INFORMADO` | Política de correção na origem (001/DP-005); a regra de avaliação não muda |
| 002/DP-001 | Competência para publicar Versão | Proex/CPAEG | Abertura exige PUBLICADA; a Campanha nunca publica; baseline da 003 permanece RASCUNHO | — |
| 001/DP-005, 001/DP-007 | Correção de dado acadêmico; vocabulário canônico | CPAEG e responsáveis pela fonte | Igualdade exata com o valor gravado; eventual correção pode mudar a elegibilidade (aceito, Clarifications) | Normalização no adaptador da fonte, sem mudar a Campanha |

Também continuam abertas 002/DP-002, 003/DP-301, 003/DP-302, 001/DP-001, 001/DP-004 e
001/DP-008 (spec, Decisões Pendentes).

## Desenho

### Modelo

Um modelo em [data-model.md](data-model.md):

- **Identidade**: UUID.
- **Versão**: FK `PROTECT`, obrigatória. Pesquisa por propriedade.
- **Período**: `inicio` e `fim`, ambos presentes ou ambos ausentes, com `inicio ≤ fim`
  (CHECK).
- **Critérios**:
  - `ano_minimo` e `ano_maximo`, com CHECK de ordem;
  - quatro arrays de texto anuláveis, com CHECK de cardinalidade ≥ 1 e sem cadeia vazia.
    Os estados gravados são inequívocos:
    - `NULL` = critério não definido, não restringe;
    - array com ≥ 1 valor = valores permitidos;
    - `[]` = configuração inválida, rejeitada pela operação (`CONJUNTO_VAZIO`) e pelo
      CHECK, nunca gravada.

    Valores exatos, sem normalização, sem duplicatas, em ordem lexicográfica só para
    estabilidade.
- **Ciclo**: `aberta_em` e `encerrada_em`, com CHECKs de coerência: encerrada exige
  aberta, aberta exige período, encerramento depois da abertura.

### Operações e rejeições

[contracts/operacoes.md](contracts/operacoes.md). Fluxo de toda escrita, como na 002:

1. abre transação;
2. bloqueia a Campanha (`select_for_update`);
3. se `aberta_em` está presente, rejeita `CAMPANHA_JA_ABERTA`, qualquer que seja o
   estado temporal (exceto `abrir` e `encerrar`);
4. verifica as regras da operação;
5. grava.

`definir_periodo`, `definir_criterios` e `abrir` acumulam violações e rejeitam todas de
uma vez. Exceção local `CampanhaRejeitada`, no mesmo padrão de
`instrumento.regras.OperacaoRejeitada` (R10).

### Estado e tempo

`estado(campanha, *, agora=None)` aplica a tabela do
[data-model](data-model.md#estado-observável-derivado), na precedência: encerramento
explícito → fim do período → abertura → preparação. Um auxiliar privado converte `agora`
(padrão `timezone.now()`) em `hoje = timezone.localdate(agora)`, na timezone configurada
do projeto. Só esse auxiliar consulta o relógio, então todos os testes passam `agora`
explícito (R6).

O encerramento por fim do período não grava nada: quem consulta com `hoje > fim` recebe
ENCERRADA, tenha a Campanha sido aberta ou não. Por isso:

- não existe job;
- não existe divergência entre linha gravada e calendário;
- não existe estado "aberta, porém vencida" nem "em preparação, porém vencida".

A permissão de escrita **não** depende do estado. Uma Campanha nunca aberta e
expirada:

- é ENCERRADA para a coleta;
- não admite Participação;
- não pode ser aberta com esse período (`FORA_DO_PERIODO`);
- o encerramento explícito é rejeitado (`CAMPANHA_NUNCA_ABERTA`), sem gravar nada;
- continua editável e removível.

Se o período for corrigido para o futuro, ela volta a EM_PREPARACAO. Isso não é
reabertura, que só existe com `aberta_em` presente e continua fora do escopo (FR-039,
DP-405).

### Elegibilidade e população

- `avaliar` é pura (R7): percorre os critérios na ordem `ANO_CONCLUSAO, UNIDADE, NIVEL,
  MODALIDADE, FORMA_OFERTA` e devolve `Elegibilidade(resultado, pendencias)`.
- `populacao_no_momento` monta um `Q` com os mesmos critérios (R8). O SQL exclui `NULL`
  nas comparações e no `IN`, o que coincide com `NAO_INFORMADO`.
- Um teste de consistência cruza as duas sobre todas as Conclusões dos cenários e todas as
  Campanhas de referência.

### Imutabilidade

Garantida pela aplicação (R10), como a Versão publicada na 002:

- toda operação de preparação chama o bloqueio e a verificação `CAMPANHA_JA_ABERTA`
  (`aberta_em` presente) antes de qualquer regra;
- nenhuma operação recebe `aberta_em` ou `encerrada_em` como parâmetro, nem os apaga;
- `abrir` e `encerrar` só gravam o próprio fato, e só quando ausente;
- testes tentam cada escrita em EM_COLETA e ENCERRADA e comparam a linha antes e depois.

Sem gatilho, sinal, `save()` sobrescrito ou `RunSQL`.

### Contrato com a 005

[contracts/consultas.md](contracts/consultas.md):

| Pergunta da 005 | Resposta |
|-----------------|----------|
| Esta Campanha está aceitando coleta nesta data? | `estado(c, agora=…) is EM_COLETA` |
| Esta Campanha está encerrada? | `estado(c, agora=…) is ENCERRADA`; detalhe em `encerramento(c, agora=…)` |
| Esta Conclusão é elegível? | `avaliar(c, conclusao)` |
| Esta Conclusão pode iniciar Participação nesta Campanha? | `admite_participacao(c, conclusao, agora=…)` (condição necessária) |
| Quais Campanhas valem para esta Conclusão agora? | `campanhas_em_coleta_para(conclusao, agora=…)` (sem prioridade; DP-404) |

## Project Structure

### Documentation (this feature)

```text
specs/004-campanhas-populacao-elegivel/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # R1–R14
├── data-model.md        # Campanha, estado derivado, elegibilidade
├── quickstart.md        # validação
├── contracts/
│   ├── operacoes.md     # escrita e rejeições
│   └── consultas.md     # estado, elegibilidade, população, contrato com a 005
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks (não criado por este comando)
```

### Source Code (repository root)

```text
trajetoria/
├── campanha/                         # NOVO app
│   ├── __init__.py
│   ├── apps.py                       # CampanhaConfig
│   ├── models.py                     # Campanha (único modelo)
│   ├── regras.py                     # Motivo, Violacao, CampanhaRejeitada
│   ├── operacoes.py                  # criar, alterar, definir_periodo, definir_criterios,
│   │                                 # abrir, encerrar, remover (único caminho de escrita)
│   ├── consultas.py                  # EstadoCampanha, estado, encerramento, avaliar,
│   │                                 # populacao_no_momento, admite_participacao,
│   │                                 # campanhas_em_coleta_para
│   └── migrations/
│       ├── __init__.py
│       └── 0001_initial.py
├── academico/                        # inalterado
├── instrumento/                      # inalterado
├── fonte_academica/                  # inalterado
└── formulario_2024/                  # inalterado

config/settings.py                    # + "trajetoria.campanha" em INSTALLED_APPS (única linha alterada)

tests/campanha/                       # NOVO
├── conftest.py                       # versão publicada, versão rascunho, agora fixo, cenários incorporados
├── construcao.py                     # auxiliares: momento(dia), conclusao(...) no ORM, rejeita(...)
├── test_campanha_modelo.py
├── test_campanha_preparacao.py
├── test_campanha_elegibilidade.py
├── test_campanha_ciclo.py
├── test_campanha_imutabilidade.py
├── test_campanha_longitudinal.py
└── test_campanha_aceitacao.py

README.md                             # + link para o quickstart da 004
```

**Structure Decision**: um app Django novo no monolito existente, no mesmo padrão dos
apps `academico` e `instrumento`: modelo, vocabulário de rejeição, operações e leitura.
Não há camada de serviço, repositório, sinais nem tarefas. O app depende de `instrumento`
e de `academico`, e nenhum deles depende dele.

## Estratégia de testes

O foco são os invariantes, não um percentual (XXVI). Todo teste temporal passa `agora`
explícito, construído por um auxiliar `momento(ano, mes, dia)` na timezone configurada do
projeto.

| Teste | Dado | Requisito |
|-------|------|-----------|
| Campanha ampla sem critérios: todas as Conclusões elegíveis, inclusive com atributos ausentes; contagem = total; `populacao_ampla` verdadeiro | Cenários da 001 + Conclusão sem atributos | US3, FR-019, SC-004 |
| Intervalo 2020–2024: 2019 ✗, 2020 ✓, 2024 ✓, 2025 ✗ | Conclusões no ORM | US4.1, FR-021 |
| Só mínimo 2020: 2019 ✗, 2031 ✓ | — | US4.2 |
| Só máximo 2024: 1998 ✓, 2025 ✗ | — | US4.3 |
| Unidade {Serra}; várias unidades {Serra, Vitória}; Cefor ✗ | Cenários | US7.1–US7.3 |
| Nível; modalidade; forma de oferta | Cenários (Técnico/Integrado, EaD) | US7, FR-018 |
| Combinação nível + anos: pendência só em ANO_CONCLUSAO | — | US7.4, FR-020 |
| Pessoa C: Serra 2022 ✓ e Cefor 2025 ✗ (ANO_CONCLUSAO, NAO_ATENDE) | Cenário C | US5.1, FR-029 |
| Atributo necessário ausente → NAO_INFORMADO; mesmo atributo sem critério → sem efeito | Conclusões sem nível, sem unidade, sem ano | US11.1–US11.3, FR-028 |
| NAO_INFORMADO ≠ NAO_ATENDE; duas pendências na ordem fixa | — | US5.2, FR-026 |
| "serra" e "Campus Serra" ≠ "Serra" | — | US7.5, FR-022 |
| Mesma avaliação em EM_PREPARACAO, EM_COLETA, ENCERRADA e datas diferentes → idêntica; nenhuma linha gravada | — | US5.3, US5.4, FR-025, FR-030 |
| Abertura com Versão RASCUNHO rejeitada (`VERSAO_NAO_PUBLICADA`); baseline da 003 continua RASCUNHO | `materializar()` e Versão de teste | US6.1, FR-009 |
| Abertura com Versão PUBLICADA, dentro do período, aceita; `aberta_em = agora` | `versao_publicada()` (instrumento mínimo de teste publicado pela 002) | US6.2 |
| Abertura antes do início e depois do fim rejeitada (`FORA_DO_PERIODO`); no primeiro e no último dia aceita | — | US6.4, FR-036 d |
| Abertura sem período e com Versão RASCUNHO: duas violações | — | US6.3 |
| Período inválido (incompleto, invertido) rejeitado sem alterar o anterior; período de um dia aceito | — | US2, FR-012 |
| Critérios inválidos (conjunto vazio, valor em branco, ano não inteiro ou ≤ 0, mínimo > máximo): todas as violações com `campo` | — | US11.4, FR-023 |
| `None` grava `NULL` e não restringe; `[]` é rejeitado e nunca gravado; valores repetidos gravados uma vez, em ordem estável, sem normalização | — | FR-023, FR-024 |
| Estado E1–E6: antes do início, nunca aberta → EM_PREPARACAO; no período, nunca aberta → EM_PREPARACAO; no período, aberta → EM_COLETA; encerrada antecipadamente → ENCERRADA; depois do fim, aberta → ENCERRADA; depois do fim, nunca aberta → ENCERRADA. Sem período → EM_PREPARACAO em qualquer data. Nenhuma escrita em nenhum caso | Uma Campanha por caso | FR-034, FR-038, US8.6 |
| Separação estado × imutabilidade, casos M-A a M-F: (M-A) nunca aberta no período → EM_PREPARACAO, editável, removível; (M-B) nunca aberta depois do fim → ENCERRADA, não admite, `abrir` → `FORA_DO_PERIODO`, `encerrar` → `CAMPANHA_NUNCA_ABERTA`, editável, removível; (M-C) M-B com período corrigido para o futuro → EM_PREPARACAO, `aberta_em` nulo; (M-D) aberta → `aberta_em` registrado, imutável; (M-E) aberta e encerrada pelo tempo → ENCERRADA, imutável; (M-F) aberta e encerrada antecipadamente → ENCERRADA, imutável | Uma Campanha por caso | FR-039, FR-040, FR-043, FR-044, US8.5–US8.7, US9.6 |
| Encerramento antecipado: ENCERRADA/EXPLICITA, `encerrada_em` registrado, período intacto | — | US8.2 |
| Fim do período: com `agora` no dia seguinte, ENCERRADA/FIM_DO_PERIODO; a linha não mudou (comparação de valores antes e depois) | — | US8.1, FR-038 b |
| `JA_EM_COLETA`, `JA_ENCERRADA`; encerrar Campanha nunca aberta rejeitado (`CAMPANHA_NUNCA_ABERTA`) | — | FR-037, FR-040 |
| Alterar critérios, trocar Versão, alterar período ou nome, remover: rejeitado (`CAMPANHA_JA_ABERTA`) em EM_COLETA e em ENCERRADA após abertura; linha idêntica | — | US9, FR-043, FR-044, SC-005 |
| Remoção de Campanha nunca aberta aceita, em EM_PREPARACAO e em ENCERRADA pelo tempo; Versão intacta | — | US9.4, US9.6 |
| Mesma Conclusão elegível em Campanhas 2025, 2027 e 2030 | — | US10.1, FR-050 |
| Duas Campanhas EM_COLETA sobrepostas devolvidas por `campanhas_em_coleta_para`, em ordem `(inicio, id)` | — | US10.2, FR-051, FR-052 |
| `admite_participacao` verdadeiro sem nenhum convite ou destinatário; falso em EM_PREPARACAO e ENCERRADA | — | US10.4, FR-048, FR-053 |
| Nova Conclusão incorporada (pelo caminho real `incorporar_pessoa`) durante a coleta passa a ser elegível e a contar, sem ação na Campanha | Fonte simulada com cenários incorporados em duas etapas | FR-032 |
| Contagem dinâmica: muda após incorporação; nenhuma coluna de contagem; consistência QuerySet ⇔ `avaliar` | Todas as Campanhas de referência | FR-031–FR-033, SC-007 |
| CHECKs do modelo por escrita direta no ORM | — | data-model |
| Exatamente um modelo novo; nenhum modelo proibido; `Versao` e `ConclusaoAcademica` sem colunas novas; suítes 001–003 inalteradas | Introspecção do registro de apps | SC-009 |

## Complexity Tracking

Vazio. Nenhuma violação a justificar: um modelo, colunas explícitas, estado derivado, sem
dependência nova e sem infraestrutura.

## Necessidade de voltar à spec

Duas revisões mudaram comportamento, e a spec já foi atualizada (Clarifications, FR-037
a FR-040, FR-043, FR-044, US6.4, US8.5–US8.7, US9, Edge Cases):

- o fim do período encerra, para a coleta, também a Campanha nunca aberta;
- a imutabilidade depende só da primeira abertura (`aberta_em`), não do estado
  temporal. Campanha nunca aberta e expirada continua editável e removível, e corrigir
  seu período não é reabertura.

Duas precisões do plan não mudam comportamento especificado:

- **FR-036 c** ("critérios válidos") não aparece como pendência de abertura: o sistema
  impede que critérios inválidos sejam gravados ([operacoes](contracts/operacoes.md#motivos-motivo)).
- **Data de referência**: representa "hoje". O estado em datas passadas anteriores aos
  fatos gravados não é reconstruído (R5), o que a spec não exige.
