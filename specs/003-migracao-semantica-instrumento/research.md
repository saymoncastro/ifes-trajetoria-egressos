# Research: Migração semântica do instrumento institucional vigente

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

A spec não deixou `NEEDS CLARIFICATION`. As decisões abaixo são técnicas: onde fica o
conteúdo, como ele vira a baseline e como provar a fidelidade. Nenhuma altera a spec, nem
as Features 001 e 002.

## R1 — Mecanismo de materialização

- **Decision**: uma **operação explícita**, `materializar()`, que lê uma **declaração em
  código Python** versionada e constrói a baseline chamando as operações públicas da 002.
  É a única abordagem adotada. A operação é chamada explicitamente; nada a executa
  automaticamente.
- **Rationale**:
  - As operações da 002 são o único caminho de escrita suportado (002, R8). Construir
    por elas garante as mesmas regras de integridade (FR-034) sem duplicar validação.
  - A declaração é dado legível, revisável em diff e importável pelos testes, sem
    parser.
  - Determinística: a mesma declaração produz sempre o mesmo conteúdo, com ordem dada
    pela declaração.
  - A operação controla idempotência e divergência (R5, R6) e não publica (FR-003).
- **Alternatives considered**:
  - **Data migration** (`instrumento/migrations/0002_…`): rodaria em todo `migrate`,
    inclusive no banco de testes e em produção, criando a baseline sem ato explícito.
    Migrações usam modelos históricos, e não as operações atuais; usar as operações
    acoplaria a migração a código que evolui. E não há como "falhar por divergência"
    numa migração que roda uma vez só.
  - **Fixture (`loaddata`)**: escreve direto no banco, contornando as operações e suas
    rejeições, e fixa UUIDs. Rejeitada pelo próprio pedido.
  - **SQL bruto**: idem.
  - **Comando de gestão como mecanismo principal**: ver R12. O comando seria só um ponto
    de entrada da mesma operação.
  - **YAML/JSON + carregador**: acrescenta um formato e um parser sem ganho de
    legibilidade sobre tuplas Python, e perde a verificação de tipos e de importação.
  - **Centenas de chamadas procedurais** (`op.adicionar_opcao(...)` linha a linha):
    difícil de revisar contra a Matriz e fácil de errar posição.

## R2 — Localização do código

- **Decision**: pacote Python novo **`trajetoria/formulario_2024/`**, que **não é app
  Django**: não tem modelos, migrações, admin, URLs nem comandos, e não entra em
  `INSTALLED_APPS`. Ele importa apenas a API pública de `trajetoria.instrumento`
  (`operacoes`, `conteudo`, `models.TipoPergunta`, `regras.OperacaoRejeitada`). Nada em
  `trajetoria/instrumento/`, `trajetoria/academico/` ou `trajetoria/fonte_academica/` é
  alterado.
- **Rationale**:
  - A 003 é conteúdo, não domínio novo. Um app sem modelos seria cerimônia.
  - Colocar o pacote fora de `instrumento/` mantém a 002 literalmente intocada (FR-040)
    e deixa a dependência num só sentido: `formulario_2024 → instrumento`.
  - O nome diz o que é: o Formulário Egresso Ifes 2024, não um mecanismo genérico.
- **Alternatives considered**:
  - **Módulo dentro de `trajetoria/instrumento/`**: misturaria um instrumento concreto
    com a estrutura genérica do instrumento, e tocaria o app da 002.
  - **App Django próprio**: só se justificaria com modelos ou comando; não há nenhum.

## R3 — Forma da declaração

- **Decision**:
  - `declaracao.py` define dois `dataclass(frozen=True)` mínimos, locais ao pacote:
    `SecaoDeclarada` (chave `"S1"`…`"S13"`, título, texto, perguntas, encaminhamento por
    chave) e `PerguntaDeclarada` (chave legada `"Q1"`…`"Q54"`, tipo da 002, texto,
    obrigatoriedade, texto explicativo, Opções, Opção com complemento, escala, regras).
  - Opções são tuplas de textos, na ordem. Regras são pares (texto da Opção, chave da
    Seção de destino ou `FINALIZAR`). A escala usa o `Escala` da 002.
  - As listas extensas (Lista C, E, 15, 17, 18, 19) são constantes de módulo, **um item
    por linha**, nomeadas como no inventário (`LISTA_15`…) e citadas pelas perguntas. A
    Lista E é usada por Q8 e Q9; cada Pergunta recebe Opções próprias na construção
    (FR-015).
  - Textos longos (abertura, termos, encerramento) são constantes de módulo com os
    parágrafos separados por linha em branco.
  - Comentários curtos nos pontos tratados pela Matriz: `# E-05 nota interna não
    migrada`, `# E-07 regra redundante de Q51 não reproduzida`, `# E-08 correção
    editorial aprovada`, `# E-09 rótulo inicial ausente (DP-301)`.
- **Rationale**: é a representação mais simples que continua tipada, legível e
  comparável linha a linha com a Matriz da spec. As chaves `Q`/`S` tornam a revisão e os
  testes compreensíveis e **não são persistidas** (FR-012).
- **Alternatives considered**:
  - **Dicionários aninhados sem tipo**: erros de chave só aparecem na execução.
  - **Reutilizar `ConteudoVersao` da 002 como declaração**: exige UUIDs e posições
    explícitas, e mistura leitura com declaração.
  - **Classes por tipo de pergunta, builder fluente, validação própria**: seria um mini
    form builder (Princípio XXIII). A validação é a da 002.

## R4 — Construção pelas operações da 002

- **Decision**: `materializar()` constrói em três passos, sempre pelas operações:
  1. `criar_pesquisa` (se preciso), `criar_versao`, `alterar_versao` com título, abertura
     e encerramento;
  2. para cada Seção, na ordem da declaração: `adicionar_secao` (posição = ordem);
     para cada Pergunta: `adicionar_pergunta` (posição = ordem; tipo, obrigatoriedade,
     texto explicativo e escala); para cada Opção: `adicionar_opcao` (posição = ordem;
     complemento textual só na Opção indicada);
  3. depois que todas as Seções existem: `definir_encaminhamento` e `definir_regra`
     (destino Seção ou `FINALIZAR`).
- **Rationale**: regras e encaminhamentos referenciam Seções posteriores, que precisam
  existir antes. Cada chamada verifica suas próprias regras (texto vazio, Opção
  repetida, complemento único, escala válida, regra só em escolha única).
- **Alternatives considered**: `bulk_create` como em `criar_versao_a_partir_de`. Seria
  mais rápido, mas contornaria as verificações das operações; o volume (cerca de 470
  operações) não justifica.

## R5 — Identificação da baseline e idempotência

- **Decision**:
  - Constantes: `NOME_PESQUISA = "Pesquisa Institucional de Egressos"` e `DESIGNACAO =
    "Formulário Egresso Ifes 2024 — referência migrada"`.
  - Pesquisa: procurada pelo nome exato. Nenhuma → criada. Uma → usada. Mais de uma →
    `PesquisaAmbigua`, sem criar nem alterar nada (FR-031).
  - Versão: procurada por (Pesquisa, designação). Inexistente → criada (R4). Existente →
    comparada (R6): equivalente → nada é escrito e o resultado diz `criada=False`;
    divergente → `BaselineDivergente`.
  - Retorno: `Resultado(versao, criada)`.
- **Rationale**: a identidade da baseline é a designação aprovada (FR-004) dentro da
  Pesquisa. A 002 não exige nome único de Pesquisa (002, R18), por isso a ambiguidade é
  tratada aqui, sem alterar a 002.
- **Alternatives considered**:
  - **UUIDs fixos na declaração**: dariam identidade "conhecida", mas acoplariam o
    conteúdo a identificadores técnicos e impediriam ter a baseline em mais de um banco
    sem colisão conceitual. A designação já identifica.
  - **Marcador de baseline** (campo, tabela ou registro de execução): vedado (FR-036;
    pedido "não criar Baseline/HistoricoMigracao").

## R6 — Equivalência e divergência

- **Decision**:
  - Uma função `forma(…)` reduz uma Versão a uma estrutura de tuplas **por valor**: textos
    da Versão; para cada Seção, na ordem: título, texto, posição do destino do
    encaminhamento e Perguntas; para cada Pergunta: tipo, texto, texto explicativo,
    obrigatoriedade, escala e Opções; para cada Opção: texto, complemento e regra
    (posição da Seção de destino ou "finalizar"). Ficam de fora identidades, estado,
    momento de publicação, origem, designação e nome da Pesquisa (FR-033).
  - A mesma função aplicada à declaração produz a forma esperada; aplicada a
    `conteudo_da_versao(v)` (leitura da 002), a forma existente.
  - Iguais → equivalente. Diferentes → `BaselineDivergente`, com um diagnóstico curto
    da **primeira** diferença (por exemplo, `S9·8: texto explicativo difere`, `S2: 7
    Perguntas, esperadas 8`), obtido percorrendo as duas formas em paralelo.
  - **Pós-condição**: logo após criar, a operação compara a forma criada com a esperada;
    se divergir (erro de construção), levanta `BaselineDivergente` e a transação desfaz
    tudo.
- **Rationale**: atende "falhar explicitamente e não alterar nada" com o mínimo de
  código. O diagnóstico localiza a divergência sem motor de diff. A pós-condição garante
  que criação e reexecução usam o mesmo critério.
- **Alternatives considered**:
  - **Diff completo de todas as diferenças**: infraestrutura sem consumidor; a análise é
    humana (FR-033).
  - **Hash do conteúdo gravado em algum lugar**: exigiria persistir metadado de migração.
  - **Comparar a árvore `ConteudoVersao` normalizada (como `sem_identidades` dos testes
    da 002)**: equivalente, mas a árvore carrega UUIDs e não se constrói a partir da
    declaração sem gravar; a forma por tuplas é mais simples.
  - **Aviso e continuar**: recusado pelo solicitante.

## R7 — Atomicidade e concorrência

- **Decision**:
  - `materializar()` inteira roda em um `transaction.atomic()`. As operações da 002 já
    abrem `atomic()` próprios, que viram savepoints do externo. Qualquer
    `OperacaoRejeitada`, `BaselineDivergente` ou erro inesperado desfaz tudo; não há
    rollback manual.
  - A unicidade de posições é adiada até o fim da transação (002, R4); as operações já
    verificam posição livre antes de gravar.
  - Concorrência: duas materializações simultâneas em banco vazio podem criar duas
    Pesquisas homônimas (o nome não é único). A segunda criação da Versão na mesma
    Pesquisa é barrada pela unicidade da designação. O pior caso deixa duas Pesquisas
    homônimas, e a execução seguinte falha explicitamente com `PesquisaAmbigua`, sem
    alteração silenciosa. Materialização é ato operacional raro; nenhum lock adicional
    é adotado.
- **Rationale**: FR-032 (atomicidade) com a infraestrutura existente.
- **Alternatives considered**: advisory lock do PostgreSQL ou unicidade do nome da
  Pesquisa. O primeiro é infraestrutura para risco improvável e explícito; o segundo
  alteraria a 002.

## R8 — Ausências

- **Decision**: rótulo inicial das 11 escalas, título de S13, textos introdutórios de
  S2–S13 e textos explicativos fora de Q10, Q32 e Q48 são `None` na declaração. A 002 grava
  `NULL` e rejeita cadeia vazia (002, R16). Nenhum valor é inventado (FR-018).
- **Rationale**: o domínio já distingue ausência de texto informado.

## R9 — Rastreabilidade Q1–Q54

- **Decision**:
  - A Matriz de Migração fica na spec (artefato de documentação).
  - A declaração usa as chaves `Q1`…`Q54` e `S1`…`S13`, só em memória.
  - Os testes usam as mesmas chaves para localizar cada Pergunta pela ordem global
    (Seção, posição) — a n-ésima é Qn (FR-009) — e citam a linha da Matriz ou o E-xx em
    cada verificação.
- **Rationale**: auditável de ponta a ponta (Matriz → declaração → teste → baseline),
  sem contaminar o banco (FR-012, FR-036).

## R10 — Prova de fidelidade independente da declaração

- **Decision**:
  - `trajetoria/formulario_2024/declaracao.py` é a **única fonte executável** da
    baseline. O inventário Markdown continua sendo referência documental e auditável:
    **não** é parseado estruturalmente, **não** vira fixture e **não** gera nada.
  - Os testes têm um **manifesto explícito de expectativas**, em código de teste,
    transcrito da Matriz da spec, independente da declaração (FR-039):
    - para cada Qn: Seção, posição, tipo, obrigatoriedade e, nas perguntas com poucas
      Opções, a tupla de Opções em ordem; nas listas extensas, o nome da lista;
    - para cada lista extensa (C, E, 15, 17, 18, 19): quantidade (23, 17, 33, 47, 50,
      77), primeiro e último item;
    - contagens de "Contagens verificáveis", as 10 regras, os 7 encaminhamentos, os 17
      percursos, os textos explicativos e os rótulos de escala.
  - O inventário é lido **como texto bruto**, com espaços colapsados e sem os marcadores
    `> ` de citação, para duas verificações de "está documentado":
    - cada texto da baseline (Versão, Seções, Perguntas, textos explicativos, Opções,
      rótulos) ocorre literalmente no texto do inventário, exceto o rótulo corrigido
      "Concordo totalmente" de Q52–Q54 (E-08), verificado à parte;
    - cada lista extensa materializada, unida por `"; "`, ocorre literalmente no texto
      do inventário. Com a quantidade e as extremidades do manifesto, isso detecta perda,
      troca de ordem e alteração de qualquer item sem extrair a lista do Markdown.
  - O manifesto e as fixtures (leitura bruta do inventário e baseline materializada uma
    vez por módulo) ficam em `tests/instrumento/formulario_2024_esperado.py`, porque
    fidelidade e navegação os compartilham. A leitura bruta tem poucas linhas e não
    reconstrói estrutura.
- **Rationale**: o oráculo não é a declaração (não é tautológico) e o inventário não se
  torna segunda linguagem executável. Uma alteração acidental na declaração diverge do
  manifesto, do texto documentado ou de ambos.
- **Alternatives considered**:
  - **Extrair listas, perguntas ou navegação do Markdown**: transformaria o inventário em
    fonte executável e criaria um parser; recusado pelo solicitante.
  - **Duplicar as seis listas inteiras no manifesto**: segunda transcrição de 247 itens,
    com custo de manutenção alto; a ocorrência literal no inventário cobre o mesmo risco.
  - **Snapshot monolítico do conteúdo**: difícil de revisar.
  - **Comparar a baseline só com a declaração**: tautológico.

## R11 — Custo dos testes

- **Decision**: os testes de fidelidade e navegação, que só leem, usam uma fixture de
  módulo que materializa a baseline uma vez numa transação desfeita ao final e devolve a
  árvore imutável `ConteudoVersao`. Os testes de materialização (idempotência,
  divergência, atomicidade) materializam por teste. Um teste com
  `django_db(transaction=True)` materializa com `COMMIT` real, para exercitar a
  unicidade adiada.
- **Rationale**: cerca de 470 operações por materialização; repetir em cada teste de
  leitura tornaria a suíte lenta sem ganho.

## R12 — Ponto de entrada

- **Decision**: **sem comando de gestão** nesta feature. A operação é chamada por código
  (testes, futura Feature 004) ou, em um ambiente, por `manage.py shell -c` (ver
  [quickstart](quickstart.md)).
- **Rationale**: mantém a linha da 002 (R17: nenhum ponto de entrada novo) e evita
  interface sem consumidor definido. A operação não publica e só cria RASCUNHO.
- **Alternatives considered**: comando `materializar_formulario_2024`. Fácil de
  acrescentar como invólucro fino se surgir necessidade operacional (por exemplo,
  implantação); exigiria transformar o pacote em app ou colocá-lo em `instrumento/`.

## R13 — Componentes não adotados

Nenhum dos itens abaixo é criado: novo modelo de domínio (`PerguntaLegada`,
`MapeamentoMigracao`, `OrigemGoogleForms`, `Baseline`, `HistoricoMigracao`,
`DecisaoMigracao`); campo legado (`q_number`, `legacy_id`); enumeração das categorias da
Matriz; framework de seed ou de dados iniciais; DSL, YAML/JSON e parser de produção;
catálogo acadêmico ou vínculo de Opções com Curso/Conclusão; vínculo Pergunta → atributo
acadêmico, ocultação ou "perguntar se a fonte não tiver"; condição de exibição para Q6;
atributo de momento de regra (`AFTER_QUESTION`, `END_OF_SECTION`, `IMMEDIATE`) ou
prioridade entre regras; motor de navegação; motor de diff, reconciliação ou
sincronização; comando, admin, editor, API; alteração de qualquer arquivo das Features
001 e 002.
