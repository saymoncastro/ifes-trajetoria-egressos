---

description: "Tasks da Feature 003 — Migração semântica do instrumento institucional vigente"
---

# Tasks: Migração semântica do instrumento institucional vigente

**Input**: Design documents from `specs/003-migracao-semantica-instrumento/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/materializacao.md](contracts/materializacao.md),
[quickstart.md](quickstart.md)

**Stack**: a da 002 (Python 3.13, Django 5.2 LTS, PostgreSQL 16+, uv, pytest +
pytest-django, ruff). Nenhuma dependência, modelo, migração ou app novo.

**Tests**: obrigatórios (Princípio XXVI: versionamento, preservação histórica,
condicionais). Testes antes da implementação. Quando a história só verifica conteúdo já
declarado em tarefa anterior (US3, US5, US6, US7, US9), os testes podem passar de
imediato; se falharem, a correção é em `trajetoria/formulario_2024/declaracao.py`, nunca
no teste nem no manifesto, a não ser que o manifesto contradiga a Matriz da spec.

**Organization**: tarefas por história. `declaracao.py`, `materializacao.py`,
`formulario_2024_esperado.py` e cada arquivo de teste são compartilhados entre histórias:
tarefas no mesmo arquivo são sequenciais.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente).
- **[Story]**: história da spec (US1–US9).

## Convenções para todas as tarefas

- **Fonte executável única**: `trajetoria/formulario_2024/declaracao.py`. O inventário
  (`docs/referencias/formulario-egresso-ifes-2024-inventario.md`) é referência
  documental: é transcrito à mão para a declaração e lido pelos testes só como texto
  bruto. Nenhum parser de Markdown, fixture ou geração a partir dele (research R10).
- **Textos exatos**: copiar do inventário caractere a caractere (aspas retas `"`,
  "auxilio", "técnico científicos", "Micro empresa", "etc)", espaçamento do título de
  S5). Única correção: rótulo final de Q52–Q54 = "Concordo totalmente" (E-08). Ausência é
  `None`, nunca `""` (R8).
- **Escrita só pelas operações da 002**, chamadas como `op.<função>` após `from
  trajetoria.instrumento import operacoes as op` (permite monkeypatch nos testes). Nada de
  `Model.objects.create`, `bulk_create`, `update` ou SQL.
- **Não alterar**: `trajetoria/instrumento/`, `trajetoria/academico/`,
  `trajetoria/fonte_academica/`, `config/`, `pyproject.toml`, `.github/`, e os testes das
  Features 001 e 002 (`tests/test_*.py`, `tests/conftest.py`, `tests/fontes_de_teste.py`,
  `tests/instrumento/conftest.py`, `tests/instrumento/construcao.py`,
  `tests/instrumento/test_instrumento_*.py`). Se alguma tarefa parecer exigir mudança
  ali, **parar** e demonstrar o caso (linha da Matriz, por que a 002 não basta, menor
  ajuste) antes de prosseguir.
- Testes de banco usam `pytestmark = pytest.mark.django_db`. Importações de auxiliares:
  `from tests.instrumento.construcao import percursos_de_secoes` e `from
  tests.instrumento.formulario_2024_esperado import …` (fixtures importadas pelo nome no
  módulo de teste).
- Verificações tabulares acumulam as diferenças numa lista e terminam com `assert
  diferencas == []`, para que uma falha mostre todas as linhas divergentes. Sem snapshot
  monolítico.

## Limites desta lista (não criar)

- Modelo, campo, migração, app Django, `apps.py`, admin, views, URLs, templates, API,
  comando de gestão.
- `PerguntaLegada`, `MapeamentoMigracao`, `Baseline`, `HistoricoMigracao` ou campo
  `q_number`/`legacy_id`; enumeração das categorias da Matriz.
- Parser de Markdown, DSL, YAML/JSON, importador, framework de seed.
- Diff engine, merge, reconciliação, reparo automático, advisory lock.
- Catálogo de cursos ou campi; vínculo de Opção com Curso ou Conclusão Acadêmica.
- Flag ou comportamento especial para as 17 candidatas; ocultação; preenchimento
  automático.
- Condição de exibição (Q6); atributo de momento de regra (`AFTER_QUESTION`,
  `END_OF_SECTION`, `IMMEDIATE`) ou prioridade entre regras; execução da jornada.
- Chamada a `op.publicar` em código de produção.
- Campanha, Participação, Resposta, autenticação, integração acadêmica.

---

## Phase 1: Setup

**Purpose**: pacote Python vazio, que não é app Django.

- [X] T001 Criar `trajetoria/formulario_2024/__init__.py` com docstring "Baseline do
  Formulário Egresso Ifes 2024 (specs/003-migracao-semantica-instrumento). Pacote Python,
  não app Django: sem modelos, migrações nem comandos." e nenhum código ainda. **Não**
  criar `apps.py` nem alterar `INSTALLED_APPS`. Verificar com `uv run python manage.py
  check`.

**Checkpoint**: `manage.py check` sem erros; `trajetoria.formulario_2024` importável.

---

## Phase 2: Foundational

**Purpose**: tipos da declaração e manifesto de expectativas, usados por todas as
histórias.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T002 [P] Criar `trajetoria/formulario_2024/declaracao.py` só com a estrutura
  (conteúdo nas histórias), conforme [data-model](data-model.md#declaração-em-código-não-persistida):
  - docstring: fonte executável única da baseline; chaves `S`/`Q` só para
    rastreabilidade, nunca persistidas (FR-012); o inventário é a referência transcrita;
  - `from trajetoria.instrumento.conteudo import Escala`, `from
    trajetoria.instrumento.models import TipoPergunta`, `from
    trajetoria.instrumento.operacoes import FINALIZAR, Finalizar`;
  - `@dataclass(frozen=True) class PerguntaDeclarada`: `chave: str`, `tipo:
    TipoPergunta`, `texto: str`, `obrigatoria: bool`, `texto_explicativo: str | None =
    None`, `opcoes: tuple[str, ...] = ()`, `complemento: str | None = None`, `escala:
    Escala | None = None`, `regras: tuple[tuple[str, str | Finalizar], ...] = ()`;
  - `@dataclass(frozen=True) class SecaoDeclarada`: `chave: str`, `titulo: str | None`,
    `texto: str | None`, `perguntas: tuple[PerguntaDeclarada, ...]`, `encaminhamento:
    str | None = None`;
  - constantes `NOME_PESQUISA = "Pesquisa Institucional de Egressos"` e `DESIGNACAO =
    "Formulário Egresso Ifes 2024 — referência migrada"` (travessão U+2014);
  - `TITULO = TEXTO_ABERTURA = TEXTO_ENCERRAMENTO = TEXTO_TERMOS = None` e `SECOES:
    tuple[SecaoDeclarada, ...] = ()` como marcadores provisórios, preenchidos em US2.
  - Sem validação própria: a coerência é verificada pelos testes (T010) e pelas
    operações da 002.
- [X] T003 [P] Criar `tests/instrumento/formulario_2024_esperado.py` (não é teste; sem
  `test_` no nome) com:
  - **fixture `inventario_bruto`** (`scope="module"`): lê o inventário como texto,
    remove o marcador de citação no início de linha (`re.sub(r"(?m)^>\s?", "", texto)`)
    e colapsa espaços (`" ".join(texto.split())`). Nada mais: **não** extrai listas,
    perguntas nem tabelas;
  - **fixture `baseline`** (`scope="module"`, recebe `django_db_setup` e
    `django_db_blocker`): dentro de `django_db_blocker.unblock()` e `transaction.atomic()`,
    chama `materializar()`, lê `conteudo_da_versao(resultado.versao)`, marca
    `transaction.set_rollback(True)` e devolve a árvore `ConteudoVersao` (imutável);
  - **função `perguntas_por_chave(conteudo) -> dict[str, ConteudoPergunta]`**: percorre
    Seções e Perguntas na ordem e associa a n-ésima Pergunta a `f"Q{n}"` (FR-009);
  - **função `textos(conteudo) -> list[str]`**: todos os textos não nulos da baseline
    (Versão, Seções, Perguntas, textos explicativos, Opções, rótulos de escala);
  - marcadores provisórios vazios para o manifesto (`SECOES_ESPERADAS`, `ESPERADO`,
    `LISTAS`, `CONTAGENS`, `REGRAS`, `ENCAMINHAMENTOS`, `PERCURSOS`), preenchidos nas
    histórias.

**Checkpoint**: `uv run pytest` continua verde (nenhum teste novo ainda);
`uv run ruff check .` sem erros.

---

## Phase 3: User Story 1 — Materializar a Pesquisa e a Versão RASCUNHO (Priority: P1) 🎯 MVP

**Goal**: `materializar()` cria, numa transação e só pelas operações da 002, a Pesquisa
"Pesquisa Institucional de Egressos" e a Versão "Formulário Egresso Ifes 2024 —
referência migrada" em RASCUNHO, com o conteúdo da declaração.

**Independent Test**: em banco vazio, `materializar()` devolve `criada=True`; existem
exatamente 1 Pesquisa e 1 Versão com nome e designação esperados, em RASCUNHO, sem
`publicada_em` nem `origem`, e nenhuma Pessoa ou Conclusão Acadêmica.

### Tests for User Story 1 ⚠️

- [X] T004 [US1] Criar `tests/instrumento/test_formulario_2024_materializacao.py`
  (`pytestmark = pytest.mark.django_db`) com os cenários de criação (devem falhar antes
  de T005):
  - banco vazio → `materializar()` devolve `Resultado` com `criada is True`;
    `Pesquisa.objects.filter(nome="Pesquisa Institucional de Egressos").count() == 1`;
    a Versão tem `designacao == "Formulário Egresso Ifes 2024 — referência migrada"`,
    `estado == "RASCUNHO"`, `publicada_em is None`, `origem_id is None` (US1-1, US1-2,
    FR-001–FR-005);
  - `forma_da_versao(resultado.versao) == forma_esperada()`;
  - Pesquisa homônima pré-existente (criada por `op.criar_pesquisa`) sem a Versão →
    a Versão é criada nela; continua 1 Pesquisa com o nome (US8-3, FR-031);
  - nenhuma linha em `trajetoria.academico` (Pessoa, Conclusão Acadêmica) antes e depois
    (US1-4, FR-030, FR-041, SC-009);
  - estrutural (FR-040, FR-041, SC-008): `trajetoria.formulario_2024` não está em
    `django.apps.apps.get_app_configs()`; `apps.get_app_config("instrumento").get_models()`
    tem exatamente os 5 modelos da 002; os diretórios `trajetoria/instrumento/migrations`
    e `trajetoria/academico/migrations` contêm só `__init__.py` e `0001_initial.py`; o
    código-fonte de `trajetoria/formulario_2024/*.py` não contém `academico`,
    `fonte_academica` nem `publicar(`;
  - **atomicidade** (FR-032): com `monkeypatch.setattr(op, "definir_regra", falha)`
    — onde `falha` levanta `RuntimeError` — `materializar()` propaga o erro e não
    sobra nenhuma Pesquisa, Versão, Seção, Pergunta ou Opção (contagens zero). Enquanto
    a declaração não tiver regras (antes de US4), usar `op.adicionar_secao` como alvo e
    trocar para `op.definir_regra` em T018;
  - **commit real** (`@pytest.mark.django_db(transaction=True)`): `materializar()` em
    transação confirmada termina sem `IntegrityError` (unicidade adiada da 002).

### Implementation for User Story 1

- [X] T005 [US1] Criar `trajetoria/formulario_2024/materializacao.py` conforme o
  [contrato](contracts/materializacao.md), caminho de **criação**:
  - `@dataclass(frozen=True) class Resultado: versao: Versao; criada: bool`;
  - `class MaterializacaoRecusada(Exception)`; `class BaselineDivergente(
    MaterializacaoRecusada)` com atributo `divergencia: str`; `class PesquisaAmbigua(
    MaterializacaoRecusada)`;
  - `forma_esperada()` (sem banco) e `forma_da_versao(versao)` (a partir de
    `conteudo_da_versao` da 002), produzindo a **mesma** estrutura por valor:
    Versão `(titulo, texto_abertura, texto_encerramento, secoes)`; Seção `(titulo,
    texto, posição do encaminhamento ou None, perguntas)`; Pergunta `(tipo, texto,
    texto_explicativo, obrigatoria, (inicio, fim, rotulo_inicio, rotulo_fim) ou None,
    opcoes)`; Opção `(texto, complemento_textual, regra)` com regra `None`, `"FINALIZAR"`
    ou a posição da Seção de destino. Sem identidades, estado, `publicada_em`, origem,
    designação ou nome da Pesquisa (R6);
  - `_primeira_divergencia(esperada, existente) -> str`: percorre as duas formas em
    paralelo e devolve o primeiro local e o que difere, no formato do contrato
    (`"Versão: texto de abertura difere"`, `"S2: 7 Perguntas, esperadas 8"`,
    `"S9·8: texto explicativo difere"`, `"S12·3·3: regra difere"`). Não é diff completo;
  - `materializar() -> Resultado`, nesta tarefa só com o caminho de criação, tudo em
    `transaction.atomic()`:
    1. Pesquisas com `nome == NOME_PESQUISA`: nenhuma → `op.criar_pesquisa`; uma → usar;
    2. `op.criar_versao(pesquisa, DESIGNACAO)`; `op.alterar_versao(versao,
       titulo=TITULO, texto_abertura=TEXTO_ABERTURA, texto_encerramento=TEXTO_ENCERRAMENTO)`;
    3. para cada `SecaoDeclarada` em `SECOES` (posição = índice + 1):
       `op.adicionar_secao(versao, posicao, titulo=…, texto=…)`; para cada
       `PerguntaDeclarada` (posição = índice + 1): `op.adicionar_pergunta(secao, posicao,
       tipo, texto, obrigatoria=…, texto_explicativo=…, escala=…)`; para cada Opção
       (posição = índice + 1): `op.adicionar_opcao(pergunta, posicao, texto,
       complemento_textual=(texto == complemento))`;
    4. depois de todas as Seções: `op.definir_encaminhamento(secao, secoes[chave])` e
       `op.definir_regra(pergunta, opcoes[texto], secoes[chave] ou op.FINALIZAR)`;
    5. pós-condição: se `forma_da_versao(versao) != forma_esperada()`, levantar
       `BaselineDivergente(_primeira_divergencia(...))` (a transação desfaz tudo);
    6. devolver `Resultado(versao, criada=True)`.
  - **Nunca** chamar `op.publicar`. Nenhuma escrita fora de `op.*`.
- [X] T006 [US1] Em `trajetoria/formulario_2024/__init__.py`, reexportar `materializar`,
  `Resultado`, `MaterializacaoRecusada`, `BaselineDivergente`, `PesquisaAmbigua`,
  `forma_esperada` e `forma_da_versao` (`__all__`). Rodar `uv run pytest
  tests/instrumento/test_formulario_2024_materializacao.py`: T004 passa (com `SECOES`
  ainda vazio, a Versão nasce sem Seções).

**Checkpoint**: criação atômica em RASCUNHO funcionando; nenhuma alteração fora de
`trajetoria/formulario_2024/` e dos testes novos.

---

## Phase 4: User Story 2 — Representar integralmente textos, Seções, Perguntas, Opções, escalas e obrigatoriedades (Priority: P1)

**Goal**: a declaração contém todo o conteúdo do instrumento original, sem as regras de
navegação (US4), e os testes provam a fidelidade com um oráculo independente.

**Independent Test**: `uv run pytest tests/instrumento/test_formulario_2024_fidelidade.py`
passa: 13 Seções, 54 Perguntas na correspondência Qn, 385 Opções em ordem, 11 escalas,
50/4 obrigatoriedades, listas extensas íntegras e todos os textos documentados no
inventário.

### Tests for User Story 2 ⚠️

- [X] T007 [US2] Preencher o manifesto em `tests/instrumento/formulario_2024_esperado.py`,
  transcrevendo **da Matriz e das tabelas da spec** (não da declaração):
  - `SECOES_ESPERADAS`: para S1–S13, `(chave, titulo, tem_texto, quantidade de
    Perguntas)` conforme "Seções da baseline": S1 "Termos e condições" com texto; S2
    "Informações Pessoais" (8); S3 "Informações do curso" (5); S4 "Ensino Médio/Técnico
    Integrado" (1); S5 "Técnico Concomitante / Subsequente /EJA - PROEJA" (2); S6
    "Graduação" (1); S7 "Pós-Graduação" (1, sem texto); S8 "Avaliação" (14); S9 "Egresso
    que trabalha" (11); S10 "Egresso que não trabalha" (1); S11 "Estudo" (3); S12
    "Egresso que estuda" (3); S13 título `None` (3). S2–S13 sem texto;
  - `ESPERADO`: dicionário `Qn → (seção, posição, tipo, obrigatoria, trecho, opcoes)`
    para Q1–Q54, onde `trecho` é um fragmento curto e **distintivo** do texto da
    pergunta, copiado da Matriz (por exemplo Q8 "escolaridade do seu pai", Q9
    "escolaridade da sua mãe", Q20 "gosto por cultura", Q21 "acesso à cultura", Q52
    "mudou a minha vida", Q53 "situação econômica", Q54 "exemplo e inspiração"), que
    nenhuma outra pergunta contém — não o texto inteiro, para o manifesto não virar
    segunda baseline (C1); e `opcoes` é a tupla exata em ordem (perguntas de poucas Opções, copiadas da coluna
    "Opções / escala" da Matriz, incluindo "Outro:"), o nome da lista (`"LISTA_C"`,
    `"LISTA_E"`, `"LISTA_15"`, `"LISTA_17"`, `"LISTA_18"`, `"LISTA_19"`) para Q8, Q9,
    Q11, Q15, Q17, Q18, Q19, ou `()` para texto curto e escala. Tipos: `TEXTO_CURTO` em
    Q3 e Q10; `ESCOLHA_MULTIPLA` em Q26, Q32 e Q47; `ESCALA` em Q20, Q21, Q36, Q42, Q43,
    Q44, Q48, Q50, Q52, Q53, Q54; `ESCOLHA_UNICA` nas demais. Opcionais: só Q6, Q42, Q44
    e Q48;
  - `LISTAS`: `nome → (quantidade, primeiro, último)`: `LISTA_C` (23, "Alegre",
    "Vitória"); `LISTA_E` (17, "Sem instrução", "Não se aplica"); `LISTA_15` (33, "Fiz
    apenas o Ensino Médio", "Técnico em Zootecnia"); `LISTA_17` (47, "Técnico em
    Administração", "Técnico em Treinamento e Instrução de Cães-Guia"); `LISTA_18` (50,
    "EaD - Complementação Pedagógica: Matemática, Física, Biologia e Química",
    "Tecnologia em Sistemas para Internet"); `LISTA_19` (77, "Aperfeiçoamento em Educação
    para o Trânsito", "Mestrado Profissional em Tecnologias Sustentáveis");
  - `CONTAGENS`: Seções 13; Perguntas 54; por tipo `ESCOLHA_UNICA` 38,
    `ESCOLHA_MULTIPLA` 3, `TEXTO_CURTO` 2, `ESCALA` 11; obrigatórias 50, opcionais 4;
    Perguntas com Opções 41; Opções 385; Opções com complemento 3; Perguntas com texto
    explicativo 3; Seções com texto 1; Seções sem título 1;
  - `TEXTOS_EXPLICATIVOS`: Q10 "Exemplo: 2020, 2021, 2022, etc."; Q32 "Obs: Não
    considerar auxilio estudantil como bolsa."; Q48 "Caso não tenha estudado mais deixe
    essa resposta em branco.";
  - `ROTULOS_FINAIS`: "Concordo totalmente" em Q20, Q21, Q36, Q42, Q43, Q44, Q50, Q52,
    Q53, Q54; "concordo totalmente" em Q48.
- [X] T008 [US2] Criar `tests/instrumento/test_formulario_2024_fidelidade.py`
  (`pytestmark = pytest.mark.django_db`; importa as fixtures `baseline` e
  `inventario_bruto`) com os testes de US2 (devem falhar antes de T009–T014):
  - Seções: quantidade, ordem, títulos, presença de texto e quantidade de Perguntas
    conforme `SECOES_ESPERADAS`; S13 com `titulo is None` (FR-017);
  - textos da Versão: `titulo == "Egresso Ifes"`; abertura com 4 parágrafos e
    encerramento com 2 (separados por `"\n\n"`); cada parágrafo, e cada parágrafo de S1
    (2), ocorre em `inventario_bruto` (FR-016, FR-017);
  - **tabela Q1–Q54**: para cada `Qn` de `ESPERADO`, comparar Seção (pela posição da
    Seção), posição, tipo, obrigatoriedade e Opções em ordem; verificar que o texto da
    n-ésima Pergunta contém o `trecho` de Qn e que nenhuma outra Pergunta o contém
    (detecta troca de textos entre perguntas, como Q8 ↔ Q9 ou Q52 ↔ Q53); quando `opcoes` é nome de
    lista, comparar quantidade, primeiro e último com `LISTAS` e verificar que
    `"; ".join(textos das Opções)` ocorre em `inventario_bruto` (detecta perda, troca de
    ordem e alteração de item) (FR-008–FR-011, FR-039, SC-003);
  - Q8 e Q9 com Opções de mesmo texto e identidades distintas (FR-015);
  - `CONTAGENS` conferidas por contagem sobre a árvore (SC-002);
  - todo texto de `textos(baseline)` ocorre em `inventario_bruto`, exceto "Concordo
    totalmente" como rótulo de Q52–Q54 (verificado em US6); a falha lista os textos não
    documentados (FR-007);
  - escalas: as 11 vão de 1 a 5; `rotulo_inicio is None` em todas (não `""`, não
    começa com "Disc") (FR-018, DP-301); rótulos finais conforme `ROTULOS_FINAIS`
    (FR-020);
  - textos explicativos exatamente conforme `TEXTOS_EXPLICATIVOS` e `None` nas demais 51
    (FR-013);
  - complemento textual só na Opção "Outro:" de Q26, Q32 e Q45, que é a última de cada
    uma; nenhuma outra Opção com complemento (FR-014).

### Implementation for User Story 2

Todas em `trajetoria/formulario_2024/declaracao.py`, sequenciais. Transcrever do
inventário conforme a Matriz da spec; `regras` e `encaminhamento` ficam para US4.

- [X] T009 [US2] Textos e listas: `TITULO = "Egresso Ifes"`; `TEXTO_ABERTURA` (os 4
  parágrafos do "Texto de abertura" do inventário, unidos por `"\n\n"`, cada um em uma
  linha lógica, sem o `> `); `TEXTO_TERMOS` (os 2 parágrafos dos "Termos e condições");
  `TEXTO_ENCERRAMENTO = "Este formulário chegou ao fim!\n\nAgradecemos imensamente a
  atenção dispensada e a participação na pesquisa."`; tuplas `LISTA_C` (23), `LISTA_E`
  (17), `LISTA_15` (33), `LISTA_17` (47), `LISTA_18` (50), `LISTA_19` (77), **um item
  por linha**, na ordem do inventário, com comentário de cabeçalho citando a lista do
  inventário. `LISTA_19` não ganha nenhum curso (E-05, DP-310).
- [X] T010 [US2] Declarar S1–S3 (Q1–Q14) em `SECOES`: S1 "Termos e condições" com
  `TEXTO_TERMOS` e Q1; S2 "Informações Pessoais" com Q2–Q9 (Q3 `TEXTO_CURTO`; Q6
  opcional, sem regra; Q8 e Q9 com `LISTA_E`); S3 "Informações do curso" com Q10–Q14
  (Q10 `TEXTO_CURTO` com texto explicativo; Q11 com `LISTA_C`; Q13 com as 3 Opções
  originais).
- [X] T011 [US2] Declarar S4–S7 (Q15–Q19): S4 "Ensino Médio/Técnico Integrado" (Q15,
  `LISTA_15`); S5 "Técnico Concomitante / Subsequente /EJA - PROEJA" (Q16 com
  "Concomitante", "Subsequente", "EJA-PROEJA"; Q17 com `LISTA_17`); S6 "Graduação" (Q18,
  `LISTA_18`); S7 "Pós-Graduação" com `texto=None` (Q19, `LISTA_19`) e comentário `# E-05:
  nota interna "Tem que atualizar a lista de cursos, adicionando doutorado" não migrada`.
- [X] T012 [US2] Declarar S8 "Avaliação" (Q20–Q33): Q20 e Q21 `ESCALA` com
  `Escala(1, 5, None, "Concordo totalmente")` e comentário `# E-09: rótulo inicial não
  confirmado (DP-301)`; Q22–Q25, Q27–Q31, Q33 com "Sim", "Não"; Q26 `ESCOLHA_MULTIPLA`
  com 6 Opções e `complemento="Outro:"`; Q32 `ESCOLHA_MULTIPLA` com 5 Opções,
  `complemento="Outro:"` e texto explicativo com "auxilio" sem acento.
- [X] T013 [US2] Declarar S9 "Egresso que trabalha" (Q34–Q44) e S10 "Egresso que não
  trabalha" (Q45): Q38 e Q39 com as faixas exatamente como no inventário (DP-305); Q40
  com as 5 Opções que citam "campus" (DP-306); Q41 sem texto explicativo e comentário
  `# E-06: nota interna "Verificar lugar dessa pergunta" não migrada`; Q42 e Q44
  `obrigatoria=False`, Q43 `obrigatoria=True` (DP-304); Q45 `ESCOLHA_UNICA` com 3
  Opções e `complemento="Outro:"`.
- [X] T014 [US2] Declarar S11 "Estudo" (Q46, Q47, Q48, nessa ordem), S12 "Egresso que
  estuda" (Q49–Q51) e S13 com `titulo=None` (Q52–Q54): Q47 `ESCOLHA_MULTIPLA` com 8
  Opções; Q48 `obrigatoria=False`, texto explicativo "Caso não tenha estudado mais deixe
  essa resposta em branco." e `Escala(1, 5, None, "concordo totalmente")`; Q50 `ESCALA`;
  Q51 com "Ifes", "Outra Instituição Pública", "Instituição Privada"; Q52–Q54 com
  `Escala(1, 5, None, "Concordo totalmente")` e comentário `# E-08: "Corcordo
  totalmente" corrigido (correção editorial aprovada, FR-021)`. Rodar
  `uv run pytest tests/instrumento/test_formulario_2024_fidelidade.py`: T008 passa.

**Checkpoint**: conteúdo integral materializado e conferido; T004 continua passando.

---

## Phase 5: User Story 3 — Rastrear Q1–Q54 pela Matriz de Migração (Priority: P1)

**Goal**: qualquer Qn é localizável da Matriz à declaração, ao teste e à baseline, sem
nada persistido.

**Independent Test**: os testes de rastreabilidade passam e a revisão de T034 confirma a
Matriz.

### Tests for User Story 3 ⚠️

- [X] T015 [US3] Em `tests/instrumento/test_formulario_2024_fidelidade.py`:
  - a sequência de chaves `Q` da declaração, na ordem de `SECOES`, é `Q1`…`Q54`, e a
    n-ésima Pergunta da baseline (`perguntas_por_chave`) tem o texto da `PerguntaDeclarada`
    de chave `Qn` (FR-009);
  - coerência da declaração (data-model, "Coerência exigida"): chaves `S1`…`S13` e
    `Q1`…`Q54` únicas e em ordem; `complemento` e textos de `regras` pertencem às
    `opcoes` da própria pergunta; destinos de regras e encaminhamentos são chaves de
    Seções posteriores; `escala` só em `ESCALA`; `opcoes` só em escolha;
  - nenhum texto de `textos(baseline)` contém um identificador legado
    (`re.search(r"\b[QS]\d{1,2}\b", texto)` é `None`) (FR-012);
  - os campos de `Pergunta`, `Secao` e `Opcao` da 002 são exatamente os do
    [data-model da 002](../002-pesquisa-versao-instrumento/data-model.md) (nenhum campo
    legado) (FR-012, FR-036).

### Implementation for User Story 3

- Nenhum código novo esperado. Se T015 falhar, corrigir `declaracao.py`.

**Checkpoint**: rastreabilidade Qn ↔ baseline comprovada.

---

## Phase 6: User Story 4 — Representar a navegação semanticamente relevante (Priority: P1)

**Goal**: 10 regras e 7 encaminhamentos da tabela "Navegação da baseline", sem a regra de
Q51 e sem momento de aplicação.

**Independent Test**: `uv run pytest tests/instrumento/test_formulario_2024_navegacao.py`
passa, inclusive os 17 percursos.

### Tests for User Story 4 ⚠️

- [X] T016 [US4] Preencher em `tests/instrumento/formulario_2024_esperado.py`, da tabela
  "Navegação da baseline" da spec:
  - `REGRAS`: `{("Q1", "Sim"): "S2", ("Q1", "Não"): "FINALIZAR", ("Q14", "Ensino
    Médio/Técnico Integrado"): "S4", ("Q14", "Técnico Concomitante/Subsequente/EJA-PROEJA"):
    "S5", ("Q14", "Graduação"): "S6", ("Q14", "Pós-Graduação"): "S7", ("Q33", "Sim"): "S9",
    ("Q33", "Não"): "S10", ("Q46", "Sim"): "S12", ("Q46", "Não"): "S13"}`;
  - `ENCAMINHAMENTOS`: `{"S4": "S8", "S5": "S8", "S6": "S8", "S7": "S8", "S9": "S11",
    "S10": "S11", "S12": "S13"}`;
  - `PERCURSOS`: os 17 percursos no formato de `percursos_de_secoes` (rótulo = título da
    Seção ou `"#13"` para S13; termina em `"FIM"`): `("Termos e condições", "FIM")` e os 16
    da forma `("Termos e condições", "Informações Pessoais", "Informações do curso", <S4|S5|S6|S7>,
    "Avaliação", <"Egresso que trabalha"|"Egresso que não trabalha">, "Estudo",
    ["Egresso que estuda",] "#13", "FIM")`, gerados no manifesto por produto explícito
    dos ramos listados, não a partir da declaração.
- [X] T017 [US4] Criar `tests/instrumento/test_formulario_2024_navegacao.py`
  (`pytestmark = pytest.mark.django_db`; fixture `baseline`) com (devem falhar antes de
  T018):
  - o conjunto de todas as regras da baseline, como `(Qn, texto da Opção) → Sn |
    "FINALIZAR"`, é exatamente `REGRAS` (10; nenhuma outra Pergunta tem regra) (FR-022,
    FR-023);
  - nenhuma Opção de Q51 tem regra (FR-024, E-07);
  - o conjunto de encaminhamentos `Sn → Sm` é exatamente `ENCAMINHAMENTOS`; S1, S2, S3,
    S8, S11 e S13 sem encaminhamento (FR-025);
  - `percursos_de_secoes(baseline) == set(PERCURSOS)` (17); o percurso com Q1 = "Não" é
    `("Termos e condições", "FIM")` (US4-1, US4-6, SC-004);
  - Q46, Q47 e Q48 estão em S11 nas posições 1, 2 e 3; Q46 é a única Pergunta com regras
    que tem outra Pergunta depois de si na mesma Seção; nenhum atributo de momento
    existe em `ConteudoPergunta`/`ConteudoOpcao` (FR-026, DP-302);
  - completude (FR-006, US1-3): **sem** a fixture `baseline` (que desfaz a transação e só
    devolve a árvore), materializar dentro do próprio teste e aplicar
    `verificar_completude` da 002 (`trajetoria.instrumento.regras`) à `Versao`
    persistida: devolve `()`, e a Versão continua em RASCUNHO (U1).
- [X] T018 [US4] Em `tests/instrumento/test_formulario_2024_materializacao.py`, trocar o
  alvo do teste de atomicidade de `op.adicionar_secao` para `op.definir_regra` (última
  etapa), conforme T004.

### Implementation for User Story 4

- [X] T019 [US4] Em `trajetoria/formulario_2024/declaracao.py`, acrescentar:
  - `regras` de Q1 (`("Sim", "S2"), ("Não", FINALIZAR)`), Q14 (4 Opções → S4, S5, S6,
    S7, na ordem), Q33 (`"Sim"` → S9, `"Não"` → S10), Q46 (`"Sim"` → S12, `"Não"` → S13);
  - `encaminhamento` de S4, S5, S6, S7 → `"S8"`; S9, S10 → `"S11"`; S12 → `"S13"`;
  - em Q51, comentário `# E-07: regra "Instituição Privada" → Q52 não reproduzida
    (redundante; FR-024)` e nenhuma regra.
  Rodar `uv run pytest tests/instrumento -k formulario_2024`: T017 e T018 passam.

**Checkpoint**: P1 completo (US1–US4): baseline criada, integral, rastreável e com
navegação. MVP utilizável pela Feature 004.

---

## Phase 7: User Story 5 — Excluir apenas conteúdo editorial interno (Priority: P2)

**Goal**: as duas notas internas não aparecem na baseline, e nada mais foi excluído por
esse motivo.

**Independent Test**: os testes de T020 passam.

### Tests for User Story 5 ⚠️

- [X] T020 [US5] Em `tests/instrumento/test_formulario_2024_fidelidade.py`:
  - nenhum texto de `textos(baseline)` contém "Tem que atualizar a lista de cursos" nem
    "Verificar lugar dessa pergunta" (FR-027, SC-005);
  - S7 com `texto is None`; Q41 com `texto_explicativo is None` e na posição 8 de S9;
  - Q19 com exatamente 77 Opções (nenhum curso acrescentado pela sugestão da nota);
  - Seções com texto: só S1; Perguntas com texto explicativo: só Q10, Q32, Q48 (nada
    mais excluído além de E-05 e E-06) (FR-028).

### Implementation for User Story 5

- Nenhum código novo esperado. Se T020 falhar, corrigir `declaracao.py`.

---

## Phase 8: User Story 6 — Registrar explicitamente a correção editorial (Priority: P2)

**Goal**: "Corcordo totalmente" → "Concordo totalmente" só em Q52–Q54; nenhuma outra
correção.

**Independent Test**: os testes de T021 passam.

### Tests for User Story 6 ⚠️

- [X] T021 [US6] Em `tests/instrumento/test_formulario_2024_fidelidade.py`:
  - rótulo final de Q52, Q53 e Q54 é "Concordo totalmente" (FR-021);
  - "Corcordo" não ocorre em nenhum texto da baseline (SC-005);
  - o inventário (texto bruto) contém "Corcordo totalmente", comprovando que a correção
    é deliberada e não transcrição;
  - Q48 mantém "concordo totalmente" minúsculo (E-10); Q32 mantém "auxilio" (E-19);
  - rótulo final "Concordo totalmente" aparece em exatamente 10 escalas (Q20, Q21, Q36,
    Q42, Q43, Q44, Q50, Q52, Q53, Q54) e "concordo totalmente" em exatamente 1 (Q48); a
    correção não se estende a nenhum outro texto, o que é garantido pela ocorrência
    literal de T008 (U2) (FR-007, FR-021).

### Implementation for User Story 6

- Nenhum código novo esperado.

---

## Phase 9: User Story 7 — Identificar candidatas a contexto institucional sem removê-las (Priority: P2)

**Goal**: as 17 candidatas permanecem perguntas comuns, sem comportamento especial.

**Independent Test**: os testes de T022 passam.

### Tests for User Story 7 ⚠️

- [X] T022 [US7] Em `tests/instrumento/test_formulario_2024_fidelidade.py`:
  - Q3, Q10–Q19, Q22, Q23, Q24, Q27, Q31 e Q32 existem, com tipo, obrigatoriedade e
    Opções do manifesto (já cobertos por T008) e **obrigatórias** como no original;
  - Q3 e Q10 são `TEXTO_CURTO`, sem Opções e sem escala (FR-029; 002, FR-037);
  - nenhuma Pergunta candidata tem regra (as únicas regras são as de `REGRAS`, já
    verificadas em T017): nenhum "perguntar se a fonte não tiver" (FR-029).
  A ausência de efeito na 001 (FR-030, FR-041) já é coberta por T004.

### Implementation for User Story 7

- Nenhum código novo esperado. A classificação "candidata" fica só na Matriz da spec.

---

## Phase 10: User Story 8 — Garantir materialização idempotente (Priority: P2)

**Goal**: reexecução equivalente é no-op; divergente falha sem escrever; nome de Pesquisa
repetido falha.

**Independent Test**: os cenários B, C, ambiguidade e baseline publicada passam.

### Tests for User Story 8 ⚠️

- [X] T023 [US8] Em `tests/instrumento/test_formulario_2024_materializacao.py` (devem
  falhar antes de T024):
  - **B**: duas execuções seguidas → a segunda devolve `criada is False` e a mesma
    Versão; os conjuntos de `id` de Pesquisa, Versão, Seções, Perguntas e Opções são
    iguais; `conteudo_da_versao` antes e depois é igual (`==`); contagens de linhas iguais
    (US8-1, FR-032, SC-007);
  - **C**: para cada alteração feita por operação pública da 002 sobre a baseline já
    materializada — `op.alterar_opcao` (texto de uma Opção de Q11),
    `op.remover_pergunta` (Q54), `op.definir_regra` (Q51 "Ifes" → S13),
    `op.alterar_versao(texto_abertura=...)`, `op.alterar_pergunta(obrigatoria=True)` em
    Q6 — `materializar()` levanta `BaselineDivergente`; `divergencia` aponta o local
    esperado (por exemplo `"S3·2·…"`, `"S13"`, `"S12·3·1"`, `"Versão"`, `"S2·5"`); e
    `conteudo_da_versao` depois da chamada é igual ao de antes da chamada (US8-2,
    FR-033). Parametrizar por alteração;
  - **ambiguidade**: duas Pesquisas "Pesquisa Institucional de Egressos" criadas por
    `op.criar_pesquisa` → `PesquisaAmbigua`; nenhuma Versão criada (US8-4, FR-031);
  - **publicada**: materializar; `op.publicar(versao)` (só no teste); materializar de
    novo → `criada is False`; estado e `publicada_em` inalterados (US8-5);
  - `BaselineDivergente` e `PesquisaAmbigua` são `MaterializacaoRecusada`.

### Implementation for User Story 8

- [X] T024 [US8] Em `trajetoria/formulario_2024/materializacao.py`, completar
  `materializar()` conforme o [contrato](contracts/materializacao.md#efeito):
  - mais de uma Pesquisa com `NOME_PESQUISA` → `PesquisaAmbigua` (mensagem com a
    quantidade, sem identificadores pessoais);
  - Versão com `DESIGNACAO` existente na Pesquisa → comparar `forma_da_versao(existente)`
    com `forma_esperada()`; iguais → `Resultado(existente, criada=False)` sem nenhuma
    escrita; diferentes → `BaselineDivergente(_primeira_divergencia(...))`;
  - nenhum merge, reparo ou escrita parcial; o estado da Versão não entra na comparação.
  Rodar `uv run pytest tests/instrumento -k formulario_2024`.

**Checkpoint**: idempotência e recusa de divergência comprovadas.

---

## Phase 11: User Story 9 — Demonstrar que nenhuma revisão metodológica foi aplicada (Priority: P3)

**Goal**: os problemas metodológicos conhecidos estão preservados e apontam para DPs.

**Independent Test**: os testes de T025 passam.

### Tests for User Story 9 ⚠️

- [X] T025 [US9] Em `tests/instrumento/test_formulario_2024_fidelidade.py`, teste tabular
  "preservações" (cada linha cita a DP):
  - Q38: Opções exatamente "Até 1 salário mínimo", "De 1 até 2,5 salários mínimos", "De
    2,5 até 5,5 salários mínimos", "De 5,5 até 10 salários mínimos", "Acima de 10
    salários mínimos" (DP-305);
  - Q39: inclui "Média empresa/organização (de 100 a 499 colaboradores)" e "Grande
    empresa/organização (acima de 500 colaboradores)" (DP-305);
  - Q40: as 5 Opções contêm "campus" nas 3 primeiras, como no original (DP-306);
  - Q13: as 3 Opções originais (DP-307);
  - Q6: S2 posição 5, logo após Q5, `ESCOLHA_UNICA`, opcional, 4 Opções, sem regra; S2
    sem regras (DP-303);
  - Q42 e Q44 opcionais, Q43 obrigatória (DP-304);
  - Q2 com "Prefiro não responder"; Q4, Q5 e Q7 obrigatórios e sem essa Opção (DP-309);
  - Q26, Q32, Q47 sem qualquer marcação de exclusividade (só texto, complemento e regra
    existem na Opção) (002/DP-005).

### Implementation for User Story 9

- Nenhum código novo esperado.

---

## Phase 12: Polish & Cross-Cutting Concerns

- [X] T026 Conferir manualmente a Matriz de Migração da [spec](spec.md#matriz-de-migração-q1q54)
  contra `trajetoria/formulario_2024/declaracao.py`, linha a linha (Q1–Q54 e E-01–E-19).
  Registrar no fim deste arquivo, em "Notas de implementação", qualquer divergência entre
  inventário e PDF original encontrada (FR-007), sem corrigir silenciosamente.
- [X] T027 [P] Rodar `uv run ruff check .`, `uv run python manage.py check` e
  `uv run python manage.py makemigrations --check --dry-run` (sem mudanças).
- [X] T028 Rodar `uv run pytest` (suíte completa): 001, 002 e 003 verdes.
- [X] T029 [P] Confirmar que nada da 001 e da 002 mudou:
  `git diff --stat main -- trajetoria/instrumento trajetoria/academico
  trajetoria/fonte_academica config pyproject.toml .github tests/conftest.py
  tests/fontes_de_teste.py tests/test_*.py tests/instrumento/conftest.py
  tests/instrumento/construcao.py "tests/instrumento/test_instrumento_*"` vazio.
- [X] T030 Executar os comandos de "Materializar em um ambiente" e "Inspecionar" do
  [quickstart](quickstart.md) num banco local: primeira execução `criada=True`, segunda
  `criada=False`, contagens `EstadoVersao.RASCUNHO 13 54 385`. Ajustar o quickstart só
  se algum comando estiver incorreto.
- [X] T031 Revisão constitucional (Definition of Done): Versão em RASCUNHO; nenhuma
  chamada a `publicar` em produção; nenhum dado pessoal; nenhum item de "Limites desta
  lista" criado; DP-301 a DP-310 e as herdadas continuam abertas e nenhuma virou regra
  implícita. Registrar a revisão pós-implementação no fim de [plan.md](plan.md).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (T001)** → **Foundational (T002, T003)** → histórias → **Polish**.

### User Story Dependencies

- **US1** (T004–T006): depende da Fase 2. Entrega a operação; funciona com `SECOES` vazio.
- **US2** (T007–T014): depende de US1 (a fixture `baseline` chama `materializar()`).
- **US3** (T015): depende de US2.
- **US4** (T016–T019): depende de US2 (Seções e Opções declaradas). T018 depende de T004.
- **US5, US6, US9** (T020, T021, T025): dependem de US2; **US7** (T022) depende de US4. Só testes.
- **US8** (T023–T024): depende de US1 e, para os locais de divergência em Q51 e S13, de
  US2 e US4.
- **Polish**: depois de todas.

### Within Each User Story

- Testes antes da implementação; nas histórias com código novo (US1, US2, US4, US8), eles
  DEVEM falhar primeiro.
- Tarefas no mesmo arquivo são sequenciais.

### Parallel Opportunities

Poucas, porque quase tudo está em três arquivos:

- **Fase 2**: T002 (`declaracao.py`) ∥ T003 (`formulario_2024_esperado.py`).
- **US2**: T007 (manifesto) ∥ T009 (`declaracao.py`); T008 depois de T007.
- **US4**: T016 (manifesto) ∥ T019 (`declaracao.py`).
- **Polish**: T027 ∥ T029.

---

## Parallel Example: Foundational e US2

```bash
# Fase 2 — arquivos independentes:
Task: "T002 tipos e constantes em trajetoria/formulario_2024/declaracao.py"
Task: "T003 fixtures e marcadores em tests/instrumento/formulario_2024_esperado.py"

# US2 — oráculo e declaração escritos de forma independente:
Task: "T007 manifesto transcrito da Matriz em tests/instrumento/formulario_2024_esperado.py"
Task: "T009 textos e listas transcritos do inventário em trajetoria/formulario_2024/declaracao.py"
```

Escrever o manifesto (T007) e a declaração (T009–T014) a partir das fontes documentais,
sem copiar um do outro, é o que torna o oráculo independente (FR-039).

---

## Implementation Strategy

### MVP First

1. Fases 1 e 2.
2. US1: operação de criação atômica em RASCUNHO.
3. US2 e US4: conteúdo integral e navegação → baseline consumível pela Feature 004.
4. **PARAR e VALIDAR** com `uv run pytest`.

### Incremental Delivery

1. Setup + Foundational.
2. P1 (US1–US4): baseline completa, rastreável e com navegação.
3. P2 (US5–US8): verificações editoriais e de candidatas; idempotência e divergência.
4. P3 (US9): preservações metodológicas.
5. Polish e revisão constitucional.

---

## Decisões Pendentes preservadas

DP-301 a DP-310, 002/DP-001 a DP-007 e 001/DP-001, DP-004, DP-007 permanecem **abertas**.
Nenhuma tarefa as resolve. Em particular: rótulo inicial ausente (DP-301); nenhum
momento de regra (DP-302); Q6 sem condição (DP-303); faixas e "campus" preservados
(DP-305, DP-306); candidatas como perguntas comuns (DP-307, DP-308); `publicar` nunca
chamada em produção (002/DP-001).

## Notes

- Total: **31 tarefas**. Código de produção em 3 arquivos novos de
  `trajetoria/formulario_2024/` (`__init__.py`, `declaracao.py`, `materializacao.py`);
  testes em 3 arquivos novos e 1 manifesto em `tests/instrumento/`. Nenhum arquivo
  existente é alterado.
- Tarefas de teste: T004, T007, T008, T015, T016, T017, T018, T020, T021, T022, T023,
  T025 (12). Tarefas de declaração (dados): T002, T009–T014, T019 (8). Código
  comportamental: T005, T006, T024 (3).
- Fazer commit ao fim de cada fase.

## Notas de implementação

Registradas em T026 (2026-10-01):

- **Matriz × declaração**: conferidas Q1–Q54 e E-01–E-19. A conferência é sustentada pelo
  manifesto (transcrito da Matriz, não da declaração) e pelos testes; nenhuma
  divergência entre Matriz e declaração.
- **Texto de abertura com 4 parágrafos, não 3**: o inventário traz a saudação "Prezado(a)
  egresso(a) do Ifes," como bloco próprio. A declaração segue o inventário (FR-007); a
  contagem foi corrigida na spec (FR-016, "Textos da Versão", E-02), em T008/T009 e no
  teste. Não altera conteúdo.
- **PDF original não disponível** neste ambiente (arquivo local não versionado). Nenhuma
  divergência inventário × PDF pôde ser verificada; o inventário segue como fonte
  versionada (FR-007).
- **DP-301 aberta**: o rótulo inicial das escalas não foi confirmado por fonte
  institucional durante a execução; permanece ausente (FR-018, FR-019).
- **Atomicidade (T004/T018)**: antes de a declaração ter Seções, o alvo provisório da
  falha forçada foi `op.alterar_versao` (e não `op.adicionar_secao`, que ainda não era
  chamado); em T018 passou a `op.definir_regra`, como previsto.
- **Fixtures importadas pelo nome** nos testes: os dois arquivos de teste que as usam têm
  `# ruff: noqa: F401, F811`, com justificativa no comentário. Nada foi colocado em
  `tests/instrumento/conftest.py` (002).
- **Listas extensas**: transcritas com um script descartável de formatação (um item por
  linha), fora do repositório. O resultado é código estático; nada lê o Markdown em
  tempo de execução.
- **Quickstart**: saída esperada corrigida para `RASCUNHO 13 54 385`; acrescentada nota
  sobre usar banco descartável, porque a 002 não exclui Versões. Validado em banco
  descartável, criado e removido (T030).
