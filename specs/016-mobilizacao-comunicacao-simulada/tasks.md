# Tasks: Mobilização e comunicação simulada da pesquisa

**Input**: `specs/016-mobilizacao-comunicacao-simulada/` — [spec](spec.md), [plan](plan.md),
[research](research.md), [data-model](data-model.md), [contratos](contracts/operacao.md) e
[quickstart](quickstart.md), com as quatro precisões aprovadas em 2026-10-03.
**Branch/baseline**: `016-mobilizacao-comunicacao-simulada`, main `0c911b5` (015/PR #24).
**Estado**: implementação autorizada e concluída em 2026-10-03; **50/50 tasks verificadas**.
Evidências de testes e demonstração registradas em [quickstart.md](quickstart.md).

## Format e convenções

`- [ ] TNNN [P?] [USn?] descrição com caminho`. IDs contínuos; [P] somente arquivos distintos,
sem dependência entre as tasks do mesmo lote liberado. Caminhos relativos à raiz do repo.
Setup/fundação/final sem história; demais tasks possuem US1–US4 conforme spec.
A nova app é pacote de aplicação com templates, sem `models.py` ou migrations.

**TDD obrigatório:** escrever e executar testes antes do bloco funcional correspondente;
confirmar falha pela ausência/comportamento da 016, sem falha causada por ambiente/fixture
quebrada. Não usar xfail/skip para atravessar gate. Depois implementar, executar os mesmos
testes e confirmar verde. Helpers/fixtures de setup não implementam comportamento da feature.
Testes novos usam locmem + modo demo + flag interna de teste; nenhum SMTP/Mailpit/rede.

## Fase 1 — Setup mínimo (2 tasks)

Meta: aproveitar stack atual e preparar suporte de teste, sem nova infraestrutura.

- [X] T001 Preparar fixtures locais e helper de snapshot completo (campos, relações, momentos e opções de Resposta) em `tests/comunicacao/conftest.py`, usando fonte/operadores canônicos e override de locmem; não criar registros de comunicação nem alterar fixtures globais.
- [X] T002 Criar somente pacote `trajetoria/comunicacao/__init__.py` e registrar app para templates em `config/settings.py`; preservar dependências, middleware e baseline 015, sem modelos/migrations/configuração produtiva.

Checkpoint: fixtures utilizáveis; não existe capacidade, renderer, consulta ou transporte novo.

## Fase 2 — Fundação: autorização/escopo 010/011 (5 tasks)

Meta: capacidade explícita e fronteira de acesso reutilizável antes de qualquer tela.
Independente: requests sintéticos/adaptador fictício, sem transporte ou rotas da 016.

### Testes primeiro

- [X] T003 [P] Escrever e confirmar RED da capacidade fixa em `tests/governanca/test_governanca_regras.py`: CPAEG/CSAEG ativos, inativos, sem vínculo, papel indevido, vínculo misto; não derivar comunicação de capacidade editorial/técnica.
- [X] T004 [P] Escrever e confirmar RED dos helpers de acesso em `tests/comunicacao/test_acesso.py`: modo desligado, operador ausente/fictício inválido, cookie somente de Pessoa, destino fechado acompanhamento, capacidade, escopo exato, NULL, várias CSAEG e revogação; nenhuma exposição/transporte antes de recusa.

### Implementação posterior

- [X] T005 Implementar/exportar `pode_simular_comunicacao` em `trajetoria/governanca/regras.py`, regra pura nomeada CPAEG/CSAEG ativa, sem nova permissão/modelo ou competência real; depende de T003 RED.
- [X] T006 Implementar helpers/decorator institucional em `trajetoria/comunicacao/acesso.py`, reusando identificação de `demonstracao/operador.py`, `escopo_de_acompanhamento` e `campanhas_visiveis`; reobter vínculos e impedir chamadas diretas com operador/contexto arbitrário; depende de T004 RED e T005.
- [X] T007 Executar GREEN de T003/T004 e regressão de `tests/governanca/` e `tests/interface/test_demonstracao_operador.py`; conferir que `trajetoria/demonstracao/operador.py` e cenário A/B/C não foram modificados.

Checkpoint: autorização não equivale a acompanhamento implícito; histórias só começam após T007.

## Fase 3 — US1: conferir público-alvo atual (P1, 9 tasks, MVP de consulta)

Todas as telas são administrativas/institucionais. Público = público-alvo da Campanha,
nunca acesso aberto de egresso. Meta independente: quatro Conclusões/duas Pessoas, uma com
contato; totais 4/2/1/1/1, e recorte CSAEG antes da deduplicação, sem envio/escrita.

### 3A — Fronteira de contato fictício (4 tasks)

- [X] T008 [P] [US1] Escrever e confirmar RED do contrato zero/um em `tests/comunicacao/test_contatos.py`: fonte+ID canônico, mapa determinístico, contatos distintos, homônimos, nome não determina endereço, ID não mapeado e `SIM-P-0010` sem contato; nenhuma coluna em Pessoa.
- [X] T009 [P] [US1] Escrever e confirmar RED da origem em `tests/comunicacao/test_origem.py`: Pessoa ou Conclusão de outra fonte torna base recusada, sem exposição/lista silenciosamente reduzida; falha do resolver não vira ausência normal; sem backend instanciado; usar caplog e exceções com sentinelas fictícias de nome/e-mail/conteúdo/credencial para comprovar zero exposição nos logs de preparação antes de T010.
- [X] T010 [US1] Implementar mapa local e `contato_ficticio -> str | None` em `trajetoria/comunicacao/contatos.py` e verificação de origem em `trajetoria/comunicacao/seguranca.py`; usar IDs estáveis e `sim-p-NNNN@example.invalid`, não tocar `academico/models.py` ou fonte acadêmica; erros de origem/resolução geram somente categoria segura, sem texto bruto da exceção em logs; depende de T008/T009 RED.
- [X] T011 [US1] Executar GREEN de `tests/comunicacao/test_contatos.py` e `tests/comunicacao/test_origem.py`; inspecionar ausência de escrita/campo de contato em `trajetoria/academico/models.py` e nenhuma alteração do cenário/provider canônico.

### 3B — Público e deduplicação (5 tasks)

- [X] T012 [P] [US1] Escrever e confirmar RED de população/contagens em `tests/comunicacao/test_publico.py`: uma/três Conclusões por Pessoa, inelegíveis, zero elegíveis/contatos, unidades diferentes/ausentes, várias CSAEG, CPAEG+CSAEG e homônimos; provar ordem 004 → escopo → PK distinta → contato, sem consultar Participação/Q1.
- [X] T013 [P] [US1] Escrever e confirmar RED do GET administrativo em `tests/comunicacao/test_publico_http.py`: 200 para autorizado nos três estados, 403 fora de escopo/sem vínculo/Pessoa sem operador, 404 inexistente/modo desligado, 405 métodos inadequados, números/momento corretos e snapshot intacto; usar CSRF onde aplicável; antes de T015, capturar logs e HTML das recusas/falhas de preparação com sentinelas fictícias e comprovar ausência de nomes/contatos/conteúdo/credenciais/tracebacks.
- [X] T014 [US1] Implementar consultas/valores de público em `trajetoria/comunicacao/consultas.py`, consumindo `populacao_no_momento`, aplicando igualdade exata de unidade antes de Pessoas distintas; validar origem/resolver e fórmulas, sem `_universo` privado da 011 ou materialização persistida; depende de T012 RED e T010.
- [X] T015 [US1] Implementar GET protegido em `trajetoria/comunicacao/views.py`, rota em `trajetoria/acompanhamento/urls.py`, resumo em `trajetoria/comunicacao/templates/comunicacao/comunicacao.html` e link contextual em `trajetoria/acompanhamento/templates/acompanhamento/campanha.html`; estender base administrativa, ocultar rascunho para B, não habilitar envio nesta etapa; tratar falhas de preparação com categoria genérica sem registrar exceção bruta ou dados pessoais; depende de T013 RED, T006 e T014.
- [X] T016 [US1] Executar GREEN de `tests/comunicacao/test_publico.py` e `tests/comunicacao/test_publico_http.py`, validar snapshot completo e cenários A 6/5/B 3/2; conferir 011 preservada em `tests/acompanhamento/`, sem transporte.

Checkpoint US1: consulta utilizável e autorizada, 1 mensagem prevista por Pessoa contactável;
não implementa preview/envio. MVP de consulta é marco interno, não conclusão da feature.

## Fase 4 — US2: conferir convite antes da simulação (P1, 9 tasks)

Meta independente: comparar renderer e mensagem construída com mesmos parâmetros, sem envio.

### 4A — Renderer único texto+HTML (5 tasks)

- [X] T017 [P] [US2] Escrever e confirmar RED do renderer em `tests/comunicacao/test_convite.py`: assunto institucional fixo, nome opcional/fallback “Olá!”, escape HTML, parâmetros somente nome/Campanha/URL, sem curso/respostas/rascunho, CTA local e texto/HTML semanticamente equivalentes, sem editor/recurso externo.
- [X] T018 [P] [US2] Escrever e confirmar RED da composição MIME/cabeçalhos em `tests/comunicacao/test_convite_mime.py`: multipart/alternative texto+HTML, um `to`, From com nome institucional fixo e mailbox `trajetoria@example.invalid` validados separadamente; remetente nomeado válido aceito, nome/mailbox adulterados e CR/LF recusados, destinatário com display name recusado, nenhum CC/BCC/anexo, URL não construída de Host do cliente e igualdade com resultado do renderer; apenas construir mensagem, sem transporte; seguir URL neutra com/sem Pessoa não abre Serra/Vitória nem cria Participação (snapshot), antes de T019/T020.
- [X] T019 [US2] Implementar renderer/template fixo em `trajetoria/comunicacao/convite.py` e `trajetoria/comunicacao/templates/comunicacao/convite.txt`/`convite.html`; conteúdo fictício institucional em português, sem prometer Campanha aberta/autenticação/entrega; depende de T017 RED.
- [X] T020 [US2] Implementar composição `EmailMultiAlternatives` em `trajetoria/comunicacao/convite.py`, consumindo somente saída do renderer, um destinatário e cabeçalhos fixos/seguros, compondo From após validação separada do nome institucional e mailbox fixos; não aplicar ao From nomeado a proibição de display name dos destinatários; depende de T018 RED e T019, sem chamar send.
- [X] T021 [US2] Executar GREEN de `tests/comunicacao/test_convite.py` e `tests/comunicacao/test_convite_mime.py`, conferir conteúdo equivalente, fallback e ausência de edição/recurso externo.

### 4B — Preview administrativo (4 tasks)

- [X] T022 [US2] Escrever e confirmar RED em `tests/comunicacao/test_preview.py`: representante determinístico por id_externo/PK no escopo, zero contato produz genérico sem destinatário, renderer comum, três estados, sandbox/srcdoc escapado, cookie de Pessoa não autoriza, sem backend e sem escrita; caplog e HTML em falha do renderer/resolver não contêm sentinelas fictícias de dados pessoais, conteúdo, credenciais ou traceback, antes de T023/T024; CTA neutro não torna Campanha em preparação respondível nem cria Participação.
- [X] T023 [US2] Integrar escolha representativa e renderer ao GET em `trajetoria/comunicacao/consultas.py` e `trajetoria/comunicacao/views.py`; nome/contato apenas no escopo, nenhum instrumento rascunho incluído; tratar erro de preview sem conteúdo/contato/exceção bruta em logs ou HTML; depende de T022 RED e T019.
- [X] T024 [US2] Implementar apresentação somente leitura em `trajetoria/comunicacao/templates/comunicacao/comunicacao.html`: remetente, representante ou ausência, assunto/texto/HTML em iframe sandbox sem scripts e título acessível, CTA/URL e código escapado; rótulo administrativo e limites do estado; sem editor/estilo da jornada.
- [X] T025 [US2] Executar GREEN de `tests/comunicacao/test_preview.py` e regressão US1; comparar prévia à mensagem construída, confirmar 320 px/200% com shell `trajetoria/acompanhamento/templates/acompanhamento/base.html` preservado.

Checkpoint US2: prévia e conteúdo único corretos, ainda sem simulação HTTP.

## Fase 5 — US3: simulação e resultado (P1, 14 tasks)

Meta independente: locmem comprova uma mensagem/Pessoa/execução, falhas parciais, estados e
zero alteração de domínio. Backend de teste não precisa Mailpit.

### 5A — Barreiras técnicas contra destinatário externo (6 tasks)

- [X] T026 [P] [US3] Escrever e confirmar RED de settings/guard em `tests/comunicacao/test_configuracao.py`: backend não explícito/indevido, SMTP fora loopback ou host DNS, porta incorreta, credencial, TLS/SSL, URL externa/userinfo/query/fragmento, modo off e locmem fora de teste; spy deve comprovar zero backend/conexão.
- [X] T027 [P] [US3] Escrever e confirmar RED do guard de domínio em `tests/comunicacao/test_seguranca.py`: endereço real, subdomínio/sufixo `example.invalid.evil`, destinatário malformado/lista/display name/CRLF, From institucional fixo válido e remetente adulterado, domínio exato válido; preflight do conjunto aborta integralmente inclusive após destino válido, domínio checado com SMTP incorreto e guarda final de `to`; sem rede.
- [X] T028 [US3] Adicionar settings locais explícitos em `config/settings.py` e documentação fictícia em `.env.example`: SMTP 127.0.0.1 ou ::1/1025, timeout 5 s, credenciais vazias/TLS/SSL off, remetente fixo, URL loopback 8000/demonstracao; operação desabilitada sem backend explícito e locmem só via flag interna de override em teste; depende de T026 RED.
- [X] T029 [US3] Implementar guards independentes de domínio, URL e transporte em `trajetoria/comunicacao/seguranca.py`, domínio constante exatamente `example.invalid` não liberável por env; validar toda preparação antes de backend, capturando configuração efetivamente usada; depende de T026/T027 RED.
- [X] T030 [US3] Aplicar validação final de destinatário/remetente ao construir mensagem em `trajetoria/comunicacao/convite.py`, reusável imediatamente antes de send; distinguir mailbox simples de destinatário e From institucional fixo validado por componentes; validar texto/HTML sem recursos externos e cabeçalhos, sem backend custom completo; depende de T027 RED e T029.
- [X] T031 [US3] Executar GREEN de `tests/comunicacao/test_configuracao.py` e `tests/comunicacao/test_seguranca.py`; confirmar rejeição de externo independentemente de Mailpit/EMAIL_HOST e ausência de conexão em cada recusa.

### 5B — Simulação/transporte e resultado transitório (8 tasks)

- [X] T032 [P] [US3] Escrever e confirmar RED em `tests/comunicacao/test_simulacao.py`: preparar/coletar permitidos, encerrada por data/ato recusada, público refeito após preview, zero contato sem backend, 1/Pessoa, resultado interno com PK/situação e agregados (sem nomes/contatos), projeção do template somente agregada, situações individuais transitórias e totais, snapshot completo intacto inclusive após seguir CTA neutro com/sem Pessoa; Campanha em preparação permanece não respondível; dois POSTs legítimos geram duas mensagens/Pessoa sem “já enviado”, histórico, chave de idempotência ou dedup entre execuções.
- [X] T033 [P] [US3] Escrever e confirmar RED de falha parcial em `tests/comunicacao/test_falhas.py`: sequência sucesso/exceção SMTP/sucesso/sem contato, retorno zero, timeout após aceite simulado e erro inesperado; cada mensagem tentada no máximo uma vez, anteriores preservadas, conexões novas/fechadas, restantes não tentadas se interrupção; marcador `pytest.mark.django_db(transaction=True)` comprova SMTP fora de atomic/transação de banco, sem retry/rollback; antes de T035, caplog e resultado das falhas SMTP/timeout/inesperadas não podem conter sentinelas fictícias de nome/endereço/corpo/respostas/credenciais nem exceção bruta ou traceback.
- [X] T034 [P] [US3] Escrever e confirmar RED do POST em `tests/comunicacao/test_simulacao_http.py`: CSRF real (`Client(enforce_csrf_checks=True)`), GET da ação 405, cliente não escolhe destinatário/conteúdo/URL/totais, autorização da operação direta, 409 encerrada, 422 preflight, antes de T036/T037, respostas 422/500 sem sentinelas fictícias/traceback, contexto de template sem coleção individual ou exceção bruta, resultado no-store sem sessão/cookie/cache e refresh/GET sem novo envio.
- [X] T035 [US3] Implementar operação em `trajetoria/comunicacao/operacoes.py`: contexto atual autorizado/estado e único instante, população/contatos/renderização/preflight completos antes de transporte, envio síncrono individual Django com nova conexão/fechamento e fail_silently=False; resultado por Pessoa em memória confirmado/falha/sem contato ou não tentada, retornar coleção interna somente PK/situação e agregados, sem nomes/contatos/conteúdo/exceção bruta; tratar falhas esperadas e inesperadas sem logging de valores sensíveis ou traceback; sem atomic, retry, gravação ou idempotência; depende de T032/T033/T034 RED, T006, T014, T020 e T031.
- [X] T036 [US3] Implementar POST institucional com CSRF/status/resultados em `trajetoria/comunicacao/views.py` e rota em `trajetoria/acompanhamento/urls.py`; operação recebe somente UUID/operador do adaptador confiável, revalida vínculos/escopo/estado e ignora payload adulterado e projeta somente instante/escopo/totais/categorias para o template, nunca a coleção individual; erros HTTP genéricos sem log de exceção bruta; depende de T034 RED e T035.
- [X] T037 [US3] Integrar formulário explícito e resposta transitória em `trajetoria/comunicacao/templates/comunicacao/comunicacao.html` e `resultado.html`: situações/tentativas/aceites/falhas/sem contato/não tentadas, aviso de incerteza e repetição independente, sem “entregue” ou lista nominal; ação somente preparo/coleta, retorno GET, no-store sem PRG que armazene resultado.
- [X] T038 [US3] Executar GREEN de `tests/comunicacao/test_simulacao.py`, `tests/comunicacao/test_falhas.py` e `tests/comunicacao/test_simulacao_http.py`; verificar igualdade tentativas=aceites+falhas e Pessoas=confirmadas+falhas+sem contato+não tentadas em execução preparada, duas execuções legítimas independentes e SMTP fora de transação, projeção agregada e zero sentinela sensível nos logs/respostas de erro.
- [X] T039 [US3] Executar regressão conjunta de `tests/comunicacao/`/`tests/campanha/`/`tests/acompanhamento/` e revisar `trajetoria/comunicacao/operacoes.py`: nenhuma mutação/entidade persistida, nenhuma consulta de Participação para segmentar, nenhuma leitura API Mailpit, nenhuma tentativa automática adicional.

Checkpoint US3: fluxo automático completo comprovado com locmem; estados são operacionais,
não entrega. “Submetidas” contador = tentativas; situação individual confirmada = retorno 1.
“Falha” = tentativa sem confirmação; “sem contato” = não tentou. Falha inesperada deixa
restantes “não tentadas”. Resultados individuais nunca são gravados nem exibidos como mailing.

## Fase 6 — US4: isolamento institucional e Mailpit manual (P2, 6 tasks)

Meta independente: roteiros/negativos de fronteira e inspeção real local do mesmo convite.

### 6A — Autorização/escopo em todas as entradas (3 tasks)

- [X] T040 [US4] Completar e executar a verificação integrada em `tests/comunicacao/test_demonstracao.py`: inventário das GET/POST da 016, URL direta fora de escopo, revogação, CPAEG→CSAEG, C sem vínculo, cookie somente de Pessoa e operador forjado; reaproveitar testes escritos antes das implementações em T004/T013/T022/T034; pode passar imediatamente, sem exigir RED artificial ou novo marcador de decorator.
- [X] T041 [US4] Auditar correspondência entre inventário em `tests/comunicacao/test_demonstracao.py` e proteções já implementadas em `trajetoria/comunicacao/acesso.py`, `views.py` e `trajetoria/acompanhamento/urls.py`; verificar CTA neutro com/sem Pessoa, Campanha em preparação não respondível e snapshot intacto; nenhuma nova camada/marcador para produzir RED. Se encontrar defeito, reproduzi-lo com teste de regressão que falhe antes da correção, preservando cenário e jornada.
- [X] T042 [US4] Executar GREEN de `tests/comunicacao/test_demonstracao.py` e regressão de `tests/acompanhamento/test_acompanhamento_demonstracao.py`/`tests/interface/test_interface_cenario.py`; confirmar ocultação de rascunho para B e zero mensagens nos negativos.

### 6B — Mailpit somente no quickstart (3 tasks)

- [X] T043 [US4] Conferir e atualizar comandos de `specs/016-mobilizacao-comunicacao-simulada/quickstart.md` e `.env.example` contra implementação: Mailpit nativo loopback SMTP1025/UI8025 sem relay/forward, app SMTP explícito local, preparo existente/idempotente e cenário Serra/Vitória EM PREPARAÇÃO; não adicionar API Mailpit/Docker/fila ou dependência à suíte.
- [X] T044 [US4] Executar roteiro manual de `specs/016-mobilizacao-comunicacao-simulada/quickstart.md` com B (3 Conclusões/2 Pessoas/1 contato/1 mensagem) e A (6/5/4/4), inspecionar texto/HTML/remetente/to/CTA, repetir B para comprovar duas mensagens legítimas para Bruno; parar Mailpit para falha sem retry/fallback e registrar evidência fictícia mínima no próprio quickstart, sem nomes/endereços em logs técnicos.
- [X] T045 [US4] Validar e registrar no `specs/016-mobilizacao-comunicacao-simulada/quickstart.md` CTA com/sem Pessoa fictícia: entrada neutra, Serra/Vitória continua em preparação e não respondível, nenhuma abertura/Participação/contorno 004/007; C e B fora de escopo recusados, suíte funciona com Mailpit parado.

Checkpoint US4: Mailpit é caixa de inspeção manual, não serviço do domínio nem infraestrutura
de teste/produção. Não precisa abertura da Campanha para demonstrar e-mail.

## Fase 7 — Validação transversal/fechamento (5 tasks)

Testes de comportamento foram escritos antes das implementações acima; esta fase executa
verificações de encerramento, não posterga testes de invariantes.

- [X] T046 Auditar zero persistência em `trajetoria/comunicacao/`, `trajetoria/academico/models.py`, `trajetoria/campanha/models.py`, `trajetoria/participacao/models.py` e migrations existentes; executar snapshots de `tests/comunicacao/` e `uv run python manage.py makemigrations --check --dry-run`, confirmar zero modelos/colunas/migrations/Convite/Destinatário/Disparo/Evento ou histórico/sessão/cache/cookie de resultado.
- [X] T047 Auditar zero destinatário externo em `tests/comunicacao/test_seguranca.py`/`test_simulacao.py`, inspecionando todos os to/cc/bcc/remetente de mail.outbox e todos os negativos (incluindo SMTP incorreto) com spy zero transporte; revisar `trajetoria/comunicacao/seguranca.py`/`operacoes.py` para preflight integral e guard final, domínio exato não configurável para exteriorização.
- [X] T048 Validar teclado/foco/labels/HTML sandbox, 320 px/200%/sem JavaScript em `trajetoria/comunicacao/templates/comunicacao/` e registrar resultados fictícios mínimos em `specs/016-mobilizacao-comunicacao-simulada/quickstart.md`; confirmar baseline015 e shell administrativo inalterados, sem nova navegação de jornada.
- [X] T049 Executar `uv run pytest` e `uv run ruff check .` usando `pyproject.toml`, com Mailpit parado; resolver regressões no escopo dos arquivos previstos e registrar comandos/resultados sem credenciais no `specs/016-mobilizacao-comunicacao-simulada/quickstart.md`.
- [X] T050 Revisar Definition of Done/38 FRs/10 SCs e documentos `specs/016-mobilizacao-comunicacao-simulada/spec.md`, `plan.md`, `contracts/` e `checklists/requirements.md`; confirmar decisões produtivas ainda abertas, nenhuma abstração genérica/editor/fila/retry/chave de idempotência/infra produtiva, e marcar somente tasks efetivamente verificadas após implementação.

## Dependencies & Execution Order

```text
F1 Setup → F2 Autorização/escopo
                 ↓
US1 3A Contato → 3B Público/deduplicação (MVP de consulta)
                 ↓
US2 4A Renderer → 4B Preview
                 ↓
US3 5A Guards/config → 5B Simulação/transporte
                 ↓
US4 6A Autorização integrada → 6B Mailpit manual
                 ↓
F7 zero persistência + zero externo + QA + regressão/DoD
```

Dependências são explícitas: US1 precisa F2; US2 consome público/contato US1; US3 consome
renderer+prévia US2 e guards; US4 valida integração das três primeiras. Não fingir histórias
independentes de componentes compartilhados. Cada história tem teste próprio e checkpoint
isolado com locmem/helpers, e pode ser validada quando seus pré-requisitos estão disponíveis.

Em cada subfase funcional, concluir tasks RED antes de modificar módulos correspondentes.
GET/escopo: T004/T013 antes de T006/T015; preview/erros: T022 antes de T023/T024;
POST/escopo/erros: T032/T033/T034 antes de T035/T036/T037. Neutralidade do CTA e ausência
de mutação devem ser testadas em T018/T022/T032 antes dos respectivos renderer/preview/envio.
T040–T042 são verificação final integrada, sem requisito de falha inicial ou código novo
para inventário/marcador. Caso detectem defeito, adicionar regressão RED antes de corrigir.
Casos já protegidos podem passar imediatamente; não quebrar código para satisfazer TDD.

## Execução serial em arquivos compartilhados

| Arquivo | Tasks que o alteram/revisam | Ordem |
| --- | --- | --- |
| `config/settings.py` | T002 → T028 | registro app antes de config email; sem edição simultânea |
| `.env.example` | T028 → T043 | configuração primeiro, conferência manual depois |
| `trajetoria/governanca/regras.py` | T005 | alteração exclusiva, preservar capacidades 010/011 |
| `trajetoria/comunicacao/acesso.py` | T006; leitura em T041 | helper antes de auditoria final |
| `trajetoria/comunicacao/seguranca.py` | T010 → T029 | origem antes de transporte/domínio |
| `trajetoria/comunicacao/consultas.py` | T014 → T023 | público antes de representante |
| `trajetoria/comunicacao/convite.py` | T019 → T020 → T030 | renderer antes de MIME/guard final |
| `trajetoria/comunicacao/views.py` | T015 → T023 → T036; leitura em T041 | GET, preview, POST, auditoria institucional |
| `trajetoria/acompanhamento/urls.py` | T015 → T036; leitura em T041 | GET antes de POST/auditoria final |
| `trajetoria/comunicacao/templates/comunicacao/comunicacao.html` | T015 → T024 → T037 | público, preview, formulário |
| `quickstart.md` | T043 → T044 → T045 → T048 → T049 | comandos antes de evidências/QA |
| `tests/comunicacao/test_demonstracao.py` | T040 → T041 → T042 | verificação integrada, auditoria e regressão |

T046/T047 são leitura/validação; não iniciar auditoria enquanto outras tasks alterarem os
arquivos auditados. Demais testes específicos são arquivos separados, sem fixture global
mutável. Mesmo executando testes em paralelo, não editar arquivo compartilhado ao mesmo tempo.

## Parallel Examples por história

Somente lotes liberados após pré-requisitos; RED primeiro e GREEN depois. [P] não autoriza
antecipar task com dependência incompleta nem execução autônoma nesta fase documental.

- Fundação: T003 + T004 em arquivos distintos, após F1.
- US1: T008 + T009; depois contato verde, T012 + T013. Implementação/escritas compartilhadas serial.
- US2: T017 + T018 após US1. Preview T022–T025 sequencial por views/template compartilhados.
- US3: T026 + T027 após US2; guards verdes, T032 + T033 + T034 em arquivos distintos.
- US4: nenhuma task marcada [P]; autorização integrada e Mailpit dependem do fluxo completo.

## Matriz RED → implementação → GREEN

| Bloco | Testes que devem falhar antes | Implementação liberada | Confirmação |
| --- | --- | --- | --- |
| Capacidade/escopo | T003/T004 | T005/T006 | T007 |
| Contato/origem | T008/T009 | T010 | T011 |
| Público/deduplicação/GET | T012/T013 | T014/T015 | T016 |
| Renderer/MIME | T017/T018 | T019/T020 | T021 |
| Preview | T022 | T023/T024 | T025 |
| Config/domínio | T026/T027 | T028/T029/T030 | T031 |
| Resultado/transporte/POST | T032/T033/T034 | T035/T036/T037 | T038/T039 |
| Autorização/CTA integrada | T004/T013/T018/T022/T032/T034 | T006/T015/T019/T023/T035/T036 | T040–T042 (auditoria, sem RED artificial) |

T001/T002 são preparação de teste/pacote sem comportamento. T040–T050 são validação/documentação,
não implementação funcional. A geração documental não executou código; a execução posterior
autorizada está registrada nos marcadores e no quickstart.

## Falhas parciais e domínio reservado — casos obrigatórios

T033 injeta falha no limite de envio preservando locmem para aceites: quatro Pessoas,
duas confirmadas, uma exceção SMTP/retorno zero e uma sem contato. Esperado: três tentativas,
dois aceites, uma falha, uma sem contato, duas mensagens no outbox, zero retry, sem desfazer
primeira mensagem. Timeout após aceite simulado pode deixar mensagem na caixa/outbox, mas
conta falha de confirmação; resultado não promete ausência. Erro inesperado aborta restantes,
conta tentativa não confirmada como falha e informa não tentadas. T032/T033 snapshots completos
provam invariantes; teste transacional verifica que operação não abre atomic para SMTP.

T027 parametriza domínio exato, domínio real, subdomínio, sufixo/lookalike e endereço inválido.
Valida guard sozinho sob SMTP errado e preflight integrado com destino externo depois de
válido: abortar tudo, spy de backend/send zerado. Guard final bloqueia adulteração antes do
send. T047 audita inventário de mensagens; nenhum to/cc/bcc pode conter endereço externo.
Nunca usar SMTP/Mailpit/rede no caso negativo; nomes/dados apenas fictícios.

## Implementation Strategy e escopo

MVP interno: F1 + F2 + US1, consulta autorizada com contato fictício/deduplicação. Não é
entrega concluída: US2/US3/US4 e validações são obrigatórias. Avançar por checkpoints verdes,
sem publicar/deploy ou antecipar produção. Não criar modelo/migration, NotificationService,
registry, fila, scheduler, retry, auth nova, API Mailpit, editor ou chave de idempotência.
SMTP nativo/config local/flag locmem interna são adaptações mínimas da demonstração existente.
Nenhuma task introduz infraestrutura produtiva; se execução sugerir generalização, remover
ampliação de escopo e manter contratos aprovados. Todas as decisões reais permanecem abertas.

## Resumo e validação desta decomposição

| Fase | História | Tasks |
| --- | --- | --- |
| 1 Setup | compartilhada | 2 |
| 2 Autorização/escopo | compartilhada | 5 |
| 3A Contato | US1 | 4 |
| 3B Público/deduplicação | US1 | 5 |
| 4A Renderer texto+HTML | US2 | 5 |
| 4B Preview | US2 | 4 |
| 5A Domínio/configuração | US3 | 6 |
| 5B Simulação/transporte | US3 | 8 |
| 6A Autorização integrada | US4 | 3 |
| 6B Mailpit quickstart | US4 | 3 |
| 7 Validação transversal | compartilhada | 5 |
| Total | US1 9; US2 9; US3 14; US4 6; compartilhadas 12 | 50 |

Hooks before/after tasks: `.specify/extensions.yml` ausente; nenhum hook a executar.
Formato, IDs, referências locais e cobertura de histórias/contratos revisados. Nenhuma task
antecipada durante a geração documental. A implementação posterior autorizada usa os
marcadores acima; nenhum commit foi criado automaticamente.
