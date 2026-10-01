# Contrato: consultas de Participação e Resposta

Interface de leitura, consumida pelos testes desta feature e, no futuro, pela 006.
Módulo: `trajetoria.participacao.consultas`. Atende FR-044 e FR-046 a FR-050.

Nenhuma consulta grava nada, calcula progresso, próxima Pergunta, obrigatoriedade ou
conclusão, nem monta modelo de tela (FR-050). Todas valem em qualquer estado da Campanha
(leitura depois do encerramento é permitida — FR-040).

## `localizar_participacao(campanha, conclusao) -> Participacao | None`

A Participação do par, ou `None`. Nunca cria (FR-046). Para "localizar ou iniciar", a 006
usa `operacoes.iniciar_participacao`, que devolve a existente (`JA_EXISTENTE`).

## `participacoes_da_conclusao(conclusao) -> tuple[Participacao, ...]`

Todas as Participações da Conclusão — zero, uma ou várias — em ordem
`(iniciada_em, id)`. A ordem é só determinística: nenhuma é "a atual" da Conclusão ou da
Pessoa (FR-049; Princípio I).

## `admite_escrita(participacao, *, agora=None) -> bool`

`estado(participacao.campanha, agora=agora) is EstadoCampanha.EM_COLETA` (004). Não
reavalia elegibilidade (FR-034, FR-048). Verdadeiro aqui não reserva nada: a escrita
verifica de novo, sob bloqueio.

## `respostas_atuais(participacao) -> dict[UUID, Resposta]`

As Respostas atuais da Participação, indexadas pelo `id` da Pergunta, com `pergunta`,
`opcao` e `opcoes` pré-carregados (FR-047).

- Pergunta **ausente** do dicionário = **não respondida**.
- Pergunta presente = respondida; o valor está na coluna do tipo
  ([data-model](../data-model.md#resposta)):

  | `pergunta.tipo` | Valor |
  |-----------------|-------|
  | `ESCOLHA_UNICA` | `resposta.opcao` (+ `resposta.complemento`, se houver) |
  | `ESCOLHA_MULTIPLA` | `set(resposta.opcoes.all())` (+ `resposta.complemento`) — conjunto; a ordem da consulta é a do instrumento, não a de seleção |
  | `TEXTO_CURTO` | `resposta.texto` |
  | `ESCALA` | `resposta.escala` |

- Para reconstruir o preenchimento, a 006 percorre as Perguntas da Versão aplicada
  (`participacao.versao`; 002, `conteudo_da_versao`) e procura cada uma no dicionário.
  Esta consulta não monta essa árvore.

## Origem dos dados na leitura (FR-044)

| O que se lê | Categoria | De onde |
|-------------|-----------|---------|
| Valores e complementos das Respostas | **Declarado** | `respostas_atuais` — único conteúdo do app |
| Curso, unidade, nível, modalidade, ano | Institucional | `participacao.conclusao` (001), lido, nunca copiado |
| Pessoa | Registro | `participacao.pessoa` (pela Conclusão) |
| Versão, Pesquisa | Configuração | `participacao.versao`, `participacao.pesquisa` (pela Campanha) |
| Coleta admitida | Derivado | `admite_escrita` (estado da 004) |

Nenhuma consulta compara, concilia ou sinaliza divergência entre declarado e
institucional (FR-043; DP-508).

## Uso pela 006

| Pergunta da 006 | Resposta |
|-----------------|----------|
| Esta Conclusão já participa desta Campanha? | `localizar_participacao(c, conclusao)` |
| Iniciar ou retomar | `iniciar_participacao(c, conclusao, agora=…)` → `CRIADA` ou `JA_EXISTENTE` |
| Ainda posso gravar? | `admite_escrita(p, agora=…)` |
| O que já foi respondido? | `respostas_atuais(p)` |
| Qual o histórico longitudinal desta Conclusão? | `participacoes_da_conclusao(conclusao)` |
