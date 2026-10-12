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
- **Revisão 3 (2026-10-08).** O solicitante autorizou antecipar **só a especificação** da
  S2 (Feature 025), com o Checkpoint 1 ainda não concluído. A implementação da 025
  continua condicionada à avaliação dos resultados do Checkpoint 1 (seção 6, S2).
- **Revisão 4 (2026-10-08).** Depois da
  [avaliação por IA dos checkpoints](../auditorias/2026-10-08-portal-checkpoints-avaliacao-ia.md)
  e dos ajustes da 024 que ela motivou, o solicitante autorizou antecipar também **o plan e
  as tasks** da 025. A implementação continua vedada. O Checkpoint 1 continua **NÃO
  APLICADO** (seção 6, S2).
- **Revisão 5 (2026-10-08).** O solicitante autorizou a **implementação** da 025 (código e
  migrações), só na demonstração. A condição de espera pelo Checkpoint 1 foi retirada para a
  025. O Checkpoint 1 continua **NÃO APLICADO** e a 026 continua fora (seção 6, S2).
- **Revisão 6 (2026-10-09).** Depois da
  [auditoria de direção visual](../auditorias/2026-10-08-portal-ux-direcao-visual.md), o
  solicitante aprovou a [ADR 0009](../adr/0009-camada-visual-do-portal.md): camada visual
  própria do Portal (layout, tokens, verde provisório, página pública), com o instrumento
  preservado. Próximos passos: protótipos de três direções, escolha e spec da camada
  visual. O Checkpoint 1 continua **NÃO APLICADO** e a 026 continua fora.
- **Revisão 7 (2026-10-09).** O PR #51 foi integrado e o solicitante escolheu a direção
  **B — trajetória**. A [028](../../specs/028-camada-visual-portal/spec.md) implementa
  localmente a camada visual da ADR 0009 na demonstração, com evidências e verificações
  registradas na feature. Os números 026/027 permanecem reservados ao roadmap; a escolha
  não libera esses trabalhos. Checkpoint 1 continua **NÃO APLICADO**.
- **Revisão 8 (2026-10-09).** Depois de um parecer externo sobre a página pública da 028,
  o solicitante autorizou a [029](../../specs/029-pagina-publica-portal/spec.md) até a
  spec, os protótipos comparativos e o bloco P do Checkpoint 1 (página pública), **sem**
  revogar decisões da ADR 0009 e **sem** implementação. Sequência: spec → protótipos →
  Checkpoint 1 → ajustes → implementação, mediante aprovação. Checkpoint 1 continua **NÃO
  APLICADO**; 026 e 027 continuam fora.
- **Revisão 9 (2026-10-09).** O solicitante descreveu o Portal como relação nos dois
  sentidos (Ifes oferece; egresso participa e contribui) e autorizou:
  - a **spec da 026** ([Volte ao Ifes](../../specs/026-volte-ao-ifes/spec.md)), com o
    percurso completo da contribuição, **sem implementação**;
  - o **reposicionamento da 029**: a página pública abre pela relação, destaca
    oportunidades e participação, e mostra só o que existe (sem "Em construção");
  - [alternativas concretas de comunidade](2026-10-09-comunidade-alternativas.md), só para
    avaliação.

  A ADR 0009 não muda. Checkpoint 1 continua **NÃO APLICADO**; a 027 continua fora.
- **Revisão 10 (2026-10-09).** Depois de revisar o plan, as tasks e os protótipos da 026, o
  solicitante autorizou a **implementação da 026, só na demonstração**, em branch e PR
  próprios, seguindo spec, plan e tasks (T001). Como na 025 (revisão 5), a espera pelo
  Checkpoint 1 fica retirada para a 026. A sequência passa a ser:
  1. 026 implementada;
  2. 029 atualizada com "Contribuir com o Ifes";
  3. 029 implementada, com **autorização separada, ainda não dada**;
  4. Checkpoint 1 (024 e bloco P da 029) sobre a experiência implementada, e ajustes;
  5. Checkpoint 2.

  Checkpoint 1 continua **NÃO APLICADO**; a avaliação por IA não o aprova. D4 e D5 continuam
  `DECISÃO PENDENTE` e precisam ser resolvidas antes de uso real. A 027 continua fora.

  Andamento em 2026-10-09: passo 1 concluído (026 integrada na demonstração, PR #56) e passo 2
  concluído (029 com "Contribuir com o Ifes" na spec, no protótipo e no bloco P; T024 da 026).
  O passo 3 aguarda autorização.
- **Revisão 11 (2026-10-10).** O solicitante autorizou a **implementação da 029** (página
  pública), na demonstração. Com ela, o passo 3 da revisão 10 fica concluído quando o PR for
  integrado. O próximo passo é o **Checkpoint 1** (024 e bloco P), sobre a experiência
  implementada, com o material do bloco P revisto: a 028 é mostrada pela cópia estática do
  protótipo. Checkpoint 1 continua **NÃO APLICADO**; D4 e D5 continuam pendentes.
- **Revisão 12 (2026-10-11).** O solicitante consolidou a **visão da Comunidade** e autorizou
  só a revisão documental
  ([alternativas de comunidade, revisão de 2026-10-11](2026-10-09-comunidade-alternativas.md#revisão-de-2026-10-11-a-visão-da-comunidade)):
  - a Comunidade é dimensão permanente do Portal, com três capacidades permanentes:
    pertencimento (B, Histórias), participação (**F**, encontros propostos por egressos) e
    reencontro voluntário (**E1**). A rede social (**E2**) continua fora;
  - 030 (Histórias) e 031 (Encontros) ficam **reservados, sem spec aberta**. A ordem entre as
    duas sai do Checkpoint 2, com preferência funcional pela 031;
  - o Checkpoint 2 ganha o **bloco Comunidade**, aplicado sobre um protótipo estático
    (§7);
  - decisões pendentes D8, D9 e D10 (§11.2). Outras soluções institucionais, como o
    aplicativo da DIREC citado na pesquisa de egressos de 2025, são ponto de atenção para uso
    real e não bloqueiam a demonstração (D10).

  Sequência: 029 integrada (PR #58) → Checkpoint 1 → protótipo da Comunidade → Checkpoint 2 →
  decisão entre 030 e 031. Constituição, ADR 0008 e ADR 0009 não mudam. Checkpoint 1 continua
  **NÃO APLICADO**; a 027 continua fora.
- **Revisão 13 (2026-10-11).** Depois da convergência visual C
  ([032](../../specs/032-convergencia-visual-c/spec.md), PRs #60 e #61), só documentação:
  - **estado consolidado** das entregas e das evidências técnicas, separado da validação com
    egressos, que **ainda não existe** (§13.1 e §13.2);
  - **sequência**, que substitui a da revisão 12: consolidação da C → acessibilidade →
    Checkpoint 1 → ajustes → protótipo estático da Comunidade → Checkpoint 2 → decisão entre
    031 e 030 (§13.3). A revisão 12 punha o Checkpoint 1 logo depois da 029; a 032 entrou
    antes dele;
  - **kit do Checkpoint 1** atualizado para a versão C, com o bloco P da página pública;
    **protocolo e fichas do Checkpoint 2**, escritos antes de qualquer sessão
    ([`docs/validacao/checkpoint-2/`](../validacao/checkpoint-2/protocolo.md)) (§13.4);
  - **recomendação da próxima spec:** a 031, condicionada à leitura dos dois checkpoints
    (§13.5). Nenhuma spec é aberta; 030 e 031 continuam reservadas.

  Constituição e ADR 0008 não mudam. A ADR 0009 recebe só uma nota de conciliação: a
  navegação usa "Participação", e não mais "Pesquisa" (decisão 8). Checkpoint 1 continua
  **NÃO APLICADO**; a 027 continua fora.
- **Revisão 14 (2026-10-11).** O solicitante autorizou antecipar **só a spec e o protótipo
  estático** da [031](../../specs/031-encontros-propostos-egressos/spec.md) (encontros
  propostos por egressos, alternativa F), **como hipótese, antes dos checkpoints**:
  - sem plan, tasks, código ou migração. A 030 não é aberta;
  - a **implementação** continua condicionada à leitura do Checkpoint 1 e do Checkpoint 2, em
    especial do bloco Comunidade. A escolha entre 031 e 030 continua com o solicitante depois
    dos dois (§13.5). Antecipar a spec não decide essa escolha;
  - o [protótipo](../../specs/031-encontros-propostos-egressos/prototipo/index.html) cobre só
    os Encontros (F), com organizadora, participante e moderação. Para o bloco Comunidade
    ainda faltam Histórias e Encontre colegas (§13.3, passo 5);
  - **revisão de produto da 031**, decidida pelo solicitante no mesmo dia:
    - a Denúncia é aceita como registro mínimo, sem sistema de atendimento, com canal externo
      como alternativa para uso real;
    - o público é contexto de descoberta, e não exclusividade;
    - nome de apresentação e origem do organizador, a primeira exposição de dado de um
      egresso a outro, ficam na
      [ADR 0010](../adr/0010-dado-de-egresso-visivel-a-outros-egressos.md);
    - depois da publicação, data, horário e link na mesma plataforma são correção operacional,
      e as demais mudanças passam por nova análise;
    - a moderação por CSAEG ou CPAEG continua hipótese da demonstração, e não competência
      aprovada;
  - Q8 do Checkpoint 2 fica decidida: CM-F1 a CM-F5 entram como **observações exploratórias,
    sem limiar** ([preparação](../validacao/checkpoint-2/preparacao-sessao.md));
  - as revisões de vocabulário e de navegação ficam listadas na spec, para a implementação.
    As telas servidas não mudam;
  - os achados A-01 a A-04 da versão C continuam não corrigidos.

  - **complemento (mesmo dia):** telas estáticas de
    [Histórias e Encontre colegas](../prototipos/2026-10-11-comunidade/index.html), sem abrir a 030
    nem especificar o diretório, e um
    [percurso curto da sessão](../validacao/checkpoint-2/percurso-bloco-comunidade.md), com 12
    telas. O rótulo de navegação do material segue uma regra de linguagem registrada como
    hipótese no percurso, sem nova decisão pendente.

  Constituição, ADR 0008 e ADR 0009 não mudam; a ADR 0010 é nova, restrita à demonstração.
  D8, D9, D10 e DP-1808 continuam pendentes para uso real. Próximos passos: integrar o PR
  documental; completar o material do bloco Comunidade com poucas telas de Histórias e de
  Encontre colegas, sem abrir a 030; escolher um percurso curto de telas para a sessão; e
  resolver a preparação (leitor de tela, procedimento de participação) antes de aplicar os
  checkpoints. Checkpoint 1 e Checkpoint 2 continuam **NÃO APLICADOS**; a 027 continua
  fora.
- **Revisão 15 (2026-10-11).** O solicitante reconduziu a 031 ao fluxo do Spec Kit:
  **clarify → plan → tasks → analyze** ficam autorizados. Isso ajusta de forma explícita a
  restrição da revisão 14 ("sem plan, tasks"):
  - preparar plan e tasks **não libera a implementação**. Código e migrações da 031 continuam
    condicionados à leitura do Checkpoint 1 e do Checkpoint 2 (bloco Comunidade) e à escolha
    entre 031 e 030. A T001 das tasks é o portão, como na 025 e na 026;
  - a expansão de protótipos termina: o material existente (031, #64; Histórias e Encontre
    colegas, #65) é suficiente. O clarify resolve só ambiguidades que mudam comportamento,
    dados ou autorização;
  - a organização dos checkpoints segue como trilha separada, sem novas entregas agora.

  Checkpoint 1 e Checkpoint 2 continuam **NÃO APLICADOS**.
- **Revisão 16 (2026-10-11).** O solicitante autorizou o **primeiro incremento funcional da
  031, só na demonstração, antes dos checkpoints**, como fez com a 025 (revisão 5) e a 026
  (revisão 10). Isso revisa explicitamente a T001 das tasks:
  - **entra no incremento 1** o percurso completo: propor, moderar (publicar, recusar,
    retirar), descobrir, confirmar, ver o link, desistir, acompanhar a quantidade, cancelar,
    encerramento automático do link e estados vazios, com autorização, visibilidade por
    situação (FR-024a), separação do núcleo e testes;
  - **fica para o incremento 2**, registrado na spec e nas tasks:
    - calendário `.ics`;
    - edição em análise e depois da publicação, com correção operacional e nova análise;
    - denúncia dentro do Portal;
    - retorno ao encontro depois da identificação pelo endereço compartilhado (a página sem
      sessão continua neutra);
    - a seção de encontros no Início;
  - nenhum protótipo, protocolo ou lista de decisões de preparação novos.

  Os checkpoints continuam **NÃO APLICADOS** e passam a avaliar a experiência funcionando.
  Não há aprovação registrada nem liberação de uso real: D8, D9, D10 e DP-1808 continuam
  pendentes. O custo aceito é ajustar ou abandonar parte do incremento depois deles.
- **Revisão 17 (2026-10-12).** A
  [auditoria da conclusão e da confirmação](../auditorias/2026-10-12-conclusao-e-confirmacao.md)
  (PR #68) abriu uma trilha pequena na jornada da pesquisa, **fora da camada Portal** (ver "Na
  mesma visão, mas fora da camada Portal"):
  - **033 — Retorno à conclusão depois de revisar** (D5, priorizada): quem revisa uma parte a
    partir da conclusão volta a ela depois de salvar, passando antes pelas partes que a
    alteração tornou aplicáveis. Sem modelo, migração nem JavaScript.
    [Spec](../../specs/033-retorno-revisao-conclusao/spec.md) aguardando aprovação; a
    implementação só começa depois dela;
  - **refinamento visual** da conclusão e da confirmação (D1, D2 e a confirmação, já
    aprovados conceitualmente): entrega separada, depois da 033, com o protótipo da auditoria
    como referência. O número é dado quando a spec for aberta;
  - D3 (título da Seção 13) e D4 (texto de encerramento) ficam como **DECISÃO PENDENTE**
    institucional para uma próxima Versão e não bloqueiam as duas entregas.

  A trilha não muda a sequência da §13.3, os números reservados (027, 030) nem a situação dos
  checkpoints, que continuam **NÃO APLICADOS**.
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
    caminho de entrada preservado após a identificação e funcionamento com a camada desabilitada.
  - Que **não há link específico de Campanha**, e a independência não exige um. O convite
    continua neutro (018 FR-053; ADR 0004) e leva à entrada do instrumento.
- **Valor para o egresso.** Nenhum direto. A S0 destrava o resto sem contornar a Constituição.
- **Dependências.** Nenhuma.
- **Necessária agora?** **Sim**, antes da S1.

### S1 — Início do egresso e shell do Portal *(024; P/M; só leitura; sem modelo novo)*

**Situação: implementada em 2026-10-07** ([spec](../../specs/024-inicio-egresso-portal/spec.md),
[validação](../../specs/024-inicio-egresso-portal/validacao.md)). Próximo passo: o
**Checkpoint 1**, com o
[protocolo](../../specs/024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md)
escrito antes do teste.

**Situação (2026-10-11, revisão 13).** Integrada (PRs #41, #42 e #47). Início e navegação
foram recompostos pela 028 e pela 032. O Checkpoint 1 continua **NÃO APLICADO** e será
aplicado sobre a versão C, depois da etapa de acessibilidade (§13.3).

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
    (= pesquisa) e Meu e-mail. *(Histórico. A 024 implementou "Pesquisa"; a 025 acrescentou
    "Oportunidades" e a 026, "Contribuir". Desde a 032 (FR-011), a navegação é Início, Minha
    trajetória, Oportunidades e Participação; a pesquisa, o e-mail e a contribuição ficam em
    Participação. Ver §13.1.)*
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

**Situação (2026-10-08): implementação autorizada na demonstração; Checkpoint 1 NÃO APLICADO.**

**Situação (2026-10-11, revisão 13): implementada e integrada na demonstração** (PR #49), com
a apresentação revista pela 028 e pela 032. O texto abaixo é o histórico das autorizações. O
Checkpoint 1 continua **NÃO APLICADO**, e a parte de Oportunidades do Checkpoint 2 está no
[protocolo do Checkpoint 2](../validacao/checkpoint-2/protocolo.md).

- **Decisão do solicitante.** Com o Checkpoint 1 ainda não concluído, ele autorizou antecipar
  **exclusivamente a especificação** da 025
  ([spec](../../specs/025-oportunidades-curadas-portal/spec.md)).
- **Exceção restrita à spec.** O protocolo do Checkpoint 1 diz que "a S2 e a S3 não começam
  antes da leitura dos resultados". Esta decisão abre exceção só para a spec.
- **O que continua vedado** até a leitura dos resultados conforme o
  [protocolo](../../specs/024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md):
  - plan, tasks, código e migrações da 025;
  - qualquer passo da S3 (026).
- **Se um critério de compreensão do Checkpoint 1 falhar:**
  - a S1 é corrigida primeiro;
  - a spec da 025 é revista se a correção mudar o Início ou a navegação.
- **O Checkpoint 1 não é dado como aprovado** por esta antecipação.
- **Revisão 4 (2026-10-08): plan e tasks também antecipados.**
  - **Base.** Avaliação por IA com navegação real
    ([relatório](../auditorias/2026-10-08-portal-checkpoints-avaliacao-ia.md)). Ela não
    encontrou impedimento técnico para planejar Oportunidades. Os ajustes A1–A4, A6 e A7
    foram feitos na 024 antes da primeira sessão.
  - **Autorizado:** `/speckit-plan` e `/speckit-tasks` da 025.
  - **Continua vedado:**
    - código e migrações da 025;
    - qualquer passo da 026.
  - **Antes da implementação.** Registrar explicitamente se a antecipação também a abrange.
    Sem esse registro, a implementação espera a leitura do Checkpoint 1.
  - **Incerteza assumida.** A compreensão dos egressos (SC-008 a SC-012 da 024) **não** foi
    validada. A IA não a mede. Se o Checkpoint 1 mostrar falha de compreensão:
    - a S1 é corrigida primeiro;
    - o plan e as tasks da 025 são revistos onde dependem do Início e da navegação. O custo
      afundado se limita a documentação.
- **Revisão 5 (2026-10-08): implementação autorizada (T001 das tasks).**
  - **Decisão do solicitante.** Avançar com código e migrações da 025, só na demonstração.
    Não há impedimento técnico. Implementar uma hipótese reversível antes do teste com egressos
    é uma decisão válida, e a condição de espera virou barreira sem ganho. Ela fica retirada
    para a 025.
  - **Continua valendo:**
    - o Checkpoint 1 continua **NÃO APLICADO** e será aplicado para validar a experiência e
      orientar correções;
    - a avaliação por IA não o aprova;
    - a 026 continua **fora** deste avanço;
    - as verificações previstas nas tasks são concluídas antes de integrar a implementação.
  - **Risco assumido.** Se o Checkpoint 1 mostrar falha de compreensão, o Início e a
    navegação podem precisar de ajuste depois, já com a 025 implementada. O custo é localizado
    na camada do Portal, que é desligável e reversível.

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
- **Situação (2026-10-09, revisão 10).** [Spec](../../specs/026-volte-ao-ifes/spec.md), plan,
  tasks e protótipos prontos; implementação autorizada **só na demonstração**, antes do
  Checkpoint 1, que continua **NÃO APLICADO**. D4 e D5 seguem pendentes para uso real.
- **Situação (2026-10-11, revisão 13).** Implementada e integrada na demonstração (PR #56),
  com o item de navegação "Contribuir" substituído por "Participação" na 032. O roteiro
  manual com teclado da 026 **não foi executado** (validação da 026). D4 e D5 continuam
  pendentes.

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
- **Encerramento da pesquisa** *(revisão 17)*. Pertence à jornada do egresso, não ao Portal:
  033 (retorno à conclusão depois de revisar) e, em seguida, o refinamento visual da
  conclusão e da confirmação. O Portal só aparece na confirmação, pela navegação que já
  existe.

### Comunidade: pertencimento, participação e reencontro *(revisão 12; spec da 031 antecipada na revisão 14)*

A visão, a fundamentação e a direção de cada capacidade estão nas
[alternativas de comunidade](2026-10-09-comunidade-alternativas.md#revisão-de-2026-10-11-a-visão-da-comunidade).
Resumo:

- **030, Histórias de egressos (B).** Editorial, com curadoria e termo de publicação. A entrada
  é a forma "Contar sua história" da 026. Fato novo provável: História.
- **031, Encontros da comunidade (F).** Egressos propõem encontros virtuais, com moderação
  antes da publicação, confirmação de participação, `.ics` e link externo. Fatos novos
  prováveis: Encontro e Confirmação. **Revisão 14:**
  [spec e protótipo](../../specs/031-encontros-propostos-egressos/spec.md) antecipados como
  hipótese, sem implementação. A spec justifica Encontro e Confirmação e acrescenta a
  Denúncia, que sai da camada se D8 indicar outro canal.
- **E1, Reencontro voluntário.** Horizonte com condições: identidade reforçada (DP-1808), D8,
  D9 e uma ADR própria antes de uso real.
- **Dependências.** As de código são o shell e o Início da S1; a 030 também depende da 026. As
  de validação são o Checkpoint 1 e o Checkpoint 2 (bloco Comunidade).
- **Entidades.** "Comunidade", "Conexão" e "Evento" continuam fora do domínio (§2).
  "Encontro" e "Confirmação" só existem se a 031 os justificar (Princípio XXII). A
  justificativa está na spec ("Fatos novos e por que existem"). Nada é criado antes da
  autorização de implementação.

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
- **Revisão 13.** O "Como" acima é de 2026-10-07. Desde então, Oportunidades (025) e a
  contribuição (026) existem no produto, a página pública (029, depois 032) abre a sessão
  com o bloco P, e a navegação usa "Participação". Os critérios abaixo não mudam. O
  procedimento vigente está no
  [protocolo](../../specs/024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md),
  "Revisão de 2026-10-11".

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
- **Protocolo (revisão 13).** [`docs/validacao/checkpoint-2/`](../validacao/checkpoint-2/protocolo.md),
  escrito antes de qualquer sessão. Ele liga estes critérios aos da 025 (SC-011 a SC-016) e
  da 026 (qualitativos) e acrescenta, como proposta a aprovar, a leitura da finalidade dos
  dois e-mails. Limiar, amostra e procedimento de participação continuam pendentes.

#### Bloco Comunidade *(revisão 12)*

- **Sobre o quê.** Um protótipo estático de Histórias, Encontros e Encontre colegas. O que é
  conceitual aparece marcado, e nada disso está implementado.
- **Critérios de compreensão.** A pessoa:
  1. distingue encontro proposto por egresso de evento do Ifes;
  2. entende quem vê a confirmação dela e quem recebe o link da reunião;
  3. entende que aparecer no diretório é escolha dela, o que é mostrado, e que o contato
     depende de aceite;
  4. não atribui ao Portal função inexistente (mensagens, rede de contatos, evento oficial
     onde não há).
- **Utilidade e interesse.** Qualitativos, anotados por pessoa:
  1. se proporia um encontro, sobre o quê e para quem;
  2. se participaria de um encontro proposto por outro egresso;
  3. se aderiria ao diretório e o que mostraria;
  4. se uma história de outro egresso lhe diz algo, e por quê.
- **Como ler o resultado.** Informa a escolha entre 030 e 031 e as condições do E1. Não é taxa
  de adesão nem métrica de engajamento (seção 7).
- **Identificadores (revisão 13).** No protocolo do Checkpoint 2, os critérios acima são
  CM-C1 a CM-C4 e CM-U1 a CM-U4, na mesma ordem.

---

## 8. Dependências

```text
 S0  ADR 0008 + Constituição 2.1.0 — CONCLUÍDA
     (fronteira; coleta independente; nome provisório; módulos decididos nas specs)
  │
  ▼
 S1  Início e shell do Portal + trajetória por regra positiva (revisa 021 FR-001/002/E2, 022 FR-001)
     + acesso direto ao instrumento e caminho de entrada preservado, com testes de independência
  │
  ▼
 ◆ Checkpoint 1 — modelo mental e navegação
   (com o teste moderado da jornada; mockup à parte para Oportunidades/Volte ao Ifes)
   [2026-10-08: a S2 (025) foi implementada na demonstração antes deste ponto, por decisão do
    solicitante; o checkpoint continua pendente]
   [2026-10-09: a S3 (026) também foi autorizada na demonstração antes deste ponto; o
    checkpoint será aplicado depois da 026 e da 029 implementadas (revisão 10)]
   [2026-10-11: a 032 (convergência C) também entrou antes; o checkpoint é aplicado sobre a
    versão C, depois da etapa de acessibilidade (revisão 13, §13.3)]
  │
  ├──────────────┐
  ▼              ▼
 S2             S3            ◄── D4 (quem cura e quem recebe) e D5 (base legal) para uso real
 Oportunidades  Volte ao Ifes
  │              │
  └──────┬───────┘
         ▼
 ◆ Checkpoint 2 — valor recebido e reciprocidade
   (+ bloco Comunidade, sobre protótipo estático; revisão 12)
         │
         ├──────────────────────────────┐
         ▼                              ▼
 S4  Linha do tempo da relação     Comunidade: 030 Histórias e 031 Encontros
     (opcional)                    (ordem decidida pelo checkpoint; preferência pela 031)
                                   [2026-10-11, revisão 14: spec e protótipo da 031
                                    antecipados como hipótese; implementação só depois
                                    da leitura dos dois checkpoints]
                                        │
                                        ▼
                                   E1 Reencontro voluntário ◄── DP-1808, D8, D9, ADR própria

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
  e moderação. **Revisão 12:** a aproximação entre egressos saiu desta lista. Ela entra como
  encontros (031) e reencontro voluntário (E1), com as condições da seção 6. Rede, mensageria
  e notificações continuam postergadas.
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
| **D6** | Limiar e autorização para mostrar agregados a egressos (DP-1101, DP-2105) | CPAEG/Proex, encarregado | Comunidade agregada (postergada) |
| **D8** | Quem modera encontros propostos por egressos, para cada recorte de público (uma unidade, várias, temático); critérios de recusa e retirada; quem recebe denúncias de encontros e do diretório. A PAEG não atribui essa função (Art. 22, VII, só "apoiar") nem proíbe encontros entre campi. A resolução observa as competências dos Arts. 14, 18, 21, 22 (inclusive XI, regulamento das CSAEG) e 26 (casos omissos), sem criar fluxo próprio agora | CPAEG, com as CSAEG e a Proex | Uso real da 031 e do E1. Na demonstração, a spec registra uma hipótese |
| **D9** | Base legal de **cada** tratamento (publicação de história, organização de encontro, confirmação, diretório), que podem ter bases diferentes; termos versionados e adesão voluntária **não substituem** a base legal (Guia da ANPD para o Poder Público); retenção de confirmações, histórias e adesões | Encarregado de dados, com a CPAEG | Uso real da 030, da 031 e do E1 |
| **D10** | Complementaridade, interoperabilidade e governança com outras soluções institucionais (aplicativo da DIREC; associações e grupos de ex-alunos), pela Constituição VI | Proex/DIREC/CPAEG | Só o uso real. Por decisão do solicitante (2026-10-11), não bloqueia a demonstração nem a validação |

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

---

## 13. Estado depois da 032 e próxima etapa *(revisão 13, 2026-10-11)*

- **Base.** `main` em `63b9447` (PR #61, convergência C integrada).
- **Natureza.** Consolidação documental. Nenhum código, banco, dependência ou instrumento
  muda. Nenhuma spec é aberta.

### 13.1 Entregas na demonstração

Tudo abaixo existe **só na demonstração**, com dados fictícios e o Portal desligável
(`TRAJETORIA_PORTAL=0`). A coleta continua independente do Portal: o convite segue
`/acesso/` → `/formacoes/` (D7).

| Etapa | Feature | PRs | O que existe hoje |
|---|---|---|---|
| S0 | ADR 0008, Constituição 2.1.0 | #40 | Fronteira da camada, coleta independente, nome provisório |
| S1 | [024](../../specs/024-inicio-egresso-portal/spec.md) | #41, #42, #47 | `/entrar/`, Início, shell com navegação; trajetória, card e vídeo antes de qualquer pesquisa (D3) |
| S2 | [025](../../specs/025-oportunidades-curadas-portal/spec.md) | #45, #48, #49 | Oportunidades pertinentes com explicação; curadoria por escopo; catálogo fictício; expiração pelo período |
| S3 | [026](../../specs/026-volte-ao-ifes/spec.md) | #55, #56 | Contribuição em seis formas, ciência versionada, Suas contribuições, retirada; lista e CSV da unidade; marco "contato feito" |
| Camada visual | [028](../../specs/028-camada-visual-portal/spec.md) | #51 a #54 | ADR 0009, direção B. A forma visual foi substituída pela C |
| Página pública | [029](../../specs/029-pagina-publica-portal/spec.md) | #55, #57, #58 | Página pública como relação nos dois sentidos. Substituída em `/` pela C; o protótipo que ela reproduz continua em [`prototipo/proposta.html`](../../specs/029-pagina-publica-portal/prototipo/proposta.html) |
| Convergência C | [032](../../specs/032-convergencia-visual-c/spec.md) | #60, #61 | Fontes locais, página pública C, Início C (linha com "Hoje" e "Adiante", encontros, oportunidades, participação), navegação **Início, Minha trajetória, Oportunidades, Participação** e a página `/participacao/` |

**Navegação vigente (032 FR-011).** Não há mais os itens "Pesquisa", "Meu e-mail" nem
"Contribuir". A pesquisa (`/formacoes/`), o e-mail (`/meu-email/`) e a contribuição ficam em
"Participação", que é o item atual também nessas telas. Nenhuma rota mudou. Documentos
anteriores que citam "Pesquisa" na navegação descrevem a versão da época.

**Encontros.** O que a demonstração mostra como encontro é a alternativa **A**: um item da
categoria "Eventos" da 025, divulgado pela unidade, com link oficial. Encontros propostos por
egressos (**F**, 031), Histórias (**B**, 030) e Encontre colegas (**E1**) **não existem**.

### 13.2 Evidências: técnicas × validação com egressos

**Validação com egressos: nenhuma.** Nenhuma sessão foi feita. O Checkpoint 1 e o
Checkpoint 2 estão **NÃO APLICADOS**. Nenhum critério de compreensão ou comportamento
(SC-008 a SC-016 da 024, P-01 a P-07 da 029, critérios do Checkpoint 2) tem resultado.

**Evidências técnicas existentes** (não substituem a validação):

| Evidência | Situação | Vale para a versão C? |
|---|---|---|
| Suíte automatizada (CI) | 3366 testes aprovados depois do code review da 032 | Sim |
| Medidas e capturas reais (320 a 1440 px, fonte a 100% e 200%) | [Validação da 032](../../specs/032-convergencia-visual-c/validacao.md) | Sim |
| Contraste AA dos pares novos | Medido na 032 | Sim |
| Passada de teclado e árvore de acessibilidade da 024 | 2026-10-08, 375×812, persona Maria ([validação](../../specs/024-inicio-egresso-portal/validacao.md)) | **Não**: navegação e Início da época, com "Pesquisa" e "Meu e-mail" no menu |
| Ordem de foco em `/oportunidades/` (025, T049) | [Validação da 025](../../specs/025-oportunidades-curadas-portal/validacao.md) | **Não**: navegação de cinco itens da época |
| Roteiro manual com teclado da 026 | Não executado na 026. A contribuição, do formulário à retirada, entrou no roteiro da versão C (linha abaixo) | Sim, pelo roteiro da C |
| Roteiro manual com teclado da 029 | 2026-10-11, sem achados, sobre a página da 029 (`950aea6`) | **Não**: a página foi substituída pela C |
| Roteiro manual com teclado da 032 | **Executado em 2026-10-11** sobre `63b9447`, no Chromium 152 embutido no app Claude, a 375×812 e 1280×800 ([validação da 032](../../specs/032-convergencia-visual-c/validacao.md#roteiro-manual-com-teclado-e-árvore-de-acessibilidade-2026-10-11)). Nenhum impedimento às tarefas; quatro achados (A-01 a A-04), nenhum corrigido | Sim |
| Leitor de tela (VoiceOver ou NVDA) | **Nunca executado** (P4 da preparação do Checkpoint 1). [Roteiro](../../specs/032-convergencia-visual-c/evidencias/roteiro-leitor-de-tela.md) pronto, sem resultados | — |
| [Avaliação por IA](../auditorias/2026-10-08-portal-checkpoints-avaliacao-ia.md) | 2026-10-08, anterior à 025 implementada | Não; e não substitui checkpoint |
| Fidelidade aos mockups "C · Convergência" | Auditoria na validação da 032 | Os mockups C **não estão versionados** no repositório. A conferência só é reproduzível pelas capturas reais |

### 13.3 Sequência

| # | Etapa | O que entra | Condição para seguir |
|---|---|---|---|
| 1 | **Consolidação da C** | Esta revisão: documentos reconciliados, kit do Checkpoint 1 na versão C, protocolo do Checkpoint 2 | PR documental integrado |
| 2 | **Acessibilidade** | Roteiro manual com teclado, num navegador real, sobre as telas que as tarefas dos dois checkpoints percorrem: página pública, `/entrar/`, Início (Ana, Bruno, Diego), Minha trajetória, Oportunidades, Participação, a contribuição do início à retirada e Meu e-mail. Teste com leitor de tela (P4). Registro na validação da 032 e, para a contribuição, na da 026 | Nenhum obstáculo que impeça uma tarefa dos checkpoints. Correções de código, se houver, precisam de autorização própria |
| 3 | **Checkpoint 1** | 024 e bloco P, sobre a versão C ([protocolo](../../specs/024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md)) | P1 a P6 da [preparação](../../specs/024-inicio-egresso-portal/evidencias/checkpoint-1/preparacao-sessao.md) resolvidas antes da primeira sessão |
| 4 | **Ajustes** | Leitura do Checkpoint 1 conforme o protocolo; ajustes do Início, da navegação ou da página pública | Ajustes integrados, ou registro de que não foram necessários |
| 5 | **Protótipo estático da Comunidade** | Histórias, Encontros e Encontre colegas, com o conceitual marcado (revisão 12; requisitos do material no [protocolo do Checkpoint 2](../validacao/checkpoint-2/protocolo.md#material-do-bloco-comunidade)) | Protótipo revisado pelo solicitante. Feito depois do passo 4, para não prototipar sobre uma navegação que o Checkpoint 1 reprove |
| 6 | **Checkpoint 2** | Produto (Oportunidades, contribuição, Participação) e bloco Comunidade, sobre o protótipo | Pendências Q1 a Q7 do protocolo resolvidas (Q8 decidida na revisão 14) |
| 7 | **Decisão entre 031 e 030** | Solicitante, com a leitura dos dois checkpoints (§13.5) | — |

- As decisões institucionais (D4, D5, D8, D9, D10, identidade e operadores reais) **não**
  bloqueiam os passos 1 a 7. Bloqueiam o uso real (§13.5).
- Os passos 3 e 6 não aprovam nada sozinhos: os resultados entram em PR próprio, com as
  fichas e a síntese, e a leitura segue a regra escrita antes do teste.
- A S4 (027) continua fora. O Checkpoint 2 informa se ela vale a pena (§7).
- **Revisão 14.** A spec e o protótipo da 031 foram antecipados, como hipótese, fora desta
  sequência. Eles não mudam a ordem nem as condições dos passos 3 a 7. O protótipo da 031 é
  parte do material do passo 5, completado no mesmo dia com Histórias e Encontre colegas e
  um percurso curto. O passo 5 só termina com a revisão do solicitante (Q7).

### 13.4 Kits de validação

| Kit | Arquivos | Situação |
|---|---|---|
| Checkpoint 1 (024 + bloco P) | [protocolo](../../specs/024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md), [preparação](../../specs/024-inicio-egresso-portal/evidencias/checkpoint-1/preparacao-sessao.md), [ficha](../../specs/024-inicio-egresso-portal/evidencias/checkpoint-1/ficha-participante.md), [bloco P](../../specs/029-pagina-publica-portal/checkpoint-pagina-publica.md), [ficha do bloco P](../../specs/029-pagina-publica-portal/checkpoint/ficha-bloco-p.md) | Atualizado para a versão C. Critérios e limiar proposto não mudam. P1 a P5 continuam pendentes; P6 (comparação histórica) é nova |
| Checkpoint 2 (025, 026 + bloco Comunidade) | [protocolo](../validacao/checkpoint-2/protocolo.md), [preparação](../validacao/checkpoint-2/preparacao-sessao.md), [ficha](../validacao/checkpoint-2/ficha-participante.md), [ficha do bloco Comunidade](../validacao/checkpoint-2/ficha-bloco-comunidade.md) | Escrito antes de qualquer sessão. Q1 a Q7 pendentes; Q8 decidida (observações exploratórias da 031). Material do bloco Comunidade completo, com [percurso curto](../validacao/checkpoint-2/percurso-bloco-comunidade.md), aguardando revisão (Q7) |

O Checkpoint 2 fica em `docs/validacao/` porque cobre duas features (025 e 026) e uma
capacidade sem spec (Comunidade). O Checkpoint 1 continua junto da 024.

### 13.5 Próxima spec: recomendação

**Candidata preferencial: 031, Encontros da comunidade** (alternativa F), condicionada à
leitura do Checkpoint 1 e do Checkpoint 2, com o bloco Comunidade.

> **Revisão 14.** A [spec da 031](../../specs/031-encontros-propostos-egressos/spec.md) já
> existe, antecipada como hipótese. Ela resolve os pontos do escopo mínimo abaixo e as duas
> obrigações listadas em "A spec da 031 também terá de". A implementação continua dependendo
> dos dois checkpoints e da decisão entre 031 e 030. Os motivos que poderiam pôr a 030 antes
> continuam valendo.

**Por que a 031.**
- É a primeira capacidade em que egressos produzem valor para outros egressos, que é o
  critério da revisão 12 para a palavra "comunidade" nas telas servidas.
- Tem a base mais direta na PAEG para a relação entre egressos: eventos e troca de
  experiência (Art. 12; Art. 8, II), sem que a PAEG a exija.
- É a preferência funcional registrada pelo solicitante (revisão 12).

**Escopo mínimo** (direção da revisão 12; insumo da spec, não requisito aprovado):
- um egresso identificado, com ao menos uma Conclusão Acadêmica, propõe um encontro
  **virtual**: título, descrição, data, horário, público e link externo de videoconferência;
- moderação institucional **antes** da publicação, com recusa e retirada motivadas e canal
  de denúncia. Na demonstração, quem modera é uma hipótese registrada na spec (D8);
- página do encontro com a distinção visível entre "Evento do Ifes" (A) e "Encontro
  proposto por egresso" (F);
- "Vou participar", que não comprova presença; cancelamento pelo organizador e pelo
  participante;
- o link da reunião só para quem confirmou e está com sessão; contagem só para o organizador
  e a moderação; sem lista nominal nem contato exposto;
- `.ics` que aponta para a página, com o aviso de que mudanças não atualizam o calendário já
  baixado;
- termos do organizador e da participação versionados (XVII), sem tratá-los como base legal
  (D9);
- confirmações como dado operacional: fora de snapshot, exportação e indicador (ADR 0008);
- fatos novos prováveis, a justificar pela spec (XXII): Encontro e Confirmação.

**Fica fora do mínimo:** encontros presenciais (seguem pela A), chat, comentários, curtidas,
contador público, notificações automáticas e integração com videoconferência.

**A spec da 031 também terá de:**
- revisar de forma explícita a decisão 7 da ADR 0009 e as vedações de vocabulário da 024,
  da 028, da 029 e da 032 (o menu público usa "Encontros", e não "Comunidade");
- responder às cinco perguntas do Princípio VI, com as outras soluções institucionais como
  ponto de atenção (D10).

**Motivos que poderiam justificar a 030 (Histórias) primeiro.** Cada um precisa aparecer na
leitura dos checkpoints ou numa análise registrada, e não ser presumido:
- no bloco Comunidade, os participantes não distinguem encontro proposto por egresso de
  evento do Ifes, ou não entendem quem vê a confirmação e o link (CM-C1 e CM-C2), e o
  protótipo não resolve isso;
- pouco interesse em propor ou participar de encontros (CM-U1, CM-U2), e interesse claro por
  histórias (CM-U4);
- moderação antes da publicação sem hipótese viável nem para a demonstração, ou a garantia
  de identidade do organizador vista como condição até para uma demonstração crível;
- custo menor: a 030 parte da forma "Contar sua história" da 026, que já existe, com um
  fato novo provável (História) e sem agenda nem confirmação;
- o protótipo mostrar que, sem histórias, um encontro não tem contexto suficiente para
  atrair participantes.

**Pré-requisitos de demonstração × bloqueios de uso real.**

| Para especificar e implementar a 031 na demonstração | Bloqueia só o uso real |
|---|---|
| Checkpoint 1 aplicado e lido; ajustes integrados | **D4**: quem cura oportunidades e quem recebe as contribuições (uso real da 025 e da 026) |
| Protótipo da Comunidade e Checkpoint 2, com o bloco Comunidade, lidos | **D5**: base legal e ciência da contribuição e do uso do contexto acadêmico |
| Decisão do solicitante entre 031 e 030 | **D8**: quem modera cada recorte de público, critérios de recusa e retirada, quem recebe denúncias |
| Hipótese de moderação registrada na spec (D8 na demonstração) | **D9**: base legal de cada tratamento (encontro, confirmação, história, diretório) e retenção |
| Termos e textos provisórios, versionados (XVII) | **D10**: complementaridade com outras soluções institucionais (aplicativo da DIREC, associações e grupos de ex-alunos) |
| Revisão explícita da decisão 7 da ADR 0009 | **Identidade**: DP-1808 e o Portão A; Gov.br não é presumido. A moderação não substitui a identidade |
| Dados fictícios, Portal desligável, testes de fronteira | **Operadores reais**: DP-1001 |
| Confirmações fora do dado analítico (ADR 0008) | Também: D1 (produção), D2 e DP-801 (nome e textos), DP-3201 e DP-3202 (ACS) |

A E1 (reencontro voluntário) continua no horizonte, com as condições da revisão 12:
DP-1808, D8, D9 e uma ADR própria antes de uso real.

### 13.6 Antes da primeira sessão do Checkpoint 1

Decidir:
- **P1:** amostra e limiar (5 participantes; 4 de 5 em cada critério). Com o bloco P, que
  admite 5 a 8, dizer como o limiar se aplica.
- **P2:** moderador e recrutamento.
- **P3:** procedimento de participação e, se houver, de gravação. Sem P3, não há sessão.
- **P5:** com ou sem vídeo.
- **P6:** se o bloco P mantém a comparação histórica, e com qual versão.

Executar:
- roteiro manual com teclado sobre a versão C (passo 2);
- **P4:** teste com leitor de tela;
- preparar o ambiente na `main` com a 032 (`63b9447` ou posterior) e registrar o commit em
  cada ficha.
