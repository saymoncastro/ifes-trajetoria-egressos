# Data Model: Polish consolidado da jornada do egresso

**Nenhuma entidade, tabela, coluna ou migração nova** (FR-042). Este documento descreve só
os **dados de apresentação** que as views passam aos templates. Todos são derivados, a
cada requisição, de entidades existentes e nunca são persistidos.

## Entidades de domínio consumidas (sem alteração)

| Entidade | Feature | Uso nesta feature | Origem |
|---|---|---|---|
| Conclusão Acadêmica | 001 | Linha e complemento da formação; frase de entrada; curso na confirmação | Institucional |
| Situação de entrada e Formação (situação, ordem) | 007 | Tela de trajetória, na ordem devolvida | Derivado pela 007 |
| Participação e Respostas atuais | 005 / 006 | Gravação por "Salvar e continuar" e "Salvar e sair"; predicado de R3 | Declarado |
| Jornada (passagens, pendências, destino) | 006 | Destinos e pendências, como hoje | Derivado pela 006 |
| Conteúdo da Versão (título, Seções, Perguntas, textos) | 002 | Títulos principais, abertura, encerramento | Instrumento |

## Dados de apresentação

### Formação apresentada (tela de trajetória)

| Campo | Tipo | Regra |
|---|---|---|
| `pk` | identificador da Conclusão | Como hoje; só no valor do botão de escolha (008 FR-086) |
| `linha` | texto | `resumo_da_formacao` (existente): curso · unidade · ano informados; vazio se nenhum |
| `complemento` | texto | Nível · modalidade · forma de oferta informados; vazio se nenhum (FR-034) |
| `situacao` | texto ou ausente | `SITUACAO_DA_FORMACAO`, **sem texto** para "sem pesquisa" (FR-036) |
| `acao` | texto ou ausente | "Iniciar a pesquisa" / "Continuar a pesquisa" (como hoje) |

A lista preserva a ordem de `situacao.formacoes`/`situacao.pendentes` (007). Nenhuma
ordenação é aplicada (FR-035).

### Resumo da Seção

| Campo | Tipo | Regra |
|---|---|---|
| `tipo_resumo` | `"erros"` \| `"pendencias"` \| ausente | `"pendencias"` só no GET com `?pendencias=1` e pendências da 006; `"erros"` só na resposta de POST com erro de forma ou rejeição da 005; nunca os dois (C3) |
| `itens` | lista de (âncora, texto) | Como hoje: "pergunta — mensagem" |
| `ha_resposta_na_secao` | booleano | R3: alguma Pergunta da Seção tem Resposta gravada (lido da jornada) |

**Derivações**

| Valor | Com `"erros"` | Com `"pendencias"` |
|---|---|---|
| Prefixo do título da página | `Erro:` | `Faltam respostas:` |
| Título do resumo | "Há problemas nesta seção" | "Ainda faltam estas perguntas:" |
| Frase de salvamento | nunca | só com `ha_resposta_na_secao` |
| Marca por Pergunta | `Erro: …` | `Falta responder: …` |

### Avisos da trajetória (lista fechada)

| Código | Quando é emitido | Texto (provisório, DP-801) |
|---|---|---|
| `situacao` | Já existe (008) | "A situação da pesquisa mudou. Veja abaixo a situação atual." |
| `salvo` | "Salvar e sair" aceito e `ha_resposta_na_secao` | "O que você respondeu nesta seção está salvo. Você pode continuar a pesquisa quando quiser." |
| `saida` | "Salvar e sair" aceito sem Resposta gravada na Seção | "Você pode continuar a pesquisa quando quiser." |

Qualquer outro valor de `aviso` é ignorado, como hoje.

### Confirmação

| Campo | Regra |
|---|---|
| `curso` | `participacao.conclusao.curso`; ausente → frase sem curso (FR-038) |
| `texto_encerramento` | Da Versão, como hoje; quando existe, suprime o agradecimento fixo (FR-040) |

## Estados e transições

Nenhuma máquina de estados nova. A Participação continua com os estados da 005/006
(rascunho → concluída). "Salvar e sair" só escolhe outro destino de redirecionamento para
um envio aceito ([contrato do rodapé](contracts/rodape-secao.md)).
