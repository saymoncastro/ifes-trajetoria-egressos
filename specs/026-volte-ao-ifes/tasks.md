# Tasks: Volte ao Ifes — o egresso se oferece para contribuir

**Input**: [spec.md](spec.md), [plan.md](plan.md), [protótipos](prototipo/index.html)

**Formato**: `[ID] [P?] [História] Descrição`. `[P]` pode correr em paralelo (arquivos
diferentes, sem dependência). Testes primeiro: cada teste é escrito e falha antes da
implementação correspondente.

## Fase 0 — Portão

- [x] **T001** Confirmar a autorização de implementação no roadmap (nova revisão) e na spec.
  **Sem isso, nenhuma tarefa abaixo começa.** Registrar se o Checkpoint 1 continua não
  aplicado e o que a autorização abrange (só demonstração).
  - **Feito em 2026-10-09.** O solicitante autorizou a implementação **só na demonstração**,
    em branch e PR próprios, seguindo spec, plan e tasks (roadmap, revisão 10; spec,
    Status). O Checkpoint 1 continua **NÃO APLICADO** e ocorre depois da implementação.
    D4 e D5 continuam `DECISÃO PENDENTE`. A implementação da 029 tem autorização separada.

## Fase 1 — Base

- [x] **T002** [P] Testes de regras sem banco em `tests/portal/test_contribuicao_regras.py`:
  formas válidas, tamanhos, e-mail inválido, situação derivada (enviada, contato registrado,
  retirada), neutralização de fórmulas no CSV.
- [x] **T003** Modelo `Manifestacao` em `trajetoria/portal/models.py` e migração
  `0002_manifestacao.py` (aditiva), com as restrições do plan (forma, tamanhos, par do
  contato, unicidade parcial).
- [x] **T004** [P] `portal/contribuicao/regras.py` (formas, situação, validação, usando
  `contato/endereco.py`) e `portal/contribuicao/planilha.py` (desvio: ver `validacao.md`), até o T002 passar.
- [x] **T005** [P] `portal/contribuicao/governanca.py`: `pode_receber_contribuicoes` e escopo
  (CPAEG institucional; CSAEG por unidade).
- [x] **T006** [P] `portal/contribuicao/mensagens.py`: textos provisórios, formas e
  `VERSAO_DA_CIENCIA`, verificados contra o vocabulário vedado.
- [x] **T007** Testes de gravação em `tests/portal/test_contribuicao_egresso.py` (parte
  "operações"): Conclusão de outra Pessoa, Formação Declarada fora, unicidade com dois
  envios, versão da ciência, unidade copiada, retirada, contato uma vez e só no escopo.
- [x] **T008** `portal/contribuicao/operacoes.py` (registrar, retirar, registrar contato) e
  `consultas.py`, até o T007 passar.

## Fase 2 — US1: oferecer uma contribuição

- [x] **T009** [US1] Testes do fluxo: três telas; formação única pré-selecionada; erro de
  e-mail mantém as escolhas; sem Conclusão dá 404; resultado mostra unidade e o que acontece
  depois.
- [x] **T010** [US1] `formularios.py`, `views_egresso.py` (`/contribuir/`,
  `/contribuir/confirmar/`, `/contribuicoes/<uuid>/`) e templates em
  `portal/templates/portal/contribuicao/`, conforme os protótipos e1 a e4.
- [x] **T011** [US1] Rotas em `portal/urls.py`; Portal desligado sem as rotas (teste).

## Fase 3 — US2: ver e retirar

- [x] **T012** [US2] Testes: lista da própria Pessoa com situação e data do contato;
  manifestação de outra Pessoa dá 404; retirada com confirmação; retirada some da lista da
  unidade.
- [x] **T013** [US2] `/contribuicoes/` e `/contribuicoes/<uuid>/retirar/`, conforme os
  protótipos e5 e e6.

## Fase 4 — US3: a unidade recebe

- [x] **T014** [US3] Testes em `tests/portal/test_contribuicao_unidade.py`: escopo CSAEG,
  CPAEG, recusa sem vínculo, registrar contato (uma vez, só ativa, só no escopo), CSV só das
  ativas e sem CPF nem nascimento.
- [x] **T015** [US3] `views_unidade.py`: `/curadoria/contribuicoes/`,
  `/curadoria/contribuicoes/exportar.csv` e `/curadoria/contribuicoes/<uuid>/contato/`, com a
  escolha de operador da 025, conforme os protótipos u1 e u2.
- [x] **T016** [P] [US3] `demonstracao.py`: duas manifestações fictícias pelo sinal
  `cenario_preparado`.

## Fase 5 — Início e navegação

- [x] **T017** Testes revisados em `tests/portal/test_inicio.py` e
  `tests/portal/test_navegacao.py`: bloco depois de Oportunidades e antes do convite; ausente
  sem Conclusão; item "Contribuir" na navegação; convite continua por último.
- [x] **T018** Bloco "Contribuir com o Ifes" em `portal/inicio.py` e no template do Início;
  item na navegação em `portal/contexto.py`. Medir o orçamento de 200 px a 375 px e a
  navegação a 320 px com fonte a 200% (plan, R9 e R10).

## Fase 6 — Fronteira e revisões

- [x] **T019** Testes em `tests/portal/test_contribuicao_fronteira.py` e revisão de
  `tests/portal/test_fronteiras.py`: dois modelos no `portal`, sem FK; migração aditiva;
  núcleo sem menção ao Portal; `ContatoDaPessoa` inalterado ao contribuir; política de
  convites (`contato/politica.py`) ignora o e-mail da contribuição; analítico e exportações
  sem a Manifestação; escritas só nas três operações.
- [x] **T020** Notas de "Requisitos revisados" na 024 (FR-016, FR-029, navegação) e na 025,
  sem apagar o histórico.

## Fase 7 — Entrega

- [x] **T021** Verificações do CI: `ruff check .`, `manage.py check`,
  `makemigrations --check --dry-run`, suíte completa.
- [x] **T022** Capturas e medidas do percurso real (egresso a 375×812 e 1440×900; unidade a
  1280×720) comparadas com os protótipos; roteiro de teclado. *(Roteiro manual com teclado
  pendente; ver `validacao.md`.)*
- [x] **T023** `validacao.md` da 026 com resultados, desvios e decisões pendentes.
- [x] **T024** Sequência com a 029 (plan, "Sequência com a 029"): atualizar a seção "Como
  você participa" do protótipo da 029 e o P-01 do bloco P para incluir "contribuir", em PR
  próprio.

## Dependências

- T001 antes de tudo.
- T002 → T004; T003 → T007 → T008; T005, T006 em paralelo com T003.
- Fase 2 depende de T008; Fase 3 de T010; Fase 4 de T008 e T005; Fase 5 de T010.
- Fase 6 em paralelo com as Fases 3 a 5, depois de T003.
- Fase 7 por último.
