# Contrato: rotas e telas

## Regras comuns

- **Ambiente.** Todas as rotas existem só no modo de demonstração (FR-130). Fora dele,
  respondem 404.
- **Proteções.** Toda escrita é POST com CSRF. Toda resposta com dado pessoal ou selo é
  `no-store`.
- **Selos.** Só em campo oculto de POST. Nunca em URL, cookie, sessão ou log. As views que
  os recebem usam `sensitive_post_parameters("selo")`. Selo vencido, adulterado ou de
  finalidade errada leva a `/acesso/`, sem detalhe.
- **Dados sensíveis.** CPF, data e HMACs nunca aparecem em URL, cabeçalho de
  redirecionamento ou log (FR-110).

## Egresso

| Rota | Método | Comportamento |
| --- | --- | --- |
| `/acesso/` (018) | POST | Em `NAO_CONFIRMADA`, além de "Conferir os dados", passa a mostrar o botão "Informar minha formação", num formulário próprio com o **selo de trânsito** em campo oculto (R6). Em `VERIFICACAO_INDISPONIVEL`, formato inválido e `CONFIRMADA`, nada muda |
| `/declaracao/` | POST | Recebe o selo de trânsito. Válido: estabelece a sessão do declarante (R7) e **renderiza na própria resposta**, sem redirecionar, porque o selo não pode ir para URL nem sessão: <br>• com declarações do par em Campanhas em coleta: a lista de FR-043 ("Continuar", "Resposta registrada" ou período encerrado) e o botão "Informar outra formação", num formulário POST para `/declaracao/nova/` com o selo oculto; <br>• sem declarações: o formulário da declaração. <br>Vencido ou inválido: redireciona para `/acesso/`, sem detalhe. Chave indisponível: tela de indisponibilidade técnica da 018 (FR-117) |
| `/declaracao/` | GET | Só com sessão do declarante; sem ela, vai para `/acesso/`. Lista as declarações do par com "Continuar" e "Resposta registrada". Sem selo, não oferece nova declaração: para informar outra formação, o egresso confirma os dados de novo em `/acesso/` |
| `/declaracao/nova/` | POST | **Sem os campos da formação:** exibe o formulário (nome, unidade, nível, curso e ano) com o selo de trânsito oculto. **Com os campos:** valida a forma. <br>• Selo vencido: volta a `/acesso/`. <br>• Resolve a Campanha (R9): nenhuma → "Não há pesquisa disponível no momento."; ambiguidade → tela da 007; uma → tela de confirmação com o contexto "Formação informada por você: …", o botão "Começar" e um **selo de início** novo (R6). <br>Não existe `GET /declaracao/nova/`: o selo nunca passa por URL |
| `/declaracao/comecar/` | POST | Consome o selo de início de forma **idempotente**. Na primeira vez, cria a declaração, os dados para consulta e a Participação (FR-016), atualiza a sessão e redireciona para `/participacoes/<id>/`. Atualização, duplo clique ou reenvio do mesmo selo levam à mesma Participação, sem criar outra. Falha de chave: indisponibilidade técnica, sem gravar nada |
| `/participacoes/<id>/…` (008) | GET/POST | Mesmas rotas e telas da jornada. A posse vem do sujeito da sessão (R19). Para âncora declarada: rótulo "informada por você" e mensagem final de FR-033 |
| `/acesso/sair/` (018) | POST | Também encerra a sessão do declarante |

**Mensagens.** Todas sem termos técnicos e sem afirmar validação (FR-006).

## Operador ("Validações de formação")

| Rota | Método | Comportamento |
| --- | --- | --- |
| `/validacoes-formacao/` | GET | Fila no escopo (FR-061, FR-063). Mostra nome, unidade, nível, curso e ano declarados, momento, Campanha e situação. Sem CPF, data nem Respostas. Sem capacidade: a recusa da 010 |
| `/validacoes-formacao/<id>/` | GET | Declaração; candidatas; outras declarações do mesmo CPF; aviso de conflito potencial; formulário de decisão. Fora do escopo: 404 indistinguível |
| `/validacoes-formacao/<id>/revelar/` | POST | Grava o acesso e mostra a mesma tela com nome, CPF e data descriptografados (R13). Dados descartados: "não estão mais disponíveis". Chave indisponível: "indisponível no momento", e nenhum acesso é registrado |
| `/validacoes-formacao/<id>/registrar/` | POST | Recebe o resultado (`confirmada` ou `nao_confirmada`) e, se confirmada, uma origem: `candidata=<uuid>`, `referencia_fonte=<texto>` ou os campos do acervo. Exige a confirmação explícita (campo de confirmação marcado). Sucesso: volta à fila com aviso. Falha (FR-074): reapresenta com o erro, sem gravar. Já decidida: aviso "já decidida" |

- **Formulário do acervo.** Os campos vêm **vazios**, nunca pré-preenchidos com o
  declarado. O declarado aparece ao lado, só para leitura (FR-082).
- **Acompanhamento (011).** O detalhe da Campanha mostra "Validações de formação: N na
  fila" e um link para `/validacoes-formacao/` quando o operador tem a capacidade (FR-101).

## Acessibilidade

A interface segue a mesma base da 015 e da 018:
- rótulos visíveis;
- erros junto ao campo e no resumo;
- foco no resumo de erro;
- teclado numérico para o ano;
- ordem lógica;
- 320 px.

A revelação é um botão, não um link. O resultado aparece com foco e anúncio.
