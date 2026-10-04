# Tasks: Gestão mínima de Campanha

**Input**: `specs/017-gestao-minima-campanha/` — [spec](spec.md) (com Clarifications de
2026-10-03), [plan](plan.md), [research](research.md), [data-model](data-model.md),
[rotas](contracts/rotas.md), [domínio](contracts/dominio.md) e [quickstart](quickstart.md).
**Branch/baseline**: `claude/spec-017-campaign-management-e96f8f`, main `5e50fec` (PR #26).
**Estado**: implementação concluída e validada; 43 tasks completas.

## Formato e convenções

`- [ ] TNNN [P?] [USn?] descrição com caminho`. IDs contínuos; [P] só para arquivos
distintos, sem dependência entre si. Caminhos relativos à raiz do repositório. Setup,
fundação e final sem história; as demais tasks levam US1–US5 da spec.

**Estrutura**: sem app novo. Escrita e orquestração no subpacote
`trajetoria/acompanhamento/gestao/`; barreira `@gestao` em `trajetoria/acompanhamento/acesso.py`;
domínio continua em `trajetoria/campanha/`.

**TDD obrigatório** (como na 016): escrever os testes do bloco, executá-los e confirmar a
falha pela ausência do comportamento da 017 (não por fixture quebrada); sem xfail/skip.
Depois implementar e confirmar verde com os mesmos testes.

**Guardas válidas para todas as tasks** — qualquer task que as viole está errada:

- nenhum model, campo ou migration (`makemigrations --check` limpo);
- nenhuma chamada a `publicar` nem superfície de publicação de Versão;
- nenhum campo, filtro ou tela de critério de abrangência, público, Lote ou divulgação;
  `definir_criterios` e `remover_campanha` não são chamados pela interface;
- `impedimentos_de_abertura` é a única fonte da regra de abertura; a interface nunca
  reimplementa as condições, e todo POST chama a operação da 004, que revalida;
- `pode_gerir_campanha` é a única regra da capacidade e continua pura; DP-402 permanece
  aberta nos textos e docstrings;
- testes de rotas são semânticos (barreira e método por rota), nunca contagem de rotas.

## Fase 1 — Setup de teste (1 task)

- [X] T001 Estender `tests/acompanhamento/construcao.py` sem mudar os estados existentes: estado `pronta` em `campanha()` (período de hoje−1 a hoje+30, nunca aberta) e helper `versao_em_rascunho(inst)` que cria, pelas operações da 002, uma Versão em RASCUNHO; criar `tests/acompanhamento/gestao.py` com helpers de requisição (`formulario(cliente, url)`, `enviar(cliente, url, dados)`, extração de erros por campo e de ações do painel). Nenhum comportamento da feature.

Checkpoint: helpers usados pelas fases seguintes; suíte atual continua verde.

## Fase 2 — Fundação: regra única de abertura e capacidade (risco: regra duplicada, autorização) (11 tasks)

Meta: as duas fontes únicas da 017 existem e estão provadas antes de qualquer tela.

### Testes primeiro

- [X] T002 [P] Escrever RED de equivalência em `tests/campanha/test_campanha_impedimentos.py`: para Versão em rascunho, sem período, antes do início, depois do fim, combinações (rascunho + sem período; rascunho + fora do período) e Campanha pronta, `impedimentos_de_abertura(c, agora=x)` devolve exatamente os `Violacao` (motivo, campo, detalhe, ordem) que `abrir(c, agora=x)` levanta em `CampanhaRejeitada`, e tupla vazia quando `abrir` abre; consultar não grava nem bloqueia (`aberta_em` intacto, nenhuma escrita).
- [X] T003 [P] Escrever RED de `pode_gerir_campanha` em `tests/governanca/test_governanca_regras.py`: CPAEG ativo → verdadeiro; CPAEG inativo, CSAEG (uma ou várias unidades), sem vínculo e vínculo misto CSAEG+CPAEG inativo → falso; misto com CPAEG ativo → verdadeiro; função pura (não lê settings nem banco).
- [X] T004 [P] Escrever RED da barreira em `tests/acompanhamento/test_gestao_acesso.py` com uma view sintética decorada por `@gestao`: modo desligado → 404 mesmo chamando a view sem middleware; sem operador → 302 para `/demonstracao/operador/?destino=acompanhamento`; CSAEG, sem vínculo e vínculo revogado entre duas requisições → 403 com "Acesso não permitido" e sem nome de Campanha; CPAEG → passa, com `request.atuacao.gerir_campanha` verdadeiro; marcador `gestao` presente.
- [X] T005 [P] Escrever RED em `tests/acompanhamento/test_acompanhamento_acesso.py` para `Atuacao.gerir_campanha` preenchido por `@acompanhamento` (CPAEG verdadeiro; CSAEG e CPAEG+CSAEG conforme a regra) e substituir `test_toda_rota_exige_o_gate_de_acompanhamento` por verificação semântica: toda rota de `acompanhamento.urls` tem exatamente uma marca entre `acompanhamento`, `comunicacao` e `gestao`; rotas com `/comunicacao/` têm `comunicacao`; rotas com `/nova/`, `/editar/`, `/abrir/` ou `/encerrar/` têm `gestao`; sem `len(urlpatterns)`.
- [X] T006 [P] Substituir em `tests/comunicacao/test_demonstracao.py` a asserção `len(rotas) == 4` (`test_inventario_protegido`) por verificação semântica equivalente das rotas de comunicação (barreira própria, sem `acompanhamento`, recusas e redirect mantidos).

### Implementação

- [X] T007 Extrair `impedimentos_de_abertura(campanha, *, agora=None) -> tuple[Violacao, ...]` em `trajetoria/campanha/consultas.py` (exportar em `__all__`), relendo o estado da Versão no banco, com a ordem "VERSAO_NAO_PUBLICADA; depois PERIODO_NAO_DEFINIDO ou FORA_DO_PERIODO" e os mesmos `campo` e `detalhe` de hoje; mover `Motivo`/`Violacao` de import conforme necessário sem ciclo. Depende de T002 RED.
- [X] T008 Fazer `abrir` em `trajetoria/campanha/operacoes.py` chamar `impedimentos_de_abertura` depois do bloqueio da linha e do tratamento de "já aberta", sem nenhuma outra mudança; executar `tests/campanha/` inteiro e T002 verdes. Depende de T007.
- [X] T009 Implementar `pode_gerir_campanha` em `trajetoria/governanca/regras.py` (exportar em `__all__`): `any(v.ativo and v.papel == Papel.CPAEG for v in vinculos)`, docstring como interpretação C1 da 017 restrita à demonstração, DP-402 aberta, sem conceder publicação, critérios, remoção ou mobilização. Depende de T003 RED.
- [X] T010 Em `trajetoria/acompanhamento/acesso.py`: acrescentar `gerir_campanha: bool = False` a `Atuacao`, preenchido em `@acompanhamento` por `pode_gerir_campanha`; criar `@gestao` (o mais externo): `settings.TRAJETORIA_DEMONSTRACAO` falso → `Http404`; sem operador → redirect à escolha; sem `pode_gerir_campanha` → `recusa(request, "A gestão de Campanhas não está disponível para esta atuação.")`; define `request.atuacao`; marcador `envolvida.gestao = True`. `@comunicacao` (016) não muda. Depende de T004, T005 RED e T009.
- [X] T011 Executar GREEN de T002–T006 e regressão de `tests/campanha/`, `tests/governanca/`, `tests/acompanhamento/`, `tests/comunicacao/`.
- [X] T012 Criar `trajetoria/acompanhamento/gestao/__init__.py` e `trajetoria/acompanhamento/gestao/mensagens.py` com o vocabulário fechado de [data-model](data-model.md) e [domínio](contracts/dominio.md): mapa motivo → (campo, texto); impedimentos (causa e correção); confirmações; aviso de sobreposição exatamente "Já existem outras Campanhas em coleta. Isso pode fazer com que alguns egressos tenham mais de uma pesquisa disponível."; avisos pós-ação `campanha-criada`, `configuracao-salva`, `coleta-aberta`, `coleta-encerrada`, `ja-em-coleta`, `ja-encerrada`; textos 409; aviso de abrangência restrita; sem nomes de `Motivo` nem identificadores.

Checkpoint: regra de abertura única provada por equivalência; capacidade e barreira testadas por comportamento; nenhuma rota nova ainda.

## Fase 3 — US1: criar Campanha ampla com período opcional (P1, MVP) (6 tasks)

Teste independente: CPAEG cria só com nome e Versão publicada → EM PREPARAÇÃO, sem critérios, impedimento "período não definido"; com período futuro → "a partir de dd/mm/aaaa".

- [X] T013 [US1] Escrever RED em `tests/acompanhamento/test_gestao_criar_editar.py` (criação): GET `/acompanhamento/campanhas/nova/` mostra Nome, Versão, Início (opcional), Fim (opcional) e nenhum campo de critério/público/lote; a escolha oferece só Versões PUBLICADA rotuladas "Pesquisa — designação" (rascunho ausente); sem Versão publicada → explicação "a publicação não é feita aqui" e nenhum `<form>`; POST nome+Versão → 302 ao detalhe com `aviso=campanha-criada`, Campanha com os seis critérios nulos e sem período; POST com período válido → período gravado; nome em branco, só uma data, início > fim, data em formato inválido, Versão fora das opções → 422, erros por campo, valores preservados e **nenhuma** Campanha criada (atomicidade criar + período); nenhuma chamada a `publicar`; nenhum HTML de gestão (formulário e erros) contém nome de `Motivo` (por exemplo `NOME_VAZIO`, `PERIODO_INCOMPLETO`) nem UUID fora de atributos de link (FR-028).
- [X] T014 [P] [US1] Implementar `CampanhaForm` em `trajetoria/acompanhamento/gestao/formularios.py`, herdando `trajetoria.editor.formularios.Formulario`: `nome` texto sem strip; `versao` `ChoiceField` com opções recebidas; `inicio`/`fim` `DateField(required=False)` com `<input type="date">` e mensagem de formato fechada; só converte (vazio → `None`), sem regra de domínio. Depende de T013 RED.
- [X] T015 [P] [US1] Implementar em `trajetoria/acompanhamento/gestao/painel.py` `versoes_oferecidas(atual=None)`: Versões `PUBLICADA` ordenadas por nome da Pesquisa e designação, rótulo "Pesquisa — designação"; se `atual` estiver em rascunho, primeira opção com sufixo "(não publicada — impede a abertura)". Depende de T013 RED.
- [X] T016 [US1] Implementar `nova` em `trajetoria/acompanhamento/gestao/views.py` (`@gestao`, `require_http_methods(["GET","POST"])`, `never_cache`): em `transaction.atomic()`, `criar_campanha(nome, versao)` e, se alguma data foi informada, `definir_periodo(inicio, fim)`, cada uma num savepoint; cada `CampanhaRejeitada` vira erro de campo pelo mapa de `mensagens`; havendo erro, desfazer e responder 422; motivo fora do mapa é relançado; sucesso → redirect `?aviso=campanha-criada`. Templates `trajetoria/acompanhamento/templates/acompanhamento/gestao/formulario.html` (estende `acompanhamento/base.html`, usa `editor/_campo.html` e `editor/_erros.html`, ajuda "O período pode ser definido depois; ele é necessário para abrir a coleta.") e a explicação sem Versão publicada. Depende de T010, T012, T014, T015.
- [X] T017 [US1] Registrar `campanhas/nova/` em `trajetoria/acompanhamento/urls.py` antes de `campanhas/<uuid:campanha>/`, e acrescentar o link "Nova Campanha" em `trajetoria/acompanhamento/templates/acompanhamento/campanhas.html` somente se `atuacao.gerir_campanha`. Depende de T016.
- [X] T018 [US1] Executar GREEN de T013 e da suíte de `tests/acompanhamento/`; confirmar que o HTML da lista para CSAEG não contém "Nova Campanha".

Checkpoint (MVP): a CPAEG cria Campanhas pela interface; nada mais muda para outros operadores.

## Fase 4 — Painel de estado e impedimentos no detalhe (P1; base de US2–US4; risco: controles que falhariam, rótulo ambíguo) (5 tasks)

As tasks desta fase levam [US2] por convenção de rótulo, mas são a base comum de US2, US3 e
US4 (FR-016, FR-017, FR-022, FR-023, FR-023a): as ações de editar, abrir e encerrar são
ligadas a partir do painel.

Teste independente: para cada situação da matriz de FR-017, o painel mostra só as ações admitidas e os impedimentos com causa e correção; CSAEG não vê painel.

- [X] T019 [US2] Escrever RED em `tests/acompanhamento/test_gestao_painel.py`: matriz FR-017 com as Campanhas do construtor — pronta → "Editar configuração" e "Abrir coleta"; sem período, em rascunho, futura → só "Editar configuração" e os impedimentos correspondentes (todos, simultâneos quando houver mais de um, com "a partir de dd/mm/aaaa" quando antes do início); expirada sem abertura → "Período encerrado — Campanha nunca aberta", aviso de que não houve coleta e "Editar configuração"; em coleta → "Encerramento previsto" e só "Encerrar coleta"; encerrada (explícita e por período) → nenhuma ação; Campanha com critérios (`unidades`, `niveis`) → aviso de leitura da abrangência; Campanha ampla → nenhuma seção de critérios/público; "Comunicação simulada" presente nos três estados; CSAEG e CPAEG+CSAEG conforme a regra; `?aviso=` desconhecido ignorado; nenhum texto do painel contém nome de `Motivo` nem UUID fora de atributos de link (FR-028).
- [X] T020 [P] [US2] Escrever RED em `tests/acompanhamento/test_acompanhamento_lista.py` e `test_acompanhamento_estados.py`: Campanha `expirada_sem_abertura` aparece como "Período encerrado — Campanha nunca aberta" na lista e no detalhe para CPAEG **e** CSAEG; Campanha encerrada após coleta continua "Encerrada"; demais textos da 011 inalterados.
- [X] T021 [US2] Implementar `painel(campanha, agora)` em `trajetoria/acompanhamento/gestao/painel.py`: situação de gestão, ações da matriz, impedimentos a partir de `impedimentos_de_abertura` (só para nunca aberta; para Versão não publicada, texto de correção conforme haja ou não Versão publicada disponível; o texto "antes do início"/"período encerrado" escolhido comparando a data de referência com `inicio`/`fim`, sem decidir se há impedimento), encerramento previsto, abrangência restrita legível só quando algum critério não é nulo. Depende de T007, T012, T019 RED.
- [X] T022 [US2] Acrescentar o rótulo em `trajetoria/acompanhamento/apresentacao.py` e usá-lo em `CampanhaAcompanhada.situacao` (`trajetoria/acompanhamento/consultas.py`) quando o estado é ENCERRADA e `aberta_em` é nulo; no detalhe (`trajetoria/acompanhamento/views.py`, ainda só GET) incluir `painel` e o aviso pós-ação de lista fechada só se `request.atuacao.gerir_campanha`; template `trajetoria/acompanhamento/templates/acompanhamento/gestao/_painel.html` incluído por `campanha.html`. Depende de T020 RED, T021.
- [X] T023 [US2] Executar GREEN de T019–T020 e regressão completa de `tests/acompanhamento/` e `tests/comunicacao/`. Em `tests/acompanhamento/test_gestao_painel.py`, para CSAEG Vitória e para CSAEG+CPAEG inativo, verificar positivamente que o detalhe e a lista não contêm nenhum marcador do painel de gestão (ações "Nova Campanha", "Editar configuração", "Abrir coleta", "Encerrar coleta", impedimentos, aviso de abrangência) e continuam contendo todos os elementos da 011 (dados, avisos, resumo, recortes, "Comunicação simulada"); a suíte existente da 011 continua verde sem alteração além do rótulo de FR-023a.

Checkpoint: estado e impedimentos compreensíveis; nenhum botão que falharia por condição conhecida.

## Fase 5 — US2: editar configuração enquanto nunca aberta (P1) (4 tasks)

Teste independente: "rodada em preparação" (rascunho, sem período) → trocar para Versão publicada e definir período que inclui hoje → impedimentos somem e "Abrir coleta" aparece.

- [X] T024 [US2] Escrever RED em `tests/acompanhamento/test_gestao_criar_editar.py` (edição): GET `/acompanhamento/campanhas/<uuid>/editar/` preenchido; Versão atual em rascunho pré-selecionada e marcada, nenhum outro rascunho; POST altera nome, Versão e período juntos (falha em qualquer um → nada gravado, 422); completar período de Campanha sem período; corrigir período de expirada sem abertura → volta a EM PREPARAÇÃO; apagar as duas datas com período existente → 422 "pode ser corrigido, mas não removido", nada gravado; Campanha sem período e datas vazias → nada muda no período; Campanha com critérios (`unidades`, `niveis`) → o formulário de edição mostra o aviso de leitura da abrangência restrita, sem campo editável, e os critérios ficam intactos após salvar; Campanha ampla → formulário sem aviso de abrangência; Campanha aberta (em coleta e encerrada) → GET e POST 409 sem gravação; UUID inexistente → 404.
- [X] T025 [US2] Implementar `editar` em `trajetoria/acompanhamento/gestao/views.py`: Campanha já aberta → página `trajetoria/acompanhamento/templates/acompanhamento/gestao/conflito.html` (409); em `transaction.atomic()` com savepoints, `alterar_campanha(nome=, versao=)` e, se alguma data foi informada, `definir_periodo`; remoção de período existente rejeitada na interface; mesmo mapa de erros e 422; `CAMPANHA_JA_ABERTA` vinda do domínio (corrida) → 409; sucesso → `?aviso=configuracao-salva`. Reutiliza `CampanhaForm`, `versoes_oferecidas(atual=)` e a abrangência restrita legível de `painel.py`, exibida como aviso de leitura no formulário. Depende de T016, T021, T024 RED.
- [X] T026 [US2] Registrar `campanhas/<uuid:campanha>/editar/` em `trajetoria/acompanhamento/urls.py` e ligar "Editar configuração" no `_painel.html`. Depende de T025.
- [X] T027 [US2] Executar GREEN de T024 e regressão de `tests/acompanhamento/`.

## Fase 6 — US3: abrir a coleta (P1; risco: revalidação no POST) (4 tasks)

Teste independente: Campanha pronta → confirmar → EM COLETA, "Aberta em", sem "Editar configuração", e a Campanha passa a aparecer na entrada de demonstração para Conclusões na sua abrangência.

- [X] T028 [US3] Escrever RED em `tests/acompanhamento/test_gestao_abrir_encerrar.py` (abertura): GET de pronta mostra o que fica fixado, "aceitar respostas imediatamente", "não há reabertura nem prorrogação"; com outra Campanha EM COLETA, mostra o aviso exato de sobreposição e os nomes, sem bloquear; sem outra, nenhum aviso; com o período terminando hoje, a confirmação informa que a coleta se encerra ao fim de hoje (e não informa quando o fim é posterior); GET com impedimentos → impedimentos e nenhum `<form>`; POST → 302 `aviso=coleta-aberta`, `aberta_em` gravado; **POST revalida**: Campanha pronta no GET que se torna inválida antes do POST (trocar para Versão em rascunho ou período futuro pelas operações da 004) → 409 com os impedimentos atuais e nada gravado; POST repetido → 302 `aviso=ja-em-coleta` sem nova gravação; POST em encerrada → `aviso=ja-encerrada`; sem CSRF → 403; nenhuma chamada a `publicar` (Versão inalterada); depois de aberta, `campanhas_em_coleta_para` inclui a Campanha para uma Conclusão abrangida.
- [X] T029 [US3] Implementar `abrir` em `trajetoria/acompanhamento/gestao/views.py`: GET calcula `painel`/impedimentos só para orientar e lista nomes das outras Campanhas EM COLETA (consulta simples por estado, sem interseção); informa "a coleta se encerra ao fim de hoje" quando a data de referência é o fim do período; POST chama sempre `operacoes.abrir` (nunca decide pelo GET); `CampanhaRejeitada` → 409 em `confirmar_abertura.html` com impedimentos atuais; `JA_EM_COLETA`/`JA_ENCERRADA` → redirect com aviso; `ABERTA` → `?aviso=coleta-aberta`. Template `trajetoria/acompanhamento/templates/acompanhamento/gestao/confirmar_abertura.html`. Depende de T021, T028 RED.
- [X] T030 [US3] Registrar `campanhas/<uuid:campanha>/abrir/` em `trajetoria/acompanhamento/urls.py` e ligar "Abrir coleta" no `_painel.html`. Depende de T029.
- [X] T031 [US3] Executar GREEN de T028 e regressão de `tests/acompanhamento/`, `tests/participacao/` e `tests/interface/`.

## Fase 7 — US4: encerrar a coleta (P2) (4 tasks)

Teste independente: Campanha em coleta → confirmar → ENCERRADA "antecipadamente", sem ações de gestão, e nova Participação recusada pela 005.

- [X] T032 [US4] Escrever RED em `tests/acompanhamento/test_gestao_abrir_encerrar.py` (encerramento): GET em coleta mostra "Novas respostas deixarão de ser aceitas", Participações preservadas e "não há reabertura"; GET em preparação, nunca aberta expirada ou encerrada → 409 explicativo sem `<form>`; POST → 302 `aviso=coleta-encerrada`, `encerrada_em` gravado, forma explícita; POST repetido → `aviso=ja-encerrada`; POST em nunca aberta → 409 sem gravação; Participações existentes intactas; `iniciar_participacao` da 005 recusado depois.
- [X] T033 [US4] Implementar `encerrar` em `trajetoria/acompanhamento/gestao/views.py`: GET só confirma EM COLETA; POST chama sempre `operacoes.encerrar`; `CAMPANHA_NUNCA_ABERTA` → 409 em `conflito.html`; `JA_ENCERRADA` → aviso; sucesso → `?aviso=coleta-encerrada`. Template `trajetoria/acompanhamento/templates/acompanhamento/gestao/confirmar_encerramento.html`. Depende de T021, T032 RED.
- [X] T034 [US4] Registrar `campanhas/<uuid:campanha>/encerrar/` em `trajetoria/acompanhamento/urls.py` e ligar "Encerrar coleta" no `_painel.html`. Depende de T033.
- [X] T035 [US4] Executar GREEN de T032 e regressão de `tests/acompanhamento/` e `tests/participacao/`.

## Fase 8 — US5: recusa a quem não gere, em toda rota real (P1; risco: vazamento) (2 tasks)

Teste independente: CSAEG, sem vínculo, sem operador, vínculo revogado e modo desligado nunca expõem nem gravam em nenhuma rota de gestão.

- [X] T036 [US5] Completar `tests/acompanhamento/test_gestao_acesso.py` com testes por comportamento sobre **todas** as rotas de gestão descobertas pelo marcador `gestao` em `acompanhamento.urls` (sem lista fixa nem contagem), GET e POST: CSAEG Vitória e sem vínculo → 403 sem nome de Campanha e sem gravação (contagem de Campanhas e `aberta_em`/`encerrada_em` inalterados); sem operador → 302; revogar o vínculo CPAEG entre GET e POST → 403 no POST; modo desligado → 404; métodos além de GET/POST → 405; lista e detalhe continuam 405 em POST; CSAEG não vê "Nova Campanha" nem o painel.
- [X] T037 [US5] Executar GREEN de T036; corrigir somente a barreira ou o registro de rotas se algo falhar, sem afrouxar o teste.

## Fase 9 — Acabamento e transversais (6 tasks)

- [X] T038 [P] Escrever e passar `tests/acompanhamento/test_gestao_acessibilidade.py` no padrão da suíte de acessibilidade da 011/editor: rótulos associados, `aria-describedby`/`aria-invalid` nos erros, resumo de erros focável, botões e links acessíveis por teclado, `lang`, títulos únicos nas quatro telas novas.
- [X] T039 [P] Escrever e passar `tests/acompanhamento/test_gestao_fronteiras.py`: varrer `trajetoria/acompanhamento/gestao/` e templates `acompanhamento/gestao/` para garantir ausência de `publicar`, `definir_criterios`, `remover_campanha`, de qualquer registro de autoria (campo, log ou mensagem com o operador; FR-027) e de nomes de campos de critério (`ano_minimo`, `ano_maximo`, `unidades`, `niveis`, `modalidades`, `formas_oferta`) como entrada de formulário; `makemigrations --check --dry-run` sem mudanças.
- [X] T040 Aplicar notas "*(Revisado pela 017 — interpretação C1 restrita à demonstração; DP-402 aberta)*" em `specs/004-campanhas-populacao-elegivel/spec.md` (FR-056 e DP-402), `specs/010-governanca-papeis-escopos/spec.md` (FR-033, FR-073), `specs/011-acompanhamento-operacional-coleta/spec.md` (FR-001, FR-016, FR-100 e rótulo de situação); atualizar docstrings de `trajetoria/governanca/regras.py` e `trajetoria/acompanhamento/acesso.py` e `trajetoria/acompanhamento/views.py` (011 continua só GET; gestão no subpacote).
- [X] T041 Executar `uv run pytest` e `uv run ruff check .` (o que o CI exige) e `ruff format --check` só nos arquivos tocados pela 017; todos verdes. Não reformatar arquivos fora da feature.
- [X] T042 Executar o roteiro manual de [quickstart.md](quickstart.md) num banco `trajetoria_demo` recriado, sem encerrar as duas Campanhas abertas do preparo; registrar evidências ao final do quickstart.
- [X] T043 Revisar o diff contra as guardas do topo e a matriz de verificação da spec; marcar o checklist e as tasks concluídas.

## Dependências

```text
T001 ─► Fase 2 (T002–T012) ─► US1 (T013–T018) ─► Painel (T019–T023) ─┬─► US2 (T024–T027)
                                                                     ├─► US3 (T028–T031)
                                                                     └─► US4 (T032–T035)
                                         US1..US4 ─► US5 (T036–T037) ─► Fase 9 (T038–T043)
```

- A Fase 2 bloqueia tudo: sem regra única e barreira não há rota.
- O painel bloqueia US2–US4, porque as ações são ligadas a partir dele.
- US2, US3 e US4 são independentes entre si depois do painel (arquivos de teste e views
  diferentes, mas o mesmo `urls.py` e `_painel.html`: registrar em sequência).
- US5 roda por último porque descobre as rotas pelo marcador e precisa de todas elas.

## Paralelismo

- Fase 2: T002, T003, T004, T005, T006 (testes em arquivos distintos).
- US1: T014 e T015 depois do RED de T013.
- Painel: T020 em paralelo com T019.
- Acabamento: T038 e T039.

## Estratégia

1. **MVP** = Fase 2 + US1: criar Campanha pela interface, com a regra de abertura já
   unificada e a autorização provada.
2. Painel → US2 → US3 → US4: cada uma fecha um passo do ciclo e é demonstrável sozinha.
3. US5 como verificação transversal de vazamento sobre todas as rotas reais.
4. Acabamento: acessibilidade, fronteiras, notas de revisão, roteiro manual.

Total: 43 tasks.


## Resultado final — 2026-10-03

- 43/43 tasks concluídas. Checklist de requisitos conferido, sem editar os marcadores.
- Suíte completa: **2033 passed, 1 deselected** (volume fora da suíte padrão), após as correções do code review.
- `ruff check .` verde; formato verificado só nos arquivos da 017; `manage.py check`: sem ocorrências;
  `makemigrations --check --dry-run`: nenhuma mudança; `git diff --check`: limpo.
- Evidências de demonstração e ajustes de formatação: [quickstart](quickstart.md).
- Nenhum hook registrado. Alterações mantidas neste worktree; nenhuma alteração no trabalho
  da 016, no banco original ou nos modelos de domínio.
