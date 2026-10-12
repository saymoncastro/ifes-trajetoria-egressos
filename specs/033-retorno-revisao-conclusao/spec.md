# Feature Specification: Retorno à conclusão depois de revisar

**Feature Branch**: `claude/033-retorno-revisao`
**Created**: 2026-10-12
**Status**: Rascunho para aprovação do solicitante. A implementação só começa depois da
aprovação desta spec e dos cenários de aceitação.
**Input**: Solicitante, 2026-10-12: priorizar a D5 da
[auditoria de conclusão e confirmação](../../docs/auditorias/2026-10-12-conclusao-e-confirmacao.md)
(seção 6). Quem revisa uma parte a partir da conclusão deve poder voltar à conclusão depois
de salvar, desde que a participação continue apta a ser concluída. Condições: o fluxo normal
não muda; nenhuma validação ou etapa obrigatória é contornada; as partes que passarem a se
aplicar depois de uma alteração aparecem antes da conclusão, mesmo só com perguntas
opcionais. Sem modelo, migração, persistência nova, JavaScript, tela nova, resumo de respostas
ou mudança no instrumento.

## Contexto

| Fato verificado | Fonte | Consequência |
|---|---|---|
| Na conclusão, a lista "volte a uma das partes" leva à Seção sem nenhuma indicação de origem | `conclusao.html`; 023 FR-027 | A Seção não sabe que veio da revisão |
| Depois de um envio aceito, o destino é sempre a Seção seguinte do percurso, ou a conclusão se a Seção enviada termina em finalização | `views.py`, `_salvar`; 006 FR-014 | Quem revisa a Parte 2 de 9 reenvia as Partes 3 a 9 (até 8 envios a mais no percurso de Ana) |
| "Salvar e sair" já usa a mesma validação e gravação e só muda o destino | 014 FR-011, FR-012 | Precedente: mudar o destino sem mudar o envio |
| O percurso avança sozinho por Seções sem obrigatória pendente e para na primeira que tem | `percurso.percorrer` | Uma Seção nova só com opcionais não segura o percurso: sem cuidado, seria pulada |
| Os destinos de navegação são sempre posteriores (Versão publicada) | 006 FR-015 | Mudar uma resposta só altera o percurso **depois** da Seção alterada |
| A conclusão revalida tudo na exibição e no envio | `concluir_view`; 006 `concluir` | Nada nesta feature autoriza concluir |
| O envio pendente (sessão vencida) guarda todos os campos enviados e os restaura | 023 FR-002 a FR-009 | O marcador enviado no formulário sobrevive à restauração |
| Mensagens de "salvo" dependem de Resposta gravada, nunca de indicador no endereço | 014 FR-008; 023 FR-016 | O aviso na volta segue a mesma regra |

### Refinamento da proposta da auditoria

A auditoria (seção 6) propunha voltar à conclusão quando a jornada continuasse finalizada e
nenhuma Seção nova tivesse entrado no percurso. Essa comparação de percursos funciona para
uma alteração isolada, mas falha em cadeia. Exemplo: Ana muda "Atualmente você trabalha?"
para "Não". "Egresso que não trabalha" entra no percurso, e ela a responde. Ao salvar essa
parte, o percurso de antes do envio terminava nela, então "Estudo", "Egresso que estuda" e a
Parte 9 contam como "novas". Ela teria de reenviá-las, que é exatamente o problema a
resolver.

Esta spec troca a comparação por uma regra local, também sem estado: depois de salvar em
revisão, a pessoa vai para **a próxima parte do percurso que ainda pede atenção**. Se não
houver nenhuma, vai para a conclusão (FR-004).

## User Scenarios & Testing

Personas e percursos da demonstração. Ana responde sobre TADS e chega à conclusão pelo
percurso "trabalha e estuda", com 9 partes: Termos e condições, Informações Pessoais,
Informações do curso, Graduação, Avaliação, Egresso que trabalha, Estudo, Egresso que
estuda, Parte 9.

### US1 — Corrigir uma resposta e voltar à conclusão (P1)

A pessoa está na conclusão, abre uma parte pela revisão, corrige e salva. Ela volta para a
conclusão, sem passar de novo pelas partes seguintes.

**Por que P1:** é o caso mais comum e o custo de hoje (até 8 envios) é o maior obstáculo do
encerramento.

**Independent Test:** por requisição, percorrer até a conclusão, abrir uma parte pela
revisão, enviar com e sem alteração e verificar o destino e as Respostas gravadas.

**Acceptance Scenarios:**

1. **Dado** Ana na conclusão, **quando** abre "Informações Pessoais" pela revisão, **então** a
   parte mostra suas respostas gravadas, diz que ela está revisando e oferece "Salvar e
   voltar à conclusão".
2. **Dado** essa parte aberta pela revisão, **quando** Ana muda o telefone e salva, **então** a
   Resposta é gravada como em qualquer envio, e ela chega à conclusão com a confirmação
   discreta de que a parte foi salva. Foram 1 envio, não 8.
3. **Dado** essa parte aberta pela revisão, **quando** Ana salva sem mudar nada, **então** ela
   volta à conclusão.
4. **Dado** Ana na conclusão, **quando** abre "Estudo" e muda "Atualmente você estuda?" de "Sim"
   para "Não", **então** "Egresso que estuda" sai do percurso (as Respostas dela ficam
   inativas, como hoje), a Parte 9 continua respondida, e ela volta à conclusão. A lista da
   revisão passa a ter 8 partes.

### US2 — Uma alteração que muda o caminho mostra as partes novas antes de concluir (P1)

Quando a alteração faz entrar no percurso uma parte que a pessoa ainda não respondeu, ela é
levada a essa parte, com a explicação, e só depois volta à conclusão.

**Por que P1:** é a condição de segurança da feature. Voltar direto não pode esconder parte
aplicável, nem obrigatória nem opcional.

**Independent Test:** por requisição, com a Versão de 2024 e com uma Versão de teste que
tenha uma Seção só de opcionais num ramo.

**Acceptance Scenarios:**

1. **Dado** Ana na conclusão, **quando** abre "Avaliação" e muda "Atualmente você trabalha?" de
   "Sim" para "Não" e salva, **então** é levada a "Egresso que não trabalha", com o aviso de
   que a resposta mudou o caminho, ainda em revisão.
2. **Dado** essa situação, **quando** responde "Egresso que não trabalha" e salva, **então**
   volta à conclusão, porque "Estudo", "Egresso que estuda" e a Parte 9 já estão respondidas.
   Foram 2 envios, não 8 nem 9.
3. **Dado** uma Versão de teste em que mudar uma resposta faz entrar uma Seção **só com
   perguntas opcionais**, nunca respondida, **quando** a pessoa salva em revisão, **então** é
   levada a essa Seção antes da conclusão.
4. **Dado** essa Seção só de opcionais, **quando** a pessoa a salva sem responder nada,
   **então** segue para a próxima parte que pede atenção, ou para a conclusão. Ela não volta
   para a mesma Seção.
5. **Dado** uma alteração que faz entrar mais de uma parte nova, **quando** a pessoa salva cada
   uma, **então** passa por todas as partes novas, em ordem, e só pelas que pedem atenção,
   antes de voltar à conclusão.

### US3 — Erros, sessão vencida e saídas continuam como hoje, sem perder a revisão (P2)

**Independent Test:** por requisição, com erro de forma, pendência, sessão vencida e "Salvar
e sair" em revisão.

**Acceptance Scenarios:**

1. **Dado** uma parte aberta pela revisão, **quando** o envio tem erro de forma, **então** nada
   é gravado, a parte é reapresentada com os erros (como hoje) e continua em revisão.
2. **Dado** uma parte aberta pela revisão, **quando** a pessoa apaga uma obrigatória e salva,
   **então** o envio aceito é gravado, a parte é reapresentada com a pendência (como hoje) e
   continua em revisão. Ela não chega à conclusão enquanto a pendência existir.
3. **Dado** uma parte aberta pela revisão e a sessão vencida, **quando** a pessoa envia, entra
   de novo e o envio é restaurado (023), **então** a parte restaurada continua em revisão e,
   ao salvar, segue a mesma regra de destino.
4. **Dado** uma parte aberta pela revisão, **quando** a pessoa usa "Salvar e sair", **então** o
   comportamento é o de hoje (014 FR-011).
5. **Dado** uma parte aberta pela revisão, **quando** a pessoa usa "Voltar à seção anterior",
   **então** a anterior abre também em revisão.

### US4 — Sem revisão, nada muda; o marcador não autoriza nada (P1)

**Independent Test:** a suíte atual da jornada passa sem alteração de expectativa; testes
novos com o marcador forjado.

**Acceptance Scenarios:**

1. **Dado** qualquer Seção aberta sem o marcador de revisão, **então** a tela, os botões, os
   avisos e os destinos são exatamente os de hoje.
2. **Dado** uma pessoa no primeiro preenchimento, **quando** acrescenta o marcador à mão e
   envia, **então** nenhuma parte com obrigatória pendente ou ainda não respondida é pulada.
   No pior caso, só as partes já respondidas que vêm depois são puladas.
3. **Dado** o marcador numa Seção fora do percurso, numa Participação concluída ou com a coleta
   encerrada, **então** valem as respostas de hoje (Seção atual, "já respondida", "período
   encerrado").
4. **Dado** que a pessoa chega à conclusão por esta feature, **então** a conclusão revalida
   tudo, como hoje, e o envio de conclusão é o da 006.

### Edge Cases

- **Parte que sai e volta ao percurso:** se Ana muda "trabalha" para "Não" e depois de novo
  para "Sim", "Egresso que trabalha" volta com as Respostas antigas. Ela conta como já
  respondida e não é reapresentada.
- **Parte já vista e deixada em branco** (só opcionais, nenhuma Resposta): não há como
  distinguir de uma parte nunca vista. Ela é reapresentada. Na dúvida, mostrar.
- **Parte só com texto, sem pergunta** (por exemplo, só termos): não pede atenção.
- **Alteração na primeira parte** que encerra o percurso (Termos "Não"): o destino é o da
  regra. A jornada finaliza pela regra da Versão, e a conclusão mostra o que a 006 permite.
- **Formação declarada (019):** a revisão e a regra valem igualmente.
- **Várias abas:** cada aba segue o marcador do próprio endereço. Nada é guardado entre elas.

## Requirements

**Entrada em revisão**

- **FR-001**: Cada parte da lista de revisão da conclusão DEVE abrir a Seção com um marcador
  de revisão no endereço. O marcador é transitório: NÃO DEVE ser gravado em banco, em sessão
  ou no navegador (Const. XXII; 023 FR-034, FR-035).
- **FR-002**: A Seção aberta com o marcador DEVE:
  - (a) levar o marcador no próprio formulário, para que o envio o carregue;
  - (b) trocar o rótulo do botão principal por "Salvar e voltar à conclusão";
  - (c) trocar a linha da parte (023 FR-013) por "Parte X · revisando suas respostas", sem o
    máximo restante;
  - (d) manter "Salvar e sair", o ponto do meio (023 FR-010) e "Voltar à seção anterior",
    esta com o marcador.

  Fora isso, a Seção é a de hoje.
- **FR-003**: Sem o marcador, a Seção, os avisos e os destinos DEVEM ser exatamente os de
  hoje.

**Destino depois de salvar em revisão**

- **FR-004**: Um envio **aceito e sem pendência** na Seção, com o marcador e sem "Salvar e
  sair", DEVE levar ao primeiro destino abaixo, calculado com as Respostas já gravadas:
  1. a primeira Seção do percurso, **depois da Seção enviada**, que **pede atenção**, aberta
     com o marcador;
  2. se nenhuma pedir atenção, a tela de conclusão.

  Uma Seção **pede atenção** quando tem obrigatória pendente (é a Seção atual da 006) ou
  quando tem ao menos uma Pergunta e nenhuma Resposta gravada.
- **FR-005**: O FR-004 só muda o destino. Validação de forma, gravação (005), Respostas
  inativas fora do percurso e cálculo do percurso (006) DEVEM ser os de hoje. Envio com erro
  de forma ou com pendência DEVE ser reapresentado como hoje (014; 023), com o marcador.
- **FR-006**: Quando o FR-004 leva a uma Seção, ela DEVE mostrar um aviso discreto de que a
  resposta mudou o caminho da pesquisa e que a parte precisa ser conferida antes de concluir.
  Texto provisório (DP-801): "Sua resposta mudou o caminho da pesquisa. Confira esta parte
  para concluir."
- **FR-007**: Quando o FR-004 leva à conclusão, a tela DEVE mostrar uma confirmação discreta
  de que a parte foi salva, **só** se a Seção enviada tiver Resposta gravada (014 FR-008).
  Texto provisório: "Parte salva." O resto da conclusão não muda nesta feature.

**Garantias**

- **FR-008**: Nenhum destino do FR-004 pode pular uma Seção do percurso que pede atenção. A
  conclusão só é destino quando nenhuma pede, e então a jornada está finalizada pela 006.
- **FR-009**: O marcador NÃO DEVE autorizar nada. Seção fora do percurso, Participação
  concluída, coleta encerrada e qualquer outra recusa DEVEM seguir as regras de hoje (008
  FR-055; 006). A conclusão continua revalidando na exibição e no envio.
- **FR-010**: A restauração de um envio pendente (023 FR-007) DEVE manter o modo revisão
  quando o envio guardado tiver o marcador.
- **FR-011**: Esta feature NÃO DEVE criar modelo, tabela, coluna, migração, JavaScript,
  armazenamento no navegador, rota ou tela nova, nem mudar Pergunta, Seção, regra,
  encaminhamento, obrigatoriedade ou texto de qualquer Versão (023 FR-033 a FR-035).
- **FR-012**: O fechamento DEVE ter testes por requisição para cada cenário de aceitação,
  incluindo:
  - a Versão de 2024 nos casos de Ana (US1, US2.1, US2.2);
  - uma Versão de teste com Seção só de opcionais num ramo (US2.3, US2.4);
  - entrada de mais de uma parte (US2.5);
  - o marcador forjado no primeiro preenchimento (US4.2);
  - a igualdade da Seção sem o marcador (US4.1).

  (Const. XXVI.)

## Success Criteria

- **SC-001**: Corrigir uma resposta que não muda o caminho custa **1 envio** a partir da
  conclusão, em qualquer parte do percurso de Ana. Hoje custa de 1 a 9 envios.
- **SC-002**: Corrigir uma resposta que muda o caminho custa 1 envio mais 1 por parte nova que
  pede atenção. No caso "trabalha → não trabalha", são 2 envios.
- **SC-003**: Em todos os testes, nenhuma chegada à conclusão acontece com uma parte do
  percurso que pede atenção.
- **SC-004**: A suíte existente da jornada passa sem mudar nenhuma expectativa sobre telas sem
  o marcador.
- **SC-005**: Nenhum modelo, migração, JavaScript ou armazenamento novo
  (`makemigrations --check` limpo).

## Assumptions

- O egresso que abre uma parte pela revisão quer voltar à conclusão. Quem quiser percorrer
  tudo de novo pode abrir cada parte.
- Reapresentar uma parte só de opcionais já vista e deixada em branco é aceitável. O custo é
  raro e a alternativa seria guardar quais partes foram vistas (estado novo).
- A apresentação visual da lista de revisão (D1, D2 da auditoria) é outra entrega. Aqui, os
  links atuais só ganham o marcador.

## Requisitos revisados

| Origem | Revisão |
|---|---|
| 006 FR-014 (destino depois do envio) | Em revisão, o destino é o do FR-004. Sem marcador, não muda |
| 023 FR-013 (linha da parte) | Em revisão, "Parte X · revisando suas respostas", sem o máximo restante (FR-002c) |
| 023 FR-016 ("Parte anterior salva.") | Em revisão, substituído pelo aviso de mudança de caminho (FR-006) ou pela confirmação na conclusão (FR-007) |
| 023 FR-027 (conclusão) | A lista de revisão ganha o marcador e a conclusão, a confirmação do FR-007. A ordem não muda nesta feature |

## Decisões para aprovação

| # | Decisão | Proposta |
|---|---|---|
| A1 | Regra de destino | "Próxima parte que pede atenção" (FR-004), no lugar da comparação de percursos da auditoria |
| A2 | Rótulo do botão em revisão | "Salvar e voltar à conclusão", com o aviso do FR-006 quando o caminho muda |
| A3 | Linha da parte em revisão | "Parte X · revisando suas respostas" |
| A4 | Confirmação na conclusão | "Parte salva.", só com Resposta gravada |
| A5 | "Voltar à conclusão sem salvar" | **Não** incluir: salvar sem mudança já volta (US1.3), e o "voltar" do navegador também |

## Decisões Pendentes

- **DP-801:** textos definitivos (FR-002, FR-006, FR-007).
- D3 e D4 da auditoria (título da Seção 13 e texto de encerramento) seguem pendentes e não
  afetam esta feature.

## Out of Scope

Refinamento visual da conclusão e da confirmação (próxima entrega); resumo de respostas;
edição na própria conclusão; salvar várias partes de uma vez; qualquer mudança na Versão.
