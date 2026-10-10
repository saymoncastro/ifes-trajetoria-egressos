# Feature Specification: Página pública do Portal — valor percebido e primeiro acesso

**Feature Branch**: `claude/029-pagina-publica`
**Created**: 2026-10-09
**Status**: Especificação para avaliação, com "Contribuir com o Ifes" incluído em 2026-10-09
(026 T024), depois da 026 integrada na demonstração. **Implementação autorizada pelo
solicitante em 2026-10-10, na demonstração** (roadmap, revisão 11); resultados em
[validacao.md](validacao.md). Checkpoint 1 **NÃO APLICADO**: vem depois desta implementação.
**Input**: Pedido do solicitante em 2026-10-09, depois de um parecer externo sobre a página
pública da 028. Reformulação visual e comunicacional substantiva da página pública, sem
capacidade nova e sem revogar decisão da [ADR 0009](../../docs/adr/0009-camada-visual-do-portal.md).
Sequência autorizada: spec → protótipos → Checkpoint 1 → ajustes → implementação.
**Revista em 2026-10-09** (roadmap, revisão 10): 026 implementada → 029 atualizada com
"Contribuir com o Ifes" → 029 implementada, mediante autorização → Checkpoint 1 (024 e
bloco P) sobre a experiência implementada → ajustes → Checkpoint 2.

**Reposicionamento (2026-10-09, solicitante).** O Portal é uma relação nos dois sentidos: o
Ifes oferece (oportunidades, formação continuada, eventos) e o egresso participa e contribui.
A primeira versão desta spec centrava a página na trajetória e no card. Agora a página abre
pela relação, destaca oportunidades e participação, e apresenta trajetória e card como partes
da experiência. Continua mostrando **só o que está disponível**: sem "Em construção" e sem
alterar a ADR 0009. A contribuição do egresso (Volte ao Ifes) entra na página porque a
[026](../026-volte-ao-ifes/spec.md) já existe na demonstração (revisão de 2026-10-09, T024). O que "comunidade" pode ser está em
[alternativas de comunidade](../../docs/roadmap/2026-10-09-comunidade-alternativas.md).

## Contexto e dependências

A 028 implementou a página pública prevista na ADR 0009 (decisão 6). Ela é correta e
acessível, mas organizada a partir das funcionalidades: título que descreve um registro
("Veja o que o Ifes registra sobre a sua formação"), quatro cartões iguais, três passos em
texto, a pesquisa explicada e um botão genérico ("Entrar no Portal"). O e-mail aparece como
benefício, embora sirva à pesquisa. A crítica do solicitante: a página não desperta
interesse nem comunica o valor concreto do Portal para o egresso.

Esta feature muda só a apresentação e a comunicação de `/` sem sessão. Não muda o que o
Portal oferece.

| Fato verificado | Fonte | Consequência para a 029 |
|---|---|---|
| `/` sem sessão mostra a página pública; com Pessoa ou declarante, vai ao destino fixo; sem cache compartilhado | 028 FR-006; `portal/views.py` (`entrada`, `never_cache`) | Mantidos. Só o template e o estilo da página mudam |
| A página pública não consulta Pessoa, não coleta dado e não usa JavaScript; o convite (`/acesso/`) não passa por ela | 028 FR-008; ADR 0009 dec. 6 | Mantidos. A demonstração usa só dados fictícios fixos |
| Card de exemplo gerado pelo código da 021, com selo "Exemplo com dados fictícios" | `portal/exemplo.py`; 028 FR-007 | Reaproveitado. Nada de exemplo é apresentado como real |
| Só capacidades existentes: trajetória, card, oportunidades (quando houver), contato, pesquisa; sem área inexistente | ADR 0009 dec. 6; 024 FR-021; 028 FR-007 | O vídeo fica fora, porque depende do renderizador (`renderizador.disponivel()`) |
| Vocabulário da página pública: sem contagem de egressos, "%", "turma", "geração", "conectad", "comunidade", "Olá", "Volte ao Ifes"; "Oportunidades" e "pesquisa" admitidos | ADR 0009 dec. 7; 028 FR-013 | Mantido e verificado em teste |
| Textos de oportunidade sem urgência ("últimas vagas", "não perca"), sem "recomendado" nem "selecionado para você" | 025 (vocabulário dos textos do sistema) | Vale para o exemplo de oportunidade da demonstração |
| A entrada não é apresentada como login, conta nem "acesso seguro" | 018 FR-061 | As chamadas usam "Conhecer o Portal" e "Confirme seus dados" |
| O e-mail tem uma finalidade declarada: contato do Ifes sobre pesquisas | 020 FR-012 | A página diz exatamente isso, como forma de participação, não como benefício |
| Textos provisórios da equipe, sem slogan; nome e linguagem definitivos com a ACS | ADR 0009 dec. 6; D2; DP-801 | "Sua história com o Ifes continua" segue fora |
| Fotografia só com licença da ACS; veto à nostalgia | ADR 0009 dec. 5; DP-2106 | Composição sem fotografia; nenhum espaço "aguarda ACS" no produto (028 FR-003) |
| Layout próprio do Portal, cards, grade e hero admitidos; `system-ui`; h1 de 40 px a partir de 768 px e 28 px no celular; verde de ação só no Portal | ADR 0009 dec. 1, 3, 4 e esclarecimento de 2026-10-09 | A composição pode mudar por inteiro dentro desses tokens |
| O celular é a referência de qualidade; o desktop tem composição própria e critérios medidos | Constituição XXI; ADR 0009 dec. 2 | A página precisa ser excelente nas duas pontas |
| Telemetria e rastreamento estão fora; conversão não é critério do Checkpoint 1 | 028 (fora de escopo); 024 SC; Constituição XVI | Nenhuma medição de uso nesta feature |
| Checkpoint 1: protocolo escrito antes do teste, critérios SC-008 a SC-016 e limiar "4 de 5" proposto (confirmação pendente em P1) | `specs/024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md` | Os critérios da 024 ficam intactos; a 029 acrescenta um bloco anterior, sobre a página pública |

**Achado no protocolo da 024.** Ele é anterior à 025 e à 028. Dois trechos ficaram
desatualizados: "Oportunidades e Volte ao Ifes não aparecem no produto" (Oportunidades
existe desde a 025) e a tarefa 1, que entregava o endereço raiz esperando o formulário
(agora a raiz mostra a página pública). A revisão do roteiro corrige os dois sem mexer nos
critérios ([checkpoint-pagina-publica.md](checkpoint-pagina-publica.md)).

## Artefatos para avaliação

- [Protótipo comparativo](prototipo/index.html): atual (028) × proposta, a 375, 1024 e 1440
  px e nas primeiras telas, com os critérios medidos e o contraste dos pares novos. A
  [proposta](prototipo/proposta.html) é o HTML servido pela demonstração com o conteúdo
  principal trocado, gerado por [`prototipo/gerar.py`](prototipo/gerar.py) a partir do
  código (card de `portal/exemplo.py`, frases da montagem da 021).
- [Bloco P do Checkpoint 1](checkpoint-pagina-publica.md) e a
  [ficha](checkpoint/ficha-bloco-p.md); nota de revisão no protocolo da 024.

## User Scenarios & Testing

### US1 — Entender em poucos segundos por que vale entrar (P1)

Um egresso recebe o endereço do Portal por uma mensagem e abre no celular. Sem rolar a
tela, entende o que é o lugar e pelo menos uma coisa concreta que vai encontrar lá. A
página não promete nada que o Portal não ofereça.

**Why this priority**: é o problema apontado pelo solicitante. Sem interesse no primeiro
contato, o resto do Portal não é visto.

**Independent Test**: teste de 5 segundos do Checkpoint 1 (bloco P) e medição da primeira
tela a 375×812, 1280×720 e 1440×900.

1. **Dado** um visitante sem sessão a 375×812, **quando** a página carrega, **então** vê o
   título, a frase de valor e a chamada principal sem rolar.
2. **Dado** o mesmo visitante a 1280×720, **quando** a página carrega, **então** vê também
   a composição visual da relação (oportunidade e trajetória de exemplo).
3. **Dado** qualquer texto da página, **quando** comparado com o que o Portal oferece,
   **então** nenhum descreve serviço, rede, benefício ou comunicação que não exista.

### US2 — Ver como funciona antes de informar dados (P1)

O visitante quer saber o que encontra antes de digitar CPF e data de nascimento. Uma ação
secundária leva a exemplos na própria página: oportunidades, a trajetória reconhecida e o
card, tudo com dados fictícios e identificado como exemplo.

**Why this priority**: pedir CPF antes de mostrar valor é a maior fricção do primeiro
acesso. Mostrar a experiência com dados fictícios reduz a incerteza sem coletar nada.

**Independent Test**: seguir "Ver como funciona" com teclado e sem JavaScript; conferir os
selos de exemplo e que nenhum dado vem do banco.

1. **Dado** um visitante, **quando** aciona "Ver como funciona", **então** chega à
   demonstração na mesma página, por âncora, sem JavaScript.
2. **Dado** a demonstração, **quando** exibida, **então** cada peça traz o selo de exemplo e
   usa os componentes reais da 025 e da 021 (item de oportunidade, linha do tempo, card).
3. **Dado** o exemplo de oportunidade, **quando** exibido, **então** não tem link para um
   site real, não usa vocabulário vedado pela 025 e diz que oportunidades só aparecem
   quando o Ifes divulga alguma para a formação.

### US3 — Entrar com confiança, ou só participar (P2)

Quem decide entrar encontra a chamada no topo e de novo no fim. A página diz de onde vêm
as informações e que a pesquisa e o e-mail são opcionais, como formas de participação.

**Independent Test**: percorrer a página com teclado; entrar pela chamada e chegar a
`/entrar/`; conferir os textos de participação contra 020 FR-012.

1. **Dado** um visitante, **quando** aciona "Conhecer o Portal" no topo ou no fim,
   **então** chega a `/entrar/`, que não muda.
2. **Dado** a seção de participação, **quando** lida, **então** apresenta a pesquisa e o
   e-mail como opcionais e com a finalidade declarada, sem listá-los como benefícios.
3. **Dado** um egresso que chega por convite de Campanha (`/acesso/`), **quando** se
   identifica, **então** vai direto à pesquisa, sem ver esta página.

### Edge Cases

- **Visitante com sessão:** `/` continua levando ao Início ou à declaração; a página
  pública não aparece.
- **Portal desligado** (`TRAJETORIA_PORTAL=0`): a página não existe; a raiz segue o
  comportamento anterior.
- **Sem rasterização:** o card de exemplo aparece em SVG, como na 028.
- **Fonte a 200% e 320 px:** sem rolagem horizontal; a demonstração vira uma coluna.
- **Movimento reduzido:** nenhuma animação é necessária; se houver transição, ela respeita
  `prefers-reduced-motion`.
- **Leitor de tela:** as peças de demonstração são anunciadas como exemplo, com texto
  alternativo; o selo não depende de cor.

## Requirements

### Functional Requirements

**Escopo e fronteira**

- **FR-001 [Arquitetura]**: A feature DEVE alterar apenas o template, o estilo e os textos
  da página pública (`/` sem sessão, Portal ligado). Rotas, destinos, `never_cache`,
  `/entrar/`, `/acesso/`, Início, Minha trajetória, Meu e-mail e Oportunidades NÃO DEVEM
  mudar.
- **FR-002 [Arquitetura]**: NÃO DEVE haver mudança na identificação, nos dados acadêmicos,
  na finalidade do contato, na pertinência ou curadoria de oportunidades, nas pesquisas,
  em modelo, migração, dependência, CDN, fonte externa, JavaScript, telemetria ou
  rastreamento.
- **FR-003 [Arquitetura]**: A página NÃO DEVE consultar Pessoa, Conclusão, Oportunidade ou
  contato. A demonstração usa só dados fictícios fixos no código (028 FR-008).

**Comunicação de valor**

- **FR-004 [Hipótese]**: A página DEVE apresentar o Portal como **relação nos dois
  sentidos**, nesta ordem: a relação (abertura) → o que o Ifes oferece (Oportunidades) →
  como o egresso participa → a trajetória com o Ifes (formações reconhecidas e card) →
  chamada final. O título comunica o sentido do lugar; a frase de apoio, o que existe hoje.
- **FR-005 [Hipótese]**: O que a página apresenta como disponível DEVE ser só isto:
  1. **Ifes → egresso:** oportunidades que o Ifes divulgar para a formação (cursos,
     eventos, programas, carreira), **quando houver**, com o motivo e a página oficial;
  2. **egresso → Ifes:**
     - oferecer uma contribuição (mentoria, experiência, vaga, pesquisa e extensão,
       parceria, a própria história) à unidade da formação, acompanhar se o contato foi
       registrado e retirar quando quiser (026), sem prazo nem resposta garantidos;
     - participar da pesquisa de acompanhamento, contando como a trajetória seguiu, e
       deixar um e-mail para os convites (opcionais);
  3. **trajetória:** ver as formações que o Ifes reconhece, com a origem, e guardar ou
     compartilhar o card.
- **FR-006 [Arquitetura]**: A seção de participação DEVE apresentar a pesquisa e o e-mail
  como opcionais, o e-mail com a finalidade declarada na 020 (convite para pesquisas de
  acompanhamento). "Contribuir com o Ifes" (026) abre essa seção, com o mesmo peso de
  Oportunidades: texto próprio e um exemplo fictício de "Suas contribuições". O texto diz
  quem recebe, que o contato é pelo e-mail informado na contribuição, que não há prazo
  garantido e que se pode retirar. *(Revisado em 2026-10-09, T024 da 026: antes, a página
  não mencionava a contribuição.)*
- **FR-007 [Arquitetura]**: Os textos DEVEM respeitar as vedações da ADR 0009 (decisão 7),
  da 025 e da 018 FR-061, e NÃO DEVEM usar slogan. São provisórios da equipe, para
  aprovação da ACS com a CPAEG antes de uso real (D2, DP-801).
- **FR-008 [Hipótese]**: Chamada principal "Conhecer o Portal", para `/entrar/`,
  no topo e no fim. Chamada secundária "Ver como funciona", para a demonstração, por
  âncora. Perto da chamada principal, uma linha diz o que será pedido (CPF e data de
  nascimento).

**Demonstração**

- **FR-009 [Hipótese]**: A página DEVE mostrar exemplos, cada um com o selo "Exemplo com
  dados fictícios", na ordem do FR-004:
  1. itens de oportunidade no formato da 025 (por exemplo, um curso e um encontro de
     egressos), com explicação de pertinência, sem link para site real;
  2. linha do tempo de formações com a origem "Registro do Ifes", no formato do Início;
  3. o card de exemplo gerado pela 021 (`portal/exemplo.py`), ao lado da linha do tempo.
- **FR-010 [Arquitetura]**: Os dados da demonstração DEVEM ser os mesmos do card de
  exemplo (formações fictícias de `portal/exemplo.py`), para que as peças contem uma só
  história. O exemplo de oportunidade é fictício e fixo no código.

**Experiência visual**

- **FR-011 [Hipótese]**: A composição DEVE ser reformulada, não só reordenada. O card não é
  a peça central da abertura. No desktop: título e uma composição visual da relação
  (oportunidade e trajetória de exemplo) dividem a primeira tela; seções alternam composições
  (não uma grade de cartões iguais); a demonstração usa os componentes reais em escala
  legível. No celular: uma coluna na ordem de leitura, com a chamada principal na
  primeira tela.
- **FR-012 [Arquitetura]**: A composição DEVE usar só os tokens da 015 e da camada do
  Portal (ADR 0009): `system-ui`, h1 de 40 px a partir de 768 px e 28 px abaixo, verde
  de ação, verde profundo e creme. A assinatura oficial não muda. Nenhum espaço de
  fotografia de protótipo vira produto.
- **FR-013 [Arquitetura]**: Acessibilidade da 015 e da 028: um h1, ordem de leitura igual à
  visual, foco visível, alvos ≥ 44×44 px nas ligações isoladas, contraste AA medido nos
  pares novos, nada comunicado só por cor, sem JavaScript.

### Requisitos revisados

| Origem | Revisão |
|---|---|
| 028, `publico.html` e textos da página pública | Substituídos pela composição e pelos textos desta feature. FR-006 a FR-008 e FR-013 da 028 continuam valendo |
| 024, protocolo do Checkpoint 1 | Acrescenta o bloco P (página pública) antes da tarefa 1 e corrige dois trechos desatualizados. Critérios SC-008 a SC-016, limiar e leitura do resultado **não mudam** |

## Success Criteria

### Medidos (protótipo e, depois, implementação)

- **SC-001**: A 375×812, sem rolar: h1, frase de valor e chamada principal.
- **SC-002**: A 1280×720 e 1440×900, descontada a faixa de demonstração: h1, frase de
  valor, chamada principal e a composição visual da abertura.
- **SC-003**: Sem rolagem horizontal de 320 a 1440 px, com fonte a 100% e 200%.
- **SC-004**: Conteúdo de pelo menos 1000 px entre 1280 e 1440 px; a demonstração usa duas
  colunas ou mais a partir de 1024 px e uma abaixo de 768 px.
- **SC-005**: Texto corrido com até cerca de 70 caracteres por linha.
- **SC-006**: Um h1; alvos ≥ 44 px; contraste ≥ 4,5:1 em todos os pares de texto novos.
- **SC-007**: Nenhuma ocorrência do vocabulário vedado (ADR 0009 dec. 7; 025; 018 FR-061)
  no texto visível, verificada por teste na implementação.
- **SC-008**: Toda peça de demonstração tem o selo de exemplo; nenhum link da página leva a
  área inexistente ou a site externo real.
- **SC-009**: Comparação lado a lado, atual (028) × proposta, a 375, 1024 e 1440 px e nas
  primeiras telas, aprovada pelo solicitante.

### Qualitativos (Checkpoint 1, bloco P)

Evidência qualitativa com 5 a 8 participantes. A maioria é **referência**, não validação
estatística. Nenhuma resposta é tratada como conversão ou retenção.

- **P-01 — Benefício real em 5 segundos**: depois de ver a primeira tela por 5 s, a pessoa
  cita ao menos uma coisa real do FR-005 (oportunidades, contribuir, participação ou
  trajetória).
  Referência: maioria.
- **P-02 — Nenhuma função inexistente**: anotado **separadamente** do P-01. A pessoa não
  atribui ao Portal função que não existe (rede, vagas garantidas, serviço, comunidade,
  mensagens, programa de mentoria, resposta ou contato garantido a quem contribui). Referência: nenhum participante. Uma atribuição já pede revisão do texto.
- **P-03 — O que espera encontrar**: a descrição livre do que haverá depois de entrar
  corresponde ao que existe.
- **P-04 — Interesse declarado**: diz se entraria e por quê. É intenção declarada; não
  conta como acesso.
- **P-05 — Motivo para voltar**: o que justificaria um acesso futuro. Serve ao roadmap; a
  página não é avaliada por isto.
- **P-06 — Confiança e identidade**: reconhece a página como do Ifes e diz se confiaria
  em informar CPF e data de nascimento.
- **P-07 — Comparação**: entre a página atual e a proposta, qual comunica melhor o que o
  Portal oferece, e por quê. Preferência estética sozinha ("gostei") não conta.

Leitura: se o P-02 falha, o texto é corrigido antes de qualquer implementação. Se o
P-01 falha na proposta e passa na atual, a proposta não segue sem revisão. Os critérios
SC-008 a SC-016 **da 024** são lidos como no protocolo da 024, sem alteração.

## Invariantes Constitucionais Afetados

- **XIV, XXI, XX:** menos fricção antes da identificação; celular como referência e
  desktop com composição própria; acessibilidade verificada.
- **XVI, XVII:** nenhum dado pessoal, finalidade, rastreamento ou consentimento novo.
- **III, IV:** a demonstração mostra a diferença entre registro do Ifes e resposta, com a
  origem visível.
- **XXII, XXVIII, XXIX:** escopo mínimo (só apresentação); spec antes de código; textos e
  composição marcados como hipótese até o Checkpoint 1.

## Fronteira do NIAE

1. Pertence ao acompanhamento? A página apresenta a camada de relacionamento (ADR 0008).
2. É necessária à coleta? Não; o convite não passa por ela.
3. Há solução institucional definitiva? Não; nome, linguagem e fotografia seguem com a ACS.
4. Integração basta? Sim; nenhuma integração nova.
5. Aumenta acoplamento? Não; reaproveita `portal/exemplo.py` e os componentes do Portal.

## Out of Scope

Slogan; fotografias; histórias de egressos; novas finalidades do e-mail; comunicação sobre
oportunidades ou atividades; telemetria, métricas de conversão ou rastreamento; teste A/B
com tráfego real; vídeo na página pública; mudanças no Início ou nas telas internas;
retenção (questão do produto, roadmap 026 e 027; a 026 é especificada à parte).

## Decisões Pendentes

- **D2, DP-801 — DECISÃO PENDENTE:** nome e linguagem definitivos, com a ACS e a CPAEG.
  Os textos da 029 são provisórios.
- **DP-2106 — DECISÃO PENDENTE:** fotografias licenciadas. A composição não depende delas.
- **Checkpoint 1, P1 e P3 da preparação da 024 — DECISÃO PENDENTE:** confirmação do limiar
  e procedimento de participação e gravação. Com mais de 5 participantes, a aplicação do
  limiar "4 de 5" aos critérios da 024 faz parte de P1, e esta feature não a decide.
- **Fidelidade no teste — Hipótese:** a proposta é avaliada como protótipo estático
  servido localmente, com a chamada levando à `/entrar/` da demonstração. A página atual é
  a da 028, servida pela demonstração.
