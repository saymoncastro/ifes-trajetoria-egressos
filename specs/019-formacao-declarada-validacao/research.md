# Research: Formação não localizada e validação posterior

Fase 0 do plan da 019. Cada item registra a decisão, a justificativa e as alternativas
rejeitadas. Critério transversal, pedido pelo solicitante: **nada além do necessário**.
Toda estrutura nova precisa de consumidor na spec.

## R1 — Um app novo (`declaracao`); o acervo não vira app

*Revisado em 2026-10-04. A primeira versão previa um app `acervo` separado.*

**Decisão.** Há **um** app novo, `trajetoria.declaracao`. Ele contém:
- os modelos `FormacaoDeclarada`, `DadosConsultaAcervo`, `ValidacaoDaFormacao`,
  `AcessoAosDadosDeConsulta` e `ReferenciaDeAcervo`;
- as operações;
- as telas;
- o adaptador da fonte de acervo, em `declaracao/acervo.py`.

O adaptador implementa o protocolo `FonteAcademica` e é passado à incorporação da 001 como
argumento, como qualquer fonte.

**Por que o acervo não justifica app próprio.** Pelos critérios do solicitante, faltam as
três condições:
- **Autorização.** Não há autorização própria: quem registra uma Referência é o validador,
  pela mesma capacidade.
- **Ciclo de vida.** Não há ciclo de vida independente: a Referência só nasce dentro do
  registro de uma validação.
- **Persistência.** A persistência é uma tabela, que só o adaptador lê.

**Por que não dentro de `fonte_academica`.** A 001 definiu esse pacote como "Python puro;
não importa Django" (001 plan, estrutura). Isso mantém o contrato e a fonte simulada
independentes do framework. Para guardar a Referência, ele teria de virar app instalado,
com modelo e migrações, o que muda a natureza da fronteira para atender um único
consumidor.

**O que continua garantido** (Princípio V):
- O núcleo `academico` só conhece o contrato.
- A Conclusão do acervo nasce pela incorporação normal.
- Trocar o acervo por uma fonte digital (DP-1911) significa trocar o adaptador passado à
  incorporação.

**Por que `declaracao` é app próprio.** É domínio novo (Terminologia 2.0.0), com
persistência, autorização (validação) e ciclo de vida próprios.

**Alternativas rejeitadas.**
- **App `acervo`.** Seria um app por feature, sem responsabilidade própria.
- **Modelos dentro de `participacao`.** Incha a 005 com regras de validação.
- **Referência dentro de `academico`.** Faria o núcleo hospedar dado de fonte, contra o
  Princípio V.

## R2 — Âncora da Participação

**Decisão.**
- **Campos.** `Participacao.conclusao` passa a aceitar `NULL`. Entra
  `Participacao.formacao_declarada`, um `OneToOneField` anulável com `PROTECT`.
- **CHECK.** Exatamente um dos dois está preenchido.
- **Unicidade.** `UNIQUE (campanha, conclusao)` fica como está. No PostgreSQL, `NULL` não
  colide.
- **Migração.** É aditiva. Como todas as linhas existentes têm Conclusão, o CHECK vale
  desde o início.
- **`pessoa`.** A propriedade `Participacao.pessoa` devolve `None` quando a âncora é
  declarada.

**Por quê.** É B′ (spec FR-030). As escritas da 005 e da 006 só leem `campanha` e
`concluida_em` (auditoria, F-1). Por isso não mudam.

**Direção da FK.** A FK fica na Participação, porque a âncora pertence a ela
(Constituição 2.0.0, Terminologia). O `CHECK` "exatamente uma âncora" só é possível com as
duas colunas na mesma tabela. `participacao` passa a depender, por modelo, de
`declaracao.FormacaoDeclarada`. `declaracao.models` não importa `participacao`, então não
há ciclo de import.

**Alternativa rejeitada.** FK de `FormacaoDeclarada` para `Participacao`. Ela não permite o
CHECK de âncora única e deixa Participação sem âncora detectável em SQL.

## R3 — Fatos gravados na decisão: abrangência congelada, conflito detectado

*Revisado em 2026-10-04.*

**Decisão.** `ValidacaoDaFormacao` guarda, no ato do registro:
- `resultado`, `conclusao`, `registrada_em` e `operador`;
- **`fora_da_abrangencia_na_validacao`**: fato **congelado**. A Conclusão confirmada não
  satisfazia a abrangência daquela Campanha. Critérios imutáveis depois da abertura (004)
  e Conclusão não atualizada (001 FR-033) tornam esse fato definitivo;
- **`conflito_detectado_na_validacao`**: fato do **momento da detecção**. Já havia outra
  Participação oficial com a mesma Conclusão na Campanha.

**Conflito não é verdade eterna.** O que fica congelado é "conflito **detectado** na
validação". Enquanto ele não for resolvido, o conflito está **pendente**, e a Participação
fica fora dos dados oficiais.

**Na 019.** Não existe resolução (DP-1907). Por isso, nesta versão, "conflito pendente"
equivale a "conflito detectado".

**Resolução futura.** Será um **registro próprio** que não altera a decisão. O filtro
oficial passará a ser "detectado e não resolvido". A extensão é aditiva: nada da 019
precisa ser migrado.

**Regra de oficialidade** (R4):

```text
institucional (âncora é Conclusão)
OU declarada + CONFIRMADA + NOT fora_da_abrangencia_na_validacao + NOT conflito pendente
```

**Alternativas rejeitadas.**
- **`em_conflito` como estado permanente.** Confunde detecção com resolução.
- **Recalcular abrangência e conflito em cada leitura.** Mesmo resultado, com custo e
  semântica espalhada.
- **Modelar a resolução agora.** Seria estrutura sem consumidor.

## R4 — Uma única definição de "oficial" e de "Conclusão efetiva"

**Decisão.** `participacao/consultas.py` ganha `participacoes_oficiais()`:
- devolve um QuerySet de Participação filtrado por
  `Q(conclusao__isnull=False) | Q(validação confirmada, sem fora_da_abrangencia_na_validacao, sem conflito pendente)`.
  Na 019, conflito pendente equivale a `conflito_detectado_na_validacao` (R3);
- anota `conclusao_efetiva_id = Coalesce("conclusao_id", "formacao_declarada__validacao__conclusao_id")`.

Ganha também `atributo_efetivo(campo)`, um `Coalesce` do atributo pelas duas rotas. É a
**única** fonte para 007, 011, 012 e 013. Usa lookups por nome e não importa
`declaracao`.

**Alternativa rejeitada.** Cada feature com o seu filtro. Já existem quatro consumidores, e
filtros duplicados divergem.

## R5 — Criptografia reversível: Fernet (`cryptography`), duas chaves por finalidade

*Revisado em 2026-10-04: separação de chaves e regra de rotação.*

**Decisão.**
- **Dependência nova.** `cryptography` (PyCA), registrada em `tests/dependencias.py` e na
  ADR 0005, criada na implementação.
- **Cifra.** `Fernet`: AES-CBC com HMAC-SHA256, autenticada e com carimbo de tempo.
- **Duas chaves**, cada uma com uma finalidade, ciclo de vida e risco:

| Chave | Configuração | Finalidade | Vida dos tokens | Rotação |
| --- | --- | --- | --- | --- |
| **A — selo** | `TRAJETORIA_CHAVE_SELO_DECLARACAO` | Selos transitórios entre a 018 e a criação da declaração (R6) | Minutos (TTL) | Trocar a qualquer momento. Selos em voo deixam de abrir e levam de volta a `/acesso/`. Não há dado persistido |
| **B — consulta** | `TRAJETORIA_CHAVE_CONSULTA_ACERVO` | `DadosConsultaAcervo` persistidos | Potencialmente longa (DP-1903) | Pela regra abaixo |

- **Validação das chaves.** Antes de qualquer uso, as duas precisam ser chaves Fernet
  válidas, diferentes entre si e diferentes de `SECRET_KEY`, das duas chaves da 018 e da
  chave de pseudonimização. Se falhar, a operação fica indisponível e não grava nada
  (FR-117).
- **Texto claro com vínculo.** O texto claro do selo de consulta traz a finalidade
  (`"acervo"`) e o UUID da declaração. Na abertura, ambos são conferidos, o que impede
  trocar tokens entre linhas ou usar um selo de trânsito como dado persistido, e
  vice-versa.

**Regra de rotação da chave B, sem campo `versao_chave`.**
- O token Fernet carrega a própria autenticação, e `MultiFernet` tenta cada chave da lista.
- Para rotacionar, a configuração passa a aceitar uma lista: a primeira chave cifra, as
  demais só decifram.
- **Toda chave antiga permanece na lista até que todos os `DadosConsultaAcervo` tenham sido
  recifrados** com `MultiFernet.rotate()`. Só então ela pode sair.
- Retirar uma chave antes disso torna os dados ilegíveis: equivale a descarte, que só a
  DP-1903 pode autorizar.
- A 019 aceita uma única chave B. A lista e o procedimento de recifragem entram quando a
  DP-1903 definir a rotação, sem migração de dados.

**Alternativas rejeitadas.**
- **Uma chave para as duas finalidades.** Mistura um token de minutos com dado de anos e
  impede rotacionar uma sem a outra.
- **AES-GCM direto.** Exige gerir nonce.
- **PyNaCl.** Outra dependência.
- **`pgcrypto`.** A chave iria ao banco.
- **Campo de versão de chave.** Desnecessário com `MultiFernet`.

## R6 — Selo transitório: credencial de curta duração, consumo idempotente

*Revisado em 2026-10-04.*

**Decisão.** O selo é tratado como **credencial transitória**. Não há infraestrutura de
token: só selos Fernet com a chave A.

| Momento | Selo | Conteúdo cifrado |
| --- | --- | --- |
| Resposta `NAO_CONFIRMADA` da 018 | **de trânsito** (`p = "transito"`) | CPF e data |
| Confirmação da formação (após `POST /declaracao/nova/`) | **de início** (`p = "inicio"`) | CPF, data, os cinco campos declarados e um `chave_de_criacao` (UUID novo) |

**Regras do selo.**
- **Onde trafega.** Só em campo oculto de formulário POST com CSRF. Nunca em URL, query
  string, cabeçalho de redirecionamento, cookie, sessão ou banco.
- **Logs e relatórios de erro.** As views que recebem selo usam
  `sensitive_post_parameters("selo")` (Django). O selo, o CPF e a data ficam fora de
  relatórios de erro e nada é registrado em log.
- **Validade curta.** Configurável em `TRAJETORIA_SELO_DECLARACAO_VALIDADE`, com padrão de
  30 minutos, igual à inatividade da sessão da 018: é o tempo de preencher cinco campos.
  Vencido, adulterado ou de finalidade errada, o selo leva de volta a `/acesso/`, sem
  detalhe.
- **Finalidade explícita.** Um selo de trânsito não serve para criar declaração, e um selo
  de início não estabelece sessão.
- **Páginas.** Todas as que contêm selo são `no-store`.

**Consumo idempotente.** O consumo acontece em `POST /declaracao/comecar/`.
- `FormacaoDeclarada.chave_de_criacao` é `UNIQUE`.
- Se o mesmo selo de início chegar duas vezes (atualização, duplo clique ou reenvio), a
  segunda chamada não cria nada. Ela encontra a declaração pela `chave_de_criacao` e,
  sendo do mesmo par, leva à mesma Participação.
- Corridas simultâneas são resolvidas pela restrição: quem perde a corrida relê, no padrão
  de `iniciar_participacao`.
- "Informar outra formação" gera um novo selo de início, com nova `chave_de_criacao`. Por
  isso declarar duas formações diferentes continua possível.

**Por quê.** Nada é persistido numa `NAO_CONFIRMADA` comum (018 FR-034; ajuste do
solicitante), e não há reavaliação (FR-002). A idempotência custa uma coluna `UNIQUE`.

**Alternativas rejeitadas.**
- **Guardar CPF e data na sessão.** É persistência no banco a cada falha.
- **Pedir CPF e data de novo.** Atrito.
- **Tabela de tokens consumidos.** Infraestrutura sem necessidade: a própria declaração é o
  registro do consumo.
- **Deduplicar pelo conteúdo declarado.** Frágil e bloquearia declarações legítimas.

## R7 — Sessão do declarante: UUIDs, não HMACs

**Decisão.**
- **Estabelecimento.** Ao abrir o selo em "Informar minha formação", o sistema calcula o
  HMAC do par, busca as declarações do par e estabelece a sessão com
  `declaracao.formacoes` (lista de UUIDs) mais os instantes da 018.
- **Atualização.** Ao criar uma declaração, o UUID dela entra na lista.
- **Exclusividade.** É exclusiva com a sessão de Pessoa: `cycle_key` mais `clear`, como na
  018.
- **Revalidação.** A cada requisição, a sessão é revalidada (expiração e existência), e
  `pessoa_em_uso` devolve `None` nessa sessão.

**Por quê.** É mais restritivo que a letra de FR-040, que permitia o HMAC do par: a sessão
não guarda HMAC, CPF nem data. A posse é verificada por pertença do UUID (FR-042).

**Alternativa rejeitada.** Guardar o HMAC do par na sessão. Funciona, mas espalha material
derivado sem necessidade.

## R8 — HMACs da declaração

**Decisão.** `FormacaoDeclarada` guarda os dois valores, ambos indexados, calculados com as
chaves e funções da 018 (`acesso/chaves.py`):
- `identificador_cpf`, para candidatas e agrupamento;
- `verificador`, para retomada.

Nunca se usa o `verificador` para agrupar ou deduplicar (FR-014).

## R9 — Início declarado e compatibilidade provisória

**Decisão.** A operação é `iniciar_participacao_declarada(dados, selo_aberto, *, origem,
agora)`, em `declaracao/operacoes.py`. Os passos, na ordem:

1. Aplica a limitação geral por origem da 018 (FR-113).
2. Valida os cinco campos.
3. Busca as Campanhas EM COLETA e avalia cada uma com `campanha.consultas.avaliar` sobre a
   `FormacaoDeclarada` ainda não gravada. Descarta pendências de `MODALIDADE` e
   `FORMA_OFERTA`, atributos que a declaração não coleta (E7).
4. Resolve o caso: nenhuma, uma ou mais Campanhas (regra da 007).
5. Com uma Campanha, numa transação, cria a `FormacaoDeclarada`, os `DadosConsultaAcervo`
   e a `Participacao` com a âncora declarada.

**Por quê.** Reaproveita a semântica exata da 004 sem reescrevê-la. Fora a âncora, a
Participação nasce igual à da 005.

**Alternativa rejeitada.** Estender `iniciar_participacao` com um ramo declarado. Ela
recebe `ConclusaoAcademica` por contrato (005), e misturar os dois casos a complicaria.

## R10 — Serialização confirmação × início institucional (FR-093)

**Decisão.** Dois pontos tomam um bloqueio na **linha da Conclusão X**
(`select_for_update`) antes de verificar e gravar:
- `registrar_validacao`, ao confirmar para X;
- `iniciar_participacao` (005).

Em `iniciar_participacao`, depois do bloqueio, se não houver Participação institucional
`(C, X)` mas houver Participação declarada oficial com Conclusão efetiva X em C, ela é
devolvida como `JA_EXISTENTE` (FR-092).

**Por quê.** A unicidade "uma oficial por (C, X)" envolve duas tabelas, então nenhum
índice a garante. Um bloqueio na linha comum é a forma mais simples. O conflito, por sua
vez, é decidido na mesma transação da confirmação.

**Alternativa rejeitada.** Bloqueio consultivo ou nível de isolamento mais forte. São mais
complexos sem ganho.

## R11 — Registro da validação

**Decisão.** A operação é `registrar_validacao(declaracao, *, vinculos, operador, agora,
resultado, origem)`. A origem é uma de três: candidata, referência na fonte digital, ou
dados do acervo.

1. Bloqueia a declaração. Se já houver decisão, levanta `JaDecidida`.
2. Verifica a capacidade e o escopo (E3).
3. Para `NAO_CONFIRMADA`, grava e encerra.
4. Para confirmada, obtém a Conclusão:
   - **Candidata:** precisa ter o mesmo `identificador_cpf`.
   - **Fonte digital:** `obter_conclusao(ref)` dá `id_externo_pessoa`, e
     `acesso.material.incorporar_com_material`, o caminho da 018, incorpora já com o
     material.
   - **Acervo:** `declaracao.acervo.registrar_referencia` registra ou reencontra a
     `ReferenciaDeAcervo`, e `incorporar_encontrada` incorpora pela
     `FonteAcervoHistorico`.
5. Bloqueia a Conclusão (R10).
6. Calcula `fora_da_abrangencia_na_validacao` e, se compatível,
   `conflito_detectado_na_validacao`, e grava.

**Erros.** Referência inexistente, fonte indisponível ou referência de acervo divergente
desfazem tudo (FR-074).

## R12 — Fonte de acervo histórico (dentro de `declaracao`)

**Decisão.**
- **Modelo.** `declaracao.ReferenciaDeAcervo` tem `unidade`, `referencia`, `nivel`,
  `curso`, `ano_conclusao`, e opcionalmente `modalidade`, `forma_oferta` e
  `data_conclusao`, além de `registrada_em` e `operador`.
- **Unicidade.** `UNIQUE (unidade, referencia)`, com a referência normalizada só em
  espaços (FR-083).
- **Adaptador.** `declaracao/acervo.py`, com `FonteAcervoHistorico.codigo =
  "acervo_historico"`. `obter_pessoa("acervo:<uuid>")` devolve
  `PessoaEncontrada(id_externo="acervo:<uuid>", nome=None, conclusoes=(ConclusaoNaFonte(id_externo=<uuid>, ...),))`,
  sem CPF nem data. `obter_conclusao(<uuid>)` segue o contrato.
- **Convergência.** O UUID da Referência é estável, então a mesma referência converge para
  a mesma Pessoa e a mesma Conclusão pela idempotência da 001.

**Por quê.** É o mínimo que faz o acervo ser fonte institucional (M1+). Ver R1 sobre a
localização.

**Alternativa rejeitada.** Pessoa do acervo agrupada por CPF. Exigiria CPF na fonte e seria
reconciliação (DP-1909).

## R13 — Revelação e trilha

**Decisão.**
- **Rota.** `POST /validacoes-formacao/<id>/revelar/`, com CSRF. Um GET não revela nada,
  para que pré-carregamento ou histórico do navegador não disparem a revelação.
- **Ordem.** Primeiro grava `AcessoAosDadosDeConsulta` (operador, declaração, momento) e,
  na mesma requisição, decifra e renderiza.
- **Cache.** Resposta `no-store`.
- **Descarte.** Se o selo foi descartado, a tela informa que os dados não estão mais
  disponíveis (FR-118).
- **Chave inválida.** A revelação fica indisponível e nada é registrado como acesso.

## R14 — Snapshot congela a Participação (012), com preenchimento provado determinístico

**Decisão.**
- **Campos novos.** `RegistroDoSnapshot` ganha `participacao` (FK anulável, `PROTECT`) e
  `origem_formacao` (lista fechada; anulável sem Participação).
- **Captura.** Usa `participacoes_oficiais`, e a integridade (FR-053 d) compara com as
  oficiais.
- **Leitura.** Usa `registro.participacao`.

**Por que o preenchimento dos snapshots existentes é determinístico.** A regra é: para cada
registro, `participacao` recebe a `Participacao(campanha = snapshot.campanha, conclusao =
registro.conclusao)`, se existir, e `origem_formacao` recebe `"institucional"`. Ela não
precisa escolher nada, por quatro invariantes já em vigor:

1. **No máximo uma candidata.** `UNIQUE (campanha, conclusao)` (`participacao_par_unico`)
   existe desde `participacao/0001_initial`. Até a 019, `conclusao` é `NOT NULL`. Logo,
   para cada par há no máximo uma Participação.
2. **A candidata é a mesma da captura.** A Participação nunca é removida (005 FR-017;
   `PROTECT`), e sua Conclusão nunca é alterada (005 FR-002).
3. **Nenhuma Participação nasceu depois da captura.** O snapshot só é capturado com a
   Campanha ENCERRADA (012 FR-010 a FR-012), e a admissão exige EM COLETA (004 FR-053).
   Não há reabertura nem prorrogação (004/DP-405; 017 C4). Escritas concorrentes ao
   encerramento são barradas pela verificação de integridade, que desfaz a captura (012
   FR-053 d, FR-054). Portanto, registro sem Participação na captura continua sem
   Participação, e registro com Participação a tem como única candidata.
4. **Toda Participação anterior à 019 é institucional.** Não existia outra âncora. Logo, é
   oficial e `origem_formacao = "institucional"`.

**Defesa adicional.**
- A migração verifica, antes de gravar, que nenhum par tem mais de uma Participação. Se
  houver, **aborta** sem escolher. Pelo item 1 isso é impossível, mas fica explícito.
- Também verifica que todo registro cuja Conclusão tinha Participação na Campanha a
  recebeu.

**Teste.** É o primeiro teste de migração do projeto (`MigrationExecutor`). Ele:
- monta um snapshot antes da migração, com registros com e sem Participação;
- migra;
- confere `participacao` e `origem_formacao`;
- confere que `linhas_do_dataset` e os indicadores produzem exatamente o mesmo resultado
  antes e depois.

## R15 — Exportação (013)

**Decisão.**
- **Coluna base nova.** `origem_formacao`, com proveniência "derivado" e três valores:
  - `institucional`;
  - `declarada_validada_fonte_digital`;
  - `declarada_validada_acervo`.
- **Versão.** `VERSAO_CONTRATO = 2`.
- **Leitura de 013 FR-021.** A regra mira colunas constantes **por construção** (Campanha,
  Versão), não colunas que variam por linha e por acaso são iguais numa Campanha. Registrar
  na nota de revisão da 013.

## R16 — Acompanhamento (011)

**Decisão.**
- **Contagens oficiais.** Iniciadas, concluídas, taxas e recortes passam a usar
  `participacoes_oficiais`.
- **Escopo e recortes.** Usam `atributo_efetivo("unidade")` e equivalentes.
- **Indicador da fila.** "Validações de formação: N na fila" conta, no escopo, as
  declarações concluídas e sem decisão mais as decisões em conflito. O escopo é pela
  unidade declarada (E3).

## R17 — Governança

**Decisão.**
- **Capacidade.** `pode_validar_formacao(vinculos)` (CPAEG ou CSAEG) em
  `governanca/regras.py`.
- **Escopo.** Reaproveita `escopo_de_acompanhamento`, com a mesma semântica de unidades.
- **Barreira.** No padrão de `acompanhamento/acesso.py`.

Não há papel novo.

## R18 — Entrada da Pessoa (007)

**Decisão.** `_participacoes_dos_pares` passa a considerar Participações oficiais pela
Conclusão efetiva. Uma declarada validada aparece como a Participação do par. Pendentes e
demais não aparecem (quarentena, FR-036).

## R19 — Jornada (008)

**Decisão.**
- **Posse.** `_participacao_da_pessoa` vira `_participacao_do_sujeito`:
  - para Pessoa, filtra por `conclusao__pessoa`;
  - para declarante, filtra por `formacao_declarada_id__in` os UUIDs da sessão.
- **Contexto.** Um auxiliar `formacao_exibida(participacao)` devolve o contexto e o
  rótulo. Para declarada:
  - o rótulo é "Formação informada por você";
  - a mensagem final é a de FR-033;
  - nenhum "Você concluiu".
- **Inalterado.** Templates, gravação e conclusão.

## R20 — Vocabulário das listas (FR-012)

**Decisão, provisória.** As opções de unidade e nível são a união dos valores distintos já
existentes em `ConclusaoAcademica` com os valores usados em critérios de Campanha.

**Por quê.** É o mesmo vocabulário por construção e não exige catálogo novo. O vocabulário
canônico continua em 001/DP-007 e 010/DP-1005.

**Alternativa rejeitada.** A Lista C de 2024. Ela é a lista de um instrumento, não o
vocabulário da Conclusão.

## R21 — Demonstração

**Decisão.**
- **Novos cenários fictícios na fonte simulada:**
  - um par inexistente para declarar;
  - uma Pessoa **presente na fonte e não importada** pelo `preparar_demonstracao`.

  A Pessoa sem data de nascimento (018) já serve de candidata.
- **Acervo.** Fica vazio. O operador fictício registra as referências durante a
  demonstração (FR-132).
- **Barreira.** `base_somente_simulada` passa a admitir `simulada` e `acervo_historico`.
- **Credenciais fictícias.** O painel da 018 lista também os pares de declaração.

## R22 — Testes

**Decisão.** Os testes ficam em `tests/declaracao/`, mais ajustes em
`participacao`, `acompanhamento`, `analitico`, `exportacao`, `interface` e `acesso`.

| Prioridade | O que cobrir | Requisitos |
| --- | --- | --- |
| Primeira | Âncora única e imutável; quarentena; oficialidade nas quatro superfícies | FR-030, FR-036, FR-051, FR-100 a FR-106 |
| | Migração dos snapshots: determinística, abortando em ambiguidade; dataset idêntico antes e depois | R14 |
| | Selo: finalidade, validade, adulteração; consumo idempotente (duplo envio e corrida) | R6 |
| | Duas chaves: inválidas, iguais entre si ou iguais a outra chave do sistema | R5 |
| | Conflito e serialização (teste com duas transações, como na 005 R11) | FR-090, FR-093 |
| | Snapshot anterior idêntico | FR-103 |
| | Varredura de vazamento: CPF e data fictícios em banco, logs, URLs, snapshots e exportações | SC-007 |
| | Revelação e trilha | FR-076, FR-116 |
| | Chave inválida fecha sem gravar | FR-117 |
| Segunda | Telas e acessibilidade com as ferramentas da 015 | — |

Os testes de fronteira recebem as novas permissões de import e a dependência aprovada.
