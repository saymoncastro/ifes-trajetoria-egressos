# Portal do Egresso × Trajetória Ifes — arquitetura de produto e roadmap

- **Data.** 2026-10-07. Base: `main` em `598ee32`, que inclui a Feature 023 e a reauditoria de
  esforço.
- **Natureza.** Análise de arquitetura de produto. **Não é spec.** Nenhum código foi alterado
  e nenhuma spec foi criada.
- **Revisão 1 (2026-10-07).** Incorpora a revisão do solicitante:
  - a divisão física em módulos fica como hipótese, a confirmar em cada spec;
  - as duas entidades novas são constatação do horizonte atual, não limite;
  - D3 decidida: Minha trajetória, card e vídeo abertos antes da pesquisa, por regra positiva;
  - D2 não bloqueia a S1;
  - checkpoint de validação logo após a S1, com critérios definidos antes;
  - S0 mínima.
- **Revisão 2 (2026-10-07).** A S0 foi executada:
  [ADR 0008](../adr/0008-portal-do-egresso-camada-de-relacionamento.md) e Constituição
  2.1.0. Ela incorpora uma decisão adicional do solicitante: **a coleta é independente do
  Portal.**
  - Campanhas continuam divulgando acesso direto ao instrumento.
  - O egresso responde sem passar pelo Início do Portal.
  - O caminho de entrada (instrumento ou Portal) é preservado depois da identificação.
  - A 024 verifica tudo isso por testes (seção 6, S1).
- **Entradas.**
  - O protótipo conceitual `portal_egresso.html`.
  - A Constituição 2.0.0.
  - As specs 001–023 e as ADRs 0001–0007.
  - As auditorias de `docs/auditorias/`.
  - O código em `trajetoria/`.
- **Pergunta a responder.** Dado o que já existe, qual é a sequência mínima e coerente de specs
  que leva do acompanhamento longitudinal a um Portal Integrado do Egresso, sem descartar o que
  existe e sem construir demais antes da hora?

---

## 0. Resposta curta

1. **O Portal não exige uma nova aplicação.**
   - **Decisão arquitetural.** Uma camada de **Portal/Relacionamento**, no mesmo projeto, banco
     e sessão, depende do núcleo do Trajetória Ifes (NIAE). O núcleo nunca depende dela, e ele
     não muda.
   - **Hipótese a confirmar nas specs.** A divisão física dessa camada em módulos Django.
2. **O primeiro passo foi uma decisão de fronteira, curta, e já está feita (S0).**
   - A Constituição 2.0.0 dizia que o Trajetória Ifes **não é** o Portal do Egresso e que a
     relação entre os dois "NÃO DEVE ser presumida" (DP-406; DP-2108).
   - O ADR 0008 e a emenda 2.1.0 admitem o Portal como hipótese em demonstração, sem adoção
     institucional.
   - Os dois também fixam que **a coleta funciona sem o Portal**: instrumento, Campanha e
     Participação são os mesmos por qualquer caminho de acesso.
3. **O código de hoje inverte a troca de valor que o Portal propõe.**
   - O login leva à lista de pesquisas (`/formacoes/`).
   - Minha trajetória só abre depois de uma Participação concluída
     (`narrativa/consultas.py:elegivel`).
   - **Decidido (D3):** na S1, a trajetória institucional passa a ser acessível por regra
     positiva, independentemente de pesquisa.
4. **Sequência.**
   - **S0** (decisão).
   - **S1** (Início e shell do Portal, sem modelo novo).
   - **Checkpoint 1** (modelo mental).
   - **S2** (Oportunidades) e **S3** (Volte ao Ifes).
   - **Checkpoint 2** (valor e reciprocidade).
   - **S4** (linha do tempo da relação), opcional.

   "Conte só o que mudou" e a comunidade agregada ficam fora da camada Portal: dependem de
   decisões institucionais já pendentes.
5. **Parte do mockup contradiz decisões já auditadas.** Por exemplo:
   - "geração 2008" e "72 conectados";
   - "cerca de 3 minutos";
   - uma atualização em 3 passos paralela ao instrumento;
   - mestrado e doutorado com ano na linha do tempo.

   A lista completa está na seção 3.3.

---

## 1. Leitura do estado atual

### 1.1 O que o sistema é hoje

O sistema é um monólito Django modular (Django 5.2, PostgreSQL 16) com cerca de 20 módulos de
domínio. **Ele só funciona em modo de demonstração:**

- sem `TRAJETORIA_DEMONSTRACAO=1`, toda página responde 404;
- a fonte acadêmica é simulada e as pessoas são fictícias;
- não há produção.

O uso real depende de três coisas:

- o Portão A (dados reais e decisões institucionais);
- o Gate B (envio real);
- a identificação de operadores (DP-1001).

| Camada | O que existe | Onde |
|---|---|---|
| Núcleo longitudinal | `Pessoa` → `ConclusaoAcademica` → `Participacao` → `Resposta`, com fonte e id externo, imutabilidade e múltiplas conclusões | `academico`, `participacao` |
| Instrumento | `Pesquisa` → `Versao` (rascunho/publicada, imutável) → `Secao` → `Pergunta` → `Opcao`; baseline 2024 migrada (54 perguntas) | `instrumento`, `formulario_2024`, `editor` |
| Coleta | `Campanha` (Versão, período, abrangência), população elegível, gestão mínima (abrir, editar, encerrar) | `campanha`, `acompanhamento/gestao` |
| Formação declarada | `FormacaoDeclarada` + `ValidacaoDaFormacao` + acervo cifrado; a Participação ancorada nela fica fora da análise oficial | `declaracao` |
| Acesso do egresso | CPF e data de nascimento conferidos por HMAC; sessão de 30 min de inatividade e 8 h no máximo; sem senha | `acesso` |
| Contato | `ContatoDaPessoa` imutável, com origem (fonte acadêmica × informado pelo egresso); só e-mail; página `/meu-email/` | `contato` |
| Mobilização | `LoteDeMobilizacao` congelado por Pessoa, envio retomável, Mailpit local; envio real desligado | `mobilizacao`, `comunicacao` |
| Devolutiva | Minha trajetória (narrativa derivada na consulta, sem persistir), card 9:16 em SVG/PNG e vídeo de ~8 s (Remotion); contrato serializável | `narrativa`, `contexto_trajetoria`, `video` |
| Operação | Acompanhamento agregado por Campanha, com escopo CPAEG/CSAEG; fila de validação de formações | `acompanhamento`, `declaracao`, `governanca` |
| Análise | Snapshot imutável de Campanha encerrada; exportação CSV/XLSX pseudonimizada (contrato GeN v2), sem tela | `analitico`, `exportacao` |
| Experiência | Um shell único (`interface/templates/interface/base.html`), mobile-first, tokens da 015, sem navegação; jornada reauditada após a 023 | `interface` |

### 1.2 O percurso do egresso, como está

```text
link neutro / URL ──► /acesso/ (CPF + data) ──► /formacoes/  ◄── "/" também redireciona para cá
                                                   │
                         ┌─────────────────────────┼──────────────────────────┐
                         ▼                         ▼                          ▼
              participação (seções)      "Ver minha trajetória"     (sem link para /meu-email/)
                         │                 (só se já concluiu)
                         ▼
                 concluída ──► /minha-trajetoria/ (card, vídeo) · /meu-email/ (convite)
```

Três fatos mostram que a experiência atual foi desenhada em torno da pesquisa:

- **O login leva à pesquisa.** O destino é `/formacoes/`, tanto em `acesso/views.py:54` quanto
  em `interface/views.py` (`inicio`).
- **A devolutiva é recompensa, não reconhecimento.** `narrativa/consultas.py:elegivel` exige
  Participação concluída ancorada em Conclusão Acadêmica. A 021 registrou isso como hipótese
  (E2).
- **O shell pertence ao app da pesquisa.** `narrativa` e `contato` estendem
  `interface/base.html`, cujo produto se chama "Trajetória Ifes — Acompanhamento de egressos".
  Não há navegação entre áreas, só links pontuais.

### 1.3 O que já está maduro e não deve ser tocado

- **Cadeia longitudinal, imutabilidade e versionamento** (Princípios I, VII e VIII).
- **Proveniência.**
  - Institucional × declarado × derivado (III).
  - Contato com origem.
  - Formação declarada em quarentena analítica.
- **Acesso sem senha e substituível** (XV). A sessão (`acesso.sessao.pessoa_em_uso`) não
  depende da pesquisa e serve a qualquer página.
- **Narrativa como contrato serializável** (021 FR-014). Outra renderização, inclusive um
  Portal externo, pode consumir a mesma narrativa.
- **Identidade visual, acessibilidade e esforço** (015, 021, 023), já auditados e medidos.

---

## 2. Domínio, capacidade e experiência

Uma entidade nova só se justifica quando existe um **fato persistente com regra própria**. Um
card no mockup não basta.

| Nível | Já existe | Novo e justificado no horizonte atual | Não deve virar entidade agora |
|---|---|---|---|
| **Domínio** | Pessoa, Conclusão Acadêmica, Formação Declarada, Pesquisa/Versão, Campanha, Participação, Resposta, Contato da Pessoa, vínculo de governança | **Oportunidade**: conteúdo institucional curado, com dono, período e público. **Manifestação de interesse**: ato da Pessoa, com finalidade e ciência registradas | "Perfil", "Trajetória" persistida, "Interesses", "Comunidade", "Conexão", "Evento", "Interação" genérica, "Usuário do portal" |
| **Capacidade** | identificar a Pessoa; resolver a entrada na pesquisa; coletar respostas; montar a narrativa; gerar card e vídeo; atualizar e-mail; mobilizar por Lote; agregar a coleta; exportar | apresentar oportunidades pertinentes **com explicação**; registrar e encaminhar uma manifestação | recomendar; casar egressos; notificar por vários canais; medir engajamento |
| **Experiência** | jornada da pesquisa; página Minha trajetória; página de e-mail | **Início** que reconhece antes de pedir; **shell com navegação**; páginas de Oportunidades e de Volte ao Ifes | comunidade com indicadores sociais; memória do campus; retrato em três estilos |

**Consequência.** O Portal é, em grande medida, **experiência**. No horizonte analisado aqui, os
únicos fatos persistentes novos justificados são **Oportunidade** e **Manifestação de
interesse**, ambos fora do núcleo do NIAE. Nenhuma entidade existente precisa ser
generalizada.

Isso é uma **constatação, não um limite arquitetural**. Uma necessidade real futura pode
revelar outro fato de domínio. Ele deve então ser justificado pela spec correspondente, como
qualquer entidade (Princípio XXII).

---

## 3. Gap analysis: Portal × sistema atual

Legenda:

- **A**: existe e pode ser reutilizado.
- **B**: existe parcialmente e precisa ser exposto ou generalizado.
- **C**: não existe e merece capacidade nova.
- **D**: só hipótese de experiência, sem mudança de domínio.
- **E**: postergar.

### 3.1 Conceitos

| Conceito | Classe | O que existe | O que falta | Risco de duplicação | Entidade nova? |
|---|---|---|---|---|---|
| Identidade da pessoa | **A** na demonstração, **B** em produção | `Pessoa` + `MaterialDeVerificacao`; sessão independente da pesquisa | Reentrada mais barata para um lugar ao qual se volta. Hoje: CPF e data a cada volta (~19 teclas, reauditoria §6) e sessão de 30 min. Depende de DP-1808 e do Portão A | "Conta do portal" ou cadastro com senha (proibido, XV) | Não |
| Múltiplas conclusões | **A** | `Pessoa.conclusoes`; narrativa por Pessoa (E2); próxima formação na confirmação (023) | Nada | Pôr campus ou curso na Pessoa, como faz o mockup ("Marina · Campus Vitória") | Não |
| Trajetória institucional | **A**, com exposição **B** | `TrajetoriaNarrativa` (021), card, vídeo | Acesso antes da pesquisa (decidido, D3), entrada pelo Início, legenda de proveniência | Uma segunda "linha do tempo" paralela à narrativa | Não |
| Dados institucionais | **A** | Contrato da fonte (001); complemento de ingresso e agregados (021 P2) | Nada | — | Não |
| Dados declarados na trajetória | **E** | `Resposta` existe, mas a 021 não a lê (FR-044) | Comparabilidade entre Versões (DP-2107 = 002/DP-006). O instrumento **não registra o ano** de mestrado ou doutorado: Q47 é caixa de seleção sem data | Inventar os marcos datados do mockup | Não |
| Campanhas | **A** | Gestão mínima (017), abrangência (ADR 0004) | Nada. O Portal só mostra "há uma pesquisa para você" | Transformar Campanha em "interação" genérica | Não |
| Instrumentos | **A** | Versão imutável, editor, baseline 2024 | Nada no Portal | O mini-formulário "Atualize" do mockup seria um **segundo instrumento** | Não |
| Participação | **A** | Resolução da entrada (`ResolucaoDaEntrada`), rascunho, conclusão | No Início, mostrar o estado que a resolução já calcula | — | Não |
| Atualização longitudinal | Mecanismo **A**; "só o que mudou" **C** | Nova Participação por Campanha; nada é sobrescrito | Reaproveitar e contextualizar é **decisão metodológica da CPAEG** (DP-307; EF-05 da auditoria de esforço), não da camada Portal | Atalho "3 passos" fora do instrumento | Não |
| Interesses | **E** | Nada no instrumento (conferido no inventário 2024) | Finalidade concreta. Sem consumidor, um perfil de interesses é dado sem uso (XVI) | "Perfil" que vira CRM | Não, por ora |
| Retrato da Trajetória | **A** | Card 9:16 (021) e vídeo (022) | Entrada pela navegação e acesso antes da pesquisa (D3). Os três estilos do mockup são **E**: a 021 limitou os temas a no máximo dois | Novo gerador de retrato | Não |
| Comunidade | Institucional mínimo **D**; declarado **E** | `ContextoInstitucionalAgregado` (concluintes por curso, unidade e ano), já usado na narrativa | Limiar de exibição (DP-1101, DP-2105). Agregados de dado declarado exigem snapshot de Campanha encerrada (012) e DP-2107. Autorização para publicar a egressos | "Conectados ao portal", "atualizaram recentemente" (comparação social, vetada) | Não |
| Oportunidades | **C** | Nada | Conteúdo curado: tipo, título, resumo, URL oficial, unidade responsável, público por contexto institucional, período. Operação por escopo | Construir vagas, inscrições, eventos ou CMS | **Sim: Oportunidade** |
| Manifestação de interesse | **C** | Nada (o contato existe, da 020) | Registrar o ato, a forma de contribuição, a formação de referência, a ciência e a retirada. Lista e exportação por unidade | Workflow de mentoria, agenda, CRM | **Sim: Manifestação de interesse** |
| Personalização | **D** | Contexto institucional das conclusões | Regra explícita e explicável ("aparece porque você concluiu X em Y") | Motor de recomendação | Não |
| Consentimento | **B** | Nenhum modelo; o termo só existe dentro do instrumento (2024) | Nas escritas novas, guardar a **versão do texto de ciência** apresentado (XVII). Sem framework genérico de consentimento | "Gerenciador de consentimentos" universal | Campo, não entidade |
| Privacidade | Princípios **A**; mecanismos **B** | Minimização, pseudonimização, cifra, logs sem dado pessoal | Limiar de agregados para o público egresso | — | Não |
| Comunicação | Pesquisa **A**; Portal **E** | E-mail por Lote (020), transporte com guardas | Avisar de oportunidades tem **outra finalidade**: base legal própria e preferência separada da mobilização (nota de roadmap da 020, item 6) | Newsletter dentro da mobilização | Não, por ora |
| Autenticação | Demonstração **A**; produção **E** | Fronteira substituível (018) | Mecanismo real (Portão A, DP-1808; Gov.br não presumido) | Login próprio do Portal | Não |
| Shell e navegação | **C** (experiência) | Shell único, sem navegação, dentro de `interface` | Shell do Portal, com navegação só para áreas que existem, e Início como destino do login | Redesenhar tokens e componentes já auditados | Não |
| Área administrativa | **B** | `VinculoDeGovernanca` (CPAEG institucional, CSAEG por unidade); padrão de telas do `/acompanhamento/`; sem Django admin | Telas mínimas de Oportunidade e de Manifestação, no mesmo padrão e escopo | Ligar o Django admin ou criar um backoffice novo | Não |
| Volte ao Ifes | **C** (é a manifestação) | — | Ver S3 | — | (a mesma) |
| Memória do campus | **E** | Nada; só a ilustração vetorial genérica (DP-2106) | Fonte de fatos do período (não existe); acervo de imagens com licença | Nostalgia inventada (auditoria de 2026-10-02, §5) | Não |
| Encontros e aproximação entre egressos | **E** | — | Base legal, desenho próprio, moderação | Rede social | Não |

### 3.2 Onde o código está acoplado a "pesquisa"

Sem generalizar por prevenção, só entram aqui os pontos em que **uma capacidade do Portal
realmente esbarra**:

| Acoplamento | Onde | Por que atrapalha o Portal | Ajuste mínimo |
|---|---|---|---|
| Login e `/` levam à lista de pesquisas | `acesso/views.py:54`; `interface/views.py` (`inicio`) | O primeiro contato é uma tarefa, não um reconhecimento | O destino passa a ser o Início do Portal; `/formacoes/` não muda |
| A narrativa só abre com Participação concluída | `narrativa/consultas.py:elegivel` | Inverte a troca de valor | **Decidido (D3):** regra positiva por Conclusão Acadêmica, revisada na S1 |
| O shell fica no app da pesquisa | `interface/templates/interface/base.html`, estendido por `narrativa` e `contato` | A navegação do Portal não cabe num template do app da pesquisa | Extrair o shell para um lugar neutro; a jornada continua **idêntica** na tela |

**Conferido no código para a D3.** A Participação é só porta de acesso, não fonte de dado:

- `elegivel` é o único ponto da narrativa que consulta `Participacao`;
- a narrativa não lê Respostas (021 FR-044);
- nenhum texto da narrativa nem do card menciona a pesquisa;
- o vídeo reutiliza a composição do card.

Card e vídeo, portanto, não dependem semanticamente da participação.

**Não estão acoplados demais e não devem ser generalizados:**

- `Campanha` e `Participacao` são corretamente específicas da pesquisa.
- `ContatoDaPessoa` já nasceu independente da Campanha.
- A sessão (`acesso`) já é neutra.
- O contrato da narrativa já é serializável.

### 3.3 O mockup confrontado com decisões já tomadas

O mockup é protótipo conceitual. Nos itens abaixo, o código e as auditorias já deram resposta.
Reabrir qualquer um exige motivo registrado.

| Elemento do mockup | Decisão existente | Recomendação |
|---|---|---|
| "Redes de Computadores · Geração 2008", "72 conectados", "31 atualizaram recentemente" | Auditoria de 2026-10-02, §5: veda "Sua turma de 2017" e comparação social. 021 FR-053: só duas métricas fechadas | Fora. A comunidade, quando vier, mostra recortes institucionais com limiar |
| "Olá, Marina" como abertura principal | A mesma auditoria: a saudação pelo nome não é o principal recurso de personalização, e o nome pode faltar (DP-2103) | Abrir pelo **contexto da formação**; o nome fica em segundo plano |
| "Campus Vitória faz parte das suas primeiras descobertas"; Memória do campus | Não há fonte para fatos do período; nostalgia inventada é vetada | Fora (E) |
| Linha do tempo com mestrado (2013) e doutorado (2021) "declarados" | Q47 não tem ano; a narrativa não usa Respostas (021 FR-044; DP-2107) | Fora até DP-2107. Uma formação **declarada pela 019** pode aparecer como "informada por você, aguardando confirmação" |
| "Cerca de 3 minutos" | 008 FR-095 veda estimativa de tempo; a jornada real tem 46 perguntas (reauditoria) | Fora. A promessa seria falsa |
| "Atualize": 3 passos (situação + interesses) fora do instrumento | Instrumento único (decisão de 2026-10-03); Princípios VII e XIII | No Portal, "Atualizar" **é** a Participação existente. "Só o que mudou" vai para a nova Versão, da CPAEG |
| Hero escuro, faixas, cartões em grade | Auditoria de identidade visual, §6: "não importar do portal: hero, faixas alternadas, cards em grade" (produto de tarefa) | **Reabrir com motivo explícito**: o Início do Portal é em parte uma superfície de navegação. Usar tokens e componentes da 015 sem redesenhar a jornada |
| Três estilos de retrato | 021: um tema em P1, no máximo dois | Fora (E) |
| "Quero ser avisada se encontros estiverem disponíveis" | XVI: não coletar sem finalidade presente | Fora. É coleta para uma função que não existe |
| Legenda "Registro institucional × declarado" | Princípio III | **Adotar.** É o melhor elemento do mockup e o domínio já sustenta |
| "Por que estou vendo isto?" | Proveniência e explicabilidade | **Adotar** em Oportunidades, com regra explícita |

---

## 4. Fronteira entre Portal e Trajetória Ifes

**Decisão arquitetural: dois anéis concêntricos no mesmo software, com dependência num único
sentido.** A divisão física do anel externo em módulos Django é uma **hipótese de
modularização** a confirmar em cada spec. Um desenho possível é `portal` (experiência),
`oportunidades` e `reciprocidade`. Também cabe um único módulo de relacionamento, ou outra
combinação.

```text
┌──────────────────────── Portal / Relacionamento (anel externo) ────────────────────────┐
│  experiência: shell, Início, navegação, composição                                     │
│  fatos próprios do horizonte atual: Oportunidade · Manifestação de interesse           │
│  (divisão em módulos Django: hipótese, decidida nas specs S1, S2 e S3)                 │
│                 │ lê Pessoa e contexto; não escreve no núcleo                          │
│  ┌──── Trajetória Ifes = NIAE (núcleo, inalterado) ─────────────────────────────────┐ │
│  │ academico · participacao · instrumento · campanha · declaracao · acesso ·        │ │
│  │ contato · narrativa · video · mobilizacao · acompanhamento · analitico ·         │ │
│  │ exportacao                                                                       │ │
│  └──────────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

Regras da fronteira, testáveis do mesmo jeito que os testes de fronteira que o projeto já tem
(`tests/*/test_*_fronteira*.py`):

1. **Dependência num só sentido.** O código do anel externo pode importar o núcleo. Nenhum
   módulo do núcleo importa o anel externo.
2. **O anel externo não escreve no núcleo.**
   - Ele não cria Participação, Resposta, Conclusão, Formação Declarada nem Contato.
   - Para isso, encaminha às telas existentes: a jornada, `/declaracao/` e `/meu-email/`.
3. **Nada do anel de relacionamento entra no dado analítico.** Oportunidades e Manifestações
   ficam fora do snapshot (012) e das exportações GeN (013).
4. **O núcleo continua funcionando sem o Portal.**
   - Com o Portal desligado, a jornada da pesquisa funciona como hoje (XXV).
   - O Portal pode ser removido, ou trocado por um Portal institucional externo, sem migração
     no núcleo. Nesse caso, o contrato da narrativa e a sessão viram as fronteiras de
     integração.
5. **Nomes.**
   - "Trajetória Ifes" continua sendo o nome do núcleo e da capacidade de acompanhamento. No
     mockup, ele já aparece assim, como rótulo da área "Atualize".
   - "Portal do Egresso" é a **denominação provisória** da experiência de demonstração. Ela
     não presume a definição institucional (D2).
6. **A coleta é independente do Portal.**
   - Portal (PAEG, Art. 10, I) e questionário (Art. 10, II) são ações distintas.
   - Campanhas divulgam acesso direto ao instrumento, por e-mail ou outro canal.
   - O egresso se identifica e responde sem passar pelo Início.
   - O caminho de entrada (instrumento ou Portal) é preservado depois da identificação.
   - Com o Portal desabilitado, a coleta funciona como hoje.

   Esta regra entrou com a S0 (ADR 0008; Constituição 2.1.0, "Camada de relacionamento").

**Por que não emendar a Constituição para dizer "o Trajetória Ifes é o Portal".** Isso apagaria
a fronteira do NIAE, que protege o núcleo de virar CRM ou portal de conteúdo (Princípios VI e
XXII). Os anéis mantêm essa proteção e, ao mesmo tempo, permitem compor o Portal aqui.

---

## 5. Proposta arquitetural

### 5.1 Alternativas avaliadas

| Alternativa | Avaliação |
|---|---|
| 1. Nova aplicação (outro projeto ou serviço) | **Não.** Duplica sessão e identidade, exige uma API entre os dois (a Constituição só admite API a partir de caso real de integração) e dobra a operação. Não há time nem produção que justifiquem |
| 2. Tudo dentro do app `interface` | **Não.** Mistura o Portal com a jornada da pesquisa; o app já tem 658 linhas na view e carrega a responsabilidade da coleta |
| 3. Camada de apresentação sobre os mesmos domínios | **Necessária, mas não suficiente.** Resolve o Início, a navegação e a trajetória. Não resolve Oportunidades nem Manifestação, que têm fatos próprios |
| **4. Combinação: camada de experiência (3) + fatos de relacionamento próprios, no mesmo projeto, fora do núcleo** | **Recomendada.** É a menor complexidade com boa separação. Segue o padrão do repositório: módulos pequenos com fronteira testada, como `contato` e `video`. A granularidade em módulos fica para as specs |

### 5.2 Mudanças estruturais necessárias

São poucas e localizadas:

1. **Shell neutro.**
   - Extrair o cabeçalho, o rodapé e a faixa de demonstração de `interface/base.html` para um
     template base compartilhado.
   - A jornada da pesquisa continua visualmente idêntica.
   - O shell do Portal acrescenta a navegação, com os tokens da 015 e sem tokens novos.
2. **Entrada do Portal.**
   - O Início do Portal ganha uma entrada neutra. O acesso direto ao instrumento pelo
     convite continua levando à pesquisa (ADR 0008).
   - A 024 compara duas formas:
     - entradas distintas, mantendo `/acesso/` → `/formacoes/`;
     - destino de lista fechada.
   - Prefere-se a que preserve os contratos existentes com menos alterações.
   - `/formacoes/`, `/participacoes/…`, `/minha-trajetoria/` e `/meu-email/` mantêm rotas e
     comportamentos, exceto a regra de acesso à trajetória (S1).
3. **Tabelas novas só nas specs S2 e S3.**
   - Uma para Oportunidade e uma para Manifestação de interesse, com migração aditiva (XXVII).
   - Nenhuma tabela existente é alterada.
   - A S1 não tem migração.
4. **Telas de operação.**
   - No padrão do `/acompanhamento/`, autorizadas por `VinculoDeGovernanca` (CSAEG por
     unidade, CPAEG institucional).
   - Sem Django admin.
5. **O que não entra:**
   - API;
   - fila nova;
   - cache novo;
   - dependência Python nova;
   - JavaScript obrigatório (a jornada funciona sem JS).

### 5.3 O que **não** muda

- Pessoa, Conclusão, Participação, Resposta, Versão e Campanha.
- Snapshot e exportações.
- Acesso por CPF e data.
- Mobilização.
- Gates de produção.

---

## 6. Roadmap S0–S4

Os números de feature seguem a ordem do repositório. Os tamanhos são relativos: P = pequeno
(1–2 histórias), M = médio.

### S0 — Decisão de fronteira do Portal *(ADR 0008 + Constituição 2.1.0; não é feature)*

**Situação: concluída em 2026-10-07.** Ver o
[ADR 0008](../adr/0008-portal-do-egresso-camada-de-relacionamento.md) e a seção "Camada de
relacionamento" da Constituição.

- **Problema.**
  - A Constituição veda presumir a relação com o Portal (Posicionamento; DP-406; DP-2108).
  - Construir a camada aqui sem registrar a decisão contornaria a Constituição.
- **Forma mínima.**
  - Um ADR curto e uma emenda pontual: **MINOR, 2.1.0**, porque o núcleo e suas invariantes
    ficam intactos.
  - A emenda toca só três trechos da Constituição:
    - "Posicionamento do Projeto";
    - "Fronteira do Domínio do NIAE";
    - o item 12 dos "Princípios Resumidos".
  - O Princípio VI não muda. Ele já admite incorporar uma capacidade quando não há solução
    institucional adequada, desde que a spec responda às cinco perguntas.
- **O que registra.**
  - O modelo de anéis e as cinco regras da seção 4.
  - Que o anel de relacionamento é **hipótese de produto reversível** (XXIX), restrita à
    demonstração até decisão da Proex/CPAEG.
  - Que a PAEG dá base para a CSAEG gerir o Portal na unidade (Art. 13, parágrafo único;
    Art. 22, III).
  - Que "Portal do Egresso" é **denominação provisória** da experiência de demonstração.
  - Que a divisão física em módulos é decidida nas specs.
  - Que **a coleta é independente do Portal**: acesso direto ao instrumento pelas Campanhas,
    destino preservado após a identificação e funcionamento com a camada desabilitada.
  - Que **não há link específico de Campanha**, e a independência não exige um. O convite
    continua neutro (018 FR-053; ADR 0004) e leva à entrada do instrumento.
- **Valor para o egresso.** Nenhum direto. A S0 destrava o resto sem contornar a Constituição.
- **Dependências.** Nenhuma.
- **Necessária agora?** **Sim**, antes da S1.

### S1 — Início do egresso e shell do Portal *(024; P/M; só leitura; sem modelo novo)*

- **Problema.** Depois do login, o egresso cai numa lista de pesquisas. Nada reconhece a
  história dele antes de pedir algo.
- **Valor para o egresso.** Um lugar que mostra, nesta ordem:
  1. o que o Ifes sabe sobre ele;
  2. de onde vem cada informação;
  3. o que ele pode fazer ali;
  4. só então, a pesquisa aberta, como convite.
- **Regra de acesso à trajetória (D3, decidida), formulada positivamente:** *a Pessoa
  identificada com ao menos uma Conclusão Acadêmica pode acessar sua trajetória institucional,
  incluindo o card e o vídeo, independentemente de participação em pesquisa.*
  - É uma regra de apresentação do domínio, não uma exceção aberta para o Portal.
  - A spec DEVE registrar que ela **revisa a 021** (FR-001, FR-002 e a escolha E2) e a
    **condição de acesso da 022** (FR-001).
  - A 021 FR-003 continua valendo: a confirmação "Pesquisa concluída" segue levando à
    trajetória.
  - Uma Pessoa sem Conclusão Acadêmica não tem trajetória institucional e segue o
    encaminhamento atual.
- **Reutiliza.**
  - A sessão do `acesso`.
  - `ResolucaoDaEntrada`, para o estado da pesquisa.
  - `TrajetoriaNarrativa`: o resumo do Início sai da mesma narrativa, sem uma segunda
    montagem.
  - O contato (020), o card e o vídeo.
  - Os tokens da 015.
- **Novos conceitos.**
  - O shell com navegação só para áreas que existem: Início, Minha trajetória, Atualizar
    (= pesquisa) e Meu e-mail.
  - A rota do Início e sua entrada neutra.
  - O nome provisório "Portal do Egresso".
- **Dois caminhos de acesso, a mesma coleta (ADR 0008).**
  - **Estado atual, conferido no código:**
    - não existe link específico de Campanha;
    - o convite leva a `/acesso/`, neutro (018 FR-053);
    - o login sempre segue para `/formacoes/`, onde a resolução da entrada (007) escolhe a
      pesquisa;
    - a 023 retoma ali o envio guardado (FR-006);
    - nenhuma tela preserva o destino pedido antes da identificação.
  - **Ajuste necessário na 024.** Introduzir o Início sem desviar o acesso direto. A spec
    compara e escolhe o mecanismo:
    - **entradas neutras distintas:** o convite mantém `/acesso/` → `/formacoes/` e o Portal
      tem entrada própria. É a alternativa mais simples, preferida pelo solicitante;
    - **destino de lista fechada.**

    Em qualquer caso: nunca URL livre (para não abrir redirecionamento aberto), nunca
    identidade, token, formação ou Campanha no endereço, e com autorização e elegibilidade
    respeitadas.
- **Testes obrigatórios de independência.**
  - Acesso espontâneo ao Portal.
  - Acesso direto ao instrumento pelo link externo do convite.
  - Caminho de entrada preservado depois da identificação, inclusive após sessão expirada,
    e com a retomada do envio guardado da 023.
  - Participação em andamento e Participação concluída.
  - Campanha encerrada; pessoa fora da abrangência ou sem pesquisa disponível.
  - Trajetória Ifes funcionando com a camada do Portal desabilitada.
  - Dependência num só sentido entre a camada e o núcleo.
- **Limite de escopo.** A 024 não é um redesenho da aplicação. Ela resolve só três coisas:
  - **acesso:** entrar pelo Portal ou direto pelo instrumento;
  - **experiência:** um Início que reconhece a história do egresso;
  - **integração:** acesso à trajetória, ao retrato e às Campanhas existentes, sem duplicar
    funcionalidade.
- **Inclui.** Os ajustes R-01, R-02 e R-05 da reauditoria de esforço, que ela mesma recomenda
  fazer "junto com o próximo trabalho".
- **Critérios de sucesso.** Os critérios observáveis do Checkpoint 1 (seção 7) entram como
  critérios de sucesso da spec. São definidos **antes** do teste.
- **Fica fora.**
  - Oportunidades, comunidade, Volte ao Ifes e interesses, inclusive como links ou áreas de
    fachada no produto.
  - Qualquer escrita nova.
  - Saudação pelo nome como destaque.
  - Indicador social.
  - Estimativa de tempo.
- **Riscos.**
  - O Início virar um painel de pendências. Mitigação: a pesquisa aparece como convite, uma
    só vez.
  - Reabrir a identidade visual sem critério. Mitigação: critério objetivo de
    reaproveitamento da 015 e captura em 375 px, como na 021 e na 023.
- **Consideração de produção, sem bloquear a demonstração.**
  - Abrir card e vídeo a todos aumenta a procura pela geração de vídeo.
  - Ela continua limitada pela ação explícita do egresso (022 FR-002) e pela concorrência
    configurada (padrão: 2).
  - A capacidade deve ser revista antes do uso real.
- **Necessária agora?** **Sim.** É o teste mais barato da hipótese de troca de valor.

### S2 — Oportunidades curadas *(025; M; primeiro fato persistente novo)*

- **Problema.** O Portal só tem algo a oferecer se houver conteúdo institucional pertinente.
- **Valor para o egresso.**
  - Caminhos concretos: formação, curso, evento, pesquisa e extensão, carreira.
  - Ligados às formações que ele concluiu, com a explicação de por que aparecem.
- **Reutiliza.**
  - O contexto institucional das conclusões (unidade, nível, curso).
  - A governança e o escopo (010).
  - O padrão de telas do acompanhamento.
  - O shell da S1.
- **Novos conceitos.**
  - **Oportunidade**:
    - tipo, de lista fechada;
    - título e resumo;
    - URL oficial;
    - unidade responsável;
    - período de divulgação;
    - público opcional, por contexto (unidade, nível ou curso).
  - Uma regra de pertinência **determinística e explicável**.
  - Telas mínimas para criar, editar e retirar, dentro do escopo.
  - A spec decide em que módulo Oportunidade vive.
- **Fica fora.**
  - Inscrição, vagas, eventos com agenda ou confirmação de presença.
  - Recomendação e interesses declarados.
  - Contagem de cliques e rastreamento.
  - Notificação.
  - Upload de imagem.
  - Integração com sistemas de oferta.
- **Riscos.**
  - **Operacional, o maior:** portal vazio ou desatualizado. Mitigação: o período de
    divulgação expira sozinho, e o Início esconde a área quando não há nada.
  - **Virar CMS.** Mitigação: sem corpo rico, só resumo e link oficial.
- **Dependências.** S1 e Checkpoint 1.
- **Necessária agora?** Depois do Checkpoint 1. Na demonstração, um catálogo fictício carregado
  pelo `preparar_demonstracao` basta.

### S3 — Volte ao Ifes: manifestação de interesse *(026; M; primeira escrita nova)*

- **Problema.** A relação só vai da instituição para o egresso. Ele não tem como se oferecer
  para contribuir.
- **Valor para o egresso.**
  - Dizer, em poucos toques, como quer contribuir: mentoria, compartilhar experiência,
    oferecer oportunidade, pesquisa e extensão, parceria, contar a própria história.
  - Saber o que acontece depois.
- **Reutiliza.**
  - Pessoa e sessão.
  - As conclusões: escolher a formação de referência define a unidade e o escopo de quem
    recebe.
  - `ContatoDaPessoa`: sem e-mail cadastrado, o egresso é convidado a ir a `/meu-email/`, sem
    duplicar contato.
  - Governança, escopo e CSV.
- **Novos conceitos.**
  - **Manifestação de interesse**:
    - forma de contribuição, de lista fechada;
    - formação de referência;
    - mensagem curta opcional;
    - versão do texto de ciência apresentado (XVII);
    - momento do registro;
    - retirada pela própria pessoa.
  - Lista por escopo para a unidade, com CSV.
  - A spec decide em que módulo a Manifestação vive.
- **Fica fora.**
  - Workflow de atendimento: estados, atribuição, prazos.
  - Programa de mentoria, agenda e pareamento entre pessoas.
  - Perfil público.
  - Coleta de currículo ou de história.
- **Riscos.**
  - Expectativa frustrada: o egresso se oferece e ninguém responde. Mitigação: saber quem
    recebe (D4) e dizer com honestidade o que acontece depois.
  - Base legal (D5).
- **Dependências.** S1 e Checkpoint 1. Independe da S2 e pode correr em paralelo.
- **Necessária agora?** Sim, preferencialmente depois da S2, pelo princípio de oferecer antes
  de pedir.

### S4 — Minha trajetória como linha do tempo da relação *(027; P; opcional)*

- **Problema.** A página mostra as formações, mas não a relação: participações, formações
  informadas, contribuições.
- **Valor para o egresso.** Ver a própria história com o Ifes por inteiro, com a proveniência
  explícita.
- **Reutiliza.** A narrativa da 021 e fatos já registrados:
  - Participações concluídas ("Você contou sua trajetória em 2026"; item ID-10 da auditoria de
    2026-10-02);
  - Formação Declarada, com o estado da validação;
  - Manifestações da S3.
- **Novos conceitos.** Nenhuma entidade. Os eventos da relação são **derivados** na consulta,
  como a narrativa (E3).
- **Fica fora.**
  - Conteúdo de Respostas (DP-2107).
  - Marcos declarados com data.
  - Fatos do período.
  - Card com eventos da relação.
- **Riscos.** Pequenos. O principal é apresentar a Participação como pendência.
- **Dependências.** S1; S3 para incluir as manifestações; e o Checkpoint 2.
- **Necessária agora?** Não. Só se o Checkpoint 2 mostrar que a página é revisitada.

### Na mesma visão, mas fora da camada Portal

- **"Conte só o que mudou."**
  - Pertence à **evolução metodológica do instrumento** e ao pacote de decisões da CPAEG para
    a nova Versão: DP-307, reaproveitamento entre formações (EF-05), divisão da Avaliação.
  - O Portal só oferece a entrada.
  - É o maior ganho de esforço restante: 6 a 7 perguntas a menos para todo egresso e ~20 por
    formação extra (reauditoria §7).
  - Não é feature do Portal.
- **Comunidade agregada.** Só depois de:
  - limiar de exibição ao público egresso (DP-1101, DP-2105);
  - autorização para publicar;
  - Campanha encerrada com snapshot (012);
  - DP-2107, para dado declarado.
- **Reentrada com menos atrito.** Spec própria, depois do Portão A e de DP-1808. Ganha peso com
  o Portal, que é um lugar ao qual se volta.

---

## 7. Checkpoints de validação

O sistema não tem usuários reais. A hipótese só pode ser testada com **teste moderado**: o
egresso entra por uma persona fictícia e conversa com base na própria história. Os critérios
são definidos **antes** de cada teste.

Não são critérios de sucesso:

- aumento de taxa de resposta;
- engajamento quantitativo;
- qualquer métrica de conversão.

O teste moderado não tem amostra nem contexto operacional para sustentar esse tipo de
conclusão.

### Checkpoint 1 — depois da S1: "fui reconhecido antes de ser solicitado"

- **O que testa.** Se o modelo mental mudou: de "isto é um formulário que o Ifes quer que eu
  responda" para "isto é um espaço meu com o Ifes".
- **Como.**
  - Usa só as capacidades reais da S1.
  - Oportunidades e Volte ao Ifes **não entram no produto**, nem como links ou áreas de
    fachada. Se for útil explorá-las, o mockup conceitual é mostrado **separadamente**, na
    mesma sessão, identificado como protótipo.
- **Economia.** Pode correr na mesma sessão do teste moderado da jornada de pesquisa que a
  reauditoria já recomendou: mesmas personas, dois objetivos.

**Critérios de compreensão (modelo mental).** A pessoa:

1. entende que entrou num espaço permanente de relacionamento com o Ifes, e não só numa
   pesquisa;
2. identifica o que o Ifes já sabe sobre a trajetória dela;
3. entende a proveniência: o que é registro do Ifes e o que ela mesma informou;
4. percebe que tem acesso a valor (trajetória, card, vídeo) antes de responder qualquer
   pesquisa;
5. sabe onde atualizar a trajetória quando houver uma pesquisa disponível.

**Critérios de comportamento (navegação).** A pessoa:

1. chega a Minha trajetória sem ajuda;
2. trata a pesquisa como um convite, uma ação disponível, e não como a finalidade de todo o
   ambiente;
3. localiza as demais capacidades reais (Retrato e vídeo, Meu e-mail);
4. não lê o Início como um painel administrativo de pendências.

**Como ler o resultado.**

- **Os critérios de compreensão falham.** O problema está na S1. Corrigir antes da S2 e da S3,
  porque construir as duas tabelas sem a premissa validada seria construir antes da hora.
- **Os de compreensão passam e os de comportamento falham.** O problema é de navegação ou de
  texto. Ajustar dentro da S1, sem replanejar.

### Checkpoint 2 — depois da S2 e da S3: "recebo valor e quero retribuir"

- **O que testa.** As capacidades reais de Oportunidades e de Volte ao Ifes.
- **Critérios de compreensão.** A pessoa:
  1. entende por que cada oportunidade aparece para ela (a explicação convence);
  2. distingue oportunidade institucional de anúncio;
  3. entende o que acontece depois de manifestar interesse, e quem recebe;
  4. entende que pode retirar a manifestação.
- **Critérios de comportamento.** A pessoa:
  1. encontra uma oportunidade pertinente sem ajuda;
  2. consegue registrar uma manifestação em poucos toques, sem dúvida sobre o uso do contato;
  3. não confunde Volte ao Ifes com a pesquisa.
- **Como ler o resultado.** O Checkpoint 2 decide se a S4 vale a pena e informa as decisões D4
  e D5 com evidência.

---

## 8. Dependências

```text
 S0  ADR 0008 + Constituição 2.1.0 — CONCLUÍDA
     (fronteira; coleta independente; nome provisório; módulos decididos nas specs)
  │
  ▼
 S1  Início e shell do Portal + trajetória por regra positiva (revisa 021 FR-001/002/E2, 022 FR-001)
     + acesso direto ao instrumento e destino preservado, com testes de independência
  │
  ▼
 ◆ Checkpoint 1 — modelo mental e navegação
   (com o teste moderado da jornada; mockup à parte para Oportunidades/Volte ao Ifes)
  │
  ├──────────────┐
  ▼              ▼
 S2             S3            ◄── D4 (quem cura e quem recebe) e D5 (base legal) para uso real
 Oportunidades  Volte ao Ifes
  │              │
  └──────┬───────┘
         ▼
 ◆ Checkpoint 2 — valor recebido e reciprocidade
         │
         ▼
 S4  Linha do tempo da relação (opcional, se o checkpoint justificar)

Trilhas paralelas, fora da camada Portal:
  CPAEG: nova Versão contextualizada ─────► "conte só o que mudou"
  Portão A / DP-1808 ─────────────────────► reentrada com menos atrito ──► uso real
  DP-1101 / DP-2105 / DP-2107 ────────────► comunidade agregada
```

As dependências **de código** são poucas:

- S2 e S3 precisam do shell e do Início da S1;
- S4 lê as manifestações da S3.

As demais setas são dependências **de decisão ou de validação**.

---

## 9. Quick wins

Quase tudo aqui é composição do que já existe e cabe na S1:

1. **Início que reconhece.** Mostra as formações, a proveniência, o estado da pesquisa como
   convite e atalhos. Não exige modelo novo.
2. **Minha trajetória, card e vídeo antes da pesquisa** (D3, decidida). É uma regra positiva no
   lugar de `narrativa/consultas.py:elegivel`. Os dados são só institucionais, e o egresso já
   vê suas formações em `/formacoes/`.
3. **Retrato e vídeo no menu.** Já existem (021 e 022); falta só navegação.
4. **Meu e-mail no menu.** Já existe (020); hoje só aparece depois de concluir a pesquisa.
5. **"Por que estou vendo isto?"** Sai de uma regra de pertinência por contexto institucional.
   Fica na S2.
6. **Devolutiva institucional por link.**
   - A PAEG prevê o Relatório Anual de Acompanhamento de Egressos (Proex, Art. 14).
   - Um link curado no Início devolve resultados sem calcular agregado aqui.
   - Só exige uma URL oficial existente.

---

## 10. Itens a postergar

Itens atraentes, mas que seriam overengineering agora:

- **Rede, mensageria, aproximação entre egressos, "avise-me de encontros".** Exigem base legal
  e moderação.
- **Perfil de interesses.** Seria dado sem consumidor (XVI).
- **Motor de recomendação, IA, crawler de editais.**
- **Vagas, inscrições, eventos com agenda.** Integrar quando houver sistema institucional, sem
  absorver o domínio (VI).
- **Notificações de oportunidades por e-mail ou outros canais.** Têm outra finalidade e outra
  base legal.
- **Comunidade com dado declarado.**
- **Memória do campus, fotografias, fatos do período** (DP-2106; vetados pela auditoria).
- **Três estilos de retrato, formatos de card além do 9:16.**
- **Marcos declarados com ano na linha do tempo** (DP-2107; o instrumento não registra datas).
- **Portal para estudantes ainda não egressos.** É outra população (Princípio II).
- **Portal para declarante sem Pessoa institucional (019).** Ele continua com `/declaracao/`.
- **Django admin, CMS, BI, API pública.**

---

## 11. Decisões

### 11.1 Já decididas pelo solicitante (2026-10-07)

| # | Decisão | Onde é registrada |
|---|---|---|
| D1 | A camada Portal/Relacionamento vive neste software, como hipótese reversível restrita à demonstração, e depende do NIAE num só sentido | S0 (ADR 0008 + emenda 2.1.0), concluída |
| D2 (provisório) | "Portal do Egresso" é o nome provisório da experiência de demonstração; "Trajetória Ifes" é o nome da capacidade de acompanhamento | S0; textos da S1 |
| D3 | A trajetória institucional, com card e vídeo, fica acessível a quem tem ao menos uma Conclusão Acadêmica, independentemente de pesquisa (alternativa a) | S1, revisando a 021 e a 022 |
| D7 | A coleta é independente do Portal: acesso direto ao instrumento pelas Campanhas, caminho de entrada preservado após a identificação e funcionamento com a camada desabilitada | S0 (ADR 0008; Constituição 2.1.0); testes na S1 |

### 11.2 Continuam pendentes

| # | Decisão | Quem decide | O que bloqueia |
|---|---|---|---|
| **D2 (definitivo)** | Nome institucional da experiência | ACS, com Proex | Só o uso real; não bloqueia a S1 |
| **D1 (produção)** | Relação entre este software e o Portal do Egresso da PAEG (Art. 10, I; Art. 13) | Proex/CPAEG/DTI | Só o uso real |
| **D4** | Quem cura as oportunidades e quem recebe e responde às manifestações em cada unidade. A PAEG aponta a CSAEG (Art. 22, III) e a DIREC (Art. 15) | CPAEG/Proex | Uso real da S2 e da S3; na demonstração vale CSAEG como hipótese |
| **D5** | Base legal e texto de ciência para guardar a manifestação e usar o contato com essa finalidade; finalidade de mostrar oportunidades por contexto acadêmico | Encarregado de dados, com a CPAEG | Uso real da S3 (e da S2, se segmentar por contexto) |
| **D6** | Limiar e autorização para mostrar agregados a egressos (DP-1101, DP-2105) | CPAEG/Proex, encarregado | Comunidade (postergada) |

O Portal não reabre as decisões que já estavam pendentes:

- DP-307 e o pacote da nova Versão (CPAEG);
- DP-1808 e o Portão A (identidade);
- DP-2107 (comparabilidade entre Versões);
- DP-1001 (operadores reais).

---

## 12. A hipótese de produto

> O acompanhamento tende a funcionar melhor quando deixa de ser uma pesquisa periódica isolada
> e passa a fazer parte de uma relação contínua.

A sequência foi montada para testar a hipótese em duas etapas e pelo menor custo:

1. **Primeiro, a premissa:** reconhecimento antes da coleta. É testada no Checkpoint 1, só com
   a mudança de experiência da S1, sem nenhuma tabela nova.
2. **Depois, valor e reciprocidade:** testados no Checkpoint 2, com as capacidades reais da S2
   e da S3.

**Se a premissa falhar, o custo afundado será só a S1**: uma camada de apresentação removível e
uma regra de acesso, com o núcleo intacto. Esse é o critério de "não construir demais antes da
hora".
