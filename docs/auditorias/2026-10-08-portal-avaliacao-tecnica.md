# Portal do Egresso — avaliação técnica exploratória

Data: 2026-10-08. Avaliação por agente, navegando na demonstração local. Não é sessão
com egresso, não atribui notas aos critérios SC-008 a SC-016 e não conclui o Checkpoint 1.

## Resultado e limites

O percurso observado permite entrar pelo Portal, consultar registros e acessar a
trajetória, a prévia do card, o formulário de e-mail e a escolha de pesquisas sem
responder a um questionário. Não foi observado bloqueio nesse percurso com Maria.
Isso comprova a disponibilidade das ações observadas, não a compreensão dos egressos.

O desenvolvimento pode continuar em correções e melhorias da etapa atual. A espera
por resultados antes de S2/S3 é uma decisão explícita do
[protocolo](../../specs/024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md),
não uma impossibilidade técnica. Antecipar essas etapas exige revisar explicitamente
o plano; esta avaliação não substitui a evidência prevista no Checkpoint 1.

## Ambiente e método

- Servidor já ativo em `http://127.0.0.1:8000/`, sem recriar banco ou chaves.
- Worktree do servidor: `.claude/worktrees/agitated-chebyshev-d2c86b`, baseado no
  commit `3653886`, com alterações locais na spec, no teste e no CSS da 021 para a
  correção de rolagem informada pelo solicitante. Essas alterações não foram editadas.
  Por isso, a evidência não é reproduzível a partir de um commit até essas alterações
  serem integradas; ao integrá-las, citar aqui o PR correspondente.
- Sem o renderizador de vídeo: o worktree do servidor não tem `video/node_modules`
  ([ambiente local, §2.14](../desenvolvimento/ambiente-local.md)).
- Chrome; viewports de 375×812 e 320×812. Fonte sem ampliação nesta avaliação.
- Uso apenas das personas fictícias do painel da demonstração.
- Inspeção visual, árvore de acessibilidade, medidas de elementos e uma verificação
  pontual do foco de teclado. A passada completa de teclado é a da
  [validação](../../specs/024-inicio-egresso-portal/validacao.md), do mesmo dia. Não foi
  usado VoiceOver ou NVDA.
- Não foram enviados e-mails nem respostas de pesquisa. O formulário de contato foi
  aberto, mas não salvo. Não foi realizado download do card; a prévia carregou.
- Não foi executada a suíte de testes nesta avaliação de navegação; o código da
  aplicação não foi alterado.

## Observações verificadas

| Percurso ou elemento | Evidência observada |
|---|---|
| Entrada pela raiz | Sem sessão, `/` levou a `/entrar/`; o botão da persona Maria levou a `/inicio/` |
| Reconhecimento | Ana, Maria e Diego exibiram respectivamente 1, 2 e 3 formações. As formações aparecem antes das ações e do convite |
| Proveniência | O Início identifica `Registro do Ifes`, derivados calculados e afirma que aquelas informações não foram respondidas pelo participante |
| Trajetória de Maria | A navegação abriu `/minha-trajetoria/`; a imagem do card carregou, com largura natural de 1080 px |
| E-mail de Maria | `Meu e-mail` abriu o formulário, com finalidade de convites à pesquisa, caráter opcional e aviso de texto provisório |
| Pesquisa de Maria | `Pesquisa` abriu as duas formações, ambas com opção de iniciar e informação de no máximo 9 partes |
| Tela estreita | A 320 px, Início e Minha trajetória de Maria tiveram `scrollWidth = clientWidth = 305 px`; o espaço restante corresponde à barra de rolagem |
| Navegação | Os quatro links do Início mediram 44 px de altura; a largura não foi medida, e FR-025 pede 44×44. O item atual usa `aria-current="page"`. `Pular para o conteúdo` tem 40 px, como registrado na validação |
| Teclado | Tab a partir de `Pular para o conteúdo` levou a `Sair`, com contorno sólido de 3 px. Confirma pontualmente a passada completa da validação; não é evidência nova |
| Saída | `Sair` levou a `/acesso/`, cuja apresentação é centrada na pesquisa |
| Persona só com matrícula ativa (F1) | João recebeu mensagem genérica de não confirmação e opções de conferir os dados ou informar formação. É a não revelação da 018: João não é identificado, então o percurso não exercita FR-010 (pessoa identificada sem Conclusão). Não foi testado o envio da declaração |
| Vídeo | Não havia opção de vídeo nas telas observadas. É o comportamento previsto sem renderizador ([spec, casos de borda](../../specs/024-inicio-egresso-portal/spec.md): "Vídeo indisponível"). Geração e reprodução não foram verificadas |

## Hipóteses para observar com egressos

Estas são perguntas de revisão, não falhas demonstradas por participantes:

1. **Continuidade do ambiente.** O cabeçalho muda de `Portal do Egresso` no Início
   para `Trajetória Ifes` nas outras páginas. O texto de FR-024 ("nas páginas do
   Portal") é ambíguo; quem fixa esse recorte é a T039 das
   [tasks](../../specs/024-inicio-egresso-portal/tasks.md). Observar se a pessoa entende
   que continua no mesmo ambiente. Se não entender, é essa interpretação que se revisa.
2. **Vocabulário da imagem.** A interface usa `card`, enquanto SC-015 também emprega
   `Retrato`. Observar se a pessoa encontra a imagem a partir da tarefa aberta,
   sem ensiná-la a palavra usada pelo produto.
3. **Reentrada depois de sair.** O retorno a `/acesso/` está previsto no
   [contrato de rotas](../../specs/024-inicio-egresso-portal/contracts/rotas.md).
   Observar se a mudança para uma entrada centrada na pesquisa enfraquece a
   compreensão de espaço de relacionamento. Eventual mudança precisa revisar a spec.
   Efeito imediato nas sessões: o kit manda não abrir `/acesso/`, e `Sair` leva
   justamente para lá. A instrução de recuperação do moderador foi incluída na
   [preparação](../../specs/024-inicio-egresso-portal/evidencias/checkpoint-1/preparacao-sessao.md).

## Próximo trabalho

**Vídeo nas sessões (P5).** Sem o renderizador, a pessoa não vê o vídeo como algo
disponível sem responder, e SC-011 e SC-015 o mencionam. O protocolo aceita "card (ou
vídeo)", então os critérios podem ser cumpridos sem ele, mas a escolha precisa ser
explícita antes da primeira sessão: instalar o renderizador no computador do moderador
ou registrar que as sessões rodam sem vídeo. Registrado como P5 na
[preparação](../../specs/024-inicio-egresso-portal/evidencias/checkpoint-1/preparacao-sessao.md).

Executar a verificação real com leitor de tela (P4) e registrar os obstáculos
observados. Em paralelo, resolver P1/P2/P3/P5 para as sessões. Não marcar a compreensão
como aprovada a partir desta inspeção. A retomada de S2/S3 segue o protocolo vigente,
salvo revisão explícita do plano pelo solicitante.

![Início de Diego na demonstração, a 375×812](evidencias/2026-10-08-portal/inicio-diego-375.jpg)
