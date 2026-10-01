# Implementation Plan: Contextualização da formação e entrada na pesquisa

**Branch**: `claude/feature-007-contextualizacao-formacao-ca197a` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-contextualizacao-formacao-entrada/spec.md`

## Summary

A 007 liga "a Pessoa já está resolvida" a "a Participação certa está em mãos", compondo
contratos existentes:

```text
Pessoa (001, já resolvida)
  → Conclusões Acadêmicas (001)                       leitura
  → campanhas_em_coleta_para(conclusao, agora) (004)  leitura, 1 por Conclusão
  → Participação do par, se 1 Campanha (005/006)      1 leitura para todas
  → situação de cada formação + resolução global      derivação pura
  → entrar(): iniciar_participacao (005)              única escrita (da 005)
  → Participação entregue à jornada (006)
```

- **Zero modelos novos, zero migrações.** Tudo derivado de 001–006 (R2).
- **Um módulo novo**, `trajetoria/participacao/entrada.py`, sem app novo e sem tocar em
  `operacoes.py`, `consultas.py`, `models.py` ou `regras.py` da 005/006 (R1).
- **Classificação por formação** (R5): 0 Campanhas → `SEM_PESQUISA`; ≥ 2 →
  `AMBIGUIDADE_OPERACIONAL` (Participação não consultada); 1 → `DISPONIVEL_PARA_INICIAR`,
  `DISPONIVEL_PARA_RETOMAR` ou `JA_CONCLUIDA`, conforme a Participação do par. Só as duas
  primeiras de "disponível" são **entrada pendente**.
- **Resolução global** (R5): zero formações → `SEM_FORMACAO`; formações sem nenhuma
  Campanha aplicável → `SEM_PESQUISA`; 1 pendente → `ENTRADA_RESOLVIDA`; 2+ →
  `SELECAO_NECESSARIA`; pesquisa aplicável e zero pendentes → `SEM_ENTRADA_PENDENTE`
  (todas concluídas, só ambíguas, mistura, com ou sem formações sem pesquisa). Não há
  ambiguidade global: ela é local à formação. Concluídas e ambíguas são sempre
  devolvidas, mas nunca contam como alternativa.
- **Entrada** (R7): reavalia no próprio momento, sem token nem snapshot; sem formação
  informada só procede em `ENTRADA_RESOLVIDA`; formação de outra Pessoa →
  `FormacaoDeOutraPessoa` antes de chamar a 005; para formação pendente chama
  `iniciar_participacao` (005), que cria ou devolve a existente; `JA_CONCLUIDA` devolve a
  Participação sem chamar a 005; `SEM_PESQUISA`/ambígua não cria nada.
- **Estruturas finais** (YAGNI, revisadas após o plan): 2 enums (`SituacaoDaFormacao`,
  com `pendente`; `ResolucaoDaEntrada`), 3 dataclasses imutáveis (`Formacao`,
  `SituacaoDeEntrada`, `Entrada`) e 1 exceção (`FormacaoDeOutraPessoa`). Removidos:
  `DesfechoDaEntrada`, `Entrada.formacao`, `SituacaoDeEntrada.pessoa/.momento/.resolvida`,
  `Formacao.entrada_pendente` ([data-model](data-model.md#simplificações-por-yagni-em-relação-ao-primeiro-desenho-do-plan)).
- **Consultas**: no máximo 3 + N (N = Conclusões da Pessoa, tipicamente 1–4), sem cache,
  índice ou materialização (R3, R4).
- Nenhuma autenticação, sessão, URL, view, API, indicador ou exportação.

## Technical Context

- **Language/Version**: Python 3.13 ([ADR 0001](../../docs/adr/0001-stack-inicial.md)).
- **Primary Dependencies**: Django 5.2 LTS e psycopg 3. Nenhuma dependência nova.
- **Storage**: PostgreSQL 16+. **Nenhuma** tabela, coluna, índice, CHECK, gatilho ou
  migração nova. Leitura de `academico_pessoa`, `academico_conclusaoacademica`,
  `campanha_campanha` e `participacao_participacao`; escrita só pela 005.
- **Testing**: pytest, pytest-django e ruff, em PostgreSQL, sem rede, com `agora`
  explícito. Classificação global também testada por tabela, sem banco. Contagem de
  consultas com `django_assert_max_num_queries`. Participações concluídas nos testes pela
  006 (`preencher_instrumento` + `concluir`).
- **Target Platform**: servidor Linux, para operação futura; nesta feature, execução local
  e CI.
- **Project Type**: aplicação web monolítica (Django), ainda sem camada web, interface ou
  API.
- **Performance Goals**: N/A além de proporcionalidade: uma consulta de situação faz
  1 (Pessoa gravada) + 1 (Conclusões) + N (Campanhas aplicáveis por Conclusão, contrato da
  004) + 0–1 (Participações dos pares) consultas. `entrar` acrescenta as da 005 (2–4).
- **Constraints**:
  - nenhuma alteração em modelos, operações, consultas, regras, contratos ou testes das
    Features 001–006 (FR-052);
  - critérios, período e estado só pela 004; nenhum filtro copiado (FR-013);
  - Participação criada só por `iniciar_participacao` (FR-033);
  - nada da jornada (006) usado para decidir formação (FR-036);
  - nenhuma Resposta criada; nada copiado da Conclusão (FR-040, FR-041);
  - nenhuma interface, URL, admin, comando, API, log (FR-049; Observabilidade);
  - somente dados fictícios (001/DP-009; 005/DP-504).
- **Scale/Scope**: 1 módulo novo (`entrada.py`: 2 enums, 3 dataclasses imutáveis, 1
  exceção, 2 funções públicas, 2 funções privadas puras); 3 arquivos de teste novos e 1
  auxiliar de testes (`tests/participacao/construcao_entrada.py`); 1 linha no README.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ | ✅ | A entrada sempre alcança a Participação do par (Campanha aplicável agora, Conclusão) pela 005; Participações de Campanhas anteriores não são consultadas nem reutilizadas; nova Campanha → nova Participação (caso K) ([contrato](contracts/entrada.md)) |
| 2 | Pessoa versus Conclusão Acadêmica (campus/curso no contexto da conclusão) | I, XI | ✅ | ✅ | `Formacao.conclusao` é a instância da 001; nada lido ou gravado na Pessoa além do `pk`; cada formação com sua unidade (caso L da spec) |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | ✅ | ✅ | Todas as Conclusões devolvidas, distintas pelo `id`; 2+ pendentes → seleção sem ranking; uma Participação por formação (005 FR-009) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | ✅ | ✅ | Nenhuma escrita além de `iniciar_participacao`, que não altera Participação existente; concluída nunca reaberta (R7) |
| 5 | Definição institucional de egresso respeitada | II | ✅ | ✅ | Só Conclusões incorporadas pela 001 (reconhecidas como concluídas); elegibilidade pela 004; nenhuma formação manual (FR-010) |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | Nenhuma migração; nenhum dado alterado; concluída devolvida sem chamar escrita |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ | ✅ | O egresso escolhe a formação; a Campanha é derivada pela 004; a Participação é a do par; nenhum conceito fundido |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | ✅ | ✅ | O contexto vem da Conclusão com fonte e referência de origem da 001, sem cópia; nenhum metadado de entrada gravado (FR-037) |
| 9 | Separação entre dado institucional, derivado e declarado; divergências explícitas | III | ✅ | ✅ | Atributos da Conclusão só identificam e contextualizam; 0 Respostas criadas (caso L); Q10–Q19 intocadas (FR-041; 003/DP-307); nenhuma comparação (005/DP-508). Situações são derivadas, não persistidas |
| 10 | Desacoplamento de integrações (providers/adaptadores, mock com mesmo contrato) | V, XV, XXV | ✅ | ✅ | Recebe Pessoa do NIAE, independente de mecanismo de identidade; não importa fonte acadêmica nem incorporação (FR-053); nenhuma autenticação, sessão ou token |
| 11 | Fronteira do NIAE (5 perguntas do Princípio VI, se aplicável) | VI | ✅ | ✅ | Respondidas na spec; identidade, Portal e BI ficam fora |
| 12 | Governança institucional (periodicidade, publicação, competências normativas) | IX, X | ✅ | ✅ | Nenhuma regra de período ou prioridade; Campanhas sobrepostas não resolvidas (004/DP-404); nenhuma Versão publicada fora do banco de teste |
| 13 | Escopo por unidade e visão institucional consolidada | XII | N/A | N/A | Sem consulta administrativa nem autorização (005/DP-505) |
| 14 | Privacidade, minimização e dados pessoais em logs/exportações | XVI, XVII | ⏸ | ⏸ | Só formações da própria Pessoa; formação alheia rejeitada sem dados dela; consulta não grava; nenhum log; capacidade não exposta (FR-049). **001/DP-009 e 005/DP-504 bloqueiam uso real** |
| 15 | Autorização (menor privilégio; competência técnica ≠ normativa) | X, XII | N/A | N/A | Sem interface, admin, URL, comando ou API; a exposição depende da fronteira de identidade (004/DP-406) |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG, quando houver interface) | XX | N/A | N/A | Sem interface; resultado de domínio, não tela (FR-050) |
| 17 | Responsividade e jornada móvel | XIV, XXI | ✅ | ✅ | Sem interface. XIV no domínio: 1 entrada pendente dispensa seleção, mesmo com concluídas/ambíguas; concluídas não aumentam alternativas; Campanha nunca exposta como escolha |
| 18 | Testes proporcionais ao risco cobrindo invariantes afetados | XXV, XXVI | ✅ | ✅ | [Estratégia de testes](#estratégia-de-testes): casos A–L do solicitante, A–O da spec, tabela pura da resolução, consultas contadas, fronteiras |
| 19 | Risco de over engineering (YAGNI; sem form builder universal) | XXII, XXIII, XXIV | ✅ | ✅ | Um módulo, duas funções públicas, valores imutáveis; sem app, modelo, migração, cache, sessão, seleção persistida, resolvedor de identidade ou workflow. Complexity Tracking vazio |
| 20 | Exportabilidade e semântica das exportações (se aplicável) | XVIII | N/A | N/A | Fora do escopo. Participação → Conclusão já basta para dimensões futuras (FR-043) |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ | ✅ | DP-701 a DP-703 e herdadas abaixo; a regra de concluídas e a ambiguidade local foram decididas pelo solicitante (spec, Clarifications), sem resolver regra institucional |

**Resultado do gate**: APROVADO (pré-Fase 0 e pós-Fase 1). O item 14 está como DECISÃO
PENDENTE, sem violação: a capacidade é construída e testada só com dados fictícios e não
é exposta.

**Conflitos identificados**: nenhum. Tensões registradas na spec, sem violação:

- XIV × Q10–Q19 perguntadas depois da contextualização: 003/DP-307 não decidida.
- XIV × ambiguidade bloqueia a formação afetada: efeito correto de 004/DP-404; as demais
  formações seguem.
- 001 FR-039 × `SEM_FORMACAO`: ramo explícito, sem abstração, testado com Pessoa criada
  diretamente.

**Revisão pós-implementação (2026-10-01, T026)**: gate mantido. Definition of Done
atendida:

- suíte completa: **916 testes verdes** após o code review (805 anteriores + 111 da 007, em
  `tests/participacao/test_entrada_situacao.py`, `test_entrada_entrar.py` e
  `test_entrada_aceitacao.py`); `ruff check`, `manage.py check` e
  `makemigrations --check` limpos;
- **zero modelos, zero migrações**: `participacao` continua com `Participacao`,
  `Resposta` e `RespostaOpcao` e com as migrações `0001` e `0002`;
- **um único arquivo de produção novo**, `trajetoria/participacao/entrada.py`; `git diff
  main` em `trajetoria/`, `config/` e nos testes existentes vazio; fora dos arquivos novos,
  só uma linha no `README.md`;
- estruturas finais: 2 enums (`SituacaoDaFormacao` com `pendente`;
  `ResolucaoDaEntrada`), 3 dataclasses imutáveis (`Formacao`, `SituacaoDeEntrada`,
  `Entrada`) e `FormacaoDeOutraPessoa`; 2 funções puras (`_classificar`, `_resolver`)
  testadas sem banco, inclusive com todas as combinações de até 3 formações;
- **consultas**: `situacao_de_entrada` dentro de 3 + N (verificado com
  `django_assert_max_num_queries`); a classificação segue exclusivamente o que
  `campanhas_em_coleta_para` devolve (verificado com dublê de tuplas controladas);
- **escrita protegida por comportamento**, sem inspeção do código-fonte: consulta sem
  alteração de linhas; dublê de `iniciar_participacao` que não grava não resulta em
  `Participacao` nova; delegação com `(campanha, conclusão, agora)` exatos; nenhuma
  chamada à 005 quando não há entrada pendente, inclusive para formação alheia;
- **teste com threads** (entradas simultâneas → uma Participação) estável em 10
  execuções seguidas e mantido;
- reavaliação no momento da entrada testada para Campanha encerrada, nova Campanha
  sobreposta, Participação criada e Participação concluída entre a consulta e a entrada;
- **code review (2026-10-01)**: sete achados corrigidos com testes — a 005 recebe o
  `agora` original (regressão: Campanha encerrada entre a avaliação e o início é
  rejeitada); formação alheia ou inexistente com a mesma rejeição (sem oráculo de
  existência); testes de aceitação de autenticação e de BI mais fortes e sem substring
  frágil; sem repetição dos `__all__` da 005/006; `_exigir` reutilizado; condição "uma
  Campanha" sem repetição. Mantida por desenho a releitura da Participação pela 005 (R7);
- Complexity Tracking continua vazio; DP-701 a DP-703 e as herdadas continuam abertas,
  sem regra implícita; somente dados fictícios.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-701 | Comunicação da ambiguidade operacional ao egresso e à governança | Proex/CPAEG, DIREC/CSAEG | Formação marcada `AMBIGUIDADE_OPERACIONAL` com as Campanhas; nada notificado | Feature de comunicação/interface consome a mesma consulta |
| DP-702 | Como distinguir formações indistinguíveis pelos atributos | CPAEG + registro acadêmico + encarregado de dados | Distintas pelo `id`; só atributos existentes; nenhum rótulo | Novo atributo na 001 por spec própria; a consulta já devolve a Conclusão inteira |
| DP-703 | Significado operacional de Participação criada na entrada e sem Respostas | CPAEG/Proex | Criada pela 005 ao entrar; nenhuma métrica | Feature de acompanhamento da coleta define a classificação, sem mudar a entrada |
| 004/DP-404 | Campanhas EM COLETA sobrepostas | CPAEG | Ambiguidade local; sem prioridade; Participação não desempata | Regra institucional aplicada na 004 (configuração) ou na classificação de `AMBIGUIDADE_OPERACIONAL`, localizada em uma função |
| 004/DP-406 | Forma de acesso e mecanismo de identificação | Proex, DTI | Recebe Pessoa já resolvida; nada exposto | Fronteira de identidade chama `situacao_de_entrada`/`entrar` |
| 005/DP-501 | Várias Conclusões elegíveis da mesma Pessoa na mesma Campanha | CPAEG | Seleção de formação; uma Participação por formação | Regra nova na resolução global, por spec própria |

Também continuam abertas, sem efeito novo: 001/DP-001, 001/DP-002, 001/DP-003,
001/DP-005, 001/DP-006, 001/DP-009, 002/DP-001, 003/DP-307, 004/DP-409, 005/DP-504,
005/DP-505, 005/DP-507, 005/DP-508, 006/DP-603 (spec, Decisões Pendentes).

## Desenho

### Modelo

[data-model.md](data-model.md): nenhum modelo, nenhuma migração. Valores imutáveis
`SituacaoDaFormacao`, `Formacao`, `ResolucaoDaEntrada`, `SituacaoDeEntrada`, `Entrada` e
a exceção `FormacaoDeOutraPessoa`.

### Consulta

[contracts/entrada.md](contracts/entrada.md). `situacao_de_entrada(pessoa, *, agora=None)`:

1. valida `pessoa` (`TypeError`; não gravada → `ValueError`) e fixa `agora`;
2. `ConclusaoAcademica.objects.filter(pessoa=pessoa)`, na ordem padrão da 001;
3. para cada Conclusão, `campanhas_em_coleta_para(conclusao, agora=agora)` (004);
4. para as Conclusões com exatamente 1 Campanha, uma consulta de `Participacao` pelos
   pares, indexada em memória por `(campanha_id, conclusao_id)`;
5. classificação por formação e resolução global, por funções puras.

**Classificação por formação** (R5):

```text
classificar(campanhas, participacao):
  len(campanhas) == 0            → SEM_PESQUISA
  len(campanhas) >= 2            → AMBIGUIDADE_OPERACIONAL   (participacao ignorada: None)
  participacao is None           → DISPONIVEL_PARA_INICIAR   ┐ entrada
  participacao.concluida_em None → DISPONIVEL_PARA_RETOMAR   ┘ pendente
  senão                          → JA_CONCLUIDA
```

**Resolução global** (R5):

```text
resolver(formacoes):
  formacoes vazio                         → SEM_FORMACAO
  P = [f for f in formacoes if f.situacao.pendente]
  len(P) == 1                             → ENTRADA_RESOLVIDA (P[0])
  len(P) >= 2                             → SELECAO_NECESSARIA (P)
  todas SEM_PESQUISA                      → SEM_PESQUISA
  senão                                   → SEM_ENTRADA_PENDENTE
                                            (concluídas, ambíguas ou mistura, com ou sem
                                             formações sem pesquisa)
```

### Entrada

`entrar(pessoa, formacao=None, *, agora=None)` (R7):

```text
agora ← momento_de_referencia(agora)
s ← situacao_de_entrada(pessoa, agora)                       reavaliada
sem formacao:
  s.resolucao ≠ ENTRADA_RESOLVIDA → Entrada(s, None, criada=False)
  f ← s.pendentes[0]
com formacao:
  f ← formação de s com o mesmo pk
  ausente (de outra Pessoa ou inexistente) → FormacaoDeOutraPessoa
                                           (antes de qualquer chamada à 005)
f SEM_PESQUISA | AMBIGUIDADE_OPERACIONAL → Entrada(s, None, criada=False)
f JA_CONCLUIDA                           → Entrada(s, f.participacao, criada=False)
f pendente:
  inicio ← iniciar_participacao(f.campanha, f.conclusao, agora=agora)   (005)
  → Entrada(s, inicio.participacao, criada = inicio.situacao is CRIADA)
indicação (FR-034): iniciada = criada; concluída = concluida_em preenchido;
                    em rascunho = demais com Participação; não realizada = sem Participação
```

### Formações concluídas

Aparecem sempre na consulta, como `JA_CONCLUIDA`, com a Participação; **não** são entrada
pendente, então não aumentam alternativas nem impedem a resolução de outra formação.
Entrar informando uma delas devolve a Participação concluída (`criada` falso) sem chamar a 005 e sem alterar nada.

### Campanhas sobrepostas

`AMBIGUIDADE_OPERACIONAL` local à formação, com todas as Campanhas na ordem da 004. A
Participação **não é consultada** para formações ambíguas, então nunca desempata (nem a
existente, nem a não respondida, nem recência). A formação ambígua não é pendente: outra
formação pendente única é resolvida; entrar pela ambígua não cria nem retoma nada.

### Tempo e concorrência

`agora` resolvido uma vez por `momento_de_referencia` para a avaliação (004); a 005 recebe o `agora` original e, sem ele, lê o relógio no instante do início (R9). Nenhum
bloqueio novo: entradas simultâneas → uma Participação pela unicidade do par (005);
mudanças entre consulta e entrada → reavaliação; concluída entre avaliação e início →
devolvida concluída (R10).

### Erros

`TypeError` (classe errada, `agora` inválido); `ValueError` (Pessoa não gravada);
`FormacaoDeOutraPessoa` (formação que não é da Pessoa — de outra Pessoa ou inexistente,
indistinguíveis; mensagem sem dados); `ParticipacaoRejeitada` da 005 propagada (R8).

## Project Structure

### Documentation (this feature)

```text
specs/007-contextualizacao-formacao-entrada/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # R1–R15
├── data-model.md        # nenhum modelo; valores derivados
├── quickstart.md        # validação
├── contracts/
│   └── entrada.md       # situacao_de_entrada, entrar, tipos
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks (não criado por este comando)
```

### Source Code (repository root)

```text
trajetoria/participacao/
└── entrada.py                        # NOVO: SituacaoDaFormacao, Formacao,
                                      #   ResolucaoDaEntrada, SituacaoDeEntrada,
                                      #   Entrada, FormacaoDeOutraPessoa,
                                      #   situacao_de_entrada, entrar
                                      #   (+ _classificar, _resolver: puras)

trajetoria/participacao/{models,operacoes,consultas,regras,percurso}.py
trajetoria/participacao/migrations/   # inalterados
trajetoria/academico/, campanha/, instrumento/, fonte_academica/, formulario_2024/
                                      # inalterados (consumidos: ConclusaoAcademica,
                                      #   campanhas_em_coleta_para, momento_de_referencia,
                                      #   iniciar_participacao)

tests/participacao/
├── test_entrada_situacao.py          # NOVO
├── test_entrada_entrar.py            # NOVO
└── test_entrada_aceitacao.py         # NOVO
                                      # construcao.py e conftest.py reutilizados; um
                                      # auxiliar de Pessoa com várias Conclusões, se
                                      # preciso, num arquivo/fixture novo da 007

README.md                             # + link para o quickstart da 007
```

**Structure Decision**: sem app novo. A capacidade é uma composição sem dados próprios
que termina numa operação da 005; vive em `participacao`, que já depende de `academico` e
`campanha`. Um módulo separado evita alterar `operacoes.py`/`consultas.py` (e os testes de
fronteira que fixam seus `__all__`), mantém `operacoes.py` como único caminho de escrita e
não cria dependência nova entre apps (research R1).

## Estratégia de testes

O foco são os invariantes (XXVI). Todo teste temporal passa `agora` explícito. Somente
dados fictícios. Instrumento e Campanhas pelos auxiliares de `tests/participacao/
construcao.py`; Participações concluídas por `preencher_instrumento` + `concluir` (006);
cenários SIM-P-0003/0004 pela incorporação da 001.

| Teste | Requisito |
|-------|-----------|
| **A** — 1 formação sem Participação → `ENTRADA_RESOLVIDA`; `entrar(pessoa)` → Participação nova do par certo, `criada` verdadeiro | US3.1–3.2, US5.1, FR-020, FR-030, FR-033 |
| **B** — 1 formação em rascunho → `ENTRADA_RESOLVIDA` (`DISPONIVEL_PARA_RETOMAR`); `entrar` → mesma Participação, `criada` falso, Respostas intactas | US6, FR-034 |
| **C** — 1 formação concluída → `SEM_ENTRADA_PENDENTE`, formação `JA_CONCLUIDA` com a Participação; `entrar(pessoa)` → sem Participação; informando a formação → a Participação concluída, mesmo `concluida_em`, `criada` falso, nada criado | US7.1–7.3, FR-022, FR-031 d, FR-035 |
| **D** — A concluída + B rascunho → `ENTRADA_RESOLVIDA` para B; A listada como `JA_CONCLUIDA`; `entrar(pessoa)` → rascunho de B, `criada` falso | US3.4, Clarifications |
| **E** — A concluída + B sem Participação → `ENTRADA_RESOLVIDA` para B; `entrar(pessoa)` → Participação nova de B | US3.5 |
| **F** — A e B pendentes (rascunho/inexistente, nas duas combinações) → `SELECAO_NECESSARIA`; `entrar(pessoa)` → sem Participação, nada criado; informando cada uma → Participações independentes; com terceira concluída, ainda 2 alternativas | US4, FR-021 |
| **G** — várias formações, nenhuma Campanha (e Campanhas que não as elegem; EM PREPARAÇÃO; ENCERRADA) → `SEM_PESQUISA`, todas listadas | US9, FR-019 |
| **H** — Pessoa sem Conclusões → `SEM_FORMACAO`; Pessoa não gravada → `ValueError` | US8, FR-003, FR-018 |
| **I** — duas Campanhas para a mesma Conclusão → formação `AMBIGUIDADE_OPERACIONAL` com as duas; sem Participação, com rascunho e com concluída numa delas: sempre ambígua; `entrar` com e sem formação → nada criado nem retomado; ambígua + 1 pendente → resolvida a pendente; ambígua + 2 pendentes → seleção entre elas | US10, FR-025–FR-027a, SC-004 |
| **J** — formação de outra Pessoa (homônima) → `FormacaoDeOutraPessoa`, mensagem sem atributos/ids alheios, nada criado; Conclusão inexistente → a mesma rejeição, mesma mensagem | US11.1, FR-044, FR-045, SC-009 |
| **K** — Participação concluída numa Campanha encerrada; nova Campanha aberta → `DISPONIVEL_PARA_INICIAR`; `entrar` → Participação nova; a anterior com mesmos `iniciada_em`, `concluida_em` e Respostas | FR-038, SC-006 |
| **L** — após consulta e entrada: 0 Respostas criadas; nenhuma coluna/valor da Conclusão em Participação | US5.2, US11.3, FR-040, FR-041, SC-007 |
| Contexto: `Formacao.conclusao` é a Conclusão da 001; `None` preservado; ordem igual à da 001 e estável entre chamadas | US1, FR-007–FR-011, SC-002 |
| Último dia do período e dia seguinte; Campanha EM PREPARAÇÃO/ENCERRADA; atributo não informado em critério → `SEM_PESQUISA` | US2.3–2.5, SC-012 |
| Resolução global por tabela, sem banco (formações em memória): todas as combinações relevantes de situações; exclusividade e exaustividade | FR-023 |
| Classificação por formação por tabela, sem banco | FR-014 |
| Consulta não grava (linhas idênticas antes e depois) | FR-024, SC-008 |
| No máximo 3 + N consultas | R3, R4 |
| Reavaliação: Campanha encerrada entre consulta e entrada → sem Participação; nova Campanha torna a formação ambígua → sem Participação; Participação criada em outra requisição → devolvida, `criada` falso; Participação concluída depois da avaliação e antes do início → concluída devolvida (simulado com `monkeypatch`: a avaliação devolve a situação anterior, de rascunho, e a 005 encontra a Participação já concluída) | FR-032, R7 passo 6 |
| Entrada repetida N vezes → 1 Participação; simultânea com threads só se estável em 10 execuções | US5.4, US6.2, SC-005 |
| `TypeError` para `pessoa`, `formacao` ou `agora` de tipo errado | FR-003 |
| Fronteiras: zero modelos e migrações novos; `participacao` com os mesmos 3 modelos; `operacoes.__all__` e `consultas.__all__` inalterados; escrita só pela 005, verificada por comportamento — consulta sem alteração de linhas, `entrar` com `iniciar_participacao` substituída por dublê que não grava não cria `Participacao`, delegação com os argumentos corretos, nenhuma chamada à 005 quando não há entrada pendente (sem inspeção do código-fonte); nenhum nome público proibido (EntrySession, Selection…) | FR-047–FR-053, SC-010, SC-011 |
| As 12 perguntas de sucesso do solicitante, ponta a ponta | spec, "Cobertura" |

## Complexity Tracking

Vazio. Nenhuma violação a justificar: nenhum modelo, nenhuma migração, nenhum app, nenhuma
dependência nova; um módulo de composição com valores imutáveis e duas funções públicas.

## Necessidade de voltar à spec ou às features anteriores

**Spec**: nenhuma mudança de comportamento. Precisões do plan:

- FR-016 (texto ajustado após o analyze): o plan lê os pares com uma única consulta ao
  modelo `Participacao` do próprio app (R4), com a mesma semântica de
  `localizar_participacao`, para não fazer uma consulta por formação.
- FR-017 "contexto (FR-007)": entregue como a própria instância de `ConclusaoAcademica`,
  sem cópia de atributos (R6).
- FR-031 (e) e FR-033: para `JA_CONCLUIDA` informada, a 005 não é chamada (nada a criar ou
  retomar); para as duas situações pendentes, sempre é (R7).
- FR-044: a rejeição de formação alheia **ou inexistente** é a exceção
  `FormacaoDeOutraPessoa`; Pessoa não gravada é `ValueError`, como na 005 (R8).

**Features 001 a 006**: nenhuma alteração de código, contrato ou teste.

**Base do branch**: este branch parte da `main` com a 006 incorporada
(saymoncastro/ifes-trajetoria-egressos#8). Antes de abrir o PR da 007, atualizar de novo
contra `main`.
