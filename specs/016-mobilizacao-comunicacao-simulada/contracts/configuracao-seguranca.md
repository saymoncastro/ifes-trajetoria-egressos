# Contrato de configuração e segurança local

Configuração continua em `config/settings.py`, lendo ambiente sem carregar `.env`.
`.env.example` documentará somente variáveis fictícias. Nova app `trajetoria.comunicacao`
permite descobrir templates, sem modelos/migrations. Dependências Python permanecem iguais.

| Setting | Valor/condição permitida |
| --- | --- |
| `TRAJETORIA_DEMONSTRACAO` | somente `1` no ambiente ativa; ausente recusa |
| `EMAIL_BACKEND` | SMTP nativo explicitamente configurado; locmem nativo somente testes |
| `EMAIL_HOST` | `127.0.0.1` ou `::1` literal; não hostname/DNS |
| `EMAIL_PORT` | 1025 |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | vazios |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | falsos |
| `EMAIL_TIMEOUT` | 5 segundos, fixo para esta demo |
| `DEFAULT_FROM_EMAIL` | `trajetoria@example.invalid`; mensagem usa remetente institucional fixo |
| `TRAJETORIA_URL_ENTRADA_DEMONSTRACAO` | default neutro `http://127.0.0.1:8000/demonstracao/` |

Ausência de configuração explícita de backend mantém operação desabilitada: default local
recusável (por exemplo valor vazio tratado no preflight), sem fallback ao SMTP padrão Django.
Capturar/validar a mesma configuração usada para construir conexão, evitando divergência
entre guard e backend. A permissão locmem exige setting interno
`TRAJETORIA_COMUNICACAO_TESTE=True` via `override_settings`, falso por padrão e sem variável
pública de ambiente; testes também ativam modo demo. Não inferir teste pelo nome do processo.

URL permite HTTP loopback literal `127.0.0.1`/`[::1]`, porta 8000, caminho exato
`/demonstracao/`; sem userinfo, query, fragmento, redirect ou identidade. Não usar request Host.
Destinatários exigem endereço simples válido, domínio exatamente `example.invalid`,
sem CR/LF, listas ou display name. Remetente é composto pelo nome institucional fixo
“Trajetória Ifes — demonstração institucional” e mailbox fixo `trajetoria@example.invalid`.
Validar esses componentes separadamente antes de formatar o cabeçalho From; somente o
remetente admite esse display name fixo. Não aceitar nome/mailbox alternativos do cliente
ou ambiente. Validar também o From final contra esses componentes, sem aplicar ao cabeçalho
formatado a proibição de display name dos destinatários. CR/LF é vedado em ambos.
Comparação de domínio normaliza somente caixa; rejeitar `x.example.invalid`,
`example.invalid.evil` e similares.
Domínio permitido é constante da 016, sem env configurável para autorizar contatos reais.

## Camadas independentes

1. Modo explícito e base exclusivamente simulada, identidade fictícia separada.
2. Capacidade/visibilidade/escopo revalidados em GET e POST e na operação direta.
3. Domínio exato em todo conjunto antes de construir backend; checagem final de cada `to`.
4. Transporte permitido e loopback, sem credenciais/TLS/SSL; configuração insegura recusa.
5. Remetente/URL/conteúdo local; sem tracking ou recursos externos, escape/cabeçalhos seguros.
6. Mailpit somente loopback, sem relay, forwarding ou liberação externa.

Nenhuma camada substitui outra. Endereço externo aborta mesmo com Mailpit ou SMTP incorreto;
SMTP incorreto também aborta com contatos fictícios válidos. Não generalizar esses guards
para comunicação real futura. Sem editor/lista client-side, CSRF, métodos fechados.

Mailpit não é acessado por HTTP pelo aplicativo, não fornece estado, não tem credenciais
reais. Conteúdo da caixa é fictício; persistência temporária do Mailpit é infraestrutura,
não Invites/Disparos no domínio. Encerrá-lo encerra a caixa temporária sem volume persistente.

Logs/erros só categorias técnicas e contagens mínimas; não incluir nomes, endereços, mensagens,
respostas, settings secretos ou texto bruto da exceção. Tratamento local dos erros esperados
impede exposição via logger genérico do request. Backend fora da allowlist, contato real ou
falha de fonte são recusa, nunca fallback silencioso.
