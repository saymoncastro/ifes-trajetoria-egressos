# Protocolo do Checkpoint 2 — "recebo valor e quero retribuir"

Escrito em 2026-10-11, **antes** de qualquer sessão
([roadmap, revisão 13](../../roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md#13-estado-depois-da-032-e-próxima-etapa-revisão-13-2026-10-11)).
Critérios: roadmap §7 (Checkpoint 2 e bloco Comunidade), 025 SC-011 a SC-016 e os
qualitativos da 026.

> **Situação: NÃO APLICADO.**
> - Nenhuma sessão com egressos foi feita.
> - O bloco Comunidade depende de um **protótipo estático que ainda não existe**.
> - O Checkpoint 2 vem depois do Checkpoint 1, dos ajustes e do protótipo da Comunidade
>   (roadmap, §13.3).
> - As pendências Q1 a Q7 ([preparação](preparacao-sessao.md)) são decididas antes da
>   primeira sessão.
> - Os resultados entram em outro PR, depois da aplicação.

## O que o teste quer saber

Duas perguntas, em duas partes da sessão:

1. **Produto (025, 026, Participação).** Com as capacidades reais da demonstração, a pessoa
   percebe que recebe algo pertinente do Ifes e consegue retribuir, entendendo o que
   acontece com o que ela oferece e com o contato que informa?
2. **Bloco Comunidade (protótipo).** Histórias, Encontros e Encontre colegas, como
   **ideias**, são compreendidos e parecem úteis? A resposta informa a escolha entre 031 e
   030 e as condições do E1.

Não são critérios de sucesso:

- taxa de clique, de resposta ou de adesão;
- engajamento ou conversão;
- preferência declarada ("gostei");
- dizer que proporia, participaria ou aderiria, que é intenção, e não adesão.

## Objeto avaliado

- **Produto:** a demonstração na `main` com a 032 integrada e os ajustes do Checkpoint 1,
  se houver. O commit vai em cada ficha.
- **Bloco Comunidade:** o protótipo estático da Comunidade (roadmap, §13.3, passo 5),
  aberto **fora** da aplicação e apresentado como protótipo. **Nada dele existe no
  produto.** Ver [Material do bloco Comunidade](#material-do-bloco-comunidade).

## Formato

- **Teste moderado**, presencial ou remoto, com uma pessoa por vez. Estimativa: 25 minutos
  de produto e 15 do bloco Comunidade. Fazer as duas partes na mesma sessão ou em sessões
  separadas é a pendência Q7.
- **Participantes:** número e limiar em Q1; perfil e recrutamento em Q2. Nenhum da equipe
  do projeto. Reaproveitar quem participou do Checkpoint 1 é escolha de Q2: essa pessoa já
  conhece o Portal, o que pesa menos aqui do que no Checkpoint 1, mas afeta "encontra sem
  ajuda".
- **Personas.** O sistema só tem dados fictícios. Cada participante usa a persona mais
  parecida com sua história e fala a partir da própria experiência
  ([preparação](preparacao-sessao.md#personas)).
- **Ambiente.** O mesmo do Checkpoint 1: demonstração local no computador do moderador, a
  375×812, com banco recém-preparado em cada sessão.
- **Participação e gravação.** Procedimento em Q3. Sem Q3 resolvida, não há sessão.
- **Dados do participante.** Só dados fictícios. Na contribuição, a pessoa usa o e-mail
  fictício que o moderador entrega e não escreve dados pessoais na mensagem.

**O que o teste preserva.**
- **Coleta independente do Portal.** O teste não usa o caminho do convite (`/acesso/`) e não
  muda nada na coleta.
- **Dados de relacionamento separados dos analíticos.** Nada do que a sessão grava na
  demonstração (contribuições, retiradas) é dado do acompanhamento, e nada entra em
  snapshot, exportação ou indicador (ADR 0008). As fichas não são dado do acompanhamento.

## Roteiro — parte 1, produto

O moderador não usa "portal", "pesquisa", "oportunidade", "contribuir", "comunidade" nem
"encontro" antes de a pessoa usar. Não ajuda nas tarefas. Se a pessoa travar por mais de 2
minutos, anota "não" e segue.

**Entrada.** O moderador abre `/entrar/` e usa "Usar estes dados" da persona escolhida. Não
há perguntas de primeira impressão: elas são do Checkpoint 1.

**O. Oportunidades** (persona principal)

- **O1.** "Há alguma coisa aqui que o Ifes oferece para você agora?" → 025 SC-015 (CP2-B1)
- **O2.** Apontando a oportunidade que a pessoa achou, ou o destaque, se ela não achou
  nenhuma: "Por que esta aparece para você?" → 025 SC-011 (CP2-C1)
- **O3.** "Quem oferece isso?" → 025 SC-012 (CP2-C2)
- **O4.** "O que acontece se você tocar no link?" A pergunta é feita sem tocar. → 025 SC-013

**R. Contribuição** (mesma persona)

- **R1.** "Se você quisesse ajudar o Ifes de alguma forma, onde faria isso?" → CP2-B2
  (encontrar) e CP2-B3
- **R2.** Tarefa: "Ofereça-se para conversar com estudantes sobre a sua área." Contar telas
  e toques até a tela de conferência. → CP2-B2
- **R3.** Na tela "Confira e envie", antes de enviar: "Quem vai receber isto? O que
  acontece depois que você enviar?" → CP2-C3
- **R4.** Na mesma tela: "Para que o Ifes vai usar este e-mail?" O moderador entrega o
  e-mail fictício. → CP2-B2 (uso do contato) e CP2-E1
- **R5.** Depois de enviar: "Onde você vê o que enviou? O que essa tela diz sobre o que vai
  acontecer?" → CP2-C3
- **R6.** "O que você fez agora é a mesma coisa que responder à pesquisa do Ifes?" e,
  apontando a forma "Pesquisa e extensão" na escolha: "O que você entende por isto?" →
  CP2-B3 e 025 SC-014
- **R7.** "Você pode desfazer isso? Como?" Depois: "Faça." → CP2-C4

**M. Participação e e-mail**

- **M1.** Em Participação, ou no bloco "Seu canal com o Ifes" do Início: "Para que o Ifes
  usaria um e-mail informado aqui? É o mesmo uso do e-mail de antes?" A pessoa não preenche
  nada. → CP2-E1

**V. Estado vazio** (só se Q5 mantiver a tarefa)

- **V1.** Com a persona Fernanda, depois de o moderador retirar o item O1 do catálogo
  fictício, na página de Oportunidades: "O que você entende desta tela?" → 025 SC-016

**A. Encontro divulgado pelo Ifes** (persona Bruno)

- **A1.** Na seção "Ninguém se forma sozinho" do Início: "O que é isto? Quem organiza? Como
  você participaria?" → CP2-R2 (registro). Serve de referência para o CM-C1 do bloco
  Comunidade.

**Fechamento**

- "Você voltaria aqui outro dia? Para quê?" → CP2-R1 (registro, para a S4)

## Roteiro — parte 2, bloco Comunidade

**Abertura, literal:** "Agora vou mostrar desenhos de ideias que **ainda não existem**.
Nada disso funciona hoje. Quero entender o que você entende e o que acharia útil."

O protótipo é aberto fora da aplicação, na ordem Histórias → Encontros → Encontre colegas.
O moderador pode usar "comunidade" e "encontro" a partir daqui, porque o protótipo usa
essas palavras (revisão 12).

**H. Histórias**
- **H1.** "O que é esta página? Quem escreveu este texto e quem decidiu publicá-lo?" →
  CM-C4 (registro de leitura)
- **H2.** "Esta história lhe diz alguma coisa? Por quê?" → CM-U4

**F. Encontros**
- **F1.** Com um evento do Ifes e um encontro proposto por egresso lado a lado: "Qual a
  diferença entre estes dois? Quem organiza cada um?" → CM-C1
- **F2.** "Se você marcar 'Vou participar', quem fica sabendo? Quem recebe o link da
  reunião?" → CM-C2
- **F3.** "Você participaria de um encontro proposto por outro egresso? De qual tipo?" →
  CM-U2
- **F4.** "Você proporia um encontro? Sobre o quê, e para quem?" → CM-U1

**D. Encontre colegas (diretório)**
- **D1.** "Como alguém passa a aparecer nesta lista? O que os outros veem? Como alguém
  falaria com você?" → CM-C3
- **D2.** "Você entraria nesta lista? O que mostraria?" → CM-U3

**Fechamento do bloco**
- "Pelo que você viu, o que mais este lugar faria?" → CM-C4

## Critérios e como observar

Cada critério é anotado por participante como **sim**, **parcial** ou **não**, com a frase
literal curta ou o comportamento que o sustenta. Só "sim" conta. O limiar é Q1.

**Parte 1, produto.**

| Critério | Origem | Tarefa | "Sim" quando a pessoa… |
|---|---|---|---|
| CP2-C1: por que aparece | Roadmap §7, compreensão 1; 025 SC-011 | O2 | explica com as próprias palavras, pela formação que concluiu, e a explicação a convence |
| CP2-C2: institucional × anúncio | Roadmap §7, compreensão 2; 025 SC-012 | O3 | diz que quem oferece é o Ifes ou a unidade, e não um anunciante |
| 025 SC-013: link oficial | 025 | O4 | diz que o link leva ao site oficial, onde estão prazos e inscrição, e que abrir não inscreve |
| 025 SC-014: não é a pesquisa | 025 | R6 | não confunde Oportunidades nem "Pesquisa e extensão" com a pesquisa de acompanhamento |
| CP2-B1: acha oportunidade pertinente | Roadmap §7, comportamento 1; 025 SC-015 | O1 | chega, sem ajuda, a uma oportunidade pertinente à própria formação |
| 025 SC-016: estado vazio | 025 | V1 | não lê a área vazia como quebrada nem como pendência sua |
| CP2-C3: o que acontece depois e quem recebe | Roadmap §7, compreensão 3; 026 | R3, R5 | diz que a unidade da formação escolhida recebe, que pode haver contato pelo e-mail informado, sem prazo garantido, e onde acompanha |
| CP2-C4: pode retirar | Roadmap §7, compreensão 4; 026 | R7 | diz que pode retirar e consegue fazê-lo |
| CP2-B2: registra sem dúvida sobre o contato | Roadmap §7, comportamento 2; 026 | R1, R2, R4 | encontra a contribuição e chega à conferência sem ajuda, sem dúvida sobre o uso do contato. "Poucos toques" depende de Q4 |
| CP2-B3: contribuir não é a pesquisa | Roadmap §7, comportamento 3; 026 | R1, R6 | não trata a contribuição como a pesquisa nem como condição para ela |
| CP2-E1: finalidade dos dois e-mails *(proposto; Q6)* | Roadmap §7, comportamento 2; 026 D-2602; 020 FR-012 | R4, M1 | diz que o e-mail da contribuição serve só para responder sobre ela e que o e-mail de Participação serve para convites do acompanhamento |
| CP2-R1: motivo para voltar | Roadmap §7 (S4) | Fechamento | registro, sem limiar |
| CP2-R2: encontro divulgado pelo Ifes | Revisão 12 (alternativa A) | A1 | registro, sem limiar |

**Parte 2, bloco Comunidade** (roadmap §7, bloco Comunidade).

| Critério | Tarefa | "Sim" quando a pessoa… |
|---|---|---|
| CM-C1: proposto por egresso × evento do Ifes | F1 | diz quem organiza cada um e que divulgar um encontro não faz do Ifes o organizador |
| CM-C2: quem vê a confirmação e o link | F2 | diz que a confirmação não é pública e que o link só aparece para quem confirmou |
| CM-C3: diretório por escolha, com aceite | D1 | diz que aparecer é escolha da pessoa, o que é mostrado e que o contato depende de aceite |
| CM-C4: nenhuma função inexistente | H1, fechamento | **não** atribui ao protótipo mensagens, rede de contatos, feed, evento oficial onde não há ou contato direto sem aceite. Anotar qual |
| CM-U1: proporia um encontro | F4 | registro: sobre o quê e para quem |
| CM-U2: participaria | F3 | registro: de qual tipo |
| CM-U3: aderiria ao diretório | D2 | registro: o que mostraria |
| CM-U4: uma história diz algo | H2 | registro: por quê |

CM-U1 a CM-U4 são qualitativos e **não** são taxa de adesão.

## Leitura do resultado

*(Proposta deste protocolo; aprovação em Q6, junto com o limiar de Q1.)*

| Resultado | Decisão |
|---|---|
| CP2-C1, CP2-C2, SC-013 ou SC-014 não atingem o limiar | Rever a explicação, a origem e o vocabulário de Oportunidades (025) |
| CP2-B1 ou SC-016 não atingem | Ajustar navegação e estado vazio de Oportunidades, sem replanejar |
| CP2-C3, CP2-C4, CP2-B2 ou CP2-B3 não atingem | Rever os textos da contribuição (ciência, Suas contribuições, chamadas). Registrar como evidência para D4 e D5 |
| CP2-E1 não atinge | Rever os textos dos dois e-mails. Registrar como evidência para D5 |
| CP2-R1 | Informa se a S4 (027) vale a pena (roadmap §7) |
| CM-C1 ou CM-C2 não atingem | A spec da 031, se escolhida, resolve a distinção e a visibilidade antes da implementação. Pesa entre os motivos para a 030 primeiro (roadmap, §13.5) |
| CM-C3 não atinge | Condição para o E1: a ADR própria e a spec resolvem a compreensão do diretório |
| CM-C4 falha | Corrigir o protótipo antes de qualquer spec que dependa dele |
| CM-U1 a CM-U4 | Informam a escolha entre 031 e 030 (roadmap, §13.5), sem limiar |

Nada é aprovado automaticamente. Qualquer mudança de código ou abertura de spec depende de
autorização do solicitante.

## Material do bloco Comunidade

O protótipo ainda não existe. Requisitos, da revisão 12 e deste protocolo:

- **Forma.** HTML estático, sem JavaScript, fora da aplicação, como os
  [protótipos da camada visual](../../prototipos/2026-10-09-portal/LEIAME.md). Dados
  fictícios com selo. A 375 px, com composição própria para o desktop (ADR 0009, decisão 2).
- **Marcação.** Cada peça marcada como "Protótipo: não existe no Portal".
- **Composição editorial substantiva**, e não uma sequência de cards administrativos
  (revisão 12, "Experiência visual").
- **Histórias (B):** autor egresso, curadoria indicada, sem fotografia de pessoa real
  (DP-2106), sem ranking.
- **Encontros (F):** um "Evento do Ifes" (A) e um "Encontro proposto por egresso" (F) com
  rótulos distintos; "Vou participar" com o texto de quem fica sabendo; o link da reunião
  mostrado só depois da confirmação; sem lista nominal nem contador público.
- **Encontre colegas (E1):** adesão por escolha, controle do que é mostrado, pedido de
  contato com aceite, recusa, bloqueio e retirada.
- **Fora (E2):** feed, comentários, curtidas, seguidores, mensagens privadas e rankings.
- A palavra "comunidade" pode aparecer no protótipo (revisão 12). Continuam vedados
  "turma", "geração", "conectad", contagens de egressos e comparação social.
- O solicitante revisa o protótipo antes da primeira sessão (Q7).

## Registro

- Uma ficha por participante nesta pasta, a partir dos modelos
  [ficha do produto](ficha-participante.md) e
  [ficha do bloco Comunidade](ficha-bloco-comunidade.md), sem nome, CPF ou contato.
- A síntese vai para `sintese.md` nesta pasta, em outro PR, com as contagens "x de N" e as
  frases literais. Remissões nas validações da [025](../../../specs/025-oportunidades-curadas-portal/validacao.md)
  e da [026](../../../specs/026-volte-ao-ifes/validacao.md).
- Nenhuma contagem é apresentada como taxa de adesão, engajamento ou conversão.
