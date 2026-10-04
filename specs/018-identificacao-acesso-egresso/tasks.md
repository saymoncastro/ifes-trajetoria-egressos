# Tasks: Identificação e acesso do egresso por dados acadêmicos

**Input**: `specs/018-identificacao-acesso-egresso/`: [spec](spec.md) (com Clarifications de
2026-10-04), [plan](plan.md), [research](research.md), [data-model](data-model.md),
[verificação](contracts/verificacao.md), [material](contracts/material.md),
[rotas](contracts/rotas.md) e [quickstart](quickstart.md).

**Branch/baseline**: `claude/018-identificacao-acesso-egresso`, `main` `05d5469` (017
mergeada no PR #27).

## Formato e convenções

- **Formato.** `- [ ] TNNN [P?] [USn?] descrição com caminho`.
- **IDs.** Contínuos, na ordem de execução.
- **[P].** Só para arquivos distintos e sem dependência entre si.
- **Caminhos.** Relativos à raiz do repositório.
- **Rótulos de história.** Setup, fundação e acabamento não levam história. As demais
  tasks levam US1–US5 da spec.

**Ordem das histórias.** A US5 (importar o material) vem antes da US1 porque não há o que
conferir sem material. As prioridades da spec continuam valendo para o MVP.

**TDD obrigatório** (como na 016 e na 017):
1. Escrever os testes do bloco.
2. Executá-los e confirmar que falham pela ausência do comportamento da 018, não por
   fixture quebrada.
3. Implementar e confirmar verde com os mesmos testes.

Sem `xfail` nem `skip`.

**Guardas válidas para todas as tasks.** Qualquer task que viole uma delas está errada.

- **Modelos intocados.** Nenhum campo novo em `Pessoa`, `ConclusaoAcademica`,
  `Participacao`, `Resposta`, `Campanha` ou `Versao`. As únicas migrações são
  `acesso/0001` e as sessões do framework.
- **Sem dado em claro.** CPF e data de nascimento nunca são persistidos em claro nem
  aparecem em log, URL, `Location`, cookie, cache, `repr` ou mensagem de exceção. A única
  exceção é o eco no formulário do próprio POST (FR-013).
- **Escrita do material.** `MaterialDeVerificacao` só é escrito por
  `acesso.material.registrar_material`.
- **Dependência num sentido só.** `acesso` depende de `academico` e
  `fonte_academica`; nenhum módulo de `academico`, `fonte_academica`, `participacao`,
  `campanha` ou `instrumento` importa `acesso`.
- **Causa nunca exposta.** `NaoConfirmada` não tem campo de causa. Nenhuma resposta,
  status ou tempo distingue as causas.
- **Limitação.** Sem bloqueio permanente, sem tabela de tentativas e sem CAPTCHA.
- **Fora do escopo.** Nada de Gov.br, SSO, OTP, link mágico, senha ou conta, e nenhum
  JavaScript novo.
- **Escrita de domínio no acesso.** Nenhuma gravação de domínio no caminho de acesso. O
  acesso não incorpora sob demanda.
- **Jornada intacta.** A jornada (005 a 008) não muda, além da origem de `pessoa_em_uso`
  e dos redirecionamentos para `/acesso/`.
- **Testes semânticos.** Testes de rotas verificam comportamento, nunca contam rotas.

## Fase 1 — Setup (3 tasks)

- [X] T001 Criar o app `trajetoria/acesso/`:
  - arquivos `__init__.py`, `apps.py` (`AcessoConfig`, `name = "trajetoria.acesso"`),
    `urls.py` vazio e `templates/acesso/`;
  - em `config/settings.py`: acrescentar `"django.contrib.sessions"` e
    `"trajetoria.acesso"` a `INSTALLED_APPS` e
    `"django.contrib.sessions.middleware.SessionMiddleware"` logo depois de
    `ModoDemonstracaoMiddleware`;
  - revisar o comentário "sem … sessions" com a justificativa de research R9;
  - incluir `trajetoria.acesso.urls` em `config/urls.py`, antes de
    `trajetoria.interface.urls`.
- [X] T002 Em `config/settings.py`, com comentários de origem:
  - **Chaves.** `TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO` e
    `TRAJETORIA_CHAVE_ACESSO_VERIFICACAO`, do ambiente, com padrão `""`.
  - **Sessão.**
    - `TRAJETORIA_SESSAO_INATIVIDADE` e `TRAJETORIA_SESSAO_DURACAO_MAXIMA` como
      `timedelta`, a partir das variáveis em minutos, com padrões 30 e 480;
    - `SESSION_COOKIE_NAME = "trajetoria_sessao_egresso"`,
      `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = "Lax"`;
    - `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` (cookie sem `Expires` nem `Max-Age`;
      inatividade e duração máxima continuam no servidor);
    - `SESSION_COOKIE_SECURE = os.environ.get("TRAJETORIA_COOKIE_SEGURO") == "1"`.
  - **Cache.** `CACHES` com `default` e `acesso`, ambos `LocMemCache`, e comentário de
    DP-1803.
  - **Limites.** `TRAJETORIA_ACESSO_LIMITES` exatamente como em
    [verificação](contracts/verificacao.md).
  - **Convite.** Padrão de `TRAJETORIA_URL_ENTRADA_DEMONSTRACAO` →
    `http://127.0.0.1:8000/acesso/`.
  - **`.env.example`.** Acrescentar as chaves (sem valor, com a orientação de geração), as
    variáveis de sessão, `TRAJETORIA_COOKIE_SEGURO=` e a nova URL do convite.
- [X] T003 Preparar os testes:
  - **`tests/conftest.py`**: fixture autouse `chaves_de_acesso(settings)`, com duas
    chaves de teste de 64 hexadecimais, distintas entre si e das outras chaves; e fixture
    autouse que limpa o cache `acesso` antes de cada teste.
  - **`tests/acesso/__init__.py`.**
  - **`tests/acesso/construcao.py`**, com:
    - `preparar_material(*ids)`, que incorpora Pessoas da `FonteSimulada` por
      `incorporar_com_material` (import tardio);
    - os valores fictícios de research R13 como constantes `ANA`, `BRUNO`, …, cada uma
      com CPF formatado, só dígitos e data;
    - o relógio controlado no padrão de `tests/interface/conftest.py`;
    - `linhas_de_dominio()`, que tira um retrato de Pessoa, Conclusão, Participação,
      Resposta e Material.

  Nenhum comportamento da feature.

**Checkpoint**: a suíte atual continua verde, com o app vazio e as sessões instaladas.

## Fase 2 — Fundação: contrato, cenários, derivações e limitação (14 tasks)

Meta: tudo que US5 e US1 consomem existe e está provado antes de qualquer tela.

### Testes primeiro

- [X] T004 [P] RED em `tests/test_contrato_fonte.py`:
  - `PessoaEncontrada` aceita `cpf` e `data_nascimento`, ambos opcionais e com padrão
    `None`;
  - `cpf` presente exige exatamente 11 dígitos: `"123"`, 12 dígitos, `"000.000.001-91"` e
    `""` → `ValueError`;
  - `repr()` não contém o CPF nem a data;
  - as construções existentes continuam válidas.
- [X] T005 [P] RED em `tests/test_fonte_simulada.py`:
  - **Tabela documentada.** Parser da nova tabela "Dados de verificação — fictícios" de
    `specs/001-nucleo-academico-fonte-simulada/contracts/cenarios-simulados.md` (colunas
    Pessoa | CPF | Nascimento | Caso; `—` = ausente). A tabela é idêntica a
    `cenarios.PESSOAS` (`cpf` só dígitos, `data_nascimento`) e aos valores de research
    R13.
  - **Fonte simulada.** `FonteSimulada.obter_pessoa` devolve esses campos.
  - **Contagens.** `len(PESSOAS) == 11` e `len(REGISTROS) == 19`, inalterados.
  - **Parser antigo.** O parser da tabela de registros continua igual.
- [X] T006 [P] RED em `tests/test_incorporacao.py`:
  - `incorporar_encontrada(codigo, resposta)` dentro de `transaction.atomic()` produz,
    para cada Pessoa do cenário, exatamente as mesmas Pessoas, Conclusões, situação e
    divergências que `incorporar_pessoa`;
  - `incorporar_pessoa` ignora `cpf` e `data_nascimento` (nenhum efeito).
- [X] T007 [P] RED em `tests/acesso/test_chaves.py`:
  - **Chaves inválidas.** `chaves_de_acesso()` levanta `ChavesInvalidas` se alguma chave
    estiver ausente, tiver menos de 32 caracteres, se forem iguais entre si ou se alguma
    for igual à `SECRET_KEY` ou à `TRAJETORIA_CHAVE_PSEUDONIMIZACAO`. A mensagem nunca
    contém a chave.
  - **Formato.** `identificador_cpf`, `verificador` e `chave_de_origem` são
    determinísticos e devolvem 64 hexadecimais minúsculos.
  - **Vetor conhecido.** Os valores conferem com `hmac.new(chave, mensagem, sha256)`
    sobre as mensagens exatas `"cpf:<11>"`, `"cpf-nascimento:<11>:<AAAA-MM-DD>"` e
    `"origem:<endereço>"`.
  - **Separação por domínio.** O mesmo CPF dá valores diferentes em `identificador_cpf` e
    em `chave_de_origem`.
  - **Separação de chaves.** Trocar uma chave muda só as derivações que a usam.
- [X] T008 [P] RED em `tests/acesso/test_normalizacao.py`:
  - **`normalizar_cpf`.**
    - Aceita `"000.000.001-91"`, `"00000000191"`, `" 000 000 001 91 "` e
      `"111.444.777-35"`.
    - Recusa (`None`) dígito verificador errado, `"111.111.111-11"`, 10 ou 12 dígitos,
      letras e vazio.
  - **`cpf_utilizavel`.** Mesma regra para o CPF canônico.
  - **`normalizar_data(texto, hoje)`.** Aceita `"12/04/1998"` e `"12041998"`. Recusa
    `"31/02/2000"`, data posterior a `hoje`, `"01/01/1899"`, `"1998-04-12"` e vazio.
- [X] T009 [P] RED em `tests/acesso/test_limitacao.py` (unidade, cache `acesso`, relógio
  controlado):
  - **Espera.** `registrar` acima de `livres` define a espera
    `min(base × fator^(k−1), máxima)`: 5, 15, 45, 135, 300 e 300 s.
  - **Consulta.** `em_espera` devolve o instante ou `None`.
  - **Espera não prolonga.** Uma tentativa durante a espera não incrementa nem prolonga.
  - **Expiração.** O contador expira pela janela (`origem` 900 s, `cpf` 3600 s).
  - **Fim da contagem.** `zerar` remove o contador.
  - **Sem bloqueio permanente.** Nunca há espera sem prazo.
  - **Cache.** Nada é gravado no banco. Os parâmetros são lidos de
    `settings.TRAJETORIA_ACESSO_LIMITES`.

### Implementação

- [X] T010 Estender `PessoaEncontrada` em `trajetoria/fonte_academica/contrato.py`:
  - `cpf: str | None = field(default=None, repr=False)` e
    `data_nascimento: date | None = field(default=None, repr=False)`;
  - em `__post_init__`, `cpf` presente exige `re.fullmatch(r"\d{11}")`. O dígito
    verificador **não** é validado (research R4);
  - docstring com FR-021: a implementação da fonte agrupa os registros do mesmo
    indivíduo.

  Depende de T004.
- [X] T011 Acrescentar `cpf` e `data_nascimento` (padrão `None`) a `PessoaSimulada` em
  `trajetoria/fonte_academica/cenarios.py`, com os valores de research R13 (CPF só
  dígitos), e repassá-los em `FonteSimulada.obter_pessoa` em
  `trajetoria/fonte_academica/simulada.py`. Acrescentar a tabela "Dados de verificação —
  fictícios" a `specs/001-nucleo-academico-fonte-simulada/contracts/cenarios-simulados.md`,
  explicando o caráter fictício e a geração com dígito verificador válido. Depende de T005
  e T010.
- [X] T012 Extrair `incorporar_encontrada(codigo, resposta) -> ResultadoIncorporacao` em
  `trajetoria/academico/incorporacao.py`:
  - **Corpo.** É exatamente o trecho atual depois de obter a resposta, cobrindo
    `PessoaEncontrada` e o tratamento de `PessoaInexistente`.
  - **Transação.** Não abre transação nem registra divergências.
  - **Chamador.** `incorporar_pessoa` passa a chamá-la e mantém a transação e o registro.
  - **Comportamento.** Nenhuma mudança.

  Depende de T006.
- [X] T013 [P] Implementar `trajetoria/acesso/chaves.py` (`Chaves`, `ChavesInvalidas`,
  `chaves_de_acesso`, `identificador_cpf`, `verificador`, `chave_de_origem`) segundo
  [verificação](contracts/verificacao.md), seguindo o padrão de
  `trajetoria/exportacao/pseudonimos.py`. Depende de T007.
- [X] T014 [P] Implementar `trajetoria/acesso/normalizacao.py` (`normalizar_cpf`,
  `cpf_utilizavel`, `normalizar_data`) segundo research R15. Depende de T008.
- [X] T015 [P] Implementar `trajetoria/acesso/limitacao.py` (`em_espera`, `registrar`,
  `zerar`, constantes de tipo `origem` e `cpf`) sobre `caches["acesso"]`. As chaves de
  cache têm o formato `acesso:<tipo>:<valor derivado>`. Exceções do cache se propagam (a
  verificação as converte). Depende de T009.
- [X] T016 Implementar `MaterialDeVerificacao` em `trajetoria/acesso/models.py`, exatamente
  como no [data-model](data-model.md):
  - `id` UUID;
  - `pessoa = OneToOneField("academico.Pessoa", on_delete=PROTECT, related_name="+")`;
  - `identificador_cpf` texto obrigatório, com `db_index=True` e **sem** `unique`;
  - `verificador` texto `null=True`;
  - `atualizado_em` data e hora sem `auto_now`, definido por quem grava;
  - `CHECK` "64 caracteres hexadecimais minúsculos" para `identificador_cpf` e para
    `verificador` quando não nulo.

  Gerar `trajetoria/acesso/migrations/0001_initial.py`.
- [X] T017 GREEN de T004–T009. Regressão de `tests/test_*.py` (001), `tests/campanha/` e
  `tests/participacao/`. `makemigrations --check --dry-run` sem mudanças pendentes.

**Checkpoint**: contrato e cenários estendidos, extração sem mudança de comportamento,
derivações, normalização e limitação provadas. Ainda não há material gravado nem rota.

## Fase 3 — US5: importar o material de verificação protegido (P1) (5 tasks)

Teste independente: preparar a demonstração. Ficam 8 linhas de material (Ana, Bruno,
Maria, Diego, Fernanda, SIM-P-0009 e as duas Carlas), 7 delas com verificador (todas
menos SIM-P-0009). Elisa, João e Gustavo ficam sem material. Nenhum CPF ou data em claro
no banco.

- [X] T018 [P] [US5] RED em `tests/acesso/test_material.py`:
  - **Tabela de atualização.** Cada linha da tabela de research R6, usando `FonteSimulada`
    com `PessoaSimulada` próprias: cria; só identificador; troca de data; ausência não
    apaga; troca de CPF com data; troca de CPF sem data (verificador anulado); carga
    igual (`atualizado_em` preservado).
  - **CPF inutilizável.** Dígito verificador inválido ou dígitos iguais → nenhum material
    e sinal `CPF_INUTILIZAVEL`.
  - **Colisão.** As Carlas coexistem, com sinal `COLISAO`.
  - **Sem conclusão.** João sem conclusão não tem material.
  - **Fidelidade.** Pessoas e Conclusões são idênticas às de `incorporar_pessoa`.
  - **Erros da fonte.** `FonteAcademicaIndisponivel` e `PessoaInexistente` são tratados
    como na 001.
  - **Chaves inválidas.** `ChavesInvalidas` antes de chamar a fonte (espião), com zero
    gravações.
  - **Sem valores em claro.** `caplog` não contém CPFs, datas, identificadores nem
    verificadores, só `fonte:id_externo` e nomes de campo.
- [X] T019 [P] [US5] RED em `tests/acesso/test_preparo.py`:
  - **Sem chaves.** `preparar()` → `PreparoRecusado` com o texto exato de
    [material](contracts/material.md), sem nenhuma gravação.
  - **Com chaves.** As 8 linhas e os 7 verificadores do teste independente.
  - **Repetição.** Repetir `preparar()` não altera `atualizado_em`.
  - **Sem valores em claro.** Nenhuma coluna de texto de nenhuma tabela contém os CPFs de
    R13, em dígitos ou formatados, nem as datas em ISO ou DD/MM/AAAA.
- [X] T020 [US5] Implementar `trajetoria/acesso/material.py`:
  - `SinalDoMaterial`, `registrar_material(pessoa, cpf, data, chaves, agora)` (tabela de
    R6; igualdade decidida por recálculo das derivações; `atualizado_em = agora` só quando
    muda; colisão verificada depois da gravação);
  - `incorporar_com_material(fonte, id_externo)`, conforme
    [material](contracts/material.md): chaves → `obter_pessoa` → `atomic` com
    `incorporar_encontrada` e `registrar_material` → log depois do commit;
  - logger `trajetoria.acesso` segundo research R14.

  Depende de T012, T013, T014, T016, T018 e T019.
- [X] T021 [US5] Em `trajetoria/demonstracao/cenario.py`, trocar `incorporar_pessoa` por
  `incorporar_com_material` e converter `ChavesInvalidas` em `PreparoRecusado`, com o texto
  exato do contrato. As demais recusas ficam inalteradas. Depende de T020.
- [X] T022 [US5] GREEN de T018–T019. Regressão de `tests/interface/`,
  `tests/comunicacao/` e `tests/acompanhamento/`, que preparam a demonstração e agora usam
  as chaves da fixture de T003.

**Checkpoint**: a importação deriva o material no mesmo ato e nada sai em claro.

## Fase 4 — US1: confirmar o acesso e chegar às próprias formações (P1, MVP) (13 tasks)

Teste independente: preparar a demonstração e abrir `/acesso/`.
- Ana (`000.000.001-91`, `12/04/1998`) leva a `/formacoes/`, com uma formação.
- Diego leva à seleção da 007, com três formações.
- O link do convite da 016 leva ao formulário vazio.

### Testes primeiro

- [X] T023 [P] [US1] RED em `tests/acesso/test_verificacao.py` (confirmação):
  - **Confirmada.** `verificar` com Ana, em todos os formatos aceitos, devolve
    `Confirmada(pessoa=Ana, versao_material=…)`; com Diego, também.
  - **Formato inválido.** CPF ou data inválidos → `FormatoInvalido` com os campos
    corretos.
  - **Sem escrita.** Nenhuma escrita em `linhas_de_dominio()`.
  - **Chaves inválidas.** `Indisponivel(CHAVE_NAO_CONFIGURADA)`.
  - **Exceção inesperada.** Uma exceção na consulta (monkeypatch) →
    `Indisponivel(FALHA_TECNICA)`, com log só do nome da classe.
  - **Sem fonte no acesso (FR-006).** Espiões em `FonteSimulada.obter_pessoa`,
    `incorporar_encontrada` e `incorporar_com_material` registram **zero** chamadas
    durante `verificar`, em todos os resultados.
- [X] T024 [P] [US1] RED em `tests/acesso/test_sessao.py` (básico):
  - `estabelecer` troca a chave de sessão (`cycle_key`) e grava **somente** as quatro
    chaves do [data-model](data-model.md), sem formação, Campanha, CPF ou data;
  - `pessoa_em_uso` devolve a Pessoa e lê a sessão uma vez por requisição;
  - sessão ausente ou corrompida → `None`, sem exceção;
  - `dados_de_sessao` é pura.
- [X] T025 [P] [US1] RED em `tests/acesso/test_rotas.py` (US1), segundo
  [rotas](contracts/rotas.md):
  - **GET `/acesso/`.** 200 com formulário e painel; `Cache-Control: no-store`.
  - **POST correto.** 303 para `/formacoes/`. A sessão identifica a Pessoa. `Location`
    não contém CPF nem data.
  - **Dados na URL.** GET com `?cpf=…&data_nascimento=…` não avalia nem preenche nada.
  - **Proteções.** POST sem CSRF → 403. PUT → 405.
  - **Base não simulada** (Pessoa de outra fonte) → 422 sem formulário nem painel, tanto
    no GET quanto no POST. O POST não é avaliado e não incrementa nenhum contador.
  - **Compatibilidade.** `/demonstracao/` → 301 para `/acesso/`.
    `/demonstracao/escolher/` e `/demonstracao/encerrar/` → 404.
  - **Raiz e jornada.** `/` → `/formacoes/` com sessão e `/acesso/` sem ela. Rotas da
    jornada sem sessão → 302 para `/acesso/`.
  - **Modo desligado.** Toda rota → 404.
  - **Isolamento.** A sessão do egresso não concede acesso a `/editor/` nem a
    `/acompanhamento/`.
- [X] T026 [P] [US1] RED em `tests/acesso/test_demonstracao.py`:
  - **Fonte do painel.** O painel lista as 11 Pessoas de `cenarios.PESSOAS` com CPF
    formatado, data DD/MM/AAAA e nota (sem CPF, sem data, CPF compartilhado, sem formação
    concluída), executando **zero** consultas ao banco (`django_assert_num_queries(0)`
    sobre a função do painel).
  - **"Usar estes dados".** É um POST real para `/acesso/`. Com Ana, confirma; com
    Elisa, não confirma.
  - **Base não simulada.** O painel não aparece.
- [X] T027 [P] [US1] RED em `tests/comunicacao/` (`conftest.py`, `test_configuracao.py`,
  `test_convite.py`, `test_convite_mime.py`, `test_preview.py`, `test_seguranca.py`,
  `test_demonstracao.py`):
  - **URL do convite.** Passa a ser `http://127.0.0.1:8000/acesso/`.
  - **Validação.** `validar_url` aceita o caminho `/acesso/` e recusa `/demonstracao/`.
  - **Demais regras.** As outras regras de segurança da 016 continuam com as mesmas
    asserções.

### Implementação

- [X] T028 [US1] Implementar `trajetoria/acesso/verificacao.py`: resultados `Confirmada`,
  `NaoConfirmada` (sem campos), `Indisponivel(causa, espera_ate=None)`, `FormatoInvalido`
  e `CausaIndisponibilidade`, com `verificar(cpf_texto, data_texto, origem, *, agora)`
  exatamente na ordem de [verificação](contracts/verificacao.md):
  - **Origem.** Espera e contagem de toda submissão.
  - **Formato.** Validação de formato.
  - **Chaves e derivações.** Chaves; derivação **sempre** das duas.
  - **CPF.** Espera por CPF.
  - **Busca.** Uma consulta por `identificador_cpf`.
  - **Comparação.** `hmac.compare_digest` com o verificador, ou com um valor fictício de
    64 caracteres quando não há um único verificador.
  - **Contagem.** Falha conta para o CPF; confirmação zera.
  - **Exceções.** Exceção inesperada → `FALHA_TECNICA`.

  Depende de T015, T020, T023.
- [X] T029 [US1] Implementar `trajetoria/acesso/sessao.py`, com `dados_de_sessao`,
  `estabelecer` (`cycle_key` + quatro chaves) e `pessoa_em_uso`, lido uma vez por
  requisição. Nesta task, `pessoa_em_uso` só verifica que a Pessoa existe e que a versão
  do material é a atual. Expiração e `encerrar` ficam para a US4. Depende de T024.
- [X] T030 [US1] Implementar a camada da entrada em `trajetoria/acesso/`:
  - **`mensagens.py`.** Vocabulário fechado de [rotas](contracts/rotas.md), sem "login",
    "conta", "senha", "autenticação segura" ou "acesso seguro".
  - **`formularios.py`.** `EntradaForm`, que só converte: `cpf` e `data_nascimento` como
    texto, com os atributos `inputmode`, `autocomplete` e a dica.
  - **`demonstracao.py`.** Painel a partir de `cenarios.PESSOAS`.
  - **Predicado único.** Criar `trajetoria/demonstracao/base.py` com
    `base_somente_simulada() -> bool` (nenhuma Pessoa nem Conclusão de outra fonte) e
    usá-lo na entrada da 018, em `trajetoria/demonstracao/cenario.py` e em
    `trajetoria/comunicacao/seguranca.validar_origem`, sem mudar o comportamento nem as
    mensagens das duas últimas. Os testes atuais da 016 e do preparo continuam verdes.
  - **`views.py` e `urls.py`.** `entrada` (GET/POST, `never_cache`, `Cache-Control:
    no-store`, `REMOTE_ADDR` como origem, `estabelecer` + 303 para `/formacoes/` quando
    confirmada).
  - **Template.** `templates/acesso/entrada.html`, estendendo `interface/base.html`, com
    rótulos, dicas, resumo de erros e painel.

  Depende de T025, T026, T028 e T029.
- [X] T031 [US1] Trocar a origem da Pessoa na interface:
  - **`trajetoria/interface/views.py`.** Importa `pessoa_em_uso` de
    `trajetoria.acesso.sessao`; `_pessoa` e `inicio` redirecionam para `/acesso/`;
    docstring atualizada.
  - **`trajetoria/demonstracao/contexto.py`.** Lê a Pessoa de `acesso.sessao`.
  - **`trajetoria/interface/templates/interface/base.html`.** A faixa ganha o texto exato
    de [rotas](contracts/rotas.md). "Trocar de pessoa" e "Encerrar demonstração" saem; o
    botão "Sair" entra na US4.

  Depende de T029.
- [X] T032 [US1] Remover o seletor de Pessoa fictícia:
  - apagar `trajetoria/demonstracao/entrada.py` e
    `trajetoria/demonstracao/templates/demonstracao/entrada.html`;
  - em `trajetoria/demonstracao/views.py` e `urls.py`, remover `escolher` e `encerrar` e
    trocar `entrada` por um redirecionamento 301 para `/acesso/`;
  - atualizar as docstrings de `demonstracao` (operador fictício e preparo apenas).

  Depende de T030 e T031.
- [X] T033 [US1] Em `trajetoria/comunicacao/seguranca.py`, fazer `validar_url` exigir o
  caminho `/acesso/` no lugar de `/demonstracao/`. Nenhuma outra regra muda. Depende de
  T027.
- [X] T034 [US1] Adaptar os testes da interface:
  - **`entrar_como`.** Em `tests/interface/construcao_interface.py`, abre a sessão com
    `client.session`, gravando `acesso.sessao.dados_de_sessao(pessoa, versao, agora)` e
    salvando.
  - **Testes a reescrever.** `test_interface_demonstracao.py`,
    `test_interface_fronteiras.py`, `test_interface_identidade.py` (faixa),
    `test_interface_aceitacao.py`, `test_interface_acessibilidade.py`,
    `test_interface_entrada.py`, `test_interface_formacoes.py` e
    `tests/editor/test_editor_acesso.py`. Os que testam o seletor, o texto antigo da
    faixa ou redirecionamentos para `/demonstracao/` passam a testar o comportamento
    equivalente da 018.
  - **Limites.** Nenhuma asserção sobre a jornada é afrouxada.

  Depende de T031 e T032.
- [X] T035 [US1] GREEN de T023–T027. Suíte completa (`uv run pytest`) verde.

**Checkpoint (MVP)**: o egresso confirma o acesso com dados fictícios e segue a jornada
existente; o seletor fictício não existe mais.

## Fase 5 — US2: dados não confirmados, sem revelar e sem gravar (P1) (3 tasks)

Teste independente: sete casos, cobrindo as cinco causas da FR-032, dão a mesma tela, o
mesmo status e nenhuma escrita.

- [X] T036 [P] [US2] RED em `tests/acesso/test_verificacao.py` (não confirmação):
  - **Casos.** Sete casos, cobrindo as cinco causas da FR-032, devolvem todos
    `NaoConfirmada()`, sem atributos de instância:
    - CPF inexistente válido (`000.000.009-49`);
    - Ana com data errada;
    - Elisa (sem CPF);
    - SIM-P-0009 (só identificador);
    - Carla `000.000.008-68` com `05/05/1992` e com `19/10/1995` (colisão);
    - João (não incorporado).
  - **Uniformidade.** Em cada caso, espiões confirmam exatamente uma chamada de
    `identificador_cpf`, uma de `verificador`, uma consulta ao material e uma de
    `hmac.compare_digest`, também nos casos de sucesso.
  - **Sem escrita.** `linhas_de_dominio()` inalterado.
- [X] T037 [P] [US2] RED em `tests/acesso/test_rotas.py` (não confirmação), para os sete
  casos de T036 via POST:
  - **Resposta idêntica.** Status 200 e o mesmo HTML depois de remover o token CSRF e os
    valores ecoados nos campos.
  - **Conteúdo.** Contém "Não foi possível confirmar os dados informados." como alvo de
    foco, o link-âncora "Conferir os dados" com `href="#cpf"` (o campo CPF tem
    `id="cpf"`) e o formulário preenchido com os valores digitados.
  - **Sem dados da base.** Nenhum nome de Pessoa nem atributo de formação.
  - **Cabeçalhos.** `Cache-Control: no-store`.
  - **Sessão preservada.** Uma sessão já existente de outra Pessoa continua intacta, com a
    mesma chave e os mesmos dados.
  - **Sem escrita.** `linhas_de_dominio()` inalterado.
- [X] T038 [US2] Completar `trajetoria/acesso/views.py` e o template para `NaoConfirmada` e
  `FormatoInvalido`: mensagem no topo com foco, resumo de erros por campo, valores
  preservados e status 200. GREEN de T036–T037. Depende de T030.

**Checkpoint**: falha segura e indistinguível; o ponto de saída `NaoConfirmada` existe
para a 019.

## Fase 6 — US3: limitar tentativas sem trancar o egresso (P1) (2 tasks)

Teste independente: com o relógio controlado, quatro falhas de um CPF levam a 429 com
`Retry-After: 5`. O comportamento é idêntico para CPF inexistente, e o par correto
confirma depois da espera.

- [X] T039 [US3] RED em `tests/acesso/test_limitacao_fluxo.py` (POSTs reais):
  - **Falhas livres.** Até três falhas do mesmo CPF são avaliadas.
  - **Primeira espera.** Na quarta falha, a próxima tentativa imediata recebe 429,
    `Retry-After: 5` e "Aguarde alguns instantes antes de tentar novamente.", sem
    contagem visível.
  - **Esperas seguintes.** 15, 45, 135 e 300 s, com teto de 300.
  - **Idêntico para inexistente.** A mesma sequência com CPF inexistente dá respostas
    idênticas.
  - **Sem bloqueio permanente.** Depois da espera, o par correto confirma e zera a
    contagem; nenhum CPF fica bloqueado.
  - **Recusa não prolonga.** Uma recusa durante a espera não prolonga a espera.
  - **Limite por origem.** Com 30 submissões livres, a 31ª submissão da mesma origem,
    inclusive de formato inválido, ainda é avaliada e passa a espera; a 32ª imediata
    recebe 429. É a mesma regra do CPF: quem passa do limite é avaliado e só a seguinte
    espera. Formato inválido não conta para o CPF.
  - **Registro.** A causa `LIMITE_TEMPORARIO` aparece como INFO, nunca como WARNING de
    falha técnica.
  - **Falha do cache.** Exceção do cache (monkeypatch) → 503 com "Não foi possível
    verificar agora…".
  - **Banco.** Nada é gravado no banco pela limitação.
- [X] T040 [US3] Em `trajetoria/acesso/views.py`, responder `Indisponivel(LIMITE_TEMPORARIO)`
  com 429 e `Retry-After` em segundos inteiros, calculado de `espera_ate`, e
  `CHAVE_NAO_CONFIGURADA` e `FALHA_TECNICA` com 503, usando os textos de `mensagens.py`.
  GREEN de T039. Depende de T028 e T030.

**Checkpoint**: a verificação por conhecimento tem o controle proporcional decidido.

## Fase 7 — US4: sessão do egresso — expirar, sair e trocar de pessoa (P2) (3 tasks)

Teste independente: confirmar, avançar o relógio além da inatividade e voltar à entrada.
Sair encerra a sessão. Confirmar A e depois B deixa só B.

- [X] T041 [US4] RED em `tests/acesso/test_sessao.py` (ciclo de vida):
  - **Inatividade.** Inatividade além de `TRAJETORIA_SESSAO_INATIVIDADE` → `None` e
    `flush()`. A duração é configurável por `settings`, com o padrão de 30 min verificado.
  - **Duração máxima.** Passar de `TRAJETORIA_SESSAO_DURACAO_MAXIMA` (padrão 8 h) →
    `None`.
  - **Renovação.** `ultimo_uso` é renovado no máximo uma vez por minuto.
  - **Material alterado.** Material alterado depois da confirmação (nova carga com data
    corrigida) → `None`.
  - **Pessoa inexistente.** Sessão com UUID de Pessoa inexistente → `None`.
  - **Sair.** POST `/acesso/sair/` faz `flush` e responde 303 para `/acesso/`; GET dá
    405; sem CSRF, 403.
  - **Fechamento do navegador.** O cookie `trajetoria_sessao_egresso` emitido na
    confirmação não tem `Expires` nem `Max-Age`.
  - **Troca de pessoa.** Confirmar B depois de A no mesmo cliente deixa só B, e a chave
    de sessão muda.
  - **Operador independente.** O cookie do operador fictício não é afetado por sair nem
    por confirmar.
  - **Faixa.** Com sessão, mostra o nome e o botão "Sair".
  - **Respostas preservadas.** Depois de expirar, a jornada redireciona para `/acesso/` e
    as Respostas salvas continuam (retomar depois de nova confirmação as exibe).
- [X] T042 [US4] Completar `trajetoria/acesso/sessao.py` (inatividade, duração máxima,
  renovação por minuto e `encerrar`), acrescentar a view `sair` (POST, `never_cache`) e a
  rota `/acesso/sair/` em `trajetoria/acesso/`, e pôr o botão "Sair" (form POST com CSRF)
  na faixa de `trajetoria/interface/templates/interface/base.html` quando houver Pessoa em
  uso. Depende de T029 e T041.
- [X] T043 [US4] GREEN de T041. Regressão de `tests/interface/` e `tests/acesso/`.

**Checkpoint**: a sessão tem fim e revogação reais.

## Fase 8 — Acabamento e verificações transversais (7 tasks)

- [X] T044 [P] Escrever e passar `tests/acesso/test_vazamento.py` (SC-005). O teste
  executa preparo, confirmação, as sete não confirmações, formato inválido, limitação,
  sair e um convite simulado da 016, capturando:
  - `caplog` em nível DEBUG de todos os loggers;
  - todos os `Location` e URLs pedidas;
  - todas as colunas de texto de todas as tabelas, incluindo `django_session` decodificada;
  - o conteúdo do cache `acesso`.

  Procura todos os CPFs e datas de R13 (dígitos, formatado, ISO, DD/MM/AAAA) e espera
  **zero** ocorrências, exceto o eco nos formulários das respostas a POST.
- [X] T045 [P] Escrever e passar `tests/acesso/test_acessibilidade.py`:
  - **Campos.** Rótulos `<label for>` visíveis; `inputmode="numeric"` nos dois campos;
    `autocomplete="bday"` na data e `"off"` no CPF; dicas por `aria-describedby`.
  - **Erros.** `aria-invalid` nos campos com erro; resumo de erros e aviso de não
    confirmação como alvo de foco (padrão do editor).
  - **Sem dependências proibidas.** Nenhum `<script>` exigido e nenhum `type="date"`.
  - **Vocabulário.** Nenhuma ocorrência de "login", "senha", "conta", "autenticação
    segura" ou "acesso seguro" nas respostas de `/acesso/` (FR-061).
- [X] T046 [P] Escrever e passar `tests/acesso/test_fronteiras.py`:
  - **Direção da dependência.** Nenhum módulo de `trajetoria/academico`,
    `fonte_academica`, `participacao`, `campanha`, `instrumento` ou `interface` (exceto o
    import de `pessoa_em_uso` em `interface/views.py`) importa `trajetoria.acesso`.
  - **Modelos.** `Pessoa` e `ConclusaoAcademica` têm os mesmos campos de antes.
  - **Sem acessor reverso.** `MaterialDeVerificacao` não cria acessor em `Pessoa`.
  - **Material fora de exportação e operador (FR-015).** Nenhum módulo de
    `trajetoria/exportacao`, `analitico`, `acompanhamento`, `comunicacao` ou `editor`
    importa `trajetoria.acesso` ou referencia `MaterialDeVerificacao`, e nenhum template
    administrativo o exibe.
  - **Dependências.** `pyproject.toml` continua igual a `tests/dependencias.py`.
  - **Migrações.** Pendentes: nenhuma.
- [X] T047 Aplicar notas "*(Revisado pela 018)*", com uma frase cada e referência à
  cláusula da 018:
  - `specs/001-nucleo-academico-fonte-simulada/spec.md` (FR-005, FR-006, FR-028, FR-033) e
    `data-model.md` (invariante "não sobrescritos" restrito a dados acadêmicos);
  - `specs/007-contextualizacao-formacao-entrada/spec.md` (FR-002);
  - `specs/008-interface-navegavel-pesquisa/spec.md` (FR-004, FR-007, FR-008);
  - `specs/016-mobilizacao-comunicacao-simulada/spec.md` (FR-021).

  Atualizar o comentário de `INSTALLED_APPS` em `config/settings.py`, que ainda chama
  `demonstracao` de "adaptador de identidade".
- [X] T048 Executar `uv run pytest`, `uv run ruff check .`, `ruff format --check` só nos
  arquivos tocados pela 018, `uv run python manage.py check` e
  `makemigrations --check --dry-run`. Tudo verde. Não reformatar arquivos fora da
  feature.
- [X] T049 Executar o roteiro manual de [quickstart.md](quickstart.md) num banco
  `trajetoria_demo` recriado, com as chaves exportadas, inclusive a verificação a 320 px
  (FR-071) no mesmo critério da 015, e registrar as evidências ao final do quickstart.
- [X] T050 Revisar o diff contra as guardas do topo e contra a matriz de verificação da
  spec, e marcar as tasks concluídas.

## Dependências

```text
T001–T003 ─► Fundação (T004–T017) ─► US5 (T018–T022) ─► US1 (T023–T035) ─┬─► US2 (T036–T038)
                                                                         ├─► US3 (T039–T040)
                                                                         └─► US4 (T041–T043)
                                                 US1..US5 ─► Acabamento (T044–T050)
```

- **Fundação.** Bloqueia tudo: contrato, cenários, derivações, limitação e o modelo.
- **US5 antes da US1.** Sem material não há o que conferir. A US5 também ajusta o preparo
  usado pelas suítes da interface.
- **US2, US3 e US4.** São independentes entre si depois da US1. Tocam o mesmo
  `acesso/views.py` (e a US4 também o `base.html`), então as implementações (T038, T040,
  T042) são registradas em sequência.
- **Acabamento.** As varreduras de vazamento e de acessibilidade precisam de todas as
  rotas e estados.

## Paralelismo

- **Fundação.** RED de T004–T009 em paralelo; depois, T013, T014 e T015 em paralelo.
- **US5.** T018 e T019.
- **US1.** RED de T023–T027 em paralelo.
- **US2.** T036 e T037.
- **Acabamento.** T044, T045 e T046.

## Estratégia

1. **MVP** = Fundação + US5 + US1: o egresso confirma o acesso com dados fictícios
   protegidos e entra na jornada existente.
2. **US2** fecha o caminho de falha seguro e o ponto de saída para a 019.
3. **US3** acrescenta o controle proporcional, e **US4** dá fim e revogação à sessão.
4. **Acabamento**: varreduras de vazamento, acessibilidade e fronteiras, notas de
   revisão e roteiro manual.

**Total**: 50 tasks.
