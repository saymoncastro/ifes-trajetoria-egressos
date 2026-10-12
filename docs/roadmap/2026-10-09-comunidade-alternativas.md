# Comunidade no Portal do Egresso — alternativas concretas

- **Data.** 2026-10-09. **Revisão de 2026-10-11:** visão da Comunidade em três dimensões,
  alternativa F (encontros propostos por egressos), divisão de E em E1 e E2 e fundamentação
  conferida. Está [no fim do documento](#revisão-de-2026-10-11-a-visão-da-comunidade); o
  texto de 2026-10-09 fica como histórico.
- **Natureza.** Análise de produto para decisão do solicitante. **Não é spec** e nenhuma
  alternativa entra em código a partir deste documento.
- **Por que existe.** O solicitante vê o Portal como relação nos dois sentidos, com
  comunidade, pertencimento e participação. Hoje a palavra "comunidade" é vedada no Portal
  (ADR 0009, decisão 7), porque sugeria uma rede que não existe. O roadmap só prevê a
  "comunidade agregada", que depende de decisões institucionais (§6, "fora da camada
  Portal"). Este documento detalha o que "comunidade" pode ser na prática, para que a
  palavra só volte quando houver uma experiência concreta por trás dela.

## O que já foi decidido e continua valendo

- Sem comparação social nem indicadores do tipo "72 conectados", "sua turma de 2017" ou
  "geração 2008" (auditoria de 2026-10-02, §5; roadmap, tabela do mockup).
- Sem perfil público, pareamento entre pessoas ou contato direto entre egressos na S3
  (roadmap, S3, "Fica fora").
- Dado pessoal, publicação e consentimento seguem a Constituição XVI e XVII: o que não está
  definido pela instituição é `DECISÃO PENDENTE`, nunca inferido.

## Alternativas

| | O que o egresso recebe | Depende de | Decisões necessárias | Custo | Risco principal |
|---|---|---|---|---|---|
| **A. Encontros de egressos** | Convites para encontros, palestras e eventos de egressos da sua unidade ou do seu curso | **Já existe**: Oportunidade da 025, categoria "Eventos", com público por unidade e curso | Só o vocabulário: admitir "comunidade" ou "egressos" no título desse tipo de conteúdo (revisão da decisão 7) | Muito baixo | Portal vazio se as unidades não divulgarem (o mesmo risco da 025) |
| **B. Histórias de egressos** | Ler trajetórias de outros egressos do Ifes, publicadas com consentimento; e ter a própria história publicada, se quiser | **026**: a forma "contar a própria história" é a porta de entrada. Precisa de curadoria pela unidade e de um conteúdo publicado novo | Termo de publicação versionado (XVII); retirada da publicação; uso de imagem (DP-2106); quem aprova o texto; base legal de publicação | Médio: um conteúdo novo, curado, com consentimento | Exposição de dado pessoal; expectativa de publicação que não acontece |
| **C. Retratos agregados** ("comunidade agregada" do roadmap) | Saber, em números agregados, o que egressos do seu curso ou unidade fazem hoje: área de atuação, continuidade de estudos | Resultados de Campanha encerrada com snapshot (012); limiar de exibição | DP-1101 e DP-2105 (limiar); autorização para publicar; DP-2107 (dado declarado) | Médio a alto | Reidentificação em recortes pequenos; parecer comparação social |
| **D. Canais oficiais por unidade ou curso** | Saber onde estão os grupos e canais oficiais de egressos (por exemplo, a página da coordenação ou um grupo moderado pela unidade) | Um conteúdo curado simples, como a Oportunidade, mas permanente | Quais canais são oficiais e quem os modera (governança da unidade); DP-2009 se o canal for WhatsApp | Baixo no sistema; alto na operação | Canal sem moderação; o Ifes responder pelo que acontece fora do sistema |
| **E. Rede entre egressos** (diretório, conexões, mentoria entre pares) | Encontrar e falar com outros egressos | Perfil público, busca, mensagens, moderação, denúncia, segurança | Exposição de dados; moderação; base legal; responsabilidade institucional | Alto | Privacidade, moderação e o Portal virar uma rede social a manter |

> **2026-10-11.** E foi dividida em **E1** (reencontro voluntário) e **E2** (rede social), e
> entrou a alternativa **F** (encontros propostos por egressos). Ver a revisão no fim.

## Recomendação

1. **A agora, sem código:** é a única que já existe. A mudança é de linguagem: chamar de
   encontros de egressos o que a 025 já divulga. Ela pede uma revisão pequena da decisão 7,
   para admitir "comunidade" ou "egressos" no rótulo de eventos de egressos.
2. **B depois da 026:** a contribuição "contar a própria história" é a entrada natural, e a
   unidade decide o que publica. Precisa de spec própria, com termo de publicação.
3. **D quando uma unidade tiver um canal oficial moderado:** custo baixo no sistema, mas
   depende de decisão institucional sobre canais.
4. **C só depois das decisões institucionais** que o roadmap já lista.
5. **E não agora:** é outro produto, com custo e risco que o piloto não justifica.

Em todos os casos, "comunidade" volta ao texto do Portal só junto da experiência concreta que
a sustenta, e cada alternativa entra no Checkpoint 2 (valor e reciprocidade).

## Decisão de 2026-10-09 (solicitante, demonstração)

- **Começar pela A**, encontros e eventos de egressos. A categoria "Eventos" da 025 já existe,
  mas a experiência ainda precisa de conteúdo e de operação: unidades divulgando encontros de
  egressos com regularidade. O rótulo usa "egressos", que não é vedado; a palavra
  "comunidade" continua fora até haver experiência concreta, e a ADR 0009 não muda.
- **B (histórias de egressos)** é a próxima especificação candidata, depois da 026.

## Decisões para o solicitante

- Quais alternativas seguem para spec, e em que ordem.
- Se aceita revisar a decisão 7 da ADR 0009 para a alternativa A (rótulo de encontros de
  egressos), mantendo as demais vedações.
- Para B e D, quem na instituição seria consultado (CPAEG, ACS, unidades).

A ordem e a revisão da decisão 7 foram respondidas em 2026-10-09 e revistas em 2026-10-11
(abaixo).

---

## Revisão de 2026-10-11: a visão da Comunidade

- **Origem.** Decisão do solicitante, depois de dois pareceres sobre a visão de Comunidade e
  sobre encontros propostos pelos próprios egressos. Registrada também no
  [roadmap](2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md), revisão 12.
- **Natureza.** Registro de visão e de decisões de produto. **Não é spec.** Nenhuma spec é
  aberta: 030 e 031 são números reservados. Nada entra em código. *(Revisão 14 do roadmap: a
  spec da 031 foi antecipada como hipótese; a 030 continua reservada.)*
- **Preservado.** Constituição 2.1.0, ADR 0008 e ADR 0009 não mudam. Onde esta revisão muda
  uma decisão de 2026-10-09, isso é dito em "O que muda em relação a 2026-10-09".

### Visão

O Trajetória Ifes e o Portal do Egresso são componentes complementares, com a fronteira da
ADR 0008:

- **Trajetória Ifes** (núcleo): acompanhamento longitudinal, pesquisas, informação acadêmica e
  dados para a avaliação institucional.
- **Portal do Egresso** (camada de relacionamento, só na demonstração): reconhecimento da
  trajetória, oportunidades, participação e comunidade.

**A Comunidade é dimensão permanente do Portal**, com três capacidades permanentes:

| Dimensão | Finalidade | Onde se materializa |
|---|---|---|
| **Pertencimento** | Reconhecer a história do egresso e preservar o vínculo com o Ifes | Minha trajetória (021, 022); A; B |
| **Participação** | Participar de atividades e também propor encontros | 026; A; **F** |
| **Reencontro** | Antigos colegas restabelecem contato, voluntariamente | **E1** |

- A Comunidade **não** está concluída com histórias editoriais e eventos institucionais.
- Uma dimensão não substitui a outra:
  - quem quer achar um colega específico não precisa ir a um encontro;
  - quem vai a encontros não precisa aparecer num diretório;
  - quem só quer acompanhar histórias do seu campus não precisa fazer nenhuma das duas coisas.
- Curso, unidade e período são **contextos de descoberta**, não grupos sociais. Nenhuma
  entidade de grupo nasce do fato de pessoas terem o mesmo curso ou campus, e nenhum encontro
  vira comunidade permanente.

Nas duas últimas linhas da tabela abaixo, o próprio egresso produz valor para outros egressos.
É isso que separa uma comunidade de conteúdo institucional:

| Experiência | Quem produz valor | Quem recebe |
|---|---|---|
| Minha trajetória | Ifes, com dados acadêmicos | O egresso |
| Oportunidades (025) | Ifes e parceiros | O egresso |
| Histórias (B) | O egresso, com curadoria institucional | Os egressos |
| Encontros da comunidade (F) | O egresso organizador | Outros egressos |
| Encontre colegas (E1) | Os egressos que aderiram | Outros egressos |

**Fica fora (E2):** feed, comentários, curtidas, seguidores, mensagens privadas, grupos
sociais administráveis, rankings, reputação e recomendação de pessoas.

> O Trajetória acompanha a história do egresso. O Portal reconhece essa história. A
> Comunidade permite que ela continue sendo construída com outras pessoas.

### Fundamentação conferida

**PAEG** (conferida no [anexo versionado](../referencias/paeg-resolucao-cs-177-2023-anexo.pdf)).
A PAEG **não exige** estas funcionalidades nem as regulamenta. Ela fixa objetivos com os quais
elas são compatíveis. Desenvolvê-las não requer alterar a Resolução CS nº 177/2023.

- **Art. 5:** valorizar a formação social do egresso e atribuir-lhe protagonismo.
- **Art. 6:** valorizar a interação do egresso com o Instituto, para consolidar o vínculo.
  Fundamenta o pertencimento.
- **Art. 8, II e IV:** incentivar a participação e o protagonismo dos egressos em eventos e
  atividades de ensino, pesquisa e extensão; manter canal de comunicação dos egressos com o
  Instituto.
- **Art. 12:** eventos voltados aos egressos, para estimular a troca de experiência entre eles
  e a criação de associação de ex-alunos. É a única base direta para a relação **entre
  egressos**, e ela passa por eventos.
- **Art. 13:** o Portal é canal de comunicação entre os egressos e as Unidades. As
  funcionalidades listadas são exemplos ("entre outros, a serem definidos por cada unidade"),
  e a lista não é fechada. Parágrafo único: a gestão do Portal cabe à CSAEG, inclusive a
  divulgação de eventos para egressos.
- **Art. 22, III e VII** (atribuições da CSAEG): gerir o Portal na unidade; **apoiar ações,
  projetos e eventos voltados aos egressos**.
- **Art. 22, X:** disponibilizar infraestrutura para a atuação do egresso **nas pesquisas e
  eventos institucionais**. Fundamenta apoio a eventos institucionais. **Não** autoriza por si
  só o uso de infraestrutura do Ifes em encontros organizados de forma autônoma por egressos.
- **Competências de articulação (Arts. 2, 14, 18, 21, 22 e 26):**
  - a PAEG é executada pelas unidades e pela Proex (Art. 2), que coordena a política e
    alimenta o Portal (Art. 14);
  - na unidade, a diretoria de pesquisa, pós-graduação e extensão, ou equivalente, coordena a
    PAEG e propõe ações de aproximação (Art. 18, I e II);
  - a CPAEG planeja a política e atua em consonância com as CSAEG (Art. 21, I e III);
  - as CSAEG regulamentam suas atividades com base nas diretrizes da CPAEG (Art. 22, XI);
  - os casos omissos são resolvidos pela CPAEG com a pró-reitoria competente (Art. 26).
  A PAEG não proíbe encontros entre campi, mas também não diz quem os autoriza: é D8.
- **Correção.** O Art. 21, VII é atribuição da CPAEG: propor a integração do mercado e da
  comunidade local com as associações de egressos. Ele não fundamenta a integração do Portal
  com associações.
- **Lacuna.** A PAEG não atribui a ninguém a moderação de encontros propostos por egressos
  (F) nem a mediação de contato entre egressos (E1). É `DECISÃO PENDENTE` (D8 do roadmap),
  definida institucionalmente antes de uso real e sem criar agora fluxo burocrático próprio.

**Pesquisa de Acompanhamento de Egressos, Versão 2025**
([registro de referência](../referencias/pesquisa-acompanhamento-egressos-2025.md)):

- 13,3% dos **participantes da pesquisa** informaram manter alguma relação com a instituição
  depois de concluir o curso. O resultado vale para quem respondeu, não para toda a população
  de egressos;
- encontros anuais e grupos de ex-alunos autogeridos são valiosos, mas insuficientes;
- recomendações: grupos temáticos, eventos periódicos, espaços de escuta, participação em
  ensino, pesquisa e extensão, e divulgação de histórias.

### Alternativas revistas

As letras de 2026-10-09 são mantidas. C e D já tinham significado, por isso os encontros
propostos por egressos são **F**.

| | Capacidade | Situação em 2026-10-11 |
|---|---|---|
| **A** | Divulgação de eventos institucionais (categoria "Eventos" da 025) | **Preservada.** Divulgação curada que aponta para a página oficial. Não é encontro proposto por egresso |
| **B** | Histórias de egressos | **Spec candidata, número 030** |
| **C** | Retratos agregados | Inalterada: depende de D6, DP-1101, DP-2105 e DP-2107 |
| **D** | Canais oficiais por unidade ou curso | Inalterada. Integração possível, sem duplicar o que já existe |
| **E1** | Reencontro voluntário: diretório opt-in e solicitação de contato com aceite | **Capacidade permanente, no horizonte**, com as condições abaixo |
| **E2** | Rede social | **Fora** |
| **F** | Encontros da comunidade, propostos por egressos | **Spec candidata, número 031.** Preferência funcional do solicitante |

### Direção registrada por capacidade

São insumos das specs, não requisitos aprovados. Cada spec confirma, revê ou registra como
`DECISÃO PENDENTE`.

**F — Encontros da comunidade (031)**

> **Revisão 14 do roadmap (2026-10-11).** A
> [spec da 031](../../specs/031-encontros-propostos-egressos/spec.md) e o
> [protótipo estático](../../specs/031-encontros-propostos-egressos/prototipo/index.html)
> foram antecipados como hipótese, sem implementação. A spec confirma a direção abaixo. Os
> pontos que ela revê ou detalha são cinco:
> - a página sem sessão é neutra (DP-3102);
> - depois da publicação, data, horário e link na mesma plataforma são correção operacional,
>   e as demais mudanças passam por nova análise;
> - a responsabilidade de moderação sai do público (H-3102), como hipótese da demonstração;
> - a Denúncia é registro mínimo da camada, sem sistema de atendimento;
> - nome de apresentação e origem do organizador seguem a
>   [ADR 0010](../adr/0010-dado-de-egresso-visivel-a-outros-egressos.md). O E1 continua
>   precisando de ADR própria.

- **O que é.** Um egresso identificado, com ao menos uma Conclusão Acadêmica, propõe um
  encontro **virtual** com título, descrição, data, horário, público e link externo de
  videoconferência. Vale qualquer plataforma, sem integração.
- **MVP:**
  - página do encontro;
  - confirmação "Vou participar", que não comprova presença;
  - compartilhamento do endereço da página;
  - cancelamento pelo organizador e pelo participante;
  - arquivo `.ics` que aponta para a página do encontro, e não para o link da reunião. Uma
    mudança de horário não atualiza o calendário de quem já baixou, e isso é dito na tela.
- **Público.** Não fica restrito automaticamente aos cursos e unidades do organizador:
  - encontros temáticos e interdisciplinares, inclusive entre campi, são admitidos;
  - o vínculo acadêmico identifica a **origem** do organizador, mas não limita o público;
  - cada recorte de público tem uma responsabilidade de moderação definida (D8).
- **Moderação.**
  - Institucional e proporcional, **antes da publicação**.
  - Recusa e retirada com motivo, e canal de denúncia.
  - A distinção é visível: "Evento do Ifes" (A) e "Encontro proposto por egresso" (F).
    Divulgar um encontro não torna o Ifes seu organizador.
- **Identidade.** Autenticação, confirmação do vínculo acadêmico e moderação de conteúdo são
  controles distintos, e a moderação **não substitui** a identidade. A garantia exigida do
  organizador para uso real é proporcional ao risco e está ligada ao DP-1808, sem presumir um
  mecanismo.
- **Privacidade.**
  - Sem lista nominal de participantes e sem contato exposto.
  - A contagem de confirmações fica restrita ao organizador e à moderação.
  - O link da reunião só aparece a quem confirmou e está com sessão.
  - Termos do organizador e da participação são versionados (XVII). Eles registram ciência e
    adesão, mas **não definem a base legal** do tratamento, que é D9. O mesmo vale para a
    retenção das confirmações.
- **Dado operacional, não analítico.** Confirmações servem ao funcionamento do encontro. Não
  entram em snapshot, exportação nem indicador de acompanhamento (ADR 0008).
- **Fora do MVP:**
  - encontros presenciais, que seguem pela A com apoio da CSAEG (Art. 22, VII);
  - chat, comentários, curtidas e contador público;
  - notificações automáticas;
  - integração com videoconferência.
- **Salas da RNP.** O egresso não cria sala no ConferênciaWeb: salas são criadas por usuários
  da instituição, e o uso deve estar alinhado a ensino, pesquisa e inovação (termos de uso do
  serviço). Uma sala institucional pode ser **articulada com a unidade responsável**,
  observados disponibilidade, autorizações, finalidade da atividade e condições de uso do
  serviço. O Art. 22, X não cria autorização automática para encontros autônomos. O padrão do
  MVP continua sendo o link externo informado pelo organizador.

**B — Histórias de egressos (030)**

- **Caráter humano e editorial.** Histórias de experiências, trajetórias de vida,
  contribuições sociais e relações com o Ifes, e não só de sucesso profissional.
- A entrada é a forma "Contar sua história" da 026, que já existe.
- Curadoria institucional, autorização de publicação com termo versionado (XVII) e retirada
  pelo próprio autor.
- Sem ranking nem comparação social. Sem fotografia até a autorização de uso de imagem
  (DP-2106).

**E1 — Reencontro voluntário**

- Adesão voluntária ao diretório, sem inclusão automática, com controle do que é mostrado.
- Nenhuma exposição automática de e-mail ou telefone.
- Solicitação de contato sujeita a aceite, com recusa, bloqueio, retirada do diretório e
  denúncia.
- Antes de uso real:
  - identidade reforçada (DP-1808);
  - base legal e retenção (D9). A adesão voluntária não substitui a base legal;
  - responsável por denúncias (D8);
  - ADR própria, porque é a primeira vez que a camada mostra dado de um egresso a outro.
- **Encontros (F) não substituem o E1.**

### Experiência visual

- O Portal deve transmitir identidade institucional, pertencimento, acolhimento e
  continuidade do vínculo, e não a aparência de sistema administrativo. A composição das
  histórias, dos encontros e do reencontro recebe o mesmo cuidado que a modelagem funcional.
- **A ADR 0009 continua valendo:**
  - camada visual própria;
  - celular como referência de qualidade, com composição própria para o desktop;
  - veto à nostalgia (decisão 5);
  - fotografia de pessoas só com autorização;
  - nada que não existe apresentado como disponível.
- O instrumento continua mobile-first e intacto.
- **Protótipo estático da Comunidade:**
  - experiência visual substantiva, com composição editorial, e não uma sequência de cards
    administrativos;
  - cobre Histórias, Encontros e Encontre colegas, com o que é conceitual marcado.
- **Navegação.** "Descubra", "Participe" e "Encontre colegas" partem das necessidades do
  egresso, e não das entidades da aplicação. São **hipóteses de protótipo**, não requisitos.
  O protótipo resolve a relação com "Contribuir com o Ifes" (026) e com Oportunidades (025).

### Critério para a palavra "comunidade"

- **Nas telas servidas**, entra com a primeira capacidade em que egressos produzem valor para
  outros egressos (F ou E1). A spec que a implementar revisa de forma explícita a decisão 7 da
  ADR 0009 e as vedações da 024, da 028 e da 029. Histórias e eventos institucionais, sozinhos,
  não bastam.
- **No protótipo estático e no Checkpoint 2**, a palavra pode aparecer, com o que é conceitual
  marcado.
- Continuam valendo as demais vedações: "turma", "geração", "conectad", contagens de egressos
  e comparação social.
- É uma **decisão de experiência**, e não uma exigência da PAEG.

### Outras soluções institucionais: ponto de atenção, não bloqueio

- **A Constituição VI continua valendo.** As specs 031 e E1 respondem às cinco perguntas,
  inclusive "existe ou está prevista solução institucional mais adequada?".
- **Já conhecido:**
  - o aplicativo da DIREC voltado a estudantes e egressos (relatório de 2025, p. 22);
  - grupos de ex-alunos autogeridos;
  - encontros anuais em campi.
- **Decisão do solicitante.** Não consultar a DIREC agora e não condicionar a essa análise a
  evolução nem a validação na demonstração. Complementaridade, interoperabilidade e governança
  são examinadas antes de uso real (D10). Nada é decidido sobre implantação definitiva ou
  substituição de sistemas.

### Sequência

1. 029 integrada (PR #58).
2. Checkpoint 1 (024 e bloco P da 029).
3. Protótipo estático da Comunidade.
4. Checkpoint 2, com o bloco Comunidade definido no roadmap, §7.
5. Decisão entre 030 e 031, comparando valor para o egresso, complexidade, governança e
   esforço. A preferência é pela 031. A 030 vem antes se houver impedimento relevante à 031.
6. E1 no horizonte, com as condições acima.

> **Revista em 2026-10-11** ([roadmap, revisão 13, §13.3](2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md#133-sequência)).
> A 032 (convergência C) entrou depois do passo 1. A sequência vigente é: consolidação da
> C → acessibilidade → Checkpoint 1 → ajustes → protótipo estático da Comunidade →
> Checkpoint 2 → decisão entre 031 e 030. O bloco Comunidade está no
> [protocolo do Checkpoint 2](../validacao/checkpoint-2/protocolo.md), e a recomendação da
> próxima spec, com o escopo mínimo da 031 e os motivos que poderiam pôr a 030 antes, está
> no [roadmap, §13.5](2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md#135-próxima-spec-recomendação).
> A lista acima fica como histórico.

### O que muda em relação a 2026-10-09

- **"B é a próxima especificação candidata"** foi substituída. A ordem entre 030 e 031 sai do
  Checkpoint 2, com preferência pela 031.
- **"E não agora"** foi revista. E se divide em E1, capacidade permanente no horizonte com
  condições, e E2, que continua fora.
- **"Começar pela A"** foi mantida como divulgação institucional. F é capacidade distinta.
- **Critério da palavra "comunidade".** Antes era "só junto da experiência concreta"; agora é
  "com F ou E1".
- Não mudam: Constituição, ADR 0008, ADR 0009 e as vedações em vigor.

### Ajustes de 2026-10-11, depois do parecer normativo

Um parecer sobre esta revisão, confrontada com a PAEG, não encontrou incompatibilidade
normativa direta e pediu quatro ajustes, aplicados acima:

1. Art. 22, X: apoio a eventos institucionais, sem autorização automática de infraestrutura
   para encontros autônomos. A sala institucional é articulada com a unidade.
2. Competências dos Arts. 2, 14, 18, 21, 22 e 26 acrescentadas à fundamentação de D8, sem
   criar fluxo agora.
3. Termos e adesão não substituem a base legal de cada tratamento: história, encontro,
   confirmação e diretório podem ter bases diferentes (D9).
4. O resultado de 13,3% foi delimitado aos participantes da pesquisa de 2025.

**Distinção que permanece:** solução em desenvolvimento e validação, com dados fictícios, não
é serviço institucional em operação com dados reais. D8 e D9 não bloqueiam specs nem a
demonstração. Bloqueiam o uso real.
