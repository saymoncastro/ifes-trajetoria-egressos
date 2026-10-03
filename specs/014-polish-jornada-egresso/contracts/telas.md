# Contrato: conteúdo das telas alteradas

O que muda em cada tela, do ponto de vista de quem a lê ou a testa. Textos provisórios
(DP-801). Telas não listadas não mudam.

## Seção (`secao.html`)

Ordem do topo (FR-024):

1. Aviso de percurso, quando houver.
2. `h1` da Seção (R9).
3. Resumo, quando houver: tipo `"erros"` ou `"pendencias"`
   ([data-model](../data-model.md#resumo-da-seção)).
4. Linha "Você está respondendo sobre: {linha}".
5. Texto de abertura da Versão, só na primeira Seção.
6. Texto da Seção.
7. Formulário ([rodapé](rodape-secao.md#formulário-da-seção)).
8. `div.saidas`.

### Controles de Pergunta (`perguntas/*.html`; também na prévia do editor)

| Tipo | Marcação |
|---|---|
| Escolha única em rádios | `fieldset.pergunta#pN` (sem `role`) › `legend#pN-enunciado` › cabeçalho › `div.opcoes[role=radiogroup][aria-labelledby=pN-enunciado][aria-required?]` › `.opcao`… › complemento › remover |
| Escala | Igual, com `div.escala` como `radiogroup`; número abaixo do controle; grade de colunas de pelo menos 44 px (R6) |
| Escolha múltipla | Sem mudança de marcação; ganha a área ativável de R5 |
| Lista suspensa, texto curto | Sem mudança |

Em todos os tipos com `.opcao` dentro de `.pergunta`, a linha ou a célula inteira ativa o
controle (R5).

## Conclusão (`conclusao.html`)

- `h1` "Concluir a pesquisa"; sem o `h1` com o título da pesquisa e sem o `h2` homônimo.
- Lista de Seções com a classe `lista-secoes`: cada ligação com pelo menos 44 px de altura
  (FR-026).
- Contexto completo e botão "Concluir pesquisa" sem mudança.

## Confirmação (`concluida.html`)

- `h1` "Pesquisa concluída".
- "Suas respostas sobre {curso} foram registradas." ou "Suas respostas foram
  registradas.".
- "Obrigado pela sua participação." **só** sem texto de encerramento.
- Contexto completo (sem mudança), texto de encerramento (sem mudança) e a ligação "Ver sua
  trajetória no Ifes".

## Trajetória (`formacoes.html`)

| Situação de entrada | Conteúdo |
|---|---|
| Todas | Aviso (`situacao`, `salvo`, `saida`), quando houver; `h1` "Sua trajetória no Ifes" |
| Entrada resolvida | "Você concluiu {linha}." (sem linha: "Encontramos uma formação sua no Ifes."); "O Ifes quer saber como sua trajetória seguiu depois disso."; frase de FR-002; botão da ação |
| Seleção necessária | Frase de FR-002; "Cada formação tem sua própria pesquisa. Escolha por qual começar ou continuar; as outras continuam disponíveis aqui."; lista de pendentes (linha, complemento, situação, botão), na ordem da 007 |
| Sem entrada pendente, sem pesquisa, sem formação | Mensagem de estado atual, uma vez |
| Outras formações (quando há) | `h2` "Suas outras formações"; linha, complemento e situação só quando houver texto ("Pesquisa já respondida" ou o texto de ambiguidade) |

Formação: `<p><strong>{linha}</strong>` e, se houver complemento,
`<br><span class="nota">{complemento}</span></p>`. Sem linha: o texto neutro atual.

## Telas de estado (`aviso.html`) e falha de envio (`403_csrf.html`)

- `aviso.html`: só o rótulo da ligação muda para "Ver sua trajetória no Ifes".
- `403_csrf.html`: "Volte à página anterior e envie novamente.".

## Título da página (`base.html`)

- `Erro: ` quando o resumo é do tipo `"erros"`.
- `Faltam respostas: ` quando é do tipo `"pendencias"`.
- Nenhum prefixo nos demais casos.
