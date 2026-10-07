# ADR 0008 — Portal do Egresso como camada de relacionamento sobre o núcleo, com coleta independente

- **Status**: Aceito como hipótese de produto, só para a demonstração. Decidido pelo
  solicitante em 2026-10-07. A adoção institucional continua pendente.
- **Data**: 2026-10-07
- **Contexto de origem**:
  - [Portal do Egresso × Trajetória Ifes — arquitetura de produto e roadmap](../roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md)
  - Constituição 2.1.0 (Posicionamento do Projeto; Fronteira do Domínio, "Camada de
    relacionamento")
  - Specs [016](../../specs/016-mobilizacao-comunicacao-simulada/spec.md) (FR-021, FR-022),
    [018](../../specs/018-identificacao-acesso-egresso/spec.md) (FR-053),
    [021](../../specs/021-minha-trajetoria-narrativa/spec.md) (DP-2108) e
    [023](../../specs/023-jornada-menos-esforco/spec.md) (FR-001, FR-006)

## Contexto

A PAEG prevê duas ações distintas:

- um **Portal do Egresso**, ambiente de relacionamento com os egressos (Art. 10, I; Art. 13);
- a **aplicação de questionário eletrônico** (Art. 10, II).

Até a 2.0.0, a Constituição dizia que o Trajetória Ifes não é o Portal e que a relação entre
os dois "NÃO DEVE ser presumida pelo desenvolvimento" (DP-406, DP-2108).

O solicitante quer testar uma hipótese de produto: o acompanhamento funciona melhor quando o
egresso, antes de ser chamado a responder, é reconhecido e recebe algo em troca. A análise do
roadmap mostrou três pontos:

- **O código hoje faz o contrário.**
  - O login leva à lista de pesquisas (`acesso/views.py`, destino `/formacoes/`).
  - A trajetória só abre depois de uma Participação concluída
    (`narrativa/consultas.py:elegivel`).
- **O Portal é sobretudo experiência.** No horizonte analisado, só dois fatos persistentes
  novos se justificam: Oportunidade e Manifestação de interesse.
- **O núcleo não precisa mudar.**

Sobre o acesso pelas Campanhas, o código mostra o seguinte:

- **O link do convite é neutro por decisão.** Ele leva à entrada `/acesso/` "sem
  identificação, token, formação ou Campanha" (018 FR-053; 016 FR-021 e FR-022; ADR 0004).
- **Não existe link específico de Campanha.** Quem recebe o convite se identifica e cai em
  `/formacoes/`. Ali a resolução da entrada (007) escolhe a pesquisa e trata os casos de
  Campanha encerrada, de formação fora da abrangência e de pesquisa em andamento.
- **Não há preservação de destino.** Uma tela que exige identificação manda para `/acesso/`,
  e o login sempre segue para `/formacoes/`.
- **A retomada de envio depende desse destino.** A 023 guarda um envio pendente quando a sessão
  expira e o retoma a partir de `/formacoes/` (023 FR-006).

Se a Feature 024 trocasse o destino padrão do login para o Início do Portal sem mais nada, o
egresso que chega pelo convite cai no Portal, e não na pesquisa. A coleta passaria a depender
do Portal.

## Alternativas consideradas

- **Nova aplicação para o Portal.**
  - Duplicaria sessão e identidade.
  - Exigiria uma API entre os dois sistemas, que a Constituição só admite a partir de caso real
    de integração.
  - Dobraria a operação.
- **Emendar a Constituição para dizer "o Trajetória Ifes é o Portal".**
  - Apagaria a fronteira que protege o núcleo de virar CRM ou portal de conteúdo (Princípios
    VI e XXII).
  - Além disso, presumiria uma decisão institucional.
- **Construir o Portal sem registrar a decisão.**
  - Contornaria a Constituição em silêncio.
- **Camada de relacionamento sobre o núcleo, no mesmo software, com coleta independente.**
  - **Escolhida.**

## Decisão

**O Portal do Egresso é desenvolvido neste software como camada de relacionamento sobre o
núcleo do Trajetória Ifes, como hipótese de produto restrita à demonstração.** As regras são
as da Constituição 2.1.0 (Fronteira do Domínio, "Camada de relacionamento"):

1. **Dependência num só sentido.** A camada depende do núcleo, nunca o contrário.
2. **A camada não escreve fatos do núcleo.** Para isso, ela encaminha às capacidades do
   próprio núcleo.
3. **Fatos da camada ficam fora do dado analítico.** Não entram em snapshot, exportação nem
   indicador.
4. **A coleta não depende do Portal.**
   - Instrumento, Campanha e Participação funcionam com a camada desabilitada.
   - A Campanha pode divulgar acesso direto ao instrumento, por e-mail ou outro canal
     institucional.
   - O egresso se identifica e responde sem passar pela página inicial do Portal.
   - Qualquer que seja o caminho, o instrumento, a Campanha e a Participação são os mesmos.
5. **O caminho de entrada escolhido sobrevive à identificação.**
   - Quem entra pelo instrumento chega ao instrumento. Quem entra pelo Portal chega ao
     Portal.
   - Valem a autenticação, a autorização (a Participação tem de ser da Pessoa) e a
     elegibilidade (a resolução da entrada e a admissão da Campanha).
   - Uma sessão identificada pode navegar entre as duas experiências, respeitadas as regras
     de acesso de cada tela.
   - O mecanismo é escolhido pela 024. Há duas opções:
     - entradas neutras distintas, uma por caminho, mantendo `/acesso/` → `/formacoes/`;
     - preservação de destino por lista fechada.
   - Em qualquer opção, a preferência é pela que preserve os contratos existentes com menos
     alterações.
6. **O link do convite continua neutro.**
   - Ele leva à entrada do instrumento, não ao Início do Portal.
   - Continua sem identidade, token, formação ou Campanha (018 FR-053).
   - A independência **não exige** link específico de Campanha. Ele não é adotado: exigiria
     rever a 018 FR-053 e a ADR 0004 sem necessidade.
7. **Nomes.**
   - "Portal do Egresso" é o nome provisório da experiência na demonstração.
   - "Trajetória Ifes" continua sendo o nome do núcleo e da capacidade de acompanhamento.
8. **A organização física em módulos não é decidida aqui.** Cada spec decide.

Esta ADR **não** representa adoção institucional. Continuam pendentes:

- a relação com o Portal da PAEG (Proex, CPAEG, DTI);
- o nome definitivo (ACS);
- os responsáveis por curadoria e atendimento (CPAEG);
- a base legal das escritas novas (encarregado de dados).

## Consequências

- **Constituição 2.1.0 (MINOR).** Esta ADR não toca nenhuma invariante do núcleo. A emenda
  altera três trechos:
  - o Posicionamento do Projeto, que admite a hipótese em demonstração;
  - a Fronteira do Domínio, que ganha a subseção "Camada de relacionamento";
  - o item 12 dos Princípios Resumidos.
- **A Feature 024 (Início do egresso e shell do Portal) deve:**
  - introduzir o Início do Portal sem prejudicar o acesso direto. O mecanismo é escolha da
    spec: entradas neutras distintas (o convite mantém `/acesso/` → `/formacoes/`; o Portal
    tem entrada própria) ou destino de lista fechada. Nunca uma URL livre, para não abrir
    redirecionamento aberto, e nunca dado de identidade no endereço;
  - preservar a retomada do envio guardado da 023 (FR-006);
  - ter testes para cada um destes casos:
    - acesso espontâneo ao Portal;
    - acesso direto ao instrumento pelo link externo do convite;
    - preservação do caminho de entrada depois da identificação, inclusive quando a sessão
      expira;
    - Participação em andamento e Participação concluída;
    - Campanha encerrada e pessoa fora da abrangência ou sem pesquisa disponível;
    - Trajetória Ifes funcionando com a camada do Portal desabilitada;
    - dependência num só sentido entre a camada e o núcleo (teste de fronteira).
- **Specs anteriores.** A 016, a 018 e a ADR 0004 não mudam, porque o link continua neutro.
  A 024 revisará, como já previsto no roadmap, o acesso à trajetória da 021 (FR-001, FR-002,
  E2) e da 022 (FR-001).
- **Reversão.** Se a hipótese falhar, ou se o Ifes adotar outro Portal, a camada sai sem
  migração no núcleo. O contrato serializável da narrativa (021) e a sessão (018) passam a ser
  as fronteiras de integração.
