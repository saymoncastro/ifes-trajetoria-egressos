# Tasks: Camada visual do Portal — direção B

**Input:** [spec.md](spec.md), [plan.md](plan.md), ADR 0009 e protótipos B.
**Situação:** direção B escolhida em 2026-10-09; implementação e validação local concluídas.
Cada etapa entrega comportamento verificável. Checkpoint 1 continua NÃO APLICADO.

## Preparação

- [x] T001 Confirmar integração do PR #51 e escolha B; registrar spec e requisitos revisados.
- [x] T002 Preparar ambiente pelo guia e registrar linha de base com ruff, check,
  makemigrations e pytest antes das mudanças de aplicação.

## Etapa 1 — Base do Portal e legenda (US3)

- [x] T003 Criar base e camada CSS do Portal; preservar `interface/base.html` e tokens da 015.
- [x] T004 Adicionar slot neutro de base nos templates compartilhados e prover seu valor
  só nas telas harmonizadas; proteger Portal desligado e shell de referência.
- [x] T005 Corrigir legenda de imagem genérica/própria; regressões de proveniência.

## Etapa 2 — Página pública e Início (US1, US2)

- [x] T006 Implementar página pública, card fictício versionado e destinos de raiz;
  revisar testes da antiga expectativa de redirecionamento sem sessão.
- [x] T007 Expor formações, agregados e descrição de card pela montagem existente,
  sem nome, resposta, contato ou escrita nova.
- [x] T008 Implementar direção B no Início; linha horizontal que permite quebra no
  desktop, ações e prévia; conservar ordem de Oportunidades e convite.
- [x] T009 Corrigir e medir a primeira tela de Ana e Diego, sem remover informações.

## Etapa 3 — Harmonização e acabamento (US3)

- [x] T010 Recolher painel fictício só em `/entrar/`, com controles nativos; preservar
  identificação, erros, CSRF e `/acesso/`.
- [x] T011 Harmonizar trajetória, contato e oportunidades, com os fluxos existentes.
- [x] T012 Verificar vocabulário, semântica, teclado, foco, alvos, contraste e fonte
  100/200 em 320–1440; confirmar orçamento móvel do destaque de oportunidades.
- [x] T013 Capturar matriz visual e comparar com B; registrar medidas e diferenças.
- [x] T014 Acrescentar notas de revisão nas specs 015/021/024/025 e atualizar roadmap
  e registro da escolha; não mudar pendências institucionais.
- [x] T015 Rodar as quatro verificações completas do CI; registrar resultados e
  limitações em `validacao.md` e revisar Definition of Done.

## Dependências e entrega

T001–T002 precedem código. Etapa 1 precede Etapa 2; Etapa 3 conclui a experiência.
T005 pode ser revisada separadamente. Nenhuma tarefa autoriza dados reais, produção,
026/027 ou mensagens à ACS. A entrega local é revisável antes de publicação ou merge.
