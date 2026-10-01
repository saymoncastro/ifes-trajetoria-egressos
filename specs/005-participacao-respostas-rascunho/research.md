# Research: Participação em Campanha e respostas em rascunho

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Não houve `NEEDS CLARIFICATION` no Technical Context. A stack é a das Features 001 a 004
([ADR 0001](../../docs/adr/0001-stack-inicial.md)), e as cinco escolhas de produto foram
confirmadas (spec, Clarifications). As decisões abaixo são de desenho.

## R1 — Onde Participação e Resposta vivem

- **Decisão**: novo app Django `trajetoria.participacao`. Ele depende de
  `trajetoria.campanha` (FK para `Campanha` e contratos de estado e elegibilidade), de
  `trajetoria.academico` (FK para `ConclusaoAcademica`) e de `trajetoria.instrumento`
  (FKs para `Pergunta` e `Opcao`). Nenhum app existente passa a conhecer o novo.
- **Rationale**: a dependência vai do conceito mais novo para os mais antigos, como na
  004 (004 R1). Participação e Resposta são inseparáveis: a Resposta não existe sem a
  Participação, e a 006 vai operar as duas juntas.
- **Alternativas rejeitadas**:
  - Participação em `campanha` e Resposta em `instrumento`: o instrumento passaria a
    conhecer dados declarados de pessoas (viola 002 FR-065) e a Campanha ganharia
    conteúdo de egresso.
  - Dois apps (`participacao` e `resposta`): separação sem consumidor; as operações de
    resposta precisam travar a Participação.

## R2 — Relações sem acesso reverso nos modelos anteriores

- **Decisão**: toda FK do app novo para modelos de features anteriores (`Campanha`,
  `ConclusaoAcademica`, `Pergunta`, `Opcao`) usa `related_name="+"`.
- **Rationale**:
  - os modelos antigos não ganham acessores, campos reversos ou dependências (FR-060);
  - o teste de 002 que exige que relações dos modelos do `instrumento` apontem só para o
    próprio app (`test_instrumento_aceitacao.py`) inspeciona `_meta.get_fields()`. Com
    `"+"`, a relação reversa é oculta e não aparece ali;
  - as consultas partem do app novo (`Participacao.objects.filter(conclusao=…)`), sem
    precisar de `conclusao.participacoes`.
- **Alternativa rejeitada**: acessores reversos (`conclusao.participacoes`,
  `pergunta.respostas`), que acoplariam modelos antigos ao novo e quebrariam o teste de
  isolamento da 002.

## R3 — Participação mínima

- **Decisão**: `Participacao(id UUID, campanha FK PROTECT, conclusao FK PROTECT,
  iniciada_em datetime)`, com `UNIQUE (campanha, conclusao)`. Pessoa, Versão e Pesquisa
  são propriedades derivadas (`conclusao.pessoa`, `campanha.versao`,
  `campanha.versao.pesquisa`).
- **Rationale**: é exatamente FR-001 a FR-005 e a Clarification de referência temporal.
  Sem estado, sem `concluida_em`, sem `atualizada_em` (FR-003, FR-055).
- **`iniciada_em`** é gravado com o momento de referência da operação (`agora`), não com
  `auto_now_add`, para que os testes controlem o tempo, como `aberta_em` na 004.
- **Alternativas rejeitadas**:
  - coluna `pessoa`, `versao` ou `pesquisa`: redundância que pode divergir (FR-004);
  - coluna `estado` com valor único EM_PREENCHIMENTO: informação sem conteúdo;
    antecipa a 006 (FR-055);
  - fotografia da elegibilidade na criação: vedada (Clarifications).

## R4 — Representação dos quatro tipos: uma tabela de Resposta com colunas tipadas

- **Decisão**: uma única tabela `Resposta`, com uma linha por `(participacao, pergunta)`
  (`UNIQUE`), e colunas explícitas para cada forma de valor:

  | Tipo da Pergunta | Onde fica o valor |
  |------------------|-------------------|
  | `ESCOLHA_UNICA` | `opcao` (FK `PROTECT` para `Opcao`) |
  | `ESCOLHA_MULTIPLA` | linhas em `RespostaOpcao` (R5); `opcao`, `texto`, `escala` nulos |
  | `TEXTO_CURTO` | `texto` (TextField) |
  | `ESCALA` | `escala` (IntegerField) |
  | complemento de "Outro" | `complemento` (TextField), só em escolha (R6) |

  CHECKs locais garantem só o que a própria linha permite verificar: no máximo uma de
  `opcao`, `texto` e `escala` preenchida, e `texto` e `complemento` nunca cadeia vazia.
  Tudo o que depende de outra tabela — correspondência entre coluna e tipo da Pergunta,
  complemento só em escolha e só com a Opção que o admite, pertença da Opção, Versão,
  limites da escala — é verificado pela operação (como na 002, R8/R9, e na 004, R10),
  sem copiar o tipo, sem gatilho e sem função PostgreSQL.
- **Rationale**:
  - **Integridade**: a Opção é FK real, com `PROTECT`; o inteiro é inteiro; o texto é
    texto. Nada de valor sem tipo.
  - **Clareza e consulta**: a 006 lê `resposta.opcao` para aplicar regras de navegação
    (que só existem em escolha única — 002 FR-035) e filtra por coluna em exportações
    futuras, sem decodificar JSON.
  - **Simplicidade**: uma linha por Pergunta respondida, como pedem FR-018 e a decisão
    de "uma Resposta por Pergunta".
- **Alternativas rejeitadas**:
  - **`JSONField` com o valor**: sem FK para Opção (perde `PROTECT` e identidade
    garantida), sem tipo de elemento, CHECKs frágeis; a vantagem (uma coluna) não
    compensa a perda de integridade.
  - **Tabela por tipo** (`RespostaEscolha`, `RespostaTexto`, `RespostaEscala`):
    quatro modelos e herança ou polimorfismo para expressar quatro colunas.
  - **Coluna `tipo` copiada da Pergunta** para CHECK local completo: redundância com
    `Pergunta.tipo`; a operação já é o único caminho de escrita.
  - **Escolha única também em `RespostaOpcao`**: unificaria "seleções", mas o banco não
    garantiria "exatamente uma" e a leitura da Opção de navegação exigiria join.

## R5 — Escolha múltipla: tabela técnica `RespostaOpcao`

- **Decisão**: modelo técnico `RespostaOpcao(id UUID, resposta FK CASCADE, opcao FK
  PROTECT)`, com `UNIQUE (resposta, opcao)`, exposto em `Resposta.opcoes` como
  `ManyToManyField(Opcao, through="RespostaOpcao", related_name="+")`. Não tem atributo
  próprio, operação própria nem significado de domínio: é a representação relacional do
  conjunto.
- **Rationale**:
  - **Conjunto**: `UNIQUE (resposta, opcao)` impede duplicata; a operação deduplica
    antes de gravar (FR-025). Não há coluna de ordem, então a ordem de seleção não é
    guardada; a leitura usa a ordem do instrumento (`Opcao.Meta.ordering = posicao`).
  - **Integridade**: FK real para a Opção, com `PROTECT` (a tabela automática do
    `ManyToManyField` usaria `CASCADE` em `opcao`, e apagar uma Opção apagaria
    seleções em silêncio).
  - **Parte do valor**: `CASCADE` em `resposta` — remover a Resposta remove o conjunto.
  - **UUID**: mesma convenção de identificador dos outros modelos (001 R3).
- **Alternativas rejeitadas**:
  - `ArrayField(UUIDField)` com IDs de Opção: sem FK, sem `PROTECT`, sem integridade
    referencial.
  - Tabela automática do `ManyToManyField`: `CASCADE` em `opcao` e `id` automático fora
    da convenção.
  - Uma Resposta por Opção selecionada: quebra "uma Resposta por Pergunta" (FR-018) e a
    identidade conceitual da resposta.
  - `CompositePrimaryKey` (Django 5.2): relações e `through` com chave composta têm
    suporte limitado; o ganho é só estético.
- **Limite aceito**: o banco não garante "≥ 1 seleção" (regra entre tabelas). A operação
  garante; um teste de modelo documenta o limite.

## R6 — Complemento de "Outro" como coluna da Resposta

- **Decisão**: `Resposta.complemento` (TextField anulável). Ele se refere,
  implicitamente, à **única** Opção da Pergunta com `complemento_textual = true`
  (002 FR-042, `UNIQUE (pergunta) WHERE complemento_textual`). A operação aceita
  complemento só quando essa Opção está selecionada (`opcao` em escolha única, ou
  presente no conjunto em escolha múltipla).
- **Rationale**: a restrição da 002 torna a associação inequívoca sem guardar qual
  Opção recebe o complemento. Uma coluna basta para os dois tipos de escolha, sem
  "resposta composta" genérica (FR-032).
- **Alternativas rejeitadas**:
  - Complemento em `RespostaOpcao`: só serve à escolha múltipla, obrigaria escolha única
    a usar a tabela e abriria espaço para vários complementos por Resposta.
  - FK explícita para a Opção do complemento: redundante com a restrição da 002.
- **Coerência na substituição**: toda escrita grava o valor inteiro, inclusive
  `complemento` (ausente ⇒ `NULL`). Trocar "Outro" por outra Opção apaga o complemento
  (FR-033 b; US8.5).

## R7 — Operações explícitas por tipo, sem valor genérico

- **Decisão**: quatro operações de escrita, uma por tipo, mais remoção:
  `responder_escolha_unica`, `responder_escolha_multipla`, `responder_texto`,
  `responder_escala` e `remover_resposta`. Todas compartilham um esqueleto privado
  (bloquear Participação → verificar coleta → verificar Pergunta → verificar tipo →
  validar valor → gravar).
- **Rationale**:
  - cada assinatura diz qual forma de valor espera, sem tipo "valor" polimórfico
    (FR-054; "não criar ResponseValue");
  - chamar a operação de um tipo para Pergunta de outro tipo é rejeição de domínio
    (`VALOR_INCOMPATIVEL`), que cobre FR-052 f;
  - não é CRUD genérico: não há `save()` exposto nem operação de "atualizar campos".
- **Alternativas rejeitadas**:
  - `registrar_resposta(participacao, pergunta, valor)` com despacho pelo tipo do valor:
    valor genérico e ambíguo (texto `"3"` é texto ou escala?).
  - `registrar_resposta(…, opcao=, opcoes=, texto=, escala=)`: saco de parâmetros que
    precisa validar "exatamente um", igual a um valor genérico.
- **Registrar e substituir são a mesma operação**: se há Resposta para a Pergunta, ela é
  atualizada no lugar (mesma identidade); senão, é criada. Não há Resposta nova a cada
  edição (FR-018, FR-033).

## R8 — Erro de programação × rejeição de domínio

- **Decisão**, no padrão da 004 (contracts/operacoes, "Tipo errado de argumento"):
  - `TypeError`, antes de qualquer escrita, para argumentos estruturais de tipo errado:
    `participacao` que não é `Participacao`, `pergunta` que não é `Pergunta`, `campanha`
    ou `conclusao` de classe errada, `agora` que não é `datetime` com timezone;
  - `ParticipacaoRejeitada` para **valores** declarados que não cabem no domínio,
    inclusive de forma errada: texto no lugar de Opção, lista em escolha única, `2.5`,
    `"3"` ou `True` em escala, texto que não é `str`. Esses valores virão da jornada e
    são entrada do egresso, não erro de programação (US3.2, US6.3, FR-052 f). Valor
    ausente ou vazio (`None`, `""`, só espaços, coleção vazia) é sempre `VALOR_VAZIO`,
    em todos os tipos: ausência de resposta só existe como ausência de linha
    ([contrato](contracts/operacoes.md#motivos-motivo), "Ausência × vazio").
- **Rationale**: a spec pede rejeição explícita com motivo para valor incompatível; a
  006 vai converter entradas HTTP e precisa de motivo de domínio, não de exceção de
  programação.

## R9 — Verificações a partir do banco, não da instância recebida

- **Decisão**: a operação relê sob bloqueio a Participação e, a partir do banco, a
  Campanha, a Pergunta (com `secao__versao_id`, tipo e limites de escala) e as Opções
  informadas (`Opcao.objects.filter(pk__in=…, pergunta=pergunta)`). Atributos da
  instância recebida não são confiados.
- **Rationale**: uma instância de `Pergunta` ou `Opcao` em memória pode estar
  desatualizada ou ter sido montada à mão; a verificação de pertença (FR-019, FR-024,
  FR-025) precisa ser a verdade gravada.
- **Pertença à Versão**: `pergunta.secao.versao_id == participacao.campanha.versao_id`.
  Não há "versão atual" em nenhum ponto (FR-020).
- **Opção de outra Versão** cai em `OPCAO_DE_OUTRA_PERGUNTA`, porque toda Opção pertence
  a uma Pergunta de uma Versão. Testado separadamente (FR-052).

## R10 — Gate de escrita: estado da Campanha, não elegibilidade

- **Decisão**:
  - **Iniciar** (par sem Participação): a admissão da 004 (FR-053), avaliada uma vez
    pelos seus contratos: `estado(…) is not EM_COLETA` → `COLETA_NAO_ADMITIDA`;
    `avaliar(…)` com pendências → `CONCLUSAO_NAO_ELEGIVEL`. Admitido ⇔ nenhuma violação,
    o que coincide com `admite_participacao` (teste de equivalência). As duas violações
    podem vir juntas (FR-012). Ajuste do code review: a primeira versão chamava
    `admite_participacao` e, na falha, reavaliava as duas condições para o diagnóstico;
    se as duas avaliações divergissem, a rejeição sairia vazia (`ValueError`).
  - **Escrever resposta**: `estado(campanha, agora=…) is EM_COLETA`. Elegibilidade não
    é reavaliada (Clarifications, FR-034).
  - **Início repetido** (par com Participação): devolve a existente sem consultar estado
    nem elegibilidade (FR-013).
- **Rationale**: consome os contratos da 004 sem replicar estado, período ou critérios
  (FR-014). A instrução "quando `admite_participacao` for falso, não escrever" foi lida
  à luz da decisão 2 das Clarifications: para escrita, só a parte "Campanha EM COLETA"
  daquele contrato se aplica.

## R11 — Concorrência com mecanismos do PostgreSQL

- **Início simultâneo do mesmo par**: `UNIQUE (campanha, conclusao)` é a garantia.
  A operação:
  1. procura a Participação; se existe, devolve `JA_EXISTENTE`;
  2. verifica a admissão;
  3. insere dentro de um savepoint (`transaction.atomic()` aninhado);
  4. se o insert viola a unicidade (`IntegrityError`), outra transação criou a
     Participação: relê e devolve `JA_EXISTENTE`.

  Em READ COMMITTED, o insert concorrente espera o commit da outra transação e então
  falha; a releitura seguinte vê a linha. É o mesmo padrão do `get_or_create` do Django,
  escrito à mão só porque a verificação de admissão fica entre a busca e o insert.
- **Escritas concorrentes na mesma Participação**: a operação bloqueia a linha da
  Participação (`select_for_update(of=("self",))`) antes de ler ou gravar Respostas.
  Escritas na mesma Participação ficam serializadas; o valor final é um dos valores
  completos (FR-053). `UNIQUE (participacao, pergunta)` é a garantia de última linha.
  `of=("self",)` evita bloquear também a Campanha, o que serializaria todas as
  Participações da rodada.
- **Escrita × encerramento explícito concorrente**: não há bloqueio da Campanha. A
  escrita é decidida pelo estado no seu momento de referência; uma escrita com `agora`
  anterior a `encerrada_em` foi legítima, ainda que confirmada um instante depois. É a
  mesma semântica "vale a partir do momento" da 004 (contracts/consultas, `estado`).
- **Alternativas rejeitadas**: bloqueio da Campanha em toda escrita; `SERIALIZABLE`;
  advisory locks; fila; framework de locking.

## R12 — Atomicidade sem rollback manual

- **Decisão**: cada operação de escrita roda em `transaction.atomic()`. Toda validação
  acontece antes da primeira gravação; se algo falhar depois (por exemplo, violação de
  CHECK), a transação desfaz tudo. Escolha múltipla substitui o conjunto apagando as
  linhas de `RespostaOpcao` da Resposta e inserindo as novas na mesma transação.
- **Rationale**: FR-051 sem código de compensação. Uma substituição inválida nunca chega
  a apagar o conjunto anterior, porque a validação vem antes.

## R13 — Tempo

- **Decisão**: `iniciar_participacao` e as escritas recebem `agora: datetime | None =
  None` e usam `momento_de_referencia(agora)` e `estado(…, agora=…)` da 004
  (`trajetoria.campanha.consultas`). Nenhum relógio novo.
- **Rationale**: timezone configurada do projeto, testes com `agora` explícito, sem
  abstração de relógio (004 R6).

## R14 — Consulta para a 006, sem modelo de tela

- **Decisão**: quatro consultas em `trajetoria.participacao.consultas`:
  `localizar_participacao`, `participacoes_da_conclusao`, `admite_escrita` e
  `respostas_atuais`. A última devolve `dict[UUID da Pergunta, Resposta]`, com `opcao`,
  `pergunta` e `opcoes` pré-carregados. Pergunta ausente do dicionário = não respondida.
- **Rationale**: FR-046 a FR-050 com os próprios modelos. A 006 percorre as Perguntas da
  Versão (002, `conteudo_da_versao`) e procura cada uma no dicionário. Nada de DTO de
  valor, árvore da jornada, progresso ou próxima Pergunta.
- **Origem identificável (FR-044)**: valor de Resposta é sempre declarado (é o único
  conteúdo do app); contexto acadêmico vem de `participacao.conclusao` (001,
  institucional). Nenhuma coluna mistura os dois.

## R15 — Sem dados pessoais novos em rastros

- **Decisão**: nenhum log novo. Mensagens de rejeição (`Violacao.detalhe`) citam
  motivo, campo e identificadores técnicos (UUID de Pergunta ou Opção), nunca o texto,
  o inteiro ou o complemento declarados (FR-059).
- **Rationale**: Observabilidade e Princípio XVI; DP-504 continua bloqueando uso real.

## R16 — Teste de 004 que proíbe "Participacao" e "Resposta" no projeto

- **Achado**: `tests/campanha/test_campanha_aceitacao.py::test_um_unico_modelo_novo_e_nenhum_proibido`
  verifica que nenhum modelo **do projeto inteiro** se chama `Participacao` ou
  `Resposta` (004 SC-009). Esta feature cria exatamente esses modelos, então o teste
  falharia.
- **Diagnóstico**: o teste era **excessivamente amplo**. A intenção de 004 SC-009 é de
  escopo — o app `campanha` tem só `Campanha`, e a 004 não cria Participação, Resposta,
  Convite, Destinatário etc. —, não proibir que features posteriores criem esses
  conceitos em seus próprios apps.
- **Decisão** (aprovada pelo solicitante; entrou na `main` pela própria Feature 004, em
  saymoncastro/ifes-trajetoria-egressos#6, e não faz parte do diff da 005): o teste
  passou a verificar o escopo do app. `test_um_unico_modelo_novo_e_nenhum_proibido` virou
  `test_app_campanha_tem_somente_o_modelo_campanha`, que exige que os modelos do app
  `campanha` sejam exatamente `["Campanha"]`. O conjunto global `PROIBIDOS` foi removido.
  É **correção de escopo de um teste**, não mudança de requisito da 004. Nenhum código de
  produção da 004 mudou; a suíte da 004 continua verde (225 testes).
- **Alternativas rejeitadas**:
  - retirar só `"Participacao"` e `"Resposta"` da lista global: manteria a fragilidade
    para features futuras (o mesmo problema já ocorrido entre 002 e 004);
  - renomear os modelos para escapar do teste: distorceria a Terminologia Fundamental da
    Constituição.
- **Lição para os testes desta feature**: a verificação de escopo da 005 também é por
  app (`participacao` = `{Participacao, Resposta, RespostaOpcao}`), sem proibição global
  por nome.

## R17 — Testes de concorrência

- **Decisão**: o teste determinístico é a proteção principal: força o ramo em que a
  busca não encontra a Participação e o insert viola a unicidade (por exemplo, criando a
  linha concorrente antes do insert por `monkeypatch` do auxiliar de busca) e exige
  `JA_EXISTENTE` com uma única linha. Um teste real com duas threads e banco transacional
  PODE existir se for estável; se se mostrar instável no CI, é removido, porque só
  provaria a mesma semântica de novo.
- **Rationale**: a garantia está no `UNIQUE` e no tratamento do `IntegrityError`, que o
  teste determinístico cobre sem depender de escalonamento de threads.
