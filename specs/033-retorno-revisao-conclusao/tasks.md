# Tasks: Retorno à conclusão depois de revisar

**Input**: [spec.md](spec.md), [plan.md](plan.md). Spec e A1 a A5 aprovadas em 2026-10-12.

- [ ] T001 Mensagens: `AVISOS["caminho"]` (informação), `AVISOS["revisada"]` (sucesso), rótulo
  "Salvar e voltar à conclusão" e linha "Parte X · revisando suas respostas" em
  `trajetoria/interface/mensagens.py` e `apresentacao.py` (FR-002, FR-006, FR-007)
- [ ] T002 `concluir_view`: links da revisão com `?revisao=1`; confirmação `revisada` só com a
  Seção no percurso e com Resposta gravada (FR-001, FR-007)
- [ ] T003 `secao` (GET) e `_tela_da_secao`: modo revisão pela query ou pelo envio pendente
  restaurado; campo oculto, rótulo, linha da parte, aviso `caminho` e anterior com marcador
  (FR-002, FR-003, FR-006, FR-010)
- [ ] T004 `_salvar`: marcador do POST; erro de forma e pendência reapresentados com o
  marcador; destino pelo `_destino_da_revisao` (FR-004, FR-005, FR-008, FR-009)
- [ ] T005 Templates `secao.html` e `conclusao.html` (FR-001, FR-002, FR-007)
- [ ] T006 Testes por requisição em `tests/interface/test_interface_revisao.py` para US1 a
  US4 e as bordas (FR-012); nota no teste da conclusão que verifica o `href` da revisão
- [ ] T007 Verificações do CI: `ruff check .`, `manage.py check`, `makemigrations --check
  --dry-run`, `pytest` (SC-004, SC-005)
- [ ] T008 Validação manual na demonstração (navegador do app, 375×812): US1.2 e US2.1/US2.2
  com Ana; registrar em `validacao.md`
