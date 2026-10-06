# Feature Specification: Jornada de resposta com menos esforço (sem mudar o instrumento)

**Feature Branch**: `claude/trajetoria-ifes-friction-audit-e237ee`

**Created**: 2026-10-05

**Status**: Draft

**Input**: User description: "Feature 023 — Jornada de resposta com menos esforço (sem mudar
o instrumento). Fonte normativa: docs/auditorias/2026-10-05-auditoria-esforco-preenchimento.md.
Preservar rigorosamente a fronteira A+B da auditoria: não incorporar itens C ou D; não
alterar Pergunta, Opção, Seção, regra, obrigatoriedade ou semântica do instrumento; não
pré-preencher Q10–Q19 nem nada a partir da Conclusão; nenhum default de resposta; nenhuma
dependência de JavaScript; sem sessionStorage/autosave. […] Decisões já tomadas pelo
solicitante em 2026-10-05: preservar envio expirado no servidor; sessionStorage fora;
complemento mantém a recusa com campo visível."

## Contexto

A [auditoria de esforço de preenchimento](../../docs/auditorias/2026-10-05-auditoria-esforco-preenchimento.md)
(achados **EF-nn**) mediu a jornada de uma egressa típica: 12 telas, 46 perguntas, cerca de
62 toques e cerca de 27 telas de rolagem num celular. Ela separou dois tipos de esforço:

- **trabalho desperdiçado**: perder o que foi marcado, erro evitável, não saber quanto
  falta, não achar o próximo passo. A interface e pequenas mudanças funcionais resolvem
  (grupos A e B da auditoria);
- **trabalho estrutural**: perguntas que a instituição já sabe, repetição entre formações e
  entre Campanhas, Seções desequilibradas. Só uma nova Versão do instrumento, com decisões
  da CPAEG e fonte acadêmica real, resolve (grupos C e D).

Esta feature trata **só do primeiro tipo**. Ela responde:

> **"Quanto trabalho desperdiçado dá para tirar da jornada sem mudar uma única Pergunta,
> Opção, Seção, regra ou obrigatoriedade do instrumento?"**

O segundo tipo vira um pacote de decisões para a CPAEG ("Versão contextualizada do
instrumento"), fora desta feature.

### Decisões do solicitante (2026-10-05)

| # | Assunto | Decisão |
|---|---|---|
| S1 | Envio de Seção com a sessão expirada (EF-01) | **Preservar no servidor**: o que foi enviado fica guardado temporariamente e volta como marcações na Seção depois da nova confirmação, sem gravar sozinho. Nunca volta ao HTML da tela de confirmação. É descartado se a confirmação resolver outro sujeito |
| S2 | Recuperação local das marcações não enviadas (EF-02) | **Fora da 023.** Mantém a exclusão da 014 (FR-043). Vira aprimoramento isolado, avaliado depois do teste com usuários |
| S3 | Complemento preenchido com a Opção desmarcada (EF-08) | **Manter a recusa** da 005/008, sem descartar texto em silêncio. Em erro, o campo fica visível e a mensagem explica as duas saídas |

### Princípios desta spec

1. **O instrumento não muda.** Nenhuma Pergunta, Opção, Seção, regra de navegação,
   encaminhamento, obrigatoriedade, texto de Versão, tipo ou ordem é alterado. Nenhuma
   Pergunta é ocultada, pulada, pré-preenchida ou sugerida. Itens C e D da auditoria não
   viram requisito.
2. **Nada é decidido pela pessoa sem que ela veja.** Nenhum valor de resposta é escolhido
   pelo sistema. Restaurar o que a própria pessoa enviou e não chegou a ser gravado não é
   default: os valores são dela, aparecem marcados e só são gravados quando ela envia de
   novo.
3. **Sem JavaScript.** A jornada continua funcionando inteira sem JavaScript (008
   FR-080). A divulgação condicional usa só CSS, e o navegador sem suporte mostra o
   comportamento de hoje.
4. **Nenhuma mensagem falsa.** A regra de verdade da 014 (FR-008) vale para toda frase
   nova: só se diz "salvo" quando há Resposta gravada, e só se diz "guardamos o que você
   marcou" quando o envio pendente foi de fato guardado.
5. **Revisões explícitas.** Onde esta feature contraria um requisito vigente (008, 014,
   018, 019), o requisito revisado é citado e a revisão é estreita (seção "Requisitos
   revisados").
6. **Textos provisórios.** Todo texto citado é exemplo funcional, revisável sem mudar
   comportamento (008/DP-801).

### Verificação no código (base `main` em `226ab6b`)

| # | Fato verificado | Evidência | Consequência para a 023 |
|---|---|---|---|
| C1 | Sem Pessoa válida, toda tela da jornada redireciona para `/acesso/` sem parâmetro | `interface/views.py` (`_pessoa`) | Hoje "expirada" e "ausente" são indistinguíveis para a pessoa (EF-01) |
| C2 | A revalidação apaga a sessão inteira ao detectar expiração | `acesso/sessao.py` (`pessoa_em_uso`, `flush`) | A preservação exige um registro separado da sessão de Pessoa |
| C3 | Nova confirmação faz `cycle_key` e limpa a sessão | `acesso/sessao.py` (`estabelecer`) | O envio pendente precisa atravessar a confirmação sem virar dado da sessão de Pessoa |
| C4 | Sessões ficam no banco; o guia de implantação agenda `clearsessions` diário | `config/settings.py`; `docs/implantacao/datacenter-ubuntu.md` | O envio pendente tem validade curta e limpeza garantida |
| C5 | O percurso determinado é uma função pura da Versão e das Respostas | `participacao/percurso.py` | O "faltam no máximo N" pode ser outra função pura, sem persistência |
| C6 | Toda Versão aplicada é PUBLICADA, com destinos sempre posteriores | 006 FR-015 | O grafo de Seções não tem ciclo; o maior caminho restante é bem definido |
| C7 | O complemento fica sempre visível; complemento com a Opção desmarcada recusa a Seção inteira | `interface/formularios.py` (`clean`); 008, 005 FR-030 | EF-08 |
| C8 | A confirmação oferece só a Minha trajetória e o convite de e-mail | `interface/templates/interface/concluida.html` | EF-06 |
| C9 | A situação de entrada já lista as formações pendentes da Pessoa | `participacao/entrada.py` (`situacao_de_entrada`) | EF-06 e EF-19 sem consulta nova de domínio |
| C10 | O selo do declarante vale 30 minutos; vencido, redireciona para `/acesso/` sem aviso | `declaracao/views_egresso.py`; `config/settings.py` | EF-18 |

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Não perder o que foi marcado quando a sessão expira (Priority: P1)

Ana está respondendo a Seção "Avaliação" (14 perguntas) no celular, para por mais de 30
minutos e, ao voltar, toca em "Salvar e continuar". Hoje ela cai na tela de CPF sem
explicação e perde tudo o que marcou. Com a 023, ela vê por que precisa confirmar os dados,
confirma e volta à mesma Seção com as marcações de antes, para conferir e salvar.

**Why this priority**: é o único P0 da auditoria que a interface resolve por inteiro. Perder
trabalho sem explicação quebra a confiança e termina em abandono.

**Independent Test**: com a inatividade configurada para 1 minuto, marcar respostas numa
Seção, esperar, enviar, confirmar os dados e verificar que a Seção reaparece com as
marcações e que nada foi gravado antes do novo envio.

**Acceptance Scenarios**:

1. **Given** uma Seção com marcações não enviadas e a sessão expirada por inatividade,
   **When** a pessoa envia a Seção, **Then** a entrada mostra um aviso de que, por
   segurança, é preciso confirmar os dados de novo e de que o que ela marcou nesta parte foi
   guardado e volta depois da confirmação; nenhuma Resposta é gravada nesse envio.
2. **Given** o cenário 1, **When** a pessoa confirma CPF e data da mesma Pessoa dentro da
   validade, **Then** ela vai direto à mesma Seção, com os valores enviados marcados e um
   aviso para conferir e salvar; nenhuma Resposta foi gravada até ela enviar de novo.
3. **Given** o cenário 2, **When** ela envia a Seção, **Then** a gravação é a de sempre
   (005), e o envio pendente deixa de existir.
4. **Given** o cenário 1, **When** quem confirma é outra Pessoa, **Then** o envio pendente
   é descartado sem ser mostrado, e a outra Pessoa segue o caminho normal.
5. **Given** o cenário 1, **When** a confirmação acontece depois da validade (30 minutos),
   **Then** o envio pendente não é usado; a pessoa vai à Seção atual sem marcações
   restauradas e sem frase sobre recuperação.
6. **Given** a sessão expirada, **When** a pessoa só abre uma tela (sem enviar nada),
   **Then** a entrada mostra o aviso de segurança, sem falar em marcações guardadas.
7. **Given** um envio pendente guardado, **When** a pessoa usa "Sair", **Then** ele é
   descartado.

---

### User Story 2 — Ir direto para a próxima formação depois de concluir (Priority: P1)

Bruno tem duas formações. Ao concluir a pesquisa da primeira, a confirmação mostra a outra e
um botão para responder sobre ela. Hoje esse caminho passa pela Minha trajetória, pelo fim
da página e pela tela de formações.

**Why this priority**: sem isso, quem tem mais de uma formação tende a achar que terminou.
O custo é muito baixo.

**Independent Test**: com uma Pessoa de duas formações pendentes, concluir a primeira e,
na confirmação, iniciar a segunda com um toque.

**Acceptance Scenarios**:

1. **Given** uma Pessoa com outra formação em situação de iniciar ou retomar, **When** ela
   conclui uma Participação, **Then** a confirmação mostra a linha da próxima formação, na
   ordem da 007, com o botão "Responder sobre esta formação" (ou "Continuar…", quando em
   andamento), antes da ligação para a Minha trajetória.
2. **Given** duas ou mais formações pendentes, **When** a confirmação é exibida, **Then**
   aparece só a primeira, mais a ligação "Ver todas as suas formações".
3. **Given** nenhuma outra formação pendente (inclusive ambiguidade operacional ou sem
   pesquisa), **When** a confirmação é exibida, **Then** ela fica como hoje.
4. **Given** uma Participação declarada (019), **When** a confirmação é exibida, **Then**
   ela fica como hoje.

---

### User Story 3 — Saber onde estou e quanto falta (Priority: P1)

Em cada Seção, a pessoa vê "Parte 4 · faltam no máximo 4 partes". Ao voltar outro dia, a tela de
formações diz "Você parou em Avaliação · faltam no máximo 4 partes".

**Why this priority**: sem horizonte, as Seções de 5 telas parecem não ter fim. A
auditoria registra isso como causa de abandono.

**Independent Test**: percorrer os 17 percursos esperados da baseline e verificar, em cada
Seção, que a parte corresponde à posição no percurso e que o "no máximo" nunca é menor que
o número de Seções que de fato vieram depois.

**Acceptance Scenarios**:

1. **Given** a primeira Seção da baseline, **When** ela é exibida, **Then** mostra "Parte 1"
   e o maior número de Seções que ainda podem vir pelas regras da Versão.
2. **Given** uma Seção cuja pergunta com regra já foi respondida, **When** ela é exibida,
   **Then** o máximo ainda considera todos os destinos dessa pergunta, porque a resposta
   pode mudar até a pessoa deixar a Seção.
3. **Given** a última Seção possível de um percurso, **When** ela é exibida, **Then** mostra
   "Última parte".
4. **Given** uma Participação em andamento, **When** a tela de formações é exibida,
   **Then** cada formação em andamento diz onde a pessoa parou e o máximo que falta; com
   todas as Seções satisfeitas e a conclusão pendente, diz "Falta só concluir".
5. **Given** uma Seção sem título na Versão, **When** ela aparece na aba, na revisão ou em
   "você parou em", **Then** é chamada de "Parte X", nunca de "Seção {posição}".
6. **Given** um envio aceito sem pendências, **When** a Seção seguinte é exibida, **Then**
   ela informa discretamente que a parte anterior foi salva, só se a Seção anterior tiver
   Resposta gravada.

---

### User Story 4 — Descrever "Outro" sem cair num erro evitável (Priority: P1)

Na Seção "Avaliação", o campo "Descreva" só aparece quando "Outro" está marcado. Se a
pessoa escrever e depois desmarcar, o erro mostra o campo e diz como resolver.

**Why this priority**: é o único erro de forma da jornada, e ele recusa a Seção mais longa.

**Independent Test**: em navegador com suporte, verificar que o campo fica oculto até a
Opção ser marcada; sem suporte, que tudo funciona como hoje; com envio de complemento e
Opção desmarcada, que a recusa mostra o campo e a nova mensagem.

**Acceptance Scenarios**:

1. **Given** uma Pergunta com Opção que admite complemento, **When** a Opção não está
   marcada, **Then** o campo de descrição não aparece nem recebe foco; **When** é marcada,
   **Then** o campo aparece logo abaixo das Opções.
2. **Given** um complemento já gravado (com a Opção marcada), **When** a Seção é reaberta,
   **Then** o campo aparece com o texto.
3. **Given** complemento preenchido e Opção desmarcada no envio, **When** a Seção é
   recusada, **Then** nada é gravado (005 FR-030), o campo aparece com o texto e a mensagem
   diz: "Você escreveu uma descrição para «Outro», mas a opção não está marcada. Marque
   «Outro» ou apague a descrição."
4. **Given** um navegador sem suporte à regra condicional de CSS, **When** a Seção é
   exibida, **Then** o campo aparece sempre, como hoje.

---

### User Story 5 — Saber o que fazer quando os dados não são confirmados (Priority: P2)

A tela "Não foi possível confirmar" passa a oferecer dois passos em ordem: primeiro conferir
os dados; se estiverem certos, informar a formação, que passará por verificação.

**Why this priority**: afeta só quem não é localizado, mas a escolha errada custa caro
(declaração desnecessária ou tentativas bloqueadas).

**Independent Test**: provocar `NAO_CONFIRMADA` por cada causa interna e verificar que a
tela é idêntica em todas, com os dois passos em ordem.

**Acceptance Scenarios**:

1. **Given** qualquer `NAO_CONFIRMADA`, **When** a tela é exibida, **Then** mostra a
   mensagem da 018 e, em ordem, "1. Confira se o CPF e a data estão certos" com a ação
   "Conferir os dados" e "2. Se estiverem certos, sua formação pode ainda não estar na nossa
   base" com a ação "Informar minha formação" e a nota de verificação institucional.
2. **Given** uma sessão de outra confirmação anterior no mesmo navegador, **When** a nova
   tentativa falha, **Then** a ligação "Continuar para suas formações" não aparece.
3. **Given** causas internas diferentes, **When** as telas são comparadas, **Then** são
   idênticas (018 FR-032).

---

### User Story 6 — Menos rolagem e menos ruído nas Seções (Priority: P2)

A pessoa lê menos e rola menos: só as 4 perguntas opcionais são marcadas como "(opcional)";
as perguntas de duas opções curtas ficam lado a lado; o convite de abertura fica recolhido
em "Sobre esta pesquisa"; o rodapé da Seção perde "Sair sem salvar esta seção"; as Seções
com mais de 8 perguntas ganham, no meio, "Precisa parar? Salvar e sair".

**Why this priority**: ganho constante em todas as Seções, com custo baixo; reduz a
exposição à perda nas Seções longas.

**Independent Test**: medir a altura das Seções no cenário A a 375×812 antes e depois e
verificar a marcação, o layout e os botões por requisição.

**Acceptance Scenarios**:

1. **Given** uma Pergunta obrigatória, **When** é exibida, **Then** não mostra
   "(obrigatória)" e continua anunciada como obrigatória à tecnologia assistiva; **Given**
   uma opcional, **Then** mostra "(opcional)".
2. **Given** uma escolha única com exatamente duas Opções curtas, **When** cabe na largura,
   **Then** as Opções ficam lado a lado, com alvo de toque de pelo menos 44 px; **When** não
   cabe (fonte ampliada), **Then** voltam a empilhar.
3. **Given** a primeira Seção com texto de abertura, **When** é exibida, **Then** o texto de
   abertura fica num bloco recolhido "Sobre esta pesquisa", e o texto da própria Seção
   (termos) continua visível por inteiro.
4. **Given** uma Seção com mais de 8 perguntas, **When** é exibida, **Then** há, depois da
   pergunta do meio, o bloco "Precisa parar? O que você marcou até aqui fica salvo." com o
   botão "Salvar e sair", que se comporta exatamente como o do rodapé.
5. **Given** uma Seção sem erro de forma, **When** é exibida, **Then** o rodapé tem "Salvar
   e continuar", "Salvar e sair" e, quando houver, "Voltar à seção anterior"; **Given** a
   reapresentação com erro de forma, **Then** "Sair sem salvar esta seção" continua
   disponível.

---

### User Story 7 — Concluir e ver a confirmação sem rolar (Priority: P3)

Na tela "Concluir a pesquisa", o aviso de irreversibilidade e o botão vêm primeiro; a
revisão e o contexto vêm depois. Na confirmação, as ações vêm antes do contexto.

**Why this priority**: refinamento de cerca de 1 tela de rolagem em cada uma.

**Independent Test**: verificar a ordem dos elementos por requisição.

**Acceptance Scenarios**:

1. **Given** a tela de conclusão, **When** é exibida, **Then** a ordem é: título, frase de
   fim com o aviso de que não poderá ser alterada, botão "Concluir pesquisa", lista para
   revisar, contexto da formação.
2. **Given** a confirmação, **When** é exibida, **Then** a ordem é: título e frase de
   registro, texto de encerramento da Versão (ou agradecimento), ações (próxima formação
   quando houver, Minha trajetória, convite de e-mail), contexto da formação.

---

### User Story 8 — Entrada e declaração com menos atrito (Priority: P3)

A dica da data aceita o que o teclado numérico oferece ("Só os números, por exemplo
05031994"). No formulário de declaração, o nome pode ser preenchido pelo navegador, o
nível é escolhido com um toque, a confirmação mostra a linha completa e permite corrigir, e
"Começar" tem destaque de ação principal. Se o selo da declaração vencer, a pessoa vê por
que precisa confirmar os dados de novo.

**Why this priority**: refinamentos de baixo custo no início da jornada e no caminho
declarado.

**Independent Test**: por requisição, verificar atributos, rótulos, ordem e destaques; com
selo vencido, verificar o aviso.

**Acceptance Scenarios**:

1. **Given** a entrada, **When** é exibida, **Then** a dica da data diz que basta digitar os
   números.
2. **Given** o formulário de declaração, **When** é exibido, **Then** o nome tem
   preenchimento automático de nome, e o nível é escolhido por botões de opção.
3. **Given** a confirmação da declaração, **When** é exibida, **Then** mostra curso,
   unidade, nível e ano; "Começar" é a ação principal; "Corrigir" volta ao formulário
   preenchido, sem nova confirmação de CPF e data dentro da validade do selo.
4. **Given** um selo vencido, **When** a pessoa avança na declaração, **Then** a entrada
   mostra: "Por segurança, confirme seus dados de novo para continuar."

---

### Edge Cases

- **Envio pendente de uma Seção que saiu do percurso** (outra resposta mudou o caminho
  antes da nova confirmação): o envio pendente é descartado, e vale o aviso de percurso da
  008.
- **Envio pendente com a Participação concluída ou a coleta encerrada** antes da nova
  confirmação: descartado; vale a tela de estado de hoje.
- **Dois envios pendentes seguidos** (a pessoa volta, não confirma e envia de outra aba):
  vale só o último.
- **Envio pendente com erro de forma** (por exemplo, complemento sem Opção): é restaurado
  como foi enviado; o erro aparece no novo envio, como sempre.
- **Envio pendente vindo de "Salvar e sair"**: depois da confirmação, a pessoa volta à
  Seção para conferir; a intenção de sair não é executada sem ela.
- **Sessão ausente, sem sinal de expiração** (navegador fechado, cookie perdido): um envio
  de Seção é guardado da mesma forma, porque só será usado se a confirmação resolver o dono
  da Participação; o aviso é o mesmo, sem afirmar que houve inatividade.
- **Declarante (019) com sessão expirada**: o envio pendente é guardado; depois de
  `NAO_CONFIRMADA` → "Informar minha formação" → lista das formações informadas →
  "Continuar", a Seção aparece restaurada se a Participação for daquele par.
- **Validade do envio pendente** termina em 30 minutos contados do envio, mesmo que a
  sessão nova seja mais longa.
- **Indicador em Seção revisitada** ("Voltar à seção anterior"): a parte é a posição dessa
  Seção no percurso determinado; o máximo é calculado a partir dela.
- **Pergunta com regra cujas Opções não têm todas regra, ou que é opcional**: o máximo
  considera também o destino padrão (encaminhamento ou Seção seguinte), como a 006.
- **Superestimativa**: depois que a pessoa deixa uma Seção com regra, o máximo da Seção
  seguinte já reflete o ramo escolhido; enquanto ela está na Seção, o máximo cobre todos os
  ramos. O "no máximo" do texto é verdadeiro nos dois casos.
- **"Parte anterior salva"** depois de voltar e reenviar uma Seção sem mudanças: só aparece
  se a Seção anterior tem Resposta gravada (regra de verdade).
- **Duas Opções curtas com "Deixar esta pergunta sem resposta"**: a caixa continua fora do
  grupo, abaixo das Opções (014 FR-022).
- **Pergunta com regra entre as duas metades** de uma Seção longa: o "Salvar e sair" do meio
  não decide nada; a regra só é lida ao deixar a Seção (006).
- **Navegador sem suporte à regra condicional de CSS**: complementos sempre visíveis, como
  hoje; nenhuma outra função depende disso.
- **Próxima formação na confirmação com a situação mudando** entre a exibição e o toque: o
  botão usa a entrada da 007, que reavalia no próprio momento; se mudou, vale o aviso de
  situação de hoje.

## Requirements *(mandatory)*

### Functional Requirements

**Sessão expirada e envio preservado (EF-01)**

- **FR-001**: Quando uma tela da jornada é pedida sem sujeito válido e a sessão anterior
  deixou de valer (inatividade, duração máxima ou revalidação), a entrada DEVE explicar o
  motivo de forma genérica (exemplo: "Por segurança, confirme seus dados de novo para
  continuar. O que você já tinha salvo continua guardado."). Vale para toda tela do egresso
  que exige sujeito: formações, Participação, Seção, conclusão, confirmação, formações
  informadas, Minha trajetória e e-mail. Sem sessão anterior, a entrada fica como hoje. O endereço NÃO DEVE conter dado pessoal, formação, Participação ou
  Campanha. [EF-01; Solicitante; 018 FR-041]
- **FR-002**: Quando um envio de Seção chega sem sujeito válido, o sistema DEVE guardar
  temporariamente um **envio pendente** com: a Participação e a Seção do endereço, os
  valores enviados para as Perguntas dessa Seção e o instante do envio. NADA DEVE ser
  gravado como Resposta nesse momento. O envio pendente NÃO DEVE conter CPF, data de
  nascimento ou material de verificação. [EF-01; S1]
- **FR-003**: Com envio pendente guardado, o aviso da entrada DEVE dizer também que o que a
  pessoa marcou nesta parte foi guardado e volta depois da confirmação (exemplo: "O que
  você marcou nesta parte foi guardado e volta assim que você confirmar."). Sem envio
  pendente guardado, essa frase NÃO DEVE aparecer. [EF-01; princípio 4]
- **FR-004**: O envio pendente DEVE ser válido por **30 minutos** a partir do envio, NÃO
  DEVE ser usado depois disso e NÃO DEVE permanecer armazenado além da validade mais o
  intervalo da limpeza operacional de sessões já prevista na implantação. Há no máximo um
  por navegador; um envio novo substitui o anterior. [S1; Const. XVI]
- **FR-005**: A nova confirmação no mesmo navegador DEVE manter o envio pendente separado
  da sessão do sujeito. A sessão do sujeito continua identificando somente a Pessoa (018
  FR-040) ou o par declarante (019). O máximo que ela guarda é uma chave opaca do registro
  do envio pendente, sem Participação, Seção nem valores. [S1; 018 FR-040, FR-043]
- **FR-006**: Depois da nova confirmação de uma Pessoa (018), se há envio pendente válido de
  Participação dessa Pessoa, a pessoa DEVE ir direto à Seção do envio pendente, em vez da
  tela de formações (redirecionamentos intermediários são aceitáveis). Se a Participação
  não é dela, o envio pendente DEVE ser descartado sem
  ser exibido, e a confirmação segue o caminho de hoje. [EF-01; S1]
- **FR-007**: Quando o sujeito dono da Participação abre a Seção do envio pendente dentro da
  validade, a Seção DEVE ser apresentada com os valores do envio pendente no lugar dos
  gravados, e um aviso (exemplo: "Recuperamos o que você tinha marcado nesta parte.
  Confira e toque em Salvar e continuar."). Isso vale também para o declarante, que chega
  pela lista das formações informadas (019). [EF-01; S1]
- **FR-008**: O envio pendente DEVE ser descartado: no primeiro envio aceito daquela Seção;
  quando a Seção sai do percurso determinado; quando a Participação é concluída ou a coleta
  deixa de admitir escrita; quando a validade termina; ao "Sair"; e quando a confirmação
  resolve outro sujeito. [S1]
- **FR-009**: A restauração NÃO DEVE gravar nada sozinha, NÃO DEVE executar o destino
  pedido no envio original ("Salvar e sair") e NÃO DEVE devolver os valores pendentes à tela
  de confirmação de dados. [S1]

**Pontos seguros de salvamento (EF-02)**

- **FR-010**: Seções com **mais de 8 Perguntas** DEVEM apresentar, logo depois da Pergunta
  do meio (posição ⌈n/2⌉), um bloco com uma frase curta (exemplo: "Precisa parar? O que você
  marcou até aqui fica salvo.") e um botão "Salvar e sair" com o mesmo comportamento,
  validação e gravação do botão do rodapé (014 FR-011, FR-012). Esse botão NÃO DEVE ser o
  envio padrão de Enter (014 FR-016). [EF-02; Hipótese quanto ao limiar de 8]

**Próxima formação (EF-06)**

- **FR-011**: Na confirmação de Participação ancorada em Conclusão Acadêmica, se a Pessoa
  tem outra formação em situação de iniciar ou retomar (007), a confirmação DEVE mostrar a
  primeira delas na ordem da 007, na forma compacta (014 FR-034), com uma ação de envio que
  usa a entrada existente (007) para aquela formação ("Responder sobre esta formação" ou
  "Continuar a pesquisa desta formação"). Com mais de uma, DEVE haver também "Ver todas as
  suas formações". [EF-06; 014 FR-035]
- **FR-012**: Formações sem pesquisa, já concluídas ou em ambiguidade operacional NÃO DEVEM
  ser oferecidas na confirmação. A confirmação declarada (019) NÃO DEVE mudar. [EF-06; 014
  FR-037]

**Progresso e retomada (EF-07, EF-19)**

- **FR-013**: Toda tela de Seção DEVE mostrar a **parte** (posição da Seção no percurso
  determinado da 006, começando em 1) e o **máximo de partes restantes**: o número de
  Seções do caminho mais longo que vai da Seção exibida até a finalização, segundo as
  regras, encaminhamentos e ordem da Versão, considerando todos os destinos possíveis das
  perguntas com regra da Seção exibida e das seguintes, qualquer que seja a Resposta gravada
  (exemplo: "Parte 4 · faltam no máximo 4 partes"; com um: "falta no máximo 1 parte"). Com máximo zero: "Parte X · última parte". NÃO DEVE haver percentual, barra,
  estimativa de tempo nem total fixo de partes. [EF-07; Hipótese de produto]
- **FR-014**: O máximo de partes restantes DEVE ser uma função de leitura determinística da
  Versão e da Seção exibida (mesma Versão e mesma Seção → mesmo resultado), calculada a cada
  exibição, sem persistir posição, progresso ou contador. Por construção, ele NUNCA DEVE ser
  menor que o número de Seções que de fato vêm depois, quaisquer que sejam as Respostas que
  a pessoa ainda der ou mudar. [EF-07; 006 FR-017; Const. XXII]
- **FR-015**: Seção sem título na Versão DEVE ser chamada de "Parte X" (X da FR-013) no
  título da aba, na lista de revisão da conclusão e na tela de formações. NÃO DEVE aparecer
  "Seção {posição}". O título principal da tela continua o da 014 FR-023. [EF-07; 008 FR-033]
- **FR-016**: Depois de um envio aceito sem pendências que leva à Seção seguinte, essa Seção
  DEVE informar discretamente que a parte anterior foi salva (exemplo: "Parte anterior
  salva."), somente se a Seção enviada tiver Resposta gravada (014 FR-008). [EF-07]
- **FR-017**: Na tela de formações, toda formação com pesquisa em andamento DEVE dizer onde a
  pessoa parou e o máximo restante (exemplo: "Você parou em «Avaliação» · faltam no máximo 4
  partes", ou "Você parou na parte 8"); com máximo zero: "é a última parte"; com a jornada
  finalizada e não concluída: "Falta só concluir". A lista de formações informadas (019) DEVE ter a mesma indicação. [EF-19]

**Complemento (EF-08)**

- **FR-018**: O campo de complemento DEVE ficar oculto (sem ocupar espaço nem receber foco)
  enquanto a Opção que o admite não estiver marcada, e aparecer logo abaixo das Opções quando
  ela for marcada, usando só a folha de estilo. Sem suporte do navegador, o campo DEVE
  aparecer sempre, como hoje. O complemento continua fora do grupo exclusivo de Opções (014
  FR-022). [EF-08; S3; 008 FR-080]
- **FR-019**: O rótulo do campo DEVE deixar claro a que Opção se refere (exemplo:
  "Descreva o que se encaixa em «Outro»"), usando o texto da Opção como hoje. [EF-08]
- **FR-020**: Complemento preenchido com a Opção desmarcada DEVE continuar recusando o envio
  sem gravar nada (005 FR-030; 008), e a Pergunta com esse erro DEVE mostrar o campo com o
  texto enviado, mesmo com a Opção desmarcada, e a mensagem: "Você escreveu uma descrição
  para «{Opção}», mas a opção não está marcada. Marque «{Opção}» ou apague a descrição."
  NÃO DEVE haver marcação automática da Opção nem descarte silencioso do texto. [EF-08; S3;
  Const. III]

**Não confirmação (EF-09)**

- **FR-021**: A tela de `NAO_CONFIRMADA` DEVE manter a mensagem, o status e o conteúdo
  idênticos para toda causa interna (018 FR-032) e apresentar as saídas como dois passos
  numerados, nesta ordem: (1) conferir os dados, com a ação "Conferir os dados" (018
  FR-033); (2) se estiverem certos, informar a formação, com a ação "Informar minha
  formação" e a nota de que ela passará por verificação institucional (019). O texto NÃO
  DEVE sugerir a causa da falha. [EF-09]
- **FR-022**: Na resposta a uma tentativa de confirmação que falhou, a ligação "Continuar
  para suas formações" de uma sessão anterior NÃO DEVE aparecer. [EF-09]

**Altura e ruído (EF-11, EF-12, EF-13, EF-22, EF-23, EF-26)**

- **FR-023**: Perguntas obrigatórias NÃO DEVEM mostrar "(obrigatória)" no enunciado e DEVEM
  continuar anunciadas como obrigatórias à tecnologia assistiva. Perguntas opcionais DEVEM
  mostrar "(opcional)". A mensagem de pendência ("Esta pergunta é obrigatória.") não muda.
  [EF-11]
- **FR-024**: Escolha única apresentada em botões de opção, com **exatamente duas Opções**
  cujos textos tenham até 15 caracteres, DEVE mostrar as Opções lado a lado, com toda a
  célula tocável e alvo de pelo menos 44 × 44 px, voltando a empilhar quando não couberem
  numa linha (mesma regra da escala, 014 FR-021). O critério é só de forma, nunca de
  Pergunta específica (008 FR-034). [EF-12; Hipótese quanto ao limite de 15]
- **FR-025**: O texto de abertura da Versão, na primeira Seção, DEVE ficar num bloco
  recolhido por padrão, com o rótulo "Sobre esta pesquisa", expansível sem JavaScript, com o
  texto exatamente como na Versão (008 FR-033). O texto da Seção (termos) DEVE continuar
  visível por inteiro. [EF-13; Const. XVII]
- **FR-026**: Fora da reapresentação com erro de forma, o rodapé da Seção NÃO DEVE mostrar
  "Sair sem salvar esta seção". Na reapresentação com erro de forma, ela DEVE continuar
  disponível, com o comportamento da 014 FR-013. "Voltar à seção anterior" fica como está
  (014 FR-014). [EF-22]
- **FR-027**: A tela de conclusão DEVE apresentar, nesta ordem: título; frase de fim com o
  aviso de que, depois de concluída, a pesquisa não poderá ser alterada; botão "Concluir
  pesquisa"; convite a revisar com a lista de Seções (FR-015); contexto da formação.
  [EF-23]
- **FR-028**: A confirmação DEVE apresentar, nesta ordem: título e frase de registro (014
  FR-038); texto de encerramento da Versão ou agradecimento (014 FR-040); próxima formação,
  quando houver (FR-011); "Ver minha trajetória no Ifes" (021); convite de e-mail (020);
  contexto da formação. Para a declarada, a ordem relativa de hoje se mantém, com o
  contexto por último. [EF-26]

**Entrada e declaração (EF-17, EF-18, EF-25)**

- **FR-029**: A dica do campo de data de nascimento DEVE dizer que basta digitar os números
  (exemplo: "Só os números, por exemplo 05031994, ou DD/MM/AAAA"). A aceitação dos formatos
  não muda. [EF-17]
- **FR-030**: Quando o selo do declarante vence (019), a entrada DEVE mostrar: "Por
  segurança, confirme seus dados de novo para continuar." O formulário de declaração não é
  preservado. [EF-18]
- **FR-031**: No formulário de declaração, o nome DEVE indicar preenchimento automático de
  nome ao navegador, e o nível DEVE ser escolhido por botões de opção. As opções de nível e
  de unidade e as validações não mudam. [EF-25]
- **FR-032**: A confirmação da declaração DEVE mostrar curso, unidade, nível e ano; "Começar"
  DEVE ter destaque de ação principal e "Sair", menor ênfase; DEVE haver "Corrigir", que
  volta ao formulário com os valores informados, sem nova confirmação de CPF e data
  enquanto o selo for válido. [EF-25]

**Fronteiras e preservações**

- **FR-033**: Esta feature NÃO DEVE alterar Pergunta, Opção, Seção, regra de navegação,
  encaminhamento, obrigatoriedade, tipo, ordem ou texto de qualquer Versão; NÃO DEVE ocultar,
  pular, pré-preencher ou sugerir Pergunta; NÃO DEVE usar dado da Conclusão Acadêmica ou da
  Formação Declarada como valor de resposta; NÃO DEVE criar default de resposta. [Princípio
  1; Const. III, VIII, XIII; 008 FR-028]
- **FR-034**: Esta feature NÃO DEVE criar modelo, tabela, coluna ou migração. O único dado
  novo é o envio pendente (FR-002), transitório e fora da sessão do sujeito. [Const. XXII]
- **FR-035**: A jornada DEVE continuar funcionando inteira com JavaScript desativado, e esta
  feature NÃO DEVE adicionar JavaScript, armazenamento local no navegador, autosave nem
  aviso ao sair da página. [008 FR-080; S2]
- **FR-036**: As exportações, o dataset analítico, a Minha trajetória, o acompanhamento e o
  editor NÃO DEVEM mudar de comportamento. A pré-visualização do editor reutiliza, por
  desenho, a apresentação das Perguntas da jornada (009) e passa a refletir "(opcional)",
  o rótulo do complemento e as Opções lado a lado; o complemento continua sempre visível
  na pré-visualização. [Escopo; 009]
- **FR-037**: O fechamento da feature DEVE exigir testes automatizados por requisição para
  cada FR verificável sem navegador, incluindo: a propriedade da FR-014 nos 17 percursos
  esperados da baseline; o ciclo completo do envio pendente (guardar, restaurar, descartar
  por outro sujeito, por validade e por "Sair"); a igualdade da tela de `NAO_CONFIRMADA`
  entre causas; e a ausência de qualquer mudança no instrumento materializado. [Const. XXVI]
- **FR-038**: A validação visual (alturas a 375×812, layout lado a lado, ocultação do
  complemento) DEVE ser registrada com capturas no fechamento. A validação em aparelho real
  é posterior e não bloqueia o fechamento. [Escopo]

### Requisitos revisados

| Requisito vigente | Revisão pela 023 |
|---|---|
| 008 FR-091 e 014 FR-042 (nenhum rascunho não enviado persistido) | Exceção única: o envio pendente transitório (FR-002 a FR-009), fora da sessão do sujeito, com validade de 30 minutos |
| 008 FR-095 e 014 FR-043 (sem indicador de progresso) | Passa a existir o indicador de partes com máximo restante (FR-013, FR-014), sem percentual nem estimativa de tempo |
| 014 FR-009 e FR-013 ("Sair sem salvar" em toda Seção) | Só na reapresentação com erro de forma (FR-026) |
| 014 FR-041, revisada por 021 e 020 (confirmação sem outra formação) | Passa a oferecer a próxima formação pendente antes da Minha trajetória (FR-011, FR-028) |
| 018 FR-040 (sessão só com a Pessoa) | A sessão pode conter só a chave opaca do registro do envio pendente (FR-005) |
| 018 FR-043 (nova confirmação substitui a sessão integralmente) | A sessão do sujeito continua substituída integralmente; o envio pendente sobrevive à confirmação só para ser usado pelo dono ou descartado (FR-005, FR-006) |
| 018 FR-033 e 019 (saídas de `NAO_CONFIRMADA`) | Mesmas ações, apresentadas em dois passos numerados (FR-021) |
| Enunciados com "(obrigatória)" (008) | Só "(opcional)" nas opcionais (FR-023) |
| Texto de abertura acompanha a primeira Seção (008) | Continua acompanhando, em bloco recolhido (FR-025) |

### Key Entities *(include if feature involves data)*

- **Envio pendente**: cópia transitória do que a própria pessoa enviou numa Seção quando não
  havia sujeito válido. Tem Participação, Seção, valores das Perguntas da Seção e instante.
  Não é Resposta, não é rascunho da 005 e não é dado da sessão do sujeito. Vale 30 minutos,
  é de uso único e é descartado nas condições da FR-008. Origem: **declarado, ainda não
  gravado**.
- **Parte e máximo restante**: leitura derivada. A parte vem do percurso determinado da 006;
  o máximo, só da estrutura da Versão aplicada. Não é persistida, não é Resposta e não é progresso da Participação.
- As demais entidades (Pessoa, Conclusão Acadêmica, Formação Declarada, Campanha, Versão,
  Participação, Resposta) não mudam.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem | Fonte ou regra de derivação | Tratamento de divergência |
|------|--------|-----------------------------|---------------------------|
| Valores do envio pendente | Declarado (não gravado) | O próprio envio da Seção | Só vira Resposta por novo envio da pessoa; descartado se o sujeito não for o dono |
| Parte e máximo restante | Derivado | Parte: percurso determinado (006). Máximo: caminho mais longo no grafo de Seções da Versão | — (leitura) |
| Próxima formação pendente | Institucional | Situação de entrada da 007 | Reavaliada no momento da entrada |
| "Você parou em" | Derivado | Seção atual da 006 | — |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Num envio de Seção feito com a sessão expirada e seguido de confirmação da
  mesma pessoa em até 30 minutos, 100% dos valores enviados reaparecem marcados na Seção, e
  nenhuma Resposta é gravada antes do novo envio.
- **SC-002**: Em 100% das chegadas à entrada por sessão expirada, a pessoa vê o motivo; em
  0% dos casos uma frase de recuperação aparece sem envio pendente guardado.
- **SC-003**: Uma pessoa com duas formações pendentes começa a segunda com **1 toque** a
  partir da confirmação da primeira (hoje: 4 toques e rolagem até o fim da Minha
  trajetória).
- **SC-004**: Em todos os 17 percursos esperados da baseline, o máximo restante mostrado em
  cada Seção nunca é menor que o número de Seções que de fato vieram depois, e a parte
  mostrada é sempre a posição real no percurso.
- **SC-005**: No percurso típico da auditoria (cenário A, celular 375×812), o número de
  erros de forma possíveis cai de 2 para 0 em navegador com suporte à regra condicional de
  CSS.
- **SC-006**: No mesmo cenário, a rolagem total das telas da jornada cai de cerca de 27,6
  para no máximo 25 telas, e a pergunta da primeira Seção fica a no máximo 1,4 tela do topo
  (hoje 1,7).
- **SC-007**: 100% das formações em andamento na tela de formações dizem onde a pessoa
  parou e quanto falta, no máximo.
- **SC-008**: A tela de `NAO_CONFIRMADA` tem o mesmo conteúdo visível e o mesmo status nas
  cinco causas internas da 018.
- **SC-009**: O instrumento materializado, os 17 percursos, as exportações e o dataset
  analítico ficam idênticos aos de antes da feature.
- **SC-010**: Toda a jornada, do acesso à confirmação, continua possível com JavaScript
  desativado.
- **SC-011**: Na reauditoria objetiva prevista depois da 023, todas as telas, exceto
  "Informações do curso" e a Seção de curso (que dependem da nova Versão), passam no
  "teste de 30 segundos" da auditoria.

## Assumptions

- O limiar de "mais de 8 Perguntas" para o salvamento no meio da Seção (FR-010) e o limite
  de 15 caracteres para Opções lado a lado (FR-024) são hipóteses de produto, reversíveis.
  Na baseline, afetam S8 (14) e S9 (11), e as perguntas Sim/Não e Q12.
- A validade de 30 minutos do envio pendente é a mesma da inatividade padrão da sessão (018
  FR-042) e do selo do declarante (019). É política operacional, não regra institucional.
- A limpeza diária de sessões, já prevista no guia de implantação, é suficiente para o
  limite de retenção da FR-004; o plan confirma ou propõe ajuste.
- A regra condicional de CSS usada na FR-018 é suportada pelos navegadores móveis atuais; o
  comportamento sem suporte é o de hoje.
- Os textos citados são provisórios (008/DP-801).
- A 023 parte da `main` em `226ab6b`, com as Features 018 a 022 integradas.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I — Longitudinalidade**: nenhuma Participação, Resposta ou âncora é alterada. O envio
  pendente só vira Resposta pela operação da 005, por novo envio da própria pessoa, na mesma
  Participação.
- **III — Dado institucional não é declarado**: nenhum dado da Conclusão ou da Formação
  Declarada vira valor de campo. O envio pendente é declarado pela própria pessoa e nunca é
  gravado sem novo envio.
- **VIII e XIII — Preservação do instrumento**: nenhuma mudança na Versão; o texto de
  abertura é apresentado recolhido, não alterado; "(opcional)" é marcação de interface,
  não texto da Pergunta.
- **XIV — Redução de fricção**: é o propósito da feature, dentro da fronteira A+B.
- **XV e XVI — Identidade, privacidade e minimização**: a sessão do sujeito continua só com
  o sujeito (018 FR-040). O envio pendente não contém CPF nem data, não vai à URL nem à tela
  de confirmação, tem validade curta e é descartado quando a confirmação resolve outro
  sujeito.
- **XVII — Consentimento**: o texto dos termos (Seção 1) continua visível por inteiro.
- **XX e XXI — Acessibilidade e mobile**: obrigatoriedade continua anunciada; alvos de 44
  px; Opções lado a lado voltam a empilhar com fonte ampliada.
- **XXII — Simplicidade**: sem modelo nem migração; indicador como função pura; nenhum
  JavaScript.

## Out of Scope *(mandatory)*

- Itens C e D da auditoria: retirar ou contextualizar Q10–Q19 e Q3 (EF-03, EF-15), repetição
  no caminho declarado (EF-04), reaproveitamento de respostas entre formações e entre
  Campanhas (EF-05, EF-21), divisão da Seção "Avaliação" (EF-10), rótulo da escala (EF-14),
  condicionais de Q6 e Q48 (EF-16), recusa dos termos (EF-20), opções exclusivas (EF-24).
  Formam o pacote de decisões da CPAEG para a "Versão contextualizada do instrumento".
- Recuperação local de marcações não enviadas (sessionStorage), autosave, aviso ao sair,
  JavaScript (S2).
- Mudar a duração da inatividade ou da sessão (política da 018, configurável sem spec).
- Link de continuação por e-mail, Gov.br ou outro mecanismo de retorno (018/DP-1808;
  004/DP-406).
- Preservar o formulário de declaração quando o selo vence (só o aviso, FR-030).
- Teclado numérico para Q3 e Q10 (EF-15, depende de atributo de formato na Versão).
- Indicador percentual, estimativa de tempo, total fixo de partes.
- Teste com egressos reais (etapa posterior, depois da reauditoria).

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

Nenhuma decisão pendente nova. Esta feature não depende de regra institucional ainda não
definida. Continuam abertas, fora do escopo e sem tratamento provisório novo: 003/DP-301,
DP-302, DP-303, DP-307, DP-308, DP-309; 008/DP-801 (linguagem definitiva); 018/DP-1801 a
DP-1808.
