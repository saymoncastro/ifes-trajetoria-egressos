# Research: Contextualização da formação e entrada na pesquisa

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Não houve `NEEDS CLARIFICATION` no Technical Context. A stack é a das Features 001 a 006
([ADR 0001](../../docs/adr/0001-stack-inicial.md)), e a única escolha de produto em aberto
(Participação concluída conta ou não como alternativa) foi decidida pelo solicitante
(spec, Clarifications). As decisões abaixo são de desenho.

## R1 — Onde a entrada vive

- **Decisão**: um módulo novo, `trajetoria/participacao/entrada.py`, no app existente
  `participacao`. Sem app novo, sem modelo, sem migração. O módulo **compõe** contratos
  públicos já existentes:
  - `ConclusaoAcademica` (001), lida pela Pessoa;
  - `campanhas_em_coleta_para` e `momento_de_referencia` (004, `campanha.consultas`);
  - `Participacao` (005/006), lida numa única consulta de leitura (R4);
  - `iniciar_participacao` (005, `participacao.operacoes`), único caminho de escrita.
- **Rationale**:
  - a capacidade não tem dado próprio: só deriva e, no fim, chama a operação de início da
    005. O app `participacao` já depende de `academico` e `campanha`, então nenhuma
    dependência nova surge e nenhum app anterior passa a depender de `participacao`;
  - um módulo separado **não altera** `operacoes.py` nem `consultas.py`. Isso cumpre
    FR-052 (não alterar 001–006) e preserva as asserções de fronteira da 005/006
    (`operacoes.__all__` com igualdade exata em `test_participacao_inicio.py`; substrings
    proibidas em `test_participacao_aceitacao.py::test_10`; os três modelos do app);
  - a escrita continua exclusiva de `operacoes.py`: `entrada.py` nunca grava modelo
    diretamente.
- **Alternativas rejeitadas**:
  - **app `entrada`**: um app sem modelo nem responsabilidade de domínio própria, criado só
    por simetria, com `apps.py` e registro em `INSTALLED_APPS` sem consumidor (XXII);
  - **acrescentar a `consultas.py` e `operacoes.py`**: altera contratos e `__all__` da
    005/006, obriga a mexer em testes de fronteira e mistura uma composição de quatro
    features com as regras de Participação e Resposta;
  - **em `campanha`**: `campanha` passaria a depender de `participacao`, invertendo a
    dependência atual;
  - **em `academico`**: o núcleo acadêmico passaria a conhecer Campanha e Participação
    (001 FR-038).

## R2 — Zero persistência

- **Decisão**: **zero** modelos novos, **zero** migrações, nenhuma coluna, índice, CHECK,
  gatilho, sinal, cache ou tabela auxiliar.
- **Rationale**: a "Análise de persistência" da spec mostra que cada informação é
  derivável: formações (001), Campanhas aplicáveis (004, no momento de referência),
  situação da Participação (005/006), e a formação/Campanha da entrada ficam registradas
  na própria Participação criada pela 005 (005 FR-002). Gravar Campanhas aplicáveis criaria
  cópia desatualizável; gravar "seleção" não tem consumidor.
- **Alternativas rejeitadas**: tabela de "opção de formação", "sessão de entrada",
  "seleção" ou "atribuição de Campanha" (spec FR-047; lista "Entidades deliberadamente não
  criadas").

## R3 — Campanhas aplicáveis: `campanhas_em_coleta_para`, uma vez por Conclusão

- **Decisão**: para cada Conclusão da Pessoa, chamar `campanhas_em_coleta_para(conclusao,
  agora=agora)` (004). A quantidade de Campanhas devolvidas decide a classificação (0, 1,
  ≥ 2). A ordem `(inicio, id)` da 004 é preservada, sem significado de preferência.
- **Rationale**:
  - é exatamente o contrato que a 004 criou para isto (004 FR-052: "base para uma futura
    URL institucional permanente resolver a Campanha sem convite"). Estado temporal,
    período e critérios ficam todos na 004 (spec FR-012, FR-013);
  - o número de consultas é **1 por Conclusão da Pessoa**, não por linha de uma listagem:
    uma Pessoa tem tipicamente 1 a 4 Conclusões. Não é um N+1 sobre volume crescente;
    é proporcional ao volume atual, como pedido;
  - cada consulta usa o filtro da 004 no banco, sem trazer Campanhas que não se aplicam.
- **Alternativas rejeitadas**:
  - **buscar todas as Campanhas EM COLETA uma vez e avaliar `avaliar()` em memória**:
    reduziria para uma consulta, mas exigiria reproduzir em `entrada.py` o filtro
    "aberta, não encerrada, dentro do período" da 004 (duas semânticas para o mesmo
    estado) ou carregar todas as Campanhas já criadas para chamar `estado()` em Python.
    O ganho (economizar 1–3 consultas por Pessoa) não justifica copiar regra da 004
    (spec FR-013; pedido do solicitante: "não copiar critérios ou filtros");
  - **`admite_participacao` para cada par (Campanha × Conclusão)**: idem, exige listar
    todas as Campanhas;
  - **cache ou materialização da aplicabilidade**: proibido (spec FR-047; pedido do
    solicitante).

## R4 — Participações: uma consulta para todas as formações com uma Campanha

- **Decisão**: depois de R3, reunir os pares (Campanha, Conclusão) das formações com
  **exatamente uma** Campanha aplicável e ler as Participações desses pares numa única
  consulta: `Participacao.objects.filter(conclusao__in=…, campanha__in=…)`, indexadas em
  memória por `(campanha_id, conclusao_id)`. Pares que não estão no índice não têm
  Participação. O momento de conclusão é `participacao.concluida_em` (006).
- **Rationale**:
  - mesma semântica de `localizar_participacao` (005 FR-046 — "nunca cria"), sem uma
    consulta por par; ler o modelo da própria app é o que `consultas.py` já faz;
  - o filtro por `conclusao__in` e `campanha__in` pode trazer pares cruzados (Conclusão A
    com a Campanha de B); o índice por par os descarta. Com 1–4 Conclusões, o excesso é
    irrelevante;
  - formações em **ambiguidade operacional** não entram na consulta: o estado de
    Participação nunca é usado para desempatar Campanhas (spec FR-027; Clarifications).
    Formações sem Campanha também não.
- **Alternativas rejeitadas**:
  - **`localizar_participacao` por par**: correto, mas uma consulta por formação;
  - **`iniciar_participacao` na consulta**: gravaria (spec FR-024);
  - **`participacoes_da_conclusao`** (005): devolve todas as Participações da Conclusão,
    inclusive de Campanhas antigas, e ainda exige filtrar pela Campanha aplicável.

## R5 — Classificação: duas funções puras sobre dados já carregados

- **Decisão**: separar I/O de regra, no padrão do `percurso.py` (006):
  - `situacao_de_entrada` faz as leituras (Conclusões → R3 → R4);
  - uma função privada pura classifica **cada formação** a partir de `(campanhas,
    participacao)`;
  - outra função privada pura deriva a **resolução global** a partir da tupla de
    formações.

  Classificação por formação (spec FR-014):

  | Campanhas aplicáveis | Participação do par | Situação | Entrada pendente |
  |----------------------|---------------------|----------|------------------|
  | 0 | — (não consultada) | `SEM_PESQUISA` | não |
  | ≥ 2 | — (não consultada) | `AMBIGUIDADE_OPERACIONAL` | não |
  | 1 | inexistente | `DISPONIVEL_PARA_INICIAR` | **sim** |
  | 1 | `concluida_em` nulo | `DISPONIVEL_PARA_RETOMAR` | **sim** |
  | 1 | `concluida_em` preenchido | `JA_CONCLUIDA` | não |

  Resolução global (spec FR-018 a FR-023), nesta ordem:

  1. nenhuma formação → `SEM_FORMACAO`;
  2. exatamente 1 formação com entrada pendente → `ENTRADA_RESOLVIDA`;
  3. 2 ou mais → `SELECAO_NECESSARIA`;
  4. 0 pendentes e todas `SEM_PESQUISA` → `SEM_PESQUISA`;
  5. 0 pendentes e ao menos uma com pesquisa aplicável (`JA_CONCLUIDA` ou
     `AMBIGUIDADE_OPERACIONAL`) → `SEM_ENTRADA_PENDENTE`.

- **Rationale**: as regras ficam legíveis e testáveis por tabela sem banco; a ordem dos
  passos 2–3 antes de 4–5 garante que formações concluídas ou ambíguas nunca aumentem as
  alternativas nem impeçam a resolução de outra (Clarifications). Os casos são mutuamente
  exclusivos e exaustivos (FR-023).
- **Alternativas rejeitadas**: métodos num objeto "Formação" com estado mutável; tabela
  de regras configurável; "pontuação" de formações (seria ranking — FR-021).

## R6 — Estruturas de resultado: valores imutáveis, sem ViewModel

- **Decisão**: dataclasses `frozen` e enums, no padrão de `Elegibilidade` (004) e
  `SituacaoDaJornada` (006). Detalhes em [data-model.md](data-model.md) e
  [contracts/entrada.md](contracts/entrada.md):
  - `SituacaoDaFormacao` (enum, 5 valores) e `Formacao` (conclusão, situação, Campanhas
    aplicáveis, Participação);
  - `ResolucaoDaEntrada` (enum, 5 valores) e `SituacaoDeEntrada` (Pessoa, momento,
    formações, resolução);
  - `Entrada` (situação reavaliada, Participação, `criada`).

  *Revisão YAGNI após o plan*: `DesfechoDaEntrada`, `Entrada.formacao`,
  `SituacaoDeEntrada.pessoa/.momento/.resolvida` e `Formacao.entrada_pendente` foram
  removidos (repetiam informação derivável ou não tinham consumidor); `pendente` passou
  para o enum `SituacaoDaFormacao` ([data-model](data-model.md#simplificações-por-yagni-em-relação-ao-primeiro-desenho-do-plan)).
- **Contexto acadêmico**: `Formacao.conclusao` é a própria instância de
  `ConclusaoAcademica`. Curso, unidade, nível, modalidade, forma de oferta, ano e data são
  lidos dela, com `None` = "não informado". Nada é copiado para outro objeto, nenhum rótulo
  é fabricado (FR-007, FR-010, FR-040; DP-702).
- **Rationale**: o resultado é de domínio, não de tela (FR-050). Carregar a instância evita
  uma segunda representação do contexto acadêmico que poderia divergir da 001.
- **Alternativas rejeitadas**: `dict` solto (sem contrato); campos copiados (`curso`,
  `unidade`… no valor — duplicação); texto de apresentação ("ADS — Serra — 2022") —
  rótulo fabricado e decisão de UX (DP-702); identificador "amigável" — idem.

## R7 — `entrar`: reutilizar `iniciar_participacao`, sem duplicar idempotência

- **Decisão**: `entrar(pessoa, formacao=None, *, agora=None)`:

  1. valida argumentos (R8) e fixa `agora = momento_de_referencia(agora)` uma vez;
  2. `situacao = situacao_de_entrada(pessoa, agora=agora)` — **reavaliada** (FR-032);
  3. sem `formacao`: se `situacao.resolucao` não é `ENTRADA_RESOLVIDA`, devolve
     `Entrada(situacao, None, criada=False)`; senão usa `situacao.pendentes[0]`;
  4. com `formacao`: procura-a, pelo `id`, entre `situacao.formacoes`; se não estiver,
     `FormacaoDeOutraPessoa`, seja de outra Pessoa, seja inexistente (code review: sem
     oráculo de existência);
  5. conforme a situação da formação:
     - `SEM_PESQUISA` ou `AMBIGUIDADE_OPERACIONAL` → `Entrada(situacao, None, False)`
       (o motivo é a situação da formação em `situacao.formacoes`), nada criado;
     - `JA_CONCLUIDA` → `Entrada(situacao, participação já lida, False)`; **não** chama
       `iniciar_participacao` (nada a criar nem a retomar);
     - `DISPONIVEL_PARA_INICIAR` ou `DISPONIVEL_PARA_RETOMAR` → `iniciar_participacao(
       formacao.campanha, formacao.conclusao, agora=agora)` (005);
  6. `Entrada(situacao, inicio.participacao, criada=inicio.situacao is CRIADA)`. A
     indicação de FR-034 é derivada: iniciada = `criada`; concluída = `concluida_em`
     preenchido (inclusive concluída entre a avaliação e o início, em outro
     dispositivo); em rascunho = os demais casos com Participação.
- **Rationale**: a 005 já garante "cria ou devolve a existente", unicidade sob
  concorrência e admissão pela 004 (005 FR-011 a FR-014). A 007 não cria Participação
  diretamente nem reimplementa `get_or_create` (FR-033). O mesmo `agora` é passado à 004 e
  à 005, então a classificação e a admissão concordam.
- **Alternativas rejeitadas**:
  - devolver diretamente a Participação em rascunho já lida, sem `iniciar_participacao`:
    economiza uma consulta, mas abre um segundo caminho de "retomar"; o pedido do
    solicitante é reutilizar a 005 nos dois casos pendentes;
  - chamar `iniciar_participacao` para `JA_CONCLUIDA`: devolveria `JA_EXISTENTE` sem
    efeito, mas é chamada inútil numa formação sem entrada pendente;
  - transação envolvendo toda a `entrar`: não dá isolamento extra em READ COMMITTED e não
    há escrita além da 005, que já é atômica.

## R8 — Erros de uso × rejeição de domínio

- **Decisão**, no padrão da 005 (R8 de lá):
  - `pessoa` que não é `Pessoa`, `formacao` que não é `ConclusaoAcademica` ou `agora`
    inválido → `TypeError`, antes de qualquer consulta de domínio;
  - `pessoa` não gravada (ou removida) → `ValueError` (spec FR-003: erro de uso da
    fronteira, nunca "sem formação");
  - `formacao` que não está entre as Conclusões da Pessoa — de **outra** Pessoa ou
    inexistente → `FormacaoDeOutraPessoa` (exceção de domínio própria do módulo), sem
    nada criado e sem consulta extra. Os dois casos são indistinguíveis de propósito:
    distinguir revelaria se um UUID é Conclusão de alguém (achado do code review). A
    mensagem não contém atributos, nome nem identificadores (FR-044, FR-045);
  - `ParticipacaoRejeitada` da 005 (só possível por mudança concorrente da Campanha) é
    propagada sem conversão (FR-046).
- **Rationale**: uma única rejeição de domínio nova não justifica enum de motivos, tupla de
  violações nem alteração de `participacao.regras` (FR-052).
- **Alternativas rejeitadas**: novo `Motivo` em `regras.py` (altera a 005); devolver
  Participação vazia para formação alheia (esconderia uso indevido da fronteira).

## R9 — Tempo

- **Decisão**: `agora: datetime | None = None` nas duas funções. A avaliação usa
  `momento_de_referencia(agora)` (004), repassado a `campanhas_em_coleta_para`. A
  `iniciar_participacao` recebe o `agora` **original**: com `agora` explícito (testes), o
  mesmo instante; sem ele, a 005 lê o relógio no instante do início. Nenhum relógio novo.
- **Rationale** (ajuste do code review): repassar o instante da avaliação faria a 005
  julgar a admissão no passado; uma Campanha encerrada explicitamente entre a avaliação e
  o início seria vista EM COLETA e a Participação nasceria depois do encerramento. Com o
  relógio do início, a 005 rejeita (`COLETA_NAO_ADMITIDA`), e a rejeição é propagada.

## R10 — Concorrência e consistência

- **Decisão**: nenhum bloqueio novo. As leituras da consulta não são serializadas; a
  escrita é a da 005, já serializada pela unicidade do par.
- **Rationale**:
  - entradas simultâneas na mesma formação: `iniciar_participacao` garante uma única
    Participação (005 FR-006, R11 de lá);
  - Campanha encerrada ou aberta entre a consulta e a entrada: `entrar` reavalia no seu
    momento (FR-032);
  - Participação concluída entre a avaliação e o início: R7, passo 6;
  - leitura sem `SELECT FOR UPDATE`: a consulta não decide nada que precise ser atômico
    com outra escrita; o pior caso é uma situação já superada, que a entrada reavalia.
- **Alternativas rejeitadas**: bloquear a Pessoa ou as Conclusões (sem invariante a
  proteger); transação `REPEATABLE READ` (sem ganho real).

## R11 — Ambiguidade local

- **Decisão**: a formação com 2+ Campanhas aplicáveis fica `AMBIGUIDADE_OPERACIONAL`, com
  `campanhas` = todas, na ordem da 004, e `participacao = None` **sempre**, mesmo que
  exista Participação numa delas. Ela não é pendente e não entra na contagem de R5.
- **Rationale**: a ambiguidade é de configuração institucional (004/DP-404); o estado de
  Participação não a mascara (Clarifications). Ser local permite resolver outra formação
  sem esconder a ambígua (FR-027a).
- **Alternativas rejeitadas**: escolher a Campanha com Participação, a ainda não
  respondida, a mais recente ou a de período mais curto (FR-025, FR-027); transformar a
  ambiguidade em resolução global que bloqueia todas as formações.

## R12 — Formações indistinguíveis (DP-702)

- **Decisão**: nada de código específico. Formações são distintas pelo `id` da Conclusão;
  a consulta devolve os atributos existentes com `None` preservado. Não há rótulo,
  apelido, número sequencial ou "identificador amigável".
- **Rationale**: o `id` interno existe tecnicamente para a entrada informar a formação,
  mas não é solução de UX institucional; isso continua em DP-702.

## R13 — Estratégia de testes

- **Decisão**: três arquivos novos em `tests/participacao/`, reutilizando
  `tests/participacao/construcao.py` sem alterá-lo, exceto por um auxiliar novo de
  Pessoa, se necessário (ver plan):
  - `test_entrada_situacao.py` — a consulta: formações, classificação por formação,
    resolução global, ambiguidade local, contexto sem cópia, nenhuma gravação, número de
    consultas;
  - `test_entrada_entrar.py` — a entrada: casos A–L do solicitante, desfechos, rejeições,
    reavaliação, longitudinalidade, nenhuma Resposta;
  - `test_entrada_aceitacao.py` — as 12 perguntas de sucesso, ponta a ponta, e as
    fronteiras (zero modelos e migrações, módulo sem escrita direta, nada de autenticação,
    nada proibido criado, contratos 001–006 inalterados).
- Para concluir Participações nos testes, usar `preencher_instrumento` + `concluir` da
  006 (a Seção 2 do instrumento de teste é opcional, então a jornada fica finalizada).
- Para os cenários da fonte simulada (SIM-P-0003, SIM-P-0004), incorporar pela 001.
- Classificação global testada também por tabela, sem banco, com `Formacao` montadas em
  memória (instâncias não gravadas).
- Concorrência: entradas simultâneas com threads só se estável em 10 execuções, como na
  006; senão, a garantia é a da 005, já testada lá.

## R14 — Testes existentes da 005/006

- **Decisão**: nenhum teste existente muda. `entrada.py` não altera `operacoes.__all__`,
  `consultas.__all__`, os modelos do app nem as migrações.
- **Verificação**: a suíte completa deve passar sem tocar em `tests/participacao/test_*`
  existentes nem em testes de outras features.

## R15 — Documentação

- **Decisão**: acrescentar ao `README.md` o link para o quickstart da 007, como nas
  features anteriores. Nenhuma outra documentação de código.
