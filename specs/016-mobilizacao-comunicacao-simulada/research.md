# Research — Feature 016

Pesquisa concluída em 2026-10-03 sobre main `0c911b5`, PR #24. Escopo aprovado em
[spec.md](spec.md). Nenhuma investigação altera decisões da baseline 015.

## R1 — Integração no acompanhamento e baseline visual

**Decisão:** link “Comunicação simulada” no detalhe de Campanha; tela própria subordinada
a esse detalhe. Estender `acompanhamento/base.html`, manter breadcrumb, contexto de atuação,
aviso de demonstração e retorno. Público, prévia e botão na mesma tela; resultado no POST.

**Razão:** o operador já conhece a Campanha e a 011 fornece visibilidade e escopo. A 015
mantém shell próprio do acompanhamento, que já inclui estilos compartilhados. Não incluir
`interface/jornada.css` nem copiar a assinatura/header da jornada para a administração.

**Alternativas:** dashboard global cria navegação sem contexto; inserir formulário no
resumo da 011 mistura consulta agregada com ação; propagar shell 015 viola seu contrato.

**Evidências locais:** `trajetoria/acompanhamento/templates/acompanhamento/{base,campanha}.html`,
[015/shell](../015-identidade-visual-jornada/contracts/shell.md),
[015/telas](../015-identidade-visual-jornada/contracts/telas.md).
Configuração e cenário canônico não tiveram mudança que exija adaptação na 015.

## R2 — Capacidade explícita, autorização e estado

**Decisão:** nova regra pura `pode_simular_comunicacao(vinculos)` para CPAEG/CSAEG ativos;
wrapper próprio em `comunicacao/acesso.py`. Reutilizar identificação fictícia da 010,
`escopo_de_acompanhamento` e `campanhas_visiveis` da 011. A operação também valida contexto
atual; nenhum contato pode ser submetido por chamá-la diretamente com lista arbitrária.

**Razão:** reutilizar escopo não transforma acompanhamento em autorização de envio. Um
único instante por execução alimenta estado e contagens; preparar/coletar autoriza simulação,
encerrada recusa. Não usar `admite_participacao`, que controla coleta real e bloquearia preparo.

**Alternativas:** decorator da 011 sozinho concede capacidade implicitamente; `is_staff`,
Pessoa escolhida ou flag demo não representam atuação institucional. Não há auth nova.
Sem operador, usar destino fechado `acompanhamento`, já existente, sem alterar seleção.

## R3 — Público e fronteira fictícia

**Decisão:** consulta 004 → filtro exato das unidades de CSAEG nas Conclusões → Pessoas
por PK distinta → contato fictício → mensagens. Consultas novas ficam em `comunicacao`,
pois a consulta da 011 promete somente agregados. Validar que a base é exclusivamente da
fonte simulada antes de expor público ou prévia; não excluir silenciosamente fonte distinta.

Contato zero/um em `comunicacao/contatos.py`, mapa explícito por `FonteSimulada.codigo` e
`id_externo` canônico, sem campo em Pessoa, sem mudança no provider acadêmico. Cada ID
mapeado usa endereço próprio; `SIM-P-0010` fica sem contato; não mapeado retorna ausência.
Nome não determina e-mail, deduplicação nem identidade.

**Razão:** contato é artefato local; essa fronteira pequena já permite substituir fonte
futura após decisão institucional sem contaminar domínio. Sem catálogo ou registry.

**Alternativas:** adicionar e-mail a Pessoa gera persistência indevida; construir contato
para todo registro da base oculta origem; deduplicar antes do escopo perde a prova do recorte.

## R4 — Convite único

**Decisão:** templates Django texto e HTML e um renderer que retorna assunto/texto/HTML,
remetente e URL. Modelo institucional não editável, somente nome opcional, Campanha e URL
neutra local. Fallback “Olá!”. Escape HTML; nenhuma consulta de Participação ou instrumento.
Prévia representativa escolhe o menor `id_externo` entre contatos no escopo, desempate PK;
sem contato renderiza genérico sem destinatário. Não carregar imagens ou CSS remoto.

**Razão:** `EmailMultiAlternatives` já compõe `multipart/alternative`; templates nativos
atendem ao consumidor concreto. HTML simples, link descritivo, sem imagem, sem motor novo.
A prévia mostra texto e HTML renderizado em iframe sandbox sem scripts/permissões,
com srcdoc escapado e título acessível; código HTML pode ser exibido em bloco escapado.
Sem recursos externos, o conteúdo não executa markup dinâmico no DOM administrativo.

**Alternativas:** renderer separado para preview diverge; editor/biblioteca/versionamento
amplia escopo; copiar contexto de formação ou rascunho vaza dado além do convite.

## R5 — Transporte e defesa em profundidade

**Decisão:** backend nativo Django SMTP para Mailpit e locmem exclusivamente no teste.
Preflight independente de destinatários e de transporte, ambos antes de instanciar backend.
Destinatários finais também passam validação imediatamente antes de cada `send()`.
Domínio constante específico da 016: exatamente `example.invalid`. Não configurável para
liberar outros domínios. Rejeitar destinatário inválido, múltiplo, com display name ou CR/LF; rejeitar
subdomínio, sufixo malicioso e domínio real. Falha em qualquer destinatário aborta o conjunto.

SMTP somente host literal `127.0.0.1` ou `::1`, porta 1025, usuário/senha vazios, TLS/SSL
falsos, timeout 5 s. Não usar DNS nem confiar nos defaults de Django para ativar a operação.
Remetente fixo `trajetoria@example.invalid`. URL configurada independente do Host do cliente,
HTTP loopback literal, porta local 8000, caminho `/demonstracao/`, sem credenciais/query/fragmento.
*(Revisado pela 018: o caminho validado passou a ser `/acesso/`, 018 FR-053 e R12.)*
Mode demo off bloqueia a operação; backend não permitido ou adapter diferente também.

**Razão:** mesmo SMTP incorreto não libera contato real: a operação checa a fronteira de
endereço por conta própria, e o guard do transporte adiciona proteção independente.
Mailpit escuta apenas loopback, sem relay/forwarding/release. Não integrar sua API.

**Alternativas:** apenas EMAIL_HOST ou apenas `.invalid` deixa defesa incompleta; backend
custom completo duplica Django; SMTP arbitrário e configurações produtivas são proibidos.

## R6 — Falha parcial e resultado sem persistência

**Decisão:** envio síncrono individual, uma conexão por mensagem com fechamento garantido,
uma tentativa, `fail_silently=False`. Retorno 1 conta aceite; 0 conta falha. Capturar
`SMTPException` e `OSError` (incluindo timeout), fechar e continuar as demais. A operação
usa conjunto preparado imutável, um destinatário por mensagem, sem CC/BCC/anexos.

Erros inesperados não são silenciosamente transformados em ausência ou sucesso: interromper,
mostrar categoria genérica e resultado parcial conhecido. Se restarem mensagens sem tentativa,
mostrar “não tentadas”; tentativa interrompida sem retorno confirmado conta falha
(nunca aceite inferido), mantendo a fórmula. `previstas = submetidas + não tentadas`, `submetidas = aceitas + falhas`.
A igualdade `submetidas = com contato` só vale na execução completa. Sem texto da exceção
ou conteúdo/endereço em logs. Preparação inteira (inclusive renderização) precede transporte.

**Razão:** lote único dificulta localizar aceite parcial; nova conexão recupera após falha.
Timeout pode ocorrer após aceite remoto: falha significa falta de confirmação, não ausência
na caixa. Nenhum retry automático, rollback SMTP ou estado “entregue”. Resposta direta POST,
`Cache-Control: no-store`, sem sessão/cache/cookie; nova visita GET não recupera resultado.
Avisar para não confirmar reenvio do POST ao atualizar navegador; não prometer idempotência.

**Alternativas:** fila/retry e persistência de Disparo resolvem outro problema; PRG exigiria
armazenar resultado ou perder contagens. Não usar Mailpit como estado do domínio.

## R7 — Testes independentes e demonstração existente

**Decisão:** locmem em todos os testes funcionais; injetar falha seletiva no limite de envio,
sem conexão externa. Testar configuração insegura com spy que prova zero backend/conexão.
Comparar renderer e MIME/outbox, autorização, deduplicação após recorte, estados e snapshots
completos do domínio. Manter testes de jornada, operadores, shell e rascunho.

O cenário já oferece Serra e Vitória EM PREPARAÇÃO: A vê 6 Conclusões/5 Pessoas;
B vê 3/2 (Bruno duas formações + Carla `SIM-P-0010`). Com esse ID sem contato, A tem 4
contatos/4 mensagens, B tem 1/1. Não modificar Campanhas, vínculos, preparo ou jornada.
`SIM-P-0009` oferece fallback sem nome na coleta ampla; nome ausente também tem teste isolado.

**Alternativas:** exigir abertura para testar Mailpit muda contexto institucional; adicionar
nova Campanha quebra cenário fixo; usar Mailpit nos testes agrega dependência desnecessária.

## Fontes técnicas primárias

- [Django 5.2 — email, SMTP, locmem e EmailMultiAlternatives](https://docs.djangoproject.com/en/5.2/topics/email/).
- [Python 3.13 — smtplib e exceções](https://docs.python.org/3.13/library/smtplib.html).
- [Mailpit — opções locais](https://mailpit.axllent.org/docs/configuration/runtime-options/).
- [Mailpit — relay explicitamente configurado](https://mailpit.axllent.org/docs/configuration/smtp-relay/).
- [RFC 2606 — `.invalid` reservado](https://www.rfc-editor.org/rfc/rfc2606.html).

Sem questões técnicas bloqueantes. Decisões institucionais abertas permanecem na spec;
esta pesquisa não habilita comunicação real.

## Precisões após análise documental

From institucional admite somente nome institucional fixo + mailbox fixo, validados
separadamente; a proibição de display name vale para destinatários simples. Resultado
retornado pela operação possui coleção interna somente PK/situação e agregados; view
projeta apenas instante/escopo/totais/categorias, sem coleção individual no template.
Testes de sigilo com caplog/sentinelas fictícias precedem cada tratamento de erro.
Auditoria final de autorização pode passar imediatamente; não exige marcador ou RED artificial.
