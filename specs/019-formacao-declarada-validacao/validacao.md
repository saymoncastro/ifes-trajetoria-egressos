# Validação da implementação — Feature 019

Data: 2026-10-04. Branch: `claude/spec-019-academic-context-d2481f`.

## Escopo entregue

Declaração com início idempotente e sessão exclusiva, jornada existente, quarentena
analítica, fila no escopo CPAEG/CSAEG, revelação auditada, validação digital e pelo acervo,
tratamento dos conflitos, retomada, migrações e proveniência congelada na exportação v2.

A 019 permanece restrita à demonstração. As DP-1901 a DP-1911 continuam pendentes:
não foram implementadas atestação institucional real, identificação produtiva,
retenção automática, rotação operacional, evidência documental, reabertura, dados
adicionais de localização, resolução de conflitos, notificação ou fusão de Pessoas.
A capacidade de demonstração registra o resultado obtido junto à instância competente.

## Testes e verificações

- `uv run pytest -q`, depois das correções do code review: **2.226 passed, 3 skipped,
  1 deselected** em 229,75 s.
- `uv run ruff check .`: sem erros.
- `uv run python manage.py check`: sem problemas.
- `uv run python manage.py makemigrations --check --dry-run`: nenhuma mudança detectada.
- `git diff --check`: sem problemas.

Os três skips são casos sem equivalente na fonte local de acervo: pessoa sem conclusão,
registro não concluído e indisponibilidade de serviço externo. O teste de volume é
excluído pela configuração padrão do projeto. As 69 tarefas estão marcadas como concluídas.

Os testes cobrem restrições do banco, idempotência e concorrência real em PostgreSQL,
falhas sem escrita, escopo, preservação de respostas, seis situações analíticas,
congelamento dos snapshots e migração dos registros históricos sem mudar contexto ou
contagens. A exportação distingue as três origens e lê o contexto confirmado; nenhuma
declaração pendente, não confirmada, fora da abrangência ou em conflito integra as
Participações oficiais. Conclusões institucionais elegíveis sem participação continuam
no universo, como antes.

As verificações de sigilo percorrem tabelas, sessão, logs, tokens, redirecionamentos,
snapshots e exportações. O único caminho de abertura dos dados persistidos é a revelação
explícita, com capacidade, escopo, registro de acesso e `no-store`.

## Navegador

Chrome, banco novo e isolado, dados exclusivamente fictícios, chaves geradas em memória.
Nenhuma chave foi gravada em arquivo. Os bancos temporários e o servidor foram removidos
ao fim da conferência.

| Percurso | Resultado observado |
| --- | --- |
| Par inexistente | Mensagem uniforme, “Conferir os dados” seguido de “Informar minha formação” |
| Declaração e confirmação | Cinco campos, ano numérico, contexto informado pelo egresso |
| Salvar e sair / Continuar | Retorno à lista de declarações, respostas preservadas e retomada no ponto correto |
| Conclusão | Mensagem de resposta registrada e verificação institucional posterior |
| Antes da validação | Uma declaração na fila; participações oficiais iniciadas e concluídas permanecem em zero |
| Revelação | Ação por botão, valores só após POST, foco na região anunciada |
| Acervo | Campos vazios, registro fictício “Livro 3, folha 12”, curso e ano diferentes do declarado |
| Depois da validação | Declaração preservada; dados confirmados separados; fila vazia; contagens oficiais 1/1 |
| Responsividade | 320 × 740 px: formulário, confirmação, lista, conclusão, fila e detalhe sem rolagem horizontal |
| Desktop | Detalhe confirmado inspecionado no viewport padrão de 1512 px |

A acessibilidade foi verificada por estrutura HTML e inspeção do navegador, incluindo
rótulos, grupos, erros associados, foco, teclado numérico e anúncio da revelação.
Esta conferência não é uma auditoria completa de WCAG nem uma sessão com leitor de tela.

- [Conclusão em 320 px](evidencias/019-concluida-mobile.png)
- [Validação em 320 px](evidencias/019-validacao-mobile.png)
- [Validação no desktop](evidencias/019-validacao-desktop.png)

## Definition of Done e hooks

Revisados longitudinalidade, preservação histórica, proveniência, autorizações,
tratamento de erros, responsividade, privacidade, complexidade e decisões pendentes.
As notas de revisão das features anteriores e o ADR 0005 foram registrados.

Não existe `.specify/extensions.yml`; nenhum hook pós-implementação está configurado.

## Code review (2026-10-04)

Dez achados, todos corrigidos e, nos de comportamento, com teste de regressão:

1. **Verificação de integridade do snapshot (012 FR-053 d).** `participacao_id` NULL
   dentro do `NOT IN` anulava a contagem. Agora a subconsulta considera só registros com
   Participação.
2. **Duas oficiais com a mesma Conclusão efetiva** recusam a captura
   (`CapturaInconsistente`), em vez de congelar só uma.
3. **Tela de "já respondida" da Pessoa** mostra a Conclusão institucional dela, nunca os
   valores declarados nem o link do declarante.
4. **Indicador da 011** conta só a fila da Campanha exibida.
5. **"Salvar e sair" do declarante** recebe os avisos `salvo` e `saida` da 014.
6. **Indicador de declarada** passa a ser explícito nas telas de estado, não deduzido do
   tipo do objeto.
7. **Código da fonte de acervo** é constante única (`fonte_academica/acervo_historico.py`).
8. **Independência 018 → 019.**
   - O selo transitório é da 018 (`acesso/transito.py`).
   - O sujeito declarante passou para `declaracao/sessao.py`.
   - A 018 não importa nem referencia a 019.
   - Isso substitui a exceção T033 × T047 registrada antes.
9. **Migração dos snapshots** com `bulk_update` em lotes.
10. **Sessão do declarante** revalidada uma vez por requisição.
