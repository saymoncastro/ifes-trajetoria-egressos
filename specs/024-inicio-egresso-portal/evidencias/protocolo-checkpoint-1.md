# Protocolo do Checkpoint 1 — "fui reconhecido antes de ser solicitado"

Escrito em 2026-10-07, **antes** de qualquer sessão de teste. Critérios: spec da 024, SC-008 a
SC-016; roadmap §7.

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
- **Ambiente.** A demonstração local com o Portal ligado, no celular do participante ou em
  viewport de 375×812, a partir de um banco recém-preparado em cada sessão (ver
  [preparação](checkpoint-1/preparacao-sessao.md)). Gravar a tela só com consentimento. O
  termo, a guarda e a retenção são `DECISÃO PENDENTE` (P3 da preparação).
- **Mesma sessão do teste da jornada.** A reauditoria de 2026-10-06 recomendou um teste da
  jornada da pesquisa. Ele pode ocorrer **depois** das tarefas abaixo, na mesma sessão.
- **Oportunidades e Volte ao Ifes não aparecem no produto.** Se o moderador quiser explorar
  essas hipóteses, mostra o mockup conceitual (`portal_egresso.html`) **ao final**, dizendo
  que é um protótipo. As reações a ele não contam para os critérios abaixo.

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

**Limiar.** "A maioria" = pelo menos **4 de 5** participantes. Cada critério é anotado por
participante como **sim**, **parcial** ou **não**. "Parcial" não conta para a maioria.

| Critério | Tarefa | "Sim" quando a pessoa… |
|---|---|---|
| SC-008: espaço próprio, não pesquisa | 2, 8 | descreve o lugar como dela ou da relação com o Ifes, sem reduzi-lo a "um questionário" ou "uma pesquisa" |
| SC-009: o que o Ifes sabe | 3 | cita ao menos uma formação (curso ou unidade e ano) sem ajuda |
| SC-010: registro × resposta | 3, 7 | diz que as formações vêm do Ifes e que a pesquisa é onde ela mesma conta |
| SC-011: valor antes de responder | 4, 7 | diz que pode ver a trajetória, o card ou o vídeo sem responder nada |
| SC-012: onde atualizar | 7 | aponta "Pesquisa" na navegação, o convite do Início ou a escolha de formações |
| SC-013: acha a trajetória | 5 | chega à página Minha trajetória sem ajuda |
| SC-014: pesquisa como convite | 2, 7 | trata a pesquisa como uma opção, não como a finalidade do lugar |
| SC-015: acha retrato, vídeo e e-mail | 6 | chega ao card (ou vídeo) e a Meu e-mail sem ajuda |
| SC-016: não é painel de pendências | 2, 8 | não descreve o Início como lista de tarefas, obrigações ou pendências |

## Leitura do resultado

| Resultado | Decisão |
|---|---|
| Compreensão (SC-008 a SC-012) atinge a maioria | A premissa se sustenta; seguir para a S2 e a S3 |
| Compreensão falha | Corrigir a S1 (textos, ordem, abertura) antes da S2 e da S3. Não construir tabelas novas |
| Só a navegação (SC-013 a SC-016) falha | Ajustar navegação e textos dentro da 024, sem replanejar |

## Registro

Uma ficha por participante em `evidencias/checkpoint-1/`, a partir do
[modelo](checkpoint-1/ficha-participante.md), sem nome, CPF ou contato: só as
anotações por critério, frases literais curtas e tempos das tarefas 5 e 6. A síntese vai
para `validacao.md`, numa seção "Checkpoint 1".
