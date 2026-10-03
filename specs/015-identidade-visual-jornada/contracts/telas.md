# Contrato: o que muda em cada tela

Só apresentação. Textos, ordem, rotas, comportamento e marcação acessível da 014/008 não
mudam (FR-036), salvo as duas mudanças de marcação indicadas.

## Matriz de inclusão das folhas

| Página | `estilo.css` (tokens + `.pergunta`) | `jornada.css` | Shell novo |
|---|---|---|---|
| Trajetória, Seções, conclusão, confirmação, telas de estado | Sim | **Sim** | **Sim** |
| Entrada e operador da demonstração | Sim | **Sim** | **Sim** (D7) |
| Prévia de Seção do editor | Sim (Perguntas mudam) | Não | Não |
| Demais telas do editor e do acompanhamento | Sim (sem efeito visual) | Não | Não |
| 403, 404, 500 | Sim (sem efeito visual) | Não | Não (R5) |

## Seção (`secao.html` e `perguntas/*.html`)

| Elemento | Mudança visual | Marcação |
|---|---|---|
| Pergunta | 48 px entre Perguntas; enunciado 18/600/1,4; auxiliares 15 px suave | Inalterada |
| Rádio / caixa | `accent-color` de ação; linha marcada com acento 4 px + fundo de seleção; hover | Inalterada |
| Escala | Células com contorno forte 1 px e `--raio`; vão de 4 px; selecionada com acento | Inalterada |
| Contexto compacto | Fio `--cor-marca` + fundo `--cor-institucional` | Inalterada |
| Resumo pendência / erro | Fio lateral 4 px + contorno 1 px na cor do estado; `:focus` visível | Inalterada |
| Frase por Pergunta | Cor do estado (IV-03, baseline) | Inalterada |
| Rodapé de ações | Cores por token; hierarquia e largura total da 014 inalteradas | Inalterada |
| Divisor `.saidas` | Borda suave | Inalterada |

## Trajetória (`formacoes.html`, `formacao.html`)

| Elemento | Mudança visual | Marcação |
|---|---|---|
| Aviso | Variante `aviso-sucesso` (`salvo`) ou `aviso-informacao` (`saida`, `situacao`) | Classe de variante acrescentada |
| Frase de entrada | Linha da formação destacada | **`<strong>` em volta da linha**; texto idêntico |
| Item de formação | Linha 600; complemento 15 px suave; situação 400; espaço simétrico; divisor suave | **Situação: `<strong>` → `<span class="situacao">`**; texto idêntico |
| Ação principal | Largura total até `30em` | Inalterada |

## Conclusão e confirmação (`conclusao.html`, `concluida.html`)

| Elemento | Mudança visual | Marcação |
|---|---|---|
| Ficha da formação | Fio `--cor-marca` + fundo institucional; `dl` empilhada até `30em` | Inalterada |
| "Concluir pesquisa" | Largura total até `30em` | Inalterada |
| Topo da confirmação | Fio de acento 4 px `--cor-sucesso` no bloco `h1` + frase de registro | Wrapper do bloco, se necessário; texto idêntico |

## Seção com aviso de percurso (`secao.html`)

Aviso `percurso` com variante `aviso-informacao`.

## Telas de estado (`aviso.html`)

Só o shell e os tokens; conteúdo inalterado.
