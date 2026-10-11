# Protocolo do Checkpoint 1 — "fui reconhecido antes de ser solicitado"

Escrito em 2026-10-07, **antes** de qualquer sessão de teste. Critérios: spec da 024, SC-008 a
SC-016; roadmap §7.

> **Situação (2026-10-08): NÃO APLICADO.**
> - Nenhuma sessão com egressos foi feita.
> - O teste com leitor de tela também não foi feito.
> - A passada de teclado e da árvore de acessibilidade ([validação](../validacao.md)) é
>   evidência técnica, não resultado com egressos.
> - Os resultados entram em outro PR, depois da aplicação.
> - A S2 e a S3 não começam antes da leitura dos resultados conforme este protocolo.

> **Revisão de 2026-10-09 (Feature 029).** Os critérios SC-008 a SC-016, o limiar e a
> leitura do resultado **não mudam**. Mudam três pontos de procedimento:
> - **Bloco P antes da tarefa 1.** A sessão começa pelo
>   [bloco da página pública](../../029-pagina-publica-portal/checkpoint-pagina-publica.md),
>   com critérios próprios (P-01 a P-07) e ficha própria. Duração: 35 a 40 minutos.
> - **Tarefa 1.** Desde a 028, o endereço raiz mostra a página pública, não o formulário.
>   A pessoa entra pela chamada da página. O SC-013 e os demais critérios continuam medindo
>   o que acontece depois da identificação.
> - **Oportunidades existem no produto** desde a 025, quando há alguma pertinente. O trecho
>   "Oportunidades e Volte ao Ifes não aparecem no produto" vale agora só para Volte ao
>   Ifes. Reações a Oportunidades vão para as observações e não contam para SC-008 a
>   SC-016.

> **Revisão de 2026-10-11 (versão C, Feature 032; roadmap, revisão 13).** Os critérios
> SC-008 a SC-016, o limiar proposto (P1) e a regra de leitura (que falha leva a que
> correção) **não mudam**. Mudam o objeto, o procedimento e o passo seguinte:
> - **Versão avaliada:** a convergência visual C, servida pela `main` com a 032 integrada
>   (`63b9447` ou posterior, com os ajustes da etapa de acessibilidade, se houver). O commit
>   usado é anotado em cada ficha. Nenhuma versão anterior é avaliada por estes critérios.
> - **Navegação:** Início, Minha trajetória, Oportunidades e **Participação** (032 FR-011).
>   Não há mais os itens "Pesquisa", "Meu e-mail" nem "Contribuir". A pesquisa, o e-mail e
>   a contribuição ficam em Participação e no fim do Início. Por isso, o "sim" do SC-012
>   cita o bloco da pesquisa em Participação no lugar do item "Pesquisa"; o critério ("sabe
>   onde atualizar") é o mesmo. Como "Participação" reúne três coisas, apontar só esse item,
>   sem chegar à pesquisa, conta como **parcial**: o que se mede continua sendo saber onde
>   fica a pesquisa. Texto anterior: *aponta "Pesquisa" na navegação, o convite do Início ou
>   a escolha de formações*.
> - **Oportunidades e contribuição existem no produto** (025 e 026). O trecho
>   "Oportunidades e Volte ao Ifes não aparecem no produto" fica como histórico. Reações a
>   Oportunidades, à contribuição e à seção de encontros ("Ninguém se forma sozinho", que
>   aparece só com um evento pertinente) vão para as observações e não contam para SC-008
>   a SC-016. Elas são o objeto do
>   [Checkpoint 2](../../../docs/validacao/checkpoint-2/protocolo.md).
> - **Mockup conceitual.** Não é mostrado neste ciclo: as capacidades que ele ilustrava
>   (Oportunidades, contribuição) agora existem, e o `portal_egresso.html` não está no
>   repositório. Se o solicitante quiser mostrá-lo, vale a regra original: ao final,
>   identificado como protótipo, sem contar para os critérios.
> - **Bloco P:** sobre a página pública C, com a comparação histórica dependente de P6
>   ([bloco P](../../029-pagina-publica-portal/checkpoint-pagina-publica.md), "Revisão de
>   2026-10-11").
> - **Leitura com a 025 e a 026 implementadas.** As linhas "seguir para a S2 e a S3" e
>   "antes da S2 e da S3" da tabela de leitura são de 2026-10-07: as duas já foram
>   implementadas na demonstração (roadmap, revisões 5 e 10). Hoje, o passo seguinte ao
>   Checkpoint 1 é o de ajustes, antes do protótipo da Comunidade (roadmap, §13.3). Se a
>   compreensão falhar, o Início e a navegação são corrigidos antes do protótipo e do
>   Checkpoint 2.
> - **Dados do participante.** A pessoa usa só as personas fictícias. Ela não digita CPF,
>   data de nascimento, e-mail ou mensagem reais em nenhuma tela.

## O que o teste quer saber

Se o modelo mental mudou:

- **de:** "isto é um formulário que o Ifes quer que eu responda";
- **para:** "isto é um espaço meu com o Ifes".

Não são critérios de sucesso:

- taxa de resposta;
- engajamento;
- conversão;
- preferência declarada ("gostei").

## Formato

- **Teste moderado e presencial ou remoto**, com uma pessoa por vez e 25 a 30 minutos por
  sessão.
- **Participantes:** 5 egressos reais. Pelo menos 1 com mais de uma formação no Ifes e pelo
  menos 1 que concluiu há mais de 5 anos. Nenhum da equipe do projeto.
- **Persona.** O sistema só tem dados fictícios. Cada participante entra como a persona mais
  parecida com sua história (Maria: duas formações; Ana: uma formação) e fala a partir da
  própria experiência.
- **Ambiente.** No primeiro ciclo: a demonstração local com o Portal ligado, **no
  computador do moderador, com viewport de 375×812**, a partir de um banco recém-preparado
  em cada sessão (ver [preparação](checkpoint-1/preparacao-sessao.md)). O servidor local
  (`127.0.0.1`) não é acessível pelo celular do participante. Usar o celular exigiria
  publicar o servidor na rede, o que fica fora deste ciclo.
- **Participação e gravação.** O termo de participação, a eventual gravação, a guarda e a
  retenção são `DECISÃO PENDENTE` (P3 da preparação). Dispensar a gravação não dispensa o
  procedimento de participação.
- **Mesma sessão do teste da jornada.** A reauditoria de 2026-10-06 recomendou um teste da
  jornada da pesquisa. Ele pode ocorrer **depois** das tarefas abaixo, na mesma sessão.
- **Oportunidades e Volte ao Ifes não aparecem no produto.** Se o moderador quiser explorar
  essas hipóteses, mostra o mockup conceitual (`portal_egresso.html`) **ao final**, dizendo
  que é um protótipo. As reações a ele não contam para os critérios abaixo. *(Histórico:
  as duas existem no produto desde a 025 e a 026; ver as revisões de 2026-10-09 e
  2026-10-11.)*

## Roteiro

O moderador não usa as palavras "portal", "pesquisa", "trajetória" nem "início" antes de a
pessoa usá-las.

1. **Entrada espontânea.** Entregar o endereço raiz. Pedir: "Entre, como se tivesse
   recebido este endereço de um amigo."
2. **Primeira impressão (30 s).** Na primeira tela depois da identificação, sem rolar:
   - "O que é este lugar?"
   - "Para que serve?"
   - "O que o Ifes quer de você aqui?"
3. **O que o Ifes sabe.** "O que o Ifes sabe sobre você, segundo esta tela?" e, em seguida,
   "De onde vem essa informação?"
4. **Valor antes da coleta.** "Existe algo aqui que você poderia levar ou guardar agora?"
5. **Tarefa: ver a própria trajetória.** "Encontre um resumo da sua história no Ifes."
6. **Tarefa: retrato e e-mail.** "Encontre uma imagem para compartilhar" e "Encontre onde
   manter seu e-mail com o Ifes."
7. **A pesquisa.** "Se o Ifes quisesse saber o que mudou na sua vida, onde você contaria?" e
   "Você precisa fazer isso para usar o resto?"
8. **Fechamento.** "Se fosse descrever esta tela para alguém, o que diria?"

## Critérios e como observar

**Limiar** (proposto; confirmação em P1 da preparação). "A maioria" = pelo menos **4 de 5**
participantes, **em cada critério**. Cada critério é anotado por participante como **sim**,
**parcial** ou **não**. "Parcial" não conta para a maioria.

| Critério | Tarefa | "Sim" quando a pessoa… |
|---|---|---|
| SC-008: espaço próprio, não pesquisa | 2, 8 | descreve o lugar como dela ou da relação com o Ifes, sem reduzi-lo a "um questionário" ou "uma pesquisa" |
| SC-009: o que o Ifes sabe | 3 | cita ao menos uma formação (curso ou unidade e ano) sem ajuda |
| SC-010: registro × resposta | 3, 7 | diz que as formações vêm do Ifes e que a pesquisa é onde ela mesma conta |
| SC-011: valor antes de responder | 4, 7 | diz que pode ver a trajetória, o card ou o vídeo sem responder nada |
| SC-012: onde atualizar | 7 | aponta a pesquisa: o bloco da pesquisa em "Participação", o convite do Início ou a escolha de formações. Apontar só o item "Participação", sem chegar à pesquisa, é **parcial** *(até 2026-10-11: "Pesquisa" na navegação; ver revisão)* |
| SC-013: acha a trajetória | 5 | chega à página Minha trajetória sem ajuda |
| SC-014: pesquisa como convite | 2, 7 | trata a pesquisa como uma opção, não como a finalidade do lugar |
| SC-015: acha retrato, vídeo e e-mail | 6 | chega ao card (ou vídeo) e a Meu e-mail sem ajuda |
| SC-016: não é painel de pendências | 2, 8 | não descreve o Início como lista de tarefas, obrigações ou pendências |

## Leitura do resultado

| Resultado | Decisão |
|---|---|
| **Cada** critério de compreensão (SC-008 a SC-012) atinge a maioria | A premissa se sustenta; seguir para a S2 e a S3 |
| Ao menos um critério de compreensão não atinge a maioria | Corrigir a S1 (textos, ordem, abertura) antes da S2 e da S3. Não construir tabelas novas |
| Só a navegação (SC-013 a SC-016) falha | Ajustar navegação e textos dentro da 024, sem replanejar |

## Registro

Uma ficha por participante em `evidencias/checkpoint-1/`, a partir do
[modelo](checkpoint-1/ficha-participante.md), sem nome, CPF ou contato: só as
anotações por critério, frases literais curtas e tempos das tarefas 5 e 6. A síntese vai
para `validacao.md`, numa seção "Checkpoint 1".
