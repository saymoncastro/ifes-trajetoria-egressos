# Feature Specification: Polish consolidado da jornada do egresso

**Feature Branch**: `claude/consolidar-auditorias-ux-5dfa52`

**Created**: 2026-10-03

**Status**: Implementada e integrada à `main` em 2026-10-03 (PR #21).

**Input**: User description: "014-polish-jornada-egresso — polish consolidado da jornada do
egresso (usabilidade, identidade, mobile-first), conforme a fronteira aprovada na
consolidação das três auditorias de UX."

## Contexto

A interface do egresso (Feature 008) passou por três auditorias, separadas de propósito:

1. **Usabilidade** — [`docs/auditorias/2026-10-01-ux-feature-008.md`](../../docs/auditorias/2026-10-01-ux-feature-008.md)
   (achados **UX-nn**), parcialmente corrigida pelo polish `226ca93`;
2. **Identidade da experiência** — [`docs/auditorias/2026-10-02-identidade-da-experiencia.md`](../../docs/auditorias/2026-10-02-identidade-da-experiencia.md)
   (achados **ID-nn**);
3. **Mobile-first** — [`docs/auditorias/2026-10-03-mobile-first-experiencia.md`](../../docs/auditorias/2026-10-03-mobile-first-experiencia.md)
   (achados **MF-nn**).

Os achados de **interface** ainda válidos das três lentes mexem nos mesmos templates, na
mesma folha de estilo e nos mesmos textos fixos e, separados, se contradiriam. Esta
feature os resolve num **único polish pequeno**, sem mudar instrumento, domínio ou
arquitetura.

Esta feature responde:

> **"Qual é o menor conjunto de mudanças de interface que resolve os achados ainda
> válidos das três auditorias, sem alterar instrumento, domínio ou arquitetura?"**

**Numeração.** Não há roadmap nem reserva de número no repositório (documentos, branches
e PRs verificados em 2026-10-03); a última feature é a 013. O polish anterior da 008
(`226ca93`, PR #12) não recebeu número próprio; este recebe o 014 porque tem spec
própria e revisa requisitos da 008 de forma rastreável.

### Princípios desta spec

1. **Tornar visível o que já existe.** O servidor já grava Seção incompleta, já é
   idempotente a reenvio e a toque duplo. Nada é resolvido no navegador que já esteja
   resolvido no servidor.
2. **Só interface.** Template, folha de estilo, texto fixo e pequenos ajustes na camada
   de apresentação existente. Nenhum modelo, migração, tabela, JavaScript ou abstração
   nova.
3. **Nada de Versão nem de decisão pendente.** Itens [V] (Versão do instrumento), [Dec]
   (decisão institucional pendente) e [T] (validação em aparelho real) não viram
   requisito de implementação.
4. **Nenhuma mensagem falsa.** A interface só afirma que algo está salvo quando há
   Resposta gravada.
5. **Textos provisórios.** Todo texto fixo citado aqui é exemplo funcional, revisável sem
   mudança de comportamento (008/DP-801).
6. **Sem regressão fora da jornada.** A folha de estilo é compartilhada com o editor
   (009), o acompanhamento (011) e a demonstração.

### Verificação no código (base `main` em `e89ca8d`)

| # | Fato verificado | Evidência | Consequência para a 014 |
|---|-----------------|-----------|-------------------------|
| C1 | O código da interface não mudou desde o polish `226ca93`; as auditorias de identidade e mobile descrevem o estado atual | Histórico de `trajetoria/interface` | Os achados ID e MF continuam válidos como descritos |
| C2 | Envio aceito com obrigatórias em branco **grava** o que foi respondido e reapresenta a Seção com pendências | Gravação da 008 sobre as operações da 005 | "Seção incompleta pode ser salva" já é comportamento; falta comunicar (FR-001, FR-002) |
| C3 | Pendências e erros de forma **nunca** aparecem na mesma reapresentação: pendências só depois de envio aceito; erros de forma e rejeições da 005 só na resposta do próprio envio, sem nada gravado (submissão atômica, 008 FR-045) | Fluxo de envio da Seção | A distinção pendência × erro é de apresentação, sem regra nova (FR-003 a FR-007) |
| C4 | A frase "o que já foi preenchido foi salvo" aparece mesmo quando nada foi respondido, porque depende de um indicador fixo no endereço e não do que está gravado (UX-13) | Redirecionamento após envio aceito | Mensagens de salvamento passam a depender do que está gravado (FR-008) |
| C5 | Os dois motores de navegador relevantes não fazem envio implícito **a partir de campos de digitação** quando o primeiro botão de envio do formulário está desabilitado, mesmo oculto (no Blink, Enter com foco em rádio ou caixa não é coberto — correção em research R2) | Código-fonte atual do WebKit e do Blink (implementação do envio implícito de formulário) | Existe solução comprovada sem JavaScript para MF-02 (nota N1); versões antigas e rótulo da tecla ficam [T] |
| C6 | A escala admite qualquer intervalo inteiro com início < fim; o editor da 009 permite criá-la | Restrição da Pergunta (002); formulário do editor (009) | Forçar a escala numa única linha poderia gerar rolagem horizontal; quando não couber, ela precisa quebrar com ordem e alinhamento (FR-021) |
| C7 | A caixa "Deixar esta pergunta sem resposta" só existe em escolha única e escala **não obrigatórias** e fica dentro do grupo exposto como grupo de rádios (UX-19) | Formulário da Seção (008 FR-043 revisado) | Correção junto com a dos controles (FR-023) |
| C8 | Só o círculo e o número de cada ponto respondem ao toque (≈ 44% da célula); nas linhas de rádio e caixa, 16 px de 44 não respondem (MF-04) | Medidas da auditoria mobile [A] | FR-019 |
| C9 | A folha de estilo da jornada é incluída também pelo editor (009), pelo acompanhamento (011) e pelas telas de demonstração; os controles de Pergunta são reutilizados pela prévia de Seção do editor | Templates base do editor e do acompanhamento; prévia da 009 | Estilo restrito às telas do egresso; a prévia acompanha os controles de propósito (FR-045) |
| C10 | A linha "curso · unidade · ano" já existe, usa só o ano mesmo quando há data e também identifica Pessoas na entrada de demonstração | Apresentação da formação (008); entrada de demonstração | Reutilizada na trajetória sem mudar de formato (FR-034) |
| C11 | As formações vêm da 007 numa ordem determinística (ano de conclusão, depois identidade) sem significado de domínio; a data, quando existe, obriga o ano | 001 (ordenação e restrição ano/data); 007 FR-011, FR-021 | A trajetória mantém a ordem da 007 e não a chama de "cronológica" (FR-035) |
| C12 | A 008 FR-023 fixa os textos de situação, inclusive o da ambiguidade operacional, tratamento provisório do 007/DP-701 | 008 FR-023; 007/DP-701 | Só "sem pesquisa" deixa de aparecer por formação; a ambiguidade continua comunicada (FR-036, FR-037) |
| C13 | A confirmação mostra "Obrigado pela sua participação." e, em seguida, o texto de encerramento da Versão, que também agradece (UX-18) | Tela de confirmação | FR-040 |
| C14 | A página de falha de confirmação de envio manda "recarregar", o que descarta as marcações (MF-09) | Página de falha de CSRF | FR-029 |
| C15 | Reenvio e toque duplo não duplicam Respostas: valor igual ao gravado não gera operação, e as restrições de unicidade e o bloqueio da Participação serializam a gravação | Auditoria mobile, seção 12 [A]; gravação da 008 | "Salvar e sair" herda essa garantia; nada novo é criado (FR-011) |

### Estado das auditorias após a verificação

| Situação | Achados |
|---|---|
| **Já resolvidos** (não reabertos) | UX-01 (posição do resumo), UX-02, UX-03, UX-05, UX-06 (grade), UX-08 (frase), UX-10, UX-12, UX-14, UX-15, UX-04 (texto da nota) |
| **Abertos e incorporados** | UX-07, UX-11 (só o heading), UX-13, UX-17 (título), UX-18, UX-19; ID-03, ID-04, ID-06, ID-09, ID-11 (em parte), ID-12, ID-14; MF-01, MF-02, MF-04, MF-05, MF-06, MF-09, MF-10, MF-13, MF-14 |
| **Mudaram de natureza** | UX-04 → MF-01 + "Salvar e sair"; UX-08 → ID-04 + texto de MF-01; UX-13 → regra de verdade das mensagens de salvamento; UX-17 → ID-14; UX-18 → ID-09; UX-06 → ID-03; ID-12 → resolvido pela linha única de C10; observações da 008 "alvo de toque confortável" e "escala cabe numa linha" → revistas por MF-04 e MF-05 |
| **Fora** (seção Out of Scope) | [V], [Dec], [T], MF-03, MF-07, MF-08, MF-11, MF-12, UX-16 |

### Decisões desta especificação

| # | Decisão | Origem |
|---|---------|--------|
| D1 | "Salvar e sair" entra como **ação secundária** e usa só a gravação já existente | Solicitante (consolidação, 2026-10-03) |
| D2 | A saída sem salvar **continua existindo**, renomeada para "Sair sem salvar esta seção", como ação **terciária**; continua navegação simples | Solicitante (2026-10-03) |
| D3 | Hierarquia do rodapé: principal "Salvar e continuar"; secundária "Salvar e sair"; terciárias "Voltar à seção anterior" e "Sair sem salvar esta seção" | Solicitante (2026-10-03) |
| D4 | MF-03 fica fora; a restauração de formulário pelo navegador não é alterada | Solicitante (2026-10-03) |
| D5 | "Salvar e sair" sem nenhuma Resposta gravada na Seção sai normalmente para a trajetória, com mensagem neutra e verdadeira, sem afirmar salvamento | Solicitante (revisão, 2026-10-03) |
| D6 | Enter/"Ir" é bloqueado sem JavaScript; a solução candidata comprovada está em N1, sem tornar o requisito dependente dela | C5 |
| D7 | A escala fica numa linha quando cabe e, quando não cabe, quebra em ordem e alinhada, nunca com rolagem horizontal da página; a recomendação da auditoria (linha única forçada) é descartada por C6 | C6 |
| D8 | A trajetória usa a ordem da 007, sem reordenar nem rotular a ordem | 007 FR-011, FR-021; 008 FR-021 |
| D9 | Por formação, omite-se só "sem pesquisa"; a mensagem de ambiguidade permanece (007/DP-701) | Const. XXIX |
| D10 | Cada formação aparece como linha principal (curso · unidade · ano) e, quando informados, linha complementar (nível · modalidade · forma de oferta); preserva a 008 FR-025 e o tratamento provisório de 007/DP-702 sem lógica de desempate | Const. III, XXIX; 007/DP-702 |
| D11 | "Você está respondendo sobre:" aparece em toda Seção, sem verificar quantas formações a Pessoa tem | Const. XXII |
| D12 | Nenhuma frase fixa qualifica a unidade (por exemplo, "campus"): "Cefor" é unidade e não campus | 007 FR-010; 008 FR-026 |
| D13 | O agradecimento fixo da confirmação só aparece quando a Versão não tem texto de encerramento | 008 FR-062 |
| D14 | A confirmação não oferece outra formação; a ligação para a trajetória basta | Const. XXII |
| D15 | Seção sem título usa o título da pesquisa como título principal; nenhum título é inventado | 008 FR-033; ID-13 é [V] |

### Notas técnicas para o plan (não vinculantes)

Soluções candidatas já verificadas ou recomendadas pelas auditorias. **Não são
requisitos**: o plan pode adotar outra solução equivalente, desde que cumpra os FRs e os
SCs correspondentes sem JavaScript e sem abstração nova.

- **N1 (FR-016, FR-017):** um primeiro botão de envio desabilitado e oculto no formulário
  da Seção impede o envio implícito a partir de campos de digitação no WebKit e no Blink
  (C5), sem entrar na ordem de foco nem na árvore de acessibilidade. Não cobre Enter com
  foco em rádio ou caixa no Blink (research R2, correção).
- **N2 (FR-019):** estender a área ativa do rótulo de cada Opção até cobrir a linha ou a
  célula inteira, só com estilo, sem mudar a marcação.
- **N3 (FR-020, FR-021):** escala em colunas com largura mínima fixa em px CSS (não
  proporcional à fonte), número abaixo do controle, quebrando em colunas alinhadas quando
  não couber.
- **N4 (FR-023):** expor como grupo de rádios só o conjunto das Opções, mantendo a caixa
  de remoção dentro da Pergunta e fora desse grupo.
- **N5 (FR-028):** o atributo de foco automático do HTML, num resumo tornado focável,
  atende "foco ao carregar" sem JavaScript; o efeito com leitores de tela é [T].
- **N6 (FR-008, FR-012):** decidir as mensagens de salvamento pelas Respostas atuais da
  Participação na Seção, já lidas pela jornada, e transmitir a saída de "Salvar e sair" à
  trajetória por um código de aviso de lista fechada, como o aviso de situação que já
  existe.
- **N7 (FR-045):** restringir as regras novas de estilo às telas da jornada e aos
  controles de Pergunta.

## Clarifications

### Session 2026-10-03

- Q: "Salvar e sair" substitui o link "Sair e continuar depois"? → A: Não. "Salvar e sair"
  entra como ação secundária; o link passa a se chamar "Sair sem salvar esta seção" e
  fica como ação terciária, de baixa ênfase, continuando navegação simples. Motivo: com
  erro de forma, "Salvar e sair" não conclui o envio, e a pessoa precisa de uma saída.
- Q: `autocomplete="off"` (MF-03) entra? → A: Não. MF-03 fica registrado e condicionado à
  validação em Safari/iOS e Android reais; nenhum outro mecanismo é adotado sem evidência.
- Q: O que acontece em "Salvar e sair" quando nenhuma Resposta foi gravada na Seção? → A:
  A pessoa sai normalmente para a trajetória; a interface não afirma que algo foi salvo e,
  se mostrar mensagem, ela é neutra e verdadeira. Sem estado, modelo ou mecanismo novo.

## User Scenarios & Testing *(mandatory)*

O ator é o **egresso** que responde à pesquisa, tipicamente no celular, podendo ser
interrompido. Na demonstração, são as Pessoas fictícias da 008 (Ana, Maria, Diego, Elisa).
As histórias são verificadas por testes automatizados por requisições HTTP comuns, sem
JavaScript, e por medição em viewport emulada; o comportamento em aparelho real é
validação posterior [T] (FR-050).

### User Story 1 - Salvar o que já respondi, mesmo sem terminar a Seção (Priority: P1)

A pessoa responde parte de uma Seção longa e quer guardar o que fez. Ela sabe, pela
própria tela, que pode salvar uma Seção incompleta; quando salva com perguntas
obrigatórias em branco, a tela mostra o que falta sem tratar isso como erro e só diz que
algo está salvo quando de fato está.

**Why this priority**: é o achado P0 da auditoria mobile (MF-01). O sistema já grava
Seção incompleta, mas ninguém diz isso e o resultado aparece como "Há problemas nesta
seção".

**Independent Test**: na Seção 2 de Ana, responder 3 de 8 perguntas e escolher "Salvar e
continuar"; conferir as 3 Respostas gravadas e a reapresentação como pendência. Repetir
sem responder nada e conferir que nenhuma frase afirma salvamento.

**Acceptance Scenarios**:

1. **Given** a tela de entrada de uma formação com pesquisa disponível, **When** é
   exibida, **Then** informa que é possível salvar a qualquer momento, mesmo sem terminar
   a Seção, e continuar depois.
2. **Given** uma Seção com 8 Perguntas, 7 obrigatórias, **When** a pessoa responde 3 e
   escolhe "Salvar e continuar", **Then** as 3 Respostas são gravadas e a mesma Seção é
   reapresentada com o resumo "Ainda faltam estas perguntas:", uma ligação para cada
   pendência e a frase de que o que foi respondido nesta Seção está salvo.
3. **Given** a reapresentação com pendências, **When** se lê o título da página, o título
   do resumo e a marcação de cada Pergunta pendente, **Then** nenhum deles usa o rótulo
   "Erro" nem "problemas".
4. **Given** uma Seção sem nenhuma Resposta gravada, **When** a pessoa envia sem
   responder nada, **Then** a reapresentação lista as pendências e **nenhuma** frase
   afirma que algo foi salvo.
5. **Given** uma Seção que, após o envio, não tem pendências, **When** a pessoa escolhe
   "Salvar e continuar", **Then** segue para o destino calculado pela 006, como hoje.

---

### User Story 2 - Interromper com segurança: quatro ações claras no fim da Seção (Priority: P1)

No fim de cada Seção, a pessoa vê quatro ações com hierarquia inequívoca: "Salvar e
continuar" (principal), "Salvar e sair" (secundária), "Voltar à seção anterior" e "Sair
sem salvar esta seção" (terciárias). Ao precisar parar, ela salva e sai com um toque e
sabe, sem mensagem falsa, se algo ficou salvo. Se houver erro de forma, ela corrige ou
sai sem salvar.

**Why this priority**: completa MF-01 para a interrupção voluntária e resolve MF-06 e
MF-14 (botão estreito; "Voltar", que descarta, a 19 px do botão principal).

**Independent Test**: na Seção 11 de Maria, marcar uma resposta e escolher "Salvar e
sair"; conferir a gravação, a chegada à trajetória com a mensagem de salvamento e, ao
entrar de novo, "Continuar a pesquisa" levando à Seção calculada pela 006. Repetir numa
Seção sem nenhuma marcação e conferir a mensagem neutra.

**Acceptance Scenarios**:

1. **Given** qualquer Seção de uma Participação em rascunho, **When** é exibida, **Then**
   o rodapé apresenta, nesta ordem, "Salvar e continuar" (ênfase principal), "Salvar e
   sair" (ênfase secundária) e, separadas dos botões e com baixa ênfase, "Voltar à seção
   anterior" (só quando houver Seção anterior no percurso) e "Sair sem salvar esta
   seção".
2. **Given** respostas marcadas e sem erro de forma, **When** a pessoa escolhe "Salvar e
   sair", **Then** as Respostas são gravadas pela mesma gravação de "Salvar e continuar",
   mesmo que restem pendências, e a pessoa chega à trajetória com a mensagem de que o que
   respondeu nesta Seção está salvo e de que pode continuar quando quiser.
3. **Given** uma Seção sem nenhuma Resposta gravada e nada marcado, **When** a pessoa
   escolhe "Salvar e sair", **Then** chega à trajetória sem que nada seja gravado, e a
   mensagem exibida (se houver) não afirma que algo foi salvo (exemplo: "Você pode
   continuar a pesquisa quando quiser.").
4. **Given** uma marcação com erro de forma (por exemplo, descrição de "Outro" sem a
   Opção "Outro" marcada), **When** a pessoa escolhe "Salvar e sair", **Then** nada é
   gravado, a mesma Seção é reapresentada com o erro, exatamente como em "Salvar e
   continuar", e "Sair sem salvar esta seção" continua disponível.
5. **Given** marcações não salvas, **When** a pessoa escolhe "Sair sem salvar esta
   seção", **Then** chega à trajetória sem nada gravado nesta Seção e sem mensagem de
   salvamento; o que já estava salvo antes continua guardado.
6. **Given** marcações não salvas, **When** a pessoa escolhe "Voltar à seção anterior",
   **Then** vai à Seção anterior do percurso sem gravar nada, como hoje.
7. **Given** uma tela de até 480 px CSS de largura, **When** o rodapé é exibido, **Then**
   os dois botões ocupam toda a largura útil da coluna e há pelo menos 32 px CSS entre a
   borda inferior do último botão e a primeira ação terciária.
8. **Given** a pessoa saiu com "Salvar e sair", **When** volta e escolhe "Continuar a
   pesquisa", **Then** chega à Seção atual calculada pela 006, com as Respostas
   gravadas.
9. **Given** um toque duplo ou um reenvio automático de "Salvar e sair", **When** os
   envios chegam ao servidor, **Then** nenhuma Resposta é duplicada e a mensagem de saída
   continua refletindo o que está gravado.

---

### User Story 3 - Digitar sem enviar a Seção por acidente (Priority: P1)

A pessoa digita o ano ou uma idade e toca na tecla de retorno do teclado ("Ir",
"Próximo", Enter). A Seção não é enviada; ela continua respondendo.

**Why this priority**: MF-02. Hoje, a primeira pergunta da Seção 3, respondida com
Enter, joga a pessoa ao topo com quatro "problemas" de perguntas que ela nem viu.

**Independent Test**: em navegador real, digitar e pressionar Enter nos campos de
digitação de uma Seção (texto curto e descrição de "Outro") e conferir que nada é enviado;
ativar os dois botões pelo teclado e conferir que enviam.

**Acceptance Scenarios**:

1. **Given** o foco num campo de texto curto da Seção (por exemplo, o ano), **When** a
   pessoa digita e pressiona Enter ("Ir"/"Próximo" no teclado virtual), **Then** nem
   "Salvar e continuar" nem "Salvar e sair" é acionado e nada é enviado.
2. **Given** o foco na descrição de "Outro" (ou em qualquer outro campo de digitação da
   Seção), **When** a pessoa digita e pressiona Enter, **Then** nada é enviado.
3. **Given** o foco em "Salvar e continuar" ou em "Salvar e sair", **When** a pessoa
   pressiona Enter ou Espaço, **Then** a ação correspondente é executada.
4. **Given** JavaScript desativado, **When** os cenários 1 a 3 são repetidos, **Then** o
   resultado é o mesmo.

*Correção de requisito após evidência de comportamento real do Chromium (2026-10-03):* a
versão anterior deste cenário exigia também que Enter com o foco num rádio ou numa caixa
de seleção não enviasse. No Chromium, com teclado físico, esse Enter pula o botão padrão
desabilitado e aciona o envio seguinte; não há solução só em HTML, e a feature não usa
JavaScript. Esse caso não é o achado MF-02 (tecla "Ir" do teclado virtual, que só existe em
campos de digitação), é comportamento anterior à 014 e fica registrado como limitação
conhecida ([research R2](research.md#r2--enterir-botão-de-envio-padrão-desabilitado);
quickstart §2.1).

---

### User Story 4 - Tocar e ler as opções com o dedo e com fonte ampliada (Priority: P1)

A pessoa toca em qualquer parte da linha de uma opção ou da célula de um ponto da escala,
e a opção é marcada. Com a fonte do sistema ampliada, a escala de 1 a 5 continua numa
linha, em ordem, sem o "5" isolado na linha de baixo. Leitores de tela continuam
encontrando o grupo de opções exclusivas, e a caixa "Deixar esta pergunta sem resposta"
deixa de ser apresentada como membro desse grupo.

**Why this priority**: MF-04 e MF-05 (P1 mobile), que mexem na mesma marcação que UX-19.
É **uma única correção** dos controles de escolha e escala; feitas em separado, se
contradiriam.

**Independent Test**: na Seção 8 (Avaliação) de Elisa, conferir por medição que toda a
área de cada célula e de cada linha ativa a opção, que a escala de 5 pontos fica numa
linha de 320 a 430 px com fonte de 100% a 200%, e que a estrutura acessível das
Perguntas de escolha única e de escala não inclui a caixa de remoção no grupo de rádios.

**Acceptance Scenarios**:

1. **Given** uma Pergunta de escala, **When** a pessoa toca em qualquer ponto da célula
   visual de um valor (acima, abaixo ou entre o controle e o número), **Then** esse valor
   é marcado.
2. **Given** uma Pergunta de escolha única ou múltipla, **When** a pessoa toca em
   qualquer ponto da linha visual de uma Opção, **Then** essa Opção é marcada (ou
   desmarcada, na múltipla).
3. **Given** uma escala de 1 a 5, **When** exibida de 320 a 430 px com fonte de 100%,
   115%, 130%, 150% e 200%, **Then** os cinco pontos ficam numa única linha, em ordem
   crescente da esquerda para a direita, igualmente espaçados, com o número junto ao seu
   controle e sem rolagem horizontal da página.
4. **Given** uma escala com mais pontos do que cabem na largura (por exemplo, de 0 a 10,
   criável pelo editor da 009), **When** exibida a 320 px, **Then** os pontos quebram em
   linhas alinhadas, com ordem de leitura preservada, sem rolagem horizontal da página.
5. **Given** uma Pergunta de escolha única ou escala não obrigatória, **When** examinada
   por tecnologia assistiva, **Then** o grupo de opções exclusivas contém só as Opções (ou
   pontos), a caixa "Deixar esta pergunta sem resposta" é um controle à parte da mesma
   Pergunta, e obrigatoriedade, invalidade e descrição da escala continuam expostas.

---

### User Story 5 - Saber em que Seção estou e sobre qual formação respondo (Priority: P2)

Ao avançar, a pessoa vê de imediato o nome da Seção nova como título principal e, logo
abaixo, uma linha que diz sobre qual formação está respondendo.

**Why this priority**: UX-07 (o topo de toda Seção é idêntico, com "Egresso Ifes" como
título) e ID-06 ("durante o curso" sem dizer qual curso, para quem tem várias
formações).

**Independent Test**: percorrer as Seções de Diego e conferir que o título principal de
cada uma é o título da Seção e que a linha de contexto começa por "Você está respondendo
sobre:".

**Acceptance Scenarios**:

1. **Given** uma Seção com título, **When** exibida, **Then** o título principal da
   página é o título da Seção, e o título da pesquisa não é o título principal.
2. **Given** uma Seção sem título na Versão, **When** exibida, **Then** o título
   principal é o título da pesquisa (ou "Pesquisa", se também não houver), sem título
   inventado, e o título da aba continua distinto das demais telas.
3. **Given** qualquer Pessoa, com uma ou várias formações, **When** uma Seção é exibida,
   **Then** a linha de contexto diz "Você está respondendo sobre:" seguida da linha da
   formação, separada das Perguntas como informação institucional.
4. **Given** a tela de conclusão, **When** exibida, **Then** o título principal é
   "Concluir a pesquisa".

---

### User Story 6 - Ver minha trajetória no Ifes e escolher a formação (Priority: P2)

A tela inicial apresenta as formações da pessoa como **trajetória no Ifes**, de forma
compacta, e a entrada parte do fato que o Ifes já conhece ("Você concluiu …"). Quando há
mais de uma formação com pesquisa, a escolha cabe na primeira tela e não parece uma lista
de pendências.

**Why this priority**: ID-03, ID-04, ID-11, ID-12, ID-14 e o resto de UX-17. É o que mais
muda a sensação de "o Ifes conhece parte da sua história" sem depender de decisão
institucional.

**Independent Test**: abrir a tela de Ana (uma formação), Maria (duas, escolha) e Diego
(três, depois de concluir); conferir título, frase de entrada, linhas por formação,
situações mostradas e ordem.

**Acceptance Scenarios**:

1. **Given** qualquer Pessoa de demonstração, **When** a tela de formações é exibida,
   **Then** o título principal é "Sua trajetória no Ifes".
2. **Given** uma única formação com entrada pendente (Ana), **When** a tela é exibida,
   **Then** começa por uma frase com a formação como fato (por exemplo, "Você concluiu
   Tecnologia em Análise e Desenvolvimento de Sistemas · Serra · 2022"), seguida de que o
   Ifes quer saber como a trajetória seguiu, da frase sobre salvar a qualquer momento e da
   ação única "Iniciar a pesquisa" ou "Continuar a pesquisa".
3. **Given** uma formação cuja fonte não informa curso, unidade ou ano, **When** a frase
   de entrada é composta, **Then** usa só os atributos informados, sem frase truncada, sem
   valor padrão e sem qualificar a unidade (nenhum "campus" fixo).
4. **Given** duas formações com entrada pendente (Maria), **When** a tela é exibida,
   **Then** uma frase explica que cada formação tem sua própria pesquisa e pede a escolha,
   sem contar formações; cada formação aparece em linhas compactas com sua ação, na ordem
   devolvida pela 007, sem destaque nem pré-seleção.
5. **Given** formações sem pesquisa (Diego), **When** a tela é exibida, **Then** essas
   formações aparecem na trajetória sem a frase "Sem pesquisa disponível no momento", e a
   situação geral da tela continua informada uma vez.
6. **Given** uma formação em ambiguidade operacional, **When** a tela é exibida, **Then**
   a formação continua mostrando que a pesquisa referente a ela não está disponível neste
   momento (007/DP-701).
7. **Given** formações já respondidas ou em andamento, **When** a tela é exibida,
   **Then** "Pesquisa já respondida" e "Pesquisa em andamento" continuam visíveis na
   formação correspondente.
8. **Given** qualquer Pessoa, **When** a ordem das formações na tela é comparada com a da
   007, **Then** é idêntica, e nenhum texto a qualifica como cronológica, principal ou
   mais recente.
9. **Given** "Data de conclusão" informada numa formação e "Ano de conclusão" noutra
   (Maria), **When** a trajetória é exibida, **Then** as duas aparecem só com o ano.

---

### User Story 7 - Erros e pendências encontráveis por quem usa leitor de tela (Priority: P2)

Quando a Seção volta com erros ou pendências, o resumo no topo recebe o foco ao carregar,
além de continuar anunciado, e cada item leva à Pergunta correspondente.

**Why this priority**: MF-10. A 008 FR-076 aceita "anunciado **ou** foco"; no celular, o
anúncio não é garantido.

**Independent Test**: reapresentar a Seção com pendência e com erro de forma e conferir
que o resumo é o elemento que recebe o foco no carregamento, sem JavaScript.

**Acceptance Scenarios**:

1. **Given** uma reapresentação com pendências ou com erros de forma, **When** a página
   carrega, **Then** o foco está no resumo, e o resumo continua anunciável a tecnologias
   assistivas.
2. **Given** o resumo, **When** a pessoa ativa um item, **Then** chega à Pergunta
   correspondente.

---

### User Story 8 - Encerramento que fecha a conversa, não o formulário (Priority: P3)

Ao concluir, a pessoa lê que suas respostas sobre aquela formação foram registradas, com
um único agradecimento.

**Why this priority**: ID-09 e UX-18 (agradecimento em dobro, "Este formulário chegou ao
fim!").

**Independent Test**: concluir a pesquisa de Diego e conferir a frase de registro com o
curso e a ocorrência única do agradecimento.

**Acceptance Scenarios**:

1. **Given** uma Participação concluída numa formação com curso informado, **When** a
   confirmação é exibida, **Then** diz que as respostas sobre aquele curso foram
   registradas.
2. **Given** curso não informado, **When** a confirmação é exibida, **Then** diz que as
   respostas foram registradas, sem curso e sem texto fabricado.
3. **Given** uma Versão com texto de encerramento, **When** a confirmação é exibida,
   **Then** o agradecimento fixo da interface não aparece, e o texto da Versão aparece
   exatamente como na Versão.
4. **Given** uma Versão sem texto de encerramento, **When** a confirmação é exibida,
   **Then** o agradecimento fixo aparece uma vez.
5. **Given** a confirmação, **When** a pessoa quer voltar, **Then** encontra a ligação
   para a trajetória e nenhuma outra ação (sem oferecer outra formação, comprovante ou
   edição).

---

### User Story 9 - Pequenos alvos e uma instrução que não faz perder respostas (Priority: P3)

As ligações da tela de conclusão têm área de toque adequada, e a página de falha de
confirmação de envio não manda recarregar.

**Why this priority**: MF-13 e MF-09, refinamentos P2 baratos nos mesmos arquivos.

**Independent Test**: medir as ligações da tela de conclusão; ler a página de falha de
confirmação de envio.

**Acceptance Scenarios**:

1. **Given** a tela "Concluir a pesquisa" a 375 px, **When** as ligações para revisar
   Seções são medidas, **Then** cada uma tem área de toque de pelo menos 44 px CSS de
   altura, sem sobreposição com a vizinha.
2. **Given** a falha de confirmação de envio, **When** a página é exibida, **Then**
   orienta a voltar à página anterior e enviar novamente, sem mencionar recarregar.

---

### User Story 10 - Telas institucionais sem regressão (Priority: P2)

Quem usa o editor (009), o acompanhamento (011) ou a demonstração não percebe nenhuma
mudança, exceto a prévia de Seção do editor, que mostra os controles como o egresso os
verá.

**Why this priority**: a folha de estilo e os controles de Pergunta são compartilhados
(C9). Um polish da jornada não pode virar regressão administrativa.

**Independent Test**: suítes automatizadas da 009, da 011 e da demonstração passam;
comparação visual das telas listadas em SC-014.

**Acceptance Scenarios**:

1. **Given** as telas do editor, do acompanhamento e da demonstração, **When** exibidas
   antes e depois desta feature, **Then** botões, listas, campos e caixas de seleção têm a
   mesma aparência e comportamento.
2. **Given** a prévia de uma Seção no editor, **When** exibida, **Then** os controles de
   escolha e escala têm a mesma forma e área de toque da jornada do egresso.

### Edge Cases

- **Seção só com Perguntas opcionais, nada respondido, "Salvar e continuar"**: segue ao
  destino da 006 (a Seção está satisfeita), sem frase de salvamento.
- **Mesma Seção, "Salvar e sair"**: sai para a trajetória com a mensagem neutra (FR-012).
- **Todas as Respostas da Seção removidas com "Deixar esta pergunta sem resposta" e
  "Salvar e sair"**: a remoção é gravada; como não resta Resposta na Seção, a mensagem é
  a neutra.
- **Seção com Respostas gravadas antes e nada mudado agora, "Salvar e sair"**: a mensagem
  de salvamento é verdadeira (o que foi respondido nesta Seção está salvo).
- **"Salvar e sair" numa Seção que muda o percurso** (Q33, Q46): grava; na volta, a 006
  calcula a Seção atual, como em qualquer retomada.
- **"Salvar e sair" na Seção cujo destino é a finalização** (inclusive Q1 = "Não"):
  grava e sai; na volta, a jornada leva à tela de conclusão (008 FR-052).
- **Rejeição da 005 numa Pergunta**: tratada como erro de forma, nas duas ações de envio.
- **Enter num campo de descrição de "Outro"**: não envia.
- **Enter com foco num rádio ou numa caixa (teclado físico)**: fora de FR-016. No
  Chromium pode enviar, como antes da 014; Espaço é a interação convencional para marcar.
  Limitação conhecida, sem JavaScript.
- **Pendência vinda da tela de conclusão** (a jornada deixou de estar finalizada): mesma
  apresentação de pendência, com a regra de verdade de FR-008.
- **Voltar do navegador depois de "Salvar e sair"**: a restauração do navegador não é
  alterada (MF-03 fora).
- **Seção sem título**: título principal com o título da pesquisa; título da aba com a
  regra atual, para continuar único.
- **Formação sem nenhum atributo**: linha neutra existente ("Dados da formação não
  informados pela fonte."); frase de entrada sem atributos e sem texto fabricado.
- **Duas formações com a mesma linha principal**: a linha complementar mostra os
  atributos informados que existirem; se nada as distinguir, continuam distintas pela
  posição na lista e pela ação própria, sem rótulo fabricado (007/DP-702).
- **Pessoa sem nenhuma formação**: título "Sua trajetória no Ifes" com a mensagem atual
  de que não foram encontradas formações.
- **Escala com rótulo de extremidade ausente** (DP-301): continua sem rótulo inventado.
- **Fonte ampliada a 200% em 320 px com a marca de erro na Pergunta**: a escala de 5
  pontos continua numa linha.
- **Orientação horizontal**: sem requisito novo além da ausência de rolagem horizontal.

## Requirements *(mandatory)*

Cada requisito indica a origem entre colchetes: achado de auditoria (**UX-nn**,
**ID-nn**, **MF-nn**), **[008 FR-nnn]** quando revisa ou preserva requisito da 008,
**[Const.]**, **[Solicitante]**, **[Hipótese]** ou DP.

### Matriz de comportamento do rodapé

Destino e mensagem de cada ação por estado da Seção no momento do envio. "Atual" =
comportamento da 008, inalterado. Nenhuma célula cria mecanismo novo.

| Estado no envio | Salvar e continuar | Salvar e sair | Voltar à seção anterior | Sair sem salvar esta seção |
|---|---|---|---|---|
| **Envio completo** (sem pendências) | Grava; destino da 006 (Seção seguinte ou conclusão) | Grava; trajetória com mensagem de salvamento se houver Resposta gravada na Seção, senão neutra | Seção anterior, nada gravado | Trajetória, nada gravado, sem mensagem |
| **Envio incompleto com respostas válidas** | Grava; mesma Seção com pendências e frase de salvamento | Grava; trajetória com mensagem de salvamento | Idem | Idem |
| **Envio sem nenhuma Resposta** (nem antes, nem agora) | Nada a gravar; mesma Seção com pendências, **sem** frase de salvamento (ou destino da 006, se não houver obrigatória) | Nada a gravar; trajetória com mensagem **neutra**, sem afirmar salvamento | Idem | Idem |
| **Erro de forma** (ou rejeição da 005) | Nada gravado; mesma Seção com os valores enviados e os erros | Igual a "Salvar e continuar" | Disponível na reapresentação | Disponível na reapresentação |
| **Seção fora do percurso** | Nada gravado; Seção atual com aviso de percurso (atual) | Igual a "Salvar e continuar" | Navegação; a Seção pedida segue a regra atual de percurso | Trajetória |
| **Coleta encerrada** | Nada gravado; tela "período encerrado", com respostas anteriores preservadas (atual) | Igual a "Salvar e continuar" | Navegação; leva à tela "período encerrado" (atual) | Trajetória |
| **Participação concluída** | Nada gravado; tela "já respondida" (atual) | Igual a "Salvar e continuar" | Navegação; leva a "já respondida" (atual) | Trajetória |
| **Toque ou reenvio repetido** | Sem duplicidade (C15); mesmo destino | Sem duplicidade (C15); mesmo destino, mensagem conforme o que está gravado | — (navegação) | — (navegação) |

### Functional Requirements

**Seção incompleta, pendências e erros de forma (MF-01, UX-13)**

- **FR-001**: Uma Seção DEVE poder ser salva **incompleta**: todo envio aceito grava o que
  foi respondido, mesmo com Perguntas obrigatórias em branco. É o comportamento atual (C2)
  e passa a ser requisito explícito, sem mecanismo novo de gravação. [MF-01; 005;
  008 FR-040, FR-050]
- **FR-002**: A tela de entrada DEVE informar, em linguagem simples, que é possível
  salvar a qualquer momento, mesmo sem terminar a Seção, e continuar depois. [MF-01;
  UX-08]
- **FR-003**: **Pendência** é uma Pergunta obrigatória do percurso sem Resposta, indicada
  pela 006, depois de um envio **aceito**. A pendência NÃO DEVE ser apresentada como erro.
  [MF-01; 008 FR-053]
- **FR-004**: **Erro de forma** é a recusa de um envio antes de gravar: valor que não
  corresponde à Pergunta, descrição de "Outro" sem a Opção marcada, ou rejeição de uma
  Pergunta pela 005. Com erro de forma, **nada** daquele envio é gravado (008 FR-045), a
  Seção é reapresentada com os valores enviados e a apresentação de erro atual é mantida
  (resumo de erros, rótulo de erro por Pergunta, indicação de erro no título da página).
  Pendências e erros de forma NÃO DEVEM aparecer na mesma reapresentação (C3). [008
  FR-044, FR-045, FR-049, FR-070]
- **FR-005**: Na reapresentação com pendências, o título do resumo DEVE anunciar o que
  falta sem usar "Erro" nem "problemas" (exemplo: "Ainda faltam estas perguntas:").
  [MF-01]
- **FR-006**: Na reapresentação com pendências, cada Pergunta pendente DEVE ser indicada
  por texto (exemplo: "Falta responder: esta pergunta é obrigatória."), sem o rótulo de
  erro, sem depender só de cor e associada à Pergunta para tecnologias assistivas. [MF-01;
  008 FR-038, FR-073, FR-075]
- **FR-007**: O título da página (aba) DEVE indicar **erro** só quando houver erro de
  forma; com pendências, DEVE indicá-las com texto distinto de erro. Revisa a 008 FR-071.
  [MF-01; 008 FR-071]
- **FR-008**: **Regra de verdade das mensagens de salvamento.** Qualquer frase que
  afirme que respostas estão salvas (na reapresentação com pendências e na saída por
  "Salvar e sair") DEVE aparecer **somente** quando a Seção apresentada ou enviada tiver ao
  menos uma Resposta gravada depois do envio, segundo o que está gravado. Sem Resposta
  gravada na Seção, NENHUMA frase DEVE afirmar ou sugerir salvamento. A regra NÃO DEVE
  depender de estado, modelo ou registro novos. [UX-13; Solicitante]

**Ações do rodapé da Seção (MF-01, MF-06, MF-14, UX-04)**

- **FR-009**: Toda Seção de Participação em rascunho DEVE apresentar, nesta ordem visual e
  de navegação por teclado, quatro ações com hierarquia inequívoca:
  1. **"Salvar e continuar"** — ação **principal**, de envio;
  2. **"Salvar e sair"** — ação **secundária**, de envio, com ênfase visual menor que a
     principal;
  3. **"Voltar à seção anterior"** — ação **terciária**, de navegação, só quando houver
     Seção anterior no percurso determinado (008 FR-054);
  4. **"Sair sem salvar esta seção"** — ação **terciária**, de navegação.
  O comportamento de cada ação em cada estado é o da Matriz de comportamento do rodapé.
  [Solicitante; MF-06; MF-14]
- **FR-010**: **"Salvar e continuar"** DEVE manter o comportamento atual: erro de forma →
  reapresenta a Seção com o erro, nada gravado; envio aceito com pendências →
  reapresenta a Seção com pendências (FR-005, FR-008); envio aceito sem pendências →
  segue ao destino calculado pela 006 (Seção seguinte ou conclusão). [008 FR-049,
  FR-050]
- **FR-011**: **"Salvar e sair"** DEVE usar exatamente a mesma validação e a mesma
  gravação de "Salvar e continuar" (008 FR-040 a FR-048) e diferir só no destino de um
  envio aceito, que é sempre a trajetória (FR-012), com ou sem pendências e qualquer que
  seja o destino calculado pela 006. Com erro de forma, Seção fora do percurso, coleta
  encerrada ou Participação concluída, DEVE se comportar exatamente como "Salvar e
  continuar". Envios repetidos (toque duplo, reenvio do navegador) NÃO DEVEM duplicar
  Respostas nem produzir mensagem incoerente com o que está gravado; a garantia é a da
  gravação existente (C15). Revisa a 008 FR-049 e FR-050 só para esta ação.
  [Solicitante; MF-01; UX-04]
- **FR-012**: A chegada à trajetória por "Salvar e sair" DEVE exibir uma mensagem
  conforme FR-008: com Resposta gravada na Seção, que o que a pessoa respondeu nesta
  Seção está salvo e que pode continuar quando quiser (exemplo: "O que você respondeu
  nesta seção está salvo. Você pode continuar a pesquisa quando quiser."); sem Resposta
  gravada, uma mensagem neutra e verdadeira (exemplo: "Você pode continuar a pesquisa
  quando quiser."). A mensagem só aparece nessa chegada, e o endereço NÃO DEVE conter
  dado pessoal, valor declarado ou nome de Seção. O aviso atual de mudança de situação
  continua existindo. [Solicitante; MF-01; 008 FR-085, FR-086]
- **FR-013**: **"Sair sem salvar esta seção"** DEVE ser navegação simples para a
  trajetória: NÃO DEVE gravar, enviar formulário, exibir mensagem de salvamento nem criar
  mecanismo novo. DEVE estar disponível em toda Seção, inclusive na reapresentação com
  erro de forma. PODE ter nota curta de que o que foi salvo antes continua guardado.
  Substitui o rótulo "Sair e continuar depois". [Solicitante; UX-04]
- **FR-014**: **"Voltar à seção anterior"** DEVE manter o comportamento atual (navegação
  simples, sem gravar) e a nota de que alterações não salvas nesta página serão
  descartadas. [008 FR-054]
- **FR-015**: As ações terciárias DEVEM ser visualmente separadas dos botões, por
  distância e por divisor visível, com pelo menos 32 px CSS entre a borda inferior do
  último botão e a primeira ação terciária, e com ênfase menor que a dos dois botões. Em
  telas de até 480 px CSS de largura, os dois botões DEVEM ocupar toda a largura útil da
  coluna. [MF-06; MF-14]

**Envio implícito (MF-02)**

- **FR-016**: Em toda tela de Seção, digitar num **campo de digitação** (texto curto,
  descrição de "Outro" e qualquer campo textual equivalente) e pressionar Enter (ou a
  tecla de retorno do teclado virtual, "Ir"/"Próximo") NÃO DEVE acionar **nenhuma** ação
  de envio, nem "Salvar e continuar" nem "Salvar e sair": digitar e confirmar a digitação
  não pode enviar a Seção prematuramente. [MF-02] *(Corrigido após evidência de
  comportamento real do Chromium: Enter com o foco num rádio ou numa caixa de seleção fica
  fora deste requisito; ver US3 e research R2.)*
- **FR-017**: FR-016 DEVE ser atendido sem JavaScript e sem prejudicar a operação por
  teclado: com o foco num botão, Enter e Espaço continuam acionando-o, e a ordem de foco e
  o que é exposto a tecnologias assistivas não ganham elemento novo perceptível. [008
  FR-074, FR-080]

**Controles de escolha e escala — correção única (MF-04 + MF-05 + UX-19)**

- **FR-018**: MF-04, MF-05 e UX-19 DEVEM ser tratados como **uma única correção** dos
  controles de escolha única em rádios, escolha múltipla e escala, aplicada de forma
  genérica pelo tipo do controle, sem tratamento por Pergunta, Seção ou Opção (008
  FR-034), sem elemento interativo novo, sem alterar o que o formulário envia e sem
  alterar texto, ordem, significado, obrigatoriedade ou rótulos da Versão (008 FR-033).
  [MF-04; MF-05; UX-19; Const. XXIII]
- **FR-019**: Toda a área visual de cada Opção (a linha inteira, nos rádios e nas caixas)
  e de cada ponto da escala (a célula inteira) DEVE ativar o controle correspondente, com
  área ativável de pelo menos 44×44 px CSS. Vale também para a caixa "Deixar esta pergunta
  sem resposta". [MF-04; 008 research R14]
- **FR-020**: Na escala, os pontos DEVEM aparecer em ordem crescente da esquerda para a
  direita, igualmente espaçados, com o número de cada ponto visualmente junto ao seu
  controle. [MF-05; 008 FR-035]
- **FR-021**: A escala DEVE ficar numa única linha sempre que os pontos couberem com a
  área de FR-019; em particular, a escala de 1 a 5 DEVE ficar numa linha de 320 a 430 px
  CSS com fonte de 100% a 200%. Quando os pontos não couberem (escalas longas permitidas
  pela 009), DEVEM quebrar em linhas alinhadas, com a ordem de leitura preservada. Em
  nenhum caso DEVE haver rolagem horizontal da página. Revisa a 008 FR-077 quanto à forma
  da escala. [MF-05; 008 FR-077]
- **FR-022**: Nas Perguntas de escolha única em rádios e de escala, o grupo exposto a
  tecnologias assistivas como grupo de opções exclusivas DEVE conter **somente** as
  Opções (ou pontos). A caixa "Deixar esta pergunta sem resposta" DEVE continuar dentro da
  Pergunta, associada a ela, mas fora desse grupo. Obrigatoriedade, indicação de erro e
  descrição da escala DEVEM continuar expostas. [UX-19; 008 FR-038, FR-043, FR-072,
  FR-073]

**Títulos e contexto (UX-07, UX-11, ID-06, MF-13)**

- **FR-023**: O título principal de cada tela de Seção DEVE ser o título da Seção; sem
  título na Versão, o título da pesquisa (ou "Pesquisa"), sem título inventado. O título
  da pesquisa NÃO DEVE ser o título principal de uma Seção que tenha título. O título
  principal da tela de conclusão DEVE ser "Concluir a pesquisa". O título da página (aba)
  mantém a regra atual, inclusive para Seção sem título, para continuar único por tela.
  Revisa a 008 FR-032 quanto à hierarquia. [UX-07; UX-11; 008 FR-032, FR-033, FR-071]
- **FR-024**: A ordem do topo da Seção DEVE ser: aviso (quando houver), título principal,
  resumo de erros ou pendências (quando houver), linha de contexto da formação, texto de
  abertura da Versão (só na primeira Seção), texto da Seção, Perguntas. [UX-07; MF-10]
- **FR-025**: A linha de contexto nas Seções DEVE começar por "Você está respondendo
  sobre:" seguida da linha da formação (FR-034), para toda Pessoa, qualquer que seja a
  quantidade de formações, separada das Perguntas como informação institucional. [ID-06;
  008 FR-027]
- **FR-026**: As ligações da tela de conclusão para revisar Seções DEVEM ter área de toque
  de pelo menos 44 px CSS de altura cada, sem sobreposição. [MF-13]

**Resumo e falha de envio (MF-10, MF-09)**

- **FR-027**: Ao reapresentar uma Seção com pendências ou com erros de forma, o resumo
  DEVE ficar no topo do conteúdo (FR-024), ter uma ligação para cada Pergunta afetada,
  **receber o foco ao carregar a página**, sem JavaScript, e continuar anunciável a
  tecnologias assistivas. O foco no resumo NÃO DEVE abrir teclado virtual nem deslocar a
  página para além do topo do conteúdo. Revisa a 008 FR-076 ("anunciado **ou** foco") para
  "foco **e** anúncio". [MF-10; UX-01; UX-12; 008 FR-049, FR-076]
- **FR-028**: O efeito de FR-027 em VoiceOver e TalkBack é validação posterior [T]
  (FR-050); a implementação NÃO DEVE remover o anúncio atual do resumo enquanto essa
  validação não ocorrer. [MF-10]
- **FR-029**: A página de falha de confirmação de envio DEVE orientar a voltar à página
  anterior e enviar novamente, e NÃO DEVE mandar recarregar a página. [MF-09]

**Trajetória e formações (ID-03, ID-04, ID-11, ID-12, ID-14, UX-17)**

- **FR-030**: A tela de formações DEVE ter como título principal "Sua trajetória no Ifes"
  em todas as situações de entrada (entrada resolvida, seleção necessária, sem entrada
  pendente, sem pesquisa, sem formação). As ligações que levam a ela DEVEM usar rótulo
  coerente (exemplo: "Ver sua trajetória no Ifes"). [ID-03]
- **FR-031**: **Entrada resolvida**: a tela DEVE abrir com uma frase que apresente a
  formação pendente como fato já conhecido pelo Ifes, seguida de que o Ifes quer saber
  como a trajetória seguiu, da frase de FR-002 e da ação única ("Iniciar a pesquisa" ou
  "Continuar a pesquisa"). Revisa a 008 FR-020 quanto ao texto. [ID-04; 008 FR-020]
- **FR-032**: A frase de FR-031 DEVE usar **somente** os atributos informados pela fonte;
  NÃO DEVE ficar truncada quando faltar atributo, usar valor padrão, deduzir atributo nem
  qualificar a unidade com palavra fixa (por exemplo, "campus"). Sem nenhum atributo
  informado, DEVE usar texto neutro. [ID-04; 007 FR-009, FR-010; 008 FR-026]
- **FR-033**: **Seleção necessária**: a tela DEVE explicar que cada formação tem sua
  própria pesquisa e pedir a escolha por qual começar ou continuar, informando que as
  outras continuam disponíveis, **sem contar** formações. Cada formação com entrada
  pendente DEVE aparecer na forma compacta de FR-034, com sua situação e sua ação, na
  ordem devolvida pela 007, sem destaque, pré-seleção, sugestão ou ranking. Revisa a 008
  FR-021 (de "perguntar" para "pedir a escolha"). [ID-14; UX-17; 008 FR-021; 007 FR-021]
- **FR-034**: Cada formação DEVE ser apresentada na forma compacta: uma **linha
  principal** com curso · unidade · ano de conclusão (só os informados; o ano é usado
  mesmo quando a fonte informa a data) e, quando informados, uma **linha complementar**
  com nível · modalidade · forma de oferta. Substitui a ficha de rótulos e valores na tela
  de formações. A linha principal DEVE ser a mesma do contexto das Seções e da entrada de
  demonstração, sem mudar o formato desta. Atributo não informado é omitido; sem nenhum,
  o texto neutro existente. [ID-03; ID-12; 008 FR-025, FR-026]
- **FR-035**: As formações DEVEM aparecer **na ordem devolvida pela 007**. A interface NÃO
  DEVE reordenar formações, descrever a ordem como cronológica, principal, atual ou mais
  recente, inferir fatos não informados (por exemplo, período de estudo, ingresso,
  continuidade ou "verticalização"), alterar regra da 007, nem usar linha do tempo
  gráfica, setas, selos, percentuais ou comparação com outras pessoas. [ID-03; 007
  FR-011, FR-021; 008 FR-095; Const. III, XXIX]
- **FR-036**: Por formação, a situação DEVE ser mostrada para "pesquisa já respondida",
  "pesquisa em andamento", "disponível para responder" (estas duas com sua ação) e
  **ambiguidade operacional**, com o texto atual. A frase "sem pesquisa disponível no
  momento" NÃO DEVE ser repetida por formação; a situação geral da tela (sem pesquisa, sem
  entrada pendente, sem formação) continua informada **uma vez**. Revisa a 008 FR-023.
  [ID-11; 008 FR-022, FR-023]
- **FR-037**: A ambiguidade operacional NÃO DEVE ser escondida, renomeada ou explicada
  além do texto atual, que é o tratamento provisório do 007/DP-701. NENHUMA Campanha DEVE
  ser nomeada, contada ou descrita. [007/DP-701; 008 FR-023, FR-024]

**Encerramento (ID-09, UX-18)**

- **FR-038**: A confirmação DEVE manter o título "Pesquisa concluída" e dizer que as
  respostas sobre o curso daquela formação foram registradas (exemplo: "Suas respostas
  sobre Licenciatura em Química foram registradas."). Sem curso informado, DEVE dizer que
  as respostas foram registradas, sem texto fabricado. [ID-09; 008 FR-062]
- **FR-039**: A confirmação NÃO DEVE afirmar finalidade, uso futuro, novo contato ou
  periodicidade. [ID-09; Const. IX; 005/DP-504]
- **FR-040**: O agradecimento fixo da interface DEVE aparecer **somente** quando a Versão
  não tiver texto de encerramento; havendo, o texto da Versão é o agradecimento, exibido
  exatamente como na Versão. Revisa a 008 FR-062 quanto ao agradecimento. [UX-18; 008
  FR-062, FR-033]
- **FR-041**: A confirmação NÃO DEVE oferecer outra formação nem qualquer ação além da
  ligação para a trajetória, e continua sem resumo, comprovante ou edição. [ID-09; 008
  FR-063]

**Fronteiras e preservações**

- **FR-042**: Esta feature NÃO DEVE criar modelo, tabela, coluna ou migração, NÃO DEVE
  persistir nada além das Respostas gravadas pelas operações existentes da 005, e NÃO DEVE
  persistir sessão de jornada, posição, rascunho não enviado ou registro de acesso. [008
  FR-091; Const. XXII]
- **FR-043**: Toda a jornada DEVE continuar funcionando com JavaScript desativado, e esta
  feature NÃO DEVE adicionar JavaScript. NÃO DEVEM ser introduzidos autosave,
  armazenamento local no navegador, aviso ao sair da página, aplicativo instalável,
  trabalho em segundo plano do navegador, modo offline, wizard, indicador de progresso ou
  estimativa de tempo. [008 FR-079, FR-080, FR-095, FR-096]
- **FR-044**: NÃO DEVE ser criada abstração genérica de componentes, motor de formulário
  ou sistema de design; as mudanças DEVEM se limitar aos templates, à folha de estilo, aos
  textos fixos e à camada de apresentação existentes. [008 FR-096; Const. XXII, XXIII]
- **FR-045**: As mudanças de estilo DEVEM se aplicar só às telas da jornada do egresso e
  aos controles de Pergunta. NÃO DEVEM alterar a aparência nem o comportamento das telas
  do editor (009), do acompanhamento (011) e da demonstração (entrada e operador), exceto
  a prévia de Seção do editor, que DEVE refletir os controles da jornada. [C9]
- **FR-046**: Esta feature NÃO DEVE alterar textos, ordem, obrigatoriedade, tipos, rótulos
  de escala ou regras de navegação da Versão, nem modelos, operações ou contratos das
  Features 001 a 013. [Const. XIII; 008 FR-092]
- **FR-047**: Esta feature NÃO DEVE desativar nem alterar a restauração de formulário pelo
  navegador ao voltar no histórico (MF-03), nem adotar outro mecanismo para isso.
  [Solicitante; MF-03]
- **FR-048**: Todos os textos fixos citados nesta spec são exemplos funcionais e
  provisórios sob 008/DP-801, revisáveis sem mudança de comportamento, desde que respeitem
  FR-008. [DP-801]

**Fechamento**

- **FR-049**: O fechamento da feature DEVE exigir testes automatizados, por requisições
  HTTP comuns e sem JavaScript, que cubram as histórias 1 a 8 e todas as células da Matriz
  de comportamento do rodapé, e a continuidade dos cenários ponta a ponta E2E-1 a E2E-4 e
  do verificador de acessibilidade da 008, ajustados só onde o texto ou a marcação mudaram
  de propósito. As medidas de tela e o comportamento de Enter são verificados conforme os
  métodos indicados nos Success Criteria. [Const. XXVI; 008 FR-097, FR-098]
- **FR-050**: A validação em aparelho real é **posterior** ao fechamento e NÃO o bloqueia.
  DEVE ficar registrada como roteiro, a partir da seção 15 da auditoria mobile, num iPhone
  com Safari e num Android com Chrome: (1) interrupção e retorno numa Seção longa; (3)
  tecla de retorno num campo de texto, inclusive o rótulo exibido; (5) toque com o polegar
  nas áreas de FR-019; (9) fonte do sistema ampliada na escala; (4) cenário do MF-03, só
  como insumo para decisão futura; e, quando houver aparelho, (7) VoiceOver e (8)
  TalkBack para FR-022 e FR-027. [MF-01; MF-02; MF-03; MF-04; MF-05; MF-10]

### Key Entities *(include if feature involves data)*

Nenhuma entidade nova. A feature só apresenta entidades existentes:

- **Conclusão Acadêmica** (001): fonte da linha da formação e da frase de entrada
  (institucional).
- **Participação em Pesquisa** e **Resposta** (005, 006): gravadas exclusivamente pelas
  operações existentes, também por "Salvar e sair" (declarado).
- **Versão da Pesquisa** (002): títulos de Seção, título da pesquisa, textos de abertura e
  encerramento, exibidos sem alteração.
- **Situação de entrada e situação de cada formação** (007): consumidas como estão, na
  ordem devolvida.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem (institucional / derivado / declarado) | Fonte ou regra de derivação | Tratamento de divergência |
|------|-----------------------------------------------|-----------------------------|---------------------------|
| Curso, unidade, nível, modalidade, forma de oferta | Institucional | Conclusão Acadêmica (001) | Exibidos, nunca gravados como Resposta nem usados para pré-preencher (008 FR-028) |
| Ano de conclusão na linha da formação | Institucional | Ano informado; com data, o ano da data (já garantido pela 001) | Nenhuma: a 001 exige ano coerente com a data |
| Situação de cada formação e ordem | Derivado pela 007 | Situação de entrada da 007 | Exibida como devolvida; nenhuma reclassificação |
| Pendências | Derivado pela 006 | Perguntas obrigatórias do percurso sem Resposta | Exibidas exatamente como a 006 indica (008 FR-053) |
| "Há Resposta gravada nesta Seção" (FR-008) | Derivado | Respostas atuais da Participação na Seção | — |
| Respostas | Declarado | Egresso, gravadas pela 005 | Divergência com o contexto continua tratada na análise (ADR 0003) |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das reapresentações com pendências, 0 ocorrências de "Erro" ou
  "problemas" no título da página, no resumo e nas Perguntas pendentes; em 100% das
  reapresentações com erro de forma, a indicação de erro continua presente. Verificado
  por teste automatizado.
- **SC-002**: Em 100% das telas e mensagens em que a Seção não tem Resposta gravada, 0
  frases afirmam ou sugerem salvamento; em 100% das que têm, a frase de salvamento está
  presente. Verificado por teste automatizado, nos estados "envio incompleto", "envio sem
  nenhuma Resposta", "Seção opcional vazia" e "Respostas removidas".
- **SC-003**: Em 100% dos envios por "Salvar e sair" sem erro de forma, as Respostas
  gravadas são exatamente as marcadas (inclusive com Seção incompleta) e a pessoa chega à
  trajetória; em 100% dos envios com erro de forma, 0 Respostas são gravadas e a Seção é
  reapresentada. Verificado por teste automatizado.
- **SC-004**: Em 100% das telas de Seção, "Sair sem salvar esta seção" está presente,
  inclusive na reapresentação com erro de forma, e usá-la grava 0 Respostas. Verificado
  por teste automatizado.
- **SC-005**: Nas Seções da Versão de referência, Enter/"Ir" num campo de digitação
  (texto curto e descrição de "Outro") produz 0 envios implícitos, e Enter ou Espaço num
  dos dois botões produz 1. Verificado num navegador real durante a implementação;
  aparelhos móveis em FR-050. Enter com o foco num rádio ou numa caixa não é medido aqui
  (limitação conhecida, US3).
- **SC-006**: A escala de 1 a 5 fica numa única linha, em ordem, em 100% das combinações
  de 320, 360, 375, 390, 412 e 430 px com fonte de 100%, 115%, 130%, 150% e 200%.
  Verificado por medição em viewport emulada.
- **SC-007**: 100% da área visual de cada Opção e de cada ponto da escala ativa o
  controle (amostragem nos quatro cantos e no centro de cada linha ou célula), e cada área
  tem pelo menos 44×44 px CSS. Verificado por medição em viewport emulada.
- **SC-008**: 0 páginas da jornada com rolagem horizontal de 320 a 1280 px com fonte de
  100% a 200%, inclusive com uma escala de 11 pontos. Verificado por medição em viewport
  emulada.
- **SC-009**: A até 480 px, os dois botões ocupam 100% da largura útil e a distância até a
  primeira ação terciária é de pelo menos 32 px CSS; as ligações da tela de conclusão têm
  pelo menos 44 px de altura. Verificado por medição em viewport emulada.
- **SC-010**: A 375×667, a primeira ação da tela de formações de Ana, Maria e Diego
  aparece na primeira tela, descontada a faixa e o cabeçalho de demonstração. Verificado
  por medição em viewport emulada.
- **SC-011**: Em 100% das Pessoas de demonstração, a ordem das formações na tela é
  idêntica à devolvida pela 007; 0 ocorrências de "Sem pesquisa disponível no momento"
  por formação; 100% das formações em ambiguidade mostram o texto atual. Verificado por
  teste automatizado.
- **SC-012**: Na confirmação, exatamente 1 agradecimento, com ou sem texto de
  encerramento na Versão. Verificado por teste automatizado.
- **SC-013**: 0 modelos, tabelas, colunas ou migrações novos; 0 arquivos ou trechos de
  JavaScript; os cenários E2E-1 a E2E-4 passam sem JavaScript; o verificador de
  acessibilidade da 008 passa em 100% das telas da jornada, incluindo os estados novos
  (pendência, saída por "Salvar e sair", trajetória).
- **SC-014**: 0 falhas nas suítes da 009, da 011 e da demonstração; 0 diferenças
  visuais, a 375 e 1280 px, nas telas: lista de Pesquisas e edição de Pergunta (009),
  painel de uma Campanha (011), entrada e operador da demonstração; a prévia de Seção da
  009 acompanha os controles da jornada.
- **SC-015**: 100% das células da Matriz de comportamento do rodapé têm destino definido e
  verificado; 0 ações sem destino e 0 mensagens contraditórias com o que está gravado.

## Assumptions

- A gravação parcial, a idempotência a reenvio e a toque duplo e a ausência de
  duplicidade já verificadas pela auditoria mobile [A] continuam válidas; esta feature
  não as reimplementa.
- O limite de 480 px CSS para botões em largura total e os 32 px de separação são
  hipóteses de produto reversíveis, derivadas das medidas da auditoria mobile. [Hipótese]
- O limite de 44×44 px CSS para área ativável vem da decisão já registrada da 008
  (research R14), agora efetivo na área tocável e não só no visual.
- A faixa e o cabeçalho de demonstração não existirão em produção; por isso as medidas de
  "primeira tela" os descontam.
- As Pessoas e formações fictícias da demonstração (Ana, Maria, Diego, Elisa) continuam
  disponíveis para os cenários.

## Relação com outras features

- **008** — esta feature revisa requisitos da 008 de forma localizada: FR-020 (texto da
  entrada), FR-021 (pedir a escolha), FR-023 (situações mostradas por formação), FR-032
  (hierarquia de títulos), FR-049 e FR-050 (só para "Salvar e sair"), FR-062
  (agradecimento), FR-071 (título com pendência), FR-076 (foco e anúncio), FR-077 (forma
  da escala e área tocável). Todos os demais requisitos da 008 continuam valendo, em
  especial FR-028, FR-034, FR-079, FR-080, FR-091, FR-095 e FR-096.
- **005 / 006** — consumidas sem alteração: gravação, pendências, destino, conclusão.
- **007** — consumida sem alteração: situação de entrada, situações, ordem.
- **009** — a prévia de Seção reutiliza os controles de Pergunta e passa a refletir
  FR-018 a FR-022; demais telas sem mudança.
- **011** e **demonstração** — compartilham a folha de estilo; sem mudança visível.
- **Auditorias** — esta feature fecha os achados [I] listados em "Estado das auditorias";
  os demais continuam registrados nos documentos de origem.

## Invariantes Constitucionais Afetados *(mandatory)*

- **III — Dado institucional não é resposta declarada**: a linha e a frase da formação
  são só exibidas; nada é gravado, pré-preenchido, sugerido ou deduzido (FR-032, FR-035).
- **VIII / XIII — Preservação histórica e instrumento**: nenhum texto, ordem ou regra da
  Versão muda; Seção sem título não ganha título inventado (FR-023, FR-046).
- **IX — Periodicidade**: a confirmação não promete novo contato (FR-039).
- **XIV — Reduzir fricção**: salvar incompleto, sair salvando, sem envio acidental,
  trajetória compacta, contextualizar em vez de perguntar.
- **XVI — Privacidade**: a mensagem de saída não carrega dado pessoal nem valor declarado
  no endereço (FR-012).
- **XX — Acessibilidade**: foco no resumo, grupo de rádios correto, alvos de 44 px,
  pendência sem depender de cor (FR-006, FR-019, FR-022, FR-027).
- **XXI — Mobile**: escala com fonte ampliada, botões de largura total, separação das
  ações que descartam (FR-015, FR-021).
- **XXII / XXIII — Simplicidade; editor não é form builder**: nenhuma abstração,
  componente genérico ou tratamento por Pergunta (FR-018, FR-044).
- **XXIX — Hipóteses não viram regra**: ordem da 007 sem significado novo; ambiguidade
  com o tratamento provisório do DP-701; textos sob DP-801; nenhuma mensagem falsa
  (FR-008, FR-035, FR-037, FR-048).

## Out of Scope *(mandatory)*

**[V] — Versão do instrumento** (revisão explícita, aprovada e versionada):

- títulos de Seção em segunda pessoa (ID-05) e título da Seção sem título (ID-13; núcleo
  de UX-11);
- ordem da jornada (ID-07), texto de abertura (ID-08), transições por texto de Seção;
- tamanho e divisão das Seções 8 e 9; reordenar, dividir ou criar Seções;
- tipo numérico para idade e ano (MF-11); Q2 aceitar texto;
- rótulo do ponto 1 das escalas (003/DP-301);
- qualquer alteração de significado ou redação de Pergunta.

**[Dec] — Decisão pendente**:

- não perguntar o que o Ifes já sabe, Q10–Q19 (ID-01, D-1, 003/DP-307), e o corte de
  nomes na lista suspensa (MF-12);
- mostrar outras formações como contexto na Seção de estudos (ID-02, 007/DP-702);
- histórico de Participações na trajetória e "bem-vindo(a) de volta" (ID-10, D-3);
- abertura por WhatsApp/e-mail, navegador embutido, persistência da identificação ao
  fechar o navegador (004/DP-406);
- métricas de abandono (008/DP-803); ver, copiar ou compartilhar respostas (008/DP-802);
- linguagem e identidade visual definitivas (008/DP-801), além do tratamento provisório;
- comunicação definitiva da ambiguidade (007/DP-701); Q1 = "Não" sem concluir (D-4).

**[T] — Validação em aparelho real** (posterior, FR-050): MF-03; frequência de descarte
de aba; rótulo e efeito da tecla de retorno no teclado virtual; VoiceOver e TalkBack;
barra "anterior/próximo" do iOS; seletor nativo com listas longas.

**Recomendações descartadas** (não fazer):

- `autocomplete="off"` ou qualquer outro mecanismo para MF-03 (D4);
- MF-07 (retorno "Salvando…"): exigiria JavaScript, e o servidor já é idempotente;
- MF-08 (reenvio ao recarregar a página de erro): uniformizar exigiria guardar valores
  não enviados, vedado pela 008 FR-091;
- UX-16 (aviso de percurso persistente): a 006 não distingue o motivo de a Seção estar
  fora do percurso;
- oferecer outra formação na confirmação, frase de finalidade, "Salvar e voltar",
  alterar o rótulo da tecla de retorno;
- reordenar formações, "linha do tempo", novo formato de linha da formação;
- escala forçada numa linha única independentemente do número de pontos;
- autosave, armazenamento local, aviso ao sair, PWA, service worker, offline, navegação
  inferior fixa, wizard, uma pergunta por tela, telas de respiro, indicador percentual,
  estimativa de tempo, framework JavaScript, design system, componente genérico,
  analytics.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

**Novas nesta feature**: nenhuma.

**Herdadas e afetadas por esta feature** (mantidas abertas, com o tratamento provisório
indicado):

- **008/DP-801** — linguagem e identidade visual: todos os textos novos são provisórios
  (FR-048).
- **007/DP-701** — comunicação da ambiguidade: texto atual preservado (FR-037).
- **007/DP-702** — distinção de formações com atributos insuficientes: só atributos
  existentes, sem rótulo fabricado (FR-032, FR-034).
- **003/DP-307** — Q10–Q19 continuam perguntadas; a linha de contexto não as substitui.
- **003/DP-301** — rótulo do ponto inicial da escala não inventado.
- **008/DP-802**, **008/DP-803**, **004/DP-406** — fora desta feature.

**Validação posterior registrada (não é decisão institucional)**: MF-03 e os demais
itens [T] de FR-050; o resultado do item 4 orienta uma eventual decisão futura sobre
MF-03.


## Nota de revisão pela Feature 021 (2026-10-04)

- **FR-030:** o título da tela de formações passa de "Sua trajetória no Ifes" a "Suas
  formações no Ifes" (021 FR-006). O nome "Minha trajetória no Ifes" fica reservado à
  devolutiva. A ligação das telas de estado (`aviso.html`) passa a "Ver suas formações no
  Ifes".
- **FR-041:** na confirmação de Participação ancorada em Conclusão Acadêmica, a ação única
  passa a ser "Ver minha trajetória no Ifes", que leva a `/minha-trajetoria/` (021
  FR-003). A confirmação declarada (019) não muda (021 FR-007). A confirmação continua sem
  download, prévia ou trecho da narrativa (008 FR-063; 021 FR-004).
- **Tela de formações:**
  - ganha a ligação "Ver minha trajetória no Ifes" quando há Participação concluída
    institucional (021 FR-005);
  - ganha o texto fixo "Ao final, você poderá ver sua trajetória no Ifes." quando há
    pesquisa a iniciar ou retomar (021 FR-070), sem conteúdo personalizado e fora da
    Versão.

  A FR-035 continua valendo para esta tela.

Referência: [021 — Minha Trajetória: narrativa visual personalizada](../021-minha-trajetoria-narrativa/spec.md).
