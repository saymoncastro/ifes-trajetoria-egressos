# Validação — Feature 031, incremento 1

- **Escopo:** primeiro incremento funcional, só na demonstração, antes dos checkpoints
  ([roadmap, revisão 16](../../docs/roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md);
  spec, "Recorte do incremento 1").
- **Checkpoint 1 e Checkpoint 2: NÃO APLICADOS.** Nada aqui é validação com egressos. As
  verificações abaixo são técnicas.
- **Uso real:** não liberado. D8, D9, D10, DP-1808, DP-3102 e DP-801 continuam pendentes.

## O que foi entregue

Percurso completo: propor → moderar (publicar, recusar, retirar) → descobrir → confirmar →
ver o link → desistir → acompanhar a quantidade → cancelar → encerramento automático do link
→ estados vazios.

| Peça | Onde |
|---|---|
| Modelos `Encontro` e `Confirmacao`; migração aditiva `0003_encontros` | `trajetoria/portal/models.py` |
| Regras puras: situação, limites, visibilidade (FR-024a), link (FR-021) | `portal/encontros/regras.py` |
| Moderação: competência, responsável pelo público, escopo de quem decidiu | `portal/encontros/governanca.py` |
| Único caminho de escrita | `portal/encontros/operacoes.py` |
| Leituras: pertinência da 025, quem vê, contagem | `portal/encontros/consultas.py` |
| Telas do egresso, do organizador e da moderação | `portal/encontros/views_*.py`, `templates/portal/encontros/` |
| Item "Encontros" na navegação (H-3105) | `portal/contexto.py` |
| Encontros fictícios da demonstração (R15) | `portal/encontros/demonstracao.py` |

## Verificações (as mesmas do CI)

| Verificação | Resultado |
|---|---|
| `uv run ruff check .` | passou |
| `uv run python manage.py check` | sem problemas |
| `uv run python manage.py makemigrations --check --dry-run` | sem mudanças |
| `uv run pytest` | 3545 passaram, 40 pulados (vídeo, sem o renderizador local; rodam no CI), 2 desmarcados |

**Testes novos:**
- `test_encontros_regras.py`: 117, sem banco. Cobrem situação, limites, a tabela inteira de
  visibilidade × quem, link, governança e vocabulário.
- `test_encontros_operacoes.py`: 22, com propor, moderar, confirmar e cancelar.
- `test_encontros_telas.py`: 29. O destaque é o link **fora do HTML** de quem não pode vê-lo,
  em cada situação (SC-002).
- `test_encontros_fronteira.py`: só a camada grava; nada no snapshot nem na exportação; o
  núcleo não importa a camada; nenhum contato lido ou gravado; logs sem dados pessoais.

**Testes revisados, com nota:**
- `test_fronteiras.py`: quatro modelos, com a FK interna `Confirmacao.encontro` admitida
  (research R2); telas que não gravam;
- `test_navegacao.py`: item "Encontros";
- `test_desabilitado.py`: rotas da 031 inexistentes sem o Portal;
- `test_oportunidades_curadoria.py`: o título "Encontro" passou a coincidir com o item da
  navegação, e o título do teste foi trocado.

## Medidas e capturas das telas servidas

Feitas com o arnês dos protótipos sobre o HTML realmente servido pela demonstração:
[`evidencias/medir.py`](evidencias/medir.py), [`evidencias/medidas.json`](evidencias/medidas.json),
[`evidencias/capturas/`](evidencias/capturas/).

- 13 telas: lista, confirmado, vou participar, cancelar participação, encerrado, sem sessão,
  propor, propor com erros, organizador, recusado, seus encontros, moderação e análise.
- Nas 13 telas: sem rolagem horizontal de 320 a 1440 px (moderação até 1280 px), com fonte
  a 100% e 200%; um h1 por tela; nenhum alvo menor que 44 px.
- A 375×812, título e data do encontro sem rolar: o fim da data fica entre 639 e 663 px.
- As capturas a 375 e 1440 px correspondem às telas p2, p3, p4, o1, o5, o6 e m1/m2 do
  [protótipo](prototipo/index.html).

**Correção feita nesta medição:** o link da trilha nas telas de análise da moderação tinha
menos de 44 px. É o mesmo padrão das telas de operação da 025 e da 026, que não foram
alteradas. A correção vale só para as telas da 031 (`moderacao/estilo.css`).

## Desvios em relação ao protótipo

- **Fora do incremento 1** (spec, "Recorte"):
  - telas de correção, alteração e nova análise (o7, o11, o12, m6, p8, p15);
  - denúncia (p12, p13, m4 com denúncias);
  - `.ics`;
  - seção do Início (p1);
  - retorno pelo endereço compartilhado. A página sem sessão (p6) leva a `/entrar/`, que
    volta ao Início.
- A página Encontros não usa "comunidade" no texto. A revisão da ADR 0009, decisão 7, fica
  para quando a palavra entrar.
- "Para quem foi proposto" mostra o público como critério ("Cursos: …"), sem a redação livre
  do protótipo.

## Pendente

- **Roteiro manual com teclado** nos cenários 2, 5, 7 e 10 do [quickstart](quickstart.md):
  **não executado**.
- **Leitor de tela:** não executado, como nas demais telas (P4 do Checkpoint 1).
- **Incremento 2:** tarefas abertas em [tasks.md](tasks.md).
