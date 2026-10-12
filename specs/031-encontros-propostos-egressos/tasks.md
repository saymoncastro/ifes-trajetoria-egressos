# Tasks: Encontros propostos por egressos

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/rotas.md),
[quickstart.md](quickstart.md), [protótipo](prototipo/index.html)

**Tests**: obrigatórios, pelo Princípio XXVI. A feature mexe em autorização, em dado pessoal
exibido a terceiros e na fronteira da camada. Cada teste é escrito e falha antes da
implementação correspondente.

**Formato**: `[ID] [P?] [História] Descrição`. `[P]`: arquivos diferentes, sem dependência
pendente. As histórias são as da spec: US1 propor, US2 moderar, US3 descobrir e confirmar,
US4 acompanhar e cancelar, US5 compartilhar e denunciar, US6 vazios e encerrados.

## Phase 0: Portão

> **Revisão 16 (2026-10-11).** O portão foi revisto: o incremento 1 foi autorizado **antes** dos
> checkpoints, só na demonstração. Marcação abaixo: `[x]` feito no incremento 1;
> `[ ]` com **(incremento 2)** fica para depois. Tarefas parciais dizem o que ficou.

- [x] T001 Confirmar no roadmap (nova revisão) e no Status da spec `specs/031-encontros-propostos-egressos/spec.md` a autorização de implementação. Ela exige: Checkpoint 1 e Checkpoint 2, com o bloco Comunidade, aplicados e lidos conforme os protocolos; escolha do solicitante entre 031 e 030 registrada; abrangência "só demonstração". **Sem isso, nenhuma tarefa abaixo começa.** Registrar o que os checkpoints mudaram na spec, nas hipóteses H-3101 a H-3108 ou no protótipo, e atualizar estas tasks antes de seguir. — **Revisto na revisão 16:** o incremento 1 foi autorizado antes dos checkpoints, que continuam NÃO APLICADOS; o que eles mudarem entra no incremento 2 ou em ajustes.

## Phase 1: Setup

- [x] T002 Criar o subpacote `trajetoria/portal/encontros/` (`__init__.py`) e a pasta de templates `trajetoria/portal/templates/portal/encontros/`, no molde de `portal/contribuicao/` (research R1).
- [x] T003 [P] Criar o construtor de cenários de teste `tests/portal/construcao_encontros.py`, com encontros, confirmações e denúncias em cada situação do data-model, e o relógio passado por parâmetro (plan, "Riscos").

## Phase 2: Foundational

**Objetivo:** modelos, regras puras, governança e textos que todas as histórias usam.

- [x] T004 [P] Testes sem banco em `tests/portal/test_encontros_regras.py`:
  - `situacao(encontro, agora)` nas nove situações e na ordem do data-model;
  - "ativo" (Em análise, Em revisão, Publicado);
  - limites: título até 90, descrição até 400, nome até 40, complemento até 300; mesmo dia; término depois do início; até 3 h; data entre 2 e 90 dias depois do envio;
  - mesmo domínio do link (R7);
  - `o_que_ver` para cada situação × quem (FR-024a, research R10);
  - quem vê o link (FR-021). **Incremento 1:** sem `mesmo_dominio`, que serve à correção do link (incremento 2).
- [ ] T005 [P] Testes sem banco em `tests/portal/test_encontros_calendario.py`, conforme [contracts/calendario.md](contracts/calendario.md):
  - CRLF e dobra em 75 octetos;
  - `UID` estável; `SEQUENCE` 0, +1 com data alterada, +1 com cancelamento; `STATUS:CANCELLED`;
  - `DTSTART` e `DTEND` em UTC;
  - `URL` da página;
  - ausência do link, do nome de apresentação e da origem. **(incremento 2)**
- [x] T006 Modelos `Encontro`, `Confirmacao` e `Denuncia` em `trajetoria/portal/models.py` e migração aditiva `trajetoria/portal/migrations/0003_encontros.py`, conforme [data-model.md](data-model.md). Restrições no banco:
  - tamanhos 1–90, 1–400, 1–40 e até 300;
  - critérios de público `NULL` ou não vazios, sem `""`, como a Oportunidade;
  - pares momento/operador coerentes;
  - motivo só com recusa ou retirada; complemento obrigatório com `outro`;
  - FK interna `Confirmacao.encontro` e `Denuncia.encontro` com `PROTECT`;
  - `publicado_por_escopo` (`institucional` ou a unidade) presente sempre que houver `publicado_em`;
  - uma confirmação ativa por (`encontro`, `pessoa_id`) com `cancelada_em IS NULL`;
  - uma denúncia por (`encontro`, `pessoa_id`). **Incremento 1:** Encontro e Confirmação, sem os campos de nova análise e correção (`primeira_publicacao_em`, `reenviado_em`, `campos_alterados`, `data_alterada_em`, `link_atualizado_em`) e sem a Denúncia, que ficam para o incremento 2 (XXII).
- [x] T007 Revisar `tests/portal/test_fronteiras.py` (`test_portal_dois_modelos_sem_fk_para_o_nucleo`): quatro modelos no `portal`, nenhuma chave cujo destino esteja fora do app, migrações só aditivas (research R2). Nota de revisão no docstring. **Incremento 1:** quatro modelos (Oportunidade, Manifestação, Encontro, Confirmação); a única FK interna é `Confirmacao.encontro`.
- [x] T008 [P] `trajetoria/portal/encontros/regras.py`: `situacao`, `ativo`, validação de campos e limites, `mesmo_dominio`, `o_que_ver` e `mostra_link`. Reaproveita `oportunidades.regras.endereco_invalido` e `origem_do_site`. Até T004 passar. **Incremento 1:** sem `mesmo_dominio`.
- [ ] T009 [P] `trajetoria/portal/encontros/calendario.py`, até T005 passar (research R11). **(incremento 2)**
- [x] T010 [P] `trajetoria/portal/encontros/governanca.py`, com `pode_moderar_encontros`, `responsavel(publico_unidades)` e `modera(escopo, encontro)`, sobre `escopo_de_acompanhamento` (research R8; H-3102). Testes no mesmo arquivo de T004:
  - unidade única → CSAEG daquela unidade;
  - demais casos → institucional;
  - CPAEG modera todos;
  - CSAEG de outra unidade não modera.
- [x] T011 [P] `trajetoria/portal/encontros/mensagens.py`, com textos provisórios (DP-801):
  - `VERSAO_DO_TERMO` e `VERSAO_DA_CIENCIA`;
  - motivos de recusa e de retirada (H-3104) e de denúncia (H-3107);
  - textos do protótipo.
  
  Um teste de vocabulário, em `tests/portal/test_encontros_regras.py`, verifica que nenhum texto afirma inscrição ou presença e que não há "turma", "geração" nem "conectad". **Incremento 1:** sem motivos de denúncia (incremento 2).

## Phase 3: US1 — Propor um encontro (P1) 🎯

**Objetivo:** Maria propõe um encontro e ele fica "Em análise", invisível aos outros.
**Teste independente:** spec, US1.

- [x] T012 [US1] Testes de gravação em `tests/portal/test_encontros_propor.py` (parte "operações"):
  - Conclusão de outra Pessoa recusada; Formação Declarada não oferecida;
  - origem copiada (R3); versão do termo e momento gravados;
  - limite de 3 ativos, inclusive com dois envios simultâneos (R9);
  - editar em análise. **Incremento 1:** sem `editar` (incremento 2). A corrida do limite é coberta pela trava na Pessoa; o teste de dois envios simultâneos fica para o incremento 2.
- [x] T013 [US1] `trajetoria/portal/encontros/operacoes.py`: `propor` e `editar`, com trava e revalidação, como único caminho de escrita. Até T012 passar. **Incremento 1:** só `propor`; `editar` no incremento 2.
- [x] T014 [US1] Testes de requisição em `tests/portal/test_encontros_propor.py` (parte "fluxo"):
  - formulário com público por unidades, níveis e cursos, a partir dos valores registrados;
  - erros por campo, com o valor preservado e o foco no resumo, sem gravar;
  - "Confira e envie" com quem analisa e o termo;
  - resultado "Em análise";
  - quarta proposta recusada com mensagem;
  - sem Conclusão: 404.
- [x] T015 [US1] Implementar:
  - `trajetoria/portal/encontros/formularios.py`;
  - `trajetoria/portal/encontros/views_organizador.py` (`/encontros/propor/`, `/encontros/propor/confirmar/`, `/encontros/<id>/editar/`);
  - os templates `propor.html`, `confirmar.html` e `em_analise.html` em `trajetoria/portal/templates/portal/encontros/`, conforme os protótipos o1 a o4;
  - as rotas em `trajetoria/portal/urls.py`. **Incremento 1:** sem `/encontros/<id>/editar/`. A gravação é em `/encontros/propor/enviar/`.

## Phase 4: US2 — Moderar antes da publicação (P1)

**Objetivo:** a moderação do escopo publica, recusa ou retira, sempre com motivo.
**Teste independente:** spec, US2.

- [x] T016 [US2] Testes em `tests/portal/test_encontros_moderacao.py`:
  - escopo: CSAEG na unidade única, CPAEG em todos, CSAEG de outra unidade recebe 404, sem competência recebe a recusa;
  - publicar, recusar e retirar com operador opaco e motivo; complemento obrigatório em `outro`;
  - `publicado_por_escopo` gravado (CPAEG num encontro de unidade única grava `institucional`), e a página diz quem moderou a partir dele (FR-024);
  - conflito na decisão simultânea, sem gravar (R8);
  - a análise não mostra CPF, data de nascimento, contato, quem confirmou nem quem denunciou;
  - a análise mostra a quantidade de confirmações e as denúncias (FR-018). **Incremento 1:** sem as denúncias na análise.
- [x] T017 [US2] Implementar:
  - `publicar`, `recusar` e `retirar` em `trajetoria/portal/encontros/operacoes.py`;
  - `trajetoria/portal/encontros/views_moderacao.py` (`/curadoria/encontros/`, `/curadoria/encontros/<id>/`, `.../recusar/`, `.../retirar/`), com a base e a escolha de operador da curadoria da 025;
  - os templates conforme os protótipos m1 a m5.

## Phase 5: US3 — Descobrir e confirmar (P1)

**Objetivo:** Diego encontra o encontro pela formação, confirma, vê o link e baixa o `.ics`.
**Teste independente:** spec, US3.

- [x] T018 [US3] Testes em `tests/portal/test_encontros_participante.py`:
  - pertinência por curso, nível e unidade, e aberto a todos, com a explicação (R6);
  - fora do público não aparece na lista;
  - confirmar com a versão da ciência; uma confirmação ativa;
  - cancelar e confirmar de novo;
  - o organizador não confirma o próprio encontro;
  - não confirma fora de Publicado;
  - `.ics` só para quem confirmou e para o organizador. **Incremento 1:** sem o `.ics` (incremento 2).
- [x] T019 [US3] Testes em `tests/portal/test_encontros_pagina.py`:
  - conteúdo por situação × quem (FR-024a);
  - **o link ausente do HTML** de quem não confirmou, sem sessão, em revisão, depois do término, cancelado ou retirado (SC-002);
  - página neutra sem sessão (FR-022).
- [x] T020 [US3] Implementar:
  - `trajetoria/portal/encontros/consultas.py` (pertinentes da Pessoa, a partir de `oportunidades.pertinencia.satisfaz` e `explicacao`; itens A da categoria Eventos);
  - `confirmar` e `cancelar_participacao` em `operacoes.py`;
  - `trajetoria/portal/encontros/views_egresso.py` (`/encontros/`, `/encontros/<id>/`, `.../participar/`, `.../cancelar-participacao/`, `.../calendario.ics`);
  - os templates conforme os protótipos p2 a p5 e p7.
  
  O contexto do template recebe o link só por `mostra_link` (plan, "Riscos"). **Incremento 1:** sem `.../calendario.ics`.
- [x] T021 [US3] Testes revisados em `tests/portal/test_inicio_convergencia.py` e `tests/portal/test_navegacao.py`:
  - seção "Ninguém se forma sozinho." com F e A e rótulos distintos; ausente sem nenhum;
  - convite por último;
  - "Encontros" na navegação com Conclusão, como item atual em `/encontros/`;
  - cinco itens sem rolagem a 320 px com fonte a 200%. **Incremento 1:** só a navegação; a seção do Início fica para o incremento 2.
- [x] T022 [US3] Implementar:
  - `inicio._encontro` com o par F e A, em `trajetoria/portal/inicio.py`, e o template do Início (protótipo p1);
  - `ENCONTROS_TEXTO` revisto em `trajetoria/portal/mensagens.py`;
  - o item "Encontros" em `trajetoria/portal/contexto.py` (research R13). **Incremento 1:** só o item "Encontros" em `contexto.py`; `inicio._encontro` e `ENCONTROS_TEXTO` ficam para o incremento 2.

## Phase 6: US4 — Acompanhar e cancelar como organizador (P2)

**Objetivo:** Maria vê a quantidade de confirmações, corrige ou altera o encontro e pode cancelar.
**Teste independente:** spec, US4.

- [x] T023 [US4] Testes em `tests/portal/test_encontros_organizador.py`:
  - "Seus encontros" com todas as situações, contagem só numérica e motivo da recusa;
  - correção de data com aviso e confirmações mantidas;
  - link no mesmo domínio vale na hora;
  - link de outro domínio vira nova análise;
  - alteração substancial: sai das listas, esconde o link, mantém as confirmações, grava `campos_alterados`;
  - nova análise na moderação mostra os campos alterados; recusar a alteração retira;
  - cancelar antes do início;
  - nada disso depois do início. **Incremento 1:** "Seus encontros" e cancelamento; correções, alteração e nova análise ficam para o incremento 2.
- [x] T024 [US4] Implementar:
  - `corrigir_data`, `corrigir_link`, `alterar` e `cancelar` em `operacoes.py`;
  - as views `/encontros/seus/`, `.../alterar-data/`, `.../corrigir-link/`, `.../alterar/` e `.../cancelar/` em `views_organizador.py`;
  - a nova análise em `views_moderacao.py`;
  - os templates conforme os protótipos o5 a o9, o11, o12, m6 e p8. **Incremento 1:** só `cancelar` e `/encontros/seus/`; o resto no incremento 2.

## Phase 7: US5 — Compartilhar e denunciar (P2)

**Objetivo:** o endereço recebido leva ao encontro depois da identificação, e qualquer egresso pode denunciar.
**Teste independente:** spec, US5.

- [ ] T025 [US5] Testes em `tests/portal/test_entradas.py` (revisado) e `tests/portal/test_encontros_pagina.py`:
  - `/entrar/?encontro=<id>` com UUID existente leva ao encontro;
  - URL externa, caminho arbitrário, UUID inexistente ou valor inválido levam ao Início (R12);
  - `destinos.sem_pessoa` em `/encontros/<id>/`;
  - fora do público abre e permite confirmar (H-3108). **(incremento 2)** O retorno pelo endereço compartilhado. O caso "fora do público abre e confirma" já está testado no incremento 1.
- [ ] T026 [US5] Implementar o destino por lista fechada em `trajetoria/portal/views.py` (`entrar`) e `trajetoria/portal/destinos.py`, sem mudar `acesso.views.identificar`; a página neutra (protótipo p6) e o aviso "Você recebeu este endereço" (p7). **(incremento 2)** A página neutra (p6) e o aviso "Você recebeu este endereço" (p7) já existem no incremento 1.
- [ ] T027 [US5] Testes de denúncia em `tests/portal/test_encontros_participante.py`:
  - uma por pessoa; em Publicado, qualquer pessoa com Conclusão; em Encerrado, só quem tinha confirmação ativa no término; o organizador não denuncia;
  - a moderação vê motivo, complemento e data, sem quem;
  - o organizador não vê; "Você denunciou…". **(incremento 2)**
- [ ] T028 [US5] Implementar `denunciar` em `operacoes.py`, `/encontros/<id>/denunciar/` em `views_egresso.py` e as denúncias na retirada (protótipos p12, p13 e m4). **(incremento 2)**

## Phase 8: US6 — Estados vazios e encerrados (P2)

**Objetivo:** nenhuma tela finge conteúdo; os encontros encerrados e cancelados mostram só o que a regra permite.
**Teste independente:** spec, US6.

- [x] T029 [US6] Testes em `tests/portal/test_encontros_pagina.py` e `tests/portal/test_encontros_organizador.py`:
  - Encontros vazia com "Propor um encontro";
  - "Seus encontros" vazia;
  - fila da moderação vazia;
  - encerrado sem link, confirmação ou cancelamento;
  - não analisado a tempo nunca publicado;
  - alteração não analisada a tempo. **Incremento 1:** sem "alteração não analisada a tempo", que depende da nova análise.
- [x] T030 [US6] Templates e textos dos estados vazios e encerrados, conforme os protótipos p9 a p11, o10 e m5.
- [x] T031 [P] [US6] `trajetoria/portal/encontros/demonstracao.py`: encontros fictícios pelo sinal `cenario_preparado` (research R15), com as personas e os textos do protótipo. O encontro de unidade única é de **Vitória**, para o operador fictício B. Incluir teste de idempotência do preparo.

## Phase 9: Fronteira, revisões e entrega

- [x] T032 Testes em `tests/portal/test_encontros_fronteira.py` e revisões:
  - núcleo sem menção à camada; `ContatoDaPessoa` inalterado;
  - analítico, exportações e mobilização sem os três fatos;
  - `test_portal_nao_grava` revisado com as telas da 031;
  - Portal desligado sem as rotas (`tests/portal/test_desabilitado.py`);
  - logs das operações sem `pessoa_id`, link da reunião nem complemento de denúncia (`caplog`; Constituição XVI).
- [x] T033 Notas de revisão, sem apagar o histórico (spec, "Requisitos revisados"):
  - ADR 0009, decisão 7 ("comunidade");
  - 024 FR-006, FR-021, FR-022, FR-023 e FR-029;
  - 025 FR-037;
  - 029 FR-007;
  - 032 FR-008, FR-011 e SC-005. **Incremento 1:** notas na 024 e na 032 (navegação). A ADR 0009 ("comunidade") e a 029 não mudam: o incremento 1 não usa a palavra nem muda a página pública.
- [x] T034 Verificações do CI: `uv run ruff check .`, `uv run python manage.py check`, `uv run python manage.py makemigrations --check --dry-run`, `uv run pytest`.
- [x] T035 Capturas e medidas reais (egresso a 375×812 e 1440×900; moderação a 1280×720), lado a lado com o protótipo, e roteiro manual com teclado nos cenários 2, 5, 7 e 10 do [quickstart](quickstart.md). **Incremento 1:** medidas e capturas em `evidencias/`. O roteiro manual com teclado **não foi executado** (pendente, `validacao.md`).
- [x] T036 `specs/031-encontros-propostos-egressos/validacao.md`, com resultados, número de testes, desvios do protótipo e decisões pendentes (D8, D9, D10, DP-1808, DP-3102, DP-801).

## Dependências

- **T001 antes de tudo.**
- **Setup e base:**
  - T002 → T006 → T007;
  - T003, T004, T005 e T011 em paralelo com T006;
  - T004 → T008; T005 → T009; T010 depois de T004.
- **US1:** T006, T008, T010 e T011 → T012 → T013 → T014 → T015.
- **US2:** depois de T013, porque precisa de encontros propostos.
- **US3:** depois de T017, porque precisa de encontros publicados.
- **US4, US5 e US6:** depois de T020. Podem correr em paralelo entre si, com cuidado em
  `operacoes.py`, que é compartilhado.
- **Phase 9:** T032 e T033 a partir de T020; T034 a T036 por último.

## Execução em paralelo (exemplos)

- **Base:** T004, T005, T011 e T003 juntos. Depois, T008, T009 e T010 juntos.
- **US3:** T018 e T019 (testes em arquivos distintos) juntos; depois T020. T021 e T022 podem
  correr ao lado de T020.
- **Pós-US3:** T025 a T028 (US5) e T029 a T031 (US6) em paralelo com T023 e T024 (US4), cada
  história com seus testes primeiro.

## Estratégia de implementação

1. **MVP (US1 + US2 + US3):** propor, moderar, descobrir, confirmar e ver o link. É o mínimo
   que demonstra a hipótese F, e o percurso curto do Checkpoint 2 já usa essas telas.
2. **Incremento:** US4 (correções, alteração e cancelamento), US5 (endereço compartilhado e
   denúncia) e US6 (vazios e encerrados), nessa ordem ou em paralelo.
3. **Entrega:** Phase 9 completa, com a `validacao.md`, antes do PR de implementação.
