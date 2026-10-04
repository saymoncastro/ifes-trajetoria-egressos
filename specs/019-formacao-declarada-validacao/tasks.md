---
description: "Tasks da Feature 019 — Formação não localizada e validação posterior"
---

# Tasks: Formação não localizada e validação posterior

**Input**: `specs/019-formacao-declarada-validacao/` (spec, plan, research R1–R22,
data-model, contracts e quickstart). Constituição 2.0.0.

**Prerequisites**: plan.md e spec.md (68 FRs), research.md, data-model.md, contracts/.

**Tests**: Princípio XXVI. São obrigatórios para:
- âncora e longitudinalidade;
- quarentena e oficialidade;
- preservação histórica (snapshot e migração);
- autorização e escopo;
- exportação;
- associação de Respostas.

Os testes de cada história são escritos antes e falham antes da implementação. Nada de
cobertura como meta.

## Formato e convenções

- `- [ ] Tnnn [P?] [USn?] descrição com caminho`.
- **[P]**: arquivo diferente e sem dependência de task incompleta.
- **Ordem das fases.** Segue o plan: a quarentena (US2) vem antes do caminho do egresso
  (US1). Assim nenhuma declaração existe sem a regra de oficialidade já em vigor. As duas
  são P1.
- **Construção de dados em teste.** Testes que precisam de declarações antes das operações
  existirem usam `tests/declaracao/construcao.py` (T012). É código de teste, nunca de
  produção.
- **Restrições de modelo.** São citadas literalmente do data-model.md.

---

## Fase 1 — Setup (3 tasks)

- [X] T001 Adicionar `cryptography` em `pyproject.toml` (dependências de produção), atualizar `uv.lock` (`uv lock`) e acrescentar a linha `"cryptography…",  # Feature 019: Fernet para selos e dados de consulta ao acervo (research R5)` em `tests/dependencias.py`
- [X] T002 Em `config/settings.py`, acrescentar:
  - `TRAJETORIA_CHAVE_SELO_DECLARACAO` (chave A) e `TRAJETORIA_CHAVE_CONSULTA_ACERVO` (chave B), lidas do ambiente, sem valor padrão (string vazia);
  - `TRAJETORIA_SELO_DECLARACAO_VALIDADE` como `timedelta(minutes=int(os.environ.get(..., "30")))`.

  Em `tests/conftest.py`, gerar as duas chaves de teste com `Fernet.generate_key()` (distintas) e configurá-las para toda a suíte, no mesmo padrão das chaves da 018.
- [X] T003 Criar o app `trajetoria/declaracao/`:
  - `__init__.py`;
  - `apps.py`;
  - `migrations/__init__.py`;
  - `templates/declaracao/`.

  Registrá-lo em `INSTALLED_APPS` (`config/settings.py`) **antes** de `trajetoria.participacao`.

---

## Fase 2 — Fundação: selos, modelos, âncora, oficialidade e capacidade (11 tasks)

**Checkpoint**: modelos migrados, âncora com CHECK, `participacoes_oficiais` correta para as
seis situações e capacidade de validar definida. Nenhuma tela ainda.

### Testes

- [X] T004 [P] Escrever `tests/declaracao/test_selo.py` (R5, R6; FR-115, FR-117):
  - **Chaves recusadas** com `ChaveIndisponivel`: A ou B ausente, malformada, A == B, ou igual a `SECRET_KEY`, a uma chave da 018 ou à de pseudonimização.
  - **Selos de trânsito e de início**: abrem com a própria finalidade; recusam outra finalidade, adulteração, vencimento (relógio controlado contra `TRAJETORIA_SELO_DECLARACAO_VALIDADE`) e selo cifrado com a chave B.
  - **Selo de consulta**: abre só com a chave B e recusa UUID de outra declaração.
  - **Logs**: `caplog` sem CPF, data nem token.
- [X] T005 [P] Escrever `tests/declaracao/test_modelos.py` com os CHECKs e unicidades do data-model:
  - **FormacaoDeclarada**:
    - textos "não vazio";
    - `identificador_cpf` e `verificador` "hex de 64";
    - `chave_de_criacao` "`UNIQUE`".
  - **ValidacaoDaFormacao**:
    - "`conclusao IS NOT NULL ⇔ resultado = CONFIRMADA`";
    - "Com `NAO_CONFIRMADA`, os dois booleanos são falsos";
    - "`conflito_detectado_na_validacao` implica `NOT fora_da_abrangencia_na_validacao`";
    - uma decisão por declaração (1:1).
  - **ReferenciaDeAcervo**:
    - "`UNIQUE (unidade, referencia)`";
    - "se presente, o ano coincide com `ano_conclusao`";
    - opcionais "não vazio quando presente".
- [X] T006 [P] Escrever `tests/participacao/test_participacao_ancora.py` (FR-030):
  - **CHECK `participacao_ancora_unica`**: rejeita as duas âncoras nulas e as duas preenchidas.
  - **Participações existentes**: continuam válidas.
  - **`pessoa`**: é `None` com âncora declarada.
  - **`UNIQUE (campanha, conclusao)`**: inalterado.
  - **Escritas da 005/006** numa Participação declarada: responder, remover, concluir e as rejeições depois da conclusão e fora da coleta, sem regra nova (FR-032).
- [X] T007 [P] Escrever `tests/participacao/test_participacao_oficiais.py` (FR-050, FR-051; R3, R4):
  - **Situações.** Uma Participação para cada uma das seis situações. `participacoes_oficiais()` devolve só `INSTITUCIONAL` e `DECLARADA_VALIDADA`, e `situacao_analitica` devolve a situação correta.
  - **Anotações.** `conclusao_efetiva_id` é a âncora ou a Conclusão da validação, e `atributo_efetivo("unidade")` segue o mesmo caminho.
  - **Conflito pendente.** É um único `Q` reutilizável (R3).
- [X] T008 [P] Acrescentar em `tests/governanca/test_governanca_regras.py` os casos de `pode_validar_formacao`: CPAEG sim, CSAEG sim, sem vínculo não, vínculo inativo não. Atualizar `tests/governanca/test_governanca_fronteiras.py` com a nova função nomeada.

### Implementação

- [X] T009 Implementar `trajetoria/declaracao/selo.py` conforme contracts/operacoes.md, seção `declaracao.selo`:
  - `ChaveIndisponivel`, `SeloInvalido`;
  - validação das chaves A e B;
  - `selar_transito` e `abrir_transito`;
  - `selar_inicio` e `abrir_inicio` (gera `chave_de_criacao` com `uuid4`);
  - `selar_consulta` e `abrir_consulta`.

  O texto claro é JSON com `p` (finalidade). Nenhum log com argumentos. Dataclasses com `repr=False` nos campos sensíveis.
- [X] T010 Implementar `trajetoria/declaracao/models.py` com os cinco modelos do data-model, CHECKs e `UniqueConstraint` exatamente como em T005. Gerar `trajetoria/declaracao/migrations/0001_initial.py`.
  - **`ValidacaoDaFormacao.resultado`**: `TextChoices`.
  - **FKs**: `ConclusaoAcademica` com `PROTECT` e `related_name="+"`.
  - **`DadosConsultaAcervo.selado`**: nunca em `__str__`.
- [X] T011 Em `trajetoria/participacao/models.py`:
  - `conclusao` passa a `null=True`;
  - acrescentar `formacao_declarada = OneToOneField("declaracao.FormacaoDeclarada", null=True, on_delete=PROTECT, related_name="participacao")`;
  - CHECK `participacao_ancora_unica` (exatamente um preenchido);
  - `pessoa` devolve `None` sem Conclusão.

  Gerar a migração aditiva `trajetoria/participacao/migrations/0003_...py`, dependente de `declaracao/0001` (depende de T010).
- [X] T012 [P] Criar `tests/declaracao/construcao.py` com auxiliares de teste:
  - `declaracao_concluida(campanha, **campos)`: declaração, dados selados e Participação concluída, criados pelo ORM;
  - `validar(formacao, conclusao=None, resultado=..., fora=False, conflito=False)`;
  - pares fictícios de CPF e data.
- [X] T013 Em `trajetoria/participacao/consultas.py`:
  - `conflito_pendente()`: um `Q` único; na 019, igual a `conflito_detectado_na_validacao`;
  - `participacoes_oficiais()`: anotada com `conclusao_efetiva_id` via `Coalesce`;
  - `atributo_efetivo(campo)`;
  - `situacao_analitica(participacao)`, na ordem de FR-050.

  Sem importar `declaracao`: só lookups por nome.
- [X] T014 Em `trajetoria/governanca/regras.py`: `pode_validar_formacao(vinculos)` (CPAEG ou CSAEG ativos), em `__all__`, no padrão de `pode_acompanhar_coleta`.

---

## Fase 3 — US2: quarentena — preservada e fora dos dados oficiais (P1) (12 tasks)

**Goal.** Nenhuma superfície oficial (007, 011, 012, 013) conta Participação não oficial,
e uma declarada validada passa a contar sem ação do egresso.

**Independent Test.** Com declarações criadas por `construcao.py` em cada situação:
indicadores da 011, snapshot, dataset e exportação consideram só as oficiais. Um snapshot
anterior a uma validação fica idêntico.

### Testes

- [X] T015 [P] [US2] Escrever `tests/participacao/test_entrada_oficiais.py` (FR-036, FR-092):
  - Pessoa com Conclusão X e declaração pendente, não confirmada, fora da abrangência ou em conflito para X: a 007 mostra X disponível, nunca "já respondida".
  - Com declarada validada para X: X aparece como já respondida (concluída) ou retomável.
- [X] T016 [P] [US2] Escrever `tests/acompanhamento/test_acompanhamento_oficiais.py` (FR-100):
  - iniciadas, concluídas, em andamento e taxas ignoram não oficiais;
  - declarada validada conta na unidade da Conclusão vinculada, inclusive no escopo de CSAEG e nos recortes;
  - elegíveis inalterados (FR-023).
- [X] T017 [P] [US2] Escrever `tests/analitico/test_analitico_oficiais.py` (FR-102 a FR-104):
  - **Universo e integridade.** Universo com as Conclusões efetivas das oficiais. A captura não falha com pendentes na Campanha, e a integridade vale para as oficiais.
  - **Campos congelados.** `participacao` e `origem_formacao` corretos para institucional, validada pela fonte digital e validada pelo acervo (Conclusão com `fonte="acervo_historico"`).
  - **Reprodutibilidade.** Snapshot S1, depois validação, depois S2: `linhas_do_dataset(S1)` e os indicadores de S1 são idênticos antes e depois. S2 inclui a validada.
- [X] T018 [P] [US2] Escrever `tests/analitico/test_analitico_migracao_registro.py`, primeiro teste de migração do projeto, com `MigrationExecutor` (R14):
  - **Antes de migrar.** Migra até o estado anterior aos campos novos e cria Campanha encerrada com snapshot e registros com e sem Participação.
  - **Depois de migrar.** `participacao` é a do par `(campanha, conclusao)` ou nula; `origem_formacao` é `"institucional"` ou nula.
  - **Aborto.** Um teste unitário da função de verificação da migração prova que ela aborta, sem gravar, quando recebe um par com duas Participações. O caso é impossível no banco, e a função é testada isolada.
- [X] T019 [P] [US2] Escrever `tests/exportacao/test_exportacao_origem.py` (FR-106):
  - coluna base `origem_formacao` com os três valores e vazio sem Participação, proveniência `derivado` e descrição do dicionário de contracts/dados-oficiais.md;
  - `VERSAO_CONTRATO == 2`;
  - nenhuma coluna ou valor contém nome declarado, campos declarados, HMAC, CPF ou data;
  - metadados iguais aos da 012.

### Implementação

- [X] T020 [US2] Em `trajetoria/participacao/entrada.py`: `_participacoes_dos_pares` usa `participacoes_oficiais()` pela `conclusao_efetiva_id` (R18).
- [X] T021 [US2] Em `trajetoria/acompanhamento/consultas.py`, substituir:
  - `Participacao.objects.filter(campanha=…)` por `participacoes_oficiais().filter(campanha=…)`;
  - `conclusao__unidade` e `conclusao__<campo>` por `atributo_efetivo(...)` no escopo (`_universo_participacao`) e nos recortes.
- [X] T022 [US2] Em `trajetoria/analitico/models.py`, acrescentar em `RegistroDoSnapshot`:
  - `participacao` (FK anulável, `PROTECT`, `related_name="+"`);
  - `origem_formacao` (`TextChoices` `institucional`, `declarada_validada_fonte_digital`, `declarada_validada_acervo`, anulável);
  - CHECK "`NULL` ⇔ `participacao` nula".

  A migração `trajetoria/analitico/migrations/000N_...py` tem `RunPython` com:
  - **verificação** em função própria, que aborta se algum par tiver mais de uma Participação;
  - **preenchimento** determinístico (R14);
  - reverso que zera os campos.
- [X] T023 [US2] Em `trajetoria/analitico/operacoes.py`:
  - `_participantes` e `_verificar` passam a usar `participacoes_oficiais()` e `conclusao_efetiva_id`;
  - cada registro grava `participacao` e `origem_formacao`, derivada como no data-model.
- [X] T024 [US2] Em `trajetoria/analitico/consultas.py`, `linhas_do_dataset` e `_contagens`/`indicadores_do_snapshot` leem a Participação por `registro.participacao`, sem procurar por `(campanha, conclusao_id)`. Atualizar a docstring do módulo.
- [X] T025 [US2] Em `trajetoria/exportacao/contrato.py`, acrescentar `ColunaBase("origem_formacao", "texto", "derivado", <descrição de contracts/dados-oficiais.md>)` depois das colunas de coleta e fazer `VERSAO_CONTRATO = 2`. Em `trajetoria/exportacao/dataset.py`, preencher a coluna a partir da linha do dataset.
- [X] T026 [US2] Ajustar os testes de fronteira:
  - `tests/analitico/test_analitico_fronteiras.py`: campos novos do registro, `PERMITIDOS`;
  - `tests/exportacao/test_exportacao_fronteiras.py`;
  - `tests/acompanhamento/test_acompanhamento_fronteiras.py`.

  Só o necessário para as novas dependências de `participacao.consultas`.

**Checkpoint.** A quarentena está garantida nas quatro superfícies antes de qualquer tela
de declaração.

---

## Fase 4 — US1: informar a formação e responder imediatamente (P1, MVP) (13 tasks)

**Goal.** Depois de `NAO_CONFIRMADA`, o egresso declara, responde à mesma Versão e recebe a
confirmação, sem criar Pessoa nem Conclusão.

**Independent Test.** Par fictício inexistente → declaração → jornada completa, e depois:
- declaração, dados selados e Participação gravados;
- nenhuma Pessoa, Conclusão ou material;
- mensagens sem afirmar validação;
- reenvio do "Começar" sem duplicar.

### Testes

- [X] T027 [P] [US1] Escrever `tests/declaracao/test_iniciar.py` (FR-005, FR-016, FR-113; R6, R9):
  - **Gravação conjunta.** `iniciar_participacao_declarada` cria declaração, `DadosConsultaAcervo` e Participação na mesma transação, com HMACs corretos e `selado` legível só pela chave B.
  - **Isolamento.** Zero Pessoa, Conclusão e `MaterialDeVerificacao` novos.
  - **Idempotência.** Mesma `chave_de_criacao` e mesmo par: mesma Participação, `criada=False`. Outro par: `SeloInvalido`.
  - **Corrida.** Duas transações com a mesma chave criam uma só declaração.
  - **Campanha.** Campanha sem critério admite; nenhuma Campanha dá `SemCampanha`; duas dão `Ambiguidade`. Nos dois casos, nada é gravado.
  - **Falhas.** Limite por origem dá `EmEspera`, e chave B inválida dá `ChaveIndisponivel`. Em ambos, nada é gravado.
- [X] T028 [P] [US1] Escrever `tests/declaracao/test_rotas_egresso.py` (FR-001 a FR-003, FR-006, FR-016, FR-033; contracts/rotas.md):
  - **Botão.** "Informar minha formação" só em `NAO_CONFIRMADA`, depois de "Conferir os dados". Não aparece em indisponível, formato inválido nem `CONFIRMADA`.
  - **Selo.** Vem em campo oculto de POST e nunca na URL nem em `Location`. `POST /declaracao/` responde 200 com formulário ou lista, sem redirecionar. `GET /declaracao/nova/` não existe (405).
  - **Indistinguível.** Conteúdo e status idênticos para CPF inexistente e CPF existente com data errada.
  - **Selo inválido.** Vencido ou adulterado leva a `/acesso/`.
  - **Fluxo completo.** Termina na mensagem final de FR-033, com "Formação informada por você".
  - **Duplo envio.** POST duplo de `/declaracao/comecar/` cria uma declaração.
  - **Desistência.** Desistir antes de começar não grava nada.
  - **Chave B ausente.** Indisponibilidade técnica sem gravar.
  - **Cabeçalhos.** `Cache-Control: no-store` em toda página com selo.
- [X] T029 [P] [US1] Escrever `tests/acesso/test_sessao_declarante.py` (FR-040, FR-042; R7):
  - **Conteúdo.** A sessão do declarante guarda só UUIDs e instantes, sem HMAC, CPF ou data.
  - **Exclusividade.** É exclusiva com a sessão de Pessoa: estabelecer uma limpa a outra.
  - **Expiração.** Inatividade e duração máxima da 018.
  - **"Sair".** Encerra a sessão.
  - **Isolamento.** `pessoa_em_uso` é `None` na sessão do declarante.
  - **Sem efeito colateral.** `NAO_CONFIRMADA` não altera sessão existente (018 FR-034).
- [X] T030 [P] [US1] Escrever `tests/interface/test_interface_declarada.py` (FR-032, FR-033, FR-042):
  - **Posse.** O declarante percorre Seções, condicionais, rascunho e conclusão. A Participação de outro par ou de Pessoa dá o mesmo 404 da 008.
  - **Pessoa.** Não acessa Participação declarada.
  - **Contexto.** Rótulo "Formação informada por você", nunca "Você concluiu".
  - **Concluída.** Sem Respostas.
- [X] T031 [P] [US1] Escrever `tests/declaracao/test_vazamento.py` (SC-007, FR-110):
  - **Cenário.** Fluxo completo com CPF e data fictícios conhecidos.
  - **Varredura.** Não podem aparecer em claro: todas as tabelas (texto de todas as colunas), `caplog`, URLs visitadas, cabeçalhos `Location`, snapshots e exportação.

### Implementação

- [X] T032 [US1] Em `trajetoria/declaracao/sessao.py` (movido de `acesso/sessao.py` no code review; a 018 só expõe `post_de_entrada`):
  - `estabelecer_declarante(request, uuids, agora)`;
  - `declaracoes_em_uso(request)`, revalidando expiração e existência;
  - `acrescentar_declaracao(request, uuid)`.

  Exclusividade com a sessão de Pessoa (`cycle_key` + `clear`). `pessoa_em_uso` ignora a sessão de declarante. `encerrar` limpa as duas.
- [X] T033 [US1] Em `trajetoria/acesso/views.py` e `trajetoria/acesso/templates/acesso/entrada.html`:
  - no ramo `NaoConfirmada`, gerar `selar_transito(cpf, data)`;
  - renderizar, depois de "Conferir os dados", um formulário POST para `/declaracao/` com o selo oculto e o botão "Informar minha formação";
  - com a chave A indisponível, renderizar o botão sem selo, que leva à indisponibilidade.

  Nada muda em `verificar`.
- [X] T034 [US1] Em `trajetoria/declaracao/consultas.py`: `opcoes_de_unidade()` e `opcoes_de_nivel()` (R20). São a união ordenada dos valores distintos de `ConclusaoAcademica` com os usados em critérios de Campanha.
- [X] T035 [US1] Em `trajetoria/declaracao/formularios.py` e `trajetoria/declaracao/mensagens.py`, o formulário dos cinco campos (FR-010, FR-011):
  - nome e curso: texto não vazio;
  - unidade e nível: escolha nas opções de T034;
  - ano: 4 dígitos, não futuro.

  Erros por campo, textos sem termos técnicos e sem afirmar validação (FR-006).
- [X] T036 [US1] Em `trajetoria/declaracao/operacoes.py`:
  - `campanhas_compativeis` (R9; E7: descartar pendências de `MODALIDADE` e `FORMA_OFERTA`);
  - `iniciar_participacao_declarada`, com passos, idempotência e exceções conforme contracts/operacoes.md;
  - `declaracoes_do_par`.
- [X] T037 [US1] Em `trajetoria/declaracao/views_egresso.py` e `trajetoria/declaracao/urls.py`, as rotas `POST /declaracao/`, `GET /declaracao/`, `POST /declaracao/nova/` e `POST /declaracao/comecar/`, conforme contracts/rotas.md.
  - **Selo.** `POST /declaracao/` renderiza na própria resposta, sem redirecionar, para não perder o selo. Não existe `GET /declaracao/nova/`.
  - **Proteções.** `sensitive_post_parameters("selo")`, `never_cache` e CSRF.
  - **Telas.** Sem pesquisa, ambiguidade e confirmação com o selo de início.
  - **Templates.** Em `trajetoria/declaracao/templates/declaracao/`, com o shell da 015.
  - **Rotas.** Registradas nas rotas do modo de demonstração.
- [X] T038 [US1] Em `trajetoria/interface/views.py`:
  - `_participacao_da_pessoa` vira `_participacao_do_sujeito` (Pessoa por `conclusao__pessoa`; declarante por `formacao_declarada_id__in`);
  - `_pessoa` aceita o declarante nas rotas da jornada.

  Em `trajetoria/interface/apresentacao.py`, `formacao_exibida(participacao)` devolve o contexto e o rótulo. Em `trajetoria/interface/mensagens.py`, entra a mensagem final de FR-033. Substituir as leituras diretas de `participacao.conclusao` nas telas pela função.
- [X] T039 [US1] Ajustar os testes de fronteira para os imports novos, sem afrouxar as demais regras:
  - `tests/interface/test_interface_fronteiras.py` (`PERMITIDOS_NA_INTERFACE`);
  - `tests/acesso/test_fronteiras.py`.

**Checkpoint.** O MVP é US2 + US1: o egresso declara e responde, e nada contamina os dados
oficiais.

---

## Fase 5 — US3: validar vinculando uma Conclusão da fonte digital (P1) (9 tasks)

**Goal.** O operador, no escopo, valida pela candidata ou pela referência na fonte. A
resposta passa a oficial sem o egresso voltar.

**Independent Test.**
- Pessoa sem data de nascimento: declara e é validada pela candidata.
- Pessoa não importada: validada pela referência.

Em seguida, verificar vínculo, situação, snapshot seguinte e declaração intacta.

### Testes

- [X] T040 [P] [US3] Escrever `tests/declaracao/test_validacao.py` (FR-070 a FR-077; R11):
  - **Candidata.** Só com o mesmo `identificador_cpf`; outra dá `ForaDoEscopo`.
  - **Referência na fonte.** Incorpora Pessoa e Conclusão com material pela 018. Referência inexistente ou fonte indisponível não grava nada.
  - **`NAO_CONFIRMADA`.** Grava só a decisão.
  - **Recusas.** `JaDecidida` (inclusive com duas transações); `ForaDaFila` com rascunho; `ForaDoEscopo` para CSAEG fora da unidade declarada ou da Conclusão.
  - **Integridade.** A validação nunca altera Participação, declaração nem Respostas (FR-015).
  - **Divergência.** É derivada.
  - **Campos gravados.** `operador` e `registrada_em`.
- [X] T041 [P] [US3] Escrever `tests/participacao/test_iniciar_concorrencia.py` (FR-092, FR-093; R10):
  - depois de uma `DECLARADA_VALIDADA` para X em C, `iniciar_participacao(C, X)` devolve a declarada como `JA_EXISTENTE`;
  - confirmação e início institucional simultâneos (duas transações, padrão 005 R11) nunca deixam duas oficiais com a mesma Conclusão efetiva.
- [X] T042 [P] [US3] Escrever `tests/declaracao/test_rotas_validacao.py` (FR-060 a FR-065, FR-076, FR-116; contracts/rotas.md):
  - **Fila por operador.** A vê tudo; B (CSAEG Vitória) vê só Vitória; C é recusado.
  - **Fila sem dados sensíveis.** Sem CPF, data, Respostas nem HMAC.
  - **Detalhe.** Mostra candidatas e outras declarações do mesmo `identificador_cpf`, nunca agrupando pelo `verificador`. Fora do escopo dá 404 indistinguível.
  - **Revelação.** `POST revelar/` grava `AcessoAosDadosDeConsulta` sem valores e mostra nome, CPF e data. `GET` não revela.
  - **Revelação indisponível.** Chave B inválida: "indisponível" e nenhum acesso registrado. Dados descartados (linha removida): "não estão mais disponíveis".
  - **Registro.** Exige a confirmação explícita.
  - **Cabeçalhos.** `no-store`.

### Implementação

- [X] T043 [US3] Em `trajetoria/participacao/operacoes.py`, `iniciar_participacao`:
  - depois de reler a Conclusão, `select_for_update` nela;
  - sem Participação institucional `(C, X)` e com declarada oficial de Conclusão efetiva X em C, devolve `Inicio(declarada, JA_EXISTENTE)` (R10).

  Documentar na docstring.
- [X] T044 [US3] Em `trajetoria/declaracao/operacoes.py`, `registrar_validacao` com as origens `candidata` e `referencia_fonte`, conforme contracts/operacoes.md:
  - bloqueio da declaração e depois da Conclusão;
  - `fora_da_abrangencia_na_validacao` congelado;
  - `conflito_detectado_na_validacao` só se compatível.

  Implementar também `revelar_dados`, com o registro de acesso antes de abrir o selo, na mesma transação.
- [X] T045 [US3] Em `trajetoria/declaracao/consultas.py`:
  - `fila(vinculos)`: concluídas sem decisão mais conflitos pendentes, no escopo pela unidade declarada;
  - `candidatas(formacao)`;
  - `outras_do_mesmo_cpf(formacao)`;
  - `divergencia(formacao, conclusao)`;
  - `conflito_potencial(formacao, conclusao)`.
- [X] T046 [US3] Em `trajetoria/declaracao/views_validacao.py`, com rotas em `trajetoria/declaracao/urls.py`, as rotas `/validacoes-formacao/`, `<id>/`, `<id>/revelar/` e `<id>/registrar/` (contracts/rotas.md).
  - **Barreira.** Com `pode_validar_formacao`, no padrão de `trajetoria/acompanhamento/acesso.py`.
  - **Templates.** Em `templates/declaracao/validacao/`, na navegação do acompanhamento.
  - **Texto.** "Registra o resultado obtido junto à instância competente" (FR-062).
- [X] T047 [US3] Ajustar `tests/governanca/test_governanca_fronteiras.py` e criar `tests/declaracao/test_fronteiras.py`:
  - **Imports permitidos** (data-model, "Dependências entre módulos").
  - **Dados sensíveis.** `DadosConsultaAcervo.selado` e os HMACs nunca em `__str__` nem `repr`.
  - **Âncora sem escrita.** Nenhuma escrita de Participação fora de `participacao.operacoes` e `declaracao.operacoes.iniciar_participacao_declarada`.
  - **Migrações.** Nenhuma pendente.
  - **FR-119.** `trajetoria/acesso/` não importa `trajetoria.declaracao`. `abrir_consulta` só é chamado por `revelar_dados`.
  - **FR-130.** Fora do modo de demonstração, `/declaracao/…` e `/validacoes-formacao/…` respondem 404.
- [X] T048 [US3] Em `trajetoria/declaracao/views_validacao.py`, o aviso de conflito potencial antes do registro (FR-090). Mostra só a existência da outra Participação, sem dados dela nem Respostas.

---

## Fase 6 — US4: validar pelo acervo histórico (P1) (5 tasks)

**Goal.** Confirmar uma formação que só existe no acervo físico. A Conclusão nasce pela
incorporação, com `fonte = "acervo_historico"`.

**Independent Test.** Declaração de formação inexistente na fonte simulada, depois
registro da Referência e então:
- a Conclusão nasce do acervo;
- a declaração fica intacta;
- a divergência é exibida;
- a Participação entra no snapshot seguinte com `declarada_validada_acervo`.

### Testes

- [X] T049 [P] [US4] Escrever `tests/declaracao/test_acervo.py` (FR-080 a FR-084; contracts/fonte-acervo.md):
  - **Registro.** `registrar_referencia` converge para a mesma `(unidade, referencia)` com espaços normalizados e valores iguais. Com valores diferentes, levanta `ReferenciaDivergente` sem gravar.
  - **Contrato da fonte.** `obter_pessoa("acervo:<uuid>")` e `obter_conclusao` seguem o contrato, sem CPF e sem data. Incluir a fonte nos testes parametrizados de `tests/test_contrato_fonte.py`.
  - **Incorporação.** Cria Pessoa e Conclusão com `fonte="acervo_historico"`. A mesma referência converge.
  - **CPF coincidente.** Com Pessoa de outra fonte de mesmo `identificador_cpf`: nenhuma fusão, e a sinalização vem sem valores.
- [X] T050 [P] [US4] Escrever `tests/declaracao/test_rotas_acervo.py` (FR-073, FR-077, FR-082):
  - **Formulário.** Os campos do acervo vêm vazios, nunca com valores declarados no `value`. O declarado aparece só para leitura.
  - **Validação pelo acervo.** Com curso e ano diferentes, ponta a ponta: "confirmada com dados diferentes" e exportação seguinte com `declarada_validada_acervo`.
  - **Escopo.** CSAEG não registra acervo de outra unidade.

### Implementação

- [X] T051 [US4] Implementar `trajetoria/declaracao/acervo.py`:
  - `registrar_referencia(dados, *, operador, agora)`;
  - `FonteAcervoHistorico`, com `codigo="acervo_historico"`, `obter_pessoa` e `obter_conclusao` conforme contracts/fonte-acervo.md.

  Depende só de `fonte_academica.contrato` e de `declaracao.models`.
- [X] T052 [US4] Em `trajetoria/declaracao/operacoes.py`, ramo `acervo` de `registrar_validacao`: `registrar_referencia`, depois `incorporar_encontrada(FonteAcervoHistorico.codigo, fonte.obter_pessoa(...))` e então a Conclusão. Em `trajetoria/declaracao/views_validacao.py`, a seção do formulário de acervo, conforme contracts/rotas.md.
- [X] T053 [US4] Em `trajetoria/demonstracao/base.py`, `base_somente_simulada` admite as fontes `simulada` e `acervo_historico` (FR-131). Ajustar `tests/acesso/test_demonstracao.py` e os testes de barreira da 016 e da 018 que dependem do predicado.

---

## Fase 7 — US5: não confirmar, fora da abrangência e conflito (P1) (3 tasks)

**Goal.** Nenhum desfecho apaga dados, e nada é contado duas vezes.

**Independent Test.** Não confirmada; confirmada fora de Campanha restrita; confirmada com
Participação institucional existente. Nos três casos: preservação, situação correta e
oficial anterior intacta.

- [X] T054 [P] [US5] Escrever `tests/declaracao/test_desfechos.py` (FR-024, FR-050, FR-051, FR-090):
  - **Não confirmada.** Fica preservada e fora das oficiais.
  - **Fora da abrangência.** Campanha restrita a pós-graduação em Vila Velha e confirmação para graduação: `DECLARADA_FORA_DA_ABRANGENCIA`, sem conflito calculado.
  - **Conflito com institucional.** Participação institucional (rascunho e concluída) já existente para X: `DECLARADA_EM_CONFLITO`, e a institucional fica inalterada.
  - **Conflito com declarada.** Segunda declarada validada para X: a primeira continua oficial e a segunda fica em conflito.
  - **Fila.** Mostra o conflito como "resolução administrativa pendente".
- [X] T055 [US5] Em `trajetoria/declaracao/consultas.py` (`fila`) e `trajetoria/declaracao/templates/declaracao/validacao/`, exibir as decisões em conflito pendente na fila, com o rótulo "resolução administrativa pendente", sem ação de resolver (DP-1907).
- [X] T056 [US5] Revisar `trajetoria/declaracao/operacoes.py` contra os cenários de T054. A ordem é: abrangência, depois conflito só se compatível, conforme o CHECK do data-model. Corrigir o que T054 apontar.

---

## Fase 8 — US6: abrangência provisória ao declarar (P2) (2 tasks)

**Goal.** Campanha com abrangência restrita alcança quem declara uma formação compatível.

- [X] T057 [P] [US6] Escrever `tests/declaracao/test_compatibilidade.py` (FR-020 a FR-023; E7):
  - critérios de unidade, nível e ano com valores declarados compatíveis e incompatíveis;
  - critério de modalidade ou forma de oferta não impede;
  - Campanha sem critério mais Campanha restrita compatível: ambiguidade;
  - declaração nunca entra em `populacao_no_momento`;
  - nenhuma configuração de comunicação (016) participa.
- [X] T058 [US6] Ajustar `campanhas_compativeis` em `trajetoria/declaracao/operacoes.py` e as telas de sem pesquisa e ambiguidade em `trajetoria/declaracao/views_egresso.py`, se T057 apontar divergência. Nenhuma regra nova além da 004.

---

## Fase 9 — US7: retomar a declaração sem duplicar (P2) (2 tasks)

**Goal.** O mesmo par reencontra as próprias declarações; outro par não vê nada.

- [X] T059 [P] [US7] Escrever `tests/declaracao/test_retomada.py` (FR-043; E8):
  - **Mesmo par.** Lista a declaração em andamento ("Continuar") e a concluída ("Resposta registrada", sem situação da validação). Com Campanha encerrada, mostra o período encerrado.
  - **Mesmo CPF, outra data.** Não lista. Uma nova declaração aparece ao validador entre as outras do mesmo CPF.
  - **Outra formação.** "Informar outra formação" gera um novo selo de início e permite outra declaração.
- [X] T060 [US7] Em `trajetoria/declaracao/views_egresso.py` (`POST` e `GET /declaracao/`) e no template da lista: estabelecer a sessão com `declaracoes_do_par` e listar as declarações em Campanhas em coleta com as situações de FR-043.
  - No `POST`, com selo: "Informar outra formação" é um formulário POST para `/declaracao/nova/` com o selo oculto.
  - No `GET`, sem selo: só "Continuar" e "Resposta registrada", e um link para `/acesso/`.

---

## Fase 10 — US8: acompanhar a fila sem expor pessoas (P2) (2 tasks)

**Goal.** Um único indicador agregado na 011, no escopo, com link para a fila.

- [X] T061 [P] [US8] Escrever `tests/acompanhamento/test_acompanhamento_validacoes.py` (FR-101):
  - "Validações de formação: N na fila" com N igual a `len(fila(vinculos))` para A e B;
  - link só com a capacidade;
  - taxas inalteradas;
  - nenhum nome na página.
- [X] T062 [US8] Em `trajetoria/acompanhamento/views.py` e no template do detalhe da Campanha, exibir o indicador. Reusar `declaracao.consultas.fila`, sem contagem paralela.

---

## Fase 11 — Acabamento e verificações transversais (7 tasks)

- [X] T063 Demonstração (FR-132, R21):
  - em `trajetoria/fonte_academica/cenarios.py`, um par fictício inexistente para declaração e uma Pessoa presente na fonte e excluída do preparo;
  - em `trajetoria/demonstracao/cenario.py`, não importar essa Pessoa;
  - em `trajetoria/acesso/demonstracao.py`, o painel com os pares de declaração;
  - ajustar `tests/acesso/test_preparo.py` e `tests/acesso/test_demonstracao.py`.

  O preparo não cria declarações nem validações.
- [X] T064 [P] Escrever `docs/adr/0005-criptografia-dados-consulta-acervo.md`, com:
  - Fernet e `cryptography`;
  - as duas chaves por finalidade;
  - a regra de rotação com `MultiFernet` (chave antiga mantida até todos os registros serem recifrados);
  - o descarte por remoção da linha;
  - as alternativas rejeitadas.

  Fonte: R5 e R6.
- [X] T065 [P] Escrever `tests/declaracao/test_acessibilidade.py`, no padrão de `tests/acesso/test_acessibilidade.py`, para as telas de declaração, lista, confirmação, fila e validação (FR-120, FR-121; SC-009):
  - rótulos e erros associados;
  - foco no resumo;
  - ano com `inputmode="numeric"`;
  - revelação por botão;
  - largura de 320 px sem rolagem horizontal.
- [X] T066 Estender `tests/declaracao/test_vazamento.py` (T031) com a revelação e o registro de acesso: o log não tem valores, e `AcessoAosDadosDeConsulta` não guarda CPF nem data. Revisar os `logger.*` novos de `trajetoria/declaracao/` (Princípio XVI; Observabilidade).
- [X] T067 [P] Aplicar as notas de revisão listadas em spec.md, "Impacto nas features anteriores":
  - specs 001, 004, 005, 006, 007, 008, 011, 012, 013 e 018;
  - `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`;
  - a nota de leitura de 013 FR-021 (R15).
- [X] T068 Remover o comentário "Sync Impact Report" do topo de `.specify/memory/constitution.md`, como exige o próprio relatório antes do commit da emenda.
- [X] T069 Executar `uv run pytest` e `uv run ruff check .`, percorrer o quickstart.md com dados fictícios e verificar a Definition of Done constitucional. Confirmar que nenhuma DECISÃO PENDENTE (DP-1901 a DP-1911) virou regra implícita no código ou nas telas (Princípio XXIX).

---

## Dependências

```text
Fase 1 → Fase 2 → US2 (quarentena) → US1 (MVP) → US3 → US4
                                         │        └→ US5 (após US3)
                                         ├→ US6 (após US1)
                                         ├→ US7 (após US1)
                                         └→ US8 (após US3: usa a fila)
Acabamento: após as histórias desejadas.
```

- **US2 antes de US1.** Nenhuma declaração existe sem a oficialidade já aplicada.
- **US4 e US5 dependem de US3.** Usam `registrar_validacao`, a fila e as telas.
- **US6 e US7 dependem de US1.** São rotas e operações do egresso.

## Paralelismo

- **Fase 2.** T004 a T008 juntos; T012 em paralelo com T009 e T010.
- **US2.** T015 a T019 juntos. As implementações T020, T021, T025 e T022 a T024 tocam
  apps diferentes. Dentro do `analitico`, a ordem é T022, T023 e T024.
- **US1.** T027 a T031 juntos. T034 e T035 em paralelo com T032 e T033.
- **US3.** T040 a T042 juntos.
- **Acabamento.** T064, T065 e T067 em paralelo.

## Estratégia

1. **MVP = Fase 1 + Fase 2 + US2 + US1.** O egresso declara e responde, com a quarentena
   já garantida nas quatro superfícies oficiais.
2. **US3 → US5 → US4.** A validação libera respostas pela fonte digital, depois os
   desfechos e depois o acervo, o caso dos egressos antigos.
3. **US6, US7 e US8.** Fecham a experiência e a operação.
4. Antes da implementação: `/speckit-analyze` cruzando Constituição 2.0.0, spec, plan e
   tasks.

**Total**: 69 tasks.

| Fase | Tasks |
| --- | --- |
| Setup | 3 |
| Fundação | 11 |
| US2 | 12 |
| US1 | 13 |
| US3 | 9 |
| US4 | 5 |
| US5 | 3 |
| US6 | 2 |
| US7 | 2 |
| US8 | 2 |
| Acabamento | 7 |


## Registro de implementação

- **T033 × T047 (revisto no code review de 2026-10-04).** A primeira implementação
  importava `declaracao.selo` na 018. Corrigido:
  - o selo de trânsito (chave A) passou a ser da própria 018, em `acesso/transito.py`,
    como ponto de saída de `NAO_CONFIRMADA` (018 FR-035);
  - a 019 o consome em `declaracao/selo.py` e valida as duas chaves;
  - o sujeito declarante saiu de `acesso/sessao.py` para `declaracao/sessao.py`, sem
    `apps.get_model`;
  - a 018 não importa nem referencia a 019, e `tests/declaracao/test_fronteiras.py`
    verifica isso sem exceção.
- **Indicador da Campanha (revisto no code review).** Conta só os itens da fila da
  Campanha exibida, no escopo do operador (FR-101). A contagem pela fila inteira induzia a
  erro numa página de Campanha.
- **Outras correções do code review**, todas com teste de regressão:
  - a verificação de integridade do snapshot ignorava Participações por causa de `NULL`
    dentro do `NOT IN`;
  - duas oficiais com a mesma Conclusão efetiva agora recusam a captura;
  - a Pessoa vê a sua Conclusão na tela de "já respondida";
  - o aviso `saida` chega ao declarante;
  - `declarada` passa a ser explícito nas telas;
  - o código da fonte de acervo é constante única (`fonte_academica/acervo_historico.py`);
  - a migração usa `bulk_update`;
  - a sessão do declarante é revalidada uma vez por requisição.

- Cobertura transversal complementada em `tests/declaracao/test_transversal.py`: selos
  fora da sessão e dos redirecionamentos, CSRF, incorporação por referência, ausência de
  escrita em falha, auditoria revertida em token inválido e coincidência sem fusão.
- O adaptador do acervo passou pelo núcleo aplicável da suíte comum do contrato. Os
  três casos sem equivalente no acervo (pessoa sem conclusão, registro não concluído e
  falha externa simulada) têm skips explícitos com justificativa.

- Validação final: suíte completa com **2.216 testes passando**, 3 skips justificados
  no contrato do acervo e 1 teste de volume fora da seleção padrão. Cinco verificações
  complementares de fronteira e sigilo passaram após a última extensão da cobertura.
  Lint, checks do Django, migrações pendentes e whitespace: sem problemas.
  Evidências e Definition of Done em [validacao.md](validacao.md).
