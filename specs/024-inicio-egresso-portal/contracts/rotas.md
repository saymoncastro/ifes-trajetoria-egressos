# Contrato: rotas e caminhos de acesso (024)

Todas as rotas existem só no modo de demonstração (`ModoDemonstracaoMiddleware`). As rotas do
Portal existem só com `TRAJETORIA_PORTAL` diferente de `"0"` (research R8).

## Rotas novas (Portal ativo)

| Rota | Método | Sem sujeito | Pessoa na sessão | Declarante (019) |
|---|---|---|---|---|
| `/` | GET | 303 → `/entrar/` | 303 → `/inicio/` | 303 → `/declaracao/` |
| `/entrar/` | GET | 200, formulário da 018, rotulado "Entrada do Portal do Egresso" | 303 → `/inicio/` | 303 → `/declaracao/` |
| `/entrar/` | POST | Mesma verificação da 018. Confirmada: 303 → `/inicio/`. Demais resultados iguais aos de `/acesso/` (erros de formato com resumo, 429 com `Retry-After`, 503, 422 de base indevida, "não confirmada" com selo da 019) | idem | idem |
| `/inicio/` | GET | 303 → `/entrar/?aviso=sessao` se a sessão acabou de expirar; senão 303 → `/entrar/` | 200 | 303 → `/declaracao/` |

Regras:

- **Destino fixo.** Nenhum parâmetro decide destino. Parâmetros desconhecidos são
  ignorados. `aviso` aceita só `sessao` em `/entrar/` (FR-006, FR-007).
- **Aviso em `/entrar/?aviso=sessao`.** Mostra só a frase genérica da 023 FR-001, nunca a do
  envio guardado (FR-007; research R9).
- **Cabeçalhos.** `/entrar/` e `/inicio/` usam `never_cache`, como `/acesso/` e
  `/minha-trajetoria/`.
- **Sem gravação.** Nenhuma das rotas grava, salvo a sessão estabelecida pela identificação
  confirmada (018).

## Rotas existentes

| Rota | Muda? | Detalhe |
|---|---|---|
| `/acesso/` (GET/POST) | **Não** no comportamento | Confirmada → `/formacoes/`. O template recebe `acao`, `continuar` e rótulo por parâmetro (research R3); com os valores padrão, o HTML é o de hoje |
| `/acesso/sair/` | Não | 303 → `/acesso/` |
| `/` (Portal **desabilitado**) | Não | `interface.views.inicio`, como hoje |
| `/formacoes/` | Texto | Sem a frase de antecipação. Com "A pesquisa tem no máximo N partes." para a formação disponível para iniciar (FR-013, FR-014). Slot de navegação (FR-022) |
| `/minha-trajetoria/`, `card.png`, `card.svg`, `video/…` | Regra de acesso | Pessoa com ao menos uma Conclusão Acadêmica (FR-009). Sem Conclusão → 302 `/formacoes/`. Sem sessão → `/acesso/` (023 FR-001), como hoje |
| `/participacoes/<id>/concluida/` | Slot | Navegação (FR-022). A ação continua sendo a trajetória (021 FR-003) |
| `/meu-email/` | Slot | Navegação (FR-022) |
| `/participacoes/<id>/secoes/<n>/`, `/concluir/`, `/declaracao/…` | Não | Sem navegação, shell da 015 |

## Matriz de caminhos (FR-033)

| # | Caso | Caminho A (convite, `/acesso/`) | Caminho B (Portal, `/` ou `/entrar/`) |
|---|---|---|---|
| 1 | Identificação confirmada | `/formacoes/` | `/inicio/` |
| 2 | Participação em rascunho | `/formacoes/` com "Continuar a pesquisa" | Início com convite "Continuar" → `/formacoes/` |
| 3 | Participação concluída | `/formacoes/`, sem entrada pendente | Início sem convite de ação |
| 4 | Campanha encerrada, fora da abrangência ou sem pesquisa | Mensagem da 007/014 | Início com frase de estado e sem ação |
| 5 | Envio guardado (023) | Volta à Seção (FR-006) | Início. O convite leva a `/formacoes/`, que volta à Seção |
| 6 | Pessoa sem Conclusão | `/formacoes/` `SEM_FORMACAO` | Início sem formações, trajetória e convite |
| 7 | Declarante | `/declaracao/` (019) | `/declaracao/` |
| 8 | Portal desabilitado | Inalterado | `/` = comportamento de hoje; `/entrar/` e `/inicio/` = 404 |
