# Data Model: Interface navegável mínima da pesquisa

**Nenhuma entidade, tabela, coluna ou migração nova** (FR-091; SC-017). Os apps
`trajetoria.interface` e `trajetoria.demonstracao` não têm `models.py`.

Este documento registra (1) o que a interface **lê** e **escreve**, sempre pelas Features
001 a 007; (2) o único estado de apresentação entre requisições; (3) os valores em memória
que a interface monta para os templates; (4) o mapeamento de estados de domínio para
telas.

## 1. Entidades consumidas (inalteradas)

| Entidade | Feature | Lida pela interface | Escrita pela interface |
|----------|---------|---------------------|------------------------|
| `Pessoa` | 001 | `nome`, `fonte` (filtro "simulada"), `conclusoes` | Nunca (o comando de demonstração incorpora pela 001) |
| `ConclusaoAcademica` | 001 | `curso`, `unidade`, `nivel`, `modalidade`, `forma_oferta`, `ano_conclusao`, `data_conclusao` (para contexto); `pk` (seleção) | Nunca |
| `Versao` / `ConteudoVersao` | 002 | `titulo`, `texto_abertura`, `texto_encerramento`, Seções | Nunca (o comando publica cópia pela 002) |
| `Secao` / `ConteudoSecao` | 002 | `posicao`, `titulo`, `texto`, Perguntas | Nunca |
| `Pergunta` / `ConteudoPergunta` | 002 | `posicao`, `tipo`, `texto`, `texto_explicativo`, `obrigatoria`, `escala` | Nunca |
| `Opcao` / `ConteudoOpcao` | 002 | `posicao`, `texto`, `complemento_textual` | Nunca |
| `Campanha` | 004 | **Nunca diretamente** (só pela 007/005/006) | Nunca (o comando cria/abre pela 004) |
| `Participacao` | 005/006 | `pk`, `conclusao` (verificação de posse), `campanha.versao` (conteúdo), `concluida_em` | Só pela entrada da 007 (início) e por `concluir` (006) |
| `Resposta` / `RespostaOpcao` | 005 | Via `SituacaoDaJornada.respostas` | Só por `responder_*` e `remover_resposta` (005) |

Instâncias ORM de `Pergunta` e `Opcao` são lidas (somente leitura) porque as operações da
005 recebem instâncias, não identificadores (research R7). `Participacao` é lida para
verificar posse (`conclusao__pessoa`) antes de qualquer outra coisa.

## 2. Estado de apresentação entre requisições

| Estado | Onde | Conteúdo | Ciclo de vida | Regras |
|--------|------|----------|---------------|--------|
| Pessoa de demonstração em uso | Cookie assinado `trajetoria_demonstracao_pessoa` (`httponly`, `SameSite=Lax`, de sessão do navegador) | `pk` da Pessoa | Criado ao escolher; apagado ao trocar/encerrar ou ao fechar o navegador | Revalidado a cada requisição: existe **e** `fonte == "simulada"`; senão é ignorado (FR-008 a FR-010) |
| Token CSRF | Cookie `csrftoken` padrão do Django | Segredo CSRF | Padrão do Django | Mecanismo de segurança, não de domínio |

**Não existe** nenhum outro estado: nada de formação escolhida, Participação corrente,
Seção atual, Seções visitadas, progresso ou rascunho de formulário não enviado (FR-091).

## 3. Valores em memória (não persistidos)

Montados por requisição e descartados. São apresentação, não domínio; nenhum é gravado.

### `ItemContexto` (contexto da formação)

Função `contexto_da_formacao(conclusao) -> list[tuple[str, str]]` em
`trajetoria/interface/apresentacao.py`. Pares (rótulo, valor) **só** para atributos
informados, nesta ordem: Curso, Unidade, Ano de conclusão (ou data, se informada), Nível,
Modalidade, Forma de oferta. Atributo `None` é omitido (FR-026). Lista vazia → o
template mostra "Dados da formação não informados pela fonte".

### `PessoaListada` (entrada de demonstração)

`(pk, nome_apresentado, resumos)`: `nome_apresentado` = `nome` ou "Pessoa fictícia sem
nome informado"; `resumos` = para cada Conclusão, `curso · unidade · ano` com os
atributos existentes. Ordem: `nome` (nulos por último), depois `pk` — determinística, sem
significado. Apenas Pessoas com `fonte == "simulada"` (FR-007, FR-008).

### `FormularioDaSecao` (Django `forms.Form`)

Construído a partir de `ConteudoSecao` + `respostas`. Campos por Pergunta (posição `n`):

| Campo | Tipo de Pergunta | Valor | Observação |
|-------|------------------|-------|------------|
| `p<n>` | escolha única | posição da Opção (`str` de inteiro) ou vazio | rádio (≤ 10 Opções) ou lista suspensa (> 10) |
| `p<n>` | escolha múltipla | lista de posições de Opção | caixas de seleção |
| `p<n>` | texto curto | texto exatamente como digitado (`strip=False`) | só espaços = ausente |
| `p<n>` | escala | inteiro entre `inicio` e `fim` | rádios |
| `p<n>-complemento` | escolha com Opção `complemento_textual` | texto (`strip=False`) | só espaços = ausente |
| `p<n>-remover` | escolha única em rádio e escala **não obrigatórias** | booleano | prevalece sobre `p<n>` |

Todos `required=False`. Validação de forma: Opção existente, ponto de escala existente,
complemento só com a Opção que o admite marcada. Contrato completo em
[contracts/formulario-secao.md](contracts/formulario-secao.md).

### `ResultadoDaGravacao`

Retorno de `salvar_secao`: `erros_por_pergunta: dict[int, list[str]]` (posição →
mensagens), `motivo_global: Motivo | None` (`COLETA_NAO_ADMITIDA`,
`PARTICIPACAO_CONCLUIDA`, `PARTICIPACAO_INEXISTENTE`) e `operacoes: int` (quantas
operações da 005 foram aplicadas; 0 se houve qualquer erro, pois tudo foi desfeito).

## 4. Mapeamento de estados de domínio para telas

### Situação de entrada (007) → tela de formações

| `ResolucaoDaEntrada` | Tela | Ação |
|----------------------|------|------|
| `SEM_FORMACAO` | "Não encontramos formações concluídas no Ifes associadas a você." | — |
| `SEM_PESQUISA` | "No momento, não há pesquisa disponível para as suas formações." + formações | — |
| `SEM_ENTRADA_PENDENTE` | "Não há pesquisa pendente para você neste momento." + formações com situação | — |
| `ENTRADA_RESOLVIDA` | "Esta pesquisa refere-se à sua formação:" + contexto de `pendentes[0]` | um botão POST sem `formacao`: "Iniciar a pesquisa" (`DISPONIVEL_PARA_INICIAR`) ou "Continuar a pesquisa" (`DISPONIVEL_PARA_RETOMAR`) |
| `SELECAO_NECESSARIA` | "Sobre qual formação do Ifes você responderá esta pesquisa?" + `pendentes` | um botão POST por formação, com `formacao=<pk>` |

Formações não pendentes, em qualquer resolução, aparecem em "Suas outras formações" com:

| `SituacaoDaFormacao` | Texto |
|----------------------|-------|
| `SEM_PESQUISA` | "Sem pesquisa disponível no momento." |
| `JA_CONCLUIDA` | "Pesquisa já respondida." |
| `AMBIGUIDADE_OPERACIONAL` | "A pesquisa referente a esta formação não está disponível neste momento." |

Nenhuma Campanha é nomeada, contada ou identificada (FR-023, FR-024).

### Resultado da entrada (007) → próxima tela

| Resultado | Próxima tela |
|-----------|--------------|
| `Entrada.participacao` em rascunho (criada ou não) | `/participacoes/<id>/` → Seção atual |
| `Entrada.participacao` com `concluida_em` | "Esta pesquisa já foi respondida." |
| `Entrada.participacao is None` | `/formacoes/?aviso=situacao` (situação atual reavaliada) |
| `FormacaoDeOutraPessoa` | 404 "Formação não disponível" |
| `ParticipacaoRejeitada` (coleta não admitida) | "O período de resposta desta pesquisa foi encerrado." |

### Jornada (006) → telas da Participação

| Condição (lida de `SituacaoDaJornada`) | Tela |
|----------------------------------------|------|
| `concluida_em` preenchido | "Esta pesquisa já foi respondida." (em Seção/conclusão); confirmação em `/concluida/` |
| `admite_escrita` falso (rascunho) | "O período de resposta desta pesquisa foi encerrado. As respostas salvas anteriormente foram preservadas." |
| `ParticipacaoRejeitada(ESTRUTURA_NAO_SUPORTADA)` | "Esta pesquisa não está disponível no momento." |
| Seção pedida ∉ `passagens` | redireciona à Seção atual (`?aviso=percurso`) |
| `finalizada` e `pode_concluir` | tela de conclusão |
| não `finalizada` | Seção (`secao_atual` por padrão) |

### Rejeições da 005/006 → mensagens

| `Motivo` | Escopo | Mensagem |
|----------|--------|----------|
| `OPCAO_DE_OUTRA_PERGUNTA`, `VALOR_INCOMPATIVEL` | Pergunta | "Selecione uma das opções apresentadas." |
| `ESCALA_FORA_DOS_LIMITES` | Pergunta | "Selecione um valor da escala." |
| `COMPLEMENTO_NAO_ADMITIDO` | Pergunta | "Para descrever, marque a opção «<texto da Opção>»." |
| `VALOR_VAZIO` | Pergunta | "Preencha a resposta ou deixe o campo em branco." (só ocorre por adulteração, pois vazio = ausente) |
| `PERGUNTA_DE_OUTRA_VERSAO` | Pergunta | "Não foi possível salvar esta resposta." (só por adulteração) |
| `OBRIGATORIA_PENDENTE` (006) | Pergunta | "Esta pergunta é obrigatória." |
| `COLETA_NAO_ADMITIDA` | global | tela "período encerrado" |
| `PARTICIPACAO_CONCLUIDA` | global | tela "já respondida" |
| `PARTICIPACAO_INEXISTENTE` | global | 404 |
| `ESTRUTURA_NAO_SUPORTADA`, incoerência na conclusão | global | tela "pesquisa indisponível" |

Nenhuma mensagem contém motivo interno, identificador ou valor declarado (FR-068).

## 5. Origem dos dados apresentados

Conforme a spec ("Origem dos Dados"): o contexto da formação é **institucional** e
aparece numa região própria (`<section aria-labelledby="contexto">` com o título "Sobre a
sua formação"), separada das Perguntas; os valores dos campos são **declarados** e só
existem como Respostas da 005. Nenhum valor institucional é usado como `initial` de campo
(FR-028).
