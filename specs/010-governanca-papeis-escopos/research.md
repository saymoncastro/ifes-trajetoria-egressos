# Research: Governança, papéis e escopos institucionais

**Feature**: 010 | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Fase 0. Não há `NEEDS CLARIFICATION` no Technical Context: as quatro decisões pré-plan
estão na seção *Clarifications* da spec. Cada item abaixo registra **Decisão**,
**Justificativa** e **Alternativas rejeitadas**. As referências de código são do estado
atual da branch (Feature 009 incluída).

## Fatos do código que condicionam o desenho

| Fato | Onde | Consequência |
|------|------|--------------|
| Não há `django.contrib.auth`, `sessions`, `admin` nem `contenttypes`; não há `request.user`, superusuário ou `is_staff` | `config/settings.py:30-51` | Não existe privilégio técnico a neutralizar; nada disso é adicionado (R10) |
| Um teste proíbe autenticação e sessão | `tests/participacao/test_entrada_aceitacao.py::test_10_nenhum_mecanismo_de_autenticacao` | A identificação não produtiva não pode usar sessão; continua usando cookie assinado (R6) |
| O modo de demonstração responde 404 a **toda** requisição quando desligado, antes de qualquer view | `trajetoria/demonstracao/middleware.py` | Produção continua fechada sem mudança no gate (R7) |
| A 008 identifica a Pessoa fictícia por cookie assinado, revalidado a cada requisição, aceitando só Pessoas da fonte simulada | `trajetoria/demonstracao/entrada.py` | Padrão reaproveitado para o operador fictício (R6) |
| Unidade é texto livre em `ConclusaoAcademica.unidade` e em `Campanha.unidades`; não há tabela de unidade, por decisão da 001 (R10) e da 004 | `academico/models.py:48`; `campanha/models.py:50` | Unidade do vínculo é texto (R3) |
| Restrição de não vazio do projeto: `CheckConstraint(~Q(campo=""))` | `academico/models.py:14`; `instrumento/models.py` | Mesmo padrão no vínculo (R3) |
| As 25 views do editor usam `_respondendo`/`_Resposta` para interromper com resposta pronta | `trajetoria/editor/views.py:31-46` | O gate de consulta por estado da Versão usa o mesmo mecanismo (R8) |
| O editor tem fronteira de importação verificada por `ast` e proíbe `demonstracao` | `tests/editor/test_editor_fronteiras.py::PERMITIDOS` | Ampliação explícita e mínima da lista (R12) |
| `publicar` é chamado só pelo preparo da demonstração e por testes | `demonstracao/cenario.py:117`; `tests/**` | Nada muda (R11) |
| Apps de domínio não têm `urls.py`, `views.py`, `admin.py`, `forms.py`, `middleware.py` | `test_entrada_aceitacao.py::test_10` | O app de governança segue a mesma forma (R1) |

## R1 — Um app pequeno `trajetoria/governanca`

**Decisão**: criar o app `trajetoria.governanca`, de domínio, com:

- `models.py` — `Papel` (`TextChoices`) e `VinculoDeGovernanca`;
- `regras.py` — as três regras puras de capacidade;
- `consultas.py` — `vinculos_ativos(identificador)`;
- `operacoes.py` — `registrar_vinculo`, `desativar_vinculo` e a rejeição;
- `migrations/0001_initial.py`.

Sem `urls.py`, `views.py`, `admin.py`, `forms.py`, `middleware.py`, `management/` nem
templates, como os demais apps de domínio.

**Justificativa**: governança é responsabilidade transversal distinta do instrumento.
Colocar o vínculo em `instrumento` acoplaria governança a Pesquisa/Versão; colocá-lo em
`editor` faria o futuro consumidor (Feature 011) depender do editor. Um app com um modelo
e quatro módulos curtos é a menor forma que mantém a fronteira.

**Alternativas rejeitadas**:

- **Vínculo dentro de `trajetoria/editor`**: o editor é camada de interface sem modelos
  (009 `test_sem_modelos_nem_migracoes`); governança não pertence a uma tela.
- **Vínculo em `academico`**: misturaria operador institucional com Pessoa e Conclusão
  (spec FR-008).
- **django-guardian, django-rules, Casbin ou similar**: dependência nova para três
  regras fixas (spec FR-034; Const. XXII). O teste da 009 fixa as dependências do
  `pyproject.toml`.

## R2 — Operador representado só por um identificador opaco no vínculo

**Decisão**: não há modelo de operador. O operador é a string
`identificador_operador`, gravada no vínculo e devolvida pela identificação. A regra de
autorização nunca interpreta o formato dela.

O **contrato futuro de identidade** (DP-1001) terá uma única obrigação perante esta
feature: resolver a requisição para esse identificador estável antes da autorização,
ou para `None`. A correspondência entre a identidade institucional (por exemplo, login
do Ifes) e o identificador é dele, não desta feature.

**Justificativa**: o único atributo do operador necessário à autorização é a identidade.
Nome, e-mail, matrícula, cargo e lotação pertencem ao futuro mecanismo de identidade
(spec FR-009; Const. XVI). Com operador só como string, um operador sem vínculo não
precisa existir em lugar nenhum: ele é simplesmente um identificador sem linhas ativas.

**Alternativas rejeitadas**:

- **Modelo `Operador` + FK no vínculo**: segunda tabela sem atributo próprio (spec
  FR-025); exigiria cadastrar operador antes do vínculo.
- **`django.contrib.auth.User` como âncora**: traz senha, superusuário e `is_staff`, que a
  spec manda não usar como autorização (FR-067), e quebra o teste de ausência de
  autenticação. Seria acrescentar privilégio técnico só para depois neutralizá-lo.
- **E-mail ou CPF como identificador**: dado pessoal, e convida a inferir unidade do
  domínio do e-mail (spec FR-007).

## R3 — Campos e restrições do vínculo

**Decisão**: `VinculoDeGovernanca` com cinco campos: `id` (UUID, padrão do projeto),
`identificador_operador`, `papel`, `unidade` (texto **não nulo**: vazio para CPAEG,
não vazio para CSAEG) e `ativo`. Restrições de banco, todas locais à linha:

| Nome | Regra |
|------|-------|
| `vinculo_identificador_nao_vazio` | `identificador_operador <> ''` |
| `vinculo_papel_valido` | `papel IN ('CPAEG', 'CSAEG')` |
| `vinculo_unidade_conforme_papel` | `(papel = 'CPAEG' AND unidade = '') OR (papel = 'CSAEG' AND unidade <> '')` |
| `vinculo_unico` | único em `(identificador_operador, papel, unidade)` |

**Escopo não é persistido**: ele é derivado do papel (CPAEG ⇒ institucional; CSAEG ⇒
unidade). Não há enum CENTRAL/UNIDADE; a única expressão da relação é a restrição
`vinculo_unidade_conforme_papel` e a propriedade de leitura que monta o rótulo.

**Unidade**: texto exatamente como informado, sem catálogo nem normalização
(DP-1005; 001 R10; 004). A operação recusa texto vazio ou só com espaços e texto com
espaços nas pontas, para evitar duas grafias invisíveis da mesma unidade; ela não
corrige o texto.

**Sem** datas, portaria, documento, observação, autor, histórico ou versão (spec FR-026;
Clarifications).

**Justificativa**: as restrições expressam só invariantes da própria linha (spec FR-019,
FR-020), sem trigger nem dependência de outra tabela. Com unidade **vazia** (e não nula)
para CPAEG, a unicidade simples de três colunas vale também para CPAEG, sem depender da
semântica de nulo em índice único (Clarifications 2026-10-02).

**Alternativas rejeitadas**:

- **Coluna `escopo`**: repetiria o papel e criaria combinações inválidas a vigiar.
- **`unidade` nula para CPAEG com `nulls_distinct=False`**: funciona no PostgreSQL 15+,
  mas faz a unicidade depender de semântica específica de nulo; a unidade vazia é mais
  simples e portável (Clarifications 2026-10-02).
- **Unicidade parcial só entre ativos** (`condition=Q(ativo=True)`): permitiria várias
  linhas inativas idênticas, que é um histórico implícito sem consumidor. Ver R4.
- **Validação de unidade contra `ConclusaoAcademica.unidade`**: dependência de outra
  tabela e recusa de unidade legítima sem egresso registrado (spec, Edge Cases).

## R4 — Regra de duplicidade: uma linha por (operador, papel, unidade), reativável

**Decisão**: existe no máximo **uma** linha para cada combinação de operador, papel e
unidade, ativa ou inativa (`vinculo_unico`).

- `registrar_vinculo` sobre combinação inexistente → cria ativa.
- `registrar_vinculo` sobre combinação existente **inativa** → reativa a mesma linha.
- `registrar_vinculo` sobre combinação existente **ativa** → rejeição `JA_ATIVO`.
- `desativar_vinculo` sobre ativa → inativa.
- `desativar_vinculo` sobre inativa → rejeição `JA_INATIVO`.
- Não há exclusão.

**Justificativa**: é a menor regra que impede vínculos ativos redundantes (spec FR-020) e
não acumula linhas. `ativo` responde só "concede autorização agora?" (Clarifications).
Reativar a mesma linha é mais simples que criar outra idêntica e não sugere mandato nem
histórico. As rejeições explícitas tornam o resultado observável nos testes e no preparo.

**Alternativas rejeitadas**:

- **Nova linha a cada designação**: histórico implícito sem consumidor (009/DP-903).
- **Operações idempotentes silenciosas**: esconderiam um registro redundante; o preparo
  da demonstração verifica a existência antes de registrar (R9).
- **Operação `reativar` separada**: mais uma operação para o mesmo efeito de
  `registrar_vinculo` sobre linha inativa.

## R5 — Capacidades: três funções puras sobre os vínculos

**Decisão**: `trajetoria/governanca/regras.py` expõe exatamente:

```text
pode_consultar_publicado(vinculos) -> bool   # algum vínculo ativo (CPAEG ou CSAEG)
pode_consultar_rascunho(vinculos)  -> bool   # algum vínculo ativo CPAEG
pode_elaborar_instrumento(vinculos) -> bool  # algum vínculo ativo CPAEG
```

- Recebem um iterável de vínculos e **só** isso; não acessam banco, requisição, settings
  nem modo de demonstração.
- Conferem `ativo` elas mesmas: um vínculo inativo passado por engano não autoriza.
- Capacidade é a existência de **algum** vínculo ativo que a conceda; não há precedência
  nem "papel ativo" (spec FR-021).
- A unidade não entra em nenhuma regra (spec FR-017).

`trajetoria/governanca/consultas.py` expõe `vinculos_ativos(identificador)`, uma
consulta, ordenada por papel e unidade (apresentação). Para `None` ou texto vazio devolve
lista vazia sem consultar o banco.

**Justificativa**: o conjunto é fixo pela spec (FR-028, FR-035). Funções nomeadas por
ação concreta são mais legíveis e testáveis que uma tabela de permissões. Separar
consulta (banco) de regra (pura) permite testar a matriz com vínculos não gravados.

**Alternativas rejeitadas**:

- **Enum `Capacidade` + dicionário papel → capacidades**: é um registro de capacidades
  em miniatura (spec FR-034); três funções de uma linha bastam.
- **Tabela de permissões ou `Permission` do Django**: proibido (FR-025, FR-034).
- **Uma regra que receba a Versão** (`pode_consultar(vinculos, versao)`): misturaria
  estado do instrumento com governança; a escolha entre publicado e rascunho fica no
  gate do editor (R8).

## R6 — Identificação não produtiva: operador fictício por cookie assinado

**Decisão**: novo módulo `trajetoria/demonstracao/operador.py`, no app que já é o
adaptador temporário de identidade da 008:

- `OPERADORES_FICTICIOS`: tupla fixa no código com os três operadores fictícios
  (identificador e rótulo de apresentação):
  - `demonstracao:operador-a` — "Operador fictício A";
  - `demonstracao:operador-b` — "Operador fictício B";
  - `demonstracao:operador-c` — "Operador fictício C".
- `operador_em_uso(request) -> str | None`:
  - com o modo desligado, devolve `None` **sem ler cookie**;
  - lê um cookie assinado próprio (`trajetoria_demonstracao_operador`, sal próprio);
  - aceita o valor **somente** se estiver em `OPERADORES_FICTICIOS`; qualquer outro valor,
    assinatura inválida ou ausência → `None`;
  - lido uma vez por requisição.
- `usar_operador(response, identificador)` (recusa identificador fora da tupla) e
  `esquecer_operador(response)`.

Rotas novas no app `demonstracao`, ao lado das da Pessoa fictícia (contrato em
[demonstracao-operador.md](contracts/demonstracao-operador.md)):

- `GET /demonstracao/operador/` — lista os três operadores fictícios, cada um com as
  atuações **lidas dos vínculos** (ou "sem atuação institucional ativa"), e o operador em
  uso;
- `POST /demonstracao/operador/escolher/` — grava o cookie e redireciona para
  `/editor/`;
- `POST /demonstracao/operador/encerrar/` — apaga o cookie.

A escolha **identifica** e nunca autoriza: as atuações exibidas vêm dos vínculos, e o
editor decide só pela regra (spec FR-056). O operador C demonstra a recusa.

**Justificativa**:

- Mesmo padrão já aceito da 008 (cookie assinado, lista fechada, revalidação por
  requisição), sem sessão nem autenticação, o que mantém o teste de ausência de
  autenticação verde.
- Lista fechada no código cumpre FR-057: nenhum vínculo registrado para identificador
  real é selecionável, mesmo com o modo ligado por engano num banco com vínculos reais.
- A escolha de operador é independente da escolha de Pessoa (spec FR-055): cookies
  distintos.

**Alternativas rejeitadas**:

- **Prefixo reservado (`demonstracao:*`) em vez de lista fechada**: qualquer vínculo com
  o prefixo seria selecionável; a lista fechada é mais estrita e igualmente simples.
- **Marcar vínculos fictícios com um campo**: atributo sem significado institucional
  (spec FR-057).
- **Operador por parâmetro de endereço ou cabeçalho**: forjável e proibido pela
  Clarifications.
- **Escolha dentro de `/editor/`**: misturaria identificação com autorização no app do
  editor.

## R7 — Produção sem identificação: o editor continua fechado

**Decisão**: nada muda no `ModoDemonstracaoMiddleware`. Com
`TRAJETORIA_DEMONSTRACAO` desligado:

- toda rota, inclusive `/editor/` e `/demonstracao/operador/`, continua 404 antes de
  qualquer view;
- `operador_em_uso` devolve `None` sem ler cookie (defesa em profundidade, caso o
  middleware seja alterado);
- nenhum identificador vindo do cliente (parâmetro, cabeçalho, cookie) é aceito.

As regras e o vínculo funcionam independentemente do modo; só a **identificação** não
existe fora dele. É o comportamento esperado da 010, não incompletude (Clarifications).

**Justificativa**: o editor não pode ser usado em produção sem identificação confiável
(DP-1001), e a forma mais simples e segura de garantir isso é a que já existe. Mudar o
gate para "editor responde 403 em produção" exporia uma superfície que ninguém pode usar.

**Alternativas rejeitadas**:

- **Remover o editor do middleware e recusar 403 sem identificação em produção**:
  superfície pública sem uso; seria preciso decidir mensagem e comportamento de produção
  antes de DP-1001.
- **Aceitar identificador por cabeçalho de proxy reverso**: é identificação produtiva,
  pendente de DP-1001.

## R8 — Gate central do editor: `@exige(regra)` + verificação por estado da Versão

**Decisão**: novo módulo `trajetoria/editor/acesso.py`, a única ponte entre editor,
identificação e governança:

- `@exige(regra)`: decorador aplicado **por fora** de todas as 25 views, com `regra` igual a
  uma das três funções de R5. Em cada requisição:
  1. `operador_em_uso(request)` — identificação (R6);
  2. `None` → **encaminhamento** (302) para a escolha de operador fictício,
     `/demonstracao/operador/`, endereço fixo, sem parâmetro de retorno; nada é lido do
     instrumento nem gravado. (Fora do modo de demonstração esta linha nunca é
     alcançada: o middleware já respondeu 404.)
  3. `vinculos_ativos(identificador)` — uma consulta;
  4. lista vazia → recusa **sem atuação ativa**;
  5. `regra(vinculos)` falsa → recusa **vínculo não permite**;
  6. anexa à requisição a atuação resolvida (vínculos e os três resultados) para as
     páginas;
  7. chama a view.

  O decorador grava `view.exige = regra` para a verificação de cobertura (R13).
- `_exigir_consulta(request, versao)`: usada pelas views de leitura que dependem do estado
  (estrutura, Seção, Pergunta, prévia e Seção da prévia), **depois** de carregar o
  elemento. Para rascunho sem `pode_consultar_rascunho` → recusa **vínculo não permite**,
  levantada como `_Resposta`, o mecanismo existente das views.

Rota → regra (tabela completa em [acesso-editor.md](contracts/acesso-editor.md)):

| Grupo | Rotas | Regra no decorador | Verificação adicional |
|-------|-------|--------------------|-----------------------|
| Listas | `/editor/`, `/editor/pesquisas/<p>/` | `pode_consultar_publicado` | Consulta filtrada (R9) |
| Leitura por estado | Versão, Seção, Pergunta, prévia, Seção da prévia | `pode_consultar_publicado` | `_exigir_consulta` |
| Diagnóstico | `/editor/versoes/<v>/diagnostico/` | `pode_consultar_rascunho` | — (só rascunho, 009) |
| Escrita | as 17 rotas de formulário, confirmação, mover e remover | `pode_elaborar_instrumento` | — |

**Ordem garantida nas escritas**: identificação → vínculos → regra → só então a view
(objeto, `_exigir_rascunho` da 009, formulário, operação da 002). Uma recusa nunca chama
operação, nunca valida formulário e nunca revela erro de validação (spec FR-039). Como o
decorador é o mais externo, ele também precede `require_http_methods`.

**Justificativa**: um ponto de verificação, declarado por rota, sem repetir a lógica em 25
views e sem framework de políticas. O decorador conhece só as três funções concretas de
R5, passadas diretamente; não há enum de capacidade, registro nem composição
(Clarifications 2026-10-02).

**Alternativas rejeitadas**:

- **Middleware de autorização para `/editor/`**: precisaria de um mapa rota → regra
  separado das views; o decorador declara a regra junto da rota.
- **Mixin ou classe base**: as views são funções.
- **Verificação nos templates**: não protege envio direto (spec FR-041).
- **Decorador genérico com nomes de permissão em texto**: registro de permissões
  disfarçado (FR-034).

## R9 — Listas sem rascunhos para quem não os consulta

**Decisão**:

- `/editor/`: contagem de Versões com `Count("versoes", filter=Q(versoes__estado=PUBLICADA))`
  quando falta `pode_consultar_rascunho`; a página diz "Somente Versões publicadas são
  exibidas para a sua atuação".
- `/editor/pesquisas/<p>/`: o queryset de Versões recebe `.filter(estado=PUBLICADA)` nas
  mesmas condições. Pesquisa sem Versão publicada mostra "nenhuma Versão publicada".
- Ações de criação ("Nova Pesquisa", "Nova Versão", "Nova Versão a partir desta",
  recomendação da 009 FR-100) só aparecem com `pode_elaborar_instrumento`.

**Justificativa**: a consulta não carrega o que a atuação não pode ver (pedido do
solicitante); esconder no template seria conveniência, não proteção (spec FR-036,
FR-041). As Pesquisas continuam todas listadas: o nome administrativo não é rascunho e a
CSAEG precisa achar o instrumento publicado.

**Alternativas rejeitadas**: ocultar Pesquisas sem Versão publicada (outra regra sem
requisito); filtrar no template (carrega rascunhos).

## R10 — Privilégio técnico: nada a neutralizar, e nada é adicionado

**Decisão**: não adicionar `django.contrib.auth` para provar que superusuário não
autoriza. A independência é verificada por construção:

- as três regras têm um único parâmetro, `vinculos` (`inspect.signature`);
- `trajetoria/governanca` e `trajetoria/editor/acesso.py` não importam
  `django.contrib.auth` nem mencionam `is_staff`, `is_superuser`, `user` ou
  `TRAJETORIA_DEMONSTRACAO` (`ast`/texto);
- com o modo de demonstração ligado e operador sem vínculo, toda rota recusa;
- o teste existente de ausência de autenticação continua verde.

Se uma feature futura introduzir contas técnicas, os testes de assinatura e de
importação continuam valendo (spec FR-068).

**Justificativa**: Const. XXII e o pedido explícito do solicitante. A propriedade
relevante é "a autorização depende exclusivamente do vínculo", e ela é verificável sem
contas.

## R11 — Publicação: nada muda

**Decisão**: `publicar` (002) continua interna; o preparo da demonstração continua sendo
o único chamador fora de testes. Nenhuma regra, rota, papel, capacidade, estado ou
marcação de publicação. Os testes da 009 que proíbem `publicar` e rotas de
publicação/aprovação continuam; a 010 acrescenta verificação de que `governanca` não tem
nada de publicação (nomes `publica*`, `aprova*`, `homolog*` ausentes).

**Justificativa**: Clarifications; 002/DP-001 aberta; o Art. 26 indica quem resolve a
omissão, não autoriza o software a resolvê-la.

## R12 — Alterações na 009 e na 008

**Decisão**: alterações mínimas e listadas.

Feature 009 (`trajetoria/editor`):

- `acesso.py` — **novo** (R8);
- `views.py` — `@exige(...)` nas 25 views; `_exigir_consulta` em 5 views de leitura;
  filtro de rascunhos nas 2 listas (R9); `_render` passa a atuação ao contexto;
- `mensagens.py` — novo `BANNER` (spec FR-061) e textos de recusa (R14);
- `apresentacao.py` — rótulo de atuação ("Comissão Própria de Acompanhamento do Egresso
  (CPAEG) — atuação institucional"; "Comissão Setorial de Acompanhamento de Egressos
  (CSAEG) — unidade Vitória");
- `templates/editor/base.html` — contexto de atuação e link "Trocar operador fictício";
- `templates/editor/recusa.html` — **novo**;
- templates de lista e de Versão publicada — ações de criação condicionadas a
  `pode_elaborar_instrumento`.

Nenhuma regra editorial, rota, formulário, operação ou mensagem de rejeição da 009 muda
(spec FR-069 a FR-071).

Feature 008 (`trajetoria/demonstracao`):

- `operador.py` — **novo** (R6);
- `urls.py`, `views.py` — três rotas de operador fictício;
- `templates/demonstracao/operador.html` — **novo**;
- `cenario.py` — vínculos fictícios no preparo (R9b abaixo).

Nada muda na jornada do egresso (`interface`), nem na escolha de Pessoa fictícia.

**R9b — vínculos no preparo**: `preparar()` passa a garantir, na mesma transação:

- operador A → CPAEG ativo;
- operador B → CSAEG da unidade "Vitória" (designação já usada pelos dados simulados)
  ativo;
- operador C → sem vínculo.

Ele registra só o que não existe ativo (consulta antes, como faz com Campanhas). E recusa
o preparo se houver vínculo de identificador fora de `OPERADORES_FICTICIOS`, com a mesma
lógica da recusa existente para dados que não são da fonte simulada. O `Resumo` do
preparo não muda.

**Justificativa**: o preparo é o mecanismo de dados fictícios existente (pedido do
solicitante); não há migração de dados nem operador real codificado.

## R13 — Mecanismo administrativo: operações de aplicação, sem tela nem comando

**Decisão**: o "mecanismo técnico administrativo controlado" da spec (FR-062) é o
conjunto de operações de `trajetoria.governanca.operacoes` e `consultas`, acessíveis
somente a quem opera o servidor (código, testes, preparo, `manage.py shell`). Não há
comando de gestão, tela, CRUD, listagem web de vínculos nem rota.

As docstrings das operações dizem que o registro **reflete designação feita fora do
sistema e não a verifica** (spec FR-065; DP-1002).

**Justificativa**: há dois consumidores concretos, testes e preparo. Um comando de gestão
seria a primeira peça de um processo oficial de registro, que depende de DP-1002. O
roteiro de demonstração desativa um vínculo pelo shell (quickstart).

**Alternativas rejeitadas**: comando `manage.py vinculos` (sem consumidor além do
quickstart; antecipa DP-1002); tela de gestão (proibida, FR-063); `admin` do Django
(não instalado; traria auth).

## R14 — Respostas HTTP e textos de recusa

**Decisão**:

| Situação | Status | Resposta |
|----------|--------|----------|
| Modo de demonstração desligado (qualquer rota) | **404** | a da 008, inalterada |
| Modo ligado, nenhum operador escolhido (GET ou POST) | **302** | para `/demonstracao/operador/`; depois da escolha, `escolher_operador` volta a `/editor/`. Sem parâmetro de retorno |
| Operador identificado sem vínculo ativo | **403** | `editor/recusa.html`, variante **sem atuação** |
| Operador com vínculo que não permite a ação (CSAEG em rascunho, diagnóstico ou escrita) | **403** | variante **vínculo não permite** (leitura de rascunho ou elaboração) |
| Elemento inexistente, operador autorizado | **404** | o da 009 (GET padrão; POST `editor/aviso.html`) |
| Elemento inexistente, operador sem vínculo ativo | **403** | a recusa precede a busca do elemento |
| Escrita em Versão publicada, operador CPAEG | **409** / 302 | os da 009, inalterados |
| Escrita em Versão publicada, operador sem `elaborar` | **403** | a autorização precede a verificação de publicada |
| CSRF ausente | **403** | `403_csrf.html` da 008, inalterado |

**Textos** (em `editor/mensagens.py`, linguagem operacional; sem número de artigo no
texto principal — Clarifications 2026-10-02):

| Variante | Texto |
|----------|-------|
| sem atuação | "Não há vínculo institucional ativo para este operador. Sem vínculo ativo, o editor não pode ser usado." |
| vínculo não permite — leitura de rascunho | "Seu vínculo institucional atual não permite consultar Versões em rascunho. Ele permite consultar o instrumento publicado." |
| vínculo não permite — elaboração | "Seu vínculo institucional atual não permite editar este instrumento. Ele permite consultar o instrumento publicado." |

A fundamentação normativa (PAEG Art. 21, VI e Art. 22, IV) fica na spec, nas docstrings
de `governanca/regras.py` e nos testes. A interface não precisa dela para ser
compreendida.

**Por que encaminhar, e não recusar, sem operador**: no modo de demonstração a ausência
de operador é o estado inicial de quem chega, não uma tentativa indevida; levar à escolha
é o caminho útil (Clarifications 2026-10-02). O destino é fixo e o retorno é sempre o
início do editor: sem mecanismo genérico de `next`. Nenhum conteúdo do instrumento é
apresentado antes da escolha.

**Por que 403 para identificado sem capacidade**: 401 pressupõe um esquema de
autenticação com desafio (`WWW-Authenticate`), que não existe e não é criado; 404
esconderia a recusa e prejudicaria o diagnóstico, e o instrumento não é dado pessoal.

Todas as recusas: `role="alert"` não é usado (não é erro de formulário); título `<h1>`
"Acesso não permitido", explicação, ligações "Voltar às Pesquisas" (quando o vínculo
permite consultar) e "Trocar operador fictício"; sem identificador, valor técnico de
papel, nome de regra, código de rejeição, UUID ou lista de vínculos (spec FR-043,
FR-044).

## R15 — Estratégia de testes

**Decisão**: testes novos em `tests/governanca/` e `tests/editor/`, e ajuste de fixtures.

`tests/governanca/` (novo):

- `test_governanca_vinculo.py` — restrições de banco (papel inválido, CPAEG com unidade,
  CSAEG sem unidade, identificador vazio, unicidade incluindo CPAEG com unidade vazia);
  operações (criar, reativar, `JA_ATIVO`, `JA_INATIVO`, unidade com espaços, vários
  operadores com o mesmo papel, mesmo operador com vários vínculos);
- `test_governanca_regras.py` — matriz completa com vínculos não gravados: CPAEG, CSAEG,
  CPAEG + CSAEG, CSAEG de duas unidades, só inativos, vazio; independência do modo de
  demonstração; assinatura de um parâmetro;
- `test_governanca_fronteiras.py` — um modelo, cinco campos, dois papéis; sem
  `urls/views/admin/forms/middleware/management`; sem `django.contrib.auth`, `is_staff`,
  `is_superuser`, `TRAJETORIA_DEMONSTRACAO`; sem nomes de publicação/aprovação; nenhum
  papel genérico (`ADMIN`, `EDITOR`, `LEITOR`, `GESTOR`, `PUBLICADOR`…); `makemigrations
  --check`.

`tests/editor/` (ajustes e novos):

- `conftest.py` — a fixture `client` passa a atuar como operador fictício A com vínculo
  CPAEG; novas fixtures `cliente_csaeg`, `cliente_sem_vinculo`, `cliente_inativo` e
  `cliente_nao_identificado`.
  **Nenhum teste de comportamento da 009 muda**: eles passam a provar SC-003 da 010;
- `test_editor_autorizacao.py` (novo). Segurança exaustiva sem produto cartesiano:
  1. **estrutural**: toda view de `editor.urls` tem `exige`, com uma das três regras; as
     8 leituras declaradas; todas as demais com `pode_elaborar_instrumento` (FR-042);
  2. **POST não autorizado em todas as rotas de escrita**: um teste parametrizado pelas
     17 rotas com o operador CSAEG (o caso mais próximo de autorizado) → 403, retrato e
     contagens idênticos, nenhuma operação da 002 chamada (`monkeypatch` que falha se
     chamada), sem erros de validação no corpo mesmo com dados inválidos;
  3. **perfis representativos** numa rota de escrita e numa de leitura: não identificado
     → 302 para a escolha; sem vínculo e inativo → 403 sem atuação; CPAEG → comportamento
     da 009 (o mesmo decorador protege todas as rotas, garantido pelo item 1);
  4. **leituras por estado**: CSAEG em publicada (estrutura, Seção, Pergunta, prévia) →
     200 sem controles; CSAEG em rascunho (as 5 leituras por estado) e diagnóstico → 403;
     listas sem rascunhos e com o aviso;
  - desativação entre GET e POST → 403 e nada gravado;
  - elemento inexistente sem vínculo → 403; com CPAEG → 404;
  - múltiplos vínculos (CPAEG + CSAEG; duas CSAEGs);
  - CPAEG em publicada: 409 da 009 inalterado;
- `test_editor_acesso.py` — o banner novo; o teste de modo desligado continua igual e
  passa a enviar também cookie de operador, cabeçalho e parâmetro → 404;
- `test_editor_fronteiras.py` — `PERMITIDOS` acrescido de
  `trajetoria.demonstracao.operador: {operador_em_uso}`,
  `trajetoria.governanca.consultas: {vinculos_ativos}` e
  `trajetoria.governanca.regras: {as três regras}`; continua proibindo `publicar`;
- `test_editor_acessibilidade.py` — `verificar` da 008 nas variantes de recusa e na
  página de escolha de operador.

`tests/interface/test_interface_demonstracao.py`:

- acrescenta as rotas de operador à lista do modo desligado;
- teste novo `test_demonstracao_operador.py`: lista com atuações lidas dos vínculos;
  escolha de A/B/C; identificador fora da lista (POST e cookie forjado assinado) recusado;
  troca sem capacidade residual; preparo cria vínculos de A e B, nada para C, é
  idempotente e recusa vínculo de identificador não fictício.

**Justificativa**: cada item da lista de testes do solicitante e de "Cobertura de
verificação exigida" da spec tem um teste nomeado (mapa SC → teste no plan).
