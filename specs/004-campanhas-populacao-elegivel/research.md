# Research: Campanhas e população elegível

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Não houve `NEEDS CLARIFICATION` no Technical Context: a stack é a das Features 001 e 002
([ADR 0001](../../docs/adr/0001-stack-inicial.md)) e as três escolhas de produto foram
confirmadas (spec, Clarifications). As decisões abaixo são de desenho.

## R1 — Onde a Campanha vive

- **Decisão**: novo app Django `trajetoria.campanha`, que depende de
  `trajetoria.instrumento` (FK para `Versao`) e lê `trajetoria.academico`
  (`ConclusaoAcademica`). Nenhum dos dois apps existentes passa a conhecer a Campanha.
- **Rationale**: a dependência vai do conceito mais novo para os mais antigos, como na
  cadeia da Constituição. Os apps existentes continuam sem mudança (spec, Relação com
  outras features).
- **Alternativas rejeitadas**:
  - Colocar a Campanha em `instrumento`: misturaria aplicação e instrumento (Princípio
    VII) e faria o instrumento depender de `academico`.
  - Módulo genérico de campanhas reutilizável: sem consumidor (XXII).

## R2 — Uma entidade só

- **Decisão**: **um** modelo novo, `Campanha`. Critérios, período e ciclo de vida são
  colunas dela. O resultado de elegibilidade e a população não são persistidos.
- **Rationale**: todos os requisitos (FR-001 a FR-057) se expressam com colunas
  explícitas. Nenhum precisa de linha própria: os critérios são fixos e poucos (FR-018),
  a população é calculada (FR-032) e não há histórico (FR-046).
- **Alternativas rejeitadas** — Segmento, Regra, Filtro, GrupoDeFiltros, tabela
  genérica `(campanha, atributo, valor)`, Populacao, MembroCampanha, Destinatario,
  Convite, Agendamento, HistoricoCampanha, VersaoCampanha. Cada uma exigiria um
  requisito que a spec não tem: composição configurável, lista materializada, convite,
  disparo agendado ou edição pós-abertura.

## R3 — Critérios multivalorados

- **Decisão**: quatro colunas `ArrayField(TextField)` do PostgreSQL, anuláveis:
  `unidades`, `niveis`, `modalidades`, `formas_oferta`. `NULL` significa critério
  ausente. Um array presente tem ao menos um elemento, sem cadeia vazia (CHECK). As
  operações gravam o conjunto deduplicado e em ordem lexicográfica, sem alterar os
  textos.
- **Rationale**:
  - **Legibilidade**: uma Campanha numa linha; a coluna diz o que é.
  - **Consulta**: `unidade__in=campanha.unidades` traduz diretamente FR-020 e FR-022
    (igualdade exata). O `NULL` da Conclusão nunca casa com `IN`, o que já dá o
    comportamento conservador de FR-028 na consulta de população.
  - **Integridade**: CHECK local em cada coluna. O `__len` do Django devolve `0` para
    array vazio, em vez de `NULL`, então `len >= 1` rejeita o vazio sem a armadilha do
    `UNKNOWN` (verificado no código do Django 5.2: `coalesce(array_length(…), 0)`).
    `~Q(col__contains=[""])` rejeita cadeia vazia.
  - **Sem catálogo**: não há tabela de Unidade, Nível, Modalidade ou Forma de Oferta.
    Os valores são textos comparados com os da Conclusão (001/DP-007).
  - **Sem dependência nova**: `ArrayField` vem com o Django (`django.contrib.postgres`)
    e o banco já é PostgreSQL. Usar o campo não exige incluir o app em
    `INSTALLED_APPS`.
- **Alternativas rejeitadas**:
  - Tabela filha por atributo: quatro modelos para guardar listas curtas, com joins para
    ler uma Campanha.
  - Tabela genérica de critérios: é o motor de regras vedado (FR-020; XXII).
  - `JSONField`: sem tipo de elemento; CHECK mais frágil.
  - Texto delimitado: ambíguo com valores que contêm o delimitador.
- **Ausente × vazio, sem ambiguidade**:

  | Gravado | Significado |
  |---------|-------------|
  | `NULL` | critério não definido; não restringe |
  | array com ≥ 1 valor | valores permitidos (qualquer um satisfaz) |
  | `[]` | configuração inválida; nunca gravado |

  `[]` é rejeitado pela operação (`CONJUNTO_VAZIO`,
  FR-023 c) e pelo CHECK. Assim, só `NULL` significa "sem restrição".

## R4 — Ano de conclusão

- **Decisão**: `ano_minimo` e `ano_maximo`, `PositiveSmallIntegerField` anuláveis, o
  mesmo tipo de `ConclusaoAcademica.ano_conclusao`. CHECK de mínimo ≤ máximo quando os
  dois estão presentes. Comparação inclusiva com `ano_conclusao`. Data completa de
  conclusão não é usada (spec, Assumptions).
- **Alternativas rejeitadas**: intervalo de datas (sem consumidor); janela relativa à
  data corrente (vedada, FR-021).

## R5 — Estado derivado, sem coluna de estado

- **Decisão**: não há coluna `estado`. A Campanha guarda dois fatos:
  - `aberta_em` (data e hora): preenchida pela abertura;
  - `encerrada_em` (data e hora): preenchida só pelo encerramento **explícito**.

  O estado observável na data de referência `hoje` é uma função pura, avaliada nesta
  ordem de precedência (spec, Clarifications):

  ```text
  1. encerrada_em presente             → ENCERRADA      (forma EXPLICITA)
  2. fim presente e hoje > fim         → ENCERRADA      (forma FIM_DO_PERIODO; aberta ou não)
  3. aberta_em presente                → EM_COLETA
  4. caso contrário                    → EM_PREPARACAO
  ```

  O tempo tem precedência sobre a abertura: uma Campanha nunca aberta cuja janela
  expirou é ENCERRADA, não "em preparação" para sempre. Sem período definido, o passo 2
  não se aplica. Não há estado EXPIRADA: "encerrada sem abertura" é identificável por
  `aberta_em` ausente.

- **Rationale**: "encerra ao fim do período" é um estado derivado da data, não um job
  que grava no banco (Clarifications). Com uma coluna de estado, seria preciso um
  processo para mantê-la coerente com o calendário. Os dois fatos gravados nunca mudam
  depois de gravados. O momento do encerramento por data também é derivado: fim do
  último dia do período, na timezone configurada do projeto.
- **Invariante FR-041**: `abrir` só aceita `inicio ≤ hoje ≤ fim`, e o estado passa a
  ENCERRADA quando `hoje > fim`. Logo, EM_COLETA implica `hoje` dentro do período.
- **Estado temporal ≠ imutabilidade** (spec, Clarifications): o estado controla a
  coleta (abrir, admitir, encerrar). A imutabilidade é controlada só por `aberta_em`
  (R10). Uma Campanha nunca aberta e expirada é ENCERRADA para a coleta, mas continua
  editável e removível. Corrigir seu período para o futuro a devolve a EM_PREPARACAO, e
  isso não é reabertura, porque nunca houve abertura (FR-039). Reabertura só existiria
  com `aberta_em` presente e continua fora do escopo (DP-405).
- **Fatos valem a partir do momento em que ocorreram** (revisão de código): `aberta_em`
  e `encerrada_em` só contam quando `agora` é igual ou posterior a eles. Assim,
  `estado` e `campanhas_em_coleta_para` nunca tratam como EM_COLETA uma Campanha
  consultada antes da sua abertura, e `encerrar` com `agora` anterior à abertura é
  rejeitado (`ANTES_DA_ABERTURA`) em vez de violar o CHECK do banco.
- **Alternativas rejeitadas**:
  - Coluna `estado` com job de encerramento: infraestrutura temporal vedada.
  - Estado AGENDADA: vedado (Clarifications).
  - Booleano `aberta`: perderia o momento da abertura (FR-045).

## R6 — Tempo determinístico nos testes

- **Decisão**: toda operação ou consulta que depende do tempo recebe o parâmetro
  nomeado opcional `agora: datetime | None`. O padrão é `timezone.now()`, e `hoje` é
  `timezone.localdate(agora)`, isto é, a data na timezone configurada do projeto
  (`settings.TIME_ZONE`). A feature não nomeia nem fixa um fuso. `abrir` grava
  `aberta_em = agora`, e `encerrar` grava `encerrada_em = agora`. Um auxiliar privado faz
  a conversão, e só ele chama `timezone.now()`. As operações de preparação (`alterar`,
  `definir_*`, `remover`) não dependem do tempo e não recebem `agora`.
- **Rationale**: os testes passam um `agora` explícito e coerente (abrir em 01/04/2027,
  consultar em 15/04/2027) sem relógio real nem biblioteca de congelamento de tempo. Com
  um único parâmetro, data de referência e momento gravado não divergem.
- **Alternativas rejeitadas**: framework de relógio injetável (desnecessário);
  `freezegun` ou equivalente (dependência nova); parâmetros `hoje: date` e
  `agora: datetime` separados (podem divergir).

## R7 — Avaliação de elegibilidade pura

- **Decisão**: `avaliar(campanha, conclusao) -> Elegibilidade`, função pura em Python
  sobre as instâncias recebidas, sem consulta ao banco e sem data. Os critérios são
  verificados em ordem fixa: ano de conclusão, unidade, nível, modalidade, forma de
  oferta. Cada critério definido produz no máximo uma pendência:
  - atributo `NULL` → `NAO_INFORMADO`;
  - atributo presente e fora do critério → `NAO_ATENDE`.

  Para os anos, uma única pendência `ANO_CONCLUSAO` cobre mínimo e máximo (FR-027).
- **Rationale**: FR-025 exige independência de estado, data e outras entidades. Uma
  função pura torna isso verificável e trivialmente determinística. Nada é persistido
  (FR-030).
- **Alternativas rejeitadas**: avaliação no banco por Conclusão (exigiria reconstruir
  motivos em SQL); registro de resultado (auditoria vedada).

## R8 — População no momento da consulta

- **Decisão**: `populacao_no_momento(campanha) -> QuerySet[ConclusaoAcademica]`, filtro
  do ORM equivalente à avaliação:
  - `ano_conclusao__gte` / `__lte`, quando definidos;
  - `unidade__in`, `nivel__in`, `modalidade__in`, `forma_oferta__in`, quando
    definidos;
  - sem critérios, todas as Conclusões.

  Contar é `.count()`. O nome da função carrega a natureza dinâmica (FR-031). Nada é
  guardado na Campanha.
- **Rationale**: filtrar no banco é direto e escala para o volume institucional. O SQL
  já exclui `NULL` em comparações e `IN`, o que coincide com FR-028.
- **Risco**: duas expressões da mesma semântica (Python e ORM). **Mitigação**: um teste
  de consistência verifica, para cada Campanha de referência e cada Conclusão dos
  cenários, que pertencer ao QuerySet ⇔ `avaliar(...)` ELEGÍVEL.
- **Alternativas rejeitadas**: iterar `avaliar` sobre todas as Conclusões (O(N) em
  Python, sem ganho de clareza); lista materializada ou fotografia (vedadas; DP-408).

## R9 — Campanhas aplicáveis e contrato com a 005

- **Decisão**: três consultas no mesmo módulo:
  - `estado(campanha, *, agora=None) -> EstadoCampanha`, que responde "está aceitando
    coleta nesta data?" e "está encerrada?";
  - `admite_participacao(campanha, conclusao, *, agora=None) -> bool`, definida como
    EM_COLETA e ELEGÍVEL (FR-053);
  - `campanhas_em_coleta_para(conclusao, *, agora=None) -> tuple[Campanha, ...]`, que
    filtra no ORM as Campanhas abertas, não encerradas explicitamente e com
    `fim >= hoje`, e aplica `avaliar`. A ordem é `(inicio, id)`: determinística e sem
    significado de preferência (FR-052; DP-404).
- **Rationale**: é o mínimo que a 005 precisa perguntar, sem placeholder de Participação.
- **Filtro no banco** (revisão de código): `campanhas_em_coleta_para` filtra as
  Campanhas pelo predicado de `avaliar` visto do lado da Campanha (critério ausente, ou
  faixa de anos e `__contains` nos arrays), derivado da mesma tabela de critérios. Um
  teste confirma a coincidência com `admite_participacao` para todas as Conclusões e
  Campanhas de referência.
- **Alternativa rejeitada**: escolher "a" Campanha aplicável (prioridade, mais recente):
  é DP-404.

## R10 — Escrita e imutabilidade

- **Decisão**: `operacoes.py` é o único caminho de escrita, como em
  `instrumento.operacoes`. Toda operação:
  1. abre transação;
  2. bloqueia a linha da Campanha (`select_for_update`);
  3. rejeita com `CAMPANHA_JA_ABERTA` se `aberta_em` estiver presente, qualquer que
     seja o estado temporal, exceto `abrir` e `encerrar`, que têm regra própria. A
     fronteira histórica é a primeira abertura, não o estado (FR-043);
  4. verifica as regras;
  5. grava.

  Não há gatilho, sinal, `save()` sobrescrito nem `RunSQL`, pelos mesmos motivos do
  [ADR 0002](../../docs/adr/0002-imutabilidade-versao-publicada.md). A FK
  `Campanha.versao` usa `PROTECT`. A remoção só existe para Campanha nunca aberta
  (`aberta_em` ausente), em qualquer estado temporal.
- **Rejeições**: exceção `CampanhaRejeitada` com uma ou mais `Violacao(motivo,
  campo, detalhe)`. `definir_periodo`, `definir_criterios` e `abrir` reúnem **todas** as
  violações (FR-012, FR-023, FR-036); as demais rejeitam na primeira. Tipo errado de
  argumento é `TypeError`, como na 002.
- **Por que não reutilizar `instrumento.regras.OperacaoRejeitada`**: ela é tipada pelo
  `Motivo` do instrumento. Reaproveitá-la acoplaria a Campanha ao vocabulário do
  instrumento ou exigiria alterar a 002. A classe local tem cerca de 20 linhas e segue o
  mesmo padrão.

## R11 — Definição dos critérios de uma vez

- **Decisão**: `definir_criterios(campanha, *, ano_minimo=None, ano_maximo=None,
  unidades=None, niveis=None, modalidades=None, formas_oferta=None)` **substitui** a
  definição inteira. Omitir é `None`, isto é, critério ausente. Chamar sem argumentos
  torna a população ampla.
- **Rationale**: a validade depende do conjunto (mínimo ≤ máximo), e FR-023 pede todas as
  pendências numa rejeição. Substituir tudo evita uma combinatória de operações por
  critério e o sentinela "manter".
- **Valores**: textos gravados exatamente como recebidos. Valor vazio ou só com espaços é
  rejeitado (`VALOR_VAZIO`), como `TEXTO_VAZIO` na 002. Repetições são descartadas
  (conjunto). Os anos são `int`, nunca `bool`, e positivos.

## R12 — Pesquisa derivada e população ampla

- **Decisão**: sem coluna `pesquisa`. A propriedade `Campanha.pesquisa` devolve
  `versao.pesquisa` (FR-003). A propriedade `Campanha.populacao_ampla` é verdadeira
  quando os seis critérios estão ausentes (FR-019).

## R13 — Sem interface

- **Decisão**: nenhuma tela, admin, URL, comando ou API. As capacidades existem só como
  funções de domínio, verificadas por testes (FR-056; DP-402), como na 002 (R17).

## R14 — Dados de teste

- **Decisão**:
  - **Cenários da 001** (`FonteSimulada` + `incorporar_pessoa`): casos realistas, como a
    Pessoa C com Serra 2022 e Cefor 2025, e para provar o caminho real de incorporação
    durante a coleta.
  - **Conclusões criadas no ORM** por um auxiliar de teste: atributos ausentes
    específicos (nível, unidade, ano), sem alterar os cenários canônicos da 001.
  - **Versão publicada de teste**: instrumento mínimo (uma Seção, uma pergunta de texto
    curto) construído pelas operações da 002 e publicado com `publicar`
    (`versao_publicada()` em `tests/campanha/construcao.py`).
  - **Baseline da 003** (`materializar()`): usada só para provar que a abertura com
    Versão em RASCUNHO é rejeitada. Nunca publicada.
- **Rationale**: nenhuma alteração em cenários, fontes ou baseline das features
  anteriores.
