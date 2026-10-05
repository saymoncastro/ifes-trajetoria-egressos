# Research: Minha Trajetória — narrativa visual personalizada

Fase 0 do plan. Cada decisão registra o que foi escolhido, por quê e quais alternativas
foram descartadas. As referências de código são da `main` em `ff12566`.

**Revisão de 2026-10-04 (solicitante).** Duas mudanças depois da primeira versão:

- **P2:** o enriquecimento não viaja mais em `obter_pessoa()`/`PessoaEncontrada`. Passa a
  ter uma fronteira e uma carga próprias, isoladas de 001, 018 e 019 (R1, R12, R13, R14).
- **Card:** o foco é o compartilhamento em rede social no formato vertical,
  especialmente o story do Instagram. O PNG é o artefato principal, o SVG é a
  representação-base, a prévia é a própria imagem salvável e o compartilhamento nativo é
  melhoria progressiva (R8 a R11).

## R1 — Dois apps novos: `narrativa` (sem models) e `contexto_trajetoria` (P2)

- **Decisão:**
  - **`trajetoria/narrativa/`** guarda a montagem, o catálogo de formulações, o card, a
    rasterização, as views e os templates. Não tem models: não persiste nada (FR-015).
  - **`trajetoria/contexto_trajetoria/` (P2)** guarda os dois models
    (`ComplementoDaConclusao`, `ContextoInstitucionalAgregado`) e a carga
    (`carga.py: carregar_contexto(fonte_de_contexto, pessoa)`).
  - **O contrato puro da capacidade** fica em `trajetoria/fonte_academica/contexto_da_trajetoria.py`,
    ao lado de `contrato.py`, sem alterá-lo.
- **Justificativa:**
  - O FR-071 e a revisão do solicitante exigem que identidade, acesso (018), incorporação
    (001) e validação (019) não importem nem conheçam o enriquecimento.
  - `acesso`, `declaracao` e `incorporacao.py` importam `academico.models`. Pôr os models
    novos ali faria a 018 carregar código da 021.
  - Um app próprio torna a fronteira verificável por teste de importação.
  - A narrativa continua só lendo.
- **Alternativas descartadas:**
  - **Models em `academico`:** quebra o isolamento pedido.
  - **Models dentro de `narrativa`:** misturaria "não persiste nada" (FR-015) com dado
    institucional persistido, e a narrativa deixaria de ser só apresentação.
  - **Narrativa dentro de `interface`:** misturaria a jornada da pesquisa, que tem regras
    de "nenhuma ação além de…" (008/014), com a devolutiva.

## R2 — Grão, gatilho e consulta de elegibilidade

- **Decisão:**
  - A narrativa é montada para a Pessoa da sessão (`pessoa_em_uso`, 018).
  - A elegibilidade (FR-001) é uma consulta só:
    `Participacao.objects.filter(conclusao__pessoa=pessoa, concluida_em__isnull=False).exists()`.
  - Participação ancorada em Formação Declarada fica fora por construção:
    `conclusao__pessoa` exige âncora institucional.
  - Inelegível: redireciona para `/formacoes/`. Sem sessão: redireciona para `/acesso/`.
- **Justificativa:**
  - O grão é a Pessoa (clarify).
  - O declarante não tem Pessoa na sessão (`declaracao/sessao.py`).
- **Observação:**
  - Na demonstração, a sessão só admite Pessoa da fonte simulada (`acesso/sessao.py:18`).
  - O caso "Pessoa do acervo" é verificado só na montagem pura. A demonstração não será
    ampliada para ele (decisão do solicitante).

## R3 — `TrajetoriaNarrativa`: dataclasses puras, entrada explícita, serialização versionada

- **Decisão:**
  - `narrativa/contrato.py` define dataclasses congeladas.
  - `narrativa/montagem.py` expõe `montar(entrada) -> TrajetoriaNarrativa`. A `entrada`
    traz nome, formações (já como valores), complementos, agregados já selecionados e
    `referencia: date`.
  - A montagem não consulta banco nem relógio. `narrativa/consultas.py` lê o banco e
    constrói a entrada.
  - `serializar()` produz o formato de [contracts/narrativa.md](contracts/narrativa.md)
    (`"versao_contrato": 1`), em ordem estável.
- **Justificativa:**
  - Mesma entrada, mesmo resultado (FR-011).
  - Testável sem banco.
  - É o formato que a 022 consumirá (FR-014).
- **Alternativas descartadas:**
  - Montar direto dos models: acopla ao ORM.
  - Serializador de terceiros: sem necessidade.

## R4 — Data de referência

- **Decisão:** nas views, `timezone.localdate()`; nos testes, data explícita.
- Data de referência anterior ao ano de conclusão: nenhum tempo decorrido.

## R5 — Regras de ordem e de continuidade (FR-019)

- **Decisão:**
  - **Ordem de exibição:** a do model (`ano_conclusao`, `id`), igual à da 007.
  - **Relação temporal:** existe só entre anos conhecidos e diferentes.
  - **"Depois dessa formação, você também concluiu {curso}.":** acompanha a formação F
    somente quando o grupo de ano imediatamente anterior tem **exatamente uma** formação.
  - **"Primeira formação conhecida":** só quando o menor ano é único.
- **Alternativas descartadas:**
  - Enumerar as formações anteriores na frase.
  - Desempatar por `id`: seria inventar ordem.

## R6 — Tempo decorrido (FR-020)

- **Com data:** "Há N anos desde essa conclusão.", em anos completos. Com N = 0, nada.
- **Só com ano:** rótulo neutro "Concluída em AAAA".
- O tempo decorrido só aparece na página, nunca no card.

## R7 — Catálogo fechado de formulações

- **Decisão:**
  - `narrativa/catalogo.py` traz constantes com placeholders nomeados e condições, no
    estilo de `interface/mensagens.py`.
  - Há variantes para cada ausência.
  - A unidade nunca recebe "Campus".
  - Dois testes: toda frase emitida pertence ao catálogo, e uma varredura das formulações
    vedadas ([contracts/catalogo.md](contracts/catalogo.md)).
- **Alternativa descartada:** frases configuráveis em banco (Princípio XXIII).

## R8 — Página: Django template; a prévia é a imagem que será postada

- **Template:** `narrativa/templates/narrativa/minha_trajetoria.html` estende
  `interface/base.html`, que já inclui os tokens da 015 inline.
- **CSS:** próprio, em `narrativa.css`, incluído no bloco de estilo.
- **Seções:** `<section>` com `<h2>`, só quando há conteúdo. Formações numa `<ol>`
  semântica.
- **Nome:** uma vez, discreto, na seção 1, só se presente.
- **Seção "Seu card"**, pensada para o celular e o story do Instagram:
  - **Prévia:** um `<img>` da própria PNG (`/minha-trajetoria/card.png`, com `?nome=1`
    quando escolhido), em proporção 9:16 e largura limitada pela coluna, com `alt`
    descritivo.
  - **Salvar no celular:** o gesto nativo de tocar e segurar ("Salvar na galeria/Fotos")
    funciona sem JavaScript.
  - **Escolha do nome:** um `<form method="get">` na própria página com a caixa "Incluir meu
    nome no card", só se houver nome, e o botão "Atualizar prévia". Ele recarrega
    `/minha-trajetoria/?nome=1#card`. A prévia e os botões passam a apontar para a versão
    com nome. Não há JavaScript e nada é gravado.
  - **Baixar:** `<a href="card.png[?nome=1]" download="minha-trajetoria-ifes.png">`.
  - **Compartilhar (melhoria progressiva):** um `<button hidden>` revelado por um script
    inline pequeno, só quando `navigator.canShare({files: [File]})` for verdadeiro.
    - Ao tocar, o script busca a mesma PNG, cria um `File` e chama `navigator.share`.
    - O menu de compartilhamento é do sistema operacional. Os destinos listados dependem
      do dispositivo, dos aplicativos instalados e do suporte do navegador. **O sistema
      não garante que o Instagram apareça.** Quando ele não aparece, o caminho é salvar a
      imagem e anexá-la no aplicativo.
    - Sem suporte, ou com JavaScript desligado, o botão continua oculto e os caminhos
      acima bastam (FR-073).
  - **Indisponibilidade do PNG (R11):** a prévia passa a ser o SVG inline, e o botão de
    baixar entrega o SVG.
- **Primeiro JavaScript do projeto:** a 015 FR-037 vedava JavaScript só naquela feature; o
  FR-028 da 021 admite melhoria progressiva. O script:
  - fica inline, com cerca de 20 linhas;
  - não carrega nada de terceiros e não envia dados;
  - não é necessário para ler, salvar nem baixar;
  - fica restrito a esta página, sem entrar em `base.html`.
- **Alternativas descartadas:**
  - **Prévia em SVG inline:** a fonte varia conforme o navegador e não é a imagem que vai
    para a rede.
  - **Botão "Postar no Instagram" por API ou *deep link*:** exige credenciais de aplicativo
    da Meta e envio a terceiros, contra o FR-039.
  - **Página separada só para o card:** uma rota a mais sem ganho.

## R9 — Rotas e respostas

Três rotas GET no app `narrativa`, montadas na raiz:

| Rota | Resposta |
|---|---|
| `/minha-trajetoria/` | Página; `?nome=1` só altera a prévia e os links |
| `/minha-trajetoria/card.png` | `image/png` com `Content-Disposition: inline; filename="minha-trajetoria-ifes.png"`. Abre como imagem (salvável) e serve de `<img>`; o download vem do atributo `download`. Com a rasterização indisponível, 404 |
| `/minha-trajetoria/card.svg` | `image/svg+xml` com `attachment; filename="minha-trajetoria-ifes.svg"`. Só é ligada na página quando o PNG está indisponível; a rota existe sempre, para testes e fallback |

**Regras comuns:**

- `require_GET` e `never_cache`.
- Mesma checagem de elegibilidade.
- `nome=1` só tem efeito com `Pessoa.nome`.
- Nenhum log com dado pessoal.
- Com o modo de demonstração desligado, 404 (`ModoDemonstracaoMiddleware`), o que cumpre o
  FR-069.

## R10 — Card SVG determinístico, vertical 9:16, com área segura

- **Geração:** template Django próprio, alimentado só por `compartilhavel` e pelo tema.
  Mesmo contexto, mesmos bytes; sem data, UUID nem contador.
- **Formato:** **1080 × 1920** (9:16), o story do Instagram e o status de outras redes
  (FR-040).
- **Área segura (FR-072):**
  - Todo texto fica entre y = 270 e y = 1570, com margens laterais de 90 px.
  - As faixas de 0 a 270 (barra de perfil e progresso do story) e de 1570 a 1920 (campo
    de resposta e ações) recebem só fundo ou grafismo dos tokens.
  - Os valores são constantes nomeadas do tema e há teste que garante que nenhum `<text>`
    sai do retângulo.
- **Composição:**
  - título "Minha trajetória no Ifes";
  - nome, se escolhido;
  - até 4 formações, cada uma com curso em destaque e "unidade · nível · modalidade · ano";
  - "e mais N formações registradas" quando houver mais;
  - "N formações registradas no Ifes";
  - em P2, no máximo um par de frases de agregado (o da primeira formação com agregado;
    FR-033);
  - rodapé e marca de demonstração dentro da área segura.
- **Legibilidade no celular:** corpo mínimo de 40 px para texto e 64 px para o título, na
  escala 1080. Contraste AA entre os tokens de texto e de fundo.
- **Quebra de linha:** calculada na montagem do compartilhável, por limite conservador de
  caracteres por linha e por tamanho de fonte. Não corta palavras nem trunca o nome. O teste
  usa o curso mais longo da fonte simulada.
- **Fonte declarada:** `font-family="Open Sans, system-ui, sans-serif"`.
- **Alternativas descartadas:**
  - **4:5 (feed):** fica como direção P3, porque o MVP tem um formato.
  - **Medir texto com `fontTools`:** outra dependência sem ganho proporcional.
  - **Fonte em base64 no SVG:** o SVG não é o artefato compartilhado.

## R11 — PNG: artefato principal, por `resvg-py` com fonte embutida, isolado e com fallback

- **Decisão:**
  - **Biblioteca:** o PNG é rasterizado do mesmo SVG com `resvg-py` (MIT; *wheels* abi3
    para manylinux, musllinux e macOS x86_64/arm64, sem biblioteca de sistema).
  - **Chamada:** `svg_to_bytes(svg_string=…, font_files=[…], skip_system_fonts=True)`.
  - **Uso isolado:** só em `narrativa/rasterizacao.py: png_de(svg) -> bytes | None`.
- **Fontes:** Open Sans (SIL OFL 1.1), **só os pesos usados pelo template: Regular e
  Bold**, com `OFL.txt`, em `trajetoria/narrativa/fontes/`.
  - É a fonte que já compõe a assinatura do Ifes.
  - Não é servida ao navegador, por isso a D-04 da 015 não muda.
  - Não há família tipográfica, variações nem sistema de fontes.
- **Spike obrigatório, primeira tarefa da fatia PNG, antes de assumir o PNG como
  requisito irremovível:**
  - instalar e renderizar **no CI** (ubuntu, Python 3.13) e no macOS arm64;
  - gerar o mesmo PNG duas vezes no mesmo processo e comparar os bytes;
  - conferir acentos e "ç" com a fonte embutida;
  - medir o tempo de rasterização de um card 1080 × 1920.
- **Se o spike falhar ou a dependência for recusada:**
  - `png_de` devolve `None`;
  - a rota PNG dá 404;
  - a página mostra o SVG e o download do SVG.
  - O resultado e a razão ficam registrados na ADR.
  - **O fallback SVG mantém a página funcionando, mas não cumpre o objetivo do story**: as
    redes não aceitam SVG. Por isso uma falha do spike é **porta de decisão**. A
    implementação para e a alternativa é levada ao solicitante antes de seguir com o card.
    Não basta entregar só o SVG.
- **Entrada da dependência:** `pyproject.toml`, `uv.lock`, `tests/dependencias.py`
  (justificativa) e a **ADR 0006**.
- **Alternativas descartadas:**
  - cairosvg ou pyvips: dependem de biblioteca de sistema (Cairo, libvips). O solicitante
    vetou Cairo.
  - Pillow desenhando: dois renderizadores divergentes.
  - Canvas no navegador: depende do dispositivo e exige JavaScript para gerar.
  - Chromium headless: reservado à 022.

## R12 — Capacidade de contexto da trajetória: contrato separado da `FonteAcademica`

- **Decisão:** módulo puro `trajetoria/fonte_academica/contexto_da_trajetoria.py`, sem
  Django:
  - `ComplementoNaFonte(id_externo_conclusao, ano_ingresso, data_ingresso=None)`.
  - `MetricaAgregada`, enumeração fechada com `CONCLUSOES_CURSO_UNIDADE_ANO` e
    `CONCLUSOES_UNIDADE_ANO`.
  - `AgregadoNaFonte(metrica, unidade, ano, valor, apurado_em, curso=None)`.
  - `ContextoDaTrajetoriaNaFonte(complementos: tuple, agregados: tuple)`.
  - `ContextoIndisponivel(Exception)`: própria, distinta de `FonteAcademicaIndisponivel`.
  - `FonteDeContextoDaTrajetoria(Protocol)` com `codigo: str` e
    `obter_contexto(ids_externos_conclusoes: tuple[str, ...]) -> ContextoDaTrajetoriaNaFonte`.
- **Regras do contrato** (validadas no `__post_init__`):
  - complemento só para ids pedidos, um por id, ano/data coerentes;
  - agregado com curso só na métrica 1, `valor >= 0`, sem cadeia vazia;
  - sem chave repetida na resposta.
- **Não muda:** `contrato.py` inteiro, ou seja, `ConclusaoNaFonte`, `PessoaEncontrada`,
  `CAMPOS_DE_CONTEXTO` e o protocolo `FonteAcademica`.
- **Mesma view, dois contratos:** um adaptador real pode ser uma única classe que lê uma
  view larga e implementa os dois protocolos. Ou duas classes sobre a mesma consulta. Em
  ambos os casos quem separa é o adaptador, e o `codigo` é o mesmo da fonte das Conclusões.
- **Justificativa:** a 018 usa `obter_pessoa()` no caminho de identidade e material de
  verificação. O enriquecimento não pode pesar nem falhar ali (FR-071).
- **Alternativas descartadas:**
  - **Campos em `PessoaEncontrada`** (versão anterior): transformam a resposta da 018 numa
    sacola de dados da 021.
  - **Operação nova no protocolo `FonteAcademica`:** obriga toda fonte fundamental
    (inclusive o acervo da 019) a conhecer a 021.
  - **Abstração genérica de "enriquecimentos":** sem segundo caso de uso (Princípio XXII).

## R13 — Carga separada, isolada e tolerante a falha

- **Função:** `contexto_trajetoria/carga.py: carregar_contexto(fonte_de_contexto, pessoa) ->
  ResultadoDaCarga`.
- **Passos:**
  1. Seleciona as Conclusões da Pessoa com `fonte == fonte_de_contexto.codigo`. Sem
     nenhuma, encerra.
  2. Chama `obter_contexto(ids)` **fora de transação**. Com `ContextoIndisponivel`, devolve
     "indisponível" e não grava nada (FR-062). A exceção não se propaga.
  3. Abre uma transação própria e grava:
     - **complemento novo:** cria;
     - **complemento igual:** nada;
     - **complemento diferente:** divergência sinalizada, nada muda (FR-048, FR-049);
     - **agregado com chave nova:** `get_or_create`;
     - **agregado com mesma chave e mesmo valor:** nada;
     - **agregado com mesma chave e valor diferente:** erro de fonte em log, nada gravado
       (FR-057).
  4. Os logs saem depois do commit (`on_commit`), só com código da fonte, métrica, recorte
     e id externo da Conclusão, como as divergências da 001.
- **Quem chama:**
  - **Demonstração:** `preparar_demonstracao`, depois de incorporar todas as Pessoas, chama
    `carregar_contexto(ContextoSimulado(), pessoa)` para cada uma, num *savepoint* próprio.
    Uma falha registra aviso e o preparo continua (FR-071).
  - **Integração real:** segue a mesma pendência do gatilho de incorporação (001/DP-006).
  - **Nunca é chamada por:** `incorporacao.py`, `acesso` nem `declaracao`.
  - **Nunca é chamada na view da narrativa.** Abrir a página não grava nada (FR-008).
- **Garantia por teste:**
  - nenhum módulo de `trajetoria/acesso`, `trajetoria/declaracao` nem
    `trajetoria/academico` importa `contexto_da_trajetoria`, `contexto_trajetoria` ou
    `narrativa`;
  - com `ContextoSimulado(indisponivel=True)`, preparo, login, resposta e narrativa P1
    funcionam (SC-014).

## R14 — Seleção da apuração e coerência (FR-058 a FR-060)

`narrativa/consultas.py`, para cada Conclusão com curso, unidade e ano e para cada
métrica:

1. lê `ContextoInstitucionalAgregado` da **mesma fonte** da Conclusão, com recorte exatamente
   igual;
2. se houver **exatamente um**, segue; com zero ou dois ou mais, omite, sem ordenar por
   nada;
3. conta as `ConclusaoAcademica` da mesma fonte no recorte. Se a contagem for maior que o
   valor, omite e registra log sem dado pessoal. A contagem é só uma trava, nunca o valor.

**Métrica 2:** é deduplicada por unidade e ano quando a Pessoa tem duas Conclusões no mesmo
recorte.

**Leitura:** a narrativa lê os models de `contexto_trajetoria`. É leitura, não carga.

## R15 — Antecipação do benefício (FR-070)

- **Decisão:** uma frase fixa em `interface/mensagens.py`: `ANTECIPACAO = "Ao final, você
  poderá ver sua trajetória no Ifes."`.
- **Onde aparece:** em `/formacoes/`, só com pesquisa a iniciar ou retomar.
- **Onde não aparece:** nas Seções, na Versão nem no caminho da 019.

## R16 — `/formacoes/` passa a "Suas formações no Ifes" (aprovado)

- "Suas formações no Ifes" é o contexto acadêmico e a entrada. "Minha trajetória no Ifes"
  é a devolutiva.
- Muda o título de `/formacoes/` (`TITULO_TRAJETORIA`) e a ligação de `aviso.html` ("Ver
  suas formações no Ifes").
- Revisa a 014 FR-030.
- Os testes `test_interface_formacoes.py:319-324` e `test_interface_conclusao.py:143, 256`
  são ajustados.

## R17 — Testes

`tests/narrativa/` e `tests/contexto_trajetoria/` (pytest-django):

- **`test_montagem.py`** (puro): ordem, continuidade, tempo, ausências, nome, determinismo,
  acervo sem nome.
- **`test_catalogo.py`:** toda frase pertence ao catálogo; varredura das vedadas em todos
  os cenários (P1 e P2).
- **`test_rotas.py`:**
  - elegibilidade, sessão expirada e declarante;
  - `no-store`;
  - `Content-Disposition` (inline no PNG, attachment no SVG);
  - `?nome=1` na página altera a prévia e os links;
  - modo demonstração desligado → 404.
- **`test_card.py`:**
  - SVG idêntico byte a byte;
  - 1080 × 1920;
  - todo `<text>` dentro da área segura;
  - campos vedados ausentes;
  - nome só com `nome=1`; nome ausente na fonte;
  - limite de 4 formações e "e mais N";
  - marca de demonstração;
  - corpo mínimo de fonte.
- **`test_png.py`:** assinatura PNG, 1080 × 1920 e reprodutibilidade. É pulado com motivo
  explícito se `png_de` for `None`.
- **`test_pagina_card.py`:**
  - a prévia é um `<img>` da PNG com `alt`;
  - o link de baixar tem `download`;
  - o botão "Compartilhar" está `hidden` no HTML (sem JavaScript continua invisível);
  - o script é inline, sem URL externa;
  - com o PNG indisponível, a página mostra o SVG e o download do SVG.
- **`test_sem_efeito.py`:** contagem de linhas antes e depois de abrir e baixar.
- **`test_fronteiras.py`:**
  - `CAMPOS_DE_CONTEXTO` com os sete atributos;
  - campos de `PessoaEncontrada` iguais aos de hoje;
  - `RegistroDoSnapshot` igual;
  - `COLUNAS_BASE`/`VERSAO_CONTRATO` da 013 iguais;
  - a narrativa não lê `Resposta` nem importa `analitico` ou `acompanhamento`;
  - **acesso, declaração e academico não importam a capacidade nem os apps da 021**
    (FR-071).
- **`tests/contexto_trajetoria/test_contrato.py`:** validações das estruturas puras e do
  protocolo; o módulo não importa Django.
- **`tests/contexto_trajetoria/test_carga.py`:**
  - complemento: criação, idempotência, divergência sem alteração, acréscimo posterior;
  - agregado: deduplicação entre Pessoas, erro de fonte;
  - indisponível não grava nada, e a Pessoa e as Conclusões ficam intactas.
- **`tests/contexto_trajetoria/test_isolamento.py`:** com o contexto indisponível, preparo
  da demonstração, login (018), resposta e narrativa P1 funcionam (SC-014).
- **`test_agregados.py`** (narrativa):
  - exatamente uma apuração → exibe; duas → omite;
  - coerência com a base local;
  - fonte diferente;
  - sem agregado → seção ausente;
  - frases com sujeito "conclusões".
- **SC-008:** 500 Pessoas do mesmo recorte carregadas → um registro por métrica e
  apuração. Marcado `volume`; na suíte padrão roda com 20.
- **Ajustes em testes existentes:** `tests/interface/test_interface_conclusao.py` (FR-003),
  `test_interface_formacoes.py` (R15, R16) e o preparo da demonstração (carga de contexto
  no fim).

## R18 — Fonte simulada de contexto e documentação do cenário (P2)

- **Dados:** `fonte_academica/cenarios.py` ganha `COMPLEMENTOS` e `AGREGADOS`, fictícios:
  - `SIM-C-0001` (Ana) → ingresso 2019;
  - TADS · Serra · 2022 → 27;
  - Serra · 2022 → 812, ambos apurados em 2026-01-31;
  - nenhum agregado para Vila Velha nem Cefor.
- **Classe:** o novo módulo `fonte_academica/contexto_simulado.py` define
  `ContextoSimulado` (`codigo = "simulada"`, parâmetro `indisponivel`).
  - Implementa só `FonteDeContextoDaTrajetoria`.
  - Usa `cenarios.REGISTROS` para saber os recortes das conclusões pedidas.
- **`FonteSimulada` não muda.**
- **Casos negativos** (duas apurações, valor incoerente, mesma chave com valor diferente,
  ingresso posterior): só em fontes de teste parametrizadas.
- **Documentação:** `specs/001-nucleo-academico-fonte-simulada/contracts/cenarios-simulados.md`
  ganha uma seção "Contexto da trajetória (021)", porque `cenarios.py` declara
  reproduzi-lo.
  - `contracts/fonte-academica.md` da 001 ganha só uma nota: "a capacidade de contexto da
    trajetória é separada; ver 021".
