# Validação: Refinamento visual da conclusão e da confirmação (034)

**Executada em 2026-10-12** sobre esta branch, depois da integração da 033 (#69).

## Testes automatizados

- `tests/interface/test_interface_refinamento.py` (13 testes):
  - ordem da conclusão e da confirmação;
  - revisão sempre recolhida, inclusive com "Parte salva." (B4);
  - "Parte N" fora do link e Parte 9 sem número repetido;
  - ordem do documento igual à do percurso;
  - singular "1 parte";
  - CSS: marcador nativo, multicoluna, alvos;
  - identificação compacta presente, parcial e ausente (B1);
  - ação principal única com outra formação pendente;
  - Portal desligado sem o título do bloco;
  - declarada inalterada;
  - textos protegidos e nenhuma frase de finalidade;
  - **aviso B6 nos dois casos**: parte nova no percurso ("trabalha → não trabalha") e parte
    só de opcionais já visitada e deixada em branco (Versão de teste).
- Revistos com nota (023 FR-027 e FR-028, revistos pela 034):
  - `test_interface_conclusao.py`: tela, título, confirmação e lista;
  - `test_interface_esforco.py`: ordem da conclusão;
  - `test_interface_identidade.py`: a ficha depois das ações.
- **Garantias da 033** preservadas: `test_interface_revisao.py` passa sem mudança de
  expectativa (o aviso é lido de `mensagens.AVISOS["caminho"]`).
- **Fronteira do núcleo:** o título "No Portal do Egresso" vem do slot neutro `produto`, e o
  núcleo continua sem mencionar o Portal (`tests/portal/test_fronteiras.py`).

## Medidas reais

HTML **servido** pela aplicação, guardado por [`evidencias/gerar_html.py`](evidencias/gerar_html.py)
num banco de demonstração descartável, recém-preparado:
- Ana, percurso "trabalha e estuda": conclusão, volta de revisão e aviso B6 na parte nova;
- Diego: confirmação com outra formação pendente;
- uma declarante.

Captura e medida por [`evidencias/capturar.py`](evidencias/capturar.py) (Chrome headless).
Números em `evidencias/medidas.json`; capturas em `evidencias/capturas/`. Valores em px, com
a faixa de demonstração incluída (ela existe na tela servida).

| Tela | 375 px: ação / conteúdo | 1280 px: ação / conteúdo |
|---|---:|---:|
| Conclusão (revisão fechada) | **690** / 738 | 570 / 618 |
| Conclusão, volta de revisão ("Parte salva.") | **764** / 812 | 644 / 692 |
| Conclusão (revisão aberta) | 1.448 / 1.496 | 987 / 1.035 |
| Parte nova com o aviso B6 | 836 / 1.060 | 731 / 933 |
| Confirmação (Ana) | 758 / 853 | 618 / 713 |
| Confirmação com outra formação (Diego) | 807 / 1.018 | 639 / 849 |
| Confirmação da declarada | 506 / 856 | 434 / 668 |

A 375×812, "Concluir pesquisa" fica na primeira tela com a revisão fechada, inclusive na
volta de uma revisão (SC-002). Para isso, nenhum espaçamento, fonte ou alvo foi reduzido.
O protótipo, sem a faixa, media 666 px.

### Fonte a 200% (WCAG 1.4.4) e refluxo a 320 CSS px (WCAG 1.4.10)

Verificações separadas, nas 7 telas acima:
- fonte a 200% a 375 e a 1280 px;
- refluxo a 320 CSS px.

Cada verificação confere a rolagem horizontal e também cada elemento esperado da tela:
- presente e visível;
- dentro da largura;
- sem conteúdo cortado.

Os elementos verificados incluem título, aviso, resumo da revisão, cada link da lista,
"Parte N", botão, identificação, ação principal e convite.

| Variante | Telas | Rolagem horizontal | Elementos ausentes, cortados ou fora da tela |
|---|---:|---|---|
| 375 px com fonte a 200% | 7 | nenhuma | nenhum |
| 1280 px com fonte a 200% | 7 | nenhuma | nenhum |
| Refluxo a 320 CSS px | 7 | nenhuma | nenhum |

A 1280 px, a lista aberta usa duas colunas, preenchidas de cima para baixo: Partes 1 a 4
na primeira e 5 a 9 na segunda (`capturas/conclusao-aberta-1280.png`). Com a fonte a 200% e
no refluxo, a lista fica em uma coluna.

## Teclado

No navegador do app (Chromium), a 375×812, sobre o HTML servido da conclusão com "Parte
salva.":

| Verificação | Resultado |
|---|---|
| Ordem de Tab | "Pular para o conteúdo" → "Sair" → resumo da revisão → (aberta) os 9 links, na ordem do percurso → "Concluir pesquisa" |
| Abrir e fechar o resumo | Enter abre; Espaço fecha |
| Foco | O comum da jornada: contorno de 3 px com afastamento de 2 px e halo amarelo de 6 px. Nenhum dos 11 alvos de `main` tem contorno ou halo fora da tela (margem de 11 px conferida); na captura ampliada, o foco do primeiro link aparece inteiro |
| Alvos | Todos os 11 alvos de `main` com pelo menos 44 px de altura |
| "Parte salva." | Exposto como `status` |
| Marcador | Nativo (▸/▾), com o resumo em `list-item` |

## Leitor de tela (US3.5) — PENDENTE

**Não executado.** O agente não liga o VoiceOver nem o NVDA, porque isso muda uma
configuração do sistema. A árvore de acessibilidade do navegador do app foi lida e mostra:
- `status` "Parte salva.";
- o título;
- a região do contexto;
- a lista com "Parte N" seguido do link com o título;
- os links com o nome igual ao título;
- o botão.

Essa ferramenta não expõe o estado aberto ou fechado do resumo, e ela não substitui um
leitor de tela.

Roteiro a executar antes da aprovação final (VoiceOver, Safari ou Chrome, macOS):
1. Na conclusão com "Parte salva.": o aviso é anunciado ao carregar.
2. O resumo é anunciado como controle expansível, com o estado fechado; ao abrir, aberto.
3. Cada item é lido como "Parte N", seguido do link com o título; a Parte 9, como link
   "Parte 9".
4. "Depois de concluída, a pesquisa não poderá ser alterada." é lido antes do botão.
5. Na confirmação: título, frase de registro, "Formação: …", texto de encerramento, título
   do bloco e a ligação "Ver minha trajetória no Ifes", nessa ordem.

## Textos protegidos e fronteiras

- Iguais aos de hoje:
  - "Pesquisa concluída";
  - a frase de registro;
  - o texto de encerramento da Versão ("Este formulário chegou ao fim!" e o agradecimento);
  - a Parte 9 sem título.
- Nenhuma frase de finalidade, uso, contato ou periodicidade foi acrescentada.
- D3 e D4 seguem pendentes.
- A confirmação da declarada continua com a ficha e a ligação "Ver suas formações
  informadas".
