# Contrato: rodapé e envio da Seção

Complementa e, nos pontos indicados, substitui a seção da Seção do
[contrato de rotas da 008](../../008-interface-navegavel-pesquisa/contracts/rotas.md).
Rotas, métodos, autorização, CSRF, `never_cache` e telas de estado **não mudam**.

## Formulário da Seção

Ordem no documento (é também a ordem de foco):

1. `<button type="submit" disabled hidden>` — **bloqueador do envio implícito** (R2).
   Nunca visível, nunca focável, nunca enviado.
2. Perguntas (contrato do formulário da 008, com a marcação de R7).
3. `div.acoes.acoes-secao`:
   - "Salvar e continuar" — `type="submit"`, classe `primario`, **sem** `name`;
   - "Salvar e sair" — `type="submit"`, `name="depois"`, `value="sair"`, classe
     `secundario`.

Depois do formulário, em `div.saidas`:

4. "Voltar à seção anterior" — `GET` da Seção anterior em `passagens`, só se existir; nota
   "Alterações não salvas nesta página serão descartadas.".
5. "Sair sem salvar esta seção" — `GET /formacoes/`; nota "O que já foi salvo antes
   continua guardado.".

`depois` não é campo do formulário da Seção: é ignorado pela validação e pela gravação.
Qualquer valor diferente de `sair` equivale a "Salvar e continuar".

## `POST /participacoes/<participacao>/secoes/<posicao>/`

Os passos 1 a 3 são **idênticos** aos da 008 para os dois botões. Só o passo 4 depende de
`depois`.

| # | Situação | Salvar e continuar | Salvar e sair (`depois=sair`) |
|---|---|---|---|
| 1 | Participação concluída | 200 "já respondida"; nada gravado | Igual |
| 1 | `admite_escrita` falso (coleta encerrada) | 200 "período encerrado"; nada gravado | Igual |
| 1 | Seção ∉ `passagens` | 302 Seção atual `?aviso=percurso` (ou `/concluir/`); nada gravado | Igual |
| 2 | Formulário inválido (erro de forma) | 200 Seção, valores enviados, resumo tipo `"erros"`; nada gravado | Igual |
| 3 | `motivo_global` | Telas atuais ("já respondida", "período encerrado", 404); nada gravado | Igual |
| 3 | `erros_por_pergunta` (rejeição da 005) | 200 Seção, resumo tipo `"erros"`; nada gravado | Igual |
| 4 | Aceito, Seção com pendências | 302 mesma Seção `?pendencias=1` (**sem** `&salvo=1`) | 302 `/formacoes/?aviso=salvo` se `ha_resposta_na_secao`, senão `?aviso=saida` |
| 4 | Aceito, destino = Seção | 302 Seção de destino | Igual à linha anterior |
| 4 | Aceito, destino = finalização | 302 `/concluir/` | Igual à linha anterior |

`ha_resposta_na_secao` é calculado sobre a jornada relida **depois** da gravação
([research R3](../research.md#r3--regra-de-verdade-das-mensagens-de-salvamento)).

**Repetição** (toque duplo, reenvio do navegador): o segundo envio repete os passos com o
estado já gravado. Valor igual ao gravado não gera operação (008 FR-040), e o destino e o
aviso são os mesmos. Nada novo é criado.

## `GET /participacoes/<participacao>/secoes/<posicao>/`

Igual à 008, com estas mudanças:

- `h1` = título da Seção ou, sem ele, título da pesquisa ("Pesquisa" como último
  substituto); sem `h2` da Seção.
- `?pendencias=1` (pendências da 006 na Seção atual) → resumo tipo `"pendencias"`; frase
  de salvamento só com `ha_resposta_na_secao`. `&salvo=1` deixa de existir e, se
  presente, é ignorado.
- O resumo, de qualquer tipo, tem `tabindex="-1"`, `autofocus` e `role="alert"`.
- Linha de contexto: "Você está respondendo sobre: {linha}".

## Ligações (GET) — sem formulário

| Ligação | Destino | Em estados terminais |
|---|---|---|
| Voltar à seção anterior | Seção anterior em `passagens` no momento em que a página foi gerada | A rota da Seção aplica as regras atuais: "já respondida", "período encerrado" ou Seção atual com aviso de percurso |
| Sair sem salvar esta seção | `/formacoes/` | Sempre a trajetória |

## `GET /formacoes/`

Igual à 008, mais os códigos de aviso `salvo` e `saida`
([data-model](../data-model.md#avisos-da-trajetória-lista-fechada)). O aviso aparece
antes do `h1`, com `role="status"`, como o aviso `situacao`.
