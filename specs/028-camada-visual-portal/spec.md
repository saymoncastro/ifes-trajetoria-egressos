# Feature Specification: Camada visual do Portal — direção B (trajetória)

**Feature Branch**: `codex/028-camada-visual-portal`
**Created**: 2026-10-09
**Status**: Implementada e validada localmente na demonstração.
**Input**: “Como seguir? Quero avançar no desenvolvimento logo.” O solicitante escolheu
“B — trajetória (recomendada)” em 2026-10-09. O escopo aplica a ADR 0009; a escolha não
resolve nenhuma pendência institucional nem aprova o Checkpoint 1.

## Contexto e dependências

A [ADR 0009](../../docs/adr/0009-camada-visual-do-portal.md) foi integrada pelo PR #51.
Os [protótipos](../../docs/prototipos/2026-10-09-portal/index.html) estão concluídos.
A direção escolhida dá destaque à trajetória, usa fundo verde profundo e creme e dispõe
a linha do tempo horizontalmente no desktop quando há várias formações.

Esta feature implementa a camada visual existente e a página pública prevista na ADR.
O número 028 evita ocupar 026 e 027, reservados no roadmap para outras capacidades.
Não antecipa essas capacidades. A demonstração independe de fotografia ou identidade
definitiva; o Checkpoint 1 continua **NÃO APLICADO**.

O protótipo B da Ana tem um achado a corrigir: a prévia/ação começa 11 px depois do
limite da primeira tela no critério de 1280×720. A implementação deve resolver e medir
esse caso, sem remover fatos, agregados ou proveniência para caber.

## User Scenarios & Testing

### US1 — Reconhecer a própria trajetória (P1)

O egresso identificado encontra as formações, a origem dos fatos e uma prévia do card,
antes do convite à pesquisa, com composição adequada à largura disponível.

**Teste independente:** abrir o Início de Ana e Diego, com uma e três formações,
a 375×812, 1280×720 e 1440×900, sem JavaScript.

1. **Dado** Ana, **quando** abre o Início, **então** vê título e primeiro fato sem rolar
   no celular; no desktop vê também prévia ou ação principal na primeira tela.
2. **Dado** Diego, **quando** abre o Início no desktop, **então** suas formações continuam
   separadas e a linha do tempo aproveita a largura, sem esconder informações.
3. **Dada** uma pesquisa pendente, **quando** percorre a página ou usa o teclado,
   **então** encontra reconhecimento, proveniência, ações, Oportunidades e convite nessa
   ordem; pode ir diretamente à pesquisa pela navegação.

### US2 — Entender o Portal antes de entrar (P1)

Quem chega a `/` sem sessão vê o que existe e uma ação para confirmar seus dados.

**Teste independente:** visitar `/` sem sessão; entrar pela ação e confirmar os dados
fictícios; repetir pelo link direto de convite `/acesso/`.

1. Sem sessão, `/` responde com página pública e ação “Entrar no Portal”. Seu h1 apresenta
   a proposta; a identificação permanece em `/entrar/`.
2. A página apresenta um card explicitamente fictício, sem consultar dados de uma Pessoa.
3. Com Pessoa na sessão, `/` continua redirecionando ao Início; com declarante, à declaração.
4. O caminho `/acesso/` continua indo diretamente à identificação e às formações.

### US3 — Usar as demais telas com uma apresentação coerente (P2)

Entrar, ver a trajetória, baixar o card, informar e-mail e consultar oportunidades
mantêm seus comportamentos e recebem a apresentação do Portal.

**Teste independente:** percorrer essas telas com teclado e sem JavaScript; desligar o
Portal e repetir a trajetória, o contato e a jornada de pesquisa.

1. `/entrar/` mostra o formulário e mensagens atuais; o painel fictício começa recolhido
   e pode ser aberto com um controle nativo, sem JavaScript.
2. Minha trajetória mantém capítulos, opções do card e vídeo quando disponível; Meu e-mail
   mantém finalidade, opcionalidade, erros e confirmação; Oportunidades mantém explicação
   e origem por item.
3. Com `TRAJETORIA_PORTAL=0`, nenhuma dessas telas recebe a camada visual nova. A pesquisa
   e o shell de referência continuam funcionando e iguais.

### Edge Cases

- Sem Conclusão: manter mensagem e ações existentes; omitir linha do tempo, agregados e card.
- Falha na montagem da narrativa: omitir o reconhecimento e a prévia juntos; manter as ações
  e o convite. Falha de Oportunidades continua isolada a esse bloco.
- Ano, curso ou unidade ausentes: mostrar apenas os fatos fornecidos pelo contrato da 021;
  nenhum ano ou relação temporal é inferido para desenhar os nós.
- Muitas formações: permitir quebra em linhas no desktop, sem carrossel nem rolagem lateral;
  no celular todas ficam na ordem de leitura.
- Sem agregados: omitir o bloco inteiro. Sem oportunidade: omitir o destaque do Início.
- Sessão expirada e POST inválido: manter avisos, limites, CSRF e regras de renovação da 018.
- Imagem genérica para formação de unidade conhecida: legenda “Ifes · ilustração”.

## Requirements

### Functional Requirements

- **FR-001 [Arquitetura]**: A camada DEVE ser exclusiva do Portal em demonstração e
  desligável pelo interruptor existente. O núcleo NÃO DEVE depender dela (ADR 0008).
- **FR-002 [Arquitetura]**: O shell e tokens da 015 DEVEM permanecer intactos. A camada
  nova só vale em `/`, `/entrar/`, `/inicio/`, `/minha-trajetoria/`, `/meu-email/` e
  `/oportunidades/`. `/acesso/`, `/formacoes/`, Participações, declaração e operação
  conservam sua composição; a navegação já existente não lhes aplica os novos tokens.
- **FR-003 [Hipótese]**: A direção B DEVE orientar a composição: verde profundo, creme,
  linha do tempo e card. Nenhum espaço “aguarda ACS” de protótipo vira conteúdo do produto.
- **FR-004 [Arquitetura]**: Container do Portal de referência 72 rem, com largura útil
  ≥ 1000 px entre 1280 e 1440 px. Texto corrido limitado a aproximadamente 70 caracteres.
- **FR-005 [Hipótese]**: Verde de ação `#195128` e forte `#00420c` só no Portal.
  `system-ui`, sem fonte servida; destaque de 40 px/700 para h1 no desktop. A assinatura
  oficial permanece sem alteração.
- **FR-006 [Arquitetura]**: `/` sem sujeito DEVE apresentar conteúdo público com ação
  para `/entrar/`. Pessoa e declarante mantêm os destinos fixos da 024. Parâmetros do
  cliente NÃO DEVEM decidir destinos. Respostas continuam sem cache compartilhado.
- **FR-007 [Hipótese]**: A página pública DEVE mostrar somente capacidades disponíveis,
  card de exemplo com selo “Exemplo com dados fictícios” e textos provisórios sem slogan.
  Oportunidades não são garantidas; não há links para áreas inexistentes.
- **FR-008 [Arquitetura]**: A página pública NÃO DEVE consultar ou expor uma Pessoa,
  coletar dado, criar Participação ou depender de JavaScript. Convites NÃO passam por ela.
- **FR-009 [Arquitetura]**: O Início DEVE consumir a montagem da narrativa da 021,
  sem segunda regra de cálculo nem leitura de Resposta ou contato. DEVE manter
  proveniência visível e todas as formações, na ordem existente.
- **FR-010 [Hipótese]**: A prévia do Início DEVE usar o card existente, sem nome e sem
  persistência nova. Agregados só aparecem quando a narrativa já os disponibiliza,
  com frase completa e data de apuração.
- **FR-011 [Hipótese]**: Com várias formações, a linha do tempo DEVE ser horizontal a
  partir de 1024 px e vertical abaixo de 768 px; pode quebrar em mais linhas para caber.
  O Início DEVE ter pelo menos duas colunas a partir de 1024 px e uma abaixo de 768 px.
- **FR-012 [Arquitetura]**: Reconhecimento e proveniência vêm antes das ações;
  Oportunidades vem depois das ações, e o convite depois de Oportunidades, na leitura,
  no foco e no visual. A navegação conserva o atalho “Pesquisa”.
- **FR-013 [Hipótese]**: Vedações de vocabulário e nome no Início da 024 permanecem;
  na página pública valem as exceções da ADR para “Oportunidades” e “pesquisa”. O nome
  fictício na faixa de demonstração permanece fora do conteúdo do produto.
- **FR-014 [Arquitetura]**: `/entrar/` DEVE manter identificação, campos, mensagens e
  destinos existentes; apenas seu painel fictício fica recolhido por padrão.
- **FR-015 [Arquitetura]**: A harmonização NÃO DEVE alterar curadoria, pertinência,
  finalidade de contato, elegibilidade da narrativa, opções de nome no card nem vídeo.
  O JavaScript opcional de compartilhamento da 021 pode permanecer; nada novo depende dele.
- **FR-016 [Arquitetura]**: Legenda com unidade só quando a imagem é daquela unidade.
  Imagem genérica usa “Ifes · ilustração”; vale para página, Início, card e vídeo que
  reutilizem a função de legenda. Nenhuma imagem afirma retratar a época do egresso.
- **FR-017 [Arquitetura]**: Sem rolagem horizontal entre 320 e 1440 px a 100% e 200% de
  fonte; um h1; foco da 015, semântica, contraste AA e alvos ≥ 44×44 px.
- **FR-018 [Arquitetura]**: Nenhum modelo, migração, dependência, CDN, integração ou
  fonte externa novo. Capturas e medições DEVEM acompanhar a entrega.

### Requisitos revisados

| Origem | Revisão explícita nesta feature |
|---|---|
| 015 FR-007, FR-008 | Coluna de 40 rem, breakpoint único e vedação a cards se delimitam ao instrumento e `/acesso/`; FR-002 a FR-005 valem no Portal |
| 015 FR-014 | Verde provisório no Portal; instrumento continua azul; D-02 permanece pendente |
| 024 FR-005 | Sem sessão, a entrada `/` mostra a página pública; sujeito mantém seu destino |
| 024 FR-026 | Tokens próprios, hero e grade admitidos no Portal, conforme ADR 0009 |
| 021 FR-076 | Unidade da legenda vem da imagem efetivamente escolhida, não da formação |
| 025, apresentação do Início | Nova composição absorve o destaque; preserva todos os campos e orçamento móvel de 270 px da 025 |

As outras regras das features de origem permanecem. Notas de revisão devem ser
acrescentadas a elas, sem apagar o histórico de decisões.

### Dados e entidades

Não há entidade nova. Conclusão Acadêmica continua distinta da Pessoa e da Participação.

| Dado | Origem | Fonte | Divergência |
|---|---|---|---|
| Formações e contexto agregado | Institucional/simulado na demonstração | Montagem da 021 | Não sobrescrever; conservar proveniência |
| Tempo desde a conclusão | Derivado | Montagem da 021 | Nenhum cálculo paralelo |
| Situação da pesquisa | Derivado | Resolução da entrada da 007 | Mesmos estados e destinos |
| Oportunidade e explicação | Conteúdo curado + contexto institucional | Consultas da 025 | Mesma regra determinística |
| Card público | Exemplo fictício versionado | Gerador da 021 | Selo explícito; não representa usuário real |
| Respostas e contato | Declarado | Não lidos pelo Início | Nenhuma coleta adicional |

## Success Criteria

- **SC-001**: A 375×812, título e primeiro fato do Início aparecem sem rolar.
- **SC-002**: A 1280×720 e 1440×900, descontada a faixa de demonstração, o Início mostra
  título, primeiro fato e prévia ou ação principal; verificar Ana e Diego.
- **SC-003**: Na página pública a 1280×720, proposta e ação de entrar aparecem sem rolar,
  descontada a faixa de demonstração.
- **SC-004**: Largura útil ≥ 1000 px nos desktops citados; duas ou mais colunas no Início
  a partir de 1024 px, uma abaixo de 768 px; nenhuma rolagem horizontal na matriz de fonte.
- **SC-005**: Teste de shell de referência passa sem editar a referência. Caminho direto
  do convite mantém telas e ações; Portal desligado preserva o shell e os destinos.
- **SC-006**: Regras de acesso, fronteiras e ausência de escritas indevidas continuam
  protegidas; lint, check, migrations e suíte passam.
- **SC-007**: Contraste medido, navegação por teclado e funcionamento sem JavaScript
  registrados; capturas comparadas com a direção B escolhida.

## Invariantes Constitucionais Afetados

- I, III, VII, VIII, XI: só apresentação; histórico, origem e várias formações preservados.
- V, VI, XV: dependência só da camada para o núcleo; identidade e fonte substituíveis.
- XVI, XVII: nenhum dado pessoal novo, rastreamento ou mudança de finalidade.
- XIV, XX, XXI: convite independente; teclado, foco, contraste e responsividade verificados.
- XXII, XXVI, XXVIII, XXIX: escopo mínimo, testes de regressão e pendências explícitas.

## Fronteira do NIAE

1. Pertence ao acompanhamento? A apresentação da pesquisa sim; o Portal é relacionamento.
2. É necessária à coleta? Não; a coleta continua independente da camada.
3. Há solução institucional definitiva? Relação com o Portal institucional está pendente.
4. Integração basta? A narrativa existente basta; não se cria contrato externo sem consumidor.
5. Aumenta acoplamento? Não deve: base e tokens próprios vivem na camada, com extensão neutra
   de apresentação quando uma tela do núcleo também for usada pelo Portal.

## Out of Scope

Produção e dados reais; 026 e 027; pesquisa ou método novo; autenticação nova; fotografias
sem licença; conteúdo de nostalgia; inscrições, vagas, comunidade, CMS ou telemetria.

## Decisões Pendentes

- **D-02, D-03, DP-801, D2 — DECISÃO PENDENTE:** identidade, assinatura, linguagem e nome
  definitivos; Proex/CPAEG, TI e ACS conforme ADR 0009. Tratamento só de demonstração.
- **DP-2106 — DECISÃO PENDENTE:** acervo e licenças, ACS/CPAEG; usar catálogo genérico atual
  com legenda honesta. Não impede a demonstração.
- **DP-406, DP-2108 — DECISÃO PENDENTE:** adoção institucional do Portal; hipótese desligável.
- As pendências de fonte, autorização, dados reais e curadoria das features de origem
  permanecem. Checkpoint 1 **NÃO APLICADO**; escolha visual não é validação com egressos.
