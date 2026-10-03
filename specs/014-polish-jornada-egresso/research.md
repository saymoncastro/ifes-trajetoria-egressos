# Research: Polish consolidado da jornada do egresso

Decisões técnicas da Fase 0. A spec não deixou nenhum `NEEDS CLARIFICATION`; cada item
abaixo escolhe **como** cumprir um grupo de requisitos, com a alternativa descartada. As
soluções candidatas da spec (N1 a N7) foram reavaliadas aqui; nenhuma é aceita só por
estar na spec.

Base verificada: `main` em `e89ca8d`; código de `trajetoria/interface` igual ao do polish
`226ca93`.

---

## R1 — "Salvar e sair": segundo botão de envio no mesmo formulário

**Decisão.** Um segundo `<button type="submit" name="depois" value="sair"
class="secundario">Salvar e sair</button>` no formulário da Seção, depois de "Salvar e
continuar". A view `_salvar` segue exatamente o caminho atual (forma → 005 → 006). Só no
último passo de um envio **aceito**, se `request.POST.get("depois") == "sair"`, redireciona
para `/formacoes/?aviso=<código>` em vez do destino da 006. O código vem de R3.

**Motivo.** O botão só envia o par `depois=sair` quando é ele que dispara o envio; com
"Salvar e continuar" o campo não vai. Assim os dois botões compartilham validação,
atomicidade (008 FR-045), concorrência, idempotência e as telas de estado (já respondida,
período encerrado, fora do percurso), sem duplicar nada (FR-011). O nome `depois` não
colide com os campos `p<n>`, e o formulário da Seção não o declara, então ele é ignorado
pela validação e pela gravação (008 FR-046).

**Alternativas descartadas.**
- Rota própria `POST …/secoes/<n>/sair/`: duplicaria a view ou exigiria refatorá-la, sem
  ganho.
- `formaction` no botão: a rota alternativa teria o mesmo problema.
- Campo oculto com a intenção: não distingue qual botão foi tocado.

---

## R2 — Enter/"Ir": botão de envio padrão desabilitado

**Decisão.** Primeiro elemento do formulário da Seção:
`<button type="submit" disabled hidden>Salvar</button>`. É o "botão padrão" do formulário
(primeiro botão de envio na ordem do documento). Como está desabilitado, o envio implícito
não acontece, nem para "Salvar e continuar" nem para "Salvar e sair".

**Evidência (C5 da spec).**
- **WebKit** (`HTMLFormElement::submitImplicitly`, `main`): percorre os elementos e
  dispara um clique simulado no primeiro botão de envio, e então retorna. O tratamento
  de ativação de `HTMLButtonElement` ignora o clique quando o controle está desabilitado.
  Não exige `renderer`, então `hidden` (`display: none`) não afeta o resultado.
- **Blink** (`HTMLFormElement::SubmitImplicitly`, `main`): com o primeiro botão de envio
  desabilitado, retorna explicitamente ("Default (submit) button is not activated; no
  implicit submission"). Também não exige estar renderizado.
- **Especificação HTML** (envio implícito): se o botão padrão está desabilitado, o envio
  implícito não envia o formulário.

**Efeitos colaterais verificados.**
- `hidden` + `disabled`: fora da ordem de foco e da árvore de acessibilidade (FR-017).
- O texto "Salvar" existe só para o verificador da 008 ("botão sem texto"); não é exibido.
- Nenhuma regra de estilo pode dar `display` a `button` de forma que anule `[hidden]`;
  hoje nenhuma dá. O teste estrutural (R13) fixa isso.
- ~~Enter num rádio ou numa caixa usa o mesmo mecanismo de envio implícito e fica
  bloqueado do mesmo jeito.~~ **Hipótese incorreta** — ver "Correção após evidência"
  abaixo.
- Enter ou Espaço com o foco num botão visível continua acionando-o (ativação direta,
  não envio implícito).
- Os outros formulários da jornada (entrada, conclusão, encerrar demonstração) não têm
  campo de texto e não mudam.

**Validação.**
- Estrutural, automatizada: o primeiro botão de envio do formulário da Seção está
  desabilitado.
- Comportamental, durante a implementação: navegador Chromium do painel (quickstart).
- iOS/Android, rótulo da tecla e versões antigas do WebKit: [T] (FR-050).

**Correção após evidência de comportamento real do Chromium (2026-10-03, implementação).**
- **Blink/Chromium bloqueia** o envio implícito pelo botão padrão desabilitado nos campos
  de digitação testados: campo de texto curto (ano, Seção 3) e descrição de "Outro"
  (Seção 8), com Enter de teclado físico. Antes do bloqueador, o mesmo Enter no ano
  enviava a Seção.
- **Com o foco num rádio ou numa caixa de seleção**, Enter **pode pular** o botão
  desabilitado e acionar o envio seguinte ("Salvar e continuar"). Observado no Chromium
  e coerente com o código do Blink: o retorno antecipado ("Default (submit) button is not
  activated") só vale quando o Enter vem de um controle que dispara envio implícito
  (campos de texto); vindo de rádio ou caixa, a busca continua até o próximo botão
  habilitado.
- **WebKit** parece ter comportamento diferente pelo código inspecionado
  (`submitImplicitly` dispara o clique no primeiro botão de envio, desabilitado, e
  retorna, sem distinguir a origem). **Sem validação física** (FR-050).
- Consequência: FR-016, US3 e SC-005 foram restritos aos campos de digitação, que é o
  problema do MF-02 (tecla "Ir" do teclado virtual). Enter em rádio ou caixa com teclado
  físico fica como limitação conhecida, anterior à 014; Espaço é a interação convencional
  para marcar; **não** se introduz JavaScript só para isso. A solução do MF-02 não muda.

**Alternativas descartadas.**
- `enterkeyhint`: só muda o rótulo da tecla; não impede o envio.
- JavaScript interceptando Enter: proibido (FR-043).
- Trocar `<input type="text">` por `<textarea>`: muda o controle de texto curto (008
  FR-035).

---

## R3 — Regra de verdade das mensagens de salvamento

**Decisão.** Um único predicado, calculado na view a partir das Respostas atuais que a
jornada da 006 já carrega:

```text
ha_resposta_na_secao = any(p.id in jornada.respostas for p in passagem.secao.perguntas)
```

- **Reapresentação com pendências** (GET com `?pendencias=1`): a frase "O que você
  respondeu nesta seção está salvo." aparece só se `ha_resposta_na_secao`. O indicador
  `&salvo=1` deixa de ser emitido e de ser lido (resolve UX-13).
- **Saída por "Salvar e sair"**: depois de gravar, a view relê a jornada (já faz isso
  hoje) e redireciona com `?aviso=salvo` se `ha_resposta_na_secao`; senão, com
  `?aviso=saida`.

**Motivo.** Usa o que está gravado e nenhum estado novo (FR-008, FR-042). Funciona igual
para envio aceito sem mudança (as Respostas anteriores continuam gravadas: a frase é
verdadeira), para remoção de todas as Respostas (o predicado fica falso) e para reenvio
repetido (o segundo envio não muda nada, e o predicado continua o mesmo).

**Risco aceito.** `/formacoes/?aviso=salvo` pode ser digitado à mão e mostrar a frase sem
envio. É o mesmo modelo dos códigos `?aviso=situacao` e `?pendencias=1` da 008:
lista fechada, sem dado pessoal, autoinfligido, sem efeito sobre o que está gravado.
Assinar o código seria infraestrutura desproporcional (Const. XXII).

**Alternativas descartadas.**
- Mensagem única e sempre verdadeira ("O que você respondeu até agora está salvo"):
  ambígua quando nada foi respondido; o solicitante pediu para não sugerir salvamento.
- Calcular pelo `ResultadoDaGravacao.operacoes`: diz se algo **mudou**, não se algo está
  **salvo**. Daria mensagem neutra para quem reenviasse sem mudança uma Seção já salva.
- Mensagem por sessão do Django: a 008 não usa sessões (R4 da 008) e não usará.

---

## R4 — Pendência e erro de forma: a mesma estrutura com outro "modo"

**Decisão.** A view informa ao template o tipo do resumo: `"pendencias"` (GET com
pendências) ou `"erros"` (resposta de POST com erros de forma ou rejeições da 005). Os dois
nunca coexistem (C3). Com esse único valor, os templates trocam:

| Elemento | Erro de forma (atual) | Pendência (novo) |
|---|---|---|
| Prefixo do título da página | `Erro: ` | `Faltam respostas: ` |
| Título do resumo | "Há problemas nesta seção" | "Ainda faltam estas perguntas:" |
| Frase de salvamento | não se aplica (nada gravado) | só com `ha_resposta_na_secao` (R3) |
| Marca por Pergunta | `Erro: <mensagem>` | `Falta responder: <mensagem>` |
| Destaque visual | borda vermelha | borda azul institucional (`#1a4480`, contraste já documentado) |
| `role="alert"`, ligações, `aria-invalid`, `aria-describedby` | mantidos | mantidos |

**Motivo.** Só apresentação. `aria-invalid="true"` continua correto para obrigatória
vazia (é inválida segundo a validação de restrições do HTML), e o verificador da 008 o
exige quando há id `-erro`. Os ids `-erro` ficam iguais para não mexer em
`aria-describedby`.

**Ajuste necessário no verificador da 008** (`test_interface_acessibilidade.py`): a regra
"há `role="alert"` ⇔ título começa por `Erro:`" passa a ser "há `role="alert"` ⇔ título
começa por `Erro:` ou `Faltam respostas:`", e "`Erro:` ⇔ a tela é de erro de forma". É a
atualização de um teste que fixava o texto antigo, não uma regra de acessibilidade mais
fraca.

---

## R5 — Área ativável de Opções e pontos (MF-04)

**Decisão.** Só CSS, restrito a `.pergunta`:

```text
.pergunta .opcao            { position: relative; }
.pergunta .opcao label::after { content: ""; position: absolute; inset: 0; }
```

O pseudo-elemento do rótulo cobre a linha (rádio, caixa, "Deixar esta pergunta sem
resposta") ou a célula (escala) inteira. Tocar em qualquer ponto ativa o rótulo, que
ativa o controle associado (`for`).

**Verificações.**
- `.opcao` contém só o controle e o rótulo, nos templates de Pergunta (e também no
  `_campo.html` do editor, que fica **fora** do escopo `.pergunta` — FR-045). A
  descrição de "Outro" fica fora de `.opcao` e não é coberta.
- O contorno de foco é desenhado no próprio controle e continua visível (a camada é
  transparente).
- Sem mudança de HTML: o que é enviado não muda (FR-018).
- Alvo mínimo: as linhas já têm `min-height: 2.75rem` (≥ 44 px com fonte a 100%) e
  largura total; as células da escala ganham 44 px de largura mínima (R6).

**Alternativa considerada.** Envolver o controle no rótulo (`<label><input> texto</label>`).
Também é robusta, mas muda a marcação de três templates e os testes que leem `label for`,
sem ganho de comportamento.

---

## R6 — Escala em colunas que quebram alinhadas (MF-05)

**Decisão.**

```text
.pergunta .escala { display: grid; grid-template-columns: repeat(auto-fit, minmax(44px, 1fr));
                    max-width: 30rem; }
.pergunta .escala .opcao { flex-direction: column; align-items: center; }
```

O número fica abaixo do controle, na mesma coluna. A largura mínima é em **px**, não em
`rem`, porque o alvo de toque é físico e não deve crescer com a fonte (é o que faz a
escala caber com fonte a 200%).

**Cálculo de pior caso (320 px, fonte 200%, Pergunta com marca de erro).** Coluna útil
de 288 px, menos borda e recuo da marca (4 + 24 px) = 260 px. Cinco colunas × 44 px =
220 px. Cabe numa linha, com cerca de 52 px por coluna. O controle (1,25 rem = 40 px) e o
número (32 px de fonte, um dígito) cabem na coluna.

**Escalas longas (C6).** Com 11 pontos a 320 px, cabem 5 ou 6 colunas por linha; os
pontos quebram em linhas **alinhadas** (mesma grade), em ordem de leitura, sem rolagem
horizontal. `max-width: 30rem` evita que, no desktop, cinco pontos se espalhem pela
coluna toda.

**Alternativas descartadas.**
- `grid-auto-flow: column` (recomendação da auditoria): nunca quebra; transborda com
  escalas longas.
- `flex-wrap` com largura flexível: a última linha ficaria com colunas mais largas,
  desalinhando os pontos.
- Largura mínima em `rem`: a 200% a quinta coluna voltaria a cair para a linha de baixo.

---

## R7 — Grupo de rádios sem a caixa de remoção (UX-19)

**Decisão.** O `fieldset.pergunta` deixa de ter `role="radiogroup"` e `aria-required`;
mantém o `id` da âncora, a `legend` (agora com id `<nome>-enunciado`), `aria-describedby` e
`aria-invalid` (atributo global, válido em grupo). As Opções passam a ficar num invólucro
com `role="radiogroup"`, `aria-labelledby="<nome>-enunciado"` e `aria-required` quando
obrigatória:

- **escala**: o invólucro é o `div.escala` que já existe;
- **escolha única em rádios**: um `div.opcoes` novo em volta das Opções;
- **lista suspensa e escolha múltipla**: sem mudança.

A caixa "Deixar esta pergunta sem resposta" continua dentro do `fieldset` (a mesma
Pergunta, a mesma legenda), mas fora do invólucro.

**Motivo.** É a menor mudança que tira a caixa do grupo exclusivo sem perder a
obrigatoriedade exposta (`aria-required` não é permitido no papel implícito `group`).
O verificador da 008 continua satisfeito: rádios e caixas seguem dentro de
`fieldset`/`legend`.

**Risco [T].** Alguns leitores podem anunciar o enunciado duas vezes (grupo do
`fieldset` e `radiogroup`). Fica no roteiro de VoiceOver/TalkBack (FR-050, itens 7 e 8).

**Alternativa descartada.** Mover a caixa para fora do `fieldset`: ela perde a associação
com a Pergunta e com a marca de erro.

---

## R8 — Foco no resumo ao carregar, sem JavaScript (MF-10)

**Decisão.** O resumo ganha `tabindex="-1"` e o atributo global `autofocus`. Mantém
`role="alert"` (FR-028) e as ligações para as Perguntas.

**Verificações.**
- `autofocus` é atributo global no HTML atual, com foco aplicado no carregamento pelos
  motores atuais. Suporte e efeito em VoiceOver/TalkBack são [T].
- Só há um resumo por página (um único `autofocus`).
- Focar um `div` não abre teclado virtual. O resumo está no topo do conteúdo (FR-024),
  então o deslocamento até ele não passa do topo.
- O verificador da 008 não trata `div` como focável; "Pular para o conteúdo" continua
  sendo o primeiro.

**Ajuste na implementação (observado no Chromium).** Sem mais nada, a rolagem do foco
alinhava o topo do resumo ao topo da tela e escondia o título da Seção, contrariando a
FR-027 ("não deslocar a página para além do topo do conteúdo"). `scroll-margin-top: 8rem`
no resumo, só CSS, faz a rolagem do foco parar antes do título. A 375×667 com a faixa de
demonstração, a página nem chega a rolar: título e resumo ficam visíveis juntos.

**Alternativa considerada.** Âncora `#titulo-erros` no redirecionamento de pendências:
rola, mas não move o foco, e não serve para a resposta de POST com erros. Descartada.

---

## R9 — Títulos das telas (UX-07, UX-11)

**Decisão.**
- `secao.html`: `h1` = título da Seção ou, sem ele, `titulo_pesquisa` (já calculado, com
  "Pesquisa" como substituto). O `h2` da Seção some. O bloco `titulo` (aba) não muda.
- `conclusao.html`: `h1` = "Concluir a pesquisa"; o `h2` homônimo some; o contexto segue
  com o seu `h2`.

A ordem do topo (FR-024) já é quase a atual. Só o título da Seção sobe para o lugar do
`h1`.

---

## R10 — Rodapé: hierarquia, largura e separação (MF-06, MF-14)

**Decisão.**
- Dentro do formulário: o botão bloqueador (R2), as Perguntas e `div.acoes.acoes-secao`
  com "Salvar e continuar" (`primario`) e "Salvar e sair" (`secundario`).
- Fora do formulário: `div.saidas` com as ligações "Voltar à seção anterior" (com a nota
  atual) e "Sair sem salvar esta seção" (com a nota "O que já foi salvo antes continua
  guardado.").
- Estilo, só com as classes novas:
  - `.acoes-secao` em coluna, com `button` em `width: 100%` sob `@media (max-width: 30em)`
    (480 px com fonte padrão);
  - `.saidas` com `margin-top: 2rem`, `padding-top: 1rem` e `border-top: 1px solid
    #565c65` (≥ 32 px até a primeira ação terciária) e fonte da `.nota`.

**Motivo.** Ações de envio dentro do formulário, ações de navegação fora, como hoje. A
ordem do documento já é a ordem de foco exigida (FR-009). `.acoes` continua existindo
para o editor sem mudança (FR-045).

---

## R11 — Trajetória e formações (ID-03, ID-04, ID-11, ID-12, ID-14)

**Decisões.**
- **Título**: todas as entradas de `_TELA_DE_FORMACOES` passam a ter "Sua trajetória no
  Ifes"; as mensagens de estado continuam.
- **Formação apresentada** (`_formacao_apresentada`):
  - `linha` = `resumo_da_formacao(conclusao)`, a função existente, sem mudança (FR-034);
  - `complemento` = nova função pequena em `apresentacao.py`, `" · ".join` de nível,
    modalidade e forma de oferta informados;
  - `situacao` = texto de `SITUACAO_DA_FORMACAO`, que passa a não ter texto para
    `SEM_PESQUISA` (`None` → não exibido);
  - `acao` como hoje.
- **Entrada resolvida**: "Você concluiu {linha}." (sem linha: "Encontramos uma formação
  sua no Ifes.") + "O Ifes quer saber como sua trajetória seguiu depois disso." + frase
  de FR-002 + botão. A frase reutiliza a linha e não precisa de gramática com partes
  ausentes nem da palavra "campus" (FR-032).
- **Seleção necessária**: "Cada formação tem sua própria pesquisa. Escolha por qual
  começar ou continuar; as outras continuam disponíveis aqui." Cada formação pendente em
  `li`, com linha, complemento, situação e botão.
- **Outras formações**: mesma forma compacta; situação só quando há texto.
- **Ordem**: a de `situacao.formacoes` e `situacao.pendentes`, sem `sorted` (FR-035).
- **Ligações** "Voltar às suas formações" → "Ver sua trajetória no Ifes" em `aviso.html` e
  `concluida.html`.
- **`dados_formacao.html`** continua em uso no contexto completo (conclusão, confirmação,
  telas de estado). Só a tela de formações deixa de usá-lo.

**Medida (SC-010).** Maria a 375×667, descontados os 231 px de demonstração: `h1` (2
linhas) + frase (3 linhas) + duas formações com 2 linhas, situação e botão. A primeira
ação fica bem acima de 667 px.

---

## R12 — Confirmação e textos fixos (ID-09, UX-18, MF-09, ID-06)

**Decisões.**
- **`concluida`**: a view passa `curso = participacao.conclusao.curso`.
  - Template: "Suas respostas sobre {curso} foram registradas." ou "Suas respostas foram
    registradas.".
  - "Obrigado pela sua participação." só com `{% if not texto_encerramento %}`.
  - O contexto completo continua (008 FR-027).
- **`403_csrf.html`**: "Volte à página anterior e envie novamente.".
- **`contexto_compacto.html`**: rótulo "Você está respondendo sobre:".
- **`formacoes.html`**: a frase de FR-002 substitui a frase operacional atual.
- **`conclusao.html`**: a lista de Seções ganha a classe `lista-secoes`, com ligações em
  bloco e `min-height: 2.75rem` (FR-026).
- **`mensagens.py`**: novos textos `AVISOS["salvo"]`, `AVISOS["saida"]`, títulos e
  marcas de pendência. Todos provisórios (DP-801).

---

## R13 — Estratégia de testes

Mesma abordagem da 008: requisições HTTP com `django.test.Client`, sem JavaScript,
operações reais e Pessoas da fonte simulada.

| Arquivo | Novo ou ajustado | Cobre |
|---|---|---|
| `tests/interface/test_interface_rodape.py` | **novo** | Matriz de comportamento do rodapé: 8 estados × 2 ações de envio, mais destino das 2 ligações e presença na reapresentação com erro (FR-009 a FR-014, SC-003, SC-004, SC-015); R3 (SC-002); estrutura de R2: primeiro botão de envio desabilitado, os dois botões nomeados (FR-016, FR-017) |
| `test_interface_secao.py` | ajustado | `h1` da Seção e substituto; linha "Você está respondendo sobre:"; marca de pendência × erro; R7 (`radiogroup` só com Opções; remover fora) |
| `test_interface_navegacao.py`, `test_interface_aceitacao.py` | ajustados | Redirecionamento de pendências sem `&salvo=1`; E2E-1 a E2E-4 |
| `test_interface_gravacao.py` | ajustado | Título "Há problemas" só com erro de forma |
| `test_interface_formacoes.py`, `test_interface_encerramento.py` | ajustados | Título, frases, forma compacta, ordem = 007, "sem pesquisa" omitido, ambiguidade mantida, aviso de saída (SC-011) |
| `test_interface_conclusao.py` | ajustado | `h1` "Concluir a pesquisa"; agradecimento único com e sem encerramento; curso ausente (SC-012) |
| `test_interface_acessibilidade.py` | ajustado | Regra de título de R4; novos estados (pendência sem e com Resposta gravada, trajetória com aviso); foco no resumo (`autofocus` + `tabindex`) |
| `tests/editor/test_editor_previa.py` | ajustado se necessário | A prévia continua passando com a nova marcação de R7 |

**Fora do pytest** (sem navegador automatizado, decisão mantida da 008): medições de
SC-005 a SC-010 e SC-014 pelo quickstart, no painel de navegador (Chromium) com viewport
emulada e fonte raiz alterada, como fez a auditoria mobile.
