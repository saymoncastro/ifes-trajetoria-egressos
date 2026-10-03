# Data model — Feature 016

**Nenhum modelo, tabela, campo, migração ou entidade persistente nova.** Campanha,
Participação e demais registros de domínio permanecem idênticos. Nenhum Convite,
Destinatário, Disparo ou Evento de entrega. Não registrar histórico/auditoria simulada.

## Modelos existentes somente lidos

| Modelo | Dados necessários | Uso |
| --- | --- | --- |
| Campanha | PK, nome, critérios, datas/encerramento, referência existente | Visibilidade, população 004, estado atual e título |
| ConclusaoAcademica | PK, Pessoa, fonte e atributos acadêmicos | Elegibilidade e escopo por unidade antes de deduplicar |
| Pessoa | PK, fonte, id_externo, nome opcional | Identidades distintas, contato e saudação |
| Vínculo de governança | operador, papel, ativo, unidade | Capacidade e escopo atuais |

Pesquisa/Versão não são personalização do convite. Referência em rascunho permanece oculta
para B. Participação, Resposta e opções não são consultadas para segmentação nem alteradas.

## Valores transitórios de aplicação

Podem ser estruturas simples/frozen dataclasses, sem `models.Model`, identidade persistente
ou serialização de histórico. São detalhes locais, não novos conceitos do domínio.

- **Contexto autorizado:** operador fictício e escopo reobtidos na operação; instante único.
- **Público:** Conclusões no escopo, Pessoas únicas ordenadas, pares Pessoa/contato ou ausência,
  números de Conclusões, Pessoas, com/sem contato e mensagens previstas.
- **Contato:** `str | None` do mapa fictício por fonte e ID estável. Invalidez é erro;
  ausência é normal. Sem escrita em Pessoa. `SIM-P-0010` ausente; demais IDs canônicos
  mapeados a `sim-p-NNNN@example.invalid`. Pessoas não canônicas não ganham endereço.
- **Convite renderizado:** assunto, texto, HTML, remetente fixo e URL neutra; mensagem de
  transporte tem um `to` distinto por Pessoa, sem CC/BCC/anexo. Nome ausente → “Olá!”.
- **Resultado interno da operação:** instante, escopo, contagens do público, tentativas/
  aceites/falhas, categoria genérica e não tentadas, mais coleção transitória de PK de Pessoa
  e situação. Não contém nomes, endereços, conteúdo ou texto bruto de exceção.
- **Representação da tela:** projeção somente de instante, escopo, totais/categorias; a
  coleção individual não é passada ao template. Ambas as representações duram somente
  a requisição, sem armazenamento ou endpoint de consulta posterior.

## Validações e transições

Ordem: Conclusões elegíveis → escopo → Pessoas distintas → contatos → mensagens.
Toda base com origem acadêmica diferente da fonte simulada é recusada antes de exposição.
Todos os contatos e conteúdos são preparados/validados antes de qualquer transporte;
nenhum destinatário pode ter domínio diferente de `example.invalid`.

| Estado derivado da Campanha (004) | Público/prévia | Nova simulação |
| --- | --- | --- |
| EM PREPARAÇÃO | sim | sim |
| EM COLETA | sim | sim |
| ENCERRADA, por data ou fechamento explícito | sim | não |

A 016 não produz transição na Campanha. Ações simultâneas e repetidas são independentes;
a deduplicação vale somente dentro de uma execução. Não há reserva de público ou promessa
de autorização invariável após o momento da verificação; requisição seguinte relê vínculos.
O conjunto preparado representa o instante da execução, não fotografia persistida.

Fórmulas: Pessoas = com + sem contato; previstas = com contato;
submetidas = aceitas + falhas. Execução completa: submetidas = previstas.
Interrupção inesperada: previstas = submetidas + não tentadas. Nenhum valor prova entrega.

Mailpit guarda artefatos de infraestrutura para inspeção local; locmem guarda outbox durante
teste. Nenhum dos dois fornece estado de domínio ou muda elegibilidade/acesso espontâneo.

## Resultado individual exclusivamente transitório

Durante uma execução, o resultado interno da operação contém PK de Pessoa e situação em memória:
“submetida ao transporte” (retorno 1, confirmação de aceite local), “falha de transporte”
(retorno 0/exceção, sem confirmação) ou “sem contato” (não tentou). Em interrupção inesperada,
contatos restantes recebem “não tentada”. Interface informa totais, sem lista de nomes/e-mails.
Não são entidades, eventos, Convites ou Destinatários persistidos. Sem SMTP dentro de transação
de banco, rollback de mensagens ou retry. Tentativas = confirmadas + falhas; Pessoas =
confirmadas + falhas + sem contato + não tentadas, após preparação válida.

Cada POST legítimo é nova execução; sem “já enviado”, histórico, deduplicação/idempotência
entre execuções ou chave de idempotência. Duas execuções podem gerar duas mensagens para
a mesma Pessoa. Nenhum estado é mantido para impedir isso.
