# Implementation Plan: Jornada de resposta e conclusão da Participação

**Branch**: `claude/feature-006-jornada-conclusao-726cf0` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-jornada-conclusao-participacao/spec.md`

## Summary

A 006 executa o instrumento sobre a Participação e fecha o seu ciclo:

```text
Versão aplicada (ConteudoVersao, 002) + Respostas atuais (005)
        → percorrer() → passagens (percurso determinado, Seção atual, destinos, pendências)
        → situacao_da_jornada()          (leitura)
        → concluir()                     (única escrita nova)
```

- **Um campo novo e nenhum modelo novo**: `Participacao.concluida_em`, anulável. `NULL` =
  rascunho; preenchido = concluída. Sem enum, sem CHECK novo (R2).
- **Derivação pura** em `trajetoria/participacao/percurso.py`: `percorrer(conteudo,
  respondidas)` devolve as passagens. O módulo não acessa o ORM nem chama consultas da
  002/005: `consultas.py` e `operacoes.py` carregam `ConteudoVersao` (002, reutilizado) e as
  Respostas e entregam as estruturas em memória. Seção como unidade; regra avaliada ao sair da Seção;
  precedência regra → encaminhamento → ordem → finalização; Pergunta com regra
  obrigatória sem resposta → destino indeterminado (R3, R4, R5).
- **Estrutura não suportada**: Versão com Seção de mais de uma Pergunta com regra é
  rejeitada (`ESTRUTURA_NAO_SUPORTADA`), sem precedência inventada (R6).
- **Respostas inativas derivadas**: só as Perguntas das Seções do percurso são lidas;
  fora disso, a Resposta é inativa por construção. Na conclusão, um `DELETE` remove as que
  ficaram fora do percurso final (R7).
- **`concluir`** em `operacoes.py` (único caminho de escrita): bloqueio → idempotência →
  coleta (004) → percurso → pendências → coerência pelas regras da 005 → remoção →
  `concluida_em`; tudo atômico, com todas as violações reunidas (R9, R10).
- **Imutabilidade**: o esqueleto de escrita da 005 rejeita Participação concluída
  (`PARTICIPACAO_CONCLUIDA`) logo após o bloqueio; `admite_escrita` considera a conclusão
  (R11).
- **Concorrência** pelo mesmo bloqueio da Participação já usado pela 005 (R12).
- **Uma consulta**: `situacao_da_jornada(participacao, agora=…)`, valor imutável que
  responde a FR-047 sem funções redundantes (R13).
- **Leitura histórica sem gate temporal**: o estado da Campanha controla criação,
  escrita e conclusão, nunca leitura. Participação concluída é reconstruída em qualquer
  data, sem consultar a Campanha (R18).

As Features 001 a 004 não mudam. A 005 muda apenas no ponto de extensão que ela previu
(005 FR-056): campo, gate de escrita e `admite_escrita`; três asserções de fronteira dos
seus testes acompanham (R16).

## Technical Context

- **Language/Version**: Python 3.13 ([ADR 0001](../../docs/adr/0001-stack-inicial.md)).
- **Primary Dependencies**: Django 5.2 LTS e psycopg 3. Nenhuma dependência nova.
- **Storage**: PostgreSQL 16+. Uma coluna anulável nova (`participacao.concluida_em`) por
  migração aditiva. Nenhuma tabela, índice, CHECK, gatilho ou função nova.
- **Testing**: pytest, pytest-django e ruff, em PostgreSQL, sem rede, com `agora`
  explícito. Testes puros de `percorrer` sobre a baseline materializada em transação
  desfeita; testes de ponta a ponta com cópia da baseline publicada só no banco de teste
  (R15). Concorrência por testes determinísticos e, se estável, um teste com threads.
- **Target Platform**: servidor Linux, para operação futura; nesta feature, execução local
  e CI.
- **Project Type**: aplicação web monolítica (Django), ainda sem camada web, interface ou
  API.
- **Performance Goals**: N/A. Uma jornada lê a Versão (consultas fixas, com prefetch) e as
  Respostas de uma Participação (dezenas). A conclusão acrescenta algumas consultas por
  Resposta ativa (R10), uma vez por Participação.
- **Constraints**:
  - nenhuma alteração em modelos, operações, contratos ou dados das Features 001–004;
  - na 005, só o previsto por FR-056;
  - nada da jornada persistido além de `concluida_em`;
  - nenhuma interface, URL, admin, comando ou API (005/DP-505);
  - nenhum log; nenhum valor declarado em rejeições;
  - somente dados fictícios (005/DP-504).
- **Scale/Scope**: 1 campo, 1 migração, 1 módulo puro novo (`percurso.py`: 1 enum, 1
  dataclass, 4 funções), 1 operação nova (`concluir`), 1 consulta nova
  (`situacao_da_jornada`), 1 consulta alterada (`admite_escrita`), 1 passo novo no
  esqueleto de escrita, 3 motivos novos.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ | ✅ | `concluida_em` dá a referência temporal das declarações consolidadas (FR-004). `concluir` bloqueia e altera só a própria Participação; o início repetido nunca cria segunda Participação (FR-041) ([data-model](data-model.md#ciclo-de-vida)) |
| 2 | Pessoa versus Conclusão Acadêmica (campus/curso no contexto da conclusão) | I, XI | ✅ | ✅ | `percorrer` não recebe Conclusão nem Pessoa; contexto acadêmico continua lido de `participacao.conclusao` (FR-007) |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | ✅ | ✅ | Jornada e conclusão por Participação, isto é, por Conclusão; nada compartilhado (005/DP-501) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | ✅ | ✅ | Nenhuma operação lê ou escreve outra Participação; percurso não usa respostas de outra (FR-008) |
| 5 | Definição institucional de egresso respeitada | II | N/A | N/A | Elegibilidade continua gate de entrada da 005; a conclusão não reavalia |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | Percurso pela Versão aplicada, imutável (FR-006, FR-009); `concluida_em` gravado uma vez; concluída imutável no caminho de escrita (R11); remoção só de Respostas de rascunho fora do percurso final, antes de consolidar (spec, Tensões; Clarifications). Migração só `AddField` anulável |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ | ✅ | Estrutura lida de `conteudo_da_versao(campanha.versao)`; nenhuma Jornada/Sessão funde conceitos; nada do instrumento copiado (R3) |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | ✅ | ✅ | Nenhum metadado novo além de `concluida_em`; sem momento por Seção, canal ou dispositivo (FR-005) |
| 9 | Separação entre dado institucional, derivado e declarado; divergências explícitas | III | ✅ | ✅ | Percurso depende só de respostas declaradas e da Versão; teste com nível da Conclusão diferente de Q14. Percurso, pendências e "fora do percurso" são derivados, não persistidos |
| 10 | Desacoplamento de integrações (providers/adaptadores, mock com mesmo contrato) | V, XV, XXV | ✅ | ✅ | Nenhuma integração; nenhuma autenticação, sessão ou token (FR-051); testes com fonte simulada |
| 11 | Fronteira do NIAE (5 perguntas do Princípio VI, se aplicável) | VI | ✅ | ✅ | Respondidas na spec: Participação e Respostas estão na Fronteira do Domínio |
| 12 | Governança institucional (periodicidade, publicação, competências normativas) | IX, X | ✅ | ✅ | A baseline não é publicada; testes usam cópia publicada só no banco de teste (R15; 002/DP-001). Q1 não é consentimento (FR-024). Semântica de navegação é capacidade desta feature, não regra institucional (DP-604) |
| 13 | Escopo por unidade e visão institucional consolidada | XII | N/A | N/A | Sem consulta por unidade nem autorização (005/DP-505) |
| 14 | Privacidade, minimização e dados pessoais em logs/exportações | XVI, XVII | ⏸ | ⏸ | Concluída guarda só o percurso final; nada de posição ou sessão; nenhum log; rejeições sem valor declarado (R17). **005/DP-504 bloqueia uso real.** Respostas inativas em rascunhos nunca concluídos: 005/DP-503, sem expiração (Clarifications). Consentimento: 002/DP-007, 005/DP-504 |
| 15 | Autorização (menor privilégio; competência técnica ≠ normativa) | X, XII | N/A | N/A | Sem interface, admin, URL, comando ou API (FR-054) |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG, quando houver interface) | XX | N/A | N/A | Sem interface; a consulta não produz tela (FR-049) |
| 17 | Responsividade e jornada móvel | XIV, XXI | ✅ | ✅ | Sem interface. XIV no domínio: só se exige o que é apresentado (FR-020); trocar de ramo e voltar não exige redigitar (R7); retomada sem sessão (R13) |
| 18 | Testes proporcionais ao risco cobrindo invariantes afetados | XXV, XXVI | ✅ | ✅ | [Estratégia de testes](#estratégia-de-testes): 17 percursos, ramos, Q46–Q48, obrigatoriedade, inatividade, conclusão, limpeza, imutabilidade, coleta, estrutura não suportada, concorrência |
| 19 | Risco de over engineering (YAGNI; sem form builder universal) | XXII, XXIII, XXIV | ✅ | ✅ | Um campo, um módulo puro, uma operação, uma consulta; sem Journey, máquina de estados, grafo, cache, cursor, progresso, snapshot, event sourcing, motor de regras ou momento de aplicação configurável. Complexity Tracking vazio |
| 20 | Exportabilidade e semântica das exportações (se aplicável) | XVIII | N/A | N/A | Exportação fora do escopo. `concluida_em` e Respostas só do percurso final facilitam exportação futura |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ | ✅ | DP-601 a DP-604 e herdadas abaixo; quatro decisões de produto confirmadas pelo solicitante (spec, Clarifications) |

**Resultado do gate**: APROVADO (pré-Fase 0 e pós-Fase 1). O item 14 está como DECISÃO
PENDENTE, sem violação: a capacidade é construída e testada só com dados fictícios, e o
uso real continua bloqueado por 005/DP-504.

**Conflitos identificados**: nenhum com a Constituição. Tensões registradas na spec e
resolvidas por decisão do solicitante:

- XIII × adotar a aplicação da regra ao sair da Seção (comportamento do Google
  Formulários): semântica de execução da baseline, não afirmação de intenção
  metodológica (DP-604; 003/DP-302).
- VIII × remover Respostas fora do percurso na conclusão: são valores de rascunho que
  nunca integram a declaração consolidada.
- XVI × Respostas inativas em rascunhos abandonados: 005/DP-503 e 005/DP-504.
- Direito de correção do titular × imutabilidade: DP-603.

**Revisão pós-implementação (2026-10-01, T038)**: gate mantido. Definition of Done
atendida:

- suíte completa: **800 testes verdes** (689 anteriores + 111 da 006, em 8 arquivos
  `tests/participacao/test_jornada_*.py`); `ruff check`, `manage.py check` e
  `makemigrations --check` limpos;
- **um único campo novo**, `Participacao.concluida_em` (anulável, sem default), numa
  migração `0002_participacao_concluida_em` com um só `AddField`, sem backfill, `RunPython`
  ou `RunSQL`; nenhum modelo, tabela, índice, CHECK, gatilho ou sinal novo;
- `percurso.py` **sem I/O**: seus testes unitários rodam sem `django_db` (o pytest-django
  bloquearia o banco) e um teste lê o código-fonte e prova que ele não importa ORM,
  `conteudo_da_versao`, `respostas_atuais`, `consultas` nem `operacoes`;
- **leitura histórica sem gate temporal**: a consulta de uma Participação concluída roda
  com `estado` substituído por uma função que falha, e devolve em 2030 o mesmo percurso,
  `concluida_em` e Respostas de 2027; a conclusão repetida não chama `estado`,
  `conteudo_da_versao`, `respostas_atuais` nem `percorrer`;
- **17 percursos** da 003 verificados duas vezes: puros, sobre a baseline materializada,
  com todas as Perguntas respondidas (o que prova a inatividade das respostas fora do
  percurso), e de ponta a ponta numa cópia publicada só no banco de teste; o oráculo
  `PERCURSOS` não entrou em produção; a baseline continua RASCUNHO;
- **concorrência**: o teste determinístico com `CaptureQueriesContext` prova o `SELECT …
  FOR UPDATE` na Participação antes de qualquer leitura de Respostas (também na
  conclusão repetida); o teste com threads passou em 10 execuções seguidas e foi mantido;
- **ordem aprovada** de `concluir`: bloqueio → `JA_CONCLUIDA` → coleta → percurso →
  pendências → coerência (validadores da 005, por `_verificar_resposta_gravada`) → só
  então remoção das inativas e `concluida_em`; conclusão rejeitada não remove nada
  (testado com respostas inativas presentes);
- `situacao_da_jornada` e `admite_escrita` usam uma única regra privada de "admite
  escrita" (achado D1 do analyze);
- **Features 001–004**: `git diff main` vazio em `trajetoria/academico`,
  `fonte_academica`, `instrumento`, `formulario_2024`, `campanha`, `config/` e nos testes
  dessas features. **Feature 005**: só `models.py` (campo), `regras.py` (3 motivos),
  `operacoes.py` (passo 2a, `concluir`, extração de `_escala_da_pergunta` sem mudança de
  comportamento) e `consultas.py` (`situacao_da_jornada`, `admite_escrita`); nenhum
  `admin.py`, `urls.py`, `views.py` ou `management/`;
- **desvio registrado**: além das três asserções de fronteira previstas em R16, uma
  quarta (`test_nao_existe_reinicio_nem_tentativa`, igualdade exata de
  `operacoes.__all__`) recebeu o mesmo ajuste: a igualdade foi mantida, com os três nomes
  da 006 acrescentados (research R16). Nenhum outro teste da 005 mudou;
- nada da lista "Limites" do tasks.md foi criado; nenhum log; nenhuma mensagem de
  rejeição contém valor declarado (testado);
- somente dados fictícios; DP-601 a DP-604, 005/DP-502 a DP-504 e as demais herdadas
  continuam abertas, sem regra implícita;
- **code review (2026-10-01)**: sete achados corrigidos, com testes de regressão (805
  testes no total):
  - `situacao_da_jornada` lê Participação e Respostas numa transação, com a linha da
    Participação em `FOR NO KEY UPDATE`, sem estado misturado durante uma conclusão;
  - `admite_escrita` de Participação inexistente devolve `False` (contrato da 005);
  - Pergunta com regra cuja Resposta não tem Opção → `VALOR_VAZIO`, não
    `OPCAO_DE_OUTRA_PERGUNTA`;
  - a coerência das Respostas ativas usa as Opções já lidas por `respostas_atuais`
    (`relida=True`/`relidas=True` nos validadores da 005): número fixo de consultas ao
    instrumento por conclusão;
  - a Versão vem junto do bloqueio (`select_related("campanha__versao")`), sem leitura
    avulsa;
  - a violação de coleta tem um só construtor (`regras.coleta_nao_admitida`), usado por
    início, escritas, conclusão e consulta; `respondidas` passou para `percurso.py`;
  - `concluir` calcula as Perguntas ativas uma vez, para validar e para remover;
- Complexity Tracking continua vazio.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-601 | Interpretação de Participação concluída por recusa (Q1 = "Não") | CPAEG/Proex + encarregado de dados | Concluída com uma única Resposta; nenhum efeito fora da Participação | Classificação derivada da Resposta a Q1 em feature de indicadores; nada no modelo muda |
| DP-602 | Exigir complemento de "Outro:" para concluir | CPAEG | Não exigido | Um item a mais em `pendencias` para a Opção com complemento selecionada sem texto, por spec própria |
| DP-603 | Correção ou edição após a conclusão | CPAEG + encarregado de dados | Concluída imutável; sem reabertura | Operação aditiva por spec própria, com preservação do valor original |
| DP-604 | Outra semântica de navegação para Versões futuras (desvio imediato, várias Perguntas com regra por Seção); intenção de Q47/Q48 (003/DP-302) | CPAEG + spec própria | Seção como unidade; regra ao sair; estrutura fora disso rejeitada | Localizado em `percurso.destino`/verificação de suporte; capacidade nova por spec |
| 005/DP-502 | Prazo de graça | CPAEG/Proex | Nenhuma conclusão fora de `EM_COLETA` | Gate localizado no passo 5 de `concluir` |
| 005/DP-503 | Destino de rascunhos não concluídos, inclusive respostas inativas | CPAEG + encarregado de dados | Preservados; sem expiração | Operação aditiva por spec própria |
| 005/DP-504, 002/DP-007 | Base legal, consentimento, termo | Encarregado de dados + CPAEG | Q1 é Resposta comum; **só dados fictícios** | Feature própria relaciona termo, momento, Participação e manifestação |
| 003/DP-302 | Intenção de Q47/Q48 | CPAEG | Execução resolvida (Seção como unidade); intenção segue em DP-604 | Nova Versão do instrumento + DP-604 |

Também continuam abertas 002/DP-001, 002/DP-006, 003/DP-303, 003/DP-304, 003/DP-307,
003/DP-309, 004/DP-404, 004/DP-406, 005/DP-501, 005/DP-505 a 005/DP-508 (spec, Decisões
Pendentes).

## Desenho

### Modelo

[data-model.md](data-model.md): `Participacao.concluida_em = DateTimeField(null=True)`,
migração `0002_participacao_concluida_em` (`AddField`). Nada mais.

### Reconstrução do percurso

[contracts/percurso.md](contracts/percurso.md). `percorrer(conteudo, respondidas)` —
puro: recebe a árvore da 002 já carregada e `respondidas` (Pergunta → Opção escolhida ou
`None`); não acessa o ORM:

1. rejeita `ESTRUTURA_NAO_SUPORTADA` se alguma Seção tem mais de uma Pergunta com regra;
2. começa na primeira Seção; para cada Seção alcançada calcula `pendentes` (obrigatórias
   sem Resposta) e `destino`;
3. para em: pendentes, destino `INDETERMINADA` ou `FINALIZACAO`; senão segue ao destino.

**Precedência de destino** (FR-012):

| # | Condição | Destino |
|---|----------|---------|
| 1 | Pergunta com regra respondida, Opção com regra | Seção da regra ou `FINALIZACAO` |
| 2 | Pergunta com regra obrigatória sem Resposta | `INDETERMINADA` |
| 3 | Encaminhamento da Seção | Seção do encaminhamento |
| 4 | Seção seguinte na ordem | ela |
| 5 | — | `FINALIZACAO` |

**Percurso parcial**: as passagens até a Seção atual, nunca além. A última passagem diz
se a jornada está finalizada, se falta resposta obrigatória (pendentes) e se o destino já
é conhecido ou ainda `INDETERMINADA` (R5).

**Obrigatoriedade**: só Perguntas das Seções das passagens são lidas. Pendências são as
da Seção atual; Seções anteriores estão satisfeitas por construção (R8).

**Respostas inativas**: `fora_do_percurso` = Perguntas com Resposta que não estão em
`perguntas_do_percurso(passagens)`. Sem coluna nem flag (R7).

### Conclusão

[contracts/conclusao.md](contracts/conclusao.md). `concluir(participacao, *, agora=None)`:

1. `TypeError` para argumento errado;
2. transação; `_bloquear` (o mesmo da 005);
3. já concluída → `JA_CONCLUIDA` (nada lido, nada gravado);
4. relógio lido após o bloqueio;
5. coleta (`estado` da 004);
6. Versão (`conteudo_da_versao`) e Respostas (`respostas_atuais`);
7. `percorrer` (estrutura não suportada);
8. `pendencias`;
9. coerência das Respostas ativas pelos validadores da 005 (`_verificar_resposta_gravada`);
10. qualquer violação → rejeita com todas; nada gravado;
11. remove Respostas fora do percurso final (`exclude(pergunta_id__in=…)`; seleções por
    `CASCADE`);
12. grava `concluida_em`;
13. devolve `CONCLUIDA`.

### Imutabilidade (alteração da 005)

- `_escrever`: passo **2a** após `_bloquear` — `concluida_em` preenchido →
  `PARTICIPACAO_CONCLUIDA`, antes da verificação de coleta.
- `admite_escrita`: `concluida_em` nulo (relido) e Campanha EM_COLETA.
- `responder_escala`: a verificação do valor é extraída para `_escala_da_pergunta`, sem
  mudar o comportamento, para que a conclusão a reuse (R10).
- `iniciar_participacao`, as demais validações e todas as consultas da 005: inalteradas.

### Concorrência

| Garantia | Mecanismo |
|----------|-----------|
| Um `concluida_em` | `select_for_update(of=("self",))` + releitura de `concluida_em` → `JA_CONCLUIDA` |
| Uma única limpeza | a segunda conclusão para no passo 3, antes de ler Respostas |
| Nenhuma escrita após concluir | escritas bloqueiam a mesma linha e verificam `concluida_em` no passo 2a |
| Conclusão × encerramento explícito | vale o estado no momento de referência da conclusão, como nas escritas da 005 (005 R11) |

### Consulta

[contracts/consultas.md](contracts/consultas.md). `situacao_da_jornada(participacao, *,
agora=None) -> SituacaoDaJornada` com `concluida_em`, `passagens`, `finalizada`,
`secao_atual`, `respostas`, `fora_do_percurso`, `impedimentos`, `admite_escrita` e
`pode_concluir`. Lê Participação, Versão e Respostas uma vez cada.

**Leitura histórica** (R18): nenhuma pré-condição de coleta. Para Participação concluída,
não consulta o estado da Campanha; para rascunho, `agora` só informa `admite_escrita` e
`COLETA_NAO_ADMITIDA`. A mesma Participação concluída devolve o mesmo resultado em
qualquer data.

### Tempo

`agora` em `concluir` e `situacao_da_jornada`, interpretado por `momento_de_referencia` e
`estado` da 004 (R14). Nenhum relógio novo.

## Project Structure

### Documentation (this feature)

```text
specs/006-jornada-conclusao-participacao/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # R1–R18
├── data-model.md        # Participacao + concluida_em; valores derivados
├── quickstart.md        # validação
├── contracts/
│   ├── percurso.md      # percorrer, Passagem, Saida, precedência
│   ├── conclusao.md     # concluir, motivos novos, gate de escrita
│   └── consultas.md     # situacao_da_jornada, admite_escrita
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks (não criado por este comando)
```

### Source Code (repository root)

```text
trajetoria/participacao/
├── models.py                         # + Participacao.concluida_em
├── regras.py                         # + PARTICIPACAO_CONCLUIDA, ESTRUTURA_NAO_SUPORTADA,
│                                     #   OBRIGATORIA_PENDENTE
├── percurso.py                       # NOVO, puro (sem ORM): Saida, Passagem, percorrer,
│                                     #   finalizada, perguntas_do_percurso, pendencias
├── operacoes.py                      # + concluir, SituacaoConclusao, ResultadoConclusao,
│                                     #   _verificar_resposta_gravada, _escala_da_pergunta;
│                                     #   _escrever: passo 2a
├── consultas.py                      # + situacao_da_jornada, SituacaoDaJornada;
│                                     #   admite_escrita considera a conclusão
└── migrations/
    └── 0002_participacao_concluida_em.py   # NOVO (AddField)

trajetoria/campanha/, academico/, instrumento/, fonte_academica/, formulario_2024/
                                      # inalterados (consumidos: estado,
                                      # momento_de_referencia, conteudo_da_versao,
                                      # materializar em testes)

tests/participacao/
├── construcao.py                     # + baseline_publicada() (cópia publicada em teste),
│                                     #   preencher_percurso(), conteúdo em memória e
│                                     #   `respondidas` para testes puros
├── test_jornada_modelo.py            # NOVO (campo e migração)
├── test_jornada_percurso.py          # NOVO (sem banco)
├── test_jornada_baseline.py          # NOVO
├── test_jornada_situacao.py          # NOVO
├── test_jornada_conclusao.py         # NOVO
├── test_jornada_imutabilidade.py     # NOVO
├── test_jornada_concorrencia.py      # NOVO
├── test_jornada_aceitacao.py         # NOVO
├── test_participacao_aceitacao.py    # ajuste de fronteira (R16)
└── test_participacao_rascunho.py     # ajuste de fronteira (R16)

README.md                             # + link para o quickstart da 006
```

**Structure Decision**: sem app novo. A jornada é um módulo puro dentro de
`participacao`, que já depende de `campanha` e `instrumento`; a escrita continua num só
módulo (`operacoes.py`). Nenhum app anterior passa a depender de `participacao`. Sem
camada de serviço, repositório, sinais, tarefas ou objeto de jornada.

## Estratégia de testes

O foco são os invariantes (XXVI). Todo teste temporal passa `agora` explícito. Testes
puros usam a baseline materializada em transação desfeita (fixture `baseline` da 003) e o
oráculo `PERCURSOS` (`tests/instrumento/formulario_2024_esperado.py`); testes de ponta a
ponta usam uma cópia da baseline publicada só no banco de teste e Versões mínimas
montadas pelas operações da 002 (R15). Somente dados fictícios.

| Teste | Requisito |
|-------|-----------|
| Percurso linear sem regras: S1 → S2 → S3 → finalização; Seções satisfeitas | US2.1, US2.4, FR-012 d, e |
| Encaminhamento prevalece sobre a ordem; regra prevalece sobre encaminhamento | US2.2, US2.3, FR-012 |
| Pergunta com regra opcional sem resposta → encaminhamento ou ordem; obrigatória sem resposta → `INDETERMINADA` | FR-012 b, c; percurso parcial |
| Seção atual com destino já conhecido (S11: Q46 respondida, Q47 pendente) | US5.2, R5 |
| Pendências só da Seção atual; opcionais nunca pendentes | US3, FR-019–FR-021 |
| Resposta fora do percurso não satisfaz, não gera pendência, não decide destino (respostas a todas as Perguntas da Versão não mudam o percurso) | FR-030 |
| Determinismo: mesmas respostas em ordens e com alterações intermediárias diferentes → mesmas passagens | US1.4, FR-017, SC-009 |
| Baseline: 17 percursos do oráculo `PERCURSOS`, puros e de ponta a ponta | US4.6, FR-027, SC-001 |
| Q1 = "Sim" → S2; Q1 = "Não" → S1 finalizada; conclusão só com Q1; respostas de S2 removidas | US4.1, US10, FR-022, FR-023, SC-007 |
| Q14: quatro destinos S4–S7 e convergência em S8 | US4.2 |
| Q33 Sim/Não: S9/S10, convergência em S11; Q34–Q44 não exigidas com "Não" | US4.3, SC-004 |
| Q46 Sim/Não: S12 → S13 / S13; Q46, Q47, Q48 em S11; Q47 exigida com Q46 = "Não"; Q48 nunca exigida | US4.4, US5, FR-025, SC-002 |
| Q51 sem regra; saída de S12 pelo encaminhamento com qualquer Opção | US4.5, FR-026 |
| Nível da Conclusão ≠ Q14: percurso segue Q14 | US1.6, FR-007 |
| Versão posterior publicada não muda o percurso de Campanha anterior | US1.5, FR-006, SC-010 |
| Duas Perguntas com regra na mesma Seção: consulta e conclusão → `ESTRUTURA_NAO_SUPORTADA`, Versão intacta | US12.1, US12.2, FR-016 |
| Retomada: nova consulta (e `iniciar_participacao` repetido) reproduz o mesmo percurso; nada gravado | US8, FR-005, FR-018 |
| Leitura histórica: concluída durante a coleta; consulta anos depois do encerramento → mesmas passagens, `concluida_em` e Respostas; escrita rejeitada; rascunho de Campanha encerrada consultável, conclusão rejeitada, nada apagado | FR-042, FR-048, R18 |
| `percurso.py` sem I/O: testes unitários sem `django_db`; o módulo não importa `django.db`, modelos, `conteudo_da_versao` nem `respostas_atuais` | R1, contracts/percurso.md "Pureza" |
| Mudança de ramo mantém respostas antigas em `fora_do_percurso`; voltar ao ramo as reativa sem reescrita | US9.1, US9.3, FR-030 |
| Conclusão válida: `concluida_em = agora`; respostas do percurso idênticas; `CONCLUIDA` | US6.1, FR-034, FR-035 |
| Conclusão remove respostas fora do percurso, inclusive seleções de múltipla (troca de Q33 e de Q14) | US9.2, US9.4, FR-032, SC-006 |
| Conclusão rejeitada (pendência, coleta, estrutura) não remove nada; todas as violações reunidas | US9.6, FR-033, FR-037, FR-044 |
| Obrigatória do percurso bloqueia, com a Pergunta no detalhe; obrigatória fora do percurso não bloqueia | US6.2, SC-003, SC-004 |
| "Outro:" selecionada sem complemento em obrigatória: conclui | FR-028 |
| Campanha encerrada explicitamente e por data: conclusão rejeitada; último dia aceito; rascunho intacto; concluída continua consultável | US11, FR-042, SC-008 |
| Resposta incoerente gravada por ORM (Opção de outra Pergunta): conclusão rejeitada com o motivo da 005 e a Pergunta | US12.3, FR-045 |
| Conclusão repetida: `JA_CONCLUIDA`, mesmo `concluida_em`, nada removido, inclusive com Campanha encerrada | US7.2, FR-036, SC-005 |
| Após a conclusão: quatro `responder_*` e `remover_resposta` → `PARTICIPACAO_CONCLUIDA` (Campanha EM_COLETA e encerrada); `admite_escrita` falso; `iniciar_participacao` → `JA_EXISTENTE` | US7, FR-038–FR-041, SC-005 |
| `situacao_da_jornada` de Participação concluída: finalizada, sem pendências, `fora_do_percurso` vazio, `pode_concluir` falso | FR-048 |
| Consultas não gravam (linhas idênticas antes e depois) | FR-049 |
| Concorrência: duas conclusões com threads e barreira → um `concluida_em` (mantido só se estável); conclusão × escrita → escrita antes considerada ou rejeitada | FR-043, SC-011 |
| Mensagens de rejeição não contêm texto, inteiro ou complemento declarados | FR-046 |
| Único campo novo: `Participacao.concluida_em`; app com os mesmos três modelos; nenhum modelo proibido; `Resposta` e modelos 001–004 sem colunas novas | FR-052, FR-053, SC-012 |
| As 11 perguntas de sucesso do solicitante, ponta a ponta | spec, "Cobertura" |

## Complexity Tracking

Vazio. Nenhuma violação a justificar: um campo anulável, um módulo de funções puras, uma
operação e uma consulta, sem dependência nova, sem modelo novo e sem infraestrutura.

## Necessidade de voltar à spec ou às features anteriores

**Spec**: nenhuma mudança de comportamento. Precisões do plan que não alteram requisitos:

- FR-047 (i) "indicação de estrutura não suportada" é uma rejeição explícita da consulta
  (`ESTRUTURA_NAO_SUPORTADA`), porque não há percurso válido a devolver (R13).
- FR-037 (d) não precisa de motivo "destino indeterminado": o destino só fica
  indeterminado quando a Pergunta com regra obrigatória está sem Resposta, e ela já é
  `OBRIGATORIA_PENDENTE` (R8).
- FR-045 usa os motivos da 005 para Respostas incoerentes, sem motivo novo (R10); a
  verificação é feita só na conclusão.
- FR-047 (g): `impedimentos` da consulta reúne as condições (b) coleta, (c) estrutura —
  como rejeição, ver acima — e (d) pendências de FR-034. A condição (e), coerência das
  Respostas, só pode falhar por escrita fora das operações e é verificada apenas em
  `concluir` (R10; [contracts/consultas.md](contracts/consultas.md)). Por isso
  `pode_concluir` verdadeiro não garante a conclusão nesse caso anômalo. O texto de
  FR-047 (g) foi ajustado na spec para dizer isso.
- A Clarification lista a conclusão como "remover → validar → registrar"; o plan valida
  antes de remover. Dentro da mesma transação o efeito é o mesmo, e validar antes evita
  escrita inútil (R9).

**Feature 005 — ponto de extensão previsto (FR-056)**: campo `concluida_em`, passo 2a do
esqueleto de escrita, `admite_escrita` e extração de `_escala_da_pergunta` (refatoração
sem mudança de comportamento). Três asserções de fronteira dos testes da 005 mudam
(R16): elas proibiam `concluir`/`concluida_em`, que a própria 005 reservou à 006. Os
demais testes da 005 devem continuar passando sem alteração.

**Features 001 a 004**: nenhuma alteração.

**Base do branch**: este branch parte da `main` com a 005 incorporada (saymoncastro/ifes-trajetoria-egressos#7). Antes de
abrir o PR da 006, atualizar de novo contra `main`.
