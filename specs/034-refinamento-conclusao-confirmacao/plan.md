# Implementation Plan: Refinamento visual da conclusão e da confirmação

**Branch**: `claude/034-refinamento-conclusao` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

## Summary

Só apresentação na jornada (`trajetoria/interface`): os templates `conclusao.html` e
`concluida.html`, um bloco de `jornada.css` e textos fixos em `mensagens.py`. As views só
passam dados que já calculam (resumo da formação, contagem de partes, títulos). A regra de
destino da 033 não muda; só o texto do aviso `caminho` (B6). Revisão 1 da spec aprovada em
2026-10-12; a 033 foi integrada (#69) antes desta implementação.

## Decisões técnicas

| # | Decisão | Por quê |
|---|---|---|
| R1 | Revisão em `<details class="revisao">` com `<summary>` em `display: list-item` (marcador nativo), preenchimento para 44 px | Sem JavaScript (023 FR-035); o `display: flex` de `details.abertura` remove o marcador, e a spec pede o nativo (FR-002) |
| R2 | Lista em `<ol class="lista-revisao">` com `columns: 2 15rem` (multicoluna) e `break-inside: avoid` | A multicoluna enche a primeira coluna de cima para baixo e depois a segunda: a ordem visual é a do documento (FR-004). Com a fonte a 200% ou a 320 px, 15 rem não cabem duas vezes e a lista fica numa coluna sozinha. Uma grade (`grid`) poria as partes em linhas (1 2 / 3 4), contra a ordem de leitura |
| R3 | "Parte N" num `<span class="numero">` fora do link, só quando a Seção tem título | O nome acessível do link é só o título (lição do protótipo); a Seção sem título já se chama "Parte N" (023 FR-015) |
| R4 | Contexto compacto: o `contexto_compacto.html` das Seções, com `resumo_formacao` e `rotulo_formacao` passados pela `concluir_view` | Um componente só, com o mesmo texto de "dados não informados" e a mesma regra para a declarada |
| R5 | Confirmação: a identificação compacta é um `<p class="formacao-concluida">` dentro do bloco `.confirmacao`, depois da frase de registro, só sem formação declarada e só com resumo não vazio | B1; o nome da classe evita "contexto" (a ficha da 015 continua definida e testada) |
| R6 | "Ver minha trajetória no Ifes" com aparência de botão por um envoltório `<p class="acao-principal">` estilizado em CSS. O `<a href="/minha-trajetoria/">` continua igual | A marcação da ligação, que vários testes de 020, 021 e 024 verificam, não muda. Com uma próxima formação na tela, o envoltório não tem a classe e a ligação volta a ser link (FR-006) |
| R7 | Título "No Portal do Egresso" só quando a navegação do Portal existe (`navegacao` no contexto). Com o Portal desligado, as mesmas ligações vêm sem esse título | Não nomear um Portal que não está ligado (024 FR-027) |
| R8 | Textos novos em `mensagens.py`: `ULTIMA_ETAPA`, `FIM_DA_PESQUISA`, `IRREVERSIVEL`, `REVISAR`, `REVISAR_NOTA`, `partes(n)`, `NO_PORTAL`, `FORMACAO_CONCLUIDA`; `AVISOS["caminho"]` com o texto da B6 | Textos provisórios num lugar só (DP-801) |
| R9 | Foco: o comum da jornada. O resumo e os links da lista ganham `padding` para o contorno de 3 px e o halo de 6 px caberem sem corte pelas colunas | B5 |

## Constitution Check

Só apresentação: nenhum modelo, migração, rota, JavaScript, dependência ou token novo
(XXII). Os textos protegidos da Versão não mudam (VIII, 008 FR-033), nem a regra de destino
da 033. Nenhuma frase de finalidade (IX; 014 FR-039). A acessibilidade é verificada com
teclado, fonte a 200%, refluxo e leitor de tela (XX), e o celular é a referência (XXI).
**Aprovado.**

## Medidas e evidências

`specs/034-refinamento-conclusao-confirmacao/evidencias/`:

- `gerar_html.py`: num banco de demonstração próprio, guarda o HTML **servido** das telas.
  Usa o cliente de teste do Django contra o banco preparado, com as personas reais. As telas:
  - conclusão de Ana (revisão fechada e aberta);
  - conclusão com "Parte salva.";
  - parte nova com o aviso B6;
  - parte só de opcionais reapresentada (Versão de teste);
  - confirmação de Ana;
  - confirmação de Diego, com outra formação pendente;
  - confirmação de uma declarante.
- `capturar.py`: Chrome headless numa moldura, como nos protótipos. Captura e mede a 375 px, a
  1280 px e com fonte a 200%. Faz o **refluxo a 320 CSS px** separadamente: confere a
  ausência de rolagem horizontal e que cada elemento esperado (título, aviso, resumo, links,
  botão, ação principal) tem largura visível dentro da tela e não é cortado.
- Teclado e árvore de acessibilidade no navegador do app, sobre o servidor de demonstração.
- Leitor de tela: tentativa com o VoiceOver. Se não for possível no ambiente do agente, fica
  como pendência explícita no PR (autorizado pelo solicitante).

## Testes

- Revistos com nota, porque a ordem e a ficha mudam (023 FR-027, FR-028):
  `test_interface_conclusao.py` (tela de conclusão, título, confirmação, lista),
  `test_interface_esforco.py` (ordem da conclusão) e `test_interface_identidade.py` (a ficha
  depois das ações).
- Novos em `tests/interface/test_interface_refinamento.py`:
  - ordem da conclusão;
  - revisão sempre recolhida, inclusive com "Parte salva.";
  - "Parte N" fora do link e Parte 9 sem número repetido;
  - singular "1 parte";
  - ausência da ficha nas duas telas;
  - identificação compacta (presente, parcial, ausente);
  - ação principal única com e sem próxima formação;
  - Portal desligado sem "No Portal do Egresso";
  - declarada inalterada;
  - textos protegidos intactos e nenhuma frase de finalidade;
  - o aviso B6 nos dois casos (parte nova, e parte opcional já vista e deixada em branco);
  - CSS: multicoluna, marcador nativo e alvos.
- A suíte da 033 continua passando sem mudar expectativa.

## Riscos

- **Recorte do foco em multicoluna:** coberto por R9 e verificado nas capturas e no teclado.
- **Leitor de tela indisponível no ambiente:** pendência explícita, autorizada.
