# Research: Gestão mínima de Campanha

Base: `main` `5e50fec`. Nenhum item da Technical Context ficou como NEEDS CLARIFICATION: a
stack, o shell e os padrões já existem. As decisões abaixo dizem **onde** e **como** reutilizar.

## R1 — Onde vive o código da 017

- **Decision**: subpacote `trajetoria/acompanhamento/gestao/` (`formularios.py`,
  `mensagens.py`, `painel.py`, `views.py`) e templates em
  `acompanhamento/templates/acompanhamento/gestao/`. A barreira `@gestao` fica em
  `acompanhamento/acesso.py`, ao lado de `@acompanhamento`. As rotas entram em
  `acompanhamento/urls.py`. `trajetoria/campanha` continua sendo o domínio e não conhece a
  interface. Nenhum app novo, nenhuma mudança em `INSTALLED_APPS`.
- **Rationale**: a 017 não introduz domínio nem persistência; é apresentação e orquestração
  das operações da 004 dentro do shell administrativo que já é da 011. Não há fronteira
  concreta no código que justifique um app: a 016 virou app porque tem domínio próprio
  (contatos, convite, operação de simulação, transporte), o que não ocorre aqui. O
  subpacote mantém `acompanhamento/views.py` (011) somente leitura e GET, separando o lado
  de escrita sem criar outro módulo de topo.
- **Alternatives considered**: app `trajetoria.gestao_campanha` (correspondência 1:1 com a
  feature, sem fronteira de domínio — rejeitada pelo solicitante e por XXII); views de
  escrita em `acompanhamento/views.py` (mistura escrita no módulo declarado somente
  leitura); módulo em `/gestao/` (paralelo ao shell, contra FR-006).

## R2 — Regra de capacidade

- **Decision**: `pode_gerir_campanha(vinculos)` em `trajetoria/governanca/regras.py`:
  `any(v.ativo and v.papel == Papel.CPAEG for v in vinculos)`. Função própria, mesmo com o
  critério idêntico a `pode_elaborar_instrumento`, documentada como interpretação C1
  restrita à demonstração.
- **Rationale**: 010 já separa regras com o mesmo critério ("consultar rascunho" e
  "elaborar") para que cada uma evolua com sua decisão; DP-402 pode mudar só esta.
- **Alternatives considered**: reaproveitar `pode_elaborar_instrumento` (amarraria gestão
  de Campanha à elaboração do questionário); `escopo_de_acompanhamento(...).institucional`
  (amarraria gestão ao acompanhamento).

## R3 — Barreira das rotas de gestão

- **Decision**: decorador `@gestao` em `acompanhamento/acesso.py`, o mais externo:
  1. modo de demonstração desligado → 404, verificado também aqui (defesa em profundidade:
     a capacidade só existe na demonstração, C1), além do middleware da 008;
  2. `vinculos_do_operador_em_uso` → sem operador, redirect à escolha com destino
     `acompanhamento`;
  3. sem `pode_gerir_campanha`, `recusa()` da 011 (403);
  4. define `request.atuacao`. Marcador `envolvida.gestao = True`.
  Campanha inexistente → 404. Como só a CPAEG passa, toda Campanha existente é visível
  (escopo institucional); não há caso "fora do escopo". `pode_gerir_campanha` continua pura
  (sem settings), como as demais regras da 010.
- **Rationale**: mesmo desenho de `@acompanhamento` e `@comunicacao`. A verificação de modo
  dentro da barreira garante que a interpretação provisória não vaze se o middleware for
  reorganizado.
- **Alternatives considered**: empilhar `@acompanhamento` + verificação interna (duas
  barreiras na mesma rota, contra o teste de inventário).

## R4 — Pontos de entrada nas páginas da 011

- **Decision**: `Atuacao` (011) ganha o campo `gerir_campanha: bool = False`, preenchido por
  `@acompanhamento` com `pode_gerir_campanha`. Com ele verdadeiro, a lista mostra "Nova
  Campanha" e a view de detalhe acrescenta ao contexto o bloco de gestão calculado por
  `acompanhamento.gestao.painel.painel(campanha, agora)`; `campanha.html` inclui
  `acompanhamento/gestao/_painel.html` só nesse caso. Para CSAEG, o HTML não muda.
- **Rationale**: integração ao shell existente (FR-006) sem tornar a 011 dependente da
  lógica de gestão; a lista e o detalhe continuam GET (FR-007).
- **Alternatives considered**: página de gestão separada por Campanha (duplicaria o
  detalhe); `request.vinculos` exposto aos templates (decisão de capacidade fora das regras).

## R5 — Impedimentos de abertura sem duplicar a regra

- **Decision**: extrair de `operacoes.abrir` a verificação para
  `campanha.consultas.impedimentos_de_abertura(campanha, *, agora=None) -> tuple[Violacao, ...]`:
  relê o estado da Versão, verifica período não definido e fora do período, na mesma ordem
  e com os mesmos `Motivo`, `campo` e `detalhe`. `abrir` passa a chamá-la depois do bloqueio
  e do tratamento de "já aberta"; o comportamento de `abrir` não muda. A apresentação
  distingue "antes do início" e "período encerrado" comparando a data de referência com
  `inicio`/`fim` só para escolher o texto; a decisão de haver impedimento é da 004.
- **Rationale**: FR-016 e FR-026 pedem uma única regra; hoje ela só existe dentro da
  transação de `abrir`.
- **Alternatives considered**: tentar `abrir` num savepoint e desfazer (grava e bloqueia
  linha em GET); reimplementar as condições na interface (duas regras divergentes).
- **Verificação**: teste de equivalência — para os mesmos dados e `agora`, os motivos de
  `CampanhaRejeitada` de `abrir` são exatamente os de `impedimentos_de_abertura`; as suítes
  da 004 continuam verdes sem alteração.

## R6 — Criar e editar com várias operações e todas as mensagens

- **Decision**: a view chama as operações da 004 dentro de `transaction.atomic()`; cada
  operação roda num savepoint próprio, e cada `CampanhaRejeitada` vira erro de campo pelo
  mapa `Motivo → (campo, texto)`. Havendo qualquer erro, a transação externa é desfeita e o
  formulário volta com os valores digitados (422). Criar: `criar_campanha(nome, versao)`;
  se houver alguma data, `definir_periodo(inicio, fim)`. Editar: `alterar_campanha(nome=,
  versao=)`; se houver alguma data, `definir_periodo`. Motivo fora do mapa é erro de
  programa (relançado), como no editor.
- **Rationale**: nenhuma regra de domínio no formulário (FR-014); criação e período juntos
  ou nada (FR-008, FR-011).
- **Alternatives considered**: validar período no formulário (duplicaria 004 FR-012);
  parar no primeiro erro (contra US1 cenário 3).
- **Dados sem regra de domínio, tratados na interface**: data em formato inválido (erro
  de entrada); Versão fora das opções oferecidas (escolha inválida); ambas as datas vazias
  numa Campanha que já tem período (FR-010: corrigir sim, remover não — a 004 não tem
  operação de remoção de período).

## R7 — Escolha de Versão

- **Decision**: `ChoiceField` com `(pk, "Pesquisa — designação")` das Versões
  `PUBLICADA`, ordenadas por nome da Pesquisa e designação. Na edição, se a Versão atual
  estiver em rascunho, ela entra como primeira opção com o sufixo "(não publicada — impede
  a abertura)". Sem Versão publicada, "Nova Campanha" mostra a explicação, sem formulário.
- **Rationale**: FR-009, FR-012; rótulo igual ao do acompanhamento.
- **Alternatives considered**: `ModelChoiceField` (o padrão do editor proíbe formulários
  ligados a modelos e quer rótulos controlados).

## R8 — Datas

- **Decision**: `DateField` com `<input type="date">` (envio ISO), `required=False`;
  formato inválido → mensagem fechada "Informe a data no formato dia/mês/ano." Exibição
  `d/m/Y` como em `_periodo.html`.
- **Rationale**: controle nativo acessível e móvel, sem JavaScript; a timezone é a do
  projeto (004).

## R9 — Abrir e encerrar

- **Decision**: GET mostra a confirmação; POST chama `abrir` ou `encerrar` e redireciona
  ao detalhe com `?aviso=<código>` de lista fechada (padrão do editor). Abrir: se houver
  impedimentos no GET, a página mostra os impedimentos e nenhum formulário; no POST,
  `CampanhaRejeitada` → página de confirmação com os impedimentos atuais, 409;
  `JA_EM_COLETA`/`JA_ENCERRADA` → detalhe com aviso do estado atual. Encerrar: só oferecido
  EM COLETA; Campanha nunca aberta → 409 explicando; `JA_ENCERRADA` → aviso. A confirmação
  de abertura lista outras Campanhas EM COLETA (nomes) com o aviso fixo de FR-019 — consulta
  simples por estado, sem interseção. Respostas com `Cache-Control: no-store`
  (`never_cache`), como no editor.
- **Rationale**: FR-017 a FR-021; PRG evita reenvio; repetir é idempotente pelo domínio.

## R10 — Rótulo da Campanha nunca aberta e expirada

- **Decision**: `CampanhaAcompanhada.situacao` (011) devolve "Período encerrado — Campanha
  nunca aberta" quando o estado é ENCERRADA e `aberta_em` é nulo; o restante do detalhe da
  011 (aviso "não chegou a entrar em coleta", linha de encerramento) fica como está.
- **Rationale**: FR-023a vale para todos os operadores, na lista e no detalhe; uma única
  propriedade alimenta as duas páginas. A 016 usa o estado de domínio, não o rótulo, e não
  muda.

## R11 — Mensagens

- **Decision**: `acompanhamento/gestao/mensagens.py` com vocabulário fechado: rótulos, ajuda,
  mapa de motivos, impedimentos (causa + correção), textos de confirmação, aviso de
  sobreposição, avisos pós-ação, recusas e aviso de abrangência restrita. Nenhum nome de
  `Motivo` ou identificador aparece ao operador (FR-028).

## R12 — Testes

- **Decision**: testes em `tests/acompanhamento/test_gestao_*.py`, com as fixtures do
  acompanhamento (operadores A/B/C, construtor de Campanhas da 011). Equivalência de
  impedimentos em `tests/campanha/`. Os testes de inventário da 011 e da 016 deixam de
  fixar a **quantidade** de rotas (não é invariante de produto) e passam a verificar
  semanticamente: toda rota sob `/acompanhamento/` tem exatamente uma barreira
  (`acompanhamento`, `comunicacao` ou `gestao`); as rotas de comunicação têm a barreira da
  016; toda rota que aceita POST de gestão tem `gestao`; lista e detalhe da 011 só aceitam
  GET. A autorização de gestão é testada por comportamento (CPAEG, CSAEG, sem vínculo, sem
  operador, vínculo revogado, modo desligado) em cada rota de gestão.
- **Rationale**: matriz mínima da spec; independência dos testes (Const. XXV).
