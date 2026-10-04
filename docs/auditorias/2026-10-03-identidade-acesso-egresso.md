# Auditoria arquitetural — identidade e acesso do egresso

Data: 2026-10-03 · Base: `main` em `5e50fec` (PR #26 / ADR 0004). A Feature 017 foi lida
como contexto no worktree `spec-017-campaign-management`, onde ainda não está commitada.

Este documento é só diagnóstico, preparatório para a Feature 018. Nada foi implementado e
nenhuma spec foi escrita.

**Fontes lidas**: Constituição 1.0.0; specs 001, 004–008, 010, 016 e 017 (só o contexto);
ADR 0004; código em `academico`, `fonte_academica`, `participacao/entrada.py`,
`demonstracao`, `interface/views.py`, `comunicacao`, `governanca` e
`exportacao/pseudonimos.py`.

**Decisões preservadas**:

- identidade, formação e participação são conceitos separados;
- uma Pessoa pode ter múltiplas formações;
- o link de mobilização é neutro e nunca se vincula a uma formação;
- e-mail não vira identidade;
- Gov.br não é presumido;
- não se criam `FormacaoDeclarada` nem Lote;
- "identidade reconhecida, formação não localizada" precisa ser representável. O
  tratamento funcional desse caso fica para a feature seguinte.

---

## 1. Como `Pessoa` é identificada fisicamente hoje e quais invariantes existem sobre `fonte` e `id_externo`

**Identidade física.** `Pessoa.id` é um UUID v4 gerado pelo NIAE
([models.py:18](../../trajetoria/academico/models.py)). É a única identidade de domínio:
Participações, exportações e pseudônimos usam esse UUID
([dataset.py:277](../../trajetoria/exportacao/dataset.py)).

**Referência de origem embutida.** `fonte` e `id_externo` são colunas da própria `Pessoa`,
ambas `NOT NULL`. A decisão está em 001 research R6, que rejeitou uma tabela 1:N por
YAGNI e previu a migração aditiva "quando houver segunda fonte".

**Invariantes que existem hoje**:

| Invariante | Onde é garantido |
|---|---|
| No máximo uma Pessoa por `(fonte, id_externo)` | `UNIQUE pessoa_origem_unica` ([models.py:30](../../trajetoria/academico/models.py)) e `get_or_create` ([incorporacao.py:100](../../trajetoria/academico/incorporacao.py)) |
| `fonte` e `id_externo` não vazios; `nome` nulo ou não vazio | `CHECK` |
| Exatamente uma referência de origem por Pessoa | Estrutural: há um único par de colunas |
| Pessoa sem conclusão elegível não é criada (FR-039, **[Escopo]**, não constitucional) | Só na incorporação ([incorporacao.py:88](../../trajetoria/academico/incorporacao.py)), não no banco |
| Nada é atualizado nem removido por nova leitura; divergência só é registrada em log | `_comparar`, `_pessoa_inexistente` |
| Conclusão tem seu próprio `(fonte, id_externo)` único e nunca muda de Pessoa | `conclusao_origem_unica`; `CONCLUSAO_DE_OUTRA_PESSOA` |
| `nome` não identifica, não deduplica e não reconcilia | FR-005; nenhuma consulta usa `nome` como chave |
| Não há CPF, e-mail, data de nascimento nem matrícula na Pessoa | FR-005, FR-028; 016 FR-011 |
| Nenhuma resolução entre fontes diferentes | FR-034 |

**Como alguém é "identificado" hoje.** Só pelo `pk`:

- o adaptador de demonstração grava o `pk` num cookie assinado
  ([demonstracao/entrada.py:46](../../trajetoria/demonstracao/entrada.py)) e revalida que
  a Pessoa vem da fonte `simulada`;
- o contrato da fonte só sabe `obter_pessoa(id_externo)`
  ([contrato.py:106](../../trajetoria/fonte_academica/contrato.py)). Não há operação de
  localizar a partir de qualquer outro atributo.

## 2. O modelo atual suporta uma mesma Pessoa com identificadores de fontes diferentes?

**Não.** A lacuna tem três partes.

1. **Estrutural.** A Pessoa guarda uma única referência. Não há onde registrar uma segunda
   referência, por exemplo `("qacademico", X)` além de `("simulada", Y)`. FR-006 diz "não
   impedir no futuro"; isso só se cumpre pela migração prevista em R6.
2. **Comportamental.** `incorporar_pessoa(fonte_B, id_B)` procura a Pessoa por
   `(fonte_B, id_B)`. Se o mesmo indivíduo já existe como `(fonte_A, id_A)`, nasce uma
   **segunda Pessoa**. Nada no fluxo associa as duas, e FR-034 proíbe associar.
3. **Contrato.** Não existe forma de perguntar à fonte "quem é a pessoa com o atributo
   verificado Z?". Sem isso, uma identidade externa não chega a uma `Pessoa`.

Uma assimetria latente: nada liga `Conclusao.fonte` a `Pessoa.fonte`. O banco aceitaria
conclusões de fontes distintas sob a mesma Pessoa. Só o caminho de incorporação impede.

**Risco anterior à autenticação.** Se a fonte real identificar o indivíduo **por
matrícula** e não por pessoa, a deduplicação por `(fonte, id_externo)` já cria várias
Pessoas para o mesmo ser humano dentro de uma única fonte. Isso reabre DP-002 e DP-003 e
é a primeira pergunta do Portão A (item 11).

## 3. Como introduzir identidade externa sem criar segunda `Pessoa`

Princípio: **o provedor de identidade nunca cria Pessoa.** Ele produz uma afirmação
verificada, e a Pessoa é encontrada **através da fonte acadêmica**, que já é a autoridade
sobre quem existe no NIAE.

```text
Provedor de identidade (externo, substituível)       Núcleo NIAE
  autentica → Afirmação verificada  ───────────────►  Resolvedor de acesso
              {provedor, chave de resolução,             │ 1. fonte.localizar(chave) → 0..N id_externo
               nível de garantia}                        │ 2. N = 1 → incorporar_pessoa(fonte, id) (idempotente)
                                                         │ 3. Pessoa por (fonte, id_externo) — a mesma de sempre
                                                         ▼
                                              Resultado tipado → sessão guarda só Pessoa.id
```

**Fluxo:**

1. A **chave de resolução** é o atributo comum entre o provedor de identidade e a fonte
   acadêmica, por exemplo CPF, login institucional ou matrícula. Qual chave existe é
   evidência do Portão A. O núcleo a trata como opaca, com um tipo.
2. O contrato `FonteAcademica` ganha uma operação de localização que devolve **0..N**
   referências. Com N > 1, o resultado é ambiguidade e nunca há escolha automática
   (FR-034, DP-003).
3. A Pessoa resolvida é a mesma `Pessoa` indexada por `(fonte, id_externo)`. Se ainda não
   foi incorporada, a incorporação sob demanda reutiliza `incorporar_pessoa`, que é
   idempotente e protegida contra corrida. O resultado continua sendo uma única Pessoa.
4. Nesse desenho **nada novo é persistido na Pessoa** e não há segunda Pessoa possível: o
   sujeito do provedor nunca vira chave de criação.

**Quando o desenho deixa de bastar.** Isso acontece se não houver chave de resolução
comum, ou se a feature seguinte criar uma Pessoa a partir da identidade, sem registro
acadêmico. Nos dois casos é preciso persistir uma referência **não acadêmica**. Mais
tarde, quando a formação for validada e o registro acadêmico aparecer, essa referência
precisa ser **associada à Pessoa existente** em vez de gerar outra. Para isso são
necessárias referências 1:N (a migração R6) e uma regra de associação, que é
reconciliação (DP-003). Esse é o custo real e pertence à feature seguinte, não à 018.

## 4. O que deve ser identidade e o que deve ser apenas contato

| Categoria | O que é | Uso permitido | Uso vedado |
|---|---|---|---|
| **Identidade de domínio** | `Pessoa.id` (UUID) | Única chave interna; pseudônimos | Exposição ao egresso ou na URL |
| **Referência de origem** | `(fonte acadêmica, id_externo)` | Proveniência e idempotência da incorporação | Ser interpretada; servir de chave entre fontes |
| **Chave de resolução** | Atributo verificado pelo provedor e presente na fonte (p. ex. CPF) | Localizar a referência de origem no momento do acesso | Ser gravada na Pessoa por conveniência; deduplicar sem regra (DP-003) |
| **Credencial ou sessão** | Prova de autenticação; sessão com `Pessoa.id` | Autorizar a requisição | Conter formação, Campanha ou Participação |
| **Contato** | E-mail, telefone, WhatsApp | Alcançar a pessoa (fronteira de contato da 016, FR-011) | Identificar, deduplicar, autorizar ou ser campo da Pessoa |
| **Apresentação** | `nome` | Saudação e distinção visual | Identidade de qualquer tipo |

Contato é **mutável, múltiplo, compartilhável e de outra fronteira**. Identidade é
**estável e verificada**. Um mesmo valor (um e-mail) pode aparecer nas duas funções, mas
cumpre papéis diferentes. Quando o e-mail é canal de OTP, ele entrega uma credencial e
continua não sendo identidade. Ver a questão 5.

## 5. E-mail deve ser identificador estável?

**Não.** Isso já decorre do código e das specs (001 FR-005, 010 FR-007, 016 FR-011). Os
riscos concretos:

- **Instabilidade longitudinal.** O acompanhamento dura décadas (Princípio I); e-mails
  mudam, provedores encerram e contas ficam abandonadas.
- **E-mail institucional desativado ou reciclado** depois da formatura. O próximo dono do
  endereço herda o acesso.
- **Compartilhamento.** Familiares com o mesmo e-mail viram duas Pessoas com uma chave só,
  e a pressão para "fundir por e-mail" viola FR-034.
- **Multiplicidade.** Uma pessoa tem vários e-mails ao longo da vida. A mesma Pessoa
  apareceria como várias.
- **Qualidade da fonte.** E-mails legados com erro de digitação, ausentes ou
  desatualizados (DP-1601). Normalização ambígua (maiúsculas, `+`, pontos).
- **Tomada de conta** de domínio ou caixa abandonada, com acesso a rascunho de respostas
  sensíveis (Q2, Q4–Q6; DP-504).
- **Minimização.** Gravar e-mail na Pessoa cria dado pessoal sem consumidor de identidade
  (Princípio XVI).

**Uso admissível, se o Portão A o escolher**: canal de OTP. Mesmo assim, o endereço viria
da fonte institucional de contato, nunca digitado pelo egresso e aceito como verdade. O
OTP prova o **controle atual da caixa** associada pela instituição a uma referência de
origem, e não a identidade. Isso tem nível de garantia menor e precisa de decisão de
proporcionalidade (Princípio XV).

## 6. Opções de autenticação compatíveis com o desenho

Todas cabem atrás da mesma fronteira, porque o núcleo recebe só uma afirmação verificada.
A diferença entre elas é **qual chave de resolução cada uma produz** e **quem fica de
fora**.

| Opção | Chave que produz | Garantia | Quem fica de fora | Evidência necessária (Portão A) |
|---|---|---|---|---|
| **Gov.br** | CPF verificado (nome e e-mail como atributos) | Alta, com níveis bronze, prata e ouro | Quem não tem conta Gov.br; registros acadêmicos sem CPF | Adesão do Ifes ao Login Único; cobertura de CPF na fonte por coorte; base legal para tratar CPF |
| **SSO institucional** | Login ou matrícula | Média ou alta | Egressos com conta desativada após a formatura; egressos anteriores ao SSO | Política de retenção de contas de egressos; o login aparece na fonte acadêmica? |
| **OTP por e-mail** | Nenhuma: prova a caixa de uma referência já conhecida | Baixa ou média | Quem não tem e-mail na fonte ou o tem desatualizado | Origem e qualidade dos contatos (DP-1601); proporcionalidade ao risco |
| OTP por SMS | Idem, com telefone | Baixa ou média | Idem, mais custo | Idem |
| Conhecimento (matrícula + nascimento) | Atributos da fonte | **Baixa**, enumerável | Quem não lembra a matrícula (Princípio XIV) | Não recomendado |
| Link mágico no convite | — | — | — | **Incompatível** com o link neutro (016 FR-021/022) |

Pode haver **composição**: um mecanismo forte como padrão e outro como alternativa. Por
isso a afirmação precisa carregar o provedor e o nível de garantia. Esta auditoria
**não escolhe** mecanismo. A observação "provavelmente Gov.br" do roadmap continua
hipótese sem evidência.

## 7. Acesso espontâneo, sem convite

1. O egresso chega à entrada permanente. A URL e a relação com o Portal do Egresso ficam em
   004/DP-406.
2. Autentica-se no provedor. Antes disso, nenhuma resposta revela se alguém é egresso
   (anti-enumeração).
3. O resolvedor devolve exatamente um destes resultados: **Pessoa resolvida**,
   **identidade sem formação localizada**, **identidade ambígua**, **fonte indisponível**
   (nunca tratada como "sem formação"; o padrão já existe em `FonteAcademicaIndisponivel`)
   ou **não autenticado**.
4. Com a Pessoa resolvida, a sessão guarda **só `Pessoa.id`**. O resto já existe:
   `situacao_de_entrada(pessoa)` e `entrar(pessoa, formacao)` da 007
   ([entrada.py:208](../../trajetoria/participacao/entrada.py)). Basta trocar
   `pessoa_em_uso` ([views.py:73](../../trajetoria/interface/views.py)), o ponto de
   substituição previsto em 008 FR-005.
5. A admissão continua sendo só a da 004/005: EM COLETA e na abrangência (ADR 0004). Ter
   sido convidado não muda nada (004 FR-048).

## 8. Acesso originado de comunicação futura

- **Mesma entrada, mesmo fluxo** do acesso espontâneo. A mensagem leva a URL neutra, sem
  token, Pessoa, Conclusão, Campanha ou Lote (016 FR-021/022; ADR 0004).
- **A mensagem nunca carrega credencial.** Se o Portão A escolher OTP ou link mágico, o
  código é pedido **na entrada**, por ação do egresso, e não embutido no convite. Isso
  mantém o convite neutro, reduz a superfície de phishing e não transforma encaminhamento
  de e-mail em acesso.
- O futuro Lote registra quem foi abordado e **não participa** da resolução de identidade
  nem da admissão. Medir de onde veio o acesso (por exemplo, um marcador de Lote não
  identificante) é decisão da feature de mobilização. A 018 não a toma.

## 9. O link pode identificar a Pessoa sem selecionar formação? Múltiplas `ConclusaoAcademica`

O link **não identifica nada**. Quem identifica é a autenticação. Mesmo depois dela, o que
se resolve é **a Pessoa, nunca a formação**. O desenho está confirmado pelo código:

- **Uma Pessoa, N Conclusões.** `situacao_de_entrada` lista todas, cada uma com a sua
  situação (007 FR-017).
- **Escolha da formação.** Exatamente uma pendente resulta em `ENTRADA_RESOLVIDA`. Mais de
  uma resulta em `SELECAO_NECESSARIA`, e o egresso escolhe a formação, nunca a Campanha.
- **Ambiguidade de Campanhas.** Fica local à formação e não é desempatada (DP-404/701).
- **Participação.** Uma por par (Campanha, Conclusão) (`participacao_par_unico`; DP-501
  em aberto).
- **Posse da formação.** É verificada a cada ação (`FormacaoDeOutraPessoa`), de forma
  indistinguível para alheia ou inexistente.

A sessão **não guarda formação**. Escolher outra formação é só outra ação sobre a mesma
Pessoa.

## 10. Identidade resolvida, mas nenhuma formação institucional encontrada

Há **quatro casos distintos**. A 018 precisa distingui-los internamente sem prometer
tratamento:

| Caso | Origem | Representação proposta na 018 |
|---|---|---|
| a) Chave não encontrada na fonte | Nunca estudou; legado não digitalizado; registro sem a chave | Resultado do resolvedor `IDENTIDADE_SEM_FORMACAO`, **sem persistir** |
| b) Pessoa encontrada, mas sem conclusão reconhecida | Matrícula ativa, evasão (cenários F1 e F3) | Idem: `incorporar_pessoa` já devolve `SEM_CONCLUSAO_ELEGIVEL` sem criar a Pessoa (FR-039) |
| c) Várias referências na fonte para a chave | Duplicidade legada | `IDENTIDADE_AMBIGUA`: nunca escolhe e nunca funde |
| d) Pessoa com formações, mas falta uma | Registro incompleto | Já representável: a Pessoa resolvida segue para a 007. A entrada **não pode afirmar que a lista é completa** |

**Nos casos a e b, na 018:**

- tela honesta, sem formação inventada;
- nenhuma Participação e nenhuma gravação;
- sem revelar detalhe do registro acadêmico. Se a mensagem pode dizer "há matrícula sem
  conclusão" é decisão pendente;
- sem caminho funcional de declaração, que fica para a feature seguinte.

**Ponte já existente.** A 007 tem `ResolucaoDaEntrada.SEM_FORMACAO` para "Pessoa
registrada sem Conclusões" ([entrada.py:77](../../trajetoria/participacao/entrada.py)).
Hoje esse estado é inalcançável por causa de FR-039. Quando a feature seguinte revisar
FR-039 e persistir uma Pessoa sem conclusão, ele passa a valer sem tocar a 007.

## 11. Decisões que precisam vir do Portão A antes da spec

**Bloqueiam a forma do contrato (antes da spec):**

1. **Identificador de pessoa na fonte real** (DP-002). A fonte tem chave por pessoa ou por
   matrícula? É estável ao longo do tempo?
2. **Chave de resolução comum.** A fonte tem CPF ou login, e com qual cobertura por coorte,
   incluindo egressos antigos? Pode ser consultada por essa chave sob demanda ou só em
   lote (DP-006)?
3. **Mecanismo disponível.** Qual é a situação de adesão do Ifes ao Gov.br? Contas de SSO
   sobrevivem à formatura? Quem opera e com quais credenciais (DTI)?

**Bloqueiam o uso real (podem ficar como DECISÃO PENDENTE na spec):**

4. **Nível de garantia exigido** e proporcionalidade ao risco (Princípio XV), decidido
   pelo encarregado com a CPAEG.
5. **Base legal** para tratar CPF ou e-mail na identificação (DP-009, DP-1603).
6. **Origem e qualidade dos contatos** (DP-1601), só se OTP for considerado.
7. **Relação com o Portal do Egresso**: se o Portal tiver login próprio, o NIAE consome a
   identidade dele, e a 018 vira só um adaptador (pendência da Constituição; DP-406).
8. **Política de duplicidade legada**: o que fazer com o resultado `IDENTIDADE_AMBIGUA`
   (DP-003, DP-005).
9. **Sessão**: duração, encerramento e uso em dispositivo compartilhado.
10. **Acessibilidade** do mecanismo escolhido (eMAG, WCAG 2.1 AA).

Os itens 1 e 2 decidem se o desenho da questão 3 basta (resolução transitória, sem modelo
novo) ou se a 018 precisa persistir uma associação. **O item 1 também pode revelar
duplicidade de Pessoas já na incorporação**, independentemente da autenticação.

## 12. Alterar `Pessoa`, criar entidade de identificadores externos ou manter a autenticação fora do núcleo?

**Recomendação: manter a autenticação fora do núcleo e não alterar o modelo na 018.**

- **Fronteira externa.** Autenticação e gestão de identidade são externas (Princípio VI;
  Fronteira do Domínio). O núcleo não pode depender de mecanismo específico (V, XV) nem
  construir "sistema de identidade" (XXII). A 018 entrega uma fronteira substituível:
  provedor simulado mais adaptador real futuro.
- **O que muda no núcleo:**
  - a operação de localização no contrato `FonteAcademica`, também implementada pela
    `FonteSimulada` com chaves fictícias;
  - o resolvedor de acesso;
  - a sessão com `Pessoa.id`.
- **Sem tabela de identificadores externos na 018.** Ela não tem consumidor enquanto a
  resolução for transitória. Gravar o sujeito do provedor seria dado pessoal sem
  finalidade (XVI) e estrutura especulativa (XXII).
- **Quando a tabela se torna necessária.** Será na feature seguinte, se ela persistir
  Pessoa a partir da identidade (sem registro acadêmico), ou na 018, se os itens 1 e 2 do
  Portão A mostrarem que não há chave comum. Aí entra a migração R6, aditiva:
  `ReferenciaDeOrigem(pessoa, fonte, id_externo)` 1:N com `UNIQUE (fonte, id_externo)`,
  tornando a referência de origem um conceito explícito (já nomeado na 001). O custo é
  pequeno: além de `incorporacao.py`, só
  [contatos.py](../../trajetoria/comunicacao/contatos.py),
  [seguranca.py](../../trajetoria/comunicacao/seguranca.py),
  [demonstracao/entrada.py](../../trajetoria/demonstracao/entrada.py),
  [cenario.py](../../trajetoria/demonstracao/cenario.py) e
  [comunicacao/consultas.py](../../trajetoria/comunicacao/consultas.py) leem
  `Pessoa.fonte`/`id_externo` (cerca de 13 arquivos de teste).

---

## Proposta de fronteira da Feature 018 — Identidade e acesso do egresso

**Problema**: hoje a Pessoa chega à jornada por um seletor fictício. A 018 define **como
um egresso real chega a ser "a Pessoa resolvida"** que a 007 e a 008 já esperam, sem
escolher o mecanismo antes da evidência.

**Dentro do escopo**

1. **Fronteira de identidade do egresso.** Contrato que devolve uma afirmação verificada
   (provedor, chave de resolução opaca com tipo, nível de garantia) ou uma falha. É
   separada da identificação de operadores (DP-1001; 010 FR-008).
2. **Provedor de identidade simulado**, com identidades fictícias e chaves fictícias.
   Substitui o seletor da 008 como adaptador de demonstração, só no modo de demonstração.
3. **Operação de localização no contrato `FonteAcademica`** (0..N) e sua implementação na
   `FonteSimulada`. Os cenários incluem: chave sem registro; chave com registro sem
   conclusão; duas referências para a mesma chave; fonte indisponível; Pessoa ainda não
   incorporada.
4. **Resolvedor de acesso** com resultados tipados: Pessoa resolvida, identidade sem
   formação localizada, identidade ambígua, fonte indisponível e não autenticado. Usa
   incorporação sob demanda por `incorporar_pessoa` (hipótese reversível para DP-006).
5. **Sessão do egresso** com só `Pessoa.id`. Estabelecer, encerrar e revalidar a cada
   requisição. Substitui `pessoa_em_uso` sem tocar a 005, a 006, a 007 nem as telas da
   jornada.
6. **Entrada única** para acesso espontâneo e acesso vindo de mensagem. O link da 016
   continua neutro e passa a apontar para ela.
7. **Telas de estado** para cada resultado, acessíveis e mobile-first, com
   anti-enumeração antes da autenticação. "Identidade sem formação" é informativa e não
   grava nada.

**Fora do escopo**

- Adaptador real (Gov.br, SSO ou OTP) até haver evidência do Portão A.
- `FormacaoDeclarada`, validação, revisão de FR-039, Pessoa sem conclusão persistida e
  Participação sem Conclusão.
- Lote, mobilização real, histórico de disparos e marcador de origem do acesso.
- Tabela `ReferenciaDeOrigem`, salvo se o Portão A (itens 1 e 2) a exigir.
- Reconciliação entre fontes (DP-003) e fusão de Pessoas.
- Identificação produtiva de operadores (DP-1001).
- Conta, senha, perfil, atualização de contato pelo egresso, "Minha Trajetória" e
  consulta das próprias respostas (DP-802).
- CPF ou e-mail persistidos na Pessoa.

**Decisões já possíveis, sem o Portão A**

- D1. O provedor de identidade nunca cria Pessoa. A Pessoa é sempre localizada pela fonte
  acadêmica e incorporada pelo caminho idempotente existente.
- D2. E-mail nunca é chave de identidade nem critério de deduplicação. No máximo é canal de
  credencial, vindo da fronteira institucional de contato.
- D3. A sessão carrega só a Pessoa, nunca formação, Campanha ou Participação. A formação é
  sempre escolhida pela 007.
- D4. A mensagem de mobilização nunca carrega identidade nem credencial. A entrada é a
  mesma para acesso espontâneo e por convite, com a mesma admissão.
- D5. Com mais de uma referência para a mesma chave, não há escolha nem fusão: o resultado
  é ambiguidade explícita.
- D6. "Fonte indisponível" nunca vira "sem formação".
- D7. "Identidade sem formação" é resultado de primeira classe, distinto de "sem
  pesquisa" (007), e não persiste nada na 018.
- D8. Identidade do egresso e identidade do operador são fronteiras distintas, mesmo que
  o futuro provedor seja o mesmo. Ser egresso não confere capacidade (010 FR-008).

**Dependências do Portão A**: itens 1 a 3 antes da spec, porque definem a forma do
contrato; itens 4 a 10 como DECISÃO PENDENTE, porque bloqueiam o uso real.

**Riscos de alteração constitucional ou de modelo**

| Risco | Onde | Natureza |
|---|---|---|
| Fonte real identifica por matrícula, gerando várias Pessoas por indivíduo | 001 FR-031, DP-002/003 | Modelo e dados; anterior à 018 |
| Sem chave comum entre provedor e fonte | Questão 3 | Modelo: a migração R6 e a associação persistida entram na 018; *Complexity Tracking* |
| Persistir sujeito do provedor no NIAE | VI, XV, XXII | Exige justificativa no plan; não exige emenda |
| OTP por e-mail | XVI; 016 FR-011 | O contato fica na fronteira de contato; não exige emenda |
| Feature seguinte (`FormacaoDeclarada`) | Terminologia "Participação = acompanhamento de **Conclusão Acadêmica**"; Princípio I (cadeia); II (Conclusão elegível ≡ egresso); FK `Participacao.conclusao NOT NULL` | **Provável emenda constitucional** (MINOR ou MAJOR) e mudança de modelo. A 018 não pode impedir isso nem antecipá-lo |
| Revisão de FR-039 | 001 | **[Escopo]**: revisável por spec, sem emenda |
| Cookie assinado sem expiração nem revogação | `demonstracao/entrada.py` | Aceitável só na demonstração; a sessão real é requisito da 018 |

**Conclusão**: a 018 cabe **sem emenda e sem mudança de modelo**, desde que o Portão A
confirme a existência de chave de resolução comum e de identificador por pessoa na fonte.
Se não confirmar, a migração R6 entra na 018, de forma aditiva e reversível, ainda sem
emenda. A pressão constitucional real está na feature seguinte, não nesta.

---

## Adendo de 2026-10-04 — decisão consolidada do solicitante

Depois desta auditoria, o solicitante simplificou a hipótese de identidade. Este adendo
registra a decisão e indica o que do texto acima continua válido e o que foi superado. A
spec correspondente é a
[018 — Identificação e acesso do egresso por dados acadêmicos](../../specs/018-identificacao-acesso-egresso/spec.md).

### Decisão

O mecanismo inicial é **CPF + data de nascimento provenientes da fonte acadêmica**,
conferidos contra material de verificação protegido por HMAC e importado com a Pessoa.

- **Natureza.** É **verificação de identidade por conhecimento**, não autenticação forte.
  CPF e data de nascimento não são segredos. A escolha é consciente e proporcional a uma
  pesquisa de egressos, e melhora o processo atual, que não tem verificação alguma.
- **Por que não Gov.br, SSO ou OTP agora.** Baixa fricção é requisito do produto. Gov.br,
  SSO e OTP ficam como evolução futura, caso a cobertura da base ou a avaliação de risco
  exijam garantia maior.
- **Profiling em paralelo.** O profiling da base real corre em paralelo e mede o volume do
  caminho excepcional. Não bloqueia a spec.

**Contrato de saída da verificação:**

```text
CONFIRMADA                  → Pessoa resolvida → sessão (só Pessoa.id) → jornada 007/008
NAO_CONFIRMADA              → mensagem genérica; "conferir os dados"; nada criado nem alterado;
                              ponto de saída para a 019 (declaração, quarentena, validação)
VERIFICACAO_INDISPONIVEL    → erro temporário; nunca tratado como NAO_CONFIRMADA
```

**Correção de nome.** A proposta usava "fonte indisponível". Como a verificação compara
com material **já importado**, a fonte acadêmica não é consultada no momento do acesso.
O caso temporário real é "verificação indisponível": configuração das chaves, falha
técnica ou limite de tentativas em vigor.

### O que continua válido desta auditoria

- **Questões 1, 2, 4, 5 e 9**, sem alteração.
- **D2.** E-mail nunca é identidade.
- **D3.** A sessão guarda só a Pessoa; a formação é escolhida na 007.
- **D4.** O link é neutro e a entrada é a mesma para acesso espontâneo e por convite.
- **D5**, agora como **colisão**: dois registros com o mesmo CPF não são escolhidos nem
  fundidos.
- **D7**, agora como `NAO_CONFIRMADA`: o caso não confirmado é de primeira classe e não
  grava nada na 018.
- **D8.** Identidade de egresso e de operador são separadas.
- **D1**, reformulada: a Pessoa vem sempre da fonte acadêmica. Agora o acesso compara com
  material importado, sem consultar a fonte no momento.
- **Riscos**: duplicidade por matrícula e pressão constitucional na 019.

### O que foi superado

- **A estrutura genérica de identidade.** Fronteira com afirmação verificada, provedor
  simulado, nível de garantia e localização na fonte com incorporação sob demanda. O ponto
  de substituição exigido pelo Princípio XV é a própria resolução de acesso, que entrega
  uma Pessoa à jornada. Não há estrutura de provedores.
- **A tabela da questão 6.** A opção "conhecimento" foi classificada como "não
  recomendada". Agora ela é adotada **conscientemente**, com controles proporcionais. O
  risco residual aceito é que alguém que conheça os dois dados possa abrir um rascunho ou
  responder primeiro.
- **"Sem modelo novo na 018".** A Pessoa ganha material de verificação protegido e
  anulável. Recomenda-se que esse material pertença à capacidade de acesso, de modo que
  possa ser removido ou substituído sem tocar Pessoa, Conclusão ou Participação.

### Regras do caminho não confirmado

Acordadas para a 019 e respeitadas pela 018:

1. **Classificação interna, nunca revelada.** "CPF conhecido com data divergente" e "CPF
   desconhecido" são distinguíveis internamente pelo identificador protegido. Para o
   egresso, a mensagem é sempre a mesma.
2. **Quarentena.** Uma declaração não confirmada nunca cria nem altera Pessoa, nunca
   mostra dado da base e nunca conta como "já respondida" para a Pessoa existente.
3. **Conferir antes.** "Conferir os dados" vem antes de qualquer caminho excepcional, para
   reduzir a fila causada por erro de digitação.
4. **Pessoa só na validação.** Criar ou associar a Pessoa acontece só na validação
   acadêmica. Onde a resposta "mora" até lá é a questão central da auditoria da 019.

### Controles proporcionais

- **Sem revelação nas respostas.** A mensagem é genérica e idêntica para as três causas de
  falha. O tempo de resposta também não deve distinguir CPF existente de inexistente.
- **Limitação de tentativas.** Por origem e por identificador protegido, com atraso
  progressivo e **sem bloqueio permanente**. Sem CAPTCHA, por acessibilidade e para não
  depender de terceiros.
- **Chaves.** Chaves HMAC distintas para localização e para verificação, fora do banco e
  distintas da chave de pseudonimização.
- **Sem vazamento.** CPF e data de nascimento nunca aparecem em log, URL, telemetria ou
  mensagem.
- **Sessão.** Com expiração e HTTPS na ativação produtiva.
- **Respostas.** Participação concluída mostra só que foi respondida e a data, o que já
  vale hoje para as respostas (008 US10, FR-023). O rascunho continua retomável: é o risco
  residual consciente.
