---

description: "Tasks da Feature 020 — Mobilização real, Lotes e contatos do egresso"
---

# Tasks: Mobilização real, Lotes e contatos do egresso

**Input**: `specs/020-mobilizacao-real-lotes-contatos/` — [spec](spec.md), [plan](plan.md),
[research](research.md), [data-model](data-model.md), [contracts/](contracts/),
[quickstart](quickstart.md).

**Tests**: obrigatórios (Constituição XXVI). A feature toca autorização, providers,
elegibilidade (ADR 0004), preservação histórica e privacidade. Os testes de cada história
vêm antes da implementação.

**Escopo**: somente demonstração. O envio real fica **desativado** (Gates A e B; DP-2010).
O adaptador de contatos é **fictício** (`example.invalid`).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: paralelizável (arquivos diferentes, sem dependência pendente)
- **[USn]**: história da spec (US1 a US7)

---

## Phase 1: Setup

- [ ] T001 Criar os apps vazios `trajetoria/contato/` (`__init__.py`, `apps.py` com `name="trajetoria.contato"`) e `trajetoria/mobilizacao/` (idem) e registrá-los em `INSTALLED_APPS` de `config/settings.py`, depois de `trajetoria.contexto_trajetoria` e antes de `trajetoria.comunicacao`
- [ ] T002 [P] Acrescentar a `config/settings.py` as configurações do research R15, sem padrão permissivo:
  - `TRAJETORIA_ENVIO_REAL = os.environ.get("TRAJETORIA_ENVIO_REAL", "")`, que só `"1"` liga;
  - `TRAJETORIA_REMETENTE_INSTITUCIONAL` e `TRAJETORIA_URL_ENTRADA`, padrão `""`;
  - `TRAJETORIA_LOTE_ENVIO_POR_ACAO`, inteiro, padrão 100.

  Documentar as quatro em `.env.example` com o aviso "envio real desativado até os Gates A e B (DP-2010)"
- [ ] T003 [P] Criar os pacotes de teste `tests/contato/__init__.py`, `tests/contato/conftest.py`, `tests/mobilizacao/__init__.py` e `tests/mobilizacao/conftest.py`. As fixtures:
  - Pessoas e Conclusões simuladas via `tests/acesso/construcao.py` ou equivalente;
  - Campanha EM_COLETA, EM_PREPARACAO e ENCERRADA;
  - vínculos CPAEG e CSAEG fictícios;
  - transporte locmem com `TRAJETORIA_COMUNICACAO_TESTE=True`, como em `tests/comunicacao/conftest.py`

---

## Phase 2: Foundational (bloqueia todas as histórias)

- [ ] T004 [P] Teste de `normalizar_email` em `tests/contato/test_endereco.py`:
  - remove espaços externos;
  - recusa CR, LF, `<>,;`, espaço interno e tabulação;
  - aplica `validate_email`;
  - põe o domínio em minúsculas e preserva a parte local;
  - recusa mais de 254 caracteres;
  - não exige `example.invalid`
- [ ] T005 [P] Implementar `normalizar_email(valor) -> str` em `trajetoria/contato/endereco.py`. Valor inválido levanta `EnderecoInvalido`, sem o valor na mensagem (research R4)
- [ ] T006 Criar o model `ContatoDaPessoa` em `trajetoria/contato/models.py` conforme data-model §1:
  - `id` UUID;
  - `pessoa` FK `academico.Pessoa` `on_delete=PROTECT`, `related_name="+"`;
  - `canal` TextChoices só `EMAIL`;
  - `valor` "Texto ≤ 254";
  - `origem` TextChoices `FONTE_ACADEMICA` | `EGRESSO`;
  - `fonte` nulo;
  - `posicao` PositiveSmallInteger nulo;
  - `obtido_em` DateTimeField sem `auto_now_add`.

  Restrições:
  - CHECK "origem fonte exige `fonte` e `posicao`; origem egresso exige ambos nulos";
  - CHECK `valor` e `fonte` não vazios (`_nao_vazio`);
  - `UniqueConstraint(fields=["pessoa","fonte","obtido_em","posicao"], condition=Q(origem="FONTE_ACADEMICA"))`;
  - índice `(pessoa, origem, obtido_em)`.

  Gerar `trajetoria/contato/migrations/0001_initial.py`
- [ ] T007 [P] Teste do model em `tests/contato/test_modelo.py`:
  - cada CHECK e a unicidade recusam no banco;
  - `Pessoa` continua com os campos `{"id","fonte","id_externo","nome","incorporado_em"}`;
  - `Pessoa` não tem relação reversa de contato
- [ ] T008 [P] Teste da política em `tests/contato/test_politica.py`, um caso por ramo de FR-008:
  - o `EGRESSO` mais recente vence o importado;
  - sem egresso, a observação de fonte mais recente vale, menor `posicao`;
  - registro inválido é pulado para o próximo da mesma observação;
  - sem nenhum, `None`;
  - o instante *t* ignora registros posteriores
- [ ] T009 Implementar `contato_utilizavel(pessoa_id, agora) -> ContatoDaPessoa | None` em `trajetoria/contato/politica.py` (data-model §1), sem aleatoriedade nem score
- [ ] T010 Criar os models `LoteDeMobilizacao` e `MembroDoLote` em `trajetoria/mobilizacao/models.py` conforme data-model §§2–3.

  `LoteDeMobilizacao`:
  - `campanha` FK `PROTECT` `related_name="+"`;
  - `nome` "Texto ≤ 120, não vazio";
  - `unidades` ArrayField nulo, com "NULL significa sem filtro; `[]` é proibido";
  - `nivel`, `curso`, `ano_minimo` e `ano_maximo` nulos;
  - `escopo_institucional` e `escopo_unidades`;
  - `excluidas_por_mobilizacao` ≥ 0;
  - `confirmado_em` e `operador` não vazio;
  - CHECKs de anos, de escopo e "se o escopo não é institucional, `unidades` não é nulo".

  `MembroDoLote`:
  - `lote` FK `related_name="membros"`;
  - `campanha`, `pessoa` e `contato` (nulo) FKs `PROTECT` `related_name="+"`;
  - `situacao` TextChoices `SEM_CONTATO`, `NAO_TENTADO`, `EM_TENTATIVA`, `SUBMETIDO_AO_TRANSPORTE`, `FALHA_DE_TRANSPORTE`;
  - `tentativa_iniciada_em` e `resultado_em` nulos.

  Restrições de `MembroDoLote`:
  - `UNIQUE(lote, pessoa)`;
  - `UniqueConstraint(fields=["campanha","pessoa"], condition=~Q(situacao="SEM_CONTATO"), name="membro_uma_abordagem_por_campanha")`;
  - CHECK `SEM_CONTATO ⇔ contato IS NULL`;
  - CHECK de coerência temporal por situação.

  Gerar `trajetoria/mobilizacao/migrations/0001_initial.py`
- [ ] T011 [P] Teste dos models em `tests/mobilizacao/test_modelo.py`: cada CHECK e as duas unicidades recusam no banco, inclusive o segundo membro não `SEM_CONTATO` da mesma Pessoa e Campanha em outro Lote
- [ ] T012 Em `trajetoria/governanca/regras.py`, acrescentar `pode_consultar_lotes`, `pode_preparar_lote` e `pode_enviar_lote` (CPAEG ou CSAEG ativos; docstring "interpretação local reversível, só demonstração — DP-2001") ao `__all__`. **Manter** `pode_simular_comunicacao` até T061
- [ ] T013 Atualizar a enumeração de regras públicas em `tests/governanca/test_governanca_regras.py` e a lista de capacidades administrativas em `tests/exportacao/test_exportacao_fronteiras.py` e `tests/analitico/test_analitico_fronteiras.py` para incluir as três novas
- [ ] T014 Implementar a seleção compartilhada em `trajetoria/mobilizacao/selecao.py`:

  ```text
  selecionar(campanha, escopo, filtros, agora) -> Selecao(conclusoes, pessoas: tuple[(pessoa_id, contato|None)], excluidas)
  ```

  Ordem FR-017:
  1. `campanha.consultas.populacao_no_momento`;
  2. escopo `unidade__in` quando não institucional;
  3. filtros;
  4. Pessoas distintas por `pessoa_id` em ordem de `pk`;
  5. exclusão de quem tem `MembroDoLote` da mesma Campanha com `situacao != SEM_CONTATO`;
  6. `contato_utilizavel`.

  `Filtros` é um dataclass validado: anos coerentes, unidades não vazias quando presentes, textos sem CR/LF

---

## Phase 3: User Story 1 — Preparar e confirmar um Lote (P1) 🎯 MVP

**Goal**: prévia transitória e Lote congelado com membros por Pessoa e contato escolhido.

**Independent Test**: confirmar um Lote na demonstração e conferir membros, contatos e
contagens sem enviar nada.

### Tests (US1)

- [ ] T015 [P] [US1] `tests/mobilizacao/test_selecao.py`:
  - a ordem FR-017 é respeitada;
  - Pessoa com duas Conclusões no recorte vira um membro;
  - Pessoa com Conclusão fora da abrangência e outra dentro entra;
  - CSAEG Serra não seleciona por Conclusão de Vitória;
  - sem contato continua membro;
  - os filtros de unidade, nível, anos e curso (igualdade textual) funcionam;
  - não há deduplicação por nome ou e-mail
- [ ] T016 [P] [US1] `tests/mobilizacao/test_confirmacao.py`:
  - a prévia não grava nada;
  - a confirmação grava o Lote e os membros numa transação;
  - Lote vazio é recusado (422);
  - a Campanha EM_PREPARACAO e EM_COLETA aceita, e a ENCERRADA recusa (409);
  - sem filtros no escopo institucional, falta de `confirmo_abrangencia` é recusada (422);
  - `excluidas_por_mobilizacao` é gravado;
  - situação inicial `SEM_CONTATO` ou `NAO_TENTADO`;
  - a confirmação ignora qualquer lista ou contato enviado pelo cliente
- [ ] T017 [P] [US1] `tests/mobilizacao/test_imutabilidade.py`: nenhuma operação altera filtros, membros ou contato de Lote confirmado, nem apaga Lote; não há rota de edição ou remoção (405 ou 404)

### Implementation (US1)

- [ ] T018 [US1] Implementar `previa(...)` e `confirmar_lote(campanha_id, operador, nome, filtros, confirmo_abrangencia, *, agora=None)` em `trajetoria/mobilizacao/operacoes.py` (contracts/transporte.md, "Confirmação"):
  - transação com `Campanha.objects.select_for_update().get(pk=...)`;
  - estado EM_PREPARACAO ou EM_COLETA (`campanha.consultas.estado`);
  - `selecionar`;
  - recusa de Lote vazio;
  - verificação `contato.pessoa_id == pessoa_id`;
  - `bulk_create` com `campanha` copiada do Lote.

  Recusas por `RecusaDeLote(categoria, status)` sem dado pessoal
- [ ] T019 [US1] Implementar o gate em `trajetoria/mobilizacao/acesso.py`:
  - decorator `@lotes` com atributo marcador `lotes=True`, que exige demonstração ligada, operador fictício e `pode_consultar_lotes`, e define `request.lotes` (contexto com escopo e atuação);
  - `lote_visivel(lote, escopo)`, conforme o research R10;
  - `campanha_autorizada` reutilizando `acompanhamento.consultas.campanhas_visiveis`
- [ ] T020 [US1] Implementar as views `lotes` (GET: lista e prévia com filtros da query) e `confirmar` (POST, `require_POST`, CSRF, 303 ao detalhe) em `trajetoria/mobilizacao/views.py`, com `Cache-Control: no-store` e as recusas da contracts/rotas.md
- [ ] T021 [US1] Criar `trajetoria/mobilizacao/templates/mobilizacao/lotes.html` no shell administrativo do acompanhamento (research R13):
  - lista de Lotes visíveis;
  - `<form method="get">` de filtros com `fieldset`/`legend`, unidades em checkbox a partir das unidades das Conclusões no escopo;
  - prévia com Conclusões, Pessoas, com contato, sem contato e excluídas;
  - formulário POST com `nome` e a caixa "Confirmo que este Lote abrange N Pessoas" quando exigida;
  - nenhum nome ou endereço
- [ ] T022 [US1] Registrar em `trajetoria/acompanhamento/urls.py` as rotas `campanhas/<uuid:campanha>/lotes/` e `campanhas/<uuid:campanha>/lotes/confirmar/`. Em `tests/acompanhamento/test_acompanhamento_acesso.py`, `test_toda_rota_exige_o_gate_de_acompanhamento` passa a aceitar a marca `lotes` para caminhos com `/lotes/`
- [ ] T023 [US1] Em `trajetoria/acompanhamento/templates/acompanhamento/campanha.html`, acrescentar o link "Lotes de mobilização", exibido quando a atuação tem `pode_consultar_lotes`. O link "Comunicação simulada" permanece até T061

**Checkpoint**: US1 testável sozinha (prévia e confirmação, sem envio).

---

## Phase 4: User Story 2 — Enviar um Lote e entender o resultado (P1)

**Goal**: envio por modo, retomável, com situações honestas e modo real desativado.

**Independent Test**: em teste (locmem), enviar um Lote e conferir `mail.outbox`,
situações e contagens. Em demonstração, o mesmo com Mailpit (quickstart).

### Tests (US2)

- [ ] T024 [P] [US2] `tests/comunicacao/test_transporte.py`, para `transporte_de_envio()` (contracts/transporte.md):
  - teste só com `TRAJETORIA_COMUNICACAO_TESTE` e locmem;
  - demonstração com as barreiras da 016 (loopback, porta 1025, sem credenciais, TLS ou SSL, remetente fictício, URL local);
  - real recusa isoladamente cada exigência faltante (envio real ≠ "1", demonstração ligada, sem TLS/SSL, sem usuário, sem senha, remetente vazio ou inválido, URL não https ou com query/fragmento, base com dados simulados);
  - combinação ambígua recusa `transporte_inseguro`;
  - nenhuma recusa abre conexão (mock do backend)
- [ ] T025 [P] [US2] `tests/comunicacao/test_convite_modos.py`:
  - o renderer em demonstração mantém o texto da 016 (regressão);
  - em real usa `convite_real.*` com o marcador "Texto provisório — pendente de aprovação institucional";
  - texto e HTML equivalentes;
  - link neutro igual para todos;
  - nenhum id de Pessoa, Lote, membro, CPF ou token;
  - `validar_conteudo` recusa recurso externo, pixel e URL diferente da do modo;
  - destinatário fora de `example.invalid` recusado em teste e demonstração e aceito em real
- [ ] T026 [P] [US2] `tests/mobilizacao/test_envio.py`:
  - só EM_COLETA (EM_PREPARACAO e ENCERRADA → 409, membros intactos);
  - uma tentativa por membro com contato;
  - `SUBMETIDO_AO_TRANSPORTE` quando `send()==1`;
  - `FALHA_DE_TRANSPORTE` com `SMTPException`/`OSError`, sem retry;
  - `tentativa_iniciada_em` e `resultado_em` gravados;
  - a mensagem vai para o contato **congelado**;
  - situação derivada do Lote (não enviado, parcial, concluído);
  - totais sem endereço;
  - nenhum "entregue", "aberto" ou "clicado" no HTML;
  - membro cuja Pessoa saiu da população depois da confirmação continua sendo enviado pelo congelado (borda da spec)
- [ ] T027 [P] [US2] `tests/mobilizacao/test_retomada.py` (research R14):
  - com `TRAJETORIA_LOTE_ENVIO_POR_ACAO=1`, ações sucessivas processam um membro cada, sem repetir;
  - transporte de teste com exceção inesperada no k-ésimo envio: a ação é interrompida (500), o membro k fica `EM_TENTATIVA` e aparece como "resultado incerto";
  - a nova ação processa só `NAO_TENTADO` e nunca reenvia o incerto;
  - membro `EM_TENTATIVA` criado diretamente no banco (queda simulada) nunca volta a `NAO_TENTADO`
- [ ] T028 [P] [US2] `tests/mobilizacao/test_link_neutro.py`: seguir a URL da mensagem não autentica, não cria Participação nem sessão e não seleciona formação ou Campanha (FR-027; 018 FR-053)

### Implementation (US2)

- [ ] T029 [US2] Criar `trajetoria/comunicacao/transporte.py` com `transporte_de_envio()`, `Transporte(modo, conexao())` e `RecusaDeTransporte(categoria)` (research R8). Migrar para ele as barreiras de `TransporteLocal` de `trajetoria/comunicacao/seguranca.py` e acrescentar o modo real, sem nomear fornecedor
- [ ] T030 [US2] Em `trajetoria/comunicacao/seguranca.py`:
  - separar `validar_destinatario(endereco, modo)`, que usa `contato.endereco.normalizar_email` e exige `example.invalid` só em teste e demonstração;
  - parametrizar `validar_url(url, modo)`: local da 016 em demonstração e teste; `https` sem credenciais, query ou fragmento em real;
  - parametrizar `validar_conteudo(texto, html, url_permitida)`;
  - `validar_mensagem` aceita o remetente do modo;
  - trocar todas as recusas de `seguranca.py` (hoje `RecusaComunicacao`, importada de `comunicacao/acesso.py`, que T060 remove) por `RecusaDeTransporte` de `comunicacao/transporte.py`, mantendo as categorias
- [ ] T031 [US2] Em `trajetoria/comunicacao/convite.py`, acrescentar o parâmetro `modo` a `renderizar_convite` (templates de demonstração ou `convite_real.*`, remetente do modo). Criar `trajetoria/comunicacao/templates/comunicacao/convite_real.txt` e `convite_real.html` (provisórios, DP-2003, mesmo CTA neutro, sem recursos externos, com o marcador de texto provisório)
- [ ] T032 [US2] Implementar `enviar_lote(lote_id, operador, *, agora=None) -> ResultadoDoEnvio` em `trajetoria/mobilizacao/operacoes.py`, seguindo exatamente o algoritmo de contracts/transporte.md "Envio":
  - revalidação;
  - lote de até N membros `NAO_TENTADO` por `pk`;
  - (a) transação curta com `select_for_update(skip_locked=True)`, recheck e gravação de `EM_TENTATIVA`;
  - (b) envio fora de transação, uma conexão por mensagem;
  - (c) gravação do resultado;
  - (d) interrupção em exceção inesperada;
  - nunca registrar texto de exceção
- [ ] T033 [US2] Implementar as views `lote` (GET detalhe) e `enviar` (POST) em `trajetoria/mobilizacao/views.py` e as rotas `campanhas/<uuid:campanha>/lotes/<uuid:lote>/` e `.../enviar/` em `trajetoria/acompanhamento/urls.py`. Depois do envio, 303 ao detalhe com aviso por categoria e totais; 500 com aviso de "a caixa pode conter mensagens" se interrompido
- [ ] T034 [US2] Criar `trajetoria/mobilizacao/templates/mobilizacao/lote.html` com:
  - filtros, momento, operador (rótulo) e contagens por situação (sem contato, não tentados, submetidos ao transporte, falhas, resultado incerto);
  - situação derivada;
  - os textos de FR-042: "aceite do transporte não comprova entrega"; "pertencer ao Lote não prova que a comunicação causou resposta";
  - sem "alcance", "entregues" ou "conversão";
  - botão "Enviar" ou "Continuar envio" só quando há não tentados e a Campanha está EM_COLETA, com explicação textual nos outros casos

**Checkpoint**: US1 + US2 entregam a mobilização completa na demonstração.

---

## Phase 5: User Story 3 — Evitar mobilização duplicada (P1)

**Goal**: no máximo uma abordagem por Pessoa e Campanha, inclusive sob concorrência.

**Independent Test**: dois Lotes sobrepostos, com exclusões e contagens; envio concorrente.

- [ ] T035 [P] [US3] `tests/mobilizacao/test_duplicidade.py`:
  - exclusão por situação (FR-024): `NAO_TENTADO`, `EM_TENTATIVA`, `SUBMETIDO_AO_TRANSPORTE`, `FALHA_DE_TRANSPORTE` e incerto excluem; `SEM_CONTATO` não exclui;
  - Pessoa sem contato que depois informou e-mail entra no Lote B com o novo e-mail;
  - Lote de outra Campanha não influi;
  - contagem "já mobilizados nesta Campanha" na prévia e no Lote
- [ ] T036 [P] [US3] `tests/mobilizacao/test_concorrencia.py` com `@pytest.mark.django_db(transaction=True)` e duas threads (research R14):
  - confirmação simultânea de dois Lotes sobrepostos da mesma Campanha: o segundo exclui os membros do primeiro, sem `IntegrityError` visível;
  - duas ações de envio simultâneas sobre o mesmo Lote: nenhum membro é tentado duas vezes e cada Pessoa recebe no máximo uma mensagem;
  - inserção direta de segundo membro não `SEM_CONTATO` da mesma Pessoa e Campanha: o banco recusa;
  - FR-025: com a confirmação concorrente forçada a colidir (seleção calculada antes do lock, via *monkeypatch*), a restrição recusa e nada é gravado parcialmente; a recusa é por categoria `mobilizacao_concorrente` (409)
- [ ] T037 [US3] Garantir em `trajetoria/mobilizacao/operacoes.py` que `confirmar_lote` trata `IntegrityError` da restrição `membro_uma_abordagem_por_campanha` como recusa por categoria (`mobilizacao_concorrente`, 409), sem gravar parcialmente

- [ ] T066 [P] [US3] `tests/mobilizacao/test_elegibilidade_preservada.py` (ADR 0004; Princípio II; FR-040, FR-041, SC-007; achado C1 do analyze):
  - Pessoa que nunca pertenceu a Lote, com formação na abrangência, inicia e conclui Participação normalmente;
  - membro de Lote (em qualquer situação) tem `situacao_de_entrada` (007) e `admite_participacao` (004) idênticos aos de antes da confirmação e do envio;
  - Pessoa excluída por mobilização anterior continua admitida;
  - depois de confirmar e enviar Lotes, as contagens e os valores de `Pessoa`, `ConclusaoAcademica`, `Campanha`, `Participacao`, `Resposta`, `FormacaoDeclarada` e dos snapshots são idênticos aos de antes;
  - o envio não cria sessão nem Participação

**Checkpoint**: SC-001 verificado.

---

## Phase 6: User Story 6 — Contato importado da fonte acadêmica (P2)

**Goal**: carga de contatos separada da fonte acadêmica, idempotente e isolada.

**Independent Test**: preparar a demonstração e conferir contatos, idempotência e
isolamento com a fonte indisponível.

> Antes de US4 e US5, porque a demonstração precisa de contatos importados para exercitar
> a atualização e o histórico.

- [ ] T038 [P] [US6] `tests/contato/test_carga.py` (contracts/fonte-de-contatos.md):
  - primeira carga grava uma observação com `posicao` 0..n-1 e o mesmo `obtido_em`;
  - mesma lista resulta em `INALTERADO`, sem gravar;
  - lista reordenada grava nova observação;
  - valor novo grava nova observação, preservando a anterior;
  - lista vazia resulta em `SEM_EMAIL`, sem gravar nem apagar;
  - `ContatosIndisponiveis` resulta em `INDISPONIVEL`, sem gravar e com log só do código da fonte;
  - valor inválido é ignorado e contado, sem o valor no log;
  - falha numa Pessoa no preparo não afeta as demais
- [ ] T039 [P] [US6] `tests/contato/test_isolamento.py` (research R14):
  - teste AST: `academico`, `acesso`, `declaracao`, `narrativa`, `video`, `contexto_trajetoria`, `participacao`, `analitico` e `exportacao`, além de `fonte_academica/contrato.py` e `fonte_academica/simulada.py`, não importam `trajetoria.contato`, `trajetoria.mobilizacao` nem `fonte_academica.contatos_da_fonte`;
  - `PessoaEncontrada`, `ConclusaoNaFonte` e `CAMPOS_DE_CONTEXTO` inalterados;
  - com a fonte de contatos levantando `ContatosIndisponiveis`, o preparo conclui e o acesso por CPF e data (018) confirma a Pessoa
- [ ] T040 [P] [US6] Criar o contrato puro `trajetoria/fonte_academica/contatos_da_fonte.py`: `ContatosIndisponiveis` e `FonteDeContatos(Protocol)` com `codigo` e `obter_emails(id_externo_pessoa) -> tuple[str, ...]`, sem Django
- [ ] T041 [US6] Mover o mapa de `trajetoria/comunicacao/contatos.py` para `trajetoria/fonte_academica/cenarios.py` como `EMAILS: dict[str, tuple[str, ...]]`, somente `example.invalid`:
  - SIM-P-0010 com `()`;
  - acrescentar um segundo e-mail a uma Pessoa, por exemplo SIM-P-0004.

  Criar `trajetoria/fonte_academica/contatos_simulados.py` (`ContatosSimulados`, `codigo` = `FonteSimulada.codigo`)
- [ ] T042 [US6] Implementar `carregar_contatos(fonte, pessoa, *, agora) -> ResultadoDaCarga` em `trajetoria/contato/carga.py`, no padrão de `trajetoria/contexto_trajetoria/carga.py` (consulta fora da transação; situações `CARREGADO`, `INALTERADO`, `SEM_EMAIL`, `INDISPONIVEL`)
- [ ] T043 [US6] Em `trajetoria/demonstracao/cenario.py`, acrescentar `_carregar_contatos(fonte_de_contatos)` depois de `_carregar_contextos`, com um *savepoint* por Pessoa simulada e log sem dado pessoal na falha. Aceitar `preparar(fonte_de_contexto=None, fonte_de_contatos=None)`. Atualizar o teste do preparo da demonstração (idempotência ao repetir)

---

## Phase 7: User Story 4 — Egresso atualiza voluntariamente seu e-mail (P2)

**Goal**: página opcional fora do instrumento, anunciada como ação secundária na conclusão
(E7), sem exibir contato guardado.

**Independent Test**: concluir uma Participação, informar e-mail e conferir o registro
`EGRESSO`, o importado preservado e a tela de conclusão com a ação principal intacta.

- [ ] T044 [P] [US4] `tests/contato/test_meu_email.py`:
  - GET e POST exigem sessão de Pessoa (018); sem ela, 303 para `/acesso/`, inclusive a sessão de declarante (019);
  - o GET não contém nenhum endereço guardado (marcadores fictícios ausentes);
  - "Salvar" e "Agora não" com o mesmo peso (mesma classe);
  - o POST válido grava `EGRESSO` com `obtido_em`; o importado permanece;
  - informe igual ao último `EGRESSO` não grava;
  - inválido retorna 422 e não grava;
  - CSRF exigido;
  - a confirmação não repete o endereço;
  - depois de salvar ou recusar, links para `/minha-trajetoria/` (só se `narrativa.consultas.elegivel`) e `/formacoes/`;
  - nenhuma Participação ou Resposta alterada;
  - `Cache-Control` sem cache
- [ ] T045 [P] [US4] `tests/interface/test_conclusao_convite.py` (impacto compartilhado E7):
  - na conclusão ancorada em Conclusão, "Ver minha trajetória no Ifes" é o **primeiro** link de ação e o convite "Quer manter seu e-mail atualizado com o Ifes?" vem depois, com classe secundária;
  - a conclusão declarada (019) não muda e não tem convite;
  - `/minha-trajetoria/`, o card (SVG) e a página e rota do vídeo da 022 não contêm o convite nem endereço, sem renderizar vídeo (sem `precisa_renderizador`);
  - a narrativa é idêntica com e sem contato informado.

  Ajustar `tests/interface/test_interface_conclusao.py:258` (`test_sem_texto_de_encerramento_agradece_uma_vez`), que hoje exige um único link no `<main>`: passa a exigir `["Ver minha trajetória no Ifes", "Quer manter seu e-mail atualizado com o Ifes?"]`, nessa ordem
- [ ] T046 [US4] Implementar `informar_email(pessoa, valor, *, agora=None)` em `trajetoria/contato/operacoes.py` (normaliza, compara com o último `EGRESSO`, grava)
- [ ] T047 [US4] Implementar `trajetoria/contato/views.py` (`meu_email`, GET e POST, `@never_cache`, `pessoa_em_uso`) e `trajetoria/contato/urls.py`. Registrar em `config/urls.py` antes de `trajetoria.interface.urls`. Em `tests/acesso/test_fronteiras.py`, permitir que `contato/views.py` importe só `pessoa_em_uso` de `trajetoria.acesso.sessao`
- [ ] T048 [US4] Criar `trajetoria/contato/templates/contato/meu_email.html` sobre `interface/base.html`:
  - um campo `type="email"` com `<label>` e `autocomplete="email"`;
  - texto de finalidade provisório (DP-2003): "contato do Ifes para pesquisas de acompanhamento de egressos";
  - "seu e-mail não será público";
  - botões de mesmo peso;
  - erro textual associado ao campo;
  - 320 px e 200%
- [ ] T049 [US4] Em `trajetoria/interface/templates/interface/concluida.html`, na ramificação não declarada, manter o parágrafo "Ver minha trajetória no Ifes" e acrescentar **depois** `<p class="secundaria"><a href="/meu-email/">Quer manter seu e-mail atualizado com o Ifes?</a></p>`, com o estilo de menor destaque em `interface/jornada.css` se a classe não existir. Atualizar o docstring de `concluida` em `trajetoria/interface/views.py` ("ação principal leva à Minha trajetória (021 FR-003, revista pela 020); convite secundário de e-mail (020 FR-009)")

---

## Phase 8: User Story 5 — Histórico reproduzível (P2)

**Goal**: o envio usa o contato congelado; o histórico não muda com contatos novos.

**Independent Test**: congelar, informar e-mail novo, enviar e conferir o destino e o
registro.

- [ ] T050 [P] [US5] `tests/mobilizacao/test_reprodutibilidade.py`, com o cenário 04/10, 05/10 e 06/10 da spec:
  - o Lote A envia para `antigo@example.invalid`;
  - o membro continua apontando o registro antigo (origem e `obtido_em`);
  - um Lote B confirmado depois de 05/10, com Pessoa não mobilizada, escolhe `novo@example.invalid`;
  - o detalhe do Lote mostra as mesmas contagens antes e depois;
  - nenhuma tela lista membros, nomes ou endereços
- [ ] T051 [US5] Revisar `enviar_lote` e `views.lote` para garantir que o destino vem exclusivamente de `membro.contato.valor` e que o detalhe só agrega por situação. Ajustar se T050 falhar

---

## Phase 9: User Story 7 — Governança e escopo dos Lotes (P2)

**Goal**: preparar ≠ enviar; CSAEG limitada às suas unidades; revalidação por requisição.

**Independent Test**: todas as rotas de Lote com cada perfil fictício.

- [ ] T052 [P] [US7] `tests/mobilizacao/test_governanca.py`:
  - matriz de rotas de contracts/rotas.md × operadores A (CPAEG), B (CSAEG Vitória) e C (sem vínculo);
  - CSAEG sem filtro de unidade ou com unidade fora do escopo → 403;
  - CSAEG não vê Lote institucional nem de outra unidade (404 ou 403 conforme `campanhas_visiveis`);
  - vínculo desativado entre a confirmação e o envio → recusa no envio;
  - `pode_acompanhar_coleta` sozinho e `pode_gerir_campanha` não concedem Lote;
  - demonstração desligada → 404
- [ ] T053 [US7] Implementar em `trajetoria/mobilizacao/operacoes.py` e `acesso.py`:
  - a exigência de filtro de unidades ⊆ unidades da CSAEG;
  - a gravação de `escopo_institucional` e `escopo_unidades`;
  - a visibilidade do research R10;
  - a checagem separada de `pode_preparar_lote` (prévia e confirmar) e `pode_enviar_lote` (enviar) em cada operação

---

## Phase 10: Polish e substituição da 016

- [ ] T054 [P] `tests/mobilizacao/test_acessibilidade.py` e verificação equivalente em `tests/contato/test_meu_email.py`:
  - sem JavaScript;
  - `fieldset`/`legend`;
  - `label` associado;
  - `role="status"` nos avisos;
  - ordem lógica;
  - nenhuma informação só por cor.

  Seguir o padrão dos testes de acessibilidade da 016 e da 021
- [ ] T055 [P] Estender `tests/acesso/test_vazamento.py`: substituir `simular_comunicacao` por preparar, confirmar e enviar um Lote, mais um POST em `/meu-email/` com endereço marcador. Verificar a ausência do endereço em caplog, requisições, `Location`, cookies, sessão e cache. Manter a varredura do banco excluindo só `ContatoDaPessoa.valor`, exclusão justificada pelo controle C1
- [ ] T056 [P] Estender `tests/analitico/test_analitico_fronteiras.py`, `tests/exportacao/test_exportacao_fronteiras.py` e `tests/acompanhamento/test_acompanhamento_fronteiras.py`:
  - nenhum campo, coluna ou indicador de contato, Lote ou membro;
  - snapshots existentes idênticos antes e depois de confirmar e enviar Lotes (SC-008);
  - o formulário de Campanha da 017 (`nova` e `editar`) continua sem campo de Lote, foco, público, curso ou campus a mobilizar, nem contato (FR-044)
- [ ] T057 [P] Teste AST do controle C1 em `tests/contato/test_controles.py`: fora de `trajetoria/contato/` e `trajetoria/mobilizacao/operacoes.py`, nenhum módulo referencia o atributo `valor` de `ContatoDaPessoa` (research R9)
- [ ] T058 [P] Teste de dependência em `tests/mobilizacao/test_fronteiras.py`:
  - `contato` não importa `mobilizacao`;
  - `comunicacao` não importa `campanha`, `acompanhamento` nem `mobilizacao`;
  - `narrativa`, `video` e `contexto_trajetoria` não importam `contato` nem `mobilizacao`
- [ ] T059 Adaptar `tests/comunicacao/` ao research R12:
  - manter e ajustar `test_convite.py`, `test_convite_mime.py`, `test_seguranca.py`, `test_configuracao.py` e `test_falhas.py` ao transporte por modo;
  - remover `test_publico.py`, `test_publico_http.py`, `test_preview.py`, `test_simulacao.py`, `test_simulacao_http.py`, `test_acesso.py`, `test_origem.py` e `test_demonstracao.py`, cobertos agora por `tests/mobilizacao/`;
  - mover a intenção de `test_contatos.py` para `tests/contato/test_carga.py`
- [ ] T060 Remover a simulação da 016:
  - `trajetoria/comunicacao/views.py`, `consultas.py`, `contatos.py`, `acesso.py` e `operacoes.py`;
  - os templates `preparar.html` e `resultado.html`;
  - as rotas `comunicacao/` e `comunicacao/simular/` de `trajetoria/acompanhamento/urls.py`;
  - a marca `comunicacao` em `tests/acompanhamento/test_acompanhamento_acesso.py`;
  - "comunicacao" das listas de `tests/acesso/test_fronteiras.py`, onde não se aplica mais
- [ ] T061 Remover `pode_simular_comunicacao` de `trajetoria/governanca/regras.py` e das enumerações de `tests/governanca/test_governanca_regras.py`, `tests/exportacao/test_exportacao_fronteiras.py` e `tests/analitico/test_analitico_fronteiras.py`. Remover o link "Comunicação simulada" de `trajetoria/acompanhamento/templates/acompanhamento/campanha.html`
- [ ] T062 Aplicar as notas de revisão:
  - `specs/001-nucleo-academico-fonte-simulada/spec.md` (e-mail admitido pela 020 por capacidade separada);
  - `specs/004-campanhas-populacao-elegivel/spec.md` e `docs/adr/0004-…md` ("Lote especificado e implementado pela 020");
  - `specs/010-governanca-papeis-escopos/spec.md` FR-028 (capacidades de Lote no lugar de simular);
  - `specs/014-polish-jornada-egresso/spec.md` FR-041 e `specs/021-minha-trajetoria-narrativa/spec.md` FR-003 ("única ação" → "ação principal", impacto compartilhado da 020);
  - `specs/016-mobilizacao-comunicacao-simulada/spec.md` (simulação substituída; FR-033 revista; DP-1607 resolvida no limite do Lote);
  - `specs/018-identificacao-acesso-egresso/spec.md` (sessão usada por `/meu-email/`)
- [ ] T063 Atualizar `docs/documentacao/index.html`, distinguindo os três estados:
  - "especificada" (já registrado);
  - "implementada, somente demonstração", com o selo `st-impl` + `st-demo`;
  - "habilitada para uso real", **ainda não**, Gates A e B.

  Atualizar `README.md` se ele listar features e rotas
- [ ] T064 Rodar `uv run ruff check .`, `uv run python manage.py makemigrations --check --dry-run` e `uv run pytest`, e corrigir o que falhar
- [ ] T065 Executar o quickstart (`specs/020-mobilizacao-real-lotes-contatos/quickstart.md` §4) na demonstração com Mailpit e registrar as evidências em `specs/020-mobilizacao-real-lotes-contatos/validacao.md`: capturas de 320 px e desktop da tela de Lotes, do detalhe, de `/meu-email/` e da conclusão com o convite secundário

---

## Dependencies & Execution Order

**Fases**:

```text
Setup (T001–T003) → Foundational (T004–T014)
  → US1 (T015–T023) → US2 (T024–T034) → US3 (T035–T037, T066)
  → US6 (T038–T043) → US4 (T044–T049) → US5 (T050–T051) → US7 (T052–T053)
  → Polish/016 (T054–T065)
```

**Dependências entre histórias**:

- **US2** depende da US1 (Lote confirmado).
- **US3** depende de US1 e US2 (exclusão e envio concorrente).
- **US6** depende só da Foundational e pode ser feita em paralelo a US1–US3.
- **US4** depende da Foundational (model e política). Usa US6 só para a demonstração.
- **US5** depende de US2 e US4.
- **US7** depende de US1 e US2.
- **T060 e T061** só depois de US1–US3: a simulação da 016 sai quando o Lote cobre o seu
  papel.

**Dentro de cada história**: testes → models e operações → views → templates.

## Parallel Opportunities

- Foundational: T004/T005 em paralelo com T006/T007; T008 em paralelo com T010/T011.
- US1: T015, T016 e T017 juntos.
- US2: T024 a T028 juntos; T029 a T031 (comunicação) em paralelo com T032 (mobilização)
  depois da Foundational.
- US6 inteira em paralelo com US1–US3 (apps e arquivos distintos).
- Polish: T054 a T058 juntos.

```text
# Exemplo (US2, testes):
T024 tests/comunicacao/test_transporte.py
T025 tests/comunicacao/test_convite_modos.py
T026 tests/mobilizacao/test_envio.py
T027 tests/mobilizacao/test_retomada.py
T028 tests/mobilizacao/test_link_neutro.py
```

## Implementation Strategy

1. **MVP**: Setup + Foundational + US1 + US2 + US3. A Campanha é mobilizada por Lotes, com
   envio na demonstração, sem duplicidade.
2. **Incremento**: US6, com contatos importados pela fronteira separada.
3. **Incremento**: US4 e US5, com o e-mail do egresso e a reprodutibilidade.
4. **Incremento**: US7, com o refinamento de governança.
5. **Fechamento**: Polish, retirada da 016, notas de revisão, documentação e validação
   manual.

O envio real **não** é habilitado em nenhuma etapa (Gates A e B; DP-2010).
