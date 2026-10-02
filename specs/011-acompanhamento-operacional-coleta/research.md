# Research: Acompanhamento operacional da coleta (Feature 011)

Fase 0 do plan. O Technical Context não tem itens `NEEDS CLARIFICATION`: a stack é a da
ADR 0001, sem dependência nova. Cada item abaixo registra **Decisão**, **Justificativa** e
**Alternativas consideradas**.

---

## R1 — Persistência: nenhuma

**Decisão**: zero modelos, zero migrations e zero índices novos.

**Justificativa**: todo número é função do estado atual de quatro coisas:

- `Campanha`: critérios, período, `aberta_em`, `encerrada_em`;
- `ConclusaoAcademica`: atributos institucionais;
- `Participacao`: existência e `concluida_em`;
- `VinculoDeGovernanca`: papel, unidade e `ativo`.

Nenhum fato novo precisa ser registrado.

- O momento da consulta é exibido, não gravado.
- A escolha do recorte é parâmetro GET, não preferência.
- A fotografia da população é exatamente 004/DP-408, reservada à Feature 012.
- O volume é fictício e pequeno, sem medida que justifique índice (spec FR-130).

**Alternativas consideradas**:

- Snapshot da população na abertura: resolveria DP-408 por conta própria. Vedado (spec
  FR-131).
- Contadores gravados na Campanha: duplicariam estado derivável e exigiriam
  sincronização (Const. XXII).
- Índice em `conclusao.unidade` ou `participacao.concluida_em`: sem medida. Se dados
  reais mostrarem lentidão, uma feature futura registra a evidência.

---

## R2 — Onde fica o código: app `trajetoria/acompanhamento`, sem models

**Decisão**: novo app `trajetoria.acompanhamento` em `INSTALLED_APPS`, sem `models.py` e
sem `migrations/`. Módulos:

| Módulo | Conteúdo |
|--------|----------|
| `consultas.py` | Campanhas visíveis, indicadores e recortes. Funções que devolvem objetos de valor; nada grava |
| `apresentacao.py` | Percentual, rótulos de situação e de "em andamento", avisos, definições curtas, textos de recusa, texto do instrumento, ordenação de linhas. Funções puras e constantes de texto |
| `acesso.py` | Decorador de autorização das views (identificação → vínculos → regra → escopo), no padrão de `editor/acesso.py` |
| `views.py` | Duas views de função: `campanhas` e `campanha` |
| `urls.py` | Duas rotas |
| `templates/acompanhamento/` | `base.html`, `campanhas.html`, `campanha.html`, `_tabela_recorte.html`, `recusa.html` |

**Justificativa**:

- O app segue o padrão do editor (009/010): consultas e textos separados das views.
- O app é **consumidor** de 004, 005, 006 e 010; nenhum desses apps passa a depender
  dele.
- "Poucos módulos" atende ao pedido. `apresentacao.py` existe porque as regras de
  exibição (FR-034, FR-036, FR-037, FR-042, FR-056) precisam de testes próprios sem
  renderizar páginas.

**Alternativas consideradas**:

- Colocar as views no app `editor`: misturaria superfícies com regras de acesso e
  propósitos diferentes. O editor não deve mudar (orientação do solicitante).
- Consultas em `campanha/consultas.py`: a 004 é domínio de Campanha, não de agregação
  por escopo de operador. Ela ganha só um acessor público (R4).
- Camada de repositório ou serviço genérico de relatório: vedado (spec FR-131).

---

## R3 — Regra de governança: `pode_acompanhar_coleta` e `escopo_de_acompanhamento`

**Decisão**: acrescentar a `trajetoria/governanca/regras.py`, no mesmo estilo puro das
três regras da 010 (só recebe `vinculos`; não lê banco, settings nem requisição):

```text
pode_acompanhar_coleta(vinculos) -> bool
    any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)

escopo_de_acompanhamento(vinculos) -> EscopoDeAcompanhamento | None
    CPAEG ativo existe      -> EscopoDeAcompanhamento(institucional=True,  unidades=frozenset())
    senão, CSAEG ativos     -> EscopoDeAcompanhamento(institucional=False, unidades={v.unidade ...})
    senão                   -> None
```

`EscopoDeAcompanhamento` é um dataclass congelado em `regras.py` com dois campos.

As duas atuações são **nomeadas** nas duas funções. Uma atuação futura não recebe
acompanhamento por omissão (Clarifications 2026-10-02).

Invariante testado: `pode_acompanhar_coleta(v) == (escopo_de_acompanhamento(v) is not None)`.

**Justificativa**:

- A semântica explícita foi pedida; o escopo é dado da regra, não da view.
- Manter as duas funções na governança deixa a regra testável sem banco.
- A view nunca reinterpreta papéis: ela recebe o escopo pronto.

**Alternativas consideradas**:

- `any(v.ativo for v in vinculos)`: é o que `pode_consultar_publicado` faz hoje. Foi
  recusado explicitamente ("qualquer vínculo presente ou futuro").
- Uma função só, devolvendo o escopo: perderia o nome `pode_acompanhar_coleta`, que
  documenta a capacidade.
- Enum de capacidade, registro ou `Permission`: vedados (spec FR-010; 010 FR-034).

**Efeito na 010**: `regras.__all__` passa de três para cinco nomes. Os testes de
fronteira da governança são atualizados para o novo conjunto, e nenhuma regra existente
muda (spec FR-141). `editor/acesso.py` não muda: sua tupla `_REGRAS` continua com as três
regras do editor.

---

## R4 — Reutilização da elegibilidade da 004: `populacao_no_momento`, sem mudança

**Decisão**: o contrato público é a função que **já existe** em
`trajetoria/campanha/consultas.py`:

```text
populacao_no_momento(campanha) -> QuerySet[ConclusaoAcademica]
```

Ela responde exatamente "quais Conclusões pertencem agora à população desta Campanha?"
(004 FR-031, FR-032). O acompanhamento só a **refina**, sem mudar o predicado:

- `populacao_no_momento(c).filter(universo)` — escopo da 010, por unidade;
- `.count()` — total;
- `.values(*campos).annotate(n=Count("id")).order_by()` — linhas do recorte.

A 004 **não muda**: `_filtro` continua privado, nenhum nome é promovido e `__all__` não
muda.

**Justificativa**:

- A 004 continua dona da pergunta "esta Conclusão pertence à população atual desta
  Campanha?". A 011 só pergunta "dentro dessa população e do escopo da 010, quais são os
  agregados?".
- A função já é pública, devolve um QuerySet componível e já é testada contra a
  avaliação pura `avaliar`. Não há duas implementações.
- Promover `_filtro` só serviria a uma agregação de várias Campanhas numa consulta. Essa
  otimização foi descartada (R6).

**Alternativas consideradas**:

- Tornar `_filtro` público (versão anterior deste plan): expõe um detalhe de
  implementação para servir a otimização prematura. Revertido.
- Nova função pública sobre QuerySet (por exemplo, `restringir_a_populacao(qs, c)`): seria
  um segundo nome para o mesmo conceito, sem consumidor que `populacao_no_momento` não
  atenda.
- Chamar `avaliar` em Python para cada Conclusão: violaria FR-072 (contagem em Python).
- `EligibilityService`, Specification Pattern, repositório: vedados.

---

## R5 — Escopo aplicado na consulta

**Decisão**: o escopo vira um `Q` sobre a Conclusão, aplicado **antes** de contar.

| Escopo | `Q` sobre `ConclusaoAcademica` | `Q` sobre `Participacao` |
|--------|-------------------------------|--------------------------|
| Institucional | `Q()` | `Q()` |
| Unidades | `Q(unidade__in=escopo.unidades)` | `Q(conclusao__unidade__in=escopo.unidades)` |

O universo usa **só o escopo do operador**, nunca o critério de unidades da Campanha
(spec FR-023):

- Do lado dos elegíveis, o critério já está em `populacao_no_momento` (R4). Repeti-lo
  seria reimplementar uma condição da 004.
- Do lado das Participações, aplicá-lo seria reavaliar elegibilidade, o que FR-038
  proíbe. Uma Participação de Conclusão hoje fora do critério (005/DP-507), mas na
  unidade do operador, continua contando para a CSAEG, como conta para a CPAEG.

As **unidades relevantes** (escopo, ou escopo ∩ critério quando a Campanha tem critério
de unidades) servem só para as linhas com zero do recorte por unidade. A oferta do recorte
por unidade e a coluna Unidade do recorte por curso dependem do escopo (institucional ou
mais de uma unidade), porque as Participações são contadas por todas as unidades do
escopo (ajuste do code review).

`unidade__in` nunca casa com `NULL`, então a Conclusão sem unidade fica fora do escopo
de qualquer CSAEG (FR-015).

**Visibilidade de Campanhas** (FR-020, FR-021):

- Institucional: `Campanha.objects.all()`.
- Unidades: `Campanha.objects.filter(Q(unidades__isnull=True) | Q(unidades__overlap=sorted(escopo.unidades)))`.
  O `overlap` do `ArrayField` (operador `&&` do PostgreSQL) faz comparação exata de
  texto, como a 004 (FR-022).

**Justificativa**: filtrar no banco garante FR-071. Nada institucional é calculado e
depois escondido.

**Alternativas consideradas**:

- Calcular tudo e filtrar no template: vedado (spec FR-071).
- Interseção em Python após carregar Campanhas: aceitável pelo volume, mas `overlap`
  mantém a regra numa expressão só e testável.

---

## R6 — Consultas: claras, sem consulta por linha, sem orçamento como contrato

**Decisão**: as mesmas duas consultas de totais servem à lista e ao detalhe, por Campanha:

```text
indicadores_da_campanha(c, escopo):
  (a) populacao_no_momento(c).filter(universo).count()
  (b) Participacao.objects.filter(campanha=c).filter(universo_participacao)
        .aggregate(iniciadas=Count("id"),
                   concluidas=Count("id", filter=Q(concluida_em__isnull=False)))
```

**Lista** (`/acompanhamento/`):

1. vínculos ativos (010);
2. Campanhas visíveis, com `select_related("versao__pesquisa")`;
3. para cada Campanha, (a) e (b).

O total é proporcional ao número de Campanhas (≈ 2 + 2N). Isso é aceito pela spec
(FR-072) e pela orientação do solicitante, porque é a forma mais simples e fiel à regra
da 004, já que cada Campanha tem critérios próprios.

**Detalhe** (`/acompanhamento/campanhas/<id>/?recorte=…`):

1. vínculos;
2. Campanha;
3. (a) e (b) para os totais;
4. (c) e (d) para o recorte:

```text
(c) populacao_no_momento(c).filter(universo).values(*campos).annotate(n=Count("id")).order_by()
(d) Participacao.objects.filter(campanha=c).filter(universo_participacao)
      .values(*("conclusao__" + f for f in campos))
      .annotate(iniciadas=…, concluidas=…).order_by()
```

São ≈ 6 consultas, **independentes do número de linhas** do recorte. As linhas de (c) e
(d) são combinadas em Python pela chave; são linhas agregadas, não registros.

Por que totais (a, b) separados das linhas (c, d): derivar os totais da soma das linhas
tornaria tautológico o teste "soma das linhas = total" (FR-052; SC-003).

**Regras que importam** (na ordem da orientação):

1. A elegibilidade vem só de `populacao_no_momento` (R4).
2. Nenhum objeto individual é carregado. Só `count()`, `aggregate()` e
   `values().annotate()`.
3. Não há consulta por linha de recorte. Uma consulta por dimensão de cada lado
   (Conclusão e Participação).
4. Nenhuma junção com a tabela de Resposta.
5. ORM simples. Sem `CASE` dinâmico, `UNION`, SQL manual ou expressão gigante.

**Proteção contra regressão (não é requisito funcional)**:

- **Detalhe**: teste com `django_assert_max_num_queries` que compara 3 e 30 valores
  distintos no recorte. O número de consultas deve ser **igual** nos dois casos, sem
  número absoluto fixado.
- **Lista**: teste que compara 1 e 3 Campanhas. A diferença deve ser no máximo
  proporcional, com ≤ 2 consultas a mais por Campanha.

Esses testes protegem o desenho implementado contra N+1 (por exemplo, consulta por
linha ou por Participação). Não são contrato da spec. Se o desenho mudar por motivo
fundamentado, eles mudam junto.

`CaptureQueriesContext` verifica que o SQL de todas as páginas não referencia as tabelas
de `Resposta` e de `RespostaOpcao` (FR-090; SC-008).

**Alternativas consideradas**:

- Agregação condicional única para todas as Campanhas da lista (versão anterior deste
  plan): exigia expor o predicado da 004 e montar uma expressão que cresce com o número
  de Campanhas. Descartada por complexidade sem medida.
- Uma consulta agrupada de Participações para a lista toda: exigiria um `Q` disjuntivo
  por Campanha no escopo de unidades. Descartada pelo mesmo motivo; (b) por Campanha é
  mais clara.
- Cache, visão materializada, SQL bruto: vedados sem problema medido.
- Se dados reais mostrarem lentidão na lista, a otimização é correção fundamentada
  futura.

---

## R7 — Os seis recortes: todos existem na Conclusão

**Decisão**: todos os seis recortes da spec são possíveis com o modelo atual. Nenhum é
excluído.

| Recorte | Valor GET | Campos da Conclusão | Chave da linha |
|---------|-----------|---------------------|----------------|
| Unidade | `unidade` | `unidade` | `(unidade,)` |
| Curso | `curso` | `unidade`, `curso` | `(unidade, curso)` |
| Nível | `nivel` | `nivel` | `(nivel,)` |
| Modalidade | `modalidade` | `modalidade` | `(modalidade,)` |
| Forma de oferta | `forma-oferta` | `forma_oferta` | `(forma_oferta,)` |
| Ano de conclusão | `ano-conclusao` | `ano_conclusao` | `(ano_conclusao,)` |

Todos são campos de `ConclusaoAcademica` (001), anuláveis, texto livre ou inteiro.

O vocabulário fechado é um `Enum` `Recorte` com seis membros. Cada membro guarda: valor
GET, rótulo, campos e rótulo de "não informado".

- **Não** é abstração de dimensão: não há registro, configuração, composição nem
  extensão.
- A chave `(unidade, curso)` foi confirmada nos Clarifications.

**Alternativas consideradas**:

- Seis views ou seis páginas: rejeitado (orientação "não criar seis telas").
- Recorte por `data_conclusao`: fora da spec (FR-050).

---

## R8 — "Não informado", ordem e linhas com zero

**Decisão**:

- **"Não informado"**: no `values()`, o `NULL` vira `None` na chave. Esse valor forma a
  linha "<Dimensão> não informado(a)". Nada é inferido nem descartado (FR-053).
  - Recorte por curso: `(unidade, None)` → "Curso não informado" naquela unidade.
  - `(None, curso)` só aparece para o CPAEG, porque uma CSAEG nunca vê unidade nula.
- **Ordem das linhas** (FR-056), por chave puramente textual e previsível:
  - `None` por último;
  - ano em ordem crescente;
  - texto ordenado por `(texto dobrado, texto exato)`, em que "dobrado" =
    `casefold()` + remoção de diacríticos (NFKD).

  A dobra serve **só para ordenar**. Nunca agrupa: "Graduação" e "graduação" continuam
  sendo duas linhas (FR-054). A ordem nunca usa indicador.
- **Linhas com zero** (FR-055), só no recorte por unidade:
  - Campanha com critério de unidades: o CPAEG vê as unidades do critério; a CSAEG vê as
    unidades relevantes.
  - Campanha sem critério: só a CSAEG ganha linhas com zero, para as unidades do seu
    escopo.
  - CPAEG em Campanha sem critério: só valores presentes, porque não há catálogo de
    unidades.

  Isso é feito em Python, acrescentando chaves conhecidas ao dicionário de linhas, sem
  consulta adicional.

**Alternativas consideradas**:

- `ORDER BY` no banco: depende da collation do PostgreSQL configurada, o que é menos
  previsível entre ambientes.
- Ordem por codepoint pura: "Águia Branca" ficaria depois de "Viana". A dobra sem
  agrupar resolve sem normalizar dados.

---

## R9 — Indicadores e taxas em memória

**Decisão**: objeto de valor `Indicadores` (frozen dataclass):

- campos `elegiveis`, `iniciadas`, `concluidas`;
- propriedades `nao_concluidas`, `taxa_inicio`, `taxa_conclusao`.

As taxas devolvem `Decimal | None`:

- `None` quando `elegiveis == 0`;
- senão `Decimal(n) * 100 / elegiveis`, arredondado com `ROUND_HALF_UP` a uma casa.

A apresentação formata com vírgula decimal ("30,0%"). Para `None`, mostra "—" com texto
acessível "não se aplica" (FR-036, FR-124).

- Nenhum limite superior: 112,5% é mostrado como 112,5% (FR-038).
- Nenhuma detecção ou nota condicional (Clarifications).

**Justificativa**: `Decimal` evita o arredondamento bancário e a imprecisão de `float`.
`None` torna impossível exibir 0% para denominador zero por engano.

**Alternativas consideradas**: `float` com `round()`, que arredonda 12,25 para 12,2
(arredondamento bancário). Calcular a taxa no template: misturaria regra e apresentação.

---

## R10 — Rótulos dependentes do estado (004)

**Decisão**: `apresentacao.py` usa `campanha.consultas.estado` e `encerramento` (004),
sem estado novo.

| Situação | Aviso | Rótulo de `nao_concluidas` |
|----------|-------|----------------------------|
| EM PREPARAÇÃO | "A coleta ainda não começou." | "Iniciadas e não concluídas" |
| EM COLETA | "Os números correspondem aos dados no momento da consulta." | "Em andamento" |
| ENCERRADA, aberta | aviso de população atual (FR-046) + data e forma do encerramento | "Iniciadas e não concluídas", com "a coleta foi encerrada" |
| ENCERRADA, nunca aberta (`aberta_em` nulo) | "Esta Campanha não chegou a entrar em coleta." + aviso de população atual | "Iniciadas e não concluídas" |

O aviso de população atual é sempre o mesmo texto:

> "A população elegível apresentada corresponde aos dados institucionais atuais e pode
> diferir da população existente quando a coleta foi encerrada."

O estado e o encerramento usam o relógio do sistema (`agora` omitido), como as demais
leituras. As funções de apresentação recebem `agora` para teste.

---

## R11 — Instrumento aplicado e Versão em rascunho

**Decisão**: a função `instrumento(campanha, pode_consultar_rascunho)` devolve um destes
resultados:

- Versão `PUBLICADA`, ou operador que pode consultar rascunho: texto
  `"<Pesquisa.nome> — <Versao.designacao>"` + link `/editor/versoes/<uuid>/`;
- caso contrário: só `"Instrumento ainda não publicado"`, sem link, sem nome da
  Pesquisa e sem designação.

Sobre o link:

- O link para Versão publicada é oferecido a todos, porque toda atuação tem
  `pode_consultar_publicado`.
- O link para rascunho só aparece para quem tem `pode_consultar_rascunho`.
- As duas regras vêm da 010, sem mudança. O editor continua aplicando sua própria
  autorização (010 FR-041).

**Justificativa**: atende Clarifications 2026-10-02 e 010 FR-036. O nome da Pesquisa
também é omitido, porque a orientação diz "apenas" o texto operacional.

---

## R12 — Acesso, recusa e roteamento

**Decisão**: `acompanhamento/acesso.py` define o decorador `@acompanhamento`, o mais
externo das duas views. A cada requisição, nesta ordem:

1. `operador_em_uso(request)` (010). Sem operador → 302 para
   `/demonstracao/operador/?destino=acompanhamento` (R13).
2. `vinculos_ativos(identificador)`. Vazio → 403, recusa "sem atuação institucional
   ativa".
3. `escopo_de_acompanhamento(vinculos)`. `None` → 403, mesma recusa. Hoje é inalcançável
   com papéis válidos, mas existe por defesa.
4. A view recebe `request.escopo` e `request.atuacao` (rótulos e
   `pode_consultar_rascunho`).

Na view de detalhe:

- 5\. Campanha inexistente → 404.
- 6\. Campanha não visível para o escopo → 403, recusa "Campanha fora do escopo", sem
  nenhum dado da Campanha. A visibilidade é verificada pela mesma função que filtra a
  lista (`campanhas_visiveis(escopo).filter(pk=…)`), para não haver duas regras.
- 7\. `recorte` inválido → 404 (FR-059). Recorte ausente → padrão: `unidade` se
  oferecido, senão `curso`.

Demais pontos:

- Com o modo desligado, o `ModoDemonstracaoMiddleware` (008) já responde 404 antes de
  tudo (FR-157).
- Só GET. Outros métodos → 405 (`require_GET`).
- O decorador marca a view (`envolvida.acompanhamento = True`). Um teste estrutural
  percorre todas as rotas do `urls.py` do app e falha se alguma não estiver marcada
  (FR-156).

**Alternativas consideradas**:

- Reutilizar `editor.acesso.exige`: ele só aceita as três regras do editor e renderiza a
  recusa do editor. Generalizá-lo alteraria o editor, o que foi vedado.
- 404 para Campanha fora do escopo: a spec pede recusa explícita (FR-153).
  - A Campanha é configuração institucional, não dado pessoal.
  - A recusa não mostra nada dela, nem o nome.
  - Distinguir recusa de inexistente segue o padrão da 010 (rascunho → recusa).

---

## R13 — Retorno após escolher operador fictício

**Decisão**: mudança mínima no adaptador de demonstração da 010:

- `/demonstracao/operador/` aceita `?destino=acompanhamento` e o repassa num campo
  oculto do formulário.
- `escolher_operador` redireciona para um destino de um **conjunto fechado**:
  `{"acompanhamento": "/acompanhamento/"}`, com padrão `/editor/`.
- Valor ausente ou desconhecido → `/editor/`, como hoje.
- A página de escolha passa a mostrar, para o operador em uso, links para "Editor do
  instrumento" e "Acompanhamento da coleta".

**Justificativa**:

- Sem isso, um operador que abre `/acompanhamento/` sem identificação escolhe o operador
  e cai no editor, sem caminho para o acompanhamento, já que o editor não deve mudar.
- O conjunto fechado preserva a decisão da 010 de não ter "mecanismo genérico de
  retorno": não há URL arbitrária, `next` nem endereço vindo do cliente.

**Alternativas consideradas**:

- Só links na página de escolha: obriga a voltar à escolha depois de cair no editor.
- `next=<url>`: vedado pela 010 (redirecionamento aberto).
- Link no cabeçalho do editor: altera o editor.

---

## R14 — Cenário de demonstração: uma Campanha fictícia em preparação, A/B/C preservados

**Decisão**: os operadores da 010 **não mudam**: A = CPAEG, B = CSAEG Vitória, C = sem
vínculo. O preparo da demonstração (`trajetoria/demonstracao/cenario.py`) acrescenta
**uma** Campanha fictícia, idempotente pelo nome:

| Atributo | Valor |
|----------|-------|
| Nome | "Demonstração — acompanhamento Serra e Vitória" |
| Versão | a **baseline em RASCUNHO** da 003 (já materializada pelo preparo) |
| Período | não definido |
| Critérios | `unidades = ["Serra", "Vitória"]`; nenhum outro |
| Ciclo | **nunca aberta** → EM PREPARAÇÃO, permanentemente |

A Campanha é criada só pelas operações da 004: `criar_campanha` e `definir_criterios`.

Com os dados simulados já existentes, sem nenhum dado acadêmico novo:

**Para B (CSAEG Vitória)**:

- Vê esta Campanha: o critério inclui Vitória. Não vê "coleta ampla" nem "coleta
  sobreposta", cujos critérios não incluem Vitória. Cobre os casos D, E e N.
- No detalhe, vê 3 elegíveis atuais, todos de Vitória: SIM-C-0002 (2014), SIM-C-0003
  (2020) e SIM-C-0012 (2016). Nenhum valor de Serra.
- O instrumento aparece como "Instrumento ainda não publicado", sem nome nem link (R11).
- O aviso "A coleta ainda não começou" aparece, com iniciadas e concluídas 0.

**Para A (CPAEG)**:

- Vê as três Campanhas.
- Nesta, vê 6 elegíveis atuais: Serra 3 (SIM-C-0001, -0004, -0013) e Vitória 3.
- Vê o instrumento identificado, com link para o editor.
- O recorte por unidade mostra as duas linhas.

**Justificativa**:

- **Não altera a semântica anterior.** Campanha nunca aberta não admite Participação
  (004 FR-053) e não aparece em `campanhas_em_coleta_para` (004 FR-052). As situações de
  entrada da 007/008 (Bruno e Carla de Vitória, "sem pesquisa disponível") ficam
  idênticas.
- `_exigir_campanhas_em_coleta` continua verificando só as duas Campanhas de coleta;
  a nova fica numa constante separada.
- **Usa a baseline em RASCUNHO**, o que permite que a regra "CSAEG não vê rascunho" (R11)
  seja exercitada no próprio cenário. A 004 permite Campanha nunca aberta com Versão em
  RASCUNHO (004 FR-010). A baseline continua editável pelo CPAEG no editor, como hoje:
  referência por Campanha não restringe edição de rascunho (002).
- **Sem período**: a Campanha nunca expira, e o preparo continua idempotente em qualquer
  data.
- **Demonstra o escopo dentro de uma mesma Campanha**: A vê 6 e B vê 3. É a evidência
  visível de FR-071.

**Limite aceito**: no cenário, B não vê Participações não nulas, porque a Campanha está
em preparação. Contagens não nulas de iniciadas e concluídas aparecem para A na "coleta
ampla", e todos os casos de contagem no escopo CSAEG ficam nos testes automatizados. Uma
Campanha EM COLETA relevante para Vitória mudaria as situações de entrada consolidadas da
007/008.

**Alternativas consideradas**:

- Mudar B para Serra (versão anterior deste plan): reescreve fixture consolidada da 010.
  Revertido.
- Campanha EM COLETA incluindo Vitória: altera a jornada de Bruno e Carla (007/008).
- Novo operador fictício: desnecessário. B já cobre o caso CSAEG.
- Novas Conclusões fictícias de Vitória: desnecessárias. Já existem três.

**Testes afetados**: nenhum teste existente muda de expectativa. Testes novos verificam:

- os vínculos A/B/C inalterados;
- a nova Campanha nunca aberta, com a baseline, idempotente;
- `situacao_de_entrada` das Pessoas de Vitória inalterada;
- a lista de B e de A, e o detalhe de B.

---

## R15 — Interface

**Decisão**: templates próprios. `acompanhamento/base.html` reutiliza, por `include`, os
estilos `interface/estilo.css` e `editor/estilo.css`, como o editor faz, mais um bloco
pequeno de estilo de tabela.

| Elemento | Decisão |
|----------|---------|
| Título | `<título> — Acompanhamento da coleta — Trajetória Ifes` |
| Faixa | Faixa de demonstração com o texto de ambiente não produtivo da 010 (FR-158) |
| Cabeçalho | "Atuação: …" e "Trocar operador fictício" |
| Navegação | Trilha `nav aria-label="Você está em"` |
| Resumo | `<dl>` ou tabela de duas colunas com definição curta de cada indicador |
| Recorte | `<table>` com `<caption>`, `<th scope="col">` e `<th scope="row">`, dentro de contêiner com `overflow-x: auto`, `tabindex="0"` e `role="region"` com rótulo. Só a tabela rola, nunca a página (FR-123) |
| Seleção de recorte | `<nav aria-label="Recortes">` com links `?recorte=…` e `aria-current` no ativo (FR-059). Sem JavaScript |
| Taxa indisponível | `<span aria-hidden="true">—</span><span class="visualmente-oculto">não se aplica</span>` (FR-124) |
| Barras | Nenhuma barra de progresso no MVP (FR-121: PODE, não DEVE). Números e tabelas bastam |

Termos que nunca aparecem: "dashboard", "KPI", "funil", "abandono", "ranking",
"melhor", "pior" (FR-110, FR-125). Um teste varre o HTML renderizado.

---

## R16 — Privacidade

**Decisão**: o código do app só lê os seguintes campos:

- da Conclusão: `unidade`, `curso`, `nivel`, `modalidade`, `forma_oferta`,
  `ano_conclusao`;
- da Participação: `campanha`, `concluida_em`, além do `id` para `Count`.

Nunca lê: `Pessoa`, `nome`, `id_externo`, `data_conclusao`, `Resposta` ou
`RespostaOpcao`.

Os templates recebem só objetos de valor, sem instâncias de Conclusão ou Participação.

Testes:

- Com Pessoas fictícias de nome e `id_externo` conhecidos, nenhum desses textos e nenhum
  UUID de Conclusão ou Participação aparece no HTML de lista, detalhe ou recortes
  (SC-005).
- A única UUID presente é a da Campanha, no endereço.
- Um teste estrutural (AST) verifica que `trajetoria/acompanhamento` não importa
  `Resposta`, `RespostaOpcao` nem `Pessoa`.

**DP-1101**: sem limiar e sem supressão (FR-082). O plan registra em "Decisões
Pendentes" que **a exposição produtiva dos recortes finos (curso, ano) deve revisitar
DP-1101** quando 010/DP-1001 for resolvida.
