# Portal do Egresso — avaliação dos checkpoints por IA

- **Data:** 2026-10-08.
- **Natureza:** avaliação por agente de IA, com navegação real na demonstração local.
- **Não é:** sessão com egressos.
- **O que não faz:**
  - não atribui "sim", "parcial" ou "não" por participante;
  - não aplica o limiar de 4 de 5;
  - não conclui o Checkpoint 1;
  - não altera o status de nenhum checkpoint.

Cada achado distingue três tipos de registro:

- **observado:** o que a interface mostrou ou fez;
- **interpretação da IA:** leitura provável, com uma leitura alternativa;
- **questão para egressos:** o que só o teste com pessoas responde.

## 1. Versão, ambiente e funcionalidades

| Item | Valor |
|---|---|
| Commit avaliado | `a5fb95d` (`main`, merge do PR #45) |
| Funcionalidades implementadas | 001–024. A 025 existe **só como spec**; não há código, tabela nem tela. A 026 não existe |
| Ambiente | macOS arm64; Python 3.13.14; Django 5.2.17; PostgreSQL 16.14; Node 26.5.0 |
| Banco | `trajetoria_avaliacao_ia`, **exclusivo desta avaliação**, criado vazio, migrado e preparado com `preparar_demonstracao`. Os 19 bancos existentes não foram tocados |
| Chaves | `.env` novo no worktree, gerado pela receita do passo 2.7 do [ambiente local](../desenvolvimento/ambiente-local.md), com `PGDATABASE` apontando para o banco exclusivo. Única diferença em relação ao texto literal, exigida pela regra de preservar bancos |
| Servidor | `runserver 127.0.0.1:8000`, Portal ligado (`TRAJETORIA_PORTAL` ausente), modo de demonstração |
| Vídeo | Disponível. `video/node_modules` foi clonado (cópia APFS, sem download) de outro worktree com `package-lock.json` idêntico. `processar_videos` rodou em segundo plano |
| Navegador | Painel do navegador do app Claude, Chromium 152, viewport emulado de 375×812 (agente de usuário Android). 320×812 nas medições de largura |
| Verificações | `migrate --check` sem pendências; `makemigrations --check` = "No changes detected"; `manage.py check` sem problemas. A suíte de testes **não** foi executada nesta avaliação |
| Código da aplicação | Não alterado |

## 2. Método e cenários

**A. Execução pela interface.**
- O ponto de partida foi a raiz, com navegação só por elementos visíveis.
- Na primeira entrada, a identificação de Ana foi digitada, como faria um egresso. Nas demais, foi usado o painel "Usar estes dados", como prevê a preparação.

**B. Inspeção técnica.**
- Árvore de acessibilidade, ordem de tabulação, foco e medidas por script no navegador.
- Rotas internas foram usadas só aqui, depois da etapa A.

**C. Análise de compreensão.** Interpretação da IA, separada do observado.

| Cenário | Persona | Executado? | Como |
|---|---|---|---|
| Uma formação, pesquisa disponível | Ana | **Sim** | Roteiro completo do protocolo, a partir da raiz |
| Duas formações | Maria | **Sim** | Início e convite |
| Três formações | Diego | **Sim** | Início e convite |
| Pesquisa em andamento | Ana | **Sim** | Iniciou a pesquisa, aceitou os termos, usou "Salvar e sair" e voltou ao Início |
| Pesquisa concluída | Fernanda | **Sim**, com ressalva | Concluída pela recusa dos termos (Q1 = "Não"), o caminho legítimo mais curto. Nenhuma jornada completa de 9 partes foi respondida |
| Pesquisa indisponível | Bruno; Ana | **Sim** | Coleta ampla encerrada pelo operador fictício A, na gestão de Campanha, **só no banco desta avaliação** |
| Pessoa identificada sem Conclusão | — | **Não** | As personas "sem formação concluída" não são identificadas (não revelação da 018). Mesma limitação da avaliação anterior |
| Download do card e do vídeo | — | **Não** | Baixar arquivos exige autorização explícita; prévia e geração foram verificadas |
| Leitor de tela | — | **Não** | Nenhum VoiceOver ou NVDA foi usado. A árvore de acessibilidade é evidência distinta |

**Limitação estrutural.** O avaliador conhece as specs e os rótulos. Ele não é ingênuo como
um egresso. Por isso, "achou em 1 clique" prova só que **o caminho existe e é visível**, não
que uma pessoa o acharia.

## 3. Registro da execução (etapa A)

Os números de captura remetem a [evidencias-2026-10-08-ia-checkpoints/](evidencias-2026-10-08-ia-checkpoints/).

| # | Tela e ação | Destino | Cliques e teclas | Rolagem |
|---|---|---|---|---|
| 1 | Raiz `/` | Redireciona a `/entrar/`, "Confirme seus dados para entrar no Portal do Egresso" ([01](evidencias-2026-10-08-ia-checkpoints/01-raiz-entrada-375.jpg)) | 0 | 0 |
| 2 | Ana digita CPF e data e tecla Enter | `/inicio/` ([02](evidencias-2026-10-08-ia-checkpoints/02-ana-inicio-primeira-tela-375.jpg)) | 2 cliques em campos, 19 teclas, Enter | 0 |
| 3 | Tarefa 5: "Minha trajetória" na navegação, visível sem rolar | `/minha-trajetoria/` ([03](evidencias-2026-10-08-ia-checkpoints/03-ana-trajetoria-topo-375.jpg)) | 1 | 0 |
| 4 | Tarefa 6a: achar a imagem para compartilhar, na mesma página | Seção "Seu card"; "Baixar imagem (PNG)" em y ≈ 2446 px ([04](evidencias-2026-10-08-ia-checkpoints/04-ana-trajetoria-card-video-fim-375.jpg)) | 0 | ≈ 2.000 px (≈ 2,5 telas) |
| 5 | "Gerar vídeo" | O vídeo ficou pronto ≈ 16 s depois, por consulta automática; a página passou a mostrar "Baixar vídeo (MP4)" | 1 | 0 |
| 6 | Tarefa 6b: "Meu e-mail". A navegação só existe no topo; no fim da página, o único link é "Voltar às suas formações" | `/meu-email/` ([05](evidencias-2026-10-08-ia-checkpoints/05-ana-meu-email-375.jpg)) | 1 | ≈ 2.000 px de volta ao topo |
| 7 | Tarefa 7: "Pesquisa" na navegação | `/formacoes/`, título "Suas formações no Ifes" ([06](evidencias-2026-10-08-ia-checkpoints/06-ana-pesquisa-formacoes-375.jpg)) | 1 | 0 |
| 8 | "Iniciar a pesquisa" → "Sim" → "Salvar e sair" | `/formacoes/?aviso=salvo`, "Você parou em «Informações Pessoais»" | 3 | 0 |
| 9 | "Início" na navegação | Convite com o mesmo texto e "Continuar" ([07](evidencias-2026-10-08-ia-checkpoints/07-ana-inicio-acoes-convite-em-andamento-375.jpg)) | 1 | ≈ 1 tela até o convite |
| 10 | "Sair" | `/acesso/`, "Confirme seus dados para **acessar a pesquisa**", produto "Trajetória Ifes" | 1 | 0 |
| 11 | Raiz → Maria (painel) | Início com 2 formações ([08](evidencias-2026-10-08-ia-checkpoints/08-maria-inicio-primeira-tela-375.jpg)); convite "Escolher a formação" | 1 | 0 |
| 12 | Raiz → Diego (painel) | Início com 3 formações; convite sobre "2 das suas formações" | 1 | 0 |
| 13 | Raiz → Fernanda → "Responder" → "Iniciar a pesquisa" → "Não" → "Salvar e continuar" → "Concluir pesquisa" | "Pesquisa concluída" ([09](evidencias-2026-10-08-ia-checkpoints/09-fernanda-pesquisa-concluida-375.jpg)); Início: "Não há pesquisa pendente para você neste momento." | 6 | 0 |
| 14 | Operador A encerra a coleta ampla; Bruno entra pela raiz | Início: "No momento, não há pesquisa disponível para as suas formações."; "Pesquisa" leva às formações sem ação ([10](evidencias-2026-10-08-ia-checkpoints/10-bruno-pesquisa-indisponivel-375.jpg)) | 1 + navegação | 0 |
| 15 | Ana entra de novo, com o rascunho e a coleta encerrada | O Início diz que não há pesquisa disponível; nada menciona o que ela começou | 1 | 0 |

**Do Início até a primeira pergunta:** 2 toques ("Responder" e "Iniciar a pesquisa").

### Medidas do Início a 375×812, fonte a 100% (inclui a faixa de demonstração)

| Persona | Altura da página | `h1` | Frase de proveniência ("Nada aqui foi respondido por você") | Convite |
|---|---|---|---|---|
| Ana (1 formação) | 1.672 px (2,1 telas) | 517 px | 845 px, abaixo da dobra | 1.303 px (1,6 tela) |
| Maria (2) | 1.779 px | 517 px | 975 px, abaixo da dobra | 1.434 px |
| Diego (3) | 1.857 px | 517 px | 1.054 px, abaixo da dobra | 1.512 px |

Minha trajetória (Ana) tem 2.917 px (3,6 telas). A seção do card começa em 1.688 px.

## 4. Inspeção técnica (etapa B)

| Verificação | Resultado |
|---|---|
| Rolagem horizontal de 320 px, fonte de 100% e 200% (raiz font-size 200%), em Início, Minha trajetória, Pesquisa, Meu e-mail e entrada | **Nenhuma** (`scrollWidth = clientWidth = 320`) |
| Navegação a 320 px | 100%: duas linhas (89 px). 200%: quatro linhas (193 px); o `h1` do Início desce a 1.296 px ([11](evidencias-2026-10-08-ia-checkpoints/11-inicio-320-fonte-200.jpg)). Na primeira tela só cabem a faixa de demonstração e o cabeçalho |
| Navegação a 375 px, fonte a 100% | Uma linha no Início, em Pesquisa e em Meu e-mail. **Duas linhas em Minha trajetória** (89 px), porque o item atual em negrito não cabe |
| Alvos | Itens da navegação com 44 px de altura e largura de 44 a 107 px. **"Sair": 28×44 px.** "Pular para o conteúdo": 40 px de altura (já registrado na validação) |
| Ordem de tabulação no Início | Pular → Sair → Início → Minha trajetória → Pesquisa → Meu e-mail → quatro ações → ação do convite. Igual à ordem visual |
| Foco | Contorno sólido de 3 px em cor escura, conferido em "Pular" e "Início" |
| Árvore de acessibilidade do Início | Marcos: banner, `navigation` "Portal do Egresso", `main`, `contentinfo`. Um único `h1`; regiões com `h2` ("O que você pode fazer", "Pesquisa de acompanhamento"); lista das formações com "Registro do Ifes" em texto; item atual com `aria-current="page"`; `lang="pt-BR"` |
| Nome do produto no cabeçalho | "Portal do Egresso" em `/entrar/` e `/inicio/`. **"Trajetória Ifes"** em Minha trajetória, Pesquisa, Meu e-mail, concluída e `/acesso/`. O rodapé diz "Trajetória Ifes" em todas |
| Leitor de tela | **Não executado** (P4 da preparação continua aberta) |

## 5. Checkpoint 1 — matriz por critério

**Legenda da execução:**
- **observável**: a IA executou e o resultado é fato da interface;
- **não avaliável por IA**: depende do que uma pessoa entende.

Nenhuma linha substitui a nota de um participante.

### SC-008 — espaço próprio, não pesquisa (tarefas 2 e 8)

- **Cenário:** Ana, Maria e Diego, primeira tela depois da identificação.
- **Evidência visível:** sem rolar, aparecem "Portal do Egresso", a navegação, a ilustração da unidade, "Sua história com o Ifes", a síntese ("O Ifes registra 1 formação concluída por você") e a primeira formação. A palavra "pesquisa" aparece na primeira tela só como item de navegação ([02](evidencias-2026-10-08-ia-checkpoints/02-ana-inicio-primeira-tela-375.jpg)).
- **Execução:** não avaliável por IA.
- **Interpretação da IA:** a abertura comunica "o que o Ifes sabe de você", e não "responda". Leitura alternativa: com "Pesquisa" e "Meu e-mail" no menu, o lugar pode ser lido como "área do aluno" ou cadastro, e não como relação.
- **Problema:** o nome do produto muda para "Trajetória Ifes" ao sair do Início (A1), e "Sair" leva a "Confirme seus dados para acessar a pesquisa" (A2). A última imagem do lugar é de pesquisa.
- **Questão para egressos:** depois de visitar trajetória e e-mail, a pessoa ainda descreve o lugar como dela, ou diz que saiu do portal e entrou na "pesquisa"?

### SC-009 — o que o Ifes sabe (tarefa 3)

- **Evidência:** curso, unidade e ano em frases completas, nível e modalidade abaixo, "Registro do Ifes" ao lado. Para Ana, também "Há 3 anos desde essa conclusão."
- **Execução:** observável. As formações aparecem para 1, 2 e 3 conclusões, na ordem da 007.
- **Interpretação da IA:** é a parte mais forte do Início. Leitura alternativa: "Em 2022… Há 3 anos" pode parecer conta errada (2026 − 2022 = 4). A conclusão é de 16/12/2022, então são 3 anos completos (A8). Se a pessoa desconfiar da conta, pode desconfiar do resto.
- **Questão para egressos:** a pessoa confia nos dados? Ela nota alguma inconsistência?

### SC-010 — registro × resposta (tarefas 3 e 7)

- **Evidência:** "Registro do Ifes" e "Calculado a partir dos registros" em texto. A frase "Essas informações vêm dos registros acadêmicos do Ifes. Nada aqui foi respondido por você." fica **abaixo da dobra** nas três personas (845–1.054 px). O convite diz "Respondê-la é como você atualiza sua trajetória com o Ifes".
- **Execução:** não avaliável por IA.
- **Interpretação da IA:** o contraste existe, mas a frase-chave só é lida por quem rola (A9). Leitura alternativa: "Registro do Ifes" basta para a maioria.
- **Questão para egressos:** sem rolar, a pessoa já diz de onde vêm as informações? Ela relaciona "atualizar a trajetória" com "contar o que eu mesma vivi"?

### SC-011 — valor antes de responder (tarefas 4 e 7)

- **Evidência:** "O que você pode fazer" lista trajetória, card, vídeo e e-mail **antes** do convite. Trajetória, card e vídeo funcionaram para Ana **sem nenhuma Participação**. O vídeo ficou pronto em ≈ 16 s.
- **Execução:** observável. O acesso antes de responder funciona.
- **Interpretação da IA:** o valor está disponível e nomeado. Leitura alternativa: "Baixar" e "Gerar" podem soar como tarefas, e não como presentes.
- **Questão para egressos:** a pessoa diz espontaneamente que pode levar algo sem responder nada?

### SC-012 — onde atualizar (tarefa 7)

- **Evidência:** quatro portas levam ao mesmo lugar, com rótulos diferentes:
  - "Pesquisa" (navegação);
  - "Responder", "Continuar" ou "Escolher a formação" (convite);
  - "Voltar às suas formações" (fim da trajetória);
  - "Ver suas formações no Ifes" (e-mail).

  O destino se chama "Suas formações no Ifes".
- **Execução:** observável, a 1 clique pela navegação em qualquer página do Portal.
- **Interpretação da IA:** o acesso é fácil, mas o nome do destino ("formações") não é o da porta ("Pesquisa") (A3). Leitura alternativa: o texto "O Ifes quer saber como sua trajetória seguiu" desfaz a dúvida logo abaixo do título.
- **Questão para egressos:** perguntada "onde contaria o que mudou", a pessoa aponta "Pesquisa" ou procura "atualizar dados"?

### SC-013 — acha a trajetória (tarefa 5)

- **Evidência:** "Minha trajetória" na navegação, visível sem rolar. "Ver minha trajetória no Ifes" também aparece em "O que você pode fazer".
- **Execução:** observável. 1 clique, 0 rolagem.
- **Interpretação da IA:** caminho direto. Leitura alternativa: "Sua história com o Ifes" (o próprio Início) pode ser tomado como o "resumo" pedido, e a pessoa não sai da página, o que também atenderia à intenção.
- **Questão para egressos:** a pessoa considera o Início ou Minha trajetória como "o resumo"? Quanto tempo leva?

### SC-014 — pesquisa como convite (tarefas 2 e 7)

- **Evidência:** o convite aparece uma vez, no fim, sem urgência, com texto por situação:
  - aberta;
  - em andamento ("Continuar", sem dizer que a pessoa já começou; A7);
  - concluída ("Não há pesquisa **pendente** para você neste momento."; A11);
  - indisponível.
- **Execução:** não avaliável por IA.
- **Interpretação da IA:** a ordem favorece o convite. Leitura alternativa: o item "Pesquisa" na navegação, de mesmo peso que "Minha trajetória", e a palavra "pendente" podem reintroduzir a ideia de obrigação.
- **Questão para egressos:** "Você precisa fazer isso para usar o resto?": a resposta é "não"?

### SC-015 — acha retrato, vídeo e e-mail (tarefa 6)

- **Evidência:**
  - na trajetória, o card está no "Capítulo 3 de 3", a ≈ 2,5 telas do topo;
  - do Início, "Baixar o card da sua trajetória" leva direto à seção (`#card`);
  - "Meu e-mail" está na navegação, mas no fim da trajetória a navegação ficou 2,5 telas acima, e o único link à vista leva à pesquisa (A4).
- **Execução:** observável. Card: 1 clique + ≈ 2,5 telas, ou 1 clique pelo Início. Vídeo: 1 clique + ≈ 16 s. E-mail: 1 clique a partir do topo.
- **Interpretação da IA:** tudo é alcançável. O atrito está na volta da trajetória e no vocabulário "card" (hipótese 2 da avaliação anterior).
- **Questão para egressos:** a pessoa encontra "uma imagem para compartilhar" pela palavra "card"? Ela consegue voltar do fim da trajetória sem rolar tudo?

### SC-016 — não é painel de pendências (tarefas 2 e 8)

- **Evidência:** o Início não tem contadores, percentuais nem listas de tarefas. As ações são links simples. O convite é um bloco.
- **Execução:** não avaliável por IA.
- **Interpretação da IA:** baixo risco. Leitura alternativa: "O que você pode fazer" seguido de "Pesquisa de acompanhamento" pode ser lido como lista de afazeres. "Pendente" (A11) reforça isso para quem já respondeu.
- **Questão para egressos:** como a pessoa descreve o Início para alguém (tarefa 8)?

## 6. Problemas, por impacto

O impacto é estimado pela IA quanto ao risco de **contaminar o Checkpoint 1**. Não é severidade medida com pessoas.

### A1 — O nome do lugar muda ao sair do Início (alto)

- **Reprodução:** Início ("Portal do Egresso") → Minha trajetória, Pesquisa ou Meu e-mail: o cabeçalho passa a "Trajetória Ifes". O rodapé diz "Trajetória Ifes" sempre.
- **Por quê:** a T039 da 024 fixou "Portal do Egresso" só no Início, numa leitura de FR-024 ("nas páginas do Portal") que a avaliação anterior já apontava como ambígua.
- **Impacto:** SC-008. As telas com a navegação do Portal parecem outro produto.
- **Ajuste sugerido:** com o Portal ligado, usar "Portal do Egresso" em todas as telas que exibem a navegação do Portal (024 FR-022). Manter "Trajetória Ifes" nas Seções, em concluir e em `/acesso/`. Exige revisar FR-024 e T039.

### A2 — "Sair" leva à entrada da pesquisa (médio-alto)

- **Reprodução:** "Sair" em qualquer página → `/acesso/`, "Confirme seus dados para acessar a pesquisa".
- **Impacto:** SC-008 e SC-014. A última tela contradiz a proposta. O kit já prevê a recuperação do moderador.
- **Ajuste sugerido:** "Sair" a partir de telas com a navegação do Portal leva a `/entrar/`. A partir das Seções, continua levando a `/acesso/`. O destino é fixo por tela, sem parâmetro do cliente, coerente com FR-006. Exige revisar `contracts/rotas.md`.

### A3 — Um destino, vários nomes (médio)

- **Reprodução:** "Pesquisa" (navegação), "Voltar às suas formações" (trajetória), "Ver suas formações no Ifes" (e-mail) → página "Suas formações no Ifes".
- **Impacto:** SC-012. A pessoa pode não reconhecer que "formações" é onde se responde.
- **Ajuste sugerido:** com o Portal ligado, trocar os links de fim de página da trajetória e do e-mail por "Voltar ao Início". O `h1` de `/formacoes/` não muda, para preservar o caminho do convite (024 SC-002).

### A4 — Sem saída útil no fim da trajetória (médio)

- **Reprodução:** no fim de Minha trajetória (3,6 telas), o único link é "Voltar às suas formações". A navegação fica 2,5 telas acima.
- **Impacto:** SC-015 (card → e-mail) e o retorno ao Início.
- **Ajuste sugerido:** o mesmo do A3 ("Voltar ao Início"). Navegação fixa não é necessária.

### A5 — A navegação muda de forma entre páginas a 375 px (médio-baixo)

- **Reprodução:** a 375 px com fonte a 100%, ela ocupa uma linha no Início e duas em Minha trajetória (o item atual em negrito não cabe).
- **Impacto:** os itens "pulam" de lugar. A 025 acrescentará um quinto item (FR-020 da 025), e a quebra passará a ocorrer em todas as páginas.
- **Ajuste sugerido:** espaçamento que mantenha a mesma quebra em todas as páginas, sem tokens novos. Medir junto com a 025.

### A6 — "Sair" com alvo de 28 px de largura (baixo)

- **Reprodução:** medido a 375 px e a 320 px com fonte a 100%.
- **Impacto:** está abaixo dos 44×44 px da 014. Fica na faixa de demonstração, que não existe em uso real.
- **Ajuste sugerido:** largura mínima de 44 px no botão.

### A7 — O convite em andamento não diz que a pessoa já começou (baixo-médio)

- **Reprodução:** Ana com rascunho: o Início mostra o mesmo texto de "aberta", com "Continuar". "Você parou em «Informações Pessoais»" só aparece em `/formacoes/`.
- **Divergência registrada:** 024 FR-020 pedia "onde parou". `contracts/inicio.md` registrou "ajuste da implementação".
- **Ajuste sugerido:** acrescentar ao convite a frase da 023 ("Você parou em «…»"), ou alinhar a spec ao contrato.

### A8 — "Em 2022… Há 3 anos" (baixo-médio)

- **Reprodução:** Ana (conclusão em 16/12/2022), Início e trajetória.
- **Impacto:** SC-009. Uma conta aparentemente errada abala a confiança no "que o Ifes sabe".
- **Ajuste sugerido:** "Há mais de 3 anos" ou "concluída em dezembro de 2022". É texto derivado da 021 e exige revisá-la.

### A9 — A proveniência explícita fica abaixo da dobra (baixo)

- **Reprodução:** a frase "Nada aqui foi respondido por você" fica entre 845 e 1.054 px a 375×812.
- **Ajuste sugerido:** nenhum antes do teste. Observar no SC-010.

### A10 — O rascunho some em silêncio quando a Campanha encerra (baixo para a 024)

- **Reprodução:** Ana tinha "Continuar". Depois do encerramento, o Início diz que não há pesquisa disponível e não menciona o que ela começou.
- **Escopo:** é comportamento da 007 e da 017, não da 024.
- **Ajuste sugerido:** nenhum agora. Registrar para a linguagem dos estados (008/DP-801).

### A11 — "Pendente" no estado de quem já respondeu (baixo)

- **Reprodução:** Fernanda, depois de concluir: "Não há pesquisa pendente para você neste momento."
- **Impacto:** SC-016.
- **Ajuste sugerido:** frase sem vocabulário de obrigação, por exemplo "Você já respondeu à pesquisa aberta." A frase vem da 014 (FR-036) e também aparece na escolha de formações.

### Fora do escopo da 024

Não entram como problemas desta avaliação:

- a recusa dos termos termina com "Suas respostas … foram registradas" (R-04; EF-20);
- "seção" e "partes" na mesma tela (R-01).

### Pontos fortes observados

- Reconhecimento acima da dobra.
- Proveniência em texto.
- Trajetória, card e vídeo antes de qualquer resposta.
- Um único convite, sem urgência.
- Nenhuma rolagem horizontal de 320 px com fonte de 100% a 200%.
- Foco visível e ordem de tabulação coerente.
- Estados da pesquisa (aberta, em andamento, concluída, indisponível) com textos distintos e verdadeiros.

## 7. Checkpoint 2

**Não executável nesta versão.** A 025 existe só como spec e a 026 não existe. Nada foi
executado, contado ou inferido sobre Oportunidades ou Volte ao Ifes.

### Roteiro para aplicação futura

Este roteiro **não** é protocolo aprovado. O protocolo do Checkpoint 2 deve ser escrito antes da aplicação, como manda o roadmap §7.

| Tarefa | Critério |
|---|---|
| "Há alguma coisa aqui que o Ifes oferece para você agora?" | 025 SC-015: encontra uma oportunidade pertinente |
| "Por que esta aparece para você?" (apontar uma) | 025 SC-011: a explicação corresponde à formação registrada |
| "Quem está oferecendo isto? É do Ifes ou é propaganda?" | 025 SC-012; origem institucional e site do Ifes × externo |
| "O que acontece se você tocar no link?" | 025 SC-013 |
| Persona sem oportunidade dirigida (por exemplo, Elisa): "O que você entende desta tela?" | 025 SC-016 (estado vazio) |
| "Pesquisa e extensão" é a mesma coisa que a pesquisa de acompanhamento? | 025 SC-014 |
| "Se quisesse ajudar o Ifes, onde faria isso?" | Roadmap CP2, comportamento 1 e 3 (026): acha Volte ao Ifes e o distingue da pesquisa |
| "Quem vai receber isso? O que acontece depois? Como o Ifes vai falar com você?" | Roadmap CP2, compreensão 3; uso do contato |
| "E se você mudar de ideia?" | Roadmap CP2, compreensão 4: retirada |

**Lacuna.** O roadmap §7 pede registrar uma manifestação "em poucos toques", sem definir o
limiar. Ele precisa ser fixado na spec da 026 ou no protocolo do Checkpoint 2, antes do
teste. Esta avaliação não propõe número.

### Análise conceitual

Nenhuma reação ao mockup foi inferida. O `portal_egresso.html` não está no repositório e não
foi usado nesta avaliação.

## 8. Limitações

- O avaliador não é ingênuo: conhecia specs, rótulos e caminhos. Encontrar em 1 clique não
  prova que um egresso encontraria.
- Viewport emulado num navegador de computador. Não houve celular real, toque real nem
  teclado virtual.
- A ampliação a 200% foi feita pelo tamanho de fonte da raiz, não pelo zoom do sistema.
- Leitor de tela: não executado.
- Downloads de card e vídeo: não executados. Só prévia e geração.
- "Concluída" foi exercitada pela recusa dos termos, não por uma jornada completa.
- A faixa de demonstração ocupa a primeira tela e afeta as medidas de dobra. Em uso real,
  ela não existe.
- A pessoa identificada sem Conclusão (024 FR-010) continua sem caminho na demonstração.

## 9. Perguntas para o teste com pessoas

1. Depois de passar por trajetória e e-mail, a pessoa ainda acha que está no mesmo lugar
   (A1)?
2. Ao sair, ela entende a tela "acessar a pesquisa" como o mesmo serviço (A2)?
3. "Pesquisa" é onde ela contaria o que mudou? O título "Suas formações no Ifes" confunde
   (A3)?
4. "Card" é uma palavra que ela usaria para "imagem para compartilhar"?
5. "Em 2022… Há 3 anos" gera desconfiança (A8)?
6. Sem rolar, ela já diz de onde vêm as informações (A9)?
7. A pessoa com rascunho percebe que já começou (A7)?

## 10. Recomendação

**Corrigir a 024 com ajustes pequenos de navegação e texto antes da primeira sessão com
egressos, e manter a sequência atual.** Não antecipar o planejamento da 025.

- **Por que corrigir antes.** A1 a A4 não são achados de compreensão a serem descobertos no
  teste. São inconsistências observáveis de nome, saída e rótulo. Se ficarem, o teste tende a
  medir a inconsistência, e não a hipótese de reconhecimento antes da coleta. Pelo próprio
  protocolo, falhas de navegação se ajustam "dentro da 024, sem replanejar".
- **Escopo sugerido da correção:**
  - A1, A2, A3 e A4, que exigem revisar FR-024, `contracts/rotas.md` e a T039;
  - A6 e A7.

  A5 fica para a 025. A8 e A11 dependem de revisar a 021 e a 014, e podem esperar o teste.
- **Por que não antecipar a 025.** Os critérios que liberam a S2 (SC-008 a SC-012) são de
  compreensão. A IA não os mede. Nenhuma evidência desta avaliação substitui a leitura do
  protocolo.
- **Nenhuma mudança é proposta no roadmap.** No protocolo e na preparação, propõe-se só
  acrescentar à "Sequência até os resultados" um passo "aplicar os ajustes A1–A4, A6 e A7 da
  avaliação por IA de 2026-10-08 (PR próprio) antes da primeira sessão". Esse acréscimo
  fica para o solicitante aprovar e não foi feito aqui.
- **Status.** O Checkpoint 1 continua **NÃO APLICADO**. Nenhuma etapa foi liberada.

## Reprodução

```bash
createdb trajetoria_avaliacao_ia
```

O `.env` é o do passo 2.7 do ambiente local, com `export PGDATABASE=trajetoria_avaliacao_ia`.

```bash
source .env && uv run python manage.py migrate && uv run python manage.py preparar_demonstracao
```

```bash
source .env && uv run python manage.py runserver 127.0.0.1:8000
```

Depois, seguir a seção 3 com o navegador a 375×812. Para apagar o banco ao final, pare o
servidor antes:

```bash
dropdb --force trajetoria_avaliacao_ia
```
