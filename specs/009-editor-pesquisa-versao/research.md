# Research: Editor institucional de Pesquisa e Versão

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Date**: 2026-10-01

Não havia `NEEDS CLARIFICATION` no Technical Context: a stack é a existente (ADR 0001), e
as quatro decisões de produto foram consolidadas na seção *Clarifications* da spec. Cada
item abaixo registra uma decisão de desenho com justificativa e alternativas rejeitadas.

Fontes lidas no código:

- 002: `trajetoria/instrumento/operacoes.py`, `regras.py`, `conteudo.py`, `models.py`;
- 003: `trajetoria/formulario_2024/materializacao.py`;
- 006: `trajetoria/participacao/percurso.py`, `regras.py`;
- 008: `trajetoria/interface/*`, `trajetoria/demonstracao/*`, `config/*`;
- testes de fronteira das 007 e 008.

---

## R1 — Onde o editor vive: um app novo, sem modelos (`trajetoria/editor`)

**Decision**: criar o pacote Django `trajetoria/editor` com:

- `apps.py`, `urls.py`, `views.py` e `formularios.py`;
- `apresentacao.py`, `diagnostico.py`, `acoes.py` e `mensagens.py`;
- `templates/editor/`.

O app não tem `models.py` nem migrações. As rotas ficam sob o prefixo `/editor/`.

**Rationale**: o app novo se justifica por três bloqueios concretos, não por preferência.

1. **007**: `tests/participacao/test_entrada_aceitacao.py::test_10` proíbe `urls.py`,
   `views.py` e `forms.py` nos apps de domínio (`instrumento`, `participacao` etc.). O
   editor não pode morar em `trajetoria/instrumento`.
2. **008**: `tests/interface/test_interface_fronteiras.py::test_interface_so_importa_o_permitido_do_dominio`
   restringe o que a jornada do egresso importa. `trajetoria.instrumento.operacoes` só
   aparece no `cenario.py` da demonstração. Pôr o editor em `trajetoria/interface`
   exigiria afrouxar essa fronteira, que protege a regra "a jornada do egresso nunca
   escreve o instrumento".
3. **Spec 009 FR-006**: o editor é uma área distinta da jornada do egresso.

Um app sem modelos é a menor unidade que satisfaz os três pontos: é o mesmo padrão das
`interface` e `demonstracao` da 008.

**Alternatives considered**:

- **Módulos dentro de `trajetoria/interface`**: viola a fronteira de importação da 008 e
  mistura operador e egresso. Rejeitado.
- **Views em `trajetoria/instrumento`**: viola o test_10 da 007 e acopla domínio e
  interface. Rejeitado.
- **Django admin**: o projeto não tem `django.contrib.*` (008 R2). O admin exporia campos
  internos, UUIDs e escrita direta no ORM, o que viola FR-021 e FR-022. Rejeitado.

---

## R2 — Disponibilidade só no modo não produtivo, sem mecanismo novo

**Decision**: as rotas do editor entram em `config/urls.py` com
`path("editor/", include("trajetoria.editor.urls"))`. Nenhum mecanismo novo de acesso é
criado.

- `ModoDemonstracaoMiddleware` (008) já levanta `Http404` em **toda** requisição, antes de
  resolver a URL, quando `TRAJETORIA_DEMONSTRACAO` não é `"1"`. As rotas do editor ficam
  cobertas automaticamente.
- A docstring do middleware é atualizada para citar o editor; o código não muda.
- O processador de contexto da demonstração não é usado pelo editor. O
  `editor/base.html` não mostra Pessoa fictícia nem links de troca de pessoa (FR-005).

**Rationale**: FR-001 e FR-002 exigem a entrada não produtiva **já existente**. O
middleware atua antes da resolução de URL, então nenhuma view do editor responde com o
modo desligado. Isso é verificável enumerando as rotas do editor em teste (R14).

O plan registra explicitamente que `TRAJETORIA_DEMONSTRACAO` **não é governança**:

- é um interruptor técnico de ambiente local;
- o banner permanente do editor (FR-003) diz que não há autenticação e que o acesso não
  confere competência institucional;
- a Feature 010 substituirá esse acesso (DP-901).

**Alternatives considered**:

- **Setting própria `TRAJETORIA_EDITOR`**: seria um segundo interruptor sem consumidor,
  que poderia ser ligado sem o modo de demonstração. Rejeitado (XXII).
- **Verificação extra dentro de cada view**: redundante com o middleware, que já é global
  e testado. Rejeitado.
- **Login simples ou senha de ambiente**: proibido (FR-004; Constituição XV). Rejeitado.

---

## R3 — Mapa de escrita: toda ação → uma operação pública da 002

**Decision**: cada POST do editor chama exclusivamente funções de
`trajetoria.instrumento.operacoes`. O mapa completo está em
[contracts/rotas.md](contracts/rotas.md).

Nenhuma ação da interface ficou sem operação correspondente:

| Ação | Operação 002 |
|------|--------------|
| Criar Pesquisa | `criar_pesquisa` |
| Criar Versão vazia | `criar_versao` |
| Nova Versão a partir de outra | `criar_versao_a_partir_de` |
| Dados da Versão | `alterar_versao` |
| Adicionar, editar e remover Seção | `adicionar_secao`, `alterar_secao`, `remover_secao` |
| Encaminhamento | `definir_encaminhamento` |
| Subir ou descer Seção | `reordenar_secoes` |
| Criar Pergunta (4 tipos, escala na criação) | `adicionar_pergunta` |
| Editar Pergunta (texto, explicativo, obrigatória, escala) | `alterar_pergunta` |
| Mover Pergunta para outra Seção | `mover_pergunta` |
| Subir ou descer Pergunta | `reordenar_perguntas` |
| Remover Pergunta | `remover_pergunta` |
| Adicionar Opção; editar texto e complemento | `adicionar_opcao`, `alterar_opcao` |
| Subir ou descer Opção | `reordenar_opcoes` |
| Remover Opção | `remover_opcao` |
| Desvio: definir, trocar, remover | `definir_regra`, `remover_regra` |

**Não usadas**: `publicar` (FR-076) e `renomear_pesquisa` (FR-011; Clarifications).

**Leituras** não são escritas e não precisam de operação:

- `conteudo_da_versao` (002 `conteudo.py`);
- `verificar_completude` (002 `regras.py`, função pública, sem escrita);
- consultas ORM de leitura, para listar Pesquisas e Versões, carregar a instância a
  passar à operação, calcular a próxima posição e a ordem atual.

**Rationale**: FR-021 e FR-022. As operações já fazem tudo o que o editor precisa:

- rejeitam Versão publicada;
- validam texto, unicidade, tipo e escala;
- serializam por Versão e são atômicas.

**Consequência**: **nenhuma alteração na 002** (o "bloqueio real" exigido para mudar a
002 não existe).

**Alternatives considered**:

- **Nova operação "trocar regra" na 002**: desnecessária; ver R6.
- **Nova operação "mover para cima"**: desnecessária; ver R7.
- **`renomear_pesquisa` exposta**: excluída pela spec.

---

## R4 — Extração mínima na 006: `secoes_nao_suportadas`

**Decision**: em `trajetoria/participacao/percurso.py`, promover a lógica privada de
`_exigir_suporte` a uma função **pura e pública**, e fazer `_exigir_suporte` consumi-la:

```text
secoes_nao_suportadas(conteudo: ConteudoVersao) -> tuple[ConteudoSecao, ...]
    Seções, na ordem, com mais de uma Pergunta com regra de navegação
    (006 FR-016; DP-604). Sem I/O.

_exigir_suporte(conteudo)            # inalterado no efeito
    violacoes = [Violacao(ESTRUTURA_NAO_SUPORTADA, "secao",
                 f"Seção {s.id} tem {n} Perguntas com regra de navegação")
                 for s in secoes_nao_suportadas(conteudo)]
    if violacoes: raise ParticipacaoRejeitada(violacoes)
```

- `__all__` de `percurso.py` ganha `"secoes_nao_suportadas"`.
- O motivo, o campo, o texto do detalhe e a ordem das violações continuam idênticos.
- Os testes existentes da 006 (`test_jornada_percurso.py::test_duas_perguntas_com_regra_na_mesma_secao_sao_rejeitadas`,
  `test_uma_violacao_por_secao_nao_suportada`, `test_jornada_conclusao.py`) passam sem
  alteração.
- Um teste novo da 006 fixa a função pública:
  - uma Versão suportada dá `()`;
  - duas Seções não suportadas aparecem na ordem;
  - as violações de `percorrer` correspondem exatamente às Seções devolvidas.

**Rationale**: esta é a "exposição limpa" pedida.

- A regra continua escrita **uma vez**, no módulo que a executa.
- A 006 continua consumindo a mesma função.
- A 009 apenas consulta o resultado.

Devolver Seções, e não `Violacao`, evita que o editor faça parsing do texto de detalhe,
que contém UUID. Assim o editor localiza o elemento pelo próprio `ConteudoSecao`.

**Alternatives considered**:

- **Tornar `_exigir_suporte` pública e capturar `ParticipacaoRejeitada` no editor**:
  obrigaria a tratar exceção como fluxo normal e a extrair a Seção do texto. Rejeitado.
- **Chamar `percorrer(conteudo, {})` e capturar a exceção**: usa a jornada como
  validador implícito e acopla o editor ao cálculo do percurso. Rejeitado.
- **Copiar a regra no editor**: proibido (FR-068, FR-069).
- **"JourneyValidator", registro de verificações ou plugin**: proibido. Rejeitado.

---

## R5 — Diagnóstico técnico: composição de dois resultados, sem persistência

**Decision**: `trajetoria/editor/diagnostico.py` define um valor em memória e uma função.

```text
@dataclass(frozen=True)
class Problema:
    origem: Literal["estrutura", "jornada"]   # A (002) ou B (006)
    causa: Enum                                # Motivo da 002, ou Motivo.ESTRUTURA_NAO_SUPORTADA (006)
    elemento: Localizacao                      # rótulo + endereço (R9)
    texto: str                                 # mensagem operacional (R10)

@dataclass(frozen=True)
class Diagnostico:
    estrutura: tuple[Problema, ...]            # A — de verificar_completude (002)
    jornada: tuple[Problema, ...]              # B — de secoes_nao_suportadas (006)
    estrutura_valida -> bool                   # not estrutura
    compativel_com_jornada -> bool             # not jornada
    sem_impedimentos_conhecidos -> bool        # ambos

diagnosticar(versao) -> Diagnostico
```

- Ela lê o conteúdo uma vez (`conteudo_da_versao`) e chama:
  - `verificar_completude(versao)` (002);
  - `secoes_nao_suportadas(conteudo)` (006).
- Ela traduz cada item para `Problema`.
- B é calculado sempre, mesmo quando A tem problemas, para que o operador veja tudo de
  uma vez (FR-066).
- As três situações da spec (Clarifications) são **derivadas no template** a partir das
  duas propriedades booleanas.

**O diagnóstico preserva os problemas concretos** (precisão pré-tasks):

- **A**: o resultado guarda **todos** os problemas devolvidos por `verificar_completude`
  (002), um `Problema` por `Violacao`, na ordem da 002.
- **B**: o resultado guarda **todas** as Seções devolvidas por `secoes_nao_suportadas`
  (006), um `Problema` por Seção.
- **Booleanos**: `estrutura_valida`, `compativel_com_jornada` e
  `sem_impedimentos_conhecidos` são só propriedades derivadas das tuplas. Eles nunca
  substituem a lista.
- **Texto acionável**: cada `Problema` diz **onde** está, pelo rótulo do elemento, e **o
  que corrigir**, como em "A Pergunta «Qual é sua situação profissional?» (Pergunta 2 da
  Seção 4) precisa ter pelo menos duas Opções."
- **Sem correção automática**: o link leva à página onde o operador corrige.
- **Causa interna**: o `Motivo` original fica em `causa`, para testes e
  rastreabilidade, e nunca é o texto exibido.

Um único value object (`Diagnostico`, com tuplas de `Problema`) basta. Ele tem
consumidores concretos: a página do diagnóstico, o resumo na estrutura e as marcas por
elemento. Não há framework, registro de verificações nem enum de aprovação.

**Rationale**:

- Atende FR-066 a FR-075 e a decisão 4 das Clarifications.
- Não há modelo `Prontidao`, enum institucional de aprovação nem gravação. O valor nasce
  e morre na requisição.
- A causa original (`Motivo` da 002, ou `Motivo.ESTRUTURA_NAO_SUPORTADA` da 006, sem vocabulário novo) fica no objeto, rastreável em
  código e em teste, e nunca vai para o HTML (FR-070).

**Alternatives considered**:

- **Enum `Situacao` com três membros**: seria um vocabulário próprio do editor fácil de
  confundir com estado. Os dois booleanos bastam. Rejeitado.
- **Gravar data do último diagnóstico**: proibido (FR-072).
- **Rodar o diagnóstico no POST de cada edição e guardá-lo**: desnecessário, porque ele
  é barato. Rejeitado.

---

## R6 — Troca de desvio tudo-ou-nada: helper `definir_desvio`

**Decision**: `trajetoria/editor/acoes.py` define:

```text
definir_desvio(pergunta, opcao, destino: Secao | FINALIZAR | None) -> None
    destino igual ao atual → nada
    destino None           → remover_regra
    opção sem regra        → definir_regra(destino)
    opção com regra        → remover_regra + definir_regra(destino),
                             dentro de transaction.atomic()
```

- As operações da 002 já abrem `transaction.atomic()` próprio. O bloco externo as
  transforma em savepoints aninhados.
- Se `definir_regra` rejeitar, o `remover_regra` anterior é desfeito, e a Opção mantém
  o destino antigo (FR-052).
- O POST de edição de Opção (texto, complemento, desvio) roda `alterar_opcao` e
  `definir_desvio` no **mesmo** bloco atômico da view: um formulário, uma ação, tudo ou
  nada.

**Rationale**:

- O contrato da 002 recusa `definir_regra` sobre Opção com regra (`REGRA_JA_DEFINIDA`).
- Duas operações numa transação externa é exatamente o padrão já aceito na 008 (R7 dela,
  "transação externa sobre várias operações").
- O helper tem um consumidor concreto.

**Alternatives considered**:

- **Nova operação `trocar_regra` na 002**: alteraria contrato sem bloqueio real.
  Rejeitado.
- **Duas requisições, "remover" depois "definir"**: exporia estado intermediário.
  Rejeitado (FR-052).
- **UnitOfWork ou service layer genérica**: proibido. Rejeitado.

---

## R7 — Subir/descer e "adicionar ao final"

**Decision**: em `acoes.py`, dois helpers pequenos.

- `proxima_posicao(conjunto)`: devolve `(max(posicao) or 0) + 1` sobre o queryset do
  conjunto (Seções da Versão, Perguntas da Seção, Opções da Pergunta). Usado em
  `adicionar_secao`, `adicionar_pergunta`, `adicionar_opcao` e `mover_pergunta`.
- `mover(elementos_em_ordem, elemento, direcao)`: devolve a lista com o elemento trocado
  com o vizinho, ou `None` quando já está na ponta. A view passa a lista a
  `reordenar_secoes`, `reordenar_perguntas` ou `reordenar_opcoes`, que exigem a ordem
  completa.

Concorrência:

- `POSICAO_OCUPADA`, quando duas inclusões competem, e `ORDEM_INCOMPLETA`, quando o
  conjunto mudou entre a leitura e a reordenação, viram a mensagem "o conteúdo mudou desde
  que esta página foi aberta" (FR-095). Nada é gravado, porque a operação é atômica.
- A exibição usa **ordinais** (1.º, 2.º… na ordem), e não o valor de `posicao`, porque
  remoções deixam lacunas. Por exemplo, a Seção de `posicao` 3, depois que a de `posicao`
  2 foi removida, aparece como "Seção 2".

**Rationale**:

- O contrato da 002 já define ordem completa e posição explícita.
- O cálculo é trivial e não justifica "PositionManager".
- A reordenação completa renumera de 1 a n, o que elimina as lacunas acumuladas.

**Alternatives considered**:

- **Arrastar e soltar ou biblioteca JS**: proibido (FR-062).
- **Campo "posição explícita"**: é PODE na spec. Fica fora desta entrega para manter um
  único caminho de ordenação. Pode ser acrescentado depois sem mudança de domínio.
- **Renumerar após cada remoção**: escrita extra sem consumidor. Rejeitado.

---

## R8 — Organização das páginas: listas sem campos de texto, formulários com um só envio

**Decision**: a navegação segue Pesquisas → Pesquisa (Versões) → Versão (estrutura) →
Seção → Pergunta → Opção. Em todas as páginas vale uma regra simples:

- **Páginas de consulta e de lista** (estrutura da Versão, Seção, Pergunta):
  - não têm campos de texto;
  - as ações por elemento são botões de POST isolados (subir, descer) ou links (editar,
    remover, mover para outra Seção, adicionar).
- **Páginas de formulário** (criar ou editar Pesquisa, Versão, dados da Versão, Seção,
  Pergunta, Opção; mover Pergunta; confirmar remoção):
  - têm **um único `<form>`** e um envio principal;
  - o formulário de nova Opção tem dois botões de envio: "Adicionar" e "Adicionar e
    incluir outra".

**Rationale**:

- A estrutura atende FR-081 a FR-084 e SC-011: qualquer Pergunta fica a duas ações da
  Versão (Versão → Seção → Pergunta).
- A regra elimina por construção o problema da auditoria UX-04 (texto digitado perdido
  ao acionar outra ação) e atende FR-083 sem JavaScript.
- Edição da Seção numa página só: título, texto introdutório e encaminhamento ficam num
  formulário único, gravado por `alterar_secao` e `definir_encaminhamento` no mesmo bloco
  atômico.
- Edição da Opção numa página só: texto, complemento e desvio ficam num formulário único
  (R6).

**Alternatives considered**:

- **Edição inline de todas as Opções na página da Pergunta**: com 77 Opções (Q19),
  teria 77 formulários e perderia texto entre ações. Rejeitado.
- **Árvore expansível ou página única**: viola FR-081 e a carga cognitiva. Rejeitado.

---

## R9 — Apresentação sem identificadores técnicos

**Decision**: `trajetoria/editor/apresentacao.py` contém funções puras sobre
`ConteudoVersao` (002):

- `rotulo_secao(ordinal, secao)`:
  - "Seção 4 — Situação profissional";
  - "Seção 13 (sem título)".
- `rotulo_pergunta(ordinal_secao, ordinal, pergunta)`: "Pergunta 2 da Seção 4: Qual sua
  ocupação?", com o texto truncado em ~80 caracteres para listas.
- `rotulo_opcao(...)`: "Opção «Não» da Pergunta 1 da Seção 1".
- `TIPOS`: tipo → nome e descrição curta (FR-032):
  - "Escolha única — o respondente marca uma Opção";
  - …
- `descrever_escala(escala)`: "De 1 a 5 (5 pontos). 1 = «…»; 5 = «…». Pontos
  intermediários aparecem só com o número." Ausência de rótulo é dita explicitamente
  (FR-049).
- `destino_da_secao(...)` e `destino_da_opcao(...)`:
  - "segue a ordem (Seção 5)", "segue para a Seção 8 — …", "finaliza o instrumento";
  - "→ Seção 3 — …", "→ finaliza o instrumento".
- `localizador(conteudo)`: mapa `id → Localizacao(rotulo, endereco)` para Versão,
  Seções, Perguntas e Opções. Os problemas da 002 trazem `elemento: UUID`; os da 006
  trazem a `ConteudoSecao`. Os dois viram rótulo e link sem expor o UUID (FR-070).
- `referencias_a(conteudo, secao_id)`: Seções cujo encaminhamento e Opções cujo desvio
  apontam para a Seção. Alimenta a explicação de `SECAO_REFERENCIADA` (FR-029).

**Endereços**: os caminhos usam os UUIDs das entidades (`/editor/secoes/<uuid>/`), como a
008 faz com Participações.

- Os valores de `<select>` de destino também são UUIDs.
- Posições seriam instáveis sob reordenação concorrente e poderiam gravar um destino
  errado em silêncio.
- UUIDs só aparecem em atributos, nunca no texto visível. O teste varre o texto
  renderizado, sem atributos (R14).

**Alternatives considered**:

- **Endereços e valores por posição**: com reordenação entre o GET e o POST, um destino
  apontaria para outra Seção sem erro. Rejeitado.
- **Identificador curto novo**: exigiria persistência. Rejeitado (FR-107).

---

## R10 — Mensagens operacionais num único lugar

**Decision**: `trajetoria/editor/mensagens.py` guarda os **textos**. O **mapeamento**
fica local e pequeno, junto de quem o usa. Não há tabela universal de tradução.

- **Diagnóstico** (`diagnostico.py`): um mapa local só dos 5 motivos que
  `verificar_completude` pode devolver:
  - `SEM_SECOES`;
  - `SECAO_SEM_PERGUNTAS`;
  - `OPCOES_INSUFICIENTES`;
  - `DESTINO_NAO_POSTERIOR`;
  - `REFERENCIA_OUTRA_VERSAO`.

  Cada um vira "o que corrigir", composto com o rótulo do elemento. A Seção da 006 usa
  `INCOMPATIVEL_COM_A_JORNADA`.
- **Ações**: cada view mapeia, localmente, só os motivos que **a operação que ela
  chama** pode devolver, segundo o contrato da 002 (`contracts/operacoes.md` da 002):
  - criar ou alterar Versão → `DESIGNACAO_REPETIDA`, `TEXTO_VAZIO`;
  - Opção → `OPCAO_REPETIDA`, `COMPLEMENTO_REPETIDO`, `TEXTO_VAZIO`;
  - escala → `ESCALA_INVALIDA`;
  - remover Seção → `SECAO_COM_PERGUNTAS`, `SECAO_REFERENCIADA`;
  - inclusão ou reordenação → `POSICAO_OCUPADA`, `ORDEM_INCOMPLETA`, que viram conflito;
  - qualquer escrita → `VERSAO_PUBLICADA`, que vira a tela 409.
- **Motivo não mapeado**: a view **não** o mascara como validação. A
  `OperacaoRejeitada` é relançada e vira 500, registrada no log, como erro de programa.
  Exemplos: `TIPO_NAO_SUPORTADO` e `REGRA_EM_TIPO_INCOMPATIVEL`, que a interface nunca
  provoca, porque não oferece a ação. Erros inesperados continuam sendo erros.
- Avisos pós-redirecionamento por código de lista fechada (`?aviso=...`, padrão da 008):
  "Seção adicionada", "Versão criada", "publicada" etc.
- Explicações fixas:
  - semântica de navegação atual (FR-056, citando que é a semântica atual, 006/DP-604);
  - tipo fixo (FR-034);
  - situação "sem impedimentos técnicos conhecidos" e o que ela não significa (FR-071);
  - banner não produtivo (FR-003);
  - recomendação genérica de trabalhar sobre cópia (FR-100).

Cada view tem um pequeno mapa `Motivo → campo` para associar o erro ao campo do
formulário, como `DESIGNACAO_REPETIDA → designacao` e `OPCAO_REPETIDA → texto`. Motivo sem
campo vai para o resumo no topo.

**Rationale**:

- Atende FR-094 a FR-096.
- Testes cobrem cada motivo mapeado por ação.
- Um teste garante que um motivo não mapeado **não** vira mensagem de validação: ele
  propaga como erro.
- O texto da 006 vem de uma constante, e não do `detalhe` técnico.

**Alternatives considered**:

- **Exibir `Violacao.detalhe`**: contém nomes de motivo e UUIDs. Rejeitado.
- **Mensagens espalhadas nas views**: dificultam a revisão de linguagem (008/DP-801).
  Rejeitado.

---

## R11 — Formulários: `forms.Form` por ação, sem reimplementar regras do domínio

**Decision**: `trajetoria/editor/formularios.py` define formulários explícitos e
pequenos. Nenhum é `ModelForm`.

| Formulário | Campos |
|------------|--------|
| `PesquisaForm` | `nome`; `confirmar_nome_repetido`, oculto |
| `DesignacaoForm` | `designacao`. Usado em "criar Versão" e "criar a partir de" |
| `DadosVersaoForm` | `designacao`, `titulo`, `texto_abertura`, `texto_encerramento` |
| `SecaoForm` | `titulo`, `texto`, `encaminhamento` (opções: "seguir a ordem" + demais Seções da Versão) |
| `TipoPerguntaForm` | `tipo` (rádios com exatamente os 4 tipos de `TipoPergunta`) |
| `PerguntaForm(tipo=…)` | `texto`, `texto_explicativo`, `obrigatoria`; com `tipo=ESCALA`, também `inicio`, `fim`, `rotulo_inicio`, `rotulo_fim` |
| `MoverPerguntaForm` | `secao` (demais Seções da Versão) |
| `OpcaoForm(tipo=…)` | `texto`, `complemento`; com escolha única, também `desvio` (sem desvio / Seções da Versão / finalizar) |

Regras dos formulários:

- **Só convertem, não validam regras do domínio** (FR-022):
  - textos com `required=False, strip=False`;
  - texto obrigatório vazio é enviado como está, e a 002 rejeita com `TEXTO_VAZIO`, que
    vira erro do campo;
  - texto opcional vazio ou só com espaços vira `None` (Edge Case da spec, [Hipótese]);
  - limites de escala usam `IntegerField(required=False)`, porque converter número não é
    regra do domínio, e o valor vai em `Escala(inicio, fim, …)`;
  - limite ausente ou início ≥ fim chega à 002, que rejeita com `ESCALA_INVALIDA`.
- **Listas de destino**:
  - o encaminhamento omite a própria Seção (FR-055 PODE);
  - o desvio lista todas as Seções da Versão;
  - nenhuma lista filtra por posição (FR-055), porque destino anterior é problema do
    diagnóstico A.
- **Tipo**: o tipo da Pergunta nunca é campo editável (FR-033). Na edição, o tipo é
  exibido com a explicação de FR-034.

**Rationale**:

- Formulários proporcionais: cada um corresponde a uma ação.
- Os campos não espelham o modelo, porque não há `escala_inicio`, `regra_finaliza` ou
  `regra_destino` como campos crus.
- Não há construtor genérico.

**Alternatives considered**:

- **`ModelForm`**: exporia colunas internas e duplicaria `CheckConstraint`s como
  validação de formulário. Rejeitado.
- **`required=True` nos textos**: seria uma segunda fonte da regra de texto obrigatório.
  Rejeitado (FR-022).

---

## R12 — Versão publicada: somente leitura na interface, recusa explícita no POST

**Decision**: o helper `_exigir_rascunho(request, versao)` é chamado no início de **toda**
view de escrita, antes de tocar no domínio:

- **GET de página de formulário** (dados da Versão, nova Seção, editar Seção, nova
  Pergunta, editar Pergunta, mover, nova ou editar Opção, confirmar remoção) de Versão
  publicada: redireciona para a página de consulta com `?aviso=publicada`.
- **POST** para Versão publicada: responde **409** com `editor/aviso.html`:
  - "Esta Versão está publicada e não pode ser alterada. Para mudar o instrumento, crie
    uma nova Versão a partir dela.";
  - link para "criar nova Versão a partir desta";
  - nenhuma operação é chamada.
- **Corrida**: se a Versão for publicada entre a verificação e a operação, a 002 rejeita
  com `VERSAO_PUBLICADA`, e a view mostra a mesma tela 409.
- **Templates de consulta** (`versao.html`, `secao.html`, `pergunta.html`):
  - recebem `editavel = not versao.publicada`;
  - sem ele, não renderizam botões, links de edição, remoção ou diagnóstico;
  - mostram "Publicada em <data> — não pode ser alterada" (FR-018);
  - oferecem "pré-visualizar" e "criar nova Versão a partir desta".

**Rationale**:

- Atende o pedido explícito de que "views também rejeitem POSTs", além do domínio
  (defesa em profundidade sem duplicar a regra).
- A view só lê `versao.publicada`; a recusa efetiva continua sendo da 002.
- Cobre US12 e FR-018 a FR-020.

**Alternatives considered**:

- **Confiar só na 002**: a recusa já existe, mas formulários de edição seriam oferecidos
  e só falhariam no envio. Rejeitado.
- **Esconder Versões publicadas**: violaria FR-018. Rejeitado.

---

## R13 — Pré-visualização: uma Seção por página, reaproveitando a apresentação por tipo da 008

**Decision**: duas rotas, ambas GET, sem `<form>` e sem botão de envio.

- `GET /editor/versoes/<v>/previa/`:
  - título apresentado e texto de abertura;
  - índice das Seções, com links;
  - texto de encerramento;
  - aviso permanente "Pré-visualização — nada é gravado; os desvios não são executados".
- `GET /editor/versoes/<v>/previa/secoes/<n>/` (n = ordinal):
  - título e texto da Seção;
  - Perguntas renderizadas com `FormularioDaSecao(secao, {}).itens()`
    (`trajetoria.interface.formularios`, 008) e os templates por tipo
    `interface/perguntas/{escolha_unica,escolha_multipla,texto_curto,escala}.html`;
  - links "Seção anterior/seguinte **na ordem**";
  - anotações **estruturais**, abaixo de cada Pergunta com desvio:
    - "Se «Não» for escolhida na aplicação real, a próxima seção será: Experiência
      profissional.";
    - "Se «Não» for escolhida na aplicação real, o instrumento é finalizado.";
  - anotação da Seção com encaminhamento: "Na aplicação real, depois desta seção vem: …".

**A prévia por Seção é leitura, não jornada** (precisão pré-tasks):

- **Navegação**: anterior e próxima são **links GET simples**, na **ordem estrutural**
  da Versão (ordinal − 1, ordinal + 1). Não há cursor, sessão de prévia, cookie,
  parâmetro de estado, nem respostas temporárias.
- **Sem jornada**: nenhuma ramificação é executada e nada da 006 calcula a próxima
  Seção. `percorrer`, `situacao_da_jornada` e `concluir` não são chamados, nem
  importados.
- **Sem dado de aplicação**: nenhuma Participação, Campanha ou Resposta é criada ou lida.
- **Natureza das anotações**: são informação estrutural lida de `ConteudoVersao`, não
  simulação.

Detalhes de comportamento:

- Os controles ficam **fora de qualquer `<form>`**, então não há envio possível. Eles
  continuam operáveis por teclado, porque o operador confere a experiência do
  respondente.
- O `<title>` e o `h1` começam com "Pré-visualização".
- Uma Seção por página evita `id` duplicado: os campos da 008 se chamam `p<n>` por
  posição dentro da Seção, e várias Seções na mesma página repetiriam `p1`.
- A navegação segue a ordem, nunca os ramos (FR-088).
- Listas longas usam a mesma lista suspensa da 008 (`LIMITE_RADIOS`), coerente com o que
  o egresso verá (FR-092).

**Acoplamento**:

- `FormularioDaSecao` depende só de `ConteudoSecao` (002) e de um dicionário de
  respostas. Com `{}`, não há Participação, Campanha nem Resposta, e nada é lido da 005,
  006 ou 007.
- As views da 008 **não** são reutilizadas. O editor tem seus próprios
  `previa.html` e `previa_secao.html`, que só incluem os templates por tipo.
- A fronteira de importação da 009 permite `trajetoria.interface.formularios` com o nome
  `FormularioDaSecao` e nada mais da 008.

**Rationale**:

- O operador confere exatamente o controle que o egresso verá.
- Não há segunda implementação da jornada.
- Não há infraestrutura de prévia: Campanha, Participação e respostas de prévia não
  existem (FR-090, FR-091).

**Alternatives considered**:

- **Templates próprios por tipo no editor**: seriam pequenos, mas divergiriam da 008 e
  mostrariam ao operador algo diferente do que o egresso vê. Rejeitado.
- **Todas as Seções numa página**: daria `id` duplicado e uma página gigante. Rejeitado.
- **Simulação interativa dos ramos**: duplicaria a 006. Rejeitado (FR-087, FR-088).
- **`<fieldset disabled>`**: tira os controles da ordem de foco e reduz o contraste,
  piorando a conferência por teclado e leitor de tela. Sem `<form>`, já não há envio.
  Rejeitado.

---

## R14 — Estratégia de testes

**Decision**: testes em `tests/editor/` (sem `__init__.py`, com o prefixo
`test_editor_*`, como em `tests/interface/`), pelo cliente HTTP do Django, com operações
reais e Postgres. Mais um teste novo em `tests/participacao/` para a função pública da
006.

Fixtures (`tests/editor/conftest.py`, `construcao_editor.py`):

- modo de demonstração ligado por padrão (`settings.TRAJETORIA_DEMONSTRACAO = True`). Os
  testes do modo desligado o desligam explicitamente;
- `pesquisa_de_teste()` e `versao_vazia()`: Pesquisa e Versão próprias, criadas pelas
  operações da 002, com nomes fictícios **diferentes** do nome da baseline;
- `baseline()`: `materializar()` da 003 dentro da transação do teste;
- `copia_da_baseline()`: `criar_versao_a_partir_de` sobre a baseline;
- `publicada()`: cópia publicada por `publicar`, **só no arranjo do teste**, nunca pelo
  editor;
- `retrato(versao)`: `conteudo_da_versao` com identidades removidas
  (`tests/instrumento/construcao.sem_identidades`), para comparar antes e depois;
- `texto_visivel(resposta)`: texto renderizado sem atributos, para varrer UUIDs, nomes de
  `Motivo`, classes e códigos de requisito.

Reutilização de outros testes:

- `tests/interface/test_interface_acessibilidade.py::verificar`, a verificação
  estrutural de acessibilidade, é reutilizada **por importação**, sem alterar a 008;
- o padrão de `ast` dos testes de fronteira da 008 é reproduzido para o editor.

Arquivos (detalhe em [quickstart.md](quickstart.md#validar-automaticamente)):

| Arquivo | Cobre |
|---------|-------|
| `test_editor_acesso.py` | Modo desligado: um único teste percorre **todas** as rotas de `editor.urls` em GET e POST, todas 404. O gate é central (middleware). Controle com o modo ligado: uma rota por família. Mais o banner e a ausência de Pessoa no cabeçalho |
| `test_editor_pesquisas.py` | Listar; criar; nome vazio; aviso e confirmação de nome repetido sem bloquear; sem renomear |
| `test_editor_versoes.py` | Listar com estados escritos e origem; criar vazia; designação repetida; criar a partir de rascunho e de publicada; origem intacta; dados da Versão |
| `test_editor_publicada.py` | Nenhum controle de edição; GET de formulário redireciona; POST em **cada** rota de escrita → 409 e retrato idêntico; corrida (publicada entre GET e POST) |
| `test_editor_secoes.py` | Criar ao final; editar e remover título; subir e descer; ações ausentes nas pontas; remover vazia; recusa com Perguntas; recusa referenciada com explicação; encaminhamento definir e remover |
| `test_editor_perguntas.py` | Os 4 tipos (só eles); escala na criação; editar sem campo de tipo; obrigatória e opcional; subir e descer; mover para outra Seção (ao final, mantém Opções e desvios); remover com cascata e confirmação |
| `test_editor_opcoes.py` | Adicionar ao final; "adicionar e incluir outra"; editar texto mantendo desvio; repetida; complemento marcar, desmarcar e segundo recusado; subir e descer; remover com desvio; ausência em texto curto e escala |
| `test_editor_escala.py` | Explicação com e sem rótulos; início ≥ fim; não inteiro; vazio; alteração |
| `test_editor_navegacao.py` | Desvio → Seção, finalizar, sem desvio; **troca atômica**, com falha injetada na segunda operação e destino antigo preservado; ausência em múltipla, texto e escala; texto da semântica atual; cenário A/B/C |
| `test_editor_diagnostico.py` | Cada condição da 002 no diagnóstico A; a limitação da 006 no B; combinação; as três situações; correção e novo diagnóstico; nenhuma gravação; "sem impedimentos" ⇒ `publicar` aceita e `secoes_nao_suportadas` vazia; ausência de "pronta", "aprovada", "homologada" |
| `test_editor_previa.py` | Controles por tipo; anotações estruturais; sem `<form>` nem botão de envio; navegação só por links GET na ordem estrutural (inclusive quando um desvio apontaria para outra Seção); abrir e navegar por todas as Seções sem alterar Versão (retrato) e sem mudar a contagem de Pesquisa, Versão, Seção, Pergunta, Opção, Campanha, Participação e Resposta; `concluir` e `percorrer` não chamados (monkeypatch que falha se chamados); sem Pessoa; Seção sem título |
| `test_editor_aceitacao.py` | Cenário principal (14 passos) e cenário de navegação, só por HTTP |
| `test_editor_baseline.py` | Editor oferece edição da baseline como de qualquer rascunho, só por GET, sem escrita; depois de todos os fluxos sobre a cópia, `materializar()` devolve `criada=False` sem recusa; nenhum texto ou nome da baseline nos fontes do editor |
| `test_editor_acessibilidade.py` | `verificar` em todas as telas, inclusive com erros; nomes acessíveis de subir, descer e remover; estados em texto |
| `test_editor_fronteiras.py` | Importações permitidas (`ast`); nenhuma escrita direta (`.save/.create/.update/.delete/bulk_`); nenhum `publicar` ou `renomear_pesquisa`; sem `models.py` nem modelos no app; `makemigrations --check`; sem `<script>` nem recurso externo; CSRF em toda rota de escrita; nenhum UUID, `Motivo`, `Traceback` no texto visível; motivo não mapeado propaga como erro (não vira mensagem) |

Fora dos testes do editor:

- `tests/participacao/test_jornada_percurso.py` ganha
  `test_secoes_nao_suportadas_publica`, sem alterar os testes existentes.

O modo sem JavaScript fica coberto por construção: o cliente HTTP do Django não executa
JS, e nenhum template tem `<script>`.

**Baseline preservada**:

- Nenhum teste chama operação de escrita sobre a Versão materializada pela 003.
- O pytest-django isola cada teste numa transação revertida, então nada sai do
  isolamento.
- `test_editor_baseline.py` confirma a equivalência com a declaração ao final dos
  fluxos.

---

## R15 — Estilo, base e acessibilidade

**Decision**: `editor/base.html` é próprio do editor e reaproveita a folha da 008.

- Inclui `interface/estilo.css` mais `editor/estilo.css` inline (padrão R14 da 008, sem
  `staticfiles`). `editor/estilo.css` é pequena: tabela ou lista da estrutura, botões
  compactos de ordenação, selos de estado em texto e alertas do diagnóstico.
- Tem `lang="pt-BR"`, link "Pular para o conteúdo", banner não produtivo (`role="note"`)
  e cabeçalho "Trajetória Ifes — Editor do instrumento".
- A trilha de navegação fica em `<nav aria-label="Você está em">`, com uma lista
  ordenada.
- Tem um `h1` por página, igual ao objeto atual (UX-05, UX-07).
- `<title>` com prefixo "Erro:" quando há erros.
- Resumo de erros no **topo** do `main` (`role="alert"`, links para os campos; UX-01).
- Erros com `aria-describedby` e `aria-invalid`.
- Estados "Rascunho" e "Publicada" e "Obrigatória" e "Opcional" sempre em texto.
- Botões de subir e descer com texto visível curto ("Subir", "Descer") e nome acessível
  completo via `aria-label`, por exemplo "Subir a Pergunta 3: Qual sua idade?"
  (FR-064).
- Depois do redirecionamento, a página volta à âncora do elemento movido
  (`#pergunta-3`).
- Folha sem larguras fixas acima de 320 px; foco visível herdado da 008.

**Rationale**:

- Atende FR-110 a FR-112 e os aprendizados da auditoria.
- Não há redesign: a 008 continua igual, e o editor só acrescenta.

**Alternatives considered**:

- **Estender `interface/base.html`**: mostraria a faixa e o cabeçalho de Pessoa fictícia
  da jornada (FR-005). Rejeitado.
- **Biblioteca de componentes ou CSS framework**: proibido. Rejeitado.

---

## R16 — Documentação e o que não muda

**Decision**:

- **Muda**:
  - `config/urls.py`: uma linha;
  - `config/settings.py`: `INSTALLED_APPS += "trajetoria.editor"` e o comentário do modo
    de demonstração citando o editor;
  - docstring de `trajetoria/demonstracao/middleware.py`;
  - `trajetoria/participacao/percurso.py`: R4;
  - `README.md`: uma linha para o quickstart da 009, dizendo que o editor é não produtivo.
- **Não muda**:
  - modelos e migrações;
  - `trajetoria/instrumento/*` (002);
  - `formulario_2024` (003);
  - `campanha` (004);
  - `participacao` fora de `percurso.py`;
  - `interface` e `demonstracao` (008), exceto a docstring;
  - `pyproject.toml`, porque não há dependência nova;
  - `.env.example`.
- **Nenhum ADR novo**: não há decisão tecnológica estrutural nova (ADR 0001 vale).

**Rationale**: o pedido do solicitante.

- 002: só se houver bloqueio real, e não há.
- 006: só a exposição limpa (R4).
- 008: só reuso visual seguro.
