# Feature Specification: Formação não localizada e validação posterior

**Feature**: `019-formacao-declarada-validacao`

**Feature Branch**: `claude/spec-019-academic-context-d2481f` (a partir da `main` em
`2f1ee86`, com a 018 mergeada)

**Created**: 2026-10-04

**Status**: Implementada e validada em 2026-10-04, restrita à demonstração.
Evidências em [validacao.md](validacao.md).
- A emenda constitucional que a feature exige foi **aplicada**: Constituição 2.0.0, MAJOR,
  aprovada em 2026-10-04 com o diff da
  [auditoria da 019, §11](../../docs/auditorias/2026-10-04-formacao-declarada-validacao.md#11-emenda-constitucional--diff-mínimo-para-revisão).
- Plan, tasks e `/speckit-analyze` concluídos em 2026-10-04. Implementação concluída
  a pedido do solicitante, com as 69 tarefas verificadas.

**Input**: Solicitação da Feature 019. Um egresso cuja verificação na 018 resultou em
`NAO_CONFIRMADA` não pode ser impedido de responder. Ele informa a formação, responde
imediatamente à mesma Versão da Campanha e vai embora. A instituição valida a formação
depois. A validação torna a resposta utilizável sem nova ação do egresso. Enquanto não há
validação, a resposta fica fora dos dados analíticos oficiais.

## Contexto

A 018 deixou um ponto de saída explícito (018 FR-035). Quem não confirma CPF + data de
nascimento recebe uma mensagem genérica e pode conferir os dados, mas não tem caminho para
responder. A 018 sozinha não vai a piloto: egressos antigos, fora da base digital ou com
cadastro incompleto, regrediriam em relação ao formulário atual, que qualquer pessoa
responde (018, Assumptions).

O caso principal desta feature:

```text
018: CPF + data → NAO_CONFIRMADA
     "Não foi possível confirmar os dados informados."
     [Conferir os dados]          (vem antes, como na 018)
     [Informar minha formação]    ← 019
            │
            ▼
     Formação Declarada (nome, unidade, nível, curso, ano)
            │
            ▼
     MESMA Versão da Campanha → conclui
     "Obrigado. Sua resposta foi registrada.
      A formação informada passará por verificação institucional."
            │                                      (o egresso não precisa voltar)
            ▼
     PENDENTE ── fora dos dados oficiais
            │
            ▼  Validações de formação (CPAEG / CSAEG, conforme escopo)
     ┌──────┴────────────────────────────────────────────────┐
     CONFIRMADA                                            NÃO CONFIRMADA
     · Conclusão já existente (fonte digital), ou          · declaração e respostas
     · Referência de acervo histórico → fonte                preservadas, nunca oficiais
       institucional ACERVO_HISTORICO → incorporação (001)
            │
            ▼
     compatibilidade definitiva com a abrangência da Campanha + verificação de conflito
            │
            ▼
     DECLARADA_VALIDADA → entra no próximo snapshot (012) e nas exportações (013)
```

A [auditoria arquitetural da 019](../../docs/auditorias/2026-10-04-formacao-declarada-validacao.md)
comparou três formas de guardar a resposta antes da validação e recomendou a B′. O
solicitante a confirmou.

### Base existente e evidências

Inspeção da `main` em `2f1ee86`, em 2026-10-04.

| Fato atual | Evidência | Consequência para a 019 |
| --- | --- | --- |
| Escritas de Resposta, percurso e conclusão dependem só da Participação (Campanha, Versão, `concluida_em`), nunca da Conclusão | `participacao/operacoes.py` (`_escrever`, `concluir`); 006 FR-006 a FR-008 | A jornada é reusada integralmente para a Participação declarada |
| Só a admissão exige Conclusão e avalia critérios sobre ela | `operacoes.py` (`iniciar_participacao`); 004 FR-053 | Há um início declarado, com compatibilidade provisória (FR-021) |
| Campanha e Conclusão da Participação são "nunca alteradas depois da criação" | 005 FR-002; 006 FR-035 | A validação nunca religa a Participação. O vínculo mora na validação (B′) |
| Nenhuma Conclusão existe fora da fonte acadêmica | 001 FR-030; `academico/incorporacao.py` | A confirmação usa sempre uma Conclusão da fronteira: fonte digital ou fonte de acervo histórico (M1+) |
| Incorporação idempotente sob referência já existe, sem disparo no produto | `acesso/material.py` (`incorporar_com_material`); `fonte_academica/contrato.py` (`obter_conclusao`) | A validação passa a ser um disparo explícito desse caminho |
| A 012 encontra a Participação na leitura, por Campanha + Conclusão | `analitico/consultas.py` | O snapshot passa a congelar a Participação que compõe cada registro (FR-104) |
| A 013 não tem origem por linha; tem proveniência por coluna; `VERSAO_CONTRATO = 1` | `exportacao/contrato.py`; 013 FR-052, FR-065 | Uma coluna base nova de origem da formação exige nova versão do contrato (FR-106) |
| O acompanhamento proíbe lista nominal e consulta individual | 011 FR-080 a FR-084 | A fila é área própria; a 011 ganha só indicador agregado com link (FR-060, FR-101) |
| Capacidades são funções nomeadas por papel; escopo CSAEG pela unidade, em texto livre | `governanca/regras.py`; 010 FR-015, FR-017 | Capacidade nova de validar formação (FR-062) |
| Critérios da Campanha ficam imutáveis depois da abertura | 004 (nome, Versão, período e critérios fixados na abertura) | A compatibilidade definitiva é avaliada contra critérios estáveis (FR-024) |
| O material de verificação usa HMAC com chaves externas ao banco; nada em claro | 018 FR-010 a FR-013; `acesso/chaves.py` | A declaração é identificada pelos mesmos derivados protegidos (HMAC). Como HMAC é irreversível e não serve à busca no acervo, CPF e data também são guardados **criptografados**, com chave própria (FR-014, FR-114) |
| Chaves externas validadas antes do uso | `exportacao/pseudonimos.py`; 018 FR-012 | Mesmo padrão para a chave de criptografia dos dados de consulta ao acervo (FR-115) |
| A demonstração recusa Pessoa ou Conclusão de fonte diferente da simulada | `demonstracao/base.py`; 018 FR-005 | A barreira passa a admitir também a fonte fictícia de acervo histórico (FR-131) |
| A baseline 2024 ainda contém Q10 a Q19 como Perguntas, e a Campanha de demonstração aplica uma cópia dela | 003 FR-029; `demonstracao/cenario.py` | Transitório aceito: quem declara também responde Q10 a Q19, como quem tem Conclusão. A 019 não altera o instrumento |

### Decisões do solicitante (2026-10-04)

Fechadas. A spec não as reabre.

1. **B′.** A Participação tem uma âncora: Conclusão Acadêmica **ou** Formação Declarada.
   A âncora nunca muda. A validação é um registro próprio que estabelece a
   correspondência entre a declaração e uma Conclusão.
2. **Instrumento único.** Mesma Versão para quem tem Conclusão e para quem declara. Dados
   acadêmicos ficam fora do instrumento. As perguntas de formação de 2024 só serviram de
   referência para escolher os campos.
3. **M1+.** Na confirmação, a Conclusão vem de uma de duas origens:
   - a fonte digital: uma Conclusão já existente ou incorporada pela referência na fonte;
   - o **acervo histórico**: o registro acadêmico confirma no acervo, o operador registra
     a referência institucional, e ela entra por uma fonte acadêmica própria,
     conceitualmente `ACERVO_HISTORICO`. A Conclusão nasce só pela incorporação da 001.

   O operador nunca cria Conclusão diretamente. A Formação Declarada nunca é fonte da
   Conclusão.
4. **Abrangência.**
   - A declaração não fica restrita a Campanhas sem critério.
   - Os valores declarados dão a **compatibilidade provisória**. A Conclusão confirmada
     dá a **compatibilidade definitiva**.
   - Uma formação confirmada fora da abrangência tem a resposta preservada, mas essa
     resposta não vale para aquela Campanha.
   - Foco de mobilização e Lote nunca limitam quem responde (ADR 0004).
5. **Fila.** Fica fora da 011, em área própria e com escopo de governança. A 011 mostra só
   um indicador agregado com link.
   - O fluxo mínimo é: PENDENTE → formação confirmada ou formação não confirmada.
   - Não há workflow de estados.
6. **Campos mínimos.** A declaração começa com nome, unidade, nível, curso e ano de
   conclusão. Dados adicionais só entram com consumidor concreto: o que o registro
   acadêmico precisar para localizar no acervo (DP-1906).
7. **Declaração preservada.** A declaração original nunca é sobrescrita. Declarado e
   confirmado coexistem.
8. **Emenda.** B′ exige emenda constitucional. A classificação será decidida pelo
   solicitante após revisar o diff.
9. **Não decidido pelo software.** Quem atesta a conclusão, qual evidência é exigida, a
   reabertura de decisão, a notificação ao egresso, o SLA e a retenção são decisões
   institucionais pendentes.
10. **CPF e data do declarante: dois usos, dois mecanismos** (revisão de 2026-10-04).
    - **Identificação e comparação**: HMAC, irreversível, com as chaves da 018.
      - O **HMAC do CPF** serve para candidatas e agrupamento.
      - O **HMAC do par** serve só para verificar quem retoma.
      - O par nunca é chave de identidade nem de deduplicação.
    - **Consulta ao acervo**: CPF e data com **criptografia reversível em nível de
      aplicação**, com chave externa ao banco, num conjunto próprio (**dados para
      consulta ao acervo**).
      - Esse conjunto nasce com a declaração, antes de qualquer validação.
      - Pode ser descartado sem apagar declaração nem decisão.
    - **Quando são gravados.** Só quando o egresso cria a declaração. Uma
      `NAO_CONFIRMADA` comum não deixa nada gravado.
    - **A quem pertencem.** Ao caminho de declaração e validação. Nunca a Pessoa,
      Resposta ou instrumento.
    - **Quem vê.** Só perfis autorizados à validação veem os valores descriptografados, e
      cada acesso é registrado.
    - **Onde nunca aparecem.** Logs, URLs, analytics, snapshots ou exportações.
    - **Retenção e descarte.** Por política institucional futura.

### Interpretação desta spec

Escolhas reversíveis feitas na spec. O `/speckit-clarify` pode revê-las.

| # | Escolha | Por quê |
| --- | --- | --- |
| E1 | CPF e data descriptografados aparecem só por **ação explícita** do operador ("Mostrar dados para consulta ao acervo"), na tela de uma declaração, nunca na lista nem automaticamente. O registro de acesso é feito a cada revelação | Menor exposição e registro de acesso com significado: "abriu a validação" não é "viu o CPF". **Confirmada pelo solicitante em 2026-10-04** |
| E2 | Só entram na fila as declarações cuja Participação está **concluída** | Rascunho não tem resposta completa a liberar. Validar rascunho seria trabalho sem efeito |
| E3 | A CSAEG vê as declarações da **unidade declarada** que está no seu vínculo. Só vincula Conclusão, e só registra acervo, da própria unidade. O restante fica com a CPAEG | Menor privilégio (XII). A unidade declarada é o único dado disponível para encaminhar |
| E4 | Conflito: a Participação que já integrava os dados oficiais continua oficial. A recém-confirmada fica em conflito, fora da análise | Não altera o que já valia e impede dupla contagem. A resolução é DP-1907 |
| E5 | A fonte de acervo entrega cada Referência de acervo como uma pessoa com uma Conclusão. A mesma referência converge para a mesma Conclusão. Associação a Pessoa de outra fonte não é feita | Reconciliação entre fontes é 001/DP-003 (DP-1909). Fundir seria inventar regra |
| E6 | O formulário da Referência de acervo **não** é pré-preenchido com os valores declarados. O declarado aparece ao lado, só para leitura | Impede que dado declarado vire institucional por cópia (Princípio III) |
| E7 | Na compatibilidade provisória, critério sobre atributo que a declaração não coleta (modalidade, forma de oferta) não impede o início. Ele é decidido na compatibilidade definitiva | Não perguntar o que não é necessário (XIV) e não excluir sem base |
| E8 | O mesmo par CPF + data, após nova `NAO_CONFIRMADA`, reencontra as próprias declarações em Campanhas em coleta, para continuar o rascunho ou ver que a resposta foi registrada | Reduz declaração duplicada. É o mesmo risco residual aceito na 018: quem conhece o par abre o rascunho |
| E9 | Decisões de validação e Referências de acervo são imutáveis na 019. Não há reabertura | Reabertura é DP-1905. Imutabilidade preserva snapshots |

## User Scenarios & Testing *(mandatory)*

Todos os egressos, CPFs, datas, acervos e referências são fictícios e existem apenas no
modo local de demonstração.

### User Story 1 - Informar a formação e responder imediatamente (Priority: P1)

O egresso não confirmou CPF e data. Conferiu os dados e continuou sem confirmação. Ele
escolhe "Informar minha formação" e preenche nome, unidade, nível, curso e ano de
conclusão. Responde à mesma pesquisa que os demais e recebe a confirmação de que a resposta
foi registrada e de que a formação passará por verificação. Não precisa voltar.

**Why this priority**: é a razão da feature. Sem ela, quem está fora da base digital não
responde.

**Independent Test**: com um CPF fictício inexistente na base, chegar a `NAO_CONFIRMADA`,
declarar uma formação e concluir a jornada. Verificar:
- a declaração e a Participação ancorada nela existem;
- nenhuma Pessoa nem Conclusão foi criada;
- as mensagens não afirmam validação.

**Acceptance Scenarios**:

1. **Given** um resultado `NAO_CONFIRMADA`, **When** a tela é exibida, **Then** "Conferir
   os dados" aparece antes de "Informar minha formação".
2. **Given** um resultado `VERIFICACAO_INDISPONIVEL` ou um formato inválido, **When** a
   tela é exibida, **Then** "Informar minha formação" **não** aparece.
3. **Given** a escolha de "Informar minha formação", **When** o egresso preenche os cinco
   campos e há exatamente uma Campanha compatível em coleta, **Then** ele pode começar.
   - Ao começar, a declaração e a Participação ancorada nela são gravadas juntas.
   - A Participação usa a Versão aplicada pela Campanha, a mesma de quem tem Conclusão.
4. **Given** uma Participação declarada em andamento, **When** o egresso navega, salva e
   conclui, **Then** Seções, condicionais, pendências e conclusão se comportam exatamente
   como na 006/008. O contexto exibido é "Formação informada por você: …", nunca "Você
   concluiu …".
5. **Given** a conclusão, **When** a confirmação é exibida, **Then** o texto é "Obrigado.
   Sua resposta foi registrada. A formação informada passará por verificação
   institucional.". Nada indica que a formação foi validada.
6. **Given** o egresso desistir antes de começar, **When** sai, **Then** nada foi gravado.
7. **Given** um CPF existente na base com data divergente e um CPF inexistente, **When**
   cada um percorre o caminho de declaração, **Then** telas, mensagens e status são
   idênticos. Nenhum dado da base é exibido.

---

### User Story 2 - Quarentena: resposta preservada e fora dos dados oficiais (Priority: P1)

Enquanto a formação não for validada, a resposta existe, mas não conta. Não entra em
contagens oficiais, snapshot ou exportação. Também não afeta a Pessoa que eventualmente
exista na base com o mesmo CPF.

**Why this priority**: sem quarentena, uma declaração falsa ou errada contamina dados
institucionais. É a condição para aceitar resposta antes da validação.

**Independent Test**: com uma Participação declarada pendente e concluída numa Campanha,
encerrar a Campanha, capturar o snapshot e exportar. Verificar que ela não aparece em
nenhum dado oficial e que conta só no indicador "Validações de formação".

**Acceptance Scenarios**:

1. **Given** uma Participação declarada pendente, **When** os indicadores oficiais da 011
   são calculados, **Then** ela não conta em iniciadas, concluídas nem nas taxas. Ela
   conta no indicador "Validações de formação: N na fila".
2. **Given** a mesma situação, **When** um snapshot é capturado, **Then** ela não compõe o
   universo nem as contagens do snapshot, e a captura não falha por isso.
3. **Given** uma Pessoa importada com o mesmo CPF do declarante, **When** ela confirma o
   acesso pela 018, **Then** as formações dela aparecem como hoje. A declaração pendente
   **não** a faz ver "já respondida", e ela pode responder normalmente.
4. **Given** uma declaração, **When** é gravada, **Then** nenhuma Pessoa, Conclusão ou
   material de verificação é criado ou alterado.

---

### User Story 3 - Validar vinculando uma Conclusão da fonte digital (Priority: P1)

Um operador com a capacidade de validar abre a fila e vê a declaração, sem as respostas.
Confere a formação junto ao registro acadêmico. Como a formação existe na fonte digital,
ele escolhe um candidato sugerido ou informa a referência da formação na fonte, e registra
"Formação confirmada". A resposta passa a valer sem o egresso voltar.

**Why this priority**: é o caminho mais comum previsto: cadastro com data errada, Pessoa
sem CPF ou sem data, recém-formado ainda não importado.

**Independent Test**: para uma Pessoa fictícia sem data de nascimento, declarar, concluir e
validar pelo candidato sugerido. Para outra, existente na fonte e ainda não importada,
validar pela referência na fonte. Verificar o vínculo, a situação `DECLARADA_VALIDADA`, a
inclusão no snapshot seguinte e a declaração intacta.

**Acceptance Scenarios**:

1. **Given** uma declaração concluída e pendente, **When** o operador do escopo abre a
   fila, **Then** vê:
   - o nome declarado, a unidade, o nível, o curso e o ano declarados, o momento e a
     Campanha;
   - os candidatos sugeridos, quando houver.

   Não vê Respostas nem valores protegidos. Na lista, não vê CPF nem data.
2. **Given** a tela de validação de uma declaração, **When** o operador autorizado aciona
   "Mostrar dados para consulta ao acervo", **Then**:
   - vê o CPF e a data de nascimento informados pelo declarante, descriptografados;
   - fica registrado quem viu, qual declaração e quando, sem os valores.

   **When** um operador fora do escopo tenta, **Then** é recusado sem revelar nada.
3. **Given** que o identificador protegido do CPF declarado coincide com o de uma Pessoa
   importada, **When** a declaração é aberta, **Then** as Conclusões dessa Pessoa aparecem
   como candidatas.
4. **Given** a escolha de um candidato e "Formação confirmada", **When** o operador
   registra e confirma o aviso, **Then**:
   - a decisão é gravada com a Conclusão, o momento e o operador;
   - a Participação, a declaração e as Respostas não mudam;
   - a situação passa a `DECLARADA_VALIDADA`, se compatível e sem conflito.
5. **Given** a referência de uma formação que existe na fonte e ainda não foi importada,
   **When** o operador a informa, **Then** a Pessoa e a Conclusão são incorporadas pelo
   caminho idempotente da 001, e a declaração é vinculada a essa Conclusão.
6. **Given** uma referência inexistente na fonte, ou a fonte indisponível, **When** o
   operador registra, **Then** nada é gravado e a declaração continua pendente, com
   mensagem compreensível.
7. **Given** a Conclusão vinculada com curso e ano diferentes dos declarados, **When** a
   validação é exibida, **Then** o histórico mostra "confirmada com dados diferentes",
   com declarado e confirmado lado a lado. Os dados oficiais usam só a Conclusão.
8. **Given** uma Campanha encerrada e um snapshot capturado antes da validação, **When** a
   validação é registrada e um novo snapshot é capturado, **Then** o snapshot anterior
   continua idêntico e o novo inclui a Participação validada.

---

### User Story 4 - Validar pelo acervo histórico (Priority: P1)

A formação não existe em nenhuma base digital. O registro acadêmico a encontra no acervo
físico. O operador registra "Formação confirmada" pelo acervo histórico e informa a
referência do acervo e os valores encontrados nele. O sistema incorpora a Conclusão pela
fonte de acervo histórico e vincula a declaração.

**Why this priority**: é o egresso de 20, 30 ou 40 anos atrás, justamente quem a 019 precisa
atender. Sem este caminho, a declaração dele ficaria pendente para sempre.

**Independent Test**: declarar uma formação fictícia inexistente na fonte simulada,
concluir, registrar a Referência de acervo e verificar:
- a Conclusão nasceu com origem no acervo histórico, pelo caminho de incorporação;
- a declaração ficou intacta;
- a divergência é derivada corretamente;
- a Participação entra no snapshot seguinte.

**Acceptance Scenarios**:

1. **Given** a escolha "pelo acervo histórico", **When** o formulário abre, **Then** os
   campos do acervo aparecem **vazios**, com os valores declarados ao lado só para
   leitura.
2. **Given** referência, unidade, nível, curso e ano preenchidos, **When** o operador
   registra e confirma, **Then**:
   - a Referência de acervo é gravada como dado institucional, com o momento e o operador;
   - a Pessoa e a Conclusão são criadas **somente** pela incorporação da 001, com origem
     no acervo histórico;
   - a declaração é vinculada a essa Conclusão.
3. **Given** uma referência já registrada antes, para a mesma unidade, **When** é
   registrada de novo noutra validação, **Then** converge para a mesma Conclusão. Não há
   duplicação.
4. **Given** que o CPF declarado coincide com uma Pessoa de outra fonte, **When** a
   Referência de acervo é incorporada, **Then** a Conclusão do acervo pertence a uma
   Pessoa da fonte de acervo. A provável coincidência é sinalizada sem fusão (DP-1909).
5. **Given** ano incoerente com a data informada, ou campo obrigatório vazio, **When** o
   operador registra, **Then** nada é gravado e o campo é apontado.

---

### User Story 5 - Não confirmar, fora da abrangência e conflito (Priority: P1)

Nem toda declaração se converte em resposta oficial. A formação pode não ser encontrada. A
formação confirmada pode estar fora da abrangência da Campanha. Ou pode já existir resposta
oficial da mesma formação na mesma Campanha. Em todos os casos, nada é apagado, e nada é
contado duas vezes.

**Why this priority**: impede contaminação e dupla contagem, e preserva auditabilidade.

**Independent Test**:
- registrar "não confirmada" e verificar a preservação e a ausência nos dados oficiais;
- confirmar para uma Conclusão fora dos critérios de uma Campanha restrita;
- confirmar para uma Conclusão que já tem Participação institucional na mesma Campanha.

**Acceptance Scenarios**:

1. **Given** uma declaração, **When** o operador registra "Formação não confirmada",
   **Then** declaração e Respostas continuam gravadas, a situação é
   `DECLARADA_NAO_CONFIRMADA` e ela nunca integra dados oficiais.
2. **Given** uma Campanha restrita à pós-graduação e uma declaração de mestrado admitida
   provisoriamente, **When** a validação confirma uma Conclusão de graduação, **Then** a
   situação é `DECLARADA_FORA_DA_ABRANGENCIA`. As Respostas ficam preservadas e não valem
   para aquela Campanha.
3. **Given** a Conclusão X com Participação institucional (concluída ou em rascunho) na
   Campanha C, **When** uma declaração de C é confirmada para X, **Then**:
   - a decisão é gravada;
   - a declarada fica `DECLARADA_EM_CONFLITO`;
   - a institucional continua exatamente como estava;
   - a fila mostra o conflito como pendente de resolução administrativa.
4. **Given** uma declaração já validada para X em C, **When** outra declaração de C é
   confirmada para X, **Then** a segunda fica em conflito e a primeira continua oficial.
5. **Given** uma declaração validada para X em C, sem conflito, **When** a Pessoa de X
   confirma o acesso pela 018, **Then** a formação X aparece como já respondida em C, e
   nenhuma segunda Participação é criada.
6. **Given** a tela de validação de uma declaração cuja confirmação geraria conflito,
   **When** o operador escolhe a Conclusão, **Then** é avisado antes de registrar, sem ver
   Respostas.

---

### User Story 6 - Abrangência provisória ao declarar (Priority: P2)

Quem declara chega a uma Campanha cuja Versão se aplica à formação declarada, mesmo que a
Campanha tenha abrangência restrita. Mobilização nunca interfere.

**Why this priority**: um instrumento próprio da pós-graduação precisa alcançar o egresso
antigo de pós-graduação fora da base digital (ADR 0004).

**Independent Test**: com Campanhas fictícias, uma sem critério e outra restrita, declarar
formações que caiam em zero, uma e duas Campanhas, e verificar a regra da 007 em cada caso.

**Acceptance Scenarios**:

1. **Given** só uma Campanha em coleta, sem critério, **When** qualquer formação é
   declarada, **Then** a Campanha é aplicável.
2. **Given** só uma Campanha em coleta, restrita a "Pós-graduação" em "Vila Velha",
   **When** a declaração é de pós-graduação em Vila Velha, **Then** é compatível
   provisoriamente. **When** é de graduação, **Then** "Não há pesquisa disponível no
   momento." e nada é gravado.
3. **Given** uma Campanha restrita a uma modalidade, que a declaração não coleta, **When**
   os demais critérios são atendidos, **Then** a compatibilidade provisória é aceita e a
   modalidade é decidida na validação (E7).
4. **Given** duas Campanhas compatíveis em coleta, **When** a formação é declarada,
   **Then** ocorre a ambiguidade operacional da 007 e nada é gravado.
5. **Given** um foco de mobilização qualquer, **When** existir, **Then** não participa da
   compatibilidade.

---

### User Story 7 - Retomar a declaração sem duplicar (Priority: P2)

O egresso que declarou e saiu antes de concluir, ou que já concluiu, volta com o mesmo CPF
e a mesma data. Após a nova `NAO_CONFIRMADA`, ele vê as formações que já informou. Pode
continuar o rascunho, ver que a resposta foi registrada ou informar outra formação.

**Why this priority**: evita declarações duplicadas, que geram trabalho na fila e conflito.
Também evita perder respostas em andamento.

**Independent Test**: declarar e sair no meio. Voltar com o mesmo par e continuar. Concluir,
voltar e verificar "resposta registrada". Voltar com outro par e verificar que nada da
primeira aparece.

**Acceptance Scenarios**:

1. **Given** uma declaração em rascunho numa Campanha em coleta, **When** o mesmo par
   resulta de novo em `NAO_CONFIRMADA`, **Then** "Informar minha formação" mostra a
   formação informada, com "Continuar".
2. **Given** uma declaração concluída, **When** o mesmo par volta, **Then** a formação
   aparece como "Resposta registrada; a formação passará por verificação institucional",
   sem as respostas. A situação da validação não é exibida.
3. **Given** declarações existentes, **When** o egresso escolhe "Informar outra formação",
   **Then** segue a US1.
4. **Given** outro par CPF + data, **When** percorre o caminho, **Then** não vê nenhuma
   declaração de outro par.
5. **Given** uma declaração em rascunho cuja Campanha encerrou, **When** o egresso volta,
   **Then** vê o período encerrado, como na 008, sem poder continuar.

---

### User Story 8 - Acompanhar pendências sem expor pessoas (Priority: P2)

A CPAEG e a CSAEG veem, no acompanhamento da Campanha, quantos itens aguardam na fila de
validação. É um único número agregado, no seu escopo, com link para a fila.

**Why this priority**: dá visibilidade operacional sem transformar pendência em taxa
oficial.

**Independent Test**: com declarações fictícias em cada situação e em unidades
diferentes, verificar o indicador para a CPAEG e para a CSAEG de Vitória, e que as taxas
oficiais não se alteram.

**Acceptance Scenarios**:

1. **Given** declarações pendentes de Vitória e de Serra, **When** a CSAEG de Vitória abre
   o acompanhamento, **Then** o indicador conta só as de Vitória e leva à fila.
2. **Given** qualquer situação declarada, exceto `DECLARADA_VALIDADA`, **When** as taxas
   oficiais são calculadas, **Then** ela não entra em numerador nem denominador.
3. **Given** uma `DECLARADA_VALIDADA`, **When** as contagens oficiais são calculadas,
   **Then** ela conta como qualquer Participação, no recorte da Conclusão vinculada.

---

### Edge Cases

- **Par que passa a confirmar.** Depois de declarar, o material é corrigido na fonte e o
  par confirma pela 018. O egresso entra como Pessoa. A declaração pendente continua
  separada (quarentena). Se for validada para uma Conclusão que já tem Participação
  institucional em C, há conflito (US5.3).
- **Mesmo egresso declara duas formações diferentes.** São duas declarações e duas
  Participações, validadas cada uma por si.
- **Mesmo egresso declara a mesma formação duas vezes.** As duas existem. A tela de
  validação mostra as outras declarações com o mesmo CPF (FR-065). A segunda confirmada
  para a mesma Conclusão na mesma Campanha fica em conflito.
- **Mesmo CPF com outra data.** O egresso volta digitando outra data, por erro dele ou da
  base. Ele não vê as declarações anteriores, porque a retomada exige o mesmo par, e pode
  declarar de novo. O agrupamento pelo HMAC do CPF mostra a duplicidade ao validador. O
  par nunca cria "outra pessoa".
- **Recusa do termo (Q1 = "Não") na baseline 2024.** A Participação declarada é concluída
  como recusa, como qualquer outra (012 FR-082), e entra na fila.
- **Campanha encerra com declaração em rascunho.** A declaração fica preservada, nunca
  entra na fila e nunca é oficial.
- **Validação depois do encerramento e do snapshot.** É permitida. O snapshot anterior não
  muda; uma nova captura a inclui.
- **Duas validações simultâneas da mesma declaração.** Uma é gravada. A outra recebe "já
  decidida" e nada grava.
- **Confirmação simultânea ao início institucional do mesmo par Campanha + Conclusão.**
  Nunca resultam duas Participações oficiais. Uma das duas ordens é aplicada integralmente.
- **Conclusão vinculada sem unidade.** Fica fora do escopo de toda CSAEG, como na 011
  FR-015. A validação é da CPAEG.
- **Referência de acervo com unidade diferente da declarada.** É permitido, desde que o
  operador tenha escopo na unidade registrada. A divergência é derivada.
- **Unidade ou nível declarados que não existem como valor de Conclusão.** As listas da
  declaração usam o vocabulário corrente das unidades e níveis (001/DP-007, 010/DP-1005).
- **Curso declarado com grafia livre.** É aceito como digitado. Não é normalizado nem
  comparado automaticamente para decidir nada.
- **Ano declarado futuro ou implausível.** É recusado com orientação de digitação. Ano
  "aproximado" é aceito como informado.
- **Nome declarado vazio ou só com espaços.** É recusado com orientação.
- **Fonte digital indisponível na validação.** Nada é gravado. É possível tentar de novo.
- **Operador sem escopo na unidade da Conclusão escolhida.** O registro é recusado sem
  revelar a Conclusão.
- **CPF declarado igual ao de duas Pessoas importadas (colisão da 018).** As Conclusões de
  ambas aparecem como candidatas. Nada é escolhido automaticamente.
- **Modo de demonstração desligado.** Nenhuma rota responde, como hoje.

## Requirements *(mandatory)*

Etiquetas de origem: **[Solicitante]** é decisão do solicitante de 2026-10-04;
**[Const.]** decorre da Constituição, já com a emenda prevista; **[Arquitetura]** é decisão
arquitetural; **[Hipótese]** é hipótese reversível; **[Escopo]** é limite desta feature;
**[00n]** é herdado da feature indicada. Nenhum requisito é **[Herdado]** do instrumento:
a 019 não altera Perguntas.

### Functional Requirements

A numeração original foi preservada na revisão de sanidade de 2026-10-04. As lacunas são
requisitos consolidados em outro. A correspondência está no
[checklist](checklists/requirements.md#revisão-de-sanidade-dos-requisitos).

#### Caminho de declaração a partir da 018

- **FR-001**: A tela de `NAO_CONFIRMADA` DEVE oferecer "Informar minha formação" depois de
  "Conferir os dados". A ação NÃO DEVE aparecer em `VERIFICACAO_INDISPONIVEL`, em
  orientação de formato nem em `CONFIRMADA`. [Solicitante; 018 FR-035]
- **FR-002**: O caminho de declaração DEVE ficar disponível somente a partir de uma
  resposta `NAO_CONFIRMADA`, para o par CPF + data que a produziu.
  - Não há nova avaliação nem nova contagem na limitação de tentativas.
  - CPF e data nunca trafegam na URL.
  - Entre a `NAO_CONFIRMADA` e o início (FR-016), CPF e data só podem existir num **selo
    transitório cifrado**, com finalidade explícita e validade curta, carregado no corpo
    dos POST da própria navegação.
  - O selo nunca vai para sessão, banco, URL, cookie ou log (FR-115).
  - Uma `NAO_CONFIRMADA` que não leva à criação de uma declaração NÃO DEVE deixar nenhum
    dado pessoal persistido, protegido ou não.

  [Solicitante; 018 FR-013, FR-030, FR-031]
- **FR-003**: O caminho de declaração NÃO DEVE revelar se o CPF existe na base, a causa
  interna da `NAO_CONFIRMADA`, nem nome, formação ou dado de Pessoa existente. Telas,
  mensagens e status DEVEM ser idênticos para CPF inexistente e para CPF existente com data
  divergente. [Solicitante; 018 FR-032]
- **FR-004**: A lógica de confirmação da 018 (`CONFIRMADA`, `NAO_CONFIRMADA`,
  `VERIFICACAO_INDISPONIVEL`) NÃO DEVE mudar. [018 FR-035]
- **FR-005**: Nenhuma etapa do caminho de declaração DEVE criar ou alterar Pessoa,
  Conclusão Acadêmica ou material de verificação. [Solicitante; Const. Terminologia
  (emenda)]
- **FR-006**: A linguagem DEVE ser de informar a formação para responder. NÃO DEVE dizer
  que a formação foi confirmada, reconhecida ou validada, nem prometer prazo, retorno ou
  atendimento (DP-1908, 018/DP-1807). O declarante NÃO DEVE ver o resultado da validação.
  [Solicitante]

#### Formação Declarada

- **FR-010**: A Formação Declarada DEVE conter exatamente:
  - **nome completo**: texto não vazio;
  - **unidade**: escolhida em lista;
  - **nível**: escolhido em lista;
  - **curso**: texto não vazio;
  - **ano de conclusão**: quatro dígitos, não futuro, aceito como lembrado;
  - os **derivados protegidos** de FR-014;
  - o **momento da declaração**.

  Os dados para consulta ao acervo (FR-114) ficam num conjunto separado, associado a ela.
  [Solicitante; Hipótese quanto aos campos]
- **FR-011**: A declaração NÃO DEVE exigir nem coletar outros dados. Matrícula, nome à
  época, modalidade e forma de oferta só entram com consumidor concreto, isto é, o
  procedimento do registro acadêmico para localizar o egresso (DP-1906). E-mail, telefone
  e outros contatos NÃO DEVEM ser coletados. [Solicitante; Const. XIV, XVI, XXII]
- **FR-012**: As listas de unidade e nível DEVEM usar o mesmo vocabulário dos atributos da
  Conclusão Acadêmica e dos critérios de Campanha, para que a compatibilidade provisória e
  a divergência sejam comparáveis. O vocabulário canônico continua pendente (001/DP-007,
  010/DP-1005). [Arquitetura]
- **FR-013**: A Formação Declarada é **dado declarado** (Princípio III, C). NÃO DEVE ser
  usada como contexto institucional, fonte de Conclusão Acadêmica nem contexto acadêmico
  exportado. [Solicitante; Const. III, Terminologia (emenda)]
- **FR-014**: CPF e data do declarante NÃO DEVEM ser persistidos em claro. Há três formas
  protegidas, cada uma com uma finalidade:

  | Forma | Finalidade | Proibição |
  | --- | --- | --- |
  | **HMAC do CPF** (identificador protegido da 018) | Candidatas (FR-065) e agrupamento das declarações do mesmo CPF | — |
  | **HMAC do par CPF + data** (verificador protegido da 018) | Só sessão e retomada (FR-040, FR-043): prova que quem volta conhece o par | NÃO DEVE servir de chave de identidade, agrupamento ou deduplicação. Uma data digitada ou cadastrada errada não pode criar "outra pessoa" |
  | **CPF e data com criptografia reversível** | Só a consulta humana ao acervo (FR-114 a FR-119) | — |

  As duas primeiras usam as chaves da 018. Comparação nunca descriptografa. [Solicitante
  (decisão 10); 018 FR-010]
- **FR-015**: Formação Declarada, Participação e Respostas DEVEM ser preservadas.
  - A Formação Declarada não muda a partir do início, nem pelo declarante nem pelo
    operador. Correção ocorre só pela validação, como divergência (FR-077).
  - A validação, em qualquer resultado, NÃO DEVE alterar nenhuma delas.

  [Solicitante; Const. I (emenda), III]
- **FR-016**: A Formação Declarada, os dados para consulta ao acervo e a Participação
  ancorada nela DEVEM ser gravados juntos, no início ("Começar"), ou nenhum deles.
  - Desistir antes do início NÃO DEVE gravar nada.
  - Repetir a mesma ação de início (atualização, duplo clique, reenvio) NÃO DEVE criar
    outra declaração: leva à mesma Participação.
  - Declarar outra formação é uma nova ação.

  [Solicitante; Const. XVI]

#### Abrangência e escolha da Campanha

- **FR-020**: A declaração DEVE poder ser aplicada a Campanha EM COLETA **com ou sem
  critério**. Foco de mobilização, Lote e público de comunicação NÃO DEVEM participar de
  nenhuma das duas compatibilidades. [Solicitante; ADR 0004]
- **FR-021**: A **compatibilidade provisória** DEVE avaliar os valores declarados de
  unidade, nível e ano contra os critérios da Campanha, com a semântica da 004:
  - E entre critérios;
  - OU dentro do conjunto;
  - igualdade exata;
  - limites de ano inclusivos.

  Critério sobre atributo que a declaração não coleta NÃO DEVE impedir o início (E7).
  [Solicitante; 004 FR-020, FR-022]
- **FR-022**: A escolha da Campanha DEVE seguir a regra da 007:
  - nenhuma compatível: "Não há pesquisa disponível no momento.", sem gravar nada;
  - exatamente uma: o egresso pode começar;
  - duas ou mais: ambiguidade operacional, sem gravar nada.

  O egresso nunca escolhe a Campanha. [007 FR-014; 004/DP-404]
- **FR-023**: A compatibilidade provisória NÃO DEVE incluir a declaração na população da
  Campanha. População, elegíveis e contagens de elegibilidade da 004/011/012 continuam só
  sobre Conclusões. [004 FR-016, FR-017]
- **FR-024**: Na confirmação, a **compatibilidade definitiva** DEVE ser avaliada entre a
  Conclusão vinculada e os critérios da Campanha, fixados desde a abertura, pela regra da
  004. Se incompatível, a situação é `DECLARADA_FORA_DA_ABRANGENCIA`, e nada é desfeito
  nem movido. [Solicitante; 004]

#### Participação declarada e jornada

- **FR-030**: A Participação DEVE ter exatamente uma âncora: uma Conclusão Acadêmica ou
  uma Formação Declarada.
  - A âncora NÃO DEVE ser alterada depois da criação.
  - Cada Formação Declarada ancora exatamente uma Participação.

  [Solicitante (B′); Const. Terminologia (emenda); 005 FR-002 revisto]
- **FR-032**: Respostas, percurso, Seções, condicionais, rascunho, pendências, conclusão e
  rejeições de escrita (após concluir, fora da coleta) da Participação declarada DEVEM
  seguir integralmente a 005 e a 006, sem regra nova. [Solicitante; 005; 006]
- **FR-033**: As telas DEVEM ser as da 008, com a identidade visual da 015. Isso inclui
  não exibir Respostas depois da conclusão. As diferenças são:
  - **contexto**: rotulado como informado pelo egresso (por exemplo, "Formação informada
    por você: Técnico em Informática — Serra — 2004"), nunca "Você concluiu …";
  - **confirmação final**: "Obrigado. Sua resposta foi registrada. A formação informada
    passará por verificação institucional."

  [Solicitante; Const. III; 008; 014]
- **FR-036**: Enquanto não for `DECLARADA_VALIDADA`, a Participação declarada NÃO DEVE
  ser tratada como Participação de nenhuma Pessoa ou Conclusão. Em particular, a 007 não
  a mostra como "já respondida" (quarentena). [Solicitante; auditoria de identidade,
  adendo, regra 2]

#### Sessão do declarante e retomada

- **FR-040**: Ao escolher "Informar minha formação", DEVE ser estabelecida uma sessão do
  declarante.
  - **O que identifica.** Só as declarações do par: os identificadores delas, obtidos pelo
    HMAC do par no momento da entrada (FR-014). Nunca HMAC, CPF, data, Pessoa, formação
    ou Campanha.
  - **Substituição.** Substitui qualquer sessão anterior do egresso no navegador.
  - **Independência.** É independente do operador fictício.
  - **Regras.** Inatividade, duração máxima, fechamento do navegador e "Sair" seguem a
    sessão da 018, com os mesmos parâmetros.

  [Arquitetura; 018 FR-040 a FR-043]
- **FR-042**: A posse de Participação e Seção DEVE ser verificada a cada ação. O
  declarante só acessa Participações ancoradas em declarações do próprio par. A recusa é a
  mesma, indistinguível, da 008. [008 FR-089, FR-090; 007 FR-044]
- **FR-043**: Antes do formulário de declaração, DEVEM ser listadas as declarações do
  mesmo par em Campanhas em coleta:
  - em andamento: "Continuar";
  - concluída: "Resposta registrada", sem situação da validação;
  - período encerrado: como na 008.

  Em seguida vem "Informar outra formação". [Hipótese (E8)]

#### Situação analítica e quarentena

- **FR-050**: A situação analítica de toda Participação DEVE ser **derivada** da âncora e
  da validação, nunca gravada na Participação. Vale a primeira condição satisfeita:

  | Situação | Condição |
  | --- | --- |
  | `INSTITUCIONAL` | âncora é Conclusão |
  | `DECLARADA_PENDENTE` | âncora é declaração sem decisão |
  | `DECLARADA_NAO_CONFIRMADA` | decisão "não confirmada" |
  | `DECLARADA_FORA_DA_ABRANGENCIA` | confirmada, Conclusão incompatível (FR-024) |
  | `DECLARADA_EM_CONFLITO` | confirmada, compatível, com conflito detectado na validação e ainda pendente (FR-090) |
  | `DECLARADA_VALIDADA` | confirmada, compatível, sem conflito |

  [Arquitetura; Const. I (emenda)]
- **FR-051**: São **oficiais** apenas `INSTITUCIONAL` e `DECLARADA_VALIDADA`.
  - **Onde entram.** Só elas integram as contagens e taxas oficiais da 011, o universo e
    os indicadores da 012 e as exportações da 013.
  - **Contexto.** O contexto acadêmico oficial vem da **Conclusão efetiva**: a âncora,
    quando institucional, ou a Conclusão da validação.
  - **Preservação.** Participações não oficiais NÃO DEVEM ser apagadas nem alteradas.

  [Solicitante; Const. I (emenda), III, VIII]

#### Fila "Validações de formação"

- **FR-060**: DEVE existir uma área própria de validações de formação, fora das telas da
  011, acessível a quem tem a capacidade (FR-062). Ela opera só com dados fictícios até
  DP-1902. [Solicitante; Const. XVI]
- **FR-061**: A fila DEVE listar:
  - as declarações cuja Participação está **concluída** e ainda sem decisão;
  - as decisões em conflito, como "resolução administrativa pendente".

  Rascunhos NÃO DEVEM entrar (E2). Não há outros estados, atribuição nem prazo.
  [Solicitante; Hipótese]
- **FR-062**: DEVE existir a capacidade nomeada de validar formação, para CPAEG e CSAEG,
  no padrão da 010. A interface DEVE dizer que o operador **registra o resultado obtido
  junto à instância competente**, não que atesta a conclusão. [Const. X; 010; DP-1901]
- **FR-063**: O escopo DEVE ser o de E3:
  - a CPAEG vê e decide tudo;
  - a CSAEG vê as declarações da unidade declarada do seu vínculo;
  - a CSAEG só vincula Conclusão, ou registra Referência de acervo, de unidade do seu
    vínculo.

  Fora do escopo, a recusa não revela o registro. [Hipótese; Const. XII; 010 FR-017]
- **FR-064**: Fila e tela de validação DEVEM mostrar:
  - nome, unidade, nível, curso e ano declarados;
  - momento;
  - Campanha;
  - situação (pendente ou em conflito).

  NÃO DEVEM mostrar Respostas, HMACs nem dado de Participação além de "concluída". CPF e
  data nunca aparecem na lista; na tela de uma declaração, só pela revelação de FR-076.
  [Const. XVI; 010 FR-033; 005/DP-505]
- **FR-065**: A tela de validação DEVE mostrar, a partir do **HMAC do CPF**:
  - como **candidatas**, as Conclusões das Pessoas importadas com o mesmo HMAC;
  - as **outras declarações com o mesmo CPF**, para que o operador perceba duplicidade.

  Nada disso é exibido ao declarante. Nada é escolhido automaticamente.
  [Solicitante; 018 FR-025]

#### Registro da validação

- **FR-070**: O registro DEVE ter um de dois resultados: "Formação confirmada" ou
  "Formação não confirmada". "Confirmada com dados diferentes" é divergência derivada
  (FR-077), não resultado. Antes de gravar, a tela DEVE pedir confirmação explícita e
  dizer o efeito. [Solicitante]
- **FR-071**: Toda decisão DEVE guardar:
  - o resultado;
  - a Conclusão vinculada, quando confirmada;
  - o momento;
  - o operador;
  - os fatos apurados na confirmação: se a Conclusão estava fora da abrangência da
    Campanha (FR-024) e se foi detectado conflito (FR-090).

  NÃO DEVE guardar texto livre. A evidência documental é DP-1904. [Const. IV; Hipótese]
- **FR-072**: Cada declaração DEVE ter no máximo uma decisão, imutável na 019 (E9;
  DP-1905). Uma decisão concorrente ou posterior recebe "já decidida", sem gravar.
  [Arquitetura]
- **FR-073**: "Formação confirmada" DEVE vincular a declaração a uma Conclusão Acadêmica
  obtida por uma de duas origens, e somente elas:
  - **(a) fonte digital**: uma candidata, uma Conclusão existente localizada pela
    referência na fonte, ou uma formação existente na fonte e ainda não importada,
    incorporada pelo caminho idempotente da 001;
  - **(b) acervo histórico**: pela Referência de acervo (FR-080 a FR-084).

  [Solicitante (M1+); 001 FR-030]
- **FR-074**: Referência inexistente, fonte indisponível, operador fora do escopo ou dado
  inválido DEVEM fazer o registro falhar sem gravar nada. A declaração continua pendente.
  [Arquitetura]
- **FR-076**: A tela de uma declaração DEVE oferecer a ação explícita "Mostrar dados para
  consulta ao acervo".
  - **Quem.** Só operador com a capacidade e no escopo (FR-063).
  - **O que mostra.** Nome, CPF e data de nascimento do declarante, descriptografados.
  - **Registro.** Cada revelação é registrada (FR-116).
  - **Onde não ficam.** Os valores não ficam na URL nem em cache.

  [Solicitante (decisão 10; E1 confirmada)]
- **FR-077**: A **divergência** entre a declaração e a Conclusão vinculada (unidade,
  nível, curso, ano) DEVE ser derivada e exibida como "confirmada com dados diferentes",
  com declarado e confirmado lado a lado. Ela não altera nem decide nada. [Solicitante;
  Const. III]

#### Fonte institucional de acervo histórico

- **FR-080**: DEVE existir uma fonte acadêmica institucional de **acervo histórico**,
  integrada pela mesma fronteira e pelo mesmo contrato das demais fontes (001).
  - **Origem.** Pessoa e Conclusão dessa fonte nascem **somente** pela incorporação
    idempotente da 001, com origem identificada.
  - **Tratamento.** Daí em diante, são tratadas como qualquer Conclusão.
  - **Sem cadastro manual.** Cadastro, edição ou exclusão manual de Pessoa ou Conclusão
    continuam vedados (001 FR-030).

  [Solicitante (M1+); Const. V]
- **FR-081**: O dado dessa fonte é a **Referência de acervo histórico**, registrada pelo
  operador com o resultado obtido no acervo. Ela contém:
  - a **referência** do registro no acervo (livro, folha, registro, processo), em texto
    não vazio, com forma definida em DP-1904;
  - **unidade, nível, curso e ano de conclusão**;
  - **modalidade, forma de oferta e data**, só quando o acervo informar, com a coerência
    ano × data da 001;
  - o **momento** e o **operador**.

  É imutável na 019 (DP-1905). [Solicitante; 001 FR-011]
- **FR-082**: A Referência de acervo é **dado institucional**. O formulário NÃO DEVE ser
  pré-preenchido com valores declarados, que aparecem ao lado só para leitura (E6).
  [Const. III]
- **FR-083**: A mesma referência na mesma unidade DEVE convergir para a mesma Conclusão. A
  mesma referência com valores diferentes DEVE ser recusada, sem gravar. [Arquitetura;
  001 FR-031, FR-033]
- **FR-084**: A fonte de acervo DEVE entregar cada Referência como uma pessoa com uma
  Conclusão. Ela NÃO DEVE associar nem fundir essa pessoa com Pessoa de outra fonte, mesmo
  com HMAC de CPF coincidente. A provável coincidência é sinalizada ao operador sem
  valores (DP-1909; 001/DP-003). [Hipótese (E5); Const. XI]

#### Conflito e concorrência

- **FR-090**: Na confirmação para a Conclusão X numa Campanha C, havendo outra Participação
  oficial com Conclusão efetiva X em C (institucional, em rascunho ou concluída, ou
  declarada validada):
  - a decisão DEVE registrar o **conflito detectado na validação**. Enquanto ele estiver
    pendente, sem resolução administrativa, a nova fica `DECLARADA_EM_CONFLITO`, fora dos
    dados oficiais;
  - a Participação que já era oficial NÃO DEVE mudar;
  - nada é fundido, excluído ou escolhido. A resolução é DP-1907. Quando existir, será um
    registro próprio, sem alterar a decisão;
  - a tela avisa antes do registro, sem exibir dados da outra Participação além da
    existência dela.

  [Solicitante; Hipótese (E4)]
- **FR-092**: Depois de uma `DECLARADA_VALIDADA` para X em C, iniciar Participação de X em
  C DEVE devolver a Participação declarada como já existente. A 007 a mostra à Pessoa de X
  como já respondida. [005 FR-013 estendido; 007]
- **FR-093**: A confirmação para X em C e o início institucional de X em C DEVEM ser
  serializados, de modo que nunca existam duas Participações oficiais com a mesma
  Conclusão efetiva na mesma Campanha. [Const. I; 005 FR-006 estendido]

#### Acompanhamento, snapshot e exportação

- **FR-100**: Os indicadores oficiais da 011 DEVEM considerar só Participações oficiais,
  com escopo e recortes pela Conclusão efetiva. [011; FR-051]
- **FR-101**: O detalhe da Campanha na 011 DEVE mostrar **um** indicador agregado, fora
  das taxas: "Validações de formação: N na fila".
  - **O que conta.** N é o número de itens da fila **desta Campanha** visíveis ao operador (FR-061, FR-063).
  - **Link.** Leva à fila, para quem tem a capacidade.
  - **Sem identificação.** Nenhum nome ou lista na 011.

  [Solicitante; 011 FR-080 a FR-084]
- **FR-102**: O universo do snapshot (012) DEVE ser a população elegível mais as
  Conclusões efetivas das Participações **oficiais**. A integridade (012 FR-053 d) vale
  para as oficiais. Pendências não aparecem no snapshot. [012 FR-030 a FR-034 revistos]
- **FR-103**: Um snapshot capturado antes de uma validação NÃO DEVE mudar em nenhuma
  leitura posterior. Uma captura posterior DEVE incluir a validada. [012 FR-050, FR-080]
- **FR-104**: Para garantir FR-103, cada registro do snapshot DEVE congelar **qual
  Participação** o compõe e a **origem da formação**. Snapshots existentes recebem esses
  valores de forma determinística: até a 019, toda Participação é institucional.
  [Arquitetura; Const. XXVII]
- **FR-106**: A exportação (013) DEVE incluir, por linha, a origem da formação, com três
  valores:
  - ancorada em Conclusão;
  - declarada, validada pela fonte digital;
  - declarada, validada pelo acervo.

  Ela NÃO DEVE conter valores declarados, nome, HMACs, CPF, data nem outros dados da
  validação. Nomes e tipos de coluna ficam no plan, assim como a leitura de 013 FR-021. A
  mudança gera nova versão do contrato (013 FR-065). [Solicitante; Const. III, IV, XVI,
  XVIII]

#### Privacidade e segurança

- **FR-110**: CPF e data NÃO DEVEM ser reexibidos depois de capturados na entrada da 018.
  - Não aparecem em telas posteriores da jornada nem da declaração. A única exceção é a
    reapresentação já prevista na própria entrada da 018, em "Conferir os dados" (018
    FR-033).
  - Não aparecem em logs, URLs, telemetria, mensagens de erro, acompanhamento,
    analytics, snapshots ou exportações.
  - Não aparecem em nenhuma tela de operador, **exceto** a revelação de FR-076.

  HMACs nunca são exibidos. O nome declarado não aparece em logs. [Solicitante (decisão
  10); Const. XVI; 018 FR-013]
- **FR-111**: Nome e dados da declaração são dado pessoal, visível só a quem tem a
  capacidade, no seu escopo (DP-1902, DP-1903). [Const. XVI]
- **FR-113**: Criar declarações DEVE estar sujeito à limitação geral por origem da 018.
  [018 FR-030]

#### Dados para consulta ao acervo

- **FR-114**: Os **dados para consulta ao acervo** DEVEM ser um conjunto próprio, separado
  da Formação Declarada e da decisão de validação.
  - **Conteúdo.** CPF e data de nascimento do declarante, com criptografia reversível em
    nível de aplicação.
  - **Ciclo de vida.** Nasce com a declaração (FR-016), existe antes de qualquer decisão
    e independe dela.
  - **Uso.** Serve só à consulta humana ao acervo.
  - **Sem cópia.** NÃO DEVE ser copiado para Pessoa, Conclusão, material de verificação,
    Resposta ou instrumento, nem depois da confirmação.

  [Solicitante (decisão 10); Const. XVI, III]
- **FR-115**: Duas chaves de criptografia, uma por finalidade:
  - uma para o **transporte transitório** de CPF e data entre a 018 e a criação da
    declaração (FR-002), com validade curta;
  - outra para os **dados persistidos** para consulta ao acervo.

  Cada chave DEVE:
  - ficar fora do banco e do repositório;
  - ser distinta da outra, das chaves da 018, da pseudonimização e do framework;
  - ser validada antes de qualquer uso.

  Chaves antigas da persistência DEVEM permanecer disponíveis até que todos os dados
  cifrados com elas tenham sido recifrados. A rotação é DP-1903.

  [Solicitante; 018 FR-011, FR-012]
- **FR-116**: Cada revelação (FR-076) DEVE gerar um registro de acesso com operador,
  declaração e momento, **sem** os valores. Esse registro não é exportado nem exibido na
  011. Consulta e retenção dele são DP-1903. [Solicitante (decisão 10); Const. IV, XVI]
- **FR-117**: Com qualquer das chaves de FR-115 ausente ou inválida:
  - **na declaração**: o caminho fica temporariamente indisponível, apresentado como
    indisponibilidade técnica (mensagem da 018), nunca como erro do egresso, e **nada** é
    gravado. Gravar CPF ou data em claro, ou a declaração sem os dados para consulta, NÃO
    DEVE ser alternativa;
  - **na validação**: só a revelação fica indisponível.

  [Solicitante; 018 FR-012]
- **FR-118**: Os dados para consulta ao acervo DEVEM poder ser descartados sem alterar
  declaração, decisão, Participação, Respostas, snapshots ou exportações.
  - **Quando.** Nada é descartado automaticamente na 019. A política é DP-1903.
  - **Depois do descarte.** A tela informa que os dados não estão mais disponíveis.

  [Solicitante; Const. XVI, XXVII]
- **FR-119**: Os dados para consulta ao acervo NÃO DEVEM ser usados em nenhuma comparação
  automática nem pela 018. Comparações usam só os HMACs (FR-014). [Arquitetura; Const.
  XV]

#### Acessibilidade e mobile

- **FR-120**: Declaração, lista de declarações e telas de validação DEVEM ter:
  - rótulos visíveis;
  - ordem lógica e foco visível;
  - erros junto ao campo, anunciados;
  - uso por teclado e leitor de tela.

  O ano usa teclado numérico. As listas de unidade e nível são utilizáveis no celular.
  [Const. XX; WCAG 2.1 AA; eMAG]
- **FR-121**: As telas do egresso DEVEM funcionar a partir de 320 px, sem rolagem
  horizontal, com a identidade visual da 015. [Const. XXI; 015]

#### Demonstração

- **FR-130**: A 019 DEVE funcionar só no modo de demonstração, com dados fictícios. Fora
  dele, nada responde. [008 FR-001; 018]
- **FR-131**: A barreira da demonstração DEVE admitir, além da fonte simulada, a fonte
  fictícia de acervo histórico. Qualquer outra origem continua impedindo a entrada.
  [018 FR-005]
- **FR-132**: Os cenários fictícios DEVEM cobrir:
  - par inexistente;
  - Pessoa sem data de nascimento (candidata por CPF);
  - formação na fonte ainda não importada;
  - formação só no acervo;
  - conflito com Participação institucional;
  - Campanha restrita com formação compatível e incompatível.

  Os operadores fictícios A (CPAEG) e B (CSAEG Vitória) exercem a fila; C é recusado. A
  preparação NÃO DEVE criar declarações nem validações. [001 FR-028; 010; Hipótese quanto
  à forma]

### Matriz mínima de verificação automatizada

| Situação | Resultado esperado | Requisitos |
| --- | --- | --- |
| `NAO_CONFIRMADA` × indisponível × formato inválido | "Informar minha formação" só na primeira | FR-001 |
| CPF inexistente × CPF existente com data errada | Caminho de declaração idêntico | FR-003 |
| Declaração com uma Campanha compatível | Declaração + Participação gravadas juntas; nenhuma Pessoa ou Conclusão criada | FR-005, FR-016 |
| Desistir antes de começar | Nada gravado | FR-016 |
| `NAO_CONFIRMADA` comum, sem declaração | Nenhum dado pessoal persistido, protegido ou não | FR-002 |
| Atualização, duplo clique ou reenvio do "Começar" | Uma declaração só; mesma Participação | FR-016 |
| Mesmo CPF com datas diferentes | Retomada só pelo par; agrupamento e candidatas pelo HMAC do CPF | FR-014, FR-043, FR-065 |
| Zero, uma e duas Campanhas compatíveis | Sem pesquisa / começar / ambiguidade | FR-022 |
| Campanha restrita: declarado compatível, incompatível e critério não coletado | Admite / recusa / admite | FR-021, E7 |
| Jornada declarada completa | Mesmo comportamento da 006/008; contexto "informada por você"; mensagem final | FR-032, FR-033 |
| Escrita após conclusão; fora da coleta | Rejeitada, como na 005/006 | FR-032 |
| Pessoa com mesmo CPF entra pela 018 com declaração pendente | Não vê "já respondida" | FR-036 |
| Retomada pelo mesmo par; outro par | Continua / nada visível | FR-042, FR-043 |
| Fila: CPAEG, CSAEG Vitória, operador sem vínculo | Tudo / só Vitória / recusa | FR-062, FR-063, FR-132 |
| Fila e telas de validação | Sem Respostas nem derivados; CPF e data só na revelação explícita | FR-064, FR-076, FR-110 |
| Rascunho declarado | Fora da fila | FR-061 |
| Candidata por CPF; colisão de CPF | Candidatas exibidas, nenhuma escolhida | FR-065 |
| Confirmar por candidata; por referência não importada; referência inexistente; fonte indisponível | Vínculo / incorporação + vínculo / nada gravado / nada gravado | FR-073, FR-074 |
| Confirmar pelo acervo | Referência gravada; Conclusão só pela incorporação; formulário não pré-preenchido | FR-080 a FR-082 |
| Mesma referência de acervo duas vezes; mesma referência com valores diferentes | Mesma Conclusão / recusa | FR-083 |
| CPF declarado coincide com Pessoa de outra fonte, validação por acervo | Sem fusão; sinalização sem valores | FR-084 |
| Não confirmada | Preservada; nunca oficial | FR-051 |
| Confirmada fora da abrangência | `DECLARADA_FORA_DA_ABRANGENCIA` | FR-024 |
| Conflito com institucional e com declarada validada | Nova fica em conflito; anterior intacta | FR-090 |
| Início institucional depois de declarada validada | Devolve a declarada; sem nova Participação | FR-092 |
| Confirmação e início institucional simultâneos | Nunca duas oficiais | FR-093 |
| Duas validações simultâneas | Uma grava; a outra "já decidida" | FR-072 |
| Validação nunca altera Participação, declaração ou Respostas | Verificado em todos os resultados | FR-015 |
| Divergência | Exibida lado a lado; nada alterado | FR-077 |
| Revelação dos dados para consulta: validador no escopo, fora do escopo, sem vínculo | Mostra CPF e data e registra o acesso / recusa / recusa | FR-076, FR-116 |
| Chave de criptografia ausente, curta ou igual a outra chave | Declaração indisponível e nada gravado; revelação indisponível | FR-115, FR-117 |
| Descarte simulado dos dados para consulta | Declaração, decisão, Participação, snapshots e exportações inalterados | FR-118 |
| Dados para consulta após confirmação | Nunca copiados para Pessoa ou material; 018 não os usa | FR-114, FR-119 |
| 011 oficial × indicador da fila × escopo | Pendências fora das taxas; indicador no escopo | FR-100, FR-101 |
| Snapshot antes e depois da validação | Anterior idêntico; posterior inclui | FR-102 a FR-104 |
| Snapshots pré-existentes | Preenchidos de forma determinística, sem mudança de leitura | FR-104 |
| Exportação | Origem da formação por linha; sem declarado, nome ou derivados; nova versão de contrato | FR-106 |
| Banco, logs, URLs, snapshots, exportações | Nenhum CPF ou data em claro | FR-014, FR-110, FR-114 |
| Testes existentes de 001 a 018 | Continuam passando; mudam só os ajustes de leitura previstos | Relação com outras features |

### Key Entities *(include if feature involves data)*

- **Formação Declarada** *(nova; dado declarado)*:
  - **Conteúdo.** Formação informada pelo egresso: nome, unidade, nível, curso e ano de
    conclusão, mais os derivados protegidos (HMAC) do par CPF + data e o momento.
  - **Imutabilidade.** Não muda depois do início.
  - **O que não é.** Não é Pessoa nem Conclusão, e não é Resposta: está fora do
    instrumento.
  - **Âncora.** Ancora exatamente uma Participação.
- **Participação em Pesquisa** *(005, revista)*:
  - **Âncora.** Uma Conclusão Acadêmica **ou** uma Formação Declarada, imutável.
  - **Resto.** Campanha, Versão, Respostas, início e conclusão como hoje.
  - **Situação analítica.** Derivada (FR-050).
- **Dados para consulta ao acervo** *(novo; dado pessoal protegido)*:
  - **Conteúdo.** CPF e data de nascimento do declarante, com criptografia reversível e
    chave externa.
  - **Cardinalidade.** Um por Formação Declarada, gravado com ela.
  - **Separação da decisão.** Existe antes de qualquer decisão e é separado dela.
  - **Acesso.** Só pela revelação explícita do validador autorizado.
  - **Descarte.** Descartável sem efeito sobre o resto.
  - **Separação.** Não pertence a Pessoa, Resposta nem instrumento.
- **Registro de acesso aos dados de consulta** *(novo; auditoria)*: operador, declaração e
  momento de cada revelação, sem valores.
- **Validação da formação** *(nova; registro administrativo)*:
  - **Conteúdo.** A decisão sobre uma Formação Declarada: confirmada (com a Conclusão
    vinculada) ou não confirmada, além de momento, operador e conflito, quando houver.
  - **Cardinalidade.** No máximo uma por declaração.
  - **Imutabilidade.** Imutável.
- **Referência de acervo histórico** *(nova; dado institucional da fonte de acervo)*:
  - **Conteúdo.** Referência ao registro no acervo, com unidade, nível, curso e ano;
    modalidade, forma de oferta e data quando houver; momento e operador.
  - **Uso.** É o dado da fonte acadêmica de acervo histórico, incorporado pela 001.
- **Fonte de acervo histórico** *(nova; adaptador da fronteira acadêmica)*: entrega as
  Referências de acervo pelo contrato comum. Cada referência é uma pessoa com uma
  Conclusão.
- **Pessoa e Conclusão Acadêmica** *(001, inalteradas)*: podem agora ter origem no acervo
  histórico, sempre pela incorporação.
- **Sessão do declarante** *(técnica, transitória)*: identifica só o par protegido. Não é
  entidade de domínio.
- **Situação analítica** *(derivada, não persistida)*: `INSTITUCIONAL`,
  `DECLARADA_PENDENTE`, `DECLARADA_NAO_CONFIRMADA`, `DECLARADA_FORA_DA_ABRANGENCIA`,
  `DECLARADA_EM_CONFLITO` e `DECLARADA_VALIDADA`.
- **Registro do snapshot** *(012, revisto)*: passa a congelar a Participação que o compõe
  e a origem da formação.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem | Fonte ou regra | Tratamento de divergência |
| --- | --- | --- | --- |
| Nome, unidade, nível, curso e ano da Formação Declarada | Declarado | Formulário de declaração | Preservado; nunca corrigido. Divergência com a Conclusão é derivada e exibida (FR-077) |
| HMAC do CPF do declarante | Derivado (técnico) | Chave de localização da 018 | Candidatas e agrupamento; nunca exportado |
| HMAC do par CPF + data | Derivado (técnico) | Chave de verificação da 018 | Só sessão e retomada; nunca chave de identidade ou deduplicação |
| CPF e data para consulta ao acervo | Informado pelo declarante; **não** é Resposta | Criptografia reversível com chave própria; revelação só ao validador autorizado | Nunca corrige a base; nunca copiado para Pessoa ou material |
| Registro de acesso aos dados de consulta | Registro de auditoria | Operador, declaração e momento de cada revelação | — |
| Respostas da Participação declarada | Declarado | Instrumento (mesma Versão) | Como na 005; nunca alteradas pela validação |
| Decisão de validação, momento, operador | Registro administrativo | Operador, com o resultado obtido junto à instância competente (DP-1901) | Imutável (DP-1905) |
| Referência de acervo e seus valores | Institucional | Acervo histórico, registrado pelo operador | Mesma referência com valores diferentes é recusada (FR-083) |
| Conclusão vinculada (fonte digital ou acervo) | Institucional | Fronteira acadêmica, incorporação da 001 | Como na 001 |
| Conclusão efetiva | Derivado | Âncora institucional ou Conclusão da validação | — |
| Situação analítica, compatibilidade provisória e definitiva, conflito | Derivado | FR-021, FR-024, FR-050, FR-090 | — |
| Candidatas | Derivado | Coincidência de identificador protegido do CPF | Nunca escolhidas automaticamente |
| Origem da formação na exportação | Derivado | Âncora e fonte da Conclusão vinculada | — |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um egresso que não confirmou o acesso consegue declarar a formação e começar
  a pesquisa em menos de 2 minutos, no celular, informando só os cinco campos.
- **SC-002**: Em 100% dos cenários fictícios, nenhuma declaração cria ou altera Pessoa,
  Conclusão ou material de verificação.
- **SC-003**: Em 100% dos cenários, Participações não oficiais ficam fora das contagens
  oficiais, dos snapshots e das exportações, e continuam preservadas.
- **SC-004**: Uma declaração validada passa a integrar o próximo snapshot e a exportação
  sem nenhuma ação do egresso. Um snapshot capturado antes da validação produz exatamente
  as mesmas linhas antes e depois dela.
- **SC-005**: Em nenhum cenário existem duas Participações oficiais com a mesma Conclusão
  efetiva na mesma Campanha.
- **SC-006**: O operador registra uma validação, por candidata, referência na fonte ou
  acervo, a partir da fila e numa única tela de decisão.
- **SC-007**: Uma busca pelos CPFs e datas fictícios no banco, nos logs da execução de
  testes, nas URLs, nos snapshots e nas exportações encontra **zero** ocorrências em claro.
  Eles só aparecem na revelação explícita ao validador autorizado.
- **SC-011**: Em 100% das revelações de dados para consulta ao acervo existe registro de
  acesso com operador, declaração e momento. Em 100% das tentativas de operador sem
  capacidade ou fora do escopo, nada é revelado.
- **SC-008**: CPF inexistente e CPF existente com data divergente produzem caminhos de
  declaração indistinguíveis em conteúdo e status.
- **SC-009**: Declaração, retomada, jornada e validação atendem WCAG 2.1 AA nas
  verificações automatizadas e manuais já usadas pela 015, a 320 px e no desktop.
- **SC-010**: Os testes existentes das features 001 a 018 continuam passando, salvo os
  ajustes previstos em "Impacto nas features anteriores".

## Assumptions

- A emenda constitucional (Constituição 2.0.0) está em vigor desde 2026-10-04.
- A 019 opera só no modo de demonstração, com dados fictícios. A ativação real depende de
  DP-1901 a DP-1903 e de 018/DP-1801 a DP-1803.
- A Campanha de demonstração continua aplicando a cópia da baseline 2024. Quem declara
  responde também Q10 a Q19, como quem tem Conclusão. A nova Versão do instrumento é
  trabalho da CPAEG, fora desta feature.
- O profiling da base real (018/DP-1804) dirá a proporção entre validação pela fonte
  digital e pelo acervo. Isso não altera esta spec.
- A sessão e a limitação de tentativas reusam os parâmetros configuráveis da 018.
- Rascunho declarado retomável pelo mesmo par CPF + data é o risco residual já aceito na
  018.

## Relação com outras features

- **018**: fornece `NAO_CONFIRMADA`, as chaves, a limitação e a sessão. A 019 acrescenta o
  caminho de declaração e o sujeito "declarante" sem alterar a verificação.
- **001**: fornece a fronteira e a incorporação. A 019 acrescenta a fonte de acervo
  histórico e o disparo de incorporação pela validação.
- **004**: fornece critérios e elegibilidade. A 019 usa a mesma semântica para a
  compatibilidade provisória (sobre o declarado) e definitiva (sobre a Conclusão).
- **005/006**: fornecem a jornada inteira, reusada sem regra nova.
- **007/008**: fornecem o modelo de situação de entrada e as telas. A 019 adapta posse e
  contexto.
- **010**: fornece papéis e escopo. A 019 acrescenta uma capacidade.
- **011**: ganha filtro de oficialidade e um indicador agregado da fila.
- **012/013**: ganham universo oficial, congelamento da Participação e origem da formação.
- **016/017**: inalteradas. O link neutro da 016 continua levando à entrada da 018.

### Impacto nas features anteriores (notas de revisão a aplicar com a 019)

- **Constituição**: Terminologia (Formação Declarada; Participação) e Princípio I,
  conforme o diff da auditoria §11. É pré-requisito.
- **001 FR-030**: o cadastro manual continua vedado. Fontes institucionais passam a
  incluir o acervo histórico, cujos dados são as Referências de acervo registradas na
  validação. O disparo da incorporação pela validação relaciona-se a DP-006.
- **004 FR-016, FR-017, FR-053**: população e elegibilidade continuam só sobre Conclusões.
  A admissão de Participação declarada usa a compatibilidade provisória (FR-021).
- **005 FR-002**: a âncora é "uma Conclusão Acadêmica **ou** uma Formação Declarada", e
  nunca é alterada.
- **005 FR-004**: a Pessoa da Participação declarada só existe pela Conclusão efetiva.
- **005 FR-006, FR-013**: unicidade e "já existente" valem pela Conclusão efetiva oficial
  (FR-092, FR-093).
- **005 FR-011**: o início declarado tem admissão própria (FR-020 a FR-022).
- **006 FR-035**: preserva Campanha e âncora.
- **007 FR-010**: a proibição de formação declarada continua dentro da entrada da Pessoa.
  A declaração é outra entrada.
- **007**: a Participação do par inclui a declarada validada.
- **008 FR-089, FR-090**: a posse passa a considerar o sujeito da sessão (Pessoa ou
  declarante).
- **010**: ganha a capacidade de validar formação.
- **011 FR-030 a FR-039**: os indicadores contam só Participações oficiais. O indicador
  da fila é novo (FR-101). FR-080 a FR-084 continuam valendo para a 011.
- **012 FR-030 a FR-034, FR-053, FR-071**: o universo é das oficiais e o registro congela
  a Participação e a origem (FR-102 a FR-104).
- **013 FR-010, FR-020, FR-026, FR-065**: ganha a coluna de origem da formação e nova
  versão do contrato (FR-106).
- **018 FR-034**: passa a oferecer a declaração, conforme FR-035. **018 FR-005**: a
  barreira admite a fonte fictícia de acervo (FR-131). **018 FR-040**: há um segundo
  sujeito de sessão.
- **ADR 0004**: a proposta sobre formação declarada vira regra, com compatibilidade
  provisória e definitiva.

## Invariantes Constitucionais Afetados *(mandatory)*

- **Terminologia e I — Longitudinalidade (NON-NEGOTIABLE), com emenda**:
  - toda Participação identifica sua âncora;
  - a cadeia Pessoa → Conclusão → Participação → Respostas vale integralmente para todo
    dado oficial (FR-051);
  - a âncora nunca muda (FR-030);
  - nenhuma Participação substitui outra, nem no conflito (FR-090).
- **II — Definição de egresso (NON-NEGOTIABLE)**: só Conclusão vinda de fonte
  institucional, digital ou acervo, faz a Participação oficial. A declaração nunca define
  egresso.
- **III — Institucional ≠ declarado (NON-NEGOTIABLE)**: a Formação Declarada é declarada e
  imutável. A Referência de acervo é institucional e não é pré-preenchida com o declarado.
  A divergência é explícita e nunca sobrescreve (FR-013, FR-077, FR-082).
- **IV — Proveniência**: origem da Conclusão (digital ou acervo), operador e momento da
  decisão, e origem da formação na exportação (FR-071, FR-081, FR-106).
- **V — Desacoplamento (NON-NEGOTIABLE)**: o acervo histórico entra como fonte pela mesma
  fronteira. O núcleo não conhece detalhes do acervo (FR-080).
- **VII — Pesquisa, Versão, Campanha, Participação (NON-NEGOTIABLE)**: mesma Versão, e
  Respostas sempre na Participação.
- **VIII — Preservação histórica (NON-NEGOTIABLE)**: nada é apagado, e snapshots
  anteriores não mudam (FR-051, FR-103).
- **X — Governança**: o operador registra o resultado obtido; não atesta. Sem workflow de
  aprovação (FR-061, FR-062).
- **XI — Identidade única**: nenhuma fusão. A coincidência entre fontes fica para a
  reconciliação (FR-084).
- **XII — Escopo por unidade**: fila e indicadores no escopo (FR-063, FR-101).
- **XIV — Fricção**: cinco campos e a mesma jornada (FR-010, FR-011).
- **XVI — Privacidade (NON-NEGOTIABLE)**:
  - nada em claro no banco;
  - HMAC para comparar e criptografia reversível só para a busca no acervo;
  - revelação explícita, restrita e registrada (FR-076, FR-114 a FR-119);
  - nenhuma Resposta para o operador;
  - fila nominal bloqueada para dados reais até DP-1902 (FR-014, FR-060, FR-064, FR-110).
- **XVIII — Exportabilidade**: origem preservada por linha (FR-106).
- **XX/XXI — Acessibilidade e mobile**: FR-120 e FR-121.
- **XXII — YAGNI**:
  - sem workflow nem estados intermediários;
  - sem texto livre;
  - sem contato;
  - sem cadastro manual de Conclusão.
- **XXVII — Migrações**: aditivas, com preenchimento determinístico dos snapshots
  existentes (FR-104).
- **XXIX — Hipóteses**: E1 a E9 marcadas, e as DPs explícitas.
- **Não afetados**: VI (ver Fronteira), IX, XIII (instrumento intacto), XV (mecanismo da
  018 intacto), XVII, XIX, XXIII. Pertinentes, mas sem impacto.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence ao acompanhamento?** Sim. Associar a resposta à formação correta é o núcleo
   longitudinal. Gestão do acervo acadêmico não pertence ao NIAE e não é criada: o NIAE
   guarda só a referência atestada necessária para incorporar.
2. **É necessária ao ciclo?** Sim. Sem ela, quem está fora da base digital não participa,
   e a representatividade cai (018, Assumptions).
3. **Há solução institucional mais adequada?** Para atestar, sim: o registro acadêmico
   (DP-1901). Para o acervo digitalizado, uma fonte institucional futura poderá substituir
   a Referência de acervo sem tocar o núcleo (DP-1911).
4. **Integração bastaria?** Não há hoje fonte digital do acervo histórico. A fonte de
   acervo é o adaptador mínimo até haver integração.
5. **Aumenta o acoplamento?** Não. O acervo entra pela fronteira acadêmica, e o núcleo
   continua recebendo Conclusões.

## Out of Scope *(mandatory)*

- Gov.br, SSO, OTP ou qualquer garantia de identidade adicional.
- Notificação ao egresso sobre o resultado; coleta de e-mail ou telefone; canal de
  atendimento (018/DP-1807).
- Reabertura, correção ou revogação de decisão ou de Referência de acervo (DP-1905).
- Resolução de conflito que troque a Participação oficial (DP-1907).
- Associação entre Pessoa do acervo e Pessoa de outra fonte (DP-1909; 001/DP-003).
- Material de acesso derivado da validação para entrar pela 018 na rodada seguinte
  (DP-1909).
- Cadastro, edição ou exclusão manual de Pessoa ou Conclusão.
- Anexos, evidências documentais, texto livre na decisão, workflow, atribuição, SLA ou
  prazo.
- Exibição de Respostas a operadores; exportação de declarações ou da fila.
- Nova Versão do instrumento; retirada de Q10 a Q19 da baseline.
- Lote, mobilização real e marcador de origem do acesso.
- Identificação produtiva de operadores (010/DP-1001).
- Registro de respostas por intermediário (005/DP-506).

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

### Herdadas, explicitamente preservadas

- **001/DP-003**: reconciliação entre fontes. Tratamento: nenhuma fusão; sinalização
  (FR-084).
- **001/DP-006, 018/DP-1805**: disparo e cadência de incorporação. Tratamento: a validação
  é um disparo explícito, sob demanda do operador.
- **001/DP-007, 010/DP-1005**: vocabulário de unidade e nível. Tratamento: listas com o
  vocabulário corrente (FR-012).
- **005/DP-505**: consulta de dados identificados. Ampliada por DP-1902.
- **005/DP-507, DP-508**: correção acadêmica e divergência declarado × institucional.
  Tratamento: divergência derivada e exibida, sem correção (FR-077).
- **018/DP-1801 a DP-1803**: risco, base legal e chaves. Continuam bloqueando o uso real.
- **018/DP-1806**: eventos de segurança. Aplica-se também à criação de declarações.
- **018/DP-1807**: canal para quem não confirma. A declaração atende o caminho; o canal
  humano continua pendente.

### Novas

- **DP-1901** — DECISÃO PENDENTE: instância com competência para atestar a conclusão e
  para fornecer a Referência de acervo (registro acadêmico, secretaria ou outra), e quem
  pode registrar o resultado no sistema. Instância competente: Proex/Proen/CPAEG, com o
  registro acadêmico. Impacto: FR-062, FR-063, FR-081. Tratamento provisório: CPAEG e
  CSAEG registram o resultado obtido, só com dados fictícios. **Bloqueia o uso real.**
- **DP-1902** — DECISÃO PENDENTE: quem pode ver os dados identificados dos declarantes,
  em qual escopo e com qual finalidade. Instância competente: encarregado de dados, com
  CPAEG/Proex. Impacto: FR-060, FR-064, FR-111. Tratamento provisório: capacidade restrita
  e só dados fictícios. **Bloqueia o uso real.**
- **DP-1903** — DECISÃO PENDENTE: base legal, finalidade, transparência ao declarante,
  retenção e descarte de:
  - nome declarado;
  - derivados protegidos;
  - **CPF e data criptografados**;
  - registros de acesso.

  Inclui o prazo de descarte depois da decisão e quem consulta os registros de acesso.
  Também custódia, geração e rotação da chave de criptografia, com a DTI, como na
  018/DP-1803. Instância competente: encarregado de dados, com DTI. Impacto: FR-010,
  FR-014, FR-111, FR-114 a FR-118. Tratamento provisório: só dados fictícios; nada é
  descartado; chave local de demonstração. **Bloqueia o uso real.**
- **DP-1904** — DECISÃO PENDENTE: evidência mínima para registrar uma confirmação, forma
  da referência de acervo. Instância competente: registro acadêmico, com CPAEG. Impacto:
  FR-071, FR-081. Tratamento provisório: referência em texto.
- **DP-1905** — DECISÃO PENDENTE: reabertura, correção ou revogação de decisão e de
  Referência de acervo, e o efeito sobre snapshots posteriores. Instância competente:
  CPAEG, com o registro acadêmico. Impacto: FR-072, FR-081. Tratamento provisório:
  imutáveis.
- **DP-1906** — DECISÃO PENDENTE: dados que o registro acadêmico precisa para localizar um
  egresso no acervo **além de nome, CPF e data** (nome à época, matrícula antiga,
  modalidade). Instância
  competente: registro acadêmico. Impacto: FR-010, FR-011. Tratamento provisório: os
  cinco campos de FR-010.
- **DP-1907** — DECISÃO PENDENTE: resolução de conflito, isto é, se e como uma
  Participação declarada validada pode prevalecer sobre a que já era oficial. Instância
  competente: CPAEG. Impacto: FR-090. Tratamento provisório: a anterior prevalece
  e a nova fica em conflito.
- **DP-1908** — DECISÃO PENDENTE: notificação ao egresso sobre o resultado da validação e
  o canal. Instância competente: Proex/CPAEG, com o encarregado. Impacto: FR-006.
  Tratamento provisório: nenhuma notificação.
- **DP-1909** — DECISÃO PENDENTE: associação da Pessoa da fonte de acervo a Pessoa de
  outra fonte, e se a validação pode habilitar o acesso pelo caminho principal da 018 na
  rodada seguinte. Instância competente: DTI e registro acadêmico, com o encarregado.
  Impacto: FR-084. Tratamento provisório: sem associação; a nova rodada exige nova
  declaração.
- **DP-1910** — DECISÃO PENDENTE: prazo e SLA da fila e destino das pendências ao fim da
  rodada. Instância competente: CPAEG. Impacto: FR-061. Tratamento provisório: nada
  expira.
- **DP-1911** — DECISÃO PENDENTE: substituição da Referência de acervo registrada no NIAE
  por fonte institucional digital do acervo, se houver digitalização. Instância
  competente: DTI e registro acadêmico. Impacto: FR-080. Tratamento provisório: a
  Referência de acervo é a fonte.
- **DP-1912** — **Decidida em 2026-10-04**: emenda MAJOR, Constituição 2.0.0, aplicada
  conforme o diff da auditoria §11. Mantida aqui só como registro.


## Nota de revisão pela Feature 023 (2026-10-05)

- **Selo vencido ou inválido:** volta à entrada com o aviso `?aviso=selo` ("Por segurança, confirme seus dados de novo para continuar."), em `/declaracao/`, `/declaracao/nova/` e `/declaracao/comecar/`.
- **Formulário:** o nome indica preenchimento automático de nome; o nível é escolhido por botões de opção. Opções e validações não mudam.
- **Confirmação:** mostra curso, unidade, nível e ano; "Começar" é a ação principal; "Corrigir" volta ao formulário preenchido, sem nova confirmação de CPF e data enquanto o selo valer.
- **Lista de formações informadas:** cada formação em andamento diz onde o declarante parou e o máximo que falta.
- **Envio pendente:** depois de estabelecer o declarante, um envio pendente de Participação fora das declarações do par é descartado.

Referência: [023 — Jornada de resposta com menos esforço](../023-jornada-menos-esforco/spec.md).
