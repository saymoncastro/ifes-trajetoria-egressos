---

description: "Tasks — Feature 025, Oportunidades curadas do Portal do Egresso"
---

# Tasks: Oportunidades curadas do Portal do Egresso

**Input**: Design documents from `specs/025-oportunidades-curadas-portal/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

> **Situação (2026-10-08): tarefas geradas, implementação NÃO autorizada.**
> - O roadmap (Revisão 4) autoriza o plan e as tasks da 025. Ele **não** autoriza código nem
>   migrações.
> - A T001 é um portão: nenhuma outra tarefa começa sem a autorização explícita no roadmap.
> - O Checkpoint 1 da 024 continua **NÃO APLICADO**.

**Tests**: obrigatórios (Const. XXVI; spec FR-043). A feature toca autorização e escopo por
unidade, uma entidade nova, a fronteira da camada, o dado analítico e a experiência
auditada da 024.

**Organization**: uma fase por história de usuário, na ordem de prioridade da spec (US1–US6).
Cada história termina com a suíte verde.

**Duas proteções pedidas na revisão do plan** valem para todas as fases:

- **P-EXPL.** A explicação cita **todos** os critérios definidos, com o valor satisfeito, em
  **cada** formação citada. Isso inclui os casos curso + nível e curso + nível + unidade
  (contracts/pertinencia.md, "Invariante testável"). Tarefas T018 e T019.
- **P-270.** O destaque do Início cabe no orçamento de 270 px **sem remover** título,
  explicação, unidade responsável, classificação do site nem domínio. Se não couber, a
  implementação para e o caso volta ao solicitante (R9; FR-004; FR-013). Tarefas T026, T027
  e T046.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo, porque os arquivos são diferentes e não há dependência
  pendente.
- **[Story]**: história da spec (US1–US6).

---

## Phase 1: Setup

- [ ] T001 **Portão de autorização.**
  - Confirmar em `docs/roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md` (seção 6, S2) que a antecipação foi **ampliada explicitamente para a implementação** (código e migrações), ou que o Checkpoint 1 foi lido conforme o protocolo e liberou a S2.
  - Sem isso, **parar aqui** e não executar nenhuma outra tarefa.
  - Registrar no PR a revisão do roadmap que autorizou.
- [ ] T002 Registrar a linha de base com a suíte e as verificações verdes:
  - `uv run ruff check .`, `uv run python manage.py check`, `uv run python manage.py makemigrations --check --dry-run` e `uv run pytest`;
  - a duração da suíte;
  - a 375×812 e fonte a 100%, com Ana, Maria e Diego e o banco recém-preparado (sem o bloco, que ainda não existe): a posição vertical (px) do `section.inicio-convite` no `/inicio/`, a altura de `nav.navegacao` nas seis telas com navegação e a posição do `h1` e da síntese.

  Salvar as medidas em `specs/025-oportunidades-curadas-portal/validacao.md`, seção "Linha de base". Elas são a referência do SC-008 e da T046.

---

## Phase 2: Foundational (bloqueia as histórias)

- [ ] T003 Criar o modelo `Oportunidade` em `trajetoria/portal/models.py`, exatamente como em data-model.md. Os campos:
  - `id` UUID PK;
  - `titulo` TextField ("1 a 120 caracteres");
  - `resumo` TextField ("1 a 300 caracteres; texto simples");
  - `categoria` TextField com `choices` `cursos`, `eventos`, `pesquisa_extensao`, `carreira`, `empreendedorismo`, `outras`, rotulados "Cursos e formação continuada", "Eventos", "Pesquisa e extensão", "Carreira e empregabilidade", "Empreendedorismo", "Outras iniciativas";
  - `unidade_responsavel` TextField default `""` ("`""` = Ifes (institucional)");
  - `endereco` TextField;
  - `inicio` e `fim` DateField;
  - `publico_unidades`, `publico_niveis` e `publico_cursos` como `ArrayField(TextField(), null=True)` ("`NULL` = critério ausente; nunca `[]` nem `""`");
  - `publicada_em`, `publicada_por`, `retirada_em` e `retirada_por`, todos nulos.

  As `CheckConstraint` (padrão de `trajetoria/campanha/models.py`):
  - título e resumo não vazios, até 120 e 300 caracteres;
  - categoria na lista;
  - `inicio <= fim`;
  - cada lista `NULL` ou com pelo menos 1 item e sem `""`;
  - `publicada_em` e `publicada_por` juntos; `retirada_em` e `retirada_por` juntos;
  - `retirada_em >= publicada_em` quando ambas existem.

  `Meta.ordering = ["-inicio", "titulo", "id"]`, só por determinismo. Docstring citando a 025, o R1 e a "Camada de relacionamento".
- [ ] T004 Gerar `trajetoria/portal/migrations/0001_oportunidade.py` com `uv run python manage.py makemigrations portal`. Conferir que:
  - a migração é aditiva;
  - não há chave estrangeira para tabelas do núcleo;
  - `makemigrations --check` volta a "No changes detected".
- [ ] T005 [P] Criar `trajetoria/portal/oportunidades/__init__.py` e `trajetoria/portal/oportunidades/regras.py`, com:
  - `Motivo` (Enum) e `OportunidadeRejeitada(violacoes)`, no padrão de `trajetoria/campanha/regras.py`;
  - `estado(oportunidade, hoje) -> Estado` (`RASCUNHO`, `AGENDADA`, `EM_DIVULGACAO`, `ENCERRADA`, `RETIRADA`), pela tabela do data-model e pelas seis regras da spec ("Estados de publicação");
  - `validar_endereco(texto) -> str | Violacao`, conforme o R6: recusa esquema diferente de `https`, ausência de nome de máquina, usuário ou senha, número IP v4 ou v6 (`ipaddress`), espaços e caracteres de controle, e mais de 500 caracteres;
  - `origem_do_site(endereco) -> tuple[str, str]`: ("site do Ifes", domínio) se o nome de máquina é `ifes.edu.br` ou termina em `.ifes.edu.br`; senão ("site externo", domínio). O domínio vai em minúsculas.

  Tudo sem banco e sem relógio.
- [ ] T006 [P] Criar `trajetoria/portal/oportunidades/mensagens.py` com os textos provisórios de contracts/oportunidades-egresso.md e contracts/curadoria.md: introdução, títulos de grupo, estado vazio, linha de origem, modelos de explicação (contracts/pertinencia.md), erros de campo, avisos (`cadastrada`, `editada`, `publicada`, `retirada`), confirmações e recusa. Docstring citando 008/DP-801 e o vocabulário vetado do R14.
- [ ] T007 [P] Criar `trajetoria/portal/oportunidades/governanca.py` (R2), com:
  - `pode_curar_oportunidades(vinculos) -> bool`: verdadeiro se houver CPAEG ou CSAEG ativo;
  - `escopo_de_curadoria(vinculos)`: reutiliza `trajetoria.governanca.regras.escopo_de_acompanhamento`;
  - `administra(escopo, unidade_responsavel) -> bool`: o escopo institucional administra tudo; o escopo por unidade administra só `unidade_responsavel in escopo.unidades` (nunca `""`).

  Docstring explicando por que a regra fica na camada (Complexity Tracking do plan).
- [ ] T008 Criar `trajetoria/portal/oportunidades/operacoes.py`, o único caminho de escrita (data-model, "Operações"), com:
  - `cadastrar(dados, *, operador, escopo, hoje)`;
  - `editar(id, dados, *, operador, escopo, hoje)`;
  - `publicar(id, *, operador, escopo, agora)`;
  - `retirar(id, *, operador, escopo, agora)`.

  Regras:
  - cada uma em `transaction.atomic` com `select_for_update`;
  - revalidar o estado (`estado(..., hoje)`) e `administra`;
  - normalizar o público: lista vazia vira `NULL`;
  - recusar com `OportunidadeRejeitada`. Os motivos mínimos são `TITULO`, `RESUMO`, `CATEGORIA`, `UNIDADE_FORA_DO_ESCOPO`, `ENDERECO`, `PERIODO_INVERTIDO`, `FIM_ANTES_DE_HOJE` (edição de publicada e publicação com fim passado), `ESTADO` (conflito) e `FORA_DO_ESCOPO`;
  - publicar e retirar gravam o momento e o identificador opaco do operador (FR-033);
  - nada mais é gravado.
- [ ] T009 [P] Criar `trajetoria/portal/oportunidades/consultas.py` com:
  - `em_divulgacao(hoje)`: `publicada_em__isnull=False, retirada_em__isnull=True, inicio__lte=hoje, fim__gte=hoje`;
  - `da_curadoria(escopo)`: tudo se institucional, senão `unidade_responsavel__in=escopo.unidades`;
  - `opcoes_de_publico()`: valores distintos, não nulos e ordenados de `ConclusaoAcademica.curso`, `.nivel` e `.unidade`, como escritos (R8);
  - `unidades_responsaveis(escopo)`: para a CPAEG, `""` mais as unidades distintas das Conclusões; para a CSAEG, as unidades do escopo.
- [ ] T010 [P] Pontos neutros no núcleo (contracts/rotas.md). Nenhum deles cita a camada:
  1. em `trajetoria/demonstracao/views.py`, transformar `_DESTINOS` num registro com `registrar_destino(chave: str, endereco: str)`, com o comentário do 011 R13 preservado (destino fechado, nunca do cliente);
  2. criar `trajetoria/demonstracao/sinais.py` com `cenario_preparado = Signal()`;
  3. em `trajetoria/demonstracao/cenario.py`, enviar `cenario_preparado.send(sender=None, data=data_local)` no fim de `preparar()`, dentro da transação.
- [ ] T011 Em `trajetoria/portal/apps.py`, implementar `PortalConfig.ready()`:
  - registrar `registrar_destino("curadoria", "/curadoria/oportunidades/")` só com `settings.TRAJETORIA_PORTAL`;
  - conectar o receptor de `trajetoria/portal/oportunidades/demonstracao.py` a `cenario_preparado` (R3, R4).
- [ ] T012 Revisar os testes de fronteira da 024 em `tests/portal/test_fronteiras.py` (R1):
  - `test_portal_sem_modelo_nem_migracao` passa a ser `test_portal_um_modelo_sem_fk_para_o_nucleo`: exatamente um modelo (`Oportunidade`); migrações do app só com `CreateModel`/`AddField`/`AddConstraint`; nenhum `ForeignKey`;
  - `test_nucleo_nao_menciona_o_portal` continua igual e precisa passar com os pontos da T010;
  - incluir `Oportunidade` em `CONTADOS` de `tests/portal/construcao.py`.
- [ ] T013 [P] Testes puros em `tests/portal/test_oportunidades_regras.py`:
  - `estado` nos cinco estados e nas seis regras: a data nunca autoriza sozinha; início e fim inclusivos em D e D+1; a retirada prevalece; Rascunho retirado; momentos coerentes;
  - `validar_endereco` com casos aceitos (`https://www.ifes.edu.br/x`, `https://oportunidades.example/a?b=1`) e recusados (`http://…`, `https://user:pw@host/`, `https://10.0.0.1/`, `https://[::1]/`, com espaço, 501 caracteres, `javascript:`);
  - `origem_do_site` para `ifes.edu.br`, `cursos.ifes.edu.br`, `ifes.edu.br.evil.example` (externo) e `www.gov.br` (externo).

**Checkpoint**: modelo, migração, regras, operações e pontos neutros prontos; suíte verde.

---

## Phase 3: User Story 1 — Encontrar oportunidades pertinentes e entender por que aparecem (P1) 🎯 MVP

**Goal**: o egresso vê, sem preencher nada, as oportunidades pertinentes à formação registrada,
com explicação e link oficial, na página e no Início.

**Independent Test**: com o catálogo fictício, a lista de cada persona coincide com o oráculo
de contracts/pertinencia.md (SC-002).

- [ ] T014 [P] [US1] Criar `trajetoria/portal/oportunidades/demonstracao.py`, com:
  - o catálogo O1–O10 de contracts/pertinencia.md, com datas relativas a `D` (a `data` recebida do sinal), `uuid5` fixos e endereços em `https://oportunidades.example/…`;
  - a carga idempotente pelas operações da T008: O1–O8 publicados com o operador da tabela; O9 publicado e retirado; O10 em rascunho;
  - o receptor `carregar_catalogo(sender, data, **kwargs)`.
- [ ] T015 [US1] Criar `trajetoria/portal/oportunidades/pertinencia.py` com `pertinentes(oportunidades, conclusoes) -> list[Item]`, pura (R7; contracts/pertinencia.md, "Regra"):
  - cada critério definido é testado **na mesma Conclusão**, por igualdade exata;
  - `NULL` não satisfaz;
  - grupos `formacao` e `todos`;
  - formações citadas na ordem recebida;
  - ordem: grupo, `inicio` decrescente, `titulo`, `id`.

  O `Item` traz a oportunidade, o grupo, as formações, a explicação e a origem
  (`origem_do_site` e a unidade responsável).
- [ ] T016 [US1] Em `trajetoria/portal/oportunidades/pertinencia.py`, implementar `explicacao(oportunidade, formacoes)` pelos modelos **revisados** de contracts/pertinencia.md:
  - cada formação é "{curso}", depois ", formação de {nível}" se houver critério de nível, depois " na unidade {unidade}" se houver critério de unidade, depois "({unidade}, {ano})" sem critério de unidade ou "({ano})" com ele;
  - fragmentos ausentes são omitidos ("uma formação" sem curso);
  - várias formações vão unidas por vírgula e "e";
  - sem público: "Aberta a todos os egressos do Ifes.".

  Nenhum dado além da Conclusão; nenhum texto livre do operador.
- [ ] T017 [P] [US1] Testes da regra em `tests/portal/test_oportunidades_pertinencia.py`:
  - sem público;
  - cada critério sozinho;
  - combinações;
  - **critérios não combinados entre Conclusões diferentes** (Pós-graduação no Cefor e Graduação na Serra × público Pós-graduação ∧ Serra → não aparece);
  - várias formações satisfazendo → aparece uma vez e cita todas na ordem;
  - valor ausente;
  - igualdade exata, sem caixa nem espaços;
  - **duas grafias** ("Tecnologia em Análise e Desenvolvimento de Sistemas" × "Análise e Desenvolvimento de Sistemas", com Conclusões de teste) alcançadas só quando as duas estão marcadas;
  - ordem e determinismo: a mesma entrada dá a mesma saída.
- [ ] T018 [P] [US1] **P-EXPL** — testes da explicação em `tests/portal/test_oportunidades_pertinencia.py`:
  - uma tabela parametrizada com os sete casos de contracts/pertinencia.md (curso; nível; unidade; curso + nível; curso + unidade; curso + nível + unidade; nível + unidade), com o texto esperado literal;
  - um teste de **invariante** que gera os públicos possíveis sobre as Conclusões da demonstração e verifica que, para toda oportunidade com público, o valor satisfeito de **cada** critério definido aparece literalmente na explicação de **cada** formação citada;
  - um caso que falharia com a versão anterior do contrato: público curso = {TADS} ∧ nível = {Graduação} → a explicação contém "formação de Graduação".
- [ ] T019 [P] [US1] **P-EXPL** — teste de vocabulário em `tests/portal/test_oportunidades_pertinencia.py`: nenhuma explicação contém "recomend", "selecionad", "não perca", "vaga", números de outros egressos, nome da Pessoa, nem dado de Resposta ou de Formação Declarada.
- [ ] T020 [US1] Criar `trajetoria/portal/oportunidades/views_egresso.py` com a view `oportunidades(request)`: `GET`, `never_cache`, `require_GET`. Respostas:
  - sem Pessoa: `/entrar/` ou `/entrar/?aviso=sessao`;
  - declarante: `/declaracao/`;
  - Pessoa sem Conclusão: 303 para `/inicio/`;
  - caso contrário, renderiza `portal/oportunidades.html` com os grupos do `pertinentes(em_divulgacao(timezone.localdate()), pessoa.conclusoes.all())`.

  Rota `oportunidades/` em `trajetoria/portal/urls.py`.
- [ ] T021 [P] [US1] Criar `trajetoria/portal/templates/portal/_oportunidade.html` (item compartilhado) e `trajetoria/portal/templates/portal/oportunidades.html`, conforme contracts/oportunidades-egresso.md:
  - `h1`, introdução e os dois `h2` (cada um omitido quando vazio), com `ul.lista-simples`;
  - cada item com categoria, `h3` com o link (`rel="noreferrer"`, nome acessível com "— {site do Ifes|site externo}: {domínio}"), resumo, explicação e a linha "Oferecida pela unidade X" ou "Oferecida pelo Ifes", com "· {origem}: {domínio}";
  - **sem** datas de divulgação, contagem, imagem, grade nem JavaScript;
  - estado vazio com "Voltar ao Início";
  - CSS só com tokens da 015, em `trajetoria/portal/templates/portal/oportunidades.css`, incluído inline.
- [ ] T022 [US1] Navegação em `trajetoria/portal/contexto.py`:
  - acrescentar "Oportunidades" (`/oportunidades/`) entre "Minha trajetória" e "Pesquisa", com a mesma condição `elegivel(pessoa)`, calculada **uma vez** para os dois itens;
  - incluir `/oportunidades/` em `_TELAS_COM_NAVEGACAO`;
  - rótulo em `trajetoria/portal/mensagens.py`;
  - o template `portal/oportunidades.html` opta pela navegação com o bloco `navegacao`.
- [ ] T023 [US1] Largura estável da navegação (R10; A5):
  - em `trajetoria/interface/templates/interface/_navegacao.html`, acrescentar `data-rotulo="{{ item.rotulo }}"` a cada link;
  - em `trajetoria/interface/templates/interface/jornada.css`, reservar a largura do negrito com `.navegacao a::after { content: attr(data-rotulo); display: block; height: 0; overflow: hidden; visibility: hidden; font-weight: <peso do item atual>; }`.

  Sem tokens novos, sem JavaScript, alvos de 44 px preservados.
- [ ] T024 [US1] Bloco do Início em `trajetoria/portal/inicio.py`:
  - `montar_inicio` ganha `oportunidades = {"destaque": Item, "total": n}`, ou `None` quando a lista é vazia;
  - usa as mesmas funções da página;
  - não lê Resposta nem contato;
  - mantém a falha isolada: uma exceção registrada em log omite só o bloco.
- [ ] T025 [US1] Em `trajetoria/portal/templates/portal/inicio.html`, inserir `section.inicio-oportunidades` **depois** de "O que você pode fazer" e **antes** do convite, conforme contracts/oportunidades-egresso.md:
  - `h2` "Oportunidades";
  - título como link oficial, explicação e origem completas;
  - "Ver as N oportunidades", ou "Ver a página de Oportunidades" se N = 1.

  O convite fica inalterado.
- [ ] T026 [US1] **P-270** — preparar a compactação do R9 em `trajetoria/portal/templates/portal/inicio.css` como classes **inativas** (`.inicio-oportunidades.compacto-1`, `-2`, `-3`), só com tokens da 015:
  1. `--espaco-1` entre parágrafos;
  2. explicação e origem em `--fonte-5` com `--entrelinha-enunciado`;
  3. explicação e origem num único parágrafo (variante de marcação no template, atrás da mesma classe).

  **Nenhuma** variante pode omitir título, explicação, unidade responsável, classificação do site ou domínio.
- [ ] T027 [P] [US1] **P-270** — testes em `tests/portal/test_oportunidades_inicio.py`:
  - em **toda** variante (padrão e compactas 1–3), o HTML do bloco contém o título, a explicação completa (comparada com o oráculo), "Oferecida pela unidade …" ou "Oferecida pelo Ifes", "site externo" ou "site do Ifes" e o domínio;
  - nenhuma variante tem regra CSS `display: none` nem `visualmente-oculto` aplicada a esses elementos visíveis.
- [ ] T028 [P] [US1] Testes da página em `tests/portal/test_oportunidades_egresso.py`:
  - acessos (Pessoa com e sem Conclusão, declarante, sem sessão e sessão expirada);
  - estrutura (um `h1`, grupos, `h3`, link com `rel="noreferrer"` e nome acessível);
  - **ausência** de datas, contagens e `<script>`;
  - parâmetros ignorados;
  - **nada gravado** (contagens de `tests/portal/construcao.py`);
  - consultas sem `participacao_resposta`, `contato_contatodapessoa` e `declaracao_`;
  - O7–O10 nunca aparecem.
- [ ] T029 [P] [US1] Testes do Início em `tests/portal/test_oportunidades_inicio.py`:
  - ordem dos blocos (reconhecimento < ações < Oportunidades < convite);
  - um único destaque, o primeiro do oráculo;
  - "Ver as N oportunidades";
  - bloco ausente sem itens;
  - convite com o mesmo texto e ação de antes (024 FR-020, revisado).
- [ ] T030 [US1] Revisar os testes da 024 (R11), com comentário de rastreabilidade para a 025 "Requisitos revisados":
  - em `tests/portal/test_inicio.py`, `VEDADOS` passa a valer **fora** de `section.inicio-oportunidades`; `test_pesquisa_so_no_convite` passa a ignorar o bloco;
  - em `tests/portal/test_navegacao.py`, a lista esperada passa a ter cinco itens e `/oportunidades/` entra entre as telas com navegação, com `aria-current`;
  - em `tests/portal/test_fronteiras.py::test_portal_nao_grava`, incluir `/oportunidades/`.
- [ ] T031 [US1] Teste do oráculo em `tests/portal/test_oportunidades_oraculo.py` (SC-002):
  - preparar a demonstração com `D` fixo;
  - para cada persona da tabela de contracts/pertinencia.md, comparar a página (grupos, ordem e explicação literal) e o destaque do Início;
  - acrescentar os casos D+11 (O7 entra) e D+61 (O1 sai), por data de referência.

**Checkpoint**: US1 completa. O egresso encontra e entende oportunidades; a curadoria ainda é
só pelas operações.

---

## Phase 4: User Story 2 — Operador da unidade cadastra e publica (P1)

**Goal**: a CSAEG cadastra, edita e publica oportunidades da própria unidade, com público livre
(DP-2502).

**Independent Test**: o operador B cadastra, edita e publica. Bruno vê a oportunidade e Ana não
(público Vitória), ou os dois veem (sem público).

- [ ] T032 [US2] Criar o decorador `curadoria` em `trajetoria/portal/oportunidades/views_curadoria.py`, no padrão de `trajetoria/acompanhamento/acesso.py::gestao` (contracts/curadoria.md, "Acesso"):
  - `settings.TRAJETORIA_DEMONSTRACAO`, ou 404;
  - `vinculos_do_operador_em_uso`, ou 303 para `/demonstracao/operador/?destino=curadoria`;
  - `pode_curar_oportunidades`, ou `acompanhamento.acesso.recusa` com o texto da recusa;
  - `request.escopo` e `request.atuacao` (`Atuacao` com rótulos).
- [ ] T033 [P] [US2] Criar `trajetoria/portal/oportunidades/formularios.py` com `OportunidadeForm` (base `trajetoria/editor/formularios.py::Formulario`):
  - título `maxlength=120`;
  - resumo `Textarea` `maxlength=300`;
  - categoria `RadioSelect`;
  - unidade responsável `Select` com `unidades_responsaveis(escopo)` ("Ifes (institucional)" só para a CPAEG);
  - endereço `URLInput` com `inputmode=url`;
  - início e fim como datas (`%Y-%m-%d`);
  - três `MultipleChoiceField` com `CheckboxSelectMultiple` (`opcoes_de_publico`) e a ajuda fixa do público.

  O formulário não grava: só a T008 grava.
- [ ] T034 [US2] Views em `trajetoria/portal/oportunidades/views_curadoria.py`:
  - `lista`;
  - `nova` (GET/POST: 422 com erros; 303 para a lista com `?aviso=cadastrada`);
  - `editar` (404 fora do escopo; 409 conflito; 303 `?aviso=editada`);
  - `publicar` (GET com a prévia `_oportunidade.html`, o público em linguagem simples, o período e o domínio completo em destaque, com o aviso de site externo; POST; 303 `?aviso=publicada`).

  Decoradores `@curadoria @require_http_methods @never_cache`. Recusas da T008 mapeadas para erros de campo ou conflito, como em `trajetoria/acompanhamento/gestao/views.py`. Rotas `curadoria/oportunidades/…` em `trajetoria/portal/urls.py`.
- [ ] T035 [P] [US2] Templates em `trajetoria/portal/templates/portal/curadoria/` (`lista.html`, `formulario.html`, `publicar.html`, `conflito.html`), estendendo `acompanhamento/base.html`:
  - tabela com `caption` e `scope`;
  - `editor/_erros.html` e `editor/_campo.html`;
  - `fieldset`/`legend` no público;
  - avisos em `<p role="status">`;
  - sem Django admin, sem editor rico, sem upload.
- [ ] T036 [P] [US2] Testes em `tests/portal/test_oportunidades_curadoria.py`:
  - sem operador → escolha de operador com destino `curadoria`, que volta a `/curadoria/oportunidades/`;
  - operador C → 403;
  - B vê só Vitória;
  - B cadastra (Rascunho, invisível ao egresso), edita e publica (Agendada ou Em divulgação);
  - B com público Serra ou sem público é **aceito** (DP-2502), e um egresso da Serra vê "Oferecida pela unidade Vitória";
  - B com unidade Serra ou `""`, inclusive por POST forjado → erro de campo, nada gravado;
  - cada forma de endereço recusada da T013 → erro de campo;
  - erros com `aria-describedby` e `aria-invalid` e foco no primeiro;
  - prévia de publicação com domínio e aviso de site externo;
  - publicação com fim no passado recusada;
  - `publicada_por` igual ao identificador do operador, que nunca aparece no HTML;
  - CSRF exigido.

**Checkpoint**: US1 e US2 funcionam juntas.

---

## Phase 5: User Story 3 — Retirada e expiração sem trabalho manual (P1)

**Goal**: a oportunidade expira sozinha e pode ser retirada na hora.

**Independent Test**: com data de referência controlada, a oportunidade aparece em D e some em
D+1. Depois de retirada, some imediatamente.

- [ ] T037 [US3] View `retirar` (GET de confirmação com o texto de contracts/curadoria.md; POST; 303 `?aviso=retirada`; 409 conflito; 404 fora do escopo) em `trajetoria/portal/oportunidades/views_curadoria.py`, com o template `trajetoria/portal/templates/portal/curadoria/retirar.html`. Na lista, mostrar a ação "Retirar" só em Rascunho, Agendada e Em divulgação, e "Editar" só nos mesmos estados.
- [ ] T038 [P] [US3] Testes em `tests/portal/test_oportunidades_curadoria.py`:
  - expiração em D e D+1 sem nenhuma ação (SC-005);
  - Agendada invisível até o início;
  - **Rascunho com período em curso invisível**;
  - retirada imediata, com `retirada_por` e `retirada_em`;
  - Rascunho retirado nunca pode ser publicado;
  - edição de publicada com fim antes de hoje recusada, com a mensagem "Para encerrar antes do prazo, retire a oportunidade.";
  - Encerrada e Retirada sem ações;
  - **conflito**: um operador retira e outro confirma publicação ou edição → 409, nada gravado (FR-034).

**Checkpoint**: o ciclo de vida completo está coberto.

---

## Phase 6: User Story 4 — Curadoria institucional (P2)

**Goal**: a CPAEG administra todas as unidades e as oportunidades institucionais.

**Independent Test**: o operador A publica uma oportunidade sem público e outra só para
Pós-graduação. A primeira aparece para todas as personas com Conclusão; a segunda, só para
Maria e Diego.

- [ ] T039 [P] [US4] Testes em `tests/portal/test_oportunidades_curadoria.py`:
  - A vê todas as unidades e as institucionais;
  - A cadastra com "Ifes (institucional)";
  - A edita e retira oportunidade de Vitória, e o registro de retirada identifica A;
  - uma oportunidade de A só para Pós-graduação aparece para Maria e Diego e não para Ana nem Bruno.

  Não há código novo além das fases anteriores. Se algum teste falhar, corrigir na T007 ou na T008.

---

## Phase 7: User Story 5 — Sem oportunidades, o Portal não finge (P2)

**Goal**: o estado vazio é honesto, e o Início não mostra área sem função.

**Independent Test**: sem oportunidades pertinentes em divulgação, o bloco do Início não existe
e a página mostra a frase de estado vazio.

- [ ] T040 [P] [US5] Testes em `tests/portal/test_oportunidades_egresso.py`:
  - catálogo esvaziado (ou só O7–O10) → página com a frase exata de estado vazio, sem "pesquisa", prazo ou cobrança, e com "Voltar ao Início";
  - Início sem `inicio-oportunidades` e sem a palavra "Oportunidade" fora da navegação;
  - o item "Oportunidades" continua na navegação (FR-020).

---

## Phase 8: User Story 6 — A coleta e o núcleo não percebem as Oportunidades (P2)

**Goal**: a camada pode ser desligada, e o dado analítico fica intacto.

**Independent Test**: snapshot e exportações idênticos com e sem oportunidades. Com o Portal
desligado, `/oportunidades/` e `/curadoria/…` dão 404.

- [ ] T041 [P] [US6] Testes em `tests/portal/test_oportunidades_fronteiras.py`:
  - snapshot de uma Campanha encerrada e exportações CSV/XLSX gerados antes e depois de publicar O1–O6: **bytes idênticos** (SC-009);
  - `analitico` e `exportacao` não importam `trajetoria.portal` (AST);
  - nenhuma tabela do núcleo muda de contagem ao cadastrar, editar, publicar ou retirar;
  - o núcleo não cita a camada (já na T012).
- [ ] T042 [P] [US6] Em `tests/portal/test_desabilitado.py`:
  - `/oportunidades/` e `/curadoria/oportunidades/` → 404;
  - a escolha de operador **não** aceita o destino `curadoria`, que cai no padrão `/editor/`;
  - a navegação não existe;
  - o caminho do convite é o mesmo da 024 (SC-010).

**Checkpoint**: todas as histórias completas.

---

## Phase 9: Polish & validação

- [ ] T043 [P] Atualizar `docs/desenvolvimento/ambiente-local.md` (tabela do passo 2.11) com `/oportunidades/` e `/curadoria/oportunidades/` (operadores A e B). Registrar que o `preparar_demonstracao` carrega o catálogo fictício pelo sinal (R4) e que as datas são relativas ao dia do preparo.
- [ ] T044 [P] Notas de revisão:
  - na spec da 024 (FR-016, FR-021, FR-022, FR-023, FR-029), apontando para a 025 "Requisitos revisados";
  - em `specs/024-inicio-egresso-portal/contracts/inicio.md` e `contracts/navegacao.md`, o bloco e o quinto item.
- [ ] T045 Rodar `uv run ruff check .`, `uv run python manage.py check`, `uv run python manage.py makemigrations --check --dry-run` e `uv run pytest`, todos verdes. Registrar os números em `specs/025-oportunidades-curadas-portal/validacao.md`.
- [ ] T046 **P-270 — medida e decisão.** No navegador a 375×812 e fonte a 100%, com o banco recém-preparado:
  - medir a posição do convite com o bloco para Ana, Maria e Diego e comparar com a T002;
  - se algum deslocamento passar de 270 px, ativar as variantes da T026 **em ordem** (1, depois 2, depois 3) até caber, medindo de novo a cada etapa;
  - se a variante 3 ainda passar, **parar**: não remover nenhuma informação; registrar as medidas em `validacao.md` e levar o caso ao solicitante (revisão do FR-021 ou do SC-008);
  - registrar a variante adotada e as medidas.
- [ ] T047 Medidas da navegação (R10; A5) em `validacao.md`:
  - altura de `nav.navegacao` igual nas seis telas com navegação a 375 px e 100%;
  - nenhuma rolagem horizontal de 320 a 1280 px com fonte de 100% a 200%;
  - alvos de 44×44 px;
  - `h1` e síntese do Início acima da dobra a 375×812 (024 SC-004).
- [ ] T048 Executar o [quickstart.md](quickstart.md) completo e registrar capturas a 375×812 em `specs/025-oportunidades-curadas-portal/evidencias/`:
  - Início com o bloco;
  - página de Ana;
  - página de Maria, sem O5;
  - estado vazio;
  - lista da curadoria de B;
  - confirmação de publicação com aviso de site externo.
- [ ] T049 Passada de teclado (página, Início, curadoria) e árvore de acessibilidade, registradas em `validacao.md`. O teste com leitor de tela continua pendente (P4 da 024) e não deve ser declarado como feito.

---

## Dependencies & Execution Order

- **T001 é portão.** Sem autorização registrada, nada começa.
- **Setup (T002)** → **Foundational (T003–T013)** → histórias.
- **US1** (T014–T031) depende da Foundational. É o MVP.
- **US2** (T032–T036) depende da Foundational. A prévia usa o `_oportunidade.html` da T021,
  então convém fazer a US1 antes.
- **US3** (T037–T038) depende da US2 (views e templates da curadoria).
- **US4** (T039) depende da US2.
- **US5** (T040) depende da US1.
- **US6** (T041–T042) depende da Foundational e das rotas da US1 e da US2.
- **Polish** (T043–T049) depois de todas. A T046 depende da T026 e da T002.

### Parallel Opportunities

- Na Foundational: T005, T006, T007, T009, T010 e T013 em paralelo (arquivos diferentes). A
  T008 depende de T005 e T007; a T011, de T010 e T014.
- Na US1: T017, T018 e T019 (testes de pertinência) em paralelo com T021 (templates). T027,
  T028 e T029 depois da T025.
- Na US2: T033 e T035 em paralelo; T036 depois da T034.
- Na Polish: T043 e T044 em paralelo.

### Exemplo (US1)

```text
Em paralelo: T017 + T018 + T019 (tests/portal/test_oportunidades_pertinencia.py — funções
puras) e T021 (templates).
Depois: T020 → T022 → T023 → T024 → T025 → T026, então T027 + T028 + T029 em paralelo, T030 e
T031.
```

## Implementation Strategy

1. **Portão (T001).** Sem autorização, parar.
2. **MVP = Foundational + US1.** O egresso vê o catálogo fictício com explicação correta.
   Validar com o oráculo (T031) e medir o P-270 cedo (antecipar a T046 logo depois da T025).
3. **US2 + US3.** Curadoria e ciclo de vida.
4. **US4 + US5 + US6.** Institucional, estado vazio e fronteiras.
5. **Polish.** Documentação, medidas e evidências.
6. **Commits no padrão do projeto:**
   - `docs(025): …`;
   - `feat(025): …`;
   - PR "Feature 025 — …", com as seções Resumo, Persistência/Modelo, Features anteriores,
     Decisões pendentes e Validação.
