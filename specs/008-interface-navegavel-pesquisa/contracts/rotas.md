# Contrato: rotas da interface

Apps: `trajetoria.interface` (jornada) e `trajetoria.demonstracao` (adaptador
temporário). Atende FR-001 a FR-011, FR-019 a FR-031, FR-050 a FR-066, FR-083 a FR-090.

## Garantias comuns

- **Modo de demonstração**: com `settings.TRAJETORIA_DEMONSTRACAO` falso, **toda** rota
  responde 404 (`404.html`), antes de qualquer view (`ModoDemonstracaoMiddleware`).
- **Pessoa**: `pessoa_em_uso(request)` (cookie assinado, revalidado: existe e
  `fonte == "simulada"`). Rotas marcadas "exige Pessoa" redirecionam (302) a
  `/demonstracao/` quando ela é `None`.
- **Posse**: rotas com `<participacao>` buscam
  `Participacao.objects.filter(pk=…, conclusao__pessoa=pessoa)`; ausente → 404, igual para
  inexistente e alheia (FR-090).
- **Métodos**: só os listados; os demais → 405. Toda escrita é POST com CSRF (FR-083).
- **Cache**: `never_cache` em `/formacoes/…` e `/participacoes/…` (FR-088).
- **Redirecionamento após POST aceito** (FR-048).
- **Sem `agora`**: as operações leem o relógio por `momento_de_referencia` (research R18).
- **Sem dados em URL**: os únicos parâmetros de consulta são `pendencias=1`, `salvo=1` e
  `aviso ∈ {percurso, situacao}`; valores fora da lista são ignorados (FR-086). Os
  formulários enviam sempre para o endereço sem parâmetros (`action` explícito), para que
  uma reapresentação com erro não repita avisos da visita anterior.
- **Títulos de página**: "`<etapa>` — Trajetória Ifes (demonstração)", prefixo "Erro: "
  quando houver erros ou pendências (FR-071).

## Demonstração

### `GET /`

Exige nada. Sem Pessoa → 302 `/demonstracao/`. Com Pessoa → 302 `/formacoes/`.

### `GET /demonstracao/`

Lista as Pessoas de `fonte == "simulada"` (`PessoaListada`, data-model §3), cada uma com
um botão POST para `/demonstracao/escolher/`. Aviso de demonstração em destaque
(FR-003). Sem Pessoas → "Nenhuma pessoa fictícia preparada. Execute o preparo do cenário
de demonstração." Nenhum identificador técnico visível (o `pk` vai só no `value` do botão).

### `POST /demonstracao/escolher/`

Campo `pessoa` (`pk`). Pessoa inexistente ou de outra fonte → 404, nada alterado. Senão:
grava o cookie e 302 `/formacoes/`. Nada de domínio é criado (FR-009).

### `POST /demonstracao/encerrar/`

Apaga o cookie; 302 `/demonstracao/`. É o botão "Encerrar demonstração" do cabeçalho;
"Trocar de pessoa" é uma ligação para `/demonstracao/`, onde escolher outra Pessoa
substitui o cookie. Ambos aparecem em todas as páginas com Pessoa (FR-011).

## Formações

### `GET /formacoes/` — exige Pessoa

`situacao_de_entrada(pessoa)` (007) → tela conforme data-model §4 ("Situação de
entrada"). Nunca grava (FR-031). `?aviso=situacao` → faixa "A situação da pesquisa mudou.
Veja abaixo a situação atual."

### `POST /formacoes/entrar/` — exige Pessoa

Campo opcional `formacao` (`pk` da Conclusão).

| Caso | Resposta |
|------|----------|
| `formacao` ausente | `entrar(pessoa)` |
| `formacao` presente | `ConclusaoAcademica` buscada por `pk` (inexistente → mesma resposta de alheia); `entrar(pessoa, conclusao)` |
| `FormacaoDeOutraPessoa` | 404 "Formação não disponível" |
| `ParticipacaoRejeitada` | 200 "O período de resposta desta pesquisa foi encerrado." |
| participação em rascunho | 302 `/participacoes/<id>/` |
| participação concluída | 200 "Esta pesquisa já foi respondida." |
| sem participação | 302 `/formacoes/?aviso=situacao` |

A interface **nunca** chama `iniciar_participacao` (FR-029).

## Participação

Todas exigem Pessoa e posse. A jornada é sempre `situacao_da_jornada(participacao)`
(006); `ParticipacaoRejeitada(ESTRUTURA_NAO_SUPORTADA)` → 200 "Esta pesquisa não está
disponível no momento."

### `GET /participacoes/<participacao>/`

| Jornada | Resposta |
|---------|----------|
| concluída | 302 `/participacoes/<id>/concluida/` |
| `admite_escrita` falso | 200 "período encerrado" |
| `finalizada` | 302 `/participacoes/<id>/concluir/` |
| senão | 302 `/participacoes/<id>/secoes/<posição de secao_atual>/` |

### `GET /participacoes/<participacao>/secoes/<posicao>/`

| Jornada | Resposta |
|---------|----------|
| concluída | 200 "Esta pesquisa já foi respondida." (sem formulário, sem valores) |
| `admite_escrita` falso | 200 "período encerrado" (sem formulário) |
| Seção `posicao` ∉ `passagens` (inclusive posição inexistente) | 302 Seção atual, `?aviso=percurso` (ou `/concluir/` se finalizada) |
| senão | 200 Seção com `FormularioDaSecao` (valores de `respostas`) |

Conteúdo da página de Seção (FR-027, FR-032 a FR-039, FR-054):

1. Faixa de demonstração e cabeçalho (Pessoa em uso, trocar, encerrar).
2. `h1` = título da Versão (ou "Pesquisa").
3. Resumo de erros/pendências (se houver), logo abaixo do `h1` — antes do contexto e do
   texto de abertura, para ficar visível sem rolar também no celular.
4. "Sobre a sua formação" — contexto da Conclusão em **uma linha** (curso · unidade ·
   ano, `resumo_da_formacao`); a lista completa fica no início, na conclusão e na
   confirmação.
5. Se é a primeira Seção da Versão: `texto_abertura`.
6. `h2` = título da Seção (se houver) e texto introdutório (se houver).
7. Perguntas, na ordem da Versão (contrato do formulário).
8. Botão **"Salvar e continuar"** (primeiro botão do formulário).
9. Se há Seção anterior em `passagens`: ligação "Voltar à seção anterior", com a nota
   "Alterações não salvas nesta página serão descartadas."
10. Ligação "Sair e continuar depois" → `/formacoes/` (nota: "O que já foi salvo fica
    guardado. O que foi marcado nesta página e ainda não foi salvo será descartado.").

`?pendencias=1` → se a Seção é a última de `passagens` e tem `pendentes`, mostra as
pendências (resumo + mensagem por Pergunta); caso contrário, ignora. `&salvo=1`
(acrescentado só pelo redirecionamento de um envio aceito) acrescenta "O que já foi
preenchido nesta seção foi salvo.". `?aviso=percurso` →
faixa "As respostas anteriores mudaram o caminho da pesquisa. Esta é a seção a responder
agora."

### `POST /participacoes/<participacao>/secoes/<posicao>/`

Passos (research R8):

1. Jornada: concluída → 200 "já respondida"; `admite_escrita` falso → 200 "período
   encerrado"; Seção ∉ `passagens` → 302 Seção atual com `?aviso=percurso`. **Nada
   gravado.**
2. `FormularioDaSecao(dados)`; inválido → 200 Seção com erros e valores enviados. **Nada
   gravado.**
3. `salvar_secao` (contrato do formulário). `motivo_global`:
   `PARTICIPACAO_CONCLUIDA` → 200 "já respondida"; `COLETA_NAO_ADMITIDA` → 200 "período
   encerrado"; `PARTICIPACAO_INEXISTENTE` → 404. `erros_por_pergunta` → 200 Seção com
   erros e valores enviados. **Nada gravado** em qualquer desses casos.
4. Jornada de novo; `Passagem` da Seção `posicao`:
   - `pendentes` → 302 mesma Seção `?pendencias=1&salvo=1`;
   - `destino` = id de Seção → 302 Seção de destino, que é a passagem seguinte do
     percurso da 006;
   - `destino` = `Saida.FINALIZACAO` → 302 `/concluir/`.

A interface nunca calcula destino, regra, encaminhamento ou obrigatoriedade (FR-051).

### `GET /participacoes/<participacao>/concluir/`

| Jornada | Resposta |
|---------|----------|
| concluída | 302 `/concluida/` |
| `admite_escrita` falso | 200 "período encerrado" |
| não `finalizada` | 302 Seção atual |
| `finalizada` | 200 tela de conclusão |

Tela de conclusão (FR-056, FR-060, FR-061): contexto da formação; "Você chegou ao fim da
pesquisa. Depois de concluída, ela não poderá ser alterada."; lista de Seções de
`passagens` com ligações para revisar (Seção sem título → "Seção <posição>"); botão POST
**"Concluir pesquisa"**. Nenhum valor declarado.

### `POST /participacoes/<participacao>/concluir/`

`concluir(participacao)` (006):

| Resultado | Resposta |
|-----------|----------|
| `CONCLUIDA` / `JA_CONCLUIDA` | 302 `/concluida/` |
| `COLETA_NAO_ADMITIDA` entre os motivos | 200 "período encerrado" |
| só `OBRIGATORIA_PENDENTE` | 302 Seção atual `?pendencias=1` |
| qualquer outro conjunto de motivos (estrutura, incoerência, motivo futuro) | 200 "pesquisa indisponível" |

Precedência quando há vários motivos: coleta → somente pendências → indisponível.

### `GET /participacoes/<participacao>/concluida/`

Rascunho → 302 `/participacoes/<id>/`. Concluída → 200 confirmação (FR-062, FR-063):
"Pesquisa concluída", "Obrigado pela sua participação.", contexto da formação,
`texto_encerramento` da Versão (se existir), ligação "Voltar às suas formações". Sem
respostas, comprovante, data, identificador ou ação de edição.

## Páginas de erro

| Situação | Template | Status |
|----------|----------|--------|
| Rota inexistente, modo desligado, recurso alheio | `404.html` autônomo (não herda a base; sem faixa nem cabeçalho de Pessoa) — "Página não encontrada." + ligação para `/` | 404 |
| Falha de CSRF | `403_csrf.html` autônomo — "Não foi possível confirmar o envio. Volte à página anterior, recarregue e tente novamente." | 403 |
| Erro inesperado | `500.html` (estático) — "Não foi possível concluir a operação. Tente novamente." + ligação para `/` | 500 |

Nenhuma contém traceback, nome de modelo, motivo interno, identificador ou nome de Pessoa
(FR-001, FR-068, FR-069). As três são **autônomas**: não herdam `interface/base.html`
nem dependem do processador de contexto. Falhas 500 são registradas pelo logger `django.request` (console).
