# Feature Specification: Oportunidades curadas do Portal do Egresso

**Feature Branch**: `claude/feature-025-oportunidades-34a20b`

**Created**: 2026-10-08

**Status**: Draft. **Só especificação.** A implementação está condicionada à leitura dos
resultados do Checkpoint 1 da 024 (ver "Dependências").

**Input**: User description: "Feature 025 — Oportunidades curadas do Portal do Egresso
(roadmap S2). Área de Oportunidades integrada ao Portal (024): o egresso encontra
possibilidades institucionais (formação continuada, cursos, eventos, pesquisa e extensão,
carreira, empreendedorismo, outras) pertinentes ao seu contexto acadêmico já registrado, com
explicação determinística de por que cada uma aparece, sem novo perfil nem novos dados
pessoais. Operadores autorizados (governança 010, escopo por unidade) cadastram, editam,
publicam e retiram oportunidades; a divulgação expira sozinha pelo período. Modelo mínimo
justificado pelos fluxos; sem CMS, inscrições, vagas, agenda, imagens, workflow editorial,
recomendação ou marketing. Fronteiras da Constituição 2.1.0 e ADR 0008. Só especificação;
implementação condicionada ao Checkpoint 1."

## Contexto

A 024 entregou um Início que reconhece a história do egresso antes de pedir qualquer coisa.
Hoje, porém, o Portal só devolve ao egresso o que ele já tem: a própria trajetória, o card e
o vídeo. Ele ainda não oferece nada novo. O
[roadmap do Portal](../../docs/roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md)
(S2) aponta a área de Oportunidades como o primeiro valor novo e como o primeiro fato
persistente da camada de relacionamento.

Esta spec responde:

> **"O egresso encontra, sem preencher nada, possibilidades institucionais pertinentes à
> formação que concluiu e entende por que cada uma aparece para ele?"**

O princípio é o do roadmap: **o egresso recebe valor antes de ser solicitado a fornecer novos
dados.** A pertinência sai só do que o Ifes já registra.

### Decisões do solicitante (2026-10-08)

| # | Assunto | Decisão |
|---|---|---|
| S1 | Antecipação | Autorizada **só a especificação** da 025, antes do Checkpoint 1. A implementação continua condicionada à avaliação dos resultados do Checkpoint 1. Registrado no roadmap |
| S2 | Pertinência | Regras simples, determinísticas e explicáveis, só com atributos institucionais disponíveis. Sem IA, sem recomendação, sem cadastro de interesses |
| S3 | Governança | Curadoria por operadores autorizados, respeitando o escopo de atuação. Não presumir que qualquer operador publica para todas as unidades |
| S4 | Escopo | Sem CMS, inscrições, vagas, agenda, imagens, workflow editorial, recomendação ou marketing |
| S5 | Modularização | Não presumir app novo. A divisão decorre das responsabilidades reais |
| S6 | Mockup | `portal_egresso.html` é referência conceitual; seus componentes e conteúdos não são copiados |

### Verificação no código (base `main` em `5880cb2`)

| Fato | Onde | Consequência para a 025 |
|---|---|---|
| A Conclusão Acadêmica tem curso, unidade, nível, modalidade, forma de oferta e ano, todos como texto da fonte, sem catálogo | `trajetoria/academico/models.py`; 001/DP-007; 010/DP-1005 | A pertinência só pode comparar esses textos por igualdade exata |
| **Não existe classificação de área do conhecimento**, eixo tecnológico, área CNPq, CINE ou equivalente, em curso nenhum | Busca em `trajetoria/`, `specs/` e `docs/` | "Oportunidade da área de tecnologia" não é calculável. O público é dito por **curso, nível ou unidade**, nunca por área |
| **Não existe identificador estável de curso.** A Conclusão só tem o `id_externo` do próprio registro da conclusão. O contrato da fonte (`ConclusaoNaFonte`) não transporta código de curso, de matriz nem de oferta | `trajetoria/fonte_academica/contrato.py`; `trajetoria/academico/models.py` | O curso é identificado pelo texto registrado. Incluir um código de curso exigiria mudar o contrato da fonte (001), o que fica fora desta feature (DP-2507) |
| A fonte simulada usa **uma única** grafia por curso. Ana e Maria têm a mesma constante (`TADS` = "Tecnologia em Análise e Desenvolvimento de Sistemas"). *(Corrigido em 2026-10-08, no plan: a versão anterior desta linha afirmava duas grafias, com base num resumo não conferido na fonte.)* Na fonte real, grafias divergentes continuam possíveis (DP-1005; 001/DP-007) | `trajetoria/fonte_academica/cenarios.py` | A limitação da comparação exata é real, mas a demonstração não a exercita. Os testes a exercitam com uma Conclusão de teste |
| A abrangência da Campanha compara conjuntos de valores com igualdade exata: todos os critérios definidos, qualquer valor do conjunto | 004 FR-018 a FR-022; ADR 0004 | A semântica de comparação é reaproveitada. O conceito não é: abrangência de Campanha não é público de divulgação (ADR 0004) |
| A governança tem dois papéis, CPAEG (institucional) e CSAEG (por unidade, em texto), e uma regra nomeada por ação | `trajetoria/governanca/`; 010 FR-028 a FR-034 | A curadoria vira uma regra nova, nomeada, no mesmo padrão |
| A PAEG atribui à CSAEG a gestão do Portal do Egresso na unidade | PAEG Art. 13, parágrafo único; Art. 22, III; 010 A14 | Fundamento para a CSAEG curar na própria unidade. A atuação institucional não tem artigo equivalente (DP-2501) |
| Operadores só existem como fictícios da demonstração, escolhidos numa tela própria | `trajetoria/demonstracao/operador.py`; 010/DP-1001 | A curadoria reaproveita essa identificação |
| Telas de operação seguem o padrão do `/acompanhamento/` e da gestão de Campanha (017): lista, formulário, confirmação explícita, conflito. Sem Django admin | `trajetoria/acompanhamento/`; 017 FR-018 a FR-021 | As telas de curadoria seguem o mesmo padrão |
| O estado da Campanha é **derivado** das datas; nenhum processo grava o encerramento por data | `trajetoria/campanha/consultas.py` (`estado`); 004 FR-038 | A expiração da divulgação segue o mesmo princípio, sem tarefa agendada |
| Escritas de operador desde a 019 guardam o identificador opaco do operador e o momento, sem tabela de histórico | `declaracao/models.py`; `mobilizacao/models.py` | Precedente para registrar quem publicou e quem retirou |
| O Portal vive num módulo próprio, sem modelos nem migrações. Um teste verifica isso, e outro verifica que nada fora dele cita o Portal | `trajetoria/portal/`; `tests/portal/test_fronteiras.py` | A 025 precisa decidir onde vive o primeiro fato persistente da camada (seção "Modularização") |
| O Início proíbe hoje as palavras "Oportunidade", "Volte ao Ifes" e "comunidade", e a navegação tem exatamente quatro itens | 024 FR-021 e FR-023; `tests/portal/test_inicio.py`; `tests/portal/test_navegacao.py` | A 025 revisa esses requisitos de forma explícita ("Requisitos revisados") |
| O Início omite um bloco quando não há o que mostrar e não usa grade de cartões nem JavaScript | 024 FR-026; research R10 | A área de Oportunidades segue as mesmas regras |
| A 375 px, os quatro itens da navegação já ocupam a largura inteira da linha. O convite à pesquisa fica na segunda tela do Início | 024 `evidencias/02` e `03` | Um quinto item quebra a navegação em duas linhas. Cada bloco antes do convite o empurra para baixo ("Início e acesso à pesquisa") |
| As auditorias de esforço medem o caminho do convite (`/acesso/` → escolha de formações → Seções) em telas, toques e rolagem. Esse caminho não passa pelo Início | Reauditoria de 2026-10-06, cenário A; 024 SC-002 | A 025 não pode tocar esse caminho, e o Início não pode esconder a pesquisa |

### O que é reutilizado

| Capacidade existente | Uso na 025 |
|---|---|
| Sessão e identificação do egresso (018) e entrada do Portal (024) | Quem vê Oportunidades. Nenhum mecanismo novo |
| Conclusões Acadêmicas da Pessoa, na ordem da 007 | Única base da pertinência e da explicação |
| Regra positiva da trajetória (024 FR-009: ao menos uma Conclusão) | Mesma condição para ver Oportunidades |
| Semântica de critérios de conjunto da Campanha (004 FR-020, FR-022) | Comparação do público com a Conclusão |
| `VinculoDeGovernanca` e o escopo de acompanhamento (CPAEG institucional; CSAEG pelas próprias unidades) | Escopo da curadoria |
| Identificação de operador fictício da demonstração | Quem cura, na demonstração |
| Padrão de telas da gestão de Campanha (017): formulário acessível, confirmação, conflito, avisos de vocabulário fechado | Telas de curadoria |
| Estado derivado de datas (004, 017) | Expiração automática |
| Shell, navegação, tokens e componentes da 015 e da 024 (`lista-simples`, origem em texto, `a.botao`) | Página de Oportunidades e bloco do Início, sem tokens novos |
| Interruptor da camada (`Portal desabilitado`, 024 FR-027) e modo de demonstração | Desliga também as Oportunidades |
| Preparação da demonstração | Catálogo fictício |

**Nada do mockup é copiado.** Ele foi conferido e diverge em pontos já decididos:

- quatro das seis razões dele usam dado declarado ou interesse ("experiência declarada",
  "seu interesse em…", "doutorado declarado", "sua área de atuação");
- filtros por categoria dependem de JavaScript;
- os cartões ficam em grade;
- "Encontro de egressos" e "comunidade" esbarram em vetos já registrados.

Só a ideia do **"Por que estou vendo isto?"**, já adotada no roadmap (§3.3), é aproveitada,
agora com regra explícita e por item.

## Modularização: decisão a partir das responsabilidades

A feature tem três responsabilidades:

1. **O fato Oportunidade**: o que foi curado, por quem, para quem e até quando.
2. **A curadoria**: telas do operador, autorizadas por governança e escopo.
3. **A apresentação ao egresso**: página e bloco do Início, com a pertinência calculada na
   consulta.

As três só têm sentido com a camada de relacionamento ligada. Nenhuma tem consumidor no
núcleo. A pertinência lê o núcleo (Conclusões); nada no núcleo lê Oportunidades.

| Alternativa | Avaliação |
|---|---|
| **A. Oportunidade vive na camada de relacionamento que já existe, junto da experiência do Portal** | **Escolhida.** Uma única fronteira: a camada depende do núcleo, o núcleo não cita a camada. O teste que já existe continua valendo, e ao desligar a camada saem juntas a página do egresso e a curadoria. Custo: revisar o invariante da 024 de que a camada "não tem modelos nem migrações" (FR-029 da 024). Isso estava previsto: o roadmap dizia "tabelas novas só nas specs S2 e S3" |
| B. Módulo próprio de Oportunidades, separado do Portal | Rejeitada nesta feature. Hoje a regra de fronteira trata como núcleo tudo o que está fora do Portal. Um módulo à parte exigiria redefinir a camada como um conjunto de módulos e duplicar o desligamento. Fica disponível se a 026 (Manifestação) mostrar que a camada cresceu a ponto de pedir divisão |
| C. Oportunidade no núcleo (por exemplo, junto do acompanhamento) | Vetada. Violaria a Constituição 2.1.0 ("Camada de relacionamento"): fatos próprios do relacionamento pertencem à camada |

**Conclusão: não é preciso app novo.** Oportunidade é o primeiro fato persistente da camada
de relacionamento e vive nela. A organização interna (submódulos, arquivos) é decisão do
plan. A regra de curadoria é um predicado sobre os vínculos de governança. Se ela ficar no
módulo de governança, isso é compatível com a fronteira desde que o núcleo continue sem
importar nem citar a camada. Essa escolha também fica para o plan.

## Modelo mínimo: cada atributo justificado por um fluxo

| Hipótese | Fluxo que exige | Decisão |
|---|---|---|
| Título | O egresso identifica a oportunidade; o operador a reconhece na lista | **Entra** |
| Resumo curto | O egresso decide se vale abrir o link sem sair do Portal | **Entra**, como texto simples curto. Corpo longo, formatação ou anexos fariam dela um CMS |
| Endereço oficial | É o único caminho até o conteúdo. O Portal não hospeda o conteúdo | **Entra**, obrigatório |
| Unidade responsável | Define o escopo de quem pode editar (governança) e mostra ao egresso quem oferece | **Entra** |
| Início e fim da divulgação | Atenuam o maior risco do roadmap, o portal desatualizado: a oportunidade sai sozinha da vista. O início permite deixar uma publicação agendada | **Entram, ambos obrigatórios.** Um fim opcional deixaria itens vencidos para sempre |
| Situação de publicação | Separa o que o operador ainda prepara do que o egresso vê, e permite retirar antes do fim | **Entra** como três momentos: rascunho, publicada, retirada. "Agendada" e "encerrada" são derivadas das datas |
| Categoria | Ajuda o egresso a reconhecer o tipo à primeira vista e a distinguir oportunidade institucional de anúncio (Checkpoint 2, compreensão 2) | **Entra** como lista fechada curta, só para apresentar. Não filtra nem decide pertinência |
| Público-alvo opcional | Sem ele não há pertinência: tudo seria "para todos" | **Entra**, com três critérios: unidade, nível e curso. Ver "Pertinência" |
| Modalidade, forma de oferta e ano no público | Nenhum fluxo pediu. Ano exigiria regra de recorte (Princípio IX) | **Fica fora** |
| Prazo de inscrição, vagas, local, data do evento | Pertencem ao conteúdo oficial | **Ficam fora.** O resumo pode mencioná-los, e a página oficial é a autoridade |
| Autor da criação, histórico de edições | Nenhum fluxo da curadoria depende disso | **Ficam fora.** Só se registra quem publicou e quem retirou, e quando (FR-033) |
| Imagem, destaque, ordem manual, contagem de cliques | Marketing ou rastreamento | **Ficam fora** |

## Pertinência

### Regra

Uma Oportunidade **aparece** para a Pessoa numa data D quando:

1. está **em divulgação** em D: foi publicada, não foi retirada e início ≤ D ≤ fim; **e**
2. vale um dos casos:
   - **ela não tem público**: é aberta a todos os egressos;
   - **ela tem público**, e ao menos **uma mesma** Conclusão Acadêmica da Pessoa satisfaz,
     sozinha, **todos** os critérios definidos. Cada critério é um conjunto de valores,
     satisfeito quando o valor da Conclusão é **igual** a um deles, sem normalização (mesma
     semântica da 004 FR-020 e FR-022).

**Os critérios nunca se combinam entre formações diferentes.** Exemplo: uma oportunidade com
público "Pós-graduação **e** Vila Velha" não aparece para quem tem uma Pós-graduação no Cefor
e uma Graduação em Vila Velha. Nenhuma formação dessa pessoa é, ao mesmo tempo, Pós-graduação
e de Vila Velha.

Uma oportunidade aparece no máximo uma vez, mesmo que mais de uma formação a satisfaça.

### Identificação do curso

- **Não há identificador estável de curso a reutilizar** ("Verificação no código"). O curso é
  identificado pelo texto que a fonte registra na Conclusão.
- **A comparação é exata.** Não há correspondência aproximada, sinônimos nem normalização de
  caixa, espaços ou acentos. Também não se cria catálogo paralelo de cursos.
- **Para tornar a limitação visível e administrável,** o operador escolhe os cursos numa lista
  com todos os valores registrados, exatamente como estão escritos. Grafias diferentes
  aparecem como opções diferentes, e ele marca as que se aplicam (FR-007).
- **Se a fonte real vier a fornecer um código de curso estável,** a troca do critério de
  curso por esse código é evolução do contrato da fonte (001), registrada como DP-2507. Não
  é feita aqui.

### Explicação

Cada item mostra **por que** aparece, numa frase gerada pela própria regra, sem texto livre
do operador:

| Caso | Exemplo de explicação (texto final no plan) |
|---|---|
| Sem público | "Aberta a todos os egressos do Ifes." |
| Público por curso | "Aparece porque você concluiu Tecnologia em Redes de Computadores (Serra, 2023)." |
| Público por nível | "Aparece porque você concluiu Mestrado Profissional em Química, formação de Pós-graduação (Vila Velha, 2020)." |
| Público por unidade | "Aparece porque você concluiu Bacharelado em Engenharia Civil na unidade Vitória (2020)." |
| Mais de um critério | Uma só frase com a formação que satisfaz, citando os critérios definidos |
| Várias formações satisfazem | Todas são citadas, na ordem da 007 |

*A forma final dos textos está em [contracts/pertinencia.md](contracts/pertinencia.md) (plan, R7).
Exemplos ajustados em 2026-10-08, depois do `/speckit-analyze`: "unidade" em vez de "campus",
como na 021 e na 024 (o Cefor não é campus).*

A explicação cita **só** os critérios que a oportunidade define e **só** fatos institucionais
da formação. Ela nunca usa Resposta, Formação Declarada, contato, nome nem comportamento.

### Por que essa regra e não outra

- **Área do conhecimento** não existe no domínio. Criá-la seria um catálogo institucional
  novo, com dono e manutenção (DP-1005, 001/DP-007), fora do escopo.
- **Interesses declarados** seriam dado sem consumidor validado (XVI). O roadmap os adia.
- **Curso, nível e unidade** já estão em toda Conclusão, vêm da fonte institucional e cabem
  numa frase compreensível.
- **Limite aceito:** "oportunidade de tecnologia para quem fez Redes" só funciona se o
  operador listar os cursos. Os valores oferecidos ao operador vêm das Conclusões já
  registradas, para evitar erro de digitação (FR-007).

## Quem administra × para quem se destina

São duas dimensões independentes, e a spec não deriva uma da outra:

| Dimensão | O que decide | Quem define | Regra |
|---|---|---|---|
| **Administração** | Quem pode ver, cadastrar, editar, publicar e retirar a oportunidade na curadoria | A unidade responsável, pelo escopo de governança | A CSAEG só administra oportunidades com unidade responsável entre as suas unidades. A CPAEG administra todas e é a única que usa "Ifes (institucional)" (FR-025, FR-026) |
| **Público** | Quais egressos veem a oportunidade no Portal | Atributo do conteúdo, escolhido por quem a administra | Qualquer combinação de unidades, níveis e cursos, ou nenhuma (todos os egressos). Isso vale também para a CSAEG, como hipótese da demonstração (FR-026; DP-2502) |

**Cenário que motivou a separação.** A unidade Vitória oferece uma especialização aberta a
egressos de todas as unidades. A CSAEG Vitória a cadastra com unidade responsável Vitória e sem
público. Ela continua sendo a única unidade que a administra. Um egresso da Serra a vê com a
explicação "Aberta a todos os egressos do Ifes" e com "Oferecida pela unidade Vitória".

**Por que isso não amplia permissões indevidamente:**

- **O escopo de administração não muda.** A CSAEG não vê nem altera oportunidade de outra
  unidade.
- **Definir um público não dá acesso a nenhum dado de egresso.** A curadoria não mostra
  quem casa com o público, nem quantos. Os valores oferecidos (cursos, níveis e unidades)
  são designações institucionais, não dados de pessoas.
- **A regra é reversível sem mudar o modelo.** Se a instância competente limitar o alcance
  por unidade (DP-2502), basta uma validação a mais no público.

## Estados de publicação

O modelo guarda só dois momentos: **publicada em** e **retirada em**, cada um com o operador.
Junto das datas de início e fim da divulgação e da data de hoje, eles determinam o estado.
Nenhum processo agendado é necessário.

| Estado | Publicada em | Retirada em | Datas | O egresso vê? |
|---|---|---|---|---|
| **Rascunho** | vazio | vazio | quaisquer | Não |
| **Agendada** | preenchido | vazio | hoje < início | Não |
| **Em divulgação** | preenchido | vazio | início ≤ hoje ≤ fim | **Sim** |
| **Encerrada** | preenchido | vazio | hoje > fim | Não |
| **Retirada** | qualquer | preenchido | quaisquer | Não |

Regras sem ambiguidade:

1. **A data nunca autoriza sozinha.** Só a publicação explícita, feita por quem tem a
   competência, preenche "publicada em". Um Rascunho com período em curso continua
   invisível.
2. **Publicar é o ato de autorização.** Não há etapa separada de aprovação. A Agendada já
   está autorizada e só espera a data de início.
3. **O último dia é inclusivo.** A oportunidade aparece durante todo o dia do fim, no fuso do
   projeto, e deixa de aparecer a partir da 0h do dia seguinte. A primeira data é inclusiva
   do mesmo modo.
4. **A retirada prevalece sobre tudo.** Ela é definitiva, vale imediatamente e é possível em
   Rascunho (descarte), Agendada e Em divulgação. Encerrada não é retirada, porque já não
   aparece. Retirada não volta a nenhum estado. Para divulgar de novo, cadastra-se outra
   oportunidade.
5. **Encerrar antes do fim é retirar.** Na edição de uma oportunidade publicada, o fim não
   pode ficar antes de hoje. Assim, um encerramento antecipado nunca acontece sem o registro
   de quem retirou.
6. **Momentos coerentes.** "Retirada em" nunca é anterior a "publicada em". Uma oportunidade
   retirada não pode ser publicada.

## Links oficiais: validação mínima

HTTPS garante a conexão, não a confiabilidade de quem publica. A spec não cria lista de
domínios nem verificação automática. Ela adota quatro medidas proporcionais:

1. **Forma do endereço.** O sistema recusa:
   - endereço que não seja absoluto em `https://`;
   - endereço com usuário ou senha embutidos;
   - endereço cujo destino seja um número IP em vez de um nome de domínio;
   - endereço com espaços;
   - endereço com mais de 500 caracteres.

   São as formas mais comuns de disfarçar um destino.
2. **Origem explícita.** O sistema classifica o domínio só para exibir:
   - **site do Ifes**, quando o domínio é `ifes.edu.br` ou um subdomínio dele;
   - **site externo**, caso contrário.

   O egresso vê sempre o domínio e essa classificação junto do link, por exemplo "site
   externo: www.gov.br". Na confirmação de publicação, o operador vê o domínio completo em
   destaque e um aviso quando o site é externo.
3. **Parceiros legítimos são admitidos** provisoriamente como site externo, sob
   responsabilidade de quem publica. O registro de quem publicou (FR-033) e a retirada
   imediata (FR-031) cobrem o erro. Exigir lista de parceiros ou autorização extra é
   decisão institucional (DP-2504).
4. **Nada é acrescentado ao endereço.** O link não ganha parâmetro de rastreamento nem dado
   da pessoa. O sistema não acessa o endereço.

## Início e acesso à pesquisa (mobile-first)

As auditorias de esforço mediram o caminho do convite. Esse caminho não passa pelo Início e
fica intacto: nenhuma tela, toque ou rolagem a mais (024 SC-002). No caminho do Portal, a
pesquisa tem hoje duas portas:

- o item "Pesquisa" da navegação, no topo de toda página do Portal;
- o convite no fim do Início, que já fica na segunda tela a 375×812 (024 `evidencias/03`).

| Alternativa para o Início | Efeito estimado no convite a 375×812 | Avaliação |
|---|---|---|
| Até três oportunidades completas (versão anterior desta spec) | Desce cerca de meia tela: três itens com título, explicação e link | **Rejeitada.** Afasta a pesquisa justamente quando há mais oportunidades |
| Bloco depois do convite | Não desce | Rejeitada. Contraria "valor antes do pedido" e deixa a oportunidade abaixo do fim provável da leitura |
| **Um destaque e o caminho para as demais** | Desce no máximo um terço de tela | **Escolhida.** Mostra uma oportunidade real com a explicação (o "por que" fica visível já no Início) e o link para as demais |

Garantias, todas verificáveis:

- **Convite.** O convite continua único e com o mesmo texto e a mesma ação por situação (024
  FR-020). A 375×812, com fonte a 100%, ele não desce mais que 270 px em relação à
  mesma persona sem o bloco (SC-008).
- **Navegação.** O item "Pesquisa" continua presente e a um toque em toda página do Portal.
- **Caminho do convite.** A escolha de formações, as Seções e o caminho do convite não mudam.
- **Navegação com cinco itens.** Ela quebra em linhas, sem rolagem horizontal de 320 a 1280
  px, com fonte de 100% a 200%. Cada item mantém alvo de 44×44 px e indicação de página
  atual. A 375×812, com fonte a 100%, o `h1` e a síntese do reconhecimento continuam acima da
  dobra (024 SC-004).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Encontrar oportunidades pertinentes e entender por que aparecem (Priority: P1)

Carla concluiu Tecnologia em Redes de Computadores no campus Serra. Ela entra pelo Portal e,
no Início, depois das próprias formações e do que pode fazer, vê um bloco de Oportunidades.
Há uma especialização em Segurança da Informação com a frase "Aparece porque você concluiu
Tecnologia em Redes de Computadores (Serra, 2023)". Ela abre a página de Oportunidades, vê
também um evento aberto a todos os egressos e segue o link para a página oficial do curso.
Ela não preencheu nada.

**Why this priority**: é o valor que o Portal oferece antes de pedir. Sem ele, a 025 não tem
o que testar no Checkpoint 2.

**Independent Test**: com o catálogo fictício e a Pessoa Carla, abrir o Início e a página de
Oportunidades. Deve aparecer cada oportunidade esperada pela regra, com a explicação certa e
o link oficial, e nenhuma oportunidade dirigida a outro curso ou unidade.

**Acceptance Scenarios**:

1. **Given** uma Pessoa com Conclusão em Redes de Computadores (Serra) e uma oportunidade em
   divulgação com público curso = Redes de Computadores, **When** ela abre a página de
   Oportunidades, **Then** a oportunidade aparece no grupo "Pela sua formação", com a
   explicação que cita essa formação.
2. **Given** uma oportunidade em divulgação sem público, **When** qualquer Pessoa com ao
   menos uma Conclusão abre a página, **Then** a oportunidade aparece no grupo "Para todos os
   egressos", com a explicação "aberta a todos os egressos".
3. **Given** uma oportunidade com público unidade = Vitória, **When** uma Pessoa sem nenhuma
   Conclusão em Vitória abre a página, **Then** a oportunidade não aparece.
4. **Given** uma oportunidade com público nível = Pós-graduação **e** unidade = Vila Velha,
   **When** uma Pessoa com Pós-graduação no Cefor e Graduação em Vila Velha abre a página,
   **Then** a oportunidade não aparece, porque nenhuma formação satisfaz os dois critérios.
5. **Given** uma Pessoa com duas formações que satisfazem o público, **When** abre a página,
   **Then** a oportunidade aparece uma vez, e a explicação cita as duas formações na ordem da
   007.
6. **Given** um item exibido, **When** a pessoa ativa o link, **Then** vai direto ao endereço
   oficial. O texto do link mostra o domínio e diz se é site do Ifes ou site externo.
7. **Given** a página de Oportunidades aberta, **When** é recarregada várias vezes, **Then** a
   lista, a ordem e as explicações são as mesmas, e nada é gravado.
8. **Given** quatro oportunidades pertinentes e uma pesquisa a iniciar, **When** a Pessoa abre
   o Início, **Then** o bloco mostra só a primeira na ordem do FR-016, com a explicação e o
   link oficial, mais um link para a página com as demais. O convite à pesquisa vem depois,
   com o mesmo texto e ação de hoje.
9. **Given** uma oportunidade da unidade Vitória aberta a todos, **When** um egresso da Serra
   abre a página, **Then** ela aparece com "Aberta a todos os egressos do Ifes" e "Oferecida
   pela unidade Vitória".

---

### User Story 2 — Operador da unidade cadastra e publica uma oportunidade (Priority: P1)

A pessoa que atua pela CSAEG da unidade Vitória escolhe o operador fictício correspondente.
Ela cadastra "Especialização em Gestão Pública — inscrições abertas", com resumo, categoria
"Cursos e formação continuada", endereço oficial, divulgação de 10/10 a 30/11 e público
unidade = Vitória. Ela revisa como o egresso verá e publica.

**Why this priority**: sem curadoria não há conteúdo. É a operação contínua de que a área
depende.

**Independent Test**: com o operador CSAEG Vitória, cadastrar, editar, publicar e conferir
que a oportunidade aparece para Bruno (Vitória) e não aparece para Ana (Serra).

**Acceptance Scenarios**:

1. **Given** um operador com vínculo CSAEG ativo em Vitória, **When** abre a curadoria,
   **Then** vê só as oportunidades com unidade responsável Vitória, em qualquer estado.
2. **Given** o formulário preenchido corretamente, **When** salva, **Then** a oportunidade
   fica em Rascunho e não aparece a nenhum egresso.
3. **Given** um Rascunho, **When** o operador pede para publicar, **Then** vê uma
   confirmação com a prévia (título, resumo, categoria, unidade, domínio do link), o
   público descrito em linguagem simples e o período. Ao confirmar, a oportunidade passa a
   Agendada ou Em divulgação, conforme a data de início.
4. **Given** o operador CSAEG Vitória, **When** tenta definir unidade responsável Serra ou
   "Ifes (institucional)", **Then** o pedido é rejeitado com mensagem compreensível, e nada
   é gravado.
5. **Given** o operador CSAEG Vitória, **When** cadastra uma especialização com unidade
   responsável Vitória e sem público, ou com público unidade = Serra, **Then** o sistema
   aceita. Depois de publicada, um egresso da Serra a vê com "Oferecida pela unidade Vitória".
   Só operadores com escopo em Vitória, e a CPAEG, a administram. [Hipótese; DP-2502]
6. **Given** um endereço que não é `https://` absoluto, com usuário ou senha, com número IP
   como destino, com espaços ou longo demais, ou um título vazio ou longo demais, um resumo
   longo demais, ou um fim anterior ao início, **When** salva, **Then** cada erro aparece
   junto do campo, de forma acessível, e nada é gravado.
7. **Given** um endereço válido fora de `ifes.edu.br`, **When** o operador pede para
   publicar, **Then** a confirmação mostra o domínio completo e avisa que é site externo.
   Ao egresso, o link aparece como "site externo", com o domínio.
8. **Given** uma oportunidade Em divulgação, **When** o operador corrige o resumo, **Then** a
   correção vale na próxima vez em que o egresso abrir a página.
9. **Given** um operador sem vínculo ativo, **When** abre a curadoria, **Then** recebe a recusa
   padrão da governança, sem ver nenhuma oportunidade.

---

### User Story 3 — Retirada e expiração sem trabalho manual (Priority: P1)

Uma oportunidade divulgada até 30/11 some da vista do egresso a partir de 01/12, sem que
ninguém faça nada. Outra precisa sair antes do prazo porque as inscrições lotaram. O
operador a retira, e ela sai na hora.

**Why this priority**: o maior risco do roadmap é o portal desatualizado. A expiração
automática e a retirada simples são a mitigação.

**Independent Test**: com uma data de referência controlada, conferir uma oportunidade no
último dia e no dia seguinte do período. Depois, retirar outra e conferir que sumiu.

**Acceptance Scenarios**:

1. **Given** uma oportunidade publicada com fim em D, **When** o egresso consulta em D,
   **Then** ela aparece. **When** consulta em D+1, **Then** ela não aparece, e nenhum processo
   nem pessoa precisou agir.
2. **Given** uma oportunidade publicada com início em D+5, **When** o egresso consulta em D,
   **Then** ela não aparece. O operador a vê como Agendada.
3. **Given** uma oportunidade Em divulgação, **When** o operador a retira e confirma, **Then**
   ela deixa de aparecer ao egresso imediatamente e fica como Retirada na curadoria, com quem
   retirou e quando.
4. **Given** uma oportunidade Encerrada ou Retirada, **When** o operador tenta editá-la,
   publicá-la ou retirá-la, **Then** a ação não está disponível. Para divulgar de novo, ele
   cadastra outra.
5. **Given** dois operadores com a mesma oportunidade aberta, **When** um a retira e o outro
   confirma a publicação ou a edição, **Then** o segundo vê a página de conflito, e nada é
   gravado.
6. **Given** um Rascunho cujo período já está em curso, **When** o egresso consulta, **Then**
   ele não aparece. A data nunca autoriza a divulgação sozinha.
7. **Given** uma oportunidade Em divulgação, **When** o operador tenta mudar o fim para antes
   de hoje, **Then** o pedido é rejeitado com a indicação de que, para encerrar antes do
   prazo, deve retirá-la.
8. **Given** um Rascunho, **When** o operador o retira, **Then** ele fica como Retirada sem
   nunca ter sido visível, e não pode mais ser publicado.

---

### User Story 4 — Curadoria institucional (Priority: P2)

A pessoa que atua pela CPAEG divulga um curso de extensão a distância oferecido pelo Cefor
para todos os egressos do Ifes e uma especialização da Reitoria só para quem concluiu
Pós-graduação, em qualquer unidade.

**Why this priority**: sem atuação institucional não há oportunidade "para todos". A
fundamentação dela é mais fraca que a da CSAEG (DP-2501), por isso P2.

**Independent Test**: com o operador CPAEG, publicar uma oportunidade sem público e outra com
público nível = Pós-graduação. A primeira deve aparecer a todas as personas com Conclusão; a
segunda, só a Maria e Diego.

**Acceptance Scenarios**:

1. **Given** um operador CPAEG, **When** abre a curadoria, **Then** vê as oportunidades de
   todas as unidades e as institucionais.
2. **Given** um operador CPAEG, **When** cadastra uma oportunidade sem público e com unidade
   responsável "Ifes (institucional)", **Then** o sistema aceita.
3. **Given** uma oportunidade de unidade, **When** o operador CPAEG a edita ou retira,
   **Then** o sistema aceita, e o registro de retirada identifica esse operador.

---

### User Story 5 — Sem oportunidades, o Portal não finge (Priority: P2)

Fernanda concluiu Técnico em Mecânica em Cariacica. Hoje não há nenhuma oportunidade dirigida a
ela nem aberta a todos. O Início não mostra o bloco. Pela navegação, ela abre Oportunidades e
lê uma frase verdadeira, sem promessa de prazo.

**Why this priority**: o estado vazio é o mais provável na operação real. Ele não pode virar
área de fachada.

**Independent Test**: com o catálogo esvaziado, ou com uma persona fora de todos os públicos e
sem oportunidades abertas em divulgação, abrir o Início e a página.

**Acceptance Scenarios**:

1. **Given** nenhuma oportunidade pertinente em divulgação, **When** a Pessoa abre o Início,
   **Then** o bloco de Oportunidades não existe na página: nem título, nem frase.
2. **Given** a mesma situação, **When** abre a página de Oportunidades, **Then** lê que, no
   momento, não há oportunidades divulgadas para as formações dela e que novas oportunidades
   aparecem ali quando o Ifes as divulga. Não há prazo, cobrança nem menção à pesquisa.
3. **Given** só oportunidades encerradas, retiradas, agendadas ou em rascunho, **When** a
   Pessoa abre a página, **Then** o resultado é o estado vazio. Nenhuma delas aparece.

---

### User Story 6 — A coleta e o núcleo não percebem as Oportunidades (Priority: P2)

A equipe técnica desliga a camada do Portal. As oportunidades cadastradas continuam no
banco, mas nenhuma tela as mostra, nem ao egresso nem ao operador. O convite, a jornada, o
snapshot e as exportações funcionam exatamente como antes.

**Why this priority**: é a garantia verificável da Constituição 2.1.0 e do ADR 0008.

**Independent Test**: com oportunidades publicadas, gerar snapshot e exportações e
compará-los com os gerados sem oportunidades. Depois, desligar a camada e percorrer o convite.

**Acceptance Scenarios**:

1. **Given** oportunidades publicadas, **When** se gera o snapshot de uma Campanha encerrada e
   as exportações, **Then** o conteúdo é idêntico ao de uma base sem oportunidades.
2. **Given** a camada desligada, **When** se abrem a página de Oportunidades ou a curadoria,
   **Then** a resposta é "não encontrado".
3. **Given** a camada desligada, **When** se percorre o caminho do convite, **Then** ele é o
   mesmo da 024 (SC-005 da 024).

---

### Edge Cases

- **Pessoa identificada sem nenhuma Conclusão Acadêmica.** Não há item de navegação nem bloco
  no Início. O pedido direto à página leva ao Início, sem revelar oportunidades. A pertinência
  não considera Formação Declarada (Princípio III; 019).
- **Sessão de declarante (019).** Não tem acesso, como no Início (024 FR-004).
- **Sessão expirada na página de Oportunidades.** Volta à entrada do Portal, como as demais
  páginas do Portal (024 FR-007).
- **Conclusão sem curso, unidade ou nível na fonte.** O critério correspondente não é
  satisfeito por ausência. Não há dedução.
- **A grafia de uma unidade ou curso muda na fonte (DP-1005, 001/DP-007).** O público antigo
  deixa de casar. A curadoria mostra só valores atuais, e o operador revê o público. Risco
  registrado.
- **Público com um curso que hoje nenhuma Conclusão registra.** Não é possível: os valores
  oferecidos vêm das Conclusões existentes. Se o valor sumir da fonte depois, a oportunidade
  simplesmente não aparece a ninguém.
- **CSAEG com vínculo em duas unidades.** O escopo é a união das unidades. O público pode
  combinar as duas.
- **O vínculo do operador que publicou é desativado.** A oportunidade continua até o fim do
  período. A CPAEG, ou outro operador da mesma unidade, pode retirá-la.
- **Fim no passado na hora de publicar.** A publicação é rejeitada. Início no passado é
  aceito, e a oportunidade entra em divulgação na hora.
- **Títulos repetidos.** São permitidos. Cada oportunidade é um registro próprio.
- **Página oficial fora do ar ou alterada.** O sistema não verifica o link. O operador retira
  a oportunidade. Risco registrado.
- **Muitas oportunidades pertinentes.** A página lista todas, na ordem do FR-016, e o Início
  mostra só a primeira. Paginação fica fora até haver volume real (Princípio XXII).
- **Duas grafias do mesmo curso** (caso possível na fonte real; nos testes, por exemplo,
  "Tecnologia em Análise e Desenvolvimento de Sistemas" e "Análise e Desenvolvimento de
  Sistemas"). São valores distintos. A oportunidade só alcança as duas se o operador marcar
  as duas.
- **Critérios satisfeitos por formações diferentes.** Não bastam. Todos os critérios precisam
  ser satisfeitos por uma mesma Conclusão (FR-012).
- **Endereço de parceiro** (por exemplo, `gov.br`). É aceito como site externo, com o domínio
  à vista (FR-004).
- **Parâmetros na URL da página de Oportunidades.** São ignorados. Nenhum parâmetro filtra,
  ordena ou redireciona.

## Requirements *(mandatory)*

### Functional Requirements

#### A Oportunidade

- **FR-001**: DEVE existir a **Oportunidade**: conteúdo institucional curado que aponta para
  uma página oficial. Ela tem só estes atributos:
  - título;
  - resumo;
  - categoria;
  - unidade responsável;
  - endereço oficial;
  - início e fim da divulgação;
  - público, opcional;
  - os momentos de publicação e de retirada, com o operador de cada um.

  NÃO DEVE ter corpo longo, formatação, imagem, anexo, prazo de inscrição, vagas, local, data
  de evento, destaque, ordem manual nem contador. [Arquitetura; roadmap S2; Const. XXII]
- **FR-002**: Título e resumo DEVEM ser texto simples, sem formatação nem marcação, exibido
  sempre como texto.
  - Título: obrigatório, até 120 caracteres.
  - Resumo: obrigatório, até 300 caracteres.

  [Hipótese; anti-CMS]
- **FR-003**: A categoria DEVE ser escolhida numa lista fechada:
  - Cursos e formação continuada;
  - Eventos;
  - Pesquisa e extensão;
  - Carreira e empregabilidade;
  - Empreendedorismo;
  - Outras iniciativas.

  A categoria só é apresentada. NÃO DEVE decidir pertinência, ordem nem filtro. [Hipótese;
  DP-2505]
- **FR-004**: O endereço oficial DEVE ser obrigatório e passar pela validação mínima da seção
  "Links oficiais". Ele DEVE:
  - ser absoluto em `https://`;
  - não conter usuário nem senha;
  - ter um nome de domínio como destino, não um número IP;
  - não conter espaços;
  - ter no máximo 500 caracteres.

  O domínio DEVE ser classificado, só para exibição, como **site do Ifes** (`ifes.edu.br` e
  subdomínios) ou **site externo**. O egresso vê o domínio e a classificação junto do link.
  O operador os vê em destaque na confirmação de publicação, com aviso quando o site é
  externo.

  O sistema NÃO DEVE buscar, copiar, incorporar nem verificar o conteúdo do endereço, nem
  acrescentar parâmetros a ele. [Arquitetura; Const. XVI; DP-2504]
- **FR-005**: A unidade responsável DEVE ser uma destas opções:
  - uma unidade, com a mesma designação textual usada nas Conclusões Acadêmicas e nos
    vínculos de governança (DP-1005);
  - "Ifes (institucional)".

  [Arquitetura; 010]
- **FR-006**: Início e fim da divulgação DEVEM ser datas obrigatórias, com início ≤ fim, no
  fuso do projeto. O período inclui o dia do fim inteiro. [Arquitetura; mesmo tratamento da
  004]
- **FR-007**: O público, quando definido, DEVE ter de um a três critérios de conjunto, cada um
  opcional e, se definido, não vazio: **unidades**, **níveis** e **cursos**.
  - Sem nenhum critério, a oportunidade é **aberta a todos os egressos**.
  - Os valores oferecidos ao operador DEVEM vir dos valores já registrados nas Conclusões
    Acadêmicas de todas as unidades, exatamente como escritos. Grafias diferentes aparecem
    como opções diferentes.
  - Não se cria catálogo, não se digita valor livre e não há correspondência aproximada.
  - O curso é identificado pelo texto, porque não existe identificador estável a reutilizar
    (DP-2507).

  [Arquitetura; Const. XXII; DP-1005; 001/DP-007]
- **FR-008**: O público da Oportunidade é conceito próprio da camada de relacionamento. Ele
  NÃO DEVE ler, alterar nem ser derivado da abrangência de uma Campanha (ADR 0004). Só a
  semântica de comparação é a mesma (004 FR-020, FR-022). [ADR 0004; Const. VII]
- **FR-009**: Os estados observáveis DEVEM ser derivados dos momentos registrados e das
  datas, sem coluna de estado gravada:

  | Estado | Condição |
  |---|---|
  | Rascunho | não publicada e não retirada |
  | Agendada | publicada, não retirada, hoje < início |
  | Em divulgação | publicada, não retirada, início ≤ hoje ≤ fim |
  | Encerrada | publicada, não retirada, hoje > fim |
  | Retirada | retirada, com ou sem publicação anterior |

  Valem as seis regras da seção "Estados de publicação":
  - a data nunca autoriza sozinha;
  - publicar é a autorização;
  - início e fim são inclusivos;
  - a retirada prevalece e é definitiva;
  - encerrar antes do fim é retirar;
  - os momentos são coerentes.

  Nenhum processo DEVE gravar o encerramento por data. [Arquitetura; precedente 004/017]
- **FR-010**: Esta feature NÃO DEVE oferecer exclusão de Oportunidade. Retirada e encerrada
  continuam visíveis na curadoria. A retenção é DP-2506. [Const. XXVII; XXIX]

#### Pertinência

- **FR-011**: Só a Pessoa identificada com ao menos uma Conclusão Acadêmica DEVE ver
  Oportunidades. É a mesma condição da trajetória (024 FR-009). Formação Declarada, Respostas,
  contato, nome e comportamento NÃO DEVEM entrar na pertinência. [Const. II, III; 024]
- **FR-012**: Uma Oportunidade DEVE aparecer para a Pessoa na data D se, e somente se:
  - está Em divulgação em D; **e**
  - não tem público, **ou** ao menos uma mesma Conclusão Acadêmica da Pessoa satisfaz,
    sozinha, todos os critérios definidos. Critérios NÃO DEVEM ser combinados entre
    Conclusões diferentes. Um critério é satisfeito quando o valor da Conclusão é igual a um
    dos valores do conjunto, por igualdade exata, sem normalização, sinônimo, correspondência
    aproximada ou dedução. Valor ausente na Conclusão não satisfaz.

  [Arquitetura; semântica da 004 FR-020 e FR-022]
- **FR-013**: Cada oportunidade exibida DEVE trazer uma explicação, gerada pela regra, que:
  - para a oportunidade sem público, diga que é aberta a todos os egressos do Ifes;
  - para a oportunidade com público, cite só as formações que, cada uma sozinha, a satisfazem
    (curso, unidade e ano), na ordem da 007, e os critérios definidos (curso, nível ou
    unidade);
  - cite a unidade responsável quando ela não for a de nenhuma formação citada (por exemplo,
    "Oferecida pela unidade Vitória");
  - não use nenhum outro dado e não admita texto livre do operador.

  Os textos finais ficam no plan, sujeitos à regra de verdade (014 FR-008). [Hipótese;
  roadmap §3.3; Const. III, IV]
- **FR-014**: A pertinência DEVE ser determinística: com a mesma Pessoa, o mesmo catálogo e a
  mesma data, resultam a mesma lista, a mesma ordem e as mesmas explicações. NÃO DEVE haver
  pontuação, ranking, aprendizado, uso de histórico de visualização nem aleatoriedade.
  [Solicitante S2; Const. XXII]
- **FR-015**: Calcular ou exibir Oportunidades NÃO DEVE gravar nada: nem pertinência, nem
  visualização, nem clique. O link DEVE levar direto ao endereço oficial, sem passar por
  endereço intermediário do sistema. [Const. XVI; roadmap S2]
- **FR-016**: A ordem DEVE ser:
  1. o grupo **"Pela sua formação"** (oportunidades com público);
  2. o grupo **"Para todos os egressos"** (sem público).

  Dentro de cada grupo, vem primeiro o início de divulgação mais recente; o desempate é pelo
  título. [Hipótese]

#### Experiência do egresso

- **FR-017**: DEVE existir a página **Oportunidades**, com:
  - um único `h1`;
  - uma frase curta que diga o que são (oportunidades divulgadas pelo Ifes, com links
    oficiais) e como são escolhidas (pelas formações que o Ifes registra, ou abertas a
    todos);
  - os grupos do FR-016, cada um com título próprio e omitido quando vazio.

  Cada item DEVE mostrar:
  - a categoria, em texto;
  - o título;
  - o resumo;
  - a unidade responsável;
  - a explicação (FR-013);
  - o link ao endereço oficial, cujo nome acessível inclua o título e diga se leva a site do
    Ifes ou a site externo, com o domínio visível (FR-004).

  As datas de divulgação NÃO DEVEM ser exibidas ao egresso, para não se confundirem com prazo
  de inscrição. [Hipótese; Const. XX]
- **FR-018**: Sem oportunidade a exibir, a página DEVE mostrar uma frase verdadeira de estado
  vazio. Ela diz que, no momento, não há oportunidades divulgadas para as formações da pessoa
  e que novas oportunidades aparecem ali quando o Ifes as divulga. NÃO DEVE prometer prazo,
  cobrar nem mencionar a pesquisa. [014 FR-008; Hipótese]
- **FR-019**: Oportunidades em Rascunho, Agendada, Encerrada ou Retirada NÃO DEVEM aparecer ao
  egresso em nenhuma tela. Não há arquivo de encerradas nem página de detalhe. [Arquitetura]
- **FR-020**: A navegação do Portal DEVE ganhar o item **"Oportunidades"**, entre "Minha
  trajetória" e "Pesquisa". Ele aparece para a Pessoa que atende ao FR-011, mesmo quando a
  lista dela está vazia, para manter a navegação estável.
  - O item "Pesquisa" DEVE continuar presente, a um toque, em toda página do Portal.
  - Com cinco itens, a navegação DEVE quebrar em linhas, sem rolagem horizontal de 320 a 1280
    px, com fonte de 100% a 200%.
  - Cada item DEVE manter alvo de 44×44 px e a indicação acessível de página atual.
  - A página de Oportunidades DEVE exibir a navegação.

  [Hipótese; revisa 024 FR-022 e FR-023]
- **FR-021**: O Início DEVE ganhar um bloco **Oportunidades** depois de "O que você pode
  fazer" e antes do convite à pesquisa. O bloco:
  - mostra **uma** oportunidade em destaque, a primeira pela ordem do FR-016, com título,
    explicação e link oficial;
  - tem um link para a página de Oportunidades, que diz quantas há no total;
  - não existe quando não há oportunidade a exibir.

  O reconhecimento continua sendo o primeiro conteúdo do Início, e o 024 SC-004 continua
  valendo. O convite à pesquisa continua único, com texto e ação inalterados (024 FR-020).
  A 375×812, com fonte a 100%, ele não desce mais que 270 px em relação à mesma persona sem
  o bloco. [Hipótese; seção "Início e acesso à pesquisa"; revisa 024 FR-016 e FR-021]
- **FR-022**: Na camada do Portal, a palavra "pesquisa" sozinha DEVE continuar designando só
  a pesquisa de acompanhamento, e o convite continua sendo a única chamada para ela (024
  FR-020). A categoria "Pesquisa e extensão" é o único outro uso admitido.

  As áreas de Oportunidades NÃO DEVEM conter:
  - urgência ("últimas vagas", "não perca", contagem regressiva);
  - indicador social ("x egressos viram");
  - "recomendado", "selecionado para você por…";
  - estimativa de tempo;
  - progresso de perfil.

  Os vetos acima valem para os **textos do sistema**: títulos de área, explicação, linha de
  origem, estados e avisos. Título e resumo são conteúdo da unidade responsável e não são
  bloqueados por vocabulário. O formulário de curadoria orienta: "Evite urgência e promessas,
  como 'últimas vagas' ou 'não perca'. Os prazos ficam na página oficial." *(Esclarecido em
  2026-10-08, depois do `/speckit-analyze`.)* [Hipótese; Const. X — o software não redefine a
  responsabilidade editorial da unidade]

  [024 FR-020, FR-021; auditoria de 2026-10-02 §5]
- **FR-023**: A página e o bloco DEVEM:
  - atender a WCAG 2.1 AA e ao eMAG: lista semântica, hierarquia de títulos, foco visível,
    nenhuma informação só por cor, link externo indicado em texto;
  - funcionar sem JavaScript;
  - caber de 320 px em diante sem rolagem horizontal, com fonte de 100% a 200%;
  - ter alvos de pelo menos 44×44 px CSS;
  - reaproveitar os tokens e componentes da 015 e da 024, sem tokens novos, sem grade de
    cartões e sem imagens (024 FR-026).

  [Const. XX, XXI; 015; 024]
- **FR-024**: A Pessoa identificada sem Conclusão Acadêmica que pedir a página de
  Oportunidades DEVE ser levada ao Início, sem mensagem que revele oportunidades. [Arquitetura]

#### Curadoria e governança

- **FR-025**: DEVE existir a competência nomeada **curar oportunidades**, numa regra única,
  com estas atribuições:
  - **CSAEG ativa**: nas unidades dos próprios vínculos. [PAEG Art. 13, parágrafo único;
    Art. 22, III]
  - **CPAEG ativa**: com escopo institucional. [Hipótese; DP-2501]

  Nenhum outro papel nem perfil técnico DEVE recebê-la. [Const. X; Governança de Permissões;
  010 FR-034]
- **FR-026**: **Administração e público são dimensões independentes** (seção "Quem administra
  × para quem se destina").
  - **Administração.** A CSAEG DEVE ver, cadastrar, editar, publicar e retirar só
    oportunidades cuja unidade responsável esteja entre as suas unidades. A CPAEG administra
    qualquer uma e é a única que usa "Ifes (institucional)". [Const. XII; Solicitante S3]
  - **Público.** Quem administra a oportunidade define o público. A unidade responsável NÃO
    DEVE restringir o público, nem o público ampliar a administração. Como hipótese da
    demonstração, a CSAEG pode dirigir a oportunidade a qualquer combinação de unidades,
    níveis e cursos, ou a todos os egressos. [Hipótese; DP-2502]
  - **Sem acesso a dado de egresso.** A curadoria NÃO DEVE mostrar quais nem quantos egressos
    casam com o público. [Const. XVI]
- **FR-027**: A curadoria DEVE listar as oportunidades do escopo do operador. Cada linha
  mostra título, unidade responsável, categoria, período e estado (FR-009), com as ações
  disponíveis para aquele estado. A lista tem estado vazio próprio. [Arquitetura; padrão
  017]
- **FR-028**: Cadastrar DEVE criar a oportunidade em Rascunho, depois de validar os FR-002 a
  FR-007 e o escopo (FR-026). Os erros aparecem junto dos campos, com vocabulário fechado de
  mensagens. Nada é gravado em caso de erro. [Arquitetura; padrão 017]
- **FR-029**: Editar DEVE ser possível em Rascunho, Agendada e Em divulgação, com as mesmas
  validações.
  - A mudança vale para o egresso na próxima consulta.
  - Editar uma oportunidade publicada não a devolve a Rascunho.
  - Numa oportunidade publicada, o fim NÃO DEVE ficar antes de hoje: encerrar antes do prazo
    é retirar (FR-031).
  - Encerrada e Retirada NÃO DEVEM ser editáveis.

  [Arquitetura]
- **FR-030**: Publicar DEVE partir de um Rascunho e exigir confirmação explícita numa tela com:
  - a prévia do item como o egresso o verá;
  - o público em linguagem simples ("todos os egressos do Ifes" ou "quem concluiu…");
  - o período.

  A tela DEVE mostrar também o domínio completo do endereço, com aviso quando for site
  externo (FR-004). A publicação DEVE ser rejeitada se o fim já passou.

  Publicar é o único ato que autoriza a divulgação: nenhuma oportunidade aparece só porque
  chegou a data de início. NÃO DEVE haver aprovação por segunda pessoa nem fluxo editorial.
  [Const. X; Solicitante S4]
- **FR-031**: Retirar DEVE ser possível em Rascunho (descarte), Agendada e Em divulgação, com
  confirmação explícita.
  - A retirada é definitiva.
  - A oportunidade sai da vista do egresso imediatamente.
  - Uma oportunidade retirada não pode ser publicada.
  - Para divulgar de novo, cadastra-se outra.

  [Arquitetura]
- **FR-032**: A expiração DEVE acontecer sem ação humana nem processo agendado. A partir do
  dia seguinte ao fim, a oportunidade é Encerrada (FR-009). [Arquitetura; roadmap S2]
- **FR-033**: Publicar e retirar DEVEM registrar o momento e o identificador opaco do
  operador. NÃO DEVE haver histórico de edições nem registro de autoria do cadastro. [Const.
  IV, proporcionalidade; precedente 019/020; DP-2506]
- **FR-034**: Se o estado da oportunidade mudou entre a exibição e a confirmação (por exemplo,
  retirada por outro operador), a ação DEVE ser recusada com página de conflito, sem gravar
  nada. [Padrão 017 FR-021]
- **FR-035**: As telas de curadoria DEVEM:
  - seguir o padrão das telas de operação existentes (formulário acessível, confirmação,
    conflito, avisos);
  - usar a identificação de operador fictício da demonstração (DP-1001);
  - não usar o Django admin, editor rico nem upload;
  - atender a WCAG 2.1 AA.

  [Const. XX; 010; 017]

#### Fronteiras

- **FR-036**: A Oportunidade e sua curadoria DEVEM pertencer à camada de relacionamento
  (seção "Modularização"). Nenhum componente do núcleo DEVE importar, ler ou citar a camada,
  e isso DEVE ser verificado por teste de fronteira. [Const. 2.1.0; ADR 0008]
- **FR-037**: A feature NÃO DEVE criar nem alterar Pessoa, Conclusão Acadêmica, Formação
  Declarada, Campanha, Versão, Participação, Resposta, contato ou vínculo de governança. As
  telas do egresso continuam sem gravar nada (024 SC-006). A única escrita nova é a curadoria
  da Oportunidade. [Const. 2.1.0; I, VII]
- **FR-038**: Oportunidades NÃO DEVEM entrar em snapshot, exportação, indicador nem tela de
  acompanhamento da coleta. [Const. 2.1.0; ADR 0008]
- **FR-039**: Com a camada desligada (024 FR-027), a página de Oportunidades, o bloco do
  Início, o item de navegação e a curadoria DEVEM ficar indisponíveis ("não encontrado"). Os
  dados ficam preservados, e o núcleo e a coleta funcionam como na 024. [Const. 2.1.0; ADR
  0008]
- **FR-040**: Como da 018 à 024, a feature inteira DEVE ficar restrita ao modo de
  demonstração. [Const. 2.1.0; XXIX]
- **FR-041**: Funcionar não DEVE exigir dado pessoal novo: a feature não pede, não guarda e
  não infere nada sobre o egresso. [Const. XVI; Solicitante]

#### Demonstração

- **FR-042**: A preparação da demonstração DEVE carregar um catálogo fictício que cubra:
  - uma oportunidade aberta a todos;
  - oportunidades por curso (Redes de Computadores; Análise e Desenvolvimento de Sistemas),
    por nível (Pós-graduação) e por unidade (Vitória);
  - uma com dois critérios, que nenhuma persona satisfaça combinando formações diferentes;
  - uma de unidade (Vitória) aberta a egressos de outras unidades;
  - uma Agendada, uma Encerrada, uma Retirada e um Rascunho com período em curso;
  - ao menos uma persona sem oportunidade dirigida (por exemplo, Fernanda, de Cariacica; Elisa
    não entra pela demonstração, porque não tem CPF).

  Os endereços DEVEM usar domínio reservado para exemplos, para nunca levar à página real de
  terceiros como se fosse oficial. A classificação site do Ifes × site externo é exercitada
  nos testes, não no catálogo. [Arquitetura; Const. XXIX]

#### Verificação automatizada

- **FR-043**: DEVE haver testes para cada um destes casos:
  1. a regra do FR-012 (sem público; cada critério; combinação; várias formações; valor
     ausente; igualdade exata; duas grafias; critérios **não** combinados entre Conclusões
     diferentes);
  2. as explicações (FR-013) para cada caso;
  3. a ordem e o determinismo (FR-014, FR-016);
  4. os estados derivados e as seis regras de publicação: Rascunho com período em curso
     invisível, início e fim inclusivos em D e D+1 com data de referência controlada,
     retirada definitiva e fim de oportunidade publicada nunca antes de hoje (FR-009,
     FR-029 a FR-032);
  5. a administração da CSAEG e da CPAEG em cada ação, e a independência entre administração
     e público, inclusive uma CSAEG dirigindo a outras unidades (FR-025, FR-026);
  6. as validações, inclusive cada forma de endereço recusada e a classificação site do
     Ifes × site externo, e o conflito (FR-004, FR-028 a FR-031, FR-034);
  7. nenhuma gravação ao exibir, e o link direto (FR-015);
  8. a Pessoa sem Conclusão, o declarante e a sessão expirada;
  9. a camada desligada (FR-039);
  10. a fronteira e a exclusão do analítico (FR-036 a FR-038);
  11. o estado vazio e o bloco ausente do Início (FR-018, FR-021);
  12. o bloco do Início com uma oportunidade só, antes do convite único e inalterado, e o
      item "Pesquisa" presente na navegação de toda página do Portal (FR-020, FR-021).

  [Const. XXVI]

### Requisitos revisados

A rastreabilidade fica aqui e, na implementação, numa nota de revisão na spec da 024.

| Requisito | Antes | Depois (025) |
|---|---|---|
| **024 FR-016** | Início: reconhecimento → proveniência → ações → convite | Reconhecimento → proveniência → ações → **Oportunidades** (uma em destaque, quando houver) → convite (FR-021) |
| **024 FR-021** | O Início NÃO DEVE conter Oportunidades | O Início PODE conter o bloco de Oportunidades do FR-021. Os demais vetos continuam: Volte ao Ifes, comunidade, interesses, indicador social, estimativa de tempo, área sem função |
| **024 FR-022** | Telas com navegação: Início, escolha de formações, confirmação, Minha trajetória, Meu e-mail | Mais a página de Oportunidades (FR-020) |
| **024 FR-023** | Navegação: Início, Minha trajetória, Pesquisa, Meu e-mail | Início, Minha trajetória, **Oportunidades**, Pesquisa, Meu e-mail (FR-020) |
| **024 FR-029** | A camada do Portal NÃO DEVE gravar nada; sem entidade nem migração | As telas do egresso continuam sem gravar nada. A camada ganha uma entidade, Oportunidade, gravada só pela curadoria (FR-037), com migração aditiva |
| **024 contrato do Início** | "Oportunidade" no vocabulário vetado | Vetado só fora do bloco do FR-021 |

**Não são revisados:**

- 024 FR-001 a FR-015 (entradas, caminho do convite, trajetória antes da pesquisa);
- 024 FR-020 (convite único);
- 024 FR-027 (desligamento), que passa a cobrir também a 025;
- 016 e 018 (convite neutro), 004 e ADR 0004 (abrangência);
- o instrumento 2024.

### Key Entities *(include if feature involves data)*

- **Oportunidade** (nova; camada de relacionamento). Conteúdo institucional curado que aponta
  para uma página oficial. Atributos: título, resumo, categoria, unidade responsável,
  endereço oficial, início e fim da divulgação, público opcional (unidades, níveis, cursos),
  momento e operador da publicação, momento e operador da retirada. Não tem relação com
  Pessoa, Conclusão, Campanha nem Participação. A ligação com a Pessoa só existe **na
  consulta**, pela regra do FR-012.
- **Pessoa** e **Conclusão Acadêmica** (existentes; só leitura). Base da pertinência e da
  explicação.
- **Vínculo de governança** (existente; só leitura). Base da competência e do escopo.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado | Origem | Fonte ou regra de derivação | Tratamento de divergência |
|---|---|---|---|
| Curso, unidade, nível e ano da formação | Institucional | Conclusão Acadêmica (001) | Comparado e exibido como na fonte (004 FR-022; 001/DP-004) |
| Oportunidade (título, resumo, categoria, endereço, unidade, período, público) | Institucional, curado | Operador com a competência do FR-025 | Corrigida por edição ou retirada. Não há divergência com o núcleo, porque não é dado sobre a Pessoa |
| Pertinência e explicação | Derivado | Regra do FR-012, na consulta, sem persistir | Recalculada a cada consulta |
| Estado da oportunidade | Derivado | FR-009, a partir dos momentos e das datas | — |

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Verificáveis automaticamente ou por medição** (gate da feature):

- **SC-001**: Os doze casos do FR-043 passam. Os testes das features anteriores continuam
  passando, exceto os que verificam requisitos revisados, que são atualizados com
  rastreabilidade.
- **SC-002**: Para cada persona da demonstração, a lista de Oportunidades coincide em 100% com
  a tabela de resultados esperados escrita **antes** da implementação (oráculo por persona),
  na ordem e na explicação.
- **SC-003**: Do Início, o egresso chega à página de Oportunidades com **um** toque e a uma
  página oficial com **um** toque, quando o bloco existe, ou com **dois**, pela página.
- **SC-004**: Zero gravações causadas pela exibição. As contagens de todas as tabelas ficam
  iguais antes e depois de abrir o Início e a página de Oportunidades, e o link leva direto
  ao domínio oficial.
- **SC-005**: Uma oportunidade com fim em D aparece em D e não aparece em D+1, sem nenhuma
  ação, em 100% dos casos de teste.
- **SC-006**: 100% das tentativas de um operador CSAEG de administrar oportunidade de outra
  unidade, ou institucional, são recusadas nas cinco ações (ver, cadastrar, editar, publicar,
  retirar), sem gravar nada. A escolha do público não altera esse resultado.
- **SC-007**: Um operador cadastra e publica uma oportunidade passando por no máximo quatro
  telas (lista → formulário → confirmação de publicação → lista), preenchendo só os campos
  do FR-001.
- **SC-008**: A 375×812 px, com fonte a 100%, e com o bloco de Oportunidades e a navegação
  de cinco itens presentes:
  - o `h1` e a síntese do reconhecimento do Início continuam visíveis sem rolar;
  - o convite à pesquisa desce no máximo 270 px em relação à mesma persona sem o bloco.

  De 320 a 1280 px, com fonte de 100% a 200%:
  - nenhuma página nova nem a navegação tem rolagem horizontal;
  - os cinco itens mantêm alvo de 44×44 px.
- **SC-009**: Snapshot e exportações gerados com e sem oportunidades publicadas são
  idênticos.
- **SC-010**: Com a camada desligada, as telas da 025 respondem "não encontrado". Com ela
  ligada ou desligada, o caminho do convite tem as mesmas telas, toques e rolagem da
  reauditoria de 2026-10-06 (cenário A; 024 SC-002).

**Checkpoint 2 — teste moderado, parte de Oportunidades** (roadmap §7; definidos antes do
teste). O número de participantes e o limiar de "maioria" ficam no protocolo do Checkpoint 2,
escrito antes da aplicação. Taxa de clique, engajamento e conversão **não** são critério.

*Compreensão.* A maioria dos participantes:

- **SC-011**: explica, com as próprias palavras, por que uma oportunidade aparece para ela, e
  a explicação a convence;
- **SC-012**: distingue oportunidade institucional de anúncio;
- **SC-013**: entende que o link leva ao site oficial, onde estão prazos e inscrição;
- **SC-014**: não confunde Oportunidades, nem "Pesquisa e extensão", com a pesquisa de
  acompanhamento.

*Comportamento.* A maioria dos participantes:

- **SC-015**: encontra, sem ajuda, uma oportunidade pertinente à própria formação;
- **SC-016**: diante do estado vazio, não interpreta a área como quebrada nem como pendência
  sua.

## Assumptions

- **Dados da demonstração.** As personas do `preparar_demonstracao` cobrem os casos de
  pertinência sem mudar o núcleo. Carla (Redes, Serra) e Maria (ADS e Pós) servem para curso
  e nível; Bruno, para unidade; Fernanda, para estado vazio dirigido.
- **Endereços e textos.** O endereço da página de Oportunidades, o da curadoria e os textos
  finais (explicações, estado vazio, rótulos) ficam no plan, sujeitos à regra de verdade e a
  captura de tela, como na 021, 023 e 024.
- **Limites de tamanho.** 120 e 300 caracteres são hipóteses de leitura em tela de 320 px. O
  plan pode ajustá-los com evidência de captura.
- **Volume.** Na demonstração, poucas dezenas de oportunidades. Paginação, busca e filtro
  ficam fora até haver volume real.
- **Data de referência.** "Hoje" é a data local do projeto, a mesma da Campanha.
- **Mockup.** Referência conceitual de tom. O que ele contradiz está listado em "O que é
  reutilizado" e não é adotado.

## Dependências

| Dependência | Tipo | Situação |
|---|---|---|
| 024 — Início, shell e navegação do Portal | Código | Integrada à `main` |
| **Checkpoint 1 da 024** | Validação | **Não aplicado.** A implementação da 025 só começa depois da leitura dos resultados, conforme o [protocolo](../024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md). Se um critério de compreensão falhar, a S1 é corrigida antes, e esta spec é revista se a correção mudar o Início ou a navegação |
| 010 — governança, papéis e escopos | Código | Existente |
| 017 — padrão de telas de gestão | Código | Existente |
| 001 — Conclusão Acadêmica e fonte simulada | Código | Existente |
| D4 / DP-2501 e DP-2502 — quem cura e com que alcance | Decisão institucional | Pendente. Bloqueia só o uso real |
| DP-2507 — identificador estável de curso na fonte real | Decisão institucional (Portão A) | Pendente. Sem ela, vale a comparação exata do texto |
| D5 / DP-2503 — finalidade de usar o contexto acadêmico | Decisão institucional | Pendente. Bloqueia só o uso real |
| Protocolo do Checkpoint 2 | Validação | A escrever depois da 025 e da 026, antes do teste |

## Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| **Portal vazio ou desatualizado** (operacional, o maior) | O egresso volta e não encontra nada, ou encontra coisa vencida | Expiração automática (FR-032); o Início esconde o bloco vazio (FR-021); estado vazio honesto (FR-018). Para uso real: ter quem cure (DP-2501) e, antes de adotar, avaliar com ao menos uma unidade se ela consegue manter a alimentação. Essa avaliação é operacional e fica fora desta feature |
| Virar CMS ou mural de anúncios | Custo de manutenção, perda de confiança | Atributos fechados (FR-001), texto curto e simples (FR-002), link oficial obrigatório (FR-004), sem imagem, sem destaque, sem urgência (FR-022) |
| Pertinência pobre sem área do conhecimento | Oportunidade "de tecnologia" exige listar cursos um a um | Valores escolhidos entre os registrados (FR-007). Uma classificação por área seria decisão institucional futura, não desta feature |
| Grafia instável de unidade e curso na fonte | O público deixa de casar em silêncio. A fonte simulada não tem o caso (uma grafia por curso); a fonte real pode ter | Igualdade exata, documentada (FR-012). A curadoria lista os valores atuais, e o operador marca todas as grafias. DP-1005 e 001/DP-007 herdadas; código de curso estável é DP-2507. Os testes exercitam o caso (FR-043, item 1) |
| Link oficial malicioso ou quebrado | Phishing ou frustração | Validação mínima da forma do endereço (sem usuário, sem IP, só `https`), classificação site do Ifes × externo, domínio à vista do egresso e do operador (FR-004), registro de quem publicou (FR-033), retirada imediata (FR-031). Lista de domínios ou autorização de parceiros: DP-2504 |
| "Pesquisa e extensão" confundida com a pesquisa de acompanhamento | O egresso acha que precisa responder algo | Vocabulário do FR-022; observado no Checkpoint 2 (SC-014) |
| Navegação com cinco itens a 320 px e fonte a 200% | Rolagem horizontal ou quebra ruim. A 375 px, os quatro itens atuais já ocupam a linha inteira | Quebra em linhas sem rolagem, alvos de 44×44 px e síntese do Início acima da dobra (FR-020, SC-008), com medição na validação |
| O Início afastar a pesquisa | Quem chega pelo Portal demora a achar a pesquisa | Uma oportunidade só no Início, convite único e inalterado e no máximo 270 px mais abaixo, item "Pesquisa" no topo de toda página (FR-020, FR-021, SC-008). O caminho do convite não passa pelo Início (SC-010) |
| Construir antes da hora | Tabela e telas sem a premissa do Checkpoint 1 validada | Só a spec foi antecipada; a implementação aguarda o Checkpoint 1 (Decisão S1) |

## Invariantes Constitucionais Afetados *(mandatory)*

- **I, VII, VIII — Longitudinalidade e preservação.** Nada do núcleo é criado nem alterado
  (FR-037). Oportunidade não se liga a Participação nem a Campanha.
- **II — Definição de egresso.** Só quem tem Conclusão Acadêmica vê Oportunidades (FR-011).
  "Todos os egressos" não inclui Pessoa sem Conclusão nem declarante.
- **III, IV — Institucional × declarado e proveniência.** A pertinência usa só fatos
  institucionais (FR-011, FR-012), e a explicação os cita (FR-013). Formação Declarada fica
  fora.
- **VI e Fronteira (Camada de relacionamento, 2.1.0).** O fato vive na camada (FR-036), não
  entra no analítico (FR-038), e a coleta independe dele (FR-039).
- **X e Governança de Permissões.** A competência é nomeada (FR-025), a administração é por
  unidade, o público não amplia a administração nem dá acesso a dado (FR-026), não há aprovação inventada (FR-030), e a atuação institucional é hipótese
  registrada (DP-2501).
- **XII — Base central, escopos por unidade.** Uma única tabela, com o escopo aplicado na
  autorização (FR-026).
- **XIV — Menos fricção.** Nada a preencher. A oportunidade fica a um ou dois toques do
  Início (SC-003).
- **XVI — Privacidade.** Nenhum dado pessoal novo (FR-041), nenhuma gravação ao exibir nem
  rastreamento de clique (FR-015), nenhum parâmetro na URL.
- **XX, XXI — Acessibilidade e mobile.** FR-023 e SC-008.
- **XXII — YAGNI.** Sem catálogo de áreas, sem filtro, sem paginação, sem histórico, sem
  exclusão, sem app novo.
- **XXVII — Migrações.** Uma tabela nova, com migração aditiva. Nenhuma tabela existente muda.
- **XXIX — Hipóteses.** São hipóteses reversíveis, testadas no Checkpoint 2:
  - categorias, ordem e limites de tamanho;
  - atuação da CPAEG;
  - público livre para a CSAEG;
  - classificação de domínio;
  - destaque único no Início;
  - a própria área.

  O que depende de instância competente está em DP-2501 a DP-2507.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence de fato ao domínio de acompanhamento?** Não. "Oportunidades profissionais" está
   entre as capacidades que o Princípio VI manda manter externas quando houver solução
   institucional. Aqui ela pertence à camada de relacionamento, admitida só na demonstração
   (Constituição 2.1.0; ADR 0008).
2. **É necessária ao ciclo de acompanhamento?** Não. É hipótese de produto: valor antes da
   coleta. O ciclo funciona sem ela (FR-039).
3. **Existe ou está prevista solução institucional mais adequada?** A PAEG prevê a divulgação
   de oportunidades no Portal do Egresso, definida por cada unidade (Art. 13). Esse Portal
   ainda não existe, e os sites dos campi publicam editais sem curadoria por egresso. A
   relação com eles é D1 (produção). A 025 **aponta** para o conteúdo oficial e não o hospeda,
   o que facilita a substituição.
4. **Integração seria suficiente?** Hoje não há fonte institucional estruturada de
   oportunidades para integrar. Se surgir, a Oportunidade curada pode ser substituída ou
   alimentada por ela sem mudar o núcleo.
5. **A incorporação aumentaria desnecessariamente o acoplamento do núcleo?** Não. O núcleo
   não conhece a Oportunidade (FR-036). A camada só lê Conclusões e vínculos.

## Out of Scope *(mandatory)*

- Inscrição, vagas, candidatura, agenda, confirmação de presença, local e data de evento.
- CMS: corpo longo, formatação, anexos, páginas de detalhe, imagens, destaques, ordem manual.
- Workflow editorial: revisão, aprovação por segunda pessoa, versões, agendamento além do
  início da divulgação.
- Recomendação, ranking, IA, aprendizado com cliques, "talvez você goste".
- Cadastro de interesses, perfil profissional, área de atuação declarada.
- Classificação de cursos por área do conhecimento ou eixo tecnológico.
- Público por modalidade, forma de oferta, ano ou coorte.
- Uso de Resposta, Formação Declarada ou contato na pertinência.
- Notificação por e-mail ou outro canal, newsletter, aviso de novas oportunidades.
- Contagem de visualizações ou cliques, métricas de engajamento, relatórios.
- Filtro, busca e paginação na página do egresso.
- Exclusão de oportunidade; histórico de edições.
- Integração com sistemas de oferta, editais ou sites dos campi.
- Volte ao Ifes, Manifestação de interesse (026), comunidade.
- Uso fora do modo de demonstração.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

### Herdadas e preservadas

- **D1 (produção) / DP-2108.** Relação com o Portal do Egresso da PAEG (Proex, CPAEG, DTI).
  Tratamento: camada só na demonstração.
- **D2 (definitivo).** Nome institucional da experiência (ACS, com Proex). Tratamento: "Portal
  do Egresso" provisório.
- **DP-1001.** Identificação real de operadores (DTI, com Proex). Tratamento: operadores
  fictícios.
- **DP-1005.** Lista canônica e grafia das unidades. Tratamento: texto da fonte, por
  igualdade exata.
- **001/DP-007.** Vocabulário de nível, modalidade e forma de oferta. Tratamento: o mesmo.
- **DP-1006.** Atuação de Proex, DIREC, Diretorias de Pesquisa, Pós-Graduação e Extensão.
  Tratamento: não representadas. Elas não curam nesta feature, mesmo que a PAEG lhes dê
  papel na interação com egressos (Art. 15, Art. 18).

### Novas

- **DP-2501** — DECISÃO PENDENTE (= D4, parte de curadoria): quem cura oportunidades em cada
  unidade e quem tem atuação institucional.
  - Instância competente: CPAEG, com Proex.
  - Impacto: FR-025.
  - Tratamento provisório:
    - CSAEG nas próprias unidades, com fundamento na PAEG Art. 22, III;
    - CPAEG com escopo institucional, como hipótese só da demonstração, sem artigo da PAEG
      que a atribua.
- **DP-2502** — DECISÃO PENDENTE: se o alcance de uma oportunidade cadastrada por uma
  unidade deve ter limite institucional. Exemplos: só os próprios egressos; outras unidades
  só com anuência; todos os egressos só pela CPAEG.
  - Instância competente: CPAEG, com Proex.
  - Impacto: FR-026, no público.
  - Tratamento provisório:
    - administração e público são independentes;
    - a unidade administra só o que é dela e dirige a oportunidade a qualquer público, como
      hipótese da demonstração;
    - o público não dá acesso a dado de egresso;
    - um limite futuro entra como validação do público, sem mudar o modelo.
- **DP-2503** — DECISÃO PENDENTE (= D5, parte de Oportunidades): se usar o contexto acadêmico
  registrado para escolher o conteúdo exibido ao egresso é compatível com a finalidade e a
  base legal do tratamento.
  - Instância competente: encarregado de dados, com a CPAEG.
  - Impacto: FR-011 a FR-013.
  - Tratamento provisório: só na demonstração. Calculado na consulta, sem gravar nada e sem
    dado novo.
- **DP-2504** — DECISÃO PENDENTE: que endereços contam como "oficiais" (só domínios do Ifes?
  também gov.br e parceiros?).
  - Instância competente: CPAEG, com DTI e ACS.
  - Impacto: FR-004.
  - Tratamento provisório:
    - validação mínima da forma do endereço;
    - classificação site do Ifes × site externo, só para exibição;
    - domínio sempre à vista do egresso e do operador;
    - parceiros aceitos como site externo;
    - quem publicou fica registrado;
    - sem lista de domínios nem autorização extra.
- **DP-2505** — DECISÃO PENDENTE: lista definitiva e redação das categorias.
  - Instância competente: CPAEG, com ACS.
  - Impacto: FR-003.
  - Tratamento provisório: as seis categorias do FR-003, como hipótese. "Formação
    continuada" e "cursos e especializações" foram unidas para evitar ambiguidade na hora
    de classificar.
- **DP-2506** — DECISÃO PENDENTE: retenção de oportunidades encerradas e retiradas, e se a
  curadoria precisa de histórico de edições.
  - Instância competente: CPAEG, com o encarregado de dados.
  - Impacto: FR-010, FR-033.
  - Tratamento provisório: nada é excluído. Registram-se só publicação e retirada, com
    operador e momento.
- **DP-2507** — DECISÃO PENDENTE: se a fonte acadêmica real fornece um identificador estável
  de curso (código de curso, matriz ou oferta) que possa substituir o texto do curso no
  público.
  - Instância competente: quem administra a fonte acadêmica (DTI, com Proen), no Portão A.
  - Impacto: FR-007 e FR-012, no critério de curso.
  - Tratamento provisório:
    - comparação exata do texto registrado, com as grafias visíveis ao operador;
    - sem correspondência aproximada nem catálogo paralelo;
    - adotar um código exigiria evoluir o contrato da fonte (001) em spec própria.
