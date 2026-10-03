# Contrato HTTP e interface

Rotas incluídas em `trajetoria/acompanhamento/urls.py`; views próprias em `comunicacao`.

| Método e rota | Entrada aceita | Saída |
| --- | --- | --- |
| GET `/acompanhamento/campanhas/<uuid>/comunicacao/` | somente UUID | HTML administrativo de público-alvo + prévia + possibilidade da ação |
| POST `/acompanhamento/campanhas/<uuid>/comunicacao/simular/` | UUID e CSRF | HTML com resultado transitório da execução |

Sem rota GET de resultado, API JSON ou mailing; métodos inadequados retornam 405.
Nenhum ID de Pessoa, destinatário, assunto, corpo, remetente, URL ou total do cliente
é usado pela operação. Formulário só contém CSRF e botão “Simular envio local”. Campos
extras não podem modificar conteúdo ou público; essa tentativa é coberta por teste.

## Autorização e erros

Modo demo desligado: middleware 404; operação direta também recusa. Sem operador: redirect
para seleção existente com destino fechado `acompanhamento`. Sem capacidade: 403.
Operador capaz com UUID inexistente: 404. Campanha existente fora do escopo: 403 sem nome,
conteúdo ou números. CSRF ausente/inválido: 403 antes de operação. Todos os GET/POST relêem
vínculos e escopo antes de consultar público. Identidade fictícia de Pessoa não autoriza.

GET autorizado: 200 nos três estados, sem transporte. POST em ENCERRADA: 409, zero
mensagens, informa estado e permite voltar à prévia. Falha de preflight: 422 com categoria
genérica e zero tentativas; sem dados sensíveis/configuração secreta. POST concluído ou com
falhas de transporte: 200, resultado informa sucesso parcial/zero aceites, sem “entregue”.
Interrupção inesperada: 500 genérico com números conhecidos/não tentadas quando disponíveis,
sem traceback. Não mascarar falha técnica como ausência de contato.

## Tela

Entrada contextual no detalhe, sem menu global. `acompanhamento/base.html`, breadcrumb
Campanhas → Campanha → Comunicação, escopo e aviso permanente “Demonstração local com
contatos fictícios; nenhum envio real”. Mantém ocultação do instrumento em rascunho.
Nenhum estilo da jornada adicionado. Sem dependência de JavaScript; teclado/foco, labels,
320 px e ampliação 200%. Não listar Pessoas ou revelar unidades fora do recorte.

Público mostra momento, Conclusões, Pessoas, com/sem contato e mensagens previstas.
Prévia: remetente, representante determinístico no escopo ou “sem destinatário”, assunto,
texto e HTML renderizado em iframe sandbox sem scripts, srcdoc escapado e título
acessível (e código HTML escapado para inspeção), CTA e URL. Modelo é somente leitura; sem campos de editor.
Em preparação explicar a verificação pré-operacional; encerrada não mostra ação habilitada.

Resultado no próprio POST com `Cache-Control: no-store`, sem armazenamento em sessão,
cache, cookie ou banco. Contexto do template recebe somente projeção agregada do resultado
interno; não recebe coleção de PKs/situações individuais, contatos ou exceção bruta.
Exibir submetidas/aceitas/falhas; interrupção também não tentadas.
Avisar que falha pode ter ocorrido após aceite na caixa e que repetir gera novas mensagens.
Link de retorno GET não envia. Atualizar POST depende da confirmação do navegador; instruir
não confirmar reenvio. Não existe garantia de execução única entre duas requisições explícitas.

## Público-alvo e acesso institucional

“Público” significa público-alvo da Campanha, nunca endpoint aberto ao público. Todas as
telas/endpoints acima são administrativos/institucionais, exigem modo demo, identificação
do operador fictício, governança 010/011 e escopo CPAEG/CSAEG. Nenhum egresso acessa
Comunicação; seleção/cookie de Pessoa não concede acesso. O CTA leva somente à entrada
neutra existente, não às telas de Comunicação.

Cada POST legítimo é nova execução independente; não existe “já enviado”, histórico ou
idempotência entre duas simulações. UI avisa que duas ações podem produzir duas mensagens
para a mesma Pessoa, sem chave/tabela/estado de idempotência. Resultado apenas em memória
por Pessoa/mensagem, totais de submetidas com confirmação, falhas, sem contato e, quando
necessário, não tentadas; tentativas/aceites são também exibidos com suas definições.
