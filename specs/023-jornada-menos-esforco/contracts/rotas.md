# Contrato de rotas — Feature 023

Só as mudanças. Rotas não citadas ficam como estão.

## Avisos da entrada (`GET /acesso/?aviso=<código>`)

Lista fechada; qualquer outro valor é ignorado.

| Código | Quando | Texto (provisório) |
|---|---|---|
| `sessao` | Tela da jornada pedida com a sessão anterior descartada, ou envio de Seção sem sujeito | "Por segurança, confirme seus dados de novo para continuar. O que você já tinha salvo continua guardado." + (só com envio pendente válido) "O que você marcou nesta parte foi guardado e volta assim que você confirmar." |
| `selo` | Selo do declarante vencido ou inválido (`/declaracao/`, `/declaracao/nova/`, `/declaracao/comecar/`) | "Por segurança, confirme seus dados de novo para continuar." |

Na resposta de uma tentativa que falhou (POST com `NAO_CONFIRMADA`, formato inválido,
limite ou indisponível), a ligação "Continuar para suas formações" não aparece.

## Redirecionamentos para a entrada

| Origem | Antes | Depois |
|---|---|---|
| Telas do egresso (`/formacoes/`, `/participacoes/…`, `GET /declaracao/`, `/minha-trajetoria/…`, `/meu-email/`) sem sujeito, com sessão descartada nesta requisição | `/acesso/` | `/acesso/?aviso=sessao` (ajudante único `destino_da_entrada(request)` em `acesso/sessao.py`) |
| `POST /participacoes/<p>/secoes/<n>/` sem sujeito | `/acesso/` | guarda o envio pendente, depois `/acesso/?aviso=sessao` |
| Demais telas sem sujeito e sem sessão anterior | `/acesso/` | `/acesso/` (inalterado) |
| Selo inválido na declaração | `/acesso/` | `/acesso/?aviso=selo` |

## Envio pendente na jornada

| Rota | Comportamento novo |
|---|---|
| `GET /formacoes/` (Pessoa) | Com envio pendente válido de Participação da Pessoa: 302 para `/participacoes/<p>/`. Com envio pendente de outro sujeito: descarta e renderiza como hoje |
| `POST /declaracao/` (selo, declarante) | Depois de estabelecer o declarante: envio pendente de Participação fora das declarações do par é descartado |
| `GET /participacoes/<p>/` | Com envio pendente válido desta Participação: 302 para `secoes/<posição do envio>/` |
| `GET /participacoes/<p>/secoes/<n>/` | Envio pendente válido desta Participação e Seção: tela com os valores pendentes, sem erros, aviso `recuperado`. Seção fora do percurso, Participação concluída ou coleta encerrada: descarta o envio pendente e segue como hoje |
| `POST /participacoes/<p>/secoes/<n>/` | Envio aceito (com ou sem pendências, "Salvar e continuar" ou "Salvar e sair") desta Seção: descarta o envio pendente |
| `POST /acesso/sair/` | Apaga o registro do envio pendente |

## Avisos da Seção (`?aviso=<código>`)

| Código | Quando | Texto |
|---|---|---|
| `percurso` | (inalterado) | (inalterado) |
| `anterior` | Redirecionamento após envio aceito sem pendências para a Seção seguinte, se a Seção enviada tem Resposta gravada | "Parte anterior salva.", em linha curta junto da parte (não em caixa de aviso); exibida só se a Seção anterior do percurso tem Resposta gravada no momento da tela |

O aviso de restauração não vai na URL: ele é derivado da presença do envio pendente
(texto: "Recuperamos o que você tinha marcado nesta parte. Confira e toque em Salvar e
continuar.").

## Declaração

| Rota | Comportamento novo |
|---|---|
| `POST /declaracao/nova/` com `corrigir=1` e selo de trânsito válido | Devolve o formulário preenchido com os valores enviados, sem validar como novo avanço |
