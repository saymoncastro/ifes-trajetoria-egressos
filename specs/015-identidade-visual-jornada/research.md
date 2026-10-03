# Research: Foundations e validação da identidade visual da jornada do egresso

Decisões técnicas do plan da Feature 015. Base: spec (FR-001 a FR-047, SC-001 a SC-014),
[auditoria de identidade visual](../../docs/auditorias/2026-10-03-identidade-visual.md) e o
código em `claude/feature-015-identidade-visual`, sincronizada com a `main` em `b4476ce` (inclui a correção IV-03, PR #23).

---

## R1 — Onde vivem as foundations e como a mudança fica restrita à jornada

**Fatos verificados.**

- `interface/estilo.css` é incluída inline por `interface/base.html` (jornada e
  demonstração), por `editor/base.html` e `acompanhamento/base.html` (que somam suas
  próprias folhas) e por `403_csrf.html`, `404.html`, `500.html`.
- Classes da jornada **também usadas** pelo editor/acompanhamento: `.aviso`,
  `.lista-simples`, `.cabecalho`, `.faixa-demonstracao`, `.acoes`, `.primario`,
  `.secundario`, `.botao`, `.nota`, `.resumo-erros` (editor `_erros.html`), e os
  elementos `a`, `button`, `h1`–`h3`, `input`, `select`, `footer`.
- Classes **só da jornada** (e da prévia, quando de Pergunta): `.pergunta`, `.escala`,
  `.opcoes`, `.com-pendencia`, `.resumo-pendencias`, `.contexto`, `.contexto-compacto`,
  `.formacao`, `.acoes-secao`, `.saidas`, `.lista-secoes`. O `.opcao` do editor
  (`_campo.html`) não está dentro de `.pergunta`.

**Decisão.** Duas camadas, sem duplicar regra:

1. **`interface/estilo.css` (compartilhada)** recebe só:
   - o bloco `:root` com **todos os tokens** (FR-001) — definir propriedades
     personalizadas não muda nada visualmente onde elas não são usadas;
   - as mudanças das regras **escopadas em `.pergunta`** (ritmo interno, tipografia,
     estados, escala), que valem para a jornada **e** para a prévia do editor (FR-040);
   - as regras já exclusivas da jornada (`.com-pendencia`, `.resumo-pendencias`) passam
     a usar tokens no lugar.
2. **`interface/jornada.css` (nova, só da jornada)**, incluída inline **apenas** por
   `interface/base.html`, depois da compartilhada: shell (cabeçalho, rodapé, faixa),
   ligações e botões da jornada, avisos com variantes, item de formação, contexto,
   resumo, ação principal em largura total, divisores suaves. Como só a jornada a inclui,
   ela pode refinar classes compartilhadas (`.aviso`, `.lista-simples`, `a`, `button`)
   sem alcançar o editor nem o acompanhamento.

**Regra verificável (teste, R9):** em `estilo.css`, nenhum seletor usado pelo
editor/acompanhamento (lista acima) passa a usar token; todo uso de `var(--…)` fica em
`:root`, em seletores sob `.pergunta`/`.escala`/`.opcoes` ou em classes só da jornada.

**Motivo.** Garante FR-040 (editor e acompanhamento sem mudança) **por construção** — as
páginas administrativas não carregam a camada da jornada —, sem condicional nem
duplicação (FR-038, FR-039). Segue a precedência existente: o editor já soma
`editor/estilo.css`, e o acompanhamento, três folhas.

**Alternativas consideradas.**
- *Uma folha com seletores prefixados por uma classe no `<body>` da jornada*: funciona,
  mas espalha o prefixo por dezenas de regras e torna a fronteira menos óbvia na revisão.
- *Mover para `jornada.css` as regras existentes só da jornada*: refatoração sem ganho
  para esta feature; elas ficam onde estão e só trocam valores por tokens.
- *`staticfiles`*: vedado sem necessidade (008 R14; FR-018).

---

## R2 — Tokens e a troca A/B pelos dois tokens de ação

**Decisão.** Propriedades personalizadas CSS no `:root` de `estilo.css`, com o contraste
em comentário ao lado de cada cor (prática de IV-P9). Nomes em
[contracts/tokens.md](contracts/tokens.md). A Direção é definida por **duas linhas**:
`--cor-acao` e `--cor-acao-forte`. Nenhum outro token, regra ou template conhece a
Direção; nenhum código Python, template ou parâmetro a lê.

- Valor mergeado: **Direção B** (`#1351b4` / `#0c326f`) — FR-014.
- Para gerar a Direção A durante a validação: editar as duas linhas (`#195128` /
  `#00420c`), capturar, e restaurar B antes do commit (quickstart §4).
- `--cor-sucesso` (`#195128`) e `--cor-marca` (`#2f9e41`) são tokens **próprios**, fixos
  nas duas direções (spec, FR-002) — mesmo quando o valor coincide com a Direção A, não
  são aliases de `--cor-acao`.

**Motivo.** Cumpre FR-011 a FR-014 e SC-010 sem mecanismo de execução (FR-012). Suporte
a propriedades personalizadas: todos os navegadores-alvo (Safari ≥ 9.1, Chrome ≥ 49).

**Alternativas.** Variável de ambiente ou contexto de template para a cor — vedado
(FR-012). Duas folhas "tema A" e "tema B" — duplicação (FR-038).

---

## R3 — Assinatura oficial: arquivo, forma de inclusão e autorização

**Download autorizado e feito em 2026-10-03** (solicitante), fora do repositório, só para
inspeção.

| Item | Valor |
|---|---|
| Origem | <https://www.ifes.edu.br/download-de-marcas> — "Ifes - marca sistêmica", indicada "para utilização em materiais da Reitoria ou que envolvam mais de um campus"; dúvidas e "formatos diferenciados" via acs@ifes.edu.br |
| Arquivo | `marca-ifes.zip` — `https://www.ifes.edu.br/images/stories/files/Institucional/assessoria_comunicacao_social/marcas/marca-ifes.zip` |
| Tamanho / data | 10.921.436 bytes; modificado no servidor em 06/03/2026 |
| SHA-256 do ZIP | `3834b6e8c25463f84cbf22bc50e9095cb7f3737ccd459e6cf84d0aee58121a12` |
| Conteúdo (28 entradas) | `_ifes/eps/`, `_ifes/jpg/`, `_ifes/png/` — assinaturas **horizontal** e **vertical** nas versões `cor`, `pb`, `preto` e `branco` (JPG sem `branco`); dois `Thumbs.db` |
| **SVG** | **Não há** |
| Ativo que seria o adequado | `_ifes/eps/ifes-horizontal-cor.eps` (Adobe Illustrator 26.0, 21/01/2022, caixa 708,66 × 283,46 pt; SHA-256 `ca2d265287cdb3d1949b6cf1f1a20639aadb75b3fb45b73377452986d3c01b6e`) e seu raster `_ifes/png/ifes-horizontal-cor.png` (2835 × 1134 px, 288 dpi; SHA-256 `589e9a96a017347b1442e2957a490d35516b0b1eb75f7a1c878d60b6f7903bde`) |
| Conferência visual (PNG) | Símbolo IF (círculo vermelho + módulos verdes) + "INSTITUTO FEDERAL" / "Espírito Santo"; sem linha de campus — é a marca sistêmica. O arquivo já inclui margem branca em volta (área de proteção embutida); o símbolo ocupa ≈ 57% da altura do arquivo |

**Decisão: a parte da assinatura está bloqueada por D-03** (regra do solicitante: sem SVG
oficial adequado, parar). Não se usa o PNG, não se converte o EPS para SVG e não se
reconstrói a marca. Fica registrado:

1. **Pedido à ACS** (acs@ifes.edu.br, canal indicado pela própria página para "formatos
   diferenciados"): a assinatura **horizontal colorida da marca sistêmica em SVG**, para
   uso digital em tela, mencionando o arquivo de origem acima. O envio do pedido é ação do
   solicitante (comunicação externa).
2. **Quando o SVG oficial chegar:** registrar nome, origem e SHA-256 aqui; incluir o ativo
   **exatamente como recebido** como template `interface/assinatura.svg`, por
   `{% include %}` inline (mesmo mecanismo da folha de estilo; sem `staticfiles`, sem
   requisição externa — FR-018). Nenhuma otimização que altere o conteúdo da marca; o
   nome acessível ("Instituto Federal do Espírito Santo") vai no elemento que envolve o
   SVG, não dentro do ativo.
3. **Dimensionamento** (a confirmar com o SVG recebido): se o ativo mantiver a margem
   embutida do PNG/EPS (símbolo ≈ 57% da altura), símbolo ≥ 30 px exige o ativo com
   ≈ 53 px de altura; com o fio de 4 px, respiros de 2–3 px e o divisor de 1 px, o
   cabeçalho fica em ≈ 62–64 px a 375 px — no limite de FR-016. Se o limite não couber,
   é achado do gate (corrigir na mesma branch, nunca encolher a marca abaixo do mínimo
   nem recortar a área de proteção).
4. **Sem o ativo, a 015 não passa no gate** (SC-001 exige a assinatura). Todo o resto da
   feature pode ser implementado e medido; o cabeçalho é construído sem a assinatura
   (nenhum marcador provisório, desenho substituto ou imagem fictícia — FR-038) e o
   ativo entra numa tarefa própria.

**Alternativas rejeitadas (por regra do solicitante):** usar o PNG oficial embutido;
converter o EPS para SVG; redesenhar. Ficam registradas só para a decisão de D-03, caso a
ACS não forneça SVG — essa decisão volta ao solicitante.

---

## R4 — Shell da jornada: cabeçalho, faixa e rodapé

**Decisão** (estrutura em [contracts/shell.md](contracts/shell.md)):

- **Faixa de demonstração** (`.faixa-demonstracao`, cor `#fff1d2` inalterada) passa a
  conter **também** os controles de demonstração ("Pessoa fictícia: …", "Trocar de
  pessoa", "Encerrar demonstração"), que hoje estão no cabeçalho. Textos, ordem, destinos
  e o formulário de encerramento não mudam. Assim o cabeçalho do produto é medível sem
  descontos artificiais (FR-016, FR-021).
- **Cabeçalho do produto**: fio de 4 px `--cor-marca` no topo (borda superior); fundo
  branco; linha com assinatura (SVG) → separador vertical 1 px `--cor-borda-suave` →
  "Trajetória Ifes" (18 px/700) e, a partir de 30 em, "Acompanhamento de egressos"
  (15 px, `--cor-texto-suave`); divisor inferior 1 px suave. Sem navegação, sem `h1`
  (o `h1` continua o título da página).
  - Orçamento a 375 px: 4 (fio) + 12 + ~32 (assinatura) + 12 + 1 ≈ **61 px** ≤ 64.
  - A 1280 px: padding 16 → ≈ 69 px ≤ 80.
  - 320 px com fonte a 200%: o grupo de texto quebra para baixo da assinatura
    (`flex-wrap`); a assinatura nunca encolhe abaixo do mínimo; sem rolagem horizontal.
- **Rodapé**: "Instituto Federal do Espírito Santo" (15 px, `--cor-texto-suave`), divisor
  superior suave; em demonstração, a linha atual de ambiente fictício continua abaixo.
- O cabeçalho e o rodapé ficam em `interface/base.html`; por herança, valem para
  trajetória, Seções, conclusão, confirmação, telas de estado (`aviso.html`) e para
  entrada e operador da demonstração (D7).

**Motivo.** Auditoria §17; FR-015 a FR-021.

**Alternativa.** Manter os controles de demonstração dentro do cabeçalho numa segunda
linha — infla o cabeçalho e exigiria descontá-los da medida; a faixa já é a área "não
produto".

---

## R5 — 403, 404 e 500 ficam fora da 015 (D8)

**Fato verificado.** `config/urls.py` não define `handler404`/`handler500`, e não há
`CSRF_FAILURE_VIEW` próprio: o Django usa `404.html`, `500.html` e `403_csrf.html` para
**todo** o sistema — inclusive `/editor/` e `/acompanhamento/`, e para qualquer rota quando
o modo de demonstração está desligado (`ModoDemonstracaoMiddleware`).

**Decisão.** São **globais e inseparáveis** sem lógica nova (escolher o template pela
rota seria condicional criada só para a fronteira). Pela regra de D8/FR-020, **não mudam
nesta feature**: continuam incluindo só `estilo.css` (a camada `jornada.css` não chega a
elas), e o shell nelas fica para a propagação transversal. A única mudança que as alcança
é a definição de tokens no `:root`, sem efeito visual.

**Registro para a propagação futura:** essas três páginas são o primeiro item quando o
shell for estendido às áreas administrativas.

---

## R6 — Questionário: ritmo, tipografia e estados dos controles

**Decisão** (regras em `estilo.css`, escopadas em `.pergunta`, valendo para a jornada e
a prévia):

- **Ritmo:** `.pergunta` com margem inferior de 48 px; enunciado → resposta 8 px
  (FR-022).
- **Tipografia:** `legend`/`label.enunciado` 18 px, peso 600, entrelinha 1,4;
  `.explicacao`, `.descricao-escala`, `.obrigatoria` e a nota "(marque todas que se
  aplicam)" em 15 px, `--cor-texto-suave` (FR-023). Nenhum texto muda.
- **Controles marcados:** `accent-color: var(--cor-acao)` nos rádios e caixas.
- **Estado selecionado:** linha/célula com controle marcado (`:has(input:checked)`) ganha
  marca de acento de 4 px na cor de ação (≥ 3:1) e fundo `--cor-selecao` (tonal,
  complementar), **sem deslocar o conteúdo** e sem reduzir a área ativável. Sem suporte a
  `:has` (Safari < 15.4, Chrome < 105, Firefox < 121), resta o controle marcado — que
  sempre foi o sinal principal (degradação aceitável).
- **Hover:** fundo `--cor-selecao` na linha/célula sob o ponteiro (apenas
  `@media (hover: hover)`).
- **Escala:** cada `.escala .opcao` com contorno 1 px `--cor-borda-forte` (6,7:1) e raio
  `--raio`; vão horizontal de 4 px entre células. Verificação de capacidade: 5 células de
  44 px + 4 vãos de 4 px = 236 px ≤ 288 px úteis a 320 px — a escala de 1 a 5 continua
  numa linha com fonte a 200% (as colunas são em px, 014 R6).
- **Cores forçadas:** fundos tonais somem; contornos e controles nativos permanecem
  (nenhum significado depende do fundo — FR-025).

**Prévia do editor — interpretação de FR-040.** A prévia herda tipografia, estados e o
espaço enunciado → resposta. O espaço **entre** Perguntas na prévia continua o do editor
(`.previa .pergunta { margin-bottom: 0.5rem }` + lista de anotações intercalada, 009),
porque ali cada Pergunta é seguida de anotações do editor. Alterar isso seria mudar a
tela do editor (FR-040). Ver "Conflitos" no plan.

---

## R7 — Feedback: avisos, pendência, erro, foco do resumo, confirmação

**Decisão** (em `jornada.css`, salvo indicação):

- **Avisos com variante por código** (lista fechada, C6): a view já escolhe o código;
  o template recebe também a variante (`sucesso` para `salvo`; `informacao` para `saida`,
  `situacao`, `percurso`) por um mapa fixo em `mensagens.py`, ao lado de `AVISOS`. Classe
  `aviso aviso-sucesso` / `aviso aviso-informacao`; fio de 4 px à esquerda na cor do
  papel; texto inalterado. O `.aviso` do editor não é tocado (só a jornada carrega
  `jornada.css`).
- **Pendência/erro:** tokens `--cor-info` e `--cor-erro` nas regras existentes
  (`estilo.css`, já exclusivas da jornada); acento uniformizado em 4 px (o contorno do
  resumo passa de 3 px a um fio lateral de 4 px + contorno 1 px na cor do estado —
  forma idêntica para os dois tipos, cor diferente; o título e o prefixo distinguem sem
  cor). IV-03 já está na baseline.
- **Foco do resumo (FR-028):** `.resumo-erros:focus` recebe o mesmo contorno + halo de
  `:focus-visible` (o foco programático por `autofocus` não ativa `:focus-visible`).
- **Confirmação (FR-029):** o bloco do topo de `concluida.html` (`h1` + frase de
  registro) recebe fio de acento de 4 px `--cor-sucesso`. Sem ícone, animação ou texto
  novo.
- **Ícones (FR-030): nenhum nesta versão.** Todo estado já tem texto; ícones ficam como
  hipótese a avaliar no registro de validação, sem biblioteca.

---

## R8 — Trajetória, contexto, ação principal e divisores

**Decisão** (em `jornada.css`; marcação mínima nos templates da jornada):

- **Item de formação:** `.formacao strong` peso 600; complemento 15 px
  `--cor-texto-suave`; situação (`<p>` hoje em `<strong>` em "Suas outras formações")
  passa a peso 400 — **mudança de marcação**: `<strong>` → `<span class="situacao">`, sem
  mudar texto, ordem ou presença (FR-031); espaço do item simétrico (padding 16/16, sem
  margem final do último parágrafo); divisor `--cor-borda-suave`.
- **Frase de entrada:** a linha da formação dentro de "Você concluiu …" vai em
  `<strong>` (FR-032). Hoje a frase vem pronta de `entrada_fato`; a view passa a separar
  prefixo e linha, mantendo o texto final idêntico (verificado por teste).
- **Ação principal em largura total até 30 em** (FR-033): botões `primario` dos
  formulários de entrada da trajetória e de conclusão.
- **Contexto e ficha (FR-034):** `.contexto` com fio de 4 px `--cor-marca` e fundo
  `--cor-institucional`; a ficha (`dl`) empilha rótulo/valor até 30 em (mesmo padrão de
  `.dados` do acompanhamento, reescrito para `.contexto dl`).
- **Divisores (FR-035):** `.lista-simples > li`, `.saidas`, rodapé e cabeçalho com
  `--cor-borda-suave`; campos, células e controles com `--cor-borda-forte`.
- **Ligações e botões da jornada:** `a` em `--cor-acao`; `button.primario` com fundo
  `--cor-acao` e hover/ativo `--cor-acao-forte`; `button.secundario` com borda e texto
  `--cor-acao`.

---

## R9 — Estratégia de testes

**Decisão.** Testes por HTTP (sem navegador), como na 014, num arquivo novo
`tests/interface/test_interface_identidade.py`, reaproveitando o leitor de cascata
criado no IV-03 (movido para `tests/interface/construcao_interface.py`):

| O que comprova | Como |
|---|---|
| `jornada.css` presente em trajetória, Seção, conclusão, confirmação, telas de estado, entrada e operador da demonstração; **ausente** em editor, acompanhamento, 403, 404, 500 (FR-020, FR-040; R1, R5) | Conteúdo do `<style>` das respostas |
| Troca A/B só nos dois tokens de ação: `--cor-acao` e `--cor-acao-forte` definidos **uma vez**; os valores hex das Direções A e B não aparecem fora dessas definições e de `--cor-sucesso`; nenhum `.py`/template referencia os tokens de ação (FR-011, FR-012) | Leitura das folhas e busca no código |
| Verde da marca só em fio/borda: `--cor-marca` nunca em `color` nem `background` (FR-003) | Regras da folha |
| Seletores compartilhados com o admin sem tokens em `estilo.css` (R1) | Regras da folha × lista de seletores compartilhados |
| Papéis de cor: pendência → info; erro → erro; aviso `salvo` → sucesso; `saida`/`situacao`/`percurso` → informação (FR-026, FR-027) | Leitor de cascata + classes da página |
| Assinatura em toda tela da jornada, com nome acessível; nenhum recurso externo (`http`, `@import`, `url(` externo, `<script>`) (FR-017, FR-018, FR-037) | HTML das respostas |
| Textos inalterados: frase de entrada idêntica; situações idênticas (FR-031, FR-032, FR-036) | Testes da 014 existentes + asserções novas |

Os testes da 014 e da 008 continuam; ajustes só onde a marcação mudar de propósito
(controles de demonstração movidos para a faixa; `<strong>` da situação).

**Medições** (alturas, contraste renderizado, reflow, 200%, SCs mobile da 014, capturas
A/B, escala de cinza, regressão administrativa por comparação de capturas) ficam no
[quickstart](quickstart.md) e no registro de validação.

---

## R10 — Registro de validação (gate)

**Decisão (solicitante, 2026-10-03).** O **registro textual** fica no repositório:
`specs/015-identidade-visual-jornada/validacao.md`, no formato de
[contracts/registro-validacao.md](contracts/registro-validacao.md) — commit validado,
Direção, viewport, escala de fonte, tela/cenário, medidas, resultado por critério e um
**identificador** para cada captura. As **capturas não são versionadas**: são anexadas
ao PR da Feature 015 (comentário/descrição) ou mantidas como artefato externo da
validação, com o identificador do registro no nome ou na legenda. Se não houver mecanismo
persistente adequado para as capturas, a decisão volta ao solicitante antes de qualquer
versionamento. O registro é preenchido a cada rodada do gate; rodada reprovada gera
correções na mesma branch e nova rodada (spec, Princípio 2; FR-042).

**Alternativa rejeitada.** Diretório de JPEGs versionado no repositório — coleção
crescente de binários.

---

## R11 — Raio e divisor entre Perguntas (hipóteses decididas no gate)

**Decisão.** `--raio` começa em **4 px** e é comparado com 0 px na rodada 1 do gate
(campos, botões, avisos, células da escala, resumo), trocando só o token. O divisor entre
Perguntas começa **ausente**; é testado a 375 px na Seção 8 e só entra se o registro
mostrar que os 48 px sozinhos não separam (FR-024, FR-044). O valor perdedor não
permanece no código.

**Resultado (gate, rodada 1 — [validacao.md](validacao.md)):** raio **4 px**, aplicado ao
mesmo token em campos, listas, células da escala e botões da jornada (com 4 px só nas
células, a interface ficava incoerente); **sem divisor** entre Perguntas. Valores "a
calibrar" adotados sem ajuste: `--cor-institucional` `#eef7f0`, `--cor-selecao` `#f2f4f7`,
`--cor-borda-suave` `#c6cace`. Correção surgida no gate: títulos (`h1`, `h2`) da jornada
quebram palavras longas (`overflow-wrap: break-word`) — "Informações Pessoais" gerava
rolagem horizontal a 320 px com fonte a 200% (causa anterior à 015).
