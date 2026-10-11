# Roteiro com leitor de tela — versão C (P4)

Pendência P4 da [preparação do Checkpoint 1](../../024-inicio-egresso-portal/evidencias/checkpoint-1/preparacao-sessao.md).
Complementa o [roteiro com teclado de 2026-10-11](../validacao.md#roteiro-manual-com-teclado-e-árvore-de-acessibilidade-2026-10-11).

> **Situação: NÃO EXECUTADO.** Os campos de resultado estão em branco. Quem executar
> preenche e registra o resultado na [validação da 032](../validacao.md).

## Preparação

- **Leitor e navegador:** VoiceOver com Safari, no macOS (Cmd+F5 liga e desliga), ou NVDA
  com Firefox ou Chrome, no Windows. Anotar as versões.
- **Ambiente:** o mesmo do Checkpoint 1, com banco recém-preparado. Anotar o commit.
- **Largura:** 375×812, em modo de dispositivo do navegador. Depois, a largura de desktop.
- **Persona:** Ana. Para o encontro, Bruno.
- **Dados:** e-mail fictício `verificacao-leitor@example.invalid`.

Para cada passo, anotar o que foi anunciado, se a tarefa foi concluída e qualquer obstáculo.

## Passos

| # | Tela e ação | O que conferir | Resultado |
|---|---|---|---|
| 1 | Página pública: ler do início | Título da página, h1 "Sua história com o Ifes", linha Ingresso → Adiante lida como lista, selos "Exemplo com dados fictícios" anunciados, decoração não anunciada | |
| 2 | Página pública: lista de títulos (rotor do VoiceOver ou H no NVDA) | Títulos na ordem da página | |
| 3 | Página pública: "Conhecer o Portal" | Leva a `/entrar/` | |
| 4 | `/entrar/`: abrir "Dados fictícios para demonstração" e usar a Ana | O estado expandido do painel é anunciado; os botões são distinguíveis pelo nome | |
| 5 | Início: ler do início | Ambiente de demonstração, navegação "Portal do Egresso" com o item atual, h1, proveniência ("Nada aqui foi respondido por você") | |
| 6 | Início: linha da trajetória | "Hoje" e "Adiante" anunciados como texto, sem depender da cor | |
| 7 | Início: lista de links | Links distinguíveis fora de contexto ("Baixar meu card", oportunidade com "site externo") | |
| 8 | Participação → Quero contribuir | Grupos "Como você quer contribuir?" e "Por qual formação?" anunciados com a legenda; dica da mensagem | |
| 9 | Contribuir: Continuar sem escolher a forma | O resumo de erro é anunciado e o foco vai para a forma | |
| 10 | Confira e envie: e-mail inválido | O erro é anunciado com o campo | |
| 11 | Confira e envie: enviar com o e-mail fictício | **A-02:** "Contribuição enviada." é anunciado? Se não, a pessoa percebe o envio pelo h1 "Sua contribuição"? | |
| 12 | Retirar a contribuição | **A-02:** "Contribuição retirada." é anunciado? | |
| 13 | Minha trajetória | Texto alternativo do card; caixa "Incluir meu nome no card" | |
| 14 | Oportunidades | Títulos "Pela sua formação" e "Para todos os egressos"; links com o domínio | |
| 15 | Meu e-mail: salvar com "abc" | **A-01:** o erro é percebido sem procurar? | |
| 16 | Participação → escolha de formações (Bruno, duas formações) | **A-04:** os dois "Iniciar a pesquisa desta formação" são distinguíveis? | |
| 17 | Início do Bruno: seção "Ninguém se forma sozinho." | O encontro é lido como item da categoria "Eventos", com o site externo | |

## Registro

- **Leitor, navegador e sistema, com versões:**
- **Commit:**
- **Data e quem executou:**
- **Obstáculos que impedem uma tarefa dos checkpoints** (corrigir antes das sessões):
- **Demais observações:**
