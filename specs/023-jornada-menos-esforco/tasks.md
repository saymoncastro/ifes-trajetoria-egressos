---

description: "Tasks — Feature 023, jornada de resposta com menos esforço"
---

# Tasks: Jornada de resposta com menos esforço (sem mudar o instrumento)

**Input**: Design documents from `specs/023-jornada-menos-esforco/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: obrigatórios (Const. XXVI; spec FR-037). Tocam autorização (posse da
Participação no envio pendente), associação de respostas (nada gravado sem envio),
condicionais (indicador sobre os percursos) e preservação do instrumento.

**Organization**: uma fase por história de usuário, na ordem de prioridade da spec.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Confirmar a linha de base: `uv run ruff check .`, `uv run python manage.py check`, `uv run python manage.py makemigrations --check --dry-run` e `uv run pytest` verdes antes de qualquer mudança (registrar a duração para comparação)

---

## Phase 2: Foundational

- [X] T002 Acrescentar o campo de leitura `conteudo: ConteudoVersao` a `SituacaoDaJornada` e preenchê-lo em `situacao_da_jornada` em `trajetoria/participacao/consultas.py` (aditivo; nenhum chamador muda)
- [X] T003 [P] Acrescentar à folha da jornada a classe utilitária `.visualmente-oculto` (padrão de texto só para tecnologia assistiva) em `trajetoria/interface/templates/interface/estilo.css`

**Checkpoint**: suíte ainda verde.

---

## Phase 3: User Story 1 — Não perder o que foi marcado quando a sessão expira (P1) 🎯 MVP

**Goal**: aviso de sessão expirada, envio pendente guardado fora da sessão do sujeito e restaurado na Seção depois da nova confirmação (FR-001 a FR-009).

**Independent Test**: com a inatividade em 1 minuto, marcar, esperar, enviar, confirmar e ver a Seção restaurada, sem Resposta gravada até o novo envio; confirmar como outra Pessoa e ver o envio descartado.

### Tests

- [X] T004 [P] [US1] Testes do armazenamento em `tests/acesso/test_pendente.py`: guardar cria um registro separado com validade de 30 min e só os campos `p<n>`, `p<n>-complemento`, `p<n>-remover` (cada valor com "até 2 000 caracteres"); a sessão do navegador guarda só a chave `pendente.envio`; ler depois de 30 min devolve `None` e apaga o registro; um segundo guardar apaga o primeiro; `descartar` apaga o registro; `estabelecer` (018) e `estabelecer_declarante` (019) preservam a chave; `encerrar` apaga o registro; nenhum CPF ou data no registro
- [X] T005 [P] [US1] Testes por requisição em `tests/interface/test_interface_esforco.py` (classe `TestEnvioPendente`), com `TRAJETORIA_SESSAO_INATIVIDADE` ajustado por `settings`/relógio: GET de tela com sessão expirada → `/acesso/?aviso=sessao`; GET sem sessão anterior → `/acesso/`; POST de Seção sem sujeito → nenhuma Resposta gravada, registro guardado, `?aviso=sessao`; a entrada mostra a frase do envio guardado só com registro válido; nova confirmação da mesma Pessoa → `/formacoes/` redireciona para a Participação e daí para a Seção, com os valores marcados, sem erros e com o aviso de recuperação; envio aceito dessa Seção grava pela 005 e apaga o registro; confirmação de outra Pessoa → registro apagado e tela de formações normal; Seção fora do percurso, Participação concluída ou coleta encerrada → registro descartado; "Salvar e sair" pendente não executa a saída; declarante (019) com sessão expirada recupera pela lista
- [X] T006 [P] [US1] Atualizar em `tests/acesso/test_sessao.py` e `tests/declaracao/test_sessao_declarante.py` as asserções de redirecionamento que mudam para `?aviso=sessao` (sem afrouxar as de sessão limpa e revalidação)

### Implementation

- [X] T007 [US1] Criar `trajetoria/acesso/pendente.py`: constante `CHAVE = "pendente.envio"`, `VALIDADE = timedelta(minutes=30)`, `LIMITE_VALOR = 2000`; `guardar(request, participacao_pk, posicao, dados)` (registro novo via `SessionStore` do `SESSION_ENGINE`, `set_expiry(VALIDADE)`, apaga o anterior), `ler(request)` (devolve dataclass `EnvioPendente` ou `None`, apaga se vencido ou ausente), `descartar(request)`; conteúdo opaco, nunca em log
- [X] T008 [US1] Em `trajetoria/acesso/sessao.py`: `pessoa_em_uso` marca `request._sessao_expirada = True` quando descarta sessão existente; `estabelecer` preserva só `pendente.CHAVE` através de `cycle_key` + `clear`; `encerrar` chama `pendente.descartar` antes do `flush`
- [X] T009 [US1] Em `trajetoria/declaracao/sessao.py`: `_revalidar` marca `request._sessao_expirada = True` ao descartar; `estabelecer_declarante` preserva `pendente.CHAVE`
- [X] T010 [US1] Em `trajetoria/acesso/mensagens.py` e `trajetoria/acesso/views.py`: avisos por código fechado (`sessao`, `selo`) em `GET /acesso/`; com `sessao` e envio pendente válido, a segunda frase; textos de [contracts/rotas.md](contracts/rotas.md); template `trajetoria/acesso/templates/acesso/entrada.html` exibe o aviso no bloco de aviso existente
- [X] T011 [US1] Criar `destino_da_entrada(request)` em `trajetoria/acesso/sessao.py` (`/acesso/?aviso=sessao` com `request._sessao_expirada` ou envio pendente guardado nesta requisição; senão `/acesso/`) e usá-lo em `trajetoria/interface/views.py` (`_pessoa`, `inicio`), `trajetoria/declaracao/views_egresso.py` (GET sem declarações), `trajetoria/narrativa/views.py` e `trajetoria/contato/views.py`; no POST de Seção sem sujeito, `interface/views.py` extrai os campos da Seção e chama `pendente.guardar` antes de redirecionar
- [X] T012 [US1] Em `trajetoria/interface/views.py`: reconciliar em `formacoes` (envio de Participação da Pessoa → 302 para `/participacoes/<p>/`; de outro sujeito → descartar); em `participacao`, redirecionar para a Seção do envio pendente válido; em `secao` GET, restaurar com `FormularioDaSecao(..., data=QueryDict)` e `itens(com_erros=False)` mais o aviso de recuperação (`mensagens.RECUPERADO`); descartar quando a Seção sai do percurso, a Participação está concluída ou a coleta encerrada; em `_salvar`, descartar após envio aceito daquela Seção
- [X] T013 [US1] Em `trajetoria/interface/formularios.py`: parâmetro `com_erros=True` em `FormularioDaSecao.itens` (quando `False`, nenhuma lista de erro nos itens); em `trajetoria/interface/mensagens.py`, texto `RECUPERADO`
- [X] T014 [US1] Em `trajetoria/declaracao/views_egresso.py`: depois de `estabelecer_declarante` no POST de `/declaracao/`, descartar envio pendente de Participação fora das declarações do par

**Checkpoint**: US1 testável sozinha (quickstart, passo 2).

---

## Phase 4: User Story 2 — Próxima formação na confirmação (P1)

**Goal**: FR-011, FR-012, FR-028 (posição das ações).

**Independent Test**: Pessoa com duas formações pendentes conclui uma e inicia a outra com um toque.

- [X] T015 [P] [US2] Testes em `tests/interface/test_interface_esforco.py` (classe `TestProximaFormacao`): oferta da primeira pendente na ordem da 007 com botão para `/formacoes/entrar/`; rótulo de iniciar e de retomar; "Ver todas as suas formações" só com mais de uma; nada com ambiguidade, sem pesquisa ou já concluída; declarada inalterada; a ação vem antes de "Ver minha trajetória no Ifes"
- [X] T016 [US2] Em `trajetoria/interface/views.py` (`concluida`): para Participação ancorada em Conclusão, calcular `situacao_de_entrada(pessoa).pendentes` e passar a primeira (forma compacta de `_formacao_apresentada`) e a contagem; textos em `trajetoria/interface/mensagens.py`
- [X] T017 [US2] Em `trajetoria/interface/templates/interface/concluida.html`: ordem de FR-028 (confirmação, encerramento ou agradecimento, próxima formação, Minha trajetória, e-mail, contexto)

---

## Phase 5: User Story 3 — Onde estou e quanto falta (P1)

**Goal**: FR-013 a FR-017.

**Independent Test**: propriedade nos 17 percursos esperados; telas mostram parte e máximo; formações mostram "Você parou em".

- [X] T018 [P] [US3] Testes da função pura em `tests/participacao/test_jornada_maximo.py`: para cada percurso de `PERCURSOS` (`tests/instrumento/formulario_2024_esperado.py`) e cada Seção k do percurso, `maximo_restante(conteudo, secao_k) >= len(percurso_sem_FIM) - k - 1`; valores exatos na baseline (Seção 1 → 8; "Avaliação" → 4; "Estudo" → 2; Seção 13 → 0); determinismo; Versão sintética com pergunta de regra opcional e com Opção sem regra (destino padrão incluído)
- [X] T019 [P] [US3] Testes de tela em `tests/interface/test_interface_esforco.py` (classe `TestProgresso`): "Parte 1 · faltam no máximo 8" na Seção 1; "última parte" na Seção 13; aba e revisão com "Parte X" para Seção sem título e nunca "Seção 13"; "Parte anterior salva." só com Resposta gravada na Seção anterior; formações com "Você parou em «Informações Pessoais»" e "Falta só concluir"; lista de formações informadas com a mesma indicação
- [X] T020 [US3] Implementar `maximo_restante(conteudo, secao_id) -> int` em `trajetoria/participacao/percurso.py` conforme [research.md](research.md) R8 (arestas: destinos de Opções com regra; destino padrão quando não há pergunta com regra, ela é opcional ou alguma Opção não tem regra; recursão com memória; exportar em `__all__`)
- [X] T021 [US3] Em `trajetoria/interface/apresentacao.py`: `rotulo_da_secao(secao, parte)` (título ou "Parte X") e `onde_parou(jornada)` (texto de FR-017 a partir de `secao_atual`, `finalizada`, `passagens` e `maximo_restante`)
- [X] T022 [US3] Em `trajetoria/interface/views.py`: passar `parte`, `maximo` e o rótulo da Seção a `secao.html`; usar "Parte X" na lista de `concluir_view`; em `_salvar`, redirecionar com `?aviso=anterior` para a Seção seguinte só se a Seção enviada tem Resposta gravada; em `formacoes`, acrescentar `onde_parou` às formações em andamento (com `situacao_da_jornada`, ignorando estrutura não suportada); `mensagens.AVISOS` ganha `anterior`
- [X] T023 [US3] Em `trajetoria/interface/templates/interface/secao.html` e `formacoes.html` / `formacao.html`: linha da parte (contrato de telas), título da aba com o rótulo, "Você parou em" por formação
- [X] T024 [US3] Em `trajetoria/declaracao/views_egresso.py` e `trajetoria/declaracao/templates/declaracao/egresso.html`: "Você parou em" por item em andamento da lista

---

## Phase 6: User Story 4 — Complemento sem erro evitável (P1)

**Goal**: FR-018 a FR-020.

**Independent Test**: campo oculto até marcar; erro com campo visível e nova mensagem; nada gravado.

- [X] T025 [P] [US4] Testes em `tests/interface/test_interface_esforco.py` (classe `TestComplemento`): a Opção que admite complemento tem `opcao-com-complemento`; o campo tem `sempre-visivel` só quando tem valor; rótulo "Descreva o que se encaixa em «Outro»"; envio com complemento e Opção desmarcada → recusa, nada gravado, mensagem nova, campo com o texto; a regra `@supports selector(:has(*))` está em `jornada.css`; a prévia do editor não recebe a regra de ocultação
- [X] T026 [US4] Em `trajetoria/interface/formularios.py`: opções com flag `complemento`; `item.complemento` com `sempre_visivel` (valor não vazio) e novo rótulo; em `trajetoria/interface/mensagens.py`, `COMPLEMENTO_SEM_OPCAO` com o texto de FR-020
- [X] T027 [US4] Em `trajetoria/interface/templates/interface/perguntas/escolha_unica.html`, `escolha_multipla.html` e `_complemento_remover.html`: classes `opcao-com-complemento` (também na `<option>`) e `sempre-visivel`
- [X] T028 [US4] Em `trajetoria/interface/templates/interface/jornada.css`: regra condicional de [research.md](research.md) R6
- [X] T029 [US4] Atualizar `tests/interface/test_interface_secao.py` e `tests/editor/test_editor_previa.py` para o novo rótulo do complemento

---

## Phase 7: User Story 5 — Não confirmação em dois passos (P2)

**Goal**: FR-021, FR-022.

**Independent Test**: telas de `NAO_CONFIRMADA` iguais entre causas, com dois passos; sem "Continuar para suas formações" após falha.

- [X] T030 [P] [US5] Testes em `tests/interface/test_interface_esforco.py` (classe `TestNaoConfirmada`): lista numerada com "Conferir os dados" antes de "Informar minha formação"; conteúdo visível igual entre as cinco causas da 018 (normalizando o token CSRF e o selo); com sessão anterior de outra Pessoa, a tentativa falha sem "Continuar para suas formações"
- [X] T031 [US5] Em `trajetoria/acesso/templates/acesso/entrada.html`: dois passos de [contracts/telas.md](contracts/telas.md); `Continuar para suas formações` só sem aviso de falha; manter o formulário de declaração (`/declaracao/`, selo) e a ação `#cpf`
- [X] T032 [US5] Atualizar asserções afetadas em `tests/acesso/test_rotas.py`, `tests/acesso/test_acessibilidade.py` e `tests/declaracao/test_rotas_egresso.py`, se houver

---

## Phase 8: User Story 6 — Menos rolagem e ruído nas Seções (P2)

**Goal**: FR-010, FR-023 a FR-026.

**Independent Test**: marcação de obrigatoriedade, lado a lado, `details`, botão do meio e rodapé conferidos por requisição.

- [X] T033 [P] [US6] Testes em `tests/interface/test_interface_esforco.py` (classe `TestDensidade`): "(opcional)" só nas 4 opcionais da baseline e " (obrigatória)" dentro de `.visualmente-oculto` nas demais; `opcoes-lado-a-lado` nas escolhas únicas de 2 Opções com até 15 caracteres e só nelas; `<details>` "Sobre esta pesquisa" na Seção 1 com o texto de abertura e o texto da Seção fora do `details`; botão do meio "Salvar e sair" (`name=depois value=sair`) depois da Pergunta ⌈n/2⌉ só em Seções com mais de 8 Perguntas, com o botão desabilitado oculto ainda como primeiro envio do formulário; "Sair sem salvar esta seção" ausente sem erro e presente com erro de forma; o botão do meio grava e sai como o do rodapé
- [X] T034 [US6] Em `trajetoria/interface/templates/interface/perguntas/_enunciado.html`: marcação de FR-023
- [X] T035 [US6] Em `trajetoria/interface/formularios.py` e `trajetoria/interface/templates/interface/perguntas/escolha_unica.html`: `item.lado_a_lado` (rádio, 2 Opções, cada uma com "até 15 caracteres") e a classe `opcoes-lado-a-lado`; CSS em `trajetoria/interface/templates/interface/estilo.css` ([research.md](research.md) R7, alvo ≥ 44 px)
- [X] T036 [US6] Em `trajetoria/interface/templates/interface/secao.html`: `<details class="abertura"><summary>Sobre esta pesquisa</summary>`; bloco do meio (FR-010; ⌈n/2⌉ calculado na view e passado como `meio`); rodapé de FR-026; estilos mínimos em `jornada.css`
- [X] T037 [US6] Atualizar `tests/interface/test_interface_rodape.py`, `test_interface_secao.py`, `test_interface_acessibilidade.py` e demais testes que dependiam de "(obrigatória)" visível, da abertura aberta ou de "Sair sem salvar" em toda Seção, citando a revisão (spec, "Requisitos revisados")

---

## Phase 9: User Story 7 — Concluir e confirmação sem rolar (P3)

**Goal**: FR-027 (a confirmação, FR-028, já está em US2).

- [X] T038 [P] [US7] Testes em `tests/interface/test_interface_esforco.py` (classe `TestConclusao`): ordem título → aviso de irreversibilidade → botão → lista → contexto; texto "volte a uma das partes"
- [X] T039 [US7] Em `trajetoria/interface/templates/interface/conclusao.html`: nova ordem; atualizar `tests/interface/test_interface_conclusao.py`

---

## Phase 10: User Story 8 — Entrada e declaração com menos atrito (P3)

**Goal**: FR-029 a FR-032.

- [X] T040 [P] [US8] Testes em `tests/interface/test_interface_esforco.py` (classe `TestEntradaDeclaracao`): dica da data; `?aviso=selo` com selo vencido em `/declaracao/`, `/declaracao/nova/` e `/declaracao/comecar/`; `autocomplete="name"`; nível em rádios dentro de `fieldset`; confirmação com nível, "Começar" primário, "Corrigir" devolvendo o formulário preenchido sem nova confirmação
- [X] T041 [US8] Em `trajetoria/acesso/templates/acesso/entrada.html`: dica da data (FR-029)
- [X] T042 [US8] Em `trajetoria/declaracao/views_egresso.py`: `SeloInvalido` → `/acesso/?aviso=selo`; `nova` com `corrigir=1` devolve `FormacaoForm(request.POST)`; a confirmação recebe o selo de trânsito para "Corrigir"
- [X] T043 [US8] Em `trajetoria/declaracao/formularios.py`: `autocomplete="name"` no nome; `nivel` com `RadioSelect`; em `trajetoria/declaracao/templates/declaracao/egresso.html`: `fieldset`/`legend` para rádios, confirmação com nível, "Começar" (`primario`), "Corrigir" (`secundario`), "Sair" com menor ênfase
- [X] T044 [US8] Atualizar `tests/declaracao/test_rotas_egresso.py` e `tests/declaracao/test_acessibilidade.py` para o redirecionamento com aviso e o novo formulário

---

## Phase 11: Polish & Cross-Cutting

- [X] T045 [P] Teste de fronteira em `tests/interface/test_interface_esforco.py` (classe `TestFronteiras`): o instrumento materializado e os 17 percursos não mudam; nenhuma migração nova; nenhum `<script>` nas telas da jornada; nenhum `localStorage`/`sessionStorage`
- [X] T046 Rodar as verificações do CI (`ruff`, `check`, `makemigrations --check`, `pytest`) e corrigir
- [X] T047 Validação visual a 375×812 (quickstart, passos 2 a 6): medir alturas do cenário A, registrar capturas em `specs/023-jornada-menos-esforco/evidencias/` e o resultado de SC-005 e SC-006 em `specs/023-jornada-menos-esforco/validacao.md`
- [X] T048 Notas de revisão nas specs revisadas: `specs/008-interface-navegavel-pesquisa/spec.md`, `specs/014-polish-jornada-egresso/spec.md`, `specs/018-identificacao-acesso-egresso/spec.md`, `specs/019-formacao-declarada-validacao/spec.md` (seção "Nota de revisão pela Feature 023")
- [X] T049 Atualizar `docs/documentacao/` e `docs/desenvolvimento/ambiente-local.md` só se citarem textos ou comportamentos alterados (verificar com grep)

---

## Dependencies & Execution Order

- Setup (T001) → Foundational (T002, T003) → histórias.
- US1 depende só da fundação. US3 depende de T002. US2 e US7 tocam `concluida.html`/`conclusao.html` e devem ser feitas em sequência (US2 antes de US7). US4 e US6 tocam os templates de Pergunta e `formularios.py`: fazer US4 antes de US6. US5 e US8 tocam `entrada.html`: US1 (T010) → US5 → US8.
- Polish depois de todas.

### Parallel Opportunities

- Os testes de cada história ([P]) podem ser escritos em paralelo com a implementação de outra história.
- T004, T005 e T006 em paralelo; T018 e T019 em paralelo; T003 com T002.

## Implementation Strategy

**MVP**: Fases 1 a 3 (US1). Elimina o único P0 que a interface resolve por inteiro.
Depois, US2 a US4 (P1), US5 e US6 (P2), US7 e US8 (P3) e o polimento. Cada fase termina com
a suíte verde.
