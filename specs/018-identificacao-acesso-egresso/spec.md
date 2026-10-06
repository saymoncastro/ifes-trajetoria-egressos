# Feature Specification: Identificação e acesso do egresso por dados acadêmicos

**Feature**: `018-identificacao-acesso-egresso`

**Feature Branch**: `claude/018-identificacao-acesso-egresso` (a partir da `main` em
`05d5469`, com a 017 mergeada)

**Created**: 2026-10-04

**Status**: Esclarecida em 2026-10-04; implementada e integrada à `main` em 2026-10-04
(PR #28), restrita à demonstração. O uso real continua bloqueado por DP-1801 a DP-1803.

**Input**: Solicitação da Feature 018. O egresso confirma o acesso informando **CPF e data
de nascimento**. Esses dados são conferidos contra um material de verificação protegido
(HMAC com chaves externas ao banco), importado da fonte acadêmica junto com a Pessoa. A
Pessoa confirmada é entregue à jornada existente (007/008). O resultado é sempre um destes
três:

- `CONFIRMADA`;
- `NAO_CONFIRMADA`, que é só o ponto de saída para a futura 019;
- `VERIFICACAO_INDISPONIVEL`, que é temporário e nunca tratado como "não confirmada".

## Contexto

Hoje a Pessoa chega à jornada por um **seletor fictício** (008, `demonstracao/entrada.py`).
Ele não verifica nada. Era aceitável porque toda a interface existe só no modo local de
demonstração. A 008 deixou o ponto de substituição pronto: a interface depende só de "qual
é a Pessoa resolvida" (008 FR-005; 007 FR-001).

A [auditoria de identidade e acesso](../../docs/auditorias/2026-10-03-identidade-acesso-egresso.md),
com o adendo de 2026-10-04, chegou a uma decisão do solicitante:

> Para a primeira versão real, CPF + data de nascimento provenientes da fonte acadêmica
> são o mecanismo de verificação de acesso. **É verificação de identidade por
> conhecimento, não autenticação forte**: uma camada proporcional de segurança, de baixa
> fricção, muito superior ao processo atual, que não verifica vínculo algum.

O caso principal desta feature:

```text
Egresso (link neutro da mobilização ou acesso espontâneo)
   │
   ▼
┌─────────────────────────────────────┐
│ Para acessar a pesquisa             │
│ CPF               [___.___.___-__]  │
│ Data de nascimento [__/__/____]     │
│ [Continuar]                         │
└─────────────────────────────────────┘
   │
   ├─ CONFIRMADA ──────────► sessão (só a Pessoa) ─► formações (007/008) ─► pesquisa
   │
   ├─ NAO_CONFIRMADA ──────► "Não foi possível confirmar os dados informados."
   │                          [Conferir os dados]   (nada criado nem alterado;
   │                                                 a saída excepcional é da 019)
   │
   └─ VERIFICACAO_INDISPONIVEL ► "Não foi possível verificar agora. Tente novamente
                                  em instantes."   (nunca encaminha à 019)
```

### Base existente e evidências

Inspeção da `main` em `5e50fec` (PR #26 / ADR 0004), em 2026-10-04. Revalidada em
`05d5469`, depois do merge da 017 (PR #27). A 017 não alterou nenhum dos módulos citados
abaixo.

| Fato atual | Evidência | Consequência para a 018 |
| --- | --- | --- |
| Pessoa tem UUID interno, uma referência de origem `(fonte, id_externo)` única e nome opcional; não tem CPF, data de nascimento nem e-mail | `academico/models.py`; 001 FR-005, FR-006 | O UUID continua sendo a identidade. CPF e nascimento entram só como material protegido, com consumidor concreto (001 FR-005) |
| A fronteira acadêmica só obtém Pessoa por `id_externo`; não transporta CPF nem nascimento | `fonte_academica/contrato.py` | A fronteira passa a fornecer, quando existirem, CPF e nascimento da pessoa (FR-020) |
| A incorporação é idempotente por `(fonte, id_externo)`, nunca atualiza nem remove e só registra divergência em log, sem valores | `academico/incorporacao.py`; 001 FR-031, FR-033 | O material é derivado na incorporação. Regra própria de atualização (FR-024) |
| Pessoa sem conclusão elegível não é materializada | 001 FR-039 (**[Escopo]**) | Inalterado. Quem não tem Pessoa no NIAE resulta em `NAO_CONFIRMADA` |
| A interface pega a Pessoa num único ponto (`pessoa_em_uso`) e a revalida a cada requisição; cookie assinado com o `pk` | `demonstracao/entrada.py`; `interface/views.py` (`_pessoa`) | A sessão da 018 substitui esse ponto sem tocar 005, 006, 007 nem as telas da jornada |
| Entrada e formações: uma Pessoa, N Conclusões; seleção quando há mais de uma pendente; posse verificada a cada ação | `participacao/entrada.py`; 007 FR-017 a FR-023, FR-044 | Formações e escolha continuam integralmente na 007 |
| Participação concluída já mostra só "pesquisa já respondida", sem respostas e sem formulário | `interface/views.py`; 008 US10, FR-023 | Nada a esconder nem a acrescentar (FR-052) |
| O rascunho retomado exibe as respostas salvas | `interface/formularios.py` (`_iniciais`) | Inalterado. É o risco residual aceito (Decisões do solicitante) |
| O convite da 016 aponta para uma URL neutra, igual para todos, sem identidade nem token | 016 FR-021, FR-022; `comunicacao/seguranca.py` (`validar_url`) | Passa a levar à entrada da 018, ainda neutra |
| O operador fictício é um adaptador separado da Pessoa | 010 FR-008; `demonstracao/operador.py` | Inalterado. Confirmar acesso como egresso não confere capacidade institucional |
| Modo de demonstração desligado: toda requisição dá 404. Não há autenticação, admin nem sessão do framework | `demonstracao/middleware.py`; `config/settings.py` | A 018 só funciona no modo de demonstração, com dados fictícios. A ativação real depende de decisões pendentes (DP-1801 a DP-1803) |
| Uma chave de pseudonimização já existe para exportações, validada antes do uso | `exportacao/pseudonimos.py` | As chaves da 018 são distintas dela e da chave do framework (FR-012) |

### Decisões do solicitante (2026-10-04)

Fechadas. A spec não as reabre.

1. **Mecanismo.** O mecanismo inicial é CPF + data de nascimento provenientes da fonte
   acadêmica. É verificação por conhecimento, não autenticação forte, e nenhum texto do
   sistema deve chamá-lo de "autenticação segura".
2. **O que fica fora.** Nada de Gov.br, SSO, OTP ou CAPTCHA nesta feature.
3. **Proteção do material.** HMAC com chaves secretas externas ao banco: uma para
   localizar pelo CPF e outra para verificar CPF + nascimento.
4. **Identidade interna.** O UUID da Pessoa continua sendo a identidade. CPF não a
   substitui.
5. **Limitação de tentativas.** Por origem e associada ao CPF protegido, com atraso
   progressivo e sem bloqueio permanente por CPF.
6. **Sem vazamento.** CPF e data de nascimento nunca aparecem em logs, URLs, telemetria ou
   mensagens.
7. **Mensagem genérica.** A mensagem é sempre a mesma e nunca revela se o CPF existe.
8. **Conferir antes.** "Conferir os dados" é oferecido antes de qualquer caminho
   excepcional.
9. **Falha não grava.** Uma falha de confirmação não cria nem altera Pessoa.
10. **Indisponibilidade ≠ não confirmação.** Indisponibilidade não encaminha à declaração.
11. **Formações.** Múltiplas formações continuam com a 007.
12. **Respostas.** A Participação concluída continua sem exibir respostas. O rascunho
    continua retomável.
13. **Profiling.** O profiling da base real ocorre em paralelo e não bloqueia esta spec.
14. **Fronteira com a 019.** Declaração de formação, resposta imediata, quarentena e
    validação pertencem à 019.

### Interpretação desta spec

Escolhas técnicas reversíveis, confirmadas no esclarecimento de 2026-10-04:

| # | Escolha | Por quê |
| --- | --- | --- |
| E1 | O terceiro resultado chama-se `VERIFICACAO_INDISPONIVEL`, não "fonte indisponível". É um estado **externo único** sobre causas **internas distintas**: chave não configurada, limite temporário e falha técnica | A verificação compara com material **já importado**; a fonte acadêmica não é consultada no acesso. Separar as causas impede tratar a limitação de tentativas como "erro técnico" |
| E2 | O material de verificação **pertence à capacidade de acesso**: fica associado à Pessoa, mas não é atributo acadêmico nem de domínio dela | Princípio XV: trocar ou remover o mecanismo (por exemplo, por Gov.br) não pode exigir mexer em Pessoa, Conclusão ou Participação. O desenho físico pertence ao plan |
| E3 | O acesso não incorpora nada sob demanda. Só existe quem já foi importado | Sem gravação no caminho de acesso; a cadência de importação continua em 001/DP-006 (DP-1805) |
| E4 | Formato inválido (CPF com dígito verificador errado, data impossível) recebe orientação de digitação, não `NAO_CONFIRMADA`, e não conta como falha de credencial. Conta, porém, na limitação geral por origem | É validação pública e não revela nada sobre a base. A limitação geral impede usar entradas inválidas para sobrecarregar a entrada sem custo |
| E5 | Valor corrigido vindo da fonte substitui o material anterior, sem histórico. Ausência numa carga não apaga o material existente. Remoção ou revogação explícita é outro caso, fora desta feature (DP-1809) | Não é fato acadêmico nem dado observado. Congelá-lo trancaria o egresso cuja data foi corrigida; apagá-lo por ausência trancaria o egresso por falha de carga |
| E6 | Na demonstração, as credenciais fictícias vêm da fonte simulada, nunca do banco | O banco não guarda CPF nem data em claro (FR-010) |

## Clarifications

### Session 2026-10-04

- Q: Como o terceiro resultado deve tratar as diferentes causas de indisponibilidade? → A:
  `VERIFICACAO_INDISPONIVEL` é o único estado externo. Internamente, as causas continuam
  distintas: chave não configurada, limite temporário e falha técnica. A limitação de
  tentativas não é erro técnico. (E1; FR-004, FR-030)
- Q: O material de verificação fica na Pessoa ou separado dela? → A: Separado. A Pessoa
  continua sendo identidade de domínio; o material pertence à capacidade de acesso. (E2;
  FR-016)
- Q: CPF estruturalmente inválido conta como tentativa? → A: Não conta como falha de
  credencial, mas entra na limitação geral por origem. (E4; FR-007, FR-030)
- Q: O que acontece com o material quando a fonte muda ou omite CPF ou data? → A: Valor
  corrigido substitui o material anterior. Ausência numa carga não apaga o existente.
  Remoção ou revogação explícita é caso diferente, fora desta feature. (E5; FR-024;
  DP-1809)
- Q: Os tempos de sessão são regra de domínio? → A: Não. São configuráveis, com padrões de
  30 minutos de inatividade e 8 horas de duração máxima, alteráveis sem nova spec.
  (FR-042)
- Q: A demonstração usa credenciais fictícias exibidas na entrada? → A: Sim, aprovado.
  (E6; FR-060)
- Q: A 018 mostra a data da resposta na Participação concluída? → A: Não. Sai do escopo
  para manter a feature restrita a identidade e acesso; a tela de concluída já não expõe
  respostas. Pode virar um ajuste posterior. (FR-052; Out of Scope)

## User Scenarios & Testing *(mandatory)*

Todos os egressos, CPFs e datas são fictícios e existem apenas no modo local de
demonstração. As cinco histórias são necessárias para fechar a feature.

### User Story 1 - Confirmar o acesso e chegar às próprias formações (Priority: P1)

O egresso chega pela entrada única, seja pelo link neutro de um convite, seja
espontaneamente. Informa CPF e data de nascimento e, confirmado, vê suas formações
exatamente como a 007/008 já apresenta. Daí inicia ou retoma a pesquisa.

**Why this priority**: é o caminho principal do produto e substitui o seletor fictício.

**Independent Test**: preparar a demonstração, abrir a entrada, informar as credenciais
fictícias de uma Pessoa com uma formação e de outra com três formações, e verificar a tela
de formações e o início da jornada.

**Acceptance Scenarios**:

1. **Given** uma Pessoa importada com material de verificação e uma formação em coleta,
   **When** o egresso informa o CPF e a data de nascimento corretos, **Then** o acesso é
   confirmado, a sessão passa a identificar essa Pessoa e a tela de formações da 008
   mostra a formação disponível para iniciar.
2. **Given** uma Pessoa com três Conclusões, **When** o acesso é confirmado, **Then**
   todas as formações aparecem com a situação da 007, e a escolha entre as pendentes
   segue a 007 (`SELECAO_NECESSARIA`). Nenhuma formação é pré-selecionada pela entrada.
3. **Given** o CPF digitado com ou sem pontuação, ou com espaços, **When** é submetido com
   a data correta, **Then** o resultado é o mesmo.
4. **Given** um convite da 016, **When** o egresso segue o link, **Then** chega à mesma
   entrada, sem nenhum dado preenchido e sem nada identificado pelo link.
5. **Given** uma sessão confirmada, **When** o egresso tenta abrir formação, Participação
   ou Seção de outra Pessoa, **Then** recebe a mesma recusa de hoje (007 FR-044; 008
   FR-089, FR-090).

---

### User Story 2 - Dados não confirmados, sem revelar nada e sem gravar nada (Priority: P1)

Os dados informados não conferem com nenhuma Pessoa. O motivo pode ser CPF desconhecido,
data divergente, CPF ausente na base ou dois registros com o mesmo CPF. O egresso recebe
sempre a mesma mensagem genérica e a opção de conferir os dados. Nada é criado nem
alterado. O resultado `NAO_CONFIRMADA` é o ponto de saída que a 019 vai usar.

**Why this priority**: o caminho de falha precisa ser seguro (sem enumeração, sem
duplicação) e honesto. É também o contrato para a 019.

**Independent Test**: para cada causa de falha nos cenários fictícios, submeter e
comparar status, conteúdo e efeitos. Tudo deve ser igual e nada deve ser gravado.

**Acceptance Scenarios**:

1. **Given** um CPF que não existe na base, **When** é submetido com qualquer data,
   **Then** a resposta é "Não foi possível confirmar os dados informados.", com a ação
   "Conferir os dados".
2. **Given** um CPF existente com a data errada, **When** é submetido, **Then** a resposta
   é **idêntica** à do cenário 1, no conteúdo e no status.
3. **Given** dois registros importados com o mesmo CPF (colisão), **When** o CPF é
   submetido com a data de um deles, **Then** o acesso **não** é confirmado: nenhuma
   Pessoa é escolhida nem fundida, e a resposta é idêntica à do cenário 1.
4. **Given** uma Pessoa importada sem CPF ou sem data de nascimento na fonte, **When**
   qualquer combinação é submetida, **Then** a resposta é idêntica à do cenário 1.
5. **Given** qualquer `NAO_CONFIRMADA`, **When** o egresso aciona "Conferir os dados",
   **Then** volta ao formulário com o CPF e a data que digitou, para corrigir, sem que
   isso apareça na URL.
6. **Given** qualquer `NAO_CONFIRMADA`, **When** o resultado é produzido, **Then** nenhuma
   Pessoa, Conclusão, Participação, Resposta ou sessão é criada ou alterada, e nenhuma
   formação, nome ou dado acadêmico é exibido.

---

### User Story 3 - Limitar tentativas sem trancar o egresso (Priority: P1)

Tentativas repetidas sem confirmação passam a esperar cada vez mais antes de serem
avaliadas. A limitação vale por origem e por CPF protegido. Nunca há bloqueio permanente,
e a espera não revela se o CPF existe.

**Why this priority**: é o controle que torna a verificação por conhecimento
proporcional. Sem ele, a entrada vira oráculo para testar pares CPF + data.

**Independent Test**: com relógio controlado, submeter falhas seguidas para o mesmo CPF,
existente e inexistente, e depois de origens diferentes. Verificar a espera, a recusa
temporária e a liberação depois do intervalo.

**Acceptance Scenarios**:

1. **Given** até três falhas seguidas para o mesmo CPF dentro da janela, **When** uma nova
   tentativa é feita, **Then** ela é avaliada normalmente.
2. **Given** a quarta falha seguida, **When** uma nova tentativa é feita antes do fim da
   espera, **Then** ela **não é avaliada** e o egresso recebe "Aguarde alguns instantes
   antes de tentar novamente". O estado externo é `VERIFICACAO_INDISPONIVEL`, nunca
   `NAO_CONFIRMADA`, e a causa interna é limite temporário, não falha técnica. As esperas
   seguintes crescem progressivamente até um teto.
3. **Given** a mesma sequência para um CPF que **não existe** na base, **When** comparada
   com a de um CPF existente, **Then** esperas, mensagens e status são idênticos.
4. **Given** a espera encerrada, **When** o egresso informa os dados corretos, **Then** o
   acesso é confirmado. Nenhum CPF fica bloqueado de forma permanente.
5. **Given** muitas falhas de uma mesma origem com CPFs diferentes, **When** a origem
   continua tentando, **Then** a limitação por origem também se aplica.
6. **Given** um acesso confirmado, **When** ocorre, **Then** as falhas anteriores daquele
   CPF deixam de contar.
7. **Given** uma origem que envia muitos CPFs estruturalmente inválidos, **When** continua
   enviando, **Then** nenhuma conta como falha de credencial, mas a limitação geral por
   origem se aplica do mesmo modo.

---

### User Story 4 - Sessão do egresso: expirar, sair e trocar de pessoa (Priority: P2)

A sessão guarda só a Pessoa confirmada. Ela expira por inatividade e por duração máxima,
pode ser encerrada pelo egresso e é substituída por uma nova confirmação.

**Why this priority**: os dispositivos podem ser compartilhados (Princípio XXI). Sem
expiração, um rascunho fica aberto a quem pegar o aparelho.

**Independent Test**: confirmar, avançar o relógio além da inatividade e verificar a volta
à entrada. Confirmar, acionar "Sair" e verificar. Confirmar A, depois confirmar B no mesmo
navegador, e verificar que só B está em uso.

**Acceptance Scenarios**:

1. **Given** uma sessão confirmada sem uso por mais que o limite de inatividade, **When**
   qualquer página da jornada é aberta, **Then** o egresso volta à entrada. As respostas
   salvas continuam preservadas.
2. **Given** uma sessão confirmada, **When** o egresso aciona "Sair", **Then** a sessão
   acaba e nenhuma página da jornada é acessível sem nova confirmação.
3. **Given** uma sessão da Pessoa A, **When** os dados da Pessoa B são confirmados no
   mesmo navegador, **Then** só B está em uso. Nada de A permanece acessível.
4. **Given** uma sessão confirmada, **When** a Pessoa deixa de existir ou o material de
   verificação dela muda, **Then** a próxima requisição revalida e, se for o caso, volta
   à entrada. A sessão nunca guarda formação, Campanha, Participação, CPF nem data.

---

### User Story 5 - Importar o material de verificação protegido (Priority: P1)

Ao incorporar uma Pessoa, o sistema recebe da fonte o CPF e a data de nascimento quando
existem. Deriva deles o material protegido e **nunca guarda os valores em claro**. Pessoas
sem esses dados continuam sendo incorporadas normalmente, só que sem acesso pelo caminho
principal.

**Why this priority**: sem o material, não há o que conferir. É aqui que se decide quem
entra pelo caminho automático e quem cairá na exceção da 019.

**Independent Test**: preparar a demonstração e verificar, no banco, que nenhum CPF nem
data aparece em claro. Conferir que cada Pessoa fictícia com CPF e data tem material
completo, que a Pessoa com CPF e sem data tem só o identificador, que as demais não têm
material e que reincorporar não duplica nada.

**Acceptance Scenarios**:

1. **Given** a fonte devolve uma Pessoa com CPF e data, **When** ela é incorporada,
   **Then** a Pessoa passa a ter o material de verificação, e nenhum valor em claro é
   persistido nem registrado.
2. **Given** a fonte devolve uma Pessoa sem CPF, ou sem data, **When** ela é incorporada,
   **Then** a Pessoa e suas Conclusões são incorporadas como hoje, sem material completo.
3. **Given** uma Pessoa já incorporada, **When** a fonte passa a devolver uma data de
   nascimento diferente, **Then** o material é atualizado para refletir a fonte, a
   divergência é sinalizada só com o nome do campo e nenhuma Participação ou Resposta é
   afetada.
4. **Given** uma Pessoa já incorporada com material, **When** a fonte passa a devolvê-la
   sem CPF ou sem data, **Then** o material existente é mantido e a ausência é sinalizada,
   como a 001 já faz com ausências. Ausência numa carga não é remoção. Remoção ou
   revogação explícita do dado pela fonte fica fora desta feature (DP-1809).
5. **Given** chaves não configuradas, inválidas ou iguais a outra chave do sistema,
   **When** uma incorporação traria CPF ou data, **Then** ela é recusada por erro de
   configuração antes de gravar qualquer coisa. Nada é incorporado sem material nem com
   material calculado de forma insegura.
6. **Given** a fonte devolve duas Pessoas (referências distintas) com o mesmo CPF, **When**
   ambas são incorporadas, **Then** as duas existem, nenhuma é fundida, a colisão é
   sinalizada sem valores e o acesso por esse CPF resulta em `NAO_CONFIRMADA` (US2.3).

---

### Edge Cases

- **CPF com pontuação, espaços ou zeros à esquerda**: normalizado para 11 dígitos antes de
  qualquer cálculo. Zeros à esquerda fazem parte do CPF.
- **CPF com menos ou mais dígitos, ou dígito verificador inválido**: orientação de
  digitação ("Confira o CPF informado"), sem avaliar. Não conta como falha de credencial
  nem revela nada, mas conta na limitação geral por origem (E4; FR-030).
- **Data impossível (31/02), futura ou em formato inválido**: orientação de digitação, sem
  avaliar. Mesma regra de limitação do CPF inválido.
- **Data plausível mas divergente da base, inclusive com dia e mês trocados**:
  `NAO_CONFIRMADA`. Não há tolerância nem correção automática.
- **Data coringa na base (por exemplo, 01/01/1900)**: tratada como qualquer valor. Quem
  detecta e corrige é o profiling e o registro acadêmico (DP-1804; 001/DP-005).
- **Mesmo CPF em matrículas diferentes da mesma pessoa**: a fronteira da fonte as entrega
  como **uma Pessoa com várias Conclusões**, sempre que a fonte permitir essa associação
  (FR-021). Se não permitir, há colisão (US5.6).
- **Recém-formado ainda não importado**: `NAO_CONFIRMADA`. A cadência de importação é
  DP-1805.
- **Pessoa confirmada sem nenhuma formação em coleta**: segue para a 007, que informa "sem
  pesquisa disponível". Não é falha de acesso.
- **Duas abas, uma confirmando A e outra B**: vale a última confirmação. A aba antiga
  passa a operar como B, e a posse de cada ação continua verificada (007 FR-044).
- **Reenvio do formulário (voltar no navegador)**: é nova tentativa. Conta para a
  limitação se falhar e nunca reaproveita resultado anterior.
- **Requisição GET com CPF ou data na URL**: ignorada e nunca avaliada. O formulário só
  aceita POST com proteção CSRF.
- **Chave trocada sem reimportação**: todo acesso passa a resultar em `NAO_CONFIRMADA`,
  indistinguível de uma falha comum. A troca de chave exige reimportação, e o procedimento
  pertence a DP-1803. A 018 não cria detecção automática dessa situação.
- **Modo de demonstração desligado**: nenhuma rota responde, como hoje.
- **Base com Pessoas de outra fonte além da simulada, em modo de demonstração**: a entrada
  recusa operar, como a 016 já faz (FR-005).
- **Operador fictício e egresso no mesmo navegador**: são sessões independentes.
  Confirmar acesso como egresso não concede nem retira capacidade institucional (010
  FR-008).

## Requirements *(mandatory)*

Etiquetas de origem: **[Solicitante]** é decisão do solicitante de 2026-10-04;
**[Const.]** decorre da Constituição; **[Arquitetura]** é decisão arquitetural;
**[Hipótese]** é hipótese reversível; **[Escopo]** é limite desta feature; **[00n]** é
herdado da feature indicada.

### Functional Requirements

#### Entrada e contrato de verificação

- **FR-001**: DEVE existir uma única entrada do egresso, a mesma para acesso espontâneo e
  para acesso vindo de comunicação. Ela pede apenas CPF e data de nascimento e não exige
  conta, senha, cadastro, e-mail nem qualquer outro dado. [Solicitante; Const. XV, XIV]
- **FR-002**: A verificação DEVE produzir exatamente um de três resultados:
  - `CONFIRMADA`, com a Pessoa resolvida;
  - `NAO_CONFIRMADA`;
  - `VERIFICACAO_INDISPONIVEL`.

  Formato inválido (FR-007) não é resultado de verificação: é orientação de digitação,
  sem avaliação. [Solicitante; Arquitetura]
- **FR-003**: `CONFIRMADA` DEVE ocorrer somente quando:
  - o CPF normalizado localiza **exatamente uma** Pessoa com material completo; e
  - o par CPF + data confere com o material dessa Pessoa.

  Em qualquer outro caso, inclusive colisão de CPF entre Pessoas, o resultado é
  `NAO_CONFIRMADA`. [Solicitante; 001 FR-034]
- **FR-004**: `VERIFICACAO_INDISPONIVEL` é o estado externo único para impedimentos
  temporários ou técnicos. Internamente, DEVE preservar causas distintas:
  - **chave não configurada**: chaves ausentes, curtas ou iguais a outra chave (FR-012);
  - **limite temporário**: tentativa recusada pela limitação (FR-030);
  - **falha técnica**: erro inesperado da verificação.

  A limitação de tentativas NÃO DEVE ser registrada nem tratada como falha técnica. Para
  o egresso, as três causas aparecem como indisponibilidade temporária, com a mensagem de
  espera no caso de limite temporário (FR-072). O estado NÃO DEVE encaminhar ao caminho
  excepcional nem ser apresentado como dados não confirmados. [Solicitante]
- **FR-005**: A entrada DEVE recusar operar no modo de demonstração quando houver Pessoas
  ou Conclusões de origem diferente da fonte simulada, sem expor dados. A recusa vale para
  exibir o formulário e para submetê-lo: um POST nessa base não é avaliado nem contado. Fora do modo de
  demonstração, nada responde (008 FR-001). [008 FR-008; 016 FR-012]
- **FR-006**: A verificação NÃO DEVE consultar a fonte acadêmica nem incorporar Pessoa no
  momento do acesso. Compara só com o material já importado (E3). [Arquitetura]
- **FR-007**: CPF DEVE ser normalizado (somente dígitos, 11 posições) e validado quanto
  ao dígito verificador. A data DEVE ser uma data válida, não futura. Entrada inválida
  recebe orientação de digitação específica do campo, não é avaliada e não conta como
  falha de credencial. Conta, porém, na limitação geral por origem (FR-030; E4).
  [Solicitante]

#### Proteção do material e dos dados informados

- **FR-010**: CPF e data de nascimento NÃO DEVEM ser persistidos em claro no Trajetória.
  Persistem somente:
  - um **identificador protegido do CPF**, que permite localizar;
  - um **verificador protegido de CPF + data**, que permite conferir.

  Ambos são derivados por HMAC com chaves secretas. [Solicitante; Const. XVI]
- **FR-011**: As duas derivações DEVEM usar **chaves distintas**, configuradas fora do
  banco de dados e fora do repositório. Hash sem chave é vedado. [Solicitante]
- **FR-012**: As chaves de acesso DEVEM ser distintas entre si, da chave do framework e da
  chave de pseudonimização das exportações. DEVEM ter tamanho mínimo e ser validadas antes
  de qualquer uso. Chave ausente ou inadequada gera `VERIFICACAO_INDISPONIVEL` no acesso e
  recusa da incorporação (US5.5). [Arquitetura; padrão de `exportacao/pseudonimos.py`]
- **FR-013**: CPF, data de nascimento e os valores protegidos NÃO DEVEM aparecer em logs,
  URLs, parâmetros de consulta, cabeçalhos de redirecionamento, telemetria, mensagens de
  erro ou páginas, com uma exceção: o reapresentar dos valores digitados ao próprio
  egresso no formulário de "Conferir os dados". [Solicitante; Const. Observabilidade]
- **FR-014**: A comparação do verificador DEVE ser feita de forma que o tempo de resposta
  não permita distinguir, na prática, CPF existente de inexistente, nem data certa de
  errada. Por exemplo, as duas derivações são sempre calculadas e a comparação é de tempo
  constante. [Arquitetura]
- **FR-015**: O material de verificação é **dado pessoal pseudonimizado** e DEVE ser
  tratado como dado protegido: menor privilégio, nunca exportado, nunca exibido a operador.
  [Const. XVI; DP-1802]
- **FR-016**: O material DEVE pertencer à capacidade de acesso e ser separável dela (E2).
  Removê-lo ou substituí-lo por outro mecanismo NÃO DEVE exigir alterar Pessoa, Conclusão,
  Participação, Resposta, exportações nem a jornada. [Const. XV, V]

#### Importação do material

- **FR-020**: A fronteira de dados acadêmicos DEVE poder fornecer, junto com a pessoa
  localizada, o CPF e a data de nascimento **quando existirem**, com ausência explícita e
  sem cadeia vazia (001 FR-023). A fonte simulada DEVE fornecê-los para seus cenários
  fictícios. [Arquitetura; 001]
- **FR-021**: A fronteira DEVE entregar como **uma única pessoa**, com várias Conclusões,
  os registros acadêmicos que a fonte permita associar ao mesmo indivíduo (por exemplo,
  matrículas com o mesmo CPF). Cada Conclusão preserva a sua referência de origem. Essa
  associação é responsabilidade da implementação da fonte, não do núcleo. [Solicitante;
  Const. V, XI; 001 FR-014]
- **FR-022**: A incorporação DEVE derivar o material no mesmo ato em que incorpora a
  Pessoa e DEVE descartar os valores em claro ao final dele. [Solicitante; Const. XVI]
- **FR-023**: Pessoa sem CPF ou sem data na fonte DEVE ser incorporada como hoje, sem
  material completo. Ela não tem acesso pelo caminho principal. [Solicitante]
- **FR-024**: Quando a fonte fornecer CPF ou data diferente do que originou o material, o
  valor corrigido DEVE substituir o material anterior, sem histórico. A divergência é
  sinalizada só com o nome do campo. A simples ausência do campo numa carga NÃO DEVE
  apagar nem alterar o material existente. Remoção ou revogação explícita indicada pela
  fonte é caso distinto, fora desta feature (DP-1809). Esta regra se aplica só ao
  material de verificação e não altera 001 FR-033 para dados acadêmicos (E5).
  [Solicitante]
- **FR-025**: Duas ou mais Pessoas com o mesmo identificador protegido de CPF DEVEM
  coexistir, sem fusão nem escolha. A colisão DEVE ser sinalizada sem valores pessoais
  (001 FR-034; 001/DP-003). [Arquitetura]
- **FR-026**: Os cenários da fonte simulada DEVEM cobrir, com dados fictícios
  documentados como tais:
  - Pessoa com uma formação;
  - Pessoa com várias formações;
  - Pessoa sem CPF;
  - Pessoa sem data de nascimento;
  - colisão de CPF entre duas Pessoas;
  - Pessoa existente na fonte sem conclusão elegível;
  - CPF com zeros à esquerda.

  Nenhum CPF fictício DEVE ser acompanhado de dado de pessoa real. [001 FR-028; Hipótese
  quanto à forma de geração]

#### Resultado não confirmado e saída para a 019

- **FR-030**: A limitação de tentativas DEVE ter dois níveis:
  - **Geral por origem.** Toda submissão à entrada conta, inclusive as de formato inválido
    (FR-007), para impedir sobrecarga sem custo; a confirmação bem-sucedida é descontada.
    O limiar é generoso e a janela é fixa, porque redes de campus e laboratórios
    compartilham a mesma origem e o tráfego contínuo não pode prolongar a espera.
  - **Por credencial.** Falhas de confirmação contam pelo identificador protegido do CPF,
    inclusive para CPF inexistente. Formato inválido não conta aqui. Até 3 falhas
    seguidas numa janela: avaliação normal.

  Regras comuns:
  - **Espera.** Passado o limiar de cada nível, uma espera crescente, com teto, antes da
    próxima avaliação.
  - **Durante a espera.** A tentativa é recusada sem avaliação (`VERIFICACAO_INDISPONIVEL`,
    causa interna limite temporário).
  - **Sem bloqueio permanente.** NÃO DEVE haver bloqueio permanente.
  - **Fim da contagem.** Confirmação bem-sucedida zera as falhas do CPF. Ao fim da
    janela, a contagem recomeça; nenhuma espera ultrapassa a janela.
  - **Simultaneidade.** Tentativas simultâneas para o mesmo CPF não escapam da contagem:
    uma é avaliada e as demais recebem a espera temporária.
  - **Valores exatos.** Os limiares do nível geral e os valores de espera pertencem ao
    plan, como parâmetros configuráveis.

  [Solicitante; Hipótese quanto aos valores]
- **FR-031**: Os contadores da limitação DEVEM ser transitórios, expirar sozinhos e NÃO
  DEVEM constituir registro de domínio, trilha de auditoria ou histórico de tentativas
  (DP-1806). [Const. XVI, XXII]
- **FR-032**: Toda `NAO_CONFIRMADA` DEVE apresentar a mesma mensagem ("Não foi possível
  confirmar os dados informados."), com o mesmo status e o mesmo conteúdo, qualquer que
  seja a causa interna:
  - CPF inexistente;
  - data divergente;
  - material incompleto;
  - colisão;
  - Pessoa não importada.

  [Solicitante]
- **FR-033**: A tela de `NAO_CONFIRMADA` DEVE apresentar o formulário já preenchido com
  os valores digitados e, no aviso, a ação "Conferir os dados", que leva o foco ao campo
  CPF. Os valores nunca trafegam na URL. [Solicitante]
- **FR-034**: `NAO_CONFIRMADA` NÃO DEVE:
  - criar nem alterar Pessoa, Conclusão, Participação, Resposta ou sessão;
  - exibir nome, formação ou qualquer dado acadêmico;
  - oferecer canal, formulário ou promessa de atendimento não decidido (DP-1807).

  [Solicitante; Const. XVI, XXIX]
- **FR-035**: O resultado `NAO_CONFIRMADA` DEVE ser um **ponto de saída explícito** da
  verificação, no qual a 019 acrescentará o caminho de declaração sem alterar a lógica de
  confirmação. A 018 NÃO DEVE persistir a causa interna da falha. A 019 poderá
  recalculá-la a partir do CPF que o próprio declarante informar. [Solicitante; Escopo;
  Const. XXII]

#### Sessão

- **FR-040**: `CONFIRMADA` DEVE estabelecer uma sessão do egresso que identifique **somente
  a Pessoa**. A sessão NÃO DEVE conter formação, Campanha, Participação, CPF, data ou
  material de verificação. [Solicitante; 007 FR-001]
- **FR-041**: A sessão DEVE ser revalidada a cada requisição: a Pessoa continua existindo e
  o material que deu origem à confirmação não mudou. Qualquer falha devolve o egresso à
  entrada, sem erro técnico. [Arquitetura]
- **FR-042**: A sessão DEVE expirar após um período de inatividade e após uma duração
  máxima, ambos **configuráveis**. Os padrões são 30 minutos de inatividade e 8 horas de
  duração máxima. São política operacional, não regra de domínio: mudam por configuração,
  sem nova spec. Fechar o navegador também encerra a sessão, por causa dos dispositivos
  compartilhados. Expirar NÃO DEVE afetar respostas já salvas. [Solicitante; Arquitetura
  quanto ao fechamento do navegador]
- **FR-043**: O egresso DEVE poder encerrar a sessão ("Sair") a partir de qualquer tela da
  jornada. Nova confirmação no mesmo navegador DEVE substituir integralmente a sessão
  anterior. A sessão do egresso DEVE ser independente da identificação do operador
  fictício (010). [Arquitetura; 010 FR-008]
- **FR-044**: A sessão DEVE substituir o ponto único de obtenção da Pessoa usado pela
  interface (008 FR-005), sem alterar Participação, Jornada, Respostas, Campanha nem as
  telas de formações, Seção, conclusão e confirmação. [008 FR-005; Const. XV]
- **FR-045**: Na ativação produtiva, a sessão e a entrada DEVEM operar somente sobre canal
  cifrado, com cookie protegido. Na demonstração local vale a configuração atual do modo
  de demonstração. [Const. XVI; DP-1803]

#### Jornada existente

- **FR-050**: Após `CONFIRMADA`, as formações, a resolução da entrada, a escolha de
  formação, o início, a retomada e a conclusão DEVEM ser exatamente os da 005 a 008. A 018
  NÃO DEVE pré-selecionar formação nem Campanha. [Solicitante; 007]
- **FR-051**: O rascunho continua retomável, exibindo as respostas salvas. [Solicitante;
  008]
- **FR-052**: Participação concluída NÃO DEVE exibir respostas nem permitir alteração, como
  hoje. A 018 não altera as telas de "já respondida". [Solicitante; 006; 008 US10]
- **FR-053**: O convite da 016 DEVE levar à entrada da 018 por URL neutra, sem
  identificação, token, formação ou Campanha. Seguir o link NÃO DEVE preencher dado nem
  identificar a Pessoa. [016 FR-021, FR-022; ADR 0004]

#### Seletor fictício e demonstração

- **FR-060**: O seletor de Pessoa fictícia da 008 DEVE deixar de ser a forma de entrar na
  jornada. Na demonstração, a entrada DEVE oferecer, claramente identificada como
  fictícia, a lista das credenciais dos cenários da fonte simulada, para teste manual. Essa
  lista é lida da fonte simulada, nunca do banco (E6). [Arquitetura; 008 FR-003, FR-004]
- **FR-061**: A entrada NÃO DEVE ser apresentada como login, conta ou "acesso seguro". A
  linguagem DEVE ser de confirmação de dados para acessar a pesquisa. [Solicitante; 008
  FR-004]
- **FR-062**: A seleção de operador fictício (010, 011, 016, 017) NÃO DEVE ser alterada.
  [Escopo]

#### Acessibilidade e mobile

- **FR-070**: O formulário DEVE ter rótulos visíveis e associados aos campos, ordem lógica
  e foco visível, e deve ser utilizável por teclado e leitor de tela. Os campos usam
  teclado numérico no celular. Erros de digitação são apresentados junto ao campo e
  anunciados. A data de nascimento NÃO DEVE depender de seletor de calendário. [Const. XX;
  eMAG; WCAG 2.1 AA]
- **FR-071**: Entrada, resultados e mensagens DEVEM funcionar a partir de 320 px de
  largura, sem rolagem horizontal, com a identidade visual da 015. [Const. XXI; 015]
- **FR-072**: Mensagens de espera e de indisponibilidade DEVEM ser compreensíveis, sem
  termos técnicos e sem contagem que revele detalhes da limitação. [Const. XX]

### Matriz mínima de verificação automatizada

| Situação | Resultado esperado | Requisitos |
| --- | --- | --- |
| CPF + data corretos, uma formação | `CONFIRMADA`; tela de formações | FR-002, FR-003, FR-050 |
| CPF + data corretos, três formações | `CONFIRMADA`; seleção da 007 | FR-050 |
| CPF com pontuação, espaços e zeros à esquerda | Mesmo resultado que sem formatação | FR-007 |
| DV inválido; data impossível ou futura | Orientação de digitação; não conta falha de credencial | FR-007 |
| Muitas submissões inválidas da mesma origem | Limitação geral por origem | FR-030 |
| CPF inexistente / data errada / sem material / colisão / não importada | `NAO_CONFIRMADA` idêntica nas cinco causas; nada gravado | FR-003, FR-032, FR-034 |
| Conferir os dados | Formulário com valores, sem URL com dados | FR-033, FR-013 |
| 4ª falha e seguintes, CPF existente × inexistente | Esperas e mensagens idênticas; sem bloqueio permanente | FR-030 |
| Muitas falhas da mesma origem | Limitação por origem | FR-030 |
| Chaves ausentes, curtas ou iguais a outra chave | `VERIFICACAO_INDISPONIVEL` no acesso; incorporação recusada | FR-012, US5.5 |
| Importação | Nenhum CPF ou data em claro no banco nem nos logs; material só com dados completos | FR-010, FR-013, FR-022, FR-023 |
| Data corrigida na fonte | Material atualizado; acesso com a nova data | FR-024 |
| Sessão: inatividade, máximo, sair, troca A→B, Pessoa alterada | Volta à entrada / só B / revalidação | FR-040 a FR-043 |
| Sessão, tela e redirecionamentos | Nunca contêm formação, Campanha, CPF ou data | FR-013, FR-040 |
| Link do convite | Entrada neutra, sem preenchimento | FR-053 |
| Concluída | Nenhuma Resposta exibida, como hoje | FR-052 |
| Chave ausente × limite × erro inesperado | Mesmo estado externo; causas internas distintas; limite nunca registrado como falha técnica | FR-004 |
| GET com dados; POST sem CSRF | Não avaliado | Edge Cases |
| Testes existentes de 005 a 008, 011, 016 e 017 | Continuam passando; muda só a forma de obter a Pessoa | FR-044, FR-062 |

### Key Entities *(include if feature involves data)*

- **Pessoa** *(001, identidade inalterada)*: identificada pelo UUID interno. Ganha, por
  meio da capacidade de acesso, um material de verificação opcional. CPF e data não viram
  atributos de domínio dela.
- **Material de verificação de acesso** *(novo; pertence à capacidade de acesso)*:
  - **Conteúdo.** Para uma Pessoa, o identificador protegido do CPF e o verificador
    protegido de CPF + data.
  - **Origem.** Derivado de dado institucional da fonte acadêmica. Não é dado declarado.
  - **Cardinalidade.** No máximo um por Pessoa. Ausente quando a fonte não fornece CPF ou
    data.
  - **Unicidade.** O identificador protegido não é único entre Pessoas (colisão possível,
    FR-025).
  - **Separação.** Separável sem tocar no restante do domínio (FR-016).
- **Sessão do egresso** *(técnica, transitória)*: identifica só a Pessoa confirmada. Tem
  inatividade e duração máxima. Não é entidade de domínio.
- **Contadores de tentativa** *(técnicos, transitórios)*: falhas por origem e por
  identificador protegido, com expiração. Não são registro de domínio.
- **Resultado de verificação** *(conceito de contrato, não persistido)*: `CONFIRMADA`
  (com a Pessoa), `NAO_CONFIRMADA` ou `VERIFICACAO_INDISPONIVEL`.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem | Fonte ou regra | Tratamento de divergência |
| --- | --- | --- | --- |
| CPF e data de nascimento da pessoa | Institucional | Fronteira de dados acadêmicos; nunca persistidos em claro | Material segue a fonte quando ela traz valor novo; ausência não remove; sinalização só com o nome do campo (FR-024) |
| Identificador protegido e verificador | Derivado (técnico, de acesso) | HMAC com chaves distintas sobre os valores institucionais | Recalculado quando a fonte muda; colisão sinalizada (FR-025) |
| CPF e data digitados pelo egresso | Informados para acesso; **não** são Resposta nem dado declarado da pesquisa | Formulário de entrada; descartados após a verificação, salvo a reapresentação em "Conferir os dados" | Divergência com a base = `NAO_CONFIRMADA`; nunca corrige a base |
| Formações apresentadas | Institucional | Conclusões da Pessoa (001), via 007 | Inalterado (001 FR-033) |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um egresso com dados corretos chega à tela das suas formações em menos de
  1 minuto, no celular, sem nenhuma informação além de CPF e data.
- **SC-002**: Em 100% dos cenários fictícios, o resultado é o esperado pela matriz:
  confirmação só com exatamente uma Pessoa e par correto.
- **SC-003**: As cinco causas de não confirmação produzem respostas indistinguíveis em
  conteúdo e status, e as esperas da limitação são idênticas para CPF existente e
  inexistente.
- **SC-004**: Nenhuma tentativa não confirmada cria ou altera Pessoa, Conclusão,
  Participação, Resposta ou sessão (verificado em 100% dos cenários de falha).
- **SC-005**: Uma busca pelos CPFs e datas fictícios no banco, nos logs da execução de
  testes e nas URLs geradas encontra **zero** ocorrências em claro.
- **SC-006**: Nenhum CPF fica impedido de forma permanente. Depois da espera máxima, o par
  correto confirma em 100% dos casos.
- **SC-007**: A jornada após a confirmação (formações, início, retomada, conclusão) é a
  mesma de hoje: os testes de 005 a 008 continuam válidos, mudando só a forma de obter a
  Pessoa.
- **SC-008**: Entrada e mensagens atendem WCAG 2.1 AA nas verificações automatizadas e
  manuais já usadas pela 015, a 320 px e no desktop.

## Assumptions

- A 018 opera só no modo local de demonstração, com a fonte simulada e dados fictícios. O
  mecanismo é desenhado para uso real, mas a ativação real depende de DP-1801 a DP-1803 e
  de um adaptador da fonte real (001/DP-001).
- O profiling da base real (cobertura e qualidade de CPF e data, duplicidade, associação
  de matrículas por CPF, cobertura por época) corre em paralelo. Ele mede o volume do
  caminho excepcional e não altera esta spec (DP-1804).
- A 019 é pré-requisito do piloto. Sem ela, quem não confirma não tem caminho, e egressos
  antigos regrediriam em relação ao formulário atual. A 018 sozinha não vai a piloto.
- A 017 está concluída e não interfere: a 018 não toca Campanha.
- Rascunho retomável com respostas salvas é risco residual aceito pelo solicitante. Quem
  conhecer CPF e data de outra pessoa pode abri-lo ou responder primeiro.

## Relação com outras features

- **001** — fornece Pessoa, Conclusão e a fronteira acadêmica. A 018 estende a fronteira
  com CPF e data (FR-020, FR-021) e a incorporação com o material (FR-022 a FR-025).
- **007/008** — recebem a Pessoa resolvida. A 018 troca só a forma de obtê-la (FR-044).
- **010/011/016/017** — inalteradas. O operador continua separado. O link da 016 leva à
  nova entrada (FR-053).
- **019 (futura)** — consome `NAO_CONFIRMADA` (FR-035): declaração de formação, resposta
  imediata, quarentena, validação acadêmica, associação ou criação de Pessoa e liberação
  analítica. Merece auditoria própria antes de ser especificada, por causa da relação
  entre Participação e Conclusão Acadêmica.

### Impacto nas features anteriores (notas de revisão a aplicar com a 018)

- **001 FR-005**: CPF e data de nascimento passam a ser obtidos da fonte, com consumidor
  concreto (a verificação de acesso), e **somente** como material protegido. O nome
  continua sem papel de identidade.
- **001 FR-006**: preservado. CPF não é chave da Pessoa. É material de acesso e critério
  de associação **dentro da fonte** (FR-021).
- **001 FR-028**: os cenários simulados ganham CPFs e datas fictícios (FR-026).
- **001 FR-033 / data-model "nunca atualizado"**: exceção limitada ao material de
  verificação (FR-024). Dados acadêmicos continuam como estão.
- **007 FR-002**: a proibição de entrada por CPF era escopo da 007 e continua valendo
  dentro dela. A 018 cria a entrada fora da 007, que segue recebendo a Pessoa resolvida.
- **008 FR-004, FR-007, FR-008**: o seletor de Pessoa fictícia deixa de ser a entrada da
  jornada (FR-060). A barreira "só fonte simulada" é preservada (FR-005).
- **016 FR-021**: a URL neutra passa a ser a da entrada da 018. A validação de URL local é
  ajustada no plan, se o caminho mudar.

## Invariantes Constitucionais Afetados *(mandatory)*

- **Terminologia, Pessoa; XI — identidade única**: o UUID continua sendo a identidade.
  Matrículas associáveis da mesma pessoa convergem para uma Pessoa com várias Conclusões
  (FR-021). Colisão nunca funde (FR-025). Nenhuma falha cria Pessoa (FR-034).
- **I — Longitudinalidade (NON-NEGOTIABLE)**: nenhuma Participação ou Resposta é criada,
  alterada ou reinterpretada pela 018. A cadeia Pessoa → Conclusão → Participação está
  intacta.
- **III — Dado institucional não é declarado (NON-NEGOTIABLE)**: CPF e data vêm da fonte
  institucional. O que o egresso digita é dado de acesso, nunca Resposta, e nunca corrige
  a base.
- **IV — Proveniência**: o material deriva da fonte que forneceu a Pessoa, com a mesma
  referência temporal da incorporação.
- **V — Desacoplamento (NON-NEGOTIABLE)**: a associação de matrículas e o formato dos dados
  na fonte ficam na implementação da fronteira (FR-021). O núcleo recebe dados canônicos.
- **XIV — Fricção**: dois campos, sem conta, senha nem e-mail. Formato inválido orienta sem
  punir.
- **XV — Identidade substituível**: o material pertence à capacidade de acesso e é
  separável (FR-016). Gov.br, SSO ou OTP poderão substituí-lo trocando só essa capacidade.
  Não há cadastro com senha. A proporcionalidade ao risco é decisão do solicitante, com
  aceitação institucional pendente (DP-1801).
- **XVI — Privacidade (NON-NEGOTIABLE)**: nada em claro, HMAC com chaves externas,
  ausência em logs e URLs, contadores transitórios. Base legal pendente e bloqueante para
  dados reais (DP-1802).
- **XX/XXI — Acessibilidade e mobile**: sem CAPTCHA; formulário acessível e numérico
  (FR-070 a FR-072).
- **XXII — YAGNI**: sem estrutura genérica de identidade, sem registro de tentativas, sem
  persistência da causa da falha.
- **XXIX — Hipóteses**: limiares, durações de sessão e regra de atualização do material
  estão marcados como hipóteses. Aceitação de risco, base legal, chaves e cadência estão
  como decisões pendentes.
- **Não afetados**: II (a definição de egresso continua na Conclusão), VII, VIII, IX, X,
  XII, XIII, XVII, XVIII, XIX, XXIII. Pertinentes, mas sem impacto.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence ao acompanhamento?** Pertence no limite necessário: o acompanhamento exige
   saber de qual Pessoa é a Participação. A gestão geral de identidade não pertence ao
   NIAE e não é criada.
2. **É necessária ao ciclo?** Sim. Sem verificação, qualquer pessoa responde por qualquer
   egresso, e a confiabilidade das respostas, propósito do sistema, fica comprometida.
3. **Há solução institucional mais adequada?** Possivelmente (Gov.br, SSO, Portal do
   Egresso), mas com fricção maior e sem decisão. Fica como evolução (DP-1808; 004/DP-406).
4. **Integração bastaria?** Não há hoje provedor institucional decidido para egressos. O
   desenho permite trocar o mecanismo sem tocar o domínio (FR-016).
5. **Aumenta o acoplamento?** Não. O núcleo continua recebendo uma Pessoa resolvida. CPF e
   data ficam confinados à fronteira acadêmica e à capacidade de acesso.

## Out of Scope *(mandatory)*

- Gov.br, SSO, OTP, link mágico, CAPTCHA, senha, conta, cadastro e recuperação de acesso.
- Declaração de formação, resposta sem Conclusão, quarentena, validação pelo registro
  acadêmico, associação ou criação de Pessoa a partir de declaração e canal de atendimento
  (todos da **019**).
- Persistência da causa da falha, registro ou trilha de tentativas.
- Incorporação sob demanda no acesso; adaptador da fonte real; cadência de importação.
- Atualização de dados cadastrais pelo egresso; e-mail ou telefone na Pessoa.
- Lote, mobilização real, marcador de origem do acesso.
- Identificação produtiva de operadores (010/DP-1001).
- Exibição de respostas concluídas; "Minha Trajetória"; consulta das próprias respostas
  (008/DP-802).
- Reconciliação entre fontes diferentes (001/DP-003).
- Revisão de 001 FR-039 (Pessoa sem conclusão).
- Data da resposta na tela de Participação concluída (possível ajuste posterior da
  jornada).
- Remoção ou revogação explícita de CPF ou data pela fonte (DP-1809).

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

### Herdadas, explicitamente preservadas

- **001/DP-001, DP-002**: fonte real e seus identificadores. Tratamento: fonte simulada; a
  associação de matrículas por CPF fica na implementação real (FR-021).
- **001/DP-003**: reconciliação entre fontes. Tratamento: nenhuma; colisão nunca funde.
- **001/DP-005, DP-006**: divergência e sincronização. Tratamento: FR-024 para o material;
  cadência em DP-1805.
- **001/DP-009, 016/DP-1603**: base legal de dados pessoais. Ampliada por DP-1802.
- **004/DP-406**: forma definitiva de acesso (URL institucional, Portal do Egresso).
  Tratamento: entrada única, sem presumir o Portal.
- **005/DP-504**: base legal das respostas sensíveis. O rascunho exibido após a
  confirmação continua dependente dela.
- **008/DP-802**: o egresso ver as próprias respostas. Inalterado: concluída não as
  mostra.

### Novas

- **DP-1801** — DECISÃO PENDENTE: aceitação institucional do nível de garantia da
  verificação por conhecimento (CPF + data) para o uso real, incluindo o risco residual de
  alguém abrir um rascunho ou responder no lugar do egresso. Instância competente:
  encarregado de dados, com CPAEG/Proex. Impacto: ativação real. Tratamento provisório:
  decisão de produto do solicitante, só com dados fictícios. **Bloqueia o uso real.**
- **DP-1802** — DECISÃO PENDENTE: base legal, finalidade, transparência e retenção do
  tratamento de CPF, data de nascimento e do material pseudonimizado para verificar
  acesso. Instância competente: encarregado de dados. Impacto: FR-010 a FR-016, FR-020 a
  FR-024. Tratamento provisório: só dados fictícios. **Bloqueia o uso real.**
- **DP-1803** — DECISÃO PENDENTE: custódia, geração, rotação e responsável pelas chaves de
  acesso; procedimento de reimportação na troca de chave; HTTPS e cookie protegido em
  produção. Instância competente: DTI, com o encarregado. Impacto: FR-011, FR-012, FR-045.
  Tratamento provisório: chaves locais de demonstração e teste. **Bloqueia o uso real.**
- **DP-1804** — DECISÃO PENDENTE: resultado do profiling da base real (cobertura de CPF e
  data por época, CPFs inválidos ou duplicados, datas coringa, associação de matrículas
  por CPF) e o que fazer com qualidade insuficiente (correção na fonte, caminho da 019).
  Instância competente: DTI e registro acadêmico, com CPAEG. Impacto: volume do caminho
  excepcional. Tratamento provisório: não bloqueia a 018.
- **DP-1805** — DECISÃO PENDENTE: cadência de importação e prazo para que um recém-formado
  possa confirmar acesso (relacionada a 001/DP-006). Instância competente: DTI e registro
  acadêmico. Impacto: quem cai em `NAO_CONFIRMADA` por não estar importado. Tratamento
  provisório: preparo explícito da demonstração.
- **DP-1806** — DECISÃO PENDENTE: necessidade de registrar eventos de segurança da entrada
  (volume de falhas, origens) para detecção de abuso, com finalidade, granularidade e
  retenção. Instância competente: DTI e encarregado. Impacto: FR-031. Tratamento
  provisório: só contadores transitórios e sinais técnicos sem dados pessoais.
- **DP-1807** — DECISÃO PENDENTE: orientação e canal oferecidos a quem não confirma (texto,
  atendimento, responsável no campus). Relacionada à 019. Instância competente:
  Proex/CPAEG com DIREC/CSAEG e registro acadêmico. Impacto: FR-034, FR-035. Tratamento
  provisório: só a mensagem genérica e "Conferir os dados".
- **DP-1808** — DECISÃO PENDENTE: se e quando um mecanismo de garantia maior (Gov.br, SSO
  ou outro) substituirá ou complementará a verificação por conhecimento, e sua relação com
  o Portal do Egresso. Instância competente: Proex, DTI e encarregado. Impacto: nenhum
  nesta feature (FR-016 garante a troca). Tratamento provisório: inexistente.
- **DP-1809** — DECISÃO PENDENTE: como a fonte real indica que um CPF ou data foi removido
  ou revogado (por exemplo, registro corrigido por erro de pessoa) e qual o efeito sobre o
  material e sobre uma sessão aberta. Instância competente: DTI e registro acadêmico.
  Impacto: FR-024. Tratamento provisório: ausência numa carga não apaga o material; não
  há remoção explícita nesta feature.

### Escolhas da spec confirmadas

As sete escolhas técnicas da versão inicial foram decididas pelo solicitante em
2026-10-04. Ver Clarifications e a tabela "Interpretação desta spec".


## Nota de revisão pela Feature 019 (2026-10-04)

FR-034 continua sem persistir falhas da verificação. NAO_CONFIRMADA oferece a declaração por selo transitório em POST, sem reavaliar o par. O selo transitório fica na própria 018 (`acesso/transito.py`, chave A), como ponto de saída de FR-035. O sujeito declarante, exclusivo com a sessão de Pessoa e guardando só UUIDs e instantes, pertence à 019 (`declaracao/sessao.py`). A 018 não importa nem referencia a 019; a dependência é só 019 → 018. FR-005 admite a fonte fictícia de acervo histórico. A 018 nunca lê os dados persistidos para consulta ao acervo.

Referência: [019 — Formação não localizada e validação posterior](../019-formacao-declarada-validacao/spec.md).


## Nota de revisão pela Feature 021 (2026-10-04)

"Minha Trajetória", listada como fora do escopo, passou a ser especificada pela 021.

- **Sessão:** a página `/minha-trajetoria/` usa a sessão de Pessoa desta feature
  (`pessoa_em_uso`), sem mudança. Sem Pessoa na sessão, inclusive na sessão do declarante
  (019), vai para `/acesso/`.
- **Separação:** a 018 não importa nem conhece a 021. A capacidade de contexto da
  trajetória, que traz ingresso e agregados, é separada da `FonteAcademica`. O caminho de
  identidade nunca depende dela (021 FR-071).
- **Fora do escopo:** a consulta das próprias respostas continua fora (008/DP-802). A 021
  não lê Respostas.

Referência: [021 — Minha Trajetória: narrativa visual personalizada](../021-minha-trajetoria-narrativa/spec.md).


## Nota de revisão pela Feature 020 (2026-10-05)

A sessão de Pessoa desta feature (`pessoa_em_uso`) também autoriza a página `/meu-email/` da 020, sem mudança. Sem Pessoa, inclusive na sessão do declarante, a página vai para `/acesso/`. O e-mail não vira credencial nem fator de verificação. FR-053 (link neutro) é preservado pelo envio por Lote.

Referência: [020 — Mobilização real, Lotes e contatos do egresso](../020-mobilizacao-real-lotes-contatos/spec.md).


## Nota de revisão pela Feature 023 (2026-10-05)

- **FR-040:** a sessão da Pessoa pode conter, além dela, só a chave opaca do registro do envio pendente (sem Participação, Seção nem valores).
- **FR-041 e FR-042:** quando a sessão deixa de valer, a volta à entrada leva o aviso de lista fechada `?aviso=sessao` ("Por segurança, confirme seus dados de novo para continuar."); sem sessão anterior, a entrada fica como antes. Os padrões de 30 minutos e 8 horas não mudam.
- **FR-043:** a nova confirmação substitui integralmente a sessão do sujeito; só a chave do envio pendente atravessa, para ser usada pelo dono da Participação ou descartada. "Sair" apaga o registro.
- **FR-032 e FR-033:** `NAO_CONFIRMADA` mantém a mesma mensagem e o mesmo conteúdo para toda causa; as saídas aparecem como dois passos numerados ("Conferir os dados", depois "Informar minha formação"). Depois de uma tentativa que falhou, a ligação "Continuar para suas formações" de uma sessão anterior não aparece.
- **Dica da data:** "Só os números, por exemplo 05031994, ou DD/MM/AAAA".

Referência: [023 — Jornada de resposta com menos esforço](../023-jornada-menos-esforco/spec.md).
