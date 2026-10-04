# Research: Identificação e acesso do egresso por dados acadêmicos

Base: `main` `05d5469` (017 mergeada). Nenhum item da Technical Context ficou como NEEDS
CLARIFICATION. A stack é a existente; as decisões abaixo dizem **onde** fica cada parte e
**como** cada requisito sensível é atendido.

## R1 — Onde vive o código da 018

- **Decision**: novo app `trajetoria.acesso`. Ele contém o material de verificação (modelo
  próprio), as derivações protegidas, a verificação, a limitação de tentativas, a sessão do
  egresso e a entrada (views, formulário, mensagens, templates).
  - O seletor de Pessoa fictícia sai de `trajetoria.demonstracao`: `entrada.py`, as rotas
    `escolher` e `encerrar` e o template `entrada.html`.
  - `demonstracao` continua com o operador fictício (010) e com o preparo do cenário.
  - `/demonstracao/` (GET) redireciona para `/acesso/`, para não quebrar endereços
    antigos.
- **Rationale**: a 018 tem domínio e persistência próprios: material, regras de
  derivação, atualização e verificação. Pelo mesmo critério que fez da 016 um app, isso
  justifica um app. Ter app próprio também concretiza E2 (FR-016): o mecanismo inteiro
  pode ser substituído sem tocar `academico`, `participacao` ou `interface`. O
  `demonstracao/entrada.py` se declarava "adaptador temporário que sai quando a fronteira
  existir"; ela passa a existir.
- **Alternatives considered**:
  - **Colunas em `Pessoa`**: rejeitada por E2, porque acopla o núcleo acadêmico ao
    mecanismo.
  - **Ampliar `demonstracao`**: rejeitada, porque mistura o mecanismo com o adaptador de
    demonstração que ele substitui.
  - **Módulos dentro de `interface`**: rejeitada, porque a interface da jornada deve
    depender só de "qual é a Pessoa".

## R2 — Material de verificação: tabela própria, 1:1 com Pessoa

- **Decision**: modelo `acesso.MaterialDeVerificacao` (ver data-model):
  - `pessoa` é um 1:1 com `PROTECT` e sem acessor reverso;
  - `identificador_cpf` é obrigatório, indexado e **não único**;
  - `verificador` é anulável;
  - `atualizado_em` serve de versão do material.

  Uma Pessoa sem CPF utilizável não tem linha. Uma Pessoa com CPF e sem data tem
  identificador e não tem verificador.
- **Rationale**:
  - **Colisão.** O identificador sem data permite detectar colisões (FR-025) e localizar
    "exatamente uma Pessoa" (FR-003) mesmo quando outra Pessoa com o mesmo CPF não tem
    data.
  - **Sem unicidade.** Um `UNIQUE` impediria incorporar o segundo registro de uma colisão.
  - **Versão.** `atualizado_em` invalida sessões quando o material muda (FR-041).
  - **Mesmo padrão.** `related_name="+"` repete o padrão da 005: o modelo antigo não
    conhece o novo.
- **Alternatives considered**:
  - **Dois modelos (localização e verificação)**: sem consumidor separado.
  - **Guardar só o verificador**: impede detectar colisão e a classificação futura da 019.
  - **Coluna de "situação" do material**: o estado é derivável da presença do
    verificador.

## R3 — Derivações protegidas e chaves

- **Decision**:
  - **Derivações.** Ambas são HMAC-SHA-256 em hexadecimal, com mensagens separadas por
    domínio:
    - `identificador_cpf = HMAC(K_loc, "cpf:" + cpf11)`;
    - `verificador = HMAC(K_ver, "cpf-nascimento:" + cpf11 + ":" + AAAA-MM-DD)`.
  - **Chaves.** Vêm de duas variáveis de ambiente, sem valor padrão:
    `TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO` e `TRAJETORIA_CHAVE_ACESSO_VERIFICACAO`.
  - **Validação das chaves.** Ambas presentes; cada uma com ≥ 32 caracteres; diferentes
    entre si, da `SECRET_KEY` e da `TRAJETORIA_CHAVE_PSEUDONIMIZACAO`. Qualquer violação é
    a causa interna `CHAVE_NAO_CONFIGURADA`.
  - **Origem do limitador.** A chave de origem do limitador também é derivada com
    `K_loc` (`"origem:" + endereço`), para não deixar endereço em claro no cache.
- **Rationale**:
  - **Hash sem chave cai.** O espaço de CPFs e de datas é pequeno, e um hash sem chave
    cai por força bruta (decisão do solicitante).
  - **Chaves separadas.** Limitam o dano de vazamento de uma delas.
  - **Separação por domínio.** Impede que um valor de uma derivação sirva na outra.
  - **Mesmo padrão.** A validação segue `exportacao/pseudonimos.py`, já revisado.
- **Alternatives considered**:
  - **Hash lento (Argon2/PBKDF2)**: não acrescenta proteção com espaço pequeno; o que
    protege é o segredo.
  - **Uma chave só**: rejeitada pelo solicitante.
  - **Chave derivada da `SECRET_KEY`**: acopla rotações independentes.

## R4 — Extensão do contrato da fonte acadêmica

- **Decision**: `PessoaEncontrada` ganha `cpf: str | None` e `data_nascimento: date | None`,
  ambos com `field(default=None, repr=False)`.
  - **Forma canônica.** O contrato exige a forma canônica: CPF com exatamente 11 dígitos;
    cadeia vazia proibida, como nos demais campos.
  - **Dígito verificador.** O contrato **não** valida o dígito verificador. CPF legado
    inválido é dado da fonte, não erro de integração. O material o trata como ausente e
    sinaliza (R6).
  - **Fonte simulada.** `PessoaSimulada` ganha os mesmos dois campos, e a `FonteSimulada`
    os repassa.
  - **Associação de matrículas.** Associar matrículas do mesmo indivíduo (FR-021) é
    responsabilidade de cada implementação da fonte e fica documentada no contrato.
- **Rationale**:
  - **Sem vazamento.** `repr=False` evita que CPF e data apareçam em `repr`, em traceback
    ou em log de objetos do contrato (FR-013).
  - **Retrocompatível.** Padrões `None` mantêm compatíveis todas as construções existentes
    do contrato nos testes.
  - **Desacoplamento.** Validar só o formato preserva o Princípio V: a peculiaridade
    "CPF legado inválido" não derruba a incorporação acadêmica.
- **Alternatives considered**:
  - **Operação separada `obter_dados_de_verificacao`**: duas idas à fonte e risco de
    inconsistência entre as respostas.
  - **Validar o DV no contrato**: rejeitaria Pessoas reais com CPF legado errado e as
    tiraria até da incorporação acadêmica.

## R5 — Composição da incorporação: acadêmico intacto, material no mesmo ato

- **Decision**:
  - **Extração em `academico/incorporacao.py`.** O corpo atual de `incorporar_pessoa`,
    depois de obter a resposta, vira a função pública
    `incorporar_encontrada(codigo, resposta) -> ResultadoIncorporacao`, sem mudança de
    comportamento. `incorporar_pessoa` passa a chamá-la.
  - **Nova operação em `acesso/material.py`.**
    `incorporar_com_material(fonte, id_externo) -> ResultadoIncorporacao`:
    1. valida as chaves e recusa **antes** de consultar ou gravar (US5.5);
    2. obtém a resposta da fonte;
    3. numa transação, chama `incorporar_encontrada` e, se a Pessoa existe, chama
       `registrar_material(pessoa, cpf, data)`;
    4. registra divergências e colisões só depois do commit.
  - **Preparo da demonstração.** `demonstracao/cenario.py` usa `incorporar_com_material`.
    Sem chaves, o preparo é recusado com mensagem orientando a exportá-las.
- **Rationale**:
  - **Direção da dependência.** `acesso` depende de `academico`, e o núcleo acadêmico não
    conhece o mecanismo de acesso (E2, FR-016).
  - **Mesmo ato.** Uma transação garante que Pessoa e material entram juntos (FR-022), e
    os valores em claro só existem na pilha da chamada.
  - **Testes da 001.** Continuam usando `incorporar_pessoa`, sem chaves.
- **Alternatives considered**:
  - **Gancho ou callback dentro de `incorporar_pessoa`**: inverte a dependência por
    configuração.
  - **Sinal do framework**: implícito, e não tem acesso aos valores em claro.
  - **Material calculado depois, em segunda passada**: abre janela de Pessoa sem material
    e exigiria guardar os valores em claro entre as passadas.

## R6 — Regra de atualização do material (FR-024)

- **Decision**: `registrar_material(pessoa, cpf, data)` decide pela tabela abaixo. "CPF
  utilizável" significa 11 dígitos, dígito verificador válido e dígitos não todos iguais.
  O material antigo é o já gravado; o novo é o derivado agora.

| CPF na carga | Data na carga | Material existente | Efeito |
| --- | --- | --- | --- |
| ausente ou inutilizável | qualquer | qualquer | Nada muda. CPF inutilizável é sinalizado |
| utilizável | presente | nenhum | Cria identificador + verificador |
| utilizável | ausente | nenhum | Cria só o identificador |
| utilizável, igual | presente, diferente | existe | Substitui o verificador; sinaliza `data_nascimento` |
| utilizável, igual | ausente | existe | Nada muda (ausência não apaga) |
| utilizável, diferente | presente | existe | Substitui os dois; sinaliza `cpf` |
| utilizável, diferente | ausente | existe | Substitui o identificador e **anula** o verificador; sinaliza `cpf` |
| igual | igual | existe | Nada muda; `atualizado_em` preservado |

  "Igual" e "diferente" são decididos recalculando as derivações, sem nunca guardar
  valores em claro. `atualizado_em` muda só quando o material muda. Depois de gravar, se
  outra Pessoa tem o mesmo `identificador_cpf`, a colisão é sinalizada.
- **Rationale**:
  - **Valor corrigido substitui.** Decisão do solicitante.
  - **Ausência não apaga.** Também do solicitante.
  - **Última linha.** Um verificador calculado com o CPF antigo não confere com o CPF
    novo. Mantê-lo daria só um falso material. Anulá-lo não é "apagar por ausência": a
    própria troca de CPF o invalidou.
- **Alternatives considered**:
  - **Congelar o primeiro material**: trancaria quem teve a data corrigida.
  - **Apagar quando ausente**: rejeitada pelo solicitante.
  - **Histórico do material**: sem consumidor (XXII).

## R7 — Algoritmo de verificação e tempo constante

- **Decision**: `verificacao.verificar(cpf_texto, data_texto, origem, agora) -> Resultado`.
  1. **Limite por origem**: em espera → `INDISPONIVEL(LIMITE_TEMPORARIO)`. Senão, conta a
     submissão.
  2. **Formato**: normaliza e valida. Inválido → `FormatoInvalido(campos)`, sem avaliar e
     sem contar falha de credencial.
  3. **Chaves**: inválidas → `INDISPONIVEL(CHAVE_NAO_CONFIGURADA)`.
  4. **Derivações**: deriva **sempre as duas**.
  5. **Limite por CPF**: em espera → `INDISPONIVEL(LIMITE_TEMPORARIO)`.
  6. **Busca**: uma consulta por `identificador_cpf`, que devolve 0..N materiais.
  7. **Decisão**: `CONFIRMADA` se, e somente se, N = 1, o verificador não é nulo e
     `hmac.compare_digest` confere. Com N ≠ 1 ou sem verificador, compara com um valor
     fictício de mesmo tamanho para manter o trabalho.
  8. **Contagem**: em `NAO_CONFIRMADA`, conta falha do CPF. Em `CONFIRMADA`, zera a
     contagem do CPF.

  Exceção inesperada nos passos 3 a 8 → `INDISPONIVEL(FALHA_TECNICA)`.

  **Resultados** (dataclasses):
  - `Confirmada(pessoa, versao_material)`;
  - `NaoConfirmada()`, sem campo de causa;
  - `Indisponivel(causa: CausaIndisponibilidade)`;
  - `FormatoInvalido(campos)`.
- **Rationale**:
  - **Sem distinção pelo tempo.** As mesmas derivações e uma consulta indexada em todos
    os ramos; nenhum ramo existe só para "CPF desconhecido" (FR-014).
  - **Sem persistência da causa.** `NaoConfirmada` não carrega causa porque a 018 não a
    persiste nem expõe (FR-035). A 019 recalcula a partir do CPF que o declarante
    informar.
- **Alternatives considered**:
  - **Buscar pelo verificador direto**: perderia a regra "exatamente uma Pessoa pelo CPF"
    e a detecção de colisão.
  - **Atraso artificial fixo**: mascara tempo, mas custa latência e não substitui
    trabalho uniforme.

## R8 — Limitação de tentativas

- **Decision**: framework de cache do Django, com `CACHES` explícito em `settings.py`:
  `LocMemCache` local, com o nome `acesso`.
  - **Dois contadores**, ambos com chave derivada (R3):

| Contador | Conta | Livre até | Janela | Depois |
| --- | --- | --- | --- | --- |
| `origem` | toda submissão de POST à entrada, descontada a confirmação | 30 | 15 min fixos desde a primeira contagem | espera crescente |
| `cpf` | falhas de credencial (`NAO_CONFIRMADA`) | 3 | 60 min fixos desde a primeira contagem | espera crescente |

  - **Espera** depois do limite livre: `min(5 s × 3^(k−1), 300 s)`, com k = 1, 2, … (5 s,
    15 s, 45 s, 135 s, 300 s, 300 s…). A tentativa durante a espera é recusada sem
    avaliação e não prolonga a espera.
  - **Fim da contagem.** Confirmação apaga o contador do CPF. Os contadores expiram
    sozinhos pela janela. Nada vai para o banco (FR-031).
  - **Configuração.** Valores em `TRAJETORIA_ACESSO_LIMITES` (dicionário em
    `settings.py`), sobrescrevível nos testes.
  - **Falha do cache.** Qualquer exceção → `FALHA_TECNICA` (falha fechada).
- **Rationale**:
  - **Origem generosa.** Laboratórios e redes de campus compartilham o mesmo endereço
    (NAT); o limite da origem é largo e o do CPF é estreito.
  - **Teto baixo.** Evita negação de serviço contra um egresso específico (decisão do
    solicitante).
  - **Cache, não tabela.** Atende ao "transitório", sem tabela de domínio.
- **Alternatives considered**:
  - **Tabela de tentativas**: vira registro de domínio e trilha (FR-031, DP-1806).
  - **Bloqueio fixo**: vedado.
  - **Contador só por origem**: não protege um CPF atacado de várias origens.
  - **Ler `X-Forwarded-For`**: falsificável sem proxy confiável. Usa-se `REMOTE_ADDR`, e
    o proxy de produção fica em DP-1803.
- **Revisão de código (2026-10-04)**: a janela deslizante e a contagem de confirmações
  prendiam um laboratório inteiro na espera máxima enquanto houvesse tráfego, e o
  `get`/`set` deixava requisições simultâneas escaparem da conta. Corrigido com janela
  fixa, espera limitada ao fim da janela, desconto da confirmação na origem, incremento
  atômico (`add` + `incr`) e trava por CPF durante a verificação (`travar`/`liberar`).
- **Limite conhecido**: `LocMemCache` é por processo. Basta na demonstração (um processo),
  mas o uso real exige cache compartilhado, registrado em DP-1803. Trocar o backend é só
  configuração.

## R9 — Sessão do egresso

- **Decision**: `django.contrib.sessions` com backend de banco e `SessionMiddleware`.
  - **Chaves na sessão**: `acesso.pessoa` (UUID), `acesso.confirmada_em`,
    `acesso.ultimo_uso` e `acesso.versao_material`. Nada mais.
  - **Ao confirmar**: `cycle_key()` (contra fixação de sessão), depois grava as chaves.
  - **A cada requisição**, em `sessao.pessoa_em_uso(request)`, a sessão é **encerrada**
    quando:
    - a inatividade passou do limite;
    - a duração máxima passou;
    - a Pessoa não existe;
    - `versao_material` difere do material atual.

    Fora desses casos, renova `ultimo_uso` no máximo uma vez por minuto.
  - **Sair**: `flush()`.
  - **Configuração**: `TRAJETORIA_SESSAO_INATIVIDADE` (padrão 30 min) e
    `TRAJETORIA_SESSAO_DURACAO_MAXIMA` (padrão 8 h), lidos do ambiente.
  - **Cookie**: `SESSION_COOKIE_NAME = "trajetoria_sessao_egresso"`, `HttpOnly`,
    `SameSite=Lax`, `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` (cookie sem `Expires` nem
    `Max-Age`) e `SESSION_COOKIE_SECURE` por variável de ambiente (desligado só na
    demonstração local). A inatividade e a duração máxima continuam aplicadas no servidor;
    o fechamento do navegador encerra a sessão antes disso, como fazia o seletor da 008, o
    que protege dispositivos compartilhados.
  - **Limpeza**: sessões expiradas saem com o `clearsessions` do framework, como rotina
    operacional (quickstart).
- **Rationale**:
  - **Revogação real.** "Sair" e as invalidações acontecem no servidor, o que um cookie
    assinado sem estado não garante.
  - **Fixação.** É mitigada pelo framework.
  - **Comportamento já testado.** Expiração e rotação vêm prontas, sem código de
    segurança artesanal.
  - **Sem conflito.** O cookie assinado do operador fictício (010) continua separado
    (FR-043).
- **Alternatives considered**:
  - **Cookie assinado com renovação por middleware (padrão da 008)**: logout só no
    cliente e reemissão artesanal a cada requisição.
  - **Backend `signed_cookies`**: mesma limitação de revogação.
  - **Cache como armazenamento**: perderia sessões a cada reinício, sem ganho.
- **Impacto**: o `settings.py` deixa de dizer "sem sessions". A migração é do próprio
  framework (`django_session`), não de domínio.

## R10 — Integração com a interface (ponto de troca da 008)

- **Decision**:
  - **Interface.** `interface/views.py` passa a importar `pessoa_em_uso` de
    `trajetoria.acesso.sessao`, e `_pessoa` redireciona para `/acesso/`. `inicio` vai para
    `/formacoes/` com sessão e para `/acesso/` sem ela.
  - **Cabeçalho.** O processador de contexto `demonstracao.contexto` passa a ler a Pessoa
    de `acesso.sessao`. Em `interface/base.html`, a faixa de demonstração troca o texto
    "Não há autenticação: a escolha de uma pessoa não comprova identidade" por um texto
    sobre dados fictícios e verificação por conhecimento. "Trocar de pessoa" e "Encerrar
    demonstração" viram "Sair", com POST para `/acesso/sair/`.
  - **Jornada.** Nenhuma outra view, template ou operação da jornada muda (FR-044).
- **Rationale**: o ponto único de troca da 008 FR-005 existe exatamente para isso.

## R11 — Rotas, estados HTTP e conteúdo

- **Decision**: ver [contracts/rotas.md](contracts/rotas.md). Em resumo:
  - **Formulário.** `GET /acesso/` mostra o formulário e, na demonstração, o painel de
    credenciais fictícias. Com sessão ativa, mostra também "Continuar para suas
    formações".
  - **Verificação.** `POST /acesso/` verifica:
    - confirmada → 303 para `/formacoes/`;
    - formato inválido → 200 com erros nos campos;
    - não confirmada → **200**, com a mensagem genérica e o formulário preenchido ("Conferir
      os dados");
    - limite → 429 com `Retry-After`;
    - chave ou falha → 503.
  - **Sair.** `POST /acesso/sair/`.
  - **Compatibilidade.** `GET /demonstracao/` redireciona (301) para `/acesso/`.
  - **Cabeçalhos.** Todas as respostas de `/acesso/` têm `Cache-Control: no-store`.
  - **Proibido.** CPF e data nunca vão para URL, `Location` ou log.
  - **Base não simulada.** GET e POST respondem 422 antes de qualquer verificação ou
    contagem. O predicado "base exclusivamente simulada" passa a existir uma só vez, em
    `trajetoria/demonstracao/base.py` (`base_somente_simulada()`), usado pela entrada da
    018, pelo preparo (`cenario.py`) e pela 016 (`comunicacao.seguranca.validar_origem`),
    sem mudar o comportamento dessas duas.
- **Rationale**:
  - **"Conferir os dados".** Fica no mesmo formulário, preenchido e com o foco na
    mensagem, sem rota extra e sem passar os valores por URL.
  - **Status igual.** `NAO_CONFIRMADA` com 200 em todas as causas (FR-032).
  - **429 e 503.** Distinguem limitação de falha técnica para clientes e operação, sem
    nada revelar sobre o CPF.
- **Alternatives considered**:
  - **Rota `/acesso/conferir/`**: exigiria guardar os valores entre requisições.
  - **Manter a entrada em `/demonstracao/`**: nome de ambiente para uma capacidade real.

## R12 — URL do convite (016)

- **Decision**:
  - **URL padrão.** `TRAJETORIA_URL_ENTRADA_DEMONSTRACAO` passa a ter o padrão
    `http://127.0.0.1:8000/acesso/`.
  - **Validação.** `comunicacao.seguranca.validar_url` aceita o caminho `/acesso/` em vez
    de `/demonstracao/`.
  - **Testes.** Os testes da 016 que fixam o caminho são atualizados.
  - **Inalterado.** Nenhuma outra regra da 016 muda.
- **Rationale**: FR-053. O redirecionamento de `/demonstracao/` cobre mensagens já
  enviadas à caixa local.

## R13 — Painel de credenciais fictícias e cenários (FR-026, FR-060)

- **Decision**:
  - **Dados.** CPFs e datas fictícios declarados em `fonte_academica/cenarios.py` e
    documentados numa **nova tabela** em
    `specs/001-…/contracts/cenarios-simulados.md` ("Dados de verificação — fictícios"). O
    parser atual (tabela de registros, 11 colunas) não é afetado, e um teste novo garante
    que a nova tabela e os dados coincidem.
  - **CPFs.** Gerados com dígito verificador válido sobre a base sequencial
    `000.000.00N`, que evidencia o caráter artificial. Para cobrir CPF sem zeros à
    esquerda, usa-se também o exemplo de documentação `111.444.777-35`. Nenhum vem
    acompanhado de dado real.

| Pessoa | CPF fictício | Nascimento | Caso exercitado |
| --- | --- | --- | --- |
| SIM-P-0001 Ana | 000.000.001-91 | 1998-04-12 | Uma formação; zeros à esquerda |
| SIM-P-0002 Bruno | 111.444.777-35 | 1990-09-03 | Duas formações; sem zeros à esquerda |
| SIM-P-0003 Maria | 000.000.002-72 | 1997-11-25 | Duas formações em unidades diferentes |
| SIM-P-0004 Diego | 000.000.003-53 | 1994-02-08 | Três formações (seleção da 007) |
| SIM-P-0005 Elisa | — | 2001-06-30 | Sem CPF na fonte → não confirma |
| SIM-P-0006 João | 000.000.004-34 | 2003-03-14 | Sem conclusão; não incorporado → não confirma |
| SIM-P-0007 Fernanda | 000.000.005-15 | 1999-08-21 | Uma formação (outra matrícula ativa) |
| SIM-P-0008 Gustavo | 000.000.006-04 | 2000-01-17 | Nenhum registro concluído → não confirma |
| SIM-P-0009 (sem nome) | 000.000.007-87 | — | Sem data na fonte → não confirma |
| SIM-P-0010 Carla | 000.000.008-68 | 1992-05-05 | Colisão de CPF → não confirma |
| SIM-P-0011 Carla | 000.000.008-68 | 1995-10-19 | Colisão de CPF → não confirma |

  - **Painel.** Lê **só** de `cenarios.PESSOAS`, nunca do banco (E6). Mostra nome, CPF
    formatado, data e uma nota derivada do próprio cenário (sem CPF, sem data, CPF
    compartilhado, sem formação concluída). Cada linha tem o botão "Usar estes dados", um
    POST real para `/acesso/` que passa pela verificação e pela limitação. O painel só
    aparece no modo de demonstração e com base exclusivamente simulada.
- **Rationale**:
  - **Cobertura.** O conjunto cobre FR-026 sem criar novas Pessoas, o que mudaria
    contagens das features 004, 011 e 016.
  - **Homônimos.** Usar os homônimos para a colisão reproduz a origem real mais provável
    de CPF compartilhado: erro de cadastro entre pessoas de mesmo nome.
- **Alternatives considered**:
  - **Novas Pessoas fictícias**: alteram contagens em várias suítes.
  - **CPFs com DV inválido**: seriam recusados pela validação de formato e não testariam
    nada.

## R14 — Observabilidade

- **Decision**: logger `trajetoria.acesso`.
  - **WARNING**: `CHAVE_NAO_CONFIGURADA`; `FALHA_TECNICA`, só com o nome da classe da
    exceção; colisão de material; CPF inutilizável na fonte; divergências do material.
    As referências são `fonte:id_externo` da Pessoa e nomes de campo, como a 001 já faz.
  - **INFO**: limite temporário atingido, com o tipo de contador e sem chave.
  - **Nada**: `NAO_CONFIRMADA` e `CONFIRMADA` não são registradas.
  - **Nunca**: CPF, data, identificador, verificador ou endereço.
- **Rationale**: Observabilidade da Constituição e FR-013. O registro de eventos de
  segurança para auditoria é DP-1806.

## R15 — Formulário: acessibilidade e entrada

- **Decision**:
  - **CPF.** Campo de texto com `inputmode="numeric"` e `autocomplete="off"`. Aceita
    pontuação e espaços. Rejeita menos ou mais de 11 dígitos, DV inválido e dígitos todos
    iguais, com "Confira o CPF informado."
  - **Data de nascimento.** Um campo de texto com dica "DD/MM/AAAA",
    `inputmode="numeric"` e `autocomplete="bday"` (WCAG 1.3.5). Aceita `DD/MM/AAAA` ou
    `DDMMAAAA`. Rejeita data impossível, futura ou anterior a 1900, com "Confira a data de
    nascimento informada."
  - **Ligação dos erros.** Erros via `aria-describedby` e resumo no topo com foco (padrão
    do editor da 009/017).
  - **Padrão de formulário.** Formulário Django com template próprio, sem JavaScript e
    sem seletor de calendário.
- **Rationale**: Princípios XX e XXI. Um só campo de data reduz toques no celular, e o
  `autocomplete="bday"` atende ao propósito de entrada identificável.
- **Alternatives considered**:
  - **Três campos de data (dia, mês, ano)**: mais toques; o ganho de acessibilidade é
    coberto pela dica e pelo `bday`.
  - **`<input type="date">`**: seletor de calendário ruim para datas distantes.

## R16 — Estratégia de testes

- **Decision**:
  - **Pasta nova `tests/acesso/`**, com:
    - derivações e chaves;
    - regra de material (tabela de R6);
    - verificação (matriz da spec);
    - limitação (relógio controlado);
    - sessão;
    - rotas e conteúdo;
    - acessibilidade;
    - varredura de vazamento: `caplog`, URLs, `Location` e banco contra os CPFs e datas
      fictícios (SC-005).
  - **Chaves de teste.** Fixture autouse em `tests/conftest.py` define chaves de teste
    válidas, e os testes de chave ausente as sobrescrevem.
  - **Interface.** `tests/interface/construcao_interface.entrar_como` passa a abrir a
    sessão por um auxiliar que grava as mesmas chaves de `sessao.estabelecer`, sem passar
    pelo formulário. Os testes de aceitação de ponta a ponta usam o POST real.
  - **Banner.** Testes que verificam o texto do banner e as rotas `/demonstracao/escolher/`
    são reescritos.
  - **Tempo constante.** É verificado estruturalmente: espiões confirmam que as duas
    derivações e `compare_digest` rodam em todos os ramos. Medir tempo seria frágil.
- **Rationale**: Princípio XXVI. A jornada (005–008) continua sendo coberta pelos testes
  existentes; só muda como a Pessoa entra (SC-007).
