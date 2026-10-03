# Contrato de operação, contato e renderer

## Capacidade e contexto

`pode_simular_comunicacao(vinculos) -> bool`: CPAEG ou CSAEG ativo, explicitamente nomeado.
Reusar `escopo_de_acompanhamento`: CPAEG ativo institucional; senão união de CSAEG ativas;
sem atuação recusa. A mesma capacidade fixa protege preparar/preview/simular nesta demo.
Não autoriza envio real nem deriva poder de editor/acompanhamento/flag técnica.

`simular_comunicacao(campanha_id, operador_id) -> resultado transitório`: assinatura local
prevista, não API pública. ID de operador vem somente do adaptador fictício confiável, nunca
de POST. A função verifica modo, identificação válida entre operadores fixos, vínculos
atuais, capacidade, Campanha visível e estado atual antes de calcular público. Não aceita
público/contexto previamente calculado pelo navegador nem backend/destinatários arbitrários.

Preparação GET usa os mesmos helpers de acesso, consulta, contatos e renderer sem envio.
Operação reobtém tudo, não usa lista da prévia. Sem mutação de domínio, `.save()`, criação
ou operação de participação. Não chamar `_universo` privado da 011; filtro simples explícito
no módulo novo preserva seu contrato agregado.

## Pipeline obrigatório

1. `populacao_no_momento(campanha)` da 004 sobre Conclusões incorporadas.
2. Restringir Conclusões à igualdade exata de `unidade` no escopo CSAEG; nulo fica fora.
3. Pessoas por PK distintas dessas Conclusões; homônimos não se fundem.
4. `contato_ficticio(pessoa) -> str | None`, mapa da fonte simulada por `id_externo`.
5. Validar conjunto inteiro, renderizar e validar mensagens; então enviar uma por Pessoa.

Antes de dados de GET ou POST, recusar base com Pessoa/Conclusão de outra fonte. Não
transformar contato inválido/falha do resolver em ausência. Nenhum campo novo em Pessoa;
nenhuma importação/sincronização/catálogo externo. IDs não mapeados não ganham contato.

## Convite não editável

Assunto: `Convite para a pesquisa — {nome_campanha}` (rejeitar CR/LF nos cabeçalhos).
Nome institucional do remetente: “Trajetória Ifes — demonstração institucional”, endereço
fixo `trajetoria@example.invalid`. Texto institucional convida a conhecer a demonstração
da Campanha, informa que dados/contatos são fictícios e que a mensagem foi produzida em
ambiente local. Saudação `Olá, {nome}!` ou `Olá!`; CTA “Abrir a demonstração”; assinatura
institucional de demonstração. Não prometer coleta aberta, periodicidade, entrega ou login.

`renderizar_convite(nome_pessoa, nome_campanha, url_entrada)` fornece um único resultado
com assunto, texto e HTML. Parâmetros vêm de dados existentes/config local validada; sem
editor. Nenhum contexto de formação, respostas, estado de participação ou rascunho.
Templates Django escapam HTML, mesma chamada na prévia e no envio. HTML simples sem scripts,
recursos externos/imagens; link textual e conteúdo equivalente na versão texto.

`EmailMultiAlternatives`: corpo texto, alternativa `text/html`, exatamente um `to`, sem
CC/BCC/anexos. Destinatário é mailbox simples sem display name. Remetente From admite
somente o nome institucional fixo junto a `trajetoria@example.invalid`; validar nome e
mailbox separadamente e conferir a composição final. Validar destinatários finais também
imediatamente antes de `send()`.
Sem contato: zero mensagem. Menor `id_externo` com contato no escopo, desempate PK, escolhe
prévia determinística; sem contatos, modelo genérico sem destinatário.

## Falhas e números

Preflight aborta integralmente antes de backend/conexão se qualquer contato ou configuração
for inseguro, renderer falhar ou origem for indevida. Validar endereço e transporte em
rotinas independentes para que SMTP incorreto não dispense domínio exato. Zero contatos
não instancia backend/conecta. Preparação inválida mostra categoria genérica, zero tentativas.

Uma mensagem/uma tentativa/uma conexão fechada; retorno 1 → aceita, 0 ou `SMTPException`/
`OSError` → falha de transporte. Continuar próximas mensagens com conexão nova; sem retry.
Incrementar submetidas ao tentar encaminhar mensagem ao backend. Erro inesperado interrompe,
não tentadas contabilizadas; tentativa sem retorno confirmado conta falha, nunca aceite
inferido; sem sucesso fictício. Nenhuma mensagem aceita é desfeita.
Timeout após DATA pode deixar mensagem na caixa: falta de confirmação não prova ausência.

A operação retorna resultado transitório com instante, escopo, contagens/categorias e
resultados individuais internos (PK de Pessoa e situação), sem nomes, endereços, conteúdo
ou detalhes de exceção. A view projeta somente instante, escopo e totais/categorias para
o template; nunca repassa a coleção individual ao contexto HTML. Nenhuma representação
é persistida ou recuperável após a requisição. Só em execução completa submetidas = com contato;
sempre submetidas = aceitas + falhas. Sem histórico, API Mailpit ou marca “entregue”.

## Precisão de execução e situações individuais

Cada POST legítimo representa nova execução independente. Não existe “já enviado”,
histórico, deduplicação ou idempotência entre duas simulações; ambas podem produzir
mensagem para a mesma Pessoa no Mailpit. Não criar chave de idempotência, tabela ou estado
persistido. A deduplicação é somente interna a uma execução, após o recorte de Conclusões.

Resultado em memória por Pessoa/mensagem: referência interna + situação “submetida ao
transporte” quando há aceite local confirmado, “falha de transporte” quando tentativa não
confirma aceite, “sem contato” quando não há tentativa. Não é estado de entrega. Falha não
desfaz mensagens anteriormente submetidas; não usar transação de banco envolvendo SMTP
nem retry automático. UI apresenta totais por situação, sem lista nominal. Contador
“submetidas” mede todas as tentativas, inclusive falhas; “aceitas” mede situação confirmada.
Em interrupção inesperada, contatos restantes recebem “não tentada” e totais específicos.
Falha de preflight não fabrica resultado por Pessoa nem executa transporte: bloqueio integral.
