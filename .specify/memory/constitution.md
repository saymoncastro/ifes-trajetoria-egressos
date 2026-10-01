# Constituição do Trajetória Ifes

**Núcleo Institucional de Acompanhamento de Egressos — NIAE**

## Convenções Normativas

Esta Constituição usa os seguintes termos normativos:

- **DEVE** / **É OBRIGATÓRIO**: requisito absoluto (equivalente a *MUST*).
- **NÃO DEVE** / **É VEDADO**: proibição absoluta (equivalente a *MUST NOT*).
- **DEVERIA** / **PREFERIR**: recomendação forte; desvio exige justificativa registrada
  na spec ou no plan (equivalente a *SHOULD*).
- **PODE**: faculdade, sem obrigação (equivalente a *MAY*).

Princípios marcados **NON-NEGOTIABLE** não admitem exceção justificada em spec, plan ou
tasks. Conflito com eles só é resolvido corrigindo a feature ou emendando formalmente
esta Constituição. Os demais princípios admitem desvio somente quando justificado e
registrado explicitamente (por exemplo, em *Complexity Tracking* do plan) e aceito em
revisão.

O marcador **`DECISÃO PENDENTE`** identifica, em qualquer artefato, uma regra
institucional ainda não definida pela instância competente. Ele NÃO DEVE ser removido
por suposição do desenvolvimento.

## Posicionamento do Projeto

O **Trajetória Ifes** é o software que implementa o **NIAE — Núcleo Institucional de
Acompanhamento de Egressos**, domínio institucional especializado em:

- acompanhamento longitudinal de egressos;
- contextualização da trajetória acadêmica;
- aplicação de pesquisas de acompanhamento;
- versionamento dos instrumentos;
- campanhas de acompanhamento;
- registro das participações ao longo do tempo;
- acompanhamento operacional da coleta;
- estruturação dos dados coletados;
- exportação e interoperabilidade;
- disponibilização de dados necessários à produção de indicadores.

O Trajetória Ifes **NÃO É** sinônimo do Portal do Egresso. A PAEG prevê, como ação
mínima, a criação de um Portal do Egresso — ambiente virtual específico, integrado aos
sistemas do Ifes, para relacionamento com os egressos (Art. 10, I) — que permitirá o
acompanhamento e toda a interação prevista na política, além de funcionalidades como
cadastro, divulgação de oportunidades de estágio/emprego, continuidade dos estudos e
eventos, a serem definidas por cada unidade (Art. 13). Esse ambiente mais amplo não é
automaticamente escopo deste software.

A forma de relação entre o Trajetória Ifes e o Portal do Egresso previsto na PAEG
(componente de acompanhamento do Portal, sistema integrado a ele ou outra composição) é
`DECISÃO PENDENTE` e NÃO DEVE ser presumida pelo desenvolvimento.

O Trajetória Ifes DEVE ser arquitetado para:

1. operar como núcleo especializado de acompanhamento;
2. integrar-se futuramente a uma solução institucional mais ampla;
3. compor o Portal do Egresso previsto na PAEG, na forma que vier a ser institucionalmente
   definida;
4. fornecer ou consumir serviços institucionais sem absorver automaticamente seus
   respectivos domínios;
5. funcionar isoladamente para desenvolvimento, testes e administração técnica enquanto
   a solução institucional mais ampla não estiver disponível.

A expectativa de integração futura NÃO DEVE bloquear a evolução independente do núcleo.
A futura existência de um Portal do Egresso NÃO DEVE exigir reescrita do domínio central.

"NIAE" é designação funcional do núcleo tecnológico e de domínio. O software NÃO cria
nova unidade administrativa ou estrutura organizacional do Ifes.

## Referência Institucional

O sistema DEVE respeitar a **Política de Acompanhamento de Egressos do Ifes — PAEG**,
aprovada pela Resolução CS nº 177/2023, que tem como documentos norteadores a Lei nº
9.394/1996 e o PDI institucional (Art. 1º). São premissas institucionais desta
Constituição, com os artigos da PAEG que as fundamentam:

- **egresso** é "aquele que efetivamente concluiu os requisitos previstos no Projeto
  Pedagógico do Curso – PPC e na legislação vigente e que está apto a receber ou já
  recebeu o diploma e/ou certificado de conclusão" (Art. 3º);
- **unidades do Ifes** compreendem os campi, o campus avançado e o Cefor (Art. 2º,
  parágrafo único);
- a política visa acompanhar os egressos em sua vida profissional e acadêmica (Art. 6º,
  Art. 7º);
- a política prevê desenvolvimento e aplicação de **questionário eletrônico**, com
  **periodicidade a ser definida pela Proex e Proen e/ou órgão competente** (Art. 10, II);
  o software NÃO DEVE inventar periodicidade;
- a política prevê análise e sistematização dos dados coletados para geração de
  indicadores de empregabilidade, verticalização dos estudos, realização profissional,
  taxa de retenção no emprego e retorno para a educação continuada, entre outros
  (Art. 10, III);
- a política prevê banco de dados que auxilie no aprimoramento dos PPCs (Art. 8º, I) e
  banco de dados central atualizado pela CPAEG (Art. 21, V);
- a política prevê atividades, no último período do curso, de estímulo aos estudantes e
  de cadastro no Portal do Egresso para registro de dados e avaliação do curso por
  questionários (Art. 9º);
- a governança institucional envolve, entre outros:
  - **Proex** (coordenação geral, monitoramento e Relatório Anual de Acompanhamento de
    Egressos — Art. 2º, Art. 14) e **DIREC** (acompanhamento e interação com egressos —
    Art. 2º, Art. 15);
  - **CPAEG**, presidida pelo Pró-Reitor de Extensão (Art. 16), à qual compete, entre
    outras atribuições, elaborar o questionário de pesquisa em conjunto com as áreas de
    ensino, pesquisa e extensão (Art. 21, VI);
  - nas unidades, a **Diretoria de Pesquisa, Pós-Graduação e Extensão** ou equivalente
    (Art. 18) e a **CSAEG**, à qual compete, entre outras atribuições, gerir o Portal do
    Egresso na unidade, aplicar o questionário e reportar atualizações necessárias à
    CPAEG (Art. 13, parágrafo único; Art. 22, III e IV);
- casos omissos da PAEG são resolvidos pela CPAEG em conjunto com a Pró-reitoria
  competente (Art. 26), e a própria política prevê avaliação e possível revisão
  (Art. 25, Art. 28);
- existe necessidade de visão institucional consolidada e, simultaneamente, de atuação
  por unidade.

O software apoia essa governança e NÃO a redefine. As citações acima referem-se ao texto
da PAEG vigente na ratificação; alteração da PAEG DEVE ser incorporada explicitamente,
por emenda quando afetar esta Constituição.

O **Formulário Egresso do Ifes 2024** (instrumento em Google Formulários atualmente
utilizado) é a referência funcional inicial do instrumento (ver Princípio XIII).

## Terminologia Fundamental

Os conceitos abaixo DEVEM permanecer semanticamente distintos em specs, modelos,
interfaces, exportações e código.

### Pessoa

Representa conceitualmente um indivíduo único no domínio. Uma Pessoa pode possuir
nenhuma, uma ou várias Conclusões Acadêmicas no Ifes. Pessoa NÃO DEVE ser confundida
com curso, campus, conclusão, participação, pesquisa ou resposta.

Uma mesma Pessoa pode possuir múltiplos identificadores externos ou registros
provenientes de diferentes fontes. Mecanismos de resolução e reconciliação de identidade
serão definidos pelas specs correspondentes; a unicidade conceitual da Pessoa NÃO
pressupõe a existência prévia de um identificador institucional único e perfeito.

### Conclusão Acadêmica

Representa um fato acadêmico institucional: *"determinada Pessoa concluiu determinada
formação, em determinado contexto acadêmico e temporal."*

Pode conter, conforme disponibilidade e necessidade: curso; unidade/campus; nível;
modalidade; forma de oferta; data ou ano de conclusão; forma de ingresso;
identificadores institucionais; demais características acadêmicas pertinentes.

Campus, curso e demais características acadêmicas pertencem ao contexto da Conclusão
Acadêmica e NÃO DEVEM ser tratados como atributos permanentes da Pessoa.

### Pesquisa

Representa o instrumento lógico de coleta.

### Versão da Pesquisa

Representa uma configuração historicamente identificável de determinada Pesquisa.

### Campanha

Representa a aplicação de determinada Versão da Pesquisa a uma população, período ou
contexto específico. Pesquisa e Campanha NÃO são sinônimos.

### Participação em Pesquisa

Representa uma ocorrência concreta de acompanhamento de determinada Conclusão Acadêmica
em determinada Campanha. Uma mesma Conclusão Acadêmica pode possuir várias Participações
em diferentes momentos.

### Resposta

Representa informação declarada pelo participante em determinada Participação em
Pesquisa. As Respostas DEVEM permanecer associadas à Participação e à Versão do
instrumento efetivamente apresentada.

## Princípios Fundamentais

### I. Longitudinalidade é estrutural — NON-NEGOTIABLE

O modelo conceitual fundamental DEVE preservar a cadeia:

**Pessoa → Conclusão Acadêmica → Participação em Pesquisa → Respostas**

- Uma mesma Conclusão Acadêmica PODE ser acompanhada várias vezes.
- Uma nova Participação NÃO DEVE substituir participação anterior, sobrescrever
  respostas anteriores, alterar retrospectivamente o estado observado, nem transformar
  a resposta mais recente em "estado atual" único da Pessoa.
- Toda Participação DEVE possuir contexto temporal.
- Toda Participação relacionada a uma formação DEVE permitir identificar
  inequivocamente a Conclusão Acadêmica observada.
- Múltiplas formações da mesma Pessoa NÃO DEVEM ser artificialmente fundidas.

Exemplo válido: Pessoa A → Graduação concluída em 2024 → participações em 2025, 2027 e
2030; e simultaneamente Pessoa A → Especialização concluída em 2029 → participações em
2030 e 2033.

**Justificativa**: o Trajetória Ifes existe para permitir acompanhamento ao longo do
tempo. Alteração que elimine esse caráter longitudinal exige emenda formal.

### II. A definição institucional de egresso deve ser respeitada — NON-NEGOTIABLE

- O sistema NÃO DEVE redefinir tecnicamente quem é considerado egresso.
- Para funcionalidades próprias de acompanhamento de egressos, uma Conclusão Acadêmica
  elegível DEVE corresponder à definição institucional vigente de egresso (atualmente,
  PAEG, Art. 3º).
- O sistema PODE futuramente manter registros de estudantes ainda não egressos para
  atividades preparatórias, comunicação ou estímulo à participação; esses registros NÃO
  DEVEM ser tratados, explícita ou implicitamente, como egressos.
- Mudanças institucionais na definição de egresso DEVEM ser incorporadas explicitamente
  e NÃO DEVEM ser inferidas pelo desenvolvimento.

### III. Dado institucional não é resposta declarada — NON-NEGOTIABLE

O sistema DEVE distinguir explicitamente três categorias de dado:

**A. Dado institucional** — proveniente de fonte institucional identificada. Exemplos:
curso; campus; modalidade; forma de oferta; ingresso; data de conclusão; demais
registros acadêmicos.

**B. Dado derivado** — calculado a partir de informações disponíveis. Exemplos: idade
calculada; tempo desde a conclusão; enquadramento em coorte; anos desde determinada
formação.

**C. Dado declarado** — efetivamente fornecido pelo egresso. Exemplos: situação
profissional; remuneração; relação entre trabalho e formação; continuidade dos estudos;
percepção sobre impactos da formação; demais respostas do instrumento.

Regras:

- Dado institucional ou derivado NÃO DEVE jamais ser registrado como se tivesse sido
  declarado pelo participante.
- Quando relevante, a origem da informação DEVE permanecer identificável.
- Princípio de experiência: **"não perguntar ao egresso aquilo que a instituição já sabe
  com qualidade suficiente."** Esse princípio NÃO significa considerar as fontes
  institucionais infalíveis.
- Divergência entre dado institucional e informação declarada DEVE ser tratada
  explicitamente. NENHUMA das fontes DEVE ser sobrescrita silenciosamente.

### IV. Proveniência deve ser preservável

Quando necessário à interpretação ou auditoria, o sistema DEVE permitir determinar: de
onde veio o dado; se é institucional, derivado ou declarado; quando foi obtido; qual
provider o forneceu; em qual contexto foi utilizado.

O nível de proveniência DEVE ser proporcional à finalidade e ao risco. NÃO DEVEM ser
criadas trilhas excessivas sem necessidade comprovada.

### V. Integrações externas devem ser desacopladas do domínio — NON-NEGOTIABLE

O domínio central NÃO DEVE depender diretamente: das tabelas do Q-Acadêmico; do esquema
de banco de qualquer sistema externo; de uma API acadêmica particular; de um Portal do
Egresso específico; de um mecanismo específico de autenticação; de tecnologia
particular de terceiros.

- Integrações DEVEM ocorrer por fronteiras explícitas e substituíveis.
- Para dados acadêmicos, DEVE existir contrato conceitualmente equivalente a
  `AcademicDataProvider`. Inicialmente DEVE ser possível utilizar
  `MockAcademicDataProvider`; posteriormente PODEM existir `QAcademicoDataProvider` ou
  outros adaptadores correspondentes às fontes institucionais efetivamente adotadas.
  (Os nomes são conceituais; a nomenclatura concreta pertence ao plan.)
- Mocks e providers reais DEVEM obedecer ao mesmo contrato de aplicação.
- Peculiaridades de sistemas externos DEVEM permanecer nos adaptadores.
- Trocar a fonte acadêmica NÃO DEVE exigir redesenhar o núcleo longitudinal.
- O domínio NÃO DEVE ser deformado para reproduzir o esquema de um sistema legado.

### VI. Integração institucional por composição, não por expansão de escopo

Uma funcionalidade existente no ecossistema de egressos NÃO passa automaticamente a
pertencer ao Trajetória Ifes. Antes de incorporar funcionalidade fora do acompanhamento
longitudinal, a respectiva spec DEVE responder:

1. Essa funcionalidade pertence de fato ao domínio de acompanhamento?
2. Ela é necessária ao ciclo de acompanhamento?
3. Existe ou está prevista solução institucional mais adequada?
4. Integração seria suficiente?
5. A incorporação aumentaria desnecessariamente o acoplamento do núcleo?

DEVERIAM permanecer externos, quando houver solução institucional adequada:
autenticação institucional; gestão geral de identidade; comunicação massiva; notícias;
eventos; oportunidades profissionais; comunidade de ex-alunos; CRM; Business
Intelligence institucional; serviços acadêmicos gerais.

O Trajetória Ifes PODE integrar-se a essas capacidades. Integração NÃO transfere
automaticamente ao NIAE a responsabilidade pelo respectivo domínio.

### VII. Pesquisa, Versão, Campanha e Participação são conceitos diferentes — NON-NEGOTIABLE

Esses conceitos NÃO DEVEM ser fundidos para simplificar banco de dados ou interface.

- Pesquisa define o instrumento lógico.
- Versão representa uma configuração histórica específica.
- Campanha representa a aplicação de uma Versão a determinado público, contexto e
  período.
- Participação representa a ocorrência concreta de acompanhamento.
- Toda Resposta DEVE permanecer associada à Participação e à Versão efetivamente
  apresentada.

### VIII. Preservação histórica é obrigatória — NON-NEGOTIABLE

- O sistema DEVE preservar o significado histórico dos dados coletados.
- Uma Versão da Pesquisa utilizada em coleta NÃO DEVE ser modificada de forma que altere
  a interpretação das respostas existentes. Mudanças que alterem significado DEVEM
  resultar em nova Versão.
- DEVEM permanecer recuperáveis, quando necessários: texto da pergunta; opções
  apresentadas; escala; condicionais relevantes; versão; campanha; contexto acadêmico;
  momento da participação.
- Respostas anteriores NÃO DEVEM ser sobrescritas por respostas posteriores.

**Justificativa**: preservação histórica prevalece sobre conveniência de edição
retroativa.

### IX. Periodicidade é configurável, não estrutural — NON-NEGOTIABLE

A longitudinalidade é estrutural; a periodicidade específica não é.

- NÃO DEVE ser fixado como regra de domínio qualquer intervalo ou sequência (por exemplo
  1, 3, 5 ou 10 anos).
- Intervalos PODEM ser utilizados por determinada Campanha quando definidos pela
  governança institucional competente (atualmente, Proex e Proen e/ou órgão competente —
  PAEG, Art. 10, II).
- Critérios de elegibilidade e periodicidade pertencem às regras da Campanha.

**Justificativa**: o software fornece capacidade; a política institucional determina
como utilizá-la.

### X. A tecnologia não redefine a governança da PAEG — NON-NEGOTIABLE

O software DEVE apoiar a governança institucional, não substituí-la. Perfis, permissões
e fluxos DEVEM permitir representar adequadamente as competências existentes. Em
particular:

- periodicidade NÃO DEVE ser decidida pelo código;
- elaboração e alteração do instrumento DEVEM respeitar as competências institucionais
  (a PAEG atribui a elaboração do questionário à CPAEG, em conjunto com as áreas de
  ensino, pesquisa e extensão — Art. 21, VI — e sua aplicação às CSAEGs — Art. 22, IV);
- publicação de uma Versão NÃO DEVE decorrer apenas de permissão técnica; a PAEG não
  define quem aprova a publicação de uma Versão, o que permanece `DECISÃO PENDENTE`;
- atuação das unidades DEVE respeitar seus escopos;
- DEVE existir capacidade de visão institucional consolidada;
- nenhum perfil técnico ou administrativo DEVE receber competência normativa apenas por
  possuir acesso ao sistema.

Papéis concretos DEVEM ser definidos em specs futuras conforme regras institucionais
efetivamente confirmadas. NÃO DEVE ser inventado workflow de aprovação sem fundamento
institucional.

### XI. Identidade institucional é única; contexto acadêmico é múltiplo

- Uma Pessoa DEVE poder possuir várias Conclusões Acadêmicas, em cursos, níveis,
  unidades, modalidades e períodos diferentes.
- O sistema NÃO DEVE determinar que uma Pessoa "pertence" permanentemente a um campus.
- O contexto da unidade decorre da Conclusão Acadêmica observada.
- Isso NÃO DEVE exigir duplicação da Pessoa.
- Identidade única é conceito de domínio: registros e identificadores de fontes
  distintas PODEM coexistir e ser reconciliados conforme spec própria (ver Terminologia,
  Pessoa).

Exemplo: Pessoa X → Curso A (Campus Serra) e Curso B (Cefor). Uma participação referente
ao Curso A pertence analiticamente ao contexto do Campus Serra; uma referente ao Curso B,
ao contexto do Cefor.

### XII. Base institucional central; escopos por unidade

- O sistema DEVE favorecer uma visão institucional consolidada.
- NÃO DEVE ser criado banco independente por campus sem necessidade comprovada.
- Escopos administrativos PODEM ser delimitados por unidade.
- Base central NÃO significa acesso irrestrito: a autorização DEVE ser compatível com a
  governança e com o princípio de menor privilégio.

### XIII. O instrumento atual é referência inicial, não limite permanente

O formulário institucional atualmente utilizado é referência funcional inicial. A
primeira transformação DEVE priorizar: migração tecnológica; integração com dados
institucionais; redução de perguntas redundantes; redução de carga cognitiva; melhor
experiência; gestão estruturada da coleta.

Ela NÃO DEVE se transformar, silenciosamente, em revisão metodológica completa. Na
migração inicial:

- preservar, quando pertinente, o significado das perguntas;
- preservar condicionais relevantes;
- preservar comparabilidade quando razoável;
- retirar da jornada aquilo que puder ser obtido institucionalmente.

Encontrar uma pergunta aparentemente inadequada NÃO autoriza alterá-la automaticamente.

Preservar o instrumento existente significa preservar seu significado metodológico e
suas regras intencionais, e NÃO necessariamente limitações técnicas, erros de interface,
inconsistências ou comportamentos acidentais da implementação atual (por exemplo, da
ferramenta Google Formulários). Correções desse tipo DEVEM ser explicitamente
identificadas e documentadas pela spec correspondente, distinguindo intenção do
instrumento de limitação ou acidente da implementação.

Toda spec DEVE distinguir, quando aplicável, a origem de cada requisito:

- requisito herdado do instrumento atual;
- requisito decorrente da PAEG;
- decisão arquitetural;
- hipótese de produto;
- oportunidade metodológica futura.

Revisões metodológicas PODEM ocorrer posteriormente, de forma explícita, aprovada e
versionada.

### XIV. A experiência do egresso deve reduzir fricção

A jornada pública DEVE exigir apenas o esforço necessário, minimizando: quantidade de
telas; quantidade de campos; repetição; digitação; listas extensas; necessidade de
lembrar informações acadêmicas; necessidade de conhecer a estrutura administrativa do
Ifes.

Sempre que possível, DEVE-SE contextualizar em vez de perguntar. PREFERIR *"Esta
pesquisa refere-se ao curso X, Campus Y, concluído em Z."* a solicitar novamente campus,
curso, modalidade ou ano de conclusão.

Essa simplificação NÃO DEVE comprometer a associação correta entre Pessoa, Conclusão
Acadêmica, Campanha e Participação.

### XV. Identidade e autenticação devem ser substituíveis

- O domínio NÃO DEVE depender permanentemente de mecanismo específico de autenticação
  (usuário e senha, OTP, Gov.br, login institucional, link mágico ou outro).
- A solução de autenticação DEVE ser proporcional ao risco.
- Solução institucional de identidade futura DEVE poder substituir o mecanismo inicial
  sem reescrita do domínio.
- NÃO DEVE ser criado cadastro tradicional com senha apenas por convenção técnica.

### XVI. Privacidade, segurança e minimização de dados — NON-NEGOTIABLE

O sistema manipula dados pessoais e respostas potencialmente sensíveis. DEVEM ser
aplicados desde o desenho: minimização de dados; finalidade conhecida; menor privilégio;
autorização explícita; separação de responsabilidades; proteção contra acesso indevido;
proteção de tokens e credenciais; ausência de segredos no repositório; cuidado com dados
pessoais em logs; proteção de exportações; rastreabilidade proporcional ao risco.

- Dado NÃO DEVE ser coletado ou persistido apenas porque poderá ser útil no futuro.
- Base legal, consentimento, retenção, anonimização, pseudonimização, compartilhamento e
  publicação, enquanto não institucionalmente definidos, NÃO DEVEM ser inventados pelo
  desenvolvimento e DEVEM ser registrados como `DECISÃO PENDENTE`.

### XVII. Consentimento deve ser historicamente identificável quando aplicável

Quando determinada aplicação exigir apresentação e aceite de termo, o sistema DEVE ser
capaz de relacionar: versão do termo apresentada; momento da apresentação; Participação;
manifestação registrada.

Regras jurídicas não formalmente estabelecidas pela instituição NÃO DEVEM ser inferidas.

### XVIII. Exportabilidade e interoperabilidade são requisitos de domínio

Os dados pertencem ao processo institucional, não à interface da aplicação.

- O sistema DEVE permitir exportação estruturada.
- CSV é o formato mínimo obrigatório de interoperabilidade; XLSX PODE ser oferecido por
  conveniência operacional.
- Exportações DEVEM poder combinar, conforme finalidade e autorização: campanha; versão;
  conclusão acadêmica; campus/unidade; curso; nível; coorte; datas; respostas; contexto
  necessário à interpretação.
- A distinção entre dado institucional, derivado e declarado DEVE ser preservável nas
  exportações.
- A utilidade dos dados NÃO DEVE depender de ferramenta específica de BI.

### XIX. O sistema acompanha a coleta; não precisa ser um BI

O Trajetória Ifes DEVE fornecer informação suficiente para gestão operacional da coleta.
Indicadores operacionais PODEM incluir: população elegível; convidados; não iniciados;
iniciados; concluídos; taxa de resposta; distribuição por unidade, curso e coorte.

Análises estatísticas avançadas e BI institucional PODEM ocorrer externamente. O NIAE
NÃO DEVE ser transformado preventivamente em plataforma analítica genérica.

### XX. Acessibilidade é requisito funcional de qualidade

Interfaces DEVEM ser acessíveis desde a implementação, adotando como referência,
conforme aplicável, **WCAG 2.1 nível AA** e **eMAG**. DEVEM ser considerados: navegação
por teclado; HTML semântico; labels apropriados; foco visível; contraste; mensagens de
erro compreensíveis; tecnologias assistivas; ordem lógica de navegação.

Acessibilidade NÃO DEVE ser tratada como etapa posterior de acabamento.

### XXI. Mobile e responsividade fazem parte da experiência principal

A jornada do egresso DEVE funcionar adequadamente em dispositivos móveis; desktop NÃO
DEVE ser presumido como ambiente principal. DEVEM ser priorizados: leitura confortável;
controles adequados; baixa carga cognitiva; ausência de layouts inadequados em telas
pequenas; interação simples; desempenho aceitável.

### XXII. Simplicidade e YAGNI são obrigatórios

O projeto DEVE resolver bem o domínio de acompanhamento de egressos. NÃO DEVEM ser
construídos preventivamente: Google Forms genérico; CRM; portal institucional completo;
sistema acadêmico; workflow engine; motor genérico de regras; plataforma de marketing;
BI completo; barramento de integração; sistema de identidade; arquitetura de
microserviços sem necessidade.

- Antes de criar abstração genérica, DEVE existir caso concreto que a justifique.
- PREFERIR: domínio explícito; componentes pequenos; responsabilidades claras; código
  legível; dependências limitadas; fluxos simples.
- EVITAR: generalizações especulativas; plugins sem consumidor; configurações
  arbitrárias; extensibilidade hipotética; infraestrutura prematura; campos sem
  finalidade conhecida.
- Complexidade adicional DEVE ser justificada na spec ou no plan.

### XXIII. O editor de pesquisa não é um form builder universal

O sistema PODE permitir manutenção de pesquisas sem alteração de código; isso NÃO
transforma o Trajetória Ifes em plataforma genérica de formulários.

- DEVEM ser adicionados somente recursos necessários ao domínio.
- NÃO DEVEM ser criados antecipadamente: scripting; plugins; fórmulas arbitrárias;
  componentes universais; workflows genéricos; linguagem própria de regras.
- Tipos de pergunta, condicionais e demais recursos DEVEM surgir de casos concretos.

### XXIV. Não fixar stack tecnológica nesta Constituição

Esta Constituição NÃO determina linguagem, framework, banco de dados, fila,
orquestrador ou outra tecnologia específica. Essas decisões pertencem aos plans e,
quando necessário, a ADRs.

A tecnologia escolhida DEVE privilegiar: simplicidade; manutenibilidade; segurança;
capacidade da equipe; ambiente institucional; operação; integração; testabilidade;
longevidade.

PREFERIR aplicação modular simples enquanto ela for suficiente. Microserviços NÃO DEVEM
ser adotados por padrão.

### XXV. O núcleo deve ser testável independentemente das integrações

- O desenvolvimento NÃO DEVE ficar bloqueado pela indisponibilidade do sistema
  acadêmico, do Portal do Egresso, da autenticação institucional ou de sistemas de
  comunicação.
- Providers, mocks e fixtures DEVEM permitir desenvolvimento e testes isolados.
- Integrações reais DEVEM ser adicionadas sem invalidar os testes do núcleo.

### XXVI. Testes devem proteger comportamento e invariantes

Toda regra relevante DEVE possuir proteção automatizada proporcional ao risco. DEVEM
ser priorizados testes de: Pessoa ↔ Conclusão Acadêmica; múltiplas conclusões;
múltiplas participações; longitudinalidade; versionamento; preservação histórica;
condicionais; elegibilidade; autorização; providers; exportações; associação correta
das respostas; migrações com impacto histórico.

- Correções de bugs relevantes DEVEM possuir teste de regressão.
- Integrações DEVERIAM possuir testes de contrato quando tecnicamente apropriado.
- Percentual de cobertura NÃO DEVE ser perseguido como objetivo isolado.

### XXVII. Migrações devem preservar significado histórico

Depois que existirem dados reais, mudanças estruturais são operações de risco. Toda
migração que possa afetar histórico DEVE: possuir estratégia explícita; preservar
informação; permitir validação; evitar reinterpretação silenciosa; evitar perda
irreversível não aprovada.

PREFERIR evolução aditiva e reversível quando razoável. Mudanças destrutivas exigem
decisão explícita.

### XXVIII. Desenvolvimento orientado por specs

Toda mudança funcional relevante DEVE nascer de spec. Uma spec DEVE responder
prioritariamente:

- qual problema está sendo resolvido;
- quem é afetado;
- qual comportamento deve existir;
- quais invariantes precisam permanecer;
- quais cenários demonstram sucesso;
- quais critérios de aceitação se aplicam;
- o que está explicitamente fora do escopo;
- quais decisões continuam pendentes.

Specs DEVEM tratar comportamento antes de implementação; detalhes técnicos pertencem
prioritariamente ao plan. Decisões de produto ou de domínio NÃO DEVEM ficar escondidas
no código.

### XXIX. Hipóteses não podem virar requisitos silenciosamente — NON-NEGOTIABLE

Quando houver dúvida sobre periodicidade, população elegível, múltiplas formações,
papéis administrativos, aprovação, autenticação, retenção, consentimento, LGPD,
publicação, compartilhamento, integração institucional, fonte acadêmica oficial,
responsabilidades do Portal do Egresso ou qualquer outra regra institucional:

- comportamento definitivo NÃO DEVE ser inventado;
- a dúvida DEVE ser registrada explicitamente como `DECISÃO PENDENTE`;
- "suposições razoáveis" ou "padrões de mercado" NÃO DEVEM substituir decisão
  institucional.

Quando for necessário prosseguir antes da decisão institucional, a solução adotada DEVE
ser: reversível; localizada; desacoplada; configurável apenas quando necessário;
claramente identificada como hipótese. Hipótese NÃO DEVE ser cristalizada como regra
institucional.

## Fronteira do Domínio do NIAE

Pertencem ao domínio central do Trajetória Ifes, salvo futura revisão constitucional:

- Pessoa, no limite necessário ao acompanhamento;
- Conclusão Acadêmica;
- Pesquisa e Versão da Pesquisa;
- Campanha;
- critérios de acompanhamento e elegibilidade;
- Participação em Pesquisa e Respostas;
- contexto institucional utilizado;
- proveniência;
- histórico longitudinal;
- acompanhamento operacional da coleta;
- exportação e disponibilização estruturada dos dados.

Podem pertencer a sistemas externos e ser integrados: sistema acadêmico; identidade
institucional; Portal do Egresso; serviços de comunicação; e-mail; notificações;
ferramentas de BI; eventos; oportunidades profissionais; outros serviços institucionais.

Integração com esses sistemas NÃO transfere automaticamente sua responsabilidade ao NIAE.

## Arquitetura de Integração

A arquitetura DEVE preservar conceitualmente a seguinte organização:

```text
Soluções institucionais externas
        │
        │ contratos/adaptadores
        ▼
┌───────────────────────────────┐
│        TRAJETÓRIA IFES        │
│             NIAE              │
│                               │
│ acompanhamento longitudinal   │
│ pesquisa e versionamento      │
│ campanhas                     │
│ participações                 │
│ respostas                     │
│ acompanhamento da coleta      │
│ dados estruturados            │
└───────────────┬───────────────┘
                │
                │ providers
                ▼
        Fontes institucionais
```

- O domínio NÃO DEVE conhecer detalhes técnicos das integrações externas além dos
  contratos necessários.
- APIs externas DEVEM surgir a partir de casos reais de integração. NÃO DEVE ser criada
  API pública ou genérica apenas porque talvez seja útil no futuro.

## Desenvolvimento Inicial com Dados Simulados

A indisponibilidade da integração acadêmica real NÃO DEVE bloquear o projeto. O
desenvolvimento inicial DEVE poder utilizar `MockAcademicDataProvider` com cenários
realistas, incluindo pelo menos casos equivalentes a:

- pessoa com uma única conclusão;
- pessoa com várias conclusões;
- conclusões em campi diferentes;
- conclusões em diferentes níveis;
- diferentes períodos de conclusão;
- múltiplas participações relativas à mesma conclusão;
- pessoa com múltiplas formações elegíveis.

O mock DEVE validar o contrato utilizado pelo domínio.

Quando a fonte acadêmica real estiver disponível, DEVE-SE: (1) estudar seu modelo;
(2) identificar correspondências; (3) implementar adaptador; (4) preservar o contrato do
domínio; (5) modificar o núcleo apenas quando surgir fato de domínio genuinamente novo.
O modelo legado NÃO DEVE ser reproduzido dentro do domínio para facilitar a integração.

## Governança de Permissões

Autorizações DEVEM ser definidas a partir das necessidades institucionais; todos os
perfis NÃO DEVEM ser presumidos antecipadamente. Quando definidos, DEVEM respeitar:
menor privilégio; separação de responsabilidades; escopo por unidade quando pertinente;
visão institucional quando autorizada; distinção entre competência técnica e competência
normativa.

Possuir acesso técnico ao sistema NÃO equivale automaticamente a poder: alterar
instrumentos; publicar versões; definir periodicidade; definir população elegível;
acessar dados de todas as unidades; exportar dados identificados; alterar configurações
institucionais. Essas competências DEVEM ser modeladas explicitamente.

## Qualidade das Exportações

Exportações NÃO DEVEM ser dumps brutos de banco de dados; DEVEM produzir datasets
semanticamente compreensíveis. Quando pertinente, DEVEM incluir: identificador da
participação; campanha; versão; identificador permitido da pessoa; conclusão acadêmica;
campus; curso; nível; ano/data de conclusão; data da participação; respostas; contexto
necessário à interpretação.

Cabeçalhos e valores DEVEM possuir significado estável ou documentado. O versionamento
da pesquisa NÃO DEVE tornar impossível interpretar exportações históricas.

## Observabilidade

O sistema DEVE possuir observabilidade proporcional à operação, registrando eventos
técnicos necessários para diagnóstico, segurança, disponibilidade, integração e
auditoria relevante.

NÃO DEVEM ser registrados desnecessariamente: CPF; e-mail; respostas sensíveis; tokens;
dados pessoais completos. Logs não são banco de dados de pesquisa.

## Definition of Done

Uma feature somente é considerada concluída quando:

- atende à spec aprovada;
- respeita esta Constituição;
- possui testes adequados ao risco;
- não quebra longitudinalidade;
- não compromete preservação histórica;
- respeita proveniência;
- mantém autorizações aplicáveis;
- possui tratamento adequado de erros;
- atende acessibilidade quando possuir interface;
- funciona adequadamente nos dispositivos pertinentes;
- não introduz complexidade injustificada;
- possui documentação necessária;
- não transforma decisão pendente em regra implícita.

## Constitution Check Obrigatório

Todo `/speckit-plan` DEVE executar Constitution Check explícito, antes da pesquisa
(Fase 0) e novamente após o desenho (Fase 1), verificando, conforme pertinência:
longitudinalidade; Pessoa versus Conclusão Acadêmica; múltiplas formações; múltiplas
participações; preservação histórica; versionamento; proveniência; separação entre dado
institucional, derivado e declarado; desacoplamento de integrações; fronteira do NIAE;
governança institucional; escopo por unidade; privacidade; autorização; acessibilidade;
responsividade; testes; risco de over engineering; decisões pendentes.

Itens não pertinentes DEVEM ser marcados como tal, não omitidos. Uma violação NÃO DEVE
ser silenciosamente aceita. Havendo conflito, DEVE-SE verificar, nesta ordem:

1. se a feature está incorreta;
2. se o escopo está excessivo;
3. se existe alternativa compatível;
4. se a própria Constituição precisa evoluir.

Somente no quarto caso ocorre emenda constitucional.

## Princípios Resumidos

Toda evolução do Trajetória Ifes DEVE preservar sobretudo:

1. uma Pessoa pode possuir várias Conclusões Acadêmicas;
2. uma Conclusão Acadêmica pode ser acompanhada várias vezes;
3. respostas de diferentes momentos nunca substituem umas às outras;
4. dado institucional não é resposta declarada;
5. dados derivados também devem ser distinguidos das respostas;
6. a origem dos dados deve ser preservável;
7. integrações externas não definem o domínio;
8. Pesquisa, Versão, Campanha e Participação são conceitos distintos;
9. periodicidade pertence à governança, não ao código;
10. a tecnologia não redefine a PAEG;
11. a Pessoa é institucional; campus e curso pertencem ao contexto acadêmico;
12. o Trajetória Ifes implementa o NIAE, não todo o Portal do Egresso;
13. integração institucional é preferível à duplicação de domínios externos;
14. preservar histórico é mais importante que facilitar edição retroativa;
15. minimizar esforço desnecessário do egresso;
16. simplicidade prevalece sobre extensibilidade especulativa;
17. acessibilidade faz parte do requisito;
18. dados devem permanecer exportáveis e interoperáveis;
19. dúvidas institucionais devem permanecer explicitamente pendentes;
20. toda evolução funcional relevante deve ser orientada por spec.

Em caso de divergência de redação, prevalece o texto integral dos Princípios
Fundamentais.

## Governança

### Supremacia

Esta Constituição prevalece sobre specs, plans, tasks, ADRs, convenções locais,
instruções de comandos/agentes e decisões incidentais de implementação.

Esta Constituição rege o desenvolvimento do software e NÃO se sobrepõe às normas
institucionais do Ifes. Conflito identificado entre esta Constituição e a PAEG ou outra
norma institucional vigente DEVE ser registrado e tratado por emenda, nunca resolvido
silenciosamente no código.

Nenhum agente ou desenvolvedor DEVE contornar silenciosamente um princípio.

### Procedimento de emenda

Se uma necessidade real exigir mudança constitucional:

1. registrar o conflito;
2. explicar por que a Constituição atual deixou de atender ao domínio;
3. avaliar impacto sobre dados, integrações e specs existentes;
4. alterar formalmente a Constituição, atualizando versão e data de última alteração;
5. somente então implementar comportamento incompatível.

### Versionamento

A Constituição usa versionamento semântico:

- **MAJOR**: mudança incompatível de princípio, governança, invariante fundamental ou
  fronteira estrutural do domínio.
- **MINOR**: novo princípio, nova restrição ou ampliação normativa relevante.
- **PATCH**: correção ou esclarecimento sem alteração substantiva de significado.

### Revisão de conformidade

- Todo plan DEVE conter Constitution Check explícito (ver seção própria).
- Toda revisão de spec, plan, tasks ou código DEVE verificar conformidade com esta
  Constituição e com a Definition of Done.
- Desvios de princípios não marcados como NON-NEGOTIABLE DEVEM ser justificados por
  escrito no plan (*Complexity Tracking*) e aceitos em revisão; desvios de princípios
  NON-NEGOTIABLE NÃO são admitidos sem emenda.

**Version**: 1.0.0 | **Ratified**: 2026-09-30 | **Last Amended**: 2026-09-30
