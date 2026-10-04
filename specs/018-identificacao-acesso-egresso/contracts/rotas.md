# Contrato HTTP e interface

Rotas em `trajetoria/acesso/urls.py`, incluídas em `config/urls.py`. Views em
`trajetoria/acesso/views.py`. Todas só existem no modo de demonstração: o middleware da 008
responde 404 antes.

| Método e rota | Entrada | Saída |
| --- | --- | --- |
| GET `/acesso/` | — | 200: formulário (CPF, data de nascimento) e painel de credenciais fictícias. Com sessão ativa, também "Continuar para suas formações" (link para `/formacoes/`) e "Sair". Base não exclusivamente simulada: 422 com "A entrada de demonstração não pode ser usada com este banco de dados.", sem formulário nem painel (FR-005) |
| POST `/acesso/` | CSRF; `cpf`, `data_nascimento` | Ver a tabela de resultados abaixo. Base não exclusivamente simulada: 422 com o mesmo texto do GET, **antes** de qualquer verificação ou contagem (FR-005) |
| POST `/acesso/sair/` | CSRF | `flush()` da sessão; 303 para `/acesso/` |
| GET `/demonstracao/` | — | 301 para `/acesso/` (compatibilidade com links antigos e mensagens já na caixa local) |
| *(removidas)* POST `/demonstracao/escolher/`, POST `/demonstracao/encerrar/` | — | 404 |

**Resultados do POST `/acesso/`:**

| Resultado | Status | Corpo | Sessão |
| --- | --- | --- | --- |
| `Confirmada` | 303 → `/formacoes/` | — | Estabelecida (`cycle_key`) |
| `FormatoInvalido` | 200 | Formulário com os valores digitados; resumo de erros com foco; erro por campo ("Confira o CPF informado." / "Confira a data de nascimento informada.") | Inalterada |
| `NaoConfirmada` | 200 | Aviso "Não foi possível confirmar os dados informados." com foco; texto "Confira os dados abaixo e tente novamente." e link-âncora "Conferir os dados" (`href="#cpf"`), que leva o foco ao campo CPF; formulário preenchido com os valores digitados. **Idêntico para todas as causas internas** | Inalterada |
| `Indisponivel(LIMITE_TEMPORARIO)` | 429 + `Retry-After` (segundos) | "Aguarde alguns instantes antes de tentar novamente." Sem contagem de tentativas | Inalterada |
| `Indisponivel(CHAVE_NAO_CONFIGURADA \| FALHA_TECNICA)` | 503 | "Não foi possível verificar agora. Tente novamente em instantes." | Inalterada |

Uma sessão ativa só é substituída por nova `Confirmada`. Resultados sem confirmação não a
encerram nem a alteram.

## Regras transversais

- **Cache.** `Cache-Control: no-store` em todas as respostas de `/acesso/` (o corpo pode
  conter CPF e data digitados).
- **Sem dados em endereços.** CPF e data só trafegam no corpo do POST. Nunca em query,
  `Location`, `Referer` gerado, cookie ou log. GET com `?cpf=` ou `?data_nascimento=` é
  ignorado.
- **Métodos.** GET e POST; demais: 405. CSRF ausente: 403 do framework, antes da
  verificação.
- **Mensagens.** Vocabulário fechado em `acesso/mensagens.py`. Nunca "login", "conta",
  "senha", "autenticação segura" nem "acesso seguro" (FR-061).
- **Sem dados da base.** Nenhum nome, formação ou dado acadêmico em qualquer resposta de
  `/acesso/` antes da confirmação. O nome da Pessoa em uso aparece só no cabeçalho, quando
  já há sessão.

## Rotas existentes alteradas

| Rota | Mudança |
| --- | --- |
| GET `/` | 302 para `/formacoes/` com sessão; para `/acesso/` sem ela |
| Toda rota da jornada (`/formacoes/…`, `/participacoes/…`) | Sem sessão válida: 302 para `/acesso/` (antes: `/demonstracao/`). Nada mais muda |
| `interface/base.html` (faixa de demonstração) | Texto: "Ambiente de demonstração. Todos os dados são fictícios. A confirmação usa CPF e data de nascimento fictícios e não é autenticação forte." Com sessão: nome da Pessoa e botão "Sair" (POST `/acesso/sair/`). Removidos "Trocar de pessoa" e "Encerrar demonstração" |
| Convite da 016 | URL neutra `http://127.0.0.1:8000/acesso/`; `validar_url` aceita o caminho `/acesso/` |
| `/demonstracao/operador/…` (010, 011, 016, 017) | Inalteradas |

## Tela de entrada

- **Base.** Usa `interface/base.html` (shell da 015), com título "Confirme seus dados
  para acessar a pesquisa".
- **Explicação.** Um parágrafo: "Use o CPF e a data de nascimento registrados no Ifes."
  Sem promessa de segurança.
- **Campos.**
  - **CPF**: rótulo visível, `inputmode="numeric"`, `autocomplete="off"`, dica "Somente
    números ou no formato 000.000.000-00".
  - **Data de nascimento**: rótulo visível, `inputmode="numeric"`, `autocomplete="bday"`,
    dica "DD/MM/AAAA".
  - **Erros**: ligados por `aria-describedby`, com `aria-invalid`.
- **Ação.** Botão "Continuar".
- **Painel de demonstração**, separado por título "Dados fictícios para demonstração": uma
  tabela com Pessoa, CPF, data e nota. Cada linha tem um formulário POST "Usar estes
  dados". O painel lê só de `cenarios.PESSOAS`.
- **Requisitos gerais.** Sem JavaScript obrigatório; teclado; foco visível; 320 px;
  ampliação de 200%; contraste AA.
