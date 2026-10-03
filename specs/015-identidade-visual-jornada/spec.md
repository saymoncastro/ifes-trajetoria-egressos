# Feature Specification: Foundations e validação da identidade visual da jornada do egresso

**Feature Branch**: `claude/feature-015-identidade-visual`

**Created**: 2026-10-03

**Status**: Draft

**Input**: User description: "015 — Foundations e validação da identidade visual do
Trajetória Ifes (jornada do egresso), conforme a auditoria
docs/auditorias/2026-10-03-identidade-visual.md e os pontos fixados pelo solicitante."

## Contexto

A [auditoria de identidade visual](../../docs/auditorias/2026-10-03-identidade-visual.md)
(achados **IV-nn**) concluiu que o Trajetória Ifes é hoje um serviço público acessível e
competente, mas **genérico**: o shell não tem nenhum sinal do Ifes (IV-01), um azul sem
origem institucional faz papel de marca, ação, contexto e pendência (IV-02), o
questionário não tem ritmo (IV-04), o feedback não tem semântica visual (IV-06) e os
controles não mostram estado (IV-07). A auditoria também listou o que **preservar**
(IV-P1 a IV-P11) e propôs foundations mínimas, um mini sistema visual e um gate em quatro
situações. A correção imediata IV-03 (frase de pendência na cor de erro) é tratada à
parte, no PR #23 (mergeado em `b4476ce`), e é **baseline** desta feature.

Esta feature responde:

> **"Qual é a primeira versão real — código de produção — das foundations e da
> identidade visual da jornada do egresso, e como ela é validada antes de qualquer
> propagação para outras áreas?"**

### Princípios desta spec

1. **Código de produção, não protótipo.** Tudo o que esta feature entrega é código de
   produção e, depois de aprovado, a foundation oficial da jornada. Não há HTML paralelo,
   tema temporário, CSS experimental duplicado, página fictícia nem implementação a
   refazer: o que não passar no gate é **refinado na mesma branch**, nunca descartado nem
   reimplementado do zero.
2. **O gate tem dois papéis, em momentos diferentes.** (a) **Antes do merge**, é critério
   de aceite da própria 015: implementar na branch → validar nas quatro situações → se
   algum critério falhar, corrigir na mesma branch → repetir o gate; só depois de
   aprovada a 015 está pronta para merge. (b) **Depois do merge**, uma decisão posterior
   controla a propagação da identidade para o editor, o acompanhamento e os demais shells
   administrativos. As quatro situações da auditoria são o **gate de validação**, não o
   limite técnico: a mudança alcança toda a jornada do egresso sempre que templates,
   componentes e estilos forem compartilhados.
3. **Sem isolamento artificial.** Nenhuma duplicação, condicional ou estilo especial
   existe só para restringir a mudança às quatro telas medidas.
4. **Muda a aparência, não a arquitetura funcional.** Tudo o que a 014 decidiu
   funcionalmente continua como está.
5. **Institucionalidade concentrada.** O Ifes aparece na assinatura oficial, no fio de
   marca, na voz institucional (contexto da formação) e na ação; o resto é neutro.
6. **A/B é troca de valor, não mecanismo.** As duas direções da cor de ação existem só
   como troca **exclusiva dos dois tokens de ação** (`--cor-acao` e `--cor-acao-forte`)
   durante o desenvolvimento.
7. **Proporcionalidade.** Nenhum design system, biblioteca, framework, fonte externa,
   componente genérico ou dependência nova.

### Verificação no código e na auditoria (base: `main` em `b4476ce`, com o IV-03)

| # | Fato verificado | Evidência | Consequência para a 015 |
|---|-----------------|-----------|-------------------------|
| C1 | Uma única folha de estilo, incluída inline, serve a jornada, as páginas 403/404/500, o editor (009), o acompanhamento (011) e a demonstração; o editor e o acompanhamento somam folhas próprias | Templates base; 008 research R14 | Valores globais (ligações, botões) alcançariam as áreas administrativas; a mudança precisa ser restrita à jornada (FR-040), como na 014 (FR-045) |
| C2 | As Perguntas usam os mesmos templates em **todas** as Seções e na prévia de Seção do editor | `interface/perguntas/*`; `editor/previa_secao.html` | Estilizar a Seção 8 muda todas as Seções e a prévia; isso é desejado e não deve ser evitado |
| C3 | As telas de entrada e de operador da demonstração estendem o template base da jornada | `demonstracao/entrada.html`, `operador.html` | Herdam o shell da jornada naturalmente (Decisão D7) |
| C4 | 403/404/500 incluem a mesma folha, sem cabeçalho nem rodapé, e ficam fora dos diretórios de templates da jornada; podem ser respostas de todo o sistema, inclusive do editor e do acompanhamento (a confirmar no plan) | `403_csrf.html`, `404.html`, `500.html` | Pertencem à 015 só se puderem receber o shell da jornada sem mudança visual nas áreas administrativas (FR-020; D8) |
| C5 | Não há arquivos estáticos servidos; fontes externas são vedadas | 008 research R14; 008 FR-082 | A assinatura entra sem infraestrutura nova de estáticos, salvo necessidade demonstrada no plan (FR-018); `system-ui` permanece |
| C6 | Avisos da trajetória e da Seção são uma lista fechada: `situacao`, `percurso`, `salvo`, `saida` | `interface/mensagens.py` (`AVISOS`) | Cada código recebe uma variante visual fixa (FR-026), sem mecanismo novo |
| C7 | O verde da marca IF (`#2f9e41`) tem 3,45:1 com branco; o portal do Ifes usa `#195128` (9,34:1) e `#00420c` | Manual da Marca IF (2015); auditoria, seção 6 | Verde da marca só como gráfico; ação em verde escuro (Direção A) ou na cor do Padrão Digital de Governo (Direção B) |
| C8 | Foco atual: contorno 3 px `#1b1b1b` + halo 6 px `#ffdd00`; alvos de 44 px; escala em grade; rodapé de quatro ações | 014; auditoria IV-P1, IV-P2, IV-P5 | Preservados sem alteração (FR-009, FR-010, FR-047) |

### Decisões desta especificação

| # | Decisão | Origem |
|---|---------|--------|
| D1 | As quatro situações da auditoria são **gate de validação**, não limite técnico; a mudança cobre toda a jornada do egresso | Solicitante (2026-10-03), ponto 1 |
| D2 | Direções A (verde Ifes) e B (cor de interação do Padrão Digital de Governo) existem só como troca **exclusiva dos dois tokens de ação** (`--cor-acao` e `--cor-acao-forte`), durante o desenvolvimento | Solicitante, ponto 2; auditoria, seção 8 |
| D3 | Código de produção; o gate é **critério de aceite da 015** (falha → refinamento na mesma branch → novo gate; merge só depois de aprovado); a propagação para áreas administrativas é decisão posterior ao merge | Solicitante, ponto 3; revisão da spec (2026-10-03) |
| D4 | Assinatura oficial **sistêmica/Reitoria** do Ifes, de fonte oficial, sem redesenho nem recoloração; download só com autorização prévia | Solicitante, ponto 4; auditoria 6.3; Portaria Ifes 1.818/2012 |
| D5 | Foundations da auditoria (seções 23 e 25) são o ponto de partida; raio 0 × 4 px continua **hipótese** a decidir nesta feature | Solicitante, ponto 5 |
| D6 | Nenhuma propagação deliberada para editor, acompanhamento ou shell administrativo, mesmo com o gate aprovado | Solicitante, pontos 1 e 8 |
| D7 | Entrada e operador da demonstração **acompanham** o shell da jornada, porque estendem o mesmo template; a faixa e os controles de demonstração continuam distintos do produto | C3; Princípio 3 (sem isolamento artificial) |
| D8 | 403, 404 e 500 pertencem à 015 **somente** se puderem receber o shell da jornada sem mudança visual nas áreas administrativas fora de escopo e sem duplicação artificial de templates; se forem globais e inseparáveis, a mudança visual delas fica para a futura propagação transversal. A decisão técnica é do plan, após inspeção do código | C4; auditoria IV-05; revisão da spec (2026-10-03) |
| D9 | A revisão perceptiva (reconhecimento como Ifes) é posterior ao fechamento e não o bloqueia, como a validação em aparelho real da 014 (FR-050) | Auditoria, seção 26; solicitante (revisão da auditoria) |

## Clarifications

### Session 2026-10-03

- Q: Qual direção da cor de ação fica no código mergeado enquanto D-02 não for decidida?
  → A: **B** (cor de ação do Padrão Digital de Governo, `#1351b4`), como tratamento
  provisório; a Direção A continua hipótese recomendada, produzida e comparada no gate;
  nenhuma alternância em tempo de execução (FR-014).
- Q: O gate decide só a propagação? → A: Não. Antes do merge, é critério de aceite da
  015 (falha → refinamento na mesma branch → novo gate); depois do merge, uma decisão
  posterior controla a propagação para áreas administrativas (Princípio 2; D3; FR-042,
  FR-045).
- Q: 403/404/500 entram na 015? → A: Só se puderem receber o shell da jornada sem mudança
  visual nas áreas administrativas e sem duplicação artificial de templates; se forem
  globais e inseparáveis, ficam para a propagação transversal; o plan decide após
  inspecionar o código (D8; FR-020).
- Q: A prévia do editor herda o ritmo da jornada? → A: Não. Herda tipografia, estados e
  tratamento visual interno dos controles e da Pergunta; não herda o espaçamento de 48 px
  entre Perguntas, o shell, o ritmo de página nem regras exclusivas da jornada (FR-040;
  US6 cenário 2).
- Q: As capturas do gate entram no repositório? → A: Não. O registro textual é versionado
  com identificadores das capturas; as capturas vão anexadas ao PR ou como artefato
  externo (FR-042).
- Q: Há SVG oficial da assinatura? → A: O ZIP oficial da marca sistêmica (inspecionado com
  autorização) só tem EPS, JPG e PNG. Sem SVG, a parte da assinatura fica bloqueada por
  D-03 e o formato deve ser pedido à ACS; nenhum formato é convertido nem redesenhado
  (FR-017, FR-018; research R3).

## User Scenarios & Testing *(mandatory)*

Atores: o **egresso** que responde à pesquisa, tipicamente no celular (na demonstração,
as Pessoas fictícias Ana, Maria, Diego e Elisa); a **equipe do produto e as instâncias
institucionais** (ACS, CPAEG/Proex) que avaliam as Direções A e B e decidem a
propagação; o **operador** do editor e do acompanhamento, que não deve perceber mudança.

### User Story 1 - Reconhecer o Ifes ao abrir qualquer tela da jornada (Priority: P1)

Ao abrir a trajetória, uma Seção ou a confirmação, no celular ou no computador, a pessoa
vê no topo a assinatura oficial do Ifes e o nome "Trajetória Ifes", num cabeçalho
compacto, e um rodapé mínimo com o nome da instituição.

**Why this priority**: IV-01 é o único achado crítico; sem ele, nenhuma outra mudança
torna o produto reconhecível como do Ifes.

**Independent Test**: abrir a trajetória de Maria, a Seção 8 e a confirmação a 375 e
1280 px e medir altura do cabeçalho, tamanho do símbolo da assinatura e área livre ao
redor; abrir 403/404 e conferir o shell conforme a decisão do plan (D8).

**Acceptance Scenarios**:

1. **Given** qualquer tela da jornada a 375 px, **When** carregada, **Then** a
   assinatura oficial do Ifes está na primeira viewport, legível, com o símbolo de pelo
   menos 30 px e a área de proteção livre, e o cabeçalho do produto tem no máximo 64 px
   de altura (descontados a faixa e os controles de demonstração).
2. **Given** a mesma tela a 1280 px, **When** carregada, **Then** o cabeçalho tem no
   máximo 80 px e mostra também o subtítulo "Acompanhamento de egressos".
3. **Given** o cabeçalho, **When** lido, **Then** a assinatura do Ifes vem primeiro e o
   nome "Trajetória Ifes" aparece em texto, subordinado a ela, sem ser composto dentro
   da assinatura.
4. **Given** as páginas 403, 404 e 500, **When** exibidas, **Then** têm o mesmo
   cabeçalho e o mesmo rodapé das demais telas da jornada **se** o plan concluir que isso
   não muda a aparência das áreas administrativas (D8); caso contrário, ficam como estão
   e a mudança é registrada para a propagação transversal.
5. **Given** a demonstração, **When** qualquer tela é exibida, **Then** a faixa de
   demonstração e os controles "Trocar de pessoa" e "Encerrar demonstração" continuam
   visíveis e distinguíveis do produto, sem usar as cores da marca.

---

### User Story 2 - Responder uma Seção longa com ritmo e estados visíveis (Priority: P1)

Na Seção 8 (14 Perguntas, escalas, rádios, caixas e "Outro"), a pessoa encontra de
imediato o começo de cada Pergunta, distingue enunciado, texto auxiliar e opções, e vê
claramente o que já marcou — inclusive na escala.

**Why this priority**: o questionário é a experiência central (auditoria, seção 16);
IV-04 e IV-07 são os achados que mais alteram a sensação de esforço.

**Independent Test**: abrir a Seção 8 a 375, 390, 430 e 1280 px, medir espaçamentos e
tamanhos, marcar opções e pontos e conferir os estados; repetir as medições da 014 para
a escala e os alvos.

**Acceptance Scenarios**:

1. **Given** uma Seção, **When** exibida, **Then** o espaço entre duas Perguntas é de
   48 px e o espaço entre o enunciado e a resposta é de 8 px.
2. **Given** uma Pergunta, **When** exibida, **Then** o enunciado aparece em 18 px e
   peso 600; texto explicativo, descrição da escala e "(obrigatória)" aparecem em 15 px
   na cor de texto secundário; as opções continuam em 16 px; nenhum texto muda.
3. **Given** uma Opção de rádio ou caixa marcada, **When** exibida, **Then** a linha
   mostra estado selecionado por uma marca de acento com contraste de pelo menos 3:1,
   além do próprio controle; o controle usa a cor de ação.
4. **Given** uma Pergunta de escala, **When** exibida, **Then** cada ponto aparece numa
   célula visualmente delimitada (contorno com pelo menos 3:1) e o ponto marcado tem
   estado selecionado visível além do controle.
5. **Given** a escala de 1 a 5 de 320 a 430 px com fonte de 100% a 200%, **When**
   exibida, **Then** continua numa única linha, em ordem, sem rolagem horizontal, e cada
   célula e linha continua inteiramente ativável com pelo menos 44×44 px (014 SC-006,
   SC-007).
6. **Given** qualquer Seção, **When** exibida, **Then** nenhuma Pergunta aparece dentro
   de card, caixa com sombra ou superfície própria.

---

### User Story 3 - Entender pendência, erro, salvamento e conclusão pela aparência (Priority: P1)

Depois de enviar, a pessoa entende pela forma e pela cor — sempre acompanhadas do texto
— se faltam respostas (pendência), se algo foi recusado (erro), se o que respondeu está
salvo ou se a pesquisa foi concluída.

**Why this priority**: IV-06 e a semântica de cor (IV-02); são os momentos de maior
ansiedade e de maior alívio da jornada.

**Independent Test**: Seção 2 de Maria com pendências; Seção 8 com erro de forma;
"Salvar e sair" com e sem Resposta gravada; mudança de situação; aviso de percurso;
conclusão e confirmação — conferir variante, cores e leitura em escala de cinza.

**Acceptance Scenarios**:

1. **Given** uma reapresentação com pendências, **When** exibida, **Then** resumo, fio
   da Pergunta, frase "Falta responder: …" e borda do campo usam a cor de
   informação/pendência e nenhum deles usa a cor de erro.
2. **Given** uma reapresentação com erro de forma, **When** exibida, **Then** resumo,
   fio, frase "Erro: …" e borda do campo usam a cor de erro.
3. **Given** as duas reapresentações convertidas para escala de cinza, **When**
   comparadas, **Then** continuam distinguíveis pelo título, pelo prefixo e pela forma,
   sem depender de cor.
4. **Given** a chegada à trajetória com o aviso `salvo`, **When** exibida, **Then** o
   aviso usa a variante de **sucesso**; com `saida`, `situacao` ou `percurso`, usa a
   variante de **informação**.
5. **Given** a confirmação "Pesquisa concluída", **When** exibida, **Then** o topo tem
   tratamento de sucesso (fio de acento na cor de sucesso e, se houver, ícone ao lado do
   título, nunca no lugar do texto), sem animação.
6. **Given** a reapresentação que leva o foco ao resumo ao carregar, **When** o resumo
   está focado, **Then** há indicação visual de foco no resumo.

---

### User Story 4 - Ver a trajetória com hierarquia clara (Priority: P2)

Na tela "Sua trajetória no Ifes", a pessoa distingue a formação, os atributos
complementares, a situação e a ação, e encontra a ação principal com o mesmo padrão das
Seções.

**Why this priority**: primeira impressão da jornada (IV-09, IV-10); a estrutura e a
ordem são da 014 e não mudam.

**Independent Test**: trajetória de Ana, Maria (seleção) e Diego (outras formações,
ambiguidade, "Pesquisa já respondida") a 375 e 1280 px.

**Acceptance Scenarios**:

1. **Given** um item de formação, **When** exibido, **Then** a linha principal tem peso
   600, o complemento 15 px na cor de texto secundário e a situação não tem o mesmo peso
   tipográfico da linha principal; o espaço acima e abaixo do conteúdo do item é igual.
2. **Given** a entrada resolvida, **When** exibida, **Then** a linha da formação na frase
   "Você concluiu …" aparece destacada, com o mesmo texto e a mesma frase da 014.
3. **Given** qualquer ação principal da jornada ("Iniciar/Continuar a pesquisa",
   "… desta formação", "Concluir pesquisa") até 480 px, **When** exibida, **Then** ocupa
   toda a largura útil da coluna, como os botões do rodapé da Seção.
4. **Given** qualquer Pessoa de demonstração, **When** a trajetória é exibida, **Then** a
   ordem, os textos, as situações e as ações são idênticos aos da 014.

---

### User Story 5 - Comparar as Direções A e B antes da decisão institucional (Priority: P2)

A equipe produz as duas variantes da cor de ação trocando exclusivamente os dois tokens
de ação (`--cor-acao` e `--cor-acao-forte`) e entrega às
instâncias institucionais um registro com as quatro situações nas duas direções, para
decidir com base no que funciona e no esclarecimento do Padrão Digital de Governo.

**Why this priority**: D-02 da auditoria — a cor de ação não é escolha estética e não
pode ser decidida antes do esclarecimento institucional.

**Independent Test**: trocar o valor de ação e sua variante forte, sem outra alteração,
e conferir que as quatro situações mudam por inteiro e continuam atendendo aos critérios
objetivos.

**Acceptance Scenarios**:

1. **Given** a Direção A, **When** se troca apenas o valor da cor de ação e o de sua
   variante forte pelos da Direção B, **Then** todas as ações, ligações, controles
   marcados e estados que usam a cor de ação mudam, e nada mais muda.
2. **Given** as duas direções, **When** medidas, **Then** ambas atendem aos critérios de
   contraste, foco e legibilidade desta spec.
3. **Given** o sistema em execução, **When** inspecionado, **Then** não existe nenhum
   meio de alternar a direção em tempo de execução (configuração, variável de ambiente,
   preferência, parâmetro de endereço, opção administrativa ou condicional).

---

### User Story 6 - Operar o editor e o acompanhamento sem perceber mudança (Priority: P2)

Quem usa o editor (009) e o acompanhamento (011) não vê mudança, exceto na prévia de
Seção do editor, que mostra as Perguntas como o egresso as verá.

**Why this priority**: a folha é compartilhada (C1); a propagação administrativa é
decisão posterior (D6).

**Independent Test**: comparação visual antes/depois, a 375 e 1280 px, das telas
administrativas listadas em SC-012; suítes da 009 e da 011.

**Acceptance Scenarios**:

1. **Given** as telas do editor e do acompanhamento, **When** exibidas antes e depois,
   **Then** cabeçalho, rodapé, botões, ligações, campos, tabelas e listas têm a mesma
   aparência.
2. **Given** a prévia de uma Seção no editor, **When** exibida, **Then** as Perguntas
   têm a mesma tipografia, os mesmos estados e o mesmo tratamento visual interno dos
   controles e da Pergunta da jornada, **sem** herdar o espaçamento entre Perguntas, o
   shell, o ritmo de página nem outras regras exclusivas da jornada; a composição própria
   da prévia (Perguntas intercaladas com anotações do editor) não muda.

### Edge Cases

- **320 px com fonte a 200%**: assinatura e nome do produto não podem gerar rolagem
  horizontal; se não couberem lado a lado, o nome passa para baixo da assinatura,
  mantendo a assinatura acima do limite mínimo; o limite de 64 px vale para fonte a
  100%.
- **Espaço insuficiente para a assinatura no tamanho mínimo**: a assinatura nunca é
  reduzida abaixo de 30 px de símbolo nem recortada; é o nome do produto que se adapta.
- **Nome de curso longo** no contexto e na ficha: quebra sem truncar; a ficha empilha
  rótulo e valor até 480 px.
- **Seção sem título** (Seção 13): mesmo ritmo e mesmo título principal da 014.
- **Escala de 0 a 10**: células delimitadas quebram em linhas alinhadas, sem rolagem
  horizontal (014 FR-021).
- **Pergunta opcional com "Deixar esta pergunta sem resposta"**: a caixa segue o padrão
  de estado das caixas.
- **Alto contraste do sistema** (cores forçadas): nenhum significado depende de fundo
  tonal ou de borda suave; marcas de estado e foco continuam visíveis.
- **Pessoa sem formação, sem pesquisa ou sem entrada pendente**: mesma tela da 014, com o
  shell novo.
- **Faixa de demonstração**: continua acima do produto, com cor própria, fora das
  medidas de cabeçalho.
- **Impressão ou JavaScript desativado**: aparência idêntica sem JavaScript; nenhum
  requisito de impressão.
- **Ícones ausentes**: se a feature não usar ícones, nenhum estado perde significado,
  porque todo estado tem texto.

## Requirements *(mandatory)*

Cada requisito indica a origem: achado da auditoria (**IV-nn**, **IV-Pn**), seção da
auditoria (**Aud. §n**), **[014 FR-nnn]**, **[008 …]**, **[Const.]**, **[Solicitante]**,
**[Hipótese]** (reversível) ou **[Arquitetura]**.

### Functional Requirements

**Foundations**

- **FR-001**: A jornada DEVE ter um **conjunto único e nomeado de valores visuais**
  (cores, tipografia, espaçamento, bordas, raio, container, breakpoint, alvo), definido
  num só lugar, com o contraste de cada cor documentado ao lado do valor. Nenhum valor
  visual da jornada DEVE ficar solto fora desse conjunto, salvo os isolados listados na
  auditoria como não-token (Aud. §25). [IV-12; Aud. §25]
- **FR-002**: As cores DEVEM ter papéis semânticos fixos, com estes valores de partida
  [Aud. §25]:

  | Papel | Valor | Contraste com branco | Uso permitido |
  |---|---|---|---|
  | Marca | `#2f9e41` | 3,45:1 | **Só gráfico** (fio de marca); nunca texto |
  | Ação | Direção A `#195128` · Direção B: cor de interação do PDG (hoje `#1351b4`) | ≥ 4,5:1 obrigatório | Botão principal, contorno do secundário, ligações, controle marcado, estado selecionado |
  | Ação forte | Direção A `#00420c` · Direção B: variante escura do PDG (hoje `#0c326f`) | ≥ 4,5:1 | Hover e ativo |
  | Sucesso | `#195128` (fixo nas duas direções) | 9,3:1 | Aviso `salvo`, confirmação |
| Voz institucional (fio) | `#2f9e41` (cor da marca, fixa nas duas direções) | 3,45:1 (gráfico) | Fio do contexto e da ficha |
| Voz institucional (fundo) | verde muito claro, ≈ `#eef7f0`, a calibrar | texto sobre ele ≥ 4,5:1 | Fundo do contexto e da ficha da formação; fundo tonal de seleção |
  | Texto | `#1b1b1b` | 17,2:1 | Corpo |
  | Texto secundário | `#565c65` | 6,7:1 | Auxiliar, notas, complemento, subtítulo |
  | Fundo | `#ffffff` | — | Página |
  | Borda forte | `#565c65` | 6,7:1 | Campos, células, contornos de controle |
  | Borda suave | ≈ `#c6cace`, a calibrar | < 3:1 | **Só divisores decorativos** |
  | Informação/pendência | `#1a4480` | 9,6:1 | Pendência, aviso informativo |
  | Erro | `#b50909` | 7,0:1 | Erro |
  | Foco | `#1b1b1b` + `#ffdd00` | 12,8:1 | Foco (inalterado) |
  | Demonstração | `#fff1d2` | — | Só a faixa de demonstração |

- **FR-003**: O verde da marca NÃO DEVE ser usado como cor de texto, de fundo sob texto
  ou de controle. O vermelho da marca IF NÃO DEVE aparecer fora da assinatura oficial.
  [Aud. §6.3, §23.1; Manual da Marca IF]
- **FR-004**: O verde DEVE aparecer **somente** em: (1) assinatura e fio de marca;
  (2) voz institucional — contexto da formação e ficha da formação; (3) ação, na
  Direção A; (4) sucesso. Perguntas, opções, campos, títulos e textos DEVEM ser neutros.
  [Aud. §23.2; Solicitante, ponto 5]
- **FR-005**: A tipografia DEVE continuar `system-ui` (sem fonte externa), com os
  tamanhos 28, 22, 18, 16 e 15 px, os pesos 400, 600 e 700 e entrelinhas 1,25
  (títulos), 1,4 (enunciados) e 1,5 (corpo); 16 px continua o mínimo de campos e corpo.
  [IV-P4; Aud. §10; 008 R14]
- **FR-006**: O espaçamento DEVE usar só os passos 4, 8, 12, 16, 24, 32 e 48 px. [Aud.
  §12]
- **FR-007**: O container da jornada DEVE continuar com 40 rem, gutter de 16 px e um
  único breakpoint de 480 px, expresso numa única unidade. [IV-P3; IV-12]
- **FR-008**: A jornada NÃO DEVE ter sombras nem cards; as bordas DEVEM usar só as
  espessuras 1 px (divisor suave), 2 px (controle, borda forte) e 4 px (acento de estado
  e voz institucional). O raio DEVE ser um valor único, **0 ou 4 px**, decidido nesta
  feature por comparação registrada (FR-044). [IV-P7; IV-13; Hipótese]
- **FR-009**: O foco DEVE permanecer exatamente o atual em todos os elementos focáveis
  (contorno 3 px `#1b1b1b`, halo 6 px `#ffdd00`). [IV-P2]
- **FR-010**: Todos os alvos DEVEM manter as áreas ativáveis da 014 (≥ 44×44 px; linha e
  célula inteiras). [IV-P5; 014 FR-019]

**Direções A e B da cor de ação**

- **FR-011**: A troca entre as Direções A e B DEVE alterar **exclusivamente os dois
  tokens de ação**, `--cor-acao` e `--cor-acao-forte`: trocar esses dois tokens DEVE
  bastar para gerar a outra direção em toda a jornada, sem tocar em nenhum outro valor,
  componente, template ou tela, e sem abstração adicional criada só para reduzi-los a um. [Solicitante, ponto 2; Aud. §8]
- **FR-012**: NÃO DEVE existir mecanismo de alternância em tempo de execução: feature
  flag, configuração, variável de ambiente, preferência do usuário, parâmetro de
  endereço, opção administrativa ou lógica condicional. [Solicitante, ponto 2; Const.
  XXII]
- **FR-013**: As duas direções DEVEM atender a todos os critérios objetivos desta spec
  (contraste, foco, estados). Depois da decisão institucional, DEVE permanecer apenas
  uma direção no código. [Solicitante, ponto 2]
- **FR-014**: Enquanto D-02 não for decidida, o valor mantido no código mergeado DEVE ser
  o da **Direção B** (cor de ação do Padrão Digital de Governo, hoje `#1351b4`, e sua
  variante forte), como **tratamento provisório** de D-02: não se deixa como padrão uma
  divergência consciente do PDG enquanto sua aplicação não for esclarecida. Isso NÃO
  rejeita a Direção A (`#195128`), que continua sendo a hipótese visual recomendada pela
  auditoria e DEVE ser produzida e comparada no gate (FR-042). Assinatura, fio de marca,
  voz institucional e sucesso permanecem verdes nas duas direções. [Solicitante,
  clarificação 2026-10-03; D-02]

**Shell institucional da jornada**

- **FR-015**: Toda tela da jornada DEVE ter um cabeçalho de fundo branco com: fio de marca
  de 4 px no topo, na cor da marca; a assinatura oficial do Ifes à esquerda; um separador
  vertical; o nome "Trajetória Ifes" em texto (18 px, peso 700); e, a partir de 480 px, o
  subtítulo "Acompanhamento de egressos" (15 px, texto secundário). [IV-01; Aud. §17.1]
- **FR-016**: O cabeçalho DEVE ter no máximo 64 px de altura a 375 px e 80 px a 1280 px,
  com fonte a 100%, descontados a faixa e os controles de demonstração; NÃO DEVE ter
  navegação. [Aud. §17.1]
- **FR-017**: A assinatura DEVE: (a) ser a **sistêmica/Reitoria** do Ifes, obtida de fonte
  oficial; (b) não ser redesenhada, recolorida, distorcida, recortada, contornada nem
  composta com o nome do produto; (c) ter o símbolo com pelo menos 30 px; (d) manter
  área de proteção de pelo menos um módulo livre de qualquer elemento; (e) usar a versão
  colorida sobre fundo branco; (f) ter nome acessível que identifique o Instituto
  Federal do Espírito Santo; (g) vir antes do nome do produto e subordiná-lo. [D4; Manual
  da Marca IF; Portaria Ifes 1.818/2012]
- **FR-018**: A assinatura DEVE ser incluída sem carregar recurso de terceiros e sem
  criar infraestrutura de arquivos estáticos, salvo necessidade demonstrada no plan.
  [Solicitante, ponto 4; 008 R14, FR-082; Const. XVI, XXII]
- **FR-019**: O rodapé da jornada DEVE ser mínimo: "Instituto Federal do Espírito Santo"
  em 15 px na cor de texto secundário, separado por divisor suave, com no máximo 120 px
  de altura a 375 px; sem colunas, redes sociais, banners ou mapa do site. Ligações de
  privacidade, acessibilidade e contato ficam fora desta feature (QF-5). Em demonstração,
  a indicação de ambiente fictício continua presente. [Aud. §17.2]
- **FR-020**: O mesmo cabeçalho e o mesmo rodapé DEVEM aparecer em todas as telas da
  jornada, inclusive telas de estado e as telas de entrada e de operador da
  demonstração. As páginas 403, 404 e 500 DEVEM receber o mesmo shell **somente** se
  isso não produzir mudança visual nas áreas administrativas fora de escopo e sem
  duplicação artificial de templates; se forem globais e inseparáveis, NÃO DEVEM mudar
  nesta feature, e a mudança fica para a propagação transversal. [IV-05; D7; D8]
- **FR-021**: A faixa e os controles de demonstração DEVEM continuar visíveis e
  distinguíveis do produto, sem usar as cores da marca nem da ação. [IV-16]

**Questionário**

- **FR-022**: Entre Perguntas DEVE haver 48 px; entre enunciado e resposta, 8 px. [IV-04]
- **FR-023**: O enunciado DEVE ter 18 px e peso 600; texto explicativo, descrição da
  escala, "(obrigatória)" e "(marque todas que se aplicam)" DEVEM ter 15 px na cor de
  texto secundário; as opções continuam com 16 px e peso 400. Nenhum texto DEVE mudar.
  [IV-04; Const. XIII]
- **FR-024**: Nenhuma Pergunta DEVE ser envolvida em card, sombra ou superfície própria.
  Um divisor suave entre Perguntas PODE ser adotado **somente** se a validação a 375 px
  mostrar que o espaço sozinho não basta, com a comparação registrada. [Aud. §16;
  Hipótese]
- **FR-025**: Rádios e caixas DEVEM usar a cor de ação no controle marcado; a linha de uma
  Opção marcada e a célula de um ponto marcado DEVEM mostrar estado selecionado por marca
  de acento com contraste de pelo menos 3:1, além do controle; o fundo tonal PODE
  complementar, nunca substituir. As células da escala DEVEM ser visualmente delimitadas
  por contorno com contraste de pelo menos 3:1. Linha e célula PODEM ter estado de hover.
  Nada disso DEVE reduzir a área ativável, mudar a marcação acessível nem quebrar a
  escala de 1 a 5 numa linha (014 FR-019 a FR-022). [IV-07]

**Feedback e estados**

- **FR-026**: Os avisos DEVEM ter duas variantes, com fio de acento de 4 px e o texto
  atual: **sucesso** (cor de sucesso, verde nas duas direções) para `salvo`; **informação** (cor de
  informação/pendência) para `saida`, `situacao` e `percurso`. [IV-06; C6]
- **FR-027**: Pendência DEVE usar a cor de informação/pendência no resumo, no fio da
  Pergunta, na frase por Pergunta e na borda do campo; erro DEVE usar a cor de erro nos
  mesmos lugares. Os acentos de estado DEVEM ter a mesma espessura (4 px). Pendência e
  erro DEVEM continuar distinguíveis sem cor, por título, prefixo e forma. [014 FR-003 a
  FR-007; IV-03 (PR #23); IV-12]
- **FR-028**: O resumo de pendência ou erro, quando focado ao carregar, DEVE ter
  indicação visual de foco. [IV-15; 014 FR-027]
- **FR-029**: A confirmação "Pesquisa concluída" DEVE ter tratamento de sucesso no topo
  (fio de acento na cor de sucesso), sem animação, ilustração ou texto novo. [IV-06]
- **FR-030**: Ícones são opcionais; se usados, DEVEM ser no máximo três (visto,
  informação, alerta), inline, de traço uniforme, sempre ao lado de texto e ocultos de
  tecnologias assistivas, só em avisos, resumos e confirmação, sem biblioteca. [IV-14;
  Hipótese]

**Trajetória, contexto e ações**

- **FR-031**: O item de formação DEVE ter: linha principal com peso 600; complemento em
  15 px na cor de texto secundário; situação em peso regular, sem competir com a linha
  principal (cor do estado quando houver); ação abaixo; divisor suave entre itens;
  espaço igual acima e abaixo do conteúdo. Conteúdo, ordem e situações DEVEM ser os da
  014. [IV-09; 014 FR-034 a FR-037]
- **FR-032**: Na entrada resolvida, a linha da formação dentro da frase "Você concluiu …"
  DEVE ser destacada visualmente, sem mudar a frase. [IV-09; 014 FR-031]
- **FR-033**: A ação principal de toda tela da jornada DEVE ocupar toda a largura útil da
  coluna até 480 px. [IV-10; 014 FR-015]
- **FR-034**: O contexto compacto ("Você está respondendo sobre:") e a ficha da formação
  DEVEM usar a voz institucional: fio de 4 px na cor da marca e fundo de voz
  institucional, iguais nas duas direções; a ficha DEVE empilhar rótulo e valor até
  480 px. [IV-11; IV-P8; Aud. §23.2]
- **FR-035**: Divisores DEVEM usar a borda suave; campos, células e contornos de controle,
  a borda forte. Nenhum significado DEVE depender da borda suave. [IV-08]

**Preservações e fronteiras**

- **FR-036**: Esta feature NÃO DEVE alterar: textos fixos, textos da Versão, ordem,
  rodapé de quatro ações e seu comportamento, salvamento e regra de verdade, pendência ×
  erro, ordem e situações das formações, forma funcional da escala, áreas ativáveis,
  ramificação, validação, retomada, rotas, marcação acessível exigida pela 014 e pela
  008. [Solicitante, ponto 6; 014 FR-009 a FR-041]
- **FR-037**: Esta feature NÃO DEVE criar modelo, tabela, coluna, migração ou JavaScript,
  nem carregar recurso de terceiros. [008 FR-080, FR-082; 014 FR-042, FR-043]
- **FR-038**: Esta feature NÃO DEVE criar HTML paralelo, tema temporário, estilo
  duplicado, página fictícia ou implementação descartável. [Solicitante, ponto 3]
- **FR-039**: Esta feature NÃO DEVE criar duplicação, condicional ou estilo especial
  destinado a restringir a mudança às quatro situações do gate; templates e estilos
  compartilhados mudam para toda a jornada. [D1; Solicitante, ponto 1]
- **FR-040**: Editor (009) e acompanhamento (011) NÃO DEVEM ter mudança visual, exceto a
  prévia de Seção do editor, que DEVE refletir a tipografia, os estados e o tratamento
  visual interno dos controles e da Pergunta compartilhados com a jornada, **sem** herdar
  espaçamento entre Perguntas, shell, ritmo de página ou demais regras exclusivas da
  jornada do egresso. O espaçamento de 48 px entre Perguntas pertence à composição da
  jornada e NÃO DEVE modificar a composição própria do editor. O shell administrativo NÃO
  DEVE mudar. [D6; 014 FR-045; Solicitante, revisão do plan 2026-10-03]
- **FR-041**: Esta feature NÃO DEVE criar componente genérico, biblioteca, pacote,
  framework, catálogo de componentes nem design system institucional. [Const. XXII,
  XXIII; Aud. §24]

**Validação e gate**

- **FR-042**: A 015 SÓ DEVE ser considerada pronta para merge depois de aprovada no gate.
  Se algum critério objetivo (SC-001 a SC-013) falhar, a implementação DEVE ser
  corrigida ou refinada na mesma branch e o gate repetido; o código não é descartado nem
  reimplementado do zero. O fechamento DEVE produzir um **registro de validação** com,
  para as quatro
  situações do gate — (1) trajetória de Maria e de Diego; (2) Seção 8 "Avaliação";
  (3) Seção 2 com pendências e a variante com erro de forma; (4) "Concluir a pesquisa" →
  "Pesquisa concluída" —, a 375, 390, 430 e 1280 px e com fonte a 200%: as medidas dos
  critérios SC-001 a SC-011; a identificação das capturas nas Direções A e B (anexadas
  ao PR ou mantidas como artefato externo, nunca versionadas como coleção de binários);
  e o resultado da comparação de
  raio (FR-008) e de divisor entre Perguntas (FR-024). [Solicitante, ponto 7; Aud. §26]
- **FR-043**: O registro DEVE incluir a verificação de regressão das áreas
  administrativas (SC-012) e o estado da **revisão perceptiva** (pendente ou realizada):
  reconhecimento imediato como produto do Ifes, a verificar com a ACS e a CPAEG/Proex e,
  se possível, com egressos — nunca por medição automatizada. A revisão perceptiva é
  posterior e NÃO bloqueia o fechamento. [D9]
- **FR-044**: As decisões de raio (0 × 4 px) e de divisor entre Perguntas DEVEM ser
  tomadas nesta feature, por comparação lado a lado registrada, e só o valor escolhido
  DEVE permanecer no código. [D5; Hipótese]
- **FR-045**: A aprovação no gate torna a 015 pronta para merge; a propagação da
  identidade para o editor, o acompanhamento e os demais shells administrativos é
  **decisão posterior ao merge** e NÃO DEVE ocorrer automaticamente nesta feature. [D3;
  D6; Solicitante, ponto 8]
- **FR-046**: O fechamento DEVE exigir: suíte completa verde; testes da 014 e da 008
  passando (ajustados só onde a marcação mudar de propósito para o shell); testes
  automatizados para as regras verificáveis sem navegador (papéis de cor em pendência,
  erro e avisos; ausência de mecanismo de alternância; ausência de recurso externo;
  telas administrativas sem mudança de estilo). [Const. XXVI; 014 FR-049]
- **FR-047**: Os critérios da 014 SC-006 a SC-010 DEVEM ser remedidos e continuar
  válidos. [Solicitante, ponto 7]

### Key Entities *(include if feature involves data)*

Nenhuma entidade nova nem alteração de dado. A feature só altera a apresentação de
entidades existentes (Conclusão Acadêmica no contexto e na trajetória; Versão da Pesquisa
nas Seções; Participação nos estados da jornada).

## Success Criteria *(mandatory)*

### Measurable Outcomes

Todos medidos nas quatro situações do gate, nas Direções A e B, salvo indicação.

- **SC-001**: Em 100% das telas da jornada a 375 px, a assinatura oficial está na
  primeira viewport, com símbolo ≥ 30 px e área de proteção livre.
- **SC-002**: Cabeçalho ≤ 64 px a 375 px e ≤ 80 px a 1280 px (fonte a 100%, sem os
  elementos de demonstração); rodapé ≤ 120 px a 375 px.
- **SC-003**: 100% dos textos com contraste ≥ 4,5:1; 100% dos contornos de controle,
  marcas de estado e células da escala com ≥ 3:1; 0 usos do verde da marca como texto.
- **SC-004**: 100% dos elementos focáveis com o foco atual visível, inclusive o resumo
  focado ao carregar.
- **SC-005**: 0 páginas da jornada com rolagem horizontal de 320 a 1280 px com fonte de
  100% a 200%, inclusive com escala de 11 pontos.
- **SC-006**: 014 SC-006 a SC-010 continuam atendidos em 100% das combinações medidas
  pela 014.
- **SC-007**: Pendência e erro distinguíveis em escala de cinza em 100% dos casos (por
  título, prefixo e forma); 0 elementos de pendência na cor de erro e 0 elementos de erro
  na cor de pendência.
- **SC-008**: Entre Perguntas, 48 px em 100% das Seções; enunciado 18 px/600; auxiliar
  15 px na cor secundária; 0 Perguntas dentro de card ou superfície própria.
- **SC-009**: 100% das Opções e pontos marcados com estado visível além do controle;
  100% das células da escala delimitadas.
- **SC-010**: Trocar exclusivamente os dois tokens de ação (`--cor-acao` e
  `--cor-acao-forte`) muda 100% dos usos de ação e
  0 outros valores; 0 mecanismos de alternância em tempo de execução.
- **SC-011**: Verde presente somente nos lugares de FR-004 (inspeção das quatro
  situações); 0 usos do vermelho da marca fora da assinatura.
- **SC-012**: 0 mudanças visuais **não intencionais**, a 375 e 1280 px, em: lista de
  Pesquisas e edição de Pergunta (009); painel de uma Campanha (011). A prévia de Seção do
  editor é a **única exceção deliberada**, limitada a tipografia, estados e tratamento
  visual interno da Pergunta e dos controles compartilhados (FR-040); shell, ritmo de
  página, espaçamento entre Perguntas e composição do editor permanecem inalterados.
- **SC-013**: 0 modelos, migrações, arquivos ou trechos de JavaScript e recursos de
  terceiros novos; suíte completa verde.
- **SC-014**: Registro de validação completo para as quatro situações, nas duas direções,
  com as decisões de raio e divisor e o estado da revisão perceptiva.

## Assumptions

- A correção IV-03 (PR #23) está mergeada na `main` (`b4476ce`); esta feature parte dela.
- As Pessoas fictícias da demonstração e a Versão de referência continuam disponíveis
  para as quatro situações.
- O arquivo oficial da assinatura sistêmica/Reitoria está disponível publicamente em
  <https://www.ifes.edu.br/download-de-marcas>; o formato e o tamanho serão informados
  antes do download, que depende de autorização do solicitante (D4). O uso nesta
  feature é local, interno e não publicado, como insumo de desenvolvimento, respeitando o
  Manual da Marca (auditoria, seção 30).
- Os valores "a calibrar" (fundo de voz institucional, borda suave) podem variar na
  implementação, desde que cumpram os papéis e os contrastes de FR-002.
- A cor de interação do Padrão Digital de Governo usada na Direção B é a publicada no DS
  gov.br no momento da implementação (hoje `#1351b4`, 7,3:1 com branco), com variante
  escura do mesmo padrão (hoje `#0c326f`, 12,3:1).
- Os limites de 64/80/120 px e os 48 px entre Perguntas são hipóteses de produto
  reversíveis derivadas da auditoria. [Hipótese]

## Invariantes Constitucionais Afetados *(mandatory)*

- **III — Dado institucional não é resposta declarada**: o destaque da formação e a voz
  institucional são só apresentação; nada é gravado ou pré-preenchido.
- **XIII — Instrumento**: nenhum texto, ordem ou regra da Versão muda (FR-023, FR-036).
- **XIV — Reduzir fricção**: ritmo, hierarquia e estados reduzem esforço sem fragmentar
  nem esconder Perguntas.
- **XVI — Privacidade**: nenhum recurso de terceiros é carregado (FR-018, FR-037).
- **XX — Acessibilidade**: contraste, foco, alvos, independência de cor e reflow
  preservados ou melhorados (FR-003, FR-009, FR-010, FR-025, FR-027).
- **XXI — Mobile**: limites de cabeçalho, ações em largura total e medições a 375–430 px.
- **XXII / XXIII — Simplicidade; não é form builder**: sem design system, componente
  genérico, configuração ou mecanismo de alternância (FR-012, FR-041).
- **XXIX — Hipóteses não viram regra**: identidade definitiva (DP-801) e aplicação do PDG
  (D-02) continuam pendentes; a direção mantida no código é tratamento provisório.

## Out of Scope *(mandatory)*

- Redesign do editor (009), do acompanhamento (011) e do shell administrativo;
  propagação deliberada da identidade para áreas administrativas (D6).
- Páginas 403, 404 e 500, **se** o plan concluir que são globais e inseparáveis das áreas
  administrativas (D8).
- Qualquer mudança funcional da 014 ou da 008 (FR-036): quatro ações, salvamento,
  pendência × erro, trajetória, ordem, escala funcional, alvos, política sem JavaScript,
  ramificações, conteúdo do instrumento.
- Barra gov.br, VLibras, modo escuro e modo de alto contraste próprios (D-02; QF-6).
- Ligações de privacidade, acessibilidade e contato no rodapé (QF-5).
- Identificação da pessoa e "Sair" no cabeçalho de produção (QF-1; 004/DP-406).
- Logotipo próprio do produto; fonte externa (Open Sans, Rawline, Inter); framework CSS;
  biblioteca de ícones; ilustrações; animações.
- Infraestrutura de arquivos estáticos, salvo necessidade demonstrada no plan (FR-018).
- Mecanismo de alternância A/B em tempo de execução (FR-012).
- Retrato de Egresso, compartilhamento, histórico, analytics.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

**Herdadas e afetadas por esta feature** (mantidas abertas; tratamento provisório
indicado):

- **008/DP-801** — DECISÃO PENDENTE: identidade visual e linguagem institucionais
  definitivas. Instância competente: Proex/CPAEG, com a comunicação institucional (ACS)
  e a TI. Impacto: toda a feature. Tratamento provisório: esta feature implementa a
  direção da auditoria como código de produção; a propagação depende da decisão.
- **Auditoria D-02** — DECISÃO PENDENTE: como o Padrão Digital de Governo (Portaria
  SECOM 7.508/2022; guia oficial do SISP) se aplica ao Trajetória e qual margem existe
  para a identidade visual do Ifes, inclusive barra gov.br e VLibras. Instância
  competente: Proex/CPAEG com a TI e a ACS. Impacto: FR-002, FR-011 a FR-014, FR-034.
  Tratamento provisório: Direções A e B pelo mesmo ponto de troca; **Direção B** mantida
  no código mergeado (FR-014); a Direção A é produzida e comparada no gate.
- **Auditoria D-03** — DECISÃO PENDENTE: (a) formato digital oficial (SVG) da assinatura
  sistêmica — o ZIP oficial não o contém; (b) uso em publicação e produção. Instância
  competente: ACS. Impacto: FR-015, FR-017, SC-001. Tratamento provisório: (a) SVG
  **derivado do EPS oficial e aceito pelo solicitante** (2026-10-03), usado sem alteração
  (research R3); a troca por um SVG da ACS é a substituição de um arquivo; (b) uso local,
  interno e não publicado, respeitando o Manual da Marca.

**Validação posterior registrada (não é decisão institucional)**: revisão perceptiva do
reconhecimento como produto do Ifes (FR-043).
