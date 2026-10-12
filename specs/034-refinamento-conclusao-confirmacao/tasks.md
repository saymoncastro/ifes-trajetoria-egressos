# Tasks: Refinamento visual da conclusão e da confirmação

**Input**: [spec.md](spec.md) (revisão 1, aprovada), [plan.md](plan.md). 033 integrada (#69).

- [x] T001 Textos em `trajetoria/interface/mensagens.py` (R8), inclusive o aviso B6 (FR-011)
- [x] T002 `concluir_view`: resumo e rótulo da formação, títulos e contagem de partes
  (FR-001, FR-003)
- [x] T003 `conclusao.html`: nova ordem, revisão recolhida, lista, aviso junto do botão, sem
  a ficha (FR-001 a FR-004)
- [x] T004 `concluida`/`concluida.html`: identificação compacta, bloco do Portal, ação
  principal única, sem a ficha; declarada inalterada (FR-005 a FR-007)
- [x] T005 `jornada.css`: revisão, lista em multicoluna, `.acao-principal`, foco sem cortes
  (FR-002, FR-004, FR-009)
- [x] T006 Testes novos e revistos com nota (FR-010, SC-004, SC-005)
- [x] T007 Verificações do CI: `ruff check .`, `manage.py check`, `makemigrations --check
  --dry-run`, `pytest`
- [x] T008 Evidências: HTML servido, capturas e medidas a 375, 1280 e fonte a 200%; refluxo a
  320 CSS px com conferência de elementos (SC-001, SC-002)
- [ ] T009 Teclado e leitor de tela; registro em `validacao.md` (US3, SC-003, SC-006).
  Teclado feito; **leitor de tela pendente**, a concluir antes da aprovação final (roteiro em
  `validacao.md`)
